"""M81 - barrel vise (OZL_Tool_BarrelVise): a Ballistic line module, a portable 2x2 item. It sits in
an OZL_Tool1..3 slot of the packer (M23, M27, M32) and shows on its shelf through the module_N
proxy. A small machinist's vise with aluminium jaw pads and wooden inserts for a barrel.

    blender --background --python build_m81.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py (system Python) before the first build: cast digits, pencil, stamp.

Size: the module pad is about 0.2 x 0.2 m, up to about 0.25 m high, flat bottom.

Proportions:
- The look is a Soviet small vise: a cast body in teal-grey enamel worn to cast iron, a rectangular
  slider of the moving jaw, a blued screw with a handle on the end. The sample has a clamp; the
  module has none: it stands on the machine shelf, which has no edge, and needs a flat bottom (as
  M44) - so the body of this non-swivel vise sits on a plate with two ears for bolts.
- TSS-80 (Glazov "Metallist" plant): jaws 80 x 50 mm, travel 100 mm, envelope 255 x 135 x
  120 mm, 4.6 kg; TSSN-80: 255 (270) x 135 x 120 (123) mm, 4.0-4.1 kg.
- TSSN-63-S: jaws 63 mm, opening 80, throat depth 40 mm, 3.7 kg. The TSS-63 envelope was not found,
  so the TSS-80 envelope scaled by 63/80 is used: about 200 x 107 x 95 mm.
- The model is class 63: jaws 63 mm (pads 70), jaw body 68 x 30 x 26 mm, plate 84 x 84 mm with two
  ears (124 mm across with the ears), jaws 96 mm up. Slider 40 x 28 mm; at a 44 mm opening it
  protrudes from the body at the back by 41 mm, so the length from the screw hub to the slider end
  is 201 mm (on a closed vise the slider sticks out further, the length is the same). The handle is
  9 x 132 mm with end caps and lies sideways.
- Between the jaws: aluminium angle pads of 2 mm, two beech inserts 100 x 18 x 34 mm with a barrel
  groove, gap 4 mm. A barrel stub for 7.62 is clamped in them (its axis is 6 mm below the insert
  top, so the barrel shows from above): breech diameter 28 with a shank of diameter 24 for the
  thread, then a cone of diameter 21 -> 17 to the muzzle, a front sight base at the muzzle; length
  196 mm (shorter than a real one - an AKM barrel is 415 mm - to fit the module place). An anvil
  behind the fixed jaw, as on the TSS-80 "with anvil".
- Size 0.20 x 0.20 x 0.114 m - lower than the item card (0.18): real vises of this class are about
  0.10-0.12 m, with the handle sideways. Real mass is about 3.5 kg; the in-game weight is 800 g of
  the OZL_Tool_Base class (module rules untouched), the mass in Geometry is the same.

Details: the "dayz" look (more matte, dirtier, AO in colour). Cast parts instead of boxes: the body
column and the lower part of the moving jaw are a loft of rounded sections with a boss to the
plate (casting fillets); jaws and plate have rounded edges, the anvil a bevel, the ears a chamfer
and countersunk holes. Inserts have a half-round barrel groove (it narrows to the muzzle with the
barrel) and end chamfers; pads are bent angles with a radius. Screw: a thrust washer, a hub with
chamfers, a riveted end, rounded handle caps; a stop screw on the slider end. Barrel: 20 sides,
breech fillets, the shank thread as a pattern (turns at a 1.75 mm pitch, no triangles), an AK front
sight - ring, base, two ears with rounded tops, a post.
No vanilla items: the module is itself a small item in a machine slot, DayZ items lie on the machines.

Condition (no faction colour): used but intact, worn paint on the edges - the body enamel is worn
to cast iron on the jaw edges, the plate and the ears, more on the moving jaw; the slider is bare
ground steel in oil; screw, handle and barrel are blued (rubbed by hands on the handle); pads are
dented aluminium with scratches; inserts are greasy beech. Markings (digits only): cast "63" on the
body side (enamel rubbed off the relief), pencil "7,62" and ticks on the insert, the stamp "3317"
on the breech.
No lamps or screens. Work look (a pose): while the machine works, the handle with the screw hub
(bone ozl_clamp on the source ozl_clamp - OZL_WorkFx pose, like the M16 feed) turns a further 20
degrees clockwise seen from the front - the vise tightens on the barrel; afterwards it goes back.
More than 20 degrees is impossible: the long end of the handle would hit the machine shelf.
LODs: near and mid (no holes in the ears, front sight, washer, handle caps, chamfers; solids of
revolution are sparser), no far one.

Blender axes: X is width, Y is depth (the front, the screw and the handle are at -Y), Z is up. The
origin is the centre of the frame bottom, so the module lands on the module_N proxy point
(autocenter = 0 in Geometry).
"""
import math
import os
import sys

import bmesh
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m -----------------------------------------------------------------------------
YF = 0.0095                     # face of the fixed jaw (hardened plate)
JG = 0.044                      # opening between the hardened jaws
YM = YF - JG                    # face of the moving jaw
JAW_X = 0.0315                  # hardened plate 63 mm
JB_X = 0.034                    # jaw body 68 mm
Z_JAW, Z_JB = (0.074, 0.096), (0.070, 0.096)
PAD_X, PAD_T = 0.035, 0.002     # angle pad 70 mm
WT, WG, W_X, Z_W = 0.018, 0.004, 0.050, (0.064, 0.098)     # inserts: thickness, gap, half-length, height
YC, ZB = YF - JG / 2, 0.092                 # barrel axis: 6 mm below the top of the inserts - the barrel shows in the groove
ZS = 0.048                      # screw axis
BEAM_X, Z_BEAM = 0.020, (0.034, 0.062)
Y_FRONT = YM - 0.066            # front of the screw hub
Y_REAR = -Y_FRONT               # slider end: the frame is symmetric in Y
WEB_X = 0.029                   # fixed-body column 58 mm (cast digits on its left side)
BASE = (0.042, YF - 0.010, YF + 0.074, 0.012)               # plate: half-width, y0, y1, thickness
EAR_Y, EAR_R, EAR_T, HOLE_R = YF + 0.036, 0.014, 0.009, 0.0055
MW_X = 0.026                    # bottom of the moving jaw
Y_HANDLE = YM - 0.056
H_X0, H_X1, H_R = -0.044, 0.088, 0.0045
# barrel: (r, x) along X from the breech; the bore for 7.62
X_B0, X_B1 = -0.098, 0.098
BORE_R, CH_R = 0.0039, 0.0060
SIGHT_X = 0.078
# fixed-body column is a casting: sections from the bottom up (z, half-width, y0, y1, corner
# radius); the lower two are the boss to the plate (a fillet), the upper one is under the jaw body.
# The slider passes through the column.
COLUMN = [
    (0.0115, 0.0350, YF - 0.0050, YF + 0.0670, 0.010),
    (0.0150, 0.0318, YF - 0.0005, YF + 0.0615, 0.009),
    (0.0210, 0.0298, YF + 0.0035, YF + 0.0555, 0.008),
    (0.0300, WEB_X, YF + 0.0060, YF + 0.0505, 0.007),
    (0.0640, WEB_X, YF + 0.0060, YF + 0.0505, 0.007),
    (0.0750, WEB_X + 0.001, YF + 0.0060, YF + 0.0450, 0.006),   # goes into the jaw body and under the anvil
]


def jaw_rings(y_in, y_out):
    """Jaw body is a casting: narrower at the bottom (a draft), ribs rounded, the top rounded along the
    outer edges; the face at the hardened plate (y_in) is straight. y_out is the outer face (the moving
    jaw's front, the fixed jaw's rear).
    """
    s = 1 if y_out > y_in else -1

    def sec(z, hw, d, r):
        y0, y1 = sorted((y_in, y_out - s * d))
        return (z, hw, y0, y1, r)
    return [sec(Z_JB[0], JB_X - 0.002, 0.001, 0.004), sec(0.0925, JB_X, 0.0, 0.005),
            sec(0.0950, JB_X - 0.0008, 0.0008, 0.0045), sec(Z_JB[1], JB_X - 0.0025, 0.0025, 0.003)]
# bottom of the moving jaw (it hugs the slider and the screw nut): the face leans forward at the
# bottom, rounded underneath
MOVING = [
    (0.0255, 0.0205, YM - 0.0370, YM - 0.0080, 0.006),
    (0.0285, 0.0245, YM - 0.0395, YM - 0.0067, 0.008),
    (0.0340, MW_X, YM - 0.0400, YM - 0.0062, 0.009),
    (0.0500, MW_X, YM - 0.0390, YM - 0.0062, 0.009),
    (0.0660, MW_X, YM - 0.0370, YM - 0.0062, 0.009),
    (0.0725, MW_X + 0.003, YM - 0.0340, YM - 0.0062, 0.008),    # goes into the jaw body
]
# anvil behind the fixed jaw: profile (y, z), a bevel to the rear-bottom
ANVIL = [(YF + 0.032, 0.072), (YF + 0.050, 0.075), (YF + 0.0565, 0.084), (YF + 0.0565, 0.092), (YF + 0.032, 0.092)]
ANVIL_X = 0.026
# insert groove: radius at the breech and at the muzzle (0.2-0.3 mm larger than the barrel there)
GROOVE_R = (0.0106, 0.0094)

LOD_SPECS = [
    dict(lod=0, sides=20, hub=20, rod=12, cap=10, arc=6, corner=3),
    dict(lod=1, sides=12, hub=12, rod=8, cap=0, arc=4, corner=2),
]

REGIONS = {
    "body": ("body", 1.0), "jaw_m": ("jaw_m", 1.0), "jaws": ("jaws", 1.0), "beam": ("beam", 1.0),
    "blued": ("blued", 1.3), "handle": ("handle", 1.3), "alu": ("alu", 1.2),
    "wood_f": ("wood_f", 1.1), "wood_m": ("wood_m", 1.1), "barrel": ("barrel", 1.5), "bore": ("bore", 0.4),
    "crown": ("crown", 1.0), "thread": ("thread", 2.0),
}

# work look: the handle with the screw hub turns further - a pose on the source ozl_clamp
SEL_CLAMP = "ozl_clamp"
CLAMP_TURN = math.radians(20.0)
CLAMP_ANIM = ("ozl_clamp_turn", dict(type="rotation", source="ozl_clamp", selection=SEL_CLAMP, axis="ozl_clamp_axis",
                                     memory=1, minValue=0.0, maxValue=1.0, angle0=0.0, angle1=CLAMP_TURN))


def wdecal(name):
    return os.path.join(WORK, name)


# decals: (image, normal axis, sign, (u axis, v axis), centre (u, v), size (w, h; the sign is the
# direction, so that the image reads from outside), range along the normal)
CAST = (wdecal("decal_cast.png"), "x", -1, ("y", "z"), (YF + 0.028, 0.047), (-0.022, 0.013),
        (-WEB_X - 0.002, -WEB_X + 0.002))
PENCIL = (wdecal("decal_pencil.png"), "z", 1, ("x", "y"), (-0.028, YF - PAD_T - 0.0055), (0.0233, 0.007),
          (Z_W[1] - 0.002, Z_W[1] + 0.002))
STAMP = (wdecal("decal_stamp.png"), "y", -1, ("x", "z"), (X_B0 + 0.017, ZB), (0.016, 0.004),
         (YC - 0.016, YC - 0.009))


# --- materials ----------------------------------------------------------------------------------
def mat_worn(mat, origin, color, under, seed=1.0, gloss=0.38, spec=0.28, chip=(0.60, 0.66), rub=0.0,
             chip_rust=0.15, rust=(0.70, 0.78), rust_low=0.2, floor_z=0.0, dust=0.3, grime=0.45, edge_r=0.003,
             decal_items=()):
    """Enamel over cast iron worn by work (as on the sample photo): chips along the edges and large
    patches where the paint was rubbed off by hands and workpieces (rub is their strength, more on
    faces looking up); grey cast iron under the enamel, polished where worn; rust only in part of the
    chips (chip_rust) and as rare specks. kmats.build_paint paints every chip with rust at 60 % - on a
    vise in use the metal in the chips is grey. edge_r is the radius for finding an edge: with rounded
    edges (3 mm chamfer) the old 3 mm made the edge wear almost vanish.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.88 for c in color[:3]) + (1,), color)
    col = kmats.decals(t, base, sep, nsep, decal_items)
    edge = t.maprange(t.edge_wear(edge_r), 0.06, 0.25, 0.0, 1.0)
    blot = t.noise(vec, 11.0, 10.0, 0.7)
    up = t.maprange(nsep.outputs["Z"], 0.2, 0.9, 0.4, 1.0)
    big = t.math("MULTIPLY", t.maprange(t.noise(vec, 2.2, 5.0, 0.6), 0.45, 0.75, 0.0, 1.0), t.math("MULTIPLY", up, rub))
    w = t.math("ADD", t.math("ADD", t.math("MULTIPLY", blot, 0.75), t.math("MULTIPLY", edge, 0.55)), big)
    chips = t.step(w, chip[0], chip[1])
    metal = t.mixc(t.maprange(t.noise(vec, 28.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                   tuple(c * 0.80 for c in under[:3]) + (1,), tuple(min(1.0, c * 1.25) for c in under[:3]) + (1,))
    col = t.mixc(chips, col, metal)
    low = t.maprange(sep.outputs["Z"], floor_z + 0.5, floor_z, 0.0, rust_low)
    speck = t.step(t.noise(vec, 24.0, 8.0, 0.7), rust[0], rust[1])
    some = t.step(t.noise(vec, 6.0, 4.0, 0.6), 0.55, 0.70)
    rust_amt = t.math("MAXIMUM", t.math("MULTIPLY", t.math("MULTIPLY", chips, some), chip_rust),
                      t.math("MULTIPLY", speck, t.math("ADD", 0.25, low)))
    rust_col = t.ramp(t.noise(vec, 30.0, 6.0, 0.6), [(0.3, kmats.RUST[0]), (0.55, kmats.RUST[1]), (0.8, kmats.RUST[2])])
    col = t.mixc(t.math("MULTIPLY", rust_amt, 0.9), col, rust_col)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    gl = t.math("SUBTRACT", t.mixf(chips, gloss, 0.50), t.math("ADD", t.math("MULTIPLY", rust_amt, 0.3),
                                                               t.math("MULTIPLY", dirt, gloss * 0.5)))
    sp = t.math("SUBTRACT", t.mixf(chips, spec, 0.55), t.math("ADD", t.math("MULTIPLY", rust_amt, 0.3),
                                                              t.math("MULTIPLY", dirt, spec * 0.4)))
    h = t.math("ADD", t.math("MULTIPLY", chips, -0.4), t.math("MULTIPLY", rust_amt, t.noise(vec, 90.0, 4.0, 0.6)))
    return kmats.out(t, col, gl, sp, h)


def mat_wood(mat, origin, color, seed=1.0, scale=7.0, along="x", gloss=0.16, spec=0.10, floor_z=0.0, dust=0.2,
             grime=0.5, rings=0.6, knots=0.4, oil=0.35, decal_items=()):
    """Beech inserts - kwood.build_wood at a small scale: the kwood pattern is made for furniture boards
    (growth rings about every 10 cm) and is invisible on an 18 mm bar; here the coordinates are
    multiplied by scale. oil is the greasiness: dark oil stains from the barrel and the jaws.
    """
    t = kmats.Tree(mat)
    vec0, sep = t.coords(origin, seed)
    vec = t.stretch(vec0, scale, scale, scale)
    nsep = t.normal()
    k = {"x": (0.04, 1.0, 1.0), "y": (1.0, 0.04, 1.0), "z": (1.0, 1.0, 0.04)}[along]
    fib = t.stretch(vec, *k)
    fibers = t.noise(fib, 60.0, 4.0, 0.7)
    wave = t.node("ShaderNodeTexWave", Scale=4.0, Distortion=5.0, **{"Detail": 3.0, "Detail Scale": 1.5})
    wave.wave_type = "RINGS"
    t.link(fib, wave.inputs["Vector"])
    ring = t.math("MULTIPLY", wave.outputs["Fac"], rings)
    tone = t.maprange(t.noise(vec, 0.8, 3.0, 0.5), 0.3, 0.7, 0.0, 1.0)
    dark = tuple(c * 0.62 for c in color[:3]) + (1,)
    light = tuple(min(1.0, c * 1.22) for c in color[:3]) + (1,)
    col = t.mixc(tone, tuple(c * 0.90 for c in color[:3]) + (1,), tuple(min(1.0, c * 1.06) for c in color[:3]) + (1,))
    col = t.mixc(t.math("MULTIPLY", ring, 0.8), col, dark)
    col = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", fibers, 0.35), 0.6), col, dark)
    knot = t.step(t.noise(t.stretch(vec, *[0.4 if x < 1 else 1.0 for x in k]), 3.0, 2.0, 0.5),
                  1.0 - 0.06 * knots, 1.0 - 0.03 * knots)
    col = t.mixc(t.math("MULTIPLY", knot, 0.85), col, tuple(c * 0.35 for c in color[:3]) + (1,))
    stain = t.math("MULTIPLY", t.maprange(t.noise(vec0, 18.0, 4.0, 0.6), 0.48, 0.70, 0.0, 1.0), oil)
    col = t.mixc(stain, col, tuple(c * 0.45 for c in color[:3]) + (1,))
    col = kmats.decals(t, col, sep, nsep, decal_items)
    edge = t.maprange(t.edge_wear(0.002), 0.06, 0.25, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.40), col, light)
    col, dirt = kmats.weather(t, col, vec0, sep, nsep, floor_z, dust, grime, 0.5)
    g = t.math("ADD", t.math("SUBTRACT", gloss, t.math("MULTIPLY", dirt, gloss * 0.6)), t.math("MULTIPLY", stain, 0.2))
    s = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.5))
    h = t.math("ADD", t.math("MULTIPLY", fibers, 0.25), t.math("MULTIPLY", ring, -0.25))
    h = t.math("SUBTRACT", h, t.math("MULTIPLY", knot, 0.3))
    return kmats.out(t, col, g, s, h)


def mat_thread(mat, origin, color, under, seed=1.0, pitch=0.00175, gloss=0.50, spec=0.50, floor_z=0.0,
               dust=0.10, grime=0.6):
    """Barrel shank thread as a pattern, no triangles: turns across the X axis (the barrel lies along X) -
    a triangle wave in x; crests are rubbed to steel, in the valleys bluing, oil and dirt; the relief
    is the same wave (in game - _nohq).
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    q = t.math("FRACT", t.math("DIVIDE", sep.outputs["X"], pitch))
    crest = t.math("ABSOLUTE", t.math("SUBTRACT", t.math("MULTIPLY", q, 2.0), 1.0))   # 1 is a crest, 0 is a valley
    top = t.step(crest, 0.55, 0.85)
    steel = t.mixc(t.maprange(t.noise(vec, 40.0, 4.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                   tuple(c * 0.75 for c in under[:3]) + (1,), under)
    col = t.mixc(top, color, steel)
    col = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", 1.0, crest), 0.6), col, kmats.GRIME)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    gl = t.math("SUBTRACT", t.mixf(top, gloss * 0.7, gloss), t.math("MULTIPLY", dirt, gloss * 0.4))
    sp = t.math("SUBTRACT", t.mixf(top, spec * 0.6, spec), t.math("MULTIPLY", dirt, spec * 0.4))
    h = t.math("MULTIPLY", t.math("SUBTRACT", crest, 0.5), 0.9)
    return kmats.out(t, col, gl, sp, h)


# enamel is darker and dirtier than a plain pass (vanilla furniture workshop has L 31...78), wear is
# stronger - on the sample the enamel is worn to cast iron on the edges and in patches on the jaw
# tops. Dust is weaker than usual: the "dayz" profile multiplies it by 1.8, and light dust on teal
# and beech whitens the whole top
TEAL = kmats.lin((64, 102, 100))         # grey-teal enamel of Soviet vises (muted)
IRON = kmats.lin((80, 78, 74))           # cast iron under the enamel
BLUED = kmats.lin((34, 36, 42))
STEEL_BRIGHT = kmats.lin((150, 150, 154))
WOOD = kmats.lin((142, 108, 76))         # beech darkened by oil
ALU = dict(color=kmats.lin((122, 124, 123)), under=kmats.lin((88, 90, 89)), gloss=0.36, spec=0.36,
           chip=(0.60, 0.66), rust=(0.98, 0.99), rust_low=0.0, floor_z=0.0, dust=0.08, grime=0.65)
PAINT = dict(color=TEAL, under=IRON, gloss=0.38, spec=0.28, rust=(0.72, 0.80), rust_low=0.20, floor_z=0.0,
             dust=0.12, grime=0.70, edge_r=0.006)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    # cast body and plate: enamel worn to cast iron on the edges, rare rust in the chips
    "body": (mat_worn, dict(PAINT, seed=2.2, chip=(0.55, 0.61), rub=0.28, decal_items=[CAST])),
    # moving jaw: it is turned and hit - more chips
    "jaw_m": (mat_worn, dict(PAINT, seed=4.4, chip=(0.53, 0.59), rub=0.38)),
    # hardened jaws, thrust washer: dark steel
    "jaws": ("steel", dict(seed=3.1, tone=0.15, along="x", gloss=0.45, spec=0.50, dust=0.08, grime=0.6)),
    # slider: ground steel in oil
    "beam": ("steel", dict(seed=5.3, tone=0.30, along="y", gloss=0.62, spec=0.70, dust=0.06, grime=0.75)),
    # screw, hub: bluing, rubbed off on the edges
    "blued": ("paint", dict(color=BLUED, under=STEEL_BRIGHT, seed=6.1, gloss=0.60, spec=0.55, chip=(0.76, 0.82),
                            rust=(0.93, 0.98), rust_low=0.0, dust=0.06, grime=0.3)),
    # handle: bluing rubbed off by palms
    "handle": ("paint", dict(color=BLUED, under=STEEL_BRIGHT, seed=7.3, gloss=0.62, spec=0.58, chip=(0.62, 0.68),
                             rust=(0.93, 0.98), rust_low=0.0, dust=0.05, grime=0.2)),
    "alu": ("paint", dict(ALU, seed=8.2)),
    "wood_f": (mat_wood, dict(color=WOOD, seed=1.7, along="x", oil=0.50, dust=0.10, grime=0.7, decal_items=[PENCIL])),
    "wood_m": (mat_wood, dict(color=WOOD, seed=3.9, along="x", oil=0.60, dust=0.10, grime=0.7)),
    # barrel: bluing, rubbed on the edges, the stamp on the breech
    "barrel": ("paint", dict(color=kmats.lin((26, 27, 31)), under=STEEL_BRIGHT, seed=9.4, gloss=0.55, spec=0.50,
                             chip=(0.76, 0.82), rust=(0.95, 0.99), rust_low=0.0, dust=0.05, grime=0.30,
                             decal_items=[STAMP])),
    "thread": (mat_thread, dict(color=kmats.lin((28, 29, 33)), under=kmats.lin((120, 120, 124)), seed=9.1,
                                dust=0.05)),
    "bore": ("flat", dict(color=kmats.lin((10, 10, 11)), gloss=0.3, spec=0.2)),
    "crown": ("steel", dict(seed=9.9, tone=0.34, along="z", gloss=0.7, spec=0.8, dust=0.05, grime=0.1)),
})

OBJ, NAME = "m81_barrel_vise", "ozr_barrel_vise"
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL_CLAMP,), bones=((SEL_CLAMP, ""),), animations=(CLAMP_ANIM,),
                 sources={"ozl_clamp": dict(animPeriod=0.8)})
P = M.part
BOUNDS = {}
LOD0 = []                       # near-LOD parts - for the work-pose preview (render_work)


# --- helpers ------------------------------------------------------------------------------------
def lathe(part, fr, prof, sides, cap_lo=False, cap_hi=False):
    """Solid of revolution about fr.n (from the M76 generator): the profile [(r, h)] goes so that the
    outside is on the right (segment normal (dh, -dr)); the cap of the first ring looks to -n, the
    last to +n.
    """
    bm = part.bm
    angs = [2 * math.pi * k / sides for k in range(sides)]
    rings = [[bm.verts.new(fr.p(r * math.cos(a), r * math.sin(a), h)) for a in angs] for r, h in prof]
    faces = []
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        for k in range(sides):
            j = (k + 1) % sides
            f = bm.faces.new([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]])
            am = (k + 0.5) * 2 * math.pi / sides
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


def frame_x(x, y, z):
    """Rotation axis is +X (barrel, handle)."""
    return g.Frame((x, y, z), (0, 1, 0), (0, 0, 1), (1, 0, 0))


def frame_front(y):
    """Rotation axis is forward, -Y (boss and screw hub)."""
    return g.Frame((0, y, ZS), (1, 0, 0), (0, 0, 1), (0, -1, 0))


def bev(spec, r=0.002, seg=1):
    return {"r": r, "seg": seg} if spec["lod"] == 0 else {}


def poly_area(poly):
    n = len(poly)
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))


def ccw(poly):
    return list(poly) if poly_area(poly) > 0 else list(poly)[::-1]


def offset_poly(poly, d):
    """Counter-clockwise outline offset outward by d (d < 0 is inward): a vertex moves along the bisector
    of the neighbouring edge normals (at sharp corners no further than about 3d).
    """
    n = len(poly)
    out = []
    for i in range(n):
        a, p, b = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % n])
        e1, e2 = p - a, b - p
        n1 = Vector((e1.y, -e1.x)).normalized()
        n2 = Vector((e2.y, -e2.x)).normalized()
        m = n1 + n2
        m = n1 if m.length < 1e-9 else m.normalized()
        k = max(0.35, m.dot(n1))
        q = p + m * (d / k)
        out.append((q.x, q.y))
    return out


def round_poly(poly, radii, seg):
    """Round the outline corners: radii is a number or a per-vertex list (0 leaves the corner); the arc is
    a quadratic curve from a point on the incoming edge through the corner to a point on the outgoing
    edge (tangent to the edges), seg segments. The point count does not depend on the sizes - outlines
    of one kind can be lofted into each other.
    """
    n = len(poly)
    out = []
    for i in range(n):
        r = radii[i] if isinstance(radii, (list, tuple)) else radii
        p = Vector(poly[i])
        if r <= 0 or seg < 1:
            out.append((p.x, p.y))
            continue
        ua, ub = Vector(poly[i - 1]) - p, Vector(poly[(i + 1) % n]) - p
        la, lb = ua.length, ub.length
        ua.normalize()
        ub.normalize()
        half = math.acos(max(-1.0, min(1.0, ua.dot(ub)))) / 2
        t = min(r / max(math.tan(half), 1e-3), 0.45 * la, 0.45 * lb)
        A, B = p + ua * t, p + ub * t
        for k in range(seg + 1):
            s = k / seg
            q = A * (1 - s) ** 2 + p * (2 * (1 - s) * s) + B * (s * s)
            out.append((q.x, q.y))
    return out


def ring3(poly, axis, c):
    """2D outline into 3D: axis is the extrusion axis ('x': the outline is in (y, z); 'y': (x, z); 'z': (x, y))."""
    if axis == "x":
        return [(c, a, b) for a, b in poly]
    if axis == "y":
        return [(a, c, b) for a, b in poly]
    return [(a, b, c) for a, b in poly]


def loft(part, rings, cap0=True, cap1=True):
    """Shell through rings with the same point count (castings, inserts): neighbouring rings are a strip
    of quads, the first and last are caps.
    """
    bm = part.bm
    vs = [[bm.verts.new(Vector(p)) for p in r] for r in rings]
    n = len(rings[0])
    faces = []
    for i in range(len(vs) - 1):
        for k in range(n):
            j = (k + 1) % n
            faces.append(bm.faces.new([vs[i][k], vs[i][j], vs[i + 1][j], vs[i + 1][k]]))
    if cap0:
        faces.append(bm.faces.new(vs[0][::-1]))
    if cap1:
        faces.append(bm.faces.new(vs[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return part.tag(faces)


def cprism(part, poly, axis, c0, c1, ch=0.0):
    """Prism with a chamfer ch on the end edges (the outline at the end is moved inward)."""
    poly = ccw(poly)
    if ch <= 0:
        return loft(part, [ring3(poly, axis, c0), ring3(poly, axis, c1)])
    inner = offset_poly(poly, -ch)
    return loft(part, [ring3(inner, axis, c0), ring3(poly, axis, c0 + ch), ring3(poly, axis, c1 - ch),
                       ring3(inner, axis, c1)])


def rrect(hw, y0, y1, r, n):
    """Rounded rectangle in plan (x, y), counter-clockwise: x from -hw to hw, n segments per corner."""
    pts = []
    for cx, cy, a0 in ((hw - r, y0 + r, -90.0), (hw - r, y1 - r, 0.0), (-hw + r, y1 - r, 90.0), (-hw + r, y0 + r, 180.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def cast_loft(part, sections, n):
    """Cast column: sections (z, half-width, y0, y1, corner radius) are rounded rectangles."""
    return loft(part, [ring3(rrect(hw, y0, y1, r, n), "z", z) for z, hw, y0, y1, r in sections])


# --- fixed body ----------------------------------------------------------------------------
def build_base(spec):
    """Plate with two ears for bolts, a cast column with a boss to the plate, the jaw body, the anvil."""
    lod = spec["lod"]
    hx, y0, y1, t = BASE
    base = P("base", "body")
    g.box(base, -hx, hx, y0, y1, 0.0, t, **bev(spec, 0.003, 2))
    parts = [base]
    n_arc = 8 if lod == 0 else 4
    for s in (-1, 1):
        ear = P("ear_%s" % ("l" if s < 0 else "r"), "body")
        poly = [(s * (hx - 0.002), EAR_Y + EAR_R)]
        for k in range(n_arc + 1):
            a = math.pi / 2 - math.pi * k / n_arc
            poly.append((s * (hx + 0.006 + EAR_R * math.cos(a)), EAR_Y + EAR_R * math.sin(a)))
        poly.append((s * (hx - 0.002), EAR_Y - EAR_R))
        if lod == 0:
            cprism(ear, poly, "z", 0.0, EAR_T, 0.0012)
            # bolt hole with a countersink on top
            cut = P("ear_cut", "body")
            fr = g.Frame((s * (hx + 0.007), EAR_Y, 0.0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
            lathe(cut, fr, [(HOLE_R, -0.003), (HOLE_R, EAR_T - 0.0012), (HOLE_R + 0.0014, EAR_T + 0.0002),
                            (HOLE_R + 0.0034, EAR_T + 0.0030)], 12, cap_lo=True, cap_hi=True)
            ear = M.boolean("ear_%s_h" % ("l" if s < 0 else "r"), ear, [cut])
        else:
            g.prism(ear, poly, (0, 1), 0.0, EAR_T)
        parts.append(ear)
    col = P("column", "body")
    if lod == 0:
        cast_loft(col, COLUMN, spec["corner"])
    else:
        cast_loft(col, [COLUMN[1], COLUMN[3], COLUMN[5]], spec["corner"])
    jb = P("jaw_f", "body")
    if lod == 0:
        cast_loft(jb, jaw_rings(YF + 0.006, YF + 0.036), spec["corner"])
    else:
        g.box(jb, -JB_X, JB_X, YF + 0.006, YF + 0.036, Z_JB[0], Z_JB[1])
    # anvil behind the fixed jaw (the TSS-80 "with anvil"): a bevel to the rear, rounded edges
    if lod == 0:
        cprism(jb, round_poly(ANVIL, [0.0, 0.002, 0.002, 0.0015, 0.0], 2), "x", -ANVIL_X, ANVIL_X, 0.0012)
    else:
        g.prism(jb, ANVIL, (1, 2), -ANVIL_X, ANVIL_X)
    jp = P("jawplate_f", "jaws")
    g.box(jp, -JAW_X, JAW_X, YF, YF + 0.006, Z_JAW[0], Z_JAW[1])
    return parts + [col, jb, jp]


# --- moving jaw, slider, screw ------------------------------------------------------------
def build_moving(spec):
    lod = spec["lod"]
    jb = P("jaw_m", "jaw_m")
    if lod == 0:
        cast_loft(jb, jaw_rings(YM - 0.006, YM - 0.036), spec["corner"])
    else:
        g.box(jb, -JB_X, JB_X, YM - 0.036, YM - 0.006, Z_JB[0], Z_JB[1])
    cast_loft(jb, MOVING if lod == 0 else [MOVING[1], MOVING[3], MOVING[5]], spec["corner"])
    # screw nut boss on the jaw face
    boss = [(0.015, 0.0), (0.015, 0.0062), (0.0140, 0.0078), (0.0128, 0.0080)] if lod == 0 else \
        [(0.015, 0.0), (0.015, 0.0080)]
    lathe(jb, frame_front(YM - 0.036), boss, spec["hub"], cap_hi=True)
    jp = P("jawplate_m", "jaws")
    g.box(jp, -JAW_X, JAW_X, YM - 0.006, YM, Z_JAW[0], Z_JAW[1])
    beam = P("beam", "beam")
    g.box(beam, -BEAM_X, BEAM_X, YM - 0.030, Y_REAR - (0.0015 if lod == 0 else 0.0), Z_BEAM[0], Z_BEAM[1],
          **bev(spec, 0.0015))
    parts = [jb, jp, beam]
    if lod == 0:
        # stop screw on the slider end: it keeps the jaw from being unscrewed
        fr = g.Frame((0, Y_REAR - 0.0015, ZS), (1, 0, 0), (0, 0, 1), (0, 1, 0))
        lathe(beam, fr, [(0.0050, 0.0), (0.0050, 0.0007), (0.0043, 0.0015)], 12, cap_hi=True)
        # thrust washer between the boss and the hub
        wash = P("washer", "jaws")
        lathe(wash, frame_front(YM - 0.044), [(0.0130, 0.0), (0.0130, 0.0013)], spec["hub"], cap_hi=True)
        parts.append(wash)
    # screw hub and handle - the work-look bone ozl_clamp (rotation about the screw axis)
    hub = P("hub", "blued", group=SEL_CLAMP)
    if lod == 0:
        lathe(hub, frame_front(YM - 0.0453), [(0.0110, 0.0), (0.0120, 0.0010), (0.0120, 0.0196), (0.0108, 0.0207)],
              spec["hub"], cap_hi=True)
        # screw end in the hub - riveted, sticks out slightly
        lathe(hub, frame_front(Y_FRONT), [(0.0058, 0.0), (0.0058, 0.0008), (0.0050, 0.0016), (0.0036, 0.0020)], 10,
              cap_hi=True)
    else:
        lathe(hub, frame_front(YM - 0.044), [(0.012, 0.0), (0.012, 0.022)], spec["hub"], cap_hi=True)
    hd = P("handle", "handle", group=SEL_CLAMP)
    g.pipe(hd, [(H_X0, Y_HANDLE, ZS), (H_X1, Y_HANDLE, ZS)], H_R, spec["rod"])
    if lod == 0:                     # handle end caps - pressed on, the end rounded
        for x0, sgn in ((H_X0, -1), (H_X1, 1)):
            prof = [(0.0045, 0.0), (0.0068, 0.0007), (0.0075, 0.0020), (0.0075, 0.0072), (0.0068, 0.0090),
                    (0.0050, 0.0101), (0.0025, 0.0106)]
            fr = g.Frame((x0 - 0.004 * sgn, Y_HANDLE, ZS), (0, 1, 0), (0, 0, 1), (sgn, 0, 0))
            lathe(hd, fr, prof, spec["cap"], cap_hi=True)
    return parts + [hub, hd]


# --- pads, inserts, barrel ----------------------------------------------------------------
def build_pads(spec):
    """Aluminium angles on the jaws: a sheet on the jaw face, a flange on its top; the bend is rounded."""
    pad = P("pads", "alu")
    for y0, s in ((YF, 1), (YM, -1)):
        poly = [(y0 - s * PAD_T, 0.068), (y0, 0.068), (y0, Z_JB[1]), (y0 + s * 0.013, Z_JB[1]),
                (y0 + s * 0.013, Z_JB[1] + PAD_T), (y0 - s * PAD_T, Z_JB[1] + PAD_T)]
        if spec["lod"] == 0:
            poly = round_poly(poly, [0.0, 0.0, 0.001, 0.0, 0.0, 0.003], 3)
        g.prism(pad, poly, (1, 2), -PAD_X, PAD_X)
    return [pad]


def wood_poly(R, spec):
    """Profile (y, z) of the fixed jaw's insert, counter-clockwise: a half-round groove of radius R around
    the barrel axis opens to the top and to the inner face; edges are rounded (near LOD).
    """
    y_in, y_out = YF - PAD_T - WT, YF - PAD_T
    z0, z1 = Z_W
    dz = z1 - ZB
    yt = YC + math.sqrt(R * R - dz * dz)
    zi = ZB - math.sqrt(R * R - (y_in - YC) ** 2)
    a0, a1 = math.atan2(dz, yt - YC), math.atan2(zi - ZB, y_in - YC)
    n = spec["arc"]
    arc = [(YC + R * math.cos(a0 + (a1 - a0) * k / n), ZB + R * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)]
    poly = [(y_in, z0), (y_out, z0), (y_out, z1)] + arc
    if spec["lod"] == 0:
        radii = [0.0015, 0.0015, 0.0015, 0.0008] + [0.0] * (n - 1) + [0.0008]
        poly = round_poly(poly, radii, 2)
    return poly


def build_wood(spec):
    """Beech inserts: the groove narrows toward the muzzle with the barrel (radius at the breech and at
    the muzzle), end chamfers; the moving jaw's insert is a mirror about the barrel axis.
    """
    out = []
    for name, side in (("wood_f", 1), ("wood_m", -1)):
        part = P(name, name)

        def prof(x, d=0.0):
            u = (x + W_X) / (2 * W_X)
            poly = wood_poly(GROOVE_R[0] + (GROOVE_R[1] - GROOVE_R[0]) * u, spec)
            if side < 0:
                poly = [(2 * YC - y, z) for y, z in poly][::-1]
            if d:
                poly = offset_poly(poly, d)
            return ring3(poly, "x", x)
        if spec["lod"] == 0:
            ch = 0.0012
            loft(part, [prof(-W_X, -ch), prof(-W_X + ch), prof(W_X - ch), prof(W_X, -ch)])
        else:
            loft(part, [prof(-W_X), prof(W_X)])
        out.append(part)
    return out


def build_barrel(spec):
    """Barrel stub: a shank of diameter 24 for the thread (turns as a pattern) and the chamber on the
    left, a breech of diameter 28 with fillets, a cone to the muzzle, the AK front sight base at the
    muzzle; the muzzle has a 7.62 bore and a rounded cut.
    """
    lod, n = spec["lod"], spec["sides"]
    L = X_B1 - X_B0
    fr = frame_x(X_B0, YC, ZB)
    b = P("barrel", "thread")
    lathe(b, fr, [(CH_R, 0.0), (0.0110, 0.0), (0.0120, 0.0010), (0.0120, 0.0110)], n)
    b.use("barrel", *REGIONS["barrel"])
    if lod == 0:
        prof = [(0.0120, 0.0110), (0.0134, 0.0118), (0.0140, 0.0128), (0.0140, 0.0294), (0.0136, 0.0310),
                (0.0119, 0.0350), (0.0107, 0.0374), (0.0103, 0.0392), (0.0100, 0.0900), (0.0085, L - 0.0015)]
    else:
        prof = [(0.0120, 0.0110), (0.0140, 0.0125), (0.0140, 0.0300), (0.0105, 0.0380), (0.0100, 0.0900),
                (0.0085, L - 0.0015)]
    lathe(b, fr, prof, n)
    b.use("crown", *REGIONS["crown"])
    lathe(b, fr, [(0.0085, L - 0.0015), (0.0078, L), (BORE_R + 0.0008, L), (BORE_R, L - 0.0006)], n)
    b.use("bore", *REGIONS["bore"])
    lathe(b, fr, [(BORE_R, L - 0.0006), (BORE_R, L - 0.006)], max(6, n // 2), cap_hi=True)
    lathe(b, fr, [(CH_R, 0.006), (CH_R, 0.0)], max(6, n // 2), cap_lo=True)
    parts = [b]
    if lod == 0:
        # AK front sight base: a collar on the barrel, a platform, two ears with rounded tops, the
        # sight post
        s = P("sight", "barrel")
        h = SIGHT_X - X_B0
        r = 0.0100 - (0.0100 - 0.0085) * (h - 0.090) / (L - 0.090 - 0.0015) + 0.0012
        lathe(s, frame_x(SIGHT_X - 0.006, YC, ZB), [(r - 0.0006, 0.0), (r, 0.0008), (r, 0.0112), (r - 0.0006, 0.012)],
              14, cap_lo=True, cap_hi=True)
        z0 = ZB + r - 0.002
        g.box(s, SIGHT_X - 0.005, SIGHT_X + 0.005, YC - 0.0068, YC + 0.0068, z0, z0 + 0.0045, r=0.0008, seg=1)
        zc, er = z0 + 0.0098, 0.004
        ear = [(SIGHT_X - er, z0 + 0.003), (SIGHT_X + er, z0 + 0.003)] + \
              [(SIGHT_X + er * math.cos(math.pi * k / 6), zc + er * math.sin(math.pi * k / 6)) for k in range(7)]
        for sy in (-1, 1):           # front sight block ears
            g.prism(s, ear, (0, 2), YC + sy * 0.0058 - 0.0011, YC + sy * 0.0058 + 0.0011)
        g.cyl(s, (SIGHT_X, YC, z0 + 0.0085), "z", 0.0011, 0.008, 8)   # sight post
        parts.append(s)
    return parts


def build_lod(spec):
    parts = build_base(spec) + build_moving(spec) + build_pads(spec) + build_wood(spec) + build_barrel(spec)
    g.triangulate(parts)
    if spec["lod"] == 0:
        LOD0[:] = parts
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("bounds: %s .. %s" % (tuple(round(c, 4) for c in BOUNDS["lo"]),
                                   tuple(round(c, 4) for c in BOUNDS["hi"])))
    return parts


def collision():
    """Four convex parts: the fixed body with the plate; the moving jaw with the slider and the screw;
    the inserts with the barrel; the handle. Mass is the item's weight in the mod, 0.8 kg.
    """
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    hx, y0, y1, t = BASE
    ear = hx + 0.006 + EAR_R
    zc, hwc, yc0, yc1, _ = COLUMN[0]
    body = (kx.box_pts(-ear, ear, y0, y1, 0.0, t)
            + kx.box_pts(-JB_X, JB_X, YF + 0.006, YF + 0.036, Z_JB[0], Z_JB[1] + PAD_T)
            + kx.box_pts(-hwc, hwc, yc0, yc1, t, COLUMN[-1][0]))
    moving = (kx.box_pts(-JB_X, JB_X, Y_FRONT, YM, 0.027, Z_JB[1] + PAD_T)
              + kx.box_pts(-BEAM_X, BEAM_X, YM, Y_REAR, Z_BEAM[0], Z_BEAM[1]))
    clamp = kx.box_pts(X_B0, X_B1, YM + PAD_T, YF - PAD_T, Z_W[0], hi[2])
    handle = kx.box_pts(H_X0 - 0.010, H_X1 + 0.010, Y_HANDLE - 0.0075, Y_HANDLE + 0.0075, ZS - 0.0075, ZS + 0.0075)
    comps = [(body, kx.PEN + r"\castiron.rvmat"), (moving, kx.PEN + r"\castiron.rvmat"),
             (clamp, kx.PEN + r"\wood.rvmat"), (handle, kx.PEN + r"\metal.rvmat")]
    memory = {
        # inventory preview camera: front-left and from above (invView = camera position)
        "invView": [(-0.24, -0.40, 0.30)],
        "ce_center": [(0.0, 0.0, 0.052)],
        "ce_radius": [(0.14, 0.0, 0.052)],
        # screw axis - bone ozl_clamp (handle with the hub), from the body to the front
        "ozl_clamp_axis": [(0.0, YM - 0.036, ZS), (0.0, Y_FRONT, ZS)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


SHOTS = [
    ("front", (-0.20, -0.48, 0.28), (0.0, -0.01, 0.050), 40),
    ("jaws", (-0.11, -0.22, 0.20), (-0.01, -0.012, 0.080), 50),
    ("top", (0.03, -0.26, 0.46), (0.0, 0.0, 0.060), 40),
    ("back", (0.32, 0.46, 0.26), (0.0, 0.0, 0.050), 40),
    ("left", (-0.48, -0.12, 0.20), (0.0, 0.0, 0.050), 40),
    ("right", (0.46, -0.24, 0.18), (0.0, 0.0, 0.050), 40),
]
WORK_SHOTS = ("front", "right")          # work pose: the handle is turned further
M.look_shots = (4, 2)


def render_work():
    """Preview of the work pose (look_on_<angle>.png): the handle with the hub is turned by CLAMP_TURN
    about the screw axis. kmodel.states can only shift groups (move), not rotate, so the frames are
    rendered here, in the same scene as render_look; nothing goes to the atlas or p3d (the rotation in
    game is model.cfg, ozl_clamp_turn).
    """
    a = kmodel.ARGV
    if M.bake_part or M.uv_hash or M.stats or not LOD0:
        return
    if not ((M.bake_only and "--look-render" in a) or (not M.bake_only and not M.geo_only and M.look_preview)):
        return
    import bpy
    import kbake
    import krender
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    kbake.use_device(sc)
    with kbake.gpu_slot(sc):
        krender.clear_scene()
        kbake.MATS.clear()
        cam = krender.setup(64)
        origin = bpy.data.objects.new("origin", None)
        sc.collection.objects.link(origin)
        obs = krender.place_look(LOD0, KINDS, origin, panels=M.panel_mats(False))
        # +Y points from the face to the body: a positive angle is clockwise seen from the front
        # (tightening)
        turn = Matrix.Translation((0, 0, ZS)) @ Matrix.Rotation(CLAMP_TURN, 4, "Y") @ Matrix.Translation((0, 0, -ZS))
        for p, ob in zip(LOD0, obs):
            if p.group == SEL_CLAMP:
                ob.matrix_world = turn
        for name, loc, target, lens in [s for s in SHOTS if s[0] in WORK_SHOTS]:
            krender.shoot(cam, os.path.join(M.renders, "look_on_%s.png" % name), loc, target, lens, (1400, 1000))
    print("work pose preview written to", M.renders)


M.run(build_lod, collision, SHOTS, row_step=0.30, row_shot=((0.15, -0.95, 0.30), (0.15, 0, 0.05)))
render_work()
