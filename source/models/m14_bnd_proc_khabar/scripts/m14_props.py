"""Trim of the M14 scale: a tray with a heap of loot, weights, a loupe, a dosimeter on tape, a bolt
instead of the zero screw, a stool with a calculator, money and an ashtray, a "Chernomorka" pack on the
lever box.

Props and sizes:
- tray - an old baking tray 340 x 260 x 45 mm: flared walls, rounded corners, rolled rim;
- rag - a soft heap with folds (a smooth surface, not a cone); on it eight watches (case dia. 34 mm with a
  rim, dial, hands, lugs, crown; straps and bracelets lie along the rag), three gold chains (one hangs
  over the rim onto the platform), a signet ring with a black stone and a plain ring;
- weights GOST 7328 (2 kg, 1 kg, 500 g) - solids of revolution with chamfers, a neck and a head;
- 10x watchmaker's loupe: knurled body, lens;
- DRG-01T1 dosimeter (175 x 90 x 55 mm): rounded body, display window in a frame (the display is its own
  texture with frames, ozl_screen), three buttons, detector slits, screws; blue insulating tape - two
  bands of two turns around the column and the dosimeter, the tail came unstuck;
- M16 bolt instead of the zero screw: washer, nut, thread;
- stool 320 x 320 x 450: a seat of two boards with rounded edges, tapered legs, aprons, stretchers,
  nails; calculator 85 x 140 x 18: keys separately, display is its own texture with frames
  (ozl_screen_2), solar cell; bundles of 500, 200 and 100 UAH (notes 154 / 148 / 142 x 75 mm, NBU, and
  their design - uah.py; layers in disorder, rubber bands), a tin ashtray with a rolled edge, ash and
  cigarette butts.

Blender axes: X is width, Y is depth (face toward -Y), Z is up.
"""
import math
import random

from mathutils import Vector

import kgeo as g
import kscale as ks
import uah
from m14_geo import (bev, face, frame_z, frustum, hull2, lathe, loft, quad, ribbon, rrect, rrect_ring, spline, tilted,
                     tube_loop)
from m14_scale import COL_CY, COL_R, COL_W, ZCAP

ZD = ks.DECK[5]                                             # platform top
COL = ks.COLUMN

# --- tray (baking tray) and the heap on the rag -----------------------------------------------
TRAY = (-0.200, 0.140, -0.250, 0.010)                       # outer top: x0 x1 y0 y1
TRAY_C = ((TRAY[0] + TRAY[1]) / 2, (TRAY[2] + TRAY[3]) / 2)
TRAY_W, TRAY_D = TRAY[1] - TRAY[0], TRAY[3] - TRAY[2]
TRAY_H, TRAY_T, FLARE = 0.045, 0.0015, 0.008
ZB = ZD + TRAY_T                                            # inner bottom
MC = (-0.030, -0.118)                                       # heap centre
RX, RY, MH = 0.118, 0.096, 0.034                            # semi-axes and height of the rag heap
RAG_T = 0.0015
# watches: (dx, dy from the heap centre, rotation, face up, metal, strap / bracelet / none, dial)
WATCHES = [
    (0.000, 0.004, 0.40, True, "gold", "strap", "watch_face"),
    (0.034, 0.022, 2.10, True, "silver", "bracelet", "watch_face_dark"),
    (-0.033, 0.026, 1.25, True, "silver", "strap", "watch_face"),
    (0.046, -0.028, 2.75, True, "gold", "bracelet", "watch_face"),
    (-0.050, -0.020, 0.90, False, "silver", "strap", "watch_face"),
    (0.010, -0.048, 1.70, True, "silver", "strap", "watch_face_dark"),
    (-0.074, 0.022, 2.50, True, "gold", None, "watch_face"),
    (0.072, 0.008, 0.20, True, "silver", "strap", "watch_face"),
]
CASE = [(0.0, 0.0), (0.0150, 0.0), (0.0167, 0.0040), (0.0145, 0.0085),
        (0.0131, 0.0074)]                                   # watch case dia. 34: bottom, side, rim
CASE_R, CASE_H = 0.0167, 0.0085
CHAINS = [
    [(-0.060, 0.050), (-0.030, 0.035), (0.000, 0.030), (0.020, 0.000), (0.050, -0.010), (0.070, 0.030), (0.090, 0.040)],
    [(-0.085, -0.050), (-0.050, -0.040), (-0.020, -0.020), (0.000, -0.026), (0.030, -0.006), (0.060, -0.052)],
    [(-0.022, 0.070), (0.000, 0.052), (0.030, 0.062), (0.050, 0.046), (0.064, 0.062)],
]
CHAIN_R = 0.0010
HANG_X = MC[0] + 0.040                                      # the chain over the front rim
RINGS = [(0.024, 0.050, 0.3, True), (-0.020, -0.058, 1.1, False)]   # dx, dy, rotation, signet
# weights: (x, y, radius, body height); loupe
WEIGHTS = [(0.225, -0.300, 0.032, 0.080), (0.232, -0.185, 0.025, 0.064), (0.140, -0.330, 0.020, 0.050)]
LOUPE = (-0.245, -0.320)
# DRG-01T1 dosimeter on the column (facing forward), display, buttons, tape
DOS = (-0.045, 0.045, COL[2] - 0.055, COL[2], 0.820, 0.995)
LCD = (-0.031, 0.031, 0.948, 0.977)                         # x0 x1 z0 z1
LCD_Y = DOS[2] - 0.0005
TAPE_BANDS = [(0.866, 0.020, 0.030), (0.914, -0.018, 0.035)]  # height of the centre, slope in x and in y
# stool and what is on it
SX, SY, SW, SZ = 0.620, -0.120, 0.320, 0.450
SEAT_T, LEG, LEG_C = 0.025, 0.036, 0.120
CALC = (SX - 0.075, SY - 0.075, 6.0)                        # centre, rotation, degrees
CALC_W, CALC_L, CALC_T = 0.085, 0.140, 0.016
CALC_LCD = (-0.031, 0.031, 0.036, 0.056)                    # u0 u1 v0 v1
# bundles of hryvnias: name, centre, bottom above the seat, thickness, denomination (note size - uah.SIZE);
# the notes are large, so the bundles are spread slightly: they do not overlap each other and do not hang off the seat
CASH = [("cash0", (0.688, -0.040), 0.0, 0.016, 500), ("cash1", (0.700, -0.031), 0.0172, 0.012, 200),
        ("cash2", (0.536, -0.035), 0.0, 0.013, 100)]
ASH = (SX + 0.075, SY - 0.085)
# cigarette butts: (dx, dy, height above the bottom, heading, lift,
# paper length, filter length, bend) - from the burnt end
BUTTS = [(-0.024, 0.004, 0.0070, 20.0, 0.0, 0.010, 0.020, 0.0),
         (0.006, -0.010, 0.0074, -70.0, 17.0, 0.013, 0.021, 0.0),
         (0.010, 0.020, 0.0066, 150.0, 2.0, 0.006, 0.018, 35.0),
         (-0.014, -0.016, 0.0072, 80.0, 3.0, 0.004, 0.019, 0.0),
         (0.024, 0.006, 0.0064, 230.0, 0.0, 0.009, 0.020, 20.0)]
# "Chernomorka" pack on the lever box lid right of the column: centre, rotation
CIG_AT = (0.118, 0.318, 92.0)
CIGS = (r"dz\gear\medical\data\pack_of_cigs_cherno_co.paa", r"dz\gear\medical\data\pack_of_cigs.rvmat")
# pieces of the pack texture (fractions of the image: x0, x1, y0, y1 top to bottom; as in M16): face, side, end
CIGS_UV = {"front": (0.117, 0.462, 0.43, 1.0), "side": (0.885, 0.970, 0.60, 1.0), "end": (0.26, 0.45, 0.20, 0.30)}


# =============================================================================
# Heap surface
# =============================================================================
def heap_q(x, y):
    dx, dy = (x - MC[0]) / RX, (y - MC[1]) / RY
    th = math.atan2(dy, dx)
    edge = 1.0 + 0.07 * math.sin(3 * th + 0.6) + 0.05 * math.sin(5 * th + 2.1)
    return math.hypot(dx, dy) / edge, th


def heap_h(x, y):
    """Height of the rag above the tray bottom: a crumpled heap with radial folds and a lump at the side."""
    q, th = heap_q(x, y)
    if q >= 1.0:
        return 0.0
    base = MH * (0.5 + 0.5 * math.cos(math.pi * q ** 1.5))
    fold = 0.0032 * math.sin(7 * th + 9.0 * q + 0.8) * math.sin(math.pi * q)
    lump = 0.004 * math.exp(-((x - MC[0] - 0.03) ** 2 + (y - MC[1] + 0.02) ** 2) / 0.0006) * (1.0 - q)
    return base + fold + lump


def surf(x, y):
    return ZB + RAG_T + heap_h(x, y)


def surf_n(x, y):
    e = 0.002
    nx = -(surf(x + e, y) - surf(x - e, y)) / (2 * e)
    ny = -(surf(x, y + e) - surf(x, y - e)) / (2 * e)
    return Vector((nx, ny, 1.0)).normalized()


def watch_xy(i):
    return MC[0] + WATCHES[i][0], MC[1] + WATCHES[i][1]


def over(x, y, skip=-1):
    """Lift above the cases of neighbouring watches: straps and chains lie on top."""
    lift = 0.0
    for i in range(len(WATCHES)):
        if i == skip:
            continue
        wx, wy = watch_xy(i)
        d = math.hypot(x - wx, y - wy)
        k = min(1.0, max(0.0, (0.0265 - d) / 0.012))
        lift = max(lift, CASE_H * k * k * (3.0 - 2.0 * k))
    return lift


def watch_frame(i):
    w = WATCHES[i]
    x, y = watch_xy(i)
    n = surf_n(x, y)
    p = Vector((x, y, surf(x, y)))
    if w[3]:
        return tilted(p, n, w[2])
    return tilted(p + n * CASE_H, -n, w[2])                 # face down: the case bottom up


# =============================================================================
# Tray, rag, loot
# =============================================================================
def build_tray(P, spec):
    lod = spec["lod"]
    tr = P("tray", "tray")
    cx, cy = TRAY_C
    if lod == 2:
        g.box(tr, TRAY[0], TRAY[1], TRAY[2], TRAY[3], ZD, ZD + TRAY_H * 0.6)
        return [tr]
    seg = 4 if lod == 0 else 1
    t, z0, z1 = TRAY_T, ZD, ZD + TRAY_H
    w1, d1, r1 = TRAY_W, TRAY_D, 0.022
    w0, d0, r0 = w1 - 2 * FLARE, d1 - 2 * FLARE, 0.016
    loft(tr, [rrect_ring(cx, cy, w0, d0, r0, seg, z0), rrect_ring(cx, cy, w1, d1, r1, seg, z1)], (cx, cy, 0),
         caps=(True, False))
    loft(tr, [rrect_ring(cx, cy, w1 - 2 * t, d1 - 2 * t, r1 - t, seg, z1),
              rrect_ring(cx, cy, w0 - 2 * t, d0 - 2 * t, r0 - t, seg, z0 + t)], (cx, cy, 0), inward=True,
         caps=(False, True))
    # rolled rim
    rim = [(x, y, z1 + 0.0005) for x, y in rrect(cx, cy, w1 + 0.002, d1 + 0.002, r1 + 0.001, 4 if lod == 0 else 1)]
    tube_loop(tr, rim, 0.003, 5 if lod == 0 else 4)
    return [tr]


def build_rag(P, spec):
    """Rag as a heap: a polar grid over the heap_h surface, the edge lies on the tray bottom."""
    lod = spec["lod"]
    if lod == 2:
        return []
    rg = P("tray_rag", "rag")
    qs = [0.12, 0.28, 0.45, 0.62, 0.78, 0.91, 1.0] if lod == 0 else [0.3, 0.6, 0.85, 1.0]
    nth = 24 if lod == 0 else 12
    bm = rg.bm

    def pt(q, th):
        edge = 1.0 + 0.07 * math.sin(3 * th + 0.6) + 0.05 * math.sin(5 * th + 2.1)
        x, y = MC[0] + RX * q * edge * math.cos(th), MC[1] + RY * q * edge * math.sin(th)
        return bm.verts.new((x, y, surf(x, y) if q < 1.0 else ZB + RAG_T))
    center = bm.verts.new((MC[0], MC[1], surf(MC[0], MC[1])))
    rings = [[pt(q, 2 * math.pi * k / nth) for k in range(nth)] for q in qs]
    skirt = [bm.verts.new((v.co.x, v.co.y, ZB + 0.0002)) for v in rings[-1]]
    new = []
    for k in range(nth):
        k1 = (k + 1) % nth
        new.append(face(rg, [center, rings[0][k], rings[0][k1]], (0, 0, 1)))
        for i in range(len(rings) - 1):
            new.append(face(rg, [rings[i][k], rings[i][k1], rings[i + 1][k1], rings[i + 1][k]], (0, 0, 1)))
        out = Vector((rings[-1][k].co.x - MC[0], rings[-1][k].co.y - MC[1], 0.0))
        new.append(face(rg, [rings[-1][k], rings[-1][k1], skirt[k1], skirt[k]], out))
    bm.normal_update()
    rg.tag(new)
    return [rg]


def strap_path(i, f, s, L, kind, curl):
    """Strap or bracelet from the lugs over the rag: points and half-thicknesses (links for a bracelet). A
    strap is not straight: toward the end it curls sideways by `curl`
    radians (leather remembers the bend of the wrist)."""
    step = 0.0065 if kind == "bracelet" else 0.008
    n = max(3, int(round(L / step)))
    lug = f.p(0.0, s * 0.0185, 0.0040)
    pts, hts = [], []
    pa, pb = 0.0, s * 0.0185
    for k in range(n + 1):
        t = L * k / n
        if k:
            phi = curl * (t / L) ** 1.5
            pa += math.sin(phi) * L / n
            pb += s * math.cos(phi) * L / n
        q = f.p(pa, pb, 0.0)
        zs = surf(q.x, q.y) + over(q.x, q.y, i) + 0.0013
        if k == 0:
            q = lug
        else:
            b = min(1.0, t / 0.020)
            q = Vector((q.x, q.y, max(zs, (1 - b) * lug.z + b * zs)))
        pts.append(tuple(q))
        hts.append((0.0016 if k % 2 == 0 else 0.0009) if kind == "bracelet" else 0.0011)
    return pts, hts


def build_watches(P, spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = {}

    def part(reg):
        if reg not in parts:
            parts[reg] = P("loot_" + reg, reg)
        return parts[reg]
    rnd = random.Random(14)
    for i, w in enumerate(WATCHES):
        if lod == 1 and i % 2:
            continue
        f = watch_frame(i)
        metal = part(w[4])
        if lod == 1:
            g.cyl(metal, (0, 0, CASE_H / 2), "z", CASE_R, CASE_H, 8, frame=f)
            continue
        lathe(metal, CASE, 14, frame=f, phase=w[2])
        lathe(part(w[6]), [(0.0131, 0.0074), (0.0, 0.0074)], 14, frame=f, phase=w[2])
        hand = part("hand_light" if w[6] == "watch_face_dark" else "sc_needle")
        for L, wd in ((0.0070, 0.0011), (0.0105, 0.0008)):
            a = rnd.uniform(0.0, 2 * math.pi)
            hf = g.Frame(f.p(0, 0, 0.0076), f.u * math.cos(a) + f.v * math.sin(a), f.v * math.cos(a) - f.u * math.sin(a),
                         f.n)
            quad(hand, hf, -0.0015, L, -wd / 2, wd / 2, 0.0)
        for s in (-1, 1):                                           # lugs
            g.box(metal, -0.0092, 0.0092, *sorted((s * 0.0140, s * 0.0196)), 0.0020, 0.0058, frame=f)
        g.box(metal, 0.0158, 0.0192, -0.0016, 0.0016, 0.0030, 0.0058, frame=f)   # crown
        if w[5]:
            for s in (-1, 1):
                curl = rnd.uniform(0.35, 0.8) * rnd.choice((-1, 1))
                pts, hts = strap_path(i, f, s, 0.060 if s > 0 else 0.046, w[5], curl)
                ribbon(part("strap" if w[5] == "strap" else w[4]), pts, f.u, 0.0080 if w[5] == "strap" else 0.0075, hts)
    return list(parts.values())


def build_chains(P, spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    ch = P("loot_chains", "gold")
    r = CHAIN_R
    for cp in (CHAINS if lod == 0 else CHAINS[:1]):
        xy = [(MC[0] + dx, MC[1] + dy, 0.0) for dx, dy in cp]
        if lod == 0:
            xy = spline(xy, 2)
        g.pipe(ch, [(x, y, surf(x, y) + over(x, y) + r) for x, y, _ in xy], r, 4 if lod == 0 else 3)
    if lod == 0:
        # over the front rim onto the platform: along the rag, along
        # the bottom, along the wall, over the rolled rim, down
        hx = HANG_X
        p3 = [(x, y, surf(x, y) + over(x, y) + r) for x, y in ((hx - 0.020, MC[1] - 0.020), (hx - 0.012, MC[1] - 0.055),
                                                               (hx - 0.004, MC[1] - 0.085))]
        p3 += [(hx, -0.229, ZB + r), (hx + 0.001, -0.2412, ZB + 0.012), (hx + 0.002, -0.2453, ZB + 0.034),
               (hx + 0.002, -0.2500, ZD + 0.0502), (hx + 0.002, -0.2530, ZD + 0.0500), (hx + 0.003, -0.2556, ZD + 0.040),
               (hx + 0.003, -0.2562, ZD + 0.020), (hx + 0.005, -0.2600, ZD + 0.006), (hx + 0.008, -0.2660, ZD + r),
               (hx + 0.015, -0.2830, ZD + r), (hx + 0.032, -0.2980, ZD + r)]
        g.pipe(ch, spline(p3, 2), r, 4)
    return [ch]


def build_rings(P, spec):
    """Signet ring with a black stone and a plain ring on the rag."""
    if spec["lod"] > 0:
        return []
    gd = P("loot_rings", "gold")
    on = P("loot_onyx", "onyx")
    for dx, dy, yaw, signet in RINGS:
        x, y = MC[0] + dx, MC[1] + dy
        R, rt = (0.0098, 0.0017) if signet else (0.0090, 0.0012)
        f = tilted(Vector((x, y, surf(x, y) + over(x, y) + rt)), surf_n(x, y), yaw)
        lathe(gd, [(R + rt * math.cos(2 * math.pi * k / 5), rt * math.sin(2 * math.pi * k / 5)) for k in range(5)], 12,
              frame=f, closed=True)
        if signet:
            g.box(gd, R - 0.0004, R + 0.0026, -0.0056, 0.0056, -0.0024, 0.0024, frame=f)
            g.box(on, R + 0.0026, R + 0.0031, -0.0043, 0.0043, -0.0018, 0.0018, frame=f)
    return [gd, on]


# =============================================================================
# Weights, loupe
# =============================================================================
def weight_prof(r, h):
    """GOST 7328 class M2 weight: body chamfers, neck, head."""
    return [(0.0, 0.0), (r * 0.93, 0.0), (r, r * 0.07), (r, h - r * 0.10), (r * 0.90, h), (r * 0.42, h),
            (r * 0.37, h + r * 0.12), (r * 0.56, h + r * 0.30), (r * 0.62, h + r * 0.48), (r * 0.42, h + r * 0.70),
            (0.0, h + r * 0.79)]


def build_weights(P, spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    br = P("weights", "brass")
    for x, y, r, h in WEIGHTS:
        if lod == 0:
            lathe(br, weight_prof(r, h), 20 if r > 0.03 else 16, frame=g.Frame((x, y, ZD), (1, 0, 0), (0, 1, 0), (0, 0, 1)))
        else:
            g.cyl(br, (x, y, ZD + h / 2), "z", r, h, 8)
    lp = P("loupe", "loupe")
    fr = g.Frame((LOUPE[0], LOUPE[1], ZD), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    parts = [br, lp]
    if lod == 0:
        lathe(lp, [(0.0, 0.0), (0.0150, 0.0), (0.0170, 0.0020), (0.0160, 0.0042), (0.0170, 0.0064), (0.0160, 0.0086),
                   (0.0168, 0.0106), (0.0140, 0.0195), (0.0130, 0.0236), (0.0118, 0.0236)], 12, frame=fr)
        ln = P("loupe_lens", "lens")
        lathe(ln, [(0.0119, 0.0230), (0.0080, 0.0238), (0.0, 0.0242)], 12, frame=fr)
        parts.append(ln)
    else:
        g.cyl(lp, (LOUPE[0], LOUPE[1], ZD + 0.012), "z", 0.017, 0.024, 8, r2=0.013)
    return parts


# =============================================================================
# Dosimeter on tape, bolt
# =============================================================================
def build_dosimeter(P, spec, sel_screen):
    lod = spec["lod"]
    x0, x1, y0, y1, z0, z1 = DOS
    ds = P("dos_body", "dos")
    g.box(ds, x0, x1, y0, y1, z0, z1, **bev(lod, 0.008, 2))
    parts = [ds]
    lx0, lx1, lz0, lz1 = LCD
    sc = P("dos_lcd", "dos_dark", group=sel_screen, section="lcd")
    fr = g.Frame((0.0, LCD_Y, 0.0), (1, 0, 0), (0, 0, 1), (0, -1, 0))
    quad(sc, fr, lx0, lx1, lz0, lz1, 0.0)
    sc.glass_frame = (fr, lx0, lx1, lz0, lz1)
    parts.append(sc)
    if lod == 2:
        return parts
    dk = P("dos_bezel", "dos_dark")
    m, yb0, yb1 = 0.005, y0 - 0.0018, y0 + 0.001
    for a0, a1, b0, b1 in ((lx0 - m, lx1 + m, lz0 - m, lz0), (lx0 - m, lx1 + m, lz1, lz1 + m), (lx0 - m, lx0, lz0, lz1),
                           (lx1, lx1 + m, lz0, lz1)):
        g.box(dk, a0, a1, yb0, yb1, b0, b1)
    if lod == 0:
        for k in range(4):                                          # slits of the detector window
            zc = 0.831 + 0.005 * k
            g.box(dk, -0.024, 0.024, y0 - 0.0004, y0 + 0.001, zc - 0.0011, zc + 0.0011)
    parts.append(dk)
    kb = P("dos_keys", "dos_key")
    for xc in (-0.022, 0.0, 0.022):
        g.box(kb, xc - 0.0068, xc + 0.0068, y0 - 0.0026, y0 + 0.001, 0.9275, 0.9365, **bev(lod, 0.0015, 1))
    parts.append(kb)
    if lod == 0:
        sw = P("dos_screws", "steel")
        for xc in (-0.036, 0.036):
            for zc in (0.829, 0.986):
                lathe(sw, [(0.0024, 0.0), (0.0014, 0.0010), (0.0, 0.0012)], 6,
                      frame=g.Frame((xc, y0 - 0.0002, zc), (1, 0, 0), (0, 0, 1), (0, -1, 0)))
        parts.append(sw)
    return parts


def tape_circles(grow):
    """Corners the tape goes around: the front of the dosimeter, the front and back of the column."""
    x0, x1, y0 = DOS[0], DOS[1], DOS[2]
    cf, cb = COL_CY - COL_W / 2 + COL_R, COL_CY + COL_W / 2 - COL_R
    xc = COL_W / 2 - COL_R
    return [(x1 - 0.008, y0 + 0.008, 0.008 + grow), (x0 + 0.008, y0 + 0.008, 0.008 + grow),
            (xc, cf, COL_R + grow), (-xc, cf, COL_R + grow), (xc, cb, COL_R + grow), (-xc, cb, COL_R + grow)]


def build_tape(P, spec):
    """Blue insulating tape: two bands of two turns (the second shifted), the tail came unstuck."""
    lod = spec["lod"]
    if lod == 2:
        return []
    tp = P("dos_tape", "tape")
    wraps = ((0.0004, 0.0), (0.0011, 0.0026)) if lod == 0 else ((0.0006, 0.0),)
    for zc, tx, ty in TAPE_BANDS:
        for grow, dz in wraps:
            pts = [(x, y, zc + dz + tx * x + ty * (y - COL_CY)) for x, y in hull2(tape_circles(grow), 7 if lod == 0 else 5)]
            ribbon(tp, pts, (0, 0, 1), 0.0095, 0.00028, closed=True)
    if lod == 0:
        y0 = DOS[2]
        # the end of the lower band came unstuck and hangs
        tail = [(0.0360, y0 - 0.0010, 0.8600), (0.0364, y0 - 0.0013, 0.8520), (0.0370, y0 - 0.0026, 0.8440),
                (0.0374, y0 - 0.0046, 0.8385)]
        ribbon(tp, spline(tail, 2), (1, 0, 0), 0.0060, 0.00028)
    return [tp]


def build_bolt(P, spec):
    """M16 bolt instead of the zero screw: washer, nut, threaded end."""
    lod = spec["lod"]
    if lod == 2:
        return []
    x, y, z = ks.ADJUST
    bt = P("adjust_bolt", "bolt")
    fr = g.Frame((x, y, z), (1, 0, 0), (0, 0, 1), (0, -1, 0))           # c: box face -> person
    g.cyl(bt, (0, 0, 0.0015), "z", 0.0172, 0.003, (16, 8)[lod], frame=fr)
    g.cyl(bt, (0, 0, 0.0095), "z", 0.0139, 0.013, 6, frame=fr)
    if lod == 0:
        th = [(0.0080, 0.0150)]
        for k in range(4):
            th += [(0.0080, 0.0172 + 0.0028 * k), (0.0071, 0.0186 + 0.0028 * k)]
        th += [(0.0064, 0.0300), (0.0, 0.0303)]
        lathe(bt, th, 8, frame=fr)
    return [bt]


# =============================================================================
# Stool, calculator, money, ashtray
# =============================================================================
def build_stool(P, spec):
    lod = spec["lod"]
    h = SW / 2
    zs = SZ - SEAT_T
    st = P("stool_seat", "wood_x")
    if lod == 0:
        for ya, yb in ((SY - h, SY - 0.0015), (SY + 0.0015, SY + h)):
            g.box(st, SX - h, SX + h, ya, yb, zs, SZ, r=0.005, seg=2)
    else:
        g.box(st, SX - h, SX + h, SY - h, SY + h, zs, SZ)
    lg = P("stool_legs", "wood_z")
    parts = [st, lg]
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = SX + sx * LEG_C, SY + sy * LEG_C
            if lod == 0:
                loft(lg, [rrect_ring(cx, cy, 0.030, 0.030, 0.004, 2, 0.0), rrect_ring(cx, cy, LEG, LEG, 0.004, 2, zs)],
                     (cx, cy, 0), caps=(True, False))
            else:
                g.box(lg, cx - LEG / 2, cx + LEG / 2, cy - LEG / 2, cy + LEG / 2, 0.0, zs)
    if lod == 2:
        return parts
    ax, ay = P("stool_rails_x", "wood_x"), P("stool_rails_y", "wood_y")
    a = LEG_C - LEG / 2                                       # inner faces of the legs
    o = LEG_C + LEG / 2 - 0.003                               # outer face of the apron
    for s in (-1, 1):
        g.box(ax, SX - a, SX + a, *sorted((SY + s * o, SY + s * (o - 0.018))), zs - 0.068, zs, **bev(lod, 0.002, 1))
        g.box(ay, *sorted((SX + s * o, SX + s * (o - 0.018))), SY - a, SY + a, zs - 0.068, zs, **bev(lod, 0.002, 1))
        g.box(ay, SX + s * LEG_C - 0.009, SX + s * LEG_C + 0.009, SY - a, SY + a, 0.120, 0.146, **bev(lod, 0.002, 1))
    parts += [ax, ay]
    if lod == 0:
        g.box(ax, SX - LEG_C + 0.009, SX + LEG_C - 0.009, SY - 0.009, SY + 0.009, 0.124, 0.144, r=0.002, seg=1)
        nl = P("stool_nails", "nail")
        for nx, ny in ((LEG_C, LEG_C), (LEG_C, -LEG_C), (-LEG_C, LEG_C), (-LEG_C, -LEG_C), (0.0, o - 0.009),
                       (0.0, -(o - 0.009)), (o - 0.009, 0.06), (-(o - 0.009), -0.06)):
            g.cyl(nl, (SX + nx, SY + ny, SZ + 0.0003), "z", 0.0026, 0.0008, 6)
        parts.append(nl)
    return parts


def calc_frame():
    return frame_z(CALC[0], CALC[1], CALC[2], SZ)


def build_calc(P, spec, sel_screen2):
    """Calculator: body, frame and display (own texture with frames), solar cell, 25 keys."""
    lod = spec["lod"]
    if lod == 2:
        return []
    f = calc_frame()
    hw, hl, t = CALC_W / 2, CALC_L / 2, CALC_T
    bd = P("calc_body", "calc_body")
    g.box(bd, -hw, hw, -hl, hl, 0.0, t, frame=f, **bev(lod, 0.0035, 2))
    u0, u1, v0, v1 = CALC_LCD
    dk = P("calc_bezel", "calc_dark")
    g.box(dk, u0 - 0.004, u1 + 0.004, v0 - 0.004, v1 + 0.004, t - 0.0004, t + 0.0006, frame=f)
    lc = P("calc_lcd", "calc_dark", group=sel_screen2, section="calc")
    lf = g.Frame(f.p(0, 0, t + 0.0008), f.u, f.v, f.n)
    quad(lc, lf, u0, u1, v0, v1, 0.0)
    lc.glass_frame = (lf, u0, u1, v0, v1)
    parts = [bd, dk, lc]
    if lod == 1:
        return parts
    sl = P("calc_solar", "solar")
    g.box(sl, -0.020, 0.020, 0.0615, 0.0662, t - 0.0004, t + 0.0005, frame=f)
    parts.append(sl)
    keys = {}
    for r in range(5):
        for c in range(5):
            reg = "key_light" if r == 0 else ("key_orange" if (r, c) == (4, 4) else "key_dark")
            if reg not in keys:
                keys[reg] = P("calc_" + reg, reg)
            frustum(keys[reg], f, -0.0322 + 0.0161 * c, 0.0185 - 0.0186 * r, 0.0128, 0.0108, 0.0106, 0.0088,
                    t - 0.0002, t + 0.0024)
    return parts + list(keys.values())


def build_cash(P, spec):
    """Bundles of notes: layers slightly in disorder (the sides are a
    cut of paper), the top note is a decal, a rubber band."""
    lod = spec["lod"]
    if lod == 2:
        return []
    pe = P("cash_edges", "paper_edge")
    bd = P("cash_bands", "band") if lod == 0 else None
    parts = [pe]
    rnd = random.Random(7)
    for nm, (cx, cy), dz, th, den in (CASH if lod == 0 else CASH[::2]):
        hx, hy = uah.SIZE[den][0] / 2, uah.SIZE[den][1] / 2
        z0 = SZ + dz
        if lod == 0:
            for k in range(3):
                ox, oy = rnd.uniform(-0.0012, 0.0012), rnd.uniform(-0.0010, 0.0010)
                g.box(pe, cx - hx + ox, cx + hx + ox, cy - hy + oy, cy + hy + oy, z0 + th * k / 3,
                      z0 + th * (k + 1) / 3 - (0.0004 if k == 2 else 0.0))
        else:
            g.box(pe, cx - hx, cx + hx, cy - hy, cy + hy, z0, z0 + th - 0.0004)
        tp = P(nm, nm)
        g.box(tp, cx - hx, cx + hx, cy - hy, cy + hy, z0 + th - 0.0006, z0 + th)
        parts.append(tp)
        if bd is not None:
            xb = cx - 0.026
            loop = [(xb, y, z) for y, z in rrect(cy, z0 + th / 2, 2 * hy + 0.0016, th + 0.0014, 0.0015, 1)]
            ribbon(bd, loop, (1, 0, 0), 0.0028, 0.0004, closed=True)
    if bd is not None:
        parts.append(bd)
    return parts


def build_ashtray(P, spec):
    """Tin ashtray with a rolled edge, lumps of ash, cigarette butts (filter, paper, burnt end)."""
    lod = spec["lod"]
    if lod == 2:
        return []
    ax, ay = ASH
    fr = g.Frame((ax, ay, SZ), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    at = P("ashtray", "ashtray")
    prof = [(0.0, 0.0), (0.040, 0.0), (0.047, 0.0020), (0.0530, 0.0130), (0.0560, 0.0205), (0.0560, 0.0234),
            (0.0536, 0.0226), (0.0505, 0.0150), (0.0430, 0.0040), (0.0385, 0.0026), (0.0, 0.0026)]
    if lod == 1:
        prof = [prof[0], prof[1], prof[4], prof[7], prof[9], prof[10]]
    lathe(at, prof, 16 if lod == 0 else 10, frame=fr)
    parts = [at]
    if lod == 1:
        return parts
    ah = P("ash", "ash")
    lathe(ah, [(0.0, 0.0072), (0.012, 0.0067), (0.024, 0.0058), (0.033, 0.0047), (0.0392, 0.0030)], 16, frame=fr,
          side=-1, jitter=0.0007, seed=5)
    parts.append(ah)
    fl, pp, bn = P("butts_filter", "butt_filter"), P("butts_paper", "butt_paper"), P("butts_burnt", "ash_dark")
    for dx, dy, z, yaw, pitch, lp, lf, kink in BUTTS:
        a, b = math.radians(yaw), math.radians(pitch)
        d = Vector((math.cos(a) * math.cos(b), math.sin(a) * math.cos(b), math.sin(b)))
        p0 = Vector((ax + dx, ay + dy, SZ + z + 0.0038))
        p1 = p0 + d * lp
        k = math.radians(kink)
        d2 = Vector((math.cos(a + k) * math.cos(b), math.sin(a + k) * math.cos(b), math.sin(b)))
        p2 = p1 + d2 * lf
        g.pipe(bn, [tuple(p0 - d * 0.0012), tuple(p0 + d * 0.0004)], 0.0034, 6)
        g.pipe(pp, [tuple(p0), tuple(p1 + d * 0.0006)], 0.0038, 6)
        g.pipe(fl, [tuple(p1), tuple(p2)], 0.0039, 6)
    return parts + [fl, pp, bn]


def cig_pack(part, fr, L=0.088, W=0.055, H=0.022):
    """A "Chernomorka" pack lying face up in frame fr (u along the pack, v across, n up): each face has its
    UV on its own piece of the vanilla texture (CIGS_UV); the top of the face picture is toward +u. From M16."""
    bm = part.bm
    uvl = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    hl, hw = L / 2, W / 2
    sides = [
        ([(a, b, H) for a, b in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))], (0, 0, 1), "front",
         lambda a, b, c: ((hw - b) / W, (a + hl) / L)),
        ([(a, b, 0.0) for a, b in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))], (0, 0, -1), "front",
         lambda a, b, c: ((b + hw) / W, (a + hl) / L)),
        ([(a, -hw, c) for a, c in ((-hl, 0.0), (hl, 0.0), (hl, H), (-hl, H))], (0, -1, 0), "side",
         lambda a, b, c: (c / H, (a + hl) / L)),
        ([(a, hw, c) for a, c in ((-hl, 0.0), (hl, 0.0), (hl, H), (-hl, H))], (0, 1, 0), "side",
         lambda a, b, c: (1.0 - c / H, (a + hl) / L)),
        ([(-hl, b, c) for b, c in ((-hw, 0.0), (hw, 0.0), (hw, H), (-hw, H))], (-1, 0, 0), "end",
         lambda a, b, c: ((b + hw) / W, c / H)),
        ([(hl, b, c) for b, c in ((-hw, 0.0), (hw, 0.0), (hw, H), (-hw, H))], (1, 0, 0), "end",
         lambda a, b, c: ((hw - b) / W, c / H)),
    ]
    new = []
    for corners, nrm, rect, st in sides:
        vs = [bm.verts.new(fr.p(*q)) for q in corners]
        loc = {v: q for v, q in zip(vs, corners)}
        f = face(part, vs, fr.u * nrm[0] + fr.v * nrm[1] + fr.n * nrm[2])
        x0, x1, y0, y1 = CIGS_UV[rect]
        for lp in f.loops:
            s, t = st(*loc[lp.vert])
            lp[uvl].uv = (x0 + (x1 - x0) * s, 1.0 - (y1 - (y1 - y0) * t))
        new.append(f)
    part.tag(new)


def build_cigs(P, spec):
    if spec["lod"] > 0:
        return []
    pk = P("cig_pack", "carton", section="cigs")
    pk.fixed_uv = True
    cig_pack(pk, frame_z(CIG_AT[0], CIG_AT[1], CIG_AT[2], ZCAP))
    return [pk]
