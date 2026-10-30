"""M86 - plate clamp, variant B: a welded angle plate with two F-clamps. A Protection line module (a
2x2 item, the module_N place of the packers M25, M29, M34). Variant A (build_m86.py) stands in the
mod as the class OZL_Tool_PlateClamp; this one lives only in the test addon: the model
OpenZone_ResearchModels\\m86_plate_clamp_b\\ozr_plate_clamp_b.p3d, class OZR_Test_M86_B (a child of
OZL_Tool_PlateClamp). If B is chosen, it is to be put into the mod in place of A (the generator
lives in the folder of A and takes m86_common.py and the decals from there).

    blender --background --python build_m86b.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py (system Python) before the first build: chalk, bullet marks, cast digits, the
stamp. Renders, atlas and PNGs go to assets/m86_plate_clamp_b/work (not next to A: the model
gallery goes by folders).

Idea: a welding angle plate with two F-clamps - a steel 90 degree angle, clamps with wooden handles
press a piece of plate; about 0.20 x 0.15 x 0.20 m, unpainted scaled steel, clamps in red enamel, a
piece of armour plate in the clamp.

Sample and sizes:
- the angle plate is a machine angle plate 200 x 150 x 150 mm (length x width x height; a catalogue
  "200x150x150 mm plain cast iron angle plate"), but welded: from 16 mm sheet, two 12 mm gussets at
  the ends, welds in the corners. A photo of an angle plate with two ribs and mounting holes (its
  base is ~10 inches by a tape - too large for the 0.2 x 0.2 module place) gives four D 13 mounting
  holes: two in the base at the front, two at the top of the wall;
- the clamps are F-type to DIN 5117 class 100/50 (BESSEY TG10: opening 100 mm, reach 50 mm, rail
  15 x 5 mm, 0.26 kg, force up to 6000 N): cast malleable iron brackets, a 140 mm rail, a screw with
  a D 18 pressure foot, a wooden handle D 26 x 82 mm with a brass-steel ring; the look follows a
  photo of a 1960s F-clamp, only with red enamel brackets and beech lacquered handles;
- in the clamp: a cut piece of 6 mm steel armour plate, ~144 x 108 mm: the face in dark olive paint,
  the edges are an angle-grinder cut (light steel with temper colours), one corner is the original
  rounded edge of the plate; two bullet marks (a lead "pancake" and a dark crater), a 50 x 50
  square for a sample and the number "4" are marked in chalk. The plate stands on the corner weld
  and leans on the wall (it does not hang in the air when the clamps are released).
Bounds 0.20 x 0.183 x 0.172 m (the fixed brackets hang past the wall at the back by 2.3 cm, the
handles of the released clamps stick out past the base at the front by 1 cm; from the module point
not farther than 0.1 m): the height is below the item card (0.20) - the angle plate is 150 mm and
the clamp rails sit over the wall. The in-game weight is 800 g of the OZL_Tool_Base class (the real
set is ~6 kg; module rules untouched), the mass in Geometry is the same.

Details (the "dayz" look: more matte, dirtier): sheet edges rounded, gussets with chamfers, welds as
an uneven bead; the clamp brackets are cast, with a pocket-channel on the sides (as in the photo),
the rail has rounded edges, a mushroom foot, a barrel handle and a ring are smooth solids of
revolution; dented bullet lead on the plate. No vanilla DayZ items on the module: the module itself
is a 0.2 x 0.2 m tool, DayZ small items are on the machines around.
Work look (no lamps or screens - the clamps come alive): at rest the clamps are released - the
moving brackets are pulled back along the rail by 8 mm, the screw is backed off a turn (the foot
11 mm from the plate); while the machine works, the brackets come up to the plate, the handles turn
a turn and the foot presses the plate to the wall; after work they release. Bones per clamp:
ozl_arm0/1 (the moving bracket, a shift along the rail) and ozl_screw0/1 (screw, foot, ring,
handle - a shift and rotation, a child of the bracket), all on the source ozl_work (a pose, like the
M16 feed, animPeriod 1.5 s). The work look has no atlas: states are only for the --look preview
(a pose).

Unlike A (a cast blue press with yellow Kevlar), this is dark steel, welding, red clamps and
armour plate.

Condition (no faction colour): used but intact, worn paint on the edges - the scale has flaked to
grey metal in places, edges rubbed, rust in specks (more at the bottom), oil stains; welds are dark
with temper colours; the red enamel of the brackets is worn to cast iron on the edges; rails are
bare steel; handles - the lacquer is rubbed off, the wood greasy. Markings (digits only): cast
"100" on the fixed brackets (in the channel, enamel worn off the relief), the stamp "17" on the
base end, chalk on the plate.
LODs: near and mid (no holes, welds, bracket pockets, rings and bullet lead; solids of revolution
sparser), no far one.

Blender axes: X is width, Y is depth (the face - the plate and handles - at -Y), Z is up. The
origin is the centre of the base bottom, so the module lands on the module_N proxy point
(autocenter = 0 in Geometry).
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
from m86_common import (axis_frame, lathe, mat_scale, mat_thread, mat_wood, mat_worn, pocket_slab,  # noqa: E402
                        retag, round_poly, slab)

DECALS = os.path.normpath(os.path.join(HERE, "..", "work"))    # decals are shared with A (make_decals.py)

# --- dimensions, m -----------------------------------------------------------------------------
T = 0.016                                     # angle plate sheet
HX, Y0, Y1 = 0.100, -0.075, 0.075             # base
H_WALL = 0.150                                # top of the wall
YW = Y1 - T                                   # wall face
G_T = 0.012                                   # gusset
GUS = [(YW, T + 0.010), (YW, T + 0.095), (YW - 0.095, T), (YW - 0.010, T)]   # profile (y, z), the corner is cut for the weld
HOLE_R = 0.0065
HOLES_BASE = [(-0.060, -0.050), (0.060, -0.050)]
HOLES_WALL = [(-0.070, 0.133), (0.070, 0.133)]
ST = 0.006                                    # armour plate
YS = YW - ST                                  # its face
DZ_SPEC = -0.0016                             # the plate rests on the corner weld
SPEC = [(x, z + DZ_SPEC) for x, z in
        [(-0.066, 0.027), (0.010, 0.026), (0.078, 0.029), (0.0785, 0.090), (0.077, 0.118), (0.073, 0.1265),
         (0.066, 0.1315), (0.057, 0.134), (-0.020, 0.133), (-0.066, 0.131)]]
WELD = (0.0045, 0.0032)                       # weld bead in the corner: radius, axis offset from the faces
# clamp in local axes: a is across, b is up, c is along the rail toward the player; the origin is
# the top of the rail at the fixed bracket
O_Y, O_Z = Y1 + 0.017, H_WALL + 0.017         # jaw of the fixed bracket (c = 0.017) - at the back face of the wall
C_FACE = O_Y - YS                             # c of the plate face (the foot comes here in the work look)
CS = C_FACE + 0.015                           # front face of the moving bracket in the work look
B_SCREW = -0.058
PITCH_B = 0.003                               # clamp screw M10 - thread as stripes
SLIDE, TURN = 0.008, PITCH_B                  # work look: the bracket comes up the rail by 8 mm, the screw turns a turn
BACK = SLIDE + TURN                           # how far the screw with the foot and handle is backed off at rest
CLAMPS = [(-0.032, 4.0), (0.046, -3.0)]       # (x, rotation about Z, degrees)
# fixed bracket (c, b): the top with the rail, down - a cast channel, the jaw at the back face of
# the wall
FIXED = [(-0.006, 0.000), (-0.003, 0.004), (0.013, 0.004), (0.016, 0.001), (0.016, -0.019), (0.012, -0.028),
         (0.012, -0.046), (0.017, -0.050), (0.017, -0.066), (0.015, -0.068), (-0.001, -0.068), (-0.006, -0.060)]
# moving bracket (c from its front face, b): a sleeve on the rail, a cast body with a waist and a
# boss for the screw
MOVING = [(0.0015, 0.0050), (0.0125, 0.0050), (0.0145, 0.0030), (0.0145, -0.0180), (0.0118, -0.0250),
          (0.0115, -0.0430), (0.0150, -0.0515), (0.0140, -0.0560), (0.0000, -0.0560), (-0.0010, -0.0515),
          (0.0025, -0.0430), (0.0022, -0.0250), (-0.0005, -0.0180), (-0.0005, 0.0030)]
HANDLE = [(0.0088, 0.0), (0.0104, 0.0025), (0.0121, 0.012), (0.0130, 0.034), (0.0128, 0.056), (0.0118, 0.070),
          (0.0100, 0.0775), (0.0068, 0.0815), (0.0030, 0.0830)]   # barrel handle (r, c from the ring)
C_FERRULE = CS + 0.014 + 0.008                # handle ring (in the work look)

LOD_SPECS = [
    dict(lod=0, sides=12, rod=10),
    dict(lod=1, sides=10, rod=6),
]

REGIONS = {
    "angle": ("angle", 0.8), "weld": ("weld", 1.2), "red": ("red", 1.2), "rail": ("rail", 1.2),
    "thread": ("thread", 1.6), "pad": ("pad", 1.2), "ferrule": ("ferrule", 1.2), "handle": ("handle", 1.2),
    "spec_face": ("spec_face", 1.1), "spec_edge": ("spec_edge", 1.3),
}


def wdecal(name):
    return os.path.join(DECALS, name)


def clamp_frame(cx, yaw):
    t = math.radians(yaw)
    return g.Frame((cx, O_Y, O_Z), (math.cos(t), math.sin(t), 0), (0, 0, 1), (math.sin(t), -math.cos(t), 0))


def toward_plate(yaw):
    """Where the bracket goes along the rail in the work look (from the player to the plate) - a world
    vector, -n of the clamp frame.
    """
    t = math.radians(yaw)
    return (-math.sin(t), math.cos(t), 0.0)


# decals: (image, normal axis, sign, (u axis, v axis), centre (u, v), size (w, h; the sign is the
# direction, so that the image reads from outside), range along the normal)
CHALK = (wdecal("decal_b_chalk.png"), "y", -1, ("x", "z"), (-0.005, 0.060 + DZ_SPEC), (0.090, 0.060),
         (YS - 0.002, YS + 0.002))
HIT1 = (wdecal("decal_b_hit.png"), "y", -1, ("x", "z"), (0.052, 0.058 + DZ_SPEC), (0.022, 0.022),
        (YS - 0.0035, YS + 0.002))
HIT2 = (wdecal("decal_b_hit.png"), "y", -1, ("x", "z"), (0.020, 0.106 + DZ_SPEC), (-0.018, 0.018),
        (YS - 0.002, YS + 0.002))
STAMP = (wdecal("decal_b_stamp.png"), "y", -1, ("x", "z"), (0.068, 0.008), (0.014, 0.006), (Y0 - 0.002, Y0 + 0.002))


def cast_decal(cx, yaw, side):
    """Cast "100" on the side of the fixed bracket (in the channel): side -1 is the left side (looks to
    -X), +1 the right.
    """
    fr = clamp_frame(cx, yaw)
    p = fr.p(side * 0.006, -0.0335, 0.005)
    w = 0.010 if side > 0 else -0.010
    return (wdecal("decal_b_cast.png"), "x", side, ("y", "z"), (p.y, p.z), (w, 0.026), (p.x - 0.003, p.x + 0.003))


# --- materials ----------------------------------------------------------------------------------
def mat_weld(mat, origin, seed=1.0, floor_z=0.0, dust=0.2, grime=0.5):
    """Weld: a lumpy bead of dark steel, temper colours (bronze, blue) in patches, darker scale along the edges."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    bump = t.noise(vec, 320.0, 4.0, 0.6)
    lump = t.noise(vec, 90.0, 4.0, 0.6)
    col = t.mixc(t.maprange(lump, 0.3, 0.7, 0.0, 1.0), kmats.lin((52, 52, 55)), kmats.lin((96, 96, 98)))
    tint = t.ramp(t.noise(vec, 40.0, 4.0, 0.6), [(0.30, kmats.lin((70, 72, 76))), (0.50, kmats.lin((112, 88, 58))),
                                                (0.70, kmats.lin((58, 66, 96)))])
    col = t.mixc(0.45, col, tint)
    col = t.mixc(t.math("MULTIPLY", t.maprange(bump, 0.4, 0.7, 0.0, 1.0), 0.5), col, kmats.lin((40, 40, 42)))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.6)
    gl = t.math("SUBTRACT", 0.40, t.math("MULTIPLY", dirt, 0.2))
    return kmats.out(t, col, gl, 0.40, t.math("ADD", t.math("MULTIPLY", bump, 0.5), t.math("MULTIPLY", lump, 0.5)))


def mat_ground(mat, origin, seed=1.0, along="x", tint=0.55, floor_z=0.0, dust=0.15, grime=0.35):
    """Angle-grinder cut: light steel with scratches along the cut, temper colours in patches
    (straw -> blue), a darker burr.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    k = {"x": (0.03, 1.0, 1.0), "y": (1.0, 0.03, 1.0), "z": (1.0, 1.0, 0.03)}[along]
    scr = t.noise(t.stretch(vec, *k), 220.0, 4.0, 0.7)
    col = t.mixc(t.maprange(scr, 0.3, 0.7, 0.0, 1.0), kmats.lin((110, 110, 112)), kmats.lin((168, 168, 170)))
    heat = t.ramp(t.noise(vec, 18.0, 4.0, 0.5), [(0.35, kmats.lin((150, 150, 150))), (0.50, kmats.lin((176, 140, 74))),
                                                (0.62, kmats.lin((122, 70, 60))), (0.75, kmats.lin((66, 80, 136)))])
    col = t.mixc(tint, col, heat)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.4)
    gl = t.math("SUBTRACT", 0.55, t.math("MULTIPLY", dirt, 0.3))
    sp = t.math("SUBTRACT", 0.65, t.math("MULTIPLY", dirt, 0.3))
    return kmats.out(t, col, gl, sp, t.math("MULTIPLY", scr, 0.3))


RED = kmats.lin((132, 24, 17))           # red enamel of the brackets (darker than plain: the dayz layers lighten it)
MALLEABLE = kmats.lin((78, 76, 74))      # malleable iron under the enamel
OLIVE_BLACK = kmats.lin((46, 50, 42))    # paint of the armour plate
STEEL_DARK = kmats.lin((92, 92, 94))
BEECH = kmats.lin((128, 86, 52))         # beech under lacquer, darkened by hands and oil

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    # angle plate: hot-rolled scaled sheet, edges rubbed, rust at the bottom; the stamp "17" on the
    # base end; the edges are rounded - edges are searched at 4 mm with a low threshold
    "angle": (mat_scale, dict(seed=2.4, flake=(0.60, 0.68), bright=0.65, oil=0.45, rust_low=0.40, grime=0.60,
                              edge_r=0.004, edge_k=(0.03, 0.15), decal_items=[STAMP])),
    "weld": (mat_weld, dict(seed=3.7, grime=0.7)),
    # clamp brackets: red enamel over malleable iron, edges rubbed, rust in places in the chips;
    # cast "100"
    "red": (mat_worn, dict(color=RED, under=MALLEABLE, seed=4.6, gloss=0.40, spec=0.30, chip=(0.55, 0.61), rub=0.25,
                           chip_rust=0.25, rust=(0.72, 0.80), rust_low=0.25, dust=0.25, grime=0.55, edge_r=0.004,
                           sat=1.3, decal_items=[cast_decal(*CLAMPS[0], -1), cast_decal(*CLAMPS[1], 1)])),
    # rails: bare steel, grinding along the rail; in dayz steel is darker (kmats.build_steel)
    "rail": ("steel", dict(seed=5.2, tone=0.12, along="y", gloss=0.48, spec=0.55, dust=0.25, grime=0.90)),
    # screws: light steel, thread in oil
    "thread": (mat_thread, dict(color=kmats.lin((112, 112, 110)), axis="y", pitch=PITCH_B, seed=6.3, crest=1.4,
                                gloss=0.55, spec=0.55, dust=0.08, grime=0.5)),
    "pad": ("steel", dict(seed=6.9, tone=0.14, along="y", gloss=0.45, spec=0.50, dust=0.15, grime=0.70)),
    "ferrule": ("steel", dict(seed=7.7, tone=0.18, along="x", gloss=0.55, spec=0.60, dust=0.15, grime=0.60)),
    # handles: beech under lacquer, the lacquer rubbed off, greasy; the grain is visible
    "handle": (mat_wood, dict(color=BEECH, seed=8.8, scale=14.0, along="y", gloss=0.30, spec=0.18, oil=0.65,
                              rings=1.2, knots=0.6, dust=0.12, grime=0.40)),
    # armour plate: dark olive paint, chips to steel; chalk and two bullet marks
    "spec_face": (mat_worn, dict(color=OLIVE_BLACK, under=STEEL_DARK, seed=9.5, gloss=0.22, spec=0.18,
                                 chip=(0.61, 0.67), rust=(0.78, 0.86), rust_low=0.0, dust=0.25, grime=0.45,
                                 decal_items=[CHALK, HIT1, HIT2])),
    "spec_edge": (mat_ground, dict(seed=1.3, along="x")),
})

OBJ, NAME = "m86_plate_clamp_b", "ozr_plate_clamp_b"
# work look: per clamp - the bracket along the rail and the screw with the foot and handle (shift
# and rotation)
SEL_ARM = ["ozl_arm%d" % k for k in range(len(CLAMPS))]
SEL_SCR = ["ozl_screw%d" % k for k in range(len(CLAMPS))]
ANIMS = []
for k in range(len(CLAMPS)):
    ANIMS += [
        ("ozl_arm%d_slide" % k, dict(type="translation", source="ozl_work", selection=SEL_ARM[k],
                                     axis="ozl_arm%d_axis" % k, memory=1, minValue=0.0, maxValue=1.0, offset0=0.0,
                                     offset1=SLIDE)),
        ("ozl_screw%d_in" % k, dict(type="translation", source="ozl_work", selection=SEL_SCR[k],
                                    axis="ozl_arm%d_axis" % k, memory=1, minValue=0.0, maxValue=1.0, offset0=0.0,
                                    offset1=TURN)),
        # right-hand thread: tightened clockwise seen from the handle (check the direction on the
        # stand)
        ("ozl_screw%d_turn" % k, dict(type="rotation", source="ozl_work", selection=SEL_SCR[k],
                                      axis="ozl_screw%d_axis" % k, memory=1, minValue=0.0, maxValue=1.0, angle0=0.0,
                                      angle1=-2 * math.pi * TURN / PITCH_B)),
    ]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=tuple(SEL_ARM + SEL_SCR),
                 bones=tuple(b for k in range(len(CLAMPS)) for b in ((SEL_ARM[k], ""), (SEL_SCR[k], SEL_ARM[k]))),
                 animations=tuple(ANIMS), sources={"ozl_work": dict(animPeriod=1.5)})
# renders, atlas and PNGs - in the variant's own folder (the generator is in folder A)
M.work = os.path.join(M.repo, "assets", OBJ, "work")
M.game_tex = os.path.join(M.work, "game_textures")
M.renders = os.path.join(M.work, "renders")
if M.look_preview:
    # work look preview (--look): the clamps are tightened; the work look has no atlas - states only
    # here
    MOVE = {}
    for k, (cx, yaw) in enumerate(CLAMPS):
        d = toward_plate(yaw)
        MOVE[SEL_ARM[k]] = tuple(c * SLIDE for c in d)
        MOVE[SEL_SCR[k]] = tuple(c * BACK for c in d)
    M.states = {"on": dict(remap={}, move=MOVE)}
P = M.part
BOUNDS = {}


# --- angle plate --------------------------------------------------------------------------------
def build_angle(spec):
    lod = spec["lod"]
    base = P("angle_base", "angle")
    wall = P("angle_wall", "angle")
    if lod == 0:
        # 16 mm sheet: edges rounded, sheet corners cut; the wall bottom is in the base
        slab(base, round_poly([(-HX, Y0), (HX, Y0), (HX, Y1), (-HX, Y1)], 0.002, 1), (0, 1), 0.0, T,
             r=0.0008, r1=0.0014, seg=2)
        slab(wall, round_poly([(-HX, T - 0.0005), (HX, T - 0.0005), (HX, H_WALL), (-HX, H_WALL)], 0.002, 1), (0, 2),
             YW, Y1, r=0.0014, seg=2)
        cuts = []
        for x, y in HOLES_BASE:
            c = P("cut", "angle")
            g.cyl(c, (x, y, T / 2), "z", HOLE_R, T + 0.004, 12)
            cuts.append(c)
        base = M.boolean("angle_base_h", base, cuts)
        cuts = []
        for x, z in HOLES_WALL:
            c = P("cut", "angle")
            g.cyl(c, (x, (YW + Y1) / 2, z), "y", HOLE_R, T + 0.004, 12)
            cuts.append(c)
        wall = M.boolean("angle_wall_h", wall, cuts)
    else:
        slab(base, [(-HX, Y0), (HX, Y0), (HX, Y1), (-HX, Y1)], (0, 1), 0.0, T, r=0.0, r1=0.0012, seg=1)
        slab(wall, [(-HX, T - 0.0005), (HX, T - 0.0005), (HX, H_WALL), (-HX, H_WALL)], (0, 2), YW, Y1, r=0.0012, seg=1)
    gus = P("gussets", "angle")
    prof = round_poly(GUS, [0.0, 0.003, 0.003, 0.0], 1) if lod == 0 else GUS
    for s in (-1, 1):
        x0, x1 = sorted((s * (HX - G_T), s * HX))
        if lod == 0:
            slab(gus, prof, (1, 2), x0, x1, r=0.0008, seg=1)
        else:
            g.prism(gus, prof, (1, 2), x0, x1)
    return [base, wall, gus]


def bead(part, a, b, r, sides, seed, n=4, wobble=0.0006, swell=0.10):
    """Weld bead: a rod through points with scatter and varying thickness - the weld is laid by hand."""
    rnd = random.Random(seed)
    pts, radii = [], []
    for i in range(n):
        t = i / (n - 1)
        p = [a[k] + (b[k] - a[k]) * t for k in range(3)]
        if 0 < i < n - 1:
            p = [c + rnd.uniform(-wobble, wobble) for c in p]
        pts.append(tuple(p))
        k = 1.0 + rnd.uniform(-swell, swell) if 0 < i < n - 1 else 0.85
        radii.append((r * k, r * k * 0.9))
    g.tube_var(part, pts, radii, sides)


def build_welds(spec):
    w = P("welds", "weld")
    r, o = WELD
    if spec["lod"] > 0:              # mid LOD - only the long weld in the corner, no scatter
        bead(w, (-HX + G_T + 0.001, YW - o, T + o), (HX - G_T - 0.001, YW - o, T + o), r, 5, 1, n=3, wobble=0.0,
             swell=0.0)
        return [w]
    bead(w, (-HX + G_T + 0.001, YW - o, T + o), (HX - G_T - 0.001, YW - o, T + o), r, 6, 1, n=10)
    for s in (-1, 1):
        x = s * (HX - G_T - o)
        bead(w, (x, YW - o, T + 0.012), (x, YW - o, T + 0.092), 0.0038, 5, 2 + s, n=4)
        bead(w, (x, YW - 0.012, T + o), (x, YW - 0.092, T + o), 0.0038, 5, 5 + s, n=4)
    return [w]


# --- armour plate -------------------------------------------------------------------------------
def build_specimen(spec):
    sp = P("specimen", "spec_face")
    if spec["lod"] == 0:
        faces = slab(sp, SPEC, (0, 2), YS, YW - 0.0003, r=0.0006, seg=1)
        # bullet lead flattened on the armour: a low "pancake" over the mark (the colour is the mark
        # decal)
        hx, hz = HIT1[4][0], HIT1[4][1]
        lathe(sp, axis_frame((hx, YS, hz), (0, -1, 0)), [(0.0055, 0.0), (0.0042, 0.0009), (0.0018, 0.0014)], 8,
              cap_hi=True)
    else:
        faces = g.prism(sp, SPEC, (0, 2), YS, YW - 0.0003)
    sp.region_index("spec_edge", *REGIONS["spec_edge"])
    retag(sp, faces, lambda n: abs(n.y) < 0.8, "spec_edge")      # the cut and the knocked-off chamfer are bare steel
    return [sp]


# --- F-clamps -----------------------------------------------------------------------------------
def build_clamp(spec, cx, yaw, k):
    lod, n = spec["lod"], spec["sides"]
    fr = clamp_frame(cx, yaw)
    cn = tuple(fr.n)
    cs, cf = CS + SLIDE, C_FACE + BACK          # at rest: the bracket is pulled back along the rail, the screw is backed off
    rail = P("rail%d" % k, "rail")
    fixed = P("fixed%d" % k, "red")
    arm = P("arm%d" % k, "red", group=SEL_ARM[k])
    if lod == 0:
        slab(rail, round_poly([(-0.002, -0.015), (0.140, -0.015), (0.140, 0.0), (-0.002, 0.0)], 0.0015, 1), (2, 1),
             -0.0025, 0.0025, r=0.0005, seg=1, frame=fr)
        # cast brackets with a channel on both sides, as in DIN 5117 (photo)
        pocket_slab(fixed, FIXED, (2, 1), -0.006, 0.006, rim=0.002, depth=0.0015, frame=fr)
        pocket_slab(arm, [(cs + c, b) for c, b in MOVING], (2, 1), -0.006, 0.006, rim=0.0018, depth=0.0012, frame=fr)
    else:
        g.box(rail, -0.0025, 0.0025, -0.015, 0.0, -0.002, 0.140, frame=fr)
        slab(fixed, FIXED, (2, 1), -0.006, 0.006, r=0.001, seg=1, frame=fr)
        g.prism(arm, [(cs + c, b) for c, b in MOVING], (2, 1), -0.0055, 0.0055, frame=fr)
    # screw boss on the moving bracket
    lathe(arm, axis_frame(fr.p(0, B_SCREW, cs - 0.003), cn),
          [(0.0068, 0.0), (0.0085, 0.0015), (0.0085, 0.0185), (0.0068, 0.020)] if lod == 0 else
          [(0.0085, 0.0), (0.0085, 0.020)], max(8, n), cap_lo=True, cap_hi=True)
    th = P("screw%d" % k, "thread", group=SEL_SCR[k])
    lathe(th, axis_frame(fr.p(0, B_SCREW, cf + 0.003), cn), [(0.005, 0.0), (0.005, C_FERRULE - C_FACE)],
          10 if lod == 0 else 6)
    pad = P("pad%d" % k, "pad", group=SEL_SCR[k])
    prof = [(0.009, 0.0), (0.009, 0.0025), (0.0075, 0.0035), (0.0058, 0.0042), (0.0048, 0.0060)]
    if lod > 0:
        prof = [(0.009, 0.0), (0.009, 0.0030), (0.0048, 0.0060)]
    lathe(pad, axis_frame(fr.p(0, B_SCREW, cf), cn), prof, n, cap_lo=True, cap_hi=True)
    hd = P("handle%d" % k, "handle", group=SEL_SCR[k])
    c0 = C_FERRULE + BACK + 0.007
    prof = HANDLE if lod == 0 else [HANDLE[0], HANDLE[2], HANDLE[4], HANDLE[6], HANDLE[-1]]
    lathe(hd, axis_frame(fr.p(0, B_SCREW, c0), cn), prof, n, cap_lo=True, cap_hi=True)
    parts = [rail, fixed, arm, th, pad, hd]
    fe = P("ferrule%d" % k, "ferrule", group=SEL_SCR[k])
    lathe(fe, axis_frame(fr.p(0, B_SCREW, C_FERRULE + BACK), cn),
          [(0.0081, 0.0), (0.0093, 0.0008), (0.0093, 0.0072), (0.0086, 0.008)] if lod == 0 else
          [(0.0092, 0.0), (0.0092, 0.008)], n, cap_lo=True, cap_hi=True)
    parts.append(fe)
    return parts


def build_lod(spec):
    parts = build_angle(spec) + build_welds(spec) + build_specimen(spec)
    for k, (cx, yaw) in enumerate(CLAMPS):
        parts += build_clamp(spec, cx, yaw, k)
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("bounds: %s .. %s" % (tuple(round(c, 4) for c in BOUNDS["lo"]),
                                   tuple(round(c, 4) for c in BOUNDS["hi"])))
    return parts


def ring_pts(fr, b, c, r, n=8):
    return [tuple(fr.p(r * math.cos(2 * math.pi * i / n), b + r * math.sin(2 * math.pi * i / n), c)) for i in range(n)]


def collision():
    """Six convex parts: the angle plate with gussets (a wedge); the armour plate; for each clamp - the
    rail with the brackets and the screw with the handle (from the foot on the plate to the end of the
    handle at rest). Mass is the item's weight in the mod, 0.8 kg.
    """
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    angle = kx.box_pts(-HX, HX, Y0, Y1, 0.0, T) + kx.box_pts(-HX, HX, YW, Y1, T, H_WALL)
    xs = [x for x, _ in SPEC]
    zs = [z for _, z in SPEC]
    comps = [(angle, kx.PEN + r"\metalplate.rvmat"),
             (kx.box_pts(min(xs), max(xs), YS, YW, min(zs), max(zs)), kx.PEN + r"\armour.rvmat")]
    for cx, yaw in CLAMPS:
        fr = clamp_frame(cx, yaw)
        body = [tuple(fr.p(a, b, c)) for a in (-0.0065, 0.0065) for b in (0.0045, -0.068) for c in (-0.006, 0.140)]
        c1 = C_FERRULE + BACK + 0.007 + HANDLE[-1][1]
        grip = ring_pts(fr, B_SCREW, C_FACE, 0.013) + ring_pts(fr, B_SCREW, c1, 0.013)
        comps += [(body, kx.PEN + r"\iron.rvmat"), (grip, kx.PEN + r"\wood.rvmat")]
    memory = {
        # inventory preview camera: front-left and from above (invView = camera position)
        "invView": [(-0.26, -0.42, 0.30)],
        "ce_center": [(0.0, 0.0, 0.085)],
        "ce_radius": [(0.14, 0.0, 0.085)],
    }
    # work look: the bracket travel along the rail is a metre toward the plate (the offset is in
    # metres), the screw rotation axis goes along the screw
    for k, (cx, yaw) in enumerate(CLAMPS):
        fr = clamp_frame(cx, yaw)
        p = fr.p(0.0, B_SCREW, CS + SLIDE)
        d = toward_plate(yaw)
        memory["ozl_arm%d_axis" % k] = [tuple(p), tuple(p[i] + d[i] for i in range(3))]
        memory["ozl_screw%d_axis" % k] = [tuple(fr.p(0.0, B_SCREW, C_FACE + BACK + 0.1)),
                                          tuple(fr.p(0.0, B_SCREW, C_FACE + BACK))]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


# the first three are the --look preview (overall view, the clamps close up, from the right); the
# work look uses the first two
SHOTS = [
    ("front", (-0.20, -0.50, 0.30), (0.0, 0.0, 0.080), 40),
    ("clamps", (-0.11, -0.24, 0.20), (0.008, 0.030, 0.095), 48),
    ("right", (0.46, -0.26, 0.20), (0.0, 0.0, 0.080), 40),
    ("back", (0.32, 0.46, 0.28), (0.0, 0.0, 0.080), 40),
    ("left", (-0.50, -0.12, 0.20), (0.0, 0.0, 0.080), 40),
    ("top", (0.03, -0.26, 0.48), (0.0, 0.0, 0.070), 40),
]

M.look_shots = (3, 2)
M.run(build_lod, collision, SHOTS, row_step=0.30, row_shot=((0.15, -0.95, 0.32), (0.15, 0, 0.07)))
