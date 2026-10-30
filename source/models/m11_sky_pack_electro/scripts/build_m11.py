"""M11 - field assembly table: Electronics Packer of the Clear Sky faction (OZL_Sky_Pack_Electro).
Packer: cargo 10x10, three module slots (module_1..3) and module proxies in the same places. Each module of
the "Electronics" line has its own slot and its own place on the board where it is used: slot 1 - oscilloscope
M72 at the back left, by the disassembled night-vision goggles (the probe goes to the goggles' board); slot 2 -
soldering station M73, powered by a wire with crocodile clips from the junction box; slot 3 - programmer M74
in front of the junction box. An empty slot is a place on the board; at slot 2 a wire with clamps sticks out
of the box.

    blender --background --python build_m11.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: system Python make_decals.py (multimeter LCD - "off" and "work" frames, multimeter
face, voltmeter scale, lightning sign, tag).

Look: the "dayz" look (matte, dirtier, coloured AO). Small things are vanilla DayZ items placed as proxies
(kvanilla): two pliers and a screwdriver on the back panel, a screwdriver on the board, a DayZ flashlight
with a 9 V battery, a radio and an electrician's kit and insulating tape on the shelf. Custom parts are
detailed: B1 table with chamfers, boards of different tones with screws; battery with a rim, lid, plugs,
handles and crocodile clips on the terminals; junction box with a voltmeter, toggle, LED, cable glands and
screws; inspection lamp - rubber ribbed handle, socket, bulb, cage and hook; multimeter with a rounded
case, knob, sockets, plugs and probes (handle, stop, needle) on the terminals of a 3336 battery;
disassembled NVG: body with eyepieces and eyecups, detached objective with a knurled ring, removed image
tube, converter board with transformer and capacitors, cover, screws; vise - cast, serrated jaws, tommy bar
and clamp screw with balls; smoke extractor - 80 mm fan on a bracket with a filter and a grille; wires -
smooth curves, crocodile clips with jaws, spring and caps.

Table: B1 base (kfurn.workbench, worktop="board") of the same size as M05 - an electronics assembler's
bench (IZhSK.296375.001, "Signal" catalogue, version -03), top 1600 x 710 mm, height 785-810 mm. Here
1.60 x 0.72 m, work surface at 0.78, cabinet 0.42 wide with four drawers, back panel and shelf at 1.40,
shelf depth 0.30. Field variant (an electronics bench: tool board on nails, parts cassette on top,
multimeter and probes, wires across the table): the steel bench is repainted Clear Sky light blue over grey
factory enamel, topped with four planed 40 mm boards; no power strip or lamp - there is no mains in the
field, everything runs from the car battery under the table.

Props and sizes:
- 6ST-55 battery under the table - 242 x 175 x 190 mm (GOST 959, the 55 Ah group size of starter
  batteries), six cell plugs, terminals at the corners of the long side with crocodile clips; wires go up
  through a bushing in the boards to a home-made junction box;
- junction box - cast aluminium 130 x 85 x 75 mm; on the front a 50 mm voltmeter with an 8-16 V scale
  (automotive, stretched scale), toggle, LED; cable glands on the sides and back;
- 12 V inspection lamp (PL-12 / portable car lamp: rubber handle 35 mm dia., A12-21 bulb in a wire cage
  ~75 mm dia., hook) hangs on a nail on the back panel;
- smoke extractor: 80 x 80 x 25 mm 12 V fan (PC type, 1990s) on a bent bracket, foam filter at the back,
  wire grille in front - stands right of slot 2 and draws the soldering smoke;
- clamp vise with 63 mm jaws at the front left corner of the board;
- disassembled NVG (binocular night-vision goggles, body ~140 x 75 x 62): detached objective
  62 dia. x 76, image tube 45 dia. x 50 (generation 1+), converter board ~90 x 55;
- flat army flashlight on a 3336 battery (battery 62 x 22 x 67 mm, body ~70 x 35 x 110 mm) with the back
  cover removed; the battery lies beside it, multimeter probes on its terminals;
- DT-830 type multimeter (1990s; 126 x 70 x 24 mm) with LCD, sockets and probes;
- parts cassette with 12 small drawers on the shelf (two pulled out), spools of solder and wire, tarpaulin
  hanging from the left end of the shelf, boxes with parts (on the board and on the floor), wires with
  crocodile clips, rosin jar, coil of wire.

Work look (class OZL_Work):
- ozl_lamp - the inspection lamp bulb and the junction box LED: lit in "work" (atlas _on);
- ozl_screen - multimeter LCD (section lcd, own texture): "off" is blank, "work" is frames _lcd_fNN
  (battery voltage 4.46-4.49 flickers in the last digit; frames);
- ozl_needle - voltmeter needle, bone on source ozl_needle: at rest on the stop (toggle off), in "work" it
  trembles around 12.6 V (wobble, mid 0.575 of the scale). Axis from the dial toward the face, phase 1 is
  100 degrees clockwise (as in M01, M08, M14; the angle sign is not verified in game);
- ozl_toggle - toggle lever, bone on source ozl_toggle: "work" is flipped up (pose);
- ozl_work - fan rotor, bone on source ozl_work: model.cfg loop (sourceAddress loop, maxValue 1/3) - 3
  turns per pass, pass 2 s (animPeriod in the mod config) - 1.5 rev/s: at 30 frames the 7 blades (51 degrees
  apart) advance 18 degrees per frame, so the rotation does not appear to run backwards.
In the "work" preview the needle and toggle are rotated into pose: the kit's move shift only translates a
part, so this file wraps krender.place_look / place itself (as in M01).

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
import kwood  # noqa: E402
import m11_geo as G  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
X0, X1, Y0, Y1 = -0.80, 0.80, -0.36, 0.36                    # table
ZT, ZP, SHD, CAB_W = 0.78, 1.40, 0.30, 0.42                  # tabletop, shelf top, shelf depth, cabinet width
ZU = ZT - 0.04                                               # underside of the boards
YP = Y1 - 0.02                                               # face of the back panel
YS = Y1 - SHD                                                # front of the shelf
ZS = ZP - 0.02                                               # underside of the shelf
CX0 = X1 - CAB_W                                             # left side of the cabinet
# module slots (proxy points = module model origin, no rotation: modules face the person):
# 1 - oscilloscope M72 (0.19 x 0.31 with probes) at the back left by the NVG, 2 - soldering station M73
# (0.21 x 0.26), 3 - programmer M74 (0.21 x 0.21) in front of the junction box
S1, S2, S3 = (-0.43, 0.175, ZT), (0.27, 0.13, ZT), (-0.155, 0.075, ZT)
MODS = [S1, S2, S3]
MOD_OBJ = [("m72_oscilloscope", "ozr_oscilloscope"), ("m73_solder_station", "ozr_solder_station"),
           ("m74_programmer", "ozr_programmer")]
# 6ST-55 battery on the floor under the table: 242 x 175 x 190
BAX0, BAX1, BAY0, BAY1, BAZ = -0.421, -0.179, -0.04, 0.135, 0.19
TERM = ((-0.395, 0.105), (-0.205, 0.105))                    # terminals: plus, minus
HOLE = (-0.275, 0.292)                                       # bushing in the boards for the wires
# junction box: body, voltmeter (centre on the front), toggle, LED
JX0, JX1, JY0, JY1, JZ1 = -0.22, -0.09, 0.20, 0.285, ZT + 0.075
GAUGE = Vector((JX0 + 0.040, JY0, ZT + 0.040))
GAUGE_R = 0.021
NEEDLE_REST, NEEDLE_SWEEP, NEEDLE_MID = -50.0, 100.0, 0.575  # from vertical; sweep; 12.6 V on the 8-16 scale
TOG = Vector((JX1 - 0.028, JY0, ZT + 0.050))                # toggle: bushing on the front
TOG_PIVOT = TOG + Vector((0.0, -0.009, 0.0))
TOG_REST, TOG_SWING = -25.0, 50.0                            # lever 25 degrees down, sweep 50
LED_P = Vector((JX1 - 0.028, JY0, ZT + 0.024))
GLAND_L = Vector((JX0, JY0 + 0.045, ZT + 0.030))             # inlet from the battery
GLAND_R = [Vector((JX1, JY0 + 0.025, ZT + 0.030)), Vector((JX1, JY0 + 0.062, ZT + 0.030))]  # station, fan
GLAND_B = Vector(((JX0 + JX1) / 2, JY1, ZT + 0.040))         # to the inspection lamp
# inspection lamp on a nail on the back panel
LX, LY = 0.11, YP - 0.045
NAIL = (LX, YP, 1.335)
LC = Vector((LX, LY, 1.235))                                 # centre of the cage
LR, LHALF = 0.038, 0.06                                      # cage radius, half-height
# multimeter face up, display toward the back panel
MMX0, MMX1, MMY0, MMY1, MMZ = 0.0, 0.07, 0.037, 0.163, ZT + 0.023
LCD = (0.012, 0.058, 0.126, 0.149)                           # x0, x1, y0, y1 of the LCD window
JACKS = ((0.015, "black"), (0.035, "cap_red"), (0.055, "black"))
JACK_Y = MMY0 + 0.015
# 3336 battery lying (terminals toward the multimeter), flat flashlight standing, its back cover
B3 = (0.035, -0.10)
FF = (-0.16, -0.10)
FF_COVER = (-0.25, -0.12)
# probes: tip on the battery terminal, handle direction from the tip
PROBES = [(Vector((0.020, -0.059, ZT + 0.0135)), Vector((-1.0, 0.04, -0.08)), "probe_black", "wire_black", 0),
          (Vector((0.050, -0.059, ZT + 0.0135)), Vector((1.0, -0.10, -0.08)), "probe_red", "wire_red", 1)]
# vise at the front left corner
VX = -0.62
# NVG: body, detached objective, image tube, converter board, cover
NB = (-0.665, 0.17)
NV_OBJ = Vector((-0.745, 0.03, ZT + 0.031))
NV_TUBE = Vector((-0.762, -0.06, ZT + 0.0225))
NV_PCB = (-0.60, -0.07, 0.09, 0.055)
NV_COVER = (-0.70, -0.15, 0.12, 0.07)
ZPCB = ZT + 0.0016
# smoke-extractor fan: centre, axis (toward the soldering spot in front of the station)
FAN_C = Vector((0.535, 0.075, ZT + 0.051))
FAN_D = Vector((-0.85, -0.53, 0.0)).normalized()
FAN_FR = g.Frame(FAN_C, (-FAN_D.y, FAN_D.x, 0.0), (0.0, 0.0, 1.0), FAN_D)
FAN_TURNS = 3                                                # turns per loop pass
# cassette on the shelf, spools, boxes
KX0, KX1, KY0, KY1, KH = -0.60, -0.34, YS + 0.05, Y1 - 0.03, 0.17
SPOOL_X = -0.24
BOX = (0.46, 0.70, -0.31, -0.11, 0.10)                       # box on the board: x0 x1 y0 y1 h
FBOX = (-0.06, 0.26, -0.12, 0.18, 0.21)                      # box on the floor
ROSIN = (0.43, -0.05)
COIL = (0.66, 0.22)
# tarpaulin: hangs from the left end of the shelf
TP_X, TP_Z1 = X0 - 0.022, 0.96
# vanilla tools on the back panel: (key, x, z of the middle, angle)
HUNG = [("pliers", -0.69, 1.205, 90.0), ("pliers", -0.61, 1.195, 90.0), ("screwdriver", -0.53, 1.215, -90.0)]

LOD_SPECS = [
    dict(lod=0, bev=1, sides=12),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "wb": ("enamel", 0.6), "wb_front": ("enamel_front", 0.9), "wb_panel": ("enamel_panel", 0.6),
    "wb_top": ("plank_a", 0.8), "plank_a": ("plank_a", 0.8), "plank_b": ("plank_b", 0.8), "plank_c": ("plank_c", 0.8),
    "steel": ("steel", 1.0), "black": ("black", 1.0), "rubber": ("rubber", 0.6), "screw": ("screw", 2.0),
    "battery": ("battery", 1.0), "battery_lid": ("battery_lid", 1.2), "lead": ("lead", 1.5), "batt_cap": ("batt_cap", 1.6),
    "cap_red": ("cap_red", 1.4), "boot_red": ("boot_red", 1.6), "boot_black": ("boot_black", 1.6),
    "clip_jaw": ("clip_jaw", 2.0), "wire_red": ("wire_red", 1.0), "wire_black": ("wire_black", 1.0),
    "cable_grey": ("cable_grey", 1.0),
    "jbox": ("jbox", 1.8), "jbox_lid": ("jbox_lid", 2.0), "volt_face": ("volt_face", 6.0), "needle": ("needle", 3.0),
    "led": ("led", 3.0), "chrome": ("chrome", 1.6), "gland": ("gland", 1.6),
    "bulb": ("bulb", 3.0), "cage": ("cage", 1.2), "lamp_grip": ("lamp_grip", 1.4),
    "mm": ("mm_case", 2.0), "mm_face": ("mm_face", 4.0), "probe_red": ("probe_red", 2.0),
    "probe_black": ("probe_black", 2.0),
    "olive": ("olive", 1.6), "lens": ("lens_dark", 2.0), "tube_face": ("tube_face", 3.0), "cathode": ("cathode", 3.0),
    "pcb": ("pcb", 5.0), "copper": ("copper", 1.5), "ferrite": ("ferrite", 2.0), "cap_blue": ("cap_blue", 2.0),
    "resistor": ("resistor", 2.0),
    "vise": ("vise", 1.4), "vise_jaw": ("vise_jaw", 2.0),
    "fan": ("fan", 1.6), "fan_label": ("fan_label", 3.0), "zinc": ("zinc", 1.4), "foam": ("foam", 1.2),
    "alu": ("alu", 1.4), "reflector": ("reflector", 2.0), "glass": ("glass", 2.0),
    "batt3336": ("batt3336", 2.0), "batt_band": ("batt_band", 2.0), "brass": ("brass", 2.0),
    "cassette": ("cassette", 1.2), "drawer": ("drawer", 1.6), "parts_mix": ("parts_mix", 2.0),
    "solder": ("solder", 1.6), "spool": ("spool", 1.4),
    "card": ("card", 0.8), "tarp": ("tarp", 0.5), "beige": ("beige", 1.2), "rosin": ("rosin", 2.0),
}

# =============================================================================
# Materials
# =============================================================================


def decal(name, ax, sign, axes, center, size, face, eps=0.0015):
    return (os.path.join(WORK, name), ax, sign, axes, center, size, (face - eps, face + eps))


# multimeter face: image top toward the back panel (+y)
FACE = [decal("decal_face.png", "z", 1, ("x", "y"), ((MMX0 + MMX1) / 2, (MMY0 + MMY1) / 2 - 0.004),
              (MMX1 - MMX0 - 0.008, MMY1 - MMY0 - 0.008), MMZ)]
# voltmeter scale on the junction box front, lightning sign on the lid
VOLT = [decal("decal_volt.png", "y", -1, ("x", "z"), (GAUGE.x, GAUGE.z), (2 * GAUGE_R, 2 * GAUGE_R), JY0 - 0.0035,
              eps=0.0012)]
BOLT = [decal("decal_bolt.png", "z", 1, ("x", "y"), (JX1 - 0.032, (JY0 + JY1) / 2 + 0.006), (0.036, 0.036), JZ1)]
# blank inventory tag on the top drawer of the cabinet
TAG = [decal("decal_tag.png", "y", -1, ("x", "z"), (X1 - CAB_W / 2, ZU - 0.025), (0.07, 0.02), Y0 + 0.02 - 0.018 - 0.002)]

KINDS = kmats.std_kinds(floor_z=0.0)
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# light-blue Clear Sky enamel over the grey factory paint of the table: chips down to grey and rust, swamp
# mud on the legs and plinth (grime near the floor), back panel and shelf cleaner
BLUE = dict(color=kmats.lin((144, 184, 206)), under=kmats.lin((128, 132, 130)), seed=2.6, gloss=0.40, spec=0.30,
            chip=(0.60, 0.66), rust=(0.68, 0.76), rust_low=1.0, floor_z=0.0, dust=0.32, grime=1.0)
# boards: planed pine, clean (a Clear Sky workplace is tidy); three tones - boards from different batches
WOOD = dict(along="x", floor_z=ZT, dust=0.14, grime=0.16, rings=0.75, knots=0.8)
KINDS.update({
    "enamel": ("paint", BLUE),
    "enamel_front": ("paint", dict(BLUE, seed=3.3, chip=(0.62, 0.68), grime=0.6, decal_items=TAG)),
    "enamel_panel": ("paint", dict(BLUE, color=kmats.lin((160, 198, 216)), seed=3.9, chip=(0.66, 0.72), rust_low=0.0,
                                   floor_z=ZT, grime=0.25)),
    "plank_a": (kwood.build_wood, dict(WOOD, color=kmats.lin((170, 128, 84)), seed=1.7)),
    "plank_b": (kwood.build_wood, dict(WOOD, color=kmats.lin((154, 114, 74)), seed=2.9)),
    "plank_c": (kwood.build_wood, dict(WOOD, color=kmats.lin((178, 140, 94)), seed=4.3, knots=1.0)),
    "screw": ("steel", dict(seed=4.9, tone=0.22, along="z", gloss=0.4, spec=0.5, dust=0.2, grime=0.5)),
    # battery: black polypropylene, dark grey lid, black plugs, lead terminals
    "battery": ("plastic", dict(color=kmats.lin((30, 30, 32)), gloss=0.35, spec=0.25, dust=0.5, grime=0.7,
                                scuff=(0.70, 0.78))),
    "battery_lid": ("plastic", dict(color=kmats.lin((52, 54, 56)), gloss=0.3, spec=0.2, dust=0.6, grime=0.5,
                                    scuff=(0.66, 0.74))),
    "batt_cap": ("plastic", dict(color=kmats.lin((26, 26, 26)), gloss=0.3, spec=0.2, dust=0.4)),
    "lead": ("paint", dict(color=kmats.lin((96, 98, 100)), under=kmats.lin((170, 172, 170)), seed=6.1, gloss=0.25,
                           spec=0.3, chip=(0.70, 0.75), rust=(0.99, 1.0), rust_low=0.0, dust=0.3, grime=0.4, yellow=0.15)),
    "boot_red": ("plastic", dict(color=kmats.lin((170, 34, 28)), gloss=0.45, spec=0.3, dust=0.2, grime=0.3)),
    "boot_black": ("plastic", dict(color=kmats.lin((24, 24, 26)), gloss=0.45, spec=0.3, dust=0.2, grime=0.3)),
    "clip_jaw": ("steel", dict(seed=5.3, tone=0.36, along="x", gloss=0.5, spec=0.6, dust=0.1, grime=0.3)),
    "wire_red": ("plastic", dict(color=kmats.lin((168, 40, 30)), gloss=0.45, spec=0.3, dust=0.2)),
    "wire_black": ("plastic", dict(color=kmats.lin((26, 26, 28)), gloss=0.45, spec=0.3, dust=0.2)),
    "cable_grey": ("plastic", dict(color=kmats.lin((70, 72, 74)), gloss=0.3, spec=0.2, dust=0.3, grime=0.3)),
    # junction box: cast aluminium in grey hammer enamel, chipped down to metal
    "jbox": ("paint", dict(color=kmats.lin((118, 124, 122)), under=kmats.lin((168, 170, 168)), seed=6.4, gloss=0.35,
                           spec=0.3, chip=(0.62, 0.68), rust=(0.99, 1.0), rust_low=0.0, floor_z=ZT, dust=0.25, grime=0.3)),
    "jbox_lid": ("paint", dict(color=kmats.lin((118, 124, 122)), under=kmats.lin((168, 170, 168)), seed=6.8, gloss=0.35,
                               spec=0.3, chip=(0.62, 0.68), rust=(0.99, 1.0), rust_low=0.0, floor_z=ZT, dust=0.3,
                               grime=0.2, decal_items=BOLT)),
    "volt_face": ("paint", dict(CLEAN, color=kmats.lin((226, 222, 206)), gloss=0.5, spec=0.4, decal_items=VOLT)),
    "needle": ("plastic", dict(color=kmats.lin((20, 20, 20)), gloss=0.4, spec=0.3, dust=0.0, grime=0.0)),
    "led": ("flat", dict(color=kmats.lin((120, 24, 20)), gloss=0.85, spec=0.8)),
    "led_on": ("flat", dict(color=kmats.lin((255, 60, 40)), gloss=0.85, spec=0.8)),
    "chrome": ("steel", dict(seed=7.1, tone=0.42, along="z", gloss=0.75, spec=0.85, floor_z=ZT, dust=0.1, grime=0.2)),
    "gland": ("plastic", dict(color=kmats.lin((30, 30, 32)), gloss=0.35, spec=0.25, dust=0.3, grime=0.3)),
    # inspection lamp bulb: "off" is frosted glass, "work" is a warm glow (atlas _on)
    "bulb": ("flat", dict(color=kmats.lin((196, 192, 176)), gloss=0.8, spec=0.7)),
    "bulb_on": ("flat", dict(color=kmats.lin((255, 236, 176)), gloss=0.8, spec=0.7)),
    "cage": ("steel", dict(seed=7.4, tone=0.30, along="z", gloss=0.45, spec=0.5, dust=0.2, grime=0.3)),
    "lamp_grip": ("plastic", dict(color=kmats.lin((28, 28, 28)), gloss=0.15, spec=0.08, dust=0.3, grime=0.4,
                                  scuff=(0.8, 0.9))),
    # multimeter: yellow case, dark face with the selector scale, probes
    "mm_case": ("plastic", dict(color=kmats.lin((214, 168, 36)), gloss=0.35, spec=0.25, dust=0.25, grime=0.3,
                                scuff=(0.64, 0.72))),
    "mm_face": ("paint", dict(CLEAN, color=kmats.lin((36, 36, 38)), gloss=0.35, spec=0.25, decal_items=FACE)),
    "probe_red": ("plastic", dict(color=kmats.lin((160, 30, 24)), gloss=0.45, spec=0.3, dust=0.2, grime=0.3)),
    "probe_black": ("plastic", dict(color=kmats.lin((28, 28, 30)), gloss=0.45, spec=0.3, dust=0.2, grime=0.3)),
    # NVG: olive enamel over aluminium, worn on the edges; dark glass, green image tube screen
    "olive": ("paint", dict(color=kmats.lin((70, 74, 54)), under=kmats.lin((120, 120, 116)), seed=7.1, gloss=0.3,
                            spec=0.25, chip=(0.60, 0.66), rust=(0.99, 1.0), rust_low=0.0, floor_z=ZT, dust=0.2, grime=0.3)),
    "lens_dark": ("flat", dict(color=kmats.lin((40, 50, 62)), gloss=0.95, spec=0.9)),
    "tube_face": ("flat", dict(color=kmats.lin((60, 104, 76)), gloss=0.95, spec=0.85)),
    "cathode": ("flat", dict(color=kmats.lin((70, 56, 84)), gloss=0.95, spec=0.85)),
    "pcb": ("paint", dict(CLEAN, color=kmats.lin((40, 94, 56)), gloss=0.5, spec=0.4)),
    "copper": ("paint", dict(CLEAN, color=kmats.lin((150, 92, 52)), under=kmats.lin((90, 50, 30)), seed=6.6, gloss=0.5,
                             spec=0.5)),
    "ferrite": ("plastic", dict(color=kmats.lin((44, 44, 46)), gloss=0.2, spec=0.15, dust=0.1)),
    "cap_blue": ("plastic", dict(color=kmats.lin((40, 70, 140)), gloss=0.5, spec=0.35, dust=0.1)),
    "resistor": ("plastic", dict(color=kmats.lin((186, 160, 120)), gloss=0.3, spec=0.2, dust=0.1)),
    # vise: cast iron in grey-blue paint, jaws of dark serrated steel
    "vise": ("paint", dict(color=kmats.lin((62, 78, 84)), under=kmats.lin((150, 150, 150)), seed=7.7, gloss=0.4,
                           spec=0.35, chip=(0.56, 0.62), rust=(0.66, 0.72), rust_low=0.0, floor_z=ZT, dust=0.2,
                           grime=0.4)),
    "vise_jaw": ("steel", dict(seed=7.9, tone=0.18, along="x", gloss=0.35, spec=0.45, floor_z=ZT, dust=0.05,
                               grime=0.4)),
    # fan: black plastic, beige sticker on the hub (no lettering), galvanized bracket,
    # grey foam filter
    "fan": ("plastic", dict(color=kmats.lin((26, 26, 28)), gloss=0.35, spec=0.25, dust=0.5, grime=0.3)),
    "fan_label": ("plastic", dict(color=kmats.lin((196, 184, 150)), gloss=0.3, spec=0.2, dust=0.3)),
    "zinc": ("steel", dict(seed=8.4, tone=0.40, along="x", gloss=0.4, spec=0.45, floor_z=ZT, dust=0.25, grime=0.3)),
    "foam": ("plastic", dict(color=kmats.lin((48, 48, 50)), gloss=0.05, spec=0.03, mottle=0.2, dust=0.4, grime=0.4,
                             scuff=(0.9, 1.0))),
    "alu": ("steel", dict(seed=8.1, tone=0.30, along="z", floor_z=ZT, dust=0.2, grime=0.3)),
    "reflector": ("steel", dict(seed=9.4, tone=0.50, along="z", gloss=0.85, spec=0.9, dust=0.05, grime=0.05)),
    "glass": ("flat", dict(color=kmats.lin((150, 156, 150)), gloss=0.9, spec=0.8)),
    "batt3336": ("paint", dict(CLEAN, color=kmats.lin((176, 52, 40)), gloss=0.45, spec=0.35, dust=0.1)),
    "batt_band": ("paint", dict(CLEAN, color=kmats.lin((40, 70, 140)), gloss=0.45, spec=0.35, dust=0.1)),
    "brass": ("paint", dict(CLEAN, color=kmats.lin((170, 140, 74)), gloss=0.55, spec=0.55, dust=0.1, grime=0.2)),
    "cassette": ("plastic", dict(color=kmats.lin((70, 76, 84)), gloss=0.40, spec=0.30, dust=0.4)),
    "drawer": ("plastic", dict(color=kmats.lin((150, 170, 186)), gloss=0.55, spec=0.4, mottle=0.12, dust=0.25)),
    "parts_mix": ("plastic", dict(color=kmats.lin((120, 98, 70)), gloss=0.3, spec=0.2, mottle=0.4, dust=0.1)),
    "solder": ("steel", dict(seed=9.9, tone=0.34, along="z", gloss=0.5, spec=0.55, dust=0.1, grime=0.1)),
    "spool": ("plastic", dict(color=kmats.lin((36, 36, 38)), gloss=0.35, spec=0.25, dust=0.4)),
    "card": ("plastic", dict(color=kmats.lin((150, 118, 80)), gloss=0.08, spec=0.05, mottle=0.18, dust=0.4, grime=0.6,
                             scuff=(0.60, 0.70))),
    # tarpaulin: unbleached grey-brown (not a faction colour)
    "tarp": ("plastic", dict(color=kmats.lin((122, 112, 88)), gloss=0.06, spec=0.04, mottle=0.22, dust=0.35, grime=0.5,
                             scuff=(0.60, 0.70))),
    "beige": ("plastic", dict(color=kmats.lin((204, 194, 166)), gloss=0.35, spec=0.25, dust=0.2)),
    "rosin": ("flat", dict(color=kmats.lin((150, 86, 24)), gloss=0.9, spec=0.6)),
})

OBJ, NAME = "m11_sky_pack_electro", "ozr_sky_pack_electro"
SEL_LAMP, SEL_SCREEN = "ozl_lamp", "ozl_screen"
SEL_WORK, SEL_NEEDLE, SEL_TOGGLE = "ozl_work", "ozl_needle", "ozl_toggle"
# "work" preview: bulb and LED lit, first frame on the LCD (move is only a marker for the needle and
# toggle pose in _posed, the shift itself is zero)
ON = dict(remap={"bulb": "bulb_on", "led": "led_on"}, emissive=(1.0, 1.0, 1.0, 1.0),
          move={SEL_NEEDLE: (0.0, 0.0, 0.0), SEL_TOGGLE: (0.0, 0.0, 0.0)})
FAN_ANIM = ("ozl_work_fan", dict(type="rotation", source="ozl_work", sourceAddress="loop", selection=SEL_WORK,
                                 axis="ozl_work_axis", memory=1, minValue=0.0, maxValue=1.0 / FAN_TURNS, angle0=0.0,
                                 angle1=2 * math.pi))
NEEDLE_ANIM = ("ozl_needle_volt", dict(type="rotation", source="ozl_needle", selection=SEL_NEEDLE,
                                       axis="ozl_needle_axis", memory=1, minValue=0.0, maxValue=1.0, angle0=0.0,
                                       angle1=math.radians(NEEDLE_SWEEP)))
TOGGLE_ANIM = ("ozl_toggle_flip", dict(type="rotation", source="ozl_toggle", selection=SEL_TOGGLE,
                                       axis="ozl_toggle_axis", memory=1, minValue=0.0, maxValue=1.0, angle0=0.0,
                                       angle1=math.radians(TOG_SWING)))
PANELS = {"lcd": dict(off="decal_lcd_off.png", frames=["decal_lcd_f%02d.png" % i for i in range(6)], size=128,
                      gloss=0.6)}
# module proxies: slots OZL_Tool1..3 are linked to them by the mod's CfgNonAIVehicles (Proxyozl_tool1..3)
PROXIES = [(r"\OpenZone_Research\models\proxies\ozl_tool%d" % (i + 1), m) for i, m in enumerate(MODS)]


def _yaw(deg):
    """Direction on the table at angle deg from +x."""
    a = math.radians(deg)
    return (math.cos(a), math.sin(a), 0.0)


# vanilla DayZ items: tools on nails on the back panel, a screwdriver by the NVG on the board, a flashlight
# and a 9 V battery for it, a radio under repair on the shelf, an electrician's kit, insulating tape
DECOR = [kv.put(k, (x, YP - 0.0005, z), **kv.hung(deg)) for k, x, z, deg in HUNG] + [
    kv.put("screwdriver", (-0.455, -0.175, ZT), **kv.flat(167)),
    kv.put("flashlight", (-0.265, -0.29, ZT), up=(0, 0, 1), fwd=(math.sin(math.radians(8)), -math.cos(math.radians(8)), 0)),
    kv.put("battery9v", (-0.165, -0.245, ZT), **kv.flat(24)),
    kv.put("radio", (0.15, 0.235, ZP), up=(0, 0, 1), fwd=(0, -1, 0)),
    kv.put("electrickit", (0.47, 0.215, ZP), **kv.flat(95)),
    kv.put("ducttape", (0.665, 0.225, ZP), **kv.flat(0)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 selections=(SEL_LAMP, SEL_SCREEN, SEL_WORK, SEL_NEEDLE, SEL_TOGGLE), hidden=(SEL_LAMP, SEL_SCREEN),
                 states={"on": ON}, bones=((SEL_WORK, ""), (SEL_NEEDLE, ""), (SEL_TOGGLE, "")),
                 animations=(FAN_ANIM, NEEDLE_ANIM, TOGGLE_ANIM), proxies=PROXIES, decor=DECOR, panels=PANELS,
                 modules=[(o, n, m) for (o, n), m in zip(MOD_OBJ, MODS)],
                 sources={"ozl_work": dict(animPeriod=2.0), "ozl_needle": dict(animPeriod=0.2),
                          "ozl_toggle": dict(animPeriod=0.15)})
P = M.part
BOUNDS = {}

# "Work" pose in the preview (render only, not exported to p3d): group -> (axis point, axis, right-hand
# angle). The needle turns clockwise seen from the face (axis +y points away from the person); the
# toggle lever goes up.
POSE = {SEL_NEEDLE: (GAUGE, Vector((0.0, 1.0, 0.0)), math.radians(NEEDLE_SWEEP * NEEDLE_MID)),
        SEL_TOGGLE: (TOG_PIVOT, Vector((1.0, 0.0, 0.0)), math.radians(TOG_SWING))}


def _posed(place):
    """krender.place_look / place that rotates the POSE group parts in the "work" look (move = ON["move"])."""
    def wrap(parts, *a, **kw):
        obs = place(parts, *a, **kw)
        if kw.get("move") is ON["move"]:
            for ob, p in zip(obs, parts):
                if p.group in POSE:
                    piv, ax, ang = POSE[p.group]
                    m = Matrix.Translation(piv) @ Matrix.Rotation(ang, 4, ax) @ Matrix.Translation(-piv)
                    ob.matrix_world = m @ Matrix.Translation(ob.location)
        return obs
    return wrap


krender.place_look = _posed(krender.place_look)
krender.place = _posed(krender.place)


def bev(lod, r=0.003, seg=1):
    return dict(r=r, seg=seg) if lod == 0 else {}


# =============================================================================
# Table (B1 base, boards): chamfers, boards of three tones, screws, bushing
# =============================================================================
BEVEL = {"wb_frame": 0.003, "wb_fronts": 0.0025, "wb_panel": 0.003}
PLANKS = ("plank_a", "plank_b", "plank_c", "plank_b")


def build_bench(spec):
    lod = spec["lod"]
    parts = [p for p in kfurn.workbench(M, spec, X0, X1, Y0, Y1, ZT, ZP, SHD, cab_w=CAB_W, worktop="board",
                                        outlets=0, lamp=False) if p.name != "wb_top"]
    for p in parts:
        # chamfers on the edges (the kfurn base is boxes with sharp edges): near LOD only
        if lod == 0 and p.name in BEVEL:
            g.bevel(p.bm, p.bm.edges[:], BEVEL[p.name], 1)
    # boards: four planed 40 mm boards with rounded edges and gaps, each with its own tone
    w = (Y1 - Y0 + 0.015) / 4
    if lod == 2:
        pl = P("planks", "plank_a")
        g.box(pl, X0 - 0.01, X1 + 0.01, Y0 - 0.01, Y1 + 0.005, ZU, ZT)
        return parts + [pl]
    for k in range(4):
        ya = Y0 - 0.01 + k * w + (0.0015 if k else 0.0)
        yb = Y0 - 0.01 + (k + 1) * w - (0.0015 if k < 3 else 0.0)
        pl = P("plank%d" % k, PLANKS[k])
        g.box(pl, X0 - 0.01, X1 + 0.01, ya, yb, ZU, ZT, **bev(lod, 0.004))
        parts.append(pl)
    if lod == 0:
        # screws: one per board over the left legs and at the right edge
        sc = P("plank_screws", "screw")
        for k in range(4):
            yc = Y0 - 0.01 + (k + 0.5) * w
            for x in (X0 + 0.03, X1 - 0.03):
                g.cyl(sc, (x, yc + 0.03 * ((k % 2) - 0.5), ZT + 0.0003), "z", 0.0042, 0.0008, 4)
        parts.append(sc)
        # adjustable feet under the left legs: hex nut and heel
        ft = P("wb_feet", "steel")
        for y in (Y0 + 0.05, Y1 - 0.05):
            g.cyl(ft, (X0 + 0.03, y, 0.016), "z", 0.009, 0.010, 6)
        parts.append(ft)
    return parts


def build_tarp(spec):
    """Tarpaulin: folded on the left end of the shelf, thrown over the edge and hanging down the left post
    in folds to 0.96 m."""
    lod = spec["lod"]
    nj = 7 if lod == 0 else (5 if lod == 1 else 3)
    ys = [YS - 0.01 + (Y1 + 0.02 - YS) * j / (nj - 1) for j in range(nj)]
    rows = []
    for x in ((-0.64, -0.70, -0.755, X0) if lod == 0 else (-0.64, X0)):
        rows.append([(x, y, ZP + 0.012 + 0.006 * math.sin(9 * y + 4 * x) + 0.004 * math.sin(23 * y)) for y in ys])
    zs = ([ZP - 0.005, ZP - 0.04, 1.30, 1.22, 1.14, 1.07, 1.01, TP_Z1] if lod == 0 else
          ([ZP - 0.03, 1.18, TP_Z1] if lod == 1 else [ZP - 0.03, TP_Z1]))
    for k, z in enumerate(zs):
        depth = 0.004 + 0.018 * (ZP - z) / (ZP - TP_Z1)
        row = []
        for j, y in enumerate(ys):
            dz = (0.025 * math.sin(7 * y + 1.3)) if z == TP_Z1 else 0.0
            fold = 0.5 + 0.5 * math.sin(26 * y + 0.7 * k)
            row.append((TP_X - 0.004 * (ZP - z > 0.02) - depth * fold, y, z + dz))
        rows.append(row)
    tp = P("tarp", "tarp")
    G.sheet(tp, rows, 0.004)
    return [tp]


# =============================================================================
# Battery under the table, wires up, bushing in the boards
# =============================================================================
def term_clip_frame(i):
    """Crocodile clip on terminal i: the jaw tips bite the top of the terminal from the front, the tail
    points forward and up."""
    x, y = TERM[i]
    tip = Vector((x, y - 0.006, BAZ + 0.019))
    u = Vector((0.15 * (1 if i else -1), -0.6, 0.78)).normalized()
    v = u.cross(Vector((0, 0, 1))).normalized()
    n = u.cross(v)
    return g.Frame(tip, u, v, -n if n.z < 0 else n)


def build_battery(spec):
    lod, sd = spec["lod"], spec["sides"]
    parts = []
    bt = P("battery", "battery")
    if lod == 2:
        g.box(bt, BAX0, BAX1, BAY0, BAY1, 0.0, BAZ)
        return [bt]
    g.box(bt, BAX0, BAX1, BAY0, BAY1, 0.008, BAZ - 0.018, **bev(lod, 0.003))
    if lod == 0:
        # stop rim at the bottom, cell partition ribs on the front
        g.box(bt, BAX0 - 0.004, BAX1 + 0.004, BAY0 - 0.004, BAY1 + 0.004, 0.0, 0.012, r=0.002, seg=1)
        for k in range(1, 6):
            x = BAX0 + (BAX1 - BAX0) * k / 6
            g.box(bt, x - 0.002, x + 0.002, BAY0 - 0.0015, BAY0 + 0.001, 0.02, BAZ - 0.03)
    parts.append(bt)
    ld = P("battery_lid", "battery_lid")
    g.box(ld, BAX0 - 0.002, BAX1 + 0.002, BAY0 - 0.002, BAY1 + 0.002, BAZ - 0.018, BAZ - 0.004, **bev(lod, 0.003))
    ym = (BAY0 + BAY1) / 2 - 0.012
    g.box(ld, BAX0 + 0.03, BAX1 - 0.03, ym - 0.016, ym + 0.016, BAZ - 0.004, BAZ, **bev(lod, 0.002))
    parts.append(ld)
    # cell plugs on the strip, terminals on bosses, red ring on the plus
    cp = P("battery_caps", "batt_cap")
    for k in range(6):
        x = BAX0 + 0.045 + (BAX1 - BAX0 - 0.09) * k / 5
        if lod == 0:
            G.lathe(cp, [(0.0095, 0.0), (0.0095, 0.006), (0.0, 0.0066)], 6, (x, ym, BAZ))
        else:
            g.cyl(cp, (x, ym, BAZ + 0.003), "z", 0.009, 0.006, 6)
    parts.append(cp)
    tm = P("battery_posts", "lead")
    for x, y in TERM:
        G.lathe(tm, [(0.015, 0.0), (0.015, 0.004), (0.0098, 0.0045), (0.0084, 0.024), (0.0, 0.0245)],
                8 if lod == 0 else 6, (x, y, BAZ - 0.004))
    parts.append(tm)
    if lod == 0:
        rr = P("battery_plus", "cap_red")
        G.lathe(rr, [(0.0175, 0.0), (0.0175, 0.0012), (0.0152, 0.0012)], 12, (TERM[0][0], TERM[0][1], BAZ - 0.004))
        parts.append(rr)
    # clips on the terminals and wires up through the bushing in the boards
    for i, (reg, boot, sgn) in enumerate((("wire_red", "boot_red", -1), ("wire_black", "boot_black", 1))):
        fr = term_clip_frame(i)
        tail = fr.p(0.061 * 1.5, 0.0, 0.0)
        if lod == 0:
            jw = P("battery_clip_jaws%d" % i, "clip_jaw", uv_name="battery_clip_jaws", uv_origin=tuple(fr.o))
            bo = P("battery_clip_boot%d" % i, boot, uv_name="battery_clip_boot", uv_origin=tuple(fr.o))
            tail = G.croc(jw, bo, fr, lod, 1.5)
            parts += [jw, bo]
        else:
            bo = P("battery_clip_boot%d" % i, boot)
            G.rod(bo, fr.p(0.03, 0, 0), tail, 0.008, 4)
            parts.append(bo)
        x = HOLE[0] + sgn * 0.004
        t0 = Vector(tail)
        pts = [tuple(t0), tuple(t0 + fr.u * 0.03), tuple(t0 + fr.u * 0.05 + Vector((sgn * 0.01, 0.0, 0.05))),
               (x + sgn * 0.025, HOLE[1] - 0.13, 0.48), (x + sgn * 0.008, HOLE[1] - 0.03, ZU - 0.07), (x, HOLE[1], ZU - 0.01),
               (x, HOLE[1], ZT + 0.002)]
        cb = P("battery_cable%d" % i, reg)
        G.cable(cb, pts, 0.0045, lod, 3, (5, 4))
        parts.append(cb)
    return parts


# =============================================================================
# Junction box: body, lid on screws, feet, voltmeter, toggle, LED, glands, cables
# =============================================================================
def gland(part, at, axis, lod):
    """Cable gland: hex nut and a dome with a hole, outward along axis."""
    G.lathe(part, [(0.0082, 0.0), (0.0082, 0.004), (0.0068, 0.0045), (0.0064, 0.010), (0.0040, 0.0135)]
            if lod == 0 else [(0.008, 0.0), (0.006, 0.012)], 6, at, axis, cap1=True)


def gland_tip(at, axis):
    return Vector(at) + Vector(axis).normalized() * 0.0135


def build_junction(spec):
    lod, sd = spec["lod"], spec["sides"]
    parts = []
    jb = P("jbox", "jbox")
    g.box(jb, JX0, JX1, JY0, JY1, ZT + (0.004 if lod == 0 else 0.0), JZ1 - 0.01, **bev(lod, 0.005, 2))
    parts.append(jb)
    jl = P("jbox_lid", "jbox_lid")
    g.box(jl, JX0 - 0.002, JX1 + 0.002, JY0 - 0.002, JY1 + 0.002, JZ1 - 0.01, JZ1, **bev(lod, 0.004))
    parts.append(jl)
    # voltmeter: dial in all LODs (the scale is a decal), needle is a bone
    vf = P("volt_face", "volt_face")
    G.lathe(vf, [(GAUGE_R, 0.0), (0.0, 0.0)], sd + 4 if lod == 0 else sd, tuple(GAUGE + Vector((0, -0.0035, 0))), (0, -1, 0))
    parts.append(vf)
    nd = P("volt_needle", "needle", group=SEL_NEEDLE)
    a = math.radians(NEEDLE_REST)
    dx, dz = math.sin(a), math.cos(a)
    px, pz = math.cos(a), -math.sin(a)
    tip, back, w = 0.0185, 0.004, 0.0009
    poly = [(GAUGE.x - dx * back + px * w, GAUGE.z - dz * back + pz * w), (GAUGE.x + dx * tip, GAUGE.z + dz * tip),
            (GAUGE.x - dx * back - px * w, GAUGE.z - dz * back - pz * w)]
    g.prism(nd, poly, (0, 2), JY0 - 0.0048, JY0 - 0.0042)
    parts.append(nd)
    if lod == 2:
        return parts
    bz = P("volt_bezel", "black")
    G.lathe(bz, [(GAUGE_R + 0.004, 0.0), (GAUGE_R + 0.004, 0.0045), (GAUGE_R + 0.0025, 0.0068), (GAUGE_R + 0.0005, 0.0068),
                 (GAUGE_R, 0.0035)] if lod == 0 else [(GAUGE_R + 0.004, 0.0), (GAUGE_R + 0.004, 0.006)],
            14 if lod == 0 else sd, tuple(GAUGE), (0, -1, 0))
    if lod == 0:
        G.lathe(bz, [(0.0028, 0.0), (0.0028, 0.0018), (0.0, 0.0024)], 8, tuple(GAUGE + Vector((0, -0.0046, 0))), (0, -1, 0))
    parts.append(bz)
    # toggle: nut, bushing, lever (bone; at rest 25 degrees down)
    tg = P("toggle_nut", "chrome")
    g.cyl(tg, tuple(TOG + Vector((0, -0.0015, 0))), "y", 0.0068, 0.003, 6)
    G.lathe(tg, [(0.0046, 0.0), (0.0046, 0.009), (0.0, 0.009)], 8, tuple(TOG), (0, -1, 0))
    parts.append(tg)
    lv = P("toggle_lever", "chrome", group=SEL_TOGGLE)
    ar = math.radians(TOG_REST)
    d = Vector((0.0, -math.cos(ar), math.sin(ar)))
    g.tube_var(lv, [tuple(TOG_PIVOT), tuple(TOG_PIVOT + d * 0.012), tuple(TOG_PIVOT + d * 0.019),
                    tuple(TOG_PIVOT + d * 0.020)], [(0.0022, 0.0022), (0.0018, 0.0018), (0.0021, 0.0021), (0.0012, 0.0012)],
               6 if lod == 0 else 5)
    parts.append(lv)
    # LED in a chrome bezel
    ld = P("led", "led", group=SEL_LAMP)
    G.lathe(ld, [(0.0029, 0.0), (0.0029, 0.004), (0.0022, 0.0062), (0.0, 0.0072)], 8, tuple(LED_P), (0, -1, 0))
    parts.append(ld)
    if lod == 0:
        lb = P("led_bezel", "chrome")
        G.lathe(lb, [(0.0048, 0.0), (0.0048, 0.002), (0.0032, 0.003), (0.003, 0.0)], 8, tuple(LED_P), (0, -1, 0))
        parts.append(lb)
        # lid screws, feet with screws into the boards
        sc = P("jbox_screws", "screw")
        for x in (JX0 + 0.007, JX1 - 0.007):
            for y in (JY0 + 0.007, JY1 - 0.007):
                G.screw(sc, (x, y, JZ1), (0, 0, 1), 0.0034, 0.0018, 6)
        parts.append(sc)
        lg = P("jbox_lugs", "jbox")
        for x, s in ((JX0, -1), (JX1, 1)):
            xa, xb = sorted((x - s * 0.002, x + s * 0.015))
            g.box(lg, xa, xb, JY1 - 0.028, JY1 - 0.004, ZT, ZT + 0.005, r=0.002, seg=1)
        parts.append(lg)
    gl = P("jbox_glands", "gland")
    gland(gl, tuple(GLAND_L), (-1, 0, 0), lod)
    for q in GLAND_R:
        gland(gl, tuple(q), (1, 0, 0), lod)
    gland(gl, tuple(GLAND_B), (0, 1, 0), lod)
    parts.append(gl)
    gm = P("hole_grommet", "rubber")
    G.lathe(gm, [(0.017, 0.0), (0.017, 0.003), (0.014, 0.0055), (0.0075, 0.0055), (0.0075, 0.0)], 10, (HOLE[0], HOLE[1], ZT),
            (0, 0, 1))
    parts.append(gm)
    # cables: from the bushing into the left gland (two wires), from the rear one to the inspection lamp,
    # from the right ones to the station (clips at the end) and to the fan
    t = gland_tip(GLAND_L, (-1, 0, 0))
    for i, (reg, dy) in enumerate((("wire_red", -0.0035), ("wire_black", 0.0035))):
        cb = P("jbox_in%d" % i, reg)
        G.cable(cb, [(HOLE[0] + dy, HOLE[1], ZT + 0.004), (HOLE[0] + dy, HOLE[1] - 0.004, ZT + 0.016),
                     (HOLE[0] + 0.02, HOLE[1] - 0.03 + dy, ZT + 0.022), (t.x - 0.015, t.y + dy, t.z - 0.004),
                     (t.x + 0.002, t.y + dy * 0.6, t.z)], 0.0032, lod, 2, (5, 4))
        parts.append(cb)
    t = gland_tip(GLAND_B, (0, 1, 0))
    lc = P("lamp_cable", "cable_grey")
    G.cable(lc, [(t.x, t.y - 0.002, t.z), (t.x, t.y + 0.016, t.z - 0.012), (t.x + 0.03, YP - 0.007, ZT + 0.0042),
                 (0.06, YP - 0.0065, ZT + 0.0042), (0.088, YP - 0.0065, ZT + 0.012), (0.095, YP - 0.006, ZT + 0.06),
                 (0.10, YP - 0.007, 0.92), (0.104, YP - 0.016, 0.995), (LX, LY + 0.006, LC.z - LHALF - 0.135)], 0.0036, lod, 2,
            (6, 4))
    parts.append(lc)
    return parts


STATION_CLIPS = [((0.405, 0.262), 25.0, "boot_red", "wire_red"), ((0.418, 0.292), 8.0, "boot_black", "wire_black")]


def build_station_lead(spec):
    """Slot 2 (M73): from the right gland a double wire along the back panel to the station place, clips at
    the ends (they lie by the station's plug; an empty slot is "a wire with clamps")."""
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    t = gland_tip(GLAND_R[0], (1, 0, 0))
    for i, ((x, y), yaw, boot, reg) in enumerate(STATION_CLIPS):
        fr = G.frame_z(x, y, yaw, ZT + G.CLIP_LOW)
        if lod == 0:
            jw = P("st_clip_jaws%d" % i, "clip_jaw", uv_name="st_clip_jaws", uv_origin=tuple(fr.o))
            bo = P("st_clip_boot%d" % i, boot, uv_name="st_clip_boot", uv_origin=tuple(fr.o))
            tail = G.croc(jw, bo, fr, lod)
            parts += [jw, bo]
        else:
            tail = fr.p(0.061, 0, 0)
        out = Vector(tail) + Vector(_yaw(yaw)) * 0.03
        dy = 0.0035 * (1 if i else -1)
        cb = P("st_lead%d" % i, reg)
        G.cable(cb, [(t.x - 0.002, t.y + dy * 0.5, t.z), (t.x + 0.02, t.y + dy, t.z - 0.006),
                     (t.x + 0.06, 0.296 + dy, ZT + 0.004), (0.20, 0.300 + dy, ZT + 0.0032), (0.43, 0.306 + dy, ZT + 0.0032),
                     (out.x + 0.04, out.y + 0.01, ZT + 0.0032), (out.x, out.y, ZT + 0.0032), tuple(tail)], 0.0028, lod, 2, (5, 4))
        parts.append(cb)
    return parts


# =============================================================================
# Back panel: inspection lamp on a nail, nails and a holder for the vanilla tools
# =============================================================================
def build_lamp(spec):
    """The lamp hangs on a hook: hook above the cage, cage of rings and ribs, bulb (ozl_lamp in all LODs)
    in the socket, rubber ribbed handle, cable down from the handle."""
    lod, sd = spec["lod"], spec["sides"]
    parts = []
    z0, z1 = LC.z - LHALF, LC.z + LHALF
    bl = P("lamp_bulb", "bulb", group=SEL_LAMP)
    prof = [(0.0, 0.0), (0.009, 0.004), (0.0145, 0.014), (0.0185, 0.030), (0.019, 0.042), (0.016, 0.054),
            (0.009, 0.062), (0.0, 0.065)]
    G.lathe(bl, prof if lod == 0 else prof[::2] + [prof[-1]], 10 if lod == 0 else 6, (LX, LY, z0 + 0.026))
    parts.append(bl)
    gp = P("lamp_grip", "lamp_grip")
    if lod == 0:
        prof = [(0.0, -0.140), (0.0060, -0.137), (0.0095, -0.118), (0.0145, -0.104)]
        for k in range(4):                                         # grip ribs
            zk = -0.094 + 0.019 * k
            prof += [(0.0174, zk), (0.0162, zk + 0.0095)]
        prof += [(0.0175, -0.018), (0.0225, -0.006), (0.0245, 0.0), (0.0245, 0.010), (0.0, 0.010)]
        G.lathe(gp, prof, 10, (LX, LY, z0 + 0.012))
    else:
        G.lathe(gp, [(0.008, -0.135), (0.017, -0.10), (0.018, -0.02), (0.024, 0.0), (0.024, 0.010), (0.0, 0.010)],
                sd, (LX, LY, z0 + 0.012))
    parts.append(gp)
    sk = P("lamp_socket", "steel")
    G.lathe(sk, [(0.0135, 0.0), (0.0135, 0.016), (0.0105, 0.019)], sd if lod == 0 else 6, (LX, LY, z0 + 0.012))
    parts.append(sk)
    cg = P("lamp_cage", "cage")
    if lod == 2:
        g.cyl(cg, (LX, LY, z1 + 0.004), "z", LR * 0.7, 0.008, 6)
        G.rod(cg, (LX, LY, z1 + 0.008), NAIL, 0.003, 3)
        return parts + [cg]
    rings = ((LC.z - 0.03, LR), (LC.z + 0.015, LR), (z1, 0.022)) if lod == 0 else \
        ((LC.z - 0.02, LR), (LC.z + 0.025, LR))
    for z, r in rings:
        G.ring(cg, (LX, LY, z), (0, 0, 1), r, 0.0016, 10 if lod == 0 else 6, 3)
    nr = 5 if lod == 0 else 4
    for k in range(nr):
        a = 2 * math.pi * (k + 0.5) / nr
        c, s = math.cos(a), math.sin(a)
        pts = [(LX + 0.025 * c, LY + 0.025 * s, z0 + 0.016), (LX + LR * c, LY + LR * s, LC.z - 0.03),
               (LX + LR * c, LY + LR * s, LC.z + 0.015), (LX + 0.022 * c, LY + 0.022 * s, z1)]
        G.cable(cg, pts, 0.0016, lod, 1, (3, 3))
    # cage cap and the hook over the nail
    G.lathe(cg, [(0.022, 0.0), (0.016, 0.006), (0.006, 0.010), (0.0, 0.011)], 10 if lod == 0 else 6, (LX, LY, z1))
    hk = [(LX, LY, z1 + 0.008), (LX, LY, z1 + 0.035), (LX, LY + 0.012, NAIL[2] + 0.012), (LX, YP - 0.012, NAIL[2] + 0.017),
          (LX, YP - 0.021, NAIL[2] - 0.002)]
    G.cable(cg, hk, 0.0022, lod, 2, (5, 4))
    parts.append(cg)
    if lod == 1:
        return parts
    nl = P("nails", "steel")
    g.cyl(nl, (NAIL[0], YP - 0.012, NAIL[2]), "y", 0.002, 0.024, 6)
    g.cyl(nl, (NAIL[0], YP - 0.0235, NAIL[2]), "y", 0.0038, 0.0012, 6)
    for key, x, z, deg in HUNG:
        lo, hi = kv.box(key)
        if key == "pliers":
            # nail between the jaws at the hinge (jaws up)
            zn = z + (hi[1] - lo[1]) / 2 - 0.075
            g.cyl(nl, (x, YP - 0.015, zn), "y", 0.002, 0.03, 6)
            g.cyl(nl, (x, YP - 0.0305, zn), "y", 0.0038, 0.0012, 6)
    parts.append(nl)
    # screwdriver holder: steel strip with a hole for the shaft, on two screws
    hd = P("sd_holder", "steel")
    for key, x, z, deg in HUNG:
        if key == "screwdriver":
            lo, hi = kv.box(key)
            zh = z + (hi[1] - lo[1]) / 2 - 0.105
            g.box(hd, x - 0.022, x + 0.022, YP - 0.032, YP, zh - 0.0015, zh + 0.0015)
            g.box(hd, x - 0.022, x + 0.022, YP - 0.0015, YP, zh - 0.0015, zh + 0.012)
            for s in (-1, 1):
                G.screw(hd, (x + s * 0.016, YP - 0.0015, zh + 0.007), (0, -1, 0), 0.0028, 0.0015, 6)
    parts.append(hd)
    return parts


def build_cassette(spec):
    """Parts cassette on the shelf: 12 drawers (4 x 3) with handles and label frames; two drawers pulled out
    with loose parts inside."""
    lod = spec["lod"]
    bx = P("cassette", "cassette")
    g.box(bx, KX0, KX1, KY0 + 0.004, KY1, ZP, ZP + KH, **bev(lod, 0.004))
    dr = P("cassette_drawers", "drawer")
    if lod > 0:
        g.box(dr, KX0 + 0.006, KX1 - 0.006, KY0 - 0.002, KY0 + 0.004, ZP + 0.006, ZP + KH - 0.006)
        return [bx, dr]
    w, h = (KX1 - KX0 - 0.01) / 4, (KH - 0.01) / 3
    tb = P("cassette_tabs", "cassette")
    mx = P("cassette_parts", "parts_mix")
    out = {(1, 0): 0.032, (3, 1): 0.022}
    for i in range(4):
        for j in range(3):
            xa, za = KX0 + 0.005 + w * i, ZP + 0.005 + h * j
            dy = out.get((i, j), 0.0)
            y0 = KY0 - 0.002 - dy
            g.box(dr, xa + 0.002, xa + w - 0.002, y0, y0 + 0.006, za + 0.002, za + h - 0.002)
            if dy:
                # walls and bottom of the pulled-out drawer, parts inside
                for xs in (xa + 0.003, xa + w - 0.005):
                    g.box(dr, xs, xs + 0.002, y0 + 0.006, KY0, za + 0.004, za + h - 0.012)
                g.box(dr, xa + 0.003, xa + w - 0.003, y0 + 0.006, KY0, za + 0.003, za + 0.005)
                for k in range(3):
                    g.cyl(mx, (xa + 0.014 + 0.012 * k, y0 + 0.012 + 0.005 * (k % 2), za + 0.0075), "x", 0.0018, 0.0065, 6)
            g.box(tb, xa + w / 2 - 0.011, xa + w / 2 + 0.011, y0 - 0.010, y0, za + h / 2 - 0.006, za + h / 2 - 0.002)
    return [bx, dr, tb, mx]


def build_spools(spec):
    """Solder spool and mounting-wire spool on the shelf between the cassette and the radio."""
    lod, sd = spec["lod"], spec["sides"]
    if lod == 2:
        return []
    parts = []
    for name, (y, rw, reg) in (("solder", (0.15, 0.034, "solder")), ("wirespool", (0.275, 0.036, "wire_red"))):
        fl = P(name + "_flanges", "spool")
        cw = P(name + "_wind", reg)
        c = (SPOOL_X, y, ZP)
        if lod == 0:
            G.lathe(fl, [(0.0, 0.0), (0.043, 0.0), (0.043, 0.004), (0.016, 0.004), (0.016, 0.050), (0.043, 0.050),
                         (0.043, 0.054), (0.0, 0.054)], sd, c)
            G.lathe(cw, [(rw, 0.0045), (rw + 0.001, 0.027), (rw, 0.0495)], sd, c)
        else:
            g.cyl(fl, (SPOOL_X, y, ZP + 0.027), "z", 0.043, 0.054, sd)
        parts += [fl, cw] if lod == 0 else [fl]
    if lod == 0:
        # the end of the solder hangs from the spool
        sw = P("solder_end", "solder")
        G.cable(sw, [(SPOOL_X + 0.034, 0.13, ZP + 0.03), (SPOOL_X + 0.05, 0.11, ZP + 0.02), (SPOOL_X + 0.06, 0.085, ZP + 0.004),
                     (SPOOL_X + 0.09, 0.075, ZP + 0.0012)], 0.0009, lod, 3, (5, 3))
        parts.append(sw)
    return parts


# =============================================================================
# Board: vise, multimeter with probes, 3336 battery, flat flashlight
# =============================================================================
def build_vise(spec):
    """Clamp vise: cast base plate and body with a rib and a small anvil, movable jaw on a slide, serrated
    jaws, screw with a tommy bar and balls; a clamp under the board with a screw and a heel."""
    lod, sd = spec["lod"], spec["sides"]
    v = P("vise", "vise")
    x0, x1 = VX - 0.055, VX + 0.055
    g.box(v, x0, x1, -0.365, -0.22, ZT, ZT + 0.014, **bev(lod, 0.004))                     # base plate
    g.box(v, VX - 0.036, VX + 0.036, -0.275, -0.22, ZT + 0.012, ZT + 0.082, **bev(lod, 0.004))  # fixed jaw
    g.box(v, VX - 0.040, VX + 0.040, -0.345, -0.305, ZT + 0.012, ZT + 0.086, **bev(lod, 0.004))  # movable jaw
    parts = [v]
    if lod == 2:
        return parts
    g.box(v, VX - 0.021, VX + 0.021, -0.305, -0.275, ZT + 0.018, ZT + 0.046, **bev(lod, 0.002))  # slide
    # clamp: down along the edge and under the board
    g.box(v, VX - 0.02, VX + 0.02, -0.388, -0.366, ZU - 0.04, ZT + 0.014, **bev(lod, 0.003))
    g.box(v, VX - 0.02, VX + 0.02, -0.388, -0.318, ZU - 0.056, ZU - 0.04, **bev(lod, 0.003))
    if lod == 0:
        # small anvil behind the fixed jaw, and the rib
        g.box(v, VX - 0.030, VX + 0.030, -0.222, -0.192, ZT + 0.060, ZT + 0.076, r=0.003, seg=1)
        g.prism(v, [(-0.222, ZT + 0.014), (-0.222, ZT + 0.060), (-0.200, ZT + 0.060)], (1, 2), VX - 0.006, VX + 0.006)
    st = P("vise_steel", "steel")
    jw = P("vise_jaws", "vise_jaw")
    for y0, y1 in ((-0.281, -0.275), (-0.305, -0.299)):
        g.box(jw, VX - 0.0375, VX + 0.0375, y0, y1, ZT + 0.050, ZT + 0.084)
        if lod == 0:
            yf = y0 if y0 > -0.29 else y1
            for k in range(3):
                z = ZT + 0.057 + 0.0095 * k
                g.box(jw, VX - 0.0375, VX + 0.0375, yf - 0.0007, yf + 0.0007, z, z + 0.0014)
    G.rod(st, (VX, -0.345, ZT + 0.034), (VX, -0.418, ZT + 0.034), 0.0068, 10 if lod == 0 else 6)       # screw
    if lod == 0:
        ball = [(0.0, -0.0075), (0.0062, -0.0038), (0.0062, 0.0038), (0.0, 0.0075)]
        G.lathe(st, [(0.0115, 0.0), (0.0115, 0.016), (0.0, 0.016)], 10, (VX, -0.410, ZT + 0.034), (0, -1, 0))  # head
        G.rod(st, (VX - 0.066, -0.418, ZT + 0.034), (VX + 0.066, -0.418, ZT + 0.034), 0.0042, 8)          # tommy bar
        for x in (VX - 0.068, VX + 0.068):
            G.lathe(st, ball, 8, (x, -0.418, ZT + 0.034), (1, 0, 0))
        # clamp screw with a heel under the board and a tommy bar at the bottom
        G.rod(st, (VX, -0.352, ZU - 0.085), (VX, -0.352, ZU - 0.006), 0.0055, 8)
        G.lathe(st, [(0.012, 0.0), (0.012, 0.004), (0.0, 0.005)], 10, (VX, -0.352, ZU - 0.009), (0, 0, 1))
        G.rod(st, (VX - 0.04, -0.352, ZU - 0.08), (VX + 0.04, -0.352, ZU - 0.08), 0.0035, 6)
        for x in (VX - 0.042, VX + 0.042):
            G.lathe(st, [(a * 0.8, b * 0.8) for a, b in ball], 6, (x, -0.352, ZU - 0.08), (1, 0, 0))
    else:
        G.rod(st, (VX - 0.06, -0.418, ZT + 0.034), (VX + 0.06, -0.418, ZT + 0.034), 0.004, 4)
    parts += [st, jw]
    return parts


def build_meter(spec):
    """DT-830 type multimeter face up: rounded case, face with the scale, LCD frame, LCD (section lcd,
    ozl_screen), selector knob, three sockets; probe plugs in COM and VΩ, wires in loops to the probes on
    the terminals of the 3336 battery."""
    lod, sd = spec["lod"], spec["sides"]
    parts = []
    cs = P("mm_case", "mm")
    g.box(cs, MMX0, MMX1, MMY0, MMY1, ZT, MMZ - 0.002, **bev(lod, 0.006, 2))
    parts.append(cs)
    fc = P("mm_face", "mm_face")
    g.box(fc, MMX0 + 0.004, MMX1 - 0.004, MMY0 + 0.004, MMY1 - 0.004, MMZ - 0.003, MMZ, **bev(lod, 0.0015))
    parts.append(fc)
    # LCD: own section ("work" frames), flat UV 0..1 over the window; image top toward the back panel
    lc = P("mm_lcd", "black", group=SEL_SCREEN, section="lcd")
    zl = MMZ + (0.0016 if lod < 2 else 0.0004)
    fr = g.Frame((0.0, 0.0, zl), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    vs = [lc.bm.verts.new((x, y, zl)) for x, y in ((LCD[0], LCD[2]), (LCD[1], LCD[2]), (LCD[1], LCD[3]), (LCD[0], LCD[3]))]
    lc.tag([G.face(lc, vs, (0, 0, 1))])
    lc.glass_frame = (fr, LCD[0], LCD[1], LCD[2], LCD[3])
    parts.append(lc)
    if lod == 2:
        return parts
    bz = P("mm_bezel", "black")
    for x0, x1, y0, y1 in ((LCD[0] - 0.004, LCD[1] + 0.004, LCD[2] - 0.004, LCD[2]), (LCD[0] - 0.004, LCD[1] + 0.004, LCD[3], LCD[3] + 0.004),
                           (LCD[0] - 0.004, LCD[0], LCD[2], LCD[3]), (LCD[1], LCD[1] + 0.004, LCD[2], LCD[3])):
        g.box(bz, x0, x1, y0, y1, MMZ, MMZ + 0.0016)
    parts.append(bz)
    kn = P("mm_knob", "black")
    kc = ((MMX0 + MMX1) / 2, MMY0 + 0.055, MMZ)
    if lod == 0:
        G.lathe(kn, [(0.0165, 0.0), (0.0165, 0.004), (0.0155, 0.0055), (0.0, 0.0055)], 12, kc)
        g.box(kn, kc[0] - 0.0028, kc[0] + 0.0028, kc[1] - 0.0145, kc[1] + 0.0145, MMZ + 0.0055, MMZ + 0.0095, r=0.0012, seg=1)
        pt = P("mm_pointer", "beige")
        g.box(pt, kc[0] - 0.0007, kc[0] + 0.0007, kc[1] + 0.006, kc[1] + 0.0135, MMZ + 0.0095, MMZ + 0.0098)
        parts.append(pt)
    else:
        g.cyl(kn, (kc[0], kc[1], MMZ + 0.003), "z", 0.016, 0.006, sd)
    parts.append(kn)
    if lod > 0:
        return parts
    jk = P("mm_jacks", "black")
    for x, reg in JACKS:
        G.lathe(jk, [(0.0046, 0.0), (0.0046, 0.0012), (0.0024, 0.0012)], 8, (x, JACK_Y, MMZ))
    parts.append(jk)
    # probe plugs in COM (black) and VΩ (red): the cap stands in the socket, the wire leaves from the top
    for k, (tipp, d, preg, wreg, j) in enumerate(PROBES):
        x = JACKS[j][0]
        pl = P("mm_plug%d" % k, preg, uv_name="mm_plug", uv_origin=(x, JACK_Y, MMZ))
        G.lathe(pl, [(0.0040, 0.0), (0.0046, 0.003), (0.0046, 0.018), (0.0030, 0.025), (0.0018, 0.029), (0.0, 0.0292)],
                8, (x, JACK_Y, MMZ))
        parts.append(pl)
        # probe: handle with a stop and a needle, tip on the battery terminal
        d = d.normalized()
        back = tipp + d * 0.128
        pr = P("mm_probe%d" % k, preg, uv_name="mm_probe", uv_origin=tuple(back))
        G.lathe(pr, [(0.0, 0.0), (0.0032, 0.003), (0.0046, 0.018), (0.0046, 0.070), (0.0074, 0.074), (0.0074, 0.080),
                     (0.0050, 0.083), (0.0030, 0.106), (0.0, 0.109)], 8, tuple(back), tuple(-d))
        parts.append(pr)
        nd = P("mm_tip%d" % k, "steel", uv_name="mm_tip", uv_origin=tuple(tipp))
        G.lathe(nd, [(0.0011, 0.0), (0.0011, 0.016), (0.0004, 0.019), (0.0, 0.0195)], 6, tuple(back - d * 0.108), tuple(-d))
        parts.append(nd)
        # wire: from the cap up, in an arc onto the board, in a loop to the probe tail
        side = 1 if j == 1 else -1
        top = (x, JACK_Y, MMZ + 0.029)
        out = back + d * 0.02
        if side < 0:
            mid = [(x - 0.002, JACK_Y - 0.007, MMZ + 0.033), (x - 0.010, JACK_Y - 0.028, ZT + 0.014), (-0.005, -0.03, ZT + 0.003),
                   (-0.035, -0.078, ZT + 0.003), (-0.10, -0.082, ZT + 0.003), (out.x - 0.015, out.y - 0.012, ZT + 0.003)]
        else:
            mid = [(x + 0.002, JACK_Y - 0.007, MMZ + 0.033), (x + 0.014, JACK_Y - 0.026, ZT + 0.014), (0.10, 0.0, ZT + 0.003),
                   (0.175, -0.022, ZT + 0.003), (0.205, -0.052, ZT + 0.003), (out.x + 0.012, out.y - 0.008, ZT + 0.003)]
        cb = P("mm_lead%d" % k, wreg)
        G.cable(cb, [top] + mid + [tuple(out), tuple(back + d * 0.002)], 0.0019, lod, 2, (4, 4))
        parts.append(cb)
    return parts


def build_battery3336(spec):
    """3336 battery lying on its wide side, tab terminals (the short one is plus) toward the multimeter;
    probe needles on them."""
    lod = spec["lod"]
    if lod == 2:
        return []
    x, y = B3
    bt = P("batt3336", "batt3336")
    g.box(bt, x - 0.031, x + 0.031, y - 0.0335, y + 0.0335, ZT, ZT + 0.022, **bev(lod, 0.002))
    parts = [bt]
    if lod == 0:
        bd = P("batt3336_band", "batt_band")
        g.box(bd, x - 0.0312, x + 0.0312, y - 0.010, y + 0.012, ZT + 0.0001, ZT + 0.0222)
        parts.append(bd)
        # plus is the short tab (right, under the red probe), minus the long one (left, under the black probe)
        cp = P("batt3336_tabs", "brass")
        for dx, ln in ((0.015, 0.010), (-0.015, 0.016)):
            xx = x + dx
            g.sweep(cp, [(xx, y + 0.0330, ZT + 0.017), (xx, y + 0.0345 + 0.002, ZT + 0.017),
                         (xx, y + 0.0345 + ln, ZT + 0.0105)], (1, 0, 0), 0.00025, 0.0032)
        parts.append(cp)
    return parts


def build_flashlight(spec):
    """Flat army flashlight: stands facing the person - bezel with glass and reflector, button on the side,
    ring handle on top; no back cover (the battery bay is dark) - the cover with its clip lies beside it."""
    lod, sd = spec["lod"], spec["sides"]
    x, y = FF
    bd = P("ff_body", "olive")
    g.box(bd, x - 0.035, x + 0.035, y - 0.0175, y + 0.0175, ZT, ZT + 0.11, **bev(lod, 0.007, 2))
    parts = [bd]
    if lod == 2:
        return parts
    zl = ZT + 0.072
    rf = P("ff_bezel", "reflector")
    G.lathe(rf, [(0.0255, 0.0), (0.0255, 0.0045), (0.0232, 0.006), (0.0205, 0.006)] if lod == 0 else
            [(0.025, 0.0), (0.025, 0.005)], 16 if lod == 0 else sd, (x, y - 0.0175, zl), (0, -1, 0))
    parts.append(rf)
    gl = P("ff_glass", "glass")
    G.lathe(gl, [(0.0208, 0.0), (0.0, 0.0)], 16 if lod == 0 else sd, (x, y - 0.0175 - 0.0042, zl), (0, -1, 0))
    parts.append(gl)
    if lod == 0:
        rr = P("ff_reflector", "reflector")
        G.lathe(rr, [(0.004, 0.0), (0.0185, -0.0003)], 12, (x, y - 0.0175 - 0.0046, zl), (0, -1, 0))
        parts.append(rr)
        dk = P("ff_back", "black")
        g.box(dk, x - 0.028, x + 0.028, y + 0.0172, y + 0.0178, ZT + 0.008, ZT + 0.102)
        parts.append(dk)
        st = P("ff_steel", "steel")
        g.box(st, x + 0.035, x + 0.039, y - 0.006, y + 0.006, ZT + 0.05, ZT + 0.068, r=0.0012, seg=1)
        G.ring(st, (x, y, ZT + 0.118), (0, 1, 0), 0.008, 0.0015, 12, 3)
        parts.append(st)
        # back cover lying inside up, the clip below (it rests on it)
        cx, cy = FF_COVER
        cv = P("ff_cover", "olive")
        G.open_box(cv, cx - 0.035, cx + 0.035, cy - 0.0525, cy + 0.0525, ZT + 0.003, ZT + 0.010, 0.0022)
        cl = P("ff_clip", "steel")
        g.box(cl, cx - 0.008, cx + 0.008, cy - 0.04, cy + 0.03, ZT, ZT + 0.003)
        parts += [cv, cl]
    return parts


# =============================================================================
# Disassembled NVG: body with eyepieces, objective, image tube, board, cover, screws, battery bay cap
# =============================================================================
def build_nvg(spec):
    lod, sd = spec["lod"], spec["sides"]
    parts = []
    x, y = NB
    bd = P("nvg_body", "olive")
    g.box(bd, x - 0.07, x + 0.07, y - 0.0375, y + 0.0375, ZT, ZT + 0.062, **bev(lod, 0.008, 2))
    parts.append(bd)
    ob = P("nvg_objective", "olive")
    lens = P("nvg_lens", "lens")
    prof = [(0.022, 0.0), (0.022, 0.008), (0.027, 0.0085), (0.027, 0.013), (0.0298, 0.0135), (0.0298, 0.036),
            (0.0278, 0.0365), (0.0278, 0.060), (0.031, 0.061), (0.031, 0.074), (0.0262, 0.0755)]
    G.lathe(ob, prof if lod == 0 else [prof[i] for i in (0, 4, 8, 10)], 10 if lod == 0 else sd, tuple(NV_OBJ), (1, 0, 0))
    G.lathe(lens, [(0.0262, 0.0745), (0.0, 0.0745)], sd, tuple(NV_OBJ), (1, 0, 0))
    parts += [ob, lens]
    if lod == 2:
        return parts
    # eyepieces with rubber eyecups toward the person
    ep, cup = P("nvg_eyepieces", "black"), P("nvg_eyecups", "rubber")
    for dx in (-0.033, 0.033):
        c = (x + dx, y - 0.0375, ZT + 0.034)
        G.lathe(ep, [(0.0168, 0.0), (0.0168, 0.010), (0.0186, 0.011), (0.0186, 0.021), (0.0168, 0.022)],
                10 if lod == 0 else 8, c, (0, -1, 0))
        G.lathe(cup, [(0.0172, 0.021), (0.0205, 0.030), (0.0228, 0.043), (0.0218, 0.0465), (0.0125, 0.044)]
                if lod == 0 else [(0.0172, 0.021), (0.022, 0.046), (0.012, 0.044)], 10 if lod == 0 else 8, c, (0, -1, 0))
        G.lathe(lens, [(0.0125, 0.040), (0.0, 0.040)], 10 if lod == 0 else 6, c, (0, -1, 0))
    parts += [ep, cup]
    if lod == 1:
        return parts
    # objective socket at the back (objective removed), battery bay on top, button on the side, open top
    st = P("nvg_mount", "steel")
    G.lathe(st, [(0.0268, 0.0), (0.0268, 0.007), (0.0222, 0.0075)], sd, (x, y + 0.0375, ZT + 0.032), (0, 1, 0))
    G.lathe(st, [(0.0115, 0.0), (0.0115, 0.009), (0.0098, 0.0095)], sd, (x + 0.042, y, ZT + 0.062), (0, 0, 1))
    g.cyl(st, (NV_OBJ.x + 0.004, NV_OBJ.y, NV_OBJ.z), "x", 0.0215, 0.008, sd)                       # objective thread
    parts.append(st)
    dk = P("nvg_dark", "black")
    G.lathe(dk, [(0.0222, 0.0), (0.0, 0.0)], sd, (x, y + 0.0375 + 0.0068, ZT + 0.032), (0, 1, 0))
    G.lathe(dk, [(0.0098, 0.0), (0.0, 0.0)], sd, (x + 0.042, y, ZT + 0.0712), (0, 0, 1))
    g.box(dk, x - 0.058, x + 0.016, y - 0.026, y + 0.026, ZT + 0.0618, ZT + 0.0624)
    G.lathe(dk, [(0.0055, 0.0), (0.0055, 0.004), (0.0, 0.0045)], 8, (x - 0.07, y + 0.012, ZT + 0.040), (-1, 0, 0))
    parts.append(dk)
    # screws joining the body halves, on the sides
    br = P("nvg_side_screws", "screw")
    for sx in (-1, 1):
        for sy in (-0.022, 0.022):
            G.screw(br, (x + sx * 0.07, y + sy, ZT + 0.016), (sx, 0, 0), 0.0026, 0.0014, 6)
    parts.append(br)
    # image tube: body, ring, screen (green) and photocathode window
    tb = P("nvg_tube", "steel")
    G.lathe(tb, [(0.0195, 0.0), (0.021, 0.002), (0.021, 0.040), (0.0225, 0.041), (0.0225, 0.047), (0.0175, 0.050)],
            sd, tuple(NV_TUBE), (1, 0, 0))
    parts.append(tb)
    tf = P("nvg_tube_face", "tube_face")
    G.lathe(tf, [(0.0175, 0.050), (0.0, 0.050)], sd, tuple(NV_TUBE), (1, 0, 0))
    ct = P("nvg_cathode", "cathode")
    G.lathe(ct, [(0.0, 0.0), (0.0195, 0.0)], sd, tuple(NV_TUBE), (1, 0, 0))
    parts += [tf, ct]
    # converter board: parts, wires into the body
    cx, cy, w, h = NV_PCB
    pc = P("nvg_pcb", "pcb")
    g.box(pc, cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2, ZT, ZPCB)
    parts.append(pc)
    fe = P("pcb_ferrite", "ferrite")
    g.box(fe, cx - 0.036, cx - 0.018, cy - 0.012, cy + 0.008, ZPCB, ZPCB + 0.016, r=0.001, seg=1)
    ch = P("pcb_chip", "black")
    g.box(ch, cx + 0.010, cx + 0.022, cy + 0.006, cy + 0.0125, ZPCB, ZPCB + 0.0035)
    g.box(ch, cx + 0.004, cx + 0.010, cy - 0.020, cy - 0.016, ZPCB, ZPCB + 0.006)
    parts += [fe, ch]
    cu = P("pcb_coil", "copper")
    G.lathe(cu, [(0.0075, 0.002), (0.0082, 0.008), (0.0075, 0.014)], 12, (cx - 0.027, cy - 0.002, ZPCB), (0, 0, 1))
    parts.append(cu)
    cpb = P("pcb_caps", "cap_blue")
    for dx, dy, r, hh in ((0.006, -0.012, 0.0042, 0.012), (0.016, -0.012, 0.0042, 0.012), (0.034, 0.010, 0.0032, 0.009)):
        G.lathe(cpb, [(r, 0.0), (r, hh), (r * 0.8, hh + 0.0006), (0.0, hh + 0.0006)], 8, (cx + dx, cy + dy, ZPCB), (0, 0, 1))
    parts.append(cpb)
    rs = P("pcb_res", "resistor")
    for k in range(3):
        g.cyl(rs, (cx + 0.028, cy - 0.016 + 0.006 * k, ZPCB + 0.0016), "x", 0.0014, 0.0065, 6)
    parts.append(rs)
    for k, (reg, dx) in enumerate((("wire_red", -0.004), ("wire_black", 0.004))):
        wr = P("pcb_wire%d" % k, reg)
        G.cable(wr, [(cx - 0.02 + dx, cy + h / 2 - 0.004, ZPCB + 0.0012), (cx - 0.024 + dx, cy + h / 2 + 0.02, ZT + 0.02),
                     (x + 0.03 + dx, y - 0.06, ZT + 0.07), (x + 0.012 + dx, y - 0.012, ZT + 0.074),
                     (x + 0.005 + dx, y - 0.004, ZT + 0.0625)], 0.0011, lod, 2, (4, 3))
        parts.append(wr)
    # body cover inside up, screws scattered, bay cap
    c0, c1, w, h = NV_COVER
    cv = P("nvg_cover", "olive")
    G.open_box(cv, c0 - w / 2, c0 + w / 2, c1 - h / 2, c1 + h / 2, ZT, ZT + 0.009, 0.0025)
    parts.append(cv)
    sc = P("nvg_screws", "screw")
    for k, (sx, sy, a) in enumerate(((-0.625, -0.13, 20.0), (-0.630, -0.168, 250.0))):
        d = Vector(_yaw(a))
        hc = Vector((sx, sy, ZT + 0.0028))
        G.lathe(sc, [(0.0028, 0.0), (0.0028, 0.0012), (0.0018, 0.0022), (0.0, 0.0024)], 6, tuple(hc), tuple(d))
        G.rod(sc, hc, hc - d * 0.008 + Vector((0, 0, -0.0016)), 0.0012, 5)
    parts.append(sc)
    kc = P("nvg_cap", "olive")
    G.knurl_ring(kc, (-0.578, 0.085, ZT + 0.005), (0, 0, 1), 0.0125, 0.010, 12, 0.0010)
    parts.append(kc)
    return parts


# =============================================================================
# Smoke-extractor fan (bone ozl_work is the rotor)
# =============================================================================
def fan_quarter(k, R, S, n=6):
    """Corner k (0..3) of the fan frame in the plane (a, b): square S minus a quarter circle R."""
    a0 = math.pi / 2 * k
    c, s = math.cos(a0), math.sin(a0)
    base = [(S, 0.0), (S, S), (0.0, S)] + [(R * math.cos(math.pi / 2 * (1 - t / n)), R * math.sin(math.pi / 2 * (1 - t / n)))
                                          for t in range(n + 1)]
    return [(p * c - q * s, p * s + q * c) for p, q in base]


def build_fan(spec):
    """80 mm fan on a bent galvanized bracket: frame with screwed corners, stator spider at the back, rotor
    of 7 blades with a sticker on the hub (bone ozl_work), grille in front, foam filter at the back, wire to
    the junction box."""
    lod = spec["lod"]
    fr = FAN_FR
    parts = []
    S, R = 0.040, 0.0385
    fm = P("fan_frame", "fan")
    if lod == 2:
        g.box(fm, -S, S, -S, S, -0.0125, 0.0125, frame=fr)
        return [fm]
    for k in range(4):
        g.prism(fm, fan_quarter(k, R, S, 4 if lod == 0 else 2), (0, 1), -0.0125, 0.0125, frame=fr)
    # spider and stator at the back
    g.cyl(fm, (0.0, 0.0, -0.0105), "z", 0.016, 0.004, 12 if lod == 0 else 6, frame=fr)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        g.box(fm, 0.014, R + 0.001, -0.0015, 0.0015, -0.0125, -0.0085,
              frame=g.Frame(fr.o, fr.u * math.cos(a) + fr.v * math.sin(a), -fr.u * math.sin(a) + fr.v * math.cos(a), fr.n))
    parts.append(fm)
    # rotor is a bone
    rt = P("fan_rotor", "fan", group=SEL_WORK)
    G.lathe(rt, [(0.0145, -0.008), (0.0145, 0.0055), (0.0125, 0.0085), (0.0, 0.0090)], 12 if lod == 0 else 8,
            tuple(fr.p(0, 0, 0)), tuple(fr.n))
    nb = 7
    for k in range(nb):
        a_mid = 2 * math.pi * k / nb
        grid = []
        rs = (0.0140, 0.0345)
        for ri, r in enumerate(rs):
            sweep = 0.24 * ri
            row = []
            for t in (-0.5, 0.0, 0.5) if lod == 0 else (-0.5, 0.5):
                ang = a_mid + sweep + t * 0.62
                c = -t * 0.010
                row.append(tuple(fr.p(r * math.cos(ang), r * math.sin(ang), c)))
            grid.append(row)
        G.sheet(rt, grid, 0.0012)
    parts.append(rt)
    if lod == 0:
        lb = P("fan_label", "fan_label", group=SEL_WORK)
        G.lathe(lb, [(0.0105, 0.0091), (0.0, 0.0091)], 12, tuple(fr.p(0, 0, 0)), tuple(fr.n))
        parts.append(lb)
    # bracket: base on the board and a post behind the frame, frame screws
    zb = ZT - FAN_C.z
    br = P("fan_bracket", "zinc")
    g.box(br, -0.048, 0.048, zb, zb + 0.003, -0.07, 0.022, frame=fr)
    g.box(br, -0.044, 0.044, zb + 0.003, -0.012, -0.0305, -0.0275, frame=fr)
    parts.append(br)
    if lod == 1:
        return parts
    sc = P("fan_screws", "screw")
    for sa in (-1, 1):
        for sb in (-1, 1):
            G.screw(sc, tuple(fr.p(sa * 0.0355, sb * 0.0355, 0.0125)), tuple(fr.n), 0.0025, 0.0016, 6)
    parts.append(sc)
    # grille: two rings and four spokes
    gr = P("fan_grill", "chrome")
    for r in (0.0355,):
        G.ring(gr, tuple(fr.p(0, 0, 0.0135)), tuple(fr.n), r, 0.0008, 12, 3)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        G.rod(gr, fr.p(0.004 * math.cos(a), 0.004 * math.sin(a), 0.0135),
              fr.p(0.0375 * math.cos(a), 0.0375 * math.sin(a), 0.0128), 0.0008, 3)
    parts.append(gr)
    fo = P("fan_filter", "foam")
    g.box(fo, -0.040, 0.040, -0.038, 0.040, -0.0275, -0.0125, frame=fr, r=0.002, seg=1)
    parts.append(fo)
    # wire: from the frame corner down to the board, along the back panel to the right gland
    t = gland_tip(GLAND_R[1], (1, 0, 0))
    a = fr.p(0.036, -0.036, -0.018)
    fc = P("fan_cable", "wire_black")
    # (runs behind the station wire and its clips, right at the back panel, toward x 0.11, below the lamp wire)
    G.cable(fc, [tuple(a), tuple(fr.p(0.046, -0.044, -0.03)), (a.x + 0.012, a.y + 0.05, ZT + 0.003), (0.588, 0.20, ZT + 0.003),
                 (0.578, 0.30, ZT + 0.003), (0.55, 0.333, ZT + 0.003), (0.40, 0.333, ZT + 0.003), (0.20, 0.322, ZT + 0.003),
                 (0.12, 0.318, ZT + 0.003), (0.0, 0.318, ZT + 0.003), (t.x + 0.03, t.y + 0.02, ZT + 0.006),
                 (t.x + 0.012, t.y, t.z - 0.004), (t.x - 0.002, t.y, t.z)], 0.0022, lod, 2, (4, 4))
    parts.append(fc)
    return parts


# =============================================================================
# Board: rosin, box, wire coil, wires with crocodile clips; box on the floor
# =============================================================================
def build_rosin(spec):
    """Rosin jar without a lid, the lid leaning against it."""
    lod, sd = spec["lod"], spec["sides"]
    if lod == 2:
        return []
    x, y = ROSIN
    tn = P("rosin_tin", "alu")
    G.lathe(tn, [(0.0, 0.0), (0.032, 0.0), (0.0325, 0.002), (0.0325, 0.013), (0.0315, 0.0142), (0.0295, 0.0142),
                 (0.0295, 0.004)] if lod == 0 else [(0.0, 0.0), (0.032, 0.0), (0.032, 0.014), (0.0, 0.014)],
            sd, (x, y, ZT))
    parts = [tn]
    rn = P("rosin", "rosin")
    G.lathe(rn, [(0.0295, 0.0), (0.0, 0.0012)], sd, (x, y, ZT + 0.011))
    parts.append(rn)
    if lod == 0:
        # the lid lies beside it bottom down
        ld = P("rosin_lid", "alu")
        G.lathe(ld, [(0.0, 0.0), (0.0335, 0.0), (0.0335, 0.008), (0.031, 0.0085)], 12, (x + 0.072, y + 0.01, ZT))
        parts.append(ld)
    return parts


def build_boxes(spec):
    """Cardboard box with parts on the board and a big one on the floor under the table, flaps open."""
    lod = spec["lod"]
    parts = []
    bx = P("box_table", "card")
    x0, x1, y0, y1, h = BOX
    if lod > 0:
        g.box(bx, x0, x1, y0, y1, ZT, ZT + h)
    else:
        G.open_box(bx, x0, x1, y0, y1, ZT, ZT + h, 0.003)
        G.flap(bx, x0, x1, y0, ZT + h, 0.08, 35, 0.003, -1, sag=0.006)
        G.flap(bx, x0, x1, y1, ZT + h, 0.08, 72, 0.003, 1, sag=0.004)
    parts.append(bx)
    fb = P("box_floor", "card")
    x0, x1, y0, y1, h = FBOX
    if lod > 0:
        g.box(fb, x0, x1, y0, y1, 0.0, h)
    else:
        G.open_box(fb, x0, x1, y0, y1, 0.0, h, 0.004)
        G.flap(fb, x0, x1, y0, h, 0.12, 40, 0.004, -1, sag=0.01)
        G.flap(fb, x0, x1, y1, h, 0.12, 12, 0.004, 1, sag=0.006)
    parts.append(fb)
    if lod > 0:
        return parts
    # contents: the upper box holds bags of parts and a board, the lower one a coil of cable on assorted junk
    x0, x1, y0, y1, h = BOX
    ct = P("box_contents", "beige")
    g.box(ct, x0 + 0.01, x0 + 0.11, y0 + 0.01, y0 + 0.10, ZT + 0.003, ZT + h - 0.03, r=0.006, seg=1)
    g.box(ct, x0 + 0.12, x1 - 0.01, y0 + 0.02, y1 - 0.02, ZT + 0.003, ZT + h - 0.045, r=0.006, seg=1)
    parts.append(ct)
    pc = P("box_pcb", "pcb")
    g.box(pc, x0 + 0.13, x0 + 0.22, y0 + 0.04, y0 + 0.11, ZT + h - 0.045, ZT + h - 0.043)
    parts.append(pc)
    x0, x1, y0, y1, h = FBOX
    fc = P("box_floor_coil", "rubber")
    pts = [((x0 + x1) / 2 + (0.09 + 0.006 * math.sin(3 * a)) * math.cos(a), (y0 + y1) / 2 + 0.085 * math.sin(a),
            h - 0.035 + 0.0035 * a) for a in (2 * math.pi * 1.6 * k / 30 for k in range(31))]
    g.pipe(fc, pts, 0.008, 5)
    g.box(fc, x0 + 0.01, x1 - 0.01, y0 + 0.01, y1 - 0.01, 0.004, h - 0.045)
    parts.append(fc)
    return parts


def build_coil(spec):
    """Coil of mounting wire on the board by the cabinet: the turns are slightly spread."""
    if spec["lod"] > 0:
        return []
    cl = P("wire_coil", "wire_red")
    c = COIL
    n = 30
    pts = [(c[0] + (0.052 + 0.004 * math.sin(3 * a) + 0.002 * math.sin(7 * a)) * math.cos(a),
            c[1] + (0.047 + 0.003 * math.cos(5 * a)) * math.sin(a), ZT + 0.0022 + 0.0011 * a)
           for a in (2 * math.pi * 3.2 * k / n for k in range(n + 1))]
    g.pipe(cl, pts, 0.0021, 4)
    return [cl]


# wires with crocodile clips on the board: (wire, cap, (tip, tail yaw) of the first clip, route points,
# same for the second clip)
LEADS = (
    ("wire_red", "boot_red", ((0.05, -0.205), 20.0),
     [(0.16, -0.15), (0.24, -0.17), (0.225, -0.225), (0.15, -0.225), (0.19, -0.27), (0.30, -0.255)], ((0.43, -0.165), 214.0)),
    ("wire_black", "boot_black", ((0.065, -0.335), 12.0),
     [(0.17, -0.305), (0.25, -0.335), (0.30, -0.30)], ((0.40, -0.295), 196.0)),
)


def build_leads(spec):
    """Wires with crocodile clips at the ends, thrown in loops across the board."""
    lod = spec["lod"]
    if lod > 0:
        return []
    parts = []
    for i, (reg, boot, (p0, y0), xy, (p1, y1)) in enumerate(LEADS):
        zc = ZT + G.CLIP_LOW
        fa, fb = G.frame_z(p0[0], p0[1], y0, zc), G.frame_z(p1[0], p1[1], y1, zc)
        jw = P("lead_jaws%d" % i, "clip_jaw", uv_name="lead_jaws", uv_origin=tuple(fa.o))
        bo = P("lead_boots%d" % i, boot)
        ta = G.croc(jw, bo, fa, lod)
        tb = G.croc(jw, bo, fb, lod)
        oa, ob = ta + fa.u * 0.012, tb + fb.u * 0.012
        zw = ZT + 0.0023 + 0.0005 * i
        pts = ([tuple(ta), (oa.x, oa.y, zw + 0.002)] + [(x, y, zw) for x, y in xy] + [(ob.x, ob.y, zw + 0.002), tuple(tb)])
        cb = P("lead%d" % i, reg)
        G.cable(cb, pts, 0.0021, lod, 4, (4, 4))
        parts += [jw, bo, cb]
    return parts


def build_lod(spec):
    parts = build_bench(spec) + build_tarp(spec) + build_battery(spec) + build_junction(spec)
    parts += build_station_lead(spec) + build_lamp(spec) + build_cassette(spec) + build_spools(spec)
    parts += build_vise(spec) + build_meter(spec) + build_battery3336(spec) + build_flashlight(spec)
    parts += build_nvg(spec) + build_fan(spec) + build_rosin(spec) + build_boxes(spec) + build_coil(spec)
    parts += build_leads(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    metal = kx.PEN + r"\metalplate.rvmat"
    table = kx.box_pts(X0 - 0.03, X1 + 0.01, Y0 - 0.03, Y1 + 0.005, 0.0, ZT)
    # a component thinner than 0.5 m does not work: the upper block goes down into the table and forward over
    # the board - the parts overlap, each one is convex
    top = kx.box_pts(X0 - 0.03, X1, Y1 - 0.51, Y1, 0.40, ZP + KH + 0.01)
    comps = [(table, metal), (top, metal)]
    memory = {
        "invView": [(-0.2, -2.6, 1.3)],
        "ce_center": [(0.0, 0.0, ZP / 2)],
        "ce_radius": [(1.1, 0.0, ZP / 2)],
        # bone axes: fan - from the hub to the soldering spot; needle - from the dial to the face; toggle - along x
        "ozl_work_axis": [tuple(FAN_C), tuple(FAN_C + FAN_D * 0.05)],
        "ozl_needle_axis": [tuple(GAUGE + Vector((0, -0.004, 0))), tuple(GAUGE + Vector((0, -0.024, 0)))],
        "ozl_toggle_axis": [tuple(TOG_PIVOT - Vector((0.005, 0, 0))), tuple(TOG_PIVOT + Vector((0.005, 0, 0)))],
    }
    for i, m in enumerate(MODS):
        memory["module_%d" % (i + 1)] = [m]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2] + 0.004)
    return comps, 140.0, memory, bbox


# the first ones are for the --look preview: junction box close up (also in "work": needle, LED, LCD), the
# board with modules in place (also empty, and in "work"), overview, NVG with the oscilloscope, station
# with the fan, back panel with the lamp
SHOTS = [
    ("jbox", (0.10, -0.50, 1.07), (-0.10, 0.16, 0.83), 34),
    ("board", (-0.10, -1.20, 1.58), (-0.08, 0.02, 0.86), 30),
    ("front", (-1.0, -2.4, 1.75), (0.0, 0.0, 1.0), 32),
    ("nvg", (-0.92, -0.62, 1.16), (-0.60, 0.04, 0.84), 34),
    ("station", (0.22, -0.66, 1.24), (0.42, 0.10, 0.85), 34),
    ("lamp_panel", (0.15, -1.15, 1.45), (-0.20, 0.25, 1.18), 32),
    ("under", (-0.6, -1.5, 0.75), (-0.15, 0.0, 0.25), 32),
    ("left", (-2.0, -1.0, 1.4), (-0.6, 0.1, 0.95), 32),
    ("back", (1.4, 1.9, 1.6), (0.0, 0.0, 0.9), 32),
]

M.look_shots = (6, 2)
M.run(build_lod, collision, SHOTS, row_step=1.9, row_shot=((1.9, -6.2, 2.0), (1.9, 0, 0.80)))
