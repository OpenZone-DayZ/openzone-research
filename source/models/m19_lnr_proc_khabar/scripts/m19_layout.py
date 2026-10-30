"""Where things are in M19 - shared by build_m19.py (Blender) and make_decals.py (system Python +
Pillow): the TV cabinet, the screen, the control strip, the innards behind the removed back wall, the
detector block, the roof, the stool.

Only numbers and simple arithmetic - no bpy or kit: make_decals.py imports the module under the system
Python.
Blender axes: X is width, Y is depth (face toward -Y), Z is up.
"""
# "Rubin-401" cabinet: 746 x 518 x 495 mm (W x H x D) on a 0.45 m stool
X0, X1, Y0, Y1 = -0.373, 0.373, -0.2475, 0.2475
ZS, ZT = 0.45, 0.968                                        # bottom of the cabinet (the seat), roof
T = 0.018                                                   # walls (veneered plywood)
R_CAB = 0.014                                               # rounding of the cabinet corners (front view)
YM = Y0 + 0.010                                             # the mask is recessed 1 cm into the cabinet

# screen: centre, semi-axes of the mask window, superellipse exponent; the mask goes from a rectangle to the window
SCX, SCZ = -0.075, (ZS + ZT) / 2
SA, SB, SN = 0.235, 0.180, 5.0
MA, MB = 0.28, (ZT - ZS) / 2 - T                            # mask rectangle x -0.355..0.205
YBI = YM + 0.035                                            # edge of the mask window (35 mm bevel)
SCR_A, SCR_B = SA + 0.02, SB + 0.02                         # the glass extends past the window edge
YSR = YBI + 0.003                                           # glass rim
BULGE = 0.022                                               # bulge of the picture tube
SCREEN_PX = (640, 502)                                      # screen frames: 2 SCR_A x 2 SCR_B

# control strip on the right: speaker grille, channel selector (PTK), two knobs
XS0, XS1 = SCX + MA, X1 - T
CH = ((XS0 + XS1) / 2, 0.63)
SMALL = ((XS0 + 0.04, 0.52), (XS1 - 0.035, 0.52))
GRILLE = ((XS0 + XS1) / 2, 0.835, XS1 - XS0 - 0.02, 0.21)   # centre x, z, width, height
SIDE_KNOBS = ((-0.17, 0.66), (-0.17, 0.585))                # on the right side: y, z

# innards: chassis on the bottom, laminate boards facing the removed wall, a speaker and the PTK behind the strip
ZB = ZS + T                                                 # inside bottom
CHASSIS = (-0.34, 0.10, -0.03, 0.236)                       # x0 x1 y0 y1
PCB_L = (-0.345, -0.17, 0.50, 0.82, 0.06)                   # boards: x0 x1 z0 z1 y of the face
PCB_R = (0.035, 0.205, 0.64, 0.93, 0.10)
SPEAKER = (GRILLE[0], GRILLE[1], 0.060)                     # x, z, basket radius (1GD, dia. 125)
TUNER = (0.226, 0.334, YM + 0.04, -0.085, 0.585, 0.675)     # PTK: x0 x1 y0 y1 z0 z1

# detector block 210 x 135 x 120 on 6 mm rubber feet, facing the removed wall (+Y)
DET = (0.12, 0.33, 0.10, 0.235, ZB + 0.006, ZB + 0.126)
DX0, DX1, DY0, DY1, DZ0, DZ1 = DET
YF = DY1 + 0.0015                                           # face of the aluminium panel
PLATE = (DX0 + 0.006, DX1 - 0.006, DZ0 + 0.006, DZ1 - 0.006)
# M42100 microammeter (80 x 80, as in M10): scale window, needle axis a little below the window
MX, MZ = 0.275, (DZ0 + DZ1) / 2
DIAL_W, DIAL_H, PIVOT_DZ, ARC_R = 0.068, 0.048, 0.004, 0.040
WIN = (MX - DIAL_W / 2, MX + DIAL_W / 2, MZ - 0.018, MZ - 0.018 + DIAL_H)
PIVOT = (MX, WIN[2] - PIVOT_DZ)
LAMP = (0.155, DZ1 - 0.030)                                 # lamp (amber), toggle, knob, sign
TOGGLE = (0.155, DZ0 + 0.034)
KNOB = (0.205, DZ0 + 0.034)
RAD = (0.205, DZ1 - 0.032, 0.032)
# SBM-20 counters in holders on the board on the roof of the block
GM_BOARD = (0.145, 0.300, 0.122, 0.212)
GM_Y = (0.147, 0.187)
GM_X = (0.170, 0.278)

# roof: a tray on a board with a coil, a mug, a loop antenna on a rotary motor, decals
TRAY = (-0.16, -0.06, 0.24, 0.18, 0.035)                    # tray: centre x, y, length, width, height
PICKUP = (TRAY[0], TRAY[1], 0.27, 0.21, 0.012)              # board with a coil under the tray
MUG_C, MUG_R, MUG_H = (0.10, -0.13), 0.042, 0.085
ANT = (0.22, 0.12)                                          # antenna base
ANT_BASE = (0.10, 0.07, 0.030)                              # length, width, height of the motor box
ANT_R = 0.075
ANT_Z = ZT + ANT_BASE[2] + 0.026 + ANT_R + 0.004            # centre of the loop
SUN = ((0.02, 0.11), 0.07)
BOLT = ((-0.31, 0.16), (0.045, 0.06))
CUPS = ((0.10, -0.13, 0.040), (0.140, -0.018, 0.041), (-0.035, 0.175, 0.040))   # mug traces

# stool: steel legs from a tube, a plywood seat 400 x 400
SEAT, ZSEAT = 0.20, 0.022
LEG_TOP, LEG_BOT = 0.165, 0.205
RING_Z = 0.14
