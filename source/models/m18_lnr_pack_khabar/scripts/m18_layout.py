"""Sizes of the M18 safe shared by the generator (build_m18.py) and the decals (make_decals.py): numbers
only, no bpy - make_decals.py runs under the system Python.

Blender axes: X is width, Y is depth (face toward -Y), Z is up; metres.
"""

# body 757 x 425, plinth 75 mm, roof at 1.40 (see the build_m18.py docstring)
X0, X1, Y0, Y1 = -0.3785, 0.3785, -0.2125, 0.2125
ZB, ZR = 0.075, 1.40
R_BODY = 0.025                      # rounding of the body edges

# door in the rebate, sticks out 10 mm; around it a dark gap and the rebate frame on the body
DX0, DX1, DZ0, DZ1 = -0.305, 0.305, 0.165, 1.315
YD = Y0 - 0.010                     # door face
GAP = 0.006                         # rebate gap
BAND = 0.028                        # rebate frame width
MOLD = 0.040                        # moulding: from the door edge to the middle of the bead
PIN_IN = 0.064                      # trim line on the door: from the door edge to the outer line
PIN_SIDE = 0.050                    # trim line on the sides: from the edges

# on the door (axis x = 0) top to bottom: nameplate, code dial, wheel, keyhole
PLATE_Z, PLATE = 1.20, (0.15, 0.075)
DIAL_Z, DIAL_R, ROSE_R = 1.02, 0.065, 0.088
WHEEL_Z, WHEEL_R, WHEEL_T = 0.74, 0.115, 0.011
KEY_Z = 0.48
# enamel wear at the wheel and the dial (make_wear): centre and size of the image on the door face
WEAR_C, WEAR_S = (0.0, 0.93), (0.40, 0.62)

# roof: module places (slot 1 - M75 in the middle at the front, slot 2 - M76 under the lamp at the left,
# slot 3 - M77 at the right)
MOD_Y = -0.084
SLOT1 = (0.0, MOD_Y)
SLOT2 = (-0.235, MOD_Y)
SLOT3 = (0.235, MOD_Y)
# leather pad under the M76 loupe (its bell is at the module point + (-0.050, 0.050), build_m76.B)
PAD = (SLOT2[0], SLOT2[1] + 0.0035, 0.215, 0.205, 0.003)          # centre x, y, width, depth, thickness
LOUPE_BELL = (SLOT2[0] - 0.050, SLOT2[1] + 0.050, 0.0475)         # trace of the bell: centre, radius
# board under the M77 lead case (23 kg)
BOARD = (SLOT3[0], SLOT3[1], 0.235, 0.175, 0.018)
