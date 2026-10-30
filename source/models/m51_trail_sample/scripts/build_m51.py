"""M51 - Trail record (OZL_Sample_07): a sample of the Trails line shared by all factions - a map
carelessly drawn by hand on a folded squared exercise-book sheet. A portable 1x2 item.

    blender --background --python build_m51.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py with the system Python first (the sheet drawing and the fold relief).

Target: a sheet from an exercise book folded several times, with a map drawn on it by hand in pencil and
pen - paths, crosses, anomaly circles, arrows; folded about 10 x 15 x 1 cm, the sheet slightly open
(part of the drawing shows); the paper is crumpled and stained, the edges fray; pencil and blue pen
lines, red circles, no captions; a flat sheet bent at the folds, 200-400 triangles, texture 512, 60-300
g.

Prototype and sizes:
- sheet: a double sheet from the middle of a school exercise book (removed whole, by the staples): GOST
  12063-89 school exercise books - 170 x 205 mm (tolerance +-2), 12/18/24 sheets; the double sheet is
  340 x 205 mm. Grid 5 mm, margins 20 mm (4 cells) with a red line at the outer edge, the grid stops 1
  cell short of the spine and 2 short of the top and bottom (the GOST exercise-book template). Two
  staples, at the quarters of the height.
- folded in four: along the spine (fold 1) with the map outside - so that it is seen without unfolding -
  and across in half (fold 2): a 170 x 102.5 mm packet. A4 folded in four would be ~10 x 15, an
  exercise-book sheet folded in four is 10.25 x 17 cm. One more fold (through the middles of the pages -
  the sheet was carried folded in eight) has been flattened and remains as a crease across the packet.
- the sheet is slightly open: the upper flap springs open on fold 2 (4 degrees at the fold, 11 at the
  edge, the free edge ~13 mm above the lower one) and its corner is dog-eared; the packet is ~1.9 cm
  thick with the opening.
- drawing (make_decals.py): pencil - road, dirt road, railway, river, forest, swamp, heights, lake,
  houses; blue pen - a trail with crosses 1-7, arrows and distance digits, start and end, a north arrow
  without a letter, a crossed-out dead end; red - anomaly circles and a dashed field with a trefoil. No
  captions, only digits.
- mass: a real double sheet is ~5 g; the class keeps the shared sample mass (60 g, OZL_Sample_Base).

State 'used but intact': yellowed paper, the outer page is dirtier, worn folds, rubbed fold crossings, a
mug ring, water stains, a dirty fingerprint, rusty staple punctures, uneven frayed edges. No faction
colour (the sample is shared). No lamps, screens or moving parts, so no work view. LODs (small item):
near and mid (flap grid half as dense, no sheet edges), no far LOD.

Design decisions: the shape is that of a real folded sheet, not randomly shifted vertices of a sparse
grid, and the paper has no angularity.
- the sheet remembers the old fold 3 (x = 0): both flaps stand as a shallow roof, the fold line ARCH
  above the ends - the packet rests on the spine and the open edge, with a shadow under the middle;
- the crumple is shallow waves (length 5-11 cm, up to ~1 mm) fading towards fold 2: the flaps do not
  touch each other (the 'gap' line in the log is the narrowest gap);
- the corners of the lower flap at the free edge are raised, the free edge of the upper one is curled
  up;
- the dog-eared corner is a real fold: the triangle at the free corner of the upper flap (legs ~21 and
  ~26 mm) is folded onto the face by DOG_PHI and springs back by 24 degrees; the axis runs along the
  face, so the corner does not enter the sheet; from above the back of the sheet (grid, red field)
  shows, the map of the corner is below, on the sheet. The fold line follows the grid diagonals, the
  fold is sharp, the mid LOD has the same triangle;
- fold 2 on the outside is a rounding of 5 faces (2 gave kinks), the ends of the rounding are closed;
- the edges fray smoothly: smooth noise along the edge length, not per vertex number (the LODs match);
- the flap grid is 16 x 8, the mid LOD 8 x 4; --stats also prints an unwrap check (uv_check: faces of
  one atlas rectangle do not overlap).
Material: the sheet image by the attribute `paper`, with old-paper layers on top in sheet coordinates
(across the folds, without a seam): yellowed all over and in patches, small rusty ageing dots, grey
graphite and finger smears, more visible relief creases, fibres; the outer pages are also handled - dirt
at the spine and at fold 2, less at the open and free edges and along fold 3, light dust on top; the
inner ones (in the fold) are cleaner. The edges are a paper cut with dirt. Atlas 1024: the thin pencil
lines are crisper in game (small item: 512-1024). No vanilla proxies on the sheet: it is a sample item,
and a pen or compass on it would be taken by the player as theirs. No work view: it is not a station.

Mesh layout: each flap is two surfaces (facing outwards and into the packet) 0.6 mm apart with edges
between them; the inner surfaces of the flaps meet at fold 2 with shared vertices, the outer ones go
round the fold. Every surface vertex has the attribute `paper`: the (s, t) coordinates of this point on
the unfolded sheet (m51_layout). The paper material takes the make_decals.py image by them, so the
drawing passes across the folds as on a real sheet and is not mirrored.

Blender axes: X is the packet length (fold 1 is at -X), Y is the width (fold 2 at the back, +Y; the free
edge at -Y, towards the front), Z is up. The origin is the centre under the packet: autocenter = 0 (in
Geometry), boundingbox_min at the bottom, so a dropped sheet lies flat. The inventory camera (invView)
is at the -X end, high and steep: the long axis stands up in the 1x2 cell.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import m51_layout as ly  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m ---------------------------------------------------------------------------
HX, HY, W = ly.HX, ly.HY, ly.W
TH = 0.0006                    # a flap is two paper layers (looks thicker so that it does not flicker)
THETA0, THETA1 = 4.0, 11.0     # lift of the upper flap at the fold and at the free edge, degrees
ARCH = 0.0030                  # old fold 3 (x = 0): the packet is a shallow roof, the fold above the ends
LIP = 0.0009                   # free edge of the upper flap curled up
CURL_B = 0.0016                # corners of the lower flap at the free edge are raised
FADE = 0.040                   # the crumple fades out towards fold 2 over this length
FRAY = 0.0006                  # frayed edges - unevenness inwards
CORNER = 0.0016                # worn corners
DOG_PHI = 156.0                # dog-ear folded onto the face, springs back 24 degrees off the sheet
MAP_C = (ly.SHEET_W / 2, ly.SHEET_H / 2)
MAP_S = (ly.SHEET_W, ly.SHEET_H)
# shallow crumple waves: (amplitude, wavelength, direction, phase)
WAVES_A = ((0.00042, 0.071, 0.40, 0.3), (0.00030, 0.104, -1.15, 2.1), (0.00022, 0.052, 0.95, 4.0))
WAVES_B = ((0.00036, 0.083, -0.55, 1.2), (0.00026, 0.061, 1.25, 5.1), (0.00018, 0.113, 0.15, 3.3))

# na - along X (even, a multiple of 8: fold 3 and the fold of the dog-ear lie on grid lines), nb = na /
# 2
LOD_SPECS = [
    dict(lod=0, na=16, nb=8, edges=True, wrap=5),
    dict(lod=1, na=8, nb=4, edges=False, wrap=2),
]

# density scale: the outer top is what shows most; the inner ones are for the gap; the bottom is not
# visible when it lies (for -z faces the unwrap itself cuts the density fourfold, hence 2.6 and 1.6)
REGIONS = {
    "paper_a": ("paper_out", 1.0), "paper_b": ("paper_inside", 0.65), "paper_in": ("paper_inside", 2.6),
    "paper_bot": ("paper_out", 1.6), "fold_out": ("paper_out", 1.0),
    # dog-eared corner: the back (left page) faces up, the face with the map faces down, onto the sheet
    "dog_in": ("paper_inside", 1.0), "dog_out": ("paper_out", 0.5),
    "edge_a": ("paper_edge", 0.3), "edge_b": ("paper_edge", 0.3),
}

GRIME = kmats.lin((112, 98, 74))        # dirt - the same colour as in make_decals.py
FOX = kmats.lin((146, 104, 60))         # rusty ageing dots on the paper
OLD = (0.94, 0.82, 0.60, 1.0)           # yellowed paper (multiply, linear colour)
SMEAR = (0.80, 0.77, 0.71, 1.0)         # grey graphite and finger smears (multiply)


# --- materials -------------------------------------------------------------------------------
def mul(t, fac, col, tint):
    """Colour multiplied by tint with fraction fac (Mix: Multiply)."""
    m = t.node("ShaderNodeMix")
    m.data_type = "RGBA"
    m.blend_type = "MULTIPLY"
    if isinstance(fac, (int, float)):
        m.inputs["Factor"].default_value = fac
    else:
        t.link(fac, m.inputs["Factor"])
    t.link(col, m.inputs[6])
    m.inputs[7].default_value = tint
    return m.outputs[2]


def shift(t, vec, off):
    v = t.node("ShaderNodeVectorMath")
    v.inputs[1].default_value = off
    t.link(vec, v.inputs[0])
    return v.outputs[0]


def patina(t, col):
    """'dayz' profile (kmats.LOOKS): the colour is desaturated and muted, as in kmats.dayz_layers."""
    d, v = kmats.LOOK["patina"]
    gray = t.node("ShaderNodeRGBToBW")
    t.link(col, gray.inputs[0])
    col = t.mixc(d, col, gray.outputs[0])
    return t.mixc(1.0 - v, col, (0, 0, 0, 1))


def paper_wear(t, origin, col, gl, h, pv, outside):
    """Old paper over the sheet image ('dayz' look). The pattern is in sheet coordinates pv: folds do
    not cut it. outside - the outer pages of the packet: they were held in hands.
    """
    col = patina(t, col)
    # the paper yellowed all over and in patches (~10 cm): old paper turns warm, not grey
    tone = t.maprange(t.noise(pv, 7.0, 4.0, 0.55), 0.35, 0.72, 0.0, 1.0)
    base, spot = (0.32, 0.40) if outside else (0.22, 0.26)
    col = mul(t, t.math("ADD", base, t.math("MULTIPLY", tone, spot)), col, OLD)
    # small rusty ageing dots - in clusters
    sp = t.step(t.noise(shift(t, pv, (3.1, 1.7, 0.0)), 150.0, 3.0, 0.5), 0.67, 0.72)
    cl = t.maprange(t.noise(shift(t, pv, (7.3, 2.9, 0.0)), 6.0, 2.0, 0.5), 0.42, 0.62, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", sp, cl), 0.50), col, FOX)
    # grey graphite and finger smears (~3-5 cm)
    sm = t.step(t.noise(shift(t, pv, (5.5, 8.1, 0.0)), 20.0, 4.0, 0.6), 0.60, 0.72)
    col = mul(t, t.math("MULTIPLY", sm, 0.38 if outside else 0.14), col, SMEAR)
    if outside:
        # handled: the folded edges of the packet (spine -X, fold 2 +Y) rub in a pocket - dirty; less so
        # the open and free edges (they are held) and the line of the old fold 3 (x = 0)
        tc = t.node("ShaderNodeTexCoord")
        tc.object = origin
        osep = t.node("ShaderNodeSeparateXYZ")
        t.link(tc.outputs["Object"], osep.inputs[0])
        ox, oy = osep.outputs["X"], osep.outputs["Y"]
        e = t.math("MAXIMUM", t.maprange(t.math("ADD", ox, HX), 0.0, 0.011, 1.0, 0.0),
                   t.maprange(t.math("SUBTRACT", HY, oy), 0.0, 0.010, 1.0, 0.0))
        e2 = t.math("MAXIMUM", t.maprange(t.math("SUBTRACT", HX, ox), 0.0, 0.007, 0.45, 0.0),
                    t.maprange(t.math("ADD", oy, HY), 0.0, 0.007, 0.45, 0.0))
        e2 = t.math("MAXIMUM", e2, t.maprange(t.math("ABSOLUTE", ox), 0.0, 0.0035, 0.40, 0.0))
        e = t.math("MAXIMUM", e, e2)
        e = t.math("MULTIPLY", e, t.maprange(t.noise(tc.outputs["Object"], 70.0, 6.0, 0.6), 0.35, 0.70, 0.25, 1.0))
        col = t.mixc(t.math("MULTIPLY", e, 0.65), col, GRIME)
        # light dust on what faces up
        nsep = t.normal()
        up = t.maprange(nsep.outputs["Z"], 0.5, 0.95, 0.0, 1.0)
        dn = t.maprange(t.noise(tc.outputs["Object"], 25.0, 5.0, 0.6), 0.40, 0.70, 0.0, 1.0)
        col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", up, dn), 0.10), col, kmats.DUST)
        gl = t.math("SUBTRACT", gl, t.math("MULTIPLY", e, 0.02))
    # creases of crumpled paper (make_decals.py relief) - more visible; fibres - fine relief
    h = t.math("MULTIPLY", h, 1.4)
    fib = t.noise(pv, 1500.0, 2.0, 0.5)
    h = t.math("ADD", h, t.math("MULTIPLY", t.math("SUBTRACT", fib, 0.5), 0.05))
    return col, gl, h


def build_paper(mat, origin, img, himg, outside=True, gloss=0.05, spec=0.035):
    """Paper with a drawing: the sheet image by the attribute `paper` (coordinates on the unfolded
    sheet), the fold and crease relief - a second image by the same coordinates; in the 'dayz' look old
    paper on top (paper_wear).
    """
    t = kmats.Tree(mat)
    attr = t.node("ShaderNodeAttribute")
    attr.attribute_type = "GEOMETRY"
    attr.attribute_name = "paper"
    pv = attr.outputs["Vector"]
    sep = t.node("ShaderNodeSeparateXYZ")
    t.link(pv, sep.inputs[0])
    s, tt = sep.outputs["X"], sep.outputs["Y"]
    col, _ = t.image(img, s, tt, MAP_C, MAP_S)
    hcol, _ = t.image(himg, s, tt, MAP_C, MAP_S)
    # pencil and ballpoint shine slightly: darker - a bit glossier
    dark = t.math("SUBTRACT", 1.0, t.bw(col))
    gl = t.math("ADD", gloss, t.math("MULTIPLY", t.maprange(dark, 0.75, 0.95, 0.0, 1.0), 0.08))
    h = t.bw(hcol)
    if kmats.LOOK["name"] == "dayz":
        col, gl, h = paper_wear(t, origin, col, gl, h, pv, outside)
    return kmats.out(t, col, gl, spec, h)


def build_paper_edge(mat, origin, color, seed=7.3, gloss=0.04, spec=0.03):
    """Paper cut: fibres, dirt in patches."""
    t = kmats.Tree(mat)
    vec, _ = t.coords(origin, seed)
    fib = t.maprange(t.noise(vec, 900.0, 3.0, 0.6), 0.3, 0.7, 0.0, 1.0)
    col = t.mixc(fib, tuple(c * 0.86 for c in color[:3]) + (1,), color)
    col = t.mixc(t.maprange(t.noise(vec, 60.0, 6.0, 0.6), 0.3, 0.7, 0.15, 0.6), col, GRIME)
    if kmats.LOOK["name"] == "dayz":
        col = patina(t, col)
    return kmats.out(t, col, gloss, spec, 0.0)


KINDS = kmats.std_kinds(floor_z=0.0)
PNG = dict(img=os.path.join(WORK, "paper_map.png"), himg=os.path.join(WORK, "paper_height.png"))
KINDS.update({
    "paper_out": (build_paper, dict(PNG, outside=True)),
    "paper_inside": (build_paper, dict(PNG, outside=False)),
    "paper_edge": (build_paper_edge, dict(color=kmats.lin((196, 188, 164)))),
})

OBJ, NAME = "m51_trail_sample", "ozr_trail_sample"
# rvmat as for vanilla paper (Paper.p3d): specular 0.1 / power 20, more matte than the 'dayz' profile
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 rvmat=dict(specular=0.1, power=20.0))
M.look_shots = (4, 2)
P = M.part
BOUNDS = {}


# --- sheet shape -----------------------------------------------------------------------------
def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3.0 - 2.0 * x)


def wave(ws, a, b):
    return sum(amp * math.sin(2 * math.pi * (a * math.cos(d) + b * math.sin(d)) / lam + ph) for amp, lam, d, ph in ws)


def _lat(seed, k):
    return random.Random(seed * 1000003 + k).uniform(-1.0, 1.0)


def vnoise(x, seed, cell):
    """Smooth noise -1..1 over a coordinate (not a vertex number): the edge is the same at near and mid
    LOD.
    """
    u = x / cell
    k = math.floor(u)
    f = smooth(u - k)
    return _lat(seed, k) * (1.0 - f) + _lat(seed, k + 1) * f


def arch(a):
    """Old fold 3 across the packet: a shallow roof."""
    return ARCH * (1.0 - abs(a) / HX)


def theta(b):
    return math.radians(THETA0 + (THETA1 - THETA0) * b / W)


def leaf_a_base(b):
    """Centre line of the upper flap (y, z) at distance b from the fold and its outward normal."""
    k = math.radians(THETA1 - THETA0) / W
    t0, tb = math.radians(THETA0), theta(b)
    y = HY - (math.sin(tb) - math.sin(t0)) / k
    z = TH + (math.cos(t0) - math.cos(tb)) / k
    return y, z, (math.sin(tb), math.cos(tb))


def pos_b(a, b):
    """Bottom of the lower flap: it lies, the crumple goes only up, the corners at the free edge are
    raised.
    """
    und = max(0.0, wave(WAVES_B, a, b)) * smooth(b / FADE)
    curl = CURL_B * smooth((b - (W - 0.035)) / 0.035) * (0.35 + 0.65 * (a / HX) ** 2)
    return Vector((a, HY - b, arch(a) + und + curl))


def pos_a(a, b):
    """Back of the upper flap and its outward normal: an arc from fold 2, the crumple and the curled
    edge go along the normal.
    """
    y, z, (ny, nz) = leaf_a_base(b)
    d = wave(WAVES_A, a, b) * smooth(b / FADE) + LIP * smooth((b - (W - 0.025)) / 0.025)
    return Vector((a, y + ny * d, z + nz * d + arch(a))), Vector((0.0, ny, nz))


def rotate(p, c, u, ang):
    return c + Matrix.Rotation(ang, 3, u) @ (p - c)


def outline(na, nb, seed):
    """Flap grid (a, b): the open edge (+X) and the free one (b = W) fray inwards, the corners at the
    free edge are worn; fold 1 (-X) and fold 2 (b = 0) are straight - they are folds.
    """
    grid = []
    for i in range(na + 1):
        col = []
        for j in range(nb + 1):
            a, b = -HX + 2 * HX * i / na, W * j / nb
            if i == na:
                a = HX - FRAY * (0.5 if j == 0 else 0.55 + 0.45 * vnoise(b, seed, 0.007))
            if j == nb:
                b = W - FRAY * (0.55 + 0.45 * vnoise(a, seed + 1, 0.007))
            col.append([a, b])
        grid.append(col)
    for i, s in ((0, 1.0), (na, -1.0)):
        grid[i][nb][0] += s * CORNER * 0.6
        grid[i][nb][1] -= CORNER * 0.8
    return grid


def paper_st(side, a, b):
    """Coordinates of a point on the unfolded sheet (m51_layout): side is 'b_top', 'b_bot', 'a_in',
    'a_out'.
    """
    left, right = ly.SPINE / 2 - a, 1.5 * ly.SPINE + a
    return {"b_top": (left, ly.FOLD2 + b), "b_bot": (right, ly.FOLD2 + b),
            "a_in": (left, ly.FOLD2 - b), "a_out": (right, ly.FOLD2 - b)}[side]


def build_sheet(spec):
    na, nb, nw = spec["na"], spec["nb"], spec["wrap"]
    k = na // 8                                   # dog-ear: k cells along each edge
    p = P("sheet", "paper_a")
    bm = p.bm
    lay = bm.verts.layers.float_vector.new("paper")
    idx = {r: p.region_index(r, *REGIONS[r]) for r in REGIONS}
    ga, gb = outline(na, nb, 5101), outline(na, nb, 5102)
    # the fold line of the dog-ear is straight: the middle points lie on it
    p1, p2 = ga[na - k][nb], ga[na][nb - k]
    for m in range(1, k):
        ga[na - k + m][nb - m] = [p1[0] + (p2[0] - p1[0]) * m / k, p1[1] + (p2[1] - p1[1]) * m / k]

    def vert(co, side, a, b):
        v = bm.verts.new(co)
        s, t = paper_st(side, a, b)
        v[lay] = (s, t, 0.0)
        return v

    # fold 2 from the inside is one line shared by both flaps
    fold = [vert(Vector((gb[i][0][0], HY, arch(gb[i][0][0]) + TH)), "b_top", gb[i][0][0], 0.0) for i in range(na + 1)]
    # lower flap B lies: the bottom is on the ground, the top is TH higher
    b_bot, b_top = [], []
    for i in range(na + 1):
        cb_, ct_ = [], [fold[i]]
        for j in range(nb + 1):
            a, b = gb[i][j]
            q = pos_b(a, b)
            cb_.append(vert(q, "b_bot", a, b))
            if j > 0:
                ct_.append(vert(q + Vector((0.0, 0.0, TH)), "b_top", a, b))
        b_bot.append(cb_)
        b_top.append(ct_)
    # upper flap A: the back and the face; the dog-ear is a rotation about the fold line
    pin, pout, nrm = {}, {}, {}
    for i in range(na + 1):
        for j in range(nb + 1):
            a, b = ga[i][j] if j > 0 else gb[i][0]
            q, n = pos_a(a, b)
            pin[i, j], pout[i, j], nrm[i, j] = q, q + n * TH, n
    # the fold axis is on the face (the outer surface): the folded corner lies on the face without
    # entering the sheet
    crease = na + nb - k                          # sum of the indices of the points on the fold line
    c1, c2 = pout[na - k, nb], pout[na, nb - k]
    u = (c2 - c1).normalized()
    ang = math.radians(DOG_PHI)
    if (rotate(pout[na, nb], c1, u, ang) - c1).dot(nrm[na, nb]) < 0:
        ang = -ang
    rot = Matrix.Rotation(ang, 3, u)
    for i, j in list(pin):
        if i + j > crease:
            pin[i, j] = rotate(pin[i, j], c1, u, ang)
            pout[i, j] = rotate(pout[i, j], c1, u, ang)
    a_in, a_out = [], []
    for i in range(na + 1):
        ci, co = [fold[i]], []
        for j in range(nb + 1):
            a, b = ga[i][j] if j > 0 else gb[i][0]
            if j > 0:
                ci.append(vert(pin[i, j], "a_in", a, b))
            co.append(vert(pout[i, j], "a_out", a, b))
        a_in.append(ci)
        a_out.append(co)
    if spec["lod"] == 0:
        gap = min(pin[i, j].z - b_top[i][j].co.z for i in range(na + 1) for j in range(1, nb + 1) if i + j <= crease)
        print("gap A-B: min %.2f mm; top %.1f mm" % (gap * 1000, max(v.co.z for v in bm.verts) * 1000))

    def face(vs, region, want):
        f = bm.faces.new(vs)
        f.normal_update()
        if f.normal.dot(Vector(want)) < 0:
            f.normal_flip()
        f[p.reg] = idx[region]
        return f

    def cell(grid, i, j, region, want, dog=None):
        """Surface cell; on the upper flap (dog - the corner region) the cell at the fold line is cut
        along it - the diagonal (i + 1, j) - (i, j + 1), and beyond the line the faces of the corner are
        rotated with it.
        """
        q = [grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]]
        if dog is None or i + j + 2 <= crease:
            face(q, region, want)
        elif i + j + 1 == crease:
            face([q[0], q[1], q[3]], region, want)
            face([q[1], q[2], q[3]], dog, rot @ Vector(want))
        else:
            face(q, dog, rot @ Vector(want))

    for i in range(na):
        for j in range(nb):
            cell(b_top, i, j, "paper_b", (0, 0, 1))
            cell(b_bot, i, j, "paper_bot", (0, 0, -1))
            _, _, (ny, nz) = leaf_a_base(W * (j + 0.5) / nb)
            cell(a_out, i, j, "paper_a", (0, ny, nz), "dog_out")
            cell(a_in, i, j, "paper_in", (0, -ny, -nz), "dog_in")
    if spec["edges"]:
        # edges: fold 1 (-X) and the open edge (+X) along j, the free edge along i; at the dog-ear they
        # are rotated
        _, _, (nyw, nzw) = leaf_a_base(W)
        for top, bot, reg, free_n, is_a in ((b_top, b_bot, "edge_b", (0, -1, 0), False),
                                            (a_out, a_in, "edge_a", (0, -nzw, nyw), True)):
            for j in range(nb):
                for i, want in ((0, (-1, 0, 0)), (na, (1, 0, 0))):
                    w = rot @ Vector(want) if is_a and i + j >= crease else want
                    face([top[i][j], top[i][j + 1], bot[i][j + 1], bot[i][j]], reg, w)
            for i in range(na):
                w = rot @ Vector(free_n) if is_a and i + nb >= crease else free_n
                face([top[i][nb], top[i + 1][nb], bot[i + 1][nb], bot[i][nb]], reg, w)
    # fold 2 from the outside: from the bottom of B round the fold to the face of A (the centre is the
    # fold line from the inside)
    rings = [[b_bot[i][0] for i in range(na + 1)]]
    _, _, (ny0, nz0) = leaf_a_base(0.0)
    end = math.atan2(ny0, nz0)                    # angle of A's normal from +z to +y
    for kk in range(1, nw):
        an = math.pi - (math.pi - end) * kk / nw  # from -z through +y to A's normal
        ring = []
        for i in range(na + 1):
            a = gb[i][0][0]
            ring.append(vert(Vector((a, HY + math.sin(an) * TH, arch(a) + TH + math.cos(an) * TH)), "b_bot", a, 0.0))
        rings.append(ring)
    rings.append([a_out[i][0] for i in range(na + 1)])
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(na):
            vs = [r0[i], r0[i + 1], r1[i + 1], r1[i]]
            c = sum((v.co for v in vs), Vector()) / 4
            cz = TH + (arch(gb[i][0][0]) + arch(gb[i + 1][0][0])) / 2
            face(vs, "fold_out", (0, c.y - HY, c.z - cz))
    if spec["edges"]:
        # ends of the rounding (at the spine and at the open edge) - a fan from the fold line
        for i, want in ((0, (-1, 0, 0)), (na, (1, 0, 0))):
            ring = [r[i] for r in rings]
            for kk in range(nw):
                face([fold[i], ring[kk], ring[kk + 1]], "edge_b", want)
    bm.normal_update()
    return [p]


def uv_check(parts, cell=0.0004):
    """Check for the kuv unwrap (printed with --stats): faces of one atlas rectangle (part / region /
    side) must not overlap in its projection, otherwise baking would mix their image (at the folded
    corner and at the rounding of the fold the face sides differ - that is what is checked).
    """
    import kuv
    seen, bad = {}, {}
    for p in parts:
        for f in p.bm.faces:
            key = kuv.face_key(p, f)
            ax, _ = kuv.face_dir(f.normal)
            ia, ib = kuv.PLANE[ax]
            (x0, y0), (x1, y1), (x2, y2) = [(v.co[ia], v.co[ib]) for v in f.verts]
            d = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
            if abs(d) < 1e-12:
                continue
            for gx in range(int(math.floor(min(x0, x1, x2) / cell)), int(math.ceil(max(x0, x1, x2) / cell)) + 1):
                for gy in range(int(math.floor(min(y0, y1, y2) / cell)), int(math.ceil(max(y0, y1, y2) / cell)) + 1):
                    px, py = (gx + 0.5) * cell, (gy + 0.5) * cell
                    w1 = ((x1 - px) * (y2 - py) - (x2 - px) * (y1 - py)) / d
                    w2 = ((x2 - px) * (y0 - py) - (x0 - px) * (y2 - py)) / d
                    if w1 > 1e-6 and w2 > 1e-6 and 1.0 - w1 - w2 > 1e-6:
                        if (key, gx, gy) in seen:
                            bad[key] = bad.get(key, 0) + 1
                        seen[key, gx, gy] = 1
    print("uv check: %d keys, overlap %s" % (len({k for k, _, _ in seen}), bad or "none"))


def build_lod(spec):
    parts = build_sheet(spec)
    g.triangulate(parts)
    if spec["lod"] == 0 and "--stats" in sys.argv:
        uv_check(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        BOUNDS["pts"] = [tuple(v) for v in vs]
    return parts


def collision():
    """One convex hull of the packet over the vertices of the near LOD. The mass is the class weight,
    0.06 kg; the impact and penetration sound is thin cloth, as for vanilla paper (Paper.p3d).
    """
    comps = [(BOUNDS["pts"], kx.PEN + r"\fabric_thin.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    cz = hi[2] / 2
    memory = {
        # inventory preview camera: from the -X end, high and steep (67 degrees) - the long axis stands
        # up in the 1x2 cell, the outer page with the trail is visible
        "invView": [(-0.16, -0.03, 0.38)],
        "ce_center": [(0.0, 0.0, cz)],
        "ce_radius": [(HX + 0.005, 0.0, cz)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.06, memory, bbox


# --look previews - the first four (M.look_shots): overview, top, close-up of the open edge, inventory
SHOTS = [
    ("front", (-0.16, -0.34, 0.20), (0.0, 0.0, 0.008), 45),
    ("top", (0.0, -0.05, 0.42), (0.0, 0.0, 0.006), 40),
    ("open", (0.17, -0.20, 0.085), (0.035, -0.01, 0.009), 40),
    ("inv", (-0.16, -0.03, 0.38), (0.0, 0.0, 0.009), 34),
    ("back", (0.22, 0.30, 0.18), (0.0, 0.0, 0.008), 45),
]

M.run(build_lod, collision, SHOTS, row_step=0.22, row_shot=((0.11, -0.80, 0.34), (0.11, 0, 0.01)))
