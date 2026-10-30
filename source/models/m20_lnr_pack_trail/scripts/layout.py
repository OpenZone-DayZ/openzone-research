"""Placement of the M20 cabinet decals, shared by build_m20.py (geometry) and make_decals.py (images).

kmats projects decals along the world axes, so sizes and positions are defined once, here.
"""
# cabinet body: 0.95 x 1.8 x 0.45 m
X0, X1, Y0, Y1 = -0.475, 0.475, -0.225, 0.225

# map on the right side panel (faces +x): y0, y1, z0, z1; the sheet is 340 x 480 mm and ripples up to
# MAP_T off the panel, pressed flat at the buttons
MAP = (-0.175, 0.165, 1.03, 1.51)
MAP_T = 0.0008
X_MAP = X1 + MAP_T

# plywood patch over the crack in the right side panel (y0, y1, z0, z1); the crack runs along the grain
# from the bottom of the panel up under the patch and shows above and below it; CRACK is that decal
# (y0, y1, z0, z1)
PATCH = (0.02, 0.15, 0.22, 0.50)
CRACK = (0.045, 0.125, 0.04, 0.68)

# inventory tag on the left side panel (faces -x): aluminium plate, number punched in digits
TAG = (-0.10, -0.04, 1.615, 1.645)
