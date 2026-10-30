"""M13 geometry that kgeo does not provide: solids of revolution in any coordinate frame, rivets with a
domed head, chain links, an angle bar with a fillet and slanted cuts, a bead weld, rounded prisms with a
chamfer, a torus, smooth curves. Parts are kgeo.Part, faces look outward (as in kgeo: kexport flips them
inward for p3d itself).

Blender axes: X is width, Y is depth (face toward -Y), Z is up.
"""
import math

from mathutils import Vector

import kgeo as g


def face(part, verts, want):
    """Face from bmesh vertices, turned to look toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    part.tag([f])
    return f


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, from M04): k points per segment."""
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


def frame_z(cx, cy, deg, z):
    """Frame of an item lying on a horizontal support: u along the item at angle deg from +X, v across,
    n up."""
    a = math.radians(deg)
    return g.Frame((cx, cy, z), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))


def basis(axis):
    """Rotation axis (from M07): (a, b, w) - two transverse and the longitudinal unit vectors; axis is "x",
    "-y", ... or a vector."""
    if isinstance(axis, str):
        w = Vector([1.0 if c == axis[-1] else 0.0 for c in "xyz"]) * (-1.0 if axis.startswith("-") else 1.0)
    else:
        w = Vector(axis).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(w.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    a = ref.cross(w).normalized()
    return a, w.cross(a).normalized(), w


def lathe(part, prof, sides, center, axis="z", closed=False, caps=(False, False), phase=0.0, ab=None):
    """Solid of revolution (from M07): prof [(r, h)] is the section (r from the axis, h along axis from
    center), traversed along the outer surface in the direction of growing h (a closed one counter-clockwise
    in the r, h axes): then the faces look outward. r = 0 is a point on the axis (a fan of triangles).
    caps - lids of the first and last ring. ab - own transverse axes (tilted watch: 12 o'clock along a)."""
    a, b, w = basis(axis)
    if ab is not None:
        a, b = Vector(ab[0]).normalized(), Vector(ab[1]).normalized()
    c = Vector(center)
    bm = part.bm
    angs = [phase + 2 * math.pi * k / sides for k in range(sides)]
    rings = []
    for r, h in prof:
        if r < 1e-7:
            rings.append(bm.verts.new(c + w * h))
        else:
            rings.append([bm.verts.new(c + (a * math.cos(t) + b * math.sin(t)) * r + w * h) for t in angs])
    idx = list(range(len(prof))) + ([0] if closed else [])
    new = []
    for i0, i1 in zip(idx, idx[1:]):
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
    part.tag(new)
    return new


def rrect(x0, x1, y0, y1, r, n):
    """Rectangle with rounded corners (n segments per corner), counter-clockwise; n = 0 - sharp (from M07)."""
    if n <= 0 or r <= 1e-6:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    out = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90.0), (x1 - r, y1 - r, 0.0), (x0 + r, y1 - r, 90.0), (x0 + r, y0 + r, 180.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def slab(part, x0, x1, y0, y1, z0, z1, rc=0.0, nc=0, re=0.0, ne=0, rb=0.0, nb=0, frame=None, caps=(True, True)):
    """Slab (from M07): in plan a rectangle with rounded corners rc (nc segments), the top edge rounded by
    re (ne segments), the bottom by rb (nb). frame is a local frame: x -> u, y -> v, z -> n. caps - lids of
    the bottom and top (the side pressed against something can be left open)."""
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
    part.tag(new)
    return new


def rivet(part, c, n, r=0.0065, h=0.0038, sides=6, dome=True):
    """Rivet with a domed head (GOST 10299) on a surface with normal n: a ring at the sheet, a ring at ~2/3
    of the height and the crown (dome) or a hexagonal pyramid (farther from the eye). The bottom sits
    0.8 mm into the sheet: no gap on a convex sheet."""
    n = Vector(n).normalized()
    prof = [(r, 0.0), (r * 0.72, h * 0.70), (0.0, h + 0.0008)] if dome else [(r, 0.0), (0.0, h + 0.0008)]
    lathe(part, prof, sides, Vector(c) - n * 0.0008, n)


def torus(part, fr, R, r, nu, nv):
    """Torus in the (u, v) plane of frame fr: R is the radius of the centre line, r of the rod."""
    bm = part.bm
    rings = []
    for i in range(nu):
        a = 2 * math.pi * i / nu
        d = fr.u * math.cos(a) + fr.v * math.sin(a)
        c = fr.o + d * R
        rings.append([bm.verts.new(c + d * (r * math.cos(2 * math.pi * k / nv)) + fr.n * (r * math.sin(2 * math.pi * k / nv)))
                      for k in range(nv)])
    for i in range(nu):
        r0, r1 = rings[i], rings[(i + 1) % nu]
        a = 2 * math.pi * (i + 0.5) / nu
        mid = fr.o + (fr.u * math.cos(a) + fr.v * math.sin(a)) * R
        for k in range(nv):
            j = (k + 1) % nv
            q = [r0[k], r0[j], r1[j], r1[k]]
            face(part, q, sum((v.co for v in q), Vector()) / 4 - mid)


def chain_link(part, c, t, w, length, width, wire, npath=8, sides=5):
    """Chain link: an oval loop of rod `wire`, outer length x width; t is along the link, w across (the link
    plane is t, w). The centre line is two semicircles of npath/2 points."""
    bm = part.bm
    t, w = Vector(t).normalized(), Vector(w).normalized()
    nrm = t.cross(w).normalized()
    rr = wire / 2
    rc = width / 2 - rr                      # radius of the centre-line arc
    hs = length / 2 - rr - rc                # half of the straight part
    half = npath // 2
    path = []
    for s, sgn in ((hs, 1), (-hs, -1)):
        for k in range(half):
            a = -math.pi / 2 + math.pi * k / (half - 1)
            path.append(Vector(c) + t * (s + sgn * rc * math.cos(a)) + w * (sgn * rc * math.sin(a)))
    n = len(path)
    rings = []
    for i in range(n):
        tan = (path[(i + 1) % n] - path[i - 1]).normalized()
        rad = nrm.cross(tan).normalized()
        rings.append([bm.verts.new(path[i] + rad * (rr * math.cos(2 * math.pi * k / sides)) +
                                   nrm * (rr * math.sin(2 * math.pi * k / sides))) for k in range(sides)])
    for i in range(n):
        r0, r1 = rings[i], rings[(i + 1) % n]
        mid = (path[i] + path[(i + 1) % n]) / 2
        for k in range(sides):
            j = (k + 1) % sides
            q = [r0[k], r0[j], r1[j], r1[k]]
            face(part, q, sum((v.co for v in q), Vector()) / 4 - mid)


def round_rect(w, h, r, seg, cx=0.0, cy=0.0):
    """Rectangle w x h with rounded corners (seg segments per corner), counter-clockwise."""
    pts = []
    r = min(r, w / 2 - 1e-5, h / 2 - 1e-5)
    for (sx, sy), a0 in (((1, -1), -90), ((1, 1), 0), ((-1, 1), 90), ((-1, -1), 180)):
        ccx, ccy = cx + sx * (w / 2 - r), cy + sy * (h / 2 - r)
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            pts.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
    return pts


def loft(part, rings_2d, levels, P, caps=(True, True)):
    """Prism by layers: rings_2d[i] is a contour (same number of points) at level levels[i];
    P(a, b, c) -> point. Lids are n-gons; faces outward (recalc)."""
    import bmesh
    bm = part.bm
    before = set(bm.faces)
    rings = [[bm.verts.new(P(a, b, c)) for a, b in poly] for poly, c in zip(rings_2d, levels)]
    n = len(rings[0])
    faces = []
    for i in range(len(rings) - 1):
        for k in range(n):
            j = (k + 1) % n
            faces.append(bm.faces.new([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]))
    if caps[0]:
        faces.append(bm.faces.new(rings[0][::-1]))
    if caps[1]:
        faces.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    part.tag([f for f in bm.faces if f not in before])
    return faces


def chamfer_prism(part, outline, c0, c1, ch, P):
    """Prism with a chamfer ch at both ends: outline(inset) -> contour (same number of points), the ends are
    already at ch; P(a, b, c) -> point."""
    rings = [outline(ch), outline(0.0), outline(0.0), outline(ch)]
    return loft(part, rings, [c0, c0 + ch, c1 - ch, c1], P)


def angle_section(L, t, r1, seg=3):
    """Section of an equal-leg angle (GOST 8509) from the outer corner (0, 0): legs along +a and +b of
    length L, thickness t, fillet r1 in the inner corner; counter-clockwise."""
    pts = [(0.0, 0.0), (L, 0.0), (L, t * 0.75), (L - t * 0.25, t)]
    c = (t + r1, t + r1)
    for k in range(seg + 1):
        a = math.radians(270 - 90 * k / seg)
        pts.append((c[0] + r1 * math.cos(a), c[1] + r1 * math.sin(a)))
    pts += [(t, L - t * 0.25), (t * 0.75, L), (0.0, L)]
    return pts


def angle_iron(part, poly, P, c0, c1, cut0=(0.0, 0.0), cut1=(0.0, 0.0)):
    """Angle bar along the third axis from c0 to c1; the cuts are slanted: the end is shifted by
    cut[0] * a + cut[1] * b (angle grinder, uneven)."""
    import bmesh
    bm = part.bm
    before = set(bm.faces)
    bot = [bm.verts.new(P(a, b, c0 + cut0[0] * a + cut0[1] * b)) for a, b in poly]
    top = [bm.verts.new(P(a, b, c1 + cut1[0] * a + cut1[1] * b)) for a, b in poly]
    faces = [bm.faces.new(bot[::-1]), bm.faces.new(top)]
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new([bot[i], bot[j], top[j], top[i]]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    part.tag([f for f in bm.faces if f not in before])


def weld(part, a, b, r, seed, n=6, sides=5):
    """Bead weld from a to b: a rod with an uneven section (sags), the ends tapered."""
    a, b = Vector(a), Vector(b)
    pts, radii = [], []
    for i in range(n + 1):
        s = i / n
        k = 0.55 + 0.45 * math.sin(math.pi * s) ** 0.5
        wob = 1.0 + 0.22 * math.sin(seed * 7.3 + i * 2.9) + 0.12 * math.sin(seed * 3.1 + i * 5.3)
        pts.append(a.lerp(b, s))
        radii.append((r * k * wob, r * k * wob * 0.85))
    g.tube_var(part, pts, radii, sides)


def resample(pts, step):
    """Polyline -> points at equal steps of length: [(point, tangent)]."""
    P_ = [Vector(p) for p in pts]
    seg = [(P_[i + 1] - P_[i]).length for i in range(len(P_) - 1)]
    total = sum(seg)
    n = max(1, int(round(total / step)))
    out, i, acc = [], 0, 0.0
    for k in range(n + 1):
        d = total * k / n
        while i < len(seg) - 1 and acc + seg[i] < d:
            acc += seg[i]
            i += 1
        t = min(max((d - acc) / max(seg[i], 1e-9), 0.0), 1.0)
        out.append((P_[i].lerp(P_[i + 1], t), (P_[i + 1] - P_[i]).normalized()))
    return out
