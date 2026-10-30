"""M67 - dimensions shared by build_m67.py (Blender) and make_decals.py (system Python + Pillow): a sport
target No. 4 folded in four, with bullet holes, and an A5 shooting protocol on a paper clip on top.
No dependencies - both import it.

Generator axes: X is the stack width (to the right), Y is the height (the top at +Y, the bottom
towards the viewer, at -Y), Z is up. The origin is the centre of the folded stack on the ground.

Image coordinates:
- target (target.png): the whole SHEET x SHEET sheet, the image centre is the centre of the rings, s to
  the right, t up (mm in the image are from the top left corner, y down). The top layer of the stack
  is the quarter of the sheet s > -FOLD_A, t > -FOLD_B, print up: s = x - CX, t = y - CY (target_st).
  The bottom layer (turned back at the second fold) is print down: s = x - CX,
  t = -(y - CY) - 2 * FOLD_B (target_st_bottom);
- protocol (protocol.png): a PROTO_W x PROTO_H sheet in its own axes (u to the right, v up, the origin
  is the sheet centre, rotated by PROTO_ROT); in the generator it is the vertex attribute `pp`.
"""
import math

# --- target: sport No. 4 (pistol 25/50 m; ISSF 25 m precision / 50 m pistol): ten D 50 mm,
#     rings every 50 mm up to one D 500, inner ten D 25, black "bull" (7-10) D 200,
#     digits 1-9 on the vertical and horizontal ~10 mm high; sheet 500 x 500 mm, paper 60-80 g/m2 ---
SHEET = 0.500
R_RING = [0.025 * k for k in range(1, 11)]       # 10, 9, ..., 1: radii 25 ... 250 mm
R_X = 0.0125                                      # inner ten
R_BLACK = 0.100
PAPER_T = 0.0001                                  # sheet ~0.1 mm

# folded in four, but not evenly: the first fold (vertical) is FOLD_A left of the centre, the second
# (horizontal) is FOLD_B below - the larger quarter is on top, the centre of the rings is at the corner
# of the stack
FOLD_A, FOLD_B = 0.007, 0.010
PW, PH = SHEET / 2 + FOLD_A, SHEET / 2 + FOLD_B   # 257 x 260 mm
X0, X1 = -PW / 2, PW / 2
Y0, Y1 = -PH / 2, PH / 2
CX, CY = X0 + FOLD_A, Y0 + FOLD_B                 # centre of the rings (on the top layer)


def target_st(x, y):
    """World x, y on the top layer -> sheet coordinates s, t (from the centre of the rings)."""
    return x - CX, y - CY


def target_st_bottom(x, y):
    """World x, y on the bottom layer (print down) -> s, t: the layer is turned back at the second fold (y =
    Y0)."""
    return x - CX, -(y - CY) - 2 * FOLD_B


# stack: 4 layers of 0.1 mm, but the folds spring: it is thicker at the folds (the left edge is the first
# fold, at the upper and lower pair; the bottom edge is the second fold, a loop of two layers), and at
# the cut edges (right and top edge) the layers drift slightly apart
T_MID = 0.0011
BUMP_LEFT = 0.0007
BUMP_BOTTOM = 0.0011
BUMP_SIG = 0.009
GAPE = 0.0004
GAPE_SIG = 0.012


def z_top(x, y):
    """Top of the stack (the top layer of the target) at the point (x, y)."""
    return (T_MID + BUMP_LEFT * math.exp(-((x - X0) / BUMP_SIG) ** 2)
            + BUMP_BOTTOM * math.exp(-((y - Y0) / BUMP_SIG) ** 2)
            + GAPE * math.exp(-((X1 - x) / GAPE_SIG) ** 2) + GAPE * math.exp(-((Y1 - y) / GAPE_SIG) ** 2))


# LOD grids: lines at the folds (humps) and at the cut edges (drifted layers)
# (x -0.020 / 0.080 and y -0.040 / Y1 - 0.014 are the boundary of the part under the protocol, build_m67.HIDDEN)
GRID = {
    0: ([X0, X0 + 0.004, X0 + 0.010, X0 + 0.022, -0.060, -0.020, 0.030, 0.080, X1 - 0.014, X1 - 0.004, X1],
        [Y0, Y0 + 0.004, Y0 + 0.010, Y0 + 0.022, -0.040, 0.040, Y1 - 0.014, Y1 - 0.004, Y1]),
    1: ([X0, X0 + 0.008, -0.020, 0.080, X1 - 0.010, X1],
        [Y0, Y0 + 0.008, -0.040, Y1 - 0.014, Y1]),
}

# bullet holes: (s, t) mm from the centre of the rings, radius mm, kind: "" is clean (a wipe ring),
# "soot" is a close-range shot (soot, powder specks, scorching), "soot2" is farther (soot and powder
# specks only). 9 mm pistol: a hole in paper of ~8.5 mm. Seven on the top quarter (s > -7, t > -10),
# one on the bottom layer (visible from below), two on the middle layers
HOLES = [
    (14.0, 22.0, 4.3, ""), (39.0, 8.0, 4.2, ""), (6.0, 47.0, 4.2, ""), (55.0, 30.0, 4.3, ""),
    (29.0, 60.0, 4.2, ""), (70.0, 13.0, 4.2, ""),
    (22.0, 121.0, 4.6, "soot"), (114.0, 22.0, 4.4, "soot2"),
    (24.0, -44.0, 4.2, ""), (-31.0, 17.0, 4.2, ""),
]

# --- shooting protocol: an A5 form (ISO 216: 148 x 210), lies on top with its top edge at the top cut
#     edge of the target, rotated by PROTO_ROT; the bottom right (free) corner has sprung ----------
PROTO_W, PROTO_H = 0.148, 0.210
PROTO_T = 0.0002                                  # for looks (0.1 mm paper gives degenerate faces)
PROTO_ROT = 3.0                                   # degrees, counter-clockwise (seen from above)
CLIP_U = 0.030                                    # paper clip: along the top edge, from the middle to the right


def _proto_center():
    a = math.radians(PROTO_ROT)
    c, s = math.cos(a), math.sin(a)
    # the bottom right corner is 4 mm from the right edge of the stack
    px = X1 - 0.004 - (PROTO_W / 2 * c + PROTO_H / 2 * s)
    # at the clip the top edge of the protocol is 0.5 mm beyond the top cut edge of the target
    py = Y1 + 0.0005 - (CLIP_U * s + PROTO_H / 2 * c)
    return px, py


PROTO_C = _proto_center()


def proto_world(u, v):
    """Protocol axes (u, v from the sheet centre) -> world x, y."""
    a = math.radians(PROTO_ROT)
    return (PROTO_C[0] + u * math.cos(a) - v * math.sin(a), PROTO_C[1] + u * math.sin(a) + v * math.cos(a))


def proto_local(x, y):
    a = math.radians(PROTO_ROT)
    dx, dy = x - PROTO_C[0], y - PROTO_C[1]
    return dx * math.cos(a) + dy * math.sin(a), -dx * math.sin(a) + dy * math.cos(a)


# the free corner of the protocol (bottom right) is lifted
LIFT = 0.0045
LIFT_RU, LIFT_RV = 0.070, 0.085


def proto_lift(u, v):
    f = 1.0 - (PROTO_W / 2 - u) / LIFT_RU - (v + PROTO_H / 2) / LIFT_RV
    return LIFT * max(0.0, f) ** 2


# coloured band (camoGround): along the sheet diagonal from bottom left to top right, width BAND_W
BAND_W = 0.026
BAND_ANG = math.degrees(math.atan2(PROTO_H, PROTO_W))


def band_dist(u, v):
    """Signed distance from the band axis (through the sheet centre)."""
    a = math.radians(BAND_ANG)
    return -u * math.sin(a) + v * math.cos(a)


# protocol grid (mm from the centre along u and v): lines at the lifted corner
PROTO_GRID = {
    0: ([-0.074, -0.020, 0.020, 0.045, 0.074], [-0.105, -0.075, -0.040, 0.020, 0.105]),
    1: ([-0.074, 0.030, 0.074], [-0.105, -0.050, 0.105]),
}

# --- stationery paper clip 28 mm (the length per shops; the width ~8.6 mm and the wire D 0.8 are
#     estimated from a photo): a "Gem" - the outer loop on top, the inner one under the protocol sheet
#     and the top layer of the target --------------------------------------------------------------
CLIP_L = 0.028
CLIP_W = 0.0086
CLIP_R = 0.0004
CLIP_IN = 0.0215                                  # how far the clip reaches onto the sheet from the edge

# --- colours (sRGB) -------------------------------------------------------------------------------
PAPER = (236, 231, 216)                           # target paper is white or cream (ISSF)
PAPER_BACK = (228, 224, 212)
PROTO_PAPER = (232, 230, 222)
INK = (24, 24, 26)
BLUE = (38, 84, 168)                              # colour of the "Ballistics" line (the stripe of the M52 tag)
BAND = (78, 126, 200)                             # protocol band: the same blue, but a lighter print,
                                                  # so that the pen reads on it
