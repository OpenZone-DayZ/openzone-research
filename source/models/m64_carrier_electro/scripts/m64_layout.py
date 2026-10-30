"""M64 - dimensions shared by build_m64.py (Blender) and make_decals.py (system Python + Pillow): a folded
blueprint diagram with a compact disc on top. No dependencies - both import it.

Generator axes: X is the width of the folded sheet (to the right), Y is the height (the top of the
sheet at +Y, the bottom towards the viewer, at -Y), Z is up. The origin is the centre of the stack on
the ground.

Image coordinates, metres / mm:
- sheet (schematic.png): the whole top sheet PW x PH, the top of the image is the top of the sheet
  (+Y); in the generator these are world x, y (lifting the corner changes only z);
- disc (cd_top.png, cd_data.png): a CD_D x CD_D square in the disc axes (u along the X axis rotated by
  CD_ROT, v along the rotated Y), the centre is the disc centre; in the generator it is the vertex
  attribute `pp`.

make_decals.py takes PW, PH, X0, Y1, the frame (FRAME_*, TB_*), CD_*, R_*, PAPER, INK, LINE_ORANGE
from here: do not change them without redrawing the images (the images live in work/; the disc and
the sheet under it are matched by CD_C, CD_ROT). The LOD grids, the sheet wave, the bend of the free
edges and the stack edge profiles are generator-only.
"""
import math

# --- sheet: a circuit diagram on A1 (GOST 2.301-68: 594 x 841 mm), folded per GOST 2.501-88 to A4
#     (210 x 297): accordion-folded into 4 strips of 210 mm, then in half across; the title block
#     (GOST 2.104-68, form 1: 185 x 55 mm) stays on top, in the bottom right corner.
#     Frame: 5 mm from the cut edge on the right and at the bottom (20 mm on the left lies at the other
#     edge of the A1, not on this panel) -----------------------------------------------------------
PW, PH = 0.210, 0.297
X0, X1 = -PW / 2, PW / 2
Y0, Y1 = -PH / 2, PH / 2
N_LAYERS = 8                      # 4 accordion strips x 2 halves
PAPER_T = 0.0002                  # top sheet, for looks (diazo paper 80-100 g/m2 ~ 0.1 mm; an edge of
                                  # 0.1 mm gives degenerate faces in Check_All, 0.2 is like the M62 tape)
GAP = 0.00025                     # top sheet above the stack (the folds spring)

# stack: 8 sheets of 0.1 mm each, but the folds spring - thicker at the folds, pressed down in the middle
T_MID = 0.0030
BUMP_TOP = 0.0014                 # top edge: the fold in half, 4 loops one inside another
BUMP_LEFT = 0.0009                # left edge: accordion folds 1-2 and 3-4 (and 5-6, 7-8 at the bottom)
BUMP_RIGHT = 0.0005               # right edge: fold 2-3 (and 6-7), the rest are cut edges
BUMP_SIG = 0.010

# Layers from the top (L1 is the top sheet, the right strip of the A1, the lower half with the title
# block): at the left edge the accordion fold loops L1-L2, L3-L4, L5-L6, L7-L8; at the right edge the
# loops L2-L3 and L6-L7, with the cut edges of L1, L4, L5, L8 between them; on top the fold in half (L1
# wraps the others from outside); at the bottom eight cut edges.

# --- LOD grids ------------------------------------------------------------------------------------
# stack: its top is the sum of humps in x and in y, linear between the grid lines (z_stack with lod),
# flat in each cell; the lines inside are for the edges (the profile changes along the edge)
STACK_GRID = {
    0: ([X0, X0 + 0.010, -0.040, 0.020, 0.070, X1 - 0.010, X1],
        [Y0, -0.085, -0.010, 0.060, Y1 - 0.010, Y1]),
    1: ([X0, X0 + 0.010, X1 - 0.010, X1],
        [Y0, Y1 - 0.010, Y1]),
}
# top sheet: all the stack lines (otherwise the sheet between lines would pass through the stack's kink)
# plus its own - for the wave, the bent-up corner (x 0.020 and y Y0 + LIFT_RY are the boundary of the
# lift; inside it the lines are denser so that the corner edges follow an arc rather than a polyline),
# the bend of the edges and the disc support
GRID = {
    0: ([X0, X0 + 0.010, -0.068, -0.040, -0.012, 0.020, 0.045, 0.058, 0.070, 0.083, X1 - 0.010, X1],
        [Y0, Y0 + 0.008, -0.130, -0.118, -0.101, -0.085, -0.064, -0.0435, -0.010, 0.025, 0.060, 0.095, 0.120,
         Y1 - 0.010, Y1]),
    1: ([X0, X0 + 0.010, -0.040, 0.020, 0.060, X1 - 0.010, X1],
        [Y0, -0.100, -0.0435, 0.020, 0.085, Y1 - 0.010, Y1]),
}


def _bump_x(x):
    return (BUMP_LEFT * math.exp(-((x - X0) / BUMP_SIG) ** 2)
            + BUMP_RIGHT * math.exp(-((X1 - x) / BUMP_SIG) ** 2))


def _bump_y(y):
    return BUMP_TOP * math.exp(-((Y1 - y) / BUMP_SIG) ** 2)


def _lin(vals, fn, t):
    """fn over the points vals, linear between them."""
    if t <= vals[0]:
        return fn(vals[0])
    for a, b in zip(vals, vals[1:]):
        if t <= b:
            f = (t - a) / (b - a)
            return fn(a) * (1 - f) + fn(b) * f
    return fn(vals[-1])


def z_stack(x, y, lod=None):
    """Top of the stack under the top sheet. lod says how this LOD is built: the humps are linear between
    its grid lines (cells are flat, triangles match the bilinear form); None means smooth."""
    if lod is None:
        return T_MID + _bump_x(x) + _bump_y(y)
    xs, ys = STACK_GRID[lod]
    return T_MID + _lin(xs, _bump_x, x) + _lin(ys, _bump_y, y)


# top sheet (the right accordion strip, the lower half): tied by folds on the left and at the top, while
# the bottom right corner (with the title block) is two cut edges: it has sprung and is lifted
LIFT = 0.0075
LIFT_RX, LIFT_RY = 0.085, 0.105


def lift(x, y):
    f = 1.0 - (X1 - x) / LIFT_RX - (y - Y0) / LIFT_RY
    return LIFT * max(0.0, f) ** 2


# the sheet does not lie flat: a gentle wave (upwards only, as it lies on the stack) and a bend of the
# free edges (the right and bottom ones are cut edges); at the folds (left and top) the sheet is held
# down and the wave dies out over HOLD
WAVE = 0.00045
CURL_R, CURL_B, CURL_W = 0.0006, 0.0004, 0.022
HOLD = 0.050


def _smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3.0 - 2.0 * t)


def wave(x, y):
    hold = _smooth((x - X0) / HOLD) * _smooth((Y1 - y) / HOLD)
    w = (0.5 + 0.25 * math.sin(2 * math.pi * x / 0.14 + 0.7) * math.sin(2 * math.pi * y / 0.19 + 1.9)
         + 0.25 * math.sin(2 * math.pi * (x + 0.6 * y) / 0.23 + 2.6))
    curl = (CURL_R * max(0.0, 1.0 - (X1 - x) / CURL_W) ** 2
            + CURL_B * max(0.0, 1.0 - (y - Y0) / CURL_W) ** 2)
    return hold * (WAVE * w + curl)


def z_sheet(x, y, lod=0):
    """Centre line of the top sheet (above the stack of this LOD)."""
    return z_stack(x, y, lod) + GAP + PAPER_T / 2 + lift(x, y) + wave(x, y)


# stack edges: outward shift (m) by the height fraction h (1 is the top, 0 the ground)
ROLL_K = 0.47                     # fold in half at the top: a roll, radius ~ half the stack thickness
SIDE_L, SIDE_R = 0.00058, 0.00030  # accordion loops on the left (4) and on the right (2): a shallow barrel
FAN = 0.0013                      # cut edges at the bottom: the lower layers fan out up to 1.3 mm

# --- title block and frame (mm from the top left corner of the top sheet, as in the image) --------
FRAME_R = 205.0                   # right frame line
FRAME_B = 292.0                   # bottom
TB_X0, TB_Y0 = FRAME_R - 185.0, FRAME_B - 55.0

# --- compact disc (IEC 60908 / ECMA-130): D 120 mm, 1.2 mm, hole D 15, clamping zone up to D 33,
#     mirror band up to D 41; paper label D 117 with a D 41 hole -----------------------------------
CD_D = 0.120
CD_R = CD_D / 2
CD_T = 0.0012
R_HOLE = 0.0075
R_CLAMP = 0.0165
R_LABEL0 = 0.0205                 # inner edge of the label
R_LABEL1 = 0.0585                 # outer edge (beyond it is the 1.5 mm mirror rim)
CD_C = (0.062, 0.080)             # centre: towards the top right corner, ~17 mm past the right edge
CD_ROT = 18.0                     # degrees, counter-clockwise (seen from above)
CD_CH_R, CD_CH_Z = 0.0004, 0.0003  # chamfer of the rim on top (the moulding is rounded)
R_MOLD, R_STACK = 0.0112, 0.0168  # moulded ring and stacking ring in the clamping zone (relief)

# --- colours (sRGB): blueprint - violet-blue lines on bluish-grey diazo paper ---------------------
PAPER = (178, 198, 224)
PAPER_BACK = (208, 217, 228)
INK = (48, 38, 112)
LINE_ORANGE = (222, 112, 34)      # colour of the "Electronics" line (the stripe of the M49 tag)
AGED = (214, 204, 168)            # diazo paper yellowed by light


def cd_local(x, y):
    """World x, y -> disc axes (u, v)."""
    a = math.radians(CD_ROT)
    dx, dy = x - CD_C[0], y - CD_C[1]
    return dx * math.cos(a) + dy * math.sin(a), -dx * math.sin(a) + dy * math.cos(a)


def cd_world(u, v):
    a = math.radians(CD_ROT)
    return CD_C[0] + u * math.cos(a) - v * math.sin(a), CD_C[1] + u * math.sin(a) + v * math.cos(a)
