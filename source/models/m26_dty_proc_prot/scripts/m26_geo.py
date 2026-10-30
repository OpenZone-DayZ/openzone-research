"""M26 primitives that kgeo does not have (the kit files stay unchanged): an angle iron per GOST 8509
with a fillet, a weld, a prism with a chamfer, a rounded rectangle, a solid of revolution along any
axis, a smooth curve, a bar between points, a screw, a cable tie, a vanilla item leaned against
something. The solid of revolution, the rounded rectangle, the curve and the bar are as in the M10
generator (m10_geo.py).

All solids are closed: the normals are computed by bmesh.ops.recalc_face_normals.
"""
import math

import bmesh
from mathutils import Vector

import kgeo as g
import kvanilla as kv

AXES = {"x": ((0, 1, 0), (0, 0, 1), (1, 0, 0)), "-x": ((0, 1, 0), (0, 0, -1), (-1, 0, 0)),
        "y": ((0, 0, 1), (1, 0, 0), (0, 1, 0)), "-y": ((1, 0, 0), (0, 0, 1), (0, -1, 0)),
        "z": ((1, 0, 0), (0, 1, 0), (0, 0, 1)), "-z": ((1, 0, 0), (0, -1, 0), (0, 0, -1))}


def frame_at(o, axis):
    """Coordinate system through point o with the axis given by the string axis ("x", "-y", "z"...)."""
    u, v, n = AXES[axis]
    return g.Frame(o, u, v, n)


def frame_axis(o, axis):
    """Coordinate system with axis n = axis (a vector) through point o: u, v - any pair across it."""
    n = Vector(axis).normalized()
    ref = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = ref.cross(n).normalized()
    v = n.cross(u).normalized()
    return g.Frame(o, u, v, n)


def lathe(part, prof, sides, fr, closed=False, a0=0.0):
    """Solid of revolution: profile prof [(r, h)] around axis fr.n through fr.o (r in the u, v plane, h
    along n). closed - the profile is closed (a ring with the section prof); otherwise the ends are
    closed with a circle (r = 0 - with a point)."""
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


def sphere(part, c, r, sides=8, rings=4):
    """Sphere (a ball at the end of a knob, a ball foot)."""
    prof = [(r * math.sin(math.pi * i / rings), -r * math.cos(math.pi * i / rings)) for i in range(rings + 1)]
    return lathe(part, prof, sides, frame_at(c, "z"))


def rrect(x0, x1, y0, y1, r, n):
    """Rectangle with rounded corners (radius r, n segments per corner), counterclockwise."""
    if r <= 0 or n <= 0:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90.0), (x1 - r, y1 - r, 0.0), (x0 + r, y1 - r, 90.0), (x0 + r, y0 + r, 180.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def hexagon(r, a0=math.pi / 6):
    return [(r * math.cos(math.pi * k / 3 + a0), r * math.sin(math.pi * k / 3 + a0)) for k in range(6)]


def knurl_poly(r, n, depth):
    """Knurled circle: 2n vertices, every other one sunk by depth."""
    return [((r - depth * (k % 2)) * math.cos(math.pi * k / n), (r - depth * (k % 2)) * math.sin(math.pi * k / n))
            for k in range(2 * n)]


def prism_bev(part, poly, c0, c1, fr=None, r=0.0, seg=1, axes=(0, 1), sides=False):
    """Prism of polygon poly along the third axis from c0 to c1 (with fr - in its u, v, n axes); r > 0 - a
    chamfer along the outline of both ends, sides - also along the edges parallel to the axis (for an
    outline with sharp corners)."""
    bm = part.bm
    before = set(bm.faces)
    faces = g.prism(part, poly, axes, c0, c1, frame=fr)
    if r > 0 and seg > 0:
        edges = {e for f in faces[:2] for e in f.edges}
        if sides:
            edges |= {e for f in faces[2:] for e in f.edges}
        g.bevel(bm, list(edges), r, seg)
        new = [f for f in bm.faces if f not in before]
        bmesh.ops.recalc_face_normals(bm, faces=new)
        part.tag(new)
        return new
    return faces


def angle_poly(a, t, lod, r1=0.006, c=0.0015):
    """Section of an angle a x t (GOST 8509: for 50 x 5 the fillet radius is 5.5 mm, the leg tip rounding
    1.8 mm) in (leg 1, leg 2) axes, the heel is at (0, 0). LOD 0 - a fillet in three segments and
    chamfers on the leg tips."""
    if lod > 0:
        return [(0.0, 0.0), (a, 0.0), (a, t), (t, t), (t, a), (0.0, a)]
    pts = [(0.0, 0.0), (a, 0.0), (a, t - c), (a - c, t)]
    for k in range(4):
        th = math.radians(-90.0 - 30.0 * k)
        pts.append((t + r1 + r1 * math.cos(th), t + r1 + r1 * math.sin(th)))
    pts += [(t, a - c), (t - c, a), (0.0, a)]
    return pts


def angle(part, heel, d1, d2, along, length, a, t, lod, c0=0.0):
    """Angle iron: the heel (outer corner) at point heel, leg 1 along d1, leg 2 along d2, the length is laid
    out from c0 to c0 + length in the direction along. Far LOD - one leg d1 as a box."""
    fr = g.Frame(heel, d1, d2, along)
    if lod == 2:
        return g.box(part, 0.0, a, 0.0, t, c0, c0 + length, frame=fr)
    return g.prism(part, angle_poly(a, t, lod), (0, 1), c0, c0 + length, frame=fr)


def tube_sq(part, center_xy, half, z0, z1, r, n, axes=(0, 1)):
    """Square tube (solid) with rounded edges: a section of 2*half with rounding r along the third axis
    from z0 to z1."""
    cx, cy = center_xy
    return g.prism(part, rrect(cx - half, cx + half, cy - half, cy + half, r, n), axes, z0, z1)


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom): k segments per link."""
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


def resample(pts, step):
    """Points along a polyline at equal step."""
    v = [Vector(p) for p in pts]
    seg = [(v[i], v[i + 1], (v[i + 1] - v[i]).length) for i in range(len(v) - 1)]
    total = sum(s[2] for s in seg)
    n = max(2, int(round(total / step)))
    out, i, acc = [], 0, 0.0
    for k in range(n + 1):
        d = total * k / n
        while i < len(seg) - 1 and acc + seg[i][2] < d:
            acc += seg[i][2]
            i += 1
        a, b, ln = seg[i]
        t = 0.0 if ln < 1e-9 else min(1.0, (d - acc) / ln)
        out.append(tuple(a + (b - a) * t))
    return out


def weld(part, pts, r=0.0028, step=0.009, sides=4):
    """Weld: a bead along polyline pts, the section is slightly wavy (weld scales) and flattened toward the ends."""
    q = resample(pts, step)
    n = len(q)
    radii = []
    for i in range(n):
        end = min(1.0, min(i, n - 1 - i) / 1.5 + 0.35)
        k = r * end * (1.0 + 0.16 * (1 if i % 2 else -1))
        radii.append((k, k * 0.75))
    return g.tube_var(part, q, radii, sides)


def box_to(part, a, b, w, h, up=(0, 0, 1), r=0.0, seg=0):
    """Bar from point a to point b with section w (across) x h (along up)."""
    a, b = Vector(a), Vector(b)
    u = (b - a).normalized()
    n = Vector(up) - u * Vector(up).dot(u)
    n.normalize()
    v = n.cross(u)
    fr = g.Frame(a, u, v, n)
    return g.box(part, 0.0, (b - a).length, -w / 2, w / 2, -h / 2, h / 2, r=r, seg=seg, frame=fr)


def rod(part, a, b, r, sides):
    """Round rod between points a and b."""
    return g.pipe(part, [tuple(a), tuple(b)], r, sides)


def screw(part, center, axis, r, sides=6):
    """Round-head screw: a low dome on a support (axis points outward from the support)."""
    return lathe(part, [(r, 0.0), (r * 0.78, r * 0.5), (0.0, r * 0.68)], sides, frame_at(center, axis))


def hex_bolt(part, center, axis, s, h, washer=True, lod=0):
    """Hex-head bolt with width across flats s and a washer (axis points outward from the support)."""
    fr = frame_at(center, axis)
    z = 0.0
    if washer and lod == 0:
        lathe(part, [(s * 0.95, 0.0), (s * 0.95, 0.0012)], 8, fr)
        z = 0.0012
    g.prism(part, hexagon(s / math.sqrt(3)), (0, 1), z, z + h, frame=fr)


def tie_loop(part, center_xy, half_x, half_y, z, w=0.0045, t=0.0009):
    """Cable tie around a rectangle (a post with a cable) in a horizontal plane, with a lock."""
    cx, cy = center_xy
    pts = rrect(cx - half_x, cx + half_x, cy - half_y, cy + half_y, min(half_x, half_y) * 0.35, 2)
    loop = [(x, y, z) for x, y in pts]
    g.sweep(part, loop, (0, 0, 1), t, w / 2, closed=True)
    g.box(part, cx + half_x - 0.001, cx + half_x + 0.005, cy - 0.003, cy + 0.003, z - w * 0.65, z + w * 0.65)


def lean(key, foot, top, toward, lods=(0, 1)):
    """A vanilla item leaned against something: the working end (the item's +Y) at point foot (on the
    floor), the handle toward the support in direction top; the item's X-Y plane (a shovel, a blade) faces
    the support toward. Returns a decor entry (like kvanilla.put); the bottom of the extent is not below foot."""
    lo, hi = kv.box(key)
    up = (Vector(foot) - Vector(top)).normalized()
    f = Vector(toward) - up * Vector(toward).dot(up)
    f.normalize()
    X, U, F = kv.axes(tuple(up), tuple(f))
    cx, cz = (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2
    local_end = (cx, hi[1], cz)
    o0 = tuple(foot[i] - (local_end[0] * X[i] + local_end[1] * U[i] + local_end[2] * F[i]) for i in range(3))
    low = min(q[2] for q in kv.corners(key, o0, tuple(up), tuple(f)))
    origin = (o0[0], o0[1], o0[2] + (foot[2] - low))
    return (kv.path(key), origin, tuple(up), tuple(f), tuple(lods), key)
