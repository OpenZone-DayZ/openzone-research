"""Layout of the Freedom gas mask test stand M30, shared by build_m30.py (geometry) and make_decals.py
(decals, the dial and the display frames lie on the same faces: decals are projected in kmats along
the world axes).

Axes: X is width, Y is depth (the face looks to -Y), Z is up. The sizes and their sources are in the
docstring of build_m30.py.
"""

# table: 1.00 x 0.60, the top of the tabletop at 0.85, an apron under the tabletop, a shelf at the bottom
TX0, TX1 = -0.50, 0.50
TY0, TY1 = -0.30, 0.30
ZT = 0.85                                                    # top of the tabletop
TOP_T = 0.028                                                # the tabletop is a sheet with a downward flange of 28 mm
OV = 0.015                                                   # tabletop overhang beyond the apron and legs
ZA = 0.75                                                    # bottom of the apron
LEG = 0.035                                                  # legs - a 35 x 35 tube
ZS = 0.20                                                    # top of the shelf
SHELF_T = 0.02
LX0, LX1 = TX0 + OV, TX1 - OV                                # outer faces of the legs and apron
LY0, LY1 = TY0 + OV, TY1 - OV

# dome on a round base on the left: the center, the base, the dome dia. 0.35 x 0.45
DX, DY = -0.17, 0.0
BASE_R, BASE_H = 0.205, 0.04
ZB = ZT + BASE_H                                             # top of the base, bottom of the dome
DOME_R, DOME_H = 0.175, 0.45
DOME_T = 0.004                                               # dome wall (acrylic 4 mm)

# mannequin head: a neck on the base flange, a GP-5 class mask pulled down to the neck
MASK_Z = ZB + 0.085                                          # bottom edge of the mask

# control unit on the right: x0, x1, y0 (face), y1, z0, z1
BLK = (0.13, 0.45, -0.13, 0.11, ZT + 0.012, ZT + 0.192)
GAUGE = (0.215, BLK[4] + 0.095)                              # gauge center on the face: x, z
GAUGE_D = 0.10                                               # dial dia. 100 (a row of GOST 2405 cases)
LAMP = (0.300, BLK[4] + 0.142)                               # lamp on the face: x, z
TOGGLES = ((0.300, 0.345, 0.390), BLK[4] + 0.070)            # toggles: x, z
VALVES = ((0.345, 0.415), -0.06)                             # valves on top: x, y
LCD = (0.338, 0.428, BLK[4] + 0.124, BLK[4] + 0.158)         # display: x0, x1, z0, z1 (the unit face)

# compressor of the Fengda AS-186 class on the shelf on the right: center x, y; 310 x 135 x 310
CMX, CMY = 0.25, 0.02
CMW, CMD, CMH = 0.31, 0.135, 0.31
TANK_R = 0.062                                               # 3 l receiver along x, at the bottom
TANK_X = (CMX - 0.145, CMX + 0.145)
TANK_Z = ZS + 0.016 + TANK_R                                 # receiver axis (on 16 mm feet)
MOTOR = (CMX - 0.115, CMX + 0.005, TANK_Z + TANK_R + 0.065, 0.055)   # motor along x: x0, x1, axis z, radius
CGAUGE = (CMX + 0.1225, CMY - 0.046, ZS + 0.181)             # compressor gauge: center (the face toward -y)
CGAUGE_D = 0.04

# on the left shelf: the vanilla gas mask, filters, rags (build_m30.DECOR)
# on the table: a filter taken off the mask, tape, a screwdriver, pliers

# faces for decals
APRON_F = (LX0 + LEG + 0.01, LX1 - LEG - 0.01, ZA + 0.006, ZT - TOP_T - 0.006)  # apron face, y = LY0
APRON_R = (LY0 + LEG + 0.01, LY1 - LEG - 0.01, ZA + 0.006, ZT - TOP_T - 0.006)  # right apron, x = LX1
BLK_TOP = (BLK[0] + 0.01, BLK[1] - 0.01, BLK[2] + 0.04, BLK[3] - 0.01)            # top of the unit, z = BLK[5]
BLK_SIDE = (BLK[2] + 0.01, BLK[3] - 0.01, BLK[4] + 0.01, BLK[5] - 0.01)           # right side, x = BLK[1]
COMP_FRONT = (CMX - 0.11, CMX + 0.11, ZS + 0.035, ZS + 0.125)                     # receiver face, y = CMY - TANK_R
