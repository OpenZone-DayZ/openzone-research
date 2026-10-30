"""M23 - gunsmith's workbench: Ballistics Packer of Duty (OZL_Dty_Pack_Ball).
A packer: 10x10 cargo, three module slots (module_1..3) and module proxies in the same places. Each
module of the line has its own slot and its own place where it is worked with: slot 1 - a vise for
the barrel M81 on a plate in place of a built-in vise, slot 2 - the borescope M82 to the right of
the vise by the PSO-1 sight, slot 3 - the gauge set M83 behind the tray with the PBS-1.

    blender --background --python build_m23.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (tool silhouettes on the board,
stencil stripes on the crates). The layout is in layout.py (shared with make_decals.py).

Detail: the "dayz" look (matte, dirtier, colored AO). There is no built-in vise - in its place a plate
on four bolts for the module M81 (an empty slot is the plate and rubbed paint around it); slot 2 is
a rubber mat, slot 3 is a light clean spot on the sheet where a box usually stands (oil and dust
around). The tools are vanilla proxies (a hacksaw, three screwdrivers in a holder, pliers and an
adjustable wrench on the board; a hammer, a gun cleaning kit and rags on the table; rags and tape on
the shelf; kvanilla) and own detailed ones: open-end wrenches (a 15-degree jaw, heads thicker than
the shank), files (a pear-shaped handle, a ring, a tapering blade), punches in a block (knurled), a
cleaning rod with a ring; hooks and holders on the board.

The sight is the own PSO-1 (pso1.py, shared with M32 and M27): the shape from the specs and photos,
its own procedural material (black shagreen enamel rubbed down to metal on the edges, the rubber
eyecup, an aluminum scale with ticks, knurling), lenses - the glass section. It stands on the rags on
its bracket, the bracket toward the person (-y), the eyepiece toward +x. (DayZ sights as proxies are
drawn white in our model, and the closed DayZ model format cannot be taken apart, hence the own
model.) In the tray are DayZ gun parts (a folding stock and a handguard with AK rails, a PB
suppressor, an SKS clip), next to the sight a box of 7.62 x 39 cartridges, loose cartridges, a second
clip. DayZ compensators and bayonets are not drawn (their class is Proxy<name>). The oiler is a pump
type: a body with two grooves and a rolled bottom, a shoulder, a hex cap, a spout with a coupling
and a thin tip, dark green paint rubbed down to tin.

The table is kfurn.workbench (worktop="metal", as in M05) of the same size as M05/M11/M15: the
electronics assembler's table IZhSK.296375.001 ("Signal" catalog, version -03), top 1600 x 710 mm,
height 785-810 mm. Here it is 1.60 x 0.72 m, the work surface at 0.78, a 0.42 cabinet with four
drawers, the panel and shelf at 1.40, the shelf 0.30 deep. Duty variant: army order, black paint, a
red stripe on the cabinet (no olive); worn by frequent use - paint worn down to metal on the edge of
the top, around the vise plate, at the drawer handles, scratches and oil spots; no rust (its own
build_worn builder, because in kmats.build_paint chips always rust). No power strip.

Props and sizes:
- the vise plate: steel 180 x 160 x 8 mm on four M10 bolts (the M81 module has an 84 x 84 plate with
  124 mm lugs across, which sits on it);
- a 12 mm plywood board on the superstructure panel with white silhouettes of the own tools; the
  tools hang in their places (what hangs and how long - layout.py); the hammer is on the table;
- the PSO-1 optical sight (own, pso1.py: 375 x 69 x 170 mm with the eyecup, sources there) stands
  on the bracket base on the rags, the eyepiece toward +x, the bracket toward the person;
- the PBS-1 suppressor is disassembled in a tin tray: body, front cap, coupling, separators, rubber
  obturators; assembled length 152 mm, O ~40 - estimated from photos;
- a pump oiler (dia. 72 x 75, spout ~0.12);
- under the table two wooden ammo crates stacked, ~0.52 x 0.34 x 0.17 (no packaging datasheet was
  found - estimated from photos), end battens, rope handles, latches, stencil stripes without lettering;
- on the left shelf a soldered zinc can (~0.36 x 0.24 x 0.155 - an estimate).

Working look: ozl_lamp is the lamp and the white inside of the shade of the lamp over the vise;
"working" - the _on atlas (the lamp is lit, OZL_Work in the mod config). There are no moving parts;
the modules in the slots "work" together with the station (they have their own OZL_Work).

Blender axes: X is width, Y is depth (the face looks to -Y), Z is up.
"""
import math
import os
import sys

from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kfurn  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import kvanilla as kv  # noqa: E402
import kwood  # noqa: E402
import layout as L  # noqa: E402
import pso1  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
X0, X1, Y0, Y1 = L.X0, L.X1, L.Y0, L.Y1                      # table
ZT, ZP, SHD, CAB_W = L.ZT, L.ZP, L.SHD, L.CAB_W              # countertop, shelf top, shelf depth, cabinet
YP = L.YP                                                    # panel face
YS = Y1 - SHD                                                # front of the shelf
ZS = ZP - 0.02                                               # bottom of the shelf
# cabinet drawer handles (kfurn.workbench: fronts 1:1:1:1.4, the handle is 0.055 below the top of the front)
HANDLE_X, HANDLE_Y = (X1 - CAB_W + X1) / 2, Y0 + 0.02 - 0.018
HANDLE_Z = (0.691, 0.540, 0.390, 0.239)
# slot 1: the vise plate for M81, its top; slot 2: the borescope mat M82;
# slot 3: the place of the gauge set M83 behind the tray (a clean spot on the sheet)
VX, VY = -0.58, -0.20
MOUNT = (0.18, 0.16, 0.008)
MAT2 = (-0.31, -0.19, 0.25, 0.23, 0.003)                     # center, size, thickness
SLOT3 = (0.58, 0.12)
MODS = [(VX, VY, ZT + MOUNT[2]), (MAT2[0], MAT2[1], ZT + MAT2[4]), (SLOT3[0], SLOT3[1], ZT)]
MOD_OBJ = [("m81_barrel_vise", "ozr_barrel_vise"), ("m82_borescope", "ozr_borescope"), ("m83_gauge_set", "ozr_gauge_set")]
CLEAN3 = (SLOT3[0] - 0.105, SLOT3[0] + 0.105, SLOT3[1] - 0.092, SLOT3[1] + 0.092)
# lamp over the vise: mount under the shelf, shade
LAMP_X, LAMP_Y, SHADE_Z0, SHADE_Z1 = -0.45, -0.10, 1.215, 1.325
# rags with the sight (moved right, under slot 2), the tray with gun parts, the oiler
SH = 0.12
RAG = (-0.31 + SH, 0.13 + SH, -0.29, -0.05)
# PSO-1 (own, pso1.py): the middle of its extent; the bottom of the bracket base is on the rags (the cloth
# there is 1.5-5.5 mm higher than the sheet - the base is sunk slightly into it); the objective toward -x,
# the bracket toward the person
SCOPE_Y, SCOPE_Z = -0.16, ZT + 0.0035
POSE = pso1.Pose((SH, SCOPE_Y), 180.0, SCOPE_Z)
TRAY = (0.38, 0.78, -0.33, -0.07, 0.024)
OILER = (0.72, -0.02)
# on the left shelf: a zinc can
ZINC = (-0.78, -0.42, YS + 0.035, YS + 0.275, 0.155)

LOD_SPECS = [
    dict(lod=0, bev=1, sides=12),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "wb": ("paint_frame", 0.6), "wb_front": ("paint_front", 0.9), "wb_panel": ("paint_panel", 0.6),
    "wb_top": ("paint_top", 0.9), "steel": ("steel", 1.0), "black": ("black", 1.0), "rubber": ("rubber", 0.5),
    "board": ("board_paint", 1.3), "mount": ("mount", 1.4), "bolt": ("bolt", 2.0), "mat": ("mat", 0.8),
    "chrome": ("chrome", 1.6), "tool_dark": ("tool_dark", 1.6), "file_steel": ("file_steel", 2.0),
    "grip_red": ("grip_red", 1.6), "brass": ("brass", 1.6),
    "wood_z": ("wood_z", 1.6), "wood_x": ("wood_x", 1.6),
    "shade": ("shade", 1.2), "shade_in": ("shade_in", 1.2), "bulb": ("bulb", 2.0), "rag": ("rag", 1.2),
    "tray": ("tray", 1.4), "tin": ("tin", 1.6), "oiler_paint": ("oiler_paint", 2.0),
    "zinc": ("zinc", 1.0), "crate": ("crate", 0.9), "rope": ("rope", 1.2), "latch": ("latch", 1.6),
}
REGIONS.update(pso1.REGIONS)

# =============================================================================
# Materials
# =============================================================================


def build_worn(mat, origin, color, bare=kmats.lin((112, 112, 116)), seed=1.0, gloss=0.32, spec=0.25,
               wear=(0.66, 0.71), edge_k=0.7, rub=(), stripes=(), scratch=0.0, oil=0.0, floor_z=0.0,
               dust=0.15, grime=0.3, decal_items=(), clean=()):
    """Paint worn by frequent use, without rust: rubbed down to metal on the edges (edge_k) and where
    hands take it (rub - [(center, semi-axes, strength)]: an ellipsoid, weaker toward the edge);
    scratches along x, oil spots on top (oil); stripes of another color - stripes
    [((x0, x1, y0, y1, z0, z1), color)] in model coordinates; clean - [(x0, x1, y0, y1)]: where something
    usually stands (an empty module slot) - the paint is darker and cleaner, without oil and dust. Bare
    metal shines and does not rust."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.9 for c in color[:3]) + (1,), color)
    for (x0, x1, y0, y1, z0, z1), scol in stripes:
        inside = 1.0
        for i, (a, b) in enumerate(((x0, x1), (y0, y1), (z0, z1))):
            w = sep.outputs[i]
            m = t.math("MULTIPLY", t.math("GREATER_THAN", w, a), t.math("LESS_THAN", w, b))
            inside = m if isinstance(inside, float) else t.math("MULTIPLY", inside, m)
        base = t.mixc(inside, base, scol)
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
    worn = t.step(f, wear[0], wear[1])
    # bare metal: polished along x, blotchy tone; at the border of the worn area - dark primer as a thin rim
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
        col = t.mixc(t.math("MULTIPLY", ol, 0.55), col, kmats.lin((14, 12, 10)))
        g_ = t.math("ADD", g_, t.math("MULTIPLY", ol, 0.25))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    if not isinstance(spot, float):
        col = t.mixc(t.math("MULTIPLY", spot, 0.75), col, tuple(c * 0.92 for c in color[:3]) + (1,))
        dirt = t.math("MULTIPLY", dirt, t.math("SUBTRACT", 1.0, spot))
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g_, s_, h)


def wall_decal(name, x0, x1, z0, z1, y):
    """Decal facing -y, only on the face at depth y."""
    return (os.path.join(WORK, name), "y", -1, ("x", "z"), ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0),
            (y - 0.002, y + 0.002))


BLACK = kmats.lin((30, 30, 32))
RED = kmats.lin((140, 24, 20))
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
FRAME = dict(color=BLACK, seed=2.1, wear=(0.67, 0.72), edge_k=0.7, scratch=0.3, floor_z=0.0, dust=0.15, grime=0.3)
TOP_RUB = [((0.0, Y0 - 0.01, ZT), (0.95, 0.07, 0.05), 0.30),       # front edge - by hands and parts
           ((VX, VY, ZT), (0.20, 0.17, 0.06), 0.55),               # around the vise plate
           ((0.04, -0.16, ZT), (0.36, 0.16, 0.03), 0.18)]          # the work area
FRONT_RUB = [((HANDLE_X, HANDLE_Y, z), (0.11, 0.06, 0.05), 0.42) for z in HANDLE_Z]
STRIPE = ((X1 - CAB_W + 0.02, X1 - CAB_W + 0.07, Y0 - 0.04, Y0 + 0.06, 0.07, 0.77), RED)
STENCIL = [wall_decal("decal_stencil.png", x0, x1, z0, z0 + h, y0) for x0, x1, y0, y1, z0, h in L.CRATES]

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "paint_frame": (build_worn, FRAME),
    "paint_front": (build_worn, dict(FRAME, seed=2.9, edge_k=0.8, rub=FRONT_RUB, stripes=[STRIPE])),
    "paint_panel": (build_worn, dict(FRAME, seed=3.7, wear=(0.71, 0.76), edge_k=0.55, scratch=0.15, floor_z=ZT,
                                     dust=0.25, grime=0.15)),
    "paint_top": (build_worn, dict(FRAME, seed=4.4, wear=(0.65, 0.70), edge_k=0.9, rub=TOP_RUB, scratch=0.9, oil=0.7,
                                   floor_z=ZT, dust=0.08, grime=0.15, clean=[CLEAN3])),
    # plywood board painted black: worn to plywood on the edges, white silhouettes on it
    "board_paint": (build_worn, dict(color=kmats.lin((38, 38, 38)), bare=kmats.lin((168, 136, 96)), seed=5.1,
                                     wear=(0.73, 0.78), edge_k=0.6, floor_z=ZT, dust=0.2, grime=0.1,
                                     decal_items=[wall_decal("decal_board.png", *L.BOARD, L.Y_BOARD)])),
    # vise plate: blued steel, worn at the edges and bolts, oil
    "mount": (build_worn, dict(color=kmats.lin((44, 46, 48)), bare=kmats.lin((120, 120, 124)), seed=6.3,
                               wear=(0.58, 0.64), edge_k=1.0, scratch=0.9, oil=0.6, floor_z=ZT, dust=0.05, grime=0.4)),
    "bolt": ("steel", dict(seed=6.6, tone=0.24, along="z", gloss=0.45, spec=0.55, floor_z=ZT, dust=0.05, grime=0.5)),
    "mat": ("plastic", dict(color=kmats.lin((28, 30, 28)), gloss=0.12, spec=0.06, mottle=0.12, dust=0.3, grime=0.5,
                            scuff=(0.66, 0.74))),
    "chrome": ("steel", dict(seed=7.1, tone=0.30, along="z", gloss=0.75, spec=0.85, floor_z=ZT, dust=0.1, grime=0.2)),
    "tool_dark": ("steel", dict(seed=7.5, tone=0.17, along="z", gloss=0.4, spec=0.5, floor_z=ZT, dust=0.05,
                                grime=0.3)),
    # file blade: dark steel, the cut is a fine ripple (no shine)
    "file_steel": ("steel", dict(seed=7.8, tone=0.20, along="x", gloss=0.25, spec=0.35, floor_z=ZT, dust=0.1,
                                 grime=0.5)),
    "grip_red": ("plastic", dict(color=kmats.lin((150, 30, 24)), gloss=0.5, spec=0.35, dust=0.1, grime=0.3,
                                 scuff=(0.6, 0.68))),
    "wood_z": (kwood.build_wood, dict(color=kmats.lin((150, 102, 62)), seed=7.9, along="z", floor_z=ZT, dust=0.1,
                                      grime=0.5, knots=0.2)),
    "wood_x": (kwood.build_wood, dict(color=kmats.lin((150, 102, 62)), seed=8.3, along="x", floor_z=ZT, dust=0.1,
                                      grime=0.5, knots=0.2)),
    "shade": (build_worn, dict(color=BLACK, seed=8.7, wear=(0.70, 0.75), edge_k=0.8, floor_z=ZT, dust=0.35,
                               grime=0.1)),
    "shade_in": ("plastic", dict(color=kmats.lin((214, 212, 200)), gloss=0.6, spec=0.45, dust=0.2, grime=0.2)),
    "shade_in_on": ("flat", dict(color=kmats.lin((255, 244, 214)), gloss=0.6, spec=0.45)),
    "bulb": ("flat", dict(color=kmats.lin((210, 206, 194)), gloss=0.7, spec=0.6)),
    "bulb_on": ("flat", dict(color=kmats.lin((255, 248, 222)), gloss=0.7, spec=0.6)),
    # rags: gray-white cotton, oily
    "rag": ("plastic", dict(color=kmats.lin((156, 148, 132)), gloss=0.06, spec=0.04, mottle=0.25, dust=0.05,
                            grime=0.55, scuff=(0.9, 1.0))),
    # oiler: dark green enamel over tin, worn to metal on the grooves, shoulder and cap, oil outside
    "oiler_paint": (build_worn, dict(color=kmats.lin((52, 62, 46)), bare=kmats.lin((150, 148, 140)), seed=9.3,
                                     wear=(0.62, 0.68), edge_k=1.0, scratch=0.5, oil=0.6, floor_z=ZT, dust=0.1,
                                     grime=0.5)),
    "tray": ("steel", dict(seed=9.9, tone=0.26, along="x", floor_z=ZT, dust=0.05, grime=0.45)),
    "tin": ("steel", dict(seed=10.3, tone=0.32, along="z", floor_z=ZT, dust=0.1, grime=0.5)),
    "brass": ("paint", dict(CLEAN, color=kmats.lin((156, 128, 70)), gloss=0.55, spec=0.55, dust=0.1, grime=0.3)),
    "zinc": ("steel", dict(seed=10.7, tone=0.30, along="x", gloss=0.45, spec=0.55, floor_z=ZP, dust=0.3, grime=0.2)),
    # crates: pine, unpainted, darkened; stencil stripes on the face
    "crate": (kwood.build_wood, dict(color=kmats.lin((146, 116, 82)), seed=11.1, along="x", floor_z=0.0, dust=0.3,
                                     grime=0.35, knots=0.6, decal_items=STENCIL)),
    "rope": ("plastic", dict(color=kmats.lin((150, 128, 88)), gloss=0.08, spec=0.05, mottle=0.25, dust=0.2,
                             grime=0.4)),
    "latch": (build_worn, dict(color=BLACK, seed=11.5, wear=(0.68, 0.73), edge_k=0.8, floor_z=0.0, dust=0.1,
                               grime=0.3)),
})
KINDS.update(pso1.kinds(POSE, floor_z=ZT))

OBJ, NAME = "m23_dty_pack_ball", "ozr_dty_pack_ball"
# Working look: the lamp and the inside of the shade are ozl_lamp (in hiddenSelections); "off" by
# default, "working" - the _on_co atlas and the _on rvmat with glow.
SEL_LAMP = "ozl_lamp"
ON = dict(remap={"shade_in": "shade_in_on", "bulb": "bulb_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
# module proxies: the slots OZL_Tool1..3 are linked to them by CfgNonAIVehicles of the mod (Proxyozl_tool1..3);
# slot N is module N of the "Ballistics" line (M81, M82, M83), without rotation: the modules face the person
PROXIES = [(r"\OpenZone_Research\models\proxies\ozl_tool%d" % (i + 1), m) for i, m in enumerate(MODS)]


# vanilla items: on the board per layout.VANILLA_BOARD, on the table and shelf here
DECOR = [kv.put(k, (x, L.Y_BOARD - 0.0005, z), **kv.hung(deg)) for k, x, z, deg in L.VANILLA_BOARD] + [
    kv.put("hammer", (-0.30, 0.075, ZT), **kv.flat(8)),
    kv.put("cleaningkit", (0.02, 0.17, ZT), **kv.flat(0)),
    kv.put("rags", (0.31, 0.14, ZT), **kv.flat(95)),
    kv.put("rags", (-0.22, YS + 0.15, ZP), **kv.flat(10)),
    kv.put("ducttape", (0.10, YS + 0.17, ZP), **kv.flat(0)),
    # by the sight: behind the rags a box of 7.62 x 39 cartridges, on the rags in front of the sight an SKS
    # clip and loose cartridges
    kv.put("ammobox762", (0.04, 0.0, ZT), **kv.flat(12)),
    kv.put("sksclip", (-0.08, -0.245, ZT + 0.003), **kv.flat(-12)),
    kv.put("rounds762", (0.10, -0.25, ZT + 0.003), up=(0, 0, 1), fwd=(0, -1, 0)),
    # in the tray on the right front corner - DayZ gun parts (lying flat)
    kv.put("akstock", (TRAY[0] + 0.150, -0.245, ZT + 0.0015), **kv.flat(3)),
    kv.put("akrail", (TRAY[1] - 0.055, -0.235, ZT + 0.0015), **kv.flat(90)),
    kv.put("pbsupp", (TRAY[0] + 0.09, -0.125, ZT + 0.0015), **kv.flat(0)),
    kv.put("sksclip", (TRAY[0] + 0.25, -0.12, ZT + 0.0015), **kv.flat(0)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 selections=(SEL_LAMP,), hidden=(SEL_LAMP,), states={"on": ON}, proxies=PROXIES, decor=DECOR,
                 modules=[(o, n, m) for (o, n), m in zip(MOD_OBJ, MODS)], glass=pso1.GLASS)
P = M.part
BOUNDS = {}


# =============================================================================
# Primitives that kgeo does not have
# =============================================================================
def rod(part, a, b, r, sides):
    """Cylinder between points a and b."""
    return g.pipe(part, [tuple(a), tuple(b)], r, sides)


def face(part, verts, want):
    """Face from bmesh vertices, oriented toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def lathe(part, prof, sides, inward=False, center=(0.0, 0.0, 0.0), axis="z", cap=False):
    """Solid of revolution (as in M15): prof [(r, h)] from bottom to top along the axis, ends open;
    inward - the surface looks toward the axis (the inside of the shade); cap - close the top. axis is
    "z" or "x"."""
    bm = part.bm
    c0 = Vector(center)

    def pt(r, h, k):
        a = 2 * math.pi * k / sides
        if axis == "z":
            return c0 + Vector((r * math.cos(a), r * math.sin(a), h))
        return c0 + Vector((h, r * math.cos(a), r * math.sin(a)))
    rings = [[bm.verts.new(pt(r, h, k)) for k in range(sides)] for r, h in prof]
    new = []
    for i in range(len(rings) - 1):
        for k in range(sides):
            j = (k + 1) % sides
            q = [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]
            c = sum((v.co for v in q), Vector()) / 4 - c0
            out = Vector((c.x, c.y, 0)) if axis == "z" else Vector((0, c.y, c.z))
            new.append(face(part, q, -out if inward else out))
    if cap:
        new.append(face(part, rings[-1], Vector((0, 0, 1)) if axis == "z" else Vector((1, 0, 0))))
    bm.normal_update()
    part.tag(new)


def open_box(part, x0, x1, y0, y1, z0, z1, t):
    """Box without a lid: a bottom and four walls of thickness t."""
    g.box(part, x0, x1, y0, y1, z0, z0 + t)
    g.box(part, x0, x1, y0, y0 + t, z0 + t, z1)
    g.box(part, x0, x1, y1 - t, y1, z0 + t, z1)
    g.box(part, x0, x0 + t, y0 + t, y1 - t, z0 + t, z1)
    g.box(part, x1 - t, x1, y0 + t, y1 - t, z0 + t, z1)


def ring_poly(cx, cz, ro, ws, ang, n=14, depth=0.2):
    """Head of an open-end wrench in the board plane: a circle ro with a jaw slot of width 2 ws, open
    toward ang (degrees from +x), the bottom of the slot is behind the center at depth * ro."""
    a = math.radians(ang)
    d, p = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
    tm = math.asin(min(0.95, ws / ro))
    pts = [(cx + ro * math.cos(a + tm + (2 * math.pi - 2 * tm) * k / n), cz + ro * math.sin(a + tm + (2 * math.pi - 2 * tm) * k / n))
           for k in range(n + 1)]
    b = -depth * ro
    pts += [(cx + d[0] * b - p[0] * ws, cz + d[1] * b - p[1] * ws), (cx + d[0] * b + p[0] * ws, cz + d[1] * b + p[1] * ws)]
    return pts


def knurl_z(part, cx, cy, z0, z1, r, n, depth):
    """Knurled rod along z: 2n vertices around, every other one sunk."""
    poly = [(cx + (r - depth * (k % 2)) * math.cos(math.pi * k / n), cy + (r - depth * (k % 2)) * math.sin(math.pi * k / n))
            for k in range(2 * n)]
    return g.prism(part, poly, (0, 1), z0, z1)


def peg(part, x, z, length=0.02, r=0.0025, lod=0):
    """Board hook: a steel peg from the plywood toward the person (near LOD only)."""
    if lod == 0:
        g.cyl(part, (x, L.Y_BOARD - length / 2, z), "y", r, length, 6)


# =============================================================================
# Table (metal top); module places: the vise plate, the mat
# =============================================================================
def build_bench(spec):
    return kfurn.workbench(M, spec, X0, X1, Y0, Y1, ZT, ZP, SHD, cab_w=CAB_W, worktop="metal", outlets=0, lamp=False)


def build_slots(spec):
    """Slot 1 - a vise plate on four bolts (the M81 vise sits on it); slot 2 - a rubber mat for the
    borescope case M82; slot 3 - only a clean spot on the sheet (build_worn, clean)."""
    lod = spec["lod"]
    w, d, t = MOUNT
    mt = P("mount_plate", "mount")
    g.box(mt, VX - w / 2, VX + w / 2, VY - d / 2, VY + d / 2, ZT, ZT + t, **(dict(r=0.002, seg=1) if lod == 0 else {}))
    parts = [mt]
    if lod < 2:
        bt = P("mount_bolts", "bolt")
        for sx in (-1, 1):
            for sy in (-1, 1):
                x, y = VX + sx * (w / 2 - 0.016), VY + sy * (d / 2 - 0.016)
                g.cyl(bt, (x, y, ZT + t + 0.003), "z", 0.0095, 0.006, 6)
                if lod == 0:
                    g.cyl(bt, (x, y, ZT + t + 0.0064), "z", 0.0055, 0.0012, 12)          # stud end
        parts.append(bt)
    cx, cy, mw, md, mtk = MAT2
    mat = P("slot2_mat", "mat")
    g.box(mat, cx - mw / 2, cx + mw / 2, cy - md / 2, cy + md / 2, ZT, ZT + mtk, **(dict(r=0.0012, seg=1) if lod == 0 else {}))
    parts.append(mat)
    return parts


# =============================================================================
# Lamp over the vise: a bracket under the shelf, a shade, a bulb (ozl_lamp)
# =============================================================================
def build_lamp(spec):
    lod, sd = spec["lod"], spec["sides"]
    n = sd + 4 if lod == 0 else sd
    parts = []
    br = P("lamp_arm", "shade")
    if lod < 2:
        g.box(br, LAMP_X - 0.04, LAMP_X + 0.04, YS + 0.03, YS + 0.11, ZS - 0.006, ZS)       # plate under the shelf
    zt = SHADE_Z1 + 0.035
    rod(br, (LAMP_X, YS + 0.07, ZS - 0.006), (LAMP_X, YS + 0.07, zt + 0.01), 0.008, 6 if lod == 0 else 4)
    rod(br, (LAMP_X, YS + 0.07, zt + 0.01), (LAMP_X, LAMP_Y, zt + 0.01), 0.008, 6 if lod == 0 else 4)
    g.cyl(br, (LAMP_X, LAMP_Y, SHADE_Z1 + 0.02), "z", 0.022, 0.04, n)                     # socket
    parts.append(br)
    sh = P("lamp_shade", "shade")
    prof = [(0.100, 0.0), (0.090, 0.02), (0.060, 0.07), (0.030, SHADE_Z1 - SHADE_Z0)]
    lathe(sh, prof if lod == 0 else prof[::3], n, center=(LAMP_X, LAMP_Y, SHADE_Z0))
    parts.append(sh)
    if lod == 2:
        return parts
    si = P("lamp_shade_in", "shade_in", group=SEL_LAMP)
    lathe(si, [(r - 0.0015, z) for r, z in (prof if lod == 0 else prof[::3])], n, inward=True,
          center=(LAMP_X, LAMP_Y, SHADE_Z0))
    parts.append(si)
    if lod == 0:
        rim = P("lamp_rim", "steel")
        g.pipe(rim, [(LAMP_X + 0.1 * math.cos(2 * math.pi * k / n), LAMP_Y + 0.1 * math.sin(2 * math.pi * k / n),
                      SHADE_Z0) for k in range(n + 1)], 0.0025, 4)
        parts.append(rim)
    bl = P("lamp_bulb", "bulb", group=SEL_LAMP)
    bp = [(0.004, -0.032), (0.022, -0.026), (0.030, -0.010), (0.029, 0.006), (0.017, 0.024), (0.014, 0.036)]
    lathe(bl, bp if lod == 0 else bp[::2], 10 if lod == 0 else 6, center=(LAMP_X, LAMP_Y, SHADE_Z1 - 0.06))
    parts.append(bl)
    return parts


# =============================================================================
# Board: own tools by silhouettes, hooks, a screwdriver holder (the vanilla ones are proxies, DECOR)
# =============================================================================
def spanner(chrome, x, z, Lg, W, lod):
    """Open-end wrench: two heads with a 15-degree jaw (the upper one smaller), a shank thinner than the heads."""
    yb = L.Y_TOOL
    th, ts = 0.0055, 0.0042
    n = 14 if lod == 0 else 8
    for cz, ro, ws, ang in ((z - W * 0.4, W * 0.62, W * 0.36, 90 + 15), (z - Lg + W * 0.55, W * 0.72, W * 0.42, -90 - 15)):
        g.prism(chrome, ring_poly(x, cz, ro, ws, ang, n), (0, 2), yb - th, yb)
    poly = [(x - 0.26 * W, z - W * 0.4 - W * 0.5), (x + 0.26 * W, z - W * 0.4 - W * 0.5),
            (x + 0.33 * W, z - Lg + W * 0.55 + W * 0.6), (x - 0.33 * W, z - Lg + W * 0.55 + W * 0.6)]
    g.prism(chrome, poly, (0, 2), yb - ts - 0.0006, yb - 0.0006)


def file_tool(wood, steel, dark, x, z, Lg, W, lod):
    """File: a pear-shaped handle with a ring, the blade tapers toward the tip; hangs on two hooks under the handle."""
    yb = L.Y_TOOL
    ya = yb - 0.0135                                          # handle axis
    n = 10 if lod == 0 else 6
    prof = [(0.0085, -0.100), (0.0112, -0.094), (0.0130, -0.064), (0.0126, -0.026), (0.0098, -0.006), (0.0050, 0.0)]
    lathe(wood, prof if lod == 0 else prof[::2] + [prof[-1]], n, center=(x, ya, z), cap=True)
    g.cyl(steel, (x, ya, z - 0.097), "z", 0.0094, 0.010, n)                              # ring
    poly = [(x - W / 2, z - 0.104), (x + W / 2, z - 0.104), (x + W * 0.3, z - Lg), (x - W * 0.3, z - Lg)]
    g.prism(dark, poly, (0, 2), ya - 0.0022, ya + 0.0022)


def build_board(spec):
    lod = spec["lod"]
    x0, x1, z0, z1 = L.BOARD
    bd = P("board", "board")
    g.box(bd, x0, x1, L.Y_BOARD, YP, z0, z1)
    parts = [bd]
    if lod == 2:
        return parts
    chrome, dark, fl = P("tools_chrome", "chrome"), P("tools_dark", "tool_dark"), P("tools_file", "file_steel")
    wood, wx = P("tools_wood", "wood_z"), P("punch_block", "wood_x")
    pg = P("board_pegs", "steel")
    for kind, x, z, p in L.TOOLS:
        if kind == "spanner":
            spanner(chrome, x, z, p["L"], p["W"], lod)
            peg(pg, x, z - p["W"] * 0.4 - 0.004, 0.012, 0.003, lod=lod)
        elif kind == "file":
            file_tool(wood, chrome, fl, x, z, p["L"], p["W"], lod)
            for s in (-1, 1):
                peg(pg, x + s * 0.0165, z - 0.075, 0.024, lod=lod)
        elif kind == "punches":
            n, step = p["n"], p["step"]
            xa = x - step * (n - 1) / 2
            g.box(wx, xa - 0.025, xa + step * (n - 1) + 0.025, L.Y_TOOL - 0.03, L.Y_TOOL, z - 0.012, z + 0.012,
                  **(dict(r=0.002, seg=1) if lod == 0 else {}))
            for k in range(n):
                xk, rk, lk = xa + step * k, L.PUNCH_R[k], L.PUNCH_LEN[k]
                yk = L.Y_TOOL - 0.015
                zt = z + 0.06
                if lod == 0:
                    knurl_z(dark, xk, yk, zt - 0.055, zt, rk + 0.0025, 8, 0.0006)            # knurled handle
                    lathe(dark, [(rk + 0.0025, -0.012), (rk, -0.006)], 8, center=(xk, yk, zt - 0.055 + 0.012))
                    g.cyl(dark, (xk, yk, zt - 0.061 - (lk - 0.061) / 2), "z", rk, lk - 0.061, 8)
                else:
                    g.cyl(dark, (xk, yk, zt - lk / 2), "z", rk + 0.002, lk, 4)
        elif kind == "rod":
            Lr = p["L"]
            rod(chrome, (x - Lr / 2, L.Y_TOOL - 0.008, z), (x + Lr / 2 - 0.015, L.Y_TOOL - 0.008, z), 0.003,
                6 if lod == 0 else 4)
            g.cyl(chrome, (x - Lr / 2 - 0.006, L.Y_TOOL - 0.008, z), "x", 0.0042, 0.012, 8)   # tip
            cx = x + Lr / 2 - 0.006
            ring = [(cx + 0.009 * math.cos(2 * math.pi * k / 12), L.Y_TOOL - 0.008, z + 0.009 * math.sin(2 * math.pi * k / 12))
                    for k in range(13)]
            if lod == 0:
                g.pipe(chrome, ring, 0.0022, 6)
            for s in (-1, 1):
                peg(pg, x + s * 0.10, z - 0.006, 0.016, lod=lod)
    # hooks and a holder for the vanilla tools
    for key, x, z, deg in L.VANILLA_BOARD:
        lo, hi = kv.box(key)
        half = (hi[1] - lo[1]) / 2
        if key == "hacksaw":
            for s in (-1, 1):
                peg(pg, x + s * 0.12, z + (hi[1] - lo[1]) / 2 - 0.016, 0.022, lod=lod)
        elif key == "wrench":
            peg(pg, x, z + half - 0.012, 0.022, lod=lod)
        elif key == "pliers":
            peg(pg, x, z + 0.02, 0.03, lod=lod)
    hd = P("sd_holder", "steel")
    xs = [x for k, x, z, d in L.VANILLA_BOARD if k == "screwdriver"]
    zh = L.SD_HOLDER_Z
    edges = [min(xs) - 0.035] + [v for x in xs for v in (x - 0.005, x + 0.005)] + [max(xs) + 0.035]
    for a, b in zip(edges[::2], edges[1::2]):
        g.box(hd, a, b, L.Y_BOARD - 0.034, L.Y_BOARD, zh - 0.003, zh)
    g.box(hd, min(xs) - 0.035, max(xs) + 0.035, L.Y_BOARD - 0.034, L.Y_BOARD - 0.031, zh - 0.010, zh - 0.003)
    for xe in (min(xs) - 0.033, max(xs) + 0.031):
        g.box(hd, xe, xe + 0.002, L.Y_BOARD - 0.034, L.Y_BOARD, zh - 0.025, zh)
    parts += [chrome, dark, fl, wood, wx, pg, hd]
    if lod == 0:
        sc = P("board_screws", "steel")
        for bx in (x0 + 0.02, (x0 + x1) / 2 + 0.03, x1 - 0.02):
            for bz in (z0 + 0.02, z1 - 0.02):
                g.cyl(sc, (bx, L.Y_BOARD - 0.001, bz), "y", 0.005, 0.002, 6)
        parts.append(sc)
    return parts


# =============================================================================
# Table: rags with the PSO-1 (pso1.py), a tray with gun parts, an oiler
# =============================================================================
def build_rag(spec):
    """Spread rags under the sight (the PSO-1 stands on it by its bracket base - build_scope)."""
    lod = spec["lod"]
    x0, x1, y0, y1 = RAG
    rg = P("rag", "rag")
    if lod == 2:
        g.box(rg, x0, x1, y0, y1, ZT, ZT + 0.003)
        return [rg]
    # the cloth lies unevenly: a grid with bumps, curled edges
    nx, ny = (12, 8) if lod == 0 else (3, 2)
    bm = rg.bm
    vs = [[bm.verts.new((x0 + (x1 - x0) * i / nx + 0.006 * math.sin(i * 2.3 + j),
                         y0 + (y1 - y0) * j / ny + 0.005 * math.cos(i * 1.7 + j * 2.1),
                         ZT + 0.0015 + (0.004 * abs(math.sin(i * 1.9 + j * 2.7)) if 0 < i < nx and 0 < j < ny else 0)))
           for j in range(ny + 1)] for i in range(nx + 1)]
    new = []
    for i in range(nx):
        for j in range(ny):
            new.append(face(rg, [vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]], (0, 0, 1)))
    rg.tag(new)
    return [rg]


def build_scope(spec):
    """The PSO-1 on the rags (pso1.py; the lens glasses are the model's glass section)."""
    return pso1.build(P, spec["lod"], POSE)


def build_tray(spec):
    """Tin tray on the right front corner; the DayZ gun parts in it are proxies (DECOR)."""
    lod = spec["lod"]
    x0, x1, y0, y1, h = TRAY
    tr = P("tray", "tray")
    if lod == 2:
        return []
    if lod == 0:
        open_box(tr, x0, x1, y0, y1, ZT, ZT + h, 0.0015)
        # rolled rim around the perimeter
        g.pipe(tr, [(x0, y0, ZT + h), (x1, y0, ZT + h), (x1, y1, ZT + h), (x0, y1, ZT + h), (x0, y0, ZT + h)], 0.0022, 6)
    else:
        g.box(tr, x0, x1, y0, y1, ZT, ZT + h)
    return [tr]


def build_oiler(spec):
    """Pump oiler 0.25 l: rolled bottom, a body with two grooves, a shoulder, a neck, a hex cap, a spout
    with a coupling at the cap, a bend and a thin tip."""
    lod = spec["lod"]
    if lod == 2:
        return []
    ox, oy = OILER
    n = 20 if lod == 0 else 8
    ol = P("oiler", "oiler_paint")
    prof = [(0.0335, 0.000), (0.0365, 0.002), (0.0370, 0.005), (0.0360, 0.007), (0.0360, 0.014), (0.0368, 0.016),
            (0.0360, 0.018), (0.0360, 0.040), (0.0368, 0.042), (0.0360, 0.044), (0.0360, 0.052), (0.0340, 0.060),
            (0.0280, 0.067), (0.0190, 0.072), (0.0125, 0.074), (0.0125, 0.079)]
    lathe(ol, prof if lod == 0 else [prof[i] for i in (0, 4, 10, 12, 13, 15)], n, center=(ox, oy, ZT))
    g.cyl(ol, (ox, oy, ZT + 0.0015), "z", 0.0335, 0.003, n)
    parts = [ol]
    cap = P("oiler_cap", "tin")
    g.cyl(cap, (ox, oy, ZT + 0.0855), "z", 0.0145, 0.013, 6)                                 # cap nut
    if lod == 0:
        g.cyl(cap, (ox, oy, ZT + 0.0935), "z", 0.0095, 0.003, 12)
    parts.append(cap)
    sp = P("oiler_spout", "steel")
    pts = [(ox, oy, ZT + 0.094), (ox - 0.006, oy, ZT + 0.115), (ox - 0.030, oy + 0.003, ZT + 0.142),
           (ox - 0.075, oy + 0.008, ZT + 0.158), (ox - 0.120, oy + 0.012, ZT + 0.160)]
    if lod == 0:
        g.cyl(sp, (ox, oy, ZT + 0.100), "z", 0.0062, 0.014, 10)                              # spout coupling
        g.pipe(sp, pts[:4], 0.0034, 8)
        g.pipe(sp, pts[3:], 0.0020, 6)                                                       # thin tip
    else:
        g.pipe(sp, pts[::2], 0.003, 4)
    parts.append(sp)
    return parts


# =============================================================================
# Shelf: zinc can
# =============================================================================
def build_shelf(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    x0, x1, y0, y1, h = ZINC
    zn = P("zinc", "zinc")
    g.box(zn, x0, x1, y0, y1, ZP, ZP + h - 0.006)
    g.box(zn, x0 - 0.002, x1 + 0.002, y0 - 0.002, y1 + 0.002, ZP + h - 0.006, ZP + h)        # lid flange
    if lod == 0:
        # bar handle of the tear-off strip on the lid
        g.pipe(zn, [(x0 + 0.03, (y0 + y1) / 2 - 0.02, ZP + h), (x0 + 0.03, (y0 + y1) / 2 - 0.02, ZP + h + 0.012),
                    (x0 + 0.03, (y0 + y1) / 2 + 0.02, ZP + h + 0.012), (x0 + 0.03, (y0 + y1) / 2 + 0.02, ZP + h)],
               0.002, 4)
    return [zn]


# =============================================================================
# Under the table: ammo crates
# =============================================================================
def build_crates(spec):
    lod = spec["lod"]
    parts = []
    cr = P("crates", "crate")
    rp = P("crate_ropes", "rope") if lod == 0 else None
    lt = P("crate_latches", "latch") if lod == 0 else None
    for x0, x1, y0, y1, z0, h in L.CRATES:
        g.box(cr, x0, x1, y0, y1, z0, z0 + h - L.CRATE_LID)
        g.box(cr, x0 - 0.004, x1 + 0.004, y0 - 0.004, y1 + 0.004, z0 + h - L.CRATE_LID, z0 + h)
        if lod > 0:
            continue
        for xa, xb in ((x0 - 0.02, x0), (x1, x1 + 0.02)):                                       # end battens
            g.box(cr, xa, xb, y0 + 0.02, y0 + 0.075, z0 + 0.01, z0 + h - L.CRATE_LID - 0.004)
            g.box(cr, xa, xb, y1 - 0.075, y1 - 0.02, z0 + 0.01, z0 + h - L.CRATE_LID - 0.004)
        if rp is not None:
            for xe, s in ((x0 - 0.02, -1), (x1 + 0.02, 1)):
                yc, zc = (y0 + y1) / 2, z0 + h * 0.62
                g.pipe(rp, [(xe - 0.002 * s, yc - 0.06, zc), (xe + 0.012 * s, yc - 0.05, zc - 0.035),
                            (xe + 0.014 * s, yc, zc - 0.045), (xe + 0.012 * s, yc + 0.05, zc - 0.035),
                            (xe - 0.002 * s, yc + 0.06, zc)], 0.005, 6)
        if lt is not None:
            for xc in (x0 + 0.11, x1 - 0.11):
                g.box(lt, xc - 0.016, xc + 0.016, y0 - 0.010, y0 - 0.004, z0 + h - 0.05, z0 + h - 0.004)
                g.box(lt, xc - 0.010, xc + 0.010, y0 - 0.012, y0, z0 + h - 0.075, z0 + h - 0.05)
    parts.append(cr)
    if rp is not None:
        parts += [rp, lt]
    return parts


def build_lod(spec):
    parts = build_bench(spec) + build_slots(spec) + build_lamp(spec) + build_board(spec)
    parts += build_rag(spec) + build_scope(spec) + build_tray(spec) + build_oiler(spec)
    parts += build_shelf(spec) + build_crates(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    metal = kx.PEN + r"\metalplate.rvmat"
    table = kx.box_pts(X0 - 0.01, X1 + 0.01, Y0 - 0.01, Y1 + 0.005, 0.0, ZT)
    # a geometry component thinner than 0.5 m does not work in the engine: the superstructure goes down,
    # inside the table, and forward over the countertop - the parts overlap, each is convex
    top = kx.box_pts(X0 - 0.03, X1, Y1 - 0.51, Y1, 0.40, ZP + 0.17)
    comps = [(table, metal), (top, metal)]
    memory = {
        "invView": [(-0.2, -2.6, 1.3)],
        "ce_center": [(0.0, 0.0, ZP / 2)],
        "ce_radius": [(1.1, 0.0, ZP / 2)],
    }
    for i, m in enumerate(MODS):
        memory["module_%d" % (i + 1)] = [m]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2] + 0.004)
    return comps, 160.0, memory, bbox


# the first ones are for the --look preview: overall, the table with the modules in place (and the same
# empty), the sight, the tray with parts, the oiler, the board
SHOTS = [
    ("front", (-1.0, -2.4, 1.75), (0.0, 0.0, 1.0), 32),
    ("bench", (-0.10, -1.15, 1.60), (-0.10, -0.08, 0.84), 32),
    ("scope", (0.30, -0.66, 1.06), (SH + 0.01, -0.16, 0.86), 38),
    ("tray", (0.80, -0.78, ZT + 0.42), (0.58, -0.17, ZT + 0.03), 36),
    ("oiler", (0.93, -0.40, ZT + 0.22), (0.68, -0.02, ZT + 0.08), 50),
    ("board", (0.0, -1.1, 1.20), (0.0, 0.30, 1.03), 32),
    ("slots", (-0.55, -0.85, 1.20), (-0.40, -0.15, 0.86), 36),
    ("right", (0.95, -1.0, 1.45), (0.45, -0.05, 0.85), 34),
    ("under", (-0.6, -1.5, 0.75), (-0.35, 0.0, 0.20), 32),
    ("back", (1.4, 1.9, 1.6), (0.0, 0.0, 0.9), 32),
]

M.look_shots = (6, 2)
M.run(build_lod, collision, SHOTS, row_step=1.9, row_shot=((1.9, -6.2, 2.0), (1.9, 0, 0.80)))
