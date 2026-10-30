"""M64 - "Electronics" carrier (OZL_Carrier_Electro): the carrier of the "Electronics" line, shared by the
factions (an electronic-device drawing in the Soviet manner with a compact disc on top of it, no jewel
case). A folded circuit diagram - a blueprint - with a box-less compact disc on top of it, shifted
towards a corner. A portable 2x2 item.

    blender --background --python build_m64.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (the diagram on the sheet, the disc
from above and below).

Target: the drawing is folded to ~21 x 30 cm, ~0.4 cm thick; paper or blueprint, thin diagram lines,
a stamp with empty fields; a CD of D 12 cm, a rainbow surface, a white label without text, lying
shifted towards a corner; 200-400 g, 300-1000 triangles (a small item: 0.3-1.5 k), texture 512-1024;
no readable text.

Reference and sizes:
- sheet: the "Circuit diagram" of an Elektronika 404/404D TV set (a lot listing): a large sheet folded
  along creases, blue-violet lines, a frame, a title block. The format is taken as A1 (GOST 2.301-68:
  594 x 841 mm), which is how household-appliance diagrams were printed. Folded per GOST 2.501-88 to
  A4: accordion-folded into 4 strips of 210 mm, then in half across - 210 x 297 mm, 8 layers. The
  title block (GOST 2.104-68, form 1: 185 x 55 mm) stays on top, in the bottom right corner; the frame
  is 5 mm from the cut edge. Diazo paper 80-100 g/m2 (~0.1 mm): 8 layers make 0.8 mm, but the folds
  spring - the stack is 3.0 mm in the middle and up to 4.4 mm at the folds (for looks).
- diagram on the top sheet: per ESKD (GOST 2.728, 2.730, 2.743, 2.723, 2.721): common-emitter stages
  (resistors 4 x 10 mm, transistors in a D 12 circle), an IC with pin fields, a tank circuit, a
  detector, a transformer, a rectifier, a connector and a bundle, dash-dot unit frames, oscillograms
  and a voltage table (as on the reference). Reference designators are numbers only, the title block
  fields are empty, the designation is digits only. Red pencil (a circled stage, a corrected value),
  ticks in plain pencil, finger marks at the corner.
- compact disc: IEC 60908 / ECMA-130: D 120 x 1.2 mm, hole D 15, a transparent clamping zone up to
  D 33, a mirror band up to D 41; a paper label D 117 with a D 41 hole (like late-90s CD-R labels):
  white, with an orange stripe - the "Electronics" line colour, like the stripe of the M49 tag - and a
  number in marker by hand (digits). The disc lies label up; the rainbow is on the mirror band and the
  rim from above and on the data side from below (seen under the edge that sticks out past the sheet
  by ~17 mm). The diagram under the disc shows through the transparent clamping zone (baked into the
  image).
- camoGround is the disc label (not the blueprint paper): a procedural colour `#(argb,...)` on the
  blueprint would wipe out the diagram itself, while a coloured label on a CD-R is normal. By default
  the selection holds the baked atlas (a white label with an orange stripe).

Detailing: "dayz" look (rvmat from the profile, the paper highlight ~0.03 - the low end of vanilla);
- stack edges follow how the sheet is folded (m64_layout.py, layers L1-L8): on top the fold in half is
  a roll with a radius of half the thickness; left and right are accordion loops as a shallow barrel
  (the loops themselves are relief and shadows by z in the material); at the bottom eight cut edges
  fan out up to 1.3 mm, unevenly along the edge;
- the top sheet does not lie flat: a gentle wave up to 0.45 mm (upwards only, held down at the folds)
  and a bend of the free edges (right and bottom) up to 0.6 mm; the bent-up corner has denser grid
  lines (the edge is an arc, not kinks); the sheet is above the stack by construction (the stack top
  is flat cells, all its lines are in the sheet grid);
- disc: 64 segments, a chamfer on the rim on top, 32 at the hole; it rests on the real triangles of
  the sheet in both LODs (a ray onto the grid, the lowest tangent plane), not on a bilinear estimate;
- the paper is aged: yellowed in blotches (like the reference), the print faded and worn at the folds,
  the folds rubbed through, grey from hands at the free edges and the bent corner, rusty specks of old
  paper, a mug ring, two creases (an old diagonal one and one along the line of the bent corner); on
  the disc, circular scratches, fingerprints, dust, the relief of the moulded rings in the clamping
  zone, a rubbed label edge;
- no vanilla items: the carrier is a small item itself and is carried to the terminal - a pen or a
  battery on top would fall off. There are no lamps, screens or moving parts, so there is no "work"
  view.

State is `used but intact`. LODs (a small item): near 1418 triangles (the small-item limit is 1500)
and middle 452 (~32 %).

Blender axes: X is the sheet width, Y is the height (the top of the sheet at +Y, the bottom towards the
viewer, -Y), Z is up. The origin is the centre of the stack on the ground: autocenter = 0 (in
Geometry), boundingbox_min at the bottom. Shared dimensions: m64_layout.py (also read by
make_decals.py).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import bmesh  # noqa: E402,F401
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import m64_layout as ly  # noqa: E402
from mathutils import Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
SCHEM = os.path.join(WORK, "schematic.png")
SEL = "camoGround"                 # disc label: the line colour is set by the config (hiddenSelections)

# k is the number of points of the stack edge profile (top ... ground), seg / hole are the disc segments
# along the rim and at the hole
LOD_SPECS = [dict(lod=0, seg=64, hole=32, chamfer=True, k=6),
             dict(lod=1, seg=32, hole=16, chamfer=False, k=3)]

# density scale: the top of the sheet with the diagram and the disc matter most; backs and hidden parts get
# almost no space
REGIONS = {
    "sheet": ("sheet", 3.2), "sheet_under": ("back", 0.6), "sheet_edge": ("cut", 0.3),
    "stack_top": ("back", 0.3), "stack_edge": ("edge", 2.4), "stack_bottom": ("back", 0.4),
    "cd_label": ("cd_label", 1.8), "cd_hub": ("cd_hub", 2.4), "cd_data": ("cd_data", 1.6),
    "cd_edge": ("cd_edge", 0.6), "cd_rim": ("cd_rim", 0.15),
}

# stains and creases of the sheet (world x, y, m)
COFFEE = ((-0.052, -0.040), 0.0335, 0.0016)          # mug ring: centre, radius, ring width
CREASES = [((-0.098, 0.030), (0.012, -0.142), 0.0007),   # an old diagonal crease across the sheet
           ((0.041, ly.Y0), (ly.X1, -0.0698), 0.0005)]    # along the line of the bent corner (lift 1/16)


# --- nodes ----------------------------------------------------------------------------------------
def attr_uv(t, name="pp"):
    a = t.node("ShaderNodeAttribute")
    a.attribute_type = "GEOMETRY"
    a.attribute_name = name
    sep = t.node("ShaderNodeSeparateXYZ")
    t.link(a.outputs["Vector"], sep.inputs[0])
    return sep.outputs["X"], sep.outputs["Y"]


def combine(t, x, y, z=0.0):
    c = t.node("ShaderNodeCombineXYZ")
    for i, s in enumerate((x, y, z)):
        if isinstance(s, (int, float)):
            c.inputs[i].default_value = s
        else:
            t.link(s, c.inputs[i])
    return c.outputs[0]


def hypot(t, a, b):
    return t.math("SQRT", t.math("ADD", t.math("MULTIPLY", a, a), t.math("MULTIPLY", b, b)))


# --- paper ----------------------------------------------------------------------------------------
def paper_base(t, vec, color, seed_scale=1.0):
    """Diazo paper: cloudy tone and fibre."""
    cloud = t.maprange(t.noise(vec, 5.0 * seed_scale, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0)
    col = t.mixc(cloud, tuple(c * 0.94 for c in color[:3]) + (1,), color)
    fib = t.noise(t.stretch(vec, 1.0, 0.4, 1.0), 260.0, 3.0, 0.6)
    col = t.mixc(t.math("MULTIPLY", t.maprange(fib, 0.45, 0.8, 0.0, 1.0), 0.18), col,
                 tuple(min(1.0, c * 1.12) for c in color[:3]) + (1,))
    return col, fib


def aged(t, vec, col, k=1.0):
    """The "dayz" profile for paper: the colour is muted (desaturated, darker - as in kmats.dayz_layers) and
    yellowed in blotches by light."""
    gray = t.node("ShaderNodeRGBToBW")
    t.link(col, gray.inputs[0])
    col = t.mixc(0.14 * k, col, gray.outputs[0])
    col = t.mixc(0.10 * k, col, (0, 0, 0, 1))
    yel = t.maprange(t.noise(vec, 3.0, 4.0, 0.55), 0.35, 0.72, 0.16, 0.46)
    col = t.mixc(t.math("MULTIPLY", yel, k), col, kmats.lin(ly.AGED))
    # grey-brown stains: the sheet has passed through hands and lain in damp
    mott = t.maprange(t.noise(vec, 9.0, 5.0, 0.6), 0.45, 0.75, 0.0, 0.18)
    return t.mixc(t.math("MULTIPLY", mott, k), col, kmats.lin((150, 142, 124)))


def edge_fade(t, x, y, vec, col, width=0.022, amount=0.75):
    """Fading and yellowing towards the cut edges and folds: blueprints yellow in light."""
    dx = t.math("MINIMUM", t.math("SUBTRACT", x, ly.X0), t.math("SUBTRACT", ly.X1, x))
    dy = t.math("MINIMUM", t.math("SUBTRACT", y, ly.Y0), t.math("SUBTRACT", ly.Y1, y))
    e = t.maprange(t.math("MINIMUM", dx, dy), 0.0, width, 1.0, 0.0)
    e = t.math("MULTIPLY", e, t.maprange(t.noise(vec, 30.0, 5.0, 0.6), 0.3, 0.7, 0.5, 1.0))
    return t.mixc(t.math("MULTIPLY", e, amount), col, kmats.lin((208, 194, 158)))


def fold_rub(t, x, y, vec, w=0.005):
    """0..1 at the folds (left edge and top): the paper is rubbed through and the print worn off there."""
    f = t.math("MAXIMUM", t.maprange(t.math("SUBTRACT", x, ly.X0), 0.0, w, 1.0, 0.0),
               t.maprange(t.math("SUBTRACT", ly.Y1, y), 0.0, w, 1.0, 0.0))
    return t.math("MULTIPLY", f, t.maprange(t.noise(vec, 60.0, 6.0, 0.7), 0.3, 0.7, 0.25, 1.0))


def handling(t, x, y, vec):
    """0..1 where the sheet is handled: the free edges (bottom, right) and the bent corner."""
    e = t.math("MAXIMUM", t.maprange(t.math("SUBTRACT", y, ly.Y0), 0.0, 0.040, 1.0, 0.0),
               t.maprange(t.math("SUBTRACT", ly.X1, x), 0.0, 0.030, 0.8, 0.0))
    rc = hypot(t, t.math("SUBTRACT", x, ly.X1), t.math("SUBTRACT", y, ly.Y0))
    e = t.math("MAXIMUM", e, t.maprange(rc, 0.0, 0.09, 1.0, 0.0))
    return t.math("MULTIPLY", e, t.maprange(t.noise(vec, 22.0, 6.0, 0.65), 0.38, 0.72, 0.0, 1.0))


def ring_stain(t, x, y, vec, c, r, w):
    """Mug ring: a ring (darker at the outer edge, as coffee dries) and a pale fill; the ring is ragged -
    missing in places."""
    rr = hypot(t, t.math("SUBTRACT", x, c[0]), t.math("SUBTRACT", y, c[1]))
    rr = t.math("ADD", rr, t.math("MULTIPLY", t.math("SUBTRACT", t.noise(vec, 45.0, 3.0, 0.5), 0.5), 0.004))
    d = t.math("SUBTRACT", rr, r)
    ring = t.maprange(t.math("ABSOLUTE", d), 0.0, w, 1.0, 0.0)
    ring = t.math("MULTIPLY", ring, t.maprange(d, -w, w * 0.5, 0.45, 1.0))
    fill = t.maprange(d, -0.004, 0.0, 1.0, 0.0)
    part = t.maprange(t.noise(vec, 11.0, 2.0, 0.5), 0.36, 0.56, 0.0, 1.0)
    return t.math("MULTIPLY", ring, part), t.math("MULTIPLY", fill, part)


def crease(t, x, y, vec, a, b, w):
    """Crease along the segment a-b: the line wanders slightly (up to 0.6 mm) and fades towards the ends and
    in places. Returns (the line itself, a bend band ~3 mm around it)."""
    ex, ey = b[0] - a[0], b[1] - a[1]
    l2 = ex * ex + ey * ey
    ln = math.sqrt(l2)
    px, py = t.math("SUBTRACT", x, a[0]), t.math("SUBTRACT", y, a[1])
    d = t.math("ADD", t.math("MULTIPLY", px, -ey / ln), t.math("MULTIPLY", py, ex / ln))
    d = t.math("ADD", d, t.math("MULTIPLY", t.math("SUBTRACT", t.noise(vec, 9.0, 3.0, 0.5), 0.5), 0.0012))
    s = t.math("ADD", t.math("MULTIPLY", px, ex / l2), t.math("MULTIPLY", py, ey / l2))
    ad = t.math("ABSOLUTE", d)
    fade = t.math("MULTIPLY", t.maprange(s, 0.0, 0.2, 0.0, 1.0), t.maprange(s, 0.8, 1.0, 1.0, 0.0))
    fade = t.math("MULTIPLY", fade, t.maprange(t.noise(vec, 6.0, 3.0, 0.5), 0.3, 0.6, 0.25, 1.0))
    return (t.math("MULTIPLY", t.maprange(ad, 0.0, w, 1.0, 0.0), fade),
            t.math("MULTIPLY", t.maprange(ad, 0.0, 0.0016, 1.0, 0.0), fade))


def paper_weather(t, col, vec, sep, nsep, dust=0.06, cav=0.35):
    """Dust on up-facing surfaces and dirt in crevices (shading) - like kmats.weather, but without the
    profile layers meant for metal (scratches, streaks, grease spots): paper has its own wear (build_sheet)."""
    if kmats.LOOK["name"] == "dayz":
        dust, cav = dust * kmats.LOOK["dust_k"], cav * kmats.LOOK["cav_k"]
    up = t.maprange(nsep.outputs["Z"], 0.4, 0.9, 0.0, 1.0)
    dn = t.maprange(t.noise(vec, 4.0, 6.0, 0.6), 0.35, 0.7, 0.4, 1.0)
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", up, dn), dust), col, kmats.DUST)
    c = t.maprange(t.cavity(0.03), 0.15, 0.6, 0.0, 1.0)
    gr = t.math("MULTIPLY", t.math("MULTIPLY", c, cav), t.maprange(t.noise(vec, 7.0, 8.0, 0.6), 0.3, 0.7, 0.5, 1.0))
    return t.mixc(gr, col, kmats.GRIME), gr


def build_sheet(mat, origin, seed=1.0):
    """Top of the folded sheet: a blueprint - the diagram from schematic.png by world x, y (lifting the
    corner changes only z); the paper has yellowed in blotches and towards the edges, the print has faded
    and is worn and rubbed through at the folds (left and top); grey from hands at the free edges and the
    corner, rusty specks, the mug ring, creases."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    x, y = sep.outputs["X"], sep.outputs["Y"]
    col, fib = paper_base(t, vec, kmats.lin(ly.PAPER))
    col = aged(t, vec, col)
    rub = fold_rub(t, x, y, vec)
    c, a = t.image(SCHEM, x, y, (0.0, 0.0), (ly.PW, ly.PH))
    fade = t.maprange(t.noise(vec, 8.0, 4.0, 0.5), 0.3, 0.7, 0.68, 1.0)
    a = t.math("MULTIPLY", t.math("MULTIPLY", a, fade), t.math("SUBTRACT", 1.0, t.math("MULTIPLY", rub, 0.7)))
    col = t.mixc(a, col, c)
    col = edge_fade(t, x, y, vec, col)
    col = t.mixc(t.math("MULTIPLY", rub, 0.38), col, kmats.lin((170, 168, 158)))
    ring, fill = ring_stain(t, x, y, vec, *COFFEE)
    col = t.mixc(t.math("MULTIPLY", fill, 0.09), col, kmats.lin((176, 140, 92)))
    col = t.mixc(t.math("MULTIPLY", ring, 0.34), col, kmats.lin((132, 92, 54)))
    fox = t.math("MAXIMUM", t.step(t.noise(vec, 150.0, 2.0, 0.5), 0.715, 0.735),
                 t.math("MULTIPLY", t.step(t.noise(vec, 38.0, 3.0, 0.5), 0.735, 0.78), 0.45))
    col = t.mixc(t.math("MULTIPLY", fox, 0.35), col, kmats.lin((160, 118, 70)))
    hand = handling(t, x, y, vec)
    col = t.mixc(t.math("MULTIPLY", hand, 0.42), col, kmats.lin((112, 104, 92)))
    cr = band = None
    for pa, pb, w in CREASES:
        ln, bd = crease(t, x, y, vec, pa, pb, w)
        cr = ln if cr is None else t.math("MAXIMUM", cr, ln)
        band = bd if band is None else t.math("MAXIMUM", band, bd)
    col = t.mixc(t.math("ADD", t.math("MULTIPLY", cr, 0.10), t.math("MULTIPLY", band, 0.05)), col,
                 kmats.lin((120, 118, 112)))
    col, _ = paper_weather(t, col, vec, sep, nsep, dust=0.06, cav=0.35)
    gl = t.math("ADD", 0.07, t.math("ADD", t.math("MULTIPLY", a, 0.03), t.math("MULTIPLY", hand, 0.04)))
    sp = t.math("ADD", 0.035, t.math("MULTIPLY", hand, 0.03))
    cockle = t.math("MULTIPLY", t.noise(vec, 24.0, 3.0, 0.5), 0.10)            # paper is cockled
    h = t.math("ADD", t.math("MULTIPLY", fib, 0.06), t.math("ADD", t.math("MULTIPLY", rub, -0.15), cockle))
    h = t.math("ADD", h, t.math("ADD", t.math("ADD", t.math("MULTIPLY", cr, -0.25), t.math("MULTIPLY", band, -0.18)),
                                    t.math("MULTIPLY", ring, 0.08)))
    return kmats.out(t, col, gl, sp, h)


def build_back(mat, origin, seed=2.0):
    """Back of the sheet (and the top of the stack under the bent corner): lighter, the print barely shows
    through the paper (mirrored), yellowed less than the face."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    x, y = sep.outputs["X"], sep.outputs["Y"]
    col, fib = paper_base(t, vec, kmats.lin(ly.PAPER_BACK), 1.3)
    col = aged(t, vec, col, 0.7)
    c, a = t.image(SCHEM, x, y, (0.0, 0.0), (-ly.PW, ly.PH))
    col = t.mixc(t.math("MULTIPLY", a, 0.08), col, c)
    col = edge_fade(t, x, y, vec, col, 0.010, 0.4)
    fox = t.step(t.noise(vec, 150.0, 2.0, 0.5), 0.72, 0.74)
    col = t.mixc(t.math("MULTIPLY", fox, 0.3), col, kmats.lin((160, 118, 70)))
    col, _ = paper_weather(t, col, vec, sep, nsep, dust=0.05, cav=0.45)
    return kmats.out(t, col, 0.06, 0.03, t.math("MULTIPLY", fib, 0.05))


def build_edge(mat, origin, seed=3.0):
    """Stack edges by side (by normal): at the bottom, towards the viewer, eight fanned cut edges with a
    shadow under each sheet; left and right, accordion loops (a roll per two sheets, a dark joint between
    loops); on top, the fold in half, a smooth rubbed roll. The cut edges are darkened by hands, with dust
    near the ground."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    z = sep.outputs["Z"]
    w_cut = t.maprange(nsep.outputs["Y"], -0.35, -0.75, 0.0, 1.0)
    w_side = t.maprange(t.math("ABSOLUTE", nsep.outputs["X"]), 0.35, 0.75, 0.0, 1.0)
    along = t.stretch(vec, 1.0, 1.0, 0.05)
    wob = t.math("ADD", t.math("MULTIPLY", t.math("SUBTRACT", t.noise(along, 35.0, 3.0, 0.5), 0.5), 0.0005),
                 t.math("MULTIPLY", t.math("SUBTRACT", t.noise(along, 110.0, 2.0, 0.5), 0.5), 0.00022))
    zw = t.math("ADD", z, wob)
    q = t.math("FRACT", t.math("DIVIDE", zw, 0.00043))
    gap = t.math("MULTIPLY", t.maprange(q, 0.0, 0.2, 1.0, 0.0),
                 t.maprange(t.noise(vec, 50.0, 3.0, 0.5), 0.3, 0.7, 0.55, 1.0))
    q2 = t.math("FRACT", t.math("DIVIDE", zw, 0.00098))
    loop = t.math("SINE", t.math("MULTIPLY", q2, math.pi))
    loop_gap = t.maprange(loop, 0.0, 0.35, 1.0, 0.0)
    aged_edge = t.mixc(t.maprange(t.noise(vec, 14.0, 4.0, 0.5), 0.3, 0.7, 0.35, 0.75), kmats.lin((188, 190, 188)),
                       kmats.lin(ly.AGED))
    cut = t.mixc(t.math("MULTIPLY", gap, 0.75), aged_edge, kmats.lin((86, 84, 80)))
    side = t.mixc(t.math("MULTIPLY", loop_gap, 0.7), t.mixc(0.15, aged_edge, (1, 1, 1, 1)), kmats.lin((92, 90, 86)))
    roll = t.mixc(t.maprange(t.noise(vec, 60.0, 5.0, 0.6), 0.3, 0.7, 0.2, 0.5), kmats.lin((180, 188, 198)),
                  kmats.lin((168, 168, 160)))
    col = t.mixc(w_cut, roll, cut)
    col = t.mixc(w_side, col, side)
    hand = t.math("MULTIPLY", t.maprange(t.noise(vec, 18.0, 6.0, 0.65), 0.4, 0.75, 0.0, 1.0),
                  t.math("ADD", 0.35, t.math("MULTIPLY", w_cut, 0.65)))
    col = t.mixc(t.math("MULTIPLY", hand, 0.45), col, kmats.lin((110, 102, 90)))
    col = t.mixc(t.math("MULTIPLY", t.maprange(z, 0.0, 0.0012, 1.0, 0.0), 0.25), col, kmats.DUST)
    col, _ = paper_weather(t, col, vec, sep, nsep, dust=0.04, cav=0.3)
    h = t.math("ADD", t.math("MULTIPLY", t.math("MULTIPLY", gap, w_cut), -0.5),
               t.math("MULTIPLY", t.math("MULTIPLY", loop, w_side), 0.35))
    return kmats.out(t, col, 0.06, 0.03, h)


def build_cut(mat, origin, seed=3.9):
    """Cut edge of the top sheet (a 0.2 mm edge): light paper, yellowed, grey from hands."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    col = t.mixc(t.maprange(t.noise(vec, 14.0, 4.0, 0.5), 0.3, 0.7, 0.3, 0.7), kmats.lin((196, 198, 196)),
                 kmats.lin(ly.AGED))
    col = t.mixc(t.math("MULTIPLY", t.maprange(t.noise(vec, 25.0, 5.0, 0.6), 0.4, 0.75, 0.0, 1.0), 0.4), col,
                 kmats.lin((126, 120, 108)))
    col, _ = paper_weather(t, col, vec, sep, nsep, dust=0.0, cav=0.3)
    return kmats.out(t, col, 0.05, 0.03, 0.0)


# --- disc -----------------------------------------------------------------------------------------
def cd_wear(t, vec, u, v, scratch=0.5, smudge=0.5):
    """Circular scratches (noise in the polar axes of the disc, seamless), fingerprints, dust specks; and
    the radius."""
    r = hypot(t, u, v)
    inv = t.math("DIVIDE", 1.5, t.math("MAXIMUM", r, 0.001))
    pol = combine(t, t.math("MULTIPLY", u, inv), t.math("MULTIPLY", v, inv), t.math("MULTIPLY", r, 1400.0))
    sc = t.step(t.noise(pol, 1.0, 2.0, 0.5), 0.70, 0.715)
    sc = t.math("MULTIPLY", sc, t.maprange(t.noise(vec, 7.0, 3.0, 0.5), 0.4, 0.7, 0.0, scratch))
    sm = t.math("MULTIPLY", t.step(t.noise(vec, 16.0, 5.0, 0.6), 0.58, 0.70), smudge)
    dust = t.step(t.noise(vec, 240.0, 2.0, 0.5), 0.73, 0.75)
    return sc, sm, dust, r


def build_cd(mat, origin, img, gloss=0.85, spec=0.75, seed=4.0, rings=False):
    """Disc from the image in disc axes (attribute pp): the polycarbonate and the mirror zones are glossy,
    the rainbow is slightly muted; scratches, fingerprints and dust specks kill the gloss. rings is the
    relief of the moulded ring and the stacking ring in the clamping zone."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    u, v = attr_uv(t)
    c, a = t.image(os.path.join(WORK, img), u, v, (0.0, 0.0), (ly.CD_D, ly.CD_D))
    gray = t.node("ShaderNodeRGBToBW")
    t.link(c, gray.inputs[0])
    col = t.mixc(0.12, c, gray.outputs[0])
    sc, sm, dust, r = cd_wear(t, vec, u, v)
    col = t.mixc(t.math("MULTIPLY", sm, 0.14), col, kmats.lin((176, 174, 170)))
    col = t.mixc(t.math("MULTIPLY", sc, 0.45), col, kmats.lin((214, 214, 216)))
    col = t.mixc(t.math("MULTIPLY", dust, 0.5), col, kmats.lin((170, 166, 158)))
    loss = t.math("ADD", t.math("ADD", t.math("MULTIPLY", sm, 0.30), t.math("MULTIPLY", sc, 0.25)),
                  t.math("MULTIPLY", dust, 0.4))
    gl = t.math("SUBTRACT", gloss, loss)
    sp = t.math("SUBTRACT", spec, t.math("ADD", t.math("MULTIPLY", sm, 0.25), t.math("MULTIPLY", dust, 0.3)))
    h = t.math("MULTIPLY", sc, -0.1)
    if rings:
        rg = t.math("MAXIMUM", t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", r, ly.R_MOLD)), 0.0, 0.0004, 1.0, 0.0),
                    t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", r, ly.R_STACK)), 0.0, 0.0006, 1.0, 0.0))
        h = t.math("ADD", h, t.math("MULTIPLY", rg, 0.35))
    return kmats.out(t, col, gl, sp, h)


def build_cd_label(mat, origin, seed=4.2):
    """Label (camoGround): paper from cd_top.png, slightly yellowed, fingerprints, a rubbed edge; beyond the
    outer edge of the label (R_LABEL1) is the glossy polycarbonate rim with a rainbow."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    u, v = attr_uv(t)
    c, a = t.image(os.path.join(WORK, "cd_top.png"), u, v, (0.0, 0.0), (ly.CD_D, ly.CD_D))
    sc, sm, dust, r = cd_wear(t, vec, u, v, 0.3, 0.4)
    rim = t.maprange(r, ly.R_LABEL1 - 0.00015, ly.R_LABEL1 + 0.00015, 0.0, 1.0)
    fib = t.noise(vec, 320.0, 3.0, 0.6)
    col = t.mixc(t.math("MULTIPLY", t.maprange(fib, 0.5, 0.8, 0.0, 1.0), 0.10), c, kmats.lin((222, 220, 210)))
    col = t.mixc(t.maprange(t.noise(vec, 6.0, 3.0, 0.5), 0.3, 0.7, 0.04, 0.16), col, kmats.lin((222, 208, 168)))
    # the label edges are rubbed: at the rim and at the clamping zone (the disc is held by the edge and by
    # the centre)
    worn = t.math("MAXIMUM",
                  t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", r, ly.R_LABEL1 - 0.0004)), 0.0, 0.0012, 1.0, 0.0),
                  t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", r, ly.R_LABEL0 + 0.0004)), 0.0, 0.0010, 0.7, 0.0))
    worn = t.math("MULTIPLY", t.math("MULTIPLY", worn, t.math("SUBTRACT", 1.0, rim)),
                  t.maprange(t.noise(vec, 40.0, 4.0, 0.6), 0.35, 0.7, 0.0, 1.0))
    col = t.mixc(t.math("MULTIPLY", worn, 0.35), col, kmats.lin((120, 112, 98)))
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", sm, t.math("SUBTRACT", 1.0, rim)), 0.18), col,
                 kmats.lin((150, 144, 132)))
    col, _ = paper_weather(t, col, vec, sep, nsep, dust=0.08, cav=0.2)
    gl = t.mixf(rim, t.math("ADD", 0.12, t.math("MULTIPLY", sm, 0.06)), t.math("SUBTRACT", 0.80, t.math("MULTIPLY", sc, 0.3)))
    sp = t.mixf(rim, 0.05, 0.7)
    h = t.mixf(rim, t.math("MULTIPLY", fib, 0.05), 0.0)
    return kmats.out(t, col, gl, sp, h)


KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "sheet": (build_sheet, dict(seed=1.1)),
    "back": (build_back, dict(seed=2.3)),
    "edge": (build_edge, dict(seed=3.4)),
    "cut": (build_cut, dict(seed=3.9)),
    "cd_label": (build_cd_label, dict(seed=4.2)),
    "cd_hub": (build_cd, dict(img="cd_top.png", gloss=0.85, spec=0.75, seed=4.6, rings=True)),
    "cd_data": (build_cd, dict(img="cd_data.png", gloss=0.9, spec=0.85, seed=5.1)),
    "cd_rim": (build_cd, dict(img="cd_top.png", gloss=0.8, spec=0.7, seed=4.9)),
    "cd_edge": ("plastic", dict(color=kmats.lin((178, 182, 188)), seed=5.5, gloss=0.6, spec=0.5, dust=0.05,
                                grime=0.0, mottle=0.05, scuff=(0.80, 0.90))),
})

OBJ, NAME = "m64_carrier_electro", "ozr_carrier_electro"
# rvmat per the "dayz" profile (specular 1.0 / 80): the highlight is set by _smdi, ~0.03 for paper (the
# low end of vanilla furniture, 0.01-0.09), 0.2-0.25 for the disc (glossy devices)
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL,), hidden=(SEL,))
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


def set_pp(p, fn):
    lay = p.bm.verts.layers.float_vector.get("pp") or p.bm.verts.layers.float_vector.new("pp")
    for v in p.bm.verts:
        a, b = fn(v.co)
        v[lay] = (a, b, 0.0)


def perimeter(nx, ny):
    """Indices (i, j) around the grid edge, counter-clockwise (seen from above): bottom, right, top, left."""
    ring = [(i, 0) for i in range(nx)] + [(nx, j) for j in range(ny)]
    ring += [(i, ny) for i in range(nx, 0, -1)] + [(0, j) for j in range(ny, 0, -1)]
    return ring


# --- stack edges ----------------------------------------------------------------------------------
def _var(t, a, b):
    """Smooth scatter 0..1 along the edge (identical from run to run)."""
    return 0.5 + 0.3 * math.sin(t * a + b) + 0.2 * math.sin(t * a * 2.7 + b * 1.9)


def side_profile(kind, along, ztop, k_pts):
    """[(outward shift, m; height fraction)] from the top of the stack to the ground for edge kind
    (m64_layout: layers): top is the fold in half, a roll; left / right are accordion loops, a shallow
    barrel; bottom is cut edges, the lower sheets fan out unevenly along the edge and from layer to layer."""
    out = []
    for k in range(k_pts):
        s = k / (k_pts - 1)
        if kind == "top":
            a = math.pi * s
            out.append((ly.ROLL_K * ztop * math.sin(a), (1.0 + math.cos(a)) / 2.0))
            continue
        if kind == "bottom":
            jit = 0.00012 * math.sin(along * 173.0 + k * 2.3) if 0 < k < k_pts - 1 else 0.0
            d = ly.FAN * (0.55 + 0.45 * _var(along, 61.0, 0.4)) * s ** 0.85 + jit
        else:
            amp = ly.SIDE_L if kind == "left" else ly.SIDE_R
            d = amp * (0.8 + 0.4 * _var(along, 47.0, 1.3)) * math.sin(math.pi * s) ** 0.8 + 0.00012 * s
        out.append((d, 1.0 - s))
    return out


def edge_profile(xs, ys, i, j, ztop, k_pts):
    """Outward direction and profile at the point (i, j) of the grid edge; at a corner, the average of the
    two edges."""
    nx, ny = len(xs) - 1, len(ys) - 1
    kinds = []
    if j == 0:
        kinds.append(("bottom", Vector((0.0, -1.0, 0.0)), xs[i]))
    if j == ny:
        kinds.append(("top", Vector((0.0, 1.0, 0.0)), xs[i]))
    if i == 0:
        kinds.append(("left", Vector((-1.0, 0.0, 0.0)), ys[j]))
    if i == nx:
        kinds.append(("right", Vector((1.0, 0.0, 0.0)), ys[j]))
    profs = [side_profile(kd, al, ztop, k_pts) for kd, _, al in kinds]
    d = sum((dv for _, dv, _ in kinds), Vector()).normalized()
    prof = [(sum(p[k][0] for p in profs) / len(profs), sum(p[k][1] for p in profs) / len(profs))
            for k in range(k_pts)]
    return d, prof


# --- stack and top sheet --------------------------------------------------------------------------
def build_stack(spec):
    """Layers L2-L8: the top is flat cells (m64_layout.z_stack of the LOD), the edge is the profile along
    the border (folds, fanned cut edges), the bottom fans out from the centre."""
    lod, k_pts = spec["lod"], spec["k"]
    xs, ys = ly.STACK_GRID[lod]
    st = P("stack", "stack_top")
    bm = st.bm
    top = [[bm.verts.new((x, y, ly.z_stack(x, y, lod))) for y in ys] for x in xs]
    nx, ny = len(xs) - 1, len(ys) - 1
    for i in range(nx):
        for j in range(ny):
            face(st, [top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1]], "stack_top", (0, 0, 1))
    ring = perimeter(nx, ny)
    cols = []
    for (i, j) in ring:
        v = top[i][j]
        d, prof = edge_profile(xs, ys, i, j, v.co.z, k_pts)
        base = Vector((v.co.x, v.co.y, 0.0))
        cols.append([v] + [bm.verts.new(base + d * off + Vector((0.0, 0.0, v.co.z * h))) for off, h in prof[1:]])
    n = len(ring)
    for a in range(n):
        b = (a + 1) % n
        want = ((cols[a][0].co.x + cols[b][0].co.x) / 2, (cols[a][0].co.y + cols[b][0].co.y) / 2, 0.0)
        for k in range(k_pts - 1):
            face(st, [cols[a][k], cols[b][k], cols[b][k + 1], cols[a][k + 1]], "stack_edge", want)
    # bottom: a fan from the centre; the border has many points on one line, so a polygon would give
    # degenerate faces
    c0 = bm.verts.new((0.0, 0.0, 0.0))
    for a in range(n):
        face(st, [c0, cols[(a + 1) % n][k_pts - 1], cols[a][k_pts - 1]], "stack_bottom", (0, 0, -1))
    return [st]


def build_sheet_geo(lod):
    """Top sheet L1: the diagram on top, a thin edge; the back only under the bent corner (elsewhere the
    sheet lies on the stack and its underside is not visible). The bottom right corner is bent up, the
    sheet is wavy."""
    xs, ys = ly.GRID[lod]
    sh = P("sheet", "sheet")
    bm = sh.bm
    h = ly.PAPER_T / 2
    zc = [[ly.z_sheet(x, y, lod) for y in ys] for x in xs]
    top = [[bm.verts.new((x, y, zc[i][j] + h)) for j, y in enumerate(ys)] for i, x in enumerate(xs)]
    bot = {}

    def b(i, j):
        if (i, j) not in bot:
            bot[(i, j)] = bm.verts.new((xs[i], ys[j], zc[i][j] - h))
        return bot[(i, j)]
    nx, ny = len(xs) - 1, len(ys) - 1
    for i in range(nx):
        for j in range(ny):
            face(sh, [top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1]], "sheet", (0, 0, 1))
            if max(ly.lift(xs[a], ys[c]) for a in (i, i + 1) for c in (j, j + 1)) > 0.0:
                face(sh, [b(i, j), b(i + 1, j), b(i + 1, j + 1), b(i, j + 1)], "sheet_under", (0, 0, -1))
    ring = perimeter(nx, ny)
    for k in range(len(ring)):
        (i, j), (i2, j2) = ring[k], ring[(k + 1) % len(ring)]
        mid = (top[i][j].co + top[i2][j2].co) * 0.5
        face(sh, [top[i][j], top[i2][j2], b(i2, j2), b(i, j)], "sheet_edge", (mid.x, mid.y, 0.0))
    return [sh]


SHEETS = {}


def sheet_parts(lod):
    """The top sheet of a LOD, built once and directly on triangles: the disc rests on those same triangles
    (cd_frame)."""
    if lod not in SHEETS:
        SHEETS[lod] = build_sheet_geo(lod)
        g.triangulate(SHEETS[lod])
    return SHEETS[lod]


CD_FRAME = None


def cd_frame():
    """The plane the disc lies on: the lowest (the centre lowest of all) of the tangent planes to the top
    sheets of both LODs. Heights are taken by a ray onto their real triangles and the vertices under the
    disc (the surface is piecewise flat: it can rise above the plane only at a vertex or at the disc
    edge), so the disc does not sink into the sheet in either LOD."""
    global CD_FRAME
    if CD_FRAME is not None:
        return CD_FRAME
    import numpy as np
    sheets = [sheet_parts(lod)[0] for lod in (0, 1)]
    trees = [BVHTree.FromBMesh(p.bm) for p in sheets]

    def top(x, y):
        z = 0.0
        for tr in trees:
            hit = tr.ray_cast(Vector((x, y, 0.2)), Vector((0.0, 0.0, -1.0)))
            if hit[0] is not None:
                z = max(z, hit[0].z)
        return z
    pts = []
    for r in sorted({min(ly.CD_R, ly.R_HOLE + 0.004 * k) for k in range(15)}):
        for k in range(120):
            a = 2 * math.pi * k / 120
            x, y = ly.cd_world(r * math.cos(a), r * math.sin(a))
            pts.append((x, y, top(x, y)))
    for p in sheets:
        for v in p.bm.verts:
            u, w = ly.cd_local(v.co.x, v.co.y)
            if ly.R_HOLE <= math.hypot(u, w) <= ly.CD_R:
                pts.append((v.co.x, v.co.y, v.co.z))
    arr = np.array(pts)
    dx, dy, s = arr[:, 0] - ly.CD_C[0], arr[:, 1] - ly.CD_C[1], arr[:, 2]
    cs = np.arange(-40, 41) * 0.0008
    best = None
    for ib in range(-40, 41):
        bb = ib * 0.0008
        lift = (s[None, :] - bb * dx[None, :] - cs[:, None] * dy[None, :]).max(axis=1)
        ic = int(np.argmin(lift))
        if best is None or lift[ic] < best[0]:
            best = (float(lift[ic]), bb, float(cs[ic]))
    a, b, c = best
    n = Vector((-b, -c, 1.0)).normalized()
    ang = math.radians(ly.CD_ROT)
    u = Vector((math.cos(ang), math.sin(ang), b * math.cos(ang) + c * math.sin(ang))).normalized()
    v = n.cross(u).normalized()
    print("CD rests at z %.4f, slope x %.4f y %.4f (%.2f deg), %d support samples"
          % (a, b, c, math.degrees(math.acos(n.z)), len(pts)))
    CD_FRAME = g.Frame((ly.CD_C[0], ly.CD_C[1], a + 0.00004), u, v, n)
    return CD_FRAME


def build_cd_geo(spec):
    """Disc: on top the clamping zone with the mirror band and the label (camoGround), the rim chamfer;
    below, the data side, the rim end and the hole wall. The hole has half as many segments, and the rings
    are stitched with a strip of triangles."""
    fr = cd_frame()
    n, nh, ch = spec["seg"], spec["hole"], spec["chamfer"]
    hub = P("cd_hub", "cd_hub")
    lab = P("cd_label", "cd_label", group=SEL)
    body = P("cd", "cd_edge")
    up, dn = tuple(fr.n), tuple(-fr.n)

    def ring(p, r, z, m):
        return [p.bm.verts.new(fr.p(r * math.cos(2 * math.pi * k / m), r * math.sin(2 * math.pi * k / m), z))
                for k in range(m)]

    def radial(k, m, s):
        a = 2 * math.pi * (k + 0.5) / m
        return (fr.u * math.cos(a) + fr.v * math.sin(a)) * s

    def band(p, ra, rb, region, want):
        m = len(ra)
        for k in range(m):
            k2 = (k + 1) % m
            face(p, [ra[k], ra[k2], rb[k2], rb[k]], region, tuple(want(k)))

    def stitch(p, ra, rb, region, want):
        """Rings with different point counts (angles from 0 ascending): a strip of triangles."""
        na, nb = len(ra), len(rb)
        ia = ib = 0
        while ia < na or ib < nb:
            if ib >= nb or (ia < na and (ia + 1) * nb <= (ib + 1) * na):
                face(p, [ra[ia], ra[(ia + 1) % na], rb[ib % nb]], region, want)
                ia += 1
            else:
                face(p, [ra[ia % na], rb[(ib + 1) % nb], rb[ib]], region, want)
                ib += 1
    stitch(hub, ring(hub, ly.R_HOLE, ly.CD_T, nh), ring(hub, ly.R_LABEL0, ly.CD_T, n), "cd_hub", up)
    re = ly.CD_R - (ly.CD_CH_R if ch else 0.0)
    band(lab, ring(lab, ly.R_LABEL0, ly.CD_T, n), ring(lab, re, ly.CD_T, n), "cd_label", lambda k: fr.n)
    if ch:
        rim = ring(body, ly.CD_R, ly.CD_T - ly.CD_CH_Z, n)
        band(body, ring(body, re, ly.CD_T, n), rim, "cd_rim", lambda k: radial(k, n, 0.6) + fr.n * 0.8)
    else:
        rim = ring(body, ly.CD_R, ly.CD_T, n)
    bot = ring(body, ly.CD_R, 0.0, n)
    band(body, rim, bot, "cd_edge", lambda k: radial(k, n, 1.0))
    hb = ring(body, ly.R_HOLE, 0.0, nh)
    band(body, ring(body, ly.R_HOLE, ly.CD_T, nh), hb, "cd_edge", lambda k: radial(k, nh, -1.0))
    stitch(body, hb, bot, "cd_data", dn)
    for p in (hub, lab, body):
        set_pp(p, lambda co: ((co - fr.o).dot(fr.u), (co - fr.o).dot(fr.v)))
    return [hub, lab, body]


def build_lod(spec):
    parts = build_stack(spec) + sheet_parts(spec["lod"]) + build_cd_geo(spec)
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


INV_VIEW = (0.01, -0.36, 0.50)


def collision():
    """One convex hull over the vertices of the near LOD (sheet and disc). The mass is the class weight,
    0.3 kg (OZL_Carrier_Base); the hit sound and penetration are thin fabric, as for the vanilla book
    (Book_kniga.p3d: fabric_thin) and the M62 carrier."""
    comps = [(BOUNDS["pts"], kx.PEN + r"\fabric_thin.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    c = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, hi[2] / 2)
    memory = {
        # inventory preview camera: from the front and above - the whole sheet, the disc in the top right corner
        "invView": [INV_VIEW],
        "ce_center": [c],
        "ce_radius": [(c[0] + 0.5 * math.dist(lo, hi), c[1], c[2])],
    }
    print("bbox %.4f..%.4f x %.4f..%.4f x 0..%.4f, preview aspect from invView %.2f (2x2 cell: ~1)"
          % (lo[0], hi[0], lo[1], hi[1], hi[2], preview_aspect(bbox, INV_VIEW)))
    return comps, 0.3, memory, bbox


# the first four are the --look preview: general view, the disc close up, the bent corner with layers,
# the edges (folds and fanned cut edges) at the bottom left corner
SHOTS = [
    ("front", (-0.22, -0.44, 0.30), (0.01, 0.0, 0.003), 45),
    ("cd", (0.17, -0.07, 0.19), (0.060, 0.075, 0.005), 50),
    ("corner", (0.24, -0.30, 0.09), (0.075, -0.115, 0.004), 50),
    ("edge", (-0.205, -0.245, 0.045), (-0.075, -0.125, 0.002), 55),
    ("top", (0.01, 0.0, 0.70), (0.01, 0.0, 0.0), 40),
    ("inv", INV_VIEW, (0.01, 0.0, 0.003), 36),
]

if __name__ == "__main__":
    M.look_shots = (4, 2)
    M.run(build_lod, collision, SHOTS, row_step=0.32, row_shot=((0.16, -0.75, 0.55), (0.16, 0.0, 0.0)))
