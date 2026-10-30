"""M53 - Protection sample (OZL_Sample_13, candidate class): a sample of the Protection line shared by
all factions - a portable 2x2 item. A shot-up titanium armour plate and a piece of an aramid pack with
mutant claw furrows, tied together with a rubber band, with a tag under the band.

    blender --background --python build_m53.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py with the system Python first (furrows, holes, bullet marks, the tag).

Target: two cut-out pieces of body armour tied with a rubber band - a dark grey plate with bullet dents
and chips along the edge and a yellow-brown aramid fabric in several layers with frayed holes and claw
furrows; a tag without text with a grey stripe (the Protection line). Samples: 60-300 g, 200-800
triangles, texture 512, no faction colour, state used but intact.

Prototype and sizes:
- the target was ~15 x 12 x 3 cm with a 'ceramic or steel' plate, but a steel plate of 15 x 12 weighs
  0.5-0.75 kg (6B5-14: 3.8 mm steel; a Safariland 5 x 8" insert: 5.1 mm), the ceramic of 6B5-15 (boron
  carbide 13 mm) 0.6 kg, and samples weigh 60-300 g. So the plate is a 1.25 mm titanium armour plate
  ADU-605-80 (alloy VT-14): 19 such plates in the chest of the 6B2 (1978-1980s, Afghanistan), also the
  back of the 6B3TM-01 and 6B5-12/16/17/18. The 6B2 protected area is 28-30 dm2 on 19 overlapping
  plates: ~1.5 dm2 per plate, here 110 x 150 mm, corners R 9. Dark grey paint, chips down to the metal.
  Mass: 110 x 150 x 1.25 mm of titanium (4.5 g/cm3) = 93 g;
- aramid: a piece of the soft pack of the same vests: 30 layers of TSVM-DZh aramid fabric. The fabric is
  ~130 g/m2, 30 layers = 3.9 kg/m2, like class IIIA soft armour; ~0.25 mm per layer = 8 mm uncompressed
  (pressed to 6.2 at the edge). The piece is 96 x 105 mm = 39 g. The left edge is the original one,
  stitched 4 mm from the edge; the other three are cut with a knife;
- the stack is 15 x 11 x 1.2 cm and 140 g: plate 93 + aramid 39 + band (a strip of bicycle tube 14 x 1.6
  mm, a ring) ~6 + tag;
- dents are from pistol rounds (9x18 PM / 7.62x25 TT, which the ADU-605-80 plate holds): a bowl D 17-20
  mm, depth 1.4-1.6 mm (the plate lies on the bulges and on the band), the paint is knocked off, lead
  splashes as rays, traces of the tombac jacket; one plate corner is bent; three claw scratches down to
  the metal over it; a number stamped in digits;
- on the aramid four parallel claw furrows (pitch 9-14 mm, 40-50 mm long, torn through up to half the
  layers: inside the fabric is brighter - it has not faded), two holes (bullets stopped): a funnel,
  turned-out fibres, soot; a couple of brown stains.

Design decisions: the 'dayz' look (matte, dirtier, dust and dirt in crevices, greasy marks, corner
shading in the colour at baking); smooth details instead of angular ones:
- plate: corners R 9 with 6 points instead of 4, an edge chamfer under the paint (highlight along the
  edge, chips down to titanium), a dent is a shallow dish plus a sharp bowl from the bullet nose, more
  rings of points - the dents read by shape, not as one patch of the decal;
- aramid: the end is rings - a shoulder at the top (the fabric at the edge is not cut off), two bands of
  bulged layers below, shifted (cut with a knife - the layers stick out unevenly); at the front right
  corner the three top layers have come off and bent back (you see it is a pack of layers, not a
  sponge), fresh lower fabric under them; the stitching of the original edge is pressed in as a groove;
- claw furrows: steep walls, a wider bottom, 8 points along and 5 across;
- holes are round (12 points) with a roll of turned-out fibres round them; one holds a PM bullet - the
  base of a tombac jacket with grey lead in the middle;
- the band is not a block: a rounded strap that smoothly goes round the aramid edge and the plate edge,
  narrower on free spans; the tag is card with a bent free end.
No vanilla proxies: the sample itself is a small item in the hands and in the inventory, DayZ has no
armour, plates or aramid items, and a tool or tape on the sample would be out of place. No work view: it
is not a station (no states, lamps or moving parts).

Details: a tag with a grey stripe and a number in digits, a stamped number on the plate, the stitching
of the pack. LODs (small item, 0.3-1.5k): near 1482, mid 588 (40 %), no far LOD. Furrows, holes and
dents at the near LOD are geometry (point triangulation, CDT), fibres and splashes are relief in _nohq.

Blender axes: X is width, Y is depth (the front faces -Y), Z is up. The origin is the centre under the
stack, on the floor; the stack lies, autocenter = 0. The inventory camera (invView) is front-above: the
long side of the plate runs away from the camera, and the item fits the square of the 2x2 cell (the
ratio is printed at build time).
"""
import math
import os
import random
import sys

import bmesh
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import m53_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# dent_rings - rings of dent points on the face: (count, share of the radius, shift around the circle);
# bot_rings - on the back; kv_rings - the aramid end: "full" (top edge, shoulder, two bands, bottom) or
# "mid" (edge, band, bottom)
LOD_SPECS = [
    dict(lod=0, kv_detail=1, fur_st=8, fur_walls=True, lips=True, holes=True, hole_n=11, rim_n=8, band_st=7,
         ramp=True, fill=0.025, pl_corner=5, dent_rings=((7, 0.40, 0.2), (8, 0.72, 0.0), (9, 1.02, 0.15)),
         bot_rings=((5, 0.45, 0.5),), kv_rings="full", flap=True, seam=True, bullet=True,
         band_seg=(3, 1, 1), band_prof=6, tag_detail=1),
    dict(lod=1, kv_detail=1, fur_st=5, fur_walls=False, lips=True, holes=True, hole_n=6, rim_n=0, band_st=4,
         ramp=False, fill=0.028, pl_corner=3, dent_rings=((5, 0.55, 0.0),), bot_rings=(), kv_rings="mid",
         flap=False, seam=False, bullet=False, band_seg=(2, 0, 0), band_prof=4, tag_detail=0),
]

REGIONS = {
    "plate": ("plate", 1.0), "plate_edge": ("plate_edge", 0.8), "plate_bot": ("plate_bot", 0.6),
    "kev_top": ("kev_top", 1.25), "kev_side": ("kev_side", 1.6), "kev_bot": ("kev_bot", 0.3),
    "kev_under": ("kev_under", 1.2), "band": ("band", 0.9), "band_low": ("band", 0.5), "tag": ("tag", 1.8),
    "bullet": ("bullet", 2.0),
}
# furrow walls steeper than 45 degrees go into the atlas as side rectangles: each furrow has its own
# (otherwise the walls of neighbouring furrows share the same texels), the material is the same aramid
# top
for _k in range(len(L.FURROWS)):
    REGIONS["kev_fur%d" % _k] = ("kev_top", 1.25)

PAINT = kmats.lin((60, 63, 64))
PAINT_DARK = kmats.lin((45, 47, 49))
PAINT_WORN = kmats.lin((80, 80, 77))        # paint rubbed to a thin layer - lighter and warmer
PRIMER = kmats.lin((38, 38, 37))            # chip rim - the paint thickness
TI = kmats.lin((112, 111, 107))             # titanium VT-14: darker and warmer than steel
TI_BRIGHT = kmats.lin((146, 145, 140))      # fresh scratches down to the metal
KEV = kmats.lin((184, 138, 58))
KEV_DARK = kmats.lin((140, 98, 40))
KEV_AGED = kmats.lin((158, 124, 74))        # the top has aged in light and dirt: brownish, dull
KEV_FRESH = kmats.lin((200, 154, 62))       # lower layers (under the peeled corner) have not faded
FUZZ = kmats.lin((224, 204, 146))
RUBBER = kmats.lin((28, 28, 29))
TALC = kmats.lin((96, 96, 94))
MANILA = kmats.lin((198, 172, 122))
TOMBAC = kmats.lin((118, 86, 56))           # bullet jacket tombac, darkened, in soot
LEAD = kmats.lin((70, 71, 74))


def wdecal(name):
    return os.path.join(WORK, name)


# --- materials: pattern at the scale of the item (a 15 cm stack) ------------------------------------
def small(t, origin, seed, k=20.0):
    vec, sep = t.coords(origin, seed)
    return t.stretch(vec, k, k, k), sep


def scratches(t, vec, amount=1.0, k=1.0):
    """Thin scratches: isolines of stretched noise in two directions, masked by sparse fields."""
    out = None
    for st, sc, ms in (((1.0, 1.0, 0.22), 2.6 * k, 1.4), ((0.25, 0.25, 1.0), 2.1 * k, 2.4)):
        n = t.noise(t.stretch(vec, *st), sc, 2.0, 0.5)
        line = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", n, 0.5)), 0.0, 0.0035, 1.0, 0.0)
        mask = t.maprange(t.noise(vec, ms, 3.0, 0.5), 0.58, 0.72, 0.0, 1.0)
        s = t.math("MULTIPLY", line, mask)
        out = s if out is None else t.math("MAXIMUM", out, s)
    return t.math("MULTIPLY", out, amount)


def overlay(t, sep, name, center, size):
    """Decal (colour, alpha) and its relief (alpha _h, 0.5 is flat) in world x, y."""
    x, y = sep.outputs["X"], sep.outputs["Y"]
    c, a = t.image(wdecal(name + ".png"), x, y, center, size)
    _, ha = t.image(wdecal(name + "_h.png"), x, y, center, size)
    return c, a, t.math("SUBTRACT", ha, 0.5)


def finish(t, col, gl, vec, nsep, cav_k=0.5, dust_k=0.16, smudge=0.0, cav_d=0.004):
    """'dayz' profile wear at the scale of the item (kmats.weather is sized for stations in metres):
    dirt in crevices and corners (AO 4 mm), dust on what faces up, greasy hand marks; the colour is
    muted like kmats.dayz_layers (the patina of the profile). -> (colour, gloss, dirt strength in
    crevices).
    """
    cav = t.maprange(t.cavity(cav_d), 0.15, 0.6, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, cav_k), col, kmats.GRIME)
    up = t.maprange(nsep.outputs["Z"], 0.4, 0.9, 0.0, 1.0)
    dust = t.math("MULTIPLY", t.math("MULTIPLY", up, t.maprange(t.noise(vec, 2.2, 4.0, 0.6), 0.35, 0.75, 0.0, 1.0)),
                  dust_k)
    col = t.mixc(dust, col, kmats.DUST)
    sm = None
    if smudge > 0:
        sm = t.math("MULTIPLY", t.step(t.noise(vec, 1.3, 4.0, 0.55), 0.63, 0.73), smudge)
        col = t.mixc(sm, col, kmats.lin((34, 31, 27)))
    if kmats.LOOK["name"] == "dayz":
        d, v = kmats.LOOK["patina"]
        gray = t.node("ShaderNodeRGBToBW")
        t.link(col, gray.inputs[0])
        col = t.mixc(d, col, gray.outputs[0])
        col = t.mixc(1.0 - v, col, (0, 0, 0, 1))
    gl = t.math("SUBTRACT", gl, t.math("ADD", t.math("MULTIPLY", cav, 0.15), t.math("MULTIPLY", dust, 0.6)))
    if sm is not None:
        gl = t.math("ADD", gl, t.math("MULTIPLY", sm, 0.25))        # grease - slightly glossy
    return col, gl, cav


def mat_plate(mat, origin, face="top", seed=1.0):
    """Titanium plate under dark grey paint: the paint is blotchy and worn to a thin layer in places,
    chips down to the metal with a dark rim along the edge and chamfer, fine scratches; on the face,
    bullet and claw marks (decal); on the back the paint has cracked and flaked off at the bulges. Matte
    ('dayz' look).
    """
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, seed)
    nsep = t.normal()
    x, y = sep.outputs["X"], sep.outputs["Y"]
    col = t.mixc(t.maprange(t.noise(vec, 1.6, 6.0, 0.6), 0.3, 0.75, 0.0, 1.0), PAINT_DARK, PAINT)
    col = t.mixc(t.maprange(t.noise(vec, 0.8, 4.0, 0.55), 0.56, 0.76, 0.0, 0.28), col, PAINT_WORN)
    edge = t.maprange(t.edge_wear(0.0007), 0.05, 0.30, 0.0, 1.0)
    chips = t.noise(vec, 7.0, 6.0, 0.6)
    ek = 0.70 if face == "edge" else 0.55
    f = t.math("ADD", t.math("MULTIPLY", edge, ek), t.math("MULTIPLY", chips, 0.5))
    lo = 0.64 if face == "edge" else 0.70
    bare = t.step(f, lo, lo + 0.03)
    rim = t.math("SUBTRACT", t.step(f, lo - 0.05, lo), bare)
    if face == "bot":
        # bulges on the back: the paint cracked and flaked off round the apex
        for dx, dy, r, dep in L.DENTS:
            d = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", t.math("SUBTRACT", x, dx), t.math("SUBTRACT", x, dx)),
                                      t.math("MULTIPLY", t.math("SUBTRACT", y, dy), t.math("SUBTRACT", y, dy))))
            ring = t.maprange(d, r * 0.55, r * 0.15, 0.0, 1.0)
            fl = t.step(t.noise(vec, 14.0, 4.0, 0.6), 0.45, 0.52)
            bare = t.math("MAXIMUM", bare, t.math("MULTIPLY", ring, fl))
    metal = t.mixc(t.maprange(t.noise(vec, 3.0, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0), TI, kmats.lin((128, 127, 122)))
    col = t.mixc(t.math("MULTIPLY", rim, 0.7), col, PRIMER)
    col = t.mixc(bare, col, metal)
    h = t.math("SUBTRACT", t.math("MULTIPLY", t.math("SUBTRACT", 1.0, bare), 0.25), t.math("MULTIPLY", rim, 0.08))
    scr = scratches(t, small(t, origin, seed + 4.7)[0], 0.35)
    col = t.mixc(t.math("MULTIPLY", scr, 0.45), col, TI_BRIGHT)
    h = t.math("SUBTRACT", h, t.math("MULTIPLY", scr, 0.2))
    # paint grain - fine relief
    h = t.math("ADD", h, t.math("MULTIPLY", t.noise(vec, 55.0, 2.0, 0.5), 0.05))
    mark = None
    if face == "top":
        c, a, hd = overlay(t, sep, "decal_plate", (0.0, 0.0), (L.PL_X + 0.004, L.PL_Y + 0.004))
        # the decal was drawn for the v1 look: the claw scratches on it are almost white and the tombac
        # orange; here the scratches are old and dirty - duller, the tombac and lead muted
        gray = t.node("ShaderNodeRGBToBW")
        t.link(c, gray.inputs[0])
        c = t.mixc(0.17, t.mixc(0.40, c, gray.outputs[0]), (0, 0, 0, 1))
        col = t.mixc(a, col, c)
        h = t.math("ADD", h, t.math("MULTIPLY", hd, 1.6))
        mark = a
    # gloss: the paint is matte, metal and lead are semi-matte
    gl = t.math("ADD", t.mixf(bare, 0.24, 0.46), t.math("MULTIPLY", scr, 0.15))
    sp = t.math("ADD", t.mixf(bare, 0.18, 0.55), t.math("MULTIPLY", scr, 0.2))
    if mark is not None:
        gl = t.mixf(t.math("MULTIPLY", mark, 0.6), gl, 0.32)
        sp = t.mixf(t.math("MULTIPLY", mark, 0.6), sp, 0.30)
    col, gl, cav = finish(t, col, gl, vec, nsep, cav_k=0.55, dust_k=0.20 if face == "top" else 0.08,
                          smudge=0.30 if face == "top" else 0.15)
    sp = t.math("SUBTRACT", sp, t.math("MULTIPLY", cav, 0.10))
    return kmats.out(t, col, gl, sp, h)


def kv_local(t, sep):
    """Axes of the aramid piece (rotated by KV_ROT): u across, v along."""
    a = math.radians(-L.KV_ROT)
    x = t.math("SUBTRACT", sep.outputs["X"], L.KV_C[0])
    y = t.math("SUBTRACT", sep.outputs["Y"], L.KV_C[1])
    u = t.math("SUBTRACT", t.math("MULTIPLY", x, math.cos(a)), t.math("MULTIPLY", y, math.sin(a)))
    v = t.math("ADD", t.math("MULTIPLY", x, math.sin(a)), t.math("MULTIPLY", y, math.cos(a)))
    return u, v


def weave(t, u, v, pitch=0.0018):
    """TSVM-DZh plain weave: a grid of thread ridges along u and along v with a 1.8 mm repeat - 3-4
    texels on the 512 atlas, no moire; -0.5..0.5. (A product of sines gave slanted ribs like corduroy
    under raking light.)
    """
    ru = t.math("ABSOLUTE", t.math("SINE", t.math("MULTIPLY", u, math.pi / pitch)))
    rv = t.math("ABSOLUTE", t.math("SINE", t.math("MULTIPLY", v, math.pi / pitch)))
    return t.math("SUBTRACT", t.math("MULTIPLY", t.math("ADD", ru, rv), 0.5), 0.5)


def mat_kevlar(mat, origin, face="top", seed=3.0):
    """Aramid fabric: yellow-brown; aged on top (brownish, dull), folds and weave, a decal (furrows,
    holes, stitching, stains); the end is bundles of layers with dark gaps and light tips of cut fibres;
    under is the lower layer exposed by the peeled corner: brighter, cleaner; dirt in folds, dust on
    top. Matte, with a barely visible silky gloss.
    """
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, seed)
    nsep = t.normal()
    z = sep.outputs["Z"]
    u, v = kv_local(t, sep)
    col = t.mixc(t.maprange(t.noise(vec, 1.3, 6.0, 0.6), 0.3, 0.75, 0.0, 1.0), KEV_DARK, KEV)
    fibre = t.noise(vec, 40.0, 3.0, 0.5)
    h = t.math("MULTIPLY", t.math("SUBTRACT", fibre, 0.5), 0.2)
    fresh = 0.0
    if face == "top":
        col = t.mixc(t.maprange(t.noise(vec, 0.9, 4.0, 0.5), 0.25, 0.75, 0.15, 0.78), col, KEV_AGED)
        crease = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", t.noise(t.stretch(vec, 1.0, 0.35, 1.0), 1.1, 2.0, 0.5), 0.5)),
                            0.0, 0.05, 1.0, 0.0)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", crease, 0.35))
        col = t.mixc(t.math("MULTIPLY", crease, 0.22), col, KEV_DARK)
        wv = weave(t, u, v)
        col = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", 0.5, wv), 0.06), col, KEV_DARK)
        h = t.math("ADD", h, t.math("MULTIPLY", wv, 0.07))
        c, a, hd = overlay(t, sep, "decal_kev", L.KV_C, (L.KV_BOX, L.KV_BOX))
        col = t.mixc(a, col, c)
        h = t.math("ADD", h, t.math("MULTIPLY", hd, 2.2))
        fresh = a
    elif face == "under":
        col = t.mixc(0.55, col, KEV_FRESH)
        wv = weave(t, u, v)
        col = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", 0.5, wv), 0.07), col, KEV_DARK)
        h = t.math("ADD", h, t.math("MULTIPLY", wv, 0.09))
        fresh = 0.6
    elif face == "side":
        # layers: in bundles of ~4 (a 1.05 mm repeat - visible on the atlas), wavy bundles, dark gaps;
        # thin gaps between layers - barely
        zz = t.math("ADD", z, t.math("MULTIPLY", t.math("SUBTRACT", t.noise(vec, 2.0, 3.0, 0.5), 0.5), 0.0016))
        ph = t.math("FRACT", t.math("DIVIDE", t.math("SUBTRACT", zz, L.KV_Z0), 0.00105))
        gap = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", ph, 0.5)), 0.33, 0.5, 0.0, 1.0)
        gap = t.math("MULTIPLY", gap, t.maprange(t.noise(vec, 6.0, 3.0, 0.5), 0.3, 0.6, 0.45, 1.0))
        col = t.mixc(t.math("MULTIPLY", gap, 0.8), col, kmats.lin((66, 46, 20)))
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", gap, 0.6))
        ph2 = t.math("FRACT", t.math("DIVIDE", t.math("SUBTRACT", zz, L.KV_Z0), 0.00026))
        thin = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", ph2, 0.5)), 0.40, 0.5, 0.0, 0.25)
        col = t.mixc(thin, col, KEV_DARK)
        # cut: light fibre tips stick out, more on the upper layers
        fz = t.step(t.noise(t.stretch(vec, 1.0, 1.0, 0.15), 30.0, 3.0, 0.6), 0.66, 0.73)
        col = t.mixc(t.math("MULTIPLY", fz, 0.38), col, FUZZ)
        h = t.math("ADD", h, t.math("MULTIPLY", fz, 0.3))
    col, gl0, cav = finish(t, col, 0.0, vec, nsep, cav_k=0.5, dust_k=0.18 if face == "top" else 0.05,
                           smudge=0.30 if face == "top" else 0.0)
    # silky gloss of aramid is barely there; dirt, dust and soot are matte
    gl = t.math("ADD", t.mixf(fresh, 0.32, 0.26), gl0)
    sp = t.math("SUBTRACT", 0.20, t.math("MULTIPLY", cav, 0.12))
    return kmats.out(t, col, gl, sp, h)


def mat_rubber(mat, origin, seed=6.0):
    """Rubber band from a bicycle tube: black, a talc bloom, small cracks at the bends, worn edges."""
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, seed, 30.0)
    nsep = t.normal()
    talc = t.maprange(t.noise(vec, 1.5, 4.0, 0.6), 0.4, 0.8, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", talc, 0.35), RUBBER, TALC)
    edge = t.maprange(t.edge_wear(0.0004), 0.05, 0.30, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.30), col, kmats.lin((72, 72, 70)))
    # cracks of old rubber - short, across the strip and only in places (solid noise isolines looked
    # like drawn contour lines)
    crk = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", t.noise(t.stretch(vec, 1.0, 0.2, 1.0), 6.0, 2.0, 0.5), 0.5)),
                     0.0, 0.006, 1.0, 0.0)
    crk = t.math("MULTIPLY", crk, t.maprange(t.noise(vec, 2.2, 3.0, 0.5), 0.56, 0.70, 0.0, 1.0))
    col = t.mixc(t.math("MULTIPLY", crk, 0.35), col, kmats.lin((12, 12, 12)))
    h = t.math("SUBTRACT", t.math("MULTIPLY", t.noise(vec, 8.0, 3.0, 0.5), 0.1), t.math("MULTIPLY", crk, 0.3))
    col, gl, cav = finish(t, col, t.math("SUBTRACT", 0.20, t.math("MULTIPLY", talc, 0.10)), vec, nsep,
                          cav_k=0.3, dust_k=0.20)
    return kmats.out(t, col, gl, 0.10, h)


def mat_tag(mat, origin, seed=7.0):
    """Tag: manila card, paper fibres, a decal (stripe, fields, number, eyelet), handled and dirty at
    the edges, matte.
    """
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, seed, 30.0)
    nsep = t.normal()
    col = t.mixc(t.math("MULTIPLY", t.maprange(t.noise(vec, 6.0, 4.0, 0.6), 0.35, 0.75, 0.0, 1.0), 0.25),
                 MANILA, kmats.lin((190, 164, 116)))
    tcx, tcy = L.tag_center()
    c, a = t.image(wdecal("decal_tag.png"), sep.outputs["X"], sep.outputs["Y"], (tcx, tcy), (L.TAG_BOX, L.TAG_BOX))
    col = t.mixc(a, col, c)
    edge = t.maprange(t.edge_wear(0.0005), 0.05, 0.30, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.35), col, kmats.lin((120, 100, 70)))
    h = t.math("MULTIPLY", t.noise(vec, 12.0, 3.0, 0.5), 0.08)
    col, gl, cav = finish(t, col, 0.12, vec, nsep, cav_k=0.4, dust_k=0.10, smudge=0.22)
    return kmats.out(t, col, gl, 0.06, h)


def mat_bullet(mat, origin, seed=8.0):
    """Base of a PM bullet stuck in the pack: the tombac jacket has darkened, grey lead in the middle,
    lint and soot at the edge.
    """
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, seed, 30.0)
    nsep = t.normal()
    hx, hy, _ = L.HOLES[L.BULLET["hole"]]
    dx, dy = t.math("SUBTRACT", sep.outputs["X"], hx), t.math("SUBTRACT", sep.outputs["Y"], hy)
    d = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", dx, dx), t.math("MULTIPLY", dy, dy)))
    core = t.maprange(d, L.BULLET["r"] * 0.42, L.BULLET["r"] * 0.30, 0.0, 1.0)
    col = t.mixc(t.maprange(t.noise(vec, 4.0, 4.0, 0.6), 0.3, 0.7, 0.0, 1.0), kmats.lin((88, 64, 42)), TOMBAC)
    col = t.mixc(core, col, LEAD)
    soot = t.maprange(d, L.BULLET["r"] * 0.45, L.BULLET["r"] * 0.85, 0.15, 0.6)
    col = t.mixc(soot, col, kmats.lin((46, 40, 32)))
    col, gl, cav = finish(t, col, 0.32, vec, nsep, cav_k=0.3, dust_k=0.05)
    sp = t.math("SUBTRACT", 0.36, t.math("MULTIPLY", soot, 0.3))
    return kmats.out(t, col, gl, sp, t.math("MULTIPLY", t.noise(vec, 20.0, 3.0, 0.5), 0.1))


KINDS = {
    "plate": (mat_plate, dict(face="top")),
    "plate_edge": (mat_plate, dict(face="edge", seed=1.4)),
    "plate_bot": (mat_plate, dict(face="bot", seed=1.8)),
    "kev_top": (mat_kevlar, dict(face="top")),
    "kev_side": (mat_kevlar, dict(face="side", seed=3.6)),
    "kev_bot": (mat_kevlar, dict(face="bot", seed=4.1)),
    "kev_under": (mat_kevlar, dict(face="under", seed=4.6)),
    "band": (mat_rubber, {}),
    "tag": (mat_tag, {}),
    "bullet": (mat_bullet, {}),
}

OBJ, NAME = "m53_prot_sample", "ozr_prot_sample"
# 'dayz' look: the rvmat comes from the profile (specular 1.0, power 80), kbake recomputes the highlight
# and gloss _smdi; a custom rvmat (0.35 / 40) would not show up in the preview - kmats.wire takes the
# specular of the profile
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=512, look="dayz")
P = M.part
BOUNDS = {}


# --- geometry ------------------------------------------------------------------------------------
def cdt(outline, inner, cons=(), gcons=()):
    """Constrained Delaunay triangulation: an outline (counter-clockwise) + inner points; cons - pairs
    of indices into inner, gcons - pairs of global indices (outline 0..n-1, then inner). -> (points,
    counter-clockwise triangles, point number by input number).
    """
    pts = [Vector(p[:2]) for p in list(outline) + list(inner)]
    n = len(outline)
    edges = [(i, (i + 1) % n) for i in range(n)] + [(n + a, n + b) for a, b in cons] + list(gcons)
    vs, _, fs, ov, _, _ = delaunay_2d_cdt(pts, edges, [], 0, 1e-7)
    vmap = {}
    for i, orig in enumerate(ov):
        for o in orig:
            vmap[o] = i
    assert len(vs) == len(pts), "CDT added points: constraints intersect (%d -> %d)" % (len(pts), len(vs))
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
    return [(v.x, v.y) for v in vs], tris, vmap


def surface(p, region, pts, tris, zf, up=True):
    """Surface from a triangulation: z = zf(x, y); faces up (up) or down. -> (vertices, faces)."""
    p.use(region, *REGIONS[region])
    bv = [p.bm.verts.new((x, y, zf(x, y))) for x, y in pts]
    faces = []
    for a, b, c in tris:
        faces.append(p.bm.faces.new((bv[a], bv[b], bv[c]) if up else (bv[a], bv[c], bv[b])))
    p.tag(faces)
    return bv, faces


def walls(p, regions, rings):
    """Side walls between vertex rings (top to bottom), the rings follow the outline counter-clockwise;
    regions - the region of each band (or one for all).
    """
    if isinstance(regions, str):
        regions = [regions] * (len(rings) - 1)
    for reg, A, B in zip(regions, rings, rings[1:]):
        p.use(reg, *REGIONS[reg])
        faces = []
        n = len(A)
        for i in range(n):
            j = (i + 1) % n
            faces.append(p.bm.faces.new((A[i], B[i], B[j], A[j])))
        p.tag(faces)


def retag(p, faces, region):
    idx = p.region_index(region, *REGIONS[region])
    for f in faces:
        f[p.reg] = idx


def outward(poly, i):
    """Outline normal (counter-clockwise) outwards at vertex i - the mean of the neighbouring edges."""
    n = len(poly)
    (x0, y0), (x1, y1), (x2, y2) = poly[i - 1], poly[i], poly[(i + 1) % n]
    ax, ay = x1 - x0, y1 - y0
    bx, by = x2 - x1, y2 - y1
    la, lb = math.hypot(ax, ay), math.hypot(bx, by)
    nx, ny = ay / la + by / lb, -ax / la - bx / lb
    ln = math.hypot(nx, ny)
    return nx / ln, ny / ln


def inset(poly, nrm, d):
    return [(x - ox * d, y - oy * d) for (x, y), (ox, oy) in zip(poly, nrm)]


def fill_grid(poly, step, keep):
    """Grid points inside the outline (no closer than 0.6 step to the edge) where keep(x, y)."""
    out = []
    xs = [q[0] for q in poly]
    ys = [q[1] for q in poly]
    nx = int((max(xs) - min(xs)) / step)
    ny = int((max(ys) - min(ys)) / step)
    for i in range(1, nx + 1):
        for j in range(1, ny + 1):
            x = min(xs) + (max(xs) - min(xs)) * i / (nx + 1)
            y = min(ys) + (max(ys) - min(ys)) * j / (ny + 1)
            if L.inside(poly, x, y) and L.edge_dist(poly, x, y) > step * 0.6 and keep(x, y):
                out.append((x, y))
    return out


def poly_x_at(poly, y):
    """Outline crossings with the line y = const -> (min x, max x)."""
    xs = []
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        if (y0 > y) != (y1 > y):
            xs.append(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
    return min(xs), max(xs)


# --- aramid: the peeled corner -------------------------------------------------------------------
def flap_cut(poly):
    """Fold line of the peeled layers at the front right corner: a straight line through points at the
    front and at the right side (L.FLAP) cuts the outline in two places - the points are inserted into
    the outline. -> (outline, dict(A, nh - the fold normal towards the corner, iA, iB, corner - the
    outline point numbers beyond the fold)).
    """
    F = L.FLAP
    A = Vector(L.kv_world(L.KV_A - F["front"], -L.KV_B))
    B = Vector(L.kv_world(L.KV_A, -L.KV_B + F["side"]))
    C = Vector(L.kv_world(L.KV_A, -L.KV_B))
    d = (B - A).normalized()
    nh = Vector((d.y, -d.x))
    if nh.dot(C - A) < 0:
        nh = -nh
    hits = []
    n = len(poly)
    for i in range(n):
        p, q = Vector(poly[i]), Vector(poly[(i + 1) % n])
        sp, sq = (p - A).dot(nh), (q - A).dot(nh)
        if (sp > 0) != (sq > 0):
            hits.append((i, p + (q - p) * (sp / (sp - sq))))
    assert len(hits) == 2, "the corner fold does not cut the outline in two places: %d" % len(hits)
    out = [tuple(v) for v in poly]
    for i, pt in sorted(hits, key=lambda h: -h[0]):
        out.insert(i + 1, (pt.x, pt.y))
    ins = sorted(h[0] for h in hits)
    i1, i2 = ins[0] + 1, ins[1] + 2
    corner = [k for k in range(len(out)) if (Vector(out[k]) - A).dot(nh) > 1e-9]
    assert corner == list(range(i1 + 1, i2)), "corner points are not consecutive: %s" % corner
    return out, dict(A=A, nh=nh, iA=i1, iB=i2, corner=corner)


def flap_recess(fl):
    """Recess under the peeled layers: beyond the fold the top is lower by the thickness of three
    layers.
    """
    A, nh, t = fl["A"], fl["nh"], L.FLAP["t"]

    def f(x, y):
        s = (Vector((x, y)) - A).dot(nh)
        return -t * L.smooth(s / 0.0008) if s > 0 else 0.0
    return f


def build_flap(poly, fl, z_hinge):
    """The three peeled layers: a sheet of FLAP t thickness over the corner outline beyond the fold,
    raised at the fold by a0 and curled towards the tip up to a1; the top is the aramid top (decal by
    world x, y), the bottom is fresh lower fabric, the edges are the layered end.
    """
    F = L.FLAP
    A, nh = fl["A"], fl["nh"]
    bnd = [Vector(poly[k]) for k in [fl["iA"]] + fl["corner"] + [fl["iB"]]]
    smax = max((p - A).dot(nh) for p in bnd)
    hm = (bnd[0] + bnd[-1]) / 2
    inner = [hm + nh * (smax * f) for f in (0.35, 0.70)]
    inner = [q for q in inner if L.inside([tuple(b) for b in bnd], q.x, q.y)]
    pts2, tris, vmap = cdt([tuple(b) for b in bnd], [tuple(q) for q in inner])
    steps = 24

    def lift(s):
        """(along from the fold, up, sheet angle) at distance s from the fold."""
        X = Z = 0.0
        th = math.radians(F["a0"])
        for k in range(steps):
            sm = s * (k + 0.5) / steps
            th = math.radians(F["a0"] + (F["a1"] - F["a0"]) * (sm / smax) ** 1.3)
            X += math.cos(th) * s / steps
            Z += math.sin(th) * s / steps
        return X, Z, th
    fp = P("kev_flap", "kev_top")
    bm = fp.bm
    top, bot = [], []
    for x, y in pts2:
        q = Vector((x, y))
        s = max(0.0, (q - A).dot(nh))
        foot = q - nh * s
        X, Z, th = lift(s)
        base = foot + nh * X
        zb = z_hinge(foot.x, foot.y) - F["t"] + Z
        nrm = (-math.sin(th) * nh.x, -math.sin(th) * nh.y, math.cos(th))
        bot.append(bm.verts.new((base.x, base.y, zb)))
        top.append(bm.verts.new((base.x + nrm[0] * F["t"], base.y + nrm[1] * F["t"], zb + nrm[2] * F["t"])))
    fp.use("kev_top", *REGIONS["kev_top"])
    fp.tag([bm.faces.new((top[a], top[b], top[c])) for a, b, c in tris])
    fp.use("kev_under", *REGIONS["kev_under"])
    fp.tag([bm.faces.new((bot[a], bot[c], bot[b])) for a, b, c in tris])
    nb = len(bnd)
    ring = [vmap[i] for i in range(nb)]
    fp.use("kev_side", *REGIONS["kev_side"])
    side = []
    for i in range(nb):
        a, b = ring[i], ring[(i + 1) % nb]
        side.append(bm.faces.new((top[a], bot[a], bot[b], top[b])))
    fp.tag(side)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    return fp


# --- aramid -------------------------------------------------------------------------------------
def build_kevlar(spec):
    """A piece of the pack: the top is a pillow over points (edge, stitching, furrows, holes, pressing
    by the band and tag, a recess under the peeled corner), the end is rings (a shoulder at the top, two
    bands of bulged layers, shifted), the bottom lies on the plate; separate: the peeled layers of the
    corner and a bullet in a hole.
    """
    rnd = random.Random(5301)
    poly = L.kv_outline(spec["kv_detail"])
    fl = None
    if spec["flap"]:
        poly, fl = flap_cut(poly)
    n = len(poly)
    nrm = [outward(poly, i) for i in range(n)]
    s_top, s_sh, s_drop = L.KV_SHOULDER if spec["kv_rings"] == "full" else (0.0010, 0.0, 0.0)
    poly_top = inset(poly, nrm, s_top)
    poly_bot = inset(poly, nrm, 0.0004)
    inner, cons, gcons, feats = [], [], [], []

    def add(x, y):
        inner.append((x, y))
        return len(inner) - 1
    for (ax, ay), (bx, by) in L.FURROWS:
        feats.append(("seg", (ax, ay, bx, by), 0.006))
    for hx, hy, r in L.HOLES:
        feats.append(("pt", (hx, hy), r * 1.25 + 0.005))
    # the tag pressed the aramid down: its outline is a constraint, everything inside follows its bottom
    foot = L.tag_footprint(spec["tag_detail"])
    fi = [add(x, y) for x, y in foot]
    cons += list(zip(fi, fi[1:] + fi[:1]))
    feats.append(("poly", foot, 0.003))
    if spec["fur_st"]:
        st = spec["fur_st"]
        for k, ((ax, ay), (bx, by)) in enumerate(L.FURROWS):
            dx, dy = bx - ax, by - ay
            ln = math.hypot(dx, dy)
            nx, ny = -dy / ln, dx / ln
            mid = []
            for i in range(st):
                j = rnd.uniform(-0.0003, 0.0003) if 0 < i < st - 1 else 0.0
                mid.append(add(ax + dx * i / (st - 1) + nx * j, ay + dy * i / (st - 1) + ny * j))
            cons += list(zip(mid, mid[1:]))
            chains = []
            if spec["fur_walls"]:
                chains.append(lambda hw: 0.62 * hw)                    # bottom of a steep wall
            if spec["lips"]:
                chains.append(lambda hw: hw + 0.0008)                  # frayed edge
            for off in chains:
                for sg in (1, -1):
                    lip = []
                    for i in range(1, st - 1):
                        tt = i / (st - 1)
                        _, hw = L.furrow_profile(k, tt)
                        o = sg * (off(hw) + rnd.uniform(-0.0003, 0.0003))
                        lip.append(add(ax + dx * tt + nx * o, ay + dy * tt + ny * o))
                    chain = [mid[0]] + lip + [mid[-1]]
                    cons += list(zip(chain, chain[1:]))
    if spec["holes"]:
        for hx, hy, r in L.HOLES:
            add(hx, hy)
            nh_, nr_ = spec["hole_n"], spec["rim_n"]
            for i in range(nh_):
                a = 2 * math.pi * (i + 0.3) / nh_
                rr = r * (0.85 + rnd.uniform(-0.06, 0.06))
                add(hx + rr * math.cos(a), hy + rr * math.sin(a))
            for i in range(nr_):
                a = 2 * math.pi * (i + 0.1) / nr_
                rr = r * (L.HOLE_RIM + 1.0) / 2 * (1.0 + rnd.uniform(-0.05, 0.05))
                add(hx + rr * math.cos(a), hy + rr * math.sin(a))
    # band: strip edges (the pressed strip is flat) and, at the near LOD, where the aramid bulges again
    for dy_, is_edge in ((-L.BAND_W / 2, True), (L.BAND_W / 2, True), (-L.BAND_W / 2 - 0.004, False),
                         (L.BAND_W / 2 + 0.004, False)):
        if not is_edge and not spec["ramp"]:
            continue
        y = L.BAND_Y + dy_
        x0, x1 = poly_x_at(poly_top, y)
        st = spec["band_st"] if is_edge else max(3, spec["band_st"] - 3)
        xs = [x0 + 0.0015 + (x1 - x0 - 0.003) * i / (st - 1) for i in range(st)]
        # where the line runs under the tag there is a gap: inside the tag outline everything follows
        # its bottom anyway
        chains = [xs]
        if min(q[1] for q in foot) < y < max(q[1] for q in foot):
            xa, xb = poly_x_at(foot, y)
            chains = [[x for x in xs if x < xa - 0.0025] + [xa - 0.0006],
                      [xb + 0.0006] + [x for x in xs if x > xb + 0.0025]]
        for ch in chains:
            line = [add(x, y) for x in ch if not L.inside(foot, x, y)]
            if is_edge:
                cons += list(zip(line, line[1:]))
    feats.append(("band", None, L.BAND_W / 2 + 0.006))
    if spec["seam"]:
        # stitching of the original edge is pressed in: a chain of points along the stitch line, a gap
        # under the band
        lx = -L.KV_A + L.SEAM_IN
        prev = None
        nseam = 10
        for i in range(nseam):
            ly = -L.KV_B + 0.004 + (2 * L.KV_B - 0.008) * i / (nseam - 1)
            x, y = L.kv_world(lx, ly)
            if abs(y - L.BAND_Y) < L.BAND_W / 2 + 0.005:
                prev = None
                continue
            k = add(x, y)
            if prev is not None:
                cons.append((prev, k))
            prev = k
        feats.append(("seam", lx, 0.0035))
    if fl is not None:
        # fold: the middle is a point, the ends are outline points; beyond the fold a pair of points so
        # that the recess is a step
        A, nh = fl["A"], fl["nh"]
        pa, pb = Vector(poly_top[fl["iA"]]), Vector(poly_top[fl["iB"]])
        m = add(*((pa + pb) / 2))
        gcons += [(fl["iA"], n + m), (n + m, fl["iB"])]
        for f in (0.3, 0.7):
            q = pa + (pb - pa) * f + nh * 0.0012
            if L.inside(poly_top, q.x, q.y):
                add(q.x, q.y)
        feats.append(("flap", None, 0.003))

    def keep(x, y):
        for kind, a, r in feats:
            if kind == "seg" and L.seg_dist(x, y, *a)[0] < r:
                return False
            if kind == "pt" and math.hypot(x - a[0], y - a[1]) < r:
                return False
            if kind == "band" and abs(y - L.BAND_Y) < r:
                return False
            if kind == "poly" and (L.inside(a, x, y) or L.edge_dist(a, x, y) < r):
                return False
            if kind == "seam" and abs(L.kv_local(x, y)[0] - a) < r:
                return False
            if kind == "flap" and (Vector((x, y)) - fl["A"]).dot(fl["nh"]) > -r:
                return False
        return True
    inner += fill_grid(poly_top, spec["fill"], keep)
    pts, tris, vmap = cdt(poly_top, inner, cons, gcons)
    kv = P("kevlar", "kev_top")
    extra = flap_recess(fl) if fl is not None else None

    def ztop(x, y):
        return L.kv_top_z(x, y, poly, extra=extra, seam=spec["seam"])
    top, tfaces = surface(kv, "kev_top", pts, tris, ztop)
    # faces: under the peeled corner - fresh lower fabric; steep furrow walls - each furrow gets its own
    # piece of the atlas
    for f in tfaces:
        c = sum((v.co for v in f.verts), Vector()) / 3
        if fl is not None and (Vector((c.x, c.y)) - fl["A"]).dot(fl["nh"]) > 0.0004:
            retag(kv, [f], "kev_under")
            continue
        f.normal_update()
        if abs(f.normal.z) < 0.72:
            for k, ((ax, ay), (bx, by)) in enumerate(L.FURROWS):
                if L.seg_dist(c.x, c.y, ax, ay, bx, by)[0] < L.FUR_HW + 0.003:
                    retag(kv, [f], "kev_fur%d" % k)
                    break
    rings = [[top[vmap[i]] for i in range(n)]]
    regions = []
    z0 = L.KV_Z0
    if spec["kv_rings"] == "full":
        hts = [v.co.z - z0 for v in rings[0]]
        rings.append([kv.bm.verts.new((x, y, z0 + h - s_drop)) for (x, y), h in zip(inset(poly, nrm, s_sh), hts)])
        regions.append("kev_top")
        for f_h, jr in ((0.62, (0.0002, 0.0009)), (0.26, (0.0000, 0.0006))):
            ring = []
            for (x, y), (ox, oy), h in zip(poly, nrm, hts):
                j = rnd.uniform(*jr)
                ring.append(kv.bm.verts.new((x + ox * j, y + oy * j, z0 + f_h * (h - s_drop) + rnd.uniform(-0.0003, 0.0003))))
            rings.append(ring)
            regions.append("kev_side")
    else:
        mid = []
        for (x, y), (ox, oy), v in zip(poly, nrm, rings[0]):
            j = rnd.uniform(0.0004, 0.0013)
            mid.append(kv.bm.verts.new((x + ox * j, y + oy * j, z0 + 0.45 * (v.co.z - z0))))
        rings.append(mid)
        regions.append("kev_side")
    pts_b, tris_b, vmap_b = cdt(poly_bot, [])
    bot, _ = surface(kv, "kev_bot", pts_b, tris_b, lambda x, y: z0, up=False)
    rings.append([bot[vmap_b[i]] for i in range(n)])
    regions.append("kev_side")
    walls(kv, regions, rings)
    bmesh.ops.recalc_face_normals(kv.bm, faces=kv.bm.faces[:])
    kv.bm.normal_update()
    parts = [kv]
    if fl is not None:
        parts.append(build_flap(poly, fl, lambda x, y: L.kv_top_z(x, y, poly, seam=spec["seam"])))
    if spec["bullet"]:
        parts.append(build_bullet(poly))
    return parts, poly


def build_bullet(poly):
    """9x18 PM bullet in hole 0, base up: the jacket edge turned inwards and lead in the middle; the
    lower part is in the fabric. Flattened unevenly - the edge is wavy.
    """
    hx, hy, _ = L.HOLES[L.BULLET["hole"]]
    r = L.BULLET["r"]
    zs = L.kv_cushion_z(hx, hy, poly) - L.BULLET["sink"]
    bl = P("bullet", "bullet")
    bm = bl.bm
    n = 10
    prof = [(0.88, -0.0012), (1.0, -0.0002), (0.70, 0.00022)]
    rings = []
    for f, dz in prof:
        ring = []
        for k in range(n):
            a = 2 * math.pi * k / n
            w = 1.0 + 0.10 * math.sin(3 * a + 0.7) + 0.05 * math.sin(7 * a + 2.1)
            ring.append(bm.verts.new((hx + r * f * w * math.cos(a), hy + r * f * w * math.sin(a), zs + dz)))
        rings.append(ring)
    faces = []
    for A, B in zip(rings, rings[1:]):
        for k in range(n):
            j = (k + 1) % n
            faces.append(bm.faces.new((A[k], A[j], B[j], B[k])))
    c = bm.verts.new((hx, hy, zs + 0.00012))
    for k in range(n):
        faces.append(bm.faces.new((rings[-1][k], rings[-1][(k + 1) % n], c)))
    bl.tag(faces)
    for f in faces:
        f.normal_update()
        cen = f.calc_center_median()
        if f.normal.dot(Vector((cen.x - hx, cen.y - hy, 0.0)) + Vector((0, 0, 0.5 * r))) < 0:
            f.normal_flip()
    bm.normal_update()
    return bl


# --- plate --------------------------------------------------------------------------------------
def plate_outline(seg):
    hx, hy, r = L.PL_X / 2, L.PL_Y / 2, L.PL_R
    pts = []
    for cx, cy, a0 in ((hx - r, -hy + r, -90), (hx - r, hy - r, 0), (-hx + r, hy - r, 90), (-hx + r, -hy + r, 180)):
        for i in range(seg + 1):
            a = math.radians(a0 + 90 * i / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        # midpoints of the long and short sides - so that the bent corner and the dents do not stretch
        # the triangles
        nxt = {-90: [(hx, -hy / 3), (hx, hy / 3)], 0: [(0.0, hy)], 90: [(-hx, hy / 3), (-hx, -hy / 3)],
               180: [(-hx / 2.2, -hy), (hx / 2.2, -hy)]}[a0]
        pts += nxt if seg > 1 else nxt[:1]
    return pts


def build_plate(spec):
    """Plate: face and back over points (dents are a dish and a bowl, bulges on the back; a bent
    corner), a 1.25 mm edge with a chamfer at the face.
    """
    lod = spec["lod"]
    poly = plate_outline(spec["pl_corner"])
    n = len(poly)
    nrm = [outward(poly, i) for i in range(n)]
    ch_h, ch_v = L.PL_CHAMF if lod == 0 else (0.0, 0.0)
    poly_top = inset(poly, nrm, ch_h) if ch_h else poly
    dents = []
    for dx, dy, r, dep in L.DENTS:
        dents.append((dx, dy))
        for cnt, q, a0 in spec["dent_rings"]:
            for i in range(cnt):
                a = 2 * math.pi * (i + a0) / cnt
                dents.append((dx + r * q * math.cos(a), dy + r * q * math.sin(a)))
    fill = fill_grid(poly_top, 0.030, lambda x, y: all(math.hypot(x - d[0], y - d[1]) > d[2] * 1.05 + 0.006
                                                       for d in L.DENTS))
    pts, tris, vmap = cdt(poly_top, dents + fill)
    pl = P("plate", "plate")

    def zt(x, y):
        return L.PL_Z1 + L.warp(x, y) - L.dent_depth(x, y)

    def zb(x, y):
        return L.PL_Z0 + L.warp(x, y) - L.dent_depth(x, y)
    top, _ = surface(pl, "plate", pts, tris, zt)
    rings = [[top[vmap[i]] for i in range(n)]]
    if ch_h:
        rings.append([pl.bm.verts.new((x, y, zt(x, y) - ch_v)) for x, y in poly])
    bdents = []
    for dx, dy, r, dep in L.DENTS:
        bdents.append((dx, dy))
        for cnt, q, a0 in spec["bot_rings"]:
            for i in range(cnt):
                a = 2 * math.pi * (i + a0) / cnt
                bdents.append((dx + r * q * math.cos(a), dy + r * q * math.sin(a)))
    pts_b, tris_b, vmap_b = cdt(poly, bdents)
    bot, _ = surface(pl, "plate_bot", pts_b, tris_b, zb, up=False)
    rings.append([bot[vmap_b[i]] for i in range(n)])
    walls(pl, "plate_edge", rings)
    bmesh.ops.recalc_face_normals(pl.bm, faces=pl.bm.faces[:])
    pl.bm.normal_update()
    return pl


# --- band ---------------------------------------------------------------------------------------
def offset_loop(loop, d):
    """Closed polyline (x, z) clockwise: offset outwards by d (mitred at the corners)."""
    out = []
    n = len(loop)
    for i in range(n):
        (x0, z0), (x1, z1), (x2, z2) = loop[i - 1], loop[i], loop[(i + 1) % n]
        a = Vector((x1 - x0, z1 - z0)).normalized()
        b = Vector((x2 - x1, z2 - z1)).normalized()
        na, nb = Vector((-a.y, a.x)), Vector((-b.y, b.x))
        m = (na + nb).normalized()
        k = max(0.35, m.dot(na))
        out.append((x1 + m.x * d / k, z1 + m.y * d / k))
    return out


def fillet_loop(loop, radii, segs, tags):
    """Closed polyline (x, z): corner i becomes an arc of radius radii[i] of segs[i] segments (0 - the
    corner as it is). tags[i] is the corner tag; -> (points, point tags).
    """
    out, otag = [], []
    n = len(loop)
    for i in range(n):
        p0, p1, p2 = Vector(loop[i - 1]), Vector(loop[i]), Vector(loop[(i + 1) % n])
        r, k = radii[i], segs[i]
        if k <= 0 or r <= 0:
            out.append(p1)
            otag.append(tags[i])
            continue
        a = (p0 - p1).normalized()
        b = (p2 - p1).normalized()
        ang = math.acos(max(-1.0, min(1.0, a.dot(b))))
        d = r / math.tan(ang / 2)
        d = min(d, (p0 - p1).length * 0.45, (p2 - p1).length * 0.45)
        r = d * math.tan(ang / 2)
        t0, t1 = p1 + a * d, p1 + b * d
        c = p1 + (a + b).normalized() * (r / math.sin(ang / 2))
        a0 = math.atan2(t0.y - c.y, t0.x - c.x)
        a1 = math.atan2(t1.y - c.y, t1.x - c.x)
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        for s in range(k + 1):
            aa = a0 + da * s / k
            out.append(Vector((c.x + r * math.cos(aa), c.y + r * math.sin(aa))))
            otag.append(tags[i])
    return [tuple(p) for p in out], otag


def build_band(spec, poly):
    """Rubber band as a ring across the stack: pressed to the top of the aramid, smoothly going round
    its edge, running taut and slanted down to the plate edge, round it and under the plate. The section
    is a strip with rounded edges; on free spans the tension narrows it. The inner side touches the
    aramid and the plate.
    """
    xl = min(poly_x_at(poly, L.BAND_Y + s * L.BAND_W / 2)[0] for s in (-1, 0, 1)) - 0.0004
    xr = max(poly_x_at(poly, L.BAND_Y + s * L.BAND_W / 2)[1] for s in (-1, 0, 1)) + 0.0004
    hx = L.PL_X / 2
    zt = L.BAND_ZIN
    loop = [(xl, zt), (xr, zt), (hx, L.PL_Z1), (hx, L.PL_Z0), (-hx, L.PL_Z0), (-hx, L.PL_Z1)]
    sk, sp, sb = spec["band_seg"]
    pts, tags = fillet_loop(loop, (0.0024, 0.0024, 0.0007, 0.0006, 0.0006, 0.0007), (sk, sk, sp, sb, sb, sp),
                            ("kev", "kev", "plate", "under", "under", "plate"))
    mid = offset_loop(pts, L.BAND_T / 2)
    nm = len(mid)
    b = P("band", "band")
    bm = b.bm
    W, T = L.BAND_W / 2, L.BAND_T / 2
    e = 0.00045
    prof = ([(W, 0.0), (W - e, T), (-W + e, T), (-W, 0.0), (-W + e, -T), (W - e, -T)] if spec["band_prof"] == 6
            else [(W, T), (-W, T), (-W, -T), (W, -T)])
    rings = []
    for i in range(nm):
        p0, p1, p2 = Vector(mid[i - 1]), Vector(mid[i]), Vector(mid[(i + 1) % nm])
        a, c = (p1 - p0).normalized(), (p2 - p1).normalized()
        t = (a + c).normalized()
        k = max(0.35, a.dot(t))
        nrm = Vector((-t.y, t.x)) / k
        # the taut span (between the aramid edge and the plate edge) is 6 % narrower
        wk = 0.94 if tags[i] != tags[(i + 1) % nm] or tags[i] != tags[i - 1] else 1.0
        if tags[i] == "under":
            wk = 0.97
        ring = []
        for w, h in prof:
            ring.append(bm.verts.new((p1.x + nrm.x * h, L.BAND_Y + w * wk, p1.y + nrm.y * h)))
        rings.append(ring)
    np_ = len(prof)
    top_f, low_f = [], []
    for i in range(nm):
        A, B = rings[i], rings[(i + 1) % nm]
        low = mid[i][1] < L.PL_Z1 + 0.0004 and mid[(i + 1) % nm][1] < L.PL_Z1 + 0.0004
        for q in range(np_):
            f = bm.faces.new((A[q], A[(q + 1) % np_], B[(q + 1) % np_], B[q]))
            (low_f if low else top_f).append(f)
    b.tag(top_f)
    retag(b, low_f, "band_low")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    return b


# --- tag ----------------------------------------------------------------------------------------
def build_tag(spec):
    """Tag - stiff card: the end with the eyelet is pressed by the band, beyond its edge the tag rises
    onto the aramid pillow and lies on it (the aramid under it is pressed with the same profile,
    L.tag_bottom); the free end is bent up and slightly curved across.
    """
    tg = P("tag", "tag")
    bm = tg.bm
    lod = spec["lod"]
    cols = (-1.0, 0.0, 1.0) if lod == 0 else (-1.0, 1.0)
    sc = L.TAG_CURL[0]
    rows = []
    for s in L.tag_stations(spec["tag_detail"]):
        z = L.tag_bottom(s)
        ww = L.tag_halfwidth(s)
        cup = 0.00025 * max(0.0, (s - sc) / (L.TAG_L - sc)) if lod == 0 else 0.0
        row = []
        for c in cols:
            x, y = L.tag_point(s, c * ww)
            zc = z + cup * (1.0 - c * c)
            row.append((bm.verts.new((x, y, zc)), bm.verts.new((x, y, zc + L.TAG_T))))
        rows.append(row)
    faces = []
    nc = len(cols)
    for A, B in zip(rows, rows[1:]):
        for c in range(nc - 1):
            faces.append(bm.faces.new((A[c][1], A[c + 1][1], B[c + 1][1], B[c][1])))
            faces.append(bm.faces.new((A[c][0], B[c][0], B[c + 1][0], A[c + 1][0])))
        faces.append(bm.faces.new((A[0][0], A[0][1], B[0][1], B[0][0])))
        faces.append(bm.faces.new((A[-1][0], B[-1][0], B[-1][1], A[-1][1])))
    for row in (rows[0], rows[-1]):
        for c in range(nc - 1):
            faces.append(bm.faces.new((row[c][0], row[c + 1][0], row[c + 1][1], row[c][1])))
    tg.tag(faces)
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    bm.normal_update()
    return tg


def build_lod(spec):
    plate = build_plate(spec)
    kv_parts, poly = build_kevlar(spec)
    parts = [plate] + kv_parts + [build_band(spec, poly), build_tag(spec)]
    from kgeo import triangulate
    triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


INV_VIEW = (-0.06, -0.21, 0.37)     # front-left above: dents closer, furrows in the middle


def preview_aspect(bbox, cam):
    """Width / height of the preview frame from camera cam onto the centre (a 2x2 cell - at most 1)."""
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
    """One convex box around the stack (plate, aramid, band); the tag has no collision. The mass is the
    item weight, 0.14 kg; the impact material is thin armour plate.
    """
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    comps = [(kx.box_pts(*bbox), kx.PEN + r"\armor_1mm_plate.rvmat")]
    cz = hi[2] / 2
    memory = {
        "invView": [INV_VIEW],
        "ce_center": [(0.0, 0.0, cz)],
        "ce_radius": [(math.hypot(L.PL_X, L.PL_Y) / 2, 0.0, cz)],
    }
    print("bbox %.4f..%.4f x %.4f..%.4f x %.4f..%.4f, preview aspect from invView %.2f (2x2 cell: <= 1)"
          % (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2], preview_aspect(bbox, INV_VIEW)))
    return comps, 0.14, memory, bbox


SHOTS = [
    ("front", (-0.11, -0.30, 0.24), (0.0, 0.0, 0.006), 55),
    ("claws", (0.035, -0.115, 0.125), (0.004, -0.006, 0.008), 60),
    ("dents", (-0.03, -0.17, 0.075), (-0.004, -0.052, 0.003), 60),
    ("back", (0.17, 0.26, 0.15), (0.0, 0.012, 0.006), 55),
    ("corner", (0.16, -0.17, 0.085), (0.042, -0.022, 0.006), 75),
    ("edge", (-0.27, -0.06, 0.035), (0.0, 0.0, 0.006), 70),
    ("top", (0.0, -0.01, 0.42), (0.0, 0.0, 0.006), 50),
]

M.look_shots = (7, 2)
if __name__ == "__main__":
    M.run(build_lod, collision, SHOTS, row_step=0.18, row_shot=((0.09, -0.40, 0.32), (0.09, 0.0, 0.005)))
