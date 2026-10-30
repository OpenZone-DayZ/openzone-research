"""Layout of the M23 gunsmith's workbench, shared by build_m23.py (geometry) and make_decals.py (the
tool silhouettes on the board are drawn under the same tools, the stripes on the crates on the same
faces: decals are projected in kmats along the world axes).

On the board the hacksaw, screwdrivers, pliers and adjustable wrench are vanilla (VANILLA_BOARD,
proxies; there are no silhouettes under them because the shapes of vanilla items are unknown); the
own ones are open-end wrenches, files, punches and a cleaning rod (TOOLS, with silhouettes). The
hammer is vanilla and lies on the table; it has no silhouette on the board: the vanilla hacksaw
(0.44 m) would lie with its right end over its face.

Tools on the board and their sizes, m (a locksmith's set, estimated from hand tool catalogs):
open-end wrenches 10-22 (length 0.12..0.18, heads at 15 degrees), files (300 with a handle),
punches dia. 4..8 in a block, a cleaning rod dia. 6 x 0.32.
"""
# table (as in M05/M11/M15)
X0, X1, Y0, Y1 = -0.80, 0.80, -0.36, 0.36
ZT, ZP, SHD, CAB_W = 0.78, 1.40, 0.30, 0.42
YP = Y1 - 0.02                                               # panel face

# plywood board on the superstructure panel (facing -y); the top is under the middle shelf gusset (its bottom is at 1.22)
BOARD = (-0.72, 0.72, 0.84, 1.215)                           # x0, x1, z0, z1
BOARD_T = 0.012
Y_BOARD = YP - BOARD_T                                       # face of the plywood
Y_TOOL = Y_BOARD - 0.001                                     # back of the tool

# own tools: (kind, x, z, parameters). x, z is the hanging point (the hook); the silhouette and the part
# are built from the same numbers (shapes below).
TOOLS = [
    ("spanner", -0.665, 1.04, dict(L=0.120, W=0.018)),
    ("spanner", -0.615, 1.04, dict(L=0.135, W=0.020)),
    ("spanner", -0.560, 1.04, dict(L=0.150, W=0.022)),
    ("spanner", -0.500, 1.04, dict(L=0.165, W=0.025)),
    ("spanner", -0.435, 1.04, dict(L=0.180, W=0.028)),
    ("file", 0.245, 1.175, dict(L=0.30, W=0.020)),
    ("file", 0.300, 1.175, dict(L=0.28, W=0.016)),
    ("punches", 0.53, 1.09, dict(n=6, step=0.035)),
    ("rod", 0.53, 0.88, dict(L=0.32)),
]
PUNCH_LEN = (0.150, 0.145, 0.140, 0.135, 0.130, 0.125)
PUNCH_R = (0.004, 0.0035, 0.003, 0.0025, 0.002, 0.002)

# vanilla tools on the board (kvanilla, proxies): (item, x, z of the bounding box middle, the angle of
# the item's +Y in the board plane: 90 is up, -90 is down). Screwdrivers sit in a holder tip down, the
# wrench hangs jaws down (by the hole in its handle), the hacksaw lies with its frame along the board.
VANILLA_BOARD = [
    ("hacksaw", -0.49, 1.130, 90.0),
    ("screwdriver", -0.165, 1.068, -90.0),
    ("screwdriver", -0.120, 1.068, -90.0),
    ("screwdriver", -0.075, 1.068, -90.0),
    ("pliers", 0.035, 1.080, 90.0),
    ("wrench", 0.135, 1.075, -90.0),
]
SD_HOLDER_Z = 1.150                                          # screwdriver holder - under the handles


def shapes(kind, x, z, p):
    """Tool silhouette in the board plane: [("rect", x0, x1, z0, z1) | ("circle", x, z, r) |
    ("poly", [(x, z), ...])]. The part in build_m23.py is built from the same sizes."""
    s = []
    if kind == "spanner":
        L, W = p["L"], p["W"]
        s += [("rect", x - W * 0.3, x + W * 0.3, z - L + W, z - W * 0.4),
              ("circle", x, z - W * 0.4, W * 0.62),
              ("circle", x, z - L + W * 0.55, W * 0.72)]
    elif kind == "file":
        L, W = p["L"], p["W"]
        s += [("rect", x - 0.013, x + 0.013, z - 0.10, z),
              ("poly", [(x - W / 2, z - 0.10), (x + W / 2, z - 0.10), (x + W * 0.3, z - L), (x - W * 0.3, z - L)])]
    elif kind == "punches":
        n, st = p["n"], p["step"]
        x0 = x - st * (n - 1) / 2
        s += [("rect", x0 - 0.025, x0 + st * (n - 1) + 0.025, z - 0.012, z + 0.012)]
        for k in range(n):
            xk = x0 + st * k
            s += [("rect", xk - PUNCH_R[k] - 0.002, xk + PUNCH_R[k] + 0.002, z + 0.06 - PUNCH_LEN[k], z + 0.06)]
    elif kind == "rod":
        L = p["L"]
        s += [("rect", x - L / 2, x + L / 2, z - 0.003, z + 0.003),
              ("circle", x + L / 2 - 0.006, z, 0.009)]
    return s


# ammo crates under the table (stacked) - x0, x1, y0, y1, bottom, height
CRATES = [(-0.70, -0.18, -0.15, 0.19, 0.0, 0.17), (-0.69, -0.17, -0.14, 0.20, 0.17, 0.17)]
CRATE_LID = 0.022
# stencil stripes on the crate face (z from the crate bottom, x from the left edge): (dx0, dx1, color)
STRIPES = [(0.16, 0.20, "black"), (0.23, 0.27, "black"), (0.31, 0.35, "red")]
STRIPE_Z = (0.035, 0.125)
