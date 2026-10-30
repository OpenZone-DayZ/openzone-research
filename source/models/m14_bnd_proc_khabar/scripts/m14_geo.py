"""M14 primitives that kgeo does not provide (here rather than in the shared kit, which other models
read): solids of revolution with their own axis, a loft of rounded rectangles, a ribbon along a curve
(insulating tape, strap, rubber band), a closed rod (rolled rim, ring), a spline.

Blender axes: X is width, Y is depth (face toward -Y), Z is up.
"""
import math
import random

import bmesh
from mathutils import Vector

import kgeo as g


def spline(pts, k, closed=False):
    """Polyline -> smooth curve through the same points (Catmull-Rom, from M04/M16); closed - a loop."""
    v = [Vector(p) for p in pts]
    n = len(v)
    out = []
    for i in range(n if closed else n - 1):
        if closed:
            p0, p1, p2, p3 = v[i - 1], v[i], v[(i + 1) % n], v[(i + 2) % n]
        else:
            p0 = v[i - 1] if i > 0 else 2 * v[i] - v[i + 1]
            p1, p2 = v[i], v[i + 1]
            p3 = v[i + 2] if i + 2 < n else 2 * v[i + 1] - v[i]
        for s in range(k):
            t = s / k
            out.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (3 * p1 - p0 - 3 * p2 + p3) * t ** 3))
    if not closed:
        out.append(v[-1])
    return [tuple(q) for q in out]


def face(part, verts, want):
    """Face from bmesh vertices, turned to look toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def frame_z(cx, cy, deg, z):
    """Frame on a horizontal support: u at angle deg from +X, v across, n up."""
    a = math.radians(deg)
    return g.Frame((cx, cy, z), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))


def frame_axis(o, n, ref=(0.0, 0.0, 1.0)):
    """Frame with axis n (u, v across, u closer to ref)."""
    n = Vector(n).normalized()
    r = Vector(ref)
    if abs(r.normalized().dot(n)) > 0.95:
        r = Vector((1.0, 0.0, 0.0)) if abs(n.x) < 0.9 else Vector((0.0, 1.0, 0.0))
    u = (r - n * r.dot(n)).normalized()
    return g.Frame(o, u, n.cross(u), n)


def tilted(o, n, yaw):
    """Local frame on an inclined surface: origin o, normal n, rotation yaw about it."""
    n = Vector(n).normalized()
    u = Vector((math.cos(yaw), math.sin(yaw), 0.0))
    u = (u - n * u.dot(n)).normalized()
    return g.Frame(o, u, n.cross(u), n)


WORLD_Z = g.Frame((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))


def lathe(part, prof, sides, frame=None, closed=False, side=1, cap0=False, cap1=False, phase=0.0, jitter=0.0,
          seed=1):
    """Solid of revolution: prof [(r, h)] about axis n of frame (without it - world z from the origin). A
    point with r = 0 is a pole (fan of triangles). closed - the profile is closed (rim, ring, torus): the
    normals point outward from the section by themselves. An open profile - normals on the right along the
    path (side = 1: going bottom-up along the outer side - outward). cap0 / cap1 - close the first / last
    ring with a disc. jitter - random shift of vertices along the axis (lumpy ash)."""
    fr = frame or WORLD_Z
    bm = part.bm
    rnd = random.Random(seed)
    rings = []
    for r, h in prof:
        if r < 1e-7:
            rings.append([bm.verts.new(fr.p(0.0, 0.0, h))])
            continue
        ring = []
        for k in range(sides):
            a = 2 * math.pi * k / sides + phase
            hh = h + (rnd.uniform(-jitter, jitter) if jitter else 0.0)
            ring.append(bm.verts.new(fr.p(r * math.cos(a), r * math.sin(a), hh)))
        rings.append(ring)
    n = len(prof)
    if closed:
        area = sum(prof[i][0] * prof[(i + 1) % n][1] - prof[(i + 1) % n][0] * prof[i][1] for i in range(n))
        side = 1 if area > 0 else -1
    new = []
    for i in range(n if closed else n - 1):
        j = (i + 1) % n
        (r0, h0), (r1, h1) = prof[i], prof[j]
        dr, dh = r1 - r0, h1 - h0
        nr, nh = dh * side, -dr * side
        A, B = rings[i], rings[j]
        for k in range(sides):
            k1 = (k + 1) % sides
            a = 2 * math.pi * (k + 0.5) / sides + phase
            want = fr.u * (math.cos(a) * nr) + fr.v * (math.sin(a) * nr) + fr.n * nh
            if len(A) == 1 and len(B) == 1:
                continue
            if len(A) == 1:
                q = [A[0], B[k], B[k1]]
            elif len(B) == 1:
                q = [A[k], A[k1], B[0]]
            else:
                q = [A[k], A[k1], B[k1], B[k]]
            new.append(face(part, q, want))
    for flag, idx, nxt in ((cap0, 0, 1), (cap1, n - 1, n - 2)):
        if flag and len(rings[idx]) > 2:
            sgn = 1.0 if prof[idx][1] >= prof[nxt][1] else -1.0
            new.append(face(part, rings[idx], fr.n * sgn))
    bm.normal_update()
    return part.tag(new)


def rrect(cx, cy, w, d, r, seg):
    """Rounded rectangle counter-clockwise: [(x, y)]; seg - segments per corner."""
    r = min(r, w / 2 - 1e-5, d / 2 - 1e-5)
    pts = []
    for k, (sx, sy) in enumerate(((1, -1), (1, 1), (-1, 1), (-1, -1))):
        ccx, ccy = cx + sx * (w / 2 - r), cy + sy * (d / 2 - r)
        a0 = (-90.0, 0.0, 90.0, 180.0)[k]
        for i in range(seg + 1):
            a = math.radians(a0 + 90.0 * i / max(seg, 1))
            pts.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
    return pts


def loft(part, rings, center, inward=False, caps=(False, False)):
    """Walls between rings of points (rings of equal length, closed): the normal is from the axis through
    center (vertical) outward or inward; caps - close the first / last ring (top and bottom: by z)."""
    bm = part.bm
    vr = [[bm.verts.new(Vector(p)) for p in ring] for ring in rings]
    c = Vector(center)
    new = []
    m = len(rings[0])
    for i in range(len(vr) - 1):
        A, B = vr[i], vr[i + 1]
        for k in range(m):
            k1 = (k + 1) % m
            q = [A[k], A[k1], B[k1], B[k]]
            mid = sum((v.co for v in q), Vector()) / 4
            out = Vector((mid.x - c.x, mid.y - c.y, 0.0))
            new.append(face(part, q, -out if inward else out))
    for flag, idx, nxt in ((caps[0], 0, 1), (caps[1], len(vr) - 1, len(vr) - 2)):
        if flag:
            z0 = sum(v.co.z for v in vr[idx]) / m
            z1 = sum(v.co.z for v in vr[nxt]) / m
            up = 1 if z0 >= z1 else -1                       # outward from the body; inward at an inner wall
            new.append(face(part, vr[idx], (0, 0, -up if inward else up)))
    bm.normal_update()
    return part.tag(new)


def rrect_ring(cx, cy, w, d, r, seg, z):
    return [(x, y, z) for x, y in rrect(cx, cy, w, d, r, seg)]


def rrect_prism(part, cx, cy, w, d, r, seg, z0, z1, caps=(True, True)):
    """Prism with rounded vertical edges."""
    return loft(part, [rrect_ring(cx, cy, w, d, r, seg, z0), rrect_ring(cx, cy, w, d, r, seg, z1)], (cx, cy, 0),
                caps=caps)


def ribbon(part, pts, wdir, half_w, half_t, closed=False):
    """Flat ribbon along pts (insulating tape, strap, rubber band): the width is along wdir (a vector or a
    list per point), straightened across the path, the thickness half_t (number or list) is across the
    ribbon. closed - a loop without ends. From ribbon() of the M16 generator."""
    bm = part.bm
    pts = [Vector(p) for p in pts]
    n = len(pts)
    ws = wdir if isinstance(wdir, list) else [wdir] * n
    ts = half_t if isinstance(half_t, list) else [half_t] * n
    rings = []
    for i in range(n):
        if closed:
            t = pts[(i + 1) % n] - pts[i - 1]
        else:
            t = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]
        t.normalize()
        w = Vector(ws[i]) - t * Vector(ws[i]).dot(t)
        w.normalize()
        th = t.cross(w).normalized()
        c, ht = pts[i], ts[i]
        rings.append([bm.verts.new(c + w * half_w + th * ht), bm.verts.new(c - w * half_w + th * ht),
                      bm.verts.new(c - w * half_w - th * ht), bm.verts.new(c + w * half_w - th * ht)])
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


def tube_loop(part, pts, r, sides):
    """Closed round rod along the loop pts (rolled tray rim): the section support is carried along the loop."""
    bm = part.bm
    pts = [Vector(p) for p in pts]
    n = len(pts)
    rings = []
    for i in range(n):
        t = (pts[(i + 1) % n] - pts[i - 1]).normalized()
        a = t.cross(Vector((0, 0, 1)))
        if a.length < 0.15:
            a = Vector((1, 0, 0)) - t * t.x
        a.normalize()
        b = a.cross(t).normalized()
        rings.append([bm.verts.new(pts[i] + (a * math.cos(2 * math.pi * k / sides) +
                                              b * math.sin(2 * math.pi * k / sides)) * r) for k in range(sides)])
    new = []
    for i in range(n):
        r0, r1 = rings[i], rings[(i + 1) % n]
        for k in range(sides):
            k1 = (k + 1) % sides
            new.append(bm.faces.new([r0[k], r0[k1], r1[k1], r1[k]]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def box_to(part, a, b, w, h, up=(0, 0, 1)):
    """Bar from point a to point b with cross-section w (across) x h (along up). From M16."""
    a, b = Vector(a), Vector(b)
    u = (b - a).normalized()
    n = Vector(up) - u * Vector(up).dot(u)
    n.normalize()
    v = n.cross(u)
    fr = g.Frame(a, u, v, n)
    return g.box(part, 0.0, (b - a).length, -w / 2, w / 2, -h / 2, h / 2, frame=fr)


def frustum(part, fr, cu, cv, w0, d0, w1, d1, h0, h1):
    """Truncated pyramid (a key): bottom w0 x d0 at h0, top w1 x d1 at h1 in frame fr; no bottom."""
    bm = part.bm
    lo = [bm.verts.new(fr.p(cu + sx * w0 / 2, cv + sy * d0 / 2, h0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    hi = [bm.verts.new(fr.p(cu + sx * w1 / 2, cv + sy * d1 / 2, h1)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    new = [face(part, hi, fr.n)]
    for k in range(4):
        k1 = (k + 1) % 4
        mid = (lo[k].co + lo[k1].co) / 2 - fr.p(cu, cv, h0)
        new.append(face(part, [lo[k], lo[k1], hi[k1], hi[k]], mid))
    bm.normal_update()
    return part.tag(new)


def quad(part, fr, a0, a1, b0, b1, c):
    """Flat rectangle in frame fr at height c, facing along fr.n (screen, watch hand)."""
    bm = part.bm
    vs = [bm.verts.new(fr.p(a, b, c)) for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
    return part.tag([face(part, vs, fr.n)])


def bev(lod, r, seg):
    return dict(r=r, seg=seg) if lod == 0 else {}


def hull2(circles, n):
    """Convex hull of circles [(x, y, r)] as a counter-clockwise polygon (from M16): the path of the
    insulating tape around the column and the dosimeter."""
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
