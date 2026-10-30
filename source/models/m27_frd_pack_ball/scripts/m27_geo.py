"""Geometry of the M27 gunsmith's table that kgeo does not have: a solid of revolution along any axis,
a torus, a Catmull-Rom spline (cables without kinks), an oval-section rod, a spring, a knurled knob,
screw heads (from the M18 and M23 generators), a fan blade, and unwraps onto pieces of vanilla
textures (as in the PSO of M23). The existing kit files are not changed, so everything specific is here.

Unwraps (uv_*): a part with its own section (kmodel vsections) and Part.fixed_uv - the generator sets
the UV; pieces of the image are fractions (x left to right, y top to bottom, as in the editor), in
Blender v = 1 - y.
"""
import math

import bmesh
from mathutils import Vector

import kgeo as g


def face(part, verts, want):
    """Face from bmesh vertices, oriented toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    part.tag([f])
    return f


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, from M04)."""
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


def perp(axis):
    """Two axes perpendicular to axis: (u, v) forming a right-handed triple with axis."""
    a = Vector(axis).normalized()
    r = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    u = r.cross(a).normalized()
    return u, a.cross(u).normalized()


def lathe(part, prof, sides, origin, axis=(0, 0, 1), cap0=False, cap1=False, phase=0.5):
    """Solid of revolution around axis through origin: prof [(r, h)] - radius and distance along the axis.
    A ring with r = 0 is a pole. Faces look outward along the profile direction (a reversed profile -
    inward); cap0, cap1 - flat ends of the first and last ring."""
    bm = part.bm
    a = Vector(axis).normalized()
    u, v = perp(a)
    o = Vector(origin)

    def ring(r, h):
        c = o + a * h
        if r < 1e-7:
            return [bm.verts.new(c)]
        return [bm.verts.new(c + (u * math.cos(2 * math.pi * (k + phase) / sides) +
                                  v * math.sin(2 * math.pi * (k + phase) / sides)) * r) for k in range(sides)]
    rings = [ring(r, h) for r, h in prof]
    new = []
    for i in range(len(prof) - 1):
        dr, dh = prof[i + 1][0] - prof[i][0], prof[i + 1][1] - prof[i][1]
        A, B = rings[i], rings[i + 1]
        if len(A) == 1 and len(B) == 1:
            continue
        for k in range(sides):
            j = (k + 1) % sides
            if len(A) == 1:
                q = [A[0], B[j], B[k]]
            elif len(B) == 1:
                q = [A[k], A[j], B[0]]
            else:
                q = [A[k], A[j], B[j], B[k]]
            f = bm.faces.new(q)
            f.normal_update()
            c = sum((x.co for x in q), Vector()) / len(q) - o
            rad = c - a * c.dot(a)
            rad = rad.normalized() if rad.length > 1e-9 else u
            if f.normal.dot(rad * dh - a * dr) < 0:
                f.normal_flip()
            new.append(f)
    for cap, rg, sgn in ((cap0, rings[0], -1), (cap1, rings[-1], 1)):
        if cap and len(rg) > 2:
            d = prof[1][1] - prof[0][1] if sgn < 0 else prof[-1][1] - prof[-2][1]
            f = bm.faces.new(rg)
            f.normal_update()
            if f.normal.dot(a * (sgn * (1 if d >= 0 else -1))) < 0:
                f.normal_flip()
            new.append(f)
    part.tag(new)
    return new


def rod(part, a, b, r, sides, cap=True):
    """Cylinder between points a and b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    return lathe(part, [(r, 0.0), (r, d.length)], sides, a, d, cap0=cap, cap1=cap)


def torus(part, c, axis, R, r, n, m, phase=0.0, arc=1.0):
    """Torus around axis through c: radius R (n segments around), section r (m sides); arc < 1 - an arc
    (a fraction of the circle, the ends are open)."""
    bm = part.bm
    a = Vector(axis).normalized()
    u, v = perp(a)
    c = Vector(c)
    closed = arc >= 1.0
    cnt = n if closed else n + 1
    rings = []
    for i in range(cnt):
        t = 2 * math.pi * arc * (i + phase) / n
        d = u * math.cos(t) + v * math.sin(t)
        rings.append([bm.verts.new(c + d * (R + r * math.cos(2 * math.pi * k / m)) + a * (r * math.sin(2 * math.pi * k / m)))
                      for k in range(m)])
    new = []
    for i in range(n):
        t = 2 * math.pi * arc * (i + 0.5 + phase) / n
        cc = c + (u * math.cos(t) + v * math.sin(t)) * R
        i1 = (i + 1) % cnt
        for k in range(m):
            q = [rings[i][k], rings[i][(k + 1) % m], rings[i1][(k + 1) % m], rings[i1][k]]
            cen = sum((x.co for x in q), Vector()) / 4
            f = bm.faces.new(q)
            f.normal_update()
            if f.normal.dot(cen - cc) < 0:
                f.normal_flip()
            new.append(f)
    part.tag(new)
    return new


def oval_tube(part, pts, radii, sides, ref, caps=True):
    """Rod of elliptical section along a polyline: radii[i] = (r across ref, r along ref); the section
    axis b is ref, straightened to a right angle to the rod (the headphone headband is a flat band)."""
    bm = part.bm
    pts = [Vector(p) for p in pts]
    ref = Vector(ref).normalized()
    n = len(pts)
    rings = []
    for i in range(n):
        if 0 < i < n - 1:
            t = (pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized()
        else:
            t = (pts[1] - pts[0]) if i == 0 else (pts[-1] - pts[-2])
        t.normalize()
        b = ref - t * ref.dot(t)
        if b.length < 1e-6:
            b = perp(t)[0]
        b.normalize()
        a = b.cross(t).normalized()
        ra, rb = radii[i]
        rings.append([bm.verts.new(pts[i] + a * (ra * math.cos(2 * math.pi * k / sides)) +
                                   b * (rb * math.sin(2 * math.pi * k / sides))) for k in range(sides)])
    new = []
    for i in range(n - 1):
        r0, r1 = rings[i], rings[i + 1]
        for k in range(sides):
            j = (k + 1) % sides
            new.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    if caps:
        new.append(bm.faces.new(rings[0][::-1]))
        new.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    part.tag(new)
    return new


def helix(part, a, b, r_coil, r_wire, turns, k=6, sides=3, phase=0.0):
    """Spring from a to b: the number of coils is turns, coil radius r_coil, wire radius r_wire (k points per coil)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    u, v = perp(d)
    n = int(turns * k)
    pts = []
    for i in range(n + 1):
        t = i / n
        ang = 2 * math.pi * turns * t + phase
        pts.append(tuple(a + d * t + (u * math.cos(ang) + v * math.sin(ang)) * r_coil))
    return g.pipe(part, pts, r_wire, sides)


def star_prism(part, c, axis, r, depth, n, h0, h1, cap1=True, phase=0.0):
    """Knurled cylinder (a knob, a flywheel): 2n points around, every other one sunk by depth; from h0 to
    h1 along axis, the h1 end is a fan to the center."""
    bm = part.bm
    a = Vector(axis).normalized()
    u, v = perp(a)
    c = Vector(c)

    def ring(h):
        out = []
        for k in range(2 * n):
            t = math.pi * (k + phase) / n
            rr = r - depth * (k % 2)
            out.append(bm.verts.new(c + a * h + (u * math.cos(t) + v * math.sin(t)) * rr))
        return out
    A, B = ring(h0), ring(h1)
    new = []
    for k in range(2 * n):
        j = (k + 1) % (2 * n)
        q = [A[k], A[j], B[j], B[k]]
        cen = sum((x.co for x in q), Vector()) / 4 - c
        new.append(face(part, q, cen - a * cen.dot(a)))
    if cap1:
        hub = bm.verts.new(c + a * h1)
        for k in range(2 * n):
            new.append(face(part, [B[k], B[(k + 1) % (2 * n)], hub], a))
    return new


def screw(part, c, n, r=0.0045, h=0.002, sides=6):
    """Screw or rivet head along normal n: a low dome (the bottom toward the sheet, no end face)."""
    return lathe(part, [(r, 0.0), (r * 0.92, h * 0.45), (r * 0.55, h * 0.85), (0.0, h)], sides, c, n)


def hexhead(part, c, n, s, h, chamfer=True):
    """Hex bolt head or nut: width across flats s, height h along normal n, a chamfered top."""
    R = s / math.sqrt(3.0)
    prof = [(R, 0.0), (R, h * 0.8), (R * 0.86, h)] if chamfer else [(R, 0.0), (R, h)]
    return lathe(part, prof, 6, c, n, cap1=True, phase=0.0)


def bprism(part, poly, axes, c0, c1, r, seg=1, frame=None):
    """g.prism with rounded edges (r is the chamfer radius, seg the segments)."""
    bm = part.bm
    before = set(bm.faces)
    fs = g.prism(part, poly, axes, c0, c1, frame=frame)
    if r > 0 and seg > 0:
        g.bevel(bm, list({e for f in fs for e in f.edges}), r, seg)
    new = [f for f in bm.faces if f not in before]
    bmesh.ops.recalc_face_normals(bm, faces=new)
    part.tag(new)
    return new


def bbox(part, x0, x1, y0, y1, z0, z1, r, lod, frame=None):
    """g.box with a chamfer on the near LOD only."""
    if lod == 0 and r > 0:
        return g.box(part, x0, x1, y0, y1, z0, z1, r=r, seg=1, frame=frame)
    return g.box(part, x0, x1, y0, y1, z0, z1, frame=frame)


def blade(part, c, axis, ang0, radii, spans, pitch_deg, thick):
    """Fan blade at hub c, rotating about the vector axis: radii - section radii from root to tip, spans - their angular width
    (degrees), ang0 - the middle of the blade (degrees), pitch_deg - the helical pitch. A closed thin
    plate: top, bottom and edges."""
    bm = part.bm
    a = Vector(axis).normalized()
    u, v = perp(a)
    c = Vector(c)
    nt = 4
    k = math.tan(math.radians(pitch_deg))
    top, bot = [], []
    for r, sp in zip(radii, spans):
        rt, rb = [], []
        for j in range(nt + 1):
            dt = math.radians(sp) * (j / nt - 0.5)
            th = math.radians(ang0) + dt
            p = c + (u * math.cos(th) + v * math.sin(th)) * r + a * (k * r * dt)
            rt.append(bm.verts.new(p + a * (thick / 2)))
            rb.append(bm.verts.new(p - a * (thick / 2)))
        top.append(rt)
        bot.append(rb)
    new = []
    nr = len(radii)
    for i in range(nr - 1):
        for j in range(nt):
            new.append(bm.faces.new([top[i][j], top[i][j + 1], top[i + 1][j + 1], top[i + 1][j]]))
            new.append(bm.faces.new([bot[i][j], bot[i + 1][j], bot[i + 1][j + 1], bot[i][j + 1]]))
    edge = [(i, 0) for i in range(nr)] + [(nr - 1, j) for j in range(1, nt + 1)] + \
           [(i, nt) for i in range(nr - 2, -1, -1)] + [(0, j) for j in range(nt - 1, 0, -1)]
    for q in range(len(edge)):
        (i0, j0), (i1, j1) = edge[q], edge[(q + 1) % len(edge)]
        new.append(bm.faces.new([top[i0][j0], bot[i0][j0], bot[i1][j1], top[i1][j1]]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    part.tag(new)
    return new


# =============================================================================
# Unwraps onto pieces of vanilla textures (vsections sections, Part.fixed_uv)
# =============================================================================
def vpart(part):
    """A part with a vanilla texture: the generator sets the UV (kuv skips it)."""
    part.fixed_uv = True
    uv_layer(part)
    return part


def uv_layer(part):
    return part.bm.loops.layers.uv.get("UVMap") or part.bm.loops.layers.uv.new("UVMap")


def _uv(lp, layer, s, t):
    lp[layer].uv = (s, 1.0 - t)


def uv_lathe(part, prof, sides, origin, axis, s0, s1, phase=0.5):
    """Solid of revolution (without poles) with UV onto a piece of the image: prof [(r, h, t)] - radius,
    place along the axis and the image row (a fraction from the top down) for the ring; around - from s0
    to s1. Faces outward along the profile direction."""
    bm = part.bm
    layer = uv_layer(part)
    a = Vector(axis).normalized()
    u, v = perp(a)
    o = Vector(origin)
    rings = []
    for r, h, _ in prof:
        c = o + a * h
        rings.append([bm.verts.new(c + (u * math.cos(2 * math.pi * (k + phase) / sides) +
                                        v * math.sin(2 * math.pi * (k + phase) / sides)) * r) for k in range(sides)])
    new = []
    for i in range(len(prof) - 1):
        dr, dh = prof[i + 1][0] - prof[i][0], prof[i + 1][1] - prof[i][1]
        for k in range(sides):
            j = (k + 1) % sides
            q = [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]
            f = bm.faces.new(q)
            f.normal_update()
            c = sum((x.co for x in q), Vector()) / 4 - o
            rad = c - a * c.dot(a)
            rad = rad.normalized() if rad.length > 1e-9 else u
            if f.normal.dot(rad * dh - a * dr) < 0:
                f.normal_flip()
            st = {rings[i][k]: (k, i), rings[i][j]: (k + 1, i), rings[i + 1][j]: (k + 1, i + 1), rings[i + 1][k]: (k, i + 1)}
            for lp in f.loops:
                kk, ii = st[lp.vert]
                _uv(lp, layer, s0 + (s1 - s0) * kk / sides, prof[ii][2])
            new.append(f)
    part.tag(new)
    return new


def uv_disk(part, center, axis, r, sides, disk, r_in=0.0, f_in=None, phase=0.5):
    """A disc (r_in = 0) or a ring facing along axis with UV onto the image circle disk = (cx, cy, rx, ry)
    - fractions."""
    bm = part.bm
    layer = uv_layer(part)
    a = Vector(axis).normalized()
    u, v = perp(a)
    c = Vector(center)
    cx, cy, rx, ry = disk

    def ang(k):
        return 2 * math.pi * (k + phase) / sides
    outer = [bm.verts.new(c + (u * math.cos(ang(k)) + v * math.sin(ang(k))) * r) for k in range(sides)]
    new = []
    if r_in <= 0:
        f = face(part, outer, a)
        for lp in f.loops:
            k = outer.index(lp.vert)
            _uv(lp, layer, cx + rx * math.cos(ang(k)), cy - ry * math.sin(ang(k)))
        new.append(f)
    else:
        fi = r_in / r if f_in is None else f_in
        inner = [bm.verts.new(c + (u * math.cos(ang(k)) + v * math.sin(ang(k))) * r_in) for k in range(sides)]
        for k in range(sides):
            j = (k + 1) % sides
            f = face(part, [outer[k], outer[j], inner[j], inner[k]], a)
            for lp in f.loops:
                if lp.vert in outer:
                    kk, ff = outer.index(lp.vert), 1.0
                else:
                    kk, ff = inner.index(lp.vert), fi
                _uv(lp, layer, cx + ff * rx * math.cos(ang(kk)), cy - ff * ry * math.sin(ang(kk)))
            new.append(f)
    return new


def uv_project(part, faces, rect, frame=None):
    """Faces onto the image rectangle rect = (s0, s1, t0, t1): each along its own main axis (local with
    frame), stretched to the extent of the faces along the other two axes."""
    layer = uv_layer(part)
    s0, s1, t0, t1 = rect

    def loc(p):
        if frame is None:
            return Vector(p)
        d = Vector(p) - frame.o
        return Vector((d.dot(frame.u), d.dot(frame.v), d.dot(frame.n)))
    pts = [loc(v.co) for f in faces for v in f.verts]
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    for f in faces:
        n = loc(f.calc_center_median() + f.normal) - loc(f.calc_center_median())
        ax = max(range(3), key=lambda i: abs(n[i]))
        ia, ib = [i for i in range(3) if i != ax]
        if ax == 1:
            ia, ib = 0, 2
        for lp in f.loops:
            p = loc(lp.vert.co)
            fa = (p[ia] - lo[ia]) / max(hi[ia] - lo[ia], 1e-6)
            fb = (p[ib] - lo[ib]) / max(hi[ib] - lo[ib], 1e-6)
            _uv(lp, layer, s0 + (s1 - s0) * fa, t1 - (t1 - t0) * fb)


def uv_box(part, x0, x1, y0, y1, z0, z1, rect, frame=None, r=0.0):
    """A box (with chamfer r) with UV onto an image rectangle."""
    fs = g.box(part, x0, x1, y0, y1, z0, z1, r=r, seg=1 if r > 0 else 0, frame=frame)
    uv_project(part, fs, rect, frame)
    return fs
