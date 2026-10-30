"""Cassette tape recorder "Elektronika-302" on the M15 shelf (the "work" loop).

Modelled on a 1982 unit; size 315 x 225 x 90 mm, 3.5 kg. On top at the left - the speaker grille (8 x 9
cells), at the right - the cassette compartment lid with a window, under it a cassette (100.4 x 63.8 x 12,
IEC 60094-7) with two reels; in front - a slanted aluminium strip: volume and tone knobs, a needle
"recording monitor" indicator, six keys (record with a red dot, rewind, play, stop, eject); at the face -
a folding handle on hinges at the sides; at the right side - a socket with a cable to the radio scanner
place (slot 2). The inscriptions of the original are not copied: only divisions, digits and symbols.

"Work" (OZL_Work): the cassette reels turn - bones ozl_reel_l and ozl_reel_r on the source ozl_work
(model.cfg loop); the supply reel is full and turns slower (1 turn per pass), the take-up reel is almost
empty - twice as fast; the indicator needle trembles (ozl_needle, wobble); the "record" and "play" keys
are pressed in (ozl_keys, pose). At rest everything stands still, the needle on the stop.
The recorder axes match the table (face toward -y); origin - the middle of the bottom (layout.REC).
"""
import math

from mathutils import Vector

import kgeo as g
import layout as L
from m15_geo import box_to, frame_plate, lathe, rod, spline

REEL_DX = 0.0213                                             # reels 42.6 mm apart
REEL_R = (0.0235, 0.0140)                                    # winding: the supply reel is full, the take-up is empty
NEEDLE_SWEEP = 80.0                                          # needle swing from stop to stop, degrees
NEEDLE_LEN = 0.0105
KEY_TRAVEL = 0.004                                           # key travel
KEYS_DOWN = (0, 3)                                           # "record" and "play"
ZF = 0.004                                                   # feet


def W(x, y, z):
    ox, oy, oz = L.REC
    return Vector((ox + x, oy + y, oz + z))


def strip_frame():
    """Slanted strip: origin - the front bottom edge in the middle, u along x, v up the slope toward the
    deck, n outward."""
    y0, y1, z0, z1 = L.REC_STRIP
    t = math.atan2(z1 - z0, y1 - y0)
    return g.Frame(W(0.0, y0, z0), Vector((1, 0, 0)), Vector((0, math.cos(t), math.sin(t))),
                   Vector((0, -math.sin(t), math.cos(t)))), math.hypot(y1 - y0, z1 - z0)


def vu_geom():
    """Indicator on the strip: (middle along the slope, needle axis in local s, stop at the left - direction)."""
    sf, ln = strip_frame()
    s_c = 0.028
    piv = s_c - L.VU[2] / 2 + 0.0008
    return sf, s_c, piv


def needle_axis():
    """Needle axis: from the scale toward the person (rule of M01, M08, M14: plus is clockwise)."""
    sf, s_c, piv = vu_geom()
    p = sf.p(L.VU[0], piv, 0.0010)
    return p, p + sf.n * 0.01


def reel_axis(k):
    cx, cy, cw, ch, ct = L.CASS
    x = cx + (-REEL_DX if k == 0 else REEL_DX)
    return W(x, cy, 0.068), W(x, cy, 0.086)


def keys_axis():
    """Key travel - along the strip normal inward; the metre is the model.cfg offset in metres."""
    sf, ln = strip_frame()
    p = sf.p(L.KEYS_REC[0], 0.02, 0.0)
    return p, p - sf.n * 1.0


def keys_move():
    """Shift of the pressed keys for the "work" preview."""
    sf, ln = strip_frame()
    return tuple(-sf.n * KEY_TRAVEL)


def needle_pose(mid):
    """Needle pose in the "work" preview: (axis point, right-hand axis, angle)."""
    sf, s_c, piv = vu_geom()
    return sf.p(L.VU[0], piv, 0.0010), -sf.n, math.radians(NEEDLE_SWEEP * mid)


def build_recorder(P, spec, sel):
    """sel - selection names: reel_l, reel_r, needle, keys. Returns the parts."""
    lod = spec["lod"]
    hw, hd, H = L.REC_W / 2, L.REC_D / 2, L.REC_H
    y0s, y1s, z0s, z1s = L.REC_STRIP
    ox, oy, oz = L.REC
    parts = []
    bd = P("rec_body", "rec_body")
    parts.append(bd)
    if lod == 2:
        g.box(bd, ox - hw, ox + hw, oy - hd, oy + hd, oz, oz + H + 0.003)
        return parts
    # body: bottom up to the strip, a deck with a compartment for the cassette, the slanted strip
    g.box(bd, ox - hw, ox + hw, oy - hd, oy + hd, oz + ZF, oz + z0s, **(dict(r=0.005, seg=2) if lod == 0 else {}))
    wx0, wx1, wy0, wy1 = L.REC_WIN
    if lod == 0:
        frame_plate(bd, (ox - hw, ox + hw, oy + y1s, oy + hd), (ox + wx0, ox + wx1, oy + wy0, oy + wy1), oz + z0s, oz + H,
                    bevel=0.003)
        g.box(bd, ox + wx0, ox + wx1, oy + wy0, oy + wy1, oz + z0s, oz + 0.070)       # compartment floor
    else:
        g.box(bd, ox - hw, ox + hw, oy + y1s, oy + hd, oz + z0s, oz + H)
    sp = P("rec_strip", "rec_alu")
    g.prism(sp, [(oy + y0s, oz + z0s), (oy + y1s, oz + z0s), (oy + y1s, oz + z1s)], (1, 2), ox - hw + 0.002, ox + hw - 0.002)
    parts.append(sp)
    # speaker grille: cloth, frame, rods (those along y are slightly lower, no flicker at the crossings)
    gx0, gx1, gy0, gy1 = L.REC_GRILLE
    gr = P("rec_grille", "rec_grille")
    parts.append(gr)
    if lod == 0:
        cl = P("rec_cloth", "rec_cloth")
        g.box(cl, ox + gx0 + 0.004, ox + gx1 - 0.004, oy + gy0 + 0.004, oy + gy1 - 0.004, oz + H, oz + H + 0.0006)
        parts.append(cl)
        frame_plate(gr, (ox + gx0, ox + gx1, oy + gy0, oy + gy1), (ox + gx0 + 0.006, ox + gx1 - 0.006, oy + gy0 + 0.006,
                                                                     oy + gy1 - 0.006), oz + H, oz + H + 0.0035, bevel=0.0012)
        ix0, ix1, iy0, iy1 = gx0 + 0.006, gx1 - 0.006, gy0 + 0.006, gy1 - 0.006
        for k in range(1, 9):
            x = ix0 + (ix1 - ix0) * k / 9
            g.box(gr, ox + x - 0.002, ox + x + 0.002, oy + iy0, oy + iy1, oz + H, oz + H + 0.0030)
        for k in range(1, 8):
            y = iy0 + (iy1 - iy0) * k / 8
            g.box(gr, ox + ix0, ox + ix1, oy + y - 0.002, oy + y + 0.002, oz + H, oz + H + 0.0035)
    else:
        g.box(gr, ox + gx0, ox + gx1, oy + gy0, oy + gy1, oz + H, oz + H + 0.003)
    # compartment lid: a frame with a window, a nameplate without inscription, the window is glass
    lx0, lx1, ly0, ly1 = L.REC_LID
    ld = P("rec_lid", "rec_lid")
    parts.append(ld)
    if lod == 0:
        frame_plate(ld, (ox + lx0, ox + lx1, oy + ly0, oy + ly1), (ox + wx0 + 0.004, ox + wx1 - 0.004, oy + wy0 + 0.004,
                                                                     oy + wy1 - 0.002), oz + H, oz + H + 0.0035, bevel=0.0012)
        pl = P("rec_plate", "rec_plate")
        g.box(pl, ox + 0.040, ox + 0.118, oy + ly0 + 0.005, oy + ly0 + 0.0145, oz + H + 0.0035, oz + H + 0.0042)
        parts.append(pl)
        gl = P("rec_lid_glass", "steel", section="glass")
        g.box(gl, ox + wx0 + 0.003, ox + wx1 - 0.003, oy + wy0 + 0.003, oy + wy1 - 0.001, oz + H + 0.0024, oz + H + 0.0030)
        parts.append(gl)
        parts += build_cassette(P, sel)
    else:
        g.box(ld, ox + lx0, ox + lx1, oy + ly0, oy + ly1, oz + H, oz + H + 0.003)
    parts += build_strip_bits(P, spec, sel)
    # handle: folded toward the face, on hinges at the sides
    hn = P("rec_handle", "rec_handle")
    zc = oz + 0.018
    pts = [(ox - hw - 0.003, oy - hd + 0.016, zc), (ox - hw - 0.003, oy - hd - 0.0055, zc),
           (ox + hw + 0.003, oy - hd - 0.0055, zc), (ox + hw + 0.003, oy - hd + 0.016, zc)]
    g.sweep(hn, pts, (0, 0, 1), 0.0028, 0.0055)
    parts.append(hn)
    if lod == 0:
        st = P("rec_hinges", "steel")
        for s in (-1, 1):
            g.box(st, *sorted((ox + s * hw, ox + s * (hw + 0.0010))), oy - hd + 0.006, oy - hd + 0.026, oz + 0.010,
                  oz + 0.026)
            g.cyl(st, (ox + s * (hw + 0.0068), oy - hd + 0.016, zc), "x", 0.0032, 0.0016, 8)
        parts.append(st)
        ft = P("rec_feet", "rubber")
        for sx in (-1, 1):
            for sy in (-1, 1):
                g.cyl(ft, (ox + sx * (hw - 0.022), oy + sy * (hd - 0.022), oz + ZF / 2), "z", 0.008, ZF, 6)
        parts.append(ft)
        parts += build_cable(P)
    return parts


def build_cassette(P, sel):
    """Cassette in the compartment: a body with a window (the label is a decal), a transparent window, reels
    with teeth and the film winding - the reel bones."""
    cx, cy, cw, ch, ct = L.CASS
    ox, oy, oz = L.REC
    z0, z1 = oz + 0.071, oz + 0.071 + ct
    x0, x1, y0, y1 = ox + cx - cw / 2, ox + cx + cw / 2, oy + cy - ch / 2, oy + cy + ch / 2
    sh = P("cass_shell", "cassette")
    g.box(sh, x0, x1, y0, y1, z0, z0 + 0.0015)
    for a, b, c, d in ((x0, x1, y0, y0 + 0.002), (x0, x1, y1 - 0.002, y1), (x0, x0 + 0.002, y0, y1), (x1 - 0.002, x1, y0, y1)):
        g.box(sh, a, b, c, d, z0 + 0.0015, z1 - 0.0015)
    lb = P("cass_top", "cass_label")
    wx, wy = 0.031, 0.010
    frame_plate(lb, (x0, x1, y0, y1), (ox + cx - wx, ox + cx + wx, oy + cy - wy, oy + cy + wy), z1 - 0.0015, z1)
    gl = P("cass_window", "steel", section="glass")
    g.box(gl, ox + cx - wx, ox + cx + wx, oy + cy - wy, oy + cy + wy, z1 - 0.0011, z1 - 0.0007)
    parts = [sh, lb, gl]
    zh0, zh1 = z0 + 0.0016, z1 - 0.0016
    for k, (key, rp) in enumerate(((sel["reel_l"], REEL_R[0]), (sel["reel_r"], REEL_R[1]))):
        hx = ox + cx + (-REEL_DX if k == 0 else REEL_DX)
        c = (hx, oy + cy, 0.0)
        hb = P("reel%d_hub" % k, "hub", group=key)
        lathe(hb, [(0.0068, zh0), (0.0110, zh0), (0.0110, zh1), (0.0068, zh1)], 12, center=c, closed=True)
        for j in range(6):
            a = 2 * math.pi * j / 6
            fr = g.Frame(Vector((hx, oy + cy, zh0)), Vector((math.cos(a), math.sin(a), 0)),
                         Vector((-math.sin(a), math.cos(a), 0)), Vector((0, 0, 1)))
            g.box(hb, 0.0040, 0.0069, -0.0008, 0.0008, 0.0, zh1 - zh0 - 0.0015, frame=fr)
        sp = P("reel%d_spindle" % k, "steel", group=key)
        g.cyl(sp, (hx, oy + cy, (oz + 0.070 + zh1 - 0.002) / 2), "z", 0.0030, zh1 - 0.002 - oz - 0.070, 8)
        tp = P("reel%d_tape" % k, "tape", group=key)
        zt = (zh0 + zh1) / 2
        lathe(tp, [(0.0111, zt - 0.0019), (rp, zt - 0.0019), (rp, zt + 0.0019), (0.0111, zt + 0.0019)], 16, center=c,
              closed=True)
        parts += [hb, sp, tp]
    return parts


def build_strip_bits(P, spec, sel):
    """On the strip: volume and tone knobs, the indicator (the needle is a bone), six keys (record and play -
    the "work" pose), the field under the keys."""
    lod = spec["lod"]
    sf, ln = strip_frame()
    parts = []
    kn = P("rec_knobs", "knob")
    parts.append(kn)
    for x in L.KNOBS:
        c = sf.p(x, 0.030, 0.0)
        if lod == 0:
            lathe(kn, [(0.0100, 0.0), (0.0100, 0.0022), (0.0089, 0.0030), (0.0088, 0.0100), (0.0079, 0.0118)], 14, center=c,
                  axis=sf.n, cap1=True)
        else:
            lathe(kn, [(0.0095, 0.0), (0.0090, 0.0115)], 8, center=c, axis=sf.n, cap1=True)
    if lod == 0:
        kc = P("rec_knob_caps", "knob_cap")
        km = P("rec_knob_marks", "knob_mark")
        for x, deg in zip(L.KNOBS, (40.0, -20.0)):
            c = sf.p(x, 0.030, 0.0118)
            lathe(kc, [(0.0060, 0.0), (0.0060, 0.0005)], 14, center=c, axis=sf.n, cap1=True)
            a = math.radians(deg + 90)
            d = sf.u * math.cos(a) + sf.v * math.sin(a)
            box_to(km, c + sf.n * 0.0004 + d * 0.0062, c + sf.n * 0.0004 + d * 0.0084, 0.0012, 0.0010, up=sf.n)
        parts += [kc, km]
    # indicator: frame, scale (decal), needle, glass
    sf, s_c, piv = vu_geom()
    vx, vw, vh = L.VU
    if lod == 0:
        bz = P("rec_vu_bezel", "rec_body")
        frame_plate(bz, (vx - vw / 2 - 0.0025, vx + vw / 2 + 0.0025, s_c - vh / 2 - 0.0025, s_c + vh / 2 + 0.0025),
                    (vx - vw / 2, vx + vw / 2, s_c - vh / 2, s_c + vh / 2), 0.0, 0.0028, frame=sf, bevel=0.0006)
        fc = P("rec_vu_face", "vu")
        g.box(fc, vx - vw / 2, vx + vw / 2, s_c - vh / 2, s_c + vh / 2, 0.0, 0.0006, frame=sf)
        nd = P("rec_needle", "needle", group=sel["needle"])
        p0 = sf.p(vx, piv, 0.0011)
        a = math.radians(90 + NEEDLE_SWEEP / 2)                # rest: at the left stop
        d = sf.u * math.cos(a) + sf.v * math.sin(a)
        box_to(nd, p0 - d * 0.0012, p0 + d * NEEDLE_LEN, 0.0006, 0.0004, up=sf.n)
        g.cyl(nd, (0, 0, 0.0), "z", 0.0011, 0.0006, 8, frame=g.Frame(p0, sf.u, sf.v, sf.n))
        vg = P("rec_vu_glass", "steel", section="glass")
        g.box(vg, vx - vw / 2, vx + vw / 2, s_c - vh / 2, s_c + vh / 2, 0.0020, 0.0024, frame=sf)
        parts += [bz, fc, nd, vg]
    # keys
    kx0, kx1, n = L.KEYS_REC
    gap = 0.0018
    kw = (kx1 - kx0 - gap * (n - 1)) / n
    if lod == 0:
        wl = P("rec_key_well", "rec_body")
        g.box(wl, kx0 - 0.003, kx1 + 0.003, 0.0005, ln - 0.008, 0.0, 0.0009, frame=sf)
        parts.append(wl)
    up = P("rec_keys", "key")
    dn = P("rec_keys_down", "key", group=sel["keys"])
    dots = P("rec_key_dots", "dot_red", group=sel["keys"]) if lod == 0 else None
    dot_b = P("rec_key_dot_b", "dot_blue") if lod == 0 else None
    for k in range(n):
        xa = kx0 + k * (kw + gap)
        prt = dn if k in KEYS_DOWN else up
        if lod == 0:
            g.box(prt, xa, xa + kw, -0.003, ln - 0.012, 0.0009, 0.0080, frame=sf, r=0.0012, seg=1)
        else:
            g.box(prt, xa, xa + kw, -0.003, ln - 0.012, 0.0, 0.0080, frame=sf)
        if lod == 0 and k in (0, 5):
            c = sf.p(xa + kw / 2, (ln - 0.012) * 0.62, 0.0080)
            lathe(dots if k == 0 else dot_b, [(0.0024, 0.0), (0.0024, 0.0004)], 12, center=c, axis=sf.n, cap1=True)
    parts += [up, dn] + ([dots, dot_b] if lod == 0 else [])
    return parts


def build_cable(P):
    """Socket at the right side, plug, cable along the shelf to the radio scanner place (slot 2): at an empty
    place - a cable without the device, the plug lies on the mat."""
    hw = L.REC_W / 2
    st = P("rec_socket", "steel")
    g.cyl(st, tuple(W(hw + 0.0008, 0.060, 0.036)), "x", 0.0085, 0.0016, 12)
    pg = P("rec_plug", "black")
    g.cyl(pg, tuple(W(hw + 0.012, 0.060, 0.036)), "x", 0.0068, 0.020, 12)
    lathe(pg, [(0.0062, 0.0), (0.0042, 0.012), (0.0032, 0.016)], 10, center=W(hw + 0.022, 0.060, 0.036), axis=(1, 0, 0))
    cb = P("rec_cable", "black")
    ox, oy, oz = L.REC
    mx0, mx1, my0, my1, mt = L.MAT2
    end = Vector((mx0 - 0.020, 0.138, oz + 0.0052))
    pts = [W(hw + 0.036, 0.060, 0.036), W(hw + 0.052, 0.055, 0.022), W(hw + 0.066, 0.035, 0.0035),
           (0.400, 0.190, oz + 0.0028), (0.448, 0.158, oz + 0.0028), (mx0 - 0.045, 0.140, oz + 0.0028),
           tuple(end - Vector((0.022, 0.0, 0.0)))]
    g.pipe(cb, spline([tuple(p) for p in pts], 3), 0.0028, 5)
    # jack plug at the end: body with knurling, steel pin toward the slot
    lathe(pg, [(0.0030, -0.022), (0.0052, -0.018), (0.0052, -0.004), (0.0042, 0.0)], 10, center=end, axis=(1, 0, 0))
    rod(st, end, end + Vector((0.010, 0.0, 0.0)), 0.0017, 8)
    return [st, pg, cb]
