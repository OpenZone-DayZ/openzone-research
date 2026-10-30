"""M86 - plate clamp (OZL_Tool_PlateClamp), variant A: a Protection line module, a portable 2x2 item.
It sits in an OZL_Tool1..3 slot of the packer (M25, M29, M34) and shows on its shelf through the
module_N proxy. Two variants were built: variant A goes into the mod as the class
OZL_Tool_PlateClamp, variant B (build_m86b.py) as the test class OZR_Test_M86_B in the test addon.

    blender --background --python build_m86.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py (system Python) before the first build: the cast digits, the marker; the decals
of variant B are made there too.

Idea: a hand screw press clamp - a cast C-frame, a screw with a handle, a pressure foot and a steel
base plate, about 0.18 x 0.22 x 0.15 m, grey or blue frame enamel, a blued screw, the handle
sideways. The module pad is about 0.2 x 0.2 m, up to about 0.25 m high, flat bottom. Purpose: clamp
armour plate or Kevlar flat so that a sample can be cut.

Sample and sizes. No datasheet of a small bench screw press with a cast C-frame was found
(auction lots, a Ukrainian marketplace, catalogues of Hoffmann/Bergschmid/Schmidt - bench presses
of this size there are lever and rack types), therefore:
- the layout follows a photo of a "screw press" lot (a steel base plate, two posts, a curved
  cross-head, a blued screw with a T-handle, a round foot) and the classic copy press whose posts
  and cross-head are one C-shaped iron casting on a plate;
- the scale follows bench presses of the same class: the lever HK 500 - base 175 x 115 mm, reach
  73, travel 40, 11 kg; the rack Mast M-AP-1000 - table 268 x 128 mm, 16 kg; and the module place
  (0.2 x 0.2);
- the screw, foot and handle follow the 100 mm clamp class (Irwin Record T120/4: opening 100,
  reach 60 mm; Faithfull 100 mm - reach 60): screw Tr20 x 4, foot diameter 48, handle D 10 x 138 mm
  with upset ends.
Model: plate 180 x 135 x 12 mm; the C-frame - I-section posts 20 x 30 mm on feet 38 x 64 mm, each
foot on two M8 bolts with washers; the span between the posts 116 mm; an arched cross-head
160 x 36 mm with a nut boss D 36; on the cross-head front a blank aluminium nameplate on two
rivets. The clearance under the cross-head is 76-86 mm. Bounds 0.194 x 0.135 x 0.170 m (the handle
is shifted sideways and sticks out past the plate by 1.4 cm; the height is with the screw backed
off two turns) - the height as on the item card (0.15), the depth less than its 0.22: deeper than
0.135 the plate is not needed, and the module places on the M34 table are 0.25 m apart.
In the clamp: a Kevlar stack (aramid fabric, 12 layers, 12 mm) 96 x 104 mm; on top a steel
pressure plate 70 x 60 x 6 (so that the foot presses evenly); at the front a round hole D 30 from
which the sample has already been cut (it lies on the plate in the left front corner); next to it
the next circle is outlined with marker and the layer count "12" is written. The real press mass
is ~5-6 kg; the in-game weight is 800 g of the OZL_Tool_Base class (module rules untouched), the
mass in Geometry is the same.

Details (the "dayz" look: more matte, dirtier): shapes without angularity - a casting with rounded
edges of the cross-head and feet, the posts widen toward the feet by a cast transition, ribs at the
feet outside; the Tr20 x 4 thread is geometry (a helical grid, crests rubbed to metal); the foot,
head and handle with upset ends are smooth solids of revolution with chamfers; the foot bolts are
chamfered heads on washers; Kevlar in uneven layers with soft edges; the cut sample lies beside.
No vanilla DayZ items on the module: the module itself is a 0.2 x 0.2 m tool, DayZ small items are
on the machines around.
Work look (a press has no lamps or screens - the screw comes alive): at rest the screw is backed
off two turns (the foot 8 mm above the pressure plate); while the machine works, the screw with its
head and handle turns two turns (Tr20 x 4: 8 mm) and the foot comes down onto the plate - clamped;
after work it releases. Bones: ozl_pad (the foot, a shift down) and ozl_work (screw, head, handle -
rotation, a child of ozl_pad), both on the source ozl_work (a pose, like the M16 feed, animPeriod
1.5 s). The work look has no atlas (nothing to glow): states are only for the --look preview (a
pose), not for baking or the p3d.

Condition (no faction colour): used but intact, worn paint on the edges - the blue enamel of the
C-frame is worn to cast iron on the edges, on the feet and around the boss; the plate is scaled
steel, edges rubbed, rust in specks; the screw is blued with oil on the thread; the handle is
rubbed to metal by hands; the foot and the pressure plate are scratched steel. Markings (digits
only and a blank nameplate): cast "0,5" on the side of the right post (enamel worn off the relief),
the marker "12" and a circle on Kevlar.
LODs: near and mid (no bolts, nameplate, hole in the Kevlar, sample, geometric thread and cast
transitions; solids of revolution sparser), no far one.

Blender axes: X is width, Y is depth (the face - Kevlar with the hole - at -Y), Z is up. The origin
is the centre of the plate bottom, so the module lands on the module_N proxy point (autocenter = 0
in Geometry).
"""
import math
import os
import sys

from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
from m86_common import (axis_frame, ccw, hex_head, hexagon, helix_thread, jitter_poly, lathe, loft,  # noqa: E402
                        mat_helix, mat_scale, mat_thread, mat_worn, offset_poly, round_poly, slab, washer)

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m -----------------------------------------------------------------------------
BASE = (0.090, -0.070, 0.065, 0.012)          # plate: half-width, y0, y1, thickness
XL = 0.068                                    # post axes
LW, LD, FT, WH = 0.010, 0.015, 0.005, 0.005   # post: half-width, half-depth, flange, half-web
FOOT = (-0.016, 0.022, 0.034, 0.008)          # foot: from the post axis inward / outward, half-depth, thickness
Z_FOOT = BASE[3] + FOOT[3]
Z_LEG = 0.090                                 # top of the post (under the cross-head)
CB_X, CD = 0.080, 0.018                       # cross-head: half-length, half-depth (flush with the boss)
BOSS_R, Z_BOSS = 0.018, (0.092, 0.130)
PITCH, DEPTH, SCREW_R = 0.004, 0.0020, 0.010  # Tr20 x 4: outer radius, thread depth
TRAVEL = 2 * PITCH                            # work look: the screw goes down two turns
Z_PACK = (BASE[3], 0.024)                     # Kevlar: 12 layers
PACK_X, PACK_Y = 0.048, (-0.068, 0.036)
HOLE = (-0.028, -0.047, 0.015)                # cut-out sample: centre x, y, radius
DISC = (-0.071, -0.051)                       # the sample itself - on the plate in the left front corner
COVER = (0.035, -0.030, 0.030, 0.006)         # pressure plate: half-width, y0, y1, thickness
Z_COVER = Z_PACK[1] + COVER[3]                # top of the pressure plate - the foot comes down here
Z_PAD = Z_COVER + TRAVEL                      # bottom of the foot at rest (the screw backed off)
PAD_H = 0.0178
Z_HEAD = (0.138 + TRAVEL, 0.162 + TRAVEL)
Z_BAR, BAR_R, BAR_X = 0.150 + TRAVEL, 0.005, (-0.040, 0.098)
BOLTS = [(s * (XL + 0.004), y) for s in (-1, 1) for y in (-0.025, 0.025)]
PLATE = (-0.058, -0.026, 0.0975, 0.1085)      # blank nameplate on the cross-head: x0, x1, z0, z1


def top_z(x):
    return 0.106 + 0.014 * (1.0 - (x / CB_X) ** 2)


def bot_z(x):
    """Cross-head underside: flat over the posts, toward the middle a smooth swell under the boss (casting)."""
    if abs(x) >= 0.058:
        return 0.088
    return 0.088 + 0.010 * (0.5 + 0.5 * math.cos(math.pi * x / 0.058))


LOD_SPECS = [
    dict(lod=0, sides=16, rod=12, knob=12),
    dict(lod=1, sides=12, rod=8, knob=8),
]

REGIONS = {
    "frame": ("frame", 1.0), "base": ("base", 0.8), "bolt": ("bolt", 1.2), "washer": ("washer", 1.0),
    "alu": ("alu", 1.3), "screw": ("screw", 1.6), "thread": ("thread", 1.6), "head": ("head", 1.3),
    "bar": ("bar", 1.3), "pad": ("pad", 1.2), "cover": ("cover", 1.0), "kevlar": ("kevlar", 1.4),
}


def wdecal(name):
    return os.path.join(WORK, name)


# decals: (image, normal axis, sign, (u axis, v axis), centre (u, v), size (w, h; the sign is the
# direction, so that the image reads from outside), range along the normal)
CAST = (wdecal("decal_a_cast.png"), "x", 1, ("y", "z"), (0.0, 0.054), (0.022, 0.011),
        (XL + LW - 0.002, XL + LW + 0.002))
MARKER = (wdecal("decal_a_marker.png"), "z", 1, ("x", "y"), (0.020, HOLE[1]), (0.060, 0.034),
          (Z_PACK[1] - 0.002, Z_PACK[1] + 0.002))


# --- materials ----------------------------------------------------------------------------------
def mat_kevlar(mat, origin, color, seed=1.0, cell=0.003, layer=0.0015, gloss=0.22, spec=0.12, floor_z=0.0,
               dust=0.2, grime=0.4, decal_items=()):
    """Aramid fabric stack: on the flat faces a plain weave (cell `cell`: neighbouring cells have threads
    along X and along Y, each thread rounded - lighter in the middle), on the cuts the layer stripes
    (pitch layer) and a light fluffy fuzz; dirty patches from hands and the press.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()

    def bands(axis, period):
        w = t.node("ShaderNodeTexWave", Scale=2 * math.pi / (20.0 * period), Distortion=0.0, Detail=0.0)
        w.wave_type = "BANDS"
        w.bands_direction = axis
        w.wave_profile = "SIN"
        t.link(vec, w.inputs["Vector"])
        return w.outputs["Fac"]
    chk = t.node("ShaderNodeTexChecker", Scale=1.0 / cell)
    t.link(vec, chk.inputs["Vector"])
    along_x, along_y = bands("Y", cell), bands("X", cell)
    weave = t.mixc(chk.outputs["Fac"], (0, 0, 0, 1), (1, 1, 1, 1))
    weave = t.math("ADD", t.math("MULTIPLY", t.bw(weave), along_y),
                   t.math("MULTIPLY", t.math("SUBTRACT", 1.0, t.bw(weave)), along_x))
    lay = t.maprange(bands("Z", layer), 0.0, 0.35, 0.0, 1.0)
    flat = t.maprange(t.math("ABSOLUTE", nsep.outputs["Z"]), 0.6, 0.8, 0.0, 1.0)
    shade = t.mixf(flat, lay, weave)
    dark = tuple(c * 0.55 for c in color[:3]) + (1,)
    light = tuple(min(1.0, c * 1.18) for c in color[:3]) + (1,)
    tone = t.maprange(t.noise(vec, 6.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0)
    col = t.mixc(tone, tuple(c * 0.92 for c in color[:3]) + (1,), color)
    col = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", 1.0, shade), 0.55), col, dark)
    fuzz = t.math("MULTIPLY", t.step(t.noise(vec, 140.0, 4.0, 0.7), 0.55, 0.70), t.math("SUBTRACT", 1.0, flat))
    edge = t.maprange(t.edge_wear(0.002), 0.06, 0.25, 0.0, 1.0)
    col = t.mixc(t.math("MAXIMUM", t.math("MULTIPLY", fuzz, 0.6), t.math("MULTIPLY", edge, 0.5)), col, light)
    smear = t.maprange(t.noise(vec, 9.0, 6.0, 0.6), 0.58, 0.75, 0.0, 0.55)
    col = t.mixc(smear, col, tuple(c * 0.60 for c in color[:3]) + (1,))
    col = kmats.decals(t, col, sep, nsep, decal_items)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.5)
    gl = t.math("SUBTRACT", t.mixf(shade, gloss * 0.6, gloss), t.math("MULTIPLY", dirt, gloss * 0.5))
    sp = t.math("SUBTRACT", t.mixf(shade, spec * 0.5, spec), t.math("MULTIPLY", dirt, spec * 0.4))
    h = t.math("ADD", t.math("MULTIPLY", shade, 0.6), t.math("MULTIPLY", fuzz, 0.2))
    return kmats.out(t, col, gl, sp, h)


BLUE = kmats.lin((50, 76, 122))          # blue enamel of machine castings, slightly muted (not the light-blue faction colour)
IRON = kmats.lin((96, 94, 90))           # cast iron under the enamel
BLUED = kmats.lin((34, 36, 42))
STEEL_BRIGHT = kmats.lin((150, 150, 154))
KEVLAR = kmats.lin((204, 166, 66))       # aramid fabric, natural (golden yellow)
ALU = dict(color=kmats.lin((150, 152, 150)), under=kmats.lin((104, 106, 105)), gloss=0.42, spec=0.42,
           chip=(0.66, 0.72), rust=(0.98, 0.99), rust_low=0.0, floor_z=0.0, dust=0.25, grime=0.45)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    # C-frame: blue enamel over cast iron, worn on the edges, on the feet and around the boss; cast
    # "0,5"; the edges are rounded - chip edges are searched at 5 mm with a low threshold (the
    # normal changes smoothly on a rounding)
    "frame": (mat_worn, dict(color=BLUE, under=IRON, seed=2.6, gloss=0.40, spec=0.30, chip=(0.54, 0.60), rub=0.45,
                             chip_rust=0.25, rust=(0.70, 0.78), rust_low=0.30, dust=0.35, grime=0.75, edge_r=0.005,
                             edge_k=(0.02, 0.10), decal_items=[CAST])),
    # plate: hot-rolled scaled steel, edges rubbed, rust in specks, oil stains
    "base": (mat_scale, dict(seed=3.3, flake=(0.60, 0.68), bright=0.60, oil=0.45, rust_low=0.35, grime=0.60,
                             edge_r=0.004, edge_k=(0.03, 0.15))),
    # foot bolts: blackened, head faces rubbed by a wrench, a reddish film at the washer
    "bolt": ("paint", dict(color=kmats.lin((30, 30, 33)), under=STEEL_BRIGHT, seed=4.1, gloss=0.40, spec=0.40,
                           chip=(0.66, 0.72), rust=(0.72, 0.82), rust_low=0.5, dust=0.2, grime=0.7)),
    # washers: plain steel, darkened, with a rusty film at the edge
    "washer": ("steel", dict(seed=4.7, tone=0.24, along="x", gloss=0.42, spec=0.45, dust=0.3, grime=0.8)),
    "alu": ("paint", dict(ALU, seed=8.2)),
    # screw: geometric thread - bluing, crests rubbed to steel by the nut, oil in the valleys
    "screw": (mat_helix, dict(color=kmats.lin((40, 42, 48)), bare=kmats.lin((138, 138, 140)),
                              r_root=SCREW_R - DEPTH, r_crest=SCREW_R, seed=5.5, gloss=0.55, spec=0.55)),
    # screw above the boss (a short piece by the head) - the thread as stripes
    "thread": (mat_thread, dict(color=kmats.lin((44, 46, 52)), axis="z", pitch=PITCH, seed=5.5, crest=2.2,
                                gloss=0.55, spec=0.55, dust=0.08, grime=0.45)),
    # screw head: bluing, rubbed on the edges
    "head": ("paint", dict(color=BLUED, under=STEEL_BRIGHT, seed=6.1, gloss=0.58, spec=0.55, chip=(0.74, 0.80),
                           rust=(0.93, 0.98), rust_low=0.0, dust=0.12, grime=0.2)),
    # handle: bluing rubbed by palms almost to metal
    "bar": ("paint", dict(color=BLUED, under=STEEL_BRIGHT, seed=7.3, gloss=0.62, spec=0.60, chip=(0.52, 0.60),
                          rust=(0.93, 0.98), rust_low=0.0, dust=0.06, grime=0.12)),
    # foot: turned steel, darkened by oil
    "pad": ("steel", dict(seed=6.6, tone=0.12, along="z", gloss=0.48, spec=0.55, dust=0.15, grime=0.90)),
    # pressure plate: ground steel with scratches, dust on top
    "cover": ("steel", dict(seed=9.1, tone=0.16, along="x", gloss=0.50, spec=0.60, dust=0.35, grime=0.90)),
    # Kevlar is grubby from hands and the oil from the screw
    "kevlar": (mat_kevlar, dict(color=KEVLAR, seed=1.9, dust=0.3, grime=0.55, decal_items=[MARKER])),
})

OBJ, NAME = "m86_plate_clamp", "ozr_plate_clamp"
# work look: the screw with the head and handle turns two turns and goes down with the foot (a pose)
SEL_PAD, SEL_SCREW = "ozl_pad", "ozl_work"
CLAMP_DOWN = ("ozl_clamp_down", dict(type="translation", source="ozl_work", selection=SEL_PAD, axis="ozl_pad_axis",
                                     memory=1, minValue=0.0, maxValue=1.0, offset0=0.0, offset1=TRAVEL))
# right-hand thread: it is tightened clockwise seen from above. The axis ozl_work_axis goes from the
# bottom up, toward whoever looks from above. The engine rotates a bone right-handed in DayZ axes
# (kexport.conv, determinant -1), which in Blender axes is a left-handed turn about the axis from
# the first point to the second: the axis looks at the person - a plus angle is clockwise for him
# (as for M08, M12, M14, M33 - their needles are right in game). The sign matters: with the opposite
# sign the screw would go down while turning counter-clockwise, like unscrewing. Checked by
# check_turn below.
CLAMP_TURN = ("ozl_clamp_turn", dict(type="rotation", source="ozl_work", selection=SEL_SCREW, axis="ozl_work_axis",
                                     memory=1, minValue=0.0, maxValue=1.0, angle0=0.0,
                                     angle1=2 * math.pi * TRAVEL / PITCH))
SCREW_AXIS = [(0.0, 0.0, Z_PAD), (0.0, 0.0, Z_HEAD[1])]          # memory points of ozl_work_axis: bottom to top


def check_turn():
    """Numeric check, as check_axes of the Storage boxes: at a small phase the engine rotation (about the
    memory axis SCREW_AXIS, in Blender axes a right-handed turn about the reversed axis) moves the
    handle clockwise seen from above: a point on +X goes toward -Y. If it does not hold, the build fails.
    """
    a, b = (Vector(q) for q in SCREW_AXIS)
    ang = CLAMP_TURN[1]["angle1"] * 0.01
    q = Matrix.Rotation(ang, 3, a - b) @ Vector((0.05, 0.0, 0.0))
    assert q.y < -0.001, "the screw tightens counter-clockwise seen from above"
    print("turns ok: the screw turns clockwise seen from above (tightening a right-hand thread), %.1f turns per stroke" %
          (CLAMP_TURN[1]["angle1"] / (2 * math.pi)))


check_turn()
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL_PAD, SEL_SCREW), bones=((SEL_PAD, ""), (SEL_SCREW, SEL_PAD)),
                 animations=(CLAMP_DOWN, CLAMP_TURN), sources={"ozl_work": dict(animPeriod=1.5)})
if M.look_preview:
    # work look preview (--look): the foot on the plate; the work look has no atlas - states only
    # here
    M.states = {"on": dict(remap={}, move={SEL_PAD: (0.0, 0.0, -TRAVEL), SEL_SCREW: (0.0, 0.0, -TRAVEL)})}
P = M.part
BOUNDS = {}


# --- plate and C-frame --------------------------------------------------------------------------
def build_base(spec):
    hx, y0, y1, t = BASE
    base = P("base", "base")
    rect = [(-hx, y0), (hx, y0), (hx, y1), (-hx, y1)]
    if spec["lod"] == 0:
        slab(base, round_poly(rect, 0.003, 1), (0, 1), 0.0, t, r=0.0008, r1=0.0016, seg=2)
    else:
        g.box(base, -hx, hx, y0, y1, 0.0, t)
    return [base]


def leg_poly(lod):
    """I-section of the post in plan (x from the post axis, y): the flanges are the inner and outer faces,
    the web across; a cast recess 10 mm deep is visible at the front and back. The near LOD has a cast
    chamfer in the inner corners of the recess and a small chamfer on the flange edges.
    """
    pts = [(-LW, -LD), (-LW + FT, -LD), (-LW + FT, -WH), (LW - FT, -WH), (LW - FT, -LD), (LW, -LD),
           (LW, LD), (LW - FT, LD), (LW - FT, WH), (-LW + FT, WH), (-LW + FT, LD), (-LW, LD)]
    if lod > 0:
        return pts
    inner = {2, 3, 8, 9}
    return round_poly(pts, [0.0025 if i in inner else 0.0008 for i in range(len(pts))], 1)


def build_frame(spec):
    """The C-frame is one casting, but built in parts: a post with a foot (two), the cross-head, the boss -
    each has its own atlas pieces (the kuv unwrap is a projection by sides: faces of one part looking
    the same way would otherwise land on the same texels).
    """
    lod = spec["lod"]
    fin, fout, fd, ft = FOOT
    parts = []
    for s in (-1, 1):
        leg = P("leg_r" if s > 0 else "leg_l", "frame")
        xc = s * XL
        x0, x1 = sorted((xc + s * fin, xc + s * fout))
        if lod == 0:
            # foot: corners cut, the top edge chamfered (the bottom lies on the plate - not visible)
            foot = round_poly([(x0, -fd), (x1, -fd), (x1, fd), (x0, fd)], 0.005, 1)
            slab(leg, foot, (0, 1), BASE[3], Z_FOOT, r=0.0, r1=0.0015, seg=1, caps=(False, True))
            # post: a cast transition to the foot below and to the cross-head above (the section is
            # wider by 2.5 and 1.8 mm); the ends are in the foot and in the cross-head
            sec = ccw([(xc + x * s, y) for x, y in leg_poly(0)])
            rings = [(Z_FOOT - 0.0005, 0.0025), (Z_FOOT + 0.0065, 0.0), (Z_LEG - 0.0075, 0.0), (Z_LEG + 0.0015, 0.0018)]
            loft(leg, [[(a, b, z) for a, b in (offset_poly(sec, d) if d > 0 else sec)] for z, d in rings],
                 cap_lo=False, cap_hi=False)
            # cast rib at the foot, outside
            xa = xc + s * LW
            tri = [(xa, Z_FOOT - 0.0005), (xa + s * 0.011, Z_FOOT - 0.0005), (xa, Z_FOOT + 0.017)]
            slab(leg, tri, (0, 2), -0.003, 0.003, r=0.0006, seg=1)
        else:
            g.box(leg, x0, x1, -fd, fd, BASE[3], Z_FOOT)
            g.prism(leg, [(xc + x * s, y) for x, y in leg_poly(1)], (0, 1), Z_FOOT - 0.001, Z_LEG)
        parts.append(leg)
    fr = P("arch", "frame")
    # arched cross-head: profile in XZ, extruded along Y; the ends are rounded, as on a casting
    xs_b = [-CB_X, -0.058, -0.040, -0.020, 0.0, 0.020, 0.040, 0.058, CB_X]
    xs_t = [CB_X, 0.053, 0.027, 0.0, -0.027, -0.053, -CB_X]
    if lod > 0:
        xs_b = [-CB_X, -0.058, -0.029, 0.0, 0.029, 0.058, CB_X]
        xs_t = [CB_X, 0.040, 0.0, -0.040, -CB_X]
    poly = [(x, bot_z(x)) for x in xs_b] + [(x, top_z(x)) for x in xs_t]
    nb = len(xs_b)
    corners = {0: (0.003, 1), nb - 1: (0.003, 1), nb: (0.005, 2), len(poly) - 1: (0.005, 2)}
    rr = [corners.get(i, (0.0, 1))[0] for i in range(len(poly))]
    nn = [corners.get(i, (0.0, 1))[1] for i in range(len(poly))]
    if lod == 0:
        # edges rounded: at the front (toward the person) an arc, at the back a chamfer
        slab(fr, round_poly(poly, rr, nn), (0, 2), -CD, CD, r=0.003, seg=2, seg1=1)
    else:
        slab(fr, round_poly(poly, rr, 1), (0, 2), -CD, CD, r=0.002, seg=1)
    # nut boss: chamfers on top and bottom, the screw goes into a hole with a chamfer
    boss = P("boss", "frame")
    h = Z_BOSS[1] - Z_BOSS[0]
    prof = [(0.0105, 0.0), (0.0158, 0.0), (BOSS_R, 0.0022), (BOSS_R, h - 0.0022), (0.0158, h), (0.0105, h)]
    lathe(boss, axis_frame((0, 0, Z_BOSS[0]), (0, 0, 1)), prof, spec["sides"])
    parts += [fr, boss]
    if lod == 0:
        bolts = P("bolts", "bolt")
        ws = P("washers", "washer")
        for x, y in BOLTS:
            washer(ws, axis_frame((x, y, Z_FOOT), (0, 0, 1)), 0.0078, 0.0016)
            hex_head(bolts, axis_frame((x, y, Z_FOOT + 0.0016), (0, 0, 1)), 0.013, 0.0055)
        plate = P("plate", "alu")
        x0, x1, z0, z1 = PLATE
        g.box(plate, x0, x1, -CD - 0.0009, -CD + 0.0005, z0, z1, r=0.0004, seg=1)
        for x in (x0 + 0.003, x1 - 0.003):
            lathe(plate, axis_frame((x, -CD - 0.0009, (z0 + z1) / 2), (0, -1, 0)),
                  [(0.0016, 0.0), (0.0013, 0.0006), (0.0006, 0.0010)], 8, cap_hi=True)
        parts += [bolts, ws, plate]
    else:
        bolts = P("bolts", "bolt")
        for x, y in BOLTS:
            hexagon(bolts, (x, y, Z_FOOT), (0, 0, 1), 0.013, 0.0068)
        plate = P("plate", "alu")
        x0, x1, z0, z1 = PLATE
        g.box(plate, x0, x1, -CD - 0.0009, -CD + 0.0005, z0, z1)
        parts += [bolts, plate]
    return parts


# --- screw, foot, handle ------------------------------------------------------------------------
def build_screw(spec):
    lod, n = spec["lod"], spec["sides"]
    up = (0, 0, 1)
    sc = P("screw", "screw", group=SEL_SCREW)
    lo, hi = Z_PAD + PAD_H - 0.001, Z_BOSS[0] + TRAVEL + 0.001     # visible piece under the boss in both looks
    if lod == 0:
        helix_thread(sc, axis_frame((0, 0, 0), up), lo, hi, SCREW_R, DEPTH, PITCH, cols=10)
    else:
        lathe(sc, axis_frame((0, 0, lo - 0.002), up), [(SCREW_R - 0.0005, 0.0), (SCREW_R - 0.0005, hi - lo + 0.004)], 8)
    th = P("screw_top", "thread", group=SEL_SCREW)
    z0 = Z_BOSS[1] - 0.004
    lathe(th, axis_frame((0, 0, z0), up), [(SCREW_R - 0.0005, 0.0), (SCREW_R - 0.0005, Z_HEAD[0] + 0.002 - z0)],
          10 if lod == 0 else 8)
    pad = P("pad", "pad", group=SEL_PAD)
    prof = [(0.0228, 0.0), (0.0240, 0.0012), (0.0240, 0.0078), (0.0222, 0.0098), (0.0135, 0.0112),
            (0.0135, 0.0162), (0.0118, PAD_H)]
    if lod > 0:
        prof = [(0.024, 0.0), (0.024, 0.0090), (0.0135, 0.0110), (0.0118, PAD_H)]
    lathe(pad, axis_frame((0, 0, Z_PAD), up), prof, 20 if lod == 0 else n, cap_lo=True, cap_hi=True)
    hd = P("head", "head", group=SEL_SCREW)
    h = Z_HEAD[1] - Z_HEAD[0]
    prof = [(0.0090, 0.0), (0.0128, 0.0), (0.015, 0.0022), (0.015, h - 0.0022), (0.0128, h)]
    if lod > 0:
        prof = [(0.0125, 0.0), (0.015, 0.002), (0.015, h - 0.002), (0.013, h)]
    lathe(hd, axis_frame((0, 0, Z_HEAD[0]), up), prof, 16 if lod == 0 else n, cap_lo=lod > 0, cap_hi=True)
    bar = P("bar", "bar", group=SEL_SCREW)
    # handle bar: the ends are in the upset heads, no end faces needed
    lathe(bar, axis_frame((BAR_X[0], 0.0, Z_BAR), (1, 0, 0)), [(BAR_R, 0.0), (BAR_R, BAR_X[1] - BAR_X[0])], spec["rod"])
    knob = ([(0.0046, 0.0), (0.0066, 0.0011), (0.0072, 0.0034), (0.0064, 0.0060), (0.0030, 0.0074)] if lod == 0 else
            [(0.0046, 0.0), (0.0070, 0.0020), (0.0060, 0.0070)])
    for x0, sgn in ((BAR_X[0], -1), (BAR_X[1], 1)):      # upset ends keep the handle from falling out of the head
        lathe(bar, axis_frame((x0 - 0.001 * sgn, 0.0, Z_BAR), (sgn, 0, 0)), knob, spec["knob"], cap_hi=True)
    return [sc, th, pad, hd, bar]


# --- Kevlar and the pressure plate --------------------------------------------------------------
def pack_outline():
    """Scissor-cut edge of the stack: edges not by a ruler, corners slightly cut."""
    y0, y1 = PACK_Y
    return [(-PACK_X + 0.002, y0), (-0.010, y0 - 0.0008), (0.022, y0 + 0.0006), (PACK_X - 0.003, y0 + 0.0002),
            (PACK_X, y0 + 0.004), (PACK_X - 0.0008, -0.010), (PACK_X + 0.0004, y1 - 0.003), (PACK_X - 0.004, y1),
            (0.004, y1 + 0.0008), (-PACK_X + 0.003, y1 - 0.0004), (-PACK_X, y1 - 0.004), (-PACK_X - 0.0006, -0.020),
            (-PACK_X + 0.0003, y0 + 0.003)]


def build_pack(spec):
    lod = spec["lod"]
    pk = P("pack", "kevlar")
    if lod == 0:
        # 12 fabric layers stacked unevenly: the middle of the stack is slightly shifted, the top
        # edge is soft
        out = ccw(pack_outline())
        z0, z1 = Z_PACK
        rings = [(jitter_poly(out, 0.0003, 1), z0), (jitter_poly(out, 0.0008, 2), (z0 + z1) / 2),
                 (jitter_poly(offset_poly(out, -0.0003), 0.0003, 3), z1 - 0.0007),
                 (offset_poly(out, -0.0011), z1)]
        loft(pk, [[(x, y, z) for x, y in ring] for ring, z in rings])
        cut = P("pack_cut", "kevlar")
        g.cyl(cut, (HOLE[0], HOLE[1], (Z_PACK[0] + Z_PACK[1]) / 2), "z", HOLE[2], Z_PACK[1] - Z_PACK[0] + 0.004, 14)
        pk = M.boolean("pack_h", pk, [cut])
        # cut-out sample: a D 30 disc of the same 12 layers (the bottom lies on the plate)
        disc = P("disc", "kevlar")
        lathe(disc, axis_frame((DISC[0], DISC[1], BASE[3]), (0, 0, 1)),
              [(0.0149, 0.0), (0.0151, 0.0110), (0.0142, Z_PACK[1] - Z_PACK[0])], 14, cap_hi=True)
        parts = [pk, disc]
    else:
        g.prism(pk, pack_outline(), (0, 1), Z_PACK[0], Z_PACK[1])
        disc = P("disc", "kevlar")
        lathe(disc, axis_frame((DISC[0], DISC[1], BASE[3]), (0, 0, 1)),
              [(0.0150, 0.0), (0.0148, Z_PACK[1] - Z_PACK[0])], 8, cap_hi=True)
        parts = [pk, disc]
    cv = P("cover", "cover")
    hx, y0, y1, t = COVER
    if lod == 0:
        slab(cv, round_poly([(-hx, y0), (hx, y0), (hx, y1), (-hx, y1)], 0.002, 1), (0, 1), Z_PACK[1], Z_COVER,
             r=0.0008, seg=1, caps=(False, True))
    else:
        g.box(cv, -hx, hx, y0, y1, Z_PACK[1], Z_COVER)
    return parts + [cv]


def build_lod(spec):
    parts = build_base(spec) + build_frame(spec) + build_screw(spec) + build_pack(spec)
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("bounds: %s .. %s" % (tuple(round(c, 4) for c in BOUNDS["lo"]),
                                   tuple(round(c, 4) for c in BOUNDS["hi"])))
    return parts


def ring_pts(r, z, n=8):
    return [(r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), z) for k in range(n)]


def collision():
    """Seven convex parts: the plate; the left and right posts with feet; the cross-head with the boss;
    the screw with the foot and head (along the screw: from the foot on the plate to the head at
    rest); the handle; the Kevlar with the pressure plate. Mass is the item's weight in the mod, 0.8 kg.
    """
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    hx, y0, y1, t = BASE
    fin, fout, fd, ft = FOOT
    comps = [(kx.box_pts(-hx, hx, y0, y1, 0.0, t), kx.PEN + r"\metalplate.rvmat")]
    for s in (-1, 1):
        x0, x1 = sorted((s * (XL + fin), s * (XL + fout)))
        comps.append((kx.box_pts(x0, x1, -fd, fd, t, Z_FOOT) + kx.box_pts(s * XL - LW, s * XL + LW, -LD, LD, t, Z_LEG),
                      kx.PEN + r"\castiron.rvmat"))
    xs = [-CB_X + 2 * CB_X * k / 8 for k in range(9)]
    arch = [(x, y, z) for x in xs for y in (-CD, CD) for z in (top_z(x), 0.088)]
    comps.append((arch + ring_pts(BOSS_R, Z_BOSS[0]) + ring_pts(BOSS_R, Z_BOSS[1]), kx.PEN + r"\castiron.rvmat"))
    comps.append((ring_pts(0.024, Z_COVER) + ring_pts(0.024, Z_PAD + 0.010) + ring_pts(0.015, Z_HEAD[0])
                  + ring_pts(0.015, Z_HEAD[1]), kx.PEN + r"\iron.rvmat"))
    comps.append((kx.box_pts(BAR_X[0] - 0.008, BAR_X[1] + 0.008, -0.007, 0.007, Z_BAR - 0.007, Z_BAR + 0.007),
                  kx.PEN + r"\iron.rvmat"))
    comps.append((kx.box_pts(-PACK_X, PACK_X, PACK_Y[0], PACK_Y[1], Z_PACK[0], Z_COVER), kx.PEN + r"\fabricp.rvmat"))
    memory = {
        # inventory preview camera: front-left and from above (invView = camera position)
        "invView": [(-0.24, -0.40, 0.32)],
        "ce_center": [(0.0, 0.0, 0.082)],
        "ce_radius": [(0.14, 0.0, 0.082)],
        # work look: the foot travel is a metre down (the offset is in metres), the screw rotation
        # axis goes up along the screw
        "ozl_pad_axis": [(0.0, 0.0, Z_HEAD[1]), (0.0, 0.0, Z_HEAD[1] - 1.0)],
        "ozl_work_axis": SCREW_AXIS,                     # bottom to top (the angle sign is at CLAMP_TURN)
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


# the first three are the --look preview (overall view, the main unit close up, from the right); the
# work look uses the first two
SHOTS = [
    ("front", (-0.20, -0.50, 0.30), (0.0, -0.005, 0.082), 40),
    ("press", (-0.13, -0.26, 0.17), (-0.008, -0.030, 0.050), 50),
    ("right", (0.46, -0.26, 0.20), (0.0, 0.0, 0.082), 40),
    ("back", (0.32, 0.46, 0.28), (0.0, 0.0, 0.082), 40),
    ("left", (-0.50, -0.12, 0.20), (0.0, 0.0, 0.082), 40),
    ("top", (0.03, -0.26, 0.48), (0.0, -0.005, 0.062), 40),
]

M.look_shots = (3, 2)
M.run(build_lod, collision, SHOTS, row_step=0.30, row_shot=((0.15, -0.95, 0.32), (0.15, 0, 0.07)))
