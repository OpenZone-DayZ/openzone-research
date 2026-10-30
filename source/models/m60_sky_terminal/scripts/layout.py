"""Where things go at the M60 field HQ of the Clear Sky - shared by build_m60.py (geometry) and
make_decals.py (the laptop screen, map, stencils, the radio strip and panel lie on the same faces: decal
projection in kmats runs along world axes).

Axes: X is width, Y is depth (the front faces -Y), Z is up. Sizes and their sources are in the docstring
of build_m60.py.
"""
import math

# --- table: four 40 mm boards on two crates standing on end -------------------------------------
TX0, TX1, TY0, TY1 = -1.05, 0.55, -0.40, 0.40
CRATE_H = 0.71                                               # crate height (on end)
BOARD_T = 0.040
TOP_B = CRATE_H + BOARD_T                                    # top of the boards 0.75
# boards: (y0, y1, x0, x1) - widths 195/190/200/185 mm, 10 mm gaps, ends staggered
BOARDS = [(-0.400, -0.205, -1.050, 0.550), (-0.195, -0.005, -1.075, 0.540),
          (0.005, 0.205, -1.035, 0.555), (0.215, 0.400, -1.060, 0.545)]
CLEATS = [(-0.585, -0.545), (0.045, 0.085)]                  # bars under the boards at the inner walls of the crates
CLEAT_T = 0.025
# crates on end: (x0, x1), y and height are shared; the face (the crate lid) is towards the player
CRATES = [(-0.99, -0.59), (0.09, 0.49)]
CY0, CY1 = -0.175, 0.175
CRATE_NUM = ["17", "4"]
CRATE_T = 0.020                                              # crate board thickness
BATTENS = ((0.015, 0.075), (CRATE_H - 0.075, CRATE_H - 0.015))   # straps near the ends, along the height
HINGE_Z = (0.19, 0.52)                                       # hinges and latches of the former lid
# handle on the outer side of the crate: two posts and a bar with a gap to the wall (a guy line is tied
# to the right one)
HANDLE_Z = (0.405, 0.445)
HANDLE_Y = 0.095
HANDLE_OUT = (0.012, 0.030)                                  # bar: outwards from the wall
# 12 mm plywood sheet on the boards under the laptop and radio
PX0, PX1, PY0, PY1 = -0.58, 0.40, -0.37, 0.35
PLY_T = 0.012
TOP = TOP_B + PLY_T                                          # top of the plywood 0.762

# --- rugged laptop of the CF-27 class (open): 0.30 x 0.24, base 36 mm, lid 24 mm -------------------
LX0, LX1, LY0, LY1 = -0.520, -0.220, -0.320, -0.080
LB_H = 0.036
LAP_R = 0.016                                                # body corner rounding in plan
LID_T, LID_D, LID_TILT = 0.024, 0.240, 14.0                  # the lid is tilted 14 degrees back from vertical
LID_Y, LID_Z = LY1 - LID_T, TOP + LB_H + 0.005               # bottom of the lid face (hinge axis)
LCD_W, LCD_H, LCD_B = 0.246, 0.184, 0.038                    # 12.1" 4:3; from the lid bottom to the screen
LXC = (LX0 + LX1) / 2
KEYS = (LX0 + 0.016, LX1 - 0.016, LY1 - 0.118, LY1 - 0.012)  # keyboard on the base: x0, x1, y0, y1
TPAD = (LXC, LY0 + 0.072, 0.064, 0.044)                      # touchpad: x, y, width, depth
LED_Y = LY0 + 0.014                                          # lamps on the front edge
BRICK_PSU = (-0.300, 0.180, 0.150, 0.068, 0.034)             # power supply: x, y, length, width, height
DC_JACK = (LX0, LY1 - 0.035, TOP + 0.016)                    # power socket on the left side


def lid_axes():
    """Lid: the origin is the bottom of the face on the hinge axis, u along x, v up the lid, n towards
    the player.
    """
    t = math.radians(LID_TILT)
    return (0.0, LID_Y, LID_Z), (1, 0, 0), (0, math.sin(t), math.cos(t)), (0, -math.cos(t), math.sin(t))


def lid_point(a, b, c):
    o, u, v, n = lid_axes()
    return tuple(o[i] + u[i] * a + v[i] * b + n[i] * c for i in range(3))


# --- radio R-159: a 305 x 160 x 170 transceiver on the battery compartment, faces the player ----------
RX0, RX1, RY0, RY1 = 0.030, 0.335, 0.120, 0.280
RXC, RYC = (RX0 + RX1) / 2, (RY0 + RY1) / 2
BAT_H, TR_H = 0.200, 0.170
BAT_IN = 0.0025                                              # the compartment is narrower than the transceiver on each side
RZS = TOP + BAT_H                                            # compartment seam (crimp belt)
RZ1 = RZS + TR_H                                             # top of the body (rim)
RZP = RZ1 - 0.0015                                           # top of the panel in the recessed top
RIBS_LO = [(TOP + 0.030, TOP + 0.058), (TOP + 0.082, TOP + 0.110), (TOP + 0.134, TOP + 0.162)]
RIBS_UP = [(RZS + 0.024, RZS + 0.048), (RZS + 0.062, RZS + 0.086), (RZS + 0.100, RZS + 0.124)]
BAND_Z = (RZ1 - 0.040, RZ1 - 0.017)                          # pale-blue CS stripe on the face
R_PANEL = (RX0 + 0.010, RX1 - 0.010, RY0 + 0.010, RY1 - 0.010)  # panel on top
R_CONN = (RX0 + 0.036, RYC)                                  # headset connector (left)
R_HANDLE = (RX0 + 0.110, RX0 + 0.245, RY1 - 0.050, RY1 - 0.016)  # lid-handle on top near the back
R_SWITCH = [(RX0 + 0.128 + 0.030 * i, RY0 + 0.034) for i in range(4)]  # frequency wafer switches
R_WIN_Y = RY0 + 0.058                                        # digit windows behind the switches
R_FREQ = "4815"
R_KNOB = (RX0 + 0.258, RY0 + 0.036)                          # volume knob
R_LAMP = (RX0 + 0.244, RY0 + 0.066)                          # transmit lamp - between the switches and the volume
R_TERM = [(RX1 - 0.108, RYC + 0.006), (RX1 - 0.078, RYC + 0.006)]  # orange terminals
R_ANT = (RX1 - 0.036, RYC)                                   # antenna input (right)
R_TAG = (RYC, RZS + 0.090, 0.070, 0.034)                     # empty nameplate on the right side: y, z, width, height
# the headset hangs at the left end: the headband across the top, cups on the front and back
HS_X = RX0 + 0.085
HS_Z = RZ1 - 0.068
HS_R = 0.0385
TANGENT = (0.135, -0.105, 24.0)                              # PTT key on the plywood: x, y, rotation

# --- left on the boards: tablet with a map, mug -----------------------------------------------
MAP_C = (-0.845, -0.150)
MAP_DEG = -7.0
MAP_BOARD = (0.230, 0.320)                                   # tablet board for A4
MAP_PAPER = (0.210, 0.297, -0.010)                           # A4 sheet: width, length, shift towards the player
MUG = (-0.995, 0.305, 0.0425, 0.085)                         # x, y, radius, height

# --- mast in a sand crate on the right ----------------------------------------------------------
MX, MY = 0.800, 0.120
BALLAST = (0.680, 0.920, 0.000, 0.240, 0.240)                # x0, x1, y0, y1, height
SAND_Z = 0.200
MAST = [(0.0225, 0.030, 1.120), (0.0180, 1.060, 1.740), (0.0140, 1.700, 1.950)]  # (radius, bottom, top)
COLLARS = [(0.0285, 1.100, 1.146), (0.0235, 1.720, 1.762)]
GUY_Z = 1.785
ANT_BASE = (1.950, 2.000)
ANT_TOP = 2.300
# guys: to the handle bar of the right crate and to two bricks on the floor
GUY_CRATE = (CRATES[1][1] + HANDLE_OUT[1] + 0.005, 0.0, HANDLE_Z[1] + 0.006)
BRICKS = [(1.075, -0.355, -55.0), (1.060, 0.470, 52.0)]      # x, y, rotation; a brick is 250 x 120 x 65
BRICK = (0.250, 0.120, 0.065)

# --- under the table: extension reel, spare battery compartment --------------------------------
REEL = dict(x=-0.340, y=0.080, z=0.170, r=0.135, coil=0.100, w=0.130, flange=0.006)
SOCK = (-0.255, -0.215, 0.030, 0.130, 0.100, 0.200)          # socket block on the right post: x0, x1, y0, y1, z0, z1
SPARE = (-0.130, 0.030, -0.050, 0.255, 0.200)                # x0, x1, y0, y1, height
