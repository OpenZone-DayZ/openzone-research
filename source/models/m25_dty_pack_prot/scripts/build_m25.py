"""M25 - washing tub: Protection Packer of Duty (OZL_Dty_Pack_Prot).
A packer: 10x10 cargo, three module slots (module_1..3) and module proxies in the same places. Each
module of the "Protection" line has its own slot and its own place where it is worked with: slot 1 -
the pressure tester M84 on the lower shelf under the tank, its hose goes to the gas mask on the dryer;
slot 2 - the gas analyzer M85 on the closed half of the lid (on a rubber mat); slot 3 - the plate
clamp M86 there too, on a plywood board.

    blender --background --python build_m25.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

The prop is an industrial parts washer Graymills PL422-A (1986): 1067 x 965 x 559 mm (L x H x D) with
the lid closed, 1524 mm high with it open, working tank 1067 x 559 x 508 mm, 40 gallons, pump
400 gal/h. The tank follows the datasheet: 1.067 x 0.559, the rim at 0.95, the lid at 0.965, the tank
depth 0.508; four legs tapering downward, as in the photo. The target size 1.4 x 1.1 x 0.7 m is
reconciled like this: the length with the pump on the right and the drain hose on the left is ~1.48,
the depth with the lid handles and the raised half ~0.70; the height of 1.1 is without the raised
lid, and by the datasheet a raised lid gives 1.524, so the dryer grille above the tank sits below it,
the top of the grille at 1.47, the top of the raised half with its handle ~1.58.

Detail:
- the "dayz" look: matte, dirtier, bare metal and galvanizing darker;
- the tank is bent sheet: rounded corners (R 14), a rounded bottom, the rim rolled outward into a
  bead, the inside with wall thickness; legs with chamfers on adjustable heels (a stud, a nut, a
  rubber pad); a shelf with a flange on angles to the legs; lids with rounded edges, a turned-under
  skirt edge, bent bar handles and hinges (a sheet, a pivot, a sheet on the tank); the raised half
  is held by a strap prop on a bracket;
- the pump is a motor with cooling fins, a fan shroud with a grille and the impeller behind it (it
  spins when "working"), a volute at the back, the inlet into the tank through the wall with a
  locknut, a terminal box with a cover on screws, a lamp and a toggle, a cable through a gland to the
  floor with a plug; a riser with a coupling, a valve with a handwheel, a clamp to the tank, a bent
  outlet with a spout; the drain - a locknut, a ball valve with a lever and a seal, a fitting with a
  worm clamp, a smooth-curve hose into a floor drain with a grille;
- the dryer: posts and crossbars of profile tube, welded mesh, S-hooks, two pegs holding the vanilla
  SSh-68 helmet and GP-5 gas mask (proxies) - they dry above the open half;
- small DayZ items as proxies (kvanilla): GP-5, SSh-68, a GP-5 filter on the lid and a spare one on
  the shelf, rags, an adjustable wrench, a screwdriver, NBC gloves and tape on the shelf; the own
  item is a brush on the grille tray.
The M84 hose: dia. 13, like the module itself; at the mask end an adapter instead of the filter (on the
valve box thread) with a clamp, at the module end a coupling on the cone of the M84 tip (its point
and direction are from build_m84.py: the tip lies by the valve, the axis is (0.92; 0.39)). Without
the module the coupling lies on the hose over the mat.
Where the GP-5 valve box is: the ground model GP5GasMask_g lies (its +Z is up from the ground), and
the worn one, GP5GasMask_m, stands (+Y is up, the face is at -Z); both have a filter slot proxy. The
rotation of the ground model into the worn one is computed from the two positions of this proxy
(their matrices are in the LOD header, like the kvanilla extent; the vanilla geometry is not read) -
the GP-5 stands upright facing the person, and the hose goes exactly into its valve box.

Props and sizes:
- the steel SSh-68 helmet (~280 x 270 x 170) and the GP-5 gas mask are vanilla DayZ models, we set no
  sizes of our own;
- a parts-washing brush ~0.30 m: a 120 x 44 block, a handle with a thickening, bristle tufts.

Duty look (as in M23): the stainless/galvanized tank in its own color; the pump, the bracket and the
dryer frame are black with red (no olive); worn by frequent use - paint worn down to metal on the
edges and at the handles, on the galvanizing the rim edges and the lid handles are rubbed; no rust.
No readable lettering: a blank nameplate on the tank face, a seal on the drain valve, red stencil
stripes on the bracket.

Working look: ozl_lamp is the pump lamp (lit when "working", _on atlas); the impeller is the bone
ozl_work on the source ozl_work: a model.cfg loop (sourceAddress loop, maxValue 1/4) - 4 turns per
2 s pass, 2 rev/s: the five blades advance by 24 degrees per frame at 30 fps, so the rotation does not
appear to go backward; the stream from the spout into the tank is the bone ozl_flow on the source
ozl_flow (OZL_WorkFx pose, 0.35 s): at rest the stream with splashes is sunk under the solvent mirror
(not visible from outside), when "working" it rises to the spout.

Blender axes: X is width, Y is depth (the face looks to -Y), Z is up.
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
import krender  # noqa: E402
import kvanilla as kv  # noqa: E402
import kwood  # noqa: E402
import m25_geo as G  # noqa: E402
import m25_mats as MT  # noqa: E402

# =============================================================================
# Dimensions, m
# =============================================================================
TX, TY = 1.067 / 2, 0.559 / 2               # tank outside (datasheet)
Z_RIM = 0.950                                # top of the rim
Z_LID = 0.965                                # top of the lid (datasheet: 965 closed)
Z_BOT = Z_RIM - 0.508 - 0.006                # bottom of the tank (depth 508 + bottom)
WALL = 0.006
RC = 0.014                                   # bend radius of the tank corners
Z_SOLV = 0.78                                # solvent mirror
# rim: the sheet leaves the wall, is rolled outward into a bead and goes into the inside (dn - outward
# from the wall, z - from the top of the rim; the traversal is counterclockwise around the metal,
# m25_geo.sweep_ring)
RIM_PROF = [(0.0, -0.016), (0.004, -0.0185), (0.009, -0.0185), (0.013, -0.016), (0.0155, -0.011),
            (0.0155, -0.006), (0.0135, -0.0015), (0.009, 0.0), (-WALL, 0.0), (-WALL, -0.004)]
RIM_PROF1 = [(0.0, -0.016), (0.0155, -0.016), (0.0155, 0.0), (-WALL, 0.0), (-WALL, -0.004)]
# embossed stiffening ribs around the tank (the height of the middle); the nameplate is between them
BEADS = (0.63, 0.83)
PLATE = (-0.36, -0.20, 0.665, 0.755)
# legs: a square tube with chamfers, tapering downward and splayed slightly outward; the heels are adjustable
LEG_TOP, LEG_BOT, LEG_SPLAY = 0.045, 0.030, 0.025
LEG_X, LEG_Y = TX - 0.045, TY - 0.045
Z_FOOT = 0.028                               # bottom of the leg (a plate), below it a stud, a nut, a pad
# shelf under the tank
Z_SH, SH_T = 0.140, 0.003
SH_X, SH_Y = 0.465, 0.212
MAT_T = 0.004
# lid: hinges at the back
LY0, LY1 = -TY - 0.018, TY + 0.004
YH, ZH = TY + 0.008, Z_LID - 0.003
LID_OPEN = -100.0                            # degrees about x: past the vertical, backward
# pump on the right on a bracket: the motor axis along y, the impeller in front, the volute behind
PX, PZ = TX + 0.11, 0.62
MY0, MY1, MR = -0.100, 0.070, 0.065           # motor body along y, radius
GUARD_Y1 = MY0 - 0.052                        # front of the fan shroud
FAN_Y = MY0 - 0.033                           # impeller
VOL_Y0, VOL_Y1, VOL_R = 0.072, 0.124, 0.070   # volute
Z_BR = 0.53                                   # top of the bracket
PIPE_R = 0.0107                               # 1/2" pipe
RISER = (PX + 0.02, (VOL_Y0 + VOL_Y1) / 2)    # riser from the volute outlet
FAUCET_Z, VALVE_Z = 1.05, 0.86
FX, FY = 0.22, RISER[1]                       # outlet spout above the tank (between the tray bars)
NOZZLE_Z = 0.975
# stream: when "working" from the spout under the mirror, at rest lowered by FLOW_L and entirely under the mirror
FLOW_TOP, FLOW_BOT = NOZZLE_Z + 0.002, Z_SOLV - 0.004
FLOW_L = FLOW_TOP - Z_SOLV + 0.006
FAN_TURNS = 4                                 # impeller turns per loop pass (2 s)
# grille tray in the tank under the open half
Z_TRAY = Z_RIM - 0.03
TRAY_TOP = Z_TRAY + 0.0045
# dryer grille
RX, RY = TX + 0.040, 0.17                    # posts
RZ0, RZ1 = 1.10, 1.46                        # bottom and top of the grille
POST_Z0 = 0.68
HOOKS = (-0.36, -0.12)                       # S-hooks on the top crossbar (free)
# helmet on a peg: the middle of the extent and the bottom (kv.put)
HELM = (0.10, 0.0, 1.115)
# drain: a pipe on the left end, a trap in the floor
DRAIN = (-TX, 0.10, 0.475)
TRAP = (-0.66, -0.12)

# module places: slot 1 - the shelf under the tank, 2 and 3 - the closed half of the lid
S1 = (0.27, -0.03, Z_SH + SH_T + MAT_T)
S2 = (-0.40, -0.07, Z_LID + MAT_T)
S3 = (-0.16, -0.10, Z_LID + 0.012)
MODS = [S1, S2, S3]
MOD_OBJ = [("m84_test_pump", "ozr_test_pump"), ("m85_gas_analyzer", "ozr_gas_analyzer"),
           ("m86_plate_clamp", "ozr_plate_clamp")]
# M84 hose tip (build_m84.py: HOSE[-1], NOZ_Z, NOZ_DIR; the cone ends at 0.040 along the axis)
M84_NOZ = Vector((0.010, -0.0785, 0.0297))
M84_DIR = Vector((0.92, 0.39, 0.0)).normalized()
HOSE_R = 0.0065

LOD_SPECS = [
    dict(lod=0, sides=16),
    dict(lod=1, sides=8),
    dict(lod=2, sides=6),
]

REGIONS = {
    "galv": ("galv", 0.7), "galv_lid": ("galv_lid", 0.8), "galv_shelf": ("galv_shelf", 0.8),
    "solvent": ("solvent", 0.4), "stream": ("stream", 2.0), "foam": ("foam", 2.0),
    "steel": ("steel", 1.2), "chrome": ("chrome", 1.6), "zinc": ("zinc", 1.6), "alu": ("alu", 1.6),
    "rubber": ("rubber", 0.8), "mat": ("mat", 1.0), "ply": ("ply", 1.2),
    "hose": ("hose", 1.2), "hose_hp": ("hose_hp", 1.4), "cable": ("cable", 1.4),
    "paint_black": ("paint_black", 1.2), "paint_red": ("paint_red", 1.2), "guard": ("guard", 1.4),
    "fan": ("fan", 1.6), "rack": ("rack", 1.0), "rack_red": ("rack_red", 1.0), "brass": ("brass", 1.6),
    "lamp": ("lamp_off", 2.0), "wood": ("wood", 1.6), "bristle": ("bristle", 1.6), "grate": ("grate", 0.8),
    "castiron": ("castiron", 1.0), "lead": ("lead", 2.0), "plate": ("plate", 2.0), "black": ("black", 1.8),
}

# =============================================================================
# Materials
# =============================================================================
BLACK = kmats.lin((30, 30, 32))
RED = kmats.lin((140, 24, 20))
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# rim and lid handles - by hands; the tank face by the nameplate - cleaner
LID_RUB = [((-TX / 2, LY0 - 0.02, Z_LID), (0.12, 0.05, 0.05), 0.5), ((TX / 2, LY0 - 0.02, Z_LID), (0.12, 0.05, 0.05), 0.5)]
TANK_RUB = [((0.0, -TY, Z_RIM - 0.01), (1.2, 0.03, 0.03), 0.35), ((TX, 0.0, Z_RIM - 0.01), (0.03, 0.6, 0.03), 0.3),
            ((-TX, 0.0, Z_RIM - 0.01), (0.03, 0.6, 0.03), 0.3)]
# stencil stripes on the front flange of the pump bracket
BR_STRIPES = [((TX + 0.005, TX + 0.215, -0.175, -0.160, Z_BR - 0.050, Z_BR - 0.040), RED),
              ((TX + 0.005, TX + 0.215, -0.175, -0.160, Z_BR - 0.030, Z_BR - 0.020), RED)]
PUMP = dict(color=BLACK, seed=2.1, wear=(0.67, 0.72), edge_k=0.75, scratch=0.3, oil=0.3, floor_z=0.0, dust=0.15,
            grime=0.3)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    # the tank hangs at 0.44 m: the "near the floor" grime is counted from the tank bottom, otherwise it does not reach it
    "galv": (MT.build_galv, dict(seed=1.3, rub=TANK_RUB, stain=0.55, floor_z=Z_BOT - 0.08, dust=0.15, grime=0.5)),
    "galv_lid": (MT.build_galv, dict(seed=1.9, tone=0.35, rub=LID_RUB, stain=0.2, floor_z=Z_RIM, dust=0.25,
                                     grime=0.15)),
    "galv_shelf": (MT.build_galv, dict(seed=2.7, tone=0.31, edge_k=0.6, floor_z=0.0, dust=0.35, grime=0.4)),
    # solvent: dark, amber, with an oil film; the stream is lighter against the light
    "solvent": (MT.build_solvent, dict(color=kmats.lin((46, 36, 20)))),
    "stream": ("flat", dict(color=kmats.lin((150, 112, 52)), gloss=0.95, spec=0.85)),
    "foam": ("plastic", dict(color=kmats.lin((190, 178, 146)), gloss=0.5, spec=0.3, mottle=0.2, dust=0.0, grime=0.0)),
    "chrome": ("steel", dict(seed=5.3, tone=0.40, along="y", gloss=0.7, spec=0.8, dust=0.1, grime=0.2)),
    "zinc": ("steel", dict(seed=5.9, tone=0.30, along="z", gloss=0.45, spec=0.5, dust=0.15, grime=0.4)),
    "alu": ("steel", dict(seed=6.7, tone=0.42, along="z", gloss=0.5, spec=0.55, dust=0.1, grime=0.3)),
    "mat": ("plastic", dict(color=kmats.lin((30, 30, 30)), gloss=0.12, spec=0.06, mottle=0.12, dust=0.3, grime=0.5,
                            scuff=(0.66, 0.74))),
    "ply": (kwood.build_wood, dict(color=kmats.lin((168, 132, 92)), seed=9.1, along="x", floor_z=Z_LID, dust=0.2,
                                   grime=0.6, knots=0.3)),
    "hose": ("plastic", dict(color=kmats.lin((22, 22, 22)), gloss=0.25, spec=0.15, dust=0.25, grime=0.5,
                             scuff=(0.8, 0.9))),
    "hose_hp": ("plastic", dict(color=kmats.lin((26, 26, 27)), gloss=0.35, spec=0.2, dust=0.1, grime=0.3,
                                scuff=(0.75, 0.85))),
    "cable": ("plastic", dict(color=kmats.lin((20, 20, 21)), gloss=0.3, spec=0.2, dust=0.3, grime=0.4)),
    "paint_black": (MT.build_worn, dict(PUMP, stripes=BR_STRIPES)),
    "paint_red": (MT.build_worn, dict(PUMP, color=RED, seed=2.9, bare=kmats.lin((120, 118, 116)))),
    "guard": (MT.build_worn, dict(PUMP, seed=3.1, edge_k=0.9, oil=0.0)),
    "fan": ("plastic", dict(color=kmats.lin((24, 24, 25)), gloss=0.3, spec=0.2, dust=0.4, grime=0.5)),
    "rack": (MT.build_worn, dict(PUMP, seed=3.7, wear=(0.68, 0.73), oil=0.0, floor_z=Z_RIM, dust=0.2, grime=0.1)),
    "rack_red": (MT.build_worn, dict(PUMP, color=RED, seed=4.4, wear=(0.68, 0.73), oil=0.0, floor_z=Z_RIM,
                                     dust=0.2, grime=0.1)),
    "brass": ("paint", dict(CLEAN, color=kmats.lin((156, 128, 70)), gloss=0.55, spec=0.55, dust=0.1, grime=0.3)),
    "lamp_off": ("flat", dict(color=kmats.lin((90, 18, 14)), gloss=0.85, spec=0.8)),
    "lamp_on": ("flat", dict(color=kmats.lin((255, 60, 40)), gloss=0.85, spec=0.8)),
    "wood": (kwood.build_wood, dict(color=kmats.lin((150, 102, 62)), seed=7.9, along="x", floor_z=Z_RIM, dust=0.1,
                                    grime=0.6, knots=0.2)),
    "bristle": ("plastic", dict(color=kmats.lin((150, 118, 70)), gloss=0.1, spec=0.05, mottle=0.3, dust=0.0,
                                grime=0.6, scuff=(0.9, 1.0))),
    "grate": ("steel", dict(seed=8.3, tone=0.28, along="x", floor_z=0.0, dust=0.1, grime=0.6)),
    # floor drain: cast iron, dark paint worn off, grime
    "castiron": ("paint", dict(color=kmats.lin((44, 44, 42)), under=kmats.lin((70, 66, 60)), seed=8.7, gloss=0.25,
                               spec=0.2, chip=(0.62, 0.70), rust=(0.80, 0.88), rust_low=0.2, floor_z=0.0, dust=0.5,
                               grime=0.9)),
    "lead": ("plastic", dict(color=kmats.lin((96, 98, 102)), gloss=0.3, spec=0.3, dust=0.1)),
    "plate": ("steel", dict(seed=8.9, tone=0.36, along="x", gloss=0.5, spec=0.6, dust=0.1, grime=0.2)),
})

OBJ, NAME = "m25_dty_pack_prot", "ozr_dty_pack_prot"


# =============================================================================
# GP-5 upright (a vanilla proxy): the rotation is from the filter slot proxy in the two models
# =============================================================================
# rows are the X, Y, Z axes of the filter in mask axes, then the origin (from the near LOD header, like kvanilla.box)
F_G = ((0.60700, -0.79373, -0.03939), (0.78902, 0.60783, -0.08935), (0.09486, 0.02316, 0.99522),
       (-0.24272, -0.11198, 0.05723))                                # GP5GasMask_g (lying)
F_M = ((1.0, 0.0, 0.0), (0.0, 0.88373, 0.46799), (0.0, -0.46799, 0.88373), (-0.0001, 1.47915, -0.21021))   # GP5GasMask_m (worn)
GP5_M_BOX = ((-0.099, 1.409, -0.210), (0.099, 1.804, 0.1015))       # extent of the worn one (LOD header)
FILTER_H = 0.0799                            # GP5GasMask_filter: from the bottom (origin) to the neck along +Y
# filter neck (the valve box thread) - the hose adapter goes here
GP5_NECK = (0.40, -0.13, 1.255)


def _n(v):
    """Axes of the worn model -> Blender for an upright mask facing -Y: +X -> +X, +Y (up) -> +Z, +Z (back
    of the head) -> +Y."""
    return Vector((v[0], v[2], v[1]))


def gp5_pose(neck_blender):
    """Origin, "up" and "forward" of the proxy of the ground model (kexport.proxy_points), so that the mask
    stands like the worn one facing the person and the filter neck lands at neck_blender; and the
    function of a point of the worn model -> Blender."""
    ag, am = [Vector(v) for v in F_G[:3]], [Vector(v) for v in F_M[:3]]
    R = Matrix(((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)))
    for vg, vm in zip(ag, am):                   # rotation worn -> ground: the sum of vg * vm^T
        for i in range(3):
            for j in range(3):
                R[i][j] += vg[i] * vm[j]
    t = Vector(F_G[3]) - R @ Vector(F_M[3])
    pm0 = -(R.transposed() @ t)                  # origin of the ground model in worn axes
    up, fwd = _n(R[1]), _n(R[2])                 # axes +Y and +Z of the ground model in Blender
    neck_m = Vector(F_M[3]) + Vector(F_M[1]) * FILTER_H
    origin = Vector(neck_blender) - _n(neck_m - pm0)

    def at(p_m):
        return origin + _n(Vector(p_m) - pm0)
    return dict(origin=origin, up=up, fwd=fwd, at=at, neck=at(neck_m), axis=_n(-Vector(F_M[1])))


GP5 = gp5_pose(GP5_NECK)
GP5_LO = GP5["at"](GP5_M_BOX[0])
GP5_HI = GP5["at"](GP5_M_BOX[1])
GP5_TIP = GP5["at"]((0.0, 1.745, -0.035))     # the peg rests against the crown from inside

# Working look: the pump lamp is ozl_lamp (in hiddenSelections); the impeller and the stream are bones
SEL_LAMP, SEL_FAN, SEL_FLOW = "ozl_lamp", "ozl_work", "ozl_flow"
ON = dict(remap={"lamp_off": "lamp_on"}, emissive=(1.0, 1.0, 1.0, 1.0), move={SEL_FLOW: (0.0, 0.0, FLOW_L)})
FAN_ANIM = ("ozl_work_fan", dict(type="rotation", source="ozl_work", sourceAddress="loop", selection=SEL_FAN,
                                 axis="ozl_work_axis", memory=1, minValue=0.0, maxValue=1.0 / FAN_TURNS, angle0=0.0,
                                 angle1=2 * math.pi))
# stream axis - one meter up: offset in meters
FLOW_ANIM = ("ozl_flow_up", dict(type="translation", source="ozl_flow", selection=SEL_FLOW, axis="ozl_flow_axis",
                                 memory=1, minValue=0.0, maxValue=1.0, offset0=0.0, offset1=FLOW_L))
# module proxies: the slots OZL_Tool1..3 are linked to them by CfgNonAIVehicles of the mod (Proxyozl_tool1..3);
# slot N is module N of the "Protection" line (M84, M85, M86), without rotation: the modules face the person
PROXIES = [(r"\OpenZone_Research\models\proxies\ozl_tool%d" % (i + 1), m) for i, m in enumerate(MODS)]
GLOVES = r"dz\characters\gloves\NBC_Gloves_g"
DECOR = [
    # on the dryer: the gas mask upright on a peg (pose - gp5_pose), the helmet on a peg
    (kv.path("gp5"), tuple(GP5["origin"]), tuple(GP5["up"]), tuple(GP5["fwd"]), (0, 1), "gp5"),
    kv.put("ssh68", HELM, up=(1, 0, 0), fwd=(0, 0, 1)),
    # on the lid: a filter unscrewed from the gas mask, rags, an adjustable wrench and a screwdriver at the edge
    kv.put("gp5filter", (-0.48, 0.19, Z_LID), up=(0, 0, 1), fwd=(0, -1, 0)),
    kv.put("rags", (-0.20, 0.165, Z_LID), **kv.flat(0)),
    kv.put("wrench", (-0.40, -0.245, Z_LID), **kv.flat(180)),
    kv.put("screwdriver", (-0.17, -0.25, Z_LID), **kv.flat(5)),
    # on the shelf left of M84: NBC gloves, a spare filter, tape
    kv.put(GLOVES, (-0.25, 0.02, Z_SH + SH_T), up=(0, 0, 1), fwd=(1, 0, 0)),
    kv.put("gp5filter", (0.06, 0.12, Z_SH + SH_T), up=(0, 0, 1), fwd=(0.3, -1, 0)),
    kv.put("ducttape", (0.05, -0.09, Z_SH + SH_T), **kv.flat(0)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 selections=(SEL_LAMP, SEL_FAN, SEL_FLOW), hidden=(SEL_LAMP,), states={"on": ON},
                 bones=((SEL_FAN, ""), (SEL_FLOW, "")), animations=(FAN_ANIM, FLOW_ANIM), proxies=PROXIES,
                 decor=DECOR, modules=[(o, n, m) for (o, n), m in zip(MOD_OBJ, MODS)],
                 sources={"ozl_work": dict(animPeriod=2.0), "ozl_flow": dict(animPeriod=0.35)})
P = M.part
BOUNDS = {}


def gp5_standin():
    """The blue GP-5 box in the preview is the extent of the upright mask (the worn model's header), not
    the rotated extent of the ground one: that one still has the filter proxy point, and the box would
    come out skewed and twice as big."""
    import bmesh
    import bpy
    bm = bmesh.new()
    for v in bmesh.ops.create_cube(bm, size=1.0)["verts"]:
        v.co = Vector(tuple(GP5_LO[i] + (v.co[i] + 0.5) * (GP5_HI[i] - GP5_LO[i]) for i in range(3)))
    me = bpy.data.meshes.new("standin_gp5")
    bm.to_mesh(me)
    bm.free()
    m = bpy.data.materials.get("vanilla_standin")
    if m is not None:
        me.materials.append(m)
    bpy.context.scene.collection.objects.link(bpy.data.objects.new(me.name, me))


def place_extras(with_modules=True):
    """Preview: like kmodel.Model.place_extras (blue boxes of vanilla items, modules in slots), but the
    GP-5 is the gp5_standin box."""
    krender.standins([d for d in M.lod0_decor() if d[5] != "gp5"])
    gp5_standin()
    for obj, name, at in M.modules if with_modules else ():
        krender.our_model(obj, name, at)


M.place_extras = place_extras


def rot_lid(v):
    """Rotation of a point of the raised lid half about the hinge axis."""
    m = Matrix.Translation((0, YH, ZH)) @ Matrix.Rotation(math.radians(LID_OPEN), 4, "X") @ \
        Matrix.Translation((0, -YH, -ZH))
    return m @ Vector(v)


def rotate_part(part):
    for v in part.bm.verts:
        v.co = rot_lid(v.co)
    part.bm.normal_update()


def chamfer_sq(c, h, ch):
    """Square of half-width h centered at c with a chamfer ch on the corners (a leg section)."""
    x, y = c
    if ch <= 0:
        return [(x - h, y - h), (x + h, y - h), (x + h, y + h), (x - h, y + h)]
    return [(x - h + ch, y - h), (x + h - ch, y - h), (x + h, y - h + ch), (x + h, y + h - ch),
            (x + h - ch, y + h), (x - h + ch, y + h), (x - h, y + h - ch), (x - h, y - h + ch)]


def leg_at(sx, sy, z):
    """Center and half-width of a leg at height z."""
    t = (z - Z_FOOT) / (Z_BOT - Z_FOOT)
    return (sx * (LEG_X + LEG_SPLAY * (1 - t)), sy * (LEG_Y + LEG_SPLAY * (1 - t))), LEG_BOT + (LEG_TOP - LEG_BOT) * t


# =============================================================================
# Tank, legs, shelf
# =============================================================================
def build_tank(spec):
    lod = spec["lod"]
    tk = P("tank", "galv")
    if lod == 2:
        g.box(tk, -TX, TX, -TY, TY, Z_BOT, Z_RIM)
        return [tk]
    nc = 3 if lod == 0 else 1
    G.slab(tk, -TX, TX, -TY, TY, Z_BOT, Z_RIM - 0.016, rc=RC, nc=nc, rb=0.008 if lod == 0 else 0.0,
           nb=2 if lod == 0 else 0, caps=(True, False))
    prof = RIM_PROF if lod == 0 else RIM_PROF1
    G.sweep_ring(tk, G.rrect(-TX, TX, -TY, TY, RC, nc), [(dn, Z_RIM + dz) for dn, dz in prof] + [(-WALL, Z_SOLV - 0.004)])
    parts = [tk]
    sv = P("solvent", "solvent")
    G.poly_cap(sv, G.rrect(-TX + WALL, TX - WALL, -TY + WALL, TY - WALL, RC - WALL, nc), Z_SOLV)
    parts.append(sv)
    if lod == 0:
        for zc in BEADS:
            G.sweep_ring(tk, G.rrect(-TX, TX, -TY, TY, RC, nc),
                         [(0.0, zc - 0.008), (0.003, zc - 0.006), (0.004, zc), (0.003, zc + 0.006), (0.0, zc + 0.008)])
        # blank nameplate on the tank face on four rivets
        pl = P("nameplate", "plate")
        x0, x1, z0, z1 = PLATE
        fr = g.Frame((0.0, -TY, 0.0), (1, 0, 0), (0, 0, 1), (0, -1, 0))
        G.slab(pl, x0, x1, z0, z1, 0.0, 0.0015, rc=0.004, nc=1, frame=fr)
        for x in (x0 + 0.008, x1 - 0.008):
            for z in (z0 + 0.008, z1 - 0.008):
                G.rivet(pl, (x, -TY - 0.0015, z), (0, -1, 0), r=0.0028, h=0.0016, sides=6)
        parts.append(pl)
    return parts


def build_legs(spec):
    lod = spec["lod"]
    lg = P("legs", "galv_shelf")
    ch = 0.005 if lod == 0 else 0.0
    z0 = Z_FOOT if lod < 2 else 0.0
    for sx in (-1, 1):
        for sy in (-1, 1):
            cb, hb = leg_at(sx, sy, z0)
            G.loft(lg, [chamfer_sq(cb, hb, ch), chamfer_sq((sx * LEG_X, sy * LEG_Y), LEG_TOP, ch)], [z0, Z_BOT + 0.004],
                   lambda a, b, c: Vector((a, b, c)), caps=(True, False))
    parts = [lg]
    if lod == 2:
        return parts
    ft = P("feet", "rubber")
    pl = P("foot_plates", "galv_shelf") if lod == 0 else None
    nt = P("foot_studs", "zinc") if lod == 0 else None
    for sx in (-1, 1):
        for sy in (-1, 1):
            (cx, cy), h = leg_at(sx, sy, Z_FOOT)
            if lod == 0:
                # pad with a chamfer, a stud with a locknut, a plate under the leg
                G.lathe(ft, [(0.027, 0.0), (0.027, 0.007), (0.023, 0.011), (0.009, 0.012)], 12, (cx, cy, 0.0), "z",
                        caps=(True, True))
                G.lathe(nt, [(0.006, 0.010), (0.006, Z_FOOT - 0.003)], 8, (cx, cy, 0.0), "z")
                G.hex_prism(nt, (cx, cy, 0.019), "z", 0.019, 0.008)
                G.slab(pl, cx - h - 0.008, cx + h + 0.008, cy - h - 0.008, cy + h + 0.008, Z_FOOT - 0.004, Z_FOOT,
                       rc=0.006, nc=1)
            else:
                g.cyl(ft, (cx, cy, Z_FOOT / 2), "z", 0.027, Z_FOOT, 6)
    parts += [p for p in (ft, pl, nt) if p is not None]
    return parts


def build_shelf(spec):
    """Shelf under the tank between the legs with a flange, on angles to the legs; the mat of the M84 place."""
    lod = spec["lod"]
    sh = P("shelf", "galv_shelf")
    if lod == 2:
        g.box(sh, -SH_X, SH_X, -SH_Y, SH_Y, Z_SH, Z_SH + SH_T)
        return [sh]
    if lod == 0:
        G.slab(sh, -SH_X, SH_X, -SH_Y, SH_Y, Z_SH, Z_SH + SH_T, rc=0.004, nc=1)
    else:
        g.box(sh, -SH_X, SH_X, -SH_Y, SH_Y, Z_SH, Z_SH + SH_T)
    t = 0.0025
    for y0, y1 in ((-SH_Y, -SH_Y + t), (SH_Y - t, SH_Y)):
        g.box(sh, -SH_X + 0.004, SH_X - 0.004, y0, y1, Z_SH - 0.025, Z_SH)
    parts = [sh]
    if lod == 0:
        for x0, x1 in ((-SH_X, -SH_X + t), (SH_X - t, SH_X)):
            g.box(sh, x0, x1, -SH_Y + 0.004, SH_Y - 0.004, Z_SH - 0.025, Z_SH)
        # gussets under the shelf corners: they go into the leg, a bolt from below
        bt = P("shelf_bolts", "zinc")
        for sx in (-1, 1):
            for sy in (-1, 1):
                (cx, cy), h = leg_at(sx, sy, Z_SH)
                xa, xb = sorted((sx * (SH_X - 0.04), cx - sx * (h - 0.006)))
                ya, yb = sorted((sy * (SH_Y - 0.04), cy - sy * (h - 0.006)))
                g.box(sh, xa, xb, ya, yb, Z_SH - 0.004, Z_SH - 0.0005)
                G.hex_prism(bt, (sx * (SH_X - 0.02), sy * (SH_Y - 0.02), Z_SH - 0.006), "z", 0.013, 0.004)
        parts.append(bt)
    mt = P("slot1_mat", "mat")
    G.slab(mt, S1[0] - 0.11, S1[0] + 0.11, S1[1] - 0.105, S1[1] + 0.105, Z_SH + SH_T, Z_SH + SH_T + MAT_T,
           rc=0.010, nc=2 if lod == 0 else 0, re=0.0015 if lod == 0 else 0.0, ne=1 if lod == 0 else 0)
    parts.append(mt)
    return parts


# =============================================================================
# Lid: the left half is closed, the right one is raised on a prop
# =============================================================================
def lid_half(spec, x0, x1, name):
    """Lid half: a sheet with rounded edges, skirts at the front and the ends with a turned-under edge, a
    bar handle, hinge leaves. Returns (what turns with the lid, what stays on the axis and on the tank)."""
    lod = spec["lod"]
    ld = P(name, "galv_lid")
    if lod == 2:
        g.box(ld, x0, x1, LY0, LY1, Z_LID - 0.004, Z_LID)
        return [ld], []
    if lod == 0:
        G.slab(ld, x0, x1, LY0, LY1, Z_LID - 0.0018, Z_LID, rc=0.008, nc=2, re=0.0012, ne=1)
    else:
        g.box(ld, x0, x1, LY0, LY1, Z_LID - 0.0018, Z_LID)
    zs0 = Z_RIM - 0.022
    g.box(ld, x0 + 0.003, x1 - 0.003, LY0, LY0 + 0.0018, zs0, Z_LID - 0.0018)                # front skirt
    xe = x0 if x0 < 0 else x1
    xa, xb = (xe, xe + 0.0018) if x0 < 0 else (xe - 0.0018, xe)
    g.box(ld, xa, xb, LY0 + 0.003, LY1 - 0.003, zs0, Z_LID - 0.0018)                         # end skirt
    if lod == 0:
        # turned-under edge of the skirts
        g.pipe(ld, [(x0 + 0.004, LY0 + 0.0009, zs0), (x1 - 0.004, LY0 + 0.0009, zs0)], 0.0018, 6)
        g.pipe(ld, [((xa + xb) / 2, LY0 + 0.004, zs0), ((xa + xb) / 2, LY1 - 0.004, zs0)], 0.0018, 6)
    moving = [ld]
    # front bar handle: a bent rod on two welded pads
    hd = P(name + "_handle", "galv_lid")
    xc, zh = (x0 + x1) / 2, Z_LID - 0.013
    pts = [(xc - 0.07, LY0, zh), (xc - 0.07, LY0 - 0.034, zh), (xc + 0.07, LY0 - 0.034, zh), (xc + 0.07, LY0, zh)]
    g.pipe(hd, G.fillet(pts, 0.012, 4) if lod == 0 else pts, 0.005, 8 if lod == 0 else 4)
    if lod == 0:
        for s in (-1, 1):
            G.lathe(hd, [(0.0085, 0.0), (0.0075, 0.0022)], 10, (xc + s * 0.07, LY0, zh), "-y", caps=(False, True))
    moving.append(hd)
    fixed = []
    if lod == 0:
        # hinges: a leaf on the lid with three screws, a pivot on the axis, a leaf on the tank rim
        lv = P(name + "_leaves", "steel")
        kn = P(name + "_knuckles", "steel")
        for xh in (x0 + 0.09, x1 - 0.09):
            G.slab(lv, xh - 0.03, xh + 0.03, LY1 - 0.045, LY1, Z_LID, Z_LID + 0.0015, rc=0.004, nc=1)
            for dx in (-0.018, 0.0, 0.018):
                G.rivet(lv, (xh + dx, LY1 - 0.025, Z_LID + 0.0015), (0, 0, 1), r=0.0028, h=0.0014, sides=6)
            g.cyl(kn, (xh, YH, ZH), "x", 0.006, 0.06, 10)
            for s in (-1, 1):
                G.lathe(kn, [(0.0045, 0.0), (0.0, 0.002)], 8, (xh + s * 0.03, YH, ZH), (s, 0, 0))
            g.box(kn, xh - 0.03, xh + 0.03, TY + 0.0155, TY + 0.017, Z_RIM - 0.034, ZH)
            for dx in (-0.018, 0.018):
                G.rivet(kn, (xh + dx, TY + 0.017, Z_RIM - 0.02), (0, 1, 0), r=0.0028, h=0.0014, sides=6)
        moving.append(lv)
        fixed.append(kn)
    return moving, fixed


def build_lid(spec):
    lod = spec["lod"]
    mv_l, fx_l = lid_half(spec, -TX - 0.018, -0.002, "lid_l")
    mv_r, fx_r = lid_half(spec, 0.002, TX + 0.018, "lid_r")
    for p in mv_r:
        rotate_part(p)
    parts = mv_l + fx_l + mv_r + fx_r
    if lod < 2:
        # prop of the raised half: a strap from a bracket on the tank end to the lid skirt, on rivets
        st = P("lid_stay", "steel")
        a = Vector((TX + 0.019, TY - 0.05, Z_RIM - 0.055))
        b = rot_lid((TX + 0.0145, LY1 - 0.20, Z_LID - 0.012))
        G.bar(st, a, b, 0.016, 0.003, up=(1, 0, 0))
        if lod == 0:
            g.box(st, TX, TX + 0.0175, a.y - 0.016, a.y + 0.016, a.z - 0.012, a.z + 0.012)       # bracket
            G.rivet(st, a + Vector((0.0015, 0, 0)), (1, 0, 0), r=0.0045, h=0.0025, sides=8)
            G.rivet(st, b + Vector((-0.0015, 0, 0)), (-1, 0, 0), r=0.0045, h=0.0025, sides=8)
        parts.append(st)
    return parts


def build_tray(spec):
    """Grille tray on the rim under the raised half: a rod frame with rounded corners, crosspieces, hooks
    over the rim."""
    lod = spec["lod"]
    if lod > 1:
        return []
    gr = P("drip_tray", "grate")
    x0, x1, y0, y1, z = 0.04, TX - 0.03, -TY + 0.02, TY - 0.02, Z_TRAY
    s = 6 if lod == 0 else 4
    ring = [(x, y, z) for x, y in G.rrect(x0, x1, y0, y1, 0.02, 3 if lod == 0 else 1)]
    g.pipe(gr, ring + [ring[0]], 0.004, s)
    for xs, ya, yo, sg in (((x0 + 0.05, x1 - 0.05), y0, -TY, -1), ((0.20, 0.33), y1, TY, 1)):
        for x in xs:
            path = [(x, ya, z), (x, ya + sg * 0.002, Z_RIM + 0.008), (x, yo + sg * 0.022, Z_RIM + 0.008),
                    (x, yo + sg * 0.022, Z_RIM - 0.016)]
            g.pipe(gr, G.fillet(path, 0.006, 3) if lod == 0 else path, 0.003, s)
    n = 9 if lod == 0 else 4
    for k in range(1, n):
        x = x0 + (x1 - x0) * k / n
        G.rod(gr, (x, y0, z), (x, y1, z), 0.0025, 4)
    for k in range(1, 4 if lod == 0 else 2):
        y = y0 + (y1 - y0) * k / (4 if lod == 0 else 2)
        G.rod(gr, (x0, y, z - 0.005), (x1, y, z - 0.005), 0.0025, 4)
    return [gr]


# =============================================================================
# Pump on the right: motor, fan, volute, terminal box
# =============================================================================
def build_pump(spec):
    lod = spec["lod"]
    n = 24 if lod == 0 else (12 if lod == 1 else 8)
    parts = []
    br = P("pump_bracket", "paint_black")
    if lod == 0:
        G.slab(br, TX, TX + 0.22, -0.17, 0.13, Z_BR - 0.008, Z_BR, rc=0.006, nc=1, re=0.002, ne=1)
    else:
        g.box(br, TX, TX + 0.22, -0.17, 0.13, Z_BR - 0.008, Z_BR)
    if lod < 2:
        g.box(br, TX, TX + 0.006, -0.17, 0.13, Z_BR - 0.10, Z_BR)                              # wall toward the tank
        g.box(br, TX + 0.006, TX + 0.22, -0.17, -0.164, Z_BR - 0.06, Z_BR - 0.008)               # front flange
    if lod == 0:
        for y in (-0.16, 0.118):                                                               # gussets
            g.prism(br, [(TX + 0.006, Z_BR - 0.008), (TX + 0.20, Z_BR - 0.008), (TX + 0.006, Z_BR - 0.10)],
                    (0, 2), y, y + 0.006)
    parts.append(br)
    mo = P("pump_motor", "paint_black")
    c = (PX, 0.0, PZ)
    G.lathe(mo, [(MR, MY0), (MR, MY1)], n, c, "y")
    # motor feet on the bracket
    for y in (-0.075, 0.045):
        g.box(mo, PX - 0.058, PX + 0.058, y - 0.012, y + 0.012, Z_BR, PZ - MR + 0.012)
        if lod < 2:
            g.box(mo, PX - 0.072, PX + 0.072, y - 0.016, y + 0.016, Z_BR, Z_BR + 0.008)
    parts.append(mo)
    if lod == 2:
        return parts
    a, b, w = G.basis("y")
    if lod == 0:
        # cooling fins along the body, except the bottom (the feet are there)
        for k in range(16):
            t = 2 * math.pi * (k + 0.5) / 16
            d = a * math.cos(t) + b * math.sin(t)
            if d.z < -0.6:
                continue
            fr = g.Frame(Vector(c) + d * (MR + 0.002), (0, 1, 0), w.cross(d), d)
            g.box(mo, MY0 + 0.012, MY1 - 0.010, -0.0013, 0.0013, -0.004, 0.004, frame=fr)
    # front end and the fan shroud: outer and inner walls, a grille of rings and spokes
    G.lathe(mo, [(MR + 0.001, 0.0), (MR - 0.001, 0.006), (MR - 0.006, 0.012)], n, (PX, MY0, PZ), "-y")
    gd = P("pump_guard", "guard")
    G.lathe(gd, [(0.067, 0.010), (0.067, 0.052)], n, (PX, MY0, PZ), "-y")
    G.lathe(gd, [(0.065, 0.012), (0.065, 0.050)], n, (PX, MY0, PZ), "-y", inward=True)
    G.lathe(gd, [(0.067, 0.052), (0.065, 0.052)], n, (PX, MY0, PZ), "-y")
    gf = g.Frame((PX, GUARD_Y1 + 0.002, PZ), (1, 0, 0), (0, 0, 1), (0, -1, 0))
    for R in ((0.022, 0.038, 0.054) if lod == 0 else (0.03, 0.054)):
        G.torus(gd, gf, R, 0.0016, 20 if lod == 0 else 12, 4)
    for k in range(4 if lod == 0 else 2):
        t = math.pi * k / (4 if lod == 0 else 2) + math.pi / 4
        d = Vector((math.cos(t), 0.0, math.sin(t)))
        G.rod(gd, Vector(gf.o) - d * 0.065, Vector(gf.o) + d * 0.065, 0.0018, 4)
    G.lathe(gd, [(0.012, 0.0), (0.012, 0.004), (0.0, 0.005)], 10, (PX, GUARD_Y1 + 0.003, PZ), "-y")
    parts.append(gd)
    # impeller - bone ozl_work (spins in a loop when "working")
    fa = P("pump_fan", "fan", group=SEL_FAN)
    G.fan(fa, (PX, FAN_Y, PZ), "-y", 0.058, 0.016, 5, 0.026, 28.0, lod=lod)
    G.rod(fa, (PX, MY0 - 0.006, PZ), (PX, FAN_Y + 0.006, PZ), 0.006, 8)
    parts.append(fa)
    # pump volute at the back, the inlet through the tank wall, the outlet up
    rd = P("pump_red", "paint_red")
    G.lathe(rd, [(MR - 0.001, 0.0), (MR + 0.004, 0.0), (MR + 0.004, 0.006), (MR - 0.001, 0.006)], n,
            (PX, MY1 - 0.004, PZ), "y")
    hv = VOL_Y1 - VOL_Y0
    G.lathe(rd, [(MR, 0.0), (VOL_R, 0.006), (VOL_R, hv - 0.008), (VOL_R - 0.010, hv), (0.026, hv + 0.004),
                 (0.0, hv + 0.006)], n, (PX, VOL_Y0, PZ), "y")
    # outlet boss: from the volute up to the riser
    rx, ry = RISER
    G.lathe(rd, [(0.019, 0.0), (0.019, 0.032), (0.023, 0.034), (0.023, 0.044), (PIPE_R + 0.002, 0.046)], 12 if lod == 0 else 8,
            (rx, ry, PZ + VOL_R - 0.03), "z")
    parts.append(rd)
    pp = P("pump_inlet", "steel")
    zi = PZ - 0.045
    G.rod(pp, (PX - VOL_R + 0.012, ry, zi), (TX + 0.002, ry, zi), 0.012, 10 if lod == 0 else 6)
    if lod == 0:
        G.hex_prism(pp, (TX + 0.004, ry, zi), "x", 0.036, 0.008)                               # locknut
        G.hex_prism(pp, ((PX - VOL_R + TX) / 2 + 0.006, ry, zi), "x", 0.030, 0.012)            # running nipple
    parts.append(pp)
    # terminal box on the motor: a body, a cover on screws; a lamp and a toggle on the face; a gland
    jb = P("pump_box", "paint_black")
    zb0, zb1 = PZ + MR - 0.008, PZ + MR + 0.052
    if lod == 0:
        G.slab(jb, PX - 0.045, PX + 0.045, -0.065, 0.035, zb0, zb1, rc=0.008, nc=2, re=0.003, ne=1)
        G.slab(jb, PX - 0.047, PX + 0.047, -0.067, 0.037, zb1, zb1 + 0.006, rc=0.009, nc=2, re=0.002, ne=1)
    else:
        g.box(jb, PX - 0.045, PX + 0.045, -0.065, 0.035, zb0, zb1 + 0.006)
    parts.append(jb)
    zl = PZ + MR + 0.025
    lm = P("pump_lamp", "lamp", group=SEL_LAMP)
    G.lathe(lm, [(0.0092, 0.0), (0.0085, 0.006), (0.006, 0.0095), (0.0, 0.011)], 12 if lod == 0 else 6,
            (PX - 0.018, -0.065, zl), "-y")
    parts.append(lm)
    if lod == 0:
        hw = P("pump_hw", "chrome")
        G.lathe(hw, [(0.0125, 0.0), (0.0125, 0.003), (0.0098, 0.0055), (0.0092, 0.005)], 14, (PX - 0.018, -0.065, zl), "-y")
        for sx in (-1, 1):
            for sy in (-1, 1):
                G.rivet(hw, (PX + sx * 0.038, -0.015 + sy * 0.044, zb1 + 0.006), (0, 0, 1), r=0.003, h=0.0016)
        parts.append(hw)
        sw = P("pump_switch", "zinc")
        G.hex_prism(sw, (PX + 0.020, -0.068, zl), "y", 0.012, 0.006)
        G.rod(sw, (PX + 0.020, -0.070, zl), (PX + 0.020, -0.086, zl - 0.010), 0.0022, 6)
        G.lathe(sw, [(0.0022, -0.003), (0.0034, 0.0), (0.0022, 0.003)], 6, (PX + 0.020, -0.087, zl - 0.011), (0, -0.85, -0.53))
        # cable gland on the right side of the box
        G.hex_prism(sw, (PX + 0.049, -0.015, PZ + MR + 0.022), "x", 0.016, 0.006)
        G.lathe(sw, [(0.0075, 0.0), (0.0055, 0.010)], 8, (PX + 0.052, -0.015, PZ + MR + 0.022), "x")
        parts.append(sw)
        # bolts of the bracket to the tank and of the motor feet
        bt = P("pump_bolts", "zinc")
        for y in (-0.14, 0.10):
            for z in (Z_BR - 0.03, Z_BR - 0.08):
                G.hex_prism(bt, (TX + 0.008, y, z), "x", 0.013, 0.004)
        for y in (-0.075, 0.045):
            for s in (-1, 1):
                G.hex_prism(bt, (PX + s * 0.064, y, Z_BR + 0.010), "z", 0.011, 0.004)
        parts.append(bt)
    # power cable: from the gland to the right, past the bracket to the floor, a plug
    cb = P("pump_cable", "cable")
    cpts = [(PX + 0.057, -0.015, PZ + MR + 0.022), (PX + 0.085, -0.01, PZ + MR + 0.005), (PX + 0.115, 0.0, 0.58),
            (PX + 0.125, 0.03, 0.42), (PX + 0.13, 0.10, 0.12), (PX + 0.14, 0.18, 0.0055), (PX + 0.16, 0.34, 0.0055)]
    g.pipe(cb, G.spline(cpts, 2) if lod == 0 else cpts, 0.0055, 8 if lod == 0 else 5)
    if lod == 0:
        e, d = Vector(cpts[-1]), (Vector(cpts[-1]) - Vector(cpts[-2])).normalized()
        G.lathe(cb, [(0.0065, 0.0), (0.012, 0.012), (0.019, 0.02), (0.019, 0.045), (0.0, 0.047)], 12, e, d)
        bp = P("plug_pins", "chrome")
        for s in (-1, 1):
            q = e + d * 0.047 + Vector((-d.y, d.x, 0.0)) * (s * 0.0095)
            G.rod(bp, q, q + d * 0.018, 0.002, 6)
        parts.append(bp)
    parts.append(cb)
    return parts


# =============================================================================
# Riser, valve, outlet, stream
# =============================================================================
def build_faucet(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    rx, ry = RISER
    z0 = PZ + VOL_R + 0.012
    pp = P("faucet_pipe", "steel")
    path = [(rx, ry, z0), (rx, ry, FAUCET_Z), (FX, FY, FAUCET_Z), (FX, FY, NOZZLE_Z + 0.008)]
    g.pipe(pp, G.fillet(path, 0.035, 6 if lod == 0 else 2), PIPE_R, 10 if lod == 0 else 6)
    # spout with a flare
    G.lathe(pp, [(PIPE_R + 0.0015, 0.012), (PIPE_R + 0.0015, 0.003), (PIPE_R, 0.0), (0.0058, 0.0004)], 12 if lod == 0 else 6,
            (FX, FY, NOZZLE_Z), "z")
    parts = [pp]
    vb = P("faucet_valve", "brass")
    G.lathe(vb, [(0.013, -0.034), (0.016, -0.030), (0.021, -0.022), (0.025, -0.008), (0.025, 0.008), (0.021, 0.022),
                 (0.016, 0.030), (0.013, 0.034)], 12 if lod == 0 else 6, (rx, ry, VALVE_Z), "z", caps=(True, True))
    G.lathe(vb, [(0.016, 0.018), (0.014, 0.036), (0.010, 0.042)], 10 if lod == 0 else 6, (rx, ry, VALVE_Z), "-y",
            caps=(False, True))
    if lod == 0:
        for dz in (-0.037, 0.037):
            G.hex_prism(vb, (rx, ry, VALVE_Z + dz), "z", 0.030, 0.010)
        G.hex_prism(vb, (rx, ry - 0.046, VALVE_Z), "y", 0.018, 0.008)                         # gland nut
        G.hex_prism(vb, (rx, ry, 0.745), "z", 0.034, 0.014)                                   # riser coupling
    parts.append(vb)
    hw = P("faucet_wheel", "paint_red")
    G.rod(hw, (rx, ry - 0.048, VALVE_Z), (rx, ry - 0.068, VALVE_Z), 0.0035, 6)
    G.handwheel(hw, (rx, ry - 0.066, VALVE_Z), "-y", 0.030, 0.0038, 3, nu=18 if lod == 0 else 10, nv=6 if lod == 0 else 4)
    parts.append(hw)
    if lod == 0:
        # riser clamp to the tank: a plate on the wall, a strap, a ring
        cl = P("riser_clamp", "paint_black")
        zc = 0.90
        g.box(cl, TX, TX + 0.004, ry - 0.02, ry + 0.02, zc - 0.015, zc + 0.015)
        G.bar(cl, (TX + 0.004, ry, zc), (rx - PIPE_R - 0.001, ry, zc), 0.024, 0.004)
        G.lathe(cl, [(PIPE_R + 0.0018, -0.012), (PIPE_R + 0.0018, 0.012)], 12, (rx, ry, zc), "z")
        bt = P("riser_clamp_bolts", "zinc")
        for dy in (-0.012, 0.012):
            G.hex_prism(bt, (TX + 0.006, ry + dy, zc), "x", 0.010, 0.004)
        parts += [cl, bt]
    # stream (bone ozl_flow): at rest it is FLOW_L lower, under the mirror
    fl = P("flow", "stream", group=SEL_FLOW)
    nseg = 10 if lod == 0 else 4
    pts, radii = [], []
    for i in range(nseg + 1):
        s = i / nseg
        pts.append((FX + 0.0007 * math.sin(i * 1.7), FY + 0.0006 * math.cos(i * 2.3), FLOW_TOP - (FLOW_TOP - FLOW_BOT) * s - FLOW_L))
        rr = 0.0042 - 0.0012 * s
        radii.append((rr, rr))
    g.tube_var(fl, pts, radii, 8 if lod == 0 else 5)
    parts.append(fl)
    fo = P("flow_foam", "foam", group=SEL_FLOW)
    zf = Z_SOLV - FLOW_L
    G.torus(fo, g.Frame((FX, FY, zf + 0.0015), (1, 0, 0), (0, 1, 0), (0, 0, 1)), 0.010, 0.0028, 16 if lod == 0 else 8,
            6 if lod == 0 else 4, squash=0.5)
    G.lathe(fo, [(0.016, 0.0004), (0.0, 0.0012)], 12 if lod == 0 else 6, (FX, FY, zf), "z")
    if lod == 0:
        for R, r in ((0.030, 0.0012), (0.048, 0.0010)):
            G.torus(fo, g.Frame((FX, FY, zf + 0.0005), (1, 0, 0), (0, 1, 0), (0, 0, 1)), R, r, 20, 3, squash=0.4)
    parts.append(fo)
    return parts


# =============================================================================
# Drain: locknut, ball valve with a lever and a seal, hose into the trap
# =============================================================================
def build_drain(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    x, y, z = DRAIN
    s = 10 if lod == 0 else 6
    dn = P("drain", "steel")
    G.rod(dn, (x + 0.004, y, z), (x - 0.036, y, z), 0.0135, s)
    if lod == 0:
        G.hex_prism(dn, (x - 0.004, y, z), "x", 0.036, 0.008)                                 # locknut
    parts = [dn]
    vb = P("drain_valve", "brass")
    G.lathe(vb, [(0.017, 0.0), (0.019, 0.004), (0.023, 0.012), (0.024, 0.018), (0.023, 0.024), (0.019, 0.032),
                 (0.017, 0.036)], 12 if lod == 0 else 6, (x - 0.034, y, z), "-x", caps=(True, True))
    if lod == 0:
        for xx in (x - 0.033, x - 0.071):
            G.hex_prism(vb, (xx, y, z), "x", 0.032, 0.006)
        G.lathe(vb, [(0.0125, 0.0), (0.0135, 0.008), (0.0118, 0.011), (0.0135, 0.017), (0.0118, 0.020)], 10,
                (x - 0.074, y, z), "-x")                                                     # hose barb
    parts.append(vb)
    # valve lever: a stem, a strap across the pipe (the valve is closed), a red handle
    xv = x - 0.052
    lv = P("drain_lever", "steel")
    G.rod(lv, (xv, y, z + 0.020), (xv, y, z + 0.036), 0.005, 8 if lod == 0 else 5)
    G.bar(lv, (xv, y + 0.008, z + 0.037), (xv, y - 0.10, z + 0.037), 0.012, 0.003)
    parts.append(lv)
    gp = P("drain_grip", "paint_red")
    G.lathe(gp, [(0.0045, 0.0), (0.0075, 0.004), (0.0080, 0.040), (0.0060, 0.047), (0.0, 0.048)], 10 if lod == 0 else 5,
            (xv, y - 0.055, z + 0.037), "-y", caps=(True, False))
    parts.append(gp)
    hs = P("drain_hose", "hose")
    tx, ty = TRAP
    pts = [(x - 0.086, y, z), (x - 0.13, y, z - 0.02), (x - 0.16, y - 0.03, z - 0.14), (x - 0.15, y - 0.10, 0.20),
           (tx + 0.01, ty + 0.05, 0.07), (tx, ty, 0.012), (tx, ty, -0.03)]
    g.pipe(hs, G.spline(pts, 3) if lod == 0 else pts[::2] + [pts[-1]], 0.016, 10 if lod == 0 else 5)
    parts.append(hs)
    tr = P("floor_trap", "castiron")
    G.lathe(tr, [(0.095, 0.0), (0.095, 0.004), (0.088, 0.008), (0.080, 0.008), (0.080, 0.004)], 20 if lod == 0 else 8,
            (tx, ty, 0.0), "z")
    if lod == 0:
        # grille: an inner ring for the hose and radial rods
        G.lathe(tr, [(0.030, 0.0), (0.030, 0.006), (0.024, 0.006), (0.024, 0.0)], 14, (tx, ty, 0.0), "z")
        for k in range(8):
            t = 2 * math.pi * (k + 0.5) / 8
            d = Vector((math.cos(t), math.sin(t), 0.0))
            G.bar(tr, Vector((tx, ty, 0.003)) + d * 0.029, Vector((tx, ty, 0.003)) + d * 0.081, 0.008, 0.006)
        hc = P("drain_clamp", "zinc")
        G.hose_clamp(hc, (x - 0.094, y, z), "-x", 0.016)
        parts.append(hc)
        # seal: wire through the lever to the valve body, a lead disc
        ld = P("drain_seal", "lead")
        G.rod(ld, (xv, y - 0.03, z + 0.037), (xv - 0.002, y - 0.026, z + 0.012), 0.0009, 4)
        g.cyl(ld, (xv - 0.002, y - 0.035, z + 0.004), "y", 0.007, 0.004, 8)
        parts.append(ld)
    parts.append(tr)
    return parts


# =============================================================================
# Dryer grille: posts, crossbars, mesh, hooks, pegs for the helmet and the gas mask
# =============================================================================
def j_peg(part, cap, x, yc, ztip, lod):
    """Rod peg: from the lower crossbar forward and up (the helmet and the gas mask are put on it), a
    rubber cap."""
    pts = [(x, RY - 0.006, RZ0), (x, yc, RZ0), (x, yc, ztip)]
    g.pipe(part, G.fillet(pts, 0.03, 5) if lod == 0 else pts, 0.005, 8 if lod == 0 else 4)
    if lod == 0:
        G.lathe(cap, [(0.003, -0.008), (0.0075, -0.006), (0.0085, 0.0), (0.006, 0.006), (0.0, 0.008)], 10,
                (x, yc, ztip), "z")


def build_rack(spec):
    lod = spec["lod"]
    parts = []
    rk = P("rack", "rack")
    for sx in (-1, 1):
        x = sx * RX
        if lod == 0:
            G.slab(rk, x - 0.015, x + 0.015, RY - 0.015, RY + 0.015, POST_Z0, RZ1 + 0.015, rc=0.003, nc=1)
        else:
            g.box(rk, x - 0.015, x + 0.015, RY - 0.015, RY + 0.015, POST_Z0, RZ1 + 0.015)
        if lod < 2:
            for z in (0.71, 0.88):                                                             # clamps to the end
                xa, xb = sorted((sx * TX, x - sx * 0.015))
                g.box(rk, xa, xb, RY - 0.022, RY + 0.022, z - 0.018, z + 0.018)
    g.box(rk, -RX + 0.015, RX - 0.015, RY - 0.008, RY + 0.008, RZ0 - 0.008, RZ0 + 0.008)       # lower crossbar
    parts.append(rk)
    rr = P("rack_top", "rack_red")
    if lod == 0:
        G.slab(rr, -RX - 0.015, RX + 0.015, RY - 0.012, RY + 0.012, RZ1 - 0.012, RZ1 + 0.012, rc=0.002, nc=1)
    else:
        g.box(rr, -RX - 0.015, RX + 0.015, RY - 0.012, RY + 0.012, RZ1 - 0.012, RZ1 + 0.012)
    parts.append(rr)
    if lod == 2:
        return parts
    wr = P("rack_wires", "rack")
    n = 20 if lod == 0 else 10
    for k in range(1, n):
        x = -RX + 2 * RX * k / n
        G.rod(wr, (x, RY, RZ0), (x, RY, RZ1), 0.0025, 4)
    G.rod(wr, (-RX, RY - 0.004, (RZ0 + RZ1) / 2), (RX, RY - 0.004, (RZ0 + RZ1) / 2), 0.0025, 4)
    # pegs: the helmet - at its middle, the gas mask - along the mask axis up to the crown from inside
    cp = P("peg_caps", "rubber") if lod == 0 else None
    j_peg(wr, cp, HELM[0], HELM[1], HELM[2] + 0.13, lod)
    j_peg(wr, cp, GP5_TIP.x, GP5_TIP.y, GP5_TIP.z, lod)
    parts.append(wr)
    if cp is not None:
        parts.append(cp)
    if lod == 0:
        bt = P("rack_bolts", "zinc")
        for sx in (-1, 1):
            for z in (0.71, 0.88):
                for dy in (-0.011, 0.011):
                    G.hex_prism(bt, (sx * (RX + 0.017), RY + dy, z), (sx, 0, 0), 0.013, 0.004)
        parts.append(bt)
        hk = P("hooks", "steel")
        for x in HOOKS:
            pts = [(x, RY + 0.018, RZ1 - 0.006), (x, RY + 0.018, RZ1 + 0.016), (x, RY, RZ1 + 0.022),
                   (x, RY - 0.018, RZ1 + 0.012), (x, RY - 0.019, RZ1 - 0.02), (x, RY - 0.024, RZ1 - 0.05),
                   (x, RY - 0.045, RZ1 - 0.07), (x, RY - 0.062, RZ1 - 0.058), (x, RY - 0.064, RZ1 - 0.042)]
            g.pipe(hk, G.spline(pts, 2), 0.0028, 5)
        parts.append(hk)
    return parts


# =============================================================================
# Hose M84 -> GP-5: an adapter on the valve box, clamps, a coupling on the M84 tip
# =============================================================================
def m84_tip():
    """Tip of the cone of the M84 nozzle in slot 1 and the nozzle axis."""
    return Vector(S1) + M84_NOZ + M84_DIR * 0.040, M84_DIR


def build_hose(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    ax, neck = GP5["axis"], GP5["neck"]
    ad = P("gp5_adapter", "alu")
    G.lathe(ad, [(0.0185, -0.004), (0.0205, 0.0), (0.0205, 0.016), (0.016, 0.020), (0.0085, 0.024)],
            14 if lod == 0 else 8, neck, ax, caps=(False, True))
    G.lathe(ad, [(0.0072, 0.024), (0.0085, 0.031), (0.0066, 0.035), (0.0080, 0.042)], 10 if lod == 0 else 6, neck, ax)
    parts = [ad]
    tip, d = m84_tip()
    cp = P("hose_coupling", "brass")
    G.lathe(cp, [(0.0058, -0.012), (0.0090, -0.009), (0.0090, 0.0), (0.0090, 0.014), (0.0078, 0.018), (0.0070, 0.022),
                 (0.0078, 0.027), (0.0066, 0.032)], 10 if lod == 0 else 6, tip, d, caps=(True, False))
    if lod == 0:
        G.hex_prism(cp, tip + d * 0.003, d, 0.017, 0.010)
    parts.append(cp)
    h0 = neck + ax * 0.040
    c1 = tip + d * 0.030
    # from the mask the hose leaves along the thread axis down and forward and sags toward the rim (steeper
    # at the top, flatter near the rim), passes over the rim bead, lies on the tank face, under the tank on
    # the shelf and to the M84 coupling
    pts = [tuple(h0), tuple(h0 + ax * 0.045), (0.403, -0.205, 1.09), (0.408, -0.245, 1.012), (0.411, -0.274, 0.973),
           (0.412, -0.291, 0.9585), (0.412, -0.3035, 0.938), (0.41, -0.2915, 0.885), (0.405, -0.2905, 0.70),
           (0.403, -0.2905, 0.46), (0.406, -0.281, 0.34), (0.418, -0.255, 0.235), (0.436, -0.212, 0.164),
           (0.445, -0.16, 0.1495), (0.44, -0.10, 0.1515), (0.41, -0.072, 0.163), tuple(c1 + d * 0.028), tuple(c1)]
    hs = P("test_hose", "hose_hp")
    g.pipe(hs, G.spline(pts, 2) if lod == 0 else pts[:2] + pts[2:-2:2] + pts[-2:], HOSE_R, 8 if lod == 0 else 6)
    parts.append(hs)
    if lod == 0:
        hc = P("test_hose_clamps", "zinc")
        G.hose_clamp(hc, neck + ax * 0.046, ax, HOSE_R, w=0.007, sides=10)
        G.hose_clamp(hc, c1 + d * 0.004, d, HOSE_R, w=0.007, sides=10)
        parts.append(hc)
    return parts


# =============================================================================
# Brush on the tray, mat and board of places 2 and 3
# =============================================================================
def build_props(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    # module places on the lid: a rubber mat under M85, a plywood board under M86
    m2 = P("slot2_mat", "mat")
    G.slab(m2, S2[0] - 0.12, S2[0] + 0.12, S2[1] - 0.11, S2[1] + 0.11, Z_LID, Z_LID + MAT_T, rc=0.012,
           nc=2 if lod == 0 else 0, re=0.0015 if lod == 0 else 0.0, ne=1 if lod == 0 else 0)
    b3 = P("slot3_board", "ply")
    G.slab(b3, S3[0] - 0.115, S3[0] + 0.115, S3[1] - 0.09, S3[1] + 0.09, Z_LID, S3[2], rc=0.006,
           nc=1 if lod == 0 else 0, re=0.002 if lod == 0 else 0.0, ne=1 if lod == 0 else 0)
    parts += [m2, b3]
    # parts-washing brush: a block, a handle with a thickening at the end, bristle tufts
    fr = G.frame_z(0.17, -0.13, 12.0, TRAY_TOP)
    bw = P("brush", "wood")
    G.slab(bw, -0.06, 0.06, -0.022, 0.022, 0.013, 0.034, rc=0.010, nc=2 if lod == 0 else 0, re=0.005 if lod == 0 else 0.0,
           ne=1 if lod == 0 else 0, frame=fr)
    tilt = math.atan2(0.0215 - 0.011, 0.18)
    hax = fr.u * math.cos(tilt) - fr.n * math.sin(tilt)
    G.lathe(bw, [(0.0095, 0.0), (0.0105, 0.03), (0.0098, 0.12), (0.0122, 0.155), (0.0110, 0.172), (0.0060, 0.180),
                 (0.0, 0.181)], 10 if lod == 0 else 6, fr.p(0.055, 0.0, 0.0235), hax)
    parts.append(bw)
    bb = P("brush_bristle", "bristle")
    if lod == 0:
        for i in range(9):
            for j in range(3):
                u, v = -0.052 + 0.013 * i, -0.013 + 0.013 * j
                g.box(bb, u - 0.0042, u + 0.0042, v - 0.0042, v + 0.0042, 0.0 + 0.0006 * ((i * 3 + j) % 4), 0.0145,
                      frame=fr)
    else:
        g.box(bb, -0.056, 0.056, -0.018, 0.018, 0.0, 0.0145, frame=fr)
    parts.append(bb)
    return parts


def build_lod(spec):
    parts = build_tank(spec) + build_legs(spec) + build_shelf(spec) + build_lid(spec) + build_tray(spec)
    parts += build_pump(spec) + build_faucet(spec) + build_drain(spec) + build_rack(spec) + build_hose(spec)
    parts += build_props(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("BOUNDS", BOUNDS)
        print("GP5 origin %s up %s fwd %s" % (tuple(round(c, 4) for c in GP5["origin"]),
                                             tuple(round(c, 4) for c in GP5["up"]), tuple(round(c, 4) for c in GP5["fwd"])))
        print("GP5 mask box %s .. %s, neck %s, axis %s" % (tuple(round(c, 3) for c in GP5_LO), tuple(round(c, 3) for c in GP5_HI),
                                                        tuple(round(c, 3) for c in GP5["neck"]), tuple(round(c, 3) for c in GP5["axis"])))
    return parts


def collision():
    metal = kx.PEN + r"\metalplate.rvmat"
    # the tank with the legs and the lid; the pump; the grille with the raised half and what hangs on it
    # (each part is at least 0.5 m thick - a thinner geometry component does not work in the engine; the
    # parts overlap, each is convex)
    body = kx.box_pts(-TX - 0.02, TX + 0.02, LY0 - 0.04, TY + 0.02, 0.0, Z_LID)
    pump = kx.box_pts(TX - 0.30, TX + 0.23, -0.25, 0.25, 0.45, Z_LID + 0.10)
    top = kx.box_pts(-RX - 0.02, RX + 0.02, -0.18, YH + 0.11, 0.62, BOUNDS["hi"][2])
    comps = [(body, metal), (pump, metal), (top, metal)]
    memory = {
        "invView": [(-0.3, -2.6, 1.4)],
        "ce_center": [(0.0, 0.0, 0.75)],
        "ce_radius": [(1.0, 0.0, 0.75)],
        "ozl_work_axis": [(PX, GUARD_Y1, PZ), (PX, MY1, PZ)],
        "ozl_flow_axis": [(FX, FY, 0.6), (FX, FY, 1.6)],
    }
    for i, m in enumerate(MODS):
        memory["module_%d" % (i + 1)] = [m]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2] + 0.004)
    return comps, 120.0, memory, bbox


# the first ones are for the --look preview: overall (and in "working"), the module places (and the same
# empty), the dryer with the gas mask and the hose, the pump
SHOTS = [
    ("front", (1.05, -2.35, 1.75), (0.05, 0.0, 0.85), 32),
    ("slots", (-1.0, -1.95, 1.30), (-0.05, -0.05, 0.62), 32),
    ("rack", (0.62, -1.30, 1.50), (0.27, 0.0, 1.10), 34),
    ("pump", (1.40, -0.95, 1.05), (0.64, -0.02, 0.74), 34),
    ("lid", (-0.55, -1.05, 1.60), (-0.28, -0.06, 1.02), 36),
    ("shelf", (-0.2, -1.45, 0.48), (0.05, 0.0, 0.22), 30),
    ("drain", (-1.4, -1.1, 0.7), (-0.62, 0.0, 0.35), 34),
    ("back", (1.5, 2.2, 1.8), (0.0, 0.0, 0.8), 32),
]

M.look_shots = (4, 2)
M.run(build_lod, collision, SHOTS, row_step=1.9, row_shot=((1.9, -6.2, 2.0), (1.9, 0, 0.80)))
