"""Small parts for M24: solids of revolution along any axis (with knurling), frames and plates with
rounded corners in the sloped planes of the console, a prism with a chamfer, screws, bolts, socket-head
screws, toggles, knobs, lamps, buttons, hinges, louvers, connectors, clamps.

lathe, rrect, louvers and hinges are from the M06 generator (m06_bits.py, where everything sticks out
to -y); here the controls are generalized to the panel coordinate system (kgeo.Frame: u along the
panel, v up along it, n outward) - on the sloped desk and the top panel of the console everything
sticks out along n. The generator creates the parts (kgeo.Part) and passes them in ready: it picks
the material region.

Blender axes: X is width, Y is depth (the face looks to -Y), Z is up.
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


def _basis(axis, ref=None):
    a = Vector(axis).normalized()
    r = Vector(ref) if ref is not None else (Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0)))
    u = r - a * r.dot(a)
    if u.length < 1e-9:
        u = Vector((1, 0, 0)) - a * a.x
    u.normalize()
    return a, u, a.cross(u)


def lathe(part, base, axis, prof, sides, knurl=(), depth=0.0, cap0=False, cap1=True, phase=0.0, ref=None):
    """Solid of revolution around axis from point base: prof [(r, s)] - radius and distance along the
    axis (s grows). knurl - indices of knurled rings (every other vertex sunk by depth); a ring with
    r = 0 is a point (a single vertex). cap0 / cap1 - close the first / last ring. phase - mesh rotation
    (rad), ref - where the angle is measured from (e.g. a hex nut with a flat up)."""
    bm = part.bm
    a, u, v = _basis(axis, ref)
    b0 = Vector(base)
    rings = []
    for i, (r, s) in enumerate(prof):
        c = b0 + a * s
        if r <= 1e-7:
            rings.append(bm.verts.new(c))
            continue
        ring = []
        for k in range(sides):
            t = phase + 2 * math.pi * k / sides
            rr = r - (depth if (i in knurl and k % 2) else 0.0)
            ring.append(bm.verts.new(c + (u * math.cos(t) + v * math.sin(t)) * rr))
        rings.append(ring)
    new = []
    for i in range(len(rings) - 1):
        r0, r1 = rings[i], rings[i + 1]
        mid = b0 + a * ((prof[i][1] + prof[i + 1][1]) / 2)
        for k in range(sides):
            j = (k + 1) % sides
            if isinstance(r0, list) and isinstance(r1, list):
                q = [r0[k], r0[j], r1[j], r1[k]]
            elif isinstance(r0, list):
                q = [r0[k], r0[j], r1]
            elif isinstance(r1, list):
                q = [r0, r1[j], r1[k]]
            else:
                continue
            cen = sum((x.co for x in q), Vector()) / len(q)
            out = cen - mid
            out -= a * out.dot(a)
            # ring across the axis (a step, the end of a skirt) - faces along the axis
            dr = prof[i + 1][0] - prof[i][0]
            ds = prof[i + 1][1] - prof[i][1]
            want = out.normalized() * ds - a * dr if out.length > 1e-9 else -a * dr
            new.append(face(part, q, want if want.length > 1e-9 else out))
    if cap0 and isinstance(rings[0], list):
        new.append(face(part, rings[0], -a))
    if cap1 and isinstance(rings[-1], list):
        new.append(face(part, rings[-1], a))
    bm.normal_update()
    part.tag(new)
    return new


def rrect(cx, cz, w, h, r, n=3):
    """Rounded rectangle in the (a, b) plane: points counterclockwise."""
    r = max(0.0, min(r, w / 2 - 1e-5, h / 2 - 1e-5))
    if r < 1e-5 or n < 1:
        return [(cx + w / 2, cz + h / 2), (cx - w / 2, cz + h / 2), (cx - w / 2, cz - h / 2), (cx + w / 2, cz - h / 2)]
    pts = []
    for ox, oz, a0 in ((cx + w / 2 - r, cz + h / 2 - r, 0), (cx - w / 2 + r, cz + h / 2 - r, 90),
                       (cx - w / 2 + r, cz - h / 2 + r, 180), (cx + w / 2 - r, cz - h / 2 + r, 270)):
        for i in range(n + 1):
            t = math.radians(a0 + 90.0 * i / n)
            pts.append((ox + r * math.cos(t), oz + r * math.sin(t)))
    return pts


def prism_bev(part, poly, axes, c0, c1, r=0.0, seg=0, frame=None):
    """kgeo.prism with a chamfer (rounding) of all edges r, seg."""
    bm = part.bm
    before = set(bm.faces)
    g.prism(part, poly, axes, c0, c1, frame=frame)
    new = [f for f in bm.faces if f not in before]
    if r > 0 and seg > 0:
        g.bevel(bm, list({e for f in new for e in f.edges}), r, seg)
        new = [f for f in bm.faces if f not in before]
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def plate(part, fr, ca, cb, w, h, r, c0, c1, n=2):
    """Plate with rounded corners on panel fr (an instrument flange, a screen holder, a nameplate)."""
    return g.prism(part, rrect(ca, cb, w, h, r, n), (0, 1), c0, c1, frame=fr)


def bezel(part, fr, ca, cb, outer, inner, c_back, c_front, c_in=None, n=3):
    """Frame with rounded corners on panel fr (a display window): outer and inner are (width, height,
    corner radius); from c_back outward to c_front, into the opening to c_in. Faces: front, outer side,
    inner side."""
    o = rrect(ca, cb, outer[0], outer[1], max(outer[2], 2e-5), n=n)
    i_ = rrect(ca, cb, inner[0], inner[1], max(inner[2], 2e-5), n=n)
    c_in = c_back if c_in is None else c_in
    bm = part.bm
    ob = [bm.verts.new(fr.p(a, b, c_back)) for a, b in o]
    of = [bm.verts.new(fr.p(a, b, c_front)) for a, b in o]
    if_ = [bm.verts.new(fr.p(a, b, c_front)) for a, b in i_]
    ib = [bm.verts.new(fr.p(a, b, c_in)) for a, b in i_]
    new = []
    m = len(o)
    for k in range(m):
        j = (k + 1) % m
        new.append(face(part, [of[k], of[j], if_[j], if_[k]], fr.n))
        oc = fr.u * ((o[k][0] + o[j][0]) / 2 - ca) + fr.v * ((o[k][1] + o[j][1]) / 2 - cb)
        new.append(face(part, [ob[k], ob[j], of[j], of[k]], oc))
        icv = fr.u * ((i_[k][0] + i_[j][0]) / 2 - ca) + fr.v * ((i_[k][1] + i_[j][1]) / 2 - cb)
        new.append(face(part, [if_[k], if_[j], ib[j], ib[k]], -icv))
    bm.normal_update()
    part.tag(new)
    return new


def disc(part, fr, a, b, c, r, sides):
    """Flat disc facing outward (+n) on panel fr: glass, a scale face, a screen."""
    bm = part.bm
    vs = [bm.verts.new(fr.p(a + r * math.cos(2 * math.pi * k / sides), b + r * math.sin(2 * math.pi * k / sides), c))
          for k in range(sides)]
    f = face(part, vs, fr.n)
    return part.tag([f])


def strip(part, a, b, n, half_w, half_t):
    """Strip from a to b on a face with normal n (a knob mark, a strap)."""
    a, b = Vector(a), Vector(b)
    u = b - a
    ln = u.length
    u.normalize()
    n = Vector(n).normalized()
    v = n.cross(u)
    g.box(part, 0.0, ln, -half_w, half_w, -half_t, half_t, frame=g.Frame(a, u, v, n))


# =============================================================================
# Fasteners
# =============================================================================
def screw(part, base, axis, r=0.0035, sides=6, washer=False):
    """Round-head screw (and a washer) on a surface at point base, outward along axis."""
    if washer:
        lathe(part, base, axis, [(r * 1.55, 0.0), (r * 1.3, 0.0010)], sides, cap1=False)
    lathe(part, base, axis, [(r, 0.0), (0.82 * r, 0.0016), (0.0, 0.0026)], sides)


def shcs(head, sock, base, axis, r=0.0065, h=0.0065, lod=0):
    """Socket-head cap screw (DIN 912): a chamfered head, a dark hexagon in the end (part sock; None -
    without it)."""
    a = Vector(axis).normalized()
    if lod > 0:
        lathe(head, base, a, [(r, 0.0), (r, h)], 6)
        return
    lathe(head, base, a, [(r, 0.0), (r, h - 0.0009), (r * 0.86, h)], 8)
    if sock is not None:
        lathe(sock, Vector(base) + a * (h + 0.00015), a, [(r * 0.46, 0.0)], 6, cap1=True)


def hex_bolt(part, base, axis, r=0.0085, h=0.0055, lod=0, washer=True, ref=None):
    """Hex-head bolt (or nut) on a washer."""
    a = Vector(axis).normalized()
    s = 0.0
    if washer and lod == 0:
        lathe(part, base, a, [(r * 1.22, 0.0), (r * 1.22, 0.0012)], 8)
        s = 0.0012
    lathe(part, Vector(base) + a * s, a, [(r, 0.0), (r, h)], 6, ref=ref)


# =============================================================================
# Controls on panel fr (everything sticks out along fr.n)
# =============================================================================
def toggle(nut, lever, fr, a, b, c, lod=0, up=True, scale=1.0):
    """MT toggle switch: a hex nut, a bushing, a lever with a ball, tilted up along the panel (up) or
    down. Returns the point of the lever axis (for the bone)."""
    n = fr.n
    base = fr.p(a, b, c)
    if lod > 0:
        lathe(nut, base, n, [(0.0055, 0.0), (0.0055, 0.004)], 6, ref=fr.u)
        return base + n * 0.004
    lathe(nut, base, n, [(0.0068, 0.0), (0.0068, 0.0028)], 6, ref=fr.u)
    lathe(nut, base + n * 0.0028, n, [(0.0040, 0.0), (0.0040, 0.0056), (0.0026, 0.0066)], 8)
    tilt = math.radians(18.0) * (1 if up else -1)
    d = n * math.cos(tilt) + fr.v * math.sin(tilt)
    pb = base + n * 0.0094
    s = scale
    if lever is not None:
        lathe(lever, pb, d, [(0.0018, 0.0), (0.0014, 0.015 * s), (0.0023, 0.0172 * s), (0.0, 0.0205 * s)], 6)
    return pb


def knob(body, ptr, fr, a, b, c, r, kind="skirt", lod=0, angle=0.0):
    """Instrument knob: "skirt" - with a skirt and a knurled body (a switch, a regulator), "plain" -
    knurled without a skirt. The mark is a white strip on the face (angle - degrees clockwise from the
    "up along the panel" direction), ptr is its part."""
    n = fr.n
    base = fr.p(a, b, c)
    if lod > 0:
        if r > 0.0125 and kind != "plain":
            lathe(body, base, n, [(r * 1.35, 0.0), (r * 1.35, 0.003), (r, 0.003), (r, 0.003 + 1.3 * r)], 8)
        else:
            lathe(body, base, n, [(r, 0.0), (r, 1.4 * r)], 6)
        return
    ns = 16 if r > 0.0105 else 12
    if kind == "plain":
        ln = 1.35 * r
        lathe(body, base, n, [(r, 0.0), (r, ln), (0.80 * r, ln + 0.0018)], ns, knurl=(0, 1), depth=0.0007)
        top, rt = ln + 0.0018, 0.80 * r
    else:
        ln = 1.25 * r
        prof = [(1.42 * r, 0.0), (1.42 * r, 0.0028), (r, 0.0042), (r, 0.0042 + ln), (0.80 * r, 0.0062 + ln)]
        lathe(body, base, n, prof, ns, knurl=(2, 3), depth=0.0009)
        top, rt = 0.0062 + ln, 0.80 * r
    t = math.radians(angle)
    d = fr.v * math.cos(t) + fr.u * math.sin(t)
    cpt = base + n * (top + 0.0002)
    if ptr is not None:
        strip(ptr, cpt + d * (0.15 * rt), cpt + d * (0.92 * rt), n, 0.0009 if r > 0.0105 else 0.0007, 0.0005)


def lamp(rim, lens, fr, a, b, c, lod=0, r=0.0065):
    """AS signal lamp: chrome knurled bezel, dome lens (the lamp selection belongs to lens)."""
    n = fr.n
    base = fr.p(a, b, c)
    if lod > 0:
        lathe(lens, base, n, [(r, 0.0), (r, 0.006), (0.6 * r, 0.009)], 6 if lod == 1 else 4)
        return
    lathe(rim, base, n, [(r * 1.45, 0.0), (r * 1.45, 0.0035), (r * 1.15, 0.0050)], 10, knurl=(0, 1), depth=0.0005,
          cap1=False)
    lathe(lens, base, n, [(r, 0.0045), (r, 0.0075), (0.62 * r, 0.0108), (0.0, 0.0123)], 8)


def push_button(bez, cap, fr, a, b, c, lod=0, r=0.0075):
    """KM push button: a ring holder and a cap with a chamfer."""
    n = fr.n
    base = fr.p(a, b, c)
    if lod > 0:
        lathe(cap, base, n, [(r * 1.3, 0.0), (r * 1.3, 0.007)], 6)
        return
    lathe(bez, base, n, [(r * 1.42, 0.0), (r * 1.42, 0.0025), (r * 1.15, 0.0040)], 12, cap1=False)
    lathe(cap, base, n, [(r, 0.0030), (r, 0.0075), (0.85 * r, 0.0090), (0.0, 0.0094)], 12)


def mushroom(ring, head, fr, a, b, c, lod=0, r=0.0145):
    """Emergency mushroom button: a yellow ring base and a red head on a stem."""
    n = fr.n
    base = fr.p(a, b, c)
    if lod > 0:
        lathe(ring, base, n, [(r * 1.4, 0.0), (r * 1.4, 0.005)], 6)
        lathe(head, base + n * 0.005, n, [(r, 0.0), (r, 0.012)], 6)
        return
    lathe(ring, base, n, [(r * 1.45, 0.0), (r * 1.45, 0.0035), (r * 1.25, 0.0060), (r * 0.62, 0.0062)], 14, cap1=False)
    lathe(head, base + n * 0.0055, n, [(r * 0.55, 0.0), (r * 0.55, 0.008), (r, 0.0095), (r, 0.0125),
                                       (r * 0.80, 0.0160), (0.0, 0.0171)], 14)


# =============================================================================
# Doors, side walls
# =============================================================================
def hinge(part, x, y, z0, z1, r=0.0052, lod=0):
    """Door hinge: a barrel along z with caps."""
    lathe(part, (x, y, z0), (0, 0, 1), [(r * 0.8, -0.002), (r, 0.0), (r, z1 - z0), (r * 0.8, z1 - z0 + 0.002)],
          6, cap0=True)


def louvers(part, face_x, sign, y0, y1, z0, n, pitch, h=0.013, d=0.0045):
    """Stamped louvers on a side wall (face x = face_x, outward - sign): n slots, each a wedge of
    height h and projection d; open downward."""
    for i in range(n):
        za = z0 + pitch * i
        poly = [(face_x, za), (face_x + sign * d, za), (face_x, za + h)]
        g.prism(part, poly, (0, 2), y0, y1)


def louvers_y(part, face_y, x0, x1, z0, n, pitch, h=0.012, d=0.004):
    """Louvers on a face toward -y (door): wedges along x, open downward."""
    for i in range(n):
        za = z0 + pitch * i
        poly = [(face_y, za), (face_y - d, za), (face_y, za + h)]
        g.prism(part, poly, (1, 2), x0, x1)


# =============================================================================
# Connectors and cables
# =============================================================================
def mil_connector(flange, body, nut, boot, base, d, ref=(0, 0, 1), lod=0, r=0.0115):
    """Round connector (like 2RM) on a wall: a square flange, a socket body, a plug with a knurled
    coupling nut and a rubber boot. base - a point on the wall, d - outward. Returns the end of the boot
    (where the cable leaves)."""
    a, u, v = _basis(d, ref)
    base = Vector(base)
    if lod > 0:
        lathe(body, base, a, [(r * 1.1, 0.0), (r * 1.1, 0.030)], 6)
        lathe(boot, base + a * 0.030, a, [(r * 0.7, 0.0), (r * 0.45, 0.020)], 6)
        return base + a * 0.050
    g.prism(flange, rrect(0.0, 0.0, 2.7 * r, 2.7 * r, 0.35 * r, 1), (0, 1), 0.0, 0.0028, frame=g.Frame(base, u, v, a))
    lathe(body, base + a * 0.0028, a, [(r * 0.92, 0.0), (r * 0.92, 0.010)], 10, cap1=False)
    lathe(nut, base + a * 0.0125, a, [(r * 1.12, 0.0), (r * 1.12, 0.0135), (r * 0.94, 0.0155)], 12, knurl=(0, 1),
          depth=0.0008, cap0=True, cap1=False)
    lathe(boot, base + a * 0.0280, a, [(r * 0.94, 0.0), (r * 0.80, 0.010), (r * 0.56, 0.022), (r * 0.44, 0.027)], 6)
    return base + a * 0.055


def bnc(nut, body, sleeve, boot, base, d, lod=0, length=0.045):
    """BNC jack on the case and a plug in it (from M06): a nut, a body, a knurled bayonet sleeve, a rubber
    boot. Returns the point where the cable leaves."""
    a = Vector(d).normalized()
    base = Vector(base)
    if lod > 0:
        lathe(body, base, a, [(0.0068, 0.0), (0.0068, 0.024)], 6)
        lathe(boot, base, a, [(0.0045, 0.024), (0.0034, length)], 6)
        return base + a * length
    lathe(nut, base, a, [(0.0074, 0.0), (0.0074, 0.0028)], 6)
    lathe(body, base, a, [(0.0048, 0.0028), (0.0048, 0.0085)], 8, cap1=False)
    lathe(sleeve, base, a, [(0.0069, 0.0085), (0.0069, 0.0205), (0.0056, 0.0222)], 12, knurl=(0, 1), depth=0.0006,
          cap1=False)
    lathe(boot, base, a, [(0.0056, 0.0222), (0.0044, 0.030), (0.0034, length)], 8)
    return base + a * length


def spline_bends(pts, k=3, min_deg=6.0):
    """Like spline, but subdivides only the segments at bends (the angle at one of the ends is more than
    min_deg): straight stretches between clips get no extra rings."""
    v = [Vector(p) for p in pts]
    n = len(v)

    def bend(i):
        if i <= 0 or i >= n - 1:
            return 0.0
        a, c = (v[i] - v[i - 1]), (v[i + 1] - v[i])
        if a.length < 1e-9 or c.length < 1e-9:
            return 0.0
        return math.degrees(a.angle(c))
    out = []
    for i in range(n - 1):
        p0 = v[i - 1] if i > 0 else 2 * v[i] - v[i + 1]
        p1, p2 = v[i], v[i + 1]
        p3 = v[i + 2] if i + 2 < n else 2 * v[i + 1] - v[i]
        kk = k if max(bend(i), bend(i + 1)) > min_deg else 1
        for s in range(kk):
            t = s / kk
            out.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (3 * p1 - p0 - 3 * p2 + p3) * t ** 3))
    out.append(v[-1])
    return [tuple(q) for q in out]


def cable(part, pts, r, lod, k=2):
    """Cable as a smooth curve through the points (near LOD - a spline at the bends, mid LOD - every
    second point)."""
    if lod == 0:
        g.pipe(part, spline_bends(pts, k), r, 6)
    else:
        sub = [pts[i] for i in range(0, len(pts), 2)]
        if sub[-1] != pts[-1]:
            sub.append(pts[-1])
        g.pipe(part, sub, r, 4)


def tie(part, center, along, across, half_a, half_c, w=0.0022):
    """Cable tie: a thin band around a post with cables. along - along the post, across - across it
    (toward the cables), half_a / half_c - half-widths of the wrap along across and along the third axis."""
    t = Vector(along).normalized()
    a = Vector(across) - t * Vector(across).dot(t)
    a.normalize()
    c = t.cross(a)
    fr = g.Frame(center, a, t, c)
    g.box(part, half_a[0], half_a[1], -w, w, -half_c, half_c, frame=fr)
