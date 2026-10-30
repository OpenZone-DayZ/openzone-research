"""M26 - armor plate shooting stand: Protection Sample Analyzer of Duty (OZL_Dty_Proc_Prot).
An analyzer: 4x4 cargo, no modules (no module_1..3 points, as in M06, M21, M24).

    blender --background --python build_m26.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (the display "off" and the "working"
frames, hit circles, a measuring scale, the indicator scale, unit marks, a tag). The positions of the
plate, the hits and the unit face are in layout26.py (shared with the decals), the primitives that
kgeo does not have are in m26_geo.py.

Composition: ~1.2 x 1.6 x 1.0 m (W x H x D). A welded frame of 50 x 5 angle iron on two skids; in the
frame window an armor plate 0.25 x 0.30 with dents stands on a shelf, pressed against two vertical
straps by four clamps. At the back, on a stand of 40 x 40 tube, a wooden bullet-trap box with sand,
on its face a plywood shield with holes, under the box a shelf of boards. In front on a post two
closed speed sensor frames, their cables run along the post and under the skids to the registration
unit with a display, which stands on a board on top of the box. The shooter is in front (at -Y), the
bullet flies through the frames into the plate and on into the sand.

References:
- a stand for shooting armor samples (US 5899432, 1999, fig. 1): two posts on a base, a lower
  clamping bar, an upper frame, the sample is held by clamps. No photo of a real frame is available;
- the plate is 0.25 x 0.30, between sizes S (222 x 298 mm) and M (241 x 318 mm) of SAPI/ESAPI plates;
  the 8 mm thickness is as for steel plates (an estimate). The dents follow a photo of a shot steel
  plate (VOP-026): a bowl, around it lead splashes and chipped paint; they are relief in the bake
  (_nohq), not geometry;
- the angle iron of the frame and skids is GOST 8509: 50 x 5, fillet radius 5.5 mm, leg tip rounding
  1.8 mm; the box stand is 40 x 40 tube, 40 x 4 angle, the shelf is 30 x 3 angle and boards;
- the clamps are G-clamps for 100 mm (like GOST 20376, estimated from the drawing): a cast frame, a
  threaded boss, a screw with a swivel foot and a tommy bar with balls at the ends; the thread is a
  drawn pattern;
- the bullet trap is like the "clay box" for shooting body armor, 24 x 24 x 5.5 inches
  (0.61 x 0.61 x 0.14 m), but with sand and deeper - 0.80 x 0.40 x 0.78 m (an estimate), so that a
  bullet that pierced the plate gets stuck; in the sand are pits and several flattened bullets;
- the sensor frames are closed, like velocity frames at a test station (a wartime photo; a two-screen
  scheme - NBSIR 84-2884, fig. 2): a 35 x 35 tube with rounded edges, base 0.23 m (an estimate).
  They do not repeat the Oehler U-frames of M24 or the Skyscreens on the rail of M28: here a closed
  frame on a post bracket, a ready lamp on top, strips of emitters inside. The 0.35 x 0.35 opening
  is wider than the plate so that it can be seen from the front;
- the registration unit is an army instrument of the 1980s: a metal case 0.28 x 0.18 x 0.12 on
  rubber feet, a vacuum fluorescent display (turquoise; M24 has red LEDs), a needle level indicator
  of the frame signal (like the M4200 on army instruments, an estimate), two channel toggles in
  guards, a threshold knob with a scale ring, a mains lamp, a carrying handle, bayonet connectors
  at the back.

Duty: the steel of the frame and skids is unpainted and rust-free, dark scale, scratched all over,
with traces of misses, sandy at the bottom; the box, the unit and the post are black with red (a
stripe on the box, the unit sides), no olive; paint worn down to metal (on the box, down to wood)
on the edges, at the handles, on the tommy bars and clamp frames. The build_worn builder is from the
M24 generator (where the reason is given), here extended with dents (hits) and board seams (planks).

Detail: the "dayz" look; angle irons with fillets and chamfers, welds, cast clamp frames with
roundings, frames and a post of rounded tube, bolts with washers, smooth cables with connectors and
ties. The small stuff is vanilla items as proxies (kvanilla): on the board by the unit a sheet with
a pen, a pack and loose 7.62 x 39 cartridges; on the shelf under the box an army ammo crate, rags, a
wrench and tape on a stack of spare plates; a sapper shovel leaned against the box (for digging
bullets out of the sand).

Working look: the display is ozl_screen, its own texture (section screen): "off" - a dark filter,
"working" - the frames screen_fNN (OZL_WorkFx frames); the frame ready lamps are ozl_lamp (_on atlas,
blink); the mains lamp and the backlight of the indicator scale are ozl_power (_on atlas, steady);
the indicator needle is the bone ozl_meter on its own source (wobble).

Blender axes: X is width, Y is depth (the face looks to -Y), Z is up.
"""
import math
import os
import sys

import bmesh
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kconsole as kc  # noqa: E402
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import krender  # noqa: E402
import kvanilla as kv  # noqa: E402
import kwood  # noqa: E402
import layout26 as lay  # noqa: E402
import m26_geo as G  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
A, T = 0.05, 0.005                                  # angle 50 x 5
# skids: axes along x, length along y, height; crosspieces (y) - the sensor post, the frame, the box legs
SKX, SKW, SKY, SKH = 0.55, 0.06, 0.50, 0.08
CROSS = (-0.285, 0.0475, 0.116, 0.484)
ZC = SKH + 0.005                                    # top of the crosspiece shelf
# frame: posts on the crosspiece, angle faces at FY, crossbars (bottom, top), a tie, the window
UX = SKX                                            # post axes
FY = lay.FY
ZTOP = 1.36
BASE_T = 0.008                                      # post heel
LOW = (0.80, 0.84)                                  # lower crossbar of the window
TOP = (1.30, ZTOP)                                  # upper crossbar
ZST = TOP[1] - A                                    # top of the posts - under the shelf of the upper crossbar
TIE = (0.40, 0.44)                                  # lower tie
FLAT_X = (0.11, 0.16)                               # vertical straps the plate is pressed against
FLAT_Y = (lay.PY1, lay.PY1 + 0.012)
FLAT_Z = (LOW[0] + 0.012, TOP[1] - 0.012)           # the straps lie on the faces of the crossbars
SHELF_Z = lay.PZ0                                   # shelf under the plate
CLAMP_Z = (0.96, 1.14)                              # clamps
SCREW_X = 0.115
CLAMP_T = 0.022                                     # clamp frame thickness
T_BAR = (70.0, 112.0, 20.0, 158.0)                  # tommy bar of each clamp - the angle from +x in the x-z plane
BRACE = (0.75, -0.42)                               # brace: from the post at height z to the skids at y
# bullet trap: a box on a stand, sand, a board on top at the back, a shield on the face
BX, BY0, BY1, BZ0, BZ1 = 0.40, 0.10, 0.50, 0.66, 1.44
WALL = 0.025
SAND_Z = 1.40
LID_Y0, LID_T = 0.27, 0.025
LID_TOP = BZ1 + LID_T
BACKER = (-0.20, 0.20, 0.85, 1.25)
STRIPE = (1.32, 1.38)                               # red stripe on the box
# stand: legs - 40 x 40 tube, strapping - 40 x 4 angle, shelf - 30 x 3 angle and boards
SA, ST = 0.04, 0.004
LEG_X, LEG_Y = 0.379, (0.116, 0.484)
LEG_TOP = BZ0 - ST
RAIL_Z = 0.36                                       # top of the shelf angles
SHELF_TOP = RAIL_Z + 0.02                           # top of the shelf boards
SPARE = ((0.180, 0.300, 8.0), (0.172, 0.296, -5.0))  # spare plates on the shelf: center, rotation
# sensor frames: y axes, half-width, bottom, top, profile, thickness
SENS_Y = (-0.40, -0.17)
SHW, SZ0, SZ1, SPW, STH = 0.21, 0.85, 1.25, 0.035, 0.035
BAR_X, BAR_Z = (0.235, 0.265), (1.035, 1.065)       # bracket along y
POST_X, POST_Y = (0.265, 0.305), (-0.305, -0.265)   # post 40 x 40
POST_C = ((POST_X[0] + POST_X[1]) / 2, (POST_Y[0] + POST_Y[1]) / 2)
POST_TOP = 1.09
# registration unit on rubber feet
UX0, UX1 = lay.UNIT_A
UY0, UY1 = 0.31, 0.49
UZ0 = LID_TOP + 0.005
UZ1 = UZ0 + 0.12
UFR = g.Frame((0, UY0, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0))      # unit face: a = x, b = z
DISP = (lay.DISP[0], lay.DISP[1], UZ0 + lay.DISP[2], UZ0 + lay.DISP[3])
CONN_X = (0.15, 0.22)                               # frame connectors on the back wall
CONN_Z = UZ0 + 0.045
# needle indicator: window, needle pivot, dial and needle planes
MW = (lay.METER_WIN[0], lay.METER_WIN[1], UZ0 + lay.METER_WIN[2], UZ0 + lay.METER_WIN[3])
PIVOT = (lay.METER_PIVOT[0], UZ0 + lay.METER_PIVOT[1])
C_DIAL, C_NEEDLE = 0.0016, 0.0024                   # from the unit face outward
METER_SPAN = math.radians(lay.METER_SWEEP)
METER_MID, METER_AMP = 0.62, 0.08                   # needle when "working": wobble mid +- amp
# Needle axis - memory points (collision below). The engine rotates a bone right-handed in DayZ axes
# (kexport.conv, determinant -1); in Blender axes this is left-handed about the axis from the first
# point to the second: the axis looks at the person - a positive angle is clockwise for him (as in
# M08, M12, M14, M33 - their needles go right in the game). The axis must not point from the unit
# face inward (+y): the needle would then go counterclockwise in the game, past zero and past the
# scale. So it goes from the pivot toward the person (-y).
METER_AXIS = [(PIVOT[0], UY0 - C_NEEDLE, PIVOT[1]), (PIVOT[0], UY0 - C_NEEDLE - 0.05, PIVOT[1])]

LOD_SPECS = [
    dict(lod=0, bev=1, sides=16),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "frame": ("frame", 1.0), "skid": ("skid", 0.7), "plate": ("plate", 4.0), "spare": ("spare", 1.6),
    "clamp": ("clamp", 1.6), "screw": ("screw", 1.6), "thread": ("thread", 2.0), "weld": ("weld", 2.0),
    "crate": ("crate", 0.6), "crate_steel": ("crate_steel", 0.8), "backer": ("backer", 1.6),
    "sand": ("sand", 1.0), "board": ("board", 0.8), "bullet": ("bullet", 4.0),
    "unit": ("unit", 1.4), "unit_red": ("unit_red", 1.2), "bezel": ("bezel", 2.5), "dial": ("dial", 6.0),
    "needle": ("needle", 4.0), "chrome": ("chrome", 3.0), "dark": ("dark", 2.0),
    "lamp_g": ("lamp_g_off", 1.6), "lamp_r": ("lamp_r_off", 1.6), "sensor": ("sensor", 1.0), "lens": ("lens", 1.5),
    "post": ("post", 0.8), "steel": ("steel", 1.0), "black": ("black", 1.0), "rubber": ("rubber", 0.4),
    "cable": ("cable", 0.8), "tag": ("tag", 4.0),
}


# =============================================================================
# Materials
# =============================================================================
def near3(t, pos, c, r):
    """|(pos - c) / r| - the distance in fractions of the ellipsoid semi-axes."""
    d = t.node("ShaderNodeVectorMath")
    d.operation = "SUBTRACT"
    t.link(pos, d.inputs[0])
    d.inputs[1].default_value = c
    q = t.node("ShaderNodeVectorMath")
    q.operation = "DIVIDE"
    t.link(d.outputs[0], q.inputs[0])
    q.inputs[1].default_value = r
    ln = t.node("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    t.link(q.outputs[0], ln.inputs[0])
    return ln.outputs["Value"]


def hit_masks(t, pos, hits):
    """Dents [(center, splash semi-axes, through)]: a bowl up to 0.29 of the semi-axis, a ridge along its
    edge, splashes up to 1, a dark middle (a pierced one has a wider hole). Returns (bowl, ridge,
    splashes, middle)."""
    acc = [None, None, None, None]
    for c, r, pierced in hits:
        d = near3(t, pos, c, r)
        m = [t.maprange(d, 0.20, 0.30, 1.0, 0.0),
             t.math("MULTIPLY", t.maprange(d, 0.24, 0.32, 0.0, 1.0), t.maprange(d, 0.32, 0.46, 1.0, 0.0)),
             t.maprange(d, 0.30, 1.0, 1.0, 0.0),
             t.maprange(d, 0.04, 0.13 if pierced else 0.08, 1.0 if pierced else 0.7, 0.0)]
        acc = [x if a is None else t.math("MAXIMUM", a, x) for a, x in zip(acc, m)]
    return acc


HIT_METAL = (kmats.lin((96, 96, 100)), kmats.lin((168, 166, 158)), kmats.lin((66, 60, 54)), kmats.lin((16, 16, 18)))
HIT_WOOD = (kmats.lin((196, 170, 128)), kmats.lin((66, 50, 34)), kmats.lin((150, 120, 84)), kmats.lin((8, 7, 6)))
HIT_SAND = (kmats.lin((134, 112, 80)), kmats.lin((112, 92, 64)), kmats.lin((170, 148, 108)), kmats.lin((70, 56, 40)))


def apply_hits(t, col, h, g_, vec, pos, hits, cols=HIT_METAL, depth=2.5):
    if not hits:
        return col, h, g_
    bowl, rim, splash, core = hit_masks(t, pos, hits)
    sp = t.math("MULTIPLY", splash, t.step(t.noise(vec, 70.0, 4.0, 0.7), 0.42, 0.62))
    col = t.mixc(t.math("MULTIPLY", sp, 0.85), col, cols[0])
    col = t.mixc(bowl, col, cols[1])
    col = t.mixc(t.math("MULTIPLY", rim, 0.6), col, cols[2])
    col = t.mixc(core, col, cols[3])
    h = t.math("ADD", h, t.math("ADD", t.math("MULTIPLY", bowl, -depth), t.math("MULTIPLY", rim, depth * 0.35)))
    h = t.math("SUBTRACT", h, t.math("MULTIPLY", core, depth * 0.6))
    g_ = t.math("ADD", g_, t.math("MULTIPLY", bowl, 0.2))
    return col, h, g_


def build_worn(mat, origin, color, bare=kmats.lin((112, 112, 116)), seed=1.0, gloss=0.32, spec=0.25,
               wear=(0.66, 0.71), edge_k=0.7, rub=(), stripes=(), scratch=0.0, oil=0.0, floor_z=0.0,
               dust=0.15, grime=0.3, decal_items=(), hits=(), hit_cols=HIT_METAL, planks=None, brushed=True):
    """Paint worn by frequent use, without rust - from the M24 generator (which took it from M23): rubbed
    to metal on the edges (edge_k) and where things are held (rub - [(center, semi-axes, strength)]);
    scratches, oil spots (oil), stripes of another color (stripes). Extended here: hits - bullet dents
    [(center, semi-axes, through)] (hit_masks); planks = (axis 0..2, step, start) - board seams across
    the axis; brushed=False - bare "metal" without polishing (the wood under the paint of the box)."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.9 for c in color[:3]) + (1,), color)
    for (x0, x1, y0, y1, z0, z1), scol in stripes:
        inside = 1.0
        for i, (a, b) in enumerate(((x0, x1), (y0, y1), (z0, z1))):
            w = sep.outputs[i]
            m = t.math("MULTIPLY", t.math("GREATER_THAN", w, a), t.math("LESS_THAN", w, b))
            inside = m if isinstance(inside, float) else t.math("MULTIPLY", inside, m)
        base = t.mixc(inside, base, scol)
    col = kmats.decals(t, base, sep, nsep, decal_items)
    edge = t.maprange(t.edge_wear(0.004), 0.05, 0.22, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 11.0, 10.0, 0.7), 0.75), t.math("MULTIPLY", edge, edge_k))
    grain = t.maprange(t.noise(vec, 34.0, 8.0, 0.7), 0.3, 0.7, 0.55, 1.0)
    for c, r, k in rub:
        near = t.maprange(near3(t, pos, c, r), 0.25, 1.0, 1.0, 0.0)
        f = t.math("ADD", f, t.math("MULTIPLY", t.math("MULTIPLY", near, grain), k))
    worn = t.step(f, wear[0], wear[1])
    if brushed:
        brush = t.noise(t.stretch(vec, 0.04, 1.0, 1.0), 90.0, 4.0, 0.7)
    else:
        brush = t.noise(t.stretch(vec, 1.0, 1.0, 0.05), 40.0, 4.0, 0.7)
    metal = t.mixc(t.maprange(brush, 0.3, 0.7, 0.0, 1.0), tuple(c * 0.75 for c in bare[:3]) + (1,),
                   tuple(min(1.0, c * 1.15) for c in bare[:3]) + (1,))
    rim = t.math("SUBTRACT", t.step(f, wear[0] - 0.05, wear[0]), worn)
    col = t.mixc(t.math("MULTIPLY", rim, 0.6), col, kmats.lin((52, 50, 46)))
    col = t.mixc(worn, col, metal)
    h = t.math("MULTIPLY", worn, -0.3)
    shine = 0.62 if brushed else 0.2
    g_ = t.math("ADD", gloss, t.math("MULTIPLY", worn, shine - gloss))
    s_ = t.math("ADD", spec, t.math("MULTIPLY", worn, (0.70 if brushed else 0.15) - spec))
    if planks is not None:
        ax, pitch, start = planks
        fr = t.math("FRACT", t.math("DIVIDE", t.math("SUBTRACT", sep.outputs[ax], start), pitch))
        dist = t.math("MULTIPLY", t.math("MINIMUM", fr, t.math("SUBTRACT", 1.0, fr)), pitch)
        seam = t.maprange(dist, 0.0012, 0.0028, 1.0, 0.0)
        col = t.mixc(t.math("MULTIPLY", seam, 0.85), col, kmats.lin((10, 10, 10)))
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", seam, 0.8))
    if scratch > 0:
        sc = t.step(t.noise(t.stretch(vec, 0.02, 1.0, 1.0), 260.0, 2.0, 0.5), 0.70, 0.73)
        sc = t.math("MULTIPLY", sc, t.maprange(t.noise(vec, 5.0, 4.0, 0.5), 0.35, 0.65, 0.0, scratch))
        sc2 = t.step(t.noise(t.stretch(vec, 1.0, 1.0, 0.03), 240.0, 2.0, 0.5), 0.71, 0.74)
        sc = t.math("MAXIMUM", sc, t.math("MULTIPLY", sc2, t.maprange(t.noise(vec, 4.0, 4.0, 0.5), 0.4, 0.7, 0.0,
                                                                      scratch * 0.7)))
        col = t.mixc(t.math("MULTIPLY", sc, 0.7), col, metal)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", sc, 0.15))
    col, h, g_ = apply_hits(t, col, h, g_, vec, pos, hits, hit_cols)
    if oil > 0:
        up = t.maprange(nsep.outputs["Z"], 0.5, 0.9, 0.0, 1.0)
        ol = t.math("MULTIPLY", t.step(t.noise(vec, 4.0, 6.0, 0.6), 0.62, 0.70), t.math("MULTIPLY", up, oil))
        col = t.mixc(t.math("MULTIPLY", ol, 0.55), col, kmats.lin((14, 12, 10)))
        g_ = t.math("ADD", g_, t.math("MULTIPLY", ol, 0.25))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g_, s_, h)


def build_sand(mat, origin, seed=3.0, hits=()):
    """Sand in the bullet trap: grain, blotchy tone, loosened pits from bullets; matte."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    pos = sep.inputs[0].links[0].from_socket
    n1 = t.noise(vec, 9.0, 6.0, 0.6)
    grains = t.noise(vec, 260.0, 2.0, 0.5)
    col = t.mixc(t.maprange(n1, 0.3, 0.7, 0.0, 1.0), kmats.lin((150, 128, 94)), kmats.lin((190, 168, 128)))
    col = t.mixc(t.math("MULTIPLY", t.step(grains, 0.58, 0.72), 0.5), col, kmats.lin((112, 94, 66)))
    damp = t.step(t.noise(vec, 2.2, 4.0, 0.5), 0.58, 0.72)
    col = t.mixc(t.math("MULTIPLY", damp, 0.35), col, kmats.lin((110, 92, 66)))
    h = t.math("ADD", t.math("MULTIPLY", n1, 0.8), t.math("MULTIPLY", grains, 0.35))
    col, h, g_ = apply_hits(t, col, h, 0.08, vec, pos, hits, HIT_SAND, depth=3.0)
    return kmats.out(t, col, g_, 0.03, h)


def build_thread(mat, origin, axis=1, pitch=0.0025, seed=5.6, tone=0.36, gloss=0.55, spec=0.70, floor_z=0.0,
                 dust=0.05, grime=0.35):
    """Threaded screw: steel, dark thread valleys every pitch along axis (0..2) - as a pattern and as
    relief (_nohq); the geometry is a smooth cylinder. In the "dayz" profile steel is darker, as in
    kmats.build_steel."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    if kmats.LOOK["name"] == "dayz":
        tone *= kmats.LOOK["steel"]
    fr = t.math("FRACT", t.math("DIVIDE", sep.outputs[axis], pitch))
    tri = t.math("ABSOLUTE", t.math("SUBTRACT", t.math("MULTIPLY", fr, 2.0), 1.0))
    groove = t.maprange(tri, 0.25, 0.45, 1.0, 0.0)
    v = t.maprange(t.noise(vec, 40.0, 4.0, 0.6), 0.3, 0.7, 0.0, 1.0)
    col = t.mixc(v, (tone * 0.85, tone * 0.86, tone * 0.88, 1), (tone * 1.10, tone * 1.10, tone * 1.12, 1))
    col = t.mixc(t.math("MULTIPLY", groove, 0.8), col, (tone * 0.25, tone * 0.24, tone * 0.22, 1))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.45)
    g_ = t.math("SUBTRACT", gloss, t.math("MULTIPLY", t.math("ADD", dirt, groove), gloss * 0.5))
    s_ = t.math("SUBTRACT", spec, t.math("MULTIPLY", t.math("ADD", dirt, groove), spec * 0.5))
    h = t.math("SUBTRACT", t.math("MULTIPLY", tri, 0.6), 0.3)
    return kmats.out(t, col, g_, s_, h)


def wdecal(name):
    return os.path.join(WORK, name)


BLACK = kmats.lin((30, 30, 32))
RED = kmats.lin((140, 24, 20))
SCALE = kmats.lin((60, 60, 62))                     # scale: dark steel without paint
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)


def hits_y(lst, y, ry):
    """Misses on faces perpendicular to y: splash semi-axes ~3.4 bowl radii."""
    return [((x, y, z), (r / 0.29, ry, r / 0.29), False) for x, z, r in lst]


PLATE_HITS = [((x, lay.PY0, z), (r / 0.29, 0.004, r / 0.29), i in lay.PIERCED) for i, (x, z, r) in enumerate(lay.HITS)]
FRAME_HITS = hits_y(lay.FRAME_HITS, (lay.PY1 + FY) / 2, 0.012)
BACKER_HITS = [((x, lay.BY, z), (r / 0.29, 0.004, r / 0.29), True) for x, z, r in lay.BACKER_HITS]
SAND_PTS = ((-0.02, 0.17), (0.05, 0.21), (-0.14, 0.24), (0.16, 0.16), (-0.25, 0.19), (0.27, 0.235))
SAND_HITS = [((x, y, SAND_Z), (0.024, 0.024, 0.02), False) for x, y in SAND_PTS]
PLATE_DECAL = (wdecal("decal_hits.png"), "y", -1, ("x", "z"), lay.PC, (lay.PX1 - lay.PX0, lay.PZ1 - lay.PZ0),
               (lay.PY0 - 0.004, lay.PY0 + 0.004))
SCALE_DECAL = (wdecal("decal_scale.png"), "y", -1, ("x", "z"), (0.0, (LOW[0] + LOW[1]) / 2 - 0.002), (0.60, 0.03),
               (FY - 0.003, FY + 0.003))
TAG_DECAL = (wdecal("decal_tag.png"), "x", 1, ("y", "z"), (0.30, 1.10), (0.08, 0.05), (BX - 0.001, BX + 0.004))
UNIT_DECAL = kc.panel_decal(wdecal("decal_unit.png"), UFR, lay.PANEL[0], lay.PANEL[1], UZ0 + lay.PANEL[2],
                            UZ0 + lay.PANEL[3])
METER_DECAL = (wdecal("decal_meter.png"), "y", -1, ("x", "z"), ((MW[0] + MW[1]) / 2, (MW[2] + MW[3]) / 2),
               (MW[1] - MW[0], MW[3] - MW[2]), (UY0 - C_DIAL - 0.001, UY0 - C_DIAL + 0.001))

# where it is worn: tommy bars and clamp frames, the unit knob, box handles, frame edges at the plate
CLAMP_RUB = [((s * 0.19, -0.05, z), (0.03, 0.03, 0.03), 0.3) for s in (-1, 1) for z in CLAMP_Z]
UNIT_RUB = [(((UX0 + UX1) / 2, (UY0 + UY1) / 2, UZ1 + 0.025), (0.12, 0.03, 0.03), 0.5),
            ((lay.TOGS[0] + 0.025, UY0, UZ0 + lay.TOG_B), (0.05, 0.02, 0.03), 0.4),
            ((lay.KNOB[0], UY0, UZ0 + lay.KNOB[1]), (0.03, 0.02, 0.03), 0.4)]
CRATE_RUB = [((s * BX, (BY0 + BY1) / 2, 1.25), (0.03, 0.10, 0.06), 0.55) for s in (-1, 1)]
FRAME_RUB = [((0.0, FY, lay.PZ0), (0.20, 0.03, 0.03), 0.35), ((0.0, FY, LOW[1]), (0.35, 0.05, 0.02), 0.3)]
WORN = dict(seed=2.1, wear=(0.67, 0.72), edge_k=0.8, scratch=0.3, floor_z=0.0, dust=0.15, grime=0.3)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "frame": (build_worn, dict(color=SCALE, bare=kmats.lin((136, 136, 140)), seed=1.3, gloss=0.30, spec=0.35,
                               wear=(0.62, 0.68), edge_k=1.0, rub=FRAME_RUB, scratch=1.0, floor_z=0.0, dust=0.45,
                               grime=0.35, hits=FRAME_HITS, decal_items=[SCALE_DECAL])),
    "skid": (build_worn, dict(color=SCALE, bare=kmats.lin((130, 130, 134)), seed=1.9, gloss=0.28, spec=0.3,
                              wear=(0.60, 0.66), edge_k=1.0, scratch=0.8, floor_z=0.0, dust=0.6, grime=0.5)),
    "plate": (build_worn, dict(color=kmats.lin((52, 54, 54)), bare=kmats.lin((130, 130, 134)), seed=4.4, gloss=0.25,
                               spec=0.2, wear=(0.70, 0.76), edge_k=1.0, scratch=0.4, floor_z=lay.PZ0, dust=0.1,
                               grime=0.1, hits=PLATE_HITS, decal_items=[PLATE_DECAL])),
    # spare plates on the shelf: the same paint, intact
    "spare": (build_worn, dict(color=kmats.lin((50, 53, 52)), bare=kmats.lin((130, 130, 134)), seed=4.9, gloss=0.25,
                               spec=0.2, wear=(0.72, 0.78), edge_k=1.0, scratch=0.3, floor_z=SHELF_TOP, dust=0.3,
                               grime=0.2)),
    "clamp": (build_worn, dict(WORN, color=BLACK, bare=kmats.lin((96, 96, 100)), seed=5.1, wear=(0.62, 0.68),
                               edge_k=1.1, rub=CLAMP_RUB, scratch=0.6, floor_z=lay.PZ0, dust=0.1, grime=0.2)),
    "screw": ("steel", dict(seed=5.6, tone=0.36, along="y", gloss=0.6, spec=0.75, floor_z=lay.PZ0, dust=0.05,
                            grime=0.25)),
    "thread": (build_thread, dict(axis=1, pitch=0.0025, floor_z=lay.PZ0)),
    # weld: scale darker than the frame, temper colors not visible under the grime
    "weld": ("steel", dict(seed=7.7, tone=0.20, along="z", gloss=0.35, spec=0.40, dust=0.45, grime=0.5)),
    "crate": (build_worn, dict(WORN, color=BLACK, bare=kmats.lin((122, 92, 62)), seed=6.3, gloss=0.22, spec=0.12,
                               wear=(0.70, 0.75), edge_k=1.0, rub=CRATE_RUB, scratch=0.25, floor_z=BZ0, dust=0.35,
                               grime=0.25, stripes=[((-1, 1, -1, 1, STRIPE[0], STRIPE[1]), RED)], brushed=False,
                               planks=(2, 0.13, BZ0), decal_items=[])),
    "crate_steel": (build_worn, dict(WORN, color=BLACK, seed=6.9, wear=(0.62, 0.68), edge_k=1.2, scratch=0.5,
                                     floor_z=0.0, dust=0.3, grime=0.3)),
    "backer": (build_worn, dict(color=kmats.lin((150, 118, 80)), bare=kmats.lin((150, 118, 80)), seed=7.3,
                                gloss=0.15, spec=0.08, wear=(0.99, 1.0), edge_k=0.0, floor_z=BZ0, dust=0.3,
                                grime=0.3, hits=BACKER_HITS, hit_cols=HIT_WOOD, brushed=False,
                                planks=(0, 0.20, BACKER[0]))),
    "sand": (build_sand, dict(hits=SAND_HITS)),
    # shelf boards: bare, gray from dust and sand
    "board": (kwood.build_wood, dict(color=kmats.lin((118, 98, 72)), seed=3.7, along="y", floor_z=0.0, dust=0.7,
                                     grime=0.5, knots=0.6)),
    # flattened bullets: copper jacket, lead in the opening
    "bullet": ("plastic", dict(color=kmats.lin((150, 92, 54)), gloss=0.45, spec=0.4, dust=0.3, grime=0.2,
                               scuff=(0.45, 0.55))),
    "unit": (build_worn, dict(WORN, color=BLACK, seed=8.1, wear=(0.66, 0.71), edge_k=0.9, rub=UNIT_RUB,
                              scratch=0.3, floor_z=UZ0, dust=0.2, grime=0.15, decal_items=[UNIT_DECAL])),
    "unit_red": (build_worn, dict(WORN, color=RED, seed=8.6, wear=(0.68, 0.73), edge_k=1.0, scratch=0.3,
                                  floor_z=UZ0, dust=0.2, grime=0.15)),
    "bezel": ("plastic", dict(color=kmats.lin((22, 22, 23)), gloss=0.30, spec=0.25, dust=0.2, grime=0.2,
                              scuff=(0.66, 0.74))),
    # indicator scale: cream; "working" - backlit
    "dial": ("paint", dict(CLEAN, color=kmats.lin((200, 194, 172)), gloss=0.5, spec=0.4, decal_items=[METER_DECAL])),
    "dial_on": ("paint", dict(CLEAN, color=kmats.lin((236, 222, 176)), gloss=0.5, spec=0.4,
                              decal_items=[METER_DECAL])),
    "needle": ("flat", dict(color=kmats.lin((20, 20, 20)), gloss=0.4, spec=0.3)),
    "chrome": ("steel", dict(seed=8.9, tone=0.44, along="z", gloss=0.62, spec=0.75, dust=0.1, grime=0.3)),
    "dark": ("flat", dict(color=kmats.lin((10, 10, 10)), gloss=0.2, spec=0.1)),
    "lamp_g_off": ("flat", dict(color=kmats.lin((34, 64, 40)), gloss=0.85, spec=0.8)),
    "lamp_r_off": ("flat", dict(color=kmats.lin((72, 24, 22)), gloss=0.85, spec=0.8)),
    "lamp_g_on": ("flat", dict(color=kmats.lin((130, 255, 140)), gloss=0.85, spec=0.8)),
    "lamp_r_on": ("flat", dict(color=kmats.lin((255, 86, 60)), gloss=0.85, spec=0.8)),
    "sensor": (build_worn, dict(WORN, color=kmats.lin((44, 44, 46)), seed=9.2, wear=(0.68, 0.73), edge_k=0.9,
                                scratch=0.3, floor_z=SZ0, dust=0.3, grime=0.15,
                                stripes=[((-1, 1, -1, 1, SZ1 - 0.012, SZ1 + 0.01), RED)])),
    "lens": ("flat", dict(color=kmats.lin((26, 14, 16)), gloss=0.95, spec=0.9)),
    "post": (build_worn, dict(WORN, color=BLACK, seed=9.8, wear=(0.64, 0.70), edge_k=1.0, scratch=0.5, dust=0.3,
                              grime=0.4)),
    "cable": ("plastic", dict(color=kmats.lin((26, 26, 26)), gloss=0.30, spec=0.2, dust=0.4, scuff=(0.8, 0.9))),
    "tag": ("paint", dict(CLEAN, color=kmats.lin((176, 178, 176)), gloss=0.5, spec=0.5, decal_items=[TAG_DECAL])),
})

OBJ, NAME = "m26_dty_proc_prot", "ozr_dty_proc_prot"
# Working look: the display has its own texture (the mod script cycles the frames), the frame lamps are
# the _on atlas (blink), the mains lamp and the scale backlight are the _on atlas (steady), the needle is
# the bone ozl_meter (wobble). All three textured selections are in hiddenSelections.
SEL_SCREEN, SEL_LAMP, SEL_POWER, SEL_METER = "ozl_screen", "ozl_lamp", "ozl_power", "ozl_meter"
# "working" preview: the needle is raised (the rotation is in _posed below); does not go into the p3d
ON_MOVE = {}
ON = dict(remap={"lamp_g_off": "lamp_g_on", "lamp_r_off": "lamp_r_on", "dial": "dial_on"},
          emissive=(1.0, 1.0, 1.0, 1.0), move=ON_MOVE)
METER_ANIM = ("ozl_meter_needle", dict(type="rotation", source="ozl_meter", selection=SEL_METER, axis="ozl_meter_axis",
                                       memory=1, minValue=0.0, maxValue=1.0, angle0=0.0, angle1=METER_SPAN))
# display: the "working" frames are from make_decals.py (36 frames, six stages per shot)
SCREEN = dict(off="screen_off.png", frames=["screen_f%02d.png" % i for i in range(lay.SCREEN_FRAMES)], size=256,
              gloss=0.8)

# vanilla DayZ items as proxies: on the board by the unit a shot log with a pen, a pack and loose
# cartridges; on the shelf an army ammo crate, rags, on the spare plates a wrench and tape; a sapper
# shovel is leaned against the box
SPARE_TOP = SHELF_TOP + 2 * 0.008
DECOR = [
    kv.put("paper", (-0.165, 0.388, LID_TOP), lift=0.0005, **kv.flat(2)),
    kv.put("pen", (-0.085, 0.405, LID_TOP), lift=0.0012, **kv.flat(70)),
    kv.put("ammobox762", (-0.352, 0.335, LID_TOP), **kv.flat(96)),
    kv.put("rounds762", (-0.345, 0.452, LID_TOP), up=(0, 0, 1), fwd=(0.3, -1, 0)),
    kv.put(r"dz\gear\containers\300RoundBox", (-0.175, 0.425, SHELF_TOP), up=(0, 0, 1), fwd=(0, -1, 0)),
    kv.put("rags", (-0.205, 0.215, SHELF_TOP), **kv.flat(4)),
    kv.put("wrench", (0.150, 0.235, SPARE_TOP), **kv.flat(32)),
    kv.put("ducttape", (0.225, 0.385, SPARE_TOP), **kv.flat(0)),
    G.lean(r"dz\gear\tools\CSLA_Field_Shovel", foot=(-0.625, 0.30, 0.0), top=(-0.432, 0.30, 0.64), toward=(1, 0, 0)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 selections=(SEL_SCREEN, SEL_LAMP, SEL_POWER, SEL_METER), hidden=(SEL_SCREEN, SEL_LAMP, SEL_POWER),
                 states={"on": ON}, bones=((SEL_METER, ""),), animations=(METER_ANIM,), decor=DECOR,
                 panels={"screen": SCREEN}, sources={"ozl_meter": dict(animPeriod=0.2)})
P = M.part
BOUNDS = {}


def engine_turn(axis_pts, ang):
    """A bone rotation by angle ang as the engine will do it by the memory axis axis_pts: (a point on the
    axis, the Blender axis for Matrix.Rotation - right-handed, the angle). The Blender axis is the reverse
    of the memory axis (from the second point to the first)."""
    a, b = Vector(axis_pts[0]), Vector(axis_pts[1])
    return tuple(a), tuple(a - b), ang


def check_needle():
    """By number, like check_axes of the Storage crates: the engine rotation moves the needle at phases 0,
    mid +- amp and 1 along the scale clockwise (from the front METER_REST -> METER_REST - METER_SWEEP),
    the tip does not leave the scale window. If they disagree - the build fails."""
    c = Vector(METER_AXIS[0])
    a = math.radians(lay.METER_REST)
    tip = c + Vector((math.cos(a), 0.0, math.sin(a))) * lay.METER_R
    seen = []
    for ph in (0.0, METER_MID - METER_AMP, METER_MID, METER_MID + METER_AMP, 1.0):
        o, ax, ang = engine_turn(METER_AXIS, ph * METER_SPAN)
        q = Vector(o) + Matrix.Rotation(ang, 3, Vector(ax)) @ (tip - Vector(o))
        deg = math.degrees(math.atan2(q.z - c.z, q.x - c.x))
        assert abs(deg - (lay.METER_REST - lay.METER_SWEEP * ph)) < 0.01, "the needle goes the wrong way: %.1f" % deg
        assert MW[0] < q.x < MW[1] and MW[2] < q.z < MW[3], "the needle tip is outside the scale window: phase %.2f" % ph
        seen.append("%.2f -> %.1f" % (ph, deg))
    print("turns ok: needle (phase -> degrees from the front) " + ", ".join(seen))


check_needle()


def _posed(place):
    """Preview of "working": the indicator needle in its working pose, by the engine rotation
    (engine_turn: the preview shows what will be in the game). kmodel only does a shift (move), so the
    rotation is here, as a wrapper over krender (as in M10); it does not go into the p3d - the model.cfg
    animation does that."""
    def wrapped(parts, *a, **kw):
        obs = place(parts, *a, **kw)
        if kw.get("move") is ON_MOVE:
            o, ax, ang = engine_turn(METER_AXIS, METER_MID * METER_SPAN)
            for p, ob in zip(parts, obs):
                if p.group == SEL_METER:
                    loc = Vector(ob.location)
                    cc = Vector(o) + loc
                    ob.matrix_world = (Matrix.Translation(cc) @ Matrix.Rotation(ang, 4, Vector(ax)) @
                                       Matrix.Translation(-cc) @ Matrix.Translation(loc))
        return obs
    return wrapped


krender.place_look = _posed(krender.place_look)
krender.place = _posed(krender.place)                # the tex_on_* renders after baking also have the needle in the working pose


# =============================================================================
# Helpers
# =============================================================================
def cable(name, region, pts, r, lod):
    c = P(name, region)
    if lod == 0:
        g.pipe(c, G.spline(pts, 2), r, 6)
    else:
        g.pipe(c, [pts[i] for i in range(0, len(pts), 2)] + ([pts[-1]] if (len(pts) - 1) % 2 else []), r, 4)
    return [c]


def bev(lod, r=0.002, seg=1):
    return dict(r=r, seg=seg) if lod == 0 else {}


def quad_face(part, fr, a0, a1, b0, b1, c):
    """Flat rectangle facing outward (+c) in system fr."""
    pts = [fr.p(a0, b0, c), fr.p(a1, b0, c), fr.p(a1, b1, c), fr.p(a0, b1, c)]
    f = part.bm.faces.new([part.bm.verts.new(q) for q in pts])
    f.normal_update()
    if f.normal.dot(fr.n) < 0:
        f.normal_flip()
    return part.tag([f])


def weld_line(part, a, b, r=0.0028):
    G.weld(part, [a, b], r)


# =============================================================================
# Skids, crosspieces, frame
# =============================================================================
def build_skids(spec):
    lod = spec["lod"]
    sk = P("skids", "skid")
    poly = [(-SKY, 0.032), (-SKY + 0.045, 0.0), (SKY - 0.045, 0.0), (SKY, 0.032), (SKY, SKH), (-SKY, SKH)]
    for s in (-1, 1):
        x0, x1 = s * SKX - SKW / 2, s * SKX + SKW / 2
        if lod == 0:
            G.prism_bev(sk, poly, x0, x1, r=0.004, seg=1, axes=(1, 2), sides=True)
        elif lod == 1:
            g.prism(sk, poly, (1, 2), x0, x1)
        else:
            g.box(sk, x0, x1, -SKY, SKY, 0.0, SKH)
    parts = [sk]
    # crosspieces - an angle with one leg on the skids, the other leg down at the front (the cables pass under it)
    cr = P("cross", "skid")
    xa, xb = -SKX - SKW / 2, SKX + SKW / 2
    for y in CROSS if lod < 2 else CROSS[::3]:
        G.angle(cr, (xa, y - A / 2, ZC), (0, 1, 0), (0, 0, -1), (1, 0, 0), xb - xa, A, T, lod)
    parts.append(cr)
    if lod == 0:
        # 12 mm rod eyes at the skid noses, welded
        ey = P("skid_eyes", "skid")
        wl = P("skid_welds", "weld")
        for s in (-1, 1):
            x = s * SKX
            pts = G.spline([(x, -SKY + 0.012, 0.040), (x, -SKY - 0.022, 0.040), (x, -SKY - 0.036, 0.058),
                            (x, -SKY - 0.022, 0.076), (x, -SKY + 0.012, 0.076)], 2)
            g.pipe(ey, pts, 0.006, 8)
            for z in (0.040, 0.076):
                weld_line(wl, (x - 0.008, -SKY - 0.002, z), (x + 0.008, -SKY - 0.002, z), 0.0035)
        parts += [ey, wl]
    return parts


def build_frame(spec):
    lod = spec["lod"]
    fr = P("frame", "frame")
    z0 = ZC + BASE_T
    # posts: the heel outside at the front, the face leg inward along x, the second leg backward
    for s in (-1, 1):
        G.angle(fr, (s * (UX + A / 2), FY, 0.0), (-s, 0, 0), (0, 1, 0), (0, 0, 1), ZST - z0, A, T, lod, c0=z0)
    # crossbars: top (the leg on top, backward; the ends 4 mm past the posts), the window bottom, a tie (the leg below)
    xt = UX + A / 2 + 0.004
    G.angle(fr, (-xt, FY, TOP[1]), (0, 0, -1), (0, 1, 0), (1, 0, 0), 2 * xt, A, T, lod)
    xi = UX - A / 2
    G.angle(fr, (-xi, FY, LOW[1]), (0, 0, -1), (0, 1, 0), (1, 0, 0), 2 * xi, A - 0.01, T, lod)
    if lod < 2:
        G.angle(fr, (-xi, FY, TIE[0]), (0, 0, 1), (0, 1, 0), (1, 0, 0), 2 * xi, A - 0.01, T, lod)
    parts = [fr]
    # post heels on the crosspiece
    if lod < 2:
        bp = P("frame_base", "frame")
        for s in (-1, 1):
            g.box(bp, s * UX - 0.045, s * UX + 0.045, FY - 0.010, FY + A + 0.012, ZC, z0, **bev(lod, 0.0015))
        parts.append(bp)
    # vertical straps of the window (they lie on the crossbar faces) and the shelf under the plate with gussets
    fl = P("frame_flats", "frame")
    for s in (-1, 1):
        g.box(fl, *sorted((s * FLAT_X[0], s * FLAT_X[1])), FLAT_Y[0], FLAT_Y[1], FLAT_Z[0], FLAT_Z[1], **bev(lod, 0.0015))
    if lod < 2:
        g.box(fl, -0.17, 0.17, -0.012, FLAT_Y[0], SHELF_Z - 0.006, SHELF_Z, **bev(lod, 0.001))
        g.box(fl, -0.17, 0.17, -0.012, -0.008, SHELF_Z - 0.03, SHELF_Z - 0.006, **bev(lod, 0.001))
    if lod == 0:
        for x in (-0.135, 0.135):
            g.prism(fl, [(FLAT_Y[0] - 0.0005, SHELF_Z - 0.006), (-0.008, SHELF_Z - 0.006),
                         (FLAT_Y[0] - 0.0005, SHELF_Z - 0.036)], (1, 2), x - 0.002, x + 0.002)
    parts.append(fl)
    # front braces: a 40 x 6 strap from the post to the skids
    if lod < 2:
        br = P("frame_braces", "frame")
        zb, yb = BRACE
        for s in (-1, 1):
            G.box_to(br, (s * UX, FY - 0.003, zb), (s * UX, yb, SKH + 0.003), 0.04, 0.006, up=(1, 0, 0),
                     **bev(lod, 0.0012))
        parts.append(br)
    if lod == 0:
        wl = P("frame_welds", "weld")
        e = FY - 0.0006
        for s in (-1, 1):
            xin, xout = s * (UX - A / 2), s * (UX + A / 2)
            weld_line(wl, (xin, e, LOW[0] + 0.002), (xin, e, LOW[1] - 0.002))
            weld_line(wl, (xin, e, TIE[0] + 0.002), (xin, e, TIE[1] - 0.002))
            weld_line(wl, (xin, e, ZST - 0.001), (xout, e, ZST - 0.001))
            weld_line(wl, (xin, FY - 0.002, z0 + 0.002), (xout, FY - 0.002, z0 + 0.002), 0.0032)
            # brace - to the post and to the skids
            zb, yb = BRACE
            weld_line(wl, (s * UX - 0.0045, FY - 0.004, zb - 0.024), (s * UX - 0.0045, FY - 0.004, zb + 0.016))
            weld_line(wl, (s * UX - 0.0045, yb - 0.022, SKH + 0.002), (s * UX - 0.0045, yb + 0.022, SKH + 0.002))
        parts.append(wl)
    return parts


def build_plate(spec):
    lod = spec["lod"]
    pl = P("plate", "plate")
    g.box(pl, lay.PX0, lay.PX1, lay.PY0, lay.PY1, lay.PZ0, lay.PZ1, **bev(lod, 0.002, 2))
    return [pl]


# =============================================================================
# Clamps: a cast G-shaped frame embraces the strap and the plate edge, a screw with a swivel foot
# presses on the plate face, the tommy bar is a rod with balls
# =============================================================================
def clamp_outline(lod):
    """Outline of the frame in plan (p - from the axis outward, y), counterclockwise: the front arm with a
    boss, the back, the rear jaw behind the strap."""
    if lod > 0:
        return [(0.100, -0.062), (0.205, -0.062), (0.205, 0.034), (0.100, 0.034), (0.100, 0.0205),
                (0.183, 0.0205), (0.183, -0.040), (0.100, -0.040)]
    pts = [(0.100, -0.062)]

    def arc(cx, cy, r, a0, a1, n):
        for k in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    arc(0.191, -0.048, 0.014, -90.0, 0.0, 2)
    arc(0.191, 0.020, 0.014, 0.0, 90.0, 2)
    pts += [(0.100, 0.034), (0.100, 0.0205)]
    arc(0.175, 0.0125, 0.008, 90.0, 0.0, 2)
    arc(0.175, -0.032, 0.008, 0.0, -90.0, 2)
    return pts


def build_clamps(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    cl = P("clamps", "clamp")
    sc = P("clamp_screws", "thread")
    parts = [cl, sc]
    hw = P("clamp_bars", "screw") if lod == 0 else None
    outline = clamp_outline(lod)
    for i, (s, zc) in enumerate([(s, z) for s in (-1, 1) for z in CLAMP_Z]):
        x = s * SCREW_X
        poly = [(s * p, y + 0.0005) for p, y in outline]
        if lod == 0:
            G.prism_bev(cl, poly, zc - CLAMP_T / 2, zc + CLAMP_T / 2, r=0.0022, seg=1)
            # threaded boss on the front arm
            G.lathe(cl, [(0.0115, 0.0), (0.0115, 0.031), (0.0085, 0.034)], 10,
                    G.frame_at((x, -0.068, zc), "y"))
        else:
            g.prism(cl, poly, (0, 1), zc - CLAMP_T / 2, zc + CLAMP_T / 2)
            g.cyl(cl, (x, -0.051, zc), "y", 0.0115, 0.034, 8)
        # screw: from the tommy bar head to the foot at the plate
        g.cyl(sc, (x, -0.0655, zc), "y", 0.0055, 0.119, 12 if lod == 0 else 6)
        if lod > 0:
            continue
        # screw head with a cross hole, the tommy bar with balls, a ball foot
        G.lathe(hw, [(0.0088, 0.0), (0.0088, 0.016), (0.0060, 0.018)], 10,
                G.frame_at((x, -0.142, zc), "y"))
        a = math.radians(T_BAR[i])
        d = Vector((math.cos(a), 0.0, math.sin(a)))
        c = Vector((x, -0.133, zc))
        G.rod(hw, c - d * 0.042, c + d * 0.042, 0.0042, 6)
        for e in (-1, 1):
            G.sphere(hw, tuple(c + d * (e * 0.045)), 0.0060, 6, 3)
        G.lathe(hw, [(0.0110, 0.0), (0.0110, 0.0035), (0.0, 0.0058)], 10,
                G.frame_at((x, -0.0006, zc), "-y"))
    if hw is not None:
        parts.append(hw)
    return parts


# =============================================================================
# Bullet trap: a stand with a shelf, a box, sand, a shield, a board, a tag, bullets in the sand
# =============================================================================
def build_stand(spec):
    """Box stand: legs of 40 x 40 tube on the crosspieces, strapping of 40 x 4 angle under the box, a
    shelf of 30 x 3 angle and boards; two spare plates on the shelf."""
    lod = spec["lod"]
    st = P("trap_stand", "crate_steel")
    parts = [st]
    for x in (-LEG_X, LEG_X):
        for y in LEG_Y:
            if lod == 0:
                G.tube_sq(st, (x, y), SA / 2, ZC, LEG_TOP, 0.004, 2)
            elif lod == 1:
                g.box(st, x - SA / 2, x + SA / 2, y - SA / 2, y + SA / 2, ZC, LEG_TOP)
    if lod == 2:
        for x in (-LEG_X, LEG_X):
            g.box(st, x - SA / 2, x + SA / 2, LEG_Y[0] - SA / 2, LEG_Y[1] + SA / 2, ZC, BZ0 - 0.04)
        g.box(st, -BX - 0.005, BX + 0.005, BY0 - 0.005, BY1 + 0.005, BZ0 - 0.04, BZ0)
        return parts
    # strapping: the long ones full length, the cross ones between them (the top legs do not overlap)
    xo, y0, y1 = BX + 0.005, BY0 - 0.005, BY1 + 0.005
    G.angle(st, (-xo, y0, BZ0), (0, 0, -1), (0, 1, 0), (1, 0, 0), 2 * xo, SA, ST, lod)
    G.angle(st, (-xo, y1, BZ0), (0, 0, -1), (0, -1, 0), (1, 0, 0), 2 * xo, SA, ST, lod)
    for s in (-1, 1):
        G.angle(st, (s * xo, y0 + SA, BZ0), (0, 0, -1), (-s, 0, 0), (0, 1, 0), y1 - y0 - 2 * SA, SA, ST, lod)
    # shelf angles between the legs and boards along y
    xi = LEG_X - SA / 2
    G.angle(st, (-xi, LEG_Y[0] - SA / 2 + 0.001, RAIL_Z), (0, 0, -1), (0, 1, 0), (1, 0, 0), 2 * xi, 0.03, 0.003, lod)
    G.angle(st, (-xi, LEG_Y[1] + SA / 2 - 0.001, RAIL_Z), (0, 0, -1), (0, -1, 0), (1, 0, 0), 2 * xi, 0.03, 0.003, lod)
    bd = P("trap_shelf", "board")
    w, gap = 0.13, 0.0125
    for k in range(5):
        xa = -0.35 + k * (w + gap)
        g.box(bd, xa, xa + w, LEG_Y[0] - 0.015, LEG_Y[1] + 0.015, RAIL_Z, SHELF_TOP, **bev(lod, 0.002))
    parts.append(bd)
    # spare plates in a stack
    sp = P("spare_plates", "spare")
    for k, (cx, cy, deg) in enumerate(SPARE):
        a = math.radians(deg)
        fr_ = g.Frame((cx, cy, SHELF_TOP + k * 0.008), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0),
                      (0, 0, 1))
        g.box(sp, -0.125, 0.125, -0.150, 0.150, 0.0, 0.008, frame=fr_, **bev(lod, 0.0015))
    parts.append(sp)
    return parts


def build_trap(spec):
    lod = spec["lod"]
    parts = []
    cr = P("trap_box", "crate")
    if lod == 2:
        g.box(cr, -BX, BX, BY0, BY1, BZ0, SAND_Z)
        g.box(cr, -BX, BX, LID_Y0, BY1, SAND_Z, BZ1 + LID_T)
        sd = P("trap_sand", "sand")
        g.quad(sd, [(-BX, BY0, SAND_Z + 0.001), (BX, BY0, SAND_Z + 0.001), (BX, LID_Y0, SAND_Z + 0.001),
                    (-BX, LID_Y0, SAND_Z + 0.001)])
        bk = P("trap_backer", "backer")
        g.box(bk, BACKER[0], BACKER[1], lay.BY, BY0, BACKER[2], BACKER[3])
        return parts + [cr, sd, bk]
    g.box(cr, -BX, BX, BY0, BY0 + WALL, BZ0, BZ1, **bev(lod, 0.003))
    g.box(cr, -BX, BX, BY1 - WALL, BY1, BZ0, BZ1, **bev(lod, 0.003))
    for s in (-1, 1):
        g.box(cr, *sorted((s * BX, s * (BX - WALL))), BY0 + WALL, BY1 - WALL, BZ0, BZ1, **bev(lod, 0.003))
    g.box(cr, -BX + WALL, BX - WALL, BY0 + WALL, BY1 - WALL, BZ0, BZ0 + 0.02)                 # bottom
    parts.append(cr)
    # sand: bumps, pits from bullets (a grid on the near LOD); it goes 1 cm under the board
    sd = P("trap_sand", "sand")
    x0, x1, y0, y1 = -BX + WALL, BX - WALL, BY0 + WALL, LID_Y0 + 0.01
    nx, ny = (12, 5) if lod == 0 else (1, 1)

    def zs(i, j):
        if lod > 0 or i in (0, nx) or j in (0, ny):
            return SAND_Z
        x = x0 + (x1 - x0) * i / nx
        y = y0 + (y1 - y0) * j / ny
        z = SAND_Z + 0.010 * math.cos(x * 4.0) + 0.005 * math.sin(y * 31.0 + x * 9.0)
        for hx, hy in SAND_PTS:
            d2 = ((x - hx) ** 2 + (y - hy) ** 2) / 0.0006
            z -= 0.010 * math.exp(-d2)
        return z
    for i in range(nx):
        for j in range(ny):
            q = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            g.quad(sd, [(x0 + (x1 - x0) * a / nx, y0 + (y1 - y0) * b / ny, zs(a, b)) for a, b in q])
    parts.append(sd)
    # board at the back on top of the box (the unit stands on it), a block under the front edge
    ld = P("trap_lid", "crate")
    g.box(ld, -BX, BX, LID_Y0, BY1, BZ1, LID_TOP, **bev(lod, 0.003))
    if lod == 0:
        g.box(ld, -BX + WALL, BX - WALL, LID_Y0, LID_Y0 + 0.03, BZ1 - 0.022, BZ1, r=0.002, seg=1)
    parts.append(ld)
    # plywood shield on the face in a steel strapping
    bk = P("trap_backer", "backer")
    g.box(bk, BACKER[0], BACKER[1], lay.BY, BY0, BACKER[2], BACKER[3])
    parts.append(bk)
    ob = P("trap_steel", "crate_steel")
    w = 0.02
    if lod == 0:
        for xa, xb, za, zb in ((BACKER[0] - w, BACKER[1] + w, BACKER[3], BACKER[3] + w),
                               (BACKER[0] - w, BACKER[1] + w, BACKER[2] - w, BACKER[2]),
                               (BACKER[0] - w, BACKER[0], BACKER[2], BACKER[3]),
                               (BACKER[1], BACKER[1] + w, BACKER[2], BACKER[3])):
            g.box(ob, xa, xb, lay.BY - 0.002, BY0, za, zb)
    # 40 x 3 angles on the vertical edges of the box
    for sx in (-1, 1):
        for yc, sy in ((BY0, -1), (BY1, 1)):
            G.angle(ob, (sx * (BX + 0.003), yc + sy * 0.003, BZ0), (0, -sy, 0), (-sx, 0, 0), (0, 0, 1), BZ1 - BZ0,
                    0.04, 0.003, lod)
    parts.append(ob)
    if lod == 0:
        # side handles on straps, shield strapping bolts, angle screws, a tag on rivets
        hd = P("trap_handles", "steel")
        for s in (-1, 1):
            xo = s * (BX + 0.003)
            g.pipe(hd, G.spline([(xo, 0.235, 1.25), (xo + s * 0.030, 0.240, 1.25), (xo + s * 0.040, 0.270, 1.25),
                                 (xo + s * 0.040, 0.330, 1.25), (xo + s * 0.030, 0.360, 1.25), (xo, 0.365, 1.25)], 2),
                   0.007, 6)
            for y in (0.232, 0.368):
                g.box(hd, *sorted((xo, xo + s * 0.004)), y - 0.018, y + 0.018, 1.228, 1.272)
                for z in (1.250,):
                    G.screw(hd, (xo + s * 0.004, y - s * 0.0, z), "x" if s > 0 else "-x", 0.0035)
        for x in (BACKER[0] - 0.01, BACKER[1] + 0.01):
            for z in (BACKER[2] - 0.01, BACKER[3] + 0.01):
                G.hex_bolt(hd, (x, lay.BY - 0.002, z), "-y", 0.010, 0.005, washer=False)
        parts.append(hd)
        tg = P("trap_tag", "tag")
        g.box(tg, BX + 0.0005, BX + 0.002, 0.26, 0.34, 1.075, 1.125, r=0.0006, seg=1)
        parts.append(tg)
        rv = P("trap_tag_rivets", "steel")
        for y in (0.266, 0.334):
            G.screw(rv, (BX + 0.002, y, 1.10), "x", 0.0028)
        parts.append(rv)
        # flattened bullets in sand pits: an opened copper jacket, lying on the side
        bl = P("sand_bullets", "bullet")
        for k, (hx, hy) in enumerate(SAND_PTS[:3]):
            a = math.radians(40 + 70 * k)
            fr_ = G.frame_axis((hx + 0.004, hy - 0.003, zs_at(hx, hy) + 0.002), (math.cos(a), math.sin(a), 0.25))
            G.lathe(bl, [(0.0, -0.007), (0.0030, -0.0065), (0.0040, -0.003), (0.0042, 0.002), (0.0068, 0.0045),
                         (0.0055, 0.0065), (0.0, 0.0058)], 6, fr_)
        parts.append(bl)
    return parts


def zs_at(x, y):
    """Sand height of the near LOD at point (x, y) (like zs in build_trap, without the grid)."""
    z = SAND_Z + 0.010 * math.cos(x * 4.0) + 0.005 * math.sin(y * 31.0 + x * 9.0)
    for hx, hy in SAND_PTS:
        z -= 0.010 * math.exp(-((x - hx) ** 2 + (y - hy) ** 2) / 0.0006)
    return z


# =============================================================================
# Sensor frames on the post
# =============================================================================
def build_sensors(spec):
    lod = spec["lod"]
    parts = []
    for i, yf in enumerate(SENS_Y):
        y0, y1 = yf - STH / 2, yf + STH / 2
        hs = P("sensor%d" % i, "sensor", uv_name="sensor", uv_origin=(0, yf, 0))
        h = SPW / 2
        loop = [(-SHW + h, yf, SZ0 + h), (SHW - h, yf, SZ0 + h), (SHW - h, yf, SZ1 - h), (-SHW + h, yf, SZ1 - h)]
        if lod == 0:
            before = set(hs.bm.faces)
            faces = g.sweep(hs, loop, (0, 1, 0), h, STH / 2, closed=True)
            g.bevel(hs.bm, list({e for f in faces for e in f.edges}), 0.0035, 1)
            new = [f for f in hs.bm.faces if f not in before]
            bmesh.ops.recalc_face_normals(hs.bm, faces=new)
            hs.tag(new)
        elif lod == 1:
            g.sweep(hs, loop, (0, 1, 0), h, STH / 2, closed=True)
        else:
            for xa, xb, za, zb in ((-SHW, SHW, SZ0, SZ0 + SPW), (-SHW, SHW, SZ1 - SPW, SZ1),
                                   (-SHW, -SHW + SPW, SZ0 + SPW, SZ1 - SPW), (SHW - SPW, SHW, SZ0 + SPW, SZ1 - SPW)):
                g.box(hs, xa, xb, y0, y1, za, zb)
        # bracket to the console
        if lod < 2:
            g.box(hs, SHW - 0.002, BAR_X[0], yf - 0.015, yf + 0.015, BAR_Z[0] - 0.005, BAR_Z[1] + 0.005, **bev(lod, 0.002))
        else:
            g.box(hs, SHW, BAR_X[1], yf - 0.015, yf + 0.015, BAR_Z[0], BAR_Z[1])
        parts.append(hs)
        # ready lamp: a dome lens in a holder
        lx = SHW - 0.04
        lp = P("sensor%d_lamp" % i, "lamp_g", group=SEL_LAMP, uv_name="sensor_lamp", uv_origin=(0, yf, 0))
        if lod == 0:
            G.lathe(lp, [(0.0, 0.0), (0.0068, 0.0), (0.0068, 0.004), (0.0058, 0.0085), (0.0034, 0.0118), (0.0, 0.0125)],
                    10, G.frame_at((lx, yf, SZ1 + 0.003), "z"))
        else:
            g.cyl(lp, (lx, yf, SZ1 + 0.007), "z", 0.007, 0.012, (10, 6, 4)[lod])
        parts.append(lp)
        if lod == 2:
            continue
        cn = P("sensor%d_conn" % i, "black", uv_name="sensor_conn", uv_origin=(0, yf, 0))
        fx = G.frame_at((SHW, yf, SZ0 + 0.03), "x")
        if lod == 0:
            # bayonet connector on the frame side and a cable plug with a knurled nut and a strain relief
            g.box(cn, SHW - 0.001, SHW + 0.002, yf - 0.012, yf + 0.012, SZ0 + 0.018, SZ0 + 0.042, r=0.001, seg=1)
            G.lathe(cn, [(0.0072, 0.002), (0.0072, 0.010), (0.0094, 0.010)], 8, fx)
            g.prism(cn, G.knurl_poly(0.0098, 6, 0.0012), (0, 1), 0.010, 0.024, frame=fx)
            G.lathe(cn, [(0.0086, 0.024), (0.0060, 0.034), (0.0046, 0.046), (0.0, 0.046)], 8, fx)
        else:
            g.cyl(cn, (SHW + 0.018, yf, SZ0 + 0.03), "x", 0.009, 0.032, 4)
        parts.append(cn)
        if lod == 1:
            continue
        ln = P("sensor%d_lens" % i, "lens", uv_name="sensor_lens", uv_origin=(0, yf, 0))
        for za, zb in ((SZ0 + SPW, SZ0 + SPW + 0.002), (SZ1 - SPW - 0.002, SZ1 - SPW)):
            g.box(ln, -SHW + SPW + 0.01, SHW - SPW - 0.01, yf - 0.008, yf + 0.008, za, zb)
        parts.append(ln)
        rm = P("sensor%d_trim" % i, "chrome", uv_name="sensor_trim", uv_origin=(0, yf, 0))
        G.lathe(rm, [(0.0068, 0.0), (0.0102, 0.0), (0.0102, 0.0028), (0.0090, 0.0042), (0.0068, 0.0042)], 8,
                G.frame_at((lx, yf, SZ1 - 0.0005), "z"), closed=True)
        # screws of the emitter covers on the frame face
        for x in (-SHW + h, SHW - h):
            for z in (SZ0 + h, SZ1 - h):
                G.screw(rm, (x, y0 - 0.0002, z), "-y", 0.0034)
        parts.append(rm)
    # console, a clamp with a thumb screw, a post with a cap, a base plate on bolts
    ps = P("sensor_post", "post")
    g.box(ps, BAR_X[0], BAR_X[1], SENS_Y[0] - 0.04, SENS_Y[1] + 0.04, BAR_Z[0], BAR_Z[1], **bev(lod, 0.002))
    if lod == 0:
        G.tube_sq(ps, POST_C, 0.02, ZC + 0.01, POST_TOP, 0.004, 2)
    else:
        g.box(ps, POST_X[0], POST_X[1], POST_Y[0], POST_Y[1], ZC, POST_TOP)
    parts.append(ps)
    if lod == 2:
        return parts
    g.box(ps, BAR_X[0] - 0.006, POST_X[1] + 0.006, POST_Y[0] - 0.006, POST_Y[1] + 0.006, BAR_Z[0] - 0.012,
          BAR_Z[1] + 0.012, **bev(lod, 0.003, 2))
    g.box(ps, POST_X[0] - 0.035, POST_X[1] + 0.035, POST_Y[0] - 0.035, POST_Y[1] + 0.035, ZC, ZC + 0.01,
          **bev(lod, 0.002))
    if lod == 0:
        kn = P("sensor_post_knob", "black")
        bz = (BAR_Z[0] + BAR_Z[1]) / 2
        fk = G.frame_at((POST_X[1] + 0.006, POST_C[1], bz), "x")
        G.lathe(kn, [(0.0052, 0.0), (0.0052, 0.010), (0.0, 0.010)], 8, fk)
        g.prism(kn, [(x * 1.0, y * 1.0) for x, y in G.knurl_poly(0.0145, 5, 0.004)], (0, 1), 0.010, 0.022, frame=fk)
        G.lathe(kn, [(0.0085, 0.022), (0.0070, 0.026), (0.0, 0.0275)], 10, fk)
        cap = P("sensor_post_cap", "black")
        G.prism_bev(cap, G.rrect(-0.0215, 0.0215, -0.0215, 0.0215, 0.005, 2), POST_TOP - 0.004, POST_TOP + 0.007,
                    G.frame_at((POST_C[0], POST_C[1], 0.0), "z"), r=0.002, seg=1)
        bl = P("sensor_post_bolts", "steel")
        for x in (POST_X[0] - 0.025, POST_X[1] + 0.025):
            for y in (POST_Y[0] - 0.025, POST_Y[1] + 0.025):
                G.hex_bolt(bl, (x, y, ZC + 0.01), "z", 0.010, 0.006, washer=False)
        wl = P("post_welds", "weld")
        weld_line(wl, (POST_X[0] - 0.001, POST_Y[0] - 0.0015, ZC + 0.012), (POST_X[1] + 0.001, POST_Y[0] - 0.0015, ZC + 0.012))
        parts += [kn, cap, bl, wl]
    return parts


# =============================================================================
# Registration unit on the box
# =============================================================================
def build_unit(spec):
    lod = spec["lod"]
    parts = []
    poly = [(UY0, UZ0), (UY1, UZ0), (UY1, UZ1), (UY0 + 0.02, UZ1), (UY0, UZ1 - 0.02)]
    bd = P("unit_body", "unit")
    if lod == 0:
        G.prism_bev(bd, poly, UX0, UX1, r=0.0025, seg=1, axes=(1, 2), sides=True)
    else:
        g.prism(bd, poly, (1, 2), UX0, UX1)
    parts.append(bd)
    sd = P("unit_sides", "unit_red")
    big = [(UY0 - 0.004, UZ0 - 0.001), (UY1 + 0.004, UZ0 - 0.001), (UY1 + 0.004, UZ1 + 0.004),
           (UY0 + 0.019, UZ1 + 0.004), (UY0 - 0.004, UZ1 - 0.019)]
    for xa, xb in ((UX0 - 0.006, UX0), (UX1, UX1 + 0.006)):
        if lod == 0:
            G.prism_bev(sd, big, xa, xb, r=0.0018, seg=1, axes=(1, 2), sides=True)
        else:
            g.prism(sd, big, (1, 2), xa, xb)
    parts.append(sd)
    # display: its own texture (section screen), UV 0..1 over the display rectangle
    ds = P("unit_display", "black", group=SEL_SCREEN, section="screen")
    quad_face(ds, UFR, DISP[0], DISP[1], DISP[2], DISP[3], 0.0008)
    ds.glass_frame = (UFR, DISP[0], DISP[1], DISP[2], DISP[3])
    parts.append(ds)
    # needle indicator: a scale (backlit when "working"), the needle is a bone
    dl = P("meter_dial", "dial", group=SEL_POWER)
    quad_face(dl, UFR, MW[0], MW[1], MW[2], MW[3], C_DIAL)
    parts.append(dl)
    # mains lamp
    la, lb = lay.LAMP[0], UZ0 + lay.LAMP[1]
    lp = P("unit_lamp", "lamp_r", group=SEL_POWER)
    if lod == 0:
        G.lathe(lp, [(0.0, 0.0), (0.0058, 0.0), (0.0058, 0.004), (0.0050, 0.0075), (0.0029, 0.0102), (0.0, 0.0108)],
                10, g.Frame(UFR.p(la, lb, 0.0), UFR.u, UFR.v, UFR.n))
    else:
        g.cyl(lp, (la, lb, 0.005), "z", 0.006, 0.008, (10, 6, 4)[lod], frame=UFR)
    parts.append(lp)
    if lod == 2:
        bz = P("meter_bezel", "bezel")
        g.box(bz, lay.METER[0], lay.METER[1], UZ0 + lay.METER[2], UZ0 + lay.METER[3], 0.0, C_DIAL - 0.0002, frame=UFR)
        return parts + [bz]
    # indicator body with a window
    m0, m1, n0, n1 = lay.METER[0], lay.METER[1], UZ0 + lay.METER[2], UZ0 + lay.METER[3]
    bz = P("meter_bezel", "bezel")
    if lod == 0:
        g.box(bz, m0, m1, n0, n1, 0.0, 0.0075, r=0.003, seg=2, frame=UFR)
        cut = P("meter_cut", "bezel")
        g.box(cut, MW[0], MW[1], MW[2], MW[3], C_DIAL - 0.0005, 0.02, frame=UFR)
        bz = M.boolean("meter_bezel", bz, [cut])
    else:
        for a0_, a1_, b0_, b1_ in ((m0, m1, MW[3], n1), (m0, m1, n0, MW[2]), (m0, MW[0], MW[2], MW[3]),
                                   (MW[1], m1, MW[2], MW[3])):
            g.box(bz, a0_, a1_, b0_, b1_, 0.0, 0.0075, frame=UFR)
    parts.append(bz)
    nd = P("meter_needle", "needle", group=SEL_METER)
    a = math.radians(lay.METER_REST)
    nf = g.Frame(UFR.p(PIVOT[0], PIVOT[1], C_NEEDLE), (math.cos(a), 0.0, math.sin(a)), (-math.sin(a), 0.0, math.cos(a)),
                 (0, -1, 0))
    tip = lay.METER_R * 1.0
    blade = [(-0.006, -0.0010), (0.003, -0.0008), (tip, -0.00022), (tip + 0.0008, 0.0), (tip, 0.00022),
             (0.003, 0.0008), (-0.006, 0.0010)] if lod == 0 else [(0.004, -0.0006), (tip, -0.0006), (tip, 0.0006),
                                                                  (0.004, 0.0006)]
    g.prism(nd, blade, (0, 1), -0.0003, 0.0003, frame=nf)
    if lod == 0:
        g.cyl(nd, (0.0, 0.0, 0.0005), "z", 0.0026, 0.0012, 8, frame=nf)
    parts.append(nd)
    if lod == 1:
        hd = P("unit_handle", "steel")
        yc = (UY0 + UY1) / 2 + 0.01
        g.pipe(hd, [(UX0 + 0.035, yc, UZ1), (UX0 + 0.045, yc, UZ1 + 0.026), (UX1 - 0.045, yc, UZ1 + 0.026),
                    (UX1 - 0.035, yc, UZ1)], 0.0055, 4)
        g.box(bz, DISP[0] - 0.006, DISP[1] + 0.006, DISP[2] - 0.006, DISP[3] + 0.006, 0.0, 0.0006, frame=UFR)
        return parts + [hd]

    # --- near LOD: the display surround, face screws, toggles in guards, the threshold knob, the lamp holder
    bzl = P("unit_bezel", "bezel")
    w = 0.006
    a0, a1, b0, b1 = DISP
    for xa, xb, ya, yb in ((a0 - w, a1 + w, b1, b1 + w), (a0 - w, a1 + w, b0 - w, b0), (a0 - w, a0, b0, b1),
                           (a1, a1 + w, b0, b1)):
        g.box(bzl, xa, xb, ya, yb, 0.0, 0.005, frame=UFR)
    parts.append(bzl)
    sc = P("unit_screws", "chrome")
    for x in (UX0 + 0.008, UX1 - 0.008):
        for z in (UZ0 + 0.008, UZ0 + 0.092):
            G.screw(sc, UFR.p(x, z, 0.0), "-y", 0.0032)
    for x in (m0 + 0.005, m1 - 0.005):
        G.screw(sc, UFR.p(x, n0 + 0.005, 0.0075), "-y", 0.0018)
    # lamp holder
    G.lathe(sc, [(0.0058, 0.0), (0.0090, 0.0), (0.0090, 0.0030), (0.0080, 0.0045), (0.0058, 0.0045)], 8,
            g.Frame(UFR.p(la, lb, 0.0), UFR.u, UFR.v, UFR.n), closed=True)
    # toggles: a bushing with a nut, a lever up (channels on), guard cheeks on the sides
    tb = UZ0 + lay.TOG_B
    for x in lay.TOGS:
        fr_ = g.Frame(UFR.p(x, tb, 0.0), UFR.u, UFR.v, UFR.n)
        G.lathe(sc, [(0.0, 0.0), (0.0048, 0.0), (0.0048, 0.008), (0.0, 0.008)], 8, fr_)
        g.prism(sc, G.hexagon(0.0072), (0, 1), 0.0, 0.0032, frame=fr_)
        d = (UFR.n * math.cos(math.radians(62)) + UFR.v * math.sin(math.radians(62))).normalized()
        G.lathe(sc, [(0.0, -0.001), (0.0022, -0.001), (0.0016, 0.012), (0.0024, 0.0185), (0.0, 0.0222)], 6, G.frame_axis(UFR.p(x, tb, 0.007), tuple(d)))
        for e in (-1, 1):
            g.box(bd, x + e * 0.0115 - 0.0012, x + e * 0.0115 + 0.0012, tb - 0.012, tb + 0.014, 0.0, 0.017, frame=UFR,
                  r=0.0008, seg=1)
    parts.append(sc)
    # threshold knob: a skirt, a knurled body, a cap, a mark
    kb = P("unit_knob", "black")
    ka, kbz = lay.KNOB[0], UZ0 + lay.KNOB[1]
    fk = g.Frame(UFR.p(ka, kbz, 0.0), UFR.u, UFR.v, UFR.n)
    r = lay.KNOB_R
    G.lathe(kb, [(r * 1.32, 0.0), (r * 1.32, 0.003), (r * 1.10, 0.0045)], 12, fk)
    g.prism(kb, G.knurl_poly(r, 10, 0.0009), (0, 1), 0.0045, 0.017, frame=fk)
    G.lathe(kb, [(r * 0.92, 0.017), (r * 0.80, 0.0195), (0.0, 0.020)], 12, fk)
    parts.append(kb)
    pt = P("unit_knob_ptr", "steel")
    g.box(pt, ka - 0.0010, ka + 0.0010, kbz + r * 0.2, kbz + r * 0.85, 0.0196, 0.0206, frame=UFR)
    parts.append(pt)
    # ventilation slots on the red sides
    vt = P("unit_vents", "dark")
    for xo, s in ((UX0 - 0.006, -1), (UX1 + 0.006, 1)):
        for k in range(4):
            z = UZ0 + 0.030 + k * 0.012
            g.box(vt, *sorted((xo, xo + s * 0.0004)), 0.37, 0.45, z, z + 0.0035)
    parts.append(vt)
    # bayonet connectors of the frames on the back wall with cable plugs
    cn = P("unit_conn", "black")
    for x in CONN_X:
        g.box(cn, x - 0.012, x + 0.012, UY1, UY1 + 0.002, CONN_Z - 0.012, CONN_Z + 0.012, r=0.0008, seg=1)
        fy = G.frame_at((x, UY1, CONN_Z), "y")
        G.lathe(cn, [(0.0072, 0.002), (0.0072, 0.010), (0.0094, 0.010)], 8, fy)
        g.prism(cn, G.knurl_poly(0.0098, 6, 0.0012), (0, 1), 0.010, 0.024, frame=fy)
        G.lathe(cn, [(0.0086, 0.024), (0.0060, 0.034), (0.0046, 0.046), (0.0, 0.046)], 8, fy)
    parts.append(cn)
    ft = P("unit_feet", "rubber")
    for x in (UX0 + 0.02, UX1 - 0.02):
        for y in (UY0 + 0.02, UY1 - 0.02):
            G.lathe(ft, [(0.0085, LID_TOP), (0.0095, LID_TOP + 0.003), (0.0080, UZ0 + 0.001)], 8,
                    G.frame_at((x, y, 0.0), "z"))
    parts.append(ft)
    # carrying handle on two posts, a rubber pad
    hd = P("unit_handle", "steel")
    yc = (UY0 + UY1) / 2 + 0.01
    for x in (UX0 + 0.035, UX1 - 0.035):
        g.box(bd, x - 0.009, x + 0.009, yc - 0.011, yc + 0.011, UZ1 - 0.001, UZ1 + 0.008, r=0.003, seg=1)
    g.pipe(hd, G.spline([(UX0 + 0.035, yc, UZ1 + 0.004), (UX0 + 0.040, yc, UZ1 + 0.020), (UX0 + 0.060, yc, UZ1 + 0.028),
                         (UX1 - 0.060, yc, UZ1 + 0.028), (UX1 - 0.040, yc, UZ1 + 0.020), (UX1 - 0.035, yc, UZ1 + 0.004)], 2),
           0.0055, 8)
    parts.append(hd)
    gr = P("unit_grip", "rubber")
    g.pipe(gr, [(UX0 + 0.085, yc, UZ1 + 0.028), (UX1 - 0.085, yc, UZ1 + 0.028)], 0.0080, 10)
    parts.append(gr)
    return parts


# =============================================================================
# Cables: from the frames along the bracket and the post down, under the crosspieces along the right
# skid back, up the leg and the box wall - to the connectors on the back wall of the unit
# =============================================================================
def build_cables(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    xr = SKX - SKW / 2 - 0.02                                   # along the right skid, inside
    for i, yf in enumerate(SENS_Y):
        xc = CONN_X[i]
        sg = -1 if i == 0 else 1
        yp = POST_Y[0] - 0.008 if i == 0 else POST_Y[1] + 0.008
        yo = -0.36 if i == 0 else -0.215                        # past the post base plate - onto the floor
        xs = xr - 0.02 * i
        dz = 0.012 * i
        pts = [(SHW + 0.046, yf, SZ0 + 0.03), (SHW + 0.060, yf, SZ0 + 0.012), (POST_X[0] - 0.006, yp, 0.78),
               (POST_X[0] - 0.005, yp, 0.45), (POST_X[0] - 0.006, yp, 0.20), (0.236, yp + sg * 0.02, 0.115),
               (0.215, yo, 0.012), (xs, -0.10, 0.008), (xs, 0.30, 0.008), (xs - 0.02, 0.54, 0.009),
               (BX - 0.012 + 0.006 * i, BY1 + 0.026, 0.15), (BX - 0.04 - 0.01 * i, BY1 + 0.012, BZ0 - 0.02),
               (BX - 0.08 - 0.02 * i, BY1 + 0.008, 1.10), (xc + 0.04, BY1 + 0.010, BZ1 + 0.012 + dz),
               (xc, UY1 + 0.07, CONN_Z), (xc, UY1 + 0.046, CONN_Z)]
        parts += cable("cable_sensor%d" % i, "cable", pts, 0.0042, lod)
    if lod == 0:
        tie = P("cable_ties", "black")
        for z in (0.30, 0.60):
            G.tie_loop(tie, (POST_C[0] - 0.0055, POST_C[1]), 0.0275, 0.035, z)
        parts.append(tie)
    return parts


def build_lod(spec):
    parts = (build_skids(spec) + build_frame(spec) + build_plate(spec) + build_clamps(spec) + build_stand(spec) +
             build_trap(spec) + build_sensors(spec) + build_unit(spec) + build_cables(spec))
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    metal = kx.PEN + r"\metalplate.rvmat"
    wood = kx.PEN + r"\wood.rvmat"
    comps = [
        (kx.box_pts(-UX - A / 2, UX + A / 2, -0.15, FY + A, SKH, ZTOP), metal),            # frame with clamps
        (kx.box_pts(-SKX - SKW / 2, SKX + SKW / 2, -SKY - 0.04, SKY, 0.0, SKH), metal),    # skids
        (kx.box_pts(-BX - 0.05, BX + 0.05, BY0, BY1, SKH, BZ1 + LID_T), wood),             # bullet trap
        (kx.box_pts(UX0 - 0.006, UX1 + 0.006, UY0, UY1, UZ0, UZ1 + 0.035), metal),         # unit
        (kx.box_pts(-SHW, POST_X[1] + 0.04, SENS_Y[0] - 0.04, SENS_Y[1] + 0.04, SKH, SZ1 + 0.015), metal),
    ]
    memory = {
        "invView": [(0.0, -3.0, 1.2)],
        "ce_center": [(0.0, 0.0, 0.8)],
        "ce_radius": [(0.85, 0.0, 0.8)],
        # needle axis: from the pivot toward the person (-y: clockwise rotation seen looking at the unit; METER_AXIS above)
        "ozl_meter_axis": METER_AXIS,
    }
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 180.0, memory, bbox


# the first ones are for the --look preview: the unit close up and the frames (the same when "working":
# display, needle, lamps), overall, the plate through both frames (the way the bullet flies), the clamps,
# the board with small stuff, the shelf under the box
SHOTS = [
    ("unit", (0.02, -0.26, 1.80), (0.13, 0.39, 1.50), 36),
    ("sensors", (0.95, -1.10, 1.45), (0.10, -0.28, 1.00), 32),
    ("front", (-1.5, -3.0, 1.75), (0.0, 0.0, 0.85), 30),
    ("plate", (-0.06, -0.98, 1.08), (0.0, 0.0, 1.05), 42),
    ("clamps", (-0.70, -0.38, 1.10), (-0.10, 0.0, 1.05), 40),
    ("trap", (-0.9, -0.6, 1.95), (0.05, 0.30, 1.40), 30),
    ("shelf", (-1.05, -0.62, 0.78), (-0.02, 0.30, 0.46), 32),
    ("side", (2.6, 0.2, 1.2), (0.0, 0.0, 0.8), 30),
    ("back", (1.4, 2.6, 1.7), (0.0, 0.0, 0.8), 30),
]

M.look_shots = (7, 2)
M.run(build_lod, collision, SHOTS, row_step=1.6, row_shot=((1.6, -6.5, 1.8), (1.6, 0, 0.8)))
