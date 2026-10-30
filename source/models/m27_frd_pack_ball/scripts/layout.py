"""Layout of the Freedom gunsmith's table M27, shared by build_m27.py (geometry) and make_decals.py
(decals lie on the same faces: decals are projected in kmats along the world axes).

Axes: X is width, Y is depth (the face looks to -Y), Z is up. The sizes of the props and their sources
are in the docstring of build_m27.py.
"""
# table (as in M05/M11/M15/M23)
X0, X1, Y0, Y1 = -0.80, 0.80, -0.36, 0.36
ZT, ZP, SHD, CAB_W = 0.78, 1.40, 0.30, 0.42
YP = Y1 - 0.02                                               # panel face
YS = Y1 - SHD                                                # front of the shelf

# faces for decals: (x0, x1, z0, z1) or (y0, y1, z0, z1) and the face coordinate
CAB_FACE = (X1 - CAB_W + 0.004, X1 - 0.004, 0.084, 0.746)    # drawer fronts, face y = Y_FRONTS
Y_FRONTS = Y0 + 0.02 - 0.018
CAB_SIDE = (Y0 + 0.02, Y1 - 0.01, 0.08, 0.75)                # right side of the cabinet, face x = X1
PANEL = (X0 + 0.03, X1 - 0.03, ZT, ZP - 0.02)                # superstructure panel, face y = YP

# gun cleaning mat on the table: x0, x1, y0, y1, thickness. Moved to the right: the vise M81 (slot 1)
# takes the front left corner, the borescope M82 (slot 2) stands on the right part of the mat
MAT = (-0.47, 0.43, -0.33, 0.01, 0.003)
ZM = ZT + MAT[4]                                             # top of the mat

# module places: slot 1 - the barrel vise M81 at the front left corner, on a steel plate clamped to the
# table with two clamps; slot 2 - the borescope M82 on the mat by the cleaning rod; slot 3 - the gauge
# set M83 on the right by the magazines. Module centers (their origin is the middle of the bottom)
SLOT1 = (-0.64, -0.22)
PLATE = (0.22, 0.27, 0.008)                                  # slot 1 plate: along x, along y from the edge, thickness
SLOT2 = (0.28, -0.12)
SLOT3 = (0.62, -0.05)
SLOT3_FOOT = (0.205, 0.180)                                  # clean spot under the gauge set

# cases: the big one (Pelican 1520 class) - two under the table, the small one (class 1200) - on the left shelf
BIG = (0.502, 0.401, 0.188)                                  # length, depth, height
SMALL = (0.295, 0.246, 0.140)
BIG_LOW = (-0.72, -0.18, 0.0)                                # x0, y0, z0 of the lower one (facing -y)
BIG_TOP = (-0.45, 0.03, BIG[2], 10.0)                        # center x, y, bottom, rotation, degrees
SMALL_POS = (-0.745, YS + 0.03, ZP)                          # x0, y0, z0
# decals on the cases: the face of the lower big one (y = BIG_LOW[1]) and the face of the small one on the shelf
BIG_FACE = (BIG_LOW[0] + 0.03, BIG_LOW[0] + BIG[0] - 0.03, 0.025, BIG[2] - 0.05)
SMALL_FACE = (SMALL_POS[0] + 0.02, SMALL_POS[0] + 0.10, ZP + 0.02, ZP + SMALL[2] * 0.62)
