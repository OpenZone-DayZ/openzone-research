"""M52 sizes (a case with weapon parts), shared by build_m52.py and make_decals.py. Metres, Blender
axes: X is the case length, Y is depth (the face with the handle is at -Y), Z is up, the origin is the
centre of the bottom. The sources of the figures are in the docstring of build_m52.py.
"""
import math

# --- body (Pelican 1120: outside 206 x 167 x 90, inside 184 x 121 x 78 mm) ---------------------
BX, BY = 0.100, 0.072          # half-sizes of the body at the top of the walls (200 x 144)
FL = 0.003                     # the parting belt is 3 mm wider: 206 x 150
RC = 0.012                     # corner rounding in plan (along the wall)
DRAFT = 0.003                  # body wall draft: 3 mm narrower at the bottom (half of it at the mid LOD)
Z_FL0, Z_P = 0.058, 0.066      # bottom of the body belt, the parting plane
IX, IY, RI = 0.092, 0.0605, 0.006   # inside 184 x 121
FOAM_Z = 0.060                 # top of the foam in the body
Z_LF1, Z_LT = 0.072, 0.090     # top of the lid belt, top of the lid (closed)
LID_TOP_IN = 0.0045            # the lid wall narrows towards the top
Z_LIN = 0.069                  # lid foam ('egg crate'), closed

# hinges and lid rotation: the axis along X at the back on the parting line, open by 100 degrees
HINGE_Y, HINGE_Z = BY + FL, Z_P   # the axis runs along the back edge of the belt: the lid lies without a gap
HINGE_R, HINGE_X, HINGE_LEN = 0.004, (-0.055, 0.055), 0.040
LID_OPEN = 100.0


def lid_rot(p):
    """Lid point from the closed to the open position (rotation about the hinge axis)."""
    a = math.radians(-LID_OPEN)
    dy, dz = p[1] - HINGE_Y, p[2] - HINGE_Z
    return (p[0], HINGE_Y + dy * math.cos(a) - dz * math.sin(a), HINGE_Z + dy * math.sin(a) + dz * math.cos(a))


# direction from the hinge axis to the front edge of the open lid (for the lid foam pattern): (0, -1, 0)
# when closed, after the rotation
LID_DIR = (0.0, -math.cos(math.radians(-LID_OPEN)), -math.sin(math.radians(-LID_OPEN)))

# latches on the front edge of the lid (open), handle and valve on the face of the body
LATCH_X, LATCH_HW = 0.062, 0.011
HANDLE_X, HANDLE_Z, HANDLE_W, HANDLE_T = 0.042, (0.026, 0.058), 0.004, 0.0045
VALVE_Z, VALVE_R = 0.040, 0.0095

# empty inventory sticker on the face of the body, right
STK_C, STK = (0.071, 0.024), (0.032, 0.020)

# --- body foam: Pick N Pluck, 1/2" (12.7 mm) cubes --------------------------------------------
PITCH = 0.0127
GX0, GY0 = -0.0889, -0.05715   # grid lines: GX0 + k * PITCH, GY0 + j * PITCH


def cells(k0, k1, j0, j1):
    """Plucked cubes k0..k1, j0..j1 (inclusive) -> (x0, x1, y0, y1)."""
    return (GX0 + k0 * PITCH, GX0 + (k1 + 1) * PITCH, GY0 + j0 * PITCH, GY0 + (j1 + 1) * PITCH)


POCKETS = {                     # name -> (x0, x1, y0, y1), depth
    "bolt": (cells(1, 8, 5, 6), 0.014),
    "cases": (cells(10, 13, 5, 6), 0.0075),
    "pin": (cells(1, 8, 3, 3), 0.0045),
    "spring": (cells(1, 7, 1, 1), 0.006),
}

# --- parts ----------------------------------------------------------------------------------
# AKM bolt (estimated from a photo): head D 18.5 x 24 with two locking lugs, tail D 10.5
BOLT_Y = 0.01905
BOLT_X0, BOLT_LEN = -0.0704, 0.090
BOLT_HEAD_R, BOLT_HEAD_L, BOLT_TAIL_R = 0.00925, 0.024, 0.00525
BOLT_ZC = FOAM_Z - POCKETS["bolt"][1] + BOLT_HEAD_R
# firing pin: 95 mm (Arsenal AK-262FF 3.8 x 0.2"), shaft D 4.5, tail D 7
PIN_Y, PIN_X0, PIN_LEN, PIN_R, PIN_R2 = -0.0127, -0.071, 0.095, 0.00225, 0.0035
PIN_ZC = FOAM_Z - POCKETS["pin"][1] + PIN_R2
# spring D 9 x 82, wire ~1.2, pitch 4.2
SPR_Y, SPR_X0, SPR_LEN, SPR_R, SPR_PITCH = -0.0381, -0.0725, 0.082, 0.0045, 0.0042
SPR_ZC = FOAM_Z - POCKETS["spring"][1] + SPR_R
# 7.62x39 cases (C.I.P.): 38.7 mm, rim D 11.35, D 10.07 at the shoulder at 30.5, neck D 8.6
CASE_LEN, CASE_RIM, CASE_SH, CASE_NECK, CASE_SH_X, CASE_NECK_X = 0.0387, 0.005675, 0.005035, 0.0043, 0.0305, 0.0329
CASE_ZC = FOAM_Z - POCKETS["cases"][1] + CASE_RIM
CASES = [                       # (axis y, head x, direction towards the neck)
    (0.0254, 0.0445, 1),        # brass - head to the left
    (0.0127, 0.0860, -1),       # lacquered steel - head to the right
]

# tag: white card 48 x 24 with corners cut at the eyelet, a blue stripe (the Ballistics line)
TAG_C, TAG_L, TAG_W, TAG_CUT = (0.062, -0.032), 0.048, 0.024, 0.005
TAG_ROT = -18.0                 # long axis from +X, degrees (the eyelet is at the -X end)
TAG_HOLE = 0.0185               # eyelet from the centre along the long axis
TAG_BOX = 0.058                 # square of the tag image in world axes
TAG_Z = (FOAM_Z + 0.0002, FOAM_Z + 0.0005)


def tag_point(s, t):
    """Tag point: s along the long axis (minus towards the eyelet), t across."""
    a = math.radians(TAG_ROT)
    return (TAG_C[0] + s * math.cos(a) - t * math.sin(a), TAG_C[1] + s * math.sin(a) + t * math.cos(a))


# --- edges, moulding and hardware after the photo of the case ----------------------------------
# roundings: a chamfer on top of the body belt; the lid top is rounded by one band (wall 14 -> 52 -> 90
# degrees: both breaks are under the smoothing threshold of 40, so the edge looks round)
CH = 0.0012                    # chamfer on top of the body belt
LID_RZ = 0.0022                # lid top rounding: from Z_LT - LID_RZ along the wall ...
LID_R0 = LID_TOP_IN * (1.0 - LID_RZ / (Z_LT - Z_LF1))   # ... (wall inset at this height)
LID_R1 = LID_R0 + 0.0028       # ... up to the top with inset LID_R1 (belt slope ~52 degrees)

# latch (open, sticking forward from the lid belt face): length; profile - build_m52.latch_profile
LATCH_L = 0.0255
# latch keeper on the body under the belt: bottom and step
KEEPER_Z = (0.044, 0.0515)
# handle: shoulders between pairs of post ribs, a steel axis pin through the ribs; the grip is wider
# than the shoulders
PIVOT_Z, PIVOT_R = 0.0505, 0.0015          # handle axis, pin radius (the ends show on the ribs)
RIB_DX, RIB_W, RIB_OUT = 0.0065, 0.0024, 0.007   # side ribs: offset from the shoulder axis, thickness, projection
HANDLE_HW, HANDLE_HG, HANDLE_HT = 0.0035, 0.0045, 0.003   # half-widths of shoulder and grip, half-thickness
HANDLE_GAP = 0.001             # from the wall to the back of the handle
HANDLE_BAR_Z, HANDLE_R = 0.0245, 0.007     # grip axis (below the valve) and bend radius
# padlock lugs at the front corners: on the body belt and on the lid (one above the other)
EAR_X, EAR_W, EAR_L, EAR_R = 0.083, 0.0045, 0.0075, 0.0021
EAR_DY = 0.004                 # hole centre - forward from the belt face

# 7.62x39 cases (C.I.P.): rim 1.5 mm, groove down to D 9.4, body from 2.9 mm - D 11.2
CASE_RIM_L, CASE_GROOVE_X, CASE_GROOVE_R, CASE_BODY_X, CASE_BODY_R = 0.0015, 0.0021, 0.0047, 0.0029, 0.0056


def lid_dir(v):
    """Direction from the closed lid to the open one (rotation without shift)."""
    a = math.radians(-LID_OPEN)
    return (v[0], v[1] * math.cos(a) - v[2] * math.sin(a), v[1] * math.sin(a) + v[2] * math.cos(a))
