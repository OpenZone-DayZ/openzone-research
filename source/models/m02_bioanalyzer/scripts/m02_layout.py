"""Shared M02 sizes for build_m02.py and make_decals.py (system Python: no bpy or mathutils).

Blender axes: X is width, Y is depth (face toward -Y), Z is up. The dimensions are described in the
docstring of build_m02.py.
"""
import math

# =============================================================================
# Cabinet and device (accepted on the stand - do not change)
# =============================================================================
CX0, CX1, CY0, CY1, ZB = -0.50, 0.50, -0.33, 0.33, 0.80     # cabinet, worktop at ZB
AX0, AX1, AY0, AY1 = -0.37, 0.37, -0.28, 0.28               # analyzer
ZA = ZB + 0.012                                             # bottom of the body (feet)
ZD = ZA + 0.16                                              # top of the deck
ZT = ZD + 0.27                                              # top of the tower
YT = 0.12                                                   # face of the tower
SLOPE_DY, SLOPE_DZ = 0.07, 0.05                             # slope at the front
SL = math.hypot(SLOPE_DY, SLOPE_DZ)
COS_S, SIN_S = SLOPE_DY / SL, SLOPE_DZ / SL                 # slope: 35.5 degrees from the horizontal
TRAY_H = 0.028                                              # lower tray of the body up to the seam

# =============================================================================
# Sample carousel: rotor in a bath, 16 cups, 6 reagent bottles, smoked lid
# =============================================================================
CCX, CCY = -0.17, -0.045                                    # carousel centre
R_LID, R_BASE, R_ROT, R_CUPS, R_REAG = 0.165, 0.160, 0.142, 0.112, 0.058
N_CUPS = 16
EMPTY_CUPS = (3, 7, 8, 13)                                  # slots without a sample
Z_ROT = ZD + 0.022                                          # top of the rotor
R_NUM = 0.131                                               # slot numbers on the rotor

# dispenser arm: post, length to the needle, extreme angles (the needle over the slots and over the wash)
POST = (0.05, 0.02)
ARM_L = 0.117
ANG_CUP = math.degrees(math.atan2(CCY - POST[1], CCX - POST[0]))      # toward the carousel centre, ~196.3
ARM_SWING = 60.0                                                       # from the slot to the wash
ANG_WASH = ANG_CUP + ARM_SWING
ANG_MID = ANG_CUP + ARM_SWING / 2                                      # the model pose is mid-swing


def arm_point(deg, r=ARM_L):
    a = math.radians(deg)
    return POST[0] + r * math.cos(a), POST[1] + r * math.sin(a)


NEEDLE_CUP = arm_point(ANG_CUP)                             # above the cup ring (r 0.112 from the centre)
NEEDLE_WASH = arm_point(ANG_WASH)                           # above the wash cell

# =============================================================================
# Tower: display (own texture, "work" frames), grille, LEDs
# =============================================================================
VFD = (0.060, 0.300, 1.130, 1.190)                          # x0 x1 z0 z1, 240 x 60 mm
VFD_PX = (512, 128)

# =============================================================================
# Keypad on the slope: a is along X, b is up the slope from the bottom edge, c is outward
# =============================================================================
KEYPAD = (0.022, 0.258, 0.006, 0.076)                       # frame a0 a1 b0 b1 (the slope is rounded by 8 mm)
KEY_ROWS = (0.0655, 0.0490, 0.0325, 0.0160)                 # row centres, top to bottom
KEY_W, KEY_H = 0.0145, 0.0125
KEY_C0, KEY_C1 = 0.003, 0.0072                              # bottom and top of the caps above the slope
NUM_COLS = (0.040, 0.058, 0.076)
FUN_COLS = (0.104, 0.122, 0.140, 0.158)
NUM_LEG = (("7", "8", "9"), ("4", "5", "6"), ("1", "2", "3"), ("0", ".", "back"))
FUN_LEG = (("up", "down", "left", "right"), ("+", "-", "*", "/"), ("=", "#", ":", "dot"),
           ("circle", "square", "tri", "star"))
BIG_A, BIG_W = 0.190, 0.024                                 # start and stop span two rows
LED_RUN = (0.215, 0.060)                                    # yellow "measuring" (blinks)
LED_PWR = (0.215, 0.024)                                    # green "power"
KEYLOCK = (0.240, 0.041)                                    # operator lock


def keys():
    """[(a, b, w, h, kind, symbol)] - all keys: digits (light), functions (dark), start, stop."""
    out = []
    for r, b in enumerate(KEY_ROWS):
        for c, a in enumerate(NUM_COLS):
            out.append((a, b, KEY_W, KEY_H, "key", NUM_LEG[r][c]))
        for c, a in enumerate(FUN_COLS):
            out.append((a, b, KEY_W, KEY_H, "key_dark", FUN_LEG[r][c]))
    hb = KEY_ROWS[0] - KEY_ROWS[1] + KEY_H
    out.append((BIG_A, (KEY_ROWS[0] + KEY_ROWS[1]) / 2, BIG_W, hb, "key_green", "play"))
    out.append((BIG_A, (KEY_ROWS[2] + KEY_ROWS[3]) / 2, BIG_W, hb, "key_red", "stop"))
    return out


def slope_xy(a, b, c):
    """Keypad point (a, b, c) -> Blender (x, y): the symbol image is projected from above along Z."""
    return a, AY0 + b * COS_S - c * SIN_S


# =============================================================================
# Printer and tape: 57 mm thermal paper comes out of the slot, curls, lies on the deck, runs down the
# slope and hangs from the front of the body
# =============================================================================
PRINTER = (0.235, 0.355, -0.175, -0.035)                    # x0 x1 y0 y1 of the printer cover
PRINTER_H = 0.010
SLOT = (0.278, 0.342, -0.114, -0.104)
PAPER_X = 0.31
TAPE_W = 0.057
TAPE_TH = 0.0003


def _slope(u, off=0.0008):
    """Point above the slope: u runs down the slope from the top edge, off is the height above the surface."""
    return (-0.21 - COS_S * u - SIN_S * off, ZD - SIN_S * u + COS_S * off)


TAPE_PATH = [
    (-0.1090, ZD + 0.004), (-0.1092, ZD + 0.016), (-0.1115, ZD + 0.027), (-0.1195, ZD + 0.0355),
    (-0.1320, ZD + 0.0385), (-0.1460, ZD + 0.0350), (-0.1580, ZD + 0.0270), (-0.1690, ZD + 0.0170),
    (-0.1760, ZD + 0.0110), (-0.1820, ZD + 0.0058), (-0.1900, ZD + 0.0018), (-0.1980, ZD + 0.0009),
    (-0.2040, ZD + 0.0008), (-0.2103, ZD + 0.0010), _slope(0.006), _slope(0.043), _slope(0.080),
    (-0.2811, ZD - 0.0494), (-0.2808, ZD - 0.0560), (-0.2808, ZD - 0.0720), (-0.2810, ZD - 0.0900),
    (-0.2822, ZD - 0.1050), (-0.2855, ZD - 0.1140),
]


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, as in M04/M16), any dimension."""
    n = len(pts)
    out = []
    for i in range(n - 1):
        p1, p2 = pts[i], pts[i + 1]
        p0 = pts[i - 1] if i > 0 else tuple(2 * a - b for a, b in zip(p1, p2))
        p3 = pts[i + 2] if i + 2 < n else tuple(2 * b - a for a, b in zip(p1, p2))
        for s in range(k):
            t = s / k
            out.append(tuple(0.5 * (2 * b + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t * t +
                                    (3 * b - a - 3 * c + d) * t ** 3) for a, b, c, d in zip(p0, p1, p2, p3)))
    out.append(tuple(pts[-1]))
    return out


def arclen(pts):
    s = [0.0]
    for p, q in zip(pts, pts[1:]):
        s.append(s[-1] + math.dist(p, q))
    return s


TAPE_LEN = arclen(spline(TAPE_PATH, 4))[-1]

# =============================================================================
# Back wall of the tower: nameplate (no words - frame, rulers, digits)
# =============================================================================
PLATE = (-0.095, -0.015, 1.150, 1.195)                      # x0 x1 z0 z1 at y = AY1
