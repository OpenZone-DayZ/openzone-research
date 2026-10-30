"""M84 - compressor with a gauge (OZL_Tool_Compressor): a Protection line module (packers M25, M29,
M34), a portable 2x2 item. It sits in the slot of its number in the line (OZL_Tool1) and shows at
the machine's module place through the proxy. A hand pressure test pump: a lever, a tank, a round
gauge on a stand, a hose with a nozzle, on a steel base.

    blender --background --python build_m84.py -- [--stats] [--look] [--geo] [--skip-bake] [--no-paa] [--preview]
    (batch bake: -- --bake-only --geo-render | --look-render)

Run make_decals.py (system Python) before the first build: the gauge dial, the tank tag.

Size: about 0.20 x 0.22 x 0.12 m, the lever up not higher than ~0.25 m, a gauge of D ~10 cm, grey
enamel. The module is at most ~0.2 x 0.2 m at the base and up to ~0.25 m high, flat bottom (module
places are 0.30 m apart on M25, 0.25 m on M29 and M34).

Sample and sizes:
- The look is a hand pressure test pump (a photo of a pressure testing pump from Wikimedia
  Commons): a steel tank, a pump with a plunger, a lever on a clevis, a gauge on a riser above the
  pump outlet, a valve with a red handwheel, a rubber high-pressure hose; the tank in grey-blue enamel.
- Real test pumps of this kind are bigger than the module place: a tank of ~12 l (Rothenberg RP 50,
  REMS Push), BES 22337 - 490 x 160 x 160 mm, 7.64 kg, a 60 mm gauge, a 1.5 m hose with a 1/2"
  BSP end. No bench test pump of 0.2 m with a datasheet was found, so the module is such a device in
  a bench version, assembled from parts of real size:
  - a general-purpose gauge D 100 mm (MP-100 / MTP-100, GOST 2405: case 100 mm, M20 x 1.5 fitting,
    0.3 kg; D 100 and G 1/2 B - WIKA 113.53): here with a rear fitting (hexagon 22) on a riser of
    1/4" tube (13.5 mm), case 100 x 36 mm, ring 103 mm;
  - a valve with a handwheel D 34 mm (red, as in the photo), a brass manifold 30 x 30 mm;
  - the pump: a body D 38 mm on a flange with three bolts, a gland nut across flats 34, a plunger
    D 11 mm, the lever is a 14 x 8 mm strip on a fork post, a grip D 15 mm with a rubber handle
    D 19; the 0.18 m lever is raised by 40 degrees and lies over the tank, as in the photo;
  - a tank 87 x 120 x 92 mm (~0.9 l) with a filler plug; the base is a 5 mm plate on two channels
    22 x 15, 190 x 180 mm;
  - a high-pressure hose D 13 mm with crimped ferrules and a union nut on the nozzle;
  bounds 0.192 x 0.180 x 0.242 m - they fit the module pad;
- the in-game weight is 800 g (OZL_Tool_Base, unchanged); the mass in Geometry is the same.

Details: the "dayz" look (more matte, dirtier, AO in colour); parts without angularity: rounded
edges of the tank, lid, plate and manifold; solids of revolution with chamfers and grooves (pump
body, lever grip, valve bonnet, gauge ring); nuts and fittings are turned hexagons with a chamfer;
channels are a real U profile; lid screws are slotted; the plug is knurled; the hose is a smooth
curve with crimped ferrules; the lever is a plate with a rounded end, the fork post sits on a
welded lug, the plunger clevis has cheeks. No vanilla items are put on the module itself: it is
carried in hands and put into a slot, and a stuck-on item would travel with it.

Condition (no faction colour): used but intact, worn paint on the edges; the grey enamel is chipped
to metal along the edges, the lever grip is rubbed. Markings: the digits of the 0-16 scale and
"2,5", a red tick of the working pressure at 10, an aluminium inventory tag "0417" on the tank, a
lead verification seal on a wire by the gauge. No letters.

Work look: no lamps or screens, the moving parts come alive:
- the lever - bone ozl_work on the source ozl_work: phase 0 is raised (as the model stands), 1 is
  the handle lowered by LEVER_SWING; the plunger with the clevis and pin - bone ozl_plunger on the
  same source, a PLUNGER_STROKE travel down (the pin follows the lever slot, which the clevis
  cheeks cover); in the work look OZL_WorkFx drives ozl_work (wobble 0..1 over 1.6 s);
- the gauge needle - bone ozl_needle on the source ozl_needle: phase 0 is zero, 1 is 16 of 16 (the
  whole scale); in the work look it sits at the red tick 10 and trembles in time with the pumping
  (wobble).
The angle sign is as for the M14 and M33 needles (the axis points to the dial face): if the needle
goes counter-clockwise in game, flip the sign of angle1 of the needle and the lever.
The work look has no atlas of its own (nothing glows): the "on" look is only a pose for the --look
preview (the lever and needle rotation is m84_shapes.install_pose), it does not go into baking or
the p3d.

LODs: near ~5.6k and mid ~1.6k triangles (~28 %: no bolts, screws, seal, handwheel spokes,
chamfers; cylinders and the hose are sparser), no far one. The near LOD is above the 1.5k
guideline: the smooth gauge, hose, handwheel and grip are the most expensive.

Blender axes: X is width, Y is depth (the face at -Y), Z is up. The origin is the centre of the
bottom, so the module lands on the module_N proxy point (autocenter = 0 in Geometry).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import m84_shapes as sh  # noqa: E402
from mathutils import Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m ------------------------------------------------------------------------------
# base: a 5 mm plate on two channels across (U profile 22 x 15, wall 2.5, flanges down)
BX0, BX1, BY0, BY1 = -0.095, 0.095, -0.092, 0.088
RUN_H, ZB = 0.015, 0.020
RUN_Y, RUN_W, RUN_T = (BY0 + 0.016, BY1 - 0.016), 0.022, 0.0025
BOLTS = [(sx * 0.082, y) for sx in (-1, 1) for y in RUN_Y]
# tank on the left
TX0, TX1, TY0, TY1, TZ1 = -0.093, -0.006, -0.040, 0.080, 0.112
CAP = (-0.074, 0.062)
TAG = (-0.050, 0.070)                   # tag on the tank face (x, z)
TAG_W, TAG_H = 0.044, 0.024
# pump at the rear right: body, flange foot, gland nut, plunger
XP, YP = 0.030, 0.046
PR, PF_R, PF_H, PZ1 = 0.019, 0.027, 0.006, 0.100
GLAND_R, GLAND_Z1 = 0.0195, 0.112
ROD_R = 0.0055
# lever in the plane y = YP, raised by TH to the left, over the tank; A - the plunger pin, F - the
# axis on the fork post; VL - across the lever, up
TH = math.radians(40.0)
D = Vector((-math.cos(TH), 0.0, math.sin(TH)))
VL = Vector((math.sin(TH), 0.0, math.cos(TH)))
ZA = 0.146
A = Vector((XP, YP, ZA))
F = A - D * 0.028
LEV_T, LEV_W = 0.008, 0.014
S_BAR, S_TUBE, S_GRIP, S_END = (-0.012, 0.118), (0.108, 0.165), (0.114, 0.165), 0.170
TUBE_R, GRIP_R = 0.0076, 0.0095
POST_W, POST_T, POST_Y = 0.012, 0.004, 0.0065
# plunger clevis: cheeks at the sides of the lever (half-width along x, from the lever outward along
# y), a bridge under it
CLV_W, CLV_Y0, CLV_Y1 = 0.0055, LEV_T / 2 + 0.0005, LEV_T / 2 + 0.0035
CLV_Z0, CLV_ZB = ZA - 0.0195, ZA - 0.0145
# fork post lug, welded to the pump collar: x0, x1, z0, z1
LUG = (XP + PR - 0.003, F.x + POST_W / 2, PZ1 - 0.0115, PZ1 - 0.0015)
# brass manifold: gauge riser up, valve forward, hose to the left
MX, MY, MS, MZ1 = 0.046, -0.006, 0.030, 0.054
STAND_R = 0.00675                       # 1/4" tube
VB = (MX - 0.009, MX + 0.009, MY - MS / 2 - 0.012, MY - MS / 2, 0.026, 0.050)    # valve body
VZ = 0.038                              # valve stem axis
WY, WR, WRR = -0.0515, 0.0145, 0.0022   # handwheel: plane, rim radius, section
HZ = 0.036                              # hose fitting axis
# gauge D 100: centre, case depth from YC (h is forward, toward -Y)
GX, GZ, YC = MX, 0.160, -0.040
GR = 0.050
H_BACK, H_CASE, H_BEZ = -0.018, 0.016, 0.0235
DIAL_R, H_DIAL, H_NEEDLE, H_GLASS = 0.046, 0.0165, (0.0180, 0.0190), 0.0215
NEEDLE_L, A_ZERO, A_SPAN = 0.0385, math.radians(225.0), math.radians(270.0)
# hose: from the valve fitting forward and left, a loop in front of the tank, the nozzle lies by the
# valve (the nozzle nut sits on a flat on the plate)
HOSE_R = 0.0065
ZH = ZB + HOSE_R + 0.0002
NOZ_NUT = 0.0166                        # nozzle union nut across flats
NOZ_Z = ZB + NOZ_NUT / 2 + 0.0001
NOZ_DIR = Vector((0.92, 0.39, 0.0)).normalized()
NOZ_E = Vector((0.010, -0.0785, NOZ_Z))  # start of the nozzle ferrule on the axis
FER_X, HOSE_Y0 = 0.015, -0.027          # ferrule end at the valve
# hose path over the plate in arcs of constant radius: from the ferrule to the left, an S-bend (R
# 10) forward past the tank corner, along the tank face, a loop R 18 at the left edge of the plate,
# back along the edge and an arc R 30 coaxially into the nozzle ferrule; in height - smoothly from
# the fitting axis to the plate and from the plate to the nozzle axis
HOSE_R1, HOSE_RU, HOSE_RN = 0.010, 0.018, 0.030
HOSE_YA = HOSE_Y0 - 2 * HOSE_R1                       # straight along the tank face
HOSE_XU = -0.070                                       # loop start
NOZ_DEG = math.degrees(math.atan2(NOZ_DIR.y, NOZ_DIR.x))
_dyn = HOSE_RN * (1 - math.cos(math.radians(NOZ_DEG)))
_ln = (NOZ_E.y - (HOSE_YA - 2 * HOSE_RU) - _dyn) / math.sin(math.radians(NOZ_DEG))
_l2 = NOZ_E.x - HOSE_XU - HOSE_RN * math.sin(math.radians(NOZ_DEG)) - _ln * math.cos(math.radians(NOZ_DEG))
HOSE_SEGS = [("arc", HOSE_R1, 90.0), ("arc", HOSE_R1, -90.0), ("line", (FER_X - 2 * HOSE_R1) - HOSE_XU),
             ("arc", HOSE_RU, 180.0), ("line", _l2), ("arc", HOSE_RN, NOZ_DEG), ("line", _ln)]
HOSE_S_DOWN = math.pi * HOSE_R1                       # by the end of the S-bend the hose has settled onto the plate


def hose_path(step_deg, max_len):
    """Hose points: the route2d path with height; the ends are 3 mm inside the ferrules (no gap at the joint)."""
    flat = sh.route2d((FER_X, HOSE_Y0), 180.0, HOSE_SEGS, step_deg, max_len)
    s_end = flat[-1][2]
    s_up = s_end - (HOSE_RN * math.radians(NOZ_DEG) + _ln)
    pts = [(FER_X + 0.003, HOSE_Y0, HZ)]
    for x, y, s in flat:
        z = HZ + (ZH - HZ) * sh.smoothstep(0.0, HOSE_S_DOWN, s) + (NOZ_Z - ZH) * sh.smoothstep(s_up, s_end, s)
        pts.append((x, y, z))
    pts.append(tuple(NOZ_E + NOZ_DIR * 0.003))
    return pts


# work look: the lever handle goes down by LEVER_SWING; the pin A follows the lever slot, the
# plunger strictly vertically, the travel is by the lever point above the pump axis; the needle is
# at the red tick
LEVER_SWING = math.radians(15.0)
PLUNGER_STROKE = (F.x - A.x) * (math.tan(TH) - math.tan(TH - LEVER_SWING))
WORK_BAR, SCALE_BAR = 10.0, 16.0

LOD_SPECS = [
    # hose: rings every 18 (30) degrees on arcs, straights as a single segment
    dict(lod=0, sides=16, gauge=40, hose=10, hose_step=(18.0, 0.10), grip=12, wheel=(16, 5), bev=True),
    dict(lod=1, sides=10, gauge=20, hose=8, hose_step=(30.0, 0.10), grip=10, wheel=(10, 4), bev=False),
]

REGIONS = {
    "tank": ("enamel", 1.0), "pump": ("enamel", 1.0), "base": ("base", 0.8), "lever": ("lever", 1.0),
    "steel": ("steel", 0.8), "chrome": ("chrome", 1.0), "bolt": ("bolt", 0.6), "brass": ("brass", 1.2),
    "pipe": ("copper", 0.8), "galv": ("galv", 0.8), "wheel": ("wheel", 1.2), "hose": ("hose", 0.7),
    "grip": ("grip", 1.0), "case": ("case", 1.2), "bezel": ("bezel", 1.4), "dial": ("dial", 4.0),
    "needle": ("needle", 0.8), "tag": ("tag", 3.0), "lead": ("lead", 1.0), "cap": ("black", 1.0),
    "glass": ("chrome", 1.0), "dark": ("dark", 0.3),
}


def wdecal(name):
    return os.path.join(WORK, name)


Y_DIAL = YC - H_DIAL
DIAL_DEC = (wdecal("decal_dial.png"), "y", -1, ("x", "z"), (GX, GZ), (2 * DIAL_R, 2 * DIAL_R),
            (Y_DIAL - 0.0005, Y_DIAL + 0.0005))
TAG_DEC = (wdecal("decal_tag.png"), "y", -1, ("x", "z"), TAG, (TAG_W, TAG_H), (TY0 - 0.0025, TY0 - 0.0006))

# modules: worn on the edges, small chips, almost no rust (only rare specks in chips)
USED = dict(chip=(0.55, 0.61), rust=(0.90, 0.95), rust_low=0.15, floor_z=0.0, dust=0.22, grime=0.42)
LIT = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
METAL = kmats.lin((142, 144, 146))
GREY = kmats.lin((122, 130, 134))       # grey enamel with a cool tint (M85 has hammered)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "enamel": ("paint", dict(USED, color=GREY, under=METAL, seed=2.4, gloss=0.38, spec=0.28)),
    "base": ("paint", dict(USED, chip=(0.50, 0.57), color=kmats.lin((98, 104, 106)), under=METAL, seed=3.1,
                           gloss=0.30, spec=0.24, grime=0.55, rust=(0.84, 0.90), rust_low=0.25)),
    # lever: it is taken by hand - the enamel is worn more
    "lever": ("paint", dict(USED, chip=(0.46, 0.54), color=GREY, under=METAL, seed=3.7, gloss=0.38, spec=0.28)),
    "steel": ("steel", dict(seed=4.3, tone=0.32, along="z", gloss=0.5, spec=0.6, dust=0.2, grime=0.4)),
    "chrome": ("steel", dict(seed=4.9, tone=0.58, along="z", gloss=0.75, spec=0.8, dust=0.05, grime=0.25)),
    "bolt": ("steel", dict(seed=5.4, tone=0.36, along="x", gloss=0.42, spec=0.5, dust=0.25, grime=0.55)),
    # brass and copper have darkened: a dull patina, lighter only on the edges ("chips" go down to
    # clean metal)
    "brass": ("paint", dict(color=kmats.lin((146, 114, 62)), under=kmats.lin((184, 148, 82)), seed=6.0, gloss=0.42,
                            spec=0.5, chip=(0.62, 0.70), rust=(0.99, 1.0), rust_low=0.0, dust=0.25, grime=0.7)),
    "copper": ("paint", dict(color=kmats.lin((140, 86, 56)), under=kmats.lin((176, 108, 70)), seed=6.6, gloss=0.40,
                             spec=0.45, chip=(0.7, 0.8), rust=(0.99, 1.0), rust_low=0.0, dust=0.25, grime=0.6)),
    "galv": ("steel", dict(seed=7.1, tone=0.46, along="z", gloss=0.4, spec=0.45, dust=0.2, grime=0.4)),
    "wheel": ("paint", dict(USED, chip=(0.60, 0.66), color=kmats.lin((160, 30, 24)), under=kmats.lin((70, 66, 64)),
                            seed=7.7, gloss=0.42, spec=0.32)),
    # rubber of the hose and handle: almost no dust or streaks - the kit lays them by the face
    # normal, and on 10-12-sided cylinders that gives stripes along the faces
    "hose": ("plastic", dict(color=kmats.lin((30, 30, 31)), seed=8.2, gloss=0.20, spec=0.10, dust=0.05, grime=0.10,
                             mottle=0.08, scuff=(0.84, 0.94))),
    "grip": ("plastic", dict(color=kmats.lin((27, 27, 28)), seed=8.6, gloss=0.12, spec=0.06, dust=0.05, grime=0.12,
                             mottle=0.08, scuff=(0.80, 0.92))),
    "case": ("paint", dict(USED, chip=(0.66, 0.72), color=kmats.lin((34, 35, 37)), under=METAL, seed=8.8,
                           gloss=0.40, spec=0.30, dust=0.18)),
    "bezel": ("steel", dict(seed=9.3, tone=0.34, along="x", gloss=0.58, spec=0.65, dust=0.15, grime=0.45)),
    "dial": ("paint", dict(LIT, color=kmats.lin((236, 233, 222)), gloss=0.5, spec=0.3, decal_items=[DIAL_DEC])),
    "needle": ("flat", dict(color=kmats.lin((20, 20, 21)), gloss=0.5, spec=0.35)),
    "tag": ("paint", dict(LIT, color=kmats.lin((184, 188, 186)), gloss=0.55, spec=0.6, dust=0.15, grime=0.2,
                          decal_items=[TAG_DEC])),
    "lead": ("plastic", dict(color=kmats.lin((112, 114, 116)), seed=9.9, gloss=0.25, spec=0.2, dust=0.2,
                             grime=0.4, scuff=(0.7, 0.8))),
    # screw slots, hex sockets
    "dark": ("flat", dict(color=kmats.lin((14, 14, 15)), gloss=0.2, spec=0.1)),
})

OBJ, NAME = "m84_test_pump", "ozr_test_pump"
SEL_LEVER, SEL_PLUNGER, SEL_NEEDLE = "ozl_work", "ozl_plunger", "ozl_needle"
# lever and needle: the axis points to the face (-Y in Blender), the angle sign is as for the
# M14/M33 needles: the needle clockwise is plus, the lever handle down (counter-clockwise seen from
# the face) is minus
LEVER_ANIM = ("ozl_work_lever", dict(type="rotation", source="ozl_work", selection=SEL_LEVER, axis="ozl_work_axis",
                                     memory=1, minValue=0.0, maxValue=1.0, angle0=0.0, angle1=-LEVER_SWING))
# plunger axis - a metre down from the pin: the offset is in metres
PLUNGER_ANIM = ("ozl_work_plunger", dict(type="translation", source="ozl_work", selection=SEL_PLUNGER,
                                         axis="ozl_plunger_axis", memory=1, minValue=0.0, maxValue=1.0,
                                         offset0=0.0, offset1=PLUNGER_STROKE))
NEEDLE_ANIM = ("ozl_needle_rot", dict(type="rotation", source="ozl_needle", selection=SEL_NEEDLE,
                                      axis="ozl_needle_axis", memory=1, minValue=0.0, maxValue=1.0, angle0=0.0,
                                      angle1=A_SPAN))
# work look preview: the handle at the bottom of the stroke, the plunger down, the needle at 10 (not
# in the p3d - that is model.cfg)
ON = dict(remap={}, move={
    SEL_LEVER: sh.rot_about(F, (0.0, 1.0, 0.0), -LEVER_SWING),
    SEL_PLUNGER: (0.0, 0.0, -PLUNGER_STROKE),
    SEL_NEEDLE: sh.rot_about((GX, 0.0, GZ), (0.0, 1.0, 0.0), A_SPAN * WORK_BAR / SCALE_BAR),
})
LOOK_RUN = "--look" in kmodel.ARGV or "--look-render" in kmodel.ARGV
sh.install_pose()
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 glass=dict(base=(0.80, 0.82, 0.80), clear=0.05, edge=0.12, smudge=0.12, streaks=0.05),
                 selections=(SEL_LEVER, SEL_PLUNGER, SEL_NEEDLE),
                 bones=((SEL_LEVER, ""), (SEL_PLUNGER, ""), (SEL_NEEDLE, "")),
                 animations=(LEVER_ANIM, PLUNGER_ANIM, NEEDLE_ANIM),
                 states={"on": ON} if LOOK_RUN else None,
                 sources={"ozl_work": dict(animPeriod=0.2), "ozl_needle": dict(animPeriod=0.2)})
M.look_shots = (4, 3)
P = M.part
BOUNDS = {}

# frames: gauge (n toward the face, -Y), lever (n along the lever), handwheel (n toward the face)
GF = g.Frame((GX, YC, GZ), (1, 0, 0), (0, 0, 1), (0, -1, 0))
LAX = g.Frame(F, (0, -1, 0), VL, D)
LBAR = g.Frame(F, D, VL, (0, 1, 0))
WF = g.Frame((MX, WY, VZ), (1, 0, 0), (0, 0, 1), (0, -1, 0))


def zf(x, y, z=0.0, phase=0.0):
    """Frame with the axis up at the point (x, y, z)."""
    return sh.axis_frame((x, y, z), "z", phase)


def bevel_kw(spec, r, seg=2):
    return {"r": r, "seg": seg} if spec["bev"] else {}


# =============================================================================
# Base and tank
# =============================================================================
def build_base(spec):
    lod = spec["lod"]
    parts = []
    pl = P("plate", "base")
    g.box(pl, BX0, BX1, BY0, BY1, RUN_H, ZB, **bevel_kw(spec, 0.0018))
    parts.append(pl)
    rn = P("runners", "base")
    for y in RUN_Y:
        sh.channel(rn, BX0 + 0.004, BX1 - 0.004, y, RUN_W, RUN_H, RUN_T)
    parts.append(rn)
    if lod == 0:
        # plate bolts into the channels: a washer and a head across flats 10 with a chamfer; there
        # is no bolt under the hose loop - none is placed (the hose would lie on the head)
        hose = [Vector(p[:2]) for p in hose_path(15.0, 0.012)]
        bl = P("plate_bolts", "bolt")
        for i, (x, y) in enumerate(BOLTS):
            if min((q - Vector((x, y))).length for q in hose) < HOSE_R + 0.0085:
                continue
            fr = zf(x, y, ZB, 0.35 + 0.7 * i)
            sh.washer(bl, fr, 0.0, 0.0011, 0.0080, 8)
            sh.nut(bl, fr, 0.0011, 0.0053, 0.010, ch_lo=False, cap_lo=False)
        parts.append(bl)
    return parts


def build_tank(spec):
    lod, n = spec["lod"], spec["sides"]
    parts = []
    tk = P("tank", "tank")
    g.box(tk, TX0, TX1, TY0, TY1, ZB, TZ1 - 0.002, **({"r": 0.006, "seg": 2} if lod == 0 else {"r": 0.004, "seg": 1}))
    parts.append(tk)
    # tank lid: a flanged sheet on four slotted screws
    ld = P("tank_lid", "tank")
    g.box(ld, TX0 - 0.002, TX1 + 0.002, TY0 - 0.002, TY1 + 0.002, TZ1 - 0.0045, TZ1 + 0.0005,
          **bevel_kw(spec, 0.0016, 1))
    parts.append(ld)
    if lod == 0:
        ls = P("lid_screws", "bolt")
        sl = P("lid_slots", "dark")
        k = 0
        for x in (TX0 + 0.007, TX1 - 0.007):
            for y in (TY0 + 0.007, TY1 - 0.007):
                fr = zf(x, y, TZ1 + 0.0004)
                sh.pan_head(ls, fr, 0.0, 0.0033, 0.0018, 8, segs=2)
                sh.slot(sl, fr, 0.0017, 0.0050, 0.0007, 0.0005, math.radians(25 + 47 * k))
                k += 1
        parts += [ls, sl]
    # filler neck and knurled plug
    cx, cy = CAP
    nk = P("cap_neck", "tank")
    g.cyl(nk, (cx, cy, TZ1 + 0.00325), "z", 0.0115, 0.0065, n, cap=False)
    parts.append(nk)
    cp = P("cap", "cap")
    if lod == 0:
        sh.knurled(cp, zf(cx, cy), 0.0150, 0.0011, TZ1 + 0.005, TZ1 + 0.0175, 12)
    else:
        g.cyl(cp, (cx, cy, TZ1 + 0.011), "z", 0.015, 0.0125, n)
    parts.append(cp)
    # inventory tag on the tank face (rounded corners), two rivets
    tx, tz = TAG
    tg = P("tag", "tag")
    if lod == 0:
        g.prism(tg, sh.rrect(tx, tz, TAG_W, TAG_H, 0.0022, 3), (0, 2), TY0 - 0.0012, TY0 + 0.0003)
    else:
        g.box(tg, tx - TAG_W / 2, tx + TAG_W / 2, TY0 - 0.0012, TY0 + 0.0003, tz - TAG_H / 2, tz + TAG_H / 2)
    parts.append(tg)
    if lod == 0:
        rv = P("tag_rivets", "steel")
        for dx in (-TAG_W / 2 + 0.0046, TAG_W / 2 - 0.0046):
            sh.pan_head(rv, sh.axis_frame((tx + dx, TY0 - 0.0012, tz), "-y"), 0.0, 0.0020, 0.0010, 6, segs=2)
        parts.append(rv)
        # drain plug at the bottom of the back wall: a washer and a hexagon
        dp = P("drain_plug", "bolt")
        fr = sh.axis_frame((-0.072, TY1, ZB + 0.013), "y", 0.3)
        sh.washer(dp, fr, 0.0, 0.0012, 0.0085, 8)
        sh.nut(dp, fr, 0.0012, 0.0062, 0.013, ch_lo=False, cap_lo=False)
        parts.append(dp)
    return parts


# =============================================================================
# Pump and lever
# =============================================================================
def build_pump(spec):
    lod, n, bev = spec["lod"], spec["sides"], spec["bev"]
    parts = []
    # body as one solid of revolution: a flange foot with a rounded edge, a fillet, a cylinder, a
    # collar under the fork
    bd = P("pump_body", "pump")
    fr = zf(XP, YP)
    if lod == 0:
        prof = [(PF_R, ZB), (PF_R, ZB + PF_H - 0.0013), (PF_R - 0.0013, ZB + PF_H),
                (PR + 0.0012, ZB + PF_H), (PR, ZB + PF_H + 0.0022),
                (PR, PZ1 - 0.0125), (PR + 0.0022, PZ1 - 0.0103), (PR + 0.0022, PZ1 - 0.0010), (PR + 0.0012, PZ1)]
        sh.lathe(bd, fr, prof, n, cap_hi=True)
    else:
        prof = [(PF_R, ZB), (PF_R, ZB + PF_H), (PR, ZB + PF_H), (PR, PZ1 - 0.0100), (PR + 0.0022, PZ1 - 0.0100),
                (PR + 0.0022, PZ1)]
        sh.lathe(bd, fr, prof, n, cap_hi=True)
    parts.append(bd)
    # gland nut across flats 34, a wiper
    gl = P("gland", "steel")
    sh.nut(gl, zf(XP, YP, 0.0, 0.2), PZ1, GLAND_Z1, 2 * GLAND_R * math.cos(math.pi / 6), ch_lo=bev, ch_hi=bev,
           cap_lo=False)
    parts.append(gl)
    if lod == 0:
        wp = P("wiper", "grip")
        sh.lathe(wp, fr, [(0.0078, GLAND_Z1 - 0.0002), (0.0078, GLAND_Z1 + 0.0010), (0.0066, GLAND_Z1 + 0.0016)],
                 12, cap_hi=True)
        parts.append(wp)
        fb = P("foot_bolts", "bolt")
        for k in range(3):
            a = math.radians(-90 + 120 * k)
            sh.nut(fb, zf(XP + 0.0232 * math.cos(a), YP + 0.0232 * math.sin(a), ZB + PF_H, 0.3 + k), 0.0, 0.0034,
                   0.0060, ch_lo=False, cap_lo=False)
        parts.append(fb)
    # plunger, clevis and pin - bone ozl_plunger (they go down in the work look)
    rod = P("plunger", "chrome", group=SEL_PLUNGER)
    z0, z1 = GLAND_Z1 - 0.004, CLV_Z0 + 0.001
    g.cyl(rod, (XP, YP, (z0 + z1) / 2), "z", ROD_R, z1 - z0, 12 if lod == 0 else 6, cap=False)
    parts.append(rod)
    ck = P("clevis", "steel", group=SEL_PLUNGER)
    g.box(ck, XP - CLV_W, XP + CLV_W, YP - CLV_Y1, YP + CLV_Y1, CLV_Z0, CLV_ZB, **bevel_kw(spec, 0.0006, 1))
    for s in (-1, 1):
        y0, y1 = sorted((YP + s * CLV_Y0, YP + s * CLV_Y1))
        sh.prism_bevel(ck, sh.round_top(XP, ZA, CLV_W, CLV_ZB - 0.001, 6 if lod == 0 else 3), (0, 2), y0, y1,
                       r=0.0004 if bev else 0.0)
    parts.append(ck)
    pa = P("pin_a", "chrome", group=SEL_PLUNGER)
    g.cyl(pa, (A.x, YP, A.z), "y", 0.0026, 2 * CLV_Y1 + 0.002, 10 if lod == 0 else 6, cap=lod != 0)
    if lod == 0:
        for s in (-1, 1):
            sh.pan_head(pa, sh.axis_frame((A.x, YP + s * CLV_Y1, A.z), "y" if s > 0 else "-y"), 0.0, 0.0036,
                        0.0013, 8, segs=2)
    parts.append(pa)
    # lever fork post: a lug on the collar and two cheeks with a rounded top around the axis F
    lg = P("fork_lug", "steel")
    x0, x1, lz0, lz1 = LUG
    g.box(lg, x0, x1, YP - POST_Y - POST_T, YP + POST_Y + POST_T, lz0, lz1, **bevel_kw(spec, 0.0008, 1))
    parts.append(lg)
    po = P("posts", "steel")
    for s in (-1, 1):
        y0, y1 = sorted((YP + s * POST_Y, YP + s * (POST_Y + POST_T)))
        sh.prism_bevel(po, sh.round_top(F.x, F.z, POST_W / 2, lz1 - 0.002, 6 if lod == 0 else 3), (0, 2), y0, y1,
                       r=0.0005 if bev else 0.0)
    parts.append(po)
    # lever axle: a pin with a head in front and a nut behind
    pn = P("pins", "chrome")
    yf = POST_Y + POST_T
    g.cyl(pn, (F.x, YP, F.z), "y", 0.0026, 2 * yf + 0.003, 10 if lod == 0 else 6, cap=lod != 0)
    if lod == 0:
        sh.pan_head(pn, sh.axis_frame((F.x, YP - yf, F.z), "-y"), 0.0, 0.0042, 0.0016, 10, segs=2)
        sh.nut(pn, sh.axis_frame((F.x, YP + yf, F.z), "y", 0.1), 0.0, 0.0030, 0.0075, ch_lo=False, cap_lo=False)
    parts.append(pn)
    # suction from the tank (a fitting on the tank wall, a copper tube, a pump fitting) and the
    # outlet to the manifold
    zs, zo = 0.034, 0.036
    out_d = Vector((MX - XP, MY - YP, 0.0)).normalized()
    p_out = Vector((XP, YP, zo)) + out_d * (PR - 0.001)
    port_in = Vector((MX, MY + MS / 2, zo))
    pl = P("pump_pipes", "pipe")
    if lod == 0:
        pp = P("pump_ports", "brass")
        sh.nut(pp, sh.axis_frame((TX1, YP, zs), "x", 0.2), 0.0, 0.0055, 0.0120, ch_lo=False, cap_lo=False)
        sh.nut(pp, sh.axis_frame((XP - PR + 0.0015, YP, zs), "-x", 0.2), 0.0, 0.0065, 0.0120, ch_lo=False,
               cap_lo=False)
        of = sh.axis_frame(p_out, out_d, 0.2)
        g.cyl(pp, (0.0, 0.0, 0.002), "z", 0.0055, 0.004, 10, cap=False, frame=of)
        sh.nut(pp, of, 0.004, 0.011, 0.0120, ch_lo=True, ch_hi=True)
        sh.nut(pp, sh.axis_frame(port_in, "y", 0.2), 0.0, 0.0060, 0.0120, ch_lo=False, cap_lo=False)
        parts.append(pp)
        g.pipe(pl, [(TX1 + 0.004, YP, zs), (XP - PR - 0.004, YP, zs)], 0.0040, 8)
        a, b = p_out + out_d * 0.010, port_in + Vector((0.0, 0.005, 0.0))
        g.pipe(pl, sh.smooth_path([a, a + out_d * 0.003, b + Vector((0.0, 0.003, 0.0)), b], 20.0, 0.006), 0.0040, 8)
    else:
        g.pipe(pl, [(TX1, YP, zs), (XP - PR + 0.001, YP, zs)], 0.0040, 6)
        g.pipe(pl, [tuple(p_out), tuple(port_in)], 0.0040, 6)
    parts.append(pl)
    return parts


def build_lever(spec):
    """Lever - bone ozl_work: a plate with a rounded end at the axis, a grip tube, a rubber handle with waists."""
    lod, bev = spec["lod"], spec["bev"]
    parts = []
    lv = P("lever_bar", "lever", group=SEL_LEVER)
    poly = sh.round_end(S_BAR[1], LEV_W / 2, S_BAR[0] + LEV_W / 2, 6 if lod == 0 else 3)
    sh.prism_bevel(lv, poly, (0, 1), -LEV_T / 2, LEV_T / 2, frame=LBAR, r=0.0009 if bev else 0.0)
    parts.append(lv)
    tb = P("lever_tube", "lever", group=SEL_LEVER)
    if lod == 0:
        sh.lathe(tb, LAX, [(0.0068, S_TUBE[0]), (TUBE_R, S_TUBE[0] + 0.0012), (TUBE_R, S_GRIP[0] + 0.002)], 12)
    else:
        g.cyl(tb, (0, 0, (S_TUBE[0] + S_GRIP[0]) / 2), "z", TUBE_R, S_GRIP[0] - S_TUBE[0], 6, frame=LAX)
    parts.append(tb)
    gr = P("grip", "grip", group=SEL_LEVER)
    s0, s1 = S_GRIP[0], S_END
    if lod == 0:
        prof = [(0.0072, s0), (0.0090, s0 + 0.0015), (0.0093, s0 + 0.0100), (0.0087, s0 + 0.0160),
                (0.0095, s0 + 0.0240), (0.0088, s0 + 0.0310), (0.0096, s0 + 0.0400), (0.0094, s1 - 0.0060),
                (0.0088, s1 - 0.0022), (0.0070, s1 - 0.0004), (0.0040, s1)]
    else:
        prof = [(0.0072, s0), (0.0092, s0 + 0.0020), (0.0095, s1 - 0.0050), (0.0080, s1 - 0.0010), (0.0045, s1)]
    sh.lathe(gr, LAX, prof, spec["grip"], cap_hi=True)
    parts.append(gr)
    return parts


# =============================================================================
# Manifold, valve, riser and gauge
# =============================================================================
def build_manifold(spec):
    lod, n, bev = spec["lod"], spec["sides"], spec["bev"]
    parts = []
    mf = P("manifold", "brass")
    g.box(mf, MX - MS / 2, MX + MS / 2, MY - MS / 2, MY + MS / 2, ZB, MZ1, **bevel_kw(spec, 0.0022))
    parts.append(mf)
    ft = P("fittings", "brass")
    # riser fitting, gauge seat (hexagon 22 from the elbow to the case), plug on the right
    sh.nut(ft, zf(MX, MY, MZ1, 0.25), 0.0, 0.0075, 0.0170, ch_lo=False, cap_lo=False, ch_hi=bev)
    y_back = YC - H_BACK
    sh.nut(ft, sh.axis_frame((MX, MY - 0.0095, GZ), "-y"), 0.0, (MY - 0.0095) - y_back, 0.0220, ch_lo=False,
           ch_hi=False, cap_lo=False, cap_hi=False)
    sh.nut(ft, sh.axis_frame((MX + MS / 2, MY, 0.034), "x", 0.3), 0.0, 0.0045, 0.0120, ch_lo=False, cap_lo=False,
           ch_hi=bev)
    if lod == 0:
        sh.nut(ft, zf(MX, MY, GZ - 0.0150, 0.25), 0.0, 0.0055, 0.0165)
    parts.append(ft)
    el = P("elbow", "brass")
    g.box(el, MX - 0.0095, MX + 0.0095, MY - 0.0095, MY + 0.0095, GZ - 0.0095, GZ + 0.0095, **bevel_kw(spec, 0.0030, 1))
    parts.append(el)
    sp = P("stand_pipe", "galv")
    z0, z1 = MZ1 + 0.006, GZ - 0.0095 + 0.001
    g.cyl(sp, (MX, MY, (z0 + z1) / 2), "z", STAND_R, z1 - z0, 12 if lod == 0 else 6, cap=False)
    parts.append(sp)
    if lod == 0:
        # two screws fixing the manifold to the plate: heads with a hex socket
        cs = P("manifold_screws", "bolt")
        dk = P("manifold_sockets", "dark")
        for sx, sy in ((-1, 1), (1, -1)):
            x, y = MX + sx * 0.0100, MY + sy * 0.0100
            sh.lathe(cs, zf(x, y, MZ1), [(0.0030, -0.0003), (0.0030, 0.0024), (0.0026, 0.0030)], 8, cap_hi=True)
            sh.disc(dk, zf(x, y, MZ1), 0.0013, 0.00305, 6)
        parts += [cs, dk]
    # valve: a hexagonal body, a bonnet, a gland nut, a spindle
    vl = P("valve", "brass")
    vf = sh.axis_frame((MX, VB[3], VZ), "-y", math.pi / 6)        # u = +x, v = +z; the body flat points left
    hb = 0.0095
    sh.nut(vl, vf, 0.0, hb, 0.0180, ch_lo=False, cap_lo=False, ch_hi=bev)
    if lod == 0:
        sh.lathe(vl, vf, [(0.0066, hb - 0.0005), (0.0072, hb + 0.0005), (0.0072, hb + 0.0060), (0.0064, hb + 0.0068)], 12)
        sh.nut(vl, vf, hb + 0.0068, hb + 0.0118, 0.0124)
    else:
        g.cyl(vl, (0, 0, hb + 0.0059), "z", 0.0072, 0.0118, 6, frame=vf)
    parts.append(vl)
    st = P("valve_stem", "chrome")
    h_w = VB[3] - WY                                              # handwheel plane from the manifold face
    g.cyl(st, (0, 0, (hb + 0.0118 + h_w) / 2), "z", 0.0025, h_w - hb - 0.0118, 8 if lod == 0 else 6, cap=False,
          frame=vf)
    parts.append(st)
    # handwheel: a rim, a hub, three spokes, a nut on the spindle
    wh = P("handwheel", "wheel")
    nmaj, nmin = spec["wheel"]
    sh.torus(wh, WF, WR, WRR, nmaj, nmin)
    if lod == 0:
        sh.lathe(wh, WF, [(0.0040, -0.0035), (0.0050, -0.0026), (0.0050, 0.0026), (0.0042, 0.0035)], 8, cap_hi=True)
        for k in range(3):
            a = math.radians(90 + 120 * k)
            d = WF.u * math.cos(a) + WF.v * math.sin(a)
            g.pipe(wh, [tuple(WF.o + d * 0.0042), tuple(WF.o + d * (WR - 0.0012))], 0.0016, 6)
        wn = P("wheel_nut", "chrome")
        sh.nut(wn, WF, 0.0035, 0.0060, 0.0055, ch_lo=False, cap_lo=False)
        parts.append(wn)
    else:
        g.cyl(wh, (MX, WY, VZ), "y", 0.0050, 0.007, 6)
        g.box(wh, -0.0016, 0.0016, -WR, WR, -0.0012, 0.0012, frame=WF)
    parts.append(wh)
    # union nut of the hose on the left of the valve body
    un = P("hose_union", "brass")
    sh.nut(un, sh.axis_frame((VB[0], (VB[2] + VB[3]) / 2 - 0.0005, HZ), "-x", 0.2), 0.0, 0.008, 0.0152, ch_lo=bev,
           ch_hi=bev, cap_lo=False)
    parts.append(un)
    return parts


def build_gauge(spec):
    lod, hs = spec["lod"], spec["gauge"]
    parts = []
    cs = P("gauge_case", "case")
    if lod == 0:
        prof = [(0.0440, H_BACK), (0.0485, H_BACK + 0.0015), (GR, H_BACK + 0.0055), (GR, H_CASE)]
    else:
        prof = [(0.0470, H_BACK), (GR, H_BACK + 0.0035), (GR, H_CASE)]
    sh.lathe(cs, GF, prof, hs, cap_lo=True)
    parts.append(cs)
    # bayonet ring: a rolled edge, a lip over the glass
    bz = P("gauge_bezel", "bezel")
    if lod == 0:
        prof = [(GR + 0.0004, H_CASE - 0.0030), (GR + 0.0016, H_CASE - 0.0018), (GR + 0.0016, H_BEZ - 0.0035),
                (GR + 0.0004, H_BEZ - 0.0002), (DIAL_R + 0.0016, H_BEZ - 0.0003), (DIAL_R + 0.0003, H_GLASS - 0.0006)]
    else:
        prof = [(GR + 0.0012, H_CASE - 0.002), (GR + 0.0012, H_BEZ - 0.0025), (DIAL_R + 0.0002, H_BEZ),
                (DIAL_R - 0.0003, H_GLASS - 0.0008)]
    sh.lathe(bz, GF, prof, hs)
    parts.append(bz)
    dl = P("dial", "dial")
    sh.disc(dl, GF, GR - 0.0003, H_DIAL, hs)
    parts.append(dl)
    if lod == 0:
        gl = P("gauge_glass", "glass", section="glass")
        sh.disc(gl, GF, DIAL_R + 0.0006, H_GLASS, hs)
        parts.append(gl)
    # needle - bone ozl_needle: at zero (225 degrees - down-left), a blade, a counterweight, an axle
    # cap
    nd = P("needle", "needle", group=SEL_NEEDLE)
    u = Vector((math.cos(A_ZERO), 0.0, math.sin(A_ZERO)))
    nf = g.Frame((GX, YC - H_NEEDLE[0], GZ), u, Vector((0, -1, 0)).cross(u), (0, -1, 0))
    t = H_NEEDLE[1] - H_NEEDLE[0]
    L = NEEDLE_L
    poly = [(-0.0072, -0.0011), (0.0, -0.0013), (L - 0.0032, -0.00045), (L, 0.0), (L - 0.0032, 0.00045),
            (0.0, 0.0013), (-0.0072, 0.0011)]
    g.prism(nd, poly, (0, 1), 0.0, t, frame=nf)
    if lod == 0:
        # the counterweight is thicker than the blade by 0.3 mm: the faces are not coplanar
        g.cyl(nd, tuple(nf.p(-0.0088, 0.0, t / 2)), "y", 0.0028, t + 0.0003, 12)
        sh.lathe(nd, sh.axis_frame((GX, YC - H_NEEDLE[1] + 0.0004, GZ), "-y"),
                 [(0.0032, 0.0), (0.0030, 0.0007), (0.0019, 0.0013)], 12, cap_hi=True)
    else:
        g.cyl(nd, (GX, YC - H_NEEDLE[1] - 0.0004, GZ), "y", 0.0028, 0.0012, 6)
    parts.append(nd)
    if lod == 0:
        # verification seal: an ear on the ring, two wire cores down to the lead seal
        ea = P("seal_ear", "bezel")
        ef = g.Frame(GF.p(0.012, -(GR + 0.0016), H_CASE + 0.0030), (1, 0, 0), (0, 0, 1), (0, -1, 0))
        g.box(ea, -0.0016, 0.0016, -0.0026, 0.0004, -0.0010, 0.0010, frame=ef)
        parts.append(ea)
        ear = ef.p(0.0, -0.0018, 0.0)
        sl = Vector((GX + 0.0150, YC - 0.0195, GZ - GR - 0.0120))
        wr = P("seal_wire", "steel")
        for dx in (-0.0007, 0.0007):
            e = ear + Vector((dx, 0.0, 0.0))
            pts = [e, e + Vector((0.0004 + dx, -0.0006, -0.0030)), sl + Vector((dx * 1.4, 0.0, 0.0065)),
                   sl + Vector((dx * 0.8, 0.0, 0.0035))]
            g.pipe(wr, sh.smooth_path(pts, 22.0, 0.006), 0.00045, 4)
        parts.append(wr)
        ld = P("seal", "lead")
        sf = sh.axis_frame(sl + Vector((0.0, 0.0016, 0.0)), "-y")
        sh.lathe(ld, sf, [(0.0040, 0.0), (0.0043, 0.0008), (0.0043, 0.0024), (0.0036, 0.0032)], 12, cap_lo=True,
                 cap_hi=True)
        parts.append(ld)
    return parts


# =============================================================================
# Hose with a nozzle
# =============================================================================
def build_hose(spec):
    lod = spec["lod"]
    parts = []
    fe = P("hose_ferrules", "steel")
    # crimped ferrule on the valve fitting: three crimps, the hose comes out of the end
    x1 = VB[0] - 0.008
    ln = x1 - FER_X
    ff = sh.axis_frame((x1, HOSE_Y0, HZ), "-x")
    # ferrule ends on the hose side are closed by a ring into the hose - no gap between them
    if lod == 0:
        prof = [(0.0062, 0.0), (0.0078, 0.0008), (0.0078, 0.0040), (0.0072, 0.0050), (0.0078, 0.0060),
                (0.0078, ln - 0.0012), (0.0070, ln), (0.0058, ln + 0.0002)]
        sh.lathe(fe, ff, prof, 10)
    else:
        g.cyl(fe, (0, 0, ln / 2), "z", 0.0078, ln, 8, frame=ff)
    hs = P("hose", "hose")
    g.pipe(hs, hose_path(*spec["hose_step"]), HOSE_R, spec["hose"])
    parts.append(hs)
    # nozzle: a crimped ferrule, a union nut (flat on the plate), a nipple cone
    nf = g.Frame(NOZ_E, Vector((0, 0, 1)).cross(NOZ_DIR), (0, 0, 1), NOZ_DIR)
    if lod == 0:
        prof = [(0.0058, -0.0002), (0.0070, 0.0), (0.0078, 0.0012), (0.0078, 0.0070), (0.0072, 0.0080),
                (0.0078, 0.0090), (0.0078, 0.0172), (0.0064, 0.0182)]
        sh.lathe(fe, nf, prof, 10)
    else:
        g.cyl(fe, (0, 0, 0.009), "z", 0.0078, 0.018, 8, frame=nf)
    parts.append(fe)
    nz = P("nozzle", "brass")
    if lod == 0:
        sh.nut(nz, nf, 0.0180, 0.0280, NOZ_NUT)
        sh.lathe(nz, nf, [(0.0058, 0.0275), (0.0058, 0.0330), (0.0052, 0.0342), (0.0040, 0.0398), (0.0030, 0.0405)],
                 10, cap_hi=True)
    else:
        sh.nut(nz, nf, 0.0180, 0.0280, NOZ_NUT, ch_lo=False, ch_hi=False)
        g.cyl(nz, (0, 0, 0.034), "z", 0.0056, 0.012, 8, r2=0.0040, frame=nf)
    parts.append(nz)
    return parts


def build_lod(spec):
    parts = (build_base(spec) + build_tank(spec) + build_pump(spec) + build_lever(spec) + build_manifold(spec) +
             build_gauge(spec) + build_hose(spec))
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("bounds", BOUNDS)
        # work pose check: the handle at the bottom of the stroke, the plunger down, the pin stays
        # on the lever axis
        m = ON["move"][SEL_LEVER]
        tip = m @ (F + D * S_END)
        pin = Vector((XP, YP, ZA - PLUNGER_STROKE))
        off = ((m @ (F + D * 0.028)) - F).normalized().cross(pin - F).y
        print("work pose: grip end (%.4f, %.4f, %.4f), plunger stroke %.4f, clevis bottom %.4f over gland %.4f, "
              "pin off lever axis %.5f" % (tip.x, tip.y, tip.z, PLUNGER_STROKE, CLV_Z0 - PLUNGER_STROKE, GLAND_Z1, off))
    return parts


def ring_pts(center, axis_u, axis_v, r, k=8):
    return [tuple(center + axis_u * (r * math.cos(2 * math.pi * (i + 0.5) / k)) +
                  axis_v * (r * math.sin(2 * math.pi * (i + 0.5) / k))) for i in range(k)]


def collision():
    """Four convex parts: the base, the tank with the plug, the gauge with the riser and manifold, the
    pump with the lever; the hose has no collision (as in M45, M73). Mass is the item's weight in the
    mod, 0.8 kg.
    """
    X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    base = kx.box_pts(BX0, BX1, BY0, BY1, 0.0, ZB)
    tank = kx.box_pts(TX0 - 0.002, TX1 + 0.002, TY0 - 0.002, TY1 + 0.002, ZB, TZ1 + 0.0175)
    gauge = ring_pts(Vector((GX, YC - H_BEZ, GZ)), X, Z, GR + 0.0016) + ring_pts(Vector((GX, YC - H_BACK, GZ)), X, Z, GR)
    gauge += kx.box_pts(MX - MS / 2, MX + MS / 2, MY - MS / 2, MY + MS / 2, ZB, MZ1)
    gauge += kx.box_pts(MX - WR - WRR, MX + WR + WRR, WY - 0.0035, VB[3], VZ - WR - WRR, VZ + WR + WRR)
    pump = ring_pts(Vector((XP, YP, ZB)), X, Y, PF_R)
    pump += ring_pts(Vector((XP, YP, GLAND_Z1)), X, Y, PR + 0.002)
    for s, r in ((S_BAR[0], LEV_W / 2), (S_END, GRIP_R)):
        c = F + D * s
        pump += ring_pts(c, Y, VL, r, 6)
    comps = [(c, kx.PEN + r"\metalplate.rvmat") for c in (base, tank, gauge, pump)]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    memory = {
        # inventory preview camera: front-left and from above (invView = camera position)
        "invView": [(-0.26, -0.46, 0.40)],
        "ce_center": [(0.0, 0.0, 0.12)],
        "ce_radius": [(0.16, 0.0, 0.12)],
        # bone axes: the lever - through the axis F toward the face, the plunger - a metre down, the
        # needle - from the dial toward the face
        "ozl_work_axis": [(F.x, YP + 0.013, F.z), (F.x, YP - 0.013, F.z)],
        "ozl_plunger_axis": [(XP, YP, ZA), (XP, YP, ZA - 1.0)],
        "ozl_needle_axis": [(GX, YC - H_NEEDLE[0], GZ), (GX, YC - H_NEEDLE[0] - 0.05, GZ)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


# the first four are the --look preview (M.look_shots), the first three are also the work look
SHOTS = [
    ("front", (-0.20, -0.56, 0.30), (0.0, -0.01, 0.115), 40),
    ("gauge", (0.0, -0.30, 0.20), (0.044, -0.05, 0.150), 50),
    ("pump", (0.34, 0.30, 0.32), (0.02, 0.03, 0.12), 42),
    ("hose", (-0.22, -0.38, 0.20), (-0.03, -0.06, 0.04), 45),
    ("left", (-0.46, -0.24, 0.26), (-0.02, 0.0, 0.11), 42),
    ("top", (0.05, -0.25, 0.58), (0.0, 0.0, 0.10), 40),
    ("back", (-0.30, 0.48, 0.28), (0.0, 0.02, 0.11), 40),
]

M.run(build_lod, collision, SHOTS, row_step=0.32, row_shot=((0.16, -1.1, 0.35), (0.16, 0, 0.11)))
