"""M29 - Freedom's chest with a work board: Protection Packer of Freedom (OZL_Frd_Pack_Prot).
A packer: 10x10 cargo, three module slots on a folding board (module_1..3) and module proxies in the
same places. Each module of the "Protection" line has its own slot and its own place where it is
worked with: slot 1 - the pressure tester M84 on the left by the mannequin, with the hose from the gas
mask going to it; slot 2 - the gas analyzer M85 between the mannequin and the helmet; slot 3 - the
plate clamp M86 on the right. The compressor stays (lamp, fan).

    blender --background --python build_m29.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (decals on the lid, the ends, the
chest face and the compressor receiver, the gauge dial without a needle). The layout is in layout.py
(shared with make_decals.py), the geometry that kgeo does not have is in m29_geo.py.

The prop is a large army wooden chest with the lid thrown back and a folding board on two folding
brackets built onto the front. On the board a mannequin head in a gas mask, a helmet, tools and the
module places; in the chest a tray with filters and a cylinder on folded tarpaulin; under the board a
small compressor.

Detail: the "dayz" look (matte, dirtier, colored AO). The soft stuff and small items are DayZ proxies
(blue boxes in the preview): on the mannequin a GP-5 gas mask, on the board a PASGT helmet
(BallisticHelmet, the model texture is BDU camouflage), a GP-5 filter unscrewed from the mask, a
screwdriver, pliers; in the tray five GP-5 filters, an adjustable wrench, tape, a "Pipsi" can, rags.
The mask is leak-tested: an adapter is screwed into the valve box instead of the filter, and from it
a dia. 13 hose (like M84) goes to the tip of the pressure tester in slot 1; without the module the
coupling lies on the end of the hose over the mat. The own parts are more detailed: the chest with a
rolled steel edge trim, riveted corner angles, hinges, a lock plate, bar handles and a chain stay for
the lid; the board with rounded edges on folding angle brackets; the mannequin is a smooth head on a
neck and a stand; the compressor is entirely new (below); the cylinder with a valve and a handwheel
on folded tarpaulin.

The GP-5 on the mannequin is the worn DayZ model GP5GasMask_m, the one the game draws on a player's
head (+Y is up, the face is at -Z, the origin is at the feet): its proxy is placed by a shift, the
head center under the mask (HC_M) to the head center of the mannequin, and a rotation about the
vertical - facing forward-left, toward the pressure tester. The ground GP5GasMask_g is not used: it is
a crumpled mask lying on its side, and its filter slot is rotated about its own axis differently
than in the worn one, so a pose computed from the two slot proxies (as in M25) lays the mask on its
side. The filter slot of the worn model (a matrix from the LOD header, like
the kvanilla extent) gives the valve box neck - the hose adapter goes there. The M84 hose tip is from
build_m84.py (via M25: the point and axis).

Sizes and sources:
- the chest is a wooden US Navy footlocker of the 1940s: 48 x 24 x 20 1/4 inches (1.22 x 0.61 x
  0.51 m). An army footlocker of the same design is smaller - 32 x 16 x 13 inches, walls of
  1/2-1 1/4 inch plywood. Here 1.22 x 0.61, the body up to 0.455 on runners of 0.022, the lid 0.07 -
  0.525 closed; walls 16 mm; steel angles, hinges at the back, bar handles on the ends. The lid is
  open by 102 degrees, held by a chain stay;
- the folding board is plywood 1.36 x 0.40 x 0.022 on two folding shelf brackets (an estimate), the
  top at 0.443 - slightly below the chest rim;
- the mannequin head is a smooth blank without a face on a neck and a stand, the size of a player's
  head (~0.15 x 0.19 x 0.21): it fills the worn DayZ GP-5 mask with a 4-15 mm gap (HEAD_RINGS -
  sections in mask axes); the neck and the stand are visible;
- the cylinder is a steel 6 l, 200-300 bar breathing apparatus cylinder, dia. 140 x 0.535 with a valve
  (an estimate by the class of 6 l cylinders); it lies on folded tarpaulin in the right half of the
  chest;
- the compressor is a small oil-free one with a 6 l receiver: 340 x 300 x 290 mm, 8.4 kg (Metabo
  Basic 160-6 W OF), the class is 330-380 x 300 x 290-440 (Scheppach HC06 350 x 324 x 276, Airpress
  H215-6 380 x 300 x 330). Here a receiver dia. 0.19 x 0.30 along the board with welded seams, a drain
  valve and stamped feet on rubber; on the platform a finned motor and a fan behind a wire guard, a
  piston block (a crankcase, a finned cylinder, a head on four bolts, an air filter), a copper
  discharge tube to a brass block: a dia. 56 gauge, a regulator, a safety valve, a quick coupling; a
  relay box with a lamp and a switch, a cable with a plug along the floor; a bar handle. The yellow
  hose rises onto the board to a blow gun.

The Freedom look (as in M27): bright green paint (no olive) on wood, rubbed to wood on the edges and at
the handles; the inside of the chest and the board are bare wood; decals overlap on the inside of the
lid, the ends and the face (with a peace sign, LEGALIZE and the leaf - kstickers), some with short
English words (allowed on Freedom only); dusty, worn, a bit careless, no rust (build_scuffed is a copy
from M27).

Working look: ozl_lamp is the lamp on the compressor relay box (_on atlas, steady); the motor fan is
the bone ozl_fan on the source ozl_work: a model.cfg loop (sourceAddress loop, maxValue 1/2) - 2
turns per 1 s pass, 5 blades: at 30 fps that is 24 degrees per frame, so the rotation does not
appear to go backward; the gauge needle is the bone ozl_needle on the source ozl_needle (0 is the
scale zero, 1 is 10 bar, 270 degrees clockwise), when "working" it wobbles around 7.2 (wobble). The
modules in the slots "work" together with the station (they have their own OZL_Work).

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
import kcabinet  # noqa: E402
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import krender  # noqa: E402
import kvanilla as kv  # noqa: E402
import kwood  # noqa: E402
import layout as L  # noqa: E402
import m29_geo as G  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
CX0, CX1, CY0, CY1 = L.CX0, L.CX1, L.CY0, L.CY1
ZSK, ZR, ZF, WALL, LID_H = L.ZSK, L.ZR, L.ZF, L.WALL, L.LID_H
ZLT = ZR + LID_H - 0.016                                     # bottom of the lid panel (inside of the lid)
BX0, BX1, BY0, BY1, BZ, BT = L.BX0, L.BX1, L.BY0, L.BY1, L.BZ, L.BT
ZB = BZ - BT                                                 # bottom of the board
BRK_X = (-0.60, 0.60)                                        # board brackets
# tray with filters (left half): x0, x1, y0, y1, top of the bottom; a partition
TX0, TX1 = CX0 + WALL + 0.003, -0.03
TY0, TY1 = CY0 + WALL + 0.003, CY1 - WALL - 0.003
TZ = ZR - 0.115
TSPLIT = 0.13
# tarpaulin and cylinder (right half)
CANVAS = (0.0, CX1 - WALL - 0.004, CY0 + WALL + 0.004, CY1 - WALL - 0.004, ZF, ZF + 0.15)
TANK_R, TANK_L = 0.07, 0.535
TANK_O = Vector((0.005, 0.20, CANVAS[5] + TANK_R))           # center of the cylinder bottom, axis along +x

# module places: slot 1 - a rubber mat, 2 - a cork pad, 3 - a steel plate on bolts
MAT_T, PLATE_T = 0.004, 0.006
SLOT_Z = (BZ + MAT_T, BZ + MAT_T, BZ + PLATE_T)
MODS = [(x, L.MOD_Y, z) for x, z in zip(L.MOD_X, SLOT_Z)]
MOD_OBJ = [("m84_test_pump", "ozr_test_pump"), ("m85_gas_analyzer", "ozr_gas_analyzer"),
           ("m86_plate_clamp", "ozr_plate_clamp")]
# M84 hose tip from the module origin (build_m84.py: HOSE[-1], NOZ_Z, NOZ_DIR - via M25; the cone ends at 0.040 along the axis)
M84_NOZ = Vector((0.010, -0.0785, 0.0297))
M84_DIR = Vector((0.92, 0.39, 0.0)).normalized()
HOSE_R = 0.0065                                              # pressure test hose dia. 13, like M84

# mannequin: the head center (the widest place) and the bottom of the neck
HX, HY = L.HEAD_XY
HEAD_CZ = BZ + 0.326
NECK_Z = HEAD_CZ - 0.27

# compressor under the board on the right
CMX, CMY = L.COMP_XY[0], L.COMP_XY[1] - 0.07                 # pulled out from under the board forward
CTR, CTZ = 0.095, 0.135                                      # receiver: radius, axis
PLAT = (CMX - 0.14, CMX + 0.14, CMY - 0.105, CMY + 0.105, CTZ + CTR - 0.004, CTZ + CTR + 0.006)
PT = PLAT[5]                                                 # platform top
MOTOR = Vector((CMX - 0.03, CMY + 0.01, PT + 0.058))         # motor axis (along x)
MOT_X0, MOT_L, MOTOR_R = 0.287, 0.165, 0.058
FAN = Vector((0.270, MOTOR.y, MOTOR.z))                      # fan hub
FAN_R = 0.050
CYL = (CMX + 0.095, CMY + 0.01)                              # pump cylinder axis
SWB = (CMX + 0.015, CMX + 0.075, CMY - 0.102, CMY - 0.052, PT, PT + 0.072)   # relay box
MAN = (CMX + 0.08, CMX + 0.15, CMY - 0.095, CMY - 0.065, PT, PT + 0.040)    # brass block
GAUGE = Vector((CMX + 0.105, CMY - 0.105, PT + 0.032))       # gauge: the center of the back wall, the face toward -y
GAUGE_D = L.GAUGE_D
G_FACE = GAUGE.y - 0.0185                                    # dial plane
NEEDLE_Y = GAUGE.y - 0.0190                                  # needle (0.8 mm thick toward the face)
NEEDLE_L, A_ZERO, A_SPAN = 0.021, math.radians(225.0), math.radians(270.0)
WORK_P = 0.72                                                # "working": 7.2 bar out of 10
LAMP = Vector((CMX + 0.032, SWB[2], PT + 0.054))
COUPLER = Vector((MAN[1], (MAN[2] + MAN[3]) / 2, PT + 0.016))
HOSE_Y_R = 0.005                                             # yellow gun hose
# blow gun on the board: the inlet (fitting) at the edge, the grip deeper into the board, the nozzle to the left
GUN = g.Frame((0.612, -0.552, BZ + 0.011), (0, 1, 0), (-1, 0, 0), (0, 0, 1))

LOD_SPECS = [
    dict(lod=0, bev=1, sides=14),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "chest": ("paint_chest", 0.7), "lid_in": ("paint_lid", 1.0), "wood_in": ("wood_in", 0.6),
    "board": ("board", 0.9), "skid": ("skid", 0.6), "hw": ("hw", 1.2), "bracket": ("bracket", 1.2),
    "rubber": ("rubber", 0.5), "cork": ("cork", 0.8), "mount": ("mount", 1.4), "bolt": ("bolt", 2.0),
    "head": ("head", 1.4), "stand": ("black", 1.2), "pole": ("chrome", 1.6),
    "tank": ("tank", 1.0), "chrome": ("chrome", 1.6), "canvas": ("canvas", 0.6), "brass": ("brass", 1.6),
    "copper": ("copper", 1.6), "zinc": ("zinc", 1.6), "hose_hp": ("hose_hp", 1.2),
    "comp_red": ("comp_red", 1.4), "comp_black": ("comp_black", 1.4), "guard": ("guard", 1.6),
    "alu": ("alu", 1.6), "fan": ("fan", 1.6), "gauge_face": ("gauge_face", 4.0), "needle": ("needle", 2.0),
    "lamp": ("lamp_off", 2.0), "hose": ("hose", 1.4), "cable": ("cable", 1.2), "toggle": ("cap_red", 1.6),
}

# =============================================================================
# Materials
# =============================================================================


def build_scuffed(mat, origin, color, bare=kmats.lin((112, 112, 116)), seed=1.0, gloss=0.32, spec=0.25,
                  wear=(0.66, 0.71), edge_k=0.7, rub=(), stripes=(), scratch=0.0, oil=0.0, floor_z=0.0,
                  dust=0.3, grime=0.3, decal_items=()):
    """Scuffed, careless paint without rust - a copy of build_scuffed from M27: decals go over the wear.
    Rubbed to bare on the edges (edge_k) and where hands take it (rub - [(center, semi-axes, strength)]);
    scratches along x, oil spots on top (oil); stripes of another color - stripes
    [((x0, x1, y0, y1, z0, z1), color)] in model coordinates."""
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
        base = t.mixc(inside, base, tuple(c * 0.9 for c in scol[:3]) + (1,))
        base = t.mixc(t.math("MULTIPLY", inside, t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0)),
                      base, scol)
    col = base
    edge = t.maprange(t.edge_wear(0.004), 0.05, 0.22, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 11.0, 10.0, 0.7), 0.75), t.math("MULTIPLY", edge, edge_k))
    grain = t.maprange(t.noise(vec, 34.0, 8.0, 0.7), 0.3, 0.7, 0.55, 1.0)
    for c, r, k in rub:
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
        near = t.maprange(ln.outputs["Value"], 0.25, 1.0, 1.0, 0.0)
        f = t.math("ADD", f, t.math("MULTIPLY", t.math("MULTIPLY", near, grain), k))
    worn = t.step(f, wear[0], wear[1])
    brush = t.noise(t.stretch(vec, 0.04, 1.0, 1.0), 90.0, 4.0, 0.7)
    metal = t.mixc(t.maprange(brush, 0.3, 0.7, 0.0, 1.0), tuple(c * 0.75 for c in bare[:3]) + (1,),
                   tuple(min(1.0, c * 1.15) for c in bare[:3]) + (1,))
    rim = t.math("SUBTRACT", t.step(f, wear[0] - 0.05, wear[0]), worn)
    col = t.mixc(t.math("MULTIPLY", rim, 0.6), col, kmats.lin((52, 50, 46)))
    col = t.mixc(worn, col, metal)
    h = t.math("MULTIPLY", worn, -0.3)
    g_ = t.math("ADD", gloss, t.math("MULTIPLY", worn, 0.62 - gloss))
    s_ = t.math("ADD", spec, t.math("MULTIPLY", worn, 0.70 - spec))
    if scratch > 0:
        sc = t.step(t.noise(t.stretch(vec, 0.02, 1.0, 1.0), 260.0, 2.0, 0.5), 0.70, 0.73)
        sc = t.math("MULTIPLY", sc, t.maprange(t.noise(vec, 5.0, 4.0, 0.5), 0.35, 0.65, 0.0, scratch))
        col = t.mixc(t.math("MULTIPLY", sc, 0.7), col, metal)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", sc, 0.15))
    col = kmats.decals(t, col, sep, nsep, decal_items)
    if oil > 0:
        up = t.maprange(nsep.outputs["Z"], 0.5, 0.9, 0.0, 1.0)
        ol = t.math("MULTIPLY", t.step(t.noise(vec, 4.0, 6.0, 0.6), 0.62, 0.70), t.math("MULTIPLY", up, oil))
        col = t.mixc(t.math("MULTIPLY", ol, 0.55), col, kmats.lin((14, 12, 10)))
        g_ = t.math("ADD", g_, t.math("MULTIPLY", ol, 0.25))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g_, s_, h)


def decal_y(name, x0, x1, z0, z1, ya, yb=None):
    """Decal facing -y, only on faces with y in ya..yb (by default, on the face at depth ya)."""
    rng = (ya - 0.002, ya + 0.002) if yb is None else (ya, yb)
    return (os.path.join(WORK, name), "y", -1, ("x", "z"), ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0), rng)


def decal_x(name, y0, y1, z0, z1, x, sign):
    """Decal on an end: facing +x (sign 1) or -x (-1; the picture is mirrored in make_decals)."""
    return (os.path.join(WORK, name), "x", sign, ("y", "z"), ((y0 + y1) / 2, (z0 + z1) / 2), (y1 - y0, z1 - z0),
            (x - 0.002, x + 0.002))


def lid_in_decal():
    x0, x1, d0, d1 = L.LID_IN
    ys = [L.lid_point(y, ZLT)[0] for y in (CY0, CY1)]
    za, zb = L.lid_point(CY1 - d0, ZLT)[1], L.lid_point(CY1 - d1, ZLT)[1]
    return decal_y("decal_lid.png", x0, x1, za, zb, min(ys) - 0.004, max(ys) + 0.004)


GREEN = kmats.lin((62, 152, 44))
WOOD = kmats.lin((150, 112, 70))
y0_, y1_, z0_, z1_ = L.END_R
END_DECALS = [decal_x("decal_end_r.png", y0_, y1_, z0_, z1_, CX1, 1),
              decal_x("decal_end_l.png", y0_, y1_, z0_, z1_, CX0, -1)]
x0_, x1_, z0_, z1_ = L.FRONT
FRONT_DECAL = decal_y("decal_front.png", x0_, x1_, z0_, z1_, CY0)
TANK_DECAL = decal_y("decal_tank.png", CMX - 0.11, CMX + 0.11, CTZ - 0.05, CTZ + 0.05, CMY - CTR - 0.005, CMY - 0.05)
GAUGE_DECAL = decal_y("decal_gauge.png", GAUGE.x - GAUGE_D / 2, GAUGE.x + GAUGE_D / 2, GAUGE.z - GAUGE_D / 2,
                      GAUGE.z + GAUGE_D / 2, G_FACE)
# worn at the handles on the ends and at the rim where the lid is taken
CHEST_RUB = [((s * CX1, (CY0 + CY1) / 2, ZR - 0.10), (0.05, 0.14, 0.08), 0.35) for s in (-1, 1)]

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "paint_chest": (build_scuffed, dict(color=GREEN, bare=WOOD, seed=2.5, wear=(0.67, 0.72), edge_k=0.85,
                                        rub=CHEST_RUB, scratch=0.5, dust=0.35, grime=0.35,
                                        decal_items=END_DECALS + [FRONT_DECAL])),
    "paint_lid": (build_scuffed, dict(color=GREEN, bare=WOOD, seed=3.1, wear=(0.69, 0.74), edge_k=0.8,
                                      scratch=0.3, dust=0.15, grime=0.2, decal_items=[lid_in_decal()])),
    "wood_in": (kwood.build_wood, dict(color=kmats.lin((176, 140, 96)), seed=4.1, along="x", floor_z=ZF, dust=0.4,
                                       grime=0.45)),
    "board": (kwood.build_wood, dict(color=kmats.lin((168, 128, 84)), seed=4.7, along="x", floor_z=ZB, dust=0.3,
                                     grime=0.3, knots=0.3)),
    "skid": (kwood.build_wood, dict(color=kmats.lin((112, 84, 56)), seed=5.3, along="x", dust=0.2, grime=0.7)),
    "hw": ("steel", dict(seed=6.1, tone=0.20, along="z", gloss=0.45, spec=0.55, dust=0.3, grime=0.4)),
    "bracket": (build_scuffed, dict(color=kmats.lin((30, 30, 32)), bare=kmats.lin((120, 120, 124)), seed=6.7,
                                    wear=(0.70, 0.76), edge_k=0.8, dust=0.3, grime=0.3)),
    # module places: a cork under the gas analyzer, the steel plate of the clamp (worn at the bolts, oil)
    "cork": ("plastic", dict(color=kmats.lin((150, 112, 72)), gloss=0.05, spec=0.03, mottle=0.35, floor_z=BZ,
                             dust=0.25, grime=0.35, scuff=(0.8, 0.9))),
    "mount": (build_scuffed, dict(color=kmats.lin((44, 46, 48)), bare=kmats.lin((120, 120, 124)), seed=7.1,
                                  wear=(0.60, 0.66), edge_k=1.0, scratch=0.8, oil=0.4, floor_z=BZ, dust=0.1,
                                  grime=0.4)),
    "bolt": ("steel", dict(seed=7.4, tone=0.24, along="z", gloss=0.45, spec=0.55, floor_z=BZ, dust=0.1, grime=0.5)),
    # mannequin: light plastic, handled at the neck
    "head": ("plastic", dict(color=kmats.lin((224, 216, 202)), gloss=0.3, spec=0.2, mottle=0.08, dust=0.25,
                             grime=0.3, scuff=(0.7, 0.8))),
    "tank": (build_scuffed, dict(color=kmats.lin((28, 28, 30)), bare=kmats.lin((120, 120, 124)), seed=9.1,
                                 gloss=0.45, wear=(0.70, 0.76), edge_k=0.6, dust=0.3, grime=0.2,
                                 stripes=[((TANK_O.x + TANK_L - 0.09, TANK_O.x + TANK_L, -1, 1, -1, 2),
                                           kmats.lin((190, 190, 186)))])),
    "chrome": ("steel", dict(seed=9.5, tone=0.34, along="x", gloss=0.75, spec=0.85, dust=0.1, grime=0.2)),
    "canvas": ("plastic", dict(color=kmats.lin((70, 84, 100)), gloss=0.06, spec=0.04, mottle=0.25, dust=0.4,
                               grime=0.4, scuff=(0.8, 0.9))),
    "brass": ("paint", dict(color=kmats.lin((146, 114, 62)), under=kmats.lin((184, 148, 82)), seed=10.0, gloss=0.42,
                            spec=0.5, chip=(0.62, 0.70), rust=(0.99, 1.0), rust_low=0.0, dust=0.25, grime=0.6)),
    "copper": ("paint", dict(color=kmats.lin((140, 86, 56)), under=kmats.lin((176, 108, 70)), seed=10.6, gloss=0.40,
                             spec=0.45, chip=(0.7, 0.8), rust=(0.99, 1.0), rust_low=0.0, dust=0.25, grime=0.6)),
    "zinc": ("steel", dict(seed=10.9, tone=0.40, along="x", gloss=0.45, spec=0.5, dust=0.1, grime=0.3)),
    # pressure test hose - black rubber, like M84
    "hose_hp": ("plastic", dict(color=kmats.lin((30, 30, 31)), gloss=0.20, spec=0.10, dust=0.15, grime=0.2)),
    # compressor: a red receiver with decals, a black motor, an aluminum block
    "comp_red": (build_scuffed, dict(color=kmats.lin((168, 34, 28)), bare=kmats.lin((110, 110, 112)), seed=11.3,
                                     gloss=0.45, wear=(0.69, 0.75), edge_k=0.6, scratch=0.4, dust=0.35,
                                     grime=0.45, decal_items=[TANK_DECAL])),
    "comp_black": ("plastic", dict(color=kmats.lin((26, 26, 27)), gloss=0.35, spec=0.25, dust=0.35)),
    "guard": ("plastic", dict(color=kmats.lin((22, 22, 23)), gloss=0.3, spec=0.25, dust=0.4)),
    "alu": ("steel", dict(seed=11.9, tone=0.40, along="z", gloss=0.4, spec=0.5, dust=0.3, grime=0.5)),
    "fan": ("plastic", dict(color=kmats.lin((36, 36, 38)), gloss=0.3, spec=0.2, dust=0.4)),
    "gauge_face": (build_scuffed, dict(color=kmats.lin((228, 226, 216)), seed=12.3, gloss=0.6, spec=0.5,
                                       wear=(0.99, 1.0), edge_k=0.0, dust=0.1, grime=0.0,
                                       decal_items=[GAUGE_DECAL])),
    "needle": ("flat", dict(color=kmats.lin((150, 26, 20)), gloss=0.5, spec=0.35)),
    "lamp_off": ("flat", dict(color=kmats.lin((120, 58, 18)), gloss=0.85, spec=0.8)),
    "lamp_on": ("flat", dict(color=kmats.lin((255, 160, 40)), gloss=0.85, spec=0.8)),
    "hose": ("plastic", dict(color=kmats.lin((218, 176, 32)), gloss=0.45, spec=0.3, dust=0.3, grime=0.3)),
    "cable": ("plastic", dict(color=kmats.lin((24, 24, 24)), gloss=0.35, spec=0.25, dust=0.3)),
})

OBJ, NAME = "m29_frd_pack_prot", "ozr_frd_pack_prot"


# =============================================================================
# GP-5 on the mannequin: the worn DayZ model GP5GasMask_m (a proxy) - as on a player's head, without rotation
# =============================================================================
# The worn model, not the ground GP5GasMask_g: the ground mask is crumpled rubber lying on its side (the
# head thickness ~10 cm against ~20 for the worn one), and its filter slot is rotated about its own axis
# by ~100 degrees differently than in the worn one, so a rotation computed from the slot proxies of the
# two models hung the mask sideways. The worn model is the one DayZ draws on a player's head: +Y is up,
# the face is at -Z, the origin is at the feet, the mask at a height of 1.52-1.80. Its proxy is placed
# by a shift: the point HC_M of the worn model goes to the head center of the mannequin; it is rotated
# only about the vertical (HEAD_DEG).
GP5_M = r"\dz\characters\masks\GP5GasMask_m"
# filter slot of the worn model (the near LOD header, like kvanilla.box): rows are the X, Y, Z axes of the
# filter in mask axes, then the origin - the filter bottom; the GP5GasMask_filter from the bottom to the neck is 0.0799 along +Y
F_M = ((1.0, 0.0, 0.0), (0.0, 0.88373, 0.46799), (0.0, -0.46799, 0.88373), (-0.0001, 1.47915, -0.21021))
FILTER_H = 0.0799
# the mask itself (the near LOD without the filter proxy triangle - it inflates the bottom of the extent in the header to 1.409)
GP5_M_BOX = ((-0.099, 1.523, -0.199), (0.099, 1.804, 0.102))
# head center under the mask: on the axis x = 0, z = -0.02, at eye level
HC_M = (0.0, 1.68, -0.02)


def _n(v):
    """Axes of the worn model -> Blender: +X -> +X, +Y (up) -> +Z, +Z (back of the head) -> +Y, and a
    rotation about the vertical by HEAD_DEG to the left - facing forward and toward the pressure tester."""
    q = Vector((v[0], v[2], v[1]))
    return Matrix.Rotation(math.radians(-L.HEAD_DEG), 3, "Z") @ q


def gp5_pose(anchor_m, anchor_b):
    """Proxy of the worn model: origin, "up" and "forward" (kexport.proxy_points), so that the model point
    anchor_m lands at anchor_b; the function of a model point -> Blender, the filter neck (the hose adapter
    goes here) and the thread axis outward, the mask face."""
    origin = Vector(anchor_b) - _n(Vector(anchor_m))

    def at(p_m):
        return origin + _n(Vector(p_m))
    neck_m = Vector(F_M[3]) + Vector(F_M[1]) * FILTER_H
    return dict(origin=origin, up=_n((0.0, 1.0, 0.0)), fwd=_n((0.0, 0.0, 1.0)), at=at, neck=at(neck_m),
                axis=_n(-Vector(F_M[1])).normalized(), face=_n(Vector((0.0, 0.0, -1.0))).normalized())


GP5 = gp5_pose(HC_M, (HX, HY, HEAD_CZ))
GP5_CORNERS = [GP5["at"]((x, y, z)) for x in (GP5_M_BOX[0][0], GP5_M_BOX[1][0])
               for y in (GP5_M_BOX[0][1], GP5_M_BOX[1][1]) for z in (GP5_M_BOX[0][2], GP5_M_BOX[1][2])]
# head of the mannequin under the mask - sections in worn-model axes from bottom to top: (height y,
# half-width, forward from the axis x = 0, z = -0.02, backward); a superellipse with exponent 2. The
# neck is round, 2 cm behind the axis: it passes into the lower cutout of the mask behind the chin. The
# head fills the mask like a player's head: behind the lenses it is visible instead of emptiness;
# 4-15 mm from the mask (checked against the points of the near, mid and far LODs of the mask, and
# between the sections too)
HEAD_RINGS = [
    (1.410, 0.030, 0.010, 0.050), (1.416, 0.040, 0.020, 0.060), (1.430, 0.043, 0.023, 0.063),
    (1.500, 0.041, 0.021, 0.061), (1.550, 0.041, 0.021, 0.061), (1.565, 0.044, 0.034, 0.058),
    (1.580, 0.047, 0.058, 0.050), (1.600, 0.057, 0.070, 0.060), (1.620, 0.065, 0.077, 0.076),
    (1.640, 0.070, 0.080, 0.092), (1.660, 0.072, 0.079, 0.100), (1.680, 0.074, 0.081, 0.104),
    (1.700, 0.074, 0.080, 0.104), (1.720, 0.074, 0.072, 0.103), (1.730, 0.073, 0.067, 0.101),
    (1.740, 0.071, 0.063, 0.098), (1.750, 0.068, 0.060, 0.093), (1.760, 0.063, 0.056, 0.085),
    (1.770, 0.055, 0.049, 0.074), (1.780, 0.044, 0.037, 0.059), (1.788, 0.026, 0.023, 0.036),
]
HEAD_POLES = (1.407, 1.7925)                                 # bottom of the neck and the crown - vertices on the axis
HEAD_SEL = (tuple(range(len(HEAD_RINGS))), (0, 2, 3, 5, 6, 8, 10, 11, 13, 15, 17, 19, 20),
            (0, 2, 5, 7, 10, 12, 15, 18, 20))
HEAD_ZC = HC_M[2]
STAND_XY = tuple(GP5["at"]((0.0, HEAD_POLES[0], HEAD_ZC + (HEAD_RINGS[0][3] - HEAD_RINGS[0][2]) / 2)))[:2]

# Working look: the relay lamp is ozl_lamp (in hiddenSelections, _on atlas); the fan is the bone ozl_fan
# on the source ozl_work (a loop), the gauge needle is the bone ozl_needle (wobble around 7.2 bar)
SEL_LAMP, SEL_FAN, SEL_NEEDLE = "ozl_lamp", "ozl_fan", "ozl_needle"
FAN_TURNS = 2                                                # turns per source pass
G.install_pose()
# "working" preview: the needle at 7.2 bar, the fan rotated (does not go into the p3d - that is model.cfg)
ON = dict(remap={"lamp_off": "lamp_on"}, emissive=(1.0, 1.0, 1.0, 1.0),
          move={SEL_NEEDLE: G.rot_about((GAUGE.x, 0.0, GAUGE.z), (0.0, 1.0, 0.0), A_SPAN * WORK_P),
                SEL_FAN: G.rot_about(FAN, (1.0, 0.0, 0.0), math.radians(30.0))})
FAN_ANIM = ("ozl_work_fan", dict(type="rotation", source="ozl_work", sourceAddress="loop", selection=SEL_FAN,
                                 axis="ozl_fan_axis", memory=1, minValue=0.0, maxValue=1.0 / FAN_TURNS, angle0=0.0,
                                 angle1=2 * math.pi))
# needle - axis toward the face (-Y Blender), clockwise is positive (as in M84, M14, M33)
NEEDLE_ANIM = ("ozl_needle_rot", dict(type="rotation", source="ozl_needle", selection=SEL_NEEDLE,
                                      axis="ozl_needle_axis", memory=1, minValue=0.0, maxValue=1.0, angle0=0.0,
                                      angle1=A_SPAN))
# module proxies: the slots OZL_Tool1..3 are linked to them by CfgNonAIVehicles of the mod (Proxyozl_tool1..3);
# slot N is module N of the "Protection" line (M84, M85, M86), without rotation: the modules face the person
PROXIES = [(r"\OpenZone_Research\models\proxies\ozl_tool%d" % (i + 1), m) for i, m in enumerate(MODS)]
PASGT = r"dz\characters\headgear\pasgt_g"
SODA = r"dz\gear\drinks\SodaCan"
FILT_TRAY = [(-0.515, -0.072), (-0.388, -0.068), (-0.262, -0.075), (-0.512, 0.056), (-0.386, 0.058)]
DECOR = [
    # on the mannequin a GP-5 gas mask is worn (the worn model, pose - gp5_pose), the filter is unscrewed
    # and stands on the board; the mask is also in the far LOD - otherwise a bare mannequin is visible from
    # afar. kvanilla does not read the extent of the worn one (it is at a height of 1.5-1.8 from its
    # origin) - the preview box is from GP5_M_BOX, the key is own
    (GP5_M, tuple(GP5["origin"]), tuple(GP5["up"]), tuple(GP5["fwd"]), (0, 1, 2), "gp5_m"),
    kv.put("gp5filter", (-0.235, -0.505, BZ), up=(0, 0, 1), fwd=(0.3, -1, 0)),
    # PASGT helmet (BallisticHelmet) across the board between the gas analyzer and the clamp
    kv.put(PASGT, (L.HELM_XY[0] + 0.01, L.HELM_XY[1] + 0.005, BZ), up=(0, 0, 1), fwd=(1, 0.1, 0)),
    # at the board edge: a screwdriver, pliers (hose clamps)
    kv.put("screwdriver", (0.0, -0.530, BZ), **kv.flat(4)),
    kv.put("pliers", (0.25, -0.532, BZ), **kv.flat(-8)),
    # in the tray: five GP-5 filters (the sixth place is empty - that filter is on the board), an adjustable
    # wrench; behind the partition tape, a "Pipsi" can, rags
] + [kv.put("gp5filter", (x, y, TZ), up=(0, 0, 1), fwd=(math.sin(k * 1.3) * 0.4, -1, 0))
     for k, (x, y) in enumerate(FILT_TRAY)] + [
    kv.put("wrench", (-0.115, -0.012, TZ), **kv.flat(78)),
    kv.put("ducttape", (-0.50, 0.29, TZ), **kv.flat(0)),
    kv.put(SODA, (-0.385, 0.215, TZ), up=(0, 0, 1), fwd=(0.2, -1, 0)),
    kv.put("rags", (-0.19, 0.275, TZ), **kv.flat(3)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 selections=(SEL_LAMP, SEL_FAN, SEL_NEEDLE), hidden=(SEL_LAMP,), states={"on": ON},
                 bones=((SEL_FAN, ""), (SEL_NEEDLE, "")), animations=(FAN_ANIM, NEEDLE_ANIM), proxies=PROXIES,
                 decor=DECOR, modules=[(o, n, m) for (o, n), m in zip(MOD_OBJ, MODS)],
                 sources={"ozl_work": dict(animPeriod=1.0), "ozl_needle": dict(animPeriod=0.2)})
P = M.part
BOUNDS = {}


def gp5_standin():
    """The blue GP-5 box in the preview is the extent of the worn mask (GP5_M_BOX), rotated like the mask."""
    import bpy
    bm = bmesh.new()
    vs = [bm.verts.new(tuple(p)) for p in GP5_CORNERS]
    for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
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
    krender.standins([d for d in M.lod0_decor() if d[5] != "gp5_m"])
    gp5_standin()
    for obj, name, at in M.modules if with_modules else ():
        krender.our_model(obj, name, at)


M.place_extras = place_extras


# =============================================================================
# Small helpers
# =============================================================================
def lidify(parts):
    """Lid parts built closed - into the open position (rotation about the hinge axis)."""
    for p in parts:
        for v in p.bm.verts:
            v.co.y, v.co.z = L.lid_point(v.co.y, v.co.z)
        p.bm.normal_update()


def retag(part, faces, region, inside):
    """Faces for which inside(center, normal) holds are moved into the given region (the inside of the chest and the lid)."""
    idx = part.region_index(region, *REGIONS[region])
    for f in faces:
        if f.is_valid and inside(f.calc_center_median(), f.normal):
            f[part.reg] = idx


def corner_cap(part, rv, x, y, z, sx, sy, sz, c=0.045, t=0.0018, top=True):
    """A steel angle at the corner (x, y, z) of a box: plates c x c of thickness t outside faces x and y
    (and z, if top); sx, sy, sz - where the corner looks outward. The plates do not overlap. rv - the
    rivet part (None - without them)."""
    def rng(a, s, d0, d1):
        return tuple(sorted((a + s * d0, a + s * d1)))
    g.box(part, *rng(x, sx, 0.0, t), *rng(y, sy, -c, t), *rng(z, sz, -c, 0.0))
    g.box(part, *rng(x, sx, -c, 0.0), *rng(y, sy, 0.0, t), *rng(z, sz, -c, 0.0))
    if top:
        g.box(part, *rng(x, sx, -c, t), *rng(y, sy, -c, t), *rng(z, sz, 0.0, t))
    if rv is not None:
        G.rivet(rv, (x + sx * t, y - sy * c * 0.5, z - sz * c * 0.5), (sx, 0, 0), r=0.0042, h=0.0022, sides=5)
        G.rivet(rv, (x - sx * c * 0.5, y + sy * t, z - sz * c * 0.5), (0, sy, 0), r=0.0042, h=0.0022, sides=5)


# =============================================================================
# Chest: body, lid, trim
# =============================================================================
def build_chest(spec):
    lod = spec["lod"]
    r, sg = (0.004, 1) if lod == 0 else (0.0, 0)
    ch = P("chest", "chest")
    ctr = Vector(((CX0 + CX1) / 2, (CY0 + CY1) / 2, (ZF + ZR) / 2))

    def inner(c, n):
        return (CX0 + WALL - 1e-3 < c.x < CX1 - WALL + 1e-3 and CY0 + WALL - 1e-3 < c.y < CY1 - WALL + 1e-3
                and c.z < ZR - 1e-3 and n.dot(ctr - c) > 0)
    faces = []
    faces += g.box(ch, CX0, CX1, CY0, CY0 + WALL, ZSK, ZR, r, sg)                  # face
    faces += g.box(ch, CX0, CX1, CY1 - WALL, CY1, ZSK, ZR, r, sg)                  # back
    for x0, x1 in ((CX0, CX0 + WALL), (CX1 - WALL, CX1)):                          # ends
        faces += g.box(ch, x0, x1, CY0 + WALL, CY1 - WALL, ZSK, ZR, r, sg)
    faces += g.box(ch, CX0 + WALL, CX1 - WALL, CY0 + WALL, CY1 - WALL, ZSK, ZF)    # bottom
    if lod < 2:
        # battens for the tray at the end and at the tray partition, inside
        for x0, x1 in ((CX0 + WALL, CX0 + WALL + 0.012), (TX1 + 0.002, TX1 + 0.014)):
            faces += g.box(ch, x0, x1, CY0 + WALL, CY1 - WALL, TZ - 0.03, TZ - 0.008)
    retag(ch, faces, "wood_in", inner)
    parts = [ch]
    if lod < 2:
        sk = P("skids", "skid")
        for y in (CY0 + 0.07, CY1 - 0.07):
            g.box(sk, CX0 + 0.03, CX1 - 0.03, y - 0.03, y + 0.03, 0.0, ZSK, **(dict(r=0.004, seg=1) if lod == 0 else {}))
        parts.append(sk)
    # lid: a panel and a rim, built closed, then thrown open
    ld = P("lid", "chest")
    lc = Vector(((CX0 + CX1) / 2, (CY0 + CY1) / 2, ZR + 0.02))

    def lid_inner(c, n):
        return c.z < ZLT + 1e-3 and n.dot(lc - c) > 0
    faces = g.box(ld, CX0, CX1, CY0, CY1, ZLT, ZR + LID_H, r, sg)
    faces += g.box(ld, CX0, CX1, CY0, CY0 + WALL, ZR, ZLT)
    faces += g.box(ld, CX0, CX1, CY1 - WALL, CY1, ZR, ZLT)
    for x0, x1 in ((CX0, CX0 + WALL), (CX1 - WALL, CX1)):
        faces += g.box(ld, x0, x1, CY0 + WALL, CY1 - WALL, ZR, ZLT)
    retag(ld, faces, "lid_in", lid_inner)
    lid_parts = [ld]
    hw = P("hardware", "hw")
    hl = P("lid_hardware", "hw")
    rv = P("rivets", "hw") if lod == 0 else None
    rl = P("lid_rivets", "hw") if lod == 0 else None
    if lod == 0:
        # rolled edge trim: a steel strap along the top of the body and the bottom of the lid
        t, h = 0.0015, 0.020
        for a, zz in ((hw, (ZR - h - 0.002, ZR - 0.002)), (hl, (ZR + 0.002, ZR + 0.002 + h))):
            g.box(a, CX0 - t, CX1 + t, CY0 - t, CY0, *zz)
            g.box(a, CX0 - t, CX1 + t, CY1, CY1 + t, *zz)
            g.box(a, CX0 - t, CX0, CY0, CY1, *zz)
            g.box(a, CX1, CX1 + t, CY0, CY1, *zz)
        # riveted angles: the bottom and top of the body, four corners of the lid
        for x in (CX0, CX1):
            for y in (CY0, CY1):
                sx, sy = (-1 if x == CX0 else 1), (-1 if y == CY0 else 1)
                corner_cap(hw, rv, x, y, ZSK, sx, sy, -1)
                corner_cap(hw, rv, x, y, ZR, sx, sy, 1, top=False)
                corner_cap(hl, rl, x, y, ZR + LID_H, sx, sy, 1)
    elif lod == 1:
        for x in (CX0, CX1):
            for y in (CY0, CY1):
                sx, sy = (-1 if x == CX0 else 1), (-1 if y == CY0 else 1)
                corner_cap(hw, None, x, y, ZSK, sx, sy, -1, c=0.05, t=0.002)
                corner_cap(hl, None, x, y, ZR + LID_H, sx, sy, 1, c=0.05, t=0.002)
    # hinges at the back: a pivot, a leaf on the back, a leaf on the lid
    for x in ((-0.40, 0.40) if lod < 2 else ()):
        G.lathe(hw, [(0.0075, -0.05), (0.0075, 0.05)], 12 if lod == 0 else 6, (x, CY1 + 0.008, ZR), "x",
                caps=(True, True))
        g.box(hw, x - 0.045, x + 0.045, CY1, CY1 + 0.003, ZR - 0.095, ZR - 0.006)
        g.box(hl, x - 0.045, x + 0.045, CY1 - 0.13, CY1 - 0.006, ZR + LID_H, ZR + LID_H + 0.003)
        if lod == 0:
            for dx in (-0.028, 0.0, 0.028):
                G.rivet(rv, (x + dx, CY1 + 0.003, ZR - 0.06), (0, 1, 0), r=0.004, h=0.002, sides=5)
                G.rivet(rl, (x + dx, CY1 - 0.08, ZR + LID_H + 0.003), (0, 0, 1), r=0.004, h=0.002, sides=5)
    if lod == 0:
        # lock plate on the lid and a lug
        G.slab(hl, -0.035, 0.035, ZR + 0.008, ZR + LID_H - 0.006, -0.0035, 0.0, rc=0.008, nc=2,
               frame=g.Frame((0.0, CY0, 0.0), (1, 0, 0), (0, 0, 1), (0, -1, 0)))
        for dx in (-0.02, 0.02):
            G.rivet(rl, (dx, CY0 - 0.0035, ZR + LID_H - 0.02), (0, -1, 0), r=0.004, h=0.002, sides=5)
        g.pipe(hl, G.fillet([(-0.012, CY0 - 0.0035, ZR + 0.014), (-0.012, CY0 - 0.018, ZR + 0.014),
                             (0.012, CY0 - 0.018, ZR + 0.014), (0.012, CY0 - 0.0035, ZR + 0.014)], 0.006, 3), 0.0028, 6)
        # bar handles on the ends: two riveted lugs, the bail hangs, a rubber grip on it
        rb = P("handle_grips", "rubber")
        for s in (-1, 1):
            x = s * CX1
            zc = ZR - 0.10
            yc = (CY0 + CY1) / 2
            for dy in (-0.065, 0.065):
                g.box(hw, *sorted((x, x + s * 0.004)), yc + dy - 0.014, yc + dy + 0.014, zc - 0.03, zc + 0.012)
                G.rivet(rv, (x + s * 0.004, yc + dy, zc - 0.018), (s, 0, 0), r=0.004, h=0.002, sides=5)
                G.lathe(hw, [(0.0085, -0.007), (0.0085, 0.007)], 8, (x + s * 0.010, yc + dy, zc + 0.002), "y",
                        caps=(True, True))
            pts = [(x + s * 0.010, yc - 0.065, zc + 0.002), (x + s * 0.016, yc - 0.065, zc - 0.068),
                   (x + s * 0.016, yc + 0.065, zc - 0.068), (x + s * 0.010, yc + 0.065, zc + 0.002)]
            g.pipe(hw, G.fillet(pts, 0.018, 4), 0.0055, 8)
            G.lathe(rb, [(0.010, -0.045), (0.0115, -0.04), (0.0115, 0.04), (0.010, 0.045)], 10,
                    (x + s * 0.016, yc, zc - 0.068), "y", caps=(True, True))
        parts.append(rb)
    lid_parts.append(hl)
    if rl is not None:
        lid_parts.append(rl)
    lidify(lid_parts)
    parts += lid_parts + [hw] + ([rv] if rv is not None else [])
    if lod < 2:
        # lid chain stay at the left end: lugs on the body and on the lid
        a = Vector((CX0 + WALL + 0.012, CY1 - 0.20, ZR - 0.05))
        b = Vector((CX0 + WALL + 0.012,) + L.lid_point(CY1 - 0.22, ZLT - 0.008))
        ca = P("lid_chain", "hw")
        kcabinet.chain(ca, a, b, lod, pitch=0.028, wire=0.0022)
        if lod == 0:
            g.box(ca, CX0 + WALL, CX0 + WALL + 0.004, a.y - 0.015, a.y + 0.015, a.z - 0.02, a.z + 0.01)
        parts.append(ca)
    return parts


# =============================================================================
# Folding board on folding brackets, module places
# =============================================================================
def build_board(spec):
    lod = spec["lod"]
    bd = P("board", "board")
    if lod == 0:
        G.slab(bd, BX0, BX1, BY0, BY1, ZB, BZ, rc=0.015, nc=2, re=0.003, ne=1, rb=0.002, nb=1)
    else:
        g.box(bd, BX0, BX1, BY0, BY1, ZB, BZ)
    parts = [bd]
    br = P("brackets", "bracket")
    for x in BRK_X:
        if lod == 2:
            g.box(br, x - 0.015, x + 0.015, CY0 - 0.006, CY0, 0.16, ZB)
            continue
        if lod == 1:
            g.box(br, x - 0.015, x + 0.015, CY0 - 0.006, CY0, 0.16, ZB)
            g.box(br, x - 0.015, x + 0.015, BY0 + 0.04, CY0 - 0.006, ZB - 0.006, ZB)
            G.bar(br, (x, CY0 - 0.01, 0.20), (x, BY0 + 0.12, ZB - 0.01), 0.018, 0.004, up=(1, 0, 0))
            continue
        # 30 x 25 angle on the chest and under the board, a folding brace on pivots
        g.box(br, x - 0.015, x + 0.015, CY0 - 0.003, CY0, 0.16, ZB)
        g.box(br, x - 0.0015, x + 0.0015, CY0 - 0.025, CY0 - 0.003, 0.16, ZB - 0.003)
        g.box(br, x - 0.015, x + 0.015, BY0 + 0.04, CY0 - 0.003, ZB - 0.003, ZB)
        g.box(br, x - 0.0015, x + 0.0015, BY0 + 0.04, CY0 - 0.025, ZB - 0.025, ZB - 0.003)
        a, b = Vector((x + 0.004, CY0 - 0.016, 0.20)), Vector((x + 0.004, BY0 + 0.12, ZB - 0.016))
        m = (a + b) / 2
        G.bar(br, a, m + (b - a).normalized() * 0.006, 0.018, 0.004, up=(1, 0, 0))
        G.bar(br, m - (b - a).normalized() * 0.006, b, 0.018, 0.004, up=(1, 0, 0))
        for p in (a, m, b):
            G.lathe(br, [(0.0055, -0.006), (0.0055, 0.006)], 8, p, "x", caps=(True, True))
        for z in (0.20, 0.30, 0.38):
            G.rivet(br, (x, CY0 - 0.003, z), (0, -1, 0), r=0.0045, h=0.002, sides=6)
    parts.append(br)
    if lod == 0:
        # board hinges to the chest face
        hg = P("board_hinges", "hw")
        for x in (-0.30, 0.30):
            g.box(hg, x - 0.05, x + 0.05, CY0 - 0.003, CY0, ZB - 0.035, ZB)
            G.lathe(hg, [(0.005, -0.05), (0.005, 0.05)], 8, (x, CY0 - 0.006, ZB), "x", caps=(True, True))
            for dx in (-0.03, 0.03):
                G.rivet(hg, (x + dx, CY0 - 0.003, ZB - 0.018), (0, -1, 0), r=0.004, h=0.002, sides=5)
        parts.append(hg)
    if lod == 2:
        return parts
    # slot 1 - a rubber mat for the pressure tester, slot 2 - a cork pad for the gas analyzer, slot 3 - a
    # steel plate on four bolts for the plate clamp
    (x1, y1, _), (x2, y2, _), (x3, y3, _) = MODS
    h = PAD = L.PAD
    mt = P("slot1_mat", "rubber")
    G.slab(mt, x1 - h / 2, x1 + h / 2, y1 - h / 2, y1 + h / 2, BZ, BZ + MAT_T,
           **(dict(rc=0.012, nc=2, re=0.0015, ne=1) if lod == 0 else {}))
    ck = P("slot2_cork", "cork")
    G.slab(ck, x2 - 0.10, x2 + 0.10, y2 - 0.10, y2 + 0.10, BZ, BZ + MAT_T,
           **(dict(rc=0.005, nc=1) if lod == 0 else {}))
    pl = P("slot3_plate", "mount")
    G.slab(pl, x3 - 0.09, x3 + 0.09, y3 - 0.075, y3 + 0.075, BZ, BZ + PLATE_T,
           **(dict(rc=0.008, nc=2, re=0.0015, ne=1) if lod == 0 else {}))
    parts += [mt, ck, pl]
    if lod == 0:
        bt = P("slot3_bolts", "bolt")
        for sx in (-1, 1):
            for sy in (-1, 1):
                c = Vector((x3 + sx * 0.072, y3 + sy * 0.057, BZ + PLATE_T))
                G.lathe(bt, [(0.0095, 0.0), (0.0095, 0.0012)], 12, c, "z", caps=(False, True))     # washer
                G.hex_prism(bt, c + Vector((0, 0, 0.0042)), "z", 0.013, 0.006)
        parts.append(bt)
    return parts


# =============================================================================
# Mannequin: stand, neck, head (the GP-5 mask over it is a vanilla proxy); test hose
# =============================================================================
def head_loft(part, rings, poles, n, at, zc, p=2.0):
    """A smooth body through superellipse sections [(y, half-width, forward, backward)] in the axes of the
    worn GP-5 model (the section axis is x = 0, z = zc; forward is toward -z), vertices on the axis at the
    bottom and top; to Blender via at."""
    bm = part.bm
    e = 2.0 / p
    rv, axes = [], []
    for y, w, f, b in rings:
        ring = []
        for k in range(n):
            t = 2 * math.pi * k / n
            c, s = math.cos(t), math.sin(t)
            x = w * math.copysign(abs(c) ** e, c)
            z = zc + (b - f) / 2 + (f + b) / 2 * math.copysign(abs(s) ** e, s)
            ring.append(bm.verts.new(tuple(at((x, y, z)))))
        rv.append(ring)
        axes.append(at((0.0, y, zc + (b - f) / 2)))
    zb, zt = (zc + (r[3] - r[2]) / 2 for r in (rings[0], rings[-1]))
    lo, hi = (bm.verts.new(tuple(at((0.0, poles[0], zb)))), bm.verts.new(tuple(at((0.0, poles[1], zt)))))
    up = at((0.0, 1.0, 0.0)) - at((0.0, 0.0, 0.0))
    for i in range(len(rv) - 1):
        for k in range(n):
            j = (k + 1) % n
            q = [rv[i][k], rv[i][j], rv[i + 1][j], rv[i + 1][k]]
            c = sum((v.co for v in q), Vector()) / 4
            G.face(part, q, c - (axes[i] + axes[i + 1]) / 2)
    for k in range(n):
        j = (k + 1) % n
        G.face(part, [rv[0][j], rv[0][k], lo], -up)
        G.face(part, [rv[-1][k], rv[-1][j], hi], up)
    bm.normal_update()


def build_head(spec):
    lod = spec["lod"]
    n = (24, 12, 8)[lod]
    parts = []
    # stand and peg - under the neck axis (it is 2 cm behind the head center, HEAD_RINGS)
    sx, sy = STAND_XY
    st = P("head_stand", "stand")
    G.lathe(st, [(0.068, 0.0), (0.072, 0.003), (0.072, 0.014), (0.066, 0.020), (0.022, 0.024), (0.0, 0.025)]
            if lod == 0 else [(0.072, 0.0), (0.072, 0.016), (0.0, 0.024)], n, (sx, sy, BZ), "z", caps=(True, False))
    parts.append(st)
    pole = P("head_pole", "pole")
    g.cyl(pole, (sx, sy, (BZ + 0.024 + NECK_Z) / 2 + 0.01), "z", 0.010, NECK_Z - BZ - 0.004, (10, 6, 6)[lod])
    parts.append(pole)
    # neck and head - by sections in the worn mask axes (HEAD_RINGS): the whole head is under the mask
    hd = P("head", "head")
    head_loft(hd, [HEAD_RINGS[i] for i in HEAD_SEL[lod]], HEAD_POLES, (16, 10, 6)[lod], GP5["at"], HEAD_ZC)
    parts.append(hd)
    return parts


def m84_tip():
    """Tip of the cone of the M84 nozzle in slot 1 and the nozzle axis."""
    return Vector(MODS[0]) + M84_NOZ + M84_DIR * 0.040, M84_DIR


def build_test_hose(spec):
    """Adapter in the neck of the GP-5 valve box (instead of the filter), a dia. 13 hose in a smooth arc onto
    the board and to the coupling on the M84 tip (without the module the coupling lies on the end of the
    hose over the mat)."""
    lod = spec["lod"]
    if lod == 2:
        return []
    ax, neck = GP5["axis"], GP5["neck"]
    ad = P("gp5_adapter", "brass")
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
    zb = BZ + HOSE_R
    # from the mask along the thread axis down and forward, sags to the board in front of the stand, lies on
    # the board and comes to the coupling on the right in a loop
    pts = [tuple(h0), tuple(h0 + ax * 0.045), (-0.392, -0.540, 0.525), (-0.405, -0.552, 0.462),
           (-0.425, -0.540, zb), (-0.440, -0.490, zb), (-0.432, -0.440, zb + 0.002), (-0.425, -0.405, zb + 0.010),
           tuple(c1 + d * 0.028), tuple(c1)]
    hs = P("test_hose", "hose_hp")
    g.pipe(hs, G.spline(pts, 3) if lod == 0 else G.spline(pts, 1), HOSE_R, 8 if lod == 0 else 5)
    parts.append(hs)
    if lod == 0:
        hc = P("test_hose_clamps", "zinc")
        G.hose_clamp(hc, neck + ax * 0.046, ax, HOSE_R, w=0.007, sides=10)
        G.hose_clamp(hc, c1 + d * 0.004, d, HOSE_R, w=0.007, sides=10)
        parts.append(hc)
    return parts


# =============================================================================
# Blow gun on the board (own), the yellow hose to it is in build_compressor
# =============================================================================
def build_gun(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    f = GUN
    up = Vector((0, 0, 1))
    bk = P("blow_gun", "comp_black")
    if lod == 0:
        G.slab(bk, 0.006, 0.078, -0.012, 0.012, -0.011, 0.011, rc=0.007, nc=2, re=0.005, ne=2, rb=0.005, nb=2, frame=f)
        G.slab(bk, 0.064, 0.098, -0.016, 0.024, -0.012, 0.012, rc=0.008, nc=2, re=0.004, ne=1, rb=0.004, nb=1, frame=f)
    else:
        g.box(bk, 0.006, 0.078, -0.012, 0.012, -0.011, 0.011, frame=f)
        g.box(bk, 0.064, 0.098, -0.016, 0.024, -0.012, 0.012, frame=f)
    parts = [bk]
    al = P("blow_gun_nozzle", "chrome")
    n = 12 if lod == 0 else 6
    G.lathe(al, [(0.0085, 0.0), (0.0085, 0.012), (0.0062, 0.018), (0.0042, 0.021)], n, f.p(0.081, 0.024, 0.0), f.v,
            caps=(False, True))
    G.rod(al, f.p(0.081, 0.044, 0.0), f.p(0.081, 0.135, 0.0), 0.0027, 8 if lod == 0 else 4)
    G.lathe(al, [(0.0034, 0.0), (0.0034, 0.010), (0.0018, 0.016)], 8 if lod == 0 else 4, f.p(0.081, 0.134, 0.0), f.v,
            caps=(True, True))
    parts.append(al)
    # inlet fitting (brass) - outward, toward the board edge
    bs = P("blow_gun_inlet", "brass")
    G.lathe(bs, [(0.0055, -0.002), (0.0055, 0.007), (0.0040, 0.009), (0.0040, 0.016), (0.0048, 0.017), (0.0034, 0.021)],
            n, f.o, -f.u, caps=(True, True))
    parts.append(bs)
    if lod == 0:
        tr = P("blow_gun_trigger", "toggle")
        g.pipe(tr, G.spline([f.p(0.066, 0.016, 0.0), f.p(0.048, 0.030, 0.0), f.p(0.030, 0.028, 0.0),
                             f.p(0.020, 0.016, 0.0)], 3), 0.0035, 6)
        parts.append(tr)
    return parts


# =============================================================================
# Inside the chest: a tray (filters, wrench, tape, can, rags - vanilla), tarpaulin, cylinder
# =============================================================================
def build_inside(spec):
    lod = spec["lod"]
    parts = []
    tr = P("tray", "wood_in")
    t = 0.010
    kb = dict(r=0.0015, seg=1) if lod == 0 else {}
    g.box(tr, TX0, TX1, TY0, TY1, TZ - t, TZ)                                         # bottom
    if lod < 2:
        g.box(tr, TX0, TX1, TY0, TY0 + t, TZ, TZ + 0.06, **kb)
        g.box(tr, TX0, TX1, TY1 - t, TY1, TZ, TZ + 0.06, **kb)
        g.box(tr, TX0, TX0 + t, TY0 + t, TY1 - t, TZ, TZ + 0.06, **kb)
        g.box(tr, TX1 - t, TX1, TY0 + t, TY1 - t, TZ, TZ + 0.06, **kb)
        g.box(tr, TX0 + t, TX1 - t, TSPLIT - t / 2, TSPLIT + t / 2, TZ, TZ + 0.045, **kb)    # partition
    parts.append(tr)
    # tarpaulin folded in a stack: three layers with rounded edges, slightly askew
    cv = P("canvas", "canvas")
    x0, x1, y0, y1, z0, z1 = CANVAS
    if lod == 2:
        g.box(cv, x0, x1, y0, y1, z0, z1)
    else:
        lay = [(0.0, 0.0, 0.0, 0.0), (0.012, -0.006, 0.018, -0.03), (0.03, -0.014, 0.034, -0.06)]
        for k, (a, b, c, d) in enumerate(lay if lod == 0 else lay[::2]):
            za, zz = z0 + (z1 - z0) * k / 3, z0 + (z1 - z0) * (k + 1) / 3 + 0.002
            if lod == 0:
                G.slab(cv, x0 + a, x1 + b, y0 + c, y1 + d, za, zz, rc=0.03, nc=2, re=0.018, ne=2, rb=0.014, nb=2)
            else:
                G.slab(cv, x0 + a, x1 + b, y0 + c, y1 + d, za, z0 + (z1 - z0) * (k + 2) / 3, rc=0.02, nc=1)
    parts.append(cv)
    # 6 l cylinder: bottom, shell, shoulder, neck, a valve with a handwheel
    n = (20, 10, 6)[lod]
    tk = P("tank", "tank")
    prof = [(0.0, 0.0), (0.030, 0.002), (0.050, 0.010), (0.063, 0.025), (0.069, 0.045), (TANK_R, 0.065),
            (TANK_R, TANK_L - 0.075), (0.067, TANK_L - 0.045), (0.058, TANK_L - 0.025), (0.042, TANK_L - 0.010),
            (0.024, TANK_L - 0.002), (0.022, TANK_L)]
    G.lathe(tk, prof if lod == 0 else [prof[i] for i in (0, 2, 4, 6, 8, 10, 11)] if lod == 1 else
            [prof[i] for i in (0, 3, 5, 6, 9, 11)], n, TANK_O, "x", caps=(False, True))
    parts.append(tk)
    if lod == 2:
        return parts
    e = TANK_O.x + TANK_L
    vl = P("tank_valve", "brass")
    c = Vector((e, TANK_O.y, TANK_O.z))
    G.lathe(vl, [(0.016, 0.0), (0.016, 0.012), (0.014, 0.014), (0.014, 0.040), (0.011, 0.044), (0.0, 0.045)],
            12 if lod == 0 else 6, c, "x", caps=(True, False))
    G.lathe(vl, [(0.008, 0.012), (0.008, 0.030)], 8 if lod == 0 else 5, c + Vector((0.026, 0, 0)), "-y",
            caps=(False, True))                                                     # outlet
    if lod == 0:
        G.hex_prism(vl, c + Vector((0.026, -0.036, 0)), "y", 0.020, 0.010)          # coupling nut
        G.lathe(vl, [(0.0065, 0.010), (0.0065, 0.018), (0.009, 0.020), (0.0, 0.022)], 8, c + Vector((0.026, 0, 0)),
                "y", caps=(False, False))                                           # diaphragm on the other side
    G.lathe(vl, [(0.0055, 0.014), (0.0055, 0.034)], 6, c + Vector((0.026, 0, 0)), "z")
    hw = P("tank_wheel", "comp_black")
    if lod == 0:
        G.handwheel(hw, c + Vector((0.026, 0, 0.036)), "z", 0.024, 0.0035, spokes=3, nu=16, nv=5)
    else:
        g.cyl(hw, tuple(c + Vector((0.026, 0, 0.036))), "z", 0.024, 0.008, 6)
    parts += [vl, hw]
    return parts


# =============================================================================
# Compressor under the board
# =============================================================================
def build_compressor(spec):
    lod = spec["lod"]
    parts = []
    # receiver: a shell with convex ends, welds, a drain valve, feet on rubber
    n = (20, 10, 6)[lod]
    rd = P("comp_tank", "comp_red")
    prof = [(0.0, 0.0), (0.030, 0.002), (0.055, 0.008), (0.075, 0.018), (0.088, 0.031), (0.094, 0.046), (CTR, 0.058),
            (CTR, 0.242), (0.094, 0.254), (0.088, 0.269), (0.075, 0.282), (0.055, 0.292), (0.030, 0.298), (0.0, 0.300)]
    c0 = (CMX - 0.15, CMY, CTZ)
    G.lathe(rd, prof if lod == 0 else [prof[i] for i in (0, 2, 4, 6, 7, 9, 11, 13)] if lod == 1 else
            [prof[i] for i in (0, 3, 6, 7, 10, 13)], n, c0, "x")
    if lod == 0:
        for h in (0.058, 0.242):
            G.torus(rd, G.axis_frame((c0[0] + h, CMY, CTZ), "x"), CTR + 0.0006, 0.0022, 20, 3)
    parts.append(rd)
    ft = P("comp_feet", "comp_red")
    rb = P("comp_feet_rubber", "rubber")
    for xf in (CMX - 0.10, CMX + 0.10):
        for s in (-1, 1):
            a = (xf, CMY + s * 0.061, 0.062)
            b = (xf, CMY + s * 0.088, 0.016)
            if lod < 2:
                G.bar(ft, a, b, 0.026, 0.004, up=(0, s, 0))
            G.lathe(rb, [(0.017, 0.0), (0.017, 0.010), (0.013, 0.014), (0.0, 0.015)] if lod == 0 else
                    [(0.017, 0.0), (0.017, 0.014), (0.0, 0.015)], (12, 6, 5)[lod], (xf, CMY + s * 0.088, 0.0), "z",
                    caps=(True, False))
    parts += [ft, rb]
    if lod == 0:
        dr = P("comp_drain", "brass")
        G.hex_prism(dr, (CMX + 0.04, CMY, CTZ - CTR - 0.004), "z", 0.014, 0.008)
        G.lathe(dr, [(0.004, -0.008), (0.004, 0.0)], 6, (CMX + 0.04, CMY, CTZ - CTR - 0.008), "z")
        g.box(dr, CMX + 0.04 - 0.012, CMX + 0.04 + 0.012, CMY - 0.002, CMY + 0.002, CTZ - CTR - 0.020,
              CTZ - CTR - 0.014)
        parts.append(dr)
    # platform on the receiver and a bar handle
    bk = P("comp_body", "comp_black")
    if lod == 0:
        G.slab(bk, *PLAT, rc=0.012, nc=2, re=0.002, ne=1)
    else:
        g.box(bk, *PLAT)
    parts.append(bk)
    hd = P("comp_handle", "comp_black")
    hy = PLAT[3] - 0.012
    hp = [(CMX - 0.13, hy, PT), (CMX - 0.13, hy, 0.405), (CMX + 0.13, hy, 0.405), (CMX + 0.13, hy, PT)]
    g.pipe(hd, G.fillet(hp, 0.03, 4) if lod == 0 else hp, 0.008, (10, 6, 4)[lod])
    if lod == 0:
        G.lathe(hd, [(0.0105, -0.07), (0.012, -0.065), (0.012, 0.065), (0.0105, 0.07)], 12, (CMX, hy, 0.405), "x",
                caps=(True, True))                                                  # rubber grip of the handle
    parts.append(hd)
    # motor: a finned body, end caps, feet, a terminal box
    mo = P("comp_motor", "comp_black")
    mprof = [(0.0, 0.0), (0.040, 0.0), (0.052, 0.005), (0.056, 0.013), (MOTOR_R, 0.022), (MOTOR_R, MOT_L - 0.020),
             (0.056, MOT_L - 0.012), (0.050, MOT_L - 0.005), (0.030, MOT_L), (0.0, MOT_L)]
    G.lathe(mo, mprof if lod == 0 else [mprof[i] for i in (0, 2, 4, 5, 7, 9)], (20, 10, 6)[lod],
            (MOT_X0, MOTOR.y, MOTOR.z), "x")
    if lod == 0:
        for k in range(12):
            a = 2 * math.pi * k / 12
            if math.cos(a - 3 * math.pi / 2) > 0.65:                                # no fins at the bottom
                continue
            d = Vector((0.0, math.cos(a), math.sin(a)))
            o = MOTOR + d * (MOTOR_R + 0.0025)
            g.box(mo, MOT_X0 + 0.028, MOT_X0 + MOT_L - 0.026, -0.0015, 0.0015, -0.0035, 0.0035,
                  frame=g.Frame((0.0, o.y, o.z), (1, 0, 0), Vector((0, 0, 1)).cross(d) if abs(d.z) < 0.99 else
                                Vector((0, 1, 0)), d))
        G.slab(mo, MOTOR.x - 0.03, MOTOR.x + 0.02, MOTOR.y - 0.022, MOTOR.y + 0.022, MOTOR.z + MOTOR_R - 0.006,
               MOTOR.z + MOTOR_R + 0.018, rc=0.005, nc=1, re=0.003, ne=1)          # terminal box
    if lod < 2:
        for xm in (MOT_X0 + 0.025, MOT_X0 + MOT_L - 0.025):
            g.box(mo, xm - 0.012, xm + 0.012, MOTOR.y - 0.045, MOTOR.y + 0.045, PT, PT + 0.012)
    parts.append(mo)
    sh = P("comp_shaft", "chrome")
    g.cyl(sh, (MOT_X0 - 0.010, MOTOR.y, MOTOR.z), "x", 0.006, 0.022, 8 if lod == 0 else 5)
    parts.append(sh)
    # fan: bone ozl_fan (rotation about ozl_fan_axis, along x)
    fn = P("comp_fan", "fan", group=SEL_FAN)
    G.fan(fn, FAN, "x", FAN_R, 0.014, (5, 3, 0)[lod], 0.026, 28.0, lod=lod)
    parts.append(fn)
    if lod < 2:
        # wire guard in front of the fan: two rings, spokes, a boss
        gd = P("comp_fan_guard", "guard")
        gx = FAN.x - 0.016
        fr = G.axis_frame((gx, FAN.y, FAN.z), "x")
        G.torus(gd, fr, FAN_R + 0.005, 0.0018, (24, 12)[lod], (4, 3)[lod])
        if lod == 0:
            G.torus(gd, fr, 0.030, 0.0016, 16, 3)
        for k in range(6 if lod == 0 else 4):
            a = 2 * math.pi * (k + 0.5) / (6 if lod == 0 else 4)
            d = fr.u * math.cos(a) + fr.v * math.sin(a)
            g.pipe(gd, [tuple(fr.o + d * 0.009), tuple(fr.o + d * (FAN_R + 0.005)),
                        tuple(fr.o + d * (FAN_R + 0.005) + Vector((0.026, 0, 0)))], 0.0016, 4)
        G.lathe(gd, [(0.010, -0.002), (0.010, 0.002)], 8, fr.o, "x", caps=(True, True))
        parts.append(gd)
    # piston block: a crankcase, a finned cylinder, a head on bolts, an air filter
    al = P("comp_pump", "alu")
    if lod == 0:
        G.slab(al, CMX + 0.055, CMX + 0.135, CMY - 0.038, CMY + 0.058, PT, 0.302, rc=0.012, nc=2, re=0.006, ne=1)
    else:
        g.box(al, CMX + 0.055, CMX + 0.135, CMY - 0.038, CMY + 0.058, PT, 0.302)
    cx, cy = CYL
    if lod < 2:
        G.lathe(al, [(0.031, 0.302), (0.031, 0.372)], 14 if lod == 0 else 8, (cx, cy, 0.0), "z")
        for k in range(5 if lod == 0 else 2):
            z = 0.312 + 0.012 * k if lod == 0 else 0.320 + 0.025 * k
            G.lathe(al, [(0.031, z), (0.043, z + 0.0005), (0.043, z + 0.0028), (0.031, z + 0.0033)],
                    14 if lod == 0 else 8, (cx, cy, 0.0), "z")
        if lod == 0:
            G.slab(al, cx - 0.047, cx + 0.047, cy - 0.045, cy + 0.045, 0.372, 0.396, rc=0.010, nc=2, re=0.004, ne=1)
        else:
            g.box(al, cx - 0.047, cx + 0.047, cy - 0.045, cy + 0.045, 0.372, 0.396)
    parts.append(al)
    if lod == 0:
        bt = P("comp_head_bolts", "bolt")
        for sx in (-1, 1):
            for sy in (-1, 1):
                G.hex_prism(bt, (cx + sx * 0.033, cy + sy * 0.031, 0.399), "z", 0.009, 0.006)
        parts.append(bt)
        af = P("comp_air_filter", "comp_black")
        G.lathe(af, [(0.012, 0.0), (0.019, 0.004), (0.019, 0.022), (0.015, 0.026), (0.0, 0.027)], 14,
                (cx, cy + 0.045, 0.384), "y", caps=(True, False))
        parts.append(af)
        # copper discharge tube from the head to the brass block, nuts at the ends
        cu = P("comp_pipe", "copper")
        mx = (MAN[0] + MAN[1]) / 2 - 0.005
        ym = (MAN[2] + MAN[3]) / 2
        cp = [(cx + 0.02, cy - 0.045, 0.384), (cx + 0.02, cy - 0.070, 0.384), (cx + 0.02, ym, 0.350),
              (mx, ym, 0.320), (mx, ym, MAN[5])]
        g.pipe(cu, G.fillet(cp, 0.012, 3), 0.004, 8)
        G.hex_prism(cu, (cx + 0.02, cy - 0.048, 0.384), "y", 0.011, 0.006)
        G.hex_prism(cu, (mx, ym, MAN[5] + 0.003), "z", 0.011, 0.006)
        parts.append(cu)
    if lod == 2:
        return parts
    # relay box with a lamp (ozl_lamp) and a switch, a brass block: gauge, regulator, valve, quick coupling
    sw = P("comp_switch", "comp_black")
    if lod == 0:
        G.slab(sw, *SWB, rc=0.006, nc=2, re=0.004, ne=1)
        G.lathe(sw, [(0.008, 0.0), (0.008, 0.010), (0.006, 0.016)], 8, (SWB[0], (SWB[2] + SWB[3]) / 2, PT + 0.024),
                "-x", caps=(False, True))                                           # cable gland
    else:
        g.box(sw, *SWB)
    parts.append(sw)
    br = P("comp_manifold", "brass")
    if lod == 0:
        G.slab(br, *MAN, rc=0.003, nc=1, re=0.002, ne=1)
    else:
        g.box(br, *MAN)
    G.lathe(br, [(0.005, 0.0), (0.005, MAN[2] - GAUGE.y + 0.001)], 8 if lod == 0 else 5,
            (GAUGE.x, MAN[2], GAUGE.z), "-y")                                       # gauge nipple
    parts.append(br)
    gc = P("comp_gauge", "chrome")
    gr = GAUGE_D / 2
    G.lathe(gc, [(0.0, 0.0), (gr - 0.002, 0.0), (gr + 0.0015, 0.003), (gr + 0.0025, 0.008), (gr + 0.0025, 0.018),
                 (gr + 0.0015, 0.0205), (gr - 0.0015, 0.0215)] if lod == 0 else
            [(0.0, 0.0), (gr + 0.002, 0.003), (gr + 0.002, 0.020), (gr - 0.0015, 0.0215)],
            20 if lod == 0 else 10, GAUGE, "-y")
    parts.append(gc)
    gf = P("comp_gauge_face", "gauge_face")
    G.lathe(gf, [(gr - 0.0012, 0.0), (0.0, 0.0)], 20 if lod == 0 else 10, (GAUGE.x, G_FACE, GAUGE.z), "-y")
    parts.append(gf)
    # needle - bone ozl_needle: at zero (225 degrees - down-left), a blade, a counterweight, a cap
    nd = P("comp_needle", "needle", group=SEL_NEEDLE)
    u = Vector((math.cos(A_ZERO), 0.0, math.sin(A_ZERO)))
    nf = g.Frame((GAUGE.x, NEEDLE_Y, GAUGE.z), u, Vector((0, -1, 0)).cross(u), (0, -1, 0))
    t = 0.0008
    Ln = NEEDLE_L
    g.prism(nd, [(-0.006, -0.0010), (0.0, -0.0012), (Ln - 0.003, -0.0004), (Ln, 0.0), (Ln - 0.003, 0.0004),
                 (0.0, 0.0012), (-0.006, 0.0010)], (0, 1), 0.0, t, frame=nf)
    G.lathe(nd, [(0.0026, 0.0), (0.0024, 0.0008), (0.0014, 0.0014)], 10 if lod == 0 else 6,
            (GAUGE.x, NEEDLE_Y - t, GAUGE.z), "-y", caps=(True, True))
    parts.append(nd)
    lp = P("comp_lamp", "lamp", group=SEL_LAMP)
    G.lathe(lp, [(0.0072, 0.0), (0.0072, 0.003), (0.0055, 0.0065), (0.0, 0.0085)], 10 if lod == 0 else 6, LAMP, "-y",
            caps=(True, False))
    parts.append(lp)
    if lod == 0:
        lb = P("comp_lamp_bezel", "chrome")
        G.lathe(lb, [(0.0072, -0.0005), (0.0105, 0.0), (0.0105, 0.0016), (0.0078, 0.0026)], 12, LAMP, "-y")
        parts.append(lb)
        tg = P("comp_toggle", "toggle")
        G.slab(tg, -0.009, 0.009, -0.013, 0.013, 0.0, 0.007, rc=0.003, nc=1, re=0.003, ne=1,
               frame=g.Frame((LAMP.x + 0.027, SWB[2], PT + 0.040), (1, 0, 0), (0, 0, 1), (0, -1, 0)))
        parts.append(tg)
        bz = P("comp_valves", "brass")
        ym = (MAN[2] + MAN[3]) / 2
        # safety valve with a ring
        G.hex_prism(bz, (MAN[0] + 0.012, ym, MAN[5] + 0.004), "z", 0.012, 0.008)
        G.lathe(bz, [(0.0055, 0.008), (0.0055, 0.024), (0.0035, 0.028)], 8, (MAN[0] + 0.012, ym, MAN[5]), "z",
                caps=(False, True))
        G.torus(bz, g.Frame((MAN[0] + 0.012, ym, MAN[5] + 0.032), (1, 0, 0), (0, 0, 1), (0, 1, 0)), 0.0075, 0.0012,
                10, 3)
        # quick coupling on the right end of the block
        G.hex_prism(bz, COUPLER + Vector((0.004, 0, 0)), "x", 0.017, 0.008)
        G.lathe(bz, [(0.0095, 0.008), (0.0095, 0.016), (0.011, 0.018), (0.011, 0.028), (0.0085, 0.031)], 12,
                COUPLER, "x", caps=(False, True))
        parts.append(bz)
        kb = P("comp_regulator", "comp_black")
        kc = (MAN[1] - 0.015, ym, MAN[5])
        G.lathe(kb, [(0.0055, 0.0), (0.0055, 0.006)], 8, kc, "z")
        G.lathe(kb, [(0.0110, 0.006), (0.0125, 0.008), (0.0125, 0.019), (0.0105, 0.022), (0.0, 0.023)], 16, kc, "z",
                caps=(True, False))
        # regulator knob knurling: eight longitudinal ribs
        for k in range(8):
            a = 2 * math.pi * k / 8
            d = Vector((math.cos(a), math.sin(a), 0.0))
            o = Vector(kc) + d * 0.0127
            g.box(kb, -0.0012, 0.0012, -0.001, 0.001, 0.009, 0.018, frame=g.Frame(o, d.cross(Vector((0, 0, 1))), d,
                                                                                  (0, 0, 1)))
        parts.append(kb)
    # yellow hose: from the quick coupling to the right, up at the end of the board, over the edge onto the board - to the gun
    hs = P("comp_hose", "hose")
    s0 = COUPLER + Vector((0.034, 0, 0))
    inlet = GUN.p(-0.021, 0.0, 0.0)
    pts = [tuple(s0), tuple(s0 + Vector((0.025, -0.006, 0.004))), (0.632, -0.588, 0.300), (0.628, -0.598, 0.400),
           (0.618, -0.586, BZ + 0.010), (0.614, -0.572, BZ + HOSE_Y_R + 0.002), tuple(inlet - GUN.u * 0.006),
           tuple(inlet)]
    g.pipe(hs, G.spline(pts, 3) if lod == 0 else G.spline(pts, 1), HOSE_Y_R, 8 if lod == 0 else 5)
    parts.append(hs)
    if lod == 0:
        hf = P("comp_hose_ends", "zinc")
        G.lathe(hf, [(0.0068, 0.0), (0.0068, 0.016)], 10, s0 - Vector((0.004, 0, 0)), "x", caps=(True, True))
        G.lathe(hf, [(0.0068, 0.0), (0.0068, 0.014)], 10, inlet - GUN.u * 0.012, GUN.u, caps=(True, True))
        parts.append(hf)
        # power cable: from the gland down the receiver face to the floor, left under the board to the chest, a plug
        cb = P("comp_cable", "cable")
        c0 = Vector((SWB[0] - 0.016, (SWB[2] + SWB[3]) / 2, PT + 0.024))
        zc = 0.0042
        cpts = [tuple(c0), (c0.x - 0.025, c0.y - 0.006, c0.z - 0.012), (CMX - 0.065, CMY - 0.108, 0.17),
                (CMX - 0.085, CMY - 0.118, 0.05), (CMX - 0.10, CMY - 0.128, zc + 0.004), (0.17, -0.60, zc),
                (0.03, -0.52, zc), (-0.04, -0.38, zc), (-0.058, -0.262, zc)]
        g.pipe(cb, G.spline(cpts, 5), zc, 6)
        pg = Vector((-0.065, -0.235, 0.0))
        pf = g.Frame(pg, (0.94, 0.34, 0), (-0.34, 0.94, 0), (0, 0, 1))              # the plug lies on its side
        G.slab(cb, -0.018, 0.018, -0.024, 0.024, 0.0, 0.026, rc=0.010, nc=2, re=0.008, ne=2, frame=pf)
        parts.append(cb)
        pn = P("comp_plug_pins", "chrome")
        for dx in (-0.0095, 0.0095):
            G.rod(pn, pf.p(dx, 0.024, 0.013), pf.p(dx, 0.043, 0.013), 0.002, 6)
        parts.append(pn)
    return parts


def build_lod(spec):
    parts = build_chest(spec) + build_board(spec) + build_head(spec) + build_test_hose(spec) + build_gun(spec)
    parts += build_inside(spec) + build_compressor(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    wood = kx.PEN + r"\wood.rvmat"
    # a geometry component thinner than 0.5 m does not work in the engine: the bottom is the chest, the
    # board and the compressor as one box; the lid is a box going forward, into the chest
    low = kx.box_pts(BX0 - 0.005, BX1 + 0.005, GAUGE.y - 0.03, CY1 + 0.02, 0.0, ZR + 0.01)
    lid_top = L.lid_point(CY0, ZR + LID_H)
    lid = kx.box_pts(CX0 - 0.005, CX1 + 0.005, CY1 - 0.50, lid_top[0] + 0.01, ZR - 0.10, lid_top[1] + 0.01)
    comps = [(low, wood), (lid, wood)]
    memory = {
        "invView": [(-0.3, -2.4, 1.5)],
        "ce_center": [(0.0, 0.0, 0.45)],
        "ce_radius": [(0.95, 0.0, 0.45)],
        # rotation axis of the compressor fan (ozl_work): from the hub along the motor axis
        "ozl_fan_axis": [(FAN.x, FAN.y, FAN.z), (FAN.x + 0.05, FAN.y, FAN.z)],
        # gauge needle axis (ozl_needle): from the needle axis toward the person
        "ozl_needle_axis": [(GAUGE.x, NEEDLE_Y, GAUGE.z), (GAUGE.x, NEEDLE_Y - 0.05, GAUGE.z)],
    }
    for i, m in enumerate(MODS):
        memory["module_%d" % (i + 1)] = [m]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2] + 0.004)
    return comps, 70.0, memory, bbox


# the first ones are for the --look preview: overall, the board with the modules in place (and the same
# empty), the compressor (when "working" - the needle at 7.2, the lamp), the mannequin with the hose to
# the pressure tester
SHOTS = [
    ("front", (-1.1, -2.5, 1.6), (0.0, 0.0, 0.45), 30),
    ("board", (-0.05, -1.45, 1.30), (-0.02, -0.33, 0.52), 34),
    ("compressor", (0.98, -1.30, 0.52), (0.46, -0.50, 0.25), 36),
    ("head", (-0.95, -1.10, 0.98), (-0.40, -0.40, 0.58), 36),
    ("inside", (0.0, -0.75, 1.65), (0.0, 0.14, 0.30), 30),
    ("lid", (0.2, -1.5, 1.05), (0.0, 0.5, 0.75), 32),
    ("right", (1.7, -0.7, 1.0), (0.0, 0.0, 0.40), 32),
    ("back", (1.3, 2.0, 1.4), (0.0, 0.0, 0.5), 32),
]

M.look_shots = (4, 3)
M.run(build_lod, collision, SHOTS, row_step=1.7, row_shot=((1.7, -5.6, 1.8), (1.7, 0, 0.5)))
