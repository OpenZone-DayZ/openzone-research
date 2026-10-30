"""M83 - gauge set (OZL_Tool_GaugeSet): a Ballistic line module, a portable 2x2 item. It sits in an
OZL_Tool1..3 slot of the line's packer (M23, M27, M32) and shows on its shelf or table through the
module_N proxy. A wooden box with plug gauges and bolt cartridge gauges (go/no-go) in sockets, the
lid open.

    blender --background --python build_m83.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]
                                                  [--bake-only [--geo-render | --look-render]]

Run make_decals.py (system Python) before the first build: the stamps on the insert, the group
plates, the inventory in the lid, the acceptance stamp on the front wall.

Size: about 0.20 x 0.06 x 0.12 m, light wood, 6-10 steel gauges in sockets, stamps are digits. The
module pad is about 0.2 x 0.2 m, up to about 0.25 m high.

Sample: the unified kit of troop gauges and instruments 56-I-01 (photos from the reibert.info
topic): gauges for the AK/AKM, SKS and RPD for 7.62 x 39 in a box of lacquered light wood - the
lid on two hinges opened back, a hasp on the front wall; inside an insert with milled sockets
shaped like the gauges, a round finger scoop at each socket; the gauge groups are labelled with
aluminium plates "56-I-212 / 231 / 327". Contents (auction lots and reibert.info): K-1 - firing pin
protrusion gauges (AK/SKS and RPD), K-2 - the bore gauge, K-3 / K-4 / K-5 - locking unit plug
gauges: go, no-go and reject, K-6 - extractor hook distance gauges (AK, SKS, RPD) and the PRB-1
front sight instrument. The Ericsson No. 148 box has the same layout principle: sockets across the
box, punched digits under them.

Sizes. There is no datasheet of the kit online. Reference figures are East German gauges of the
same purpose for 7.62 x 39 (a forum topic of the International Ammunition Association): a bolt gap
gauge 33.21 mm long with a head D 11.25 mm; a firing pin protrusion gauge - a 39.42 x 3 mm plate.
The 39.4 mm plate K-1 (105 pixels) gives the photo scale - ~2.66 pixels per mm in the right
column; by it (an estimate, not cross-checked):
- K-3...K-5 - cylinders ~35 x D 8.6 mm (by the photo), the model is 33.2 x D 9 mm (the length of
  the East German one) with a groove at the end; the reject gauge K-5 has a cone at the end, as in
  the photo; the no-go K-4 has a red band (the no-go side of gauges is painted red);
- K-2 - a rod ~135 mm D ~4 mm: a round tail with a head and a square part with flats;
- K-6 - rods ~54-56 mm D 6.4 mm with a neck and a collar at the end, the SKS gauge has a knurled
  body D 7;
- K-1 - plates 40 x 9 x 3 mm with V-notches at both ends;
- finger scoops D 12-15 mm, plates ~24 x 7 mm with two rivets.
The 56-I-01 box in the photo is ~0.35 m inside: it also holds the PRB-1 instrument (the biggest
item of the kit). The module is a box with gauges only (9 pieces, no PRB-1), so it is smaller:
200 x 122 mm, body 42 mm, lid 16 mm - closed 0.20 x 0.058 x 0.122 m. The lid at 105 degrees
stands behind the box, all together ~0.20 x 0.17 x 0.165 m. Plates without the letter: "56-212",
"56-231", "56-327", the set "56-01"; in the lid a paper inventory (a table in digits, a stamp with
a star and no text); the stamps "2"..."5" are punched into the wood by the sockets of the left group.

Condition (no faction colour): used but intact - the box lacquer is worn to light wood on the
edges, the insert is greasy by the scoops, dirt in the sockets; the gauges are ground steel,
slightly dull; hinges and hasp are darkened steel. Markings: digits on the plates, stamps, the
inventory; no letters.
LODs: near and mid (the mid insert has no sockets - the gauges sink into a flat board; no edge
roundings, chamfers or screws), no far one.

Details (the "dayz" look: more matte, dirtier, AO in colour; the sizes, socket layout and decals
are fixed - the stamps of make_decals.py are drawn for them):
- box and lid: edges rounded, vertical corners with a 4 mm radius; the side panels run the full
  depth, the front and back sit between them (the joint as in the photo), a gap in the joints and
  under the walls; a chamfer on the plywood bottom; nail heads on the sides at the joints;
- rounding is a tangent polygon (arc_pts): two 30-degree faces instead of one at 45 - the step is
  below the 40-degree smoothing threshold (krender, kexport), so the edge shades round without
  extra faces;
- insert: finger scoops with 16 sides instead of 10, a rounded edge; socket ends with 6 sides per
  half circle instead of 3, a chamfered edge; the insert is three boards (the joints and the board
  tone are in the material), a gap at the walls;
- gauges: 16 sides per circle (the upper 220 degrees are visible, the bottom is always in the
  socket), chamfers on the ends, grooves; the K-4 red band is a part of the body, not a ring put
  on; chamfers on the square part of K-2 and on the K-1 plates, rounded corners on the plates;
  steel from build_gauge: darker, grinding marks, light chamfers, rare oxide spots (in "dayz" the
  highlight dies out - the metal reads by them);
- card hinges: two leaves with rounded corners on two screws each, an axle, five knuckles
  (knuckle joints are in the hinge material); the hasp is a swivel strap on a screw with a hole for
  a seal (in the photo it hangs on the front wall), on the lid a plate with the same hole: the
  strap is swung up, the holes align and the seal wire goes through both;
- lacquer (build_lacquer): worn to wood on the edges, on the front edge where the box is opened,
  on the sides and underneath; the insert is greasy by the scoops; fine growth rings (kwood has a
  ~0.1 m band, invisible on a 0.2 m box); a corner of the inventory has come unstuck at the hinges.
No vanilla DayZ items: in the 0.2 m box all the room is taken by shaped sockets. No lamps, screens
or moving parts - there is no work look (the module stays as it is in the slot).

Blender axes: X is width, Y is depth (the face and the hasp at -Y, hinges at the back), Z is up.
The origin is the centre of the bounds at the base, so the module lands on the module_N proxy
point (autocenter = 0 in Geometry).
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
import kwood  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m ------------------------------------------------------------------------------
OY = -0.024                             # the box is shifted forward: the open lid stands behind it
BX0, BX1 = -0.100, 0.100
HD = 0.061
BY0, BY1 = OY - HD, OY + HD
T = 0.009                               # walls
ZB = 0.006                              # bottom (plywood)
ZR = 0.042                              # top of the walls
IX0, IX1 = BX0 + T, BX1 - T
IHY = HD - T                            # insert: +-0.052 from the middle along Y
ZI = 0.034                              # top of the insert
LR, LH = 0.011, 0.016                   # lid: edge height, full height
LID_A = math.radians(105.0)
PIV = Vector((0.0, BY1 + 0.0016, ZR + 0.0004))     # hinge axis
HINGE_X = (-0.060, 0.060)
# roundings (in the photo the box corners are clearly round, the edges worn)
RC = 0.004                              # vertical corners of the box and lid
RT = 0.0012                             # top edges of the box walls
RL = 0.0020                             # top edge of the lid panel
RF = 0.0012                             # free edge of the lid sides
GAP = 0.0005                            # gap between the insert and the walls
SEAMS = (0.0255, -0.049)                # joints of the insert boards (local y): between the rows and at the front wall
LATCH = (0.003, 0.033, 0.028)           # hasp swivel strap: bottom, top, screw axis (z)
SLOTS = (18.0, 75.0, 132.0, 40.0, 101.0, 160.0, 58.0, 7.0)    # hinge screw slots, degrees


def Y(yl):
    """Local depth (from the middle of the box) -> world."""
    return OY + yl


# gauges (x0, x1 - ends, y - the local socket axis): K-2 rod, K-3...K-5 plug gauges, K-1 plates, K-6
# rods
ROD = dict(x0=-0.083, x1=0.0515, y=0.039, r=0.0020, depth=0.0030, hw=0.0028, scoop=(0.058, 0.0068))
SHASHKA = [dict(n=3, x0=-0.084, y=0.017), dict(n=4, x0=-0.040, y=0.017), dict(n=5, x0=-0.062, y=-0.006)]
SH_L, SH_R, SH_DEPTH, SH_HW, SH_SCOOP = 0.0332, 0.0045, 0.0058, 0.0052, 0.0072
FLATS = [dict(x0=0.010, y=0.024), dict(x0=0.010, y=-0.015)]
FL_L, FL_HW, FL_T, FL_DEPTH = 0.040, 0.0045, 0.003, 0.0022
PINS = [dict(x0=0.010, y=0.011, r=0.0032, L=0.054, knurl=False), dict(x0=0.010, y=-0.002, r=0.0035, L=0.056, knurl=True),
        dict(x0=0.010, y=-0.028, r=0.0032, L=0.054, knurl=False)]
PIN_SCOOP = 0.0058
# plates: picture key, centre (x, local y), width, height
PLATES = [("01", -0.046, -0.036, 0.032, 0.0080), ("212", 0.022, -0.043, 0.024, 0.0068),
          ("231", 0.049, -0.043, 0.024, 0.0068), ("327", 0.076, -0.043, 0.024, 0.0068)]
PLATE_T = 0.0008
# inventory in the lid (closed-lid axes)
PAPER = (0.060, 0.037, 0.0004)          # half-width, half-height, thickness

# kc - faces per plan corner rounding, ke - per edge rounding (0 - sharp), arc - the visible arc of
# the gauges (degrees from +Y through the top), end / scoop - faces of the socket ends (per half
# circle) and of the scoops, pch / sch - the edge of sockets and scoops (radius, faces), hk - faces
# of the hinge axle
LOD_SPECS = [
    dict(lod=0, sides=16, arc=(-20.0, 200.0), kc=2, ke=2, end=6, scoop=16, pch=(0.0006, 1), sch=(0.0010, 2), hk=10),
    dict(lod=1, sides=8, arc=(10.0, 170.0), kc=2, ke=0, end=2, scoop=8, pch=(0.0, 0), sch=(0.0, 0), hk=6),
]

REGIONS = {
    "frame_x": ("frame_x", 1.0), "frame_y": ("frame_y", 1.0), "lid_panel": ("lid_panel", 0.7),
    "ply": ("ply", 0.4), "insert": ("insert", 1.4), "paper": ("paper", 2.5), "steel": ("steel", 2.2),
    "steel2": ("steel2", 2.2), "knurl": ("knurl", 3.0), "red": ("red", 2.0), "plate": ("plate", 4.0),
    "hinge": ("hinge", 1.2), "hasp": ("hasp", 1.5), "screw": ("screw", 1.5), "slot": ("slot", 0.3),
    "inner": ("inner", 0.05),
}


def wdecal(name):
    return os.path.join(WORK, name)


def lid_matrix():
    """Lid rotation on the hinges: the front edge goes up and back (about the X axis)."""
    return Matrix.Translation(PIV) @ Matrix.Rotation(-LID_A, 4, "X") @ Matrix.Translation(-PIV)


def at_lid(p):
    """A point of the closed lid -> where it is on the open one."""
    return tuple(lid_matrix() @ Vector(p))


def paper_face():
    """Face of the inventory on the open lid: (centre z, height along z, min y, max y)."""
    m = lid_matrix()
    z0 = ZR + LR - PAPER[2]
    pts = [m @ Vector((0.0, OY + s * PAPER[1], z0)) for s in (-1, 1)]
    zs, ys = [p.z for p in pts], [p.y for p in pts]
    return (min(zs) + max(zs)) / 2, max(zs) - min(zs), min(ys), max(ys)


INSERT_DEC = (wdecal("decal_insert.png"), "z", 1, ("x", "y"), (0.0, OY), (IX1 - IX0, 2 * IHY), (ZI - 0.0003, ZI + 0.0003))
PLATE_DECS = [(wdecal("decal_plate_%s.png" % k), "z", 1, ("x", "y"), (x, Y(y)), (w, h),
               (ZI + PLATE_T - 0.0003, ZI + PLATE_T + 0.0003)) for k, x, y, w, h in PLATES]
_PZ, _PH, _PY0, _PY1 = paper_face()
PAPER_DEC = (wdecal("decal_paper.png"), "y", -1, ("x", "z"), (0.0, _PZ), (2 * PAPER[0], _PH), (_PY0 - 0.004, _PY1 + 0.004))
FRONT_DEC = (wdecal("decal_front.png"), "y", -1, ("x", "z"), (-0.058, 0.023), (0.028, 0.015), (BY0 - 0.0008, BY0 + 0.0008))

# --- materials ----------------------------------------------------------------------------------
KNURL_PIN = PINS[1]
KNURL_C = (Y(KNURL_PIN["y"]), ZI - KNURL_PIN["r"] + 0.0020)     # knurling axis (y, z), as in build_gauges


def mat_knurl(mat, origin, seed=1.0, n=14, pitch=None):
    """Straight cross-hatch knurling on a rod along X: two helical grooves at 45 degrees around the axis
    (n starts around the circumference - the pattern closes without a seam), light ridges, dark and
    dirt in the grooves.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    r = KNURL_PIN["r"]
    pitch = pitch or 2 * math.pi * r / n
    dy = t.math("SUBTRACT", sep.outputs["Y"], KNURL_C[0])
    dz = t.math("SUBTRACT", sep.outputs["Z"], KNURL_C[1])
    phi = t.math("MULTIPLY", t.math("ARCTAN2", dz, dy), n / (2 * math.pi))
    xa = t.math("DIVIDE", sep.outputs["X"], pitch)

    def groove(u):
        q = t.math("ABSOLUTE", t.math("SUBTRACT", t.math("FRACT", u), 0.5))
        return t.maprange(q, 0.28, 0.44, 0.0, 1.0)
    gr = t.math("MAXIMUM", groove(t.math("ADD", xa, phi)), groove(t.math("SUBTRACT", xa, phi)))
    # ridge tone as on the ground steel of the gauges (GAUGE in the dayz profile)
    light = kmats.lin((124, 126, 129))
    dark = kmats.lin((30, 31, 33))
    col = t.mixc(t.maprange(t.noise(vec, 400.0, 3.0, 0.5), 0.3, 0.7, 0.0, 0.3), light, kmats.lin((98, 100, 104)))
    col = t.mixc(t.math("MULTIPLY", gr, 0.85), col, dark)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, ZI - 0.006, 0.05, 0.4, 0.4)
    gl = t.math("SUBTRACT", 0.55, t.math("MULTIPLY", gr, 0.35))
    sp = t.math("SUBTRACT", 0.7, t.math("MULTIPLY", gr, 0.5))
    return kmats.out(t, col, gl, sp, t.math("MULTIPLY", gr, -0.8))


def _tree(mat):
    """Material node tree without clearing: layers are added on top of a finished builder."""
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    return t


def _sock(mat, ref):
    return ref if isinstance(ref, (int, float)) else kmats.sock(mat, ref)


def spot(t, pos, c, r, a=0.25, b=1.0):
    """0..1 at point pos: 1 inside the ellipsoid c with semi-axes r (up to the fraction a), 0 by the
    fraction b (like rub in build_worn of M23).
    """
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
    return t.maprange(ln.outputs["Value"], a, b, 1.0, 0.0)


def build_lacquer(mat, origin, color, seed=1.0, along="x", gloss=0.30, spec=0.15, rings=0.4, knots=0.2,
                  floor_z=0.0, dust=0.22, grime=0.55, decal_items=(), bare=kmats.lin((172, 136, 96)),
                  wear=(0.70, 0.78), rub=(), grease=(), seams=(), nails=(), fine=0.22):
    """Lacquered light wood (kwood.build_wood) with lacquer wear: on the edges and where the box is picked
    up and moved (rub - [(centre, semi-axes, strength)]) the lacquer is worn to matte wood; grease -
    places greasy from fingers (darker, slightly glossy); seams - [(axis, coordinate)] board joints: a
    dark line, the boards on both sides have different tones; nails - nail heads (points on faces);
    fine - the strength of fine growth rings (kwood has a ~0.1 m band, invisible on a 0.2 m box, here
    ~4 mm).
    """
    outs = kwood.build_wood(mat, origin, color=color, seed=seed, along=along, gloss=gloss, spec=spec,
                            floor_z=floor_z, dust=dust, grime=grime, rings=rings, knots=knots,
                            decal_items=decal_items)
    t = _tree(mat)
    col, gl, sp, h = (_sock(mat, outs[k]) for k in ("color", "gloss", "spec", "height"))
    vec, sep = t.coords(origin, seed + 0.53)
    pos = sep.inputs[0].links[0].from_socket
    kk = {"x": (0.04, 1.0, 1.0), "y": (1.0, 0.04, 1.0), "z": (1.0, 1.0, 0.04)}[along]
    fvec = t.stretch(vec, *kk)
    # fine growth rings and grain - they show through the lacquer darker
    wv = t.node("ShaderNodeTexWave", Scale=220.0, Distortion=10.0, **{"Detail": 2.0, "Detail Scale": 1.0})
    wv.wave_type = "RINGS"
    t.link(fvec, wv.inputs["Vector"])
    late = t.math("MULTIPLY", t.maprange(wv.outputs["Fac"], 0.55, 1.0, 0.0, 1.0),
                  t.maprange(t.noise(vec, 5.0, 3.0, 0.5), 0.3, 0.7, 0.5, 1.0))
    col = t.mixc(t.math("MULTIPLY", late, fine), col, tuple(c * 0.70 for c in color[:3]) + (1,))
    fib = t.maprange(t.noise(fvec, 140.0, 3.0, 0.6), 0.3, 0.7, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", fib, fine * 0.35), col, tuple(c * 0.80 for c in color[:3]) + (1,))
    h = t.math("ADD", h, t.math("MULTIPLY", late, 0.05))
    # lacquer worn to wood: sharp edges and rub places, ragged (noise patches); mid-face stays
    # unworn
    edge = t.maprange(t.edge_wear(0.003), 0.05, 0.25, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 40.0, 8.0, 0.7), 0.45), t.math("MULTIPLY", edge, 0.75))
    grain = t.maprange(t.noise(fvec, 60.0, 4.0, 0.6), 0.3, 0.7, 0.5, 1.0)
    for c, r, k in rub:
        f = t.math("ADD", f, t.math("MULTIPLY", t.math("MULTIPLY", spot(t, pos, c, r), grain), k))
    worn = t.step(f, wear[0], wear[1])
    raw = t.mixc(fib, tuple(c * 0.78 for c in bare[:3]) + (1,), bare)
    raw = t.mixc(t.maprange(t.noise(vec, 9.0, 4.0, 0.5), 0.35, 0.7, 0.1, 0.55), raw, kmats.lin((88, 70, 50)))
    col = t.mixc(t.math("MULTIPLY", worn, 0.80), col, raw)
    gl = t.mixf(worn, gl, 0.08)
    sp = t.mixf(worn, sp, 0.05)
    h = t.math("SUBTRACT", h, t.math("MULTIPLY", worn, 0.12))
    for c, r, k in grease:
        gm = t.math("MULTIPLY", spot(t, pos, c, r), t.maprange(t.noise(vec, 9.0, 4.0, 0.5), 0.3, 0.7, 0.35, 1.0))
        gm = t.math("MULTIPLY", gm, k)
        col = t.mixc(gm, col, kmats.lin((70, 42, 22)))
        gl = t.math("ADD", gl, t.math("MULTIPLY", gm, 0.12))
    tones = (kmats.lin((120, 64, 30)), kmats.lin((236, 170, 96)))
    for i, (ax, v) in enumerate(seams):
        w = sep.outputs["XYZ".index(ax.upper())]
        line = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", w, v)), 0.00012, 0.00035, 1.0, 0.0)
        side = t.math("GREATER_THAN", w, v)
        col = t.mixc(t.math("MULTIPLY", side, 0.10), col, tones[i % 2])
        col = t.mixc(t.math("MULTIPLY", line, 0.8), col, kmats.lin((44, 24, 10)))
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", line, 0.4))
    for c in nails:
        nm = spot(t, pos, c, (0.0008, 0.0008, 0.0008), 0.55, 0.85)
        col = t.mixc(nm, col, kmats.lin((50, 44, 38)))
        gl = t.mixf(nm, gl, 0.30)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", nm, 0.25))
    return kmats.out(t, col, gl, sp, h)


def build_gauge(mat, origin, tone=0.24, seed=7.0, along="x", gloss=0.80, spec=0.95, floor_z=0.0, dust=0.05,
                grime=0.35):
    """Ground steel of the gauges: the tone is darker than the plain steel (it looked almost white),
    grinding marks along the axis - finer and more contrasty than kmats.build_steel, lighter chamfers
    (they get rubbed), rare dark oxide and finger spots. In the dayz profile the kit itself kills the
    highlight and gloss, so the metal reads by the marks and the light chamfers on dark.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    if kmats.LOOK["name"] == "dayz":
        tone *= kmats.LOOK["steel"]
    k = {"x": (0.02, 1.0, 1.0), "y": (1.0, 0.02, 1.0), "z": (1.0, 1.0, 0.02)}[along]
    brush = t.noise(t.stretch(vec, *k), 320.0, 4.0, 0.7)
    smudge = t.noise(vec, 6.0, 6.0, 0.6)
    edge = t.maprange(t.edge_wear(0.0008), 0.03, 0.12, 0.0, 1.0)
    v = t.math("ADD", tone, t.math("MULTIPLY", t.math("SUBTRACT", brush, 0.5), 0.18))
    v = t.math("ADD", v, t.math("MULTIPLY", t.math("SUBTRACT", smudge, 0.5), 0.10))
    v = t.math("ADD", v, t.math("MULTIPLY", edge, 0.12))
    comb = t.node("ShaderNodeCombineColor")
    for i in range(3):
        t.link(v, comb.inputs[i])
    col = t.mixc(0.15, comb.outputs[0], (0.26, 0.28, 0.31, 1))
    ox = t.math("MULTIPLY", t.step(t.noise(vec, 70.0, 6.0, 0.7), 0.64, 0.72),
                t.maprange(t.noise(vec, 9.0, 4.0, 0.5), 0.35, 0.7, 0.0, 1.0))
    col = t.mixc(t.math("MULTIPLY", ox, 0.65), col, kmats.lin((52, 44, 38)))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.45)
    gl = t.math("SUBTRACT", gloss, t.math("ADD", t.math("MULTIPLY", dirt, gloss * 0.6), t.math("MULTIPLY", ox, 0.3)))
    sp = t.math("SUBTRACT", spec, t.math("ADD", t.math("MULTIPLY", dirt, spec * 0.5), t.math("MULTIPLY", ox, 0.4)))
    h = t.math("SUBTRACT", t.math("MULTIPLY", brush, 0.06), t.math("MULTIPLY", ox, 0.1))
    return kmats.out(t, col, gl, sp, h)


def build_hinge(mat, origin, gaps=(), axis=(0.0, 0.0), rmax=0.0021, **kw):
    """Darkened hinge steel (kmats.build_steel) and the axle knuckle joints: dark rings at x from gaps -
    only at the hinge axis axis (y, z), the leaves are not touched.
    """
    outs = kmats.build_steel(mat, origin, **kw)
    t = _tree(mat)
    col, h = _sock(mat, outs["color"]), _sock(mat, outs["height"])
    _, sep = t.coords(origin, 0.0)
    dy = t.math("SUBTRACT", sep.outputs["Y"], axis[0])
    dz = t.math("SUBTRACT", sep.outputs["Z"], axis[1])
    near = t.math("LESS_THAN", t.math("ADD", t.math("MULTIPLY", dy, dy), t.math("MULTIPLY", dz, dz)), rmax * rmax)
    for xg in gaps:
        line = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", sep.outputs["X"], xg)), 0.00008, 0.0002, 1.0, 0.0)
        line = t.math("MULTIPLY", line, near)
        col = t.mixc(line, col, (0.004, 0.004, 0.004, 1))
        h = t.math("SUBTRACT", h, line)
    return kmats.out(t, col, _sock(mat, outs["gloss"]), _sock(mat, outs["spec"]), h)


# lacquer over light wood (beech, birch), reddish as the 56-I-01 in the photo (daylight by a
# window): box and lid are darker than the insert; the dayz profile mutes the colour further
FRAME = kmats.lin((172, 90, 44))
STEEL = dict(along="x", gloss=0.62, spec=0.78, floor_z=ZI - 0.006, dust=0.05, grime=0.25)
# gauges are ground steel: darker than plain steel (which looked almost white), with a highlight
GAUGE = dict(STEEL, gloss=0.80, spec=0.95, grime=0.35)
PAPERY = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.08, grime=0.2)
# lacquer wear: the front edge - it is gripped to open; the bottom - the box is moved over a table;
# the sides - held in hands; the front edge of the open lid
RUB_BOX = [((0.0, BY0, ZR), (0.050, 0.008, 0.008), 0.40),
           ((0.0, OY, 0.0), (0.14, 0.09, 0.0045), 0.40),
           ((BX0, OY, 0.024), (0.006, 0.07, 0.030), 0.20), ((BX1, OY, 0.024), (0.006, 0.07, 0.030), 0.20)]
RUB_LID = [(at_lid((0.0, BY0, ZR + 0.004)), (0.050, 0.012, 0.012), 0.40)]
GREASE_BOX = [((0.0, BY0, 0.030), (0.05, 0.006, 0.014), 0.25),
              (at_lid((0.0, BY0, ZR + 0.006)), (0.045, 0.012, 0.012), 0.30)]     # and the lid edge where it is opened
# finger scoops (x, local y): the insert around them is greasy
SCOOPS = ([(ROD["scoop"][0], ROD["y"])] + [(s["x0"] + SH_L + 0.004, s["y"]) for s in SHASHKA] +
          [(f["x0"] + FL_L + 0.003, f["y"]) for f in FLATS] + [(p["x0"] + p["L"] + 0.004, p["y"]) for p in PINS])
GREASE_INS = [((x, Y(y), ZI), (0.011, 0.011, 0.012), 0.45) for x, y in SCOOPS]
# nail heads: the sides are nailed to the front and back - two at each joint, one on the lid
NAILS = ([(x, y, z) for x in (BX0, BX1) for y in (BY0 + T / 2, BY1 - T / 2) for z in (0.017, 0.033)] +
         [at_lid((x, y, ZR + LR * 0.5)) for x in (BX0, BX1) for y in (BY0 + T / 2, BY1 - T / 2)])
# axle knuckle joints: five knuckles per 20 mm
GAPS = [hx - 0.010 + 0.004 * i for hx in HINGE_X for i in range(1, 5)]

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "frame_x": (build_lacquer, dict(color=FRAME, seed=1.3, along="x", rings=0.45, knots=0.25,
                                    decal_items=[FRONT_DEC], rub=RUB_BOX + RUB_LID, grease=GREASE_BOX)),
    "frame_y": (build_lacquer, dict(color=FRAME, seed=2.1, along="y", rings=0.45, knots=0.25,
                                    rub=RUB_BOX + RUB_LID, nails=NAILS)),
    "lid_panel": (build_lacquer, dict(color=kmats.lin((166, 88, 42)), seed=3.3, along="x", rings=0.35, knots=0.2,
                                      dust=0.20, grime=0.50, rub=RUB_LID, wear=(0.72, 0.80))),
    "ply": (build_lacquer, dict(color=kmats.lin((158, 112, 70)), seed=4.7, along="x", gloss=0.20, spec=0.10,
                                rings=0.2, knots=0.1, dust=0.15, grime=0.7, rub=RUB_BOX[1:2], wear=(0.66, 0.74),
                                fine=0.18)),
    "insert": (build_lacquer, dict(color=kmats.lin((212, 148, 68)), seed=5.9, along="x", gloss=0.26, spec=0.12,
                                   rings=0.25, knots=0.1, floor_z=ZI - 0.010, dust=0.20, grime=0.55,
                                   decal_items=[INSERT_DEC], wear=(0.74, 0.82), grease=GREASE_INS,
                                   seams=[("y", Y(s)) for s in SEAMS], fine=0.16)),
    "paper": ("paint", dict(PAPERY, color=kmats.lin((214, 200, 160)), seed=6.6, gloss=0.08, spec=0.05,
                            decal_items=[PAPER_DEC])),
    "steel": (build_gauge, dict(GAUGE, seed=7.2, tone=0.24)),
    "steel2": (build_gauge, dict(GAUGE, seed=7.8, tone=0.21)),
    "knurl": (mat_knurl, dict(seed=8.1)),
    "red": ("paint", dict(color=kmats.lin((168, 36, 28)), under=kmats.lin((150, 152, 154)), seed=8.7, gloss=0.4,
                          spec=0.3, chip=(0.74, 0.80), rust=(0.99, 1.0), rust_low=0.0, floor_z=ZI - 0.006, dust=0.05,
                          grime=0.2)),
    "plate": ("paint", dict(PAPERY, color=kmats.lin((176, 178, 176)), seed=9.3, gloss=0.45, spec=0.4,
                            decal_items=PLATE_DECS)),
    "hinge": (build_hinge, dict(STEEL, seed=9.9, tone=0.09, gloss=0.35, spec=0.4, grime=0.6, floor_z=0.0, gaps=GAPS,
                                axis=(PIV.y, PIV.z))),
    # hasp strap - light zinc plating (photo), dull in patches
    "hasp": ("steel", dict(STEEL, seed=10.4, tone=0.34, gloss=0.40, spec=0.45, grime=0.55, floor_z=0.0)),
    "screw": ("steel", dict(STEEL, seed=11.0, tone=0.16, grime=0.5, floor_z=0.0)),
    "slot": ("flat", dict(color=kmats.lin((16, 15, 14)), gloss=0.05, spec=0.02)),
    "inner": ("flat", dict(color=kmats.lin((40, 26, 16)), gloss=0.1, spec=0.05)),
})

OBJ, NAME = "m83_gauge_set", "ozr_gauge_set"
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz")
P = M.part
BOUNDS = {}


# --- primitives missing from kgeo ---------------------------------------------------------------
def retag(part, test, region="inner"):
    """Hidden faces go to the dark "inner" region with a small scale (they need no atlas room). test(face)."""
    part.bm.normal_update()
    idx = part.region_index(region, *M.regions[region])
    for f in part.bm.faces:
        if f.is_valid and test(f):
            f[part.reg] = idx


def facing(axis, sign, thr=0.99):
    return lambda f: f.normal[axis] * sign > thr


def face(part, verts, want):
    """A face from bmesh vertices, turned toward `want`."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def arc_pts(k):
    """Rounding of a right angle with a tangent polygon of k faces: (cos, sin) of k + 1 vertices, already
    multiplied by 1 / cos(half step). The normal step between neighbouring faces is 90 / (k + 1)
    degrees: for k = 2 it is 30, below the 40-degree smoothing threshold (krender.place_look,
    kexport.visual_lod), so the edge shades round; for k = 1 it is one 45-degree chamfer, sharp (it
    catches the light like a milled edge).
    """
    s = math.pi / 2 / (k + 1)
    R = 1.0 / math.cos(s / 2)
    return [(R * math.cos(s * (j + 0.5)), R * math.sin(s * (j + 0.5))) for j in range(k + 1)]


def rrect(x0, x1, y0, y1, r=(0.0, 0.0, 0.0, 0.0), k=2):
    """Rectangle outline counter-clockwise; the corners (x0 y0, x1 y0, x1 y1, x0 y1) with radii r are
    rounded by a tangent polygon of k faces (arc_pts); radius 0 or k = 0 is a sharp corner.
    """
    out = []
    for (px, py), (sx, sy), a0, rr in zip(((x0, y0), (x1, y0), (x1, y1), (x0, y1)),
                                          ((1, 1), (-1, 1), (-1, -1), (1, -1)), (180.0, 270.0, 0.0, 90.0), r):
        if rr <= 0 or k <= 0:
            out.append((px, py))
            continue
        cx, cy = px + sx * rr, py + sy * rr
        ca, sa = math.cos(math.radians(a0)), math.sin(math.radians(a0))
        for c, s in arc_pts(k):
            out.append((cx + rr * (c * ca - s * sa), cy + rr * (c * sa + s * ca)))
    return out


def circle(xc, yc, r, n):
    return [(xc + r * math.cos(2 * math.pi * k / n), yc + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def stadium(xa, xb, yc, hw, n):
    """Socket outline: a rectangle with semicircular ends (xa, xb are the end points), counter-clockwise;
    n is the face count per half circle.
    """
    pts = []
    for i in range(n + 1):
        a = -math.pi / 2 + math.pi * i / n
        pts.append((xb - hw + hw * math.cos(a), yc + hw * math.sin(a)))
    for i in range(n + 1):
        a = math.pi / 2 + math.pi * i / n
        pts.append((xa + hw + hw * math.cos(a), yc + hw * math.sin(a)))
    return pts


def inset(pts, d):
    """Counter-clockwise outline moved inward by d (outward for d < 0): vertices go along the bisector."""
    n = len(pts)
    out = []
    for i in range(n):
        ax, ay = pts[i - 1]
        bx, by = pts[i]
        cx, cy = pts[(i + 1) % n]
        l1, l2 = math.hypot(bx - ax, by - ay), math.hypot(cx - bx, cy - by)
        n1 = (-(by - ay) / l1, (bx - ax) / l1)
        n2 = (-(cy - by) / l2, (cx - bx) / l2)
        k = d / (1.0 + n1[0] * n2[0] + n1[1] * n2[1])
        out.append((bx + (n1[0] + n2[0]) * k, by + (n1[1] + n2[1]) * k))
    return out


def levels(z0, z1, bot=None, top=None):
    """Rings of the slab from the bottom up - (inward offset, height): bot / top = (radius, faces) of the
    rounding of the lower and upper edge with a tangent polygon (arc_pts), None is a sharp edge.
    """
    out = []
    if bot and bot[0] > 0 and bot[1] > 0:
        r = bot[0]
        out += [(r - r * s, z0 + r - r * c) for c, s in arc_pts(bot[1])]
    else:
        out.append((0.0, z0))
    if top and top[0] > 0 and top[1] > 0:
        r = top[0]
        out += [(r - r * c, z1 - r + r * s) for c, s in arc_pts(top[1])]
    else:
        out.append((0.0, z1))
    return out


def slab(part, pts, lv, frame=None, caps=(True, True)):
    """Slab along the outline pts (counter-clockwise in the a-b plane of the frame) - a stack of rings lv
    [(inward offset, height along c)] (levels): this rounds the edges, and the plan corners come from
    the outline (rrect). caps closes the bottom and top. The frame is right-handed (u x v = n); without
    it, world axes.
    """
    bm = part.bm
    fr = frame or g.Frame((0.0, 0.0, 0.0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    rings = [[bm.verts.new(fr.p(a, b, c)) for a, b in (inset(pts, d) if d else pts)] for d, c in lv]
    n = len(pts)
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            faces.append(bm.faces.new([r0[i], r0[j], r1[j], r1[i]]))
    if caps[0]:
        faces.append(bm.faces.new(rings[0][::-1]))
    if caps[1]:
        faces.append(bm.faces.new(rings[-1]))
    return part.tag(faces)


def lathe(part, fr, prof, n, arc=None, caps=(True, True)):
    """Solid of revolution about the axis n of the frame fr: prof [(c, r)] with increasing c; n is the face
    count per full circle; arc = (a0, a1) - only this arc, degrees from u to v (the bottom of gauges
    sunk into sockets is never visible), the ends are arc polygons. The frame is right-handed (u x v = n).
    """
    bm = part.bm
    if arc is None:
        angs, closed = [2 * math.pi * k / n for k in range(n)], True
    else:
        a0, a1 = math.radians(arc[0]), math.radians(arc[1])
        m = max(2, int(round((a1 - a0) / (2 * math.pi / n))))
        angs, closed = [a0 + (a1 - a0) * k / m for k in range(m + 1)], False
    rings = [[bm.verts.new(fr.p(r * math.cos(a), r * math.sin(a), c)) for a in angs] for c, r in prof]
    na = len(angs)
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(na if closed else na - 1):
            j = (k + 1) % na
            faces.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    for ring, sgn, use in ((rings[0], -1.0, caps[0]), (rings[-1], 1.0, caps[1])):
        if use:
            faces.append(face(part, ring, fr.n * sgn))
    return part.tag(faces)


def fx(x0, yc, zc):
    """Frame of a body along X: u is +Y, v is up (arc: 0 toward +Y, 90 is the top)."""
    return g.Frame((x0, yc, zc), (0, 1, 0), (0, 0, 1), (1, 0, 0))


def disk(part, fr, r, n, c=0.0):
    """A flat polygon of radius r facing along the axis n of the frame fr at height c."""
    vs = [part.bm.verts.new(fr.p(r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), c))
          for k in range(n)]
    return part.tag([face(part, vs, fr.n)])


def screw(head, slot, fr, r, h, n, deg, dome=False):
    """Screw: a head above the surface (frame fr, axis n outward; dome - round, otherwise countersunk) and
    a slot at angle deg - a dark stripe on the end (a 0.4 mm slot cannot be taken by the LOD, the
    colour draws it).
    """
    prof = [(0.0, r), (h * 0.35, r), (h * 0.7, r * 0.8), (h, r * 0.45)] if dome else [(0.0, r), (h, r * 0.8)]
    lathe(head, fr, prof, n, caps=(False, True))
    a = math.radians(deg)
    d, p = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
    L, w, c = prof[-1][1] * 0.92, 0.00018, h + 0.00003
    vs = [slot.bm.verts.new(fr.p(sx * L * d[0] + sy * w * p[0], sx * L * d[1] + sy * w * p[1], c))
          for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    slot.tag([face(slot, vs, fr.n)])


# --- box ----------------------------------------------------------------------------------------
def build_box(spec):
    """Plywood bottom, side panels over the full depth (their ends come out at the front and back, as in
    the photo), the front and back between them; the top edges are rounded, a chamfer at the bottom -
    a gap is visible in the joints and under the walls.
    """
    kc, ke = spec["kc"], spec["ke"]
    top = (RT, ke) if ke else None
    bt = P("bottom", "ply")
    slab(bt, rrect(BX0, BX1, BY0, BY1, (RC,) * 4, kc),
         levels(0.0, ZB, bot=(0.0008, ke) if ke else None, top=(0.0006, 1) if ke else None))
    retag(bt, facing(2, 1))
    parts = [bt]
    for nm, x0, x1, rr in (("wall_l", BX0, BX0 + T, (RC, 0.0, 0.0, RC)), ("wall_r", BX1 - T, BX1, (0.0, RC, RC, 0.0))):
        w = P(nm, "frame_y")
        slab(w, rrect(x0, x1, BY0, BY1, rr, kc), levels(ZB, ZR, top=top))
        retag(w, facing(2, -1))
        parts.append(w)
    for nm, y0, y1 in (("wall_f", BY0, BY0 + T), ("wall_b", BY1 - T, BY1)):
        w = P(nm, "frame_x")
        slab(w, rrect(BX0 + T, BX1 - T, y0, y1), levels(ZB, ZR, top=top))
        retag(w, lambda f: facing(2, -1)(f) or abs(f.normal[0]) > 0.99)
        parts.append(w)
    return parts + build_latch(spec) + build_hinges(spec, lid=False)


def build_latch(spec):
    """Hasp (photo): a swivel strap hangs on a screw on the front wall, with a hole near the bottom for a
    seal; closing the box, it is swung up onto the lid plate (build_lid).
    """
    lod, kc, ke = spec["lod"], spec["kc"], spec["ke"]
    z0, z1, zp = LATCH
    fr = g.Frame((0.0, BY0, 0.0), (1, 0, 0), (0, 0, 1), (0, -1, 0))
    pl = P("latch", "hasp")
    slab(pl, rrect(-0.005, 0.005, z0, z1, (0.0015,) * 4, kc), levels(-0.0001, 0.0011, top=(0.0004, 1) if ke else None),
         frame=fr)
    parts = [pl]
    if lod == 0:
        sc, sl, hole = P("latch_screw", "screw"), P("latch_slot", "slot"), P("latch_hole", "inner")
        screw(sc, sl, g.Frame((0.0, BY0 - 0.0011, zp), (1, 0, 0), (0, 0, 1), (0, -1, 0)), 0.0021, 0.0007, 10, 82.0,
              dome=True)
        disk(hole, g.Frame((0.0, BY0 - 0.0011, z0 + 0.0045), (1, 0, 0), (0, 0, 1), (0, -1, 0)), 0.0012, 10, 0.00003)
        parts += [sc, sl, hole]
    return parts


def build_hinges(spec, lid):
    """Card hinges (photo): a leaf on the edge of the back wall and a leaf on the lid side, two
    countersunk screws each; the axle is common, on the hinge axis PIV, with chamfers at the ends;
    five knuckles - the joints are drawn by the hinge material. lid - the lid leaves, in the
    closed-lid axes (build_lid rotates them).
    """
    lod, kc = spec["lod"], spec["kc"]
    tag = "l" if lid else "w"
    leaves = P("hinge_" + tag, "hinge")
    parts = [leaves]
    sc = sl = pins = None
    if lod == 0:
        sc, sl = P("hinge_screws_" + tag, "screw"), P("hinge_slots_" + tag, "slot")
        parts += [sc, sl]
    if not lid:
        pins = P("hinge_pins", "hinge")
        parts.append(pins)
    z0, z1 = (ZR - 0.0008, ZR + 0.0002) if lid else (ZR - 0.0002, ZR + 0.0006)
    for i, hx in enumerate(HINGE_X):
        slab(leaves, rrect(hx - 0.010, hx + 0.010, BY1 - 0.0085, BY1 + 0.0004, (0.0012, 0.0012, 0.0, 0.0), kc),
             levels(z0, z1))
        if pins is not None:
            lathe(pins, fx(hx - 0.010, PIV.y, PIV.z), [(0.0, 0.0017), (0.0200, 0.0017)], spec["hk"])
        if sc is None:
            continue
        for j, sx in enumerate((-0.0055, 0.0055)):
            deg = SLOTS[(2 * i + j + (4 if lid else 0)) % len(SLOTS)]
            if lid:
                fr = g.Frame((hx + sx, BY1 - 0.0043, z0), (1, 0, 0), (0, -1, 0), (0, 0, -1))
            else:
                fr = g.Frame((hx + sx, BY1 - 0.0043, z1), (1, 0, 0), (0, 1, 0), (0, 0, 1))
            screw(sc, sl, fr, 0.0013, 0.00025, 10, deg)
    return parts


# --- insert with sockets ------------------------------------------------------------------------
def cutter_levels(floor, cham):
    """Rings of the socket cutter: a wall from the bottom up, the insert edge is a rounding
    cham = (radius, faces) (arc_pts), the last face is extended above the insert top: the cutter ring
    does not lie in the plane of the top, so the difference cuts it cleanly; above it the cutter is
    higher than the insert.
    """
    c, k = cham
    lv = [(0.0, floor)]
    if c > 0 and k > 0:
        v = [(-c + c * cc, ZI - c + c * ss) for cc, ss in arc_pts(k)]
        (da, za), (db, zb) = v[-2], v[-1]
        t = 0.0005 / (zb - za)
        v[-1] = (db + (db - da) * t, zb + 0.0005)
        lv += v
    lv.append((lv[-1][0], ZI + 0.002))
    return lv


def pocket_cutters(spec):
    ne, ns, pch, sch = spec["end"], spec["scoop"], spec["pch"], spec["sch"]
    cuts = []

    def cut(name, pts, floor, cham):
        c = P(name, "insert")
        slab(c, pts, cutter_levels(floor, cham))
        cuts.append(c)
    yr = Y(ROD["y"])
    cut("p_rod", stadium(ROD["x0"] - 0.0015, ROD["x1"] + 0.0015, yr, ROD["hw"], ne), ZI - ROD["depth"], pch)
    cut("s_rod", circle(ROD["scoop"][0], yr, ROD["scoop"][1], ns), ZI - ROD["depth"] - 0.0025, sch)
    for s in SHASHKA:
        x1 = s["x0"] + SH_L
        cut("p_sh%d" % s["n"], stadium(s["x0"] - 0.0015, x1 + 0.0015, Y(s["y"]), SH_HW, ne), ZI - SH_DEPTH, pch)
        cut("s_sh%d" % s["n"], circle(x1 + 0.0040, Y(s["y"]), SH_SCOOP, ns), ZI - SH_DEPTH - 0.0025, sch)
    for i, f in enumerate(FLATS):
        yc = Y(f["y"])
        cut("p_fl%d" % i, [(f["x0"] - 0.0008, yc - FL_HW - 0.0006), (f["x0"] + FL_L + 0.0008, yc - FL_HW - 0.0006),
                           (f["x0"] + FL_L + 0.0008, yc + FL_HW + 0.0006), (f["x0"] - 0.0008, yc + FL_HW + 0.0006)],
            ZI - FL_DEPTH, pch)
        cut("s_fl%d" % i, circle(f["x0"] + FL_L + 0.0030, yc, PIN_SCOOP, ns), ZI - FL_DEPTH - 0.0030, sch)
    for i, p in enumerate(PINS):
        depth = 2 * p["r"] - 0.0020
        hw = p["r"] + 0.0007
        cut("p_pin%d" % i, stadium(p["x0"] - 0.0010, p["x0"] + p["L"] + 0.0010, Y(p["y"]), hw, ne), ZI - depth, pch)
        cut("s_pin%d" % i, circle(p["x0"] + p["L"] + 0.0040, Y(p["y"]), PIN_SCOOP, ns), ZI - depth - 0.0025, sch)
    return cuts


def build_insert(spec):
    """Insert: a board with sockets (near LOD) or a flat one (mid), a gap between it and the walls."""
    lod = spec["lod"]
    x0, x1, y0, y1 = IX0 + GAP, IX1 - GAP, Y(-IHY) + GAP, Y(IHY) - GAP
    ins = P("insert", "insert")
    g.box(ins, x0, x1, y0, y1, ZI - 0.012, ZI)
    if lod == 0:
        ins = M.boolean("insert", ins, pocket_cutters(spec))
        # where a socket touches a scoop almost tangentially, the difference leaves points a
        # fraction of a millimetre apart and points on a line - triangulation makes degenerate faces
        # from them (with chamfers also where the scoop rounding meets the socket chamfer: edges
        # shorter than 0.25 mm are welded)
        bm = ins.bm
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.0002)
        bmesh.ops.dissolve_degenerate(bm, dist=0.00025, edges=bm.edges[:])
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), verts=bm.verts[:], edges=bm.edges[:])
        bm.normal_update()
    # the bottom is closed by the floor - no faces there; the sides are in the gap at the walls,
    # dark
    hidden = [f for f in ins.bm.faces if f.calc_center_median().z < ZI - 0.0115]
    bmesh.ops.delete(ins.bm, geom=hidden, context="FACES")

    def side(f):
        c = f.calc_center_median()
        return abs(f.normal.z) < 0.5 and min(abs(c.x - x0), abs(c.x - x1), abs(c.y - y0), abs(c.y - y1)) < 1e-4
    retag(ins, side)
    return [ins]


# --- gauges -------------------------------------------------------------------------------------
def build_gauges(spec):
    lod, n, arc, kc = spec["lod"], spec["sides"], spec["arc"], spec["kc"]
    hi = lod == 0
    parts = []
    # K-2: the bore gauge - a round tail with a head, then a square part with flats
    zc = ZI - ROD["depth"] + ROD["r"]
    yr, x0 = Y(ROD["y"]), ROD["x0"]
    rod = P("rod", "steel")
    prof = ([(0.0, 0.0016), (0.0006, 0.0022), (0.0114, 0.0022), (0.0120, 0.0019), (0.0894, 0.0019)] if hi else
            [(0.0, 0.0022), (0.0120, 0.0022), (0.0121, 0.0019), (0.0894, 0.0019)])
    lathe(rod, fx(x0, yr, zc), prof, n, arc=arc)
    slab(rod, rrect(-0.0018, 0.0018, -0.0017, 0.0017, (0.0005,) * 4, 1), levels(0.0, ROD["x1"] - x0 - 0.0890),
         frame=fx(x0 + 0.0890, yr, zc), caps=(False, True))
    parts.append(rod)
    # K-3...K-5: plug gauges, chamfers on the ends, a groove at the right one; K-5 has a cone, K-4 a
    # red band (part of the body: three segments of one profile)
    zs = ZI - SH_DEPTH + SH_R
    for s in SHASHKA:
        head = [(0.0, 0.0016), (0.0005, 0.0021), (0.0085, SH_R)] if s["n"] == 5 else [(0.0, 0.0038), (0.0007, SH_R)]
        tail = [(SH_L - 0.0044, SH_R), (SH_L - 0.0040, 0.0040), (SH_L - 0.0032, 0.0040), (SH_L - 0.0028, SH_R),
                (SH_L - 0.0007, SH_R), (SH_L, 0.0038)]
        if not hi:
            head, tail = [head[0], head[-1]], [(SH_L, SH_R)]
        fr = fx(s["x0"], Y(s["y"]), zs)
        if s["n"] == 4:
            a, b, c = P("shashka4", "steel2"), P("band4", "red"), P("shashka4_tail", "steel2")
            lathe(a, fr, head + [(0.014, SH_R)], n, arc=arc, caps=(True, False))
            lathe(b, fr, [(0.014, SH_R), (0.022, SH_R)], n, arc=arc, caps=(False, False))
            lathe(c, fr, [(0.022, SH_R)] + tail, n, arc=arc, caps=(False, True))
            parts += [a, b, c]
        else:
            sh = P("shashka%d" % s["n"], "steel2")
            lathe(sh, fr, head + tail, n, arc=arc)
            parts.append(sh)
    # K-1: plates with V-notches at the ends, chamfered top edges
    for i, f in enumerate(FLATS):
        x0, x1, yc, v = f["x0"], f["x0"] + FL_L, Y(f["y"]), 0.0016
        poly = [(x0, yc - FL_HW), (x1, yc - FL_HW), (x1, yc - 0.0015), (x1 - v, yc), (x1, yc + 0.0015),
                (x1, yc + FL_HW), (x0, yc + FL_HW), (x0, yc + 0.0015), (x0 + v, yc), (x0, yc - 0.0015)]
        fl = P("flat%d" % i, "steel")
        z0 = ZI - FL_DEPTH
        slab(fl, poly, levels(z0, z0 + FL_T, top=(0.0004, 1) if hi else None), caps=(False, True))
        parts.append(fl)
    # K-6: rods with a neck and a collar, the SKS gauge has a knurled body
    for i, p in enumerate(PINS):
        r, L = p["r"], p["L"]
        zp = ZI - (2 * r - 0.0020) + r
        fr = fx(p["x0"], Y(p["y"]), zp)
        if hi:
            body = [(0.0, r - 0.0005), (0.0005, r), (L - 0.0146, r)]
            tip = [(L - 0.0146, r), (L - 0.0140, 0.0024), (L - 0.0042, 0.0024), (L - 0.0038, 0.0029),
                   (L - 0.0006, 0.0029), (L, 0.0023)]
        else:
            body = [(0.0, r), (L - 0.0140, r)]
            tip = [(L - 0.0140, r), (L - 0.0139, 0.0026), (L, 0.0026)]
        if p["knurl"]:
            kb, tp = P("pin%d_knurl" % i, "knurl"), P("pin%d" % i, "steel")
            lathe(kb, fr, body, n, arc=arc, caps=(True, False))
            lathe(tp, fr, tip, n, arc=arc, caps=(False, True))
            parts += [kb, tp]
        else:
            pn = P("pin%d" % i, "steel")
            lathe(pn, fr, body + tip[1:], n, arc=arc)
            parts.append(pn)
    # plates on the insert: rounded corners
    for k, x, y, w, h in PLATES:
        pl = P("plate_%s" % k, "plate")
        slab(pl, rrect(x - w / 2, x + w / 2, Y(y) - h / 2, Y(y) + h / 2, (0.0010,) * 4, kc),
             levels(ZI - 0.0002, ZI + PLATE_T), caps=(False, True))
        parts.append(pl)
    return parts


# --- lid ----------------------------------------------------------------------------------------
def build_paper(spec, z1):
    """Inventory in the lid (closed-lid axes): a 0.4 mm sheet glued to the panel; the corner by the
    hinges on the right has come unstuck and lifted off the panel - the sheet is double-sided, the
    grid is denser at that corner.
    """
    hx, hy, t = PAPER
    pp = P("paper", "paper")
    if spec["lod"] > 0:
        g.box(pp, -hx, hx, OY - hy, OY + hy, z1 - t, z1)
        retag(pp, facing(2, 1))
        return [pp]
    cx, cy = hx, OY + hy

    def lift(x, y):
        return 0.0018 * max(0.0, 1.0 - math.hypot(x - cx, y - cy) / 0.024) ** 2
    xs = [-hx, 0.0, hx - 0.024, hx - 0.010, hx]
    ys = [OY - hy, OY + hy - 0.024, OY + hy - 0.010, OY + hy]
    bm = pp.bm
    fr = [[bm.verts.new((x, y, z1 - t - lift(x, y))) for x in xs] for y in ys]
    bk = [[bm.verts.new((x, y, z1 - lift(x, y))) for x in xs] for y in ys]
    nx, ny = len(xs) - 1, len(ys) - 1
    faces = []
    for j in range(ny):
        for i in range(nx):
            faces.append(face(pp, [fr[j][i], fr[j][i + 1], fr[j + 1][i + 1], fr[j + 1][i]], (0, 0, -1)))
            faces.append(face(pp, [bk[j][i], bk[j][i + 1], bk[j + 1][i + 1], bk[j + 1][i]], (0, 0, 1)))
    per = ([(i, 0) for i in range(nx)] + [(nx, j) for j in range(ny)] + [(i, ny) for i in range(nx, 0, -1)] +
           [(0, j) for j in range(ny, 0, -1)])
    for k in range(len(per)):
        (i0, j0), (i1, j1) = per[k], per[(k + 1) % len(per)]
        a0, a1, b0, b1 = fr[j0][i0], fr[j1][i1], bk[j0][i0], bk[j1][i1]
        mid = (a0.co + a1.co) / 2
        faces.append(face(pp, [a0, a1, b1, b0], (mid.x, mid.y - OY, 0.0)))
    pp.tag(faces)
    return [pp]


def build_lid(spec):
    """Lid in closed axes: a panel with rounded edges, sides (the lateral ones over the full depth), the
    inventory, hinge leaves, the hasp plate; then the rotation on the hinges (lid_matrix).
    """
    lod, kc, ke = spec["lod"], spec["kc"], spec["ke"]
    z0, z1, z2 = ZR, ZR + LR, ZR + LH
    panel = P("lid_panel", "lid_panel")
    slab(panel, rrect(BX0, BX1, BY0, BY1, (RC,) * 4, kc),
         levels(z1, z2, bot=(0.0006, 1) if ke else None, top=(RL, ke) if ke else None))
    parts = [panel]
    bot = (RF, ke) if ke else None
    for nm, x0, x1, rr in (("lid_l", BX0, BX0 + T, (RC, 0.0, 0.0, RC)), ("lid_r", BX1 - T, BX1, (0.0, RC, RC, 0.0))):
        w = P(nm, "frame_y")
        slab(w, rrect(x0, x1, BY0, BY1, rr, kc), levels(z0, z1, bot=bot))
        retag(w, facing(2, 1))
        parts.append(w)
    for nm, y0, y1 in (("lid_f", BY0, BY0 + T), ("lid_b", BY1 - T, BY1)):
        w = P(nm, "frame_x")
        slab(w, rrect(BX0 + T, BX1 - T, y0, y1), levels(z0, z1, bot=bot))
        retag(w, lambda f: facing(2, 1)(f) or abs(f.normal[0]) > 0.99)
        parts.append(w)
    parts += build_paper(spec, z1) + build_hinges(spec, lid=True)
    if lod == 0:
        # hasp plate on the face of the front side: the box strap is swung up, its hole meets the
        # plate hole - the seal wire goes through both; the plate is on one screw
        fr = g.Frame((0.0, BY0, 0.0), (1, 0, 0), (0, 0, 1), (0, -1, 0))
        zc = LATCH[2] + (LATCH[2] - LATCH[0] - 0.0045)          # hole of the strap swung up
        st, ss, sl, hole = P("lid_plate", "hasp"), P("lid_plate_screw", "screw"), P("lid_plate_slot", "slot"), \
            P("lid_plate_hole", "inner")
        slab(st, rrect(-0.004, 0.004, zc - 0.0055, zc + 0.0035, (0.0012,) * 4, kc), levels(-0.0001, 0.0007),
             frame=fr, caps=(False, True))
        disk(hole, g.Frame((0.0, BY0 - 0.0007, zc), (1, 0, 0), (0, 0, 1), (0, -1, 0)), 0.0012, 10, 0.00003)
        screw(ss, sl, g.Frame((0.0, BY0 - 0.0007, zc - 0.0036), (1, 0, 0), (0, 0, 1), (0, -1, 0)), 0.0011, 0.00025, 8,
              24.0)
        parts += [st, ss, sl, hole]
    m = lid_matrix()
    for p in parts:
        bmesh.ops.transform(p.bm, matrix=m, verts=p.bm.verts[:])
        p.bm.normal_update()
    return parts


def build_lod(spec):
    parts = build_box(spec) + build_insert(spec) + build_gauges(spec) + build_lid(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    for p in parts:
        bad = sum(1 for f in p.bm.faces if f.calc_area() < 5e-8)
        if bad:
            print("degenerate: %s %d (lod %d)" % (p.name, bad, spec["lod"]))
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("bounds", BOUNDS)
    return parts


def collision():
    """Two convex parts: the box with the gauges and the open lid. Mass is the item's weight in the mod,
    0.8 kg.
    """
    box = kx.box_pts(BX0, BX1, BY0 - 0.0012, BY1 + 0.0004, 0.0, ZR + 0.004)
    m = lid_matrix()
    lid = [tuple(m @ Vector(q)) for q in kx.box_pts(BX0, BX1, BY0 - 0.0012, BY1 + 0.0004, ZR - 0.006, ZR + LH)]
    pen = kx.PEN + r"\wood.rvmat"
    comps = [(box, pen), (lid, pen)]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    memory = {
        # inventory preview camera: front-left and from above (invView = camera position)
        "invView": [(-0.26, -0.46, 0.42)],
        "ce_center": [(0.0, 0.0, 0.08)],
        "ce_radius": [(0.13, 0.0, 0.08)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


# the first five are the --look preview: overall view, the insert from above, the right column, the
# hinge, the hasp from the front
SHOTS = [
    ("front", (-0.22, -0.52, 0.40), (0.0, 0.0, 0.06), 40),
    ("insert", (0.0, OY - 0.13, 0.36), (0.0, OY + 0.002, 0.03), 46),
    ("right", (0.10, OY - 0.11, 0.20), (0.048, OY - 0.008, 0.034), 55),
    ("hinge", (0.10, -0.05, 0.15), (0.058, BY1 - 0.003, ZR + 0.006), 60),
    ("latch", (-0.06, -0.24, 0.09), (-0.025, BY0, 0.022), 50),
    ("lid", (0.05, -0.40, 0.15), (0.0, 0.06, 0.10), 46),
    ("left", (-0.48, -0.02, 0.26), (-0.04, 0.0, 0.06), 40),
    ("back", (0.32, 0.46, 0.30), (0.0, 0.02, 0.07), 40),
]

M.look_shots = (5, 2)
M.run(build_lod, collision, SHOTS, row_step=0.30, row_shot=((0.15, -1.1, 0.40), (0.15, 0, 0.08)))
