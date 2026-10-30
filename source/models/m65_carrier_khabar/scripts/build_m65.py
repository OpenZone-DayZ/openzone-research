"""M65 - "Khabar" carrier (OZL_Carrier_Khabar): the carrier of the "Khabar" line, shared by the factions
- a stack of sheets from pads, handwritten in columns of prices, on a cardboard backing board under
a black binder clip. It should look like a price list: several pages of illegible handwritten text
held by a binder. A portable 2x2 item.

    blender --background --python build_m65.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (sheets with handwriting, the print
on the board).

Target: ~15 x 21 x 1 cm (A5), 5-8 notebook or typed sheets written over by hand illegibly: columns of
lines with prices, with digits and dot leaders on the right; squared and ruled sheets, uneven edges,
the top one folded; a 32 mm binder clip with metal handles; a cardboard backing board underneath
(camoGround); 200-400 g, 300-1000 triangles (about 1.4 k after detailing, within the small-item
limit of 0.3-1.5 k), texture 512-1024; no readable text.

Detailing: "dayz" look (matte, dirtier, coloured AO; the rvmat comes from the profile, as in the
preview); the clip is not a box: the jaws lie flat on the paper at the edge, the jaw bends and the
back corners are arcs, the jaw curls are round (10 sides); the handles are a smooth curve (a spline
through control points, denser points on the bends) rather than a polyline with kinks, the ends are
led into the curls from their outer end, the legs are slightly wider than the body; the original
rounded corner of the board is 6 segments; below the clip handle the top sheet is slightly bowed
across its width (0.8 mm), the folded corner springs in an arc (three strips of 12-18-25 degrees
instead of one plane). A small DayZ item: a vanilla ballpoint pen is tucked under the loop of the
upper clip handle (the proxy \\dz\\gear\\tools\\Pen: there is no Proxy<name> class; the model itself
sets its texture - loot_pen_co.paa in Pen.p3d, while the Pen_Black/_Red/_Green/_Blue classes only set
writingColor in the config, checked against the game's gear_tools.pbo), so the upper clip handle is
raised and rests on it (the generator computes the angle from the extent of the DayZ pen).

Reference and sizes:
- sheets: A5 (ISO 216: 148 x 210 mm) from glue-bound pads: 5 mm squares and 7 mm rules, a glue strip
  from the binding on top; six sheets. The second from the bottom is torn from a spiral pad - its left
  edge is ragged. They do not lie flat: rotated by 0.5-2.2 degrees, the third from the bottom is
  lowered by ~10 mm - its bottom with the total peeks out from under the stack. Handwriting:
  make_decals.py (modelled on a handwritten expense book with columns of prices, which gives the look
  of a "price list", and on a binder clip on a written-over stack).
- top sheet: a buyer's price list: a title with an underline and a date in digits, lines made of a
  number, squiggles for the name, a dot leader, two columns of prices, edits in red, sections, a
  radiation sign at a couple of lines. The bottom right corner is folded (legs 36 and 44 mm, the
  corner springs in an arc, ~25 degrees at the end), the bottom of the sheet stands off the stack by up
  to ~3 mm (the sheet springs under the clip); the corner of the lower sheet shows under the folded
  corner.
- backing board: an offcut of painted pressboard from an old folder (the line's camouflage is the
  camoGround selection), knife-cut to A5 with a margin: 166 x 232 mm, ~1 mm (estimate: a ~9 mm border
  at the sides and ~20 mm at the bottom so that the line colour reads); the top right corner is the
  original rounded folder corner (r 6 mm) with a remnant of printed rules, the bottom is cut slightly
  askew. On the visible strip at the bottom: a pen tested with a spiral, tally sticks, a digit in a
  circle. The colour is brown, like the paint of the M50 Khabar sample jar (the line colour is taken
  from its sample, as M62 takes the green of the M47 caps and M64 the orange of the M49 tag); darker
  than the M63 kraft.
- clip: a 32 mm binder clip (1-1/4"): width 32 mm, opening 16 mm (5/8" - the same for ACCO, Staples,
  Quill, Officemate), height with the handles 44 mm (GeM catalogue, binder clip 32 mm). The body is
  0.45 mm steel in black enamel: the back is 15 mm, the jaws are 16.5 mm from the back, with curls at
  the jaw ends holding the handle ends bent inwards. The handles are nickel-plated wire ~1.3 mm,
  41 mm from the axis, with a bulb-shaped loop (after a photo of a real clip). The upper handle is
  thrown back onto the sheets (it rests on the DayZ pen), the lower one points outwards along the
  cheek of the clip.
- it lies as if thrown: on the far edge of the board and on the lower handle, so the whole stack is
  tilted (~3 degrees, computed from the geometry).

Marks: a hand-drawn radiation sign, digits, ruling. No letters: the squiggles are loops and humps of
fluent handwriting, not one letter can be read. State is `used but intact`: the paper has yellowed
towards the edges, stains, a mug ring, greasy fingerprints, rust from the clip jaws on the top sheet;
the clip enamel is chipped to steel on the edges, occasional rust; the board edges are rubbed down to
light fibre. There are no lamps, screens or moving parts, so there is no "work" view (the carrier is
not a machine). LODs (a small item): near and middle, no far one.

Blender axes: X is the sheet width, Y is the height (the clip at +Y; the bottom of the sheets towards
the viewer, at -Y), Z is up. The origin is the centre of the board on the ground (before the tilt):
autocenter = 0 (in Geometry). Shared dimensions: m65_layout.py (also read by make_decals.py).
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
import kvanilla as kv  # noqa: E402
import m65_layout as ly  # noqa: E402
from mathutils import Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
SEL = "camoGround"                 # backing board: the line colour is set by the config (hiddenSelections)

LOD_SPECS = [dict(lod=0), dict(lod=1)]

# density scale: the top sheet matters most; for the lower sheets only the visible strips; backs, hidden
# parts and the bottom get almost no space
REGIONS = {
    **{"top_%s%s" % (r, sd): ("sheet", 1.0) for r in "tabc" for sd in "lr"},
    "top_back": ("sheet_back", 0.5),
    "flap_b": ("sheet_back", 0.9), "flap_f": ("sheet", 2.0),
    "s2_l": ("sheet", 0.35), "s2_h": ("sheet", 0.04),
    "s3_b": ("sheet", 0.85), "s3_h": ("sheet", 0.04),
    "s5_c": ("sheet", 0.85), "s5_h": ("sheet", 0.04),
    "s1_h": ("sheet", 0.04), "s4_h": ("sheet", 0.04),
    "back": ("sheet_back", 0.05), "edge": ("paper_edge", 0.3),
    "bd_l": ("board", 0.35), "bd_r": ("board", 0.35), "bd_b": ("board", 0.7), "bd_h": ("board", 0.03),
    "bd_bot": ("board_back", 0.4), "bd_edge": ("board_edge", 0.4),
    "clip": ("clip", 1.2), "clip_in": ("clip_in", 0.4),
    "wire": ("wire", 0.25),
}


# --- materials ------------------------------------------------------------------------------------
def attr_uv(t, name="pp"):
    a = t.node("ShaderNodeAttribute")
    a.attribute_type = "GEOMETRY"
    a.attribute_name = name
    sep = t.node("ShaderNodeSeparateXYZ")
    t.link(a.outputs["Vector"], sep.inputs[0])
    return sep.outputs["X"], sep.outputs["Y"]


IMG_C = (ly.SLOT_W * (ly.N_SHEETS - 1) / 2, 0.0)
IMG_S = (ly.SLOT_W * ly.N_SHEETS, ly.SLOT_H)
PAPER = kmats.lin((236, 233, 222))


def build_sheet(mat, origin, back=False, gloss=0.07, spec=0.05, seed=3.0):
    """Paper with handwriting by the attribute `pp` (the sheet cell in sheets.png): fibre, light dust, the
    pen is slightly glossy and presses into the paper. The back is the same sheet point: the handwriting
    shows through mirrored and pale."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    u, v = attr_uv(t)
    c, a = t.image(os.path.join(WORK, "sheets.png"), u, v, IMG_C, IMG_S)
    col = t.mixc(a, PAPER, c)
    dark = t.math("MULTIPLY", t.maprange(t.bw(c), 0.55, 0.25, 0.0, 1.0), a)
    if back:
        col = t.mixc(0.82, col, kmats.lin((232, 229, 216)))
        dark = t.math("MULTIPLY", dark, 0.0)
    col = t.mixc(t.math("MULTIPLY", t.noise(vec, 220.0, 3.0, 0.6), 0.10), col, kmats.lin((206, 200, 184)))
    col, _ = kmats.weather(t, col, vec, sep, nsep, 0.0, dust=0.06, grime=0.0, cav=0.25)
    gl = t.math("ADD", gloss, t.math("MULTIPLY", dark, 0.10))
    h = t.math("SUBTRACT", t.math("MULTIPLY", t.noise(vec, 300.0, 2.0, 0.5), 0.05), t.math("MULTIPLY", dark, 0.12))
    return kmats.out(t, col, gl, spec, h)


def build_board(mat, origin, color, seed=1.0, front=True, gloss=0.14, spec=0.08):
    """Pressboard: fibres and cloudy tone; the front has the print (board_print.png by `pp`, the board point
    before the tilt); the edges and corners are rubbed down to light fibre, greasy near the bottom edge."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    x, y = attr_uv(t)
    fib = t.noise(t.stretch(vec, 1.0, 0.35, 1.0), 160.0, 4.0, 0.7)
    cloud = t.maprange(t.noise(vec, 5.0, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0)
    col = t.mixc(cloud, tuple(c * 0.84 for c in color[:3]) + (1,), color)
    col = t.mixc(t.math("MULTIPLY", t.maprange(fib, 0.45, 0.8, 0.0, 1.0), 0.25), col,
                 tuple(min(1.0, c * 1.25) for c in color[:3]) + (1,))
    h = t.math("MULTIPLY", fib, 0.12)
    x0, x1, y0, y1 = -ly.BW / 2, ly.BW / 2, -ly.BH / 2, ly.BH / 2
    if front:
        gate = t.facing(nsep, "Z", 1, 0.5)
        pc, pa = t.image(os.path.join(WORK, "board_print.png"), x, y, (0.0, 0.0), (ly.BW, ly.BH))
        col = t.mixc(t.math("MULTIPLY", pa, gate), col, pc)
        # greasy near the bottom edge, where the stack is picked up
        dy = t.math("DIVIDE", t.math("SUBTRACT", y, y0), 0.022)
        grab = t.math("MULTIPLY", t.math("POWER", math.e, t.math("MULTIPLY", t.math("MULTIPLY", dy, dy), -1.0)),
                      t.maprange(t.noise(vec, 18.0, 6.0, 0.6), 0.35, 0.7, 0.2, 1.0))
        col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", grab, gate), 0.35), col, tuple(c * 0.55 for c in color[:3]) + (1,))
    dx = t.math("MINIMUM", t.math("SUBTRACT", x, x0), t.math("SUBTRACT", x1, x))
    dyy = t.math("MINIMUM", t.math("SUBTRACT", y, y0), t.math("SUBTRACT", y1, y))
    edge = t.maprange(t.math("MINIMUM", dx, dyy), 0.0, 0.0035, 1.0, 0.0)
    corner = t.maprange(t.math("ADD", dx, dyy), 0.0, 0.014, 1.0, 0.0)
    wear = t.math("MULTIPLY", t.math("MAXIMUM", edge, corner), t.maprange(t.noise(vec, 70.0, 6.0, 0.7), 0.3, 0.7, 0.3, 1.0))
    col = t.mixc(t.math("MULTIPLY", wear, 0.7), col, tuple(min(1.0, c * 1.5 + 0.06) for c in color[:3]) + (1,))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, 0.0, dust=0.10, grime=0.0, cav=0.45)
    gl = t.math("SUBTRACT", gloss, t.math("MULTIPLY", t.math("ADD", wear, dirt), gloss * 0.6))
    return kmats.out(t, col, gl, spec, h)


def build_clip(mat, origin, inner=False, seed=7.0):
    """Black enamel over steel at the scale of a 3 cm clip: chips on the edges and in patches down to the
    steel, occasional rust in the chips; darker and rustier inside."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    black = kmats.lin((16, 16, 18)) if not inner else kmats.lin((12, 12, 12))
    col = t.mixc(t.maprange(t.noise(vec, 300.0, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0), black,
                 tuple(c * 1.6 for c in black[:3]) + (1,))
    edge = t.maprange(t.edge_wear(0.0005), 0.05, 0.3, 0.0, 1.0)
    blot = t.noise(vec, 700.0, 6.0, 0.7)
    chips = t.step(t.math("ADD", t.math("MULTIPLY", blot, 0.65), t.math("MULTIPLY", edge, 0.6)), 0.64, 0.70)
    steel = kmats.lin((112, 112, 116))
    col = t.mixc(chips, col, steel)
    speck = t.step(t.noise(vec, 1300.0, 6.0, 0.7), 0.70 if not inner else 0.62, 0.75 if not inner else 0.68)
    rust_amt = t.math("MAXIMUM", t.math("MULTIPLY", chips, 0.5), speck)
    rust_col = t.ramp(t.noise(vec, 900.0, 6.0, 0.6), [(0.3, kmats.RUST[0]), (0.55, kmats.RUST[1]), (0.8, kmats.RUST[2])])
    col = t.mixc(t.math("MULTIPLY", rust_amt, 0.8), col, rust_col)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, 0.0, dust=0.05, grime=0.0, cav=0.2)
    g0, s0 = (0.55, 0.45) if not inner else (0.30, 0.25)
    gl = t.math("SUBTRACT", g0, t.math("MULTIPLY", rust_amt, g0 * 0.8))
    gl = t.math("ADD", gl, t.math("MULTIPLY", chips, 0.1))
    sp = t.math("ADD", t.math("SUBTRACT", s0, t.math("MULTIPLY", rust_amt, s0 * 0.8)), t.math("MULTIPLY", chips, 0.35))
    h = t.math("ADD", t.math("MULTIPLY", chips, -0.3), t.math("MULTIPLY", rust_amt, t.noise(vec, 2000.0, 3.0, 0.6)))
    return kmats.out(t, col, gl, sp, h)


def build_wire(mat, origin, seed=8.0):
    """Nickel-plated wire: light metal, slight darkening in patches, rust specks. In the "dayz" profile it is
    darker, like the kit's bare steel (LOOK steel), more matte, with dust on the upper side: a shiny white
    wire would look "almost white", as on M11-M32."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    dayz = kmats.LOOK["name"] == "dayz"
    k = kmats.LOOK.get("steel", 1.0) if dayz else 1.0
    hi = tuple(c * k for c in kmats.lin((170, 170, 172))[:3]) + (1,)
    lo = tuple(c * k for c in kmats.lin((122, 120, 114))[:3]) + (1,)
    tarn = t.maprange(t.noise(vec, 400.0, 4.0, 0.6), 0.35, 0.75, 0.0, 1.0)
    col = t.mixc(tarn, hi, lo)
    speck = t.step(t.noise(vec, 1500.0, 6.0, 0.7), 0.74, 0.78)
    col = t.mixc(t.math("MULTIPLY", speck, 0.8), col, kmats.RUST[1])
    g0, s0 = (0.80, 0.90)
    if dayz:
        nsep = t.normal()
        up = t.maprange(nsep.outputs["Z"], 0.4, 0.9, 0.0, 1.0)
        col = t.mixc(t.math("MULTIPLY", up, 0.18), col, kmats.DUST)
        g0, s0 = (0.70, 0.80)
    gl = t.math("SUBTRACT", g0, t.math("ADD", t.math("MULTIPLY", tarn, 0.2), t.math("MULTIPLY", speck, 0.6)))
    sp = t.math("SUBTRACT", s0, t.math("ADD", t.math("MULTIPLY", tarn, 0.25), t.math("MULTIPLY", speck, 0.7)))
    return kmats.out(t, col, gl, sp, t.math("MULTIPLY", speck, 0.2))


KINDS = kmats.std_kinds(floor_z=0.0)
BROWN = kmats.lin((98, 62, 42))                       # brown pressboard: colour of the "Khabar" line (M50 paint)
KINDS.update({
    "sheet": (build_sheet, dict(seed=3.1)),
    "sheet_back": (build_sheet, dict(back=True, seed=3.7)),
    "paper_edge": ("plastic", dict(color=kmats.lin((206, 200, 184)), seed=5.5, gloss=0.05, spec=0.03, dust=0.1,
                                   grime=0.0, mottle=0.10, scuff=(0.95, 1.0))),
    "board": (build_board, dict(color=BROWN, seed=1.3, front=True)),
    "board_back": (build_board, dict(color=kmats.lin((90, 58, 40)), seed=1.9, front=False, gloss=0.10,
                                     spec=0.06)),
    "board_edge": ("plastic", dict(color=kmats.lin((168, 130, 96)), seed=2.4, gloss=0.05, spec=0.03, dust=0.1,
                                   grime=0.0, mottle=0.14, scuff=(0.9, 1.0))),
    "clip": (build_clip, dict(seed=7.1)),
    "clip_in": (build_clip, dict(inner=True, seed=7.6)),
    "wire": (build_wire, dict(seed=8.2)),
})

OBJ, NAME = "m65_carrier_khabar", "ozr_carrier_khabar"
# "dayz" look: the rvmat comes from the profile (specular 1.0 / 80), as the --look preview computes it;
# the vanilla pen (decor) is placed after the stack is tilted, in build_lod
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL,), hidden=(SEL,))
BOUNDS = {}
TILT = {}


def P(name, region, **kw):
    return M.part(name, region, **kw)


def face(p, verts, region, want):
    f = p.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    f[p.reg] = p.region_index(region, *REGIONS[region])
    return f


# --- flat polygons --------------------------------------------------------------------------------
def clip_poly(poly, axis, c, keep_less):
    """Sutherland-Hodgman: the part of a polygon on one side of the line coord[axis] = c."""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ina = (a[axis] <= c) if keep_less else (a[axis] >= c)
        inb = (b[axis] <= c) if keep_less else (b[axis] >= c)
        if ina:
            out.append(a)
        if ina != inb:
            t = (c - a[axis]) / (b[axis] - a[axis])
            q = [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]
            q[axis] = c
            out.append(tuple(q))
    return out


def area(poly):
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                     for i in range(len(poly)))


def cells(outline, xcuts, ycuts):
    """Cut an outline (counter-clockwise) by the lines x = xcuts, y = ycuts: [(i, j, polygon)]."""
    xs = [-1e9] + sorted(xcuts) + [1e9]
    ys = [-1e9] + sorted(ycuts) + [1e9]
    res = []
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            p = list(outline)
            for axis, c, less in ((0, xs[i], False), (0, xs[i + 1], True), (1, ys[j], False), (1, ys[j + 1], True)):
                if abs(c) < 1e8 and p:
                    p = clip_poly(p, axis, c, less)
            if len(p) >= 3 and area(p) > 1e-9:
                res.append((i, j, p))
    return res


def slab(p, polys, to_xy, z_mid, th, reg_bot, reg_edge, pp_fn):
    """Sheet of thickness th from polygons [(polygon (u, v) counter-clockwise, top region)]: the top and
    bottom share vertices (welded by coordinates), the edges run along edges that have a single face.
    to_xy(u, v) -> (x, y); z_mid(u, v) is the centre line; pp_fn(u, v) -> coordinates on the paper."""
    bm = p.bm
    lay = bm.verts.layers.float_vector.get("pp") or bm.verts.layers.float_vector.new("pp")
    top, bot = {}, {}

    def key(q):
        return (round(q[0], 7), round(q[1], 7))

    def vert(store, q, dz):
        k = key(q)
        if k not in store:
            x, y = to_xy(*q)
            v = bm.verts.new((x, y, z_mid(*q) + dz))
            a, b = pp_fn(*q)
            v[lay] = (a, b, 0.0)
            store[k] = v
        return store[k]
    edges = {}
    for poly, reg in polys:
        vt = [vert(top, q, th / 2) for q in poly]
        vb = [vert(bot, q, -th / 2) for q in poly]
        face(p, vt, reg, (0, 0, 1))
        face(p, vb[::-1], reg_bot, (0, 0, -1))
        for i in range(len(poly)):
            a, b = key(poly[i]), key(poly[(i + 1) % len(poly)])
            ek = (min(a, b), max(a, b))
            edges.setdefault(ek, []).append((poly[i], poly[(i + 1) % len(poly)]))
    for ek, uses in edges.items():
        if len(uses) != 1:
            continue
        a, b = uses[0]
        xa, ya = to_xy(*a)
        xb, yb = to_xy(*b)
        out = (yb - ya, -(xb - xa), 0.0)                    # counter-clockwise outline: outwards is to the right
        face(p, [top[key(a)], top[key(b)], bot[key(b)], bot[key(a)]], reg_edge, out)


# --- backing board --------------------------------------------------------------------------------
def centroid(poly):
    return sum(q[0] for q in poly) / len(poly), sum(q[1] for q in poly) / len(poly)


def build_board(spec):
    """The backing board is the same in both LODs: the cells coincide with the atlas regions."""
    bd = P("board", "bd_h", group=SEL)
    polys = [(poly, ly.board_region(*centroid(poly))) for _, _, poly in cells(ly.board_outline(), ly.B_XCUT, ly.B_YCUT)]
    slab(bd, polys, lambda u, v: (u, v), lambda u, v: ly.BT / 2, ly.BT, "bd_bot", "bd_edge", lambda u, v: (u, v))
    return [bd]


# --- sheets ---------------------------------------------------------------------------------------
def sheet_outline(s, lod=0):
    hw, hh = ly.SW / 2, ly.SH / 2
    if s.get("ragged") and lod == 0:
        return [(hw, -hh), (hw, hh)] + ly.ragged_left()
    if s["name"] == "top":
        return [(-hw, -hh), ly.DOG_F1, ly.DOG_F2, (hw, hh), (-hw, hh)]
    return [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]


def z_sheet(s):
    if s["name"] == "top":
        return lambda u, v: s["z"] + ly.top_lift(u, v)
    return lambda u, v: s["z"]


def sheet_uv(s, x, y):
    """World point (before the tilt) -> (u, v) of sheet s: the inverse of ly.sheet_xy."""
    a = math.radians(s["rot"])
    dx, dy = x - s["c"][0], y - s["c"][1]
    return dx * math.cos(a) + dy * math.sin(a), -dx * math.sin(a) + dy * math.cos(a)


def build_sheets(spec):
    lod = spec["lod"]
    parts = []
    for s in ly.SHEETS:
        if lod == 1 and s["name"] in ("s1", "s4"):
            continue
        uc, vc = s["ucut"], s["vcut"]
        if lod == 1:                                       # middle LOD: only the cuts along atlas regions
            uc, vc = {"top": ((0.0,), (-0.0300, 0.0200, 0.0620)), "s5": ((), ())}.get(s["name"], (uc, vc))
        p = P("sheet_" + s["name"], "edge")
        polys = [(poly, ly.sheet_region(s, *centroid(poly))) for _, _, poly in cells(sheet_outline(s, lod), uc, vc)]
        slab(p, polys, lambda u, v, s=s: ly.sheet_xy(s, u, v), z_sheet(s), ly.TH,
             "top_back" if s["name"] == "top" else "back", "edge", lambda u, v, s=s: ly.pp(s, u, v))
        parts.append(p)
    parts.append(build_flap(lod))
    return parts


# the corner springs in an arc: flatter at the fold, steeper towards the end - paper, not tin; the
# height of the corner end over the sheet is ~9 mm
FLAP_PHI = (12.0, 18.0, 25.0)


def build_flap(lod=0):
    """Folded corner of the top sheet: the corner triangle is reflected across the fold line and bent away
    from the sheet; in the near LOD, three strips along the fold with a growing angle (FLAP_PHI), in the
    middle LOD one plane at DOG_PHI. The top of the corner is the back of the sheet (flap_b), the
    underside is the face with handwriting (flap_f); pp holds the corner's points on the sheet, so the
    handwriting on the corner is the one that was in the corner."""
    s = ly.SHEETS[-1]
    zf = z_sheet(s)
    a2, b2, c2 = Vector(ly.DOG_F1), Vector(ly.DOG_F2), Vector(ly.DOG_C)
    d = (b2 - a2).normalized()
    m2 = a2 + d * (c2 - a2).dot(d)                         # foot of the perpendicular from the corner
    dist = (c2 - m2).length
    mir = m2 - (c2 - m2)                                   # reflection of the corner, into the sheet

    def w3(q):
        x, y = ly.sheet_xy(s, q.x, q.y)
        return Vector((x, y, zf(q.x, q.y)))
    A, B, Mw = w3(a2), w3(b2), w3(m2)
    D3 = (B - A).normalized()
    win = w3(mir) - Mw
    win -= D3 * win.dot(D3)
    win.normalize()
    N = D3.cross(win)
    if N.z < 0:
        N = -N
    phis = FLAP_PHI if lod == 0 else (ly.DOG_PHI,)
    n = len(phis)
    prof, snorm = [Vector((0.0, 0.0, 0.0))], []
    for ph in phis:
        r = math.radians(ph)
        dk = win * math.cos(r) + N * math.sin(r)
        prof.append(prof[-1] + dk * (dist / n))
        nk = D3.cross(dk).normalized()
        snorm.append(nk if nk.dot(N) > 0 else -nk)
    vnorm = [snorm[0]] + [(snorm[k - 1] + snorm[k]).normalized() for k in range(1, n)] + [snorm[-1]]
    # corner points (u, v): boundary k is the segment E_k F_k parallel to the fold (at k/n of the distance
    # to the corner)
    rows = []
    for k in range(n + 1):
        f = k / n
        rows.append([a2 + (c2 - a2) * f] if k == n else [a2 + (c2 - a2) * f, b2 + (c2 - b2) * f])
    p = P("flap", "edge")
    lay = p.bm.verts.layers.float_vector.new("pp")

    def vert(q2, k, sg):
        foot = a2 + d * (q2 - a2).dot(d)
        v = p.bm.verts.new(w3(foot) + prof[k] + vnorm[k] * (ly.TH if sg > 0 else 0.0))   # lies on the sheet
        v[lay] = (*ly.pp(s, q2.x, q2.y), 0.0)
        return v
    top = [[vert(q, k, 1) for q in row] for k, row in enumerate(rows)]
    bot = [[vert(q, k, -1) for q in row] for k, row in enumerate(rows)]
    cen = sum((v.co for row in top for v in row), Vector()) / sum(len(r) for r in top)
    for k in range(n):
        tq = top[k] + top[k + 1][::-1]
        bq = bot[k] + bot[k + 1][::-1]
        face(p, tq, "flap_b", snorm[k])
        face(p, bq, "flap_f", -snorm[k])
        # corner edges (along the sides towards the corner); there is no edge along the fold (boundary 0)
        for side in (0, 1):
            i0 = side if len(top[k]) > side else 0
            i1 = side if len(top[k + 1]) > side else 0
            ta, tb, ba, bb = top[k][i0], top[k + 1][i1], bot[k][i0], bot[k + 1][i1]
            face(p, [ta, tb, bb, ba], "edge", (ta.co + tb.co) / 2 - cen)
    return p


# --- clip -----------------------------------------------------------------------------------------
def fillet(pts, spec):
    """Polyline (y, z) with rounded corners: spec maps an inner point number -> (radius, arc segments)."""
    out = [pts[0].copy()]
    for i in range(1, len(pts) - 1):
        r, n = spec.get(i, (0.0, 0))
        q, qa, qb = pts[i], pts[i - 1], pts[i + 1]
        d1, d2 = (q - qa).normalized(), (qb - q).normalized()
        turn = math.acos(max(-1.0, min(1.0, d1.dot(d2))))
        if r <= 0 or n <= 0 or turn < 1e-4:
            out.append(q.copy())
            continue
        tl = r * math.tan(turn / 2)
        s0, e0 = q - d1 * tl, q + d2 * tl
        side = 1.0 if d1.x * d2.y - d1.y * d2.x > 0 else -1.0
        c = s0 + Vector((-d1.y, d1.x)) * (r * side)
        a0 = math.atan2(s0.y - c.y, s0.x - c.x)
        da = math.atan2(e0.y - c.y, e0.x - c.x) - a0
        while da > math.pi:
            da -= 2 * math.pi
        while da < -math.pi:
            da += 2 * math.pi
        for k in range(n + 1):
            a = a0 + da * k / n
            out.append(c + Vector((math.cos(a), math.sin(a))) * r)
    out.append(pts[-1].copy())
    return out


def clip_corners():
    """Centre line of the steel (y, z) by corners: the upper jaw (the edge and the flat LIP stretch on the
    paper) -> back corner -> back -> corner -> lower jaw."""
    zu = ly.Z_TOP + ly.CST / 2 + 0.00005
    zl = -ly.CST / 2 - 0.00005
    ys = ly.CY_S - ly.CST / 2
    return [Vector((ly.CY_J, zu)), Vector((ly.CY_J + ly.LIP, zu)),
            Vector((ys, ly.CZ_C + ly.CHS / 2 - ly.CST / 2)), Vector((ys, ly.CZ_C - ly.CHS / 2 + ly.CST / 2)),
            Vector((ly.CY_J + ly.LIP, zl)), Vector((ly.CY_J, zl))]


def clip_profile(lod=0):
    """Body profile: the jaw bends (R_LIP) and the back corners (R_SPINE) are arcs; in the middle LOD the
    jaws have no bend and the back corners are two segments."""
    spec = ({1: (ly.R_LIP, 2), 2: (ly.R_SPINE, 4), 3: (ly.R_SPINE, 4), 4: (ly.R_LIP, 2)} if lod == 0
            else {2: (ly.R_SPINE, 2), 3: (ly.R_SPINE, 2)})
    return fillet(clip_corners(), spec)


def build_clip(spec):
    lod = spec["lod"]
    prof = clip_profile(lod)
    cen = Vector((ly.CY_S - ly.CD / 3, ly.CZ_C))
    segn = []
    for a, b in zip(prof, prof[1:]):
        t = (b - a).normalized()
        nrm = Vector((t.y, -t.x))
        if nrm.dot((a + b) / 2 - cen) < 0:
            nrm = -nrm
        segn.append(nrm)
    vn = []
    for i in range(len(prof)):
        if i == 0:
            vn.append(segn[0])
        elif i == len(prof) - 1:
            vn.append(segn[-1])
        else:
            m = (segn[i - 1] + segn[i]).normalized()
            vn.append(m / max(0.3, m.dot(segn[i])))
    h = ly.CST / 2
    body = P("clip", "clip")
    bm = body.bm
    x0, x1 = -ly.CW / 2, ly.CW / 2
    # profile is (y, z): q.x is y, q.y is z; O is the outer surface of the steel, I the inner one
    O = {x: [bm.verts.new((x, q.x + n.x * h, q.y + n.y * h)) for q, n in zip(prof, vn)] for x in (x0, x1)}
    I = {x: [bm.verts.new((x, q.x - n.x * h, q.y - n.y * h)) for q, n in zip(prof, vn)] for x in (x0, x1)}
    for k in range(len(prof) - 1):
        nrm = Vector((0.0, segn[k].x, segn[k].y))
        face(body, [O[x0][k], O[x0][k + 1], O[x1][k + 1], O[x1][k]], "clip", nrm)
        face(body, [I[x0][k], I[x0][k + 1], I[x1][k + 1], I[x1][k]], "clip_in", -nrm)
        for x, sx in ((x0, -1), (x1, 1)):
            face(body, [O[x][k], O[x][k + 1], I[x][k + 1], I[x][k]], "clip", (sx, 0, 0))
    for k, want in ((0, (0, -1, 0)), (len(prof) - 1, (0, -1, 0))):   # jaw ends
        face(body, [O[x0][k], O[x1][k], I[x1][k], I[x0][k]], "clip", want)
    parts = [body]
    # jaw curls at the ends: the bent ends of the handles sit in them; 10 sides are 36 degrees and get
    # smoothed (rolled steel, not a nut); in the middle LOD a single one across the full width
    tabs = P("tabs", "clip")
    for zc in tab_centers():
        if lod == 1:
            g.cyl(tabs.use("clip"), Vector((0.0, YH, zc)), "x", ly.TAB_R, ly.CW, 5)
            continue
        for xs in ((x0 + ly.TAB_L / 2), (x1 - ly.TAB_L / 2)):
            g.cyl(tabs.use("clip"), Vector((xs, YH, zc)), "x", ly.TAB_R, ly.TAB_L, 10)
    parts.append(tabs)
    return parts


def tab_centers():
    return (ly.Z_TOP + ly.CST + 0.85 * ly.TAB_R, -ly.CST - 0.85 * ly.TAB_R)


YH = ly.CY_J - 0.4 * ly.TAB_R        # axis of the curls and handles along y


# --- DayZ pen under the upper clip handle (proxy) -------------------------------------------------
def pen_place():
    """DayZ pen (\\dz\\gear\\tools\\Pen) across the top sheet, under the loop of the upper clip handle, before
    the stack is tilted. Item axes (kvanilla): +Y runs along the pen, the body is around the axis
    x = z = 0 (the x extent is symmetric, +-3.5 mm; the clip sticks out to 12.5 mm towards -z). It lies on
    its side: the item's +Y runs along Blender X (rotated by PEN_ROT), the item's +Z points to the clip,
    the pen clip towards the viewer, the body rests on the paper. Returns the proxy origin, up, fwd, the
    axis (point, direction) and the body radius."""
    lo, hi = kv.box("pen")
    rad = max(-lo[0], hi[0])
    psi = math.radians(ly.PEN_ROT)
    up = Vector((math.cos(psi), math.sin(psi), 0.0))
    fwd = Vector((-math.sin(psi), math.cos(psi), 0.0))
    top = ly.SHEETS[-1]
    y_ax = YH - ly.PEN_B
    u, v = sheet_uv(top, ly.PEN_X, y_ax)
    z_paper = top["z"] + ly.top_lift(u, v) + ly.TH / 2
    yc = (lo[1] + hi[1]) / 2                               # middle of the extent along the pen: above PEN_X
    c = Vector((ly.PEN_X, y_ax, z_paper + rad))
    o = c - up * yc
    return dict(o=o, up=up, fwd=fwd, axis=(c, up), rad=rad, z_paper=z_paper)


PEN = pen_place()


def handle_up_angle(path):
    """Lift of the upper clip handle (rad): the handle plane passes through the axis of the curls and
    touches the body of the DayZ pen (radius + wire) where the loop crosses it, on both sides of the loop
    (the DayZ pen is rotated, so the larger angle is taken). Returns (angle, distance of the contact from
    the axis, m)."""
    zu = tab_centers()[0]
    (c, ax), rad = PEN["axis"], PEN["rad"] + ly.WIRE_R + 0.0001
    best, bc = -1.0, 0.0
    # where the loop passes over the DayZ pen: path points at b ~ PEN_B
    near = [a for a, b in path if abs(b - ly.PEN_B) < 0.004] or [-0.0078, 0.0078]
    for xa in (min(near), max(near)):
        y_ax = c.y + (xa - c.x) * ax.y / ax.x
        dy, dz = YH - y_ax, c.z - zu
        dd = math.hypot(dy, dz)
        beta = math.atan2(dz, dy) + math.asin(min(1.0, rad / dd))
        if beta > best:
            best, bc = beta, math.sqrt(max(0.0, dd * dd - rad * rad))
    return best, bc


def build_handles(spec):
    lod = spec["lod"]
    path = ly.handle_path(lod)
    # wire section: faceted for any count below 10 (the kit smooths up to 40 degrees), so the triangles go
    # into the smoothness of the curve (loop points every ~15 degrees), not into the section facets
    sides = 5 if lod == 0 else 4
    zu, zl = tab_centers()
    parts = []
    # upper: thrown back onto the sheets, the loop rests on the DayZ pen (the contact is computed from its
    # extent)
    beta, bc = handle_up_angle(ly.handle_path(0))
    if lod == 0:
        print("handle up: %.1f deg over the DayZ pen, contact %.1f mm from the axis, %d path points"
              % (math.degrees(beta), bc * 1000, len(path)))
    o = Vector((0.0, YH, zu))
    bdir = Vector((0.0, -math.cos(beta), math.sin(beta)))
    hu = P("handle_up", "wire")
    g.pipe(hu, [o + Vector((a, 0, 0)) + bdir * b for a, b in path], ly.WIRE_R, sides)
    parts.append(hu)
    # lower: outwards, along the lower cheek (from the jaw to the back and beyond)
    cs = clip_corners()
    d = (cs[3] - cs[4]).normalized()
    o = Vector((0.0, YH, zl))
    bdir = Vector((0.0, d.x, d.y))
    hl = P("handle_dn", "wire")
    g.pipe(hl, [o + Vector((a, 0, 0)) + bdir * b for a, b in path], ly.WIRE_R, sides)
    parts.append(hl)
    return parts


# --- tilt: the dropped stack rests on the far edge of the board and on the lower handle -----------
def tilt(parts):
    y_piv = -ly.BH / 2
    if "a" not in TILT:
        best = 0.0
        for p in parts:
            for v in p.bm.verts:
                dy = v.co.y - y_piv
                if dy > 1e-4 and v.co.z < 0:
                    best = max(best, math.atan2(-v.co.z, dy))
        TILT["a"] = best
        print("tilt %.2f deg" % math.degrees(best))
    for p in parts:
        for v in p.bm.verts:
            v.co = tilt_pt(v.co)
        p.bm.normal_update()


def tilt_pt(q, vec=False):
    """A point (or a vector with vec) into the tilted stack: a rotation about the bottom edge of the board."""
    a = TILT["a"]
    ca, sa = math.cos(a), math.sin(a)
    y0 = 0.0 if vec else -ly.BH / 2
    dy, z = q[1] - y0, q[2]
    return Vector((q[0], y0 + dy * ca - z * sa, dy * sa + z * ca))


def build_lod(spec):
    parts = build_board(spec) + build_sheets(spec) + build_clip(spec) + build_handles(spec)
    g.triangulate(parts)
    tilt(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        BOUNDS["pts"] = hull_points(parts)
        print("lowest z %.5f" % BOUNDS["lo"][2])
        # the DayZ pen is a proxy in the near and middle LODs, already in the tilted stack
        M.decor = ((kv.path("pen"), tuple(tilt_pt(PEN["o"])), tuple(tilt_pt(PEN["up"], True)),
                    tuple(tilt_pt(PEN["fwd"], True)), (0, 1), "pen"),)
    return parts


def hull_points(parts):
    """Collision hull points: for the board and the sheets only the outline corners (by `pp`), since the
    other cut points lie on straight edges and give degenerate hull faces; the clip and handles in full."""
    sheets = {"sheet_" + s["name"]: s for s in ly.SHEETS}
    pts = []
    for p in parts:
        lay = p.bm.verts.layers.float_vector.get("pp")
        if p.name == "board":
            keep = {(round(u, 6), round(v, 6)) for u, v in ly.board_outline()}
            pts += [tuple(v.co) for v in p.bm.verts if (round(v[lay][0], 6), round(v[lay][1], 6)) in keep]
        elif p.name in sheets:
            s = sheets[p.name]
            hw, hh = ly.SW / 2, ly.SH / 2
            keep = {(round(u, 6), round(v, 6)) for u, v in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh),
                                                            ly.DOG_F1, ly.DOG_F2)}
            for v in p.bm.verts:
                u = v[lay][0] - ly.SLOT_W * s["slot"]
                if (round(u, 6), round(v[lay][1], 6)) in keep or (s.get("ragged") and abs(abs(v[lay][1]) - hh) < 1e-6):
                    pts.append(tuple(v.co))
        else:
            pts += [tuple(v.co) for v in p.bm.verts]
    return pts


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


INV_VIEW = (0.0, -0.39, 0.34)


def collision():
    """One convex hull over the vertices of the near LOD. The mass is the class weight, 0.3 kg
    (OZL_Carrier_Base); the hit sound and penetration are thin fabric, as for the vanilla book and paper
    (Book_kniga.p3d, Paper.p3d: fabric_thin). The DayZ pen is a proxy with no collision of its own; it
    lies inside the hull (under the clip handle)."""
    comps = [(BOUNDS["pts"], kx.PEN + r"\fabric_thin.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    c = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, hi[2] / 2)
    memory = {
        # inventory preview camera: from the front and above - the sheet with the price list, the clip at
        # the top
        "invView": [INV_VIEW],
        "ce_center": [c],
        "ce_radius": [(c[0] + 0.5 * math.dist(lo, hi), c[1], c[2])],
    }
    print("bbox %.4f..%.4f x %.4f..%.4f x 0..%.4f, preview aspect from invView %.2f (2x2 cell: ~1)"
          % (lo[0], hi[0], lo[1], hi[1], hi[2], preview_aspect(bbox, INV_VIEW)))
    return comps, 0.3, memory, bbox


# the first five are the --look preview (M.look_shots): general view, the clip with the DayZ pen close
# up, the clip from behind (back, lower handle), the folded corner, the inventory view; the rest only
# in --geo
SHOTS = [
    ("front", (-0.22, -0.40, 0.30), (0.0, 0.01, 0.006), 45),
    ("clip", (0.045, 0.012, 0.125), (0.0, 0.090, 0.018), 50),
    ("back", (0.11, 0.25, 0.11), (0.0, 0.105, 0.010), 50),
    ("dogear", (0.19, -0.21, 0.09), (0.055, -0.088, 0.006), 50),
    ("inv", INV_VIEW, (0.0, 0.015, 0.006), 36),
    ("top", (0.0, 0.015, 0.62), (0.0, 0.015, 0.0), 40),
    ("side", (-0.36, 0.06, 0.05), (0.0, 0.03, 0.008), 60),
]

if __name__ == "__main__":
    M.look_shots = (5, 2)
    M.run(build_lod, collision, SHOTS, row_step=0.26, row_shot=((0.13, -0.70, 0.55), (0.13, 0.02, 0.0)))
