"""Geometry of the M18 safe that kgeo does not provide: a solid of revolution about any axis (from M09),
a torus, a profile swept along a rounded rectangle (door moulding, closure frame), a rod of oval section
with a given orientation (wheel spokes, mug handle), a Catmull-Rom spline (a cord without kinks), a
knurled handle, screw and bolt heads. The existing kit files are left unchanged, so everything of its
own is here.
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
    """Two axes perpendicular to axis: (axis, u, v) - a right-handed triple."""
    a = Vector(axis).normalized()
    r = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    u = r.cross(a).normalized()
    return u, a.cross(u).normalized()


def lathe(part, prof, sides, origin, axis=(0, 0, 1), cap0=False, cap1=False, phase=0.5):
    """Solid of revolution about axis through origin: prof [(r, h)] - radius and distance along the axis.
    A ring with r = 0 is a pole. Faces look outward along the profile direction (the reverse profile -
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


def ball(part, c, r, sides, axis=(0, 0, 1), rings=6):
    prof = [(r * math.sin(math.pi * i / rings), -r * math.cos(math.pi * i / rings)) for i in range(rings + 1)]
    return lathe(part, prof, sides, c, axis)


def torus(part, c, axis, R, r, n, m, phase=0.0):
    """Torus about axis through c: radius R (n segments around), section r (m sides)."""
    bm = part.bm
    a = Vector(axis).normalized()
    u, v = perp(a)
    c = Vector(c)
    rings = []
    for i in range(n):
        t = 2 * math.pi * (i + phase) / n
        d = u * math.cos(t) + v * math.sin(t)
        rings.append([bm.verts.new(c + d * (R + r * math.cos(2 * math.pi * k / m)) + a * (r * math.sin(2 * math.pi * k / m)))
                      for k in range(m)])
    new = []
    for i in range(n):
        t = 2 * math.pi * (i + 0.5 + phase) / n
        cc = c + (u * math.cos(t) + v * math.sin(t)) * R
        for k in range(m):
            q = [rings[i][k], rings[i][(k + 1) % m], rings[(i + 1) % n][(k + 1) % m], rings[(i + 1) % n][k]]
            cen = sum((x.co for x in q), Vector()) / 4
            f = bm.faces.new(q)
            f.normal_update()
            if f.normal.dot(cen - cc) < 0:
                f.normal_flip()
            new.append(f)
    part.tag(new)
    return new


def oval_tube(part, pts, radii, sides, ref, caps=True):
    """Rod of elliptical section along a polyline: radii[i] = (r across ref, r along ref); the section axis
    b is ref straightened to a right angle to the rod (a spoke is thinner along the wheel axis, a mug
    handle is wider along the mug axis)."""
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


def rrect2(cx, cy, w, h, r, k):
    """Rounded rectangle w x h centred at (cx, cy): 4 (k + 1) points counter-clockwise."""
    r = min(r, w / 2 - 1e-5, h / 2 - 1e-5)
    pts = []
    for sx, sy, a0 in ((1, -1, -90), (1, 1, 0), (-1, 1, 90), (-1, -1, 180)):
        ox, oy = cx + sx * (w / 2 - r), cy + sy * (h / 2 - r)
        for i in range(k + 1):
            t = math.radians(a0 + 90.0 * i / k)
            pts.append((ox + r * math.cos(t), oy + r * math.sin(t)))
    return pts


def frame_molding(part, cx, cz, w, h, r, k, prof, y0, out=-1.0):
    """Profile swept along a rounded rectangle in the x-z plane (moulding, closure frame): prof [(a, d)] -
    a is the shift outward from the line (w x h, corner radius r), d is the height above plane y0 toward
    out (the face is toward -y). Faces look away from the profile body."""
    bm = part.bm
    rings = []
    for a, d in prof:
        y = y0 + out * d
        rings.append([bm.verts.new((x, y, z)) for x, z in rrect2(cx, cz, w + 2 * a, h + 2 * a, r + a, k)])
    hx, hz = w / 2 - r, h / 2 - r
    new = []
    for i in range(len(prof) - 1):
        da, dd = prof[i + 1][0] - prof[i][0], prof[i + 1][1] - prof[i][1]
        A, B = rings[i], rings[i + 1]
        n = len(A)
        for j in range(n):
            jj = (j + 1) % n
            q = [A[j], A[jj], B[jj], B[j]]
            c = sum((v.co for v in q), Vector()) / 4
            px = min(max(c.x, cx - hx), cx + hx)
            pz = min(max(c.z, cz - hz), cz + hz)
            nin = Vector((c.x - px, 0.0, c.z - pz))
            nin = nin.normalized() if nin.length > 1e-9 else Vector((0.0, 0.0, 1.0))
            want = -dd * nin + da * Vector((0.0, out, 0.0))
            new.append(face(part, q, want))
    return new


def star_prism(part, c, axis, r, depth, n, h0, h1, cap1=True, phase=0.0):
    """Knurled cylinder (disc knob): 2n points around, every other one recessed by depth; from h0 to h1
    along axis, the end h1 is a fan toward the centre."""
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
    """Screw or rivet head along normal n: a low dome (bottom toward the sheet, no end cap)."""
    return lathe(part, [(r, 0.0), (r * 0.92, h * 0.45), (r * 0.55, h * 0.85), (0.0, h)], sides, c, n)


def slotted(part, dark, c, n, r=0.0045, h=0.0018, sides=8, ang=0.3):
    """Slotted screw: a dome and a dark slot across (dark is the slot part)."""
    screw(part, c, n, r, h, sides)
    n = Vector(n).normalized()
    u, v = perp(n)
    d = u * math.cos(ang) + v * math.sin(ang)
    w = d.cross(n).normalized()
    p = Vector(c) + n * (h * 0.86)
    q = [p - d * r * 0.85 - w * 0.0005, p + d * r * 0.85 - w * 0.0005, p + d * r * 0.85 + w * 0.0005,
         p - d * r * 0.85 + w * 0.0005]
    face(dark, [dark.bm.verts.new(x) for x in q], n)


def hexhead(part, c, n, s, h, chamfer=True):
    """Hexagonal bolt head or nut: s across flats, height h along normal n, chamfered top."""
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


def disc_grid(part, c, rings, sectors, height_fn, want=(0, 0, 1)):
    """Uneven disc (top of a heap of bolts): rings - radii from the edge to the centre, point height -
    height_fn(r, angle)."""
    bm = part.bm
    c = Vector(c)
    loops = []
    for r in rings:
        if r < 1e-7:
            loops.append([bm.verts.new(c + Vector((0, 0, height_fn(0.0, 0.0))))])
            continue
        loops.append([bm.verts.new(c + Vector((r * math.cos(2 * math.pi * k / sectors), r * math.sin(2 * math.pi * k / sectors),
                                               height_fn(r, 2 * math.pi * k / sectors)))) for k in range(sectors)])
    new = []
    for i in range(len(loops) - 1):
        A, B = loops[i], loops[i + 1]
        for k in range(sectors):
            j = (k + 1) % sectors
            q = [A[k], A[j], B[0]] if len(B) == 1 else [A[k], A[j], B[j], B[k]]
            new.append(face(part, q, want))
    return loops[0], new
