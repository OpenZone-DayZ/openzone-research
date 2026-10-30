"""M62 - "Bio" carrier (OZL_Carrier_Bio): the carrier of the "Bio" line, shared by the factions - a
cardboard binder folder with analysis results: forms are bound in, an analyser printer tape folded
accordion-style is tucked in on top and sticks out of the folder; the folder is tied. A portable
2x2 item.

    blender --background --python build_m62.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (cover print, relief, label, form,
tape).

Target: ~22 x 30.5 x 1 cm (27 x 37 with the tape and the bow); a cardboard cover (camoGround), a
metal binder, 5-8 form sheets with fields and digits, a narrow thermal tape ~5 cm sticking out of the
folder, ties; 200-400 g, 300-1500 triangles (a small item), texture 512-1024; the paper has no
readable text.

Reference and sizes:
- folder: cardboard "Delo" A4 with a binder (a Soviet reference with printed rules; the size is not
  given there, estimated 23 x 32). Catalogue "Delo" folders: BRAUBERG 110923 and 128987 - 305 x 220 mm,
  spine 22-25 mm, board 280-440 g/m2 (~0.3-0.6 mm); OfficeSpace 257305 - 310 x 220. Taken: 305 x 220,
  board 0.7 mm (for looks), i.e. 22 x 30.5 cm.
- binder: metal prongs with a clamping bar on the back cover, holes per ISO 838 (80 mm, 12 mm from
  the sheet edge); the bar ~110 x 13 mm is an estimate. Under the closed cover it shows as relief:
  the bar and prongs push the board out (relief: make_decals.py, cover_height.png).
- forms: A4 (210 x 297), 8 sheets on the binder; one more lies on top, not bound, and peeks out from
  under the bottom of the cover by 20-30 mm: total boxes with digits, a signature flourish, a stamp.
- tape: thermal paper 57 mm (the standard width of till and instrument thermal printers, e.g. MPRINT
  G58 for Laktan 1-4M analysers; in M02 the tape is eyeballed at 50 mm), folded accordion-style at
  105 mm, 7 layers; the accordion sticks out past the top edge by 35 mm, outside the layers spring
  open in a fan (the folds are visible from above), the free end (the head of the printout) comes
  out from under the bottom layer and lies on the ground. Print: a 5 x 7 dot matrix, columns of
  digits per sample (in the style of a spectrophotometer printout; no close-up of an analyser's own
  tape was found).
- ties: 8 mm cotton tape, a bow at the middle of the open edge; the loops lie on the cover, the ends
  hang down to the ground.
- cover: green pressboard (the colour of the "Bio" line, like the green tube caps of M47) - the
  camoGround selection: front, spine, back. The front has printed rules (like "Delo", wordless),
  spine creases and a 90 x 60 mm paper label: biohazard sign, fields with a handwritten sample
  number, a violet stamp without text. The label, forms, tape and ribbon are not camoGround: they stay
  when the cover is recoloured.

Marks: the biohazard sign, stamps without text, fields and digits. State: `used but intact`. There
are no lamps, screens or moving parts, and it is not a machine: the carrier has no working state, so
there is no "work" view (OZL_Work). LODs (a small item): near and middle, no far one.

Detailing:
- "dayz" look: matte, more worn; the profile's dirt layers (blotches, scratches, streaks) are finer
  on a 30 cm folder (SMALL) and weaker on paper (PAPER_LOOK) - the look_tweak function, the kit is
  untouched;
- cover: the free corners are rounded (worn), the bottom one at the open edge is bent back along an
  old crease line (the same line as on the cover_height.png relief), pressboard fibre, a sun-faded
  top, a glass ring, a thumbed strip at the open edge, unevenly rubbed edges;
- forms on the binder: three piles slightly out of line (stepped edges), the loose form sags past the
  edge of the cover and lies on the floor;
- bow: the knot is a soft wrap instead of a box, the loops have more segments, towards the far end
  the ribbon rises on edge (like a real tape loop), the ends are smooth curves with a roll at the
  knot, the cuts are slanted; the tape has a rib weave, the ends on the floor are dirtier;
- tape: the layers outside spring in a smooth S-curve, the free end lies on the floor drifting
  sideways and curled up (thermal paper remembers the roll); the edge at the floor and the ends are
  dusty.
There are no vanilla DayZ items (proxies): the folder has none of the parts DayZ has, and the DayZ
pen is recoloured by the config (like the cigarette packs) - a proxy would be drawn in the wrong colour.

Blender axes: X is the folder width (spine at -X, open edge at +X), Y is the height (the top of the
folder at +Y, the tape sticks out there; the bottom towards the viewer, -Y), Z is up. The origin is
the centre of the back cover on the ground: autocenter = 0 (in Geometry), boundingbox_min at the
bottom, so a dropped folder lies flat. Shared dimensions: m62_layout.py (also read by make_decals.py).
"""
import contextlib
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
import m62_layout as ly  # noqa: E402
from mathutils import Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
SEL = "camoGround"                 # cover: the line colour is set by the config (hiddenSelections)
UP = Vector((0.0, 0.0, 1.0))

# --- cover: height of the centre line of the front cover ------------------------------------------
Z_SPINE = ly.CB + ly.H0 + ly.CB / 2                          # at the spine: forms and the bar under it
Z_TIE = ly.LOOSE_Z1 + ly.TIE_TH + 0.00005 + ly.CB / 2        # at the bow: the tie pulled it down to the forms
Z_FREE = 0.0042                                              # the free corners of the open edge spring up
R_STACK = (ly.TAPE_X0, ly.TAPE_X1, ly.Y_IN, ly.Y1)           # the accordion under the cover
# the free corners are worn round; the bottom corner at the open edge was once folded and flattened: it
# is bent up along a crease line, the same one as on the relief (make_decals.py, cover_height.png: from
# 186 mm along the bottom to 268 mm from the top along the open edge)
R_CORNER = 0.003
CREASE = ((ly.X0 + 0.186, ly.Y0), (ly.X1, ly.Y1 - 0.268))
DOG_DEG = 11.0
_CD = (CREASE[1][0] - CREASE[0][0], CREASE[1][1] - CREASE[0][1])
DOG_N = (_CD[1] / math.hypot(*_CD), -_CD[0] / math.hypot(*_CD))   # from the crease line towards the corner


def smooth(a):
    a = min(max(a, 0.0), 1.0)
    return a * a * (3 - 2 * a)


def z_open(y):
    return Z_FREE + (Z_TIE - Z_FREE) * math.exp(-((y - ly.Y_BOW) / 0.075) ** 2)


def z_lin(x, y):
    return Z_SPINE + (z_open(y) - Z_SPINE) * (x - ly.X0) / ly.FW


def zc(x, y):
    """Front cover, stiff cardboard: flat from the spine to the open edge, pulled down at the bow, raised
    over the tape accordion (the hump falls off smoothly, radius ~45 mm)."""
    cx = min(max(x, R_STACK[0]), R_STACK[1])
    cy = min(max(y, R_STACK[2]), R_STACK[3])
    d = math.hypot(x - cx, y - cy)
    need = ly.stack_top(cy) + 0.0002 + ly.CB / 2
    lift = max(0.0, need - z_lin(cx, cy)) * math.exp(-(d / 0.045) ** 2) * smooth((x - ly.X0) / ly.FW / 0.35)
    return z_lin(x, y) + lift


def z_cover(x, y):
    """zc plus the bent corner: everything beyond the crease line is rotated about it by DOG_DEG."""
    d = (x - CREASE[0][0]) * DOG_N[0] + (y - CREASE[0][1]) * DOG_N[1]
    return zc(x, y) + (d * math.tan(math.radians(DOG_DEG)) if d > 1e-9 else 0.0)


# front cover grid: lines run along the edges of the label, the accordion and the bow (the label
# vertices coincide with the cover vertices, the accordion lies wholly under the hump plateau) and
# through the corners of the crease line of the bent corner
GRID = {
    0: ([ly.X0, ly.LABEL_X[0], -0.040, ly.LABEL_X[1], ly.TAPE_X0, ly.TAPE_X, ly.TAPE_X1, CREASE[0][0], ly.X1],
        [ly.Y0, CREASE[1][1], -0.090, -0.055, ly.Y_BOW, ly.LABEL_Y[0], ly.Y_IN, ly.LABEL_Y[1], ly.Y1]),
    1: ([ly.X0, -0.040, ly.TAPE_X0, ly.TAPE_X1, CREASE[0][0], ly.X1], [ly.Y0, CREASE[1][1], ly.Y_BOW, ly.Y_IN, ly.Y1]),
}


def cover_top(lod, x, y):
    """Top of this LOD's front cover at the point (x, y): by the grid, with a margin for the square's
    diagonal."""
    xs, ys = GRID[lod]
    i = max(0, min(len(xs) - 2, sum(1 for v in xs[1:-1] if v <= x)))
    j = max(0, min(len(ys) - 2, sum(1 for v in ys[1:-1] if v <= y)))
    fx = min(max((x - xs[i]) / (xs[i + 1] - xs[i]), 0.0), 1.0)
    fy = min(max((y - ys[j]) / (ys[j + 1] - ys[j]), 0.0), 1.0)
    z00, z10, z01, z11 = zc(xs[i], ys[j]), zc(xs[i + 1], ys[j]), zc(xs[i], ys[j + 1]), zc(xs[i + 1], ys[j + 1])
    z = (z00 * (1 - fx) + z10 * fx) * (1 - fy) + (z01 * (1 - fx) + z11 * fx) * fy
    return z + abs(z00 + z11 - z10 - z01) / 4 + ly.CB / 2


# forms on the binder, in three piles slightly out of line (the prongs hold them at the spine, towards
# the open edge and in height the sheets drift apart by ~1 mm): (shift x, shift y, rotation about the
# holes, share of the stack from - to)
FORM_SLABS = [(0.0, 0.0, 0.0, 0.0, 0.40), (0.0008, -0.0006, 0.22, 0.40, 0.75), (-0.0003, 0.0009, -0.18, 0.75, 1.0)]
# the loose form sags past the edge of the stack and lies on the floor
LOOSE_ZM = (ly.LOOSE_Z0 + ly.LOOSE_Z1) / 2
STACK_Y0 = -ly.SH / 2                                        # bottom edge of the stack of forms
LOOSE_SAG = 0.021                                            # how far from the stack edge it reaches the floor

LOD_SPECS = [dict(lod=0), dict(lod=1)]

# density scale: the front cover, the label, the top tape layer and the bottom of the form matter most;
# backs and what the cover hides get almost no space
REGIONS = {
    "cover": ("cover", 1.0), "cover_in": ("cover_in", 0.2), "cover_edge": ("cover_edge", 0.5),
    "label": ("label", 2.2),
    "forms_in": ("paper", 0.05), "forms_edge": ("paper_edge", 0.6),
    "form": ("form", 2.2), "form_hid": ("paper", 0.05),
    "tape": ("tape", 3.0), "tape_lo": ("tape", 0.8), "tape_back": ("tape_back", 0.8), "tape_hid": ("tape_back", 0.1),
    "tie": ("tie", 1.5),
}


# --- materials ------------------------------------------------------------------------------------
# The "dayz" profile layers (kmats.dayz_layers: tonal blotches, grease stains, scratches, streaks) are
# tuned for machines 1-2 m in size: on a 30 cm folder one blotch covers the whole cover. So their noise
# is made finer (SMALL), and on paper and ribbon they are weaker - by a temporary profile tweak while
# the material is built (look_tweak); the kit is not changed.
SMALL = 3.5
PAPER_LOOK = dict(smudge=0.12, scratches=0.05, streaks=0.15, mottle=0.10)
CLOTH_LOOK = dict(scratches=0.0, streaks=0.2, smudge=0.25)


@contextlib.contextmanager
def look_tweak(**kw):
    look = kmats.LOOK
    if look["name"] != "dayz" or not kw:
        yield
        return
    old = {k: look[k] for k in kw}
    look.update(kw)
    try:
        yield
    finally:
        look.update(old)


def small(t, vec):
    return t.stretch(vec, SMALL, SMALL, SMALL)


def tone(color, k):
    return tuple(min(1.0, c * k) for c in color[:3]) + (1.0,)


def attr_uv(t, name="pp"):
    a = t.node("ShaderNodeAttribute")
    a.attribute_type = "GEOMETRY"
    a.attribute_name = name
    sep = t.node("ShaderNodeSeparateXYZ")
    t.link(a.outputs["Vector"], sep.inputs[0])
    return sep.outputs["X"], sep.outputs["Y"]


def gauss(t, x, y, cx, cy, sx, sy):
    dx = t.math("DIVIDE", t.math("SUBTRACT", x, cx), sx)
    dy = t.math("DIVIDE", t.math("SUBTRACT", y, cy), sy)
    q = t.math("ADD", t.math("MULTIPLY", dx, dx), t.math("MULTIPLY", dy, dy))
    return t.math("POWER", math.e, t.math("MULTIPLY", q, -1.0))


def dist_to(t, x, y, cx, cy):
    dx, dy = t.math("SUBTRACT", x, cx), t.math("SUBTRACT", y, cy)
    return t.math("SQRT", t.math("ADD", t.math("MULTIPLY", dx, dx), t.math("MULTIPLY", dy, dy)))


RING = (0.046, -0.104, 0.025)          # glass ring: centre, radius


def build_cover(mat, origin, color, seed=1.0, front=True, gloss=0.16, spec=0.10, faded=None):
    """Pressboard: fibre and fine fuzz, cloudy tone; the front also has the printed rules and relief
    (creases, the binder bar, the crease line), a sun-faded top, a drip stain, an incomplete glass ring,
    a greasy spot and a thumbed strip at the open edge; edges and corners are unevenly rubbed down to
    light fibre."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    x, y, z = sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]
    fib = t.noise(t.stretch(vec, 1.0, 0.35, 1.0), 160.0, 4.0, 0.7)
    felt = t.noise(t.stretch(vec, 0.25, 1.0, 1.0), 480.0, 3.0, 0.6)
    cloud = t.maprange(t.noise(vec, 4.0, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0)
    col = t.mixc(cloud, tone(color, 0.84), color)
    col = t.mixc(t.math("MULTIPLY", t.maprange(fib, 0.45, 0.8, 0.0, 1.0), 0.28), col, tone(color, 1.25))
    col = t.mixc(t.math("MULTIPLY", t.maprange(felt, 0.55, 0.85, 0.0, 1.0), 0.20), col, tone(color, 0.78))
    h = t.math("ADD", t.math("MULTIPLY", fib, 0.12), t.math("MULTIPLY", felt, 0.08))
    if front:
        gate = t.math("MULTIPLY", t.facing(nsep, "Z", 1, 0.5), t.math("GREATER_THAN", z, 0.002))
        pc, pa = t.image(os.path.join(WORK, "cover_print.png"), x, y, (0.0, 0.0), (ly.FW, ly.FH))
        col = t.mixc(t.math("MULTIPLY", pa, gate), col, pc)
        hc, _ = t.image(os.path.join(WORK, "cover_height.png"), x, y, (0.0, 0.0), (ly.FW, ly.FH))
        rel = t.math("SUBTRACT", t.bw(hc), 0.5)
        h = t.math("ADD", h, t.math("MULTIPLY", t.math("MULTIPLY", rel, gate), 3.0))
        if faded is not None:
            # sun-faded: the top of the folder (it lay outwards in the stack) is lighter and yellower along
            # with the print, with an uneven boundary
            fy = t.math("ADD", y, t.math("MULTIPLY", t.math("SUBTRACT", t.noise(vec, 7.0, 3.0, 0.5), 0.5), 0.08))
            col = t.mixc(t.math("MULTIPLY", t.maprange(fy, -0.05, 0.13, 0.0, 0.32), gate), col, faded)
        # drip stain: a darker rim, slightly darker inside, an uneven edge
        dist = t.math("ADD", dist_to(t, x, y, -0.058, -0.098), t.math("MULTIPLY", t.noise(vec, 60.0, 3.0, 0.5), 0.006))
        ring = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", dist, 0.017)), 0.0, 0.0012, 1.0, 0.0)
        inside = t.math("LESS_THAN", dist, 0.017)
        stain = t.math("MULTIPLY", t.math("ADD", t.math("MULTIPLY", ring, 0.45), t.math("MULTIPLY", inside, 0.10)), gate)
        col = t.mixc(stain, col, tone(color, 0.55))
        # ring from a glass with reagent: a thin brown rim, broken in places, a light shadow inside
        rd = t.math("ADD", dist_to(t, x, y, RING[0], RING[1]),
                    t.math("MULTIPLY", t.math("SUBTRACT", t.noise(vec, 45.0, 3.0, 0.5), 0.5), 0.004))
        rim = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", rd, RING[2])), 0.0, 0.0010, 1.0, 0.0)
        broken = t.maprange(t.noise(vec, 22.0, 2.0, 0.5), 0.41, 0.53, 0.0, 1.0)
        cup = t.math("ADD", t.math("MULTIPLY", rim, broken), t.math("MULTIPLY", t.math("LESS_THAN", rd, RING[2]), 0.08))
        col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", cup, gate), 0.48), col, kmats.lin((104, 94, 54)))
        # greasy spot at the open edge where the folder is picked up, and a thumbed strip along it
        grab = t.math("MULTIPLY", gauss(t, x, y, 0.098, -0.080, 0.022, 0.045),
                      t.maprange(t.noise(vec, 18.0, 6.0, 0.6), 0.35, 0.7, 0.3, 1.0))
        col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", grab, gate), 0.45), col, tone(color, 0.6))
        band = t.math("MULTIPLY", t.maprange(t.math("SUBTRACT", ly.X1, x), 0.0, 0.035, 1.0, 0.0),
                      t.maprange(t.noise(vec, 25.0, 5.0, 0.6), 0.35, 0.75, 0.0, 0.32))
        col = t.mixc(t.math("MULTIPLY", band, gate), col, tone(color, 0.62))
    # edges and corners: the board is unevenly rubbed down to light fibre
    dx = t.math("MINIMUM", t.math("SUBTRACT", x, ly.X0), t.math("SUBTRACT", ly.X1, x))
    dy = t.math("MINIMUM", t.math("SUBTRACT", y, ly.Y0), t.math("SUBTRACT", ly.Y1, y))
    jit = t.math("MULTIPLY", t.math("SUBTRACT", t.noise(vec, 140.0, 3.0, 0.6), 0.5), 0.003)
    edge = t.maprange(t.math("ADD", t.math("MINIMUM", dx, dy), jit), 0.0, 0.0035, 1.0, 0.0)
    corner = t.maprange(t.math("ADD", dx, dy), 0.0, 0.016, 1.0, 0.0)
    wear = t.math("MULTIPLY", t.math("MAXIMUM", edge, corner), t.maprange(t.noise(vec, 70.0, 6.0, 0.7), 0.3, 0.7, 0.3, 1.0))
    col = t.mixc(t.math("MULTIPLY", wear, 0.7), col, tuple(min(1.0, c * 1.5 + 0.06) for c in color[:3]) + (1,))
    col, dirt = kmats.weather(t, col, small(t, vec), sep, nsep, 0.0, dust=0.10, grime=0.0, cav=0.5)
    gl = t.math("SUBTRACT", gloss, t.math("MULTIPLY", t.math("ADD", wear, dirt), gloss * 0.6))
    return kmats.out(t, col, gl, spec, h)


def build_sheet(mat, origin, img, center, size, paper, gloss=0.08, spec=0.05, seed=3.0, age=0.0, look=None):
    """Paper with an image by the attribute `pp` (coordinates on the sheet): fibre, light dust, dirt near
    the floor; age yellows the paper in blotches (thermal paper also greys); look is the "dayz" layers
    (PAPER_LOOK by default)."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    u, v = attr_uv(t)
    c, a = t.image(img, u, v, center, size)
    col = t.mixc(a, paper, c)
    col = t.mixc(t.math("MULTIPLY", t.noise(vec, 220.0, 3.0, 0.6), 0.10), col, kmats.lin((200, 196, 182)))
    if age > 0:
        col = t.mixc(t.math("MULTIPLY", t.maprange(t.noise(vec, 30.0, 4.0, 0.6), 0.4, 0.75, 0.0, 1.0), age), col,
                     kmats.lin((214, 206, 178)))
    with look_tweak(**(look or PAPER_LOOK)):
        col, _ = kmats.weather(t, col, small(t, vec), sep, nsep, 0.0, dust=0.08, grime=0.25, cav=0.35, low_h=0.0015)
    dark = t.math("SUBTRACT", 1.0, t.bw(c))
    gl = t.math("ADD", gloss, t.math("MULTIPLY", t.math("MULTIPLY", dark, a), 0.12))   # the ink is slightly glossy
    return kmats.out(t, col, gl, spec, t.math("MULTIPLY", t.noise(vec, 300.0, 2.0, 0.5), 0.05))


def paper_plain(mat, origin, **kw):
    """Paper without an image (backs, edges of the stack): kmats.build_plastic with weak "dayz" layers."""
    with look_tweak(**PAPER_LOOK):
        return kmats.build_plastic(mat, origin, **kw)


def build_cloth(mat, origin, color, seed=6.2, gloss=0.05, spec=0.03):
    """Cotton tape: a weave rib (tone and relief in two directions), greased by hands in blotches; what lies
    on the floor (the ends, the bottom of the knot) is dusty and dirty (weather with low_h 3 mm)."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    w1 = t.noise(t.stretch(vec, 1.0, 0.05, 1.0), 1800.0, 1.0, 0.5)
    w2 = t.noise(t.stretch(vec, 0.05, 1.0, 1.0), 1800.0, 1.0, 0.5)
    weave = t.math("MAXIMUM", w1, w2)
    col = t.mixc(t.maprange(t.noise(vec, 40.0, 4.0, 0.6), 0.3, 0.7, 0.0, 1.0), tone(color, 0.92), color)
    col = t.mixc(t.math("MULTIPLY", t.maprange(weave, 0.5, 0.8, 0.0, 1.0), 0.18), col, tone(color, 0.8))
    hand = t.maprange(t.noise(vec, 70.0, 4.0, 0.6), 0.48, 0.78, 0.0, 0.30)
    col = t.mixc(hand, col, kmats.lin((128, 116, 94)))
    with look_tweak(**CLOTH_LOOK):
        col, dirt = kmats.weather(t, col, small(t, vec), sep, nsep, 0.0, dust=0.18, grime=0.5, cav=0.6, low_h=0.003)
    gl = t.math("SUBTRACT", gloss, t.math("MULTIPLY", dirt, gloss * 0.5))
    h = t.math("ADD", t.math("MULTIPLY", weave, 0.18), t.math("MULTIPLY", hand, -0.05))
    return kmats.out(t, col, gl, spec, h)


KINDS = kmats.std_kinds(floor_z=0.0)
GREEN = kmats.lin((64, 106, 74))     # toned down: (70, 116, 80) looked too bright next to vanilla items
FADED = kmats.lin((108, 128, 96))
PAPER = kmats.lin((236, 233, 220))
KINDS.update({
    "cover": (build_cover, dict(color=GREEN, seed=1.3, front=True, faded=FADED)),
    "cover_in": (build_cover, dict(color=kmats.lin((74, 116, 84)), seed=1.9, front=False, gloss=0.10, spec=0.06)),
    "cover_edge": ("plastic", dict(color=kmats.lin((62, 90, 66)), seed=2.4, gloss=0.06, spec=0.04, dust=0.1,
                                   grime=0.0, mottle=0.16, scuff=(0.8, 0.95))),
    "label": (build_sheet, dict(img=os.path.join(WORK, "label.png"), center=ly.LABEL_C, size=ly.LABEL_S,
                                paper=kmats.lin((240, 236, 220)), seed=3.3, age=0.22,
                                look=dict(PAPER_LOOK, smudge=0.30, mottle=0.14))),
    "form": (build_sheet, dict(img=os.path.join(WORK, "form.png"), center=(0.0, 0.0), size=(ly.SW, ly.SH),
                               paper=PAPER, seed=3.7, age=0.10)),
    "tape": (build_sheet, dict(img=os.path.join(WORK, "tape.png"), center=(0.0, -ly.TAPE_LEN / 2),
                               size=(ly.TAPE_W, ly.TAPE_LEN), paper=kmats.lin((240, 239, 232)), gloss=0.22,
                               spec=0.14, seed=4.1, age=0.22)),
    "tape_back": (paper_plain, dict(color=kmats.lin((234, 232, 222)), seed=4.6, gloss=0.12, spec=0.06, dust=0.08,
                                    grime=0.0, mottle=0.04, scuff=(0.95, 1.0))),
    "paper": (paper_plain, dict(color=PAPER, seed=5.1, gloss=0.06, spec=0.04, dust=0.08, grime=0.0, mottle=0.05,
                                scuff=(0.95, 1.0))),
    "paper_edge": (paper_plain, dict(color=kmats.lin((214, 210, 196)), seed=5.5, gloss=0.05, spec=0.03, dust=0.1,
                                     grime=0.0, mottle=0.12, scuff=(0.95, 1.0))),
    "tie": (build_cloth, dict(color=kmats.lin((212, 203, 178)), seed=6.2)),
})

OBJ, NAME = "m62_carrier_bio", "ozr_carrier_bio"
# rvmat: specular[] as in the "dayz" profile (the --look preview computes the highlight with it),
# specularPower stays 25: paper has a broad, dull highlight
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 rvmat=dict(specular=1.0, power=25.0), selections=(SEL,), hidden=(SEL,))
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


def retag(p, faces, fn):
    for f in faces:
        f.normal_update()
        f[p.reg] = p.region_index(fn(f.normal))


def set_pp(p, fn):
    lay = p.bm.verts.layers.float_vector.get("pp") or p.bm.verts.layers.float_vector.new("pp")
    for v in p.bm.verts:
        a, b = fn(v.co)
        v[lay] = (a, b, 0.0)


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, as in M16)."""
    v = [Vector(q) for q in pts]
    out = []
    for i in range(len(v) - 1):
        p0 = v[i - 1] if i > 0 else 2 * v[i] - v[i + 1]
        p1, p2 = v[i], v[i + 1]
        p3 = v[i + 2] if i + 2 < len(v) else 2 * v[i + 1] - v[i]
        for s in range(k):
            t = s / k
            out.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (3 * p1 - p0 - 3 * p2 + p3) * t ** 3))
    out.append(v[-1])
    return [tuple(q) for q in out]


def tangents(pts):
    v = [Vector(q) for q in pts]
    n = len(v)
    return [(v[min(n - 1, i + 1)] - v[max(0, i - 1)]).normalized() for i in range(n)]


def arc_frac(pts):
    """Fraction of the polyline's length at each point (0 is the start, 1 the end)."""
    s = [0.0]
    for a, b in zip(pts, pts[1:]):
        s.append(s[-1] + math.dist(a, b))
    return [q / s[-1] for q in s]


def interp(table, f):
    """Piecewise-linear lookup in a table [(fraction, value)]."""
    for (f0, a), (f1, b) in zip(table, table[1:]):
        if f <= f1:
            return a + (b - a) * min(max((f - f0) / max(f1 - f0, 1e-9), 0.0), 1.0)
    return table[-1][1]


# --- sheets: the cover and the loose form ---------------------------------------------------------
def corner_arc(x, y, inner_x, inner_y, r, n):
    """Rounding of the corner (x, y) with radius r in n segments, walked counter-clockwise (seen from above);
    inner_x, inner_y give the side of the corner where the sheet is (+1 / -1)."""
    cx, cy = x + inner_x * r, y + inner_y * r
    a0 = {(-1, 1): -90.0, (-1, -1): 0.0, (1, -1): 90.0, (1, 1): 180.0}[(inner_x, inner_y)]
    return [(cx + r * math.cos(math.radians(a0 + 90.0 * k / n)), cy + r * math.sin(math.radians(a0 + 90.0 * k / n)))
            for k in range(n + 1)]


def sheet(p, us, vs, xy, zmid, th, reg_top, reg_bot, reg_edge, rounded=(), r=0.0, n=1, crease=None,
          skip_first_u=False):
    """Sheet over the grid us x vs (the sheet's own coordinates, xy(u, v) -> world (x, y)): the top and
    bottom lie th/2 from the mid-surface zmid(x, y), with edges along the perimeter. rounded lists grid
    corner nodes (i, j) rounded with radius r (n segments); crease = ((i, j), (i1, j1), (i2, j2)) means
    cell (i, j) is cut by the diagonal between its nodes (the crease line: the sheet is folded along it,
    zmid accounts for that); skip_first_u omits the edge at u = us[0] (the spine is there). reg_top(u, v)
    gives the region of a cell's top by its middle."""
    bm = p.bm
    nu, nv = len(us) - 1, len(vs) - 1
    pts = {}
    arcs = {}
    for i in range(nu + 1):
        for j in range(nv + 1):
            pts[("g", i, j)] = (us[i], vs[j])
    for (i, j) in rounded:
        ix, iy = (-1 if i == nu else 1), (-1 if j == nv else 1)
        keys = []
        for k, q in enumerate(corner_arc(us[i], vs[j], ix, iy, r, n)):
            pts[("a", i, j, k)] = q
            keys.append(("a", i, j, k))
        arcs[("g", i, j)] = keys
        del pts[("g", i, j)]
    top, bot = {}, {}
    for key, (u, v) in pts.items():
        x, y = xy(u, v)
        z = zmid(x, y)
        top[key] = bm.verts.new((x, y, z + th / 2))
        bot[key] = bm.verts.new((x, y, z - th / 2))

    def expand(keys):
        out = []
        for k in keys:
            out += arcs.get(k, [k])
        return out
    cells = []
    for i in range(nu):
        for j in range(nv):
            poly = expand([("g", i, j), ("g", i + 1, j), ("g", i + 1, j + 1), ("g", i, j + 1)])
            if crease and crease[0] == (i, j):
                a, b = sorted((poly.index(("g",) + tuple(crease[1])), poly.index(("g",) + tuple(crease[2]))))
                cells += [poly[a:b + 1], poly[b:] + poly[:a + 1]]
            else:
                cells.append(poly)
    for poly in cells:
        cu = sum(pts[k][0] for k in poly) / len(poly)
        cv = sum(pts[k][1] for k in poly) / len(poly)
        face(p, [top[k] for k in poly], reg_top(cu, cv), (0, 0, 1))
        face(p, [bot[k] for k in poly][::-1], reg_bot, (0, 0, -1))
    ring = ([("g", i, 0) for i in range(nu + 1)] + [("g", nu, j) for j in range(1, nv + 1)] +
            [("g", i, nv) for i in range(nu - 1, -1, -1)] + [("g", 0, j) for j in range(nv - 1, 0, -1)])
    ring = expand(ring)
    for k1, k2 in zip(ring, ring[1:] + ring[:1]):
        if skip_first_u and abs(pts[k1][0] - us[0]) < 1e-9 and abs(pts[k2][0] - us[0]) < 1e-9:
            continue
        a, b = top[k1].co, top[k2].co
        out = (b.y - a.y, -(b.x - a.x), 0.0)
        face(p, [top[k1], top[k2], bot[k2], bot[k1]], reg_edge, out)


def rounded_rect(x0, x1, y0, y1, r, n):
    """Rectangle, counter-clockwise, with corners rounded at x1 (the free edge of the cover)."""
    pts = [(x0, y0)]
    pts += corner_arc(x1, y0, -1, 1, r, n)
    pts += corner_arc(x1, y1, -1, -1, r, n)
    pts.append((x0, y1))
    return pts


# --- folder ---------------------------------------------------------------------------------------
def build_folder(spec):
    lod = spec["lod"]
    xs, ys = GRID[lod]
    nx = len(xs) - 1
    h = ly.CB / 2
    n_arc = 3 if lod == 0 else 1
    fr = P("front", "cover", group=SEL)
    sheet(fr, xs, ys, lambda u, v: (u, v), z_cover, ly.CB, lambda u, v: "cover", "cover_in", "cover_edge",
          rounded=((nx, 0), (nx, len(ys) - 1)), r=R_CORNER, n=n_arc, crease=((nx - 1, 0), (nx - 1, 0), (nx, 1)),
          skip_first_u=True)
    bk = P("back", "cover", group=SEL)
    retag(bk, g.prism(bk, rounded_rect(ly.X0, ly.X1, ly.Y0, ly.Y1, R_CORNER, n_arc), (0, 1), 0.0, ly.CB),
          lambda n: "cover_in" if n.z > 0.5 else ("cover" if n.z < -0.5 else "cover_edge"))
    # spine: the board wraps around the edge of the stack, slightly convex
    sp = P("spine", "cover", group=SEL)
    zt = Z_SPINE + h
    n_seg = 6 if lod == 0 else 2
    out_r, bulge = zt / 2, 0.0016
    rings = []
    for k in range(n_seg + 1):
        a = -math.pi / 2 + math.pi * k / n_seg
        po = (ly.X0 - bulge * math.cos(a), zt / 2 + out_r * math.sin(a))
        pi = (ly.X0 - (bulge - ly.CB * 0.8) * math.cos(a), zt / 2 + (out_r - ly.CB) * math.sin(a))
        rings.append([sp.bm.verts.new((px, y, pz)) for (px, pz) in (po, pi) for y in (ly.Y0, ly.Y1)])
    for k in range(n_seg):
        r0, r1 = rings[k], rings[k + 1]
        face(sp, [r0[0], r0[1], r1[1], r1[0]], "cover", (-1, 0, 0))
        face(sp, [r0[2], r0[3], r1[3], r1[2]], "cover_in", (1, 0, 0))
    for e, want in ((0, (0, -1, 0)), (1, (0, 1, 0))):       # ends of the spine
        ring = [r[e] for r in rings] + [r[2 + e] for r in rings][::-1]
        face(sp, ring, "cover_edge", want)
    parts = [fr, bk, sp]
    # forms on the binder (their edges show in the gap): piles out of line - each its own part, so that
    # faces covered from above by a neighbouring face do not share atlas space with open ones
    slabs = FORM_SLABS if lod == 0 else [(0.0, 0.0, 0.0, 0.0, 1.0)]
    for idx, (dx, dy, deg, f0, f1) in enumerate(slabs):
        a = math.radians(deg)
        frm = g.Frame((ly.HOLE_X + dx, dy, 0.0), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))
        fm = P("forms_%d" % idx, "forms_edge")
        retag(fm, g.box(fm, ly.FORM_X0 - ly.HOLE_X, ly.FORM_X0 + ly.SW - ly.HOLE_X, -ly.SH / 2, ly.SH / 2,
                        ly.FORM_Z0 + f0 * ly.FORM_T, ly.FORM_Z0 + f1 * ly.FORM_T, frame=frm),
              lambda n: "forms_in" if abs(n.z) > 0.5 else "forms_edge")
        parts.append(fm)
    # loose form: the bottom strip (visible) and the rest (under the cover) are different atlas regions;
    # past the edge of the stack the sheet sags and lies on the floor
    a = math.radians(ly.LOOSE_ROT)
    frame = g.Frame((ly.LOOSE_C[0], ly.LOOSE_C[1], 0.0), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0),
                    (0, 0, 1))
    lo = P("loose", "form")
    vs0 = -ly.SH / 2
    strip = vs0 + ly.LOOSE_STRIP
    if lod == 0:
        lus = [-ly.SW / 2, 0.0, ly.SW / 2]
        lvs = [vs0, vs0 + 0.006, vs0 + 0.012, vs0 + 0.018, vs0 + 0.024, vs0 + 0.030, strip, ly.SH / 2]
    else:
        lus = [-ly.SW / 2, ly.SW / 2]
        lvs = [vs0, vs0 + 0.012, vs0 + 0.024, strip, ly.SH / 2]

    def z_loose(x, y):
        d = STACK_Y0 - y
        return LOOSE_ZM if d <= 0 else LOOSE_ZM - (LOOSE_ZM - 0.00016) * smooth(d / LOOSE_SAG)
    sheet(lo, lus, lvs, lambda u, v: tuple(frame.p(u, v, 0.0))[:2], z_loose, ly.LOOSE_T,
          lambda u, v: "form" if v < strip else "form_hid", "form_hid", "form_hid")
    set_pp(lo, lambda co: ((co - frame.o).dot(frame.u), (co - frame.o).dot(frame.v)))
    parts.append(lo)
    # label on the front cover
    lb = P("label", "label")
    lxs = [x for x in xs if ly.LABEL_X[0] - 1e-6 <= x <= ly.LABEL_X[1] + 1e-6]
    lys = [y for y in ys if ly.LABEL_Y[0] - 1e-6 <= y <= ly.LABEL_Y[1] + 1e-6]
    if len(lxs) < 2 or len(lys) < 2:                         # middle LOD: the label corners lie inside squares
        lxs, lys = list(ly.LABEL_X), list(ly.LABEL_Y)
        zf = lambda x, y: cover_top(lod, x, y) + 0.0002  # noqa: E731
    else:
        zf = lambda x, y: zc(x, y) + h + 0.0004  # noqa: E731
    gv = [[lb.bm.verts.new((x, y, zf(x, y))) for y in lys] for x in lxs]
    for i in range(len(lxs) - 1):
        for j in range(len(lys) - 1):
            face(lb, [gv[i][j], gv[i + 1][j], gv[i + 1][j + 1], gv[i][j + 1]], "label", (0, 0, 1))
    set_pp(lb, lambda co: (co.x, co.y))
    parts.append(lb)
    return parts


# --- tape -----------------------------------------------------------------------------------------
# free end (the head of the printout): from the fold of the bottom layer (Y_OUT) it lies down to the
# floor, drifts slightly sideways, the tip is curled up (thermal paper remembers the roll). (y from
# Y_OUT, z) from the accordion to the tip
TAIL_GROUND = [(0.004, 0.00088), (0.009, 0.00050), (0.015, 0.00027), (0.022, 0.00021), (0.030, 0.00024),
               (0.038, 0.00021), (0.045, 0.00022)]
TAIL_DRIFT = 0.005                 # sideways drift towards the tip
CURL_R, CURL_DEG = 0.0045, 125.0   # curl: radius at the floor (22 % tighter towards the tip), angle


def tail_points(near):
    """Tail of the tape [(dx, y from Y_OUT, z)] from the tip of the curl to the accordion."""
    ground = TAIL_GROUND if near else [TAIL_GROUND[i] for i in (1, 3, 6)]
    y0, zg = ground[-1][0], ground[-1][1]
    n = 6 if near else 2
    curl = []
    for j in range(1, n + 1):
        th = math.radians(CURL_DEG) * j / n
        r = CURL_R * (1.0 - 0.22 * j / n)
        curl.append((y0 + r * math.sin(th), zg + r * (1.0 - math.cos(th))))
    out = []
    for dy, z in ground + curl:
        f = min(1.0, dy / (y0 + CURL_R))
        out.append((TAIL_DRIFT * f * f, dy, z))
    return out[::-1]


def tape_points(lod):
    """Centre line of the tape [(dx, y, z, layer)] from the free end on the ground (s = 0, the head of the
    printout): the tail, the bottom layer inwards, a fold, the next one outwards... the top layer
    inwards, the end of the tape is under the cover (as ly.tape_path, the layer heights come from there
    too). Outside, a layer springs: it leaves the cover edge horizontally and rises to the fold in a
    smooth S-curve. The middle LOD takes every second layer."""
    near = lod == 0
    layers = list(range(ly.N_LAYERS)) if near else [0, 3, 6]
    out = [(dx, ly.Y_OUT + dy, z, layers[0]) for dx, dy, z in tail_points(near)]
    for i, k in enumerate(layers):
        inward = i % 2 == 0
        zo, ze, zi = ly.z_layer(k, "out"), ly.z_layer(k, "edge"), ly.z_layer(k, "in")
        fs = (0.0, 1.0 / 3, 2.0 / 3, 1.0) if near else (0.0, 1.0)
        row = [(ly.Y_OUT + (ly.Y1 - ly.Y_OUT) * f, zo + (ze - zo) * smooth(f)) for f in fs] + [(ly.Y_IN, zi)]
        if not inward:
            row = row[::-1]
        out += [(0.0, y, z, k) for y, z in row]
        if i == len(layers) - 1:
            break
        k2 = layers[i + 1]
        if inward:                                          # inside: a half-circle around -y
            za, zb, n, y0, sgn = zi, ly.z_layer(k2, "in"), (2 if near else 1), ly.Y_IN, -1
        else:                                               # outside: around +y
            za, zb, n, y0, sgn = zo, ly.z_layer(k2, "out"), (3 if near else 1), ly.Y_OUT, 1
        zm, r = (za + zb) / 2, (zb - za) / 2
        for j in range(1, n + 1):
            ang = -math.pi / 2 + math.pi * j / (n + 1)
            out.append((0.0, y0 + sgn * r * math.cos(ang), zm + r * math.sin(ang), k))
    return out


def build_tape(spec):
    """Accordion: two sheets (print and back) TAPE_TH apart, across along X. The print side faces (-X) x s
    (s is the run of the tape from the free end): up on the tail and the inward layers, down on the
    outward layers, outwards on the outer folds, inwards in the curl. The image runs along (across, -s):
    the top of the image (the head of the printout) is at the free end; it reads from the front of the
    model and is not mirrored. Each layer is its own part: the layers lie one above another, and a
    per-side unwrap would otherwise pile them into the same texels."""
    pts = tape_points(spec["lod"])
    p3 = [Vector((ly.TAPE_X + dx, y, z)) for dx, y, z, _ in pts]
    s = [0.0]
    for a, b in zip(p3, p3[1:]):
        s.append(s[-1] + (b - a).length)
    top = pts[-1][3]
    tang = tangents(p3)
    parts = []
    i0 = 0
    while i0 < len(pts) - 1:
        k = pts[i0][3]
        i1 = i0
        while i1 < len(pts) - 1 and pts[i1][3] == k:
            i1 += 1
        p = P("tape_%d" % k, "tape")
        lay = p.bm.verts.layers.float_vector.new("pp")
        rings = []
        for i in range(i0, i1 + 1):
            t = tang[i]
            w = Vector((1.0, 0.0, 0.0)) - t * t.x                 # across the tape
            w.normalize()
            n = (-w).cross(t).normalized()
            ring = []
            for side in (1, -1):
                for xw in (-ly.TAPE_W / 2, ly.TAPE_W / 2):
                    v = p.bm.verts.new(p3[i] + w * xw + n * (side * ly.TAPE_TH / 2))
                    v[lay] = (xw, -s[i], 0.0)
                    ring.append(v)
            rings.append((ring, n))
        for (r0, n0), (r1, n1) in zip(rings, rings[1:]):
            n = (n0 + n1).normalized()
            yc = sum(v.co.y for v in r0 + r1) / 8
            hid = yc < ly.Y1 - 0.002
            main = k == top or yc > ly.Y_OUT + 0.001             # the top layer and the tail on the ground
            face(p, [r0[0], r0[1], r1[1], r1[0]], "tape_hid" if hid else ("tape" if main else "tape_lo"), n)
            face(p, [r0[2], r0[3], r1[3], r1[2]], "tape_hid" if hid else "tape_back", -n)
        parts.append(p)
        i0 = i1
    return parts


# --- ties -----------------------------------------------------------------------------------------
def ribbon(p, pts, sides=None, region="tie", w=ly.TIE_W, th=ly.TIE_TH, widths=None, caps=False, cut=0.0):
    """Ribbon along pts: the section is a narrow rhombus (edge, middle on top, edge, middle below), the edges
    are closed. The width follows sides[i] (straightened across the run; turning sides along the ribbon
    gives roll and twist), without sides it is horizontal across the run; widths is the fraction of the
    width (the ribbon is gathered at the knot); caps closes the ends; cut is a slanted end cut (the edges
    are shifted along the run by +-cut)."""
    pts = [Vector(q) for q in pts]
    widths = widths or [1.0] * len(pts)
    tg = tangents(pts)
    rings = []
    for i, t in enumerate(tg):
        s = Vector(sides[i]) if sides else UP.cross(t)
        s = s - t * s.dot(t)
        s = Vector((1, 0, 0)) if s.length < 1e-6 else s.normalized()
        n = t.cross(s).normalized()
        hw = w * widths[i] / 2
        e0, e1 = pts[i] - s * hw, pts[i] + s * hw
        if cut and i == len(pts) - 1:
            e0, e1 = e0 - t * cut, e1 + t * cut
        rings.append(([p.bm.verts.new(q) for q in (e0, pts[i] + n * th / 2, e1, pts[i] - n * th / 2)], n))
    for (r0, n0), (r1, n1) in zip(rings, rings[1:]):
        n = (n0 + n1).normalized()
        for q, want in ((0, n), (1, n), (2, -n), (3, -n)):
            face(p, [r0[q], r0[(q + 1) % 4], r1[(q + 1) % 4], r1[q]], region, want)
    if caps:
        face(p, rings[0][0], region, -tg[0])
        face(p, rings[-1][0], region, tg[-1])


# the bow knot at the middle of the open edge, on the floor: a soft wrap over the gathered loops and ends
KNOT = Vector((ly.X1 + 0.0047, ly.Y_BOW + 0.0003, 0.0026))
KNOT_AX = Vector((math.cos(math.radians(15.0)), math.sin(math.radians(15.0)), 0.0))
KNOT_PROF = [(-0.0042, 0.0034, 0.0020), (-0.0024, 0.0042, 0.0025), (0.0, 0.0044, 0.0026), (0.0024, 0.0042, 0.0025),
             (0.0042, 0.0034, 0.0020)]
# loops on the cover: (name, direction from the knot, length, half-width, rise over its neighbour at the knot)
LOOPS = (("loop_a", 158.0, 0.037, 0.0098, 0.0), ("loop_b", 212.0, 0.032, 0.0092, 0.0006))
LOOP_TILT = 28.0                   # towards the far end of the loop the ribbon rises on edge, outwards
# ends from the knot to the floor: direction, control points (along, sideways, z) from the knot, roll
# by length fraction (on edge at the knot, lying flat further on; tail_b turns slightly onto its edge
# towards the end)
TAILS = {
    "tail_a": (30.0, [(0.000, 0.0000, 0.0023), (0.006, 0.0004, 0.0018), (0.0115, 0.0010, 0.0008),
                      (0.017, 0.0016, 0.00032), (0.026, 0.0011, 0.00027), (0.036, -0.0006, 0.00027),
                      (0.047, -0.0015, 0.00027)],
               [(0.0, 38.0), (0.35, 0.0), (1.0, -6.0)]),
    "tail_b": (-29.0, [(0.000, 0.0000, 0.0021), (0.006, -0.0004, 0.0015), (0.0115, -0.0011, 0.0006),
                       (0.017, -0.0015, 0.00032), (0.025, -0.0006, 0.00030), (0.033, 0.0010, 0.00030),
                       (0.043, 0.0018, 0.00027)],
               [(0.0, -32.0), (0.30, 0.0), (0.62, 10.0), (1.0, 2.0)]),
}


def build_bow(spec):
    lod = spec["lod"]
    X1, YB = ly.X1, ly.Y_BOW
    parts = []
    kn = P("knot", "tie")
    prof = KNOT_PROF if lod == 0 else KNOT_PROF[::2]
    g.tube_var(kn, [tuple(KNOT + KNOT_AX * d) for d, _, _ in prof], [(a, b) for _, a, b in prof], 10 if lod == 0 else 6)
    parts.append(kn)

    # loops: from the knot in a teardrop over the cover and back into the knot; the ribbon is gathered at
    # the knot and stands on edge outwards towards the far end (its lower edge on the cover)
    k0 = KNOT - KNOT_AX * 0.0026
    n_pts = 19 if lod == 0 else 7
    for name, ang, ln, hw, over in LOOPS:
        ax = Vector((math.cos(math.radians(ang)), math.sin(math.radians(ang)), 0.0))
        pr = Vector((-ax.y, ax.x, 0.0))
        xy, us = [], []
        for i in range(n_pts):
            ph = 0.30 + (2 * math.pi - 0.60) * i / (n_pts - 1)
            u = (1 - math.cos(ph)) / 2
            q = k0 + ax * (ln * u) + pr * (hw * math.sin(ph) * (0.55 + 0.45 * u))
            xy.append(Vector((q.x, q.y, 0.0)))
            us.append(u)
        pts, sides, wid = [], [], []
        for q, u, t in zip(xy, us, tangents(xy)):
            s0 = UP.cross(t).normalized()                     # left along the run: the outside of the loop
            a = math.radians(LOOP_TILT) * smooth((u - 0.3) / 0.7)
            wf = 0.55 + 0.45 * smooth(u / 0.3)
            hwf = ly.TIE_W * wf / 2
            inner = q - s0 * (hwf * math.cos(a))
            near = max(0.0, 1.0 - u / 0.3)
            if max(q.x, inner.x) > X1 - 0.0015:
                base = KNOT.z + 0.0009
            else:
                base = max(cover_top(lod, inner.x, inner.y), cover_top(lod, q.x, q.y)) + 0.0002
            z = base + ly.TIE_TH / 2 + hwf * math.sin(a) + over * near + 0.0004 * near
            pts.append((q.x, q.y, z))
            sides.append(s0 * math.cos(a) + UP * math.sin(a))
            wid.append(wf)
        lp = P(name, "tie")
        ribbon(lp, pts, sides, widths=wid)
        parts.append(lp)

    # ends hang from the knot to the floor: smooth curves, rolled at the knot, slanted cuts
    t0 = KNOT + KNOT_AX * 0.0020
    for name, (deg, ctrl, roll) in TAILS.items():
        d = Vector((math.cos(math.radians(deg)), math.sin(math.radians(deg)), 0.0))
        e = Vector((-d.y, d.x, 0.0))
        raw = [tuple(t0 + d * a + e * b + Vector((0.0, 0.0, z - t0.z))) for a, b, z in ctrl]
        pts = spline(raw, 2) if lod == 0 else [raw[i] for i in (0, 2, 4, 6)]
        fr = arc_frac(pts)
        tg = tangents([(q[0], q[1], 0.0) for q in pts])
        out, sides = [], []
        for q, f, t in zip(pts, fr, tg):
            rho = math.radians(interp(roll, f))
            s0 = UP.cross(t).normalized()
            out.append((q[0], q[1], max(q[2], 0.00025 + ly.TIE_TH / 2 * abs(math.cos(rho)) +
                                         ly.TIE_W / 2 * abs(math.sin(rho)))))
            sides.append(s0 * math.cos(rho) + UP * math.sin(rho))
        tl = P(name, "tie")
        ribbon(tl, out, sides, caps=True, cut=0.0011)
        parts.append(tl)

    # ties from under the front cover and from the back one go into the knot
    zf = Z_TIE - ly.CB / 2 - ly.TIE_TH / 2 - 0.00003
    zb = ly.CB + ly.TIE_TH / 2 + 0.00003
    strips = {
        "tie_front": [(X1 - 0.011, YB + 0.0016, zf), (X1 - 0.004, YB + 0.0016, zf), (X1 - 0.0005, YB + 0.0014, zf + 0.0001),
                      (X1 + 0.0024, YB + 0.0011, KNOT.z + 0.0002)],
        "tie_back": [(X1 - 0.005, YB - 0.0030, zb), (X1 - 0.0015, YB - 0.0030, zb), (X1 + 0.0010, YB - 0.0026, ly.CB + 0.0005),
                     (X1 + 0.0028, YB - 0.0020, KNOT.z - 0.0011)],
    }
    for name, sp in strips.items():                          # almost entirely under the cover and in the knot
        st = P(name, "tie")
        ribbon(st, sp)
        parts.append(st)
    return parts


def build_lod(spec):
    parts = build_folder(spec) + build_tape(spec) + build_bow(spec)
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


INV_VIEW = (0.02, -0.40, 0.48)


def collision():
    """One convex hull over the vertices of the near LOD (folder, tape, bow). The mass is the class weight,
    0.3 kg (OZL_Carrier_Base); the hit sound and penetration are thin fabric, as for the vanilla book
    (Book_kniga.p3d: fabric_thin)."""
    comps = [(BOUNDS["pts"], kx.PEN + r"\fabric_thin.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    c = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, hi[2] / 2)
    memory = {
        # inventory preview camera: from the front and above - the folder, the tape above it, the bow on the
        # right
        "invView": [INV_VIEW],
        "ce_center": [c],
        "ce_radius": [(c[0] + 0.5 * math.dist(lo, hi), c[1], c[2])],
    }
    print("bbox %.4f..%.4f x %.4f..%.4f x 0..%.4f, preview aspect from invView %.2f (2x2 cell: ~1)"
          % (lo[0], hi[0], lo[1], hi[1], hi[2], preview_aspect(bbox, INV_VIEW)))
    return comps, 0.3, memory, bbox


# the first five are the --look preview: general view, bow, tape, bent corner with the form, top view
SHOTS = [
    ("front", (-0.24, -0.46, 0.30), (0.01, 0.02, 0.004), 45),
    ("bow", (0.25, -0.13, 0.095), (0.098, -0.022, 0.003), 50),
    ("tape", (0.15, 0.36, 0.12), (0.045, 0.175, 0.004), 50),
    ("corner", (0.20, -0.255, 0.105), (0.068, -0.140, 0.002), 50),
    ("top", (0.02, 0.03, 0.66), (0.02, 0.03, 0.0), 40),
    ("form", (0.06, -0.33, 0.08), (0.03, -0.16, 0.001), 50),
    ("inv", INV_VIEW, (0.02, 0.03, 0.004), 36),
]

if __name__ == "__main__":
    M.look_shots = (5, 2)
    M.run(build_lod, collision, SHOTS, row_step=0.32, row_shot=((0.16, -0.75, 0.55), (0.16, 0.03, 0.0)))
