"""M27 - Freedom's gunsmith's table: Ballistics Packer of Freedom (OZL_Frd_Pack_Ball).
A packer: 10x10 cargo, three module slots (module_1..3) and module proxies in the same places. Each
module of the line has its own slot and its own place where it is worked with: slot 1 - the barrel
vise M81 at the front left corner (on a steel plate clamped to the table with two clamps - an empty
slot shows the plate and the clamps), slot 2 - the borescope M82 on the mat by the cleaning rod (empty:
a clean spot on the mat), slot 3 - the gauge set M83 on the right by the magazines (empty: a clean
spot on the sheet).

    blender --background --python build_m27.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (decals on the cabinet, panel and
cases - including the peace sign, LEGALIZE and the Freedom leaf; the mat grid). The layout is in
layout.py (shared with make_decals.py); the own geometry is in m27_geo.py.

Detail: the "dayz" look (matte, dirtier, colored AO); chamfers on the table edges, more segments on
the solids of revolution, cables as smooth curves. The small stuff is vanilla DayZ items as proxies
(kvanilla): two screwdrivers and pliers on a magnetic strip, a gun cleaning kit, rags, STANAG
magazines taped together, loose cartridges and a pack of 5.56, on the shelf tape, a radio and a
cassette.
Sights: the DayZ sight proxies (PSO-6, PO 4x34) cannot be used - vanilla optics as proxies are drawn
white in our model, and an own shape with a DayZ texture comes out in stripes (the unwrap of an own
shape does not match the vanilla picture). So both sights are own, with their own material: in place
of the 6x42 under the lamp, the PSO-1 on its bracket base (pso1.py, shared with M23 and M32), and in
place of the ACOG a compact prism sight of the ACOG TA31 class on a base with two thumb screws
(acog.py; Western optics for the STANAG magazines and 5.56 cartridges on this table). The cans are
DayZ "Spite" soda (an own 330 ml can shape by the extent of the vanilla SodaCan 0.064 x 0.123 - with a
proxy the config sets the brand); the turns of tape on the lamp and the roll on the table are DayZ
blue tape (Izolent_co, with which DayZ magazines are taped). "Working" is a loop: a desk fan on the
shelf, its impeller spins (bone ozl_work, a model.cfg loop); the lamp is lit (ozl_lamp, _on atlas).

The table is kfurn.workbench (worktop="metal", as in M05/M23) of the same size as M05/M11/M15/M23:
the electronics assembler's table IZhSK.296375.001 ("Signal" catalog, version -03), top 1600 x 710 mm,
height 785-810 mm. Here it is 1.60 x 0.72 m, the work surface at 0.78, a 0.42 cabinet with four
drawers, the panel and shelf at 1.40, the shelf 0.30 deep. The base has no power strip and no lamp:
the lamp is own, taped to the panel.

The Freedom variant is the first Freedom model and sets their look for M28-M31; not like M23 (Duty:
black with red, everything in its place). The cabinet and panel are bright green (no olive), the
frame and shelf are gray hammer-finish enamel, the top is gray paint scratched down to metal. The
cabinet has overlapping decals: some are short English warning words (CAUTION, FRAGILE, HIGH
VOLTAGE, THIS SIDE UP, KEEP DRY, WARNING, DANGER - allowed on Freedom only), a peace sign and
LEGALIZE, the rest are pictograms and patterns; no names, brands or logos. Worn, dusty, a bit
careless: scratches, chips down to metal, dust, decals faded and scratched, some with a peeled
corner; no rust (build_scuffed is the M23 build_worn builder, the decals lie over the wear).

Props and sizes:
- a gun cleaning mat ~0.90 x 0.34 x 0.003 (rubber, a 25 mm grid; by the class of rifle mats,
  36 x 14 inches - an estimate);
- the sights (own): PSO-1 - 375 x 69 x 170 mm with the eyecup (pso1.py, sources there), ACOG TA31
  class with the base - 150 x 51 x 64 mm (acog.py); both stand on their bases on the mat;
- suppressors: KAC QDSS NT4 class (mid-1990s) - length 6.4-6.75 inches (~0.17 m), O ~40 - an
  estimate; the second, thicker one (dia. 45 x 0.19) stands on its end;
- Pelican class cases: the big 1520 - outside 19.78 x 15.77 x 7.41 inches (0.502 x 0.401 x
  0.188 m), two under the table stacked, the top one crooked; the small 1200 - 11.62 x 9.68 x
  5.50 inches (0.295 x 0.246 x 0.140 m) on the left shelf; no logos: a lid and bottom with a seam,
  two double-throw latches, a hinged handle, a valve, a hinge;
- 330 ml soda cans: the extent of the vanilla DayZ can 0.064 x 0.123 (kvanilla, near LOD SodaCan);
- the slot 1 plate: steel 220 x 270 x 8 mm at the table edge, two clamps (G-clamps, ~80 mm jaw) - an
  estimate; the M81 module has an 84 x 84 plate with 124 mm lugs across, which sits on it, the lugs
  on two bolts of the plate;
- a desk fan of the "Veterok" class (USSR): a metal body in blue-gray hammer-finish enamel, soft
  blades without a guard, ~0.30 m; impeller dia. 0.23, base dia. 0.15 - an estimate;
- a cleaning rod with a handle and brushes, a bottle of gun oil, a roll of blue tape;
- on the panel: a desk lamp with a spring arm (yellow, two arms ~0.28 m - an estimate), its stand with
  a clamp taped to the panel; a magnetic strip with tools, crooked; ear defenders on a hook.

Working look: ozl_lamp is the lamp and the white inside of the shade ("working" - _on atlas); the fan
impeller is the bone ozl_work on the source ozl_work: a model.cfg loop (sourceAddress loop, maxValue
1/10) - 10 turns per pass, a pass is 2 s, 5 rev/s. The modules in the slots "work" together with the
station.

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
import layout as L  # noqa: E402
import m27_geo as q  # noqa: E402
import pso1  # noqa: E402
import acog  # noqa: E402  (after pso1, which it uses)

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
X0, X1, Y0, Y1 = L.X0, L.X1, L.Y0, L.Y1
ZT, ZP, SHD, CAB_W = L.ZT, L.ZP, L.SHD, L.CAB_W
YP, YS = L.YP, L.YS
ZS = ZP - 0.02                                               # bottom of the shelf
ZM = L.ZM                                                    # top of the mat
YE = Y0 - 0.01                                               # front edge of the countertop
# sights on the mat (own): the PSO-1 under the lamp, the bracket toward the person, the objective toward
# -x at 8 degrees; the ACOG with the objective toward the right front corner of the mat, the windage cap
# toward the person. The bottoms of the bases are on the mat
PSO_POSE = pso1.Pose((-0.26, -0.13), 188.0, ZM)
ACOG_POSE = acog.Pose((0.06, -0.205), -20.0, ZM)
# cabinet drawer handles (kfurn.workbench: fronts 1:1:1:1.4, the handle is 0.055 below the top of the front)
HANDLE_X, HANDLE_Y = (X1 - CAB_W + X1) / 2, Y0 + 0.02 - 0.018
HANDLE_Z = (0.691, 0.540, 0.390, 0.239)
# module places: proxy points (the module origin is the middle of its bottom)
PW, PD, PT = L.PLATE
MODS = [(L.SLOT1[0], L.SLOT1[1], ZT + PT), (L.SLOT2[0], L.SLOT2[1], ZM), (L.SLOT3[0], L.SLOT3[1], ZT)]
MOD_OBJ = [("m81_barrel_vise", "ozr_barrel_vise"), ("m82_borescope", "ozr_borescope"), ("m83_gauge_set", "ozr_gauge_set")]
CLAMP_X = (L.SLOT1[0] - 0.09, L.SLOT1[0] + 0.09)
# empty slots 2 and 3 are clean spots (the mat under the borescope case, the sheet under the gauge box)
CLEAN2 = (L.SLOT2[0] - 0.112, L.SLOT2[0] + 0.112, L.SLOT2[1] - 0.075, L.SLOT2[1] + 0.07)
w3, d3 = L.SLOT3_FOOT
CLEAN3 = (L.SLOT3[0] - w3 / 2, L.SLOT3[0] + w3 / 2, L.SLOT3[1] - d3 / 2, L.SLOT3[1] + d3 / 2)
# lamp: the stand is taped to the panel (bottom, top), the elbow under the shelf, the head, where it shines
LAMP_X = -0.60
YC = YP - 0.012
C0, C1 = Vector((LAMP_X, YC, 0.96)), Vector((LAMP_X, YC, 1.13))
ELBOW = Vector((-0.585, 0.13, 1.33))
HEAD = Vector((-0.47, -0.10, 1.25))
AIM = Vector((-0.26, -0.13, ZM))
# magnetic strip (x0, x1, z0, z1), its face; ear defenders on a hook
STRIP = (0.02, 0.36, 1.165, 1.195)
YSTRIP = YP - 0.014
MUFF_X, MUFF_Z = 0.52, 1.10
# fan on the shelf: base place, pivot height, tilt down and yaw toward the mat, degrees
FAN_X, FAN_Y, FAN_PIVOT, FAN_TILT, FAN_YAW = -0.22, 0.21, 0.15, 25.0, 12.0
FAN_TURNS = 10                                               # turns per loop pass (5 rev/s over 2 s)

LOD_SPECS = [
    dict(lod=0, bev=1, sides=12),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "wb": ("paint_frame", 0.7), "wb_cab": ("paint_cab", 0.9), "wb_front": ("paint_front", 1.5),
    "wb_panel": ("paint_panel", 0.9),
    "wb_top": ("paint_top", 0.9), "steel": ("steel", 1.0), "black": ("black", 1.0), "rubber": ("rubber", 0.5),
    "mat": ("mat", 1.0), "supp": ("supp", 2.0),
    "supp_tan": ("supp_tan", 2.0), "soot": ("soot", 2.0), "chrome": ("chrome", 1.6), "brass": ("brass", 1.6),
    "grip_black": ("grip_black", 1.6), "tool_dark": ("tool_dark", 1.6),
    "bottle": ("bottle", 1.4), "cap_red": ("cap_red", 1.4), "label": ("label", 1.6),
    "case_black": ("case_black", 1.3), "case_tan": ("case_tan", 1.0), "case_hw": ("case_hw", 1.4),
    "lamp_paint": ("lamp_paint", 1.2), "shade_in": ("shade_in", 1.2), "bulb": ("bulb", 2.0),
    "cable": ("cable", 1.4), "card": ("card", 1.6), "muff": ("muff", 1.4),
    "mount": ("mount", 1.4), "bolt": ("bolt", 2.0), "clamp": ("clamp", 1.4),
    "fan_body": ("fan_body", 1.2), "fan_blade": ("fan_blade", 1.4),
}
REGIONS.update(pso1.REGIONS)
REGIONS.update(acog.REGIONS)

# vanilla textures by path: section -> (_co, rvmat)
VSECT = {
    "soda": (r"dz\gear\drinks\data\SodaCan_spite_co.paa", r"dz\gear\drinks\data\sodacan.rvmat"),
    "izolent": (r"dz\weapons\attachments\data\Izolent_co.paa", r"dz\weapons\attachments\data\izolenta.rvmat"),
}
# pieces of images: rectangles (x0, x1, y0, y1) and circles (cx, cy, rx, ry) - fractions, y from the top down
SODA_BAND, SODA_RIM = (0.0, 0.858), (0.0, 0.77, 0.004, 0.027)
SODA_TOP, SODA_BOTTOM = (0.795, 0.24, 0.198, 0.198), (0.11, 0.14, 0.10, 0.10)
IZO = (0.43, 0.73, 0.40, 0.53)
IZO_DISK = (0.58, 0.465, 0.12, 0.06)

# =============================================================================
# Materials
# =============================================================================


def build_scuffed(mat, origin, color, bare=kmats.lin((112, 112, 116)), seed=1.0, gloss=0.32, spec=0.25,
                  wear=(0.66, 0.71), edge_k=0.7, rub=(), stripes=(), scratch=0.0, oil=0.0, floor_z=0.0,
                  dust=0.3, grime=0.3, decal_items=(), clean=(), clean_k=0.6, clean_tone=0.95):
    """Scuffed, careless paint without rust - the build_worn builder from M23, only the decals go over the
    wear: under a decal the paint is intact, the decal itself is already worn in the PNG. Rubbed to metal
    on the edges (edge_k) and where hands take it (rub - [(center, semi-axes, strength)]); scratches along
    x, oil spots on top (oil); stripes of another color - stripes [((x0, x1, y0, y1, z0, z1), color)] in
    model coordinates; clean - [(x0, x1, y0, y1)]: where something usually stands (an empty module slot)
    - cleaner, no oil and dust (clean_k - how much, clean_tone - the tone: the paint did not fade under an
    object); decals (the mat grid) stay in the clean spot."""
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
        base = t.mixc(inside, base, tuple(c * 0.9 for c in scol[:3]) + (1,))
        base = t.mixc(t.math("MULTIPLY", inside, t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0)),
                      base, scol)
    col = base
    edge = t.maprange(t.edge_wear(0.004), 0.05, 0.22, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 11.0, 10.0, 0.7), 0.75), t.math("MULTIPLY", edge, edge_k))
    grain = t.maprange(t.noise(vec, 34.0, 8.0, 0.7), 0.3, 0.7, 0.55, 1.0)
    for c, r, k in rub:
        d = t.node("ShaderNodeVectorMath")
        d.operation = "SUBTRACT"
        t.link(pos, d.inputs[0])
        d.inputs[1].default_value = c
        qn = t.node("ShaderNodeVectorMath")
        qn.operation = "DIVIDE"
        t.link(d.outputs[0], qn.inputs[0])
        qn.inputs[1].default_value = r
        ln = t.node("ShaderNodeVectorMath")
        ln.operation = "LENGTH"
        t.link(qn.outputs[0], ln.inputs[0])
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
        col = t.mixc(t.math("MULTIPLY", spot, clean_k), col, tuple(c * clean_tone for c in color[:3]) + (1,))
        if decal_items:
            col = t.mixc(spot, col, kmats.decals(t, col, sep, nsep, decal_items))
        dirt = t.math("MULTIPLY", dirt, t.math("SUBTRACT", 1.0, spot))
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g_, s_, h)


def decal_y(name, x0, x1, z0, z1, y):
    """Decal facing -y, only on the face at depth y."""
    return (os.path.join(WORK, name), "y", -1, ("x", "z"), ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0),
            (y - 0.002, y + 0.002))


def decal_x(name, y0, y1, z0, z1, x):
    """Decal facing +x (the right side)."""
    return (os.path.join(WORK, name), "x", 1, ("y", "z"), ((y0 + y1) / 2, (z0 + z1) / 2), (y1 - y0, z1 - z0),
            (x - 0.002, x + 0.002))


def decal_z(name, x0, x1, y0, y1, z):
    """Decal facing up."""
    return (os.path.join(WORK, name), "z", 1, ("x", "y"), ((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0, y1 - y0),
            (z - 0.002, z + 0.002))


GREEN = kmats.lin((62, 152, 44))
GREY = kmats.lin((78, 80, 80))
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
FRAME = dict(color=GREY, seed=2.1, wear=(0.68, 0.73), edge_k=0.7, scratch=0.4, floor_z=0.0, dust=0.3, grime=0.3)
TOP_RUB = [((0.0, Y0 - 0.01, ZT), (0.95, 0.07, 0.05), 0.30),       # front edge
           ((-0.05, -0.15, ZT), (0.50, 0.20, 0.03), 0.20),          # work place by the mat
           ((L.SLOT1[0], -0.30, ZT), (0.18, 0.10, 0.05), 0.30),     # by the vise plate
           ((0.60, -0.22, ZT), (0.22, 0.14, 0.03), 0.15)]
FRONT_RUB = [((HANDLE_X, HANDLE_Y, z), (0.11, 0.06, 0.05), 0.35) for z in HANDLE_Z]
x0_, x1_, z0_, z1_ = L.CAB_FACE
CAB_DECAL = decal_y("decal_cab.png", x0_, x1_, z0_, z1_, L.Y_FRONTS)
y0_, y1_, z0_, z1_ = L.CAB_SIDE
SIDE_DECAL = decal_x("decal_side.png", y0_, y1_, z0_, z1_ - 0.08, X1)
x0_, x1_, z0_, z1_ = L.PANEL
PANEL_DECAL = decal_y("decal_panel.png", x0_, x1_, z0_, z1_, YP)
x0_, x1_, z0_, z1_ = L.BIG_FACE
CASE_DECAL = decal_y("decal_case.png", x0_, x1_, z0_, z1_, L.BIG_LOW[1])
x0_, x1_, z0_, z1_ = L.SMALL_FACE
CASE_S_DECAL = decal_y("decal_case_s.png", x0_, x1_, z0_, z1_, L.SMALL_POS[1])
MAT_DECAL = decal_z("decal_mat.png", L.MAT[0], L.MAT[1], L.MAT[2], L.MAT[3], ZM)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "paint_frame": (build_scuffed, FRAME),
    "paint_cab": (build_scuffed, dict(FRAME, color=GREEN, seed=2.5, decal_items=[SIDE_DECAL])),
    "paint_front": (build_scuffed, dict(FRAME, color=GREEN, seed=2.9, edge_k=0.8, rub=FRONT_RUB,
                                        decal_items=[CAB_DECAL])),
    "paint_panel": (build_scuffed, dict(FRAME, color=GREEN, seed=3.7, wear=(0.72, 0.77), edge_k=0.55, scratch=0.25,
                                        floor_z=ZT, dust=0.35, grime=0.15, decal_items=[PANEL_DECAL])),
    "paint_top": (build_scuffed, dict(FRAME, color=kmats.lin((112, 114, 110)), seed=4.4, wear=(0.66, 0.71),
                                      edge_k=0.9, rub=TOP_RUB, scratch=1.0, oil=0.5, floor_z=ZT, dust=0.3,
                                      grime=0.2, clean=[CLEAN3], clean_k=0.8,
                                      clean_tone=0.78)),
    # cleaning mat: dark rubber, a grid, dust and oil; cleaner under the borescope case
    "mat": (build_scuffed, dict(color=kmats.lin((44, 47, 46)), bare=kmats.lin((44, 47, 46)), seed=5.1,
                                wear=(0.99, 1.0), edge_k=0.0, gloss=0.12, spec=0.06, oil=0.6, floor_z=ZT, dust=0.25,
                                grime=0.2, decal_items=[MAT_DECAL], clean=[CLEAN2],
                                clean_k=0.3)),
    "supp": (build_scuffed, dict(color=kmats.lin((40, 40, 42)), bare=kmats.lin((110, 110, 112)), seed=9.5,
                                 wear=(0.70, 0.76), edge_k=0.7, floor_z=ZT, dust=0.1, grime=0.3)),
    "supp_tan": (build_scuffed, dict(color=kmats.lin((124, 108, 82)), bare=kmats.lin((96, 96, 98)), seed=9.7,
                                     wear=(0.70, 0.76), edge_k=0.8, floor_z=ZT, dust=0.2, grime=0.3)),
    "soot": ("plastic", dict(color=kmats.lin((40, 38, 34)), gloss=0.1, spec=0.08, mottle=0.3, dust=0.0, grime=0.2,
                             scuff=(0.66, 0.74))),
    "chrome": ("steel", dict(seed=7.1, tone=0.30, along="z", gloss=0.75, spec=0.85, floor_z=ZT, dust=0.1, grime=0.2)),
    "tool_dark": ("steel", dict(seed=7.5, tone=0.17, along="z", gloss=0.4, spec=0.5, floor_z=ZT, dust=0.05,
                                grime=0.3)),
    "brass": ("paint", dict(CLEAN, color=kmats.lin((176, 140, 70)), gloss=0.6, spec=0.6)),
    "grip_black": ("plastic", dict(color=kmats.lin((26, 26, 26)), gloss=0.3, spec=0.2, dust=0.15, scuff=(0.6, 0.7))),
    "bottle": ("plastic", dict(color=kmats.lin((214, 210, 192)), gloss=0.35, spec=0.2, dust=0.3, grime=0.4)),
    "cap_red": ("plastic", dict(color=kmats.lin((168, 34, 28)), gloss=0.4, spec=0.3, dust=0.2, grime=0.3)),
    "label": ("plastic", dict(color=kmats.lin((196, 176, 120)), gloss=0.1, spec=0.05, mottle=0.25, dust=0.2,
                              grime=0.5)),
    # cases: impact-resistant plastic, lighter scratches, dust; decals
    "case_black": (build_scuffed, dict(color=kmats.lin((30, 30, 32)), bare=kmats.lin((66, 66, 68)), seed=10.3,
                                       gloss=0.3, spec=0.2, wear=(0.70, 0.76), edge_k=0.8, scratch=0.6, dust=0.45,
                                       grime=0.35, decal_items=[CASE_DECAL, CASE_S_DECAL])),
    "case_tan": (build_scuffed, dict(color=kmats.lin((150, 128, 94)), bare=kmats.lin((176, 160, 130)), seed=10.7,
                                     gloss=0.3, spec=0.2, wear=(0.70, 0.76), edge_k=0.8, scratch=0.6, dust=0.45,
                                     grime=0.35)),
    "case_hw": ("plastic", dict(color=kmats.lin((34, 34, 36)), gloss=0.35, spec=0.25, dust=0.3)),
    # lamp: yellow enamel, chips
    "lamp_paint": (build_scuffed, dict(color=kmats.lin((222, 172, 34)), seed=8.7, wear=(0.70, 0.75), edge_k=0.8,
                                       floor_z=ZT, dust=0.4, grime=0.15)),
    "shade_in": ("plastic", dict(color=kmats.lin((214, 212, 200)), gloss=0.6, spec=0.45, dust=0.2, grime=0.2)),
    "shade_in_on": ("flat", dict(color=kmats.lin((255, 244, 214)), gloss=0.6, spec=0.45)),
    "bulb": ("flat", dict(color=kmats.lin((210, 206, 194)), gloss=0.7, spec=0.6)),
    "bulb_on": ("flat", dict(color=kmats.lin((255, 248, 222)), gloss=0.7, spec=0.6)),
    "cable": ("plastic", dict(color=kmats.lin((24, 24, 24)), gloss=0.35, spec=0.25, dust=0.3)),
    "card": ("plastic", dict(color=kmats.lin((150, 120, 80)), gloss=0.1, spec=0.05, mottle=0.2, dust=0.1)),
    "muff": ("plastic", dict(color=kmats.lin((52, 58, 46)), gloss=0.3, spec=0.2, dust=0.35, scuff=(0.62, 0.7))),
    # slot 1 plate: blued steel, worn at the edges, oil; the clamps - red-orange enamel, chipped
    "mount": (build_scuffed, dict(color=kmats.lin((44, 46, 48)), bare=kmats.lin((120, 120, 124)), seed=6.3,
                                  wear=(0.60, 0.66), edge_k=1.0, scratch=0.9, oil=0.6, floor_z=ZT, dust=0.1,
                                  grime=0.4)),
    "bolt": ("steel", dict(seed=6.6, tone=0.24, along="z", gloss=0.45, spec=0.55, floor_z=ZT, dust=0.05, grime=0.5)),
    "clamp": (build_scuffed, dict(color=kmats.lin((168, 66, 30)), bare=kmats.lin((96, 94, 92)), seed=6.9,
                                  wear=(0.64, 0.70), edge_k=1.0, scratch=0.3, floor_z=0.0, dust=0.2, grime=0.4)),
    # fan: blue-gray hammer-finish enamel, soft blades of dark rubber, dust on everything
    "fan_body": (build_scuffed, dict(color=kmats.lin((96, 112, 122)), bare=kmats.lin((130, 130, 128)), seed=11.7,
                                     wear=(0.72, 0.78), edge_k=0.8, scratch=0.2, floor_z=ZP, dust=0.55, grime=0.3)),
    "fan_blade": ("plastic", dict(color=kmats.lin((40, 42, 44)), gloss=0.25, spec=0.15, mottle=0.15, dust=0.5,
                                  grime=0.3)),
})
KINDS.update(pso1.kinds(PSO_POSE, floor_z=ZT))
KINDS.update(acog.kinds(ACOG_POSE, floor_z=ZT))

OBJ, NAME = "m27_frd_pack_ball", "ozr_frd_pack_ball"
# Working look: the lamp and the inside of the shade are ozl_lamp (in hiddenSelections; "working" - the
# _on_co atlas and the _on rvmat with glow); the fan impeller is the bone ozl_work, a model.cfg loop.
SEL_LAMP, SEL_FAN = "ozl_lamp", "ozl_work"
ON = dict(remap={"shade_in": "shade_in_on", "bulb": "bulb_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
FAN_ANIM = ("ozl_work_fan", dict(type="rotation", source="ozl_work", sourceAddress="loop", selection=SEL_FAN,
                                 axis="ozl_work_axis", memory=1, minValue=0.0, maxValue=1.0 / FAN_TURNS, angle0=0.0,
                                 angle1=2 * math.pi))
# module proxies: the slots OZL_Tool1..3 are linked to them by CfgNonAIVehicles of the mod (Proxyozl_tool1..3);
# slot N is module N of the "Ballistics" line (M81, M82, M83), without rotation: the modules face the person
PROXIES = [(r"\OpenZone_Research\models\proxies\ozl_tool%d" % (i + 1), m) for i, m in enumerate(MODS)]
# vanilla items: on the magnetic strip - tip and jaws down, crooked; on the table and shelf
DECOR = [
    kv.put("screwdriver", (0.075, YSTRIP, 1.168), **kv.hung(-84)),
    kv.put("screwdriver", (0.145, YSTRIP, 1.160), **kv.hung(-97)),
    kv.put("pliers", (0.305, YSTRIP, 1.150), **kv.hung(-81)),
    kv.put("cleaningkit", (-0.60, 0.075, ZT), **kv.flat(2)),
    kv.put("rags", (0.66, 0.18, ZT), **kv.flat(0)),
    # STANAG magazines taped together (a single magazine is not drawn as a proxy: class Proxymagazine_stanag30)
    kv.put(r"dz\weapons\attachments\magazine\magazine_stanag30_coupled", (0.63, -0.25, ZT), **kv.flat(12)),
    kv.put(r"dz\weapons\ammunition\556_LooseRounds", (0.475, -0.28, ZT), up=(0, 0, 1), fwd=(0.3, -1, 0)),
    kv.put(r"dz\weapons\ammunition\556_20RoundBox", (0.772, -0.24, ZT), **kv.flat(84)),
    kv.put("ducttape", (0.03, 0.20, ZP), **kv.flat(0)),
    kv.put("radio", (0.36, 0.29, ZP), up=(0, 0, 1), fwd=(0, -1, 0)),
    kv.put("cassette", (0.63, 0.13, ZP), **kv.flat(18)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 selections=(SEL_LAMP, SEL_FAN), hidden=(SEL_LAMP,), states={"on": ON}, bones=((SEL_FAN, ""),),
                 animations=(FAN_ANIM,), sources={"ozl_work": dict(animPeriod=2.0)}, proxies=PROXIES, decor=DECOR,
                 modules=[(o, n, m) for (o, n), m in zip(MOD_OBJ, MODS)], vsections=VSECT, glass=pso1.GLASS)
P = M.part
BOUNDS = {}
AXES = {}


# =============================================================================
# Primitives
# =============================================================================
def turn(cx, cy, z, deg):
    """Local axes rotated about the vertical: u along the item, v across, n up."""
    a = math.radians(deg)
    return g.Frame((cx, cy, z), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))


def vp(name, section):
    """A part with a vanilla texture (section VSECT)."""
    return q.vpart(P(name, "black", section=section))


def cable(part, pts, r, lod, k=4):
    """Cable as a smooth curve through the points (g.pipe: the section is carried along the cable, not twisted)."""
    g.pipe(part, q.spline(pts, k) if lod == 0 else [tuple(p) for p in pts], r, 6 if lod == 0 else 4)


# =============================================================================
# Table (kfurn.workbench, metal): chamfers, panel screws
# =============================================================================
BEVEL = {"wb_frame": 0.003, "wb_fronts": 0.0025, "wb_shelf": 0.0015, "wb_panel": 0.003}


def build_bench(spec):
    """The base; the cabinet body is its own region wb_cab (green) in the frame part: kuv puts the faces
    of a part with one side into one rectangle, and the inner faces of the left legs would land on the
    texture of the cabinet side. Chamfers (the kfurn base is boxes with sharp edges) - on the near LOD."""
    lod = spec["lod"]
    parts = kfurn.workbench(M, spec, X0, X1, Y0, Y1, ZT, ZP, SHD, cab_w=CAB_W, worktop="metal", outlets=0,
                            lamp=False)
    for p in parts:
        if lod == 0 and p.name in BEVEL:
            g.bevel(p.bm, p.bm.edges[:], BEVEL[p.name], 1)
    fr = next(p for p in parts if p.name == "wb_frame")
    kind, scale = REGIONS["wb_cab"]
    idx = fr.region_index("wb_cab", kind, scale)
    for f in fr.bm.faces:
        c = f.calc_center_median()
        if c.x > X1 - CAB_W - 0.001 and c.z < ZT - 0.029:
            f[fr.reg] = idx
    if lod == 0:
        sc = P("panel_screws", "steel")
        for x in (X0 + 0.06, X1 - 0.06):
            for z in (ZT + 0.035, ZS - 0.03):
                q.screw(sc, (x, YP, z), (0, -1, 0), 0.0045, 0.002, 8)
        parts.append(sc)
    return parts


# =============================================================================
# Slot 1: a plate on the table edge, two clamps, bolts for the lugs of the M81 vise
# =============================================================================
def build_slot1(spec):
    lod = spec["lod"]
    cx, cy = L.SLOT1
    mt = P("vise_plate", "mount")
    q.bbox(mt, cx - PW / 2, cx + PW / 2, YE, YE + PD, ZT, ZT + PT, 0.0015, lod)
    parts = [mt]
    if lod == 2:
        return parts
    bt = P("vise_bolts", "bolt")
    for s in (-1, 1):
        x = cx + s * 0.062
        if lod == 0:
            q.lathe(bt, [(0.0105, 0.0), (0.0105, 0.0015)], 12, (x, cy, ZT + PT), cap1=True)       # washer
        q.hexhead(bt, (x, cy, ZT + PT + 0.0015), (0, 0, 1), 0.017, 0.007)
        if lod == 0:
            q.lathe(bt, [(0.005, 0.0), (0.005, 0.006), (0.0035, 0.0075)], 8, (x, cy, ZT + PT + 0.0085), cap1=True)
    parts.append(bt)
    # clamps: a frame in the y-z plane across the table edge, a screw from below into the countertop, a tommy bar
    cl = P("clamps", "clamp")
    sw = P("clamp_screws", "steel")
    zu = ZT - 0.03                                             # bottom of the countertop
    ztop = ZT + PT + 0.004
    ys = YE + 0.016                                            # screw axis
    for x in CLAMP_X:
        pts = [(x, YE + 0.025, ztop + 0.006), (x, YE - 0.012, ztop + 0.006), (x, YE - 0.030, ztop - 0.008),
               (x, YE - 0.033, zu - 0.020), (x, YE - 0.022, zu - 0.042), (x, YE + 0.006, zu - 0.046),
               (x, YE + 0.030, zu - 0.046)]
        g.sweep(cl, q.spline(pts, 3) if lod == 0 else pts, (1, 0, 0), 0.0065, 0.005)
        if lod == 1:
            continue
        q.lathe(cl, [(0.011, 0.0), (0.011, 0.004)], 10, (x, YE + 0.018, ZT + PT), cap1=True)  # heel
        q.rod(sw, (x, ys, zu - 0.075), (x, ys, zu - 0.004), 0.0045, 8)                       # screw
        q.lathe(sw, [(0.009, 0.0), (0.009, 0.004)], 10, (x, ys, zu - 0.004), cap1=True)     # screw heel
        q.rod(sw, (x - 0.035, ys, zu - 0.070), (x + 0.035, ys, zu - 0.070), 0.0028, 6)      # tommy bar
        for s in (-1, 1):
            q.lathe(sw, [(0.0, -0.005), (0.0045, 0.0), (0.0, 0.005)], 6, (x + s * 0.037, ys, zu - 0.070), (1, 0, 0))
    parts.append(cl)
    if lod == 0:
        parts.append(sw)
    return parts


def build_mat(spec):
    if spec["lod"] == 2:
        return []
    x0, x1, y0, y1, t = L.MAT
    mt = P("mat", "mat")
    q.bbox(mt, x0, x1, y0, y1, ZT, ZT + t, 0.0012, spec["lod"])
    return [mt]


def build_scopes(spec):
    """Sights on the mat (own): the PSO-1 (pso1.py) and a compact ACOG class one (acog.py); the lens
    glasses are the model's glass section."""
    return pso1.build(P, spec["lod"], PSO_POSE) + acog.build(P, spec["lod"], ACOG_POSE)


# =============================================================================
# Suppressors, cleaning rod
# =============================================================================
def build_supps(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    n = 16 if lod == 0 else 8
    parts = []
    # NT4 class suppressor lies on the mat: a knurled coupling at the rear, a body, an end with a bevel
    sp = P("supp", "supp")
    fr = turn(-0.33, -0.27, ZM + 0.020, 4.0)
    o = fr.p(-0.085, 0, 0)
    prof = [(0.0, 0.0), (0.012, 0.0), (0.0160, 0.003), (0.0160, 0.020), (0.0195, 0.024), (0.0200, 0.027),
            (0.0200, 0.160), (0.0180, 0.168), (0.0085, 0.170)]
    q.lathe(sp, prof if lod == 0 else [prof[i] for i in (0, 1, 3, 5, 6, 8)] + [(0.0, 0.170)], n, o, fr.u)
    if lod == 0:
        q.star_prism(sp, o, fr.u, 0.0172, 0.0012, 14, 0.005, 0.018, cap1=False)
    parts.append(sp)
    # the second, thicker one, stands on its end: grooves along the body
    s2 = P("supp_tan", "supp_tan")
    c2 = (0.06, 0.06, ZT)
    prof2 = [(0.0, 0.0), (0.019, 0.0), (0.0225, 0.006), (0.0225, 0.058), (0.0219, 0.060), (0.0225, 0.062),
             (0.0225, 0.124), (0.0219, 0.126), (0.0225, 0.128), (0.0225, 0.184), (0.020, 0.190), (0.009, 0.192)]
    q.lathe(s2, prof2 if lod == 0 else [prof2[i] for i in (0, 1, 2, 9, 10)] + [(0.0, 0.190)], 12 if lod == 0 else 8, c2)
    parts.append(s2)
    if lod == 0:
        so = P("supp_bore", "soot")
        q.lathe(so, [(0.0085, 0.0), (0.0, 0.0)], 10, fr.p(0.0852, 0, 0), fr.u)
        q.lathe(so, [(0.009, 0.0), (0.0, 0.0)], 10, (c2[0], c2[1], ZT + 0.1922))
        parts.append(so)
    return parts


def build_rod(spec):
    """Cleaning rod with a bearing handle and a brass brush - in front of the borescope, two spare brushes."""
    lod = spec["lod"]
    if lod == 2:
        return []
    a, b = Vector((-0.13, -0.300, ZM + 0.0125)), Vector((0.36, -0.287, ZM + 0.0035))
    d = (b - a).normalized()
    n = 10 if lod == 0 else 6
    hd = P("rod_handle", "grip_black")
    prof = [(0.0, 0.0), (0.008, 0.002), (0.0115, 0.010), (0.0125, 0.030), (0.0120, 0.065), (0.0100, 0.082),
            (0.0060, 0.088)]
    q.lathe(hd, prof if lod == 0 else [prof[i] for i in (0, 2, 4, 6)], n, a, d)
    rd = P("rod", "chrome")
    q.lathe(rd, [(0.0065, 0.0), (0.0065, 0.010), (0.0028, 0.012)], 8 if lod == 0 else 5, a + d * 0.087, d)
    q.rod(rd, a + d * 0.099, b - d * 0.04, 0.0028, 6 if lod == 0 else 4)
    parts = [hd, rd]
    if lod == 0:
        br = P("brushes", "brass")
        q.star_prism(br, b - d * 0.04, d, 0.0060, 0.0018, 10, 0.0, 0.034)                      # brush on the rod
        for p0, ang in (((0.29, -0.250, ZM + 0.0055), 8.0), ((0.335, -0.262, ZM + 0.0050), -14.0)):
            dd = Vector((math.cos(math.radians(ang)), math.sin(math.radians(ang)), 0.0))
            q.star_prism(br, p0, dd, 0.0055, 0.0016, 10, 0.0, 0.028)
            q.rod(br, Vector(p0) - dd * 0.012, Vector(p0), 0.0022, 6)
        parts.append(br)
    return parts


# =============================================================================
# Soda cans (vanilla "Spite" texture), a bottle of oil, a roll of tape
# =============================================================================
# (x, y, z of the support, stands - None / lies at an angle, degrees)
CANS = [
    (-0.30, 0.18, ZT, None),
    (0.30, 0.22, ZT, 22.0),
    (-0.08, -0.24, 0.0, 70.0),
    (0.15, 0.13, ZP, None),
    (0.70, 0.22, ZP, 84.0),
]
CAN_R, CAN_H = 0.032, 0.122


def soda_can(part, o, a, lod):
    """330 ml can from the bottom o along axis a: the label unwrap, the shell and the lid follow the DayZ
    picture."""
    n = 12 if lod == 0 else 8
    s0, s1 = SODA_BAND
    prof = [(0.026, 0.0, 0.975), (0.032, 0.010, 0.957), (0.032, 0.098, 0.52), (0.027, 0.114, 0.475)]
    q.uv_lathe(part, prof if lod == 0 else [prof[i] for i in (0, 2, 3)], n, o, a, s0, s1)
    r0, r1, t0, t1 = SODA_RIM
    q.uv_lathe(part, [(0.027, 0.114, t1), (0.0272, 0.1215, t0)], n, o, a, r0, r1)
    q.uv_disk(part, Vector(o) + Vector(a) * 0.1215, a, 0.0272, n, SODA_TOP)
    q.uv_disk(part, o, -Vector(a), 0.026, n, SODA_BOTTOM)


def build_cans(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    cn = vp("cans", "soda")
    for x, y, z, lie in CANS:
        if lie is None:
            soda_can(cn, (x, y, z), (0, 0, 1), lod)
        else:
            a = Vector((math.cos(math.radians(lie)), math.sin(math.radians(lie)), 0.0))
            soda_can(cn, Vector((x, y, z + CAN_R)) - a * (CAN_H / 2), a, lod)
    return [cn]


def build_table_bits(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    n = 16 if lod == 0 else 8
    # gun oil bottle: shoulder, neck, a red cap with a spout, a paper label
    bx, by = -0.14, 0.17
    bt = P("bottle", "bottle")
    prof = [(0.0, 0.0), (0.024, 0.0), (0.0255, 0.003), (0.0255, 0.075), (0.022, 0.090), (0.012, 0.100),
            (0.010, 0.106)]
    q.lathe(bt, prof if lod == 0 else [prof[i] for i in (1, 3, 5, 6)], n, (bx, by, ZT))
    cp = P("bottle_cap", "cap_red")
    cprof = [(0.0, 0.106), (0.011, 0.106), (0.011, 0.118), (0.0065, 0.122), (0.0045, 0.134), (0.0015, 0.140),
             (0.0, 0.140)]
    q.lathe(cp, cprof if lod == 0 else [cprof[i] for i in (1, 2, 4, 6)], 10 if lod == 0 else 6, (bx, by, ZT))
    parts += [bt, cp]
    if lod == 0:
        lb = P("bottle_label", "label")
        q.lathe(lb, [(0.0258, 0.018), (0.0258, 0.064)], n, (bx, by, ZT))
        parts.append(lb)
    # roll of blue tape (the DayZ tape texture), a cardboard core
    tx, ty = 0.45, 0.10
    tp = vp("tape_roll", "izolent")
    s0, s1, t0, t1 = IZO
    q.uv_lathe(tp, [(0.040, 0.0, t1), (0.040, 0.019, t0)], 16 if lod == 0 else 8, (tx, ty, ZT), (0, 0, 1), s0, s1)
    q.uv_disk(tp, (tx, ty, ZT + 0.019), (0, 0, 1), 0.040, 16 if lod == 0 else 8, IZO_DISK, r_in=0.026)
    parts.append(tp)
    cd = P("tape_core", "card")
    q.lathe(cd, [(0.0245, 0.0193), (0.0245, 0.0)], 12 if lod == 0 else 6, (tx, ty, ZT))
    q.lathe(cd, [(0.0262, 0.0193), (0.0245, 0.0193)], 12 if lod == 0 else 6, (tx, ty, ZT))
    parts.append(cd)
    return parts


# =============================================================================
# Pelican class cases
# =============================================================================
def pelican(body, hw, fr, size, lod):
    """Case with the bottom center at fr.o, facing -v: a bottom and a lid with rounded corners, a seam,
    two double-throw latches, a hinged handle, a valve, a hinge at the back, ribs on the lid."""
    Lx, D, H = size
    zs = H * 0.72
    if lod == 2:
        g.box(body, -Lx / 2, Lx / 2, -D / 2, D / 2, 0.0, H, frame=fr)
        return
    rb = dict(r=0.013, seg=2) if lod == 0 else {}
    g.box(body, -Lx / 2, Lx / 2, -D / 2, D / 2, 0.0, zs - 0.004, frame=fr, **rb)
    g.box(body, -Lx / 2, Lx / 2, -D / 2, D / 2, zs + 0.004, H, frame=fr, **rb)
    g.box(body, -Lx / 2 - 0.004, Lx / 2 + 0.004, -D / 2 - 0.004, D / 2 + 0.004, zs - 0.007, zs + 0.007, frame=fr,
          **(dict(r=0.004, seg=1) if lod == 0 else {}))
    if lod > 0:
        return
    for s in (-1, 1):                                                                  # ribs on the lid
        g.box(body, s * Lx * 0.3 - 0.012, s * Lx * 0.3 + 0.012, -D / 2 + 0.03, D / 2 - 0.03, H - 0.002, H + 0.004,
              frame=fr, r=0.003, seg=1)
    for s in (-1, 1):                                                                  # latches
        xc = s * (Lx / 2 - 0.13 * Lx / 0.5)
        g.box(hw, xc - 0.024, xc + 0.024, -D / 2 - 0.009, -D / 2 + 0.001, zs - 0.045, zs - 0.012, frame=fr)  # body
        g.box(hw, xc - 0.021, xc + 0.021, -D / 2 - 0.016, -D / 2 - 0.007, zs - 0.040, zs + 0.026, frame=fr,
              r=0.0025, seg=1)                                                         # lever
        g.box(hw, xc - 0.014, xc + 0.014, -D / 2 - 0.012, -D / 2, zs + 0.018, zs + 0.030, frame=fr)  # hook
    # handle: hinges and a bail, folded down along the lid face
    for s in (-1, 1):
        g.box(hw, s * 0.075 - 0.010, s * 0.075 + 0.010, -D / 2 - 0.014, -D / 2, zs + 0.012, zs + 0.034, frame=fr)
    pts = [fr.p(-0.075, -D / 2 - 0.008, zs + 0.024), fr.p(-0.066, -D / 2 - 0.020, zs + 0.016),
           fr.p(0.0, -D / 2 - 0.022, zs + 0.012), fr.p(0.066, -D / 2 - 0.020, zs + 0.016),
           fr.p(0.075, -D / 2 - 0.008, zs + 0.024)]
    q.oval_tube(hw, q.spline(pts, 2), [(0.0065, 0.0085)] * 9, 6, fr.n)
    # valve with a knurled ring, a hinge at the back
    q.star_prism(hw, fr.p(Lx / 2 - 0.05, -D / 2, H * 0.40), -fr.v, 0.012, 0.0012, 8, 0.0, 0.006, cap1=False)
    q.lathe(hw, [(0.0115, 0.006), (0.0075, 0.007), (0.0, 0.009)], 8, fr.p(Lx / 2 - 0.05, -D / 2, H * 0.40), -fr.v)
    q.rod(body, fr.p(-Lx / 2 + 0.035, D / 2 + 0.006, zs), fr.p(Lx / 2 - 0.035, D / 2 + 0.006, zs), 0.006, 8)


def build_cases(spec):
    lod = spec["lod"]
    blk, tan = P("case_black", "case_black"), P("case_tan", "case_tan")
    hw = P("case_hw", "case_hw") if lod == 0 else None
    bx0, by0, _ = L.BIG_LOW
    fr = turn(bx0 + L.BIG[0] / 2, by0 + L.BIG[1] / 2, 0.0, 0.0)
    pelican(blk, hw, fr, L.BIG, lod)
    cx, cy, z0, a = L.BIG_TOP
    pelican(tan, hw, turn(cx, cy, z0 + (0.004 if lod < 2 else 0.0), a), L.BIG, lod)
    sx0, sy0, sz0 = L.SMALL_POS
    parts = [blk, tan] + ([hw] if hw else [])
    if lod < 2:
        # a part of its own: otherwise the atlas rectangle would stretch from the floor to the shelf
        sm = P("case_small", "case_black")
        hs = P("case_small_hw", "case_hw") if lod == 0 else None
        pelican(sm, hs, turn(sx0 + L.SMALL[0] / 2, sy0 + L.SMALL[1] / 2, sz0, 0.0), L.SMALL, lod)
        parts += [sm] + ([hs] if hs else [])
    return parts


# =============================================================================
# Lamp on a spring arm: the stand with a clamp is taped to the panel
# =============================================================================
def izo_band(part, c, r, w, n, axis=(0, 0, 1)):
    """A turn of tape around the stand: a low ring with a bulge."""
    s0, s1, t0, t1 = IZO
    q.uv_lathe(part, [(r - 0.0004, -w / 2, t1), (r + 0.0004, 0.0, (t0 + t1) / 2), (r - 0.0004, w / 2, t0)], n, c, axis,
               s0, s1)


def izo_strip(part, o, deg, w, h=0.019, t=0.0008):
    """Tail of tape on the panel (facing -y): from point o at angle deg, length w."""
    a = math.radians(deg)
    u = Vector((math.cos(a), 0.0, math.sin(a)))
    v = Vector((0.0, -1.0, 0.0)).cross(u).normalized()
    if v.z < 0:
        v = -v
    fr = g.Frame(o, u, v, (0, -1, 0))
    q.uv_box(part, 0.0, w, -h / 2, h / 2, 0.0, t, IZO, frame=fr)


def build_lamp(spec):
    lod = spec["lod"]
    n = 20 if lod == 0 else 8
    parts = []
    arm = P("lamp_arm", "lamp_paint")
    # stand, at the bottom the lamp clamp (there is nothing to clamp it to on the panel, so it is taped)
    q.rod(arm, C0, C1, 0.008, 8 if lod == 0 else 5)
    q.bbox(arm, LAMP_X - 0.024, LAMP_X + 0.024, YP - 0.030, YP - 0.002, C0.z - 0.055, C0.z + 0.006, 0.002, lod)
    if lod == 0:
        sw = P("lamp_clamp_screw", "steel")
        q.rod(sw, (LAMP_X, YC - 0.004, C0.z - 0.055), (LAMP_X, YC - 0.004, C0.z - 0.095), 0.0035, 6)
        parts.append(sw)
        kb = P("lamp_knobs", "grip_black")
        q.star_prism(kb, (LAMP_X, YC - 0.004, C0.z - 0.095), (0, 0, -1), 0.011, 0.0015, 8, 0.0, 0.010)
    # arms: pairs of rods, a spring under the lower one, hinges with thumb screws
    d1, d2 = (ELBOW - C1), (HEAD - ELBOW)
    s1 = d1.cross(Vector((0, 0, 1))).normalized()
    s2 = d2.cross(Vector((0, 0, 1))).normalized()
    rs = 6 if lod == 0 else 4
    if lod < 2:
        for s in (-1, 1):
            q.rod(arm, C1 + s1 * (0.011 * s), ELBOW + s1 * (0.011 * s), 0.0042, rs)
            q.rod(arm, ELBOW + s2 * (0.009 * s), HEAD + s2 * (0.009 * s), 0.0038, rs)
    else:
        q.rod(arm, C1, ELBOW, 0.006, 4)
        q.rod(arm, ELBOW, HEAD, 0.006, 4)
    for c, s, r in ((C1, s1, 0.012), (ELBOW, s1, 0.011), (HEAD, s2, 0.010)):
        q.lathe(arm, [(r, -0.017), (r, 0.017)], 10 if lod == 0 else 6, c - s * 0.0, s, cap0=True, cap1=True)
        if lod == 0 and c is not HEAD:
            q.star_prism(kb, c + s * 0.017, s, 0.010, 0.0016, 4, 0.0, 0.008)
    parts.append(arm)
    if lod == 0:
        sp = P("lamp_springs", "steel")
        nd = s1.cross(d1).normalized()
        if nd.z > 0:
            nd = -nd
        a0, a1 = C1 + d1 * 0.12 + nd * 0.016, ELBOW - d1 * 0.12 + nd * 0.016
        q.helix(sp, a0, a1, 0.0042, 0.0008, 8, k=5, sides=3)
        q.rod(sp, C1 + d1 * 0.06, a0, 0.0011, 3)
        q.rod(sp, a1, ELBOW - d1 * 0.05, 0.0011, 3)
        n2 = s2.cross(d2).normalized()
        if n2.z < 0:
            n2 = -n2
        b0, b1 = ELBOW + d2 * 0.10 + n2 * 0.015, HEAD - d2 * 0.18 + n2 * 0.015
        q.helix(sp, b0, b1, 0.0036, 0.0007, 5, k=5, sides=3)
        q.rod(sp, ELBOW + d2 * 0.05, b0, 0.0010, 3)
        q.rod(sp, b1, HEAD - d2 * 0.12, 0.0010, 3)
        parts += [sp, kb]
    # head: a shade with a rolled edge, a rear cover with a switch, a socket, a bulb
    ax = (AIM - HEAD).normalized()
    up = (Vector((0, 0, 1)) - ax * ax.z).normalized()
    so = HEAD + ax * 0.014
    sh = P("lamp_shade", "lamp_paint")
    prof = [(0.0, -0.030), (0.016, -0.028), (0.026, -0.018), (0.030, -0.004), (0.031, 0.020), (0.040, 0.045),
            (0.060, 0.080), (0.074, 0.110), (0.078, 0.120)]
    if lod:
        prof = [prof[i] for i in (0, 2, 4, 6, 8)]
    q.lathe(sh, prof, n, so, ax)
    if lod == 0:
        q.torus(sh, so + ax * 0.120, ax, 0.078, 0.0025, n, 4, phase=0.5)
    parts.append(sh)
    if lod < 2:
        si = P("lamp_shade_in", "shade_in", group=SEL_LAMP)
        inner = [(r - 0.0015, h) for r, h in prof[::-1] if h >= 0.020]
        q.lathe(si, inner, n, so, ax)
        q.lathe(si, [(inner[-1][0], 0.020), (0.0, 0.021)], n, so, ax)
        parts.append(si)
        bl = P("lamp_bulb", "bulb", group=SEL_LAMP)
        bp = [(0.0, 0.024), (0.011, 0.026), (0.014, 0.040), (0.025, 0.058), (0.029, 0.073), (0.025, 0.090),
              (0.012, 0.099), (0.0, 0.101)]
        q.lathe(bl, bp if lod == 0 else [bp[i] for i in (0, 2, 4, 6, 7)], 12 if lod == 0 else 6, so, ax)
        parts.append(bl)
    if lod == 0:
        hw = P("lamp_socket", "black")
        q.lathe(hw, [(0.0155, 0.022), (0.0155, 0.040)], 12, so, ax)
        q.rod(hw, so - ax * 0.018 + up * 0.026, so - ax * 0.018 + up * 0.040, 0.005, 8)            # switch
        parts.append(hw)
    if lod == 2:
        return parts
    # tape: turns around the stand and the clamp, tails on the panel - crooked (the DayZ tape texture)
    tp = vp("lamp_tape", "izolent")
    for z in (1.00, 1.09):
        izo_band(tp, (LAMP_X, YC, z), 0.0102, 0.019, 10 if lod == 0 else 6)
    if lod == 0:
        izo_strip(tp, Vector((LAMP_X - 0.065, YP - 0.0002, 0.985)), 12.0, 0.13)
        izo_strip(tp, Vector((LAMP_X - 0.06, YP - 0.0002, 1.105)), -16.0, 0.12)
        izo_strip(tp, Vector((LAMP_X - 0.045, YP - 0.0002, C0.z - 0.06)), 53.0, 0.13)
        q.uv_box(tp, LAMP_X - 0.0255, LAMP_X + 0.0255, YP - 0.0315, YP - 0.0015, C0.z - 0.032, C0.z - 0.013, IZO)
        # cable: from the head along the arms and the stand, down the panel, along the table and over the left edge to the floor
        cb = P("lamp_cable", "cable")
        pts = [so - ax * 0.026 + up * 0.012, HEAD - d2 * 0.12 + Vector((0, 0, -0.012)),
               HEAD - d2 * 0.5 + Vector((0, 0, -0.024)), ELBOW + Vector((0.0, 0.0, -0.022)),
               C1 + d1 * 0.5 + Vector((0.013, 0.0, -0.018)), C1 + Vector((0.014, -0.006, -0.02)),
               Vector((LAMP_X + 0.0145, YC - 0.004, 1.05)), Vector((LAMP_X + 0.016, YC - 0.004, 0.94)),
               Vector((LAMP_X + 0.03, YP - 0.010, ZT + 0.04)), Vector((LAMP_X + 0.0, YP - 0.016, ZT + 0.0045)),
               Vector((-0.72, YP - 0.03, ZT + 0.0045)), Vector((X0 - 0.013, YP - 0.04, ZT - 0.006)),
               Vector((X0 - 0.020, YP - 0.05, ZT - 0.12)), Vector((X0 - 0.03, YP - 0.08, 0.20)),
               Vector((X0 - 0.03, YP - 0.12, 0.0045)), Vector((X0 + 0.05, YP - 0.20, 0.0045))]
        cable(cb, pts, 0.0032, lod, k=2)
        parts.append(cb)
    parts.append(tp)
    return parts


# =============================================================================
# Panel: a magnetic strip with a punch (the vanilla screwdrivers and pliers are DECOR), ear defenders on a hook
# =============================================================================
def build_board(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    x0, x1, z0, z1 = STRIP
    bk = P("mag_strip", "black")
    q.bbox(bk, x0, x1, YSTRIP, YP, z0, z1, 0.002, lod)
    parts = [bk]
    if lod == 0:
        sc = P("strip_screws", "steel")
        for x in (x0 + 0.015, x1 - 0.015):
            q.screw(sc, (x, YSTRIP, (z0 + z1) / 2), (0, -1, 0), 0.004, 0.0018, 8)
        parts.append(sc)
    # the punch hangs crooked on the magnet: a knurled handle, a shank, a cone
    dk = P("punch", "tool_dark")
    a = math.radians(-6.0)
    u = Vector((math.sin(a), 0, -math.cos(a)))
    top = Vector((0.225, YSTRIP - 0.0065, z1 + 0.045))
    if lod == 0:
        q.star_prism(dk, top, u, 0.0062, 0.0007, 8, 0.0, 0.075, cap1=False)
        q.lathe(dk, [(0.0, 0.0), (0.0062, 0.0)], 12, top, u)
        q.lathe(dk, [(0.0062, 0.075), (0.0035, 0.085), (0.0030, 0.135), (0.0012, 0.140)], 8, top, u)
    else:
        q.rod(dk, top, top + u * 0.14, 0.005, 4)
    parts.append(dk)
    # ear defenders: cups (oval), ear cushions toward the panel, a band as a ribbon over the hook, yokes
    mf = P("muffs", "muff")
    nc = 12 if lod == 0 else 8
    yb = YP - 0.004
    for s in (-1, 1):
        c = Vector((MUFF_X + s * 0.05, yb, MUFF_Z))
        before = set(mf.bm.verts)
        prof = [(0.040, 0.014), (0.042, 0.024), (0.040, 0.036), (0.032, 0.046), (0.018, 0.051), (0.0, 0.052)]
        q.lathe(mf, prof if lod == 0 else [prof[i] for i in (0, 2, 4, 5)], nc, c, (0, -1, 0), cap0=True)
        for v in set(mf.bm.verts) - before:
            v.co.z = c.z + (v.co.z - c.z) * 1.22
    band = [(MUFF_X - 0.05, YP - 0.032, MUFF_Z + 0.050), (MUFF_X - 0.052, YP - 0.032, MUFF_Z + 0.095),
            (MUFF_X - 0.030, YP - 0.032, MUFF_Z + 0.132), (MUFF_X, YP - 0.032, MUFF_Z + 0.142),
            (MUFF_X + 0.030, YP - 0.032, MUFF_Z + 0.132), (MUFF_X + 0.052, YP - 0.032, MUFF_Z + 0.095),
            (MUFF_X + 0.05, YP - 0.032, MUFF_Z + 0.050)]
    pts = q.spline(band, 2) if lod == 0 else band[::3]
    q.oval_tube(mf, pts, [(0.0035, 0.010)] * len(pts), 6 if lod == 0 else 4, (0, 1, 0))
    parts.append(mf)
    if lod == 0:
        rb = P("muff_pads", "rubber")
        for s in (-1, 1):
            before = set(rb.bm.verts)
            c = (MUFF_X + s * 0.05, yb - 0.009, MUFF_Z)
            q.torus(rb, c, (0, -1, 0), 0.030, 0.0085, 12, 4)
            for v in set(rb.bm.verts) - before:
                v.co.z = c[2] + (v.co.z - c[2]) * 1.22
        hk = P("hook", "steel")
        g.pipe(hk, q.spline([(MUFF_X, YP, MUFF_Z + 0.128), (MUFF_X, YP - 0.030, MUFF_Z + 0.134),
                             (MUFF_X, YP - 0.044, MUFF_Z + 0.150)], 3), 0.0028, 6)
        for s in (-1, 1):                                                                    # cup yokes
            g.pipe(hk, q.spline([(MUFF_X + s * 0.050, YP - 0.032, MUFF_Z + 0.052),
                                 (MUFF_X + s * 0.050, YP - 0.032, MUFF_Z + 0.040),
                                 (MUFF_X + s * 0.050, YP - 0.026, MUFF_Z + 0.030)], 2), 0.0016, 4)
        parts += [rb, hk]
    return parts


# =============================================================================
# Fan on the shelf: the impeller is the bone ozl_work (the "working" loop)
# =============================================================================
def fan_axes():
    t, y = math.radians(FAN_TILT), math.radians(FAN_YAW)
    a = Vector((math.sin(y) * math.cos(t), -math.cos(y) * math.cos(t), -math.sin(t)))
    w = (Vector((0, 0, 1)) - a * a.z).normalized()
    pv = Vector((FAN_X, FAN_Y, ZP + FAN_PIVOT))
    return a, w, pv, pv + w * 0.05


def build_fan(spec):
    lod = spec["lod"]
    a, w, pv, c = fan_axes()
    side = a.cross(w).normalized()
    AXES["fan"] = (c, a)
    n = 16 if lod == 0 else 8
    fb = P("fan_body", "fan_body")
    # cast base, stand, a tilt hinge with a thumb screw, the motor housing
    base = [(0.0, 0.0), (0.075, 0.0), (0.076, 0.004), (0.074, 0.012), (0.064, 0.022), (0.042, 0.030), (0.016, 0.034),
            (0.0, 0.035)]
    q.lathe(fb, base if lod == 0 else [base[i] for i in (0, 1, 3, 5, 7)], n, (FAN_X, FAN_Y, ZP))
    q.rod(fb, (FAN_X, FAN_Y, ZP + 0.030), pv - Vector((0, 0, 0.010)), 0.009, 8 if lod == 0 else 5)
    q.lathe(fb, [(0.013, -0.016), (0.013, 0.016)], 10 if lod == 0 else 6, pv, side, cap0=True, cap1=True)
    q.rod(fb, pv, c - w * 0.040, 0.010, 8 if lod == 0 else 5)
    mot = [(0.0, -0.085), (0.022, -0.082), (0.036, -0.072), (0.044, -0.055), (0.046, -0.035), (0.045, -0.006),
           (0.040, 0.0), (0.014, 0.004), (0.0, 0.005)]
    q.lathe(fb, mot if lod == 0 else [mot[i] for i in (0, 2, 4, 5, 7, 8)], n, c, a)
    parts = [fb]
    if lod == 0:
        kb = P("fan_knobs", "grip_black")
        q.star_prism(kb, pv + side * 0.016, side, 0.012, 0.002, 4, 0.0, 0.010)                   # thumb screw
        ks = Vector((0, -1, 0.9)).normalized()
        q.star_prism(kb, Vector((FAN_X, FAN_Y - 0.052, ZP + 0.022)), ks, 0.011, 0.0012, 9, 0.0, 0.012)   # speed
        q.rod(kb, c - a * 0.070 + w * 0.034, c - a * 0.070 + w * 0.054, 0.006, 8)                 # oscillation button
        q.lathe(fb, [(0.040, -0.045), (0.0465, -0.044), (0.0465, -0.040), (0.040, -0.039)], n, c, a)   # rim
        parts.append(kb)
    if lod == 2:
        return parts
    # impeller: a cap hub and four soft blades (bone ozl_work)
    rt = P("fan_rotor", "fan_blade", group=SEL_FAN)
    hub = [(0.004, 0.004), (0.004, 0.018), (0.019, 0.018), (0.020, 0.030), (0.016, 0.040), (0.008, 0.045),
           (0.0, 0.046)]
    q.lathe(rt, hub if lod == 0 else [hub[i] for i in (0, 2, 3, 5, 6)], 12 if lod == 0 else 6, c, a)
    radii = [0.018, 0.045, 0.075, 0.097, 0.108, 0.113] if lod == 0 else [0.018, 0.08, 0.112]
    spans = [40.0, 52.0, 58.0, 54.0, 42.0, 20.0] if lod == 0 else [40.0, 58.0, 26.0]
    for k in range(4):
        q.blade(rt, c + a * 0.028, a, 20.0 + 90.0 * k, radii, spans, 24.0, 0.003)
    parts.append(rt)
    if lod == 0:
        cb = P("fan_cable", "cable")
        cable(cb, [Vector((FAN_X + 0.02, FAN_Y + 0.070, ZP + 0.006)), Vector((FAN_X + 0.05, FAN_Y + 0.11, ZP + 0.0035)),
                   Vector((FAN_X + 0.07, Y1 - 0.004, ZP + 0.0035)), Vector((FAN_X + 0.075, Y1 + 0.010, ZP - 0.02)),
                   Vector((FAN_X + 0.075, Y1 + 0.012, ZP - 0.25))], 0.003, lod)
        parts.append(cb)
    return parts


def build_lod(spec):
    parts = build_bench(spec) + build_slot1(spec) + build_mat(spec) + build_scopes(spec)
    parts += build_supps(spec) + build_rod(spec) + build_cans(spec) + build_table_bits(spec) + build_cases(spec)
    parts += build_lamp(spec) + build_board(spec) + build_fan(spec)
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
    # inside the table, and forward over the countertop (the lamp head is there); up to the top of the fan
    # on the shelf
    top = kx.box_pts(X0 - 0.01, X1 + 0.01, Y1 - 0.51, Y1, 0.40, ZP + 0.30)
    comps = [(table, metal), (top, metal)]
    c, a = AXES["fan"]
    memory = {
        "invView": [(-0.2, -2.6, 1.3)],
        "ce_center": [(0.0, 0.0, ZP / 2)],
        "ce_radius": [(1.1, 0.0, ZP / 2)],
        "ozl_work_axis": [tuple(c), tuple(c + a * 0.05)],
    }
    for i, m in enumerate(MODS):
        memory["module_%d" % (i + 1)] = [m]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2] + 0.004)
    return comps, 160.0, memory, bbox


# the first ones are for the --look preview: overall, the table with the modules in place (and the same
# empty), the lamp from below (the inside of the shade is visible - it glows when "working"), the mat
# with the sights, the sights close up, the shelf with the fan, the lamp; the "working" look uses the
# first three
SHOTS = [
    ("front", (-1.0, -2.4, 1.75), (0.0, 0.0, 1.0), 32),
    ("bench", (-0.05, -1.20, 1.62), (-0.02, -0.08, 0.84), 30),
    ("glow", (0.0, -0.78, 0.90), (-0.36, -0.06, 1.10), 30),
    ("mat", (0.02, -0.78, 1.18), (-0.06, -0.16, 0.81), 36),
    ("scopes", (0.02, -0.80, 1.10), (-0.13, -0.15, 0.85), 32),
    ("shelf", (-0.40, -0.90, 1.78), (-0.15, 0.18, 1.48), 36),
    ("lamp", (-0.98, -0.80, 1.42), (-0.55, 0.10, 1.10), 34),
    ("slot1", (-0.98, -0.95, 1.08), (-0.62, -0.26, 0.76), 40),
    ("cabinet", (0.35, -1.25, 0.75), (0.55, -0.2, 0.42), 34),
    ("right", (1.15, -1.0, 1.25), (0.55, 0.0, 0.85), 32),
    ("under", (-0.55, -1.5, 0.55), (-0.45, 0.0, 0.22), 32),
    ("back", (1.4, 1.9, 1.6), (0.0, 0.0, 0.9), 32),
]

M.look_shots = (7, 3)
M.run(build_lod, collision, SHOTS, row_step=1.9, row_shot=((1.9, -6.2, 2.0), (1.9, 0, 0.80)))
