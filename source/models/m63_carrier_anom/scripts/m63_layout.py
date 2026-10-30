"""Dimensions shared by M63 (the "Anomaly" carrier): build_m63.py (Blender) and make_decals.py (system
Python + Pillow) both use them. Metres. Sources of the sizes are in the docstring of build_m63.py.

The envelope uses its own coordinates (u, v): u runs along the envelope from the glued bottom (0) to
the mouth (EL), v across, 0 in the middle. In Blender: X = u - U0, Y = v, Z is up. The envelope lies
flap up (the back with the seams), the mouth is at +X, the flap is open and lies flat beyond the
mouth, with a half-pulled-out print on it.

The print uses its own coordinates (s, t): s runs along from the inner end (0) to the outer one
(PRINT_L), t across from the edge at -v (0) to the edge at +v (PRINT_W). It is rotated by PRINT_ROT
about the mouth point.

make_decals.py reads only the sizes of the envelope, flap, seam, bottom, notch, flap button, print and
tag from here: changing them means redrawing the decals. Everything else is geometry only: the bent
corner (DOG_*), rounded corners, more segments in the notch and the winding, a half-section string,
the peeled tag corner (PEEL_*), an eyelet with a rim (EYE_RO, EYE_RI).
"""
import math

# --- envelope 7 x 10 inches (open end, the flap on the short end) ---------------------------------
EL = 0.254                  # length (10")
EW = 0.1778                 # width (7")
HW = EW / 2
T0 = 0.00035                # thickness at the folded edge (two kraft layers ~0.12 mm and air)
PAPER = 0.00015             # one kraft layer
FLAP_T = 0.00025            # the flap looks thicker than one layer: a 0.15 mm high edge comes out degenerate
FD = 0.045                  # flap depth
F_TAPER = 0.008             # the flap narrows towards its edge by this much on each side
F_R = 0.008                 # flap corner rounding
NOTCH_R = 0.012             # finger notch in the mouth of the back
NOTCH_SEG = (12, 4)         # notch segments per LOD (fewer segments made the notch read as a polygon)
FLAP_SEG = (5, 1)           # segments per rounded flap corner per LOD
BOT_FLAP = 0.030            # glued bottom on the back
SEAM_V = 0.004              # edge of the seam overlap in the middle of the back
SEAM_GLUE = 0.010           # glue strip under the overlap (towards -v from the edge)

# the corner at the glued bottom (u = 0, v = -HW) is bent up along a straight crease, both walls
# together. The crease is where the decal of the back already shows a diagonal fold at this corner
# (make_decals.py: (0, -0.052) - (0.034, -HW), almost straight): 36.9 mm from the corner along the
# bottom edge and 34 mm along the side; the bend is soft (the DOG_W strip), beyond it the small corner
# is flat, raised by 11 degrees (~4.5 mm at the tip)
DOG_A = HW - 0.052
DOG_B = 0.034
DOG_W = 0.003
DOG_SLOPE = math.tan(math.radians(11.0))
TIP_R = 0.0025              # the bent corner is worn: rounded
CORNER_R = 0.003            # the second corner of the bottom (u = 0, v = +HW) is worn

# inside: three more prints and a folded protocol have slid to the bottom of the envelope
STACK = (0.004, 0.184, -0.067, 0.063)       # u0, u1, v0, v1
STACK_T = 0.0014
PUFF = 0.0014               # the paper does not hug the pile tightly

# --- 13 x 18 cm print on glossy photo paper -------------------------------------------------------
PRINT_L = 0.180
PRINT_W = 0.130
PRINT_T = 0.0003
PULL = 0.090                # pulled out halfway
PRINT_ROT = math.radians(3.5)
PRINT_DV = 0.009            # sideways shift (towards +v)
S_MOUTH = PRINT_L - PULL    # where the print passes the mouth
S_IN = S_MOUTH - 0.018      # the print model starts inside the envelope 18 mm from the mouth (the notch is 12)
DRAPE_GAP = 0.00025         # gap between the back and the print at the mouth
CURL = 0.0006               # print edges are raised (glossy paper curls towards the emulsion)
BORDER = (0.006, 0.006, 0.006, 0.008)       # white border: left (s=0), right, top (+t), bottom

# --- fibre washer buttons with an eyelet, and the string ------------------------------------------
WASHER_R = 0.0125
WASHER_T = 0.0009
WASHER_BEV = 0.00025        # bevel on the top edge of the washer (die-cut fibre, the edge is crushed)
WASHER_LIFT = 0.0010        # the washer sits on the eyelet shank: the string runs under it
EYE_R = 0.003               # eyelet of the middle LOD (a cone)
EYE_RO = 0.0030             # eyelet of the near LOD: the rolled rim outside and the hole
EYE_RI = 0.0013
EYE_H = 0.0006
BTN_BODY = (0.188, 0.0)     # on the back, under the edge of the closed flap
BTN_FLAP = (EL + FD / 2, 0.0)   # on the flap (outside; the flap is open, so the washer is underneath)
FLAP_RING = 10              # points around the ring at the flap washer (the hump of the flap over it)
STRING_R = 0.0006           # half-width of the string
STRING_H = 0.00075          # height over the support: it lies on half its section, being soft it is slightly flattened
STRING_Z0 = 0.00006         # bottom of the section over the support
FLAP_SAG = 0.010            # sag of the flap from the washer edge to the ground

# --- tag ------------------------------------------------------------------------------------------
LABEL_C = (0.093, -0.026)
LABEL_SIZE = (0.072, 0.042)
LABEL_ROT = math.radians(-2.5)
LABEL_T = 0.0002
# the tag corner at the mouth (a = +hw, b = -hh) has peeled off: raised by PEEL_H, the fold runs along
# the diagonal of the PEEL_A x PEEL_B cell (near LOD)
PEEL_A = 0.014
PEEL_B = 0.010
PEEL_H = 0.0022

# --- in the world ---------------------------------------------------------------------------------
U0 = 0.172                  # X = u - U0: the origin is the middle of the length (envelope + pulled-out print)

# image of the back and of the inside of the flap (make_decals.py): u 0..ENV_IMG_L, v -HW..HW
ENV_IMG_L = 0.300


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def inside(poly, x, y):
    c = False
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            c = not c
    return c


def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def edge_dist(poly, x, y):
    return min(seg_dist(x, y, *poly[i], *poly[(i + 1) % len(poly)]) for i in range(len(poly)))


# --- print ----------------------------------------------------------------------------------------
def print_uv(s, t):
    """Print point (s, t) -> envelope (u, v)."""
    a, b = s - S_MOUTH, t - PRINT_W / 2
    c, sn = math.cos(PRINT_ROT), math.sin(PRINT_ROT)
    return EL + a * c - b * sn, PRINT_DV + a * sn + b * c


def print_st(u, v):
    """Inverse of print_uv."""
    a, b = u - EL, v - PRINT_DV
    c, sn = math.cos(PRINT_ROT), math.sin(PRINT_ROT)
    return S_MOUTH + a * c + b * sn, PRINT_W / 2 - a * sn + b * c


def print_outline():
    return [print_uv(s, t) for s, t in ((S_IN, 0.0), (PRINT_L, 0.0), (PRINT_L, PRINT_W), (S_IN, PRINT_W))]


# --- flap -----------------------------------------------------------------------------------------
def flap_outline(seg=3, step=None):
    """Flap outline (u, v) counter-clockwise from the hinge at -v: side, rounding, edge, rounding, side; the
    hinge (u = EL) is the closing edge. step: long segments (sides, edge) are split to no longer than
    step; otherwise needle triangles appear along the flap edge, which is as high as the paper is thick."""
    tip = EL + FD
    side_end = (tip - F_R, -HW + F_TAPER)
    arc0 = [(tip - F_R + F_R * math.cos(-math.pi / 2 + (math.pi / 2) * k / seg),
             -HW + F_TAPER + F_R + F_R * math.sin(-math.pi / 2 + (math.pi / 2) * k / seg)) for k in range(seg + 1)]
    arc1 = [(tip - F_R + F_R * math.cos((math.pi / 2) * k / seg),
             HW - F_TAPER - F_R + F_R * math.sin((math.pi / 2) * k / seg)) for k in range(seg + 1)]
    corners = [(EL, -HW)] + arc0 + arc1 + [(EL, HW)]
    if step is None:
        step = 0.5 * math.hypot(side_end[0] - EL, side_end[1] + HW) + 1e-6
    pts = []
    for a, b in zip(corners, corners[1:]):
        n = max(1, int(math.ceil(math.hypot(b[0] - a[0], b[1] - a[1]) / step)))
        pts += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    pts.append(corners[-1])
    return pts


def flap_bottom(u, v):
    """Flap bottom: lies on the ground, raised over the washer of its own button; beyond the washer edge the
    paper sags (a convex falloff over FLAP_SAG)."""
    r = math.hypot(u - BTN_FLAP[0], v - BTN_FLAP[1])
    if r <= WASHER_R:
        return WASHER_T
    x = min(1.0, (r - WASHER_R) / FLAP_SAG)
    return WASHER_T * (1.0 - x) ** 2


def flap_top(u, v):
    return flap_bottom(u, v) + FLAP_T


# --- print height ---------------------------------------------------------------------------------
def print_bottom(s, t):
    """Bottom of the print: inside the envelope it lies on the front wall; from the mouth it runs as a stiff
    sheet straight onto the washer of the flap button (the flap sags lower between them) and drops to the
    ground beyond the washer; the edges curl up (less under the back)."""
    s_edge = S_MOUTH + FD / 2 - WASHER_R          # washer edge on the mouth side
    s_far = S_MOUTH + FD / 2 + WASHER_R
    z_in = PAPER + 0.00005
    z_mouth = z_in + 0.00006
    z_bump = flap_top(*BTN_FLAP) + 0.00008
    if s <= S_MOUTH:
        z = z_in + (z_mouth - z_in) * smooth((s - S_MOUTH + 0.006) / 0.006)
    elif s <= s_edge:
        z = z_mouth + (z_bump - z_mouth) * (s - S_MOUTH) / (s_edge - S_MOUTH)
    elif s <= s_far:
        z = z_bump
    else:
        k = (s - s_far) / (PRINT_L - s_far)
        z = z_bump - (z_bump - 0.00012) * (k * k * (1.6 - 0.6 * k))
    w = smooth((s - S_MOUTH) / 0.024)              # inside the envelope the sheet is pressed by the back: flat
    q = (t - PRINT_W / 2) / (PRINT_W / 2)
    z += CURL * q * q * w
    u, v = print_uv(s, t)
    if u > EL:
        z = max(z, flap_top(u, v) + 0.00008)
    return z


def print_top(s, t):
    return print_bottom(s, t) + PRINT_T


# --- bent corner and worn corners -----------------------------------------------------------------
def dog_line():
    """Crease of the bent corner: a point on the bottom edge (u = 0) and the unit normal in plan towards the
    corner."""
    ln = math.hypot(DOG_A, DOG_B)
    return (0.0, -HW + DOG_A), (-DOG_A / ln, -DOG_B / ln)


def dog_d(u, v):
    """Distance in plan from the crease towards the corner (> 0 is the bent part)."""
    (u0, v0), (nx, ny) = dog_line()
    return (u - u0) * nx + (v - v0) * ny


def dog_lift(u, v):
    """Lift of the bent corner: 0 up to the crease, a soft bend over DOG_W, then a flat sheet with slope
    DOG_SLOPE. It is added to both walls of the envelope and to its edges."""
    d = dog_d(u, v)
    if d <= 0.0:
        return 0.0
    if d < DOG_W:
        return DOG_SLOPE * d * d / (2 * DOG_W)
    return DOG_SLOPE * (d - DOG_W / 2)


def _dog_cross(d):
    """Where the line at distance d from the crease crosses the bottom edge (u = 0) and the side (v = -HW)."""
    (u0, v0), (nx, ny) = dog_line()
    return (0.0, v0 + d / ny), ((d - (-HW - v0) * ny) / nx, -HW)


def dog_folds():
    """The crease (d = 0) and the end of the bend (d = DOG_W) as polylines "bottom edge - middle - side":
    constraint edges for triangulation, so that triangles do not cross the bend."""
    out = []
    for d in (0.0, DOG_W):
        a, b = _dog_cross(d)
        out.append((a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), b))
    return out


def dog_points(seg=2):
    """Outline at the bent corner, counter-clockwise: the crease and the bend on the bottom edge, the rounded
    small corner, the bend and the crease on the side."""
    a0, b0 = _dog_cross(0.0)
    a1, b1 = _dog_cross(DOG_W)
    cx, cy = TIP_R, -HW + TIP_R
    arc = [(cx + TIP_R * math.cos(math.pi + 0.5 * math.pi * k / seg),
            cy + TIP_R * math.sin(math.pi + 0.5 * math.pi * k / seg)) for k in range(seg + 1)]
    return [a0, a1] + arc + [b1, b0]


def corner_points(seg=2):
    """Worn bottom corner at the +v side, counter-clockwise: from the side to the bottom edge."""
    return [(CORNER_R + CORNER_R * math.cos(0.5 * math.pi * (1 + k / seg)),
             HW - CORNER_R + CORNER_R * math.sin(0.5 * math.pi * (1 + k / seg))) for k in range(seg + 1)]


# --- back -----------------------------------------------------------------------------------------
def back_outline(notch_seg=8, tip_seg=2):
    """Outline of the back (u, v), counter-clockwise: the bottom (worn corner, bent corner), the -v side, the
    mouth with the notch, the +v side."""
    pts = corner_points(tip_seg) + [(0.0, 0.045), (0.0, 0.0), (0.0, -0.045)] + dog_points(tip_seg)
    for u in (0.068, 0.102, 0.136, 0.170, 0.204, 0.232):
        pts.append((u, -HW))
    mouth = [-HW, -0.078, -0.066, -0.054, -0.040, -0.024]
    for v in mouth:
        pts.append((EL, v))
    for k in range(notch_seg + 1):
        a = -math.pi / 2 + math.pi * k / notch_seg
        pts.append((EL - NOTCH_R * math.cos(a), NOTCH_R * math.sin(a)))
    for v in (0.024, 0.040, 0.054, 0.066, 0.078):
        pts.append((EL, v))
    for u in (EL, 0.232, 0.204, 0.170, 0.136, 0.102, 0.068, 0.034):
        pts.append((u, HW))
    # drop duplicates (corners)
    out = []
    for p in pts:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 1e-6:
            out.append(p)
    if math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) < 1e-6:
        out.pop()
    return out


def pillow(u, v):
    """Lift of the back over the pile inside: a plateau over the pile, a soft falloff towards the edges."""
    u0, u1, v0, v1 = STACK
    fu = smooth((u - (u0 - 0.004)) / 0.022) * (1.0 - smooth((u - u1 + 0.006) / 0.030))
    fv = smooth((v - (v0 - 0.006)) / 0.026) * (1.0 - smooth((v - v1 + 0.008) / 0.026))
    # the paper over the pile is convex: the middle of the pile is higher
    cu, cv = (u0 + u1) / 2, (v0 + v1) / 2
    d = ((u - cu) / ((u1 - u0) / 2)) ** 2 + ((v - cv) / ((v1 - v0) / 2)) ** 2
    puff = PUFF * max(0.0, 1.0 - d) ** 1.3
    edge = smooth(min(u, HW - abs(v), EL - u) / 0.020)
    return T0 + (STACK_T * fu * fv + puff * fu * fv) * edge


def drape(u, v):
    """The back at the mouth rests on the pulled-out print: its edge sits under the paper."""
    s, t = print_st(u, v)
    if s < S_IN - 0.012:
        return 0.0
    tc = min(max(t, 0.0), PRINT_W)
    dist = abs(t - tc)
    base = print_top(min(max(s, S_IN), S_MOUTH), tc) + DRAPE_GAP
    fall = 1.0 - smooth(dist / 0.009)
    # falloff towards the envelope edges: the paper of the back is drawn in by the fold
    edge = smooth((HW - abs(v)) / 0.010)
    return T0 + (base - T0) * fall * edge if base > T0 else 0.0


def back_top(u, v):
    return max(pillow(u, v), drape(u, v)) + dog_lift(u, v)


# --- tag ------------------------------------------------------------------------------------------
def label_uv(a, b):
    """Tag point (a, b), a along the long side, b across (from the centre) -> (u, v)."""
    c, sn = math.cos(LABEL_ROT), math.sin(LABEL_ROT)
    return LABEL_C[0] + a * c - b * sn, LABEL_C[1] + a * sn + b * c


def label_peel(a, b):
    """Lift of the peeled tag corner: the corner vertex itself only (a = +hw, b = -hh)."""
    hw, hh = LABEL_SIZE[0] / 2, LABEL_SIZE[1] / 2
    return PEEL_H if abs(a - hw) < 1e-9 and abs(b + hh) < 1e-9 else 0.0


# --- string ---------------------------------------------------------------------------------------
def string_path(lod=0):
    """String: points (u, v, lift over the surface under it; None means it lies on the ground) and the number
    of smoothing points per segment. The string is wound on the eyelet shank under the washer (as on real
    envelopes: the washer holds the winding; it is not visible under the washer) and comes out from under
    the washer edge towards the -v side; over the back it lies loose, in a hook, over the edge onto the
    ground, with the end bent towards the bottom of the envelope. A winding outside the washer as an even
    ring read as a gasket, not as a string."""
    cu, cv = BTN_BODY

    def polar(r, deg):
        a = math.radians(deg)
        return cu + r * math.cos(a), cv + r * math.sin(a)
    under = [polar(0.0085, 235.0) + (-0.0001,), polar(0.0115, 250.0) + (0.0,), polar(0.0150, 262.0) + (0.0,)]
    back = [(0.1890, -0.0240), (0.1935, -0.0335), (0.1930, -0.0440), (0.1860, -0.0540), (0.1735, -0.0620),
            (0.1600, -0.0700), (0.1505, -0.0790), (0.1465, -HW + 0.003)]
    ground = [(0.1450, -HW - 0.0026), (0.1420, -0.0975), (0.1345, -0.1035), (0.1235, -0.1065), (0.1120, -0.1055),
              (0.1035, -0.1020)]
    pts = under + [(u, v, 0.0) for u, v in back] + [(u, v, None) for u, v in ground]
    # the hook at the washer gets three points per segment, other bends two, almost straight runs one (where
    # adjacent segments meet at less than 40 degrees the LOD smooths them)
    subs = [1, 1, 3, 3, 3, 3, 3, 1, 2, 1, 2, 1, 2, 2, 1, 1]
    if lod != 0:
        pts = [pts[i] for i in (0, 2, 4, 6, 8, 10, 11, 13, 15, 16)]
        subs = [1] * (len(pts) - 1)
    return pts, subs
