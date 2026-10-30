"""M52 - Ballistic sample (OZL_Sample_12): a sample of the Ballistics line shared by all factions - a
small impact-resistant case with the lid open; in the foam cutouts lie a bolt, a firing pin, a spring
and two fired cartridge cases, and a tag with a blue stripe is tied to the firing pin. A portable 2x2
item.

    blender --background --python build_m52.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py with the system Python first (the tag, a sticker on the body).

Target: ~18 x 15 x 9 cm 'like a Pelican 1120'; black plastic with ribs, two latches, a handle, a
pressure valve without a brand; the lid open by ~100 degrees, grey foam with cutouts inside; a tag with
a blue stripe (the Ballistics line); 200-800 triangles, texture 512.

Prototype and sizes:
- case: Pelican 1120 Protector (the Protector series dates from the 1980s): outside 206 x 167 x 90 mm,
  inside 184 x 121 x 78 mm (lid 13 + body 65), 0.58 kg - RS Components 296-3098; the inside is 7.24 x
  4.76 x 3.07" there and 8.12 x 6.56 x 3.56" at sportsmans.com. Model: body 200 x 144 at the top of the
  walls, parting belt 206 x 150, the walls taper to the bottom by 3 mm; body 66 mm, lid 24 mm; hinges at
  the back, the axis along the back edge of the belt, the lid open at 100 degrees. The latches are on
  the lid (as on the Protector), open and sticking out past the front edge, as in the photo; the latch
  keepers are on the body under the belt. The handle is folded down along the face of the body, with a
  pressure equalisation valve above it (no brand).
- foam: Pick N Pluck: 1/2" (12.7 mm) cubes with scores; the sockets are plucked by cubes (rectangular),
  deep enough for the parts to protrude 3-5 mm. The lid has an 'egg crate'.
- AKM bolt: no official part dimensions were found - an estimate from a photo of an AKS-74U bolt at a
  length of 90 mm: head D 18.5 x 24 mm with two locking lugs (D 23.5 across), an extractor, a guide cam,
  a tail D 10.5.
- firing pin: 95 mm after the Arsenal AK-262FF (7.62x39, '3.8 x 0.2 in'): shaft D 4.5, tail D 7.
- spring: coiled, D 9 x 82 mm, pitch 4.2 (the coils are a texture along a helix; an estimate).
- 7.62x39 cases per C.I.P.: length 38.7, rim D 11.35, D 10.07 at the shoulder (at 30.5), neck D 8.6. One
  is brass (an imported cartridge), the other lacquered steel (Soviet); the primers are punched, soot at
  the necks.
- mass 750 g: the case with foam 0.58 kg (RS) + bolt, firing pin, spring, cases.

State 'used but intact' as for all samples: dusty plastic with small wear along the ribs, pressed foam,
metal worn to a shine. No faction colour (the sample is shared). Signs: a tag with a blue stripe, empty
fields and a hand-written number in digits; an empty inventory sticker on the body. No lamps, screens or
moving parts, so no work view.

Design decisions: the 'dayz' look (matte, dirtier, the rvmat comes from the profile). Edges and moulding
follow the photo of the case:
- the case corners in plan are three segments (30 degrees, below the smoothing threshold of 40, so the
  corners are round, not faceted), a chamfer on the top of the body belt, the lid top is rounded;
- latches are a lever with a hook at the end, the keepers under the belt are a wedge with a step; the
  handle is cast, the shoulders narrower than the grip, smooth bends, the face with bevels, hanging on
  steel pins between pairs of post ribs; the valve is round, with a chamfer and ribbing; hinges are
  cylinders, the three knuckles and the axis ends are texture; padlock lugs at the corners of the belt
  and the lid; on the lid edge a rubber gasket ring (texture);
- foam: dark grey, the Pick N Pluck scores are thin cuts (wider ones read as tiles), oil blotches and
  lint;
- parts in the sockets: the bolt is a body of revolution (end chamfer, step to the tail) with chamfered
  lugs, a guide cam with rounded corners and an extractor; the end has a cup for the case with the
  firing pin hole and soot, the tail a pin hole; the firing pin is a conical striker, a shaft and a step
  to the tail; the cases are rim, groove, body, shoulder, neck, funnel (10 sides); the tag string is
  stretched to the firing pin and wound round its tail;
- no vanilla items: DayZ has no separate bolt, firing pin, spring or fired case models, and the vanilla
  Protector Case is closed;
- the 'dayz' dirt layers are a local copy of kmats.weather / dayz_layers: kit scratches on faces across
  their axis give light blotches;
- budget - small item (near up to 1.5k).

LODs: near 1498 and mid 468 (~31 %: corners of two segments, no sockets - the parts are sunk into flat
foam, a hexagonal valve, no keepers, lugs, extractor or string), no far LOD.

The origin is the centre of the bottom: autocenter = 0 (in Geometry), boundingbox_min at the bottom -
the case stands on its bottom. Collision is two convex hulls: the body and the open lid. The inventory
camera (invView) is front-left-above: the sockets with the parts and the lid foam are visible; a 2x2
cell is square and the case with the open lid is about as wide as it is tall.
"""
import math
import os
import sys

import bmesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import m52_layout as L  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# case corners: 3 segments per corner (30 degrees - smooth at the 40 degree threshold), 2 at the mid LOD
LOD_SPECS = [
    dict(lod=0, corner=3, sides=10),
    dict(lod=1, corner=2, sides=6),
]

REGIONS = {
    "case": ("case", 1.0), "hw": ("hw", 1.2), "valve": ("valve", 2.0), "foam": ("foam", 0.8),
    "foam_lid": ("foam_lid", 0.8), "bolt": ("bolt", 3.0), "pin": ("pin", 3.0), "spring": ("spring", 3.0),
    "brass": ("brass", 3.5), "lacq": ("lacq", 3.5), "tag": ("tag", 3.0), "cord": ("cord", 0.6),
    "sticker": ("sticker", 2.5), "hinge": ("hinge", 1.5), "lid_top": ("lid_top", 1.0),
    "rib": ("rib", 1.2), "ear": ("ear", 1.5), "ear_b": ("ear_b", 1.5), "gasket": ("gasket", 1.0),
}


def wdecal(name):
    return os.path.join(WORK, name)


TAG_DEC = (wdecal("decal_tag.png"), "z", 1, ("x", "y"), L.TAG_C, (L.TAG_BOX, L.TAG_BOX), (L.TAG_Z[1] - 0.0002, 0.065))
STK_DEC = (wdecal("decal_sticker.png"), "y", -1, ("x", "z"), L.STK_C, L.STK, None)

# samples: used but intact - no chips or rust, a little dust and dirt
LIT = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.05, grime=0.15)


def wall_y(z, lod=0):
    """Body face (-Y) at height z: a tapered wall (the mid LOD - from the bottom to the top of the
    belt).
    """
    if lod > 0:
        return -(L.BY - L.DRAFT / 2 + (L.FL + L.DRAFT / 2) * z / L.Z_P)
    return -(L.BY - L.DRAFT * (L.Z_FL0 - z) / L.Z_FL0)


Y_FL = -(L.BY + L.FL)                                                # face of the belt (body and lid)
PIVOT_Y = wall_y(L.PIVOT_Z) - L.HANDLE_GAP - L.HANDLE_HT              # handle axis, mid-thickness
EAR_LID_C = L.lid_rot((L.EAR_X, Y_FL - L.EAR_DY, L.Z_P + 0.002))     # lid lug hole (lid open)
EAR_LID_AX = L.lid_dir((0.0, 0.0, 1.0))
EAR_BASE_C = (L.EAR_X, Y_FL - L.EAR_DY, L.Z_P - 0.002)


# --- materials --------------------------------------------------------------------------------
def dayz_layers(t, col, g, vec, sep, nsep, grime):
    """kmats.dayz_layers with one fix: scratches along x (s1) do not land on faces looking along x, and
    scratches along y (s2) not on faces looking along y. In kit the scratch noise is stretched along a
    world axis, and on faces across this axis it degenerates into round light blotches ~4 mm (on a small
    case they look like paint splashes). The rest is as in kit.
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
    st = t.math("MULTIPLY", t.math("MULTIPLY", st, vert), k["streaks"] * min(1.0, 0.4 + grime))
    col = t.mixc(st, col, kmats.GRIME)
    sm = t.math("MULTIPLY", t.step(t.noise(vec, 3.2, 4.0, 0.5), 0.64, 0.74), k["smudge"])
    col = t.mixc(sm, col, kmats.lin((40, 36, 30)))
    s1 = t.step(t.noise(t.stretch(vec, 0.03, 1.0, 1.0), 220.0, 2.0, 0.5), 0.71, 0.725)
    s2 = t.step(t.noise(t.stretch(vec, 1.0, 0.03, 1.0), 220.0, 2.0, 0.5), 0.71, 0.725)
    s1 = t.math("MULTIPLY", s1, t.maprange(t.math("ABSOLUTE", nsep.outputs["X"]), 0.3, 0.6, 1.0, 0.0))
    s2 = t.math("MULTIPLY", s2, t.maprange(t.math("ABSOLUTE", nsep.outputs["Y"]), 0.3, 0.6, 1.0, 0.0))
    sc = t.math("MULTIPLY", t.math("MAXIMUM", s1, s2),
                t.maprange(t.noise(vec, 6.0, 4.0, 0.5), 0.4, 0.7, 0.0, k["scratches"]))
    col = t.mixc(sc, col, t.mixc(0.5, col, (0.55, 0.55, 0.55, 1)))
    g = t.math("MAXIMUM", g, t.math("MAXIMUM", st, sm))
    return col, g


def weather(t, col, vec, sep, nsep, floor_z=0.0, dust=0.35, grime=0.5, cav=0.5, low_h=0.25):
    """kmats.weather, but the 'dayz' profile layers come from dayz_layers above (scratches without
    blotches).
    """
    if kmats.LOOK["name"] != "dayz":
        return kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, cav, low_h)
    dust, cav = dust * kmats.LOOK["dust_k"], cav * kmats.LOOK["cav_k"]
    up = t.maprange(nsep.outputs["Z"], 0.4, 0.9, 0.0, 1.0)
    dn = t.maprange(t.noise(vec, 4.0, 6.0, 0.6), 0.35, 0.7, 0.4, 1.0)
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", up, dn), dust), col, kmats.DUST)
    c = t.maprange(t.cavity(0.04), 0.15, 0.6, 0.0, 1.0)
    low = t.maprange(sep.outputs["Z"], floor_z, floor_z + low_h, 1.0, 0.0)
    g = t.math("MAXIMUM", t.math("MULTIPLY", c, cav), t.math("MULTIPLY", low, grime))
    g = t.math("MULTIPLY", g, t.maprange(t.noise(vec, 7.0, 8.0, 0.6), 0.3, 0.7, 0.5, 1.0))
    col = t.mixc(g, col, kmats.GRIME)
    return dayz_layers(t, col, g, vec, sep, nsep, grime)


def build_plastic(mat, origin, color, seed=3.0, gloss=0.35, spec=0.25, floor_z=0.0, dust=0.3, grime=0.3,
                  mottle=0.06, scuff=(0.62, 0.70), low_h=0.03):
    """kmats.build_plastic with its own weather (no blotches) and floor dirt only in the bottom low_h (a
    9 cm case: with kit's 25 cm the whole case is 'at the floor').
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    col = t.mixc(t.maprange(t.noise(vec, 6.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                 tuple(c * (1 - mottle) for c in color[:3]) + (1,), tuple(min(1.0, c * (1 + mottle)) for c in color[:3]) + (1,))
    edge = t.maprange(t.edge_wear(0.002), 0.06, 0.25, 0.0, 1.0)
    sc = t.step(t.math("ADD", t.math("MULTIPLY", t.noise(vec, 18.0, 8.0, 0.7), 0.7), t.math("MULTIPLY", edge, 0.6)),
                scuff[0], scuff[1])
    col = t.mixc(t.math("MULTIPLY", sc, 0.35), col, tuple(min(1.0, c * 1.6 + 0.04) for c in color[:3]) + (1,))
    col, dirt = weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.4, low_h)
    g = t.math("SUBTRACT", gloss, t.math("MULTIPLY", t.math("ADD", dirt, sc), gloss * 0.5))
    s = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.5))
    return kmats.out(t, col, g, s, t.math("MULTIPLY", sc, -0.2))


def build_foam(mat, origin, color, seed=1.0, grid=False, egg=None):
    """Grey foam: pores, pressed and greasy patches, lint dust, shadow in the sockets; grid - Pick N
    Pluck scores by 12.7 mm cubes (both on the top, across the wall on the socket walls); egg = pitch -
    an 'egg crate' in the plane of the open lid (the pattern runs from the hinge axis along L.LID_DIR).
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    x, y, z = sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]
    dark = tuple(c * 0.72 for c in color[:3]) + (1,)
    pores = t.noise(vec, 1800.0, 2.0, 0.5)
    col = t.mixc(t.maprange(pores, 0.3, 0.7, 0.0, 1.0), tuple(c * 0.86 for c in color[:3]) + (1,), color)
    col = t.mixc(t.maprange(t.noise(vec, 45.0, 4.0, 0.6), 0.4, 0.75, 0.0, 0.35), col, dark)
    # greasy from fingers and parts (oil from the bolt), pressed: darker blotches
    smear = t.step(t.noise(vec, 70.0, 4.0, 0.6), 0.60, 0.72)
    col = t.mixc(t.math("MULTIPLY", smear, 0.45), col, tuple(c * 0.55 for c in color[:3]) + (1,))
    h = t.math("SUBTRACT", t.math("MULTIPLY", pores, 0.18), t.math("MULTIPLY", smear, 0.15))
    if grid:
        # scores are thin closed cuts, not tile seams: a narrow dark line, uneven along its length
        def line(c, c0):
            q = t.math("FRACT", t.math("DIVIDE", t.math("SUBTRACT", c, c0), L.PITCH))
            d = t.math("SUBTRACT", 0.5, t.math("ABSOLUTE", t.math("SUBTRACT", q, 0.5)))
            return t.maprange(d, 0.005, 0.016, 1.0, 0.0)
        lx = t.math("MULTIPLY", line(x, L.GX0), t.math("SUBTRACT", 1.0, t.math("ABSOLUTE", nsep.outputs["X"])))
        ly = t.math("MULTIPLY", line(y, L.GY0), t.math("SUBTRACT", 1.0, t.math("ABSOLUTE", nsep.outputs["Y"])))
        ln = t.math("MULTIPLY", t.math("MAXIMUM", lx, ly), t.maprange(t.noise(vec, 160.0, 3.0, 0.6), 0.3, 0.7, 0.45, 1.0))
        col = t.mixc(t.math("MULTIPLY", ln, 0.55), col, tuple(c * 0.45 for c in color[:3]) + (1,))
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", ln, 0.35))
    if egg:
        s = t.math("ADD", t.math("MULTIPLY", t.math("SUBTRACT", y, L.HINGE_Y), L.LID_DIR[1]),
                   t.math("MULTIPLY", t.math("SUBTRACT", z, L.HINGE_Z), L.LID_DIR[2]))
        k = 2 * math.pi / egg
        e = t.math("MULTIPLY", t.math("SINE", t.math("MULTIPLY", x, k)), t.math("SINE", t.math("MULTIPLY", s, k)))
        hh = t.math("ADD", 0.5, t.math("MULTIPLY", e, 0.5))
        col = t.mixc(t.maprange(hh, 0.0, 1.0, 0.55, 0.0), col, dark)
        h = t.math("ADD", h, t.math("MULTIPLY", hh, 1.6))
    cav = t.maprange(t.cavity(0.012), 0.1, 0.55, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.7), col, tuple(c * 0.35 for c in color[:3]) + (1,))
    up = t.maprange(nsep.outputs["Z"], 0.5, 0.95, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", up, t.maprange(t.noise(vec, 9.0, 6.0, 0.6), 0.45, 0.75, 0.0, 0.3)),
                 col, kmats.DUST)
    # lint and crumbs: light dots
    lint = t.step(t.noise(vec, 700.0, 2.0, 0.5), 0.74, 0.76)
    col = t.mixc(t.math("MULTIPLY", lint, 0.35), col, kmats.DUST)
    return kmats.out(t, col, 0.05, 0.03, h)


def build_gunmetal(mat, origin, color, bright, seed=1.0, gloss=0.5, spec=0.65, wear=(0.55, 0.75)):
    """Blued or phosphated steel: an even dark tone, worn to a shine along edges and protrusions, a thin
    layer of oil and dirt in the corners.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    tone = t.maprange(t.noise(vec, 320.0, 4.0, 0.6), 0.3, 0.7, 0.0, 1.0)
    base = t.mixc(tone, tuple(c * 0.82 for c in color[:3]) + (1,), color)
    edge = t.maprange(t.edge_wear(0.0010), 0.05, 0.3, 0.0, 1.0)
    rub = t.step(t.math("ADD", t.math("MULTIPLY", t.noise(t.stretch(vec, 0.2, 1.0, 1.0), 500.0, 6.0, 0.7), 0.55),
                        t.math("MULTIPLY", edge, 0.85)), wear[0], wear[1])
    col = t.mixc(rub, base, bright)
    col, dirt = weather(t, col, vec, sep, nsep, -1.0, dust=0.04, grime=0.0, cav=0.7, low_h=0.01)
    g_ = t.math("SUBTRACT", t.mixf(rub, gloss, gloss + 0.2), t.math("MULTIPLY", dirt, gloss * 0.6))
    s = t.math("SUBTRACT", t.mixf(rub, spec, 0.9), t.math("MULTIPLY", dirt, spec * 0.6))
    return kmats.out(t, col, g_, s, t.math("MULTIPLY", tone, 0.05))


def _over(mat, origin, o):
    """A tree on top of a finished builder: (t, x, y, z, normal, colour, height, gloss, highlight)."""
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    _, sep = t.coords(origin, 0.0)
    nsep = t.normal()
    s = [kmats.sock(mat, o[k]) if not isinstance(o[k], (int, float)) else o[k]
         for k in ("color", "height", "gloss", "spec")]
    return (t, sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"], nsep) + tuple(s)


def _dist2(t, a, a0, b, b0):
    """Distance in the plane of two coordinates to the point (a0, b0)."""
    da, db = t.math("SUBTRACT", a, a0), t.math("SUBTRACT", b, b0)
    return t.math("SQRT", t.math("ADD", t.math("MULTIPLY", da, da), t.math("MULTIPLY", db, db)))


def build_boltmat(mat, origin, face=None, xhole=None, **kw):
    """Bolt: blued steel (build_gunmetal) plus a cup for the case head on the end of the head with the
    firing pin hole and soot (face = (end x, y and z of the axis, cup r, hole r)), and on top of the
    tail a hole for the firing pin retaining pin (xhole = (x, y, r)).
    """
    o = build_gunmetal(mat, origin, **kw)
    t, x, y, z, nsep, col, h, g_, s_ = _over(mat, origin, o)
    if face:
        xf, yc, zc, rc, rh = face
        rad = _dist2(t, y, yc, z, zc)
        front = t.math("MULTIPLY", t.math("LESS_THAN", nsep.outputs["X"], -0.7), t.math("LESS_THAN", x, xf + 0.0006))
        soot = t.math("MULTIPLY", front, t.maprange(rad, rc + 0.002, rc - 0.001, 0.0, 0.85))
        col = t.mixc(soot, col, (0.008, 0.007, 0.006, 1))
        edge = t.math("MULTIPLY", front, t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", rad, rc)), 0.0002, 0.0005,
                                                    1.0, 0.0))
        col = t.mixc(t.math("MULTIPLY", edge, 0.85), col, (0.002, 0.002, 0.002, 1))
        hole = t.math("MULTIPLY", front, t.math("LESS_THAN", rad, rh))
        col = t.mixc(hole, col, (0.0, 0.0, 0.0, 1))
        cup = t.math("MULTIPLY", front, t.math("LESS_THAN", rad, rc))
        h = t.math("SUBTRACT", h, t.math("ADD", t.math("MULTIPLY", cup, 0.6), hole))
        g_ = t.mixf(t.math("MAXIMUM", soot, hole), g_, 0.05)
        s_ = t.mixf(t.math("MAXIMUM", soot, hole), s_, 0.05)
    if xhole:
        xh, yh, rh = xhole
        hole2 = t.math("MULTIPLY", t.math("GREATER_THAN", nsep.outputs["Z"], 0.5),
                       t.math("LESS_THAN", _dist2(t, x, xh, y, yh), rh))
        col = t.mixc(hole2, col, (0.0, 0.0, 0.0, 1))
        h = t.math("SUBTRACT", h, hole2)
    return kmats.out(t, col, g_, s_, h)


def build_spring(mat, origin, color, bright, x0, yc, zc, pitch, r):
    """Coiled spring on a cylinder: coils along a helix (phase = x / pitch + angle / 2pi), a dark gap
    between the coils; a wire ring at the ends, dark inside.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 7.0)
    nsep = t.normal()
    x, y, z = sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]
    dy, dz = t.math("SUBTRACT", y, yc), t.math("SUBTRACT", z, zc)
    ang = t.math("DIVIDE", t.math("ARCTAN2", dz, dy), 2 * math.pi)
    q = t.math("FRACT", t.math("ADD", t.math("DIVIDE", t.math("SUBTRACT", x, x0), pitch), ang))
    coil = t.math("SUBTRACT", 1.0, t.math("ABSOLUTE", t.math("SUBTRACT", t.math("MULTIPLY", q, 2.0), 1.0)))
    wire = t.maprange(coil, 0.18, 0.42, 0.0, 1.0)
    top = t.maprange(coil, 0.55, 0.95, 0.0, 1.0)
    col = t.mixc(top, color, bright)
    col = t.mixc(wire, (0.004, 0.004, 0.005, 1), col)
    rad = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", dy, dy), t.math("MULTIPLY", dz, dz)))
    end = t.math("MULTIPLY", t.math("GREATER_THAN", t.math("ABSOLUTE", nsep.outputs["X"]), 0.7),
                 t.math("LESS_THAN", rad, r - 0.0013))
    col = t.mixc(end, col, (0.004, 0.004, 0.005, 1))
    # oil and dust in the gaps between the coils
    oil = t.math("MULTIPLY", t.maprange(t.noise(vec, 90.0, 4.0, 0.6), 0.45, 0.7, 0.0, 0.5), t.math("SUBTRACT", 1.0, top))
    col = t.mixc(oil, col, (0.012, 0.011, 0.009, 1))
    g_ = t.mixf(wire, 0.1, 0.6)
    s = t.mixf(wire, 0.05, 0.75)
    h = t.math("SUBTRACT", t.math("MULTIPLY", wire, t.math("ADD", 0.4, t.math("MULTIPLY", top, 0.6))),
               t.math("MULTIPLY", end, 1.0))
    return kmats.out(t, col, g_, s, h)


def build_cartridge(mat, origin, color, x_head, sign, yc, zc, gloss=0.6, spec=0.7, lacquer=False):
    """Fired case along X: a punched primer on the head, dark in the groove at the rim, soot at the neck
    (black inside the neck); brass has tarnish patches, lacquer is worn to steel along the rim. The
    groove, shoulder and neck are geometry (build_small).
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 9.0 + x_head * 10)
    nsep = t.normal()
    x, y, z = sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]
    u = t.math("MULTIPLY", t.math("SUBTRACT", x, x_head), float(sign))         # 0 - head, 38.7 mm - neck
    dy, dz = t.math("SUBTRACT", y, yc), t.math("SUBTRACT", z, zc)
    rad = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", dy, dy), t.math("MULTIPLY", dz, dz)))
    tarn = t.maprange(t.noise(vec, 260.0, 5.0, 0.65), 0.45, 0.75, 0.0, 0.6)
    col = t.mixc(tarn, color, tuple(c * 0.55 for c in color[:3]) + (1,))
    streak = t.maprange(t.noise(t.stretch(vec, 0.08, 1.0, 1.0), 700.0, 4.0, 0.7), 0.55, 0.8, 0.0, 0.5)
    col = t.mixc(streak, col, tuple(min(1.0, c * 1.35) for c in color[:3]) + (1,))
    if lacquer:
        rim = t.math("MULTIPLY", t.math("LESS_THAN", u, L.CASE_RIM_L + 0.0002),
                     t.maprange(t.edge_wear(0.0006), 0.05, 0.3, 0.0, 1.0))
        col = t.mixc(rim, col, kmats.lin((150, 150, 148)))
    groove = t.math("MULTIPLY", t.math("GREATER_THAN", u, L.CASE_RIM_L), t.math("LESS_THAN", u, L.CASE_BODY_X))
    col = t.mixc(t.math("MULTIPLY", groove, 0.45), col, (0.01, 0.009, 0.006, 1))
    head = t.math("MULTIPLY", t.math("GREATER_THAN", t.math("MULTIPLY", nsep.outputs["X"], -float(sign)), 0.7),
                  t.math("LESS_THAN", u, 0.0004))
    primer = t.math("MULTIPLY", head, t.math("LESS_THAN", rad, 0.0027))
    col = t.mixc(primer, col, kmats.lin((176, 120, 72)))
    ring = t.math("MULTIPLY", head, t.math("MULTIPLY", t.math("GREATER_THAN", rad, 0.0027), t.math("LESS_THAN", rad, 0.0031)))
    dent = t.math("MULTIPLY", head, t.math("LESS_THAN", rad, 0.0008))
    col = t.mixc(t.math("MAXIMUM", ring, t.math("MULTIPLY", dent, 0.8)), col, (0.02, 0.016, 0.01, 1))
    soot = t.maprange(u, 0.031, 0.0387, 0.0, 0.75)
    inside = t.math("MULTIPLY", t.math("GREATER_THAN", u, 0.0355), t.math("LESS_THAN", rad, L.CASE_NECK - 0.0002))
    col = t.mixc(t.math("MAXIMUM", soot, inside), col, (0.012, 0.011, 0.010, 1))
    # dust and fingerprints on the fired case
    col, dirt = weather(t, col, vec, sep, nsep, -1.0, dust=0.05, grime=0.0, cav=0.5, low_h=0.01)
    g_ = t.math("SUBTRACT", gloss, t.math("MULTIPLY", t.math("MAXIMUM", t.math("MAXIMUM", soot, tarn), dirt), gloss * 0.7))
    s = t.math("SUBTRACT", spec, t.math("MULTIPLY", t.math("MAXIMUM", soot, tarn), spec * 0.6))
    h = t.math("SUBTRACT", 0.0, t.math("ADD", t.math("MULTIPLY", groove, 0.3), t.math("MULTIPLY", dent, 1.0)))
    return kmats.out(t, col, g_, s, h)


def build_valve(mat, origin, color, xc, zc):
    """Pressure valve on the face of the body: a ribbed rim (rays round the circle, longitudinal ribs on
    the side), a smooth middle with a groove; dust in the ribbing.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 6.0)
    nsep = t.normal()
    x, z = sep.outputs["X"], sep.outputs["Z"]
    dx, dz = t.math("SUBTRACT", x, xc), t.math("SUBTRACT", z, zc)
    rad = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", dx, dx), t.math("MULTIPLY", dz, dz)))
    ang = t.math("ARCTAN2", dz, dx)
    knurl = t.math("MULTIPLY", t.math("GREATER_THAN", rad, 0.0068),
                   t.maprange(t.math("SINE", t.math("MULTIPLY", ang, 36.0)), -0.2, 0.6, 0.0, 1.0))
    mid = t.math("LESS_THAN", rad, 0.0058)
    col = t.mixc(t.math("MULTIPLY", knurl, 0.5), color, tuple(c * 2.2 for c in color[:3]) + (1,))
    col = t.mixc(t.math("MULTIPLY", mid, 0.6), col, tuple(c * 1.6 for c in color[:3]) + (1,))
    ring = t.math("MULTIPLY", t.math("GREATER_THAN", rad, 0.0058), t.math("LESS_THAN", rad, 0.0066))
    col = t.mixc(ring, col, (0.004, 0.004, 0.004, 1))
    col, dirt = weather(t, col, vec, sep, nsep, -1.0, dust=0.15, grime=0.0, cav=0.6, low_h=0.01)
    g_ = t.math("SUBTRACT", t.mixf(mid, 0.3, 0.45), t.math("MULTIPLY", dirt, 0.15))
    return kmats.out(t, col, g_, 0.25, t.math("SUBTRACT", t.math("MULTIPLY", knurl, 0.6), ring))


def build_lid_top(mat, origin, **kw):
    """Top of the lid (open - faces backwards): plastic and a moulded panel - a groove 10 mm from the
    edge (in lid axes: x and s run from the hinge axis along L.LID_DIR), finer texture inside the panel.
    """
    o = build_plastic(mat, origin, **kw)
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    _, sep = t.coords(origin, 0.0)
    x, y, z = sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]
    s = t.math("ADD", t.math("MULTIPLY", t.math("SUBTRACT", y, L.HINGE_Y), L.LID_DIR[1]),
               t.math("MULTIPLY", t.math("SUBTRACT", z, L.HINGE_Z), L.LID_DIR[2]))
    hx = L.BX - L.LID_TOP_IN - 0.010
    s0 = L.HINGE_Y - (L.BY - L.LID_TOP_IN) + 0.010
    s1 = L.HINGE_Y + (L.BY - L.LID_TOP_IN) - 0.010
    # distance to the panel outline (max norm): < 0 inside
    dx = t.math("SUBTRACT", t.math("ABSOLUTE", x), hx)
    ds = t.math("SUBTRACT", t.math("ABSOLUTE", t.math("SUBTRACT", s, (s0 + s1) / 2)), (s1 - s0) / 2)
    d = t.math("MAXIMUM", dx, ds)
    groove = t.maprange(t.math("ABSOLUTE", d), 0.0006, 0.0016, 1.0, 0.0)
    inside = t.maprange(d, 0.0, -0.0015, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", groove, 0.8), kmats.sock(mat, o["color"]), (0.006, 0.006, 0.007, 1))
    col = t.mixc(t.math("MULTIPLY", inside, 0.25), col, (0.03, 0.03, 0.033, 1))
    h = t.math("SUBTRACT", t.math("MULTIPLY", inside, -0.4), t.math("MULTIPLY", groove, 0.8))
    h = t.math("ADD", h, kmats.sock(mat, o["height"]))
    return kmats.out(t, col, kmats.sock(mat, o["gloss"]), kmats.sock(mat, o["spec"]), h)


STEEL_PIN = kmats.lin((118, 118, 122))


def build_hinge(mat, origin, xs, half, y0, z0, r, **kw):
    """Hinges at the back: plastic, three knuckles per hinge - dark gaps between them, a steel axis (r)
    at the ends. Hinges are symmetric in x (|x| is taken).
    """
    o = build_plastic(mat, origin, **kw)
    t, x, y, z, nsep, col, h, g_, s_ = _over(mat, origin, o)
    ax = t.math("ABSOLUTE", x)
    gap = None
    for xb in (abs(xs[0]) - half / 3, abs(xs[0]) + half / 3):
        gg = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", ax, xb)), 0.0003, 0.0008, 1.0, 0.0)
        gap = gg if gap is None else t.math("MAXIMUM", gap, gg)
    pin = t.math("MULTIPLY", t.math("GREATER_THAN", t.math("ABSOLUTE", nsep.outputs["X"]), 0.7),
                 t.math("LESS_THAN", _dist2(t, y, y0, z, z0), r))
    col = t.mixc(t.math("MULTIPLY", gap, 0.85), col, (0.004, 0.004, 0.004, 1))
    col = t.mixc(pin, col, STEEL_PIN)
    h = t.math("SUBTRACT", h, t.math("MULTIPLY", gap, 0.8))
    return kmats.out(t, col, t.mixf(pin, g_, 0.5), t.mixf(pin, s_, 0.6), h)


def build_rib(mat, origin, y0, z0, r, **kw):
    """Handle post ribs: body plastic, on the sides the steel end of the handle axis pin (y0, z0, r)."""
    o = build_plastic(mat, origin, **kw)
    t, x, y, z, nsep, col, h, g_, s_ = _over(mat, origin, o)
    d = _dist2(t, y, y0, z, z0)
    side = t.math("GREATER_THAN", t.math("ABSOLUTE", nsep.outputs["X"]), 0.7)
    pin = t.math("MULTIPLY", side, t.math("LESS_THAN", d, r))
    rim = t.math("MULTIPLY", side, t.math("MULTIPLY", t.math("GREATER_THAN", d, r), t.math("LESS_THAN", d, r + 0.0004)))
    col = t.mixc(t.math("MULTIPLY", rim, 0.7), col, (0.004, 0.004, 0.004, 1))
    col = t.mixc(pin, col, STEEL_PIN)
    h = t.math("ADD", h, t.math("MULTIPLY", pin, 0.4))
    return kmats.out(t, col, t.mixf(pin, g_, 0.5), t.mixf(pin, s_, 0.6), h)


def build_ear(mat, origin, c, axis, r, **kw):
    """Padlock lug: body plastic and a hole r along the direction axis through the point c (dark, with a
    worn edge). Lugs are symmetric in x (|x| is taken).
    """
    o = build_plastic(mat, origin, **kw)
    t, x, y, z, nsep, col, h, g_, s_ = _over(mat, origin, o)
    comb = t.node("ShaderNodeCombineXYZ")
    t.link(t.math("ABSOLUTE", x), comb.inputs[0])
    t.link(y, comb.inputs[1])
    t.link(z, comb.inputs[2])
    d = t.node("ShaderNodeVectorMath")
    d.operation = "SUBTRACT"
    t.link(comb.outputs[0], d.inputs[0])
    d.inputs[1].default_value = tuple(c)
    dot = t.node("ShaderNodeVectorMath")
    dot.operation = "DOT_PRODUCT"
    t.link(d.outputs[0], dot.inputs[0])
    dot.inputs[1].default_value = tuple(axis)
    sc = t.node("ShaderNodeVectorMath")
    sc.operation = "SCALE"
    sc.inputs[0].default_value = tuple(axis)
    t.link(dot.outputs["Value"], sc.inputs[3])
    pr = t.node("ShaderNodeVectorMath")
    pr.operation = "SUBTRACT"
    t.link(d.outputs[0], pr.inputs[0])
    t.link(sc.outputs[0], pr.inputs[1])
    ln = t.node("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    t.link(pr.outputs[0], ln.inputs[0])
    dist = ln.outputs["Value"]
    hole = t.maprange(dist, r - 0.0002, r + 0.0001, 1.0, 0.0)
    worn = t.maprange(dist, r + 0.0001, r + 0.0010, 1.0, 0.0)
    col = t.mixc(t.math("MULTIPLY", worn, 0.5), col, kmats.lin((70, 70, 72)))
    col = t.mixc(hole, col, (0.0, 0.0, 0.0, 1))
    h = t.math("SUBTRACT", h, hole)
    return kmats.out(t, col, t.mixf(hole, g_, 0.0), t.mixf(hole, s_, 0.0), h)


def build_gasket(mat, origin, **kw):
    """Rim of the open lid's parting line: body plastic and a rubber gasket ring in the groove - a strip
    1.4-4 mm from the wall inside (max norm in closed-lid axes: x and y = HINGE_Y - s).
    """
    o = build_plastic(mat, origin, **kw)
    t, x, y, z, nsep, col, h, g_, s_ = _over(mat, origin, o)
    s = t.math("ADD", t.math("MULTIPLY", t.math("SUBTRACT", y, L.HINGE_Y), L.LID_DIR[1]),
               t.math("MULTIPLY", t.math("SUBTRACT", z, L.HINGE_Z), L.LID_DIR[2]))
    yc = t.math("SUBTRACT", L.HINGE_Y, s)
    d = t.math("MAXIMUM", t.math("SUBTRACT", t.math("ABSOLUTE", x), L.IX), t.math("SUBTRACT", t.math("ABSOLUTE", yc), L.IY))
    ring_ = t.math("MULTIPLY", t.maprange(d, 0.0012, 0.0016, 0.0, 1.0), t.maprange(d, 0.0042, 0.0038, 0.0, 1.0))
    seam = t.math("MAXIMUM", t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", d, 0.0013)), 0.0001, 0.0003, 1.0, 0.0),
                  t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", d, 0.0041)), 0.0001, 0.0003, 1.0, 0.0))
    rub = t.mixc(t.maprange(t.noise(t.coords(origin, 4.4)[0], 120.0, 3.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                 kmats.lin((40, 40, 42)), kmats.lin((50, 49, 50)))
    col = t.mixc(ring_, col, rub)
    col = t.mixc(t.math("MULTIPLY", seam, 0.8), col, (0.003, 0.003, 0.003, 1))
    h = t.math("SUBTRACT", t.math("ADD", h, t.math("MULTIPLY", ring_, 0.25)), t.math("MULTIPLY", seam, 0.6))
    return kmats.out(t, col, t.mixf(ring_, g_, 0.12), t.mixf(ring_, s_, 0.06), h)


# wear of black plastic is along the edges (edge_wear), rare on flat surfaces: otherwise light blotches
CASE = dict(color=kmats.lin((30, 30, 32)), seed=2.1, gloss=0.28, spec=0.2, dust=0.12, grime=0.3, mottle=0.06,
            scuff=(0.76, 0.82))
HW = dict(color=kmats.lin((24, 24, 25)), seed=2.7, gloss=0.38, spec=0.25, dust=0.25, grime=0.3, mottle=0.04,
          scuff=(0.72, 0.80))
KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "case": (build_plastic, CASE),
    "lid_top": (build_lid_top, dict(CASE, seed=2.4)),
    "gasket": (build_gasket, dict(CASE, seed=2.6)),
    "hw": (build_plastic, HW),
    "hinge": (build_hinge, dict(HW, seed=2.9, xs=L.HINGE_X, half=L.HINGE_LEN / 2, y0=L.HINGE_Y, z0=L.HINGE_Z,
                                r=0.0013)),
    "rib": (build_rib, dict(CASE, seed=3.1, y0=PIVOT_Y, z0=L.PIVOT_Z, r=L.PIVOT_R)),
    "ear": (build_ear, dict(CASE, seed=3.3, c=EAR_LID_C, axis=EAR_LID_AX, r=L.EAR_R)),
    "ear_b": (build_ear, dict(CASE, seed=3.5, c=EAR_BASE_C, axis=(0.0, 0.0, 1.0), r=L.EAR_R)),
    "valve": (build_valve, dict(color=kmats.lin((34, 34, 36)), xc=0.0, zc=L.VALVE_Z)),
    # foam: dark grey, like Pick N Pluck (a lighter tone comes out almost white in the preview)
    "foam": (build_foam, dict(color=kmats.lin((100, 102, 104)), seed=3.7, grid=True)),
    "foam_lid": (build_foam, dict(color=kmats.lin((94, 96, 98)), seed=4.1, egg=0.024)),
    "bolt": (build_boltmat, dict(color=kmats.lin((40, 42, 48)), bright=kmats.lin((150, 152, 156)), seed=5.0,
                                 face=(L.BOLT_X0, L.BOLT_Y, L.BOLT_ZC, 0.0058, 0.0011),
                                 xhole=(L.BOLT_X0 + L.BOLT_LEN - 0.0065, L.BOLT_Y, 0.0012))),
    "pin": (build_gunmetal, dict(color=kmats.lin((70, 72, 76)), bright=kmats.lin((168, 168, 170)), seed=5.6,
                                 wear=(0.5, 0.7))),
    "spring": (build_spring, dict(color=kmats.lin((52, 52, 55)), bright=kmats.lin((150, 150, 152)), x0=L.SPR_X0,
                                  yc=L.SPR_Y, zc=L.SPR_ZC, pitch=L.SPR_PITCH, r=L.SPR_R)),
    # fired brass is muted, lacquered steel is greenish brown (Soviet lacquer)
    "brass": (build_cartridge, dict(color=kmats.lin((182, 146, 84)), x_head=L.CASES[0][1], sign=L.CASES[0][2],
                                    yc=L.CASES[0][0], zc=L.CASE_ZC)),
    "lacq": (build_cartridge, dict(color=kmats.lin((104, 92, 58)), x_head=L.CASES[1][1], sign=L.CASES[1][2],
                                   yc=L.CASES[1][0], zc=L.CASE_ZC, gloss=0.45, spec=0.4, lacquer=True)),
    "tag": ("paint", dict(LIT, color=kmats.lin((232, 228, 214)), under=kmats.lin((232, 228, 214)), seed=7.6,
                          gloss=0.12, spec=0.06, decal_items=[TAG_DEC])),
    "cord": (build_plastic, dict(color=kmats.lin((196, 186, 160)), seed=7.0, gloss=0.08, spec=0.04, dust=0.1,
                             grime=0.25, mottle=0.12, scuff=(0.9, 1.0))),
    "sticker": ("paint", dict(LIT, color=kmats.lin((226, 222, 204)), under=kmats.lin((226, 222, 204)), seed=8.1,
                              gloss=0.3, spec=0.2, decal_items=[STK_DEC])),
})

OBJ, NAME = "m52_ball_sample", "ozr_ball_sample"
# rvmat from the 'dayz' profile (specular 1.0 / 80): the highlight is set by _smdi
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=512, look="dayz")
P = M.part
BOUNDS = {}
EPS = 1e-6


# --- helpers --------------------------------------------------------------------------------
def rrect(x0, x1, y0, y1, r, n):
    """Rounded rectangle, counter-clockwise (top view); n is segments per corner."""
    if r <= 0 or n <= 0:
        return [(x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def outline(inset, n):
    """Body outline shifted inwards (inset > 0) or outwards (< 0)."""
    return rrect(-L.BX + inset, L.BX - inset, -L.BY + inset, L.BY - inset, max(L.RC - inset, 0.002), n)


def inner(n):
    return rrect(-L.IX, L.IX, -L.IY, L.IY, L.RI, n)


def orient(p, faces, want):
    """Reorient faces by the expected direction want(centre) -> vector."""
    p.bm.normal_update()
    for f in faces:
        if f.normal.dot(Vector(want(f.calc_center_median()))) < 0:
            f.normal_flip()
    p.bm.normal_update()
    return p.tag(faces)


def radial(c):
    return (c.x, c.y, 0.0)


def radial_up(c):
    return (c.x, c.y, math.hypot(c.x, c.y))


def band(p, ring_a, ring_b, want):
    """A strip of quads between two vertex rings (the same number of points)."""
    faces = []
    for i in range(len(ring_a)):
        j = (i + 1) % len(ring_a)
        faces.append(p.bm.faces.new([ring_a[i], ring_a[j], ring_b[j], ring_b[i]]))
    return orient(p, faces, want)


def ring(p, poly, z):
    return [p.bm.verts.new((x, y, z)) for x, y in poly]


def revolve(p, prof, origin, axis, u, sides, phase=0.0, caps=(False, False)):
    """Body of revolution: prof [(a, r)] - along the direction axis from origin, and the radius, r = 0
    is a vertex on the axis (cone, funnel). The profile runs along the body surface from one end to the
    other; outward is to the left of the direction in the (a, r) plane: this way the ends, steps, the
    case groove and the neck funnel face correctly (a lathe_x whose normals run from the middle of the
    body would flip a groove face looking towards the middle). caps - a flat polygonal end at the first
    ring (faces -axis) and at the last (+axis): two triangles fewer than a fan to the axis.
    """
    bm = p.bm
    o, ax, uu = Vector(origin), Vector(axis).normalized(), Vector(u).normalized()
    vv = ax.cross(uu)

    def rad(k):
        t = 2 * math.pi * k / sides + phase
        return uu * math.cos(t) + vv * math.sin(t)
    rings = []
    for a, r in prof:
        if r <= 0:
            rings.append([bm.verts.new(o + ax * a)] * sides)
        else:
            rings.append([bm.verts.new(o + ax * a + rad(k) * r) for k in range(sides)])
    faces = []
    for i in range(len(prof) - 1):
        (a0, r0), (a1, r1) = prof[i], prof[i + 1]
        na, nr = -(r1 - r0), (a1 - a0)
        for k in range(sides):
            j = (k + 1) % sides
            q = [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]
            q = [v for m, v in enumerate(q) if v not in q[:m]]
            if len(q) < 3:
                continue
            f = bm.faces.new(q)
            f.normal_update()
            if f.normal.dot(ax * na + rad(k + 0.5) * nr) < 0:
                f.normal_flip()
            faces.append(f)
    for idx, sgn in ((0, -1.0), (-1, 1.0)):
        if caps[0 if idx == 0 else 1] and prof[idx][1] > 0:
            f = bm.faces.new(rings[idx])
            f.normal_update()
            if f.normal.dot(ax * sgn) < 0:
                f.normal_flip()
            faces.append(f)
    bm.normal_update()
    return p.tag(faces)


def drop(p, test):
    """Remove hidden faces of a part (the root of a cast-on part inside the wall, the bottom of the tag
    on the foam).
    """
    p.bm.normal_update()
    gone = [f for f in p.bm.faces if test(f.normal, f.calc_center_median())]
    bmesh.ops.delete(p.bm, geom=gone, context="FACES")
    p.bm.normal_update()


def inside_wall(lod=0):
    """Root face of a part cast onto the body face: it looks into the wall (+y) and stands behind the
    face.
    """
    return lambda n, c: n.y > 0.9 and c.y > wall_y(c.z, lod) - 1e-5


def inside_flange(n, c):
    """Root face of a part on the belt face (of the body or the closed lid): it looks into the belt and
    stands in it.
    """
    return n.y > 0.9 and c.y > Y_FL - 1e-5


def bar(p, pts, out, hws, ht, face=0.55):
    """Cast handle bar along the polyline pts in the plane with normal out (outwards, towards the
    person): a six-point section - flat back, a face with bevels (face - the share of the face width);
    hws[i] is the half-width at point i (shoulders narrower than the grip), ht the half-thickness. A
    bisector bevel at the bends.
    """
    bm = p.bm
    pv = [Vector(q) for q in pts]
    nrm = Vector(out).normalized()
    n = len(pv)
    sec = ((1.0, -1.0), (1.0, 0.3), (face, 1.0), (-face, 1.0), (-1.0, 0.3), (-1.0, -1.0))
    rings = []
    for i in range(n):
        if 0 < i < n - 1:
            a = (pv[i] - pv[i - 1]).normalized()
            b = (pv[i + 1] - pv[i]).normalized()
            t = a + b
            t = b if t.length < 1e-9 else t.normalized()
            k = max(0.3, a.dot(t))
        else:
            t = (pv[1] - pv[0]) if i == 0 else (pv[-1] - pv[-2])
            t.normalize()
            k = 1.0
        w = t.cross(nrm).normalized() * (hws[i] / k)
        rings.append([bm.verts.new(pv[i] + w * sw + nrm * (ht * sn)) for sw, sn in sec])
    m = len(sec)
    faces = []
    for i in range(n - 1):
        r0, r1 = rings[i], rings[i + 1]
        for q in range(m):
            faces.append(bm.faces.new([r0[q], r0[(q + 1) % m], r1[(q + 1) % m], r1[q]]))
    faces.append(bm.faces.new(rings[0][::-1]))
    faces.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return p.tag(faces)


def boxp(name, region, x0, x1, y0, y1, z0, z1, **kw):
    p = P(name, region)
    g.box(p, x0, x1, y0, y1, z0, z1, **kw)
    return p


def rotate_lid(parts):
    m = Matrix.Rotation(math.radians(-L.LID_OPEN), 3, "X")
    for p in parts:
        bmesh.ops.rotate(p.bm, cent=(0.0, L.HINGE_Y, L.HINGE_Z), matrix=m, verts=p.bm.verts[:])
        p.bm.normal_update()
    return parts


def front_poly(pts_mm, y0, z0):
    """Profile in the y-z plane from millimetres (forward from the face y0, up from z0) -> (y, z) in
    metres.
    """
    return [(y0 - dy * 0.001, z0 + dz * 0.001) for dy, dz in pts_mm]


# latch in the open position (in closed-lid axes): a thickening at the axis, a thinner lever, a hook at
# the end that catches the body keeper; mm: forward from the belt face, up from the parting line
LATCH_MM = [(-0.5, 0.8), (19.5, 1.6), (20.5, -0.8), (24.5, -0.8), (25.5, 3.0), (24.0, 5.8), (-0.5, 5.6)]
# padlock lugs: on the lid (above the parting line) and on the body belt (below it), rounded end; the
# root is inside the belt, not in the parting plane (otherwise faces would coincide with the rim)
EAR_LID_MM = [(-1.5, 0.2), (6.0, 0.2), (7.5, 1.3), (7.5, 2.9), (6.0, 4.0), (-1.5, 4.0)]
EAR_BASE_MM = [(-1.0, -4.0), (6.0, -4.0), (7.5, -2.8), (7.5, -1.2), (6.0, 0.0), (-1.0, 0.0)]


# --- body -----------------------------------------------------------------------------------
def build_base(spec):
    lod, n = spec["lod"], spec["corner"]
    parts = []
    p = P("base", "case")
    if lod == 0:
        # tapered wall (narrower at the bottom by DRAFT), a step under the belt, a chamfer on top of the
        # belt
        r0 = ring(p, outline(L.DRAFT, n), 0.0)
        r1 = ring(p, outline(0.0, n), L.Z_FL0)
        band(p, r0, r1, radial)
        fl0 = ring(p, outline(-L.FL, n), L.Z_FL0)
        band(p, r1, fl0, lambda c: (0, 0, -1))                       # bottom of the belt
        fl1 = ring(p, outline(-L.FL, n), L.Z_P - L.CH)
        band(p, fl0, fl1, radial)
        top = ring(p, outline(-L.FL + L.CH, n), L.Z_P)
        band(p, fl1, top, radial_up)                                 # chamfer
    else:
        r0 = ring(p, outline(L.DRAFT / 2, n), 0.0)
        top = ring(p, outline(-L.FL, n), L.Z_P)
        band(p, r0, top, radial)
    orient(p, [p.bm.faces.new(r0)], lambda c: (0, 0, -1))            # bottom
    in1 = ring(p, inner(n), L.Z_P)
    band(p, top, in1, lambda c: (0, 0, 1))                           # parting rim
    in0 = ring(p, inner(n), L.FOAM_Z - 0.0005)
    band(p, in0, in1, lambda c: (-c.x, -c.y, 0))                     # wall inside down to the foam
    parts.append(p)
    # foam: with plucked sockets (a boolean difference) at the near LOD, flat at the mid
    if lod == 0:
        fm = P("foam", "foam")
        g.box(fm, -L.IX, L.IX, -L.IY, L.IY, L.FOAM_Z - 0.017, L.FOAM_Z)
        cuts = []
        for name, ((x0, x1, y0, y1), d) in L.POCKETS.items():
            c = P("pocket_" + name, "foam")
            g.box(c, x0, x1, y0, y1, L.FOAM_Z - d, L.FOAM_Z + 0.004)
            cuts.append(c)
        fm = M.boolean("foam", fm, cuts)
        hidden = [f for f in fm.bm.faces
                  if f.calc_center_median().z < L.FOAM_Z - 0.0165 or
                  (abs(f.normal.z) < 0.5 and (abs(f.calc_center_median().x) > L.IX - 1e-4 or
                                              abs(f.calc_center_median().y) > L.IY - 1e-4))]
        bmesh.ops.delete(fm.bm, geom=hidden, context="FACES")
        fm.bm.normal_update()
    else:
        fm = P("foam", "foam")
        f = fm.bm.faces.new([fm.bm.verts.new((x, y, L.FOAM_Z)) for x, y in inner(n)])
        orient(fm, [f], lambda c: (0, 0, 1))
    parts.append(fm)
    return parts


def build_lid(spec):
    """Lid in the closed position (then rotated about the hinge axis): belt, walls, rounded top, rim,
    inner wall and the 'egg crate' foam; the latches are open past the front edge, padlock lugs at the
    corners.
    """
    lod, n = spec["lod"], spec["corner"]
    p = P("lid", "case")
    f0 = ring(p, outline(-L.FL, n), L.Z_P)
    if lod == 0:
        f1 = ring(p, outline(-L.FL, n), L.Z_LF1)
        band(p, f0, f1, radial)
        w0 = ring(p, outline(0.0, n), L.Z_LF1)
        band(p, f1, w0, lambda c: (0, 0, 1))                         # top of the belt
        w1 = ring(p, outline(L.LID_R0, n), L.Z_LT - L.LID_RZ)        # the wall tapers towards the top
        band(p, w0, w1, radial)
        top = ring(p, outline(L.LID_R1, n), L.Z_LT)                  # top rounding
        band(p, w1, top, radial_up)
    else:
        top = ring(p, outline(L.LID_TOP_IN / 2, n), L.Z_LT)
        band(p, f0, top, radial)
    tf = p.bm.faces.new(top)
    orient(p, [tf], lambda c: (0, 0, 1))
    p.tag([tf], p.region_index("lid_top", *REGIONS["lid_top"]))
    i0 = ring(p, inner(n), L.Z_P)
    rim = band(p, f0, i0, lambda c: (0, 0, -1))                      # parting rim with the gasket
    p.tag(rim, p.region_index("gasket", *REGIONS["gasket"]))
    i1 = ring(p, inner(n), L.Z_LIN + 0.0005)
    band(p, i0, i1, lambda c: (-c.x, -c.y, 0))
    fl = P("lid_foam", "foam_lid")
    f = fl.bm.faces.new([fl.bm.verts.new((x, y, L.Z_LIN)) for x, y in inner(n)])
    orient(fl, [f], lambda c: (0, 0, -1))
    lt = P("latches", "hw")
    parts = [p, fl, lt]
    for s in (-1, 1):
        x = s * L.LATCH_X
        if lod == 0:
            g.prism(lt, front_poly(LATCH_MM, Y_FL, L.Z_P), (1, 2), x - L.LATCH_HW, x + L.LATCH_HW)
        else:
            g.box(lt, x - L.LATCH_HW, x + L.LATCH_HW, Y_FL - L.LATCH_L, Y_FL + 0.0005, L.Z_P + 0.0010, L.Z_P + 0.0060)
    drop(lt, inside_flange)
    if lod == 0:
        er = P("lid_ears", "ear")
        for s in (-1, 1):
            g.prism(er, front_poly(EAR_LID_MM, Y_FL, L.Z_P), (1, 2), s * L.EAR_X - L.EAR_W, s * L.EAR_X + L.EAR_W)
        drop(er, inside_flange)
        parts.append(er)
    return rotate_lid(parts)


def handle_path(lod):
    """Handle axis in the face plane (x, z): shoulders from the axes down, bends of radius HANDLE_R
    (three segments per bend at the near LOD), the grip below; half-width per point - wider at the grip.
    """
    hx, zb, rr = L.HANDLE_X, L.HANDLE_BAR_Z, L.HANDLE_R
    zt = L.PIVOT_Z + 0.0025
    hw, hg = L.HANDLE_HW, L.HANDLE_HG
    if lod == 0:
        left = [(-hx + rr + rr * math.cos(math.radians(a)), zb + rr + rr * math.sin(math.radians(a))) for a in (210, 240)]
        right = [(hx - rr + rr * math.cos(math.radians(a)), zb + rr + rr * math.sin(math.radians(a))) for a in (300, 330)]
        pts = [(-hx, zt), (-hx, zb + rr)] + left + [(-hx + rr, zb), (hx - rr, zb)] + right + [(hx, zb + rr), (hx, zt)]
        ws = [hw, hw, hw + (hg - hw) * 0.35, hw + (hg - hw) * 0.7, hg, hg, hw + (hg - hw) * 0.7, hw + (hg - hw) * 0.35,
              hw, hw]
    else:
        pts = [(-hx, zt), (-hx, zb + rr * 0.4), (-hx + rr * 0.4, zb), (hx - rr * 0.4, zb), (hx, zb + rr * 0.4), (hx, zt)]
        ws = [hw, hw, hg, hg, hw, hw]
    return pts, ws


def build_hardware(spec):
    """Hinges at the back (on the axis), the handle on pins between the post ribs, the valve, latch
    keepers, padlock lugs, a sticker - on the face of the body.
    """
    lod, s = spec["lod"], spec["sides"]
    parts = []
    hg = P("hinges", "hinge")
    for x in L.HINGE_X:
        if lod == 0:
            g.cyl(hg, (x, L.HINGE_Y, L.HINGE_Z), "x", L.HINGE_R, L.HINGE_LEN, 8)
        else:           # boxes - at the near-LOD hinge positions (the atlas is empty between them)
            g.box(hg, x - L.HINGE_LEN / 2, x + L.HINGE_LEN / 2, L.HINGE_Y - L.HINGE_R, L.HINGE_Y + L.HINGE_R,
                  L.HINGE_Z - L.HINGE_R, L.HINGE_Z + L.HINGE_R)
    if lod == 0:        # the lower front quarter of the cylinder is inside the body belt
        drop(hg, lambda n, c: abs(n.x) < 0.5 and c.y < L.HINGE_Y - 0.0005 and c.z < L.HINGE_Z - 0.0005)
    parts.append(hg)
    # handle: a cast bar along the face (the back is HANDLE_GAP from the wall)
    hd = P("handle", "hw")
    pts2, ws = handle_path(lod)
    pts = [(x, wall_y(z, lod) - L.HANDLE_GAP - L.HANDLE_HT, z) for x, z in pts2]
    if lod == 0:
        bar(hd, pts, (0, -1, 0), ws, L.HANDLE_HT)
    else:
        g.sweep(hd, pts, (0, 1, 0), L.HANDLE_HW, L.HANDLE_HT)
    parts.append(hd)
    # post ribs at the sides of the handle shoulders: under the belt on top, a bevel into the wall at
    # the bottom
    rb = P("ribs", "rib")
    zr0 = 0.010
    for sx in (-1, 1):
        for dx in (-L.RIB_DX, L.RIB_DX):
            xr = sx * (L.HANDLE_X + dx)
            poly = [(wall_y(zr0, lod) + 0.0005, zr0), (wall_y(zr0 + 0.006, lod) - L.RIB_OUT, zr0 + 0.006),
                    (wall_y(L.Z_FL0, lod) - L.RIB_OUT, L.Z_FL0), (wall_y(L.Z_FL0, lod) + 0.0005, L.Z_FL0)]
            g.prism(rb, poly, (1, 2), xr - L.RIB_W / 2, xr + L.RIB_W / 2)
    drop(rb, inside_wall(lod))
    parts.append(rb)
    vy = wall_y(L.VALVE_Z, lod)
    vv = P("valve", "valve")
    if lod == 0:
        # valve: round, ribbed side (texture), a chamfer, a flat top with a button (texture)
        prof = [(0.0, L.VALVE_R), (0.0040, L.VALVE_R), (0.0052, L.VALVE_R - 0.0012)]
        revolve(vv, prof, (0.0, vy + 0.0005, L.VALVE_Z), (0, -1, 0), (1, 0, 0), 12, caps=(False, True))
    else:
        g.cyl(vv, (0.0, vy - 0.002, L.VALVE_Z), "y", L.VALVE_R, 0.005, 6)
    parts.append(vv)
    if lod == 0:
        # latch keepers under the belt: a wedge from the wall up to a step under which the hook catches
        kp = P("keepers", "case")
        z0, z1 = L.KEEPER_Z
        for sx in (-1, 1):
            x = sx * L.LATCH_X
            poly = [(wall_y(z0) + 0.0005, z0), (wall_y(z1) - 0.0034, z1), (wall_y(L.Z_FL0) - 0.0034, L.Z_FL0),
                    (wall_y(L.Z_FL0) + 0.0005, L.Z_FL0)]
            g.prism(kp, poly, (1, 2), x - L.LATCH_HW, x + L.LATCH_HW)
        drop(kp, inside_wall(0))
        parts.append(kp)
        # padlock lugs on the body belt (under the lid lugs)
        er = P("base_ears", "ear_b")
        for sx in (-1, 1):
            g.prism(er, front_poly(EAR_BASE_MM, Y_FL, L.Z_P), (1, 2), sx * L.EAR_X - L.EAR_W, sx * L.EAR_X + L.EAR_W)
        drop(er, inside_flange)
        parts.append(er)
    st = P("sticker", "sticker")
    (cx, cz), (w, h) = L.STK_C, L.STK
    corners = [(cx - w / 2, cz - h / 2), (cx + w / 2, cz - h / 2), (cx + w / 2, cz + h / 2), (cx - w / 2, cz + h / 2)]
    g.quad(st, [(x, wall_y(z, lod) - 0.0003, z) for x, z in corners])
    orient(st, st.bm.faces[:], lambda c: (0, -1, 0))
    parts.append(st)
    return parts


# --- contents -------------------------------------------------------------------------------
def build_bolt(spec):
    """AKM bolt lying with the head towards -X: a body of revolution (end chamfer, head, step to the
    tail), two chamfered locking lugs (at the sides), a guide cam on top, diagonal (towards the case
    face), with rounded corners, an extractor at the end; the cup for the case, the firing pin and pin
    holes are texture.
    """
    lod, s = spec["lod"], spec["sides"]
    x0, y, zc = L.BOLT_X0, L.BOLT_Y, L.BOLT_ZC
    R, Rt, hl, ln = L.BOLT_HEAD_R, L.BOLT_TAIL_R, L.BOLT_HEAD_L, L.BOLT_LEN
    p = P("bolt", "bolt")
    xh = x0 + hl
    if lod > 0:                                                      # head with lugs - one box
        g.box(p, x0, xh, y - 0.01175, y + 0.01175, zc - R, zc + R)
        g.cyl(p, ((xh + x0 + ln) / 2, y, zc), "x", Rt, x0 + ln - xh, s)
        return [p]
    revolve(p, [(0.0, 0.0080), (0.0010, R), (hl, R), (hl, Rt), (ln, Rt)], (x0, y, zc), (1, 0, 0), (0, 1, 0), s,
            caps=(True, True))

    def frame(deg):
        a = math.radians(deg)
        return g.Frame((0.0, y, zc), (1, 0, 0), (0, math.cos(a), math.sin(a)), (0, -math.sin(a), math.cos(a)))
    lug = [(x0, R - 0.0015), (x0, 0.0110), (x0 + 0.0008, 0.01175), (x0 + 0.010, 0.01175), (x0 + 0.010, R - 0.0015)]
    for deg in (0.0, 180.0):                                         # locking lugs
        g.prism(p, lug, (0, 1), -0.0035, 0.0035, frame=frame(deg))
    cam = [(-0.003, R - 0.0015), (0.003, R - 0.0015), (0.003, R + 0.0035), (0.002, R + 0.0045), (-0.002, R + 0.0045),
           (-0.003, R + 0.0035)]
    g.prism(p, cam, (2, 1), xh - 0.009, xh + 0.001, frame=frame(120.0))      # guide cam, to the case face
    g.box(p, x0 - 0.0003, x0 + 0.012, R - 0.0010, R + 0.0007, -0.0016, 0.0016, frame=frame(145.0))   # extractor
    return [p]


def build_small(spec):
    """Firing pin, spring, two cases."""
    lod, s = spec["lod"], spec["sides"]
    parts = []
    pn = P("pin", "pin")
    if lod == 0:
        # striker - a cone to the D 4.5 shaft, a smooth step to the D 7 tail, a flat end
        prof = [(0.0, 0.0), (0.004, L.PIN_R), (0.068, L.PIN_R), (0.0705, L.PIN_R2), (L.PIN_LEN, L.PIN_R2)]
        revolve(pn, prof, (L.PIN_X0, L.PIN_Y, L.PIN_ZC), (1, 0, 0), (0, 1, 0), 8, caps=(False, True))
    else:
        prof = [(0.0, 0.0), (0.004, L.PIN_R), (0.070, L.PIN_R), (0.070, L.PIN_R2), (L.PIN_LEN, L.PIN_R2)]
        revolve(pn, prof, (L.PIN_X0, L.PIN_Y, L.PIN_ZC), (1, 0, 0), (0, 1, 0), 5, caps=(False, True))
    parts.append(pn)
    sp = P("spring", "spring")
    g.cyl(sp, (L.SPR_X0 + L.SPR_LEN / 2, L.SPR_Y, L.SPR_ZC), "x", L.SPR_R, L.SPR_LEN, 10 if lod == 0 else s)
    parts.append(sp)
    for (yc, xh, sg), reg in zip(L.CASES, ("brass", "lacq")):
        c = P("case_" + reg, reg)
        if lod > 0:
            g.cyl(c, (xh + sg * L.CASE_LEN / 2, yc, L.CASE_ZC), "x", L.CASE_SH, L.CASE_LEN, s)
            parts.append(c)
            continue
        # 10 sides - below the smoothing threshold (40 degrees): the case is round. Head, rim, groove,
        # body up to the shoulder, shoulder, neck and funnel inside
        prof = [(0.0, L.CASE_RIM), (L.CASE_RIM_L, L.CASE_RIM), (L.CASE_GROOVE_X, L.CASE_GROOVE_R),
                (L.CASE_BODY_X, L.CASE_BODY_R), (L.CASE_SH_X, L.CASE_SH), (L.CASE_NECK_X, L.CASE_NECK),
                (L.CASE_LEN, L.CASE_NECK), (L.CASE_LEN - 0.0025, 0.0)]
        revolve(c, prof, (xh, yc, L.CASE_ZC), (sg, 0, 0), (0, 1, 0), 10, phase=math.pi / 10, caps=(True, False))
        parts.append(c)
    return parts


def build_tag(spec):
    lod = spec["lod"]
    h, w, c = L.TAG_L / 2, L.TAG_W / 2, L.TAG_CUT
    poly = [L.tag_point(sv, tv) for sv, tv in ((-h, -w + c), (-h + c, -w), (h, -w), (h, w), (-h + c, w), (-h, w - c))]
    tg = P("tag", "tag")
    # 0.3 mm card lies on the foam: one face (the 0.3 mm edge is not visible)
    f = tg.bm.faces.new([tg.bm.verts.new((x, y, L.TAG_Z[1])) for x, y in poly])
    orient(tg, [f], lambda c_: (0, 0, 1))
    parts = [tg]
    if lod == 0:
        # string: from the eyelet stretched across the foam to the tail of the firing pin, a turn round
        # it (pitch along the axis - so it does not cross itself) and an end pulled into a knot next to
        # the incoming end
        ex, ey = L.tag_point(-L.TAG_HOLE, 0.0)
        rl = L.PIN_R2 + 0.0009            # the turn chords (65 degrees) barely go into the firing pin

        def at(deg, x):
            a = math.radians(deg)
            return (x, L.PIN_Y + rl * math.cos(a), L.PIN_ZC + rl * math.sin(a))
        pts = [(ex, ey, L.TAG_Z[1] + 0.0004), (0.0232, -0.0184, L.FOAM_Z + 0.0005),
               at(165, 0.0211), at(100, 0.0207), at(35, 0.0203), at(-30, 0.0199), at(-95, 0.0195), at(-160, 0.0191),
               at(155, 0.0186)]
        cd = P("cord", "cord")
        g.pipe(cd, pts, 0.0006, 4)
        parts.append(cd)
    return parts


def build_lod(spec):
    parts = build_base(spec) + build_lid(spec) + build_hardware(spec) + build_bolt(spec) + build_small(spec) + \
        build_tag(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def preview_aspect(bbox, cam):
    """Width / height of the preview frame from camera cam onto the centre (a 2x2 cell - about 1)."""
    x0, x1, y0, y1, z0, z1 = bbox
    c = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    d = (c - Vector(cam)).normalized()
    right = d.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(d).normalized()
    pts = [Vector(q) - c for q in kx.box_pts(*bbox)]
    w = max(q.dot(right) for q in pts) - min(q.dot(right) for q in pts)
    h = max(q.dot(up) for q in pts) - min(q.dot(up) for q in pts)
    return w / h


INV_VIEW = (-0.20, -0.46, 0.40)


def collision():
    """Two convex hulls: the body up to the parting line and the open lid (no latches). The mass is the
    sample weight, 0.75 kg; the impact sound is plastic.
    """
    ring_b = outline(-L.FL, 2)
    base = [(x, y, z) for x, y in ring_b for z in (0.0, L.Z_P)]
    lid = [L.lid_rot((x, y, z)) for x, y in ring_b for z in (L.Z_P, L.Z_LT)]
    pen = kx.PEN + r"\plastic.rvmat"
    comps = [(base, pen), (lid, pen)]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    c = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, hi[2] / 2)
    memory = {
        "invView": [INV_VIEW],
        "ce_center": [c],
        "ce_radius": [(c[0] + 0.5 * math.dist(lo, hi), c[1], c[2])],
    }
    print("bbox %.4f..%.4f x %.4f..%.4f x 0..%.4f, preview aspect from invView %.2f (2x2 cell: ~1)"
          % (lo[0], hi[0], lo[1], hi[1], hi[2], preview_aspect(bbox, INV_VIEW)))
    return comps, 0.75, memory, bbox


# the first six are the --look previews (M.look_shots): overview, parts in the sockets close-up, top
# view, face hardware close-up (handle, valve, ribs, keepers, lugs), lid back and hinges, inventory
# camera
SHOTS = [
    ("front", (-0.26, -0.50, 0.38), (0.0, 0.01, 0.085), 45),
    ("parts", (0.10, -0.16, 0.19), (0.02, 0.0, 0.058), 50),
    ("inside", (-0.02, -0.21, 0.33), (0.005, 0.0, 0.055), 50),
    ("lock", (0.13, -0.30, 0.12), (0.03, -0.07, 0.05), 50),
    ("back", (0.34, 0.50, 0.30), (0.0, 0.03, 0.09), 45),
    ("inv", INV_VIEW, (0.0, 0.022, 0.118), 36),
    ("side", (0.55, -0.12, 0.16), (0.0, 0.02, 0.10), 45),
]
M.look_shots = (6, 2)

if __name__ == "__main__":
    M.run(build_lod, collision, SHOTS, row_step=0.26, row_shot=((0.13, -0.95, 0.45), (0.13, 0.0, 0.10)))
