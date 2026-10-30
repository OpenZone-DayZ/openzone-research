"""Layout of the M36 SOP staff terminal - shared by build_m36.py (geometry) and make_decals.py:
the screens, keyboard, stencils and the radio panel lie on the same faces (kmats projects
decals along the world axes).

Axes: X - width, Y - depth (front at -Y), Z - up. Dimensions and their sources are in the
docstring of build_m36.py.
"""
import math

# --- Folding table 1.00 x 0.60, top at 0.74 ---------------------------------------------------
TX0, TX1, TY0, TY1 = -0.50, 0.50, -0.30, 0.30
TOP = 0.74
PLY = 0.018                                                  # plywood tabletop
APRON = 0.045                                                # frame angle under the plywood
LEG_X = 0.455                                                # X-shaped supports at the table ends
LEG_R = 0.0125                                               # 25 mm tube
LEG_Y = 0.255                                                # floor feet and frame legs at +-LEG_Y
STRETCH_Z = 0.37                                             # long brace through support axes

# --- Rugged laptop of the CF-27 class (open): 0.30 x 0.24, base 36 mm, lid 24 mm --------------
LX0, LX1, LY0, LY1 = -0.490, -0.190, -0.280, -0.040
LB_H = 0.036
LID_T, LID_D, LID_TILT = 0.024, 0.240, 12.0                  # lid tilted 12 deg from vertical
LID_Y, LID_Z = LY1 - LID_T, TOP + LB_H + 0.005               # bottom of the lid face (hinge axis)
LCD_W, LCD_H, LCD_B = 0.246, 0.184, 0.038                    # 12.1 in 4:3; lid bottom to screen
LXC = (LX0 + LX1) / 2
KEYS = (LX0 + 0.016, LX1 - 0.016, LY1 - 0.118, LY1 - 0.012)  # base keyboard: x0, x1, y0, y1
TPAD = (LXC, LY0 + 0.070, 0.064, 0.046)                      # touchpad: x, y, width, depth


def lid_axes():
    """Lid frame: origin is the bottom of the face on the hinge axis; u along x, v up the lid,
    n toward the player.
    """
    t = math.radians(LID_TILT)
    return (0.0, LID_Y, LID_Z), (1, 0, 0), (0, math.sin(t), math.cos(t)), (0, -math.cos(t), math.sin(t))


def lid_point(a, b, c):
    o, u, v, n = lid_axes()
    return tuple(o[i] + u[i] * a + v[i] * b + n[i] * c for i in range(3))


# --- 14 in CRT in a steel case: 0.36 x 0.36 x 0.375 -------------------------------------------
MX0, MX1, MY0, MY1 = -0.170, 0.190, -0.075, 0.300
MX = (MX0 + MX1) / 2
MFEET = 0.012
MZ0, MZ1 = TOP + MFEET, TOP + 0.360
BEZ_T = 0.028                                                # front bezel of the case
WIN_W, WIN_H, WIN_Z = 0.292, 0.224, TOP + 0.205              # window in the bezel
CRT_W, CRT_H = 0.268, 0.201                                  # 14 in tube, 13 in visible area
CRT_EDGE = 0.016                                             # glass edge depth below bezel face
CRT_SAG = 0.010                                              # glass bulge
CRT_NUM = dict(y=0.13, z=TOP + 0.27, w=0.15, h=0.05, text="0731")   # number on case left side

# --- Radio of the R-107 class: 375 x 185 x 270, long side along the depth, on the right -------
RX0, RX1, RY0, RY1 = 0.305, 0.490, -0.080, 0.295
RZ1 = TOP + 0.270
RXC = (RX0 + RX1) / 2
R_PANEL = (RX0 + 0.010, RX1 - 0.010, RY0 + 0.010, RY1 - 0.010)
R_KNOBS = [(RX0 + 0.050, 0.120, 0.022), (RX1 - 0.050, 0.120, 0.022)]          # freq: x, y, radius
R_WINDOWS = [(RX0 + 0.050, 0.185), (RX1 - 0.050, 0.185)]                      # counter windows
R_WIN = (0.056, 0.020)
R_SMALL = [(RX0 + 0.040, 0.030, 0.012), (RXC, 0.030, 0.012), (RX1 - 0.040, 0.030, 0.012)]
R_LAMP = (RXC, -0.030)
R_SOCK = [(RX0 + 0.035, -0.045), (RX1 - 0.035, -0.045)]                       # headset sockets
R_ANT = (RX1 - 0.035, 0.260)
R_FREQ = [("31.250", RX0 + 0.050), ("47.025", RX1 - 0.050)]

# --- TA-57 field telephone, opened: two halves 165 x 222 --------------------------------------
PH_X0, PH_XH, PH_X1 = -0.170, -0.005, 0.160                  # body | hinges | lid
PH_Y0, PH_Y1 = -0.298, -0.076
PH_HB, PH_HL = 0.045, 0.034                                  # depth of the body and of the lid

# --- Front right: logbook, pencil, the radio handset ------------------------------------------
BOOK = (0.305, -0.215, 0.210, 0.148, -4.0)                   # center x, y, size, rotation
HANDSET = (0.355, -0.205, 18.0)

# --- Tripod antenna on the right --------------------------------------------------------------
ANT_C = (0.640, 0.090)
ANT_FOOT = 0.135
ANT_HEAD = 0.470
ANT_MAST = (0.430, 0.860)
ANT_TOP = 1.500

# --- Under the table: two iron boxes and a cable reel -----------------------------------------
BOX1 = dict(x0=-0.400, x1=0.100, y0=-0.140, y1=0.180, h=0.300, lid=0.045)
BOX2 = dict(x0=0.140, x1=0.420, y0=0.040, y1=0.280, h=0.250, lid=0.040)
BOX1_NUM = dict(x=-0.150, z=0.165, w=0.20, h=0.065, text="3502")
BOX1_BAND = dict(x=-0.150, z=0.085, w=0.40, h=0.030)
BOX2_NUM = dict(x=0.280, z=0.120, w=0.10, h=0.050, text="54")
REEL = dict(x=0.300, y=-0.140, z=0.165, r=0.140, coil=0.118, core=0.060, w=0.180, flange=0.008, handle=0.330)
