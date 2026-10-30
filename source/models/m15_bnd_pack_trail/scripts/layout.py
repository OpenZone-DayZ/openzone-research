"""Where things lie on the M15 spotter's table - shared by build_m15.py (geometry) and make_decals.py
(decals are turned the way the papers lie, and the marker marks on the map are under the pins: kmats
projects decals along the world axes).

Sizes, m: A4 sheet 210 x 297, A5 148 x 210, A3 297 x 420; photo 9 x 13 cm; Palm III PDA (1998)
119 x 81 x 18; Psion Series 5 (1997) closed 170 x 90 x 23; pager ~62 x 45 x 18 (as in M13); flash drive
~60 x 20 x 9 with a cap; "Elektronika-302" tape recorder 315 x 225 x 90.

Modules are in their places: slot 1 (M78, PDA reader) on the table at the left, slot 2 (M79, radio
scanner) on the shelf at the right, slot 3 (M80, tablet with maps) on the table in the middle in front of
the map. The module pads are free of papers.
"""
# table (as M05/M11: base B1)
X0, X1, Y0, Y1 = -0.80, 0.80, -0.36, 0.36
ZT, ZP, SHD, CAB_W = 0.78, 1.40, 0.30, 0.42
YP = Y1 - 0.02                                               # face of the back panel
YS = Y1 - SHD                                                # front of the shelf

# modules: the module model origin (middle of the bottom) is the ozl_toolN proxy point; their extents (m, from
# the origin) are from the MLOD build/model-root: M78 0.18 x 0.15, M79 x +-0.084, y -0.120..+0.166, M80 0.206 x 0.216
MODS = [(-0.43, -0.06, ZT), (0.58, YS + 0.125, ZP + 0.003), (-0.08, 0.205, ZT)]
MOD_OBJ = [("m78_pda_reader", "ozr_pda_reader"), ("m79_radio_scanner", "ozr_radio_scanner"),
           ("m80_map_board", "ozr_map_board")]
MOD_BOX = [((-0.090, -0.075), (0.090, 0.075)), ((-0.084, -0.120), (0.084, 0.166)), ((-0.103, -0.109), (0.103, 0.107))]
MAT2 = (0.497, 0.668, 0.068, 0.352, 0.003)                   # mat under M79: x0 x1 y0 y1 thickness

# fibreboard on the back panel and the map on it (vertical, facing -y); the board top is under the middle
# gusset of the shelf (its bottom is at 1.22)
CORK = (-0.66, 0.52, 0.83, 1.215)                            # x0, x1, z0, z1
CORK_T = 0.010
Y_CORK = YP - CORK_T                                         # face of the board
MAP = (-0.50, 0.34, 0.855, 1.195)                            # x0, x1, z0, z1
Y_MAP = Y_CORK - 0.0006
# photos and notes on the board around the map: name, x0, x1, z0, z1
PINNED = [
    ("photo0", 0.375, 0.505, 1.095, 1.185),
    ("photo1", 0.380, 0.470, 0.880, 1.010),
    ("note0", -0.645, -0.520, 1.040, 1.190),
    ("note1", -0.635, -0.525, 0.850, 1.000),
]
Y_PIN = Y_CORK - 0.0005
# pins: (x, z, colour); marker marks on the map under them
PINS = [
    (-0.40, 1.13, "red"), (-0.27, 0.99, "red"), (-0.12, 1.16, "yellow"), (-0.03, 0.93, "red"),
    (0.10, 1.08, "blue"), (0.22, 0.90, "red"), (0.25, 1.17, "yellow"), (-0.33, 0.89, "blue"),
    # on photos and notes
    (0.44, 1.17, "red"), (0.425, 0.995, "red"), (-0.582, 1.175, "yellow"), (-0.58, 0.985, "red"),
]
# red threads between pins (numbers in PINS)
STRINGS = [(0, 1), (1, 3), (3, 5), (5, 4), (4, 2), (2, 0), (4, 8), (5, 9), (0, 10), (7, 11), (1, 7), (6, 8)]

# papers on the table: name, centre (x, y), rotation about z, (w, h), height of the bottom above the board,
# picture, fold (which corner of the sheet is raised: 0..3 counter-clockwise from the lower left, lift, m) or None
PAPERS = [
    ("paper1", (-0.670, -0.100), -8.0, (0.210, 0.297), 0.0000, "table", (0, 0.007)),
    ("paper0", (-0.420, -0.252), 86.0, (0.148, 0.210), 0.0000, "lines", (1, 0.005)),
    ("paper2", (-0.632, 0.140), 22.0, (0.148, 0.210), 0.0008, "lines", None),
    ("sketch", (-0.060, -0.150), 3.0, (0.420, 0.297), 0.0000, "sketch", None),
    ("photo2", (-0.235, -0.272), -8.0, (0.090, 0.130), 0.0008, "photo", None),
    ("paper5", (-0.312, 0.212), 31.0, (0.148, 0.210), 0.0000, "lines", (2, 0.004)),
    ("paper3", (0.360, 0.160), 22.0, (0.210, 0.297), 0.0000, "lines", (1, 0.006)),
    ("paper4", (0.170, 0.170), -9.0, (0.210, 0.297), 0.0008, "table", None),
    ("paper6", (0.420, -0.270), -4.0, (0.210, 0.148), 0.0000, "lines", (0, 0.005)),
    ("photo3", (0.100, 0.045), 17.0, (0.130, 0.090), 0.0016, "photo", None),
]
PAPER_T = 0.0006

# bolt markers on the sketch: head centre (x, y), shaft direction (degrees), with a rag
BOLTS = [((-0.165, -0.185), 30.0, True), ((0.020, -0.075), -60.0, True), ((0.095, -0.225), 160.0, False),
         ((-0.090, -0.262), 95.0, True), ((-0.200, -0.055), -15.0, False),
         # a handful of spares by the ashtray
         ((0.600, -0.030), 120.0, False), ((0.632, -0.065), 75.0, True)]

# PDAs: the Palm lies face down with the battery cover removed; the Psion
PALM = (0.119, 0.081, 0.018)
PDA_DOWN = ((-0.660, -0.130), -12.0)
PSION = ((-0.670, 0.250), 8.0, (0.170, 0.090, 0.023))

# flash drives: centre, rotation (the second one has its cap off)
FLASH = [((-0.560, 0.035), 40.0), ((0.215, -0.075), -25.0), ((0.140, -0.285), 70.0)]

# pager, butterfly knife, keys, ashtray, mug, carton of cigarettes
PAGER = ((0.300, -0.050), -18.0)
KNIFE = ((0.555, -0.282), 24.0)
KEYS = ((0.700, -0.115), 0.0)
ASHTRAY = (0.470, -0.130)
MUG = (0.660, 0.125)
CARTON = ((0.470, 0.262), 3.0, (0.280, 0.090, 0.048))
# "Chernomorka" packs 88 x 55 x 22 (the first is open), notebook 165 x 205 x 10, deck of cards 58 x 88 x 16
PACKS = [((0.300, 0.060), 62.0), ((0.395, 0.100), -30.0)]
NOTEBOOK = ((-0.450, 0.200), -6.0, (0.165, 0.205, 0.010))
DECK = ((0.215, 0.040), 25.0, (0.058, 0.088, 0.016))

# pager screen (in local axes from its centre): centre (dx, dy), size (w, h)
PAGER_SCR = ((-0.004, 0.004), (0.036, 0.016))

# shelf: map rolls (x of the middle, y, radius, length), box (x0 x1 y0 y1 h), tape recorder (middle of the
# bottom), the slot 2 mat - MAT2
ROLLS = ((-0.55, YS + 0.050, 0.022, 0.42), (-0.53, YS + 0.098, 0.020, 0.38), (-0.54, YS + 0.074, 0.019, 0.34))
TIN = (-0.78, -0.53, YS + 0.12, YS + 0.29, 0.09)
REC = (0.140, YS + 0.135, ZP)
# tape recorder in its own axes (middle of the bottom, face toward -y): body, slanted strip, upper deck
REC_W, REC_D, REC_H = 0.315, 0.212, 0.090
REC_STRIP = (-0.106, -0.056, 0.065, 0.088)                   # y0 y1 z0 z1 of the slanted strip
REC_GRILLE = (-0.150, -0.008, -0.050, 0.098)                 # speaker grille x0 x1 y0 y1
REC_LID = (0.008, 0.150, -0.050, 0.098)                      # cassette compartment lid
REC_WIN = (0.026, 0.134, -0.030, 0.046)                      # lid window (and the compartment under it)
CASS = (0.080, 0.008, 0.1004, 0.0638, 0.012)                 # cassette: centre x y, sizes
VU = (-0.030, 0.034, 0.013)                                  # strip indicator: x, width, slope height
KNOBS = (-0.122, -0.080)                                     # volume and tone knobs
KEYS_REC = (0.030, 0.150, 6)                                 # keys: x0, x1, how many


def local(center, deg, dx, dy):
    """World x, y of the point (dx, dy) given in the axes of an item turned by deg about z."""
    import math
    a = math.radians(deg)
    return (center[0] + dx * math.cos(a) - dy * math.sin(a), center[1] + dx * math.sin(a) + dy * math.cos(a))
