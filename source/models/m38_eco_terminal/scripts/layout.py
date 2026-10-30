"""Layout of the M38 computer terminal of the Scientists - shared by build_m38.py (geometry) and
make_decals.py: the screen, keyboard, paper, log, numbered disc, counter and tag lie on the
same faces (kmats projects decals along the world axes).

Axes: X - width, Y - depth (front at -Y), Z - up. Dimensions and their sources are in the
docstring of build_m38.py.
"""

# --- Tape drive cabinet (class of the ES-5017 / IBM 3420), left -------------------------------
X0, X1 = -1.00, -0.24                                        # 0.76 wide
CXC = (X0 + X1) / 2
CY0, CY1 = -0.22, 0.40                                       # front, back (0.62 deep)
CH = 1.62                                                    # top of the body
STILE = 0.045                                                # white posts of the front frame
FRONT_T = 0.02                                               # white frame thickness (along y)
REC = 0.12                                                   # depth of the window recess
YD = CY0 + REC                                               # aluminium panel face in the recess
WIN = (X0 + STILE, X1 - STILE, 1.00, 1.57)                   # window: x0, x1, z0, z1
WIN_R = 0.016                                                # corner radius of the window frame
BAND = (0.86, 1.00)                                          # white band under the window
LOWER = (0.07, 0.86)                                         # grey-green lower door
PLINTH = 0.07
YP = CY0 + 0.006                                             # face of the band and the lower door
YG = CY0 + 0.010                                             # window glass
# Console on the roof: a dark grey box on two legs
CON = (X0 + 0.01, X1 - 0.01, CY0 - 0.02, CY0 + 0.40, CH + 0.025, 1.80)
CON_Y = CON[2]
DISC = (X0 + 0.110, 1.7225, 0.045)                          # numbered disc: x, z, radius
# Square lamp buttons (26 mm): 9 in the top row; the bottom row has 2 on the left, 1 in the
# middle, 3 on the right. Role: lamp - lit while working, blink - blinks, btn - a button
# without a lamp.
BTN = 0.026
BTN_TOP = [(X0 + 0.215 + 0.036 * i, 1.752, c, r) for i, (c, r) in
           enumerate(zip("ywwyyywwr", ("lamp", "lamp", "btn", "blink", "lamp", "btn", "blink", "btn", "btn")))]
BTN_LOW = [(X0 + 0.215, 1.700, "g", "lamp"), (X0 + 0.251, 1.700, "r", "btn"), (X0 + 0.323, 1.700, "w", "btn"),
           (X0 + 0.431, 1.700, "w", "btn"), (X0 + 0.467, 1.700, "w", "btn"), (X0 + 0.503, 1.700, "w", "btn")]
COUNTER = (X0 + 0.585, X0 + 0.645, 1.693, 1.707)             # hour counter: x0, x1, z0, z1
TAG = (X0 + 0.575, X0 + 0.715, 1.738, 1.775)                 # paper tag without text
YELLOW = (X0 + 0.030, X0 + 0.085, 1.656, 1.668)              # yellow plate, lower left (blank)
# Reels: file reel on the left (full), machine reel on the right (less tape); 10.5 in = 267 mm
REEL_R = 0.1335
REELS = ((CXC - 0.165, 1.325, 0.118), (CXC + 0.165, 1.325, 0.082))   # x, z, winding radius
HUB_R = 0.050
REEL_Y = (YD - 0.040, YD - 0.012)                            # front and rear flange (along y)
WINDOW_R = (0.064, 0.118)                                    # flange windows: from and to (radius)
HEAD = (CXC - 0.125, CXC + 0.125, WIN[2], WIN[2] + 0.10)     # head block at the window bottom
ROLL_R = 0.012                                               # guide rollers on the head block
ROLLS = ((HEAD[0] + 0.030, HEAD[3] + 0.020), (HEAD[1] - 0.030, HEAD[3] + 0.020))
PLATE = (CXC - 0.24, CXC - 0.06, 0.905, 0.955)               # blank nameplate on the white band
PLATE2 = (CXC + 0.02, CXC + 0.10, 0.910, 0.950)              # second one, dark
LOCK = (X1 - STILE - 0.06, 0.80)                             # lower door lock: x, z
GP5 = (0.12, 1.24)                                           # gas mask on the cabinet's left: y, z
HOOK_Z = 1.355                                               # hook: the mask straps go over it

# --- Operator's desk with a pedestal, right ---------------------------------------------------
DX0, DX1 = -0.22, 1.00
DY0, DY1 = -0.40, 0.40
DZ0, DZ = 0.700, 0.735                                       # bottom and top of the tabletop
TOP_R = 0.012                                                # rounding of the tabletop edges
PED = (0.53, 0.99)                                           # pedestal under the printer: x0, x1
PED_SHELF = 0.10                                             # top of the pedestal's lower shelf
SLOT = (0.25, 0.28)                                          # paper slot in the tabletop (along y)

# Terminal (class of the Robotron K 8924: 510 x 330 x 420): CRT case on a plinth
TXC, TW = 0.22, 0.48
TY0, TY1 = -0.03, 0.39
TZ0, TZ1 = DZ + 0.03, DZ + 0.34
T_FRONT = 0.10                                               # depth of the front part of the case
T_R = 0.016                                                  # case rounding
SCR_Z = TZ0 + 0.175
POCKET = (0.272, 0.207, 0.022, 0.028)                        # tube window: w, h, radius, depth
SCR_W, SCR_H, SCR_R = 0.264, 0.199, 0.019                    # visible glass, 12 in
SCR_SAG = 0.010
T_LAMP = (TXC + 0.185, TZ0 + 0.035)                          # power lamp on the chin
T_KNOBS = ((TXC + 0.125, TZ0 + 0.035), (TXC + 0.150, TZ0 + 0.035))

# Terminal keyboard (estimate: class of the K 7637, ~480 x 200), wedge-shaped
KX0, KX1 = TXC - 0.24, TXC + 0.24
KY0, KY1 = -0.375, -0.175
KZ_F, KZ_B = DZ + 0.028, DZ + 0.052
KEYS = (KX0 + 0.014, KX1 - 0.014, KY0 + 0.020, KY1 - 0.024)
KEY_GAP = 0.0018                                             # half the gap between keys
KEY_UNITS = 20.5                                             # key field width in key units
# Rows of the main block (top = far row): (row, [(start, width) in key units])
KEY_ROWS = [(0, [(i, 1) for i in range(15)]),
            (1, [(0, 1.5)] + [(1.5 + i, 1) for i in range(12)] + [(13.5, 1.5)]),
            (2, [(0, 1.75)] + [(1.75 + i, 1) for i in range(11)] + [(12.75, 2.25)]),
            (3, [(0, 2.25)] + [(2.25 + i, 1) for i in range(10)] + [(12.25, 2.75)]),
            (4, [(0, 1.5), (1.5, 1.5), (3.0, 9.0), (12.0, 1.5), (13.5, 1.5)])]
KEY_FN = [(16.0 + i * 1.1, j) for i in range(4) for j in range(5)]       # beige service block 4 x 5


def key_zs(y):
    """Height of the sloped keyboard top above point y."""
    return KZ_F + (y - KY0) / (KY1 - KY0) * (KZ_B - KZ_F)


def key_rects():
    """Keys: [(x0, x1, y0, y1, beige)] - the same ones make_decals.make_keys() draws."""
    x0, x1, y0, y1 = KEYS
    u = (x1 - x0 - KEY_GAP) / KEY_UNITS
    kh = (y1 - y0 - KEY_GAP) / 5.0
    out = []

    def add(xu, w, r, beige):
        out.append((x0 + xu * u + KEY_GAP, x0 + (xu + w) * u - KEY_GAP, y1 - (r + 1) * kh + KEY_GAP,
                    y1 - r * kh - KEY_GAP, beige))
    for r, ks in KEY_ROWS:
        for xu, w in ks:
            add(xu, w, r, False)
    for xu, r in KEY_FN:
        add(xu, 1, r, True)
    return out


# 80-column dot-matrix printer (class of the Epson FX: 414 x 350 x 168)
PX0, PX1 = 0.555, 0.969
PXC = (PX0 + PX1) / 2
PY0, PY1 = -0.17, 0.18
PZ1 = DZ + 0.168
P_REAR = (0.088, DZ + 0.150)                                 # front edge of the rear block, its top
P_FRONT = (-0.110, DZ + 0.096)                               # rear edge of the front block, its top
P_BAY = (PX0 + 0.026, PX1 - 0.026, -0.104, 0.086, DZ + 0.045)  # mechanism bay: x0 x1 y0 y1 z0
PLATEN = (0.036, DZ + 0.098, 0.021)                          # platen: y, axis z, radius
P_HEAD_Y = -0.010                                            # print head in front of the platen
HEAD_TRAVEL = 0.203                                          # 80 chars at 1/10 in - head travel
P_LAMPS = ((PX1 - 0.110, "g", "lamp"), (PX1 - 0.085, "a", "blink"), (PX1 - 0.060, "a", "off"))
P_LAMP_Z = DZ + 0.060
# Fan-fold paper 9.5 in (241 mm with the perforation), sheet 11 in (279 mm)
PAPER_W = 0.241
STACK = (PXC - PAPER_W / 2, PXC + PAPER_W / 2, -0.10, 0.179, PED_SHELF, PED_SHELF + 0.12)
# Output: the web rises from the slot behind the cover, bends back and hangs over the table edge
P_EXIT = (0.066, 0.086)                                      # paper exit slot behind the cover
OUT_PATH = ((0.076, DZ + 0.110), (0.076, PZ1 + 0.012), (0.075, 0.955), (0.085, 0.995), (0.120, 1.018),
            (0.180, 1.024), (0.240, 1.004), (0.290, 0.955), (0.326, 0.885), (0.346, 0.805), (0.356, DZ + 0.004),
            (0.395, DZ + 0.004), (0.408, DZ - 0.030), (0.413, 0.46))
PRINT = (PXC - PAPER_W / 2, PXC + PAPER_W / 2, PZ1, 1.03)    # printed part visible from the front
# Input: from the top of the stack up through the tabletop slot, over the printer back into
# the gap behind the tractors
IN_PATH = ((0.170, STACK[5]), (0.200, 0.30), (0.245, 0.50), (0.265, DZ0 - 0.02), (0.265, DZ + 0.010),
           (0.258, DZ + 0.090), (0.236, DZ + 0.150), (0.200, DZ + 0.171), (0.160, DZ + 0.169), (0.141, DZ + 0.160),
           (0.133, DZ + 0.147))

# Media receiving log - open, right in front of the printer; page 150 x 205
LOG = (0.675, -0.282)                                        # center x, y
LOG_PAGE = (0.150, 0.205)
LOG_H = (0.004, 0.011)                                       # page block thickness: edge, spine
