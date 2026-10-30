"""M17 geometry that kgeo does not provide: solids of revolution in any coordinate frame, rivets with a
domed head, a torus, an angle bar with a fillet, a weld, slabs with rounded edges, rounded rectangles,
smooth curves (after M07 and M13). Parts are kgeo.Part, faces look outward - toward whoever looks at them
(kexport flips them itself for p3d).

Blender axes: X is width, Y is depth (the customer side is -Y), Z is up.
"""
import math

import bmesh
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
    """Rotation axis: (a, b, w) - two transverse and the longitudinal unit vectors; axis is "x", "-y", ...
    or a vector."""
    if isinstance(axis, str):
        w = Vector([1.0 if c == axis[-1] else 0.0 for c in "xyz"]) * (-1.0 if axis.startswith("-") else 1.0)
    else:
        w = Vector(axis).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(w.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    a = ref.cross(w).normalized()
    return a, w.cross(a).normalized(), w


def lathe(part, prof, sides, center, axis="z", closed=False, caps=(False, False), phase=0.0):
    """Solid of revolution: prof [(r, h)] is the section (r from the axis, h along axis from center);
    traversed along the visible surface in the direction of growing h: then the faces look outward (the
    reverse direction - inward, like a pipe looked into). r = 0 is a point on the axis (a fan). caps - lids
    of the first and last ring."""
    a, b, w = basis(axis)
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
    return new


def rrect(x0, x1, y0, y1, r, n):
    """Rectangle with rounded corners (n segments per corner), counter-clockwise; n = 0 - sharp."""
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
    re (ne segments), the bottom by rb (nb). frame is a local frame: x -> u, y -> v, z -> n."""
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


def rivet(part, c, n, r=0.0065, h=0.0038, sides=6, dome=True):
    """Rivet with a domed head (GOST 10299) or a bolt head on a surface with normal n. The bottom sits
    0.8 mm into the sheet: no gap."""
    n = Vector(n).normalized()
    prof = [(r, 0.0), (r * 0.72, h * 0.70), (0.0, h + 0.0008)] if dome else [(r, 0.0), (0.0, h + 0.0008)]
    lathe(part, prof, sides, Vector(c) - n * 0.0008, n)


def torus(part, fr, R, r, nu, nv, arc=(0.0, 2 * math.pi)):
    """Torus (or a torus arc `arc`, rad) in the (u, v) plane of frame
    fr: R is the radius of the centre line, r of the rod."""
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
    for i in range(nu):
        r0, r1 = rings[i], rings[(i + 1) % n_ring]
        a = arc[0] + (arc[1] - arc[0]) * (i + 0.5) / nu
        mid = fr.o + (fr.u * math.cos(a) + fr.v * math.sin(a)) * R
        for k in range(nv):
            j = (k + 1) % nv
            q = [r0[k], r0[j], r1[j], r1[k]]
            face(part, q, sum((v.co for v in q), Vector()) / 4 - mid)


def angle_section(L, t, r1, seg=2):
    """Section of an equal-leg angle (GOST 8509) from the outer corner (0, 0): legs along +a and +b of
    length L, thickness t, fillet r1 in the inner corner, leg edges rounded; counter-clockwise."""
    pts = [(0.0, 0.0), (L, 0.0), (L, t * 0.75), (L - t * 0.25, t)]
    if seg <= 0:                                  # farther from the eye: a sharp inner corner
        return pts + [(t, t), (t, L - t * 0.25), (t * 0.75, L), (0.0, L)]
    c = (t + r1, t + r1)
    for k in range(seg + 1):
        a = math.radians(270 - 90 * k / seg)
        pts.append((c[0] + r1 * math.cos(a), c[1] + r1 * math.sin(a)))
    pts += [(t, L - t * 0.25), (t * 0.75, L), (0.0, L)]
    return pts


def prism_poly(part, poly, P, c0, c1, cut0=(0.0, 0.0), cut1=(0.0, 0.0)):
    """Prism by the section poly (points (a, b)) along the third axis from c0 to c1; P(a, b, c) -> point.
    The cuts are slanted: the end is shifted by cut[0] * a + cut[1] * b (angle grinder, uneven). Closed -
    normals outward."""
    bm = part.bm
    bot = [bm.verts.new(P(a, b, c0 + cut0[0] * a + cut0[1] * b)) for a, b in poly]
    top = [bm.verts.new(P(a, b, c1 + cut1[0] * a + cut1[1] * b)) for a, b in poly]
    faces = [bm.faces.new(bot[::-1]), bm.faces.new(top)]
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new([bot[i], bot[j], top[j], top[i]]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    part.tag(faces)
    return faces


def weld(part, a, b, r, seed, n=4, sides=4):
    """Bead weld from a to b: a rod with an uneven section (sags), the ends tapered."""
    a, b = Vector(a), Vector(b)
    pts, radii = [], []
    for i in range(n + 1):
        s = i / n
        k = 0.45 + 0.55 * math.sin(math.pi * s) ** 0.5
        wob = 1.0 + 0.22 * math.sin(seed * 7.3 + i * 2.9) + 0.12 * math.sin(seed * 3.1 + i * 5.3)
        pts.append(a.lerp(b, s))
        radii.append((r * k * wob, r * k * wob * 0.8))
    g.tube_var(part, pts, radii, sides)


def blob(part, c, n, r, h, sides=5, seed=0.0):
    """Weld blob (tack) on a surface with normal n: a flattened uneven dome."""
    n = Vector(n).normalized()
    a, b, _ = basis(n)
    bm = part.bm
    c = Vector(c) - n * 0.0005
    ring = []
    for k in range(sides):
        t = 2 * math.pi * k / sides + seed
        rr = r * (1.0 + 0.25 * math.sin(seed * 5.1 + k * 2.3))
        ring.append(bm.verts.new(c + (a * math.cos(t) + b * math.sin(t)) * rr))
    top = bm.verts.new(c + n * h + a * (0.2 * r * math.sin(seed)))
    for k in range(sides):
        j = (k + 1) % sides
        face(part, [ring[k], ring[j], top], n + (ring[k].co + ring[j].co) / 2 - c)


def box_to(part, a, b, w, h, up=(0, 0, 1)):
    """Bar from point a to point b with cross-section w (across) x h (along up)."""
    a, b = Vector(a), Vector(b)
    u = (b - a).normalized()
    n = Vector(up) - u * Vector(up).dot(u)
    n.normalize()
    v = n.cross(u)
    fr = g.Frame(a, u, v, n)
    return g.box(part, 0.0, (b - a).length, -w / 2, w / 2, -h / 2, h / 2, frame=fr)


def rod(part, a, b, r, sides):
    """Cylinder between points a and b."""
    return g.pipe(part, [tuple(a), tuple(b)], r, sides)


def loft_inner(part, rings, centre, extra_cap=None):
    """Bowl by rings of points (same count, top to bottom), faces inward, toward the axis centre (a point on
    the bowl axis); extra_cap - close the bottom ring with a floor facing up."""
    bm = part.bm
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
    c = Vector(centre)
    n = len(rings[0])
    for r0, r1 in zip(vr, vr[1:]):
        for k in range(n):
            j = (k + 1) % n
            q = [r0[k], r0[j], r1[j], r1[k]]
            m = sum((v.co for v in q), Vector()) / 4
            want = Vector((c.x - m.x, c.y - m.y, 0.0))
            face(part, q, want if want.length > 1e-6 else Vector((0, 0, 1)))
    if extra_cap:
        face(part, vr[-1], Vector((0, 0, 1)))
    return vr


def ring_flat(part, inner, outer, z, up=True):
    """Flat ring between contours inner and outer (same number of points) at height z."""
    bm = part.bm
    vi = [bm.verts.new((a, b, z)) for a, b in inner]
    vo = [bm.verts.new((a, b, z)) for a, b in outer]
    n = len(inner)
    for k in range(n):
        j = (k + 1) % n
        face(part, [vi[k], vi[j], vo[j], vo[k]], Vector((0, 0, 1 if up else -1)))
    return vi, vo


def wall_band(part, outline, z0, z1, centre):
    """Side band along the contour outline (points (a, b)) from z0 to z1, faces outward from centre."""
    bm = part.bm
    lo = [bm.verts.new((a, b, z0)) for a, b in outline]
    hi = [bm.verts.new((a, b, z1)) for a, b in outline]
    c = Vector(centre)
    n = len(outline)
    for k in range(n):
        j = (k + 1) % n
        q = [lo[k], lo[j], hi[j], hi[k]]
        m = sum((v.co for v in q), Vector()) / 4
        face(part, q, Vector((m.x - c.x, m.y - c.y, 0.0)))


def square_ring(s, n, phase=0.0):
    """Points of a square with half-side s at the same angles as a circle of n points (the square corners
    land on vertices when n is a multiple of 8): for a flat "square - circle" ring."""
    out = []
    for k in range(n):
        t = phase + 2 * math.pi * k / n
        ct, st = math.cos(t), math.sin(t)
        m = max(abs(ct), abs(st))
        out.append((s * ct / m, s * st / m))
    return out


def fan_blade(part, centre, axis_a, axis_b, axis_w, ang, stations, thick):
    """Axial fan blade: stations [(r, half-chord, pitch angle, deg)] from the hub to the tip; axis_a, axis_b -
    the plane of rotation, axis_w - the axis (toward the observer). A thin box by the sections."""
    bm = part.bm
    c = Vector(centre)
    rings = []
    for r, hc, beta in stations:
        rad = axis_a * math.cos(ang) + axis_b * math.sin(ang)
        tng = -axis_a * math.sin(ang) + axis_b * math.cos(ang)
        bt = math.radians(beta)
        chord = tng * math.cos(bt) + axis_w * math.sin(bt)
        nrm = -tng * math.sin(bt) + axis_w * math.cos(bt)
        p = c + rad * r
        rings.append([bm.verts.new(p + chord * s * hc + nrm * t * thick / 2)
                      for s, t in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    for i in range(len(rings) - 1):
        r0, r1 = rings[i], rings[i + 1]
        mid = sum((v.co for v in r0 + r1), Vector()) / 8
        for k in range(4):
            j = (k + 1) % 4
            q = [r0[k], r0[j], r1[j], r1[k]]
            face(part, q, sum((v.co for v in q), Vector()) / 4 - mid)
    tip = rings[-1]
    face(part, tip, sum((v.co for v in tip), Vector()) / 4 - c)
    root = rings[0]
    face(part, root, c - sum((v.co for v in root), Vector()) / 4)


def triangulate_safe(parts):
    """Like kgeo.triangulate, but without empty parts."""
    out = [p for p in parts if len(p.bm.faces)]
    for p in out:
        bmesh.ops.triangulate(p.bm, faces=p.bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
        p.bm.normal_update()
    return out
