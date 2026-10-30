"""M04 - measuring chamber with an instrument rack on a laboratory cabinet: the Scientists' Anomaly
Analyzer (OZL_Eco_Proc_Anom). Processor: cargo 4x4, no modules (no module_1..3 points).

    blender --background --python build_m04.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (radiation sign, instrument scales,
recorder scale, knob limbs; analyzer digits and recorder tape: "off" and "work" frames).

The chamber is a low-background lead shield for gamma spectrometry of samples, sized after the ORTEC
HPLBS1 ("HPLBS Series" spec, 2014): cast lead 101 mm in a 12.7 mm steel shell, chamber diameter
28 x 40 cm (for a 4 l Marinelli beaker), outside diameter 51 x 63 cm, 1134 kg, top of the chamber
1.39-1.54 m above the floor. Here the lead is bare and dark, held by steel bands; there is one lid,
hinged back, with a handle at the front (the ORTEC has two halves on vertical axes). The detector
enters the chamber from below through the worktop; the detector cables run from a side gland to the rack.

The instrument rack on the right is a benchtop frame for three units, like Soviet radiometric
installations of the 1970-80s: at the bottom a KSP4 recorder (type description in the USSR State
Register of Measuring Instruments, 04244-81: 400 x 400 x 367 mm, chart width 250 mm, LPGS-250
tape), above it a pulse analyzer (AI-1024, a single-unit instrument with the controls on the front
panel) with gas-discharge digit indicators, at the top a radiometer-intensity meter with panel
pointer meters (like the M4200). The cabinet is the B9 base (as in M02), worktop at 0.80 m.

The whole model is 1.22 x 1.53 x 0.72 m. A real shield with a 10 cm wall is 0.51 m in diameter and
0.63 m high, and a 1.0 m rack does not fit beside it, hence the overall size. Sizes and shape match
the version already accepted.

Built with kmodel (the "dayz" look); the shield has 48 sides. The B9 cabinet is its own
(kfurn.lab_cabinet is left untouched: the accepted M02 and M35 use it). Small props are vanilla DayZ
items through proxies (kvanilla): a journal (sheet of paper), a pen, analyzer punch cards, iodine and
anti-radiation pills, a screwdriver, a GP-5 gas mask.

"Work" look (the OZL_WorkFx.c loop of the mod, class OZL_Work in config.cpp): the chamber lid closes
(bone ozl_lid, pose, 1.8 s) and opens after the work; the recorder pen draws an uneven curve (bone
ozl_pen - three translations on the sources ozl_pen, ozl_pen_2, ozl_pen_3, wobble), the tape creeps
down and under the pen is the same trace (72 frames of ozl_screen_2 at 0.1 s, layout.py); the
analyzer digits count pulses (64 frames of ozl_screen, glow); the intensity meter needle trembles
(bone ozl_needle, wobble); the kilovoltmeter needle goes to the working voltage (bone ozl_needle_2,
pose); the count lamp blinks (ozl_lamp_blink); the "power" and "high voltage" lamps are lit
(ozl_lamp). Needles: 0 is the scale zero, 1 is the end (80 degrees clockwise); the axis points to
the player, the sign of the angle is as in M14.

Lid: at rest (idle) it is tilted back, showing the chamber with its copper lining, the detector and
the sample jar; the swing bolt hangs down. The sign of the lid angle is checked numerically by the
engine rule (check_lid_axis).

Blender axes: X is width, Y is depth (face toward -Y), Z is up.
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
import krender  # noqa: E402
import kvanilla as kv  # noqa: E402
import layout as LY  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
CX0, CX1, CY0, CY1, ZB = -0.60, 0.60, -0.35, 0.35, 0.80     # cabinet, worktop at ZB
PLINTH, T_TOP = 0.08, 0.03                                   # plinth, worktop thickness
# lead shield
SX, SY = -0.285, -0.05                                       # cylinder axis
R_OUT, R_CAV = 0.255, 0.140                                  # outer radius and chamber radius
Z0 = ZB + 0.020                                              # bottom (on a steel plate)
ZF = Z0 + 0.114                                              # chamber floor
ZS = ZF + 0.400                                              # lid joint = top of the chamber
ZL = ZS + 0.114                                              # top of the lid
BAND = 0.007                                                 # band thickness
ZH = ZS + 0.031                                              # handle axis
HY, HZ = SY + R_OUT + 0.035, ZS + 0.040                      # hinge axis
OPEN_DEG = 95.0                                              # lid at rest: tilted back
ZT_SIGN = (Z0 + ZS) / 2                                      # sign plate
ZG = Z0 + 0.085                                              # cable glands
GLANDS = (SY + 0.035, SY - 0.035)                            # signal and high-voltage
# band clamps are staggered (bottom, top, lid): front right, front left, left at the hook
A_CLAMPS = (math.radians(300.0), math.radians(235.0), math.radians(215.0))
YB = SY - R_OUT - BAND - 0.013                               # swing bolt axis (front)
# instrument rack
RX0, RX1, RY0, RY1 = 0.08, 0.56, -0.21, 0.19
CHK = 0.015                                                  # side panel
IX0, IX1 = RX0 + CHK, RX1 - CHK
ZR0 = ZB + 0.027                                             # top of the lower plate
ZM1 = ZR0 + 0.400                                            # recorder: ZR0..ZM1
ZM2 = ZM1 + 0.142                                            # pulse analyzer: ZM1..ZM2
ZM3 = ZM2 + 0.142                                            # radiometer: ZM2..ZM3
ZRT = ZM3 + 0.014                                            # top of the rack
YP = RY0 + 0.004                                             # face of the panels
TOP = ZRT + 0.0015                                           # on the rack top (grille)
# recorder
KX0, KX1 = 0.12, 0.52                                        # KSP4 face, 400 mm
WX0, WX1, WZ0, WZ1 = 0.14, 0.50, ZR0 + 0.115, ZR0 + 0.385    # window
TX0, TX1 = 0.18, 0.46                                        # tape 280 mm, field 250
TAPE_X = (TX0 + TX1) / 2
FX0 = TX0 + LY.FIELD_X0                                      # left edge of the field = pen zero
Y_CHART = RY0 + 0.030                                        # face of the tape in the window
CH_Z1 = WZ0 + LY.CHART_H                                     # top of the visible tape (the scale is above)
Z_PEN = CH_Z1 - LY.PEN_D                                     # pen line
Y_ROD = RY0 + 0.020                                          # carriage rod
Z_ROD = Z_PEN + 0.014

LOD_SPECS = [
    dict(lod=0, sides=16, shield=40, band=40, cable=6),
    dict(lod=1, sides=8, shield=24, band=20, cable=5),
    dict(lod=2, sides=6, shield=12, band=0, cable=0),
]

REGIONS = {
    "cab": ("cab", 0.6), "worktop": ("worktop", 0.7), "cab_front": ("cab_front", 0.9), "black": ("black", 1.0),
    "chrome": ("chrome", 1.4), "card": ("card", 2.0),
    "steel": ("steel", 1.0), "lead": ("lead", 0.9), "copper": ("copper", 0.9), "band": ("band", 1.0),
    "plate": ("plate_steel", 0.6), "bakelite": ("bakelite", 1.4), "sign": ("sign", 3.0), "inst": ("inst", 0.8),
    "panel": ("panel", 1.6), "dial": ("dial", 3.5), "rec_case": ("rec_case", 1.2),
    "chart": ("chart", 2.2), "pen": ("pen", 1.5), "ink": ("ink", 2.0), "key": ("key", 1.6), "lamp_g": ("lamp_g", 1.6),
    "lamp_r": ("lamp_r", 1.6), "rubber": ("rubber", 0.4), "cable_grey": ("cable_grey", 0.4), "alu": ("alu", 1.2),
    "cup": ("plastic_white", 1.2), "cap_red": ("cap_red", 1.2), "grille_v": ("grille_v", 1.0),
    "grille_h": ("grille_h", 1.0), "dark": ("dark", 0.5), "needle": ("needle", 3.0),
}

# =============================================================================
# Materials
# =============================================================================


def mat_chart(mat, origin):
    """Tape hanging from the recorder (atlas): paper, field grid every 10 and 50 mm, edge perforation, a
    violet pen trace - the same curve the pen writes on the tape in the window (layout.pen_x: a sum of
    three sines; the tape point at length L was written at the moment -L / v)."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 9.0)
    X = sep.outputs["X"]
    L = t.math("ADD", sep.outputs["Y"], sep.outputs["Z"])

    def lines(c, pitch, half):
        f = t.math("FRACT", t.math("DIVIDE", c, pitch))
        d = t.math("MINIMUM", f, t.math("SUBTRACT", 1.0, f))
        return t.math("LESS_THAN", d, half / pitch)
    field = t.math("LESS_THAN", t.math("ABSOLUTE", t.math("SUBTRACT", X, TAPE_X)), 0.1255)
    u = t.math("SUBTRACT", X, FX0)
    fine = t.math("MULTIPLY", t.math("MAXIMUM", lines(u, 0.01, 0.0006), lines(L, 0.01, 0.0006)), field)
    bold = t.math("MULTIPLY", t.math("MAXIMUM", lines(u, 0.05, 0.0011), lines(L, 0.05, 0.0011)), field)
    tx = FX0
    for _, mid, amp, n, dd in LY.PEN:
        sw = t.math("SINE", t.math("MULTIPLY", L, -2 * math.pi * n / LY.TAPE_RUN))
        tx = t.math("ADD", tx, t.math("MULTIPLY", t.math("ADD", mid, t.math("MULTIPLY", sw, amp)), dd))
    ink = t.math("LESS_THAN", t.math("ABSOLUTE", t.math("SUBTRACT", X, tx)), 0.0007)
    # perforation: holes of diameter 3.5 mm every 10 mm, 7.5 mm from the tape edges
    hx = t.math("SUBTRACT", t.math("ABSOLUTE", t.math("SUBTRACT", X, TAPE_X)), (TX1 - TX0) / 2 - 0.0075)
    hl = t.math("MULTIPLY", t.math("SUBTRACT", t.math("FRACT", t.math("DIVIDE", L, 0.010)), 0.5), 0.010)
    hole = t.math("LESS_THAN", t.math("ADD", t.math("MULTIPLY", hx, hx), t.math("MULTIPLY", hl, hl)), 0.00175 ** 2)
    paper = t.mixc(t.maprange(t.noise(vec, 14.0, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0), kmats.lin((240, 236, 222)),
                   kmats.lin((226, 218, 194)))
    col = t.mixc(t.math("MULTIPLY", fine, 0.7), paper, kmats.lin((232, 176, 156)))
    col = t.mixc(bold, col, kmats.lin((204, 112, 88)))
    col = t.mixc(ink, col, kmats.lin((72, 48, 140)))
    col = t.mixc(hole, col, kmats.lin((46, 44, 42)))
    return kmats.out(t, col, 0.12, 0.06, 0.0)


LEAD = dict(color=kmats.lin((72, 75, 80)), under=kmats.lin((150, 152, 156)), seed=7.7, gloss=0.22, spec=0.18,
            chip=(0.68, 0.74), rust=(0.99, 1.0), rust_low=0.0, floor_z=ZB, dust=0.35, grime=0.35)


def mat_lead(mat, origin):
    """Cast lead: over painted metal (chips show light metal) whitish oxide patches and speckles, with
    lower gloss there."""
    outs = kmats.build_paint(mat, origin, **LEAD)
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    vec, sep = t.coords(origin, 12.0)
    blot = t.maprange(t.noise(vec, 3.0, 6.0, 0.6), 0.50, 0.80, 0.0, 1.0)
    speck = t.maprange(t.noise(vec, 40.0, 4.0, 0.6), 0.58, 0.78, 0.0, 1.0)
    ox = t.math("MINIMUM", t.math("ADD", t.math("MULTIPLY", blot, 0.6), t.math("MULTIPLY", speck, 0.3)), 0.8)
    col = t.mixc(ox, kmats.sock(mat, outs["color"]), kmats.lin((138, 140, 138)))
    gl = t.mixf(ox, kmats.sock(mat, outs["gloss"]), 0.08)
    return dict(outs, color=kmats.Tree.ref(col), gloss=kmats.Tree.ref(gl))


def decal(name, center, size, y_face, eps=0.0012):
    return (os.path.join(WORK, name), "y", -1, ("x", "z"), center, size, (y_face - eps, y_face + eps))


def rect_decal(name, r, y_face):
    x0, x1, z0, z1 = r
    return decal(name, ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0), y_face)


# faces: plate (a wider range over the cylinder), panel meters, recorder scale, knob limbs on the panels
TREFOIL = [decal("decal_trefoil.png", (SX, ZT_SIGN), (0.082, 0.082), SY - R_OUT, eps=0.0035)]
M_RATE = (0.124, 0.252, ZM2 + 0.019, ZM2 + 0.123)
M_HV = (0.277, 0.367, ZM2 + 0.051, ZM2 + 0.123)
NIX = (0.121, 0.329, ZM1 + 0.050, ZM1 + 0.102)
SCALE = (WX0 + 0.01, WX1 - 0.01, WZ1 - 0.035, WZ1 - 0.008)
# scale 0..100 (make_decals.make_scale) exactly above the tape field: the pen at zero stands on "0"
assert abs(SCALE[1] - SCALE[0] - LY.SCALE_W) < 1e-9 and abs((SCALE[0] + SCALE[1]) / 2 - FX0 - LY.FIELD_W / 2) < 1e-9
Y_DIAL = YP - 0.0055                                         # face of the meter scales (behind the glass)
DIALS = [rect_decal("decal_meter_rate.png", M_RATE, Y_DIAL), rect_decal("decal_meter_hv.png", M_HV, Y_DIAL),
         rect_decal("decal_scale.png", SCALE, RY0 + 0.022)]
SEL = (0.395, ZM1 + 0.073)                                   # analyzer selector
KNOBS_AN = [(0.462, ZM1 + 0.095)]
KNOBS_RAD = [(0.408, ZM2 + 0.099), (0.468, ZM2 + 0.099)]
RINGS = [decal("decal_ring6.png", SEL, (0.085, 0.085), YP)]
RINGS += [decal("decal_ring10.png", c, (0.050, 0.050), YP) for c in KNOBS_AN]
RINGS += [decal("decal_ring10.png", c, (0.056, 0.056), YP) for c in KNOBS_RAD]


def meter_pivot(rect, wpx, hpx):
    """Needle axis and scale radius (m) - from the scale drawing make_decals.meter_geom."""
    x0, x1, z0, z1 = rect
    r = min(hpx * 0.80, wpx * 0.50)
    sx, sz = (x1 - x0) / wpx, (z1 - z0) / hpx
    return x0 + wpx / 2 * sx, z1 - (hpx * 0.10 + r * 1.27) * sz, r * (sx + sz) / 2


RATE_PIV = meter_pivot(M_RATE, 512, 416)
HV_PIV = meter_pivot(M_HV, 384, 320)
Y_NEEDLE = YP - 0.0070
SWEEP = 80.0                                                 # scale degrees: phase 0 -> 1
RATE_MID, RATE_AMP, RATE_PERIOD = 0.55, 0.05, 0.9           # the intensity meter trembles around 10^2.2
HV_ON = 0.60                                                 # kilovoltmeter at work: 1.2 kV

KINDS = kmats.std_kinds(floor_z=0.0)
LAB = dict(KINDS["enamel_lab"][1])
INST = dict(color=kmats.lin((124, 131, 131)), under=kmats.lin((56, 56, 58)), seed=3.3, gloss=0.45, spec=0.35,
            chip=(0.65, 0.71), rust=(0.70, 0.80), rust_low=0.15, floor_z=ZB, dust=0.30, grime=0.30)
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
KINDS.update({
    "cab": ("paint", LAB),
    "cab_front": ("paint", dict(LAB, seed=2.9)),
    "chrome": ("steel", dict(seed=6.1, tone=0.44, along="x", gloss=0.60, spec=0.70, dust=0.2, grime=0.45)),
    "card": ("plastic", dict(color=kmats.lin((214, 206, 182)), gloss=0.10, spec=0.05, mottle=0.12, dust=0.4,
                             grime=0.5)),
    "lead": (mat_lead, {}),
    "copper": ("paint", dict(color=kmats.lin((150, 86, 52)), under=kmats.lin((90, 50, 30)), seed=6.6, gloss=0.45,
                             spec=0.50, chip=(0.99, 1.0), rust=(0.62, 0.72), rust_low=0.0, floor_z=ZF, dust=0.1,
                             grime=0.3)),
    "band": ("paint", dict(INST, seed=4.9)),
    "inst": ("paint", INST),
    "panel": ("paint", dict(color=kmats.lin((182, 185, 180)), under=kmats.lin((80, 80, 82)), seed=4.4, gloss=0.40,
                            spec=0.30, chip=(0.72, 0.78), rust=(0.99, 1.0), rust_low=0.0, floor_z=ZB, dust=0.12,
                            grime=0.15, decal_items=RINGS)),
    "dial": ("paint", dict(CLEAN, color=kmats.lin((236, 234, 224)), gloss=0.75, spec=0.55, decal_items=DIALS)),
    "rec_case": ("paint", dict(color=kmats.lin((52, 55, 58)), under=kmats.lin((110, 112, 114)), seed=5.1, gloss=0.45,
                               spec=0.35, chip=(0.66, 0.72), rust=(0.99, 1.0), rust_low=0.0, floor_z=ZB, dust=0.25,
                               grime=0.3)),
    "sign": ("paint", dict(CLEAN, color=kmats.lin((236, 186, 22)), gloss=0.5, spec=0.4, decal_items=TREFOIL)),
    "plate_steel": ("steel", dict(seed=7.3, tone=0.26, along="x", floor_z=ZB, dust=0.3, grime=0.4)),
    "alu": ("steel", dict(seed=8.1, tone=0.44, along="z", dust=0.1, grime=0.1)),
    "bakelite": ("plastic", dict(color=kmats.lin((46, 31, 22)), gloss=0.55, spec=0.45, dust=0.2, mottle=0.10,
                                 scuff=(0.75, 0.82))),
    "key": ("plastic", dict(color=kmats.lin((200, 196, 186)), gloss=0.40, spec=0.30, dust=0.15)),
    "pen": ("plastic", dict(color=kmats.lin((170, 30, 30)), gloss=0.5, spec=0.4, dust=0.1)),
    "ink": ("flat", dict(color=kmats.lin((70, 46, 136)), gloss=0.6, spec=0.4)),
    "needle": ("flat", dict(color=kmats.lin((18, 18, 18)), gloss=0.4, spec=0.3)),
    "cable_grey": ("plastic", dict(color=kmats.lin((118, 120, 118)), gloss=0.30, spec=0.2, dust=0.3)),
    "dark": ("flat", dict(color=kmats.lin((16, 16, 17)), gloss=0.2, spec=0.1)),
    "chart": (mat_chart, {}),
    # lamps: "off" - dark lenses, "work" - lit (atlas _on; the count lamp blinks)
    "lamp_g": ("flat", dict(color=kmats.lin((34, 86, 42)), gloss=0.85, spec=0.8)),
    "lamp_r": ("flat", dict(color=kmats.lin((112, 26, 22)), gloss=0.85, spec=0.8)),
    "lamp_g_on": ("flat", dict(color=kmats.lin((150, 255, 150)), gloss=0.85, spec=0.8)),
    "lamp_r_on": ("flat", dict(color=kmats.lin((255, 96, 70)), gloss=0.85, spec=0.8)),
})

# =============================================================================
# Model: work looks, bones, DayZ items
# =============================================================================
OBJ, NAME = "m04_anomaly_analyzer", "ozr_anomaly_analyzer"
SEL_NIXIE, SEL_CHART = "ozl_screen", "ozl_screen_2"          # own texture: the "work" frames
SEL_LAMP, SEL_BLINK = "ozl_lamp", "ozl_lamp_blink"           # atlas _on: lit / blinking
SEL_PEN, SEL_RATE, SEL_HV, SEL_LID = "ozl_pen", "ozl_needle", "ozl_needle_2", "ozl_lid"
GL = SEL_LID                                                 # lid part group (bone)
NIXIE = dict(off="decal_nixie_off.png", frames=["decal_nixie_f%02d.png" % i for i in range(LY.NIXIE_FRAMES)],
             size=256, gloss=0.85)
CHART = dict(off="decal_chart_off.png", frames=["decal_chart_f%02d.png" % i for i in range(LY.CHART_FRAMES)],
             size=256, gloss=0.15)
# preview of the "work" look: the pen sits where its trace is on tape frame 0, the needles and the lid
# are rotated (TURNS, below); this does not go into the p3d - the pose is set by the model.cfg bones
ON_MOVE = {SEL_PEN: (LY.pen_x(LY.frame_time(0)), 0.0, 0.0)}
ON = dict(remap={"lamp_g": "lamp_g_on", "lamp_r": "lamp_r_on"}, emissive=(1.0, 1.0, 1.0, 1.0), move=ON_MOVE)
# the lid is closed in "work": in the preview a rotation by +OPEN_DEG about Blender +x (back to swing)
TURNS = {SEL_RATE: ((RATE_PIV[0], Y_NEEDLE, RATE_PIV[1]), (0.0, 1.0, 0.0), math.radians(SWEEP * RATE_MID)),
         SEL_HV: ((HV_PIV[0], Y_NEEDLE, HV_PIV[1]), (0.0, 1.0, 0.0), math.radians(SWEEP * HV_ON)),
         SEL_LID: ((0.0, HY, HZ), (1.0, 0.0, 0.0), math.radians(OPEN_DEG))}


def needle_anim(sel, src):
    return ("%s_turn" % sel, dict(type="rotation", source=src, selection=sel, axis=sel + "_axis", memory=1,
                                  minValue=0.0, maxValue=1.0, angle0=0.0, angle1=math.radians(SWEEP)))


# pen axis - a metre along +x from the field zero: offset in metres. Three translations of one bone
# on three sources add up (layout.PEN): the main travel - phase = fraction of the field, the other two -
# ripple by D metres
PEN_ANIMS = tuple(("%s_move" % src, dict(type="translation", source=src, selection=SEL_PEN, axis="ozl_pen_axis",
                                         memory=1, minValue=0.0, maxValue=1.0, offset0=0.0, offset1=dd))
                  for src, _, _, _, dd in LY.PEN)
# lid axis - along the hinge from -x to +x Blender. The engine rotates a bone by a positive angle
# clockwise for whoever the axis points at (memory[0] -> memory[1]; that is how the needles of M08,
# M12, M14, M33 work in game): the lid closes counter-clockwise for someone standing at the right (+x),
# so the angle is -OPEN_DEG (checked numerically in check_lid_axis). With +OPEN_DEG the lid would go
# even further back in game
LID_AXIS = ((SX - 0.12, HY, HZ), (SX + 0.12, HY, HZ))
LID_ANIM = ("ozl_lid_close", dict(type="rotation", source="ozl_lid", selection=SEL_LID, axis="ozl_lid_axis",
                                  memory=1, minValue=0.0, maxValue=1.0, angle0=0.0, angle1=-math.radians(OPEN_DEG)))
BONES = ((SEL_PEN, ""), (SEL_RATE, ""), (SEL_HV, ""), (SEL_LID, ""))
ANIMS = PEN_ANIMS + (needle_anim(SEL_RATE, "ozl_needle"), needle_anim(SEL_HV, "ozl_needle_2"), LID_ANIM)
SOURCES = {"ozl_needle": dict(animPeriod=0.2), "ozl_needle_2": dict(animPeriod=1.5),
           "ozl_lid": dict(animPeriod=LY.LID_PERIOD)}
SOURCES.update({src: dict(animPeriod=LY.PEN_ANIM_PERIOD[src]) for src, *_ in LY.PEN})

IODINE, CHELATE = r"dz\gear\medical\IodineTincture", r"dz\gear\medical\ChelatingTablets"
DECOR = [
    # on the rack top: journal (sheet), pen, stack of analyzer punch cards, iodine
    kv.put("paper", (0.245, -0.015, TOP), **kv.flat(86)),
    kv.put("pen", (0.31, -0.075, TOP + 0.0004), **kv.flat(148)),
    kv.put("punchedcard", (0.462, 0.104, TOP), **kv.flat(90)),
    kv.put("punchedcard", (0.466, 0.100, TOP + 0.0011), **kv.flat(84)),
    kv.put("punchedcard", (0.457, 0.108, TOP + 0.0022), **kv.flat(95)),
    kv.put(IODINE, (0.505, -0.148, TOP), up=(0, 0, 1), fwd=(0.3, -1, 0)),
    # on the worktop: anti-radiation pills at the edge, a screwdriver across the recorder tape
    kv.put(CHELATE, (0.538, -0.292, ZB), up=(0, 0, 1), fwd=(-0.4, -1, 0)),
    kv.put("screwdriver", (0.215, -0.322, ZB), lift=0.0018, **kv.flat(6)),
    # GP-5 gas mask on the hook at the left of the shield (facing out)
    kv.put("gp5", (SX - R_OUT - BAND - 0.003, SY, ZS - 0.164), up=(0, 0, 1), fwd=(-1, 0, 0), normal=(-1, 0, 0)),
]


class Model(kmodel.Model):
    def panel_mats(self, on):
        """Preview of "work": the tape does not glow (OZL_Work has only frames for it, the material is
        unchanged), the digits - a frame with a count (frame 0 is a reset, "000000")."""
        out = super().panel_mats(on)
        if on:
            _, frames = self.panel_pngs("chart")
            out["chart"] = krender.panel_material(frames[0], glow=0.0, gloss=CHART["gloss"])
            _, frames = self.panel_pngs("nixie")
            out["nixie"] = krender.panel_material(frames[len(frames) // 2 + 1], glow=1.6, gloss=NIXIE["gloss"])
        return out


M = Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
          glass=dict(base=(0.55, 0.58, 0.56), clear=0.06, edge=0.16, smudge=0.06, streaks=0.03),
          selections=(SEL_NIXIE, SEL_CHART, SEL_LAMP, SEL_BLINK, SEL_PEN, SEL_RATE, SEL_HV, SEL_LID),
          hidden=(SEL_NIXIE, SEL_CHART, SEL_LAMP, SEL_BLINK), states={"on": ON}, bones=BONES, animations=ANIMS,
          decor=DECOR, panels={"nixie": NIXIE, "chart": CHART}, sources=SOURCES)
P = M.part
BOUNDS = {}


# --- preview: the "work" pose with rotations ---------------------------------------------------
# krender sets the look pose only by translation (move); the needles and the lid need rotation. The
# wrappers are here and the library is untouched: the look is recognised by the same move dictionary (ON_MOVE).
def _turn(parts, obs, move):
    if move is not ON_MOVE:
        return obs
    for p, ob in zip(parts, obs):
        t = TURNS.get(p.group)
        if t:
            piv, ax, ang = Vector(t[0]), Vector(t[1]), t[2]
            ob.matrix_world = (Matrix.Translation(piv) @ Matrix.Rotation(ang, 4, ax) @ Matrix.Translation(-piv) @
                               Matrix.Translation(ob.location))
    return obs


_place_look, _place = krender.place_look, krender.place


def _place_look_turn(parts, *a, **kw):
    return _turn(parts, _place_look(parts, *a, **kw), kw.get("move"))


def _place_turn(parts, *a, **kw):
    return _turn(parts, _place(parts, *a, **kw), kw.get("move"))


krender.place_look, krender.place = _place_look_turn, _place_turn


def engine_turn(p, axis, angle):
    """Point p (Blender) after the engine rotates the bone: about the axis memory[0] -> memory[1] by angle
    (rad), right-handed in DayZ axes (which are left-handed), and for whoever the axis points at that is
    clockwise (this is how the lids of the OpenZone_StorageCases boxes, accepted in game, and the M10
    needles were checked) - and back into Blender axes."""
    a, b = (Vector(kx.conv(q)) for q in axis)
    k = (b - a).normalized()
    v = Vector(kx.conv(p)) - a
    q = a + v * math.cos(angle) + k.cross(v) * math.sin(angle) + k * k.dot(v) * (1.0 - math.cos(angle))
    return Vector((-q.x, -q.z, q.y))                          # inverse of kexport.conv


def check_lid_axis():
    """Lid angle sign by number: model.cfg (axis LID_AXIS, angle1) closes the lid the same way as the
    preview (TURNS), and the closed lid lands in place - the handle at the front at its height."""
    grip = Vector((SX, SY - R_OUT - 0.055, ZH))               # handle of the closed lid
    piv = Vector((0.0, HY, HZ))
    rest = Matrix.Rotation(math.radians(-OPEN_DEG), 3, "X") @ (grip - piv) + piv   # as swing: at rest
    want = Matrix.Rotation(TURNS[SEL_LID][2], 3, "X") @ (rest - piv) + piv         # preview of "work"
    got = engine_turn(rest, LID_AXIS, LID_ANIM[1]["angle1"])
    print("lid grip: rest y %.3f z %.3f -> engine y %.3f z %.3f (closed y %.3f z %.3f)" %
          (rest.y, rest.z, got.y, got.z, grip.y, grip.z))
    assert (got - grip).length < 1e-6 and (want - grip).length < 1e-6, "the engine would close the lid the wrong way"
    # needles: preview and engine rotate the same way
    for sel, (pv, ax, ang) in ((SEL_RATE, TURNS[SEL_RATE]), (SEL_HV, TURNS[SEL_HV])):
        tip = Vector(pv) + Vector((0.0, 0.0, 0.02))
        want = Matrix.Rotation(ang, 3, Vector(ax)) @ (tip - Vector(pv)) + Vector(pv)
        axis = ((pv[0], Y_NEEDLE, pv[2]), (pv[0], Y_NEEDLE - 0.05, pv[2]))
        got = engine_turn(tip, axis, ang)
        assert (got - want).length < 1e-6, "needle %s goes a different way in the engine than in the preview" % sel


check_lid_axis()


# =============================================================================
# Primitives missing from kgeo (kept here so that the kit library stays untouched)
# =============================================================================
def U(part, region):
    return part.use(region, *REGIONS[region])


def bev(lod, r, seg):
    return dict(r=r, seg=seg) if lod == 0 else {}


def orient(f, want):
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def basis(axis):
    d = Vector(axis).normalized()
    a = Vector((0.0, 0.0, 1.0)) if abs(d.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    e1 = d.cross(a).normalized()
    return d, e1, d.cross(e1).normalized()


def lathe(part, prof, sides, center, axis=(0.0, 0.0, 1.0), phase=0.0, cap0=False, cap1=False):
    """Body of revolution about axis from the point center: prof [(r, h)] - the section is traversed so that
    the body is on the left (up the outer wall, inward across the top; for a cavity - down its wall),
    faces point out of the body; r = 0 is an apex on the axis (fan). cap0 / cap1 - close the first / last
    ring (against / along the axis). phase - rotation of the rings in fractions of a step (a nut face
    toward the person)."""
    bm = part.bm
    d, e1, e2 = basis(axis)
    c0 = Vector(center)
    rings = []
    for r, h in prof:
        if r < 1e-7:
            rings.append([bm.verts.new(c0 + d * h)])
        else:
            rings.append([bm.verts.new(c0 + d * h + (e1 * math.cos(a) + e2 * math.sin(a)) * r)
                          for a in (2 * math.pi * (k + phase) / sides for k in range(sides))])
    new = []
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        A, B = rings[i], rings[i + 1]
        if len(A) == 1 and len(B) == 1:
            continue
        nr, nh = h1 - h0, r0 - r1                      # outward: the tangent rotated by -90
        for k in range(sides):
            j = (k + 1) % sides
            q = [A[0], B[k], B[j]] if len(A) == 1 else [A[k], A[j], B[0]] if len(B) == 1 else \
                [A[k], A[j], B[j], B[k]]
            f = bm.faces.new(q)
            m = f.calc_center_median() - c0
            rad = m - d * m.dot(d)
            rad = rad.normalized() if rad.length > 1e-9 else e1
            new.append(orient(f, rad * nr + d * nh))
    for ring, want, on in ((rings[0], -d, cap0), (rings[-1], d, cap1)):
        if on and len(ring) > 2:
            new.append(orient(bm.faces.new(ring), want))
    return part.tag(new)


def fluted(part, center, axis, r, depth, n, h0, h1, cap=True):
    """Knurled bushing (instrument knob, knurling): 2n vertices on a circle, every other one sunk by depth;
    cap - close the h1 end."""
    bm = part.bm
    d, e1, e2 = basis(axis)
    c0 = Vector(center)
    rings = [[bm.verts.new(c0 + d * h + (e1 * math.cos(math.pi * k / n) + e2 * math.sin(math.pi * k / n)) *
                           (r - depth * (k % 2))) for k in range(2 * n)] for h in (h0, h1)]
    new = []
    for k in range(2 * n):
        j = (k + 1) % (2 * n)
        f = bm.faces.new([rings[0][k], rings[0][j], rings[1][j], rings[1][k]])
        m = f.calc_center_median() - c0
        new.append(orient(f, m - d * m.dot(d)))
    if cap:
        new.append(orient(bm.faces.new(rings[1]), d))
    return part.tag(new)


def quad_facing(part, corners, want):
    f = part.bm.faces.new([part.bm.verts.new(Vector(c)) for c in corners])
    return part.tag([orient(f, want)])


def axis_matrix(center, axis):
    rot = {"x": Matrix.Rotation(math.pi / 2, 4, "Y"), "y": Matrix.Rotation(math.pi / 2, 4, "X"),
           "z": Matrix.Identity(4)}[axis]
    return Matrix.Translation(center) @ rot


def torus(part, center, axis, R, r, seg, sides):
    """Eyebolt ring (from M03)."""
    bm = part.bm
    m = axis_matrix(center, axis)
    rings = []
    for i in range(seg):
        c, s = math.cos(2 * math.pi * i / seg), math.sin(2 * math.pi * i / seg)
        rings.append([bm.verts.new(m @ Vector(((R + r * math.cos(th)) * c, (R + r * math.cos(th)) * s, r * math.sin(th))))
                      for th in (2 * math.pi * k / sides for k in range(sides))])
    new = []
    for i in range(seg):
        r0, r1 = rings[i], rings[(i + 1) % seg]
        for k in range(sides):
            j = (k + 1) % sides
            new.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, k segments per link): cable and tape
    without kinks on the near LOD."""
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


def arc_plate(part, a0, a1, z0, z1, r0, r1, n):
    """Plate following the shield cylinder: a ring sector r0..r1 between angles a0..a1 (rad) and heights
    z0..z1 (plate, hinge pad)."""
    bm = part.bm
    cols = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        c, s = math.cos(a), math.sin(a)
        cols.append([bm.verts.new((SX + r * c, SY + r * s, z)) for r, z in ((r0, z0), (r1, z0), (r1, z1), (r0, z1))])
    new = []
    up = Vector((0.0, 0.0, 1.0))
    for i in range(n):
        A, B = cols[i], cols[i + 1]
        am = a0 + (a1 - a0) * (i + 0.5) / n
        rad = Vector((math.cos(am), math.sin(am), 0.0))
        for q, want in (([A[1], B[1], B[2], A[2]], rad), ([A[2], B[2], B[3], A[3]], up),
                        ([A[0], B[0], B[1], A[1]], -up)):
            new.append(orient(bm.faces.new(q), want))
    for col, a, sgn in ((cols[0], a0, -1.0), (cols[-1], a1, 1.0)):
        new.append(orient(bm.faces.new(col), Vector((-math.sin(a), math.cos(a), 0.0)) * sgn))
    return part.tag(new)


def u_handle(part, a, b, out, depth, rr, r, sides, lod):
    """Bar handle: from point a on the surface outward by depth, along to b, back; the corners are arcs of
    radius rr (lod > 0 - no arcs)."""
    a, b, out = Vector(a), Vector(b), Vector(out).normalized()
    t = (b - a).normalized()
    if lod > 0:
        pts = [a - out * 0.002, a + out * depth, b + out * depth, b - out * 0.002]
    else:
        ca, cb = a + out * (depth - rr) + t * rr, b + out * (depth - rr) - t * rr
        arc = (0.0, math.pi / 4, math.pi / 2)
        pts = [a - out * 0.002] + [ca - t * rr * math.cos(f) + out * rr * math.sin(f) for f in arc] + \
              [cb + t * rr * math.cos(f) + out * rr * math.sin(f) for f in arc[::-1]] + [b - out * 0.002]
    return g.pipe(part, [tuple(p) for p in pts], r, sides)


def hex_bolt(part, center, axis, r, h, washer=0.0):
    """Hex-head bolt (and a washer, washer being its radius) from point center along axis."""
    if washer:
        lathe(part, [(washer, 0.0), (washer, 0.0016), (0.0, 0.0016)], 12, center, axis)
    h0 = 0.0016 if washer else 0.0
    lathe(part, [(r, h0), (r, h0 + h * 0.82), (r * 0.80, h0 + h), (0.0, h0 + h)], 6, center, axis, phase=0.5)


def dome_screw(name, center, axis=(0.0, -1.0, 0.0), r=0.0034):
    s = P(name, "steel", uv_name="screw%d" % round(r * 10000), uv_origin=center)
    lathe(s, [(r, 0.0), (r * 0.72, 0.0014), (0.0, 0.0019)], 6, center, axis)
    return [s]


# =============================================================================
# Cabinet B9
# =============================================================================
def build_cabinet(spec):
    """B9 base - a laboratory cabinet (like kfurn.lab_cabinet, more detailed): body with rounded edges,
    worktop with a rounded edge, plinth; at the left a door with a stamped panel on two hinges, with a
    bracket handle and a lock; at the right three drawers with brackets, label holders (labels blank)
    and a lock on the top one."""
    lod = spec["lod"]
    x0, x1, y0, y1, top = CX0, CX1, CY0, CY1, ZB
    parts = []
    body = P("cab_body", "cab")
    g.box(body, x0, x1, y0 + 0.02, y1, PLINTH if lod < 2 else 0.0, top - T_TOP, **bev(lod, 0.006, 1))
    parts.append(body)
    wt = P("cab_top", "worktop")
    g.box(wt, x0 - 0.01, x1 + 0.01, y0 - 0.012, y1 + 0.005, top - T_TOP, top, **bev(lod, 0.008, 2))
    parts.append(wt)
    gap, t = 0.004, 0.018
    z_lo, z_hi = PLINTH + gap, top - T_TOP - gap
    yf = y0 + 0.02 - t                                      # face of the fronts
    fr = P("cab_fronts", "cab_front")
    parts.append(fr)
    if lod == 2:
        g.box(fr, x0 + gap, x1 - gap, yf, y0 + 0.02, z_lo, z_hi)
        return parts
    pl = P("cab_plinth", "black")
    g.box(pl, x0 + 0.04, x1 - 0.04, y0 + 0.04, y1 - 0.04, 0.0, PLINTH + 0.002)
    parts.append(pl)
    xm = x0 + gap + (x1 - x0 - gap) * 0.48
    door = (x0 + gap, xm - gap, z_lo + gap / 2, z_hi - gap / 2)
    g.box(fr, door[0], door[1], yf, y0 + 0.02, door[2], door[3], **bev(lod, 0.003, 1))
    drawers = []
    za = z_hi
    for k in range(3):
        zb = za - (z_hi - z_lo) / 3
        drawers.append((xm, x1 - gap, zb + gap / 2, za - gap / 2))
        g.box(fr, *drawers[-1][:2], yf, y0 + 0.02, *drawers[-1][2:], **bev(lod, 0.003, 1))
        za = zb
    hd = P("cab_handles", "chrome")
    sd = 6 if lod == 0 else 4
    out = (0.0, -1.0, 0.0)
    dcx, dcz = door[1] - 0.05, door[3] - 0.12
    u_handle(hd, (dcx, yf, dcz - 0.06), (dcx, yf, dcz + 0.06), out, 0.028, 0.008, 0.0048, sd, lod)
    for d in drawers:
        cx, cz = (d[0] + d[1]) / 2, d[3] - 0.045
        u_handle(hd, (cx - 0.06, yf, cz), (cx + 0.06, yf, cz), out, 0.028, 0.008, 0.0048, sd, lod)
    parts.append(hd)
    if lod > 0:
        return parts
    # stamped door panel
    g.box(fr, door[0] + 0.05, door[1] - 0.05, yf - 0.002, yf + 0.001, door[2] + 0.06, door[3] - 0.06, r=0.002, seg=1)
    # door hinges, locks (door and top drawer), label holders
    hg = P("cab_hinges", "chrome")
    for zc in (door[3] - 0.10, door[2] + 0.10):
        lathe(hg, [(0.0, -0.035), (0.0058, -0.035), (0.0062, -0.031), (0.0062, 0.031), (0.0058, 0.035), (0.0, 0.035)],
              8, (door[0] - 0.0015, yf + 0.003, zc))
    parts.append(hg)
    lk = P("cab_locks", "chrome")
    dk = P("cab_keyholes", "dark")
    for cx, cz, r in ((dcx, dcz - 0.105, 0.0092), ((drawers[0][0] + drawers[0][1]) / 2, drawers[0][3] - 0.016, 0.0080)):
        lathe(lk, [(r, 0.0), (r, 0.0025), (r * 0.82, 0.0042), (0.0, 0.0042)], 10, (cx, yf, cz), out)
        g.box(dk, cx - 0.0011, cx + 0.0011, yf - 0.0046, yf - 0.0040, cz - 0.0045, cz + 0.0020)
    parts += [lk, dk]
    for i, d in enumerate(drawers):
        cx, cz = (d[0] + d[1]) / 2, d[3] - 0.092
        lb = P("cab_label%d" % i, "chrome", uv_name="cab_label", uv_origin=(cx, yf, cz))
        g.box(lb, cx - 0.036, cx + 0.036, yf - 0.0015, yf + 0.0005, cz - 0.019, cz + 0.019, r=0.001, seg=1)
        U(lb, "card")
        g.box(lb, cx - 0.031, cx + 0.031, yf - 0.0020, yf - 0.0013, cz - 0.014, cz + 0.014)
        parts.append(lb)
    return parts


# =============================================================================
# Lead shield
# =============================================================================
def band_ring(part, z0, z1, n, lod):
    """Steel band on the lead: rolled edges (chamfers) and a wall; it sits on the lead from inside."""
    if lod == 0:
        lathe(part, [(R_OUT - 0.0005, z0), (R_OUT + BAND, z0 + 0.0016), (R_OUT + BAND, z1 - 0.0016),
                     (R_OUT - 0.0005, z1)], n, (SX, SY, 0.0))
    else:
        lathe(part, [(R_OUT + BAND, z0), (R_OUT + BAND, z1)], n, (SX, SY, 0.0))


def band_clamp(part, zc, h, a):
    """Band clamp: two lugs at the band ends, a hex-head bolt and a nut across."""
    rad = Vector((math.cos(a), math.sin(a), 0.0))
    tan = Vector((-math.sin(a), math.cos(a), 0.0))
    c = Vector((SX, SY, zc)) + rad * (R_OUT + BAND)
    for s in (-1, 1):
        fr = g.Frame(c + tan * (s * 0.010), tan, Vector((0.0, 0.0, 1.0)), rad)
        g.box(part, -0.0035, 0.0035, -h / 2, h / 2, -0.002, 0.015, frame=fr)
    bc = c + rad * 0.009
    lathe(part, [(0.0, -0.0215), (0.0038, -0.0215), (0.0038, 0.0215), (0.0, 0.0215)], 6, bc, tan)
    lathe(part, [(0.0, -0.0205), (0.0066, -0.0205), (0.0066, -0.0135)], 6, bc, tan, phase=0.5)
    lathe(part, [(0.0066, 0.0135), (0.0066, 0.0200), (0.0, 0.0200)], 6, bc, tan, phase=0.5)


def build_shield(spec):
    lod, n = spec["lod"], spec["shield"]
    parts = []
    pl = P("base_plate", "plate")
    g.box(pl, SX - 0.29, SX + 0.29, SY - 0.29, SY + 0.29, ZB, Z0, **bev(lod, 0.004, 1))
    parts.append(pl)
    body = P("body", "lead")
    c = (SX, SY, 0.0)
    # the lid is open at rest: the top of the wall is visible - a chamfer outside; the chamber lining and
    # the floor are copper, chamfered at the edge
    lathe(body, [(R_OUT, Z0)] + ([(R_OUT, ZS - 0.004), (R_OUT - 0.004, ZS)] if lod == 0 else [(R_OUT, ZS)]) +
          [(R_CAV + 0.010, ZS)], n, c)
    U(body, "copper")
    lathe(body, ([(R_CAV + 0.010, ZS), (R_CAV, ZS - 0.008)] if lod == 0 else [(R_CAV + 0.010, ZS), (R_CAV, ZS)]) +
          [(R_CAV, ZF), (0.0, ZF)], n, c)
    parts.append(body)
    if lod == 2:
        return parts
    for nm, z0, z1, ac in (("band_lo", Z0, Z0 + 0.05, A_CLAMPS[0]), ("band_hi", ZS - 0.05, ZS, A_CLAMPS[1])):
        bd = P(nm, "band")
        band_ring(bd, z0, z1, spec["band"], lod)
        if lod == 0:
            band_clamp(bd, (z0 + z1) / 2, z1 - z0 - 0.010, ac)
        parts.append(bd)
    parts += build_sign(lod) + build_hinge_body(lod) + build_glands(lod)
    if lod == 0:
        parts += build_plate_bolts() + build_latch_body() + build_mask_hook()
    return parts


def build_sign(lod):
    """Radiation sign plate on the cylinder, on four rivets."""
    sg = P("sign", "sign")
    half = 0.044 / R_OUT
    a = -math.pi / 2                                           # front (-Y)
    arc_plate(sg, a - half, a + half, ZT_SIGN - 0.044, ZT_SIGN + 0.044, R_OUT - 0.002, R_OUT + 0.0018,
              8 if lod == 0 else 2)
    parts = [sg]
    if lod == 0:
        for i, (da, dz) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
            aa = a + da * (half - 0.0068 / R_OUT)
            rad = (math.cos(aa), math.sin(aa), 0.0)
            ctr = (SX + (R_OUT + 0.0018) * rad[0], SY + (R_OUT + 0.0018) * rad[1], ZT_SIGN + dz * 0.0372)
            rv = P("sign_rivet%d" % i, "steel", uv_name="sign_rivet", uv_origin=ctr)
            lathe(rv, [(0.0030, -0.0003), (0.0024, 0.0009), (0.0, 0.0014)], 6, ctr, rad)
            parts.append(rv)
    return parts


def build_hinge_body(lod):
    """Hinge on the upper band: a pad following the cylinder on four bolts, a boss up to the axis, a middle
    knuckle; the axle with heads."""
    hb = P("hinge_body", "band")
    a = math.pi / 2                                            # back (+Y)
    half = 0.058 / (R_OUT + BAND)
    rl = R_OUT + BAND
    arc_plate(hb, a - half, a + half, ZS - 0.048, ZS - 0.004, rl - 0.001, rl + 0.007, 6 if lod == 0 else 2)
    g.box(hb, SX - 0.044, SX + 0.044, SY + rl + 0.002, HY, ZS - 0.034, HZ, **bev(lod, 0.003, 1))
    lathe(hb, [(0.0, -0.044), (0.018, -0.044), (0.018, 0.044), (0.0, 0.044)], 16 if lod == 0 else 8,
          (SX, HY, HZ), (1.0, 0.0, 0.0))
    parts = [hb]
    pin = P("hinge_pin", "steel")
    prof = [(0.0, -0.130), (0.009, -0.127), (0.013, -0.122), (0.013, -0.115), (0.009, -0.115), (0.009, 0.115),
            (0.013, 0.115), (0.013, 0.122), (0.009, 0.127), (0.0, 0.130)] if lod == 0 else \
        [(0.0, -0.125), (0.010, -0.125), (0.010, 0.125), (0.0, 0.125)]
    lathe(pin, prof, 10 if lod == 0 else 6, (SX, HY, HZ), (1.0, 0.0, 0.0))
    parts.append(pin)
    if lod == 0:
        for i, (da, zz) in enumerate(((-1, ZS - 0.036), (1, ZS - 0.036), (-1, ZS - 0.016), (1, ZS - 0.016))):
            aa = a + da * half * 0.68
            rad = (math.cos(aa), math.sin(aa), 0.0)
            ctr = (SX + (rl + 0.007) * rad[0], SY + (rl + 0.007) * rad[1], zz)
            bt = P("hinge_bolt%d" % i, "steel", uv_name="hinge_bolt", uv_origin=ctr)
            hex_bolt(bt, ctr, rad, 0.0065, 0.0045)
            parts.append(bt)
    return parts


def build_glands(lod):
    """Detector cable glands on the right: a wrench-flat body and a cap nut, a cable out of it."""
    gl = P("glands", "steel")
    for gy in GLANDS:
        x0 = SX + math.sqrt(R_OUT ** 2 - (gy - SY) ** 2) - 0.004
        ctr = (x0, gy, ZG)
        lathe(gl, [(0.0165, 0.0), (0.0165, 0.013), (0.0, 0.013)], 6, ctr, (1.0, 0.0, 0.0), phase=0.5)
        lathe(gl, [(0.0125, 0.013), (0.0130, 0.024), (0.0105, 0.030), (0.0050, 0.0335)], 10 if lod == 0 else 6, ctr,
              (1.0, 0.0, 0.0))
    return [gl]


def gland_tip(gy):
    return SX + math.sqrt(R_OUT ** 2 - (gy - SY) ** 2) - 0.004 + 0.030


def build_plate_bolts():
    parts = []
    for i, (bx, by) in enumerate(((SX - 0.25, SY - 0.25), (SX + 0.25, SY - 0.25), (SX - 0.25, SY + 0.25),
                                  (SX + 0.25, SY + 0.25))):
        bt = P("plate_bolt%d" % i, "steel", uv_name="plate_bolt", uv_origin=(bx, by, Z0))
        hex_bolt(bt, (bx, by, Z0), (0.0, 0.0, 1.0), 0.0115, 0.0095, washer=0.0165)
        parts.append(bt)
    return parts


def build_latch_body():
    """Swing bolt at the front: cheeks with an axle on the upper band; a bolt with a wing nut hangs down
    (the lid is open at rest; in "work" it closes and rests with its lug above the hanging bolt)."""
    lt = P("latch_body", "band")
    y_out = SY - R_OUT - BAND
    for s in (-1, 1):
        g.box(lt, SX + s * 0.0075 - 0.0025, SX + s * 0.0075 + 0.0025, y_out - 0.022, y_out + 0.004, ZS - 0.046,
              ZS - 0.021, r=0.0012, seg=1)
    lathe(lt, [(0.0, -0.0105), (0.0028, -0.0105), (0.0028, 0.0105), (0.0, 0.0105)], 8, (SX, YB, ZS - 0.034),
          (1.0, 0.0, 0.0))
    bl = P("latch_bolt", "steel")
    piv = Vector((SX, YB, ZS - 0.034))
    lathe(bl, [(0.0, -0.0048), (0.0068, -0.0048), (0.0068, 0.0048), (0.0, 0.0048)], 10, piv, (1.0, 0.0, 0.0))
    d = Vector((0.0, -0.28, -1.0)).normalized()
    end = piv + d * 0.078
    g.pipe(bl, [tuple(piv), tuple(end)], 0.0045, 8)
    wing_nut(bl, piv + d * 0.060, d)
    return [lt, bl]


def wing_nut(part, base, d):
    """Wing nut on a bolt: hub and two wings (along x)."""
    d = Vector(d).normalized()
    lathe(part, [(0.0075, 0.0), (0.0075, 0.0085), (0.0056, 0.0115), (0.0, 0.0115)], 10, base, d)
    u = Vector((1.0, 0.0, 0.0))
    fr = g.Frame(base, u, d, u.cross(d))
    for s in (-1, 1):
        poly = [(s * a, b) for a, b in ((0.0050, 0.0015), (0.0165, 0.0050), (0.0180, 0.0125), (0.0150, 0.0165),
                                        (0.0050, 0.0110))]
        g.prism(part, poly if s > 0 else poly[::-1], (0, 1), -0.0013, 0.0013, frame=fr)


def build_mask_hook():
    """Hook at the left on the upper band: the vanilla GP-5 hangs on it (DECOR)."""
    hk = P("mask_hook", "steel")
    x = SX - R_OUT - BAND
    g.box(hk, x - 0.004, x + 0.002, SY - 0.010, SY + 0.010, ZS - 0.046, ZS - 0.014, r=0.0012, seg=1)
    g.pipe(hk, spline([(x - 0.002, SY, ZS - 0.034), (x - 0.020, SY, ZS - 0.036), (x - 0.030, SY, ZS - 0.028),
                       (x - 0.032, SY, ZS - 0.016)], 2), 0.0032, 6)
    return [hk]


def swing(parts):
    """Lid at rest: everything on the lid is tilted back about the hinge axis (the bone ozl_lid closes it
    in "work")."""
    m = Matrix.Rotation(math.radians(-OPEN_DEG), 3, "X")
    for p in parts:
        bmesh.ops.rotate(p.bm, verts=p.bm.verts[:], cent=Vector((0.0, HY, HZ)), matrix=m)
        p.bm.normal_update()
    return parts


def build_lid(spec):
    """Lid (built closed, swing tilts it open): cast lead with chamfers, band with a clamp, hinge knuckles,
    handle on flanges, eyebolt, lug for the swing bolt; a copper plug is visible from below."""
    lod, n = spec["lod"], spec["shield"]
    parts = []
    ld = P("lid", "lead", group=GL)
    c = (SX, SY, 0.0)
    U(ld, "copper")
    lathe(ld, [(0.0, ZS - 0.030), (R_CAV - 0.004, ZS - 0.030), (R_CAV - 0.004, ZS)], n, c)
    U(ld, "lead")
    if lod < 2:
        prof = [(R_CAV - 0.004, ZS), (R_OUT, ZS), (R_OUT, ZL - 0.008), (R_OUT - 0.008, ZL), (0.0, ZL)]
    else:
        prof = [(R_CAV - 0.004, ZS), (R_OUT, ZS), (R_OUT, ZL), (0.0, ZL)]
    lathe(ld, prof, n, c)
    parts.append(ld)
    if lod == 2:
        return parts
    lb = P("lid_band", "band", group=GL)
    band_ring(lb, ZS + 0.006, ZS + 0.056, spec["band"], lod)
    if lod == 0:
        band_clamp(lb, ZS + 0.031, 0.040, A_CLAMPS[2])
    parts.append(lb)
    kn = P("lid_knuckles", "band", group=GL)
    for s in (-1, 1):
        x0, x1 = sorted((SX + s * 0.050, SX + s * 0.105))
        g.box(kn, x0, x1, SY + R_OUT + BAND - 0.006, HY, HZ - 0.016, ZS + 0.054, **bev(lod, 0.003, 1))
        lathe(kn, [(0.0, x0 - SX), (0.018, x0 - SX), (0.018, x1 - SX), (0.0, x1 - SX)], 12 if lod == 0 else 8,
              (SX, HY, HZ), (1.0, 0.0, 0.0))
    parts.append(kn)
    # handle: posts on flanges, bakelite grip
    hp = P("lid_handle_posts", "steel", group=GL)
    yb = SY - R_OUT - 0.055
    for s in (-1, 1):
        x = SX + s * 0.075
        ys = SY - math.sqrt((R_OUT + BAND) ** 2 - 0.075 ** 2)
        if lod == 0:
            lathe(hp, [(0.0150, -0.004), (0.0150, 0.002), (0.0105, 0.0055), (0.0, 0.0055)], 12, (x, ys, ZH),
                  (0.0, -1.0, 0.0))
        g.pipe(hp, [(x, ys + 0.002, ZH), (x, yb, ZH)], 0.0075, 6 if lod == 0 else 4)
    parts.append(hp)
    gr = P("lid_grip", "bakelite", group=GL)
    if lod == 0:
        lathe(gr, [(0.0, -0.096), (0.0090, -0.0955), (0.0135, -0.092), (0.0145, -0.080), (0.0152, 0.0),
                   (0.0145, 0.080), (0.0135, 0.092), (0.0090, 0.0955), (0.0, 0.096)], 10, (SX, yb, ZH), (1.0, 0.0, 0.0))
    else:
        g.pipe(gr, [(SX - 0.095, yb, ZH), (SX + 0.095, yb, ZH)], 0.014, 6)
    parts.append(gr)
    if lod == 0:
        # eyebolt: collar with a chamfer, neck, ring
        ey = P("lid_eye", "steel", group=GL)
        lathe(ey, [(0.026, ZL - 0.001), (0.026, ZL + 0.003), (0.0125, ZL + 0.011), (0.0110, ZL + 0.017),
                   (0.0, ZL + 0.017)], 12, (SX, SY, 0.0))
        torus(ey, (SX, SY, ZL + 0.017 + 0.026 + 0.0025), "y", 0.026, 0.0068, 14, 6)
        parts.append(ey)
        # lug for the swing bolt on the lid band
        ll = P("latch_lid", "band", group=GL)
        y_out = SY - R_OUT - BAND
        for s in (-1, 1):
            g.box(ll, SX + s * 0.0075 - 0.0025, SX + s * 0.0075 + 0.0025, y_out - 0.022, y_out + 0.004, ZS + 0.008,
                  ZS + 0.021, r=0.0012, seg=1)
        parts.append(ll)
    return parts


ZD = ZF + 0.240                                              # top of the detector cap
ZM0, ZM_TOP = ZF + 0.180, ZF + 0.285                         # Marinelli beaker: bottom, top of the lid


def build_inside(spec):
    """Chamber (lid open at rest): an aluminium detector cap rises 24 cm from the floor, with a Marinelli
    beaker with a sample on it (the well fits over the detector): white, with a lid and a red marking
    tape - visible from above in the copper chamber."""
    if spec["lod"] == 2:
        return []
    sd = 24 if spec["lod"] == 0 else 8
    c = (SX, SY, 0.0)
    dt = P("detector", "alu")
    lathe(dt, [(0.040, ZF - 0.001), (0.040, ZD - 0.004), (0.037, ZD), (0.0, ZD)], sd, c)
    jar = P("marinelli", "cup")
    lathe(jar, [(0.0, ZD + 0.004), (0.0425, ZD + 0.004), (0.0425, ZM0), (0.065, ZM0), (0.065, ZM_TOP - 0.008),
                (0.0625, ZM_TOP - 0.008)], sd, c)
    lathe(jar, [(0.0668, ZM_TOP - 0.013), (0.0668, ZM_TOP - 0.002), (0.0650, ZM_TOP), (0.0, ZM_TOP)], sd, c)
    parts = [dt, jar]
    if spec["lod"] == 0:
        tp = P("marinelli_tape", "cap_red")
        lathe(tp, [(0.0656, ZM_TOP - 0.052), (0.0656, ZM_TOP - 0.034)], sd, c)
        parts.append(tp)
    return parts


# =============================================================================
# Instrument rack
# =============================================================================
def build_rack(spec):
    lod = spec["lod"]
    parts = []
    fr = P("rack", "inst")
    g.box(fr, RX0, RX1, RY0, RY1, ZB + 0.012 if lod < 2 else ZB, ZR0, **bev(lod, 0.002, 1))
    if lod == 2:
        g.box(fr, RX0, RX1, RY0 + 0.004, RY1, ZR0, ZRT)
        parts.append(fr)
        for nm, z0, z1 in (("panel_an", ZM1, ZM2), ("panel_rad", ZM2, ZM3)):
            pn = P(nm, "panel")
            g.box(pn, IX0, IX1, YP - 0.002, YP + 0.004, z0 + 0.001, z1 - 0.001)
            parts.append(pn)
        return parts
    for x0, x1 in ((RX0, RX0 + CHK), (RX1 - CHK, RX1)):
        g.box(fr, x0, x1, RY0, RY1, ZR0 - 0.002, ZRT - 0.012, **bev(lod, 0.004, 1))
    g.box(fr, RX0, RX1, RY0, RY1, ZRT - 0.014, ZRT, **bev(lod, 0.004, 2))
    g.box(fr, IX0, IX1, RY1 - 0.010, RY1, ZR0, ZRT - 0.014)
    parts.append(fr)
    # black behind the gaps between the panels of the upper units; the recorder window is deeper and the black does
    # not reach it
    bk = P("rack_backing", "black")
    g.box(bk, IX0, IX1, YP + 0.008, YP + 0.014, ZM1 - 0.002, ZRT - 0.014)
    parts.append(bk)
    for nm, z0, z1 in (("panel_an", ZM1, ZM2), ("panel_rad", ZM2, ZM3)):
        pn = P(nm, "panel")
        g.box(pn, IX0 + 0.001, IX1 - 0.001, YP, YP + 0.008, z0 + 0.001, z1 - 0.001, **bev(lod, 0.0012, 1))
        parts.append(pn)
        zc = (z0 + z1) / 2
        if lod == 0:
            for sx_, xh in ((0, IX0 + 0.011), (1, IX1 - 0.011)):
                h = P("%s_h%d" % (nm, sx_), "steel", uv_name="rack_handle", uv_origin=(xh, YP, zc))
                u_handle(h, (xh, YP, zc - 0.045), (xh, YP, zc + 0.045), (0.0, -1.0, 0.0), 0.028, 0.008, 0.0045, 6, lod)
                parts.append(h)
            for xs in (IX0 + 0.011, IX1 - 0.011):
                for zs in (z0 + 0.010, z1 - 0.010):
                    parts += dome_screw("%s_s%d" % (nm, len(parts)), (xs, YP, zs))
    fl = P("rec_fill", "panel")
    for x0, x1 in ((IX0 + 0.001, KX0 - 0.001), (KX1 + 0.001, IX1 - 0.001)):
        g.box(fl, x0, x1, YP, YP + 0.008, ZR0 + 0.001, ZM1 - 0.001)
    parts.append(fl)
    gb = P("rack_vent_back", "grille_v")
    g.box(gb, IX0 + 0.05, IX1 - 0.05, RY1 - 0.0005, RY1 + 0.0015, ZM1 + 0.02, ZRT - 0.04)
    parts.append(gb)
    if lod > 0:
        return parts
    gt = P("rack_vent_top", "grille_h")
    g.box(gt, RX0 + 0.06, RX1 - 0.06, RY0 + 0.08, RY1 - 0.06, ZRT - 0.001, ZRT + 0.0015)
    parts.append(gt)
    # louvres on the sides (rear top) and carry handles
    lv = P("rack_louvers", "dark")
    for xo, sgn in ((RX0, -1), (RX1, 1)):
        for k in range(6):
            zk = ZM1 + 0.030 + k * 0.017
            g.box(lv, *sorted((xo + sgn * 0.0006, xo - sgn * 0.0010)), 0.020, 0.125, zk, zk + 0.0055)
    parts.append(lv)
    for i, (xo, sgn) in enumerate(((RX0, -1), (RX1, 1))):
        sh = P("rack_carry%d" % i, "steel", uv_name="rack_carry", uv_origin=(xo, 0.0, ZRT - 0.06))
        u_handle(sh, (xo, -0.07, ZRT - 0.06), (xo, 0.07, ZRT - 0.06), (sgn, 0.0, 0.0), 0.026, 0.009, 0.0048, 6, lod)
        for yy in (-0.07, 0.07):
            g.box(sh, *sorted((xo, xo + sgn * 0.003)), yy - 0.010, yy + 0.010, ZRT - 0.072, ZRT - 0.048)
        parts.append(sh)
    for i, (fx, fy) in enumerate(((RX0 + 0.03, RY0 + 0.03), (RX1 - 0.03, RY0 + 0.03), (RX0 + 0.03, RY1 - 0.03),
                                  (RX1 - 0.03, RY1 - 0.03))):
        ft = P("rack_foot%d" % i, "rubber", uv_name="rack_foot", uv_origin=(fx, fy, ZB))
        lathe(ft, [(0.0, ZB), (0.0145, ZB), (0.016, ZB + 0.002), (0.016, ZB + 0.010), (0.012, ZB + 0.0125)], 10,
              (fx, fy, 0.0))
        parts.append(ft)
    # back wall: fuses, the power cord plug in its connector, cable connector nuts
    bp = P("rack_back_parts", "black")
    for fx in (0.36, 0.40):
        lathe(bp, [(0.0075, 0.0), (0.0075, 0.010), (0.0060, 0.016), (0.0, 0.017)], 6, (fx, RY1, ZR0 + 0.045),
              (0.0, 1.0, 0.0))
    g.box(bp, 0.475, 0.525, RY1, RY1 + 0.006, ZR0 + 0.022, ZR0 + 0.058)     # power connector
    g.box(bp, 0.480, 0.520, RY1 + 0.006, RY1 + 0.036, ZR0 + 0.026, ZR0 + 0.054)  # plug
    U(bp, "steel")
    for xx, zz in ((0.250, ZM1 + 0.065), (0.430, ZM2 + 0.080)):
        lathe(bp, [(0.0085, 0.0), (0.0085, 0.0025), (0.0, 0.0025)], 6, (xx, RY1, zz), (0.0, 1.0, 0.0), phase=0.5)
    parts.append(bp)
    return parts


# --- panel details: each part is its own, identical ones share an atlas place (uv_name) ---------
def toggle(name, x, z, yf, lod, big=False, up=True):
    """Toggle: hex nut, bushing, lever with a thickening at the end."""
    if lod > 0:
        return []
    c = (x, yf, z)
    p = P(name, "steel", uv_name="toggle_big" if big else "toggle", uv_origin=c)
    rn = 0.0072 if big else 0.0062
    out = (0.0, -1.0, 0.0)
    lathe(p, [(rn, 0.0), (rn, 0.0030), (0.0, 0.0030)], 6, c, out, phase=0.5)
    ln = 0.025 if big else 0.020
    dl = Vector((0.0, -0.94, 0.34 if up else -0.34))
    lathe(p, [(0.0024, 0.0), (0.0014, ln * 0.84), (0.0026, ln * 0.92), (0.0, ln)], 6, (x, yf - 0.0026, z), dl)
    return [p]


def knob(name, x, z, yf, r, lod, angle=0.0, skirt=True):
    """Bakelite knob: skirt, knurled head, a white mark on the end; angle - where the mark points, degrees
    from the top, clockwise."""
    c = (x, yf, z)
    out = (0.0, -1.0, 0.0)
    kb = P(name, "bakelite", uv_name="knob%d%s" % (round(r * 1000), "s" if skirt else ""), uv_origin=c)
    if lod > 0:
        g.cyl(kb, (x, yf - 0.012, z), "y", r, 0.024, 6)
        return [kb]
    h0 = 0.0
    if skirt:
        lathe(kb, [(r * 1.32, 0.0), (r * 1.32, 0.0028), (r * 1.08, 0.0055), (0.0, 0.0055)], 12, c, out)
        h0 = 0.0055
    fluted(kb, c, out, r, 0.0011, 10, h0, 0.0205)
    a = math.radians(angle)
    fr = g.Frame((x, yf - 0.0205, z), (math.cos(a), 0.0, -math.sin(a)), (math.sin(a), 0.0, math.cos(a)), out)
    pt = P(name + "_ptr", "key", uv_name="knob_ptr", uv_origin=c)
    g.box(pt, -0.0013, 0.0013, r * 0.22, r * 0.86, 0.0, 0.0006, frame=fr)
    return [kb, pt]


def lamp(name, x, z, yf, reg, lod, group="body"):
    """Signal lamp: steel rim and a dome lens (the lens is the "work" look selection)."""
    c = (x, yf, z)
    out = (0.0, -1.0, 0.0)
    lens = P(name, reg, group=group, uv_name="lamp_" + reg, uv_origin=c)
    if lod > 0:
        g.cyl(lens, (x, yf - 0.005, z), "y", 0.0080, 0.010, 6)
        return [lens]
    rim = P(name + "_rim", "steel", uv_name="lamp_rim", uv_origin=c)
    lathe(rim, [(0.0108, 0.0), (0.0108, 0.0038), (0.0084, 0.0058)], 10, c, out)
    lathe(lens, [(0.0080, 0.0040), (0.0080, 0.0068), (0.0058, 0.0104), (0.0, 0.0120)], 10, c, out)
    return [rim, lens]


def bnc(name, x, z, yf, lod):
    """BNC socket: nut, body with two bayonet pins, a white insulator in the depth."""
    if lod > 0:
        return []
    c = (x, yf, z)
    out = (0.0, -1.0, 0.0)
    p = P(name, "steel", uv_name="bnc", uv_origin=c)
    lathe(p, [(0.0085, 0.0), (0.0085, 0.0025), (0.0, 0.0025)], 6, c, out, phase=0.5)
    lathe(p, [(0.0062, 0.0025), (0.0062, 0.0150), (0.0047, 0.0150), (0.0047, 0.0130)], 8, c, out)
    for s in (-1, 1):
        g.box(p, *sorted((x + s * 0.0058, x + s * 0.0078)), yf - 0.0118, yf - 0.0098, z - 0.0009, z + 0.0009)
    U(p, "cup")
    lathe(p, [(0.0047, 0.0130), (0.0, 0.0130)], 8, c, out)
    return [p]


def bnc_plug(part, base, d, lod):
    """BNC plug on a cable: knurled union nut and a tail; the cable runs from base + d * 0.030."""
    if lod > 0:
        lathe(part, [(0.0075, 0.0), (0.0075, 0.012), (0.0045, 0.030)], 5, base, d)
        return
    fluted(part, base, d, 0.0078, 0.0007, 8, 0.0, 0.0120, cap=False)
    lathe(part, [(0.0078, 0.0120), (0.0056, 0.0160), (0.0047, 0.0300), (0.0038, 0.0320)], 8, base, d)


def key(name, x, z, yf, reg, lod):
    k = P(name, reg, uv_name="key_" + reg, uv_origin=(x, yf, z))
    g.box(k, x - 0.012, x + 0.012, yf - 0.009, yf + 0.001, z - 0.0085, z + 0.0085, **bev(lod, 0.0016, 1))
    return [k]


def meter(name, rect, piv, needle_group, lod):
    """Panel meter (like the M4200): body on the panel, window frame with glass, the scale (decal) in the
    depth, the needle is a bone (0 is the scale zero) with an axle cap."""
    x0, x1, z0, z1 = rect
    parts = []
    cs = P(name + "_case", "black")
    g.box(cs, x0 - 0.008, x1 + 0.008, YP - 0.004, YP + 0.002, z0 - 0.008, z1 + 0.008, **bev(lod, 0.002, 1))
    if lod == 0:
        for bx0, bx1, bz0, bz1 in ((x0 - 0.008, x1 + 0.008, z1, z1 + 0.008), (x0 - 0.008, x1 + 0.008, z0 - 0.008, z0),
                                   (x0 - 0.008, x0, z0, z1), (x1, x1 + 0.008, z0, z1)):
            g.box(cs, bx0, bx1, YP - 0.0105, YP - 0.0035, bz0, bz1)
    parts.append(cs)
    fc = P(name + "_face", "dial")
    g.box(fc, x0, x1, Y_DIAL, YP - 0.0035, z0, z1)
    parts.append(fc)
    if lod == 0:
        gl = P(name + "_glass", "rec_case", section="glass")
        yg = YP - 0.0090
        quad_facing(gl, [(x0, yg, z0), (x1, yg, z0), (x1, yg, z1), (x0, yg, z1)], (0.0, -1.0, 0.0))
        parts.append(gl)
    px, pz, rr = piv
    th = math.radians(130.0)                                   # scale zero: 40 degrees left of vertical
    fr = g.Frame((px, Y_NEEDLE + 0.0002, pz), (math.cos(th), 0.0, math.sin(th)), (-math.sin(th), 0.0, math.cos(th)),
                 (0.0, -1.0, 0.0))
    nd = P(name + "_needle", "needle", group=needle_group)
    g.prism(nd, [(-0.20 * rr, -0.0012), (1.02 * rr, -0.0002), (1.02 * rr, 0.0002), (-0.20 * rr, 0.0012)], (0, 1), 0.0,
            0.0006, frame=fr)
    if lod == 0:
        g.cyl(nd, (px, Y_NEEDLE, pz), "y", 0.0042, 0.0022, 10)
    parts.append(nd)
    return parts


# =============================================================================
# Recorder, analyzer, radiometer
# =============================================================================
def build_pen(lod):
    """Pen carriage on a rod (bone ozl_pen; stands at the field zero): body, a lever toward the tape, an
    ink cartridge, the pen tip."""
    px = FX0
    pn = P("rec_pen", "pen", group=SEL_PEN)
    g.box(pn, px - 0.009, px + 0.009, Y_ROD - 0.006, Y_ROD + 0.006, Z_ROD - 0.006, Z_ROD + 0.008, **bev(lod, 0.0015, 1))
    if lod == 0:
        U(pn, "steel")
        g.box(pn, px - 0.0015, px + 0.0015, Y_ROD + 0.002, Y_CHART - 0.0014, Z_PEN - 0.001, Z_ROD - 0.006)
        U(pn, "ink")
        g.cyl(pn, (px + 0.0058, Y_ROD - 0.0035, Z_ROD + 0.002), "z", 0.0026, 0.016, 8)
        lathe(pn, [(0.0010, 0.0), (0.0, 0.0028)], 6, (px, Y_CHART - 0.0042, Z_PEN), (0.0, 1.0, 0.0))
    return [pn]


def build_recorder(spec):
    """KSP4 recorder: frame with a window and a glazed door, tape (own texture, "work" frames), scale, pen
    carriage on a rod, pressure roller, a slot with a tear-off bar, controls below."""
    lod = spec["lod"]
    parts = []
    bz = P("rec_bezel", "rec_case")
    if lod == 2:
        g.box(bz, KX0, KX1, RY0 - 0.006, RY0 + 0.004, ZR0, ZM1)
        ch = P("rec_chart", "chart")
        g.box(ch, TX0, TX1, RY0 - 0.008, RY0 - 0.006, WZ0, CH_Z1)
        return [bz, ch]
    y0, y1 = RY0 - 0.010, RY0 + 0.040
    b = bev(lod, 0.002, 1)
    g.box(bz, KX0, KX1, y0, y1, WZ1, ZM1, **b)
    g.box(bz, KX0, KX1, y0, y1, ZR0, WZ0, **b)
    g.box(bz, KX0, WX0, y0, y1, WZ0, WZ1)
    g.box(bz, WX1, KX1, y0, y1, WZ0, WZ1)
    parts.append(bz)
    dk = P("rec_inside", "dark")
    g.box(dk, WX0, WX1, RY0 + 0.038, RY0 + 0.042, WZ0, WZ1)
    parts.append(dk)
    ch = P("rec_chart", "black", group=SEL_CHART, section="chart")
    quad_facing(ch, [(TX0, Y_CHART, WZ0), (TX1, Y_CHART, WZ0), (TX1, Y_CHART, CH_Z1), (TX0, Y_CHART, CH_Z1)],
                (0.0, -1.0, 0.0))
    ch.glass_frame = (g.WORLD, TX0, TX1, WZ0, CH_Z1)
    parts.append(ch)
    sc = P("rec_scale", "dial")
    g.box(sc, SCALE[0], SCALE[1], RY0 + 0.022, RY0 + 0.026, SCALE[2], SCALE[3])
    parts.append(sc)
    parts += build_pen(lod)
    gl = P("rec_glass", "rec_case", section="glass")
    yg = RY0 - 0.0125 if lod == 0 else RY0 - 0.004
    quad_facing(gl, [(WX0, yg, WZ0), (WX1, yg, WZ0), (WX1, yg, WZ1), (WX0, yg, WZ1)], (0.0, -1.0, 0.0))
    parts.append(gl)
    sl = P("rec_slot", "black")
    g.box(sl, TX0 - 0.008, TX1 + 0.008, RY0 - 0.0105, RY0 - 0.009, ZR0 + 0.094, ZR0 + 0.104)
    parts.append(sl)
    if lod > 0:
        return parts
    # door: frame around the glass, two hinges at the left, a latch handle at the right
    dr = P("rec_door", "rec_case")
    for bx0, bx1, bz0, bz1 in ((WX0 - 0.008, WX1 + 0.008, WZ1 - 0.003, WZ1 + 0.008),
                               (WX0 - 0.008, WX1 + 0.008, WZ0 - 0.008, WZ0 + 0.003),
                               (WX0 - 0.008, WX0 + 0.003, WZ0 + 0.003, WZ1 - 0.003),
                               (WX1 - 0.003, WX1 + 0.008, WZ0 + 0.003, WZ1 - 0.003)):
        g.box(dr, bx0, bx1, RY0 - 0.0145, RY0 - 0.0100, bz0, bz1)
    U(dr, "steel")
    for zh in (WZ0 + 0.035, WZ1 - 0.035):
        lathe(dr, [(0.0, -0.013), (0.0040, -0.013), (0.0040, 0.013), (0.0, 0.013)], 6, (WX0 - 0.0075, RY0 - 0.0115, zh))
    parts.append(dr)
    dh = P("rec_latch", "bakelite")
    lathe(dh, [(0.0068, 0.0), (0.0068, 0.0035), (0.0050, 0.0095), (0.0, 0.0108)], 12,
          (WX1 + 0.0025, RY0 - 0.0145, (WZ0 + WZ1) / 2), (0.0, -1.0, 0.0))
    parts.append(dh)
    rd = P("rec_rod", "steel")
    g.pipe(rd, [(WX0, Y_ROD, Z_ROD), (WX1, Y_ROD, Z_ROD)], 0.0030, 8)
    g.pipe(rd, [(TX0 - 0.01, Y_CHART - 0.006, WZ0 + 0.012), (TX1 + 0.01, Y_CHART - 0.006, WZ0 + 0.012)], 0.006, 8)
    # tear-off bar above the slot
    g.box(rd, TX0 - 0.012, TX1 + 0.012, RY0 - 0.0135, RY0 - 0.0100, ZR0 + 0.1045, ZR0 + 0.1100)
    parts.append(rd)
    # controls below, at the sides of the hanging tape: left a toggle and the "power" lamp, right the speed knob
    zc = ZR0 + 0.056
    yf = RY0 - 0.010
    parts += toggle("rec_tg0", 0.137, zc - 0.012, yf, lod) + lamp("rec_lamp", 0.160, zc + 0.020, yf, "lamp_g", lod,
                                                                     group=SEL_LAMP)
    parts += knob("rec_speed", 0.495, zc, yf, 0.016, lod, angle=-40.0)
    for xs in (KX0 + 0.009, KX1 - 0.009):
        for zs in (ZR0 + 0.010, ZM1 - 0.010):
            parts += dome_screw("rec_s%d" % len(parts), (xs, yf, zs))
    return parts


def build_analyzer(spec):
    """Pulse analyzer: gas-discharge digits (own texture, "work" frames) behind glass, a row of buttons, a
    selector, a knob, toggles, connectors."""
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    x0, x1, z0, z1 = NIX
    nc = P("nixie_case", "black")
    g.box(nc, x0 - 0.008, x1 + 0.008, YP - 0.004, YP + 0.002, z0 - 0.008, z1 + 0.008, **bev(lod, 0.0015, 1))
    if lod == 0:
        for bx0, bx1, bz0, bz1 in ((x0 - 0.008, x1 + 0.008, z1, z1 + 0.008), (x0 - 0.008, x1 + 0.008, z0 - 0.008, z0),
                                   (x0 - 0.008, x0, z0, z1), (x1, x1 + 0.008, z0, z1)):
            g.box(nc, bx0, bx1, YP - 0.0095, YP - 0.0035, bz0, bz1)
    parts.append(nc)
    nf = P("nixie_face", "black", group=SEL_NIXIE, section="nixie")
    yq = YP - 0.0042
    quad_facing(nf, [(x0, yq, z0), (x1, yq, z0), (x1, yq, z1), (x0, yq, z1)], (0.0, -1.0, 0.0))
    nf.glass_frame = (g.WORLD, x0, x1, z0, z1)
    parts.append(nf)
    if lod == 0:
        gl = P("nixie_glass", "rec_case", section="glass")
        yg = YP - 0.0075
        quad_facing(gl, [(x0, yg, z0), (x1, yg, z0), (x1, yg, z1), (x0, yg, z1)], (0.0, -1.0, 0.0))
        parts.append(gl)
    zk = ZM1 + 0.021
    if lod == 0:
        for i in range(6):
            parts += key("an_key%d" % i, 0.135 + 0.036 * i, zk, YP, "key" if i % 3 else "black", lod)
    else:
        ks = P("an_keys", "black")
        g.box(ks, 0.123, 0.327, YP - 0.008, YP + 0.001, zk - 0.0085, zk + 0.0085)
        parts.append(ks)
    parts += knob("an_selector", SEL[0], SEL[1], YP, 0.019, lod, angle=-25.0)
    for i, (kx_, kz) in enumerate(KNOBS_AN):
        parts += knob("an_knob%d" % i, kx_, kz, YP, 0.012, lod, angle=60.0)
    parts += toggle("an_tg0", 0.448, ZM1 + 0.028, YP, lod) + toggle("an_tg1", 0.482, ZM1 + 0.028, YP, lod, up=False)
    parts += bnc("an_bnc0", 0.515, ZM1 + 0.103, YP, lod) + bnc("an_bnc1", 0.515, ZM1 + 0.061, YP, lod)
    return parts


def build_radiometer(spec):
    """Radiometer-intensity meter: a logarithmic count-rate meter and a kilovoltmeter (needles are bones),
    knobs, toggles, lamps "count" (blinks) and "high voltage", an input connector."""
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = meter("m_rate", M_RATE, RATE_PIV, SEL_RATE, lod) + meter("m_hv", M_HV, HV_PIV, SEL_HV, lod)
    for i, (kx_, kz) in enumerate(KNOBS_RAD):
        parts += knob("rad_knob%d" % i, kx_, kz, YP, 0.015, lod, angle=(-70.0, 35.0)[i])
    for i, tx in enumerate((0.398, 0.433, 0.468)):
        parts += toggle("rad_tg%d" % i, tx, ZM2 + 0.031, YP, lod, up=i != 1)
    parts += toggle("rad_power", 0.514, ZM2 + 0.031, YP, lod, big=True)
    parts += lamp("rad_lamp_g", 0.514, ZM2 + 0.109, YP, "lamp_g", lod, group=SEL_BLINK)
    parts += lamp("rad_lamp_r", 0.514, ZM2 + 0.079, YP, "lamp_r", lod, group=SEL_LAMP)
    parts += bnc("rad_bnc", 0.322, ZM2 + 0.023, YP, lod)
    return parts


def build_tape(spec):
    """Tape from the recorder slot: it hangs, lies on the worktop and bends over its edge."""
    lod = spec["lod"]
    pts = [(TAPE_X, RY0 - 0.004, ZR0 + 0.099), (TAPE_X, RY0 - 0.022, ZR0 + 0.094), (TAPE_X, RY0 - 0.045, ZR0 + 0.072),
           (TAPE_X, RY0 - 0.062, ZR0 + 0.035), (TAPE_X, RY0 - 0.075, ZB + 0.006), (TAPE_X, RY0 - 0.105, ZB + 0.0012),
           (TAPE_X, CY0 + 0.010, ZB + 0.0012), (TAPE_X, CY0 - 0.010, ZB - 0.006), (TAPE_X, CY0 - 0.016, ZB - 0.040)]
    if lod == 0:
        pts = spline(pts, 2)
    elif lod == 1:
        pts = [pts[k] for k in (0, 2, 4, 5, 6, 8)]
    else:
        pts = [pts[k] for k in (2, 5, 6, 8)]
    tp = P("tape", "chart")
    g.sweep(tp, pts, (1, 0, 0), 0.0005, (TX1 - TX0) / 2)
    return [tp]


def build_cables(spec):
    """Detector cables from the glands to the back wall of the rack (signal to the analyzer, high voltage
    to the radiometer) with BNC plugs, the power cord behind the cabinet with a plug on the floor, a
    patch cable at the front."""
    lod = spec["lod"]
    if lod == 2:
        return []
    sd = spec["cable"]
    gs, gh = gland_tip(GLANDS[0]), gland_tip(GLANDS[1])
    sig = [(gs - 0.004, GLANDS[0], ZG), (gs + 0.016, GLANDS[0] + 0.004, ZG - 0.008), (0.036, 0.004, ZG - 0.050),
           (0.046, 0.022, ZB + 0.026), (0.060, 0.060, ZB + 0.0065), (0.060, 0.170, ZB + 0.0065),
           (0.062, RY1 + 0.020, ZB + 0.012), (0.075, RY1 + 0.060, ZB + 0.0065), (0.170, RY1 + 0.075, ZB + 0.010),
           (0.235, RY1 + 0.080, ZB + 0.090), (0.248, RY1 + 0.080, ZM1 + 0.010), (0.250, RY1 + 0.065, ZM1 + 0.058),
           (0.250, RY1 + 0.031, ZM1 + 0.065)]
    hv = [(gh - 0.004, GLANDS[1], ZG), (gh + 0.018, GLANDS[1] + 0.004, ZG - 0.010), (0.030, -0.070, ZG - 0.065),
          (0.036, -0.050, ZB + 0.024), (0.040, -0.020, ZB + 0.0055), (0.042, RY1 + 0.004, ZB + 0.0055),
          (0.065, RY1 + 0.030, ZB + 0.0055), (0.380, RY1 + 0.036, ZB + 0.0055), (0.418, RY1 + 0.060, ZB + 0.060),
          (0.428, RY1 + 0.070, ZM2 + 0.020), (0.430, RY1 + 0.060, ZM2 + 0.072), (0.430, RY1 + 0.031, ZM2 + 0.080)]
    pwr = [(0.500, RY1 + 0.034, ZR0 + 0.040), (0.502, RY1 + 0.075, ZR0 + 0.028), (0.510, CY1 - 0.012, ZB + 0.0048),
           (0.520, CY1 + 0.020, ZB - 0.010), (0.520, CY1 + 0.034, 0.45), (0.520, CY1 + 0.050, 0.03),
           (0.470, CY1 + 0.130, 0.006), (0.420, CY1 + 0.200, 0.006)]
    if lod == 0:
        sig, hv, pwr = spline(sig, 2), spline(hv, 2), pwr
    else:
        sig = [sig[k] for k in (0, 2, 4, 6, 8, 10, 12)]
        hv = [hv[k] for k in (0, 2, 4, 6, 8, 9, 11)]
        pwr = [pwr[k] for k in (0, 2, 4, 6, 7)]
    parts = []
    for nm, reg, pts, r in (("cable_sig", "rubber", sig, 0.0045), ("cable_hv", "cable_grey", hv, 0.0042),
                            ("cable_pwr", "rubber", pwr, 0.0050)):
        c = P(nm, reg)
        g.pipe(c, pts, r, sd)
        parts.append(c)
    # BNC plugs in the back wall of the rack
    for i, (xx, zz) in enumerate(((0.250, ZM1 + 0.065), (0.430, ZM2 + 0.080))):
        pl = P("back_plug%d" % i, "steel", uv_name="bnc_plug", uv_origin=(xx, RY1, zz))
        bnc_plug(pl, (xx, RY1 + 0.0015, zz), (0.0, 1.0, 0.0), lod)
        parts.append(pl)
    if lod > 0:
        return parts
    # power cord plug on the floor
    pg = P("cable_pwr_plug", "black")
    tip = Vector(pwr[-1])
    dirn = (tip - Vector(pwr[-2])).normalized()
    lathe(pg, [(0.0060, 0.0), (0.0120, 0.010), (0.0175, 0.016), (0.0175, 0.036), (0.0150, 0.040), (0.0, 0.040)], 8,
          tuple(tip - dirn * 0.004), tuple(dirn))
    U(pg, "steel")
    side = dirn.cross(Vector((0.0, 0.0, 1.0))).normalized()
    for s in (-1, 1):
        a0 = tip + dirn * 0.036 + side * (s * 0.0095)
        g.pipe(pg, [tuple(a0), tuple(a0 + dirn * 0.019)], 0.0020, 6)
    parts.append(pg)
    # front patch cable: analyzer connector -> radiometer input
    pc = P("cable_patch", "rubber")
    a, b = Vector((0.515, YP - 0.040, ZM1 + 0.061)), Vector((0.322, YP - 0.040, ZM2 + 0.023))
    pp = [tuple(a), (0.512, YP - 0.062, ZM1 + 0.074), (0.488, YP - 0.078, ZM1 + 0.108),
          (0.420, YP - 0.080, ZM1 + 0.128), (0.350, YP - 0.066, ZM2 + 0.000), (0.324, YP - 0.052, ZM2 + 0.016),
          tuple(b)]
    g.pipe(pc, spline(pp, 2), 0.0030, 6)
    parts.append(pc)
    for i, (xx, zz) in enumerate(((0.515, ZM1 + 0.061), (0.322, ZM2 + 0.023))):
        pl = P("patch_plug%d" % i, "steel", uv_name="bnc_plug", uv_origin=(xx, YP, zz))
        bnc_plug(pl, (xx, YP - 0.0100, zz), (0.0, -1.0, 0.0), lod)
        parts.append(pl)
    return parts


def build_lod(spec):
    parts = build_cabinet(spec)
    parts += build_shield(spec) + swing(build_lid(spec)) + build_inside(spec)
    parts += build_rack(spec) + build_recorder(spec) + build_analyzer(spec) + build_radiometer(spec)
    parts += build_tape(spec) + build_cables(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def lid_points():
    """Envelope of the lid with its handle and hinge - tilted open as at rest (the collision does not move with the
    bone)."""
    pts = [Vector((x, y, z)) for x in (SX - R_OUT - BAND, SX + R_OUT + BAND)
           for y in (SY - R_OUT - 0.07, HY + 0.02) for z in (ZS - 0.03, ZL + 0.07)]
    m = Matrix.Rotation(math.radians(-OPEN_DEG), 3, "X")
    c = Vector((0.0, HY, HZ))
    return [tuple(m @ (p - c) + c) for p in pts]


def collision():
    cab = kx.box_pts(CX0 - 0.01, CX1 + 0.01, CY0 - 0.01, CY1 + 0.01, 0.0, ZB)
    # a component thinner than 0.5 m does not work: the shield and rack go down inside the cabinet, the
    # parts overlap, each convex
    rr = R_OUT + BAND + 0.005
    ring8 = [(SX + rr * math.cos(math.pi * k / 4), SY + rr * math.sin(math.pi * k / 4)) for k in range(8)]
    shield = [(x, y, z) for x, y in ring8 for z in (0.40, ZS)] + lid_points()
    rack = kx.box_pts(0.06, 0.58, -0.25, 0.25, 0.40, ZRT + 0.003)
    metal = kx.PEN + r"\metalplate.rvmat"
    comps = [(cab, metal), (shield, metal), (rack, metal)]
    memory = {
        "invView": [(0.0, -2.4, 1.2)],
        "ce_center": [(0.0, 0.0, ZRT / 2)],
        "ce_radius": [(0.9, 0.0, ZRT / 2)],
        # bone axes: the pen - a metre along +x from the field zero; the needles - from the axis toward the player
        # (as in M14)
        "ozl_pen_axis": [(FX0, Y_ROD, Z_ROD), (FX0 + 1.0, Y_ROD, Z_ROD)],
        SEL_RATE + "_axis": [(RATE_PIV[0], Y_NEEDLE, RATE_PIV[1]), (RATE_PIV[0], Y_NEEDLE - 0.05, RATE_PIV[1])],
        SEL_HV + "_axis": [(HV_PIV[0], Y_NEEDLE, HV_PIV[1]), (HV_PIV[0], Y_NEEDLE - 0.05, HV_PIV[1])],
        # lid axis - along the hinge, from -x to +x (the angle sign - check_lid_axis)
        "ozl_lid_axis": list(LID_AXIS),
    }
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (CX0 - 0.01, CX1 + 0.01, min(lo[1], CY0 - 0.01), CY1 + 0.01, 0.0, hi[2] + 0.004)
    return comps, 300.0, memory, bbox


# the first ones are for the --look preview: overview, instruments, recorder (and in "work": lid
# closed), chamber; then right, back
SHOTS = [
    ("front", (-1.0, -2.3, 1.75), (0.0, 0.0, 1.05), 32),
    ("panel", (0.60, -0.95, 1.45), (0.32, RY0, 1.33), 40),
    ("recorder", (0.15, -0.95, 1.10), (0.32, RY0, 0.97), 38),
    # lid open - steeper from above: the sample on the detector deep in the chamber is visible
    ("chamber", (-0.72, -0.78, 2.15), (SX, SY, 1.18), 36),
    ("right", (1.6, -1.2, 1.7), (0.25, 0.0, 1.15), 32),
    ("back", (1.4, 1.9, 1.6), (0.0, 0.0, 0.9), 32),
]

M.look_shots = (4, 3)
M.run(build_lod, collision, SHOTS, row_step=1.6, row_shot=((1.6, -5.2, 2.0), (1.6, 0, 0.80)))
