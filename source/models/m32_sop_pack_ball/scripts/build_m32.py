"""M32 - the SOP weapon cabinet: the SOP Ballistics Packer (OZL_Sop_Pack_Ball). A packer:
cargo 10x10, three module places on a folding table (module_1..3) and proxies for the
modules at the same places. Each module of the line has its own slot and its own working
place: slot 1 - the M81 barrel vise where the clamp vise used to be (a steel plate on four
bolts at the left front corner of the table), slot 2 - the M82 borescope in the middle of
the back row, slot 3 - the M83 gauge set where the pencil case was (the case moved to the
shelf above, next to the ammo boxes).

    blender --background --python build_m32.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: make_decals.py with the system Python (the door number, the crate
stripes). Positions are in layout.py (shared with make_decals.py), primitives in m32_geo.py.

Look: "dayz" (matte, dirtier, colored AO). There is no built-in vise - slot 1 is empty: a
plate on bolts and worn-off paint around it; slots 2 and 3 are empty - clean patches on the
worn table sheet where a case and a box usually stand. The scope has its own PSO-1 (pso1.py,
shared with M23 and M27: a shape from the specs and photos, its own material - black
shagreen enamel worn to metal, rubber, an aluminium scale, lenses as a glass section)
because the vanilla scope proxies render white in our model; it stands on the mat on its
bracket. Small items are vanilla proxy things (kvanilla): a weapon cleaning kit, an RPK
magazine, an SKS clip and loose 7.62 x 39 on the table; two boxes of 7.62 x 39 next to the
pencil case on the shelf, a flashlight and insulating tape on the wooden box, rags on the
crates below. The own parts are more detailed: weapon covers following the silhouette of
an assault rifle (butt, neck, magazine, forend, barrel) with a strap and a tie, steel boxes
and a briefcase with rounded edges and smooth handles, a suppressor with grooves and ends,
a lamp with a ribbed body and a cable to a junction box on the cabinet back (the cable is a
smooth curve), on the right door inside a rod lock (rods in guides), on the left one bolts,
on the opening an alarm sensor with an LED.

The cabinet is the shared cabinet base (kcabinet.cabinet, moved into the library by this
model; M34 uses it too): an army steel two-door cabinet 1.00 x 1.90 x 0.50 m on a 6 cm
plinth, the doors open at 105 degrees, the lower border of the upper compartment is a
folding panel 0.96 x 0.50 on a piano hinge, lowered to the table at 0.85 m on two chains.
There is no public passport of a Soviet weapon cabinet (ShKhO / OSh); the dimensions come
from the card, the body from cabinets of the same design: ShMDO 900 x 1800 x 500 mm and a
two-tier rifle cabinet of UHL-MASH (plinth, shelves, cradles); the table on chains follows a
gun cleaning cabinet of Caron RAD GunWorks. The first SOP model, it sets the look for
M33-M36: the post-Soviet army, the equipment still Soviet; olive paint, worn on the door
edges, at the handle, on the table edge and the crate corners, in places touched up with
fresh olive; a red-brown primer under the worn olive, then metal; no rust (its own builder
build_worn with touch-ups, as in M23; kmats is left alone).

Contents (the dimensions where there is no passport are estimates from photos):
- on the left - a pyramid for four rifles: a lower cradle with sockets for the butts
  (felt), an upper comb with forend notches (pitch 0.115), a locking bar on a hinge with a
  padlock; two sockets hold weapons in canvas covers (no rifles themselves; the cover
  follows an AKM silhouette of 880 mm with a magazine), two are empty;
- on the right - shelves at 1.18 and 1.52: on the bottom one a 90s case (an aluminium
  briefcase with ribs, ~0.40 x 0.30 x 0.10 - Zero Halliburton class, an estimate), on the
  middle one two steel ammo boxes (belt boxes ~0.28 x 0.12 x 0.19) and the pencil case, on
  the top one a wooden box with a lid;
- above the pyramid a small shelf with a zinc can (~0.33 x 0.22 x 0.08);
- in the lower compartment - two wooden ammo crates stacked (~0.46 x 0.29 x 0.155) with
  stencil stripes, two more steel boxes on the right;
- on the doors inside: on the left a frame with an empty inventory list (paper without
  text) and bolts, on the right a canvas pouch on hooks and a rod lock; outside - a lever
  handle with a keyhole and a seal cup (right), the number "17" by stencil and a blank
  aluminium tag (left).
On the table - a canvas mat in the middle; on it the PSO-1 scope (own, pso1.py: 375 x 69 x
170 mm with the eyecup) stands on the bracket base, the bracket toward the person; in front
of it an assembled suppressor of the PBS-1 class (length 152 mm, dia ~40 - an estimate from
photos). At M23 (Duty) the same PSO-1 lies on a rag and the parts are in a tray.

Machine look: ozl_lamp - the shade of a jar-type lamp (NPP class, dia ~0.2) on a bracket
above the table, steady while working (atlas _on); ozl_led - the LED of the alarm sensor on
the opening, blinking while working (OZL_WorkFx blink). No moving parts; the modules in the
slots "work" together with the machine (their own OZL_Work).

Blender axes: X - width, Y - depth (front at -Y), Z - up.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kcabinet  # noqa: E402
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import kvanilla as kv  # noqa: E402
import kwood  # noqa: E402
import layout as L  # noqa: E402
import m32_geo as G  # noqa: E402
import pso1  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
X0, X1, Y0, Y1, H = L.X0, L.X1, L.Y0, L.Y1, L.H
ZT, TD = L.ZT, L.TD
XI0, XI1 = X0 + kcabinet.T, X1 - kcabinet.T
ZI0 = kcabinet.FOOT + kcabinet.T
YI1 = Y1 - kcabinet.T
XP = 0.0                                                     # pyramid left, shelves right
SHELVES = [(XP + 0.003, XI1, 1.18), (XP + 0.003, XI1, 1.52), (XI0, XP - 0.003, 1.76)]
PARTITIONS = [(XP, ZT, H - kcabinet.T)]
# pyramid: socket centers, the lower cradle and the upper comb
SLOTS = [XI0 + 0.0575 + 0.115 * k for k in range(4)]
RACK_Y = (0.20, 0.42)
COMB_Z = 1.40
# Module slots: 1 - the M81 vise plate at the left front corner (where the clamp vise was),
# 2 - the M82 borescope case in the back row, centered, 3 - the M83 gauge box on the right
# where the pencil case was. Modules are ~0.20-0.22 x 0.20 at the base, the origin is the
# base center
MOUNT = (0.15, 0.14, 0.006)                                  # plate: width, depth, thickness
S1 = (-0.315, -0.355)
MODS = [(S1[0], S1[1], ZT + MOUNT[2]), (0.0, -0.125, ZT), (0.330, -0.350, ZT)]
MOD_OBJ = [("m81_barrel_vise", "ozr_barrel_vise"), ("m82_borescope", "ozr_borescope"), ("m83_gauge_set", "ozr_gauge_set")]
CLEAN2 = (-0.115, 0.115, -0.215, -0.075)                     # M82 case stands here (lid behind)
CLEAN3 = (0.225, 0.435, -0.415, -0.285)                      # where the M83 box stands
# canvas mat in the middle of the front row - between slots 1 and 3, in front of slot 2
MAT = (-0.195, 0.215, -0.485, -0.235)
ZM = ZT + 0.004                                              # mat top
# PSO-1 (own, pso1.py): the middle of its extent is where the PSO-6 used to stand; the bracket
# base bottom is on the mat (the canvas there is 1.3-3.7 mm above the sheet); between the clip
# in front and the loose rounds behind; objective toward -x, bracket toward the person
SCOPE = (0.0, -0.345, ZT + 0.0025)
POSE = pso1.Pose(SCOPE[:2], 180.0, SCOPE[2])
SUPP = (-0.185, -0.452)                                      # PBS-1 in front of the scope: rear end, axis
PENAL = (0.335, 0.10)                                        # case on 1.18 shelf: front, along y
# lamp above the table: the shade points down
LAMP_X, LAMP_Y, LAMP_Z = 0.0, -0.24, 1.84
# alarm sensor on the right frame of the opening (the frame face is y = 0)
SENSOR = (XI1 - kcabinet.LIP / 2, 1.69)

LOD_SPECS = [
    dict(lod=0, bev=1, sides=12),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "cb": ("olive_body", 0.6), "cb_in": ("olive_in", 0.5), "cb_door": ("olive_door", 0.8),
    "cb_door_in": ("olive_door_in", 0.6), "cb_table": ("olive_table", 1.0), "steel": ("steel", 1.0),
    "black": ("black", 0.6), "felt": ("felt", 1.0), "rack_wood": ("rack_wood", 1.2), "lock": ("lock", 2.0),
    "case": ("case", 1.2), "case_trim": ("case_trim", 1.6), "ammo": ("ammo_box", 1.0), "crate": ("crate", 0.9),
    "crate_top": ("crate", 0.9), "rope": ("rope", 1.2), "latch": ("latch", 1.6), "zinc": ("zinc", 1.0),
    "paper": ("paper", 1.6), "canvas": ("canvas", 1.0), "strap": ("strap", 1.6), "mat": ("mat", 1.0),
    "mount": ("mount", 1.4), "bolt": ("bolt", 2.0), "rubber": ("rubber", 1.4),
    "supp": ("supp", 2.2), "tin": ("tin", 2.0), "lamp": ("olive_lamp", 1.4), "bulb": ("bulb", 1.6),
    "tag": ("tag", 2.5), "chain": ("chain", 1.6), "cable": ("cable", 1.4), "sensor": ("sensor", 3.0),
    "led": ("led", 4.0),
}
REGIONS.update(pso1.REGIONS)

# =============================================================================
# Materials
# =============================================================================


def build_worn(mat, origin, color, bare=kmats.lin((104, 104, 106)), primer=kmats.lin((96, 46, 34)), seed=1.0,
               gloss=0.28, spec=0.22, wear=(0.68, 0.73), edge_k=0.75, rub=(), touch=0.0, scratch=0.0, oil=0.0,
               floor_z=0.0, dust=0.2, grime=0.3, decal_items=(), clean=()):
    """SOP olive: old army paint, heavily worn - worn off on the edges (edge_k) and in the places
    that get grabbed (rub - [(center, half-axes, strength)]); a red-brown primer under the olive
    (a rim around the worn spot), bare metal in the middle of the spot. touch - the share of
    touch-up patches: fresh olive of a slightly different tone, with no wear under it. clean -
    [(x0, x1, y0, y1)]: something usually stands there (an empty module slot) - the paint is
    darker and cleaner, with no oil or dust (as in M23). No rust.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.88 for c in color[:3]) + (1,), color)
    # sun-faded paint in larger patches
    base = t.mixc(t.math("MULTIPLY", t.maprange(t.noise(vec, 0.9, 4.0, 0.5), 0.45, 0.75, 0.0, 1.0), 0.35), base,
                  tuple(min(1.0, c * 1.25 + 0.01) for c in color[:3]) + (1,))
    col = kmats.decals(t, base, sep, nsep, decal_items)
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
    tp = None
    if touch > 0:
        # touch-up: patches of fresh olive, the wear under them is reset
        tp = t.step(t.noise(vec, 3.2, 5.0, 0.55), 1.0 - touch * 0.5, 1.0 - touch * 0.5 + 0.02)
        f = t.math("SUBTRACT", f, t.math("MULTIPLY", tp, 0.6))
    worn = t.step(f, wear[0], wear[1])
    deep = t.step(f, wear[1] + 0.05, wear[1] + 0.09)                 # spot center - bare metal
    brush = t.noise(t.stretch(vec, 0.04, 1.0, 1.0), 90.0, 4.0, 0.7)
    metal = t.mixc(t.maprange(brush, 0.3, 0.7, 0.0, 1.0), tuple(c * 0.75 for c in bare[:3]) + (1,),
                   tuple(min(1.0, c * 1.15) for c in bare[:3]) + (1,))
    rim = t.math("SUBTRACT", t.step(f, wear[0] - 0.05, wear[0]), worn)
    col = t.mixc(t.math("MULTIPLY", rim, 0.55), col, kmats.lin((44, 46, 34)))
    if tp is not None:
        col = t.mixc(t.math("MULTIPLY", tp, 0.85), col, tuple(c * 1.06 for c in color[:3]) + (1,))
    col = t.mixc(worn, col, primer)
    col = t.mixc(deep, col, metal)
    h = t.math("MULTIPLY", worn, -0.3)
    g_ = t.math("ADD", gloss, t.math("MULTIPLY", deep, 0.58 - gloss))
    s_ = t.math("ADD", spec, t.math("MULTIPLY", deep, 0.66 - spec))
    if scratch > 0:
        sc = t.step(t.noise(t.stretch(vec, 0.02, 1.0, 1.0), 260.0, 2.0, 0.5), 0.70, 0.73)
        sc = t.math("MULTIPLY", sc, t.maprange(t.noise(vec, 5.0, 4.0, 0.5), 0.35, 0.65, 0.0, scratch))
        col = t.mixc(t.math("MULTIPLY", sc, 0.7), col, metal)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", sc, 0.15))
    # clean rectangles: a soft edge of ~6 mm
    spot = 0.0
    for x0, x1, y0, y1 in clean:
        m = 1.0
        for i, (a, b) in enumerate(((x0, x1), (y0, y1))):
            w = sep.outputs[i]
            e = t.math("MULTIPLY", t.maprange(w, a - 0.006, a + 0.006, 0.0, 1.0), t.maprange(w, b + 0.006, b - 0.006, 0.0, 1.0))
            m = e if isinstance(m, float) else t.math("MULTIPLY", m, e)
        spot = m if isinstance(spot, float) else t.math("MAXIMUM", spot, m)
    if oil > 0:
        up = t.maprange(nsep.outputs["Z"], 0.5, 0.9, 0.0, 1.0)
        ol = t.math("MULTIPLY", t.step(t.noise(vec, 4.0, 6.0, 0.6), 0.62, 0.70), t.math("MULTIPLY", up, oil))
        if not isinstance(spot, float):
            ol = t.math("MULTIPLY", ol, t.math("SUBTRACT", 1.0, spot))
        col = t.mixc(t.math("MULTIPLY", ol, 0.5), col, kmats.lin((16, 14, 10)))
        g_ = t.math("ADD", g_, t.math("MULTIPLY", ol, 0.25))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    if not isinstance(spot, float):
        col = t.mixc(t.math("MULTIPLY", spot, 0.75), col, tuple(c * 0.92 for c in color[:3]) + (1,))
        dirt = t.math("MULTIPLY", dirt, t.math("SUBTRACT", 1.0, spot))
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g_, s_, h)


def wall_decal(name, x0, x1, z0, z1, y):
    """A decal facing -y, only at the face at depth y."""
    return (os.path.join(WORK, name), "y", -1, ("x", "z"), ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0),
            (y - 0.002, y + 0.002))


OLIVE = kmats.lin((80, 86, 56))
NUM = L.NUM
# number on the left door: the face looks toward -x (tilted by 15 degrees); u is along y, to the
# viewer's right it is -y
DOOR_NUM = (os.path.join(WORK, "decal_number.png"), "x", -1, ("y", "z"), (L.DOOR_MID_Y, NUM["z"]),
            (-NUM["w"] * math.sin(math.radians(L.DOOR_DEG)), NUM["h"]), L.NUM_X)
STENCIL = [wall_decal("decal_stencil.png", x0, x1, z0, z0 + h, y0) for x0, x1, y0, y1, z0, h in L.CRATES]
# where hands grab: the right door handle (outside and edge), the door edges, the front edge of the
# table
HANDLE_RUB = [((X1 + 0.12, -0.40, kcabinet.FOOT + 0.98), (0.12, 0.10, 0.16), 0.5)]
DOOR_RUB = HANDLE_RUB + [((X0 - 0.13, -0.49, 1.0), (0.06, 0.06, 0.9), 0.30),
                         ((X1 + 0.13, -0.49, 1.0), (0.06, 0.06, 0.9), 0.30)]
# table: the front edge, around the vise plate (slot 1), the work place by the mat
TABLE_RUB = [((0.0, -0.50, ZT), (0.6, 0.06, 0.05), 0.35), ((S1[0], S1[1], ZT), (0.14, 0.13, 0.05), 0.50),
             ((0.0, -0.36, ZT), (0.30, 0.16, 0.03), 0.15)]
BODY_RUB = [((0.0, 0.0, ZT), (0.5, 0.04, 0.03), 0.35)]                 # threshold by the table

KINDS = kmats.std_kinds(floor_z=0.0)
OLV = dict(color=OLIVE, seed=2.1, touch=0.35, scratch=0.25, floor_z=0.0, dust=0.18, grime=0.3)
KINDS.update({
    "olive_body": (build_worn, dict(OLV, rub=BODY_RUB)),
    "olive_in": (build_worn, dict(OLV, seed=2.6, wear=(0.72, 0.77), edge_k=0.7, touch=0.15, scratch=0.15,
                                  floor_z=ZT, dust=0.3, grime=0.2)),
    "olive_door": (build_worn, dict(OLV, seed=3.3, edge_k=0.95, rub=DOOR_RUB, decal_items=[DOOR_NUM])),
    "olive_door_in": (build_worn, dict(OLV, seed=3.8, wear=(0.70, 0.75), edge_k=0.8, touch=0.2, scratch=0.2,
                                       dust=0.15, grime=0.15)),
    "olive_table": (build_worn, dict(OLV, seed=4.4, wear=(0.65, 0.70), edge_k=1.0, rub=TABLE_RUB, touch=0.2,
                                     scratch=0.9, oil=0.6, floor_z=ZT, dust=0.05, grime=0.15,
                                     clean=[CLEAN2, CLEAN3])),
    "olive_lamp": (build_worn, dict(OLV, seed=4.9, wear=(0.70, 0.75), edge_k=0.8, touch=0.0, floor_z=ZT,
                                    dust=0.4, grime=0.1)),
    "ammo_box": (build_worn, dict(color=kmats.lin((72, 80, 52)), seed=5.3, wear=(0.66, 0.71), edge_k=1.0,
                                  touch=0.25, scratch=0.3, floor_z=0.0, dust=0.3, grime=0.3)),
    "felt": ("plastic", dict(color=kmats.lin((60, 66, 54)), gloss=0.04, spec=0.03, mottle=0.2, dust=0.1,
                             grime=0.4, scuff=(0.9, 1.0))),
    "rack_wood": (kwood.build_wood, dict(color=kmats.lin((118, 82, 52)), seed=6.1, along="x", floor_z=ZT,
                                         dust=0.15, grime=0.5, knots=0.3)),
    "lock": ("steel", dict(seed=6.7, tone=0.22, along="z", gloss=0.45, spec=0.55, floor_z=ZT, dust=0.05,
                           grime=0.4)),
    # aluminium briefcase: ribs, light metal, a black trim and handle
    "case": ("steel", dict(seed=7.1, tone=0.38, along="x", gloss=0.55, spec=0.7, floor_z=ZT, dust=0.25,
                           grime=0.25)),
    "case_trim": ("plastic", dict(color=kmats.lin((28, 28, 28)), gloss=0.3, spec=0.2, dust=0.2, scuff=(0.6, 0.7))),
    "crate": (kwood.build_wood, dict(color=kmats.lin((126, 112, 76)), seed=8.3, along="x", floor_z=0.0, dust=0.3,
                                     grime=0.35, knots=0.5, decal_items=STENCIL)),
    "rope": ("plastic", dict(color=kmats.lin((150, 128, 88)), gloss=0.08, spec=0.05, mottle=0.25, dust=0.2,
                             grime=0.4)),
    "latch": (build_worn, dict(color=kmats.lin((40, 42, 38)), seed=8.9, wear=(0.66, 0.71), edge_k=0.9,
                               floor_z=0.0, dust=0.1, grime=0.3)),
    "zinc": ("steel", dict(seed=9.3, tone=0.30, along="x", gloss=0.45, spec=0.55, floor_z=1.76, dust=0.35,
                           grime=0.2)),
    "paper": ("plastic", dict(color=kmats.lin((206, 198, 170)), gloss=0.15, spec=0.08, mottle=0.12, dust=0.1,
                              grime=0.25, scuff=(0.9, 1.0))),
    "canvas": ("plastic", dict(color=kmats.lin((104, 102, 70)), gloss=0.05, spec=0.03, mottle=0.22, dust=0.2,
                               grime=0.45, scuff=(0.66, 0.74))),
    # cover strap and tie: canvas tape darker than the cover, greasy
    "strap": ("plastic", dict(color=kmats.lin((70, 72, 48)), gloss=0.08, spec=0.05, mottle=0.2, dust=0.15,
                              grime=0.55, scuff=(0.7, 0.8))),
    # canvas cleaning mat: lighter than the pouch, oily
    "mat": ("plastic", dict(color=kmats.lin((122, 112, 82)), gloss=0.06, spec=0.04, mottle=0.3, floor_z=ZT,
                            dust=0.05, grime=0.6, scuff=(0.9, 1.0))),
    # M81 vise plate: blued steel, worn at the edges and by the bolts, oil (as in M23)
    "mount": (build_worn, dict(color=kmats.lin((44, 46, 48)), bare=kmats.lin((120, 120, 124)), primer=kmats.lin((40, 40, 40)),
                               seed=9.7, wear=(0.58, 0.64), edge_k=1.0, scratch=0.9, oil=0.6, floor_z=ZT, dust=0.05,
                               grime=0.4)),
    "bolt": ("steel", dict(seed=10.1, tone=0.24, along="z", gloss=0.45, spec=0.55, floor_z=ZT, dust=0.05, grime=0.5)),
    "supp": (build_worn, dict(color=kmats.lin((34, 34, 36)), bare=kmats.lin((108, 108, 110)),
                              primer=kmats.lin((40, 40, 40)), seed=10.9, wear=(0.70, 0.76), edge_k=0.7, floor_z=ZT,
                              dust=0.0, grime=0.3)),
    "tin": (build_worn, dict(color=kmats.lin((46, 48, 40)), bare=kmats.lin((120, 120, 120)),
                             primer=kmats.lin((50, 50, 46)), seed=11.3, wear=(0.68, 0.73), edge_k=0.9, floor_z=1.18,
                             dust=0.2, grime=0.3)),
    "bulb": ("flat", dict(color=kmats.lin((196, 194, 182)), gloss=0.7, spec=0.6)),
    "bulb_on": ("flat", dict(color=kmats.lin((255, 246, 214)), gloss=0.7, spec=0.6)),
    # chains: blued steel, lighter on the links that rub
    "chain": ("steel", dict(seed=12.3, tone=0.17, along="z", gloss=0.45, spec=0.55, floor_z=ZT, dust=0.1, grime=0.3)),
    "tag": ("steel", dict(seed=11.9, tone=0.52, along="x", gloss=0.5, spec=0.6, dust=0.1, grime=0.2)),
    "cable": ("plastic", dict(color=kmats.lin((26, 26, 26)), gloss=0.3, spec=0.2, dust=0.35, grime=0.3,
                              scuff=(0.8, 0.9))),
    # alarm sensor: grey plastic, the LED is dark red when off and lit while working
    "sensor": ("plastic", dict(color=kmats.lin((172, 168, 156)), gloss=0.3, spec=0.2, dust=0.4, grime=0.4,
                               scuff=(0.7, 0.8))),
    "led": ("flat", dict(color=kmats.lin((70, 14, 12)), gloss=0.85, spec=0.8)),
    "led_on": ("flat", dict(color=kmats.lin((255, 50, 34)), gloss=0.85, spec=0.8)),
})
KINDS.update(pso1.kinds(POSE, floor_z=ZT))

OBJ, NAME = "m32_sop_pack_ball", "ozr_sop_pack_ball"
# Machine look: the lamp shade is ozl_lamp, the sensor LED is ozl_led (both in
# hiddenSelections); off by default, working - the _on_co atlas and the _on rvmat with a glow.
SEL_LAMP, SEL_LED = "ozl_lamp", "ozl_led"
ON = dict(remap={"bulb": "bulb_on", "led": "led_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
# Proxies for the modules: the mod's CfgNonAIVehicles links the OZL_Tool1..3 slots to them
# (Proxyozl_tool1..3); slot N is module N of the "Ballistics" line (M81, M82, M83), unrotated:
# the modules face the person
PROXIES = [(r"\OpenZone_Research\models\proxies\ozl_tool%d" % (i + 1), m) for i, m in enumerate(MODS)]
# Vanilla items: the table - the back row on both sides of slot 2 and the mat; the shelves; the
# crates below
_ZS0 = SHELVES[0][2]
_ZCRATE = SHELVES[1][2] + 0.15                                # top of the wooden box on the 1.52 shelf
_ZLOW = L.CRATES[1][4] + L.CRATES[1][5]                       # top of the crate stack below
DECOR = [
    kv.put("cleaningkit", (-0.290, -0.115, ZT), **kv.flat(0)),
    kv.put("rpkmag", (0.300, -0.120, ZT), **kv.flat(176)),
    # on the mat - the PSO-1 (own, build_scope); loose 7.62 x 39 behind the eyepiece (clear of the
    # scope's extent)
    kv.put("rounds762", (0.160, -0.270, ZM), up=(0, 0, 1), fwd=(0.3, -1, 0)),
    kv.put("sksclip", (0.095, -0.445, ZM), **kv.flat(-6)),
    kv.put("ammobox762", (0.415, 0.300, _ZS0), **kv.flat(90)),
    kv.put("ammobox762", (0.412, 0.296, _ZS0 + 0.052), **kv.flat(84)),
    kv.put("flashlight", (0.150, 0.230, _ZCRATE), **kv.flat(8)),
    kv.put("ducttape", (0.330, 0.250, _ZCRATE), **kv.flat(0)),
    kv.put("rags", (-0.235, 0.220, _ZLOW), **kv.flat(95)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 selections=(SEL_LAMP, SEL_LED), hidden=(SEL_LAMP, SEL_LED), states={"on": ON}, proxies=PROXIES,
                 decor=DECOR, modules=[(o, n, m) for (o, n), m in zip(MOD_OBJ, MODS)], glass=pso1.GLASS)
P = M.part
BOUNDS = {}
LAY = {}


def bev(lod, r=0.003, seg=1):
    return dict(r=r, seg=seg) if lod == 0 else {}


# =============================================================================
# Cabinet (the shared base) and its small parts: door locks, alarm sensor
# =============================================================================
def build_cabinet(spec):
    parts, lay = kcabinet.cabinet(M, spec, X0, X1, Y0, Y1, H, table_z=ZT, table_d=TD, door_deg=L.DOOR_DEG,
                                  shelves=SHELVES, partitions=PARTITIONS, regions=dict(chain="chain"))
    LAY.update(lay)
    return parts


def build_door_locks(spec):
    """Inside the doors (near LOD only): on the right a rod lock (the body by the handle, rods up
    and down in four guides, the rod ends go into the flange), on the left bolts at the top and
    bottom with mushroom handles. a - from the hinge along the door width, b - from the face
    inward, c - height.
    """
    if spec["lod"] > 0:
        return []
    fl, fr = LAY["doors"]
    w = LAY["door_w"]
    zd0, zd1 = LAY["door_z"]
    zh = kcabinet.FOOT + 0.98
    st = P("door_locks", "steel")
    a, b = w - 0.036, 0.013
    fr_box(st, w - 0.095, w - 0.023, 0.0045, 0.021, zh - 0.08, zh + 0.08, fr, 0, 0.002)
    for s, z_end in ((1, zd1 - 0.004), (-1, zd0 + 0.004)):
        G.rod(st, fr.p(a, b, zh + s * 0.08), fr.p(a, b, z_end), 0.0055, 6)
    for zg in (zh + 0.32, zh + 0.66, zh - 0.32, zh - 0.62):
        kcabinet.fbox(st, a - 0.013, a + 0.013, 0.0045, b + 0.008, zg - 0.010, zg + 0.010, frame=fr)
    G.rod(st, fr.p(w - 0.06, 0.021, zh), fr.p(w - 0.06, 0.030, zh), 0.007, 8)             # handle axis
    for zc, s in ((zd1 - 0.13, 1), (zd0 + 0.13, -1)):
        G.rod(st, fl.p(a, b, zc - s * 0.04), fl.p(a, b, zc + s * 0.125), 0.0045, 6)        # bolt
        for zg in (zc - s * 0.02, zc + s * 0.09):
            kcabinet.fbox(st, a - 0.011, a + 0.011, 0.0045, b + 0.007, zg - 0.008, zg + 0.008, frame=fl)
        G.rod(st, fl.p(a, b, zc), fl.p(a, b + 0.020, zc), 0.0028, 6)                       # handle
        G.rod(st, fl.p(a, b + 0.019, zc), fl.p(a, b + 0.026, zc), 0.0065, 6)               # mushroom
    return [st]


def build_sensor(spec):
    """Alarm sensor on the right frame of the opening: a grey body, an LED (ozl_led blinks while
    working), the cable runs smoothly into the frame.
    """
    lod = spec["lod"]
    if lod == 2:
        return []
    x, z = SENSOR
    sn = P("alarm_sensor", "sensor")
    g.box(sn, x - 0.012, x + 0.012, -0.016, 0.0, z - 0.035, z + 0.035, **bev(lod, 0.002))
    parts = [sn]
    if lod == 0:
        g.cyl(sn, (x, -0.017, z + 0.022), "y", 0.0045, 0.002, 10)                              # bezel
        cb = P("alarm_cable", "cable")
        g.pipe(cb, G.spline([(x, -0.008, z - 0.035), (x + 0.002, -0.009, z - 0.06), (x + 0.004, -0.006, z - 0.09),
                             (x + 0.006, 0.002, z - 0.105)], 2), 0.0022, 4)
        parts.append(cb)
    ld = P("alarm_led", "led", group=SEL_LED)
    g.cyl(ld, (x, -0.0185, z + 0.022), "y", 0.0030, 0.002, 10 if lod == 0 else 6)
    parts.append(ld)
    return parts


# =============================================================================
# Pyramid: cradle, comb, locking bar with a lock, weapons in covers
# =============================================================================
# Cover following the silhouette of an AKM with a magazine (880 mm): height above ZT,
# half-axis along x (thickness), along y (along the weapon), center along y. From the bottom:
# butt, neck, grip and the magazine as a hump forward, receiver, forend in the comb notch,
# barrel; the top is tied. Folds are a small wave of the half-axes.
COVER = [(0.071, 0.027, 0.058, 0.318), (0.10, 0.030, 0.064, 0.320), (0.20, 0.029, 0.060, 0.316),
         (0.29, 0.025, 0.046, 0.308), (0.35, 0.028, 0.058, 0.290), (0.41, 0.031, 0.082, 0.266),
         (0.47, 0.031, 0.084, 0.262), (0.52, 0.029, 0.060, 0.282), (0.57, 0.024, 0.034, 0.300),
         (COMB_Z - ZT + 0.06, 0.020, 0.026, 0.303), (0.78, 0.017, 0.020, 0.302), (0.82, 0.016, 0.017, 0.301),
         (0.835, 0.0135, 0.0145, 0.301), (0.848, 0.008, 0.009, 0.301)]
COVER_TIE = 0.818


def cover(cv, st, x, lod, k):
    prof = COVER if lod == 0 else [COVER[i] for i in (0, 2, 3, 5, 7, 8, 9, 11, 13)]
    pts, radii = [], []
    for i, (z, rx, ry, yy) in enumerate(prof):
        fold = 1.0 + (0.05 * math.sin(i * 2.3 + k * 1.7) if 0 < i < len(prof) - 2 else 0.0)
        pts.append((x + 0.002 * math.sin(i * 1.3 + k), yy, ZT + z))
        radii.append((rx * fold, ry * (2.0 - fold)))
    g.tube_var(cv, pts, radii, 8 if lod == 0 else 6)
    if lod > 0:
        return
    # tie at the muzzle: a cord ring
    rx, ry = 0.0172, 0.0182
    ring = [(x + rx * math.cos(2 * math.pi * j / 10), 0.301 + ry * math.sin(2 * math.pi * j / 10), ZT + COVER_TIE)
            for j in range(11)]
    g.pipe(st, ring, 0.0022, 4)
    g.pipe(st, [(x - 0.017, 0.300, ZT + COVER_TIE), (x - 0.024, 0.296, ZT + COVER_TIE - 0.03),
                (x - 0.022, 0.290, ZT + COVER_TIE - 0.07)], 0.0018, 4)
    # strap: from the sling swivel at the forend it sags forward in a loop to the butt (outside
    # the cover and the magazine hump, in front of the comb's locking bar)
    sl = G.spline([(x, 0.282, 1.60), (x, 0.245, 1.47), (x, 0.226, 1.40), (x, 0.180, 1.33), (x, 0.163, 1.25),
                   (x, 0.166, 1.15), (x, 0.190, 1.07), (x, 0.225, 1.04), (x, 0.258, 1.045)], 1)
    g.sweep(st, sl, (1, 0, 0), 0.0016, 0.0115)


def build_rack(spec):
    lod = spec["lod"]
    y0, y1 = RACK_Y
    wd = P("rack_wood", "rack_wood")
    xa, xb = XI0 + 0.004, XP - 0.006
    if lod == 2:
        g.box(wd, xa, xb, y0, y1, ZT, ZT + 0.07)
        g.box(wd, xa, xb, y0 + 0.08, y1, COMB_Z, COMB_Z + 0.04)
        return [wd]
    # lower cradle: a bar with sockets for the butts (the socket is felt, recessed)
    g.box(wd, xa, xb, y0, y1, ZT, ZT + 0.07, **bev(lod))
    fe = P("rack_felt", "felt")
    for x in SLOTS if lod == 0 else ():
        g.box(fe, x - 0.035, x + 0.035, y0 + 0.04, y1 - 0.03, ZT + 0.07, ZT + 0.0715)
    # comb: a back bar and teeth, the forend notches open forward, felt in the notches. The comb
    # is made of its own parts: its top is above the cradle and the teeth are in front of the
    # back bar - in the atlas they must not share texels with what is under and behind them (a
    # rectangle is a part / region / side)
    yc = y0 + 0.07
    cb = P("rack_comb", "rack_wood")
    g.box(cb, xa, xb, yc + 0.07, y1, COMB_Z, COMB_Z + 0.04, **bev(lod))
    tt = P("rack_teeth", "rack_wood")
    edges = [xa] + [v for x in SLOTS for v in (x - 0.026, x + 0.026)] + [xb]
    for i in range(0, len(edges), 2):
        g.box(tt, edges[i], edges[i + 1], yc, yc + 0.07, COMB_Z, COMB_Z + 0.04)
    for x in SLOTS if lod == 0 else ():
        g.box(fe, x - 0.026, x + 0.026, yc + 0.066, yc + 0.0705, COMB_Z + 0.002, COMB_Z + 0.038)
    # comb brackets to the back and the side
    st = P("rack_steel", "steel")
    g.box(st, xa, xa + 0.004, yc + 0.07, YI1, COMB_Z - 0.04, COMB_Z + 0.04)
    g.box(st, xb - 0.004, xb, yc + 0.07, YI1, COMB_Z - 0.04, COMB_Z + 0.04)
    g.box(st, (xa + xb) / 2 - 0.02, (xa + xb) / 2 + 0.02, y1, YI1, COMB_Z, COMB_Z + 0.04)
    # locking bar in front of the notches: a hinge on the left, an eye on the right, a padlock
    zb = COMB_Z + 0.012
    g.box(st, xa + 0.006, xb - 0.004, yc - 0.012, yc - 0.004, zb, zb + 0.022, **bev(lod, 0.0015))
    parts = [wd, cb, tt, st]
    # two sockets hold weapons in canvas covers (the rifle itself is not modeled), straps and ties
    sp = P("rack_straps", "strap") if lod == 0 else None
    for i, x in enumerate((SLOTS[0], SLOTS[2])):
        cv = P("rack_cover%d" % i, "canvas")
        cover(cv, sp, x, lod, i)
        parts.append(cv)
    if lod == 0:
        parts += [fe, sp]
        g.cyl(st, (xa + 0.012, yc - 0.008, zb + 0.011), "z", 0.006, 0.04, 8)
        g.box(st, xb - 0.03, xb - 0.024, yc - 0.024, yc - 0.004, zb - 0.01, zb + 0.032)           # eye
        lk = P("rack_lock", "lock")
        lx, ly, lz = xb - 0.04, yc - 0.03, zb - 0.055
        g.box(lk, lx - 0.022, lx + 0.022, ly - 0.008, ly + 0.008, lz - 0.025, lz + 0.022, r=0.004, seg=1)
        g.pipe(lk, [(lx + 0.012, ly, lz + 0.020)] + G.arc((lx, ly, lz + 0.034), 0.012, 0, 180, 6) +
               [(lx - 0.012, ly, lz + 0.020)], 0.0035, 5)
        g.cyl(lk, (lx, ly - 0.0085, lz - 0.008), "y", 0.004, 0.002, 8)                           # keyhole
        parts.append(lk)
    return parts


# =============================================================================
# Shelves: case, steel ammo boxes, pencil case, wooden box, zinc can; the lower compartment
# =============================================================================
def ammo_box(part, latch, x0, x1, y0, y1, z0, h, lod, handle=True):
    """Steel ammo box (a belt box): a body with rounded edges, a lid with a flange, a folding
    bracket handle on the lid (an arc without kinks), a latch lever on the -y end, a stamped
    rib on the end.
    """
    g.box(part, x0, x1, y0, y1, z0, z0 + h - 0.035, **bev(lod, 0.005))
    g.box(part, x0 - 0.003, x1 + 0.003, y0 - 0.003, y1 + 0.003, z0 + h - 0.035, z0 + h - 0.006, **bev(lod, 0.003))
    if lod > 0:
        return
    xc = (x0 + x1) / 2
    zt = z0 + h - 0.006
    if not handle:
        g.box(latch, xc - 0.022, xc + 0.022, y0 - 0.012, y0 - 0.004, z0 + h - 0.075, z0 + h - 0.012)
        g.box(part, x0 + 0.012, x1 - 0.012, y0 - 0.004, y0, z0 + 0.03, z0 + h - 0.09)
        return
    # the handle lies on the lid: a rod bracket with rounded corners, lugs at the ends
    ya, yb = y0 + 0.05, y1 - 0.05
    pts = [(xc - 0.012, ya - 0.004, zt + 0.003), (xc - 0.012, ya + 0.006, zt + 0.0075),
           (xc - 0.012, ya + 0.02, zt + 0.0085), (xc - 0.012, yb - 0.02, zt + 0.0085),
           (xc - 0.012, yb - 0.006, zt + 0.0075), (xc - 0.012, yb + 0.004, zt + 0.003)]
    g.pipe(latch, pts, 0.0035, 5)
    for yy in (ya - 0.006, yb + 0.006):
        g.box(latch, xc - 0.020, xc - 0.004, yy - 0.006, yy + 0.006, zt, zt + 0.006)
    # latch: a lever on an axis near the top of the end
    g.box(latch, xc - 0.022, xc + 0.022, y0 - 0.012, y0 - 0.004, z0 + h - 0.075, z0 + h - 0.012)
    g.cyl(latch, (xc, y0 - 0.008, z0 + h - 0.012), "x", 0.004, 0.05, 6)
    g.box(part, x0 + 0.012, x1 - 0.012, y0 - 0.004, y0, z0 + 0.03, z0 + h - 0.09)                 # rib on the end


def build_shelves(spec):
    lod = spec["lod"]
    parts = []
    # 90s case at the bottom of the right compartment: an aluminium briefcase with ribs, the handle
    # and latches facing the front
    cs = P("case", "case")
    ct = P("case_trim", "case_trim")
    x0, x1, y0, y1, z0, h = 0.045, 0.445, 0.06, 0.36, ZT, 0.10
    g.box(cs, x0, x1, y0, y1, z0 + 0.004, z0 + h, **bev(lod, 0.010, 2))
    parts.append(cs)
    if lod < 2:
        g.box(ct, x0 - 0.003, x1 + 0.003, y0 - 0.003, y1 + 0.003, z0 + h * 0.62, z0 + h * 0.66,
              **bev(lod, 0.0015))                                                                  # seam trim
        g.box(ct, x0 + 0.01, x1 - 0.01, y0 + 0.01, y1 - 0.01, z0, z0 + 0.004)                     # skid feet
        xc, zh = (x0 + x1) / 2, z0 + h * 0.62
        if lod == 0:
            # handle: an arc of elliptical section on two bosses
            hp = G.spline([(xc - 0.058, y0 - 0.006, zh), (xc - 0.052, y0 - 0.024, zh), (xc - 0.030, y0 - 0.031, zh),
                           (xc + 0.030, y0 - 0.031, zh), (xc + 0.052, y0 - 0.024, zh), (xc + 0.058, y0 - 0.006, zh)], 3)
            g.tube_var(ct, hp, [(0.006, 0.0085)] * len(hp), 6)
            for s in (-1, 1):
                g.box(ct, xc + s * 0.058 - 0.010, xc + s * 0.058 + 0.010, y0 - 0.010, y0, zh - 0.012, zh + 0.012)
            for xl in (x0 + 0.06, x1 - 0.06):                                                      # latches
                g.box(cs, xl - 0.02, xl + 0.02, y0 - 0.008, y0, z0 + h * 0.5, z0 + h * 0.8, r=0.003, seg=1)
                g.box(ct, xl - 0.006, xl + 0.006, y0 - 0.010, y0 - 0.007, z0 + h * 0.66, z0 + h * 0.75)
            rb = P("case_ribs", "case")
            parts.append(rb)
            for k in range(5):                                                                     # lid ribs
                yk = y0 + 0.05 + 0.05 * k
                g.box(rb, x0 + 0.02, x1 - 0.02, yk - 0.005, yk + 0.005, z0 + h, z0 + h + 0.003)
        else:
            G.rod(ct, (xc - 0.05, y0 - 0.026, zh), (xc + 0.05, y0 - 0.026, zh), 0.007, 4)
        parts.append(ct)
    # middle shelf: two steel boxes and the pencil case (moved from the M83 module place on the
    # table), vanilla boxes next to it
    lt = P("ammo_latches", "latch") if lod == 0 else None
    z = SHELVES[0][2]
    for i, xa in enumerate((0.04, 0.175) if lod < 2 else ()):
        ab = P("ammo_box%d" % i, "ammo")
        ammo_box(ab, lt, xa, xa + 0.12, 0.10, 0.38, z, 0.19, lod)
        parts.append(ab)
    if lt is not None:
        parts.append(lt)
    if lod < 2:
        parts += build_penal(lod, z)
    # top shelf: a wooden box with a hinged lid
    cr = P("shelf_crate", "crate_top")
    z = SHELVES[1][2]
    g.box(cr, 0.05, 0.43, 0.09, 0.40, z, z + 0.13, **bev(lod, 0.002))
    g.box(cr, 0.046, 0.434, 0.086, 0.404, z + 0.13, z + 0.15, **bev(lod, 0.003))
    if lod == 0:
        for xa, xb in ((0.03, 0.05), (0.43, 0.45)):                                               # battens
            g.box(cr, xa, xb, 0.11, 0.38, z + 0.01, z + 0.125)
    parts.append(cr)
    if lod < 2:
        # zinc can above the pyramid (soldered shut, the bracket handle of the opening strip)
        zn = P("zinc", "zinc")
        z = SHELVES[2][2]
        x0, x1, y0, y1 = -0.42, -0.09, 0.10, 0.32
        g.box(zn, x0, x1, y0, y1, z, z + 0.075)
        g.box(zn, x0 - 0.002, x1 + 0.002, y0 - 0.002, y1 + 0.002, z + 0.075, z + 0.08, **bev(lod, 0.0015))
        if lod == 0:
            g.box(zn, x0 + 0.02, x1 - 0.02, y0 + 0.025, y0 + 0.031, z + 0.08, z + 0.0815)          # strip seam
            g.pipe(zn, [(x0 + 0.03, y0 + 0.09, z + 0.08), (x0 + 0.03, y0 + 0.09, z + 0.090),
                        (x0 + 0.03, y0 + 0.095, z + 0.094), (x0 + 0.03, y0 + 0.125, z + 0.094),
                        (x0 + 0.03, y0 + 0.13, z + 0.090), (x0 + 0.03, y0 + 0.13, z + 0.08)], 0.002, 5)
        parts.append(zn)
    return parts


def build_penal(lod, z):
    """Pencil case with an AK accessory (dia ~0.03 x 0.10 - an estimate): a tin cylinder, a lid
    with a seam, lies along y on the shelf.
    """
    px, py = PENAL
    n = 8 if lod == 0 else 6
    r = 0.015
    pn = P("penal", "tin")
    prof = [(r - 0.002, 0.0), (r, 0.002), (r, 0.074), (r - 0.0006, 0.076), (r + 0.0006, 0.078), (r + 0.0006, 0.098),
            (r - 0.0015, 0.1)]
    pr = prof if lod == 0 else [prof[i] for i in (0, 2, 4, 6)]
    # solid of revolution along x turned to y: points (r, h) -> along y
    ring = []
    for rr, hh in pr:
        ring.append([(px + rr * math.cos(2 * math.pi * k / n), py + hh, z + r + rr * math.sin(2 * math.pi * k / n))
                     for k in range(n)])
    bm = pn.bm
    vs = [[bm.verts.new(p) for p in rg] for rg in ring]
    new = []
    for i in range(len(vs) - 1):
        for k in range(n):
            j = (k + 1) % n
            c = sum((v.co for v in (vs[i][k], vs[i][j])), vs[i][k].co * 0) / 2
            new.append(G.face(pn, [vs[i][k], vs[i][j], vs[i + 1][j], vs[i + 1][k]], (c.x - px, 0, c.z - z - r)))
    new.append(G.face(pn, vs[0], (0, -1, 0)))
    new.append(G.face(pn, vs[-1], (0, 1, 0)))
    pn.tag(new)
    return [pn]


def build_lower(spec):
    """Lower compartment: two wooden ammo crates stacked, two steel boxes on the right."""
    lod = spec["lod"]
    rp = P("crate_ropes", "rope") if lod == 0 else None
    lt = P("crate_latches", "latch") if lod == 0 else None
    parts = []
    for i, (x0, x1, y0, y1, z0, h) in enumerate(L.CRATES):
        cr = P("crate%d" % i, "crate")
        parts.append(cr)
        g.box(cr, x0, x1, y0, y1, z0, z0 + h - L.CRATE_LID, **bev(lod, 0.002))
        g.box(cr, x0 - 0.004, x1 + 0.004, y0 - 0.004, y1 + 0.004, z0 + h - L.CRATE_LID, z0 + h, **bev(lod, 0.003))
        if lod > 0:
            continue
        for xa, xb in ((x0 - 0.008, x0), (x1, x1 + 0.008)):                                      # end battens
            g.box(cr, xa, xb, y0 + 0.02, y0 + 0.07, z0 + 0.01, z0 + h - L.CRATE_LID - 0.004)
            g.box(cr, xa, xb, y1 - 0.07, y1 - 0.02, z0 + 0.01, z0 + h - L.CRATE_LID - 0.004)
        for xc in (x0 + 0.10, x1 - 0.10):
            g.box(lt, xc - 0.016, xc + 0.016, y0 - 0.010, y0 - 0.004, z0 + h - 0.05, z0 + h - 0.004)
            g.box(lt, xc - 0.010, xc + 0.010, y0 - 0.012, y0, z0 + h - 0.075, z0 + h - 0.05)
        yc, zc = (y0 + y1) / 2, z0 + h * 0.6
        g.pipe(rp, G.spline([(x1 + 0.006, yc - 0.05, zc), (x1 + 0.014, yc - 0.04, zc - 0.03), (x1 + 0.016, yc, zc - 0.04),
                             (x1 + 0.014, yc + 0.04, zc - 0.03), (x1 + 0.006, yc + 0.05, zc)], 2), 0.005, 4)
    if rp is not None:
        parts += [rp, lt]
    lt2 = P("ammo_latches_low", "latch") if lod == 0 else None
    for i, xa in enumerate((0.07, 0.21)):
        ab = P("ammo_box_low%d" % i, "ammo")
        ammo_box(ab, lt2, xa, xa + 0.12, 0.10, 0.38, ZI0, 0.19, lod, handle=False)          # under the table
        parts.append(ab)
    if lt2 is not None:
        parts.append(lt2)
    return parts


def fr_box(part, a0, a1, b0, b1, c0, c1, frame, lod, r):
    """A chamfered box on a door (near LOD): kgeo.box with a chamfer in a frame inflates by r in
    every direction - the pouch stuck out through the sheet by 7.5 mm and gave "lips" along the
    edges (m32_geo.fbox).
    """
    if lod == 0:
        G.fbox(part, a0, a1, b0, b1, c0, c1, frame, r=r, seg=1)
    else:
        kcabinet.fbox(part, a0, a1, b0, b1, c0, c1, frame=frame)


def door_list(pp, fl):
    """Inventory list in a steel frame: a sheet without text."""
    kcabinet.fbox(pp, 0.13, 0.35, 0.0045, 0.0065, 1.24, 1.54, frame=fl)
    fm = P("door_list_frame", "steel")
    for a0, a1, z0, z1 in ((0.12, 0.13, 1.23, 1.55), (0.35, 0.36, 1.23, 1.55), (0.13, 0.35, 1.23, 1.24),
                           (0.13, 0.35, 1.54, 1.55)):
        kcabinet.fbox(fm, a0, a1, 0.0045, 0.009, z0, z1, frame=fl)
    return [pp, fm]


# =============================================================================
# Doors: the list and the pouch inside, the seal cup and tag outside
# =============================================================================
def build_doors_extra(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    fl, fr = LAY["doors"]
    w = LAY["door_w"]
    parts = []
    # inventory list in a frame on the left door inside (b is from the face inward; the door sheet
    # inside is at 0.0045)
    pp = P("door_list", "paper")
    if lod == 1:
        kcabinet.fbox(pp, 0.12, 0.36, 0.0045, 0.0065, 1.23, 1.55, frame=fl)
        parts.append(pp)
    else:
        parts += door_list(pp, fl)
    # pouch on the right door inside: on two hooks, a flap on top (roundings - canvas)
    cv = P("door_pouch", "canvas")
    a0, a1, z0, z1 = w - 0.34, w - 0.15, 1.18, 1.40
    fr_box(cv, a0, a1, 0.0045, 0.065, z0, z1, fr, lod, 0.012)
    fr_box(cv, a0 - 0.004, a1 + 0.004, 0.0045, 0.070, z1 - 0.08, z1 + 0.01, fr, lod, 0.008)
    parts.append(cv)
    if lod == 0:
        hk = P("door_hooks", "steel")
        for a in (a0 + 0.04, a1 - 0.04):
            kcabinet.fbox(hk, a - 0.006, a + 0.006, 0.0045, 0.03, z1 + 0.01, z1 + 0.04, frame=fr)
        sp = P("door_pouch_strap", "strap")
        kcabinet.fbox(sp, (a0 + a1) / 2 - 0.012, (a0 + a1) / 2 + 0.012, 0.066, 0.0715, z1 - 0.13, z1 - 0.07,
                      frame=fr)                                                                     # tongue
        kcabinet.fbox(hk, (a0 + a1) / 2 - 0.016, (a0 + a1) / 2 + 0.016, 0.0715, 0.0745, z1 - 0.115, z1 - 0.095,
                      frame=fr)                                                                     # buckle
        parts += [hk, sp]
    # seal cup on the right door outside by the handle and a tag on the left
    st = P("door_seal", "steel")
    zh = kcabinet.FOOT + 0.98
    g.cyl(st, (w - 0.055, -0.016, zh + 0.15), "y", 0.016, 0.032, 12 if lod == 0 else 6, frame=fr)
    parts.append(st)
    tg = P("door_tag", "tag")
    kcabinet.fbox(tg, 0.20, 0.30, -0.0015, 0.0, 0.30, 0.36, frame=fl)
    if lod == 0:
        for a in (0.207, 0.293):                                                                   # rivets
            g.cyl(tg, (a, -0.0015, 0.33), "y", 0.003, 0.002, 6, frame=fl)
    parts.append(tg)
    return parts


# =============================================================================
# Table: module places, mat, scope, suppressor
# =============================================================================
def build_slots(spec):
    """Slot 1 - a steel vise plate on four bolts (the vise sits on it); slots 2 and 3 are only
    clean patches on the table sheet (build_worn, clean).
    """
    lod = spec["lod"]
    w, d, t = MOUNT
    x, y = S1
    mt = P("mount_plate", "mount")
    g.box(mt, x - w / 2, x + w / 2, y - d / 2, y + d / 2, ZT, ZT + t, **bev(lod, 0.002))
    parts = [mt]
    if lod < 2:
        bt = P("mount_bolts", "bolt")
        for sx in (-1, 1):
            for sy in (-1, 1):
                bx, by = x + sx * (w / 2 - 0.016), y + sy * (d / 2 - 0.016)
                g.cyl(bt, (bx, by, ZT + t + 0.003), "z", 0.0095, 0.006, 6)
                if lod == 0:
                    g.cyl(bt, (bx, by, ZT + t + 0.0064), "z", 0.0055, 0.0012, 6)           # stud end
        parts.append(bt)
    return parts


def build_mat(spec):
    """Canvas cleaning mat: lies unevenly, the edges slightly raised."""
    lod = spec["lod"]
    x0, x1, y0, y1 = MAT
    mt = P("mat", "mat")
    if lod == 2:
        g.box(mt, x0, x1, y0, y1, ZT, ZM)
        return [mt]
    nx, ny = (6, 4) if lod == 0 else (3, 2)
    bm = mt.bm
    vs = [[bm.verts.new((x0 + (x1 - x0) * i / nx + 0.004 * math.sin(i * 2.1 + j),
                         y0 + (y1 - y0) * j / ny + 0.004 * math.cos(i * 1.3 + j * 2.3),
                         ZT + 0.0012 + (0.0025 * abs(math.sin(i * 1.7 + j * 2.9)) if 0 < i < nx and 0 < j < ny
                                        else 0.0)))
           for j in range(ny + 1)] for i in range(nx + 1)]
    new = []
    for i in range(nx):
        for j in range(ny):
            new.append(G.face(mt, [vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]], (0, 0, 1)))
    mt.tag(new)
    return [mt]


def build_supp(spec):
    """A PBS-1 class suppressor, assembled (152 x dia 40): a rear threaded coupling, a body with a
    groove, a front end with a rounding and an exit hole.
    """
    lod = spec["lod"]
    if lod == 2:
        return []
    n = 10 if lod == 0 else 8
    sx, sy = SUPP
    sp = P("supp", "supp")
    zc = ZM + 0.020
    prof = [(0.0125, 0.0), (0.0145, 0.0015), (0.0145, 0.018), (0.0170, 0.0205), (0.0195, 0.024), (0.0200, 0.028),
            (0.0200, 0.084), (0.0192, 0.0855), (0.0200, 0.087), (0.0200, 0.142), (0.0193, 0.148), (0.0170, 0.1512),
            (0.0090, 0.152)]
    pr = prof if lod == 0 else [prof[i] for i in (0, 2, 5, 9, 11, 12)]
    G.lathe(sp, pr, n, center=(sx, sy, zc), axis="x")
    G.lathe(sp, [(0.0090, 0.152), (0.0060, 0.146)], n, center=(sx, sy, zc), axis="x", cap=True)  # exit
    G.lathe(sp, [(0.0125, 0.0), (0.0080, 0.004)], n, center=(sx, sy, zc), axis="x", cap=True)   # rear thread
    return [sp]


def build_scope(spec):
    """PSO-1 on the mat (pso1.py, shared with M23 and M27; the lens glass is the glass section
    of the model).
    """
    return pso1.build(P, spec["lod"], POSE)


# =============================================================================
# Jar-type lamp above the table (ozl_lamp): a bracket from the roof, a cable to the box on the
# cabinet back
# =============================================================================
def build_lamp(spec):
    lod = spec["lod"]
    n = 12 if lod == 0 else (8 if lod == 1 else 6)
    parts = []
    br = P("lamp_arm", "lamp")
    # bracket: a pipe from the roof up, smoothly forward above the table and smoothly down to the
    # lamp body
    za = H + 0.085
    pts = ([(LAMP_X, 0.12, H)] + G.arc((LAMP_X, 0.08, H + 0.045), 0.04, 0, 90, 4, "yz")[0:] +
           G.arc((LAMP_X, LAMP_Y + 0.04, H + 0.045), 0.04, 90, 180, 4, "yz") + [(LAMP_X, LAMP_Y, LAMP_Z + 0.07)])
    if lod > 0:
        pts = [pts[0], (LAMP_X, 0.12, za), (LAMP_X, LAMP_Y, za), pts[-1]]
    g.pipe(br, pts, 0.011, 8 if lod == 0 else 4)
    if lod < 2:
        g.box(br, LAMP_X - 0.04, LAMP_X + 0.04, 0.08, 0.16, H, H + 0.006, **bev(lod, 0.002))     # plate on the roof
    parts.append(br)
    # body: a bowl with cooling fins, a cable gland on top
    bd = P("lamp_body", "lamp")
    body = [(0.097, 0.0), (0.099, 0.004), (0.099, 0.030), (0.092, 0.042), (0.070, 0.056), (0.036, 0.064),
            (0.020, 0.066)]
    G.lathe(bd, body if lod == 0 else [body[i] for i in (0, 2, 4, 6)], n, center=(LAMP_X, LAMP_Y, LAMP_Z), cap=True)
    g.cyl(bd, (LAMP_X, LAMP_Y, LAMP_Z + 0.0005), "z", 0.097, 0.001, n)                          # rim below
    if lod == 0:
        g.cyl(bd, (LAMP_X, LAMP_Y, LAMP_Z + 0.071), "z", 0.016, 0.010, 10)                     # pipe bushing
        # cooling fins along the body cone: a plate in the (radius, height) plane
        fin = [(0.066, 0.055), (0.096, 0.034), (0.096, 0.041), (0.068, 0.061)]
        for k in range(6):
            a = 2 * math.pi * (k + 0.5) / 6
            fr = g.Frame((LAMP_X, LAMP_Y, LAMP_Z), (math.cos(a), math.sin(a), 0), (0, 0, 1), (-math.sin(a), math.cos(a), 0))
            g.prism(bd, fin, (0, 1), -0.002, 0.002, frame=fr)
        g.cyl(bd, (LAMP_X + 0.040, LAMP_Y, LAMP_Z + 0.061), "z", 0.009, 0.012, 8)              # gland
    parts.append(bd)
    bl = P("lamp_glass", "bulb", group=SEL_LAMP)
    # the shade bottom is a disc, not a point: a ring of radius 0 gives degenerate faces
    prof = [(0.078, 0.0), (0.076, -0.018), (0.070, -0.036), (0.058, -0.054), (0.040, -0.068), (0.016, -0.078)]
    G.lathe(bl, prof if lod == 0 else prof[::2] + [prof[-1]], n, center=(LAMP_X, LAMP_Y, LAMP_Z))
    g.cyl(bl, (LAMP_X, LAMP_Y, LAMP_Z - 0.0785), "z", 0.0165, 0.001, n)
    parts.append(bl)
    if lod == 0:
        # grille: a ring at the body, a ring at the bottom and six arcs along the shade
        cg = P("lamp_cage", "lamp")
        g.pipe(cg, G.arc((LAMP_X, LAMP_Y, LAMP_Z - 0.003), 0.086, 0, 360, n, "xy"), 0.0045, 4)
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            arc = [(LAMP_X + (r + 0.0055) * math.cos(a), LAMP_Y + (r + 0.0055) * math.sin(a), LAMP_Z + h)
                   for r, h in prof[:-1]] + [(LAMP_X + 0.020 * math.cos(a), LAMP_Y + 0.020 * math.sin(a), LAMP_Z - 0.084)]
            g.pipe(cg, arc, 0.0028, 4)
        parts.append(cg)
        # cable: from the gland up along the pipe, back along the roof, into the junction box on the
        # back
        cb = P("lamp_cable", "cable")
        xs = LAMP_X + 0.040
        cpts = [(xs, LAMP_Y, LAMP_Z + 0.067), (0.036, LAMP_Y + 0.004, LAMP_Z + 0.105), (0.020, LAMP_Y + 0.02, H + 0.075),
                (0.0158, LAMP_Y + 0.07, H + 0.085), (0.0158, -0.05, H + 0.085), (0.0158, 0.05, H + 0.084),
                (0.024, 0.16, H + 0.035), (0.040, 0.22, H + 0.010), (0.050, 0.25, H + 0.002)]
        g.pipe(cb, G.spline(cpts, 2), 0.0045, 4)
        g.cyl(cb, (0.050, 0.25, H + 0.003), "z", 0.009, 0.006, 8)                                # roof bushing
        parts.append(cb)
    return parts


def build_lod(spec):
    parts = build_cabinet(spec) + build_door_locks(spec) + build_sensor(spec) + build_rack(spec)
    parts += build_shelves(spec) + build_lower(spec) + build_doors_extra(spec) + build_slots(spec)
    parts += build_mat(spec) + build_supp(spec) + build_scope(spec) + build_lamp(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    metal = kx.PEN + r"\metalplate.rvmat"
    # components no thinner than 0.5 m: the body, the table down to the floor, the doors - with a
    # margin, equally on both sides of the sheet
    cab = kx.box_pts(X0, X1, Y0, Y1, 0.0, H + 0.10)
    table = kx.box_pts(X0, X1, -TD - 0.02, Y0 + 0.01, 0.0, ZT + 0.02)
    comps = [(cab, metal), (table, metal)]
    for s in (-1, 1):
        xc = s * (X1 + 0.065)
        comps.append((kx.box_pts(xc - 0.25, xc + 0.25, -0.50, 0.0, 0.0, H - 0.03), metal))
    memory = {
        "invView": [(-0.3, -2.6, 1.4)],
        "ce_center": [(0.0, 0.0, H / 2)],
        "ce_radius": [(1.1, 0.0, H / 2)],
    }
    for i, m in enumerate(MODS):
        memory["module_%d" % (i + 1)] = [m]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2] + 0.004)
    return comps, 180.0, memory, bbox


# The first ones are for the --look preview: overall view, the table with the modules in place
# (and empty), the scope and the suppressor close up, the pyramid, the shelves
SHOTS = [
    ("front", (-1.1, -2.6, 1.65), (0.0, 0.0, 1.0), 30),
    ("table", (0.0, -1.15, 1.55), (0.0, -0.25, 0.86), 34),
    ("scope", (0.22, -0.88, 1.14), (0.0, -0.36, 0.92), 40),
    ("rack", (-0.15, -1.0, 1.45), (-0.24, 0.25, 1.25), 34),
    ("shelves", (0.35, -1.0, 1.45), (0.24, 0.2, 1.25), 34),
    ("lower", (0.3, -1.4, 0.45), (-0.1, 0.2, 0.35), 32),
    ("door_left", (-1.5, -1.2, 1.3), (-0.56, -0.26, 1.15), 34),
    ("door_right", (1.2, -1.4, 1.3), (0.56, -0.26, 1.15), 34),
    ("lamp", (0.45, -0.95, 1.55), (0.0, -0.24, 1.75), 40),
    ("back", (1.4, 2.0, 1.7), (0.0, 0.0, 0.95), 30),
]

M.look_shots = (5, 2)
M.run(build_lod, collision, SHOTS, row_step=1.9, row_shot=((1.9, -6.4, 2.2), (1.9, 0, 0.95)))
