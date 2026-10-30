"""M67 - "Ballistics" carrier (OZL_Carrier_Ball): the carrier of the "Ballistics" line, shared by the
factions: a paper target with bullet holes, folded in four, with a shooting protocol form pinned to
it by a paper clip. A portable 2x2 item.

    blender --background --python build_m67.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]
                                                   [--bake-only [--geo-render | --look-render]]

Before the first run, run make_decals.py with the system Python (target, hole mask, protocol).

Target: folded ~20 x 25 x 1 cm; a target of circles with digits or a silhouette, 6-10 holes with torn
edges and scorching, the folds visible; a protocol - a form with fields, on top; a cardboard folder
cover underneath (camoGround) or a coloured band on the protocol; 200-400 g, 300-1000 triangles,
texture 512-1024; no readable text.

Reference and sizes:
- target: sport No. 4 (for a pistol at 25 and 50 m; a similar round target with bullet holes served as
  the reference). Per ISSF rules (the 25 m precision / 50 m pistol target; excerpts of the rules on
  zielsport.at, Eemann Tech cards): ten D 50 mm, rings every 50 mm up to one D 500, inner ten D 25,
  black "bull" (7-10) D 200, lines 0.2-0.5 mm, digits 1-9 ~10 mm high on the vertical and horizontal,
  no digit on the ten. The sheet is 500 x 500 mm, paper 60-80 g/m2 (shops: neva-target "Target No. 4
  (sport) 500*500 mm 60 g/m", arbaletdv "No. 4 sport (500x500)"; the airgun.org.ru and print-net tables
  give a 550 x 500 blank, ISSF wants a visible part of at least 550 x 520). Folded in four, print
  outside: 4 layers of ~0.1 mm, the stack ~250 x 250 mm. The folds are not at the centre (at 7 and
  10 mm), so the larger quarter 257 x 260 mm is on top, and the centre of the rings with the holes is
  at the corner where the folds meet (the left and bottom edges of the stack are folds, the right and
  top are cut edges). The thickness is for looks: the folds spring, 2-2.3 mm at the folds, ~1.1 in the
  middle; overall ~25.7 x 26 x 0.4 cm (with the protocol and the clip).
- holes: 10 shots from a 9 mm pistol (a hole in paper of ~8.5 mm): seven are visible on the top
  quarter (six in the black, tightly grouped), one on the bottom layer, two on the middle ones. A torn
  edge with star-shaped tears, a grey wipe ring along the edge; two holes are close-range shots
  (forensic ballistics: soot and powder specks, a brown scorch at the nearer one), the distance in cm
  is in pencil beside them. Also in pencil, the total in a circle, a pen number in the empty field, a
  violet judge's stamp without text.
- protocol: an A5 form (ISO 216: 148 x 210 mm): items with numbers and lines for entries, a table for
  10 shots (deviations horizontally and vertically, distance from the centre, points, a note - the
  numbers match the holes of the target), a 1:5 hit diagram with rings, the dispersion circle and the
  mean point of impact, signature lines with flourishes and a violet stamp. A blue diagonal band (the
  colour of the "Ballistics" line, like the stripe of the M52 tag) is the camoGround selection (the
  "coloured band on the protocol" variant: a folder cover underneath is already used by M62 and M65).
  It lies on top of the target, rotated by 3 degrees, its top edge at the top cut edge; the free
  bottom right corner has sprung by ~4.5 mm.
- paper clip: stationery, 28 mm (the length per shop cards; the width ~8.6 mm and the wire D 0.8 are
  estimated from a photo), a "Gem": the outer loop on top of the protocol, the bend wraps the edge,
  the inner loop is under the top layer of the target (not visible, not built). Galvanized steel.

State is `used but intact`: the paper has yellowed at the folds and cut edges, finger and graphite
marks at the corner, the folds are worn. There are no lamps, screens or moving parts, so there is no
"work" view. LODs (a small item): near and middle.

Detailing (preview without baking is `-- --look`):
- "dayz" look (kmodel.Model(look="dayz")); the rvmat has specular 1.0, as in the profile: in "dayz"
  the paper highlight is already compressed in _smdi to G ~0.03 (specular x G ~0.03 is the low end of
  vanilla workshop furniture), and the preview computes the highlight from the profile's specular -
  otherwise the preview and the game would diverge;
- the paper gets its own "dayz" treatment (paper_dayz), not kmats.weather: streaks and scratches
  belong to metal, and the noisy dust of kmats.weather gave grain on the black paint. The colour is
  muted per the profile (patina), the tone in blotches (the paper yellowed unevenly), dust in specks,
  greasy finger spots, hand marks at the right cut edge and at the bent corner; the ripple of the
  sheet is relief;
- bent corner: the top left corner of the stack (fold on the left, cut edge on top) is bent up by 15
  degrees along a 30 x 26 mm crease (the whole stack, like a folded map in a pocket); the print
  follows the sheet: the target materials take the sheet coordinates from before the bend (vertex
  attribute tp), as the protocol does with pp;
- edges follow the structure of the folded sheet: the left edge has two loops of the first fold
  (layers 1-2 and 3-4) with a groove between them, the bottom one loop of the second (1-4 around
  2-3), at the right cut edge there is a gap between layers 1 and 4 (layers 2-3 are 14 mm shorter),
  at the top a notch under the pair 1-2 (layers 3-4 are 20 mm shorter);
- creases: across the "bull" of the target (the paint cracked in a white line), the crease of the bent
  corner and a smoothed crease of the bottom right corner; the protocol was folded in half - a crease
  across the sheet, the sheet tented slightly along it (up to 0.9 mm), the print and the pen worn at
  the fold; a rust mark at the clip, a finger stain at the lifted corner of the protocol;
- holes: in the hole the next layer in shadow and a shadow at the torn edge, around the hole a dent
  (the bullet entry);
- the clip is smoother: 9 segments per bend;
- triangles 992 / 346 (target: 300-1000), atlas 1024: the edges are four parts by side (thin strips
  are their own atlas rectangles, otherwise a round fold facing up would take a rectangle spanning
  the whole stack);
- no vanilla items: DayZ has no paper clip, the pen (Pen) is coloured by the config - a proxy would be
  drawn with the model's default (like cigarette packs), and cartridges or casings on a paper carrier
  would be out of place.

Blender axes: X is the stack width, Y is the height (the top at +Y, the bottom towards the viewer,
-Y), Z is up. The origin is the centre of the stack on the ground: autocenter = 0 (in Geometry),
boundingbox_min at the bottom. Shared dimensions: m67_layout.py (also read by make_decals.py; the
detailing sizes are here and do not change the images).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import m67_layout as ly  # noqa: E402
from mathutils import Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
TARGET_PNG = os.path.join(WORK, "target.png")
HOLES_PNG = os.path.join(WORK, "target_holes.png")
PROTO_PNG = os.path.join(WORK, "protocol.png")
SEL = "camoGround"                 # blue protocol band: the line colour is set by the config (hiddenSelections)

# bend: the bend lines of the bent corner (fractions of DOG_LC), prof: points per edge profile
LOD_SPECS = [dict(lod=0, seg=9, sides=6, bend=(0.0, 1.0), prof=5),
             dict(lod=1, seg=3, sides=4, bend=(0.0, 1.0), prof=3)]

# density: the open part of the target and the protocol matter most; the target under the protocol, the
# bottom and the edges get little
REGIONS = {
    "target": ("target", 3.0), "target_hidden": ("target", 0.35), "target_bottom": ("target_bottom", 1.6),
    "fold": ("fold", 1.6), "cut": ("cut", 1.4),
    "proto": ("proto", 3.4), "proto_under": ("proto_under", 1.2), "proto_edge": ("cut", 0.6),
    "clip": ("clip", 1.6),
}

# --- detailing: bent corner, creases, tented protocol ---------------------------------------------
# the top left corner of the stack is bent up along a crease: DOG_A from the corner along the top edge,
# DOG_B along the left one; the bend is a DOG_LC strip along the crease, beyond it straight at DOG_DEG;
# the axis is the crease on the ground
DOG_A, DOG_B = 0.030, 0.026
DOG_DEG = 15.0
DOG_LC = 0.003
_DL = math.hypot(DOG_A, DOG_B)
DOG_N = (-DOG_B / _DL, DOG_A / _DL)                 # crease normal, towards the corner
DOG_P = (ly.X0, ly.Y1 - DOG_B)                      # the crease point on the left edge
DOG_C = DOG_N[0] * DOG_P[0] + DOG_N[1] * DOG_P[1]

# target creases (top layer, sheet coordinates before the bend): (start, end, relief depth: > 0 is a
# ridge, < 0 a groove, fraction of the length for the ends to fade out). Ends beyond the sheet edge
# mean the crease runs to the edge
CREASES = [
    # diagonally across the "bull" (from the bottom fold towards the protocol, past the holes): the stack
    # was once bent over - the paint cracked in a ragged white line
    ((ly.CX + 0.060, ly.CY - 0.012), (ly.CX + 0.060 + 0.21 * 0.7071, ly.CY - 0.012 + 0.21 * 0.7071), 0.8, 0.15),
    # crease of the bent corner (a groove from above: the corner is bent towards the viewer)
    ((DOG_P[0] - 0.3 * DOG_A, DOG_P[1] - 0.3 * DOG_B), (ly.X0 + 1.3 * DOG_A, ly.Y1 + 0.3 * DOG_B), -0.6, 0.0),
    # smoothed bent corner at the bottom right
    ((ly.X1 - 1.3 * 0.036, ly.Y0 - 0.3 * 0.030), (ly.X1 + 0.3 * 0.036, ly.Y0 + 1.3 * 0.030), -0.4, 0.0),
]

# the protocol was folded in half (A6, for a pocket): a crease across the sheet near the middle, the sheet
# tents along it
PROTO_CREASE, PROTO_CW, PROTO_CH = -0.002, 0.026, 0.0009
# protocol grids (u, v from the sheet centre): lines at the lifted corner and at the crease (PROTO_CREASE +-
# PROTO_CW)
PGRID = {
    0: ([-0.074, -0.020, 0.020, 0.045, 0.074], [-0.105, -0.075, -0.040, -0.028, -0.002, 0.024, 0.105]),
    1: ([-0.074, 0.030, 0.074], [-0.105, -0.050, -0.028, -0.002, 0.024, 0.105]),
}

# stack edge profiles: (height fraction, outward shift, m) from the top to the ground. The left edge is
# the first fold: two loops (layers 1-2 on top, 3-4 below) with a groove between; the bottom is the
# second fold: one loop (1-4 outside, 2-3 inside); the right cut edge is layers 1 and 4 with a gap
# between them (2-3 are 14 mm shorter); the top is the pair 1-2 above, with a notch under it (3-4 are
# 20 mm shorter). The first point is the top edge with no shift
PROFILES = {
    5: {"l": [(1.0, 0.0), (0.76, 0.00045), (0.50, 0.00012), (0.24, 0.00045), (0.0, 0.0001)],
        "b": [(1.0, 0.0), (0.82, 0.00085), (0.50, 0.0011), (0.18, 0.00085), (0.0, 0.0001)],
        "r": [(1.0, 0.0), (0.82, 0.00012), (0.54, -0.0007), (0.26, 0.00005), (0.0, 0.0001)],
        "t": [(1.0, 0.0), (0.74, 0.00012), (0.42, -0.0009), (0.16, -0.0006), (0.0, -0.0003)]},
    3: {"l": [(1.0, 0.0), (0.5, 0.0008), (0.0, 0.0001)],
        "b": [(1.0, 0.0), (0.5, 0.0011), (0.0, 0.0001)],
        "r": [(1.0, 0.0), (0.5, 0.0002), (0.0, 0.0001)],
        "t": [(1.0, 0.0), (0.5, 0.0002), (0.0, 0.0001)]},
}
SIDES = {"l": (-1.0, 0.0), "b": (0.0, -1.0), "r": (1.0, 0.0), "t": (0.0, 1.0)}

# paper colours in "dayz" (sRGB); AGED is how much the yellowed and thumbed paper darkens (almost
# invisible on paint: it is a multiplication): white 236 -> ~212, like light vanilla plastic in look_compare
YELLOW = kmats.lin((196, 184, 150))
SMUDGE = kmats.lin((112, 104, 90))
DUSTC = kmats.lin((150, 142, 126))
CREASE_DIRT = kmats.lin((126, 118, 102))
RUSTC = kmats.lin((132, 88, 50))
FOXING = kmats.lin((150, 112, 72))
AGED = (0.88, 0.85, 0.78, 1.0)


# --- materials ------------------------------------------------------------------------------------
def attr_uv(t, name="pp"):
    a = t.node("ShaderNodeAttribute")
    a.attribute_type = "GEOMETRY"
    a.attribute_name = name
    sep = t.node("ShaderNodeSeparateXYZ")
    t.link(a.outputs["Vector"], sep.inputs[0])
    return sep.outputs["X"], sep.outputs["Y"]


def sheet(t, seed, name="tp"):
    """Sheet coordinates from the vertex attribute (before the corner bend): a vector shifted by seed for
    the noises and separate X, Y, Z - like Tree.coords, but the print and the noises follow the sheet."""
    a = t.node("ShaderNodeAttribute")
    a.attribute_type = "GEOMETRY"
    a.attribute_name = name
    shift = t.node("ShaderNodeVectorMath")
    shift.inputs[1].default_value = (seed * 3.1, seed * 1.7, seed * 0.9)
    t.link(a.outputs["Vector"], shift.inputs[0])
    sep = t.node("ShaderNodeSeparateXYZ")
    t.link(a.outputs["Vector"], sep.inputs[0])
    return shift.outputs[0], sep


def paper_base(t, vec, color, seed_scale=1.0):
    """Target paper: cloudy tone and fibre."""
    cloud = t.maprange(t.noise(vec, 6.0 * seed_scale, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0)
    col = t.mixc(cloud, tuple(c * 0.95 for c in color[:3]) + (1,), color)
    fib = t.noise(t.stretch(vec, 1.0, 0.4, 1.0), 280.0, 3.0, 0.6)
    col = t.mixc(t.math("MULTIPLY", t.maprange(fib, 0.45, 0.8, 0.0, 1.0), 0.12), col,
                 tuple(min(1.0, c * 1.06) for c in color[:3]) + (1,))
    return col, fib


def mulc(t, col, rgba):
    """The colour multiplied by rgba (paper darkens, black paint does not)."""
    m = t.node("ShaderNodeMix")
    m.data_type = "RGBA"
    m.blend_type = "MULTIPLY"
    m.inputs["Factor"].default_value = 1.0
    t.link(col, m.inputs[6])
    m.inputs[7].default_value = rgba
    return m.outputs[2]


def paper_dayz(t, col, vec, ink=None, dust=1.0, smudge=1.0, mottle=1.0, aged=AGED):
    """The "dayz" profile on paper, without streaks and scratches (those belong to metal): the colour is
    muted (the profile's patina), the paper yellowed and thumbed (aged), the tone in blotches - uneven,
    rare rusty specks of old paper, dust in specks (less on paint: grain stands out on black), greasy
    finger spots. In profile v1 the look is not changed."""
    k = kmats.LOOK
    if k["name"] != "dayz":
        return col
    d, v = k["patina"]
    gray = t.node("ShaderNodeRGBToBW")
    t.link(col, gray.inputs[0])
    col = t.mixc(d, col, gray.outputs[0])
    col = t.mixc(1.0 - v, col, (0, 0, 0, 1))
    col = mulc(t, col, aged)
    n1 = t.maprange(t.noise(vec, 6.0, 4.0, 0.55), 0.30, 0.72, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", n1, 0.30 * mottle), col, mulc(t, col, (0.86, 0.80, 0.66, 1.0)))
    n2 = t.maprange(t.noise(vec, 2.2, 3.0, 0.5), 0.35, 0.65, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", n2, 0.08 * mottle), col, (0, 0, 0, 1))
    fox = t.math("MULTIPLY", t.step(t.noise(vec, 150.0, 2.0, 0.5), 0.765, 0.79),
                 t.maprange(t.noise(vec, 3.0, 2.0, 0.5), 0.45, 0.7, 0.0, 0.45 * mottle))
    col = t.mixc(fox, col, FOXING)
    specks = t.step(t.noise(vec, 380.0, 2.0, 0.5), 0.68, 0.74)
    ds = t.math("MULTIPLY", specks, t.maprange(t.noise(vec, 4.5, 3.0, 0.5), 0.35, 0.70, 0.1, 0.45 * dust))
    sm = t.math("MULTIPLY", t.step(t.noise(vec, 8.0, 4.0, 0.5), 0.60, 0.74), 0.20 * smudge)
    if ink is not None:
        # on black paint, light dust and blotches read as stars and haze - almost none there
        ds = t.math("MULTIPLY", ds, t.math("SUBTRACT", 1.0, t.math("MULTIPLY", ink, 0.88)))
        sm = t.math("MULTIPLY", sm, t.math("SUBTRACT", 1.0, t.math("MULTIPLY", ink, 0.8)))
    col = t.mixc(ds, col, DUSTC)
    return t.mixc(sm, col, SMUDGE)


def edge_dirt(t, x, y, vec, width=0.014):
    """0..1 closeness to the edge of the stack (the folds - left and bottom - stronger, the cut edges
    weaker), in blotches."""
    dl = t.maprange(t.math("SUBTRACT", x, ly.X0), 0.0, width, 1.0, 0.0)
    db = t.maprange(t.math("SUBTRACT", y, ly.Y0), 0.0, width, 1.0, 0.0)
    dr = t.maprange(t.math("SUBTRACT", ly.X1, x), 0.0, width * 0.6, 0.6, 0.0)
    dt = t.maprange(t.math("SUBTRACT", ly.Y1, y), 0.0, width * 0.6, 0.6, 0.0)
    e = t.math("MAXIMUM", t.math("MAXIMUM", dl, db), t.math("MAXIMUM", dr, dt))
    return t.math("MULTIPLY", e, t.maprange(t.noise(vec, 34.0, 5.0, 0.6), 0.3, 0.7, 0.45, 1.0))


def crease(t, x, y, vec, a, b, width, halo, ends=0.18, wob=0.0005):
    """Crease along the segment a-b (sheet coordinates, m): line is a narrow fold line of width width, soft
    is the bend around it (halo, stronger towards the line); both fade out towards the ends of the
    segment (the ends fraction of the length); the line wanders slightly (wob) - a fold made by hand,
    not along a ruler."""
    (ax, ay), (bx, by) = a, b
    ln = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / ln, (by - ay) / ln
    dx, dy = t.math("SUBTRACT", x, ax), t.math("SUBTRACT", y, ay)
    par = t.math("ADD", t.math("MULTIPLY", dx, ux), t.math("MULTIPLY", dy, uy))
    ps = t.math("ADD", t.math("MULTIPLY", dx, -uy), t.math("MULTIPLY", dy, ux))
    if wob > 0:
        ps = t.math("ADD", ps, t.math("MULTIPLY", t.math("SUBTRACT", t.noise(vec, 40.0, 2.0, 0.5), 0.5), 2.0 * wob))
    perp = t.math("ABSOLUTE", ps)
    if ends > 0:
        taper = t.math("MULTIPLY", t.maprange(par, 0.0, ends * ln, 0.0, 1.0),
                       t.maprange(par, ln, (1.0 - ends) * ln, 0.0, 1.0))
    else:
        taper = 1.0
    line = t.maprange(perp, 0.0, width, 1.0, 0.0)
    soft = t.maprange(perp, 0.0, halo, 1.0, 0.0)
    soft = t.math("MULTIPLY", soft, soft)
    if not isinstance(taper, float):
        line, soft = t.math("MULTIPLY", line, taper), t.math("MULTIPLY", soft, taper)
    return line, soft


def hole_mask(t, x, v, center, dx=0.0, dy=0.0):
    """Hole mask (hole 1, tears ~0.5) at a sheet point shifted by (dx, dy)."""
    xx = x if dx == 0.0 else t.math("ADD", x, dx)
    vv = v if dy == 0.0 else t.math("ADD", v, dy)
    hc, ha = t.image(HOLES_PNG, xx, vv, center, (ly.SHEET, ly.SHEET))
    return t.math("MULTIPLY", t.bw(hc), ha)


def build_target(mat, origin, bottom=False, fold=False, seed=1.0):
    """Target: the print, holes and marks from target.png by sheet coordinates (attribute tp). The top layer
    uses x, y; the bottom layer (print down, turned back at the second fold) uses x, -y; the folds are
    like the top (the print wraps around the fold), but more worn. The paint is worn off at the edges, on
    the folds and along the creases, the holes have a shadow at the edge and a dent around them, the
    sheet ripples, "dayz" (paper_dayz)."""
    t = kmats.Tree(mat)
    vec, sep = sheet(t, seed)
    x, y = sep.outputs["X"], sep.outputs["Y"]
    col, fib = paper_base(t, vec, kmats.lin(ly.PAPER))
    if bottom:
        v = t.math("MULTIPLY", y, -1.0)
        center = (ly.CX, -ly.CY + 2 * ly.FOLD_B)
    else:
        v = y
        center = (ly.CX, ly.CY)
    c, a = t.image(TARGET_PNG, x, v, center, (ly.SHEET, ly.SHEET))
    hole = hole_mask(t, x, v, center)
    e = edge_dirt(t, x, y, vec, 0.008 if fold else 0.006)
    # the paint wears off: at the edges of the stack, on the fold, along the creases (a crack in patches)
    wear = t.math("MULTIPLY", e, 0.15)
    h_extra, line_all, rub = None, None, None
    if fold:
        rub = t.maprange(t.noise(t.stretch(vec, 1.0, 1.0, 0.2), 70.0, 5.0, 0.7), 0.45, 0.75, 0.0, 0.4)
        wear = t.math("MAXIMUM", wear, t.math("MULTIPLY", rub, 1.2))
    elif not bottom:
        # the paint crack along the crease is ragged: the paint holds in places
        brk = t.maprange(t.noise(vec, 160.0, 3.0, 0.6), 0.42, 0.58, 0.0, 1.0)
        for pa, pb, depth, ends in CREASES:
            line, soft = crease(t, x, y, vec, pa, pb, 0.0003, 0.004, ends)
            wear = t.math("MAXIMUM", wear, t.math("MULTIPLY", line, t.math("MULTIPLY", brk, 0.85)))
            line_all = line if line_all is None else t.math("MAXIMUM", line_all, line)
            hs = t.math("MULTIPLY", t.math("ADD", soft, t.math("MULTIPLY", line, 0.5)), depth)
            h_extra = hs if h_extra is None else t.math("ADD", h_extra, hs)
    if kmats.LOOK["name"] == "dayz":
        # the print is worn in places (rubbed by a pocket and hands): black lightens slightly in small patches
        # (3 % of paper on black is already visible, 14 % read as haze)
        wear = t.math("MAXIMUM", wear, t.maprange(t.noise(vec, 40.0, 4.0, 0.6), 0.56, 0.78, 0.0, 0.03))
    keep = t.math("SUBTRACT", 1.0, t.math("MULTIPLY", wear, t.math("SUBTRACT", 1.0, hole)))
    ka = t.math("MULTIPLY", a, keep)
    col = t.mixc(ka, col, c)
    ink = t.math("MULTIPLY", ka, t.math("SUBTRACT", 1.0, hole))
    h_hole = t.math("MULTIPLY", hole, -0.6)
    if not fold:
        # holes: the hole edges come from neighbouring samples of the mask (+-0.8 mm): inside at the edge, the
        # shadow of the torn rim; around it, a dent (the paper was pressed in along the bullet path); in the
        # hole, the next layer in shadow
        ero, dil = hole, hole
        for dx, dy in ((0.001, 0.0), (-0.001, 0.0), (0.0, 0.001), (0.0, -0.001)):
            m2 = hole_mask(t, x, v, center, dx, dy)
            ero = t.math("MINIMUM", ero, m2)
            dil = t.math("MAXIMUM", dil, m2)
        inner = t.math("MAXIMUM", t.math("SUBTRACT", hole, ero), 0.0)
        outer = t.math("MAXIMUM", t.math("SUBTRACT", dil, hole), 0.0)
        core = t.step(hole, 0.75, 0.95)
        col = t.mixc(t.math("MULTIPLY", core, 0.32), col, (0, 0, 0, 1))
        col = t.mixc(t.math("MULTIPLY", inner, 0.50), col, kmats.lin((52, 48, 42)))
        col = t.mixc(t.math("MULTIPLY", outer, 0.12), col, kmats.lin((90, 86, 80)))
        h_hole = t.math("SUBTRACT", h_hole, t.math("MULTIPLY", outer, 0.25))
    # yellowed and thumbed towards the edges; yellowing is barely visible on black paint
    yk = t.math("SUBTRACT", 1.0, t.math("MULTIPLY", ink, 0.8))
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", e, 0.5 if fold else 0.35), yk), col, YELLOW)
    if kmats.LOOK["name"] == "dayz":
        col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", e, 0.30), yk), col, SMUDGE)
    if rub is not None:
        col = t.mixc(rub, col, kmats.lin((150, 146, 136)))
    if line_all is not None:
        col = t.mixc(t.math("MULTIPLY", line_all, 0.15), col, CREASE_DIRT)
    if not fold and not bottom:
        # hand marks: at the right cut edge (the folded target is held by it) and at the bent corner
        hr = t.maprange(t.math("SUBTRACT", ly.X1, x), 0.0, 0.045, 1.0, 0.0)
        dd = t.math("ADD", t.math("MULTIPLY", t.math("SUBTRACT", x, DOG_P[0]), DOG_N[0]),
                    t.math("MULTIPLY", t.math("SUBTRACT", y, DOG_P[1]), DOG_N[1]))
        hd = t.maprange(dd, -0.022, 0.006, 0.0, 1.0)
        hands = t.math("MULTIPLY", t.math("MAXIMUM", hr, hd), t.step(t.noise(vec, 16.0, 3.0, 0.5), 0.42, 0.66))
        col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", hands, 0.26), yk), col, SMUDGE)
    col = paper_dayz(t, col, vec, ink=ink, dust=0.6 if fold else 1.0, smudge=0.6 if bottom else 1.0)
    gl = t.math("ADD", 0.07, t.math("MULTIPLY", ink, 0.02))
    # fibre only barely: on black paint the relief glints like sandpaper; the sheet ripple is gentle waves
    h = t.math("ADD", t.math("MULTIPLY", fib, t.math("SUBTRACT", 0.012, t.math("MULTIPLY", ink, 0.010))), h_hole)
    if not fold:
        h = t.math("ADD", h, t.math("MULTIPLY", t.math("SUBTRACT", t.noise(vec, 9.0, 2.0, 0.5), 0.5), 1.6))
    if h_extra is not None:
        h = t.math("ADD", h, h_extra)
    return kmats.out(t, col, t.math("MULTIPLY", gl, t.math("SUBTRACT", 1.0, hole)), 0.05, h)


def build_cut(mat, origin, seed=3.0):
    """Cut edges and rims: paper layers as thin strips along, the rims darkened by hands."""
    t = kmats.Tree(mat)
    vec, sep = sheet(t, seed)
    layers = t.noise(t.stretch(vec, 1.0, 1.0, 60.0), 40.0, 3.0, 0.5)
    col = t.mixc(t.maprange(layers, 0.35, 0.65, 0.0, 1.0), kmats.lin((198, 194, 182)), kmats.lin((232, 228, 216)))
    col = t.mixc(t.math("MULTIPLY", t.maprange(t.noise(vec, 25.0, 5.0, 0.6), 0.4, 0.75, 0.0, 1.0), 0.4), col,
                 kmats.lin((160, 150, 128)))
    col = paper_dayz(t, col, vec, dust=0.3, smudge=1.3)
    return kmats.out(t, col, 0.05, 0.03, t.math("MULTIPLY", layers, 0.2))


def build_proto(mat, origin, under=False, seed=4.0):
    """Protocol from the image in sheet axes (attribute pp). The back is lighter, the print barely shows
    through (mirrored). A crease across the sheet (the print worn off on it), a rust mark of the clip, a
    finger stain at the lifted corner, "dayz" (paper_dayz)."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    u, v = attr_uv(t)
    col, fib = paper_base(t, vec, kmats.lin(ly.PROTO_PAPER), 1.3)
    size = (-ly.PROTO_W if under else ly.PROTO_W, ly.PROTO_H)
    c, a = t.image(PROTO_PNG, u, v, (0.0, 0.0), size)
    # crease: the sheet was folded in half - the print is worn off along the line, dirt in it; a relief
    # ridge around
    dv = t.math("ABSOLUTE", t.math("SUBTRACT", v, PROTO_CREASE))
    line = t.maprange(dv, 0.0, 0.0007, 1.0, 0.0)
    soft = t.maprange(dv, 0.0, 0.007, 1.0, 0.0)
    soft = t.math("MULTIPLY", soft, soft)
    brk = t.maprange(t.noise(vec, 260.0, 2.0, 0.5), 0.35, 0.62, 0.25, 1.0)
    keep = t.math("SUBTRACT", 1.0, t.math("MULTIPLY", line, t.math("MULTIPLY", brk, 0.75)))
    pa = t.math("MULTIPLY", a, 0.10) if under else t.math("MULTIPLY", a, keep)
    col = t.mixc(pa, col, c)
    # yellowing towards the sheet edges
    du = t.math("SUBTRACT", ly.PROTO_W / 2, t.math("ABSOLUTE", u))
    dv2 = t.math("SUBTRACT", ly.PROTO_H / 2, t.math("ABSOLUTE", v))
    e = t.maprange(t.math("MINIMUM", du, dv2), 0.0, 0.008, 1.0, 0.0)
    e = t.math("MULTIPLY", e, t.maprange(t.noise(vec, 40.0, 5.0, 0.6), 0.3, 0.7, 0.4, 1.0))
    col = t.mixc(t.math("MULTIPLY", e, 0.35), col, kmats.lin((206, 196, 160)))
    col = t.mixc(t.math("MULTIPLY", line, 0.16), col, CREASE_DIRT)
    if not under:
        # rust mark around the outer loop of the clip (the sheet got damp): a band along the loop outline in
        # clip axes (a from the sheet edge inwards, b across; the clip is rotated by 4 degrees, as in clip_path)
        ca, sa = math.cos(math.radians(4.0)), math.sin(math.radians(4.0))
        du = t.math("SUBTRACT", u, ly.CLIP_U)
        dve = t.math("SUBTRACT", ly.PROTO_H / 2, v)
        ka_ = t.math("SUBTRACT", t.math("MULTIPLY", dve, ca), t.math("MULTIPLY", du, sa))
        kb_ = t.math("ADD", t.math("MULTIPLY", du, ca), t.math("MULTIPLY", dve, sa))
        ra = t.math("SUBTRACT", t.math("ABSOLUTE", t.math("SUBTRACT", ka_, 0.0131)), 0.0138)
        rb = t.math("SUBTRACT", t.math("ABSOLUTE", kb_), 0.0039)
        ring = t.maprange(t.math("ABSOLUTE", t.math("MAXIMUM", ra, rb)), 0.0, 0.0018, 1.0, 0.0)
        rust = t.math("MULTIPLY", ring, t.maprange(t.noise(vec, 140.0, 3.0, 0.6), 0.32, 0.62, 0.15, 1.0))
        col = t.mixc(t.math("MULTIPLY", rust, 0.50), col, RUSTC)
        # finger stain at the lifted corner (the protocol is lifted by it)
        fu = t.math("SUBTRACT", u, 0.060)
        fv = t.math("SUBTRACT", v, -0.092)
        fr = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", fu, fu), t.math("MULTIPLY", fv, fv)))
        fing = t.math("MULTIPLY", t.maprange(fr, 0.004, 0.022, 1.0, 0.0),
                      t.maprange(t.noise(vec, 60.0, 4.0, 0.6), 0.35, 0.65, 0.3, 1.0))
        col = t.mixc(t.math("MULTIPLY", fing, 0.32), col, SMUDGE)
    col = paper_dayz(t, col, vec, ink=None if under else a, dust=0.4 if under else 0.8,
                     smudge=0.5 if under else 0.9, aged=(0.90, 0.88, 0.81, 1.0))
    gl = 0.07 if under else t.math("ADD", 0.08, t.math("MULTIPLY", a, 0.06))
    h = t.math("MULTIPLY", fib, 0.05)
    if not under:
        h = t.math("ADD", h, t.math("MULTIPLY", soft, 0.7))
        h = t.math("ADD", h, t.math("MULTIPLY", t.math("SUBTRACT", t.noise(vec, 12.0, 2.0, 0.5), 0.5), 1.0))
    return kmats.out(t, col, gl, 0.05, h)


KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "target": (build_target, dict(seed=1.1)),
    "target_bottom": (build_target, dict(bottom=True, seed=1.7)),
    "fold": (build_target, dict(fold=True, seed=2.1)),
    "cut": (build_cut, dict(seed=3.4)),
    "proto": (build_proto, dict(seed=4.2)),
    "proto_under": (build_proto, dict(under=True, seed=4.8)),
    "clip": ("steel", dict(seed=5.5, tone=0.46, along="x", gloss=0.62, spec=0.8, dust=0.05, grime=0.15)),
})

OBJ, NAME = "m67_carrier_ball", "ozr_carrier_ball"
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 rvmat=dict(specular=1.0, power=40.0), selections=(SEL,), hidden=(SEL,))
BOUNDS = {}


def P(name, region, **kw):
    p = M.part(name, region, **kw)
    for r in REGIONS:
        p.region_index(r, *REGIONS[r])
    return p


def face(p, verts, region, want):
    f = p.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    f[p.reg] = p.region_index(region)
    return f


def set_attr(p, name, fn):
    lay = p.bm.verts.layers.float_vector.get(name) or p.bm.verts.layers.float_vector.new(name)
    for v in p.bm.verts:
        v[lay] = fn(v.co)


def set_pp(p, fn):
    def pp(co):
        a, b = fn(co)
        return (a, b, 0.0)
    set_attr(p, "pp", pp)


def poly_area(poly):
    return 0.5 * sum(poly[k][0] * poly[(k + 1) % len(poly)][1] - poly[(k + 1) % len(poly)][0] * poly[k][1]
                     for k in range(len(poly)))


# --- bent corner ----------------------------------------------------------------------------------
def dog_d(x, y):
    """Distance from the crease of the bent corner towards the corner (> 0 is the bent part)."""
    return (x - DOG_P[0]) * DOG_N[0] + (y - DOG_P[1]) * DOG_N[1]


def bend(co):
    """A sheet point before the bend (z is the height above the ground) -> after: the corner beyond the
    crease is rotated up about the crease on the ground; the strip 0 < d < DOG_LC is bent in an arc of
    radius DOG_LC / angle, beyond it straight."""
    d = dog_d(co[0], co[1])
    if d <= 0.0:
        return Vector(co)
    th = math.radians(DOG_DEG)
    r = DOG_LC / th
    z = co[2]
    if d <= DOG_LC:
        f = d / r
        dd = (r - z) * math.sin(f)
        zz = r * (1.0 - math.cos(f)) + z * math.cos(f)
    else:
        dd = r * math.sin(th) + (d - DOG_LC) * math.cos(th) - z * math.sin(th)
        zz = r * (1.0 - math.cos(th)) + (d - DOG_LC) * math.sin(th) + z * math.cos(th)
    return Vector((co[0] + (dd - d) * DOG_N[0], co[1] + (dd - d) * DOG_N[1], zz))


def split_bend(poly, lines):
    """Polygon (x, y) -> pieces split along the bend lines d = lines[k] (from the crease towards the
    corner), without degenerate ones."""
    out, rest = [], poly
    for dk in lines:
        below = clip_poly(rest, DOG_N, DOG_C + dk, True)
        if len(below) >= 3 and abs(poly_area(below)) > 1e-9:
            out.append(below)
        rest = clip_poly(rest, DOG_N, DOG_C + dk, False)
        if len(rest) < 3 or abs(poly_area(rest)) <= 1e-9:
            return out
    out.append(rest)
    return out


class Verts:
    """Part vertices by the sheet point before the bend: the attribute tp is the sheet point (the print
    follows it), the vertex itself is after the corner bend (bend). Identical points make a single vertex."""

    def __init__(self, p):
        self.p = p
        self.lay = p.bm.verts.layers.float_vector.get("tp") or p.bm.verts.layers.float_vector.new("tp")
        self.cache = {}

    def __call__(self, x, y, z):
        k = (round(x, 7), round(y, 7), round(z, 7))
        if k not in self.cache:
            vt = self.p.bm.verts.new(bend((x, y, z)))
            vt[self.lay] = (x, y, z)
            self.cache[k] = vt
        return self.cache[k]


# --- target stack ---------------------------------------------------------------------------------
# the top of the stack is split into parts with their own atlas rectangles: the middle under the
# protocol gets almost no texels (it is visible only under the lifted corner of the protocol)
HIDDEN = (-0.020, 0.080, -0.040, ly.Y1 - 0.014)


def top_piece(x, y):
    x0, x1, y0, y1 = HIDDEN
    if x < x0:
        return "tgt_left"
    if y < y0:
        return "tgt_low"
    if x > x1:
        return "tgt_right"
    if y > y1:
        return "tgt_top"
    return "tgt_hidden"


def ring_points(xs, ys, lines):
    """Edge of the stack counter-clockwise (seen from above): grid points and the intersections of the bend
    lines of the bent corner with the top and left edges."""
    x0, x1, y0, y1 = xs[0], xs[-1], ys[0], ys[-1]

    def desc(vals):
        res = []
        for q in sorted(vals, reverse=True):
            if not res or abs(res[-1] - q) > 1e-7:
                res.append(q)
        return res
    top_x = [x0 + DOG_A - dk * _DL / DOG_B for dk in lines]
    left_y = [y1 - DOG_B + dk * _DL / DOG_A for dk in lines]
    pts = [(x, y0) for x in xs[:-1]] + [(x1, y) for y in ys[:-1]]
    pts += [(x, y1) for x in desc(list(xs[1:]) + top_x)]
    pts += [(x0, y) for y in desc(list(ys[1:]) + left_y)]
    return pts


def sides_of(x, y):
    s = []
    for name, ok in (("l", abs(x - ly.X0) < 1e-9), ("b", abs(y - ly.Y0) < 1e-9),
                     ("r", abs(x - ly.X1) < 1e-9), ("t", abs(y - ly.Y1) < 1e-9)):
        if ok:
            s.append(name)
    return s


def edge_profile(sides, prof):
    """Rim profile at an edge point: at a corner, the average of the two sides, the shift along the bisector."""
    rows = [prof[s] for s in sides]
    dx = sum(SIDES[s][0] for s in sides)
    dy = sum(SIDES[s][1] for s in sides)
    m = math.hypot(dx, dy)
    pr = [(sum(r[k][0] for r in rows) / len(rows), sum(r[k][1] for r in rows) / len(rows))
          for k in range(len(rows[0]))]
    return pr, (dx / m, dy / m)


def build_packet(spec):
    lod = spec["lod"]
    xs, ys = ly.GRID[lod]
    lines = [DOG_LC * f for f in spec["bend"]]
    nx, ny = len(xs) - 1, len(ys) - 1
    pieces, vmaps = {}, {}
    for i in range(nx):
        for j in range(ny):
            cx, cy = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
            name = top_piece(cx, cy)
            if name not in pieces:
                pieces[name] = P(name, "target")
                vmaps[name] = Verts(pieces[name])
            pc, V = pieces[name], vmaps[name]
            cell = [(xs[i], ys[j]), (xs[i + 1], ys[j]), (xs[i + 1], ys[j + 1]), (xs[i], ys[j + 1])]
            for poly in split_bend(cell, lines):
                face(pc, [V(px, py, ly.z_top(px, py)) for px, py in poly],
                     "target_hidden" if name == "tgt_hidden" else "target", (0, 0, 1))
    # rims: a part of its own per side (thin strips are their own atlas rectangles): folds at the left and
    # bottom as loops, cut edges at the right and top with a gap and a notch between the layers
    prof = PROFILES[spec["prof"]]
    edges = {}
    for s in SIDES:
        ep = P("edge_" + s, "fold" if s in "lb" else "cut")
        edges[s] = (ep, Verts(ep))
    ring = ring_points(xs, ys, lines)
    profs = []
    for x, y in ring:
        sd = sides_of(x, y)
        pr, (dx, dy) = edge_profile(sd, prof)
        zt = ly.z_top(x, y)
        profs.append((sd, [(x + dx * o, y + dy * o, zt * zf) for zf, o in pr]))
    n = len(ring)
    for k in range(n):
        (s0, q0), (s1, q1) = profs[k], profs[(k + 1) % n]
        side = [s for s in s0 if s in s1][0]
        ep, V = edges[side]
        region = "fold" if side in "lb" else "cut"
        want = (SIDES[side][0], SIDES[side][1], 0.0)
        for m in range(len(q0) - 1):
            face(ep, [V(*q0[m]), V(*q1[m]), V(*q1[m + 1]), V(*q0[m + 1])], region, want)
    # bottom: the main part is a fan from the centre (many points on one line along the edge, a polygon
    # would give degenerate faces), the bend strips and the bent corner are fans from their own middle
    pk = P("packet", "target_bottom")
    VB = Verts(pk)
    outline = [(q[-1][0], q[-1][1]) for _, q in profs]
    for idx, piece in enumerate(split_bend(outline, lines)):
        if idx == 0:
            c = VB(0.0, 0.0, 0.0)
        else:
            c = VB(sum(q[0] for q in piece) / len(piece), sum(q[1] for q in piece) / len(piece), 0.0)
        m = len(piece)
        for k in range(m):
            q0, q1 = piece[k], piece[(k + 1) % m]
            if math.dist(q0, q1) < 1e-7:
                continue
            face(pk, [c, VB(q1[0], q1[1], 0.0), VB(q0[0], q0[1], 0.0)], "target_bottom", (0, 0, -1))
    return list(pieces.values()) + [edges[s][0] for s in SIDES] + [pk]


def packet_top_z(lod, x, y):
    """Top of the stack of a LOD at the point (x, y): bilinear over its grid. Beyond the stack is the
    ground. The bent corner is far from the protocol and not needed here."""
    xs, ys = ly.GRID[lod]
    if not (ly.X0 <= x <= ly.X1 and ly.Y0 <= y <= ly.Y1):
        return 0.0
    i = max(0, min(len(xs) - 2, sum(1 for v in xs[1:-1] if v <= x)))
    j = max(0, min(len(ys) - 2, sum(1 for v in ys[1:-1] if v <= y)))
    fx = (x - xs[i]) / (xs[i + 1] - xs[i])
    fy = (y - ys[j]) / (ys[j + 1] - ys[j])
    z = ly.z_top
    z00, z10, z01, z11 = z(xs[i], ys[j]), z(xs[i + 1], ys[j]), z(xs[i], ys[j + 1]), z(xs[i + 1], ys[j + 1])
    return (z00 * (1 - fx) + z10 * fx) * (1 - fy) + (z01 * (1 - fx) + z11 * fx) * fy


def proto_rest():
    """The plane of the protocol bottom in its axes: z = a + b*u + c*v - the lowest (at the sheet centre) of
    those above the stack top of both LODs at all points of the sheet: the protocol rests on the layers
    that have drifted apart at the cut edges and does not sink into the target in either LOD."""
    pts = []
    for iu in range(25):
        for iv in range(31):
            u = -ly.PROTO_W / 2 + ly.PROTO_W * iu / 24
            v = -ly.PROTO_H / 2 + ly.PROTO_H * iv / 30
            x, y = ly.proto_world(u, v)
            pts.append((u, v, max(packet_top_z(0, x, y), packet_top_z(1, x, y))))
    best = None
    for ib in range(-30, 31):
        for ic in range(-30, 31):
            b, c = ib * 0.0004, ic * 0.0004
            a = max(s - b * u - c * v for u, v, s in pts)
            if best is None or a < best[0]:
                best = (a, b, c)
    a, b, c = best
    print("protocol rests at z %.4f, slope u %.4f v %.4f" % (a, b, c))
    return (a + 0.00006, b, c)


REST = None


def proto_tent(u, v):
    """The protocol tented along the crease: only upwards from the plane, so it does not sink into the
    target."""
    return PROTO_CH * max(0.0, 1.0 - abs(v - PROTO_CREASE) / PROTO_CW)


def proto_z(u, v):
    """Centre line of the protocol sheet."""
    a, b, c = REST
    return a + b * u + c * v + ly.PROTO_T / 2 + ly.proto_lift(u, v) + proto_tent(u, v)


def clip_poly(poly, nrm, d0, keep_less):
    """Clip a convex polygon [(u, v)] by the half-plane n.p < d0 (keep_less) or n.p > d0."""
    def val(p):
        s = nrm[0] * p[0] + nrm[1] * p[1] - d0
        return -s if keep_less else s
    out = []
    for k in range(len(poly)):
        p, q = poly[k], poly[(k + 1) % len(poly)]
        vp, vq = val(p), val(q)
        if vp >= 0:
            out.append(p)
        if (vp >= 0) != (vq >= 0):
            tt = vp / (vp - vq)
            out.append((p[0] + (q[0] - p[0]) * tt, p[1] + (q[1] - p[1]) * tt))
    # a point exactly on the cut line is included twice - remove adjacent duplicates
    res = []
    for q in out:
        if not res or math.dist(q, res[-1]) > 1e-7:
            res.append(q)
    if len(res) > 1 and math.dist(res[0], res[-1]) <= 1e-7:
        res.pop()
    return res


def build_proto(spec):
    """Protocol: the top is a sheet over a grid cut along the edges of the blue band (the band is a part of
    its own, camoGround, but in the same atlas rectangle), the back, the rim along the outline."""
    global REST
    if REST is None:
        REST = proto_rest()
    lod = spec["lod"]
    us, vs = PGRID[lod]
    pr = P("proto", "proto")
    bd = P("band", "proto", group=SEL, uv_name="proto")
    a = math.radians(ly.BAND_ANG)
    nrm = (-math.sin(a), math.cos(a))
    hw = ly.BAND_W / 2
    h = ly.PROTO_T / 2
    cache = {}

    def V(p, uv, dz):
        k = (p.name, round(uv[0], 7), round(uv[1], 7), dz)
        if k not in cache:
            x, y = ly.proto_world(*uv)
            cache[k] = p.bm.verts.new((x, y, proto_z(*uv) + dz))
        return cache[k]
    for i in range(len(us) - 1):
        for j in range(len(vs) - 1):
            cell = [(us[i], vs[j]), (us[i + 1], vs[j]), (us[i + 1], vs[j + 1]), (us[i], vs[j + 1])]
            for p, polys in ((pr, [clip_poly(cell, nrm, -hw, True), clip_poly(cell, nrm, hw, False)]),
                             (bd, [clip_poly(clip_poly(cell, nrm, -hw, False), nrm, hw, True)])):
                for poly in polys:
                    if len(poly) < 3:
                        continue
                    if abs(poly_area(poly)) < 1e-8:
                        continue
                    face(p, [V(p, q, h) for q in poly], "proto", (0, 0, 1))
            face(pr, [V(pr, q, -h) for q in cell], "proto_under", (0, 0, -1))
    # rim along the outline: grid points and the intersections of the band edges with the outline
    ring = []
    corners = [(-ly.PROTO_W / 2, -ly.PROTO_H / 2), (ly.PROTO_W / 2, -ly.PROTO_H / 2),
               (ly.PROTO_W / 2, ly.PROTO_H / 2), (-ly.PROTO_W / 2, ly.PROTO_H / 2)]
    for k in range(4):
        p0, p1 = corners[k], corners[(k + 1) % 4]
        if p0[1] == p1[1]:
            ts = sorted({(u - p0[0]) / (p1[0] - p0[0]) for u in us})
        else:
            ts = sorted({(v - p0[1]) / (p1[1] - p0[1]) for v in vs})
        for d0 in (-hw, hw):
            s0 = nrm[0] * p0[0] + nrm[1] * p0[1] - d0
            s1 = nrm[0] * p1[0] + nrm[1] * p1[1] - d0
            if (s0 < 0) != (s1 < 0):
                ts.append(s0 / (s0 - s1))
        for tt in sorted(t for t in set(ts) if 0.0 <= t < 1.0 - 1e-9):
            ring.append((p0[0] + (p1[0] - p0[0]) * tt, p0[1] + (p1[1] - p0[1]) * tt))
    n = len(ring)
    for k in range(n):
        q0, q1 = ring[k], ring[(k + 1) % n]
        mu, mv = (q0[0] + q1[0]) / 2, (q0[1] + q1[1]) / 2
        want = Vector((*ly.proto_world(mu, mv), 0.0)) - Vector((*ly.proto_world(0.0, 0.0), 0.0))
        face(pr, [V(pr, q0, h), V(pr, q1, h), V(pr, q1, -h), V(pr, q0, -h)], "proto_edge", tuple(want))
    for p in (pr, bd):
        set_pp(p, lambda co: ly.proto_local(co.x, co.y))
        # the protocol rim uses the cut-edge material: the sheet coordinates (tp) are the point itself
        set_attr(p, "tp", lambda co: (co.x, co.y, co.z))
    return [pr, bd]


# --- paper clip -----------------------------------------------------------------------------------
def clip_path(seg):
    """Wire axis of the "Gem" clip in protocol axes (u, v, z): the outer loop lies on the sheet, the bend at
    the edge goes under the sheet. a is from the sheet edge inwards (along -v), b is across (along u)."""
    L, W, r = ly.CLIP_L, ly.CLIP_W, ly.CLIP_R
    edge_v = ly.PROTO_H / 2
    u0 = ly.CLIP_U
    tilt = math.radians(4.0)                        # the clip was put on not strictly across the edge
    R1 = W / 2 - r                                  # the large bend of the outer loop
    R3 = 2.5e-3 - r                                 # bend at the edge: it wraps the sheet
    a_out = -0.0007                                 # the extreme point of the bend, beyond the sheet edge

    def to_uv(a, b):
        ca, sa = math.cos(tilt), math.sin(tilt)
        return u0 + b * ca - a * sa, edge_v - a * ca - b * sa
    z_top = lambda a, b: proto_z(*to_uv(a, b)) + ly.PROTO_T / 2 + r      # noqa: E731
    pts = []
    # leg 1 (the free end ~3/4 of the length from the large bend) -> large bend -> leg 2
    a_far = L - W / 2 + a_out
    pts.append((0.0072, -R1))
    for k in range(seg + 1):
        f = math.pi * k / seg
        pts.append((a_far + R1 * math.sin(f), -R1 * math.cos(f)))
    # leg 2 leads to the edge, the bend R3 at the edge (centre at b = R1 - R3) goes down
    out = [(*to_uv(a, b), z_top(a, b)) for a, b in pts]
    bc = R1 - R3
    a_c = a_out + R3
    z0 = z_top(a_c, R1)
    z1 = REST[0] - 0.0001 - r                        # under the top layer of the target
    for k in range(seg + 1):
        f = math.pi * k / seg
        a = a_c - R3 * math.sin(f)
        b = bc + R3 * math.cos(f)
        s = (1 - math.cos(f)) / 2
        out.append((*to_uv(a, b), z0 + (z1 - z0) * s))
    # a short tail under the sheet (the inner loop is not visible further on)
    a, b = a_c + 0.003, bc - R3
    out.append((*to_uv(a, b), z1))
    return out


def build_clip(spec):
    cp = P("clip", "clip")
    pts = []
    for u, v, z in clip_path(spec["seg"]):
        x, y = ly.proto_world(u, v)
        pts.append((x, y, z))
    g.pipe(cp, pts, ly.CLIP_R, spec["sides"])
    for f in cp.bm.faces:
        f[cp.reg] = cp.region_index("clip")
    return [cp]


def build_lod(spec):
    parts = build_packet(spec) + build_proto(spec) + build_clip(spec)
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        BOUNDS["pts"] = [tuple(v) for v in vs]
    return parts


def preview_aspect(bbox, cam):
    """Width / height of the preview frame from camera cam onto the centre (a 2x2 cell gives about 1)."""
    x0, x1, y0, y1, z0, z1 = bbox
    c = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    d = (c - Vector(cam)).normalized()
    right = d.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(d).normalized()
    pts = [Vector(q) - c for q in kx.box_pts(*bbox)]
    w = max(q.dot(right) for q in pts) - min(q.dot(right) for q in pts)
    h = max(q.dot(up) for q in pts) - min(q.dot(up) for q in pts)
    return w / h


INV_VIEW = (-0.03, -0.20, 0.55)


def collision():
    """One convex hull over the vertices of the near LOD. The mass is the class weight, 0.3 kg
    (OZL_Carrier_Base); the hit sound and penetration are thin fabric, as for the vanilla book
    (Book_kniga.p3d: fabric_thin) and the M62-M64 carriers."""
    comps = [(BOUNDS["pts"], kx.PEN + r"\fabric_thin.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    c = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, hi[2] / 2)
    memory = {
        # inventory preview camera: from the front and above - the centre of the target with the holes
        # closer, the protocol farther
        "invView": [INV_VIEW],
        "ce_center": [c],
        "ce_radius": [(c[0] + 0.5 * math.dist(lo, hi), c[1], c[2])],
    }
    print("bbox %.4f..%.4f x %.4f..%.4f x 0..%.4f, preview aspect from invView %.2f (2x2 cell: ~1)"
          % (lo[0], hi[0], lo[1], hi[1], hi[2], preview_aspect(bbox, INV_VIEW)))
    return comps, 0.3, memory, bbox


# camera angles: the first M.look_shots[0] are the --look preview (general view, holes, bent corner,
# clip, protocol corner, inventory view), the rest only in the grey-form and textured renders
SHOTS = [
    ("front", (-0.20, -0.46, 0.30), (0.0, 0.0, 0.002), 45),
    ("holes", (-0.21, -0.27, 0.16), (-0.085, -0.085, 0.002), 50),
    ("dogear", (-0.27, -0.03, 0.07), (-0.122, 0.118, 0.004), 55),
    ("clip", (0.13, 0.03, 0.10), (0.077, 0.128, 0.002), 55),
    ("corner", (0.26, -0.24, 0.07), (0.10, -0.07, 0.003), 50),
    ("inv", INV_VIEW, (0.0, 0.0, 0.002), 36),
    ("top", (0.0, 0.0, 0.72), (0.0, 0.0, 0.0), 40),
]
M.look_shots = (6, 2)

if __name__ == "__main__":
    M.run(build_lod, collision, SHOTS, row_step=0.32, row_shot=((0.16, -0.75, 0.55), (0.16, 0.0, 0.0)))
