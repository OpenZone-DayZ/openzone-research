"""What is where in M10 - shared by build_m10.py (Blender) and make_decals.py (system Python + Pillow):
the sizes of the crate and the machine, the detector unit and its front panel, the dosimeter and its
display.

Only numbers and simple arithmetic - no bpy and no kit: make_decals.py imports this module with the
system Python. Blender axes: X is width, Y is depth (face toward -Y), Z is up.
"""
# crate stand: 0.72 x 0.13 x 0.42
CX0, CX1, CY0, CY1, ZS = -0.36, 0.36, -0.21, 0.21, 0.13
BOARD = 0.018

# Sibir-5 machine: 675 x 700 x 375 (W x H x D) - as in kwasher.layout
X0, X1, Y0, Y1, HM = -0.3375, 0.3375, -0.1875, 0.1875, 0.70
SPLIT = 0.55
ZT = ZS + HM                                   # top of the deck
XS = X0 + (X1 - X0) * SPLIT                    # boundary of the compartments
WASH = (X0 + 0.025, XS - 0.012, Y0 + 0.028, Y1 - 0.030)
LID_T = 0.014                                  # lid thickness

# machine panel (kwasher.layout: panel, KNOB_FR, WELL_R) - for the knob scales
PANEL_W, PANEL_H = (X1 - 0.040) - (X0 + 0.040), 0.127
KNOB_FR, WELL_R = (0.20, 0.50, 0.80), 0.036

# detector unit 240 x 160 x 130 on the tank lid, on 6 mm rubber feet
DXC = (WASH[0] + WASH[1]) / 2
DX0, DX1, DY0, DY1 = DXC - 0.12, DXC + 0.12, -0.095, 0.065
DZF = ZT + LID_T                               # top of the tank lid
DZ0 = DZF + 0.006                              # bottom of the box
DZ1 = DZ0 + 0.13                               # roof of the box
# front panel (an aluminium sheet 2 mm forward): x0, x1, z0, z1 and its face
PLATE = (DX0 + 0.005, DX1 - 0.005, DZ0 + 0.005, DZ1 - 0.005)
YF = DY0 - 0.002
# microammeter M42100 (80 x 80): the scale window, the needle axis slightly below the window
MX, MZ = DX0 + 0.065, DZ0 + 0.066
DIAL_W, DIAL_H, PIVOT_DZ, ARC_R = 0.068, 0.048, 0.004, 0.040
WIN = (MX - DIAL_W / 2, MX + DIAL_W / 2, MZ - 0.018, MZ - 0.018 + DIAL_H)
# lamps (green - "power", red - count), toggle, sensitivity knob, probe socket
LAMP_G = (DX0 + 0.128, DZ0 + 0.100)
LAMP_R = (DX0 + 0.158, DZ0 + 0.100)
TOGGLE = (DX0 + 0.205, DZ0 + 0.100)
KNOB = (DX0 + 0.180, DZ0 + 0.042)
BNC = (DX0 + 0.128, DZ0 + 0.042)

# dosimeter RKSB-104 lying on the unit: x, y of the centre, length, width, height; display - centre and size
DOS = (DX0 + 0.105, (DY0 + DY1) / 2 - 0.005, 0.165, 0.083, 0.030)
DOS_TOP = DZ1 + DOS[4]
LCD = (DOS[0] - 0.029, DOS[1] + 0.008, 0.052, 0.022)
DOS_BTN = [(DOS[0] + 0.022, DOS[1] + 0.012), (DOS[0] + 0.022, DOS[1] - 0.014)]   # buttons to the right of the display
DOS_GRILLE = (DOS[0] + 0.048, DOS[0] + 0.072, DOS[1] - 0.022, DOS[1] + 0.022)  # beeper grille x0 x1 y0 y1
