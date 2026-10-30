"""Small parts for M21: a copy of the small parts of M06 (m06_bits.py) - solids of revolution along
any axis with knurling, rounded-corner frames, instrument knobs, BNC connectors, toggles, lamps,
keys, screws, bar handles, hinges, louvers, eyebolts, an alligator clip, board components - kept
separate so that a change for one model does not alter the other. At the end come the parts specific
to the radio-intercept rack: a pointer knob, a knob with a crank pin, phone jacks, a headphone
plug, an SR-50 connector with a flange, the axis of a cable coil. The parts (kgeo.Part) are
created by the generator and passed in ready: it picks the material region.

Blender axes: X is width, Y is depth (the face looks to -Y), Z is up.
"""
import math

from mathutils import Vector

import kgeo as g

FRONT = Vector((0.0, -1.0, 0.0))                 # from the panel toward the person


def face(part, verts, want):
    """Face from bmesh vertices, oriented toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def quad_to(part, corners, want):
    """A single face from points, oriented toward want."""
    f = face(part, [part.bm.verts.new(Vector(c)) for c in corners], want)
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
    """Rounded rectangle in the x-z plane: points around it (counterclockwise seen from -y)."""
    r = max(0.0, min(r, w / 2 - 1e-5, h / 2 - 1e-5))
    if r < 1e-5:
        return [(cx + w / 2, cz + h / 2), (cx - w / 2, cz + h / 2), (cx - w / 2, cz - h / 2), (cx + w / 2, cz - h / 2)]
    pts = []
    for ox, oz, a0 in ((cx + w / 2 - r, cz + h / 2 - r, 0), (cx - w / 2 + r, cz + h / 2 - r, 90),
                       (cx - w / 2 + r, cz - h / 2 + r, 180), (cx + w / 2 - r, cz - h / 2 + r, 270)):
        for i in range(n + 1):
            t = math.radians(a0 + 90.0 * i / n)
            pts.append((ox + r * math.cos(t), oz + r * math.sin(t)))
    return pts


def bezel(part, cx, cz, outer, inner, y_back, y_front, y_in=None, n=3, ic=None):
    """Frame with rounded corners (screen tube, instrument holder, recorder door): outer and inner are
    (width, height, corner radius); from the panel face y_back forward to y_front (y_front < y_back),
    into the opening to y_in (default y_back). ic - (x, z) of the opening center if it is not centered.
    Faces: front, outer side, inner side."""
    icx, icz = ic if ic is not None else (cx, cz)
    o = rrect(cx, cz, outer[0], outer[1], max(outer[2], 2e-5), n=n)
    i_ = rrect(icx, icz, inner[0], inner[1], max(inner[2], 2e-5), n=n)
    y_in = y_back if y_in is None else y_in
    bm = part.bm
    ob = [bm.verts.new((x, y_back, z)) for x, z in o]
    of = [bm.verts.new((x, y_front, z)) for x, z in o]
    if_ = [bm.verts.new((x, y_front, z)) for x, z in i_]
    ib = [bm.verts.new((x, y_in, z)) for x, z in i_] if abs(y_in - y_front) > 1e-6 else None
    new = []
    m = len(o)
    for k in range(m):
        j = (k + 1) % m
        new.append(face(part, [of[k], of[j], if_[j], if_[k]], FRONT))
        oc = Vector(((o[k][0] + o[j][0]) / 2 - cx, 0, (o[k][1] + o[j][1]) / 2 - cz))
        new.append(face(part, [ob[k], ob[j], of[j], of[k]], oc))
        if abs(y_in - y_front) > 1e-6:
            icv = Vector(((i_[k][0] + i_[j][0]) / 2 - icx, 0, (i_[k][1] + i_[j][1]) / 2 - icz))
            new.append(face(part, [if_[k], if_[j], ib[j], ib[k]], -icv))
    bm.normal_update()
    part.tag(new)
    return new


def plate(part, cx, cz, w, h, r, y_back, y_front, n=2):
    """Rounded-corner plate facing -y (nameplate, tag, key): a prism over rrect."""
    poly = rrect(cx, cz, w, h, r, n)
    return g.prism(part, poly, (0, 2), y_front, y_back)


# =============================================================================
# Panel controls (the panel face is the plane y = yf, everything sticks out to -y)
# =============================================================================
def knob(body, ptr, x, yf, z, r, kind="plain", lod=0, angle=0.0, cap=None):
    """Instrument knob: kind "skirt" - with a skirt (range switch), "plain" - knurled, "dual" - double
    (a small fine-tuning knob on top, cap is its part). The mark is a white strip on the face
    (angle - degrees clockwise from 12 o'clock), ptr is its part. Far LODs use a smooth cylinder."""
    base = (x, yf, z)
    if lod > 0:
        # mid LOD: large ones with a skirt, small ones as hexagonal cylinders (dark dots on the panel)
        if r > 0.0125 and kind != "plain":
            lathe(body, base, FRONT, [(r * 1.35, 0.0), (r * 1.35, 0.003), (r, 0.003), (r, 0.003 + 1.3 * r)], 8)
        else:
            lathe(body, base, FRONT, [(r, 0.0), (r, 1.4 * r)], 6)
        return
    ns = 12 if r > 0.0105 else 10
    if kind == "plain":
        L = 1.35 * r
        prof = [(r, 0.0), (r, L), (0.80 * r, L + 0.0018)]
        lathe(body, base, FRONT, prof, ns, knurl=(0, 1) if r > 0.0095 else (), depth=0.0007)
        top = L + 0.0018
        rt = 0.80 * r
    else:
        L = 1.25 * r
        prof = [(1.42 * r, 0.0), (1.42 * r, 0.0028), (r, 0.0042), (r, 0.0042 + L), (0.80 * r, 0.0062 + L)]
        lathe(body, base, FRONT, prof, ns, knurl=(2, 3), depth=0.0008)
        top = 0.0062 + L
        rt = 0.80 * r
    a = math.radians(angle)
    d = Vector((math.sin(a), 0, math.cos(a)))
    c = Vector(base) + FRONT * (top + 0.0002)
    _strip(ptr, c + d * (0.15 * rt), c + d * (0.92 * rt), 0.0009 if r > 0.0105 else 0.0007, 0.0005)
    if kind == "dual" and cap is not None:
        rc = 0.52 * r
        lathe(cap, Vector(base) + FRONT * top, FRONT, [(rc, 0.0), (rc, 0.009), (0.8 * rc, 0.0105)], 10,
              knurl=(0, 1), depth=0.0005)
        c2 = Vector(base) + FRONT * (top + 0.0107)
        d2 = Vector((math.sin(a + 1.9), 0, math.cos(a + 1.9)))
        _strip(ptr, c2 + d2 * (0.1 * rc), c2 + d2 * (0.8 * rc), 0.0006, 0.0004)


def _strip(part, a, b, half_w, half_t):
    """Strip from a to b on a face looking to -y (a mark)."""
    a, b = Vector(a), Vector(b)
    u = (b - a)
    L = u.length
    u.normalize()
    n = FRONT.copy()
    v = n.cross(u)
    fr = g.Frame(a, u, v, n)
    g.box(part, 0.0, L, -half_w, half_w, -half_t, half_t, frame=fr)


def bnc_socket(nut, body, x, yf, z, lod=0, studs=True):
    """BNC (SR-50) socket on the panel: hex nut, body with bayonet pins."""
    if lod > 0:
        lathe(body, (x, yf, z), FRONT, [(0.0065, 0.0), (0.0065, 0.012)], 6)
        return
    lathe(nut, (x, yf, z), FRONT, [(0.0074, 0.0), (0.0074, 0.0028)], 6, ref=(1, 0, 0))
    lathe(body, (x, yf, z), FRONT, [(0.0048, 0.0028), (0.0048, 0.0135)], 8)
    if studs:
        for s in (-1, 1):
            g.box(body, x + s * 0.0048 - 0.0007 + s * 0.0007, x + s * 0.0048 + 0.0007 + s * 0.0007,
                  yf - 0.0112, yf - 0.0098, z - 0.0007, z + 0.0007)


def bnc_plug(sleeve, boot, x, yf, z, lod=0, length=0.045):
    """BNC plug in the socket: knurled bayonet sleeve, body, rubber boot (toward the cable).
    Returns the point where the cable leaves (the end of the boot)."""
    if lod > 0:
        lathe(sleeve, (x, yf, z), FRONT, [(0.0068, 0.008), (0.0068, 0.024)], 6)
        lathe(boot, (x, yf, z), FRONT, [(0.0045, 0.024), (0.0034, length)], 6)
        return Vector((x, yf, z)) + FRONT * length
    lathe(sleeve, (x, yf, z), FRONT, [(0.0069, 0.0085), (0.0069, 0.0205), (0.0056, 0.0222)], 10,
          knurl=(0, 1), depth=0.0006, cap1=False)
    lathe(boot, (x, yf, z), FRONT, [(0.0056, 0.0222), (0.0044, 0.030), (0.0034, length)], 8)
    return Vector((x, yf, z)) + FRONT * length


def plug_along(sleeve, boot, tip, d, lod=0):
    """BNC plug along direction d from the socket tip (on a terminal block): the same as bnc_plug but at
    an angle. Returns the end of the boot."""
    d = Vector(d).normalized()
    if lod > 0:
        lathe(sleeve, tip, d, [(0.0068, 0.0), (0.0068, 0.016)], 6)
        lathe(boot, tip, d, [(0.0045, 0.016), (0.0034, 0.036)], 6)
        return Vector(tip) + d * 0.036
    lathe(sleeve, tip, d, [(0.0069, 0.0), (0.0069, 0.012), (0.0056, 0.0137)], 10, knurl=(0, 1), depth=0.0006,
          cap0=True, cap1=False)
    lathe(boot, tip, d, [(0.0056, 0.0137), (0.0044, 0.022), (0.0034, 0.036)], 8)
    return Vector(tip) + d * 0.036


def toggle(nut, lever, x, yf, z, lod=0, up=True):
    """MT toggle switch: nut, bushing, lever with a ball (up is on)."""
    if lod > 0:
        lathe(nut, (x, yf, z), FRONT, [(0.0055, 0.0), (0.0055, 0.004)], 6)
        return
    lathe(nut, (x, yf, z), FRONT, [(0.0064, 0.0), (0.0064, 0.0025)], 6, ref=(1, 0, 0))
    lathe(nut, (x, yf, z), FRONT, [(0.0036, 0.0025), (0.0036, 0.0085), (0.0024, 0.0095)], 8)
    tilt = math.radians(18.0) * (1 if up else -1)
    d = Vector((0.0, -math.cos(tilt), math.sin(tilt)))
    b = Vector((x, yf, z)) + FRONT * 0.0092
    lathe(lever, b, d, [(0.0017, 0.0), (0.0013, 0.014), (0.0021, 0.0160), (0.0, 0.0188)], 6)


def lamp(rim, lens, x, yf, z, lod=0, r=0.0065):
    """AS signal lamp: chrome knurled bezel, dome lens (the lamp selection belongs to lens)."""
    if lod > 0:
        lathe(lens, (x, yf, z), FRONT, [(r, 0.0), (r, 0.006), (0.6 * r, 0.009)], 6 if lod == 1 else 4)
        return
    lathe(rim, (x, yf, z), FRONT, [(r * 1.45, 0.0), (r * 1.45, 0.0035), (r * 1.15, 0.0050)], 10,
          knurl=(0, 1), depth=0.0005, cap1=False)
    lathe(lens, (x, yf, z), FRONT, [(r * 1.02, 0.0045), (r, 0.0075), (0.62 * r, 0.0108), (0.0, 0.0123)], 10)


def key(part, x, yf, z, w=0.016, h=0.014, depth=0.009, lod=0):
    """Key: a cap with a chamfer."""
    if lod > 0:
        g.box(part, x - w / 2, x + w / 2, yf - depth, yf, z - h / 2, z + h / 2)
        return
    g.box(part, x - w / 2, x + w / 2, yf - depth, yf + 0.001, z - h / 2, z + h / 2, r=0.0013, seg=1)


def screw(part, x, yf, z, r=0.0035, lod=0, washer=False, axis=None):
    """Round-head screw (and a cup washer) on face yf; axis - if the face does not look to -y."""
    if lod > 0:
        return
    a = Vector(axis) if axis is not None else FRONT
    b = Vector((x, yf, z))
    if washer:
        lathe(part, b, a, [(r * 1.55, 0.0), (r * 1.3, 0.0010)], 8, cap1=False)
    lathe(part, b, a, [(r, 0.0), (0.82 * r, 0.0016), (0.0, 0.0026)], 7)


def u_handle(part, a, b, n, stand, r, lod=0, bosses=None, smooth=True):
    """Bar handle of rod radius r: from point a to point b (on the surface), standing off by stand along
    normal n; the ends sit in bosses (bosses - a part, radius ~1.6 r). smooth - bends as a smooth
    curve (otherwise chamfered)."""
    a, b, n = Vector(a), Vector(b), Vector(n).normalized()
    t = (b - a).normalized()
    k = min(0.45 * stand, 0.3 * (b - a).length)
    pts = [a, a + n * (stand - k), a + n * stand + t * k, b + n * stand - t * k, b + n * (stand - k), b]
    if lod == 0 and smooth:
        pts = [Vector(p) for p in spline([tuple(p) for p in pts], 2)]
    g.pipe(part, [tuple(p) for p in pts], r, 6 if lod == 0 else 4)
    if bosses is not None and lod == 0:
        for p in (a, b):
            lathe(bosses, p, n, [(r * 1.75, 0.0), (r * 1.75, 0.004), (r * 1.35, 0.0055)], 7)


def hinge(part, x, y, z0, z1, r=0.0052, lod=0):
    """Door hinge: barrel along z, a cut between the knuckles (a groove in the middle)."""
    lathe(part, (x, y, z0), (0, 0, 1), [(r, 0.0), (r, z1 - z0)], 8 if lod == 0 else 6, cap0=True)


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


def eye_bolt(part, x, y, z, lod=0, r_ring=0.018, r_wire=0.0042, yaw=0.0):
    """M12 eyebolt on the roof: a collar washer and a ring."""
    lathe(part, (x, y, z), (0, 0, 1), [(0.013, 0.0), (0.013, 0.004), (0.0075, 0.010)], 8, cap1=True)
    zc = z + 0.010 + r_ring
    c, s = math.cos(yaw), math.sin(yaw)
    pts = []
    m = 12                                        # M06 used 8 segments and a 4-sided rod, which made the ring octagonal
    for k in range(m + 1):
        t = -math.pi / 2 + 2 * math.pi * k / m
        q = Vector((r_ring * math.cos(t) * c, r_ring * math.cos(t) * s, r_ring * math.sin(t)))
        pts.append((x + q.x, y + q.y, zc + q.z))
    g.pipe(part, pts, r_wire, 6)


def alligator(jaw, boot, tip, u, up, lod=0, size=1.0, open_deg=4.0):
    """Alligator clip (like the one in M16, smaller): two toothed jaws from tip along u, the jaws open
    along up; a boot on the tail. Returns the tail point (where the wire starts)."""
    u = Vector(u).normalized()
    n = Vector(up) - u * Vector(up).dot(u)
    n.normalize()
    v = n.cross(u)
    fr = g.Frame(tip, u, v, n)
    s = size
    prof = [(0.0, 0.0005), (0.007, 0.0008), (0.013, 0.0011), (0.018, 0.0025), (0.024, 0.0036), (0.033, 0.0058)]
    for sg in (1, -1):
        pts = [fr.p(a * s, 0.0, sg * c * s) for a, c in (prof if lod == 0 else prof[::2] + [prof[-1]])]
        g.sweep(jaw, pts, fr.v, 0.0003 * s, 0.0024 * s)
        if lod == 0:
            for i in range(4):
                a0 = (0.0015 + 0.0028 * i) * s
                c0 = sg * 0.0005 * s
                g.prism(jaw, [(a0 - 0.001 * s, c0), (a0 + 0.001 * s, c0), (a0, c0 - sg * 0.0006 * s)], (0, 2),
                        -0.0021 * s, 0.0021 * s, frame=fr)
    if lod == 0:
        g.cyl(jaw, (0.0195 * s, 0.0, 0.0), "y", 0.001 * s, 0.006 * s, 8, frame=fr)
    sec = [(0.021, 0.0033, 0.0036), (0.025, 0.0040, 0.0048), (0.034, 0.0042, 0.0053), (0.042, 0.0038, 0.0047),
           (0.047, 0.0026, 0.0029), (0.050, 0.0018, 0.0019)]
    if lod > 0:
        sec = sec[::2] + [sec[-1]]
    g.tube_var(boot, [fr.p(a * s, 0.0, 0.0) for a, _, _ in sec], [(rb * s, rc * s) for _, rb, rc in sec],
               10 if lod == 0 else 6)
    return fr.p(0.050 * s, 0.0, 0.0)


# =============================================================================
# Probe board: parts on the board face (the face looks to -y at y = yb)
# =============================================================================
def dip(body, legs, x, yb, z, n, lod=0, horizontal=True):
    """DIP chip (n pins, 2.54 pitch): the body and legs along the long sides."""
    L = 0.00254 * (n // 2) + 0.0012
    W = 0.0064
    hx, hz = (L / 2, W / 2) if horizontal else (W / 2, L / 2)
    g.box(body, x - hx, x + hx, yb - 0.0042, yb - 0.0007, z - hz, z + hz, **(dict(r=0.0004, seg=1) if lod == 0 else {}))
    if lod > 0:
        return
    # leg: two visible faces - toward the viewer and outward (the rest are pressed to the board and the body)
    for k in range(n // 2):
        off = -L / 2 + 0.0006 + 0.00127 + 0.00254 * k
        for s in (-1, 1):
            if horizontal:
                xa, za = x + off, z + s * (W / 2 + 0.0011)
                quad_to(legs, [(xa - 0.0003, yb - 0.0030, za - s * 0.0011), (xa + 0.0003, yb - 0.0030, za - s * 0.0011),
                               (xa + 0.0003, yb - 0.0030, za), (xa - 0.0003, yb - 0.0030, za)], FRONT)
                quad_to(legs, [(xa - 0.0003, yb - 0.0030, za), (xa + 0.0003, yb - 0.0030, za), (xa + 0.0003, yb, za),
                               (xa - 0.0003, yb, za)], (0, 0, s))
            else:
                xa, za = x + s * (W / 2 + 0.0011), z + off
                quad_to(legs, [(xa - s * 0.0011, yb - 0.0030, za - 0.0003), (xa, yb - 0.0030, za - 0.0003),
                               (xa, yb - 0.0030, za + 0.0003), (xa - s * 0.0011, yb - 0.0030, za + 0.0003)], FRONT)
                quad_to(legs, [(xa, yb - 0.0030, za - 0.0003), (xa, yb, za - 0.0003), (xa, yb, za + 0.0003),
                               (xa, yb - 0.0030, za + 0.0003)], (s, 0, 0))


def resistor(body, leads, x, yb, z, along="x", lod=0, L=0.0062, r=0.0012):
    """MLT resistor lying on the board: body with thickened ends, leads bent into the board."""
    a = Vector((1, 0, 0)) if along == "x" else Vector((0, 0, 1))
    c = Vector((x, yb - r - 0.0004, z))
    lathe(body, c - a * (L / 2), a, [(0.0, 0.0), (r, 0.0010), (0.85 * r, 0.0020), (0.85 * r, L - 0.0020),
                                     (r, L - 0.0010), (0.0, L)], 6 if lod == 0 else 4)
    if lod > 0:
        return
    for s in (-1, 1):
        e = c + a * s * (L / 2)
        g.pipe(leads, [tuple(e), tuple(e + a * s * 0.0022), tuple(Vector((e.x, yb, e.z)) + a * s * 0.0030)], 0.00028, 3)


def can_cap(part, top, x, yb, z, r=0.004, L=0.011, lod=0):
    """Electrolytic capacitor (stands on the board, axis toward -y): can, crimp groove, chamfered top."""
    lathe(part, (x, yb, z), FRONT, [(r, 0.0), (0.92 * r, 0.0022), (r, 0.0032), (r, L - 0.0008), (0.88 * r, L)],
          10 if lod == 0 else 6)
    if top is not None and lod == 0:
        lathe(top, Vector((x, yb, z)) + FRONT * L, FRONT, [(0.86 * r, 0.0), (0.0, 0.0002)], 10)


def transistor(can, x, yb, z, lod=0):
    """TO-5 metal-can transistor: flange, cap, locating tab."""
    lathe(can, (x, yb, z), FRONT, [(0.0047, 0.0), (0.0047, 0.0008), (0.0042, 0.0008), (0.0042, 0.0062),
                                   (0.0036, 0.0068)], 10 if lod == 0 else 6)
    if lod == 0:
        g.box(can, x + 0.0042, x + 0.0058, yb - 0.0008, yb, z - 0.0005, z + 0.0005)


# =============================================================================
# Specific to M21: Soviet receiver knobs, jacks, plug, SR-50, louvers, cable coil
# =============================================================================
def pointer_knob(body, ptr, x, yf, z, r, lod=0, angle=0.0):
    """Pointer knob (R-250 and tube equipment): a round skirt at the panel with a tapering "beak" on it
    and a white mark along the beak; angle - degrees clockwise from 12 o'clock (where the beak points).
    Far LODs use a cylinder."""
    base = Vector((x, yf, z))
    if lod > 0:
        lathe(body, base, FRONT, [(r * 1.15, 0.0), (r * 1.15, 1.2 * r)], 6 if lod == 1 else 4)
        return
    lathe(body, base, FRONT, [(r * 1.25, 0.0), (r * 1.25, 0.0025), (r * 1.10, 0.0040), (r * 0.72, 0.0046)], 12)
    a = math.radians(angle)
    d = (math.sin(a), math.cos(a))                      # beak: from the axis in the x-z plane
    s = (d[1], -d[0])                                   # across the beak
    L, w0, w1 = 1.30 * r, 0.60 * r, 0.26 * r
    c = -0.80 * r + w0                                  # center of the tail semicircle
    loc = [(L, -w1), (L, w1)] + [(c + w0 * math.cos(t), w0 * math.sin(t))
                                 for t in (math.pi / 2 + math.pi * i / 6 for i in range(7))]
    poly = [(x + p * d[0] + q * s[0], z + p * d[1] + q * s[1]) for p, q in loc]
    hb = 1.05 * r
    g.prism(body, poly, (0, 2), yf - 0.0040, yf - 0.0040 - hb)
    top = base + FRONT * (0.0040 + hb + 0.0002)
    dv = Vector((d[0], 0.0, d[1]))
    _strip(ptr, top - dv * (0.10 * r), top + dv * (0.95 * L), 0.0008, 0.0004)


def crank_knob(body, pin, x, yf, z, r, lod=0, pin_angle=40.0, teeth=True):
    """Large bakelite tuning knob (R-250): a skirt at the panel (with teeth - teeth, as on the fine
    tuning knob), body, rounded end and a pin handle near the edge of the end (pin_angle - degrees
    clockwise from 12 o'clock; pin - the pin part or None)."""
    base = Vector((x, yf, z))
    if lod > 0:
        lathe(body, base, FRONT, [(r * 1.12, 0.0), (r * 1.12, 0.006), (r, 0.008), (r, 0.80 * r)], 8 if lod == 1 else 6)
        return
    ns = 20 if r > 0.030 else 18
    prof = [(r * 1.14, 0.0), (r * 1.14, 0.0070), (r * 1.06, 0.0085), (r * 0.97, 0.0100), (r * 0.97, 0.58 * r),
            (r * 0.90, 0.66 * r), (r * 0.62, 0.71 * r), (0.0, 0.73 * r)]
    lathe(body, base, FRONT, prof, ns, knurl=(0, 1) if teeth else (), depth=0.0020 if teeth else 0.0)
    if pin is not None:
        a = math.radians(pin_angle)
        c = base + FRONT * (0.66 * r) + Vector((math.sin(a), 0.0, math.cos(a))) * (0.62 * r)
        lathe(pin, c, FRONT, [(0.0046, 0.0), (0.0043, 0.016), (0.0034, 0.0205), (0.0, 0.0215)], 10)


def phone_jack(rim, hole, x, yf, z, lod=0, r=0.0060):
    """Phone jack (6.3 mm): chrome ring nut with a rounded edge, dark hole (hole - the part for the
    dark bottom, or None)."""
    if lod > 0:
        lathe(rim, (x, yf, z), FRONT, [(r * 1.3, 0.0), (r * 1.3, 0.003)], 6)
        return
    lathe(rim, (x, yf, z), FRONT, [(r * 1.45, 0.0), (r * 1.45, 0.0022), (r * 1.10, 0.0034), (r * 0.55, 0.0024)], 10,
          cap1=False)
    if hole is not None:
        lathe(hole, (x, yf, z), FRONT, [(r * 0.56, 0.0023)], 8)


def jack_plug(sleeve, handle, base, d, lod=0, L=0.058):
    """6.3 mm headphone plug in the jack: chrome sleeve at the jack, knurled bakelite handle, cord
    strain relief; d - direction away from the jack. Returns the end of the strain relief."""
    d = Vector(d).normalized()
    base = Vector(base)
    if lod > 0:
        lathe(handle, base, d, [(0.0055, 0.006), (0.0055, L - 0.012), (0.0030, L)], 6)
        return base + d * L
    lathe(sleeve, base, d, [(0.0042, 0.0), (0.0042, 0.006), (0.0050, 0.0075)], 10, cap1=False)
    lathe(handle, base, d, [(0.0050, 0.0075), (0.0062, 0.0100), (0.0062, 0.0300), (0.0055, L - 0.016),
                            (0.0040, L - 0.008), (0.0030, L)], 10, knurl=(1, 2), depth=0.0004)
    return base + d * L


def sr50(flange, body, screws, x, yf, z, lod=0):
    """SR-50 antenna connector on the panel: a square flange on four screws, a body with a shoulder,
    a center socket."""
    if lod > 0:
        g.box(flange, x - 0.011, x + 0.011, yf - 0.002, yf, z - 0.011, z + 0.011)
        lathe(body, (x, yf, z), FRONT, [(0.0065, 0.002), (0.0065, 0.012)], 6)
        return
    plate(flange, x, z, 0.024, 0.024, 0.0025, yf, yf - 0.0022)
    lathe(body, (x, yf, z), FRONT, [(0.0072, 0.0022), (0.0072, 0.0040), (0.0060, 0.0045), (0.0060, 0.0145),
                                    (0.0052, 0.0150), (0.0025, 0.0150), (0.0020, 0.0120)], 12)
    if screws is not None:
        for sx in (-1, 1):
            for sz in (-1, 1):
                screw(screws, x + sx * 0.0085, yf - 0.0022, z + sz * 0.0085, 0.0018)


def key_cap(part, x, yf, z, w, h, depth=0.004, ch=0.0012):
    """Key cap on face yf (looks to -y): a truncated pyramid - edges chamfered by ch (a face and four
    sides, 10 triangles instead of ~50 for a chamfered box)."""
    bm = part.bm
    corners = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    back = [bm.verts.new((x + sx * w / 2, yf + 0.0005, z + sz * h / 2)) for sx, sz in corners]
    fw, fh = max(w / 2 - ch, w * 0.2), max(h / 2 - ch, h * 0.2)
    front = [bm.verts.new((x + sx * fw, yf - depth, z + sz * fh)) for sx, sz in corners]
    new = [face(part, front, FRONT)]
    for i in range(4):
        j = (i + 1) % 4
        q = [back[i], back[j], front[j], front[i]]
        c = sum((v.co for v in q), Vector()) / 4 - Vector((x, yf, z))
        c.y = 0.0
        new.append(face(part, q, c.normalized() + FRONT * 0.3))
    bm.normal_update()
    part.tag(new)
    return new


def hood_louvre(part, x0, x1, yf, zt, h, d, t=0.0012, n=6):
    """Stamped louver hood on face yf (looks to -y): an arc from the panel at the top forward and down
    by h with projection d, thickness t, open downward; along x from x0 to x1 (a kgeo.sweep ribbon
    along the arc)."""
    xc = (x0 + x1) / 2
    pts = []
    for i in range(n + 1):
        th = math.pi / 2 * i / n
        pts.append((xc, yf - (d - t / 2) * math.sin(th), zt - t / 2 - (h - t / 2) * (1 - math.cos(th))))
    g.sweep(part, pts, (1, 0, 0), t / 2, (x1 - x0) / 2)


def coil_pts(cx, cy, z0, r, turns, cr, n_per_turn, phase=0.0, wob=0.005):
    """Axis of a cable coil laid on a shelf: turns stacked on one another (a rise of 2.1 cable radii per
    turn, so the turns do not intersect), the radius wanders (laid by hand). Returns the axis points."""
    pts = []
    n = int(round(turns * n_per_turn))
    for i in range(n + 1):
        t = 2 * math.pi * i / n_per_turn + phase
        k = i / n_per_turn
        rr = r + wob * math.sin(1.7 * t + 0.5) + 0.4 * wob * math.sin(4.1 * t)
        pts.append((cx + rr * math.cos(t), cy + 0.92 * rr * math.sin(t), z0 + cr + k * 2.1 * cr))
    return pts
