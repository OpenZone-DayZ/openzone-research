"""M66 - "Trails" carrier (OZL_Carrier_Trail): the carrier of the "Trails" line, shared by the factions -
a drawing tube with a strap, the end cap removed and hanging on a cord, a rolled tracing paper with
an inked map sticking out of the mouth. A portable 1x3 item.

    blender --background --python build_m66.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (the map on tracing paper, the tag).

Target: a tube with a tracing-paper map, 1x3; a Soviet tube of D ~9 x 63 cm (measured against a tape
measure in a photo), shortened to ~45-50 cm for the 1x3 slots, following a vanilla item of a similar
size; a plastic or cardboard tube (camoGround), the end cap removed and hanging on a cord, a strap;
the tracing paper protrudes by ~8 cm, translucent, the ink lines visible. Carriers: 200-400 g,
300-1000 triangles, texture 512-1024, paper without readable text.

Reference and sizes:
- tube: a Soviet plastic drawing tube with "diamond" knurling (a lot "Tube for drawings, USSR"): by tape
  measure in the photo ~63-65 cm, D ~9 cm; a similar 1980s tube on Yandex Market is 9 x 9 x 63 cm.
  63 cm is an A1 sheet (594 x 841 mm per GOST 2.301-68) rolled along the short side plus ~36 mm for
  the bottom and the cap. For the 1x3 slots (target 45-50 cm) the same tube is used for the A2 format
  (420 x 594, rolled along the 420 side): body 455 mm (420 + the same ends), D 90 mm, wall 2.3 mm.
  Vanilla 1x3 items (a water bottle, a hunting knife, a wrench) are 27-34 cm long; 45 cm is the
  longest item in 1x3, but not longer than a machete in 1x4.
- knurling: diamonds ~24 x 14 mm, thin grooves (from the photo); the body has two knurled clamp bands
  of 26 mm (about 3 cm in the photo, ~13 cm between them, with the handle there) - we use 15 cm
  between the centres; the strap lugs are on them. The closed bottom is a cup D 94.4 mm x 32 mm fitted
  over the body; at the mouth a smooth band of 50 mm, the cap goes onto it - a cup D 95 x 50 mm
  (estimated from the end in the photo).
- strap: a carrying strap of black leatherette 20 x 1.8 mm between the clamp lugs (the tube in the
  photo has a handle on the bands); a long shoulder strap would not fit in 1x3: a loop a metre long
  would spread twice as wide as the tube. The strap has fallen to the side, its middle lies on the
  ground.
- the cap is off and stands bottom down on the ground by the protruding roll, the cord (cotton,
  D 2.5 mm) runs from the lug of the second clamp along the side of the tube and over the ground to the
  hole near the edge of the cap.
- tracing paper: an A2 sheet of tracing paper for ink (GOST 892-89, 40 g/m2, like roll tracing paper
  640/878 mm on sale) 420 x 594 mm, rolled along the 420 side: in the tube the roll has relaxed
  against the wall - D ~80 mm, 2.4 turns, hollow (you can see inside); the roll lies on the bottom of
  the tube, pulled out by 80 mm (target ~8 cm) and slightly unwound outside. The free edge of the outer
  turn is a step on top. On the sheet is the edge of a map inked from a topographic map
  (make_decals.py): a frame with minute checks, kilometre grid numbers outside the frame,
  registration crosses, contour lines, a river, a road with a bridge, a forest, a marsh, a route in
  red ink with points 1-7 and arrows, anomaly zones. The tracing paper is translucent: through the
  outer turn the ink of the next one shows (the same drawing shifted by a turn, pale), inside the roll
  is the back of the sheet.
- tag 70 x 40 mm on the body by the mouth: a red stripe (the colour of the "Trails" line), empty
  fields, a pen number, a violet stamp with a wind rose and no text.
- weight: a real plastic A2 tube with tracing paper is ~300 g - the same as OZL_Carrier_Base (300 g).

Detailing:
- "dayz" look (kmodel look="dayz": matte, dirtier, coloured AO; the rvmat comes from the profile, not
  an own 0.6);
- round parts are round: the body, the roll and the dark gap have 28 faces around, the cap 24 (middle
  LOD: 14 and 12); the outer end of the bottom is rounded by two belts of faces at 30 degrees (so LOD
  smoothing does not break them, the threshold is 40), the mouth has a chamfer on the outer edge, the
  cap has chamfers on the bottom and the rim;
- "diamond" knurling - raised pillow-like diamonds (relief), dark and dusty in places in the grooves,
  the tops of the diamonds and of the clamp ribs rubbed; the cap is knurled with the same diamond; the
  bottom and the cap bottom have a moulded ring and a sprue; scuffs, scratches, dust on top and ground
  dirt below come from the profile layers (weather() is a copy of kmats.weather: in the kit, streaks
  and scratches along world axes on a black 9 cm item broke into light drops);
- lugs are cast brackets on the clamps (two posts and a crossbar), the strap is threaded under the
  crossbar, wraps it, the end lies over the strap and is stitched with a rectangle with a cross;
  stitching along the strap edges; the strap and the cord are smooth curves; near the ground the strap
  twists a quarter turn, like a real one;
- the cord (five sides, a three-strand twist pattern) comes out of the hole in the post of the second
  lug, lies along the ground, climbs the wall at the cap and goes into the hole at the edge, with a
  knot inside the cap;
- roll: the free edge of the outer turn at the end lags slightly (a shadow under it), the inner turns
  slide out by 1.5 mm - the end is stepped with turn lines; inside is a cone into the dark (instead of
  a wall and a dark bottom, 56 triangles fewer); the tracing paper has yellowed towards the end, a
  crease along the axis, a folded corner at the free edge; the tag has a peeled corner;
- triangles 1536 / 510 (the small-item guideline is up to 1.5 k, middle ~40 %).
No vanilla items as proxies: the carrier is itself a loot item that is picked up and carried; a decor
item on or beside it would vanish with it and look like something that can be taken separately. There
is no "work" view: the carrier is not a machine and has no "working" state (no lamps, screens or
moving parts either).

State is `used but intact`: dust in the knurling grooves and on top, scuffs on the edges of the
bottom, the cap and the clamps, scratches on the smooth band from the cap; the tracing paper is
thumbed at the end. No faction colour: the tube is the camoGround selection (body, bottom, lugs, cap),
its texture is set by the config (hiddenSelectionsTextures; a procedural colour
#(argb,8,8,3)color(...) recolours the plastic evenly, the knurling relief stays). LODs (a small
item): near and middle (~40 %), no far one.

Blender axes: X is along the tube (the mouth and the roll at +X), Y is across (the strap, the cord and
the cap at +Y), Z is up. The origin is the middle of the frame on the ground: autocenter = 0 (in
Geometry). The inventory camera (invView) looks from the bottom side, from above and steeply: the
tube fills the height of the 1x3 cell, the roll and the cap at the top.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import bmesh  # noqa: E402
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import m66_layout as L  # noqa: E402
from mathutils import Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

LOD_SPECS = [
    dict(lod=0),
    dict(lod=1),
]

REGIONS = {
    "body": ("plastic_body", 1.0),
    "end": ("plastic_end", 0.8),
    "lip": ("plastic_lip", 0.6),
    "inner": ("plastic_in", 0.4),
    "cap_out": ("cap_out", 0.9),
    "cap_rim": ("cap_rim", 0.6),
    "cap_in": ("cap_in", 0.5),
    "lug": ("lug", 1.0),
    "roll_out": ("paper_out", 2.0),
    "roll_gap": ("paper_gap", 0.3),
    "roll_edge": ("paper_edge", 0.6),
    "roll_in": ("paper_in", 0.7),
    "dark": ("dark", 0.2),
    "label": ("label", 1.6),
    "strap": ("strap", 0.9),
    "cord": ("cord", 0.6),
}

PLASTIC = kmats.lin((34, 34, 36))
TURN = 2 * math.pi * L.ROLL_R          # length of one turn of the tracing paper
GND = L.STRAP_T / 2 + 0.0002           # centre of a strap lying on the ground


def wdecal(name):
    return os.path.join(WORK, name)


def W(u, v, z):
    """Tube point (u, v, z) -> Blender."""
    return (u - L.U0, v - L.V0, z)


def tpt(u, r, th, zc=L.ZC, vc=0.0):
    """A point on radius r around the axis along u (the axis at (vc, zc)), angle th."""
    return W(u, vc + r * math.cos(th), zc + r * math.sin(th))


def on_lug(c, x, y, du=0.0):
    """A point at the clamp lug with middle c: x is along the arc from the lug middle (towards larger theta),
    y is above radius R, du is along the axis (tube coordinates u, v, z)."""
    th = L.LUG_THETA + x / L.R
    r = L.R + y
    return (c + du, r * math.cos(th), L.ZC + r * math.sin(th))


def lug_dirs(x):
    """Outwards from the axis and along the arc (towards larger theta) at lug point x."""
    th = L.LUG_THETA + x / L.R
    return Vector((0.0, math.cos(th), math.sin(th))), Vector((0.0, -math.sin(th), math.cos(th)))


def cap_pt(r, z, d):
    """A point at the cap: at distance r from its axis in direction d (a unit vector (u, v)), height z."""
    cu, cv = L.CAP_C
    return (cu + d.x * r, cv + d.y * r, z)


# where the cord leaves the cap axis (towards the tube, along the ground) and where the holes for it are
CORD_DIR = Vector((0.430 - L.CAP_C[0], 0.052 - L.CAP_C[1])).normalized()
HOLE_CAP = W(*cap_pt(L.CAP_R, L.CAP_H - 0.0078, CORD_DIR))
HOLE_LUG = W(*on_lug(L.CLAMPS[1], 0.0, L.CORD_HOLE_Y, L.LUG_L / 2))


# --- materials ------------------------------------------------------------------------------------
def coords(t, origin, seed, k=20.0):
    """Model coordinates (metres, shifted by seed, for the weather() layers), the same stretched k times (an
    own fine pattern), and separate X, Y, Z."""
    raw, sep = t.coords(origin, seed)
    return raw, t.stretch(raw, k, k, k), sep


def obj_pos(sep):
    return sep.inputs[0].links[0].from_socket


def dist_to(t, sep, pt):
    d = t.node("ShaderNodeVectorMath")
    d.operation = "DISTANCE"
    t.link(obj_pos(sep), d.inputs[0])
    d.inputs[1].default_value = pt
    return d.outputs["Value"]


def cyl_coords(t, sep):
    """Tube coordinates from model coordinates: u along the axis, angle theta around the circumference."""
    u = t.math("ADD", sep.outputs["X"], L.U0)
    v = t.math("ADD", sep.outputs["Y"], L.V0)
    th = t.math("ARCTAN2", t.math("SUBTRACT", sep.outputs["Z"], L.ZC), v)
    return u, v, th


def cap_coords(t, sep):
    """Cap coordinates: the angle around its axis, the distance from the axis, the height."""
    x = t.math("SUBTRACT", sep.outputs["X"], L.CAP_C[0] - L.U0)
    y = t.math("SUBTRACT", sep.outputs["Y"], L.CAP_C[1] - L.V0)
    ang = t.math("ARCTAN2", y, x)
    rr = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", x, x), t.math("MULTIPLY", y, y)))
    return ang, rr, sep.outputs["Z"]


def band(t, u, a, b, soft=0.0008):
    """1 inside u = a..b, smooth at the edges."""
    return t.math("MULTIPLY", t.maprange(u, a - soft, a + soft, 0.0, 1.0), t.maprange(u, b - soft, b + soft, 1.0, 0.0))


def ring_line(t, x, at, half):
    """1 on the line x = at, falling to 0 at distance half."""
    return t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", x, at)), 0.0, half, 1.0, 0.0)


def knurl_cell(t, along, ang, pitch, n):
    """Diamond knurling: 0 in the grooves (two families of slanted lines), 1 at the diamond middles. A
    product, not the minimum of two waves: with the minimum the diamond breaks along the diagonals into a
    pyramid, with the product it is a smooth pillow."""
    ka = t.math("DIVIDE", along, pitch)
    kt = t.math("MULTIPLY", ang, n / (2 * math.pi))
    s1 = t.math("ABSOLUTE", t.math("SINE", t.math("MULTIPLY", t.math("ADD", ka, kt), math.pi)))
    s2 = t.math("ABSOLUTE", t.math("SINE", t.math("MULTIPLY", t.math("SUBTRACT", ka, kt), math.pi)))
    return t.math("MULTIPLY", s1, s2)


def knurl_layer(t, col, h, vec, nsep, cell, zone):
    """Pillow diamonds (relief up), dark ~1 mm grooves with dust in places, rubbed diamond tops. Returns
    (colour, height, tops - for the gloss)."""
    pil = t.math("MULTIPLY", t.math("SQRT", t.maprange(cell, 0.0, 0.85, 0.0, 1.0)), zone)
    grv = t.math("MULTIPLY", t.maprange(cell, 0.0, 0.16, 1.0, 0.0), zone)
    h = t.math("ADD", h, t.math("MULTIPLY", pil, 0.55))
    col = t.mixc(t.math("MULTIPLY", grv, 0.65), col, kmats.lin((10, 10, 11)))
    up = t.maprange(nsep.outputs["Z"], -0.2, 0.8, 0.15, 1.0)
    dmask = t.maprange(t.noise(vec, 2.6, 4.0, 0.6), 0.42, 0.72, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", grv, dmask), t.math("MULTIPLY", up, 0.6)), col,
                 kmats.lin((92, 87, 78)))
    crest = t.math("MULTIPLY", t.maprange(cell, 0.70, 1.0, 0.0, 1.0), zone)
    rubn = t.maprange(t.noise(vec, 4.0, 5.0, 0.6), 0.38, 0.70, 0.15, 1.0)
    crest = t.math("MULTIPLY", crest, rubn)
    col = t.mixc(t.math("MULTIPLY", crest, 0.30), col, kmats.lin((66, 66, 68)))
    return col, h, crest


def molded_disc(t, col, h, rr, disc):
    """Moulded bottom: a ring groove and a sprue in the middle (rr is the distance from the axis, disc is
    the bottom mask)."""
    for at, half, k in ((0.030, 0.0007, 0.5), (0.0335, 0.0005, 0.35)):
        ln = t.math("MULTIPLY", ring_line(t, rr, at, half), disc)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", ln, k))
        col = t.mixc(t.math("MULTIPLY", ln, 0.5), col, kmats.lin((12, 12, 13)))
    spr = t.math("MULTIPLY", t.maprange(rr, 0.0022, 0.0030, 1.0, 0.0), disc)
    h = t.math("ADD", h, t.math("MULTIPLY", spr, 0.4))
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", ring_line(t, rr, 0.0026, 0.0004), disc), 0.6), col,
                 kmats.lin((70, 70, 72)))
    return col, h


def weather(t, col, vec, sep, nsep, floor_z=0.0, dust=0.35, grime=0.5, cav=0.5, low_h=0.25, scratch=None):
    """kmats.weather and kmats.dayz_layers (dust on top, dirt near the ground and in corners, sun fading,
    tonal blotches, grease spots, scratches) - an own copy for a small portable item, the kit is
    untouched. In the kit streaks run along world Z and scratches along world X and Y: on a black 9 cm
    tube the streaks broke into light drops, and scratches across the sides facing +-Y became blotches.
    Here the streaks are soft and weak, grease spots have no small islands, scratches run only along the
    surface: scratch is "x" (along the tube axis), "z" (along the cap wall) or None. The rest is as in
    the kit, with the same profile numbers."""
    k = kmats.LOOK
    dayz = k["name"] == "dayz"
    if dayz:
        dust, cav = dust * k["dust_k"], cav * k["cav_k"]
    up = t.maprange(nsep.outputs["Z"], 0.4, 0.9, 0.0, 1.0)
    dn = t.maprange(t.noise(vec, 4.0, 6.0, 0.6), 0.35, 0.7, 0.4, 1.0)
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", up, dn), dust), col, kmats.DUST)
    c = t.maprange(t.cavity(0.04), 0.15, 0.6, 0.0, 1.0)
    low = t.maprange(sep.outputs["Z"], floor_z, floor_z + low_h, 1.0, 0.0)
    g = t.math("MAXIMUM", t.math("MULTIPLY", c, cav), t.math("MULTIPLY", low, grime))
    g = t.math("MULTIPLY", g, t.maprange(t.noise(vec, 7.0, 8.0, 0.6), 0.3, 0.7, 0.5, 1.0))
    col = t.mixc(g, col, kmats.GRIME)
    if not dayz:
        return col, g
    d, v = k["patina"]
    gray = t.node("ShaderNodeRGBToBW")
    t.link(col, gray.inputs[0])
    col = t.mixc(d, col, gray.outputs[0])
    col = t.mixc(1.0 - v, col, (0, 0, 0, 1))
    n1 = t.maprange(t.noise(vec, 1.7, 5.0, 0.6), 0.3, 0.7, 0.0, 1.0)
    col = t.mixc(n1, t.mixc(k["mottle"], col, (0, 0, 0, 1)), t.mixc(k["mottle"] * 0.4, col, (1, 1, 1, 1)))
    vert = t.maprange(t.math("ABSOLUTE", nsep.outputs["Z"]), 0.35, 0.6, 1.0, 0.0)
    st = t.maprange(t.noise(t.stretch(vec, 1.0, 1.0, 0.07), 16.0, 2.0, 0.5), 0.5, 0.75, 0.0, 1.0)
    st = t.math("MULTIPLY", t.math("MULTIPLY", st, vert), k["streaks"] * 0.25 * min(1.0, 0.4 + grime))
    col = t.mixc(st, col, kmats.GRIME)
    sm = t.math("MULTIPLY", t.step(t.noise(vec, 3.2, 2.0, 0.5), 0.60, 0.76), k["smudge"])
    col = t.mixc(sm, col, kmats.lin((40, 36, 30)))
    if scratch:
        sx = {"x": (0.03, 1.0, 1.0), "z": (1.0, 1.0, 0.03)}[scratch]
        s1 = t.step(t.noise(t.stretch(vec, *sx), 220.0, 2.0, 0.5), 0.71, 0.725)
        sc = t.math("MULTIPLY", s1, t.maprange(t.noise(vec, 6.0, 4.0, 0.5), 0.4, 0.7, 0.0, k["scratches"]))
        col = t.mixc(sc, col, t.mixc(0.5, col, (0.55, 0.55, 0.55, 1)))
    g = t.math("MAXIMUM", g, t.math("MAXIMUM", st, sm))
    return col, g


def wear_tail(t, col, gloss, spec, h, raw, vec, sep, nsep, edge_k=0.5, dust=0.06, grime=0.25, scratch=None):
    """Common tail of the plastic: wear on the edges (a rubbed edge is lighter, but not in blotches: noise
    gave light drops on black), dirt in corners, the look layers (dust on top, ground dirt below,
    blotches, scratches along scratch - weather())."""
    edge = t.maprange(t.edge_wear(0.0015), 0.05, 0.3, 0.0, 1.0)
    rub = t.step(t.math("ADD", t.math("MULTIPLY", t.noise(vec, 3.0, 3.0, 0.5), 0.30), t.math("MULTIPLY", edge, edge_k)),
                 0.42, 0.62)
    col = t.mixc(t.math("MULTIPLY", rub, 0.40), col, kmats.lin((70, 70, 72)))
    cav = t.maprange(t.cavity(0.004), 0.08, 0.5, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.5), col, kmats.lin((10, 10, 10)))
    col, dirt = weather(t, col, raw, sep, nsep, floor_z=0.0, dust=dust, grime=grime, cav=0.35, low_h=0.03,
                        scratch=scratch)
    gloss = t.math("SUBTRACT", gloss, t.math("ADD", t.math("MULTIPLY", dirt, 0.22), t.math("MULTIPLY", rub, 0.08)))
    spec = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, 0.14))
    return col, gloss, spec, h


def plastic_base(t, vec):
    tone = t.maprange(t.noise(vec, 1.2, 5.0, 0.55), 0.3, 0.75, 0.0, 1.0)
    col = t.mixc(tone, tuple(c * 0.82 for c in PLASTIC[:3]) + (1,), tuple(c * 1.12 for c in PLASTIC[:3]) + (1,))
    h = t.math("MULTIPLY", t.noise(vec, 30.0, 3.0, 0.5), 0.03)
    return col, h


def mat_plastic(mat, origin, face="body", seed=1.0):
    """Black plastic of the tube. body: pillow-diamond knurling between the smooth bottom and the mouth band,
    knurled clamps; end: the bottom (a moulded ring and a sprue on the end); lip: the end of the mouth;
    in: inside; lug: the lugs (the second one has a cord hole in the post)."""
    t = kmats.Tree(mat)
    raw, vec, sep = coords(t, origin, seed)
    nsep = t.normal()
    col, h = plastic_base(t, vec)
    gloss, spec = 0.40, 0.30
    u, v, th = cyl_coords(t, sep)
    if face == "body":
        zone = band(t, u, L.END_L + 0.004, L.MOUTH_U - L.MOUTH_BAND)
        ribs = None
        for c in L.CLAMPS:
            cz = band(t, u, c - L.CLAMP_W / 2, c + L.CLAMP_W / 2)
            zone = t.math("MULTIPLY", zone, t.math("SUBTRACT", 1.0, band(t, u, c - L.CLAMP_W / 2 - 0.002,
                                                                           c + L.CLAMP_W / 2 + 0.002)))
            r = t.math("MULTIPLY", cz, t.math("ADD", 0.5, t.math("MULTIPLY", 0.5, t.math(
                "COSINE", t.math("MULTIPLY", t.math("SUBTRACT", u, c), 2 * math.pi * L.CLAMP_RIBS / L.CLAMP_W)))))
            ribs = r if ribs is None else t.math("ADD", ribs, r)
        cell = knurl_cell(t, u, th, L.KNURL_ALONG, L.KNURL_N)
        col, h, crest = knurl_layer(t, col, h, vec, nsep, cell, zone)
        # clamp ribs: relief up, tops rubbed, dust in the valleys
        h = t.math("ADD", h, t.math("MULTIPLY", ribs, 0.9))
        rtop = t.math("MULTIPLY", t.step(ribs, 0.80, 0.97), t.maprange(t.noise(vec, 5.0, 4.0, 0.6), 0.35, 0.7, 0.3, 1.0))
        col = t.mixc(t.math("MULTIPLY", rtop, 0.40), col, kmats.lin((78, 78, 80)))
        cz_all = t.math("SUBTRACT", 1.0, t.math("ADD", zone, t.math("SUBTRACT", 1.0, band(t, u, L.END_L + 0.004,
                                                                                              L.MOUTH_U - L.MOUTH_BAND))))
        dol = t.math("MULTIPLY", t.math("MULTIPLY", t.math("SUBTRACT", 1.0, t.step(ribs, 0.15, 0.45)),
                                        t.math("MAXIMUM", cz_all, 0.0)),
                     t.maprange(t.noise(vec, 3.0, 4.0, 0.6), 0.4, 0.7, 0.0, 0.5))
        col = t.mixc(dol, col, kmats.lin((88, 84, 76)))
        # smooth band at the mouth: rubbed by the cap - smoother, ring scratches; a stop mark at its start
        mb = band(t, u, L.MOUTH_U - L.MOUTH_BAND + 0.003, L.MOUTH_U - 0.001)
        scr = t.step(t.noise(t.stretch(vec, 1.0, 0.02, 0.02), 40.0, 3.0, 0.6), 0.62, 0.70)
        col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", mb, scr), 0.35), col, kmats.lin((96, 96, 98)))
        stop = ring_line(t, u, L.MOUTH_U - L.MOUTH_BAND + 0.0015, 0.0006)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", stop, 0.4))
        col = t.mixc(t.math("MULTIPLY", stop, 0.5), col, kmats.lin((14, 14, 15)))
        gloss = t.math("ADD", t.math("SUBTRACT", 0.44, t.math("MULTIPLY", zone, 0.12)),
                       t.math("ADD", t.math("MULTIPLY", crest, 0.10), t.math("MULTIPLY", mb, 0.06)))
    elif face == "end":
        rr = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", v, v), t.math("MULTIPLY", t.math(
            "SUBTRACT", sep.outputs["Z"], L.ZC), t.math("SUBTRACT", sep.outputs["Z"], L.ZC))))
        disc = t.maprange(u, 0.0004, 0.0001, 0.0, 1.0)
        col, h = molded_disc(t, col, h, rr, disc)
        gloss = 0.36
    elif face == "in":
        col = t.mixc(0.55, col, kmats.lin((12, 12, 12)))
        gloss = 0.30
    elif face == "lug":
        hole = t.maprange(dist_to(t, sep, HOLE_LUG), 0.0012, 0.0017, 1.0, 0.0)
        col = t.mixc(hole, col, kmats.lin((6, 6, 6)))
        gloss = 0.38
    col, gloss, spec, h = wear_tail(t, col, gloss, spec, h, raw, vec, sep, nsep,
                                    edge_k=0.7 if face in ("end", "lip", "lug") else 0.5,
                                    scratch="x" if face == "body" else None)
    return kmats.out(t, col, gloss, spec, h)


def mat_cap(mat, origin, face="out"):
    """Cap: the same black plastic, diamond knurling, two moulded marks near the bottom, a moulded ring and a
    sprue on the bottom, a cord hole near the edge; the rim is rubbed; dark inside."""
    t = kmats.Tree(mat)
    raw, vec, sep = coords(t, origin, 2.6)
    nsep = t.normal()
    col, h = plastic_base(t, vec)
    ang, rr, z = cap_coords(t, sep)
    gloss = {"out": 0.40, "rim": 0.30, "in": 0.28}[face]
    crest = 0.0
    if face == "out":
        side = t.maprange(rr, L.CAP_R - 0.0012, L.CAP_R - 0.0004, 0.0, 1.0)
        zone = t.math("MULTIPLY", band(t, z, 0.018, L.CAP_H - 0.007), side)
        cell = knurl_cell(t, z, ang, L.KNURL_ALONG, L.KNURL_N)
        col, h, crest = knurl_layer(t, col, h, vec, nsep, cell, zone)
        for zr in (0.010, 0.014):
            ln = t.math("MULTIPLY", ring_line(t, z, zr, 0.0006), side)
            h = t.math("SUBTRACT", h, t.math("MULTIPLY", ln, 0.6))
            col = t.mixc(t.math("MULTIPLY", ln, 0.5), col, kmats.lin((14, 14, 15)))
        disc = t.maprange(z, 0.0004, 0.0001, 0.0, 1.0)
        col, h = molded_disc(t, col, h, rr, disc)
        hole = t.maprange(dist_to(t, sep, HOLE_CAP), 0.0013, 0.0018, 1.0, 0.0)
        col = t.mixc(hole, col, kmats.lin((6, 6, 6)))
        gloss = t.math("ADD", t.math("SUBTRACT", 0.42, t.math("MULTIPLY", zone, 0.10)), t.math("MULTIPLY", crest, 0.10))
    if face == "in":
        col = t.mixc(0.30, col, kmats.lin((16, 16, 16)))
    col, gloss, spec, h = wear_tail(t, col, gloss, 0.30 if face != "in" else 0.18, h, raw, vec, sep, nsep,
                                    edge_k=0.8 if face == "rim" else 0.5, dust=0.05 if face == "in" else 0.06,
                                    scratch="z" if face == "out" else None)
    return kmats.out(t, col, gloss, spec, h)


def paper_attr(t, name):
    attr = t.node("ShaderNodeAttribute")
    attr.attribute_type = "GEOMETRY"
    attr.attribute_name = name
    sep = t.node("ShaderNodeSeparateXYZ")
    t.link(attr.outputs["Vector"], sep.inputs[0])
    return sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]


MAP_S = 0.110          # sheet strip in map.png (make_decals.MAP_S)


def map_image(t, tt, s, shift=0.0):
    return t.image(wdecal("map.png"), t.math("SUBTRACT", tt, shift) if shift else tt, s,
                   (L.SHEET_T / 2, MAP_S / 2), (L.SHEET_T, MAP_S))


def mat_paper_out(mat, origin):
    """Outer turn of the tracing paper: milky paper, yellowed towards the end, the ink of the next turn shows
    through it palely (the same drawing shifted by a turn), its own ink on top; a crease along the axis
    and a folded corner at the free edge; in shadow inside the tube; thumbed at the end."""
    t = kmats.Tree(mat)
    raw, vec, sep = coords(t, origin, 3.3, 30.0)
    nsep = t.normal()
    tt, s, _ = paper_attr(t, "paper")
    base = kmats.lin((196, 199, 193))
    col = t.mixc(t.maprange(t.noise(vec, 1.5, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0), tuple(c * 0.93 for c in base[:3]) + (1,), base)
    yel = t.math("MULTIPLY", t.maprange(s, 0.0, 0.05, 0.50, 0.12), t.maprange(t.noise(vec, 0.9, 4.0, 0.5), 0.3, 0.7, 0.5, 1.0))
    col = t.mixc(yel, col, kmats.lin((204, 190, 150)))
    _, ga = map_image(t, tt, s, -TURN)
    col = t.mixc(t.math("MULTIPLY", ga, 0.30), col, kmats.lin((124, 130, 134)))
    ic, ia = map_image(t, tt, s)
    col = t.mixc(t.math("MULTIPLY", ia, 0.92), col, ic)
    # crease along the axis and a folded corner at the free edge near the end
    crease = ring_line(t, tt, L.CREASE_T, 0.0011)
    dog = ring_line(t, t.math("ADD", t.math("MULTIPLY", tt, 1.15), s), 0.014, 0.0008)
    corner = t.maprange(t.math("ADD", t.math("MULTIPLY", tt, 1.15), s), 0.0125, 0.0145, 1.0, 0.0)
    col = t.mixc(t.math("MULTIPLY", t.math("ADD", crease, dog), 0.12), col, kmats.lin((150, 150, 144)))
    col = t.mixc(t.math("MULTIPLY", corner, 0.18), col, kmats.lin((176, 168, 140)))
    grime = t.math("MULTIPLY", t.maprange(s, 0.0, 0.025, 1.0, 0.0),
                   t.maprange(t.noise(vec, 2.5, 5.0, 0.6), 0.35, 0.75, 0.0, 0.45))
    col = t.mixc(grime, col, kmats.lin((146, 136, 116)))
    shade = t.maprange(s, L.ROLL_OUT - 0.004, L.ROLL_OUT + 0.012, 1.0, 0.25)
    col = t.mixc(t.math("SUBTRACT", 1.0, shade), col, kmats.lin((26, 27, 28)))
    cav = t.maprange(t.cavity(0.003), 0.1, 0.5, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.35), col, kmats.lin((70, 72, 72)))
    col, dirt = weather(t, col, raw, sep, nsep, floor_z=0.0, dust=0.04, grime=0.10, cav=0.2, low_h=0.02)
    wr = t.noise(t.stretch(vec, 1.0, 0.25, 0.25), 9.0, 3.0, 0.5)
    h = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 14.0, 3.0, 0.5), 0.03), t.math("MULTIPLY", wr, 0.05))
    h = t.math("ADD", h, t.math("MULTIPLY", t.math("ADD", crease, dog), 0.45))
    return kmats.out(t, col, t.math("SUBTRACT", 0.16, t.math("MULTIPLY", dirt, 0.08)), 0.10, h)


def mat_paper_in(mat, origin):
    """Inside the roll: the back of the sheet (ink mirrored, pale), darker the deeper it goes."""
    t = kmats.Tree(mat)
    raw, vec, sep = coords(t, origin, 3.9, 30.0)
    tt, s, _ = paper_attr(t, "paper")
    col = t.mixc(t.maprange(t.noise(vec, 1.5, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0), kmats.lin((150, 154, 150)),
                 kmats.lin((172, 174, 168)))
    _, ia = map_image(t, tt, s)
    col = t.mixc(t.math("MULTIPLY", ia, 0.40), col, kmats.lin((96, 100, 104)))
    deep = t.maprange(s, 0.0, L.ROLL_END - L.ROLL_IN_U, 0.0, 0.88)
    col = t.mixc(deep, col, kmats.lin((14, 14, 15)))
    return kmats.out(t, col, 0.10, 0.06, t.math("MULTIPLY", t.noise(vec, 9.0, 3.0, 0.5), 0.03))


def mat_paper_edge(mat, origin):
    """End of the roll: the edges of 2.4 turns of tracing paper - thin lines between the turns, yellowed,
    thumbed."""
    t = kmats.Tree(mat)
    raw, vec, sep = coords(t, origin, 4.4, 30.0)
    vc, zc = L.roll_axis()
    y = t.math("SUBTRACT", t.math("ADD", sep.outputs["Y"], L.V0), vc)
    z = t.math("SUBTRACT", sep.outputs["Z"], zc)
    rr = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", y, y), t.math("MULTIPLY", z, z)))
    lay = t.math("DIVIDE", t.math("SUBTRACT", L.ROLL_R + L.ROLL_FLARE, rr), L.ROLL_WALL / 2.4)
    line = t.maprange(t.math("ABSOLUTE", t.math("SINE", t.math("MULTIPLY", lay, math.pi))), 0.0, 0.35, 1.0, 0.0)
    base = kmats.lin((214, 212, 200))
    col = t.mixc(t.maprange(t.noise(vec, 2.0, 5.0, 0.6), 0.3, 0.75, 0.0, 1.0), tuple(c * 0.90 for c in base[:3]) + (1,), base)
    col = t.mixc(t.math("MULTIPLY", line, 0.40), col, kmats.lin((118, 116, 108)))
    col = t.mixc(t.maprange(t.noise(vec, 1.2, 4.0, 0.5), 0.35, 0.7, 0.1, 0.4), col, kmats.lin((198, 182, 140)))
    return kmats.out(t, col, 0.10, 0.06, t.math("MULTIPLY", line, -0.3))


def mat_flat(mat, origin, color, seed=4.0, gloss=0.12, spec=0.06):
    t = kmats.Tree(mat)
    raw, vec, sep = coords(t, origin, seed, 30.0)
    col = t.mixc(t.maprange(t.noise(vec, 2.0, 5.0, 0.6), 0.3, 0.75, 0.0, 1.0),
                 tuple(c * 0.92 for c in color[:3]) + (1,), color)
    return kmats.out(t, col, gloss, spec, 0.0)


def mat_label(mat, origin):
    """Tag: the picture by tag coordinates, matte paper, a shadow along the edge, dust on top."""
    t = kmats.Tree(mat)
    raw, vec, sep = coords(t, origin, 5.1, 30.0)
    nsep = t.normal()
    a, b, _ = paper_attr(t, "lbl")
    col, _ = t.image(wdecal("label.png"), a, b, (0.0, 0.0), L.LABEL_SIZE)
    cav = t.maprange(t.cavity(0.003), 0.1, 0.5, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.4), col, kmats.lin((80, 70, 54)))
    col, dirt = weather(t, col, raw, sep, nsep, floor_z=0.0, dust=0.05, grime=0.05, cav=0.2, low_h=0.01)
    return kmats.out(t, col, 0.10, 0.05, t.math("MULTIPLY", t.noise(vec, 14.0, 3.0, 0.5), 0.05))


def mat_strap(mat, origin):
    """Strap: black leatherette embossed like leather, stitching along the edges, the end at the lug stitched
    with a rectangle with a cross; edges and bends rubbed to grey-brown (attribute strapp = (from the near
    end, across -1..1, side +-1))."""
    t = kmats.Tree(mat)
    raw, vec, sep = coords(t, origin, 6.4, 40.0)
    nsep = t.normal()
    sd, sw, sn = paper_attr(t, "strapp")
    base = kmats.lin((30, 28, 27))
    grain = t.noise(vec, 40.0, 4.0, 0.7)
    col = t.mixc(t.maprange(t.noise(vec, 1.5, 5.0, 0.6), 0.3, 0.75, 0.0, 1.0), tuple(c * 0.8 for c in base[:3]) + (1,), base)
    col = t.mixc(t.math("MULTIPLY", t.maprange(grain, 0.45, 0.65, 0.0, 1.0), 0.25), col, kmats.lin((58, 54, 50)))
    aw = t.math("ABSOLUTE", sw)
    dash = t.maprange(t.math("SINE", t.math("MULTIPLY", sd, 2 * math.pi / 0.0032)), -0.1, 0.25, 0.0, 1.0)
    stitch = t.math("MULTIPLY", ring_line(t, aw, 0.84, 0.05), dash)
    # stitching of the end: a rectangle with a cross on the tail, outside (sn > 0)
    a0, a1, wb = 0.0025, 0.0105, 0.62
    in_box = t.math("MULTIPLY", band(t, sd, a0, a1, 0.0004), t.maprange(aw, wb + 0.04, wb + 0.02, 0.0, 1.0))
    rel = t.math("MULTIPLY", t.math("SUBTRACT", t.math("DIVIDE", t.math("SUBTRACT", sd, a0), a1 - a0), 0.5), 2.0 * wb)
    diag = t.math("MAXIMUM", ring_line(t, sw, rel, 0.05), ring_line(t, sw, t.math("MULTIPLY", rel, -1.0), 0.05))
    edges = t.math("MAXIMUM", t.math("MAXIMUM", ring_line(t, sd, a0, 0.0004), ring_line(t, sd, a1, 0.0004)),
                   ring_line(t, aw, wb, 0.04))
    dash2 = t.maprange(t.math("SINE", t.math("MULTIPLY", t.math("ADD", sd, t.math("MULTIPLY", aw, 0.006)),
                                             2 * math.pi / 0.0024)), -0.1, 0.25, 0.0, 1.0)
    box = t.math("MULTIPLY", t.math("MULTIPLY", t.math("MAXIMUM", diag, edges), in_box),
                 t.math("MULTIPLY", dash2, t.math("GREATER_THAN", sn, 0.0)))
    thread = t.math("MAXIMUM", stitch, box)
    col = t.mixc(t.math("MULTIPLY", thread, 0.85), col, kmats.lin((80, 76, 70)))
    edge = t.maprange(t.edge_wear(0.0008), 0.05, 0.3, 0.0, 1.0)
    rub = t.step(t.math("ADD", t.math("MULTIPLY", t.noise(vec, 5.0, 6.0, 0.6), 0.7), t.math("MULTIPLY", edge, 0.7)),
                 0.62, 0.72)
    col = t.mixc(t.math("MULTIPLY", rub, 0.55), col, kmats.lin((86, 72, 60)))
    cav = t.maprange(t.cavity(0.003), 0.1, 0.5, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.4), col, kmats.lin((10, 9, 8)))
    col, dirt = weather(t, col, raw, sep, nsep, floor_z=0.0, dust=0.05, grime=0.30, cav=0.3, low_h=0.02)
    h = t.math("ADD", t.math("MULTIPLY", grain, 0.08), t.math("MULTIPLY", thread, 0.30))
    return kmats.out(t, col, t.math("SUBTRACT", 0.26, t.math("MULTIPLY", dirt, 0.12)), 0.20, h)


def mat_cord(mat, origin):
    """Cotton cord: grey-beige, twisted in three strands (attribute cordp = (along, cos, sin of the angle)),
    thumbed, dirty from the ground below."""
    t = kmats.Tree(mat)
    raw, vec, sep = coords(t, origin, 8.2, 30.0)
    nsep = t.normal()
    s, ca, sa = paper_attr(t, "cordp")
    ang = t.math("ARCTAN2", sa, ca)
    ply = t.math("SINE", t.math("ADD", t.math("MULTIPLY", s, 2 * math.pi / 0.0030), t.math("MULTIPLY", ang, 3.0)))
    tw = t.maprange(ply, -1.0, 1.0, 0.0, 1.0)
    col = t.mixc(t.maprange(t.noise(vec, 3.0, 5.0, 0.6), 0.3, 0.75, 0.0, 1.0), kmats.lin((128, 120, 100)),
                 kmats.lin((178, 168, 144)))
    col = t.mixc(t.math("MULTIPLY", t.maprange(tw, 0.55, 0.9, 0.0, 1.0), 0.45), col, kmats.lin((92, 84, 66)))
    cav = t.maprange(t.cavity(0.002), 0.1, 0.5, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.4), col, kmats.lin((60, 54, 42)))
    col, dirt = weather(t, col, raw, sep, nsep, floor_z=0.0, dust=0.05, grime=0.45, cav=0.4, low_h=0.012)
    return kmats.out(t, col, 0.05, 0.03, t.math("MULTIPLY", tw, 0.25))


KINDS = {
    "plastic_body": (mat_plastic, dict(face="body")),
    "plastic_end": (mat_plastic, dict(face="end", seed=1.3)),
    "plastic_lip": (mat_plastic, dict(face="lip", seed=1.6)),
    "plastic_in": (mat_plastic, dict(face="in", seed=1.9)),
    "lug": (mat_plastic, dict(face="lug", seed=2.2)),
    "cap_out": (mat_cap, dict(face="out")),
    "cap_rim": (mat_cap, dict(face="rim")),
    "cap_in": (mat_cap, dict(face="in")),
    "paper_out": (mat_paper_out, {}),
    "paper_in": (mat_paper_in, {}),
    "paper_edge": (mat_paper_edge, {}),
    "paper_gap": (mat_flat, dict(color=kmats.lin((64, 66, 64)), seed=4.6, gloss=0.08, spec=0.04)),
    "dark": (mat_flat, dict(color=kmats.lin((12, 12, 12)), seed=4.8, gloss=0.02, spec=0.0)),
    "label": (mat_label, {}),
    "strap": (mat_strap, {}),
    "cord": (mat_cord, {}),
}

OBJ, NAME = "m66_carrier_trail", "ozr_carrier_trail"
# rvmat from the "dayz" profile (specular 1.0: the highlight is cut by _smdi)
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=("camoGround",), hidden=("camoGround",))
P = M.part
BOUNDS = {}


# --- geometry -------------------------------------------------------------------------------------
def fan(p, region, ring, center, want):
    p.use(region, *REGIONS[region])
    c = p.bm.verts.new(center)
    faces = []
    n = len(ring)
    for i in range(n):
        f = p.bm.faces.new((ring[i], ring[(i + 1) % n], c))
        f.normal_update()
        if f.normal.dot(Vector(want)) < 0:
            f.normal_flip()
        faces.append(f)
    p.tag(faces)
    return faces


def lathe(p, prof, ths, point, normal):
    """Solid of revolution: prof is [(a, r, region of the belt up to the next point)], a along the axis, r
    from it; point(a, r, th) gives a Blender point, normal(na, nr, th) the outward vector of the face. A
    belt faces away from the body: (-dr, da) in the (a, r) plane. Returns the vertex rings."""
    rings = [[p.bm.verts.new(point(a, r, th)) for th in ths] for a, r, _ in prof]
    n = len(ths)
    half = math.pi / n
    for i in range(len(prof) - 1):
        (a0, r0, reg), (a1, r1, _) = prof[i], prof[i + 1]
        p.use(reg, *REGIONS[reg])
        faces = []
        for k in range(n):
            j = (k + 1) % n
            f = p.bm.faces.new((rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]))
            f.normal_update()
            if f.normal.dot(Vector(normal(-(r1 - r0), a1 - a0, ths[k] + half))) < 0:
                f.normal_flip()
            faces.append(f)
        p.tag(faces)
    return rings


def tube_point(a, r, th):
    return tpt(a, r, th)


def tube_normal(na, nr, th):
    return (na, nr * math.cos(th), nr * math.sin(th))


def build_tube(lod):
    """Body (camoGround): the cup-like bottom with a rounded end, the body with knurling (a pattern), the
    mouth end with a chamfer, the wall inside down to the dark gap."""
    n = L.SIDES[lod]
    ths = L.theta_list(n)
    p = P("tube", "body", group="camoGround")
    if lod == 0:
        # the end is rounded by two belts of faces at 30 and 60 degrees: the 30 degree joints get smoothed
        s = L.BOT_R / (math.cos(math.radians(30)) + math.sin(math.radians(30)))
        prof = [(0.0, L.R_END - L.BOT_R, "end"),
                (s * math.sin(math.radians(30)), L.R_END - L.BOT_R + s * math.cos(math.radians(30)), "end"),
                (L.BOT_R, L.R_END, "end"),
                (L.END_L, L.R_END, "body"),
                (L.END_L, L.R, "body"),
                (L.MOUTH_U - L.LIP_CH, L.R, "lip"),
                (L.MOUTH_U, L.R - L.LIP_CH, "lip"),
                (L.MOUTH_U, L.R_IN, "inner"),
                (L.DEEP_U, L.R_IN, None)]
    else:
        prof = [(0.0, L.R_END, "end"), (L.END_L, L.R_END, "body"), (L.END_L, L.R, "body"), (L.MOUTH_U, L.R, "lip"),
                (L.MOUTH_U, L.R_IN, "inner"), (L.DEEP_U, L.R_IN, None)]
    rings = lathe(p, prof, ths, tube_point, tube_normal)
    fan(p, "end", rings[0], W(0.0, 0.0, L.ZC), (-1, 0, 0))
    p.bm.normal_update()
    BOUNDS["deep_ring"] = [tuple(v.co) for v in rings[-1]]
    return p


def roll_loop(u, lod, inner=False, flap=0.0):
    """Section of the roll at u: [(Blender point, phi, r)] from the free edge (phi = 0) in the winding
    direction to the end of the turn (phi = 2pi, under the edge); inner is the inner surface (without the
    step); flap is how far the free edge lags (the first two points)."""
    n = L.SIDES[lod]
    vc, zc = L.roll_axis()
    out = []
    for k in range(n + (0 if inner else 1)):
        phi = 2 * math.pi * k / n
        th = L.EDGE_THETA + L.WIND * phi
        r = L.roll_radius(phi, u)
        if inner:
            r = L.roll_radius(0.0, min(u, L.ROLL_END)) - L.ROLL_WALL
        elif k < 2:
            r += flap * (1.0, 0.35)[k]
        out.append((tpt(u, r, th, zc, vc), phi, r))
    return out


def build_roll(lod):
    """Tracing paper roll: the outer turn as a spiral with a step at the free edge (attribute paper = (t, s):
    t along the sheet from the free edge, s from the end of the roll), the edge lags slightly at the end;
    the end is stepped (the inner turns slide out), inside is the back of the sheet as a cone into the
    dark. The outer turn is a single belt from the gap in the depth to the end: it unwinds by 1.2 mm, a
    separate belt at the mouth gave nothing."""
    p = P("roll", "roll_out")
    lay = p.bm.verts.layers.float_vector.new("paper")
    us = [L.DEEP_U, L.ROLL_END]
    vc, zc = L.roll_axis()
    th_e = L.EDGE_THETA
    tang = (0.0, -math.sin(th_e) * L.WIND, math.cos(th_e) * L.WIND)   # along the winding direction at the edge

    def vert(co, tt, s):
        q = p.bm.verts.new(co)
        q[lay] = (tt, s, 0.0)
        return q

    def flap(u):
        return L.ROLL_FLAP if (lod == 0 and u >= L.ROLL_END) else 0.0
    rings = []
    for u in us:
        rings.append([vert(co, phi * L.ROLL_R, L.ROLL_END - u) for co, phi, r in roll_loop(u, lod, flap=flap(u))])
    p.use("roll_out", *REGIONS["roll_out"])
    faces = []
    for a, b in zip(rings, rings[1:]):
        for k in range(len(a) - 1):
            f = p.bm.faces.new((a[k], a[k + 1], b[k + 1], b[k]))
            f.normal_update()
            c = f.calc_center_median()
            if f.normal.dot(Vector((0.0, c.y + L.V0 - vc, c.z - zc))) < 0:
                f.normal_flip()
            faces.append(f)
    p.tag(faces)
    # step at the free edge: from the edge (phi = 0) down to the end of the turn (phi = 2pi), facing against
    # the winding direction - where the lower turn is visible; near the end there is a shadow under the
    # lagging edge
    p.use("roll_gap", *REGIONS["roll_gap"])
    faces = []
    for a, b in zip(rings, rings[1:]):
        f = p.bm.faces.new((a[0], a[-1], b[-1], b[0]))
        f.normal_update()
        if f.normal.dot(Vector(tuple(-c for c in tang))) < 0:
            f.normal_flip()
        faces.append(f)
    p.tag(faces)
    # end: from the outer section to the inner one, the inner turns slide out by ROLL_TELE
    outer = rings[-1]
    u_in = L.ROLL_END + (L.ROLL_TELE if lod == 0 else 0.0)
    inner = [vert(co, L.TURN_IN0 + phi * L.ROLL_R, L.ROLL_END - u_in)
             for co, phi, r in roll_loop(u_in, lod, inner=True)]
    p.use("roll_edge", *REGIONS["roll_edge"])
    n = len(inner)
    faces = []
    for k in range(n):
        q = (outer[k], outer[k + 1], inner[(k + 1) % n], inner[k])
        f = p.bm.faces.new(q)
        f.normal_update()
        if f.normal.x < 0:
            f.normal_flip()
        faces.append(f)
    # between outer[-1] and outer[0] is a step at the same radius as inner[0]: it has no area
    p.tag(faces)
    # inside: the back of the sheet as a cone towards the axis, darkening to black in the depth (the
    # material works by s) - instead of a wall and a dark bottom, 56 triangles fewer. Each triangle has its
    # own apex, with t from the middle of its edge: the ink on the back does not stretch in rays towards
    # the apex
    apex = tpt(L.ROLL_CONE_U, 0.0, 0.0, zc, vc)
    p.use("roll_in", *REGIONS["roll_in"])
    faces = []
    for k in range(n):
        tip = vert(apex, L.TURN_IN0 + (k + 0.5) * TURN / n, L.ROLL_END - L.ROLL_CONE_U)
        f = p.bm.faces.new((inner[k], inner[(k + 1) % n], tip))
        f.normal_update()
        c = f.calc_center_median()
        if f.normal.dot(Vector((0.3, -(c.y + L.V0 - vc), -(c.z - zc)))) < 0:
            f.normal_flip()
        faces.append(f)
    p.tag(faces)
    p.bm.normal_update()
    return p


def build_dark(lod, deep_ring):
    """Dark gap between the tube wall and the roll deep in the mouth."""
    p = P("dark", "dark")
    n = L.SIDES[lod]
    ths = L.theta_list(n)
    vc, zc = L.roll_axis()
    a = [p.bm.verts.new(q) for q in deep_ring]
    b = []
    for th in ths:
        phi = ((L.EDGE_THETA - th) * L.WIND) % (2 * math.pi)
        b.append(p.bm.verts.new(tpt(L.DEEP_U, L.roll_radius(phi, L.DEEP_U) - 0.0002, th, zc, vc)))
    p.use("dark", *REGIONS["dark"])
    faces = []
    for k in range(n):
        j = (k + 1) % n
        f = p.bm.faces.new((a[k], a[j], b[j], b[k]))
        f.normal_update()
        if f.normal.x < 0:
            f.normal_flip()
        faces.append(f)
    p.tag(faces)
    p.bm.normal_update()
    return p


def build_cap(lod):
    """Removed cap: a cup with its bottom on the ground and its open edge up; chamfers on the bottom and the
    rim."""
    p = P("cap", "cap_out", group="camoGround")
    n = L.CAP_SIDES[lod]
    ths = [2 * math.pi * k / n for k in range(n)]
    cu, cv = L.CAP_C

    def point(a, r, th):
        return W(cu + r * math.cos(th), cv + r * math.sin(th), a)

    def normal(na, nr, th):
        return (nr * math.cos(th), nr * math.sin(th), na)
    if lod == 0:
        prof = [(0.0, L.CAP_R - L.CAP_CH_B, "cap_out"), (L.CAP_CH_B, L.CAP_R, "cap_out"),
                (L.CAP_H - L.CAP_CH_T, L.CAP_R, "cap_rim"), (L.CAP_H, L.CAP_R - L.CAP_CH_T, "cap_rim"),
                (L.CAP_H, L.CAP_RI, "cap_in"), (L.CAP_IN_Z, L.CAP_RI, None)]
    else:
        prof = [(0.0, L.CAP_R, "cap_out"), (L.CAP_H, L.CAP_R, "cap_rim"), (L.CAP_H, L.CAP_RI, "cap_in"),
                (L.CAP_IN_Z, L.CAP_RI, None)]
    rings = lathe(p, prof, ths, point, normal)
    fan(p, "cap_out", rings[0], W(cu, cv, 0.0), (0, 0, -1))
    fan(p, "cap_in", rings[-1], W(cu, cv, L.CAP_IN_Z), (0, 0, 1))
    p.bm.normal_update()
    return p


def lug_frame(c):
    th = L.LUG_THETA
    o = Vector(tpt(c, 0.0, th))
    return g.Frame(o, (1, 0, 0), (0, -math.sin(th), math.cos(th)), (0, math.cos(th), math.sin(th)))


def build_lugs(lod):
    """Clamp lugs for the strap: cast brackets (two posts and a crossbar), standing on the middle of a body
    face, the posts sunk in; a block in the middle LOD."""
    p = P("lugs", "lug", group="camoGround")
    rf = L.R * math.cos(math.pi / L.SIDES[0])
    top = L.R + L.LUG_GAP + L.LUG_T
    for c in L.CLAMPS:
        fr = lug_frame(c)
        if lod == 0:
            a0 = L.LUG_L / 2 - L.LUG_T / 2
            cb, cm = rf - L.LUG_SINK, top - L.LUG_T / 2
            g.sweep(p, [fr.p(-a0, 0.0, cb), fr.p(-a0, 0.0, cm), fr.p(a0, 0.0, cm), fr.p(a0, 0.0, cb)], fr.v,
                    L.LUG_T / 2, L.LUG_D / 2)
        else:
            g.box(p, -L.LUG_L / 2, L.LUG_L / 2, -L.LUG_D / 2, L.LUG_D / 2, rf - L.LUG_SINK, top, frame=fr)
    p.bm.normal_update()
    return p


def label_pts(a, b, n, lift=0.0):
    """Tag point: a along the axis from the middle, b along the arc (b grows towards smaller theta, so the
    image is not mirrored); on a flat face of the body n-gon, lift is the height above it (the peeled
    corner)."""
    th = L.LABEL_THETA - b / L.R
    r = L.facet_radius(L.R, n, th) + L.LABEL_T + lift
    return tpt(L.LABEL_U + a, r, th)


def build_label(lod):
    p = P("label", "label")
    lay = p.bm.verts.layers.float_vector.new("lbl")
    n = L.SIDES[lod]
    hw, hh = L.LABEL_SIZE[0] / 2, L.LABEL_SIZE[1] / 2
    pa, pb, ph = L.LABEL_PEEL
    # along the arc: the tag edges and the polygon vertices between them (tag faces are parallel to the body
    # faces)
    bs = [-hh, hh]
    for th in L.theta_list(n):
        b = (L.LABEL_THETA - th) * L.R
        if -hh + 0.001 < b < hh - 0.001:
            bs.append(b)
    if lod == 0 and all(abs(b - (hh - pb)) > 0.002 for b in bs):
        bs.append(hh - pb)
    bs.sort()
    As = [-hw, 0.0, hw - pa, hw] if lod == 0 else [-hw, hw]
    grid = []
    for a in As:
        row = []
        for b in bs:
            q = p.bm.verts.new(label_pts(a, b, n, ph if (lod == 0 and a == hw and b == hh) else 0.0))
            q[lay] = (a, b, 0.0)
            row.append(q)
        grid.append(row)
    faces = []
    for i in range(len(As) - 1):
        for j in range(len(bs) - 1):
            f = p.bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
            f.normal_update()
            c = f.calc_center_median()
            if f.normal.dot(Vector((0.0, c.y + L.V0, c.z - L.ZC))) < 0:
                f.normal_flip()
            faces.append(f)
    p.tag(faces)
    p.bm.normal_update()
    return p


def bez(p0, p1, p2, p3, t):
    """Point of a cubic Bezier curve (vectors)."""
    a = 1.0 - t
    return p0 * a ** 3 + p1 * (3 * a * a * t) + p2 * (3 * a * t * t) + p3 * t ** 3


def strap_half(c, sgn, lod, tail=0.024, dv=0.0):
    """Half of the strap from the end at the lug with middle c down to the ground: [(point (u, v, z), where
    the face of the tape looks)]. sgn is the direction the strap leaves the lug along the axis (+1 for the
    first lug). Near LOD: the end of the strap lies over the strap (the tail), rises onto the crossbar,
    wraps it and goes under it - then the strap runs along the side of the tube; it hangs from the tube
    in a Bezier curve down to the ground (touching it on the way to the middle) and runs along the ground
    in a smooth arc to the middle; the tape face looks outwards at the tail, towards the tube after the
    wrap, and turns down towards the ground. Middle LOD: the strap starts in the lug block, with half as
    many points."""
    def P_(x, y, du=0.0):
        return on_lug(c, x, y, sgn * du)
    ym, yt, yo = L.STRAP_Y
    x8 = L.R * (math.radians(8.0) - L.LUG_THETA)
    out = []
    if lod == 0:
        for x, y in ((-tail, yt), (-0.012, yt), (-0.0070, 0.0046), (-0.0038, yo), (0.0036, yo)):
            out.append((P_(x, y), lug_dirs(x)[0]))
        wx, wy, wr = L.STRAP_WRAP
        for deg in (30.0, -30.0):
            a = math.radians(deg)
            x, y = wx + wr * math.cos(a), wy + wr * math.sin(a)
            rad, tng = lug_dirs(x)
            out.append((P_(x, y), tng * math.cos(a) + rad * math.sin(a)))
        for x, du in ((0.0036, 0.0), (-0.0042, 0.0), (-0.014, 0.0), (-0.026, 0.0015)):
            out.append((P_(x, ym, du), -lug_dirs(x)[0]))
        prev = Vector(P_(-0.026, ym, 0.0015))
    else:
        out.append((P_(0.0, 0.0015), -lug_dirs(0.0)[0]))
        prev = Vector(P_(0.0, 0.0015))
    # leaves the tube at theta = 8 degrees, hangs and lies down on the ground
    p0 = Vector(P_(x8, ym + 0.0003, 0.010))
    n0 = -lug_dirs(x8)[0]
    out.append((tuple(p0), n0))
    down = Vector((0.0, 0.0, -1.0))
    gp = Vector((c + sgn * 0.040, 0.0640 + dv, GND))
    tg = Vector((sgn * 1.0, 0.25, 0.0)).normalized()
    p1, p2 = p0 + (p0 - prev).normalized() * 0.020, gp - tg * 0.016
    # points are denser towards the ground: the bend is steeper there (the kink at the contact is no more
    # than ~25 degrees)
    for t in ((0.42, 0.70, 0.88) if lod == 0 else (0.5,)):
        w = t ** 0.8
        out.append((tuple(bez(p0, p1, p2, gp, t)), (n0 * (1.0 - w) + down * w).normalized()))
    out.append((tuple(gp), down))
    if lod == 0:
        out.append(((c + sgn * 0.062, 0.0688 + dv * 0.5, GND), down))
    return out


def strap_path(lod):
    """The whole strap: from the tail at the first lug to the tail at the second, the middle lies on the
    ground."""
    c0, c1 = L.CLAMPS
    a = strap_half(c0, 1.0, lod)
    b = strap_half(c1, -1.0, lod, tail=0.021, dv=0.0016)
    mid = ((c0 + c1) / 2, 0.0700, GND)
    return a + [(mid, Vector((0.0, 0.0, -1.0)))] + b[::-1]


def ribbon(p, path, hw, ht, attr):
    """Tape of rectangular section along a path [(tube point, where the face looks)]: the width is across the
    path in the face plane, the ends are closed. Attribute attr = (from the near end along the path,
    across -1..1, side +-1) is for the stitching in the material."""
    bm = p.bm
    lay = bm.verts.layers.float_vector.new(attr)
    pts = [Vector(W(*q)) for q, _ in path]
    nfs = [Vector(n) for _, n in path]
    n = len(pts)
    acc = [0.0]
    for i in range(1, n):
        acc.append(acc[-1] + (pts[i] - pts[i - 1]).length)
    total = acc[-1]
    rings = []
    for i in range(n):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        w = t.cross(nfs[i].normalized()).normalized()
        nf = w.cross(t).normalized()
        c = pts[i]
        sd = min(acc[i], total - acc[i])
        ring = []
        for sw, sn in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
            q = bm.verts.new(c + w * (hw * sw) + nf * (ht * sn))
            q[lay] = (sd, float(sw), float(sn))
            ring.append(q)
        rings.append(ring)
    new = []
    for i in range(n - 1):
        r0, r1 = rings[i], rings[i + 1]
        for k in range(4):
            new.append(bm.faces.new((r0[k], r0[(k + 1) % 4], r1[(k + 1) % 4], r1[k])))
    new.append(bm.faces.new(rings[0][::-1]))
    new.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return p.tag(new)


def build_strap(lod):
    p = P("strap", "strap")
    ribbon(p, strap_path(lod), L.STRAP_W / 2, L.STRAP_T / 2, "strapp")
    p.bm.normal_update()
    return p


def cord_path(lod):
    """Cap cord: from the hole in the post of the second lug along the side of the tube, over the ground to
    the cap, up its wall into the hole near the edge, a knot inside: [(point (u, v, z), section radii)]."""
    c1 = L.CLAMPS[1]
    cr = L.CORD_R
    post = L.LUG_L / 2
    one = (cr, cr)
    d = CORD_DIR
    x36, x15, x0 = (L.R * (math.radians(a) - L.LUG_THETA) for a in (36.0, 15.0, 0.0))
    pts = [
        (on_lug(c1, 0.0, L.CORD_HOLE_Y, post - 0.0022), one),        # in the post
        (on_lug(c1, 0.0, L.CORD_HOLE_Y, post + 0.0012), one),        # left the hole
        (on_lug(c1, -0.0032, 0.0017, post + 0.0048), one),
        (on_lug(c1, x36, cr + 0.0004, 0.0235), one),
        (on_lug(c1, x15, cr + 0.0004, 0.0305), one),
    ]
    # leaves the tube on the side and sags to the ground (a Bezier with long arms: it lies down gently,
    # without a kink - a sheer drop would break on the ground), runs smoothly over the ground to the cap,
    # bends up at the wall (bends of no more than ~35 degrees per point)
    p0 = Vector(on_lug(c1, x0, cr + 0.0006, 0.0350))
    t0 = (p0 - Vector(pts[-1][0])).normalized()
    gp = Vector((c1 + 0.068, 0.0585, cr))
    tg = Vector((1.0, 0.30, 0.0)).normalized()          # along the ground, in the same direction as it hung
    pts.append((tuple(p0), one))
    for t in (0.35, 0.65, 0.88):
        pts.append((tuple(bez(p0, p0 + t0 * 0.022, gp - tg * 0.030, gp, t)), one))
    pts.append((tuple(gp), one))
    w0 = Vector(cap_pt(L.CAP_R + cr + 0.0060, cr, d))
    dd = Vector((d.x, d.y, 0.0))
    for t in (1.0 / 3, 2.0 / 3):
        pts.append((tuple(bez(gp, gp + tg * 0.030, w0 + dd * 0.022, w0, t)), one))
    pts.append((tuple(w0), one))
    pts += [
        (cap_pt(L.CAP_R + cr + 0.0032, cr + 0.0005, d), one),         # bends up along the wall
        (cap_pt(L.CAP_R + cr + 0.0013, cr + 0.0022, d), one),
        (cap_pt(L.CAP_R + cr + 0.00035, 0.0065, d), one),
        (cap_pt(L.CAP_R + cr * 0.9, L.CAP_H - 0.0105, d), one),
        (cap_pt(L.CAP_R + cr * 0.2, L.CAP_H - 0.0078, d), one),       # enters the hole
        (cap_pt(L.CAP_RI - 0.0006, L.CAP_H - 0.0075, d), one),       # passed the wall
        (cap_pt(L.CAP_RI - 0.0026, L.CAP_H - 0.0078, d), (cr * 2.0, cr * 1.8)),     # knot
        (cap_pt(L.CAP_RI - 0.0044, L.CAP_H - 0.0083, d), (cr * 1.35, cr * 1.2)),
    ]
    if lod != 0:
        pts = [pts[i] for i in (0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 19)]
    return pts
# near-LOD points: 0 in the post, 1 out, 2 bend, 3-4 along the tube, 5 leaves, 6-8 sags, 9 ground, 10-11
# along the ground, 12 at the cap, 13-15 bends up, 16 along the wall, 17 hole, 18 inside, 19-20 knot


def build_cord(lod):
    p = P("cord", "cord")
    path = cord_path(lod)
    pts = [W(*q) for q, _ in path]
    sides = 5 if lod == 0 else 3
    bm = p.bm
    n0 = len(bm.verts)
    g.tube_var(p, pts, [r for _, r in path], sides)
    bm.verts.ensure_lookup_table()
    lay = bm.verts.layers.float_vector.new("cordp")
    acc = 0.0
    for i in range(len(pts)):
        if i:
            acc += (Vector(pts[i]) - Vector(pts[i - 1])).length
        for k in range(sides):
            a = 2 * math.pi * k / sides
            bm.verts[n0 + i * sides + k][lay] = (acc, math.cos(a), math.sin(a))
    p.bm.normal_update()
    return p


def build_lod(spec):
    lod = spec["lod"]
    tube = build_tube(lod)
    roll = build_roll(lod)
    parts = [tube, roll, build_dark(lod, BOUNDS["deep_ring"]), build_cap(lod), build_lugs(lod),
             build_label(lod), build_strap(lod), build_cord(lod)]
    g.triangulate(parts)
    if lod == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        BOUNDS["pts"] = [tuple(v) for v in vs]
    return parts


# from the bottom side, above and steeply: the tube fills the height of the 1x3 cell, the roll and the cap
# at the top
INV_VIEW = (-0.20, -0.03, 0.60)


def preview_aspect(bbox, cam):
    """Width / height of the preview frame from camera cam onto the centre (a 1x3 cell gives about 0.33)."""
    x0, x1, y0, y1, z0, z1 = bbox
    c = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    d = (c - Vector(cam)).normalized()
    right = d.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(d).normalized()
    pts = [Vector(q) - c for q in BOUNDS["pts"]]
    w = max(q.dot(right) for q in pts) - min(q.dot(right) for q in pts)
    h = max(q.dot(up) for q in pts) - min(q.dot(up) for q in pts)
    return w / h


def collision():
    """One convex hull over all points of the near LOD. The mass is the class weight (0.3 kg,
    OZL_Carrier_Base); a hit is plastic (as for vanilla plastic bottles)."""
    comps = [(BOUNDS["pts"], kx.PEN + r"\plastic.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    cz = hi[2] / 2
    memory = {
        "invView": [INV_VIEW],
        "ce_center": [(0.0, 0.0, cz)],
        "ce_radius": [(max(abs(lo[0]), abs(hi[0])), 0.0, cz)],
    }
    print("bbox %.4f..%.4f x %.4f..%.4f x %.4f..%.4f, preview aspect from invView %.2f (1x3 cell: ~0.33)"
          % (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2], preview_aspect(bbox, INV_VIEW)))
    return comps, 0.3, memory, bbox


TGT = (0.0, 0.0, 0.03)
# camera angles; the first five are the --look preview: general view, the roll, the cap with the cord,
# the lug with the strap threaded through, the bottom; then the strap, the top view, the inventory camera
LUG1 = W(*on_lug(L.CLAMPS[0], 0.0, 0.0))
SHOTS = [
    ("front", (0.02, -0.62, 0.36), TGT, 42),
    ("roll", (0.48, -0.16, 0.16), (0.24, -0.04, 0.045), 55),
    ("cap", (0.36, 0.34, 0.20), (0.17, 0.02, 0.03), 50),
    ("lug", (LUG1[0] + 0.07, LUG1[1] + 0.20, LUG1[2] + 0.13), (LUG1[0] + 0.004, LUG1[1] + 0.004, LUG1[2] - 0.012), 75),
    ("back", (-0.50, 0.30, 0.30), TGT, 42),
    ("strap", (-0.05, 0.42, 0.22), (-0.05, 0.0, 0.03), 45),
    ("top", (0.0, -0.01, 0.95), (0.0, 0.0, 0.0), 40),
    ("inv", INV_VIEW, TGT, 38),
]
M.look_shots = (5, 2)

if __name__ == "__main__":
    M.run(build_lod, collision, SHOTS, row_step=0.65, row_shot=((0.33, -1.1, 0.75), (0.33, 0.0, 0.0)))
