"""Layout of the homemade Freedom chronograph M28, shared by build_m28.py (geometry) and make_decals.py
(decals, the screen and the keyboard lie on the same faces: decals are projected in kmats along the
world axes).

Axes: X is width (along the rail, the barrel at -x), Y is depth (the face looks to -Y), Z is up. The
sizes and their sources are in the docstring of build_m28.py.
"""
import math

# rail: an aluminum tube 40 x 30, the center in depth RY, the top at RZ1
RX0, RX1 = -0.70, 0.70
RY, RHW = 0.05, 0.015
RZ0, RZ1 = 0.83, 0.87
ZB = 1.00                                                    # shot line (through the frame windows)

# tripods: (center x, rotation, degrees); a head under the rail, legs to the floor on radius TR
TRIPODS = ((-0.50, -6.0), (0.50, 8.0))
TR, TZ_APEX, TZ_HEAD = 0.26, 0.72, 0.76

# photosensor frames: center x (1219 mm between the screens - Oehler 35P), body, rods, visor
FX = (-0.6095, 0.6095)
F_HX, F_HY, F_Z1 = 0.04, 0.05, 0.925                         # half-sizes of the body and its top
F_TOP, F_TOPHW = 1.16, 0.16                                  # top of the rods, their half-spread at the top
F_SHADE = (0.05, 0.185, 1.177)                               # half-width along x, along y, top of the visor

# V-stop at the start: a plate on the rail (it ends 1.3 cm short of the body of frame 1), a post, a
# V-block; the turns of tape that fasten the plate to the end of the rail
VX = -0.77
REST_X1 = RX0 + 0.038
REST_TAPE = (RX0 + 0.005, RX0 + 0.027)
# catcher bag on the board at the end
BOARD = (0.665, 0.80, RY - 0.17, RY + 0.17, RZ1, RZ1 + 0.018)
BAG = (0.675, 0.795, RY - 0.15, RY + 0.15, BOARD[5], 1.12)

# Pelican 1520 class case (bright green) on the floor between the tripods
CASE = (0.502, 0.401, 0.188)
CASE_C = (0.0, -0.04)                                        # center x, y
CX0, CX1 = CASE_C[0] - CASE[0] / 2, CASE_C[0] + CASE[0] / 2
CY0, CY1 = CASE_C[1] - CASE[1] / 2, CASE_C[1] + CASE[1] / 2
CZ = CASE[2]                                                 # top of the case

# IBM ThinkPad 760 class laptop: 297 x 211 x 54 mm; base 35, lid 19, open at 105 degrees
LT_W, LT_D, LT_B, LT_L = 0.297, 0.211, 0.035, 0.019
LT_C = (-0.08, -0.075)                                       # center of the base x, y
LX0, LX1 = LT_C[0] - LT_W / 2, LT_C[0] + LT_W / 2
LY0, LY1 = LT_C[1] - LT_D / 2, LT_C[1] + LT_D / 2
LZ = CZ + LT_B                                               # top of the base
LID_DEG = 15.0                                               # lid tilt backward from the vertical
HINGE = (LT_C[0], LY1 - 0.012, LZ)
# 12.1" 4:3 screen - 246 x 184 mm, in the lid at b (up the lid) from 0.013
SCR_W, SCR_H, SCR_B0 = 0.246, 0.184, 0.013


def lid_point(a, b, c):
    """A lid point: a along x from the center, b up the lid from the hinge, c toward the screen face."""
    t = math.radians(LID_DEG)
    return (HINGE[0] + a, HINGE[1] + b * math.sin(t) - c * math.cos(t), HINGE[2] + b * math.cos(t) + c * math.sin(t))


# keyboard on the base top (face z = LZ): x0, x1, y0, y1
KEYS = (LX0 + 0.012, LX1 - 0.012, LY0 + 0.085, LY1 - 0.018)
PALM = (LX0, LX1, LY0, KEYS[2])
# key rows from the rear one (F keys) to the space bar: (fraction of the depth, key widths in fractions),
# gap; the keys are drawn by make_decals.py (a decal - the mid LOD) and build_m28.py (raised ones - the
# near LOD) by key_rects()
KEY_ROWS = [(0.11, [1] * 16), (0.17, [1] * 13 + [2]), (0.17, [1.5] + [1] * 12 + [1.5]),
            (0.17, [1.8] + [1] * 11 + [2.2]), (0.17, [2.3] + [1] * 10 + [2.7]),
            (0.17, [1.2, 1.2, 1.2, 6.2, 1.2, 1, 1, 1])]
KEY_GAP = 0.0016
# red trackpoint - between rows 4 and 5 (by G, H, B), fractions of the width and depth from the rear edge
TRACK = (0.47, 0.62)


def key_rects():
    """Keys: [(x0, x1, y0, y1)] on the base top, rows from the rear edge of KEYS to the front."""
    x0, x1, y0, y1 = KEYS
    W, H = x1 - x0, y1 - y0
    out, y = [], KEY_GAP
    for frac, keys in KEY_ROWS:
        h = H * frac - KEY_GAP
        unit = (W - KEY_GAP) / sum(keys)
        x = KEY_GAP
        for k in keys:
            w = unit * k - KEY_GAP
            out.append((x0 + x, x0 + x + w, y1 - y - h, y1 - y))
            x += w + KEY_GAP
        y += h + KEY_GAP
    return out


def track_xy():
    x0, x1, y0, y1 = KEYS
    return x0 + (x1 - x0) * TRACK[0], y1 - (y1 - y0) * TRACK[1]


# interface unit (homemade, an estimate) on the case to the right of the laptop
BOX = (0.10, 0.22, -0.17, -0.07, CZ, CZ + 0.05)
BOX_LCD = (0.110, 0.182, CZ + 0.021, CZ + 0.039)             # x0, x1, z0, z1 on the face y = BOX[2]; 4:1
BOX_LED = (0.200, CZ + 0.030)

# the laptop screen and the unit display share one own texture (section screen; the "working" frames of
# both change together): the top 3/4 of the image is the 4:3 screen, the bottom 1/4 the 4:1 display
PANEL_PX = 512
PANEL_SPLIT = 0.25

# faces for decals
CASE_FRONT = (CX0 + 0.012, CX1 - 0.012, 0.012, 0.125)       # face y = CY0, below the lid seam
CASE_TOP = (CX0 + 0.012, CX1 - 0.012, CY0 + 0.012, CY1 - 0.012)  # face z = CZ
CASE_SIDE = (CY0 + 0.012, CY1 - 0.012, 0.012, 0.125)        # right side, face x = CX1
# turns of tape on the rail (they hold the frame cables): center x, tape width
TAPE_X, TAPE_W = (-0.42, -0.17, 0.08, 0.32), 0.025
RAIL_FRONT = (RX0 + 0.02, RX1 - 0.02, RZ0 + 0.003, RZ1 - 0.003)  # face y = RY - RHW
