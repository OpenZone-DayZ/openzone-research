"""Layout of the M31 Freedom computer - shared by build_m31.py (geometry) and make_decals.py:
the decals, screen and keyboard lie on the same faces (kmats projects decals along the world
axes).

Axes: X - width, Y - depth (front at -Y), Z - up. Dimensions and their sources are in the
docstring of build_m31.py.
"""

# Cases of the Pelican 1620 class (630 x 492 x 352 mm) stand on their end: along x the
# thickness is 0.352 (the lid faces the table middle), along y 0.492, height 0.630.
CASE = (0.352, 0.492, 0.630)
CASES = (-0.41, 0.41)                                        # x of the centers
CASE_Y = 0.0
CY0, CY1 = CASE_Y - CASE[1] / 2, CASE_Y + CASE[1] / 2
SEAM_K = 0.72                                                # seam: thickness fraction from outside
CASE_R = 0.034                                               # edge radius along thickness (y-z)
CASE_END_R = (0.026, 0.018)                                  # rounding of base bottom and lid top
RIM = (0.005, 0.011)                                         # seam rim: protrusion, half width
WHEEL = (0.040, 0.026)                                       # rear bottom wheels: radius, width


def case_x(i):
    """x0, x1 of case i."""
    return CASES[i] - CASE[0] / 2, CASES[i] + CASE[0] / 2


def seam_x(i):
    """x of the lid seam: the lid faces the table middle."""
    x0, x1 = case_x(i)
    return x0 + SEAM_K * CASE[0] if i == 0 else x1 - SEAM_K * CASE[0]


def case_out(i):
    """x of the outer side (the base bottom) and the outward direction."""
    x0, x1 = case_x(i)
    return (x0, -1) if i == 0 else (x1, 1)


LATCH_Z = (0.164, 0.466)                                     # seam latches (as pelican() in M27)
HANDLE_Z = 0.315                                             # handle between them, folded

# Tabletop - plywood 1220 x 610 x 18 (a quarter of a 2440 x 1220 sheet), slightly rotated
PX0, PX1, PY0, PY1 = -0.61, 0.61, -0.305, 0.305
PZ0 = CASE[2]
DZ = PZ0 + 0.018                                             # top of the tabletop
PLANK_DEG = 1.5

# 15 in CRT monitor: 360 x 362 x 387 mm with the stand; the bezel face is at y = MY0
MX, MY0 = -0.13, -0.085
MW, MD = 0.360, 0.387
MZ0 = DZ + 0.045                                             # case bottom above the swivel stand
MZ1 = DZ + 0.362
M_FRONT = 0.11                                               # depth of the front part (bezel)
M_R = 0.014                                                  # rounding of the front part
M_BACK = (0.11, MZ0 + 0.035, MZ1 - 0.08)                     # back wall: half-width, bottom, top
# Tube: visible glass 285 x 215 (image 250 x 187 - Sun 15 in), bulge 14 mm
SCR_W, SCR_H, SCR_Z = 0.285, 0.215, MZ0 + 0.172
SCR_R = 0.016                                                # glass corner rounding
SCR_SAG = 0.014                                              # glass center bulges past the edge
POCKET = (SCR_W + 0.014, SCR_H + 0.014, SCR_R + 0.006, 0.026)  # bezel window: w, h, radius, depth
M_LED = (MX + 0.150, MZ0 + 0.026)                            # power LED on the chin
M_STAND_Y = MY0 + 0.17                                       # swivel stand axis

# Speakers (estimate from photos and the Labtec LCS-1030, 9.5 in tall) - 95 x 140 x 235,
# turned toward the player
SPK = (0.095, 0.140, 0.235)
SPEAKERS = ((-0.385, 0.03, -12.0), (0.105, 0.03, 10.0))      # center x, y, rotation in degrees

# Mini-tower case of the 90s: 203 x 406 x 406 (Dell Dimension XPS P90, 1995)
TX0, TX1 = 0.20, 0.403
TXC = (TX0 + TX1) / 2
TY0, TY1 = -0.10, 0.306
TZ1 = DZ + 0.406
T_BEZEL = 0.024                                              # depth of the plastic front panel
BAY_X = (TX0 + 0.028, TX0 + 0.176)                           # 5.25 in bays - 148 mm
BAYS = (TZ1 - 0.060, TZ1 - 0.018, TZ1 - 0.106, TZ1 - 0.064)  # CD drive on top, a blank below it
FDD = (TX0 + 0.050, TX0 + 0.152, TZ1 - 0.150, TZ1 - 0.124)   # 3.5 in floppy drive
T_LEDS = ((TX0 + 0.040, DZ + 0.175, "g"), (TX0 + 0.062, DZ + 0.175, "a"))
T_POWER = (TX0 + 0.155, DZ + 0.175)
FAN = (TXC + 0.035, TZ1 - 0.068, 0.038)                      # PSU fan on the back: x, z, radius

# Radio of the AN/PRC-77 class: 273 x 273 x 100 mm, panel up, edge toward the player
RX0, RX1 = -0.592, -0.492
RY0, RY1 = 0.012, 0.285
RZ1 = DZ + 0.273
R_BAT = DZ + 0.093                                           # top of the battery box
ANT = (RX0 + 0.022, RY1 - 0.030)                             # antenna socket
ANT_BASE = 0.075                                             # spring base AB-591 above the panel
# AT-892 antenna (3 ft tape) bent in an arc sideways over the speaker: (dx, dy, z) of the
# points from the top of the base, top at ~1.40
ANT_PATH = ((0.0, 0.0, 0.0), (0.003, 0.0, 0.10), (0.012, 0.004, 0.24), (0.045, 0.008, 0.34),
            (0.11, 0.012, 0.385), (0.19, 0.016, 0.37), (0.26, 0.02, 0.31))
R_LAMP = (RX0 + 0.075, RY0 + 0.040)                          # lamp on the panel
R_KNOBS = ((RX0 + 0.050, RY0 + 0.105, 0.019), (RX0 + 0.050, RY0 + 0.175, 0.019),   # freq: MHz, kHz
           (RX0 + 0.068, RY0 + 0.045, 0.010), (RX0 + 0.032, RY0 + 0.235, 0.011))   # mode, volume
R_AUDIO = ((RX0 + 0.030, RY0 + 0.024), (RX0 + 0.030, RY0 + 0.058))                  # headset sockets

# Keyboard of the IBM Model M class (New Model M: 455 x 180 x 50), wedge-shaped
KX0, KX1 = MX - 0.2275, MX + 0.2275
KY0, KY1 = -0.292, -0.112
KZ_F, KZ_B = DZ + 0.026, DZ + 0.046                          # top at the front, at the back
KEYS = (KX0 + 0.012, KX1 - 0.012, KY0 + 0.016, KY1 - 0.022)  # key field on top
KEY_GAP = 0.0011                                             # half the gap between keys
K_LEDS = [(KEYS[1] - 0.075 + 0.019 * i, KY1 - 0.012) for i in range(3)]   # Num/Caps/Scroll over numpad


def key_zs(y):
    """Height of the sloped keyboard top above point y."""
    return KZ_F + (y - KY0) / (KY1 - KY0) * (KZ_B - KZ_F)


def key_rects():
    """Model M keys: [(x0, x1, y0, y1, grey)] - the main block (a row of F-keys and five rows), the
    arrows and the block above them, the numpad; shared by make_decals.make_keys() and
    build_m31.py. The field is 22.5 keys wide and 6.5 rows high (there is a gap between the
    F-keys and the number row).
    """
    x0, x1, y0, y1 = KEYS
    u = (x1 - x0 - KEY_GAP) / 22.5
    kh = (y1 - y0 - KEY_GAP) / 6.5
    out = []

    def key(xu, r, w=1.0, h=1.0, grey=1):
        out.append((x0 + xu * u + KEY_GAP, x0 + (xu + w) * u - KEY_GAP, y1 - (r + h) * kh + KEY_GAP,
                    y1 - r * kh - KEY_GAP, bool(grey)))
    rows = [(0, [(0, 1, 1)] + [(k, 1, 1) for k in (2, 3, 4, 5, 6.5, 7.5, 8.5, 9.5, 11, 12, 13, 14)]),
            (1.5, [(i, 1, 0) for i in range(13)] + [(13, 2, 1)]),
            (2.5, [(0, 1.5, 1)] + [(1.5 + i, 1, 0) for i in range(12)] + [(13.5, 1.5, 0)]),
            (3.5, [(0, 1.75, 1)] + [(1.75 + i, 1, 0) for i in range(11)] + [(12.75, 2.25, 1)]),
            (4.5, [(0, 2.25, 1)] + [(2.25 + i, 1, 0) for i in range(10)] + [(12.25, 2.75, 1)]),
            (5.5, [(0, 1.5, 1), (2.5, 1.5, 1), (4, 7, 0), (11, 1.5, 1), (13.5, 1.5, 1)])]
    for r, ks in rows:
        for xu, w, grey in ks:
            key(xu, r, w, 1, grey)
    for i in range(3):                                          # block above arrows, arrows
        key(15.25 + i, 0)
        for j in range(2):
            key(15.25 + i, 1.5 + j)
        key(15.25 + i, 5.5)
    key(16.25, 4.5)
    for i in range(4):                                          # numpad
        for j in range(4):
            if i == 3 and j == 2:
                continue
            if i == 3 and j == 3:
                key(18.5 + i, 4.5, 1, 2, 1)
                continue
            key(18.5 + i, 1.5 + j, 1, 2 if i == 3 and j == 1 else 1, i == 3 or j == 0)
    key(18.5, 5.5, 2, 1, 0)
    key(20.5, 5.5, 1, 1, 0)
    return out


# Mouse pad and mouse, mug, floppies, radio handset
PAD = (0.165, 0.395, -0.300, -0.115)
MOUSE = (0.29, -0.205, -8.0)                                 # x, y, rotation
MUG = (0.505, -0.175, 0.041, 0.095)                          # x, y, radius, height
FLOPPY = (-0.42, -0.10)
HANDSET = (-0.48, -0.215, 14.0)

# Power strip on the floor between the cases, at the back (center, rotation)
STRIP = (0.02, 0.17, -14.0)

# Faces for decals
CASE_FRONT = [None, None]                                    # x0, x1, z0, z1 on the face y = CY0 (base)
for _i in (0, 1):
    _x0, _x1 = case_x(_i)
    _s = seam_x(_i)
    CASE_FRONT[_i] = ((_x0 + 0.012, _s - 0.012) if _i == 0 else (_s + 0.012, _x1 - 0.012)) + (0.020, CASE[2] - 0.020)
CASE_SIDE = (CY0 + 0.015, CY1 - 0.015, 0.020, CASE[2] - 0.025)  # outer sides: y0, y1, z0, z1
TOWER_SIDE = (TY0 + 0.012, TY1 - 0.012, DZ + 0.015, TZ1 - 0.012)  # right side, face x = TX1
TOWER_FRONT = (TX0 + 0.010, TX1 - 0.010, DZ + 0.018, DZ + 0.150)  # lower front, below the buttons
MON_TOP = (MX - MW / 2 + 0.012, MX + MW / 2 - 0.012, MY0 + 0.012, MY0 + M_FRONT - 0.008)  # bezel top
RADIO_SIDE = (RY0 + 0.012, RY1 - 0.012, DZ + 0.012, RZ1 - 0.015)  # radio left side, face x = RX0
