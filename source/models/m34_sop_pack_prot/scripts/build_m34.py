"""M34 - the SOP equipment cabinet: the SOP Protection Packer (OZL_Sop_Pack_Prot). A packer:
cargo 10x10, three module places on a folding table (module_1..3) and proxies for the
modules at the same places. Each module of the "Protection" line has its own slot and its
own working place: slot 1 - the M84 pressure tester to the right of the bust, with a hose
to the vanilla GP-5 on the bust; slot 2 - the M85 gas analyzer at the back in the center;
slot 3 - the M86 plate clamp on the right, on a plywood pad under the work lamp.

    blender --background --python build_m34.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

No decals (make_decals.py is not needed): the unreadable details are done by geometry and
color.

The cabinet is the shared cabinet base (kcabinet.cabinet, moved out by M32): the same army
steel two-door cabinet 1.00 x 1.90 x 0.50 m on a 6 cm plinth, the doors open to 105
degrees, a folding panel 0.96 x 0.50 on a piano hinge lowered on two chains to the table at
0.85 m. The body dimensions match M32 (ShMDO 900 x 1800 x 500 mm and a UHL-MASH cabinet;
the sources are in kcabinet and build_m32.py). An analog equipment cabinet (a weapon and
equipment cabinet 1275 x 900 x 500 mm, 1 mm steel, 61 kg) was compared with the base: the
same depth (0.50), width 0.90 against 1.00, and 1.275 high is a low cabinet without a
folding table (only 0.4 m would remain above a table at 0.85); from it the layout (a
partition, shelves on the left, a shelf with a helmet on the right, vent perforations on
the doors) and the contents were taken, the dimensions follow the base so that M32 and M34
stand on the same base.

SOP: olive, Soviet equipment still in service, worn on the edges and at the handles,
touched up in places, no rust - the build_worn builder from M32 (a red-brown primer under
the olive, metal in the middle of a worn spot) plus a clean patch where slot 2 is empty (as
in M23).

Look: "dayz" (matte, dirtier, colored AO). The soft things and small items are vanilla
proxy things (kvanilla): SSh-68 helmets on the shelves (Ssh68Helmet_g, kv.flat - the skirt
on the shelf), GP-5 gas masks (on the bust a worn model GP5GasMask_m; the ground model
GP5GasMask_g lies on the bottom of the left compartment), GP-5 filter canisters
(GP5GasMask_filter) on the shelves and in the door tray, a screwdriver, an adjustable
wrench and pliers on the table. The own things use smooth surfaces, without boxes and
octagons: GP-5 canvas bags - a soft box with rounded edges and slightly convex sides, a
flap as a sheet over the top edge onto the front, a button, a tape strap; the mannequin
bust - one smooth surface through sections (torso, shoulders, neck, head, no face) on an
oval stand; cylinders - more facets, a shoulder to the neck, a valve with a side fitting, a
nut and a handwheel; the crate - boards with gaps, battens, an overlapping lid; the lying
cylinders sit in the cutouts of the pads; the cylinder collar is a steel strap. The work
lamp is moved to the right rear corner, the reflector above the M86 place: hinges with
thumbscrews, parallel rods, a button on the base, a socket body, a rolled reflector edge;
the cord is a smooth curve to the socket on the right wall of the compartment.

Contents (the dimensions where there is no passport are estimates from photos):
- a GP-5 gas mask in a canvas bag (the bag ~0.21 x 0.10 x 0.23 - an estimate from photos):
  two stand on the left against the back, one lies on the right shelf, one hangs on hooks
  on the left door inside;
- 7 l cylinders (a dia 140 series per GOST 949, length ~0.53 - an estimate; like the 6 l
  cylinder of M29): black with a white band (air), a brass valve with a handwheel. Two
  stand on the right, strapped to the back, two lie in the lower compartment on wooden pads
  with cutouts;
- a wooden crate (~0.32 x 0.34 x 0.30 - an estimate) with a bracket handle in the lower
  compartment on the left, with a bundle of canvas on it;
- blank aluminium tags on the shelf edges, a lead seal on a wire on the right door handle,
  white bands on the cylinders (tags, seals, stripes - without text).
On the table - a mannequin bust (a smooth blank without a face, like the head in M29/M30;
shoulders ~0.34 - an estimate from an ordinary torso; the head by sections in the axes of a
worn mask, the size of a player's head) in a vanilla GP-5: the filter is unscrewed, a brass
adapter is screwed into the neck of the valve box, from it a hose runs to the M84 place
with a brass coupling at the end (without the module the hose and the coupling lie on the
table); an old work lamp on hinges (NKP class, a cast iron base dia ~0.16, a conical
reflector dia ~0.16 - an estimate from photos); a mechanical stopwatch (case dia 55, a head
with a lug - like the Soviet Agat / SOPpr, an estimate) - the pressure test time.

Machine look: ozl_lamp - the bulb and the white inside of the work lamp reflector, working
- the _on atlas (steady); ozl_work - the stopwatch hand, a model.cfg loop (sourceAddress
"loop", one turn per 60 s, like a second hand). The modules in the slots "work" together
with the machine (their OZL_Work).

Every item has its own parts (a bag - the box, flap and strap separately, a cylinder - the
body, band and valve): the kuv atlas lays the faces of a part out by sides into one
rectangle, so identical items side by side or a flap on top of a box would share texels.

Blender axes: X - width, Y - depth (front at -Y), Z - up.
"""
import math
import os
import sys

import bmesh
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kcabinet  # noqa: E402
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import krender  # noqa: E402
import kvanilla as kv  # noqa: E402
import kwood  # noqa: E402

# =============================================================================
# Dimensions, m
# =============================================================================
X0, X1, Y0, Y1, H = -0.50, 0.50, 0.0, 0.50, 1.90               # the same base as M32
ZT, TD, DOOR_DEG = 0.85, 0.50, 105.0
XI0, XI1 = X0 + kcabinet.T, X1 - kcabinet.T
ZI0 = kcabinet.FOOT + kcabinet.T
YI1 = Y1 - kcabinet.T
XP = 0.0                                                     # helmets left, cylinders right
SH_L1, SH_L2, SH_R = 1.24, 1.58, 1.52                         # shelves: left lower and upper, right
SHELVES = [(XI0, XP - 0.003, SH_L1), (XI0, XP - 0.003, SH_L2), (XP + 0.003, XI1, SH_R)]
PARTITIONS = [(XP, ZT, H - kcabinet.T)]
LAYOUT = kcabinet.layout(X0, X1, Y0, Y1, H, ZT, TD, DOOR_DEG)
DOOR_W = LAYOUT["door_w"]
# Module places ("Protection" line): slot 1 - M84 to the right of the bust, slot 2 - M85 at
# the back in the center (the lid folds back up to +0.103 from the point), slot 3 - M86 on a
# plywood pad under the lamp
PLY = (0.29, -0.31, 0.24, 0.18, 0.012)                       # center, size, pad thickness
MODS = [(0.06, -0.34, ZT), (-0.04, -0.10, ZT), (PLY[0], PLY[1], ZT + PLY[4])]
MOD_OBJ = [("m84_test_pump", "ozr_test_pump"), ("m85_gas_analyzer", "ozr_gas_analyzer"),
           ("m86_plate_clamp", "ozr_plate_clamp")]
# Module extents: width, depth back/forward, height - only for the --stats check that the
# vanilla items do not touch them
MOD_BOX = [(0.192, 0.090, 0.090, 0.242), (0.205, 0.103, 0.107, 0.245), (0.194, 0.068, 0.068, 0.162)]
CLEAN2 = (MODS[1][0] - 0.10, MODS[1][0] + 0.10, MODS[1][1] - 0.10, MODS[1][1] + 0.09)
# bust at the left front corner (in a GP-5), the lamp in the right rear corner, the reflector above
# M86
BUST_X, BUST_Y = -0.255, -0.30
LAMP_X, LAMP_Y = 0.37, -0.075
# stopwatch at the right front corner, under the lamp light
SW = (0.425, -0.455)
# cylinders
TANK_R, TANK_L = 0.070, 0.53

LOD_SPECS = [
    dict(lod=0, bev=1, sides=12),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "cb": ("olive_body", 0.6), "cb_in": ("olive_in", 0.5), "cb_door": ("olive_door", 0.8),
    "cb_door_in": ("olive_door_in", 0.6), "cb_table": ("olive_table", 1.0), "steel": ("steel", 1.0),
    "black": ("black", 0.6), "chain": ("chain", 1.6), "tray": ("olive_in", 1.2),
    "strap": ("strap", 1.4), "bag": ("canvas", 1.0), "button": ("black", 2.0),
    "tank": ("tank", 1.0), "band": ("band", 1.2), "valve": ("brass", 2.0),
    "crate": ("crate", 0.9), "chock": ("chock", 1.2), "roll": ("canvas_roll", 1.0),
    "head": ("head", 1.4), "stand": ("black", 1.2), "tag": ("tag", 2.5), "seal": ("lead", 3.0),
    "lamp": ("lamp_paint", 1.4), "lamp_in": ("lamp_in", 1.6), "bulb": ("bulb", 2.0), "cast": ("cast", 1.2),
    "cable": ("rubber", 1.0), "hose": ("rubber", 1.4), "chrome": ("chrome", 2.5), "dial": ("dial", 3.0),
    "hand": ("hand", 3.0), "bakelite": ("bakelite", 1.6), "ply": ("ply", 1.0), "vent": ("black", 0.8),
}

# =============================================================================
# Materials
# =============================================================================


def build_worn(mat, origin, color, bare=kmats.lin((104, 104, 106)), primer=kmats.lin((96, 46, 34)), seed=1.0,
               gloss=0.28, spec=0.22, wear=(0.68, 0.73), edge_k=0.75, rub=(), touch=0.0, scratch=0.0, oil=0.0,
               floor_z=0.0, dust=0.2, grime=0.3, decal_items=(), clean=()):
    """SOP olive - the M32 builder: old army paint, heavily worn - worn off on the edges (edge_k)
    and in the places that get grabbed (rub - [(center, half-axes, strength)]); a red-brown
    primer under the olive (a rim around the worn spot), bare metal in the middle of the spot.
    touch - the share of touch-up patches: fresh olive of a slightly different tone, with no
    wear under it. No rust. clean - [(x0, x1, y0, y1)]: something usually stands there (an
    empty module slot) - the paint is darker and cleaner, with no oil or dust (as in M23).
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.88 for c in color[:3]) + (1,), color)
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
        tp = t.step(t.noise(vec, 3.2, 5.0, 0.55), 1.0 - touch * 0.5, 1.0 - touch * 0.5 + 0.02)
        f = t.math("SUBTRACT", f, t.math("MULTIPLY", tp, 0.6))
    worn = t.step(f, wear[0], wear[1])
    deep = t.step(f, wear[1] + 0.05, wear[1] + 0.09)
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
    # clean rectangles (an empty slot): a soft edge of ~6 mm
    spot = 0.0
    for x0, x1, y0, y1 in clean:
        m = 1.0
        for i, (a, b) in enumerate(((x0, x1), (y0, y1))):
            w = sep.outputs[i]
            e = t.math("MULTIPLY", t.maprange(w, a - 0.006, a + 0.006, 0.0, 1.0),
                       t.maprange(w, b + 0.006, b - 0.006, 0.0, 1.0))
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


OLIVE = kmats.lin((80, 86, 56))
# where hands grab: the right door handle, the door edges, the front table edge, the threshold of
# the opening
HANDLE_RUB = [((X1 + 0.12, -0.40, kcabinet.FOOT + 0.98), (0.12, 0.10, 0.16), 0.5)]
DOOR_RUB = HANDLE_RUB + [((X0 - 0.13, -0.49, 1.0), (0.06, 0.06, 0.9), 0.30),
                         ((X1 + 0.13, -0.49, 1.0), (0.06, 0.06, 0.9), 0.30)]
# no spot under the tool: on the open table the red primer in the middle looked like blood
TABLE_RUB = [((0.0, -0.50, ZT), (0.6, 0.06, 0.05), 0.35), ((0.0, -0.25, ZT), (0.45, 0.25, 0.03), 0.12)]
BODY_RUB = [((0.0, 0.0, ZT), (0.5, 0.04, 0.03), 0.35)]
# shelf edges where the helmets are taken off
SHELF_RUB = [((-0.24, 0.03, SH_L1), (0.24, 0.05, 0.03), 0.3), ((-0.24, 0.03, SH_L2), (0.24, 0.05, 0.03), 0.3),
             ((0.24, 0.03, SH_R), (0.24, 0.05, 0.03), 0.3)]

KINDS = kmats.std_kinds(floor_z=0.0)
OLV = dict(color=OLIVE, seed=2.1, touch=0.35, scratch=0.25, floor_z=0.0, dust=0.18, grime=0.3)
KINDS.update({
    "olive_body": (build_worn, dict(OLV, seed=2.3, rub=BODY_RUB)),
    "olive_in": (build_worn, dict(OLV, seed=2.8, wear=(0.71, 0.76), edge_k=0.7, rub=SHELF_RUB, touch=0.15,
                                  scratch=0.15, floor_z=ZT, dust=0.3, grime=0.2)),
    "olive_door": (build_worn, dict(OLV, seed=3.5, edge_k=0.95, rub=DOOR_RUB)),
    "olive_door_in": (build_worn, dict(OLV, seed=3.9, wear=(0.70, 0.75), edge_k=0.8, touch=0.2, scratch=0.2,
                                       dust=0.15, grime=0.15)),
    "olive_table": (build_worn, dict(OLV, seed=4.6, wear=(0.68, 0.73), edge_k=1.0, rub=TABLE_RUB, touch=0.2,
                                     scratch=0.5, oil=0.3, floor_z=ZT, dust=0.05, grime=0.15, clean=[CLEAN2])),
    "chain": ("steel", dict(seed=12.3, tone=0.17, along="z", gloss=0.45, spec=0.55, floor_z=ZT, dust=0.1, grime=0.3)),
    "strap": ("plastic", dict(color=kmats.lin((86, 84, 58)), gloss=0.08, spec=0.05, mottle=0.25, dust=0.25,
                              grime=0.4, scuff=(0.7, 0.8))),
    # canvas gas mask bags
    "canvas": ("plastic", dict(color=kmats.lin((104, 102, 70)), gloss=0.05, spec=0.03, mottle=0.22, dust=0.25,
                               grime=0.45, scuff=(0.66, 0.74))),
    "canvas_roll": ("plastic", dict(color=kmats.lin((86, 92, 62)), gloss=0.05, spec=0.03, mottle=0.3, dust=0.3,
                                    grime=0.4, scuff=(0.7, 0.78))),
    # cylinders: black, a white band (air), a brass valve
    "tank": (build_worn, dict(color=kmats.lin((30, 30, 32)), primer=kmats.lin((58, 58, 58)),
                              bare=kmats.lin((120, 120, 124)), seed=7.1, gloss=0.4, wear=(0.70, 0.76), edge_k=0.8,
                              scratch=0.4, floor_z=0.0, dust=0.3, grime=0.2)),
    "band": ("plastic", dict(color=kmats.lin((206, 204, 192)), gloss=0.3, spec=0.2, mottle=0.1, dust=0.25,
                             grime=0.25, scuff=(0.62, 0.70))),
    "brass": ("plastic", dict(color=kmats.lin((156, 120, 58)), gloss=0.55, spec=0.55, mottle=0.25, dust=0.15,
                              grime=0.5, scuff=(0.9, 1.0))),
    "crate": (kwood.build_wood, dict(color=kmats.lin((122, 106, 70)), seed=8.3, along="x", floor_z=0.0, dust=0.3,
                                     grime=0.35, knots=0.5)),
    "chock": (kwood.build_wood, dict(color=kmats.lin((118, 82, 52)), seed=8.9, along="y", dust=0.3, grime=0.5,
                                     knots=0.2)),
    # slot 3 pad: plywood with clamp marks
    "ply": (kwood.build_wood, dict(color=kmats.lin((160, 128, 86)), seed=13.3, along="x", floor_z=ZT, dust=0.15,
                                   grime=0.5, rings=0.25, knots=0.15)),
    # bust: old painted papier-mache, beige, scuffed and dusty
    "head": ("plastic", dict(color=kmats.lin((188, 176, 158)), gloss=0.22, spec=0.15, mottle=0.08, floor_z=ZT,
                             dust=0.3, grime=0.3, scuff=(0.72, 0.82))),
    "tag": ("steel", dict(seed=11.9, tone=0.52, along="x", gloss=0.5, spec=0.6, dust=0.1, grime=0.2)),
    "lead": ("plastic", dict(color=kmats.lin((112, 114, 116)), gloss=0.35, spec=0.3, mottle=0.3, dust=0.1)),
    # work lamp: grey-green hammer enamel, a cast iron base, a white reflector inside
    "lamp_paint": (build_worn, dict(color=kmats.lin((76, 92, 86)), primer=kmats.lin((60, 60, 58)), seed=9.7,
                                    wear=(0.68, 0.74), edge_k=0.9, scratch=0.3, floor_z=ZT, dust=0.3, grime=0.2)),
    "cast": (build_worn, dict(color=kmats.lin((34, 36, 34)), primer=kmats.lin((44, 44, 44)), seed=10.3,
                              wear=(0.68, 0.74), edge_k=1.0, floor_z=ZT, dust=0.2, grime=0.3)),
    "lamp_in": ("plastic", dict(color=kmats.lin((214, 212, 198)), gloss=0.45, spec=0.35, mottle=0.08, dust=0.25,
                                grime=0.15)),
    "lamp_in_on": ("flat", dict(color=kmats.lin((255, 244, 214)), gloss=0.5, spec=0.4)),
    "bulb": ("flat", dict(color=kmats.lin((196, 194, 182)), gloss=0.7, spec=0.6)),
    "bulb_on": ("flat", dict(color=kmats.lin((255, 248, 222)), gloss=0.7, spec=0.6)),
    "bakelite": ("plastic", dict(color=kmats.lin((58, 38, 28)), gloss=0.4, spec=0.3, mottle=0.2, floor_z=ZT,
                                 dust=0.3, grime=0.3, scuff=(0.7, 0.8))),
    # stopwatch: a chrome case, white enamel dial, a red hand
    "chrome": ("steel", dict(seed=12.9, tone=0.34, along="z", gloss=0.7, spec=0.8, floor_z=ZT, dust=0.06,
                             grime=0.3)),
    "dial": ("plastic", dict(color=kmats.lin((226, 222, 206)), gloss=0.5, spec=0.35, mottle=0.05, dust=0.08,
                             grime=0.1)),
    "hand": ("plastic", dict(color=kmats.lin((168, 32, 24)), gloss=0.5, spec=0.35, mottle=0.05, dust=0.02)),
})

OBJ, NAME = "m34_sop_pack_prot", "ozr_sop_pack_prot"
# Machine look: the bulb and the reflector inside of the work lamp are ozl_lamp (in
# hiddenSelections); off by default, working - the _on_co atlas and the _on rvmat with a glow.
# The stopwatch hand is the bone ozl_work on a loop: it goes around while working (OZL_Work,
# type = "loop") and stands at zero at rest.
SEL_LAMP, SEL_HAND = "ozl_lamp", "ozl_work"
# preview of the working look: the stopwatch hand at a quarter turn - by the engine turn (_posed
# below)
ON_MOVE = {}
ON = dict(remap={"bulb": "bulb_on", "lamp_in": "lamp_in_on"}, emissive=(1.0, 1.0, 1.0, 1.0), move=ON_MOVE)
HAND_TURNS = 1                                   # turns per pass of the loop (whole: no seam)
HAND_ANIM = ("ozl_work_hand", dict(type="rotation", source="ozl_work", sourceAddress="loop", selection=SEL_HAND,
                                   axis="ozl_work_axis", memory=1, minValue=0.0, maxValue=1.0 / HAND_TURNS,
                                   angle0=0.0, angle1=2 * math.pi))
# The stopwatch hand axis is the memory points ozl_work_axis: from bottom to top, toward
# someone looking at the dial from above. The engine turns a bone with a right-hand screw in
# DayZ axes (kexport.conv, determinant -1); in Blender axes this is a left-hand screw around
# the axis from the first point to the second: an axis pointing at the viewer gives a
# positive angle clockwise for them (as in M08, M12, M14, M33). With the axis pointing
# top-down the hand would go counterclockwise in the game.
HAND_AXIS = [(SW[0], SW[1], ZT + 0.0035), (SW[0], SW[1], ZT + 0.0135)]
HAND_PREVIEW = 0.25                              # working preview: a quarter turn, 12 to 3


def engine_turn(axis_pts, ang):
    """Turn of a bone by angle ang as the engine would do it by the memory axis axis_pts: (a point
    on the axis, the Blender axis for Matrix.Rotation - a right-hand screw, the angle). The
    Blender axis is opposite to the memory axis (from the second point to the first).
    """
    a, b = Vector(axis_pts[0]), Vector(axis_pts[1])
    return a, a - b, ang


def check_hand():
    """Numeric check: the engine's turn takes the stopwatch hand clockwise as seen from above:
    from 12 (the head, +y) to 3 (+x). If it does not match, the build fails.
    """
    o, ax, ang = engine_turn(HAND_AXIS, HAND_PREVIEW * HAND_ANIM[1]["angle1"])
    q = Matrix.Rotation(ang, 3, ax) @ Vector((0.0, 1.0, 0.0))
    assert q.x > 0.99, "the stopwatch hand goes counterclockwise"
    print("turns ok: the stopwatch hand goes clockwise from above, a quarter turn from 12 to 3")


check_hand()
# Proxies for the modules: the mod's CfgNonAIVehicles links the OZL_Tool1..3 slots to them
# (Proxyozl_tool1..3); slot N is module N of the "Protection" line (M84, M85, M86),
# unrotated: the modules face the person
PROXIES = [(r"\OpenZone_Research\models\proxies\ozl_tool%d" % (i + 1), m) for i, m in enumerate(MODS)]

# --- Vanilla items: no more than ~15, the extent check is check_decor() in --stats ------------
# The GP-5 on the bust is the worn DayZ model GP5GasMask_m, the one the game draws on a
# player's head: +Y is up, the face is toward -Z, the origin is at the feet, the mask is at
# a height of 1.52-1.80. The proxy is placed by a shift, without rotation: the head center
# under the mask (HC_M) goes to the center of the bust head. The ground model GP5GasMask_g
# is a crumpled mask lying on its side - it does not look worn at any rotation.
GP5_M = r"\dz\characters\masks\GP5GasMask_m"
# Filter slot of the worn model (the near-LOD header, like kvanilla.box; the numbers are the
# same as in M25 and M29): the rows are the filter X, Y, Z axes in mask axes, then the origin
# - the filter bottom; the neck is 0.0799 away along +Y
F_M = ((1.0, 0.0, 0.0), (0.0, 0.88373, 0.46799), (0.0, -0.46799, 0.88373), (-0.0001, 1.47915, -0.21021))
FILTER_H = 0.0799
# the mask itself (the near LOD without the filter proxy triangle - it inflates the bottom of the
# header extent to 1.409)
GP5_M_BOX = ((-0.099, 1.523, -0.199), (0.099, 1.804, 0.102))
HC_M = (0.0, 1.68, -0.02)                        # head center under the mask: axis x = 0, z = -0.02, eye level
BUST_Z = ZT + 0.016
HEAD_Y = BUST_Y - 0.016                          # bust head axis (the head center under the mask)
HEAD_H = 0.395                                   # height of the head center above the stand


def gp5_at(p_m):
    """A point of the worn GP-5 model -> Blender: +X -> +X, +Y (up) -> +Z, +Z (the back of the
    head) -> +Y, HC_M goes to the center of the bust head.
    """
    return Vector((BUST_X + p_m[0] - HC_M[0], HEAD_Y + p_m[2] - HC_M[2], BUST_Z + HEAD_H + p_m[1] - HC_M[1]))


GP5_ORIGIN = gp5_at((0.0, 0.0, 0.0))             # worn model origin (feet) = proxy origin
GP5_NECK = gp5_at(Vector(F_M[3]) + Vector(F_M[1]) * FILTER_H)      # filter neck: the hose adapter
GP5_AXIS = Vector((0.0, -F_M[1][2], -F_M[1][1]))                     # thread axis outward (down-forward)
GP5_CORNERS = [tuple(gp5_at((x, y, z))) for x in (GP5_M_BOX[0][0], GP5_M_BOX[1][0])
               for y in (GP5_M_BOX[0][1], GP5_M_BOX[1][1]) for z in (GP5_M_BOX[0][2], GP5_M_BOX[1][2])]
# Bust: the torso to mid-chest, shoulders, neck, a head without a face - sections (height
# above the stand, half-width, half-depth, shift forward(-)/back(+), superellipse exponent).
# The head (from 0.265) is by sections in the axes of the worn mask, like the M29 blank
# (build_m29.py HEAD_RINGS: y, half-width, forward and back from the axis x = 0, z = -0.02):
# it fills the mask like a player's head, 4-15 mm from the mask (checked against the points of
# the near, middle and far LODs of the mask)
HEAD_RINGS = [
    (1.550, 0.041, 0.021, 0.061), (1.565, 0.044, 0.034, 0.058), (1.580, 0.047, 0.058, 0.050),
    (1.600, 0.057, 0.070, 0.060), (1.620, 0.065, 0.077, 0.076), (1.640, 0.070, 0.080, 0.092),
    (1.660, 0.072, 0.079, 0.100), (1.680, 0.074, 0.081, 0.104), (1.700, 0.074, 0.080, 0.104),
    (1.720, 0.074, 0.072, 0.103), (1.730, 0.073, 0.067, 0.101), (1.740, 0.071, 0.063, 0.098),
    (1.750, 0.068, 0.060, 0.093), (1.760, 0.063, 0.056, 0.085), (1.770, 0.055, 0.049, 0.074),
    (1.780, 0.044, 0.037, 0.059), (1.788, 0.026, 0.023, 0.036), (1.7915, 0.012, 0.011, 0.017),
]
BUST_SEC = [
    (0.000, 0.146, 0.088, 0.000, 2.6), (0.040, 0.155, 0.092, 0.000, 2.6), (0.090, 0.164, 0.092, 0.006, 2.7),
    (0.130, 0.168, 0.086, 0.012, 2.8), (0.165, 0.170, 0.076, 0.016, 3.0), (0.190, 0.158, 0.066, 0.018, 3.0),
    (0.207, 0.122, 0.058, 0.018, 2.6), (0.222, 0.075, 0.051, 0.015, 2.2), (0.240, 0.050, 0.047, 0.010, 2.0),
] + [(HEAD_H + y - HC_M[1], w, (f + b) / 2, HEAD_Y - BUST_Y + (b - f) / 2, 2.0) for y, w, f, b in HEAD_RINGS]
# which sections go into the LODs: the near one - all, the middle and far - every second or third
# (top and bottom always)
BUST_LODS = (tuple(range(len(BUST_SEC))), (0, 3, 6, 8, 9, 11, 13, 15, 17, 19, 21, 23, 25, 26),
             (0, 4, 8, 11, 14, 17, 20, 23, 26))
# tray on the right door: a0, a1, bottom, depth; above the upper end of the table chain (at
# 1.02 the filter tray ran into the chain)
TRAY = (DOOR_W - 0.33, DOOR_W - 0.06, 1.42, 0.135)


def tray_pt(a):
    return tuple(LAYOUT["doors"][1].p(a, 0.069, TRAY[2]))


UPRIGHT = dict(up=(0, 0, 1), fwd=(0, -1, 0))
IN_TRAY = dict(up=(0, 0, 1), fwd=tuple(LAYOUT["doors"][1].v))           # the item box is along the door
DECOR = [
    # a GP-5 is worn on the bust - the worn model, by a shift (gp5_at); also in the far LOD -
    # otherwise a bare head shows from afar. kvanilla does not read the extent of the worn model
    # (it sits at 1.5-1.8 above the origin) - the preview box and check_decor use GP5_M_BOX,
    # with a key of their own
    (GP5_M, tuple(GP5_ORIGIN), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0), (0, 1, 2), "gp5_m"),
    kv.put("gp5", (-0.25, 0.137, ZT), **kv.flat(90)),                          # left compartment, by bags
    kv.put("ssh68", (-0.335, 0.27, SH_L1), **kv.flat(0)),
    kv.put("gp5filter", (-0.10, 0.20, SH_L1), **UPRIGHT),
    kv.put("ssh68", (-0.315, 0.27, SH_L2), **kv.flat(180)),
    kv.put("gp5filter", (-0.085, 0.34, SH_L2), **UPRIGHT),
    kv.put("gp5filter", (-0.09, 0.15, SH_L2), **kv.flat(90)),
    kv.put("ssh68", (0.155, 0.27, SH_R), **kv.flat(0)),
    kv.put("gp5filter", tray_pt(TRAY[0] + 0.07), **IN_TRAY),                  # right door tray
    kv.put("gp5filter", tray_pt(TRAY[0] + 0.195), **IN_TRAY),
    kv.put("pliers", (-0.34, -0.462, ZT), **kv.flat(-3)),                      # table front
    kv.put("screwdriver", (0.055, -0.472, ZT), **kv.flat(2)),
    kv.put("wrench", (0.285, -0.432, ZT), **kv.flat(176)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 selections=(SEL_LAMP, SEL_HAND), hidden=(SEL_LAMP,), states={"on": ON}, proxies=PROXIES,
                 bones=((SEL_HAND, ""),), animations=(HAND_ANIM,), decor=DECOR,
                 modules=[(o, n, m) for (o, n), m in zip(MOD_OBJ, MODS)],
                 sources={"ozl_work": dict(animPeriod=60.0)})
P = M.part
BOUNDS = {}
LAY = {}


def gp5_standin():
    """A blue GP-5 box on the bust in the preview - the extent of the worn mask (GP5_M_BOX),
    as in M29.
    """
    import bpy
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in GP5_CORNERS]
    for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
        bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new("standin_gp5")
    bm.to_mesh(me)
    bm.free()
    m = bpy.data.materials.get("vanilla_standin")
    if m is not None:
        me.materials.append(m)
    bpy.context.scene.collection.objects.link(bpy.data.objects.new(me.name, me))


def place_extras(with_modules=True):
    """Preview: like kmodel.Model.place_extras (blue vanilla boxes, modules in the slots), but the
    worn GP-5 is the gp5_standin box (kvanilla does not read its extent).
    """
    krender.standins([d for d in M.lod0_decor() if d[5] != "gp5_m"])
    gp5_standin()
    for obj, name, at in M.modules if with_modules else ():
        krender.our_model(obj, name, at)


M.place_extras = place_extras


# =============================================================================
# Primitives that kgeo lacks (lathe, along, upright, rod, bar - as in M29; spline - from M16)
# =============================================================================
def along(o, d):
    """Local axes with u along d (a tilted solid of revolution)."""
    d = Vector(d).normalized()
    ref = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    v = d.cross(ref).normalized()
    return g.Frame(o, d, v, d.cross(v))


def upright(o, deg=0.0):
    """Local axes of an upright solid of revolution: u - up, v - right, n - forward (toward -y at
    deg 0), rotated about the vertical by deg.
    """
    a = math.radians(deg)
    return g.Frame(o, (0, 0, 1), (math.cos(a), math.sin(a), 0), (math.sin(a), -math.cos(a), 0))


def face(part, verts, want):
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def lathe(part, prof, sides, frame, inward=False, caps=(False, False), kv=1.0, kn=1.0, want=None):
    """Solid of revolution around the u axis of the local axes frame: prof [(r, h)] - the radius
    and the place along u; the section is an ellipse r*kv along v and r*kn along n. inward -
    the surface looks toward the axis (the inside); caps - the ends (start, end) are closed;
    want - where all faces look (a flat ring).
    """
    bm = part.bm
    rings = []
    for r, h in prof:
        ring = []
        for k in range(sides):
            a = 2 * math.pi * k / sides
            ring.append(bm.verts.new(frame.p(h, r * kv * math.cos(a), r * kn * math.sin(a))))
        rings.append(ring)
    new = []
    for i in range(len(rings) - 1):
        for k in range(sides):
            j = (k + 1) % sides
            q = [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]
            c = sum((v.co for v in q), Vector()) / 4
            ax = frame.o + frame.u * (c - frame.o).dot(frame.u)
            out = c - ax
            new.append(face(part, q, want if want is not None else (-out if inward else out)))
    if caps[0]:
        new.append(face(part, rings[0], -frame.u))
    if caps[1]:
        new.append(face(part, rings[-1], frame.u))
    bm.normal_update()
    part.tag(new)


def rod(part, a, b, r, sides):
    return g.pipe(part, [tuple(a), tuple(b)], r, sides)


def bar(part, a, b, w, t):
    """Flat strip: width w horizontally, thickness t vertically, from point a to b."""
    a, b = Vector(a), Vector(b)
    u = (b - a).normalized()
    v = u.cross(Vector((0, 0, 1))).normalized()
    kcabinet.fbox(part, 0.0, (b - a).length, -w / 2, w / 2, -t / 2, t / 2, frame=g.Frame(a, u, v, u.cross(v)))


def bev(lod, r=0.003):
    return dict(r=r, seg=1) if lod == 0 else {}


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, from M16/M04)."""
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


def outward(part, faces):
    """A closed piece outward: the sign of the volume by the faces (as kcabinet.fbox) - in a
    mirrored frame (the right door) recomputing the normals could turn it inside out.
    """
    vol = 0.0
    for f in faces:
        vs = [v.co for v in f.verts]
        for i in range(1, len(vs) - 1):
            vol += vs[0].dot(vs[i].cross(vs[i + 1]))
    if vol < 0:
        for f in faces:
            f.normal_flip()
    part.bm.normal_update()


def closed_rings(part, rings, caps=(True, True)):
    """Faces between rings of vertices (of equal length) and the ends; outward."""
    bm = part.bm
    m = len(rings[0])
    new = []
    for i in range(len(rings) - 1):
        for k in range(m):
            j = (k + 1) % m
            new.append(bm.faces.new([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]))
    if caps[0]:
        new.append(bm.faces.new(rings[0][::-1]))
    if caps[1]:
        new.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    outward(part, new)
    part.tag(new)
    return new


def loft(part, secs, n, z0, cx, cy, kn=1.0):
    """A smooth body through superellipse sections (the bust): secs [(h, half-width along x,
    half-depth along y, shift along y, exponent)] from the bottom to the top; the ends are
    closed.
    """
    bm = part.bm
    rings = []
    for h, a, b, dy, p in secs:
        e = 2.0 / p
        ring = []
        for k in range(n):
            t = 2 * math.pi * k / n
            c, s = math.cos(t), math.sin(t)
            x = cx + a * math.copysign(abs(c) ** e, c)
            y = cy + dy + b * kn * math.copysign(abs(s) ** e, s)
            ring.append(bm.verts.new((x, y, z0 + h)))
        rings.append(ring)
    return closed_rings(part, rings)


def rrect(hw, hd, rc, nc):
    """Rounded rectangle, counterclockwise: half-sizes, corner radius, segments per corner."""
    rc = max(0.002, min(rc, hw - 0.001, hd - 0.001))
    pts = []
    for sx, sy, a0 in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        cx, cy = sx * (hw - rc), sy * (hd - rc)
        for k in range(nc + 1):
            a = math.radians(a0 + 90.0 * k / nc)
            pts.append((cx + rc * math.cos(a), cy + rc * math.sin(a)))
    return pts


def soft_box(part, x0, x1, y0, y1, z0, z1, rc, rz, nc, nz, bulge=0.0, frame=None):
    """Soft box (a canvas bag): the plan corners are rounded rc, the top and bottom edges rz (nz
    rings per edge), the sides slightly convex (bulge at mid-height). frame - local axes
    (a, b, c).
    """
    hw, hd = (x1 - x0) / 2, (y1 - y0) / 2
    xc, yc = (x0 + x1) / 2, (y0 + y1) / 2
    prof = [(z0 + rz * (1 - math.cos(math.pi / 2 * k / nz)), rz * (1 - math.sin(math.pi / 2 * k / nz)))
            for k in range(nz + 1)]
    if bulge:
        prof.append(((z0 + z1) / 2, -bulge))
    prof += [(z1 - rz * (1 - math.cos(math.pi / 2 * k / nz)), rz * (1 - math.sin(math.pi / 2 * k / nz)))
             for k in range(nz, -1, -1)]
    bm = part.bm
    rings = []
    for z, ins in prof:
        ring = []
        for px, py in rrect(hw - ins, hd - ins, rc - ins, nc):
            p = (xc + px, yc + py, z)
            ring.append(bm.verts.new(frame.p(*p) if frame else Vector(p)))
        rings.append(ring)
    return closed_rings(part, rings)


def to_world(frame, p):
    return tuple(frame.p(*p)) if frame else tuple(p)


# =============================================================================
# Cabinet (the shared base) and own small parts on it: ventilation cutouts on the doors, a socket in
# the right compartment
# =============================================================================
def build_cabinet(spec):
    parts, lay = kcabinet.cabinet(M, spec, X0, X1, Y0, Y1, H, table_z=ZT, table_d=TD, door_deg=DOOR_DEG,
                                  shelves=SHELVES, partitions=PARTITIONS, regions=dict(chain="chain"))
    LAY.update(lay)
    return parts


def build_cabinet_extra(spec):
    """Ventilation cutouts at the top and bottom of each door (louvres on the doors of the
    reference cabinet) - seen from inside as dark slots in the sheet; a socket on the right
    wall of the compartment (the lamp cord).
    """
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    w = LAY["door_w"]
    zd0, zd1 = LAY["door_z"]
    for f, sd in zip(LAY["doors"], "lr"):
        vp = P("door_vents_" + sd, "vent")
        nslot = 7 if lod == 0 else 1
        for zb in (zd1 - 0.20, zd0 + 0.10):
            for k in range(nslot):
                c0 = zb + k * 0.015 if lod == 0 else zb
                c1 = c0 + 0.007 if lod == 0 else zb + 0.097
                a0, a1 = w * 0.28, w * 0.72
                b = 0.0047
                vs = [vp.bm.verts.new(f.p(a, b, c)) for a, c in ((a0, c0), (a1, c0), (a1, c1), (a0, c1))]
                vp.tag([face(vp, vs, f.v)])
        parts.append(vp)
    # socket: a bakelite box on the right wall of the compartment, the lamp cord plug
    so = P("socket", "bakelite")
    g.box(so, XI1 - 0.026, XI1, 0.085, 0.155, ZT + 0.035, ZT + 0.105)
    if lod == 0:
        lathe(so, [(0.0135, 0.026), (0.0135, 0.041), (0.0075, 0.044), (0.0075, 0.054)], 8,
              g.Frame((XI1, 0.12, ZT + 0.07), (-1, 0, 0), (0, 1, 0), (0, 0, 1)), caps=(True, True))   # plug
    parts.append(so)
    return parts


# =============================================================================
# Props: a GP-5 bag, a cylinder
# =============================================================================
def bag(name, x0, x1, y0, y1, z0, h, lod, strap=True, flap=0.10, frame=None):
    """GP-5 bag standing, facing -y (in the local axes frame): a soft box, a flap - a sheet over
    the top edge and down the face, a button, a tape strap across the top. The box, flap and
    strap are different parts (they lie on one another and would share texels in the atlas;
    each bag has its own parts for the same reason).
    """
    part = P(name, "bag")
    z1 = z0 + h
    if lod == 2:
        kcabinet.fbox(part, x0, x1, y0, y1, z0, z1, frame=frame or g.Frame((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)))
        return [part]
    rz, bul = 0.016, (0.006 if lod == 0 else 0.0)
    zb = z1 - 0.004
    soft_box(part, x0, x1, y0, y1, z0, zb, 0.028, rz, 2 if lod == 0 else 1, 2 if lod == 0 else 1, bulge=bul,
             frame=frame)
    parts = [part]
    # flap: a 4 mm sheet from the rear third of the top forward, along the edge rounding and down
    # the face
    fp = P(name + "_flap", "bag")
    t = 0.004
    xc = (x0 + x1) / 2
    R = rz + t / 2 + 0.0008
    cyz = (y0 + rz, zb - rz)
    path = [(y1 - 0.03, zb + t / 2 + 0.0008), ((y0 + y1) / 2, zb + t / 2 + 0.0008)]
    for k in range(5 if lod == 0 else 2):
        ph = math.pi / 2 * k / (4 if lod == 0 else 1)
        path.append((cyz[0] - R * math.sin(ph), cyz[1] + R * math.cos(ph)))
    path += [(y0 - t / 2 - 0.0008 - bul * 0.7, zb - flap * 0.55), (y0 - t / 2 - 0.0008 - bul, zb - flap)]
    nrm = (frame.u if frame else Vector((1, 0, 0)))
    g.sweep(fp, [to_world(frame, (xc, y, z)) for y, z in path], nrm, t / 2, (x1 - x0) / 2 + 0.003)
    parts.append(fp)
    if lod > 0:
        return parts
    bt = P(name + "_button", "button")
    bc = to_world(frame, (xc, y0 - t - 0.0010 - bul, zb - flap + 0.022))
    lathe(bt, [(0.0075, 0.0), (0.0055, 0.004)], 8, along(bc, -frame.v if frame else (0, -1, 0)), caps=(True, True))
    parts.append(bt)
    if strap:
        # strap: tape across the top of the bag, the ends go down the sides (sewn to the sides)
        ym = (y0 + y1) / 2 + 0.01
        sp = P(name + "_strap", "strap")
        pts = spline([(x0 - 0.0085, ym, zb - 0.07), (x0 - 0.0085, ym, zb - 0.02), (x0 + 0.012, ym, zb + 0.009),
                      (xc, ym + 0.012, zb + 0.016), (x1 - 0.012, ym, zb + 0.009), (x1 + 0.0085, ym, zb - 0.02),
                      (x1 + 0.0085, ym, zb - 0.07)], 2)
        nrm = frame.v if frame else Vector((0, 1, 0))
        g.sweep(sp, [to_world(frame, p) for p in pts], nrm, 0.0012, 0.011)
        parts.append(sp)
    return parts


def tank(name, fr, lod, n=None, simple=False):
    """7 l cylinder along u of frame fr from the bottom: dia 140 x 0.53, black with a white band,
    a shoulder to the neck, a valve: a brass body, a side fitting with a nut, a handwheel
    (simple - lying in the lower compartment: a valve without a fitting, coarser).
    """
    body = P(name, "tank")
    n = n or (12 if lod == 0 else 8 if lod == 1 else 6)
    R, L = TANK_R, TANK_L
    if lod == 2:
        lathe(body, [(0.05, 0.0), (R, 0.03), (R, L - 0.09), (0.03, L)], n, fr, caps=(True, True))
        return [body]
    bot = [(0.042, 0.0), (0.064, 0.008), (R, 0.032)] if lod == 0 else [(0.05, 0.0), (R, 0.03)]
    top = [(R, L - 0.09), (0.0665, L - 0.060), (0.0560, L - 0.034), (0.0380, L - 0.016), (0.0240, L - 0.006),
           (0.0220, L)]
    if lod > 0:
        top = [top[0], top[2], top[4], top[5]]
    band = P(name + "_band", "band")
    lathe(body, bot + [(R, L - 0.17)], n, fr, caps=(True, False))
    lathe(band, [(R + 0.0004, L - 0.17), (R + 0.0004, L - 0.09)], n, fr)
    lathe(body, top, n, fr, caps=(False, True))
    if lod > 0:
        return [body, band]
    valve = P(name + "_valve", "valve")
    vo = fr.o + fr.u * L
    vf = g.Frame(vo, fr.u, fr.v, fr.n)
    hw = vo + fr.u * 0.062
    if simple:
        lathe(valve, [(0.0175, 0.0), (0.0175, 0.042), (0.0085, 0.062)], 6, vf, caps=(True, True))
        lathe(valve, [(0.006, 0.0), (0.028, 0.003), (0.006, 0.012)], 8, g.Frame(hw, fr.u, fr.v, fr.n), caps=(True, True))
        return [body, band, valve]
    lathe(valve, [(0.017, 0.0), (0.0185, 0.005), (0.0185, 0.040), (0.0105, 0.047), (0.0085, 0.062)],
          8, vf, caps=(True, True))
    # side fitting with a coupling nut
    so = vo + fr.u * 0.024
    lathe(valve, [(0.0075, 0.016), (0.0075, 0.030), (0.0105, 0.031), (0.0105, 0.043)], 6,
          g.Frame(so, fr.v, fr.n, fr.u), caps=(False, True))
    # handwheel: a rim, a hub
    lathe(valve, [(0.006, 0.0), (0.0285, 0.002), (0.0285, 0.010), (0.006, 0.012)], 9,
          g.Frame(hw, fr.u, fr.v, fr.n), caps=(True, True))
    return [body, band, valve]


# =============================================================================
# Left compartment: helmets and filters on the shelves (vanilla), bags on the bottom
# =============================================================================
def build_left(spec):
    lod = spec["lod"]
    parts = []
    # compartment bottom: two GP-5 bags stand by the back, a vanilla GP-5 lies in front of them
    # (DECOR)
    parts += bag("bag_l0", -0.455, -0.245, 0.30, 0.40, ZT, 0.23, lod)
    parts += bag("bag_l1", -0.23, -0.02, 0.275, 0.375, ZT, 0.225, lod, strap=False, flap=0.09)
    return parts


# =============================================================================
# Right compartment: cylinders under a strap, a helmet (vanilla) on the shelf and a bag lying
# =============================================================================
def build_right(spec):
    lod = spec["lod"]
    parts = []
    yc = YI1 - TANK_R - 0.004
    for i, x in enumerate((0.105, 0.27)):
        parts += tank("tank_up%d" % i, upright((x, yc, ZT + 0.002)), lod)
    if lod == 0:
        # collar: a 25 x 2.5 mm steel strap around the cylinders, the ends on angles at the back
        st = P("tank_clamp", "steel")
        zc = ZT + 0.33
        r = TANK_R + 0.0035
        kk = 5
        pts = [(0.022, YI1 - 0.003, zc)]
        for x in (0.105, 0.27):
            for k in range(kk + 1):
                a = math.radians(180 + 180 * k / kk)
                pts.append((x + r * math.cos(a), yc + r * math.sin(a), zc))
        pts.append((0.353, YI1 - 0.003, zc))
        g.sweep(st, pts, (0, 0, 1), 0.00125, 0.0125)
        for xe in (0.022, 0.353):
            g.box(st, xe - 0.012, xe + 0.012, YI1 - 0.022, YI1, zc - 0.02, zc + 0.02)                # angles
            g.cyl(st, (xe, YI1 - 0.024, zc), "y", 0.0065, 0.006, 6)                                  # bolts
        parts.append(st)
    if lod == 2:
        return parts
    # shelf: next to the helmet a bag lying (flap up)
    parts += bag("bag_r", 0.30, 0.47, 0.20, 0.42, SH_R, 0.095, lod, strap=False, flap=0.05)
    return parts


# =============================================================================
# Lower compartment: a wooden crate with a bundle, two cylinders lying on pads
# =============================================================================
def build_lower(spec):
    lod = spec["lod"]
    parts = []
    cr = P("crate", "crate")
    x0, x1, y0, y1, h = -0.47, -0.15, 0.06, 0.40, 0.30
    z0 = ZI0
    zl = z0 + h - 0.022                                     # bottom of the lid
    if lod == 2:
        g.box(cr, x0, x1, y0, y1, z0, z0 + h)
        return [cr]
    # body slightly inside, three boards with gaps on the face and the right side, two end
    # battens on the face, an overlapping lid with two battens
    g.box(cr, x0 + 0.006, x1 - 0.006, y0 + 0.006, y1 - 0.006, z0, zl)
    hb = (zl - z0) / 3
    for k in range(3 if lod == 0 else 1):
        za, zb = (z0 + k * hb + 0.002, z0 + (k + 1) * hb - 0.002) if lod == 0 else (z0, zl)
        g.box(cr, x0 + 0.02, x1 - 0.02, y0, y0 + 0.008, za, zb)                                  # face
        g.box(cr, x1 - 0.008, x1, y0 + 0.02, y1 - 0.02, za, zb)                                  # right side
    if lod == 0:
        for xa in (x0, x1 - 0.022):
            g.box(cr, xa, xa + 0.022, y0 - 0.004, y0 + 0.02, z0, zl)                             # face battens
    g.box(cr, x0 - 0.004, x1 + 0.004, y0 - 0.008, y1 + 0.004, zl, z0 + h, **bev(lod, 0.004))   # lid
    if lod == 0:
        for xa in (x0 + 0.04, x1 - 0.064):
            g.box(cr, xa, xa + 0.024, y0 - 0.006, y1 + 0.002, z0 + h, z0 + h + 0.012)
    parts.append(cr)
    if lod == 0:
        st = P("crate_handle", "steel")
        yc, zc = (y0 + y1) / 2, z0 + h * 0.6
        g.pipe(st, [(x1, yc - 0.06, zc + 0.01), (x1 + 0.022, yc - 0.055, zc - 0.012),
                    (x1 + 0.026, yc, zc - 0.022), (x1 + 0.022, yc + 0.055, zc - 0.012),
                    (x1, yc + 0.06, zc + 0.01)], 0.0045, 6)
        for s in (-1, 1):
            g.box(st, x1, x1 + 0.006, yc + s * 0.06 - 0.012, yc + s * 0.06 + 0.012, zc - 0.005, zc + 0.03)
        parts.append(st)
    # canvas bundle on the lid: a roll with cinched ends and two ties
    rl = P("roll", "roll")
    zr = z0 + h + (0.012 if lod == 0 else 0.0) + 0.052
    xs = [x0 + 0.02, x0 + 0.04, x0 + 0.08, (x0 + x1) / 2, x1 - 0.08, x1 - 0.04, x1 - 0.02]
    rad = [(0.030, 0.024), (0.052, 0.044), (0.064, 0.052), (0.066, 0.053), (0.064, 0.052), (0.052, 0.044),
           (0.030, 0.024)]
    ys = [0.226, 0.222, 0.224, 0.221, 0.219, 0.222, 0.220]
    sel = range(7) if lod == 0 else (0, 2, 4, 6)
    g.tube_var(rl, [(xs[i], ys[i], zr - (0.052 - rad[i][1]) * 0.9) for i in sel], [rad[i] for i in sel],
               10 if lod == 0 else 6)
    parts.append(rl)
    if lod == 0:
        for i, x in enumerate((x0 + 0.10, x1 - 0.10)):
            rt = P("roll_tie%d" % i, "strap")
            lathe(rt, [(0.0675, -0.009), (0.0675, 0.009)], 14, g.Frame((x, 0.222, zr), (1, 0, 0), (0, 1, 0), (0, 0, 1)),
                  kn=0.80)
            parts.append(rt)
    # cylinders lying, valve to the left, on two pads with cutouts for the cylinders
    ys_t = (0.13, 0.31)
    for i, x in enumerate((0.0, 0.36)):
        ch = P("chock%d" % i, "chock")
        zb, zt = ZI0, ZI0 + 0.045
        poly = [(0.04, zb), (0.44, zb), (0.44, zt)]
        for yt in reversed(ys_t):
            poly += [(yt + 0.05, zt), (yt, zb + 0.02), (yt - 0.05, zt)]
        poly.append((0.04, zt))
        g.prism(ch, poly, (1, 2), x - 0.025, x + 0.025)
        parts.append(ch)
    zc_t = ZI0 + 0.02 + TANK_R / 0.894
    for i, y in enumerate(ys_t):
        # bottom at the right wall, the valve toward the crate
        parts += tank("tank_low%d" % i, g.Frame((0.47, y, zc_t), (-1, 0, 0), (0, 1, 0), (0, 0, 1)), lod,
                      n=10 if lod == 0 else 6, simple=True)
    return parts


# =============================================================================
# Doors: a bag on hooks on the left, a tray with filters (vanilla) on the right, a seal, tags on the
# shelves
# =============================================================================
def build_doors_extra(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    fl, fr = LAY["doors"]
    w = LAY["door_w"]
    parts = []
    # GP-5 bag on the left door inside: local axes with b from the sheet toward the person (the
    # bag face looks into the cabinet), the sheet inside is at 0.0045; above the upper end of the
    # table chain (at 1.12 the chain passed through the bag)
    flb = g.Frame(fl.o, fl.u, -fl.v, fl.n)
    a0, a1, z0, z1 = 0.12, 0.33, 1.40, 1.63
    parts += bag("door_bag", a0, a1, -0.10, -0.0045, z0, z1 - z0, lod, strap=False, frame=flb)
    if lod == 0:
        hk = P("door_hooks", "steel")
        for a in (a0 + 0.03, a1 - 0.03):
            kcabinet.fbox(hk, a - 0.006, a + 0.006, 0.0045, 0.012, z1 + 0.03, z1 + 0.06, frame=fl)
            g.pipe(hk, [fl.p(a, 0.010, z1 + 0.045), fl.p(a, 0.03, z1 + 0.05), fl.p(a, 0.036, z1 + 0.065)], 0.0028, 6)
        parts.append(hk)
        sp = P("door_bag_strap", "strap")
        # strap loops from the top of the bag onto the hooks
        for a in (a0 + 0.03, a1 - 0.03):
            pts = [(a, -0.035, z1 - 0.002), (a, -0.03, z1 + 0.03), (a, -0.027, z1 + 0.058),
                   (a, -0.018, z1 + 0.066), (a, -0.010, z1 + 0.05)]
            g.sweep(sp, [to_world(flb, p) for p in pts], flb.u, 0.0012, 0.010)
        parts.append(sp)
    # tray on the right door inside: a bottom, a rim with a rolled edge, ends; in it two vanilla
    # GP-5 filter canisters (DECOR)
    tr = P("door_tray", "tray")
    ta0, ta1, tz, td = TRAY
    kcabinet.fbox(tr, ta0, ta1, 0.0045, td, tz - 0.004, tz, frame=fr)
    kcabinet.fbox(tr, ta0, ta1, td - 0.004, td, tz, tz + 0.05, frame=fr)
    for a in (ta0, ta1 - 0.004):
        kcabinet.fbox(tr, a, a + 0.004, 0.0045, td - 0.004, tz, tz + 0.05, frame=fr)
    if lod == 0:
        g.pipe(tr, [fr.p(ta0, td - 0.002, tz + 0.05), fr.p(ta1, td - 0.002, tz + 0.05)], 0.003, 6)
    parts.append(tr)
    # lead seal on a wire under the right door handle (outside)
    if lod == 0:
        sl = P("seal", "seal")
        zh = kcabinet.FOOT + 0.98
        ah = w - 0.055
        out = -fr.v
        a = fr.p(ah, -0.024, zh - 0.095)
        c = fr.p(ah + 0.004, -0.012, zh - 0.16)
        g.pipe(sl, [a, a.lerp(c, 0.5) + out * 0.004, c], 0.0012, 4)
        lathe(sl, [(0.010, 0.0), (0.011, 0.003), (0.010, 0.006)], 8, along(c, out), caps=(True, True))
        parts.append(sl)
    # blank aluminium tags on the shelf edges
    tg = P("shelf_tags", "tag")
    for xa, xb, z in SHELVES:
        xc = (xa + xb) / 2
        g.box(tg, xc - 0.04, xc + 0.04, 0.0285, 0.03, z - 0.026, z - 0.006)
    parts.append(tg)
    return parts


# =============================================================================
# Table: a mannequin bust in a GP-5, a hose to the M84 place, the M86 pad, a work lamp, a stopwatch
# =============================================================================
def build_bust(spec):
    lod = spec["lod"]
    n = 14 if lod == 0 else 8 if lod == 1 else 6
    parts = []
    st = P("bust_base", "stand")
    prof = [(0.150, 0.0), (0.153, 0.006), (0.147, 0.016)] if lod == 0 else [(0.152, 0.0), (0.150, 0.016)]
    lathe(st, prof, 20 if lod == 0 else 8, upright((BUST_X, BUST_Y, ZT)), caps=(True, True), kn=0.68)
    parts.append(st)
    bs = P("bust", "head")
    loft(bs, [BUST_SEC[i] for i in BUST_LODS[lod]], n, BUST_Z, BUST_X, BUST_Y)
    parts.append(bs)
    return parts


def build_hose(spec):
    """The filter is unscrewed from the worn GP-5, a brass adapter is screwed into the neck of the
    valve box (as in M29); from it a hose runs down in front of the bust chest and along the
    table to the M84 place, a brass coupling at the end (without the module it lies on the
    table - a "hose without a device").
    """
    lod = spec["lod"]
    if lod == 2:
        return []
    ax = GP5_AXIS
    h0 = GP5_NECK + ax * 0.040
    pts = [tuple(h0), tuple(h0 + ax * 0.02), (-0.240, -0.494, 1.02), (-0.215, -0.484, 0.94),
           (-0.185, -0.474, ZT + 0.035), (-0.155, -0.466, ZT + 0.008), (-0.120, -0.457, ZT + 0.0065),
           (-0.088, -0.443, ZT + 0.0065), (-0.062, -0.425, ZT + 0.0065)]
    hs = P("test_hose", "hose")
    g.pipe(hs, spline(pts, 3 if lod == 0 else 1), 0.0062, 6 if lod == 0 else 4)
    parts = [hs]
    cp = P("test_hose_fittings", "valve")
    # adapter: a thread in the neck, a wrench flat band, a barb for the hose (as in M29)
    fa = along(GP5_NECK, ax)
    lathe(cp, [(0.0185, -0.004), (0.0205, 0.0), (0.0205, 0.016), (0.016, 0.020), (0.0085, 0.024)],
          14 if lod == 0 else 8, fa, caps=(True, True))
    lathe(cp, [(0.0072, 0.024), (0.0085, 0.031), (0.0066, 0.035), (0.0080, 0.042)], 10 if lod == 0 else 6, fa)
    if lod == 0:
        # at the end - a quick-release coupling
        e0, e1 = Vector(pts[-2]), Vector(pts[-1])
        d = (e1 - e0).normalized()
        lathe(cp, [(0.0072, 0.0), (0.0098, 0.004), (0.0098, 0.020), (0.0115, 0.023), (0.0080, 0.033)], 8,
              along(e1 - d * 0.002, d), caps=(True, True))
    parts.append(cp)
    return parts


def build_ply(spec):
    """Slot 3: a plywood pad under the M86 plate clamp (when empty - plywood with dents from the
    plate).
    """
    lod = spec["lod"]
    cx, cy, w, d, t = PLY
    pl = P("slot3_ply", "ply")
    g.box(pl, cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2, ZT, ZT + t, **bev(lod, 0.002))
    return [pl]


def build_lamp(spec):
    """Work lamp on hinges in the right rear corner of the table: a cast iron base with a button,
    a post, two pairs of rods on hinges with thumbscrews, a socket body, a conical reflector
    with a rolled edge above the M86 place; the bulb and the white inside of the reflector are
    ozl_lamp; the cord goes to the socket on the right wall.
    """
    lod = spec["lod"]
    n = 16 if lod == 0 else 8 if lod == 1 else 6
    parts = []
    base = P("lamp_base", "cast")
    bp = [(0.080, 0.0), (0.082, 0.004), (0.072, 0.018), (0.034, 0.029), (0.020, 0.034)]
    lathe(base, bp if lod == 0 else [bp[i] for i in (0, 2, 4)], n, upright((LAMP_X, LAMP_Y, ZT)), caps=(True, True))
    parts.append(base)
    j0 = Vector((LAMP_X, LAMP_Y, ZT + 0.068))
    j1 = Vector((LAMP_X + 0.012, LAMP_Y + 0.020, ZT + 0.40))
    j2 = Vector((PLY[0] + 0.035, PLY[1] + 0.115, ZT + 0.47))
    ax = (j1 - j0).cross(j2 - j1).normalized()                   # hinge axes: across the rod plane
    if lod < 2:
        ps = P("lamp_post", "cast")
        g.cyl(ps, (LAMP_X, LAMP_Y, ZT + 0.046), "z", 0.013, 0.026, 10 if lod == 0 else 5)
        parts.append(ps)
    if lod == 0:
        sw = P("lamp_switch", "bakelite")
        g.box(sw, LAMP_X - 0.012, LAMP_X + 0.012, LAMP_Y - 0.072, LAMP_Y - 0.050, ZT + 0.016, ZT + 0.030)
        g.cyl(sw, (LAMP_X, LAMP_Y - 0.061, ZT + 0.034), "z", 0.0055, 0.008, 8)
        parts.append(sw)
    ar = P("lamp_arm", "lamp")
    a2 = P("lamp_arm2", "lamp") if lod == 0 else None
    for a, b in ((j0, j1), (j1, j2)):
        rod(ar, a, b, 0.0065, 8 if lod == 0 else 4)
        if lod == 0:
            off = ax.cross((b - a).normalized()) * 0.017            # second rod of the parallelogram
            rod(a2, a + off, b + off, 0.0042, 6)
    parts += [ar] + ([a2] if a2 else [])
    if lod == 0:
        jt = P("lamp_joints", "cast")
        for j in (j0, j1, j2):
            rod(jt, j - ax * 0.017, j + ax * 0.017, 0.0125, 8)
            if j is not j0:
                rod(jt, j + ax * 0.017, j + ax * 0.026, 0.006, 6)                                  # screw
                kcabinet.fbox(jt, -0.004, 0.004, -0.016, 0.016, 0.0, 0.003,
                              frame=g.Frame(j + ax * 0.026, ax.cross(Vector((0, 0, 1))).normalized(),
                                            Vector((0, 0, 1)), ax))                                  # thumbscrew
        parts.append(jt)
    # reflector: a cone from the hinge down onto the M86 pad (slightly forward - the light also
    # falls on the stopwatch)
    d = Vector((-0.20, -0.55, -1.0)).normalized()
    so = j2 + d * 0.03
    fr = along(so, d)
    hs = P("lamp_housing", "lamp")
    lathe(hs, [(0.019, -0.034), (0.023, -0.030), (0.023, -0.004), (0.020, 0.0)] if lod == 0 else
          [(0.021, -0.034), (0.021, 0.0)], 10 if lod == 0 else 6, fr, caps=(True, False))
    rod(hs, j2, so - d * 0.017, 0.006, 6 if lod == 0 else 4)
    parts.append(hs)
    sh = P("lamp_shade", "lamp")
    prof = [(0.021, 0.0), (0.027, 0.018), (0.041, 0.046), (0.061, 0.086), (0.075, 0.113), (0.081, 0.124),
            (0.0835, 0.128)]
    pr = prof if lod == 0 else [prof[i] for i in (0, 2, 4, 6)]
    lathe(sh, pr, n, fr, caps=(True, False))
    parts.append(sh)
    if lod < 2:
        li = P("lamp_reflector", "lamp_in", group=SEL_LAMP)
        rin = [(r - 0.0028, h + 0.0025) for r, h in pr[1:]]
        lathe(li, rin, n, fr, inward=True)
        lathe(li, [(pr[-1][0], pr[-1][1]), (rin[-1][0], rin[-1][1])], n, fr, want=fr.u)       # rolled edge
        parts.append(li)
    bl = P("lamp_bulb", "bulb", group=SEL_LAMP)
    bpz = [(0.008, 0.022), (0.022, 0.045), (0.029, 0.070), (0.020, 0.094), (0.004, 0.103)]
    lathe(bl, bpz if lod == 0 else [bpz[i] for i in (0, 2, 4)], 10 if lod == 0 else 6, fr, caps=(True, True))
    parts.append(bl)
    if lod == 0:
        cb = P("lamp_cable", "cable")
        pts = [(LAMP_X + 0.05, LAMP_Y + 0.055, ZT + 0.006), (LAMP_X + 0.065, LAMP_Y + 0.10, ZT + 0.0045),
               (0.445, 0.07, ZT + 0.0045), (0.44, 0.112, ZT + 0.012), (0.437, 0.12, ZT + 0.04),
               (XI1 - 0.055, 0.12, ZT + 0.07)]
        g.pipe(cb, spline(pts, 2), 0.0040, 5)
        parts.append(cb)
    return parts


def build_stopwatch(spec):
    """Mechanical stopwatch lying on the table: a chrome case dia 55 with a rim, a white dial
    with ticks, a red hand (ozl_work - goes around while working), a head with a lug toward +y.
    """
    lod = spec["lod"]
    if lod > 0:
        return []
    cx, cy = SW
    n = 14
    zd = ZT + 0.0122                                             # dial
    cs = P("sw_case", "chrome")
    prof = [(0.0205, 0.0), (0.0262, 0.0025), (0.0275, 0.0080), (0.0258, 0.0132), (0.0234, 0.0146),
            (0.0224, zd - ZT - 0.0005)]
    lathe(cs, prof if lod == 0 else [prof[i] for i in (0, 2, 4, 5)], n, upright((cx, cy, ZT)), caps=(True, False))
    parts = [cs]
    dl = P("sw_dial", "dial")
    lathe(dl, [(0.0226, 0.0), (0.0226, 0.0006)], n, upright((cx, cy, zd - 0.0006)), caps=(False, True))
    parts.append(dl)
    if lod == 0:
        # ticks: every five seconds, long and thick at 0/15/30/45; flat, facing up
        tk = P("sw_ticks", "black")
        for k in range(12):
            a = 2 * math.pi * k / 12
            r0, hw_ = (0.0168, 0.0008) if k % 3 == 0 else (0.0188, 0.00045)
            ca, sa = math.cos(a), math.sin(a)
            q = [(r0, -hw_), (0.0213, -hw_), (0.0213, hw_), (r0, hw_)]
            vs = [tk.bm.verts.new((cx + r * sa + w * ca, cy + r * ca - w * sa, zd + 0.0002)) for r, w in q]
            tk.tag([face(tk, vs, (0, 0, 1))])
        parts.append(tk)
        # head with a lug toward +y; the lug lies inclined to the table
        cr = P("sw_crown", "chrome")
        lathe(cr, [(0.0028, 0.027), (0.0028, 0.0335), (0.0042, 0.0345), (0.0042, 0.0405)], 8,
              g.Frame((cx, cy, ZT + 0.0075), (0, 1, 0), (1, 0, 0), (0, 0, 1)), caps=(False, True))
        c = Vector((cx, cy + 0.0478, ZT + 0.0050))
        dv = Vector((0, math.cos(math.radians(16)), -math.sin(math.radians(16))))
        ring = [tuple(c + 0.0080 * (math.cos(2 * math.pi * k / 10) * Vector((1, 0, 0)) +
                                    math.sin(2 * math.pi * k / 10) * dv)) for k in range(11)]
        g.pipe(cr, ring, 0.0014, 4)
        parts.append(cr)
    hd = P("sw_hand", "hand", group=SEL_HAND)
    bar(hd, (cx, cy - 0.0050, zd + 0.0009), (cx, cy + 0.0200, zd + 0.0009), 0.0011, 0.0005)
    if lod == 0:
        g.cyl(hd, (cx, cy, zd + 0.0010), "z", 0.0017, 0.0014, 8)
    parts.append(hd)
    return parts


def check_decor():
    """--stats: the extents of the vanilla items (kv.corners) and the intersections of the boxes
    with one another and with the module places - the items must not hang, sink or intersect.
    """
    world = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    boxes = []                                       # (name, 8 corners, box axes)
    for d in DECOR:
        q = GP5_CORNERS if d[5] == "gp5_m" else kv.corners(d[5], d[1], d[2], d[3])
        lo = tuple(min(c[i] for c in q) for i in range(3))
        hi = tuple(max(c[i] for c in q) for i in range(3))
        boxes.append((d[5], q, kv.axes(d[2], d[3])))
        print("decor %-12s lo (%.3f %.3f %.3f) hi (%.3f %.3f %.3f)" % ((d[5],) + lo + hi))
    for (o, _), m, (w, db, df, hh) in zip(MOD_OBJ, MODS, MOD_BOX):
        q = [(x, y, z) for x in (m[0] - w / 2, m[0] + w / 2) for y in (m[1] - df, m[1] + db) for z in (m[2], m[2] + hh)]
        boxes.append((o, q, world))
    hits = 0
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            # separating axes - the sides of both boxes (rotated items in the door tray)
            ov = []
            for ax in a[2] + b[2]:
                pa = [sum(c[k] * ax[k] for k in range(3)) for c in a[1]]
                pb = [sum(c[k] * ax[k] for k in range(3)) for c in b[1]]
                ov.append(min(max(pa), max(pb)) - max(min(pa), min(pb)))
            if all(v > 0.0005 for v in ov):
                hits += 1
                print("decor overlap: %s x %s by %.3f" % (a[0], b[0], min(ov)))
    print("decor: %d items, %d overlaps" % (len(DECOR), hits))


def build_lod(spec):
    parts = build_cabinet(spec) + build_cabinet_extra(spec) + build_left(spec) + build_right(spec)
    parts += build_lower(spec) + build_doors_extra(spec) + build_bust(spec) + build_hose(spec) + build_ply(spec)
    parts += build_lamp(spec) + build_stopwatch(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        if "--stats" in sys.argv:
            check_decor()
    return parts


def collision():
    metal = kx.PEN + r"\metalplate.rvmat"
    # as in M32: the body, the table down to the floor, the doors - boxes no thinner than 0.5 m,
    # equally on both sides of the sheet
    cab = kx.box_pts(X0, X1, Y0, Y1, 0.0, H + 0.02)
    table = kx.box_pts(X0, X1, -TD - 0.02, Y0 + 0.01, 0.0, ZT + 0.02)
    comps = [(cab, metal), (table, metal)]
    for s in (-1, 1):
        xc = s * (X1 + 0.065)
        comps.append((kx.box_pts(xc - 0.25, xc + 0.25, -0.50, 0.0, 0.0, H - 0.03), metal))
    memory = {
        "invView": [(-0.3, -2.6, 1.4)],
        "ce_center": [(0.0, 0.0, H / 2)],
        "ce_radius": [(1.1, 0.0, H / 2)],
        # stopwatch hand axis, like the M16 spindle axis
        "ozl_work_axis": HAND_AXIS,                      # up, toward person (HAND_AXIS)
    }
    for i, m in enumerate(MODS):
        memory["module_%d" % (i + 1)] = [m]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2] + 0.004)
    return comps, 180.0, memory, bbox


# The first ones are for the --look preview: overall view, the table with the modules in
# place (and empty), the lamp above M86 with the stopwatch, the bust in a GP-5 with the hose
# to M84, helmets on the shelves at the left, cylinders at the right
SHOTS = [
    ("front", (-1.1, -2.6, 1.65), (0.0, 0.0, 1.0), 30),
    ("table", (0.05, -1.25, 1.55), (0.02, -0.22, 0.98), 34),
    ("lamp", (0.50, -1.15, 1.30), (0.30, -0.25, 1.08), 36),
    ("bust", (-0.32, -1.02, 1.17), (-0.13, -0.38, 0.96), 40),
    ("left", (0.15, -1.05, 1.62), (-0.42, -0.15, 1.40), 32),
    ("right", (0.35, -1.0, 1.45), (0.24, 0.25, 1.25), 34),
    ("lower", (0.3, -1.4, 0.45), (0.0, 0.2, 0.35), 32),
    ("door_left", (-1.5, -1.2, 1.45), (-0.56, -0.26, 1.35), 34),
    ("door_right", (1.2, -1.4, 1.45), (0.56, -0.26, 1.30), 34),
    ("back", (1.4, 2.0, 1.7), (0.0, 0.0, 0.95), 30),
]

def _posed(place):
    """Preview of the working look: the stopwatch hand at a quarter turn - by the engine turn
    (engine_turn: the preview shows where the hand goes in the game). kmodel only knows a shift
    (move), so the turn is here, a wrapper over krender (as in M10); it does not go into the
    p3d - there model.cfg animates.
    """
    def wrapped(parts, *a, **kw):
        obs = place(parts, *a, **kw)
        if kw.get("move") is ON_MOVE:
            o, ax, ang = engine_turn(HAND_AXIS, HAND_PREVIEW * HAND_ANIM[1]["angle1"])
            for p, ob in zip(parts, obs):
                if p.group == SEL_HAND:
                    loc = Vector(ob.location)
                    cc = o + loc
                    ob.matrix_world = (Matrix.Translation(cc) @ Matrix.Rotation(ang, 4, ax) @ Matrix.Translation(-cc) @
                                       Matrix.Translation(loc))
        return obs
    return wrapped


krender.place_look = _posed(krender.place_look)
krender.place = _posed(krender.place)

if __name__ == "__main__":
    M.look_shots = (6, 3)
    M.run(build_lod, collision, SHOTS, row_step=1.9, row_shot=((1.9, -6.4, 2.2), (1.9, 0, 0.95)))
