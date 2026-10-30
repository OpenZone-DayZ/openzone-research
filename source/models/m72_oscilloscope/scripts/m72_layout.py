"""Layout of the front panel and the sides of the M72 oscilloscope, shared by build_m72.py (Blender) and
make_decals.py (system Python + Pillow): knobs, buttons and sockets stand exactly on their scales and
pictograms.

Metres, the model's Blender axes: x is width (0 is the middle), z is height from the floor, the face
is at -Y. The positions were measured from photos of the real instrument (the front, 554 x 738 px:
the case is 325 px wide, and the left side).
"""

W = 0.100                       # case width (type description: 100 x 190 x 300 mm)
FOOT_H = 0.009                  # feet
Z_TOP = 0.190

# face: the control panel at the bottom, the black screen panel, a light strip at the top
PANEL_X = (-0.0475, 0.0475)
PANEL_Z = (0.011, 0.116)
BEZEL_Z = (0.116, 0.177)
STRIP_Z = (0.177, 0.1875)

SCREEN_C, SCREEN_WH = (-0.0075, 0.1465), (0.069, 0.055)    # CRT window
GRID_DIV, GRID_NX, GRID_NY = 0.006, 10, 8                  # grid of 10 x 8 divisions of 6 mm

# knobs by the screen: focus and brightness
SCR_KNOBS = [(0.039, 0.159), (0.039, 0.141)]
# left column of the panel: X shift, trigger level, external trigger socket, Y shift, Y input
KNOB_POS_X = (-0.039, 0.103)
KNOB_LEVEL = (-0.039, 0.084)
JACK_TRIG = (-0.039, 0.068)
KNOB_POS_Y = (-0.039, 0.051)
INPUT_Y = (-0.039, 0.030)
SMALL_R = 0.0042
# large switches: time / div. and volt / div.
BIG_T = (-0.007, 0.082)
BIG_V = (-0.006, 0.031)
BIG_CAP_R, BIG_SKIRT_R = 0.0105, 0.0135
T_LABELS = ["50", "20", "10", "5", "2", "1", ".5", ".2", ".1"]
V_LABELS = ["5", "2", "1", ".5", ".2", ".1", ".05", ".02", ".01"]
SCALE_A0, SCALE_A1 = 225.0, -45.0      # scale arc: from bottom left over the top to bottom right, degrees
T_POINTER = 3                           # which digit the switch points at (index)
V_POINTER = 2
# right column: buttons (power, ms/us, single/auto, trigger +/-, int./ext., open/closed input)
BTN_X, BTN_WH = 0.039, (0.010, 0.0068)
BUTTONS = [0.108, 0.098, 0.088, 0.071, 0.058, 0.040]
GROUND = (0.041, 0.020)                 # case ground terminal

# left side (-x): two trimmer holes, a screwdriver slot; the right side (+x) has an inventory sticker
SIDE_C, SIDE_WH = (-0.005, 0.105), (0.240, 0.160)          # side image: (y, z)
SIDE_HOLES = [(0.003, 0.108), (-0.050, 0.108)]
SIDE_SCREW = (-0.105, 0.047)
SIDE_TAG = (0.072, 0.150)               # on the right side (y, z), 24 x 13 mm
TAG_WH = (0.024, 0.013)

# tray: slots along the sides
TRAY_Z = (FOOT_H, 0.020)
VENT_C, VENT_WH = (-0.004, 0.0145), (0.230, 0.0085)        # (y, z)

# power supply box at the back: perforation on the back face and sides
PSU_X, PSU_Y, PSU_Z = (-0.035, 0.035), (0.123, 0.146), (0.075, 0.181)
