"""M03 - radiation-shielded glove box: the Scientists' Anomaly Packer (OZL_Eco_Pack_Anom).
Packer: cargo 10x10, three module places (module_1..3) and proxies for the modules at the same
places. Each module of the Anomaly line has its own slot and working place: slot 1 - probe-detector
M69 inside on the floor, detector end toward the sample; slot 2 - dosimeter-radiometer M70 outside on
the mat of the right-hand shelf; slot 3 - lead house M71 inside in the middle next to the lead cup.
The probe cable runs through a gland in the right wall behind the airlock: a socket at the probe
plug inside, a plug on the mat by the radiometer outside.

    blender --background --python build_m03.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]
                                                  [--gloves-out]

Before the first run, run make_decals.py with the system Python (radiation sign and gauge scale).

The device follows GOST 28164-89 "Radiation-protection glove boxes", type 1BP1 (single-sided,
single-module, one operator), table 1 and drawing 8: inside 900 x 700 mm, 500 deep at the top (the
front wall above the gloves slopes back, the window is in the slope), working zone height 700,
worktop 950 mm above the floor, glove axes at 1150 and 450 mm apart, glove port 180 mm, lower bend
of the front wall 325 mm above the worktop; side airlock with its axis at 1140 mm, total height with
filters and the draft gauge on the roof 1850 mm, width with the airlock ~1.2 m. Per the drawing a
valve panel and a solid-waste removal unit sit under the box. To the right of the airlock is a shelf
with a mat; with it the total width is 1.64 m.

Deviations from the GOST: the base is a frame on four legs with a lower shelf instead of a cabinet;
the airlock is a lying drum with a round lid on a hand wheel at the front, so that it is visible
from the working side; the glass is yellowish, like lead glass.

Glove variants: by default the gloves are INSIDE the box, like a real radiochemical one (it is under
vacuum, the gloves are drawn in and lie on the floor); --gloves-out hangs the gloves OUTSIDE (like an
overpressure box): readable at once but implausible for radiochemistry. The outside variant is a
separate object m03_glovebox_out; its frames go to work/renders with the out_ mark (look_out_front.png
and so on).

Look: the "dayz" look (matte, dirtier, coloured AO); laboratory equipment: intact enamel, chips on
the edges down to grey primer, worn to bare metal under the glove rings, at the airlock and on the
front edge of the base; rust only at the feet of the base. The gloves are soft (the glove builders
below explain the construction): a box glove is ~0.75 m (sleeve from diameter 0.17 at the ring to
the wrist, hand ~0.19); inside, the sleeve sags from the ring to the floor and lies there, palm
down, thumb toward the middle. Small props are vanilla DayZ items through proxies (kvanilla): a GP-5
gas mask and a spare filter, a rag, tape, an adjustable wrench and a screwdriver on the lower shelf;
a journal sheet and a pen on the module shelf.

Work look: ozl_lamp - chamber light and the green "power" lamp (steady), ozl_lamp_work - the yellow
"work" lamp (blinks); ozl_needle - draft gauge needle: at rest on 20 (the box is always under
vacuum), in "work" it trembles from the hand movements in the gloves (wobble, a bone on the source
ozl_needle, up to 0.2 rad). "Work" is atlas _on (glow); OZL_Work is in the mod's config. The
modules in the slots work together with the device (their own OZL_Work).

Blender axes: X is width, Y is depth (face toward -Y), Z is up.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import krender  # noqa: E402
import kvanilla as kv  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
GLOVES_OUT = "--gloves-out" in kmodel.ARGV

# =============================================================================
# Dimensions, m
# =============================================================================
SX0, SX1, SY0, SY1, ZS = -0.82, 0.82, -0.36, 0.36, 0.92     # base, top at ZS
BX0, BX1 = -0.82, 0.14                                       # box width
BXC = (BX0 + BX1) / 2
YF, YB, WALL = -0.38, 0.38, 0.03                             # front, back, wall
XI1 = BX1 - WALL                                             # right wall, inner side
ZF, ZK, ZC, ZR, ZTOP = 0.95, 1.275, 1.65, 1.68, 1.85         # floor, bend, ceiling, roof, top
TAN = 0.20 / (ZR - ZK)                                       # slope: at the top the box is 200 mm shallower
TILT = math.degrees(math.atan(TAN))
COS = math.cos(math.radians(TILT))
FRONT = g.inclined_front(YF, ZK, TILT)
BL = (ZR - ZK) / COS                                         # slope length
WA, WB0, WB1 = 0.355, 0.045, BL - 0.045                      # window: half width, bottom and top along the slope
PX, PZ, PR_HOLE = (BXC - 0.225, BXC + 0.225), 1.15, 0.09     # glove rings: glove axes, opening
PORT_CUT_SIDES = (20, 10)                                    # sides of the ring cut-out in the body (LOD 1, 2)
LX, LR, LY0, LY1 = 0.335, 0.17, -0.30, 0.24                  # airlock: x axis, radius, front and back
LZ = ZS + 0.035 + LR
HX0, HX1 = 0.53, 0.82                                        # module shelf
ZM = ZS + 0.006                                              # top of the shelf mat
ZL = 0.155                                                   # top of the lower shelf
GX, GY, GZ = BXC - 0.12, -0.10, ZR + 0.105                   # draft gauge on the roof
FACE_Y = GY - 0.021                                          # its scale
NEEDLE_REST = 20.0                                           # needle at rest: working vacuum, divisions
NEEDLE_SWING = 0.20                                          # "work": trembles up to 0.2 rad (~2.5 divisions)
VX, VY = BXC + 0.12, -0.05                                   # valve on the roof
PIG = (-0.02, 0.02, ZL)                                      # lead container on the lower shelf
WASTE = (BX0 + 0.12, 0.12)                                   # solid-waste removal unit
DRAIN = (-0.20, 0.06)                                        # liquid-waste drain into the jerrycan
CAN = (-0.50, -0.28, -0.16, 0.12, 0.40)                      # jerrycan: x0 x1 y0 y1 top
CAN_CAP = (-0.33, 0.06)
# modules: slot 1 - probe M69 on the floor, detector end (-x) toward the sample; slot 2 - radiometer
# M70 on the shelf mat; slot 3 - lead house M71 on the tray by the cup. Everything valuable is inside
# at the back wall: from a step away the line of sight through the bottom of the window reaches the
# floor only beyond the middle of the depth, and the gloves lie at the front wall
TRAY_T = 0.003
S1 = (-0.10, 0.235, ZF)
S2 = (0.675, -0.15, ZM)
S3 = (-0.50, 0.25, ZF + TRAY_T)
MODS = [S1, S2, S3]
MOD_OBJ = [("m69_anom_probe", "ozr_anom_probe"), ("m70_radiometer", "ozr_radiometer"),
           ("m71_lead_shield", "ozr_lead_shield")]
# plug of the M69 probe cable (from its generator: plug end at x 0.0823, y Y0 + 0.106 = 0.071,
# axis 0.008 above the bottom)
M69_PLUG = Vector((S1[0] + 0.0823, S1[1] + 0.071, ZF + 0.008))
# inside: sample tray, lead cup and its lid, tongs, light
SAMPLE_TRAY = (-0.37, -0.25, 0.17, 0.31, 0.022)              # x0 x1 y0 y1 height
STONE = (-0.31, 0.24)
CUP, LID = (-0.70, 0.275), (-0.70, 0.17)
LAMP, LAMP_Z = (BXC - 0.26, BXC + 0.26), 1.47
# cable gland in the right wall behind the airlock (y, z)
GLAND = (0.30, 1.03)
CABLE_R = 0.004
# lighting panel on the front right of the right glove ring: x0 x1 z0 z1 depth; lamps and toggle by z
CB = (0.032, 0.124, 1.045, 1.205, 0.045)
CB_X = (CB[0] + CB[1]) / 2
CB_LAMPS = (1.172, 1.128)                                    # green "power", yellow "work"
CB_TOGGLE = 1.078


def y_out(z):
    return YF + (z - ZK) * TAN


def y_in(z):
    return y_out(z) + WALL / COS


LOD_SPECS = [
    dict(lod=0, bev=2, sides=16),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "box": ("enamel_box", 1.0), "box_front": ("enamel_front", 2.0), "cav": ("steel_in", 0.5),
    "stand": ("enamel_stand", 0.6), "steel": ("steel", 1.0), "chrome": ("chrome", 1.5), "rubber": ("rubber", 0.8),
    "glove": ("glove", 1.0), "glove_in": ("glove_in", 0.6), "black": ("black", 1.2), "red": ("wheel_red", 1.2),
    "gauge": ("gauge", 3.0),
    "lead": ("lead", 1.0), "lead_bare": ("lead_bare", 1.0), "lead_cup": ("lead_cup", 1.5), "stone": ("stone", 2.0),
    "canister": ("canister", 0.6), "cap_red": ("cap_red", 1.0), "filter": ("filter", 1.0),
    "grille_h": ("grille_h", 1.2), "plate": ("plate", 2.0), "panel": ("panel", 1.5),
    "lamp_tube": ("lamp_tube", 1.0), "lamp_green": ("lamp_green", 3.0), "lamp_amber": ("lamp_amber", 3.0),
    "cable": ("cable", 0.8), "alu": ("alu", 1.2),
}


# =============================================================================
# Materials
# =============================================================================
def build_enamel(mat, origin, color, under=kmats.lin((92, 94, 90)), bare=kmats.lin((150, 152, 150)), seed=1.0,
                 gloss=0.42, spec=0.30, chip=(0.64, 0.70), rust_low=0.0, floor_z=0.0, dust=0.30, grime=0.35,
                 rub=(), decal_items=()):
    """Laboratory equipment enamel (Scientists: intact, wear at the handles): like kmats.build_paint, but
    chips go down to grey primer, deeper to metal, and there is no rust (rust_low - only at the floor);
    rub - [(centre, half-axes, strength)] is wear where the box is rubbed by hands and elbows: an
    ellipsoid, weaker toward its edge (the build_worn technique from M23)."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.93 for c in color[:3]) + (1,), color)
    col = kmats.decals(t, base, sep, nsep, decal_items)
    edge = t.maprange(t.edge_wear(0.004), 0.06, 0.25, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 11.0, 10.0, 0.7), 0.75), t.math("MULTIPLY", edge, 0.55))
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
    chips = t.step(f, chip[0], chip[1])
    col = t.mixc(chips, col, under)
    deep = t.step(f, chip[1] + 0.08, chip[1] + 0.14)
    brush = t.noise(t.stretch(vec, 0.04, 1.0, 1.0), 90.0, 4.0, 0.7)
    metal = t.mixc(t.maprange(brush, 0.3, 0.7, 0.0, 1.0), tuple(c * 0.8 for c in bare[:3]) + (1,), bare)
    col = t.mixc(deep, col, metal)
    g_ = t.math("ADD", gloss, t.math("MULTIPLY", deep, 0.58 - gloss))
    s_ = t.math("ADD", spec, t.math("MULTIPLY", deep, 0.62 - spec))
    if rust_low > 0:
        low = t.maprange(sep.outputs["Z"], floor_z + 0.25, floor_z, 0.0, rust_low)
        speck = t.step(t.noise(vec, 24.0, 8.0, 0.7), 0.62, 0.70)
        rust = t.math("MULTIPLY", t.math("MAXIMUM", t.math("MULTIPLY", chips, 0.8), speck), low)
        rcol = t.ramp(t.noise(vec, 30.0, 6.0, 0.6), [(0.3, kmats.RUST[0]), (0.55, kmats.RUST[1]), (0.8, kmats.RUST[2])])
        col = t.mixc(t.math("MULTIPLY", rust, 0.9), col, rcol)
        g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", rust, gloss * 0.8))
        s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", rust, spec * 0.8))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g_, s_, t.math("MULTIPLY", chips, -0.4))


def build_lead(mat, origin, seed=7.7, tone=(96, 100, 104), oxide=0.7, floor_z=0.0, dust=0.3, grime=0.4):
    """Bare cast lead (bricks, cup): dull grey-blue, whitish oxide patches and speckles, dents as relief,
    low gloss, lower still on the oxide (the mat_lead technique from M04)."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    c = kmats.lin(tone)
    col = t.mixc(t.maprange(t.noise(vec, 3.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0), tuple(x * 0.85 for x in c[:3]) + (1,), c)
    blot = t.maprange(t.noise(vec, 3.0, 6.0, 0.6), 0.50, 0.80, 0.0, 1.0)
    speck = t.maprange(t.noise(vec, 40.0, 4.0, 0.6), 0.58, 0.78, 0.0, 1.0)
    ox = t.math("MINIMUM", t.math("ADD", t.math("MULTIPLY", blot, 0.6 * oxide), t.math("MULTIPLY", speck, 0.3 * oxide)),
                0.8)
    col = t.mixc(ox, col, kmats.lin((156, 158, 154)))
    dents = t.noise(vec, 14.0, 3.0, 0.5)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    gl = t.math("SUBTRACT", 0.32, t.math("ADD", t.math("MULTIPLY", ox, 0.22), t.math("MULTIPLY", dirt, 0.12)))
    sp = t.math("SUBTRACT", 0.28, t.math("MULTIPLY", ox, 0.18))
    return kmats.out(t, col, gl, sp, t.math("MULTIPLY", t.math("SUBTRACT", dents, 0.5), 0.3))


TREFOIL = [(os.path.join(WORK, "decal_trefoil.png"), "y", -1, ("x", "z"), (BXC, PZ), (0.115, 0.115),
            (YF - 0.01, YF + 0.005))]
TREFOIL_PIG = [(os.path.join(WORK, "decal_trefoil.png"), "y", -1, ("x", "z"), (PIG[0], PIG[2] + 0.13), (0.085, 0.085),
                (-0.10, -0.075))]
GAUGE = [(os.path.join(WORK, "decal_gauge.png"), "y", -1, ("x", "z"), (GX, GZ), (2 * 0.057, 2 * 0.057),
          (FACE_Y - 0.003, FACE_Y + 0.003))]

KINDS = kmats.std_kinds(floor_z=0.0)
# enamel wear: under the glove rings - forearms, front edge - elbows, airlock end by the lid, handles of the back
# door
BOX_RUB = [((px, YF, PZ - 0.07), (0.16, 0.06, 0.12), 0.35) for px in PX] + [
    ((BXC, YF, ZS + 0.01), (0.46, 0.05, 0.05), 0.25), ((LX, LY0, LZ), (0.22, 0.05, 0.22), 0.30),
    ((BXC + 0.18, YB, 1.28), (0.06, 0.04, 0.24), 0.30)]
BOX = dict(color=kmats.lin((116, 130, 114)), under=kmats.lin((92, 94, 90)), seed=1.7, gloss=0.42, spec=0.30,
           chip=(0.64, 0.70), floor_z=0.0, dust=0.30, grime=0.30, rub=BOX_RUB)
STAND_RUB = [((0.0, SY0, ZS - 0.01), (0.85, 0.05, 0.035), 0.30), ((0.675, SY0, ZS), (0.16, 0.05, 0.05), 0.25),
             ((0.0, SY0, ZL - 0.005), (0.85, 0.05, 0.03), 0.25)]
KINDS.update({
    "enamel_box": (build_enamel, BOX),
    "enamel_front": (build_enamel, dict(BOX, decal_items=TREFOIL)),
    "enamel_stand": (build_enamel, dict(color=kmats.lin((92, 102, 90)), under=kmats.lin((70, 72, 70)), seed=2.9,
                                        gloss=0.36, spec=0.26, chip=(0.60, 0.66), rust_low=0.7, floor_z=0.0,
                                        dust=0.35, grime=0.55, rub=STAND_RUB)),
    "steel_in": ("steel", dict(seed=3.1, tone=0.34, along="x", floor_z=ZF, dust=0.2, grime=0.15)),
    "chrome": ("steel", dict(seed=7.1, tone=0.36, along="z", gloss=0.70, spec=0.80, dust=0.12, grime=0.2)),
    # glove rubber: black, semi-matte, lighter where stretched
    "glove": ("plastic", dict(color=kmats.lin((24, 24, 25)), gloss=0.32, spec=0.22, dust=0.25, grime=0.2,
                              mottle=0.08, scuff=(0.97, 1.0))),
    # glove from inside (ring opening): even dark rubber without dust and scratches - a dark opening
    "glove_in": ("flat", dict(color=kmats.lin((16, 16, 17)), gloss=0.25, spec=0.15)),
    "wheel_red": (build_enamel, dict(color=kmats.lin((158, 30, 24)), under=kmats.lin((70, 66, 62)), seed=6.1,
                                     gloss=0.45, spec=0.32, chip=(0.56, 0.63), dust=0.2, grime=0.25)),
    "gauge": ("paint", dict(color=kmats.lin((236, 234, 226)), chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0,
                            gloss=0.60, spec=0.45, dust=0.0, grime=0.0, decal_items=GAUGE)),
    "lead": ("paint", dict(color=kmats.lin((88, 92, 96)), under=kmats.lin((128, 130, 132)), seed=7.7, gloss=0.25,
                           spec=0.2, chip=(0.62, 0.68), rust=(0.99, 1.0), rust_low=0.0, dust=0.3, grime=0.4,
                           decal_items=TREFOIL_PIG)),
    "lead_bare": (build_lead, dict(seed=8.1, floor_z=ZL)),
    "lead_cup": (build_lead, dict(seed=8.9, oxide=0.5, floor_z=ZF, dust=0.1, grime=0.2)),
    "stone": ("plastic", dict(color=kmats.lin((88, 66, 54)), gloss=0.40, spec=0.30, mottle=0.35, dust=0.05,
                              grime=0.4, scuff=(0.55, 0.65))),
    "canister": ("plastic", dict(color=kmats.lin((214, 206, 172)), gloss=0.3, spec=0.2, mottle=0.08, dust=0.5,
                                 grime=0.4)),
    "filter": (build_enamel, dict(color=kmats.lin((168, 172, 166)), under=kmats.lin((96, 96, 96)), seed=8.3,
                                  gloss=0.40, spec=0.30, chip=(0.62, 0.68), floor_z=ZR, dust=0.45, grime=0.3)),
    "plate": ("steel", dict(seed=7.3, tone=0.42, along="x", dust=0.15, grime=0.2)),
    "panel": (build_enamel, dict(color=kmats.lin((178, 180, 174)), under=kmats.lin((90, 92, 90)), seed=9.1,
                                 gloss=0.40, spec=0.30, chip=(0.62, 0.68), dust=0.2, grime=0.25,
                                 rub=[((CB_X, YF - CB[4], CB_TOGGLE), (0.03, 0.02, 0.03), 0.35)])),
    # lamps: "off" is the dark glass of the cap, "work" - lit (_on, glow)
    "lamp_tube": ("flat", dict(color=kmats.lin((196, 196, 186)), gloss=0.6, spec=0.5)),
    "lamp_tube_on": ("flat", dict(color=kmats.lin((255, 250, 232)), gloss=0.6, spec=0.5)),
    "lamp_green": ("flat", dict(color=kmats.lin((34, 78, 40)), gloss=0.85, spec=0.8)),
    "lamp_green_on": ("flat", dict(color=kmats.lin((90, 255, 110)), gloss=0.85, spec=0.8)),
    "lamp_amber": ("flat", dict(color=kmats.lin((112, 72, 18)), gloss=0.85, spec=0.8)),
    "lamp_amber_on": ("flat", dict(color=kmats.lin((255, 176, 36)), gloss=0.85, spec=0.8)),
    "cable": ("plastic", dict(color=kmats.lin((56, 58, 60)), gloss=0.30, spec=0.2, dust=0.3, grime=0.3,
                              scuff=(0.8, 0.9))),
    "alu": ("steel", dict(seed=8.8, tone=0.44, along="x", gloss=0.45, spec=0.5, floor_z=ZF, dust=0.1, grime=0.3)),
})

OBJ, NAME = ("m03_glovebox_out", "ozr_glovebox_out") if GLOVES_OUT else ("m03_glovebox", "ozr_glovebox")
# Work look: lamps use atlas _on (onSelections; the yellow one blinks), the needle is a bone
SEL_LAMP, SEL_BLINK, SEL_NEEDLE = "ozl_lamp", "ozl_lamp_work", "ozl_needle"
# preview of the "work" look: the needle at mid-tremble, rotated like the engine does it
# (engine_turn, the _posed wrapper below)
ON_MOVE = {}
ON = dict(remap={"lamp_tube": "lamp_tube_on", "lamp_green": "lamp_green_on", "lamp_amber": "lamp_amber_on"},
          emissive=(1.0, 1.0, 1.0, 1.0), move=ON_MOVE)
NEEDLE_ANIM = ("ozl_needle_wobble", dict(type="rotation", source=SEL_NEEDLE, selection=SEL_NEEDLE,
                                          axis="ozl_needle_axis", memory=1, minValue=0.0, maxValue=1.0,
                                          angle0=0.0, angle1=NEEDLE_SWING))
NEEDLE_MID, NEEDLE_AMP = 0.5, 0.35                           # tremble in "work": wobble mid +- amp
# The needle axis is given by memory points (collision). The engine rotates a bone right-handed in
# DayZ axes (kexport.conv, determinant -1); in Blender axes that is a left-handed rotation about the
# axis from the first point to the second. The axis points toward the person, so a positive angle is
# clockwise for them (as in M08, M12, M14, M33, whose needles are right in game). An axis pointing
# from the face into the device makes the needle swing counter-clockwise, toward smaller divisions.
# So the axis points to the person (-Y) and positive is clockwise, up the scale.
NEEDLE_AXIS = [(GX, FACE_Y + 0.010, GZ), (GX, FACE_Y - 0.010, GZ)]


def engine_turn(axis_pts, ang):
    """Rotation of a bone by angle ang as the engine does it about the memory axis axis_pts: (point on the
    axis, Blender axis for Matrix.Rotation - right-handed, angle). The Blender axis is opposite to the
    memory axis (from the second point to the first)."""
    a, b = Vector(axis_pts[0]), Vector(axis_pts[1])
    return a, a - b, ang


def check_needle():
    """Numeric check, like check_axes of the Storage boxes: the engine rotation at phases 0, mid +- amp and
    1 moves the needle clockwise from NEEDLE_REST toward larger divisions of the 0..60 scale (270 degrees
    clockwise from the lower-left corner) and keeps it on the scale. If it does not hold, the build fails."""
    c = Vector((GX, FACE_Y, GZ))
    th = math.radians(-(135.0 + 270.0 * NEEDLE_REST / 60.0))
    tip = c + Vector((math.cos(th), 0.0, math.sin(th))) * 0.046
    seen, last = [], None
    for ph in (0.0, NEEDLE_MID - NEEDLE_AMP, NEEDLE_MID, NEEDLE_MID + NEEDLE_AMP, 1.0):
        o, ax, ang = engine_turn(NEEDLE_AXIS, ph * NEEDLE_SWING)
        q = o + Matrix.Rotation(ang, 3, ax) @ (tip - o)
        deg = math.degrees(math.atan2(q.z - c.z, q.x - c.x)) % 360.0     # front view: right is +X
        div = (225.0 - deg) % 360.0 / 270.0 * 60.0                         # scale division under the needle
        assert 0.0 <= div <= 60.0, "needle off the scale: %.1f" % div
        assert last is None or div >= last - 1e-6, "needle moves counter-clockwise, toward smaller divisions"
        last = div
        seen.append("%.2f -> %.1f" % (ph, div))
    assert last > NEEDLE_REST + 1.0, "needle does not move clockwise"
    print("turns ok: needle (phase -> scale divisions) " + ", ".join(seen))


check_needle()
# proxies for the modules: the mod's CfgNonAIVehicles binds slots OZL_Tool1..3 to them (Proxyozl_tool1..3);
# slot N is module N of the Anomaly line (M69, M70, M71), no rotation: the modules face the person
PROXIES = [(r"\OpenZone_Research\models\proxies\ozl_tool%d" % (i + 1), m) for i, m in enumerate(MODS)]
# vanilla DayZ items: the lower shelf and the module shelf
DECOR = [
    kv.put("gp5", (0.40, -0.17, ZL), up=(0, 1, 0), fwd=(0, 0, 1)),            # on its back, glass up
    kv.put("gp5filter", (0.68, -0.17, ZL), up=(0, 0, 1), fwd=(0, -1, 0)),     # spare filter, standing
    kv.put("rags", (0.24, 0.18, ZL), **kv.flat(80)),
    kv.put("ducttape", (-0.66, -0.20, ZL), **kv.flat(0)),
    kv.put("wrench", (-0.17, -0.27, ZL), **kv.flat(5)),
    kv.put("screwdriver", (0.03, -0.20, ZL), **kv.flat(175)),
    kv.put("paper", (0.692, 0.165, ZM), **kv.flat(90)),                        # measurement journal
    kv.put("pen", (0.71, 0.12, ZM + 0.0005), **kv.flat(70)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.62, 0.52, 0.20), clear=0.24, edge=0.14, smudge=0.07, streaks=0.04),
                 selections=(SEL_LAMP, SEL_BLINK, SEL_NEEDLE), hidden=(SEL_LAMP, SEL_BLINK), states={"on": ON},
                 bones=((SEL_NEEDLE, ""),), animations=(NEEDLE_ANIM,), sources={SEL_NEEDLE: dict(animPeriod=0.2)},
                 proxies=PROXIES, decor=DECOR, modules=[(o, n, m) for (o, n), m in zip(MOD_OBJ, MODS)])
if GLOVES_OUT:
    # frames of the "gloves outside" variant go to the same work/renders with an out_ mark after the view
    # (geo_out_front.png, look_out_compare.png): the bake service takes only work/renders and the gallery
    # shows them, and the frames of the main variant are not overwritten
    _shoot = krender.shoot

    def shoot_out(cam, path, *args, **kw):
        folder, fn = os.path.split(path)
        tag, _, rest = fn.partition("_")
        return _shoot(cam, os.path.join(folder, "%s_out_%s" % (tag, rest)), *args, **kw)
    krender.shoot = shoot_out
P = M.part
BOUNDS = {}


# =============================================================================
# Primitives missing from kgeo
# =============================================================================
def axes(axis):
    """An axis and two unit vectors perpendicular to it."""
    a = Vector(axis).normalized()
    h = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    u = h.cross(a).normalized()
    return a, u, a.cross(u).normalized()


def orient(f, want):
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def lathe(part, prof, sides, center, axis, start=0.0):
    """Body of revolution: prof [(r, h)] along axis (a vector) from center. The winding keeps the material
    on the left: along the outer wall from the base up, along the end toward the axis, along the bore
    down; the segment normal (dh, -dr) points outward. Ends are open (caps are disc)."""
    bm = part.bm
    a, u, v = axes(axis)
    c = Vector(center)

    def rad(k):
        t = start + 2 * math.pi * k / sides
        return u * math.cos(t) + v * math.sin(t)
    rings = [[bm.verts.new(c + a * h + rad(k) * r) for k in range(sides)] for r, h in prof]
    new = []
    for i in range(len(prof) - 1):
        dr, dh = prof[i + 1][0] - prof[i][0], prof[i + 1][1] - prof[i][1]
        for k in range(sides):
            j = (k + 1) % sides
            f = bm.faces.new([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]])
            new.append(orient(f, rad(k + 0.5) * dh - a * dr))
    return part.tag(new)


def disc(part, center, axis, r, sides, r_in=0.0, start=0.0):
    """Disc (or ring r_in..r) facing along axis."""
    bm = part.bm
    a, u, v = axes(axis)
    c = Vector(center)
    dirs = [u * math.cos(start + 2 * math.pi * k / sides) + v * math.sin(start + 2 * math.pi * k / sides)
            for k in range(sides)]
    outer = [bm.verts.new(c + d * r) for d in dirs]
    if r_in <= 0:
        return part.tag([orient(bm.faces.new(outer), a)])
    inner = [bm.verts.new(c + d * r_in) for d in dirs]
    return part.tag([orient(bm.faces.new([outer[k], outer[(k + 1) % sides], inner[(k + 1) % sides], inner[k]]), a)
                     for k in range(sides)])


def torus(part, center, axis, R, r, seg, sides):
    """Torus (hand wheel rim, eyebolt)."""
    bm = part.bm
    a, u, v = axes(axis)
    c = Vector(center)
    rings = []
    for i in range(seg):
        t = 2 * math.pi * i / seg
        d = u * math.cos(t) + v * math.sin(t)
        rings.append([bm.verts.new(c + d * (R + r * math.cos(2 * math.pi * k / sides)) +
                                   a * (r * math.sin(2 * math.pi * k / sides))) for k in range(sides)])
    new = []
    for i in range(seg):
        r0, r1 = rings[i], rings[(i + 1) % seg]
        for k in range(sides):
            j = (k + 1) % sides
            new.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def bolt(part, at, axis, r=0.0065, h=0.0055, sides=6):
    """Hex head (nut) on a surface: at - on the surface, axis - outward; no bottom."""
    lathe(part, [(r, 0.0), (r, h)], sides, at, axis, start=math.pi / sides)
    disc(part, Vector(at) + Vector(axis).normalized() * h, axis, r, sides, start=math.pi / sides)


def bolts(prefix, region, pts, axis, r=0.0065, h=0.0055, sides=6, uv_name=None):
    """Identical bolts: each is its own part with a shared unwrap (one place in the atlas)."""
    out = []
    for i, p in enumerate(pts):
        b = P("%s%d" % (prefix, i), region, uv_name=uv_name or prefix, uv_origin=tuple(p))
        bolt(b, p, axis, r, h, sides)
        out.append(b)
    return out


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, as in M16 and M69)."""
    v = [Vector(p) for p in pts]
    out = []
    for i in range(len(v) - 1):
        p0 = v[i - 1] if i > 0 else 2 * v[i] - v[i + 1]
        p1, p2 = v[i], v[i + 1]
        p3 = v[i + 2] if i + 2 < len(v) else 2 * v[i + 1] - v[i]
        for s in range(k):
            t = s / k
            out.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (3 * p1 - p0 - 3 * p2 + p3) * t ** 3))
    out.append(v[-1])
    return [tuple(q) for q in out]


def bends(pts, r, n=4):
    """Pipe polyline with bends: each corner is an arc of n segments (a quadratic curve from the point r
    before the corner to the point r after it)."""
    v = [Vector(p) for p in pts]
    out = [v[0]]
    for i in range(1, len(v) - 1):
        a, b, c = v[i - 1], v[i], v[i + 1]
        p0 = b + (a - b).normalized() * min(r, (a - b).length * 0.5)
        p2 = b + (c - b).normalized() * min(r, (c - b).length * 0.5)
        for s in range(n + 1):
            t = s / n
            out.append((1 - t) ** 2 * p0 + 2 * (1 - t) * t * b + t * t * p2)
    out.append(v[-1])
    return [tuple(q) for q in out]


def skin(part, nodes, edges, radii, levels):
    """Soft shape from a skeleton (glove): nodes, edges, radii (across, in thickness) -> Skin modifier
    (+ Subdivision levels) -> part faces. For a horizontal branch "across" lies in the floor plane and
    "thickness" is up; for a vertical one they are along x and y (checked in Blender 5.2)."""
    me = bpy.data.meshes.new("skin_tmp")
    me.from_pydata([tuple(p) for p in nodes], edges, [])
    ob = bpy.data.objects.new("skin_tmp", me)
    bpy.context.scene.collection.objects.link(ob)
    ob.modifiers.new("skin", "SKIN")
    sv = me.skin_vertices[0].data
    for i, r in enumerate(radii):
        sv[i].radius = r
    sv[0].use_root = True
    if levels:
        ss = ob.modifiers.new("smooth", "SUBSURF")
        ss.levels = ss.render_levels = levels
    dg = bpy.context.evaluated_depsgraph_get()
    ev = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bpy.data.meshes.remove(me)
    bm = part.bm
    vs = [bm.verts.new(v.co) for v in ev.vertices]
    new = [bm.faces.new([vs[i] for i in poly.vertices]) for poly in ev.polygons]
    bpy.data.meshes.remove(ev)
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def stone(part, center, size, subdiv, seed=3.0):
    """Lumpy stone (artifact sample): an icosphere with noise, the bottom flattened - it lies."""
    bm = part.bm
    before = set(bm.faces)
    ret = bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    c = Vector(center)
    for v in ret["verts"]:
        d = v.co.normalized()
        k = 1.0 + 0.22 * noise.noise(d * 1.7 + Vector((seed, 0, 0))) + 0.07 * noise.noise(d * 4.0)
        q = Vector((d.x * size[0] * k, d.y * size[1] * k, max(d.z * size[2] * k, -size[2] * 0.75)))
        v.co = c + q
    faces = [f for f in bm.faces if f not in before]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return part.tag(faces)


def open_tray(part, x0, x1, y0, y1, z0, h, t, lip=0.0):
    """Tray: floor and four walls of thickness t; lip is the radius of the rolled edge."""
    g.box(part, x0, x1, y0, y1, z0, z0 + t)
    g.box(part, x0, x1, y0, y0 + t, z0 + t, z0 + h)
    g.box(part, x0, x1, y1 - t, y1, z0 + t, z0 + h)
    g.box(part, x0, x0 + t, y0 + t, y1 - t, z0 + t, z0 + h)
    g.box(part, x1 - t, x1, y0 + t, y1 - t, z0 + t, z0 + h)
    if lip:
        g.pipe(part, [(x0, y0, z0 + h), (x1, y0, z0 + h), (x1, y1, z0 + h), (x0, y1, z0 + h), (x0, y0, z0 + h)], lip, 6)


# =============================================================================
# Box: body, glass, window frame, glove rings, gloves
# =============================================================================
def build_shell(spec):
    """Side-profile prism minus the chamber, the window in the slope and (near LODs) the glove openings."""
    lod = spec["lod"]
    outer = [(YF, ZS), (YB, ZS), (YB, ZR), (y_out(ZR), ZR), (YF, ZK)]
    base = P("shell_base", "box")
    g.prism(base, outer, (1, 2), BX0, BX1)
    if spec["bev"]:
        g.bevel(base.bm, base.bm.edges[:], 0.008, spec["bev"])
    zk_in = ZK - WALL * (1 / COS - 1) / TAN
    inner = [(YF + WALL, ZF), (YB - WALL, ZF), (YB - WALL, ZC), (y_in(ZC), ZC), (YF + WALL, zk_in)]
    cav = P("cut_cav", "cav")
    g.prism(cav, inner, (1, 2), BX0 + WALL, BX1 - WALL)
    win = P("cut_win", "steel")
    g.box(win, BXC - WA, BXC + WA, WB0, WB1, -0.07, 0.02, frame=FRONT)
    cutters = [cav, win]
    if lod < 2:
        for i, px in enumerate(PX):
            c = P("cut_port%d" % i, "steel")
            g.cyl(c, (px, YF + 0.01, PZ), "y", PR_HOLE, 0.10, PORT_CUT_SIDES[lod])
            cutters.append(c)
    shell = M.boolean("shell", base, cutters)
    # the lower part of the front is its own region: it carries the radiation sign and needs density
    fr = shell.region_index("box_front", *REGIONS["box_front"])
    for f in shell.bm.faces:
        c = f.calc_center_median()
        if f.normal.y < -0.95 and c.y < YF + 0.004 and c.z < ZK:
            f[shell.reg] = fr
    return shell


def build_glass():
    p = P("glass", "box", section="glass")
    a0, a1, b0, b1 = BXC - WA + 0.003, BXC + WA - 0.003, WB0 + 0.003, WB1 - 0.003
    c = -0.012
    g.quad(p, [FRONT.p(a0, b0, c), FRONT.p(a1, b0, c), FRONT.p(a1, b1, c), FRONT.p(a0, b1, c)])
    p.glass_frame = (FRONT, a0, a1, b0, b1)
    return p


def build_window_frame(spec):
    """Window clamp frame on the slope (chamfers), rubber seal along the glass edge, bolts."""
    lod = spec["lod"]
    if lod == 2:
        return []
    fr = P("win_frame", "steel")
    w, t = 0.04, 0.014
    a0, a1 = BXC - WA - w, BXC + WA + w
    kw = dict(r=0.003, seg=1) if lod == 0 else {}
    for x0, x1, b0, b1 in ((a0, a1, WB0 - w, WB0), (a0, a1, WB1, WB1 + w), (a0, BXC - WA, WB0, WB1),
                           (BXC + WA, a1, WB0, WB1)):
        g.box(fr, x0, x1, b0, b1, 0.0, t, frame=FRONT, **kw)
    parts = [fr]
    if lod == 0:
        gs = P("win_gasket", "rubber")
        e = 0.007
        for x0, x1, b0, b1 in ((BXC - WA, BXC + WA, WB0, WB0 + e), (BXC - WA, BXC + WA, WB1 - e, WB1),
                               (BXC - WA, BXC - WA + e, WB0 + e, WB1 - e), (BXC + WA - e, BXC + WA, WB0 + e, WB1 - e)):
            g.box(gs, x0, x1, b0, b1, -0.012, 0.003, frame=FRONT)
        parts.append(gs)
        pts = [(BXC + a, b) for a in (-0.30, -0.15, 0.0, 0.15, 0.30) for b in (WB0 - w / 2, WB1 + w / 2)]
        pts += [(BXC + s * (WA + w / 2), (WB0 + WB1) / 2) for s in (-1, 1)]
        parts += bolts("win_bolt", "steel", [FRONT.p(a, b, t) for a, b in pts], FRONT.n, 0.0075, 0.0055)
    return parts


# glove ring (from the wall face outward, along -y): ring flange; the glove cuff - a roll behind, around
# the ring and over the front edge (CUFF), then dark rubber into the opening down to the bottom (bore:
# the glove seen from inside; no chamber shows between the glove and the ring); a clamp over the cuff
RING = [(0.136, 0.0), (0.136, 0.0065), (0.1325, 0.0095), (0.1125, 0.0095), (0.1115, 0.012)]
CUFF = [(0.1125, 0.009), (0.1158, 0.0125), (0.1128, 0.016), (0.1128, 0.038), (0.1095, 0.0445), (0.0935, 0.0445)]


def bore(rb):
    """Rubber in the opening down to the bottom; rb is smaller than the inscribed radius of the cut in the
    body (a polygon), otherwise the cut wall shows through the rubber as light patches."""
    return [(0.0935, 0.0445), (rb, 0.039), (rb, -0.020)]
BAND = [(0.1128, 0.0205), (0.1157, 0.021), (0.1157, 0.0295), (0.1128, 0.030)]


def build_ports(spec):
    """Glove rings on the box front; a disc on the far LOD."""
    lod = spec["lod"]
    axis = (0.0, -1.0, 0.0)
    parts = []
    for i, px in enumerate(PX):
        c = (px, YF, PZ)
        if lod == 2:
            d = P("port%d" % i, "rubber", uv_name="port", uv_origin=c)
            g.cyl(d, (px, YF - 0.012, PZ), "y", 0.125, 0.024, 8)
            parts.append(d)
            continue
        n = 18 if lod == 0 else 10
        rg = P("port_ring%d" % i, "steel", uv_name="port_ring", uv_origin=c)
        lathe(rg, RING if lod == 0 else [RING[0], RING[1], RING[3]], n, c, axis)
        parts.append(rg)
        cf = P("port_cuff%d" % i, "glove", uv_name="port_cuff", uv_origin=c)
        lathe(cf, CUFF if lod == 0 else [CUFF[k] for k in (0, 3, 4, 5)], n, c, axis)
        cf.use("glove_in", *REGIONS["glove_in"])
        rb = PR_HOLE * math.cos(math.pi / PORT_CUT_SIDES[lod]) - 0.0015
        lathe(cf, bore(rb), n, c, axis)
        disc(cf, (px, YF + 0.020, PZ), axis, rb, n)
        parts.append(cf)
        if lod == 0:
            bd = P("port_band%d" % i, "steel", uv_name="port_band", uv_origin=c)
            lathe(bd, BAND, n, c, axis)
            # clamp lock from below: two lugs and a tightening screw
            g.box(bd, px - 0.012, px + 0.012, YF - 0.0305, YF - 0.0200, PZ - 0.1235, PZ - 0.1150)
            g.cyl(bd, (px, YF - 0.025, PZ - 0.1215), "x", 0.0035, 0.034, 6)
            parts.append(bd)
            pts = [(px + 0.124 * math.cos(a), YF - 0.0065, PZ + 0.124 * math.sin(a))
                   for a in (math.radians(30 + 60 * k) for k in range(6))]
            parts += bolts("port%d_bolt" % i, "steel", pts, axis, 0.0055, 0.0045, uv_name="port_bolt")
    return parts


# glove: fingers from the knuckles - (across the hand, length): index, middle, ring, little finger
FINGERS = ((0.030, 0.066), (0.010, 0.077), (-0.010, 0.072), (-0.030, 0.057))
# sleeve inside: x offset toward the wall and (y, z, radius across, in thickness) from the ring to the
# wrist (the first two nodes are on the ring axis: the sleeve leaves the opening straight, behind the
# cuff bottom)
SLEEVE_DX = (0.0, 0.0, 0.010, 0.030, 0.068, 0.101)
SLEEVE_IN = [(-0.345, PZ, 0.086, 0.086), (-0.300, PZ - 0.001, 0.085, 0.084), (-0.258, 1.100, 0.079, 0.072),
             (-0.225, 1.025, 0.073, 0.054), (-0.185, ZF + 0.032, 0.068, 0.032), (-0.110, ZF + 0.026, 0.059, 0.025)]


def hand(W, d, n, ts, lod):
    """Hand skeleton from wrist W: d toward the fingers, n the back of the hand, ts the thumb side (+1
    along d x n). The Skin root sits 3 cm back inside the sleeve (the end of the sleeve tube hides
    there), the palm is the middle and the knuckles, four fingers from the knuckles, the thumb from the
    middle of the palm; the fingers curl slightly toward the palm, Skin with smoothing rounds them off by
    itself."""
    W = Vector(W)
    d = Vector(d).normalized()
    n = Vector(n)
    n = (n - d * n.dot(d)).normalized()
    e = d.cross(n)

    def at(a, b, c):
        return W + d * a + e * b + n * c
    nodes = [at(-0.030, 0.0, 0.0), W, at(0.045, 0.0, 0.001), at(0.080, 0.0, -0.001)]
    radii = [(0.050, 0.024), (0.048, 0.022), (0.050, 0.019), (0.049, 0.017)]
    edges = [(0, 1), (1, 2), (2, 3)]
    for b, L in FINGERS:
        bb = b * ts
        i = len(nodes)
        nodes.append(at(0.100 + L, bb * 1.2, -0.010))
        radii.append((0.0098, 0.0088))
        edges.append((3, i))
    i = len(nodes)
    nodes += [at(0.034, 0.046 * ts, -0.005), at(0.084, 0.074 * ts, -0.009)]
    radii += [(0.0130, 0.0108), (0.0105, 0.0092)]
    edges += [(2, i), (i, i + 1)]
    return nodes, edges, radii


def sleeve_path(px, s):
    """Sleeve from the ring to the wrist: [(point, (radius across, in thickness))], wrist W, toward the
    fingers d, back of the hand n. s is the side (-1 left), the thumb points to the middle of the box.
    Inside: the sleeve sags from the ring to the floor and lies there, palm down, fingers toward the back
    wall. Outside (--gloves-out): the sleeve leaves the ring, bends down and hangs in front of the base,
    palm to the base."""
    if not GLOVES_OUT:
        sl = [((px + s * dx, y, z), (rx, ry)) for dx, (y, z, rx, ry) in zip(SLEEVE_DX, SLEEVE_IN)]
        return sl, (px + s * 0.110, -0.075, ZF + 0.023), (0.10 * s, 1.0, 0.0), (0.0, 0.0, 1.0), (0, 1, 3, 4)
    # bend at the ring - an arc of radius ~0.1 m from horizontal to vertical, then the sleeve hangs
    sl = [((px, -0.40, 1.150), (0.086, 0.086)), ((px, -0.45, 1.145), (0.085, 0.083)),
          ((px + 0.003 * s, -0.488, 1.137), (0.083, 0.080)), ((px + 0.006 * s, -0.521, 1.116), (0.080, 0.076)),
          ((px + 0.009 * s, -0.542, 1.083), (0.077, 0.071)), ((px + 0.011 * s, -0.550, 1.035), (0.073, 0.066)),
          ((px + 0.013 * s, -0.552, 0.93), (0.066, 0.058)), ((px + 0.015 * s, -0.548, 0.84), (0.056, 0.046))]
    return sl, (px + 0.016 * s, -0.545, 0.80), (0.0, 0.06, -1.0), (0.0, -1.0, 0.0), (0, 3, 5, 7)


def lerp_radii(radii, k):
    """Radii for the points of spline(pts, k): k per segment, linear."""
    out = []
    for a, b in zip(radii, radii[1:]):
        out += [tuple(x + (y - x) * j / k for x, y in zip(a, b)) for j in range(k)]
    return out + [radii[-1]]


def build_gloves(spec):
    """Gloves: the sleeve is its own tube along a smoothed curve (12 sides: with Skin plus smoothing the
    section has 8 sides, neighbouring faces at 45 degrees, and the export with threshold 40 draws them as
    facets), the hand is Skin with smoothing; the tube end (wrist, narrower than the hand) is inside the
    hand root."""
    lod = spec["lod"]
    if lod == 2 and not GLOVES_OUT:
        return []                       # not visible from afar inside
    parts = []
    for i, (px, s) in enumerate(zip(PX, (-1, 1))):
        gl = P("glove%d" % i, "glove")
        sl, W, d, n, keep = sleeve_path(px, s)
        if lod > 0:
            sl = [sl[k] for k in keep]
        pts = [Vector(q) for q, _ in sl] + [Vector(W)]
        rad = [r for _, r in sl] + [(0.036, 0.015)]
        if lod == 2:
            g.tube_var(gl, pts, rad, 5)
        else:
            k = 3 if lod == 0 else 1
            g.tube_var(gl, spline(pts, k), lerp_radii(rad, k), 12 if lod == 0 else 6)
            skin(gl, *hand(W, d, n, -s, lod), 1 if lod == 0 else 0)
        parts.append(gl)
    return parts


# =============================================================================
# Front: lighting panel, nameplate; back door, eyebolts
# =============================================================================
def lamp_lens(name, region, group, z, lod):
    """Panel lamp: chrome rim and a lens cap (selection group)."""
    c = (CB_X, YF - CB[4], z)
    axis = (0.0, -1.0, 0.0)
    n = 12 if lod == 0 else 6
    out = []
    if lod == 0:
        bz = P(name + "_bezel", "chrome", uv_name="cb_bezel", uv_origin=c)
        lathe(bz, [(0.0135, 0.0), (0.0135, 0.005), (0.0118, 0.0075), (0.0098, 0.0075)], n, c, axis)
        out.append(bz)
    ln = P(name, region, group=group)
    lathe(ln, [(0.0098, 0.0055), (0.0092, 0.0100), (0.0066, 0.0128)], n, c, axis)
    disc(ln, Vector(c) + Vector(axis) * 0.0128, axis, 0.0066, n)
    out.append(ln)
    return out


def build_panel(spec):
    """Lighting panel to the right of the right glove ring: the "power" lamp (ozl_lamp), the "work" lamp
    (ozl_lamp_work, blinks), a toggle; a flexible sleeve with wires goes down under the box into the
    base frame; an empty nameplate."""
    lod = spec["lod"]
    x0, x1, z0, z1, dp = CB
    pn = P("cb_box", "panel")
    g.box(pn, x0, x1, YF - dp, YF + 0.001, z0, z1, **(dict(r=0.004, seg=1) if lod == 0 else {}))
    parts = [pn]
    parts += lamp_lens("cb_lamp_net", "lamp_green", SEL_LAMP, CB_LAMPS[0], lod)
    parts += lamp_lens("cb_lamp_work", "lamp_amber", SEL_BLINK, CB_LAMPS[1], lod)
    if lod == 2:
        return parts
    tg = P("cb_toggle", "chrome")
    bolt(tg, (CB_X, YF - dp, CB_TOGGLE), (0.0, -1.0, 0.0), 0.0085, 0.006)
    parts.append(tg)
    lv = P("cb_lever", "black")
    g.pipe(lv, [(CB_X, YF - dp - 0.005, CB_TOGGLE), (CB_X, YF - dp - 0.026, CB_TOGGLE - 0.009)], 0.0026,
           6 if lod == 0 else 4)
    parts.append(lv)
    pl = P("nameplate", "plate")
    g.box(pl, 0.025, 0.088, YF - 0.003, YF + 0.001, 0.962, 1.018, **(dict(r=0.001, seg=1) if lod == 0 else {}))
    parts.append(pl)
    if lod == 0:
        cd = P("cb_conduit", "steel")
        x = x1 - 0.014
        g.pipe(cd, bends([(x, YF - 0.022, z0 + 0.002), (x, YF - 0.022, ZS - 0.02), (x, SY0 - 0.004, ZS - 0.045)],
                         0.025, 4), 0.0055, 8)
        parts.append(cd)
        parts += bolts("plate_rivet", "plate", [(x, YF - 0.003, z) for x in (0.031, 0.082) for z in (0.968, 1.012)],
                       (0.0, -1.0, 0.0), 0.0022, 0.0012)
    return parts


def build_box_details(spec):
    """Service door at the back (bolts, two handles), eyebolts on the roof."""
    lod = spec["lod"]
    if lod == 2:
        return []
    dr = P("back_door", "box")
    g.box(dr, BXC - 0.26, BXC + 0.26, YB - 0.001, YB + 0.006, 1.00, 1.56, **(dict(r=0.004, seg=1) if lod == 0 else {}))
    parts = [dr]
    if lod == 1:
        return parts
    hd = P("door_handles", "steel")
    for z in (1.12, 1.44):
        x = BXC + 0.18
        path = [(x, YB + 0.006, z - 0.045), (x, YB + 0.038, z - 0.045), (x, YB + 0.038, z + 0.045),
                (x, YB + 0.006, z + 0.045)]
        g.pipe(hd, path, 0.0065, 6)
    parts.append(hd)
    if lod == 0:
        pts = [(BXC + a, YB + 0.006, z) for a in (-0.24, 0.24) for z in (1.02, 1.28, 1.54)]
        parts += bolts("door_bolt", "steel", pts, (0.0, 1.0, 0.0), 0.007, 0.005)
        for i, (x, y) in enumerate(((BX0 + 0.06, 0.33), (BX1 - 0.06, 0.33))):
            ey = P("eye%d" % i, "steel", uv_name="eye", uv_origin=(x, y, ZR))
            lathe(ey, [(0.017, 0.0), (0.017, 0.006), (0.009, 0.014)], 8, (x, y, ZR), (0, 0, 1))
            torus(ey, (x, y, ZR + 0.036), (0, 1, 0), 0.020, 0.0055, 10, 4)
            parts.append(ey)
    return parts


# =============================================================================
# Airlock
# =============================================================================
def build_lock(spec):
    """Drum with ends, a convex lid with a hub and hand wheel, a hinge, swing bolts, cradles, a neck into
    the wall; inside the box - the inner lid."""
    lod = spec["lod"]
    big = 24 if lod == 0 else (12 if lod == 1 else 8)
    parts = []
    dr = P("lock_drum", "box")
    g.cyl(dr, (LX, (LY0 + LY1) / 2, LZ), "y", LR, LY1 - LY0 - 0.004, big)
    parts.append(dr)
    ht = P("lock_hatch", "steel")
    if lod == 2:
        g.cyl(ht, (LX, LY0 - 0.015, LZ), "y", 0.16, 0.03, big)
        parts.append(ht)
        return parts
    # ends: the back cover on bolts, a flange at the front - the lid seat
    if lod == 0:
        fl = P("lock_flange", "steel")
        lathe(fl, [(LR + 0.0005, -0.014), (LR + 0.016, -0.014), (LR + 0.016, 0.006), (LR - 0.02, 0.006)], big,
              (LX, LY1, LZ), (0, 1, 0))
        disc(fl, (LX, LY1 + 0.006, LZ), (0, 1, 0), LR - 0.02, big)
        lathe(fl, [(LR + 0.0005, -0.010), (LR + 0.018, -0.010), (LR + 0.018, 0.0), (LR - 0.012, 0.0)], big,
              (LX, LY0, LZ), (0, -1, 0))
        parts.append(fl)
    # the lid is convex, with a hub
    prof = [(0.160, 0.0), (0.160, 0.012), (0.152, 0.022), (0.120, 0.031), (0.060, 0.038), (0.030, 0.039)]
    lathe(ht, prof if lod == 0 else [prof[k] for k in (0, 2, 4, 5)], big, (LX, LY0, LZ), (0, -1, 0))
    disc(ht, (LX, LY0 - 0.039, LZ), (0, -1, 0), 0.030, big)
    parts.append(ht)
    hb = P("lock_boss", "steel")
    g.cyl(hb, (LX, LY0 - 0.050, LZ), "y", 0.028, 0.024, 12 if lod == 0 else 6)
    parts.append(hb)
    # hand wheel: rim, hub, three spokes slightly dished
    yw = LY0 - 0.085
    hw = P("lock_wheel", "red")
    torus(hw, (LX, yw, LZ), (0, 1, 0), 0.095, 0.009, 20 if lod == 0 else 10, 5 if lod == 0 else 3)
    g.cyl(hw, (LX, yw + 0.006, LZ), "y", 0.022, 0.036, 10 if lod == 0 else 6)
    for k in range(3):
        a = math.radians(90 + 120 * k)
        sp = [(LX + 0.018 * math.cos(a), yw + 0.010, LZ + 0.018 * math.sin(a)),
              (LX + 0.055 * math.cos(a), yw + 0.004, LZ + 0.055 * math.sin(a)),
              (LX + 0.090 * math.cos(a), yw, LZ + 0.090 * math.sin(a))]
        g.pipe(hw, sp if lod == 0 else sp[::2], 0.0068, 5 if lod == 0 else 3)
    parts.append(hw)
    # drum cradles: the top follows its shape
    th0 = math.acos(0.11 / (LR + 0.002))
    arc = [(LX + (LR + 0.002) * math.cos(-th0 - (math.pi - 2 * th0) * k / 6),
            LZ + (LR + 0.002) * math.sin(-th0 - (math.pi - 2 * th0) * k / 6)) for k in range(7)]
    sd_ = P("lock_saddles", "stand")
    for y0, y1 in ((LY0 + 0.06, LY0 + 0.10), (LY1 - 0.10, LY1 - 0.06)):
        g.prism(sd_, [(LX - 0.11, ZS), (LX + 0.11, ZS)] + arc, (0, 2), y0, y1)
    parts.append(sd_)
    # neck into the box wall and a flange on the wall
    nk = P("lock_neck", "steel")
    x1 = LX - LR + 0.03
    g.cyl(nk, ((BX1 + x1) / 2, 0.0, LZ), "x", 0.085, x1 - BX1, 14 if lod == 0 else 6, cap=False)
    if lod == 0:
        lathe(nk, [(0.122, 0.0), (0.122, 0.008), (0.086, 0.008)], 14, (BX1, 0.0, LZ), (1, 0, 0))
    parts.append(nk)
    if lod == 1:
        return parts
    nt = P("lock_wheel_nut", "steel")
    bolt(nt, (LX, yw - 0.012, LZ), (0, -1, 0), 0.012, 0.010)
    parts.append(nt)
    rb = LR + 0.007
    parts += bolts("lock_bolt", "steel", [(LX + rb * math.cos(a), LY1 + 0.006, LZ + rb * math.sin(a))
                                          for a in (math.radians(30 + 60 * k) for k in range(6))], (0, 1, 0),
                   0.006, 0.005)
    parts += bolts("neck_bolt", "steel", [(BX1 + 0.008, 0.104 * math.cos(a), LZ + 0.104 * math.sin(a))
                                          for a in (math.radians(45 + 90 * k) for k in range(4))], (1, 0, 0),
                   0.0055, 0.0045)
    # hinge on the right: leaves on the lid and on the flange, two cams, a pin
    hg = P("lock_hinge", "steel")
    xh = LX + 0.192
    for dz in (-0.045, 0.045):
        g.box(hg, LX + 0.120, xh, LY0 - 0.030, LY0 - 0.020, LZ + dz - 0.015, LZ + dz + 0.015, r=0.002, seg=1)
        g.cyl(hg, (xh, LY0 - 0.018, LZ + dz), "z", 0.011, 0.030, 8)
    g.box(hg, xh - 0.008, xh + 0.010, LY0 - 0.012, LY0 + 0.012, LZ - 0.075, LZ + 0.075, r=0.002, seg=1)
    g.cyl(hg, (xh, LY0 - 0.018, LZ), "z", 0.004, 0.14, 6)
    parts.append(hg)
    # two swing bolts on the left: a lug on the flange, a bolt over the lid edge, a wing nut
    lb, lk = P("lock_latch", "steel"), P("lock_knobs", "black")
    for ang in (155.0, 205.0):
        a = math.radians(ang)
        cx, cz = math.cos(a), math.sin(a)
        g.cyl(lb, (LX + 0.198 * cx, LY0 + 0.001, LZ + 0.198 * cz), "y", 0.010, 0.022, 8)
        g.pipe(lb, [(LX + 0.198 * cx, LY0 - 0.010, LZ + 0.198 * cz), (LX + 0.150 * cx, LY0 - 0.032, LZ + 0.150 * cz)],
               0.0042, 6)
        g.cyl(lk, (LX + 0.150 * cx, LY0 - 0.041, LZ + 0.150 * cz), "y", 0.0125, 0.016, 8)
        g.box(lk, LX + 0.150 * cx - 0.003, LX + 0.150 * cx + 0.003, LY0 - 0.052, LY0 - 0.034,
              LZ + 0.150 * cz - 0.022, LZ + 0.150 * cz + 0.022)
    parts += [lb, lk]
    # inner airlock lid on the right chamber wall: handle, hinges
    ih = P("lock_inner", "steel")
    c = (XI1, 0.0, LZ)
    lathe(ih, [(0.108, 0.0), (0.108, 0.007), (0.100, 0.011), (0.040, 0.0135)], 16, c, (-1, 0, 0))
    disc(ih, (XI1 - 0.0135, 0.0, LZ), (-1, 0, 0), 0.040, 16)
    g.pipe(ih, [(XI1 - 0.012, -0.045, LZ + 0.035), (XI1 - 0.042, -0.045, LZ + 0.035),
                (XI1 - 0.042, -0.045, LZ - 0.035), (XI1 - 0.012, -0.045, LZ - 0.035)], 0.005, 6)
    for dz in (-0.05, 0.05):
        g.cyl(ih, (XI1 - 0.010, 0.112, LZ + dz), "z", 0.008, 0.03, 8)
    parts.append(ih)
    return parts


# =============================================================================
# Probe cable: gland in the right wall, inside - to the M69 plug, outside - onto the mat to M70
# =============================================================================
def build_cables(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    gy, gz = GLAND
    n = 10 if lod == 0 else 6
    parts = []
    gl = P("gland", "chrome")
    bolt(gl, (BX1, gy, gz), (1, 0, 0), 0.016, 0.012)                        # nut outside
    lathe(gl, [(0.011, 0.012), (0.011, 0.020), (0.0075, 0.027)], n, (BX1, gy, gz), (1, 0, 0))
    bolt(gl, (XI1, gy, gz), (-1, 0, 0), 0.016, 0.010)                       # nut inside
    if lod == 0:
        parts.append(gl)
    cb = P("probe_cable", "cable")
    p0 = M69_PLUG + Vector((0.0145, 0.0, 0.0))
    zc = ZF + CABLE_R + 0.0005
    inside = [tuple(p0), (p0.x + 0.026, p0.y + 0.002, zc), (0.060, gy + 0.006, ZF + 0.022), (0.086, gy, 1.008),
              (XI1 - 0.010, gy, gz)]
    zm = ZM + CABLE_R + 0.0005
    out = [(BX1 + 0.026, gy, gz), (BX1 + 0.055, gy + 0.004, gz - 0.008), (0.30, 0.315, 0.965),
           (0.42, 0.315, ZS + CABLE_R), (0.548, 0.298, zm), (0.566, 0.200, zm), (0.570, 0.040, zm),
           (0.572, -0.021, ZM + 0.0085)]
    k, sides = (2, 6) if lod == 0 else (1, 4)
    if lod == 0:
        g.pipe(cb, spline(inside, k), CABLE_R, sides)
    g.pipe(cb, spline(out, k), CABLE_R, sides)
    parts.append(cb)
    # socket at the probe plug (along +x) and plug at the radiometer (along -y): body, union nut
    pl = P("cable_plugs", "chrome")
    g.cyl(pl, tuple(M69_PLUG + Vector((0.0072, 0.0, 0.0))), "x", 0.0082, 0.0145, n)
    g.cyl(pl, (0.572, -0.034, ZM + 0.0085), "y", 0.0082, 0.024, n)
    parts.append(pl)
    if lod == 0:
        nt = P("cable_nuts", "black")
        g.cyl(nt, tuple(M69_PLUG + Vector((0.0175, 0.0, 0.0))), "x", 0.0062, 0.008, 8)
        g.cyl(nt, (0.572, -0.017, ZM + 0.0085), "y", 0.0062, 0.008, 8)
        parts.append(nt)
    return parts


# =============================================================================
# Module shelf to the right of the airlock
# =============================================================================
def build_shelf(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    mt = P("shelf_mat", "rubber")
    g.box(mt, HX0 + 0.015, HX1 - 0.015, SY0 + 0.03, SY1 - 0.03, ZS - 0.001, ZM,
          **(dict(r=0.002, seg=1) if lod == 0 else {}))
    rl = P("shelf_rails", "steel")
    kw = dict(r=0.0015, seg=1) if lod == 0 else {}
    g.box(rl, HX0, HX1, SY1 - 0.015, SY1 - 0.005, ZS, ZS + 0.04, **kw)
    g.box(rl, HX1 - 0.01, HX1, SY0, SY1 - 0.005, ZS, ZS + 0.04, **kw)
    if lod == 0:
        g.box(rl, HX0, HX1 - 0.01, SY0, SY0 + 0.008, ZS, ZS + 0.015, **kw)
    return [mt, rl]


# =============================================================================
# Roof: filters, draft gauge with a needle, valve with a pipe to the airlock
# =============================================================================
# filter housing (from the roof up): flange, cup with a rib, lid rim, lid
FILTER = [(0.094, 0.0), (0.094, 0.010), (0.078, 0.013), (0.078, 0.068), (0.081, 0.071), (0.081, 0.081),
          (0.078, 0.084), (0.078, 0.150), (0.084, 0.156), (0.080, 0.166), (0.060, 0.168)]
FILTER1 = [(0.094, 0.0), (0.094, 0.010), (0.078, 0.014), (0.078, 0.152), (0.084, 0.160), (0.060, 0.168)]
NEEDLE = [(-0.012, -0.0018), (0.0, -0.0022), (0.046, -0.0006), (0.048, 0.0), (0.046, 0.0006), (0.0, 0.0022),
          (-0.012, 0.0018)]


def needle_poly(pts):
    """Needle in the scale plane (x, z): (along, across) -> world; at rest on NEEDLE_REST divisions (the
    0..60 scale over 270 degrees clockwise from the lower-left corner, as in make_decals.py)."""
    th = math.radians(-(135.0 + 270.0 * NEEDLE_REST / 60.0))
    d, pv = (math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))
    return [(GX + a * d[0] + b * pv[0], GZ + a * d[1] + b * pv[1]) for a, b in pts]


def build_roof(spec):
    lod = spec["lod"]
    parts = []
    n = 14 if lod == 0 else (8 if lod == 1 else 6)
    for i, fx in enumerate((BXC - 0.30, BXC + 0.30)):
        c = (fx, 0.20, ZR)
        fl = P("filter%d" % i, "filter", uv_name="filter", uv_origin=c)
        lathe(fl, FILTER if lod == 0 else FILTER1, n, c, (0, 0, 1))
        if i == 0 or lod == 2:
            disc(fl, (fx, 0.20, ZR + 0.168), (0, 0, 1), 0.060, n)
        parts.append(fl)
        if i == 1 and lod < 2:
            gr = P("filter_grille", "grille_h")
            disc(gr, (fx, 0.20, ZR + 0.1675), (0, 0, 1), 0.060, n)
            parts.append(gr)
        if lod == 0:
            pts = [(fx + 0.086 * math.cos(a), 0.20 + 0.086 * math.sin(a), ZR + 0.010)
                   for a in (math.radians(90 + 120 * k) for k in range(3))]
            parts += bolts("filter%d_bolt" % i, "steel", pts, (0, 0, 1), 0.0055, 0.0045, uv_name="filter_bolt")
    if lod == 2:
        return parts
    # exhaust (left) - a pipe backward toward the ventilation, a flange at the end
    st = P("exhaust", "steel")
    fx = BXC - 0.30
    g.cyl(st, (fx, 0.355, ZR + 0.10), "y", 0.028, 0.15, 12 if lod == 0 else 6)
    if lod == 0:
        lathe(st, [(0.0285, -0.006), (0.042, -0.006), (0.042, 0.006), (0.0285, 0.006)], 12, (fx, 0.418, ZR + 0.10),
              (0, 1, 0))
    parts.append(st)
    # draft gauge: body, back plate, post with a fitting, scale, rim, needle (bone ozl_needle)
    ng = 16 if lod == 0 else 8
    c = (GX, GY, GZ)
    gb = P("gauge_body", "black")
    lathe(gb, [(0.045, -0.024), (0.060, -0.021), (0.064, -0.014), (0.064, 0.014)], ng, c, (0, -1, 0))
    disc(gb, (GX, GY + 0.024, GZ), (0, 1, 0), 0.045, ng)
    parts.append(gb)
    gs = P("gauge_stem", "steel")
    g.cyl(gs, (GX, GY + 0.004, (ZR + GZ - 0.062) / 2), "z", 0.0065, GZ - 0.062 - ZR, 8 if lod == 0 else 4)
    if lod == 0:
        bolt(gs, (GX, GY + 0.004, ZR), (0, 0, 1), 0.013, 0.012)
        bolt(gs, (GX, GY + 0.004, GZ - 0.075), (0, 0, 1), 0.010, 0.010)
    parts.append(gs)
    gf = P("gauge_face", "gauge")
    disc(gf, (GX, FACE_Y, GZ), (0, -1, 0), 0.058, ng)
    parts.append(gf)
    bz = P("gauge_bezel", "chrome")
    lathe(bz, [(0.0655, 0.012), (0.0662, 0.019), (0.0630, 0.0245), (0.0585, 0.025), (0.0575, 0.021)] if lod == 0 else
          [(0.0655, 0.012), (0.0655, 0.024), (0.0575, 0.024)], ng, c, (0, -1, 0))
    parts.append(bz)
    nd = P("gauge_needle", "black", group=SEL_NEEDLE)
    g.prism(nd, needle_poly(NEEDLE if lod == 0 else [NEEDLE[k] for k in (0, 3, 6)]), (0, 2), FACE_Y - 0.0030,
            FACE_Y - 0.0018)
    if lod == 0:
        g.cyl(nd, (GX, FACE_Y - 0.003, GZ), "y", 0.0045, 0.003, 8)
    parts.append(nd)
    # valve: a pipe from the roof, a cast body along x (blank on the left), cap nut, stem, hand wheel
    nv = 10 if lod == 0 else 6
    vb = P("valve", "steel")
    g.cyl(vb, (VX, VY, ZR + 0.025), "z", 0.014, 0.05, nv)
    lathe(vb, [(0.012, -0.042), (0.016, -0.034), (0.016, -0.024), (0.027, -0.010), (0.027, 0.010), (0.016, 0.024),
               (0.016, 0.034), (0.012, 0.042)] if lod == 0 else
          [(0.014, -0.040), (0.026, 0.0), (0.014, 0.040)], nv, (VX, VY, ZR + 0.07), (1, 0, 0))
    disc(vb, (VX - (0.042 if lod == 0 else 0.040), VY, ZR + 0.07), (-1, 0, 0), 0.012 if lod == 0 else 0.014, nv)
    if lod == 0:
        bolt(vb, (VX, VY, ZR + 0.094), (0, 0, 1), 0.016, 0.018)
        g.cyl(vb, (VX, VY, ZR + 0.124), "z", 0.0045, 0.024, 6)
    parts.append(vb)
    vw = P("valve_wheel", "red")
    torus(vw, (VX, VY, ZR + 0.137), (0, 0, 1), 0.034, 0.005, 12 if lod == 0 else 8, 4 if lod == 0 else 3)
    if lod == 0:
        g.cyl(vw, (VX, VY, ZR + 0.137), "z", 0.008, 0.012, 8)
        for k in range(3):
            a = math.radians(90 + 120 * k)
            g.pipe(vw, [(VX + 0.006 * math.cos(a), VY + 0.006 * math.sin(a), ZR + 0.139),
                        (VX + 0.031 * math.cos(a), VY + 0.031 * math.sin(a), ZR + 0.137)], 0.0035, 4)
    parts.append(vw)
    # pipe from the valve along the roof, down the right wall and into the top of the airlock:
    # bends, union nut, clamps
    pp = P("lock_pipe", "steel")
    xw, xd = BX1 + 0.022, LX - 0.07
    zd = LZ + math.sqrt(LR * LR - (LX - xd) ** 2)
    path = [(VX + 0.040, VY, ZR + 0.07), (xw, VY, ZR + 0.07), (xw, VY, zd + 0.06), (xd, VY, zd + 0.06),
            (xd, VY, zd + 0.012)]
    g.pipe(pp, bends(path, 0.03, 3) if lod == 0 else path, 0.010, 6 if lod == 0 else 4)
    if lod == 0:
        bolt(pp, (xd, VY, zd - 0.004), (0, 0, 1), 0.016, 0.016)
        for z in (ZR - 0.10, LZ + 0.30):
            g.box(pp, BX1, xw + 0.004, VY - 0.012, VY + 0.012, z - 0.010, z + 0.010, r=0.002, seg=1)
    parts.append(pp)
    return parts


# =============================================================================
# Base: legs with feet, frame, top, lower shelf, valve panel, waste unit, drain
# =============================================================================
def build_stand(spec):
    lod = spec["lod"]
    parts = []
    st = P("stand", "stand")
    kw = dict(r=0.003, seg=1) if lod == 0 else {}
    z_leg = 0.03 if lod == 0 else 0.0
    legs = [(x, y) for x in (SX0 + 0.02, SX1 - 0.02) for y in (SY0 + 0.02, SY1 - 0.02)]
    for x, y in legs:
        g.box(st, x - 0.02, x + 0.02, y - 0.02, y + 0.02, z_leg, ZS - 0.025, **kw)
    g.box(st, SX0, SX1, SY0, SY1, ZS - 0.025, ZS, **kw)
    g.box(st, SX0, SX1, SY0, SY1, 0.14, ZL, **kw)
    if lod < 2:
        for y0, y1 in ((SY0, SY0 + 0.04), (SY1 - 0.04, SY1)):
            g.box(st, SX0 + 0.04, SX1 - 0.04, y0, y1, ZS - 0.065, ZS - 0.025)
            g.box(st, SX0 + 0.04, SX1 - 0.04, y0, y1, 0.10, 0.14)
        for x0, x1 in ((SX0, SX0 + 0.04), (SX1 - 0.04, SX1)):
            g.box(st, x0, x1, SY0 + 0.04, SY1 - 0.04, ZS - 0.065, ZS - 0.025)
        # valve panel under the box front
        g.box(st, BXC - 0.20, BXC + 0.20, SY0 - 0.008, SY0, 0.72, ZS - 0.065,
              **(dict(r=0.002, seg=1) if lod == 0 else {}))
    parts.append(st)
    if lod == 0:
        # adjustable feet: rubber heel, screw, lock nut
        for i, (x, y) in enumerate(legs):
            ft = P("foot%d" % i, "rubber", uv_name="foot", uv_origin=(x, y, 0.0))
            lathe(ft, [(0.024, 0.0), (0.024, 0.006), (0.019, 0.011), (0.009, 0.012)], 8, (x, y, 0.0), (0, 0, 1))
            disc(ft, (x, y, 0.012), (0, 0, 1), 0.009, 8)
            fs = P("foot_screw%d" % i, "steel", uv_name="foot_screw", uv_origin=(x, y, 0.0))
            g.cyl(fs, (x, y, 0.021), "z", 0.0055, 0.018, 8, cap=False)
            bolt(fs, (x, y, 0.024), (0, 0, 1), 0.012, 0.006)
            parts += [ft, fs]
    if lod == 2:
        return parts
    # panel valves: hexagonal body, stem, hand wheel; empty tags above them
    for k in range(3):
        x = BXC - 0.12 + 0.12 * k
        c = (x, SY0 - 0.008, 0.79)
        vv = P("panel_valve%d" % k, "steel", uv_name="panel_valve", uv_origin=c)
        bolt(vv, c, (0, -1, 0), 0.015, 0.016)
        if lod == 0:
            g.cyl(vv, (x, SY0 - 0.031, 0.79), "y", 0.004, 0.014, 6)
        parts.append(vv)
        vh = P("panel_wheel%d" % k, "black", uv_name="panel_wheel", uv_origin=c)
        if lod == 0:
            torus(vh, (x, SY0 - 0.039, 0.79), (0, 1, 0), 0.017, 0.0035, 10, 4)
            g.box(vh, x - 0.016, x + 0.016, SY0 - 0.041, SY0 - 0.037, 0.788, 0.792)
            g.box(vh, x - 0.002, x + 0.002, SY0 - 0.041, SY0 - 0.037, 0.774, 0.806)
        else:
            g.cyl(vh, (x, SY0 - 0.034, 0.79), "y", 0.017, 0.012, 6)
        parts.append(vh)
    if lod == 0:
        tg = P("panel_tags", "plate")
        for k in range(3):
            x = BXC - 0.12 + 0.12 * k
            g.box(tg, x - 0.018, x + 0.018, SY0 - 0.0095, SY0 - 0.008, 0.826, 0.842)
        parts.append(tg)
    # solid-waste removal unit: a pipe from the box floor with flanges, a slide gate with a handle, a bayonet cap
    wx, wy = WASTE
    n = 12 if lod == 0 else 6
    wp = P("waste_pipe", "stand")
    if lod == 0:
        lathe(wp, [(0.055, 0.520), (0.055, 0.648)], n, (wx, wy, 0.0), (0, 0, 1))
        lathe(wp, [(0.0555, 0.648), (0.074, 0.648), (0.074, 0.660)], n, (wx, wy, 0.0), (0, 0, 1))
        lathe(wp, [(0.074, 0.700), (0.074, 0.712), (0.0555, 0.712)], n, (wx, wy, 0.0), (0, 0, 1))
        lathe(wp, [(0.055, 0.712), (0.055, 0.866)], n, (wx, wy, 0.0), (0, 0, 1))
        lathe(wp, [(0.0555, 0.866), (0.075, 0.866), (0.075, ZS - 0.025)], n, (wx, wy, 0.0), (0, 0, 1))
    else:
        lathe(wp, [(0.055, 0.520), (0.055, ZS - 0.025)], n, (wx, wy, 0.0), (0, 0, 1))
    parts.append(wp)
    wg = P("waste_gate", "steel")
    g.box(wg, wx - 0.08, wx + 0.08, wy - 0.075, wy + 0.075, 0.660, 0.700, **(dict(r=0.004, seg=1) if lod == 0 else {}))
    lathe(wg, [(0.058, 0.490), (0.066, 0.493), (0.066, 0.517), (0.058, 0.521)], n, (wx, wy, 0.0), (0, 0, 1))
    disc(wg, (wx, wy, 0.490), (0, 0, -1), 0.058, n)
    if lod == 0:
        g.pipe(wg, [(wx + 0.08, wy, 0.68), (wx + 0.16, wy, 0.68)], 0.006, 8)
        for k in range(3):                                         # bayonet lugs
            a = math.radians(30 + 120 * k)
            g.box(wg, wx + 0.064 * math.cos(a) - 0.008, wx + 0.064 * math.cos(a) + 0.008,
                  wy + 0.064 * math.sin(a) - 0.008, wy + 0.064 * math.sin(a) + 0.008, 0.496, 0.512)
    parts.append(wg)
    if lod == 0:
        kn = P("waste_knob", "black")
        g.cyl(kn, (wx + 0.166, wy, 0.68), "y", 0.009, 0.06, 8)
        parts.append(kn)
    # liquid-waste drain: a neck from the floor, a tap with a lever, a fitting, a hose into the jerrycan
    dx, dy = DRAIN
    dp = P("drain", "steel")
    g.cyl(dp, (dx, dy, 0.8725), "z", 0.011, 0.045, 10 if lod == 0 else 6)
    bolt(dp, (dx, dy, 0.832), (0, 0, 1), 0.016, 0.018)
    g.cyl(dp, (dx, dy, 0.822), "z", 0.008, 0.02, 8 if lod == 0 else 4)
    parts.append(dp)
    hs = P("drain_hose", "rubber")
    hose = [(dx, dy, 0.814), (dx - 0.004, dy - 0.012, 0.74), (dx - 0.05, dy - 0.07, 0.60),
            (CAN_CAP[0], CAN_CAP[1], 0.50), (CAN_CAP[0], CAN_CAP[1], CAN[4] + 0.034)]
    g.pipe(hs, spline(hose, 3) if lod == 0 else hose, 0.008, 6 if lod == 0 else 4)
    parts.append(hs)
    if lod == 0:
        lv = P("drain_lever", "red")
        g.box(lv, dx, dx + 0.07, dy - 0.005, dy + 0.005, 0.838, 0.844, r=0.002, seg=1)
        parts.append(lv)
    return parts


# =============================================================================
# Lower shelf: liquid-waste jerrycan, lead container, lead bricks (spare)
# =============================================================================
PIG_PROF = [(0.100, 0.0), (0.108, 0.005), (0.110, 0.014), (0.110, 0.226), (0.108, 0.232), (0.1155, 0.234),
            (0.1155, 0.262), (0.111, 0.268), (0.060, 0.272)]


def build_props(spec):
    lod = spec["lod"]
    parts = []
    n = 16 if lod == 0 else (10 if lod == 1 else 8)
    pg = P("pig", "lead")
    lathe(pg, PIG_PROF if lod == 0 else [PIG_PROF[k] for k in (0, 3, 6, 8)], n, PIG, (0, 0, 1))
    disc(pg, (PIG[0], PIG[1], PIG[2] + 0.272), (0, 0, 1), 0.060, n)
    parts.append(pg)
    if lod == 2:
        return parts
    if lod == 0:
        ey = P("pig_eye", "steel")
        lathe(ey, [(0.020, 0.2715), (0.020, 0.278), (0.010, 0.286)], 8, PIG, (0, 0, 1))
        torus(ey, (PIG[0], PIG[1], PIG[2] + 0.302), (1, 0, 0), 0.020, 0.0055, 10, 4)
        parts.append(ey)
        pts = [(PIG[0] + 0.088 * math.cos(a), PIG[1] + 0.088 * math.sin(a), PIG[2] + 0.2698)
               for a in (math.radians(45 + 90 * k) for k in range(4))]
        parts += bolts("pig_bolt", "steel", pts, (0, 0, 1), 0.0065, 0.005)
    x0, x1, y0, y1, ztop = CAN
    cn = P("canister", "canister")
    g.box(cn, x0, x1, y0, y1, ZL, ztop, r=0.02, seg=1)
    if lod == 0:
        hx = x0 + 0.05
        g.pipe(cn, bends([(hx, y0 + 0.05, ztop - 0.004), (hx, y0 + 0.05, ztop + 0.035), (hx, y1 - 0.10, ztop + 0.035),
                          (hx, y1 - 0.10, ztop - 0.004)], 0.018, 2), 0.011, 6)
    g.cyl(cn, (CAN_CAP[0], CAN_CAP[1], ztop + 0.002), "z", 0.022, 0.012, 12 if lod == 0 else 6)
    parts.append(cn)
    cc = P("canister_cap", "cap_red")
    lathe(cc, [(0.025, ztop + 0.008), (0.025, ztop + 0.030), (0.021, ztop + 0.034)], 12 if lod == 0 else 6,
          (CAN_CAP[0], CAN_CAP[1], 0.0), (0, 0, 1))
    disc(cc, (CAN_CAP[0], CAN_CAP[1], ztop + 0.034), (0, 0, 1), 0.021, 12 if lod == 0 else 6)
    parts.append(cc)
    br = P("bricks", "lead_bare")
    kw = dict(r=0.003, seg=1) if lod == 0 else {}
    for bx, by, bz in ((0.40, 0.075, 0.0), (0.41, 0.185, 0.0), (0.405, 0.125, 0.05)):
        g.box(br, bx, bx + 0.20, by, by + 0.10, ZL + bz, ZL + bz + 0.05, **kw)
    parts.append(br)
    return parts


# =============================================================================
# Inside the box: sample tray, cup and lid, tongs, tray under M71, drain, light
# =============================================================================
def build_inside(spec):
    lod = spec["lod"]
    parts = []
    # chamber light on the back wall (the body on two brackets, the diffuser is ozl_lamp): below the
    # ceiling, so it is visible from the window in "work"
    x0, x1 = LAMP
    yw = YB - WALL
    lh = P("lamp_housing", "steel")
    g.box(lh, x0, x1, yw - 0.040, yw - 0.012, LAMP_Z - 0.035, LAMP_Z + 0.035,
          **(dict(r=0.004, seg=1) if lod == 0 else {}))
    if lod == 0:
        for xb in (x0 + 0.05, x1 - 0.05):
            g.box(lh, xb - 0.012, xb + 0.012, yw - 0.013, yw, LAMP_Z - 0.025, LAMP_Z + 0.025)
    parts.append(lh)
    lp = P("lamp_tube", "lamp_tube", group=SEL_LAMP)
    g.box(lp, x0 + 0.02, x1 - 0.02, yw - 0.049, yw - 0.039, LAMP_Z - 0.026, LAMP_Z + 0.026)
    parts.append(lp)
    if lod == 2:
        return parts
    tx0, tx1, ty0, ty1, th = SAMPLE_TRAY
    st = P("sample_tray", "alu")
    if lod == 0:
        open_tray(st, tx0, tx1, ty0, ty1, ZF, th, 0.0015, lip=0.002)
    else:
        g.box(st, tx0, tx1, ty0, ty1, ZF, ZF + 0.004)
    parts.append(st)
    sn = P("sample", "stone")
    stone(sn, (STONE[0], STONE[1], ZF + 0.0015 + 0.0225), (0.042, 0.034, 0.03), 3 if lod == 0 else 2)
    parts.append(sn)
    # lead cup (walls, inner floor) and its lid with a handle next to it on the floor
    cp = P("cup", "lead_cup")
    if lod == 0:
        n = 12
        lathe(cp, [(0.038, 0.0), (0.040, 0.003), (0.040, 0.082), (0.036, 0.085), (0.027, 0.085), (0.026, 0.020)], n,
              (CUP[0], CUP[1], ZF), (0, 0, 1))
        disc(cp, (CUP[0], CUP[1], ZF + 0.020), (0, 0, 1), 0.026, n)
        lathe(cp, [(0.046, 0.0), (0.046, 0.012), (0.043, 0.015), (0.013, 0.015), (0.012, 0.030), (0.010, 0.032)], n,
              (LID[0], LID[1], ZF), (0, 0, 1))
        disc(cp, (LID[0], LID[1], ZF + 0.032), (0, 0, 1), 0.010, n)
    else:
        g.cyl(cp, (CUP[0], CUP[1], ZF + 0.0425), "z", 0.040, 0.085, 8)
    parts.append(cp)
    # steel tray under the lead house M71 (slot 3): when empty, a tray with a rim
    ct = P("castle_tray", "steel")
    cx0, cx1, cy0, cy1 = S3[0] - 0.12, S3[0] + 0.12, S3[1] - 0.095, S3[1] + 0.095
    if lod == 0:
        open_tray(ct, cx0, cx1, cy0, cy1, ZF, 0.010, TRAY_T)
    else:
        g.box(ct, cx0, cx1, cy0, cy1, ZF, ZF + TRAY_T)
    parts.append(ct)
    if lod == 1:
        return parts
    # crucible tongs on the floor in front of the house and the tray: two arms crossed, a pivot
    tg = P("tongs", "steel")
    yc, zt, xs = 0.125, ZF + 0.003, 0.12
    for s in (-1, 1):
        lift = 0.006 if s > 0 else 0.0
        pts = [(-0.62 + xs, yc + 0.020 * s, zt), (-0.56 + xs, yc + 0.014 * s, zt + lift * 0.3),
               (-0.50 + xs, yc + 0.006 * s, zt + lift * 0.7), (-0.46 + xs, yc, zt + lift),
               (-0.42 + xs, yc - 0.008 * s, zt + lift * 0.7), (-0.395 + xs, yc - 0.010 * s, zt + lift * 0.3),
               (-0.380 + xs, yc - 0.004 * s, zt)]
        g.pipe(tg, pts, 0.003, 5)
    g.cyl(tg, (-0.46 + xs, yc, zt + 0.003), "z", 0.0045, 0.011, 8)
    parts.append(tg)
    # floor drain grille
    dr = P("floor_drain", "grille_h")
    disc(dr, (DRAIN[0], DRAIN[1], ZF + 0.0008), (0, 0, 1), 0.022, 12)
    parts.append(dr)
    dg = P("floor_drain_ring", "steel")
    lathe(dg, [(0.029, 0.0), (0.029, 0.0012), (0.022, 0.0016)], 12, (DRAIN[0], DRAIN[1], ZF), (0, 0, 1))
    parts.append(dg)
    return parts


def build_lod(spec):
    parts = [build_shell(spec)]
    if spec["lod"] < 2:
        parts.append(build_glass())
    parts += build_window_frame(spec) + build_ports(spec) + build_gloves(spec) + build_panel(spec)
    parts += build_box_details(spec) + build_lock(spec) + build_cables(spec) + build_shelf(spec)
    parts += build_roof(spec) + build_stand(spec) + build_props(spec) + build_inside(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    stand = kx.box_pts(SX0, SX1, SY0, SY1, 0.0, ZS)
    box = kx.prism_pts([(YF - 0.03, ZS), (YB, ZS), (YB, ZR), (y_out(ZR), ZR), (YF - 0.03, ZK)], BX0, BX1)
    # a collision component thinner than 0.5 m does not work: the airlock and roof go down into the base
    # and the box; convex parts may overlap
    lock = kx.box_pts(0.0, LX + LR + 0.02, LY0 - 0.095, LY1, 0.60, LZ + LR + 0.01)
    roof = kx.box_pts(BX0 + 0.08, BX1 - 0.06, -0.15, 0.36, 1.30, ZTOP)
    metal = kx.PEN + r"\metalplate.rvmat"
    comps = [(stand, metal), (box, metal), (lock, metal), (roof, metal)]
    memory = {
        "invView": [(-0.2, -2.8, 1.2)],
        "ce_center": [(0.0, 0.0, ZTOP / 2)],
        "ce_radius": [(1.3, 0.0, ZTOP / 2)],
        "ozl_needle_axis": NEEDLE_AXIS,                      # toward the person (-Y), see NEEDLE_AXIS
    }
    for i, m in enumerate(MODS):
        memory["module_%d" % (i + 1)] = [m]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2] + 0.004)
    return comps, 220.0, memory, bbox


# the first ones are for the --look preview: overview, the inside through the window (modules M69 and
# M71 in place, and again empty), the airlock and shelf with M70, glove rings and panel, the inside
# from above (gloves on the floor), roof, lower shelf
SHOTS = [
    ("front", (-0.9, -2.7, 1.75), (0.0, 0.0, 1.0), 30),
    ("inside", (BXC + 0.05, -1.05, 1.85), (BXC, 0.10, 0.98), 30),
    ("shelf", (1.15, -1.15, 1.55), (0.52, -0.02, 1.0), 34),
    ("ports", (-0.20, -1.15, 1.30), (-0.18, -0.38, 1.12), 34),
    ("gloves_in", (BXC, -0.62, 1.78), (BXC, -0.02, 0.96), 34),
    ("roof", (BXC + 0.25, -0.95, 2.25), (BXC + 0.05, 0.05, 1.76), 34),
    ("lower", (0.4, -1.7, 0.75), (0.0, 0.0, 0.35), 32),
    ("back", (1.6, 2.2, 1.7), (0.0, 0.0, 0.9), 30),
]
M.look_shots = (7, 2)
if GLOVES_OUT:
    # "gloves outside" variant: overview and a close-up of the gloves (frames look_out_*, see shoot_out)
    SHOTS = [SHOTS[0], ("gloves", (-0.05, -1.55, 1.15), (-0.34, -0.45, 0.95), 34)] + SHOTS[1:3]
    M.look_shots = (2, 1)
def _posed(place):
    """Preview of the "work" look: the draft-gauge needle at the middle of the tremble, by the engine
    rotation (engine_turn: the preview shows what will be in game). kmodel can only translate (move), so
    the rotation is done here by a wrapper over krender (as in M10); it does not go into the p3d - the
    animation is in model.cfg."""
    def wrapped(parts, *a, **kw):
        obs = place(parts, *a, **kw)
        if kw.get("move") is ON_MOVE:
            o, ax, ang = engine_turn(NEEDLE_AXIS, NEEDLE_MID * NEEDLE_SWING)
            for p, ob in zip(parts, obs):
                if p.group == SEL_NEEDLE:
                    loc = Vector(ob.location)
                    cc = o + loc
                    ob.matrix_world = (Matrix.Translation(cc) @ Matrix.Rotation(ang, 4, ax) @ Matrix.Translation(-cc) @
                                       Matrix.Translation(loc))
        return obs
    return wrapped


krender.place_look = _posed(krender.place_look)
krender.place = _posed(krender.place)

M.run(build_lod, collision, SHOTS, row_step=2.0, row_shot=((2.0, -6.4, 2.2), (2.0, 0, 0.85)))
