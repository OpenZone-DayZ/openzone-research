"""M68 - "Protection" carrier (OZL_Carrier_Prot): the carrier of the "Protection" line, shared by the
factions ("a test protocol in an army map case") - a Soviet officer's map case opened into two leaves:
on the left under a scratched celluloid a protection test protocol form on top of a map, on the right
the body with a pencil holder; the flap is thrown back, the corner of a second sheet sticks out of
the mouth. A portable 2x2 item.

    blender --background --python build_m68.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (protocol, copy, map, celluloid
scratches, stitching and stamp on the leather, the corner of the second sheet).

Target: ~22 x 32 x 4 cm, a body (camoGround) with a flap and two tabs, a strap, pockets for pencils;
a transparent scratched window with a protocol form under it; the corner of a second sheet sticks out
from under the flap; no readable text.

Reference and sizes:
- a Soviet field officer's map case (a shop item, photos of it open and closed): 22 x 28 cm, 22 x 32
  with the flap. Other items: 31 x 22 cm (a shop card), 12.2 x 8.6 x 2.3" = 310 x 218 x 58 mm (a lot
  "Soviet officer's map case 1973": "two compartments - one of transparent plastic for maps, the other
  for belongings, with holders for pencils and rulers"). Hence two leaves: a cover with a window and a
  body with a pencil holder (the open reference photo shows three: a window, a flannel-lined body, a
  pencil holder). The celluloid window of Soviet map cases is inside (museum descriptions), so the case
  lies open, as in the photo, rather than closed with the window outside. Open, it is ~0.49 x 0.46 m
  with the flap and the strap.
- the body lies on its back, the sides ~3 cm (the nominal thickness of 4-5.8 cm includes the
  contents); the front wall is a pillow from the edge; the cover with the window is thrown back by 180
  degrees and lies on the ground, the leather fold is at the left edge of the body. The window frame
  is 15 mm, the celluloid is scratched, worn in patches, cracked at the fold, with a crease across;
  under it is an A5 protocol form on top of a topographic map and a carbon copy.
- the flap ~10.5 cm (closed it covers ~0.38 of the height) is thrown back up suede side out, a nickel
  lock tongue at the end, stitching and a wordless stamp on the suede; the corner of the second sheet
  of the protocol comes out of the mouth onto the flap.
- tabs (two): a strap with a hook across the window and a tab with a turn-lock from under the bottom
  of the body.
- pencil holder: two strips with loops: a red-blue pencil, a "Konstruktor" pencil, a ballpoint pen, a
  stub of a black one; a pocket on the left with the edge of a folded map.
- shoulder strap: light leather 20 mm: fastened with a ring at the right near the top, the free end
  with the buckle lies near the bottom.

The line colour of "Protection" is the grey stripe of the form (like the M53 sample tag). Marks:
digits, fields, scales, a "bullet - plate" pictogram, hit points, a stamp with a star without text, a
map without captions. State is `used but intact`: the leather is worn at the edges and corners, the
cover fold is greasy, the celluloid is scratched and yellowed. There are no lamps, screens or moving
parts, so there is no "work" view. LODs (a small item): near and middle, no far one.

Detailing (small-item budget: up to 1.5 k triangles in the near LOD, middle ~40 %):
- "dayz" look (kmodel look="dayz"): matte, dirtier, blotches, scratches; the rvmat follows the profile
  (specular 1.0), as in the preview; leather and suede get their own profile layers (leather_weather:
  short scratches instead of long straight ones, less dust - otherwise the dark leather turned grey);
  the nickel is dulled and darker (like the build_steel of the vanilla look), the paper has its own
  light dust without profile blotches (paper in a map case);
- corners of the leaf and the body are 30 degrees per segment (45 gave faceted corners in shadow, the
  sharp-edge threshold of kexport is 40), straight sides of rings have no extra points; the body has
  an edge with a seam roll;
- the cover fold is a smooth curve (Catmull-Rom through control points, simplified to 9 points);
- pencil holder loops wrap the pencils in an arc (4 points of 36 degrees), not a trapezoid; the empty
  loop is a sagged low arc;
- the strap is a smooth curve, at the ring it lies on the wire; a keeper at the buckle; the buckle is
  a frame with chamfered corners and a tongue, tilted (the rear bar on the strap, the front one on
  the ground); the ring has 9 points; the hook of the window strap lies on the frame, not over the
  window;
- the turn-lock is a rosette with a chamfer and a wing nut; the flap has two lock rivets, the lock
  tongue has chamfered end corners; the pocket is soft, bulged by the folded map; the pen has a
  writing end with a steel tip, unsharpened pencil ends show wood;
- on the leather, creases at the cover fold and at the flap root; on the suede, tufted pile, smoothed
  stripes, bald patches and a greasy border.
No vanilla DayZ items (proxies): there is no room for them on the open case without intersections (the
DayZ compass is 15.8 x 10.9 cm by extent, free space is 9 x 12), and the DayZ pen colour is set by the
config (such proxies are drawn in the model's default colour). There is no "work" state: the carrier
is an inventory item, not a machine (it has no m_OZL_State).

Blender axes: X is across (the cover at -X, the body at +X), Y is along (the flap at +Y), Z is up. The
origin is the middle between the leaves on the ground, autocenter = 0 (in Geometry). Shared
dimensions: m68_layout.py.
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
import m68_layout as ly  # noqa: E402
from mathutils import Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
SEL = "camoGround"                 # body leather: the colour is set by the config (hiddenSelections)

LOD_SPECS = [dict(lod=0), dict(lod=1)]
SIDES = "lrtb"
Z_UP = Vector((0.0, 0.0, 1.0))

# atlas regions: the window with the protocol matters most; the rings of the leaf and the body are
# split by side, otherwise a ring's atlas rectangle would span the whole leaf and be empty in the middle
REGIONS = {
    "win": ("window", 2.3),
    "body_top": ("lth_front", 0.75), "body_bot": ("lth_dark", 0.15), "mouth": ("mouth", 0.6),
    **{"bs_" + s: ("lth_dark", 0.55) for s in SIDES},
    **{"lf_" + s: ("lth_frame", 0.8) for s in SIDES},
    "leaf_bot": ("lth_dark", 0.12),
    "bend": ("lth_frame", 0.7),
    "suede": ("suede", 0.7), "flap_bot": ("lth_dark", 0.12), "edge": ("edge", 0.35),
    "tab": ("lth_dark", 0.7), "band": ("lth_front", 0.8), "pocket": ("lth_front", 0.75),
    "ringtab": ("lth_dark", 0.5), "wstrap": ("lth_frame", 0.9),
    "strap": ("strap", 0.6), "keeper": ("strap_plain", 0.6),
    "metal": ("metal", 0.6),
    "pen_red": ("pen_red", 0.6), "pen_blue": ("pen_blue", 0.6), "pen_green": ("pen_green", 0.6),
    "pen_black": ("pen_black", 0.6), "wood": ("wood", 0.6), "lead": ("lead", 0.4),
    "lead_red": ("lead_red", 0.4), "lead_blue": ("lead_blue", 0.4),
    "pen_body": ("pen_body", 0.6), "pen_cap": ("pen_cap", 0.6),
    "paper2": ("paper2", 1.3), "paper_b": ("paper_back", 0.1), "paper_edge": ("paper_edge", 0.2),
    "fmap": ("fmap", 0.9),
}


# --- materials ------------------------------------------------------------------------------------
def mul(t, col, rgba):
    m = t.node("ShaderNodeMix")
    m.data_type = "RGBA"
    m.blend_type = "MULTIPLY"
    m.inputs["Factor"].default_value = 1.0
    t.link(col, m.inputs[6])
    m.inputs[7].default_value = rgba
    return m.outputs[2]


def sheet_uv(t, x, y, c, deg):
    """Coordinates of a sheet rotated by deg about c: (u, v) from the sheet centre."""
    a = math.radians(deg)
    dx, dy = t.math("SUBTRACT", x, c[0]), t.math("SUBTRACT", y, c[1])
    u = t.math("ADD", t.math("MULTIPLY", dx, math.cos(a)), t.math("MULTIPLY", dy, math.sin(a)))
    v = t.math("SUBTRACT", t.math("MULTIPLY", dy, math.cos(a)), t.math("MULTIPLY", dx, math.sin(a)))
    return u, v


def scale(c, k, add=0.0):
    return tuple(min(1.0, x * k + add) for x in c[:3]) + (1.0,)


def crease_mask(t, vec, sep, creases):
    """Creases: [(axis, centre, half-width)] - a band where the leather is bent, with fine wrinkles along
    the fold (noise stretched along the fold line). None means no creases."""
    out = None
    for axis, c, half in creases:
        coord = sep.outputs["XYZ".index(axis.upper())]
        zone = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", coord, c)), 0.0, half, 1.0, 0.0)
        st = (1.0, 0.06, 1.0) if axis == "x" else (0.06, 1.0, 1.0)
        cr = t.step(t.noise(t.stretch(vec, *st), 170.0, 3.0, 0.55), 0.57, 0.64)
        cz = t.math("MULTIPLY", cr, zone)
        out = cz if out is None else t.math("MAXIMUM", out, cz)
    return out


def leather_weather(t, col, vec, sep, nsep, dust=0.05, cav=0.35):
    """kmats.weather together with the "dayz" profile layers (kmats.dayz_layers), adapted for leather: the
    profile's long straight scratches (~15 cm, meant for paint) read as ruler lines on the walls of
    leather - here the scratches are short (1-2 cm) and lighter, the colour of the worn top layer rather
    than grey; less dust (leather is rubbed by hands and clothes; with the profile's dust the dark leather
    turned grey); streaks on the sides are half as strong. The colour muting, tonal blotches and grease
    spots are as in the profile. Without the "dayz" profile it is plain kmats.weather. Returns (colour,
    dirt strength)."""
    k = kmats.LOOK
    if k["name"] != "dayz":
        return kmats.weather(t, col, vec, sep, nsep, 0.0, dust=dust, grime=0.0, cav=cav)
    dust, cav = dust * k["dust_k"], cav * k["cav_k"]
    up = t.maprange(nsep.outputs["Z"], 0.4, 0.9, 0.0, 1.0)
    dn = t.maprange(t.noise(vec, 4.0, 6.0, 0.6), 0.35, 0.7, 0.4, 1.0)
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", up, dn), dust), col, kmats.DUST)
    c = t.maprange(t.cavity(0.04), 0.15, 0.6, 0.0, 1.0)
    g = t.math("MULTIPLY", t.math("MULTIPLY", c, cav), t.maprange(t.noise(vec, 7.0, 8.0, 0.6), 0.3, 0.7, 0.5, 1.0))
    col = t.mixc(g, col, kmats.GRIME)
    d, v = k["patina"]
    gray = t.node("ShaderNodeRGBToBW")
    t.link(col, gray.inputs[0])
    col = t.mixc(d, col, gray.outputs[0])
    col = t.mixc(1.0 - v, col, (0, 0, 0, 1))
    n1 = t.maprange(t.noise(vec, 1.7, 5.0, 0.6), 0.3, 0.7, 0.0, 1.0)
    col = t.mixc(n1, t.mixc(k["mottle"], col, (0, 0, 0, 1)), t.mixc(k["mottle"] * 0.4, col, (1, 1, 1, 1)))
    vert = t.maprange(t.math("ABSOLUTE", nsep.outputs["Z"]), 0.35, 0.6, 1.0, 0.0)
    st = t.step(t.noise(t.stretch(vec, 1.0, 1.0, 0.07), 16.0, 6.0, 0.6), 0.60, 0.70)
    st = t.math("MULTIPLY", t.math("MULTIPLY", st, vert), k["streaks"] * 0.2)
    col = t.mixc(st, col, kmats.GRIME)
    sm = t.math("MULTIPLY", t.step(t.noise(vec, 3.2, 4.0, 0.5), 0.64, 0.74), k["smudge"])
    col = t.mixc(sm, col, kmats.lin((40, 36, 30)))
    s1 = t.step(t.noise(t.stretch(vec, 0.3, 1.0, 1.0), 260.0, 2.0, 0.5), 0.72, 0.735)
    s2 = t.step(t.noise(t.stretch(vec, 1.0, 0.3, 1.0), 260.0, 2.0, 0.5), 0.72, 0.735)
    sc = t.math("MULTIPLY", t.math("MAXIMUM", s1, s2),
                t.maprange(t.noise(vec, 6.0, 4.0, 0.5), 0.45, 0.75, 0.0, k["scratches"] * 0.7))
    col = t.mixc(sc, col, t.mixc(0.35, col, (0.45, 0.36, 0.28, 1.0)))
    return col, t.math("MAXIMUM", g, t.math("MAXIMUM", st, sm))


def build_leather(mat, origin, color, seed=1.0, gloss=0.36, spec=0.22, wear=1.0, mouth=False, grain=1300.0,
                  print_=True, creases=()):
    """Leather: blotchy tone, fine moire and wrinkles, wear on the edges and in patches (lighter, more rusty
    and duller); thin scratches; stitching and the stamp (leather_print.png by X, Y, on up-facing parts;
    print_=False omits them: the strap keeper); at the body mouth (mouth) a dark gap between the walls;
    creases are the creases at the folds. Dust, dirt and the "dayz" profile layers come from
    leather_weather."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    x, y = sep.outputs["X"], sep.outputs["Y"]
    mott = t.maprange(t.noise(vec, 9.0, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0)
    col = t.mixc(mott, scale(color, 0.80), scale(color, 1.08))
    pits = t.noise(vec, grain, 3.0, 0.5)
    wrink = t.step(t.noise(t.stretch(vec, 1.0, 3.5, 1.0), 120.0, 3.0, 0.6), 0.62, 0.70)
    col = t.mixc(t.math("MULTIPLY", t.maprange(pits, 0.35, 0.65, 0.0, 1.0), 0.18), col, scale(color, 0.62))
    col = t.mixc(t.math("MULTIPLY", wrink, 0.25), col, scale(color, 0.7))
    crz = crease_mask(t, vec, sep, creases)
    if crz is not None:
        col = t.mixc(t.math("MULTIPLY", crz, 0.5), col, scale(color, 0.5))
    edge = t.maprange(t.edge_wear(0.0025), 0.03, 0.22, 0.0, 1.0)
    sc = t.noise(vec, 42.0, 6.0, 0.7)
    worn = t.math("MULTIPLY", t.step(t.math("ADD", t.math("MULTIPLY", edge, 0.7), t.math("MULTIPLY", sc, 0.55)),
                                     0.62, 0.80), wear)
    col = t.mixc(t.math("MULTIPLY", worn, 0.85), col, scale(color, 1.75, 0.035))
    scr = t.step(t.noise(t.stretch(vec, 28.0, 1.0, 1.0), 45.0, 2.0, 0.5), 0.71, 0.735)
    col = t.mixc(t.math("MULTIPLY", scr, 0.35 * wear), col, scale(color, 1.6, 0.03))
    thread = None
    if print_:
        gate = t.facing(nsep, "Z", 1, 0.5)
        pc, pa = t.image(os.path.join(WORK, "leather_print.png"), x, y, ly.PRINT_C, ly.PRINT_S)
        pa = t.math("MULTIPLY", pa, gate)
        col = t.mixc(pa, col, pc)
        thread = t.step(pa, 0.9, 0.95)
    if mouth:
        z = sep.outputs["Z"]
        band = t.math("MULTIPLY", t.maprange(z, 0.011, 0.013, 0.0, 1.0), t.maprange(z, 0.020, 0.0225, 1.0, 0.0))
        band = t.math("MULTIPLY", band, t.facing(nsep, "Y", 1, 0.5))
        col = t.mixc(band, col, kmats.lin((14, 10, 8)))
    col, dirt = leather_weather(t, col, vec, sep, nsep, dust=0.05, cav=0.35)
    gl = t.math("SUBTRACT", gloss, t.math("ADD", t.math("MULTIPLY", worn, gloss * 0.5), t.math("MULTIPLY", dirt, 0.1)))
    sp = t.math("SUBTRACT", spec, t.math("MULTIPLY", worn, spec * 0.4))
    h = t.math("MULTIPLY", pits, 0.14)
    if thread is not None:
        h = t.math("ADD", h, t.math("MULTIPLY", thread, 0.5))
    h = t.math("SUBTRACT", h, t.math("ADD", t.math("MULTIPLY", wrink, 0.12), t.math("MULTIPLY", worn, 0.1)))
    if crz is not None:
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", crz, 0.25))
    return kmats.out(t, col, gl, sp, h)


def build_suede(mat, origin, color, seed=6.0):
    """Suede of the flap underside: pile in patches of different density (large and small), smoothed pile
    stripes, bald patches (the pile worn down to smooth leather - darker and more rusty), a greasy border
    along the edges and dark finger stains at the free edge, a crease at the flap root (flat suede read as
    cardboard); stitching, the stamp and the lock rivets come from leather_print.png."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    x, y = sep.outputs["X"], sep.outputs["Y"]
    nap = t.noise(vec, 260.0, 5.0, 0.65)
    col = t.mixc(t.maprange(nap, 0.3, 0.7, 0.0, 1.0), scale(color, 0.80), scale(color, 1.10))
    # pile in tufts (1-3 cm) is what tells suede from cardboard at a distance
    tuft = t.maprange(t.noise(vec, 38.0, 5.0, 0.62), 0.32, 0.68, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", tuft, 0.50), col, scale(color, 0.70))
    brush = t.maprange(t.noise(t.stretch(vec, 0.15, 1.0, 1.0), 40.0, 3.0, 0.5), 0.45, 0.7, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", brush, 0.22), col, scale(color, 1.14))
    cloud = t.maprange(t.noise(vec, 7.0, 4.0, 0.5), 0.35, 0.7, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cloud, 0.55), col, scale(color, 0.70))
    bald = t.step(t.noise(vec, 10.0, 5.0, 0.6), 0.60, 0.68)
    col = t.mixc(t.math("MULTIPLY", bald, 0.55), col, (color[0] * 0.62, color[1] * 0.50, color[2] * 0.40, 1.0))
    # greasy border: along the flap edges, where it is picked up and where it rubs the body
    rim = t.math("MINIMUM", t.math("MINIMUM", t.math("SUBTRACT", x, ly.FL_X0), t.math("SUBTRACT", ly.FL_X1, x)),
                 t.math("SUBTRACT", ly.FL_Y1, y))
    rim = t.math("MULTIPLY", t.maprange(rim, 0.0, 0.014, 1.0, 0.0),
                 t.maprange(t.noise(vec, 30.0, 5.0, 0.6), 0.3, 0.7, 0.4, 1.0))
    col = t.mixc(t.math("MULTIPLY", rim, 0.45), col, scale(color, 0.58))
    grip = t.math("MULTIPLY", t.maprange(y, ly.FL_Y1 - 0.035, ly.FL_Y1, 0.0, 1.0),
                  t.maprange(t.noise(vec, 20.0, 6.0, 0.6), 0.4, 0.7, 0.0, 1.0))
    col = t.mixc(t.math("MULTIPLY", grip, 0.55), col, scale(color, 0.52))
    crz = crease_mask(t, vec, sep, (("y", ly.BY1 + 0.006, 0.018),))
    col = t.mixc(t.math("MULTIPLY", crz, 0.45), col, scale(color, 0.58))
    pc, pa = t.image(os.path.join(WORK, "leather_print.png"), x, y, ly.PRINT_C, ly.PRINT_S)
    col = t.mixc(t.math("MULTIPLY", pa, t.facing(nsep, "Z", 1, 0.5)), col, pc)
    col, dirt = leather_weather(t, col, vec, sep, nsep, dust=0.08, cav=0.3)
    rivet = t.step(pa, 0.95, 0.99)
    gl = t.math("ADD", 0.05, t.math("ADD", t.math("MULTIPLY", grip, 0.10),
                                    t.math("ADD", t.math("MULTIPLY", rivet, 0.5), t.math("MULTIPLY", bald, 0.10))))
    sp = t.math("ADD", 0.03, t.math("MULTIPLY", rivet, 0.6))
    h = t.math("ADD", t.math("MULTIPLY", nap, 0.2), t.math("MULTIPLY", rivet, 0.5))
    h = t.math("SUBTRACT", h, t.math("ADD", t.math("MULTIPLY", crz, 0.25), t.math("MULTIPLY", bald, 0.1)))
    return kmats.out(t, col, gl, sp, h)


def build_window(mat, origin, seed=9.0):
    """Window: under the celluloid a map, a carbon copy and a protocol form (each its own image in its own
    coordinates, rotated); the celluloid is yellowish, scratched and worn (cell_scr.png), with dust in
    the corners by the frame; glossy, the relief is a gentle wave of the film."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    x, y = sep.outputs["X"], sep.outputs["Y"]
    col, _ = t.image(os.path.join(WORK, "map.png"), x, y, ly.MAP_C, ly.MAP_S)
    u, v = sheet_uv(t, x, y, ly.COPY_C, ly.COPY_ROT)
    cc, ca = t.image(os.path.join(WORK, "copy.png"), u, v, (0.0, 0.0), (ly.COPY_W, ly.COPY_H))
    col = t.mixc(ca, col, cc)
    u, v = sheet_uv(t, x, y, ly.PROT_C, ly.PROT_ROT)
    pc, pa = t.image(os.path.join(WORK, "protocol.png"), u, v, (0.0, 0.0), (ly.PROT_W, ly.PROT_H))
    # shadow of the protocol edge on the copy and the map (the paper is slightly raised)
    us, vs = sheet_uv(t, t.math("ADD", x, -0.0007), t.math("ADD", y, 0.0009), ly.PROT_C, ly.PROT_ROT)
    _, sa = t.image(os.path.join(WORK, "protocol.png"), us, vs, (0.0, 0.0), (ly.PROT_W, ly.PROT_H))
    col = t.mixc(t.math("MULTIPLY", sa, 0.22), col, (0.02, 0.02, 0.02, 1.0))
    col = t.mixc(pa, col, pc)
    col = mul(t, col, (0.94, 0.90, 0.76, 1.0))                       # old celluloid yellows
    sc_img, _ = t.image(os.path.join(WORK, "cell_scr.png"), x, y, ly.MAP_C, ly.MAP_S)
    scr = t.bw(sc_img)
    col = t.mixc(t.math("MULTIPLY", scr, 0.75), col, (0.80, 0.80, 0.76, 1.0))
    dx = t.math("MINIMUM", t.math("SUBTRACT", x, ly.WIN_X0), t.math("SUBTRACT", ly.WIN_X1, x))
    dy = t.math("MINIMUM", t.math("SUBTRACT", y, ly.WIN_Y0), t.math("SUBTRACT", ly.WIN_Y1, y))
    near = t.maprange(t.math("MINIMUM", dx, dy), 0.0, 0.006, 1.0, 0.0)
    dust = t.math("MULTIPLY", near, t.maprange(t.noise(vec, 60.0, 5.0, 0.6), 0.35, 0.7, 0.2, 1.0))
    col = t.mixc(t.math("MULTIPLY", dust, 0.5), col, kmats.lin((150, 140, 120)))
    gl = t.math("SUBTRACT", 0.90, t.math("ADD", t.math("MULTIPLY", scr, 0.6), t.math("MULTIPLY", dust, 0.5)))
    sp = t.math("SUBTRACT", 0.80, t.math("MULTIPLY", scr, 0.5))
    h = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 9.0, 2.0, 0.5), 0.25), t.math("MULTIPLY", scr, 0.15))
    return kmats.out(t, col, gl, sp, h)


def build_paper(mat, origin, img, center, size, paper, seed=4.0, gloss=0.08):
    """Paper with a picture by X, Y (outside the picture, the paper colour). Its own weak dust and corner
    dirt: the paper lies in a map case; the blotches and scratches of the "dayz" profile (kmats.weather)
    do not suit paper."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    c, a = t.image(os.path.join(WORK, img), sep.outputs["X"], sep.outputs["Y"], center, size)
    col = t.mixc(a, paper, c)
    col = t.mixc(t.math("MULTIPLY", t.noise(vec, 200.0, 3.0, 0.6), 0.1), col, scale(paper, 0.88))
    up = t.maprange(nsep.outputs["Z"], 0.4, 0.9, 0.0, 1.0)
    dust = t.math("MULTIPLY", up, t.maprange(t.noise(vec, 30.0, 4.0, 0.6), 0.4, 0.75, 0.0, 0.12))
    col = t.mixc(dust, col, kmats.DUST)
    cav = t.maprange(t.cavity(0.02), 0.15, 0.6, 0.0, 0.4)
    col = t.mixc(cav, col, kmats.GRIME)
    col = t.mixc(0.06, col, (0.0, 0.0, 0.0, 1.0))
    return kmats.out(t, col, gloss, 0.05, t.math("MULTIPLY", t.noise(vec, 300.0, 2.0, 0.5), 0.05))


def build_metal(mat, origin, seed=8.0):
    """Nickel-plated steel: light metal, darkening in patches, rust specks. In the "dayz" profile it is
    darker (tone x LOOK["steel"], as in kmats.build_steel), with bloom and dirt in corners (weather),
    lower gloss - old nickel, not chrome."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    dayz = kmats.LOOK["name"] == "dayz"
    k = kmats.LOOK.get("steel", 1.0) if dayz else 1.0
    tarn = t.maprange(t.noise(vec, 300.0, 4.0, 0.6), 0.35, 0.75, 0.0, 1.0)
    hi = tuple(c * k for c in kmats.lin((182, 182, 184))[:3]) + (1.0,)
    lo = tuple(c * k for c in kmats.lin((120, 116, 104))[:3]) + (1.0,)
    col = t.mixc(tarn, hi, lo)
    speck = t.step(t.noise(vec, 1200.0, 6.0, 0.7), 0.74, 0.78)
    col = t.mixc(t.math("MULTIPLY", speck, 0.8), col, kmats.RUST[1])
    dirt = 0.0
    if dayz:
        blot = t.step(t.noise(vec, 160.0, 5.0, 0.6), 0.62, 0.72)          # bloom patches
        col = t.mixc(t.math("MULTIPLY", blot, 0.45), col, kmats.lin((70, 64, 52)))
        col, dirt = kmats.weather(t, col, vec, sep, nsep, 0.0, dust=0.05, grime=0.0, cav=0.5)
    gl = t.math("SUBTRACT", 0.78 if not dayz else 0.62,
                t.math("ADD", t.math("MULTIPLY", tarn, 0.25), t.math("MULTIPLY", speck, 0.6)))
    sp = t.math("SUBTRACT", 0.88, t.math("ADD", t.math("MULTIPLY", tarn, 0.3), t.math("MULTIPLY", speck, 0.7)))
    if dayz:
        gl = t.math("SUBTRACT", gl, t.math("MULTIPLY", dirt, 0.3))
        sp = t.math("SUBTRACT", sp, t.math("MULTIPLY", dirt, 0.3))
    return kmats.out(t, col, gl, sp, t.math("MULTIPLY", speck, 0.2))


def paint(rgb, gloss=0.55, seed=3.0):
    """Pencil lacquer and pen plastic: more tonal blotches and rubbed facets (the pencils looked new
    otherwise)."""
    return ("plastic", dict(color=kmats.lin(rgb), seed=seed, gloss=gloss, spec=0.4, dust=0.08, grime=0.0,
                            mottle=0.09, scuff=(0.68, 0.76)))


STRAP_RGB = (156, 100, 56)
KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "lth_dark": (build_leather, dict(color=kmats.lin((50, 33, 25)), seed=1.1)),
    "lth_front": (build_leather, dict(color=kmats.lin((60, 38, 28)), seed=1.4)),
    # window frame and cover fold: creases along the fold (between the leaf and the body, x ~ 0)
    "lth_frame": (build_leather, dict(color=kmats.lin((100, 54, 34)), seed=1.7, gloss=0.40,
                                      creases=(("x", (ly.LX1 + ly.BX0) / 2, 0.026),))),
    "mouth": (build_leather, dict(color=kmats.lin((50, 33, 25)), seed=1.1, mouth=True)),
    "strap": (build_leather, dict(color=kmats.lin(STRAP_RGB), seed=2.2, gloss=0.30, wear=0.8)),
    "strap_plain": (build_leather, dict(color=kmats.lin(STRAP_RGB), seed=2.3, gloss=0.30, wear=0.8, print_=False)),
    "suede": (build_suede, dict(color=kmats.lin((178, 144, 108)), seed=6.1)),
    "edge": ("plastic", dict(color=kmats.lin((36, 24, 18)), seed=2.6, gloss=0.25, spec=0.12, dust=0.05, grime=0.0,
                             mottle=0.12, scuff=(0.70, 0.80))),
    "window": (build_window, dict(seed=9.1)),
    "metal": (build_metal, dict(seed=8.3)),
    "pen_red": paint((176, 34, 30), seed=3.1), "pen_blue": paint((34, 58, 146), seed=3.2),
    "pen_green": paint((34, 86, 56), seed=3.3), "pen_black": paint((26, 26, 28), seed=3.4),
    "wood": ("plastic", dict(color=kmats.lin((214, 172, 120)), seed=3.5, gloss=0.12, spec=0.05, dust=0.0,
                             grime=0.0, mottle=0.10, scuff=(0.95, 1.0))),
    "lead": ("plastic", dict(color=kmats.lin((52, 52, 56)), seed=3.6, gloss=0.6, spec=0.5, dust=0.0, grime=0.0)),
    "lead_red": paint((168, 36, 30), gloss=0.3, seed=3.7), "lead_blue": paint((40, 58, 140), gloss=0.3, seed=3.8),
    "pen_body": paint((146, 178, 206), gloss=0.75, seed=3.9), "pen_cap": paint((30, 42, 108), gloss=0.6, seed=4.1),
    "paper2": (build_paper, dict(img="sheet2.png", center=ly.S2_C, size=ly.S2_S, paper=kmats.lin((236, 232, 222)),
                                 seed=4.2)),
    "paper_back": ("plastic", dict(color=kmats.lin((226, 222, 210)), seed=4.3, gloss=0.05, spec=0.03, dust=0.05,
                                   grime=0.0)),
    "paper_edge": ("plastic", dict(color=kmats.lin((214, 208, 192)), seed=4.4, gloss=0.05, spec=0.03, dust=0.05,
                                   grime=0.0)),
    "fmap": (build_paper, dict(img="map.png", center=(ly.BX0 + 0.040, -0.040), size=ly.MAP_S,
                               paper=kmats.lin((236, 232, 212)), seed=4.5)),
})

OBJ, NAME = "m68_carrier_prot", "ozr_carrier_prot"
# "dayz" look; the rvmat comes from the profile (specular 1.0 / 80): the preview computes the highlight the
# same way and the game matches the preview
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL,), hidden=(SEL,))
BOUNDS = {}


def P(name, region, **kw):
    return M.part(name, region, **kw)


def U(p, region):
    return p.use(region, *REGIONS[region])


def face(p, verts, region, want):
    f = p.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    f[p.reg] = p.region_index(region, *REGIONS[region])
    return f


def side_of(cx, cy, x, y, hw, hh):
    dx, dy = (x - cx) / hw, (y - cy) / hh
    if abs(dx) > abs(dy):
        return "r" if dx > 0 else "l"
    return "t" if dy > 0 else "b"


# --- curves ---------------------------------------------------------------------------------------
def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, as in M16): k points per span."""
    v = [Vector(p) for p in pts]
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


def simplify(pts, tol):
    """Douglas-Peucker: keep the curve points where it bends (the deviation from the chord exceeds tol, m),
    so straight runs get no extra triangles."""
    if len(pts) < 3:
        return list(pts)
    a, b = Vector(pts[0]), Vector(pts[-1])
    ab = b - a
    best, bi = -1.0, 0
    for i in range(1, len(pts) - 1):
        q = Vector(pts[i])
        t = max(0.0, min(1.0, (q - a).dot(ab) / max(ab.length_squared, 1e-12)))
        d = (a + ab * t - q).length
        if d > best:
            best, bi = d, i
    if best <= tol:
        return [pts[0], pts[-1]]
    return simplify(pts[:bi + 1], tol)[:-1] + simplify(pts[bi:], tol)


def loop_pipe(p, pts, r, sides, phase=None):
    """Closed round rod (a ring, a buckle frame, a hook) without end caps (in g.pipe they lie inside the
    loop and are wasted). The section frame uses the horizontal across the run (for a loop lying on the
    ground the section stands upright); phase rotates the section (by default a 4-sided one has a flat
    top and bottom)."""
    bm = p.bm
    q = [Vector(c) for c in pts]
    if (q[0] - q[-1]).length < 1e-9:
        q = q[:-1]
    n = len(q)
    ph = (math.pi / sides) if phase is None else phase
    rings = []
    for i in range(n):
        t = (q[(i + 1) % n] - q[i]).normalized() + (q[i] - q[i - 1]).normalized()
        t.normalize()
        a = t.cross(Z_UP)
        if a.length < 0.15:
            a = Vector((1.0, 0.0, 0.0))
        a.normalize()
        b = a.cross(t).normalized()
        rings.append([bm.verts.new(q[i] + (a * math.cos(ph + 2 * math.pi * k / sides) +
                                           b * math.sin(ph + 2 * math.pi * k / sides)) * r) for k in range(sides)])
    new = []
    for i in range(n):
        r0, r1 = rings[i], rings[(i + 1) % n]
        for k in range(sides):
            j = (k + 1) % sides
            new.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return p.tag(new)


def frame_pts(c, d, length, width, ch, z_fn):
    """Buckle or hook frame: a length (along d) x width rectangle with corners chamfered by ch, 8 points
    (ch = 0 gives 4 corners); z_fn(u) is the height along the frame (u runs along d from the centre)."""
    d = Vector((d[0], d[1], 0.0)).normalized()
    w = Vector((-d.y, d.x, 0.0))
    hl, hw = length / 2, width / 2
    uv = [(-hl, -hw + ch), (-hl + ch, -hw), (hl - ch, -hw), (hl, -hw + ch), (hl, hw - ch), (hl - ch, hw),
          (-hl + ch, hw), (-hl, hw - ch)] if ch > 0 else [(-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw)]
    return [tuple(Vector((c[0], c[1], 0.0)) + d * u + w * v + Vector((0.0, 0.0, z_fn(u)))) for u, v in uv]


# --- flat polygons (from M65) ---------------------------------------------------------------------
def clip_poly(poly, axis, c, keep_less):
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
                res.append(p)
    return res


def slab(p, polys, z_mid, th, reg_top, reg_bot, reg_edge, bottom=True, sink=0.0):
    """Sheet of thickness th from polygons (counter-clockwise): the top and bottom share vertices, the edges
    run along edges that have a single face. z_mid(x, y) is the centre line. bottom=False omits the bottom
    face (the sheet lies on the leather, its underside is not visible), the edge goes lower by sink so
    there is no gap on the bends of the support."""
    bm = p.bm
    top, bot = {}, {}

    def key(q):
        return (round(q[0], 7), round(q[1], 7))

    def vert(store, q, dz):
        k = key(q)
        if k not in store:
            store[k] = bm.verts.new((q[0], q[1], z_mid(*q) + dz))
        return store[k]
    edges = {}
    for poly in polys:
        vt = [vert(top, q, th / 2) for q in poly]
        face(p, vt, reg_top, (0, 0, 1))
        if bottom:
            vb = [vert(bot, q, -th / 2) for q in poly]
            face(p, vb[::-1], reg_bot, (0, 0, -1))
        for i in range(len(poly)):
            a, b = key(poly[i]), key(poly[(i + 1) % len(poly)])
            edges.setdefault((min(a, b), max(a, b)), []).append((poly[i], poly[(i + 1) % len(poly)]))
    dz_b = -th / 2 - (0.0 if bottom else sink)
    for uses in edges.values():
        if len(uses) != 1:
            continue
        a, b = uses[0]
        out = (b[1] - a[1], -(b[0] - a[0]), 0.0)
        face(p, [top[key(a)], top[key(b)], vert(bot, b, dz_b), vert(bot, a, dz_b)], reg_edge, out)


# --- body and leaf: "pillows" by profile rings ----------------------------------------------------
def rings_part(p, cx, cy, profile, lod, band_region, fill_top, fill_bot, want_fn):
    """Rings of a rounded W x HL rectangle by the profile [(inset, z)], stitched with quads;
    band_region(i, side, face centre) -> the region of band i; fill_top is the region of the top fill
    (None omits it: another part makes the fill), fill_bot of the bottom one; want_fn(i, face centre) says
    where the face of band i should look. Returns the inner ring."""
    rings = []
    for d, z in profile:
        pts = ly.ring(cx, cy, ly.W, ly.HL, d, lod)
        rings.append([p.bm.verts.new((x, y, z)) for x, y in pts])
    n = len(rings[0])
    hw, hh = ly.W / 2, ly.HL / 2
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for k in range(n):
            q = [a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]]
            c = sum((v.co for v in q), Vector()) / 4
            face(p, q, band_region(i, side_of(cx, cy, c.x, c.y, hw, hh), c), want_fn(i, c))
    if fill_top:
        face(p, rings[-1], fill_top, (0, 0, 1))
    if fill_bot:
        face(p, rings[0][::-1], fill_bot, (0, 0, -1))
    return [v.co.copy() for v in rings[-1]]


def build_body(spec):
    lod = spec["lod"]
    prof = ly.BODY_RINGS if lod == 0 else ly.BODY_RINGS_L1
    n_side = ly.BODY_KANT if lod == 0 else 2               # side bands (up to and including the edge)
    straight = ly.W / 2 - ly.R_C

    def region(i, side, c):
        if i >= n_side:
            return "body_top"
        if side == "t" and abs(c.x - ly.BXC) < straight:
            return "mouth"
        return "bs_" + side
    p = P("body", "body_top", group=SEL)
    rings_part(p, ly.BXC, 0.0, prof, lod, region, "body_top", "body_bot",
               lambda i, c: c - Vector((ly.BXC, 0.0, 0.016)))
    return [p]


def build_leaf(spec):
    lod = spec["lod"]
    p = P("leaf", "lf_l", group=SEL)

    def region(i, side, c):
        return "lf_" + side
    # the lower chamfer faces outwards and down, the other bands (edge, frame, step to the window) face up
    inner = rings_part(p, ly.LXC, 0.0, ly.LEAF_RINGS if lod == 0 else ly.LEAF_RINGS_L1, lod, region, None, "leaf_bot",
                       lambda i, c: (c - Vector((ly.LXC, 0.0, 0.004))) if i == 0 else Vector((0, 0, 1)))
    w = P("window", "win")
    face(w, [w.bm.verts.new(q) for q in inner], "win", (0, 0, 1))
    return [p, w]


def bend_path(lod):
    """Cover fold: a smooth curve through the control points ly.BEND, simplified to 9 points (a turn of no
    more than 26 degrees at a point, below the sharp-edge threshold of 40)."""
    if lod == 0:
        return simplify(spline(ly.BEND, 12), 0.0003)
    return ly.BEND_L1


def build_bend(spec):
    path = bend_path(spec["lod"])
    p = P("bend", "bend", group=SEL)
    g.sweep(p, [(q[0], 0.0, q[1]) for q in path], (0, 1, 0), ly.BEND_T / 2, ly.BEND_Y)
    return [p]


# --- flap, lock, the sheet from under the flap ----------------------------------------------------
def build_flap(spec):
    lod = spec["lod"]
    p = P("flap", "suede", group=SEL)
    outline = ly.flap_outline(0.0, 6 if lod == 0 else 3)
    # no cut at the root (under the body): it adds no shape; two cuts give the curl of the free edge
    ycuts = ly.FL_YCUT[1:] if lod == 0 else ly.FL_YCUT[1:2]
    slab(p, cells(outline, (), ycuts), lambda x, y: ly.flap_z(y), ly.FL_T, "suede", "flap_bot", "edge")
    parts = [p]
    # lock tongue: under the flap, sticking out past the free edge; in the near LOD the end corners are
    # chamfered
    lk = ly.LOCK
    q = P("lock", "metal")
    x0 = ly.LOCK_X
    if lod == 0:
        ch = 0.0026
        poly = [(x0 - lk["w0"], lk["y0"]), (x0 + lk["w0"], lk["y0"]), (x0 + lk["w1"], lk["y1"] - ch),
                (x0 + lk["w1"] - ch, lk["y1"]), (x0 - lk["w1"] + ch, lk["y1"]), (x0 - lk["w1"], lk["y1"] - ch)]
    else:
        poly = [(x0 - lk["w0"], lk["y0"]), (x0 + lk["w0"], lk["y0"]), (x0 + lk["w1"], lk["y1"]),
                (x0 - lk["w1"], lk["y1"])]

    def zl(x, y):
        under = ly.flap_z(min(y, ly.FL_Y1)) - ly.FL_T / 2 - lk["t"] / 2 - 0.0001
        return max(lk["t"] / 2, under)
    # the cut at the flap edge is omitted: a straight tongue stays below the underside of the curl even
    # without it (by 0.3 mm at the worst place, checked against flap_z), and this saves 8 triangles
    slab(q, [poly], zl, lk["t"], "metal", "metal", "metal")
    parts.append(q)
    if lod == 0:
        # lock rivets: low domes over the printed circles (leather_print.png)
        rv = P("rivets", "metal")
        for cx, cy in ly.RIVETS:
            z0 = ly.flap_z(cy) + ly.FL_T / 2 - 0.0001
            ring = [rv.bm.verts.new((cx + 0.0024 * math.cos(math.pi * k / 3), cy + 0.0024 * math.sin(math.pi * k / 3), z0))
                    for k in range(6)]
            apex = rv.bm.verts.new((cx, cy, z0 + 0.0008))
            for k in range(6):
                face(rv, [ring[k], ring[(k + 1) % 6], apex], "metal", (0, 0, 1))
        parts.append(rv)
    return parts


def build_sheet2(spec):
    p = P("sheet2", "paper2")
    ycuts = ly.S2_YCUT if spec["lod"] == 0 else ly.S2_YCUT[1:2]
    slab(p, cells(ly.s2_outline(), (), ycuts), lambda x, y: ly.s2_z(y), ly.S2_T, "paper2", "paper_b", "paper_edge")
    return [p]


# --- tab with a turn-lock -------------------------------------------------------------------------
def build_tab(spec):
    lod = spec["lod"]
    hw = ly.TAB_W / 2
    n = 6 if lod == 0 else 3
    outline = [(ly.TAB_X - hw, ly.TAB_Y0)]
    for k in range(n + 1):
        a = math.radians(180.0 + 180.0 * k / n)
        outline.append((ly.TAB_X + hw * math.cos(a), ly.TAB_Y1 + hw + hw * math.sin(a)))
    outline.append((ly.TAB_X + hw, ly.TAB_Y0))
    if area(outline) < 0:
        outline = outline[::-1]
    p = P("tab", "tab", group=SEL)
    slab(p, [outline], lambda x, y: ly.TAB_T / 2, ly.TAB_T, "tab", "flap_bot", "edge")
    parts = [p]
    tr = ly.TURN
    m = P("turn", "metal")
    z0 = ly.TAB_T
    if lod == 0:
        # a rosette with a chamfer (an 8-point oval, the bottom sunk into the leather) and a wing nut
        # across, instead of two plates
        bm = m.bm
        ns = 8

        def oval(rx, ry, z, rot=0.0):
            ca, sa = math.cos(rot), math.sin(rot)
            out = []
            for k in range(ns):
                a = 2 * math.pi * (k + 0.5) / ns
                u, v = rx * math.cos(a), ry * math.sin(a)
                out.append(bm.verts.new((tr["x"] + u * ca - v * sa, tr["y"] + u * sa + v * ca, z)))
            return out

        def band(r0, r1, zc):
            for k in range(ns):
                q = [r0[k], r0[(k + 1) % ns], r1[(k + 1) % ns], r1[k]]
                c = sum((v.co for v in q), Vector()) / 4
                face(m, q, "metal", c - Vector((tr["x"], tr["y"], zc)))
        b0 = oval(tr["rx"], tr["ry"], z0 - 0.0002)
        b1 = oval(tr["rx"] - 0.0016, tr["ry"] - 0.0014, z0 + tr["t"])
        band(b0, b1, z0 - 0.002)
        face(m, b1, "metal", (0, 0, 1))
        rot = math.radians(30.0)
        k0 = oval(0.0050, 0.0021, z0 + tr["t"] - 0.0002, rot)
        k1 = oval(0.0045, 0.0016, z0 + tr["t"] + tr["knob_h"], rot)
        band(k0, k1, z0 + tr["t"] + tr["knob_h"] / 2)
        face(m, k1, "metal", (0, 0, 1))
    else:
        ns = 6
        oval = [(tr["x"] + tr["rx"] * math.cos(2 * math.pi * k / ns), tr["y"] + tr["ry"] * math.sin(2 * math.pi * k / ns))
                for k in range(ns)]
        slab(m, [oval], lambda x, y: ly.TAB_T + tr["t"] / 2, tr["t"], "metal", "metal", "metal")
    parts.append(m)
    return parts


# --- pencil holder --------------------------------------------------------------------------------
def z_band_base(x, y):
    return ly.body_z_top(x, y) + ly.BAND_T / 2


ARCH = (145.0, 108.0, 72.0, 35.0)  # loop arc points around the pencil axis, deg: a ~36 step keeps the arc smooth


def band_path(by, lod, filled):
    """Centre line of the strip with loops (x, z): the loop legs on the wall, the top an arc around the
    pencil (not a trapezoid along the hexagon faces); an empty loop is a sagged low arc."""
    R = ly.PEN_R
    pts = [(ly.BAND_X0, z_band_base(ly.BAND_X0, by))]
    for i, x in enumerate(ly.PEN_XS):
        zb = z_band_base(x, by)
        if lod == 1:
            continue
        if filled[i]:
            zc = zb - ly.BAND_T / 2 + R * 0.866                 # pencil axis (it lies on a facet on the leather)
            ra = R + ly.BAND_T / 2 + 0.0005
            pts.append((x - R - 0.0019, zb))
            pts += [(x + ra * math.cos(math.radians(a)), zc + ra * math.sin(math.radians(a))) for a in ARCH]
            pts.append((x + R + 0.0019, zb))
        else:
            # the empty loop has sagged: a low 3.4 mm arc (turns of 28-34 degrees at the points - no facets)
            pts += [(x - R - 0.0022, zb), (x - R, zb + 0.0024), (x, zb + 0.0034), (x + R, zb + 0.0024),
                    (x + R + 0.0022, zb)]
    pts.append((ly.BAND_X1, z_band_base(ly.BAND_X1, by)))
    if lod == 1:                                           # middle LOD: a straight strip over the pencil tops
        zt = pts[0][1] + R * 1.84
        pts = [(ly.BAND_X0, pts[0][1]), (ly.PEN_XS[0] - R - 0.002, zt), (ly.PEN_XS[-1] + R + 0.002, zt),
               (ly.BAND_X1, pts[-1][1])]
    return pts


def strip(p, pts3, nrm_fn, half_w, half_t, wdir_fn, caps=True):
    """A tape without a bottom face: the top and two edges along the polyline pts3; nrm_fn(i, t) is the
    tape's "up", wdir_fn(i, t) the width direction. No bottom is needed: the tape lies on the leather or
    on the ground."""
    bm = p.bm
    pts = [Vector(q) for q in pts3]
    n = len(pts)
    rings = []
    for i in range(n):
        if 0 < i < n - 1:
            t = (pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized()
        else:
            t = (pts[1] - pts[0]) if i == 0 else (pts[-1] - pts[-2])
        t.normalize()
        up = Vector(nrm_fn(i, t)).normalized()
        wd = Vector(wdir_fn(i, t)).normalized()
        c = pts[i]
        rings.append([bm.verts.new(c + up * half_t + wd * half_w), bm.verts.new(c + up * half_t - wd * half_w),
                      bm.verts.new(c - up * half_t - wd * half_w), bm.verts.new(c - up * half_t + wd * half_w)])
    for i in range(n - 1):
        r0, r1 = rings[i], rings[i + 1]
        up = Vector(nrm_fn(i, (pts[i + 1] - pts[i]).normalized()))
        wd = Vector(wdir_fn(i, (pts[i + 1] - pts[i]).normalized()))
        face(p, [r0[0], r0[1], r1[1], r1[0]], p.regions[p.cur][0], up)
        face(p, [r0[0], r1[0], r1[3], r0[3]], p.regions[p.cur][0], wd)
        face(p, [r0[1], r1[1], r1[2], r0[2]], p.regions[p.cur][0], -wd)
    if caps:
        for r, sg in ((rings[0], -1), (rings[-1], 1)):
            d = (pts[-1] - pts[-2]) if sg > 0 else (pts[0] - pts[1])
            face(p, list(r), p.regions[p.cur][0], d)


def build_bands(spec):
    lod = spec["lod"]
    parts = []
    for j, by in enumerate(ly.BAND_YS):
        filled = [pc["y0"] <= by - ly.BAND_W / 2 and pc["y1"] >= by + ly.BAND_W / 2 for pc in sorted(ly.PENCILS, key=lambda q: q["slot"])]
        path = band_path(by, lod, filled)
        p = P("band%d" % j, "band", group=SEL)

        def up(i, t):
            n = Vector((-t.z, 0.0, t.x))
            return n if n.z >= 0 else -n
        strip(p, [(x, by, z) for x, z in path], up, ly.BAND_W / 2, ly.BAND_T / 2, lambda i, t: (0.0, 1.0, 0.0))
        parts.append(p)
    return parts


def hex_ring(bm, x, y, zc, r, k0=0.0):
    return [bm.verts.new((x + r * math.cos(math.radians(60 * k + k0)), y, zc + r * math.sin(math.radians(60 * k + k0))))
            for k in range(6)]


def build_pencils(spec):
    lod = spec["lod"]
    R = ly.PEN_R
    parts = []
    for pc in ly.PENCILS:
        x = ly.PEN_XS[pc["slot"]]
        zc = ly.body_z_top(x, (pc["y0"] + pc["y1"]) / 2) + R * 0.866
        kind = pc["kind"]
        p = P("pencil%d" % pc["slot"], "wood")
        bm = p.bm
        y0, y1 = pc["y0"], pc["y1"]
        sharp_lo = kind == "redblue"
        sharp_hi = kind != "pen"
        b0 = y0 + (ly.SHARP if sharp_lo else 0.0)
        b1 = y1 - (ly.SHARP if sharp_hi else 0.0)
        paint_lo, paint_hi = {"redblue": ("pen_blue", "pen_red"), "green": ("pen_green", "pen_green"),
                              "black": ("pen_black", "pen_black"), "pen": ("pen_body", "pen_body")}[kind]
        lead_lo, lead_hi = {"redblue": ("lead_blue", "lead_red")}.get(kind, ("lead", "lead"))
        r_body = R if kind != "pen" else R * 0.95
        cuts = [b0, (b0 + b1) / 2, b1] if kind == "redblue" else [b0, b1]
        rings = [hex_ring(bm, x, y, zc, r_body) for y in cuts]
        for i in range(len(rings) - 1):
            reg = paint_lo if (kind == "redblue" and i == 0) else paint_hi
            for k in range(6):
                q = [rings[i][k], rings[i][(k + 1) % 6], rings[i + 1][(k + 1) % 6], rings[i + 1][k]]
                c = sum((v.co for v in q), Vector()) / 4
                face(p, q, reg, c - Vector((x, c.y, zc)))

        def tip(ring_end, y_end, sgn, lead_reg):
            """Sharpening: a cone of wood down to the lead and the lead to a point."""
            ys = y_end + sgn * (ly.SHARP - ly.LEAD)
            if lod == 0:
                small = hex_ring(bm, x, ys, zc, 0.0011)
                for k in range(6):
                    q = [ring_end[k], ring_end[(k + 1) % 6], small[(k + 1) % 6], small[k]]
                    c = sum((v.co for v in q), Vector()) / 4
                    face(p, q, "wood", c - Vector((x, c.y - sgn * 0.01, zc)))
                apex = bm.verts.new((x, y_end + sgn * ly.SHARP, zc))
                for k in range(6):
                    q = [small[k], small[(k + 1) % 6], apex]
                    c = sum((v.co for v in q), Vector()) / 3
                    face(p, q, lead_reg, c - Vector((x, c.y - sgn * 0.01, zc)))
            else:
                apex = bm.verts.new((x, y_end + sgn * ly.SHARP, zc))
                for k in range(6):
                    q = [ring_end[k], ring_end[(k + 1) % 6], apex]
                    c = sum((v.co for v in q), Vector()) / 3
                    face(p, q, "wood", c - Vector((x, c.y - sgn * 0.01, zc)))
        if sharp_hi:
            tip(rings[-1], b1, 1, lead_hi)
        if sharp_lo:
            tip(rings[0], b0, -1, lead_lo)
        elif kind == "pen" and lod == 0:
            # the writing end of the pen: a plastic cone and a steel tip of the refill
            small = hex_ring(bm, x, y0 - 0.0062, zc, 0.0011)
            for k in range(6):
                q = [rings[0][k], rings[0][(k + 1) % 6], small[(k + 1) % 6], small[k]]
                c = sum((v.co for v in q), Vector()) / 4
                face(p, q, "pen_body", c - Vector((x, c.y + 0.01, zc)))
            apex = bm.verts.new((x, y0 - 0.0084, zc))
            for k in range(6):
                q = [small[k], small[(k + 1) % 6], apex]
                c = sum((v.co for v in q), Vector()) / 3
                face(p, q, "metal", c - Vector((x, c.y + 0.01, zc)))
        else:
            # the unsharpened end of a pencil is wood with a lead (for the pen in the middle LOD, its colour)
            face(p, rings[0][::-1], paint_lo if kind == "pen" else "wood", (0, -1, 0))
        if kind == "pen":
            # cap with a clip on the upper end
            cap0, cap1 = y1 - 0.052, y1
            cr = [hex_ring(bm, x, y, zc, R * 1.12) for y in (cap0, cap1)]
            for k in range(6):
                q = [cr[0][k], cr[0][(k + 1) % 6], cr[1][(k + 1) % 6], cr[1][k]]
                c = sum((v.co for v in q), Vector()) / 4
                face(p, q, "pen_cap", c - Vector((x, c.y, zc)))
            face(p, cr[1], "pen_cap", (0, 1, 0))
            face(p, cr[0][::-1], "pen_cap", (0, -1, 0))
            if lod == 0:
                U(p, "metal")
                g.box(p, x - 0.0012, x + 0.0012, cap0 + 0.004, cap1 - 0.002, zc + R * 1.12 * 0.866,
                      zc + R * 1.12 * 0.866 + 0.0009)
        else:
            if not sharp_hi:
                face(p, rings[-1], paint_hi, (0, 1, 0))
        parts.append(p)
    return parts


def bump(v, a, b, m):
    """0 at the edges [a, b], 1 in the depth (further than m from the edge), smooth."""
    s = max(0.0, min(1.0, min(v - a, b - v) / m))
    return s * s * (3 - 2 * s)


def build_pocket(spec):
    lod = spec["lod"]
    pk = ly.POCKET
    p = P("pocket", "pocket", group=SEL)
    poly = [(pk["x0"], pk["y0"]), (pk["x1"], pk["y0"]), (pk["x1"], pk["y1"]), (pk["x0"], pk["y1"])]
    base = lambda x, y: ly.body_z_top(x, y) + pk["t"] / 2 + 0.0004  # noqa: E731
    if lod == 0:
        # the pocket is soft: the folded map bulges it by ~2.5 mm in the middle, the edges are sewn to the wall
        mx, my = 0.010, 0.012
        xc, yc = (pk["x0"] + mx, pk["x1"] - mx), (pk["y0"] + my, pk["y1"] - my)

        def zt(x, y):
            return base(x, y) + 0.0025 * bump(x, pk["x0"], pk["x1"], mx) * bump(y, pk["y0"], pk["y1"], my)
        slab(p, cells(poly, xc, yc), zt, pk["t"], "pocket", "body_bot", "edge", bottom=False, sink=0.0006)
    else:
        slab(p, [poly], base, pk["t"], "pocket", "body_bot", "edge")
    pp = ly.POCKET_PAPER
    m = P("pocket_map", "fmap")
    poly = [(pp["x0"], pp["y0"]), (pp["x1"], pp["y0"]), (pp["x1"], pp["y1"]), (pp["x0"], pp["y1"])]
    slab(m, [poly], lambda x, y: ly.body_z_top(x, y) + pp["t"] / 2 + 0.0002, pp["t"], "fmap", "paper_b", "paper_edge",
         bottom=lod != 0, sink=0.0003)
    return [p, m]


# --- ring, strap, buckle; the strap across the window with a hook ---------------------------------
def loop_pts(cx, cy, z, rx, ry, n, rot=0.0):
    a0 = math.radians(rot)
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        u, v = rx * math.cos(a), ry * math.sin(a)
        pts.append((cx + u * math.cos(a0) - v * math.sin(a0), cy + u * math.sin(a0) + v * math.cos(a0), z))
    return pts


def strap_path(lod):
    """Strap on the ground: a smooth curve through the points ly.STRAP; at the ring the strap lies on the
    lower wire of the ring and comes down to the ground within ~13 mm."""
    if lod == 0:
        pts2 = simplify(spline(ly.STRAP, 12), 0.0005)
    else:
        pts2 = list(ly.STRAP_L1)
    out, s = [], 0.0
    z_ring = ly.RING["r"] * 2 + ly.STRAP_T / 2 + 0.0002
    for i, q in enumerate(pts2):
        if i:
            s += math.dist(q, pts2[i - 1])
        k = max(0.0, 1.0 - s / 0.013) if lod == 0 else 0.0
        out.append((q[0], q[1], ly.STRAP_T / 2 + (z_ring - ly.STRAP_T / 2) * k * k * (3 - 2 * k)))
    if lod == 0 and len(out) > 2 and math.dist(out[0][:2], out[1][:2]) > 0.010:
        # a point where it leaves the ring, so that the strap lies down smoothly
        a, b = Vector(out[0]), Vector(out[1])
        mid = a + (b - a) * (0.006 / (b - a).length)
        out.insert(1, (mid.x, mid.y, ly.STRAP_T / 2 + (z_ring - ly.STRAP_T / 2) * 0.35))
    return out


def build_strap(spec):
    lod = spec["lod"]
    parts = []
    rg = ly.RING
    if lod == 0:
        m = P("ring", "metal")
        loop_pipe(m, loop_pts(rg["x"], rg["y"], rg["r"], rg["rx"], rg["ry"], 9), rg["r"], 4)
        parts.append(m)
        # the leather loop of the ring: from the side of the body to the ring (absent in the middle LOD)
        t = P("ringtab", "ringtab", group=SEL)
        g.sweep(t, [(ly.BX1 - 0.002, rg["y"], 0.017), (ly.BX1 + 0.004, rg["y"], 0.010),
                    (rg["x"] - rg["rx"], rg["y"], 0.003)], (0, 1, 0), 0.0012, 0.0055)
        parts.append(t)
    # strap on the ground
    path = strap_path(lod)
    s = P("strap", "strap")
    strip(s, path, lambda i, tt: (0, 0, 1), ly.STRAP_W / 2, ly.STRAP_T / 2,
          lambda i, tt: Vector((0, 0, 1)).cross(tt))
    parts.append(s)
    if lod == 0:
        a, b = Vector(path[-2]), Vector(path[-1])
        d = Vector((b.x - a.x, b.y - a.y, 0.0)).normalized()
        wv = Vector((-d.y, d.x, 0.0))
        # buckle on the free end: a frame with chamfered corners, the rear bar lies on the end of the strap, the
        # front one on the ground; the tongue runs from the rear bar to the front one
        bk = ly.BUCKLE
        c = b + d * (bk["h"] / 2 - 0.002)
        b_ = P("buckle", "metal")

        def zb(u):
            return bk["r"] + ly.STRAP_T * (0.5 - u / bk["h"])
        loop_pipe(b_, frame_pts(c, d, bk["h"], bk["w"], 0.0032, zb), bk["r"], 4)
        rp = Vector((c.x, c.y, 0.0)) - d * (bk["h"] / 2)
        fp = Vector((c.x, c.y, 0.0)) + d * (bk["h"] / 2 + 0.0008)
        g.pipe(b_, [tuple(rp + Vector((0, 0, zb(-bk["h"] / 2) + bk["r"] * 0.6))),
                    tuple(fp + Vector((0, 0, zb(bk["h"] / 2) + bk["r"] + 0.0006)))], 0.0008, 4)
        parts.append(b_)
        # keeper: a leather loop across the strap behind the buckle
        k_ = P("keeper", "keeper")
        kc = Vector((b.x, b.y, 0.0)) - d * 0.017
        hw = ly.STRAP_W / 2
        kp = [kc - wv * (hw + 0.0014) + Vector((0, 0, 0.0006)), kc - wv * (hw + 0.0004) + Vector((0, 0, ly.STRAP_T + 0.0007)),
              kc + wv * (hw + 0.0004) + Vector((0, 0, ly.STRAP_T + 0.0007)), kc + wv * (hw + 0.0014) + Vector((0, 0, 0.0006))]

        def kup(i, tt):
            n = d.cross(tt)
            return n if n.z >= 0 else -n
        strip(k_, [tuple(q) for q in kp], kup, 0.0042, 0.0007, lambda i, tt: d, caps=False)
        parts.append(k_)
        # hook of the window strap: a 16 x 10 mm frame on the window frame, the strap passes through it
        # (right-angle corners: a 2 mm chamfer is not visible on such a small part, but costs twice the
        # triangles)
        hk = ly.HOOK
        h_ = P("hook", "metal")
        loop_pipe(h_, frame_pts((hk["x"], hk["y"]), (0.0, 1.0), hk["h"], hk["w"], 0.0,
                                lambda u: 0.0054 + hk["r"]), hk["r"], 4)
        parts.append(h_)
    return parts


def build_wstrap(spec):
    zf, zw = 0.0054, ly.Z_WIN
    ht = ly.WSTRAP_T / 2
    path = [(ly.WSTRAP_Y0, zf + ht), (ly.WIN_Y0 - 0.0015, zf + ht), (ly.WIN_Y0 + 0.004, zw + ht + 0.0004),
            (ly.WIN_Y1 - 0.004, zw + ht + 0.0004), (ly.WIN_Y1 + 0.0015, zf + ht), (ly.WSTRAP_Y1, zf + ht)]
    if spec["lod"] == 1:
        path = [path[0], path[2], path[3], path[5]]
    p = P("wstrap", "wstrap", group=SEL)

    def up(i, t):
        n = Vector((0.0, -t.z, t.y))
        return n if n.z >= 0 else -n
    # the ends (1.3 mm) lie on the frame and are not visible, so they are omitted
    strip(p, [(ly.WSTRAP_X, y, z) for y, z in path], up, ly.WSTRAP_W / 2, ht, lambda i, t: (1.0, 0.0, 0.0),
          caps=False)
    return [p]


def build_lod(spec):
    parts = (build_body(spec) + build_leaf(spec) + build_bend(spec) + build_flap(spec) + build_sheet2(spec)
             + build_tab(spec) + build_bands(spec) + build_pencils(spec) + build_pocket(spec) + build_strap(spec)
             + build_wstrap(spec))
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        groups = {"body": ("body", "bend", "ringtab", "band", "pencil", "pocket", "ring"),
                  "leaf": ("leaf", "window", "wstrap", "hook"),
                  "flap": ("flap", "lock", "sheet2", "rivets"),
                  "strap": ("strap", "tab", "turn", "buckle", "keeper")}
        BOUNDS["comps"] = {k: [tuple(v.co) for p in parts if p.name.startswith(names) for v in p.bm.verts]
                           for k, names in groups.items()}
        print("lowest z %.5f" % BOUNDS["lo"][2])
    return parts


def preview_aspect(bbox, cam):
    x0, x1, y0, y1, z0, z1 = bbox
    c = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    d = (c - Vector(cam)).normalized()
    right = d.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(d).normalized()
    pts = [Vector(q) - c for q in kx.box_pts(*bbox)]
    w = max(q.dot(right) for q in pts) - min(q.dot(right) for q in pts)
    h = max(q.dot(up) for q in pts) - min(q.dot(up) for q in pts)
    return w / h


def hull_corners(pts):
    """Convex hull vertices without those lying on its edges (cut points on straight edges give degenerate
    hull faces, as happened with M65)."""
    hp = [Vector(q) for q in kx.hull(pts)[0]]
    keep = []
    for i, v in enumerate(hp):
        on_edge = False
        for j, a in enumerate(hp):
            if j == i or on_edge:
                continue
            for k in range(j + 1, len(hp)):
                if k == i:
                    continue
                b = hp[k]
                ab = b - a
                t = (v - a).dot(ab) / max(ab.length_squared, 1e-12)
                if 1e-4 < t < 1 - 1e-4 and (a + ab * t - v).length < 2e-4:
                    on_edge = True
                    break
        if not on_edge:
            keep.append(tuple(v))
    return keep


INV_VIEW = (0.02, -0.40, 0.85)


def collision():
    """Four convex hulls: the body with the pencil holder, the leaf with the window, the flap, the strap with
    the tab. The mass is the class weight, 0.3 kg (OZL_Carrier_Base); the hit material is leather
    (penetration\\leather)."""
    mat = kx.PEN + r"\leather.rvmat"
    comps = [(hull_corners(pts), mat) for pts in BOUNDS["comps"].values()]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    c = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, hi[2] / 2)
    memory = {
        # inventory preview camera: from the front and above - the whole open case
        "invView": [INV_VIEW],
        "ce_center": [c],
        "ce_radius": [(c[0] + 0.5 * math.dist(lo, hi), c[1], c[2])],
    }
    print("bbox %.4f..%.4f x %.4f..%.4f x 0..%.4f, preview aspect from invView %.2f (2x2 cell: ~1)"
          % (lo[0], hi[0], lo[1], hi[1], hi[2], preview_aspect(bbox, INV_VIEW)))
    return comps, 0.3, memory, bbox


# the first five are the --look preview: general view, the window with the protocol (the main part),
# the pencil holder and the pocket, the flap with the lock and the sheet, the strap with the buckle and
# the tab with the lock
SHOTS = [
    ("front", (-0.30, -0.62, 0.48), (0.01, 0.03, 0.01), 40),
    ("window", (-0.16, -0.30, 0.30), (-0.118, -0.005, 0.004), 45),
    ("pencils", (0.36, -0.20, 0.22), (0.17, 0.0, 0.03), 50),
    ("flap", (0.02, 0.52, 0.26), (0.12, 0.17, 0.01), 45),
    ("strap", (0.40, -0.40, 0.20), (0.19, -0.15, 0.006), 50),
    ("top", (0.015, 0.035, 1.05), (0.015, 0.035, 0.0), 45),
    ("side", (-0.70, -0.10, 0.12), (0.0, 0.03, 0.015), 50),
    ("inv", INV_VIEW, (0.015, 0.035, 0.01), 36),
]
M.look_shots = (5, 2)

if __name__ == "__main__":
    M.run(build_lod, collision, SHOTS, row_step=0.6, row_shot=((0.3, -1.7, 1.3), (0.3, 0.03, 0.0)))
