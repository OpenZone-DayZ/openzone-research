"""M05 - electronics assembly bench: the Scientists' Electronics Packer (OZL_Eco_Pack_Electro).
Packer: cargo 10x10, three module places (module_1..3) and proxies for the modules at the same
places. Each module of the Electronics line has its own slot and working place: slot 1 - oscilloscope
M72 on the left shelf (where the former built-in S1-94 stood; it is gone); slot 2 - soldering station
M73 on the bench at the right (where the former built-in station with a stand stood; gone); slot 3 -
programmer M74 on the antistatic mat by the board.

    blender --background --python build_m05.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (instrument scales without needles,
the knob limb, housing slots, the board, the image-intensifier tube (EOP) screen "off" and the "work"
frames, rosin stains). The shared sizes of the scales and the screen are in layout.py.

The bench is the B1 base (kfurn.workbench), after the radio-electronics assembler's bench
IZHSK.296375.001 (Signal catalogue, version -03): tabletop 1600 x 710 mm, working surface height
785-810 mm, a cabinet with drawers on ball-bearing slides, a steel antistatic sheet on the tabletop.
Here: 1.60 x 0.72 m, tabletop at 0.78, a 0.42 cabinet with four drawers, a panel with an outlet strip
and a shelf at 1.40 with depth 0.30, a fluorescent light under the shelf.

Look: the "dayz" look (matte, dirtier, coloured AO). The B1 bench has chamfers on the edges of the
frame, cabinet, fronts, panel and shelf at the near LOD (own processing of the kfurn parts, the
library is untouched). The empty module places are not duplicates: slot 1 - a bare shelf, the probe
of the station's oscilloscope stays on the mat with a free BNC connector; slot 2 - rosin stains and
solder drops on the sheet (a decal) and its own outlet on the panel behind the station; slot 3 - the mat.

Instruments and props: own detailed ones - a lab power supply on the shelf (two pointer meters,
voltmeter 0..30 and ammeter 0..3, ~220 x 124 x 250 mm estimated from photos of Soviet supplies; the
needles are own parts, bones ozl_needle_v / _a), a magnifier lamp on a spring arm (ring body of
diameter 220 with a diameter 132 lens), a disassembled night-vision goggle (body 150 x 80 x 65,
estimated from photos) with the removed objective, bottom cover, screws in a jar lid and tweezers, an
18 mm EOP (body diameter 37, length ~32 estimated) in a steel prism with its power board (screen
toward the master), the probe of the station's oscilloscope (stays at the station, cable to a free
BNC connector), an antistatic mat 760 x 430 with ground snaps and a wrist strap, cassette cabinets
of 2 x 12 drawers, an open parts tray, a rosin jar, a solder spool and a wire coil. Small things are
vanilla DayZ items through proxies (kvanilla; blue boxes in the preview): screwdriver, pliers, paper
and pen, a flashlight and a D battery, a remote detonator, a radio, a rangefinder, an electrician
kit, tape.

Work look (the "work" loop, OZL_WorkFx of the mod): ozl_lamp - the light under the shelf, the ring
lamp and opal belt of the magnifier, the supply's mains lamp, the strip key (atlas _on, lit);
ozl_lamp_2 - the LED on the board (blinks, blink); ozl_screen - the EOP screen, own texture (section
screen): "off" is dark glass, "work" plays glow frames with "snow" (frames); the voltmeter and ammeter
needles are the bones ozl_needle_v / ozl_needle_a on sources of the same names (wobble): at zero at
rest, trembling around 12 V and 0.6 A at work.

Blender axes: X is width, Y is depth (face toward -Y), Z is up.
"""
import math
import os
import sys

from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kfurn  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import krender  # noqa: E402
import kvanilla as kv  # noqa: E402
import layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
X0, X1, Y0, Y1 = -0.80, 0.80, -0.36, 0.36                    # bench
ZT, ZP, SHD, CAB_W = 0.78, 1.40, 0.30, 0.42                  # tabletop, shelf top, shelf depth, cabinet
YP = Y1 - 0.02                                               # panel face
YS = Y1 - SHD                                                # shelf front
ZS = ZP - 0.02                                               # shelf bottom
OX0 = X0 + 0.30                                              # outlet strip (kfurn.workbench)
SOCK_Z = ZT + 0.09
SOCK_Y = YP - 0.046                                          # outlet face
SOCKETS = [OX0 + 0.06 + 0.12 * k for k in range(4)]
# mat
MX0, MX1, MY0, MY1 = -0.70, 0.06, -0.33, 0.10
ZM = ZT + 0.003                                              # top of the mat
# module places: slot N is module N of the line (M72 on the left shelf, M73 on the bench at the right,
# M74 on the mat by the board)
SLOTS = [(-0.67, (YS + Y1) / 2, ZP), (0.20, 0.20, ZT), (-0.09, -0.17, ZM)]
MOD_OBJ = [("m72_oscilloscope", "ozr_oscilloscope"), ("m73_solder_station", "ozr_solder_station"),
           ("m74_programmer", "ozr_programmer")]
# module envelopes from the proxy point (their MLOD near LOD, for the layout check)
MOD_BOX = [((-0.099, -0.164, 0.0), (0.086, 0.149, 0.204)), ((-0.100, -0.136, 0.0), (0.111, 0.128, 0.200)),
           ((-0.105, -0.103, 0.0), (0.106, 0.108, 0.063))]
OUT2 = (0.29, ZT + 0.075)                                    # soldering station outlet on the panel (x, z)
ROSIN_C = (0.205, 0.205)                                     # rosin stains (slot 2): centre
GP = (0.076, ZT + 0.09)                                      # ground terminal on the panel (x, z)
# power supply on the shelf
PSX0, PSX1, PSY0, PSY1, PSZ0, PSZ1 = -0.56, -0.34, YS + 0.008, YS + 0.256, ZP + 0.006, ZP + 0.13
METER_C = [(-0.500, PSZ1 - 0.036), (-0.400, PSZ1 - 0.036)]   # V and A scale windows: centre (x, z)
KNOBS = [(-0.525, ZP + 0.036, 0.012), (-0.468, ZP + 0.036, 0.010)]  # voltage and current knobs: x, z, r
TOGGLE = (-0.428, ZP + 0.024)
PILOT = (-0.428, ZP + 0.052)
POSTS = [(-0.403, "cap_red"), (-0.378, "black"), (-0.353, "post_green")]
POST_Z = ZP + 0.030
GROMMET = (-0.37, PSY1 + 0.013)                              # supply cord grommet through the shelf
# spools on the shelf
SPOOL_S, SPOOL_W = (-0.24, 0.15), (-0.24, 0.265)
# magnifier lamp: base, post top, elbow, head centre and its axis (toward the master)
LB = Vector((-0.71, 0.21, ZT))
LJ = Vector((-0.71, 0.21, ZT + 0.31))
LE = Vector((-0.58, 0.02, ZT + 0.50))
LH = Vector((-0.34, -0.17, ZT + 0.26))
LAX = Vector((0.0, -0.15, 1.0)).normalized()
_bk = (LE - LH) - LAX * (LE - LH).dot(LAX)
BACK = _bk.normalized()                                      # from the head centre to the arm
LR_OUT = 0.110
LYOKE = LH + BACK * LR_OUT                                   # edge of the body where the fork attaches
LW = LYOKE + (LE - LYOKE).normalized() * 0.06                # head joint
# night-vision goggle and its parts on the mat
NV = (-0.56, -0.02)
NV_W, NV_D, NV_H = 0.150, 0.080, 0.065
OBJ_P = (-0.665, 0.055)                                      # removed objective (stands on its end)
COVER = (-0.62, -0.19, 0.12, 0.07)                           # bottom cover: centre, size
DISH = (-0.50, -0.185)                                       # jar lid with screws
TWZ = ((-0.51, -0.262), (-0.445, -0.243))                    # tweezers: tail, tips
EOP = (-0.34, -0.255)                                        # EOP in the prism: centre
EOP_Z = ZM + 0.035                                           # EOP axis
PCB = (-0.34, -0.14, 0.09, 0.055)                            # EOP power board: centre, size
ZPCB = ZM + 0.0016
PROBE_TIP = Vector((PCB[0] + PCB[2] / 2 - 0.002, -0.150, ZPCB + 0.003))
PROBE_DIR = Vector((0.064, -0.055, 0.004)).normalized()      # from the hook to the tail
BNC_P = (-0.222, 0.074, ZM + 0.0058)                         # free probe BNC connector: end face
# alligator clips of the supply wires on the input pads of the board (left)
CLIPS_Y = [PCB[1] + 0.008, PCB[1] - 0.010]
# on the right of the bench: cassette cabinets, parts tray, rosin jar
KX0, KX1, KY0, KY1, KH = 0.50, 0.78, 0.12, 0.30, 0.15
TRX0, TRX1, TRY0, TRY1 = 0.44, 0.72, -0.31, -0.13
TIN, LID = (0.40, 0.27), (0.41, 0.19)

LOD_SPECS = [
    dict(lod=0, bev=1, sides=16),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "wb": ("enamel_grey", 0.6), "wb_front": ("enamel_front", 0.9), "wb_panel": ("enamel_panel", 0.6),
    "wb_top": ("top_steel", 0.7), "steel": ("steel", 1.0), "black": ("black", 1.0), "rubber": ("rubber", 0.5),
    "outlet": ("ivory", 1.4), "diffuser": ("diffuser", 0.5), "switch_r": ("switch_r", 1.5),
    "mat": ("esd_mat", 0.7), "psu_case": ("psu_case", 1.2), "lamp_head": ("lamp_head", 1.2),
    "opal": ("opal", 1.2), "ring_tube": ("ring_tube", 0.8), "front_dark": ("front_dark", 2.0),
    "dial": ("dial", 5.0), "needle": ("needle", 2.0), "psu_lamp": ("psu_lamp", 2.0), "chrome": ("chrome", 1.6),
    "cap_red": ("cap_red", 1.6), "post_green": ("post_green", 1.6), "pcb": ("pcb", 6.0), "ferrite": ("ferrite", 3.0),
    "hv_block": ("hv_block", 3.0), "cap_blue": ("cap_blue", 3.0), "resistor": ("resistor", 3.0),
    "pcb_led": ("pcb_led", 4.0), "olive": ("olive", 1.6), "lens": ("lens_dark", 2.0), "eop_body": ("eop_body", 2.5),
    "brass": ("brass", 2.5), "cable_grey": ("cable_grey", 0.5), "wire_red": ("wire_red", 0.6),
    "wire_black": ("wire_black", 0.6), "clip_steel": ("clip_steel", 3.0), "boot_red": ("boot_red", 2.5),
    "boot_black": ("boot_black", 2.5), "probe": ("probe", 2.0), "cassette": ("cassette", 1.2),
    "drawer_y": ("drawer_y", 1.6), "solder": ("solder", 1.5), "tin": ("tin", 2.0), "rosin": ("rosin", 2.0),
    "strap": ("strap", 1.5), "tray": ("tray", 1.2), "cap_red_small": ("cap_red", 3.0),
    "led_spare": ("led_spare", 3.0),
}

# =============================================================================
# Materials
# =============================================================================


def decal(name, ax, sign, axes, center, size, face, eps=0.0012):
    return (os.path.join(WORK, name), ax, sign, axes, center, size, (face - eps, face + eps))


def rect(name, r, y_face):
    x0, x1, z0, z1 = r
    return decal(name, "y", -1, ("x", "z"), ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0), y_face)


def dial_rect(cx, cz):
    return (cx - L.DIAL_W / 2, cx + L.DIAL_W / 2, cz - L.DIAL_H / 2, cz + L.DIAL_H / 2)


def build_sheet(mat, origin, seed=2.0, tone=0.30, along="x", gloss=0.55, spec=0.75, floor_z=0.0, dust=0.25,
                grime=0.35, decal_items=()):
    """Steel tabletop sheet: like kmats.build_steel but with decals over the brushing - rosin stains and
    solder drops where the soldering station stands (slot 2 is empty - it shows that soldering happens here)."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    if kmats.LOOK["name"] == "dayz":
        tone *= kmats.LOOK["steel"]
    k = {"x": (0.02, 1.0, 1.0), "y": (1.0, 0.02, 1.0), "z": (1.0, 1.0, 0.02)}[along]
    brush = t.noise(t.stretch(vec, *k), 120.0, 4.0, 0.7)
    smudge = t.noise(vec, 3.5, 6.0, 0.6)
    v = t.math("ADD", tone, t.math("ADD", t.math("MULTIPLY", t.math("SUBTRACT", brush, 0.5), 0.10),
                                   t.math("MULTIPLY", t.math("SUBTRACT", smudge, 0.5), 0.12)))
    comb = t.node("ShaderNodeCombineColor")
    for i in range(3):
        t.link(v, comb.inputs[i])
    col = t.mixc(0.12, comb.outputs[0], (0.30, 0.31, 0.33, 1))
    col = kmats.decals(t, col, sep, nsep, decal_items)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.45)
    g_ = t.math("SUBTRACT", gloss, t.math("MULTIPLY", t.math("ADD", dirt, t.math("MULTIPLY", smudge, 0.3)), gloss * 0.6))
    s_ = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.6))
    return kmats.out(t, col, g_, s_, t.math("MULTIPLY", brush, 0.08))


DIALS = [rect("decal_meter_%s.png" % k, dial_rect(*c), PSY0 - 0.0015) for k, c in zip(("v", "a"), METER_C)]
KNOB_RING = [decal("decal_knob_ring.png", "y", -1, ("x", "z"), (KNOBS[0][0], KNOBS[0][1]), (0.046, 0.046), PSY0)]
VENTS = [decal("decal_vents.png", "x", s, ("y", "z"), ((PSY0 + PSY1) / 2 + 0.01, ZP + 0.072), (0.17, 0.07), x, 0.002)
         for s, x in ((-1, PSX0), (1, PSX1))]
PCBD = [decal("decal_pcb.png", "z", 1, ("x", "y"), (PCB[0], PCB[1]), (PCB[2], PCB[3]), ZPCB)]
ROSIN = [decal("decal_rosin.png", "z", 1, ("x", "y"), ROSIN_C, L.ROSIN_SIZE, ZT, 0.002)]

KINDS = kmats.std_kinds(floor_z=0.0)
# Scientists' grey enamel: tidy, few chips; almost no rust (a laboratory)
GREY = dict(color=kmats.lin((132, 138, 136)), under=kmats.lin((60, 60, 62)), seed=2.3, gloss=0.40, spec=0.30,
            chip=(0.66, 0.72), rust=(0.70, 0.78), rust_low=0.4, floor_z=0.0, dust=0.22, grime=0.35)
CASE = dict(color=kmats.lin((204, 194, 166)), under=kmats.lin((96, 94, 90)), seed=3.7, gloss=0.40, spec=0.30,
            chip=(0.70, 0.76), rust=(0.99, 1.0), rust_low=0.0, floor_z=ZT, dust=0.25, grime=0.2)
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
KINDS.update({
    "enamel_grey": ("paint", GREY),
    "enamel_front": ("paint", dict(GREY, color=kmats.lin((146, 152, 150)), seed=2.9, chip=(0.66, 0.72))),
    "enamel_panel": ("paint", dict(GREY, color=kmats.lin((160, 165, 160)), seed=3.1, chip=(0.70, 0.76), rust_low=0.0,
                                   floor_z=ZT, grime=0.25)),
    "top_steel": (build_sheet, dict(seed=6.2, tone=0.36, along="x", floor_z=ZT, dust=0.2, grime=0.25,
                                    decal_items=ROSIN)),
    "ivory": ("plastic", dict(color=kmats.lin((214, 206, 184)), gloss=0.45, spec=0.3, dust=0.25, grime=0.3)),
    # light diffuser: "off" - milky plastic, "work" - glows
    "diffuser": ("plastic", dict(color=kmats.lin((214, 214, 206)), gloss=0.35, spec=0.25, dust=0.3, grime=0.1)),
    "diffuser_on": ("flat", dict(color=kmats.lin((255, 252, 240)), gloss=0.35, spec=0.25)),
    "switch_r": ("flat", dict(color=kmats.lin((120, 26, 22)), gloss=0.6, spec=0.5)),
    "switch_r_on": ("flat", dict(color=kmats.lin((255, 70, 50)), gloss=0.6, spec=0.5)),
    "esd_mat": ("plastic", dict(color=kmats.lin((70, 98, 110)), gloss=0.12, spec=0.08, mottle=0.08, dust=0.3,
                                grime=0.2, scuff=(0.72, 0.80))),
    "psu_case": ("paint", dict(CASE, color=kmats.lin((196, 188, 164)), seed=3.3, decal_items=VENTS)),
    "lamp_head": ("paint", dict(CASE, color=kmats.lin((214, 208, 190)), seed=4.1)),
    "opal": ("plastic", dict(color=kmats.lin((226, 224, 214)), gloss=0.45, spec=0.3, dust=0.2, grime=0.1)),
    "opal_on": ("flat", dict(color=kmats.lin((255, 252, 238)), gloss=0.45, spec=0.3)),
    "ring_tube": ("flat", dict(color=kmats.lin((206, 204, 196)), gloss=0.7, spec=0.5)),
    "ring_tube_on": ("flat", dict(color=kmats.lin((255, 254, 246)), gloss=0.7, spec=0.5)),
    "front_dark": ("paint", dict(color=kmats.lin((60, 62, 64)), under=kmats.lin((130, 130, 132)), seed=5.3, gloss=0.4,
                                 spec=0.3, chip=(0.74, 0.80), rust=(0.99, 1.0), rust_low=0.0, floor_z=ZT, dust=0.15,
                                 grime=0.1, decal_items=KNOB_RING)),
    "dial": ("paint", dict(CLEAN, color=kmats.lin((236, 234, 224)), gloss=0.7, spec=0.5, decal_items=DIALS)),
    "needle": ("flat", dict(color=kmats.lin((16, 16, 16)), gloss=0.5, spec=0.4)),
    "psu_lamp": ("flat", dict(color=kmats.lin((30, 70, 36)), gloss=0.85, spec=0.8)),
    "psu_lamp_on": ("flat", dict(color=kmats.lin((90, 255, 110)), gloss=0.85, spec=0.8)),
    "chrome": ("steel", dict(seed=7.1, tone=0.42, along="x", gloss=0.7, spec=0.8, floor_z=ZT, dust=0.1, grime=0.15)),
    "post_green": ("plastic", dict(color=kmats.lin((40, 110, 54)), gloss=0.45, spec=0.3, dust=0.2)),
    "pcb": ("paint", dict(CLEAN, color=kmats.lin((34, 92, 52)), gloss=0.6, spec=0.45, dust=0.1, decal_items=PCBD)),
    "ferrite": ("plastic", dict(color=kmats.lin((46, 46, 48)), gloss=0.25, spec=0.2, mottle=0.1, dust=0.1)),
    "hv_block": ("plastic", dict(color=kmats.lin((198, 170, 92)), gloss=0.55, spec=0.35, mottle=0.12, dust=0.1)),
    "cap_blue": ("plastic", dict(color=kmats.lin((40, 60, 120)), gloss=0.5, spec=0.35, dust=0.1)),
    "resistor": ("plastic", dict(color=kmats.lin((196, 178, 132)), gloss=0.4, spec=0.25, dust=0.1)),
    "pcb_led": ("flat", dict(color=kmats.lin((90, 16, 14)), gloss=0.85, spec=0.8)),
    "pcb_led_on": ("flat", dict(color=kmats.lin((255, 60, 40)), gloss=0.85, spec=0.8)),
    "led_spare": ("flat", dict(color=kmats.lin((110, 20, 18)), gloss=0.8, spec=0.7)),
    "olive": ("paint", dict(color=kmats.lin((66, 70, 52)), under=kmats.lin((40, 40, 40)), seed=7.1, gloss=0.3, spec=0.25,
                            chip=(0.60, 0.66), rust=(0.99, 1.0), rust_low=0.0, floor_z=ZT, dust=0.2, grime=0.35)),
    "lens_dark": ("flat", dict(color=kmats.lin((40, 52, 66)), gloss=0.95, spec=0.9)),
    "eop_body": ("plastic", dict(color=kmats.lin((26, 26, 27)), gloss=0.25, spec=0.15, dust=0.15, scuff=(0.7, 0.8))),
    "brass": ("paint", dict(CLEAN, color=kmats.lin((168, 136, 74)), gloss=0.55, spec=0.55, dust=0.05)),
    "cable_grey": ("plastic", dict(color=kmats.lin((118, 120, 118)), gloss=0.30, spec=0.2, dust=0.3)),
    "wire_red": ("plastic", dict(color=kmats.lin((168, 40, 30)), gloss=0.45, spec=0.3, dust=0.2)),
    "wire_black": ("plastic", dict(color=kmats.lin((24, 24, 25)), gloss=0.40, spec=0.3, dust=0.2)),
    "clip_steel": ("steel", dict(seed=8.1, tone=0.40, along="x", gloss=0.6, spec=0.7, dust=0.1, grime=0.4)),
    "boot_red": ("plastic", dict(color=kmats.lin((168, 30, 26)), gloss=0.35, spec=0.25, dust=0.3, grime=0.4,
                                 scuff=(0.66, 0.74))),
    "boot_black": ("plastic", dict(color=kmats.lin((26, 26, 28)), gloss=0.3, spec=0.2, dust=0.3, grime=0.4,
                                   scuff=(0.66, 0.74))),
    "probe": ("plastic", dict(color=kmats.lin((96, 98, 100)), gloss=0.35, spec=0.25, dust=0.2, scuff=(0.66, 0.74))),
    "cassette": ("plastic", dict(color=kmats.lin((190, 192, 188)), gloss=0.40, spec=0.30, dust=0.3)),
    "drawer_y": ("plastic", dict(color=kmats.lin((222, 196, 118)), gloss=0.55, spec=0.4, mottle=0.12, dust=0.2)),
    "tray": ("plastic", dict(color=kmats.lin((150, 154, 150)), gloss=0.35, spec=0.25, dust=0.3, grime=0.3)),
    "solder": ("steel", dict(seed=8.8, tone=0.50, along="z", dust=0.1, grime=0.1)),
    "tin": ("steel", dict(seed=9.4, tone=0.34, along="z", gloss=0.5, spec=0.6, floor_z=ZT, dust=0.15, grime=0.5)),
    "rosin": ("flat", dict(color=kmats.lin((150, 92, 24)), gloss=0.85, spec=0.6)),
    "strap": ("plastic", dict(color=kmats.lin((36, 52, 96)), gloss=0.15, spec=0.08, mottle=0.15, dust=0.3,
                              grime=0.4)),
})

OBJ, NAME = "m05_electro_pack", "ozr_electro_pack"
# Work look: lamps use atlas _on (lit), the board LED the same atlas, blinking; the EOP screen has its
# own texture with frames; needles are bones on their own sources (wobble)
SEL_SCREEN, SEL_LAMP, SEL_LED = "ozl_screen", "ozl_lamp", "ozl_lamp_2"
SEL_NEEDLE = {"v": "ozl_needle_v", "a": "ozl_needle_a"}
ON = dict(remap={"diffuser": "diffuser_on", "switch_r": "switch_r_on", "opal": "opal_on", "ring_tube": "ring_tube_on",
                 "psu_lamp": "psu_lamp_on", "pcb_led": "pcb_led_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
NEEDLE_ANIMS = tuple((SEL_NEEDLE[k], dict(type="rotation", source=SEL_NEEDLE[k], selection=SEL_NEEDLE[k],
                                          axis=SEL_NEEDLE[k] + "_axis", memory=1, minValue=0.0, maxValue=1.0,
                                          angle0=0.0, angle1=math.radians(L.SWEEP_DEG)))
                     for k in ("v", "a"))
SCREEN = dict(off="decal_eop_off.png", frames=["decal_eop_f%02d.png" % i for i in range(L.EOP_FRAMES)], size=L.EOP_PX,
              gloss=0.8)
# proxies for the modules: the mod's CfgNonAIVehicles binds slots OZL_Tool1..3 to them (Proxyozl_tool1..3)
PROXIES = [(r"\OpenZone_Research\models\proxies\ozl_tool%d" % (i + 1), s) for i, s in enumerate(SLOTS)]
# vanilla DayZ items: proxies, drawn by the engine; the preview shows blue boxes of their size
DETONATOR = r"dz\gear\tools\RemoteDetonator"
RANGEFINDER = r"dz\gear\optics\Rangefinder"
DECOR = [
    kv.put("screwdriver", (-0.56, -0.298, ZM), **kv.flat(180)),          # on the mat, tip to the left
    kv.put("pliers", (0.112, -0.20, ZT), **kv.flat(100)),                 # by the mat on the right
    kv.put("paper", (0.28, -0.21, ZT), lift=0.0015, **kv.flat(96)),        # sheet with notes
    kv.put("pen", (0.31, -0.17, ZT), lift=0.0025, **kv.flat(35)),          # pen on the sheet
    kv.put("flashlight", (0.535, -0.065, ZT), up=(0, 0, 1), fwd=(0.15, -1, 0)),   # flashlight for repair
    kv.put("batteryd", (0.70, -0.06, ZT), up=(0, 0, 1), fwd=(0, -1, 0)),
    kv.put(DETONATOR, (-0.27, 0.205, ZT), **kv.flat(2)),                 # remote detonator to take apart
    kv.put("radio", (0.02, 0.215, ZP), up=(0, 0, 1), fwd=(0, -1, 0)),    # radio on the shelf
    kv.put(RANGEFINDER, (0.33, 0.16, ZP), **kv.flat(80)),
    kv.put("electrickit", (0.52, 0.205, ZP), **kv.flat(92)),
    kv.put("ducttape", (0.70, 0.235, ZP), **kv.flat(0)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.60, 0.64, 0.62), clear=0.06, edge=0.14, smudge=0.06, streaks=0.03),
                 selections=(SEL_SCREEN, SEL_LAMP, SEL_LED, SEL_NEEDLE["v"], SEL_NEEDLE["a"]),
                 hidden=(SEL_SCREEN, SEL_LAMP, SEL_LED), states={"on": ON},
                 bones=((SEL_NEEDLE["v"], ""), (SEL_NEEDLE["a"], "")), animations=NEEDLE_ANIMS,
                 sources={SEL_NEEDLE["v"]: dict(animPeriod=0.3), SEL_NEEDLE["a"]: dict(animPeriod=0.2)},
                 proxies=PROXIES, decor=DECOR, panels={"screen": SCREEN},
                 modules=[(o, n, s) for (o, n), s in zip(MOD_OBJ, SLOTS)])
P = M.part
BOUNDS = {}
FOOT = []                                                    # own near-LOD props: (name, lo, hi)


def use(part, region):
    """Next faces of the part go to region (kind and scale from REGIONS)."""
    return part.use(region, *REGIONS[region])


def bev(lod, r=0.003, seg=1):
    return dict(r=r, seg=seg) if lod == 0 else {}


def foot(lod, name, x0, x1, y0, y1, z0, z1):
    if lod == 0:
        FOOT.append((name, (x0, y0, z0), (x1, y1, z1)))


# =============================================================================
# Primitives missing from kgeo
# =============================================================================
def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, from M04)."""
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


def basis(axis):
    """Two axes perpendicular to axis."""
    a = Vector(axis).normalized()
    u = a.cross(Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))).normalized()
    return a, u, a.cross(u).normalized()


def rod(part, a, b, r, sides):
    """Cylinder between points a and b."""
    return g.pipe(part, [tuple(a), tuple(b)], r, sides)


def face(part, verts, want):
    """Face from bmesh vertices, turned toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def lathe(part, prof, sides, center, axis=(0, 0, 1), closed=False, phase=0.0):
    """Body of revolution about axis through center: prof [(r, h)] - the section, traversed counter-clockwise
    (up the outside, inward across the top, down the inside); the face normal is (dh, -dr) in the section
    plane, so faces point outward for any profile. r = 0 is a pole; closed - the last point joins the first."""
    a, u, v = basis(axis)
    c = Vector(center)
    bm = part.bm

    def radial(k):
        ang = 2 * math.pi * k / sides + phase
        return u * math.cos(ang) + v * math.sin(ang)
    rings = []
    for r, h in prof:
        if r < 1e-7:
            rings.append([bm.verts.new(c + a * h)] * sides)
        else:
            rings.append([bm.verts.new(c + a * h + radial(k) * r) for k in range(sides)])
    n = len(prof)
    new = []
    for i in range(n if closed else n - 1):
        i2 = (i + 1) % n
        dr, dh = prof[i2][0] - prof[i][0], prof[i2][1] - prof[i][1]
        ln = math.hypot(dr, dh)
        if ln < 1e-9:
            continue
        nr, nh = dh / ln, -dr / ln
        for k in range(sides):
            j = (k + 1) % sides
            q = []
            for vv in (rings[i][k], rings[i][j], rings[i2][j], rings[i2][k]):
                if vv not in q:
                    q.append(vv)
            if len(q) < 3:
                continue
            new.append(face(part, q, radial(k + 0.5) * nr + a * nh))
    bm.normal_update()
    part.tag(new)
    return new


def torus(part, center, axis, big, small, n1, n2, phase=0.0):
    """Ring with a round section (ring lamp): a body of revolution of a closed circle."""
    prof = [(big + small * math.cos(2 * math.pi * k / n2), small * math.sin(2 * math.pi * k / n2)) for k in range(n2)]
    return lathe(part, prof, n1, center, axis, closed=True, phase=phase)


def ribbed(part, center, axis, r_out, r_in, length, n):
    """Knurled bushing along axis (knob, focus ring): 2n vertices on a circle, every other one sunk."""
    a, u, v = basis(axis)
    poly = [((r_out if k % 2 == 0 else r_in) * math.cos(math.pi * k / n), (r_out if k % 2 == 0 else r_in) * math.sin(math.pi * k / n))
            for k in range(2 * n)]
    fr = g.Frame(Vector(center) - a * (length / 2), u, v, a)
    return g.prism(part, poly, (0, 1), 0.0, length, frame=fr)


def ring(part, center, axis, r_in, r_out, length, sides):
    """Ring along an arbitrary axis: outer and inner walls and two ends."""
    h = length / 2
    return lathe(part, [(r_in, -h), (r_out, -h), (r_out, h), (r_in, h)], sides, center, axis, closed=True)


def disc(part, center, axis, r, sides):
    """Flat disc facing along axis."""
    _, u, v = basis(axis)
    c = Vector(center)
    return g.quad(part, [tuple(c + (u * math.cos(2 * math.pi * k / sides) + v * math.sin(2 * math.pi * k / sides)) * r)
                         for k in range(sides)])


def helix(center, axis, r0, r1, length, turns, steps):
    a, u, v = basis(axis)
    c = Vector(center)
    pts = []
    for i in range(steps + 1):
        t = i / steps
        ang = 2 * math.pi * turns * t
        r = r0 + (r1 - r0) * t
        pts.append(tuple(c + a * (length * t) + (u * math.cos(ang) + v * math.sin(ang)) * r))
    return pts


def coil_on(path, r, turns, steps_per_turn):
    """Coiled cord lying on a plane: a coil of radius r around a smooth curve path (points are the cord axis)."""
    pv = [Vector(p) for p in path]
    lens = [0.0]
    for i in range(1, len(pv)):
        lens.append(lens[-1] + (pv[i] - pv[i - 1]).length)
    total = lens[-1]
    n = max(8, int(turns * steps_per_turn))
    out = []
    for s in range(n + 1):
        d = total * s / n
        i = max(0, min(len(pv) - 2, next((k for k in range(len(lens) - 1) if lens[k + 1] >= d), len(pv) - 2)))
        f = (d - lens[i]) / max(lens[i + 1] - lens[i], 1e-9)
        p = pv[i].lerp(pv[i + 1], f)
        t = (pv[i + 1] - pv[i]).normalized()
        side = t.cross(Vector((0, 0, 1))).normalized()
        up = side.cross(t).normalized()
        ang = 2 * math.pi * turns * s / n
        out.append(tuple(p + (up * math.cos(ang) + side * math.sin(ang)) * r))
    return out


def _rings(pts, r, sides):
    """Rings of a tube along a polyline - like kgeo.tube_var: the section frame is carried along without flipping."""
    pts = [Vector(p) for p in pts]
    n = len(pts)
    out, a_prev = [], None
    for i in range(n):
        if 0 < i < n - 1:
            t = (pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized()
        else:
            t = (pts[1] - pts[0]) if i == 0 else (pts[-1] - pts[-2])
        t.normalize()
        a = t.cross(Vector((0, 0, 1)))
        if a.length < 0.15:
            a = a_prev.copy() if a_prev is not None else Vector((1, 0, 0))
            a -= t * a.dot(t)
        a.normalize()
        if a_prev is not None and a.dot(a_prev) < 0:
            a = -a
        a_prev = a
        b = a.cross(t).normalized()
        out.append((pts[i], t, [pts[i] + a * (r * math.cos(2 * math.pi * k / sides)) + b * (r * math.sin(2 * math.pi * k / sides))
                                for k in range(sides)]))
    return out


def cable(name, region, pts, r, sides, chunk=0.16, group="body"):
    """Cable - a smooth tube through points, cut into parts of about chunk m: each part takes its own small
    rectangle in the atlas (one part for the whole cable would take rectangles of its whole envelope).
    The rings are shared by neighbouring pieces, so the joint is invisible. Returns the parts."""
    rings = _rings(pts, r, sides)
    lens = [0.0]
    for i in range(1, len(rings)):
        lens.append(lens[-1] + (rings[i][0] - rings[i - 1][0]).length)
    n_parts = max(1, int(math.ceil(lens[-1] / chunk - 0.25)))
    parts, made = [], {}
    for i in range(len(rings) - 1):
        k = min(n_parts - 1, int((lens[i] + lens[i + 1]) / 2 / max(lens[-1], 1e-9) * n_parts))
        if k not in made:
            made[k] = (P("%s_%d" % (name, k) if n_parts > 1 else name, region, group=group), {})
            parts.append(made[k][0])
        part, vmap = made[k]
        bm = part.bm
        for ii in (i, i + 1):
            if ii not in vmap:
                vmap[ii] = [bm.verts.new(q) for q in rings[ii][2]]
        new = []
        for s in range(sides):
            s2 = (s + 1) % sides
            quad = [vmap[i][s], vmap[i][s2], vmap[i + 1][s2], vmap[i + 1][s]]
            mid = sum((q.co for q in quad), Vector()) / 4
            axis_p = (rings[i][0] + rings[i + 1][0]) / 2
            new.append(face(part, quad, mid - axis_p))
        if i == 0:
            new.append(face(part, vmap[0][::-1], -rings[0][1]))
        if i == len(rings) - 2:
            new.append(face(part, vmap[i + 1], rings[-1][1]))
        part.tag(new)
    return parts


def croc(jaw, boot, tip, d, length=0.046, lod=0):
    """Alligator clip 50 mm (length is the length, jaws and cap are fractions of it): jaws at tip, the
    boot-like cap back along d. Returns the point where the wire leaves the cap."""
    d = Vector(d).normalized()
    side = d.cross(Vector((0, 0, 1)))
    side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
    up = side.cross(d).normalized()
    t = Vector(tip)
    fr = g.Frame(t, d, side, up)
    k = length / 0.046
    for s in (1, -1):
        poly = [(0.0, 0.0004 * s), (0.024 * k, 0.0012 * s), (0.024 * k, 0.0032 * s), (0.005 * k, 0.0017 * s)]
        if s < 0:
            poly = poly[::-1]
        g.prism(jaw, [(a, c) for a, c in poly], (0, 2), -0.0033 * k, 0.0033 * k, frame=fr)
    prof = [(0.016, 0.0036, 0.0032), (0.024, 0.0058, 0.0050), (0.036, 0.0063, 0.0055), (0.042, 0.0052, 0.0046),
            (0.046, 0.0028, 0.0028)]
    g.tube_var(boot, [tuple(t + d * (a * k)) for a, _, _ in prof], [(rx * k ** 0.5, rz * k ** 0.5) for _, rx, rz in prof],
               8 if lod == 0 else 6)
    return t + d * length


# =============================================================================
# Bench (B1 base): chamfers, light, outlets, ground terminal
# =============================================================================
BEVEL = {"wb_frame": 0.003, "wb_fronts": 0.0025, "wb_shelf": 0.0015, "wb_panel": 0.003, "wb_lamp": 0.003}


def build_bench(spec):
    lod = spec["lod"]
    parts = kfurn.workbench(M, spec, X0, X1, Y0, Y1, ZT, ZP, SHD, cab_w=CAB_W, worktop="metal", outlets=4,
                            regions={"diffuser": "diffuser", "switch": "switch_r"})
    for p in parts:
        # diffuser and the strip key light up in the "work" look
        if p.name in ("wb_diffuser", "wb_switch"):
            p.group = SEL_LAMP
        # chamfers on edges (the kfurn base is boxes with sharp edges): near LOD only
        if lod == 0 and p.name in BEVEL:
            g.bevel(p.bm, p.bm.edges[:], BEVEL[p.name], 1)
    if lod == 2:
        return parts
    # end caps of the light under the shelf
    ec = P("lamp_endcaps", "black")
    for xa, xb in ((X0 + 0.112, X0 + 0.124), (X1 - 0.124, X1 - 0.112)):
        g.box(ec, xa, xb, YS + 0.016, YS + 0.114, ZS - 0.049, ZS, **bev(lod, 0.002))
    parts.append(ec)
    return parts


def build_outlets(spec):
    """Lamp and supply plugs in the strip outlets; the soldering station's own outlet on the panel (slot 2)."""
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    pl = P("plugs", "black")
    prof = [(0.0175, 0.0), (0.0175, 0.019), (0.0166, 0.024), (0.0125, 0.0275), (0.0068, 0.030), (0.0058, 0.041),
            (0.0, 0.0415)]
    for x in SOCKETS[:2]:
        lathe(pl, prof if lod == 0 else [prof[i] for i in (0, 1, 3, 5, 6)], 10 if lod == 0 else 6, (x, SOCK_Y, SOCK_Z),
              (0, -1, 0))
    parts.append(pl)
    # station outlet: round surface-mounted, ivory, two sockets and a screw
    x, z = OUT2
    so = P("socket2", "outlet")
    lathe(so, [(0.028, 0.0), (0.028, 0.016), (0.0262, 0.0215), (0.0215, 0.0245), (0.0, 0.0255)],
          12 if lod == 0 else 8, (x, YP, z), (0, -1, 0))
    parts.append(so)
    foot(lod, "station outlet", x - 0.028, x + 0.028, YP - 0.026, YP, z - 0.028, z + 0.028)
    if lod == 0:
        sk = P("socket2_holes", "black")
        for dx in (-0.0095, 0.0095):
            g.cyl(sk, (x + dx, YP - 0.0252, z), "y", 0.0026, 0.0012, 8)
        g.cyl(sk, (x, YP - 0.0256, z + 0.014), "y", 0.0022, 0.0008, 8)
        parts.append(sk)
    return parts


def build_ground(spec):
    """Ground terminal on the panel to the right of the strip: an insulating plate, two studs with nuts and
    a wing nut; a wire from the snap at the rear corner of the mat to the lower stud."""
    lod = spec["lod"]
    if lod == 2:
        return []
    x, z = GP
    parts = []
    pl = P("ground_plate", "black")
    g.box(pl, x - 0.014, x + 0.014, YP - 0.006, YP, z - 0.034, z + 0.034, **bev(lod, 0.0015))
    parts.append(pl)
    st = P("ground_studs", "steel")
    for zz in (z + 0.016, z - 0.016) if lod == 0 else ():
        g.cyl(st, (x, YP - 0.0085, zz), "y", 0.0050, 0.005, 6)                  # nut
        g.cyl(st, (x, YP - 0.016, zz), "y", 0.0024, 0.013, 6)  # stud
        if lod == 0:
            g.cyl(st, (x, YP - 0.0125, zz), "y", 0.0068, 0.0012, 8)            # washer under the lug
            g.cyl(st, (x, YP - 0.0185, zz), "y", 0.0036, 0.004, 8)             # wing nut: hub and ears
            g.box(st, x - 0.010, x + 0.010, YP - 0.020, YP - 0.017, zz - 0.0022, zz + 0.0022)
    parts.append(st)
    # wire: snap on the mat - over the sheet to the panel - up to the lower stud
    snap = (MX1 - 0.03, MY1 - 0.03)
    pts = [(snap[0], snap[1], ZM + 0.004), (snap[0] + 0.004, snap[1] + 0.035, ZT + 0.0035),
           (snap[0] + 0.012, 0.20, ZT + 0.003), (snap[0] + 0.03, 0.29, ZT + 0.0035), (x - 0.006, YP - 0.026, ZT + 0.022),
           (x - 0.001, YP - 0.024, z - 0.030), (x, YP - 0.0135, z - 0.016)]
    parts += cable("ground_cord", "cable_grey", spline(pts, 2) if lod == 0 else pts, 0.0026, 5 if lod == 0 else 4)
    return parts


# =============================================================================
# Shelf: power supply, spools, cord grommet
# =============================================================================
def needle_pivot(cx, cz):
    """Meter needle axis with the scale window at (cx, cz): fractions of the window - layout.PIVOT."""
    x0, x1, z0, z1 = dial_rect(cx, cz)
    return x0 + L.PIVOT[0] * (x1 - x0), z1 - L.PIVOT[1] * (z1 - z0)


NEEDLE_Y = PSY0 - 0.0032                                     # the needle is in front of the scale
NEEDLE_POSE = {}                                             # preview of "work": bone -> (axis, degrees)
for _k, _c in zip(("v", "a"), METER_C):
    _px, _pz = needle_pivot(*_c)
    NEEDLE_POSE[SEL_NEEDLE[_k]] = ((_px, NEEDLE_Y, _pz), L.METERS[_k]["mid"] * L.SWEEP_DEG)


def build_psu(spec):
    """Laboratory power supply: housing with rounded edges, slots (a decal) and a handle on top, framed
    face, two meters under glass with their own needles, knobs with skirts, a toggle, a mains lamp,
    terminals with banana plugs of the wires, rubber feet."""
    lod = spec["lod"]
    parts = []
    cs = P("psu_case", "psu_case")
    g.box(cs, PSX0, PSX1, PSY0 + 0.010, PSY1, PSZ0, PSZ1, **bev(lod, 0.006, 2))
    parts.append(cs)
    fp = P("psu_front", "front_dark")
    g.box(fp, PSX0 + 0.003, PSX1 - 0.003, PSY0, PSY0 + 0.012, PSZ0 + 0.003, PSZ1 - 0.003, **bev(lod, 0.0015))
    parts.append(fp)
    foot(lod, "power supply", PSX0, PSX1, PSY0 - 0.02, PSY1, ZP, PSZ1 + 0.03)
    if lod == 2:
        return parts
    ft = P("psu_feet", "rubber")
    for x in (PSX0 + 0.02, PSX1 - 0.02) if lod == 0 else ():
        for y in (PSY0 + 0.03, PSY1 - 0.03):
            g.cyl(ft, (x, y, ZP + 0.003), "z", 0.009, 0.006, 6)
    parts.append(ft)
    # meters: scale (a decal without a needle), bezel, needle - its own part (bone), axle cap, glass
    dl, bz = P("psu_dials", "dial"), P("psu_bezels", "black")
    for cx, cz in METER_C:
        x0, x1, z0, z1 = dial_rect(cx, cz)
        g.box(dl, x0, x1, PSY0 - 0.0015, PSY0 + 0.001, z0, z1)
        t = 0.005
        for a0, a1, b0, b1 in ((x0 - t, x1 + t, z1, z1 + t), (x0 - t, x1 + t, z0 - t, z0), (x0 - t, x0, z0, z1),
                               (x1, x1 + t, z0, z1)):
            g.box(bz, a0, a1, PSY0 - 0.0065, PSY0, b0, b1)
    parts += [dl, bz]
    a0 = math.radians(L.ARC_DEG[0])
    d = Vector((math.cos(a0), 0.0, math.sin(a0)))
    pp = Vector((-math.sin(a0), 0.0, math.cos(a0)))
    ln, tail = L.NEEDLE_R * L.DIAL_H, L.NEEDLE_TAIL * L.DIAL_H
    for key, (cx, cz) in zip(("v", "a"), METER_C):
        px, pz = needle_pivot(cx, cz)
        nd = P("psu_needle_" + key, "needle", group=SEL_NEEDLE[key])
        fr = g.Frame((px, NEEDLE_Y, pz), d, pp, (0, -1, 0))
        g.prism(nd, [(-tail, -0.0009), (ln, -0.00025), (ln, 0.00025), (-tail, 0.0009)], (0, 1), -0.0003, 0.0003, frame=fr)
        g.cyl(nd, (px, NEEDLE_Y - 0.0006, pz), "y", 0.0024, 0.0014, 8 if lod == 0 else 6)
        parts.append(nd)
    if lod == 0:
        gl = P("psu_glass", "psu_case", section="glass")
        for cx, cz in METER_C:
            x0, x1, z0, z1 = dial_rect(cx, cz)
            y = PSY0 - 0.0058
            g.quad(gl, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)])
        parts.append(gl)
    # knobs: skirt with a mark, knurled body, cap
    kn = P("psu_knobs", "black")
    ix = P("psu_knob_marks", "dial")
    for i, (x, z, r) in enumerate(KNOBS):
        c0 = (x, PSY0, z)
        if lod == 0:
            lathe(kn, [(r + 0.0035, 0.0), (r + 0.0035, 0.0022), (r + 0.0012, 0.0032), (r * 0.98, 0.0036)], 12, c0, (0, -1, 0))
            ribbed(kn, (x, PSY0 - 0.0091, z), (0, -1, 0), r, r - 0.0007, 0.011, 10 if i == 0 else 8)
            lathe(kn, [(r - 0.0004, 0.0146), (r * 0.82, 0.0158), (0.0, 0.0163)], 10, c0, (0, -1, 0))
            g.box(ix, x - 0.0006, x + 0.0006, PSY0 - 0.0037, PSY0 - 0.0031, z + r + 0.0004, z + r + 0.0031)
        else:
            g.cyl(kn, (x, PSY0 - 0.008, z), "y", r, 0.016, 8)
    parts.append(kn)
    if lod == 0:
        parts.append(ix)
    # mains toggle
    tg = P("psu_toggle", "chrome")
    x, z = TOGGLE
    g.cyl(tg, (x, PSY0 - 0.002, z), "y", 0.0065, 0.004, 6)
    if lod == 0:
        g.cyl(tg, (x, PSY0 - 0.0055, z), "y", 0.0040, 0.003, 8)
        a = Vector((x, PSY0 - 0.006, z))
        b = a + Vector((0.0, -0.0125, 0.0068))
        rod(tg, a, b, 0.0015, 6)
        lathe(tg, [(0.0, -0.0022), (0.0017, -0.0015), (0.0022, 0.0), (0.0017, 0.0015), (0.0, 0.0022)], 6, b, b - a)
    parts.append(tg)
    # mains lamp: chrome rim and green cap (ozl_lamp)
    x, z = PILOT
    if lod == 0:
        pb = P("psu_pilot_bezel", "chrome")
        lathe(pb, [(0.0062, 0.0), (0.0062, 0.0025), (0.0049, 0.0036), (0.0040, 0.0036)], 12, (x, PSY0, z), (0, -1, 0))
        parts.append(pb)
    pl = P("psu_pilot", "psu_lamp", group=SEL_LAMP)
    lathe(pl, [(0.0040, 0.0030), (0.0039, 0.0050), (0.0028, 0.0068), (0.0, 0.0075)], 10 if lod == 0 else 6,
          (x, PSY0, z), (0, -1, 0))
    parts.append(pl)
    # terminals: hex base, cap, a hole for a banana; banana plugs of wires in the red and black ones
    pb = P("psu_post_bases", "black")
    pc = P("psu_posts", "cap_red")
    for x, reg in POSTS:
        if lod == 0:
            g.cyl(pb, (x, PSY0 - 0.0015, POST_Z), "y", 0.0085, 0.003, 6)
        use(pc, reg)
        prof = [(0.0072, 0.003), (0.0072, 0.007), (0.0062, 0.0085), (0.0062, 0.016), (0.0050, 0.0178), (0.0024, 0.0184)]
        lathe(pc, prof if lod == 0 else [prof[i] for i in (0, 3, 5)], 8 if lod == 0 else 5, (x, PSY0, POST_Z), (0, -1, 0))
    parts += [pb, pc]
    bn = P("psu_bananas", "cap_red")
    for x, reg in POSTS[:2] if lod == 0 else ():
        use(bn, reg)
        lathe(bn, [(0.0043, 0.0184), (0.0043, 0.030), (0.0036, 0.034), (0.0023, 0.040), (0.0, 0.041)],
              6, (x, PSY0, POST_Z), (0, -1, 0))
    parts.append(bn)
    # carry handle on top
    hd = P("psu_handle", "chrome")
    yc = (PSY0 + PSY1) / 2
    hp = [(PSX0 + 0.035, yc, PSZ1 + 0.004), (PSX0 + 0.035, yc, PSZ1 + 0.020), (PSX0 + 0.050, yc, PSZ1 + 0.029),
          (PSX1 - 0.050, yc, PSZ1 + 0.029), (PSX1 - 0.035, yc, PSZ1 + 0.020), (PSX1 - 0.035, yc, PSZ1 + 0.004)]
    g.pipe(hd, spline(hp, 2) if lod == 0 else hp, 0.0042, 8 if lod == 0 else 6)
    parts.append(hd)
    if lod == 0:
        hb = P("psu_handle_blocks", "black")
        for x in (PSX0 + 0.035, PSX1 - 0.035):
            g.box(hb, x - 0.009, x + 0.009, yc - 0.012, yc + 0.012, PSZ1 - 0.001, PSZ1 + 0.008, r=0.002, seg=1)
        parts.append(hb)
        # face screws
        sc = P("psu_screws", "chrome")
        for x in (PSX0 + 0.009, PSX1 - 0.009):
            for z in (PSZ0 + 0.009, PSZ1 - 0.009):
                g.cyl(sc, (x, PSY0 - 0.0006, z), "y", 0.0026, 0.0012, 6)
        parts.append(sc)
    # mains cord: from the rear wall to the grommet through the shelf (under the shelf it runs along the panel to
    # the outlet)
    gx, gy = GROMMET
    gr = P("psu_grommets", "rubber")
    for z0, ax in ((ZP, (0, 0, 1)),) if lod == 0 else ():
        lathe(gr, [(0.0110, 0.0), (0.0110, 0.0018), (0.0078, 0.0034), (0.0046, 0.0026), (0.0, 0.0022)],
              10 if lod == 0 else 6, (gx, gy, z0), ax)
    parts.append(gr)
    pts = [(gx, PSY1 - 0.004, PSZ0 + 0.024), (gx, PSY1 + 0.005, PSZ0 + 0.020), (gx, gy - 0.001, ZP + 0.012),
           (gx, gy, ZP + 0.002)]
    parts += cable("psu_mains_top", "rubber", spline(pts, 2) if lod == 0 else pts, 0.003, 6 if lod == 0 else 4)
    x1 = SOCKETS[1]
    pts = [(gx, gy, ZS - 0.002), (gx + 0.001, gy + 0.002, ZS - 0.06), (gx + 0.006, YP - 0.006, 1.15), (gx + 0.018, YP - 0.006, 1.00),
           (x1 - 0.010, YP - 0.020, SOCK_Z + 0.050), (x1, SOCK_Y - 0.052, SOCK_Z + 0.012), (x1, SOCK_Y - 0.0415, SOCK_Z)]
    parts += cable("psu_mains", "rubber", spline(pts, 2) if lod == 0 else pts, 0.003, 5 if lod == 0 else 4)
    return parts


def build_spools(spec):
    """Solder spool (black cheeks, tin winding, wire tail) and a coil of hookup wire."""
    lod = spec["lod"]
    if lod == 2:
        return []
    n = 16 if lod == 0 else 8
    parts = []
    fl = P("spool_flanges", "black")
    sp = P("solder_spool", "solder")
    wr = P("wire_spool", "wire_red")
    for (x, y), wind, rw, h in ((SPOOL_S, sp, 0.034, 0.050), (SPOOL_W, wr, 0.036, 0.042)):
        for z0 in (ZP, ZP + h - 0.004):
            g.cyl(fl, (x, y, z0 + 0.002), "z", 0.043, 0.004, n)
        lathe(wind, [(rw, ZP + 0.004), (rw, ZP + h - 0.004)], n, (x, y, 0.0), (0, 0, 1))
        foot(lod, "spool", x - 0.043, x + 0.043, y - 0.043, y + 0.043, ZP, ZP + h)
    parts += [fl, sp, wr]
    if lod == 0:
        # solder tail hangs from the spool onto the shelf, the wire end in a loop
        x, y = SPOOL_S
        pts = [(x + 0.034, y - 0.006, ZP + 0.030), (x + 0.046, y - 0.010, ZP + 0.024), (x + 0.058, y - 0.022, ZP + 0.010),
               (x + 0.066, y - 0.040, ZP + 0.0012), (x + 0.075, y - 0.070, ZP + 0.0012)]
        g.pipe(sp, spline(pts, 3), 0.0010, 5)
        x, y = SPOOL_W
        pts = [(x - 0.036, y - 0.004, ZP + 0.024), (x - 0.050, y - 0.010, ZP + 0.018), (x - 0.060, y - 0.030, ZP + 0.006),
               (x - 0.055, y - 0.060, ZP + 0.0014), (x - 0.035, y - 0.070, ZP + 0.0014)]
        g.pipe(wr, spline(pts, 3), 0.0011, 5)
    return parts


# =============================================================================
# Magnifier lamp
# =============================================================================
def joint_axis(d):
    """Arm joint axis: horizontal, across link d."""
    a = Vector(d).cross(Vector((0, 0, 1)))
    return a.normalized() if a.length > 1e-6 else Vector((1, 0, 0))


HEAD_SHELL = [(0.100, -0.004), (0.107, 0.001), (0.110, 0.010), (0.106, 0.019), (0.092, 0.026), (0.077, 0.027),
              (0.066, 0.012), (0.066, -0.004)]
OPAL = [(0.090, -0.020), (0.1015, -0.020), (0.1015, -0.0045), (0.090, -0.0045)]


def build_lamp(spec):
    """Magnifier lamp: weighted base, post, two links of rod pairs with springs below, joints with lock
    knobs, a ring body with a lens in a rim, a ring lamp and an opal belt (ozl_lamp), a handle, a key; a
    wire down the arm and over the bench to the outlet."""
    lod, sd = spec["lod"], spec["sides"]
    parts = []
    bs = P("lamp_base", "lamp_head")
    prof = [(0.0, 0.0), (0.076, 0.0), (0.076, 0.010), (0.073, 0.018), (0.060, 0.025), (0.022, 0.029), (0.016, 0.032),
            (0.016, 0.046), (0.0, 0.046)]
    lathe(bs, prof if lod == 0 else [prof[i] for i in (0, 1, 2, 4, 6, 7, 8)], 20 if lod == 0 else (12 if lod == 1 else 8),
          LB, (0, 0, 1))
    parts.append(bs)
    foot(lod, "magnifier base", LB.x - 0.076, LB.x + 0.076, LB.y - 0.076, LB.y + 0.076, ZT, ZT + 0.046)
    j1, j2 = joint_axis(LE - LJ), joint_axis(LW - LE)
    jm = (j1 + j2).normalized()
    if lod == 2:
        ar = P("lamp_arm", "steel")
        g.pipe(ar, [tuple(LB + Vector((0, 0, 0.04))), tuple(LJ), tuple(LE), tuple(LW), tuple(LYOKE)], 0.008, 3)
        hd = P("lamp_head", "lamp_head")
        lathe(hd, [HEAD_SHELL[i] for i in (0, 2, 4, 6, 7)], 8, LH, LAX, closed=True)
        return parts + [ar, hd]
    ar = P("lamp_arm", "chrome")
    rod(ar, LB + Vector((0, 0, 0.044)), LJ - Vector((0, 0, 0.012)), 0.0085, sd)
    downs = []
    for p0, p1, ja in ((LJ, LE, j1), (LE, LW, j2)):
        dd = (p1 - p0).normalized()
        dn = dd.cross(ja).normalized()
        if dn.z > 0:
            dn = -dn
        downs.append(dn)
        for s in ((-1, 1) if lod == 0 else (0,)):
            off = ja * 0.011 * s
            rod(ar, p0 + off, p1 + off, 0.0045 if lod == 0 else 0.007, 8 if lod == 0 else 4)
    parts.append(ar)
    # joints: rounded hubs across the links, knurled lock knobs
    jn = P("lamp_joints", "black")
    for c, ja, r, ln in ((LJ, j1, 0.016, 0.040), (LE, jm, 0.016, 0.040), (LW, j2, 0.013, 0.034)):
        h = ln / 2
        if lod == 0:
            lathe(jn, [(0.0, -h), (r - 0.002, -h), (r, -h + 0.002), (r, h - 0.002), (r - 0.002, h), (0.0, h)], 10, c, ja)
            ribbed(jn, c + ja * (h + 0.005), ja, 0.0125, 0.0112, 0.010, 8)
            lathe(jn, [(0.0112, h + 0.010), (0.0, h + 0.012)], 8, c, ja)
        else:
            g.pipe(jn, [tuple(c - ja * h), tuple(c + ja * h)], r, 8)
    parts.append(jn)
    if lod == 0:
        # balance springs under the links
        spr = P("lamp_springs", "steel")
        for (p0, p1), dn in zip(((LJ, LE), (LE, LW)), downs):
            dv = p1 - p0
            c0 = p0 + dv * 0.16 + dn * 0.020
            g.pipe(spr, helix(c0, dv, 0.0058, 0.0058, dv.length * 0.56, 7, 24), 0.0011, 3)
            for e in (c0, c0 + dv.normalized() * dv.length * 0.56):
                rod(spr, e, e - dn * 0.017, 0.0012, 3)                         # spring hooks to the link
        parts.append(spr)
    # head: body, opal belt and ring lamp below (ozl_lamp), lens in a rim, handle, key
    n = 24 if lod == 0 else 12
    hd = P("lamp_head", "lamp_head")
    lathe(hd, HEAD_SHELL if lod == 0 else [HEAD_SHELL[i] for i in (0, 2, 4, 6, 7)], n, LH, LAX, closed=True)
    parts.append(hd)
    op = P("lamp_opal", "opal", group=SEL_LAMP)
    lathe(op, OPAL, n, LH, LAX, closed=True)
    parts.append(op)
    if lod == 0:
        tb = P("lamp_tube", "ring_tube", group=SEL_LAMP)
        torus(tb, LH - LAX * 0.0135, LAX, 0.080, 0.0085, 20, 5)
        parts.append(tb)
        rim = P("lamp_bezel", "black")
        ring(rim, LH + LAX * 0.026, LAX, 0.064, 0.0745, 0.003, n)
        parts.append(rim)
    ln_ = P("lamp_lens", "lamp_head", section="glass")
    disc(ln_, LH + LAX * 0.012, LAX, 0.066, n)
    parts.append(ln_)
    jh = BACK.cross(LAX).normalized()
    yk = P("lamp_yoke", "chrome")
    rod(yk, LW, LYOKE + BACK * 0.004, 0.0065, 8 if lod == 0 else 6)
    parts.append(yk)
    if lod == 0:
        # handle at the front: stem and ball
        hn = P("lamp_handle", "black")
        front = LH - BACK * (LR_OUT - 0.004)
        tip = front - BACK * 0.042
        rod(hn, front, tip, 0.0055, 8)
        lathe(hn, [(0.0, -0.011), (0.007, -0.009), (0.0095, -0.002), (0.0090, 0.005), (0.006, 0.009), (0.0, 0.011)], 8,
              tip - BACK * 0.009, -BACK)
        # key on the body by the arm
        fr = g.Frame(LH + LAX * 0.0245 + BACK * 0.084, jh, BACK, LAX)
        g.box(hn, -0.007, 0.007, -0.006, 0.006, -0.001, 0.0055, frame=fr, r=0.0012, seg=1)
        parts.append(hn)
        # wire: from the key along the links (below the rods), along the post - into the base
        pts = [LH + LAX * 0.024 + BACK * 0.092, LYOKE + LAX * 0.018 + BACK * 0.012, LW + downs[1] * 0.012]
        dv2 = LW - LE
        pts += [LE + dv2 * 0.5 + downs[1] * 0.010, LE + downs[0] * 0.016 + jm * 0.022]
        dv1 = LE - LJ
        pts += [LJ + dv1 * 0.5 + downs[0] * 0.012, LJ + Vector((0.0, 0.0, -0.022)) + jm * 0.020,
                Vector((LB.x, LB.y, ZT + 0.20)) + jm * 0.014, Vector((LB.x, LB.y, ZT + 0.062)) + jm * 0.014,
                Vector((LB.x, LB.y, ZT + 0.040)) + jm * 0.012]
        parts += cable("lamp_cord", "cable_grey", spline([tuple(p) for p in pts], 3), 0.0026, 5)
    # wire from the base over the bench to the panel and up to the plug in outlet 0
    x0s = SOCKETS[0]
    pts = [(LB.x + 0.030, LB.y + 0.060, ZT + 0.006), (LB.x + 0.06, LB.y + 0.105, ZT + 0.0028),
           (LB.x + 0.13, YP - 0.012, ZT + 0.0028), (x0s - 0.03, YP - 0.016, ZT + 0.0035), (x0s - 0.008, SOCK_Y - 0.044, ZT + 0.020),
           (x0s, SOCK_Y - 0.054, SOCK_Z - 0.040), (x0s, SOCK_Y - 0.050, SOCK_Z - 0.008), (x0s, SOCK_Y - 0.0415, SOCK_Z)]
    parts += cable("lamp_mains", "cable_grey", spline(pts, 2) if lod == 0 else pts, 0.0026, 5 if lod == 0 else 4)
    return parts


# =============================================================================
# Mat, disassembled night-vision goggle, EOP, board, probe, supply wires
# =============================================================================
def build_mat(spec):
    """Antistatic mat with rounded corners, two ground snaps; a wrist strap on a coiled cord."""
    lod = spec["lod"]
    mt = P("esd_mat", "mat")
    g.box(mt, MX0, MX1, MY0, MY1, ZT, ZM, **bev(lod, 0.0012))
    parts = [mt]
    if lod == 2:
        return parts
    sn = P("mat_snaps", "steel")
    snaps = [(MX1 - 0.03, MY1 - 0.03), (MX1 - 0.075, MY1 - 0.022)]
    for x, y in snaps if lod == 0 else ():
        lathe(sn, [(0.0068, 0.0), (0.0068, 0.0014), (0.0050, 0.0022), (0.0034, 0.0024), (0.0034, 0.0042), (0.0, 0.0045)],
              8 if lod == 0 else 6, (x, y, ZM), (0, 0, 1))
    parts.append(sn)
    if lod == 0:
        # wrist strap: a coiled cord from the second snap, lies on the mat as a loop to the strap
        x, y = snaps[1]
        bx, by = -0.050, 0.038
        path = spline([(x - 0.004, y + 0.002, ZM + 0.0068), (x - 0.03, y + 0.010, ZM + 0.0068), (x - 0.060, y + 0.002, ZM + 0.0068),
                       (bx - 0.020, by + 0.024, ZM + 0.0068)], 4)
        cw = P("strap_coil", "wire_black")
        g.pipe(cw, coil_on(path, 0.0056, 6, 5), 0.0011, 3)
        rod(cw, (x - 0.004, y + 0.002, ZM + 0.0068), (x, y, ZM + 0.004), 0.0018, 4)
        parts.append(cw)
        st = P("strap_band", "strap")
        lathe(st, [(0.022, 0.0), (0.034, 0.0), (0.034, 0.0024), (0.022, 0.0024)], 16, (bx, by, ZM), (0, 0, 1), closed=True)
        parts.append(st)
        g.cyl(sn, (bx - 0.016, by + 0.019, ZM + 0.0034), "z", 0.0052, 0.002, 8)            # strap snap
        foot(lod, "wrist strap", bx - 0.034, bx + 0.034, by - 0.034, by + 0.034, ZM, ZM + 0.003)
    return parts


def build_nvg(spec):
    """Disassembled night-vision goggle: rounded body, eyepieces with diopter rings and eyecups (toward the
    master), objective socket at the back, battery cover and mounting pad on top; the removed objective,
    bottom cover, screws in a jar lid, tweezers."""
    lod = spec["lod"]
    parts = []
    x, y = NV
    bd = P("nvg_body", "olive")
    g.box(bd, x - NV_W / 2, x + NV_W / 2, y - NV_D / 2, y + NV_D / 2, ZM, ZM + NV_H, **bev(lod, 0.010, 2))
    parts.append(bd)
    foot(lod, "NVG body", x - NV_W / 2, x + NV_W / 2, y - NV_D / 2 - 0.05, y + NV_D / 2 + 0.008, ZM, ZM + NV_H + 0.01)
    if lod == 2:
        return parts
    ep, cup = P("nvg_eyepieces", "black"), P("nvg_eyecups", "rubber")
    for dx in (-0.033, 0.033):
        c0 = (x + dx, y - NV_D / 2 + 0.002, ZM + 0.036)
        if lod == 0:
            lathe(ep, [(0.0175, 0.0), (0.0175, 0.011), (0.0168, 0.0125), (0.0168, 0.030)], 12, c0, (0, -1, 0))
            ribbed(ep, (c0[0], c0[1] - 0.0175, c0[2]), (0, -1, 0), 0.0192, 0.0181, 0.009, 10)
            lathe(cup, [(0.0168, 0.030), (0.0182, 0.034), (0.0206, 0.042), (0.0216, 0.046), (0.0202, 0.0483), (0.0142, 0.0472),
                        (0.0122, 0.040)], 12, c0, (0, -1, 0))
            lz = P("nvg_ep_lens%d" % (dx > 0), "lens")
            disc(lz, (c0[0], c0[1] - 0.039, c0[2]), (0, -1, 0), 0.0122, 12)
            parts.append(lz)
        else:
            g.cyl(ep, (x + dx, y - NV_D / 2 - 0.018, ZM + 0.036), "y", 0.019, 0.036, 8)
    parts += [ep, cup]
    # objective socket at the back (objective removed): a threaded ring and a dark cavity
    mn = P("nvg_mount", "black")
    cm = (x, y + NV_D / 2 - 0.002, ZM + 0.034)
    lathe(mn, [(0.026, 0.0), (0.026, 0.006), (0.0245, 0.0075), (0.0195, 0.0075), (0.0195, 0.003), (0.0, 0.0028)],
          14 if lod == 0 else 8, cm, (0, 1, 0))
    parts.append(mn)
    if lod == 0:
        tp = P("nvg_top", "black")
        ribbed(tp, (x + 0.050, y + 0.012, ZM + NV_H + 0.004), (0, 0, 1), 0.0105, 0.0096, 0.008, 10)   # battery cover
        g.box(tp, x - 0.022, x + 0.022, y - 0.012, y + 0.020, ZM + NV_H - 0.001, ZM + NV_H + 0.007, r=0.0015, seg=1)
        g.box(tp, x - 0.016, x + 0.016, y - 0.008, y + 0.016, ZM + NV_H + 0.007, ZM + NV_H + 0.011, r=0.0010, seg=1)
        parts.append(tp)
        sc = P("nvg_screws", "steel")
        for sx in (-1, 1):
            for sy in (-1, 1):
                g.cyl(sc, (x + sx * (NV_W / 2 - 0.014), y + sy * (NV_D / 2 - 0.012), ZM + NV_H + 0.0004), "z", 0.0022,
                      0.0012, 6)
        parts.append(sc)
    # the removed objective stands on its thread: thread, body, knurled focus ring, lens in a mount
    ox, oy = OBJ_P
    ob = P("nvg_objective", "olive")
    oprof = [(0.0, 0.0), (0.0215, 0.0), (0.0215, 0.012), (0.0262, 0.0132), (0.0262, 0.029), (0.0280, 0.046),
             (0.0280, 0.066), (0.0300, 0.068), (0.0300, 0.0725), (0.0262, 0.0735), (0.0240, 0.0705)]
    lathe(ob, oprof if lod == 0 else [oprof[i] for i in (0, 1, 2, 4, 6, 8, 10)],
          12 if lod == 0 else 8, (ox, oy, ZM), (0, 0, 1))
    parts.append(ob)
    foot(lod, "lens", ox - 0.030, ox + 0.030, oy - 0.030, oy + 0.030, ZM, ZM + 0.074)
    if lod == 0:
        fr_ = P("nvg_focus", "black")
        ribbed(fr_, (ox, oy, ZM + 0.0375), (0, 0, 1), 0.0300, 0.0287, 0.015, 12)
        parts.append(fr_)
        lz = P("nvg_obj_lens", "lens")
        disc(lz, (ox, oy, ZM + 0.0703), (0, 0, 1), 0.0240, 14)
        parts.append(lz)
        # bottom cover of the body: a shallow tray with screw holes (lies inside up)
        cx, cy, cw, chh = COVER
        cv = P("nvg_cover", "olive")
        x0_, x1_, y0_, y1_ = cx - cw / 2, cx + cw / 2, cy - chh / 2, cy + chh / 2
        g.box(cv, x0_, x1_, y0_, y1_, ZM, ZM + 0.0025, r=0.0012, seg=1)
        for a0, a1, b0, b1 in ((x0_, x1_, y0_, y0_ + 0.003), (x0_, x1_, y1_ - 0.003, y1_), (x0_, x0_ + 0.003, y0_, y1_),
                               (x1_ - 0.003, x1_, y0_, y1_)):
            g.box(cv, a0, a1, b0, b1, ZM + 0.0025, ZM + 0.014)
        parts.append(cv)
        foot(lod, "NVG cover", x0_, x1_, y0_, y1_, ZM, ZM + 0.014)
        ch = P("nvg_cover_holes", "black")
        for sx in (-1, 1):
            for sy in (-1, 1):
                g.cyl(ch, (cx + sx * (cw / 2 - 0.012), cy + sy * (chh / 2 - 0.010), ZM + 0.0026), "z", 0.0024, 0.0004, 8)
        parts.append(ch)
        # jar lid with screws
        dx_, dy_ = DISH
        ds = P("screw_dish", "tin")
        lathe(ds, [(0.0, 0.0), (0.026, 0.0), (0.026, 0.006), (0.0245, 0.0068), (0.0245, 0.0012), (0.0, 0.0012)], 16,
              (dx_, dy_, ZM), (0, 0, 1))
        parts.append(ds)
        foot(lod, "lid with screws", dx_ - 0.026, dx_ + 0.026, dy_ - 0.026, dy_ + 0.026, ZM, ZM + 0.007)
        for k, (ax_, ay_) in enumerate(((-0.010, 0.004), (0.002, -0.009), (0.010, 0.007))):
            a = 1.3 * k
            d = Vector((math.cos(a), math.sin(a), 0.0))
            p0 = Vector((dx_ + ax_, dy_ + ay_, ZM + 0.0030))
            rod(sc, p0, p0 + d * 0.008, 0.0011, 4)
            g.cyl(sc, tuple(p0), "z", 0.0023, 0.0016, 6)
        # tweezers: two blades joined at the tail, tips apart
        tw = P("tweezers", "steel")
        t0, t1 = Vector((TWZ[0][0], TWZ[0][1], ZM + 0.0012)), Vector((TWZ[1][0], TWZ[1][1], ZM + 0.0012))
        d = (t1 - t0).normalized()
        nn = Vector((-d.y, d.x, 0.0))
        ln = (t1 - t0).length
        for s in (-1, 1):
            pts = [t0, t0 + d * ln * 0.45 + nn * s * 0.0045, t0 + d * ln * 0.85 + nn * s * 0.0030, t1 + nn * s * 0.0010]
            g.sweep(tw, [tuple(p) for p in spline([tuple(p) for p in pts], 2)], (0, 0, 1), 0.0022, 0.0006)
        parts.append(tw)
        foot(lod, "tweezers", min(t0.x, t1.x) - 0.006, max(t0.x, t1.x) + 0.006, min(t0.y, t1.y) - 0.006,
             max(t0.y, t1.y) + 0.006, ZM, ZM + 0.002)
    return parts


def build_eop(spec):
    """18 mm EOP in a steel prism with the screen toward the master: potted body, contact rings, input
    window at the back, the screen (ozl_screen, own texture) in front; two wires from the board."""
    lod = spec["lod"]
    if lod == 2:
        return []
    x, y = EOP
    parts = []
    vb = P("eop_vblock", "steel")
    poly = [(x - 0.025, ZM), (x + 0.025, ZM), (x + 0.025, ZM + 0.022), (x + 0.013, ZM + 0.022), (x, ZM + 0.009),
            (x - 0.013, ZM + 0.022), (x - 0.025, ZM + 0.022)]
    g.prism(vb, poly, (0, 2), y - 0.015, y + 0.015)
    parts.append(vb)
    foot(lod, "image tube in prism", x - 0.025, x + 0.025, y - 0.018, y + 0.016, ZM, EOP_Z + 0.019)
    tb = P("eop_tube", "eop_body")
    c0 = (x, y + 0.016, EOP_Z)                                   # rear end, axis forward to the master
    prof = [(0.0, 0.0), (0.0150, 0.0), (0.0170, 0.001), (0.0185, 0.003), (0.0185, 0.029), (0.0172, 0.031), (0.0128, 0.032),
            (0.0106, 0.031)]
    lathe(tb, prof if lod == 0 else [prof[i] for i in (0, 3, 4, 6, 7)], 12 if lod == 0 else 8, c0, (0, -1, 0))
    parts.append(tb)
    if lod == 0:
        rg = P("eop_rings", "brass")
        for h in (0.006, 0.026):
            ring(rg, (x, y + 0.016 - h, EOP_Z), (0, -1, 0), 0.0184, 0.0193, 0.0026, 12)
        parts.append(rg)
        wn = P("eop_window", "lens")
        disc(wn, (x, y + 0.0162, EOP_Z), (0, 1, 0), 0.0140, 12)
        parts.append(wn)
    sc = P("eop_screen", "black", group=SEL_SCREEN, section="screen")
    r = L.EOP_SCREEN_R
    cen = Vector((x, y + 0.016 - 0.0309, EOP_Z))
    disc(sc, cen, (0, -1, 0), r, 16 if lod == 0 else 8)
    sc.glass_frame = (g.Frame(cen, (1, 0, 0), (0, 0, 1), (0, -1, 0)), -r, r, -r, r)
    parts.append(sc)
    return parts


def build_pcb(spec):
    """EOP power board on the mat under the lens: a trace decal, a transformer on a ferrite pot core, a
    multiplier in compound, capacitors, resistors, a transistor, an LED (ozl_lamp_2, blinks), output
    wires to the EOP."""
    lod = spec["lod"]
    cx, cy, w, h = PCB
    pc = P("eop_pcb", "pcb")
    g.box(pc, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2, ZM, ZPCB)
    parts = [pc]
    foot(lod, "circuit board", cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2, ZM, ZPCB + 0.012)
    if lod == 2:
        return parts
    fe = P("pcb_trafo", "ferrite")
    lathe(fe, [(0.0, 0.0), (0.0090, 0.0), (0.0092, 0.002), (0.0092, 0.0095), (0.0085, 0.011), (0.0, 0.011)],
          10 if lod == 0 else 6, (cx - 0.025, cy + 0.008, ZPCB), (0, 0, 1))
    parts.append(fe)
    hv = P("pcb_hv", "hv_block")
    g.box(hv, cx + 0.004, cx + 0.036, cy + 0.004, cy + 0.019, ZPCB, ZPCB + 0.010, **bev(lod, 0.0015))
    parts.append(hv)
    if lod == 0:
        cp = P("pcb_caps", "cap_blue")
        for ox, oy in ((-0.004, -0.014), (0.008, -0.014)):
            lathe(cp, [(0.0, 0.0), (0.0030, 0.0), (0.0030, 0.0105), (0.0026, 0.0110), (0.0, 0.0111)], 8, (cx + ox, cy + oy, ZPCB),
                  (0, 0, 1))
        parts.append(cp)
        rs = P("pcb_resistors", "resistor")
        for k in range(4):
            g.cyl(rs, (cx + 0.022 + 0.0005 * k, cy - 0.020 + 0.0045 * k, ZPCB + 0.0013), "x", 0.0012, 0.0065, 6)
        parts.append(rs)
        bk = P("pcb_black", "black")
        g.box(bk, cx - 0.016, cx - 0.008, cy + 0.015, cy + 0.0178, ZPCB, ZPCB + 0.011, r=0.0006, seg=1)   # transistor
        g.box(bk, cx - 0.014, cx - 0.010, cy + 0.0178, cy + 0.0186, ZPCB + 0.006, ZPCB + 0.009)          # flange
        parts.append(bk)
        ld = P("pcb_led", "pcb_led", group=SEL_LED)
        lathe(ld, [(0.0028, 0.0), (0.0028, 0.0012), (0.0025, 0.0013), (0.0025, 0.0050), (0.0018, 0.0068), (0.0007, 0.0076),
                   (0.0, 0.0077)], 10, (cx + 0.036, cy - 0.016, ZPCB), (0, 0, 1))
        parts.append(ld)
        # output wires to the contact rings of the EOP
        ex, ey = EOP
        for k, (px, reg, hh) in enumerate(((cx - 0.006, "wire_red", 0.026), (cx + 0.006, "wire_black", 0.006))):
            ring_y = ey + 0.016 - hh
            side = -1 if k == 0 else 1
            pts = [(px, cy - h / 2 + 0.003, ZPCB + 0.0012), (px + side * 0.002, cy - h / 2 - 0.010, ZM + 0.0016),
                   (ex + side * 0.024, ring_y + 0.012, ZM + 0.026), (ex + side * 0.0215, ring_y, EOP_Z - 0.004),
                   (ex + side * 0.0190, ring_y, EOP_Z)]
            parts += cable("eop_wire%d" % k, reg, spline(pts, 2), 0.0009, 4)
    return parts


def build_leads(spec):
    """Supply wires: from the bananas in the terminals they hang from the shelf onto the bench, along the
    mat to the alligator clips on the input pads of the board."""
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    x_edge = PCB[0] - PCB[2] / 2
    for k, ((px, reg), ly) in enumerate(zip(POSTS[:2], CLIPS_Y)):
        wire = "wire_red" if reg == "cap_red" else "wire_black"
        tip = (x_edge - 0.007, ly, ZM + 0.0045)
        d = Vector((-1.0, 0.04 * (1 - 2 * k), 0.08))
        if lod == 0:
            stub = P("lead_stub%d" % k, "solder")
            g.pipe(stub, spline([(x_edge + 0.003, ly, ZPCB + 0.0005), (x_edge - 0.002, ly, ZPCB + 0.0012),
                                 (x_edge - 0.010, ly, ZM + 0.0045)], 2), 0.0005, 4)
            parts.append(stub)
        if lod == 0:
            jaw, boot = P("lead_clip%d" % k, "clip_steel"), P("lead_boot%d" % k, "boot_red" if k == 0 else "boot_black")
            tail = croc(jaw, boot, tip, d, lod=lod)
            parts += [jaw, boot]
        else:
            tail = Vector(tip) + d.normalized() * 0.046
        y0 = PSY0 - (0.041 if lod == 0 else 0.018)              # from a banana (middle LOD: from the terminal)
        dz = 0.012 * k
        pts = [(px, y0, POST_Z), (px - 0.002, y0 - 0.012, POST_Z - 0.010), (px - 0.006, y0 - 0.016, POST_Z - 0.045),
               (px - 0.014, y0 - 0.013, 1.25 - dz), (px - 0.024, y0 - 0.008, 1.06 - dz), (px - 0.034, y0 - 0.004, 0.92 - dz),
               (px - 0.044, y0 + 0.001, ZM + 0.045), (px - 0.050, y0 - 0.006, ZM + 0.0045),
               (-0.455 + 0.010 * k, -0.030, ZM + 0.0020), (-0.452 + 0.008 * k, ly + 0.030, ZM + 0.0021),
               (tail.x - 0.008, ly + 0.004 * (1 - 2 * k), tail.z), tuple(tail)]
        parts += cable("psu_lead%d" % k, wire, spline(pts, 2) if lod == 0 else pts, 0.0019, 4)
    return parts


def build_probe(spec):
    """Probe of the station's oscilloscope (stays at the station, slot 1 is empty - the connector is free):
    a hook on the board pad, a body with a finger stop, a ground wire with a mini-alligator, a cable
    smoothly over the mat to the BNC connector."""
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    d = PROBE_DIR
    t = PROBE_TIP
    pr = P("probe_body", "probe")
    prof = [(0.010, 0.0030), (0.020, 0.0034), (0.022, 0.0060), (0.027, 0.0062), (0.029, 0.0050), (0.034, 0.0052),
            (0.070, 0.0058), (0.082, 0.0050), (0.090, 0.0034), (0.096, 0.0026)]
    pp = prof if lod == 0 else [prof[i] for i in (0, 3, 6, 9)]
    g.tube_var(pr, [tuple(t + d * s) for s, _ in pp], [(r, r) for _, r in pp], 8 if lod == 0 else 6)
    parts.append(pr)
    foot(lod, "probe", min(t.x, (t + d * 0.096).x) - 0.006, max(t.x, (t + d * 0.096).x) + 0.006,
         min(t.y, (t + d * 0.096).y) - 0.006, max(t.y, (t + d * 0.096).y) + 0.006, ZM, ZM + 0.012)
    if lod == 0:
        hk = P("probe_hook", "steel")
        side = d.cross(Vector((0, 0, 1))).normalized()
        pts = [t + d * 0.011, t + d * 0.002, t - d * 0.0015 - Vector((0, 0, 0.0016)), t + d * 0.0012 - Vector((0, 0, 0.0034)),
               t + d * 0.0042 - Vector((0, 0, 0.0028))]
        g.pipe(hk, spline([tuple(p) for p in pts], 2), 0.0006, 4)
        parts.append(hk)
        # ground wire with a mini-alligator, lies alongside
        g0 = t + d * 0.031 + side * 0.004
        pts = [g0, g0 + side * 0.012 + d * 0.006 - Vector((0, 0, 0.002)), g0 + side * 0.026 - d * 0.010,
               g0 + side * 0.030 - d * 0.030]
        pts = [Vector((p.x, p.y, max(p.z, ZM + 0.0012))) for p in pts]
        parts += cable("probe_gnd", "wire_black", spline([tuple(p) for p in pts], 2), 0.0010, 4)
        jaw, boot = P("probe_gnd_clip", "clip_steel"), P("probe_gnd_boot", "boot_black")
        tail = pts[-1]
        dd = (pts[-1] - pts[-2]).normalized()
        tip = tail + dd * 0.030
        croc(jaw, boot, Vector((tip.x, tip.y, ZM + 0.0030)), -Vector((dd.x, dd.y, -0.02)), length=0.030)
        parts += [jaw, boot]
    # cable: from the probe tail over the mat to the free BNC connector
    e = t + d * 0.096
    bx, by, bz = BNC_P
    pts = [tuple(e), (e.x + 0.006, e.y - 0.008, ZM + 0.0025), (e.x + 0.016, e.y + 0.010, ZM + 0.0025), (-0.218, -0.11, ZM + 0.0025),
           (-0.226, -0.02, ZM + 0.0025), (bx, by - 0.055, ZM + 0.0030), (bx, by - 0.041, bz)]
    parts += cable("probe_cable", "wire_black", spline(pts, 2) if lod == 0 else pts, 0.0024, 5 if lod == 0 else 4)
    # BNC connector: body with a bayonet sleeve, rubber boot
    bn = P("probe_bnc", "chrome")
    lathe(bn, [(0.0, 0.0), (0.0042, 0.0), (0.0046, 0.0006), (0.0046, 0.0100), (0.0057, 0.0106), (0.0057, 0.0195),
               (0.0040, 0.0210), (0.0040, 0.024)], 8 if lod == 0 else 6, (bx, by, bz), (0, -1, 0))
    parts.append(bn)
    if lod == 0:
        bt = P("probe_bnc_boot", "rubber")
        lathe(bt, [(0.0040, 0.024), (0.0040, 0.032), (0.0031, 0.039), (0.0024, 0.041), (0.0, 0.0412)], 8,
              (bx, by, bz), (0, -1, 0))
        parts.append(bt)
    foot(lod, "BNC connector", bx - 0.006, bx + 0.006, by - 0.041, by, ZM, ZM + 0.012)
    if lod == 0:
        pin = P("probe_bnc_pin", "black")
        disc(pin, (bx, by + 0.0002, bz), (0, 1, 0), 0.0030, 8)
        parts.append(pin)
    return parts


# =============================================================================
# On the right of the bench: cassette cabinets, parts tray with parts, rosin jar
# =============================================================================
def build_cassettes(spec):
    """Two cassette cabinets of 12 drawers (4 x 3) one on top of the other: rounded body, drawers with tabs."""
    lod = spec["lod"]
    parts = []
    bx = P("cassettes", "cassette")
    for b in range(2):
        z0 = ZT + b * KH
        g.box(bx, KX0, KX1, KY0 + 0.004, KY1, z0 + 0.0005, z0 + KH - 0.0005, **bev(lod, 0.003))
    parts.append(bx)
    foot(lod, "parts drawers", KX0, KX1, KY0 - 0.012, KY1, ZT, ZT + 2 * KH)
    dr = P("cassette_drawers", "drawer_y")
    if lod > 0:
        for b in range(2 if lod == 1 else 1):
            za, zb = (ZT + b * KH, ZT + (b + 1) * KH) if lod == 1 else (ZT, ZT + 2 * KH)
            g.box(dr, KX0 + 0.006, KX1 - 0.006, KY0 - 0.002, KY0 + 0.004, za + 0.006, zb - 0.006)
        return parts + [dr]
    w, h = (KX1 - KX0 - 0.01) / 4, (KH - 0.01) / 3
    tb = P("cassette_tabs", "drawer_y")
    for b in range(2):
        for i in range(4):
            for j in range(3):
                xa = KX0 + 0.005 + w * i
                za = ZT + b * KH + 0.005 + h * j
                g.box(dr, xa + 0.002, xa + w - 0.002, KY0 - 0.002, KY0 + 0.004, za + 0.002, za + h - 0.002)
                g.box(tb, xa + w / 2 - 0.011, xa + w / 2 + 0.011, KY0 - 0.010, KY0 - 0.002, za + h / 2 - 0.004,
                      za + h / 2 + 0.0015)
    parts += [dr, tb]
    return parts


def build_tray(spec):
    """Open parts tray of 4 x 3 cells: resistors, capacitors, transistors, ICs, LEDs."""
    lod = spec["lod"]
    if lod == 2:
        return []
    zb, zh = ZT, ZT + 0.035
    tr = P("tray", "tray")
    t = 0.003
    g.box(tr, TRX0, TRX1, TRY0, TRY1, zb, zb + 0.004, **bev(lod, 0.0015))
    for i in range(5) if lod == 0 else (0, 4):
        x = TRX0 + (TRX1 - TRX0) * i / 4
        xa = min(max(x - t / 2, TRX0), TRX1 - t)
        inner = 0 < i < 4
        g.box(tr, xa, xa + t, TRY0 + (t if inner else 0), TRY1 - (t if inner else 0), zb, zh - (0.004 if inner else 0))
    for j in range(4) if lod == 0 else (0, 3):
        y = TRY0 + (TRY1 - TRY0) * j / 3
        ya = min(max(y - t / 2, TRY0), TRY1 - t)
        inner = 0 < j < 3
        g.box(tr, TRX0 + t, TRX1 - t, ya, ya + t, zb, zh - (0.004 if inner else 0))
    parts = [tr]
    foot(lod, "parts tray", TRX0, TRX1, TRY0, TRY1, ZT, zh)
    if lod > 0:
        return parts
    cw, ch = (TRX1 - TRX0) / 4, (TRY1 - TRY0) / 3
    kinds = ["resistor", "cap_blue", "ic", "transistor", "cap_red_small", "led", "resistor", "ic", "cap_blue", "transistor",
             "resistor", "led"]
    pt = P("tray_parts", "resistor")
    z0 = zb + 0.004
    for c, kind in enumerate(kinds):
        i, j = c % 4, c // 4
        xc, yc = TRX0 + cw * (i + 0.5), TRY0 + ch * (j + 0.5)
        for k in range(1):
            a = 1.9 * k + c
            x, y = xc + 0.020 * math.cos(a), yc + 0.014 * math.sin(a * 1.3)
            if kind == "resistor":
                use(pt, "resistor")
                g.cyl(pt, (x, y, z0 + 0.0013), "x", 0.0013, 0.0068, 5)
            elif kind in ("cap_blue", "cap_red_small"):
                use(pt, kind)
                lathe(pt, [(0.0030, 0.0), (0.0030, 0.0095), (0.0, 0.0100)], 7, (x, y, z0),
                      (0, 0, 1))
            elif kind == "ic":
                use(pt, "black")
                g.box(pt, x - 0.0095, x + 0.0095, y - 0.0033, y + 0.0033, z0 + 0.0006, z0 + 0.0040)
                use(pt, "steel")
                for s in (-1, 1):
                    g.box(pt, x - 0.0085, x + 0.0085, y + s * 0.0033, y + s * 0.0045, z0, z0 + 0.0022)
            elif kind == "transistor":
                use(pt, "black")
                poly = [(x + 0.0024 * math.cos(math.pi * q / 6), y + 0.0024 * math.sin(math.pi * q / 6)) for q in range(7)]
                g.prism(pt, poly, (0, 1), z0, z0 + 0.0048)
            else:
                use(pt, "led_spare")
                lathe(pt, [(0.0028, 0.0), (0.0028, 0.0012), (0.0025, 0.0050), (0.0, 0.0076)],
                      7, (x, y, z0), (0, 0, 1))
    parts.append(pt)
    return parts


def build_rosin(spec):
    """Rosin jar without a lid: rolled edge, rosin with a dent from the tip; the lid lies next to it, inside up."""
    lod = spec["lod"]
    if lod == 2:
        return []
    n = 12 if lod == 0 else 8
    x, y = TIN
    tn = P("rosin_tin", "tin")
    lathe(tn, [(0.0, 0.0), (0.0305, 0.0), (0.031, 0.0015), (0.031, 0.0170), (0.0318, 0.0180), (0.0310, 0.0190),
               (0.0296, 0.0182), (0.0296, 0.0120)], n, (x, y, ZT), (0, 0, 1))
    parts = [tn]
    rs = P("rosin", "rosin")
    lathe(rs, [(0.0296, 0.0120), (0.020, 0.0124), (0.010, 0.0108), (0.0, 0.0098)], n, (x, y, ZT), (0, 0, 1))
    parts.append(rs)
    lx, ly = LID
    if lod == 0:
        ld = P("rosin_lid", "tin")
        lathe(ld, [(0.0, 0.0), (0.0330, 0.0), (0.0330, 0.0078), (0.0316, 0.0082), (0.0316, 0.0012), (0.0, 0.0012)], n,
              (lx, ly, ZT), (0, 0, 1))
        parts.append(ld)
    foot(lod, "rosin jar", x - 0.032, x + 0.032, y - 0.032, y + 0.032, ZT, ZT + 0.019)
    foot(lod, "jar lid", lx - 0.033, lx + 0.033, ly - 0.033, ly + 0.033, ZT, ZT + 0.008)
    return parts


def build_lod(spec):
    parts = build_bench(spec) + build_outlets(spec) + build_ground(spec)
    parts += build_psu(spec) + build_spools(spec)
    parts += build_mat(spec) + build_lamp(spec) + build_nvg(spec) + build_eop(spec) + build_pcb(spec)
    parts += build_leads(spec) + build_probe(spec)
    parts += build_cassettes(spec) + build_tray(spec) + build_rosin(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        check_layout()
    return parts


def check_layout():
    """Footprints of things on the bench, mat and shelf: vanilla (kv.corners), modules in the slots
    (MOD_BOX) and own (FOOT) - overlaps of footprints (more than 2 mm on all axes) and a vanilla item's
    bottom above its support go to the log. A footprint is a box: "M73 and the station outlet" is not an
    overlap (by the M73 MLOD vertices: behind the station block there are only a cord and a plug no
    higher than 14 mm above the sheet, the outlet on the panel starts at 47 mm)."""
    boxes = []
    for d in DECOR:
        q = kv.corners(d[5], d[1], d[2], d[3])
        boxes.append(("decor: " + str(d[5]).split("\\")[-1], tuple(min(c[i] for c in q) for i in range(3)),
                      tuple(max(c[i] for c in q) for i in range(3))))
    for (o, _n), s, (lo, hi) in zip(MOD_OBJ, SLOTS, MOD_BOX):
        boxes.append(("module: " + o, tuple(s[i] + lo[i] for i in range(3)), tuple(s[i] + hi[i] for i in range(3))))
    boxes += FOOT
    bad = 0
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            ov = [min(a[2][k], b[2][k]) - max(a[1][k], b[1][k]) for k in range(3)]
            if all(o > 0.002 for o in ov):
                print("layout: %s and %s overlap (%.3f x %.3f x %.3f)" % (a[0], b[0], ov[0], ov[1], ov[2]))
                bad += 1
    for name, lo, hi in boxes[:len(DECOR)]:
        print("layout: %-16s x %.3f..%.3f  y %.3f..%.3f  z %.4f..%.4f" % (name[7:], lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
    print("layout: footprint overlaps: %d" % bad)


def collision():
    table = kx.box_pts(X0 - 0.01, X1 + 0.01, Y0 - 0.01, Y1 + 0.005, 0.0, ZT)
    # a component thinner than 0.5 m does not work: the superstructure goes down into the bench and
    # forward over the tabletop - the parts overlap, each convex
    top = kx.box_pts(X0, X1, Y1 - 0.51, Y1, 0.40, ZP + 0.22)
    metal = kx.PEN + r"\metalplate.rvmat"
    comps = [(table, metal), (top, metal)]
    memory = {
        "invView": [(-0.2, -2.6, 1.3)],
        "ce_center": [(0.0, 0.0, 0.80)],
        "ce_radius": [(1.1, 0.0, 0.80)],
    }
    for i, s in enumerate(SLOTS):
        memory["module_%d" % (i + 1)] = [s]
    # needle axes: from the scale toward the person - a positive angle moves the needle clockwise (from
    # zero to the scale end)
    for k, (cx, cz) in zip(("v", "a"), METER_C):
        px, pz = needle_pivot(cx, cz)
        memory[SEL_NEEDLE[k] + "_axis"] = [(px, NEEDLE_Y, pz), (px, NEEDLE_Y - 0.01, pz)]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (min(lo[0], X0 - 0.01), max(hi[0], X1 + 0.01), min(lo[1], Y0 - 0.01), Y1 + 0.005, 0.0, max(hi[2], ZP + 0.22))
    return comps, 140.0, memory, bbox


# preview of "work": the needles at mid-swing (in game OZL_WorkFx wobble drives them). The kit shifts
# the parts of the look (states move), but a needle needs rotation about its axis - a wrapper over
# krender.place_look, only here
_place_look = krender.place_look


def _place_look_posed(parts, kind_table, origin, remap=None, **kw):
    obs = _place_look(parts, kind_table, origin, remap=remap, **kw)
    if remap:
        for p, ob in zip(parts, obs):
            pose = NEEDLE_POSE.get(p.group)
            if pose:
                pv = Vector(pose[0])
                # rotation about Blender +Y by +angle is clockwise when looking at the scale from the front
                ob.matrix_world = Matrix.Translation(pv) @ Matrix.Rotation(math.radians(pose[1]), 4, "Y") @ \
                    Matrix.Translation(-pv)
    return obs


krender.place_look = _place_look_posed

# the first ones are for the --look preview: the work place on the mat (and in "work"), the whole bench
# with the modules (and empty), overview, the shelf with the supply, the right edge with the station,
# the magnifier; the rest are for --geo
SHOTS = [
    ("mat", (-0.22, -0.88, 1.30), (-0.30, -0.10, 0.84), 34),
    ("bench", (-0.05, -1.62, 1.72), (-0.02, 0.05, 1.08), 30),
    ("front", (-1.0, -2.4, 1.75), (0.0, 0.0, 1.0), 32),
    ("psu", (-0.40, -0.62, 1.62), (-0.48, 0.15, 1.46), 34),
    ("right", (0.78, -0.82, 1.36), (0.25, 0.06, 0.86), 34),
    ("lamp", (-1.00, -0.80, 1.42), (-0.52, -0.02, 1.02), 32),
    ("back", (1.4, 1.9, 1.6), (0.0, 0.0, 0.9), 32),
    ("top", (0.0, -0.30, 3.0), (0.0, -0.02, 0.80), 34),
]

M.look_shots = (6, 2)
M.run(build_lod, collision, SHOTS, row_step=1.9, row_shot=((1.9, -6.2, 2.0), (1.9, 0, 0.80)))
