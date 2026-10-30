"""M80 - dimensions shared by build_m80.py (Blender) and make_decals.py (system Python): where the map,
the ruler and the instruments lie on the board - the images are drawn in the same coordinates.

Board coordinates a, b, c: a is across (along the model's X, to the right), b is up the slope from
the lower edge of the board, c is along the normal from the plywood face. Metres. The sources of
the sizes are in the docstring of build_m80.py.
"""
TILT = 20.0                               # board tilt from the table, degrees

# plywood board: width, length along the slope, thickness (8 mm plywood)
BOARD_W, BOARD_L, BOARD_T = 0.206, 0.200, 0.008

# map sheet under celluloid: a0, a1, b0, b1 (the edges go under the tape and the clamp bar)
MAP = (-0.097, 0.097, 0.002, 0.197)
MAP_C = 0.0004                            # above the plywood (the celluloid is in the sheet texture)

# cloth tape along the side edges: from the board edge inward by TAPE_IN, along the slope to TAPE_B1
TAPE_IN, TAPE_B1 = 0.013, 0.172

# officer's ruler 200 x 100 x 1.5 (green, transparent): centre along a, lower edge along b
RULER = (0.200, 0.100, 0.0015)
RULER_A, RULER_B0 = 0.002, 0.112
RULER_C0 = MAP_C + 0.0003

# clamp bar on two wing bolts: b0, b1, thickness; the bolts' positions along a
BAR_B = (0.178, 0.196)
BAR_T = 0.003
BOLT_A = 0.072

# curvimeter KU-A (map measurer): dial centre (a, b) and handle rotation from the "up the board"
# direction, degrees. b is set so that the case rim stays clear of the board lip; the images do not
# depend on the position.
CURV_C, CURV_ROT = (-0.056, 0.0230), -70.0
CURV_R, CURV_TIP = 0.0195, 0.031          # lens-shaped body: radius of the round part, tip distance from the centre
CURV_DIAL_R = 0.0158
CURV_HANDLE = 0.027                        # handle length beyond the tip

# Adrianov compass: centre (a, b), rotation of the sighting ring, degrees; the strap runs along b
COMP_C = (0.048, 0.052)
COMP_R, COMP_BEZEL_R = 0.0215, 0.0228
COMP_DIAL_R = 0.0172
BEZEL_ROT = 35.0
NEEDLE_DEG = 64.0                          # where the needle points (from "up the board", counter-clockwise)
STRAP_W, STRAP_T = 0.016, 0.0018
STRAP_TOP = 0.166                           # end of the upper strap (with holes), along b
STRAP_HOLES = (0.112, 0.160, 0.0065)        # holes: from, to, step (along b)

# inventory tag on the face of the lip: centre x, centre z, size
TAG_X, TAG_Z, TAG = -0.058, 0.0175, (0.028, 0.011)

# --- in millimetres of the map sheet: x from the left edge of the sheet, y down from the top edge
# ---
MAP_W_MM = (MAP[1] - MAP[0]) * 1000.0
MAP_H_MM = (MAP[3] - MAP[2]) * 1000.0


def map_mm(a, b):
    """Board point (a, b) -> map sheet mm (x to the right, y down)."""
    return (a - MAP[0]) * 1000.0, (MAP[3] - b) * 1000.0
