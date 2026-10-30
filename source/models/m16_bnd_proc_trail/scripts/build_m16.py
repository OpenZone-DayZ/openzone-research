"""M16 - drilling machine with a reader: Trail Analyzer of the Bandits (OZL_Bnd_Proc_Trail).
Analyzer: cargo 4x4, no modules (no module_1..3 points, as in M02, M04, M06, M08, M10, M14).

    blender --background --python build_m16.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: system Python make_decals.py (laptop screen "off" and "work" frames, keyboard, PDA
and card reader boards, boom box face).

Look: the "dayz" look (matte, dirtier), wires with crocodile clips, the board, the card reader and the
laptop in detail; the "work" loop: the spindle turns, lines run on the screen (own screen texture,
frames), LEDs blink; small things are vanilla DayZ items as proxies (kvanilla).

Machine - a Soviet bench vertical drilling machine 2M112 (drilling up to 12 mm). Sizes: in plan 870 x
560 mm, 170 kg (no datasheet was found, the height is not given). 870 here is the height (in the photos
the machine height is ~1.6 of the depth and the width about a third of the depth, as with the belt guard),
560 is the depth from the front of the base to the motor. Spindle reach 200 mm. A base with a table and
three T-slots (pitch 50, width 14 mm), a column with a lifting screw under a bellows, a head with a quill
and a three-handle feed wheel on the right, a "start/stop" push-button post on the head face, a V-belt
guard on top from the spindle to the motor, the motor at the rear right (the depth stop on the left of
the head face is left out: it moved with the quill and is not needed in the game). Factory grey-green
enamel, the guard greener (as in the NS-12 photo), rust in the chips and on the table. Chuck - a keyed
three-jaw 16 mm (dia. ~60 at the body): the jaws converge on the drill, key sockets; the key lies on the
base. Drill dia. 6 with two spiral flutes (pitch ~33 mm - 30 degree angle).

Bench - short: 1.00 x 0.60 m, height 0.66 (a low bench is used for a bench machine so that the wheel is
at hand); a welded frame of 50 angle, a steel sheet on boards on top, a shelf of boards below. Repainted
dirty black, the sheet worn to metal (Bandits).

Trim (Bandits: stolen, battered, dirty, piled with loot):
- on the machine table a machine vise with 100 mm jaws (GOST 16518): a disassembled PDA board (Palm III,
  119 x 81 mm - as in M15) is clamped flat in it: the processor in a QFP package with leads on four
  sides, two memory ICs, a crystal, capacitors; a right-angle pin header of 6 pins (pitch 2.54) is
  soldered to the right edge, two 50 mm crocodile clips are attached to it (jaws with teeth, rivet,
  spring, soft cap, red and black); the PDA body is open: the back cover lies on the machine base, the
  front half with the screen is behind the machine;
- on the right an open thick 90s laptop: ~300 x 230 x 40 mm, screen 10.4" (211 x 158), like the IBM
  ThinkPad 755 / Toshiba T4900 of 1994-97, no logo: keys separately (key 16 x 13 mm, pitch 18.3), a red
  pointing stick and two buttons under the space bar, the screen recessed 3 mm into the lid frame, ports
  at the back; a ribbon-cable plug to the card reader is in the parallel port (DB-25);
- a home-made card reader: a board on a wooden block 130 x 80 x 30: a card socket, an IC in a DIP-16
  package, an IDC 2 x 5 ribbon connector, a capacitor, a dia. 5 LED (blinks in work), the crocodile
  wires and a 9 V battery clip are soldered to it (the battery is vanilla);
- at the rear right a two-cassette boom box (~440 x 130 x 160, like the portable boom boxes of the
  1990s), handle, antenna, two volume knobs, a recording LED; a cigarette pack on it;
- rolls of insulating tape (dia. 60 x 19, blue and black), cigarette packs 88 x 55 x 22; vanilla: a
  partly drunk vodka, pliers by the vise, on the shelf an empty vodka on its side, an electrician's kit
  and a rag, a box of junk beside.

Work look: the laptop screen is ozl_screen, own texture (section screen): "off" is dark glass, "work"
is frames _screen_fNN (OZL_WorkFx frames); the LEDs of the reader and boom box are ozl_lamp (atlas _on,
blink); the spindle with the chuck and drill is the bone ozl_work on the source ozl_work: a model.cfg
loop (sourceAddress loop, maxValue 1/6) - 6 turns per pass, a pass takes 2 s (animPeriod in the mod
config), 3 turns per second: at 30 frames the jaws (120 degrees apart) advance 36 degrees per frame, so
the rotation does not appear to run backwards. At rest the spindle stands still.
Feed: while the machine works, the quill with the spindle goes down (bone ozl_feed, a child of ozl_work;
the source ozl_feed is OZL_WorkFx pose, 1.6 s) and the drill enters the memory IC of the board by 2 mm,
the feed wheel turns (ozl_wheel); after the work it goes up. The 2M112 quill travel is 100 mm; here
~95 mm: the drill is long, dia. 6 x 139 (GOST 886, long series).
The cigarette packs are DayZ "Chernomorka" packs: an own 88 x 55 x 22 box with the vanilla texture by
path (pack_of_cigs_cherno_co.paa, section cigs; the default DayZ pack model is another brand and a proxy
cannot be repainted).

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
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import krender  # noqa: E402
import kvanilla as kv  # noqa: E402
import kwood  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
# bench
BX0, BX1, BY0, BY1, ZT = -0.50, 0.50, -0.30, 0.30, 0.66
LEG, TOP_T = 0.05, 0.045
ZSH = 0.13                                                    # top of the lower shelf
# 2M112 machine: column and spindle axis (reach 200), everything from the bench top
DX = -0.25
CY = 0.15                                                     # column axis
SY = CY - 0.20                                                # spindle axis
BASE = (DX - 0.17, DX + 0.17, -0.29, 0.25)                    # base x0 x1 y0 y1
BASE_H = 0.085                                                # top of the base table
COL_R, COL_Z0, COL_Z1 = 0.045, 0.15, 0.60
HEAD = (DX - 0.12, DX + 0.12, SY - 0.07, CY + 0.075, 0.56, 0.75)
MOTOR = (DX + 0.115, CY + 0.06, 0.075)                        # motor: x, y of the axis, radius
GUARD_Z0, GUARD_Z1, GUARD_R = 0.75, 0.87, 0.105
FEED = (HEAD[1] + 0.005, SY, 0.64)                            # feed wheel hub
# spindle: quill (stands still), spindle nose, chuck, drill (bone ozl_work)
Q_Z0, CH_Z0, CH_Z1, BIT_Z0 = 0.48, 0.385, 0.455, 0.25
QUILL_TOP = 0.60                                              # the quill goes into the head (visible during the feed)
SPIN_TURNS = 6                                                # turns per loop pass
# vise under the spindle
VX, VY = DX, SY
V_W = 0.13                                                    # jaw width
V_Z0 = BASE_H
V_Z1 = BASE_H + 0.075                                         # jaw top
PCB = (0.119, 0.081, 0.0016)
PCB_Z = V_Z1 - 0.006                                          # bottom of the PDA board
# feed: the drill enters the memory IC under the spindle by 2 mm (its top is 1.4 mm above the board)
FEED_TRAVEL = BIT_Z0 - (PCB_Z + PCB[2] + 0.0014) + 0.002
# right-angle pin header at the right edge of the board: 6 pins along y, sticking out toward +x
HDR_X = VX + PCB[0] / 2
HDR_Z = ZT + PCB_Z + PCB[2] + 0.00125                         # pin axis
HDR_Y = [VY + (k - 2.5) * 0.00254 for k in range(6)]
# crocodile clips: (pin, yaw of the axis from +x, downward tilt), cap
CLIPS = [(1, -22.0, 14.0, "boot_red", "wire_red"), (4, 22.0, 14.0, "boot_black", "wire_black")]
# laptop
LAP = (0.06, 0.36, -0.29, -0.06, 0.040)                       # x0 x1 y0 y1 h
LID_H, LID_T, LID_DEG = 0.225, 0.011, 16.0
SCR = (0.236, 0.176, 0.112)                                   # screen: width, height, centre along the lid
SCR_IN = 0.003                                                # screen recessed into the frame
DB25 = (0.085, 0.140)                                         # parallel port on the laptop rear, x
# card reader, boom box
RDR = (0.005, 0.135, 0.03, 0.11, 0.030)                       # x0 x1 y0 y1 h
BB = (0.05, 0.47, 0.15, 0.28, 0.160)
# small things on the bench
TAPES = [((0.43, 0.05), 0.0, "tape_blue"), ((0.43, 0.05), 0.0195, "tape_black"), ((-0.035, -0.255), 0.0, "tape_blue")]
PACKS = [((0.43, -0.255), 18.0, 0.0), ((0.30, 0.215), -8.0, BB[4])]   # centre, rotation, bottom
PDA_PARTS = [("pda_back", (DX - 0.09, -0.225), 6.0, BASE_H), ("pda_front", (-0.015, 0.20), 80.0, 0.0)]

LOD_SPECS = [
    dict(lod=0, bev=1, sides=16),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "bench": ("paint_black", 0.6), "bench_top": ("bench_top", 0.6), "board": ("board", 0.6),
    "drill": ("drill", 0.8), "drill_table": ("drill_table", 0.9), "guard": ("guard", 0.8), "column": ("chrome", 1.2),
    "steel": ("steel", 1.0), "black": ("black", 1.5), "rubber": ("rubber", 0.6), "chuck": ("chuck", 2.0),
    "bit": ("bit", 3.0), "btn_green": ("btn_green", 3.0), "btn_red": ("btn_red", 3.0),
    "vice": ("vice", 1.2), "pcb": ("pcb", 6.0), "chip": ("chip", 5.0), "dark": ("dark", 2.0), "pda": ("pda", 2.0),
    "pda_glass": ("pda_glass", 3.0), "pin_gold": ("pin_gold", 4.0), "solder": ("solder", 4.0),
    "cap_blue": ("cap_blue", 4.0), "can": ("can", 4.0),
    "wire_red": ("wire_red", 1.0), "wire_black": ("black", 1.0), "ribbon": ("ribbon", 1.5),
    "ribbon_red": ("ribbon_red", 1.5), "db_hood": ("db_hood", 2.5),
    "clip_jaw": ("clip_jaw", 5.0), "boot_red": ("boot_red", 4.0), "boot_black": ("boot_black", 4.0),
    "lap": ("lap", 1.2), "kbd": ("kbd", 3.0), "key": ("key", 3.0), "track_red": ("track_red", 4.0),
    "reader_wood": ("wood", 1.0), "reader_pcb": ("reader_pcb", 5.0), "led": ("led", 4.0),
    "bb": ("bb", 1.0), "bb_face": ("bb_face", 3.0), "tape_blue": ("tape_blue", 1.5), "tape_black": ("tape_black", 1.5),
    "tape_core": ("card", 1.5), "carton": ("carton", 2.0), "carton_band": ("carton_band", 2.0),
    "card": ("card", 0.8), "junk": ("junk", 0.6),
}

# =============================================================================
# Materials
# =============================================================================


def decal(name, ax, sign, uv, center, size, rng=None):
    return (os.path.join(WORK, name), ax, sign, uv, center, size, rng)


def top_decal(name, center, size):
    """Decal on a top face: a part with a decal has its own area, hence no range."""
    return decal(name, "z", 1, ("x", "y"), center, size)


_LCX = (LAP[0] + LAP[1]) / 2
KBD = (LAP[0] + 0.022, LAP[1] - 0.022, LAP[3] - 0.105, LAP[3] - 0.012)
PCB_C = (VX, VY)
RDR_PCB = (RDR[0] + 0.012, RDR[1] - 0.012, RDR[2] + 0.010, RDR[3] - 0.010)
BB_FACE = (BB[0] + 0.012, BB[1] - 0.012, ZT + 0.012, ZT + BB[4] - 0.022)

KINDS = kmats.std_kinds(floor_z=0.0)
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# dirty black paint over grey (Bandits): chips down to grey, rust at the floor, dirt at the bottom
BLACK = dict(color=kmats.lin((38, 38, 36)), under=kmats.lin((124, 126, 122)), seed=1.9, gloss=0.28, spec=0.22,
             chip=(0.55, 0.61), rust=(0.58, 0.66), rust_low=1.0, floor_z=0.0, dust=0.45, grime=0.9)
# factory grey-green enamel of the machine: chips down to cast iron, rust in the chips
DRILL = dict(color=kmats.lin((104, 122, 110)), under=kmats.lin((70, 66, 62)), seed=3.3, gloss=0.38, spec=0.30,
             chip=(0.56, 0.62), rust=(0.54, 0.62), rust_low=0.0, floor_z=ZT, dust=0.4, grime=0.8)
KINDS.update({
    "paint_black": ("paint", BLACK),
    # bench sheet: black paint worn to metal, oil and rust spots
    "bench_top": ("paint", dict(BLACK, color=kmats.lin((44, 43, 40)), under=kmats.lin((96, 92, 86)), seed=2.7,
                                chip=(0.42, 0.50), rust=(0.50, 0.58), rust_low=0.0, floor_z=ZT, gloss=0.35,
                                spec=0.35, dust=0.5)),
    "board": (kwood.build_wood, dict(color=kmats.lin((112, 86, 58)), seed=3.1, along="x", floor_z=0.0, dust=0.5,
                                     grime=0.9, knots=0.6)),
    "drill": ("paint", DRILL),
    # base table: paint scraped off by chips, rust in the slots and on the edges (NS-12 photo)
    "drill_table": ("paint", dict(DRILL, color=kmats.lin((96, 100, 94)), under=kmats.lin((118, 70, 38)), seed=4.1,
                                  chip=(0.42, 0.50), rust=(0.40, 0.48), gloss=0.42, spec=0.4)),
    "guard": ("paint", dict(DRILL, color=kmats.lin((70, 110, 62)), under=kmats.lin((112, 66, 36)), seed=5.2,
                            chip=(0.54, 0.60), rust=(0.52, 0.60))),
    "chrome": ("steel", dict(seed=6.1, tone=0.34, along="z", gloss=0.60, spec=0.75, floor_z=ZT, dust=0.35, grime=0.8)),
    "chuck": ("steel", dict(seed=6.8, tone=0.32, along="z", gloss=0.60, spec=0.75, floor_z=ZT, dust=0.25, grime=0.9)),
    # high-speed steel drill: dark, blued, lighter edges
    "bit": ("steel", dict(seed=7.0, tone=0.16, along="z", gloss=0.55, spec=0.6, floor_z=ZT, dust=0.05, grime=0.4)),
    "btn_green": ("plastic", dict(color=kmats.lin((40, 112, 52)), gloss=0.45, spec=0.3, dust=0.4, grime=0.6)),
    "btn_red": ("plastic", dict(color=kmats.lin((160, 30, 24)), gloss=0.45, spec=0.3, dust=0.4, grime=0.6)),
    "vice": ("paint", dict(DRILL, color=kmats.lin((64, 80, 96)), under=kmats.lin((110, 108, 104)), seed=7.4,
                           chip=(0.50, 0.57), rust=(0.52, 0.60))),
    "pcb": ("paint", dict(CLEAN, color=kmats.lin((28, 84, 46)), gloss=0.55, spec=0.4, dust=0.15,
                          decal_items=[top_decal("decal_pcb.png", PCB_C, PCB[:2])])),
    # IC packages: black compound, matte
    "chip": ("plastic", dict(color=kmats.lin((22, 22, 24)), gloss=0.35, spec=0.25, dust=0.15, grime=0.2,
                             scuff=(0.8, 0.9))),
    "dark": ("flat", dict(color=kmats.lin((20, 20, 20)), gloss=0.3, spec=0.2)),
    "pda": ("plastic", dict(color=kmats.lin((70, 72, 74)), gloss=0.35, spec=0.25, dust=0.3, grime=0.4,
                            scuff=(0.62, 0.70))),
    "pda_glass": ("flat", dict(color=kmats.lin((60, 68, 60)), gloss=0.85, spec=0.6)),
    "pin_gold": ("paint", dict(CLEAN, color=kmats.lin((196, 156, 64)), gloss=0.6, spec=0.6, dust=0.1)),
    "solder": ("steel", dict(seed=7.7, tone=0.48, along="z", gloss=0.7, spec=0.7, dust=0.05, grime=0.2)),
    "cap_blue": ("plastic", dict(color=kmats.lin((34, 52, 118)), gloss=0.5, spec=0.35, dust=0.2, grime=0.3)),
    "can": ("steel", dict(seed=7.9, tone=0.42, along="x", gloss=0.6, spec=0.7, dust=0.1, grime=0.3)),
    "wire_red": ("plastic", dict(color=kmats.lin((160, 30, 26)), gloss=0.4, spec=0.3, dust=0.2)),
    "ribbon": ("plastic", dict(color=kmats.lin((132, 130, 124)), gloss=0.3, spec=0.2, dust=0.3, scuff=(0.8, 0.9))),
    "ribbon_red": ("plastic", dict(color=kmats.lin((150, 36, 30)), gloss=0.3, spec=0.2, dust=0.3)),
    # connector hood of the 90s: beige-grey plastic
    "db_hood": ("plastic", dict(color=kmats.lin((176, 172, 158)), gloss=0.35, spec=0.25, dust=0.4, grime=0.6)),
    # crocodile clip: nickel-plated steel, jaws in scale; caps - soft PVC
    "clip_jaw": ("steel", dict(seed=8.1, tone=0.40, along="x", gloss=0.6, spec=0.7, dust=0.1, grime=0.5)),
    "boot_red": ("plastic", dict(color=kmats.lin((168, 30, 26)), gloss=0.35, spec=0.25, dust=0.3, grime=0.5,
                                 scuff=(0.66, 0.74))),
    "boot_black": ("plastic", dict(color=kmats.lin((26, 26, 28)), gloss=0.3, spec=0.2, dust=0.3, grime=0.5,
                                   scuff=(0.66, 0.74))),
    "lap": ("plastic", dict(color=kmats.lin((46, 46, 48)), gloss=0.30, spec=0.22, dust=0.35, grime=0.5,
                            scuff=(0.58, 0.66))),
    "kbd": ("paint", dict(CLEAN, color=kmats.lin((30, 30, 32)), gloss=0.3, spec=0.2, dust=0.2,
                          decal_items=[top_decal("decal_kbd.png", ((KBD[0] + KBD[1]) / 2, (KBD[2] + KBD[3]) / 2),
                                                 (KBD[1] - KBD[0], KBD[3] - KBD[2]))])),
    # keys: dark plastic, the middle worn to a shine
    "key": ("plastic", dict(color=kmats.lin((50, 50, 53)), gloss=0.3, spec=0.2, dust=0.25, grime=0.3,
                            scuff=(0.55, 0.64))),
    "track_red": ("plastic", dict(color=kmats.lin((176, 34, 30)), gloss=0.15, spec=0.1, dust=0.1)),
    "wood": ("paint", dict(color=kmats.lin((128, 98, 66)), under=kmats.lin((86, 64, 42)), seed=4.4, gloss=0.12,
                           spec=0.06, chip=(0.60, 0.68), rust=(0.99, 1.0), rust_low=0.0, floor_z=ZT, dust=0.35,
                           grime=0.9)),
    "reader_pcb": ("paint", dict(CLEAN, color=kmats.lin((28, 84, 46)), gloss=0.55, spec=0.4, dust=0.2,
                                 decal_items=[top_decal("decal_reader.png",
                                                        ((RDR_PCB[0] + RDR_PCB[1]) / 2, (RDR_PCB[2] + RDR_PCB[3]) / 2),
                                                        (RDR_PCB[1] - RDR_PCB[0], RDR_PCB[3] - RDR_PCB[2]))])),
    # LEDs: "off" - dark red, "work" - lit (blinking is done by the mod script)
    "led": ("flat", dict(color=kmats.lin((70, 14, 12)), gloss=0.85, spec=0.8)),
    "led_on": ("flat", dict(color=kmats.lin((255, 60, 40)), gloss=0.85, spec=0.8)),
    "bb": ("plastic", dict(color=kmats.lin((40, 40, 42)), gloss=0.35, spec=0.25, dust=0.45, grime=0.5,
                           scuff=(0.58, 0.66))),
    "bb_face": ("paint", dict(CLEAN, color=kmats.lin((36, 36, 38)), gloss=0.3, spec=0.2, dust=0.25, grime=0.3,
                              decal_items=[decal("decal_boombox.png", "y", -1, ("x", "z"),
                                                 ((BB_FACE[0] + BB_FACE[1]) / 2, (BB_FACE[2] + BB_FACE[3]) / 2),
                                                 (BB_FACE[1] - BB_FACE[0], BB_FACE[3] - BB_FACE[2]))])),
    "tape_blue": ("plastic", dict(color=kmats.lin((38, 62, 128)), gloss=0.5, spec=0.35, dust=0.3, grime=0.4,
                                  scuff=(0.7, 0.8))),
    "tape_black": ("plastic", dict(color=kmats.lin((22, 22, 24)), gloss=0.5, spec=0.35, dust=0.3, grime=0.4,
                                   scuff=(0.7, 0.8))),
    "carton": ("plastic", dict(color=kmats.lin((214, 208, 196)), gloss=0.3, spec=0.2, mottle=0.06, dust=0.3,
                               grime=0.3)),
    "carton_band": ("plastic", dict(color=kmats.lin((150, 30, 30)), gloss=0.35, spec=0.25, dust=0.25)),
    "card": ("plastic", dict(color=kmats.lin((150, 118, 80)), gloss=0.08, spec=0.05, mottle=0.18, dust=0.4, grime=0.7,
                             scuff=(0.60, 0.70))),
    "junk": ("plastic", dict(color=kmats.lin((78, 74, 60)), gloss=0.08, spec=0.05, mottle=0.3, dust=0.4, grime=0.6)),
})

OBJ, NAME = "m16_bnd_proc_trail", "ozr_bnd_proc_trail"
# Work look: the screen is its own texture (the frames are stepped by the mod script), the LEDs are the _on
# atlas (blink), the spindle is a model.cfg loop.
SEL_SCREEN, SEL_LAMP, SEL_SPINDLE = "ozl_screen", "ozl_lamp", "ozl_work"
SEL_FEED, SEL_WHEEL = "ozl_feed", "ozl_wheel"
# "work" look preview: the quill with the spindle is lowered (not exported to p3d - model.cfg does it)
ON = dict(remap={"led": "led_on"}, emissive=(1.0, 1.0, 1.0, 1.0),
          move={SEL_FEED: (0.0, 0.0, -FEED_TRAVEL), SEL_SPINDLE: (0.0, 0.0, -FEED_TRAVEL)})
SPINDLE_ANIM = ("ozl_work_spindle", dict(type="rotation", source="ozl_work", sourceAddress="loop",
                                         selection=SEL_SPINDLE, axis="ozl_work_axis", memory=1, minValue=0.0,
                                         maxValue=1.0 / SPIN_TURNS, angle0=0.0, angle1=2 * math.pi))
# feed axis - a metre down from the bottom of the head: offset in metres
FEED_ANIM = ("ozl_feed_down", dict(type="translation", source="ozl_feed", selection=SEL_FEED, axis="ozl_feed_axis",
                                   memory=1, minValue=0.0, maxValue=1.0, offset0=0.0, offset1=FEED_TRAVEL))
WHEEL_TURN = 2.4                                               # wheel turn over the whole feed travel, rad
WHEEL_ANIM = ("ozl_feed_wheel", dict(type="rotation", source="ozl_feed", selection=SEL_WHEEL, axis="ozl_wheel_axis",
                                     memory=1, minValue=0.0, maxValue=1.0, angle0=0.0, angle1=-WHEEL_TURN))
# Bone axes are memory points (collision). The engine rotates a bone as a right-hand screw in DayZ axes
# (kexport.conv, determinant -1); in Blender axes that is a left-hand screw about the axis from the first
# point to the second: the axis looks at the person, a plus angle is clockwise for him (as in M08, M12,
# M14, M33 - their needles are verified in game). Spindle: the axis runs bottom to top (toward whoever looks
# from above), plus is clockwise from above, as one drills. Wheel: the axis points right, toward whoever
# looks at the wheel from the side; a minus angle is counter-clockwise for him, the front handle goes
# down when the head is lowered, as on a real drilling machine.
SPINDLE_AXIS = [(DX, SY, ZT + BIT_Z0), (DX, SY, ZT + HEAD[4])]
WHEEL_AXIS = [(FEED[0] + 0.02, FEED[1], ZT + FEED[2]), (FEED[0] + 0.12, FEED[1], ZT + FEED[2])]


def engine_turn(axis_pts, ang):
    """Rotation of a bone by angle ang as the engine will do it about the memory axis axis_pts: (point on
    the axis, Blender axis for Matrix.Rotation - a right-hand screw, angle). The Blender axis is opposite
    to the memory axis (from the second point to the first)."""
    a, b = Vector(axis_pts[0]), Vector(axis_pts[1])
    return a, a - b, ang


def check_turns():
    """By numbers, like check_axes of the Storage boxes: the spindle turns clockwise seen from above; at a
    small feed phase the front handle of the wheel (a spoke at 210 degrees: forward and down) goes down. If
    they do not match, the build fails."""
    _, ax, ang = engine_turn(SPINDLE_AXIS, 0.1)
    q = Matrix.Rotation(ang, 3, ax) @ Vector((1.0, 0.0, 0.0))
    assert q.y < -0.05, "spindle turns counter-clockwise seen from above"
    _, ax, ang = engine_turn(WHEEL_AXIS, 0.1 * WHEEL_ANIM[1]["angle1"])
    a = math.radians(210.0)
    v = Vector((0.0, math.cos(a), math.sin(a)))
    q = Matrix.Rotation(ang, 3, ax) @ v
    assert q.z < v.z - 0.05, "front handle of the wheel does not go down"
    print("turns ok: spindle - clockwise from above, wheel - front handle goes down as the head is lowered")


check_turns()
CIGS = (r"dz\gear\medical\data\pack_of_cigs_cherno_co.paa", r"dz\gear\medical\data\pack_of_cigs.rvmat")
# pieces of the pack texture (fractions of the image: x0, x1, y0, y1 top to bottom): the face with the coat of
# arms and a map, the side with the barcode, the end is a blue field
CIGS_UV = {"front": (0.117, 0.462, 0.43, 1.0), "side": (0.885, 0.970, 0.60, 1.0), "end": (0.26, 0.45, 0.20, 0.30)}
SCREEN = dict(off="decal_screen_off.png", frames=["decal_screen_f%02d.png" % i for i in range(12)], size=256,
              gloss=0.8)
DECOR = [
    kv.put("vodka", (0.43, -0.14, ZT), up=(0, 0, 1), fwd=(0.5, -1, 0)),                # half-full
    kv.put("pliers", (0.0, -0.105, ZT), **kv.flat(78)),                                   # by the vise
    kv.put("battery9v", (0.158, 0.052, ZT), up=(0, 0, 1), fwd=(0, -1, 0)),                # next to the reader
    kv.put("vodka", (0.10, 0.03, ZSH), **kv.flat(200)),                                   # empty, on the shelf
    kv.put("electrickit", (0.30, -0.13, ZSH), **kv.flat(5)),
    kv.put("rags", (0.31, 0.15, ZSH), **kv.flat(75)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 selections=(SEL_SCREEN, SEL_LAMP, SEL_SPINDLE, SEL_FEED, SEL_WHEEL), hidden=(SEL_SCREEN, SEL_LAMP),
                 states={"on": ON}, bones=((SEL_FEED, ""), (SEL_SPINDLE, SEL_FEED), (SEL_WHEEL, "")),
                 animations=(FEED_ANIM, WHEEL_ANIM, SPINDLE_ANIM), decor=DECOR, panels={"screen": SCREEN},
                 vsections={"cigs": CIGS}, sources={"ozl_work": dict(animPeriod=2.0), "ozl_feed": dict(animPeriod=1.6)})
P = M.part
BOUNDS = {}


# =============================================================================
# Primitives that kgeo does not provide
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


def rod(part, a, b, r, sides):
    """Cylinder between points a and b."""
    return g.pipe(part, [tuple(a), tuple(b)], r, sides)


def frame_z(cx, cy, deg, z):
    a = math.radians(deg)
    return g.Frame((cx, cy, z), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))


def face(part, verts, want):
    """Face from bmesh vertices, turned to look toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def lathe(part, prof, sides, center=(0.0, 0.0, 0.0), axis="z", cap=False):
    """Solid of revolution: prof [(r, h)] from bottom to top along axis ("z" or "x") from center; cap closes
    the top with a disc."""
    bm = part.bm
    c0 = Vector(center)

    def pt(r, h, k):
        a = 2 * math.pi * k / sides
        if axis == "z":
            return c0 + Vector((r * math.cos(a), r * math.sin(a), h))
        return c0 + Vector((h, r * math.cos(a), r * math.sin(a)))
    rings = [[bm.verts.new(pt(r, h, k)) for k in range(sides)] for r, h in prof]
    new = []
    for i in range(len(rings) - 1):
        for k in range(sides):
            j = (k + 1) % sides
            q = [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]
            c = sum((v.co for v in q), Vector()) / 4 - c0
            out = Vector((c.x, c.y, 0)) if axis == "z" else Vector((0, c.y, c.z))
            new.append(face(part, q, out))
    if cap:
        new.append(face(part, rings[-1], Vector((0, 0, 1)) if axis == "z" else Vector((1, 0, 0))))
    bm.normal_update()
    part.tag(new)


def hull2(circles, n):
    """Convex hull of circles [(x, y, r)] as a polygon (belt guard)."""
    pts = []
    for x, y, r in circles:
        pts += [(x + r * math.cos(2 * math.pi * k / n), y + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    pts = sorted(set(pts))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 1e-12:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 1e-12:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def knurl(part, cx, cy, z0, z1, r, n, depth):
    """Knurled bushing about z: 2n vertices around, every other one recessed by depth."""
    poly = [(cx + (r - depth * (k % 2)) * math.cos(math.pi * k / n), cy + (r - depth * (k % 2)) * math.sin(math.pi * k / n))
            for k in range(2 * n)]
    return g.prism(part, poly, (0, 1), z0, z1)


def twist_drill(part, cx, cy, z0, z1, r, turns, n_len, n_sec):
    """Twist drill along z: a section with two lands and two flutes is rotated along the axis by `turns`
    turns - in rotation you can see the flutes run; the bottom is a 118 degree point cone."""
    bm = part.bm
    rings = []
    for i in range(n_len + 1):
        t = i / n_len
        z = z0 + (z1 - z0) * t
        a0 = 2 * math.pi * turns * t
        ring = []
        for k in range(n_sec):
            a = 2 * math.pi * k / n_sec
            rr = r * (0.58 + 0.42 * abs(math.cos(a)) ** 0.6)
            ring.append(bm.verts.new((cx + rr * math.cos(a + a0), cy + rr * math.sin(a + a0), z)))
        rings.append(ring)
    new = []
    for i in range(n_len):
        for k in range(n_sec):
            j = (k + 1) % n_sec
            q = [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]
            c = sum((v.co for v in q), Vector()) / 4
            new.append(face(part, q, (c.x - cx, c.y - cy, 0)))
    tip = bm.verts.new((cx, cy, z0 - r * 0.6))
    for k in range(n_sec):
        j = (k + 1) % n_sec
        new.append(face(part, [rings[0][k], rings[0][j], tip], (0, 0, -1)))
    new.append(face(part, rings[-1], (0, 0, 1)))
    bm.normal_update()
    part.tag(new)


def ribbon(part, pts, wdir, half_w, half_t):
    """Flat ribbon along pts (ribbon cable): the width is along wdir, straightened across the path, the
    thickness across the ribbon; the ribbon does not collapse on a climb, unlike kgeo.sweep with a constant normal."""
    bm = part.bm
    pts = [Vector(p) for p in pts]
    n = len(pts)
    rings = []
    for i in range(n):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        w = Vector(wdir) - t * Vector(wdir).dot(t)
        w.normalize()
        th = t.cross(w).normalized()
        c = pts[i]
        rings.append([bm.verts.new(c + w * half_w + th * half_t), bm.verts.new(c - w * half_w + th * half_t),
                      bm.verts.new(c - w * half_w - th * half_t), bm.verts.new(c + w * half_w - th * half_t)])
    new = []
    for i in range(n - 1):
        r0, r1 = rings[i], rings[i + 1]
        for q in range(4):
            new.append(bm.faces.new([r0[q], r0[(q + 1) % 4], r1[(q + 1) % 4], r1[q]]))
    new.append(bm.faces.new(rings[0][::-1]))
    new.append(bm.faces.new(rings[-1]))
    import bmesh
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def box_to(part, a, b, w, h, up=(0, 0, 1)):
    """Bar from point a to point b with cross-section w (across) x h (along up)."""
    a, b = Vector(a), Vector(b)
    u = (b - a).normalized()
    n = Vector(up) - u * Vector(up).dot(u)
    n.normalize()
    v = n.cross(u)
    fr = g.Frame(a, u, v, n)
    return g.box(part, 0.0, (b - a).length, -w / 2, w / 2, -h / 2, h / 2, frame=fr)


# =============================================================================
# Bench
# =============================================================================
def build_bench(spec):
    lod = spec["lod"]
    zu = ZT - TOP_T
    tp = P("bench_top", "bench_top")
    g.box(tp, BX0, BX1, BY0, BY1, ZT - 0.004, ZT)
    bd = P("bench_boards", "board")
    g.box(bd, BX0 + 0.005, BX1 - 0.005, BY0 + 0.005, BY1 - 0.005, zu, ZT - 0.004)
    fr = P("bench_frame", "bench")
    parts = [tp, bd, fr]
    for sx in (BX0, BX1 - LEG):
        for sy in (BY0, BY1 - LEG):
            g.box(fr, sx, sx + LEG, sy, sy + LEG, 0.0, zu)
    if lod == 2:
        g.box(bd, BX0 + LEG, BX1 - LEG, BY0 + LEG, BY1 - LEG, ZSH - 0.025, ZSH)
        return parts
    # aprons under the sheet and the shelf frame
    for za, zb in ((zu - 0.05, zu), (ZSH - 0.04, ZSH - 0.02)):
        g.box(fr, BX0 + LEG, BX1 - LEG, BY0, BY0 + 0.005, za, zb)
        g.box(fr, BX0 + LEG, BX1 - LEG, BY1 - 0.005, BY1, za, zb)
        g.box(fr, BX0, BX0 + 0.005, BY0 + LEG, BY1 - LEG, za, zb)
        g.box(fr, BX1 - 0.005, BX1, BY0 + LEG, BY1 - LEG, za, zb)
    # shelf of three boards
    w = (BY1 - BY0 - 0.012) / 3
    for k in range(3):
        g.box(bd, BX0 + 0.006, BX1 - 0.006, BY0 + 0.006 + k * w + 0.002, BY0 + 0.006 + (k + 1) * w - 0.002, ZSH - 0.02, ZSH)
    if lod == 0:
        ft = P("bench_feet", "rubber")
        for sx in (BX0, BX1 - LEG):
            for sy in (BY0, BY1 - LEG):
                g.box(ft, sx - 0.005, sx + LEG + 0.005, sy - 0.005, sy + LEG + 0.005, 0.0, 0.006)
        parts.append(ft)
    return parts


# =============================================================================
# 2M112 drilling machine
# =============================================================================
def build_drill(spec):
    lod, sd = spec["lod"], spec["sides"]
    z = ZT
    x0, x1, y0, y1 = BASE
    bs = P("drill_base", "drill")
    parts = [bs]
    # base: a cast plate with a rim, a table with slots, a boss for the column at the back
    g.box(bs, x0, x1, y0, y1, z, z + 0.055, **(dict(r=0.006, seg=1) if lod == 0 else {}))
    g.box(bs, DX - 0.11, DX + 0.11, CY - 0.09, y1, z + 0.055, z + 0.15, **(dict(r=0.008, seg=1) if lod == 0 else {}))
    tb = P("drill_table", "drill_table")
    if lod == 2:
        g.box(tb, x0 + 0.02, x1 - 0.02, y0 + 0.02, CY - 0.10, z + 0.055, z + BASE_H)
    else:
        # three slots 14 wide at pitch 50 along Y: four table strips
        edges = [x0 + 0.025, DX - 0.057, DX - 0.043, DX - 0.007, DX + 0.007, DX + 0.043, DX + 0.057, x1 - 0.025]
        for a, b in zip(edges[::2], edges[1::2]):
            g.box(tb, a, b, y0 + 0.025, CY - 0.10, z + BASE_H - 0.012, z + BASE_H)
        g.box(tb, x0 + 0.025, x1 - 0.025, y0 + 0.025, CY - 0.10, z + 0.055, z + BASE_H - 0.012)
    parts.append(tb)
    # column; at the bottom a lifting screw under a bellows (as in the 2M112 photo)
    cl = P("drill_column", "column")
    g.cyl(cl, (DX, CY, z + (COL_Z0 + COL_Z1) / 2), "z", COL_R, COL_Z1 - COL_Z0, sd)
    parts.append(cl)
    if lod < 2:
        bl = P("drill_bellows", "rubber")
        if lod == 0:
            for k in range(7):
                g.cyl(bl, (DX, CY, z + 0.167 + k * 0.0334), "z", 0.058 if k % 2 == 0 else 0.052, 0.0334, sd)
        else:
            g.cyl(bl, (DX, CY, z + 0.15 + 0.117), "z", 0.056, 0.234, sd)
        parts.append(bl)
    # head
    hx0, hx1, hy0, hy1, hz0, hz1 = HEAD
    hd = P("drill_head", "drill")
    g.box(hd, hx0, hx1, hy0, hy1, z + hz0, z + hz1, **(dict(r=0.012, seg=2) if lod == 0 else {}))
    # quill housing under the head and the motor boss
    g.cyl(hd, (DX, SY, z + hz0 - 0.03), "z", 0.050, 0.06, sd)
    if lod < 2:
        g.box(hd, DX + 0.03, DX + 0.20, CY - 0.01, CY + 0.14, z + hz1 - 0.05, z + hz1)
    parts.append(hd)
    # quill: does not turn (the spindle is inside, build_spindle), goes down with the feed - up into the head
    ql = P("drill_quill", "column", group=SEL_FEED)
    g.cyl(ql, (DX, SY, z + (Q_Z0 + QUILL_TOP) / 2), "z", 0.030, QUILL_TOP - Q_Z0, sd)
    parts.append(ql)
    # motor at the rear right: a body with ribs, a terminal box
    mx, my, mr = MOTOR
    mt = P("drill_motor", "guard")
    g.cyl(mt, (mx, my, z + hz1 - 0.05 - 0.11), "z", mr, 0.22, sd)
    if lod == 0:
        for k in range(6):
            a = 2 * math.pi * (k + 0.5) / 6
            g.box(mt, -0.004, 0.004, 0.0, 0.012, 0.0, 0.17,
                  frame=g.Frame((mx + mr * math.cos(a), my + mr * math.sin(a), z + hz1 - 0.24),
                                (-math.sin(a), math.cos(a), 0), (math.cos(a), math.sin(a), 0), (0, 0, 1)))
        g.box(mt, mx + mr - 0.01, mx + mr + 0.04, my - 0.045, my + 0.045, z + hz1 - 0.16, z + hz1 - 0.08)
    parts.append(mt)
    # belt guard on top: from the spindle pulley to the motor pulley
    gd = P("drill_guard", "guard")
    poly = hull2([(DX, SY, GUARD_R), (mx, my, GUARD_R * 0.9)], 16 if lod == 0 else 8)
    g.prism(gd, poly, (0, 1), z + GUARD_Z0, z + GUARD_Z1)
    parts.append(gd)
    if lod == 0:
        # spindle shank above the guard and the guard bolts
        g.cyl(gd, (DX, SY, z + GUARD_Z1 + 0.012), "z", 0.018, 0.024, 10)
        bt = P("drill_bolts", "steel")
        for (bx, by) in ((DX - 0.07, SY - 0.07), (DX + 0.06, SY - 0.085), (mx + 0.07, my + 0.05)):
            g.cyl(bt, (bx, by, z + GUARD_Z1 + 0.003), "z", 0.008, 0.006, 6)
        parts.append(bt)
        # no depth stop (a ruler on the head face and a screw with nuts on the quill): it is not needed in the game,
        # and with the ozl_feed feed only the quill, spindle, chuck and drill move
        # "start/stop" push-button post on the head face at the right: a box and two buttons
        bx = hx1 - 0.045
        g.box(hd, bx - 0.025, bx + 0.025, hy0 - 0.032, hy0 + 0.002, z + hz0 + 0.06, z + hz0 + 0.15, r=0.004, seg=1)
        for zz, reg in ((z + hz0 + 0.125, "btn_green"), (z + hz0 + 0.085, "btn_red")):
            bn = P("drill_btn_" + reg[4:], reg)
            g.cyl(bn, (bx, hy0 - 0.036, zz), "y", 0.011, 0.010, 12)
            parts.append(bn)
        # chuck key on the base behind the vise: a shaft with a bit and a cross handle
        ky = P("chuck_key", "steel")
        kx0, ky0, kz = DX + 0.10, 0.02, z + BASE_H + 0.006
        rod(ky, (kx0, ky0 - 0.045, kz), (kx0, ky0 + 0.035, kz), 0.004, 8)
        rod(ky, (kx0 - 0.045, ky0 + 0.035, kz), (kx0 + 0.045, ky0 + 0.035, kz), 0.0045, 8)
        g.cyl(ky, (kx0, ky0 - 0.05, kz), "y", 0.006, 0.012, 10)
        parts.append(ky)
    if lod < 2:
        # feed wheel: a hub and three handles with balls
        fx, fy, fz = FEED
        fd = P("drill_feed", "steel", group=SEL_WHEEL)
        g.cyl(fd, (fx + 0.02, fy, z + fz), "x", 0.032, 0.04, sd)
        parts.append(fd)
        bl = P("drill_balls", "black", group=SEL_WHEEL)
        for k in range(3):
            a = math.radians(90 + 120 * k)
            tip = Vector((fx + 0.05, fy + 0.15 * math.cos(a), z + fz + 0.15 * math.sin(a)))
            rod(fd, (fx + 0.04, fy, z + fz), tip, 0.007, 6 if lod == 0 else 4)
            if lod == 0:
                lathe(bl, [(0.004, -0.018), (0.013, -0.012), (0.018, 0.0), (0.013, 0.012), (0.004, 0.018)], 10,
                      center=tuple(tip), axis="x")
            else:
                g.cyl(bl, tuple(tip), "x", 0.018, 0.03, 4)
        parts.append(bl)
    if lod == 0:
        # motor cord behind the bench
        cb = P("drill_cord", "wire_black")
        g.pipe(cb, spline([(mx + mr + 0.03, my, z + HEAD[5] - 0.12), (mx + mr + 0.05, BY1 + 0.02, z + HEAD[5] - 0.20),
                           (mx + mr + 0.06, BY1 + 0.04, z + 0.20), (mx + mr + 0.07, BY1 + 0.03, z - 0.15),
                           (mx + mr + 0.08, BY1 + 0.02, 0.25)], 3), 0.005, 6)
        parts.append(cb)
    return parts


def build_spindle(spec):
    """Bone ozl_work (turns): spindle nose, chuck with a knurled bushing and key sockets, three jaws, a
    drill with spiral flutes."""
    lod, sd = spec["lod"], spec["sides"]
    z = ZT
    sp = P("spindle", "chuck", group=SEL_SPINDLE)
    g.cyl(sp, (DX, SY, z + (CH_Z1 + Q_Z0) / 2), "z", 0.016, Q_Z0 - CH_Z1, 10 if lod == 0 else 6)
    parts = [sp]
    if lod == 0:
        # chuck body: a cone nose at the bottom, a knurled bushing, a ring with sockets
        lathe(sp, [(0.011, CH_Z0 - 0.004), (0.020, CH_Z0 + 0.004), (0.026, CH_Z0 + 0.018)], 20, center=(DX, SY, z))
        knurl(sp, DX, SY, z + CH_Z0 + 0.018, z + CH_Z1 - 0.016, 0.030, 18, 0.0018)
        lathe(sp, [(0.027, CH_Z1 - 0.016), (0.027, CH_Z1 - 0.004), (0.020, CH_Z1)], 20, center=(DX, SY, z), cap=True)
        kh = P("chuck_holes", "dark", group=SEL_SPINDLE)
        for k in range(3):
            a = 2 * math.pi * k / 3 + math.pi / 3
            f = g.Frame((DX + 0.0272 * math.cos(a), SY + 0.0272 * math.sin(a), z + CH_Z1 - 0.010),
                        (-math.sin(a), math.cos(a), 0), (0, 0, 1), (math.cos(a), math.sin(a), 0))
            g.box(kh, -0.0035, 0.0035, -0.0035, 0.0035, -0.001, 0.0008, frame=f)
        parts.append(kh)
        # jaws: come out of the nose and converge on the drill
        jw = P("chuck_jaws", "chuck", group=SEL_SPINDLE)
        for k in range(3):
            a = 2 * math.pi * k / 3
            top = Vector((DX + 0.011 * math.cos(a), SY + 0.011 * math.sin(a), z + CH_Z0 + 0.002))
            bot = Vector((DX + 0.0055 * math.cos(a), SY + 0.0055 * math.sin(a), z + CH_Z0 - 0.012))
            box_to(jw, top, bot, 0.004, 0.004, up=(math.cos(a), math.sin(a), 0))
        parts.append(jw)
        bt = P("drill_bit", "bit", group=SEL_SPINDLE)
        twist_drill(bt, DX, SY, z + BIT_Z0, z + CH_Z0 - 0.004, 0.003, 2.2, 14, 10)
        parts.append(bt)
    else:
        g.cyl(sp, (DX, SY, z + (CH_Z0 + CH_Z1) / 2), "z", 0.026, CH_Z1 - CH_Z0, sd, r2=0.030)
        if lod == 1:
            bt = P("drill_bit", "bit", group=SEL_SPINDLE)
            twist_drill(bt, DX, SY, z + BIT_Z0, z + CH_Z0, 0.003, 2.2, 4, 6)
            parts.append(bt)
    return parts


# =============================================================================
# Vise with the PDA board, parts of the PDA body, pin header, crocodile clips, wires
# =============================================================================
def build_vice(spec):
    lod, sd = spec["lod"], spec["sides"]
    z = ZT
    hw = V_W / 2
    vc = P("vice", "vice")
    gap = PCB[1] / 2
    # base, fixed jaw at the back, movable at the front
    g.box(vc, VX - hw - 0.01, VX + hw + 0.01, VY - 0.12, VY + 0.09, z + V_Z0, z + V_Z0 + 0.025)
    g.box(vc, VX - hw, VX + hw, VY + gap, VY + gap + 0.035, z + V_Z0 + 0.025, z + V_Z1)
    g.box(vc, VX - hw, VX + hw, VY - gap - 0.035, VY - gap, z + V_Z0 + 0.025, z + V_Z1)
    parts = [vc]
    if lod > 0:
        return parts
    st = P("vice_screw", "steel")
    g.cyl(st, (VX, VY - gap - 0.08, z + V_Z0 + 0.045), "y", 0.009, 0.09, 8)
    g.cyl(st, (VX, VY - gap - 0.13, z + V_Z0 + 0.045), "y", 0.016, 0.02, sd)
    rod(st, (VX - 0.075, VY - gap - 0.13, z + V_Z0 + 0.045), (VX + 0.075, VY - gap - 0.13, z + V_Z0 + 0.045), 0.005, 6)
    for s in (-1, 1):
        lathe(st, [(0.003, -0.009), (0.008, -0.005), (0.009, 0.0), (0.008, 0.005), (0.003, 0.009)], 8,
              center=(VX + s * 0.082, VY - gap - 0.13, z + V_Z0 + 0.045), axis="x")
    # jaw bolts
    for s in (-1, 1):
        for xx in (VX - 0.035, VX + 0.035):
            g.cyl(st, (xx, VY + s * (gap + 0.0365), z + V_Z1 - 0.02), "y", 0.005, 0.003, 6)
    parts.append(st)
    jw = P("vice_jaws", "steel")
    for s in (-1, 1):
        y = VY + s * gap
        g.box(jw, VX - hw + 0.005, VX + hw - 0.005, *sorted((y, y + s * 0.004)), z + V_Z1 - 0.04, z + V_Z1 + 0.001)
    parts.append(jw)
    return parts


def build_pda(spec):
    """PDA board flat in the jaws: QFP processor, memory, crystal, capacitors, a right-angle pin header at
    the right edge; the body halves beside it."""
    lod = spec["lod"]
    z = ZT + PCB_Z
    w, h, t = PCB
    pc = P("pda_pcb", "pcb")
    g.box(pc, VX - w / 2, VX + w / 2, VY - h / 2, VY + h / 2, z, z + t)
    parts = [pc]
    if lod == 2:
        return parts
    zt = z + t

    def at(cx, cy):
        return VX - w / 2 + cx * w, VY + h / 2 - cy * h
    ch = P("pda_chips", "chip")
    # ICs at the places of their traces in decal_pcb.png: (x, y fractions of the board, width, depth in fractions)
    chips = ((0.45, 0.47, 0.30, 0.22), (0.80, 0.30, 0.16, 0.16), (0.62, 0.76, 0.22, 0.10))
    for i, (cx, cy, cw, chh) in enumerate(chips):
        x, y = at(cx, cy)
        hx_, hy_ = cw * w / 2, chh * h / 2
        g.box(ch, x - hx_, x + hx_, y - hy_, y + hy_, zt, zt + 0.0014)
    parts.append(ch)
    if lod == 0:
        pn = P("pda_pins", "solder")
        for i, (cx, cy, cw, chh) in enumerate(chips):
            x, y = at(cx, cy)
            hx_, hy_ = cw * w / 2, chh * h / 2
            n = max(4, int(cw * w / 0.002))                    # lead pitch ~2 mm
            for k in range(n):
                px = x - hx_ + (k + 0.5) * 2 * hx_ / n
                for s in (-1, 1):
                    yy = y + s * hy_
                    g.box(pn, px - 0.00035, px + 0.00035, *sorted((yy, yy + s * 0.0016)), zt, zt + 0.0007)
            if i == 0:                                         # QFP: leads on the sides too
                m = max(4, int(chh * h / 0.002))
                for k in range(m):
                    py = y - hy_ + (k + 0.5) * 2 * hy_ / m
                    for s in (-1, 1):
                        xx = x + s * hx_
                        g.box(pn, *sorted((xx, xx + s * 0.0016)), py - 0.00035, py + 0.00035, zt, zt + 0.0007)
        parts.append(pn)
        # crystal (an oval can lying) and electrolytic capacitors
        cn = P("pda_crystal", "can")
        cxq, cyq = at(0.15, 0.75)
        g.box(cn, cxq - 0.0055, cxq + 0.0055, cyq - 0.0022, cyq + 0.0022, zt, zt + 0.0035, r=0.0015, seg=1)
        parts.append(cn)
        cp = P("pda_caps", "cap_blue")
        tops = P("pda_cap_tops", "can")
        for fx, fy in ((0.88, 0.70), (0.90, 0.18), (0.12, 0.25)):
            cx_, cy_ = at(fx, fy)
            g.cyl(cp, (cx_, cy_, zt + 0.003), "z", 0.0025, 0.006, 10)
            g.cyl(tops, (cx_, cy_, zt + 0.0062), "z", 0.0023, 0.0004, 10)
        parts += [cp, tops]
    # right-angle header: a plastic strip at the edge, pins toward +x
    hd = P("pda_header", "chip")
    g.box(hd, HDR_X - 0.0035, HDR_X - 0.001, HDR_Y[0] - 0.0016, HDR_Y[-1] + 0.0016, zt, zt + 0.0025)
    parts.append(hd)
    if lod == 0:
        pg = P("pda_header_pins", "pin_gold")
        for y in HDR_Y:
            g.box(pg, HDR_X - 0.003, HDR_X + 0.0065, y - 0.00032, y + 0.00032, HDR_Z - 0.00032, HDR_Z + 0.00032)
        parts.append(pg)
    # body halves: the back cover at the front of the base, the front one with the screen behind the machine
    for nm, (cx, cy), deg, dz in PDA_PARTS:
        fr = frame_z(cx, cy, deg, ZT + dz)
        pk = P(nm, "pda")
        g.box(pk, -0.0595, 0.0595, -0.0405, 0.0405, 0.0, 0.002, frame=fr)
        if lod == 0:
            for s in (-1, 1):
                g.box(pk, -0.0595, 0.0595, *sorted((s * 0.0405, s * 0.0375)), 0.002, 0.009, frame=fr)
            for s in (-1, 1):
                g.box(pk, *sorted((s * 0.0595, s * 0.0565)), -0.0375, 0.0375, 0.002, 0.009, frame=fr)
        parts.append(pk)
        if nm == "pda_front":
            gl = P("pda_front_glass", "pda_glass")
            g.box(gl, -0.030, 0.030, -0.005, 0.0345, 0.0018, 0.0028, frame=fr)
            parts.append(gl)
    return parts


def clip_frame(k):
    """Frame of crocodile clip k: origin - the jaw tips on the pin, u from the tip to the tail, n - the top
    of the clip (jaws open along n), v across."""
    pin, yaw, pitch, _, _ = CLIPS[k]
    a, p = math.radians(yaw), math.radians(pitch)
    u = Vector((math.cos(a) * math.cos(p), math.sin(a) * math.cos(p), -math.sin(p)))
    n = Vector((0, 0, 1)) - u * u.z
    n.normalize()
    v = n.cross(u)
    tip = Vector((HDR_X + 0.0045, HDR_Y[pin], HDR_Z))
    return g.Frame(tip, u, v, n)


def build_clips(spec):
    """50 mm crocodile clips on the header pins: two jaws from a strip with teeth near the tip, rivet,
    spring, soft cap on the tail; the wire leaves the cap."""
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    jaw = P("clip_jaws", "clip_jaw")
    parts.append(jaw)
    # profile of the upper jaw (a along, c up): the tips are closed on the pin, spread at the rivet, the tails
    # are spread by the spring
    prof = [(0.0, 0.0006), (0.008, 0.0009), (0.017, 0.0012), (0.023, 0.0028), (0.030, 0.0042), (0.042, 0.0066),
            (0.050, 0.0082)]
    for k in range(len(CLIPS)):
        fr = clip_frame(k)
        boot = P("clip_boot_%d" % k, CLIPS[k][3])
        for s in (1, -1):
            pts = [fr.p(a, 0.0, s * c) for a, c in (prof if lod == 0 else prof[::3])]
            g.sweep(jaw, pts, fr.v, 0.0003, 0.0030)
            if lod == 0:
                for i in range(5):                                  # teeth on the inner side
                    a0 = 0.0015 + 0.003 * i
                    c0 = s * 0.0006
                    tri = [(a0 - 0.0012, c0), (a0 + 0.0012, c0), (a0, c0 - s * 0.0007)]
                    g.prism(jaw, tri, (0, 2), -0.0027, 0.0027, frame=fr)
        if lod == 0:
            g.cyl(jaw, (0.0245, 0.0, 0.0), "y", 0.0012, 0.0074, 8, frame=fr)         # rivet
            g.cyl(jaw, (0.0275, 0.0, 0.0), "y", 0.0021, 0.0052, 8, frame=fr)         # spring
        # cap: from the rivet to the tail, the section grows and rounds off
        sec = [(0.027, 0.0040, 0.0044), (0.031, 0.0048, 0.0058), (0.042, 0.0050, 0.0064), (0.052, 0.0046, 0.0058),
               (0.058, 0.0032, 0.0036), (0.061, 0.0022, 0.0023)]
        if lod > 0:
            sec = sec[::2] + [sec[-1]]
        g.tube_var(boot, [fr.p(a, 0.0, 0.0) for a, _, _ in sec], [(rb, rc) for _, rb, rc in sec],
                   10 if lod == 0 else 6)
        parts.append(boot)
    return parts


def wire_route(k):
    """Wire of clip k: from the cap tail down onto the machine table, over the base edge onto the bench
    sheet and to the left edge of the card reader (soldered to the board)."""
    fr = clip_frame(k)
    s = 1 if k == 0 else -1
    tail = fr.p(0.061, 0.0, 0.0)
    out = fr.p(0.072, 0.0, -0.002)
    zb = ZT + BASE_H + 0.0022                                  # on the machine table
    zr = ZT + 0.055 + 0.0022                                    # on the base rim
    xe = BASE[1] - 0.025                                        # table edge (strips with slots)
    yb = VY - s * 0.012
    pts = [tuple(tail), tuple(out),
           (out.x + 0.004, out.y - s * 0.003, zb + 0.008),
           (xe - 0.003, yb + 0.022, zb),
           (BASE[1] - 0.008, yb + 0.034, zr + 0.002),
           (BASE[1] + 0.022, yb + 0.050, ZT + 0.0022),
           (-0.035, 0.048 - s * 0.006, ZT + 0.0022),
           (RDR[0] - 0.008, 0.088 - s * 0.006, ZT + 0.0022),
           (RDR[0] - 0.004, 0.090 - s * 0.006, ZT + RDR[4] * 0.6),
           (RDR_PCB[0] - 0.001, 0.092 - s * 0.006, ZT + RDR[4] + 0.0035),
           (RDR_PCB[0] + 0.006, 0.092 - s * 0.006, ZT + RDR[4] + 0.0012)]
    return pts


def build_wires(spec):
    """Crocodile wires to the card reader, a ribbon cable from the laptop parallel port to the reader
    connector, a 9 V battery clip, the laptop power cord behind the bench."""
    lod = spec["lod"]
    if lod == 2:
        return []
    z = ZT
    parts = []
    for k in range(len(CLIPS)):
        wr = P("wire_%d" % k, CLIPS[k][4])
        pts = wire_route(k)
        g.pipe(wr, spline(pts, 4) if lod == 0 else pts, 0.0021, 6 if lod == 0 else 4)
        parts.append(wr)
    # 10-wire ribbon (12.7 mm): from the DB-25 hood at the laptop rear (an adapter is in the hood), over the
    # sheet, across the front edge of the reader into the IDC plug
    xa = (DB25[0] + DB25[1]) / 2
    hood_y1 = LAP[3] + 0.045
    xp = 0.069                                                  # axis of the IDC plug on the reader
    zp = z + RDR[4] - 0.0014
    rb_pts = [(xa, hood_y1 - 0.004, z + 0.020), (xa - 0.004, hood_y1 + 0.010, z + 0.008),
              (xa - 0.012, hood_y1 + 0.024, z + 0.0007), (xp + 0.010, RDR[2] - 0.012, z + 0.0007),
              (xp, RDR[2] - 0.0025, z + 0.0016), (xp, RDR[2] - 0.0009, z + RDR[4] * 0.5),
              (xp, RDR[2] + 0.0008, z + RDR[4] - 0.002), (xp, RDR[2] + 0.006, zp + 0.010),
              (xp, RDR_PCB[2] + 0.0028, zp + 0.0115)]
    rb = P("ribbon", "ribbon")
    pts = spline(rb_pts, 3) if lod == 0 else rb_pts
    ribbon(rb, pts, (1, 0, 0), 0.00635, 0.0006)
    parts.append(rb)
    if lod == 0:
        # red wire along the ribbon edge (the first conductor)
        rr = P("ribbon_edge", "ribbon_red")
        ribbon(rr, [(q[0] - 0.0057, q[1], q[2]) for q in pts], (1, 0, 0), 0.0007, 0.00068)
        parts.append(rr)
    # DB-25 hood at the laptop rear, screws
    hd = P("db25_hood", "db_hood")
    g.box(hd, DB25[0] - 0.002, DB25[1] + 0.002, LAP[3] - 0.001, hood_y1, z + 0.010, z + 0.030,
          **(dict(r=0.003, seg=1) if lod == 0 else {}))
    parts.append(hd)
    if lod == 0:
        sw = P("db25_screws", "steel")
        for xx in (DB25[0] + 0.004, DB25[1] - 0.004):
            g.cyl(sw, (xx, LAP[3] + 0.012, z + 0.020), "y", 0.003, 0.016, 8)
        parts.append(sw)
        # 9 V clip on the battery: a black cover with snaps, two thin wires to the right edge of the board
        bx, by = 0.158, 0.052
        sn = P("snap", "black")
        g.box(sn, bx - 0.013, bx + 0.013, by - 0.008, by + 0.008, z + 0.0465, z + 0.0525, r=0.0015, seg=1)
        parts.append(sn)
        for j, reg in enumerate(("wire_red", "wire_black")):
            dy = (j - 0.5) * 0.006
            wr = P("snap_wire_%d" % j, reg)
            g.pipe(wr, spline([(bx - 0.012, by + dy, z + 0.050), (bx - 0.020, by + dy, z + 0.049),
                               (RDR[1] + 0.004, by + dy * 1.5, z + RDR[4] + 0.004),
                               (RDR_PCB[1] - 0.005, RDR_PCB[2] + 0.006 + dy, z + RDR[4] + 0.0012)], 3), 0.0011, 5)
            parts.append(wr)
        # laptop power cord behind the bench
        pw = P("wire_power", "wire_black")
        g.pipe(pw, spline([(LAP[1] - 0.02, LAP[3], z + 0.015), (LAP[1] + 0.04, LAP[3] + 0.05, z + 0.004),
                           (BX1 - 0.03, 0.10, z + 0.004), (BX1 + 0.012, 0.12, z - 0.05), (BX1 + 0.015, 0.14, 0.25)], 3),
               0.003, 6)
        parts.append(pw)
    return parts


# =============================================================================
# Laptop, card reader, boom box
# =============================================================================
def lid_frame():
    """The lid is open at 90 + LID_DEG: the face plane passes through the rear top of the body; c - toward
    the person."""
    t = math.radians(LID_DEG)
    return g.Frame((_LCX, LAP[3], ZT + LAP[4]), (1, 0, 0), (0, math.sin(t), math.cos(t)), (0, -math.cos(t), math.sin(t)))


def build_laptop(spec):
    lod = spec["lod"]
    x0, x1, y0, y1, h = LAP
    z = ZT
    lp = P("laptop", "lap")
    g.box(lp, x0, x1, y0, y1, z + 0.004, z + h, **(dict(r=0.005, seg=2) if lod == 0 else {}))
    g.box(lp, x0 + 0.006, x1 - 0.006, y0 + 0.006, y1 - 0.006, z, z + 0.004)
    parts = [lp]
    if lod < 2:
        kb = P("laptop_kbd", "kbd")
        g.box(kb, KBD[0], KBD[1], KBD[2], KBD[3], z + h - 0.001, z + h + 0.0006)
        parts.append(kb)
    if lod == 0:
        # keys: a narrower row of function keys, four main rows of 14, the bottom one small keys and a space bar
        ky = P("laptop_keys", "key")
        rows = [(15, 0.55)] + [(14, 1.0)] * 4 + [(None, 1.0)]
        hs = sum(r[1] for r in rows)
        yy = KBD[3] - 0.002
        W = KBD[1] - KBD[0] - 0.004
        for n, kf in rows:
            rh = (KBD[3] - KBD[2] - 0.004) * kf / hs
            xs = ([(0.0, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0)] if n is None
                  else [(c / n, (c + 1) / n) for c in range(n)])
            for a, b in xs:
                g.box(ky, KBD[0] + 0.002 + a * W + 0.001, KBD[0] + 0.002 + b * W - 0.001, yy - rh + 0.001, yy - 0.001,
                      z + h + 0.0006, z + h + 0.0036)
            yy -= rh
        parts.append(ky)
        # pointing stick between the keys and two buttons under the space bar
        tr = P("laptop_track", "track_red")
        g.cyl(tr, (_LCX, KBD[2] + 0.033, z + h + 0.004), "z", 0.0028, 0.006, 10)
        parts.append(tr)
        bn = P("laptop_buttons", "key")
        for s in (-1, 1):
            g.box(bn, _LCX + s * 0.004, _LCX + s * 0.024, KBD[2] - 0.016, KBD[2] - 0.006, z + h - 0.0005, z + h + 0.0012)
        parts.append(bn)
        pt = P("laptop_ports", "black")
        # ports at the rear: parallel (the ribbon plug is in it), serial, power; a grille on the right
        for a, b in ((DB25[0], DB25[1]), (0.16, 0.19), (0.30, 0.315)):
            g.box(pt, a, b, y1 - 0.0005, y1 + 0.0012, z + 0.012, z + 0.027)
        for k in range(7):
            yk = y0 + 0.05 + k * 0.012
            g.box(pt, x1 - 0.0005, x1 + 0.0010, yk, yk + 0.006, z + 0.012, z + 0.030)
        for sx in (x0 + 0.02, x1 - 0.03):                                                # rubber feet
            for sy in (y0 + 0.02, y1 - 0.03):
                g.box(pt, sx, sx + 0.012, sy, sy + 0.012, z - 0.0005, z + 0.0010)
        parts.append(pt)
    # lid: back part, screen frame, the screen recessed by SCR_IN (own texture - section screen)
    fr = lid_frame()
    hw = (x1 - x0) / 2
    ld = P("laptop_lid", "lap")
    g.box(ld, -hw, hw, 0.0, LID_H, -LID_T, -SCR_IN if lod < 2 else 0.0, frame=fr,
          **(dict(r=0.003, seg=1) if lod == 0 else {}))
    if lod < 2:
        sa0, sa1 = -SCR[0] / 2, SCR[0] / 2
        sb0, sb1 = SCR[2] - SCR[1] / 2, SCR[2] + SCR[1] / 2
        for a0, a1, b0, b1 in ((-hw, hw, 0.0, sb0), (-hw, hw, sb1, LID_H), (-hw, sa0, sb0, sb1), (sa1, hw, sb0, sb1)):
            g.box(ld, a0, a1, b0, b1, -SCR_IN, 0.0, frame=fr)
    parts.append(ld)
    sc = P("laptop_screen", "black", group=SEL_SCREEN, section="screen")
    cs = -SCR_IN + 0.0006 if lod < 2 else 0.0006
    vs = [sc.bm.verts.new(fr.p(a, b, cs)) for a, b in ((-SCR[0] / 2, SCR[2] - SCR[1] / 2), (SCR[0] / 2, SCR[2] - SCR[1] / 2),
                                                       (SCR[0] / 2, SCR[2] + SCR[1] / 2), (-SCR[0] / 2, SCR[2] + SCR[1] / 2))]
    sc.tag([face(sc, vs, fr.n)])
    sc.glass_frame = (fr, -SCR[0] / 2, SCR[0] / 2, SCR[2] - SCR[1] / 2, SCR[2] + SCR[1] / 2)
    parts.append(sc)
    if lod == 0:
        hg = P("laptop_hinge", "black")
        for s in (-1, 1):
            g.cyl(hg, (_LCX + s * (hw - 0.05), y1 - 0.006, z + h), "x", 0.008, 0.05, 10)
        parts.append(hg)
    return parts


def build_reader(spec):
    """Home-made card reader: a board on a block; a card socket, DIP-16, an IDC 2 x 5 connector with the
    ribbon plug, a capacitor, a dia. 5 LED (ozl_lamp), soldering of the wires, two screws."""
    lod = spec["lod"]
    x0, x1, y0, y1, h = RDR
    z = ZT
    wd = P("reader_block", "reader_wood")
    g.box(wd, x0, x1, y0, y1, z, z + h - 0.003, **(dict(r=0.003, seg=1) if lod == 0 else {}))
    parts = [wd]
    if lod == 2:
        return parts
    zp = z + h - 0.0014                                        # board top
    pc = P("reader_pcb", "reader_pcb")
    g.box(pc, RDR_PCB[0], RDR_PCB[1], RDR_PCB[2], RDR_PCB[3], z + h - 0.003, zp)
    parts.append(pc)
    ld = P("reader_led", "led", group=SEL_LAMP)
    lx, ly = RDR_PCB[1] - 0.010, RDR_PCB[3] - 0.008
    if lod == 0:
        lathe(ld, [(0.0028, 0.0), (0.0028, 0.0010), (0.0025, 0.0011), (0.0025, 0.0050), (0.0018, 0.0068),
                   (0.0007, 0.0076)], 12, center=(lx, ly, zp), cap=True)
    else:
        lathe(ld, [(0.0028, 0.0), (0.0025, 0.0050), (0.0007, 0.0076)], 6, center=(lx, ly, zp), cap=True)
    parts.append(ld)
    # card socket: a steel clip, a slot toward the front
    sl = P("reader_slot", "steel")
    g.box(sl, RDR_PCB[0] + 0.003, RDR_PCB[0] + 0.043, RDR_PCB[2] + 0.002, RDR_PCB[2] + 0.040, zp, zp + 0.0028)
    parts.append(sl)
    ic = P("reader_chips", "chip")
    g.box(ic, 0.072, 0.096, 0.081, 0.0875, zp + 0.0006, zp + 0.0040)                    # DIP-16
    g.box(ic, 0.058, 0.080, RDR_PCB[2] + 0.004, RDR_PCB[2] + 0.013, zp, zp + 0.0085)    # IDC 2 x 5 connector
    parts.append(ic)
    if lod == 0:
        lg = P("reader_legs", "solder")
        for k in range(8):
            xk = 0.0735 + k * 0.00305
            for s in (-1, 1):
                yk = 0.0843 + s * 0.0034
                g.box(lg, xk - 0.0004, xk + 0.0004, *sorted((yk, yk + s * 0.0012)), zp, zp + 0.0025)
        # solder: blobs at the wire ends and under the clip
        for xx, yy in ((RDR_PCB[0] + 0.006, 0.086), (RDR_PCB[0] + 0.006, 0.098), (RDR_PCB[1] - 0.005, RDR_PCB[2] + 0.003),
                       (RDR_PCB[1] - 0.005, RDR_PCB[2] + 0.009)):
            lathe(lg, [(0.0022, 0.0), (0.0016, 0.0009), (0.0006, 0.0014)], 8, center=(xx, yy, zp), cap=True)
        parts.append(lg)
        cp = P("reader_cap", "cap_blue")
        g.cyl(cp, (0.104, 0.084, zp + 0.0045), "z", 0.003, 0.009, 10)
        parts.append(cp)
        # ribbon plug in the connector: grey, with latches
        pl = P("reader_plug", "db_hood")
        g.box(pl, 0.0565, 0.0815, RDR_PCB[2] + 0.0025, RDR_PCB[2] + 0.0145, zp + 0.0085, zp + 0.0145)
        parts.append(pl)
        sw = P("reader_screws", "steel")
        for xx, yy in ((RDR_PCB[0] + 0.005, RDR_PCB[2] + 0.005), (RDR_PCB[1] - 0.005, RDR_PCB[3] - 0.005)):
            g.cyl(sw, (xx, yy, zp + 0.0004), "z", 0.0032, 0.0012, 8)
        parts.append(sw)
    return parts


def build_boombox(spec):
    lod, sd = spec["lod"], spec["sides"]
    x0, x1, y0, y1, h = BB
    z = ZT
    bb = P("boombox", "bb")
    g.box(bb, x0, x1, y0, y1, z, z + h, **(dict(r=0.012, seg=2) if lod == 0 else {}))
    parts = [bb]
    if lod == 2:
        return parts
    fc = P("boombox_face", "bb_face")
    g.box(fc, BB_FACE[0], BB_FACE[1], y0 - 0.002, y0 + 0.003, BB_FACE[2], BB_FACE[3])
    parts.append(fc)
    ld = P("boombox_led", "led", group=SEL_LAMP)
    if lod == 0:
        g.cyl(ld, (x1 - 0.115, y0 - 0.003, z + h - 0.013), "y", 0.0028, 0.004, 10)
    else:
        g.box(ld, x1 - 0.12, x1 - 0.11, y0 - 0.0035, y0, z + h - 0.016, z + h - 0.010)
    parts.append(ld)
    hd = P("boombox_handle", "black")
    ym = (y0 + y1) / 2
    hp = [(x0 + 0.09, ym, z + h), (x0 + 0.11, ym, z + h + 0.035), (x1 - 0.11, ym, z + h + 0.035),
          (x1 - 0.09, ym, z + h)]
    g.pipe(hd, spline(hp, 2) if lod == 0 else hp, 0.009, 8 if lod == 0 else 4)
    parts.append(hd)
    if lod == 0:
        an = P("boombox_antenna", "steel")
        rod(an, (x1 - 0.02, y1 - 0.02, z + h + 0.004), (x0 + 0.04, y1 - 0.02, z + h + 0.004), 0.003, 6)
        g.cyl(an, (x1 - 0.02, y1 - 0.02, z + h + 0.004), "x", 0.005, 0.012, 8)
        parts.append(an)
        # cassette keys on top at the face, two volume knobs
        kb = P("boombox_keys", "steel")
        for k in range(2):
            for j in range(5):
                xa = x0 + 0.145 + 0.075 * k + 0.0125 * j
                g.box(kb, xa, xa + 0.010, y0 + 0.006, y0 + 0.03, z + h, z + h + 0.005)
        parts.append(kb)
        kn = P("boombox_knobs", "black")
        for xx in (x0 + 0.05, x1 - 0.05):
            g.cyl(kn, (xx, y0 + 0.035, z + h + 0.007), "z", 0.012, 0.014, 14)
        parts.append(kn)
    return parts


# =============================================================================
# Small things: insulating tape, cigarettes, shelf
# =============================================================================
def build_props(spec):
    lod, sd = spec["lod"], spec["sides"]
    parts = []
    if lod == 0:
        tp = {}
        cr = P("tape_cores", "tape_core")
        for (cx, cy), dz, reg in TAPES:
            if reg not in tp:
                tp[reg] = P(reg, reg)
            g.cyl(tp[reg], (cx, cy, ZT + dz + 0.0095), "z", 0.030, 0.019, sd)
            g.cyl(cr, (cx, cy, ZT + dz + 0.0096), "z", 0.0195, 0.0194, 10)
        parts += list(tp.values()) + [cr]
        pk = P("packs", "carton", section="cigs")
        pk.fixed_uv = True
        for (cx, cy), deg, dz in PACKS:
            cig_pack(pk, frame_z(cx, cy, deg, ZT + dz))
        parts.append(pk)
    if lod < 2:
        # on the shelf: a box of junk
        fb = P("shelf_box", "card")
        g.box(fb, -0.40, -0.12, -0.18, 0.12, ZSH, ZSH + 0.20)
        parts.append(fb)
        if lod == 0:
            jk = P("shelf_junk", "junk")
            g.box(jk, -0.37, -0.16, -0.14, 0.08, ZSH + 0.20, ZSH + 0.24, r=0.015, seg=1)
            parts.append(jk)
    return parts


def cig_pack(part, fr, L=0.088, W=0.055, H=0.022):
    """A Chernomorka pack lying face up in frame fr (u along the pack, v across, n up): a box, each face has
    its UV on its own piece of the vanilla texture (CIGS_UV); the top of the face picture is toward +u."""
    bm = part.bm
    uvl = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    hl, hw = L / 2, W / 2
    # face: (corners in local a, b, c; normal; piece; (s, t) from (a, b, c) - fractions of the piece from the left
    # and from the bottom)
    sides = [
        ([(a, b, H) for a, b in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))], (0, 0, 1), "front",
         lambda a, b, c: ((hw - b) / W, (a + hl) / L)),
        ([(a, b, 0.0) for a, b in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))], (0, 0, -1), "front",
         lambda a, b, c: ((b + hw) / W, (a + hl) / L)),
        ([(a, -hw, c) for a, c in ((-hl, 0.0), (hl, 0.0), (hl, H), (-hl, H))], (0, -1, 0), "side",
         lambda a, b, c: (c / H, (a + hl) / L)),
        ([(a, hw, c) for a, c in ((-hl, 0.0), (hl, 0.0), (hl, H), (-hl, H))], (0, 1, 0), "side",
         lambda a, b, c: (1.0 - c / H, (a + hl) / L)),
        ([(-hl, b, c) for b, c in ((-hw, 0.0), (hw, 0.0), (hw, H), (-hw, H))], (-1, 0, 0), "end",
         lambda a, b, c: ((b + hw) / W, c / H)),
        ([(hl, b, c) for b, c in ((-hw, 0.0), (hw, 0.0), (hw, H), (-hw, H))], (1, 0, 0), "end",
         lambda a, b, c: ((hw - b) / W, c / H)),
    ]
    new = []
    for corners, nrm, rect, st in sides:
        vs = [bm.verts.new(fr.p(*q)) for q in corners]
        loc = {v: q for v, q in zip(vs, corners)}
        f = face(part, vs, fr.u * nrm[0] + fr.v * nrm[1] + fr.n * nrm[2])
        x0, x1, y0, y1 = CIGS_UV[rect]
        for lp in f.loops:
            s, t = st(*loc[lp.vert])
            lp[uvl].uv = (x0 + (x1 - x0) * s, 1.0 - (y1 - (y1 - y0) * t))
        new.append(f)
    part.tag(new)


def build_lod(spec):
    parts = build_bench(spec) + build_drill(spec) + build_spindle(spec) + build_vice(spec) + build_pda(spec)
    parts += build_clips(spec) + build_wires(spec) + build_laptop(spec) + build_reader(spec) + build_boombox(spec)
    parts += build_props(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """Convex components no thinner than 0.5 m: the bench, the machine and a block of the laptop with the
    boom box; the last two go down into the bench and overlap it."""
    metal = kx.PEN + r"\metalplate.rvmat"
    bench = kx.box_pts(BX0, BX1, BY0, BY1, 0.0, ZT)
    drill = kx.box_pts(DX - 0.22, DX + 0.29, BASE[2], BY1, ZT - 0.40, ZT + GUARD_Z1)
    desk = kx.box_pts(0.0, BX1, BY0, BY1, ZT - 0.30, ZT + 0.24)
    comps = [(bench, metal), (drill, metal), (desk, metal)]
    memory = {
        "invView": [(0.0, -2.6, 1.3)],
        "ce_center": [(0.0, 0.0, 0.78)],
        "ce_radius": [(1.0, 0.0, 0.78)],
        "ozl_work_axis": SPINDLE_AXIS,                    # bottom to top (see SPINDLE_AXIS)
        "ozl_feed_axis": [(DX, SY, ZT + HEAD[4]), (DX, SY, ZT + HEAD[4] - 1.0)],
        "ozl_wheel_axis": WHEEL_AXIS,                    # to the right (the angle sign is in WHEEL_ANIM)
    }
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 250.0, memory, bbox


# the first ones are for the --look preview: laptop and vise (also in "work": the screen, the head
# lowered), overview, crocodile clips, card reader, cigarette pack
SHOTS = [
    ("laptop", (0.05, -0.95, 1.05), (0.22, -0.05, ZT + 0.10), 34),
    ("vice", (-0.02, -0.55, 1.05), (DX + 0.04, SY, ZT + 0.16), 34),
    ("front", (-1.0, -2.5, 1.75), (0.0, 0.0, 0.95), 30),
    ("clips", (-0.05, -0.30, ZT + 0.30), (HDR_X + 0.03, VY, ZT + 0.14), 45),
    ("reader", (-0.10, 0.34, ZT + 0.30), (0.075, 0.065, ZT + 0.03), 40),
    ("packs", (0.58, -0.52, ZT + 0.26), (0.43, -0.25, ZT + 0.012), 40),
    ("drill", (-1.2, -1.1, 1.45), (DX, 0.0, ZT + 0.45), 30),
    ("right", (1.3, -1.0, 1.35), (0.20, 0.05, ZT + 0.10), 32),
    ("back", (1.2, 2.2, 1.6), (0.0, 0.0, 0.9), 30),
]

def _posed(place):
    """Preview of the "work" look: the feed wheel is turned over the whole travel by the engine rotation
    (engine_turn: the preview shows where the wheel goes in game while the head is lowered). kmodel can only
    shift (move), so the rotation is here, a wrapper over krender (as in M10); not exported to p3d - the
    model.cfg animation does that."""
    def wrapped(parts, *a, **kw):
        obs = place(parts, *a, **kw)
        if kw.get("move") is ON["move"]:
            o, ax, ang = engine_turn(WHEEL_AXIS, WHEEL_ANIM[1]["angle1"])
            for p, ob in zip(parts, obs):
                if p.group == SEL_WHEEL:
                    loc = Vector(ob.location)
                    cc = o + loc
                    ob.matrix_world = (Matrix.Translation(cc) @ Matrix.Rotation(ang, 4, ax) @ Matrix.Translation(-cc) @
                                       Matrix.Translation(loc))
        return obs
    return wrapped


krender.place_look = _posed(krender.place_look)
krender.place = _posed(krender.place)

M.look_shots = (6, 2)
M.run(build_lod, collision, SHOTS, row_step=1.4, row_shot=((1.4, -5.6, 1.8), (1.4, 0, 0.80)))
