"""M84's own shapes: the kit (source/models/_kit) is shared by all models and is not changed, so everything
missing from kgeo lives here, in the generator folder.

- solids of revolution (lathe), a torus (the flywheel rim), a single-face circle - from the former
  build_m84.py (from M76);
- a nut and a bolt head with chamfered corners (like a turned hexagon: the end is a circle across
  the flats), a washer, a slotted screw head, a knurled plug, a channel, a plate with a rounded end
  and a chamfer;
- a smooth hose path: a Catmull-Rom curve through support points, points denser at bends;
- the work pose in the --look preview: the kit (krender.place_look, the look's move) can only shift
  a group, while the lever and the needle rotate - install_pose() makes move accept a 4x4 matrix
  (a rotation about an axis). The kit file is not changed: the wrapper is installed from the M84
  generator and lives only in its run.
"""
import math

from mathutils import Matrix, Vector

import kgeo as g


# --- frames -------------------------------------------------------------------------------------
def axis_frame(center, axis, phase=0.0):
    """Frame with axis n along `axis` ("x", "y", "z", "-x"... or a vector); u, v are across, rotated by phase."""
    if isinstance(axis, str):
        sign = -1.0 if axis.startswith("-") else 1.0
        axis = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[axis[-1]]
        axis = tuple(sign * c for c in axis)
    n = Vector(axis).normalized()
    ref = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = ref.cross(n).normalized()
    v = n.cross(u).normalized()
    if phase:
        c, s = math.cos(phase), math.sin(phase)
        u, v = u * c + v * s, v * c - u * s
    return g.Frame(center, u, v, n)


def rot_about(point, axis, angle):
    """Matrix of a rotation by angle about the axis `axis` through the point (the work pose in the preview)."""
    p = Vector(point)
    return Matrix.Translation(p) @ Matrix.Rotation(angle, 4, Vector(axis)) @ Matrix.Translation(-p)


def _outward(faces, center):
    for f in faces:
        f.normal_update()
        if f.normal.dot(f.calc_center_median() - center) < 0:
            f.normal_flip()


# --- solids of revolution -----------------------------------------------------------------------
def lathe(part, fr, prof, sides, cap_lo=False, cap_hi=False, phase=0.0):
    """Solid of revolution about the axis fr.n (from M76): the profile [(r, h)] from the bottom up along
    the outer side; faces are turned outward.
    """
    bm = part.bm
    angs = [phase + 2 * math.pi * k / sides for k in range(sides)]
    rings = [[bm.verts.new(fr.p(r * math.cos(a), r * math.sin(a), h)) for a in angs] for r, h in prof]
    faces = []
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        for k in range(sides):
            j = (k + 1) % sides
            f = bm.faces.new([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]])
            am = phase + (k + 0.5) * 2 * math.pi / sides
            want = (fr.u * math.cos(am) + fr.v * math.sin(am)) * (h1 - h0) - fr.n * (r1 - r0)
            f.normal_update()
            if f.normal.dot(want) < 0:
                f.normal_flip()
            faces.append(f)
    for ring, sign, on in ((rings[0], -1, cap_lo), (rings[-1], 1, cap_hi)):
        if on:
            f = bm.faces.new(ring)
            f.normal_update()
            if f.normal.dot(fr.n) * sign < 0:
                f.normal_flip()
            faces.append(f)
    return part.tag(faces)


def torus(part, fr, R, r, n_major, n_minor):
    """Torus about the axis fr.n (from M76): the flywheel rim."""
    bm = part.bm
    rings = []
    for i in range(n_major):
        a = 2 * math.pi * i / n_major
        d = fr.u * math.cos(a) + fr.v * math.sin(a)
        rings.append([bm.verts.new(fr.o + d * (R + r * math.cos(b)) + fr.n * (r * math.sin(b)))
                      for b in [2 * math.pi * j / n_minor for j in range(n_minor)]])
    faces = []
    for i in range(n_major):
        i2 = (i + 1) % n_major
        am = 2 * math.pi * (i + 0.5) / n_major
        d = fr.u * math.cos(am) + fr.v * math.sin(am)
        for j in range(n_minor):
            j2 = (j + 1) % n_minor
            f = bm.faces.new([rings[i][j], rings[i2][j], rings[i2][j2], rings[i][j2]])
            bm_ = 2 * math.pi * (j + 0.5) / n_minor
            f.normal_update()
            if f.normal.dot(d * math.cos(bm_) + fr.n * math.sin(bm_)) < 0:
                f.normal_flip()
            faces.append(f)
    return part.tag(faces)


def disc(part, fr, r, h, n, phase=0.0):
    """A circle as one face in the plane h of the frame fr, looking along fr.n (the dial, the glass)."""
    bm = part.bm
    vs = [bm.verts.new(fr.p(r * math.cos(phase + 2 * math.pi * i / n), r * math.sin(phase + 2 * math.pi * i / n), h))
          for i in range(n)]
    f = bm.faces.new(vs)
    f.normal_update()
    if f.normal.dot(fr.n) < 0:
        f.normal_flip()
    return part.tag([f])


# --- fasteners ----------------------------------------------------------------------------------
def nut(part, fr, h0, h1, s, ch_lo=True, ch_hi=True, cap_lo=True, cap_hi=True, phase=0.0, k=0.16):
    """A hexagon across flats s (a nut, a bolt head, a fitting) along fr.n from h0 to h1. A chamfer on the
    corners (ch_lo / ch_hi), as on a turned nut: the end is a hexagon at the face mid-points, the
    corners are cut. A bottom end is not needed on a support - cap_lo=False.
    """
    bm = part.bm
    R = s / math.sqrt(3.0)
    ri = s / 2.0
    c = k * R
    corners = [phase + math.pi / 3 * i for i in range(6)]
    mids = [a + math.pi / 6 for a in corners]

    def ring(rad, angs, h):
        return [bm.verts.new(fr.p(rad * math.cos(a), rad * math.sin(a), h)) for a in angs]
    c_lo = ring(R, corners, h0 + (c if ch_lo else 0.0))
    c_hi = ring(R, corners, h1 - (c if ch_hi else 0.0))
    m_lo = ring(ri, mids, h0) if ch_lo else None
    m_hi = ring(ri, mids, h1) if ch_hi else None
    faces = []
    for i in range(6):
        j = (i + 1) % 6
        loop = [c_lo[i]] + ([m_lo[i]] if ch_lo else []) + [c_lo[j], c_hi[j]] + ([m_hi[i]] if ch_hi else []) + [c_hi[i]]
        faces.append(bm.faces.new(loop))
        if ch_hi:
            faces.append(bm.faces.new([m_hi[i - 1], c_hi[i], m_hi[i]]))
        if ch_lo:
            faces.append(bm.faces.new([m_lo[i - 1], c_lo[i], m_lo[i]]))
    if cap_hi:
        faces.append(bm.faces.new(m_hi if ch_hi else c_hi))
    if cap_lo:
        faces.append(bm.faces.new(m_lo if ch_lo else c_lo))
    _outward(faces, fr.p(0.0, 0.0, (h0 + h1) / 2))
    return part.tag(faces)


def washer(part, fr, h0, h1, r, sides=10):
    """Washer on a support: the side and the top (the bottom is on the support, the hole is closed by the head)."""
    return lathe(part, fr, [(r, h0), (r, h1)], sides, cap_hi=True)


def pan_head(part, fr, h0, r, h, sides=8, phase=0.0, segs=3):
    """Pan head of a screw or rivet: round, on the support h0 (no invisible bottom); segs is the number of
    belts along the height.
    """
    if segs >= 3:
        prof = [(r, h0), (r * 0.97, h0 + 0.35 * h), (r * 0.78, h0 + 0.78 * h), (r * 0.42, h0 + h)]
    else:
        prof = [(r, h0), (r * 0.9, h0 + 0.55 * h), (r * 0.5, h0 + h)]
    return lathe(part, fr, prof, sides, cap_hi=True, phase=phase)


def slot(part, fr, h_top, length, width, depth, angle):
    """Slot on a screw head: a dark strip in the u-v plane of the frame, rotated by angle (its own region
    of the part - dark).
    """
    c, s = math.cos(angle), math.sin(angle)
    f2 = g.Frame(fr.o, fr.u * c + fr.v * s, fr.v * c - fr.u * s, fr.n)
    return g.box(part, -length / 2, length / 2, -width / 2, width / 2, h_top - depth, h_top + 0.00008, frame=f2)


def knurled(part, fr, r, depth, h0, h1, flutes, ch=0.0015, phase=0.0):
    """Knurled plug: a star-shaped side (ridge - valley), a chamfer on top, the top and the bottom."""
    bm = part.bm
    n = 2 * flutes
    angs = [phase + 2 * math.pi * k / n for k in range(n)]
    rr = [r if k % 2 == 0 else r - depth for k in range(n)]
    lo = [bm.verts.new(fr.p(rr[k] * math.cos(a), rr[k] * math.sin(a), h0)) for k, a in enumerate(angs)]
    hi = [bm.verts.new(fr.p(rr[k] * math.cos(a), rr[k] * math.sin(a), h1 - ch)) for k, a in enumerate(angs)]
    rt = r - depth - ch
    top = [bm.verts.new(fr.p(rt * math.cos(a), rt * math.sin(a), h1)) for a in angs]
    faces = []
    for k in range(n):
        j = (k + 1) % n
        faces.append(bm.faces.new([lo[k], lo[j], hi[j], hi[k]]))
        faces.append(bm.faces.new([hi[k], hi[j], top[j], top[k]]))
    faces.append(bm.faces.new(top))
    faces.append(bm.faces.new(lo[::-1]))
    _outward(faces, fr.p(0.0, 0.0, h0 + (h1 - h0) * 0.3))
    return part.tag(faces)


# --- profiles -----------------------------------------------------------------------------------
def channel(part, x0, x1, yc, w, h, t):
    """Channel with flanges down along x (a plate support): a U profile w x h, wall t."""
    a, b = yc - w / 2, yc + w / 2
    poly = [(a, 0.0), (a + t, 0.0), (a + t, h - t), (b - t, h - t), (b - t, 0.0), (b, 0.0), (b, h), (a, h)]
    return g.prism(part, poly, (1, 2), x0, x1)


def rrect(cx, cy, w, h, r, seg=3):
    """Rectangle with rounded corners (counter-clockwise)."""
    pts = []
    for (sx, sy), a0 in (((1, -1), -90.0), ((1, 1), 0.0), ((-1, 1), 90.0), ((-1, -1), 180.0)):
        ox, oy = cx + sx * (w / 2 - r), cy + sy * (h / 2 - r)
        for i in range(seg + 1):
            a = math.radians(a0 + 90.0 * i / seg)
            pts.append((ox + r * math.cos(a), oy + r * math.sin(a)))
    return pts


def round_end(x1, half, cx, seg=6):
    """A strip of width 2*half along the second axis up to x1, the rear end is a semicircle around
    (cx, 0) (counter-clockwise).
    """
    pts = [(x1, -half), (x1, half)]
    for i in range(seg + 1):
        a = math.radians(90.0 + 180.0 * i / seg)
        pts.append((cx + half * math.cos(a), half * math.sin(a)))
    return pts


def round_top(cx, cz, half, z_low, seg=6):
    """A post of width 2*half from z_low upward, the top is a semicircle around (cx, cz) (counter-clockwise)."""
    pts = [(cx - half, z_low), (cx + half, z_low)]
    for i in range(seg + 1):
        a = math.pi * i / seg
        pts.append((cx + half * math.cos(a), cz + half * math.sin(a)))
    return pts


def prism_bevel(part, poly, axes, c0, c1, frame=None, r=0.0, seg=1):
    """g.prism with a chamfer along the outline of both ends (lever plate, cheeks, posts)."""
    bm = part.bm
    before = set(bm.faces)
    faces = g.prism(part, poly, axes, c0, c1, frame=frame)
    if r > 0 and seg > 0:
        edges = list({e for f in faces[:2] for e in f.edges})
        g.bevel(bm, edges, r, seg)
        new = [f for f in bm.faces if f not in before]
        part.tag(new)
        return new
    return faces


# --- hose path ----------------------------------------------------------------------------------
def catmull(pts, k):
    """Polyline -> a curve through the same points (Catmull-Rom, as in M73): k points per segment."""
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
    return out


def smooth_path(pts, step_deg=10.0, max_len=0.014, dense=32):
    """Smooth path through support points: the curve is computed densely, and the points kept are where
    the direction has turned by step_deg or a straight stretch is longer than max_len - denser at
    bends, sparser on straights.
    """
    d = catmull(pts, dense)
    out = [d[0]]
    for i in range(1, len(d) - 1):
        a = d[i] - out[-1]
        b = d[i + 1] - d[i]
        if a.length < 1e-9 or b.length < 1e-9:
            continue
        if math.degrees(a.angle(b)) >= step_deg or a.length >= max_len:
            out.append(d[i])
    out.append(d[-1])
    return [tuple(q) for q in out]


def route2d(start, heading_deg, segs, step_deg=15.0, max_len=0.012):
    """Planar path of lines and arcs of constant radius (a hose over the plate): segs is
    [("line", L) | ("arc", R, deg)], deg > 0 turns left (counter-clockwise seen from above). Points are
    every step_deg on arcs and at least every max_len on straights. Returns [(x, y, s)], s is the path
    length from the start.
    """
    x, y = start
    h = math.radians(heading_deg)
    s = 0.0
    out = [(x, y, 0.0)]
    for seg in segs:
        if seg[0] == "line":
            ln = seg[1]
            n = max(1, int(math.ceil(ln / max_len)))
            for i in range(1, n + 1):
                d = ln * i / n
                out.append((x + d * math.cos(h), y + d * math.sin(h), s + d))
            x, y, s = x + ln * math.cos(h), y + ln * math.sin(h), s + ln
        else:
            r, deg = seg[1], seg[2]
            sign = 1.0 if deg > 0 else -1.0
            cx, cy = x - sign * r * math.sin(h), y + sign * r * math.cos(h)
            a0 = math.atan2(y - cy, x - cx)
            da = math.radians(deg)
            n = max(1, int(math.ceil(abs(deg) / step_deg)))
            for i in range(1, n + 1):
                a = a0 + da * i / n
                out.append((cx + r * math.cos(a), cy + r * math.sin(a), s + r * abs(da) * i / n))
            x, y = cx + r * math.cos(a0 + da), cy + r * math.sin(a0 + da)
            h += da
            s += r * abs(da)
    return out


def smoothstep(a, b, x):
    t = min(max((x - a) / max(b - a, 1e-9), 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


# --- work pose in the preview -------------------------------------------------------------------
def install_pose():
    """krender.place_look: the look's move maps a group to a shift (as in the kit) or a 4x4 matrix (a
    rotation). Preview only: in the p3d the pose is set by model.cfg (bones on the sources ozl_work,
    ozl_needle).
    """
    import krender
    if getattr(krender.place_look, "_m84_pose", False):
        return
    orig = krender.place_look

    def place_look(parts, kind_table, origin, remap=None, glow=1.5, sharp_deg=40.0, panels=None, move=None):
        move = dict(move or {})
        mats = {k: v for k, v in move.items() if isinstance(v, Matrix)}
        shifts = {k: v for k, v in move.items() if not isinstance(v, Matrix)}
        obs = orig(parts, kind_table, origin, remap=remap, glow=glow, sharp_deg=sharp_deg, panels=panels,
                   move=shifts)
        for p, ob in zip(parts, obs):
            if p.group in mats:
                ob.matrix_world = mats[p.group]
        return obs
    place_look._m84_pose = True
    krender.place_look = place_look
