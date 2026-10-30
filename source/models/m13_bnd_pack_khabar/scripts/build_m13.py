"""M13 - lead chest for loot: Loot Packer of the Bandits (OZL_Bnd_Pack_Khabar).
Packer: cargo 10x10, three module places on the lid (module_1..3) and module proxies in the same places.
Each module of the "Khabar" line has its own slot and place: slot 1 - dosimeter M75 at the front left
(an empty slot is a clean rectangle in the dust on the lead); slot 2 - jeweller's loupe M76 on the
right, in front of the heap of watches and chains; slot 3 - lead capsule M77 at the rear left. The "work"
look of the station is a pager in the pile of loot.

    blender --background --python build_m13.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: system Python make_decals.py (hryvnias, cards, dials, the pager screen "off" and
"work" frames, sign). Where things lie on the lid - loot.py (shared with make_decals.py), the size and
design of the hryvnias - uah.py.

Look: the "dayz" look (matte, dirtier, coloured AO); the chest follows M07 on the same B2 base (rounded
corners, recessed plinth on feet, lid with a rounded edge, gasket, hinges with a pin, a grille of slanted
louvres in a screwed frame); no handle or lock cylinder - they would leave holes; lead is its own
material (m13_mats.build_lead: dull, whitish oxide, dents, scratches down to bright metal, dark dirty
dust); rivets - low hexagonal heads; angles - GOST 8509 section with a fillet, slanted angle-grinder
cuts, bead welds; a chain of round links (12 points around the contour - a smooth silhouette); a lock
with a chamfer, a shackle through the lug, a keyhole cover and a bunch of keys; the loot is detailed and
from DayZ: "Chernomorka" packs (own box with the vanilla pack texture, as in M16), a heap of watches and
chains, money bundles of three layers, a butterfly knife with scales, pins and a latch, cigarette butts;
vanilla proxies (kvanilla): a partly drunk and an empty vodka bottle, a flashlight, a lockpick, an open
can.

Chest - base B2: a shop chest freezer of the 1970s-90s, 1500 x 860 x 680 mm, as in M07 and kchest
(sized by the volume class of the "Biryusa" range: CF32 1085 x 885 x 665, B-560KX 1790 x 810 x 665 mm).
Repainted dirty black over white factory enamel (Bandits), white and rust show in the chips.

Trim:
- crooked 3 mm lead sheets overlapping on rivets (the sheets are skewed, with dents, the lower edge
  waves away; the upper overlapping sheet passes over the edge of the lower), on the face, back, ends
  and lid; the compressor grille is left open;
- angles 40 x 40 x 4 (GOST 8509: fillet r1 = 5 mm) on the vertical edges and along the bottom of the
  face and back;
- a chain (link 60 x 34 mm, rod 10 mm) over the lid from a staple on the back to a lug on the face,
  a VS2M1 padlock on the lug: 105 x 70 x 34 mm, shackle dia. 14; the last link is on the shackle;
- a key in the keyhole, two more on the ring;
- loot (loot.py): hryvnia bundles under a rubber band (500, 200, 100 UAH; notes 142-154 x 75 by
  denomination, NBU - uah.py), loose 50 and 20 UAH, a "Chernomorka" carton (pack 88 x 55 x 22), cards
  58 x 88, a pager ~62 x 45 x 16 (like the Motorola Bravo), a butterfly knife (130 mm handles),
  wristwatches (case dia. 33-40), chains dia. ~2.4, rings, cigarette butts (filter 20 mm, dia. 7.8);
- a radiation sign in stencil paint on the face.

Work look: the pager screen is ozl_screen, own texture (section screen): "off" is blank glass, "work" is
frames _screen_fN (the number appears digit by digit, the envelope blinks; OZL_WorkFx frames); the
pager LED is ozl_lamp (atlas _on, blinks - blink). There are no moving parts. The modules in the slots
"work" together with the station (their own OZL_Work: the M75 display).

Blender axes: X is width, Y is depth (face toward -Y), Z is up.
"""
import math
import os
import sys

from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import kvanilla as kv  # noqa: E402
import loot  # noqa: E402
import m13_geo as G  # noqa: E402
import uah  # noqa: E402
from m13_mats import build_lead, build_rusty  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
CX0, CX1, CY0, CY1 = -0.75, 0.75, -0.34, 0.34                # chest (as M07 and kchest)
ZFOOT, ZB, ZG, ZL = 0.03, 0.075, 0.80, 0.86                  # plinth bottom, body bottom, lid seam, lid top
LIP, RCH = 0.006, 0.032                                      # lid overhang, rounding of the vertical corners
GRILLE = (-0.235, 0.235, 0.085, 0.335)                       # grille on the right end: y0, y1, z0, z1
T = 0.003                                                    # lead sheet
LIFT = T + 0.0008                                            # the upper overlapping sheet is raised above the lower
# angles 40 x 40 x 4, fillet 5 mm; the outer corner is outside the lead
AL, AT, AR = 0.040, 0.004, 0.005
AX0, AX1, AY0, AY1 = CX0 - 0.013, CX1 + 0.013, CY0 - 0.014, CY1 + 0.014
AZ = 0.060                                                   # bottom of the face/back angles
AYB0, AYB1 = CY0 - AT - 0.0012, CY1 + AT + 0.0012           # their leg lies against the body under the sheets
# chain in the plane x = CHX: from a staple on the back over the lid to the lock shackle on the face
CHX = -0.012
CH_L, CH_W, CH_D = 0.060, 0.034, 0.010                       # link: length, width, rod
CH_PITCH = CH_L - 2 * CH_D
# lug on the face: a plate with a hole (hole axis is x), the lock hangs by its shackle in it
EYE_Z, EYE_Y = 0.715, CY0 - 0.029                            # hole centre
STAPLE_Z, STAPLE_Y = 0.700, CY1 + 0.032                      # staple on the back: axis of the rod
# VS2M1 padlock: body 70 x 34 x 65, shackle dia. 14 (centre line radius 20), height with the shackle 105
PL_W, PL_D, PL_H, PL_SH, PL_ARC = 0.070, 0.034, 0.065, 0.007, 0.020
PL_ZT = EYE_Z - 0.001 - PL_ARC - 0.022                       # body top: shackle arc top is in the hole
PL_Y = EYE_Y
KH_Z = PL_ZT - PL_H / 2 - 0.010                              # keyhole

LOD_SPECS = [
    dict(lod=0, bev=2, sides=12),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "chest": ("paint_black", 0.5), "lid": ("paint_lid", 0.5), "plinth": ("dark", 0.3), "gasket": ("rubber", 0.4),
    "grille": ("grille", 0.6), "grille_frame": ("louver", 0.8), "steel": ("steel", 0.8), "hinge": ("hinge", 0.8),
    "hole": ("dark", 0.2), "screw": ("screw", 0.6),
    "lead": ("lead", 0.55), "lead_sign": ("lead_sign", 0.9), "lead_b": ("lead_b", 0.4), "lead_lid": ("lead_lid", 0.7),
    "rivet": ("rivet", 0.1), "angle": ("angle", 0.6), "weld": ("weld", 0.4), "chain": ("chain", 0.7), "eye": ("eye", 1.2),
    "lock": ("lock", 2.0), "shackle": ("shackle", 1.2), "brass": ("brass", 2.0), "keysteel": ("keysteel", 2.0),
    "band": ("band", 1.5), "carton": ("pager", 1.0),
    "pager": ("pager", 3.0), "pager_bezel": ("pager_bezel", 3.0), "pager_key": ("pager_key", 3.0), "led": ("led", 3.0),
    "knife_steel": ("knife_steel", 2.5), "blade": ("blade", 2.0), "knife_inlay": ("knife_inlay", 2.5),
    "knife_pin": ("knife_pin", 2.5),
    "w_steel": ("w_steel", 3.0), "w_gold": ("w_gold", 3.0), "leather": ("leather", 2.0), "gold": ("gold", 2.0),
    "stone": ("stone", 3.0), "filter": ("filter", 2.0), "paper": ("paper", 2.0), "ash": ("ash", 2.0),
}
for _nm, *_ in loot.CASH + loot.NOTES:
    REGIONS[_nm] = (_nm, 5.0)
REGIONS["deck"] = ("deck", 6.0)
for _nm, *_ in loot.FAN:
    REGIONS[_nm] = (_nm, 6.0)
for _w in loot.WATCHES + [loot.WATCH_TILT]:
    REGIONS["dial_" + _w[0]] = ("dial_" + _w[0], 8.0)


# =============================================================================
# Lead sheets (the geometry is needed before the materials: the loot is placed on them)
# =============================================================================
class Sheet:
    """Crooked lead sheet (from M09, with dents): o is the corner, u and v are the edges (full-length
    vectors), n is outward. The sheet bulges between the rivets, the lower edge waves away, dents are
    [(a, b, radius as a fraction, depth m)]; ramp = (a0, a1, h) - the upper overlapping sheet: from a0 to
    a1 it rises by h (passes over the edge of the lower one)."""

    def __init__(self, o, u, v, n, bulge, wave, seed, dents=(), ramp=None):
        self.o, self.u, self.v, self.n = Vector(o), Vector(u), Vector(v), Vector(n).normalized()
        self.bulge, self.wave, self.seed, self.dents, self.ramp = bulge, wave, seed, dents, ramp

    def lift(self, a):
        if not self.ramp:
            return 0.0
        a0, a1, h = self.ramp
        s = min(max((a - a0) / (a1 - a0), 0.0), 1.0)
        return h * s * s * (3 - 2 * s)

    def warp(self, a, b):
        bul = self.bulge * math.sin(math.pi * a) * math.sin(math.pi * b) * (0.7 + 0.3 * math.sin(5 * a + self.seed))
        wav = self.wave * (1 - b) ** 4 * math.sin(2 * math.pi * a + 0.3 * math.sin(self.seed)) ** 2
        dent = sum(dp * math.exp(-((a - da) ** 2 + (b - db) ** 2) / (r * r)) for da, db, r, dp in self.dents)
        # a dent presses the sheet to the chest, but not into it
        return max(0.0, bul + wav - dent) + self.lift(a)

    def at(self, a, b, off=T):
        return self.o + self.u * a + self.v * b + self.n * (self.warp(a, b) + off)

    def build(self, part, nu, nv):
        bm = part.bm
        front = [[bm.verts.new(self.at(i / nu, j / nv)) for j in range(nv + 1)] for i in range(nu + 1)]
        back = [[bm.verts.new(self.at(i / nu, j / nv, 0.0)) for j in range(nv + 1)] for i in range(nu + 1)]
        for i in range(nu):
            for j in range(nv):
                G.face(part, [front[i][j], front[i + 1][j], front[i + 1][j + 1], front[i][j + 1]], self.n)
                G.face(part, [back[i][j], back[i][j + 1], back[i + 1][j + 1], back[i + 1][j]], -self.n)
        un, vn = self.u.normalized(), self.v.normalized()
        for i in range(nu):
            G.face(part, [front[i][0], front[i + 1][0], back[i + 1][0], back[i][0]], -vn)
            G.face(part, [front[i][nv], front[i + 1][nv], back[i + 1][nv], back[i][nv]], vn)
        for j in range(nv):
            G.face(part, [front[0][j], front[0][j + 1], back[0][j + 1], back[0][j]], -un)
            G.face(part, [front[nu][j], front[nu][j + 1], back[nu][j + 1], back[nu][j]], un)
        part.bm.normal_update()

    def plate(self, part):
        """Far LOD: a flat slab by the corners of the sheet."""
        bm = part.bm
        q = [self.o, self.o + self.u, self.o + self.u + self.v, self.o + self.v]
        fr = [bm.verts.new(p + self.n * (T + 0.001)) for p in q]
        bk = [bm.verts.new(p) for p in q]
        G.face(part, fr, self.n)
        G.face(part, bk, -self.n)
        cen = sum(q, Vector()) / 4
        for i in range(4):
            j = (i + 1) % 4
            G.face(part, [fr[i], fr[j], bk[j], bk[i]], (q[i] + q[j]) / 2 - cen)

    def rivets(self, step, inset=0.022):
        """Rivets along the contour every ~step, a bit crooked (handmade)."""
        lu, lv = self.u.length, self.v.length
        du, dv = inset / lu, inset / lv
        out = []
        nu, nv = max(2, round(lu / step)), max(2, round(lv / step))
        for k in range(nu + 1):
            a = du + (1 - 2 * du) * k / nu
            for b in (dv, 1 - dv):
                out.append((a + 0.004 * math.sin(k * 7.1 + self.seed), b + 0.25 * dv * math.sin(k * 3.3 + self.seed)))
        for k in range(1, nv):
            b = dv + (1 - 2 * dv) * k / nv
            for a in (du, 1 - du):
                out.append((a + 0.25 * du * math.sin(k * 5.7 + self.seed), b))
        return [self.at(a, b) for a, b in out]


# sheets: name, area, sheet, (nu, nv) of the near LOD, rivet step (the head is a hexagonal pyramid: small,
# the faces are not visible, while a hemisphere of rings would still be faceted - p3d smoothing works up
# to 40 degrees); face and back - two overlapping sheets each, the upper one passes over the edge of the
# lower; the back is below the hinges
SHEETS = [
    ("lead_f0", "lead", Sheet((CX0 + 0.008, CY0, 0.11), (0.800, 0, 0.012), (0.004, 0, 0.660), (0, -1, 0), 0.009, 0.014,
                              1.3, dents=[(0.30, 0.35, 0.10, 0.012), (0.72, 0.72, 0.07, 0.009), (0.12, 0.80, 0.05, 0.006)]),
     (10, 7), 0.15),
    ("lead_f1", "lead_sign", Sheet((0.030, CY0, 0.095), (0.712, 0, -0.008), (-0.006, 0, 0.670), (0, -1, 0), 0.008, 0.012,
                                   2.9, dents=[(0.80, 0.25, 0.09, 0.011), (0.25, 0.60, 0.06, 0.007)],
                                   ramp=(0.075, 0.040, LIFT)), (10, 7), 0.15),
    ("lead_b0", "lead_b", Sheet((CX0 + 0.012, CY1, 0.10), (0.760, 0, -0.010), (0.0, 0, 0.645), (0, 1, 0), 0.008, 0.010,
                                4.1, dents=[(0.45, 0.55, 0.12, 0.010)]), (6, 5), 0.20),
    ("lead_b1", "lead_b", Sheet((-0.020, CY1, 0.12), (0.758, 0, 0.006), (0.005, 0, 0.622), (0, 1, 0), 0.008, 0.012,
                                5.3, dents=[(0.70, 0.30, 0.08, 0.008)], ramp=(0.095, 0.056, LIFT)), (6, 5), 0.20),
    ("lead_l", "lead", Sheet((CX0, CY0 + 0.012, 0.115), (0, 0.652, 0.010), (0, -0.004, 0.650), (-1, 0, 0), 0.010,
                             0.012, 6.2, dents=[(0.62, 0.40, 0.12, 0.012), (0.25, 0.75, 0.07, 0.008)]), (7, 6), 0.15),
    ("lead_r", "lead", Sheet((CX1, CY0 + 0.020, 0.370), (0, 0.640, -0.012), (0, 0.0, 0.405), (1, 0, 0), 0.007, 0.006,
                             7.7, dents=[(0.35, 0.55, 0.10, 0.009)]), (7, 5), 0.15),
    # lid: almost flat (the loot and modules stand on them), dents
    # only at the edges; the left sheet is over the right one
    ("lead_lid_r", "lead_lid", Sheet((0.120, CY0 - 0.002, ZL), (CX1 + 0.002 - 0.120, 0, 0), (0, 0.684, 0), (0, 0, 1), 0.002,
                                     0.0, 8.4, dents=[(0.85, 0.08, 0.08, 0.004), (0.06, 0.94, 0.07, 0.003)]),
     (7, 7), 0.15),
    ("lead_lid_l", "lead_lid", Sheet((CX0 - 0.002, CY0 - 0.004, ZL), (0.912, 0, 0), (0, 0.688, 0), (0, 0, 1), 0.001, 0.0,
                                     9.1, dents=[(0.03, 0.10, 0.06, 0.003), (0.55, 0.96, 0.05, 0.003)],
                                     ramp=(0.912, 0.956, LIFT)), (9, 7), 0.15),
]
SHEET = {nm: sh for nm, _, sh, *_ in SHEETS}
LID_L, LID_R = SHEET["lead_lid_l"], SHEET["lead_lid_r"]


def lid_z(x, y):
    """Top of the lead on the lid at a point (the left sheet lies over the right one up to its right edge)."""
    sh = LID_L if x <= LID_L.o.x + LID_L.u.x - 0.004 else LID_R
    a = min(max((x - sh.o.x) / sh.u.x, 0.0), 1.0)
    b = min(max((y - sh.o.y) / sh.v.y, 0.0), 1.0)
    return sh.at(a, b).z


def face_y(sheet, x, z):
    """Face of the face/back sheet at point (x, z): the y of the surface."""
    sh = SHEET[sheet]
    a = min(max((x - sh.o.x) / sh.u.x, 0.0), 1.0)
    b = min(max((z - sh.o.z - sh.u.z * a) / sh.v.z, 0.0), 1.0)
    return sh.at(a, b).y


# =============================================================================
# Layout of the watch heap: heights (the straps of the next ones lie on the previous, the chains on top)
# =============================================================================
HEAP = []                                                    # (x, y, radius, top above the lid)


def heap_rel(x, y):
    top = 0.0
    for cx, cy, r, h in HEAP:
        if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
            top = max(top, h)
    return top


def layout_heap():
    out = []
    for nm, (cx, cy), deg, r, h, strap, dial, (l12, l6) in loot.WATCHES:
        base = max([heap_rel(cx, cy)] + [heap_rel(cx + 0.85 * r * math.cos(t), cy + 0.85 * r * math.sin(t))
                                          for t in (k * math.pi / 3 for k in range(6))])
        a = math.radians(deg)
        u = Vector((math.cos(a), math.sin(a), 0.0))
        sw = 0.020 if r >= 0.019 else 0.018
        st = 0.0028 if strap != "leather" else 0.0024
        straps = []
        for s, L in ((1, l12), (-1, l6)):
            pts = []
            n = 8
            for i in range(n):
                d = r + 0.002 + (L - r - 0.002) * i / (n - 1)
                x, y = cx + u.x * s * d, cy + u.y * s * d
                k = max(0.0, 1.0 - (d - r - 0.002) / 0.016)
                desc = base + st / 2 + (0.45 * h - st / 2) * (0.5 - 0.5 * math.cos(math.pi * k))
                pts.append([x, y, max(heap_rel(x, y) + st / 2, desc)])
            for _ in range(2):
                for i in range(1, n - 1):
                    pts[i][2] = max(pts[i][2], (pts[i - 1][2] + pts[i + 1][2]) / 2 - 0.0004)
            straps.append(pts)
        HEAP.append((cx, cy, r, base + h))
        for pts in straps:
            for x, y, z in pts:
                HEAP.append((x, y, sw / 2, z + st / 2))
        out.append(dict(name=nm, c=(cx, cy), deg=deg, r=r, h=h, base=base, strap=strap, sw=sw, st=st, straps=straps,
                        tilt=None))
    # no bracelet, tilted: one edge on the lid, the other on the neighbour's case
    nm, (cx, cy), deg, r, h, dial, on = loot.WATCH_TILT
    w0 = next(w for w in out if w["name"] == on)
    d = Vector((w0["c"][0] - cx, w0["c"][1] - cy, 0.0)).normalized()
    h0 = w0["base"] + w0["h"]
    th = math.asin(min(0.9, h0 / (2 * r)))
    n = (-d * math.sin(th) + Vector((0, 0, 1)) * math.cos(th)).normalized()
    u0 = Vector((math.cos(math.radians(deg)), math.sin(math.radians(deg)), 0.0))
    u = (u0 - n * u0.dot(n)).normalized()
    out.append(dict(name=nm, c=(cx, cy), deg=deg, r=r, h=h, base=h0 / 2, strap=None, tilt=(n, u, n.cross(u))))
    HEAP.append((cx, cy, r, h0 / 2 + h * math.cos(th)))
    return out


WATCH_GEO = layout_heap()


def chain_heap():
    """Chains over the heap: anchor points -> smooth curve, the height is the top of the heap under it,
    sagging over the edges of the cases."""
    out = []
    for ctrl in loot.CHAINS:
        pts = [list(p) for p in G.spline([(x, y, 0.0) for x, y in ctrl], 4)]
        for p in pts:
            p[2] = heap_rel(p[0], p[1]) + 0.0012
        for _ in range(3):
            for i in range(1, len(pts) - 1):
                pts[i][2] = max(pts[i][2], (pts[i - 1][2] + pts[i + 1][2]) / 2 - 0.0006)
        out.append(pts)
    for pts in out:
        for x, y, z in pts:
            HEAP.append((x, y, 0.0024, z + 0.0012))
    return out


CHAIN_GEO = chain_heap()

# =============================================================================
# Materials
# =============================================================================


def decal(name, ax, sign, uv, center, size, rng=None):
    return (os.path.join(WORK, name), ax, sign, uv, center, size, rng)


def top_decal(name, center, size):
    """Decal on a top face: every part with a decal has its own area, hence no range."""
    return decal(name, "z", 1, ("x", "y"), center, size)


def rot_box(w, h, deg):
    a = math.radians(deg)
    return (w * abs(math.cos(a)) + h * abs(math.sin(a)), w * abs(math.sin(a)) + h * abs(math.cos(a)))


KINDS = kmats.std_kinds(floor_z=0.0)
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# dirty black paint over the white factory enamel (Bandits): chips down to white and rust, dirt at the
# bottom and in corners
BLACK = dict(color=kmats.lin((36, 36, 34)), under=kmats.lin((222, 222, 212)), seed=1.9, gloss=0.30, spec=0.22,
             chip=(0.55, 0.61), rust=(0.60, 0.68), rust_low=1.0, floor_z=0.0, dust=0.45, grime=0.9)
SIGN = (0.40, 0.40)                                          # sign on the right sheet of the face: centre x, z
TREFOIL = decal("decal_trefoil_spray.png", "y", -1, ("x", "z"), SIGN, (0.24, 0.24), (CY0 - 0.03, CY0 - 0.002))
GOLD = kmats.lin((196, 156, 72))
KINDS.update({
    "paint_black": ("paint", BLACK),
    "paint_lid": ("paint", dict(BLACK, seed=3.3, chip=(0.50, 0.57), rust_low=0.0)),
    "louver": ("paint", dict(BLACK, seed=5.9, chip=(0.50, 0.58))),
    "dark": ("flat", dict(color=kmats.lin((16, 16, 16)), gloss=0.15, spec=0.08)),
    "grille": (build_rusty, dict(seed=5.2, rust=0.45, dust=0.3, grime=0.8)),
    "hinge": (build_rusty, dict(seed=6.6, rust=0.35, bright=0.3)),
    "screw": (build_rusty, dict(seed=6.9, rust=0.5, scale=3.0)),
    # lead (m13_mats): face and ends, the right sheet of the face with the sign, back (dustier), lid - with
    # the clean trace of the instrument in the dust (empty slot 1)
    "lead": (build_lead, dict(seed=6.3, rust_streaks=0.25)),
    "lead_sign": (build_lead, dict(seed=9.6, decal_items=[TREFOIL], rust_streaks=0.25)),
    "lead_b": (build_lead, dict(seed=4.4, dust=0.55, rust_streaks=0.3)),
    "lead_lid": (build_lead, dict(seed=7.4, dust=0.32, clean=[loot.DUST_CLEAN])),
    "rivet": (build_rusty, dict(seed=7.3, rust=0.55, bright=0.2, scale=3.0)),
    "angle": (build_rusty, dict(seed=8.1, rust=0.55)),
    "weld": (build_rusty, dict(seed=9.9, rust=0.70, scale=2.0)),
    "chain": (build_rusty, dict(seed=4.6, rust=0.58, bright=0.6, scale=2.0)),
    "eye": (build_rusty, dict(seed=5.5, rust=0.50, bright=0.2)),
    # lock: dark grey enamel over silumin, worn down to metal at the edges
    "lock": ("paint", dict(color=kmats.lin((66, 68, 66)), under=kmats.lin((150, 150, 146)), seed=3.9, gloss=0.35,
                           spec=0.30, chip=(0.56, 0.62), rust=(0.64, 0.72), rust_low=0.0, floor_z=0.6, dust=0.3,
                           grime=0.6)),
    "shackle": ("steel", dict(seed=2.9, tone=0.34, along="z", gloss=0.45, spec=0.5, dust=0.2, grime=0.5)),
    "brass": ("paint", dict(CLEAN, color=kmats.lin((168, 136, 70)), gloss=0.55, spec=0.55, dust=0.1, grime=0.3)),
    "keysteel": ("steel", dict(seed=8.8, tone=0.42, along="z", gloss=0.5, spec=0.6, dust=0.05, grime=0.3)),
    # loot
    "band": ("plastic", dict(color=kmats.lin((150, 72, 48)), gloss=0.3, spec=0.2, dust=0.1)),
    "pager": ("plastic", dict(color=kmats.lin((30, 32, 34)), gloss=0.35, spec=0.25, dust=0.2, grime=0.3,
                              scuff=(0.58, 0.68))),
    "pager_bezel": ("plastic", dict(color=kmats.lin((14, 14, 15)), gloss=0.5, spec=0.35, dust=0.1, grime=0.2)),
    "pager_key": ("plastic", dict(color=kmats.lin((96, 98, 100)), gloss=0.15, spec=0.1, dust=0.2, grime=0.5,
                                  scuff=(0.7, 0.8))),
    "led": ("flat", dict(color=kmats.lin((96, 24, 20)), gloss=0.8, spec=0.7)),
    "led_on": ("flat", dict(color=kmats.lin((255, 50, 36)), gloss=0.8, spec=0.7)),
    "knife_steel": ("steel", dict(seed=3.3, tone=0.46, along="x", gloss=0.55, spec=0.65, dust=0.05, grime=0.35)),
    "blade": ("steel", dict(seed=3.7, tone=0.55, along="x", gloss=0.65, spec=0.75, dust=0.0, grime=0.2)),
    "knife_inlay": ("plastic", dict(color=kmats.lin((20, 20, 22)), gloss=0.3, spec=0.2, dust=0.1, grime=0.2,
                                    scuff=(0.6, 0.7))),
    "knife_pin": ("steel", dict(seed=4.1, tone=0.60, along="z", gloss=0.6, spec=0.7, dust=0.0, grime=0.2)),
    "w_steel": ("steel", dict(seed=5.1, tone=0.62, along="x", gloss=0.7, spec=0.8, dust=0.05, grime=0.25)),
    "w_gold": ("paint", dict(CLEAN, color=GOLD, gloss=0.7, spec=0.75)),
    "gold": ("paint", dict(CLEAN, color=kmats.lin((204, 164, 76)), gloss=0.72, spec=0.78)),
    "leather": ("plastic", dict(color=kmats.lin((78, 48, 28)), gloss=0.25, spec=0.15, mottle=0.15, dust=0.1,
                                grime=0.3, scuff=(0.6, 0.7))),
    "stone": ("flat", dict(color=kmats.lin((150, 16, 30)), gloss=0.9, spec=0.85)),
    "filter": ("plastic", dict(color=kmats.lin((196, 140, 80)), gloss=0.1, spec=0.05, mottle=0.2, dust=0.1,
                               grime=0.3, scuff=(0.9, 1.0))),
    "paper": ("plastic", dict(color=kmats.lin((226, 222, 208)), gloss=0.1, spec=0.05, mottle=0.1, dust=0.1,
                              grime=0.3, scuff=(0.9, 1.0))),
    "ash": ("flat", dict(color=kmats.lin((62, 60, 56)), gloss=0.05, spec=0.02)),
})


def note_edge(nm):
    """Colour of the pack end (a cut of light paper with the denomination
    ink) and of the note underside - by denomination (uah.PAL)."""
    pal = uah.PAL[loot.UAH[nm]]
    return kmats.lin(tuple(int(c * 0.90) for c in uah.mix(pal["paper"], pal["field"], 0.40)))


def loot_kinds():
    """Loot decals: each bundle, note, card and dial has its own look (top - a picture turned the way it
    lies; the hryvnias come from make_decals.py through uah.py)."""
    for nm, (cx, cy), deg, dz, t in loot.CASH:
        KINDS[nm] = ("paint", dict(CLEAN, color=note_edge(nm), gloss=0.15, spec=0.08, dust=0.1,
                                   decal_items=[top_decal("decal_%s.png" % nm, (cx, cy),
                                                          rot_box(*loot.note_size(nm), deg))]))
    for nm, (cx, cy), deg, dz in loot.NOTES:
        KINDS[nm] = ("paint", dict(CLEAN, color=note_edge(nm), gloss=0.15, spec=0.08, dust=0.1,
                                   decal_items=[top_decal("decal_%s.png" % nm, (cx, cy),
                                                          rot_box(*loot.note_size(nm), deg))]))
    nm, (cx, cy), deg, dz, t = loot.DECK
    KINDS[nm] = ("paint", dict(CLEAN, color=kmats.lin((226, 222, 210)), gloss=0.3, spec=0.2,
                               decal_items=[top_decal("decal_deck.png", (cx, cy), rot_box(*loot.CARD, deg))]))
    for nm, (cx, cy), deg, dz, code in loot.FAN:
        KINDS[nm] = ("paint", dict(CLEAN, color=kmats.lin((236, 234, 226)), gloss=0.3, spec=0.2,
                                   decal_items=[top_decal("decal_%s.png" % nm, (cx, cy), rot_box(*loot.CARD, deg))]))
    for w in WATCH_GEO:
        dr = 2 * w["r"] * 0.80
        c = dial_center(w)
        KINDS["dial_" + w["name"]] = ("paint", dict(CLEAN, color=kmats.lin((200, 196, 186)), gloss=0.6, spec=0.5,
                                                    decal_items=[top_decal("decal_dial_%s.png" % w["name"], (c.x, c.y),
                                                                           rot_box(dr, dr, w["deg"] - 90.0))]))


def watch_frame(w):
    """Origin (bottom of the case), the 12 o'clock axis (a), the 3
    o'clock axis (-b) and the normal of the watch dial."""
    cx, cy = w["c"]
    if w["tilt"]:
        n, u, v = w["tilt"]
    else:
        a = math.radians(w["deg"])
        u = Vector((math.cos(a), math.sin(a), 0.0))
        n = Vector((0.0, 0.0, 1.0))
        v = n.cross(u)
    return Vector((cx, cy, lid_z(cx, cy) + w["base"])), u, v, n


def dial_center(w):
    o, u, v, n = watch_frame(w)
    return o + n * (w["h"] - 0.0012)


OBJ, NAME = "m13_bnd_pack_khabar", "ozr_bnd_pack_khabar"
# Work look: the pager screen is its own texture (the frames are stepped by the mod script), the LED is
# the _on atlas (blinks).
SEL_SCREEN, SEL_LAMP = "ozl_screen", "ozl_lamp"
ON = dict(remap={"led": "led_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
SCREEN = dict(off="pager_off.png", frames=["pager_f%d.png" % i for i in range(8)], size=256, gloss=0.7)
# DayZ "Chernomorka" packs: an own box with the vanilla pack texture (the default DayZ pack model is another
# brand and the proxy cannot be repainted; as in M16); texture pieces are from M16
CIGS = (r"dz\gear\medical\data\pack_of_cigs_cherno_co.paa", r"dz\gear\medical\data\pack_of_cigs.rvmat")
CIGS_UV = {"front": (0.117, 0.462, 0.43, 1.0), "side": (0.885, 0.970, 0.60, 1.0), "end": (0.26, 0.45, 0.20, 0.30)}
# modules in the slots: slot N is module N of the "Khabar" line, no rotation (they face the person)
MOD_OBJ = [("m75_dosimeter", "ozr_dosimeter"), ("m76_jeweler_loupe", "ozr_jeweler_loupe"),
           ("m77_lead_case", "ozr_lead_case")]
# near-LOD bounds of the modules from the proxy point (their MLOD) - for checking the layout
MOD_BOX = [((-0.104, -0.074, 0.0), (0.100, 0.071, 0.166)), ((-0.097, -0.090, 0.0), (0.097, 0.097, 0.224)),
           ((-0.102, -0.076, 0.0), (0.099, 0.078, 0.113))]
MODS = [(x, y, lid_z(x, y)) for x, y in loot.SLOTS]
PROXIES = [(r"\OpenZone_Research\models\proxies\ozl_tool%d" % (i + 1), m) for i, m in enumerate(MODS)]


def lz(x, y):
    return (x, y, lid_z(x, y))


# vanilla items: on the lid - a partly drunk vodka by the packs, an empty one lying and an open can on the
# left, a flashlight by the dosimeter, a lockpick by the chain
DECOR = [
    kv.put("vodka", lz(0.672, 0.262), up=(0, 0, 1), fwd=(0.35, -1, 0)),
    kv.put("vodka", lz(-0.650, 0.055), **kv.flat(98)),
    kv.put(r"dz\gear\food\FoodCan_250g_open", lz(-0.655, 0.258), up=(0, 0, 1), fwd=(0.3, -1, 0)),
    kv.put("flashlight", lz(-0.645, -0.205), **kv.flat(0)),
    kv.put(r"dz\gear\tools\Lockpick", lz(-0.170, -0.185), **kv.flat(100)),
]
loot_kinds()
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 selections=(SEL_SCREEN, SEL_LAMP), hidden=(SEL_SCREEN, SEL_LAMP), states={"on": ON},
                 proxies=PROXIES, decor=DECOR, modules=[(o, n, m) for (o, n), m in zip(MOD_OBJ, MODS)],
                 panels={"screen": SCREEN}, vsections={"cigs": CIGS})
P = M.part
BOUNDS = {}


def screw(name, center, axis, r=0.0035, h=0.0024, region="screw", sides=6):
    """Screw head - its own part with a shared unwrap (like the bolt in M07)."""
    b = P(name, region, uv_name="screw_%s" % axis, uv_origin=center)
    g.cyl(b, center, axis, r, h, sides)
    return b


# =============================================================================
# Chest (base B2; as M07): body, plinth on feet, lid, gasket, grille, hinges
# =============================================================================
def build_chest(spec):
    lod = spec["lod"]
    nc = (4, 2, 1)[lod]
    parts = []
    body = P("chest_body", "chest")
    G.slab(body, CX0, CX1, CY0, CY1, ZB, ZG, rc=RCH, nc=nc, rb=0.008 if lod == 0 else 0.0, nb=2 if lod == 0 else 0,
           caps=(True, False))
    parts.append(body)
    pl = P("chest_plinth", "plinth")
    G.slab(pl, CX0 + 0.012, CX1 - 0.012, CY0 + 0.012, CY1 - 0.012, ZFOOT, ZB + 0.004, rc=RCH - 0.012, nc=nc,
           caps=(True, False))
    parts.append(pl)
    if lod == 0:
        # adjustable feet: heel, stud, nut
        ft = P("chest_feet", "plinth")
        for x in (CX0 + 0.07, CX1 - 0.07):
            for y in (CY0 + 0.07, CY1 - 0.07):
                G.lathe(ft, [(0.022, 0.0), (0.022, 0.006), (0.009, 0.011), (0.012, 0.018), (0.012, 0.025),
                             (0.007, ZFOOT + 0.002)], 6, (x, y, 0.0), "z")
        parts.append(ft)
    ld = P("chest_lid", "lid")
    G.slab(ld, CX0 - LIP, CX1 + LIP, CY0 - LIP, CY1 + LIP, ZG + 0.006, ZL, rc=RCH + LIP, nc=nc,
           re=(0.014, 0.012, 0.0)[lod], ne=(3, 1, 0)[lod], rb=0.003 if lod == 0 else 0.0, nb=1 if lod == 0 else 0)
    parts.append(ld)
    gs = P("chest_gasket", "gasket")
    G.slab(gs, CX0 + 0.003, CX1 - 0.003, CY0 + 0.003, CY1 - 0.003, ZG - 0.002, ZG + 0.008, rc=RCH - 0.003, nc=nc,
           caps=(False, False))
    parts.append(gs)
    # compressor grille on the right end: dark opening, frame, slanted louvres, screws
    gy0, gy1, gz0, gz1 = GRILLE
    gr = P("chest_grille", "grille")
    g.box(gr, CX1 - 0.002, CX1 + 0.002, gy0, gy1, gz0, gz1)
    parts.append(gr)
    fr = P("chest_grille_frame", "grille_frame")
    w, t = 0.014, 0.010
    g.box(fr, CX1, CX1 + t, gy0 - w, gy1 + w, gz1, gz1 + w)
    g.box(fr, CX1, CX1 + t, gy0 - w, gy1 + w, gz0 - w, gz0)
    g.box(fr, CX1, CX1 + t, gy0 - w, gy0, gz0, gz1)
    g.box(fr, CX1, CX1 + t, gy1, gy1 + w, gz0, gz1)
    if lod < 2:
        n = 9 if lod == 0 else 5
        for k in range(n):
            z = gz0 + 0.016 + (gz1 - gz0 - 0.032) * k / (n - 1)
            g.prism(fr, [(CX1 + 0.001, z + 0.011), (CX1 + 0.009, z + 0.004), (CX1 + 0.009, z - 0.001),
                         (CX1 + 0.001, z + 0.006)], (0, 2), gy0, gy1)
    parts.append(fr)
    if lod == 0:
        for y in (gy0 - w / 2, gy1 + w / 2):
            for z in (gz0 - w / 2, gz1 + w / 2):
                parts.append(screw("grille_screw", (CX1 + t + 0.0012, y, z), "x"))
    if lod < 2:
        # hinges at the back: leaves on the body and lid, pin
        hg = P("lid_hinges", "hinge")
        for x in (-0.50, 0.50):
            g.box(hg, x - 0.034, x + 0.034, CY1, CY1 + 0.003, ZG - 0.046, ZG - 0.004)
            g.box(hg, x - 0.034, x + 0.034, CY1 + LIP, CY1 + LIP + 0.003, ZG + 0.012, ZL - 0.016)
            g.cyl(hg, (x, CY1 + 0.011, ZG + 0.004), "x", 0.0075, 0.072, 10 if lod == 0 else 6)
        parts.append(hg)
    if lod == 0:
        for x in (-0.50, 0.50):
            parts.append(screw("hinge_screw", (x, CY1 + 0.0042, ZG - 0.025), "y", 0.004))
            parts.append(screw("hinge_screw", (x, CY1 + LIP + 0.0042, ZG + 0.032), "y", 0.004))
        # the handle is gone (a chain instead), the lock cylinder is
        # drilled out: holes in the lid and in the body above the leaf
        hl = P("chest_holes", "hole")
        for x in (-0.235, 0.235):
            for dz in (-0.010, 0.010):
                g.cyl(hl, (x, CY0 - LIP - 0.0003, 0.830 + dz), "y", 0.0032, 0.0012, 6)
        g.cyl(hl, (0.30, CY0 - 0.0003, ZG - 0.024), "y", 0.0105, 0.0012, 10)
        parts.append(hl)
    return parts


# =============================================================================
# Lead cladding, rivets
# =============================================================================
def build_cladding(spec):
    lod = spec["lod"]
    parts = []
    for name, reg, sh, (nu, nv), step in SHEETS:
        p = P(name, reg)
        if lod == 2:
            sh.plate(p)
        else:
            sh.build(p, *((nu, nv) if lod == 0 else (2, 2)))
        parts.append(p)
        if lod == 0:
            rv = P(name + "_rivets", "rivet")
            for c in sh.rivets(step):
                G.rivet(rv, c, sh.n, sides=6, dome=False)
            parts.append(rv)
    return parts


# =============================================================================
# Angles 40 x 40 x 4, welds
# =============================================================================
CORNERS = [((AX0, AY0), (1, 1), 0.035, 0.790), ((AX1, AY0), (-1, 1), 0.040, 0.784),
           ((AX0, AY1), (1, -1), 0.038, 0.786), ((AX1, AY1), (-1, -1), 0.035, 0.792)]


def build_angles(spec):
    """Angles on the vertical edges and along the bottom of the face and back; the near LOD has a section
    with a fillet, slanted cuts and rough bead welds where the leg lies on a sheet."""
    lod = spec["lod"]
    an = P("angles", "angle")
    sec = G.angle_section(AL, AT, AR, 3) if lod == 0 else [(0, 0), (AL, 0), (AL, AT), (AT, AT), (AT, AL), (0, AL)]
    for i, ((cx, cy), (sx, sy), z0, z1) in enumerate(CORNERS):
        def Pv(a, b, c, cx=cx, cy=cy, sx=sx, sy=sy):
            return Vector((cx + sx * a, cy + sy * b, c))
        cut = (0.10 * math.sin(i * 2.1), -0.08 * math.cos(i * 1.7)) if lod == 0 else (0.0, 0.0)
        G.angle_iron(an, sec, Pv, z0, z1, cut0=(0.0, 0.0), cut1=cut)
    # bottom of the face and back: one leg stands on the face over the
    # bottom edges of the sheets, the other goes under the chest
    for k, (y, s) in enumerate(((AYB0, 1), (AYB1, -1))):
        def Ph(a, b, c, y=y, s=s):
            return Vector((c, y + s * a, AZ + b))
        cut = (0.06, 0.04 * (1 if k else -1)) if lod == 0 else (0.0, 0.0)
        G.angle_iron(an, sec, Ph, AX0 + AL, AX1 - AL, cut0=cut, cut1=(-cut[0], cut[1]))
    parts = [an]
    if lod == 0:
        wd = P("welds", "weld")
        k = 0
        for (cx, cy), (sx, sy), z0, z1 in CORNERS:
            for z in ((z0 + 0.03, 0.42, z1 - 0.04) if cy < 0 else (z0 + 0.03, z1 - 0.04)):
                k += 1
                j = 0.004 * math.sin(k * 2.7)
                # end of the face leg: a weld vertically, from the leg edge to the sheet
                x = cx + sx * (AL + 0.002)
                y = cy + sy * (AT + 0.0035)
                G.weld(wd, (x, y, z - 0.016 + j), (x, y, z + 0.016 + j), 0.0040, k, 3, 4)
                # end of the end leg
                x = cx + sx * (AT + 0.0035)
                y = cy + sy * (AL + 0.002)
                G.weld(wd, (x, y, z - 0.014 - j), (x, y, z + 0.016 - j), 0.0040, k + 50, 3, 4)
        for y, s in ((AYB0, 1), (AYB1, -1)):
            for x in ((-0.55, -0.12, 0.31, 0.62) if s > 0 else (-0.40, 0.45)):
                k += 1
                G.weld(wd, (x - 0.022, y + s * (AT + 0.0008), AZ + AL + 0.0005),
                       (x + 0.022, y + s * (AT + 0.0008), AZ + AL + 0.0005), 0.0032, k, 3, 4)
        parts.append(wd)
    return parts


# =============================================================================
# Chain, lug, staple, padlock with keys
# =============================================================================
def chain_path():
    """Centre line of the chain for links lying flat: [(point, surface normal, free)] - from the link on the
    lock shackle up the face, over the lid, down the back to the staple. Free links (on the shackle, on the
    staple) hang unsupported: the ones standing on edge have no lift above the surface."""
    zt = lid_z(CHX, 0.0)
    rb = 0.014 + CH_D / 2                                    # bend over the rounded lid edge
    yf, yb = CY0 - LIP - CH_D / 2, CY1 + LIP + CH_D / 2
    zs = PL_ZT + 0.022 + PL_ARC * math.sin(math.acos(CHX / PL_ARC))   # rod of the shackle under the link
    hs = CH_L / 2 - CH_D / 2 - (CH_W / 2 - CH_D / 2)
    pts = [((CHX, PL_Y, zs + hs), (0, -1, 0), True),
           ((CHX, yf - 0.006, zs + hs + 0.050), (0, -1, 0), True),
           ((CHX, yf, ZG - 0.010), (0, -1, 0), False),
           ((CHX, yf, zt - 0.014), (0, -1, 0), False)]
    for k in range(1, 4):
        a = math.pi / 2 * k / 4
        pts.append(((CHX, CY0 - LIP + 0.014 - rb * math.cos(a), zt - 0.014 + rb * math.sin(a)),
                    (0, -math.cos(a), math.sin(a)), False))
    for y in (-0.326, -0.2, -0.1, 0.0, 0.1, 0.2, 0.326):
        pts.append(((CHX, y, lid_z(CHX, y) + CH_D / 2), (0, 0, 1), False))
    for k in range(1, 4):
        a = math.pi / 2 * k / 4
        pts.append(((CHX, CY1 + LIP - 0.014 + rb * math.sin(a), zt - 0.014 + rb * math.cos(a)),
                    (0, math.sin(a), math.cos(a)), False))
    hs_b = hs
    pts += [((CHX, yb, zt - 0.014), (0, 1, 0), False),
            ((CHX, yb, STAPLE_Z + hs_b + 0.050), (0, 1, 0), False),
            ((CHX, STAPLE_Y, STAPLE_Z + hs_b), (0, 1, 0), True)]
    return pts


def chain_links():
    """Links: (centre, along, across, on edge) - at equal steps, an even number of gaps: both end links
    stand on edge (their plane is across the axis of the shackle and the staple)."""
    path = chain_path()
    P_ = [Vector(p) for p, _, _ in path]
    seg = [(P_[i + 1] - P_[i]).length for i in range(len(P_) - 1)]
    total = sum(seg)
    n = max(2, int(round(total / CH_PITCH)))
    n += n % 2
    out, i, acc = [], 0, 0.0
    for k in range(n + 1):
        d = total * k / n
        while i < len(seg) - 1 and acc + seg[i] < d:
            acc += seg[i]
            i += 1
        t = min(max((d - acc) / max(seg[i], 1e-9), 0.0), 1.0)
        p = P_[i].lerp(P_[i + 1], t)
        nrm = Vector(path[i][1]).lerp(Vector(path[i + 1][1]), t).normalized()
        free = path[i][2] if t < 0.5 else path[i + 1][2]
        tan = (P_[i + 1] - P_[i]).normalized()
        edge = k % 2 == 0
        if edge:
            w = nrm - tan * nrm.dot(tan)
            c = p if free else p + nrm * (CH_W / 2 - CH_D / 2 - 0.001)
        else:
            w = tan.cross(nrm)
            c = p
        out.append((c, tan, w.normalized(), edge, p))
    return out


def build_chain(spec):
    lod = spec["lod"]
    parts = []
    if lod == 2:
        return parts
    ch = P("chain", "chain")
    links = chain_links()
    if lod == 0:
        for c, t, w, edge, p in links:
            G.chain_link(ch, c, t, w, CH_L, CH_W, CH_D, 12, 4)
    else:
        # middle LOD: the chain is a ribbon along the centre line
        g.sweep(ch, [tuple(p) for c, t, w, edge, p in links[::2]], (1, 0, 0), CH_D * 0.6, CH_W / 2 - 0.004)
    parts.append(ch)
    return parts


def build_eyes(spec):
    """Lug on the face - an 8 mm steel plate with a dia. 17 hole at the end, welded to the sheet; the staple
    on the back - a dia. 12 rod bent into a U, the legs welded."""
    lod = spec["lod"]
    parts = []
    ey = P("eye_plate", "eye")
    y0 = face_y("lead_f0", 0.0, EYE_Z) + 0.002
    yr = EYE_Y

    def outline(inset):
        r = 0.016 - inset
        pts = [(y0, EYE_Z - r), (yr, EYE_Z - r)]
        n = 6 if lod == 0 else 3
        for k in range(1, n):
            a = -math.pi / 2 - math.pi * k / n
            pts.append((yr + r * math.cos(a), EYE_Z + r * math.sin(a)))
        pts += [(yr, EYE_Z + r), (y0, EYE_Z + r)]
        return pts

    def Pp(a, b, c):
        return Vector((c, a, b))
    if lod == 0:
        G.chamfer_prism(ey, outline, -0.004, 0.004, 0.0008, Pp)
    else:
        G.loft(ey, [outline(0.0), outline(0.0)], [-0.004, 0.004], Pp)
    parts.append(ey)
    if lod < 2:
        # the hole (visible from the plate ends around the shackle) - dark circles on both sides
        hl = P("eye_hole", "hole")
        for s in (-1, 1):
            g.cyl(hl, (s * 0.0042, yr, EYE_Z), "x", 0.0085, 0.0004, 8 if lod == 0 else 6)
        parts.append(hl)
        st = P("staple", "eye")
        yb = face_y("lead_b1", CHX, STAPLE_Z) - 0.004
        pts = [(CHX - 0.026, yb, STAPLE_Z), (CHX - 0.026, STAPLE_Y - 0.008, STAPLE_Z),
               (CHX - 0.020, STAPLE_Y, STAPLE_Z), (CHX + 0.020, STAPLE_Y, STAPLE_Z),
               (CHX + 0.026, STAPLE_Y - 0.008, STAPLE_Z), (CHX + 0.026, yb, STAPLE_Z)]
        g.pipe(st, G.spline(pts, 2) if lod == 0 else pts, 0.006, 10 if lod == 0 else 4)
        parts.append(st)
    if lod == 0:
        wd = P("eye_welds", "weld")
        for s in (-1, 1):
            G.weld(wd, (s * 0.0055, y0 - 0.001, EYE_Z - 0.015), (s * 0.0055, y0 - 0.001, EYE_Z + 0.015), 0.003, 3 + s, 3, 4)
            G.weld(wd, (CHX + s * 0.026, yb + 0.003, STAPLE_Z - 0.010), (CHX + s * 0.026, yb + 0.003, STAPLE_Z + 0.010),
                   0.0045, 7 + s, 3, 4)
        parts.append(wd)
    return parts


def build_padlock(spec):
    """VS2M1 padlock on the face lug: cast body with rounded corners and a chamfer, a dia. 14 shackle
    through the lug hole and the last chain link, a keyhole with the cover swung aside, a key in it."""
    lod = spec["lod"]
    parts = []
    bd = P("padlock", "lock")
    z0, z1 = PL_ZT - PL_H, PL_ZT

    def outline(inset):
        return G.rrect(-PL_W / 2 + inset, PL_W / 2 - inset, z0 + inset, z1 - inset, max(0.012 - inset, 0.001),
                       (3, 1, 0)[lod])

    def Pp(a, b, c):
        return Vector((a, c, b))
    if lod == 0:
        G.chamfer_prism(bd, outline, PL_Y - PL_D / 2, PL_Y + PL_D / 2, 0.0028, Pp)
        # collar along the seam of the body
        G.loft(bd, [G.rrect(-PL_W / 2 - 0.0012, PL_W / 2 + 0.0012, z1 - 0.010, z1 - 0.004, 0.002, 1)] * 2,
               [PL_Y - PL_D / 2 + 0.006, PL_Y + PL_D / 2 - 0.006], lambda a, b, c: Vector((a, c, b)), caps=(False, False))
    else:
        G.loft(bd, [outline(0.0), outline(0.0)], [PL_Y - PL_D / 2, PL_Y + PL_D / 2], Pp)
    parts.append(bd)
    sh = P("padlock_shackle", "shackle")
    n = 9 if lod == 0 else 4
    arc = [(PL_ARC * math.cos(math.pi * k / n), PL_Y, PL_ZT + 0.022 + PL_ARC * math.sin(math.pi * k / n))
           for k in range(n + 1)]
    g.pipe(sh, [(PL_ARC, PL_Y, PL_ZT - 0.004)] + arc + [(-PL_ARC, PL_Y, PL_ZT - 0.004)], PL_SH, (10, 6, 4)[lod])
    parts.append(sh)
    if lod == 2:
        return parts
    yf = PL_Y - PL_D / 2
    kh = P("padlock_keyhole", "hole")
    g.box(kh, -0.0016, 0.0016, yf - 0.0004, yf + 0.001, KH_Z - 0.006, KH_Z + 0.004)
    parts.append(kh)
    if lod == 0:
        # keyhole cover swung aside on a rivet
        fl = P("padlock_flap", "lock")
        g.cyl(fl, (0.011, yf - 0.0009, KH_Z + 0.003), "y", 0.0085, 0.0016, 12)
        g.cyl(fl, (0.006, yf - 0.0019, KH_Z + 0.008), "y", 0.0024, 0.0012, 8)
        parts.append(fl)
        parts += build_keys(yf, KH_Z)
    return parts


def build_keys(yf, zk):
    """Key in the keyhole (shaft outward, ring head), two more keys on the ring: brass and steel, hanging,
    turned slightly toward the person."""
    st = P("keys_steel", "keysteel")
    br = P("keys_brass", "brass")
    yb = yf - 0.024                                         # head centre
    g.cyl(st, (0.0, yf - 0.003, zk), "y", 0.0036, 0.006, 8)                       # collar
    g.cyl(st, (0.0, (yf + yb) / 2 - 0.004, zk), "y", 0.0021, yf - yb - 0.008, 8)  # shaft
    G.torus(st, g.Frame((0.0, yb, zk), (0, 1, 0), (0, 0, 1), (1, 0, 0)), 0.0078, 0.0024, 10, 4)
    # ring in the plane of the face through the head
    rc, rr = Vector((0.0, yb, zk - 0.0115)), 0.0115
    G.torus(st, g.Frame(rc, (1, 0, 0), (0, 0, 1), (0, -1, 0)), rr, 0.0010, 12, 3)
    for part, ang, turn, L in ((br, 250.0, 35.0, 0.044), (st, 292.0, -30.0, 0.038)):
        a = math.radians(ang)
        top = rc + Vector((rr * math.cos(a), 0.0, rr * math.sin(a)))
        tr = math.radians(turn)
        side = Vector((math.cos(tr), -math.sin(tr), 0.0))                         # key plane: side, z
        c = top - Vector((0, 0, 0.0085 - 0.0021 - 0.0010))          # the ring rod is in the head hole
        G.torus(part, g.Frame(c, side, (0, 0, 1), side.cross(Vector((0, 0, 1)))), 0.0085, 0.0021, 8, 4)
        fr = g.Frame(c - Vector((0, 0, 0.0085)), side, (0, 0, -1), side.cross(Vector((0, 0, -1))))
        g.box(part, -0.0035, 0.0035, 0.0, 0.004, -0.0012, 0.0012, frame=fr)        # neck
        g.box(part, -0.0016, 0.0016, 0.004, L - 0.012, -0.0010, 0.0010, frame=fr)  # shaft
        g.box(part, 0.0016, 0.0080, L - 0.022, L - 0.010, -0.0010, 0.0010, frame=fr)  # bit
        g.box(part, 0.0016, 0.0050, L - 0.016, L - 0.013, -0.0012, 0.0012, frame=fr)  # bit notch (tooth)
    return [st, br]


# =============================================================================
# Loot: money, cards, packs, pager, knife, watches and chains, cigarette butts
# =============================================================================
def build_cash(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    bd = P("cash_bands", "band") if lod == 0 else None
    for nm, (cx, cy), deg, dz, t in loot.CASH:
        w, h = loot.note_size(nm)
        p = P(nm, nm)
        base = lid_z(cx, cy) + dz
        if lod == 0:
            # a bundle is three layers knocked off by a millimetre or two: the note edges are not in line
            for k, (du, dv, dd) in enumerate(((0.0, 0.0, 0.0), (0.0016, -0.0010, 1.2), (-0.0010, 0.0012, -0.8))):
                fr = G.frame_z(cx + du, cy + dv, deg + dd, base + t * k / 3)
                if k < 2:
                    g.box(p, -w / 2, w / 2, -h / 2, h / 2, 0.0, t / 3, frame=fr)
                else:
                    G.slab(p, -w / 2, w / 2, -h / 2, h / 2, 0.0, t / 3, rc=0.0015, nc=1, re=0.0006, ne=1, frame=fr,
                           caps=(False, True))
            fr = G.frame_z(cx, cy, deg, base)
            for off in (-0.035, 0.040):
                e = 0.0007
                loop = [fr.p(off, -h / 2 - e, -e), fr.p(off, h / 2 + e, -e), fr.p(off, h / 2 + e, t + e),
                        fr.p(off, -h / 2 - e, t + e)]
                g.sweep(bd, loop, tuple(fr.u), 0.0007, 0.0035, closed=True)
        else:
            g.box(p, -w / 2, w / 2, -h / 2, h / 2, 0.0, t, frame=G.frame_z(cx, cy, deg, base))
        parts.append(p)
    if bd is not None:
        parts.append(bd)
    if lod == 0:
        for nm, (cx, cy), deg, dz in loot.NOTES:
            w, h = loot.note_size(nm)
            p = P(nm, nm)
            g.box(p, -w / 2, w / 2, -h / 2, h / 2, 0.0, loot.NOTE_T, frame=G.frame_z(cx, cy, deg, lid_z(cx, cy) + dz))
            parts.append(p)
    return parts


def build_cards(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    cw, ch = loot.CARD
    nm, (cx, cy), deg, dz, t = loot.DECK
    dk = P(nm, nm)
    fr = G.frame_z(cx, cy, deg, lid_z(cx, cy) + dz)
    if lod == 0:
        G.slab(dk, -cw / 2, cw / 2, -ch / 2, ch / 2, 0.0, t, rc=0.003, nc=2, re=0.0008, ne=1, frame=fr)
    else:
        g.box(dk, -cw / 2, cw / 2, -ch / 2, ch / 2, 0.0, t, frame=fr)
    parts.append(dk)
    if lod == 0:
        for nm, (cx, cy), deg, dz, code in loot.FAN:
            p = P(nm, nm)
            G.slab(p, -cw / 2, cw / 2, -ch / 2, ch / 2, 0.0, loot.CARD_T, rc=0.003, nc=2,
                   frame=G.frame_z(cx, cy, deg, lid_z(cx, cy) + dz))
            parts.append(p)
    return parts


def cig_pack(part, fr, L, W, H):
    """A "Chernomorka" pack lying face up in frame fr (u along the pack, v across, n up): a box, each face
    has its UV on its own piece of the vanilla texture (CIGS_UV); the top of the face picture is toward +u
    (from M16)."""
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
    for corners, nrm, rect, st in sides:
        vs = [bm.verts.new(fr.p(*q)) for q in corners]
        loc = {v: q for v, q in zip(vs, corners)}
        f = G.face(part, vs, fr.u * nrm[0] + fr.v * nrm[1] + fr.n * nrm[2])
        x0, x1, y0, y1 = CIGS_UV[rect]
        for lp in f.loops:
            s, t = st(*loc[lp.vert])
            lp[uvl].uv = (x0 + (x1 - x0) * s, 1.0 - (y1 - (y1 - y0) * t))


def build_cigs(spec):
    """A "Chernomorka" carton: lower layer - 5 packs, upper - 4 (one taken out, it lies beside)."""
    lod = spec["lod"]
    if lod == 2:
        return []
    pk = P("packs", "carton", section="cigs")
    pk.fixed_uv = True
    pk.bm.loops.layers.uv.new("UVMap")
    L, W, H = loot.PACK
    (bx, by), bdeg = loot.BLOCK
    a = math.radians(bdeg)
    e1, e2 = Vector((math.cos(a), math.sin(a), 0.0)), Vector((-math.sin(a), math.cos(a), 0.0))
    z0 = max(lid_z(bx + s1 * 0.14, by + s2 * 0.045) for s1 in (-1, 1) for s2 in (-1, 1))
    for layer, count in ((0, 5), (1, 4)):
        for k in range(count):
            c = Vector((bx, by, z0 + layer * H)) + e1 * ((k - 2) * W) + e1 * (0.0006 * math.sin(k * 3.1 + layer))
            cig_pack(pk, g.Frame(c, e2, -e1, (0, 0, 1)), L, W, H)
    (lx, ly), ldeg = loot.LOOSE_PACK
    cig_pack(pk, G.frame_z(lx, ly, ldeg, lid_z(lx, ly)), L, W, H)
    return [pk]


def build_pager(spec):
    """Digital pager (like the Motorola Bravo) on scattered notes, face up, on a clip: rounded body,
    recessed screen window (ozl_screen - own texture with frames), three buttons, LED (ozl_lamp)."""
    lod = spec["lod"]
    if lod == 2:
        return []
    (cx, cy), deg = loot.PAGER
    L, W, H = loot.PAGER_SIZE
    under = max(dz for _, _, _, dz in loot.NOTES) + loot.NOTE_T
    base = lid_z(cx, cy) + under + 0.003
    fr = G.frame_z(cx, cy, deg, base)
    parts = []
    body = P("pager", "pager")
    if lod == 0:
        G.slab(body, -L / 2, L / 2, -W / 2, W / 2, 0.0, H, rc=0.007, nc=2, re=0.004, ne=2, rb=0.002, nb=1, frame=fr)
        g.box(body, -0.016, 0.022, -0.016, 0.016, -0.003, 0.0, frame=fr)                     # clip
    else:
        g.box(body, -L / 2, L / 2, -W / 2, W / 2, -0.003, H, frame=fr)
    parts.append(body)
    (su, sv), (sw, sh) = loot.PAGER_SCREEN
    bz = P("pager_bezel", "pager_bezel")
    G.slab(bz, su - sw / 2 - 0.0025, su + sw / 2 + 0.0025, sv - sh / 2 - 0.0025, sv + sh / 2 + 0.0025, H - 0.0006,
           H + 0.0005, rc=0.0015, nc=1 if lod == 0 else 0, frame=fr, caps=(False, True))
    parts.append(bz)
    sc = P("pager_screen", "pager_bezel", section="screen", group=SEL_SCREEN)
    vs = [sc.bm.verts.new(fr.p(a, b, H + 0.0007)) for a, b in ((su - sw / 2, sv - sh / 2), (su + sw / 2, sv - sh / 2),
                                                               (su + sw / 2, sv + sh / 2), (su - sw / 2, sv + sh / 2))]
    G.face(sc, vs, fr.n)
    sc.glass_frame = (g.Frame(fr.p(su - sw / 2, sv - sh / 2, 0.0), fr.u, fr.v, fr.n), 0.0, sw, 0.0, sh)
    parts.append(sc)
    ld = P("pager_led", "led", group=SEL_LAMP)
    G.lathe(ld, [(0.0019, 0.0), (0.0017, 0.0008), (0.0, 0.0013)], 8 if lod == 0 else 4,
            fr.p(-L / 2 + 0.0075, W / 2 - 0.0070, H - 0.0002), tuple(fr.n))
    parts.append(ld)
    if lod == 0:
        ks = P("pager_keys", "pager_key")
        for k in (-1, 0, 1):
            G.slab(ks, k * 0.0125 - 0.0045, k * 0.0125 + 0.0045, -W / 2 + 0.0045, -W / 2 + 0.0105, H - 0.0003,
                   H + 0.0014, rc=0.0016, nc=1, re=0.0006, ne=1, frame=fr, caps=(False, True))
        parts.append(ks)
    return parts


def build_knife(spec):
    """Folded butterfly knife lying flat: two handles (steel, a black scale on top), a strip of blade
    visible between them, two pivots at the blade end, a latch bracket at the other end."""
    lod = spec["lod"]
    if lod == 2:
        return []
    (cx, cy), deg = loot.KNIFE
    fr = G.frame_z(cx, cy, deg, lid_z(cx, cy))
    hd = P("knife", "knife_steel")
    if lod > 0:
        g.box(hd, -0.064, 0.064, -0.0125, 0.0125, 0.0, 0.012, frame=fr)
        return [hd]
    for z0, z1 in ((0.0, 0.0052), (0.0068, 0.0120)):
        G.slab(hd, -0.064, 0.064, -0.0125, 0.0125, z0, z1, rc=0.005, nc=2, re=0.0012, ne=1, rb=0.0008, nb=1, frame=fr)
    bl = P("knife_blade", "blade")
    G.slab(bl, -0.056, 0.060, -0.0108, 0.0105, 0.0050, 0.0070, rc=0.004, nc=1, frame=fr, caps=(False, False))
    # the scale is three inserts with steel between them (handle cutouts)
    il = P("knife_inlay", "knife_inlay")
    for a0, a1 in ((-0.052, -0.022), (-0.017, 0.012), (0.017, 0.044)):
        G.slab(il, a0, a1, -0.0088, 0.0088, 0.0118, 0.0127, rc=0.004, nc=2, re=0.0004, ne=1, frame=fr,
               caps=(False, True))
    pn = P("knife_pins", "knife_pin")
    for u, v in ((0.056, -0.0055), (0.056, 0.0055), (0.049, 0.0)):
        g.cyl(pn, (u, v, 0.0125), "z", 0.0021, 0.0012, 6, frame=fr)
    latch = [(-0.054, -0.0068, 0.0124), (-0.064, -0.0068, 0.0124), (-0.0685, -0.004, 0.0118), (-0.0685, 0.004, 0.0118),
             (-0.064, 0.0068, 0.0124), (-0.054, 0.0068, 0.0124)]
    g.pipe(pn, [tuple(fr.p(*q)) for q in latch], 0.0011, 5)
    g.cyl(pn, (-0.054, 0.0, 0.0124), "y", 0.0012, 0.016, 6, frame=fr)
    return [hd, bl, il, pn]


def build_watches(spec):
    """Heap of wristwatches (WATCH_GEO): case with a rim, dial (decal), lugs, crown, a bracelet or strap in
    two halves - they lie on their neighbours; a watch without a bracelet lies tilted on neighbouring ones;
    chains on top, rings beside."""
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    sides = 12 if lod == 0 else 6
    for w in WATCH_GEO:
        o, u, v, n = watch_frame(w)
        r, h = w["r"], w["h"]
        metal = "w_gold" if w["strap"] == "gold" else "w_steel"
        cs = P("case_" + w["name"], metal)
        if lod == 0:
            prof = [(0.84 * r, 0.0), (r, 0.0016), (r, 0.66 * h), (0.90 * r, h), (0.80 * r, h - 0.0012)]
            G.lathe(cs, prof, sides, o, tuple(n), caps=(bool(w["tilt"]), False), ab=(u, v))
        else:
            G.lathe(cs, [(r, 0.0), (r, h - 0.0012), (0.80 * r, h - 0.0012)], sides, o, tuple(n), ab=(u, v))
        dl = P("dial_" + w["name"], "dial_" + w["name"])
        G.lathe(dl, [(0.80 * r, h - 0.0012), (0.0, h - 0.0012)], sides, o, tuple(n), ab=(u, v))
        parts += [cs, dl]
        if lod == 0:
            fr = g.Frame(o, u, v, n)
            sw = w.get("sw", 0.018)
            for s in (-1, 1):
                for q in (-1, 1):
                    a0, a1 = sorted((s * 0.80 * r, s * (r + 0.0045)))
                    b0, b1 = sorted((q * (sw / 2 - 0.0025), q * (sw / 2 + 0.0008)))
                    g.box(cs, a0, a1, b0, b1, 0.0012, 0.60 * h, frame=fr)
            g.cyl(cs, (0.0, -(r + 0.0016), 0.48 * h), "y", 0.0024, 0.0032, 6, frame=fr)            # crown
        if w["strap"] and lod == 0:
            sp = P("strap_" + w["name"], "leather" if w["strap"] == "leather" else metal)
            for k, pts in enumerate(w["straps"]):
                wp = [(x, y, lid_z(x, y) + z) for x, y, z in pts]
                g.sweep(sp, wp, tuple(v), w["st"] / 2, w["sw"] / 2)
                if w["strap"] == "leather" and k == 1:
                    # buckle at the end
                    x, y, z = wp[-1]
                    g.box(sp, -0.004, 0.004, -w["sw"] / 2 - 0.0018, w["sw"] / 2 + 0.0018, -w["st"] / 2,
                          w["st"] / 2 + 0.0016, frame=g.Frame((x, y, z), u, v, (0, 0, 1)))
                elif w["strap"] != "leather" and k == 1:
                    # bracelet clasp
                    x, y, z = wp[len(wp) // 2]
                    g.box(sp, -0.010, 0.010, -w["sw"] / 2, w["sw"] / 2, -w["st"] / 2, w["st"] / 2 + 0.0012,
                          frame=g.Frame((x, y, z), u, v, (0, 0, 1)))
            parts.append(sp)
        elif w["strap"]:
            sp = P("strap_" + w["name"], "leather" if w["strap"] == "leather" else metal)
            for pts in w["straps"]:
                x0, y0, _ = pts[0]
                x1, y1, z1 = pts[-1]
                g.sweep(sp, [(x0, y0, lid_z(x0, y0) + pts[0][2]), (x1, y1, lid_z(x1, y1) + z1)], tuple(v),
                        w["st"] / 2, w["sw"] / 2)
            parts.append(sp)
    if lod == 0:
        gd = P("gold_chains", "gold")
        for pts in CHAIN_GEO:
            g.pipe(gd, [(x, y, lid_z(x, y) + z) for x, y, z in pts], 0.0012, 3)
        for (x, y), R, stone in loot.RINGS:
            z = lid_z(x, y) + heap_rel(x, y) + 0.0017
            G.torus(gd, g.Frame((x, y, z), (1, 0, 0), (0, 1, 0), (0, 0, 1)), R, 0.0017, 10, 4)
            if stone:
                stp = P("ring_stone", "stone")
                G.lathe(stp, [(0.0036, 0.0), (0.0030, 0.0016), (0.0, 0.0028)], 8, (x + R, y, z + 0.0008), "z")
                parts.append(stp)
        parts.append(gd)
    return parts


def build_butts(spec):
    """Cigarette butts: filter, the rest of the cigarette, the burnt end."""
    if spec["lod"] > 0:
        return []
    fl, pa, ash = P("butt_filters", "filter"), P("butt_paper", "paper"), P("butt_ash", "ash")
    r = 0.0039
    for (cx, cy), deg, L in loot.BUTTS:
        fr = G.frame_z(cx, cy, deg, lid_z(cx, cy))
        g.cyl(fl, (-L / 2 + 0.010, 0.0, r), "x", r, 0.020, 10, frame=fr)
        rest = L - 0.020
        g.cyl(pa, (-L / 2 + 0.020 + (rest - 0.002) / 2, 0.0, r), "x", r * 0.98, rest - 0.002, 10, frame=fr, cap=False)
        g.cyl(ash, (L / 2 - 0.001, 0.0, r * 0.95), "x", r * 0.9, 0.002, 6, r2=r * 0.55, frame=fr)
    return [fl, pa, ash]


def build_lod(spec):
    parts = build_chest(spec) + build_cladding(spec) + build_angles(spec) + build_chain(spec) + build_eyes(spec)
    parts += build_padlock(spec) + build_cash(spec) + build_cards(spec) + build_cigs(spec) + build_pager(spec)
    parts += build_knife(spec) + build_watches(spec) + build_butts(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


# =============================================================================
# Layout check (--stats): vanilla items, modules and loot do not intersect
# =============================================================================
def rect_box(name, cx, cy, deg, w, h, z0, z1, group=None):
    bw, bh = rot_box(w, h, deg)
    return (name, group or name, (cx - bw / 2, cy - bh / 2, z0), (cx + bw / 2, cy + bh / 2, z1))


def check_layout():
    boxes = []
    for d in DECOR:
        q = kv.corners(d[5], d[1], d[2], d[3])
        boxes.append((str(d[5]).split("\\")[-1], "decor%d" % len(boxes), tuple(min(p[i] for p in q) for i in range(3)),
                      tuple(max(p[i] for p in q) for i in range(3))))
    for (o, _), m, (lo, hi) in zip(MOD_OBJ, MODS, MOD_BOX):
        boxes.append((o, o, tuple(m[i] + lo[i] for i in range(3)), tuple(m[i] + hi[i] for i in range(3))))
    zl = ZL + T
    for nm, (cx, cy), deg, dz, t in loot.CASH:
        boxes.append(rect_box(nm, cx, cy, deg, *loot.note_size(nm), zl + dz, zl + dz + t, "cash"))
    for nm, (cx, cy), deg, dz in loot.NOTES:
        boxes.append(rect_box(nm, cx, cy, deg, *loot.note_size(nm), zl + dz, zl + dz + 0.001, "pager"))
    nm, (cx, cy), deg, dz, t = loot.DECK
    boxes.append(rect_box(nm, cx, cy, deg, *loot.CARD, zl, zl + t))
    for nm, (cx, cy), deg, dz, code in loot.FAN:
        boxes.append(rect_box(nm, cx, cy, deg, *loot.CARD, zl + dz, zl + dz + 0.001, "fan"))
    (bx, by), bdeg = loot.BLOCK
    boxes.append(rect_box("packs", bx, by, bdeg, 5 * loot.PACK[1], loot.PACK[0], zl, zl + 0.044))
    (lx, ly), ldeg = loot.LOOSE_PACK
    boxes.append(rect_box("pack", lx, ly, ldeg, loot.PACK[0], loot.PACK[1], zl, zl + 0.022))
    (px, py), pdeg = loot.PAGER
    boxes.append(rect_box("pager", px, py, pdeg, loot.PAGER_SIZE[0], loot.PAGER_SIZE[1], zl + 0.002, zl + 0.02, "pager"))
    (kx_, ky), kdeg = loot.KNIFE
    boxes.append(rect_box("knife", kx_, ky, kdeg, 0.138, 0.025, zl, zl + 0.013))
    hx = [x for x, y, r, h in HEAP]
    hy = [y for x, y, r, h in HEAP]
    boxes.append(("watches", "watches", (min(hx) - 0.01, min(hy) - 0.01, zl), (max(hx) + 0.01, max(hy) + 0.01, zl + 0.02)))
    for (cx, cy), deg, L in loot.BUTTS:
        boxes.append(rect_box("butt", cx, cy, deg, L, 0.008, zl, zl + 0.008, "butt%.3f" % cx))
    for n, gr, lo, hi in boxes:
        print("layout: %-16s x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f" % (n, lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if a[1] == b[1]:
                continue
            if all(a[2][k] < b[3][k] - 0.002 and b[2][k] < a[3][k] - 0.002 for k in range(3)):
                print("layout: OVERLAP %s / %s" % (a[0], b[0]))
    # lid edges: the rivets along the sheet contour are 22 mm from the edge
    for n, gr, lo, hi in boxes:
        if lo[0] < CX0 + 0.020 or hi[0] > CX1 - 0.020 or lo[1] < CY0 + 0.018 or hi[1] > CY1 - 0.018:
            print("layout: EDGE %s (rivets along the lid edge)" % n)


def collision():
    metal = kx.PEN + r"\metalplate.rvmat"
    chest = kx.box_pts(AX0, AX1, AY0 - 0.06, AY1 + 0.04, 0.0, ZL + 2 * T)
    comps = [(chest, metal)]
    memory = {
        "invView": [(0.0, -2.8, 1.1)],
        "ce_center": [(0.0, 0.0, 0.6)],
        "ce_radius": [(1.0, 0.0, 0.6)],
    }
    for i, m in enumerate(MODS):
        memory["module_%d" % (i + 1)] = [m]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 260.0, memory, bbox


# the first ones are for the --look preview: overview, the lid with the modules in place (also empty), the
# loot with the pager (also in "work"), the lock with the chain, the watch heap; then the end, the back,
# the left half of the lid
SHOTS = [
    ("front", (-1.30, -2.70, 1.75), (0.0, 0.0, 0.66), 30),
    ("lid", (0.0, -1.35, 1.90), (0.0, -0.02, 0.88), 30),
    ("loot", (0.62, -0.80, 1.30), (0.44, -0.04, 0.89), 34),
    ("padlock", (0.30, -0.95, 0.92), (0.0, -0.37, 0.70), 35),
    ("watches", (0.30, -0.40, 1.10), (0.25, 0.02, 0.875), 42),
    ("slots_left", (-0.75, -0.95, 1.42), (-0.42, -0.02, 0.89), 34),
    ("right", (2.2, -1.3, 1.35), (0.4, 0.0, 0.5), 30),
    ("back", (1.4, 2.8, 1.7), (0.0, 0.0, 0.6), 30),
]

if "--stats" in sys.argv:
    check_layout()
M.look_shots = (5, 3)
M.run(build_lod, collision, SHOTS, row_step=2.0, row_shot=((2.0, -7.0, 1.8), (2.0, 0, 0.6)))
