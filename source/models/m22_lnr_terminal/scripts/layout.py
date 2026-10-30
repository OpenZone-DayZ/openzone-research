"""Layout of the M22 bar counter, shared by build_m22.py (geometry) and make_decals.py (images).
Decals are projected in kmats along the world axes, so the cash register and the radio stand exactly
axis-aligned, and positions and sizes are set here once. Pure Python (make_decals.py runs on the
system Python without Blender).

The register is a Soviet "Oka": a 9-row keyboard on a panel sloping toward the cashier (+y), above it
the cashier display window, at the top left the receipt window, on the right a crank; at the top rear
a customer display with a lamp. There is no datasheet, the size is estimated from photos (a key is
~15 mm at a pitch of ~19): 340 x 380 x 330 mm. The Oka display is electronic, the digits glow (seven
segments behind dark glass). The radio is a VEF-202 (1971-1980): 305 x 240 x 105 mm.
"""
import math

ZT = 1.10                                          # top of the counter

# --- register: center of the base, the keyboard faces the bartender (+y) ----------------------------
RX, RY = 0.30, 0.10
REG_W = 0.34                                        # along x
REG_YB, REG_YF = RY - 0.17, RY + 0.19               # back wall (toward the player), bottom of the keyboard
REG_FEET = 0.006                                    # rubber feet
REG_ZD, REG_ZK, REG_ZH = 0.09, 0.13, 0.28           # top of the cash drawer, bottom and top of the keyboard
KEY_Y0 = RY - 0.02                                  # top of the keyboard slope (along y)
# sloped panel: the origin is the middle of the lower edge, u along +x, v up the slope, n outward
KB_O = (RX, REG_YF, ZT + REG_ZK)
_dy, _dz = KEY_Y0 - REG_YF, REG_ZH - REG_ZK
KB_LEN = math.hypot(_dy, _dz)
KB_V = (0.0, _dy / KB_LEN, _dz / KB_LEN)
KB_N = (0.0, _dz / KB_LEN, -_dy / KB_LEN)
WELL_H, KEY_H = 0.0015, 0.0075                      # bottom of the key well above the panel, key height
KEY_W, KEY_PITCH = 0.0155, 0.0195


def kb_point(a, b, c=0.0):
    """Point on the sloped panel: a along +x from the middle, b up the slope from the lower edge, c outward."""
    return (KB_O[0] + a, KB_O[1] + KB_V[1] * b + KB_N[1] * c, KB_O[2] + KB_V[2] * b + KB_N[2] * c)


# keys: columns from the cashier's left hand (he stands at +y facing -y, so his left hand is at +x) to the right
KEY_ROWS_B0 = 0.030                                 # bottom row (digit 1), the step up is KEY_PITCH
COL_A = [0.045 - KEY_PITCH * c for c in range(7)]   # a of the centers of the seven digit columns
COL_COLOR = ["black", "black", "cream", "cream", "cream", "black", "black"]
FN_A, FN_W = COL_A[6] - KEY_PITCH - 0.004, 0.024    # function key column
FN_COLOR = ["orange", "orange", "orange", "orange", "blue", "cream", "teal", "red", "black"]   # top to bottom
FN_MARK = ["I", "II", "III", "IV", "*", "-", "x", "+", ""]
LONG_A, LONG_W = FN_A - FN_W / 2 - 0.004 - 0.007, 0.014   # the long key and two locks
LONG_B = (KEY_ROWS_B0 + KEY_PITCH * 3 - 0.008, KEY_ROWS_B0 + KEY_PITCH * 5 + 0.008)
LOCK_B = (KEY_ROWS_B0 + KEY_PITCH * 0.5, KEY_ROWS_B0 + KEY_PITCH * 7.5)


def row_b(r):
    """b of the center of row r (0 is the top, digit 9; 8 is the bottom, digit 1)."""
    return KEY_ROWS_B0 + KEY_PITCH * (8 - r)


def keys():
    """All keys: (color, a, b, width along a, width along b, sign). The two left black columns have no
    digits and no bottom row (as on the real register)."""
    out = []
    for c, col in enumerate(COL_COLOR):
        for r in range(9):
            if c < 2 and r == 8:
                continue
            out.append((col, COL_A[c], row_b(r), KEY_W, KEY_W, "" if c < 2 else str(9 - r)))
    for r, col in enumerate(FN_COLOR):
        out.append((col, FN_A, row_b(r), FN_W, KEY_W, FN_MARK[r]))
    out.append(("black", LONG_A, sum(LONG_B) / 2, LONG_W, LONG_B[1] - LONG_B[0], ""))
    return out


# key well (dark bottom, frame) and windows on the panel (a0, a1, b0, b1)
WELL = (LONG_A - LONG_W / 2 - 0.010, COL_A[0] + KEY_W / 2 + 0.010, KEY_ROWS_B0 - KEY_W / 2 - 0.009,
        row_b(0) + KEY_W / 2 + 0.009)
CASH_WIN = (-0.135, 0.035, 0.212, 0.240)            # cashier display (the same image as the customer display)
CHECK_WIN = (0.068, 0.150, 0.150, 0.236)            # receipt window: frame, glass, the roll behind it
PLATE = (0.072, 0.146, 0.030, 0.046)                # nameplate without text
# digit decal on the keys - a projection from above (x, y); its frame in the world follows the keys
_tops = [kb_point(a, b, WELL_H + KEY_H) for _, a, b, _, _, _ in keys()]
KEYS_C = ((min(p[0] for p in _tops) + max(p[0] for p in _tops)) / 2, (min(p[1] for p in _tops) + max(p[1] for p in _tops)) / 2)
KEYS_S = (max(p[0] for p in _tops) - min(p[0] for p in _tops) + 0.04, max(p[1] for p in _tops) - min(p[1] for p in _tops) + 0.03)
KEYS_RNG = (min(p[2] for p in _tops) - 0.004, max(p[2] for p in _tops) + 0.004)

# customer display: a superstructure at the top rear, the window on the -y face, a lamp beside it (ozl_lamp)
HEAD = (RX - 0.12, RX + 0.12, REG_YB, REG_YB + 0.08, ZT + REG_ZH, ZT + REG_ZH + 0.05)
DISP = (RX - 0.105, RX + 0.045, ZT + REG_ZH + 0.012, ZT + REG_ZH + 0.038)   # x0 x1 z0 z1
LAMP_C = (RX + 0.085, ZT + REG_ZH + 0.025)
DISP_FRAMES = ["0.", "4.", "45.", "450.", "450.*", "1200.*", "1200.*", "0."]   # "working": entering a sum, the total

# cash drawer (the "working" pose: slides out toward the bartender)
DRAWER_TRAVEL = 0.12

# --- radio: faces the player (-y) ------------------------------------------------------------------
QX, QY = -0.55, 0.06
Q_W, Q_H, Q_D = 0.305, 0.240, 0.105
Q_FEET = 0.004
Q_YF = QY - Q_D / 2                                 # face of the case
Q_PANEL = Q_YF - 0.003                              # face of the silver panel
SCALE_C = (QX, ZT + Q_FEET + 0.186)                 # scale window (ozl_screen)
SCALE_S = (0.264, 0.050)
SCALE_Y = Q_PANEL - 0.0005                          # the scale is on the panel, the needle and glass in front of it
GRILLE_C = (QX, ZT + Q_FEET + 0.085)                # speaker grille
GRILLE_S = (0.275, 0.125)
NEEDLE_X0 = SCALE_C[0] - SCALE_S[0] / 2 + 0.028     # needle at rest (phase 0)
NEEDLE_TRAVEL = 0.20                                # needle travel per phase 1 (m)

# --- countertop: where the mugs and the ashtray stand (stains from bottoms and burns) -------------
MUGS_TOP = [(-0.22, -0.17, 30.0, True), (-0.06, -0.22, 200.0, True), (-0.10, 0.16, 120.0, False)]
ASHTRAY = (0.66, -0.17)
TOP_C, TOP_S = (0.0, 0.01), (2.20, 0.68)            # decal of stains over the whole countertop
