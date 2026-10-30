"""M65 - dimensions shared by build_m65.py (Blender) and make_decals.py (system Python + Pillow): the
backing board, the sheets of the stack, the folded corner of the top sheet, the binder clip. No
dependencies - both import it.

Generator axes (before the tilt): X is the sheet width (the left edge at -X), Y is the sheet height
(the top with the clip at +Y, the bottom towards the viewer, at -Y), Z is up. The origin is the centre
of the board on the ground. A dropped stack rests on the far edge of the board and on the clip handle,
so the generator then tilts everything by the angle TILT (it computes it) about the bottom edge of
the board.

Coordinates on paper (the vertex attribute `pp` in the generator, the image of make_decals.py), metres:
sheet i lies in its own cell of the shared image - pp = (SLOT_W * slot + u, v), where (u, v) are from
the sheet centre, u to the right, v up the sheet (towards the clip). The top of the image is the top
of the sheets.
"""
import math

# --- sheets: A5 (ISO 216: 148 x 210 mm), from glue-bound pads with 5 mm squares and with rules ----
SW, SH = 0.148, 0.210
TH = 0.0002                       # sheet (for looks; the real one is ~0.1 mm - thinner would flicker)
GAP = 0.00034                     # pitch of sheets in the stack

# --- backing board: an offcut of painted pressboard from an old folder, knife-cut to A5 with a margin
#     (estimate: ~9 mm at the sides, ~20 mm at the bottom, so that the line colour reads as a frame),
#     ~1 mm board ----------------------------------------------------------------------------------
BW, BH = 0.166, 0.232
BT = 0.0010
B_Y1 = BH / 2                     # top of the board: in the jaws of the clip
Y_TOP = B_Y1 - 0.0010             # top of the sheets: pushed into the clip slightly less than the board
# board outline (counter-clockwise): the bottom is cut slightly askew, the top right corner is the
# original rounded folder corner (r 6 mm), the others are cut
B_R = 0.006


B_R_SEG = 6                       # the original corner is an arc of 6 segments (3 showed facets in close-ups)


def board_outline():
    x0, x1, y0, y1 = -BW / 2, BW / 2, -BH / 2, BH / 2
    pts = [(x0 + 0.0004, y0), (x1, y0 + 0.0013), (x1 - 0.0003, y1 - B_R)]
    cx, cy = x1 - 0.0003 - B_R, y1 - B_R
    for k in range(1, B_R_SEG):
        a = math.pi / 2 * k / B_R_SEG
        pts.append((cx + B_R * math.cos(a), cy + B_R * math.sin(a)))
    pts += [(cx, y1), (x0, y1 - 0.0004)]
    return pts


# board split into cells: the visible borders at the left, right and bottom are atlas regions of their own
B_XCUT = (-0.0700, 0.0700)
B_YCUT = (Y_TOP - SH + 0.0040,)

# --- sheets of the stack (bottom to top): ruling, centre (from the top of the sheets), rotation (deg.,
#     counter-clockwise), image cell; cuts (u, v) run along the edges of the visible strips and of the
#     atlas strips (sheet_region) ------------------------------------------------------------------
SLOT_W, SLOT_H = 0.170, 0.226


def _c(dx, dy):
    return (dx, Y_TOP - SH / 2 + dy)


SHEETS = [
    dict(name="s1", rule="grid", c=_c(0.0010, -0.0004), rot=0.5, ucut=(), vcut=(), ink="pencil"),
    # torn from a spiral pad: the left edge is ragged, the sheet sticks out to the left
    dict(name="s2", rule="lines", c=_c(-0.0034, -0.0006), rot=-1.4, ucut=(-0.0640,), vcut=(), ragged=True,
         ink="black"),
    # lowered by ~10 mm: its bottom with the total peeks out from under the upper sheets
    dict(name="s3", rule="lines", c=_c(0.0018, -0.0105), rot=2.2, ucut=(), vcut=(-SH / 2 + 0.0190,), ink="blue"),
    dict(name="s4", rule="grid", c=_c(-0.0016, -0.0003), rot=-0.5, ucut=(), vcut=(), ink="violet"),
    # under the folded corner of the top sheet - its corner is exposed
    dict(name="s5", rule="grid", c=_c(0.0012, -0.0009), rot=0.8, ucut=(SW / 2 - 0.0500,), vcut=(-SH / 2 + 0.0560,),
         ink="violet"),
    # top: the price list
    dict(name="top", rule="grid", c=_c(0.0, -0.0002), rot=-0.5, ucut=(-0.040, 0.0, 0.040),
         vcut=(-0.0920, -0.0780, -0.0600, -0.0300, 0.0200, 0.0620), ink="blue"),
]
for _i, _s in enumerate(SHEETS):
    _s["slot"] = _i
    _s["z"] = BT + (_i + 0.5) * GAP   # centre line of the sheet (without bending)
N_SHEETS = len(SHEETS)
Z_TOP = BT + N_SHEETS * GAP       # top of the stack under the clip


def sheet_region(s, cu, cv):
    """Atlas region of a sheet cell s by its centre (cu, cv): the top sheet gets four strips in height and
    two halves in width (atlas rectangles of comparable size pack more tightly on shelves); for the lower
    sheets, the visible strips and "_h", the part covered by the sheets above."""
    n = s["name"]
    if n == "top":
        side = "l" if cu < 0.0 else "r"
        for lim, reg in ((-0.030, "top_c"), (0.020, "top_b"), (0.062, "top_a")):
            if cv < lim:
                return reg + side
        return "top_t" + side
    if n == "s2":
        return "s2_l" if cu < -0.0640 else "s2_h"
    if n == "s3":
        return "s3_b" if cv < -SH / 2 + 0.0190 else "s3_h"
    if n == "s5":
        return "s5_c" if (cu > SW / 2 - 0.0500 and cv < -SH / 2 + 0.0560) else "s5_h"
    return n + "_h"


def board_region(cx, cy):
    if cy < B_YCUT[0]:
        return "bd_b"
    if cx < B_XCUT[0]:
        return "bd_l"
    if cx > B_XCUT[1]:
        return "bd_r"
    return "bd_h"


def ragged_left(rnd_seed=65):
    """Ragged left edge of sheet s2 (u, v) from top to bottom: scraps of the spiral perforation every ~10 mm."""
    import random
    r = random.Random(rnd_seed)
    pts = []
    n = 21
    for k in range(n + 1):
        v = SH / 2 - SH * k / n
        du = r.uniform(0.0, 0.0011) + (0.0009 if k % 2 else 0.0)
        pts.append((-SW / 2 + du, v))
    return pts


# --- folded corner of the top sheet: bottom right, the legs along the bottom and the right edge ---
DOG_A, DOG_B = 0.036, 0.044
DOG_PHI = 18.0                    # angle between the folded corner and the sheet, deg.
DOG_C = (SW / 2, -SH / 2)         # corner of the sheet (u, v)
DOG_F1 = (SW / 2 - DOG_A, -SH / 2)
DOG_F2 = (SW / 2, -SH / 2 + DOG_B)

# the bottom of the top sheet lifts off the stack (the sheet springs under the clip)
CURL_V0 = -0.050                  # from this line down
CURL_H = 0.0032                   # lift of the bottom edge


# a sheet is not a board: below the clip handle the top sheet is slightly bowed across its width - in
# the middle it stands off the lower ones by WAVE_H, while the edges and the strip at the clip lie on
# the stack
WAVE_H = 0.0008
WAVE_V0, WAVE_V1 = 0.040, -0.020   # from v0 (flat) to v1 (full height)


def top_lift(u, v):
    f = max(0.0, (CURL_V0 - v) / (CURL_V0 + SH / 2))
    g = 0.65 + 0.35 * (u + SW / 2) / SW            # slightly higher towards the right edge (the corner)
    t = max(0.0, min(1.0, (WAVE_V0 - v) / (WAVE_V0 - WAVE_V1)))
    t = t * t * (3.0 - 2.0 * t)
    wave = WAVE_H * t * math.sin(math.pi * max(0.0, min(1.0, (u + SW / 2) / SW)))
    return CURL_H * f * f * g + wave


def sheet_xy(s, u, v):
    """Sheet point (u, v from the centre) as world x, y (before the tilt)."""
    a = math.radians(s["rot"])
    cx, cy = s["c"]
    return (cx + u * math.cos(a) - v * math.sin(a), cy + u * math.sin(a) + v * math.cos(a))


def pp(s, u, v):
    return (SLOT_W * s["slot"] + u, v)


# --- binder clip 32 mm (1-1/4"): opening 16 mm (5/8", the same for ACCO / Staples / Quill / Officemate),
#     height with the handles 44 mm (GeM catalogue, binder clip 32 mm) -----------------------------
CW = 0.032                        # width
CD = 0.0165                       # body depth: from the back to the jaws
CHS = 0.0150                      # height of the back (16 mm opening minus the steel)
CST = 0.00045                     # steel
CY_S = Y_TOP + 0.0012             # the back (outer)
CY_J = CY_S - CD                  # jaws
CZ_C = Z_TOP / 2                  # middle of the clamped stack
TAB_R = 0.0011                    # curl of the jaw, holding the handle ends
TAB_L = 0.0060                    # curls at the ends of the jaw
WIRE_R = 0.00065                  # handle wire (~1.3 mm)
H_LEN = 0.0414                    # handle: from the axis to the end of the loop

# body: at the edge the jaw lies flat on the paper (LIP), the jaw bend and the back corners are arcs
# (steel is bent, not broken)
LIP = 0.0012
R_LIP = 0.0015
R_SPINE = 0.0016

# handle in its own plane (a across, b from the axis): control points of a smooth curve (a centripetal
# Catmull-Rom spline). The end is led into the curl from inside (C0-C1 along the curl axis), leaves
# through its outer end and bends into a leg - the legs are slightly wider than the body, as on a real
# clip; the legs converge to the neck, the bulb-shaped loop is ~16 mm
HANDLE_CTRL = [(-0.0108, 0.0), (-0.0152, 0.0), (-0.0166, 0.0010), (-0.0164, 0.0040), (-0.0110, 0.0165),
               (-0.0062, 0.0232), (-0.0054, 0.0262), (-0.0070, 0.0300), (-0.0080, 0.0340), (-0.0066, 0.0385),
               (-0.0034, 0.0408), (0.0, H_LEN)]
# rod segment (decimate): turn on a long segment (deg.), the longest length (m), turn on a short one
# (deg.) and the length from which it counts as long (m) - a kink is visible when a segment is longer
# than the wire thickness: in the loop (r ~8 mm) points every ~15 degrees, in tight bends at the curls
# fewer; near and middle LODs
HANDLE_STEP = {0: (15.0, 0.0070, 40.0, 0.0026), 1: (45.0, 0.0140, 60.0, 0.0040)}


def _cr_segment(p0, p1, p2, p3, n):
    """Centripetal Catmull-Rom (Barry-Goldman) from p1 to p2: n points without p2."""
    def tj(t, a, b):
        return t + max(1e-12, math.dist(a, b)) ** 0.5

    def mix(a, b, ta, tb, t):
        k = (t - ta) / (tb - ta)
        return tuple(x + (y - x) * k for x, y in zip(a, b))
    t0 = 0.0
    t1 = tj(t0, p0, p1)
    t2 = tj(t1, p1, p2)
    t3 = tj(t2, p2, p3)
    out = []
    for k in range(n):
        t = t1 + (t2 - t1) * k / n
        a1, a2, a3 = mix(p0, p1, t0, t1, t), mix(p1, p2, t1, t2, t), mix(p2, p3, t2, t3, t)
        b1, b2 = mix(a1, a2, t0, t2, t), mix(a2, a3, t1, t3, t)
        out.append(mix(b1, b2, t1, t2, t))
    return out


def spline(ctrl, n=16):
    """Dense smooth curve through all points of ctrl (the ends use mirrored points)."""
    ext = [tuple(2 * a - b for a, b in zip(ctrl[0], ctrl[1]))] + list(ctrl) + \
        [tuple(2 * a - b for a, b in zip(ctrl[-1], ctrl[-2]))]
    out = []
    for i in range(1, len(ext) - 2):
        out += _cr_segment(ext[i - 1], ext[i], ext[i + 1], ext[i + 2], n)
    out.append(tuple(ctrl[-1]))
    return out


def decimate(pts, turn_deg, max_len, tight_deg=None, tight_len=1.0):
    """Polyline from a dense curve: a new point appears when the curve has turned by the allowed angle or
    has run max_len. The allowed angle is tight_deg on a short segment and turn_deg from length tight_len:
    points are denser on large arcs and sparser in tight bends and on straight legs; the ends stay."""
    out = [pts[0]]
    acc, run = 0.0, 0.0
    for i in range(1, len(pts) - 1):
        d0 = (pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        d1 = (pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
        l0, l1 = math.hypot(*d0), math.hypot(*d1)
        if l0 > 1e-12 and l1 > 1e-12:
            c = max(-1.0, min(1.0, (d0[0] * d1[0] + d0[1] * d1[1]) / (l0 * l1)))
            acc += math.degrees(math.acos(c))
        run += l0
        lim = turn_deg if tight_deg is None else tight_deg - (tight_deg - turn_deg) * min(1.0, run / tight_len)
        if acc >= lim or run >= max_len:
            out.append(pts[i])
            acc, run = 0.0, 0.0
    out.append(pts[-1])
    return out


def handle_path(lod=0):
    """The whole handle from the end in one curl through the loop to the end in the other: a smooth curve
    through the control points HANDLE_CTRL, thinned by turn angle (HANDLE_STEP), the left half is mirrored
    so the handle is symmetric. A spline curve rather than a polyline through the control points: no kinks."""
    full = HANDLE_CTRL + [(-a, b) for a, b in reversed(HANDLE_CTRL[:-1])]
    n = 16
    dense = spline(full, n)
    half = dense[:n * (len(HANDLE_CTRL) - 1) + 1]          # up to and including the top of the loop
    left = decimate(half, *HANDLE_STEP[lod])
    left[-1] = (0.0, HANDLE_CTRL[-1][1])
    return left + [(-a, b) for a, b in reversed(left[:-1])]


# --- DayZ pen (proxy \dz\gear\tools\Pen) tucked under the upper clip handle -----------------------
# it lies across the sheet on the paper, the loop of the clip handle rests on it (so the clip handle is
# slightly raised); PEN_B is the distance from the clip handle axis to the DayZ pen axis, m; the
# rotation is counter-clockwise from the X axis
PEN_B = 0.031
PEN_X = 0.004
PEN_ROT = 3.5
