"""M21 - radio-intercept rack: Trail Analyzer of the Neutrals (OZL_Lnr_Proc_Trail).
An analyzer: 4x4 cargo, no module slots (analyzers and terminals have none).

    blender --background --python build_m21.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (scales, limbs, table, board, notepad,
tag, grounding sign, loudspeaker grille; displays, LCD and PDA screen - "off" and the "working" frames).

The rack is a floor-standing instrument cabinet 800 x 2000 x 700 mm (GOST 28601.2-90; the dimensions
come from the M06 generator) with a 690 mm opening between the rails. Brown enamel of the Neutrals (no green),
lived-in: worn edges, moderate rust (more near the floor), a tin patch on rivets on the left door.

The contents are real receivers of the 1970s-90s (W x H x D):
- R-250M2 shortwave receiver (USSR), 650 x 460 x 450 mm with protruding parts, 90 kg (the R-250 is
  650 x 460 x 450, 650 x 530 x 520 with shock mounts; the M2 is the same case with pentode tubes).
  Gray hammer-finish enamel, two screwed panels, four bar handles; the upper panel has a gauge, a
  fine-tuning limb with a pin handle, a range switch and an SR-50 antenna input; the lower one has
  the scale window in a bakelite surround, two large tuning knobs, phone jacks, the subrange table
  and a jack block. It stands at the bottom, as in real racks (the heaviest); its power supply is
  behind the doors.
- ICOM IC-R7000 scanner (Japan, 1986), 286 x 110 x 276 mm, 8 kg: black; the S-meter and the frequency
  display under one glass, a 4 x 3 keypad, a loudspeaker grille on the lid, a fold-out stand in front.
- Yaesu FRG-7700 shortwave receiver (Japan, 1980), 334 x 129 x 225 mm, 6 kg (another source gives
  330 x 127 x 254): gray panel, black case, S-meter on the left, frequency display on the right.
- AOR AR3000A scanner (Japan, 1990), 138 x 80 x 200 mm, 1.2 kg: black, LCD, 4 x 4 keypad.
Around them: a loudspeaker with stamped louver hoods; TON-2 headphones on a hook under the grille
(steel headband, bakelite capsules, ear cushions, a braided cord with a plug in a patch-panel jack);
a coil of antenna cable; a patch panel (antenna switch, BNC jacks with plugs, a jumper, lamps). On
the roof is a discone scanner antenna on a mast; its cable runs from the panel up the left rail
(taped), through the front left eyebolt and along the roof to the mast connector; a second cable
goes from the mast back into the entry. On the pull-out shelf: a homemade card reader (a board on a
block, a memory card socket, a chip, an LED, a 9 V battery on a holder), a PDA stand (Palm III,
120 x 80 x 18), a ribbon cable and wires, a sheet with written frequencies, a mug.

Detail: the "dayz" look (matte, dirtier, colored AO); the rack enamel is worn at the door handles,
the lock and the shelf handle, the hammer enamel of the R-250M2 at the bar handles. The rack is its
own copy of the detailed M06 rack (m21_rack.py): chamfers, louvers and screws on the side walls,
eyebolts, a grounding bolt with a plate, screwed panels, a grille frame, hinges, bar handles, a
sealed lock, an inventory tag (digits), shelf slides, a handle and a mat. The instrument details
(m21_bits.py, a copy of the M06 small parts plus its own) are turned knurled knobs with a skirt and
a mark, "beak" knobs, large knobs with a pin, limbs, BNC jacks with plugs, toggles, lamps in
bezels, keys with chamfered edges, screws, bar handles, window frames with rounded corners, glass.
Cables and cords are smooth curves (kgeo.pipe along a spline), jumpers sag in an arc. Vanilla DayZ
items are proxies (kvanilla): a screwdriver and a 9 V battery by the card reader, a pen on the
frequency sheet, two cassettes on the AR3000A, tape on the loudspeaker.

Working look (the OZL_WorkFx loop):
- ozl_screen, ozl_screen_2, ozl_screen_3, ozl_screen_4 - the IC-R7000 display, the FRG-7700 display,
  the AR3000A LCD and the PDA screen: their own textures (sections vfd7, vfdf, lcd, pda; flat UV
  0..1) - "off" and the "working" frames (frames);
- ozl_lamp - steady glow (_on atlas): the backlight of the R-250M2 scale window and of the IC-R7000
  and FRG-7700 S-meters, the R-250M2 power lamp and the green panel lamp; ozl_lamp_2 - blinks
  (blink): the card-reader LED and the red panel lamp;
- the needles of the three S-meters are bones ozl_needle (R-250M2), ozl_needle_2 (IC-R7000),
  ozl_needle_3 (FRG-7700) on their own sources: rotation, 0 is the scale zero, 1 is the scale end,
  96 degrees clockwise; the axis points from the needle pivot toward the viewer (as in M06 and M08:
  the Blender -> p3d conversion is a reflection, kexport.conv, so a positive rotation about the
  axis toward the viewer is clockwise). The R-250M2 fine-tuning limb and the cursor of its scale
  are bones ozl_tune_disc (rotation, 1.5 turns per phase 1) and ozl_tune_visor (translation along
  the scale, axis 1 m - the offset in meters) on one source ozl_tune: the limb turns, the cursor
  moves. When "working" the needles and the limb wobble (wobble).
In the "working" preview (states on, move) the needles are rotated and the limb and the cursor are
mid-wobble: krender.place_look and place are extended here with a group rotation (as in M06); the
kit is untouched.

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
import m21_bits as b  # noqa: E402
import m21_rack as rk  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
X0, X1, Y0, Y1, H = -0.40, 0.40, -0.35, 0.35, 2.00          # rack (as in M06)
XI0, XI1 = rk.rack_opening(X0, X1)                           # opening between the rails
ST = rk.SHELF_T
YF = Y0 + 0.012                                              # instrument face
Y_FACE = YF - 0.0015                                         # faces of scales and displays
Y_NEEDLE = YF - 0.0026                                       # needles - between the scale and the glass
# cells from bottom to top: the compartment with doors (power supply), R-250M2, the pull-out shelf,
# IC-R7000 and FRG-7700, the patch panel, AR3000A with the loudspeaker, the grille
Z_DOOR, Z_R, Z_SLIDE, Z_A, Z_P, Z_B, Z_V, Z_TOP = 0.10, 0.52, 1.00, 1.10, 1.26, 1.42, 1.74, 1.96
CELLS = [(Z_DOOR, Z_R, "doors"), (Z_R, Z_SLIDE, "open"), (Z_SLIDE, Z_A, "slide"), (Z_A, Z_P, "open"),
         (Z_P, Z_B, "blank"), (Z_B, Z_V, "open"), (Z_V, Z_TOP, "vent")]
# pull-out shelf (top of the mat is ZM)
ZS, PULL, SDEPTH = 1.065, 0.30, 0.42
TY0, TY1 = Y0 - PULL, Y0 - PULL + SDEPTH
ZM = ZS + 0.003
# doors (as in m21_rack): face, middle of the handles, the lock; the tag on the right door; the
# grounding bolt on the left side wall (y, z); eyebolts (the antenna cable runs through the front left one)
YD = Y0 - 0.018
XM = 0.0
ZH = min(Z_R - 0.003 - 0.20, Z_DOOR + 0.003 + 0.40)
ZL = Z_R - 0.003 - 0.10
TAG = (0.21, Z_R - 0.075)
GROUND = (0.29, 0.24)
EYES = [(X0 + 0.06, Y0 + 0.06, 0.0), (X1 - 0.06, Y0 + 0.06, 0.0), (X0 + 0.06, Y1 - 0.06, 0.0),
        (X1 - 0.06, Y1 - 0.06, 0.0)]
# instruments: (x0, x1, z0, z1, depth); tabletop ones stand on FOOT feet
FOOT = 0.006
R250 = (-0.325, 0.325, Z_R + ST, Z_R + ST + 0.460, 0.450)    # R-250M2
R7 = (-0.335, -0.049, Z_A + ST, Z_A + ST + 0.110, 0.276)     # IC-R7000
FRG = (0.005, 0.339, Z_A + ST, Z_A + ST + 0.129, 0.225)      # FRG-7700
AR = (-0.322, -0.184, Z_B + ST, Z_B + ST + 0.080, 0.200)     # AR3000A
SPK = (-0.150, 0.050, Z_B + ST, Z_B + ST + 0.180, 0.150)     # loudspeaker
ZP = (Z_P + Z_B) / 2                                         # patch panel row
YP = Y0 - 0.003                                              # face of the blank panel

# --- R-250M2: the upper panel has the gauge, limb, range switch, antenna input; the lower one has
# the scale surround, table, large knobs, jacks
RZ0, RZ1 = R250[2], R250[3]
ZSPLIT = RZ1 - 0.210                                         # seam between the upper and lower panels
M_R = (-0.120, -0.060, 0.902, 0.952)                         # gauge face
DISC = (0.095, 0.925, 0.052)                                 # fine-tuning limb: x, z, radius
Y_DISC = YF - 0.014                                          # limb face
BAND = (0.200, 0.928, 0.013)                                 # range switch
ANT = (0.265, 0.957)                                         # SR-50 antenna input
HOUS = (-0.130, 0.130, 0.650, 0.770)                         # bakelite surround of the scale window
Y_HOUS = YF - 0.026                                          # surround face
W_R = (-0.105, 0.105, 0.665, 0.757)                          # scale window (drum and scale)
Y_WIN = Y_HOUS - 0.0005
TB = (0.172, 0.268, 0.648, 0.770)                            # subrange table
STRIP = (0.172, 0.262, 0.604, 0.618)                         # jack block
# the scale in the window follows the make_r250_window decal: ticks from 0.08 to 0.92 of the width,
# the field is 0.52..0.94 of the height
SCALE_X = (W_R[0] + 0.08 * (W_R[1] - W_R[0]), W_R[0] + 0.92 * (W_R[1] - W_R[0]))
SCALE_Z = (W_R[3] - 0.94 * (W_R[3] - W_R[2]), W_R[3] - 0.52 * (W_R[3] - W_R[2]))
VISOR_REST = 0.25                                            # cursor at rest - at 2.0 MHz
VISOR_X = SCALE_X[0] + VISOR_REST * (SCALE_X[1] - SCALE_X[0])
TUNE_RUN = 0.50 * (SCALE_X[1] - SCALE_X[0])                  # cursor travel at phase 1, m
TUNE_TURNS = 1.5                                             # limb turns at phase 1
# knobs: (x, z, radius, kind, limb, mark angle clockwise from 12 o'clock)
K_R250 = [(-0.250, 0.912, 0.009, "plain", None, 20), (-0.178, 0.864, 0.012, "pointer", None, -40),
          (-0.090, 0.858, 0.016, "skirt", "ring11", 30), (0.008, 0.927, 0.008, "plain", None, -60),
          (0.008, 0.864, 0.012, "pointer", "ring6", 50), (0.060, 0.864, 0.009, "plain", None, 110),
          (0.135, 0.862, 0.011, "pointer", "ring6", -55), (0.200, 0.862, 0.011, "pointer", "ring6", 25),
          (0.265, 0.905, 0.010, "plain", None, 45), (0.265, 0.862, 0.010, "plain", None, -30),
          (BAND[0], BAND[1], BAND[2], "pointer", "ring12", 70),
          (-0.245, 0.745, 0.009, "plain", None, 0), (-0.245, 0.612, 0.020, "skirt", "ring11", -35),
          (0.000, 0.618, 0.008, "plain", None, 90)]
TOG_R250 = [(-0.262, 0.864), (-0.236, 0.864), (0.035, 0.962), (-0.245, 0.560), (0.000, 0.568)]
JACKS_R250 = [(-0.262, 0.705), (-0.228, 0.705), (-0.262, 0.672), (-0.228, 0.672)]
BIG_R250 = [(-0.079, 0.598, 0.036, False, 215.0), (0.079, 0.598, 0.033, True, 35.0)]   # x, z, r, teeth, pin
HANDLES_R250 = [(x, za, zb) for x in (-0.293, 0.293) for za, zb in ((0.800, 0.975), (0.550, 0.765))]

# --- IC-R7000
R7A = R7[2] + FOOT
WF_7 = (R7[0] + 0.046, R7[0] + 0.212, R7[3] - 0.040, R7[3] - 0.006)   # silver window frame
M_7 = (R7[0] + 0.052, R7[0] + 0.110, R7[3] - 0.036, R7[3] - 0.010)    # S-meter
D_7 = (R7[0] + 0.120, R7[0] + 0.204, R7[3] - 0.036, R7[3] - 0.010)    # frequency display
KP_7 = (R7[0] + 0.216, R7[1] - 0.004, R7A + 0.030, R7[3] - 0.004)     # keypad block
TUNE_7 = (R7[0] + 0.168, R7A + 0.030, 0.023)
K_R7 = [(R7[0] + 0.016, R7[3] - 0.015, 0.006, "skirt", "ring_w", -60),
        (R7[0] + 0.036, R7[3] - 0.015, 0.006, "skirt", "ring_w", 40),
        (R7[0] + 0.064, R7A + 0.015, 0.0085, "dual", "ring_w", 30),
        (R7[0] + 0.094, R7A + 0.015, 0.0085, "dual", "ring_w", -20),
        (R7[0] + 0.232, R7A + 0.015, 0.008, "skirt", "ring_w", 0),
        (R7[0] + 0.270, R7A + 0.015, 0.008, "skirt", "ring_w", 60)]
# buttons: (x, z, width, height, is white)
KEYS_R7 = ([(R7[0] + 0.016, R7[3] - 0.031, 0.012, 0.006, True), (R7[0] + 0.036, R7[3] - 0.031, 0.012, 0.006, True)] +
           [(R7[0] + 0.040 + 0.014 * i, R7A + 0.050 - 0.013 * j, 0.0105, 0.0055, j == 1) for i in range(4)
            for j in (0, 1)] +
           [(R7[0] + xx, R7A + 0.008 + 0.014 * k, 0.011, 0.006, k == 0) for xx in (0.128, 0.208) for k in range(4)] +
           [(R7[0] + 0.251, R7A + 0.023, 0.008, 0.005, True), (R7[0] + 0.251, R7A + 0.010, 0.008, 0.005, False)] +
           [(R7[0] + 0.225, R7[3] - 0.021 - 0.0105 * k, 0.009, 0.0055, True) for k in range(5)] +
           [(R7[0] + 0.243 + 0.014 * i, R7[3] - 0.026 - 0.0125 * j, 0.010, 0.0065, False) for i in range(3)
            for j in range(4)])

# --- FRG-7700
FRA = FRG[2] + FOOT
M_F = (FRG[0] + 0.016, FRG[0] + 0.076, FRG[3] - 0.046, FRG[3] - 0.010)
D_F = (FRG[1] - 0.124, FRG[1] - 0.018, FRG[3] - 0.040, FRG[3] - 0.012)
TUNE_F = (FRG[0] + 0.170, FRA + 0.058, 0.026)
K_FRG = [(FRG[0] + 0.046, FRA + 0.052, 0.011, "skirt", "ring11", -40),
         (FRG[0] + 0.022, FRA + 0.016, 0.0075, "plain", None, 30), (FRG[0] + 0.058, FRA + 0.016, 0.0075, "plain", None, -50),
         (FRG[0] + 0.094, FRA + 0.016, 0.0075, "plain", None, 10),
         (FRG[1] - 0.090, FRA + 0.020, 0.009, "skirt", "ring6", 30), (FRG[1] - 0.058, FRA + 0.020, 0.008, "plain", None, -20),
         (FRG[1] - 0.026, FRA + 0.020, 0.008, "plain", None, 70)]
KEYS_FRG = ([(FRG[1] - 0.112 + 0.0215 * i, FRG[3] - 0.054, 0.014, 0.007, True) for i in range(5)] +
            [(FRG[0] + 0.090 + 0.018 * i, FRG[3] - 0.018, 0.012, 0.006, i == 0) for i in range(3)] +
            [(FRG[0] + 0.118, FRA + 0.016, 0.011, 0.008, False)])

# --- AR3000A
ARA = AR[2] + 0.004
L_A = (AR[0] + 0.010, AR[0] + 0.076, AR[3] - 0.034, AR[3] - 0.010)
K_AR = [(AR[0] + 0.020, ARA + 0.016, 0.0075, "plain", None, 30), (AR[0] + 0.052, ARA + 0.018, 0.011, "dual", None, -40)]
KEYS_AR = [(AR[0] + 0.090 + 0.0125 * i, AR[3] - 0.014 - 0.0155 * j, 0.0095, 0.0085, j == 0) for i in range(4)
           for j in range(4)]

# --- patch panel: antenna switch, BNC jacks (0 - antenna, 2-3 - jumper), lamps, headphone and
# loudspeaker jacks, a toggle
K_P = [(-0.270, ZP, 0.016, "pointer", "ring6", -30)]
BNC_P = [(-0.180, ZP, True), (-0.130, ZP, False), (-0.080, ZP, True), (-0.030, ZP, True)]
JACK_PHONES, JACK_SPK = (0.170, ZP), (0.215, ZP)

# --- headphones on a hook under the grille, the antenna on the roof
HOOK = (0.248, Y0 - 0.046, 1.724)                            # bottom of the hook: x, y, z
BAND_R = 0.080                                               # headband radius
MAST = (0.0, 0.12)
ZT_ANT = H + 0.240                                           # top of the antenna

# --- pull-out shelf: card reader (x0, x1, y0, y1, h), PDA on a stand, notepad, mug
RDR = (-0.285, -0.155, TY0 + 0.05, TY0 + 0.14, 0.035)
RDR_PCB = (RDR[0] + 0.012, RDR[1] - 0.012, RDR[2] + 0.010, RDR[3] - 0.010)
PDA_X, PDA_Y, PDA_DEG = -0.005, TY0 + 0.095, 20.0            # PDA bottom: center x, y; tilted back
PDA_W, PDA_H, PDA_T = 0.080, 0.120, 0.018
PDA_SCR = (-0.028, 0.028, 0.045, 0.105)                      # screen in PDA axes: x, up along the plane
PAD = (0.070, 0.180, TY0 + 0.015, TY0 + 0.160)               # notepad x0 x1 y0 y1
MUG = (0.250, TY0 + 0.095, 0.040, 0.088)                     # mug: x, y, radius, height
BAT = (-0.128, TY0 + 0.072)                                  # 9 V battery by the card reader

LOD_SPECS = [
    dict(lod=0, bev=2, sides=16),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "rk": ("enamel", 0.5), "rk_rail": ("rail", 0.8), "rk_panel": ("enamel_panel", 0.6), "rk_door": ("enamel_door", 0.6),
    "rk_front": ("enamel_front", 0.8), "rk_inner": ("dark", 0.3), "grille_v": ("grille_v", 0.8),
    "steel": ("steel", 1.2), "chrome": ("chrome", 1.4), "black": ("black", 1.2), "rubber": ("rubber", 0.6),
    "tag": ("tag", 6.0), "mat": ("mat", 0.6), "seal": ("seal", 2.0), "patch": ("patch", 1.0), "dark": ("dark", 1.0),
    "r250": ("hammer", 0.8), "r250_case": ("hammer_case", 0.5), "bakelite": ("bakelite", 1.2), "limb": ("limb", 3.0),
    "dial": ("dial", 4.0), "win": ("win", 5.0), "needle": ("needle", 3.0), "visor": ("visor", 3.0),
    "meter7": ("meter7", 5.0), "meterf": ("meterf", 5.0),
    "jp": ("jp", 0.8), "jp_front": ("jp_front", 1.2), "jp_top": ("jp_top", 1.0), "frg": ("frg", 1.2),
    "silver": ("silver", 2.0), "bezel": ("bezel", 1.4), "knob": ("knob", 1.6), "ptr": ("ptr", 3.0),
    "key": ("key", 1.6), "key_w": ("key_w", 1.6),
    "lamp_g": ("lamp_g_off", 2.0), "lamp_r": ("lamp_r_off", 2.0), "led": ("led", 3.0),
    "spk": ("spk", 1.0), "pcb": ("pcb", 6.0), "chip": ("chip", 4.0), "lead": ("lead", 3.0), "solder": ("solder", 4.0),
    "cap_blue": ("cap_blue", 4.0), "card": ("card", 4.0), "wood": ("wood", 1.2), "pda": ("pda", 2.0),
    "pda_face": ("pda_face", 2.0), "paper": ("paper", 4.0), "mug": ("mug", 1.6), "tea": ("tea", 1.0),
    "coax": ("coax", 0.6), "cord": ("cord", 1.0), "ribbon": ("ribbon", 1.5), "wire_red": ("wire_red", 1.5),
    "tape": ("tape", 1.2), "pad_rubber": ("pad_rubber", 1.4),
}

# =============================================================================
# Materials
# =============================================================================


def decal(name, center, size, y_face, eps=0.0012):
    return (os.path.join(WORK, name), "y", -1, ("x", "z"), center, size, (y_face - eps, y_face + eps))


def rect(name, r, y_face):
    x0, x1, z0, z1 = r
    return decal(name, ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0), y_face)


def top_decal(name, r, z=None):
    x0, x1, y0, y1 = r
    return (os.path.join(WORK, name), "z", 1, ("x", "y"), ((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0, y1 - y0),
            None if z is None else (z - 0.0012, z + 0.0012))


RING_K = {"pointer": 4.4, "plain": 4.6, "skirt": 5.0, "dual": 5.0}


def rings(knobs, y):
    return [decal("decal_%s.png" % rg, (x, z), (r * RING_K[kind], r * RING_K[kind]), y)
            for x, z, r, kind, rg, _ in knobs if rg]


DIALS = [rect("decal_r250_meter.png", M_R, Y_FACE), rect("decal_r250_table.png", TB, YF - 0.0010)]
LIMB = [decal("decal_r250_limb.png", DISC[:2], (DISC[2] * 2.0, DISC[2] * 2.0), Y_DISC)]
TAGD = [rect("decal_tag.png", (TAG[0] - 0.034, TAG[0] + 0.034, TAG[1] - 0.014, TAG[1] + 0.014), YD - 0.0008)]
GNDD = [(os.path.join(WORK, "decal_ground.png"), "x", -1, ("y", "z"), (GROUND[0], GROUND[1] + 0.038), (0.030, 0.030),
         (X0 - 0.002, X0 + 0.0005))]
GRILLE7 = [top_decal("decal_r7_grille.png", (R7[0] + 0.070, R7[0] + 0.230, YF + 0.070, YF + 0.130), R7[3])]
PCBD = [top_decal("decal_reader_pcb.png", RDR_PCB)]
PADD = [top_decal("decal_notepad.png", PAD)]

KINDS = kmats.std_kinds(floor_z=0.0)
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# brown enamel of the Neutrals over a dark primer: chips on the edges, moderate rust, more near the floor
ENAMEL = dict(color=kmats.lin((92, 64, 46)), under=kmats.lin((62, 54, 48)), seed=2.1, gloss=0.40, spec=0.30,
              chip=(0.56, 0.62), rust=(0.62, 0.70), rust_low=0.8, floor_z=0.0, dust=0.4, grime=0.6)
# gray hammer-finish enamel of the R-250M2: old but intact; worn at the bar handles and the large knobs
HAMMER = dict(color=kmats.lin((150, 152, 150)), under=kmats.lin((70, 72, 74)), seed=2.9, gloss=0.40, spec=0.32,
              chip=(0.64, 0.70), rust=(0.70, 0.78), rust_low=0.3, floor_z=Z_R, dust=0.35, grime=0.45)
JP = dict(color=kmats.lin((34, 34, 36)), under=kmats.lin((96, 96, 98)), seed=3.7, gloss=0.30, spec=0.25,
          chip=(0.72, 0.78), rust=(0.99, 1.0), rust_low=0.0, floor_z=Z_A, dust=0.30, grime=0.30)
DOOR_RUB = [((XM + s * 0.04, YD - 0.01, ZH), (0.026, 0.05, 0.085), 0.55) for s in (-1, 1)] + \
           [((XM + 0.04, YD - 0.01, ZL), (0.020, 0.05, 0.020), 0.5)]
TRAY_RUB = [((0.0, TY0 - 0.02, ZS - 0.012), (0.11, 0.05, 0.025), 0.55)]
R250_RUB = [((x, YF - 0.01, (za + zb) / 2), (0.022, 0.05, (zb - za) / 2 + 0.012), 0.42) for x, za, zb in HANDLES_R250] + \
           [((x, YF - 0.01, z), (r * 1.5, 0.05, r * 1.5), 0.30) for x, z, r, _, _ in BIG_R250]


def mat_paint(mat, origin, rub=(), bare=kmats.lin((150, 146, 140)), hammer=False, **kw):
    """Paint (kmats.build_paint); hammer - hammer-finish enamel (from M06): dimples with dark edges and
    light bottoms, relief; rub - [(center, semi-axes, strength)]: rubbed by hands down to the primer and
    to the metal (at the door and shelf handles, the lock, the bar handles)."""
    outs = kmats.build_paint(mat, origin, **kw)
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    vec, sep = t.coords(origin, 17.0)
    col = kmats.sock(mat, outs["color"])
    res = dict(outs)
    if hammer:
        cells = t.noise(vec, 55.0, 2.0, 0.45)
        pit = t.maprange(cells, 0.38, 0.62, 0.0, 1.0)
        col = t.mixc(t.math("MULTIPLY", pit, 0.22), col, tuple(min(1.0, c * 1.25) for c in kw["color"][:3]) + (1,))
        col = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", 1.0, pit), 0.18), col,
                     tuple(c * 0.72 for c in kw["color"][:3]) + (1,))
        h = outs["height"]
        hh = t.math("ADD", kmats.sock(mat, h) if not isinstance(h, (int, float)) else h, t.math("MULTIPLY", pit, 0.35))
        res.update(color=kmats.Tree.ref(col), height=kmats.Tree.ref(hh))
    if rub:
        pos = sep.inputs[0].links[0].from_socket
        grain = t.maprange(t.noise(vec, 34.0, 8.0, 0.7), 0.3, 0.7, 0.55, 1.0)
        f = None
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
            near = t.maprange(ln.outputs["Value"], 0.3, 1.0, 1.0, 0.0)
            v = t.math("MULTIPLY", t.math("MULTIPLY", near, grain), k)
            f = v if f is None else t.math("MAXIMUM", f, v)
        f = t.math("ADD", f, t.math("MULTIPLY", t.noise(vec, 11.0, 10.0, 0.7), 0.25))
        prim = t.step(f, 0.42, 0.48)
        worn = t.step(f, 0.56, 0.62)
        col = t.mixc(t.math("MULTIPLY", prim, 0.75), col, kw["under"])
        col = t.mixc(worn, col, bare)
        g0 = kmats.sock(mat, outs["gloss"]) if isinstance(outs["gloss"], tuple) else outs["gloss"]
        s0 = kmats.sock(mat, outs["spec"]) if isinstance(outs["spec"], tuple) else outs["spec"]
        res.update(color=kmats.Tree.ref(col), gloss=kmats.Tree.ref(t.mixf(worn, g0, 0.58)),
                   spec=kmats.Tree.ref(t.mixf(worn, s0, 0.62)))
    return res


KINDS.update({
    "enamel": (mat_paint, ENAMEL),
    "enamel_panel": (mat_paint, dict(ENAMEL, color=kmats.lin((100, 70, 50)), seed=3.4, rust_low=0.0, floor_z=Z_A,
                                     decal_items=rings(K_P, YP))),
    "enamel_door": (mat_paint, dict(ENAMEL, seed=3.7, rub=DOOR_RUB)),
    "enamel_front": (mat_paint, dict(ENAMEL, color=kmats.lin((100, 70, 50)), seed=4.0, rust_low=0.2, floor_z=ZS - 0.5,
                                     rub=TRAY_RUB)),
    "rail": ("steel", dict(seed=6.1, tone=0.24, along="z", holes=(("x", "z"), 0.016, 0.28), dust=0.3, grime=0.5)),
    "dark": ("flat", dict(color=kmats.lin((22, 20, 18)), gloss=0.2, spec=0.1)),
    "chrome": ("steel", dict(seed=7.1, tone=0.36, along="z", gloss=0.70, spec=0.80, dust=0.15, grime=0.3)),
    "tag": ("paint", dict(CLEAN, color=kmats.lin((186, 188, 184)), gloss=0.45, spec=0.40, dust=0.1,
                          decal_items=TAGD + GNDD)),
    # shelf mat: old dark rubber, scuffed
    "mat": ("plastic", dict(color=kmats.lin((40, 38, 34)), gloss=0.10, spec=0.06, mottle=0.12, dust=0.35, grime=0.5,
                            scuff=(0.66, 0.76))),
    "seal": ("steel", dict(seed=8.8, tone=0.24, along="z", gloss=0.30, spec=0.35, dust=0.2, grime=0.4)),
    "patch": ("paint", dict(color=kmats.lin((150, 152, 148)), under=kmats.lin((112, 70, 40)), seed=7.3, gloss=0.45,
                            spec=0.5, chip=(0.50, 0.58), rust=(0.55, 0.64), rust_low=0.5, floor_z=0.0, dust=0.3,
                            grime=0.6)),
    "hammer": (mat_paint, dict(HAMMER, rub=R250_RUB, hammer=True, decal_items=rings(K_R250, YF))),
    "hammer_case": (mat_paint, dict(HAMMER, seed=3.1, hammer=True)),
    "bakelite": ("plastic", dict(color=kmats.lin((26, 22, 20)), gloss=0.55, spec=0.45, dust=0.2, mottle=0.08,
                                 scuff=(0.70, 0.78))),
    "limb": ("paint", dict(CLEAN, color=kmats.lin((24, 22, 20)), gloss=0.55, spec=0.45, decal_items=LIMB)),
    "dial": ("paint", dict(CLEAN, color=kmats.lin((236, 232, 218)), gloss=0.6, spec=0.4, decal_items=DIALS)),
    "win": ("paint", dict(CLEAN, color=kmats.lin((30, 28, 26)), gloss=0.85, spec=0.6,
                          decal_items=[rect("decal_r250_win_off.png", W_R, Y_WIN)])),
    "win_on": ("paint", dict(CLEAN, color=kmats.lin((30, 28, 26)), gloss=0.85, spec=0.6,
                             decal_items=[rect("decal_r250_win_on.png", W_R, Y_WIN)])),
    "meter7": ("paint", dict(CLEAN, color=kmats.lin((150, 140, 110)), gloss=0.6, spec=0.4,
                             decal_items=[rect("decal_r7000_meter_off.png", M_7, Y_FACE)])),
    "meter7_on": ("paint", dict(CLEAN, color=kmats.lin((246, 222, 150)), gloss=0.6, spec=0.4,
                                decal_items=[rect("decal_r7000_meter_on.png", M_7, Y_FACE)])),
    "meterf": ("paint", dict(CLEAN, color=kmats.lin((140, 146, 140)), gloss=0.6, spec=0.4,
                             decal_items=[rect("decal_frg_meter_off.png", M_F, Y_FACE)])),
    "meterf_on": ("paint", dict(CLEAN, color=kmats.lin((214, 240, 236)), gloss=0.6, spec=0.4,
                                decal_items=[rect("decal_frg_meter_on.png", M_F, Y_FACE)])),
    "needle": ("flat", dict(color=kmats.lin((20, 18, 18)), gloss=0.5, spec=0.3)),
    "visor": ("flat", dict(color=kmats.lin((176, 30, 24)), gloss=0.5, spec=0.3)),
    "jp": ("paint", JP),
    "jp_front": ("paint", dict(JP, seed=3.9, decal_items=rings(K_R7, YF) + rings(K_AR, YF))),
    "jp_top": ("paint", dict(JP, seed=4.3, decal_items=GRILLE7)),
    "frg": ("paint", dict(color=kmats.lin((156, 158, 156)), under=kmats.lin((60, 60, 62)), seed=4.8, gloss=0.42,
                          spec=0.35, chip=(0.74, 0.80), rust=(0.99, 1.0), rust_low=0.0, floor_z=Z_A, dust=0.3,
                          grime=0.3, decal_items=rings(K_FRG, YF))),
    # silver cast frame of the IC-R7000 window
    "silver": ("steel", dict(seed=8.2, tone=0.44, along="x", gloss=0.50, spec=0.55, dust=0.2, grime=0.3)),
    "bezel": ("plastic", dict(color=kmats.lin((24, 24, 25)), gloss=0.35, spec=0.25, dust=0.2, scuff=(0.70, 0.78))),
    "knob": ("plastic", dict(color=kmats.lin((26, 25, 24)), gloss=0.45, spec=0.35, dust=0.15, grime=0.2,
                             scuff=(0.66, 0.74))),
    "ptr": ("flat", dict(color=kmats.lin((226, 224, 214)), gloss=0.4, spec=0.3)),
    "key": ("plastic", dict(color=kmats.lin((96, 104, 98)), gloss=0.35, spec=0.25, dust=0.2, scuff=(0.62, 0.70))),
    "key_w": ("plastic", dict(color=kmats.lin((196, 194, 186)), gloss=0.40, spec=0.30, dust=0.2, scuff=(0.62, 0.70))),
    "lamp_g_off": ("flat", dict(color=kmats.lin((34, 64, 40)), gloss=0.85, spec=0.8)),
    "lamp_r_off": ("flat", dict(color=kmats.lin((72, 24, 22)), gloss=0.85, spec=0.8)),
    "lamp_g_on": ("flat", dict(color=kmats.lin((130, 255, 140)), gloss=0.85, spec=0.8)),
    "lamp_r_on": ("flat", dict(color=kmats.lin((255, 86, 60)), gloss=0.85, spec=0.8)),
    "led": ("flat", dict(color=kmats.lin((70, 14, 12)), gloss=0.85, spec=0.8)),
    "led_on": ("flat", dict(color=kmats.lin((255, 60, 40)), gloss=0.85, spec=0.8)),
    "spk": (mat_paint, dict(color=kmats.lin((88, 100, 114)), under=kmats.lin((58, 58, 60)), seed=5.6, gloss=0.38,
                            spec=0.3, chip=(0.62, 0.68), rust=(0.72, 0.80), rust_low=0.0, floor_z=Z_B, dust=0.5,
                            grime=0.4)),
    "pcb": ("paint", dict(CLEAN, color=kmats.lin((36, 88, 50)), gloss=0.55, spec=0.4, dust=0.2, decal_items=PCBD)),
    "chip": ("plastic", dict(color=kmats.lin((22, 22, 24)), gloss=0.35, spec=0.25, dust=0.1, grime=0.1,
                             scuff=(0.8, 0.9))),
    "lead": ("steel", dict(seed=7.7, tone=0.46, along="z", gloss=0.65, spec=0.7, dust=0.05, grime=0.15)),
    "solder": ("steel", dict(seed=7.9, tone=0.50, along="z", gloss=0.7, spec=0.7, dust=0.05, grime=0.2)),
    "cap_blue": ("plastic", dict(color=kmats.lin((34, 52, 118)), gloss=0.5, spec=0.35, dust=0.2, grime=0.3)),
    # PDA memory card in the reader slot: dark blue plastic
    "card": ("plastic", dict(color=kmats.lin((30, 40, 70)), gloss=0.45, spec=0.3, dust=0.1, scuff=(0.7, 0.8))),
    "wood": (kwood.build_wood, dict(color=kmats.lin((132, 100, 66)), seed=4.4, along="x", floor_z=ZM, dust=0.3,
                                    grime=0.5, knots=0.4)),
    "pda": ("plastic", dict(color=kmats.lin((70, 72, 74)), gloss=0.35, spec=0.25, dust=0.3, grime=0.4,
                            scuff=(0.6, 0.7))),
    "pda_face": ("plastic", dict(color=kmats.lin((48, 50, 52)), gloss=0.30, spec=0.22, dust=0.2, grime=0.3)),
    "paper": ("paint", dict(CLEAN, color=kmats.lin((226, 222, 204)), gloss=0.1, spec=0.05, decal_items=PADD)),
    # enameled mug: blue enamel, chips down to black iron
    "mug": ("paint", dict(color=kmats.lin((60, 84, 140)), under=kmats.lin((26, 26, 30)), seed=9.4, gloss=0.6,
                          spec=0.4, chip=(0.55, 0.61), rust=(0.70, 0.78), rust_low=0.0, floor_z=ZM, dust=0.15,
                          grime=0.4)),
    "tea": ("flat", dict(color=kmats.lin((70, 38, 18)), gloss=0.9, spec=0.6)),
    "coax": ("plastic", dict(color=kmats.lin((26, 26, 26)), gloss=0.30, spec=0.2, dust=0.4, scuff=(0.8, 0.9))),
    # headphone cord in a fabric braid
    "cord": ("plastic", dict(color=kmats.lin((96, 72, 48)), gloss=0.15, spec=0.1, mottle=0.2, dust=0.3)),
    "ribbon": ("plastic", dict(color=kmats.lin((132, 130, 124)), gloss=0.3, spec=0.2, dust=0.3, scuff=(0.8, 0.9))),
    "wire_red": ("plastic", dict(color=kmats.lin((160, 30, 26)), gloss=0.4, spec=0.3, dust=0.2)),
    # tape that fastens the antenna cable to the rail
    "tape": ("plastic", dict(color=kmats.lin((20, 20, 22)), gloss=0.5, spec=0.35, dust=0.3, scuff=(0.7, 0.8))),
    # headphone ear cushions: old soft rubber
    "pad_rubber": ("plastic", dict(color=kmats.lin((34, 30, 28)), gloss=0.18, spec=0.1, mottle=0.1, dust=0.2,
                                   scuff=(0.66, 0.76))),
})

OBJ, NAME = "m21_lnr_proc_trail", "ozr_lnr_proc_trail"
SEL_SCREEN, SEL_SCREEN2, SEL_SCREEN3, SEL_SCREEN4 = "ozl_screen", "ozl_screen_2", "ozl_screen_3", "ozl_screen_4"
SEL_LAMP, SEL_LAMP2 = "ozl_lamp", "ozl_lamp_2"
SEL_NEEDLE, SEL_NEEDLE2, SEL_NEEDLE3 = "ozl_needle", "ozl_needle_2", "ozl_needle_3"
SEL_DISC, SEL_VISOR = "ozl_tune_disc", "ozl_tune_visor"
# displays and screens have their own frame textures (kmodel panels): PNGs from make_decals.py
PANELS = {
    "vfd7": dict(off="decal_vfd7_off.png", frames=["decal_vfd7_f%02d.png" % i for i in range(8)], size=256, gloss=0.7),
    "vfdf": dict(off="decal_vfdf_off.png", frames=["decal_vfdf_f%02d.png" % i for i in range(6)], size=256, gloss=0.7),
    "lcd": dict(off="decal_lcd_off.png", frames=["decal_lcd_f%02d.png" % i for i in range(8)], size=256, gloss=0.5),
    "pda": dict(off="decal_pda_off.png", frames=["decal_pda_f%02d.png" % i for i in range(12)], size=256, gloss=0.5),
}
# wobble when "working" (OZL_WorkFx wobble): source -> (middle, amplitude, period in s)
WOBBLE = {"ozl_needle": (0.45, 0.10, 1.3), "ozl_needle_2": (0.55, 0.18, 0.7), "ozl_needle_3": (0.62, 0.06, 2.1),
          "ozl_tune": (0.50, 0.40, 11.0)}
A_REST, A_SPAN = 138.0, 96.0                                 # make_meter scale: from 138 to 42 degrees


def needle_geom(face):
    """Needle from the make_meter decal: the pivot is 0.08 of the height below the face, the length
    follows the scale arc (the decals are drawn in the proportions of their faces)."""
    x0, x1, z0, z1 = face
    w, h = x1 - x0, z1 - z0
    r = min(1.10 * h, 0.56 * w) * 0.80
    return ((x0 + x1) / 2, z0 - 0.08 * h), r * 1.02


NEEDLES = [(SEL_NEEDLE, M_R), (SEL_NEEDLE2, M_7), (SEL_NEEDLE3, M_F)]


def needle_axis(face):
    (cx, cz), _ = needle_geom(face)
    return (cx, Y_NEEDLE, cz)


# "working" preview: the needles, limb and cursor are mid-wobble (pose_move below)
_TUNE_MID = WOBBLE["ozl_tune"][0]
ON = dict(remap={"win": "win_on", "meter7": "meter7_on", "meterf": "meterf_on", "lamp_g_off": "lamp_g_on",
                 "lamp_r_off": "lamp_r_on", "led": "led_on"},
          emissive=(1.0, 1.0, 1.0, 1.0),
          move=dict([(sel, ("rot", needle_axis(fc), (0.0, 1.0, 0.0), math.radians(A_SPAN) * WOBBLE[sel][0]))
                     for sel, fc in NEEDLES] +
                    [(SEL_DISC, ("rot", (DISC[0], YF, DISC[1]), (0.0, 1.0, 0.0), 2 * math.pi * TUNE_TURNS * _TUNE_MID)),
                     (SEL_VISOR, (TUNE_RUN * _TUNE_MID, 0.0, 0.0))]))
ANIMS = tuple((sel, dict(type="rotation", source=sel, selection=sel, axis=sel + "_axis", memory=1, minValue=0.0,
                         maxValue=1.0, angle0=0.0, angle1=math.radians(A_SPAN))) for sel, _ in NEEDLES) + (
    (SEL_DISC, dict(type="rotation", source="ozl_tune", selection=SEL_DISC, axis=SEL_DISC + "_axis", memory=1,
                    minValue=0.0, maxValue=1.0, angle0=0.0, angle1=2 * math.pi * TUNE_TURNS)),
    (SEL_VISOR, dict(type="translation", source="ozl_tune", selection=SEL_VISOR, axis=SEL_VISOR + "_axis", memory=1,
                     minValue=0.0, maxValue=1.0, offset0=0.0, offset1=TUNE_RUN)),
)
SOURCES = {"ozl_needle": dict(animPeriod=0.2), "ozl_needle_2": dict(animPeriod=0.2), "ozl_needle_3": dict(animPeriod=0.2),
           "ozl_tune": dict(animPeriod=0.5)}
# vanilla items: by the card reader a screwdriver and a 9 V battery (with a block with wires), a pen on
# the sheet; two cassettes on the AR3000A (intercept recordings); tape on the loudspeaker
DECOR = [
    kv.put("screwdriver", (-0.3065, -0.522, ZM), **kv.flat(90)),
    kv.put("battery9v", (BAT[0], BAT[1], ZM), up=(0, 0, 1), fwd=(-0.3, -1, 0)),
    kv.put("pen", (0.122, -0.566, ZM + 0.004), **kv.flat(62)),
    kv.put("cassette", (-0.253, -0.262, AR[3]), **kv.flat(94)),
    kv.put("cassette", (-0.250, -0.252, AR[3] + 0.0105), **kv.flat(78)),
    kv.put("ducttape", (-0.052, -0.258, SPK[3]), **kv.flat(0)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.58, 0.60, 0.58), clear=0.08, edge=0.14, smudge=0.12, streaks=0.04),
                 selections=(SEL_SCREEN, SEL_SCREEN2, SEL_SCREEN3, SEL_SCREEN4, SEL_LAMP, SEL_LAMP2,
                             SEL_NEEDLE, SEL_NEEDLE2, SEL_NEEDLE3, SEL_DISC, SEL_VISOR),
                 hidden=(SEL_SCREEN, SEL_SCREEN2, SEL_SCREEN3, SEL_SCREEN4, SEL_LAMP, SEL_LAMP2), states={"on": ON},
                 bones=tuple((s, "") for s in (SEL_NEEDLE, SEL_NEEDLE2, SEL_NEEDLE3, SEL_DISC, SEL_VISOR)),
                 animations=ANIMS, decor=DECOR, panels=PANELS, sources=SOURCES)
P = M.part
BOUNDS = {}


# =============================================================================
# Preview pose: group rotation about an axis (needles, limb) on top of the kmodel shift (move), as in M06
# =============================================================================
def _split_move(move):
    tr, rot = {}, {}
    for k, v in (move or {}).items():
        if isinstance(v, tuple) and v and v[0] == "rot":
            rot[k] = v[1:]
        else:
            tr[k] = v
    return tr, rot


def _pose(parts, obs, rot):
    for p, ob in zip(parts, obs):
        if p.group in rot:
            piv, axis, ang = rot[p.group]
            pv = Vector(piv)
            ob.matrix_world = Matrix.Translation(pv) @ Matrix.Rotation(ang, 4, Vector(axis)) @ \
                Matrix.Translation(-pv) @ ob.matrix_world


_PLACE_LOOK, _PLACE = krender.place_look, krender.place


def pose_place_look(parts, kind_table, origin, remap=None, glow=1.5, sharp_deg=40.0, panels=None, move=None):
    tr, rot = _split_move(move)
    obs = _PLACE_LOOK(parts, kind_table, origin, remap=remap, glow=glow, sharp_deg=sharp_deg, panels=panels,
                      move=tr or None)
    _pose(parts, obs, rot)
    return obs


def pose_place(parts, tag, offset, mats, sharp_deg=40.0, move=None):
    tr, rot = _split_move(move)
    obs = _PLACE(parts, tag, offset, mats, sharp_deg=sharp_deg, move=tr or None)
    _pose(parts, obs, rot)
    return obs


krender.place_look, krender.place = pose_place_look, pose_place


# =============================================================================
# Small parts of the instrument face
# =============================================================================
def knobs(prefix, lst, lod, yf=YF, cap_reg="knob"):
    """Knobs from a list (x, z, r, kind, limb, angle): "beak", knurled, with a skirt, dual (the small
    knob of a dual one is cap_reg); the far LOD gets only the large ones."""
    parts = []
    for i, (x, z, r, kind, _, ang) in enumerate(lst):
        if lod == 2 and r < 0.015:
            continue
        uvk = ("knob_ptr%d_%d" % (round(ang), round(r * 1000))) if kind == "pointer" else \
              ("knob_%s%d" % (kind, round(r * 1000)))
        kb = P("%s_knob%d" % (prefix, i), "knob", uv_name=uvk, uv_origin=(x, yf, z))
        pt = P("%s_knob%d_ptr" % (prefix, i), "ptr", uv_name="%s_knob_ptr%d" % (prefix, i), uv_origin=(x, yf, z))
        cp = None
        if kind == "pointer":
            b.pointer_knob(kb, pt, x, yf, z, r, lod, angle=ang)
        else:
            cp = P("%s_knob%d_cap" % (prefix, i), cap_reg, uv_name="knob_cap%d" % round(r * 1000), uv_origin=(x, yf, z)) \
                if kind == "dual" else None
            b.knob(kb, pt, x, yf, z, r, kind, lod, angle=ang, cap=cp)
        parts += [p for p in (kb, pt, cp) if p is not None and p.bm.faces]
    return parts


def sockets(prefix, lst, lod, yf=YF):
    """BNC jacks; the occupied ones get a plug with a boot (their own functions build the cable to it).
    Near LOD only."""
    parts = []
    if lod > 0:
        return parts
    for i, (x, z, plugged) in enumerate(lst):
        nut = P("%s_bnc%d_nut" % (prefix, i), "steel", uv_name="bnc_nut", uv_origin=(x, yf, z))
        bd = P("%s_bnc%d" % (prefix, i), "chrome", uv_name="bnc_body%d" % (0 if plugged else 1), uv_origin=(x, yf, z))
        b.bnc_socket(nut, bd, x, yf, z, lod, studs=not plugged)
        parts += [p for p in (nut, bd) if p.bm.faces]
        if plugged:
            sl = P("%s_plug%d" % (prefix, i), "chrome", uv_name="plug_sleeve", uv_origin=(x, yf, z))
            bt = P("%s_plug%d_boot" % (prefix, i), "rubber", uv_name="plug_boot", uv_origin=(x, yf, z))
            b.bnc_plug(sl, bt, x, yf, z, lod)
            parts += [sl, bt]
    return parts


def plug_end(x, z, yf=YF):
    """End of the BNC plug boot in the jack (x, z) on face yf - where the cable leaves."""
    return (x, yf - 0.045, z)


def toggles(prefix, lst, lod, yf=YF):
    parts = []
    if lod == 2:
        return parts
    for i, (x, z) in enumerate(lst):
        nut = P("%s_tg%d" % (prefix, i), "steel", uv_name="toggle_nut", uv_origin=(x, yf, z))
        lv = P("%s_tg%d_lever" % (prefix, i), "chrome", uv_name="toggle_lever", uv_origin=(x, yf, z))
        b.toggle(nut, lv, x, yf, z, lod)
        parts += [p for p in (nut, lv) if p.bm.faces]
    return parts


def lamp(name, x, z, reg, sel, lod, yf=YF):
    """Signal lamp: the lens is in the lamp selection on all LODs, the bezel on the near ones."""
    lens = P(name, reg, uv_name="lamp_" + reg, uv_origin=(x, yf, z), group=sel)
    rim = P(name + "_rim", "chrome", uv_name="lamp_rim", uv_origin=(x, yf, z)) if lod == 0 else None
    b.lamp(rim, lens, x, yf, z, lod)
    return [p for p in (rim, lens) if p is not None]


def jacks(prefix, lst, lod, yf=YF, r=0.0055):
    """Phone jacks: ring and dark bottom (near LODs)."""
    if lod == 2:
        return []
    parts = []
    for i, (x, z) in enumerate(lst):
        rim = P("%s_jack%d" % (prefix, i), "chrome", uv_name="jack_rim%d" % round(r * 10000), uv_origin=(x, yf, z))
        hole = P("%s_jack%d_hole" % (prefix, i), "dark", uv_name="jack_hole%d" % round(r * 10000), uv_origin=(x, yf, z)) \
            if lod == 0 else None
        b.phone_jack(rim, hole, x, yf, z, lod, r=r)
        parts += [p for p in (rim, hole) if p is not None]
    return parts


def keys(prefix, lst, lod, yf=YF, depth=0.004):
    """Keys (x, z, width, height, is white): caps with chamfered edges; near LOD only."""
    if lod > 0:
        return []
    out = {}
    for x, z, w, h, white in lst:
        reg = "key_w" if white else "key"
        if reg not in out:
            out[reg] = P("%s_%s" % (prefix, reg), reg)
        b.key_cap(out[reg], x, yf, z, w, h, depth=depth, ch=min(0.0012, 0.22 * min(w, h)))
    return list(out.values())


def screws(name, pts, lod, yf=YF, r=0.0034):
    if lod > 0:
        return []
    sc = P(name, "steel")
    for x, z in pts:
        b.screw(sc, x, yf, z, r)
    return [sc]


def screen(name, r, sec, sel, lod, y=Y_FACE, hood=0.004, margin=0.004, radius=0.003, glass=True):
    """Display or screen: a face with its own texture (section sec, selection sel; on the far LOD a black
    atlas cell without a selection), a rounded-corner frame (hood - projection, or None), glass."""
    x0, x1, z0, z1 = r
    cx, cz, w, h = (x0 + x1) / 2, (z0 + z1) / 2, x1 - x0, z1 - z0
    if lod == 2:
        fc = P(name, "black")
        g.box(fc, x0, x1, y, YF - 0.0005, z0, z1)
        return [fc]
    fc = P(name, "black", group=sel, section=sec)
    g.quad(fc, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)])
    parts = [fc]
    if hood:
        hd = P(name + "_hood", "bezel")
        b.bezel(hd, cx, cz, (w + 2 * margin, h + 2 * margin, radius), (w + 0.001, h + 0.001, radius * 0.5), YF,
                YF - hood, y_in=y, n=2 if lod == 0 else 1)
        parts.append(hd)
    if glass:
        gl = P(name + "_glass", "bezel", section="glass")
        yg = YF - 0.0035
        g.quad(gl, [(x0, yg, z0), (x1, yg, z0), (x1, yg, z1), (x0, yg, z1)])
        parts.append(gl)
    return parts


def meter(name, r, region, sel, lod, group="body", frame=None, depth=0.005, glass=True):
    """Needle gauge: a face with a scale (region, decal; group - the backlight selection), a rounded-
    corner holder (frame - (width, height, radius), or None for no holder of its own), glass, a needle
    (bone sel): a thin tapering strip with a counterweight, from the pivot up-left (the scale zero)."""
    x0, x1, z0, z1 = r
    cx, cz, w, h = (x0 + x1) / 2, (z0 + z1) / 2, x1 - x0, z1 - z0
    fc = P(name, region, group=group)
    g.box(fc, x0, x1, Y_FACE, YF - 0.0005, z0, z1)
    parts = [fc]
    if lod == 2:
        return parts
    if frame:
        bz = P(name + "_bezel", "bakelite" if frame[0] > 0.07 else "bezel")
        b.bezel(bz, cx, cz, frame, (w, h, 0.0015), YF, YF - depth, y_in=Y_FACE, n=2 if lod == 0 else 1)
        parts.append(bz)
    if glass:
        gl = P(name + "_glass", "bezel", section="glass")
        yg = YF - 0.0040
        g.quad(gl, [(x0, yg, z0), (x1, yg, z0), (x1, yg, z1), (x0, yg, z1)])
        parts.append(gl)
    (px, pz), ln = needle_geom(r)
    nd = P(name + "_needle", "needle", group=sel)
    a = math.radians(A_REST)
    u = Vector((math.cos(a), 0.0, math.sin(a)))
    fr = g.Frame((px, Y_NEEDLE, pz), u, b.FRONT.cross(u), b.FRONT)
    poly = [(-0.16 * ln, -0.0010), (0.0, -0.0008), (ln, -0.00022), (ln, 0.00022), (0.0, 0.0008), (-0.16 * ln, 0.0010)]
    g.prism(nd, poly, (0, 1), 0.0, 0.0005, frame=fr)
    parts.append(nd)
    return parts


def case(name, box, front_reg, case_reg, lod, feet=FOOT, front=0.006):
    """Case of a tabletop instrument: a front panel with a chamfer, a cover with rounded edges behind
    it, front feet; the far LOD gets only the panel."""
    x0, x1, z0, z1, depth = box
    za = z0 + feet
    pn = P(name + "_front", front_reg)
    g.box(pn, x0, x1, YF, YF + front, za, z1, **(dict(r=0.0018, seg=2) if lod == 0 else {}))
    parts = [pn]
    if lod == 2:
        return parts
    cs = P(name + "_case", case_reg)
    g.box(cs, x0 + 0.001, x1 - 0.001, YF + front, YF + depth, za + 0.0005, z1, **(dict(r=0.004, seg=2) if lod == 0 else {}))
    parts.append(cs)
    if lod == 0 and feet > 0.002:
        ft = P(name + "_feet", "rubber")
        for x in (x0 + 0.028, x1 - 0.028):
            b.lathe(ft, (x, YF + 0.030, z0), (0, 0, 1), [(0.0075, 0.0), (0.0075, feet - 0.0015), (0.0060, feet)], 8)
        parts.append(ft)
    return parts


def hang(a, c, drop, out=0.012, n=6):
    """Sagging wire between the ends of boots a and c (from M06): leaves the boot forward, sags by drop
    and bulges forward by out in the middle (a smooth arc, not a "check mark")."""
    a, c = Vector(a), Vector(c)
    pts = [tuple(a), tuple(a + Vector((0.0, -0.008, -0.003)))]
    for i in range(1, n):
        t = i / n
        k = math.sin(math.pi * t)
        pts.append(tuple(a.lerp(c, t) + Vector((0.0, -0.008 - out * k, -0.003 - drop * k ** 1.2))))
    pts += [tuple(c + Vector((0.0, -0.008, -0.003))), tuple(c)]
    return pts


def cable(name, region, pts, r, lod, k=2):
    """Cable along a spline through the points (near LOD - smooth, k points per span; mid LOD - fewer)."""
    c = P(name, region)
    if lod == 0:
        g.pipe(c, b.spline(pts, k), r, 6)
    elif lod == 1:
        g.pipe(c, b.spline(pts, 1), r, 4)
    else:
        g.pipe(c, [pts[0], pts[len(pts) // 2], pts[-1]], r, 3)
    return [c]


def tape_wrap(part, c, axis, r, length=0.020):
    """A few turns of tape around a cable of radius r at point c (cable axis - axis): a sleeve with
    slightly beveled edges."""
    a = Vector(axis).normalized()
    base = Vector(c) - a * (length / 2)
    b.lathe(part, base, a, [(r + 0.0004, 0.0), (r + 0.0011, 0.0015), (r + 0.0012, length - 0.0015),
                            (r + 0.0004, length)], 10, cap1=False)


# =============================================================================
# Rack (its own copy with the small parts - m21_rack.py) and the patch panel
# =============================================================================
def build_rack(spec):
    lod = spec["lod"]
    parts = rk.instrument_rack(M, spec, X0, X1, Y0, Y1, H, CELLS, slide=dict(z=ZS, pull=PULL, depth=SDEPTH),
                               regions=dict(front="rk_front"), tag=TAG, ground=GROUND, eyebolts=EYES)
    # patch panel: lamps on all LODs
    parts += lamp("patch_lamp_g", 0.060, ZP, "lamp_g", SEL_LAMP, lod, yf=YP)
    parts += lamp("patch_lamp_r", 0.100, ZP, "lamp_r", SEL_LAMP2, lod, yf=YP)
    if lod == 2:
        return parts
    parts += knobs("patch", K_P, lod, yf=YP)
    parts += sockets("patch", BNC_P, lod, yf=YP)
    parts += jacks("patch", [JACK_PHONES, JACK_SPK], lod, yf=YP, r=0.0060)
    parts += toggles("patch_switch", [(0.275, ZP)], lod, yf=YP)
    if lod == 0:
        # jumper between jacks 2 and 3 - sags in an arc
        parts += cable("patch_cord", "coax", hang(plug_end(BNC_P[2][0], ZP, YP), plug_end(BNC_P[3][0], ZP, YP), 0.034,
                                                  out=0.010, n=6), 0.0032, lod)
        # patch on the left door: tin on rivets over a rusted spot (above the louvers)
        xm = (XI0 + XI1) / 2
        pt = P("door_patch", "patch")
        g.box(pt, XI0 + 0.032, xm - 0.085, YD - 0.0016, YD, 0.300, 0.420, r=0.0006, seg=1)
        parts.append(pt)
        rv = P("door_rivets", "steel")
        for x in (XI0 + 0.042, (XI0 + xm) / 2 - 0.026, xm - 0.095):
            for z in (0.310, 0.410):
                b.lathe(rv, (x, YD - 0.0016, z), b.FRONT, [(0.0030, 0.0), (0.0024, 0.0010), (0.0, 0.0016)], 8)
        parts.append(rv)
        # hook for the headphones: a rod from the grille panel, a nut at the base, the tip bent up
        hk = P("hook", "steel")
        hx, hy, hz = HOOK
        g.pipe(hk, b.spline([(hx, Y0 - 0.003, Z_V + 0.007), (hx, Y0 - 0.014, Z_V + 0.004), (hx, Y0 - 0.030, hz + 0.008),
                             (hx, hy + 0.004, hz + 0.0022), (hx, hy - 0.004, hz + 0.0030), (hx, hy - 0.008, hz + 0.012)],
                            2), 0.0022, 6)
        b.lathe(hk, (hx, Y0 - 0.003, Z_V + 0.007), b.FRONT, [(0.0045, 0.0), (0.0045, 0.0030)], 6, ref=(1, 0, 0))
        parts.append(hk)
    return parts


# =============================================================================
# R-250M2
# =============================================================================
def build_r250(spec):
    """R-250M2: two screwed panels of gray hammer-finish enamel, four bar handles; at the top a gauge in
    a square bakelite holder, a fine-tuning limb with a pin handle (bone ozl_tune_disc), the range
    switch, the SR-50 antenna input, knobs, toggles, lamps; at the bottom the bakelite surround of the
    scale window with a cursor (bone ozl_tune_visor), the subrange table, two large tuning knobs, phone
    jacks, a volume knob, a jack block."""
    lod = spec["lod"]
    x0, x1, z0, z1, depth = R250
    parts = []
    pn = P("r250_panels", "r250")
    for za, zb in ((z0, ZSPLIT - 0.0015), (ZSPLIT + 0.0015, z1)):
        g.box(pn, x0, x1, YF, YF + 0.006, za, zb, **(dict(r=0.0025, seg=2) if lod == 0 else {}))
    parts.append(pn)
    # scale surround: a bakelite block with rounded corners, the window (backlight - ozl_lamp), the limb
    hs = P("r250_housing", "bakelite")
    hx, hz = (HOUS[0] + HOUS[1]) / 2, (HOUS[2] + HOUS[3]) / 2
    b.plate(hs, hx, hz, HOUS[1] - HOUS[0], HOUS[3] - HOUS[2], 0.010 if lod < 2 else 0.0, YF, Y_HOUS,
            n=3 if lod == 0 else 1)
    parts.append(hs)
    wf = P("r250_win", "win", group=SEL_LAMP)
    g.box(wf, W_R[0], W_R[1], Y_WIN, Y_HOUS + 0.0004, W_R[2], W_R[3])
    parts.append(wf)
    dk = P("r250_disc", "limb", group=SEL_DISC)
    b.lathe(dk, (DISC[0], YF, DISC[1]), b.FRONT, [(DISC[2], 0.0), (DISC[2], 0.012), (DISC[2] - 0.002, 0.014)],
            (32, 14, 8)[lod])
    parts.append(dk)
    for i, (x, z, r, teeth, pa) in enumerate(BIG_R250):
        kb = P("r250_big%d" % i, "bakelite")
        pin = P("r250_big%d_pin" % i, "bakelite") if lod == 0 else None
        b.crank_knob(kb, pin, x, YF, z, r, lod, pin_angle=pa, teeth=teeth)
        parts += [p for p in (kb, pin) if p is not None]
    parts += lamp("r250_lamp_r", -0.252, 0.955, "lamp_r", SEL_LAMP, lod) + \
        lamp("r250_lamp_g", -0.218, 0.955, "lamp_g", SEL_LAMP, lod)
    if lod == 2:
        return parts
    cs = P("r250_case", "r250_case")
    g.box(cs, x0 + 0.004, x1 - 0.004, YF + 0.006, YF + depth, z0 + 0.004, z1 - 0.004,
          **(dict(r=0.006, seg=2) if lod == 0 else {}))
    parts.append(cs)
    # scale window frame - a bakelite lip, glass, the cursor (a red thread)
    lip = P("r250_win_lip", "bakelite")
    wx, wz, ww, wh = (W_R[0] + W_R[1]) / 2, (W_R[2] + W_R[3]) / 2, W_R[1] - W_R[0], W_R[3] - W_R[2]
    b.bezel(lip, wx, wz, (ww + 0.016, wh + 0.016, 0.006), (ww + 0.002, wh + 0.002, 0.002), Y_HOUS, Y_HOUS - 0.006,
            y_in=Y_WIN, n=2 if lod == 0 else 1)
    parts.append(lip)
    gl = P("r250_win_glass", "bezel", section="glass")
    yg = Y_HOUS - 0.0035
    g.quad(gl, [(W_R[0], yg, W_R[2]), (W_R[1], yg, W_R[2]), (W_R[1], yg, W_R[3]), (W_R[0], yg, W_R[3])])
    parts.append(gl)
    vs = P("r250_visor", "visor", group=SEL_VISOR)
    g.box(vs, VISOR_X - 0.0007, VISOR_X + 0.0007, Y_WIN - 0.0016, Y_WIN - 0.0008, SCALE_Z[0] + 0.0012, SCALE_Z[1] - 0.0012)
    parts.append(vs)
    # gauge: a square bakelite holder, face, glass, needle (bone ozl_needle)
    parts += meter("r250_meter", M_R, "dial", SEL_NEEDLE, lod, frame=(0.084, 0.078, 0.007), depth=0.009)
    # fine-tuning knob on the limb: bakelite with a pin (turns with the limb); a pointer mark above the limb
    kb = P("r250_disc_knob", "bakelite", group=SEL_DISC)
    pin = P("r250_disc_pin", "bakelite", group=SEL_DISC) if lod == 0 else None
    b.crank_knob(kb, pin, DISC[0], Y_DISC, DISC[1], 0.024, lod, pin_angle=135.0, teeth=False)
    parts += [p for p in (kb, pin) if p is not None]
    if lod == 0:
        ix = P("r250_index", "ptr")
        zi = DISC[1] + DISC[2] + 0.0025
        g.prism(ix, [(DISC[0] - 0.003, zi + 0.004), (DISC[0] + 0.003, zi + 0.004), (DISC[0], zi)], (0, 2), YF - 0.0008, YF)
        parts.append(ix)
    # subrange table: a plate on four rivets
    tb = P("r250_table", "dial")
    b.plate(tb, (TB[0] + TB[1]) / 2, (TB[2] + TB[3]) / 2, TB[1] - TB[0], TB[3] - TB[2], 0.003, YF, YF - 0.0010)
    parts.append(tb)
    # knobs, toggles, jacks, the antenna input
    parts += knobs("r250", K_R250, lod)
    parts += toggles("r250", TOG_R250, lod)
    parts += jacks("r250", JACKS_R250, lod)
    fl = P("r250_ant_flange", "steel")
    bd = P("r250_ant", "chrome")
    sc = P("r250_ant_screws", "steel") if lod == 0 else None
    b.sr50(fl, bd, sc, ANT[0], YF, ANT[1], lod)
    parts += [p for p in (fl, bd, sc) if p is not None]
    # bar handles with bosses
    hd = P("r250_handles", "chrome")
    bo = P("r250_handle_bosses", "chrome") if lod == 0 else None
    for x, za, zb in HANDLES_R250:
        b.u_handle(hd, (x, YF, za), (x, YF, zb), (0, -1, 0), 0.028, 0.0055, lod=lod, bosses=bo)
    parts += [p for p in (hd, bo) if p is not None]
    if lod == 0:
        # jack block: a bakelite strip with five holes
        sp = P("r250_strip", "bakelite")
        b.plate(sp, (STRIP[0] + STRIP[1]) / 2, (STRIP[2] + STRIP[3]) / 2, STRIP[1] - STRIP[0], STRIP[3] - STRIP[2], 0.003,
                YF, YF - 0.005)
        sh = P("r250_strip_holes", "dark")
        for k in range(5):
            xk = STRIP[0] + 0.012 + (STRIP[1] - STRIP[0] - 0.024) * k / 4
            b.lathe(sh, (xk, YF - 0.0052, (STRIP[2] + STRIP[3]) / 2), b.FRONT, [(0.0024, 0.0)], 8)
        parts += [sp, sh]
        # screws of the panels, of the scale surround and of the table; scale correctors on the surround
        pts = []
        for za, zb in ((z0, ZSPLIT), (ZSPLIT, z1)):
            pts += [(x, z) for x in (x0 + 0.011, x1 - 0.011) for z in (za + 0.011, zb - 0.011)]
            pts += [(0.0, zb - 0.011)]
        parts += screws("r250_screws", pts, lod)
        parts += screws("r250_housing_screws", [(HOUS[0] + 0.008, HOUS[2] + 0.008), (HOUS[1] - 0.008, HOUS[2] + 0.008),
                                                (HOUS[0] + 0.008, HOUS[3] - 0.008), (HOUS[1] - 0.008, HOUS[3] - 0.008),
                                                (-0.118, 0.708), (0.118, 0.708)], lod, yf=Y_HOUS, r=0.0030)
        parts += screws("r250_table_rivets", [(TB[0] + 0.005, TB[2] + 0.005), (TB[1] - 0.005, TB[2] + 0.005),
                                              (TB[0] + 0.005, TB[3] - 0.005), (TB[1] - 0.005, TB[3] - 0.005)], lod,
                        yf=YF - 0.0010, r=0.0018)
    return parts


# =============================================================================
# IC-R7000, FRG-7700, AR3000A
# =============================================================================
def build_r7000(spec):
    """IC-R7000: black; the S-meter and display under one glass in a silver frame, the keypad in its own
    frame on the right, a tuning knob with a dimple, dual knobs, buttons, jacks, a stand."""
    lod = spec["lod"]
    x0, x1, z0, z1, depth = R7
    parts = case("r7", R7, "jp_front", "jp_top", lod)
    parts += meter("r7_meter", M_7, "meter7", SEL_NEEDLE2, lod, group=SEL_LAMP, glass=False)
    parts += screen("r7_vfd", D_7, "vfd7", SEL_SCREEN, lod, hood=None, glass=False)
    kb = P("r7_tune", "knob")
    tx, tz, tr = TUNE_7
    if lod == 0:
        # tuning knob: a skirt with a knurled rubber holder, body, an end with a finger dimple
        b.lathe(kb, (tx, YF, tz), b.FRONT, [(tr * 1.15, 0.0), (tr * 1.15, 0.0030), (tr, 0.0050),
                                            (tr, 0.0200), (tr * 0.93, 0.0235), (tr * 0.50, 0.0250), (0.0, 0.0252)], 20,
                knurl=(2, 3), depth=0.0010)
        dm = P("r7_tune_dimple", "rubber")
        b.lathe(dm, (tx + 0.010, YF - 0.0252, tz - 0.008), b.FRONT, [(0.0062, 0.0), (0.0050, 0.0006)], 12)
        parts.append(dm)
    else:
        b.lathe(kb, (tx, YF, tz), b.FRONT, [(tr * 1.12, 0.0), (tr, 0.004), (tr, 0.022)], 8 if lod == 1 else 6)
    parts.append(kb)
    if lod == 2:
        return parts
    # common window frame (cast, silver), a dark background between the S-meter and the display; the glass
    # is above the needle (the display has its own texture with a light filter; under gray glass it looked
    # washed out in the preview)
    wx0, wx1, wz0, wz1 = WF_7
    wf = P("r7_window", "silver")
    b.bezel(wf, (wx0 + wx1) / 2, (wz0 + wz1) / 2, (wx1 - wx0, wz1 - wz0, 0.003),
            (wx1 - wx0 - 0.007, wz1 - wz0 - 0.007, 0.0015), YF, YF - 0.0045, y_in=Y_FACE, n=2 if lod == 0 else 1)
    parts.append(wf)
    bg = P("r7_window_back", "dark")
    g.box(bg, wx0 + 0.003, wx1 - 0.003, YF - 0.0010, YF - 0.0005, wz0 + 0.003, wz1 - 0.003)
    parts.append(bg)
    gl = P("r7_glass", "bezel", section="glass")
    yg = YF - 0.0038
    g.quad(gl, [(M_7[0] - 0.001, yg, M_7[2] - 0.001), (M_7[1] + 0.001, yg, M_7[2] - 0.001),
                (M_7[1] + 0.001, yg, M_7[3] + 0.001), (M_7[0] - 0.001, yg, M_7[3] + 0.001)])
    parts.append(gl)
    parts += knobs("r7", K_R7, lod)
    if lod == 0:
        # keypad frame, remote-control window; buttons; power key; jacks; stand
        kp = P("r7_keypad", "bezel")
        b.bezel(kp, (KP_7[0] + KP_7[1]) / 2, (KP_7[2] + KP_7[3]) / 2, (KP_7[1] - KP_7[0], KP_7[3] - KP_7[2], 0.003),
                (KP_7[1] - KP_7[0] - 0.004, KP_7[3] - KP_7[2] - 0.004, 0.002), YF, YF - 0.0020, n=2)
        parts.append(kp)
        rw = P("r7_remote_window", "dark")
        g.box(rw, x0 + 0.236, x0 + 0.278, YF - 0.0012, YF, z1 - 0.016, z1 - 0.008)
        parts.append(rw)
        parts += keys("r7_keys", KEYS_R7, lod)
        pw = P("r7_power", "key_w")
        b.key_cap(pw, x0 + 0.016, YF, R7A + 0.040, 0.009, 0.022, depth=0.004, ch=0.0012)
        parts.append(pw)
        parts += jacks("r7", [(x0 + 0.014, R7A + 0.012), (x0 + 0.030, R7A + 0.012)], lod, r=0.0035)
        st = P("r7_stand", "steel")
        g.pipe(st, b.spline([(x0 + 0.05, YF + 0.03, z0 + 0.0022), (x0 + 0.05, YF - 0.002, z0 + 0.0022),
                             (x0 + 0.058, YF - 0.010, z0 + 0.0022), (x1 - 0.058, YF - 0.010, z0 + 0.0022),
                             (x1 - 0.05, YF - 0.002, z0 + 0.0022), (x1 - 0.05, YF + 0.03, z0 + 0.0022)], 2), 0.0020, 6)
        parts.append(st)
    return parts


def build_frg(spec):
    """FRG-7700: a gray panel on a black case, the S-meter on the left, the display on the right, the
    tuning knob in the center, a row of knobs below, buttons under the display and by the S-meter, a
    phone jack."""
    lod = spec["lod"]
    x0, x1, z0, z1, _ = FRG
    parts = case("frg", FRG, "frg", "jp", lod)
    parts += meter("frg_meter", M_F, "meterf", SEL_NEEDLE3, lod, group=SEL_LAMP, frame=(M_F[1] - M_F[0] + 0.010,
                                                                                      M_F[3] - M_F[2] + 0.010, 0.004))
    parts += screen("frg_vfd", D_F, "vfdf", SEL_SCREEN2, lod, hood=0.005, margin=0.005, radius=0.003, glass=False)
    tx, tz, tr = TUNE_F
    kb = P("frg_tune", "knob")
    if lod == 0:
        b.lathe(kb, (tx, YF, tz), b.FRONT, [(tr * 1.16, 0.0), (tr * 1.16, 0.0035), (tr, 0.0058),
                                            (tr, 0.0210), (tr * 0.94, 0.0245), (tr * 0.55, 0.0262), (0.0, 0.0264)], 20,
                knurl=(2, 3), depth=0.0010)
        dm = P("frg_tune_dimple", "knob")
        b.lathe(dm, (tx - 0.011, YF - 0.0264, tz + 0.009), b.FRONT, [(0.0058, 0.0), (0.0046, 0.0006)], 12)
        parts.append(dm)
    else:
        b.lathe(kb, (tx, YF, tz), b.FRONT, [(tr * 1.12, 0.0), (tr, 0.004), (tr, 0.024)], 8 if lod == 1 else 6)
    parts.append(kb)
    if lod == 2:
        return parts
    parts += knobs("frg", K_FRG, lod)
    if lod == 0:
        parts += keys("frg_keys", KEYS_FRG, lod)
        parts += jacks("frg", [(x1 - 0.118, FRA + 0.016)], lod, r=0.0042)
        parts += screws("frg_screws", [(x0 + 0.006, FRA + 0.008), (x1 - 0.006, FRA + 0.008), (x0 + 0.006, z1 - 0.007),
                                       (x1 - 0.006, z1 - 0.007)], lod, r=0.0022)
    return parts


def build_ar(spec):
    """AR3000A: black, the LCD on the left in a frame, a 4 x 4 keypad on the right, a dual volume and
    squelch knob, a tuning knob, a phone jack."""
    lod = spec["lod"]
    x0, x1, z0, z1, _ = AR
    parts = case("ar", AR, "jp_front", "jp", lod, feet=0.004)
    parts += screen("ar_lcd", L_A, "lcd", SEL_SCREEN3, lod, hood=0.004, margin=0.004, radius=0.002, glass=False)
    if lod == 2:
        return parts
    parts += knobs("ar", K_AR, lod)
    if lod == 0:
        parts += keys("ar_keys", KEYS_AR, lod, depth=0.0035)
        parts += jacks("ar", [(x0 + 0.078, ARA + 0.010)], lod, r=0.0030)
    return parts


def build_speaker(spec):
    """Loudspeaker: a steel box of gray-blue enamel with rounded edges, three stamped louver hoods and
    dark slots under them, screws, rubber feet."""
    lod = spec["lod"]
    x0, x1, z0, z1, depth = SPK
    bx = P("spk_box", "spk")
    g.box(bx, x0, x1, YF, YF + depth, z0 + 0.004, z1, **(dict(r=0.007, seg=2) if lod == 0 else
                                                       (dict(r=0.006, seg=1) if lod == 1 else {})))
    parts = [bx]
    if lod == 2:
        return parts
    sl = P("spk_slots", "dark")
    lv = P("spk_louvres", "spk")
    for k in range(3):
        zt = z0 + 0.150 - 0.045 * k
        g.box(sl, x0 + 0.030, x1 - 0.030, YF - 0.0008, YF, zt - 0.028, zt - 0.003)
        if lod == 0:
            b.hood_louvre(lv, x0 + 0.026, x1 - 0.026, YF, zt, 0.030, 0.011, t=0.0014, n=6)
        else:
            g.box(lv, x0 + 0.026, x1 - 0.026, YF - 0.010, YF, zt - 0.004, zt)
    parts += [sl, lv]
    if lod == 0:
        parts += screws("spk_screws", [(x, z) for x in (x0 + 0.012, x1 - 0.012) for z in (z0 + 0.016, z1 - 0.012)], lod,
                        r=0.0030)
        ft = P("spk_feet", "rubber")
        for x in (x0 + 0.025, x1 - 0.025):
            b.lathe(ft, (x, YF + 0.025, z0), (0, 0, 1), [(0.008, 0.0), (0.008, 0.0028), (0.0065, 0.0040)], 10)
        parts.append(ft)
    return parts


# =============================================================================
# TON-2 headphones on a hook
# =============================================================================
def build_phones(spec):
    """TON-2 headphones: the steel headband lies as an arc on the hook, at its ends are sliders and
    yokes holding bakelite capsules (a domed back, a cap nut) with rubber ear cushions facing each
    other; a fabric-braided cord from the left capsule sags to the plug in a patch-panel jack."""
    lod = spec["lod"]
    if lod == 2:
        return []
    hx, hy, hz = HOOK
    R = BAND_R
    zc = hz + 0.0022 + 0.0016 - R                            # arc center: the top of the headband is on the hook
    n = 16 if lod == 0 else 6
    band = [(hx + R * math.cos(math.pi * k / n), hy, zc + R * math.sin(math.pi * k / n)) for k in range(n + 1)]
    bd = P("phones_band", "steel")
    g.sweep(bd, band, (0, 1, 0), 0.0015, 0.0070)
    parts = [bd]
    cup = P("phones_cups", "bakelite")
    pad = P("phones_pads", "pad_rubber")
    yk = P("phones_yokes", "steel")
    ends = []
    for s in (-1, 1):
        xe = hx + s * R
        # slider: a plate down from the end of the headband; yoke - a bracket with pivots on the sides of the capsule
        g.box(yk, xe - 0.0016, xe + 0.0016, hy - 0.0055, hy + 0.0055, zc - 0.022, zc + 0.002)
        xc = xe + s * 0.004                                  # capsule axis (across - x)
        zcap = zc - 0.050
        if lod == 0:
            for sy in (-1, 1):
                g.pipe(yk, [(xe, hy + sy * 0.006, zc - 0.022), (xe + s * 0.0015, hy + sy * 0.026, zc - 0.030),
                            (xe + s * 0.0025, hy + sy * 0.035, zcap + 0.010), (xe + s * 0.003, hy + sy * 0.036, zcap)],
                       0.0016, 5)
        # capsule: from the ear cushion (toward the middle) - body - the back domed outward
        inward = Vector((-s, 0.0, 0.0))
        base = Vector((xc, hy, zcap))
        prof = [(0.0, 0.0), (0.024, 0.0010), (0.0335, 0.0075), (0.0340, 0.0185), (0.0270, 0.0258), (0.0, 0.0292)]
        b.lathe(cup, base, -inward, prof if lod == 0 else [prof[i] for i in (0, 2, 3, 5)], 16 if lod == 0 else 8)
        # ear cushion: a soft ring toward the middle
        pp = [(0.0185, 0.0), (0.0290, 0.0016), (0.0310, 0.0070), (0.0240, 0.0118), (0.0160, 0.0078)]
        b.lathe(pad, base, inward, pp if lod == 0 else [pp[i] for i in (0, 2, 4)], 16 if lod == 0 else 8, cap1=True)
        ends.append(base)
    parts += [cup, pad, yk]
    # cord: from the bottom of the left capsule down to the plug in the panel's headphone jack (the plug
    # pulls it upward, toward the headphones - no kink at the handle)
    jx, jz = JACK_PHONES
    sl = P("phones_plug_sleeve", "chrome")
    hd = P("phones_plug", "bakelite")
    d = Vector((0.10, -0.75, 0.65)).normalized()
    tail = b.jack_plug(sl, hd, (jx, YP, jz), d, lod)
    parts += [p for p in (sl, hd) if p.bm.faces]
    e = ends[0]
    pts = [(e.x - 0.004, hy + 0.002, e.z - 0.031), (e.x - 0.006, hy - 0.006, e.z - 0.060), (e.x - 0.005, hy - 0.016, 1.470),
           (tail.x - 0.004, tail.y - 0.020, tail.z + 0.040), tuple(tail + d * 0.012), tuple(tail)]
    parts += cable("phones_cord", "cord", pts, 0.0026, lod)
    return parts


# =============================================================================
# Antenna, cables, coil
# =============================================================================
def build_antenna(spec):
    """Discone scanner antenna on a mast at the rear edge of the roof: a base plate on bolts, the mast,
    a hub, eight disc spokes and eight cone generatrices, connectors at the mast base. The cable from
    the patch-panel jack runs left, up the left rail (taped), through the front left eyebolt and along
    the roof to the mast; the second goes from the mast back into the rear wall entry. A coil of spare
    cable lies on the shelf."""
    lod = spec["lod"]
    mx, my = MAST
    zt = ZT_ANT
    parts = []
    ms = P("ant_mast", "steel")
    b.lathe(ms, (mx, my, H + 0.008), (0, 0, 1), [(0.0100, 0.0), (0.0100, zt - 0.052 - H - 0.008)], (12, 8, 4)[lod])
    parts.append(ms)
    if lod == 2:
        return parts
    bs = P("ant_base", "black")
    g.box(bs, mx - 0.045, mx + 0.045, my - 0.045, my + 0.045, H, H + 0.008, **(dict(r=0.002, seg=1) if lod == 0 else {}))
    parts.append(bs)
    hb = P("ant_hub", "black")
    b.lathe(hb, (mx, my, zt - 0.054), (0, 0, 1), [(0.0130, 0.0), (0.0210, 0.010), (0.0210, 0.034), (0.0160, 0.040),
                                                  (0.0, 0.042)], 14 if lod == 0 else 6)
    parts.append(hb)
    rods = P("ant_rods", "steel")
    nr = 8 if lod == 0 else 4
    for k in range(nr):
        a = 2 * math.pi * (k + 0.5) / nr
        ca, sa = math.cos(a), math.sin(a)
        g.pipe(rods, [(mx + 0.018 * ca, my + 0.018 * sa, zt - 0.046), (mx + 0.150 * ca, my + 0.150 * sa, H + 0.075)],
               0.0022, 6 if lod == 0 else 3)
        g.pipe(rods, [(mx + 0.018 * ca, my + 0.018 * sa, zt - 0.020), (mx + 0.112 * ca, my + 0.112 * sa, zt - 0.016)],
               0.0022, 6 if lod == 0 else 3)
    parts.append(rods)
    # connectors at the mast base: in front - the cable from the panel, behind - into the entry
    cn = P("ant_connectors", "chrome")
    ends = {}
    for s in (-1, 1):
        base = Vector((mx, my + s * 0.010, H + 0.030))
        d = Vector((0.0, s, 0.0))
        b.lathe(cn, base, d, [(0.0080, 0.0), (0.0080, 0.010), (0.0068, 0.012)], 10 if lod == 0 else 6, cap1=False)
        b.lathe(cn, base + d * 0.012, d, [(0.0072, 0.0), (0.0072, 0.016), (0.0050, 0.020), (0.0050, 0.026)],
                10 if lod == 0 else 6, knurl=(0, 1) if lod == 0 else (), depth=0.0005)
        ends[s] = base + d * 0.038
    parts.append(cn)
    # cable from the panel: from the antenna jack plug to the left, up the rail, through the eyebolt, along the roof
    e = Vector(plug_end(BNC_P[0][0], ZP, YP))
    f = ends[-1]
    xr, yr = -0.364, Y0 - 0.0060
    pts = [tuple(e), (e.x - 0.003, e.y - 0.010, ZP - 0.008), (-0.205, Y0 - 0.064, ZP - 0.040),
           (-0.280, Y0 - 0.058, ZP - 0.050), (-0.338, Y0 - 0.036, ZP - 0.026), (xr + 0.001, Y0 - 0.014, ZP + 0.030),
           (xr, yr, ZP + 0.120), (xr, yr, Z_V), (xr, yr, H - 0.060), (xr + 0.001, Y0 - 0.002, H - 0.012),
           (-0.357, Y0 + 0.008, H + 0.012), (-0.347, Y0 + 0.030, H + 0.024), (-0.340, Y0 + 0.060, H + 0.028),
           (-0.334, Y0 + 0.092, H + 0.021), (-0.302, Y0 + 0.150, H + 0.0065), (-0.180, -0.050, H + 0.0058),
           (-0.060, 0.012, H + 0.0058), (f.x - 0.004, f.y - 0.020, H + 0.014), tuple(f + Vector((0, -0.004, 0))), tuple(f)]
    parts += cable("ant_coax", "coax", pts, 0.0055, lod)
    f = ends[1]
    pts = [tuple(f), tuple(f + Vector((0, 0.006, 0))), (mx + 0.012, my + 0.090, H + 0.010), (mx + 0.040, Y1 - 0.060, H + 0.0058),
           (mx + 0.048, Y1 - 0.008, H + 0.004), (mx + 0.050, Y1 + 0.010, H - 0.022), (mx + 0.050, Y1 + 0.011, H - 0.065),
           (mx + 0.050, Y1 + 0.010, 1.905), (mx + 0.050, Y1 + 0.005, 1.890)]
    parts += cable("ant_coax_back", "coax", pts, 0.0055, lod)
    if lod == 0:
        # the cable is taped to the rail
        tw = P("ant_tape", "tape")
        for z in (Z_B + 0.10, Z_V + 0.02, H - 0.130):
            tape_wrap(tw, (xr, yr, z), (0, 0, 1), 0.0055)
        parts.append(tw)
        # coil of spare cable on the top shelf, the tail goes back
        cl = P("coil", "coax")
        zb_ = Z_B + ST
        # turns from the left edge, the last ends at the back - from there the tail goes to the rear wall
        cp = b.coil_pts(0.215, -0.232, zb_, 0.056, 2.75, 0.0045, 14, phase=math.pi)
        last = Vector(cp[-1])
        cp += [tuple(last + Vector((0.002, 0.024, -0.003))), (0.220, -0.125, zb_ + 0.011), (0.226, -0.060, zb_ + 0.0045)]
        g.pipe(cl, cp, 0.0045, 6)
        parts.append(cl)
    return parts


# =============================================================================
# Pull-out shelf: card reader, battery, PDA on a stand, notepad, mug, wires
# =============================================================================
def pda_frame():
    return g.inclined_front(PDA_Y, ZM + 0.012, PDA_DEG)


def build_reader(lod):
    """Homemade card reader: a board on a wooden block, a socket with the PDA memory card, a chip with
    legs, a capacitor, an LED (ozl_lamp_2, blinks), screws; a 9 V battery holder with wires."""
    x0, x1, y0, y1, h = RDR
    zt = ZM + h
    parts = []
    wd = P("reader_block", "wood")
    g.box(wd, x0, x1, y0, y1, ZM, zt - 0.0016, **(dict(r=0.003, seg=1) if lod == 0 else {}))
    parts.append(wd)
    led = P("reader_led", "led", group=SEL_LAMP2)
    lx, ly = RDR_PCB[1] - 0.010, RDR_PCB[3] - 0.008
    prof = [(0.0028, 0.0), (0.0028, 0.0010), (0.0025, 0.0011), (0.0025, 0.0050), (0.0018, 0.0068), (0.0007, 0.0076)]
    b.lathe(led, (lx, ly, zt), (0, 0, 1), prof if lod == 0 else [prof[i] for i in (0, 3, 5)], 12 if lod == 0 else 6)
    parts.append(led)
    if lod == 2:
        return parts
    pc = P("reader_pcb", "pcb")
    g.box(pc, RDR_PCB[0], RDR_PCB[1], RDR_PCB[2], RDR_PCB[3], zt - 0.0016, zt)
    parts.append(pc)
    # socket (steel holder) and a memory card inserted halfway
    sl = P("reader_slot", "steel")
    g.box(sl, RDR_PCB[0] + 0.004, RDR_PCB[0] + 0.048, RDR_PCB[2] + 0.002, RDR_PCB[2] + 0.040, zt, zt + 0.0034,
          **(dict(r=0.0006, seg=1) if lod == 0 else {}))
    parts.append(sl)
    cd = P("reader_card", "card")
    g.box(cd, RDR_PCB[0] + 0.0045, RDR_PCB[0] + 0.0475, RDR_PCB[2] - 0.016, RDR_PCB[2] + 0.012, zt + 0.0006, zt + 0.0028,
          **(dict(r=0.0006, seg=1) if lod == 0 else {}))
    parts.append(cd)
    ic = P("reader_chip", "chip")
    cx, cy = RDR_PCB[0] + 0.072, RDR_PCB[2] + 0.030
    g.box(ic, cx - 0.012, cx + 0.012, cy - 0.0034, cy + 0.0034, zt + 0.0006, zt + 0.0040)
    parts.append(ic)
    if lod == 0:
        lg = P("reader_legs", "lead")
        for k in range(8):
            xk = cx - 0.0089 + k * 0.00254
            for s in (-1, 1):
                g.box(lg, xk - 0.0004, xk + 0.0004, *sorted((cy + s * 0.0034, cy + s * 0.0046)), zt, zt + 0.0026)
        parts.append(lg)
        cp = P("reader_cap", "cap_blue")
        b.lathe(cp, (RDR_PCB[1] - 0.012, RDR_PCB[2] + 0.012, zt), (0, 0, 1),
                [(0.0030, 0.0), (0.0030, 0.0080), (0.0026, 0.0090)], 10)
        parts.append(cp)
        sw = P("reader_screws", "steel")
        for xx, yy in ((RDR_PCB[0] + 0.005, RDR_PCB[3] - 0.005), (RDR_PCB[1] - 0.005, RDR_PCB[2] + 0.005)):
            b.screw(sw, xx, yy, zt, 0.0030, axis=(0, 0, 1))
        parts.append(sw)
        # 9 V battery holder (the battery is vanilla) and two wires to the board edge, solder blobs
        lo, hi = kv.box("battery9v")
        up, fwd = (0, 0, 1), (-0.3, -1, 0)
        org = next(d[1] for d in DECOR if d[5] == "battery9v")
        top = Vector(kv.to_blender(((lo[0] + hi[0]) / 2, hi[1], (lo[2] + hi[2]) / 2), org, up, fwd))
        X, U, F = (Vector(v) for v in kv.axes(up, fwd))
        fr = g.Frame(top, X, F, U)
        sn = P("battery_snap", "black")
        g.box(sn, -0.0135, 0.0135, -0.0080, 0.0080, 0.0, 0.0055, frame=fr, r=0.0012, seg=1)
        parts.append(sn)
        for k, (reg, sx) in enumerate((("wire_red", -0.006), ("black", 0.006))):
            a = fr.p(sx, 0.0, 0.0050)
            ex = RDR_PCB[1] - 0.004
            ey = RDR_PCB[2] + 0.024 + 0.008 * k
            w = P("battery_wire%d" % k, reg)
            g.pipe(w, b.spline([tuple(a), tuple(a + U * 0.008 + X * 0.002), (a.x + 0.010, a.y + 0.012, zt + 0.012),
                                (ex + 0.008, ey, zt + 0.006), (ex, ey, zt + 0.0012)], 3), 0.0012, 5)
            parts.append(w)
        sd = P("reader_solder", "solder")
        for k in range(2):
            b.lathe(sd, (RDR_PCB[1] - 0.004, RDR_PCB[2] + 0.024 + 0.008 * k, zt), (0, 0, 1),
                    [(0.0020, 0.0), (0.0014, 0.0009), (0.0, 0.0014)], 8)
        parts.append(sd)
    return parts


def build_pda(lod):
    """PDA (Palm III) on a stand: a case with rounded edges, a screen (own texture, ozl_screen_4) in a
    dark frame, four round buttons and a rocker, a stylus in its slot; the stand is a base with an
    inclined back, a connector step, a sync button."""
    f = pda_frame()
    parts = []
    pd = P("pda", "pda")
    g.box(pd, PDA_X - PDA_W / 2, PDA_X + PDA_W / 2, 0.0, PDA_H, -PDA_T, 0.0, frame=f,
          **(dict(r=0.006, seg=2) if lod == 0 else {}))
    parts.append(pd)
    a0, a1, b0, b1 = PDA_X + PDA_SCR[0], PDA_X + PDA_SCR[1], PDA_SCR[2], PDA_SCR[3]
    if lod < 2:
        sc = P("pda_screen", "black", group=SEL_SCREEN4, section="pda")
        vs = [sc.bm.verts.new(f.p(a, bb, 0.0004)) for a, bb in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
        sc.tag([b.face(sc, vs, f.n)])
        sc.glass_frame = (f, a0, a1, b0, b1)
        parts.append(sc)
    else:
        sc = P("pda_screen", "black")
        g.box(sc, a0, a1, b0, b1, 0.0, 0.0006, frame=f)
        parts.append(sc)
    cr = P("pda_cradle", "black")
    g.box(cr, PDA_X - 0.050, PDA_X + 0.050, PDA_Y - 0.032, PDA_Y + 0.062, ZM, ZM + 0.012,
          **(dict(r=0.004, seg=2) if lod == 0 else {}))
    if lod < 2:
        g.box(cr, PDA_X - 0.042, PDA_X + 0.042, 0.004, 0.072, -PDA_T - 0.010, -PDA_T, frame=f,
              **(dict(r=0.003, seg=1) if lod == 0 else {}))
    parts.append(cr)
    if lod == 2:
        return parts
    if lod == 0:
        # dark screen frame and the handwriting area under it
        fm = P("pda_face", "pda_face")
        m = 0.004
        for aa, ab, ba, bb_ in ((a0 - m, a1 + m, b1, b1 + m), (a0 - m, a1 + m, b0 - 0.018, b0), (a0 - m, a0, b0, b1),
                                (a1, a1 + m, b0, b1)):
            g.box(fm, aa, ab, ba, bb_, 0.0, 0.0010, frame=f)
        parts.append(fm)
        bt = P("pda_buttons", "pda_face")
        for da in (-0.030, -0.017, 0.017, 0.030):
            b.lathe(bt, f.p(PDA_X + da, 0.017, 0.0), f.n, [(0.0046, 0.0), (0.0046, 0.0012), (0.0036, 0.0019)], 10)
        g.box(bt, PDA_X - 0.0065, PDA_X + 0.0065, 0.0125, 0.0215, 0.0, 0.0016, frame=f, r=0.0008, seg=1)
        parts.append(bt)
        sy = P("pda_stylus", "steel")
        b.lathe(sy, f.p(PDA_X + PDA_W / 2 - 0.0055, PDA_H - 0.004, -PDA_T / 2), f.v,
                [(0.0021, 0.0), (0.0021, 0.0075), (0.0016, 0.0095)], 8)
        parts.append(sy)
        # connector step of the stand under the bottom of the PDA, the sync button
        lp = P("pda_cradle_lip", "black")
        g.box(lp, PDA_X - 0.030, PDA_X + 0.030, -0.004, 0.006, -PDA_T - 0.002, 0.004, frame=f, r=0.0012, seg=1)
        parts.append(lp)
        hb = P("pda_sync", "key_w")
        b.lathe(hb, (PDA_X + 0.036, PDA_Y - 0.020, ZM + 0.012), (0, 0, 1), [(0.0050, 0.0), (0.0050, 0.0016),
                                                                             (0.0040, 0.0024)], 12)
        parts.append(hb)
    return parts


def build_tray(spec):
    lod = spec["lod"]
    parts = build_reader(lod) + build_pda(lod)
    x0, x1, y0, y1, h = RDR
    # notepad: a cardboard backing, a sheet with frequencies (the pen is vanilla)
    pp = P("notepad", "paper")
    g.box(pp, PAD[0], PAD[1], PAD[2], PAD[3], ZM, ZM + 0.004, **(dict(r=0.0008, seg=1) if lod == 0 else {}))
    parts.append(pp)
    # enameled mug: rolled rim, tea inside, a flat handle
    mx, my, mr, mh = MUG
    n = (20, 10, 6)[lod]
    mg = P("mug", "mug")
    prof = [(0.0, 0.0), (mr - 0.004, 0.0), (mr, 0.0040), (mr + 0.0010, mh - 0.0045), (mr + 0.0024, mh - 0.0016),
            (mr + 0.0014, mh), (mr - 0.0004, mh - 0.0030), (mr - 0.0018, mh - 0.0240)]
    b.lathe(mg, (mx, my, ZM), (0, 0, 1), prof if lod == 0 else [prof[i] for i in (0, 1, 3, 5, 7)], n, cap1=False)
    if lod < 2:
        hp = [(mx + mr + 0.0005, my, ZM + mh - 0.016), (mx + mr + 0.016, my, ZM + mh - 0.017),
              (mx + mr + 0.025, my, ZM + mh - 0.034), (mx + mr + 0.021, my, ZM + 0.030), (mx + mr + 0.0005, my, ZM + 0.020)]
        hp = b.spline(hp, 2) if lod == 0 else hp
        g.tube_var(mg, hp, [(0.0060, 0.0018)] * len(hp), 6 if lod == 0 else 4)
    parts.append(mg)
    te = P("tea", "tea")
    b.lathe(te, (mx, my, ZM + mh - 0.0215), (0, 0, 1), [(mr - 0.0016, 0.0)], n)
    parts.append(te)
    if lod == 2:
        return parts
    # wires: a ribbon from the card reader to the stand, cables of the reader and the stand go back into the rack
    rb = P("reader_ribbon", "ribbon")
    ym = (y0 + y1) / 2
    pts = [(x1 - 0.002, ym + 0.010, ZM + 0.020), (x1 + 0.014, ym + 0.012, ZM + 0.010), (x1 + 0.034, ym + 0.016, ZM + 0.0016),
           (PDA_X - 0.074, PDA_Y + 0.036, ZM + 0.0016), (PDA_X - 0.060, PDA_Y + 0.034, ZM + 0.004),
           (PDA_X - 0.050, PDA_Y + 0.032, ZM + 0.007)]
    g.sweep(rb, b.spline(pts, 3) if lod == 0 else pts, (0, 0, 1), 0.012, 0.0008)
    parts.append(rb)
    zl = ZS + 0.015                                      # rear rim of the shelf
    for name, a, xb in (("reader_cable", (x0 + 0.040, y1 + 0.002, ZM + 0.012), x0 + 0.090),
                        ("pda_cable", (PDA_X + 0.030, PDA_Y + 0.062, ZM + 0.007), PDA_X + 0.130)):
        pts = [a, (a[0] - 0.004, a[1] + 0.020, ZM + 0.0028), (a[0] + 0.010, -0.420, ZM + 0.0028),
               (xb - 0.010, -0.300, ZM + 0.0028), (xb, -0.255, zl + 0.0035), (xb, -0.236, zl + 0.003),
               (xb + 0.004, -0.215, ZS - 0.010), (xb + 0.008, -0.180, Z_SLIDE + ST + 0.0028)]
        parts += cable(name, "black", pts, 0.0028, lod)
    return parts


def build_lod(spec):
    parts = build_rack(spec) + build_r250(spec) + build_r7000(spec) + build_frg(spec) + build_ar(spec)
    parts += build_speaker(spec) + build_phones(spec) + build_antenna(spec) + build_tray(spec)
    parts = [p for p in parts if p is not None and len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    rack = kx.box_pts(X0, X1, Y0 - 0.05, Y1, 0.0, H)
    # a geometry component thinner than 0.5 m does not work in the engine: the shelf goes inside the rack and down
    shelf = kx.box_pts(XI0 - 0.012, XI1 + 0.012, TY0 - 0.06, Y0 + 0.20, 0.50, ZS + 0.13)
    metal = kx.PEN + r"\metalplate.rvmat"
    comps = [(rack, metal), (shelf, metal)]
    memory = {
        "invView": [(0.0, -2.8, 1.2)],
        "ce_center": [(0.0, 0.0, H / 2)],
        "ce_radius": [(0.8, 0.0, H / 2)],
    }
    # the axes of the needles and the limb point from the pivot toward the viewer (as in M06, M08: phase > 0
    # is clockwise); the cursor goes along the scale to the right, 1 m (offset in meters)
    for sel, fc in NEEDLES:
        a = needle_axis(fc)
        memory[sel + "_axis"] = [a, (a[0], a[1] - 0.05, a[2])]
    memory[SEL_DISC + "_axis"] = [(DISC[0], YF, DISC[1]), (DISC[0], YF - 0.05, DISC[1])]
    zv = (SCALE_Z[0] + SCALE_Z[1]) / 2
    memory[SEL_VISOR + "_axis"] = [(VISOR_X, Y_WIN - 0.0012, zv), (VISOR_X + 1.0, Y_WIN - 0.0012, zv)]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (X0, X1, min(lo[1], TY0 - 0.06), max(hi[1], Y1), 0.0, max(hi[2], H))
    return comps, 300.0, memory, bbox


# the first ones are for the --look preview: overall, instruments and shelf, R-250M2, shelf close-up,
# top; the "working" look: overall, instruments, R-250M2
SHOTS = [
    ("front", (-1.1, -3.0, 1.45), (0.0, 0.0, 1.05), 30),
    ("receivers", (-0.30, -1.15, 1.37), (-0.02, Y0, 1.22), 34),
    ("r250", (0.35, -1.25, 1.07), (0.0, Y0, 0.76), 34),
    ("shelf", (0.45, -1.05, 1.47), (-0.05, TY0 + 0.15, 1.07), 36),
    ("top", (0.55, -1.30, 1.87), (0.0, Y0, 1.67), 34),
    ("back", (1.5, 2.3, 1.6), (0.0, 0.0, 1.0), 30),
]

M.look_shots = (5, 3)
M.run(build_lod, collision, SHOTS, row_step=1.2, row_shot=((1.2, -6.5, 1.6), (1.2, 0, 1.0)))
