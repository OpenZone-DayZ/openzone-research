"""M19 primitives that kgeo does not provide (the shared kit files are left unchanged): a solid of
revolution about any axis, contour rings (a rounded rectangle, a superellipse) and a bridge between them,
a profile along a rounded rectangle (a tray, a board, a seat), knurling, a smooth curve, a bar between
points, a screw. Partly as in M10 (m10_geo.py of the M10 model).
"""
import math

import bmesh
from mathutils import Vector

import kgeo as g


def frame_axis(o, axis):
    """Coordinate frame with axis n = axis (a vector) through point o: u, v are any pair across."""
    n = Vector(axis).normalized()
    ref = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = ref.cross(n).normalized()
    v = n.cross(u).normalized()
    return g.Frame(o, u, v, n)


AXES = {"x": ((0, 1, 0), (0, 0, 1), (1, 0, 0)), "-x": ((0, 1, 0), (0, 0, -1), (-1, 0, 0)),
        "y": ((0, 0, 1), (1, 0, 0), (0, 1, 0)), "-y": ((1, 0, 0), (0, 0, 1), (0, -1, 0)),
        "z": ((1, 0, 0), (0, 1, 0), (0, 0, 1)), "-z": ((1, 0, 0), (0, -1, 0), (0, 0, -1))}


def frame_at(o, axis):
    """Coordinate frame with axis axis ("x", "-y", "z"...) through point o."""
    u, v, n = AXES[axis]
    return g.Frame(o, u, v, n)


def lathe(part, prof, sides, fr, closed=False, a0=0.0):
    """Solid of revolution: profile prof [(r, h)] about axis fr.n through fr.o (r in the u, v plane, h along
    n). closed - the profile is closed (a ring with section prof); otherwise the ends are closed with a disc
    (r = 0 - with a point)."""
    bm = part.bm
    rings = []
    for r, h in prof:
        if r < 1e-7:
            rings.append([bm.verts.new(fr.p(0.0, 0.0, h))])
        else:
            rings.append([bm.verts.new(fr.p(r * math.cos(a0 + 2 * math.pi * k / sides),
                                            r * math.sin(a0 + 2 * math.pi * k / sides), h)) for k in range(sides)])
    new = []

    def bridge(r0, r1):
        if len(r0) == 1 and len(r1) == 1:
            return
        if len(r0) == 1:
            for k in range(sides):
                new.append(bm.faces.new([r0[0], r1[k], r1[(k + 1) % sides]]))
        elif len(r1) == 1:
            for k in range(sides):
                new.append(bm.faces.new([r0[k], r0[(k + 1) % sides], r1[0]]))
        else:
            for k in range(sides):
                j = (k + 1) % sides
                new.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    for i in range(len(rings) - 1):
        bridge(rings[i], rings[i + 1])
    if closed:
        bridge(rings[-1], rings[0])
    else:
        if len(rings[0]) > 1:
            new.append(bm.faces.new(rings[0]))
        if len(rings[-1]) > 1:
            new.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def face(part, verts, want):
    """Face from bmesh vertices, turned to look toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


# --- contour rings ------------------------------------------------------------------------
def rr_pts(hw, hh, r, n):
    """Rounded rectangle 2 hw x 2 hh about zero: 4 (n + 1) points (a, b) counter-clockwise; with the same n
    for different rings the points correspond to each other (corners have the same indices)."""
    r = max(1e-4, min(r, hw - 1e-4, hh - 1e-4))
    pts = []
    for cx, cy, a0 in ((hw - r, -hh + r, -90.0), (hw - r, hh - r, 0.0), (-hw + r, hh - r, 90.0), (-hw + r, -hh + r, 180.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def rr_xz(cx, cz, hw, hh, r, n, y):
    """Rounded-rectangle ring in the plane y = const (body face, mask)."""
    return [Vector((cx + a, y, cz + b)) for a, b in rr_pts(hw, hh, r, n)]


def rr_xy(cx, cy, hw, hh, r, n, z):
    """Rounded-rectangle ring in the plane z = const (tray, board, seat)."""
    return [Vector((cx + a, cy + b, z)) for a, b in rr_pts(hw, hh, r, n)]


def se_ring(y, a, b, n, N, cx, cz, rect=False, warp=0.7):
    """N contour points about (cx, cz) in the y plane: a superellipse |x/a|^n + |z/b|^n = 1 or (rect) a
    rectangle 2a x 2b. The parameter is the direction on the unit circle, N is a multiple of 8: the
    rectangle corners land on the 45 degree points. warp packs points toward the corners (that is where the
    superellipse bends, the straight sides need few points): at a corner the step is (1 + warp) / (1 - warp)
    times smaller than at the middle of a side; it is the same for all rings - the points of the rings
    correspond to each other."""
    pts = []
    for k in range(N):
        u = 2 * math.pi * k / N
        t = u + warp / 4 * math.sin(4 * u)
        sx, sz = math.cos(t), math.sin(t)
        if rect:
            m = max(abs(sx), abs(sz))
            px, pz = sx / m, sz / m
        else:
            lam = (abs(sx) ** n + abs(sz) ** n) ** (-1.0 / n)
            px, pz = sx * lam, sz * lam
        pts.append(Vector((cx + a * px, y, cz + b * pz)))
    return pts


def bridge_rings(part, rings, want, closed_loop=False):
    """Faces between neighbouring rings of the same length; want(i, face centre) - where the face of belt i
    looks. closed_loop - the last ring closes onto the first. Returns the ring vertices."""
    bm = part.bm
    vr = [[bm.verts.new(p) for p in r] for r in rings]
    N = len(rings[0])
    new = []
    pairs = list(range(len(rings) - 1)) + ([len(rings) - 1] if closed_loop else [])
    for i in pairs:
        r0, r1 = vr[i], vr[(i + 1) % len(vr)]
        for k in range(N):
            j = (k + 1) % N
            q = [r0[k], r0[j], r1[j], r1[k]]
            c = sum((v.co for v in q), Vector()) / 4
            new.append(face(part, q, want(i, c)))
    bm.normal_update()
    part.tag(new)
    return vr


def fan(part, ring_verts, center, want):
    bm = part.bm
    cv = bm.verts.new(center)
    N = len(ring_verts)
    new = [face(part, [ring_verts[k], ring_verts[(k + 1) % N], cv], want) for k in range(N)]
    bm.normal_update()
    return part.tag(new)


def cap(part, ring_verts, want):
    """Flat face over a ring of vertices (polygon)."""
    f = face(part, list(ring_verts), want)
    part.bm.normal_update()
    return part.tag([f])


def profile_xy(part, cx, cy, hw, hh, r, n, prof, z0=0.0):
    """Solid over a rounded rectangle: profile prof [(d, z)] - the contour offset outward (d) at height
    z0 + z; the ends are closed with faces. A closed solid - bmesh computes the outward normals."""
    bm = part.bm
    rings = [[bm.verts.new(p) for p in rr_xy(cx, cy, hw + d, hh + d, r + d, n, z0 + z)] for d, z in prof]
    N = len(rings[0])
    new = []
    for i in range(len(rings) - 1):
        for k in range(N):
            j = (k + 1) % N
            new.append(bm.faces.new([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]))
    new.append(bm.faces.new(rings[0]))
    new.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def band_xy(part, cx, cy, hw, hh, r, n, prof, z0=0.0):
    """Open ribbon over a rounded rectangle (a wrap around the edge of a board): profile [(d, z)], faces
    look outward from the axis."""
    rings = [rr_xy(cx, cy, hw + d, hh + d, r + d, n, z0 + z) for d, z in prof]
    return bridge_rings(part, rings, lambda i, c: (c.x - cx, c.y - cy, 0.0))


def torus(part, fr, R, r, n, m):
    """Torus in the (u, v) plane of frame fr: n section rings of radius r on a circle of radius R."""
    bm = part.bm
    rings = []
    for i in range(n):
        a = 2 * math.pi * i / n
        d = fr.u * math.cos(a) + fr.v * math.sin(a)
        c = fr.o + d * R
        rings.append([bm.verts.new(c + (d * math.cos(2 * math.pi * k / m) + fr.n * math.sin(2 * math.pi * k / m)) * r)
                      for k in range(m)])
    new = []
    for i in range(n):
        a = 2 * math.pi * (i + 0.5) / n
        cc = fr.o + (fr.u * math.cos(a) + fr.v * math.sin(a)) * R
        for k in range(m):
            q = [rings[i][k], rings[i][(k + 1) % m], rings[(i + 1) % n][(k + 1) % m], rings[(i + 1) % n][k]]
            c = sum((v.co for v in q), Vector()) / 4
            new.append(face(part, q, c - cc))
    bm.normal_update()
    return part.tag(new)


# --- small things -------------------------------------------------------------------------
def knurl_poly(r, n, depth):
    """Knurled circle: 2n vertices, every other one recessed by depth."""
    return [((r - depth * (k % 2)) * math.cos(math.pi * k / n), (r - depth * (k % 2)) * math.sin(math.pi * k / n))
            for k in range(2 * n)]


def hexagon(r):
    return [(r * math.cos(math.pi * k / 3 + math.pi / 6), r * math.sin(math.pi * k / 3 + math.pi / 6)) for k in range(6)]


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom): k segments per span."""
    v = [Vector(p) for p in pts]
    out = []
    for i in range(len(v) - 1):
        p0 = v[i - 1] if i > 0 else 2 * v[i] - v[i + 1]
        p1, p2 = v[i], v[i + 1]
        p3 = v[i + 2] if i + 2 < len(v) else 2 * v[i + 1] - v[i]
        for s in range(k):
            t = s / k
            out.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (3 * p1 - p0 - 3 * p2 + p3) * t ** 3))
    out.append(v[-1])
    return [tuple(q) for q in out]


def box_to(part, a, b, w, h, up=(0, 0, 1), r=0.0, seg=0):
    """Bar from point a to point b with cross-section w (across) x h (along up)."""
    a, b = Vector(a), Vector(b)
    u = (b - a).normalized()
    n = Vector(up) - u * Vector(up).dot(u)
    n.normalize()
    v = n.cross(u)
    fr = g.Frame(a, u, v, n)
    return g.box(part, 0.0, (b - a).length, -w / 2, w / 2, -h / 2, h / 2, r=r, seg=seg, frame=fr)


def screw(part, center, axis, r, sides=6):
    """Screw with a domed head: a low dome on a support (axis points outward from the support)."""
    lathe(part, [(r, 0.0), (r * 0.78, r * 0.5), (0.0, r * 0.68)], sides, frame_at(center, axis) if isinstance(axis, str)
          else frame_axis(center, axis))


def knob(part, mark, o, axis, r_skirt, r_body, h_body, lod, ribs=9, sides=None, plain=False):
    """Control knob: a skirt with a chamfer, a knurled (plain - smooth) cap, a dome; the mark is a white bar
    on the cap (mark - a separate part or None). axis points outward from the panel."""
    fr = frame_at(o, axis) if isinstance(axis, str) else frame_axis(o, axis)
    sd = sides or (14 if lod == 0 else 8)
    if lod == 0:
        lathe(part, [(r_skirt, 0.0), (r_skirt, 0.0025), (r_skirt - 0.0025, 0.0045), (0.0, 0.0045)], sd, fr)
        if plain:
            lathe(part, [(r_body, 0.0045), (r_body, 0.0045 + h_body)], sd, fr)
        else:
            g.prism(part, knurl_poly(r_body, ribs, 0.0009), (0, 1), 0.0045, 0.0045 + h_body, frame=fr)
        lathe(part, [(r_body - 0.0009, 0.0045 + h_body), (r_body * 0.75, 0.0045 + h_body + 0.002),
                     (0.0, 0.0045 + h_body + 0.0028)], sd, fr)
        if mark is not None:
            g.box(mark, -0.0007, 0.0007, r_body * 0.25, r_body * 0.85, 0.0045 + h_body + 0.0018,
                  0.0045 + h_body + 0.0026, frame=fr)
    else:
        lathe(part, [(0.0, 0.0), (r_skirt, 0.0), (r_body, 0.004), (r_body, 0.004 + h_body), (0.0, 0.004 + h_body)],
              sd if lod == 1 else 6, fr)
    return fr
