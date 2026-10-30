"""M85 - gas analyzer (OZL_Tool_GasAnalyzer): a Protection line module (packers M25, M29, M34), a
portable 2x2 item. It sits in an OZL_Tool1..3 slot and shows on the machine shelf through the
module_N proxy. A universal gas analyzer UG-2 at work: the air intake device with the lid open and
the rod cocked, a rubber tube to the indicator tube, next to it an open box of spare tubes and
ampoules with powder.

    blender --background --python build_m85.py -- [--stats] [--look] [--bake-only --geo-render] [--preview]

Run make_decals.py (system Python) before the first build: the plates, the "100" rod label, the
scale card in the lid, the box label. Layout: m85_layout.py.

Size: about 0.21 x 0.21 x 0.25 m, grey enamel, the rod in a sleeve, the scale is digits. The module
is about 0.2 x 0.2 m at the base and up to about 0.25 m high.

Sample and sizes:
- UG-2 air intake device - "not more than 110 x 105 x 200 mm, mass not more than 1.5 kg"; the
  indicator tube set - "not more than 0.3 kg", 140 x 75 x 30 mm (datasheet figures from seller
  cards). One seller gives "195 x 160 x 90 mm, 1.2 kg" without explanation - by other sellers that
  is the kit of indicator means (a case), not part of the module. The body is tall (photo), so 200
  is the height with the lid;
- the device (a labour hygiene textbook; GOST 12.1.014-84 - the indicator tube method): inside the
  body a rubber bellows with a spring; the rod with a head is inserted into the sleeve and
  compresses the bellows, the stop enters a recess in one of four longitudinal grooves of the rod
  (two recesses per groove); pressing the stop releases the rod, the bellows expands and a set
  volume of air passes through the indicator tube put on the rubber tube; the volume is on the head
  and the faces of the rod. The length of the stained powder column is compared with the scale;
- panel layout from a photo (a 1989 specimen): grey hammered enamel over aluminium, a box lid on a
  hinge at the back opened past vertical, a frog clasp at the front, brackets with a leather strap
  at the sides; on the panel a numbered plate, a second plate, a chrome sleeve with a stop screw on
  the left, a fitting at the left rear corner, a rubber tube in a loop around the sleeve;
- the rod, from a second photo: a faceted ~8 mm bar with two recesses, a head of ~D 25 mm with a
  white label "100" (an estimate from the photo, no datasheet); the "100" stroke is taken as 25 mm
  - the bellows is ~D 70 mm in a 110 x 105 body;
- the indicator tube: glass D 5 x 90 mm, powder between cotton swabs (an estimate, no datasheet):
  ammonia - yellow powder, turns blue from the inlet side.
The lid is opened by 140 degrees (in the photo - past vertical): at 100 it would rise to 0.28 m,
and the module place is up to 0.25. Everything together ~0.21 x 0.21 x 0.25 m.

Condition (no faction colour): used but intact, worn paint on the edges; the enamel is cold grey,
rubbed down to aluminium, no rust (M70 has grey-blue hammered enamel over a red primer). Markings:
the digits of the number on the plate, a blank plate, "100" on the rod, scales with digits on the
card in the lid, the box label with digits and a round stamp without text.

Details: the "dayz" look (more matte, dirtier; its own worn enamel build_worn - in
kmats.build_paint the chips always rust, while here it is aluminium). Body and lid are stamped,
with rounded ribs; a piano hinge with knuckles and rivets; a clasp - a base on rivets, lugs, an
axle, a lever with a folded-back end, a wire loop; brackets with a leather strap (photo): the strap
is sewn into the brackets, hangs at the sides and goes under the body; the sleeve, the stop with
knurling, the fitting, screws and the rod head are solids of revolution with chamfers; the hose goes
along arcs to the indicator tube, no kinks; tubes and ampoules are glass (section glass,
transparent) with powder columns and cotton swabs inside. No vanilla items: the 0.2 x 0.2 m module
place is taken by the device and the box.

Work look: the indicator tube is ozl_screen (the powder column inside the glass: off - clean
yellow, work - blue stained from the inlet side; the _on atlas, no glow - powder does not glow).
The rod is bone ozl_work on the source ozl_work, the loop "pumps": two translation animations on
one bone - over 0..0.8 of the source the rod rises by the 25 mm sample stroke (the bellows draws
air through the tube), over 0.8..1 it is pushed back; at 0 and 1 the rod is cocked, so the loop
restart is not visible. A pass is animPeriod 4 s (sources).
LODs: near and mid (no rivets, hinge knuckles, the strap bend in the bracket, rod grooves and
recesses, the glass of tubes and ampoules - the tubes there are opaque), no far one.

Blender axes: X is width, Y is depth (the face at -Y), Z is up; the origin is the middle of the
place at the base.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import bmesh  # noqa: E402
import bpy  # noqa: E402,F401
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import krender  # noqa: E402
import m85_layout as L  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# Smoothing: kexport and krender by default make edges steeper than 40 degrees sharp - the hexagonal
# hose, tubes and hinge knuckles would come out faceted like pencils. Here (and only in this model)
# the threshold is 72: a hexagon is smooth with a margin (at 61 the margin was 1 degree: on steep
# hose bends a 60-degree edge could pass the threshold after triangulation), while the right angles
# of the boxes, plates and strap stay sharp. The faceted rod uses faces without shared vertices
# (build_rod). The library is not changed.
# The stripes on the hose come from the material, not the threshold: kmats dust follows the face
# normal (see smooth_normal).
# The place_look preview uses the same threshold and no glow: this model's work look has no glow
# (emissive=None), while the kit lights everything replaced in remap in the preview.
SHARP_DEG = 72.0
_visual_lod, _place, _place_look = kx.visual_lod, krender.place, krender.place_look


def _vis(parts, res, sections, selections=(), sharp_deg=SHARP_DEG, proxies=()):
    return _visual_lod(parts, res, sections, selections, sharp_deg=SHARP_DEG, proxies=proxies)


def _plc(parts, tag, offset, mats, sharp_deg=SHARP_DEG, move=None):
    return _place(parts, tag, offset, mats, sharp_deg=SHARP_DEG, move=move)


def _plc_look(parts, kind_table, origin, remap=None, glow=1.5, sharp_deg=SHARP_DEG, panels=None, move=None):
    return _place_look(parts, kind_table, origin, remap=remap, glow=0.0, sharp_deg=SHARP_DEG, panels=panels,
                       move=move)


kx.visual_lod, krender.place, krender.place_look = _vis, _plc, _plc_look

LOD_SPECS = [
    dict(lod=0, sides=20, small=12, tiny=8, cseg=3, hose=6, glass=True),
    dict(lod=1, sides=10, small=6, tiny=5, cseg=1, hose=6, glass=False),
]

REGIONS = {
    "body": ("body", 1.0), "panel": ("panel", 1.2), "lid": ("lid", 0.8), "lid_in": ("lid_in", 0.8),
    "plate1": ("plate1", 4.0), "plate2": ("plate2", 4.0), "chrome": ("chrome", 1.5), "rod": ("rod", 2.0),
    "nickel": ("nickel", 1.0), "rivet": ("rivet", 1.0), "knurl": ("knurl", 2.0), "hose": ("hose", 0.8),
    "strap": ("strap", 0.9), "itube": ("itube", 4.0), "tubes": ("tubes", 2.5), "ampoule": ("ampoule", 2.0),
    "carton": ("carton", 1.0), "carton_lid": ("carton_lid", 0.6), "insert": ("insert", 0.6),
    "card": ("card", 3.0), "label": ("label", 4.0), "box_label": ("box_label", 4.0), "groove": ("groove", 0.5),
    "hole": ("hole", 0.3), "inner": ("inner", 0.05), "glass": ("glass", 1.0),
}

# --- decals --------------------------------------------------------------------------------------


def wdecal(name):
    return os.path.join(WORK, name)


def plate_dec(img, rect):
    (x0, x1), (y0, y1) = rect
    z = L.ZP + L.PLATE_T
    return (wdecal(img), "z", 1, ("x", "y"), ((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0, y1 - y0),
            (z - 0.0003, z + 0.0003))


PLATE1_DEC = plate_dec("decal_plate1.png", L.PLATE1)
PLATE2_DEC = plate_dec("decal_plate2.png", L.PLATE2)
# by height both the cocked and the raised rod: the work-look preview shifts the part while the
# material pattern stays in place (in game the bone shifts it together with the UV)
HEAD_DEC = (wdecal("decal_head.png"), "z", 1, ("x", "y"), (L.SX, L.SY), (L.LABEL_W, L.LABEL_W),
            (L.HEAD_TOP - 0.0002, L.HEAD_TOP + L.ROD_STROKE + 0.0005))
BOX_DEC = (wdecal("decal_box_label.png"), "y", -1, ("x", "z"), L.BOX_LABEL_C, L.BOX_LABEL,
           (L.BY0 - 0.0006, L.BY0 + 0.0002))

# --- lid: rotation on the hinge ------------------------------------------------------------------
HINGE = Vector((0.0, L.HINGE_Y, L.HINGE_Z))
LID_M = Matrix.Translation(HINGE) @ Matrix.Rotation(math.radians(L.LID_DEG), 4, "X") @ Matrix.Translation(-HINGE)
# scale card under the lid bottom (looks down when closed); after the rotation - up and forward
CARD_C0 = Vector((L.DCX, L.DCY + 0.002, L.ZS + L.LID_H - L.LID_T - 0.0003))
CARD_C = LID_M @ CARD_C0
CARD_U = Vector((1.0, 0.0, 0.0))
CARD_V = (LID_M.to_3x3() @ Vector((0.0, -1.0, 0.0))).normalized()

# --- materials -----------------------------------------------------------------------------------
LIT = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
POWDER_Y = kmats.lin((214, 190, 70))    # ammonia: yellow, turns blue
STAIN = kmats.lin((70, 104, 176))
COTTON = kmats.lin((236, 234, 226))
GLASS = kmats.lin((178, 194, 190))


def build_worn(mat, origin, color, bare=kmats.lin((112, 112, 116)), seed=1.0, gloss=0.32, spec=0.25,
               wear=(0.66, 0.71), edge_k=0.7, rub=(), scratch=0.0, pits=0.0, floor_z=0.0, dust=0.15, grime=0.3,
               rim_col=kmats.lin((52, 50, 46)), bare_gloss=0.62, bare_spec=0.70, brush=True, decal_items=()):
    """Paint (here hammered enamel over aluminium, and cardboard) worn by frequent use, without rust (in
    kmats.build_paint the chips always rust). Taken from the M23 pilot (build_worn) and extended: pits -
    the hammered enamel dimples (dark rims, light bottoms, relief), bare_gloss/bare_spec/brush - the
    look of what is under the paint (aluminium is glossy and ground, cardboard is not). Worn to `bare`
    on the edges (edge_k) and where hands take it (rub - [(centre, semi-axes, strength)]); scratches
    (scratch) in two directions.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.9 for c in color[:3]) + (1,), color)
    pit = None
    if pits > 0:
        # hammered enamel (as on M70: small dimples, weak relief - for a 0.2 m item)
        pit = t.maprange(t.noise(vec, 340.0, 2.0, 0.40), 0.38, 0.62, 0.0, 1.0)
        base = t.mixc(t.math("MULTIPLY", pit, pits), base, tuple(min(1.0, c * 1.20) for c in color[:3]) + (1,))
        base = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", 1.0, pit), pits * 0.8), base,
                      tuple(c * 0.76 for c in color[:3]) + (1,))
    col = kmats.decals(t, base, sep, nsep, decal_items)
    edge = t.maprange(t.edge_wear(0.004), 0.05, 0.22, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 11.0, 10.0, 0.7), 0.75), t.math("MULTIPLY", edge, edge_k))
    grain = t.maprange(t.noise(vec, 34.0, 8.0, 0.7), 0.3, 0.7, 0.55, 1.0)
    for c, r, k in rub:
        d = t.node("ShaderNodeVectorMath")
        d.operation = "SUBTRACT"
        t.link(pos, d.inputs[0])
        d.inputs[1].default_value = tuple(c)
        q = t.node("ShaderNodeVectorMath")
        q.operation = "DIVIDE"
        t.link(d.outputs[0], q.inputs[0])
        q.inputs[1].default_value = tuple(r)
        ln = t.node("ShaderNodeVectorMath")
        ln.operation = "LENGTH"
        t.link(q.outputs[0], ln.inputs[0])
        near = t.maprange(ln.outputs["Value"], 0.25, 1.0, 1.0, 0.0)
        f = t.math("ADD", f, t.math("MULTIPLY", t.math("MULTIPLY", near, grain), k))
    worn = t.step(f, wear[0], wear[1])
    if brush:
        br = t.noise(t.stretch(vec, 0.04, 1.0, 1.0), 90.0, 4.0, 0.7)
        metal = t.mixc(t.maprange(br, 0.3, 0.7, 0.0, 1.0), tuple(c * 0.75 for c in bare[:3]) + (1,),
                       tuple(min(1.0, c * 1.15) for c in bare[:3]) + (1,))
    else:
        metal = t.mixc(t.maprange(t.noise(vec, 60.0, 4.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                       tuple(c * 0.85 for c in bare[:3]) + (1,), bare)
    rim = t.math("SUBTRACT", t.step(f, wear[0] - 0.05, wear[0]), worn)
    col = t.mixc(t.math("MULTIPLY", rim, 0.6), col, rim_col)
    col = t.mixc(worn, col, metal)
    h = t.math("MULTIPLY", worn, -0.3)
    if pit is not None:
        h = t.math("ADD", h, t.math("MULTIPLY", t.math("MULTIPLY", pit, 0.10), t.math("SUBTRACT", 1.0, worn)))
    g_ = t.math("ADD", gloss, t.math("MULTIPLY", worn, bare_gloss - gloss))
    s_ = t.math("ADD", spec, t.math("MULTIPLY", worn, bare_spec - spec))
    if scratch > 0:
        s1 = t.step(t.noise(t.stretch(vec, 0.02, 1.0, 1.0), 260.0, 2.0, 0.5), 0.70, 0.73)
        s2 = t.step(t.noise(t.stretch(vec, 1.0, 1.0, 0.03), 240.0, 2.0, 0.5), 0.71, 0.735)
        sc = t.math("MULTIPLY", t.math("MAXIMUM", s1, s2),
                    t.maprange(t.noise(vec, 5.0, 4.0, 0.5), 0.35, 0.65, 0.0, scratch))
        col = t.mixc(t.math("MULTIPLY", sc, 0.7), col, metal)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", sc, 0.15))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g_, s_, h)


def smooth_normal(t):
    """Smooth normal (Geometry Normal, not True Normal): kmats takes the face normal for dust, streaks and
    wear, and a six-sided hose came out striped like a pencil in the preview. Thin round parts (the
    hose, tube contents) use this one - the dirt lies smoothly.
    """
    gn = t.node("ShaderNodeNewGeometry")
    s = t.node("ShaderNodeSeparateXYZ")
    t.link(gn.outputs["Normal"], s.inputs[0])
    return s


def build_rubber(mat, origin, color, seed=3.0, gloss=0.2, spec=0.1, floor_z=0.0, dust=0.3, grime=0.3, mottle=0.08,
                 scuff=(0.70, 0.80)):
    """Rubber (the hose): as kmats.build_plastic, but without edge wear on face edges and with a smooth
    normal for dust - a round hose has no edges.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = smooth_normal(t)
    col = t.mixc(t.maprange(t.noise(vec, 6.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                 tuple(c * (1 - mottle) for c in color[:3]) + (1,), tuple(min(1.0, c * (1 + mottle)) for c in color[:3]) + (1,))
    sc = t.step(t.noise(t.stretch(vec, 1.0, 1.0, 1.0), 18.0, 8.0, 0.7), scuff[0], scuff[1])
    col = t.mixc(t.math("MULTIPLY", sc, 0.30), col, tuple(min(1.0, c * 1.8 + 0.03) for c in color[:3]) + (1,))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.4)
    g_ = t.math("SUBTRACT", gloss, t.math("MULTIPLY", t.math("ADD", dirt, sc), gloss * 0.5))
    s_ = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.5))
    return kmats.out(t, col, g_, s_, t.math("MULTIPLY", sc, -0.15))


def along(t, sep, o, d):
    """Coordinate of a point along the axis d from the point o: (p - o) . d (model axes = axes of the origin empty)."""
    acc = None
    for i, ax in enumerate("XYZ"):
        if abs(d[i]) < 1e-9:
            continue
        term = t.math("MULTIPLY", t.math("SUBTRACT", sep.outputs[ax], float(o[i])), float(d[i]))
        acc = term if acc is None else t.math("ADD", acc, term)
    return acc


def band_fac(t, s, lo, hi, soft):
    """1 on the segment [lo, hi] of the coordinate s, smoothly to the edges over soft."""
    return t.math("MULTIPLY", t.maprange(s, lo - soft, lo, 0.0, 1.0), t.maprange(s, hi, hi + soft, 1.0, 0.0))


def tube_fill(t, vec, s, plug0, p0, p1, plug1, powder, stain=None):
    """Tube contents: cotton swabs at the ends of the column, powder (grain), glass outside the column
    (visible only on the mid LOD, where the tube is opaque); stain = (s0, s1) - a stained column with
    a blurred front from the s0 side.
    """
    soft = 0.0004
    grain = t.maprange(t.noise(vec, 1400.0, 2.0, 0.5), 0.3, 0.7, 0.0, 1.0)
    pc = t.mixc(grain, tuple(c * 0.86 for c in powder[:3]) + (1,), powder)
    if stain is not None:
        s0, s1 = stain
        front = t.math("ADD", s0, t.math("MULTIPLY", t.noise(vec, 300.0, 2.0, 0.5), 0.004))
        st = t.maprange(t.math("SUBTRACT", s, front), -0.002, 0.001, 0.0, 1.0)
        sc = t.mixc(grain, tuple(c * 0.80 for c in STAIN[:3]) + (1,), STAIN)
        pc = t.mixc(st, pc, sc)
    glass = t.mixc(t.maprange(t.noise(vec, 60.0, 3.0, 0.5), 0.3, 0.7, 0.0, 1.0), tuple(c * 0.9 for c in GLASS[:3]) + (1,),
                   GLASS)
    col = t.mixc(band_fac(t, s, plug0, plug1, soft), glass, COTTON)
    col = t.mixc(band_fac(t, s, p0, p1, soft), col, pc)
    return col


def mat_itube(mat, origin, stain=0.0):
    """Indicator tube at work (the axis goes from the lower end in the hose to the upper one, the air inlet)."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 9.0)
    s = along(t, sep, L.TUBE_A, L.TUBE_D)
    p0, p1 = L.TUBE_POWDER
    col = tube_fill(t, vec, s, p0 - L.TUBE_PLUG, p0, p1, p1 + L.TUBE_PLUG, POWDER_Y,
                    stain=(p1 - stain, p1) if stain else None)
    return kmats.out(t, col, 0.55, 0.40, 0.0)


def mat_tubes(mat, origin):
    """Spare tubes in the box (along Y): each has its own powder colour - by the tube number from X."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 11.0)
    n, x0, pitch = L.SPARE_N, L.SPARE_X0, L.SPARE_PITCH
    fac = t.math("DIVIDE", t.math("SUBTRACT", sep.outputs["X"], x0 - pitch / 2), n * pitch)
    r = t.node("ShaderNodeValToRGB")
    cr = r.color_ramp
    cr.interpolation = "CONSTANT"
    while len(cr.elements) < n:
        cr.elements.new(0.5)
    for i, el in enumerate(cr.elements):
        el.position = i / n
        el.color = kmats.lin(L.SPARE_COLORS[i])
    t.link(fac, r.inputs["Fac"])
    y0, y1 = L.SPARE_Y
    s = t.math("SUBTRACT", sep.outputs["Y"], y0)
    ln = y1 - y0
    p0, p1 = 0.012, ln - 0.008
    soft = 0.0004
    grain = t.maprange(t.noise(vec, 1400.0, 2.0, 0.5), 0.3, 0.7, 0.0, 1.0)
    pc = t.mixc(t.math("MULTIPLY", grain, 0.14), r.outputs["Color"], (0.0, 0.0, 0.0, 1.0))
    col = t.mixc(band_fac(t, s, p0 - L.TUBE_PLUG, p1 + L.TUBE_PLUG, soft), GLASS, COTTON)
    col = t.mixc(band_fac(t, s, p0, p1, soft), col, pc)
    col, _ = kmats.weather(t, col, vec, sep, smooth_normal(t), 0.0, 0.10, 0.0, 0.3)
    return kmats.out(t, col, 0.45, 0.30, 0.0)


def mat_ampoule(mat, origin):
    """Sealed ampoule with powder (lies along X): powder in the body, a drawn-out tip - glass."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 13.0)
    s = t.math("SUBTRACT", sep.outputs["X"], L.AMP_X[0])
    ln = L.AMP_X[1] - L.AMP_X[0]
    grain = t.maprange(t.noise(vec, 1200.0, 2.0, 0.5), 0.3, 0.7, 0.0, 1.0)
    powder = kmats.lin((228, 222, 196))
    pc = t.mixc(grain, tuple(c * 0.88 for c in powder[:3]) + (1,), powder)
    col = t.mixc(band_fac(t, s, 0.0015, ln - 0.024, 0.0006), GLASS, pc)
    col, _ = kmats.weather(t, col, vec, sep, smooth_normal(t), 0.0, 0.12, 0.0, 0.3)
    return kmats.out(t, col, 0.45, 0.30, 0.0)


def mat_card(mat, origin):
    """Scale card under the bottom of the open lid: the picture in the card's slanted axes (CARD_U, CARD_V)."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 15.0)
    u = along(t, sep, CARD_C, CARD_U)
    v = along(t, sep, CARD_C, CARD_V)
    paper = kmats.lin((214, 208, 186))
    c, a = t.image(wdecal("decal_card.png"), u, v, (0.0, 0.0), L.CARD_WH)
    col = t.mixc(a, paper, c)
    col, dirt = kmats.weather(t, col, vec, sep, t.normal(), 0.0, 0.10, 0.15, 0.4)
    return kmats.out(t, col, 0.18, 0.10, 0.0)


def mat_knurl_x(mat, origin, center, ribs, color, seed=1.0, gloss=0.45, spec=0.5):
    """Knurled stop head (axis along X): dark grooves between the ribs - the cosine of the angle around
    the axis center = (y, z), in phase with the geometry ribs (rib tops are at angles 2 pi k / ribs
    from +z); no knurling on the end (from M79, the axis turned).
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    dy = t.math("SUBTRACT", sep.outputs["Y"], center[0])
    dz = t.math("SUBTRACT", sep.outputs["Z"], center[1])
    ang = t.math("ARCTAN2", dy, dz)
    rib = t.math("ADD", 0.5, t.math("MULTIPLY", t.math("COSINE", t.math("MULTIPLY", ang, float(ribs))), 0.5))
    side = t.maprange(t.math("ABSOLUTE", nsep.outputs["X"]), 0.5, 0.8, 1.0, 0.0)
    groove = t.math("MULTIPLY", t.math("SUBTRACT", 1.0, rib), side)
    col = t.mixc(t.math("MULTIPLY", groove, 0.55), color, tuple(c * 0.45 for c in color[:3]) + (1,))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, 0.0, 0.05, 0.3, 0.5)
    gl = t.math("SUBTRACT", gloss, t.math("MULTIPLY", groove, gloss * 0.4))
    return kmats.out(t, col, gl, spec, t.math("MULTIPLY", t.math("MULTIPLY", rib, side), 0.8))


# where the enamel is rubbed by hands (centre, semi-axes, strength): the clasp, the front of the top
# edge, the brackets; on the panel - around the sleeve and the stop; at the lid - the front edge it
# is lifted by (already rotated)
BODY_RUB = [((L.DCX, L.DY0, L.ZS - 0.012), (0.022, 0.010, 0.017), 0.24),
            ((L.DCX, L.DY0, L.ZS), (0.060, 0.010, 0.008), 0.14),
            ((L.DX0, L.LUG_Y, L.LUG_Z), (0.010, 0.022, 0.030), 0.30),
            ((L.DX1, L.LUG_Y, L.LUG_Z), (0.010, 0.022, 0.030), 0.30)]
PANEL_RUB = [((L.SX, L.SY, L.ZP), (0.030, 0.030, 0.010), 0.30),
             ((L.SX - 0.025, L.SY, L.ZP), (0.014, 0.012, 0.010), 0.25)]
LID_RUB = [(tuple(LID_M @ Vector((L.DCX, L.DY0, L.ZS + 0.016))), (0.030, 0.014, 0.014), 0.40)]
ENAMEL = dict(color=kmats.lin((146, 150, 153)), bare=kmats.lin((182, 184, 186)), seed=2.1, gloss=0.36, spec=0.28,
              wear=(0.69, 0.74), edge_k=1.0, scratch=0.60, pits=0.18, floor_z=0.0, dust=0.20, grime=0.35)
CARTON = dict(color=kmats.lin((150, 156, 150)), bare=kmats.lin((198, 190, 166)), seed=9.4, gloss=0.10, spec=0.05,
              wear=(0.74, 0.80), edge_k=1.0, floor_z=0.0, dust=0.25, grime=0.30, rim_col=kmats.lin((118, 112, 98)),
              bare_gloss=0.06, bare_spec=0.04, brush=False)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "body": (build_worn, dict(ENAMEL, rub=BODY_RUB)),
    "panel": (build_worn, dict(ENAMEL, seed=2.7, wear=(0.74, 0.79), edge_k=0.7, rub=PANEL_RUB, dust=0.12)),
    "lid": (build_worn, dict(ENAMEL, seed=3.3, rub=LID_RUB)),
    "lid_in": (build_worn, dict(ENAMEL, seed=3.8, wear=(0.76, 0.80), edge_k=0.6, scratch=0.2, dust=0.08,
                                grime=0.35)),
    "plate1": ("paint", dict(LIT, color=kmats.lin((30, 30, 33)), gloss=0.5, spec=0.4, decal_items=[PLATE1_DEC])),
    "plate2": ("paint", dict(LIT, color=kmats.lin((30, 30, 33)), gloss=0.5, spec=0.4, decal_items=[PLATE2_DEC])),
    # sleeve and head chrome, rod steel, hinge and clasp nickel: in the dayz profile steel is darker
    # (x0.65)
    "chrome": ("steel", dict(seed=6.8, tone=0.42, along="z", gloss=0.70, spec=0.80, dust=0.06, grime=0.30)),
    "rod": ("steel", dict(seed=7.3, tone=0.40, along="z", gloss=0.62, spec=0.75, dust=0.03, grime=0.25)),
    "nickel": ("steel", dict(seed=7.9, tone=0.40, along="x", gloss=0.50, spec=0.60, dust=0.12, grime=0.40)),
    "rivet": ("steel", dict(seed=8.1, tone=0.36, along="z", gloss=0.45, spec=0.55, dust=0.10, grime=0.45)),
    "knurl": (mat_knurl_x, dict(center=(L.SY, L.STOP_Z), ribs=12, color=kmats.lin((128, 130, 133)), seed=8.4)),
    "hose": (build_rubber, dict(color=kmats.lin((30, 30, 31)), seed=8.9, gloss=0.20, spec=0.10, mottle=0.10, dust=0.25,
                                grime=0.30, scuff=(0.72, 0.82))),
    # strap: leather, dark brown, rubbed lighter on the edges and the bend
    "strap": ("plastic", dict(color=kmats.lin((70, 48, 32)), seed=9.1, gloss=0.22, spec=0.12, mottle=0.22, dust=0.20,
                              grime=0.35, scuff=(0.56, 0.66))),
    "itube": (mat_itube, dict()),
    "itube_on": (mat_itube, dict(stain=L.TUBE_STAIN)),
    "tubes": (mat_tubes, dict()),
    "ampoule": (mat_ampoule, dict()),
    # cardboard box: rubbed to light cardboard on the edges, a label on the end
    "carton": (build_worn, CARTON),
    "carton_lid": (build_worn, dict(CARTON, color=kmats.lin((142, 148, 142)), seed=9.9, dust=0.30, grime=0.40)),
    "box_label": ("paint", dict(LIT, color=kmats.lin((150, 156, 150)), gloss=0.12, spec=0.06, dust=0.10,
                                decal_items=[BOX_DEC])),
    "insert": ("plastic", dict(color=kmats.lin((150, 128, 96)), seed=10.3, gloss=0.08, spec=0.04, mottle=0.10,
                               dust=0.2, grime=0.3, scuff=(0.9, 1.0))),
    "card": (mat_card, dict()),
    "label": ("paint", dict(LIT, color=kmats.lin((168, 170, 172)), gloss=0.45, spec=0.35, decal_items=[HEAD_DEC])),
    "groove": ("flat", dict(color=kmats.lin((70, 72, 75)), gloss=0.45, spec=0.4)),
    "hole": ("flat", dict(color=kmats.lin((10, 10, 11)), gloss=0.1, spec=0.05)),
    "inner": ("flat", dict(color=kmats.lin((40, 41, 42)), gloss=0.1, spec=0.05)),
    "glass": ("flat", dict(color=GLASS, gloss=0.9, spec=0.8)),     # section glass - not in the atlas
})

OBJ, NAME = "m85_gas_analyzer", "ozr_gas_analyzer"
SEL_TUBE, SEL_WORK = "ozl_screen", "ozl_work"
# work look preview: the rod raised by the sample stroke (as at 0.8 of the source), the tube turns
# blue
ON = dict(remap={"itube": "itube_on"}, emissive=None, move={SEL_WORK: (0.0, 0.0, L.ROD_STROKE)})
# the loop "pumps" (OZL_WorkFx loop): over 0..0.8 of the source the rod rises along the whole axis
# (the sample stroke), over 0.8..1 it returns; at 0 and 1 it is cocked, the loop restart is not
# noticeable. Two translations on one bone.
RISE = dict(type="translation", source="ozl_work", selection=SEL_WORK, axis="ozl_work_axis", memory=1,
            minValue=0.0, maxValue=0.8, offset0=0.0, offset1=1.0)
PRESS = dict(RISE, minValue=0.8, maxValue=1.0, offset0=0.0, offset1=-1.0)
GLASS_CA = dict(size=128, seed=17, base=(0.70, 0.74, 0.72), clear=0.04, edge=0.10, smudge=0.06, streaks=0.0)
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz", glass=GLASS_CA,
                 selections=(SEL_TUBE, SEL_WORK), hidden=(SEL_TUBE,), states={"on": ON}, bones=((SEL_WORK, ""),),
                 animations=(("ozl_work_rise", RISE), ("ozl_work_press", PRESS)),
                 sources={"ozl_work": dict(animPeriod=4.0)})
P = M.part
BOUNDS = {}


# =============================================================================
# Primitives missing from kgeo
# =============================================================================
def ridx(part, region):
    return part.region_index(region, *M.regions[region])


def retag(part, test, region="inner"):
    """Hidden faces go to the dark "inner" region with a small scale (they need no atlas room)."""
    part.bm.normal_update()
    idx = ridx(part, region)
    for f in part.bm.faces:
        if f.is_valid and test(f):
            f[part.reg] = idx


def facing(axis, sign, thr=0.99):
    return lambda f: f.normal[axis] * sign > thr


def transform(part, m):
    for v in part.bm.verts:
        v.co = m @ v.co
    part.bm.normal_update()
    return part


def box(name, region, x0, x1, y0, y1, z0, z1, **kw):
    p = P(name, region, **{k: kw.pop(k) for k in ("uv_name", "uv_origin", "group", "section") if k in kw})
    g.box(p, x0, x1, y0, y1, z0, z1, **kw)
    return p


def cyl(name, region, c, axis, r, length, sides, **kw):
    p = P(name, region, **{k: kw.pop(k) for k in ("uv_name", "uv_origin", "group", "section") if k in kw})
    g.cyl(p, c, axis, r, length, sides, **kw)
    return p


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, as in M79); k is the step count per
    segment (one for all or a list per segment: more on steep arcs).
    """
    v = [Vector(p) for p in pts]
    ks = list(k) if isinstance(k, (list, tuple)) else [k] * (len(v) - 1)
    out = []
    for i in range(len(v) - 1):
        p0 = v[i - 1] if i > 0 else 2 * v[i] - v[i + 1]
        p1, p2 = v[i], v[i + 1]
        p3 = v[i + 2] if i + 2 < len(v) else 2 * v[i + 1] - v[i]
        for s in range(ks[i]):
            t = s / ks[i]
            out.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (3 * p1 - p0 - 3 * p2 + p3) * t ** 3))
    out.append(v[-1])
    return [tuple(q) for q in out]


def frame_axis(o, d):
    """Right-handed frame with axis n = d (u x v = n): for solids of revolution along any axis."""
    n = Vector(d).normalized()
    u = Vector((0, 0, 1)).cross(n)
    if u.length < 1e-6:
        u = Vector((1, 0, 0))
    u.normalize()
    return g.Frame(o, u, n.cross(u), n)


def fz(o):
    return g.Frame(o, (1, 0, 0), (0, 1, 0), (0, 0, 1))


def fx(o, sign=1):
    return g.Frame(o, (0, 1, 0), (0, 0, 1), (1, 0, 0)) if sign > 0 else g.Frame(o, (0, 0, 1), (0, 1, 0), (-1, 0, 0))


def fy(o, sign=1):
    return g.Frame(o, (0, 0, 1), (1, 0, 0), (0, 1, 0)) if sign > 0 else g.Frame(o, (1, 0, 0), (0, 0, 1), (0, -1, 0))


def lathe(part, prof, sides, frame, regs=None, cap0=0, cap1=0, cap_regs=(None, None), phase=0.0):
    """Solid of revolution: prof [(r, h)] along the axis frame.n; faces look where the profile traversal
    leads: up along the outer side - outward, along the top toward the axis - up, down along the bore -
    inward (sleeve, ends without extra faces). regs is the region of each belt (None - the current
    one); cap0/cap1 close the first or last ring: +1 - the disc looks along the axis, -1 - against.
    """
    bm = part.bm
    rings = []
    for r, h in prof:
        rings.append([bm.verts.new(frame.p(r * math.cos(phase + 2 * math.pi * k / sides),
                                           r * math.sin(phase + 2 * math.pi * k / sides), h)) for k in range(sides)])
    new = []
    for i in range(len(rings) - 1):
        band = [bm.faces.new([rings[i][k], rings[i][(k + 1) % sides], rings[i + 1][(k + 1) % sides], rings[i + 1][k]])
                for k in range(sides)]
        part.tag(band, ridx(part, regs[i]) if regs and regs[i] else None)
        new += band
    for ring, sgn, reg in ((rings[0], cap0, cap_regs[0]), (rings[-1], cap1, cap_regs[1])):
        if sgn:
            f = bm.faces.new(ring if sgn > 0 else ring[::-1])
            part.tag([f], ridx(part, reg) if reg else None)
            new.append(f)
    bm.normal_update()
    return new


def knurl_lathe(part, frame, h0, h1, r, depth, ribs, ch, region_side, region_end):
    """Knurled head: 2 * ribs vertices around the circle, every other one sunk by depth; the ends are a
    smooth chamfer ch and the end faces. Rib tops are at angles 2 pi k / ribs (in phase with mat_knurl_x).
    """
    bm = part.bm
    n = 2 * ribs

    def ring(rr, h, knurled):
        return [bm.verts.new(frame.p((rr - depth * (k % 2) * knurled) * math.cos(math.pi * k / ribs),
                                     (rr - depth * (k % 2) * knurled) * math.sin(math.pi * k / ribs), h))
                for k in range(n)]
    rings = [ring(r - ch, h0, 0), ring(r, h0 + ch, 1), ring(r, h1 - ch, 1), ring(r - ch, h1, 0)]
    side, end = ridx(part, region_side), ridx(part, region_end)
    for i in range(3):
        part.tag([bm.faces.new([rings[i][k], rings[i][(k + 1) % n], rings[i + 1][(k + 1) % n], rings[i + 1][k]])
                  for k in range(n)], side if i == 1 else end)
    part.tag([bm.faces.new(rings[0][::-1]), bm.faces.new(rings[-1])], end)
    bm.normal_update()


def rrect(cx, cy, w, d, r, seg, inset=0.0):
    """Rectangle with rounded corners (counter-clockwise from above), inset moves it inward."""
    rr = max(r - inset, 0.0002)
    hx, hy = w / 2 - inset - rr, d / 2 - inset - rr
    pts = []
    for sx, sy, a0 in ((1, -1, -90.0), (1, 1, 0.0), (-1, 1, 90.0), (-1, -1, 180.0)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90.0 * k / seg)
            pts.append((cx + sx * hx + rr * math.cos(a), cy + sy * hy + rr * math.sin(a)))
    return pts


def rr_lathe(part, cx, cy, w, d, r, seg, prof, regs, cap0=0, cap1=0, cap_regs=(None, None)):
    """Stamped box: rings of a rounded rectangle prof [(inset, z)] - like lathe, faces look along the
    profile traversal. regs is the region of each belt.
    """
    bm = part.bm
    rings = [[bm.verts.new((x, y, z)) for x, y in rrect(cx, cy, w, d, r, seg, ins)] for ins, z in prof]
    n = len(rings[0])
    for i in range(len(rings) - 1):
        part.tag([bm.faces.new([rings[i][k], rings[i][(k + 1) % n], rings[i + 1][(k + 1) % n], rings[i + 1][k]])
                  for k in range(n)], ridx(part, regs[i]))
    for ring, sgn, reg in ((rings[0], cap0, cap_regs[0]), (rings[-1], cap1, cap_regs[1])):
        if sgn:
            part.tag([bm.faces.new(ring if sgn > 0 else ring[::-1])], ridx(part, reg))
    bm.normal_update()


def arc_prof(r, z_top, inset0, n):
    """Rounding of the top edge: from the wall (inset inset0, z_top - r) to the top (inset inset0 + r, z_top)."""
    return [(inset0 + r - r * math.cos(math.radians(90.0 * k / n)), z_top - r + r * math.sin(math.radians(90.0 * k / n)))
            for k in range(n + 1)]


def dome(part, c, n_dir, r, h, sides=6):
    """A rivet or a head: a low cone with a flat top, the axis n_dir outward."""
    lathe(part, [(r, 0.0), (r * 0.55, h)], sides, frame_axis(c, n_dir), cap1=1)


def band(part, pts, nrm, half_w, half_t):
    """A flat strap along pts: nrm[i] is where its thickness looks at point i (straightened across the
    run), the width is across the run and the thickness. The support is given at every point - the
    strap does not twist by itself and can bend only across its width, like a real strap.
    """
    bm = part.bm
    pv = [Vector(p) for p in pts]
    n = len(pv)
    rings = []
    for i in range(n):
        t = (pv[min(i + 1, n - 1)] - pv[max(i - 1, 0)]).normalized()
        nn = Vector(nrm[i]) - t * Vector(nrm[i]).dot(t)
        nn.normalize()
        w = nn.cross(t).normalized()
        c = pv[i]
        rings.append([bm.verts.new(c + w * half_w + nn * half_t), bm.verts.new(c - w * half_w + nn * half_t),
                      bm.verts.new(c - w * half_w - nn * half_t), bm.verts.new(c + w * half_w - nn * half_t)])
    new = []
    for i in range(n - 1):
        r0, r1 = rings[i], rings[i + 1]
        for q in range(4):
            new.append(bm.faces.new([r0[q], r0[(q + 1) % 4], r1[(q + 1) % 4], r1[q]]))
    new.append(bm.faces.new(rings[0][::-1]))
    new.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


# =============================================================================
# Body: walls, flange and panel - one stamped surface
# =============================================================================
def build_case(spec):
    lod, cs = spec["lod"], spec["cseg"]
    parts = []
    w, d, r = L.DW, L.DD, L.CORNER_R
    rb, rt = L.EDGE_RB, L.EDGE_RT
    body = P("body", "body")
    # bottom edge (a chamfer), the wall, a rounded top edge under the lid
    prof = [(rb, 0.0), (0.0, rb)] + arc_prof(rt, L.ZS, 0.0, 1)
    regs = ["body"] * 3
    # a ledge up to the flange, the flange (outward, top, inward) and the panel
    prof += [(L.LIP_IN, L.ZS), (L.LIP_IN, L.ZL), (L.LIP_IN + L.LIP_T, L.ZL), (L.LIP_IN + L.LIP_T, L.ZP)]
    regs += ["body", "body", "body", "panel"]
    rr_lathe(body, L.DCX, L.DCY, w, d, r, cs, prof, regs, cap0=-1, cap1=1, cap_regs=("inner", "panel"))
    parts.append(body)
    parts += build_hinge(spec, lid=False)
    parts += build_latch(spec)
    for sg in (-1, 1):
        parts += build_lug(spec, sg)
    return parts


def build_hinge(spec, lid):
    """Piano hinge: a leaf on the back wall (of the body or the lid), knuckles every other one (1, 3, 5 on
    the body, 2, 4 on the lid) on a common axle, leaf rivets; on the mid LOD - a leaf and one tube.
    """
    lod = spec["lod"]
    parts = []
    x0 = L.DCX - L.HINGE_W / 2
    if lid:
        leaf = box("lid_leaf", "nickel", x0, x0 + L.HINGE_W, L.DY1 - 0.0002, L.DY1 + 0.0006, L.ZS + 0.0020, L.ZS + 0.0110)
        zr = L.ZS + 0.0072
    else:
        leaf = box("hinge_leaf", "nickel", x0, x0 + L.HINGE_W, L.DY1 - 0.0002, L.DY1 + 0.0006, L.ZS - 0.0100, L.ZS)
        zr = L.ZS - 0.0058
    parts.append(leaf)
    if lod == 0:
        seg = L.HINGE_W / L.HINGE_KN
        for i in range(L.HINGE_KN):
            if (i % 2 == 1) != lid:
                continue
            xc = x0 + seg * (i + 0.5)
            parts.append(cyl("knuckle%d" % i, "nickel", (xc, L.HINGE_Y, L.HINGE_Z), "x", 0.0022, seg - 0.0006, 8,
                             uv_name="knuckle", uv_origin=(xc, L.HINGE_Y, L.HINGE_Z)))
        rv = P("leaf_rivets_%s" % ("lid" if lid else "body"), "rivet")
        for xx in (x0 + 0.014, x0 + L.HINGE_W - 0.014):
            dome(rv, (xx, L.DY1 + 0.0006, zr), (0, 1, 0), 0.0012, 0.0005)
        parts.append(rv)
    elif not lid:
        parts.append(cyl("hinge_barrel", "nickel", (L.DCX, L.HINGE_Y, L.HINGE_Z), "x", 0.0022, L.HINGE_W, 6))
    return parts


def build_latch(spec):
    """Frog clasp on the face, open: a base on two rivets, lugs, an axle, the lever hangs down and
    slightly off the wall, its end is rolled into a tube with a wire loop in it.
    """
    lod = spec["lod"]
    parts = []
    x, y0, zs = L.DCX, L.DY0, L.ZS
    parts.append(box("latch_base", "nickel", x - 0.009, x + 0.009, y0 - 0.0011, y0 + 0.0002, zs - 0.020, zs - 0.004,
                     **(dict(r=0.0005, seg=1) if lod == 0 else {})))
    ax = (x, y0 - 0.0030, zs - 0.0075)
    if lod == 0:
        rv = P("latch_rivets", "rivet")
        for sx in (-1, 1):
            dome(rv, (x + sx * 0.0064, y0 - 0.0011, zs - 0.0165), (0, -1, 0), 0.0012, 0.0005)
        parts.append(rv)
        for sx in (-1, 1):
            parts.append(box("latch_ear%d" % (sx > 0), "nickel", x + sx * 0.0054 - 0.0004, x + sx * 0.0054 + 0.0004,
                             y0 - 0.0042, y0 - 0.0010, zs - 0.0098, zs - 0.0052, uv_name="latch_ear",
                             uv_origin=(x + sx * 0.0054, y0, zs - 0.0075)))
    parts.append(cyl("latch_axle", "nickel", ax, "x", 0.0011, 0.0118, spec["tiny"]))
    tilt = 0.12
    v = Vector((0, -math.sin(tilt), -math.cos(tilt)))
    nn = Vector((0, -math.cos(tilt), math.sin(tilt)))
    fr = g.Frame(Vector(ax) + nn * 0.0006, (1, 0, 0), v, nn)
    lever = P("latch_lever", "nickel")
    g.box(lever, -0.0050, 0.0050, -0.0010, 0.0220, -0.0004, 0.0004, frame=fr)
    parts.append(lever)
    e = fr.p(0, 0.0222, 0.0010)
    if lod == 0:
        parts.append(cyl("latch_curl", "nickel", tuple(e), "x", 0.0011, 0.0104, 8))
    lp = P("latch_loop", "nickel")
    loop = [(x - 0.0060, e.y, e.z), (x - 0.0064, e.y - 0.0006, e.z - 0.0060), (x - 0.0052, e.y - 0.0010, e.z - 0.0120),
            (x - 0.0026, e.y - 0.0012, e.z - 0.0148), (x, e.y - 0.0012, e.z - 0.0154),
            (x + 0.0026, e.y - 0.0012, e.z - 0.0148), (x + 0.0052, e.y - 0.0010, e.z - 0.0120),
            (x + 0.0064, e.y - 0.0006, e.z - 0.0060), (x + 0.0060, e.y, e.z)]
    g.pipe(lp, loop if lod == 0 else loop[::2], 0.0007, 6 if lod == 0 else 4)
    parts.append(lp)
    return parts


def build_lug(spec, sg):
    """Strap bracket on the side wall (a U of strip on two rivets, rounded bends) and the strap: its end
    is wrapped around the crossbar and riveted to itself, the strap hangs along the wall and goes under
    the body - the device was put down on the strap (photo: a strap on brackets).
    """
    lod = spec["lod"]
    parts = []
    xw = L.DX0 if sg < 0 else L.DX1
    yb, zb, out = L.LUG_Y, L.LUG_Z, L.LUG_OUT
    nm = "l" if sg < 0 else "r"
    br = P("lug_" + nm, "nickel")
    if lod == 0:
        pts = [(0.0006, -0.0155), (0.0006, -0.0100), (0.0016, -0.0086), (0.0036, -0.0079), (out, -0.0064),
               (out, 0.0064), (0.0036, 0.0079), (0.0016, 0.0086), (0.0006, 0.0100), (0.0006, 0.0155)]
    else:
        pts = [(0.0006, -0.0155), (0.0006, -0.0095), (out, -0.0070), (out, 0.0070), (0.0006, 0.0095), (0.0006, 0.0155)]
    g.sweep(br, [(xw + sg * a, yb + b, zb) for a, b in pts], (0, 0, 1), 0.0006, 0.0060)
    parts.append(br)
    if lod == 0:
        rv = P("lug_rivets_" + nm, "rivet")
        for yy in (yb - 0.0128, yb + 0.0128):
            dome(rv, (xw + sg * 0.0012, yy, zb), (sg, 0, 0), 0.0014, 0.0006)
        parts.append(rv)
    # strap: thickness along x at the wall, width along y
    t2 = L.STRAP_T / 2
    x_in = xw + sg * (out - 0.0006) / 2                       # middle of the gap between the wall and the crossbar
    x_out = xw + sg * (out + 0.0006 + t2)                     # outer end of the strap past the crossbar
    zf, rf = zb + 0.0062, abs(x_out - x_in) / 2
    xf = (x_in + x_out) / 2
    ext = (sg, 0.0, 0.0)
    wall = (-sg, 0.0, 0.0)
    pts, nrm = [], []
    if lod == 0:
        for p in ((x_in + sg * L.STRAP_T, yb, zb - 0.024), (x_in + sg * (L.STRAP_T + 0.0001), yb, zb - 0.016),
                  (x_out - sg * 0.0010, yb, zb - 0.0085), (x_out, yb, zb - 0.0040), (x_out, yb, zb + 0.0040)):
            pts.append(p)
            nrm.append(ext)
        for k in range(5):                                     # bend around the crossbar
            phi = math.pi * k / 4
            pts.append((xf + sg * rf * math.cos(phi), yb, zf + rf * math.sin(phi)))
            nrm.append((sg * math.cos(phi), 0.0, math.sin(phi)))
        pts += [(x_in, yb, zb - 0.0020)]
        nrm += [wall]
    else:
        pts.append((x_in, yb, zb + 0.0062))
        nrm.append(wall)
    pts += [(x_in, yb, zb - 0.0160), (xw + sg * 0.0026, yb + 0.0008, zb - 0.045), (xw + sg * 0.0032, yb + 0.0016, zb - 0.085),
            (xw + sg * 0.0030, yb + 0.0021, 0.030), (x_in, yb + 0.0022, 0.0112)]
    nrm += [wall] * 5
    rb2 = 0.0040                                               # fold-under below the body
    cxb, czb = x_in - sg * rb2, 0.0011 + rb2
    for k in range(1, 4 if lod == 0 else 2):
        psi = math.radians(90.0 * k / (3 if lod == 0 else 1))
        pts.append((cxb + sg * rb2 * math.cos(psi), yb + 0.0022, czb - rb2 * math.sin(psi)))
        nrm.append((-sg * math.cos(psi), 0.0, math.sin(psi)))
    pts.append((x_in - sg * 0.0110, yb + 0.0022, 0.0011))
    nrm.append((0.0, 0.0, 1.0))
    st = P("strap_" + nm, "strap")
    band(st, pts, nrm, L.STRAP_W / 2, t2)
    parts.append(st)
    if lod == 0:
        rv = P("strap_rivet_" + nm, "rivet")
        dome(rv, (x_in + sg * (L.STRAP_T + 0.0001 + t2), yb, zb - 0.0165), ext, 0.0013, 0.0006)
        parts.append(rv)
    return parts


# =============================================================================
# Lid: built closed, then rotated on the hinge
# =============================================================================
def build_lid(spec):
    """Box lid with rounded ribs, the hinge leaf and knuckles, the clasp bracket on two rivets, the scale
    card under the bottom on two tabs.
    """
    lod, cs = spec["lod"], spec["cseg"]
    parts = []
    top = L.ZS + L.LID_H
    lid = P("lid", "lid")
    prof = [(L.LID_T, top - L.LID_T), (L.LID_T, L.ZS), (0.0, L.ZS)]
    regs = ["lid_in", "lid"]
    arc = arc_prof(L.LID_RT, top, 0.0, 2 if lod == 0 else 1)
    prof += arc
    regs += ["lid"] * len(arc)
    rr_lathe(lid, L.DCX, L.DCY, L.DW, L.DD, L.CORNER_R, cs, prof, regs, cap0=-1, cap1=1, cap_regs=("lid_in", "lid"))
    parts.append(lid)
    parts += build_hinge(spec, lid=True)
    x, y0, zs = L.DCX, L.DY0, L.ZS
    parts.append(box("keeper", "nickel", x - 0.0065, x + 0.0065, y0 - 0.0010, y0 + 0.0002, zs + 0.0050, zs + 0.0180,
                     **(dict(r=0.0004, seg=1) if lod == 0 else {})))
    parts.append(box("keeper_hook", "nickel", x - 0.0055, x + 0.0055, y0 - 0.0036, y0 - 0.0008, zs + 0.0160,
                     zs + 0.0178))
    if lod == 0:
        rv = P("keeper_rivets", "rivet")
        for sx in (-1, 1):
            dome(rv, (x + sx * 0.0042, y0 - 0.0010, zs + 0.0090), (0, -1, 0), 0.0011, 0.0005)
        parts.append(rv)
    # scale card: a face under the bottom (looks down when closed), two holding tabs at the corners
    cw, ch = L.CARD_WH
    c = CARD_C0
    card = P("card", "card")
    g.quad(card, [(c.x - cw / 2, c.y + ch / 2, c.z), (c.x + cw / 2, c.y + ch / 2, c.z), (c.x + cw / 2, c.y - ch / 2, c.z),
                  (c.x - cw / 2, c.y - ch / 2, c.z)])
    parts.append(card)
    if lod == 0:
        for k, sx in enumerate((-1, 1)):
            parts.append(box("card_clip%d" % k, "nickel", c.x + sx * cw / 2 - 0.004, c.x + sx * cw / 2 + 0.004,
                             c.y - ch / 2 - 0.0015, c.y - ch / 2 + 0.0045, c.z - 0.0005, c.z + 0.0003,
                             uv_name="card_clip", uv_origin=(c.x + sx * cw / 2, c.y - ch / 2, c.z)))
    for p in parts:
        transform(p, LID_M)
    return parts


# =============================================================================
# Panel: sleeve, stop, fitting, plates, screws; the rod is a bone
# =============================================================================
def build_panel(spec):
    lod, n, ns, nt = spec["lod"], spec["sides"], spec["small"], spec["tiny"]
    parts = []
    sx, sy, zp = L.SX, L.SY, L.ZP
    # sleeve: a flange with a chamfer, a liner, a chamfer on top, a bore for the rod (dark)
    sl = P("sleeve", "chrome")
    fr_, fh, sr, shh, br = L.FLANGE_R, L.FLANGE_H, L.SLEEVE_R, L.SLEEVE_H, L.BORE_R
    if lod == 0:
        prof = [(fr_, -0.0002), (fr_, fh * 0.55), (fr_ - 0.0006, fh), (sr, fh), (sr, shh - 0.0008),
                (sr - 0.0008, shh), (br + 0.0004, shh), (br, shh - 0.0035)]
        regs = ["chrome"] * 6 + ["hole"]
    else:
        prof = [(fr_, -0.0002), (fr_, fh), (sr, fh), (sr, shh), (br, shh), (br, shh - 0.0030)]
        regs = ["chrome"] * 4 + ["hole"]
    lathe(sl, prof, 16 if lod == 0 else n, fz((sx, sy, zp)), regs=regs, cap1=1, cap_regs=(None, "hole"))
    parts.append(sl)
    # stop on the left: a boss, a screw, a knurled head (the axis goes toward -x from the sleeve
    # wall)
    fs = fx((sx - sr + 0.0006, sy, L.STOP_Z), -1)
    st = P("stop", "chrome")
    lathe(st, [(0.0036, -0.0012), (0.0036, 0.0016), (0.0030, 0.0022)], ns, fs, cap1=1)
    lathe(st, [(0.0016, 0.0018), (0.0016, 0.0064)], nt, fs)
    parts.append(st)
    kn = P("stop_knob", "knurl")
    if lod == 0:
        knurl_lathe(kn, fs, 0.0062, 0.0132, 0.0056, 0.0004, 12, 0.0006, "knurl", "chrome")
    else:
        lathe(kn, [(0.0050, 0.0062), (0.0056, 0.0068), (0.0056, 0.0126), (0.0050, 0.0132)], 8, fs, cap0=-1, cap1=1)
    parts.append(kn)
    # bellows fitting: a flange with a chamfer; the end of the hose put on it hides the barbed tube
    nx, ny = L.NIP
    nip = P("nipple", "nickel")
    lathe(nip, [(0.0044, -0.0002), (0.0044, 0.0008), (0.0038, 0.0013), (0.0022, 0.0013), (0.0022, 0.0030)], ns,
          fz((nx, ny, zp)))
    parts.append(nip)
    # plates
    for nm, reg, ((x0, x1), (y0, y1)) in (("plate1", "plate1", L.PLATE1), ("plate2", "plate2", L.PLATE2)):
        parts.append(box(nm, reg, x0, x1, y0, y1, zp - 0.0002, zp + L.PLATE_T))
    # bellows fixing screws: a chamfered head and a slot
    if lod == 0:
        for k, (x, y) in enumerate(L.SCREWS):
            sc = P("screw%d" % k, "nickel", uv_name="screw", uv_origin=(x, y, zp))
            lathe(sc, [(0.0022, 0.0), (0.0021, 0.0004), (0.0012, 0.0009)], 8, fz((x, y, zp)), cap1=1)
            parts.append(sc)
            a = 0.6 + 0.9 * k
            fr = g.Frame((x, y, zp + 0.0009), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))
            parts.append(P("slot%d" % k, "hole", uv_name="slot", uv_origin=(x, y, zp)))
            g.box(parts[-1], -0.0019, 0.0019, -0.00030, 0.00030, -0.0002, 0.00008, frame=fr)
    return parts


def build_rod(spec):
    """Rod (bone ozl_work): a faceted bar in the sleeve, a neck, a chamfered head with the "100" label;
    the faces have grooves and recesses (the lower recesses are in the sleeve, with the rod raised they
    come out on top).
    """
    lod, n = spec["lod"], spec["sides"]
    parts = []
    sx, sy = L.SX, L.SY
    a, c = L.ROD_A / 2, L.ROD_CH
    poly = [(sx - a + c, sy - a), (sx + a - c, sy - a), (sx + a, sy - a + c), (sx + a, sy + a - c),
            (sx + a - c, sy + a), (sx - a + c, sy + a), (sx - a, sy + a - c), (sx - a, sy - a + c)]
    rod = P("rod", "rod", group=SEL_WORK)
    g.prism(rod, poly, (0, 1), L.ROD_Z0, L.HEAD_Z0 - L.NECK_H + 0.0005)
    retag(rod, facing(2, -1))
    # faceted bar (photo): faces without shared vertices - flat, with crisp edges at any threshold
    bmesh.ops.split_edges(rod.bm, edges=rod.bm.edges[:])
    parts.append(rod)
    nk = P("neck", "chrome", group=SEL_WORK)
    lathe(nk, [(0.0040, -0.0006), (0.0044, 0.0004), (L.NECK_R, 0.0016), (L.NECK_R, L.NECK_H + 0.0002)],
          10 if lod == 0 else 6, fz((sx, sy, L.HEAD_Z0 - L.NECK_H)))
    parts.append(nk)
    hd = P("head", "chrome", group=SEL_WORK)
    hr, hh = L.HEAD_R, L.HEAD_H
    if lod == 0:
        prof = [(L.NECK_R - 0.0003, 0.0), (hr - 0.0012, 0.00035), (hr, 0.0012), (hr, 0.0025), (hr - 0.0005, 0.0032),
                (hr - 0.0013, hh)]
    else:
        prof = [(L.NECK_R - 0.0003, 0.0), (hr, 0.0010), (hr, 0.0026), (hr - 0.0010, hh)]
    lathe(hd, prof, 16 if lod == 0 else n, fz((sx, sy, L.HEAD_Z0)), cap1=1)
    parts.append(hd)
    lb = P("head_label", "label", group=SEL_WORK)
    w, z = L.LABEL_W / 2, L.HEAD_TOP + 0.0001
    g.quad(lb, [(sx - w, sy - w, z), (sx + w, sy - w, z), (sx + w, sy + w, z), (sx - w, sy + w, z)])
    parts.append(lb)
    if lod == 0:
        ztop = L.HEAD_Z0 - L.NECK_H
        zs = L.ZP + L.SLEEVE_H
        # grooves: a dark stripe in the middle of each face
        for k, (nx, ny) in enumerate(((0, -1), (1, 0), (0, 1), (-1, 0))):
            gx, gy = sx + nx * (a + 0.00005), sy + ny * (a + 0.00005)
            hw = 0.0006
            p = P("groove%d" % k, "groove", group=SEL_WORK, uv_name="groove", uv_origin=(gx, gy, L.ROD_Z0))
            if nx:
                g.box(p, gx - 0.0001, gx + 0.0001, gy - hw, gy + hw, L.ROD_Z0, ztop)
            else:
                g.box(p, gx - hw, gx + hw, gy - 0.0001, gy + 0.0001, L.ROD_Z0, ztop)
            parts.append(p)
            # latch recesses: two per groove (visible from the front and the right), the lower one
            # is in the sleeve now
            for j, zz in enumerate((zs + 0.005, zs + 0.005 - L.ROD_STROKE) if k < 2 else ()):
                q = P("notch%d_%d" % (k, j), "hole", group=SEL_WORK, uv_name="notch", uv_origin=(gx, gy, zz))
                if nx:
                    g.box(q, gx - 0.00015, gx + 0.00015, gy - 0.0012, gy + 0.0012, zz - 0.0010, zz + 0.0010)
                else:
                    g.box(q, gx - 0.0012, gx + 0.0012, gy - 0.00015, gy + 0.00015, zz - 0.0010, zz + 0.0010)
                parts.append(q)
    return parts


# =============================================================================
# Hose and indicator tube
# =============================================================================
def hose_points(lod):
    """From the fitting up, in a loop around the sleeve over the panel to the front, over the right edge
    of the flange down the wall (smoothly, Catmull-Rom), then the arcs from m85_layout.hose_route to
    the tube.
    """
    nx, ny = L.NIP
    zh = L.ZP + L.HOSE_R
    # from the fitting up and in a wide arc (~12 mm) forward-left onto the panel
    rise = [(nx, ny, L.ZP + 0.0016), (nx, ny, L.ZP + 0.0090), (nx - 0.0006, ny - 0.0058, L.ZP + 0.0142),
            (nx - 0.0026, ny - 0.0140, L.ZP + 0.0145), (nx - 0.0050, ny - 0.0225, L.ZP + 0.0100),
            (nx - 0.0072, ny - 0.0300, zh + 0.0010)]
    # loop over the panel around the sleeve (photo), to the right front corner; points every ~15-20
    # mm
    loop = [(L.DX0 + 0.0116, L.DY0 + 0.0390, zh), (L.DX0 + 0.0162, L.DY0 + 0.0220, zh),
            (L.DX0 + 0.0280, L.DY0 + 0.0115, zh), (L.DX0 + 0.0460, L.DY0 + 0.0085, zh),
            (L.DX0 + 0.0670, L.DY0 + 0.0090, zh), (L.DX0 + 0.0870, L.DY0 + 0.0120, zh),
            (L.DX1 - 0.0080, L.HOSE_Y - 0.0016, zh + 0.0006)]
    # over the flange edge: an arc around its upper outer corner, then down the wall
    cx, cz, rho = L.DX1 - L.LIP_IN - L.LIP_T * 0.5, L.ZL, L.HOSE_R + 0.0005
    drape = [(cx + rho * math.cos(math.radians(a)), L.HOSE_Y - 0.0008 * math.sin(math.radians(a)),
              cz + rho * math.sin(math.radians(a))) for a in (90.0, 55.0, 20.0)]
    drape += [(L.HOSE_X, L.HOSE_Y, L.ZS - 0.0010), (L.HOSE_X, L.HOSE_Y, L.ZS - 0.0120)]
    ctrl = rise + loop + drape
    # steps per segment: the rise from the fitting - 2, the loop turn at the left front corner - 3,
    # the straight run along the front - 2, over the edge - 2, along the wall - 1
    ks = [2] * len(rise) + [3, 3, 3, 2, 2, 2] + [2, 2, 2, 1, 1]
    top = spline(ctrl, ks) if lod == 0 else ctrl[::2] + ctrl[-1:]
    wall = [(L.HOSE_X, L.HOSE_Y, 0.090), (L.HOSE_X, L.HOSE_Y, L.HOSE_R + L.HOSE_R3)]
    low = L.HOSE_LOW if lod == 0 else L.HOSE_LOW[1::2] + L.HOSE_LOW[-1:]
    return top + wall + list(low)


def build_hose_tube(spec):
    lod = spec["lod"]
    parts = []
    pts = hose_points(lod)
    # hose ends are put on the fitting and on the tube - stretched, slightly thicker
    rad = [L.HOSE_R + 0.0004] * 2 + [L.HOSE_R] * (len(pts) - 4) + [L.HOSE_R + 0.0003] * 2
    hs = P("hose", "hose")
    g.tube_var(hs, pts, [(r, r) for r in rad], spec["hose"])
    parts.append(hs)
    fr = frame_axis(L.TUBE_A, L.TUBE_D)
    p0, p1 = L.TUBE_POWDER
    core = P("itube", "itube", group=SEL_TUBE)
    if spec["glass"]:
        gl = P("itube_glass", "glass", section="glass")
        lathe(gl, [(0.0016, 0.0), (0.0021, 0.0010), (L.TUBE_R, 0.0032), (L.TUBE_R, L.TUBE_L - 0.0032),
                   (0.0021, L.TUBE_L - 0.0010), (0.0016, L.TUBE_L)], 8, fr, cap0=-1, cap1=1)
        parts.append(gl)
        lathe(core, [(L.TUBE_RI, p0 - L.TUBE_PLUG), (L.TUBE_RI, p1 + L.TUBE_PLUG)], 8, fr, cap0=-1, cap1=1)
    else:
        lathe(core, [(0.0017, 0.0), (L.TUBE_R, 0.0030), (L.TUBE_R, L.TUBE_L - 0.0030), (0.0017, L.TUBE_L)], 6, fr,
              cap0=-1, cap1=1)
    parts.append(core)
    return parts


# =============================================================================
# Tube box
# =============================================================================
def tray(name, region, inner_region, x0, x1, y0, y1, z0, z1, wall, lod):
    """A cardboard box open at the top: the shell minus the inside (the walls are the region inner_region)."""
    raw = P(name + "_raw", region)
    g.box(raw, x0, x1, y0, y1, z0, z1, **(dict(r=0.0006, seg=1) if lod == 0 else {}))
    cut = P(name + "_cut", inner_region)
    g.box(cut, x0 + wall, x1 - wall, y0 + wall, y1 - wall, z0 + wall, z1 + 0.01)
    p = M.boolean("%s_%d" % (name, lod), raw, [cut])
    retag(p, facing(2, -1))
    return p


def build_box(spec):
    lod = spec["lod"]
    parts = []
    pad, lt = L.LIDB_PAD, L.LIDB_T
    parts.append(tray("box_lid", "carton_lid", "carton_lid", L.BX0 - pad, L.BX1 + pad, L.BY0 - pad, L.BY1 + pad,
                      0.0, L.LIDB_H, lt, lod))
    parts.append(tray("box", "carton", "insert", L.BX0, L.BX1, L.BY0, L.BY1, lt, lt + L.BH, L.CARD_T, lod))
    # label on the front end - a face of its own: at the cardboard scale (1) the print smeared
    (cx, cz), (w, h) = L.BOX_LABEL_C, L.BOX_LABEL
    lb = P("box_label", "box_label")
    y = L.BY0 - 0.0002
    g.quad(lb, [(cx - w / 2, y, cz - h / 2), (cx + w / 2, y, cz - h / 2), (cx + w / 2, y, cz + h / 2),
                (cx - w / 2, y, cz + h / 2)])
    parts.append(lb)
    ct = L.CARD_T
    xi0, xi1 = L.BX0 + ct, L.BX1 - ct
    parts.append(box("insert", "insert", xi0, xi1, L.BY0 + ct, L.BY1 - ct, lt + ct, L.INSERT_Z))
    # cradles under the tubes: the tubes lie on them and do not sink
    for k, yy in enumerate((L.SPARE_Y[0] + 0.012, L.SPARE_Y[1] - 0.012)):
        parts.append(box("cradle%d" % k, "insert", xi0, xi1, yy - 0.0015, yy + 0.0015, L.INSERT_Z,
                         L.SPARE_Z - L.TUBE_R, uv_name="cradle", uv_origin=(xi0, yy, L.INSERT_Z)))
    parts.append(box("divider", "insert", xi0, xi1, L.DIV_Y - 0.0006, L.DIV_Y + 0.0006, L.INSERT_Z, 0.020))
    # spare tubes along Y: glass with melted ends, inside swabs and powder of their own colour; on
    # the mid LOD they are opaque (the material gives glass at the ends, swabs, powder)
    y0, y1 = L.SPARE_Y
    ln = y1 - y0
    shell = [(0.0020, 0.0), (L.TUBE_R, 0.0012), (L.TUBE_R, ln - 0.0012), (0.0020, ln)]
    sgl = P("spare_glass", "glass", section="glass") if spec["glass"] else None
    for i in range(L.SPARE_N):
        fr = fy((L.SPARE_X0 + i * L.SPARE_PITCH, y0, L.SPARE_Z))
        core = P("spare%d" % i, "tubes")
        if sgl is not None:
            lathe(sgl, shell, 6, fr, cap0=-1, cap1=1)
            lathe(core, [(L.TUBE_RI, 0.0080), (L.TUBE_RI, ln - 0.0040)], 6, fr, cap0=-1, cap1=1)
        else:
            lathe(core, shell, 4, fr, cap0=-1, cap1=1)
        parts.append(core)
    if sgl is not None:
        parts.append(sgl)
    # ampoules along X: a bottom, a body, a shoulder, a neck, a drawn-out sealed tip; powder inside
    a0, a1 = L.AMP_X
    la, r = a1 - a0, L.AMP_R
    ag = P("amp_glass", "glass", section="glass") if spec["glass"] else None
    for i, yy in enumerate(L.AMP_Y):
        fr = fx((a0, yy, L.AMP_Z))
        core = P("amp%d" % i, "ampoule")
        shell = [(0.0012, 0.0), (0.0034, 0.0007), (r, 0.0028), (r, la - 0.016), (0.0015, la - 0.009),
                 (0.0005, la)]
        if ag is not None:
            lathe(ag, shell, 6, fr, cap0=-1, cap1=1)
            lathe(core, [(0.0030, 0.0010), (0.0035, 0.0022), (0.0035, la - 0.024)], 6, fr, cap0=-1, cap1=1)
        else:
            lathe(core, [shell[0], shell[2], shell[3], shell[4], shell[5]], 5, fr, cap0=-1, cap1=1)
        parts.append(core)
    if ag is not None:
        parts.append(ag)
    return parts


def build_lod(spec):
    parts = build_case(spec) + build_lid(spec) + build_panel(spec) + build_rod(spec) + build_hose_tube(spec) + \
        build_box(spec)
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("bounds", tuple(round(c, 4) for c in BOUNDS["lo"]), tuple(round(c, 4) for c in BOUNDS["hi"]))
        print("rod head top raised: %.4f" % (L.HEAD_TOP + L.ROD_STROKE))
        print("tube A %s D %s rest %s" % (tuple(round(c, 4) for c in L.TUBE_A), tuple(round(c, 3) for c in L.TUBE_D),
                                          tuple(round(c, 4) for c in L.TUBE_REST)))
        print("hose: %d points" % len(hose_points(0)))
    return parts


def collision():
    """Four convex parts: the body with brackets, clasp and strap; the sleeve with the rod; the opened
    lid; the tube box. The hose and the indicator tube have no collision (like the cords of M79). Mass
    is the item's weight in the mod, 0.8 kg.
    """
    body = kx.box_pts(L.DX0 - 0.0072, L.DX1 + 0.0072, L.DY0 - 0.006, L.DY1 + 0.0048, 0.0, L.ZL)
    rod = kx.box_pts(L.SX - L.SLEEVE_R - 0.0140, L.SX + L.FLANGE_R, L.SY - L.FLANGE_R, L.SY + L.FLANGE_R, L.ZP,
                     L.HEAD_TOP)
    lid = [tuple(LID_M @ Vector(q)) for q in kx.box_pts(L.DX0, L.DX1, L.DY0, L.DY1 + 0.0025, L.ZS, L.ZS + L.LID_H)]
    pad = L.LIDB_PAD
    kit = kx.box_pts(L.BX0 - pad, L.BX1 + pad, L.BY0 - pad, L.BY1 + pad, 0.0, L.LIDB_T + L.BH)
    comps = [(body, kx.PEN + r"\metalplate.rvmat"), (rod, kx.PEN + r"\metalplate.rvmat"),
             (lid, kx.PEN + r"\metalplate.rvmat"), (kit, kx.PEN + r"\plastic.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    memory = {
        # inventory preview camera: front-left and from above (invView = camera position)
        "invView": [(-0.30, -0.52, 0.42)],
        "ce_center": [(0.0, 0.0, 0.11)],
        "ce_radius": [(0.17, 0.0, 0.11)],
        # rod travel axis: the whole axis length is the sample stroke (offset1 = 1 at ozl_work_rise)
        "ozl_work_axis": [(L.SX, L.SY, L.HEAD_Z0), (L.SX, L.SY, L.HEAD_Z0 + L.ROD_STROKE)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, max(hi[2], L.HEAD_TOP + L.ROD_STROKE))
    return comps, 0.8, memory, bbox


SHOTS = [
    ("front", (-0.30, -0.55, 0.40), (0.0, 0.0, 0.10), 40),
    ("panel", (-0.09, -0.22, 0.42), (L.SX, L.SY, L.ZP + 0.012), 50),
    ("tubes", (0.24, -0.26, 0.22), (0.050, -0.010, 0.022), 45),
    ("right", (0.46, -0.22, 0.26), (0.0, 0.0, 0.10), 40),
    ("back", (-0.30, 0.44, 0.30), (-0.040, 0.0, 0.110), 40),
    ("lid", (-0.06, -0.36, 0.40), (L.DCX, L.DY1 + 0.035, L.ZS + 0.035), 55),
]
# --look preview: overall view, panel close-up, tubes and box, right side (strap, hose); the work
# look uses the first three
M.look_shots = (4, 3)

M.run(build_lod, collision, SHOTS, row_step=0.32, row_shot=((0.16, -1.15, 0.40), (0.16, 0, 0.10)))
