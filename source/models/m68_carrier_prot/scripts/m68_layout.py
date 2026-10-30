"""M68 - dimensions shared by build_m68.py (Blender) and make_decals.py (system Python + Pillow): an open
officer's map case in two leaves, the flap thrown back. No dependencies - both import it.

Axes (as in the generator): X is across the case (the leaf with the window at -X, the body at +X), Y is
along it (the top with the flap at +Y, the bottom with the tab at -Y), Z is up. The origin is the middle
between the leaves on the ground. Everything lies on the ground, no tilt.

The make_decals.py images are laid on the model by X, Y coordinates (metres): leather_print.png - the
whole layout from above (stitching, a stamp on the suede), map.png - the map under the celluloid of
the window, protocol.png - the protocol form in its own coordinates (rotation and shift - PROT_*),
sheet2.png - the corner of the second sheet.
"""
import math

# --- leaf and body: a 22 x 28 cm case (a shop item; 22 x 32 overall with the flap), leather sheet
#     ~1.5 mm; corners rounded r 10 mm (by eye from a photo) ---------------------------------------
W, HL = 0.220, 0.280
R_C = 0.010
R_MIN = 0.0035                    # at the inner rings the corner does not collapse to a point

# the body lies on its back: the front wall (with the pencil holder) faces up, the sides are ~3 cm
BX0, BX1 = 0.012, 0.232
BXC = (BX0 + BX1) / 2
BY0, BY1 = -HL / 2, HL / 2
# body profile: (inset from the outline, z) from bottom to top: the back on the ground, a rounded bottom,
# a convex side, the front wall edge as a roll (an inset below zero means the roll sticks out past the
# side by 0.4 mm and shows as a seam line in light), the front wall pillow. The rings have no
# intermediate points on straight sides, corners take 30 degrees each
BODY_RINGS = [(0.0055, 0.0), (0.0010, 0.0050), (0.0, 0.0150), (-0.0004, 0.0265), (0.0028, 0.0316),
              (0.042, 0.0342)]
BODY_KANT = 3                     # edge ring: the front wall starts from it (body_z_top)
BODY_RINGS_L1 = [(0.0055, 0.0), (0.0, 0.013), (0.0026, 0.0300), (0.040, 0.0340)]

# leaf with the window: the cover, opened by 180 degrees, lies on the ground; ~5 mm thick (two leathers,
# celluloid, paper); the window frame is 15 mm, the window is slightly below the frame
LX0, LX1 = -0.228, -0.008
LXC = (LX0 + LX1) / 2
FRAME = 0.0150
WIN_IN = 0.0162                   # inset of the window edge
LEAF_RINGS = [(0.003, 0.0), (0.0, 0.0024), (0.0016, 0.0049), (FRAME, 0.0054), (WIN_IN, 0.0041)]
LEAF_RINGS_L1 = [(0.003, 0.0), (0.0016, 0.0049), (FRAME, 0.0054), (WIN_IN, 0.0041)]
Z_WIN = 0.0041
WIN_X0, WIN_X1 = LX0 + WIN_IN, LX1 - WIN_IN
WIN_Y0, WIN_Y1 = BY0 + WIN_IN, BY1 - WIN_IN
WIN_C = ((WIN_X0 + WIN_X1) / 2, 0.0)
WIN_W, WIN_H = WIN_X1 - WIN_X0, WIN_Y1 - WIN_Y0

# the fold of the cover: from the edge of the body front wall (on the left) down to the leaf on the
# ground; the path (x, z) lists control points through which the generator leads a smooth curve. The end
# is on the front wall 7.5 mm from the edge, half its thickness sunk into the leather; the curve passes
# the edge roll with a ~1 mm gap
BEND = [(-0.016, 0.0027), (-0.0058, 0.0035), (-0.0002, 0.0072), (0.0031, 0.0140), (0.0060, 0.0212),
        (0.0090, 0.0266), (0.0124, 0.0308), (0.0195, 0.0322)]
BEND_L1 = [(-0.016, 0.0027), (-0.0030, 0.0045), (0.0040, 0.0170), (0.0195, 0.0310)]
BEND_Y = 0.128
BEND_T = 0.0024

# --- flap: thrown back up and lying on the ground suede side up (closed, the flap covers ~0.38 of the
#     height, 10.5 cm; open, its underside is light suede); the root is under the back -------------
FL_X0, FL_X1 = BX0 + 0.002, BX1 - 0.002
FL_Y0, FL_Y1 = BY1 - 0.012, BY1 + 0.105
FL_R = 0.022                      # rounding of the free corners
FL_T = 0.0026
FL_CURL = 0.0022                  # the free edge is curled up slightly
FL_YCUT = (BY1 + 0.004, BY1 + 0.062, BY1 + 0.088)


def flap_z(y):
    t = max(0.0, (y - (BY1 + 0.062)) / (FL_Y1 - (BY1 + 0.062)))
    return FL_T / 2 + FL_CURL * t * t


# lock tongue (nickel) under the flap at the free edge, sticking out past the edge by 12 mm
LOCK_X = BXC
LOCK = dict(y0=FL_Y1 - 0.016, y1=FL_Y1 + 0.012, w0=0.013, w1=0.0085, t=0.0011)
RIVETS = [(LOCK_X - 0.0085, FL_Y1 - 0.009), (LOCK_X + 0.0085, FL_Y1 - 0.009)]

# --- tab with a turn-lock: from under the bottom of the body, lies on the ground (at the bottom of the
#     body in one reference photo, bottom right in the other); 26 x 58 mm, rounded end -------------
TAB_X = BX0 + 0.150
TAB_W = 0.026
TAB_Y0, TAB_Y1 = BY0 + 0.010, BY0 - 0.050
TAB_T = 0.0028
TURN = dict(x=TAB_X, y=TAB_Y1 + 0.017, rx=0.0105, ry=0.0075, t=0.0012, knob_r=0.0042, knob_h=0.0032)

# --- pencil holder on the front wall of the body: two strips with loops (on the right in the reference) ---
PEN_XS = (BX0 + 0.130, BX0 + 0.146, BX0 + 0.162, BX0 + 0.178)
BAND_YS = (0.064, -0.036)
BAND_W = 0.014
BAND_T = 0.0016
BAND_X0, BAND_X1 = BX0 + 0.118, BX0 + 0.191
PEN_R = 0.0040                    # hexagon of 7 mm across flats: radius to the vertices 4 mm

# pencils: slot x, bottom and top along y, kind; the top is sharpened (both ends for the two-colour one)
PENCILS = [
    dict(slot=0, y0=-0.084, y1=0.090, kind="redblue"),      # red-blue, sharpened at both ends
    dict(slot=1, y0=-0.078, y1=0.104, kind="green"),        # a plain "Konstruktor" pencil, almost new
    dict(slot=2, y0=-0.070, y1=0.086, kind="pen"),          # ballpoint pen with a cap
    dict(slot=3, y0=-0.064, y1=0.044, kind="black"),        # a stub, held in the lower loop
]
SHARP = 0.016                     # length of the sharpening (wood)
LEAD = 0.0035                     # lead

# patch pocket on the left of the front wall, with the edge of a folded map sticking out
POCKET = dict(x0=BX0 + 0.020, x1=BX0 + 0.104, y0=-0.122, y1=-0.006, t=0.0018)
POCKET_PAPER = dict(x0=BX0 + 0.030, x1=BX0 + 0.092, y0=-0.040, y1=0.0005, t=0.0006)

# --- shoulder strap: attached at the right near the top, the free end with the buckle lies near the bottom ---
RING = dict(x=BX1 + 0.014, y=BY1 - 0.024, rx=0.0085, ry=0.0115, r=0.0016)
STRAP_W, STRAP_T = 0.020, 0.0026
STRAP = [(BX1 + 0.016, BY1 - 0.034), (BX1 + 0.019, BY1 - 0.070), (BX1 + 0.020, 0.030), (BX1 + 0.019, -0.040),
         (BX1 + 0.016, -0.095), (BX1 + 0.008, -0.132), (BX1 - 0.008, -0.158), (BX1 - 0.026, -0.172)]
STRAP_L1 = [STRAP[0], STRAP[2], STRAP[4], STRAP[6], STRAP[7]]
BUCKLE = dict(w=0.026, h=0.018, r=0.0015)                  # buckle frame at the end of the strap

# --- elastic strap across the window (a vertical strap with a hook at the bottom in the reference) ---
WSTRAP_X = WIN_X0 + 0.012
WSTRAP_W, WSTRAP_T = 0.011, 0.0013
WSTRAP_Y0, WSTRAP_Y1 = BY0 + 0.006, BY1 - 0.006
# the hook is on the frame where the strap still lies on the leather (at the window edge it would hang over
# the celluloid)
HOOK = dict(x=WSTRAP_X, y=BY0 + 0.0105, w=0.016, h=0.010, r=0.0012)

# --- papers ---------------------------------------------------------------------------------------
# protocol: an A5 form (148 x 210) under the celluloid of the window: shift from the window centre and
# rotation (degrees)
PROT_W, PROT_H = 0.148, 0.210
PROT_C = (WIN_C[0] + 0.004, WIN_C[1] + 0.008)
PROT_ROT = -2.0
# second sheet (a blue carbon copy) under the protocol, its corner is visible at the top left
COPY_W, COPY_H = 0.148, 0.210
COPY_C = (WIN_C[0] - 0.012, WIN_C[1] + 0.016)
COPY_ROT = 4.5
# a sheet corner from under the flap: comes out of the body mouth and lies on the flap
S2_CORNER = (BX0 + 0.080, BY1 + 0.036)
S2_A = 52.0                       # direction of the first edge from the corner (degrees from -X, clockwise)
S2_YIN = BY1 - 0.012              # the edges go into the body up to this y
S2_T = 0.0003
S2_YCUT = (BY1 - 0.002, BY1 + 0.004, BY1 + 0.010)


def s2_z(y):
    """Centre line of the sheet: in the mouth (z ~ 1.6 cm) -> onto the flap."""
    zin, zout = 0.0160, FL_T + S2_T / 2 + 0.0002
    t = min(1.0, max(0.0, (y - (BY1 - 0.002)) / 0.012))
    return zin + (zout - zin) * (3 * t * t - 2 * t * t * t)


def s2_outline():
    cx, cy = S2_CORNER
    a = math.radians(S2_A)
    d1 = (-math.cos(a), -math.sin(a))           # the first edge goes left and down
    d2 = (math.sin(a), -math.cos(a))            # the second goes right and down (at a right angle)
    l1 = (cy - S2_YIN) / -d1[1]
    l2 = (cy - S2_YIN) / -d2[1]
    return [(cx + d1[0] * l1, S2_YIN), (cx + d2[0] * l2, S2_YIN), (cx, cy)]


# --- images ---------------------------------------------------------------------------------------
# leather_print.png: the whole layout from above
PRINT_C = (0.016, 0.034)
PRINT_S = (0.500, 0.500)
# map.png: the window with a margin
MAP_C = WIN_C
MAP_S = (WIN_W + 0.006, WIN_H + 0.006)
# sheet2.png: a sheet corner from under the flap
S2_C = (BX0 + 0.082, BY1 + 0.010)
S2_S = (0.120, 0.060)
STAMP = dict(x=BX0 + 0.160, y=BY1 + 0.074, w=0.046, h=0.020, rot=-6.0)


# --- outlines -------------------------------------------------------------------------------------
def rrect(cx, cy, w, h, r, nc=2, nx=2, ny=3):
    """Rounded rectangle, counter-clockwise: 4 * (nc + 1) arc points and intermediate points on the sides
    (nx on the top and bottom, ny on the lateral ones). The number and order of points do not depend on
    the inset, so rings are stitched with quads."""
    r = max(r, R_MIN)
    hw, hh = w / 2, h / 2
    corners = [(cx + hw - r, cy - hh + r, -90.0), (cx + hw - r, cy + hh - r, 0.0),
               (cx - hw + r, cy + hh - r, 90.0), (cx - hw + r, cy - hh + r, 180.0)]
    pts = []
    for i, (ccx, ccy, a0) in enumerate(corners):
        for k in range(nc + 1):
            a = math.radians(a0 + 90.0 * k / nc)
            pts.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
        nx_, ny_, a1 = corners[(i + 1) % 4]
        nxt = (nx_ + r * math.cos(math.radians(a1)), ny_ + r * math.sin(math.radians(a1)))
        end = pts[-1]
        n = ny if i in (0, 2) else nx
        for k in range(1, n + 1):
            t = k / (n + 1)
            pts.append((end[0] + (nxt[0] - end[0]) * t, end[1] + (nxt[1] - end[1]) * t))
    return pts


def ring(cx, cy, w, h, inset, lod=0):
    """Profile ring of the leaf or body. A corner takes 3 segments of 30 degrees (below the 40 degree
    threshold for sharp edges in kexport/krender, so the corner reads smooth in shadow rather than
    faceted), straight sides have no intermediate points (they gave no shape); the middle LOD takes 2
    segments."""
    nc, nx, ny = (3, 0, 0) if lod == 0 else (2, 0, 0)
    return rrect(cx, cy, w - 2 * inset, h - 2 * inset, R_C - inset, nc, nx, ny)


def profile_z(rings, d):
    """Profile height [(inset, z)] at inset d (linear between the rings)."""
    if d <= rings[0][0]:
        return rings[0][1]
    for (d0, z0), (d1, z1) in zip(rings, rings[1:]):
        if d <= d1:
            return z0 + (z1 - z0) * (d - d0) / (d1 - d0)
    return rings[-1][1]


def body_z_top(x, y):
    """Height of the body front wall at the point (x, y): by the profile rings from the edge (linear between
    them)."""
    d = min(x - BX0, BX1 - x, y - BY0, BY1 - y)
    return profile_z(BODY_RINGS[BODY_KANT:], d)


def flap_outline(inset=0.0, n=8):
    """Flap outline (counter-clockwise) with inset inset: the root at the bottom (under the body), rounded
    free corners."""
    x0, x1 = FL_X0 + inset, FL_X1 - inset
    y0, y1 = FL_Y0, FL_Y1 - inset
    r = max(0.002, FL_R - inset)
    pts = [(x0, y0), (x1, y0)]
    for k in range(n + 1):
        a = math.radians(90.0 * k / n)
        pts.append((x1 - r + r * math.cos(a), y1 - r + r * math.sin(a)))
    for k in range(n + 1):
        a = math.radians(90.0 + 90.0 * k / n)
        pts.append((x0 + r + r * math.cos(a), y1 - r + r * math.sin(a)))
    return pts


def rot(p, c, deg):
    a = math.radians(deg)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))
