"""M80 - map board (OZL_Tool_MapBoard): a Trail line module, a portable 2x2 item. It sits in an
OZL_Tool1..3 slot of the packer (M15, M20) and shows on its shelf through the module_N proxy.
A tilted plywood board on a stand, a map under celluloid, an officer's ruler, a curvimeter and an
Adrianov compass on it.

    blender --background --python build_m80.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py (system Python) before the first build: the annotated map, the ruler, the
dials, the tag.

Size: about 0.20 x 0.10 x 0.20 m, tilt about 20 degrees, plywood, cloudy celluloid, a map of its
own that cannot be read, a ruler of green plastic. The module pad is about 0.2 x 0.2 m, up to
0.25 m high.

Proportions:
- Officer's ruler: 200 (205) x 100 mm, transparent green plastic, thickness 1-1.5 mm (a naval one
  is 262 x 102 x 1 mm). Stencils, coordinate measurers and the protractor follow a photo (without
  captions). Taken: 200 x 100 x 1.5, corners rounded R3.
- KU-A curvimeter (Zlatoust Watch Factory): the datasheet envelope is "not more than 100 x 40 x
  15 mm", a measured specimen is 89 x 39 x 14 mm, the scale is 0-100 cm. Taken: a lens-shaped body
  62 x 39 mm, thickness 10.4 mm at the rim and 13.7 at the glass, a 27 mm handle with a collar at
  the body and a brass eyelet at the end - about 0.094 m together with the wheel.
- Adrianov compass: diameter about 50 mm, height 16 mm, 43 g (a museum specimen is 52 x 17 mm).
  Taken: body diameter 43, sighting ring diameter 45.6, height 12.2 mm at the ring and 16.7 at
  the front sight; strap 16 mm; needle 27.6 mm on a brass pin.
- The board is 8 mm plywood (7 plies), 206 x 200 mm: it holds a 1 : 50 000 map folded in four (a
  sheet of about 40 x 45 cm -> about 20 x 22 cm); the width follows the ruler (200 mm) with a
  margin. There is no ready sample of such a board, so the stand is a simple pine desk: two 12 mm
  cheeks screwed into the rear rail, and a 12 x 31.5 mm lip at the front holds the board and
  whatever slides off it (the pen lies on it). Tilt 20 degrees.
- The celluloid lies over the map, held at the sides by black cloth tape (about 13 mm wide on the
  board face), at the top by an aluminium bar 200 x 18 x 3 on two M5 wing bolts (DIN 315, M5: wing
  span about 20 mm). The ruler is clamped under the bar too and sticks out past the top edge of
  the board by 12 mm.
- Size about 0.207 x 0.216 x 0.100 m - fits the module pad.

Condition (no faction colour): used but intact - the celluloid yellowed, scratched and cloudy,
traces of rubbed-out grease pencil; the plywood and the pine darkened, edges worn; the tape
dusty; the compass and curvimeter edges worn. Markings: scales and digits (ruler, curvimeter,
compass, map grid and heights), a radiation sign in grease pencil, an inventory tag with a
punched number - no letters.

Details: the "dayz" look (more matte, dirtier, corner shading in colour). Round parts are dense
(compass and curvimeter 32 sides); the wheel, wing nuts, washers and the eyelet are solids of
revolution with chamfers; chamfers on the cheeks, board, rail and bar; wing-nut wings are blades
with a rounded end. The compass strap is flat leather with rounded edges that wraps the lugs and
the lip along a smooth curve (fillet), not a kink; lugs and buckle are a rod with rounded
corners; the cheek screws are in the material. A vanilla DayZ pen (Pen) lies on the lip as a
proxy, clip up.

Work look: the compass needle is a separate part above the limb (the needle drawn in comp_top.png
is painted over in the comp material so that it does not double), the bone ozl_needle on the
source ozl_needle (rotation about the axis ozl_needle_axis, 0..24 degrees for the phase 0..1).
While the machine with the module works, OZL_WorkFx wobbles it (wobble). At rest (phase 0) the
needle stands as in the image. The board has no lamps or screens.
LODs: near and mid (no chamfers, washers, screws, tag, front sight, buckle, pin and eyelet; fewer
sides), no far one.

The ruler is a glass section (kexport.write_glass): its own _ca from make_decals.py
(ruler_ca.png) instead of the shared kexport.glass_ca - green transparent plastic, stencil
cut-outs transparent through. The ruler has no bottom (it lies on the celluloid), otherwise the
tone would double. The celluloid is not a separate part: the gloss, yellowing, scratches and
grease pencil are in the map sheet texture (as in the M68 window).

Blender axes: X is width, Y is depth (the face and the lip are at -Y), Z is up. The origin is the
centre of the bottom, so the module lands on the module_N proxy point (autocenter = 0 in Geometry).
"""
import math
import os
import shutil
import sys

import bmesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import kvanilla as kv  # noqa: E402
import kwood  # noqa: E402
import m80_layout as LY  # noqa: E402
from mathutils import Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m ------------------------------------------------------------------------------
A = math.radians(LY.TILT)
W, LB, T = LY.BOARD_W, LY.BOARD_L, LY.BOARD_T
Y_F, Z_F = -0.0890, 0.0140               # front lower edge of the board's underside (on the cheeks)
# board: a along X, b up the slope, c along the normal from the underside
BF = g.Frame((0.0, Y_F, Z_F), (1, 0, 0), (0, math.cos(A), math.sin(A)), (0, -math.sin(A), math.cos(A)))
FACE = T + LY.MAP_C                        # face of the map sheet (c)
Y_LB = Y_F - T * math.sin(A)              # back face of the lip (touches the board's top edge)
LEDGE_T = 0.012
Y_LF = Y_LB - LEDGE_T                      # face of the lip
Z_FACE0 = Z_F + T * math.cos(A)            # board face at the lip
LEDGE_H = Z_FACE0 + 0.010                  # the lip is 10 mm above the board face
LEDGE_R = 0.0018                           # chamfer of the lip edges
CHEEK_X = (0.074, 0.086)                   # stand cheeks
CHEEK_B = 0.176                            # the cheek ends under the board at b = 0.176
Y_CB = Y_F + CHEEK_B * math.cos(A)
Z_CB = Z_F + CHEEK_B * math.sin(A)
RULER_A0, RULER_A1 = LY.RULER_A - LY.RULER[0] / 2, LY.RULER_A + LY.RULER[0] / 2
RULER_B1 = LY.RULER_B0 + LY.RULER[1]
RULER_TOP = T + LY.RULER_C0 + LY.RULER[2]
BAR_C0 = RULER_TOP + 0.0001
# compass needle (a separate part above the limb, bone ozl_needle): half-length, half-width, bottom
# (c of the compass)
NEEDLE_LN, NEEDLE_W, NEEDLE_C, NEEDLE_T = LY.COMP_DIAL_R - 0.0034, 0.0015, 0.0112, 0.00025
NEEDLE_SWING = 24.0                        # degrees per phase 0..1 (wobble mid 0.5, amp 0.35: 12 +- 8)
LUG_C, LUG_R = 0.0042, 0.0008              # strap lugs: axis height (c of the compass), rod radius
# DayZ pen on the lip: middle x, the axis along the middle of the lip's top
PEN_X = -0.035
Y_LEDGE_C = (Y_LF + Y_LB) / 2

LOD_SPECS = [
    dict(lod=0, sides=16),
    dict(lod=1, sides=8),
]

REGIONS = {
    "ply": ("ply", 0.6), "map": ("map", 2.6), "tape": ("tape", 0.8),
    "pine_y": ("pine_y", 0.7), "pine_x": ("pine_x", 0.7), "ledge": ("ledge", 1.0),
    "alu": ("alu", 1.0), "nut": ("nut", 1.5), "steel": ("steel", 1.2),
    "curv": ("curv", 2.0), "curv_dial": ("curv", 3.2), "brass": ("brass", 2.0),
    "comp": ("comp", 2.0), "comp_dial": ("comp", 3.2),
    "leather": ("leather", 1.2), "buckle": ("buckle", 1.5), "tag": ("tag", 3.0),
    "ruler": ("ruler", 1.0), "needle": ("needle", 3.0), "lume": ("lume", 3.0), "dark": ("dark", 2.0),
}

SEL_NEEDLE = "ozl_needle"


def wdecal(name):
    return os.path.join(WORK, name)


def rot_frame(o, deg):
    """Frame on the board face at point o (BF a, b, c), rotated by deg about the normal:
    u is to the right, v is "up" of the image, n is away from the board.
    """
    t = math.radians(deg)
    u = BF.u * math.cos(t) + BF.v * math.sin(t)
    v = -BF.u * math.sin(t) + BF.v * math.cos(t)
    return g.Frame(BF.p(*o), u, v, BF.n)


CU = rot_frame((LY.CURV_C[0], LY.CURV_C[1], FACE + 0.0002), LY.CURV_ROT)   # curvimeter, v toward the handle
CO = rot_frame((LY.COMP_C[0], LY.COMP_C[1], FACE + 0.0002), 0.0)          # compass, v up the board


# =============================================================================
# Materials: the pattern is in board and instrument coordinates (frame), not world axes
# =============================================================================
def fc(t, origin, fr):
    """Point coordinates in the frame fr: sockets (a, b, c)."""
    tc = t.node("ShaderNodeTexCoord")
    tc.object = origin
    sub = t.node("ShaderNodeVectorMath")
    sub.operation = "SUBTRACT"
    sub.inputs[1].default_value = tuple(fr.o)
    t.link(tc.outputs["Object"], sub.inputs[0])
    outs = []
    for ax in (fr.u, fr.v, fr.n):
        dot = t.node("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        dot.inputs[1].default_value = tuple(ax)
        t.link(sub.outputs[0], dot.inputs[0])
        outs.append(dot.outputs["Value"])
    return outs


def facing(t, ax):
    """Cosine between the face normal and the axis ax."""
    geo = t.node("ShaderNodeNewGeometry")
    dot = t.node("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    dot.inputs[1].default_value = tuple(ax)
    t.link(geo.outputs["True Normal"], dot.inputs[0])
    return dot.outputs["Value"]


def wrap(mat):
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    return t


def disc_mask(t, a, b, pts, r0, r1):
    """1 inside circles (a, b) of radius r0, fading to nothing by r1."""
    out = None
    for pa, pb in pts:
        da, db = t.math("SUBTRACT", a, pa), t.math("SUBTRACT", b, pb)
        d = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", da, da), t.math("MULTIPLY", db, db)))
        m = t.maprange(d, r0, r1, 1.0, 0.0)
        out = m if out is None else t.math("MAXIMUM", out, m)
    return out


def mat_map(mat, origin):
    """Map sheet under celluloid: the picture map.png in board coordinates; the celluloid gloss is from
    map_gloss.png (grease pencil and scratches are matte); the instruments cast a light contact shadow.
    """
    t = kmats.Tree(mat)
    a, b, c = fc(t, origin, BF)
    m0, m1, m2, m3 = LY.MAP
    center, size = ((m0 + m1) / 2, (m2 + m3) / 2), (m1 - m0, m3 - m2)
    col, _ = t.image(wdecal("map.png"), a, b, center, size)
    gl_c, _ = t.image(wdecal("map_gloss.png"), a, b, center, size)
    gl_c.node.image.colorspace_settings.name = "Non-Color"
    gl = t.bw(gl_c)
    cav = t.maprange(t.cavity(0.010), 0.12, 0.55, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.45), col, kmats.GRIME)
    vec, _ = t.coords(origin, 3.3)
    up = t.maprange(t.noise(vec, 9.0, 4.0, 0.6), 0.45, 0.75, 0.0, 0.12)
    col = t.mixc(up, col, kmats.DUST)
    gloss = t.math("SUBTRACT", t.math("MULTIPLY", gl, 0.92), t.math("MULTIPLY", up, 0.6))
    spec = t.math("ADD", 0.05, t.math("MULTIPLY", gl, 0.55))
    h = t.math("MULTIPLY", t.math("SUBTRACT", 1.0, gl), -0.15)
    return kmats.out(t, col, gloss, spec, h)


def mat_ply(mat, origin, **kw):
    """FK plywood: birch veneer on the face and underside; on the edges 7 plies of 1.14 mm, the plies
    with cross grain are darker (end grain), thin glue seams between them.
    """
    outs = kwood.build_wood(mat, origin, **kw)
    t = wrap(mat)
    a, b, c = fc(t, origin, BF)
    edge = t.maprange(t.math("ABSOLUTE", facing(t, BF.n)), 0.35, 0.6, 1.0, 0.0)
    q = t.math("DIVIDE", c, T / 7.0)
    par = t.math("FLOORED_MODULO", t.math("FLOOR", q), 2.0)
    glue = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", t.math("FRACT", q), 0.5)), 0.40, 0.5, 0.0, 1.0)
    col = kmats.sock(mat, outs["color"])
    col = t.mixc(t.math("MULTIPLY", edge, t.math("MULTIPLY", par, 0.45)), col, kmats.lin((112, 82, 50)))
    col = t.mixc(t.math("MULTIPLY", edge, t.math("MULTIPLY", glue, 0.55)), col, kmats.lin((70, 52, 34)))
    return dict(outs, color=kmats.Tree.ref(col))


NAILS = [(x, z) for x in (-0.080, 0.080) for z in (0.0085, 0.0225)]


def mat_ledge(mat, origin, **kw):
    """Pine lip: wood, on the face nail heads into the cheeks (darkened, with a rusty halo)."""
    outs = kwood.build_wood(mat, origin, **kw)
    t = wrap(mat)
    _, sep = t.coords(origin, 0.0)
    front = t.maprange(facing(t, (0, -1, 0)), 0.5, 0.8, 0.0, 1.0)
    x, z = sep.outputs["X"], sep.outputs["Z"]
    head = t.math("MULTIPLY", disc_mask(t, x, z, NAILS, 0.0011, 0.0014), front)
    halo = t.math("MULTIPLY", disc_mask(t, x, z, NAILS, 0.0013, 0.0032), front)
    col = kmats.sock(mat, outs["color"])
    col = t.mixc(t.math("MULTIPLY", halo, 0.45), col, kmats.RUST[1])
    col = t.mixc(head, col, kmats.lin((58, 56, 54)))
    return dict(outs, color=kmats.Tree.ref(col))


# cheek screw into the end of the rear rail (y, z): in the middle of the rail
CHEEK_SCREW = (Y_CB - 0.0085, 0.0100)


def mat_cheek(mat, origin, **kw):
    """Pine cheek: wood, on the outer face a screw with a straight slot into the rail end (countersunk,
    with a dark halo from hands and damp).
    """
    outs = kwood.build_wood(mat, origin, **kw)
    t = wrap(mat)
    _, sep = t.coords(origin, 0.0)
    nx = facing(t, (1, 0, 0))
    outer = t.math("MULTIPLY", t.math("GREATER_THAN", t.math("MULTIPLY", sep.outputs["X"], nx), 0.0),
                   t.maprange(t.math("ABSOLUTE", nx), 0.6, 0.85, 0.0, 1.0))
    y, z = sep.outputs["Y"], sep.outputs["Z"]
    yc, zc = CHEEK_SCREW
    head = t.math("MULTIPLY", disc_mask(t, y, z, [CHEEK_SCREW], 0.0024, 0.0027), outer)
    halo = t.math("MULTIPLY", disc_mask(t, y, z, [CHEEK_SCREW], 0.0026, 0.0048), outer)
    ang = math.radians(35.0)
    across = t.math("SUBTRACT", t.math("MULTIPLY", t.math("SUBTRACT", z, zc), math.cos(ang)),
                    t.math("MULTIPLY", t.math("SUBTRACT", y, yc), math.sin(ang)))
    slot = t.math("MULTIPLY", t.maprange(t.math("ABSOLUTE", across), 0.00025, 0.00040, 1.0, 0.0),
                  t.math("MULTIPLY", disc_mask(t, y, z, [CHEEK_SCREW], 0.0020, 0.0022), outer))
    col = kmats.sock(mat, outs["color"])
    col = t.mixc(t.math("MULTIPLY", halo, 0.40), col, kmats.lin((54, 40, 28)))
    col = t.mixc(head, col, kmats.lin((92, 88, 82)))
    col = t.mixc(slot, col, kmats.lin((22, 20, 18)))
    return dict(outs, color=kmats.Tree.ref(col))


DIAL_BLACK = kmats.lin((16, 16, 18))


def mat_decal_plastic(mat, origin, fr=None, img=None, center=(0, 0), size=(0.01, 0.01), c_min=0.0,
                      dial_r=0.0, glass_gloss=0.85, knurl=None, needle=None, darken=0.0, **kw):
    """Instrument plastic (bakelite) with a face picture in the frame fr: the picture is on faces looking
    along fr.n above c_min; under the glass (r < dial_r) it is glossier. knurl = (r, c0, c1, n) -
    ribbing on the ring side; needle = (degrees, half-length, half-width) - the needle drawn in the
    picture is painted over with the limb colour (the needle is a separate part above the limb and
    wobbles in the work look). darken is a fraction toward black over the wear: the tone patches of
    the "dayz" profile mix in white, and nearly black plastic comes out grey (~80 of 255), lighter
    than vanilla black plastic.
    """
    outs = kmats.build_plastic(mat, origin, **kw)
    t = wrap(mat)
    a, b, c = fc(t, origin, fr)
    col = kmats.sock(mat, outs["color"])
    if darken > 0:
        col = t.mixc(darken, col, (0.0, 0.0, 0.0, 1.0))
    gl = kmats.sock(mat, outs["gloss"])
    up = t.math("MULTIPLY", t.math("GREATER_THAN", facing(t, fr.n), 0.55), t.math("GREATER_THAN", c, c_min))
    ic, ia = t.image(img, a, b, center, size)
    m = t.math("MULTIPLY", ia, up)
    col = t.mixc(m, col, ic)
    rr = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", a, a), t.math("MULTIPLY", b, b)))
    glass = t.math("MULTIPLY", t.math("LESS_THAN", rr, dial_r), up)
    gl = t.mixf(glass, gl, glass_gloss)
    if needle:
        deg, ln, hw = needle
        an = math.radians(90.0 + deg)
        along = t.math("ADD", t.math("MULTIPLY", a, math.cos(an)), t.math("MULTIPLY", b, math.sin(an)))
        across = t.math("SUBTRACT", t.math("MULTIPLY", b, math.cos(an)), t.math("MULTIPLY", a, math.sin(an)))
        strip = t.math("MULTIPLY", t.math("LESS_THAN", t.math("ABSOLUTE", along), ln + 0.0006),
                       t.math("LESS_THAN", t.math("ABSOLUTE", across), hw + 0.0005))
        hub = t.math("LESS_THAN", rr, 0.0013)
        col = t.mixc(t.math("MULTIPLY", t.math("MAXIMUM", strip, hub), glass), col, DIAL_BLACK)
    if knurl:
        r0, c0, c1, n = knurl
        side = t.maprange(t.math("ABSOLUTE", facing(t, fr.n)), 0.3, 0.5, 1.0, 0.0)
        band = t.math("MULTIPLY", t.math("GREATER_THAN", rr, r0),
                      t.math("MULTIPLY", t.math("GREATER_THAN", c, c0), t.math("LESS_THAN", c, c1)))
        ang = t.math("ARCTAN2", b, a)
        rib = t.math("ABSOLUTE", t.math("SUBTRACT", t.math("FRACT", t.math("MULTIPLY", ang, n / (2 * math.pi))), 0.5))
        rib = t.math("MULTIPLY", t.maprange(rib, 0.15, 0.35, 1.0, 0.0), t.math("MULTIPLY", side, band))
        col = t.mixc(t.math("MULTIPLY", rib, 0.5), col, kmats.lin((78, 70, 62)))
    return dict(outs, color=kmats.Tree.ref(col), gloss=kmats.Tree.ref(gl))


def mat_leather(mat, origin, holes=(), **kw):
    """Leather strap: brown, rubbed lighter on the edges and bends; holes in the upper half
    (holes = [(a, b)] in board coordinates).
    """
    outs = kmats.build_plastic(mat, origin, **kw)
    t = wrap(mat)
    a, b, c = fc(t, origin, BF)
    up = t.math("GREATER_THAN", facing(t, BF.n), 0.5)
    col = kmats.sock(mat, outs["color"])
    m = t.math("MULTIPLY", disc_mask(t, a, b, holes, 0.0009, 0.0012), up)
    col = t.mixc(m, col, (0.006, 0.004, 0.003, 1))
    ring = t.math("MULTIPLY", disc_mask(t, a, b, holes, 0.0011, 0.0020), up)
    col = t.mixc(t.math("MULTIPLY", ring, 0.4), col, kmats.lin((40, 26, 16)))
    return dict(outs, color=kmats.Tree.ref(col))


def mat_tag(mat, origin, decal_items=(), **kw):
    """Aluminium tag: metal with a punched number on top."""
    outs = kmats.build_steel(mat, origin, **kw)
    t = wrap(mat)
    _, sep = t.coords(origin, 0.0)
    col = kmats.decals(t, kmats.sock(mat, outs["color"]), sep, t.normal(), decal_items)
    return dict(outs, color=kmats.Tree.ref(col))


TAG_DEC = (wdecal("tag.png"), "y", -1, ("x", "z"), (LY.TAG_X, LY.TAG_Z), LY.TAG, (Y_LF - 0.0012, Y_LF))
HOLES = []
_hb = LY.STRAP_HOLES[0]
while _hb <= LY.STRAP_HOLES[1] + 1e-6:
    HOLES.append((LY.COMP_C[0], _hb))
    _hb += LY.STRAP_HOLES[2]

PINE = kmats.lin((146, 108, 70))                 # pine, darkened by time and hands
KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "map": (mat_map, {}),
    "ply": (mat_ply, dict(color=kmats.lin((206, 172, 124)), seed=1.3, along="y", rings=0.25, knots=0.2, dust=0.2,
                          grime=0.25)),
    "pine_y": (mat_cheek, dict(color=PINE, seed=2.1, along="y", rings=0.5, knots=0.4, dust=0.3, grime=0.65)),
    "pine_x": (kwood.build_wood, dict(color=PINE, seed=2.9, along="x", rings=0.5, knots=0.4, dust=0.3, grime=0.65)),
    "ledge": (mat_ledge, dict(color=PINE, seed=3.4, along="x", rings=0.5, knots=0.3, dust=0.25, grime=0.6)),
    # black cloth tape: matte, dusty
    "tape": ("plastic", dict(color=kmats.lin((30, 29, 28)), seed=4.1, gloss=0.10, spec=0.05, mottle=0.18, dust=0.15,
                             grime=0.2, scuff=(0.80, 0.90))),
    "alu": ("steel", dict(seed=4.6, tone=0.34, along="x", gloss=0.42, spec=0.50, dust=0.3, grime=0.4)),
    "nut": ("steel", dict(seed=5.2, tone=0.24, along="z", gloss=0.45, spec=0.55, dust=0.3, grime=0.5)),
    # curvimeter: black plastic, the face is curv_top.png
    "curv": (mat_decal_plastic, dict(color=kmats.lin((18, 18, 19)), seed=5.8, gloss=0.50, spec=0.35, dust=0.04,
                                     grime=0.15, scuff=(0.80, 0.88), fr=CU, img=wdecal("curv_top.png"),
                                     size=(0.044, 0.066), c_min=0.0095, dial_r=LY.CURV_DIAL_R + 0.0004,
                                     darken=0.45)),
    "brass": ("paint", dict(color=kmats.lin((168, 132, 66)), under=kmats.lin((120, 92, 44)), seed=6.3, gloss=0.6,
                            spec=0.6, chip=(0.9, 0.95), rust=(0.97, 0.99), rust_low=0.0, dust=0.05, grime=0.5)),
    # compass: bakelite, the limb and ring are comp_top.png, ribbing on the ring side; the drawn
    # needle is painted over
    "comp": (mat_decal_plastic, dict(color=kmats.lin((26, 22, 20)), seed=6.9, gloss=0.45, spec=0.35, mottle=0.12,
                                     dust=0.12, grime=0.2, scuff=(0.66, 0.74), fr=CO, img=wdecal("comp_top.png"),
                                     size=(0.048, 0.048), c_min=0.0080, dial_r=LY.COMP_DIAL_R,
                                     knurl=(LY.COMP_BEZEL_R - 0.0006, 0.0086, 0.0113, 120),
                                     needle=(LY.NEEDLE_DEG, NEEDLE_LN, NEEDLE_W), darken=0.25)),
    # compass needle: blued steel under glass; the north end is yellowed luminous compound
    "needle": ("plastic", dict(color=kmats.lin((40, 44, 58)), seed=7.1, gloss=0.55, spec=0.45, mottle=0.04,
                               dust=0.02, grime=0.05, scuff=(0.95, 1.0))),
    "lume": ("flat", dict(color=kmats.lin((206, 222, 168)), gloss=0.35, spec=0.2)),
    "dark": ("flat", dict(color=kmats.lin((10, 10, 10)), gloss=0.1, spec=0.05)),
    # leather: the "dayz" profile multiplies dust by 1.8 and mutes colour - so the values are darker
    # and less dusty than the plain ones
    "leather": (mat_leather, dict(color=kmats.lin((84, 50, 26)), seed=7.5, gloss=0.30, spec=0.15, mottle=0.22,
                                  dust=0.06, grime=0.3, scuff=(0.62, 0.72), holes=HOLES)),
    "buckle": ("steel", dict(seed=8.1, tone=0.26, along="x", gloss=0.55, spec=0.6, dust=0.1, grime=0.4)),
    "tag": (mat_tag, dict(seed=8.6, tone=0.36, along="x", gloss=0.45, spec=0.5, dust=0.15, grime=0.3,
                          decal_items=[TAG_DEC])),
    "ruler": ("flat", dict(color=kmats.lin((150, 200, 160)), gloss=0.9, spec=0.8)),   # glass section, not baked
})


def ruler_ca(path_png, **_):
    """Instead of the shared kexport.glass_ca: the ruler from make_decals.py (cut-outs are transparent through)."""
    src = wdecal("ruler_ca.png")
    if not os.path.exists(src):
        raise SystemExit("missing %s - run make_decals.py first" % src)
    os.makedirs(os.path.dirname(path_png), exist_ok=True)
    shutil.copy2(src, path_png)


kx.glass_ca = ruler_ca

# work look: the compass needle wobbles (OZL_WorkFx wobble on the source ozl_needle); phase 0 is
# rest
NEEDLE_ANIM = ("ozl_needle_swing", dict(type="rotation", source=SEL_NEEDLE, selection=SEL_NEEDLE,
                                        axis="ozl_needle_axis", memory=1, minValue=0.0, maxValue=1.0,
                                        angle0=0.0, angle1=math.radians(NEEDLE_SWING)))
# vanilla item: a pen on top of the lip, along it, clip up (lies on the body)
DECOR = [kv.put("pen", (PEN_X, Y_LEDGE_C, LEDGE_H), up=(1, 0, 0), fwd=(0, 0, -1), lods=(0, 1))]

OBJ, NAME = "m80_map_board", "ozr_map_board"
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, glass=dict(), look="dayz",
                 selections=(SEL_NEEDLE,), bones=((SEL_NEEDLE, ""),), animations=(NEEDLE_ANIM,),
                 sources={SEL_NEEDLE: dict(animPeriod=0.2)}, decor=DECOR)
P = M.part
BOUNDS = {}


# =============================================================================
# Primitives missing from kgeo
# =============================================================================
def lathe(part, fr, prof, sides, cap_lo=False, cap_hi=False, a0=0.0):
    """Solid of revolution about fr.n (from M76): the profile [(r, h)] from bottom to top, faces outward."""
    bm = part.bm
    angs = [a0 + 2 * math.pi * k / sides for k in range(sides)]
    rings = [[bm.verts.new(fr.p(r * math.cos(a), r * math.sin(a), h)) for a in angs] for r, h in prof]
    faces = []
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        for k in range(sides):
            j = (k + 1) % sides
            f = bm.faces.new([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]])
            am = a0 + (k + 0.5) * 2 * math.pi / sides
            want = (fr.u * math.cos(am) + fr.v * math.sin(am)) * (h1 - h0) - fr.n * (r1 - r0)
            f.normal_update()
            if f.normal.dot(want) < 0:
                f.normal_flip()
            faces.append(f)
    for ring, sign, on in ((rings[0], -1, cap_lo), (rings[-1], 1, cap_hi)):
        if on:
            f = bm.faces.new(ring)
            f.normal_update()
            if f.normal.dot(fr.n) * sign < 0:
                f.normal_flip()
            faces.append(f)
    return part.tag(faces)


def loft(part, fr, outline, rings, cap_lo=True, cap_hi=True):
    """Slab along the outline [(u, v)] (convex, counter-clockwise): rings [(scale, c)] from bottom to
    top - a rounded lip; the caps are polygons.
    """
    bm = part.bm
    before = set(bm.faces)
    vs = [[bm.verts.new(fr.p(u * s, v * s, c)) for u, v in outline] for s, c in rings]
    n = len(outline)
    for i in range(len(rings) - 1):
        for k in range(n):
            j = (k + 1) % n
            bm.faces.new([vs[i][k], vs[i][j], vs[i + 1][j], vs[i + 1][k]])
    if cap_lo:
        bm.faces.new(vs[0][::-1])
    if cap_hi:
        bm.faces.new(vs[-1])
    faces = [f for f in bm.faces if f not in before]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return part.tag(faces)


def fillet(pts, r, n=2, min_turn=12.0):
    """Polyline with rounded corners (strap, rod - no kinks): at each inner corner an arc (a quadratic
    Bezier) of radius about r in n segments; r is a number or a per-point list (0 keeps the corner);
    nearly straight corners (a turn below min_turn degrees) are left alone.
    """
    pts = [Vector(p) for p in pts]
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        ri = r[i] if isinstance(r, (list, tuple)) else r
        a, p, b = pts[i - 1], pts[i], pts[i + 1]
        d1, d2 = a - p, b - p
        l1, l2 = d1.length, d2.length
        d1.normalize()
        d2.normalize()
        th = math.acos(max(-1.0, min(1.0, d1.dot(d2))))
        if ri <= 0 or math.pi - th < math.radians(min_turn):
            out.append(p)
            continue
        t = min(ri / math.tan(th / 2), 0.45 * l1, 0.45 * l2)
        p0, p2 = p + d1 * t, p + d2 * t
        for k in range(n + 1):
            s = k / n
            out.append(p0 * (1 - s) ** 2 + p * (2 * s * (1 - s)) + p2 * (s * s))
    out.append(pts[-1])
    return out


# strap section: the near LOD is a flat hexagon (rounded edges), the mid one a rectangle
STRAP_PROF = {0: [(1.0, 0.0), (0.94, 1.0), (-0.94, 1.0), (-1.0, 0.0), (-0.94, -1.0), (0.94, -1.0)],
              1: [(1.0, 1.0), (-1.0, 1.0), (-1.0, -1.0), (1.0, -1.0)]}


def strap(part, pts, half_w, half_t, lod, out_hint):
    """Strap along a planar curve pts (plane x = const): width along X, thickness along the curve's
    normal in its plane (outward from the support - out_hint at the first point, no flips afterwards);
    half_w[i] is the half-width at a point.
    """
    bm = part.bm
    pts = [Vector(p) for p in pts]
    n = len(pts)
    X = Vector((1.0, 0.0, 0.0))
    prof = STRAP_PROF[0 if lod == 0 else 1]
    rings, prev = [], Vector(out_hint)
    for i in range(n):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        up = t.cross(X).normalized()
        if up.dot(prev) < 0:
            up = -up
        prev = up
        rings.append([bm.verts.new(pts[i] + X * (s * half_w[i]) + up * (q * half_t)) for s, q in prof])
    new = []
    m = len(prof)
    for i in range(n - 1):
        r0, r1 = rings[i], rings[i + 1]
        for k in range(m):
            j = (k + 1) % m
            new.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    new.append(bm.faces.new(rings[0][::-1]))
    new.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def flat_poly(part, pts, nrm):
    """A single flat face from points, facing nrm."""
    bm = part.bm
    f = bm.faces.new([bm.verts.new(Vector(p)) for p in pts])
    f.normal_update()
    if f.normal.dot(Vector(nrm)) < 0:
        f.normal_flip()
    return part.tag([f])


def rounded_rect(a0, a1, b0, b1, r, seg):
    """Outline of a rectangle with rounded corners (counter-clockwise, from the lower right corner)."""
    pts = []
    for ca, cb, ang0 in ((a1 - r, b0 + r, -90.0), (a1 - r, b1 - r, 0.0), (a0 + r, b1 - r, 90.0),
                         (a0 + r, b0 + r, 180.0)):
        for k in range(seg + 1):
            t = math.radians(ang0 + 90.0 * k / seg)
            pts.append((ca + r * math.cos(t), cb + r * math.sin(t)))
    return pts


def place_box(part, fr, x0, x1, y0, y1, z0, z1, **kw):
    return g.box(part, x0, x1, y0, y1, z0, z1, frame=fr, **kw)


def use(part, region):
    """The part's next faces go to another region (look and scale from REGIONS)."""
    return part.use(region, *REGIONS[region])


def bev(lod, r, seg=1):
    return {"r": r, "seg": seg} if lod == 0 else {}


# =============================================================================
# Stand and board
# =============================================================================
def build_stand(spec):
    lod = spec["lod"]
    parts = []
    for s, nm in ((-1, "cheek_l"), (1, "cheek_r")):
        ch = P(nm, "pine_y", uv_name="cheek")
        y0 = Y_LB
        z0 = Z_F + (y0 - Y_F) * math.tan(A) - 0.0003          # cheek top is 0.3 mm below the board's underside
        # cheek bottom is a shallow arch between two legs (a carpenter's desk); the rear leg is
        # under the rail
        ya, yb = y0 + 0.024, Y_CB - 0.024
        k_n = 4 if lod == 0 else 2
        arch = [(ya + (yb - ya) * k / k_n, 0.005 * math.sin(math.pi * k / k_n)) for k in range(1, k_n)]
        poly = [(y0, 0.0), (ya, 0.0)] + arch + [(yb, 0.0), (Y_CB, 0.0), (Y_CB, Z_CB - 0.0003), (y0, z0)]
        x0, x1 = sorted((s * CHEEK_X[0], s * CHEEK_X[1]))
        g.prism(ch, poly, (1, 2), x0, x1)
        if lod == 0:
            g.bevel(ch.bm, ch.bm.edges[:], 0.0012, 1)          # worn cheek edges
        parts.append(ch)
    rail = P("rail", "pine_x")
    g.box(rail, -CHEEK_X[0], CHEEK_X[0], Y_CB - 0.016, Y_CB - 0.001, 0.0, 0.020, **bev(lod, 0.0015))
    parts.append(rail)
    ledge = P("ledge", "ledge")
    g.box(ledge, -W / 2, W / 2, Y_LF, Y_LB, 0.0, LEDGE_H, **bev(lod, LEDGE_R, 2))
    parts.append(ledge)
    if lod == 0:
        tg = P("tag", "tag")
        tw, th = LY.TAG
        g.box(tg, LY.TAG_X - tw / 2, LY.TAG_X + tw / 2, Y_LF - 0.0006, Y_LF, LY.TAG_Z - th / 2, LY.TAG_Z + th / 2)
        parts.append(tg)
    return parts


def build_board(spec):
    lod = spec["lod"]
    parts = []
    bd = P("board", "ply")
    g.box(bd, -W / 2, W / 2, 0.0, LB, 0.0, T, frame=BF, **bev(lod, 0.0012))
    parts.append(bd)
    mp = P("map", "map")
    m0, m1, m2, m3 = LY.MAP
    g.quad(mp, [BF.p(m0, m2, FACE), BF.p(m1, m2, FACE), BF.p(m1, m3, FACE), BF.p(m0, m3, FACE)])
    parts.append(mp)
    # tape: a U around the side edge, from the face to the underside; on the near LOD it wraps the
    # board chamfer
    tt = 0.00025
    for s, nm in ((-1, "tape_l"), (1, "tape_r")):
        tp = P(nm, "tape")
        bm_ = (0.004 + LY.TAPE_B1) / 2
        half = (LY.TAPE_B1 - 0.004) / 2
        e = W / 2 + tt
        path = [(W / 2 - LY.TAPE_IN, FACE + tt + 0.0001), (e, FACE + tt + 0.0001), (e, -tt), (W / 2 - 0.006, -tt)]
        pts = [BF.p(s * a, bm_, c) for a, c in path]
        if lod == 0:
            pts = fillet(pts, 0.0015, 2)
        g.sweep(tp, pts, BF.v, tt, half)
        parts.append(tp)
    return parts


def build_ruler(spec):
    """Ruler: top and edges (no bottom), rounded corners; a glass section; UV maps its own frame onto the
    ruler_ca picture.
    """
    p = P("ruler", "ruler", section="glass")
    bm = p.bm
    c0, c1 = T + LY.RULER_C0, RULER_TOP
    a0, a1, b0, b1 = RULER_A0, RULER_A1, LY.RULER_B0, RULER_B1
    pts = rounded_rect(a0, a1, b0, b1, 0.003, 3 if spec["lod"] == 0 else 1)
    top = [bm.verts.new(BF.p(a, b, c1)) for a, b in pts]
    bot = [bm.verts.new(BF.p(a, b, c0)) for a, b in pts]
    faces = [bm.faces.new(top)]
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new([bot[i], bot[j], top[j], top[i]]))
    p.tag(faces)
    bm.normal_update()
    p.glass_frame = (BF, a0, a1, b0, b1)
    return [p]


# DIN 315 wing-nut wing in the nut's (a, c) plane: from the hub up and out, the end rounded
WING_LOD0 = [(0.0030, 0.0006), (0.0068, 0.0022), (0.0092, 0.0041), (0.0103, 0.0063), (0.0101, 0.0082),
             (0.0091, 0.0094), (0.0077, 0.0096), (0.0058, 0.0084), (0.0035, 0.0063)]
WING_LOD1 = [(0.0032, 0.0008), (0.0102, 0.0060), (0.0034, 0.0062)]


def build_clamp(spec):
    """Aluminium clamp bar on two M5 bolts with wing nuts and washers."""
    lod = spec["lod"]
    parts = []
    bar = P("bar", "alu")
    g.box(bar, -0.100, 0.100, LY.BAR_B[0], LY.BAR_B[1], BAR_C0, BAR_C0 + LY.BAR_T, frame=BF, **bev(lod, 0.0008))
    parts.append(bar)
    bmid = (LY.BAR_B[0] + LY.BAR_B[1]) / 2
    ctop = BAR_C0 + LY.BAR_T
    for s in (-1, 1):
        nf = g.Frame(BF.p(s * LY.BOLT_A, bmid, ctop), BF.u, BF.v, BF.n)
        org = tuple(nf.o)
        z0 = 0.0
        if lod == 0:
            ws = P("washer%d" % s, "nut", uv_name="washer", uv_origin=org)
            lathe(ws, nf, [(0.0050, 0.0), (0.0050, 0.0010), (0.0028, 0.0010)], 12)
            parts.append(ws)
            z0 = 0.0010
        hub = P("hub%d" % s, "nut", uv_name="hub", uv_origin=org)
        prof = ([(0.0046, z0), (0.0046, z0 + 0.0012), (0.0036, z0 + 0.0060), (0.0026, z0 + 0.0068)] if lod == 0 else
                [(0.0046, z0), (0.0046, z0 + 0.0015), (0.0038, z0 + 0.0062), (0.0030, z0 + 0.0064)])
        lathe(hub, nf, prof, 12 if lod == 0 else 6, cap_hi=True)
        parts.append(hub)
        wings = P("wings%d" % s, "nut", uv_name="wings", uv_origin=org)
        for sg in (-1, 1):
            poly = [(a, z0 + c) for a, c in (WING_LOD0 if lod == 0 else WING_LOD1)]
            if sg < 0:
                poly = [(-a, c) for a, c in poly[::-1]]
            g.prism(wings, poly, (0, 2), -0.0008, 0.0008, frame=nf)
        parts.append(wings)
        if lod == 0:
            # bolt end above the hub: a thread with a chamfer on the tip
            tip = P("bolt%d" % s, "steel", uv_name="bolt", uv_origin=org)
            lathe(tip, nf, [(0.0024, z0 + 0.0062), (0.0024, z0 + 0.0078), (0.0019, z0 + 0.0083)], 10, cap_hi=True)
            parts.append(tip)
    return parts


# =============================================================================
# KU-A curvimeter
# =============================================================================
def vesica(seg):
    """Outline of the lens-shaped body: a circle of radius R and tangents to the tips at +-TIP along v
    (counter-clockwise).
    """
    R, TIP = LY.CURV_R, LY.CURV_TIP
    al = math.acos(R / TIP)
    pts = [(0.0, TIP)]
    for i in range(seg + 1):
        th = math.pi / 2 + al + (math.pi - 2 * al) * i / seg
        pts.append((R * math.cos(th), R * math.sin(th)))
    pts.append((0.0, -TIP))
    for i in range(seg + 1):
        th = 3 * math.pi / 2 + al + (math.pi - 2 * al) * i / seg
        pts.append((R * math.cos(th), R * math.sin(th)))
    return pts


def build_curv(spec):
    lod = spec["lod"]
    parts = []
    TIP = LY.CURV_TIP
    nn = 32 if lod == 0 else 12
    body = P("curv_body", "curv")
    rings = ([(0.88, 0.0005), (0.96, 0.0014), (1.0, 0.0032), (1.0, 0.0072), (0.97, 0.0092), (0.90, 0.0104)]
             if lod == 0 else [(0.94, 0.0006), (1.0, 0.0030), (1.0, 0.0080), (0.92, 0.0104)])
    loft(body, CU, vesica(9 if lod == 0 else 4), rings)
    parts.append(body)
    bz = P("curv_bezel", "curv")
    lathe(bz, CU, [(0.0182, 0.0100), (0.0182, 0.0113), (0.0166, 0.0117)] if lod == 0 else
          [(0.0182, 0.0100), (0.0182, 0.0112), (0.0175, 0.0117), (0.0166, 0.0117)], nn)
    parts.append(bz)
    dl = P("curv_dial", "curv_dial")
    # dial glass is a dome (the face picture is in the material)
    prof = ([(0.0166, 0.0117), (0.0128, 0.0129), (0.0060, 0.0136)]
            if lod == 0 else [(0.0166, 0.0117), (0.0120, 0.0129), (0.0060, 0.0135)])
    lathe(dl, CU, prof, nn, cap_hi=True)
    parts.append(dl)
    # handle from the upper tip: a collar at the body, a shaft, a rounded end
    hd = P("curv_handle", "curv")
    hc = 0.0057
    H = LY.CURV_HANDLE
    if lod == 0:
        vs = [TIP - 0.006, TIP + 0.0005, TIP + 0.0018, TIP + 0.0032, TIP + H - 0.0040, TIP + H - 0.0018,
              TIP + H - 0.0006, TIP + H]
        rs = [0.0040, 0.0046, 0.0046, 0.0041, 0.0041, 0.0038, 0.0029, 0.0014]
    else:
        vs = [TIP - 0.006, TIP + 0.0015, TIP + 0.0035, TIP + H - 0.003, TIP + H - 0.0008, TIP + H]
        rs = [0.0040, 0.0047, 0.0041, 0.0041, 0.0034, 0.0016]
    g.tube_var(hd, [CU.p(0, v, hc) for v in vs], [(r, r) for r in rs], 12 if lod == 0 else 6)
    parts.append(hd)
    if lod == 0:
        # brass eyelet at the end of the handle: a hole through it for a lace
        ef = g.Frame(CU.p(0, TIP + H - 0.0045, hc), CU.u, CU.v, CU.n)
        ey = P("curv_eyelet", "brass")
        lathe(ey, ef, [(0.0023, 0.0035), (0.0023, 0.0040), (0.0019, 0.0044), (0.0012, 0.0042)], 12)
        use(ey, "dark")
        lathe(ey, ef, [(0.0012, 0.00418)], 12, cap_hi=True)
        parts.append(ey)
    # fork and wheel at the lower tip
    vw = -TIP - 0.0012
    fk = P("curv_fork", "curv")
    for s in (-1, 1):
        place_box(fk, CU, s * 0.0022 - 0.0006, s * 0.0022 + 0.0006, vw - 0.0028, -TIP + 0.0060, 0.0020, 0.0088)
    parts.append(fk)
    wh = P("curv_wheel", "brass")
    if lod == 0:
        # wheel: a rim with chamfers, the axis along the curvimeter's u
        wf = g.Frame(CU.p(0.0, vw, 0.0052), CU.v, CU.n, CU.u)
        lathe(wh, wf, [(0.0028, -0.0016), (0.0040, -0.0010), (0.0040, 0.0010), (0.0028, 0.0016)], 14,
              cap_lo=True, cap_hi=True)
    else:
        g.cyl(wh, (0.0, vw, 0.0052), "x", 0.0040, 0.0032, 6, frame=CU)
    parts.append(wh)
    if lod == 0:
        ax = P("curv_axle", "steel")
        g.cyl(ax, (0.0, vw, 0.0052), "x", 0.0010, 0.0060, 8, frame=CU)
        parts.append(ax)
    return parts


# =============================================================================
# Adrianov compass with a strap
# =============================================================================
def build_needle(lod):
    """Needle above the limb (bone ozl_needle): a rhombus of blued steel, the north end is luminous
    compound, a brass pin in the centre. At rest it points along the drawn needle (NEEDLE_DEG).
    """
    an = math.radians(90.0 + LY.NEEDLE_DEG)
    d = CO.u * math.cos(an) + CO.v * math.sin(an)
    q = CO.u * -math.sin(an) + CO.v * math.cos(an)
    nf = g.Frame(CO.o, d, q, CO.n)
    ln, w = NEEDLE_LN, NEEDLE_W
    parts = []
    nd = P("needle", "needle", group=SEL_NEEDLE)
    g.prism(nd, [(ln, 0.0), (0.0, w), (-ln, 0.0), (0.0, -w)], (0, 1), NEEDLE_C, NEEDLE_C + NEEDLE_T, frame=nf)
    use(nd, "lume")
    top = NEEDLE_C + NEEDLE_T + 0.00004
    flat_poly(nd, [nf.p(ln - 0.0003, 0.0, top), nf.p(0.45 * ln, 0.5 * w, top), nf.p(0.45 * ln, -0.5 * w, top)],
              CO.n)
    parts.append(nd)
    if lod == 0:
        pv = P("needle_pivot", "brass", group=SEL_NEEDLE)
        lathe(pv, CO, [(0.0010, NEEDLE_C - 0.0005), (0.0010, NEEDLE_C + 0.0006), (0.0007, NEEDLE_C + 0.0009)], 8,
              cap_hi=True)
        parts.append(pv)
    return parts


def build_compass(spec):
    lod = spec["lod"]
    parts = []
    nn = 32 if lod == 0 else 14
    body = P("comp_body", "comp")
    lathe(body, CO, [(0.0185, 0.0004), (0.0205, 0.0012), (LY.COMP_R, 0.0030), (LY.COMP_R, 0.0086)], nn, cap_lo=True)
    parts.append(body)
    RB = LY.COMP_BEZEL_R
    bz = P("comp_bezel", "comp")
    lathe(bz, CO, [(LY.COMP_R - 0.0004, 0.0086), (RB, 0.0086), (RB, 0.0113), (RB - 0.0006, 0.0120),
                   (0.0190, 0.0122), (LY.COMP_DIAL_R + 0.0004, 0.0118)], nn)
    parts.append(bz)
    # inner wall of the ring on the mid LOD too: the limb is below the ring, the needle above the
    # limb
    bzi = P("comp_bezel_in", "comp")
    lathe(bzi, CO, [(LY.COMP_DIAL_R + 0.0004, 0.0118), (LY.COMP_DIAL_R + 0.0002, 0.0106)], nn)
    parts.append(bzi)
    dl = P("comp_dial", "comp_dial")
    zd = 0.0106
    lathe(dl, CO, [(LY.COMP_DIAL_R + 0.0002, zd), (0.010, zd + 0.0003)], nn, cap_hi=True)
    parts.append(dl)
    parts += build_needle(lod)
    if lod == 0:
        # front sight and rear sight on the sighting ring
        th = math.radians(90.0 + LY.BEZEL_ROT)
        for k, (ang, kind) in enumerate(((th, "front"), (th + math.pi, "rear"))):
            rd = Vector((math.cos(ang), math.sin(ang)))
            sf = g.Frame(CO.p(rd.x * 0.0205, rd.y * 0.0205, 0.0121), CO.u * rd.x + CO.v * rd.y,
                         -CO.u * rd.y + CO.v * rd.x, CO.n)
            sp = P("sight_%s" % kind, "steel")
            if kind == "front":
                g.prism(sp, [(-0.0013, 0.0), (0.0013, 0.0), (0.0004, 0.0046), (-0.0004, 0.0046)], (0, 2),
                        -0.0005, 0.0005, frame=sf)
            else:
                for s in (-1, 1):
                    place_box(sp, sf, -0.0011, 0.0011, s * 0.0012 - 0.00045, s * 0.0012 + 0.00045, 0.0, 0.0040)
            parts.append(sp)
    # strap lugs: wire staples with rounded corners
    for s, nm in ((1, "lug_t"), (-1, "lug_b")):
        lg = P(nm, "steel", uv_name="lug")
        pts = [CO.p(u, s * v, LUG_C) for u, v in ((-0.0085, 0.0190), (-0.0085, 0.0252), (0.0085, 0.0252),
                                                  (0.0085, 0.0190))]
        if lod == 0:
            pts = fillet(pts, 0.0014, 2)
        g.pipe(lg, pts, LUG_R, 5 if lod == 0 else 4)
        parts.append(lg)
    parts += build_strap(lod)
    return parts


def build_strap(lod):
    """Strap: the upper half wraps the lug, lies on the sheet and steps onto the ruler (with holes); the
    lower one wraps the lower lug, goes down to the lip and is thrown over it, the buckle hangs on the
    lip face. The near LOD has smooth bends (fillet) and rounded edges.
    """
    parts = []
    hw, ht = LY.STRAP_W / 2, LY.STRAP_T / 2
    x = LY.COMP_C[0]
    cb = LY.COMP_C[1]
    c_lug = FACE + 0.0002 + LUG_C                   # lug axis in board c
    over = c_lug + LUG_R + ht + 0.0001              # strap over the lug rod
    lie = FACE + ht + 0.0002
    on_ruler = RULER_TOP + ht + 0.0002
    smooth = lod == 0
    # upper: the end is under the compass ring, over the lug rod, down onto the sheet, along the
    # sheet, onto the ruler
    up = [(cb + 0.0212, over), (cb + 0.0252, over), (cb + 0.0276, c_lug - 0.0004), (cb + 0.0318, lie),
          (LY.RULER_B0 - 0.004, lie), (LY.RULER_B0 + 0.003, on_ruler), (LY.STRAP_TOP - 0.004, on_ruler)]
    pts = [BF.p(x, b, c) for b, c in up]
    if smooth:
        pts = fillet(pts, [0, 0.0016, 0.0020, 0.0040, 0.0030, 0.0030, 0], 2)
    ends = [(LY.STRAP_TOP - 0.0015, 0.8), (LY.STRAP_TOP - 0.0003, 0.45)] if smooth else [(LY.STRAP_TOP, 0.35)]
    pts += [BF.p(x, b, on_ruler) for b, _ in ends]
    wd = [hw * 0.9] + [hw] * (len(pts) - 1 - len(ends)) + [hw * k for _, k in ends]
    st = P("strap_t", "leather")
    strap(st, pts, wd, ht, lod, BF.n)
    parts.append(st)
    # lower: in world coordinates (y, z) along the lip profile; o is the offset of the strap middle
    # from the faces
    o = ht + 0.0003
    b1 = (Y_LB + o - Y_F + lie * math.sin(A)) / math.cos(A)       # on the sheet the strap butts against the lip
    lo = [BF.p(x, cb - 0.0212, over), BF.p(x, cb - 0.0252, over), BF.p(x, cb - 0.0276, c_lug - 0.0004),
          BF.p(x, cb - 0.0318, lie), BF.p(x, b1, lie), Vector((x, Y_LB + o, LEDGE_H + o)),
          Vector((x, Y_LF - o, LEDGE_H + o)), Vector((x, Y_LF - o, 0.0110))]
    if smooth:
        lo = fillet(lo, [0, 0.0016, 0.0020, 0.0040, 0.0020, LEDGE_R + o, LEDGE_R + o, 0], 2)
    else:
        lo = [lo[0], lo[1], lo[3], lo[4], lo[5], lo[6], lo[7]]
    sb = P("strap_b", "leather")
    strap(sb, lo, [hw * 0.9] + [hw] * (len(lo) - 1), ht, lod, BF.n)
    parts.append(sb)
    # buckle: a wire frame on the lip face (rounded corners), the tongue up
    yk = Y_LF - 0.0030
    bk = P("buckle", "buckle")
    fr = [(0.0, 0.0185), (0.0100, 0.0185), (0.0100, 0.0050), (-0.0100, 0.0050), (-0.0100, 0.0185), (0.0, 0.0185)]
    bpts = [Vector((x + a, yk, z)) for a, z in fr]
    if smooth:
        bpts = fillet(bpts, [0, 0.0024, 0.0016, 0.0016, 0.0024, 0], 2)
    g.pipe(bk, bpts, 0.0009, 5 if lod == 0 else 4)
    if lod == 0:
        g.pipe(bk, [Vector((x, yk - 0.0002, 0.0185)), Vector((x, yk - 0.0011, 0.0140)), Vector((x, yk - 0.0013, 0.0110)),
                    Vector((x, yk - 0.0010, 0.0080))], 0.0006, 6)
    parts.append(bk)
    return parts


# =============================================================================
def build_lod(spec):
    parts = build_stand(spec) + build_board(spec) + build_ruler(spec) + build_clamp(spec) + build_curv(spec)
    parts += build_compass(spec)
    g.triangulate(parts)
    for p in parts:                                       # degenerate faces: it is obvious whose part it is
        bad = sum(1 for f in p.bm.faces if f.calc_area() < 6e-8)
        if bad:
            print("DEGENERATE: LOD%d %s %d" % (spec["lod"] + 1, p.name, bad))
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("bounds: %s .. %s" % (tuple(round(c, 4) for c in BOUNDS["lo"]),
                                   tuple(round(c, 4) for c in BOUNDS["hi"])))
        for d in DECOR:                                   # vanilla items: the bounds are in place
            q = kv.corners(d[5], d[1], d[2], d[3])
            print("decor %s: x %.4f..%.4f y %.4f..%.4f z %.4f..%.4f" % (
                d[5], min(c[0] for c in q), max(c[0] for c in q), min(c[1] for c in q), max(c[1] for c in q),
                min(c[2] for c in q), max(c[2] for c in q)))
    return parts


def collision():
    """One convex hull - a wedge: the bottom by the bounds, the lip at the front, the top of the board
    with the ruler and wing nuts at the rear. Mass is the item's weight in the mod (0.8 kg; module
    rules are not touched); the hit material is wood.
    """
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    x0, x1 = lo[0], hi[0]
    y_back = BF.p(0, RULER_B1, RULER_TOP).y
    z_back = BF.p(0, RULER_B1, RULER_TOP).z
    nut = BF.p(0, (LY.BAR_B[0] + LY.BAR_B[1]) / 2, BAR_C0 + LY.BAR_T + 0.0105)
    pts = [(x, y, 0.0) for x in (x0, x1) for y in (lo[1], hi[1])]
    pts += [(x, lo[1], LEDGE_H) for x in (x0, x1)]
    pts += [(x, y_back, z_back) for x in (x0, x1)]
    pts += [(x, nut.y, nut.z) for x in (-LY.BOLT_A - 0.011, LY.BOLT_A + 0.011)]
    comps = [(pts, kx.PEN + r"\wood.rvmat")]
    memory = {
        # inventory preview camera: front-left and from above (as on M71, M76)
        "invView": [(-0.24, -0.44, 0.36)],
        "ce_center": [(0.0, 0.0, 0.05)],
        "ce_radius": [(0.15, 0.0, 0.05)],
        # compass needle axis (bone ozl_needle): along the limb normal through the pin
        "ozl_needle_axis": [tuple(CO.p(0, 0, NEEDLE_C)), tuple(CO.p(0, 0, NEEDLE_C + 0.010))],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


SHOTS = [
    ("front", (-0.14, -0.56, 0.30), (0.0, 0.0, 0.05), 40),
    ("compass", (0.010, -0.215, 0.235), (0.046, -0.046, 0.040), 85),
    ("instruments", (-0.07, -0.21, 0.25), (-0.012, -0.066, 0.035), 62),
    ("clamp", (0.20, -0.10, 0.26), (0.06, 0.07, 0.085), 62),
    ("ledge", (-0.12, -0.34, 0.11), (-0.02, -0.10, 0.03), 55),
    ("left", (-0.50, -0.24, 0.24), (0.0, 0.0, 0.05), 40),
    ("map", (0.02, -0.26, 0.36), (0.0, 0.0, 0.05), 46),
    ("top", (0.0, -0.06, 0.58), (0.0, 0.0, 0.05), 40),
    ("back", (0.36, 0.46, 0.28), (0.0, 0.0, 0.05), 40),
]
M.look_shots = (6, 2)
_panel_mats = M.panel_mats


def panel_mats_ruler(on):
    """Preview: the ruler (a glass section) with its own picture ruler_ca.png (scales, stencils), not the
    kit's grey glass; the tex_* render shows it the same way after baking.
    """
    import krender
    out = _panel_mats(on)
    out["glass"] = krender.game_glass(wdecal("ruler_ca.png"))
    return out


M.panel_mats = panel_mats_ruler

M.run(build_lod, collision, SHOTS, row_step=0.32, row_shot=((0.16, -1.1, 0.35), (0.16, 0, 0.05)))
