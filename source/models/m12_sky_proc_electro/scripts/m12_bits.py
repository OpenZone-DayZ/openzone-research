"""M12 (diagnostic case) generator primitives that kgeo does not provide: solids of revolution, knurling,
rings, smooth curves, bar handles, bolts and rivets, a rounded box in any frame, a profile swept around a
rounded rectangle (the case tray with a bead and a rim), the toothed disc of a selector switch, a
crocodile clip.

Taken from the M04 generators (lathe, fluted, spline, u_handle, hex_bolt) and M16 (box_to, crocodile
clip); they live here so that the shared kit stays unchanged.
"""
import math

from mathutils import Vector

import kgeo as g


def orient(f, want):
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def basis(axis):
    d = Vector(axis).normalized()
    a = Vector((0.0, 0.0, 1.0)) if abs(d.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    e1 = d.cross(a).normalized()
    return d, e1, d.cross(e1).normalized()


def lathe(part, prof, sides, center, axis=(0.0, 0.0, 1.0), phase=0.0, cap0=False, cap1=False):
    """Solid of revolution about axis `axis` through `center`: prof [(r, h)] traverses the section with the
    solid on the left (up the outer wall, inward across the top), faces look out of the solid; r = 0 is an
    apex on the axis. cap0 / cap1 close the first / last ring. phase rotates the rings in fractions of a step."""
    bm = part.bm
    d, e1, e2 = basis(axis)
    c0 = Vector(center)
    rings = []
    for r, h in prof:
        if r < 1e-7:
            rings.append([bm.verts.new(c0 + d * h)])
        else:
            rings.append([bm.verts.new(c0 + d * h + (e1 * math.cos(a) + e2 * math.sin(a)) * r)
                          for a in (2 * math.pi * (k + phase) / sides for k in range(sides))])
    new = []
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        A, B = rings[i], rings[i + 1]
        if len(A) == 1 and len(B) == 1:
            continue
        nr, nh = h1 - h0, r0 - r1
        for k in range(sides):
            j = (k + 1) % sides
            q = [A[0], B[k], B[j]] if len(A) == 1 else [A[k], A[j], B[0]] if len(B) == 1 else \
                [A[k], A[j], B[j], B[k]]
            f = bm.faces.new(q)
            m = f.calc_center_median() - c0
            rad = m - d * m.dot(d)
            rad = rad.normalized() if rad.length > 1e-9 else e1
            new.append(orient(f, rad * nr + d * nh))
    for ring, want, on in ((rings[0], -d, cap0), (rings[-1], d, cap1)):
        if on and len(ring) > 2:
            new.append(orient(bm.faces.new(ring), want))
    return part.tag(new)


def fluted(part, center, axis, r, depth, n, h0, h1, cap=True):
    """Knurled bushing (handle, terminal cap, plug): 2n vertices around, every other one recessed by
    depth; cap closes the h1 end."""
    bm = part.bm
    d, e1, e2 = basis(axis)
    c0 = Vector(center)
    rings = [[bm.verts.new(c0 + d * h + (e1 * math.cos(math.pi * k / n) + e2 * math.sin(math.pi * k / n)) *
                           (r - depth * (k % 2))) for k in range(2 * n)] for h in (h0, h1)]
    new = []
    for k in range(2 * n):
        j = (k + 1) % (2 * n)
        f = bm.faces.new([rings[0][k], rings[0][j], rings[1][j], rings[1][k]])
        m = f.calc_center_median() - c0
        new.append(orient(f, m - d * m.dot(d)))
    if cap:
        new.append(orient(bm.faces.new(rings[1]), d))
    return part.tag(new)


def crenel(part, center, axis, r_out, r_in, teeth, h0, h1, frac=0.55):
    """Toothed disc (skirt of the Ts4315 selector): `teeth` teeth at r_out, roots down to r_in; frac is the
    fraction of the step under a tooth. The bottom is open - the disc sits on the panel."""
    bm = part.bm
    d, e1, e2 = basis(axis)
    c0 = Vector(center)
    ring = []
    for k in range(teeth):
        a0 = 2 * math.pi * k / teeth
        a1 = a0 + 2 * math.pi * frac / teeth
        a2 = 2 * math.pi * (k + 1) / teeth
        for r, a in ((r_out, a0), (r_out, a1), (r_in, a1), (r_in, a2)):
            ring.append(e1 * (r * math.cos(a)) + e2 * (r * math.sin(a)))
    bot = [bm.verts.new(c0 + d * h0 + q) for q in ring]
    top = [bm.verts.new(c0 + d * h1 + q) for q in ring]
    new = []
    n = len(ring)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new([bot[i], bot[j], top[j], top[i]])
        m = (ring[i] + ring[j]) / 2
        new.append(orient(f, m if m.length > 1e-9 else e1))
    new.append(orient(bm.faces.new(top), d))
    return part.tag(new)


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, k segments per span)."""
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


def u_handle(part, a, b, out, depth, rr, r, sides, lod):
    """Bar bracket: from surface point a along out for depth, along to b, back; corners are arcs of
    radius rr (lod > 0 - no arcs)."""
    a, b, out = Vector(a), Vector(b), Vector(out).normalized()
    t = (b - a).normalized()
    if lod > 0:
        pts = [a - out * 0.002, a + out * depth, b + out * depth, b - out * 0.002]
    else:
        ca, cb = a + out * (depth - rr) + t * rr, b + out * (depth - rr) - t * rr
        arc = (0.0, math.pi / 4, math.pi / 2)
        pts = [a - out * 0.002] + [ca - t * rr * math.cos(f) + out * rr * math.sin(f) for f in arc] + \
              [cb + t * rr * math.cos(f) + out * rr * math.sin(f) for f in arc[::-1]] + [b - out * 0.002]
    return g.pipe(part, [tuple(p) for p in pts], r, sides)


def hex_bolt(part, center, axis, r, h, washer=0.0):
    """Hex-head bolt (and a washer, washer is its radius) from point center along axis."""
    if washer:
        lathe(part, [(washer, 0.0), (washer, 0.0014), (0.0, 0.0014)], 10, center, axis)
    h0 = 0.0014 if washer else 0.0
    lathe(part, [(r, h0), (r, h0 + h * 0.82), (r * 0.80, h0 + h), (0.0, h0 + h)], 6, center, axis, phase=0.5)


def dome(part, center, axis, r, sides=6):
    """Rivet or screw head with a sphere."""
    return lathe(part, [(r, 0.0), (r * 0.72, r * 0.40), (0.0, r * 0.55)], sides, center, axis)


def quad_facing(part, corners, want):
    f = part.bm.faces.new([part.bm.verts.new(Vector(c)) for c in corners])
    return part.tag([orient(f, want)])


def fbox(part, frame, a0, a1, b0, b1, c0, c1, r=0.0, seg=0):
    """Box in frame `frame` with rounded edges: built in world axes and moved by the frame matrix (kgeo.box
    flips the bevel inside out in a rotated frame)."""
    bm = part.bm
    before = set(bm.verts)
    faces = g.box(part, a0, a1, b0, b1, c0, c1, r=r, seg=seg)
    m = frame.matrix()
    for v in bm.verts:
        if v not in before:
            v.co = m @ v.co
    bm.normal_update()
    return faces


def box_to(part, a, b, w, h, up=(0, 0, 1)):
    """Bar from point a to point b with cross-section w (across) x h (along up)."""
    a, b = Vector(a), Vector(b)
    u = (b - a).normalized()
    n = Vector(up) - u * Vector(up).dot(u)
    n.normalize()
    v = n.cross(u)
    return g.box(part, 0.0, (b - a).length, -w / 2, w / 2, -h / 2, h / 2, frame=g.Frame(a, u, v, n))


# --- case tray: profile along a rounded rectangle ------------------------------------------
def rrect_loop(x0, x1, y0, y1, r, nseg):
    """Rounded rectangle in the (a, b) plane, counter-clockwise: [(a, b, na, nb)], normals outward; nseg = 0
    gives sharp corners (the normal is the bisector of length sqrt(2), so an offset gives parallel walls)."""
    out = []
    corners = ((x1 - r, y0 + r, -90.0, x1, y0), (x1 - r, y1 - r, 0.0, x1, y1), (x0 + r, y1 - r, 90.0, x0, y1),
               (x0 + r, y0 + r, 180.0, x0, y0))
    for cx, cy, a0, kx_, ky_ in corners:
        if nseg == 0:
            a = math.radians(a0 + 45.0)
            out.append((kx_, ky_, math.cos(a) * math.sqrt(2.0), math.sin(a) * math.sqrt(2.0)))
            continue
        for k in range(nseg + 1):
            a = math.radians(a0 + 90.0 * k / nseg)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a), math.cos(a), math.sin(a)))
    return out


def loop_sweep(part, frame, loop, prof, seg_use=None, cap0=None, cap1=None):
    """Profile prof [(d, c)] along the closed contour loop (rrect_loop) in frame `frame`: d is the offset
    along the contour normal outward, c along frame.n. The profile is traversed with the solid on the left
    (up the outer wall, inward across the top, down the inner one), faces look out of the solid. seg_use is a
    function (part) -> select a region, called for each profile segment; cap0 / cap1 are the same kind of
    function: close the first ring (facing against frame.n) / the last (facing along frame.n)."""
    bm = part.bm
    rings = [[bm.verts.new(frame.p(a + d * na, b + d * nb, c)) for a, b, na, nb in loop] for d, c in prof]
    nrm = [frame.u * na + frame.v * nb for _, _, na, nb in loop]
    n = len(loop)
    for i in range(len(prof) - 1):
        if seg_use:
            seg_use[i](part)
        (d0, c0), (d1, c1) = prof[i], prof[i + 1]
        if abs(d1 - d0) + abs(c1 - c0) < 1e-9:
            continue
        new = []
        for k in range(n):
            j = (k + 1) % n
            f = bm.faces.new([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]])
            want = (nrm[k] + nrm[j]) * (c1 - c0) + frame.n * (2.0 * (d0 - d1))
            new.append(orient(f, want))
        part.tag(new)
    for ring, use, sgn in ((rings[0], cap0, -1.0), (rings[-1], cap1, 1.0)):
        if use:
            use(part)
            part.tag([orient(bm.faces.new(ring), frame.n * sgn)])


def rrect_prism(part, frame, x0, x1, y0, y1, r, nseg, c0, c1):
    """Plate over a rounded rectangle in frame `frame`, thickness c0..c1 along frame.n."""
    poly = [(a, b) for a, b, _, _ in rrect_loop(x0, x1, y0, y1, r, nseg)]
    return g.prism(part, poly, (0, 1), c0, c1, frame=frame)


# --- crocodile clip (from M16) ------------------------------------------------------------
def croc(jaw, boot, fr, lod, k=1.0, gap=0.0, teeth=False, spring=True, sides=8):
    """Crocodile clip in frame fr: origin at the jaw tips, u from the tip to the tail, n up (jaws open
    along n), v across. Two jaws from a strip (teeth - with teeth near the tip), rivet, spring; soft cap on
    the tail (sides faces). k is the scale (1 = a 50 mm clip); gap - the jaws are spread at the tip by this
    much on each side (fading out toward the rivet; m before scaling): a clip on a thick terminal. The cap
    tail is fr.p(0.061 k, 0, 0)."""
    prof = [(0.0, 0.0006), (0.008, 0.0009), (0.017, 0.0012), (0.023, 0.0028), (0.030, 0.0042), (0.042, 0.0066),
            (0.050, 0.0082)]
    prof = [(a, c + gap * max(0.0, 1.0 - a / 0.023)) for a, c in prof]
    for s in (1, -1):
        pts = [fr.p(a * k, 0.0, s * c * k) for a, c in (prof if lod == 0 else prof[::3])]
        g.sweep(jaw, pts, fr.v, 0.0003 * k, 0.0030 * k)
        if lod == 0 and teeth and gap == 0.0:
            for i in range(5):
                a0 = (0.0015 + 0.003 * i) * k
                c0 = s * 0.0006 * k
                tri = [(a0 - 0.0012 * k, c0), (a0 + 0.0012 * k, c0), (a0, c0 - s * 0.0007 * k)]
                g.prism(jaw, tri, (0, 2), -0.0027 * k, 0.0027 * k, frame=fr)
    if lod == 0 and spring:
        g.cyl(jaw, (0.0245 * k, 0.0, 0.0), "y", 0.0012 * k, 0.0074 * k, 6, frame=fr)
        g.cyl(jaw, (0.0275 * k, 0.0, 0.0), "y", 0.0021 * k, 0.0052 * k, 6, frame=fr)
    sec = [(0.027, 0.0040, 0.0044), (0.031, 0.0048, 0.0058), (0.042, 0.0050, 0.0064), (0.052, 0.0046, 0.0058),
           (0.058, 0.0032, 0.0036), (0.061, 0.0022, 0.0023)]
    if lod > 0:
        sec = sec[::2] + [sec[-1]]
    g.tube_var(boot, [fr.p(a * k, 0.0, 0.0) for a, _, _ in sec], [(rb * k, rc * k) for _, rb, rc in sec],
               sides if lod == 0 else 5)
