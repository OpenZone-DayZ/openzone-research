"""RP-150Ts13 scale for M14, detailed: sizes and layout come from base B7 (kscale.py in the kit, which is
left unchanged because other models are built on it), the shape is here.

Compared with B7's platform_scale(): rounded cast shapes (lever box with a lid overhang and a plinth,
column with rounded edges on a bolted flange, head neck), the head drum with a rolled edge and a convex
rear cover on screws, the dial rim of rounded section on eight screws, a pointer with a counterweight
and an axis cap; wheels with tyres and hubs, adjustable front feet; an inspection door on hinges with a
latch, a blank nameplate on rivets, a handle for rolling at the back of the column; the arrester (the
platform stop lever) at the left of the box face - a bolt instead of the zero screw on the right
(build_bolt in m14_props).

Work look: the arrester is released (bone ozl_lever, rotation by 90 degrees), the pointer goes to the
weight (bone ozl_weigh: the axis cap) and breathes around it (bone ozl_needle - a child of ozl_weigh:
the pointer with a counterweight).
"""
import math

from mathutils import Vector

import kgeo as g
import kscale as ks
from m14_geo import bev, box_to, face, frame_axis, lathe, loft, rrect_prism, rrect_ring, spline

X0, X1, Y0, Y1 = ks.X0, ks.X1, ks.Y0, ks.Y1
HOUS = ks.HOUSING                                   # lever box x0 x1 y0 y1 z0 z1
COL = ks.COLUMN
HC = ks.HEAD_C
ZCAP = HOUS[5] + 0.008                              # top of the box lid (with the overhang)
COL_W, COL_R = 0.100, 0.016                         # column: section, edge radius
COL_CY = (COL[2] + COL[3]) / 2
COL_Z0, COL_Z1 = ZCAP + 0.020, COL[5]               # above the flange up to the neck
NEEDLE_YC = sum(ks.NEEDLE_Y) / 2
# arrester: axis on the box face at the left (mirrors the bolt in place of the zero screw), lever
# down-left; "work" - rotation by 90 degrees clockwise for the person (up-left)
LEVER_C = (-ks.ADJUST[0], HOUS[2], ks.ADJUST[2])
LEVER_LEN = 0.072
LEVER_DIR = Vector((-1.0, 0.0, -1.0)).normalized()
# rolling handle: at the back of the column
HANDLE_Z = 1.00


def head_frame(y=0.0):
    """Head frame: axis +Y (from the face to the back), u is +X, v is +Z."""
    return g.Frame((HC[0], y, HC[2]), (1, 0, 0), (0, 0, 1), (0, 1, 0))


def build_frame(P, spec):
    lod, sd = spec["lod"], spec["sides"]
    parts = []
    fr = P("sc_frame", "sc_frame")
    z0, z1 = ks.FRAME_Z
    if lod < 2:
        bv = bev(lod, 0.004, 1)
        g.box(fr, X0, X1, Y0, Y0 + ks.RAIL, z0, z1, **bv)
        for xa, xb in ((X0, X0 + ks.RAIL), (X1 - ks.RAIL, X1)):
            g.box(fr, xa, xb, Y0 + ks.RAIL - 0.004, HOUS[2] + 0.02, z0, z1, **bv)
        pan = P("sc_pan", "sc_inner")
        g.box(pan, X0 + ks.RAIL, X1 - ks.RAIL, Y0 + ks.RAIL, HOUS[2], z0, z1 - 0.004)
        parts.append(pan)
    else:
        g.box(fr, X0, X1, Y0, HOUS[2], 0.0, z1)
    parts.append(fr)
    if lod == 2:
        return parts
    # front feet: a threaded leg with a lock nut, a plate
    ft = P("sc_feet", "steel")
    for x in (X0 + 0.045, X1 - 0.045):
        c = (x, Y0 + 0.03, 0.0)
        if lod == 0:
            lathe(ft, [(0.0, 0.0), (0.024, 0.0), (0.024, 0.006), (0.0085, 0.0105), (0.0085, z0 + 0.001)], 10, frame=g.Frame(c, (1, 0, 0), (0, 1, 0), (0, 0, 1)), cap1=True)
            g.cyl(ft, (x, Y0 + 0.03, 0.0165), "z", 0.0135, 0.007, 6)
        else:
            g.cyl(ft, (x, Y0 + 0.03, z0 / 2), "z", 0.023, z0, 8)
    parts.append(ft)
    return parts


def build_wheels(P, spec):
    """Wheels at the back on the sides of the frame: a tyre of rounded section, a cast disc with a hub, a
    washer and a split pin at the end of the axle; the axle goes through the box."""
    lod = spec["lod"]
    parts = []
    wh = P("sc_wheels", "rubber")
    hub = P("sc_hubs", "sc_frame") if lod == 0 else None
    for s in (-1, 1):
        cx = s * (X1 + 0.003 + ks.WHEEL_W / 2)
        c = (cx, ks.WHEEL_Y, ks.WHEEL_R)
        if lod == 0:
            fr = g.Frame(c, (0, 1, 0), (0, 0, 1), (1, 0, 0))
            lathe(wh, [(0.036, -0.0125), (0.046, -0.0150), (0.0535, -0.0118), (0.0556, 0.0), (0.0535, 0.0118),
                       (0.046, 0.0150), (0.036, 0.0125)], 14, frame=fr, closed=True)
            # disc with a convex hub, washer, split pin
            lathe(hub, [(0.0, -0.0115), (0.0366, -0.0115), (0.0366, 0.0115), (0.020, 0.0125), (0.0165, 0.017),
                        (0.0165, 0.021), (0.0, 0.021)], 10, frame=g.Frame(c, (0, 1, 0), (0, 0, 1), (s, 0, 0)))
        else:
            g.cyl(wh, c, "x", ks.WHEEL_R, ks.WHEEL_W, (16, 10, 6)[lod])
    parts.append(wh)
    if hub is not None:
        parts.append(hub)
    if lod < 2:
        ax = P("sc_axle", "steel")
        g.cyl(ax, (0.0, ks.WHEEL_Y, ks.WHEEL_R), "x", 0.012, 0.733, (10, 6)[lod])
        if lod == 0:
            for s in (-1, 1):
                xe = s * 0.3565                                  # washer behind the hub, split pin at the axle end
                g.cyl(ax, (xe, ks.WHEEL_Y, ks.WHEEL_R), "x", 0.018, 0.003, 12)
                # split pin: a loop through the axle
                g.pipe(ax, [(xe + s * 0.005, ks.WHEEL_Y - 0.004, ks.WHEEL_R + 0.016),
                            (xe + s * 0.005, ks.WHEEL_Y - 0.008, ks.WHEEL_R + 0.006),
                            (xe + s * 0.005, ks.WHEEL_Y - 0.004, ks.WHEEL_R - 0.016),
                            (xe + s * 0.005, ks.WHEEL_Y + 0.004, ks.WHEEL_R - 0.024)], 0.0014, 4)
        parts.append(ax)
    return parts


def build_deck(P, spec):
    """Platform: a ribbed sheet (the "checker" pattern is in the deck material), rounded edges."""
    lod = spec["lod"]
    dk = P("sc_deck", "sc_deck")
    g.box(dk, *ks.DECK, **bev(lod, 0.006, 2))
    return [dk]


def build_housing(P, spec, sel_lever):
    """Lever box: plinth, body with rounded edges, lid with an overhang, inspection door on hinges,
    nameplate, arrester (the lever is bone sel_lever)."""
    lod = spec["lod"]
    hx0, hx1, hy0, hy1, hz0, hz1 = HOUS
    bd = P("sc_housing", "sc_body")
    parts = [bd]
    if lod == 2:
        g.box(bd, hx0, hx1, hy0, hy1, hz0, ZCAP)
        return parts
    if lod == 0:
        g.box(bd, hx0 - 0.008, hx1 + 0.008, hy0 - 0.008, hy1 + 0.004, 0.0, 0.022, r=0.004, seg=1)
        g.box(bd, hx0, hx1, hy0, hy1, 0.016, hz1 - 0.010, r=0.016, seg=2)
        g.box(bd, hx0 - 0.006, hx1 + 0.006, hy0 - 0.006, hy1 + 0.004, hz1 - 0.016, ZCAP, r=0.010, seg=2)
    else:
        g.box(bd, hx0, hx1, hy0, hy1, hz0, hz1 - 0.012)
        g.box(bd, hx0 - 0.006, hx1 + 0.006, hy0 - 0.006, hy1 + 0.004, hz1 - 0.016, ZCAP)
    # inspection door
    g.box(bd, -0.120, 0.060, hy0 - 0.004, hy0 + 0.003, 0.060, 0.170, **bev(lod, 0.003, 1))
    if lod == 0:
        hw = P("sc_hinges", "steel")
        for za, zb in ((0.074, 0.096), (0.134, 0.156)):
            g.cyl(hw, (-0.1235, hy0 - 0.0045, (za + zb) / 2), "z", 0.0048, zb - za, 10)
        # latch: a rotating wing knob on a washer
        g.cyl(hw, (0.044, hy0 - 0.006, 0.115), "y", 0.0085, 0.004, 12)
        g.box(hw, 0.0395, 0.0485, hy0 - 0.017, hy0 - 0.008, 0.103, 0.127, r=0.002, seg=1)
        parts.append(hw)
        # blank nameplate on two rivets
        pl = P("sc_plate", "plate")
        g.box(pl, -0.036, 0.036, hy0 - 0.0016, hy0 + 0.001, 0.236, 0.272, r=0.0015, seg=1)
        parts.append(pl)
        rv = P("sc_rivets", "steel")
        for x in (-0.030, 0.030):
            lathe(rv, [(0.0028, 0.0), (0.0018, 0.0013), (0.0, 0.0016)], 6,
                  frame=g.Frame((x, hy0 - 0.0015, 0.254), (1, 0, 0), (0, 0, 1), (0, -1, 0)))
        parts.append(rv)
    # arrester: a cast boss on the box face, a lever with a hub and a handle (bone)
    lx, ly, lz = LEVER_C
    g.cyl(bd, (lx, ly - 0.005, lz), "y", 0.018, 0.010, (16, 8)[lod])
    lv = P("sc_lever", "steel", group=sel_lever)
    yl = ly - 0.0135
    g.cyl(lv, (lx, ly - 0.0125, lz), "y", 0.0105, 0.006, (12, 6)[lod])
    tip = Vector((lx, yl, lz)) + LEVER_DIR * LEVER_LEN
    box_to(lv, (lx, yl, lz), tip, 0.012, 0.006, up=(0, -1, 0))
    parts.append(lv)
    kb = P("sc_lever_knob", "black", group=sel_lever)
    if lod == 0:
        lathe(kb, [(0.0, -0.003), (0.0075, 0.0), (0.0105, 0.009), (0.0095, 0.019), (0.006, 0.0245), (0.0, 0.026)], 12,
              frame=frame_axis(tip - LEVER_DIR * 0.004, LEVER_DIR, ref=(0, -1, 0)))
    else:
        g.pipe(kb, [tuple(tip - LEVER_DIR * 0.004), tuple(tip + LEVER_DIR * 0.02)], 0.0095, 6)
    parts.append(kb)
    return parts


def build_column(P, spec):
    """Column on a cast bolted flange, head neck, rod cover at the back, rolling handle."""
    lod, sd = spec["lod"], spec["sides"]
    cy = COL_CY
    cl = P("sc_column", "sc_body")
    parts = [cl]
    if lod == 0:
        rrect_prism(cl, 0.0, cy, COL_W, COL_W, COL_R, 4, COL_Z0 - 0.004, COL_Z1)
        loft(cl, [rrect_ring(0.0, cy, 0.150, 0.150, 0.020, 4, ZCAP - 0.002), rrect_ring(0.0, cy, 0.150, 0.150, 0.020, 4, ZCAP + 0.010),
                  rrect_ring(0.0, cy, 0.120, 0.120, 0.022, 4, ZCAP + 0.016), rrect_ring(0.0, cy, COL_W, COL_W, COL_R, 4, ZCAP + 0.026)],
             (0.0, cy, 0.0), caps=(False, False))
        # flange top (the ring between the outer edge and the column is covered by the loft slope); flange bolts
        bt = P("sc_flange_bolts", "steel")
        for sx in (-1, 1):
            for sy in (-1, 1):
                g.cyl(bt, (sx * 0.060, cy + sy * 0.060, ZCAP + 0.0125), "z", 0.0085, 0.006, 6)
        parts.append(bt)
    else:
        g.box(cl, -COL_W / 2, COL_W / 2, cy - COL_W / 2, cy + COL_W / 2, ZCAP - 0.002, COL_Z1)
        if lod == 1:
            g.box(cl, -0.075, 0.075, cy - 0.075, cy + 0.075, ZCAP - 0.002, ZCAP + 0.012)
    # neck: from the column to the bottom of the drum
    nk = [(0.051, COL_Z1 - 0.012), (0.047, COL_Z1 + 0.020), (0.051, COL_Z1 + 0.037), (0.067, COL_Z1 + 0.045),
          (0.062, COL_Z1 + 0.058), (0.050, COL_Z1 + 0.075)]
    if lod > 0:
        nk = [nk[0], nk[2], nk[3], nk[-1]]
    lathe(cl, nk, (20, 12, 8)[lod], frame=g.Frame((0.0, cy, 0.0), (1, 0, 0), (0, 1, 0), (0, 0, 1)))
    if lod == 2:
        return parts
    if lod == 0:
        # rod cover on the back of the column on four screws
        g.box(cl, -0.030, 0.030, cy + COL_W / 2 - 0.001, cy + COL_W / 2 + 0.003, 0.56, 0.94, r=0.002, seg=1)
        sw = P("sc_cover_screws", "steel")
        for z in (0.575, 0.925):
            for x in (-0.021, 0.021):
                lathe(sw, [(0.0034, 0.0), (0.0021, 0.0015), (0.0, 0.0018)], 6,
                      frame=g.Frame((x, cy + COL_W / 2 + 0.003, z), (1, 0, 0), (0, 0, 1), (0, 1, 0)))
        parts.append(sw)
    # rolling handle: a pipe bracket on two bosses
    hd = P("sc_handle", "sc_frame")
    yb = cy + COL_W / 2
    pts = [(-0.036, yb - 0.004, HANDLE_Z), (-0.036, yb + 0.050, HANDLE_Z), (-0.026, yb + 0.080, HANDLE_Z),
           (0.026, yb + 0.080, HANDLE_Z), (0.036, yb + 0.050, HANDLE_Z), (0.036, yb - 0.004, HANDLE_Z)]
    g.pipe(hd, spline(pts, 2) if lod == 0 else pts, 0.011, (7, 6)[lod])
    if lod == 0:
        for x in (-0.036, 0.036):
            g.cyl(hd, (x, yb + 0.003, HANDLE_Z), "y", 0.017, 0.008, 10)
    parts.append(hd)
    return parts


def build_head(P, spec, sel_weigh, sel_needle):
    """Head: a drum with a rolled edge and a convex rear cover, a rim of rounded section on screws, the
    scale, glass (near LOD), a pointer with a counterweight (bone sel_needle) and the axis cap (bone sel_weigh)."""
    lod = spec["lod"]
    hs = (40, 20, 12)[lod]
    parts = []
    hf = head_frame()
    bd = P("sc_head", "sc_body")
    drum = [(0.183, 0.2555), (0.1962, 0.2580), (0.1975, 0.2650), (0.1975, 0.3720), (0.1940, 0.3830), (0.1840, 0.3870),
            (0.1500, 0.3960), (0.0900, 0.4000), (0.0, 0.4015)]
    if lod > 0:
        drum = [drum[0], drum[2], drum[3], drum[4], drum[6], drum[-1]]
    lathe(bd, [(r, y) for r, y in drum], hs, frame=hf)
    parts.append(bd)
    if lod == 0:
        sw = P("sc_head_screws", "steel")
        for k in range(6):
            a = 2 * math.pi * (k + 0.5) / 6
            o = hf.p(0.163 * math.cos(a), 0.163 * math.sin(a), 0.3925)
            lathe(sw, [(0.0042, 0.0), (0.0030, 0.0015), (0.0, 0.0020)], 6,
                  frame=g.Frame(o, (1, 0, 0), (0, 0, 1), Vector((0.0, 0.94, 0.0)) + Vector((math.cos(a), 0, math.sin(a))) * 0.34))
        parts.append(sw)
    # dial rim
    ch = P("sc_ring", "chrome")
    if lod < 2:
        ring = [(0.1800, 0.2365), (0.1920, 0.2350), (0.2040, 0.2400), (0.2060, 0.2520), (0.2010, 0.2630),
                (0.1880, 0.2580), (0.1810, 0.2480)]
        if lod == 1:
            ring = [ring[0], ring[2], ring[4], ring[5]]
        lathe(ch, ring, hs, frame=hf, closed=True)
        if lod == 0:
            for k in range(8):
                a = 2 * math.pi * (k + 0.5) / 8
                o = hf.p(0.1935 * math.cos(a), 0.1935 * math.sin(a), 0.2353)
                lathe(ch, [(0.0046, 0.0), (0.0032, -0.0016), (0.0, -0.0022)], 6,
                      frame=g.Frame(o, (1, 0, 0), (0, 0, 1), (0, 1, 0)), side=-1)
    else:
        g.cyl(ch, (HC[0], (ks.RING_Y[0] + ks.DRUM_Y[0]) / 2, HC[2]), "y", ks.RING_R1, ks.DRUM_Y[0] - ks.RING_Y[0], hs)
    parts.append(ch)
    # scale, glass
    dl = P("sc_dial", "sc_dial")
    g.cyl(dl, (HC[0], (ks.DIAL_Y + 0.2565) / 2, HC[2]), "y", ks.DIAL_R, 0.2565 - ks.DIAL_Y, hs)
    parts.append(dl)
    if lod == 0:
        gl = P("sc_glass", "steel", section="glass")
        g.cyl(gl, (HC[0], ks.GLASS_Y, HC[2]), "y", 0.1806, 0.0012, hs)
        parts.append(gl)
    # pointer: up at zero; a blade to the tip, a disc counterweight, the axis cap
    y0, y1 = ks.NEEDLE_Y
    nd = P("sc_needle", "sc_needle", group=sel_needle)
    L = ks.NEEDLE_L
    if lod == 0:
        poly = [(-0.0046, -0.026), (-0.0036, 0.0), (-0.0016, 0.110), (-0.0007, 0.150), (0.0, L), (0.0007, 0.150),
                (0.0016, 0.110), (0.0036, 0.0), (0.0046, -0.026)]
    else:
        poly = [(-0.004, -0.026), (-0.0012, 0.12), (0.0, L), (0.0012, 0.12), (0.004, -0.026)]
    g.prism(nd, [(HC[0] + a, HC[2] + b) for a, b in poly], (0, 2), y0, y1)
    if lod < 2:
        g.cyl(nd, (HC[0], (y0 + y1) / 2, HC[2] - 0.034), "y", 0.0105, y1 - y0 + 0.0006, (16, 8)[lod])
    parts.append(nd)
    if lod < 2:
        cp = P("sc_needle_cap", "sc_needle", group=sel_weigh)
        # the system axis points to the person (-Y), from the pointer face: the cap stops 1 mm short of the glass
        lathe(cp, [(0.0, -0.0004), (0.0082, -0.0004), (0.0082, 0.0010), (0.0058, 0.0020), (0.0, 0.0024)], (12, 8)[lod],
              frame=g.Frame((HC[0], y0, HC[2]), (1, 0, 0), (0, 0, 1), (0, -1, 0)))
        parts.append(cp)
    return parts


def build_scale(P, spec, sel):
    """The whole scale; sel - bone names: lever, weigh, needle."""
    parts = build_frame(P, spec) + build_wheels(P, spec) + build_deck(P, spec)
    parts += build_housing(P, spec, sel["lever"]) + build_column(P, spec)
    parts += build_head(P, spec, sel["weigh"], sel["needle"])
    return parts
