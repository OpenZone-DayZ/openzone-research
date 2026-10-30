"""Dimensions shared by M66 (the "Trails" carrier): build_m66.py (Blender) and make_decals.py (system
Python + Pillow) both use them. Metres. Sources of the sizes are in the docstring of build_m66.py.

The tube uses its own coordinates: u runs along the axis from the outer end of the bottom (0) to the
mouth (MOUTH_U), v across (+v is the side where the strap, the cord and the cap have fallen), z is up;
the angle theta around the axis: v = r cos(theta), z = ZC + r sin(theta) (90 degrees is the top, 180
is the -v side). In Blender: X = u - U0, Y = v - V0, Z = z. The tube lies on the ground, the mouth at
+X; the cap is off and stands bottom down beside the protruding roll of tracing paper, the carrying
strap and the cap cord have fallen on the +v side.

The tracing paper uses its own coordinates (s, t): s from the outer end of the roll (0) deep into the
tube, t along the sheet across the axis from the free edge of the outer turn (0) inwards in the
winding direction.

make_decals.py takes only SHEET_T and LABEL_SIZE from here: do not change them without redrawing the
images.
"""
import math

# --- tube for the A2 format (a 420 x 594 sheet is rolled along the short side) --------------------
R = 0.045                   # body, outer radius (D 90)
WALL = 0.0023               # wall
R_IN = R - WALL             # inside
R_END = 0.0472              # closed bottom: a cup fitted over the body
END_L = 0.032               # its length
BOT_R = 0.004               # rounding of the outer end of the bottom (two belts of faces)
MOUTH_U = 0.455             # mouth: tube length without the cap
LIP_CH = 0.0008             # chamfer of the outer edge of the mouth
ZC = R_END                  # the tube lies on the bottom: the axis is at its radius above the ground
SIDES = (28, 14)            # faces around the circumference per LOD (a vertex at the top and the bottom)

# strap clamps are knurled bands (3 cm wide, ~13 cm between them in the reference)
CLAMPS = (0.150, 0.300)     # band centres along u
CLAMP_W = 0.026
CLAMP_RIBS = 5
MOUTH_BAND = 0.050          # smooth band at the mouth, the cap goes onto it
KNURL_ALONG = 0.024         # knurl diamonds: pitch along the axis
KNURL_N = 16                # diamonds around the circumference (an integer, so the pattern meets at the seam)

# clamp lugs: a cast bracket on the clamp - two posts and a crossbar, the strap is threaded under it
LUG_L = 0.026               # along the axis, across the clamp width: 21 mm between the posts for a 20 mm strap
LUG_D = 0.008               # along the arc
LUG_T = 0.0025              # thickness of the posts and the crossbar
LUG_SINK = 0.0028           # posts are sunk in so they do not hang in the air on a coarse middle LOD
LUG_GAP = 0.0022            # clearance under the crossbar above radius R (1.8 mm strap and a gap)

# --- removed cap: a cup that fits onto the mouth, standing bottom down on the ground --------------
CAP_R = 0.0475
CAP_RI = CAP_R - 0.0023
CAP_H = 0.050
CAP_IN_Z = 0.0025           # inner bottom
CAP_CH_B = 0.0020           # bottom chamfer
CAP_CH_T = 0.0012           # chamfer of the outer edge of the rim
CAP_SIDES = (24, 12)        # faces around the cap per LOD

# --- tracing paper roll: A2, 420 mm wide, 594 mm wound --------------------------------------------
SHEET_T = 0.594             # sheet length along the winding
ROLL_DROP = 0.0018          # the roll lies on the bottom of the tube: its axis is below the tube axis
ROLL_R = R_IN - ROLL_DROP - 0.0010     # outer turn (1 mm from the wall at the bottom)
ROLL_WALL = 0.0012          # turns at the end (2.4 turns of 40 g/m2 paper and air)
ROLL_STEP = 0.0006          # step at the free edge of the outer turn
ROLL_OUT = 0.080            # protrudes from the mouth
ROLL_END = MOUTH_U + ROLL_OUT
ROLL_FLARE = 0.0012         # outside, the roll unwinds slightly
ROLL_TELE = 0.0015          # inner turns slide out of the end: the end is stepped
ROLL_FLAP = 0.0012          # the free edge of the outer turn lags at the end
EDGE_THETA = math.radians(122)     # the free edge of the outer turn is on top, closer to -v
WIND = -1.0                 # the turn runs with decreasing theta from the edge: the map is not mirrored outside
DEEP_U = 0.415              # the inside of the mouth is visible up to here, beyond it is a dark gap
ROLL_IN_U = 0.480           # the inside of the roll is visible up to here, beyond it is dark
ROLL_CONE_U = 0.425         # inside the roll: a cone into the dark, apex on the axis (no wall, no bottom)
TURN_IN0 = 2 * math.pi * ROLL_R      # inside the roll: the next turn of the sheet (t one turn further)
CREASE_T = 0.231            # crease of the sheet along the axis (t), visible from the front near the free edge

# --- tag on the body ------------------------------------------------------------------------------
LABEL_SIZE = (0.070, 0.040)         # along the axis, along the arc
LABEL_U = 0.360
LABEL_THETA = math.radians(112)     # middle of the tag: on top, slightly towards -v
LABEL_T = 0.0003
LABEL_PEEL = (0.012, 0.010, 0.0016)  # peeled corner at the mouth: along the axis, along the arc, lift

# --- carrying strap and cap cord ------------------------------------------------------------------
STRAP_W = 0.020
STRAP_T = 0.0018
# strap at the lug: above radius R it passes under the crossbar, the tail lies over the strap and over
# the crossbar; the wrap around the crossbar is a half-circle (centre along the arc, above R, radius)
STRAP_Y = (0.0011, 0.0030, 0.0057)
STRAP_WRAP = (0.0044, 0.0034, 0.0023)
CORD_R = 0.00125
CORD_HOLE_Y = 0.0020        # hole for the cord in the post of the second lug: height above R

CAP_C = (0.505, ROLL_R + ROLL_FLARE + CAP_R + 0.0016)     # cap centre (u, v)

# model frame and origin: the middle of the frame, on the ground
U_MIN, U_MAX = 0.0, CAP_C[0] + CAP_R
V_MIN, V_MAX = -R_END, CAP_C[1] + CAP_R
U0 = (U_MIN + U_MAX) / 2
V0 = (V_MIN + V_MAX) / 2


def theta_list(n):
    """Angles of the body polygon vertices: a vertex at the top (90) and at the bottom (270)."""
    return [math.pi / 2 + 2 * math.pi * k / n for k in range(n)]


def facet_radius(r, n, th):
    """Distance from the axis to the flat face of an n-gon whose vertices lie on radius r, at angle th."""
    step = 2 * math.pi / n
    rel = (th - math.pi / 2) % step - step / 2
    return r * math.cos(step / 2) / math.cos(rel)


def facet_mid(n, k):
    """Angle of the middle of face k counted from the top vertex towards +v (decreasing theta)."""
    return math.pi / 2 - 2 * math.pi * (k + 0.5) / n


def roll_axis():
    """Axis of the roll (v, z)."""
    return 0.0, ZC - ROLL_DROP


def roll_radius(phi, u):
    """Outer turn of the roll: phi runs from the free edge in the winding direction (0..2pi), the radius
    drops by a step towards the end of the turn (it goes under the edge); outside the mouth the roll
    unwinds slightly."""
    r = ROLL_R - ROLL_STEP * phi / (2 * math.pi)
    if u > MOUTH_U:
        r += ROLL_FLARE * (min(u - MOUTH_U, ROLL_OUT) / ROLL_OUT) ** 1.5
    return r


def sheet_t(phi, r=ROLL_R):
    return phi * r


LUG_THETA = facet_mid(SIDES[0], 2)     # middle of the third face from the top towards +v (58 degrees)
