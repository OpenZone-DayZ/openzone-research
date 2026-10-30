"""M48 - Anomalous sample (OZL_Sample_03, candidate class): a sample of the Anomaly line shared by all
factions - a portable 1x1 item. A lead cup with a screw cap and a wire seal.

    blender --background --python build_m48.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py with the system Python first (a trefoil for the ring tag, a stamp on the cap).

Target: a lead capsule-cylinder (a lead cup for sources and active samples) D 4 x 9 cm, dull grey cast
lead, thread and knurling on the cap, a wire seal through a lug, a yellow ring tag with a radiation
sign. Samples: 200-800 triangles, texture 512, no faction colour, state used but intact; the vanilla
stand-in for grip and preview is InjectionVial (1x1).

Prototype and sizes: a laboratory lead container for preparations (Wikimedia Commons,
File:Plomo_blindaje.jpg): a cast lead cup whose cap goes over the top of the body and is slightly wider;
the photographed body has peeling paint, ours is bare lead. The class is a lead pig / vial shield
(Mirion C-vial shield 0665-0001: outer D 43 mm, inner D 27 mm, height 80 mm, lead 8 mm, 0.79 kg; Images
SI lead pig 57 x 89 mm). The D 4 x 9 cm target fits this class: body D 40 mm, cap D 42 mm, height 90 mm
(cap 25.5 mm, ~4 mm of open neck thread under the cap). The mass in the mod is 60 g (shared with
OZL_Sample_Base, unchanged; a real cup of this size weighs 0.8-1.2 kg); the mass in Geometry is the
same.

Details: diamond knurling on the cap, the neck thread, two cast lugs (body and cap) with holes, a wire
loop through both and a lead lens seal with a letterless imprint, a yellow ring tag with four trefoils
and a folded-seam lock, a number stamped in digits on the cap end. Dull lead with whitish oxide in
patches and recesses, scratches, small dents, edges rubbed by hands.

Design: the 'dayz' look (matte, dirtier, AO baked into the colour). No corners: the body has 20 sides
and the cap 28, the bottom, the shoulder and the cap top are rounded (the top rounding is three segments
over 90 degrees: kexport smooths edges up to 40 degrees, so it is smooth in game). The ring tag is a
separate ring over the body (0.7 mm) with a folded-seam lock; the cast lugs have through holes; the seal
is a lens with a rim; the wire is a Catmull-Rom spline with a parallel-transported section frame (the
section does not twist), not a polyline. No vanilla items (DayZ has no lead container, and a small
sample takes no extras) and no work view: a sample is an item, not a station.

LODs (small item, 0.3-1.5k): near ~1.5k triangles (above the 800 budget of samples on purpose: detail
comes first), mid ~35-40 %, no far LOD. The knurling and the thread are relief in the texture (_nohq).

Blender axes: X is width, Y is depth (the front faces -Y), Z is up. The origin is the centre of the
bottom, the cup stands.
"""
import math
import os
import sys

import bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m ---------------------------------------------------------------------------
R_BODY = 0.020                 # body, D 40 mm
FIL_BOT = 0.0014               # bottom rounding (casting)
Z_BAND0, Z_BAND1 = 0.026, 0.046   # ring tag
BAND_T = 0.0007                # the ring stands proud of the body
R_BAND = R_BODY + BAND_T
BAND_CH = 0.00035              # chamfer of the ring edges (along the height)
Z_SHOULDER = 0.0603
R_NECK = 0.0188                # neck with the thread; the shoulder is the rounding R_BODY - R_NECK
Z_CAP0 = 0.0645                # cap bottom
R_CAP = 0.021                  # cap, D 42 mm
CH_CAP = 0.0005                # chamfer of the cap bottom
Z_KNURL0, Z_KNURL1 = 0.0672, 0.0852
FIL_TOP = 0.0020               # rounding of the cap top
Z_TOP = 0.090
TREFOIL_D = 0.0125             # as in make_decals.py
STAMP_D = 0.026
SEAM_A = -135.0                # folded-seam lock of the ring: front left, at the joint of the unwrap sides
SEAM_W = 0.0016
N_KNURL = 40                   # knurl diamonds around the circumference (3.3 mm pitch)
THREAD_P = 0.00125             # neck thread pitch

# lugs: angle (from +X counter-clockwise), hole centre (rc, zc), rounding radius rl, hole rh,
# half-thickness hw (along the tangent), the bottom goes into the body down to rb
LUG_BODY = dict(a=-35.0, rc=0.0229, zc=0.0567, rl=0.0026, rh=0.0009, hw=0.0013, rb=R_BODY - 0.0007)
LUG_CAP = dict(a=-57.0, rc=0.0239, zc=0.0684, rl=0.0026, rh=0.0009, hw=0.0013, rb=R_CAP - 0.0007)
# seal: a lead lens D 9 x 3.2 hangs on the wire next to the ring tag (left of the body lug: the wire
# enters its hole in a smooth arc)
SEAL = dict(a=-52.0, z=0.0400, r=0.0045, t=0.0032)
WIRE_R = 0.00045
CHANNEL = 0.0009               # wire channels in the seal - tangent, offset from the centre

# sides around the circumference: body and ring 20 (straight profile, the facets do not show from the
# side), cap 28
LOD_SPECS = [
    dict(lod=0, body=20, cap=28, seal=14, wire=4),
    dict(lod=1, body=14, cap=16, seal=8, wire=3),
]

REGIONS = {
    "lead": ("lead", 1.0), "thread": ("thread", 1.6), "knurl": ("knurl", 1.6), "cap_top": ("cap_top", 1.6),
    "band": ("band", 1.6), "seal": ("seal", 1.6), "wire": ("wire", 0.8),
}


def wdecal(name):
    return os.path.join(WORK, name)


# trefoils on the ring: front, right, back, left (the lugs and the seal sit between front and right, the
# lock between front and left)
ZB = (Z_BAND0 + Z_BAND1) / 2
SKIN = (R_BAND - 0.0012, R_BAND + 0.0012)
TREFOILS = [
    (wdecal("decal_trefoil.png"), "y", -1, ("x", "z"), (0.0, ZB), (TREFOIL_D, TREFOIL_D), (-SKIN[1], -SKIN[0])),
    (wdecal("decal_trefoil.png"), "x", 1, ("y", "z"), (0.0, ZB), (TREFOIL_D, TREFOIL_D), SKIN),
    (wdecal("decal_trefoil.png"), "y", 1, ("x", "z"), (0.0, ZB), (TREFOIL_D, TREFOIL_D), SKIN),
    (wdecal("decal_trefoil.png"), "x", -1, ("y", "z"), (0.0, ZB), (TREFOIL_D, TREFOIL_D), (-SKIN[1], -SKIN[0])),
]

LEAD = kmats.lin((92, 95, 101))
LEAD_DARK = kmats.lin((64, 67, 72))
OXIDE = kmats.lin((170, 172, 166))
BRIGHT = kmats.lin((160, 164, 172))      # fresh cut lead in a scratch
POLISH = kmats.lin((126, 130, 138))      # rubbed by hands
YELLOW = kmats.lin((222, 176, 34))
SOOT = kmats.lin((34, 31, 27))           # dirt in crevices and knurling


def radial(a_deg):
    """Local axes at angle a: u is tangent (counter-clockwise), v is up, n is outward."""
    a = math.radians(a_deg)
    return g.Frame((0, 0, 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1), (math.cos(a), math.sin(a), 0))


def cyl_pt(a_deg, r, z):
    a = math.radians(a_deg)
    return (r * math.cos(a), r * math.sin(a), z)


def seal_center():
    """Seal centre: the back of the lens rests on the ring tag."""
    return Vector(cyl_pt(SEAL["a"], R_BAND + 0.0001 + SEAL["t"] / 2, SEAL["z"]))


# --- materials: pattern at the scale of the item (edges per 4 cm, not per metre as on stations) -----
def small(t, origin, seed, k=25.0):
    vec, sep = t.coords(origin, seed)
    return t.stretch(vec, k, k, k), sep


def tri(t, x):
    """Sawtooth 0..1 -> triangle: 0 at the edges, 1 in the middle."""
    return t.math("SUBTRACT", 1.0, t.math("MULTIPLY", t.math("ABSOLUTE", t.math("SUBTRACT", x, 0.5)), 2.0))


def vmath(t, op, a, b):
    """Vector operation: a, b are sockets or tuples (constants)."""
    n = t.node("ShaderNodeVectorMath")
    n.operation = op
    for i, x in enumerate((a, b)):
        if isinstance(x, tuple):
            n.inputs[i].default_value = x
        else:
            t.link(x, n.inputs[i])
    return n.outputs["Value" if op in ("DOT_PRODUCT", "LENGTH", "DISTANCE") else "Vector"]


def scratches(t, vec, amount=1.0):
    """Thin scratches: isolines of stretched noise in two directions, masked by sparse fields."""
    out = None
    for st, sc, ms in (((1.0, 1.0, 0.22), 2.6, 1.4), ((0.25, 0.25, 1.0), 2.1, 2.4)):
        n = t.noise(t.stretch(vec, *st), sc, 2.0, 0.5)
        line = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", n, 0.5)), 0.0, 0.007, 1.0, 0.0)
        mask = t.maprange(t.noise(vec, ms, 3.0, 0.5), 0.56, 0.70, 0.0, 1.0)
        s = t.math("MULTIPLY", line, mask)
        out = s if out is None else t.math("MAXIMUM", out, s)
    return t.math("MULTIPLY", out, amount)


def item_layers(t, col, dirt, vec, nsep, grime=0.5):
    """'dayz' profile layers (like kmats.dayz_layers) at the scale of a 4 x 9 cm item: muted colour
    (patina), tone blotches, dirt streaks on the sides, greasy finger marks. The strengths come from
    kmats.LOOK, the pattern size is fitted to the item (stations use per-metre sizes). Nothing outside
    the 'dayz' profile.
    """
    k = kmats.LOOK
    if k["name"] != "dayz":
        return col, dirt
    d, v = k["patina"]
    gray = t.node("ShaderNodeRGBToBW")
    t.link(col, gray.inputs[0])
    col = t.mixc(d, col, gray.outputs[0])
    col = t.mixc(1.0 - v, col, (0, 0, 0, 1))
    n1 = t.maprange(t.noise(vec, 0.9, 5.0, 0.6), 0.3, 0.7, 0.0, 1.0)
    col = t.mixc(n1, t.mixc(k["mottle"], col, (0, 0, 0, 1)), t.mixc(k["mottle"] * 0.4, col, (1, 1, 1, 1)))
    vert = t.maprange(t.math("ABSOLUTE", nsep.outputs["Z"]), 0.35, 0.6, 1.0, 0.0)
    st = t.step(t.noise(t.stretch(vec, 1.0, 1.0, 0.12), 8.0, 6.0, 0.6), 0.58, 0.68)
    st = t.math("MULTIPLY", t.math("MULTIPLY", st, vert), k["streaks"] * min(1.0, 0.4 + grime))
    col = t.mixc(st, col, kmats.GRIME)
    sm = t.math("MULTIPLY", t.step(t.noise(vec, 2.2, 4.0, 0.5), 0.64, 0.74), k["smudge"])
    col = t.mixc(sm, col, kmats.lin((40, 36, 30)))
    return col, t.math("MAXIMUM", dirt, t.math("MAXIMUM", st, sm))


def mat_lead(mat, origin, seed=1.0, tone=1.0, knurl=False, thread=False, stamp=False, seal=False,
             scratch=1.0, dings=1.0):
    """Cast lead: dull grey-bluish, whitish oxide in patches, specks and a film in recesses, scratches
    down to bright metal, small dents (lead is soft), edges rubbed by hands, dirt in crevices and at the
    bottom. knurl - diamond knurling (relief, tops rubbed, dirt in the grooves), thread - screw thread,
    stamp - digits stamped on the cap end, seal - the sealer imprint on the seal (a ring and rays, no
    letters).
    """
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    base = tuple(min(1.0, c * tone) for c in LEAD[:3]) + (1,)
    dark = tuple(min(1.0, c * tone) for c in LEAD_DARK[:3]) + (1,)
    col = t.mixc(t.maprange(t.noise(vec, 1.2, 6.0, 0.6), 0.3, 0.75, 0.0, 1.0), dark, base)
    # cast crust: fine tone ripple; dark greasy blotches (hands, oil)
    col = t.mixc(t.math("MULTIPLY", t.maprange(t.noise(vec, 14.0, 3.0, 0.6), 0.35, 0.65, 0.0, 1.0), 0.22), col, dark)
    tar = t.maprange(t.noise(vec, 0.6, 4.0, 0.5), 0.52, 0.72, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", tar, 0.70), col, tuple(c * 0.72 for c in dark[:3]) + (1,))
    # whitish oxide: in patches (powdery - ragged by fine noise), specks and a film in recesses
    cav = t.maprange(t.cavity(0.004), 0.10, 0.50, 0.0, 1.0)
    blot = t.maprange(t.noise(vec, 0.9, 6.0, 0.6), 0.54, 0.76, 0.0, 1.0)
    blot = t.math("MULTIPLY", blot, t.maprange(t.noise(vec, 25.0, 3.0, 0.6), 0.38, 0.68, 0.25, 1.0))
    speck = t.maprange(t.noise(vec, 9.0, 4.0, 0.6), 0.64, 0.80, 0.0, 1.0)
    ox = t.math("MINIMUM", t.math("ADD", t.math("ADD", t.math("MULTIPLY", blot, 0.38), t.math("MULTIPLY", speck, 0.45)),
                                  t.math("MULTIPLY", cav, 0.40)), 0.80)
    col = t.mixc(ox, col, OXIDE)
    # dents: sparse blotches are pressed in, slightly lighter at the edge (the metal is displaced)
    ding = t.math("MULTIPLY", t.step(t.noise(vec, 3.4, 2.0, 0.5), 0.70, 0.78), dings)
    scr = scratches(t, vec, scratch)
    col = t.mixc(t.math("MULTIPLY", scr, 0.8), col, BRIGHT)
    edge = t.maprange(t.edge_wear(0.0010), 0.05, 0.30, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.6), col, POLISH)
    h = t.math("SUBTRACT", t.math("MULTIPLY", scr, -0.25), t.math("MULTIPLY", ding, 0.30))
    gl_extra = 0.0
    groove = None
    if knurl:
        # diamonds: two helical families of grooves at 45 degrees, N_KNURL diamonds around the
        # circumference
        pitch = 2 * math.pi * R_CAP / N_KNURL
        th = t.math("ARCTAN2", sep.outputs["Y"], sep.outputs["X"])
        u = t.math("MULTIPLY", th, N_KNURL / (2 * math.pi))
        w = t.math("DIVIDE", sep.outputs["Z"], pitch)
        d1 = tri(t, t.math("FRACT", t.math("ADD", u, w)))
        d2 = tri(t, t.math("FRACT", t.math("SUBTRACT", u, w)))
        top = t.maprange(t.math("MINIMUM", d1, d2), 0.0, 0.42, 0.0, 1.0)
        groove = t.math("SUBTRACT", 1.0, top)
        col = t.mixc(t.math("MULTIPLY", top, 0.40), col, POLISH)
        h = t.math("ADD", h, t.math("MULTIPLY", top, 0.55))
        gl_extra = t.math("MULTIPLY", top, 0.12)
    if thread:
        # single-start thread: the turn rises one pitch per revolution
        th = t.math("ARCTAN2", sep.outputs["Y"], sep.outputs["X"])
        ph = t.math("ADD", t.math("DIVIDE", sep.outputs["Z"], THREAD_P), t.math("DIVIDE", th, 2 * math.pi))
        ridge = tri(t, t.math("FRACT", ph))
        groove = t.maprange(ridge, 0.0, 0.5, 1.0, 0.0)
        h = t.math("ADD", h, t.math("MULTIPLY", ridge, 0.4))
    if stamp:
        c, a = t.image(wdecal("decal_stamp.png"), sep.outputs["X"], sep.outputs["Y"], (0.0, 0.0), (STAMP_D, STAMP_D))
        m = t.math("MULTIPLY", a, t.facing(nsep, "Z", 1, 0.5))
        col = t.mixc(t.math("MULTIPLY", m, 0.55), col, SOOT)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", m, 0.5))
    if seal:
        # sealer imprint on both sides of the lens: a ring at the edge and six rays from the middle
        a = math.radians(SEAL["a"])
        ax, uu = (math.cos(a), math.sin(a), 0.0), (-math.sin(a), math.cos(a), 0.0)
        d = vmath(t, "SUBTRACT", pos, tuple(seal_center()))
        du, dv = vmath(t, "DOT_PRODUCT", d, uu), vmath(t, "DOT_PRODUCT", d, (0.0, 0.0, 1.0))
        rr = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", du, du), t.math("MULTIPLY", dv, dv)))
        ring = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", rr, 0.0029)), 0.00012, 0.00030, 1.0, 0.0)
        ang = t.math("ARCTAN2", dv, du)
        ray = t.maprange(tri(t, t.math("FRACT", t.math("MULTIPLY", ang, 6 / (2 * math.pi)))), 0.80, 0.92, 0.0, 1.0)
        ray = t.math("MULTIPLY", ray, t.math("MULTIPLY", t.maprange(rr, 0.0006, 0.0009, 0.0, 1.0),
                                             t.maprange(rr, 0.0021, 0.0024, 1.0, 0.0)))
        nax = t.math("ADD", t.math("MULTIPLY", nsep.outputs["X"], ax[0]), t.math("MULTIPLY", nsep.outputs["Y"], ax[1]))
        on_face = t.maprange(t.math("ABSOLUTE", nax), 0.75, 0.9, 0.0, 1.0)
        m = t.math("MULTIPLY", t.math("MAXIMUM", ring, ray), on_face)
        col = t.mixc(t.math("MULTIPLY", m, 0.45), col, LEAD_DARK)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", m, 0.45))
    if groove is not None:
        col = t.mixc(t.math("MULTIPLY", groove, 0.50), col, SOOT)
    gr = t.maprange(t.cavity(0.007), 0.12, 0.55, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", gr, 0.70), col, kmats.GRIME)
    # bottom: dirt from the table and floor (up to ~14 mm above the bottom), ragged edge
    low = t.maprange(t.math("ADD", sep.outputs["Z"], t.math("MULTIPLY", t.noise(vec, 3.0, 4.0, 0.6), 0.005)),
                     0.002, 0.016, 1.0, 0.0)
    col = t.mixc(t.math("MULTIPLY", low, t.maprange(t.noise(vec, 4.0, 4.0, 0.6), 0.3, 0.7, 0.55, 0.90)), col, kmats.GRIME)
    up = t.maprange(nsep.outputs["Z"], 0.4, 0.9, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", up, t.noise(vec, 3.0, 4.0, 0.6)), 0.30), col, kmats.DUST)
    col, dirt = item_layers(t, col, t.math("MAXIMUM", gr, t.math("MULTIPLY", low, 0.6)), vec, nsep)
    gl = t.math("ADD", 0.28, t.math("ADD", t.math("MULTIPLY", scr, 0.25), t.math("MULTIPLY", edge, 0.20)))
    gl = t.math("SUBTRACT", gl, t.math("ADD", t.math("MULTIPLY", ox, 0.15), t.math("MULTIPLY", dirt, 0.12)))
    if not isinstance(gl_extra, float):
        gl = t.math("ADD", gl, gl_extra)
    sp = t.math("ADD", 0.30, t.math("ADD", t.math("MULTIPLY", scr, 0.35), t.math("MULTIPLY", edge, 0.30)))
    sp = t.math("SUBTRACT", sp, t.math("ADD", t.math("MULTIPLY", ox, 0.15), t.math("MULTIPLY", dirt, 0.15)))
    return kmats.out(t, col, gl, sp, h)


def mat_band(mat, origin):
    """Yellow ring tag (painted aluminium) over the body: the paint has faded in patches, chips down to
    metal at the edges and the lock, scratches, dirt at the edges and in the lock, trefoils.
    """
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, 6.1)
    nsep = t.normal()
    col = t.mixc(t.maprange(t.noise(vec, 1.5, 6.0, 0.6), 0.3, 0.75, 0.0, 1.0),
                 tuple(c * 0.84 for c in YELLOW[:3]) + (1,), YELLOW)
    col = t.mixc(t.math("MULTIPLY", t.maprange(t.noise(vec, 0.7, 4.0, 0.5), 0.4, 0.7, 0.0, 1.0), 0.35), col,
                 kmats.lin((210, 192, 118)))
    col = kmats.decals(t, col, sep, nsep, TREFOILS)
    # paint rubbed by fingers down to a thin layer (lighter and greyer) - also over the trefoils
    rub = t.maprange(t.noise(vec, 2.5, 5.0, 0.6), 0.56, 0.74, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", rub, 0.55), col, kmats.lin((176, 166, 124)))
    z = sep.outputs["Z"]
    # the ring is dirtier at the bottom: dust and dirt from the table
    low = t.maprange(t.math("ADD", z, t.math("MULTIPLY", t.noise(vec, 3.0, 4.0, 0.6), 0.004)), Z_BAND0 + 0.001,
                     Z_BAND0 + 0.010, 1.0, 0.0)
    col = t.mixc(t.math("MULTIPLY", low, 0.40), col, kmats.GRIME)
    inside = t.math("MULTIPLY", t.maprange(z, Z_BAND0, Z_BAND0 + 0.0009, 0.0, 1.0),
                    t.maprange(z, Z_BAND1 - 0.0009, Z_BAND1, 1.0, 0.0))
    near = t.math("MAXIMUM", t.maprange(z, Z_BAND0, Z_BAND0 + 0.003, 1.0, 0.0),
                  t.maprange(z, Z_BAND1 - 0.003, Z_BAND1, 0.0, 1.0))
    edge = t.maprange(t.edge_wear(0.0008), 0.05, 0.30, 0.0, 1.0)
    chips = t.step(t.math("ADD", t.math("ADD", t.math("MULTIPLY", t.noise(vec, 6.0, 6.0, 0.6), 0.8),
                                        t.math("MULTIPLY", near, 0.40)), t.math("MULTIPLY", edge, 0.35)), 0.80, 0.84)
    col = t.mixc(chips, col, kmats.lin((150, 152, 156)))
    scr = scratches(t, vec, 0.8)
    col = t.mixc(t.math("MULTIPLY", scr, 0.6), col, kmats.lin((236, 222, 170)))
    col = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", 1.0, inside), 0.65), col, kmats.GRIME)
    gr = t.maprange(t.cavity(0.004), 0.15, 0.6, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", gr, 0.55), col, kmats.GRIME)
    up = t.maprange(nsep.outputs["Z"], 0.4, 0.9, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", up, 0.25), col, kmats.DUST)
    col, dirt = item_layers(t, col, gr, vec, nsep, grime=0.4)
    h = t.math("SUBTRACT", t.math("MULTIPLY", inside, 0.35), t.math("ADD", t.math("MULTIPLY", chips, 0.35),
                                                                       t.math("MULTIPLY", scr, 0.15)))
    gl = t.math("SUBTRACT", 0.40, t.math("ADD", t.math("MULTIPLY", chips, 0.15), t.math("MULTIPLY", dirt, 0.15)))
    # a chip is bare aluminium: slightly glossier than the paint
    sp = t.math("ADD", t.math("SUBTRACT", 0.28, t.math("MULTIPLY", dirt, 0.10)), t.math("MULTIPLY", chips, 0.20))
    return kmats.out(t, col, gl, sp, h)


KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "lead": (mat_lead, dict(seed=1.0)),
    "knurl": (mat_lead, dict(seed=2.3, knurl=True, scratch=0.6, dings=0.4)),
    "thread": (mat_lead, dict(seed=3.1, thread=True, scratch=0.4, dings=0.0)),
    "cap_top": (mat_lead, dict(seed=4.7, stamp=True, scratch=0.35)),
    "seal": (mat_lead, dict(seed=7.9, tone=1.18, seal=True, scratch=0.5, dings=0.5)),
    "band": (mat_band, {}),
    # steel sealing wire: dull, dirty
    "wire": ("steel", dict(seed=8.4, tone=0.26, along="z", gloss=0.40, spec=0.50, dust=0.05, grime=0.45)),
})

OBJ, NAME = "m48_anomaly_sample", "ozr_anomaly_sample"
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=512, look="dayz")
P = M.part
BOUNDS = {}


# --- primitives missing from kgeo ----------------------------------------------------------------
def face(part, verts, want):
    """Face from bmesh vertices, oriented towards want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def arc(cx, cz, rad, a0, a1, k):
    """k + 1 points of an arc in the profile plane (r, z): centre (cx, cz), angles a0 -> a1 (degrees
    from +r towards +z).
    """
    return [(cx + rad * math.cos(math.radians(a0 + (a1 - a0) * i / k)),
             cz + rad * math.sin(math.radians(a0 + (a1 - a0) * i / k))) for i in range(k + 1)]


def lathe(p, prof, n, a0=0.0):
    """Body of revolution about Z: prof is [(r, z, region of the segment up to the next point)] from
    bottom to top, r = 0 is a point on the axis (fan). Faces look outward when the profile runs from the
    bottom over the side to the top.
    """
    bm = p.bm
    rings = []
    for r, z, _ in prof:
        if r < 1e-9:
            rings.append([bm.verts.new((0.0, 0.0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(a0 + 2 * math.pi * k / n), r * math.sin(a0 + 2 * math.pi * k / n), z))
                          for k in range(n)])
    for i in range(len(prof) - 1):
        reg = prof[i][2]
        p.use(reg, *REGIONS[reg])
        A, B = rings[i], rings[i + 1]
        faces = []
        for k in range(n):
            k1 = (k + 1) % n
            if len(A) == 1:
                faces.append(bm.faces.new([A[0], B[k1], B[k]]))
            elif len(B) == 1:
                faces.append(bm.faces.new([A[k], A[k1], B[0]]))
            else:
                faces.append(bm.faces.new([A[k], A[k1], B[k1], B[k]]))
        p.tag(faces)
    bm.normal_update()


def lathe_axis(p, prof, n, c, e1, e2, ax):
    """Body of revolution about axis ax through point c (e1, e2, ax form a right-handed triple): prof is
    [(r, h)] from the 'bottom' to the 'top', r = 0 is a point on the axis. Faces look outward by the
    same rule as in lathe.
    """
    bm = p.bm
    rings = []
    for r, hh in prof:
        if r < 1e-9:
            rings.append([bm.verts.new(c + ax * hh)])
        else:
            rings.append([bm.verts.new(c + ax * hh + (e1 * math.cos(2 * math.pi * k / n) + e2 * math.sin(2 * math.pi * k / n)) * r)
                          for k in range(n)])
    faces = []
    for i in range(len(prof) - 1):
        A, B = rings[i], rings[i + 1]
        for k in range(n):
            k1 = (k + 1) % n
            if len(A) == 1:
                faces.append(bm.faces.new([A[0], B[k1], B[k]]))
            elif len(B) == 1:
                faces.append(bm.faces.new([A[k], A[k1], B[0]]))
            else:
                faces.append(bm.faces.new([A[k], A[k1], B[k1], B[k]]))
    p.tag(faces)
    bm.normal_update()


def catmull(pts, k):
    """Centripetal Catmull-Rom spline through pts (no loops or overshoots on uneven point spacing): k
    points per span.
    """
    v = [Vector(q) for q in pts]
    ext = [2 * v[0] - v[1]] + v + [2 * v[-1] - v[-2]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        t0 = 0.0
        t1 = t0 + max((p1 - p0).length, 1e-9) ** 0.5
        t2 = t1 + max((p2 - p1).length, 1e-9) ** 0.5
        t3 = t2 + max((p3 - p2).length, 1e-9) ** 0.5
        for j in range(k):
            s = t1 + (t2 - t1) * j / k
            a1 = (t1 - s) / (t1 - t0) * p0 + (s - t0) / (t1 - t0) * p1
            a2 = (t2 - s) / (t2 - t1) * p1 + (s - t1) / (t2 - t1) * p2
            a3 = (t3 - s) / (t3 - t2) * p2 + (s - t2) / (t3 - t2) * p3
            b1 = (t2 - s) / (t2 - t0) * a1 + (s - t0) / (t2 - t0) * a2
            b2 = (t3 - s) / (t3 - t1) * a2 + (s - t1) / (t3 - t1) * a3
            out.append((t2 - s) / (t2 - t1) * b1 + (s - t1) / (t2 - t1) * b2)
    out.append(v[-1])
    return out


def thin(pts, deg, step):
    """Thinning of a dense curve: a point stays where deg degrees of turn or a length of step has
    accumulated.
    """
    keep, ang, ln = [pts[0]], 0.0, 0.0
    for i in range(1, len(pts) - 1):
        d0, d1 = pts[i] - pts[i - 1], pts[i + 1] - pts[i]
        ln += d0.length
        if d0.length > 1e-9 and d1.length > 1e-9:
            ang += d0.angle(d1)
        if ang >= math.radians(deg) or ln >= step:
            keep.append(pts[i])
            ang, ln = 0.0, 0.0
    keep.append(pts[-1])
    return keep


def pipe_rmf(part, pts, r, sides):
    """Round rod along a curve with parallel transport of the section frame (rotation-minimizing frame):
    the frame rotates with the tangent, so the section does not twist and the rod is not twisted - even
    where the curve runs vertically (kgeo.tube_var re-derives the frame there).
    """
    bm = part.bm
    pts = [Vector(q) for q in pts]
    n = len(pts)
    tans = []
    for i in range(n):
        if i == 0:
            tv = pts[1] - pts[0]
        elif i == n - 1:
            tv = pts[-1] - pts[-2]
        else:
            tv = (pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized()
        tans.append(tv.normalized())
    ref = Vector((0, 0, 1)) if abs(tans[0].z) < 0.9 else Vector((1, 0, 0))
    a = (ref - tans[0] * ref.dot(tans[0])).normalized()
    rings = []
    for i in range(n):
        if i > 0:
            a = tans[i - 1].rotation_difference(tans[i]) @ a
            a = (a - tans[i] * a.dot(tans[i])).normalized()
        b = tans[i].cross(a).normalized()
        rings.append([bm.verts.new(pts[i] + (a * math.cos(2 * math.pi * k / sides) + b * math.sin(2 * math.pi * k / sides)) * r)
                      for k in range(sides)])
    new = []
    for i in range(n - 1):
        for k in range(sides):
            j = (k + 1) % sides
            new.append(bm.faces.new([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]))
    new.append(bm.faces.new(rings[0][::-1]))
    new.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


# --- geometry ------------------------------------------------------------------------------------
def build_body(spec):
    """Cast body: rounded bottom, straight side, the shoulder rounds straight into the threaded neck."""
    lod, n = spec["lod"], spec["body"]
    ft = R_BODY - R_NECK
    if lod == 0:
        prof = [(0.0, 0.0, "lead")]
        prof += [(r, z, "lead") for r, z in arc(R_BODY - FIL_BOT, FIL_BOT, FIL_BOT, -90.0, 0.0, 2)]
        prof += [(r, z, "lead") for r, z in arc(R_NECK, Z_SHOULDER - ft, ft, 0.0, 90.0, 2)[:-1]]
    else:
        prof = [(0.0, 0.0, "lead"), (R_BODY - 0.0010, 0.0, "lead"), (R_BODY, 0.0010, "lead"),
                (R_BODY, Z_SHOULDER - 0.0009, "lead")]
    prof += [(R_NECK, Z_SHOULDER, "thread"), (R_NECK, Z_CAP0 + 0.001, None)]
    body = P("body", "lead")
    lathe(body, prof, n, a0=math.pi / n)
    return [body]


def build_band(spec):
    """Ring tag: a 20 mm band over the body (0.7 mm), chamfered edges; the lock is a folded seam - the
    bent-back end lies on top (near LOD only).
    """
    lod, n = spec["lod"], spec["body"]
    band = P("band", "band")
    prof = [(R_BODY, Z_BAND0, "band"), (R_BAND, Z_BAND0 + BAND_CH, "band"), (R_BAND, Z_BAND1 - BAND_CH, "band"),
            (R_BODY, Z_BAND1, None)]
    lathe(band, prof, n, a0=math.pi / n)
    if lod == 0:
        g.box(band, -SEAM_W / 2, SEAM_W / 2, Z_BAND0 + BAND_CH, Z_BAND1 - BAND_CH, R_BAND - 0.0003, R_BAND + 0.00035,
              frame=radial(SEAM_A))
    return [band]


def build_cap(spec):
    """Cap: an annular end with a chamfer at the bottom, the side (knurling is in the texture), the top
    rounded R 2.
    """
    lod, n = spec["lod"], spec["cap"]
    if lod == 0:
        prof = [(R_NECK, Z_CAP0, "lead"), (R_CAP - CH_CAP, Z_CAP0, "lead"), (R_CAP, Z_CAP0 + CH_CAP, "lead"),
                (R_CAP, Z_KNURL0, "knurl"), (R_CAP, Z_KNURL1, "lead")]
        top = arc(R_CAP - FIL_TOP, Z_TOP - FIL_TOP, FIL_TOP, 0.0, 90.0, 3)
        prof += [(r, z, "lead") for r, z in top[:-1]] + [(top[-1][0], top[-1][1], "cap_top")]
    else:
        prof = [(R_NECK, Z_CAP0, "lead"), (R_CAP, Z_CAP0, "lead"), (R_CAP, Z_KNURL0, "knurl"), (R_CAP, Z_KNURL1, "lead"),
                (R_CAP, Z_TOP - FIL_TOP, "lead"), (R_CAP - FIL_TOP, Z_TOP, "cap_top")]
    prof.append((0.0, Z_TOP, None))
    cap = P("cap", "lead")
    lathe(cap, prof, n, a0=math.pi / n)
    return [cap]


# angles along the lug outline from 'outward' to 'up': the half circle of the end and three points of
# the bottom inside the body
LUG_PHI = (-90, -60, -30, 0, 30, 60, 90, 135, 180, 225)


def lug(name, d, lod):
    """Cast lug: a plate along the radius, 2 hw thick, with a semicircular outer end (rl) and a through
    hole rh for the wire; the bottom goes into the body down to rb. Mid LOD is a solid plate.
    """
    p = P(name, "lead")
    fr = radial(d["a"])
    zc, rc, rl, rh, hw, rb = d["zc"], d["rc"], d["rl"], d["rh"], d["hw"], d["rb"]
    if lod:
        k = 5
        arc_ = [(zc + rl * math.sin(math.radians(-90 + 180 * i / (k - 1))),
                 rc + rl * math.cos(math.radians(-90 + 180 * i / (k - 1)))) for i in range(k)]
        poly = [(zc - rl, rb)] + arc_ + [(zc + rl, rb)]
        g.prism(p, poly, (1, 2), -hw, hw, frame=fr)
        return p

    def outer(ph):
        if ph <= 90:
            return rl * math.sin(math.radians(ph)), rc + rl * math.cos(math.radians(ph))
        return {135: (rl, rb), 180: (0.0, rb), 225: (-rl, rb)}[ph]

    def hole(ph):
        return rh * math.sin(math.radians(ph)), rc + rh * math.cos(math.radians(ph))
    bm = p.bm
    O = {s: [bm.verts.new(fr.p(s * hw, zc + outer(ph)[0], outer(ph)[1])) for ph in LUG_PHI] for s in (-1, 1)}
    H = {s: [bm.verts.new(fr.p(s * hw, zc + hole(ph)[0], hole(ph)[1])) for ph in LUG_PHI] for s in (-1, 1)}
    c_hole = fr.p(0.0, zc, rc)
    faces = []
    K = len(LUG_PHI)
    for k in range(K):
        j = (k + 1) % K
        for s in (-1, 1):
            faces.append(face(p, [O[s][k], O[s][j], H[s][j], H[s][k]], fr.u * s))
        if LUG_PHI[k] not in (135, 180):          # the bottom wall is inside the body
            mid = (O[1][k].co + O[1][j].co) / 2
            want = mid - c_hole - fr.u * (mid - c_hole).dot(fr.u)
            faces.append(face(p, [O[-1][k], O[-1][j], O[1][j], O[1][k]], want))
        mid = (H[1][k].co + H[1][j].co) / 2
        want = -(mid - c_hole - fr.u * (mid - c_hole).dot(fr.u))
        faces.append(face(p, [H[-1][k], H[-1][j], H[1][j], H[1][k]], want))
    p.tag(faces)
    bm.normal_update()
    return p


def wire_path():
    """Wire axis: from the left channel of the seal up, through the body lug (counter-clockwise), a loop
    to the right and up, over the gap to the cap lug, through it (clockwise), a loop down into the right
    channel of the seal. Straight along the axis of each hole.
    """
    c0 = seal_center()
    fs = radial(SEAL["a"])

    def seal_pt(s, dz):
        return c0 + fs.u * (s * CHANNEL) + Vector((0.0, 0.0, dz))

    def lp(d, s):
        return radial(d["a"]).p(s, d["zc"], d["rc"])

    def cp(a, r, z):
        return Vector(cyl_pt(a, r, z))

    def through(d, sign):
        # five points on the hole axis: inside the lug and 0.4 mm beyond it the curve is straight, the
        # bend is outside
        return [lp(d, sign * q) for q in (-0.0034, -0.0017, 0.0, 0.0017, 0.0034)]
    b, c = LUG_BODY, LUG_CAP
    ctrl = ([seal_pt(1, 0.0020), seal_pt(1, 0.0050), cp(-49.3, 0.0226, 0.0495), cp(-47.4, 0.0228, 0.0535)] +
            through(b, 1) +
            [cp(-23.0, 0.0236, 0.0590), cp(-25.5, 0.0242, 0.0632), cp(-33.0, 0.0247, 0.0668), cp(-41.5, 0.0246, 0.0683)] +
            through(c, -1) +
            [cp(-69.0, 0.0243, 0.0660), cp(-68.5, 0.0239, 0.0615), cp(-64.0, 0.0233, 0.0555),
             cp(-59.0, 0.0228, 0.0500), cp(-56.0, 0.0226, 0.0470), seal_pt(-1, 0.0050), seal_pt(-1, 0.0020)])
    return catmull(ctrl, 12)


def build_seal(spec):
    """Seal: a lead lens D 9 on the wire, hanging by the ring tag; the wire loops through the body lug
    and the cap lug (the cap cannot be unscrewed without breaking the seal).
    """
    lod = spec["lod"]
    parts = [lug("lug_body", LUG_BODY, lod), lug("lug_cap", LUG_CAP, lod)]
    s = P("seal", "seal")
    fs = radial(SEAL["a"])
    c0 = seal_center()
    r, ht = SEAL["r"], SEAL["t"] / 2
    if lod == 0:
        prof = [(0.0, -ht), (0.62 * r, -ht * 0.93), (0.91 * r, -ht * 0.62), (r, 0.0), (0.91 * r, ht * 0.62),
                (0.62 * r, ht * 0.93), (0.0, ht)]
    else:
        prof = [(0.0, -ht), (r * 0.92, -ht * 0.7), (r * 0.92, ht * 0.7), (0.0, ht)]
    lathe_axis(s, prof, spec["seal"], c0, fs.u, fs.v, fs.n)
    parts.append(s)
    dense = wire_path()
    w = P("wire", "wire")
    # near LOD: a point per 15 degrees of turn or 3 mm (smooth along the rod: < 40 degrees)
    pipe_rmf(w, thin(dense, 15.0, 0.0030) if lod == 0 else thin(dense, 60.0, 0.012), WIRE_R, spec["wire"])
    parts.append(w)
    return parts


def build_lod(spec):
    parts = build_body(spec) + build_band(spec) + build_cap(spec) + build_seal(spec)
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """One convex octagonal prism circumscribed around the cap (D 42), from the bottom to the end; the
    lugs and the seal have no collision. The mass is the item weight in the mod, 60 g.
    """
    ro = R_CAP / math.cos(math.pi / 8)
    ring = [(ro * math.cos(2 * math.pi * (k + 0.5) / 8), ro * math.sin(2 * math.pi * (k + 0.5) / 8)) for k in range(8)]
    pts = [(x, y, z) for x, y in ring for z in (0.0, Z_TOP)]
    comps = [(pts, kx.PEN + r"\metalplate.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    memory = {
        # inventory preview camera: front-left and above (invView is where the camera is)
        "invView": [(-0.10, -0.24, 0.15)],
        "ce_center": [(0.0, 0.0, 0.045)],
        "ce_radius": [(0.03, 0.0, 0.045)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.06, memory, bbox


# the first four are the --look previews: overview, seal and lugs close-up, cap end, rear view
SHOTS = [
    ("front", (-0.10, -0.26, 0.12), (0.0, 0.0, 0.045), 60),
    ("seal", (0.115, -0.120, 0.075), (0.012, -0.014, 0.054), 75),
    ("top", (0.04, -0.12, 0.25), (0.0, 0.0, 0.085), 60),
    ("back", (0.14, 0.22, 0.10), (0.0, 0.0, 0.045), 60),
]

M.look_shots = (4, 2)
M.run(build_lod, collision, SHOTS, row_step=0.07, row_shot=((0.035, -0.20, 0.09), (0.035, 0, 0.045)))
