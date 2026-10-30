"""M61 geometry missing from kgeo: solids of revolution in any coordinate system (with a pattern around
the circle), slabs with rounded edges, torus, knurling, ribbon, smooth curves and a coiled cord.
Modelled on M17, M60 and M05 (their functions are copied here so the kit and other generators stay
untouched). Parts are kgeo.Part; faces point outwards, towards the viewer (kexport flips them for p3d).

Blender axes: X is width, Y is depth (the working side is -Y), Z is up.
"""
import math

import bmesh
from mathutils import Vector

import kgeo as g


def face(part, verts, want):
    """Face from bmesh vertices, oriented towards want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    part.tag([f])
    return f


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom), k points per segment."""
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


def simplify(pts, deg=4.0):
    """Drop curve points where it barely turns, so straight runs get no extra rings."""
    out = [tuple(pts[0])]
    for i in range(1, len(pts) - 1):
        a = Vector(pts[i]) - Vector(out[-1])
        b = Vector(pts[i + 1]) - Vector(pts[i])
        if a.length < 1e-9 or b.length < 1e-9:
            continue
        if a.angle(b) > math.radians(deg):
            out.append(tuple(pts[i]))
    out.append(tuple(pts[-1]))
    return out


def cord(part, pts, r, sides, k=3, deg=5.0):
    """Wire or cord: a smooth curve through the control points with a round section."""
    pp = simplify(spline(pts, k), deg) if k > 1 else [tuple(p) for p in pts]
    return g.pipe(part, pp, r, sides)


def resample(pts, step):
    """Curve points at equal steps of length (the ends stay in place)."""
    pv = [Vector(p) for p in pts]
    lens = [0.0]
    for a, b in zip(pv, pv[1:]):
        lens.append(lens[-1] + (b - a).length)
    n = max(2, int(round(lens[-1] / step)))
    out, i = [], 0
    for s in range(n + 1):
        d = lens[-1] * s / n
        while i < len(lens) - 2 and lens[i + 1] < d:
            i += 1
        f = (d - lens[i]) / max(lens[i + 1] - lens[i], 1e-9)
        out.append(tuple(pv[i].lerp(pv[i + 1], f)))
    return out


def coil_on(path, r, turns, steps_per_turn):
    """Twisted cord lying on a plane: a coil of radius r around the smooth curve path (from M05)."""
    pv = [Vector(p) for p in resample(path, 0.002)]
    lens = [0.0]
    for i in range(1, len(pv)):
        lens.append(lens[-1] + (pv[i] - pv[i - 1]).length)
    total = lens[-1]
    n = max(8, int(turns * steps_per_turn))
    out, i = [], 0
    for s in range(n + 1):
        d = total * s / n
        while i < len(lens) - 2 and lens[i + 1] < d:
            i += 1
        f = (d - lens[i]) / max(lens[i + 1] - lens[i], 1e-9)
        p = pv[i].lerp(pv[i + 1], f)
        t = (pv[i + 1] - pv[i]).normalized()
        side = t.cross(Vector((0, 0, 1)))
        side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
        up = side.cross(t).normalized()
        ang = 2 * math.pi * turns * s / n
        out.append(tuple(p + (up * math.cos(ang) + side * math.sin(ang)) * r))
    return out


def frame_z(cx, cy, deg, z):
    """Frame of a thing lying on a horizontal support: u runs along it at angle deg from +X, v across,
    n up."""
    a = math.radians(deg)
    return g.Frame((cx, cy, z), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))


def basis(axis):
    """Rotation axis: (a, b, w) are two transverse unit vectors and the longitudinal one; axis is "x", "-y", ...
    or a vector."""
    if isinstance(axis, str):
        w = Vector([1.0 if c == axis[-1] else 0.0 for c in "xyz"]) * (-1.0 if axis.startswith("-") else 1.0)
    else:
        w = Vector(axis).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(w.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    a = ref.cross(w).normalized()
    return a, w.cross(a).normalized(), w


def lathe(part, prof, sides, center, axis="z", caps=(False, False), phase=0.0, rfn=None):
    """Solid of revolution: prof [(r, h)] is the section (r from the axis, h along axis from center). The
    walk goes along the visible surface in the direction of growing h, so faces point outwards (the
    opposite walk points them inwards). r = 0 is a point on the axis (a fan). caps closes the first and
    last rings. rfn(i, t) is the radius multiplier of ring i at angle t (a pattern around the circle:
    knurling of a tea-glass holder, recesses)."""
    a, b, w = basis(axis)
    c = Vector(center)
    bm = part.bm
    angs = [phase + 2 * math.pi * k / sides for k in range(sides)]
    rings = []
    for i, (r, h) in enumerate(prof):
        if r < 1e-7:
            rings.append(bm.verts.new(c + w * h))
        else:
            rings.append([bm.verts.new(c + (a * math.cos(t) + b * math.sin(t)) * r * (rfn(i, t) if rfn else 1.0) + w * h)
                          for t in angs])
    new = []
    for i0 in range(len(prof) - 1):
        i1 = i0 + 1
        (r0, h0), (r1, h1) = prof[i0], prof[i1]
        nr, nh = h1 - h0, -(r1 - r0)
        R0, R1 = rings[i0], rings[i1]
        for k in range(sides):
            j = (k + 1) % sides
            tm = angs[k] + math.pi / sides
            want = (a * math.cos(tm) + b * math.sin(tm)) * nr + w * nh
            if isinstance(R0, list) and isinstance(R1, list):
                vs = [R0[k], R0[j], R1[j], R1[k]]
            elif isinstance(R0, list):
                vs = [R0[k], R0[j], R1]
            elif isinstance(R1, list):
                vs = [R0, R1[j], R1[k]]
            else:
                continue
            new.append(face(part, vs, want))
    for cap, i, o in ((caps[0], 0, 1), (caps[1], len(prof) - 1, len(prof) - 2)):
        if cap and isinstance(rings[i], list):
            new.append(face(part, rings[i], w * (1.0 if prof[i][1] > prof[o][1] else -1.0)))
    return new


def rrect(x0, x1, y0, y1, r, n):
    """Rectangle with rounded corners (n segments per corner), counter-clockwise; n = 0 gives sharp corners."""
    if n <= 0 or r <= 1e-6:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    out = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90.0), (x1 - r, y1 - r, 0.0), (x0 + r, y1 - r, 90.0), (x0 + r, y0 + r, 180.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def slab(part, x0, x1, y0, y1, z0, z1, rc=0.0, nc=0, re=0.0, ne=0, rb=0.0, nb=0, frame=None, caps=(True, True)):
    """Slab (from M07/M17): a rectangle in plan with corners rounded by rc (nc segments), the top edge
    rounded by re (ne segments), the bottom one by rb (nb). frame is the local system: x -> u, y -> v,
    z -> n."""
    rows = []
    if rb > 0 and nb > 0:
        rows += [(rb * (1 - math.sin(math.pi / 2 * k / nb)), z0 + rb * (1 - math.cos(math.pi / 2 * k / nb)))
                 for k in range(nb + 1)]
    else:
        rows.append((0.0, z0))
    top = [(re * (1 - math.cos(math.pi / 2 * k / ne)), z1 - re + re * math.sin(math.pi / 2 * k / ne))
           for k in range(ne + 1)] if re > 0 and ne > 0 else [(0.0, z1)]
    for r in top:
        if abs(r[0] - rows[-1][0]) > 1e-7 or abs(r[1] - rows[-1][1]) > 1e-7:
            rows.append(r)
    bm = part.bm

    def p3(a, b, c):
        return frame.p(a, b, c) if frame else Vector((a, b, c))

    def d3(a, b, c):
        return (frame.u * a + frame.v * b + frame.n * c) if frame else Vector((a, b, c))
    ctr = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    rings = []
    for d, h in rows:
        pts = rrect(x0 + d, x1 - d, y0 + d, y1 - d, max(rc - d, 0.0005) if nc else 0.0, nc)
        rings.append([(bm.verts.new(p3(a, b, h)), Vector((a, b, h))) for a, b in pts])
    new = []
    n = len(rings[0])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(n):
            j = (k + 1) % n
            q = [r0[k], r0[j], r1[j], r1[k]]
            loc = sum((e[1] for e in q), Vector()) / 4 - ctr
            new.append(face(part, [e[0] for e in q], d3(*loc)))
    if caps[0]:
        new.append(face(part, [e[0] for e in rings[0]], d3(0, 0, -1)))
    if caps[1]:
        new.append(face(part, [e[0] for e in rings[-1]], d3(0, 0, 1)))
    return new


def torus(part, fr, R, r, nu, nv, arc=(0.0, 2 * math.pi)):
    """Torus (or a torus arc of arc radians) in the (u, v) plane of frame fr: R is the radius of the
    centre line, r the radius of the rod."""
    bm = part.bm
    full = abs(arc[1] - arc[0] - 2 * math.pi) < 1e-6
    n_ring = nu if full else nu + 1
    rings = []
    for i in range(n_ring):
        a = arc[0] + (arc[1] - arc[0]) * i / nu
        d = fr.u * math.cos(a) + fr.v * math.sin(a)
        c = fr.o + d * R
        rings.append([bm.verts.new(c + d * (r * math.cos(2 * math.pi * k / nv)) + fr.n * (r * math.sin(2 * math.pi * k / nv)))
                      for k in range(nv)])
    for i in range(nu if full else nu):
        r0, r1 = rings[i], rings[(i + 1) % n_ring]
        a = arc[0] + (arc[1] - arc[0]) * (i + 0.5) / nu
        mid = fr.o + (fr.u * math.cos(a) + fr.v * math.sin(a)) * R
        for k in range(nv):
            j = (k + 1) % nv
            q = [r0[k], r0[j], r1[j], r1[k]]
            face(part, q, sum((v.co for v in q), Vector()) / 4 - mid)


def knurl(part, center, axis, r, h0, h1, n, depth, cap=True):
    """Knurled knob (rotary switch, terminal nut): 2n faces around the circle, every other one sunk by depth;
    the top end is closed."""
    a, b, w = basis(axis)
    c0 = Vector(center)
    bm = part.bm

    def ring(h):
        return [bm.verts.new(c0 + w * h + (a * math.cos(math.pi * k / n) + b * math.sin(math.pi * k / n)) *
                             (r - depth * (k % 2))) for k in range(2 * n)]
    lo, hi = ring(h0), ring(h1)
    for k in range(2 * n):
        j = (k + 1) % (2 * n)
        q = [lo[k], lo[j], hi[j], hi[k]]
        rad = sum((v.co for v in q), Vector()) / 4 - (c0 + w * ((h0 + h1) / 2))
        rad -= w * rad.dot(w)
        face(part, q, rad)
    if cap:
        face(part, hi, w)


def ribbon(part, pts, wdir, half_w, half_t):
    """Flat ribbon along pts (folder tie, strap): the width goes along wdir, made perpendicular to the run;
    the thickness is across the ribbon (from M16/M60)."""
    bm = part.bm
    pts = [Vector(p) for p in pts]
    n = len(pts)
    rings = []
    for i in range(n):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        w = Vector(wdir) - t * Vector(wdir).dot(t)
        w.normalize()
        th = t.cross(w).normalized()
        c = pts[i]
        rings.append([bm.verts.new(c + w * half_w + th * half_t), bm.verts.new(c - w * half_w + th * half_t),
                      bm.verts.new(c - w * half_w - th * half_t), bm.verts.new(c + w * half_w - th * half_t)])
    new = []
    for i in range(n - 1):
        r0, r1 = rings[i], rings[i + 1]
        for q in range(4):
            new.append(bm.faces.new([r0[q], r0[(q + 1) % 4], r1[(q + 1) % 4], r1[q]]))
    new.append(bm.faces.new(rings[0][::-1]))
    new.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def cloth(part, fr, w, h, nx, ny, wave, thick=0.0006, taper=0.0):
    """Cloth flag: a w x h sheet in the (u, n) plane of frame fr (u from the pole, n up), waving by
    wave(s, t) -> shift along v; two sides (face and back) thick apart, the edge is closed.
    taper narrows the sheet towards the middle at the free end (0.92 gives a triangular pennant)."""
    bm = part.bm
    sides = []
    for sgn in (-1, 1):
        grid = [[bm.verts.new(fr.p(w * i / nx, wave(i / nx, j / ny) + sgn * thick / 2,
                                   h * (0.5 + (j / ny - 0.5) * (1.0 - taper * i / nx))))
                 for j in range(ny + 1)] for i in range(nx + 1)]
        for i in range(nx):
            for j in range(ny):
                face(part, [grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]], fr.v * sgn)
        sides.append(grid)
    lo, hi = sides
    rim = [(i, 0) for i in range(nx)] + [(nx, j) for j in range(ny)] + \
          [(i, ny) for i in range(nx, 0, -1)] + [(0, j) for j in range(ny, 0, -1)]
    ctr = fr.p(w / 2, 0.0, h / 2)
    for k, (i, j) in enumerate(rim):
        i2, j2 = rim[(k + 1) % len(rim)]
        q = [lo[i][j], lo[i2][j2], hi[i2][j2], hi[i][j]]
        m = sum((v.co for v in q), Vector()) / 4
        face(part, q, m - ctr)


def rod(part, a, b, r, sides):
    """Cylinder between points a and b."""
    return g.pipe(part, [tuple(a), tuple(b)], r, sides)
