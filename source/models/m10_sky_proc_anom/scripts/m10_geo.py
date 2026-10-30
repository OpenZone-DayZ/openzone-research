"""M10 primitives missing from kgeo (kept here so that the kit files stay untouched): body of
revolution in any axis, rounded rectangle, U-profile body, knurling, coil spring, a two-circle
envelope (belt), smooth curve through points, bar between points.

All bodies are closed: normals are computed by bmesh.ops.recalc_face_normals.
"""
import math

import bmesh
from mathutils import Vector

import kgeo as g


def frame_axis(o, axis):
    """Coordinate system with axis n = axis (a vector) through the point o: u, v are any pair across."""
    n = Vector(axis).normalized()
    ref = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = ref.cross(n).normalized()
    v = n.cross(u).normalized()
    return g.Frame(o, u, v, n)


AXES = {"x": ((0, 1, 0), (0, 0, 1), (1, 0, 0)), "-x": ((0, 1, 0), (0, 0, -1), (-1, 0, 0)),
        "y": ((0, 0, 1), (1, 0, 0), (0, 1, 0)), "-y": ((1, 0, 0), (0, 0, 1), (0, -1, 0)),
        "z": ((1, 0, 0), (0, 1, 0), (0, 0, 1)), "-z": ((1, 0, 0), (0, -1, 0), (0, 0, -1))}


def frame_at(o, axis):
    """Coordinate system with axis axis ("x", "-y", "z"...) through the point o."""
    u, v, n = AXES[axis]
    return g.Frame(o, u, v, n)


def lathe(part, prof, sides, fr, closed=False, a0=0.0):
    """Body of revolution: profile prof [(r, h)] about the axis fr.n through fr.o (r is in the u, v plane,
    h is along n). closed - the profile is closed (a ring with section prof); otherwise the ends are
    closed with a disc (r = 0 - with a point)."""
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


def rrect(x0, x1, y0, y1, r, n):
    """Rectangle with rounded corners (radius r, n segments per corner), counter-clockwise."""
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90.0), (x1 - r, y1 - r, 0.0), (x0 + r, y1 - r, 90.0), (x0 + r, y0 + r, 180.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def u_shell(x0, x1, y0, y1, t, r, n):
    """Body profile without the back wall (in plan): the face and two sides of thickness t, the front
    corners rounded with radius r (n segments); open to +Y."""
    ri = r - t
    pts = [(x0, y1)]
    for k in range(n + 1):
        a = math.radians(180.0 + 90.0 * k / n)
        pts.append((x0 + r + r * math.cos(a), y0 + r + r * math.sin(a)))
    for k in range(n + 1):
        a = math.radians(270.0 + 90.0 * k / n)
        pts.append((x1 - r + r * math.cos(a), y0 + r + r * math.sin(a)))
    pts += [(x1, y1), (x1 - t, y1)]
    for k in range(n + 1):
        a = math.radians(360.0 - 90.0 * k / n)
        pts.append((x1 - r + ri * math.cos(a), y0 + r + ri * math.sin(a)))
    for k in range(n + 1):
        a = math.radians(270.0 - 90.0 * k / n)
        pts.append((x0 + r + ri * math.cos(a), y0 + r + ri * math.sin(a)))
    pts.append((x0 + t, y1))
    return pts


def knurl_poly(r, n, depth):
    """Knurled disc: 2n vertices, every other one sunk by depth."""
    return [((r - depth * (k % 2)) * math.cos(math.pi * k / n), (r - depth * (k % 2)) * math.sin(math.pi * k / n))
            for k in range(2 * n)]


def hexagon(r):
    return [(r * math.cos(math.pi * k / 3 + math.pi / 6), r * math.sin(math.pi * k / 3 + math.pi / 6)) for k in range(6)]


def helix(c, r, z0, z1, turns, per_turn, a0=0.0):
    """Points of a helix about the vertical through c (a spring)."""
    n = max(2, int(turns * per_turn))
    return [(c[0] + r * math.cos(a0 + 2 * math.pi * turns * i / n), c[1] + r * math.sin(a0 + 2 * math.pi * turns * i / n),
             z0 + (z1 - z0) * i / n) for i in range(n + 1)]


def hull2(circles, n):
    """Convex envelope of circles [(x, y, r)] as a polygon, counter-clockwise (a belt on pulleys)."""
    pts = []
    for x, y, r in circles:
        pts += [(x + r * math.cos(2 * math.pi * k / n), y + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    pts = sorted(set(pts))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 1e-12:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 1e-12:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


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
    """Points along a polyline at an equal step (for hose corrugation)."""
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


def box_to(part, a, b, w, h, up=(0, 0, 1), r=0.0, seg=0):
    """Bar from point a to point b with section w (across) x h (along up)."""
    a, b = Vector(a), Vector(b)
    u = (b - a).normalized()
    n = Vector(up) - u * Vector(up).dot(u)
    n.normalize()
    v = n.cross(u)
    fr = g.Frame(a, u, v, n)
    return g.box(part, 0.0, (b - a).length, -w / 2, w / 2, -h / 2, h / 2, r=r, seg=seg, frame=fr)


def screw(part, center, axis, r, sides=6):
    """Screw with a round head: a low dome on a support (axis points away from the support)."""
    lathe(part, [(r, 0.0), (r * 0.78, r * 0.5), (0.0, r * 0.68)], sides, frame_at(center, axis))
