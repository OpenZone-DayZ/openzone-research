"""M63 - "Anomaly" carrier (OZL_Carrier_Anom): the carrier of the "Anomaly" line, shared by the factions -
a kraft envelope closed with a "button and string" tie, with a spectrogram on glossy photo paper
pulled halfway out of it. A portable 2x2 item.

    blender --background --python build_m63.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (the drawing of the back, the print,
the tag).

Target: a thick paper envelope with a spectrogram half pulled out - a snapshot of a spectrum on
glossy photo paper (a dark background, a light curve with peaks and a scale); ~18 x 24 x 1 cm; a
kraft envelope (camoGround) with a flap on a "button and string" tie, a 13 x 18 cm photo with a white
border, glossy material, a curve with 3-5 peaks, a scale of ticks without captions. Carriers:
200-400 g, 300-1000 triangles, texture 512-1024; the camoGround selection is what gets painted in the
line colour (the envelope); the paper has no readable text.

Reference and sizes:
- envelope: kraft "envelope with string" 7 x 10 inches, 18 x 25.4 cm (Goldkraft Envelope with String
  7 x 10 Inch; ~18 x 24 is the same class). As on "button and string" envelopes (Quality Park 10 x 13
  inter-departmental): open end - the flap on the short end, a hard fibre button with a stainless
  eyelet on the flap outside and on the back, a string no shorter than 9" (230 mm; a purchasing
  specification). The back has a glued bottom (30 mm, 45-degree corners) and a seam in the middle, and
  a finger notch in the mouth. The washer-button diameter is not given in the listings found - 25 mm
  from a photo (estimate); the flap is 45 mm (estimate). The European analogue is string & washer C5
  229 x 162 mm, 180 g/m2 (Blake SW624).
- print: 13 x 18 cm, the Soviet photo paper format (13 x 18 "Foton" paper, Kyiv, 1982; "Fotobrom"
  13 x 18, 1991; glossy 13 x 18 is ~225 g/m2 today). White border 6 mm (8 at the bottom), thickness
  0.3 mm. The frame shows a photo of a multichannel analyser screen (make_decals.py): a gamma spectrum
  on a logarithmic scale, five peaks and a narrow unknown line with a cursor, scale ticks without
  captions, a row of indicator digits; on the border in pencil the number "31-118" and a "?" with an
  arrow. Inside the envelope there are three more prints and a folded protocol - the back bulges over
  them (envelope thickness ~3 mm, ~4 mm with the button).
- pulled out halfway (90 of 180 mm) over the open flap: the flap lies flat beyond the mouth,
  outside-down, on the washer of its own button - the print above it is slightly raised and descends
  to the ground as a stiff sheet; rotated by 3.5 degrees, the edges curl towards the emulsion.
- string: cotton twine ~1.2 mm: comes out from under the washer on the back, a winding around it, the
  end on top, the free end over the edge onto the ground.
- tag 72 x 42 mm on the back: a yellow stripe (the "Anomaly" line, like the sample ring of M48),
  empty fields, a number in ballpoint digits, a violet stamp with a radiation sign.
- weight: a real envelope with four prints and a sheet is ~50 g; the class uses the shared carrier
  weight (300 g, OZL_Carrier_Base, within 200-400 g).

State is `used but intact`: the kraft is rubbed at the edges (light frayed fibres), dirt at the mouth
and along the edges, water stains, soft creases, the white border of the print has yellowed slightly.
There are no lamps, screens or moving parts, so there is no "work" view. No faction colour: the
envelope is the camoGround selection (all the kraft: back, flap, bottom, edges, mouth), its texture
is set by the config (hiddenSelectionsTextures; a procedural colour #(argb,8,8,3)color(...) recolours
the envelope evenly, the relief stays). LODs (a small item): near and middle (~40 %), no far one.

Detailing: "dayz" look - matte, dirtier, coloured AO; the kit wear layers (kmats.weather: dust, tonal
blotches, greasy hand spots, scuffs) are also used in the materials of the envelope, tag, back of the
print and twine (little dust: the envelope is carried in a bag); on the washer and eyelet only the
profile's colour muting (patina) and greasy spots: the kit layers on a 25 mm part laid a pink veil.
Round things have no facets: the LOD is smoothed only where adjacent faces meet at less than 40
degrees (kexport.visual_lod), so the washer has 24 sides with a bevel on the top edge, the eyelet is a
rolled rim with a dark hole (12 sides), the washer under the flap and its hump on the flap have 12 and
10; the twine lies on the paper and is visible from above, so it is built as the top half of the
section (5 sides along the arc, no bottom); it is wound on the eyelet shank under the washer and comes
out from under its edge (a winding outside the washer as an even ring read as a gasket), lies loose on
the back, in a hook, over the edge onto the ground in a smooth curve, with a knot and a frayed tip at
the end. The finger notch has 12 segments, the rounded flap corners 5 each. The corner at the glued
bottom is bent along a crease - the diagonal fold already drawn on the decal of the back (both walls,
11 degrees, the fibres are broken along the crease), the second bottom corner is worn, the tag corner
at the mouth has peeled off; the print emulsion has hairline scratches, dust specks and a crack at the
outer corner. There are no vanilla DayZ items on the envelope: it has no small parts with a vanilla
analogue.

Blender axes: X is along the envelope (the mouth and the print are at +X), Y is across, Z is up. The
origin is the middle of the length (envelope + pulled-out print), on the ground: autocenter = 0 (in
Geometry), boundingbox_min at the bottom, so a dropped envelope lies flat. The inventory camera
(invView) looks from the front, right and above: the print is closer, the envelope recedes.
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
import m63_layout as L  # noqa: E402
from mathutils import Vector  # noqa: E402
from mathutils.geometry import delaunay_2d_cdt  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

LOD_SPECS = [
    dict(lod=0),
    dict(lod=1),
]

REGIONS = {
    "back": ("kraft_back", 1.0),
    "flap_in": ("kraft_flap", 0.8),
    "env_bot": ("kraft_bot", 1.0),          # downward faces: the layout itself cuts their density by four
    "env_edge": ("kraft_edge", 0.6),
    "mouth": ("mouth", 0.6),
    "print_top": ("print_top", 1.7),
    "print_bot": ("print_back", 0.5),
    "print_edge": ("print_edge", 0.6),
    "label": ("label", 1.5),
    "label_edge": ("label_edge", 0.6),
    "washer": ("fiber", 1.4),
    "eyelet": ("eyelet", 1.2),
    "hole": ("hole", 0.6),
    "string": ("twine", 0.35),
}

# kraft is saturated enough to survive the "dayz" profile layers (tonal blotches towards white, dust,
# scuffs), which remove more saturation than its 12 % muting; otherwise it read as pinkish beige (S
# 0.32-0.35 against 0.42); with these colours the estimate is ~0.38
KRAFT = kmats.lin((172, 126, 76))
KRAFT_IN = kmats.lin((186, 142, 94))


def wdecal(name):
    return os.path.join(WORK, name)


def W(u, v, z):
    """Envelope point (u, v) and height -> Blender."""
    return (u - L.U0, v, z)


# --- materials ------------------------------------------------------------------------------------
def small(t, origin, seed, k=20.0):
    vec, sep = t.coords(origin, seed)
    return t.stretch(vec, k, k, k), sep


def wear(t, col, origin, seed, sep, dust, cav, k=5.0):
    """"dayz" profile layers of the kit (kmats.weather): dust on up-facing surfaces, dirt in corners, tonal
    blotches, greasy hand spots, small scuffs. The kit noises are tuned for machine-sized metres and the
    envelope is 25 cm, so the coordinates are k times finer; there is no "near the floor" dirt (floor_z is
    below the ground): the whole carrier lies on the ground. Returns (colour, dirt strength)."""
    vec, _ = t.coords(origin, seed)
    return kmats.weather(t, col, t.stretch(vec, k, k, k), sep, t.normal(), floor_z=-1.0, dust=dust, grime=0.0,
                         cav=cav)


def patina(t, col):
    """Only the colour muting of the "dayz" profile (kmats.LOOK["patina"]: desaturate by a fraction and
    darken) - for small parts: the kit's dust and scuffs on a 25 mm washer laid a pink veil."""
    d, v = kmats.LOOK.get("patina", (0.0, 1.0))
    gray = t.node("ShaderNodeRGBToBW")
    t.link(col, gray.inputs[0])
    col = t.mixc(d, col, gray.outputs[0])
    return t.mixc(1.0 - v, col, (0.0, 0.0, 0.0, 1.0))


def kraft_fibers(t, vec):
    """Kraft: large tonal blotches, fibres along the machine direction (X), dark specks."""
    blot = t.maprange(t.noise(vec, 0.9, 4.0, 0.55), 0.3, 0.75, 0.0, 1.0)
    fib = t.noise(t.stretch(vec, 0.18, 1.0, 1.0), 14.0, 6.0, 0.7)
    speck = t.step(t.noise(vec, 9.0, 3.0, 0.5), 0.74, 0.78)
    return blot, fib, speck


def env_overlay(t, sep):
    c, a = t.image(wdecal("env_top.png"), sep.outputs["X"], sep.outputs["Y"], (L.ENV_IMG_L / 2 - L.U0, 0.0),
                   (L.ENV_IMG_L, L.EW))
    _, ha = t.image(wdecal("env_top_h.png"), sep.outputs["X"], sep.outputs["Y"], (L.ENV_IMG_L / 2 - L.U0, 0.0),
                    (L.ENV_IMG_L, L.EW))
    return c, a, t.math("SUBTRACT", ha, 0.5)


def dog_crease(t, sep):
    """1 on the bend of the bent corner (a straight line in plan, the middle of the DOG_W strip), 0 further
    than ~1 mm away. The line crosses the envelope only near the corner: further in both directions it is
    beyond its edge."""
    (u0, v0), (nx, ny) = L.dog_line()
    d = t.math("ADD", t.math("MULTIPLY", t.math("SUBTRACT", sep.outputs["X"], u0 - L.U0), nx),
               t.math("MULTIPLY", t.math("SUBTRACT", sep.outputs["Y"], v0), ny))
    d = t.math("SUBTRACT", d, L.DOG_W / 2)
    return t.maprange(t.math("ABSOLUTE", d), 0.0003, 0.0013, 1.0, 0.0)


def mat_kraft(mat, origin, base, face="back", seed=1.0):
    """Kraft paper of the envelope: blotchy tone, fibres, specks; on the back and the flap, the decal
    (seams, creases, dirt, stains, worn edges); the shadow of the string, washer and tag is shading; along
    the bend of the bent corner, broken light fibres; on top, the "dayz" profile wear."""
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, seed)
    blot, fib, speck = kraft_fibers(t, vec)
    col = t.mixc(blot, tuple(c * 0.88 for c in base[:3]) + (1,), tuple(min(1.0, c * 1.08) for c in base[:3]) + (1,))
    col = t.mixc(t.math("MULTIPLY", t.maprange(fib, 0.35, 0.65, 0.0, 1.0), 0.22), col,
                 tuple(c * 0.80 for c in base[:3]) + (1,))
    col = t.mixc(t.math("MULTIPLY", speck, 0.7), col, kmats.lin((70, 50, 30)))
    h = t.math("ADD", t.math("MULTIPLY", fib, 0.06), t.math("MULTIPLY", blot, 0.04))
    if face in ("back", "flap"):
        c, a, hh = env_overlay(t, sep)
        col = t.mixc(a, col, c)
        h = t.math("ADD", h, t.math("MULTIPLY", hh, 1.4))
    if face == "bot":
        col = t.mixc(t.math("MULTIPLY", t.maprange(t.noise(vec, 3.0, 6.0, 0.6), 0.45, 0.75, 0.0, 1.0), 0.45),
                     col, kmats.lin((96, 84, 66)))
    if face == "edge":
        col = t.mixc(0.35, col, kmats.lin((120, 90, 58)))
    if face in ("back", "bot", "edge"):
        cr = dog_crease(t, sep)
        col = t.mixc(t.math("MULTIPLY", cr, 0.5), col, kmats.lin((204, 174, 130)))
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", cr, 0.6))
    cav = t.maprange(t.cavity(0.004), 0.08, 0.5, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.55), col, kmats.lin((40, 28, 16)))
    # little dust: the envelope is carried in a bag, not kept on a bench (with dust 0.12 the kraft greyed to
    # pink)
    col, dirt = wear(t, col, origin, seed + 0.37, sep, dust=0.03, cav=0.35)
    return kmats.out(t, col, t.math("SUBTRACT", 0.12, t.math("MULTIPLY", dirt, 0.05)), 0.06, h)


def mat_mouth(mat, origin):
    """Mouth from inside: a dark gap, the inner side of the kraft in shadow."""
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, 2.2)
    col = t.mixc(t.maprange(t.noise(vec, 3.0, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0), kmats.lin((26, 19, 12)),
                 kmats.lin((44, 32, 20)))
    return kmats.out(t, col, 0.05, 0.02, 0.0)


def paper_attr(t, name):
    attr = t.node("ShaderNodeAttribute")
    attr.attribute_type = "GEOMETRY"
    attr.attribute_name = name
    sep = t.node("ShaderNodeSeparateXYZ")
    t.link(attr.outputs["Vector"], sep.inputs[0])
    return sep.outputs["X"], sep.outputs["Y"]


def hairlines(t, a, b, deg, scale, thr, mask_scale, seed):
    """Hairline scratches over the sheet: thin strokes along direction deg in sheet coordinates (a, b), in
    patches (a mask)."""
    r = math.radians(deg)
    ca, sa = math.cos(r), math.sin(r)
    pa = t.math("ADD", t.math("MULTIPLY", a, ca), t.math("MULTIPLY", b, sa))
    pb = t.math("SUBTRACT", t.math("MULTIPLY", b, ca), t.math("MULTIPLY", a, sa))
    comb = t.node("ShaderNodeCombineXYZ")
    t.link(pa, comb.inputs[0])
    t.link(pb, comb.inputs[1])
    comb.inputs[2].default_value = seed
    lines = t.step(t.noise(t.stretch(comb.outputs[0], 0.02, 1.0, 1.0), scale, 2.0, 0.5), thr, thr + 0.014)
    mask = t.maprange(t.noise(comb.outputs[0], mask_scale, 3.0, 0.5), 0.48, 0.70, 0.0, 1.0)
    return t.math("MULTIPLY", lines, mask)


def mat_print(mat, origin):
    """Print emulsion: the picture by sheet coordinates (s, t), glossy. An old print: slightly yellowed and
    dulled, smeared fingerprints kill the gloss, hairline scratches and dust specks on the emulsion are
    lighter than the black screen, and at the outer corner there is an emulsion crack down to the white
    base (the corner was once bent). No kit tonal blotches here: they would blur the frame."""
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, 3.3, 30.0)
    s, tt = paper_attr(t, "paper")
    col, _ = t.image(wdecal("print.png"), s, tt, (L.PRINT_L / 2, L.PRINT_W / 2), (L.PRINT_L, L.PRINT_W))
    gray = t.node("ShaderNodeRGBToBW")
    t.link(col, gray.inputs[0])
    col = t.mixc(0.10, col, gray.outputs[0])
    col = t.mixc(0.06, col, kmats.lin((150, 128, 84)))
    smudge = t.maprange(t.noise(vec, 1.6, 5.0, 0.6), 0.60, 0.74, 0.0, 1.0)
    # scratches: along the sheet, diagonal and a few across
    sc = t.math("MAXIMUM", hairlines(t, s, tt, 4.0, 700.0, 0.72, 25.0, 0.3),
                hairlines(t, s, tt, 38.0, 650.0, 0.73, 22.0, 1.7))
    sc = t.math("MAXIMUM", sc, t.math("MULTIPLY", hairlines(t, s, tt, -71.0, 600.0, 0.74, 18.0, 2.9), 0.7))
    col = t.mixc(t.math("MULTIPLY", sc, 0.55), col, kmats.lin((118, 116, 112)))
    dust = t.step(t.noise(vec, 140.0, 2.0, 0.5), 0.80, 0.83)
    col = t.mixc(t.math("MULTIPLY", dust, 0.5), col, kmats.lin((150, 146, 136)))
    # the corner that was once bent: along the fold, a light matte strip and a dashed emulsion crack (from
    # the bottom edge towards the outer one, ~28 mm; a solid 38 mm one read as a thread, and a 21 mm one
    # lay almost wholly on the white border and was invisible)
    s0, t0, s1, t1 = L.PRINT_L - 0.022, 0.0, L.PRINT_L, 0.017
    ln = math.hypot(s1 - s0, t1 - t0)
    nx, ny = -(t1 - t0) / ln, (s1 - s0) / ln
    d = t.math("ADD", t.math("MULTIPLY", t.math("SUBTRACT", s, s0), nx), t.math("MULTIPLY", t.math("SUBTRACT", tt, t0), ny))
    jit = t.math("MULTIPLY", t.math("SUBTRACT", t.noise(vec, 9.0, 4.0, 0.6), 0.5), 0.0012)
    gaps = t.step(t.noise(vec, 26.0, 2.0, 0.5), 0.40, 0.47)
    crack = t.math("MULTIPLY", t.maprange(t.math("ABSOLUTE", t.math("ADD", d, jit)), 0.0001, 0.00028, 1.0, 0.0), gaps)
    bend = t.maprange(t.math("ABSOLUTE", d), 0.0006, 0.0026, 1.0, 0.0)
    col = t.mixc(t.math("MULTIPLY", bend, 0.10), col, kmats.lin((160, 156, 148)))
    col = t.mixc(t.math("MULTIPLY", crack, 0.75), col, kmats.lin((214, 208, 194)))
    gl = t.math("SUBTRACT", 0.80, t.math("ADD", t.math("ADD", t.math("MULTIPLY", smudge, 0.40), t.math("MULTIPLY", sc, 0.25)),
                                         t.math("MULTIPLY", bend, 0.30)))
    sp = t.math("SUBTRACT", 0.60, t.math("MULTIPLY", smudge, 0.30))
    h = t.math("SUBTRACT", t.math("MULTIPLY", smudge, 0.04), t.math("ADD", t.math("MULTIPLY", sc, 0.10),
                                                                     t.math("MULTIPLY", crack, 0.5)))
    return kmats.out(t, col, gl, sp, h)


def mat_flatpaper(mat, origin, color, seed=4.0, gloss=0.12, spec=0.06):
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, seed, 30.0)
    col = t.mixc(t.maprange(t.noise(vec, 2.0, 5.0, 0.6), 0.3, 0.75, 0.0, 1.0),
                 tuple(c * 0.92 for c in color[:3]) + (1,), color)
    cav = t.maprange(t.cavity(0.003), 0.1, 0.5, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.4), col, kmats.lin((90, 84, 70)))
    col, dirt = wear(t, col, origin, seed + 0.41, sep, dust=0.05, cav=0.3)
    return kmats.out(t, col, gloss, spec, t.math("MULTIPLY", t.noise(vec, 12.0, 3.0, 0.5), 0.05))


def mat_label(mat, origin):
    """Tag: the picture by tag coordinates, matte paper, a shadow along the edge and at the seam; the tag is
    thumbed - the "dayz" profile wear."""
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, 5.1, 30.0)
    a, b = paper_attr(t, "lbl")
    col, _ = t.image(wdecal("label.png"), a, b, (0.0, 0.0), L.LABEL_SIZE)
    cav = t.maprange(t.cavity(0.003), 0.1, 0.5, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.4), col, kmats.lin((80, 70, 54)))
    col, dirt = wear(t, col, origin, 5.5, sep, dust=0.05, cav=0.3)
    return kmats.out(t, col, 0.10, 0.05, t.math("MULTIPLY", t.noise(vec, 14.0, 3.0, 0.5), 0.05))


def mat_fiber(mat, origin):
    """Washer button of hard red fibre: dark red, blotchy, rubbed lighter along the edge, the top is thumbed
    (the washer is turned to wind the string) - dark greasy spots; the colour is muted per the "dayz"
    profile (patina)."""
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, 6.4, 40.0)
    base = kmats.lin((122, 42, 32))
    col = t.mixc(t.maprange(t.noise(vec, 1.2, 6.0, 0.6), 0.3, 0.75, 0.0, 1.0), tuple(c * 0.70 for c in base[:3]) + (1,),
                 base)
    swirl = t.maprange(t.noise(t.stretch(vec, 1.0, 0.3, 1.0), 6.0, 8.0, 0.7), 0.4, 0.7, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", swirl, 0.35), col, kmats.lin((150, 64, 48)))
    col = t.mixc(t.math("MULTIPLY", t.step(t.noise(vec, 9.0, 3.0, 0.5), 0.7, 0.75), 0.6), col, kmats.lin((60, 22, 16)))
    edge = t.maprange(t.edge_wear(0.0005), 0.05, 0.3, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.45), col, kmats.lin((150, 84, 66)))
    grease = t.maprange(t.noise(vec, 2.4, 5.0, 0.6), 0.55, 0.72, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", grease, 0.35), col, kmats.lin((50, 20, 15)))
    cav = t.maprange(t.cavity(0.002), 0.1, 0.5, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.5), col, kmats.lin((30, 14, 10)))
    col = patina(t, col)
    gl = t.math("ADD", 0.22, t.math("MULTIPLY", grease, 0.10))
    return kmats.out(t, col, gl, 0.18, t.math("MULTIPLY", t.noise(vec, 20.0, 3.0, 0.5), 0.06))


def mat_eyelet(mat, origin):
    """Eyelet: stainless steel, dull, with dark patches and dirt in the rolled rim (the bare steel of the
    "dayz" profile is darker, like a vanilla tool)."""
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, 7.7, 40.0)
    col = t.mixc(t.maprange(t.noise(vec, 4.0, 6.0, 0.6), 0.35, 0.75, 0.0, 1.0), kmats.lin((72, 72, 68)),
                 kmats.lin((122, 120, 114)))
    cav = t.maprange(t.cavity(0.0015), 0.1, 0.5, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.6), col, kmats.lin((34, 30, 26)))
    col = patina(t, col)
    return kmats.out(t, col, t.math("SUBTRACT", 0.45, t.math("MULTIPLY", cav, 0.2)), 0.50, 0.0)


def mat_hole(mat, origin):
    """Eyelet hole: darkness, with the dirty kraft of the back at the bottom."""
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, 8.0, 40.0)
    col = t.mixc(t.maprange(t.noise(vec, 3.0, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0), kmats.lin((16, 12, 9)),
                 kmats.lin((36, 26, 16)))
    return kmats.out(t, col, 0.05, 0.02, 0.0)


def mat_twine(mat, origin):
    """Cotton twine: greyish beige, thumbed, dusty."""
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, 8.2, 30.0)
    col = t.mixc(t.maprange(t.noise(vec, 3.0, 5.0, 0.6), 0.3, 0.75, 0.0, 1.0), kmats.lin((150, 140, 116)),
                 kmats.lin((196, 186, 160)))
    cav = t.maprange(t.cavity(0.002), 0.1, 0.5, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.4), col, kmats.lin((70, 62, 48)))
    col, dirt = wear(t, col, origin, 8.6, sep, dust=0.06, cav=0.4, k=8.0)
    return kmats.out(t, col, 0.05, 0.03, t.math("MULTIPLY", t.noise(vec, 30.0, 3.0, 0.5), 0.1))


KINDS = {
    "kraft_back": (mat_kraft, dict(base=KRAFT, face="back")),
    "kraft_flap": (mat_kraft, dict(base=KRAFT_IN, face="flap", seed=1.4)),
    "kraft_bot": (mat_kraft, dict(base=KRAFT, face="bot", seed=1.8)),
    "kraft_edge": (mat_kraft, dict(base=KRAFT, face="edge", seed=2.0)),
    "mouth": (mat_mouth, {}),
    "print_top": (mat_print, {}),
    "print_back": (mat_flatpaper, dict(color=kmats.lin((230, 226, 214)))),
    "print_edge": (mat_flatpaper, dict(color=kmats.lin((214, 210, 198)), seed=4.4)),
    "label": (mat_label, {}),
    "label_edge": (mat_flatpaper, dict(color=kmats.lin((206, 198, 176)), seed=5.5)),
    "fiber": (mat_fiber, {}),
    "eyelet": (mat_eyelet, {}),
    "hole": (mat_hole, {}),
    "twine": (mat_twine, {}),
}

OBJ, NAME = "m63_carrier_anom", "ozr_carrier_anom"
# "dayz" look: the rvmat comes from the profile (specular 1.0; kbake recomputes the highlight and the gloss
# of _smdi)
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=("camoGround",), hidden=("camoGround",))
P = M.part
BOUNDS = {}


# --- geometry -------------------------------------------------------------------------------------
def cdt(outline, inner, chains=()):
    """Delaunay triangulation: an outline (counter-clockwise) + interior points + constraint polylines
    (creases: their points come from the outline or from inner) -> (points, counter-clockwise triangles)."""
    pts = [Vector((x, y)) for x, y in list(outline) + list(inner)]
    n = len(outline)
    edges = [(i, (i + 1) % n) for i in range(n)]

    def idx(q):
        for i, p in enumerate(pts):
            if abs(p.x - q[0]) < 1e-7 and abs(p.y - q[1]) < 1e-7:
                return i
        raise KeyError("chain point %s not in outline or inner" % (q,))
    for ch in chains:
        ids = [idx(q) for q in ch]
        edges += list(zip(ids, ids[1:]))
    vs, _, fs, _, _, _ = delaunay_2d_cdt(pts, edges, [], 0, 1e-7)
    assert len(vs) == len(pts), "CDT added points (%d -> %d)" % (len(pts), len(vs))
    tris = []
    for f in fs:
        cx = sum(vs[i].x for i in f) / 3
        cy = sum(vs[i].y for i in f) / 3
        if not L.inside(outline, cx, cy):
            continue
        a, b, c = (vs[i] for i in f)
        if (b - a).cross(c - a) < 0:
            f = (f[0], f[2], f[1])
        tris.append(tuple(f))
    return [(v.x, v.y) for v in vs], tris


def surface(p, region, pts, tris, zf, up=True):
    p.use(region, *REGIONS[region])
    bv = [p.bm.verts.new(W(u, v, zf(u, v))) for u, v in pts]
    faces = [p.bm.faces.new((bv[a], bv[b], bv[c]) if up else (bv[a], bv[c], bv[b])) for a, b, c in tris]
    p.tag(faces)
    return bv


def strip(p, region, top, bot, want):
    """Strip of quads between the point rows top and bot (Blender); want(i) is where it should face."""
    p.use(region, *REGIONS[region])
    tv = [p.bm.verts.new(q) for q in top]
    bv = [p.bm.verts.new(q) for q in bot]
    faces = []
    for i in range(len(top) - 1):
        f = p.bm.faces.new((tv[i], tv[i + 1], bv[i + 1], bv[i]))
        f.normal_update()
        if f.normal.dot(Vector(want(i))) < 0:
            f.normal_flip()
        faces.append(f)
    p.tag(faces)
    return faces


def grid_inside(poly, us, vs, margin):
    out = []
    for u in us:
        for v in vs:
            if L.inside(poly, u, v) and L.edge_dist(poly, u, v) > margin:
                out.append((u, v))
    return out


def outward_dir(poly, i):
    """Outward normal of the (counter-clockwise) outline on the segment i -> i+1."""
    (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % len(poly)]
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy)
    return (dy / ln, -dx / ln, 0.0)


def flap_rings(lod):
    """Flap points around the washer of its button - the same for the top and the bottom of the flap,
    otherwise the bottom, triangulated differently, would show through the top. Two rings: the washer
    edge and the end of the sag."""
    if lod != 0:
        return []
    bu, bv = L.BTN_FLAP
    n = L.FLAP_RING
    return [(bu + r * math.cos(2 * math.pi * k / n + 0.3), bv + r * math.sin(2 * math.pi * k / n + 0.3))
            for r in (L.WASHER_R - 0.001, L.WASHER_R + L.FLAP_SAG - 0.001) for k in range(n)]


def build_envelope(lod):
    """Envelope (camoGround): the back with a notch in the mouth, the flap from inside, the bottom, edges,
    mouth. The bent corner (m63_layout.dog_*) lifts both walls and the edges; the crease and the end of
    the bend are constraint edges of the triangulation of the back and the bottom."""
    p = P("env", "back", group="camoGround")
    tip_seg = 2 if lod == 0 else 1
    folds = L.dog_folds()
    mids = [f[1] for f in folds]
    # back
    back = L.back_outline(L.NOTCH_SEG[lod], tip_seg)
    if lod == 0:
        inner = grid_inside(back, (0.016, 0.046, 0.080, 0.114, 0.148, 0.178, 0.204),
                            (-0.075, -0.052, -0.026, 0.0, 0.026, 0.052, 0.075), 0.006)
        inner += grid_inside(back, (0.226, 0.243), (-0.080, -0.040, -0.014, 0.014, 0.040), 0.004)
        edge_s = (L.S_IN - 0.006, L.S_IN + 0.003, L.S_MOUTH - 0.009, L.S_MOUTH - 0.003)
        edge_t = (-0.0012, -0.007, L.PRINT_W + 0.0012, L.PRINT_W + 0.007)
    else:
        inner = grid_inside(back, (0.030, 0.090, 0.150, 0.205), (-0.060, -0.020, 0.020, 0.060), 0.008)
        edge_s = (L.S_IN + 0.002, L.S_MOUTH - 0.005)
        edge_t = (-0.0015, L.PRINT_W / 2, L.PRINT_W + 0.0015)
    # the back rests on the pulled-out print: points along its edges, otherwise the sparse mesh of the back
    # passes below the edge and the edge sticks through the paper
    for s in edge_s:
        for t in edge_t:
            q = L.print_uv(s, t)
            if L.inside(back, *q) and L.edge_dist(back, *q) > 0.002:
                inner.append(q)
    # the bent corner is flat: no mesh points are needed inside it or at the bend
    inner = [q for q in inner if L.dog_d(*q) < -0.002] + mids
    pts, tris = cdt(back, inner, folds)
    surface(p, "back", pts, tris, L.back_top)
    # flap from inside: the flap outline and the hinge along the mouth (without the notch)
    fo = L.flap_outline(L.FLAP_SEG[lod], 0.012) if lod == 0 else L.flap_outline(L.FLAP_SEG[lod])
    hinge = [(L.EL, v) for v in (0.066, 0.040, 0.012, -0.012, -0.040, -0.066)]
    if lod != 0:
        hinge = [(L.EL, v) for v in (0.040, -0.040)]
    flap = fo + hinge
    bu, bv = L.BTN_FLAP
    finner = flap_rings(lod) + [(bu, bv)]
    fpts, ftris = cdt(flap, finner)
    surface(p, "flap_in", fpts, ftris, L.flap_top)
    # bottom: the front wall on the ground (raised with the back at the bent corner) and the flap from below
    tip = L.dog_points(tip_seg)
    bottom = (tip[2:] + [(u, -L.HW) for u in (0.068, 0.128, 0.192)] + fo[:-1] +
              [(u, L.HW) for u in (L.EL, 0.192, 0.128, 0.068)] + L.corner_points(tip_seg) + [(0.0, 0.0)] + tip[:2])
    bin_ = grid_inside(bottom, (0.07, 0.15, 0.22), (-0.045, 0.045), 0.01) + finner + mids

    def zbot(u, v):
        return L.flap_bottom(u, v) if u > L.EL + 1e-6 else L.dog_lift(u, v)
    bpts, btris = cdt(bottom, bin_, folds)
    surface(p, "env_bot", bpts, btris, zbot, up=False)
    # edges of the back (bottom, sides): from the top of the back to the bottom of the front wall, along the
    # outline of the back without the mouth
    n = len(back)
    for i in range(n):
        a, b = back[i], back[(i + 1) % n]
        if a[0] >= L.EL - 1e-6 and b[0] >= L.EL - 1e-6:
            continue                    # the mouth is handled separately
        if (a[0] > L.EL - L.NOTCH_R - 1e-6 and abs(a[1]) < L.NOTCH_R + 1e-6) or \
                (b[0] > L.EL - L.NOTCH_R - 1e-6 and abs(b[1]) < L.NOTCH_R + 1e-6):
            continue
        d = outward_dir(back, i)
        strip(p, "env_edge", [W(*a, L.back_top(*a)), W(*b, L.back_top(*b))],
              [W(*a, L.dog_lift(*a)), W(*b, L.dog_lift(*b))], lambda k, d=d: d)
    # flap edge: from the top of the flap to the bottom
    for i in range(len(fo) - 1):
        a, b = fo[i], fo[i + 1]
        d = outward_dir(flap, i)
        strip(p, "env_edge", [W(*a, L.flap_top(*a)), W(*b, L.flap_top(*b))],
              [W(*a, L.flap_bottom(*a)), W(*b, L.flap_bottom(*b))], lambda k, d=d: d)
    # mouth: the cut edge of the back (light, as thick as the paper) and a dark gap under it down to the
    # front wall
    mouth = [q for q in back if q[0] > L.EL - L.NOTCH_R - 1e-6 and (q[0] >= L.EL - 1e-6 or abs(q[1]) <= L.NOTCH_R + 1e-6)]
    mouth.sort(key=lambda q: q[1])

    def want(k):
        a, b = mouth[k], mouth[k + 1]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        return (dy / ln, -dx / ln, 0.0)
    top = [W(u, v, L.back_top(u, v)) for u, v in mouth]
    bot = [W(u, v, L.PAPER) for u, v in mouth]
    # want() is the normal to the right of the walk (v grows): out of the mouth, towards +u. A single strip:
    # the light cut edge of the back (0.15 mm) as a separate strip degenerated at the sides of the mouth,
    # and Check_All found degenerate faces
    strip(p, "mouth", top, bot, want)
    p.bm.normal_update()
    return p


def build_print(lod):
    """Print: a 0.3 mm sheet, the top is the emulsion with the picture (attribute paper = (s, t)), the
    bottom, edges."""
    p = P("print", "print_top")
    lay = p.bm.verts.layers.float_vector.new("paper")
    sm = L.S_MOUTH
    if lod == 0:
        ss = [L.S_IN, sm - 0.012, sm, sm + 0.011, sm + 0.0225, sm + 0.034, sm + 0.050, sm + 0.070, L.PRINT_L]
        ts = [0.0, 0.0325, 0.065, 0.0975, L.PRINT_W]
        tb = [0.0, 0.065, L.PRINT_W]
    else:
        ss = [L.S_IN, sm, sm + 0.0225, sm + 0.050, L.PRINT_L]
        ts = [0.0, 0.065, L.PRINT_W]
        tb = ts

    def vert(s, t, z):
        u, v = L.print_uv(s, t)
        q = p.bm.verts.new(W(u, v, z))
        q[lay] = (s, t, 0.0)
        return q

    def sheet(region, tlist, zf, up):
        p.use(region, *REGIONS[region])
        grid = [[vert(s, t, zf(s, t)) for t in tlist] for s in ss]
        faces = []
        for i in range(len(ss) - 1):
            for j in range(len(tlist) - 1):
                q = [grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]]
                faces.append(p.bm.faces.new(q if up else q[::-1]))
        p.tag(faces)
        return grid
    sheet("print_top", ts, L.print_top, True)
    sheet("print_bot", tb, L.print_bottom, False)
    # edges: the long sides and the outer end (the inner end is inside the envelope)
    p.use("print_edge", *REGIONS["print_edge"])
    faces = []

    def edge_quad(s0, t0, s1, t1, want):
        a = vert(s0, t0, L.print_top(s0, t0))
        b = vert(s1, t1, L.print_top(s1, t1))
        c = vert(s1, t1, L.print_bottom(s1, t1) - 0.00002)
        d = vert(s0, t0, L.print_bottom(s0, t0) - 0.00002)
        f = p.bm.faces.new((a, b, c, d))
        f.normal_update()
        if f.normal.dot(Vector(want)) < 0:
            f.normal_flip()
        faces.append(f)
    c, sn = math.cos(L.PRINT_ROT), math.sin(L.PRINT_ROT)
    for i in range(len(ss) - 1):
        edge_quad(ss[i], 0.0, ss[i + 1], 0.0, (sn, -c, 0.0))
        edge_quad(ss[i], L.PRINT_W, ss[i + 1], L.PRINT_W, (-sn, c, 0.0))
    for j in range(len(ts) - 1):
        edge_quad(L.PRINT_L, ts[j], L.PRINT_L, ts[j + 1], (c, sn, 0.0))
    p.tag(faces)
    p.bm.normal_update()
    return p


def build_label(lod):
    """Tag on the back: a 0.2 mm sheet following the shape of the back, attribute lbl = (a, b) gives
    coordinates on the tag. In the near LOD the corner at the mouth (a = +hw, b = -hh) has peeled off:
    the corner cell is two triangles folded along the diagonal, the corner is lifted, the back of the tag
    shows under it, the corner edges are as thick as the sheet."""
    p = P("label", "label")
    lay = p.bm.verts.layers.float_vector.new("lbl")
    hw, hh = L.LABEL_SIZE[0] / 2, L.LABEL_SIZE[1] / 2
    peel = lod == 0
    if peel:
        As = [-hw, -hw / 3, hw / 3, hw - L.PEEL_A, hw]
        Bs = [-hh, -hh + L.PEEL_B, 0.0, hh]
    else:
        As = [-hw, 0.0, hw]
        Bs = [-hh, 0.0, hh]
    z_under = 0.00004                     # back of the tag above the kraft

    def lift(a, b):
        return L.label_peel(a, b) if peel else 0.0

    def vert(a, b, dz):
        u, v = L.label_uv(a, b)
        q = p.bm.verts.new(W(u, v, L.back_top(u, v) + lift(a, b) + dz))
        q[lay] = (a, b, 0.0)
        return q
    top = [[vert(a, b, z_under + L.LABEL_T) for b in Bs] for a in As]
    faces = []
    ci = len(As) - 2 if peel else -1       # cell of the peeled corner: (ci, 0)
    for i in range(len(As) - 1):
        for j in range(len(Bs) - 1):
            A, B, C, D = top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1]
            if i == ci and j == 0:
                faces += [p.bm.faces.new((A, B, C)), p.bm.faces.new((A, C, D))]
            else:
                faces.append(p.bm.faces.new((A, B, C, D)))
    p.tag(faces)
    p.use("label_edge", *REGIONS["label_edge"])
    if peel:
        # back of the lifted corner
        a0, b1 = As[ci], Bs[1]
        q = [vert(a0, -hh, z_under), vert(hw, -hh, z_under), vert(hw, b1, z_under)]
        f = p.bm.faces.new((q[0], q[2], q[1]))
        f.normal_update()
        if f.normal.z > 0:
            f.normal_flip()
        p.tag([f])
    ring = [(a, -hh) for a in As] + [(hw, b) for b in Bs[1:]] + [(a, hh) for a in As[-2::-1]] + [(-hw, b) for b in Bs[-2:0:-1]]
    faces = []
    for i in range(len(ring)):
        (a0, b0), (a1, b1) = ring[i], ring[(i + 1) % len(ring)]
        # bottom of the edge: under the glued part, slightly into the kraft; at the lifted corner, the back
        # of the sheet
        lo0 = z_under if lift(a0, b0) > 0 else -0.0001
        lo1 = z_under if lift(a1, b1) > 0 else -0.0001
        q = [vert(a0, b0, z_under + L.LABEL_T), vert(a1, b1, z_under + L.LABEL_T), vert(a1, b1, lo1), vert(a0, b0, lo0)]
        f = p.bm.faces.new(q)
        f.normal_update()
        mid_a, mid_b = (a0 + a1) / 2, (b0 + b1) / 2
        u0, v0 = L.label_uv(0, 0)
        u1, v1 = L.label_uv(mid_a, mid_b)
        if f.normal.dot(Vector((u1 - u0, v1 - v0, 0.0))) < 0:
            f.normal_flip()
        faces.append(f)
    p.tag(faces)
    p.bm.normal_update()
    return p


def washer_base(cu, cv):
    """Height under the washer: at the highest point of the back under it."""
    return max([L.back_top(cu, cv)] + [L.back_top(cu + L.WASHER_R * math.cos(2 * math.pi * k / 8),
                                                   cv + L.WASHER_R * math.sin(2 * math.pi * k / 8)) for k in range(8)])


def lathe(p, center, prof, sides, regions, cap_top=None, cap_bottom=None, rot=0.0):
    """Solid of revolution about the vertical through center (Blender x, y): the profile [(r, z), ...] is
    counter-clockwise (from the bottom outside, up, inwards), so faces point outwards; regions[i] is the
    region of segment i; cap_top / cap_bottom is the region of the cap at the last / first profile point
    (None means no cap)."""
    bm = p.bm
    cx, cy = center
    rings = [[bm.verts.new((cx + r * math.cos(rot + 2 * math.pi * k / sides),
                            cy + r * math.sin(rot + 2 * math.pi * k / sides), z)) for k in range(sides)]
             for r, z in prof]
    for i in range(len(prof) - 1):
        p.use(regions[i], *REGIONS[regions[i]])
        fs = []
        for k in range(sides):
            j = (k + 1) % sides
            fs.append(bm.faces.new((rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k])))
        p.tag(fs)
    if cap_top:
        p.use(cap_top, *REGIONS[cap_top])
        p.tag([bm.faces.new(rings[-1])])
    if cap_bottom:
        p.use(cap_bottom, *REGIONS[cap_bottom])
        p.tag([bm.faces.new(rings[0][::-1])])


def build_buttons(lod):
    """Button on the back: a fibre washer on the eyelet shank (the string runs under it) and an eyelet; the
    washer under the open flap. Near LOD: the washer has 24 sides with a bevel on top (faces meet at 15
    degrees and get smoothed), the eyelet is a rolled rim, an inner wall and a dark hole."""
    parts = []
    p = P("button", "washer")
    cu, cv = L.BTN_BODY
    c = W(cu, cv, 0.0)[:2]
    z0 = washer_base(cu, cv) + L.WASHER_LIFT
    z1 = z0 + L.WASHER_T
    if lod == 0:
        R, bev = L.WASHER_R, L.WASHER_BEV
        lathe(p, c, [(R, z0), (R, z1 - bev), (R - bev, z1)], 24, ["washer", "washer"], cap_top="washer",
              cap_bottom="washer")
        ro, ri, eh = L.EYE_RO, L.EYE_RI, L.EYE_H
        prof = [(ro, z1 - 0.00005), (ro - 0.0004, z1 + eh - 0.00012), (ri + 0.00035, z1 + eh),
                (ri, z1 + eh - 0.0004), (ri, z1 + 0.00005)]
        lathe(p, c, prof, 12, ["eyelet"] * 4, cap_top="hole", rot=math.pi / 12)
    else:
        g.cyl(p, Vector(W(cu, cv, z0 + L.WASHER_T / 2)), "z", L.WASHER_R, L.WASHER_T, 12)
        p.use("eyelet", *REGIONS["eyelet"])
        zb = L.back_top(cu, cv) - 0.0002
        zt = z1 + L.EYE_H
        g.cyl(p, Vector(W(cu, cv, (zb + zt) / 2)), "z", L.EYE_R, zt - zb, 8, r2=L.EYE_R * 0.75)
    p.bm.normal_update()
    parts.append(p)
    if lod == 0:
        q = P("button_flap", "washer")
        bu, bv = L.BTN_FLAP
        g.cyl(q, Vector(W(bu, bv, L.WASHER_T / 2 - 0.00002)), "z", L.WASHER_R, L.WASHER_T - 0.00004, 12)
        q.bm.normal_update()
        parts.append(q)
    return parts


def catmull(pts, subs):
    """Smooth a polyline (u, v, lift) with Catmull-Rom: subs is the points per segment (a number or a
    per-segment list: straight runs less often, bends more often)."""
    out = []
    n = len(pts)
    for i in range(n - 1):
        sub = subs if isinstance(subs, int) else subs[i]
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, n - 1)]
        for k in range(sub):
            t = k / sub
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 +
                                    (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(3)))
    out.append(pts[-1])
    return out


def half_tube(p, pts, radii, n_arc):
    """Twine lying on paper and on the ground: the top half of an elliptical section (n_arc faces along the
    arc from one side over the top to the other), no bottom - it rests on the support and is not visible.
    radii[i] = (half-width, height). The section frame is as in kgeo.tube_var: a sideways (t x Z), b up;
    the rings do not twist. Faces look away from the axis, the end caps run along the rod."""
    bm = p.bm
    pts = [Vector(q) for q in pts]
    n = len(pts)
    rings, a_prev = [], None
    for i in range(n):
        if 0 < i < n - 1:
            t = (pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized()
        else:
            t = (pts[1] - pts[0]) if i == 0 else (pts[-1] - pts[-2])
        t.normalize()
        a = t.cross(Vector((0, 0, 1)))
        if a.length < 0.15:
            a = a_prev.copy() if a_prev is not None else Vector((1, 0, 0))
            a -= t * a.dot(t)
        a.normalize()
        if a_prev is not None and a.dot(a_prev) < 0:
            a = -a
        a_prev = a
        b = a.cross(t).normalized()
        rx, rz = radii[i]
        rings.append([bm.verts.new(pts[i] + a * (rx * math.cos(math.pi * k / n_arc)) +
                                   b * (rz * math.sin(math.pi * k / n_arc))) for k in range(n_arc + 1)])
    faces = []
    for i in range(n - 1):
        axis = (pts[i] + pts[i + 1]) / 2
        for k in range(n_arc):
            f = bm.faces.new((rings[i][k], rings[i][k + 1], rings[i + 1][k + 1], rings[i + 1][k]))
            f.normal_update()
            if f.normal.dot(f.calc_center_median() - axis) < 0:
                f.normal_flip()
            faces.append(f)
    for ring, tdir in ((rings[0], pts[0] - pts[1]), (rings[-1], pts[-1] - pts[-2])):
        f = bm.faces.new(ring)
        f.normal_update()
        if f.normal.dot(tdir) < 0:
            f.normal_flip()
        faces.append(f)
    p.tag(faces)
    return faces


def build_string(lod):
    """Twine: wound under the washer, comes out from under its edge, lies loose on the back, over the edge
    onto the ground in a smooth curve (m63_layout.string_path); a knot and a frayed tip at the end."""
    p = P("string", "string")
    raw, subs = L.string_path(lod)
    pts = catmull([(u, v, 0.0 if lift is None else lift) for u, v, lift in raw], subs)
    out = []
    for u, v, lift in pts:
        if u <= L.EL and abs(v) <= L.HW:
            base = L.back_top(u, v)
        elif abs(v) <= L.HW + 0.0015:
            base = L.T0 * (1.0 - (abs(v) - L.HW) / 0.0015)          # goes over the edge
        else:
            base = 0.0
        out.append(Vector(W(u, v, base + L.STRING_Z0 + lift)))
    R, H = L.STRING_R, L.STRING_H
    radii = [(R, H)] * len(out)
    # a knot at the end (a plain one, ~3 mm) and a frayed tip beyond it, along the direction of the tail on
    # the ground
    d = (out[-1] - out[-2])
    d.z = 0.0
    d.normalize()
    if lod == 0:
        ext = [(0.0010, (R * 1.55, H * 1.45)), (0.0024, (R * 1.65, H * 1.5)), (0.0034, (R * 1.1, H * 1.0)),
               (0.0056, (R * 0.8, H * 0.55))]
    else:
        ext = [(0.0017, (R * 1.6, H * 1.5)), (0.0050, (R * 0.8, H * 0.55))]
    last = out[-1].copy()
    for dist, rr in ext:
        out.append(last + d * dist)
        radii.append(rr)
    half_tube(p, out, radii, 5 if lod == 0 else 2)
    p.bm.normal_update()
    return p


def build_lod(spec):
    lod = spec["lod"]
    parts = [build_envelope(lod), build_print(lod), build_label(lod)] + build_buttons(lod) + [build_string(lod)]
    g.triangulate(parts)
    if lod == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        BOUNDS["pts"] = [tuple(v) for v in vs]
    return parts


# from the front, right and above, steeply (azimuth -34, 67 degrees): the print is closer, the envelope
# recedes, the frame is ~1 : 1 - it fits the square of a 2x2 cell (the preview fits it by height,
# anything wider is cropped)
INV_VIEW = (0.155, -0.113, 0.435)


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


def collision():
    """One convex hull over all points of the near LOD (envelope, print, string). The mass is the class
    weight (0.3 kg, OZL_Carrier_Base); a hit is thin fabric, as for vanilla paper (Paper.p3d)."""
    comps = [(BOUNDS["pts"], kx.PEN + r"\fabric_thin.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    cz = hi[2] / 2
    memory = {
        "invView": [INV_VIEW],
        "ce_center": [(0.0, 0.0, cz)],
        "ce_radius": [(max(abs(lo[0]), abs(hi[0])), 0.0, cz)],
    }
    print("bbox %.4f..%.4f x %.4f..%.4f x %.4f..%.4f, preview aspect from invView %.2f (2x2 cell: ~1)"
          % (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2], preview_aspect(bbox, INV_VIEW)))
    return comps, 0.3, memory, bbox


SHOTS = [
    ("front", (0.02, -0.44, 0.30), (0.0, -0.005, 0.002), 45),
    ("button", (-0.02, -0.17, 0.14), (0.014, -0.012, 0.002), 75),
    ("print", (0.24, -0.20, 0.17), (0.11, 0.008, 0.001), 50),
    ("corner", (-0.04, -0.26, 0.10), (-0.130, -0.062, 0.003), 70),
    ("top", (0.0, -0.01, 0.62), (0.0, -0.005, 0.002), 40),
    ("mouth", (0.33, -0.12, 0.085), (0.084, 0.004, 0.001), 90),
    ("back", (-0.30, 0.26, 0.22), (0.0, 0.0, 0.002), 45),
    ("inv", INV_VIEW, (0.0, -0.005, 0.002), 38),
]
# --look preview: all angles (the carrier is small, a frame on the bake machine's GPU takes seconds); there
# are no machine states
M.look_shots = (len(SHOTS), 0)

if __name__ == "__main__":
    M.run(build_lod, collision, SHOTS, row_step=0.42, row_shot=((0.21, -0.75, 0.55), (0.21, 0.0, 0.0)))
