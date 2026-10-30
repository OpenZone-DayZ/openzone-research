"""Layout constants of the M32 weapon cabinet, shared by build_m32.py (geometry) and
make_decals.py: the door number and the crate stripes lie on the same faces (kmats projects
decals along the world axes).

Axes: X - width, Y - depth (front at -Y), Z - up. Dimensions and their sources are in the
docstring of build_m32.py.
"""
import math

# Cabinet (kcabinet): the body front is at y = 0, the folding table in front of it reaches y = -0.50
X0, X1, Y0, Y1, H = -0.50, 0.50, 0.0, 0.50, 1.90
ZT, TD, DOOR_DEG = 0.85, 0.50, 105.0
DOOR_T = 0.025                                               # kcabinet.DOOR_T

# Left door, outside: the number is stenciled in white paint.
_th = math.radians(DOOR_DEG)
_w = (X1 - X0) / 2 - 0.002
DOOR_MID_Y = Y0 - DOOR_T - math.sin(_th) * _w / 2           # door middle along y
NUM = dict(text="17", z=1.52, w=0.17, h=0.11)               # 0.11 digit height - army stencil
NUM_X = (X0 - 0.16, X0 + 0.01)                               # x range of the door face

# Ammo crates in the lower compartment (stacked, left): x0, x1, y0 (front), y1, bottom, height
CRATES = [(-0.470, -0.010, 0.07, 0.36, 0.08, 0.155), (-0.462, -0.002, 0.08, 0.37, 0.235, 0.155)]
CRATE_LID = 0.02
# Stencil stripes on the crate face (x from the left edge): (dx0, dx1, color)
STRIPES = [(0.05, 0.08, "black"), (0.36, 0.39, "black"), (0.40, 0.43, "red")]
STRIPE_Z = (0.03, 0.115)
