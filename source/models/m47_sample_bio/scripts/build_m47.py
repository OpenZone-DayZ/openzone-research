"""M47 - Biosample (OZL_Sample_01): a Bio line sample shared by all factions. A thermal sample case: a
plastic case with a latch and a window in the lid, a blue cold pack and two tubes with green caps in
sockets inside. A portable 1x2 item.

    blender --background --python build_m47.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py with the system Python first (biohazard sign, tag, snowflakes).

Target: about 8 x 20 x 6 cm; white or light-grey plastic, a blue gel cold pack, two tubes with coloured
caps (green is the Bio line colour), an empty paper tag, a biohazard sign; the lid is closed and the
tubes show through a clear window; 60-300 g. Small-item budget: 0.3-1.5k triangles, mid LOD ~40 %,
texture 512-1024.

Prototype and sizes:
- case: a household thermal case, 20.5 x 7.5 x 5.5 cm with a 17 x 4 cm cold pack (the lab counterpart is
  the Sarstedt cool transport container). Model: a rigid case 205 x 78 x 55 mm - 3 mm wider than the
  photographed one so that the 48 mm window fits the cold pack and the tubes; body 34 mm, lid 20 mm on
  two hinges at the back, a flip latch at the front, a lug for the tag cord on the end; window 124 x 48
  mm in a recessed frame.
- cold pack 170 x 40 x 12 mm with a welded seam round the perimeter, in a foam cradle.
- tubes 13 x 75 mm (the vacuum blood-tube size, BD 13 x 75 / 13 x 100; the green cap is lithium heparin
  and matches the line colour): glass, blood, an empty paper label, cap D 16.4 x 18 mm (Hemogard: ribbed
  skirt, rubber plug in the middle). They lie in the cutouts of two cross cradles over the cold pack.
- tag: a small manila tag 40 x 22 mm with an eyelet, on a cord from the lug (fields empty).
- mass 250 g (case, cold pack with ~100 ml of gel, two tubes).

Design decisions:
- 'dayz' look: matte, slightly yellowed plastic, edges and roundings worn to grey, dirt in the crevices
  (seam groove, hinges, window frame) and at the bottom, fine scratches, greasy hand marks. The wear
  pattern is scaled for a small item (K_SMALL): kit's is sized for stations of one or two metres and
  would give one blotch over a 20 cm case; cavities use AO 6 mm (kit: 4 cm, which here is the whole
  interior). The material builders are local, kit is untouched.
- no angularity: the bottom of the body and the top of the lid are rounded by two faces at 30 and 60
  degrees (smoothing breaks at 40 degrees in game and in the preview, so a single 45-degree chamfer read
  as a facet); the walls have a moulding draft from the seam; the parting seam is a groove (0.8 mm
  chamfers) with a dark gasket. Body and lid are surfaces over rings of one kind (no boolean
  differences, so the unwrap is the same on every run).
- no vanilla proxies: the case is closed, inside are the line's own items (vanilla ones cannot replace
  them), and nothing foreign belongs on a portable sample. Vanilla plastic and small items serve as the
  look reference (look_compare).
- atlas 1024: there are twice as many details, and at 512 the wear, the label fields and the cap ribbing
  would blur in game (1024 gives 2000 px/m).
- state 'used but intact'; no faction colour (the sample is shared). Signs: biohazard sign, empty tag
  with fields, snowflakes on the cold pack (a 'cold' pictogram), thermal indicator. No lamps, screens or
  moving parts, so no work view. LODs: near ~1500 triangles and mid (~32 %: no cord, eyelet, indicator,
  gasket, hinge knuckles and pin, latch lugs; fewer faces), no far LOD.

Blender axes: X is length, Y is width (the latch side faces -Y), Z is up. The origin is the centre of
the bottom: autocenter = 0 (in Geometry), boundingbox_min at the bottom, so a dropped case lies on its
bottom. The inventory camera (invView) is on the -X end, looking from above: the long axis stands up in
the 1x2 cell, like the vanilla syringe (its invView is from the end, above).
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
from mathutils import Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m ---------------------------------------------------------------------------
L, W = 0.205, 0.078
HX, HY = L / 2, W / 2
RC = 0.018                      # corner radius in plan
TRAY_H = 0.034
LID_Z0, LID_Z1 = 0.0350, 0.055
RB, RT = 0.0035, 0.0040         # rounding of the body bottom and the lid top
CT = 0.0008                     # edge chamfers at the parting seam (the groove)
DRAFT_T, DRAFT_L = 0.0005, 0.0004          # draft: body wall to the bottom, lid wall to the top
LIP_Z, LIP_IN = (0.0336, 0.0354), 0.0010   # gasket in the seam groove
WIN = (-0.062, 0.062, -0.024, 0.024)       # window in the lid
WIN_R = 0.004
POCKET, POCKET_D = 0.003, 0.0012           # recessed window frame: width, depth
GLASS_Z = LID_Z1 - POCKET_D + 0.0002       # the glass rests on the rubber gasket of the frame
GLASS_IN = 0.002                           # the glass overlaps the gasket
FOAM_Z = 0.026                  # the well bottom is foam
PACK = (-0.085, 0.085, -0.020, 0.020, 0.022, 0.034)   # cold pack (snowflake print, bounds)
PACK_X = 0.0645                 # the cold pack is not visible beyond the well walls (x = +-0.062)
# cold pack cross-section (y, z) from front to back: undercut into the foam, welded rim, soft top
_PK = [(0.0195, 0.0255), (0.0215, 0.0278), (0.0215, 0.0284), (0.0200, 0.0284), (0.0192, 0.0303),
       (0.0175, 0.0320), (0.0145, 0.0333), (0.0100, 0.0339)]
PACK_PROF = [(-y, z) for y, z in _PK] + [(0.0, 0.0341)] + [(y, z) for y, z in reversed(_PK)]
PACK_SEAM = {0, 1, 2, 13, 14, 15}          # profile segments that form the seam rim
CRADLE_X, CRADLE_HW = (-0.016, 0.031), 0.004
CRADLE_Y, CRADLE_TOP = 0.0200, 0.0405      # cradle: half-width, top (the tube axis)
TUBE_R, TUBE_Y, TUBE_X = 0.0065, 0.0095, (-0.025, 0.050)
TUBE_ZC = 0.0405
FILL_X = 0.030                  # level mark on the label; the air bubble is at the cap, on top
LABEL_X = (-0.012, 0.036)       # paper label along the tube
LABEL_WIN = (25.0, 115.0)       # label window (the blood shows): angle from +y towards +z, degrees - top-back
LABEL_LINES = (140.0, 165.0, -170.0)       # empty fields on the label (same angle)
CAP_X0, CAP_SKIRT, CAP_TOP, CAP_R = 0.040, 0.0558, 0.0580, 0.0082
HINGE_X, HINGE_LEN, HINGE_R = (-0.055, 0.055), 0.028, 0.0032
HINGE_Y, HINGE_Z = HY + 0.0022, 0.0350
# hinge knuckles measured from its middle: the two outer ones on the lid, the middle one on the body,
# 0.8 mm gaps
KNUCKLES = ((-0.0140, -0.0053, True), (-0.0045, 0.0045, False), (0.0053, 0.0140, True))
LATCH_W = 0.0094                # half-width of the latch tab
LATCH_PIN = (-HY - 0.0026, 0.0470)         # latch pin (y, z)
LUG_C, LUG_HOLE_R = (HX + 0.0032, 0.0180), 0.0026     # lug hole (x, z)
BIO_C, BIO = (-0.0815, 0.004), 0.025       # biohazard sticker, as in make_decals.py
TAG_C, TAG_L, TAG_W, TAG_CUT = (0.0815, -0.002), 0.040, 0.022, 0.005
TAG_ROT, TAG_HOLE, TAG_BOX = 14.0, 0.0145, 0.052
TAG_Z = (0.0551, 0.0555)
TAG_CURL = 0.0016               # the free end of the tag is raised
IND_C, IND_SIZE = (-0.0815, -0.0225), (0.016, 0.008)  # thermal indicator
CORD_R = 0.0007
PACK_L, PACK_W = PACK[1] - PACK[0], PACK[3] - PACK[2]
K_SMALL = 3.5                   # wear pattern finer than on stations (the item is 20 cm)

LOD_SPECS = [
    dict(lod=0, corner=3, sides=10),
    dict(lod=1, corner=2, sides=6),
]

REGIONS = {
    "case": ("case", 1.0), "inner": ("inner", 0.6), "seam": ("seam", 0.4), "gasket": ("gasket", 0.5),
    "foam": ("foam", 0.8), "latch": ("latch", 1.5), "steel": ("steel", 0.8),
    "pack": ("pack", 1.6), "pack_seam": ("pack_seam", 0.8),
    "tube": ("tube", 3.0), "cap": ("cap", 2.0), "rubber": ("rubber", 1.5),
    "cord": ("cord", 0.6), "tag": ("tag", 3.0), "grommet": ("grommet", 1.0),
    "sticker": ("sticker", 3.0), "indicator": ("indicator", 3.0), "glass": ("cord", 1.0),
}


def wdecal(name):
    return os.path.join(WORK, name)


BIO_DEC = (wdecal("decal_bio.png"), "z", 1, ("x", "y"), BIO_C, (BIO, BIO), (LID_Z1 - 0.001, LID_Z1 + 0.002))
TAG_DEC = (wdecal("decal_tag.png"), "z", 1, ("x", "y"), TAG_C, (TAG_BOX, TAG_BOX), (TAG_Z[1] - 0.0003, 0.06))
SNOW_DEC = (wdecal("decal_snow.png"), "z", 1, ("x", "y"), (0.0, 0.0), (PACK_L, PACK_W), (0.031, 0.036))


# --- materials (local builders: the pattern is scaled for a small item) -------------------------
def coords_s(t, origin, seed, k=K_SMALL):
    """Pattern coordinates: the same as kit's (from the model origin, offset by seed) but k times finer."""
    vec, sep = t.coords(origin, seed)
    return t.stretch(vec, k, k, k), sep


def layers_s(t, col, dirt, vec, nsep, grime, soil):
    """Layers of the 'dayz' profile like kmats.dayz_layers (muting, tone blotches, streaks, greasy
    marks, scratches), but streaks, blotches and scratches scale with soil: the sample is 'used but
    intact'.
    """
    k = kmats.LOOK
    d, v = k["patina"]
    gray = t.node("ShaderNodeRGBToBW")
    t.link(col, gray.inputs[0])
    col = t.mixc(d, col, gray.outputs[0])
    col = t.mixc(1.0 - v, col, (0, 0, 0, 1))
    n1 = t.maprange(t.noise(vec, 1.7, 5.0, 0.6), 0.3, 0.7, 0.0, 1.0)
    col = t.mixc(n1, t.mixc(k["mottle"], col, (0, 0, 0, 1)), t.mixc(k["mottle"] * 0.4, col, (1, 1, 1, 1)))
    vert = t.maprange(t.math("ABSOLUTE", nsep.outputs["Z"]), 0.35, 0.6, 1.0, 0.0)
    st = t.step(t.noise(t.stretch(vec, 1.0, 1.0, 0.07), 16.0, 6.0, 0.6), 0.60, 0.70)
    st = t.math("MULTIPLY", t.math("MULTIPLY", st, vert), k["streaks"] * soil * min(1.0, 0.4 + grime))
    col = t.mixc(st, col, kmats.GRIME)
    sm = t.math("MULTIPLY", t.step(t.noise(vec, 3.2, 4.0, 0.5), 0.64, 0.74), k["smudge"] * soil)
    col = t.mixc(sm, col, kmats.lin((40, 36, 30)))
    s1 = t.step(t.noise(t.stretch(vec, 0.03, 1.0, 1.0), 220.0, 2.0, 0.5), 0.71, 0.725)
    s2 = t.step(t.noise(t.stretch(vec, 1.0, 0.03, 1.0), 220.0, 2.0, 0.5), 0.71, 0.725)
    sc = t.math("MULTIPLY", t.math("MAXIMUM", s1, s2),
                t.maprange(t.noise(vec, 6.0, 4.0, 0.5), 0.4, 0.7, 0.0, k["scratches"] * soil))
    col = t.mixc(sc, col, t.mixc(0.5, col, (0.55, 0.55, 0.55, 1)))
    dirt = t.math("MAXIMUM", dirt, t.math("MAXIMUM", st, sm))
    return col, dirt


def weather_s(t, col, vec, sep, nsep, floor_z=0.0, dust=0.1, grime=0.3, cav=0.4, low_h=0.012, cav_dist=0.006,
              soil=1.0):
    """kmats.weather for small items: dust on upward-facing surfaces, dirt in cavities (AO cav_dist) and
    below low_h from the bottom, layers_s in the 'dayz' profile. Returns (colour, dirt strength).
    """
    k = kmats.LOOK
    dayz = k["name"] == "dayz"
    if dayz:
        dust, cav = dust * k["dust_k"], cav * k["cav_k"]
    up = t.maprange(nsep.outputs["Z"], 0.4, 0.9, 0.0, 1.0)
    dn = t.maprange(t.noise(vec, 4.0, 6.0, 0.6), 0.35, 0.7, 0.4, 1.0)
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", up, dn), dust), col, kmats.DUST)
    c = t.maprange(t.cavity(cav_dist), 0.15, 0.6, 0.0, 1.0)
    low = t.maprange(sep.outputs["Z"], floor_z, floor_z + low_h, 1.0, 0.0)
    dirt = t.math("MAXIMUM", t.math("MULTIPLY", c, cav), t.math("MULTIPLY", low, grime))
    dirt = t.math("MULTIPLY", dirt, t.maprange(t.noise(vec, 7.0, 8.0, 0.6), 0.3, 0.7, 0.5, 1.0))
    col = t.mixc(dirt, col, kmats.GRIME)
    if dayz:
        col, dirt = layers_s(t, col, dirt, vec, nsep, grime, soil)
    return col, dirt


def tone(color, k):
    return tuple(min(1.0, c * k) for c in color[:3]) + (1,)


def build_aged(mat, origin, color, seed=3.0, gloss=0.30, spec=0.22, floor_z=0.0, dust=0.1, grime=0.3, cav=0.4,
               mottle=0.05, yellow=0.0, scuff=(0.64, 0.72), scuff_col=None, rim=0.0, scratch=0.0, soil=1.0,
               bands=(), band_h=0.0, low_h=0.012):
    """Moulded plastic that has seen use: tone blotches, yellowing (yellow - more on top), wear on edges
    and (rim) on roundings in colour scuff_col (grey on white plastic, not lighter), fine scratches in
    two directions (scratch), bands [(z0, z1, colour)] across the height - the seam inside the well;
    with band_h they are moulded grooves (the latch tab ribbing).
    """
    t = kmats.Tree(mat)
    vec, sep = coords_s(t, origin, seed)
    nsep = t.normal()
    col = t.mixc(t.maprange(t.noise(vec, 6.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0), tone(color, 1 - mottle),
                 tone(color, 1 + mottle))
    if yellow > 0:
        up = t.maprange(nsep.outputs["Z"], -0.3, 0.9, 0.35, 1.0)
        yl = t.math("MULTIPLY", t.math("MULTIPLY", t.maprange(t.noise(vec, 1.2, 4.0, 0.5), 0.3, 0.7, 0.3, 1.0), up),
                    yellow)
        col = t.mixc(yl, col, kmats.lin((206, 186, 132)))
    bmask = 0.0
    for z0, z1, bc in bands:
        m = t.math("MULTIPLY", t.math("GREATER_THAN", sep.outputs["Z"], z0), t.math("LESS_THAN", sep.outputs["Z"], z1))
        col = t.mixc(m, col, bc)
        bmask = m if isinstance(bmask, float) else t.math("MAXIMUM", bmask, m)
    scol = scuff_col or tuple(min(1.0, c * 1.6 + 0.04) for c in color[:3]) + (1,)
    edge = t.maprange(t.edge_wear(0.0015), 0.06, 0.25, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 18.0, 8.0, 0.7), 0.7), t.math("MULTIPLY", edge, 0.6))
    if rim > 0:
        # roundings wear first: faces at 20..70 degrees to the horizontal
        nz = t.math("ABSOLUTE", nsep.outputs["Z"])
        tilt = t.math("MULTIPLY", t.maprange(nz, 0.15, 0.45, 0.0, 1.0), t.maprange(nz, 0.97, 0.80, 0.0, 1.0))
        f = t.math("ADD", f, t.math("MULTIPLY", tilt, rim))
    sc = t.step(f, scuff[0], scuff[1])
    col = t.mixc(t.math("MULTIPLY", sc, 0.55), col, scol)
    h = t.math("MULTIPLY", sc, -0.2)
    if band_h > 0 and not isinstance(bmask, float):
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", bmask, band_h))
    if scratch > 0:
        s1 = t.step(t.noise(t.stretch(vec, 0.04, 1.0, 1.0), 160.0, 2.0, 0.5), 0.70, 0.72)
        s2 = t.step(t.noise(t.stretch(vec, 1.0, 0.05, 1.0), 160.0, 2.0, 0.5), 0.70, 0.72)
        sk = t.math("MULTIPLY", t.math("MAXIMUM", s1, s2),
                    t.maprange(t.noise(vec, 3.0, 4.0, 0.5), 0.35, 0.65, 0.0, scratch))
        col = t.mixc(t.math("MULTIPLY", sk, 0.6), col, scol)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", sk, 0.1))
    col, dirt = weather_s(t, col, vec, sep, nsep, floor_z, dust, grime, cav, low_h, soil=soil)
    gl = t.math("SUBTRACT", gloss, t.math("MULTIPLY", t.math("ADD", dirt, sc), gloss * 0.5))
    sp = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.5))
    return kmats.out(t, col, gl, sp, h)


def build_foam(mat, origin, color, seed=3.7, gloss=0.05, spec=0.03, cell=900.0, dust=0.03, grime=0.15, soil=0.4):
    """Polyethylene foam of the cradle: ~1 mm cells (Voronoi pattern - dimples in colour and relief)."""
    t = kmats.Tree(mat)
    vec0, sep = t.coords(origin, seed)
    vec = t.stretch(vec0, K_SMALL, K_SMALL, K_SMALL)
    nsep = t.normal()
    vor = t.node("ShaderNodeTexVoronoi", Scale=cell)
    t.link(vec0, vor.inputs["Vector"])
    d = vor.outputs["Distance"]
    pit = t.maprange(d, 0.05, 0.55, 1.0, 0.0)
    col = t.mixc(t.maprange(t.noise(vec, 6.0, 4.0, 0.6), 0.3, 0.7, 0.0, 1.0), tone(color, 0.92), color)
    col = t.mixc(t.math("MULTIPLY", pit, 0.22), col, tone(color, 0.6))
    col, dirt = weather_s(t, col, vec, sep, nsep, 0.0, dust, grime, 0.3, soil=soil)
    gl = t.math("SUBTRACT", gloss, t.math("MULTIPLY", dirt, gloss * 0.5))
    return kmats.out(t, col, gl, spec, t.math("MULTIPLY", d, 0.6))


def build_print(mat, origin, color, seed=5.0, gloss=0.5, spec=0.4, decal_items=(), mottle=0.04, dust=0.05,
                grime=0.15, wrinkle=0.0, fiber=0.0, soil=0.6):
    """Film, sticker, card with a print (decal_items): fine film wrinkles (wrinkle), card fibres
    (fiber), light dirt.
    """
    t = kmats.Tree(mat)
    vec, sep = coords_s(t, origin, seed)
    nsep = t.normal()
    col = t.mixc(t.maprange(t.noise(vec, 8.0, 5.0, 0.6), 0.3, 0.7, 0.0, 1.0), tone(color, 1 - mottle),
                 tone(color, 1 + mottle))
    h = 0.0
    if fiber > 0:
        fb = t.noise(t.stretch(vec, 1.0, 0.2, 1.0), 260.0, 3.0, 0.6)
        col = t.mixc(t.math("MULTIPLY", t.maprange(fb, 0.4, 0.7, 0.0, 1.0), fiber * 0.3), col, tone(color, 0.8))
        h = t.math("MULTIPLY", fb, fiber * 0.3)
    col = kmats.decals(t, col, sep, nsep, decal_items)
    if wrinkle > 0:
        wr = t.math("MULTIPLY", t.noise(t.stretch(vec, 1.0, 0.3, 1.0), 30.0, 3.0, 0.6), wrinkle)
        h = wr if isinstance(h, float) else t.math("ADD", h, wr)
    col, dirt = weather_s(t, col, vec, sep, nsep, 0.0, dust, grime, 0.3, soil=soil)
    gl = t.math("SUBTRACT", gloss, t.math("MULTIPLY", dirt, gloss * 0.5))
    sp = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, gl, sp, h)


def local_tube(t, sep):
    """Coordinates from the axis of the tube itself (ly, dz) and the angle from +y towards +z: both
    tubes share one piece of the atlas (uv_name), so their print is identical, not mirrored.
    """
    y = sep.outputs["Y"]
    ly = t.math("SUBTRACT", y, t.math("MULTIPLY", t.math("SIGN", y), TUBE_Y))
    dz = t.math("SUBTRACT", sep.outputs["Z"], TUBE_ZC)
    return ly, dz, t.math("ARCTAN2", dz, ly)


def build_tube(mat, origin, liquid, glass, label, gloss=0.85, spec=0.7):
    """Tube under the window: opaque glass, the colour is what shows through it. The tube lies: blood
    along its whole length, an air bubble on top at the cap; a paper label over three quarters of the
    circumference with the blood visible in its window; empty pencil fields and a level mark on the
    label.
    """
    t = kmats.Tree(mat)
    vec, sep = coords_s(t, origin, 9.0)
    nsep = t.normal()
    x = sep.outputs["X"]
    ly, dz, phi = local_tube(t, sep)
    hz = t.math("DIVIDE", dz, TUBE_R)                              # -1 bottom .. 1 top
    xa = t.math("SUBTRACT", FILL_X + 0.009, t.math("MULTIPLY", t.math("ADD", hz, 1.0), 0.005))
    air = t.maprange(t.math("SUBTRACT", x, xa), -0.0004, 0.0004, 0.0, 1.0)
    dark = tone(liquid, 0.45)
    liq = t.mixc(t.maprange(hz, -1.0, 0.7, 0.0, 1.0), dark, liquid)
    liq = t.mixc(t.maprange(t.noise(vec, 40.0, 4.0, 0.5), 0.3, 0.7, 0.0, 0.25), liq, dark)
    col = t.mixc(air, liq, glass)
    inx = t.math("MULTIPLY", t.math("GREATER_THAN", x, LABEL_X[0]), t.math("LESS_THAN", x, LABEL_X[1]))
    win = t.math("MULTIPLY", t.math("GREATER_THAN", phi, math.radians(LABEL_WIN[0])),
                 t.math("LESS_THAN", phi, math.radians(LABEL_WIN[1])))
    lab = t.math("MULTIPLY", inx, t.math("SUBTRACT", 1.0, win))
    paper = t.mixc(t.maprange(t.noise(vec, 30.0, 4.0, 0.6), 0.3, 0.7, 0.0, 1.0), tone(label, 0.93), label)
    lines = t.math("MULTIPLY", t.math("GREATER_THAN", x, FILL_X - 0.0007), t.math("LESS_THAN", x, FILL_X))
    for a in LABEL_LINES:
        lines = t.math("MAXIMUM", lines, t.math("LESS_THAN", t.math("ABSOLUTE", t.math("SUBTRACT", phi, math.radians(a))),
                                                0.025))
    lines = t.math("MULTIPLY", lines, t.math("MULTIPLY", t.math("GREATER_THAN", x, LABEL_X[0] + 0.003),
                                              t.math("LESS_THAN", x, LABEL_X[1] - 0.003)))
    paper = t.mixc(t.math("MULTIPLY", lines, 0.7), paper, kmats.lin((118, 116, 132)))
    col = t.mixc(lab, col, paper)
    gl = t.mixf(lab, gloss, 0.15)
    sp = t.mixf(lab, spec, 0.08)
    col, dirt = weather_s(t, col, vec, sep, nsep, 0.0, 0.02, 0.05, 0.2, soil=0.3)
    return kmats.out(t, col, gl, sp, t.math("MULTIPLY", lab, 0.05))


def build_cap(mat, origin, color, seed=6.2, gloss=0.42, spec=0.3, ribs=24):
    """Hemogard cap: ribbed skirt (grooves in colour and relief), worn edges."""
    t = kmats.Tree(mat)
    vec, sep = coords_s(t, origin, seed)
    nsep = t.normal()
    x = sep.outputs["X"]
    ly, dz, phi = local_tube(t, sep)
    groove = t.maprange(t.math("SINE", t.math("MULTIPLY", phi, float(ribs))), -0.35, -0.8, 0.0, 1.0)
    skirt = t.math("MULTIPLY", t.math("GREATER_THAN", x, CAP_X0 + 0.0012), t.math("LESS_THAN", x, CAP_SKIRT - 0.0006))
    groove = t.math("MULTIPLY", groove, skirt)
    col = t.mixc(t.maprange(t.noise(vec, 10.0, 4.0, 0.6), 0.3, 0.7, 0.0, 1.0), tone(color, 0.94), color)
    col = t.mixc(t.math("MULTIPLY", groove, 0.45), col, tone(color, 0.55))
    edge = t.maprange(t.edge_wear(0.001), 0.06, 0.25, 0.0, 1.0)
    sc = t.step(t.math("ADD", t.math("MULTIPLY", t.noise(vec, 18.0, 8.0, 0.7), 0.7), t.math("MULTIPLY", edge, 0.6)),
                0.66, 0.74)
    col = t.mixc(t.math("MULTIPLY", sc, 0.4), col, tuple(min(1.0, c * 1.4 + 0.03) for c in color[:3]) + (1,))
    col, dirt = weather_s(t, col, vec, sep, nsep, 0.0, 0.03, 0.10, 0.3, soil=0.3)
    h = t.math("SUBTRACT", t.math("MULTIPLY", groove, -0.5), t.math("MULTIPLY", sc, 0.1))
    gl = t.math("SUBTRACT", gloss, t.math("MULTIPLY", t.math("ADD", dirt, sc), gloss * 0.5))
    sp = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.5))
    return kmats.out(t, col, gl, sp, h)


def build_indicator(mat, origin, center, size, seed=8.8):
    """Cold-chain thermal indicator: a white sticker, a thin frame, a blue sample dot and an empty
    window (not triggered). No text.
    """
    t = kmats.Tree(mat)
    vec, sep = coords_s(t, origin, seed)
    nsep = t.normal()
    (cx, cy), (w, h) = center, size
    dx = t.math("SUBTRACT", sep.outputs["X"], cx)
    dy = t.math("SUBTRACT", sep.outputs["Y"], cy)
    ax, ay = t.math("ABSOLUTE", dx), t.math("ABSOLUTE", dy)

    def dist(ox):
        a = t.math("SUBTRACT", dx, ox)
        return t.math("SQRT", t.math("ADD", t.math("MULTIPLY", a, a), t.math("MULTIPLY", dy, dy)))
    paper = kmats.lin((236, 234, 224))
    col = t.mixc(t.maprange(t.noise(vec, 30.0, 4.0, 0.6), 0.3, 0.7, 0.0, 1.0), tone(paper, 0.95), paper)
    inner = t.math("MULTIPLY", t.math("LESS_THAN", ax, w / 2 - 0.0010), t.math("LESS_THAN", ay, h / 2 - 0.0010))
    outer = t.math("MULTIPLY", t.math("LESS_THAN", ax, w / 2 - 0.0004), t.math("LESS_THAN", ay, h / 2 - 0.0004))
    grey = kmats.lin((96, 98, 106))
    col = t.mixc(t.math("SUBTRACT", outer, inner), col, grey)
    col = t.mixc(t.math("LESS_THAN", dist(-0.0038), 0.0022), col, kmats.lin((38, 84, 182)))
    d2 = dist(0.0038)
    col = t.mixc(t.math("MULTIPLY", t.math("LESS_THAN", d2, 0.0024), t.math("GREATER_THAN", d2, 0.0018)), col, grey)
    col, dirt = weather_s(t, col, vec, sep, nsep, 0.0, 0.06, 0.2, 0.3, soil=0.5)
    gl = t.math("SUBTRACT", 0.30, t.math("MULTIPLY", dirt, 0.15))
    return kmats.out(t, col, gl, 0.2, 0.0)


# white plastic that has seen use: lighter than vanilla lab items (125..135), here ~170 so that the
# sample is light but not CG-white; yellowed, edges and roundings worn to grey
CASE = dict(color=kmats.lin((206, 202, 188)), seed=2.1, gloss=0.30, spec=0.22, dust=0.12, grime=0.40, cav=0.5,
            mottle=0.05, yellow=0.28, scuff=(0.61, 0.70), scuff_col=kmats.lin((150, 144, 128)), rim=0.35,
            scratch=0.7, soil=0.85, low_h=0.018)
LATCH_C = kmats.lin((122, 124, 122))
LATCH_GRIP = [(z, z + 0.0005, tone(LATCH_C, 0.7)) for z in (0.0300, 0.0312, 0.0324)]   # latch tab ribbing
KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "case": (build_aged, CASE),
    # well interior: lighter dirt, a dark band at the height of the parting seam
    "inner": (build_aged, dict(CASE, color=kmats.lin((192, 191, 182)), seed=2.6, yellow=0.08, dust=0.03, grime=0.2,
                               rim=0.0, scratch=0.2, soil=0.4, bands=[(0.0341, 0.0349, kmats.lin((92, 92, 88)))])),
    "seam": (build_aged, dict(color=kmats.lin((62, 62, 60)), seed=3.1, gloss=0.18, spec=0.12, dust=0.05, grime=0.3,
                              scuff=(0.9, 1.0), soil=0.5)),
    "gasket": (build_aged, dict(color=kmats.lin((34, 34, 34)), seed=3.4, gloss=0.15, spec=0.10, dust=0.15, grime=0.2,
                                scuff=(0.9, 1.0), soil=0.5)),
    "foam": (build_foam, dict(color=kmats.lin((184, 186, 180)), seed=3.7)),
    # latch: grey plastic, worn lighter
    "latch": (build_aged, dict(CASE, color=LATCH_C, seed=4.4, yellow=0.0, gloss=0.32, scuff=(0.58, 0.68),
                               scuff_col=kmats.lin((170, 170, 164)), rim=0.1, scratch=0.8, soil=0.9,
                               bands=LATCH_GRIP, band_h=0.6)),
    "steel": ("steel", dict(seed=4.2, tone=0.34, along="x", gloss=0.55, spec=0.65, dust=0.05, grime=0.4)),
    "pack": (build_print, dict(color=kmats.lin((34, 86, 196)), seed=5.0, gloss=0.55, spec=0.45, decal_items=[SNOW_DEC],
                               wrinkle=0.25, dust=0.02, grime=0.1, soil=0.3)),
    "pack_seam": (build_print, dict(color=kmats.lin((86, 134, 214)), seed=5.3, gloss=0.6, spec=0.45, wrinkle=0.5,
                                    dust=0.02, grime=0.15, soil=0.3)),
    "tube": (build_tube, dict(liquid=kmats.lin((112, 16, 18)), glass=kmats.lin((118, 132, 138)),
                              label=kmats.lin((234, 230, 214)))),
    "cap": (build_cap, dict(color=kmats.lin((46, 150, 72)))),
    "rubber": (build_aged, dict(color=kmats.lin((92, 94, 96)), seed=6.6, gloss=0.12, spec=0.08, dust=0.02, grime=0.2,
                                scuff=(0.9, 1.0), soil=0.3)),
    "cord": (build_aged, dict(color=kmats.lin((176, 156, 116)), seed=7.0, gloss=0.06, spec=0.04, dust=0.1, grime=0.4,
                              mottle=0.14, scuff=(0.9, 1.0), soil=0.8)),
    "tag": (build_print, dict(color=kmats.lin((212, 188, 138)), seed=7.6, gloss=0.10, spec=0.06, decal_items=[TAG_DEC],
                              dust=0.15, grime=0.35, fiber=0.3, soil=0.8)),
    "grommet": ("steel", dict(seed=7.3, tone=0.42, along="x", gloss=0.55, spec=0.6, dust=0.05, grime=0.4)),
    "sticker": (build_print, dict(color=kmats.lin((236, 182, 26)), seed=8.1, gloss=0.35, spec=0.25,
                                  decal_items=[BIO_DEC], dust=0.08, grime=0.25, soil=0.6)),
    "indicator": (build_indicator, dict(center=IND_C, size=IND_SIZE)),
})

OBJ, NAME = "m47_sample_bio", "ozr_sample_bio"
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 glass=dict(base=(0.86, 0.88, 0.88), clear=0.04, edge=0.12, smudge=0.07, streaks=0.0))
P = M.part
BOUNDS = {}


# --- helpers --------------------------------------------------------------------------------
def rr(x0, x1, y0, y1, r, n):
    """Rounded rectangle, counter-clockwise (top view): always 4 (n + 1) points - rings of one kind join
    strip to strip, point to point.
    """
    r = max(r, 2e-4)
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def outline(d, n):
    """Case outline inset by d."""
    return rr(-HX + d, HX - d, -HY + d, HY - d, RC - d, n)


def win_ring(d, n):
    """Window outline widened by d."""
    x0, x1, y0, y1 = WIN
    return rr(x0 - d, x1 + d, y0 - d, y1 + d, WIN_R + d, n)


def at_z(pts, z):
    return [(x, y, z) for x, y in pts]


def tray_d(z):
    """Body moulding draft: the wall is inset by DRAFT_T at the bottom, not at the seam."""
    return DRAFT_T * max(0.0, 1.0 - z / TRAY_H)


def lid_d(z):
    """Lid moulding draft: zero at the seam, DRAFT_L at the top."""
    return DRAFT_L * min(1.0, max(0.0, (z - LID_Z0) / (LID_Z1 - LID_Z0)))


def reg(p, name):
    return p.region_index(name, *REGIONS[name])


def face(p, verts, want):
    """Face from bmesh vertices, oriented towards want."""
    f = p.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def loft(p, rings, regions):
    """Surface over rings of equal length (counter-clockwise, top view): the strip between rings i and
    i+1 is in region regions[i]. The order [a_i, a_i+1, b_i+1, b_i] gives the normal 'along the ring x
    towards the next one': outward at the wall, up at the top, towards the window at the frame and well
    walls. Neighbouring strips share rings, so smoothing runs across the joints.
    """
    bm = p.bm
    vr = [[bm.verts.new(q) for q in r] for r in rings]
    n = len(vr[0])
    for k in range(len(vr) - 1):
        a, b = vr[k], vr[k + 1]
        p.tag([bm.faces.new([a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]]) for i in range(n)], reg(p, regions[k]))
    bm.normal_update()
    return vr


def lathe_x(p, prof, y, zc, sides, regions):
    """Body of revolution about an axis along x through (y, zc): prof [(x, r)] along the outer surface
    from one end to the other, r = 0 is a tip; strip i is in region regions[i]. The winding order gives
    outward normals for both side and end rings by itself.
    """
    bm = p.bm
    rings = []
    for x, r in prof:
        if r <= 0:
            rings.append([bm.verts.new((x, y, zc))] * sides)
        else:
            rings.append([bm.verts.new((x, y + r * math.cos(2 * math.pi * k / sides),
                                        zc + r * math.sin(2 * math.pi * k / sides))) for k in range(sides)])
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        fs = []
        for k in range(sides):
            j = (k + 1) % sides
            q = [a[k], a[j], b[j], b[k]]
            fs.append(bm.faces.new([v for m, v in enumerate(q) if v not in q[:m]]))
        p.tag(fs, reg(p, regions[i]))
    bm.normal_update()


def xcyl(p, x0, x1, y, z, r, sides, cap0=None, cap1=None):
    """Cylinder along x from x0 to x1 (sides in the part's current region); cap0, cap1 - the end region
    or None (no end face).
    """
    bm = p.bm

    def ring(x):
        return [bm.verts.new((x, y + r * math.cos(2 * math.pi * k / sides), z + r * math.sin(2 * math.pi * k / sides)))
                for k in range(sides)]
    a, b = ring(x0), ring(x1)
    p.tag([bm.faces.new([a[k], a[(k + 1) % sides], b[(k + 1) % sides], b[k]]) for k in range(sides)])
    if cap0:
        p.tag([bm.faces.new(a[::-1])], reg(p, cap0))
    if cap1:
        p.tag([bm.faces.new(b)], reg(p, cap1))


def annulus(p, cx, cy, z, r0, r1, n):
    """Flat ring facing up."""
    bm = p.bm
    o = [bm.verts.new((cx + r1 * math.cos(2 * math.pi * k / n), cy + r1 * math.sin(2 * math.pi * k / n), z))
         for k in range(n)]
    i = [bm.verts.new((cx + r0 * math.cos(2 * math.pi * k / n), cy + r0 * math.sin(2 * math.pi * k / n), z))
         for k in range(n)]
    p.tag([face(p, [o[k], o[(k + 1) % n], i[(k + 1) % n], i[k]], (0, 0, 1)) for k in range(n)])


def ring_prism_y(p, outer, hole, y0, y1):
    """Part with a hole along y: outer and hole contours [(x, z)] of equal length, points at the same
    angles from the hole centre.
    """
    bm = p.bm

    def vs(poly, y):
        return [bm.verts.new((x, y, z)) for x, z in poly]
    o0, o1, h0, h1 = vs(outer, y0), vs(outer, y1), vs(hole, y0), vs(hole, y1)
    n = len(outer)
    fs = []
    for k in range(n):
        j = (k + 1) % n
        fs += [bm.faces.new([o0[k], o0[j], h0[j], h0[k]]), bm.faces.new([o1[k], h1[k], h1[j], o1[j]]),
               bm.faces.new([o0[k], o1[k], o1[j], o0[j]]), bm.faces.new([h0[k], h0[j], h1[j], h1[k]])]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    p.tag(fs)


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, from M04/M16)."""
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


def tag_point(s, t):
    a = math.radians(TAG_ROT)
    return (TAG_C[0] - s * math.sin(a) + t * math.cos(a), TAG_C[1] + s * math.cos(a) + t * math.sin(a))


def round_rings(d0, z0, rad, up):
    """90-degree rounding with two faces at 30 and 60 degrees: [(inset, z)] from the wall (d0, z0) to
    the horizontal - up (lid) or down (body bottom).
    """
    l = rad / (0.5 + math.sqrt(3) / 2)
    if up:
        return [(d0, z0), (d0 + 0.5 * l, z0 + math.sqrt(3) / 2 * l), (d0 + rad, z0 + rad)]
    return [(d0 + rad, z0 - rad), (d0 + rad - math.sqrt(3) / 2 * l, z0 - rad + 0.5 * l), (d0, z0)]


# --- case -----------------------------------------------------------------------------------
def build_case(spec):
    """Body and lid are surfaces over rings (no boolean differences). The lid is a single strip: chamfer
    at the seam, wall, rounding, top, window frame, rubber gasket, well wall down to the foam, well
    bottom. Invisible faces (the top of the body and the bottom of the lid below the seam) are not
    built.
    """
    lod, n = spec["lod"], spec["corner"]
    zp = LID_Z1 - POCKET_D
    tray = P("tray", "case")
    if lod == 0:
        prof = round_rings(0.0, RB, RB, up=False) + [(0.0, TRAY_H - CT), (CT, TRAY_H)]
    else:
        prof = [(0.003, 0.0), (0.0, 0.003), (0.0, LID_Z0)]             # no seam: the wall goes up to the lid
    vr = loft(tray, [at_z(outline(d + tray_d(z), n), z) for d, z in prof], ["case"] * (len(prof) - 1))
    tray.tag([tray.bm.faces.new(vr[0][::-1])], reg(tray, "case"))      # bottom
    lid = P("lid", "case")
    if lod == 0:
        z0 = LID_Z1 - RT
        outer = [(CT, LID_Z0), (lid_d(LID_Z0 + CT), LID_Z0 + CT)] + round_rings(lid_d(z0), z0, RT, up=True)
        rings = [at_z(outline(d, n), z) for d, z in outer]
        regions = ["case"] * 6 + ["gasket", "inner"]
    else:
        rings = [at_z(outline(0.0, n), LID_Z0), at_z(outline(0.0, n), LID_Z1 - 0.003), at_z(outline(0.003, n), LID_Z1)]
        regions = ["case"] * 4 + ["gasket", "inner"]
    rings += [at_z(win_ring(POCKET, n), LID_Z1), at_z(win_ring(POCKET, n), zp), at_z(win_ring(0.0, n), zp),
              at_z(win_ring(0.0, n), FOAM_Z)]
    vr = loft(lid, rings, regions)
    lid.tag([lid.bm.faces.new(vr[-1])], reg(lid, "foam"))             # well bottom
    parts = [tray, lid]
    if lod == 0:
        lip = P("lip", "seam")
        loft(lip, [at_z(outline(LIP_IN, n), z) for z in LIP_Z], ["seam"])
        parts.append(lip)
    # glass: one face on the gasket, the corners go under the lid top
    gl = P("glass", "glass", section="glass")
    x0, x1, y0, y1 = WIN
    gx0, gx1, gy0, gy1 = x0 - GLASS_IN, x1 + GLASS_IN, y0 - GLASS_IN, y1 + GLASS_IN
    g.quad(gl, [(gx0, gy0, GLASS_Z), (gx1, gy0, GLASS_Z), (gx1, gy1, GLASS_Z), (gx0, gy1, GLASS_Z)])
    gl.glass_frame = (g.Frame((0, 0, GLASS_Z), (1, 0, 0), (0, 1, 0), (0, 0, 1)), gx0, gx1, gy0, gy1)
    parts.append(gl)
    return parts


def leaf(p, x0, x1, up):
    """Hinge knuckle leaf: from the knuckle to the lid wall (up) or to the body wall."""
    z0, z1 = (HINGE_Z + 0.0006, HINGE_Z + 0.0092) if up else (HINGE_Z - 0.0092, HINGE_Z - 0.0006)
    g.box(p, x0, x1, HY - 0.0008, HY + 0.0024, z0, z1)


def build_hinges(spec):
    """Two hinges at the back: three knuckles each on a steel pin (the pin shows in the gaps, its ends
    are in the outer knuckles), leaves to the lid and the body.
    """
    lod = spec["lod"]
    hg = P("hinges", "case")
    for xc in HINGE_X:
        if lod > 0:
            xcyl(hg, xc - HINGE_LEN / 2, xc + HINGE_LEN / 2, HINGE_Y, HINGE_Z, HINGE_R, 6, "case", "case")
            continue
        for a, b, on_lid in KNUCKLES:
            hg.use("case")
            xcyl(hg, xc + a, xc + b, HINGE_Y, HINGE_Z, HINGE_R, 10, "steel" if a == KNUCKLES[0][0] else None,
                 "steel" if b == KNUCKLES[-1][1] else None)
            leaf(hg, xc + a, xc + b, on_lid)
        hg.use("steel", *REGIONS["steel"])
        xcyl(hg, xc + KNUCKLES[0][0] + 0.0004, xc + KNUCKLES[-1][1] - 0.0004, HINGE_Y, HINGE_Z, 0.0013, 4)
    return [hg]


def build_latch(spec):
    """Flip latch at the front: a tab on a pin in two lugs of the lid, a hook under the body stop, a
    finger tab at the bottom.
    """
    lod = spec["lod"]
    lt = P("latch", "latch")
    yb = -HY
    if lod > 0:
        g.box(lt, -LATCH_W, LATCH_W, yb - 0.0042, yb + 0.0005, 0.0262, 0.0490)
        return [lt]
    py, pz = LATCH_PIN
    prof = [(yb - 0.0042, 0.0466), (yb - 0.0042, 0.0287), (yb - 0.0066, 0.0264), (yb - 0.0066, 0.0255),
            (yb - 0.0030, 0.0255), (yb + 0.0001, 0.0263), (yb + 0.0001, 0.0279), (yb - 0.0018, 0.0280),
            (yb - 0.0018, 0.0466)]
    g.prism(lt, prof, (1, 2), -LATCH_W, LATCH_W)
    xcyl(lt, -LATCH_W - 0.0003, LATCH_W + 0.0003, py, pz, 0.0024, 8)           # knuckle on the pin
    lug = [(yb + 0.0006, pz - 0.0030)] + [(py - 0.0030 * math.cos(math.radians(a)), pz + 0.0030 * math.sin(math.radians(a)))
                                          for a in (-90, 0, 90)] + [(yb + 0.0006, pz + 0.0030)]
    for s in (-1, 1):
        x0, x1 = sorted((s * (LATCH_W + 0.0003), s * (LATCH_W + 0.0037)))
        g.prism(lt, lug, (1, 2), x0, x1)                                            # lugs on the lid
    g.box(lt, -0.0125, 0.0125, yb - 0.0017, yb + 0.0005, 0.0281, 0.0299)           # stop on the body
    return [lt]


def build_lug(spec):
    """Moulded lug on the +X end: a loop with a hole across (along y) through which the tag cord is
    threaded.
    """
    lod = spec["lod"]
    lg = P("lug", "case")
    cx, cz = LUG_C
    xw = HX - 0.0006
    arc = [(HX + 0.0025 + 0.0065 * math.cos(math.radians(a)), 0.0180 + 0.0065 * math.sin(math.radians(a)))
           for a in (-90, -60, -30, 0, 30, 60, 90)]
    outer = [(xw, 0.0115)] + arc + [(xw, 0.0245), (xw, 0.0180)]
    if lod > 0:
        g.prism(lg, outer, (0, 2), -0.003, 0.003)
        return [lg]
    hole = []
    for x, z in outer:
        a = math.atan2(z - cz, x - cx)
        hole.append((cx + LUG_HOLE_R * math.cos(a), cz + LUG_HOLE_R * math.sin(a)))
    ring_prism_y(lg, outer, hole, -0.003, 0.003)
    return [lg]


def build_cord(spec):
    """Cord: from the lug hole up along the end, over the lid rounding, across the tag - into the
    eyelet.
    """
    if spec["lod"] > 0:
        return []
    hx, hy = tag_point(TAG_HOLE, 0.0)
    pts = [(LUG_C[0], 0.0, LUG_C[1]), (LUG_C[0] + 0.0004, -0.0042, LUG_C[1] + 0.0010),
           (HX + 0.0050, -0.0040, 0.0340), (HX + 0.0012, -0.0012, 0.0515), (HX - 0.0012, 0.0000, 0.0534),
           (HX - 0.0050, 0.0012, 0.0559), (hx + 0.0015, hy - 0.0005, 0.0564), (hx, hy, 0.0546)]
    cd = P("cord", "cord")
    g.pipe(cd, spline(pts, 2), CORD_R, 4)
    return [cd]


def build_tag(spec):
    """Tag: 0.4 mm card, the free end slightly raised; the eyelet is a metal ring."""
    lod = spec["lod"]
    h, w, c = TAG_L / 2, TAG_W / 2, TAG_CUT
    tg = P("tag", "tag")
    if lod > 0:
        poly = [tag_point(s, t) for t, s in ((-w, -h), (w, -h), (w, h - c), (w - c, h), (-w + c, h), (-w, h - c))]
        g.prism(tg, poly, (0, 1), *TAG_Z)
        return [tg]
    bm = tg.bm
    rows = [-h, -0.4 * h, h - c, h]
    th = TAG_Z[1] - TAG_Z[0]
    top, bot = [], []
    for s in rows:
        half = w if s < h - c + 1e-9 else w - c
        q = max(0.0, (-0.4 * h - s) / (0.6 * h))
        z = TAG_Z[1] + TAG_CURL * q * q
        pts = [tag_point(s, side * half) for side in (-1, 1)]
        top.append([bm.verts.new((x, y, z)) for x, y in pts])
        bot.append([bm.verts.new((x, y, z - th)) for x, y in pts])
    cx, cy = TAG_C

    def edge(q):
        cen = sum((v.co for v in q), Vector()) / len(q)
        return face(tg, q, (cen.x - cx, cen.y - cy, 0.0))
    fs = []
    for i in range(len(rows) - 1):
        fs.append(face(tg, [top[i][0], top[i][1], top[i + 1][1], top[i + 1][0]], (0, 0, 1)))
        fs.append(face(tg, [bot[i][0], bot[i + 1][0], bot[i + 1][1], bot[i][1]], (0, 0, -1)))
        for sd in (0, 1):
            fs.append(edge([top[i][sd], top[i + 1][sd], bot[i + 1][sd], bot[i][sd]]))
    for i in (0, len(rows) - 1):
        fs.append(edge([top[i][0], top[i][1], bot[i][1], bot[i][0]]))
    tg.tag(fs)
    hx, hy = tag_point(TAG_HOLE, 0.0)
    gr = P("grommet", "grommet")
    annulus(gr, hx, hy, TAG_Z[1] + 0.00008, 0.0017, 0.0033, 8)
    return [tg, gr]


def build_labels(spec):
    """Biohazard sticker and thermal indicator - on the lid, with rounded corners."""
    lod = spec["lod"]
    z = LID_Z1 + 0.0003
    st = P("sticker", "sticker")
    poly = rr(BIO_C[0] - BIO / 2, BIO_C[0] + BIO / 2, BIO_C[1] - BIO / 2, BIO_C[1] + BIO / 2, 0.0015, 1)
    st.tag([st.bm.faces.new([st.bm.verts.new(q) for q in at_z(poly, z)])])
    parts = [st]
    if lod == 0:
        ind = P("indicator", "indicator")
        (cx, cy), (iw, ih) = IND_C, IND_SIZE
        g.quad(ind, at_z([(cx - iw / 2, cy - ih / 2), (cx + iw / 2, cy - ih / 2), (cx + iw / 2, cy + ih / 2),
                          (cx - iw / 2, cy + ih / 2)], z))
        parts.append(ind)
    return parts


def cradle_profile(nseg):
    """Cradle section (y, z): the bottom is sunk into the soft pillow (the joint line runs along its
    top), tube cutouts on top.
    """
    r = TUBE_R + 0.0003
    pts = [(-CRADLE_Y, 0.0296), (CRADLE_Y, 0.0296), (CRADLE_Y, CRADLE_TOP)]
    for yc in (TUBE_Y, -TUBE_Y):
        for i in range(nseg + 1):
            a = math.radians(-180.0 * i / nseg)
            pts.append((yc + r * math.cos(a), CRADLE_TOP + r * math.sin(a)))
    pts.append((-CRADLE_Y, CRADLE_TOP))
    return pts


def build_inside(spec):
    """Under the window: the cold-pack pillow, two cradles with cutouts, two tubes with caps."""
    lod, s = spec["lod"], spec["sides"]
    parts = []
    pk = P("pack", "pack")
    if lod == 0:
        prof, seam = PACK_PROF, PACK_SEAM
    else:
        prof, seam = [PACK_PROF[i] for i in (0, 2, 3, 5, 8, 11, 13, 14, 16)], {0, 1, 6, 7}
    bm = pk.bm
    a = [bm.verts.new((-PACK_X, y, z)) for y, z in prof]
    b = [bm.verts.new((PACK_X, y, z)) for y, z in prof]
    for k in range(len(prof) - 1):
        pk.tag([bm.faces.new([a[k], b[k], b[k + 1], a[k + 1]])], reg(pk, "pack_seam" if k in seam else "pack"))
    parts.append(pk)
    cr = P("cradles", "foam")
    for xc in CRADLE_X:
        poly = (cradle_profile(3) if lod == 0 else
                [(-CRADLE_Y, 0.0328), (CRADLE_Y, 0.0328), (CRADLE_Y, CRADLE_TOP - 0.003), (-CRADLE_Y, CRADLE_TOP - 0.003)])
        g.prism(cr, poly, (1, 2), xc - CRADLE_HW, xc + CRADLE_HW)
    parts.append(cr)
    # the tubes are identical - they take the atlas once (uv_name), each from its own axis
    t0 = TUBE_X[0]
    R = TUBE_R
    if lod == 0:
        prof = [(t0, 0.0)] + [(t0 + R * (1 - math.cos(math.radians(a))), R * math.sin(math.radians(a))) for a in (30, 60)]
        prof += [(t0 + R, R), (CAP_X0 + 0.0008, R)]
        rc = CAP_TOP - CAP_SKIRT
        lc = rc / (0.5 + math.sqrt(3) / 2)
        cprof = [(CAP_X0, R + 0.0001), (CAP_X0, CAP_R), (CAP_SKIRT, CAP_R),
                 (CAP_SKIRT + math.sqrt(3) / 2 * lc, CAP_R - 0.5 * lc), (CAP_TOP, CAP_R - rc),
                 (CAP_TOP - 0.0003, 0.0036), (CAP_TOP - 0.0003, 0.0)]
        cregs = ["cap"] * 5 + ["rubber"]
    else:
        prof = [(t0, 0.0), (t0 + R, R), (CAP_X0 + 0.0008, R)]
        cprof = [(CAP_X0, R + 0.0001), (CAP_X0, CAP_R), (CAP_TOP - 0.0015, CAP_R), (CAP_TOP, CAP_R - 0.0015),
                 (CAP_TOP, 0.0)]
        cregs = ["cap"] * 4
    for k, y in enumerate((-TUBE_Y, TUBE_Y)):
        o = (0.0, y, TUBE_ZC)
        tb = P("tube_%d" % k, "tube", uv_name="tube", uv_origin=o)
        lathe_x(tb, prof, y, TUBE_ZC, s, ["tube"] * (len(prof) - 1))
        parts.append(tb)
        cp = P("cap_%d" % k, "cap", uv_name="cap", uv_origin=o)
        lathe_x(cp, cprof, y, TUBE_ZC, s, cregs)
        parts.append(cp)
    return parts


def build_lod(spec):
    parts = build_case(spec) + build_hinges(spec) + build_latch(spec) + build_lug(spec) + build_cord(spec)
    parts += build_tag(spec) + build_labels(spec) + build_inside(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """One convex hull of the case (outline with 2 segments per corner, up to the lid top); the cord and
    the tag have no collision. The mass is the item weight, 0.25 kg; the impact sound is plastic.
    """
    ring = rr(-HX, HX, -HY, HY, RC, 2)
    pts = [(x, y, z) for x, y in ring for z in (0.0, LID_Z1)]
    comps = [(pts, kx.PEN + r"\plastic.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    memory = {
        # inventory preview camera: from the -X end above, almost along the axis - the long axis stands
        # up in the 1x2 cell, projection ~1:2 (the camera does not go to the side, otherwise the case is
        # wider than the cell)
        "invView": [(-0.27, -0.03, 0.31)],
        "ce_center": [(0.0, 0.0, 0.0275)],
        "ce_radius": [(0.11, 0.0, 0.0275)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.25, memory, bbox


# all seven are the --look previews: overview, window close-up (tubes, cold pack), top, back (hinges),
# end with the lug and tag, latch, inventory camera
SHOTS = [
    ("front", (-0.20, -0.40, 0.27), (0.0, 0.0, 0.028), 45),
    ("window", (-0.11, -0.12, 0.17), (0.005, 0.0, 0.038), 40),
    ("top", (0.0, -0.10, 0.44), (0.0, 0.0, 0.03), 40),
    ("back", (0.26, 0.34, 0.22), (0.0, 0.0, 0.028), 45),
    ("tag", (0.21, -0.13, 0.15), (0.075, 0.0, 0.035), 45),
    ("latch", (-0.05, -0.22, 0.09), (0.0, -0.035, 0.035), 50),
    ("inv", (-0.27, -0.03, 0.31), (0.0, 0.0, 0.0275), 34),
]

M.look_shots = (7, 2)
M.run(build_lod, collision, SHOTS, row_step=0.25, row_shot=((0.125, -0.95, 0.40), (0.125, 0, 0.03)))
