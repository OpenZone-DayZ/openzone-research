"""M28 - homemade Freedom chronograph: Ballistic Sample Analyzer of Freedom (OZL_Frd_Proc_Ball).
An analyzer: 4x4 cargo, no modules. The sample socket is a V-stop for a barrel at the start of the rail.

    blender --background --python build_m28.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (decals on the case, the laptop lid
and the rail, the keyboard, the own texture of the laptop screen and the unit display - "off" and the
"working" frames). The layout is in layout.py (shared with make_decals.py).

A light homemade rig on tripods, unlike M24 (Duty: a B6 console and a heavy rail bed with a clamp).
A long aluminum rail on two tripods, two U-shaped photosensor frames with visors, a V-stop for the
barrel at the start, a sandbag catcher at the end; on the floor between the tripods a bright green
case, on it an open 90s laptop and a homemade interface unit; the wires are taped to the rail.
1.60 x 1.18 x 0.58 m.

Sources and sizes:
- the Oehler 35P chronograph: a 4-foot rail, 1219 mm between the primary screens - here the frame
  centers are at +-0.6095; the frames follow the Oehler Skyscreen III (the sensor body at the bottom,
  rods going up in a V, a diffuser bar on top) and the ProChrono Digital (rods with visors at the
  ends); body 80 x 100 x 55 mm, rods up to 1.16 m, spread at the top 0.32, visor 0.10 x 0.37 -
  estimated from photos;
- an amateur tripod setup (a forum photo): a rail on a tripod, wires hang and lie on the ground;
- a 1.4 m rail, an aluminum tube 40 x 30 mm, top at 0.87; two photo tripods, legs dia. 21/16 mm in two
  sections, spread 0.26 - the height with the rail ~0.87, with the frames 1.18;
- a Pelican 1520 class case: 0.502 x 0.401 x 0.188 m outside (as in M27), bright green (Freedom, no
  olive);
- an IBM ThinkPad 760 class laptop (1995-97): 297 x 211 x 54 mm (11.7 x 8.3 x 2 inches), a 12.1" 4:3
  screen - 246 x 184 mm; base 35, lid 19 - an estimate;
- a sandbag 14 x 26 inches (0.36 x 0.66 m empty), filled halfway and folded: it stands
  0.12 x 0.30 x 0.23 on a piece of plywood at the end of the rail;
- an interface unit 120 x 100 x 50 mm (homemade in a cast case, an estimate), a V-stop 60 x 90 mm on
  a post - an estimate; BNC connectors (dia. 14.5 plug), DB-9, a power plug - typical sizes.

Detail:
- the "dayz" look: matte, more worn, spots, scratches, shadows in corners;
- chamfers and roundings on all visible edges. Tripods: a quick-release plate, a head with a tilt axis,
  a handle and a lock, a spider with three lugs and leg axes, a column with a lock and braces,
  two-section legs with flag locks, rubber heels. Frames: rod sockets, a sensor window in the frame, an
  LED in a holder, a BNC jack with a plug, a thumbscrew clamp to the rail, screws. The case: a seam
  belt along the rounded outline, double latches with pivots, a folding handle, a knurled valve, a
  hinge. The laptop: separate keys, a trackpoint and two buttons, the screen sunk into the frame,
  hinges, ports, feet, a disk lamp. The unit: a lid on screws, a display in a frame, an LED in a
  holder, a toggle with a nut, BNC and DB-9 connectors, feet. All cables are smooth curves
  (Catmull-Rom, g.pipe) with BNC and DB-9 plugs and a power plug, the laptop power supply has a cord
  and a plug;
- the catcher bag is a smooth "pillow" (a settled bottom, a crumpled top, gentle folds, a neck with a
  tie), the fabric is a weave of threads (build_burlap), not a chamfered box;
- the V-stop plate ends 1.3 cm short of the body of the first frame;
- the small stuff is vanilla DayZ items as proxies (kvanilla, DECOR): on the case a screwdriver, two
  9 V batteries (chronographs run on a "Krona"), a box of 7.62 x 39 cartridges and loose ones; on the
  floor tape, a sheet of paper with a pen (series records), a water bottle, an electrician's kit and
  pliers.
Freedom decals: a peace sign on the case face, a peace sign and LEGALIZE on the laptop lid -
make_decals.py.

Working look: the laptop screen and the unit display are ozl_screen (own texture, OZL_WorkFx frames:
a series of 10 shots - speed, table, bars, totals, the same speed on the display); the LEDs of the
frames and the unit and the disk lamp of the laptop are ozl_lamp (_on atlas, OZL_WorkFx blink). The
chronograph has no moving parts. LODs: the mid LOD has no small stuff, the far one has no wires, tape,
decals or the own screen texture (one section; the case, the laptop and the rail are from regions
without decals).

Blender axes: X is width (along the rail, the barrel at -x), Y is depth (the face looks to -Y), Z is up.
"""
import math
import os
import sys

from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import kvanilla as kv  # noqa: E402
import kwood  # noqa: E402
import layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m (the rest is in layout.py)
# =============================================================================
RX0, RX1, RY, RHW, RZ0, RZ1 = L.RX0, L.RX1, L.RY, L.RHW, L.RZ0, L.RZ1
FX, F_HX, F_HY, F_Z1, F_TOP, F_TOPHW = L.FX, L.F_HX, L.F_HY, L.F_Z1, L.F_TOP, L.F_TOPHW
CZ, LZ = L.CZ, L.LZ
LID_T = math.radians(L.LID_DEG)
LID = g.Frame(L.HINGE, (1, 0, 0), (0, math.sin(LID_T), math.cos(LID_T)), (0, -math.cos(LID_T), math.sin(LID_T)))
FRONT = g.Frame((0, 0, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0))  # facing -y: a = x, b = z
YC = RY + RHW + 0.007                                        # frame cables run along the rear side of the rail
CABLE_Z = (0.843, 0.857)
BNC_Z = RZ1 + 0.028                                          # connector on the back of the frame body
BOX_BNC = (0.13, 0.17)                                       # connectors on the back of the unit: x
BOX_BNC_Z = L.BOX[4] + 0.03
FRAME_TILT = (3.0, -4.0)                                     # visors turned crooked, degrees
ROD_Y = 0.036                                                # rod sockets on top of the frame body: +-y
SCR_IN = 0.003                                               # the screen is sunk into the lid frame
# tripod z levels: head (plate, tilt body, base), spider, column, braces
TZ_PLATE, TZ_TILT, TZ_PAN = 0.812, 0.784, 0.762
TZ_SPIDER = (0.700, 0.738)
TZ_BRACE = 0.47
LUG_R = 0.044                                                # leg axes on the spider: radius
# laptop connectors: power at the back left, serial on the right; the unit: DB-9 on the left side
DC_X = L.LX0 + 0.04
SER_Y_LAP, SER_Y_BOX = -0.10, -0.150
SER_Z = CZ + 0.0175
# laptop power supply on the floor behind the case: bottom center, axis from the laptop cord inlet to the mains cord
BRICK, BRICK_U = (-0.33, 0.30, 0.0), (-0.8, 0.6, 0.0)

LOD_SPECS = [
    dict(lod=0, sides=16),
    dict(lod=1, sides=8),
    dict(lod=2, sides=4),
]

REGIONS = {
    "rail": ("rail", 1.2), "alu": ("alu", 0.9), "black": ("black", 1.2), "rubber": ("rubber", 0.8),
    "housing": ("housing", 1.6), "rods": ("rods", 1.2), "diffuser": ("diffuser", 1.2), "lens": ("lens", 2.0),
    "wood": ("wood", 1.0), "sandbag": ("sandbag", 1.0), "cord": ("cord", 2.0),
    "case": ("case", 1.5), "case_plain": ("case_plain", 0.6), "case_hw": ("case_hw", 1.4),
    "laptop": ("laptop", 2.6), "key": ("key", 2.5), "track_red": ("track_red", 4.0),
    "box": ("box", 1.8), "chrome": ("chrome", 1.6), "steel": ("steel", 1.6), "dark": ("dark", 0.6),
    "led_g": ("led_g", 1.0), "led_r": ("led_r", 1.0),
    "tape": ("tape", 1.4), "tape_blue": ("tape_blue", 1.4), "cable": ("cable", 1.0), "cable_grey": ("cable_grey", 1.0),
}

# =============================================================================
# Materials
# =============================================================================


def build_scuffed(mat, origin, color, bare=kmats.lin((112, 112, 116)), seed=1.0, gloss=0.32, spec=0.25,
                  wear=(0.66, 0.71), edge_k=0.7, rub=(), scratch=0.0, floor_z=0.0, dust=0.3, grime=0.3,
                  decal_items=()):
    """Scuffed, careless paint (plastic) without rust - the M27 builder, without stripes and oil: rubbed to
    the base on the edges (edge_k) and where hands take it (rub - [(center, semi-axes, strength)]),
    scratches along x; decals go over the wear (the decal itself is already worn in the PNG), dust and
    grime go over everything."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    col = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                 tuple(c * 0.9 for c in color[:3]) + (1,), color)
    edge = t.maprange(t.edge_wear(0.004), 0.05, 0.22, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 11.0, 10.0, 0.7), 0.75), t.math("MULTIPLY", edge, edge_k))
    grain = t.maprange(t.noise(vec, 34.0, 8.0, 0.7), 0.3, 0.7, 0.55, 1.0)
    for c, r, k in rub:
        d = t.node("ShaderNodeVectorMath")
        d.operation = "SUBTRACT"
        t.link(pos, d.inputs[0])
        d.inputs[1].default_value = c
        q = t.node("ShaderNodeVectorMath")
        q.operation = "DIVIDE"
        t.link(d.outputs[0], q.inputs[0])
        q.inputs[1].default_value = r
        ln = t.node("ShaderNodeVectorMath")
        ln.operation = "LENGTH"
        t.link(q.outputs[0], ln.inputs[0])
        near = t.maprange(ln.outputs["Value"], 0.25, 1.0, 1.0, 0.0)
        f = t.math("ADD", f, t.math("MULTIPLY", t.math("MULTIPLY", near, grain), k))
    worn = t.step(f, wear[0], wear[1])
    brush = t.noise(t.stretch(vec, 0.04, 1.0, 1.0), 90.0, 4.0, 0.7)
    metal = t.mixc(t.maprange(brush, 0.3, 0.7, 0.0, 1.0), tuple(c * 0.75 for c in bare[:3]) + (1,),
                   tuple(min(1.0, c * 1.15) for c in bare[:3]) + (1,))
    rim = t.math("SUBTRACT", t.step(f, wear[0] - 0.05, wear[0]), worn)
    col = t.mixc(t.math("MULTIPLY", rim, 0.6), col, kmats.lin((52, 50, 46)))
    col = t.mixc(worn, col, metal)
    h = t.math("MULTIPLY", worn, -0.3)
    g_ = t.math("ADD", gloss, t.math("MULTIPLY", worn, 0.62 - gloss))
    s_ = t.math("ADD", spec, t.math("MULTIPLY", worn, 0.70 - spec))
    if scratch > 0:
        sc = t.step(t.noise(t.stretch(vec, 0.02, 1.0, 1.0), 260.0, 2.0, 0.5), 0.70, 0.73)
        sc = t.math("MULTIPLY", sc, t.maprange(t.noise(vec, 5.0, 4.0, 0.5), 0.35, 0.65, 0.0, scratch))
        col = t.mixc(t.math("MULTIPLY", sc, 0.7), col, metal)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", sc, 0.15))
    col = kmats.decals(t, col, sep, nsep, decal_items)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g_, s_, h)


def build_burlap(mat, origin, color, seed=5.0, floor_z=0.0, dust=0.5, grime=0.5):
    """Polypropylene fabric sack: blotchy tone, weave threads (noise stripes along three axes - on any
    face two of them), sand in the folds and on top; almost no shine, the threads are relief."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    col = t.mixc(t.maprange(t.noise(vec, 5.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                 tuple(c * 0.80 for c in color[:3]) + (1,), color)
    weave = None
    for k in ((0.04, 1.0, 1.0), (1.0, 0.04, 1.0), (1.0, 1.0, 0.04)):
        s = t.maprange(t.noise(t.stretch(vec, *k), 320.0, 1.0, 0.5), 0.42, 0.62, 0.0, 1.0)
        weave = s if weave is None else t.math("MAXIMUM", weave, s)
    col = t.mixc(t.math("MULTIPLY", weave, 0.22), col, tuple(c * 0.6 for c in color[:3]) + (1,))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g_ = t.math("SUBTRACT", 0.08, t.math("MULTIPLY", dirt, 0.04))
    return kmats.out(t, col, g_, 0.04, t.math("MULTIPLY", weave, 0.25))


def wdecal(name):
    return os.path.join(WORK, name)


def decal_y(name, x0, x1, z0, z1, y, sign=-1, depth=(-0.002, 0.002)):
    """Decal on a face facing -y (sign=1 - toward +y) at depth y..y+depth."""
    return (wdecal(name), "y", sign, ("x", "z"), ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0),
            (y + depth[0], y + depth[1]))


def decal_x(name, y0, y1, z0, z1, x):
    return (wdecal(name), "x", 1, ("y", "z"), ((y0 + y1) / 2, (z0 + z1) / 2), (y1 - y0, z1 - z0),
            (x - 0.002, x + 0.002))


def decal_z(name, x0, x1, y0, y1, z):
    return (wdecal(name), "z", 1, ("x", "y"), ((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0, y1 - y0),
            (z - 0.002, z + 0.002))


CASE_DECALS = [decal_y("decal_case_front.png", *L.CASE_FRONT, L.CY0), decal_z("decal_case_top.png", *L.CASE_TOP, CZ),
               decal_x("decal_case_side.png", *L.CASE_SIDE, L.CX1)]
RAIL_DECAL = decal_y("decal_rail.png", *L.RAIL_FRONT, RY - RHW)
KEYS_DECAL = decal_z("decal_keys.png", *L.KEYS, LZ)
# lid back: the plane c = -LT_L is tilted by LID_DEG, the y projection follows its extent
_lb0, _lb1 = L.lid_point(0, 0.01, -L.LT_L), L.lid_point(0, L.LT_D - 0.01, -L.LT_L)
LID_DECAL = (wdecal("decal_lid.png"), "y", 1, ("x", "z"), (L.LT_C[0], (_lb0[2] + _lb1[2]) / 2),
             (L.LT_W - 0.02, _lb1[2] - _lb0[2]), (_lb0[1] - 0.002, _lb1[1] + 0.002))

GREEN = kmats.lin((62, 152, 44))
# rail: the top is worn where the frames stand and the stop plate lies
RAIL_RUB = [((x, RY, RZ1), (0.07, 0.03, 0.02), 0.35) for x in FX] + [((RX0 + 0.05, RY, RZ1), (0.10, 0.03, 0.02), 0.3)]
CASE = dict(color=GREEN, bare=kmats.lin((112, 176, 96)), seed=10.3, gloss=0.3, spec=0.2, wear=(0.70, 0.76),
            edge_k=0.8, scratch=0.6, dust=0.45, grime=0.35)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "rail": (build_scuffed, dict(color=kmats.lin((168, 170, 170)), bare=kmats.lin((206, 206, 210)), seed=2.1,
                                 gloss=0.45, spec=0.5, wear=(0.70, 0.75), edge_k=0.6, rub=RAIL_RUB, scratch=0.7,
                                 floor_z=RZ0, dust=0.3, grime=0.15, decal_items=[RAIL_DECAL])),
    "alu": ("steel", dict(seed=2.6, tone=0.45, along="z", gloss=0.5, spec=0.6, floor_z=0.0, dust=0.3, grime=0.35)),
    "housing": (build_scuffed, dict(color=kmats.lin((30, 30, 32)), bare=kmats.lin((70, 70, 72)), seed=3.3,
                                    wear=(0.70, 0.76), edge_k=0.8, scratch=0.3, floor_z=RZ1, dust=0.35, grime=0.2)),
    "rods": ("steel", dict(seed=3.7, tone=0.16, along="z", gloss=0.45, spec=0.5, floor_z=RZ1, dust=0.15, grime=0.2)),
    "diffuser": ("plastic", dict(color=kmats.lin((226, 224, 212)), gloss=0.45, spec=0.3, dust=0.45, grime=0.3,
                                 scuff=(0.62, 0.70))),
    "lens": ("flat", dict(color=kmats.lin((24, 30, 38)), gloss=0.95, spec=0.9)),
    # plywood under the bag: pine veneer along x, the edges darkened
    "wood": (kwood.build_wood, dict(color=kmats.lin((168, 132, 88)), seed=6.1, along="x", floor_z=RZ1, dust=0.45,
                                    grime=0.45, knots=0.3)),
    "sandbag": (build_burlap, dict(color=kmats.lin((176, 160, 124)), seed=6.6, floor_z=L.BAG[4], dust=0.5, grime=0.5)),
    "cord": ("plastic", dict(color=kmats.lin((150, 128, 88)), gloss=0.08, spec=0.05, mottle=0.25, dust=0.3, grime=0.4)),
    "case": (build_scuffed, dict(CASE, decal_items=CASE_DECALS)),
    "case_plain": (build_scuffed, CASE),
    "case_hw": ("plastic", dict(color=kmats.lin((34, 34, 36)), gloss=0.35, spec=0.25, dust=0.3)),
    "laptop": (build_scuffed, dict(color=kmats.lin((40, 40, 42)), bare=kmats.lin((74, 74, 76)), seed=4.1,
                                   gloss=0.3, spec=0.22, wear=(0.71, 0.77), edge_k=0.8, scratch=0.4, floor_z=CZ,
                                   dust=0.3, grime=0.2, decal_items=[KEYS_DECAL, LID_DECAL])),
    # keys: dark plastic, the middle rubbed to a shine
    "key": ("plastic", dict(color=kmats.lin((50, 50, 53)), gloss=0.3, spec=0.2, dust=0.25, grime=0.3,
                            scuff=(0.55, 0.64))),
    "track_red": ("plastic", dict(color=kmats.lin((176, 34, 30)), gloss=0.15, spec=0.1, dust=0.1)),
    "box": (build_scuffed, dict(color=kmats.lin((70, 78, 88)), bare=kmats.lin((150, 150, 154)), seed=4.7,
                                wear=(0.68, 0.73), edge_k=0.9, scratch=0.5, floor_z=CZ, dust=0.35, grime=0.2)),
    "chrome": ("steel", dict(seed=5.1, tone=0.32, along="z", gloss=0.75, spec=0.85, floor_z=CZ, dust=0.1, grime=0.2)),
    "dark": ("flat", dict(color=kmats.lin((24, 28, 27)), gloss=0.8, spec=0.6)),
    "led_g": ("flat", dict(color=kmats.lin((34, 64, 40)), gloss=0.85, spec=0.8)),
    "led_g_on": ("flat", dict(color=kmats.lin((130, 255, 140)), gloss=0.85, spec=0.8)),
    "led_r": ("flat", dict(color=kmats.lin((72, 24, 22)), gloss=0.85, spec=0.8)),
    "led_r_on": ("flat", dict(color=kmats.lin((255, 86, 60)), gloss=0.85, spec=0.8)),
    "tape": ("plastic", dict(color=kmats.lin((148, 150, 150)), gloss=0.5, spec=0.35, dust=0.3, grime=0.4,
                             scuff=(0.66, 0.74))),
    "tape_blue": ("plastic", dict(color=kmats.lin((34, 74, 168)), gloss=0.55, spec=0.35, dust=0.15, grime=0.3,
                                  scuff=(0.7, 0.78))),
    "cable": ("plastic", dict(color=kmats.lin((24, 24, 24)), gloss=0.35, spec=0.25, dust=0.35)),
    "cable_grey": ("plastic", dict(color=kmats.lin((150, 150, 146)), gloss=0.35, spec=0.25, dust=0.3, grime=0.4)),
})

OBJ, NAME = "m28_frd_proc_ball", "ozr_frd_proc_ball"
# Working look: the laptop screen and the unit display are ozl_screen, an own texture (section screen,
# the frames are cycled by the mod script); the LEDs and the disk lamp are ozl_lamp (_on atlas, blink).
SEL_SCREEN, SEL_LAMP = "ozl_screen", "ozl_lamp"
ON = dict(remap={"led_g": "led_g_on", "led_r": "led_r_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
FRAMES = 10
SCREEN = dict(off="decal_panel_off.png", frames=["decal_panel_f%02d.png" % i for i in range(FRAMES)], size=L.PANEL_PX,
              gloss=0.8)
# vanilla items: on the case and on the floor between the tripods
DECOR = [
    kv.put("screwdriver", (0.09, -0.210, CZ), **kv.flat(180)),                           # in front of the laptop
    kv.put("battery9v", (0.215, 0.065, CZ), up=(0, 0, 1), fwd=(0.3, -1, 0)),               # spare "Krona" batteries
    kv.put("battery9v", (0.150, 0.080, CZ), **kv.flat(70)),
    kv.put("ammobox762", (-0.10, 0.109, CZ), **kv.flat(4)),                                # behind the laptop lid
    kv.put("rounds762", (0.0, 0.112, CZ), up=(0, 0, 1), fwd=(0.2, -1, 0)),
    kv.put("ducttape", (-0.43, -0.29, 0.0), **kv.flat(0)),
    kv.put("paper", (0.41, -0.26, 0.0), lift=0.0008, **kv.flat(10)),                      # series records
    kv.put("pen", (0.44, -0.24, 0.0012), **kv.flat(40)),
    kv.put("waterbottle", (0.33, 0.135, 0.0), up=(0, 0, 1), fwd=(0, -1, 0)),
    kv.put("electrickit", (0.10, 0.26, 0.0), **kv.flat(8)),
    kv.put("pliers", (0.33, 0.265, 0.0), **kv.flat(150)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 selections=(SEL_SCREEN, SEL_LAMP), hidden=(SEL_SCREEN, SEL_LAMP), states={"on": ON},
                 decor=DECOR, panels={"screen": SCREEN})
P = M.part
BOUNDS = {}


# =============================================================================
# Primitives that kgeo does not have
# =============================================================================
def turn(cx, cy, z, deg):
    """Local axes rotated about the vertical: u along the item, v across, n up."""
    a = math.radians(deg)
    return g.Frame((cx, cy, z), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))


def axis_frame(o, d):
    """Local axes with n along d (a solid of revolution in any direction)."""
    d = Vector(d).normalized()
    ref = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    u = d.cross(ref).normalized()
    return g.Frame(o, u, d.cross(u), d)


def face(part, verts, want):
    """Face from bmesh vertices, oriented toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def lathe(part, prof, sides, fr, cap0=False, cap1=False, phase=0.0):
    """Solid of revolution around axis n of frame fr: prof [(r, h)] - along the outer surface from the
    start to the end (along the axis by growing h, on an end - toward the axis or away); cap0 / cap1 -
    close the first / last ring. The face normal points outward from the profile."""
    bm = part.bm
    rings = [[bm.verts.new(fr.p(r * math.cos(2 * math.pi * k / sides + phase),
                                r * math.sin(2 * math.pi * k / sides + phase), h)) for k in range(sides)]
             for r, h in prof]
    new = []
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        for k in range(sides):
            j = (k + 1) % sides
            q = [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]
            c = sum((v.co for v in q), Vector()) / 4 - fr.o
            rad = (c - fr.n * c.dot(fr.n)).normalized()
            new.append(face(part, q, rad * (h1 - h0) - fr.n * (r1 - r0)))
    if cap0:
        new.append(face(part, rings[0], -fr.n))
    if cap1:
        new.append(face(part, rings[-1], fr.n))
    bm.normal_update()
    return part.tag(new)


def knurl(part, fr, r, depth, n, h0, h1):
    """Knurled thumbscrew around axis n of frame fr: 2n vertices around, every other one sunk by depth."""
    poly = [((r - depth * (k % 2)) * math.cos(math.pi * k / n), (r - depth * (k % 2)) * math.sin(math.pi * k / n))
            for k in range(2 * n)]
    return g.prism(part, poly, (0, 1), h0, h1, frame=fr)


def keycap(part, x0, x1, y0, y1, z0, z1, inset=0.0005):
    """Key without a bottom: the top is narrower than the base by inset (slanted sides), five faces."""
    bm = part.bm
    lo = [bm.verts.new(q) for q in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0))]
    hi = [bm.verts.new(q) for q in ((x0 + inset, y0 + inset, z1), (x1 - inset, y0 + inset, z1),
                                    (x1 - inset, y1 - inset, z1), (x0 + inset, y1 - inset, z1))]
    c = ((x0 + x1) / 2, (y0 + y1) / 2)
    new = [face(part, hi, (0, 0, 1))]
    for k in range(4):
        j = (k + 1) % 4
        m = (lo[k].co + lo[j].co) / 2
        new.append(face(part, [lo[k], lo[j], hi[j], hi[k]], (m.x - c[0], m.y - c[1], 0.0)))
    return part.tag(new)


def rrect(hx, hy, r, n):
    """Rectangle with rounded corners (outline counterclockwise) - the case belt."""
    pts = []
    for cx, cy, a0 in ((hx - r, hy - r, 0.0), (-hx + r, hy - r, 90.0), (-hx + r, -hy + r, 180.0), (hx - r, -hy + r, 270.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def rod(part, a, b, r, sides):
    return g.pipe(part, [tuple(a), tuple(b)], r, sides)


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, from M24)."""
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


def bev(lod, r):
    """Edge chamfer-rounding: near LOD - 2 segments (small parts - 1), mid LOD - 1 for large ones."""
    if lod == 0:
        return dict(r=r, seg=2 if r >= 0.005 else 1)
    if lod == 1 and r >= 0.006:
        return dict(r=r, seg=1)
    return {}


def front_quad(part, x0, x1, z0, z1, y):
    """A single face facing -y (far LOD: the screen, an LED)."""
    return g.quad(part, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)])


def cable(name, region, pts, r, lod, k=3, sides=6):
    """Cable as a smooth curve (near LOD) or through the control points (mid LOD)."""
    c = P(name, region)
    if lod == 0:
        g.pipe(c, spline(pts, k), r, sides)
    else:
        g.pipe(c, pts, r, 4)
    return [c]


def bnc_jack(part, o, d, lod):
    """BNC jack on a case: a hex nut and a barrel (under the plug)."""
    fr = axis_frame(o, d)
    lathe(part, [(0.0075, 0.0), (0.0075, 0.0025), (0.0048, 0.0025), (0.0048, 0.006)], 6, fr, cap1=True)


def bnc_plug(ch, bt, o, d, lod):
    """BNC plug on a cable: o - the jack end, d - from the jack toward the cable; a knurled bayonet nut, a
    boot, a rubber strain relief. Returns the point where the cable leaves."""
    fr = axis_frame(o, d)
    n = 10 if lod == 0 else 6
    lathe(ch, [(0.0062, 0.0025), (0.0070, 0.0035), (0.0070, 0.0125), (0.0060, 0.0145), (0.0052, 0.0165)], n, fr,
          cap0=True)
    lathe(bt, [(0.0052, 0.0160), (0.0050, 0.0220), (0.0043, 0.0300), (0.0039, 0.0340)], 8 if lod == 0 else 5, fr,
          cap1=True)
    return tuple(fr.p(0, 0, 0.032))


# =============================================================================
# Rail and tripods
# =============================================================================
def build_rail(spec):
    lod = spec["lod"]
    rl = P("rail", "rail" if lod < 2 else "alu")
    g.box(rl, RX0, RX1, RY - RHW, RY + RHW, RZ0, RZ1, **(dict(r=0.004, seg=2) if lod == 0 else
                                                           dict(r=0.004, seg=1) if lod == 1 else {}))
    parts = [rl]
    if lod == 0:
        # end plugs: an insert and a rounded shoulder
        pl = P("rail_plugs", "black")
        for s, xe in ((-1, RX0), (1, RX1)):
            g.box(pl, *sorted((xe, xe + s * 0.004)), RY - RHW - 0.0008, RY + RHW + 0.0008, RZ0 - 0.0008, RZ1 + 0.0008,
                  r=0.0018, seg=1)
        parts.append(pl)
    return parts


def leg_points(cx, a):
    ca, sa = math.cos(a), math.sin(a)
    top = Vector((cx + LUG_R * ca, RY + LUG_R * sa, 0.712))
    foot = Vector((cx + L.TR * ca, RY + L.TR * sa, 0.0015))
    return top, foot, Vector((ca, sa, 0.0))


def build_tripod(i, spec):
    """Photo tripod: a quick-release plate under the rail, a head (tilt body and axis, a handle, a lock), a
    pan base, a column with a lock, a spider with lugs, two-section legs with flag locks, rubber heels,
    braces from the column to the legs."""
    lod, n = spec["lod"], spec["sides"]
    cx, deg = L.TRIPODS[i]
    al, bk, rb = P("tripod%d_alu" % i, "alu"), P("tripod%d_black" % i, "black"), P("tripod%d_rubber" % i, "rubber")
    g.box(al, cx - 0.045, cx + 0.045, RY - 0.035, RY + 0.035, TZ_PLATE, RZ0, **bev(lod, 0.003))
    angles = [math.radians(deg + 90 + 120 * k) for k in range(3)]
    if lod == 2:
        g.box(bk, cx - 0.03, cx + 0.03, RY - 0.03, RY + 0.03, TZ_SPIDER[0], TZ_PLATE)
        for a in angles:
            top, foot, _ = leg_points(cx, a)
            rod(al, top, foot, 0.01, 3)
        return [al, bk]
    up = turn(cx, RY, 0.0, deg)
    # head: the tilt body, the tilt axis across the rail, the pan base
    g.box(bk, -0.028, 0.028, -0.026, 0.026, TZ_TILT, TZ_PLATE, frame=up, **bev(lod, 0.005))
    g.cyl(bk, (0.0, 0.0, TZ_TILT + 0.008), "y", 0.015, 0.068, n, frame=up)
    pan = [(0.030, 0.0), (0.033, 0.003), (0.033, 0.016), (0.029, 0.020), (0.026, 0.022)]
    lathe(bk, pan if lod == 0 else [pan[0], pan[2], pan[4]], min(n, 12), g.Frame((cx, RY, TZ_PAN), (1, 0, 0), (0, 1, 0), (0, 0, 1)),
          cap0=True, cap1=True)
    # column from the braces to the head, a spider with three lugs
    g.cyl(al, (cx, RY, (TZ_BRACE + TZ_PAN) / 2), "z", 0.011, TZ_PAN - TZ_BRACE, max(6, n - 4))
    sp = [(0.030, 0.0), (0.038, 0.006), (0.038, 0.030), (0.030, 0.038)]
    lathe(bk, sp, min(n, 12),
          g.Frame((cx, RY, TZ_SPIDER[0]), (1, 0, 0), (0, 1, 0), (0, 0, 1)), cap0=True, cap1=True)
    parts = [al, bk, rb]
    for k, a in enumerate(angles):
        top, foot, rad = leg_points(cx, a)
        d = (foot - top).normalized()
        if lod == 1:
            rod(al, top, foot + d * -0.02, 0.0095, 6)
            g.cyl(rb, (foot.x, foot.y, 0.012), "z", 0.011, 0.024, 6)
            continue
        lug = turn(cx, RY, 0.0, math.degrees(a))
        g.box(bk, 0.028, 0.052, -0.012, 0.012, TZ_SPIDER[0] + 0.002, 0.728, frame=lug)
        mid = top + (foot - top) * 0.55
        rod(al, top, mid + d * 0.02, 0.0105, 10)                                           # upper section
        rod(al, mid, foot - d * 0.02, 0.0078, 10)                                          # lower section
        # flag lock: a collar at the end of the upper section and a lever outside
        lk = axis_frame(mid - d * 0.02, d)
        lathe(bk, [(0.0105, 0.0), (0.0145, 0.004), (0.0145, 0.038), (0.0080, 0.044)], 10, lk)
        side = rad - d * rad.dot(d)
        side.normalize()
        lv = g.Frame(tuple(mid - d * 0.004 + side * 0.016), tuple(side.cross(d)), tuple(d), tuple(side))
        g.box(bk, -0.007, 0.007, -0.006, 0.040, -0.003, 0.003, frame=lv)
        # rubber heel
        lathe(rb, [(0.0040, 0.0), (0.0105, 0.004), (0.0120, 0.012), (0.0110, 0.024), (0.0085, 0.030)], 10,
              axis_frame(foot, -d), cap0=True)
        # brace from the column
        rod(bk, (cx + 0.016 * rad.x, RY + 0.016 * rad.y, TZ_BRACE), tuple(top + (foot - top) * 0.40), 0.0035, 6)
    if lod == 1:
        return parts
    ch = P("tripod%d_steel" % i, "steel")
    for a in angles:
        g.cyl(ch, (LUG_R, 0.0, 0.715), "y", 0.0045, 0.030, 8, frame=turn(cx, RY, 0.0, math.degrees(a)))
    parts.append(ch)
    # brace clamp on the column, the column lock on the spider (between the legs), the head lock and handle
    lathe(bk, [(0.012, 0.0), (0.018, 0.003), (0.018, 0.017), (0.012, 0.020)], 10,
          g.Frame((cx, RY, TZ_BRACE - 0.010), (1, 0, 0), (0, 1, 0), (0, 0, 1)))
    a = math.radians(deg + 30)
    rad = Vector((math.cos(a), math.sin(a), 0.0))
    o = Vector((cx, RY, (TZ_SPIDER[0] + TZ_SPIDER[1]) / 2)) + rad * 0.036
    fr = axis_frame(o, rad)
    lathe(bk, [(0.0035, 0.0), (0.0035, 0.010)], 6, fr)
    knurl(bk, axis_frame(o + rad * 0.010, rad), 0.010, 0.0012, 8, 0.0, 0.009)
    # head handle: a rod from the front end of the tilt axis forward-sideways and slightly down, a rubber
    # grip; the axis lock is at the rear end
    ax = Vector(up.v)
    c = Vector(up.p(0.0, 0.0, TZ_TILT + 0.008))
    a = math.radians(deg - 70)
    hd = Vector((math.cos(a), math.sin(a), -0.12)).normalized()
    h0 = c - ax * 0.030
    rod(bk, h0, h0 + hd * 0.11, 0.0055, 8)
    lathe(rb, [(0.0060, 0.0), (0.0085, 0.006), (0.0090, 0.060), (0.0075, 0.072), (0.0040, 0.076)], 10,
          axis_frame(h0 + hd * 0.10, hd), cap1=True)
    knurl(bk, axis_frame(c + ax * 0.034, ax), 0.011, 0.0012, 8, 0.0, 0.010)
    # the plate is taped to the rail with silver tape - crooked
    tp = P("tripod%d_tape" % i, "tape")
    fr = turn(cx, RY, 0.0, 6.0 if i else -8.0)
    g.box(tp, -0.018, 0.018, -RHW - 0.0015, RHW + 0.0015, TZ_PLATE - 0.002, RZ1 + 0.0015, frame=fr, r=0.0012, seg=1)
    parts.append(tp)
    return parts


# =============================================================================
# Photosensor frames: a body on the rail, V rods, a crossbar (U), a visor
# =============================================================================
def build_frames(spec):
    lod, n = spec["lod"], spec["sides"]
    parts = []
    for i, fx in enumerate(FX):
        hs = P("frame%d_housing" % i, "housing", uv_name="frame_housing", uv_origin=(fx, 0, 0))
        g.box(hs, fx - F_HX, fx + F_HX, RY - F_HY, RY + F_HY, RZ1, F_Z1, **bev(lod, 0.006))
        parts.append(hs)
        # "ready" LED on the face of the body, in a holder
        lx, lz = fx + 0.024, RZ1 + 0.029
        ld = P("frame%d_led" % i, "led_g", group=SEL_LAMP, uv_name="frame_led", uv_origin=(fx, 0, 0))
        if lod == 2:
            front_quad(ld, lx - 0.006, lx + 0.006, lz - 0.005, lz + 0.005, RY - F_HY - 0.001)
        else:
            lathe(ld, [(0.0032, 0.0), (0.0032, 0.0025), (0.0024, 0.0040), (0.0010, 0.0047)], 10 if lod == 0 else 5,
                  axis_frame((lx, RY - F_HY, lz), (0, -1, 0)), cap1=True)
        parts.append(ld)
        rd = P("frame%d_rods" % i, "rods", uv_name="frame_rods", uv_origin=(fx, 0, 0))
        rs = 8 if lod == 0 else (5 if lod == 1 else 3)
        for s in (-1, 1):
            rod(rd, (fx, RY + s * ROD_Y, F_Z1 - 0.004), (fx, RY + s * F_TOPHW, F_TOP), 0.0032, rs)
        if lod < 2:
            rod(rd, (fx, RY - F_TOPHW - 0.004, F_TOP), (fx, RY + F_TOPHW + 0.004, F_TOP), 0.0032, rs)
        parts.append(rd)
        # diffuser visor on top, turned crooked
        hx, hy, zt = L.F_SHADE
        sh = P("frame%d_shade" % i, "diffuser")
        fr = turn(fx, RY, 0.0, FRAME_TILT[i])
        if lod == 2:
            g.quad(sh, [fr.p(-hx, -hy, zt), fr.p(hx, -hy, zt), fr.p(hx, hy, zt), fr.p(-hx, hy, zt)])
        else:
            g.box(sh, -hx, hx, -hy, hy, zt - 0.003, zt, frame=fr, **(dict(r=0.0012, seg=1) if lod == 0 else {}))
        parts.append(sh)
        if lod == 2:
            continue
        # sensor window on top of the body - in a frame
        ln = P("frame%d_window" % i, "lens", uv_name="frame_window", uv_origin=(fx, 0, 0))
        g.box(ln, fx - 0.012, fx + 0.012, RY - 0.024, RY + 0.024, F_Z1 - 0.0005, F_Z1 + 0.0008)
        parts.append(ln)
        cl = P("frame%d_clips" % i, "black", uv_name="frame_clips", uv_origin=(fx, 0, 0))
        for a0, a1, b0, b1 in ((-0.016, 0.016, -0.028, -0.024), (-0.016, 0.016, 0.024, 0.028),
                               (-0.016, -0.012, -0.024, 0.024), (0.012, 0.016, -0.024, 0.024)):
            g.box(cl, fx + a0, fx + a1, RY + b0, RY + b1, F_Z1 - 0.0005, F_Z1 + 0.0018)
        for s in (-1, 1):
            y = RY + s * F_TOPHW
            g.box(cl, fx - 0.009, fx + 0.009, y - 0.009, y + 0.009, F_TOP - 0.012, L.F_SHADE[2] - 0.003)
        if lod == 0:
            # rod sockets, a thumbscrew clamp to the rail, face screws
            for s in (-1, 1):
                b = Vector((fx, RY + s * ROD_Y, F_Z1 - 0.002))
                d = (Vector((fx, RY + s * F_TOPHW, F_TOP)) - b).normalized()
                lathe(cl, [(0.0065, 0.0), (0.0065, 0.014), (0.0045, 0.019)], 10, axis_frame(b, d))
            g.box(cl, fx - 0.02, fx + 0.02, RY - RHW - 0.004, RY - RHW, RZ1 - 0.026, RZ1, r=0.0015, seg=1)
            o = Vector((fx, RY - RHW - 0.004, RZ1 - 0.013))
            lathe(cl, [(0.0030, 0.0), (0.0030, 0.006)], 8, axis_frame(o, (0, -1, 0)))
            knurl(cl, axis_frame(o + Vector((0, -0.006, 0)), (0, -1, 0)), 0.0095, 0.0012, 8, 0.0, 0.008)
        parts.append(cl)
        if lod == 0:
            ch = P("frame%d_bnc" % i, "chrome", uv_name="frame_bnc", uv_origin=(fx, 0, 0))
            o = Vector((fx, RY + F_HY, BNC_Z))
            bnc_jack(ch, o, (0, 1, 0), lod)
            for sx in (-1, 1):
                for z in (RZ1 + 0.009, F_Z1 - 0.009):
                    g.cyl(ch, (fx + sx * 0.031, RY - F_HY - 0.0004, z), "y", 0.0022, 0.0012, 6)
            parts.append(ch)
            # LED holder
            bz = P("frame%d_ledring" % i, "chrome", uv_name="frame_ledring", uv_origin=(fx, 0, 0))
            lathe(bz, [(0.0034, 0.0), (0.0050, 0.0006), (0.0050, 0.0018), (0.0034, 0.0026)], 12,
                  axis_frame((lx, RY - F_HY, lz), (0, -1, 0)))
            parts.append(bz)
    return parts


# =============================================================================
# V-stop at the start, catcher bag at the end
# =============================================================================
def build_rest(spec):
    lod = spec["lod"]
    vx = L.VX
    al = P("rest_alu", "alu")
    g.box(al, vx - 0.03, L.REST_X1, RY - 0.02, RY + 0.02, RZ1, RZ1 + 0.006, **bev(lod, 0.0015))   # plate on the rail
    g.box(al, vx - 0.01, vx + 0.01, RY - 0.01, RY + 0.01, RZ1 + 0.006, 0.952, **bev(lod, 0.002))  # post
    vb = P("rest_v", "rubber")
    if lod == 2:
        g.box(vb, vx - 0.03, vx + 0.03, RY - 0.045, RY + 0.045, 0.950, 0.99)
        return [al, vb]
    # rubber V-block: a cradle with rounded tops and a rounded bottom of the notch
    poly = [(RY - 0.045, 0.950), (RY + 0.045, 0.950), (RY + 0.045, 0.999), (RY + 0.042, 1.004), (RY + 0.035, 1.006),
            (RY + 0.031, 1.004), (RY + 0.005, 0.977), (RY, 0.9745), (RY - 0.005, 0.977), (RY - 0.031, 1.004),
            (RY - 0.035, 1.006), (RY - 0.042, 1.004), (RY - 0.045, 0.999)]
    g.prism(vb, poly if lod == 0 else [poly[i] for i in (0, 1, 2, 4, 7, 10, 12)], (1, 2), vx - 0.03, vx + 0.03)
    parts = [al, vb]
    if lod > 0:
        return parts
    bk = P("rest_black", "black")
    g.box(bk, vx - 0.016, vx + 0.016, RY - 0.016, RY + 0.016, RZ1 + 0.006, RZ1 + 0.03, r=0.002, seg=1)  # post clamp
    o = Vector((vx, RY - 0.016, RZ1 + 0.018))
    lathe(bk, [(0.0030, 0.0), (0.0030, 0.006)], 8, axis_frame(o, (0, -1, 0)))
    knurl(bk, axis_frame(o + Vector((0, -0.006, 0)), (0, -1, 0)), 0.011, 0.0012, 10, 0.0, 0.009)
    g.box(bk, vx - 0.032, vx + 0.032, RY - 0.047, RY + 0.047, 0.946, 0.951, r=0.0015, seg=1)       # block platform
    parts.append(bk)
    tp = P("rest_tape", "tape")
    for x0, x1 in (L.REST_TAPE,):
        g.box(tp, x0, x1, RY - 0.0215, RY + 0.0215, RZ0 - 0.0015, RZ1 + 0.0075, r=0.0015, seg=1)
    parts.append(tp)
    return parts


def sandbag(part, fr, hx, hy, h, nu, nv):
    """Half-filled sandbag - a smooth "pillow" in axes fr (u is thickness, v is width, n is up, the bottom
    at n = 0): in plan a superellipse (a rectangle with rounded corners), the bottom settled and spread
    over the board, narrower and crumpled at the top, gentle folds on the sides. The top pole is a small
    ring for the neck."""
    bm = part.bm
    rings = []
    for i in range(nv + 1):
        th = -math.pi / 2 + math.pi * (i + 0.5) / (nv + 1)
        s, c = math.sin(th), abs(math.cos(th))
        rho = c ** (0.22 if s < 0 else 0.40)
        z = 0.0 if i == 0 else h * (0.5 + 0.5 * math.copysign(abs(s) ** 0.75, s))
        tz = z / h
        bulge = 1.0 + 0.07 * (1.0 - tz) - 0.05 * tz * tz
        ring = []
        for k in range(nu):
            ph = 2 * math.pi * k / nu
            cp, sp = math.cos(ph), math.sin(ph)
            fold = 1.0 + (0.045 * math.sin(3 * ph + 1.3 + 2.0 * tz) + 0.025 * math.sin(5 * ph + 0.4)) * math.sin(math.pi * tz)
            r = rho * bulge * fold
            x = hx * r * math.copysign(abs(cp) ** 0.7, cp)
            y = hy * r * math.copysign(abs(sp) ** 0.7, sp)
            dz = 0.012 * math.sin(2 * ph + 0.7) * tz ** 3
            ring.append(bm.verts.new(fr.p(x, y, z + dz)))
        rings.append(ring)
    new = []
    for i in range(nv):
        for k in range(nu):
            j = (k + 1) % nu
            q = [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]
            c = sum((v.co for v in q), Vector()) / 4 - fr.o
            new.append(face(part, q, Vector(c) - fr.n * (h * 0.45)))
    new.append(face(part, rings[0], -fr.n))
    new.append(face(part, rings[-1], fr.n))
    bm.normal_update()
    part.tag(new)
    top = sum((v.co for v in rings[-1]), Vector()) / nu
    return top


def build_catcher(spec):
    lod = spec["lod"]
    parts = []
    x0, x1, y0, y1, z0, z1 = L.BOARD
    if lod < 2:
        wd = P("board", "wood")
        g.box(wd, x0, x1, y0, y1, z0, z1, **bev(lod, 0.002))
        parts.append(wd)
    if lod == 0:
        # angle under the board: a shelf under the rail and a post to the board, two bolts into the rail
        al = P("board_bracket", "alu")
        g.box(al, 0.62, x1 - 0.005, RY - 0.012, RY + 0.012, RZ0 - 0.004, RZ0, r=0.001, seg=1)
        g.box(al, x1 - 0.02, x1 - 0.005, RY - 0.012, RY + 0.012, RZ0 - 0.004, z0, r=0.001, seg=1)
        parts.append(al)
        bt = P("board_bolts", "steel")
        for x in (0.64, 0.685):
            g.cyl(bt, (x, RY, RZ0 - 0.0055), "z", 0.0055, 0.003, 6)
        parts.append(bt)
    bx0, bx1, by0, by1, bz0, bz1 = L.BAG
    bg = P("sandbag", "sandbag")
    fr = turn((bx0 + bx1) / 2, (by0 + by1) / 2, bz0, 5.0)
    hx, hy, h = (bx1 - bx0) / 2, (by1 - by0) / 2, bz1 - bz0 - 0.02
    if lod == 2:
        g.box(bg, -hx, hx, -hy, hy, 0.0, h, frame=fr)
        parts.append(bg)
        return parts
    top = sandbag(bg, fr, hx, hy, h, 20 if lod == 0 else 10, 9 if lod == 0 else 5)
    parts.append(bg)
    if lod == 0:
        # neck: gathered, tied with a cord and folded over as a flat tail onto the top, toward the barrel
        o = Vector(top)
        n_, u_ = Vector(fr.n), Vector(fr.u)
        pts = [o - n_ * 0.010, o + n_ * 0.010, o + n_ * 0.020 - u_ * 0.010, o + n_ * 0.016 - u_ * 0.030,
               o + n_ * 0.004 - u_ * 0.050]
        rad = [(0.024, 0.024), (0.013, 0.013), (0.020, 0.012), (0.030, 0.008), (0.034, 0.005)]
        sp = spline([tuple(p) for p in pts], 3)
        rr = []
        for k in range(len(sp)):
            f = k / (len(sp) - 1) * (len(rad) - 1)
            a = min(int(f), len(rad) - 2)
            t = f - a
            rr.append(tuple(rad[a][j] * (1 - t) + rad[a + 1][j] * t for j in range(2)))
        g.tube_var(bg, sp, rr, 10)
        cd = P("sandbag_cord", "cord")
        c = o + n_ * 0.009
        ring = [tuple(c + u_ * (0.0150 * math.cos(2 * math.pi * k / 12)) +
                      Vector(fr.v) * (0.0150 * math.sin(2 * math.pi * k / 12))) for k in range(13)]
        g.pipe(cd, ring, 0.0025, 6)
        g.pipe(cd, [ring[3], tuple(Vector(ring[3]) + Vector(fr.v) * 0.02 - Vector(fr.n) * 0.012),
                    tuple(Vector(ring[3]) + Vector(fr.v) * 0.028 - Vector(fr.n) * 0.035)], 0.0022, 6)
        parts.append(cd)
    return parts


# =============================================================================
# Pelican 1520 class case (bright green), laptop, interface unit
# =============================================================================
def pelican(body, hw, fr, size, lod):
    """Case with the bottom center at fr.o, facing -v: a body with rounded edges, a lid seam belt along the
    same outline, two double latches (a plate, a pivot at the bottom, a hook on the lid, a stop on the
    body), a folding handle on two supports, a valve with a knurled head (pelican() from M27, more
    detailed; no ribs on the lid - the laptop stands on it)."""
    Lx, D, H = size
    zs = H * 0.72
    g.box(body, -Lx / 2, Lx / 2, -D / 2, D / 2, 0.0, H, frame=fr,
          **(dict(r=0.012, seg=3) if lod == 0 else dict(r=0.012, seg=1) if lod == 1 else {}))
    if lod == 2:
        return
    g.prism(body, rrect(Lx / 2 + 0.004, D / 2 + 0.004, 0.016, 4 if lod == 0 else 1), (0, 1), zs - 0.006, zs + 0.006,
            frame=fr)
    if lod > 0:
        return
    for s in (-1, 1):                                                                  # latches
        xc = s * (Lx / 2 - 0.13 * Lx / 0.5)
        y0 = -D / 2
        g.box(hw, xc - 0.024, xc + 0.024, y0 - 0.006, y0 + 0.001, zs - 0.062, zs - 0.040, frame=fr)
        g.box(hw, xc - 0.021, xc + 0.021, y0 - 0.011, y0 - 0.003, zs - 0.046, zs + 0.026, frame=fr, r=0.003, seg=1)
        g.cyl(hw, tuple(fr.p(xc, y0 - 0.009, zs - 0.046)), "x", 0.0055, 0.046, 10)
        g.box(hw, xc - 0.015, xc + 0.015, y0 - 0.008, y0 + 0.001, zs + 0.018, zs + 0.034, frame=fr)
        for t in (-1, 1):                                                              # lock lugs
            g.box(hw, xc + t * 0.030 - 0.004, xc + t * 0.030 + 0.004, y0 - 0.009, y0 + 0.001, zs - 0.05, zs - 0.026,
                  frame=fr)
    for s in (-1, 1):                                                                  # handle supports
        g.box(hw, s * 0.075 - 0.009, s * 0.075 + 0.009, -D / 2 - 0.012, -D / 2 + 0.001, zs + 0.006, zs + 0.040,
              frame=fr, r=0.003, seg=1)
    g.box(hw, -0.068, 0.068, -D / 2 - 0.024, -D / 2 - 0.008, zs + 0.012, zs + 0.034, frame=fr, r=0.0065, seg=2)
    o = Vector(fr.p(Lx / 2 - 0.05, -D / 2, H * 0.4))                                   # valve
    lathe(hw, [(0.014, 0.0), (0.014, 0.002)], 16, axis_frame(o, (0, -1, 0)))
    knurl(hw, axis_frame(o + Vector((0, -0.002, 0)), (0, -1, 0)), 0.011, 0.0010, 10, 0.0, 0.006)


def build_case(spec):
    lod = spec["lod"]
    body = P("case", "case" if lod < 2 else "case_plain")
    hw = P("case_hw", "case_hw") if lod == 0 else None
    pelican(body, hw, turn(L.CASE_C[0], L.CASE_C[1], 0.0, 0.0), L.CASE, lod)
    parts = [body] + ([hw] if hw else [])
    if lod == 0:
        # lid hinge at the back - without decals (the far LOD takes green from it)
        hg = P("case_hinge", "case_plain")
        zs = CZ * 0.72
        g.box(hg, L.CX0 + 0.05, L.CX1 - 0.05, L.CY1 - 0.002, L.CY1 + 0.005, zs - 0.016, zs + 0.016, r=0.002, seg=1)
        g.cyl(hg, ((L.CX0 + L.CX1) / 2, L.CY1 + 0.007, zs), "x", 0.0065, L.CASE[0] - 0.11, 10)
        parts.append(hg)
    return parts


def build_laptop(spec):
    """ThinkPad 760 class laptop: the base (separate keys on the near LOD, a trackpoint and two buttons,
    the disk lamp - ozl_lamp, ports at the back and on the right, feet), the lid with the screen sunk
    into the frame, hinges, a latch."""
    lod = spec["lod"]
    reg = "laptop" if lod < 2 else "black"
    base = P("laptop_base", reg)
    g.box(base, L.LX0, L.LX1, L.LY0, L.LY1, CZ + (0.002 if lod == 0 else 0.0), LZ, **bev(lod, 0.004))
    lid = P("laptop_lid", reg)
    hw = L.LT_W / 2
    sa0, sa1, sb0, sb1 = -L.SCR_W / 2, L.SCR_W / 2, L.SCR_B0, L.SCR_B0 + L.SCR_H
    if lod == 2:
        g.box(lid, -hw, hw, -0.004, L.LT_D, -L.LT_L, 0.0, frame=LID)
        sc = P("laptop_screen", "lens")
        g.quad(sc, [LID.p(sa0, sb0, 0.0008), LID.p(sa1, sb0, 0.0008), LID.p(sa1, sb1, 0.0008), LID.p(sa0, sb1, 0.0008)])
        return [base, lid, sc]
    g.box(lid, -hw, hw, -0.004, L.LT_D, -L.LT_L, -SCR_IN, frame=LID, **bev(lod, 0.004))
    for a0, a1, b0, b1 in ((-hw, hw, -0.004, sb0), (-hw, hw, sb1, L.LT_D), (-hw, sa0, sb0, sb1), (sa1, hw, sb0, sb1)):
        g.box(lid, a0, a1, b0, b1, -SCR_IN - 0.001, 0.0, frame=LID)
    # screen: the own texture, the top 3/4 of the image (the bottom 1/4 is the unit display)
    sc = P("laptop_screen", "dark", group=SEL_SCREEN, section="screen")
    cs = -SCR_IN + 0.0006
    vs = [sc.bm.verts.new(LID.p(a, b, cs)) for a, b in ((sa0, sb0), (sa1, sb0), (sa1, sb1), (sa0, sb1))]
    sc.tag([face(sc, vs, LID.n)])
    sc.glass_frame = (LID, sa0, sa1, sb0 - (sb1 - sb0) * L.PANEL_SPLIT / (1 - L.PANEL_SPLIT), sb1)
    parts = [base, lid, sc]
    if lod > 0:
        return parts
    ky = P("laptop_keys", "key")
    for x0, x1, y0, y1 in L.key_rects():
        keycap(ky, x0 + 0.0003, x1 - 0.0003, y0 + 0.0003, y1 - 0.0003, LZ - 0.0005, LZ + 0.0027)
    parts.append(ky)
    tx, ty = L.track_xy()
    tr = P("laptop_track", "track_red")
    lathe(tr, [(0.0022, 0.0), (0.0022, 0.0040), (0.0030, 0.0046), (0.0030, 0.0056), (0.0020, 0.0062)], 10,
          g.Frame((tx, ty, LZ), (1, 0, 0), (0, 1, 0), (0, 0, 1)), cap1=True)
    parts.append(tr)
    bk = P("laptop_bits", "black")
    for s in (-1, 1):                                                                  # buttons under the space bar
        g.box(bk, tx + s * 0.004, tx + s * 0.027, L.KEYS[2] - 0.017, L.KEYS[2] - 0.005, LZ - 0.0005, LZ + 0.0012,
              r=0.0008, seg=1)
    for s in (-1, 1):                                                                  # hinges
        g.cyl(bk, tuple(LID.p(s * 0.11, 0.0, -0.009)), "x", 0.0085, 0.042, 12)
    g.box(bk, -0.02, 0.02, L.LT_D - 0.008, L.LT_D - 0.003, -0.0005, 0.0012, frame=LID)  # lid latch
    for sx in (L.LX0 + 0.02, L.LX1 - 0.032):                                          # feet
        for sy in (L.LY0 + 0.02, L.LY1 - 0.032):
            g.box(bk, sx, sx + 0.012, sy, sy + 0.012, CZ, CZ + 0.0025)
    # ports: power and ports at the back, serial on the right, a grille on the left
    for a, b in ((DC_X - 0.008, DC_X + 0.008), (L.LX0 + 0.08, L.LX0 + 0.13), (L.LX0 + 0.15, L.LX0 + 0.19)):
        g.box(bk, a, b, L.LY1 - 0.0005, L.LY1 + 0.0010, CZ + 0.009, CZ + 0.026)
    g.box(bk, L.LX1 - 0.0005, L.LX1 + 0.0010, SER_Y_LAP - 0.017, SER_Y_LAP + 0.017, CZ + 0.010, CZ + 0.025)
    for k in range(5):
        yk = L.LY0 + 0.06 + k * 0.014
        g.box(bk, L.LX0 - 0.0010, L.LX0 + 0.0005, yk, yk + 0.006, CZ + 0.012, CZ + 0.028)
    parts.append(bk)
    hd = P("laptop_hdd_led", "led_g", group=SEL_LAMP)
    g.box(hd, L.LX1 - 0.0085, L.LX1 - 0.0045, L.KEYS[3] - 0.016, L.KEYS[3] - 0.008, LZ - 0.0004, LZ + 0.0007)
    parts.append(hd)
    return parts


def build_box(spec):
    """Homemade interface unit in a cast case: a lid on four screws, a display in a frame (own texture,
    the bottom quarter of the screen image), an LED in a holder, a toggle, two BNC jacks at the back,
    DB-9 on the left side, feet."""
    lod = spec["lod"]
    x0, x1, y0, y1, z0, z1 = L.BOX
    bx = P("ibox", "box")
    g.box(bx, x0, x1, y0, y1, z0 + (0.002 if lod == 0 else 0.0), z1 - (0.004 if lod == 0 else 0.0), **bev(lod, 0.004))
    lx0, lx1, lz0, lz1 = L.BOX_LCD
    lx, lz = L.BOX_LED
    ld = P("ibox_led", "led_r", group=SEL_LAMP)
    if lod == 2:
        lc = P("ibox_lcd", "lens")
        front_quad(lc, lx0, lx1, lz0, lz1, y0 - 0.0008)
        front_quad(ld, lx - 0.004, lx + 0.004, lz - 0.004, lz + 0.004, y0 - 0.001)
        return [bx, lc, ld]
    lc = P("ibox_lcd", "dark", group=SEL_SCREEN, section="screen")
    yq = y0 - 0.0004
    vs = [lc.bm.verts.new(q) for q in ((lx0, yq, lz0), (lx1, yq, lz0), (lx1, yq, lz1), (lx0, yq, lz1))]
    lc.tag([face(lc, vs, (0, -1, 0))])
    lc.glass_frame = (FRONT, lx0, lx1, lz0, lz0 + (lz1 - lz0) / L.PANEL_SPLIT)
    lathe(ld, [(0.0030, 0.0), (0.0030, 0.0022), (0.0022, 0.0036), (0.0010, 0.0042)], 10 if lod == 0 else 5,
          axis_frame((lx, y0, lz), (0, -1, 0)), cap1=True)
    parts = [bx, lc, ld]
    if lod > 0:
        return parts
    g.box(bx, x0 - 0.0006, x1 + 0.0006, y0 - 0.0006, y1 + 0.0006, z1 - 0.005, z1, r=0.002, seg=1)  # lid
    bk = P("ibox_black", "black")
    for a0, a1, b0, b1 in ((lx0 - 0.003, lx1 + 0.003, lz0 - 0.003, lz0), (lx0 - 0.003, lx1 + 0.003, lz1, lz1 + 0.003),
                           (lx0 - 0.003, lx0, lz0, lz1), (lx1, lx1 + 0.003, lz0, lz1)):
        g.box(bk, a0, a1, y0 - 0.0015, y0 + 0.0005, b0, b1)
    for sx in (x0 + 0.012, x1 - 0.022):                                                # feet
        for sy in (y0 + 0.01, y1 - 0.02):
            g.box(bk, sx, sx + 0.01, sy, sy + 0.01, z0, z0 + 0.0025)
    # DB-9 on the left side: a block for the plug
    g.box(bk, x0 - 0.0012, x0 + 0.0005, SER_Y_BOX - 0.016, SER_Y_BOX + 0.016, SER_Z - 0.007, SER_Z + 0.007)
    parts.append(bk)
    ch = P("ibox_hw", "chrome")
    for sx in (x0 + 0.007, x1 - 0.007):                                                # lid screws
        for sy in (y0 + 0.007, y1 - 0.007):
            g.cyl(ch, (sx, sy, z1 + 0.0005), "z", 0.0028, 0.001, 6)
    lathe(ch, [(0.0034, 0.0), (0.0048, 0.0006), (0.0048, 0.0016), (0.0034, 0.0024)], 12,
          axis_frame((lx, y0, lz), (0, -1, 0)))                                       # LED holder
    # toggle: nut, bushing, a lever with a ball, tilted toward +x
    tx, ty = 0.20, -0.095
    g.cyl(ch, (tx, ty, z1 + 0.0015), "z", 0.0058, 0.003, 6)
    g.cyl(ch, (tx, ty, z1 + 0.005), "z", 0.0034, 0.004, 10)
    lv = axis_frame((tx, ty, z1 + 0.006), (math.sin(math.radians(18)), 0.0, math.cos(math.radians(18))))
    lathe(ch, [(0.0016, 0.0), (0.0019, 0.010), (0.0026, 0.0115), (0.0026, 0.0135), (0.0014, 0.0145)], 8, lv, cap1=True)
    for x in BOX_BNC:
        bnc_jack(ch, (x, y1, BOX_BNC_Z), (0, 1, 0), lod)
    parts.append(ch)
    return parts


# =============================================================================
# Wires and tape: the frame cables along the rail at the back, down to the unit; the unit - the
# laptop; the laptop power along the floor back to the power supply, from it a cord with a plug
# =============================================================================
def build_wires(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    ch, bt = P("plugs_chrome", "chrome"), P("plugs_boot", "black")
    yb = L.BOX[3]
    ends = []
    for i, fx in enumerate(FX):
        o = (fx, RY + F_HY, BNC_Z)
        e0 = bnc_plug(ch, bt, o, (0, 1, 0), lod) if lod == 0 else o
        e1 = (bnc_plug(ch, bt, (BOX_BNC[i], yb, BOX_BNC_Z), (0, 1, 0), lod) if lod == 0
              else (BOX_BNC[i], yb, BOX_BNC_Z))
        ends.append((e0, e1))
    (a0, b0), (a1, b1) = ends
    s0, s1 = 1, -1
    # frame cable: from the plug back, down under the frame body, to the rear side of the rail, along it
    # under the tape, from the free end of the rail with a sag down onto the case lid, under tape and into
    # the back of the unit
    pts0 = [a0, (FX[0], 0.146, BNC_Z - 0.006), (FX[0] + s0 * 0.012, 0.128, RZ1 - 0.006),
            (FX[0] + s0 * 0.040, 0.092, CABLE_Z[0] + 0.002), (-0.52, YC, CABLE_Z[0]), (-0.42, YC, CABLE_Z[0]),
            (-0.17, YC, CABLE_Z[0]), (0.04, YC, CABLE_Z[0]), (0.105, YC + 0.004, 0.828), (0.125, YC - 0.006, 0.70),
            (0.13, 0.03, 0.48), (0.13, 0.008, 0.30), (0.13, 0.004, 0.205), (0.13, -0.012, CZ + 0.0035),
            (0.13, -0.026, CZ + 0.010), (0.13, -0.034, BOX_BNC_Z - 0.004), b0]
    pts1 = [a1, (FX[1], 0.146, BNC_Z - 0.006), (FX[1] + s1 * 0.012, 0.128, RZ1 - 0.006),
            (FX[1] + s1 * 0.040, 0.092, CABLE_Z[1] + 0.002), (0.52, YC, CABLE_Z[1]), (0.40, YC, CABLE_Z[1]),
            (0.32, YC, CABLE_Z[1]), (0.22, YC, CABLE_Z[1]), (0.172, YC + 0.006, 0.818), (0.176, YC + 0.004, 0.66),
            (0.178, 0.034, 0.46), (0.172, 0.010, 0.30), (0.17, 0.006, 0.205), (0.17, -0.012, CZ + 0.0035),
            (0.17, -0.026, CZ + 0.010), (0.17, -0.034, BOX_BNC_Z - 0.004), b1]
    parts += cable("cable_frame0", "cable", pts0, 0.0035, lod, k=2)
    parts += cable("cable_frame1", "cable", pts1, 0.0035, lod, k=2)
    # serial: a DB-9 plug in the laptop side - an S-shape over the case lid - a plug in the unit side
    pl = P("plugs_db9", "black")
    parts.append(pl)
    xa, xb = L.LX1, L.BOX[0]
    for x, s, y in ((xa, 1, SER_Y_LAP), (xb, -1, SER_Y_BOX)):
        g.box(pl, *sorted((x, x + s * 0.008)), y - 0.0155, y + 0.0155, SER_Z - 0.0065, SER_Z + 0.0065,
              **(dict(r=0.0015, seg=1) if lod == 0 else {}))
        if lod == 0:
            for t in (-1, 1):                                                          # plug screws
                g.cyl(ch, (x + s * 0.010, y + t * 0.0125, SER_Z), "x", 0.0022, 0.004, 8)
            lathe(pl, [(0.0045, 0.0), (0.0042, 0.004), (0.0034, 0.006)], 8,
                  axis_frame((x + s * 0.008, y, SER_Z), (s, 0, 0)), cap1=True)
    xm = (xa + xb) / 2
    sa, sb = (xa + 0.013, SER_Y_LAP, SER_Z), (xb - 0.013, SER_Y_BOX, SER_Z)
    pts = [sa, (xm, SER_Y_LAP - 0.006, CZ + 0.008), (xm, (SER_Y_LAP + SER_Y_BOX) / 2, CZ + 0.003),
           (xm, SER_Y_BOX + 0.006, CZ + 0.008), sb]
    parts += cable("cable_serial", "cable_grey", pts, 0.003, lod)
    # laptop power: a plug in the back of the base, over the case edge to the floor, back to the power supply
    fr = axis_frame((DC_X, L.LY1, CZ + 0.0175), (0, 1, 0))
    if lod == 0:
        lathe(pl, [(0.0048, 0.0), (0.0048, 0.012), (0.0040, 0.016), (0.0034, 0.024)], 10, fr, cap1=True)
    s = Vector(fr.p(0, 0, 0.022))
    # power supply: center BRICK, axis bu - from the laptop cord inlet to the mains cord outlet
    bc, bu = Vector(BRICK), Vector(BRICK_U).normalized()
    b_in, b_out = bc - bu * 0.068 + Vector((0, 0, 0.012)), bc + bu * 0.068 + Vector((0, 0, 0.012))
    pts = [tuple(s), (DC_X - 0.004, L.LY1 + 0.034, CZ + 0.008), (DC_X - 0.02, L.CY1 - 0.016, CZ + 0.0035),
           (DC_X - 0.034, L.CY1 + 0.008, CZ - 0.012), (DC_X - 0.042, L.CY1 + 0.024, 0.09), (DC_X - 0.058, L.CY1 + 0.05, 0.004),
           tuple(b_in - bu * 0.03 + Vector((0, 0, -0.0088))), tuple(b_in)]
    parts += cable("cable_power", "cable", pts, 0.003, lod)
    if lod > 0:
        return [p for p in parts if len(p.bm.faces)]
    br = P("power_brick", "black")
    fb = g.Frame(tuple(bc), tuple(bu), (-bu.y, bu.x, 0.0), (0, 0, 1))
    g.box(br, -0.05, 0.05, -0.03, 0.03, 0.0, 0.032, r=0.005, seg=1, frame=fb)
    for u in (-1, 1):                                                                  # cord strain reliefs
        lathe(br, [(0.0065, 0.0), (0.0060, 0.008), (0.0040, 0.018)], 8,
              axis_frame(fb.p(u * 0.05, 0.0, 0.012), tuple(bu * u)), cap1=True)
    parts.append(br)
    # mains cord: on the floor back and left behind a tripod leg, the plug lies on its side
    ep = axis_frame((-0.60, 0.338, 0.0165), (-1.0, -0.12, 0.0))
    e = Vector(ep.p(0, 0, -0.010))
    pts = [tuple(b_out), tuple(b_out + bu * 0.03 + Vector((0, 0, -0.0088))), (-0.43, 0.352, 0.0035),
           (-0.50, 0.362, 0.0035), (-0.56, 0.348, 0.0035), (e.x + 0.012, e.y, 0.012), tuple(e)]
    parts += cable("cable_mains", "cable", pts, 0.0035, lod)
    lathe(br, [(0.0040, -0.012), (0.0110, -0.004), (0.0165, 0.006), (0.0165, 0.034), (0.0120, 0.040)], 12, ep, cap1=True)
    for t in (-1, 1):                                                                  # plug pins
        g.pipe(ch, [tuple(ep.p(t * 0.0095, 0.0, 0.038)), tuple(ep.p(t * 0.0095, 0.0, 0.057))], 0.0020, 6)
    # turns of tape over the cables along the rail: silver and one blue
    for k, x in enumerate(L.TAPE_X):
        tp = P("rail_tape%d" % k, "tape_blue" if k == 3 else "tape")
        fr = turn(x, RY, 0.0, (-7.0, 4.0, 9.0, -5.0)[k])
        g.box(tp, -L.TAPE_W / 2, L.TAPE_W / 2, -RHW - 0.0012, YC - RY + 0.0047, RZ0 - 0.0012, RZ1 + 0.0012, frame=fr,
              r=0.0012, seg=1)
        parts.append(tp)
    # cables are pressed to the case lid by the unit with tape: a hump of tape over both
    tp = P("case_tape", "tape")
    fr = turn(0.150, -0.012, CZ, 12.0)
    g.box(tp, -0.03, 0.03, -0.011, 0.011, 0.0, 0.0078, frame=fr, r=0.003, seg=1)
    parts.append(tp)
    parts += [ch, bt]
    return [p for p in parts if len(p.bm.faces)]


def build_lod(spec):
    parts = build_rail(spec) + build_tripod(0, spec) + build_tripod(1, spec) + build_frames(spec)
    parts += build_rest(spec) + build_catcher(spec) + build_case(spec) + build_laptop(spec) + build_box(spec)
    parts += build_wires(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """One box by the extent: a component thinner than 0.5 m does not work in the engine, and between the
    tripods under the rail the case and the laptop stand anyway."""
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    y0, y1 = min(lo[1], -0.26), max(hi[1], 0.26)
    box = kx.box_pts(lo[0], hi[0], y0, y1, 0.0, hi[2])
    comps = [(box, kx.PEN + r"\metalplate.rvmat")]
    memory = {
        "invView": [(0.0, -2.3, 1.2)],
        "ce_center": [(0.0, 0.0, 0.6)],
        "ce_radius": [(1.0, 0.0, 0.6)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2] + 0.004)
    return comps, 60.0, memory, bbox


def decor_report():
    """--stats: extents of the vanilla items (kv.corners) - not hanging, not sinking, not intersecting."""
    boxes = []
    for d in DECOR:
        q = kv.corners(d[5], d[1], d[2], d[3])
        lo = tuple(min(c[i] for c in q) for i in range(3))
        hi = tuple(max(c[i] for c in q) for i in range(3))
        boxes.append((d[5], lo, hi))
        print("decor %-12s x %.3f..%.3f  y %.3f..%.3f  z %.3f..%.3f" % (d[5], lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if all(a[1][k] < b[2][k] - 1e-4 and b[1][k] < a[2][k] - 1e-4 for k in range(3)):
                print("decor overlap:", a[0], b[0])


# the first ones are for the --look preview: the laptop and the unit (the same when "working"), overall,
# a frame with the bag, the stop, the case with small stuff
SHOTS = [
    ("laptop", (-0.10, -0.80, 0.72), (-0.02, -0.06, 0.26), 34),
    ("front", (-0.7, -2.5, 1.55), (0.0, 0.05, 0.62), 32),
    ("frame", (1.05, -0.85, 1.28), (0.58, 0.05, 1.0), 34),
    ("rest", (-1.25, -0.75, 1.22), (-0.62, 0.05, 0.86), 34),
    ("case", (0.55, -1.05, 0.55), (0.06, -0.06, 0.12), 30),
    ("head", (-0.30, -0.62, 1.02), (-0.50, 0.05, 0.76), 36),
    ("floor", (0.95, -0.95, 0.75), (0.25, 0.0, 0.05), 32),
    ("right", (1.9, -0.9, 1.05), (0.15, 0.05, 0.6), 32),
    ("top", (0.2, -1.0, 2.3), (0.0, 0.05, 0.6), 30),
    ("back", (1.3, 2.1, 1.5), (0.0, 0.05, 0.6), 32),
]

if "--stats" in kmodel.ARGV:
    decor_report()
M.look_shots = (5, 1)
M.run(build_lod, collision, SHOTS, row_step=1.9, row_shot=((1.9, -6.4, 1.8), (1.9, 0, 0.6)))
