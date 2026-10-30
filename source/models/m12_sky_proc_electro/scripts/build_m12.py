"""M12 - diagnostic case: Electronics Analyzer of the Clear Sky faction (OZL_Sky_Proc_Electro).
Analyzer: cargo 4x4, no modules (no module_1..3 points, as in M02, M04, M06, M08, M16).

    blender --background --python build_m12.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: system Python make_decals.py (oscilloscope screen "off" and "work" frames, scale,
stencil, board, dial, sign).

A Clear Sky field diagnostics stand made of real things:
- two wooden 7.62x54R ammo crates (packing for 880 rounds, two zinc cans) stacked - 488 x 353 x 151 mm,
  28 kg; unpainted wood with swamp mud at the bottom, black stencil without letters, lid battens, wooden
  handles on the ends, hasps, hinges, a seal;
- the case - a metal radio spare-parts box with a lid on a piano hinge (OST 5.8602-80, "metal boxes for
  spare parts": steel, waterproof, ~10.5-10.9 kg, insert sizes are multiples of 90 mm, inner length 450):
  body 500 x 360 x 200 mm, the lid 100 mm deep is raised vertically and held by two stops; modelled on the
  army test set in the AN/APM-282 case: a dark panel with connectors, toggles, lamps and a selector
  switch. Repainted Clear Sky light blue over grey primer;
- in the lid - the S1-94 oscilloscope (100 x 190 x 300 mm, screen 60 x 40 mm; as in M05/M06) on a steel
  shelf with gussets, held by a strap, and an analogue combined meter of the Ts4342 type (related to the
  Ts4315: scale window on top, aluminium panel with a selector switch, keys, terminals on the end face);
  there is no datasheet for the Ts4342, its size 215 x 115 x 80 mm follows the proportions of Ts4315
  photos and sellers' listings;
- in the body - a socket with an edge connector and the probe board in it (the analyzer's slot): the
  oscilloscope probe and the multimeter crocodile clips on the board's test points;
- a 6ST-55 battery on the ground - 242 x 175 x 190 mm (GOST 959, as in M11), wires with crocodile
  clips to the panel terminals.
Overall ~0.73 x 0.87 x 0.46 m: two crates stacked (0.30), the case body (0.21) and a lid as tall as the
case is deep (0.36) give 0.87.

Look: the "dayz" look; the body and lid are a stamped tray with rounded corners, a rolled rim and a bead,
on runners; "frog" latches (the case is open: the lever and the wire loop hang), folding handles on
brackets with rubber grips, piano hinge, riveted stops, a blank nameplate; crates - boards with chamfers,
nails, hasps with a slot and a loop, hinges, boss handles, the stencil is kept off the gap between the
boards; S1-94 - panel frame, rubber screen hood, switches with a skirt and a knob over them, knurled
knobs, toggles, BNC with a plug, louvres, a shelf on gussets, a strap with a buckle; Ts4342 (after the
Ts4315) - window frame, aluminium panel on rivets, selector with a toothed skirt, keys, corrector,
terminals with caps and plugs, a holder; the oscilloscope divider probe with a hook and a ground lead,
multimeter crocodile clips; panel - socket on lugs, board with ICs, capacitors, resistors and an LED,
terminals with ring lugs, ShR connectors with union nuts and caps on chains, fuses, a nameplate; battery
with ribs, plugs, conical terminals and handles, crocodile clips; cables and wires - smooth curves.
Small things are vanilla DayZ items as proxies (kvanilla): a screwdriver in spring clips in the lid, a
9 V battery on the panel, an electrician's kit with pliers on it on the ground, rags, insulating tape.

Work look (OZL_WorkFx.c of the mod, class OZL_Work in config.cpp): on the S1-94 screen the beam runs
along the sweep and draws damped oscillations (24 ozl_screen frames of 0.05 s, own texture, glow), the
Ts4342 needle trembles (bone ozl_needle on source ozl_needle, wobble), the oscilloscope mains lamp and the
green panel lamp are lit (ozl_lamp), the yellow panel lamp and the board LED blink (ozl_lamp_blink); the
red "alarm" lamp stays off. Needle: 0 is the scale zero, 1 is the end (90 degrees clockwise); the axis
points to the player, the angle sign is as in M08 (not verified in game).

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
import m12_bits as mb  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
XC = -0.10                                                  # axis of the case and crates along x
# 7.62x54R ammo crates: 488 x 353 x 151, the lid battens are included in the height
BW, BD, BH = 0.488, 0.353, 0.151
BATTEN = 0.015                                              # battens on the lid at the ends
CRATES = [(XC - 0.008, 0.006, 0.0), (XC + 0.005, -0.004, BH)]   # (centre x, centre y, bottom)
ZT = 2 * BH                                                 # top of the stack
# case: body 500 x 360 x 200, lid 100 deep, raised vertically (hinge at the back top)
CW, CD, LD = 0.50, 0.36, 0.10
CX0, CX1, CY0, CY1 = XC - CW / 2, XC + CW / 2, -CD / 2, CD / 2
ZC0 = ZT + 0.008                                            # bottom of the body (runners)
ZC1 = ZC0 + 0.200                                           # top of the body = hinge axis
WALL = 0.006
R_CASE = 0.016                                              # corner radius of the tray
ZPN = ZC1 - 0.034                                           # panel inside the body
LY0, LY1 = CY1, CY1 + LD                                    # lid: back from the hinge
LZ0 = ZC1 + 0.004                                           # bottom of the raised lid (above the body rim)
LZ1 = LZ0 + CD                                              # top of the raised lid
YLI = LY1 - 0.008                                           # inner wall of the lid (face toward -Y)
# S1-94 oscilloscope: 100 x 190 x 300, back to the lid, on a shelf
C94 = (XC - 0.215, XC - 0.115, ZC1 + 0.148, ZC1 + 0.148 + 0.190)   # x0, x1, z0, z1
YF94 = YLI - 0.300                                          # face of the oscilloscope panel
CRT94 = (C94[0] + 0.017, C94[1] - 0.017, C94[3] - 0.068, C94[3] - 0.024)
KNOBS_BIG = [(C94[0] + 0.025, C94[3] - 0.098), (C94[0] + 0.075, C94[3] - 0.098)]       # V/div, time/div
KNOBS_SMALL = [(C94[0] + 0.018, C94[3] - 0.128), (C94[0] + 0.050, C94[3] - 0.128), (C94[0] + 0.082, C94[3] - 0.128)]
TOGS94 = [(C94[0] + 0.030, C94[2] + 0.039, True), (C94[0] + 0.070, C94[2] + 0.039, False)]
BNC94 = (C94[0] + 0.018, C94[2] + 0.016)
LAMP94 = (C94[0] + 0.050, C94[2] + 0.016)
PWR94 = (C94[0] + 0.080, C94[2] + 0.016)
# Ts4342 type multimeter: 115 x 215 x 80, stands in the lid facing the player
MX0, MX1, MZ0, MZ1 = XC + 0.100, XC + 0.215, ZC1 + 0.090, ZC1 + 0.090 + 0.215
MYF = YLI - 0.080                                           # multimeter face
MWIN = (MX0 + 0.010, MX1 - 0.010, MZ1 - 0.030 - 0.063, MZ1 - 0.030)    # scale window
MSY = MYF + 0.003                                           # scale in the window (recessed)
PIVOT = Vector(((MWIN[0] + MWIN[1]) / 2, MSY - 0.0008, MWIN[2] + 0.063 * (1.0 - 0.94)))
NEEDLE_L = 0.063 * 0.72
MKZ = MZ0 + 0.065                                           # selector axis
MYM = (MYF + YLI) / 2                                       # terminals on the top end face
PLUG_AX = Vector((0.0, -0.87, 0.5))                         # plugs point forward at an angle (the lid is close)
# body panel: socket and board, toggles, lamps, selector, terminals, connectors, fuses
FIX = (XC - 0.200, XC - 0.020, -0.135, -0.100)              # socket x0, x1, y0, y1
PCB = (XC - 0.185, XC - 0.035, ZPN + 0.022, ZPN + 0.112)    # board x0, x1, z0, z1
PCB_Y = (FIX[2] + FIX[3]) / 2
PCB_F = PCB_Y - 0.0008                                      # face of the board
TP = {"scope": XC - 0.162, "red": XC - 0.115, "gnd": XC - 0.060}   # test points on the top edge
TP_Z = PCB[3] + 0.0055                                      # top of the test-point loop
CHIPS_X = (XC - 0.158, XC - 0.118, XC - 0.078)
CHIP_Z = PCB[2] + 0.050
CAPS = [(XC - 0.170, PCB[2] + 0.076), (XC - 0.050, PCB[2] + 0.024)]
RESISTORS = [(XC - 0.144, PCB[2] + 0.020), (XC - 0.104, PCB[2] + 0.020), (XC - 0.064, PCB[2] + 0.020)]
LED = (XC - 0.046, PCB[2] + 0.072)
TOGGLES = [(XC + 0.045 + 0.042 * i, -0.135, i in (0, 1)) for i in range(4)]     # x, y, lever "on"
GAL = (XC + 0.185, -0.030)                                  # selector
POSTS = [(XC + 0.205, -0.110, "cap_red"), (XC + 0.205, 0.080, "black")]   # battery power terminals
SOCKETS = [XC - 0.180, XC - 0.100, XC - 0.020]              # ShR connectors at the back
SOCK_Y = 0.110
FUSES = [(XC + 0.212, 0.140), (XC + 0.231, 0.140)]
PN_PLATE = (XC + 0.185, XC + 0.220, -0.168, -0.146)         # panel nameplate x0, x1, y0, y1
# lid: hook with a coil of wire, screwdriver in clips
HOOK = (XC + 0.025, LZ1 - 0.065)
SDX, SDZ = XC - 0.050, LZ1 - 0.174                          # axis and middle of the screwdriver
# 6ST-55 battery on the ground on the right: 175 (x) x 242 (y) x 190
BAX0, BAX1, BAY0, BAY1, BAZ = 0.190, 0.365, -0.175, 0.067, 0.190
BLID = BAZ - 0.004                                          # top of the lid (the terminals sit on it)
TERM = [((BAX0 + BAX1) / 2, BAY0 + 0.030), ((BAX0 + BAX1) / 2, BAY1 - 0.030)]
BCAP_X = (BAX0 + BAX1) / 2 + 0.035                          # row of plugs

LOD_SPECS = [
    dict(lod=0, bev=2, sides=16, nseg=2),
    dict(lod=1, bev=0, sides=8, nseg=1),
    dict(lod=2, bev=0, sides=6, nseg=0),
]

REGIONS = {
    "crate": ("crate", 0.6), "crate_front": ("crate_front", 0.8), "gap": ("gap", 0.3),
    "iron": ("iron", 1.4), "nail": ("nail", 3.0), "seal": ("seal", 2.0),
    "case": ("case", 0.6), "case_in": ("case_in", 0.6), "rubber": ("rubber", 0.8), "plate": ("plate", 2.0),
    "panel": ("panel", 1.4), "steel": ("steel", 1.2), "black": ("black", 1.5), "dark": ("dark", 1.0),
    "strap": ("strap", 1.0), "tape": ("tape", 2.0),
    "inst": ("inst", 0.8), "cream": ("cream", 1.6), "key": ("key", 2.0),
    "lamp_g": ("lamp_g", 2.0), "lamp_r": ("lamp_r", 2.0), "lamp_y": ("lamp_y", 2.0), "lamp_rf": ("lamp_rf", 2.0),
    "led": ("led", 3.0),
    "mm_case": ("mm_case", 1.0), "mm_plate": ("mm_plate", 1.6), "mm_scale": ("mm_scale", 5.0),
    "needle": ("needle", 2.0),
    "pcb": ("pcb", 5.0), "chip": ("chip", 4.0), "solder": ("solder", 4.0), "cap_blue": ("cap_blue", 3.0),
    "resistor": ("resistor", 4.0), "fixture": ("fixture", 1.6), "brass": ("brass", 2.0), "cap_red": ("cap_red", 1.6),
    "battery": ("battery", 1.0), "lead": ("lead", 1.5), "wire_red": ("wire_red", 1.0), "cable": ("cable", 0.8),
    "probe": ("probe", 2.0), "probe_cap": ("probe_cap", 2.5), "clip_jaw": ("clip_jaw", 3.0),
    "boot_red": ("boot_red", 2.5), "boot_black": ("boot_black", 2.5),
}

# =============================================================================
# Materials
# =============================================================================


def decal(name, center, size, y_face, eps=0.0012):
    return (os.path.join(WORK, name), "y", -1, ("x", "z"), center, size, (y_face - eps, y_face + eps))


def rect(name, r, y_face, eps=0.0012):
    x0, x1, z0, z1 = r
    return decal(name, ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0), y_face, eps)


def top_decal(name, center, size, z_face, eps=0.0012):
    """Decal on a horizontal face looking up, image top toward the back wall (+y)."""
    return (os.path.join(WORK, name), "z", 1, ("x", "y"), center, size, (z_face - eps, z_face + eps))


KINDS = kmats.std_kinds(floor_z=0.0)
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
WOOD = dict(color=kmats.lin((150, 120, 84)), seed=1.3, along="x", floor_z=0.0, dust=0.35, grime=0.9, knots=0.6)
# stencil: from 6 to 116 mm above the crate bottom (the gap between the face boards is at 0.44-0.49 of the
# image height)
STENCIL = [decal("decal_stencil.png", (cx, z0 + 0.061), (0.30, 0.110), cy - BD / 2) for cx, cy, z0 in CRATES]
# Clear Sky light-blue paint over the grey primer of the army box: chips down to the primer, rust in the
# chips and at the bottom (old equipment), panel and instruments clean
BLUE = dict(color=kmats.lin((150, 192, 214)), under=kmats.lin((96, 100, 102)), seed=2.8, gloss=0.35, spec=0.28,
            chip=(0.60, 0.66), rust=(0.70, 0.78), rust_low=0.8, floor_z=ZT, dust=0.25, grime=0.6)
PANEL_DECALS = [top_decal("decal_ring.png", GAL, (0.070, 0.070), ZPN),
                top_decal("decal_bolt.png", (XC + 0.175, 0.115), (0.034, 0.034), ZPN)]
MSCALE = [rect("decal_meter.png", MWIN, MSY, eps=0.001)]
PCBD = [rect("decal_pcb.png", PCB, PCB_F, eps=0.0006)]
KINDS.update({
    "crate": (kwood.build_wood, WOOD),
    "crate_front": (kwood.build_wood, dict(WOOD, decal_items=STENCIL)),
    "gap": ("flat", dict(color=kmats.lin((40, 32, 24)), gloss=0.05, spec=0.03)),
    "iron": ("paint", dict(color=kmats.lin((36, 38, 38)), under=kmats.lin((90, 70, 52)), seed=3.6, gloss=0.3, spec=0.3,
                           chip=(0.56, 0.62), rust=(0.60, 0.68), rust_low=1.0, floor_z=0.0, dust=0.3, grime=0.6)),
    "nail": ("steel", dict(seed=3.1, tone=0.24, along="z", gloss=0.4, spec=0.5, dust=0.3, grime=0.7)),
    "seal": ("paint", dict(color=kmats.lin((120, 124, 128)), under=kmats.lin((80, 82, 84)), seed=3.9, gloss=0.3,
                           spec=0.4, chip=(0.8, 0.9), rust=(0.99, 1.0), rust_low=0.0, dust=0.2, grime=0.3)),
    "case": ("paint", BLUE),
    "case_in": ("paint", dict(BLUE, color=kmats.lin((168, 204, 222)), seed=3.4, chip=(0.70, 0.76), rust=(0.99, 1.0),
                              rust_low=0.0, dust=0.12, grime=0.1)),
    "panel": ("paint", dict(CLEAN, color=kmats.lin((30, 32, 34)), under=kmats.lin((140, 140, 140)), seed=4.1, gloss=0.4,
                            spec=0.3, chip=(0.80, 0.86), dust=0.08, decal_items=PANEL_DECALS)),
    "plate": ("steel", dict(seed=8.6, tone=0.46, along="x", gloss=0.5, spec=0.6, dust=0.15, grime=0.3)),
    "dark": ("flat", dict(color=kmats.lin((14, 14, 15)), gloss=0.2, spec=0.1)),
    "strap": ("plastic", dict(color=kmats.lin((60, 66, 72)), gloss=0.08, spec=0.05, mottle=0.15, dust=0.3, grime=0.2,
                              scuff=(0.66, 0.74))),
    "tape": ("plastic", dict(color=kmats.lin((26, 26, 28)), gloss=0.5, spec=0.35, dust=0.2, scuff=(0.7, 0.8))),
    # S1-94: grey-blue body, cream front panel (as in M06)
    "inst": ("paint", dict(color=kmats.lin((112, 120, 126)), under=kmats.lin((60, 60, 62)), seed=3.3, gloss=0.42,
                           spec=0.32, chip=(0.70, 0.76), rust=(0.99, 1.0), rust_low=0.0, dust=0.15, grime=0.1)),
    "cream": ("paint", dict(color=kmats.lin((214, 206, 182)), under=kmats.lin((110, 108, 100)), seed=4.4, gloss=0.40,
                            spec=0.30, chip=(0.74, 0.80), rust=(0.99, 1.0), rust_low=0.0, dust=0.08, grime=0.08)),
    "key": ("plastic", dict(color=kmats.lin((218, 210, 188)), gloss=0.35, spec=0.25, dust=0.12, scuff=(0.7, 0.8))),
    # lamps: unlit - dark glass, "work" - bright; the "alarm" lamp (lamp_rf) never lights
    "lamp_g": ("flat", dict(color=kmats.lin((22, 60, 30)), gloss=0.85, spec=0.8)),
    "lamp_r": ("flat", dict(color=kmats.lin((70, 18, 16)), gloss=0.85, spec=0.8)),
    "lamp_y": ("flat", dict(color=kmats.lin((80, 52, 14)), gloss=0.85, spec=0.8)),
    "lamp_rf": ("flat", dict(color=kmats.lin((70, 18, 16)), gloss=0.85, spec=0.8)),
    "led": ("flat", dict(color=kmats.lin((70, 14, 12)), gloss=0.85, spec=0.8)),
    "lamp_g_on": ("flat", dict(color=kmats.lin((90, 255, 120)), gloss=0.85, spec=0.8)),
    "lamp_r_on": ("flat", dict(color=kmats.lin((255, 60, 40)), gloss=0.85, spec=0.8)),
    "lamp_y_on": ("flat", dict(color=kmats.lin((255, 176, 40)), gloss=0.85, spec=0.8)),
    "led_on": ("flat", dict(color=kmats.lin((255, 50, 36)), gloss=0.85, spec=0.8)),
    # multimeter: black case, aluminium panel, white scale, black needle
    "mm_case": ("plastic", dict(color=kmats.lin((22, 22, 23)), gloss=0.45, spec=0.35, dust=0.1, scuff=(0.70, 0.78))),
    "mm_plate": ("steel", dict(seed=7.4, tone=0.55, along="x", gloss=0.45, spec=0.55, dust=0.05, grime=0.05)),
    "mm_scale": ("paint", dict(CLEAN, color=kmats.lin((236, 234, 224)), gloss=0.5, spec=0.3, decal_items=MSCALE)),
    "needle": ("flat", dict(color=kmats.lin((20, 20, 20)), gloss=0.5, spec=0.4)),
    "pcb": ("paint", dict(CLEAN, color=kmats.lin((34, 92, 52)), gloss=0.6, spec=0.45, decal_items=PCBD)),
    "chip": ("plastic", dict(color=kmats.lin((22, 22, 24)), gloss=0.35, spec=0.25, dust=0.1, grime=0.1, scuff=(0.8, 0.9))),
    "solder": ("steel", dict(seed=7.7, tone=0.48, along="z", gloss=0.7, spec=0.7, dust=0.05, grime=0.2)),
    "cap_blue": ("plastic", dict(color=kmats.lin((34, 52, 118)), gloss=0.5, spec=0.35, dust=0.15, grime=0.2)),
    "resistor": ("plastic", dict(color=kmats.lin((176, 150, 110)), gloss=0.4, spec=0.3, dust=0.1)),
    "fixture": ("plastic", dict(color=kmats.lin((52, 40, 30)), gloss=0.5, spec=0.4, dust=0.05, mottle=0.1)),
    "brass": ("paint", dict(CLEAN, color=kmats.lin((196, 160, 80)), gloss=0.6, spec=0.6)),
    "battery": ("plastic", dict(color=kmats.lin((30, 30, 32)), gloss=0.35, spec=0.25, dust=0.5, grime=0.8,
                                scuff=(0.70, 0.78))),
    "lead": ("paint", dict(color=kmats.lin((96, 98, 100)), under=kmats.lin((170, 172, 170)), seed=6.1, gloss=0.25,
                           spec=0.3, chip=(0.70, 0.75), rust=(0.99, 1.0), rust_low=0.0, dust=0.3, grime=0.4, yellow=0.15)),
    "wire_red": ("plastic", dict(color=kmats.lin((168, 40, 30)), gloss=0.45, spec=0.3, dust=0.2)),
    "cable": ("plastic", dict(color=kmats.lin((28, 28, 30)), gloss=0.3, spec=0.2, dust=0.3, grime=0.3, scuff=(0.8, 0.9))),
    "probe": ("plastic", dict(color=kmats.lin((40, 44, 50)), gloss=0.4, spec=0.3, dust=0.05)),
    "probe_cap": ("plastic", dict(color=kmats.lin((150, 150, 146)), gloss=0.35, spec=0.25, dust=0.1)),
    # crocodile clips: nickel-plated steel; caps - soft PVC
    "clip_jaw": ("steel", dict(seed=8.1, tone=0.40, along="x", gloss=0.6, spec=0.7, dust=0.1, grime=0.5)),
    "boot_red": ("plastic", dict(color=kmats.lin((168, 30, 26)), gloss=0.35, spec=0.25, dust=0.3, grime=0.5,
                                 scuff=(0.66, 0.74))),
    "boot_black": ("plastic", dict(color=kmats.lin((26, 26, 28)), gloss=0.3, spec=0.2, dust=0.3, grime=0.5,
                                   scuff=(0.66, 0.74))),
})

# =============================================================================
# Model: looks, needle bone, DayZ items
# =============================================================================
OBJ, NAME = "m12_sky_proc_electro", "ozr_sky_proc_electro"
SEL_SCREEN, SEL_LAMP, SEL_BLINK, SEL_NEEDLE = "ozl_screen", "ozl_lamp", "ozl_lamp_blink", "ozl_needle"
LAMPS = [(XC + 0.060, -0.080, "lamp_g", SEL_LAMP), (XC + 0.100, -0.080, "lamp_y", SEL_BLINK),
         (XC + 0.140, -0.080, "lamp_rf", "body")]
CRT_FRAMES = 24                                             # make_decals.CRT_FRAMES (0.05 s each)
CRT = dict(off="decal_crt_off.png", frames=["decal_crt_f%02d.png" % i for i in range(CRT_FRAMES)], size=256,
           gloss=0.85)
NEEDLE_SWEEP = 90.0                                         # degrees of scale: phase 0 -> 1
NEEDLE_MID, NEEDLE_AMP, NEEDLE_PERIOD = 0.55, 0.05, 1.1     # in "work" it trembles around the middle of the scale
# "work" look preview: the needle is rotated (TURNS, below), not exported to p3d - the pose is set by the bone
ON_MOVE = {}
ON = dict(remap={"lamp_g": "lamp_g_on", "lamp_r": "lamp_r_on", "lamp_y": "lamp_y_on", "led": "led_on"},
          emissive=(1.0, 1.0, 1.0, 1.0), move=ON_MOVE)
TURNS = {SEL_NEEDLE: (tuple(PIVOT), (0.0, 1.0, 0.0), math.radians(NEEDLE_SWEEP * NEEDLE_MID))}
NEEDLE_ANIM = ("ozl_needle_turn", dict(type="rotation", source="ozl_needle", selection=SEL_NEEDLE,
                                       axis="ozl_needle_axis", memory=1, minValue=0.0, maxValue=1.0, angle0=0.0,
                                       angle1=math.radians(NEEDLE_SWEEP)))
DECOR = [
    # in the lid: screwdriver tip down in two spring clips
    kv.put("screwdriver", (SDX, YLI, SDZ), **kv.hung(-90.0)),
    # on the panel: a spare multimeter battery
    kv.put("battery9v", (XC + 0.175, 0.060, ZPN), **kv.flat(90.0)),
    # on the ground: electrician's kit left of the crates with pliers on it; rags and insulating tape right of
    # the battery
    kv.put("electrickit", (-0.48, 0.05, 0.0), **kv.flat(82.0)),
    kv.put("pliers", (-0.48, 0.05, kv.box("electrickit")[1][2] - kv.box("electrickit")[0][2]), **kv.flat(64.0)),
    kv.put("rags", (-0.55, -0.22, 0.0), **kv.flat(-20.0)),
    kv.put("ducttape", (0.46, -0.10, 0.0), **kv.flat(0.0)),
]


class Model(kmodel.Model):
    def panel_mats(self, on):
        """Work preview: the screen shows the frame with the beam at 3/4 of the sweep (frame 0 - beam at the
        left edge)."""
        out = super().panel_mats(on)
        if on:
            _, frames = self.panel_pngs("crt")
            out["crt"] = krender.panel_material(frames[17], glow=1.6, gloss=CRT["gloss"])
        return out


M = Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
          glass=dict(base=(0.82, 0.86, 0.88), clear=0.05, edge=0.10, smudge=0.06, streaks=0.03),
          selections=(SEL_SCREEN, SEL_LAMP, SEL_BLINK, SEL_NEEDLE), hidden=(SEL_SCREEN, SEL_LAMP, SEL_BLINK),
          states={"on": ON}, bones=((SEL_NEEDLE, ""),), animations=(NEEDLE_ANIM,), decor=DECOR,
          panels={"crt": CRT}, sources={"ozl_needle": dict(animPeriod=0.2)})
P = M.part
BOUNDS = {}


# --- preview: "work" pose with the needle rotated -----------------------------------------------
# krender places the look pose by a shift only (move); the needle needs a rotation. The wrapper is here
# (as in M04), the library is unchanged: the look is recognised by the same move dict (ON_MOVE).
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


# =============================================================================
# Small panel parts: each part is its own, identical ones share a place in the atlas (uv_name)
# =============================================================================
def U(part, region):
    return part.use(region, *REGIONS[region])


def use(region):
    return lambda part: U(part, region)


def bev(lod, r, seg):
    return dict(r=r, seg=seg) if lod == 0 else {}


def plane(c, out, up):
    """Frame of a panel part: origin c, n outward, v is the panel "up", u to the right (as a person sees it)."""
    d = Vector(out).normalized()
    v = Vector(up) - d * Vector(up).dot(d)
    v.normalize()
    return g.Frame(c, v.cross(d), v, d)


def FF(x, z, y=YF94):
    """Face of the instrument in the lid (looks toward -Y)."""
    return plane((x, y, z), (0.0, -1.0, 0.0), (0.0, 0.0, 1.0))


def FP(x, y, z=ZPN):
    """Body panel (looks up, "up" is toward the back wall)."""
    return plane((x, y, z), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0))


def knob(name, F, r, lod, angle=0.0, skirt=True, reg="black", cap=None, tag="f"):
    """Knob: skirt, knurled head, white mark on the end (angle - degrees clockwise from the panel "up");
    cap = (radius, height) - an aluminium knob on top (a switch with a smooth knob)."""
    c, d = F.o, F.n
    h = max(0.012, r * 1.6)
    kb = P(name, reg, uv_name="knob_%s%d%s%s" % (tag, round(r * 1000), "s" if skirt else "", "c" if cap else ""),
           uv_origin=tuple(c))
    if lod > 0:
        mb.lathe(kb, [(r, 0.0), (r, h), (0.0, h)], 6, c, d)
        return [kb]
    h0 = 0.0
    if skirt:
        mb.lathe(kb, [(r * 1.32, 0.0), (r * 1.32, 0.0026), (r * 1.08, 0.0052), (0.0, 0.0052)], 12, c, d)
        h0 = 0.0052
    mb.fluted(kb, c, d, r, min(0.0011, r * 0.12), 8 if r > 0.007 else 6, h0, h)
    top, rr = h, r
    if cap:
        cr, ch = cap
        U(kb, "steel")
        mb.lathe(kb, [(cr, h), (cr, h + ch - 0.0012), (cr * 0.85, h + ch), (0.0, h + ch)], 10, c, d)
        top, rr = h + ch, cr
    a = math.radians(angle)
    dirv = F.v * math.cos(a) + F.u * math.sin(a)
    fr = g.Frame(c + d * top, dirv.cross(d), dirv, d)
    pt = P(name + "_ptr", "key", uv_name="knob_ptr_" + tag, uv_origin=tuple(c))
    g.box(pt, -0.0011, 0.0011, rr * 0.22, rr * 0.86, 0.0, 0.0006, frame=fr)
    return [kb, pt]


def toggle(name, F, lod, up=True, big=False, tag="f"):
    """Toggle: hex nut, threaded bushing, lever with a thickening at the end."""
    if lod > 0:
        return []
    c, d = F.o, F.n
    p = P(name, "steel", uv_name="toggle_%s%s" % (tag, "b" if big else ""), uv_origin=tuple(c))
    rn = 0.0072 if big else 0.0062
    mb.lathe(p, [(rn, 0.0), (rn, 0.0030), (0.0, 0.0030)], 6, c, d, phase=0.5)
    mb.lathe(p, [(0.0034, 0.0030), (0.0034, 0.0052), (0.0, 0.0052)], 6, c, d)
    ln = 0.022 if big else 0.018
    dl = d * 0.94 + F.v * (0.34 if up else -0.34)
    mb.lathe(p, [(0.0022, 0.0), (0.0013, ln * 0.84), (0.0025, ln * 0.92), (0.0, ln)], 6, c + d * 0.0050, dl)
    return [p]


def lamp(name, F, reg, lod, group="body", s=1.0, tag="f"):
    """Signal lamp: steel rim and a dome lens (the lens is what the "work" look highlights)."""
    c, d = F.o, F.n
    lens = P(name, reg, group=group, uv_name="lamp_%s_%s%d" % (tag, reg, round(s * 10)), uv_origin=tuple(c))
    if lod > 0:
        mb.lathe(lens, [(0.0080 * s, 0.0), (0.0080 * s, 0.010 * s), (0.0, 0.010 * s)], 6, c, d)
        return [lens]
    rim = P(name + "_rim", "steel", uv_name="lamp_rim_%s%d" % (tag, round(s * 10)), uv_origin=tuple(c))
    mb.lathe(rim, [(0.0108 * s, 0.0), (0.0108 * s, 0.0038 * s), (0.0084 * s, 0.0058 * s)], 8, c, d)
    mb.lathe(lens, [(0.0080 * s, 0.0040 * s), (0.0080 * s, 0.0068 * s), (0.0058 * s, 0.0104 * s), (0.0, 0.0120 * s)],
             10, c, d)
    return [rim, lens]


def screw(name, c, axis, r, tag):
    s = P(name, "steel", uv_name="screw_%s%d" % (tag, round(r * 10000)), uv_origin=tuple(c))
    mb.dome(s, c, axis, r)
    return [s]


def cable(name, region, pts, r, lod, k=2):
    """Cable as a smooth curve through the points (middle LOD - polyline, far LOD - no cables); thick - 6
    faces, thin - 5."""
    if lod == 2:
        return []
    c = P(name, region)
    g.pipe(c, mb.spline(pts, k) if lod == 0 else [pts[i] for i in range(0, len(pts), 2)] + [pts[-1]] * (len(pts) % 2 == 0),
           r, (6 if r >= 0.004 else 5) if lod == 0 else 4)
    return [c]


def croc_frame(tip, u, across):
    """Crocodile clip frame: origin at the jaw tips, u toward the tail, the jaws close across `across`."""
    u = Vector(u).normalized()
    v = Vector(across) - u * Vector(across).dot(u)
    v.normalize()
    return g.Frame(tip, u, v, u.cross(v))


# =============================================================================
# Ammo crates
# =============================================================================
def crate(name, cx, cy, z0, lod):
    """7.62x54R crate: face and back boards full length (nails go into the ends), end boards between them
    with boss handles, lid of three boards, battens at the ends; the face is two boards with a gap,
    chamfers at the edges. Far LOD - a box."""
    x0, x1, y0, y1 = cx - BW / 2, cx + BW / 2, cy - BD / 2, cy + BD / 2
    h = BH - BATTEN
    T, E, gap = 0.018, 0.022, 0.005
    zm = z0 + h * 0.48
    zt = z0 + h - T                                          # underside of the lid boards
    if lod == 2:
        b = P(name, "crate")
        g.box(b, x0, x1, y0, y1, z0, z0 + BH)
        return [b]
    fr = P(name + "_front", "crate_front")
    sd = P(name + "_boards", "crate")
    bt = P(name + "_battens", "crate")
    parts = [fr, sd, bt]
    b1 = bev(lod, 0.0018, 1)
    if lod == 1:
        g.box(fr, x0, x1, y0, y0 + 0.02, z0, z0 + h)
        g.box(sd, x0, x1, y0 + 0.02, y1, z0, z0 + h)
    else:
        core = P(name + "_core", "gap")
        g.box(core, x0 + 0.004, x1 - 0.004, y0 + 0.004, y1 - 0.004, z0 + 0.002, z0 + h - 0.003)
        parts.append(core)
        for za, zb in ((z0, zm - gap / 2), (zm + gap / 2, zt)):
            g.box(fr, x0, x1, y0, y0 + T, za, zb, **b1)
            g.box(sd, x0, x1, y1 - T, y1, za, zb)
        for xa in (x0, x1 - E):
            g.box(sd, xa, xa + E, y0 + T, y1 - T, z0, zt)
        tw = (BD - 2 * gap) / 3
        for j in range(3):
            ya = y0 + j * (tw + gap)
            g.box(fr if j == 0 else sd, x0, x1, ya, ya + tw, zt, z0 + h, **(b1 if j == 0 else {}))
    # battens (covered above by the upper crate or the case) - no chamfers
    for xa in (x0, x1 - 0.05):
        g.box(bt, xa, xa + 0.05, y0, y1, z0 + h, z0 + BH)
    # handles on the ends: a boss, a grip hollowed out underneath
    for xx, s in ((x0, -1), (x1, 1)):
        g.box(bt, *sorted((xx, xx + s * 0.024)), cy - 0.09, cy + 0.09, z0 + h * 0.55, z0 + h * 0.85, **b1)
        if lod == 0:
            g.box(bt, *sorted((xx, xx + s * 0.012)), cy - 0.11, cy + 0.11, z0 + h * 0.25, z0 + h * 0.55)
    if lod > 0:
        return parts
    # face nails - into the end boards, two per board
    k = 0
    for xx in (x0 + E / 2, x1 - E / 2):
        for za, zb in ((z0, zm - gap / 2), (zm + gap / 2, zt)):
            for f in (0.28, 0.72):
                c = (xx, y0, za + (zb - za) * f)
                nl = P("%s_nail%d" % (name, k), "nail", uv_name="nail_y", uv_origin=c)
                mb.lathe(nl, [(0.0032, 0.0), (0.0024, 0.0007), (0.0, 0.0009)], 5, c, (0, -1, 0))
                parts.append(nl)
                k += 1
    parts += crate_iron(name, cx, y0, z0 + h)
    return parts


def crate_iron(name, cx, y0, zt):
    """Hasps on the face: hinge knuckle on the lid edge, a strap down with a slot, a staple through it
    (the hinges at the back and the leaves on the lid are hidden - not built)."""
    ir = P(name + "_iron", "iron", uv_name="crate_iron", uv_origin=(cx, y0, zt))
    sl = P(name + "_slots", "dark", uv_name="crate_slots", uv_origin=(cx, y0, zt))
    for dx in (-0.15, 0.15):
        xs = cx + dx
        mb.lathe(ir, [(0.0, -0.014), (0.0042, -0.014), (0.0042, 0.014), (0.0, 0.014)], 6, (xs, y0 - 0.0006, zt - 0.0006),
                 (1, 0, 0))
        g.box(ir, xs - 0.012, xs + 0.012, y0 - 0.0058, y0 - 0.0030, zt - 0.072, zt - 0.003)
        g.box(sl, xs - 0.0042, xs + 0.0042, y0 - 0.0062, y0 - 0.0055, zt - 0.061, zt - 0.045)
        mb.u_handle(ir, (xs - 0.0028, y0, zt - 0.053), (xs + 0.0028, y0, zt - 0.053), (0, -1, 0), 0.0105, 0.0018,
                    0.0011, 4, 1)
    return [ir, sl]


def build_crates(spec):
    lod = spec["lod"]
    parts = []
    for i, (cx, cy, z0) in enumerate(CRATES):
        parts += crate("crate%d" % i, cx, cy, z0, lod)
    if lod == 0:
        # seal on a wire at the left hasp of the upper crate
        cx, cy, z0 = CRATES[1]
        xs, y0, zt = cx - 0.15, cy - BD / 2, z0 + BH - BATTEN
        sl = P("crate_seal", "seal")
        g.pipe(sl, mb.spline([(xs + 0.0028, y0 - 0.011, zt - 0.053), (xs + 0.006, y0 - 0.012, zt - 0.062),
                              (xs + 0.008, y0 - 0.0115, zt - 0.072)], 2), 0.0007, 4)
        mb.lathe(sl, [(0.0, -0.0019), (0.0060, -0.0019), (0.0066, 0.0), (0.0060, 0.0019), (0.0, 0.0019)], 8,
                 (xs + 0.009, y0 - 0.0115, zt - 0.080), (0, -1, 0))
        parts.append(sl)
    return parts


# =============================================================================
# Case: body and lid trays, panel, hardware
# =============================================================================
def body_frame():
    """Body plan: a - x from the case axis, b - y; c - up from the bottom of the body."""
    return g.Frame((XC, 0.0, ZC0), (1, 0, 0), (0, 1, 0), (0, 0, 1))


def lid_frame():
    """Raised lid plan: a - x, b - z from the middle; c - from the back wall (lid bottom) toward the player."""
    return g.Frame((XC, LY1, (LZ0 + LZ1) / 2), (1, 0, 0), (0, 0, 1), (0, -1, 0))


# tray profile (d - offset outward from the contour, c - height): rounded bottom, bead, rolled rim, inner
# wall; the number is how many first segments are outside (the rest are inside)
BODY_PROF = {
    0: ([(-0.008, 0.0), (-0.0012, 0.0030), (0.0, 0.0075), (0.0, 0.082), (0.0024, 0.0865),
         (0.0024, 0.0975), (0.0, 0.102), (0.0, 0.1955), (0.0016, 0.1975), (0.0016, 0.2015), (0.0, 0.2035),
         (-0.0035, 0.2035), (-WALL, 0.2005), (-WALL, ZPN - ZC0)], 12),
    1: ([(-0.008, 0.0), (0.0, 0.006), (0.0, 0.198), (0.0016, 0.2015), (-WALL, 0.2015), (-WALL, ZPN - ZC0)], 4),
    2: ([(0.0, 0.0), (0.0, 0.200), (-WALL, 0.200), (-WALL, ZPN - ZC0)], 2),
}
LID_PROF = {
    0: ([(-0.010, 0.0), (-0.004, 0.0009), (-0.0010, 0.0035), (0.0, 0.0075), (0.0, 0.0955), (0.0016, 0.0975),
         (0.0016, 0.1015), (0.0, 0.1035), (-0.0035, 0.1035), (-WALL, 0.1005), (-0.0064, 0.0925), (-WALL, 0.008)],
        ["case"] * 9 + ["rubber", "case_in"]),
    1: ([(-0.008, 0.0), (0.0, 0.006), (0.0, 0.098), (0.0016, 0.1015), (-WALL, 0.1015), (-WALL, 0.008)],
        ["case"] * 4 + ["case_in"]),
    2: ([(0.0, 0.0), (0.0, 0.100), (-WALL, 0.100), (-WALL, 0.008)], ["case"] * 2 + ["case_in"]),
}


def build_case(spec):
    lod, nseg = spec["lod"], spec["nseg"]
    parts = []
    body = P("case_body", "case")
    prof, n_out = BODY_PROF[lod]
    mb.loop_sweep(body, body_frame(), mb.rrect_loop(-CW / 2, CW / 2, -CD / 2, CD / 2, R_CASE, nseg), prof,
                  seg_use=[use("case")] * n_out + [use("case_in")] * (len(prof) - 1 - n_out), cap0=use("case"))
    parts.append(body)
    pn = P("case_panel", "panel")
    mb.rrect_prism(pn, body_frame(), -CW / 2 + WALL, CW / 2 - WALL, -CD / 2 + WALL, CD / 2 - WALL, R_CASE - WALL, nseg,
                   ZPN - 0.004 - ZC0, ZPN - ZC0)
    parts.append(pn)
    if lod == 2:
        return parts
    rn = P("case_runners", "case")
    for y in (-0.12, 0.12):
        g.box(rn, CX0 + 0.035, CX1 - 0.035, y - 0.016, y + 0.016, ZT, ZC0 + 0.002)
    parts.append(rn)
    for i, dx in enumerate((-0.15, 0.15)):
        parts += latch("case_latch%d" % i, XC + dx, lod)
    for xe, s in ((CX0, -1), (CX1, 1)):
        parts += end_handle("case_handle_%s" % ("l" if s < 0 else "r"), xe, s, lod)
    parts += build_hinge(lod) + build_stays(lod)
    if lod == 0:
        # blank nameplate on the face between the latches
        dp = P("case_plate", "plate")
        g.box(dp, XC - 0.040, XC + 0.040, CY0 - 0.0012, CY0 + 0.001, ZC1 - 0.082, ZC1 - 0.042, r=0.0008, seg=1)
        parts.append(dp)
        for i, (sx_, sz) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
            parts += screw("case_plate_r%d" % i, (XC + sx_ * 0.035, CY0 - 0.0012, ZC1 - 0.062 + sz * 0.015), (0, -1, 0),
                           0.0018, "y")
        # panel screws at the corners
        for i, (x, y) in enumerate(((CX0 + 0.016, CY0 + 0.016), (CX1 - 0.016, CY0 + 0.016), (CX0 + 0.016, CY1 - 0.016),
                                    (CX1 - 0.016, CY1 - 0.016))):
            parts += screw("panel_screw%d" % i, (x, y, ZPN), (0, 0, 1), 0.0040, "z")
    return parts


def latch(name, xs, lod):
    """Frog latch on the face: base on four rivets, lugs with a pin; the case is open - the lever hangs
    down, the wire loop dangles below it."""
    y0 = CY0
    lt = P(name, "steel", uv_name="latch", uv_origin=(xs, y0, ZC1))
    g.box(lt, xs - 0.020, xs + 0.020, y0 - 0.0025, y0 + 0.001, ZC1 - 0.062, ZC1 - 0.026, **bev(lod, 0.0012, 1))
    if lod > 0:
        g.box(lt, xs - 0.011, xs + 0.011, y0 - 0.010, y0 - 0.0025, ZC1 - 0.080, ZC1 - 0.034)
        return [lt]
    for sx_ in (-1, 1):
        g.box(lt, xs + sx_ * 0.0125 - 0.0018, xs + sx_ * 0.0125 + 0.0018, y0 - 0.0105, y0 - 0.0025, ZC1 - 0.042,
              ZC1 - 0.029)
        mb.dome(lt, (xs + sx_ * 0.015, y0 - 0.0025, ZC1 - 0.057), (0, -1, 0), 0.0022)
    mb.lathe(lt, [(0.0, -0.016), (0.0022, -0.016), (0.0022, 0.016), (0.0, 0.016)], 6, (xs, y0 - 0.0075, ZC1 - 0.035),
             (1, 0, 0))
    g.sweep(lt, mb.spline([(xs, y0 - 0.0075, ZC1 - 0.035), (xs, y0 - 0.0102, ZC1 - 0.050), (xs, y0 - 0.0112, ZC1 - 0.066),
                           (xs, y0 - 0.0092, ZC1 - 0.079)], 2), (1, 0, 0), 0.0011, 0.0105)
    mb.u_handle(lt, (xs - 0.0108, y0 - 0.0118, ZC1 - 0.049), (xs + 0.0108, y0 - 0.0118, ZC1 - 0.049), (0.0, -0.22, -1.0),
                0.046, 0.004, 0.0013, 4, 1)
    return [lt]


def end_handle(name, xe, s, lod):
    """Folding handle on the end (s = -1 left, 1 right): two brackets with lugs on rivets, a rod hanging
    down, rubber grip."""
    zc = ZC1 - 0.040
    hb = P(name, "steel", uv_name="handle_" + ("l" if s < 0 else "r"), uv_origin=(xe, 0.0, zc))
    for yy in (-0.055, 0.055):
        g.box(hb, *sorted((xe, xe + s * 0.0025)), yy - 0.011, yy + 0.011, zc - 0.016, zc + 0.012)
        g.box(hb, *sorted((xe + s * 0.0025, xe + s * 0.011)), yy - 0.004, yy + 0.004, zc - 0.006, zc + 0.006)
        if lod == 0:
            mb.dome(hb, (xe + s * 0.0025, yy, zc - 0.0115), (s, 0, 0), 0.0024)
    out = Vector((s * 0.18, 0.0, -1.0))
    mb.u_handle(hb, (xe + s * 0.0075, -0.055, zc), (xe + s * 0.0075, 0.055, zc), out, 0.062, 0.010, 0.0042,
                6 if lod == 0 else 4, lod)
    parts = [hb]
    if lod == 0:
        gr = P(name + "_grip", "rubber", uv_name="handle_grip", uv_origin=(xe, 0.0, zc))
        c = Vector((xe + s * 0.0075, 0.0, zc)) + out.normalized() * 0.062
        mb.lathe(gr, [(0.0, -0.040), (0.0060, -0.040), (0.0075, -0.034), (0.0075, 0.034), (0.0060, 0.040), (0.0, 0.040)],
                 8, tuple(c), (0, 1, 0))
        parts.append(gr)
    return parts


def build_hinge(lod):
    """Piano hinge at the back: knuckles on the pin, a leaf riveted on the back wall of the body (under the
    rim), a leaf under the bottom of the raised lid."""
    hg = P("case_hinge", "case")
    L = CW - 0.06
    yk, zk = CY1 + 0.0045, ZC1 + 0.0005
    if lod == 0:
        n = 7
        seg = L / n
        for i in range(n):
            xa = CX0 + 0.03 + i * seg + 0.0006
            mb.lathe(hg, [(0.0, 0.0), (0.0042, 0.0), (0.0042, seg - 0.0012), (0.0, seg - 0.0012)], 6, (xa, yk, zk), (1, 0, 0))
        g.box(hg, CX0 + 0.03, CX1 - 0.03, CY1 + 0.0016, CY1 + 0.0031, ZC1 - 0.028, zk - 0.002)
        g.box(hg, CX0 + 0.03, CX1 - 0.03, yk + 0.002, LY0 + 0.030, LZ0 - 0.0016, LZ0)
    else:
        mb.lathe(hg, [(0.0, 0.0), (0.0042, 0.0), (0.0042, L), (0.0, L)], 5, (CX0 + 0.03, yk, zk), (1, 0, 0))
    return [hg]


def build_stays(lod):
    """Lid stops at the sides: a steel strip between the brackets on the body wall and the lid wall, the
    pins are rivets with a washer."""
    st = P("case_stays", "steel")
    for xe, s in ((CX0, -1), (CX1, 1)):
        a = Vector((xe + s * 0.0045, 0.115, ZC1 - 0.028))
        b = Vector((xe + s * 0.0045, LY0 + 0.042, LZ0 + 0.150))
        mb.box_to(st, a, b, 0.012, 0.0025, up=(s, 0, 0))
        if lod == 0:
            for q in (a, b):
                g.box(st, *sorted((xe, xe + s * 0.0030)), q.y - 0.009, q.y + 0.009, q.z - 0.009, q.z + 0.009)
                mb.dome(st, tuple(q + Vector((s * 0.00125, 0.0, 0.0))), (s, 0, 0), 0.0045, 6)
    return [st]


def build_lid(spec):
    """The lid is raised vertically: tray with rounded corners, a rim with a rubber seal, lighter inside;
    outside - two beads and a folding handle, on top (the former front edge) - the mating latch hooks."""
    lod, nseg = spec["lod"], spec["nseg"]
    lid = P("lid", "case")
    prof, regs = LID_PROF[lod]
    mb.loop_sweep(lid, lid_frame(), mb.rrect_loop(-CW / 2, CW / 2, -CD / 2, CD / 2, R_CASE, nseg), prof,
                  seg_use=[use(r) for r in regs], cap0=use("case"), cap1=use("case_in"))
    parts = [lid]
    if lod == 2:
        return parts
    # outside (at the back, not visible to the player): two beads and a folding handle - simple solids
    rb = P("lid_ribs", "case")
    for zz in (LZ0 + 0.095, LZ1 - 0.095):
        g.box(rb, CX0 + 0.035, CX1 - 0.035, LY1 - 0.002, LY1 + 0.0028, zz - 0.009, zz + 0.009)
    parts.append(rb)
    hw = P("lid_hardware", "steel")
    zc = (LZ0 + LZ1) / 2 + 0.030
    for xx in (XC - 0.065, XC + 0.065):
        g.box(hw, xx - 0.011, xx + 0.011, LY1, LY1 + 0.003, zc - 0.012, zc + 0.012)
        g.box(hw, xx - 0.004, xx + 0.004, LY1 + 0.003, LY1 + 0.011, zc - 0.006, zc + 0.006)
    mb.u_handle(hw, (XC - 0.065, LY1 + 0.0075, zc), (XC + 0.065, LY1 + 0.0075, zc), (0.0, 0.2, -1.0), 0.055, 0.010,
                0.0045, 6 if lod == 0 else 4, 1)
    # mating latch hooks on the top edge
    for dx in (-0.15, 0.15):
        xs = XC + dx
        g.box(hw, xs - 0.013, xs + 0.013, LY0 + 0.0065, LY0 + 0.026, LZ1, LZ1 + 0.0024)
        mb.lathe(hw, [(0.0, -0.010), (0.0030, -0.010), (0.0030, 0.010), (0.0, 0.010)], 6 if lod == 0 else 5,
                 (xs, LY0 + 0.0045, LZ1 + 0.0042), (1, 0, 0))
    parts.append(hw)
    return parts


# =============================================================================
# Instruments in the lid
# =============================================================================
def build_scope(spec):
    """S1-94 on a shelf with gussets, back to the lid, strap with a buckle: body with rounded edges and
    louvres, panel frame, cream panel, rubber screen hood, screen (own texture, "work" frames), switches,
    knobs, toggles, BNC, mains lamp, power inlet on the side."""
    lod = spec["lod"]
    x0, x1, z0, z1 = C94
    yp, yb = YF94, YLI
    parts = []
    cs = P("c94_case", "inst")
    g.box(cs, x0, x1, yp + 0.006, yb, z0, z1, **bev(lod, 0.004, 2))
    parts.append(cs)
    w = 0.005
    pn = P("c94_panel", "cream")
    g.box(pn, x0 + w, x1 - w, yp, yp + 0.007, z0 + w, z1 - w)
    parts.append(pn)
    sc = P("c94_screen", "black", group=SEL_SCREEN, section="crt")
    ys = yp - 0.0015
    mb.quad_facing(sc, [(CRT94[0], ys, CRT94[2]), (CRT94[1], ys, CRT94[2]), (CRT94[1], ys, CRT94[3]),
                        (CRT94[0], ys, CRT94[3])], (0, -1, 0))
    sc.glass_frame = (g.WORLD, CRT94[0], CRT94[1], CRT94[2], CRT94[3])
    parts.append(sc)
    sh = P("c94_shelf", "steel")
    g.box(sh, x0 - 0.008, x1 + 0.008, yp + 0.018, yb, z0 - 0.004, z0, **bev(lod, 0.0008, 1))
    parts.append(sh)
    if lod == 2:
        return parts
    fr = P("c94_frame", "inst")
    for a0, a1, c0, c1 in ((x0, x1, z1 - w, z1), (x0, x1, z0, z0 + w), (x0, x0 + w, z0 + w, z1 - w),
                           (x1 - w, x1, z0 + w, z1 - w)):
        g.box(fr, a0, a1, yp - 0.004, yp + 0.0075, c0, c1)
    parts.append(fr)
    hd = P("c94_hood", "rubber")
    t = 0.0065
    hx0, hx1, hz0, hz1 = CRT94[0] - t, CRT94[1] + t, CRT94[2] - t, CRT94[3] + t
    for a0, a1, c0, c1 in ((hx0, hx1, hz1 - t, hz1), (hx0, hx1, hz0, hz0 + t), (hx0, hx0 + t, hz0 + t, hz1 - t),
                           (hx1 - t, hx1, hz0 + t, hz1 - t)):
        g.box(hd, a0, a1, yp - 0.010, yp + 0.001, c0, c1, **bev(lod, 0.0018, 1))
    parts.append(hd)
    gl = P("c94_glass", "inst", section="glass")
    yg = yp - 0.0055
    mb.quad_facing(gl, [(CRT94[0], yg, CRT94[2]), (CRT94[1], yg, CRT94[2]), (CRT94[1], yg, CRT94[3]),
                        (CRT94[0], yg, CRT94[3])], (0, -1, 0))
    parts.append(gl)
    # controls
    for i, (x, z) in enumerate(KNOBS_BIG):
        parts += knob("c94_sw%d" % i, FF(x, z), 0.012, lod, angle=(-50.0, 35.0)[i], cap=(0.0058, 0.009))
    if lod == 0:
        for i, (x, z) in enumerate(KNOBS_SMALL):
            parts += knob("c94_kn%d" % i, FF(x, z), 0.0065, lod, angle=(20.0, -60.0, 90.0)[i], skirt=False)
    for i, (x, z, up) in enumerate(TOGS94):
        parts += toggle("c94_tg%d" % i, FF(x, z), lod, up=up)
    parts += toggle("c94_power", FF(*PWR94), lod, up=True, big=True)
    parts += lamp("c94_lamp", FF(*LAMP94), "lamp_r", lod, group=SEL_LAMP, s=0.8)
    # shelf: bent edge in front, flange on the lid, gussets
    g.box(sh, x0 - 0.008, x1 + 0.008, yp + 0.018, yp + 0.0215, z0 - 0.018, z0)
    g.box(sh, x0 - 0.008, x1 + 0.008, yb - 0.003, yb, z0 - 0.034, z0)
    for xa, xb in ((x0 - 0.008, x0 - 0.005), (x1 + 0.005, x1 + 0.008)):
        g.prism(sh, [(yb, z0 - 0.004), (yp + 0.065, z0 - 0.004), (yb, z0 - 0.115)], (1, 2), xa, xb)
    # strap over the top to the shelf, buckle on the right
    st = P("c94_strap", "strap")
    yst, r_, o = yp + 0.070, 0.008, 0.0035
    pts = [(x0 - o, yst, z0 + 0.002)]
    n = 4 if lod == 0 else 2
    for cx, cz, a0 in ((x0 + r_, z1 - r_, 180.0), (x1 - r_, z1 - r_, 90.0)):
        for k in range(n):
            a = math.radians(a0 - 90.0 * k / (n - 1))
            pts.append((cx + (r_ + o) * math.cos(a), yst, cz + (r_ + o) * math.sin(a)))
    pts.append((x1 + o, yst, z0 + 0.002))
    g.sweep(st, pts, (0, 1, 0), 0.0011, 0.015)
    parts.append(st)
    # power inlet on the right side
    pw = P("c94_inlet", "black")
    mb.lathe(pw, [(0.0085, 0.0), (0.0085, 0.006), (0.0060, 0.013), (0.0, 0.016)], 8 if lod == 0 else 6,
             (x1, yb - 0.035, z0 + 0.035), (1, 0, 0))
    parts.append(pw)
    if lod > 0:
        return parts
    bk = P("c94_buckle", "steel")
    g.box(bk, x1 + 0.0035, x1 + 0.0065, yst - 0.019, yst + 0.019, z0 + 0.061, z0 + 0.089, r=0.001, seg=1)
    g.box(bk, x1 + 0.0065, x1 + 0.0080, yst - 0.0025, yst + 0.0025, z0 + 0.064, z0 + 0.086)
    parts.append(bk)
    # louvres on the sides by the back wall
    vt = P("c94_vents", "dark")
    for xf, s in ((x0, -1), (x1, 1)):
        for k in range(3):
            yc = yb - 0.045 - 0.036 * k
            g.box(vt, *sorted((xf - s * 0.0004, xf + s * 0.0006)), yc - 0.013, yc + 0.013, z1 - 0.040, z1 - 0.034)
    parts.append(vt)
    for i, (xs, zs) in enumerate(((x0 + 0.009, z0 + 0.009), (x1 - 0.009, z0 + 0.009), (x0 + 0.009, z1 - 0.009),
                                  (x1 - 0.009, z1 - 0.009))):
        parts += screw("c94_screw%d" % i, (xs, yp, zs), (0, -1, 0), 0.0026, "f")
    bn = P("c94_bnc", "steel")
    mb.lathe(bn, [(0.0085, 0.0), (0.0085, 0.0025), (0.0, 0.0025)], 6, (BNC94[0], yp, BNC94[1]), (0, -1, 0), phase=0.5)
    parts.append(bn)
    return parts


def build_meter(spec):
    """Ts4342 type multimeter (after the Ts4315) in a holder: black case, window frame, scale with glass,
    needle (bone ozl_needle), aluminium panel on rivets with a corrector, selector with a toothed skirt,
    keys and a knob, terminals with caps on the top end face."""
    lod = spec["lod"]
    parts = []
    cs = P("mm_case", "mm_case")
    g.box(cs, MX0, MX1, MYF + 0.004, YLI, MZ0, MZ1, **bev(lod, 0.006, 2))
    parts.append(cs)
    scl = P("mm_scale", "mm_scale")
    g.box(scl, MWIN[0], MWIN[1], MSY, MSY + 0.002, MWIN[2], MWIN[3])
    parts.append(scl)
    pl = P("mm_plate", "mm_plate")
    g.box(pl, MX0 + 0.006, MX1 - 0.006, MYF + 0.0015, MYF + 0.0042, MZ0 + 0.008, MWIN[2] - 0.016, **bev(lod, 0.0010, 1))
    parts.append(pl)
    # needle at zero - left-up at 45 degrees from vertical (like the decal_meter scale)
    nd = P("mm_needle", "needle", group=SEL_NEEDLE)
    a = math.radians(135.0)
    fr = g.Frame(PIVOT, (math.cos(a), 0.0, math.sin(a)), (-math.sin(a), 0.0, math.cos(a)), (0, -1, 0))
    L = NEEDLE_L
    g.prism(nd, [(-0.18 * L, -0.0010), (L, -0.00025), (L, 0.00025), (-0.18 * L, 0.0010)], (0, 1), -0.0003, 0.0003,
            frame=fr)
    if lod == 0:
        mb.lathe(nd, [(0.0026, -0.0006), (0.0026, 0.0008), (0.0, 0.0010)], 8, tuple(PIVOT), (0, -1, 0))
    parts.append(nd)
    if lod == 2:
        return parts
    bz = P("mm_bezel", "mm_case")
    bz0, bz1 = MWIN[2] - 0.010, MZ1 - 0.024
    for xa, xb, za, zb in ((MX0 + 0.003, MX1 - 0.003, bz0, MWIN[2]), (MX0 + 0.003, MX1 - 0.003, MWIN[3], bz1),
                           (MX0 + 0.003, MWIN[0], MWIN[2], MWIN[3]), (MWIN[1], MX1 - 0.003, MWIN[2], MWIN[3])):
        g.box(bz, xa, xb, MYF, MYF + 0.0045, za, zb, **bev(lod, 0.0012, 1))
    parts.append(bz)
    gl = P("mm_glass", "mm_case", section="glass")
    y = MYF + 0.0005
    mb.quad_facing(gl, [(MWIN[0], y, MWIN[2]), (MWIN[1], y, MWIN[2]), (MWIN[1], y, MWIN[3]), (MWIN[0], y, MWIN[3])],
                   (0, -1, 0))
    parts.append(gl)
    # selector: toothed skirt, dome, bar knob with a white insert (set to "V")
    cxm = (MX0 + MX1) / 2
    kn = P("mm_switch", "black")
    c = Vector((cxm, MYF + 0.0015, MKZ))
    d = Vector((0.0, -1.0, 0.0))
    if lod == 0:
        mb.crenel(kn, c, d, 0.0280, 0.0245, 16, 0.0, 0.0055)
        mb.lathe(kn, [(0.0222, 0.0055), (0.0222, 0.0080), (0.0, 0.0100)], 16, c, d)
        al = math.radians(-28.0)
        Fa = plane(c, d, (math.sin(al), 0.0, math.cos(al)))
        mb.fbox(kn, Fa, -0.0062, 0.0062, -0.026, 0.026, 0.0090, 0.0190, r=0.003, seg=1)
        pt = P("mm_switch_ptr", "key")
        g.box(pt, -0.0012, 0.0012, 0.011, 0.023, 0.0190, 0.0196, frame=Fa)
        parts.append(pt)
    else:
        mb.lathe(kn, [(0.028, 0.0), (0.028, 0.012), (0.0, 0.012)], 8, c, d)
    parts.append(kn)
    # terminals on the top end face: black "*" and red, nut and knurled cap
    for x, reg in ((MX0 + 0.020, "black"), (MX1 - 0.020, "cap_red")):
        tp = P("mm_post_" + reg, reg)
        cc = (x, MYM, MZ1)
        if lod == 0:
            U(tp, "steel")
            mb.lathe(tp, [(0.0066, 0.0), (0.0066, 0.0028), (0.0, 0.0028)], 6, cc, (0, 0, 1), phase=0.5)
            U(tp, reg)
            mb.fluted(tp, cc, (0, 0, 1), 0.0068, 0.0006, 8, 0.0028, 0.0150, cap=False)
            mb.lathe(tp, [(0.0068, 0.0150), (0.0, 0.0170)], 16, cc, (0, 0, 1))
        else:
            mb.lathe(tp, [(0.0068, 0.0), (0.0068, 0.017), (0.0, 0.017)], 6, cc, (0, 0, 1))
        parts.append(tp)
    # holder: shelf with a flange on the lid
    hs = P("mm_holder", "steel")
    g.box(hs, MX0 - 0.006, MX1 + 0.006, MYF + 0.010, YLI, MZ0 - 0.004, MZ0)
    g.box(hs, MX0 - 0.006, MX1 + 0.006, YLI - 0.003, YLI, MZ0 - 0.030, MZ0)
    parts.append(hs)
    if lod > 0:
        return parts
    g.box(hs, MX0 + 0.004, MX1 - 0.004, MYF + 0.0005, MYF + 0.0040, MZ0 - 0.004, MZ0 + 0.0065)
    for xa, xb in ((MX0 - 0.004, MX0), (MX1, MX1 + 0.004)):
        g.box(hs, xa, xb, YLI - 0.050, YLI, MZ0 + 0.095, MZ0 + 0.120)
    for i, xx in enumerate((MX0 + 0.012, MX1 - 0.012)):
        bt = P("mm_holder_bolt%d" % i, "steel", uv_name="shelf_bolt", uv_origin=(xx, YLI, MZ0))
        mb.hex_bolt(bt, (xx, YLI - 0.003, MZ0 - 0.017), (0, -1, 0), 0.0045, 0.0035)
        parts.append(bt)
    # panel rivets, zero corrector, keys, the "Ohm" knob
    for i, (x, z) in enumerate(((MX0 + 0.0105, MZ0 + 0.0105), (MX1 - 0.0105, MZ0 + 0.0105),
                                (MX0 + 0.0105, MWIN[2] - 0.0205), (MX1 - 0.0105, MWIN[2] - 0.0205))):
        parts += screw("mm_rivet%d" % i, (x, MYF + 0.0015, z), (0, -1, 0), 0.0018, "f")
    zc = P("mm_zero", "black")
    mb.lathe(zc, [(0.0042, 0.0), (0.0042, 0.0012), (0.0, 0.0018)], 8, (cxm, MYF + 0.0015, MWIN[2] - 0.022),
             (0, -1, 0))
    U(zc, "dark")
    g.box(zc, cxm - 0.0030, cxm + 0.0030, MYF - 0.0005, MYF - 0.0002, MWIN[2] - 0.0228, MWIN[2] - 0.0212)
    parts.append(zc)
    ky = P("mm_keys", "key")
    for i in range(3):
        x = MX0 + 0.017 + 0.0235 * i
        g.box(ky, x - 0.0105, x + 0.0105, MYF - 0.0035, MYF + 0.0016, MZ0 + 0.013, MZ0 + 0.029, r=0.0014, seg=1)
    parts.append(ky)
    parts += knob("mm_knob", FF(MX1 - 0.019, MZ0 + 0.021, MYF + 0.0015), 0.0072, lod, angle=-30.0, skirt=False)
    return parts


def build_lidgear(spec):
    """In the lid between the instruments: a coil of spare wire on a hook, tied with insulating tape; two
    spring clips for the screwdriver (the screwdriver itself is vanilla, DECOR)."""
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    hx, hz = HOOK
    hk = P("coil_hook", "steel")
    mb.lathe(hk, [(0.0060, 0.0), (0.0060, 0.0020), (0.0, 0.0020)], 8, (hx, YLI, hz), (0, -1, 0))
    hp = [(hx, YLI - 0.001, hz), (hx, YLI - 0.022, hz), (hx, YLI - 0.030, hz + 0.004), (hx, YLI - 0.031, hz + 0.010)]
    g.pipe(hk, mb.spline(hp, 2) if lod == 0 else hp, 0.0026, 5 if lod == 0 else 4)
    parts.append(hk)
    cl = P("coil_wire", "cable")
    turns, n = (2, 14) if lod == 0 else (1, 8)
    rx, rz = 0.040, 0.050
    cz = hz - rz + 0.0056
    pts = []
    for t in range(turns):
        for k in range(n):
            a = 2 * math.pi * k / n
            pts.append((hx + rx * math.sin(a) + 0.003 * t, YLI - 0.020 - 0.0045 * t - 0.002 * math.sin(a),
                        cz + rz * math.cos(a)))
    pts.append(pts[0])
    g.pipe(cl, pts, 0.0028, 5 if lod == 0 else 4)
    parts.append(cl)
    if lod > 0:
        return parts
    tp = P("coil_tape", "tape")
    mb.lathe(tp, [(0.0, -0.007), (0.0078, -0.007), (0.0086, -0.005), (0.0086, 0.005), (0.0078, 0.007), (0.0, 0.007)], 8,
             (hx + 0.0015, YLI - 0.0222, cz - rz), (1, 0, 0))
    parts.append(tp)
    # clip for the screwdriver handle: base on a rivet, two bent tendrils around the handle
    zh = SDZ + 0.075
    cp = P("sd_clip0", "steel")
    g.box(cp, SDX - 0.010, SDX + 0.010, YLI - 0.0018, YLI, zh - 0.006, zh + 0.006)
    for s in (-1, 1):
        cpts = [(SDX + s * 0.006, YLI - 0.001, zh), (SDX + s * 0.0205, YLI - 0.011, zh), (SDX + s * 0.0195, YLI - 0.024, zh),
                (SDX + s * 0.0100, YLI - 0.034, zh)]
        g.sweep(cp, cpts, (0, 0, 1), 0.0006, 0.0055)
    mb.dome(cp, (SDX, YLI - 0.0018, zh), (0, -1, 0), 0.0022)
    parts.append(cp)
    # clip for the shaft: post from the lid and a ring around the shaft
    zs = SDZ - 0.060
    cq = P("sd_clip1", "steel")
    g.box(cq, SDX - 0.007, SDX + 0.007, YLI - 0.0018, YLI, zs - 0.005, zs + 0.005)
    mb.box_to(cq, (SDX, YLI - 0.0015, zs), (SDX, YLI - 0.0125, zs), 0.008, 0.0012, up=(0, 0, 1))
    ring = [(SDX + 0.0055 * math.sin(2 * math.pi * k / 8), YLI - 0.018 + 0.0055 * math.cos(2 * math.pi * k / 8), zs)
            for k in range(9)]
    g.pipe(cq, ring, 0.0008, 4)
    parts.append(cq)
    return parts


# =============================================================================
# Body panel: socket and board, controls, terminals, connectors
# =============================================================================
def post(name, x, y, reg, lod):
    """Power terminal: insulating base, ring lug of the wire with a tongue and a ferrule toward +x, knurled
    cap."""
    c = (x, y, ZPN)
    p = P(name, reg)
    if lod > 0:
        mb.lathe(p, [(0.0095, 0.0), (0.0095, 0.022), (0.0, 0.022)], 6, c, (0, 0, 1))
        return [p]
    mb.lathe(p, [(0.0105, 0.0), (0.0105, 0.0035), (0.0082, 0.0052), (0.0, 0.0052)], 10, c, (0, 0, 1))
    mb.fluted(p, c, (0, 0, 1), 0.0086, 0.0007, 7, 0.0075, 0.0200, cap=False)
    mb.lathe(p, [(0.0086, 0.0200), (0.0, 0.0228)], 14, c, (0, 0, 1))
    rt = P(name + "_ring", "brass", uv_name="post_ring", uv_origin=c)
    mb.lathe(rt, [(0.0090, 0.0052), (0.0090, 0.0075), (0.0040, 0.0075)], 10, c, (0, 0, 1))
    g.box(rt, x + 0.0060, x + 0.0150, y - 0.0035, y + 0.0035, ZPN + 0.0052, ZPN + 0.0075)
    mb.lathe(rt, [(0.0, 0.0), (0.0032, 0.0), (0.0032, 0.009), (0.0, 0.009)], 6, (x + 0.0145, y, ZPN + 0.0063), (1, 0, 0))
    return [p, rt]


def post_cable_end(x, y):
    """Wire end at the ferrule of a terminal lug."""
    return (x + 0.0235, y, ZPN + 0.0063)


def shr(i, x, lod):
    """ShR connector: flange on four screws, body with a socket. 0 - cap in place (on a chain), 1 - cap
    removed and lying beside (pins visible), 2 - plug with a cable to the oscilloscope."""
    c = Vector((x, SOCK_Y, ZPN))
    s = P("sock%d" % i, "steel", uv_name="sock", uv_origin=tuple(c))
    parts = [s]
    if lod > 0:
        mb.lathe(s, [(0.012, 0.0), (0.012, 0.014), (0.0, 0.014)], 6, tuple(c), (0, 0, 1))
        if i == 2:
            pg = P("sock_plug", "black")
            mb.lathe(pg, [(0.014, 0.010), (0.014, 0.040), (0.006, 0.054), (0.0, 0.054)], 6, tuple(c), (0, 0, 1))
            parts.append(pg)
        return parts
    g.box(s, x - 0.017, x + 0.017, SOCK_Y - 0.017, SOCK_Y + 0.017, ZPN, ZPN + 0.0028)
    mb.lathe(s, [(0.0118, 0.0028), (0.0118, 0.0140), (0.0102, 0.0140), (0.0102, 0.0120)], 10, tuple(c), (0, 0, 1))
    U(s, "black")
    mb.lathe(s, [(0.0102, 0.0120), (0.0, 0.0120)], 10, tuple(c), (0, 0, 1))
    U(s, "steel")
    for sx_, sy_ in ((-1, -1), (1, 1)):
        mb.dome(s, (x + sx_ * 0.0125, SOCK_Y + sy_ * 0.0125, ZPN + 0.0028), (0, 0, 1), 0.0021)
    if i == 2:
        pg = P("sock_plug", "black")
        mb.fluted(pg, tuple(c), (0, 0, 1), 0.0140, 0.0008, 8, 0.0100, 0.0240, cap=False)
        mb.lathe(pg, [(0.0140, 0.0240), (0.0115, 0.0400), (0.0065, 0.0520), (0.0, 0.0540)], 12, tuple(c), (0, 0, 1))
        parts.append(pg)
        return parts
    cp = P("sock_cap%d" % i, "black")
    if i == 0:
        cc, ax = c, Vector((0.0, 0.0, 1.0))
        h0 = 0.0100
    else:
        ax = Vector((0.94, 0.34, 0.0)).normalized()
        cc = Vector((x + 0.034, SOCK_Y - 0.020, ZPN + 0.0145)) - ax * 0.010
        h0 = 0.0
    mb.fluted(cp, tuple(cc), tuple(ax), 0.0140, 0.0008, 8, h0, h0 + 0.012, cap=False)
    mb.lathe(cp, [(0.0140, h0 + 0.012), (0.0, h0 + 0.016)], 16, tuple(cc), tuple(ax))
    parts.append(cp)
    # chain from the cap to the flange screw
    a = cc + ax * (h0 + 0.006) + Vector((0.0, -0.0142, 0.0)) if i == 0 else cc + ax * 0.008 + Vector((0.0, 0.0142, 0.0))
    b = Vector((x + 0.0125, SOCK_Y - 0.0125, ZPN + 0.0045))
    mid = (a + b) / 2 + Vector((0.004, -0.010, -0.004))
    ch = P("sock_chain%d" % i, "steel")
    g.pipe(ch, mb.spline([tuple(a), tuple(mid), tuple(b)], 2), 0.0008, 4)
    parts.append(ch)
    return parts


def build_panel(spec):
    lod = spec["lod"]
    parts = []
    fx = P("fixture", "fixture")
    g.box(fx, FIX[0], FIX[1], FIX[2], FIX[3], ZPN, ZPN + 0.024, **bev(lod, 0.002, 1))
    parts.append(fx)
    if lod == 2:
        pc = P("pcb", "pcb")
        g.box(pc, PCB[0], PCB[1], PCB_Y - 0.0008, PCB_Y + 0.0008, PCB[2], PCB[3])
        return parts + [pc]
    if lod == 0:
        # socket mounting lugs at the ends, screws, a slot for the board
        for xa, xb in ((FIX[0] - 0.010, FIX[0] + 0.002), (FIX[1] - 0.002, FIX[1] + 0.010)):
            g.box(fx, xa, xb, FIX[2] + 0.006, FIX[3] - 0.006, ZPN, ZPN + 0.004)
        for i, x in enumerate((FIX[0] - 0.005, FIX[1] + 0.005)):
            br = P("fixture_screw%d" % i, "brass", uv_name="fx_screw", uv_origin=(x, PCB_Y, ZPN))
            mb.dome(br, (x, PCB_Y, ZPN + 0.004), (0, 0, 1), 0.0034)
            parts.append(br)
        sl = P("fixture_slot", "dark")
        g.box(sl, FIX[0] + 0.010, FIX[1] - 0.010, PCB_Y - 0.0028, PCB_Y + 0.0028, ZPN + 0.0236, ZPN + 0.0242)
        parts.append(sl)
    for i, (x, y, up) in enumerate(TOGGLES):
        parts += toggle("tog%d" % i, FP(x, y), lod, up=up, tag="p")
    for i, (x, y, reg, grp) in enumerate(LAMPS):
        parts += lamp("plamp%d" % i, FP(x, y), reg, lod, group=grp, tag="p")
    parts += knob("gal", FP(*GAL), 0.014, lod, angle=40.0, tag="p")
    for x, y, reg in POSTS:
        parts += post("post_" + reg, x, y, reg, lod)
    for i, x in enumerate(SOCKETS):
        parts += shr(i, x, lod)
    if lod > 0:
        return parts
    for i, (x, y) in enumerate(FUSES):
        fu = P("fuse%d" % i, "black", uv_name="fuse", uv_origin=(x, y, ZPN))
        mb.lathe(fu, [(0.0080, 0.0), (0.0080, 0.0040), (0.0068, 0.0050), (0.0068, 0.0125), (0.0, 0.0155)], 8,
                 (x, y, ZPN), (0, 0, 1))
        parts.append(fu)
    dp = P("panel_plate", "plate")
    x0, x1, y0, y1 = PN_PLATE
    g.box(dp, x0, x1, y0, y1, ZPN, ZPN + 0.0012, r=0.0006, seg=1)
    parts.append(dp)
    for i, x in enumerate((x0 + 0.004, x1 - 0.004)):
        parts += screw("panel_plate_r%d" % i, (x, (y0 + y1) / 2, ZPN + 0.0012), (0, 0, 1), 0.0016, "z")
    return parts


def build_pcb(spec):
    """Probe board in the socket (facing the player): three DIP-14 ICs with leads, two electrolytic capacitors,
    three resistors on leads, an LED (blinks in "work"), test-point loops on the edge."""
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    pc = P("pcb", "pcb")
    g.box(pc, PCB[0], PCB[1], PCB_Y - 0.0008, PCB_Y + 0.0008, PCB[2], PCB[3])
    parts.append(pc)
    yf = PCB_F
    ch = P("pcb_chips", "chip")
    for x in CHIPS_X:
        g.box(ch, x - 0.0095, x + 0.0095, yf - 0.0042, yf - 0.0006, CHIP_Z - 0.0032, CHIP_Z + 0.0032)
    parts.append(ch)
    tp = P("pcb_tp", "solder")
    for x in TP.values():
        mb.u_handle(tp, (x - 0.0022, PCB_Y, PCB[3] - 0.0005), (x + 0.0022, PCB_Y, PCB[3] - 0.0005), (0, 0, 1), 0.0060,
                    0.0015, 0.00055, 4, 1)
    parts.append(tp)
    if lod > 0:
        return parts
    # IC leads (visible from the front) - seven per side
    for x in CHIPS_X:
        for s in (-1, 1):
            for k in range(7):
                xk = x - 0.00762 + k * 0.00254
                za, zb = sorted((CHIP_Z + s * 0.0030, CHIP_Z + s * 0.0047))
                mb.quad_facing(tp, [(xk - 0.0004, yf - 0.0016, za), (xk + 0.0004, yf - 0.0016, za),
                                    (xk + 0.0004, yf - 0.0016, zb), (xk - 0.0004, yf - 0.0016, zb)], (0, -1, 0))
    cp = P("pcb_caps", "cap_blue")
    for x, z in CAPS:
        mb.lathe(cp, [(0.0040, 0.0), (0.0040, 0.0105), (0.0036, 0.0112)], 10, (x, yf, z), (0, -1, 0))
        U(cp, "solder")
        mb.lathe(cp, [(0.0036, 0.0112), (0.0, 0.0113)], 10, (x, yf, z), (0, -1, 0))
        U(cp, "cap_blue")
    parts.append(cp)
    rs = P("pcb_res", "resistor")
    for x, z in RESISTORS:
        mb.lathe(rs, [(0.0, -0.0042), (0.0016, -0.0035), (0.0016, 0.0035), (0.0, 0.0042)], 6, (x, yf - 0.0022, z),
                 (1, 0, 0))
        for s in (-1, 1):
            g.pipe(tp, [(x + s * 0.0040, yf - 0.0022, z), (x + s * 0.0058, yf - 0.0022, z), (x + s * 0.0063, yf - 0.0003, z)],
                   0.0003, 3)
    parts.append(rs)
    ld = P("pcb_led", "led", group=SEL_BLINK)
    mb.lathe(ld, [(0.0029, 0.0), (0.0029, 0.0010), (0.0026, 0.0011), (0.0026, 0.0048), (0.0012, 0.0068), (0.0, 0.0073)],
             8, (LED[0], yf, LED[1]), (0, -1, 0))
    parts.append(ld)
    return parts


# =============================================================================
# Probes, crocodile clips, wires
# =============================================================================
def build_leads(spec):
    """Oscilloscope divider probe on a test point (hook, grey cap, stop ring, shank), cable in a loop to
    the BNC plug and a ground lead with a small crocodile clip on a socket screw; multimeter wires - from the
    plugs in the terminals, forward at an angle (the lid is close), to the crocodile clips on the test
    points; the oscilloscope power cable from the connector plug to the inlet on the side."""
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    # --- oscilloscope probe
    tip = Vector((TP["scope"], PCB_Y - 0.0030, TP_Z - 0.0010))
    dirv = Vector((-0.04, -0.42, 1.0)).normalized()
    pb = P("probe_scope", "probe")
    if lod == 0:
        U(pb, "steel")
        g.pipe(pb, mb.spline([tuple(tip + dirv * 0.012), tuple(tip + dirv * 0.004), tuple(tip + Vector((0.0, 0.0020, -0.0012))),
                              tuple(tip + Vector((0.0, 0.0052, 0.0006)))], 2), 0.0005, 4)
        U(pb, "probe_cap")
        mb.lathe(pb, [(0.0010, 0.010), (0.0032, 0.013), (0.0036, 0.030), (0.0040, 0.031)], 8, tuple(tip), tuple(dirv))
        U(pb, "probe")
        mb.lathe(pb, [(0.0040, 0.031), (0.0052, 0.033), (0.0056, 0.044), (0.0082, 0.046), (0.0082, 0.050), (0.0058, 0.052),
                      (0.0058, 0.096), (0.0046, 0.102), (0.0030, 0.118)], 10, tuple(tip), tuple(dirv))
    else:
        mb.lathe(pb, [(0.0035, 0.010), (0.0058, 0.040), (0.0058, 0.100), (0.0030, 0.118)], 6, tuple(tip), tuple(dirv))
    parts.append(pb)
    end = tip + dirv * 0.118
    plug_base = Vector((BNC94[0], YF94 - 0.0025, BNC94[1]))
    plug_end = plug_base + Vector((0.0, -0.032, 0.0))
    pl = P("probe_bnc_plug", "steel")
    if lod == 0:
        mb.fluted(pl, tuple(plug_base), (0, -1, 0), 0.0078, 0.0007, 8, 0.0, 0.0120, cap=False)
        mb.lathe(pl, [(0.0078, 0.0120), (0.0056, 0.0160), (0.0047, 0.0300), (0.0038, 0.0320)], 8, tuple(plug_base), (0, -1, 0))
    else:
        mb.lathe(pl, [(0.0075, 0.0), (0.0075, 0.012), (0.0045, 0.030)], 5, tuple(plug_base), (0, -1, 0))
    parts.append(pl)
    zl = ZPN + 0.0030
    parts += cable("probe_cable", "cable", [tuple(end), tuple(end + dirv * 0.016), (-0.282, -0.182, 0.712), (-0.303, -0.180, 0.672),
                                            (-0.320, -0.165, 0.600), (-0.330, -0.140, 0.530), (-0.334, -0.105, zl + 0.0015),
                                            (-0.330, -0.060, zl), (-0.320, -0.035, zl + 0.013), (-0.310, -0.050, 0.540),
                                            (-0.303, -0.075, 0.600), (-0.299, -0.088, 0.645), (BNC94[0], -0.082, BNC94[1] - 0.006),
                                            (BNC94[0], -0.070, BNC94[1] - 0.0005), tuple(plug_end)], 0.0026, lod, k=3)
    # probe ground lead: from the ring to a small crocodile clip on the left socket screw
    gnd_tip = Vector((FIX[0] - 0.005, PCB_Y, ZPN + 0.0052))
    gfr = croc_frame(gnd_tip, (0.25, -0.35, 1.0), (0.0, 1.0, 0.0))
    if lod == 0:
        jaw = P("probe_gnd_jaws", "clip_jaw")
        boot = P("probe_gnd_boot", "boot_black")
        mb.croc(jaw, boot, gfr, lod, k=0.6, spring=False, sides=6)
        parts += [jaw, boot]
        ring = tip + dirv * 0.046
        tail = gfr.p(0.061 * 0.6, 0.0, 0.0)
        parts += cable("probe_gnd_wire", "cable", [tuple(ring + Vector((0.006, 0.0, 0.0))), (ring.x + 0.012, ring.y - 0.010, ring.z - 0.035),
                                                   (tail.x + 0.010, tail.y - 0.012, tail.z + 0.030), tuple(tail)], 0.0011, lod)
    # --- multimeter wires: plugs in the terminals, crocodile clips on the test points
    ax = PLUG_AX.normalized()
    for x, reg, wire, tpk, u in ((MX1 - 0.020, "cap_red", "wire_red", "red", (0.05, 0.75, 0.66)),
                                 (MX0 + 0.020, "black", "cable", "gnd", (0.05, 0.75, 0.66))):
        base = Vector((x, MYM, MZ1 + 0.0170))
        pg = P("mm_plug_" + reg, reg)
        if lod == 0:
            mb.lathe(pg, [(0.0, -0.004), (0.0045, -0.004), (0.0052, 0.002), (0.0052, 0.020), (0.0026, 0.034)],
                     10, tuple(base), tuple(ax))
        else:
            mb.lathe(pg, [(0.0050, -0.004), (0.0050, 0.020), (0.0026, 0.034)], 6, tuple(base), tuple(ax))
        parts.append(pg)
        e = base + ax * 0.034
        fr = croc_frame(Vector((TP[tpk], PCB_Y, TP_Z - 0.0015)), u, (1.0, 0.0, 0.0))
        jaw = P("mm_croc_%s_jaws" % tpk, "clip_jaw")
        boot = P("mm_croc_%s_boot" % tpk, "boot_red" if reg == "cap_red" else "boot_black")
        mb.croc(jaw, boot, fr, lod)
        parts += [jaw, boot]
        tail = fr.p(0.061, 0.0, 0.0)
        fu = fr.u
        zl = ZPN + 0.0021                                    # the wire lies on the panel
        if tpk == "red":
            mid = [(-0.200, -0.030, 0.600), (-0.180, -0.006, 0.502), (-0.140, 0.010, zl), (-0.060, 0.032, zl),
                   (-0.025, 0.085, 0.545), (-0.012, 0.125, 0.650), (-0.006, 0.140, 0.720), (0.000, 0.148, 0.795),
                   (0.018, 0.153, 0.840), (0.046, 0.156, 0.862), (0.072, 0.159, 0.871), (x - 0.006, 0.168, 0.870)]
        else:
            mid = [(-0.150, -0.032, 0.600), (-0.140, -0.010, 0.502), (-0.110, 0.002, zl), (-0.070, 0.016, zl),
                   (-0.035, 0.075, 0.540), (-0.021, 0.120, 0.650), (-0.016, 0.140, 0.740), (-0.010, 0.150, 0.815),
                   (0.002, 0.158, 0.852), (x - 0.006, 0.168, 0.866)]
        pts = [tuple(tail), tuple(tail + fu * 0.018)] + mid + [tuple(e + ax * 0.022), tuple(e)]
        parts += cable("mm_lead_" + tpk, wire, pts, 0.0021, lod)
    # --- oscilloscope power cable: from the connector plug up to the inlet on the right side
    x2 = SOCKETS[2]
    inlet = Vector((C94[1] + 0.016, YLI - 0.035, C94[2] + 0.035))
    parts += cable("scope_power", "cable", [(x2, SOCK_Y, ZPN + 0.056), (x2 - 0.004, SOCK_Y + 0.010, ZPN + 0.090),
                                            (x2 - 0.020, 0.170, 0.600), (C94[1] + 0.048, 0.215, inlet.z - 0.032),
                                            (inlet.x + 0.014, inlet.y - 0.002, inlet.z - 0.004), tuple(inlet)], 0.0040, lod)
    return parts


# =============================================================================
# Battery
# =============================================================================
def build_battery(spec):
    """6ST-55: body with rounded edges, a clamp ledge along the bottom of the long sides, ribs; lid with a
    seam, a strip with six knurled plugs, conical lead terminals, folding handles on the ends; crocodile
    clips on the terminals, wires over the case rim to the panel terminals."""
    lod, sd = spec["lod"], spec["sides"]
    bt = P("battery", "battery")
    g.box(bt, BAX0, BAX1, BAY0, BAY1, 0.0, BAZ - 0.016, **bev(lod, 0.005, 1))
    parts = [bt]
    if lod == 2:
        g.box(bt, BAX0 + 0.002, BAX1 - 0.002, BAY0 + 0.002, BAY1 - 0.002, BAZ - 0.016, BAZ)
        return parts
    g.box(bt, BAX0 + 0.002, BAX1 - 0.002, BAY0 + 0.002, BAY1 - 0.002, BAZ - 0.016, BLID, **bev(lod, 0.004, 1))
    g.box(bt, BCAP_X - 0.016, BCAP_X + 0.016, BAY0 + 0.022, BAY1 - 0.022, BLID, BAZ, **bev(lod, 0.002, 1))
    tm = P("battery_posts", "lead")
    for x, y in TERM:
        mb.lathe(tm, [(0.012, 0.0), (0.012, 0.004), (0.0092, 0.006), (0.0082, 0.024), (0.0, 0.024)],
                 12 if lod == 0 else 6, (x, y, BLID), (0, 0, 1))
    parts.append(tm)
    if lod == 0:
        g.box(bt, BAX0 - 0.004, BAX1 + 0.004, BAY0 + 0.006, BAY1 - 0.006, 0.0, 0.012)
        for xf, s in ((BAX0, -1), (BAX1, 1)):
            for y in (-0.105, 0.005):
                g.box(bt, *sorted((xf - s * 0.001, xf + s * 0.0018)), y - 0.003, y + 0.003, 0.014, BAZ - 0.030)
        for k in range(6):
            cc = (BCAP_X, BAY0 + 0.040 + 0.0324 * k, BAZ)
            cp = P("battery_cap%d" % k, "black", uv_name="battery_cap", uv_origin=cc)
            mb.fluted(cp, cc, (0, 0, 1), 0.0105, 0.0008, 6, 0.0, 0.0080, cap=False)
            mb.lathe(cp, [(0.0105, 0.0080), (0.0, 0.0102)], 12, cc, (0, 0, 1))
            parts.append(cp)
        hd = P("battery_handles", "black")
        for yf, s in ((BAY0, -1),):                      # the handle at the rear end is not visible - not built
            for xx in (BAX0 + 0.040, BAX1 - 0.040):
                g.box(hd, xx - 0.008, xx + 0.008, *sorted((yf, yf + s * 0.006)), BAZ - 0.034, BAZ - 0.018)
            mb.u_handle(hd, (BAX0 + 0.040, yf + s * 0.004, BAZ - 0.026), (BAX1 - 0.040, yf + s * 0.004, BAZ - 0.026),
                        (0.0, s * 0.25, -1.0), 0.040, 0.008, 0.0040, 5, lod)
        parts.append(hd)
    # clips on the terminals (jaws spread around the terminal) and wires to the panel terminals
    for (x, y), (px, py, reg), cu in zip(TERM, POSTS, ((-1.0, 0.0, 0.35), (-0.7, 0.7, 0.35))):
        fr = croc_frame(Vector((x + 0.006, y, BLID + 0.014)), cu, (0.0, 0.0, 1.0))
        jaw = P("battery_clamp_jaws_" + reg, "clip_jaw")
        boot = P("battery_clamp_boot_" + reg, "boot_red" if reg == "cap_red" else "boot_black")
        mb.croc(jaw, boot, fr, lod, k=1.6, gap=0.0058, sides=6)
        parts += [jaw, boot]
        tail = fr.p(0.061 * 1.6, 0.0, 0.0)
        u = fr.u
        if reg == "cap_red":
            mid = [(0.162, py - 0.033, 0.262), (0.163, py - 0.028, 0.320), (0.165, py - 0.020, 0.420),
                   (0.163, py - 0.012, 0.495), (0.157, py - 0.006, 0.527)]
        else:
            mid = [(0.188, py + 0.038, 0.258), (0.172, py + 0.030, 0.300), (0.166, py + 0.020, 0.380),
                   (0.164, py + 0.014, 0.470), (0.158, py + 0.009, 0.526)]
        ce = post_cable_end(px, py)
        pts = [tuple(tail), tuple(tail + u * 0.020)] + mid + [(0.146, py + 0.003, 0.534), (0.136, py + 0.001, 0.520),
                                                          (ce[0] + 0.005, py, ce[2] + 0.016), ce]
        parts += cable("battery_cable_" + reg, "wire_red" if reg == "cap_red" else "cable", pts, 0.0045, lod)
    return parts


def build_lod(spec):
    parts = build_crates(spec) + build_case(spec) + build_lid(spec) + build_scope(spec) + build_meter(spec)
    parts += build_lidgear(spec) + build_panel(spec) + build_pcb(spec) + build_leads(spec) + build_battery(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    wood = kx.PEN + r"\wood.rvmat"
    metal = kx.PEN + r"\metalplate.rvmat"
    stack = kx.box_pts(CX0 - 0.02, CX1 + 0.02, CY0 - 0.01, CY1 + 0.01, 0.0, ZC1)
    # a component thinner than 0.5 m does not work: the lid goes forward, over the body (the oscilloscope is
    # there too), and down into the body; the battery goes left, into the crates
    lid = kx.box_pts(CX0, CX1, LY1 - 0.51, LY1 + 0.01, ZC1 - 0.12, LZ1 + 0.006)
    batt = kx.box_pts(BAX1 - 0.50, BAX1, BAY0, BAY1, 0.0, BAZ + 0.02)
    comps = [(stack, wood), (lid, metal), (batt, metal)]
    memory = {
        "invView": [(0.0, -2.4, 1.0)],
        "ce_center": [(0.0, 0.0, 0.45)],
        "ce_radius": [(0.65, 0.0, 0.45)],
        # multimeter needle axis (ozl_needle): from the needle axis toward the player
        "ozl_needle_axis": [tuple(PIVOT), tuple(PIVOT + Vector((0, -0.05, 0)))],
    }
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 60.0, memory, bbox


# the first ones are for the --look preview: overview, instruments in the lid and the panel (in "work" -
# overview and instruments: screen, needle, lamps), the battery with clips; then probes, crates, from behind
SHOTS = [
    ("front", (-0.80, -1.62, 1.18), (-0.02, 0.0, 0.46), 32),
    ("instruments", (-0.12, -0.88, 1.02), (XC, 0.06, 0.70), 32),
    ("panel", (0.06, -0.62, 1.02), (XC, -0.04, 0.53), 34),
    ("right", (1.05, -0.95, 0.80), (0.12, -0.02, 0.32), 32),
    ("probes", (-0.42, -0.55, 0.80), (-0.22, -0.12, 0.62), 40),
    ("crates", (-0.40, -1.05, 0.42), (XC, 0.0, 0.18), 32),
    ("back", (1.0, 1.9, 1.25), (0.0, 0.0, 0.48), 30),
]

M.look_shots = (4, 2)
M.run(build_lod, collision, SHOTS, row_step=1.1, row_shot=((1.1, -5.0, 1.3), (1.1, 0, 0.5)))
