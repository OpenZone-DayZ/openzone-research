"""M53 - shared sizes for build_m53.py (Blender) and make_decals.py (system Python + Pillow): a titanium
armour plate, a piece of an aramid pack on it, claw furrows, holes, dents, a rubber band, a tag. No
dependencies - both import it.

Axes as in the generator: X is width, Y is depth (the front faces -Y), Z is up. The origin is the centre
under the stack, on the floor. The stack lies: the plate at the bottom, a piece of aramid on it, the
rubber band across.

Everything make_decals.py reads (positions and radii of the furrows, holes, dents and scratches, the
number, the tag, the stitching) is fixed, so the drawn decals stay valid. The generator adds shapes the
decals do not know: the dent profile (a shallow dish + a sharp bowl from the bullet nose), steeper
furrow walls, a turned-out edge at the holes, a bullet in hole 0, a pressed-in groove along the
stitching, a bent free end of the tag; their sizes are at the end of each part's section.
"""
import math
import random

# --- armour plate: titanium VT-14, 1.25 mm (ADU-605-80, chest of the 6B2 and back of the 6B3/6B5) ---
PL_X, PL_Y = 0.110, 0.150        # 28-30 dm2 of the 6B2 over 19 overlapping plates: ~1.5 dm2 each
PL_T = 0.00125
PL_R = 0.009                     # corner rounding
PL_Z0 = 0.0016                   # bottom of the plate: what touches the floor are the hit bulges and the band
PL_Z1 = PL_Z0 + PL_T
# plate corner bent by a hit: (corner x, y), lift, radius of influence
WARP = ((-PL_X / 2, -PL_Y / 2), 0.0022, 0.050)
# dents from pistol rounds (plate face up, the bulge points down): (x, y, radius, depth)
DENTS = [
    (-0.028, -0.060, 0.0100, 0.0016),
    (0.016, -0.057, 0.0090, 0.0015),
    (0.044, -0.037, 0.0085, 0.0014),     # the dent edge is under the aramid
]
# claw scratches on the plate: three parallel ones across the open strip at the front, between the dents
PL_CLAW_DIR = math.radians(70.0)
PL_CLAWS = [(-0.0165, -0.0730, 0.034), (-0.0090, -0.0736, 0.037), (-0.0015, -0.0722, 0.031)]  # start x, y, length
STAMP = (0.040, -0.068)          # stamped number near the front right corner (digits)
# plate edge rounded by the paint: a chamfer (horizontal, vertical) at the face; a dent is a shallow
# dish of DENT_DISH of the depth plus a sharp bowl from the bullet nose of DENT_CRATER of the radius
# (the total depth is unchanged: the plate still rests on the bulges and the band)
PL_CHAMF = (0.00030, 0.00050)
DENT_DISH = 0.62
DENT_CRATER = 0.40

# --- piece of the aramid pack: 30 layers of TSVM-DZh, cut with a knife ---------------------------
KV_C = (0.002, 0.018)            # centre in plan
KV_ROT = 7.0                     # counter-clockwise rotation, degrees
KV_A, KV_B = 0.048, 0.0525       # half-sizes along its own axes (96 x 105 mm)
KV_Z0 = PL_Z1 + 0.0001
KV_T_EDGE = 0.0060               # the layers are pressed at the edge
KV_T_MID = 0.0080                # 30 layers of ~0.25 mm, uncompressed
KV_EDGE_SOFT = 0.012             # from the edge to the full thickness
KV_BOX = 0.128                   # square of the aramid image (decals) around KV_C
SEAM_IN = 0.0040                 # the left edge is the original one, stitched 4 mm from the edge
# end in rings (top edge, shoulder, two bands of bulged layers shifted, bottom): at the edge the top
# goes down by a shoulder; the stitching is a pressed-in groove; at the front right corner the top three
# layers cut with a knife (0.75 mm) have come off and bent back (FLAP: from the corner along the front
# and along the right side, thickness, slope at the fold and at the tip, degrees)
KV_SHOULDER = (0.0016, 0.0006, 0.0006)   # top edge and shoulder from the rim; shoulder below the top edge
SEAM_DIP = (0.00030, 0.0009)             # stitching groove: depth, half-width
FLAP = dict(front=0.020, side=0.017, t=0.00075, a0=3.0, a1=20.0)

# --- rubber band: a strip of bicycle tube as a ring across the stack ------------------------------
BAND_Y = 0.030
BAND_W = 0.014
BAND_T = 0.0016
BAND_ZIN = KV_Z0 + 0.0062        # bottom of the band above the aramid (the aramid under it is pressed)

# --- claw furrows on the aramid: (start x, y), (end x, y); the direction is towards the front right ---
FURROWS = [
    ((-0.030, 0.010), (-0.0067, -0.0273)),
    ((-0.017, 0.016), (0.0095, -0.0264)),
    ((-0.004, 0.016), (0.0225, -0.0264)),
    ((0.010, 0.011), (0.0312, -0.0229)),
]
FUR_DEPTH = (0.0034, 0.0038, 0.0036, 0.0028)   # 12-15 of the 30 layers are torn
FUR_HW = 0.0018                  # half-width of a furrow in the middle
FUR_LIP = 0.0005                 # frayed edges - above the fabric

# --- holes (the bullets are stopped, none goes through): x, y, radius ---------------------------
HOLES = [(-0.028, 0.052, 0.0034), (-0.006, 0.061, 0.0030)]
HOLE_DEPTH = 0.0042
# around a hole the fibres are turned outwards as a roll (to HOLE_RIM radii, above the fabric by
# HOLE_LIP); in hole 0 sits a 9 x 18 PM bullet, base up (it is flattened, the middle of the base shows):
# base radius, how far it is below the fabric around
HOLE_RIM, HOLE_LIP = 1.55, 0.00045
BULLET = dict(hole=0, r=0.0032, sink=0.0006)

# --- tag: manila 44 x 24 mm with an eyelet, tucked under the band ----------------------------------
TAG_L, TAG_W, TAG_CUT = 0.044, 0.024, 0.005
TAG_P0 = (0.016, 0.0245)         # middle of the end with the eyelet (under the band)
TAG_ROT = 85.0                   # long axis from +x counter-clockwise: from under the band backwards
TAG_RISE = 0.008                 # from the band edge the tag rises onto the aramid pillow
TAG_REST = KV_Z0 + KV_T_MID - 0.0004   # and lies on it, pressing it slightly
TAG_HOLE = 0.0060                # eyelet from the end
TAG_T = 0.0003
TAG_STRIPE = (0.032, 0.040)      # grey stripe of the Protection line: from the end with the eyelet
TAG_BOX = 0.064                  # square of the tag image around its centre
TAG_CURL = (0.030, 0.0015)       # the free end of the tag is bent up - from s, lift at the tip


def rot(x, y, deg):
    a = math.radians(deg)
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))


def kv_world(lx, ly):
    x, y = rot(lx, ly, KV_ROT)
    return (KV_C[0] + x, KV_C[1] + y)


def kv_local(x, y):
    """World point -> aramid-piece axes (the inverse of kv_world)."""
    return rot(x - KV_C[0], y - KV_C[1], -KV_ROT)


def kv_outline(detail=1):
    """Outline of the piece, counter-clockwise (top view), world x, y. The left edge is the original,
    straight, with finished corners; the other three are cut with a knife: a wave, pulled threads, cut
    corners. detail=0 is for the mid LOD.
    """
    rnd = random.Random(53)
    a, b = KV_A, KV_B
    # sides: (start, end, number of segments, scatter along the normal)
    n_cut = 7 if detail else 3
    n_neat = 4 if detail else 2
    sides = [((-a + 0.0015, -b), (a - 0.0020, -b), n_cut, 0.0011),        # front - cut
             ((a, -b + 0.0020), (a, b - 0.0015), n_cut, 0.0012),          # right - cut
             ((a - 0.0015, b), (-a + 0.0025, b), n_cut, 0.0010),          # back - cut
             ((-a, b - 0.0025), (-a, -b + 0.0015), n_neat, 0.0002)]       # left - original edge
    pts = []
    for (x0, y0), (x1, y1), n, jit in sides:
        tx, ty = x1 - x0, y1 - y0
        ln = math.hypot(tx, ty)
        nx, ny = ty / ln, -tx / ln                                       # outwards
        for i in range(n + 1):
            f = i / n
            j = 0.0 if i in (0, n) else rnd.uniform(-jit, jit)
            fa = f + (0.0 if i in (0, n) else rnd.uniform(-0.25, 0.25) / n)
            pts.append((x0 + tx * fa + nx * j, y0 + ty * fa + ny * j))
    return [kv_world(x, y) for x, y in pts]


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
    """Distance to a segment and the fraction t along it."""
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - t * dx, py - ay - t * dy), t


def edge_dist(poly, x, y):
    return min(seg_dist(x, y, *poly[i], *poly[(i + 1) % len(poly)])[0] for i in range(len(poly)))


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def furrow_profile(k, t):
    """Furrow k at fraction t: (depth, half-width) - the claw enters shallow, goes deeper at a third,
    comes out.
    """
    s = math.sin(math.pi * max(0.0, min(1.0, t)))
    lead = 0.75 + 0.25 * math.sin(math.pi * min(1.0, t * 1.4))
    return FUR_DEPTH[k] * (s ** 0.6) * lead, FUR_HW * (0.35 + 0.65 * s)


def kv_cushion_z(x, y, poly):
    """Aramid pillow without marks: thinner at the edge, a light wave of layers."""
    d = edge_dist(poly, x, y)
    z = KV_Z0 + KV_T_EDGE + (KV_T_MID - KV_T_EDGE) * smooth(d / KV_EDGE_SOFT)
    return z + 0.00025 * math.sin(x * 70.0 + 1.3) * math.cos(y * 55.0 - 0.4) * smooth(d / 0.006)


def kv_top_z(x, y, poly, extra=None, seam=True):
    """Aramid top: the pillow (thinner at the edge), the stitching groove, pressed by the band and tag,
    claw furrows (steep walls, frayed edges above the fabric), holes (a funnel, a turned-out roll; in
    the hole with a bullet the fabric goes down to the bullet base); extra(x, y) is an addition from the
    generator (the peeled corner).
    """
    z = kv_cushion_z(x, y, poly)
    if seam:
        lx, ly = kv_local(x, y)
        ds = abs(lx - (-KV_A + SEAM_IN))
        if ds < SEAM_DIP[1] and abs(ly) < KV_B - 0.003:
            z -= SEAM_DIP[0] * (1.0 - (ds / SEAM_DIP[1]) ** 2)
    dy = abs(y - BAND_Y) - BAND_W / 2
    cap = BAND_ZIN - TAG_T - 0.00005 + max(0.0, dy) * 0.35
    z = min(z, cap)
    for k, ((ax, ay), (bx, by)) in enumerate(FURROWS):
        dp, t = seg_dist(x, y, ax, ay, bx, by)
        depth, hw = furrow_profile(k, t)
        if dp < hw:
            z -= depth * (1.0 - (dp / hw) ** 4)              # steeper walls, wider bottom (torn layers)
        elif dp < hw + 0.0022 and 0.0 < t < 1.0:
            z += FUR_LIP * math.sin(math.pi * (dp - hw) / 0.0022) * math.sin(math.pi * t)
    s, q = tag_uv(x, y)
    m = 0.0007
    if -m <= s <= TAG_L + m and abs(q) <= TAG_W / 2 + m:
        z = min(z, tag_bottom(s) - 0.00005)                  # the tag pressed the aramid down
    for i, (hx, hy, r) in enumerate(HOLES):
        dr = math.hypot(x - hx, y - hy)
        if dr < r:
            dz = HOLE_DEPTH * (1.0 - (dr / r) ** 0.5)          # funnel: narrow and deep
            if i == BULLET["hole"]:
                dz = min(dz, BULLET["sink"] + 0.0004)          # under the bullet base
            z -= dz
        elif dr < r * HOLE_RIM:
            z += HOLE_LIP * math.sin(math.pi * (dr - r) / (r * (HOLE_RIM - 1.0)))   # turned-out roll
    if extra is not None:
        z += extra(x, y)
    return z


def dent_depth(x, y):
    """Sum of the dents at a point (on the face - down, on the back - a bulge down): a shallow dish and
    a sharp bowl from the bullet nose in the middle; the depth in the middle is dep.
    """
    s = 0.0
    for dx, dy, r, dep in DENTS:
        q = math.hypot(x - dx, y - dy) / r
        if q < 1.0:
            s += dep * DENT_DISH * (1.0 - q * q) ** 2
        if q < DENT_CRATER:
            s += dep * (1.0 - DENT_DISH) * (1.0 - (q / DENT_CRATER) ** 2)
    return s


def warp(x, y):
    (cx, cy), lift, rad = WARP
    q = math.hypot(x - cx, y - cy) / rad
    return lift * (1.0 - q) ** 2 if q < 1.0 else 0.0


def tag_frame():
    """Tag axes: the origin is the middle of the end with the eyelet, u runs along the tag, v across (to
    the left).
    """
    a = math.radians(TAG_ROT)
    return TAG_P0, (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))


def tag_point(s, w):
    (ox, oy), (ux, uy), (vx, vy) = tag_frame()
    return (ox + ux * s + vx * w, oy + uy * s + vy * w)


def tag_center():
    return tag_point(TAG_L / 2, 0.0)


def tag_uv(x, y):
    """World point -> (s along the tag from the end, q across)."""
    (ox, oy), (ux, uy), (vx, vy) = tag_frame()
    return ((x - ox) * ux + (y - oy) * uy, (x - ox) * vx + (y - oy) * vy)


def tag_exit():
    """s where the tag has fully come out from under the band (the far edge of the strip)."""
    _, (ux, uy), (vx, vy) = tag_frame()
    y_far = BAND_Y + BAND_W / 2
    return (y_far - TAG_P0[1] + abs(vy) * TAG_W / 2) / uy


def tag_bottom(s):
    """Tag bottom: under the band it is pressed to it, beyond the edge it rises onto the pillow and lies
    on it; the free end of the card is bent up (TAG_CURL).
    """
    z0 = BAND_ZIN - TAG_T
    s0 = tag_exit()
    if s <= s0:
        return z0
    if s <= s0 + TAG_RISE:
        return z0 + (TAG_REST - z0) * (s - s0) / TAG_RISE
    sc, lift = TAG_CURL
    if s > sc:
        return TAG_REST + lift * ((s - sc) / (TAG_L - sc)) ** 2
    return TAG_REST


def tag_stations(detail=1):
    s0 = tag_exit()
    if not detail:
        return [0.0, s0, s0 + TAG_RISE, TAG_L]
    sc = TAG_CURL[0]
    return [0.0, TAG_CUT, s0, s0 + TAG_RISE, sc, (sc + TAG_L) / 2, TAG_L]


def tag_halfwidth(s):
    return TAG_W / 2 - TAG_CUT * (1.0 - s / TAG_CUT) if s < TAG_CUT else TAG_W / 2


def tag_footprint(detail=1, m=0.0004):
    """Tag outline in plan, inflated by m (counter-clockwise)."""
    st = tag_stations(detail)
    right = [tag_point(s if 0 < s < TAG_L else s + (m if s else -m), -(tag_halfwidth(s) + m)) for s in st]
    left = [tag_point(s if 0 < s < TAG_L else s + (m if s else -m), tag_halfwidth(s) + m) for s in st]
    return right + left[::-1]
