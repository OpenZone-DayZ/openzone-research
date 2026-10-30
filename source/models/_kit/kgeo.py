"""Geometry of the OpenZone Research models: LOD parts and bmesh primitives.

A part knows its face regions (region name -> material kind and texel density scale), and the
primitives can lie in any plane and in an inclined coordinate frame (Frame).

Blender axes: X - width, Y - depth (the front, the working side, is at -Y), Z - up. kexport.conv
converts them to p3d.
"""
import math

import bmesh
from mathutils import Matrix, Vector


class Part:
    """A LOD part: a bmesh, a group (a bone or "body"), a section ("atlas" - the shared texture,
    "glass" - transparent glass with its own _ca) and face regions [(name, material kind, scale)].
    uv_name and uv_origin serve identical parts: they take the atlas once, in local coordinates
    (from uv_origin)."""

    def __init__(self, name, region=None, kind="paint", scale=1.0, group="body", section="atlas",
                 uv_name=None, uv_origin=(0.0, 0.0, 0.0)):
        self.name = name
        self.group = group
        self.section = section
        self.regions = []
        self.uv_name = uv_name or name
        self.uv_origin = Vector(uv_origin)
        self.bm = bmesh.new()
        self.reg = self.bm.faces.layers.int.new("region")
        self.cur = 0
        if region is not None:
            self.use(region, kind, scale)

    def region_index(self, region, kind=None, scale=1.0):
        for i, r in enumerate(self.regions):
            if r[0] == region:
                return i
        if kind is None:
            raise KeyError("region %s of %s has no kind" % (region, self.name))
        self.regions.append((region, kind, scale))
        return len(self.regions) - 1

    def use(self, region, kind=None, scale=1.0):
        """The following primitives write their faces into this region."""
        self.cur = self.region_index(region, kind, scale)
        return self

    def tag(self, faces, idx=None):
        idx = self.cur if idx is None else idx
        for f in faces:
            f[self.reg] = idx
        return faces


# --- inclined coordinate frame -----------------------------------------------------------
class Frame:
    """A local coordinate frame: origin o, axes u (along the width), v (up the plane),
    n (outward). A local point (a, b, c) -> o + a*u + b*v + c*n."""

    def __init__(self, o, u, v, n):
        self.o, self.u, self.v, self.n = Vector(o), Vector(u).normalized(), Vector(v).normalized(), Vector(n).normalized()

    def p(self, a, b, c):
        return self.o + self.u * a + self.v * b + self.n * c

    def matrix(self):
        m = Matrix.Identity(4)
        for i in range(3):
            m[i][0], m[i][1], m[i][2], m[i][3] = self.u[i], self.v[i], self.n[i], self.o[i]
        return m


WORLD = Frame((0, 0, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0))   # a=x, b=z, c=-y (toward the front)


def inclined_front(y0, z0, deg):
    """A front plane tilted back by deg from the vertical: it passes through (y0, z0), b runs up
    the plane, c points outward (forward and up)."""
    t = math.radians(deg)
    return Frame((0, y0, z0), (1, 0, 0), (0, math.sin(t), math.cos(t)), (0, -math.cos(t), math.sin(t)))


# --- primitives ------------------------------------------------------------------------------
def _new_faces(bm, before):
    return [f for f in bm.faces if f not in before]


# Bevel profile for two segments. The arc (0.5) gives transitions of 22.5 / 45 / 22.5 degrees: the
# middle break exceeds the sharp-edge threshold (sharp_deg 40 degrees in kexport and krender), so a
# hard line shows in the middle of every rounded edge. 0.40 gives three transitions of ~30 degrees:
# the edge looks smooth. One segment (a 45-degree bevel) and three or more (transitions of at most
# 30 degrees) keep the arc.
BEVEL2_PROFILE = 0.40


def bevel(bm, edges, offset, seg):
    edges = [e for e in edges if e.is_valid]
    if seg <= 0 or offset <= 0 or not edges:
        return
    verts = list({v for e in edges for v in e.verts})
    bmesh.ops.bevel(bm, geom=verts + edges, offset=offset, offset_type="OFFSET", segments=seg,
                    profile=BEVEL2_PROFILE if seg == 2 else 0.5, affect="EDGES", clamp_overlap=True)
    bm.normal_update()


def box(part, x0, x1, y0, y1, z0, z1, r=0.0, seg=0, frame=None):
    """A box in world axes or (with frame) in local ones: x0..x1 along u, y0..y1 along v, z0..z1
    along n. r, seg - bevel of all edges."""
    bm = part.bm
    before = set(bm.faces)
    ret = bmesh.ops.create_cube(bm, size=1.0)
    vs = ret["verts"]
    for v in vs:
        a = x0 + (v.co.x + 0.5) * (x1 - x0)
        b = y0 + (v.co.y + 0.5) * (y1 - y0)
        c = z0 + (v.co.z + 0.5) * (z1 - z0)
        v.co = frame.p(a, b, c) if frame else Vector((a, b, c))
    if r > 0 and seg > 0:
        bevel(bm, list({e for v in vs for e in v.link_edges}), r, seg)
    faces = _new_faces(bm, before)
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return part.tag(faces)


def prism(part, poly, axes, c0, c1, frame=None):
    """A prism: polygon poly in the plane of axes = (ia, ib) (0 - x, 1 - y, 2 - z), along the
    third axis from c0 to c1. With frame the axes are local (u, v, n)."""
    bm = part.bm
    ia, ib = axes
    ic = 3 - ia - ib

    def P(a, b, c):
        q = [0.0, 0.0, 0.0]
        q[ia], q[ib], q[ic] = a, b, c
        return frame.p(*q) if frame else Vector(q)
    bot = [bm.verts.new(P(a, b, c0)) for a, b in poly]
    top = [bm.verts.new(P(a, b, c1)) for a, b in poly]
    faces = [bm.faces.new(bot[::-1]), bm.faces.new(top)]
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new([bot[i], bot[j], top[j], top[i]]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return part.tag(faces)


def cyl(part, center, axis, r, length, sides, r2=None, cap=True, frame=None):
    """A cylinder (or a cone r -> r2) centered at center along axis ("x", "y", "z" - world axes,
    or local ones with frame)."""
    bm = part.bm
    before = set(bm.faces)
    rot = {"x": Matrix.Rotation(math.pi / 2, 4, "Y"), "y": Matrix.Rotation(math.pi / 2, 4, "X"),
           "z": Matrix.Identity(4)}[axis]
    m = Matrix.Translation(center) @ rot
    if frame:
        m = frame.matrix() @ m
    bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=sides, radius1=r,
                          radius2=r if r2 is None else r2, depth=length, matrix=m)
    faces = _new_faces(bm, before)
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return part.tag(faces)


def sweep(part, pts, normal, half_side, half_n, closed=False):
    """A rod of rectangular section along the polyline pts in the plane with normal `normal`: one
    ring of vertices per point, mitered along the bisector at the bends."""
    bm = part.bm
    pts = [Vector(p) for p in pts]
    nrm = Vector(normal).normalized()
    n = len(pts)
    rings = []
    for i in range(n):
        if closed or 0 < i < n - 1:
            a = (pts[i] - pts[i - 1]).normalized()
            b = (pts[(i + 1) % n] - pts[i]).normalized()
            t = a + b
            t = b if t.length < 1e-9 else t.normalized()
            k = max(0.3, a.dot(t))
        else:
            t = (pts[1] - pts[0]) if i == 0 else (pts[-1] - pts[-2])
            t.normalize()
            k = 1.0
        side = t.cross(nrm).normalized() * (half_side / k)
        up = nrm * half_n
        c = pts[i]
        rings.append([bm.verts.new(c + side + up), bm.verts.new(c - side + up),
                      bm.verts.new(c - side - up), bm.verts.new(c + side - up)])
    new = []
    for i in range(n if closed else n - 1):
        r0, r1 = rings[i], rings[(i + 1) % n]
        for q in range(4):
            new.append(bm.faces.new([r0[q], r0[(q + 1) % 4], r1[(q + 1) % 4], r1[q]]))
    if not closed:
        new.append(bm.faces.new(rings[0][::-1]))
        new.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def tube(part, pts, radius, sides, closed=False):
    """DEPRECATED; use pipe() for new models. Here each next ring is turned by 180 degrees, and the
    rod twists into a ribbon. Kept only because the accepted m01 and m02 are built on it (cables,
    the curtain handle, a toggle): replacing it with pipe() changes their near LOD, hence the atlas
    and the bake."""
    bm = part.bm
    pts = [Vector(p) for p in pts]
    n = len(pts)
    rings = []
    ref = Vector((0, 0, 1))
    for i in range(n):
        if 0 < i < n - 1:
            t = ((pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized())
            t = (pts[i + 1] - pts[i]).normalized() if t.length < 1e-9 else t.normalized()
        else:
            t = ((pts[1] - pts[0]) if i == 0 else (pts[-1] - pts[-2])).normalized()
        if abs(t.dot(ref)) > 0.95:
            ref = Vector((1, 0, 0))
        a = t.cross(ref).normalized()
        b = t.cross(a).normalized()
        ref = b                                  # carry the reference on: the rings do not twist
        rings.append([bm.verts.new(pts[i] + (a * math.cos(2 * math.pi * k / sides) +
                                             b * math.sin(2 * math.pi * k / sides)) * radius)
                      for k in range(sides)])
    new = []
    for i in range(n - 1):
        r0, r1 = rings[i], rings[i + 1]
        for k in range(sides):
            j = (k + 1) % sides
            new.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    if not closed:
        new.append(bm.faces.new(rings[0][::-1]))
        new.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def tube_var(part, pts, radii, sides):
    """A rod of variable elliptical section along a polyline (a glove, a hose): radii[i] =
    (across, thickness). The section reference is carried along the rod and does not flip, so the
    rings do not twist."""
    bm = part.bm
    pts = [Vector(p) for p in pts]
    n = len(pts)
    # Round section (pipe): the reference is carried along the curve without twisting (a
    # rotation-minimizing frame). The "across and horizontal" reference is needed only by a flattened
    # section (a glove, a flat hose): with a round one it would turn by 90 degrees at once on
    # leaving a vertical stretch, which twists the rod on one segment. On a horizontal curve the
    # reference stays t x Z.
    circle = all(abs(rx - rz) < 1e-9 for rx, rz in radii)
    rings, a_prev, t_prev = [], None, None
    for i in range(n):
        if 0 < i < n - 1:
            t = (pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized()
        else:
            t = (pts[1] - pts[0]) if i == 0 else (pts[-1] - pts[-2])
        t.normalize()
        if circle and a_prev is not None:
            a = t_prev.rotation_difference(t) @ a_prev
            a -= t * a.dot(t)
        else:
            a = t.cross(Vector((0, 0, 1)))
            if a.length < 0.15:
                a = a_prev.copy() if a_prev is not None else Vector((1, 0, 0))
                a -= t * a.dot(t)
        a.normalize()
        if not circle and a_prev is not None and a.dot(a_prev) < 0:
            a = -a
        a_prev, t_prev = a, t
        b = a.cross(t).normalized()
        rx, rz = radii[i]
        rings.append([bm.verts.new(pts[i] + a * (rx * math.cos(2 * math.pi * k / sides)) +
                                   b * (rz * math.sin(2 * math.pi * k / sides))) for k in range(sides)])
    new = []
    for i in range(n - 1):
        r0, r1 = rings[i], rings[i + 1]
        for k in range(sides):
            j = (k + 1) % sides
            new.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    new.append(bm.faces.new(rings[0][::-1]))
    new.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def pipe(part, pts, r, sides):
    """A round rod of constant section (a cable, a handle, a tube) - use it instead of tube()."""
    return tube_var(part, pts, [(r, r)] * len(pts), sides)


def quad(part, corners):
    """One flat face from points (counterclockwise seen from the front side)."""
    bm = part.bm
    f = bm.faces.new([bm.verts.new(Vector(c)) for c in corners])
    return part.tag([f])


def triangulate(parts):
    for p in parts:
        bmesh.ops.triangulate(p.bm, faces=p.bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
        p.bm.normal_update()


def tri_count(parts):
    return sum(len(p.bm.faces) for p in parts)
