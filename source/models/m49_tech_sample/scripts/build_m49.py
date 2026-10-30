"""M49 - Technical sample (OZL_Sample_17): a sample of the Electronics line shared by all factions. A
silvery antistatic bag with a circuit board and chips inside and a paper tag stapled to the weld of the
bag. A portable 1x2 item.

    blender --background --python build_m49.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py with the system Python first (the board on both sides, the chip tops, the tag, the
film texture bag_ca.png). The preview without baking is `-- --look`.

Target: about 10 x 15 x 1 cm (the real bag); a translucent silvery film (the green board shows), a
welded seam at the top, crumpled folds, a tag without text with an orange stripe (the Electronics line);
200-800 triangles, texture 512, 60-300 g.

Prototype and sizes:
- bag: a metallised shielding bag, 3M SCC 1000 Static Shielding Bag, 4 x 6" (101.6 x 152.4 mm inside),
  film 2.8-3 mil (0.07 mm). The side seams and the bottom are 4 mm welds; the neck is sealed across with
  a 6 mm weld 10 mm below the edge (how a sample is sealed), above it is the open edge.
- board: a half-size Eurocard, 100 x 80 x 1.6 mm, with an edge connector on gold-plated contacts along
  the short edge (like ISA boards). DIP packages per JEDEC MS-001 (pitch 2.54 mm, rows 7.62 and 15.24
  mm; DIP-14/16 19 x 6.4 mm, DIP-40 52.3 x 13.7 mm, height 4.2-4.4 mm; standoff under the body A1 >=
  0.38, lead b2 = 1.52 at the body, b = 0.46 mm at the board); a ROM in a ceramic DIP-24 32 x 15.2 mm
  with a quartz window (like K573RF2 / 2716); an HC-49/U crystal 11.05 x 4.65 x 13.46 mm lying down;
  axial electrolytic capacitors D 6.3 x 13 mm lying down (like K50-6). Leads under the board 1.5 mm. The
  bag over the board is 10 mm thick.
- tag: manila 46 x 28 mm, nailed to the weld with one 24/6 staple (crown 12 mm, wire ~0.5 mm, legs
  clinched on the back).
- mass 60 g, as OZL_Sample_Base in the mod (board ~50 g, bag and tag); the mass in Geometry is the same.

State is 'used but intact': the film has folds, fingerprints, scratches and dust at the seams, the neck
corner is dog-eared, the back of the board has a jumper wire (a repair) and rosin. No faction colour
(the sample is shared). Signs: an ESD mark on the film (a hand in a triangle with an arc), a tag with an
orange stripe, a hand-written number in digits, bars instead of lines.

Design decisions:
- 'dayz' look (kmodel look="dayz", the rvmat comes from the profile). The parts lie in a sealed bag: no
  dust on them, fewer streaks (the profile is tuned for this model: kmats.LOOK streaks 0.15 instead of
  0.50), dirt in the crevices.
- the film is a soft shell: its grid nodes form a membrane stretched between the seams and lying on the
  parts with sag (an obstacle problem: h = max(floor, neighbour mean - sag)). The grid lines run along
  the edges of the part rows, with an extra line at the side seams for a smooth descent. A node is never
  lower than the parts in the neighbouring cells, so the triangles do not cut the chips and the film is
  stretched over them like the real thing.
- the film wear is in its texture: the generator takes bag_ca.png (make_decals.py) and adds dirt at the
  seams, rubbed spots, scratches and specks (film_wear, numpy); the same PNG goes to the game. The
  highlight is more matte than the kit glass (own rvmat film_rvmat: SMDI G 0.30, B 0.51 instead of 1 /
  1).
- the own texture replaces the shared kexport.glass_ca: the ESD mark, the seams and the weld ribbing
  (make_decals.py) and the wear (film_wear); the front is on the right, the back on the left (UV:
  glass_frame). Atlas 1024 (at 512 the 80 x 100 mm board drawing and the chip tops blurred); the film is
  the glass section _ca 1024 (the 512 make_decals drawing is scaled up, the wear is drawn at 1024).
- DIP packages: double draft towards the parting line, top chamfers, a gap above the board; the 154 pins
  are blades (1.52 mm at the body, 0.46 mm at the board) with feet on the pads of the drawing; the
  ceramic ROM has a dark stripe of glass seal and a convex quartz window. The crystal is a flat can with
  a 'stadium' section and a rounded end, a base flange and two leads; the capacitors are bodies of
  revolution (a crimp at the plus end, a rubber plug, a minus stripe) with leads bent to the pads. The
  board is FR4 with edges of their own colour and a key notch of the contacts (a cutout, as in the
  drawing). The tag has rounded corners and its bottom is bent away from the film; the staple is wire
  with clinched legs on the back.
- no vanilla proxies (a 1x2 inventory item, nothing to put on it) and no work view (a sample is not a
  station and has no OZL_Work states).

LODs (small item): near 1490 triangles (of 1500), mid 538 (36 %: the film on a coarse grid, no pins,
staple, crystal flange or capacitor leads), no far LOD.

Blender axes: X is width, Z is height, Y is thickness (the front faces -Y). The bag STANDS and the
origin is the bag centre: the frame of the vanilla paper sheet (Paper.p3d: the sheet lies in the X-Y
plane of the engine, the origin is at the centre, Geometry is +-4 mm in Z); rotationFlags = 16 in the
config makes it lie down on the ground, as with Paper. The inventory camera (invView) is front-left at
45 degrees: a 1x2 cell is twice as tall as it is wide and the preview fits the item by height, while the
10 x 15 bag is wider than half its height, so at an angle it fits. The Blender preview shows the bag
lying face up (look_back - face down): the ground, the sun and the camera are rotated, not the model
(Model.laid), so the procedural materials in --look are the same as when baking the standing model.
"""
import math
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kbake  # noqa: E402
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import krender  # noqa: E402
import m49_layout as L  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

HX, HZ = L.HX, L.HZ
SEAM = L.SIDE_SEAM
CLEAR_F, CLEAR_B = 0.0004, 0.0003      # film clearance above the parts and above the leads
FREE_MIN = 0.0003                      # empty bag: a layer no closer to the middle (the layers do not meet)
SEAL_Y = 0.00012                       # weld: two film layers
TAG_T = 0.0003                         # tag thickness
EPS = 1e-6
PCB_TOP = L.pcb_z(100.0)


def wdecal(name):
    return os.path.join(WORK, name)


def bx(x_mm):
    return L.pcb_x(x_mm)


def bz(z_mm):
    return L.pcb_z(z_mm)


def at(x_mm, h_mm, w_mm, zc):
    """Part point on the board: x in board mm, h in mm above the board face (towards -Y), w in mm across
    the row from the axis zc (m, model z).
    """
    return Vector((x_mm / 1000.0, L.PCB_Y0 - h_mm / 1000.0, zc + w_mm / 1000.0))


# --- parts on the board: sizes missing from m49_layout ------------------------------------------
# DIP (JEDEC MS-001): standoff under the body; the mould parting line is at 0.42 of the body height
# above the standoff
STANDOFF = {"dip": 0.5, "eprom": 0.4}
PIN_TOP, PIN_FOOT = 0.76, 0.23         # half-width of a lead at the body and at the board, mm
WIN_X, WIN_R, WIN_H = 2.0, 4.0, 0.2    # ROM window: offset from the centre, radius, height, mm (as in decal_chips)
# HC-49/U crystal lying down: 'stadium' section 11.05 x 4.65 (radius 2.325, straight part 2 x 3.175)
XT_R, XT_C, XT_YC = 2.325, 3.175, 2.35
XT_FL = 0.6                            # base flange along the axis, mm
XT_PAD = 19.65                         # lead pads (board drawing: axial_pads), mm
# K50-6 lying down: the axis is 0.2 mm above the board; body profile along the axis from the minus end:
# (r, x from the end)
CAP_LIFT = 0.2
CAP_R = 3.15
CAP_AXIS = CAP_R + CAP_LIFT
CAP_PROF = [(2.45, 0.0), (3.10, 0.5), (3.15, 10.9), (2.86, 11.45), (3.15, 12.0), (2.90, 12.7), (2.30, 13.0)]
CAP_PAD = 2.6                          # the lead runs to the pad beyond the end, mm
KEY_D = 5.5                            # depth of the key notch of the contacts, mm (as in the drawing)


def dip_shape(part):
    """DIP body: half-width, standoff, parting-line height, half-span of the legs at the board (mm)."""
    kind, cx, cz, lx, wz, h, n = part
    W = wz / 2
    s0 = STANDOFF[kind]
    hp = s0 + (h - s0) * 0.42
    zf = max(L.row_spacing(n) / 2, W + 0.45)
    return W, s0, hp, zf


def dip_profile(kind, W, h, s0, hp, simple=False):
    """Body section across the row (w, h), mm, counter-clockwise: the bottom towards the board is not
    built. Epoxy: double draft towards the parting line and a top chamfer; ceramic: almost straight
    sides; simple is the mid LOD.
    """
    if simple:
        right = [(W - 0.1, s0), (W, h - 0.3), (W - 0.35, h)]
    elif kind == "eprom":
        right = [(W - 0.06, s0), (W, hp), (W - 0.06, h - 0.30), (W - 0.32, h)]
    else:
        right = [(W - 0.14, s0), (W, hp), (W - 0.16, h - 0.32), (W - 0.42, h)]
    return right + [(-w, hh) for w, hh in reversed(right)]


def pin_xs(part):
    """x of the DIP leads (mm) - the same as the pads of the board drawing (make_decals.pins)."""
    kind, cx, cz, lx, wz, h, n = part
    half = n // 2
    x0 = cx - (half - 1) * 2.54 / 2
    return [x0 + i * 2.54 for i in range(half)]


# --- what is under the film: (x0, x1, z0, z1, height to the front, height to the back or None) ---
BOXES = [(bx(-40), bx(40), L.PCB_Z0, PCB_TOP, -L.PCB_Y0, L.PCB_Y0 + L.PCB_T + L.LEADS)]
for _p in L.PARTS:
    _k, _cx, _cz, _lx, _wz, _h, _n = _p
    if _k in ("dip", "eprom"):
        _W, _s0, _hp, _zf = dip_shape(_p)
        _top = _h + (WIN_H if _k == "eprom" else 0.0)
        BOXES.append((bx(_cx - _lx / 2), bx(_cx + _lx / 2), bz(_cz - _zf - 0.3), bz(_cz + _zf + 0.3),
                      _top / 1000.0 - L.PCB_Y0, None))
    elif _k == "cap":
        BOXES.append((bx(_cx - _lx / 2), bx(_cx + _lx / 2), bz(_cz - _wz / 2), bz(_cz + _wz / 2),
                      (2 * CAP_R + CAP_LIFT) / 1000.0 - L.PCB_Y0, None))
        BOXES.append((bx(_cx - _lx / 2 - CAP_PAD - 0.4), bx(_cx + _lx / 2 + CAP_PAD + 0.4), bz(_cz - 0.6),
                      bz(_cz + 0.6), (CAP_AXIS + 0.4) / 1000.0 - L.PCB_Y0, None))
    else:                                                          # crystal and its leads
        BOXES.append((bx(_cx - _lx / 2), bx(_cx + _lx / 2), bz(_cz - _wz / 2 - 0.3), bz(_cz + _wz / 2 + 0.3),
                      (_h + 0.3) / 1000.0 - L.PCB_Y0, None))
        BOXES.append((bx(XT_PAD - 0.5), bx(_cx - _lx / 2), bz(_cz - 2.8), bz(_cz + 2.8),
                      (XT_YC + 0.4) / 1000.0 - L.PCB_Y0, None))


def vnoise(x, z, cell, seed):
    """Smooth noise 0..1 over the nodes of the cell lattice (the same for all LODs)."""
    def h(i, j):
        return (math.sin(i * 127.1 + j * 311.7 + seed * 74.7) * 43758.5453) % 1.0
    gx, gz = x / cell, z / cell
    i, j = math.floor(gx), math.floor(gz)
    fx, fz = gx - i, gz - j
    fx, fz = fx * fx * (3 - 2 * fx), fz * fz * (3 - 2 * fz)
    a = h(i, j) + (h(i + 1, j) - h(i, j)) * fx
    b = h(i, j + 1) + (h(i + 1, j + 1) - h(i, j + 1)) * fx
    return a + (b - a) * fz


def line_dist(x, z, line):
    """Signed distance from a point to the line (+ is the counter-clockwise side of the direction)."""
    (x0, z0), (x1, z1) = line
    dx, dz = x1 - x0, z1 - z0
    n = math.hypot(dx, dz)
    return ((x - x0) * dz - (z - z0) * dx) / n * -1.0


# film sag (1/m, membrane Laplacian): the front is on top when the bag lies; the back lies on the ground
SAG = {True: 30.0, False: 8.0}


def under_tag(x, z, margin=0.002):
    """Model point (x, z) is under the tag (with margin)."""
    phi = math.radians(L.TAG_ROT)
    dx, dz = x - L.TAG_PIN[0], z - L.TAG_PIN[1]
    s = dx * math.cos(phi) + dz * math.sin(phi)
    t = -dx * math.sin(phi) + dz * math.cos(phi)
    return abs(s) <= L.TAG_W / 2 + margin and -(L.TAG_H - L.TAG_TOP) - margin <= t <= L.TAG_TOP + margin


def film_y(xs, zs, front):
    """Y of the film nodes of the front (front) or the back: grid xs x zs -> [[y]]. The edges, seams,
    weld and neck are fixed; inside the pocket it is a membrane: h = max(floor, neighbour mean - sag),
    the floor not lower than the parts in the neighbouring cells (the triangles of a cell lie between
    its nodes, so above the parts).
    """
    n, m = len(xs), len(zs)
    seed = 1.0 if front else 2.0
    clear = CLEAR_F if front else CLEAR_B
    fixed, req = {}, {}
    for i, x in enumerate(xs):
        for j, z in enumerate(zs):
            nz = vnoise(x, z, 0.011, seed)
            if abs(x) >= HX - EPS or z <= -HZ + EPS:
                fixed[i, j] = 0.0                                  # edge: the layers are welded
            elif z >= HZ - EPS:
                fixed[i, j] = 0.0004 + 0.0004 * nz                 # open edge of the neck
            elif (abs(x) >= HX - SEAM - EPS or z <= -HZ + SEAM + EPS
                  or L.SEAL_Z0 - EPS <= z <= L.SEAL_Z1 + EPS):
                fixed[i, j] = SEAL_Y
            elif z > L.SEAL_Z1:
                fixed[i, j] = 0.0003 + 0.0008 * nz                 # neck above the weld
            else:
                xa, xb, za, zb = xs[i - 1], xs[i + 1], zs[j - 1], zs[j + 1]
                need = [b[4] if front else b[5] for b in BOXES
                        if b[0] < xb - EPS and b[1] > xa + EPS and b[2] < zb - EPS and b[3] > za + EPS]
                need = [v for v in need if v is not None]
                req[i, j] = max(need) + clear if need else FREE_MIN
    h = dict(fixed)
    h.update(req)
    k = SAG[front]
    coef = {}
    for (i, j) in req:
        dl, dr = xs[i] - xs[i - 1], xs[i + 1] - xs[i]
        dd, du = zs[j] - zs[j - 1], zs[j + 1] - zs[j]
        w = (2 / (dl * (dl + dr)), 2 / (dr * (dl + dr)), 2 / (dd * (dd + du)), 2 / (du * (dd + du)))
        coef[i, j] = w + (sum(w),)
    for _ in range(800):                                           # Gauss-Seidel
        for (i, j), lo in req.items():
            a, b, c, d, s = coef[i, j]
            v = (a * h[i - 1, j] + b * h[i + 1, j] + c * h[i, j - 1] + d * h[i, j + 1] - k) / s
            h[i, j] = v if v > lo else lo
    out = [[0.0] * m for _ in range(n)]
    sgn = -1.0 if front else 1.0
    for i, x in enumerate(xs):
        for j, z in enumerate(zs):
            hh = h[i, j]
            # crumpled film: only upwards from the floor; not crumpled under the tag - it is not visible
            # there and the tag lies flatter
            if (i, j) in req and not (front and under_tag(x, z)):
                taut = req[i, j] > 0.001
                hh += (0.00035 if taut else (0.0008 if front else 0.0005)) * vnoise(x, z, 0.011, seed)
                if front and not taut:                             # fold across the empty space
                    d = abs(line_dist(x, z, L.CREASE))
                    hh += 0.0013 * max(0.0, 1.0 - d / 0.007)
            y = sgn * hh
            d = line_dist(x, z, L.DOGEAR)                          # dog-eared corner - both layers
            if d > 0:
                y -= 0.35 * d
            out[i][j] = y
    return out


def film_front_at(xs, zs, ys, x, z):
    """Film y at point (x, z): a cell is two triangles and which diagonal the triangulation will cut is
    not known beforehand, so the more protruding of the two cuts (the smaller y) is taken.
    """
    def cell(vals, v):
        for k in range(len(vals) - 1):
            if vals[k] - EPS <= v <= vals[k + 1] + EPS:
                return k
        return 0 if v < vals[0] else len(vals) - 2
    i, j = cell(xs, x), cell(zs, z)
    fx = min(max((x - xs[i]) / (xs[i + 1] - xs[i]), 0.0), 1.0)
    fz = min(max((z - zs[j]) / (zs[j + 1] - zs[j]), 0.0), 1.0)
    y00, y10, y11, y01 = ys[i][j], ys[i + 1][j], ys[i + 1][j + 1], ys[i][j + 1]
    a = y00 + fx * (y10 - y00) + fz * (y11 - y10) if fx >= fz else y00 + fz * (y01 - y00) + fx * (y11 - y01)
    b = (y00 + fx * (y10 - y00) + fz * (y01 - y00) if fx + fz <= 1.0
         else y11 + (1.0 - fx) * (y01 - y11) + (1.0 - fz) * (y10 - y11))
    return min(a, b)


# film grids per LOD: z lines run along the edges of the part rows (the film descends between the rows),
# an extra line at the side seams for a smooth descent to the seam
X_OUT0, X_OUT1 = [-HX, -HX + SEAM, -0.0434], [0.0434, HX - SEAM, HX]
Z_BOT, Z_TOP = [-HZ, -HZ + SEAM], [L.SEAL_Z0, L.SEAL_Z1, HZ]
GRIDS = {
    0: dict(front=(X_OUT0 + [-0.040, -0.0267, -0.0133, 0.0, 0.0133, 0.0267, 0.040] + X_OUT1,
                   Z_BOT + [bz(v) for v in (0.0, 16.8, 23.2, 31.15, 44.85, 65.6, 73.8, 80.2, 94.15, 100.0)]
                   + [0.0385, 0.048] + Z_TOP),
            back=(X_OUT0 + [-0.040, 0.040] + X_OUT1,
                  Z_BOT + [L.PCB_Z0, PCB_TOP, 0.044] + Z_TOP)),
    1: dict(front=([-HX, -HX + SEAM, -0.040, -0.0133, 0.0133, 0.040, HX - SEAM, HX],
                   Z_BOT + [bz(v) for v in (0.0, 16.8, 44.85, 73.8, 94.15, 100.0)] + [0.044] + Z_TOP),
            back=([-HX, -HX + SEAM, -0.040, 0.040, HX - SEAM, HX],
                  Z_BOT + [L.PCB_Z0, PCB_TOP] + Z_TOP)),
}
FILM = {lod: {side: (xs, zs, film_y(xs, zs, side == "front")) for side, (xs, zs) in gr.items()}
        for lod, gr in GRIDS.items()}


# --- tag: a plane no closer than the front film of its LOD --------------------------------------
TAG_RC = 0.0016                        # tag corner radius
TAG_CURL = 0.00045                     # the bottom of the tag is bent away from the film


def tag_frame(lod):
    """The tag hangs from the staple and rests on the film: the top is at the weld, the tilt along the
    tag keeps the bottom from going under the film, the roll across was found by search: the smallest
    average gap under the tag (the film under it is uneven: the board capacitor and a fold at the bottom
    left). One per LOD (the mid LOD film is coarser); the x-z footprint is the same.
    """
    phi = math.radians(L.TAG_ROT)
    u0 = Vector((math.cos(phi), 0.0, math.sin(phi)))
    v0 = Vector((-math.sin(phi), 0.0, math.cos(phi)))
    pin = Vector((L.TAG_PIN[0], 0.0, L.TAG_PIN[1]))
    clr = 0.00025                                                  # the film height is exact (film_front_at)
    samples = []
    for a in range(11):
        for b in range(11):
            s = -L.TAG_W / 2 + L.TAG_W * a / 10
            t = -(L.TAG_H - L.TAG_TOP) + L.TAG_H * b / 10
            q = pin + u0 * s + v0 * t
            samples.append((s, t, film_front_at(*FILM[lod]["front"], q.x, q.z) - clr))
    xs, zs, ys = FILM[lod]["front"]
    for i, x in enumerate(xs):                                     # and the film nodes under the tag
        for j, z in enumerate(zs):
            if under_tag(x, z, 0.0):
                d = Vector((x, 0.0, z)) - pin
                samples.append((d.dot(u0), d.dot(v0), ys[i][j] - clr))
    best = None
    for kb in range(-14, 15):                                      # roll: y per metre across the tag
        sb = kb * 0.01
        y_top = min(f - s * sb for s, t, f in samples if t >= -0.004)
        sa = max([0.03] + [(y_top + s * sb - f) / -t for s, t, f in samples if t < -0.004])
        y_top = min([y_top] + [f - t * sa - s * sb for s, t, f in samples if t > 0])
        gap = sum(f - (y_top + t * sa + s * sb) for s, t, f in samples) / len(samples)
        if best is None or gap < best[0] - 1e-9:
            best = (gap, y_top, sa, sb)
    gap, y_top, sin_a, sin_b = best
    up = Vector((0, 1, 0))
    u = (u0 * math.sqrt(1 - sin_b ** 2) + up * sin_b).normalized()
    v = v0 * math.sqrt(1 - sin_a ** 2) + up * sin_a
    v = (v - u * u.dot(v)).normalized()
    print("tag LOD%d: tilt %.1f deg, roll %.1f deg, mean gap %.2f mm"
          % (lod + 1, math.degrees(math.asin(sin_a)), math.degrees(math.asin(sin_b)), gap * 1000))
    return g.Frame((pin.x, y_top, pin.z), u, v, u.cross(v)), sin_a


def tag_outline(nseg):
    """Tag outline (s, t) in its plane: rounded corners with nseg segments, counter-clockwise."""
    w2, t0, t1, r = L.TAG_W / 2, -(L.TAG_H - L.TAG_TOP), L.TAG_TOP, TAG_RC
    pts = []
    for cs, ct, a0 in ((w2 - r, t1 - r, 0.0), (-w2 + r, t1 - r, 90.0), (-w2 + r, t0 + r, 180.0),
                       (w2 - r, t0 + r, 270.0)):
        for k in range(nseg + 1):
            a = math.radians(a0 + 90.0 * k / nseg)
            pts.append((cs + r * math.cos(a), ct + r * math.sin(a)))
    return pts


def tag_curl(t):
    """Bend of the tag away from the film (along the normal): 0 at the staple, TAG_CURL at the bottom."""
    f = (L.TAG_TOP - t) / L.TAG_H
    return TAG_CURL * f * f


TAG_FRAMES = {lod: tag_frame(lod) for lod in FILM}
TAG_FRAME, TAG_SIN = TAG_FRAMES[0]
_tc = TAG_FRAME.p(0.0, L.TAG_TOP - L.TAG_H / 2, TAG_T)
_ys = [TAG_FRAME.p(s, t, TAG_T + tag_curl(t)).y for s, t in tag_outline(2)]
_phi = math.radians(abs(L.TAG_ROT))
_cos_a = math.sqrt(1 - TAG_SIN ** 2)
TAG_DEC = (wdecal("decal_tag.png"), "y", -1, ("x", "z"), (_tc.x, _tc.z),
           (L.TAG_W * math.cos(_phi) + L.TAG_H * _cos_a * math.sin(_phi),
            L.TAG_W * math.sin(_phi) + L.TAG_H * _cos_a * math.cos(_phi)),
           (min(_ys) - 0.0006, max(_ys) + 0.0006))

PCB_C = (0.0, L.PCB_Z0 + 0.050)
PCB_DEC = [(wdecal("decal_pcb_front.png"), "y", -1, ("x", "z"), PCB_C, (0.080, 0.100),
            (L.PCB_Y0 - 0.0003, L.PCB_Y0 + 0.0003)),
           (wdecal("decal_pcb_back.png"), "y", 1, ("x", "z"), PCB_C, (0.080, 0.100),
            (L.PCB_Y0 + L.PCB_T - 0.0003, L.PCB_Y0 + L.PCB_T + 0.0003))]
CHIP_DEC = [(wdecal("decal_chips.png"), "y", -1, ("x", "z"), PCB_C, (0.080, 0.100),
             (L.PCB_Y0 - 0.0052, L.PCB_Y0 - 0.0033))]
CAP_X = [(bx(cx - lx / 2), bx(cx + lx / 2)) for k, cx, cz, lx, wz, h, n in L.PARTS if k == "cap"]
_ep = [p for p in L.PARTS if p[0] == "eprom"][0]
EPROM_FRIT = L.PCB_Y0 - dip_shape(_ep)[2] / 1000.0             # y of the ceramic glass seal (parting line)

LOD_SPECS = [
    dict(lod=0, sides=8),
    dict(lod=1, sides=6),
]

REGIONS = {
    "pcb": ("pcb", 1.0), "pcb_back": ("pcb", 0.5), "pcb_edge": ("pcb_edge", 0.4),
    "chip": ("chip", 1.0), "ceramic": ("ceramic", 1.0), "window": ("window", 1.6),
    "cap": ("cap", 1.0), "can": ("can", 1.0), "tin": ("tin", 0.7),
    "steel": ("steel", 1.0), "paper": ("paper", 1.6), "film": ("film", 1.0),
}

LIT = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, floor_z=-1.0)


def mat_dip(mat, origin, color, gloss, spec, seed, ceramic=False):
    """DIP body: epoxy compound (fine mould grain, tone blotches, edges rubbed lighter) or ceramic (a
    dark glass-seal stripe along the parting line); the top is the decal_chips drawing (key, first-lead
    dot, marking stripes, ROM window). Leads are separate parts (pins_*).
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    dark = tuple(c * 0.84 for c in color[:3]) + (1,)
    col = t.mixc(t.maprange(t.noise(vec, 900.0, 2.0, 0.5), 0.35, 0.65, 0.0, 1.0), dark, color)
    col = t.mixc(t.maprange(t.noise(vec, 40.0, 4.0, 0.5), 0.3, 0.7, 0.0, 0.6), col, dark)
    edge = t.maprange(t.edge_wear(0.0004), 0.05, 0.3, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.4), col, tuple(min(1.0, c * 1.9 + 0.03) for c in color[:3]) + (1,))
    if ceramic:
        y = sep.outputs["Y"]
        frit = t.math("MULTIPLY", t.math("GREATER_THAN", y, EPROM_FRIT - 0.00028),
                      t.math("LESS_THAN", y, EPROM_FRIT + 0.00028))
        side = t.math("LESS_THAN", t.math("ABSOLUTE", nsep.outputs["Y"]), 0.6)
        col = t.mixc(t.math("MULTIPLY", frit, side), col, kmats.lin((52, 40, 34)))
    col = kmats.decals(t, col, sep, nsep, CHIP_DEC)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, -1.0, 0.0, 0.12, 0.4)
    gl = t.math("SUBTRACT", gloss, t.math("MULTIPLY", dirt, gloss * 0.5))
    return kmats.out(t, col, gl, spec, t.math("MULTIPLY", edge, -0.15))


def mat_window(mat, origin):
    """ROM quartz window: a light bezel, the window and die drawing from decal_chips on top; glossy."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 4.4)
    nsep = t.normal()
    col = kmats.decals(t, kmats.lin((150, 146, 136)), sep, nsep, CHIP_DEC)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, -1.0, 0.0, 0.05, 0.2)
    return kmats.out(t, col, 0.8, 0.6, 0.0)


def mat_axial(mat, origin):
    """K50-6: aluminium can in a blue sleeve (from the minus end to the crimp), a light 'minus' stripe
    along the top, a crimp and a rubber plug at the plus end; bare aluminium is matte.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 12.0)
    nsep = t.normal()
    x = sep.outputs["X"]
    sleeve = plug = None
    for a, b in CAP_X:
        s = t.math("MULTIPLY", t.math("GREATER_THAN", x, a + 0.00025), t.math("LESS_THAN", x, b - 0.00195))
        p = t.math("MULTIPLY", t.math("GREATER_THAN", x, b - 0.00006), t.math("LESS_THAN", x, b + 0.001))
        sleeve = s if sleeve is None else t.math("ADD", sleeve, s)
        plug = p if plug is None else t.math("ADD", plug, p)
    plug = t.math("MULTIPLY", plug, t.math("GREATER_THAN", nsep.outputs["X"], 0.7))
    col = t.mixc(t.maprange(t.noise(vec, 25.0, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0), kmats.lin((26, 44, 104)),
                 kmats.lin((34, 58, 132)))
    stripe = t.math("GREATER_THAN", t.math("MULTIPLY", nsep.outputs["Y"], -1.0), 0.92)
    col = t.mixc(stripe, col, kmats.lin((176, 184, 196)))
    col = t.mixc(sleeve, t.mixc(t.maprange(t.noise(vec, 60.0, 3.0, 0.5), 0.3, 0.7, 0.0, 1.0),
                                kmats.lin((150, 152, 154)), kmats.lin((182, 184, 186))), col)
    col = t.mixc(plug, col, kmats.lin((44, 44, 46)))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, -1.0, 0.0, 0.12, 0.4)
    gl = t.mixf(sleeve, 0.42, 0.48)
    return kmats.out(t, col, t.mixf(plug, gl, 0.15), t.mixf(sleeve, 0.45, 0.35), 0.0)


KINDS = kmats.std_kinds(floor_z=-1.0)
KINDS.update({
    # green solder mask with the board drawing on both sides; no dust inside the bag
    "pcb": ("paint", dict(LIT, color=kmats.lin((34, 96, 58)), under=kmats.lin((34, 96, 58)), seed=2.2, gloss=0.55,
                          spec=0.35, dust=0.0, grime=0.15, decal_items=PCB_DEC)),
    # FR4 fibreglass edges are pale olive and rough
    "pcb_edge": ("paint", dict(LIT, color=kmats.lin((176, 168, 118)), under=kmats.lin((176, 168, 118)), seed=2.6,
                               gloss=0.18, spec=0.10, dust=0.0, grime=0.25)),
    "chip": (mat_dip, dict(color=kmats.lin((26, 26, 28)), gloss=0.32, spec=0.22, seed=3.1)),
    "ceramic": (mat_dip, dict(color=kmats.lin((196, 190, 176)), gloss=0.40, spec=0.28, seed=3.7, ceramic=True)),
    "window": (mat_window, {}),
    "cap": (mat_axial, {}),
    # crystal can is nickel-plated steel; leads and chip legs are tinned, matte
    "can": ("steel", dict(seed=7.3, tone=0.44, along="x", gloss=0.55, spec=0.65, floor_z=-1.0, dust=0.0, grime=0.2)),
    "tin": ("steel", dict(seed=6.4, tone=0.46, along="y", gloss=0.45, spec=0.55, floor_z=-1.0, dust=0.0, grime=0.25)),
    # tag and staple are outside the bag: dust and hand stains
    "paper": ("paint", dict(LIT, color=kmats.lin((228, 214, 172)), under=kmats.lin((228, 214, 172)), seed=5.3,
                            gloss=0.12, spec=0.06, dust=0.2, grime=0.35, yellow=0.3, decal_items=[TAG_DEC])),
    "film": ("flat", dict(color=kmats.lin((160, 162, 166)), gloss=0.9, spec=0.8)),   # glass section, not baked
})


# --- film: texture with wear and rvmat ---------------------------------------------------------
FILM_SPEC, FILM_GLOSS = 0.30, 0.60     # film SMDI: G highlight strength, B gloss (up to x0.85 of the profile)


def _vgrid(rng, h, w, cy, cx):
    """Smooth noise 0..1 on an h x w grid: cy x cx cells (smoothed bilinear)."""
    cy, cx = max(1, int(round(cy))), max(1, int(round(cx)))
    gr = rng.random((cy + 2, cx + 2))
    yy = (np.arange(h) + 0.5) / h * cy
    xx = (np.arange(w) + 0.5) / w * cx
    yi, xi = yy.astype(int), xx.astype(int)
    fy, fx = yy - yi, xx - xi
    fy, fx = (fy * fy * (3 - 2 * fy))[:, None], (fx * fx * (3 - 2 * fx))[None, :]
    a, b = gr[yi][:, xi], gr[yi][:, xi + 1]
    c, d = gr[yi + 1][:, xi], gr[yi + 1][:, xi + 1]
    top, bot = a + (b - a) * fx, c + (d - c) * fx
    return top + (bot - top) * fy


def film_wear(a):
    """Film wear over bag_ca.png (RGBA 0..1, rows top to bottom; back on the left, front on the right):
    dirt at the edges, seams and weld, rubbed spots, thin scratches and specks - their masks are drawn
    four times finer than a pixel and averaged (otherwise a 1-pixel line of the 512 texture turns into a
    staircase). No letters; fingerprints, folds and the ESD mark are already in the make_decals.py
    drawing.
    """
    a = a.copy()
    H, W = a.shape[:2]
    hw = W // 2
    F = 4                                                 # resolution margin for the scratch and speck masks
    bw, bh = L.BAG_W * 1000.0, L.BAG_H * 1000.0          # half-texture size in mm
    kx_, kz_ = hw / bw, H / bh                            # px per mm
    xm = (np.arange(hw) + 0.5) / kx_
    zm = (np.arange(H) + 0.5) / kz_                       # from the top edge (the neck) down
    d_edge = np.minimum(np.minimum(xm, bw - xm)[None, :], (bh - zm)[:, None])
    z_mod = (L.HZ - zm / 1000.0)[:, None]
    seal = ((z_mod > L.SEAL_Z0 - 0.002) & (z_mod < L.SEAL_Z1 + 0.002)).astype(np.float32)
    near = np.clip(np.exp(-d_edge / 5.0) + 0.6 * seal, 0.0, 1.0)
    for half, seed in ((0, 71), (1, 73)):
        rng = np.random.default_rng(seed)
        s = a[:, half * hw:(half + 1) * hw]
        rgb, al = s[..., :3], s[..., 3]
        n1 = _vgrid(rng, H, hw, bh / 7.0, bw / 7.0) * 0.65 + _vgrid(rng, H, hw, bh / 2.2, bw / 2.2) * 0.35
        dirt = np.clip((n1 - 0.50) * 2.4, 0.0, 1.0) * (0.15 + 0.85 * near) * 0.45
        rgb[:] = rgb * (1 - dirt[..., None]) + np.array([0.37, 0.35, 0.31]) * dirt[..., None]
        al[:] = al + 0.18 * dirt
        n2 = _vgrid(rng, H, hw, bh / 13.0, bw / 13.0)
        scuff = np.clip((n2 - 0.62) * 3.0, 0.0, 1.0) * 0.28
        rgb[:] = rgb * (1 - scuff[..., None]) + 0.72 * scuff[..., None]
        al[:] = al + 0.05 * scuff
        hs = np.zeros((H * F, hw * F), np.float32)        # scratches: lines 0.2 mm wide
        main = rng.uniform(0, math.pi)
        for _ in range(55):
            x0, z0 = rng.uniform(0, bw), rng.uniform(0, bh)
            ln = math.exp(rng.uniform(math.log(3.0), math.log(16.0)))
            ang = main + rng.normal(0.0, 0.3) if rng.random() < 0.6 else rng.uniform(0, math.pi)
            q = np.linspace(0.0, 1.0, max(3, int(ln / 0.04)))
            cols = np.clip(((x0 + math.cos(ang) * ln * q) * kx_ * F).astype(int), 0, hw * F - 2)
            rows = np.clip(((z0 + math.sin(ang) * ln * q) * kz_ * F).astype(int), 0, H * F - 2)
            val = (rng.uniform(0.4, 0.9) * np.sqrt(np.sin(np.pi * q))).astype(np.float32)
            for dr, dc in ((0, 0), (1, 0), (0, 1)):
                np.maximum.at(hs, (rows + dr, cols + dc), val)
        sc = hs.reshape(H, F, hw, F).mean(axis=(1, 3))
        rgb[:] = rgb + 0.35 * sc[..., None]
        al[:] = al + 0.05 * sc
        hs[:] = 0.0                                       # specks are light, near the edges and the weld
        m = 900
        px, pz = rng.integers(0, hw * F - 3, m), rng.integers(0, H * F - 3, m)
        keep = rng.random(m) < 0.08 + 0.92 * near[pz // F, px // F]
        for c0, r0 in zip(px[keep], pz[keep]):
            hs[r0:r0 + 3, c0:c0 + 3] = rng.uniform(0.5, 1.0)       # ~0.15 x 0.2 mm at a 1024 texture
        dust = hs.reshape(H, F, hw, F).mean(axis=(1, 3))
        rgb[:] = rgb * (1 - 0.6 * dust[..., None]) + 0.78 * 0.6 * dust[..., None]
        al[:] = al + 0.22 * dust
        np.clip(s, 0.0, 1.0, out=s)
    return a


FILM_TEX = 1024                        # film texture side: the 512 drawing doubled (scratches are thinner than a pixel)


def _up(a, size):
    """Bilinear upscale of RGBA (rows top to bottom) to size x size."""
    H, W = a.shape[:2]

    def axis(n, m):
        c = np.clip((np.arange(m) + 0.5) * n / m - 0.5, 0.0, n - 1.0)
        i0 = np.floor(c).astype(int)
        i1 = np.minimum(i0 + 1, n - 1)
        return i0, i1, (c - i0).astype(np.float32)
    y0, y1, fy = axis(H, size)
    x0, x1, fx = axis(W, size)
    top = a[y0][:, x0] * (1 - fx)[None, :, None] + a[y0][:, x1] * fx[None, :, None]
    bot = a[y1][:, x0] * (1 - fx)[None, :, None] + a[y1][:, x1] * fx[None, :, None]
    return top * (1 - fy)[:, None, None] + bot * fy[:, None, None]


def film_rgba():
    """bag_ca.png from make_decals.py, enlarged to FILM_TEX, with the film_wear wear: RGBA 0..1, rows
    top to bottom.
    """
    src = wdecal("bag_ca.png")
    if not os.path.exists(src):
        raise SystemExit("missing %s - run make_decals.py first" % src)
    im = bpy.data.images.load(src, check_existing=False)
    w, h = im.size
    arr = np.array(im.pixels[:], np.float32).reshape(h, w, 4)[::-1]
    bpy.data.images.remove(im)
    if w != FILM_TEX or h != FILM_TEX:
        arr = _up(arr, FILM_TEX)
    return film_wear(arr)


def bag_ca(path_png, **_):
    """Instead of the shared kexport.glass_ca: the film texture (make_decals.py) with wear."""
    os.makedirs(os.path.dirname(path_png), exist_ok=True)
    kbake.save_png(path_png, film_rgba())


def film_rvmat(path):
    """Instead of kexport.write_glass: the same glass (fresnel, forcedDiffuse - checked in game) but
    with a more matte film highlight: SMDI G 0.30 and B 0.51 instead of 1 and 1 (the 'dayz' profile:
    glass 0.9 -> 0.27).
    """
    kx.write_super(path, "#(argb,8,8,3)color(0.5,0.5,1,1,NOHQ)",
                   "#(argb,8,8,3)color(0,%.2f,%.2f,1,SMDI)" % (FILM_SPEC, FILM_GLOSS * kmats.LOOK["gloss"]),
                   specular=1.0, power=80.0, fresnel="#(ai,32,128,1)fresnel(1.74,1.36)", forced_alpha=1.0)


kx.glass_ca = bag_ca
kx.write_glass = film_rvmat


def film_material(path_png):
    """Film in the --look preview: the same texture with wear that goes to the game (bag_ca writes it
    where the build does, work/game_textures), the highlight as in film_rvmat.
    """
    bag_ca(path_png)
    im = bpy.data.images.load(path_png, check_existing=False)
    m = bpy.data.materials.new("m49_film")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = im
    nt.links.new(n.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(n.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = 1.0 - FILM_GLOSS * kmats.LOOK["gloss"]
    b.inputs["Specular IOR Level"].default_value = min(1.0, FILM_SPEC * kmats.LOOK["rvmat"]["specular"] * 2.5)
    return m


# --- preview: the bag lies --------------------------------------------------------------------
BACK_SHOTS = ("back",)


def laid(lods, back=False):
    """Matrix 'as it lies' (model -> preview world): face up with the neck away from the camera (+Y), or
    face down (back) with the neck towards the camera. The bottom is on the ground.
    """
    ys = [v.co.y for parts in lods for p in parts for v in p.bm.verts]
    if back:
        return Matrix.Translation((0.0, 0.0, -min(ys) + 0.0003)) @ Matrix.Rotation(math.radians(90.0), 4, "X")
    return Matrix.Translation((0.0, 0.0, max(ys) + 0.0003)) @ Matrix.Rotation(math.radians(-90.0), 4, "X")


class Model(kmodel.Model):
    """Preview of the lying bag: the model stays in its own axes (as when baking - procedural materials,
    decals and dust are computed from its normals and coordinates), while the ground, the sun and the
    camera are placed into its axes by the inverse matrix of laid().
    """

    @staticmethod
    def _env():
        return [(ob, ob.matrix_world.copy()) for ob in bpy.context.scene.objects if ob.type in ("MESH", "LIGHT")]

    @staticmethod
    def _shoot(cam, env, R, path, loc, target, lens, res):
        ri = R.inverted()
        for ob, m0 in env:
            ob.matrix_world = ri @ m0
        loc, target = Vector(loc), Vector(target)
        q = (target - loc).to_track_quat("-Z", "Y")
        cam.matrix_world = ri @ (Matrix.Translation(loc) @ q.to_matrix().to_4x4())
        cam.data.type = "PERSP"
        cam.data.lens = lens
        sc = bpy.context.scene
        sc.render.resolution_x, sc.render.resolution_y = res
        os.makedirs(os.path.dirname(path), exist_ok=True)
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)

    def render(self, lods, shots, row_step, row_shot, textured):
        """Grey shape (--geo, --bake-only --geo-render) and the game look (--preview): as in kmodel, but
        the bag lies (laid).
        """
        krender.clear_scene()
        cam = krender.setup(64 if textured else 16)
        env = self._env()
        if textured:
            mats = {"atlas": krender.game_material(self.game_tex, self.name),
                    "glass": krender.game_glass(os.path.join(self.game_tex, self.name + "_glass_ca.png"))}
            mats.update(self.panel_mats(False))
        else:
            mats = {"atlas": krender.grey(), "glass": krender.glass_grey()}
        tag = "tex" if textured else "geo"
        krender.place(lods[0], "l0", (0, 0, 0), mats)
        self.place_extras()
        for name, loc, target, lens in shots:
            self._shoot(cam, env, laid([lods[0]], name in BACK_SHOTS),
                        os.path.join(self.renders, "%s_%s.png" % (tag, name)), loc, target, lens, (1400, 1000))
        krender.clear_scene()
        cam = krender.setup(48 if textured else 16)
        env = self._env()
        for i, parts in enumerate(lods):
            krender.place(parts, "l%d" % i, (i * row_step, 0, 0), mats)
        loc, target = row_shot
        self._shoot(cam, env, laid(lods), os.path.join(self.renders, tag + "_lods.png"), loc, target, 32,
                    (1800, 800))

    def _render_look(self, lods, shots, scene, n_main=3, n_state=2):
        """Preview without baking: views of the lying bag (look_<view>.png) and look_compare - the bag
        stands on the ground beside vanilla samples and a 1.80 m person. The film is the texture with
        wear.
        """
        res = (1400, 1000)
        film = film_material(os.path.join(self.game_tex, self.name + "_glass_ca.png"))
        cam, origin = scene()
        env = self._env()
        krender.place_look(lods[0], self.kinds, origin, panels={"glass": film})
        for name, loc, target, lens in shots[:n_main]:
            self._shoot(cam, env, laid([lods[0]], name in BACK_SHOTS),
                        os.path.join(self.renders, "look_%s.png" % name), loc, target, lens, res)
        cam, origin = scene()
        obs = krender.place_look(lods[0], self.kinds, origin, panels={"glass": film})
        lift = HZ + 0.0005
        for ob in obs + [origin]:
            ob.location.z += lift
        xs = [v.co.x for p in lods[0] for v in p.bm.verts]
        x0, x1, top = min(xs), max(xs), 2 * HZ
        right = krender.reference_set(x1 + 0.35)
        cx, width = (x0 + right) / 2, right - x0
        dist = max(width, top * 1.6) * 0.95 + 0.8
        krender.shoot(cam, os.path.join(self.renders, "look_compare.png"), (cx, -dist, 1.35), (cx, 0.0, 0.85), 35,
                      (1600, 900))


OBJ, NAME = "m49_tech_sample", "ozr_tech_sample"
M = Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, glass=dict(), look="dayz")
# 'dayz' profile for this model: the parts lie in a sealed bag - there is almost no dirt streaking on
# them
kmats.LOOK = dict(kmats.LOOK, streaks=0.15)
P = M.part
BOUNDS = {}


def face(part, verts, want):
    """Face from bmesh vertices, oriented towards want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def film_part(name, lod, side):
    xs, zs, ys = FILM[lod][side]
    front = side == "front"
    p = P(name, "film", section="glass")
    bm = p.bm
    vs = [[bm.verts.new((x, ys[i][j], z)) for j, z in enumerate(zs)] for i, x in enumerate(xs)]
    faces = []
    for i in range(len(xs) - 1):
        for j in range(len(zs) - 1):
            q = [vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]]   # normal -Y
            faces.append(bm.faces.new(q if front else q[::-1]))
    p.tag(faces)
    bm.normal_update()
    # film UV: the front is the right half of _ca, the back the left (x runs left to right, as on the
    # front)
    a0, a1 = (-3 * HX, HX) if front else (-HX, 3 * HX)
    p.glass_frame = (g.Frame((0, 0, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0)), a0, a1, -HZ, HZ)
    return p


# --- board and parts ----------------------------------------------------------------------------
def loft(part, prof, sections, zc, center=(0.0, 0.0), cap0=True, cap1=True, open_last=True):
    """Body along x over the section prof [(w, h)] mm (counter-clockwise): sections [(x mm, scale)] -
    the section squeezed towards center (w, h) by that scale; the face between the last and the first
    section point (the bottom, towards the board) is not built (open_last). Face normal (w, h): (dh,
    -dw) -> model (0, dw, dh).
    """
    bm = part.bm
    cw, ch = center
    rings = [[bm.verts.new(at(x, ch + (hh - ch) * s, cw + (w - cw) * s, zc)) for w, hh in prof] for x, s in sections]
    k = len(prof)
    new = []
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(k - 1 if open_last else k):
            j = (i + 1) % k
            dw, dh = prof[j][0] - prof[i][0], prof[j][1] - prof[i][1]
            new.append(face(part, [r0[i], r0[j], r1[j], r1[i]], (0.0, dw, dh)))
    if cap0:
        new.append(face(part, rings[0], (-1, 0, 0)))
    if cap1:
        new.append(face(part, rings[-1], (1, 0, 0)))
    part.tag(new)
    return new


def lathe_x(part, prof, x0, ya, zc, sides, drop=0.55):
    """Body of revolution along x: prof [(r, dx)] mm from the end x0 (mm), the axis ya mm above the
    board; the top face is whole (phase -pi/sides), faces looking into the board (normal towards +Y
    above drop) are not built.
    """
    bm = part.bm
    ph = -math.pi / sides
    rings = [[bm.verts.new(at(x0 + dx, ya + r * math.cos(ph + 2 * math.pi * k / sides),
                              r * math.sin(ph + 2 * math.pi * k / sides), zc)) for k in range(sides)]
             for r, dx in prof]
    new = []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            am = ph + 2 * math.pi * (k + 0.5) / sides
            want = Vector((0.0, -math.cos(am), math.sin(am)))
            if want.y > drop:
                continue
            new.append(face(part, [r0[k], r0[j], r1[j], r1[k]], want))
    new.append(face(part, rings[0], (-1, 0, 0)))
    new.append(face(part, rings[-1], (1, 0, 0)))
    part.tag(new)


def stadium(r, c, yc, segs):
    """'Stadium' section (w, h) mm: two semicircles of radius r centred at (+-c, yc), counter-clockwise
    from the bottom right; the last face (the bottom) is towards the board.
    """
    pts = [(c + r * math.cos(-math.pi / 2 + math.pi * k / segs), yc + r * math.sin(-math.pi / 2 + math.pi * k / segs))
           for k in range(segs + 1)]
    pts += [(-c + r * math.cos(math.pi / 2 + math.pi * k / segs), yc + r * math.sin(math.pi / 2 + math.pi * k / segs))
            for k in range(segs + 1)]
    return pts


def wire(part, pts_mm, zc, r_mm, sides):
    """Lead: a rod through the points (x, h, w) mm (kgeo pipe - no twisting)."""
    g.pipe(part, [tuple(at(x, h, w, zc)) for x, h, w in pts_mm], r_mm / 1000.0, sides)


def build_pcb():
    """Half-size Eurocard with a key notch between the contacts; the edges are FR4, the back is the
    solder side.
    """
    pcb = P("pcb", "pcb")
    k0, k1 = L.FINGERS[5]
    poly = [(bx(-40), bz(0)), (bx(k0), bz(0)), (bx(k0), bz(KEY_D)), (bx(k1), bz(KEY_D)), (bx(k1), bz(0)),
            (bx(40), bz(0)), (bx(40), bz(100)), (bx(-40), bz(100))]
    g.prism(pcb, poly, (0, 2), L.PCB_Y0, L.PCB_Y0 + L.PCB_T)
    back = pcb.region_index("pcb_back", *REGIONS["pcb_back"])       # solder side - less room in the atlas
    edge = pcb.region_index("pcb_edge", *REGIONS["pcb_edge"])
    for f in pcb.bm.faces:
        f.normal_update()
        if f.normal.y > 0.9:
            f[pcb.reg] = back
        elif abs(f.normal.y) < 0.5:
            f[pcb.reg] = edge
    return pcb


def build_board(spec):
    lod, n = spec["lod"], spec["sides"]
    near = lod == 0
    parts = [build_pcb()]
    chips, cer, win = P("chips", "chip"), P("eprom", "ceramic"), P("window", "window")
    for i, part in enumerate(L.PARTS):
        kind, cx, cz, lx, wz, h, npin = part
        zc = bz(cz)
        x0, x1 = cx - lx / 2, cx + lx / 2
        if kind in ("dip", "eprom"):
            W, s0, hp, zf = dip_shape(part)
            body = cer if kind == "eprom" else chips
            loft(body, dip_profile(kind, W, h, s0, hp, simple=not near), [(x0, 1.0), (x1, 1.0)], zc)
            if kind == "eprom":                                       # quartz window - a convex disc
                wx = cx + WIN_X
                ns = 10 if near else 8
                bm = win.bm
                lo = [bm.verts.new(at(wx + WIN_R * math.cos(2 * math.pi * k / ns), h - 0.05,
                                      WIN_R * math.sin(2 * math.pi * k / ns), zc)) for k in range(ns)]
                hi = [bm.verts.new(at(wx + (WIN_R - 0.3) * math.cos(2 * math.pi * k / ns), h + WIN_H,
                                      (WIN_R - 0.3) * math.sin(2 * math.pi * k / ns), zc)) for k in range(ns)]
                new = [face(win, [lo[k], lo[(k + 1) % ns], hi[(k + 1) % ns], hi[k]],
                            (math.cos(2 * math.pi * (k + 0.5) / ns), -0.6, math.sin(2 * math.pi * (k + 0.5) / ns)))
                       for k in range(ns)]
                new.append(face(win, hi, (0, -1, 0)))
                win.tag(new)
            if near:                                                  # leads - blades onto the pads
                pn = P("pins_%d" % i, "tin", uv_name="pins", uv_origin=(bx(cx), 0.0, zc))
                bm = pn.bm
                new = []
                for x in pin_xs(part):
                    for sg in (-1, 1):
                        q = [bm.verts.new(at(x - PIN_TOP, hp, sg * (W + 0.02), zc)),
                             bm.verts.new(at(x + PIN_TOP, hp, sg * (W + 0.02), zc)),
                             bm.verts.new(at(x + PIN_FOOT, -0.05, sg * zf, zc)),
                             bm.verts.new(at(x - PIN_FOOT, -0.05, sg * zf, zc))]
                        new.append(face(pn, q, (0.0, -0.3, sg)))
                pn.tag(new)
                parts.append(pn)
        elif kind == "xtal":
            xt = P("xtal", "can")
            xb = x0 + (XT_FL - 0.3 if near else 0.0)                 # can - from the flange
            secs = [(xb, 1.0), (x1 - 0.45, 1.0), (x1, 0.86)] if near else [(xb, 1.0), (x1, 1.0)]
            loft(xt, stadium(XT_R, XT_C, XT_YC, 3), secs, zc, center=(0.0, XT_YC), cap0=not near)
            if near:                                                  # base flange and leads
                loft(xt, stadium(XT_R + 0.3, XT_C, XT_YC, 3), [(x0, 1.0), (x0 + XT_FL, 1.0)], zc)
                xl = P("xtal_leads", "tin")
                for sg in (-1, 1):
                    wire(xl, [(x0 + 0.15, XT_YC, sg * 2.44), (x0 - 1.0, XT_YC, sg * 2.2),
                              (XT_PAD + 0.45, 1.1, sg * 1.1), (XT_PAD + 0.25, -0.3, sg * 0.9)], zc, 0.22, 3)
                parts.append(xl)
            parts.append(xt)
        else:                                                         # K50-6, minus towards x0
            cp = P("cap_%d" % i, "cap", uv_name="cap", uv_origin=(bx(cx), 0.0, zc))
            prof = CAP_PROF if near else [(2.6, 0.0), (CAP_R, 0.6), (CAP_R, lx - 0.6), (2.5, lx)]
            lathe_x(cp, prof, x0, CAP_AXIS, zc, n)
            parts.append(cp)
            if near:
                cl = P("cap_leads_%d" % i, "tin", uv_name="cap_leads", uv_origin=(bx(cx), 0.0, zc))
                for xe, sg in ((x0, -1), (x1, 1)):
                    wire(cl, [(xe - sg * 0.3, CAP_AXIS, 0.0), (xe + sg * 1.5, CAP_AXIS, 0.0),
                              (xe + sg * CAP_PAD, CAP_AXIS - 1.4, 0.0), (xe + sg * CAP_PAD, -0.3, 0.0)], zc, 0.3, 3)
                parts.append(cl)
    return parts + [chips, cer, win]


def build_tag(spec):
    """Manila tag: rounded corners, the bottom bent away from the film; the 24/6 staple is wire over the
    tag, with clinched legs on the back of the bag (near LOD).
    """
    lod = spec["lod"]
    frame = TAG_FRAMES[lod][0]
    tag = P("tag", "paper")
    bm = tag.bm
    out = tag_outline(2 if lod == 0 else 1)
    top = [bm.verts.new(frame.p(s, t, TAG_T + tag_curl(t))) for s, t in out]
    bot = [bm.verts.new(frame.p(s, t, tag_curl(t))) for s, t in out]
    new = [face(tag, top, frame.n), face(tag, bot[::-1], -frame.n)]
    tc = L.TAG_TOP - L.TAG_H / 2
    for k in range(len(out)):
        j = (k + 1) % len(out)
        mid = frame.u * ((out[k][0] + out[j][0]) / 2) + frame.v * ((out[k][1] + out[j][1]) / 2 - tc)
        new.append(face(tag, [bot[k], bot[j], top[j], top[k]], mid))
    tag.tag(new)
    parts = [tag]
    if lod == 0:
        st = P("staple", "steel")
        r = 0.00026
        crown = [(-0.0060, TAG_T - 0.0001), (-0.00592, TAG_T + 0.6 * r), (-0.0057, TAG_T + r), (0.0057, TAG_T + r),
                 (0.00592, TAG_T + 0.6 * r), (0.0060, TAG_T - 0.0001)]
        g.pipe(st, [tuple(frame.p(s, 0.0, c)) for s, c in crown], r, 4)
        yb = SEAL_Y + r                                               # back: legs bent to the middle
        for sg in (-1, 1):
            a, b = frame.p(sg * 0.0060, 0.0, 0.0), frame.p(sg * 0.0022, 0.0, 0.0)
            g.pipe(st, [(a.x, yb - 0.00015, a.z), (b.x, yb, b.z)], r, 4)
        parts.append(st)
    return parts


def build_lod(spec):
    lod = spec["lod"]
    parts = build_board(spec) + build_tag(spec) + [film_part("film_front", lod, "front"),
                                                   film_part("film_back", lod, "back")]
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if lod == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


INV_VIEW = (-0.252, -0.252, 0.050)    # front-left at 45 degrees, slightly above


def preview_aspect(bbox, cam):
    """Width / height of the preview frame from camera cam onto the centre (a 1x2 cell: at most 0.5)."""
    x0, x1, y0, y1, z0, z1 = bbox
    c = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    d = (c - Vector(cam)).normalized()
    right = d.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(d).normalized()
    pts = [Vector(q) - c for q in kx.box_pts(*bbox)]
    w = max(q.dot(right) for q in pts) - min(q.dot(right) for q in pts)
    h = max(q.dot(up) for q in pts) - min(q.dot(up) for q in pts)
    return w / h


def collision():
    """One convex box around the bag (Paper.p3d is also a sheet box). The mass is the sample weight in
    the mod, 60 g; the impact sound is plastic.
    """
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (-HX, HX, lo[1], hi[1], -HZ, HZ)
    comps = [(kx.box_pts(*bbox), kx.PEN + r"\plastic.rvmat")]
    memory = {
        "invView": [INV_VIEW],
        "ce_center": [(0.0, 0.0, 0.0)],
        "ce_radius": [(math.hypot(HX, HZ), 0.0, 0.0)],
    }
    print("bbox y %.4f..%.4f, preview aspect from invView %.2f (1x2 cell: <= 0.5)"
          % (lo[1], hi[1], preview_aspect(bbox, INV_VIEW)))
    return comps, 0.06, memory, bbox


# views - the bag lies face up with the neck away from the camera (+Y); back - face down, neck towards
# the camera. The first six are the --look previews: overview, top, the board close-up (leads, crystal,
# ROM window), the tag with the staple, the back (solder side, staple legs), the end (thickness, how the
# film lies on the parts)
SHOTS = [
    ("front", (-0.07, -0.21, 0.25), (0.0, 0.0, 0.004), 50),
    ("top", (0.0, -0.03, 0.34), (0.0, 0.0, 0.0), 50),
    ("board", (0.035, -0.10, 0.11), (0.0, -0.015, 0.004), 50),
    ("tag", (0.06, 0.005, 0.10), (0.012, 0.052, 0.004), 50),
    ("back", (0.07, -0.21, 0.25), (0.0, 0.0, 0.004), 50),
    ("edge", (-0.24, -0.10, 0.05), (0.0, 0.0, 0.004), 60),
]

if __name__ == "__main__":
    M.look_shots = (6, 0)
    M.run(build_lod, collision, SHOTS, row_step=0.14, row_shot=((0.07, -0.26, 0.30), (0.07, 0.0, 0.0)))
