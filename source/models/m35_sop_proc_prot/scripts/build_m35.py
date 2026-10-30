"""M35 - the SOP muffle furnace: the Protection Sample Analyzer (OZL_Sop_Proc_Prot). An
analyzer: cargo 4x4, no modules. The sample socket is a plate cooling on two fireclay
bricks.

    blender --background --python build_m35.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: make_decals.py with the system Python (scales, the regulator dial, a
sign, a stencil). Positions are in layout.py (shared with make_decals.py).

The device (card M35, a cabinet with the instrument on top): a laboratory muffle furnace,
still of Soviet make, on an olive cabinet, a control panel next to it; a plate cools on
bricks, tongs next to it. There is no Soviet floor furnace with passport dimensions in open
sources, so the furnace is a benchtop chamber furnace of the MP-2 class on a laboratory
cabinet:
- the furnace body 600 x 365 x 450 mm (L x W x H), chamber 400 x 250 x 160 (MP-2/1200;
  MP-2/1000 - 500 x 300 x 200), 60 kg, 380 V, 10-12 kW (a muffle furnace catalog); the look
  is the MP-2U (classified ads): a shell with rounded edges on skids, a front plate with
  rounded corners and an inner panel on screws, a heavy slab door on forks with a lever and
  a black ball, at the side a regulator box with a 0-10 scale, embossed louvres and a lamp;
  the lever and ball, the peephole, the thermometer and the exhaust hood follow the Heraeus
  KR 170 (Wikimedia Commons File: Muffle_furnace.jpg, CC BY-SA 3.0). The door 300 x 240 x 65
  follows the chamber with lining margins (an estimate);
- the cabinet 900 x 700, the worktop is a steel sheet at 0.80 (a lab cabinet is 0.75-0.90,
  like kfurn.lab_cabinet); a 10 mm asbestos-cement sheet under the furnace;
- the control panel 360 x 440 x 200 (an estimate from the panels of SNOL furnaces): a
  pyrometric millivoltmeter of the MPShchPr class (window 120 x 90, scale 0-1200 degrees,
  an estimate), an ammeter of the M4200 class 80 x 80 (the case as in M33), "mains" and
  "heating" lamps, a packet switch;
- a thermocouple in a porcelain sleeve dia 16 in the roof (a TKhA-0806 class - an
  estimate), an exhaust stub and a dia 80 pipe (galvanized) up to 1.53 and an elbow back
  toward the wall - the model height is 1.57 (the card says 1.6);
- fireclay brick ShA-5 250 x 123 x 65 (GOST 390-96); a plate 250 x 300 x 8 (a 10 x 12"
  armor plate - a steel insert, tempering colors after tempering); crucible tongs ~0.40
  (an estimate from photos).
The extent 0.90 x 1.57 x 0.83 m is within the card (0.9 x 1.6 x 0.8).

Look: "dayz" (matte, dirtier, colored AO); the cabinet, furnace and panel have rounded edges
and the small details of a real instrument (own builders here: cabinet - a cabinet after
kfurn.lab_cabinet with rounded fronts, hinges, a lock, frames for tags and round handles;
slab, bezel, lathe, fillet - slabs, frames, solids of revolution, smooth bends); the door
lever is a rod with smooth bends on forks with pins; the tongs are a round rod with
half-ring jaws and handle loops; the cables have glands. Vanilla proxy items (kvanilla): on
the panel a log (paper) and a pen, on the left side of the panel on hooks pliers, an
adjustable wrench and a screwdriver. While working (a loop, OZL_Work in the mod's
config.cpp): the "mains" lamp, the glow in the peephole and along the door gap are steady
(ozl_lamp), the "heating" lamps blink - the regulator switches the heater on and off
(ozl_lamp_2, blink), the pyrometer and ammeter needles sway around their working marks
(bones ozl_needle, ozl_needle_2 on their own sources, wobble).

SOP look (the build_worn builder is from M32/M33): the cabinet and the panel are olive,
heavily worn (edges, handles, fronts), primer under the paint, touched up in places, no
rust. The furnace is silver-grey heat-resistant paint (per the card) with soot above the
door, at the peephole and at the stub. Unreadable details: scales and a dial with digits, a
"hot surface" sign, an inventory number by stencil on the cabinet, blank nameplates on the
panel and tags on the drawers.

Machine look: ozl_lamp - the "mains" lamp of the panel, the peephole mica and the gap
around the door (the _on atlas, the _on rvmat with a glow; orange - the furnace is
burning); ozl_lamp_2 - the "heating" lamps of the panel and of the regulator box. The
needles are the bones ozl_needle (pyrometer) and ozl_needle_2 (ammeter): phase 0 - at zero,
1 - the scale end; while working the pyrometer is at 0.75 of the scale (900 degrees), the
ammeter at 0.60. LODs: the middle one has no small items (screws, louvres, nameplates,
tongs, hinges, hooks), the far one has the cabinet, furnace, pipe, panel, bricks with the
plate, no glass.

Blender axes: X - width, Y - depth (front at -Y), Z - up.
"""
import math
import os
import sys

from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import krender  # noqa: E402
import kvanilla as kv  # noqa: E402
import layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m (the rest is in layout.py)
# =============================================================================
X0, X1, Y0, Y1, TOP = L.X0, L.X1, L.Y0, L.Y1, L.TOP
FX0, FX1, FCX, FY0, FY1, FZ0, FZ1 = L.FX0, L.FX1, L.FCX, L.FY0, L.FY1, L.FZ0, L.FZ1
DW, DH, DT, DZ0 = L.DW, L.DH, L.DT, L.DZ0
HX0, HX1, HY0, HY1, HZ0, HZ1 = L.HX0, L.HX1, L.HY0, L.HY1, L.HZ0, L.HZ1
SX0, SX1, SY0, SY1, SZ0, SZ1 = L.SX0, L.SX1, L.SY0, L.SY1, L.SZ0, L.SZ1
YS = SY0 - 0.006                                             # face of the control panel
PANEL_Y = FY0 - L.FRONT_T                                    # face of the furnace front plate
INNER_T = 0.003                                              # inner panel on the front plate
DOOR_BACK = PANEL_Y - INNER_T                                # door against the inner panel
DOOR_FACE = DOOR_BACK - DT                                   # door face
ZP = DZ0 + DH * 0.5                                          # door fork axes
YPIN = DOOR_FACE + DT * 0.5
XFORK = (FCX - DW / 2 - 0.009, FCX + DW / 2 + 0.009)         # forks left and right of the door
KNOB = (FX0 - 0.060, FY0 - 0.115, DZ0 + 0.10)                # lever ball: forward and to the left
NEEDLE0 = L.needle_rest()
INNER = (FX0 + 0.012, FX1 - 0.012, FZ0 + 0.022, FZ1 - 0.095)  # inner panel: x0, x1, z0, z1
PEEP_R = 0.0118                                              # peephole mica (seen in a bronze bushing)
DUCT = dict(gland_tc=(SX1 - 0.05, 0.23), gland_side=(0.24, TOP + 0.060))   # panel glands: top, right
HOUSE_GL = ((HX0 + 0.022, HZ0 + 0.05), (HX1 - 0.024, HZ0 + 0.05))         # box glands at the back (x, z)
TONGS = (-0.44, -0.325)                                      # tongs at the worktop edge, jaws to the left

LOD_SPECS = [
    dict(lod=0, sides=12),
    dict(lod=1, sides=8),
    dict(lod=2, sides=6),
]

REGIONS = {
    "cab": ("olive_cab", 0.7), "cab_front": ("olive_front", 0.8), "worktop": ("worktop", 0.8),
    "plinth": ("black", 0.5), "handle": ("chrome", 1.4), "asb": ("asbestos", 0.8), "card": ("card", 2.0),
    "f_body": ("heat_body", 0.8), "f_front": ("heat_front", 1.0), "f_door": ("heat_door", 1.2),
    "f_house": ("heat_house", 1.2), "f_feet": ("black", 0.8), "lever": ("lever", 1.6), "ball": ("bakelite", 1.6),
    "slot": ("bore", 1.0), "rivet": ("heat_body", 2.0), "dial": ("dial", 4.0), "gap": ("gap", 1.0),
    "exhaust": ("galv", 0.8), "clamp": ("galv_dark", 1.2), "sheath": ("porcelain", 2.0), "tc_head": ("alu", 2.0),
    "sh_box": ("olive_box", 0.8), "sh_face": ("olive_panel", 1.2), "black": ("bakelite", 1.6),
    "chrome": ("chrome", 1.6), "face_t": ("face_t", 5.0), "face_a": ("face_a", 5.0), "needle": ("needle", 2.0),
    "tag": ("tag", 2.5), "lamp_g": ("lamp_g", 1.6), "lamp_r": ("lamp_r", 1.6), "peep": ("peep", 3.0),
    "brick": ("brick", 1.0), "plate": ("plate", 1.6), "tongs": ("tongs", 1.6), "cable": ("cable", 1.0),
}

# =============================================================================
# Materials
# =============================================================================


def build_worn(mat, origin, color, bare=kmats.lin((104, 104, 106)), primer=kmats.lin((96, 46, 34)), seed=1.0,
               gloss=0.28, spec=0.22, wear=(0.68, 0.73), edge_k=0.75, rub=(), touch=0.0, scratch=0.0, soot=(),
               floor_z=0.0, dust=0.2, grime=0.3, decal_items=()):
    """SOP olive - the builder of M32/M33: old army paint, worn off on the edges (edge_k) and
    where hands grab (rub - [(center, half-axes, strength)]), primer under it, bare metal in
    the middle of a spot; touch - touch-up patches. No rust. New in M35: soot - [(center,
    half-axes, strength)] - soot (darker and matte, in patches), for the furnace.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket

    def near(c, r):
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
        return t.maprange(ln.outputs["Value"], 0.25, 1.0, 1.0, 0.0)

    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.88 for c in color[:3]) + (1,), color)
    base = t.mixc(t.math("MULTIPLY", t.maprange(t.noise(vec, 0.9, 4.0, 0.5), 0.45, 0.75, 0.0, 1.0), 0.35), base,
                  tuple(min(1.0, c * 1.25 + 0.01) for c in color[:3]) + (1,))
    col = kmats.decals(t, base, sep, nsep, decal_items)
    edge = t.maprange(t.edge_wear(0.004), 0.05, 0.22, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 11.0, 10.0, 0.7), 0.75), t.math("MULTIPLY", edge, edge_k))
    grain = t.maprange(t.noise(vec, 34.0, 8.0, 0.7), 0.3, 0.7, 0.55, 1.0)
    for c, r, k in rub:
        f = t.math("ADD", f, t.math("MULTIPLY", t.math("MULTIPLY", near(c, r), grain), k))
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
    if soot:
        # soot: a soft spot at the source, a ragged edge by noise, it stretches farther upward
        sm = None
        cloud = t.maprange(t.noise(vec, 6.0, 8.0, 0.65), 0.3, 0.7, 0.35, 1.0)
        for c, r, k in soot:
            s1 = t.math("MULTIPLY", t.math("MULTIPLY", near(c, r), cloud), k)
            sm = s1 if sm is None else t.math("MAXIMUM", sm, s1)
        sm = t.math("MINIMUM", sm, 1.0)
        col = t.mixc(t.math("MULTIPLY", sm, 0.92), col, kmats.lin((20, 19, 18)))
        g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", sm, gloss * 0.8))
        s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", sm, spec * 0.8))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g_, s_, h)


def build_plate(mat, origin, center, radius, seed=8.0):
    """Steel plate after tempering: tempering colors in rings from the middle (blue, violet,
    straw) to the grey edge, scale in patches, lighter edges.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    d = t.node("ShaderNodeVectorMath")
    d.operation = "SUBTRACT"
    t.link(pos, d.inputs[0])
    d.inputs[1].default_value = center
    q = t.node("ShaderNodeVectorMath")
    q.operation = "DIVIDE"
    t.link(d.outputs[0], q.inputs[0])
    q.inputs[1].default_value = radius
    ln = t.node("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    t.link(q.outputs[0], ln.inputs[0])
    r = t.math("ADD", ln.outputs["Value"], t.math("MULTIPLY", t.math("SUBTRACT", t.noise(vec, 4.0, 6.0, 0.65), 0.5), 0.6))
    col = t.ramp(r, [(0.0, kmats.lin((58, 60, 70))), (0.25, kmats.lin((66, 76, 104))), (0.42, kmats.lin((92, 78, 102))),
                     (0.58, kmats.lin((132, 110, 76))), (0.76, kmats.lin((146, 128, 94))), (0.95, kmats.lin((106, 106, 108)))])
    scale = t.step(t.noise(vec, 18.0, 8.0, 0.7), 0.62, 0.70)
    col = t.mixc(t.math("MULTIPLY", scale, 0.7), col, kmats.lin((34, 32, 32)))
    edge = t.maprange(t.edge_wear(0.002), 0.05, 0.25, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.6), col, kmats.lin((150, 150, 152)))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, TOP, 0.05, 0.1)
    g_ = t.math("SUBTRACT", 0.5, t.math("MULTIPLY", scale, 0.35))
    return kmats.out(t, col, g_, t.math("SUBTRACT", 0.55, t.math("MULTIPLY", scale, 0.4)),
                     t.math("MULTIPLY", scale, 0.15))


def build_brick(mat, origin, color, seed=9.0, floor_z=0.0, dust=0.2, grime=0.5):
    """ShA fireclay brick: blotchy tone, dark chamotte grains, chips on the edges lighter (a fresh
    break), scorch marks from hot plates on top, dust and grime.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    col = t.mixc(t.maprange(t.noise(vec, 3.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                 tuple(c * 0.82 for c in color[:3]) + (1,), tuple(min(1.0, c * 1.08) for c in color[:3]) + (1,))
    grog = t.step(t.noise(vec, 150.0, 2.0, 0.5), 0.66, 0.69)
    col = t.mixc(t.math("MULTIPLY", grog, 0.75), col, kmats.lin((92, 70, 48)))
    edge = t.maprange(t.edge_wear(0.005), 0.05, 0.25, 0.0, 1.0)
    chip = t.step(t.math("ADD", t.math("MULTIPLY", t.noise(vec, 14.0, 8.0, 0.7), 0.7), t.math("MULTIPLY", edge, 0.6)),
                  0.64, 0.70)
    col = t.mixc(t.math("MULTIPLY", chip, 0.55), col, tuple(min(1.0, c * 1.22 + 0.02) for c in color[:3]) + (1,))
    up = t.maprange(nsep.outputs["Z"], 0.5, 0.9, 0.0, 1.0)
    burn = t.math("MULTIPLY", up, t.maprange(t.noise(vec, 5.0, 6.0, 0.6), 0.35, 0.65, 0.15, 0.75))
    col = t.mixc(burn, col, kmats.lin((46, 38, 30)))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    return kmats.out(t, col, 0.06, 0.04, t.math("MULTIPLY", chip, -0.4))


def wdecal(name):
    return os.path.join(WORK, name)


METER_DECALS = {m["scale"]: [(wdecal("decal_meter_%s.png" % m["scale"]), "y", -1, ("x", "z"),
                              (m["x"], m["z"] + m["h"] / 2), (m["w"], m["h"]), (YS - 0.004, YS + 0.001))]
                for m in L.METERS}
_hs = L.HEAT_SIGN
FRONT_DECALS = [(wdecal("decal_heat.png"), "y", -1, ("x", "z"), (_hs["x"], _hs["z"]), (_hs["s"], _hs["s"]),
                 (PANEL_Y - 0.003, PANEL_Y + 0.002))]
DIAL_DECALS = [(wdecal("decal_dial.png"), "x", 1, ("y", "z"), (L.DIAL["y"], L.DIAL["z"]),
                (-2 * L.DIAL["r"], 2 * L.DIAL["r"]), (HX1 - 0.001, HX1 + 0.006))]
_st = L.STENCIL
STENCIL_DECALS = [(wdecal("decal_stencil.png"), "y", -1, ("x", "z"), (_st["x"], _st["z"]), (_st["w"], _st["h"]),
                   (L.DOOR_Y - 0.004, L.DOOR_Y + 0.002))]

OLIVE = kmats.lin((80, 86, 56))                              # M32/M33 olive
SILVER = kmats.lin((140, 142, 137))                          # silver heat-resistant paint
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# soot: above the door (stretching up the plate), at the peephole, at the stub on the roof
SOOT_FRONT = [((FCX, FY0, DZ0 + DH + 0.02), (0.16, 0.1, 0.07), 1.0), ((FCX, FY0, FZ1 - 0.02), (0.10, 0.1, 0.06), 0.6)]
SOOT_DOOR = [((FCX, DOOR_FACE, DZ0 + DH), (0.15, 0.1, 0.05), 0.9), ((L.PEEP["x"], DOOR_FACE, L.PEEP["z"]),
                                                                    (0.04, 0.05, 0.04), 0.8)]
SOOT_BODY = [((L.EXH["x"], L.EXH["y"], FZ1), (0.09, 0.09, 0.03), 0.9), ((FCX, FY0, DZ0 + DH + 0.05), (0.16, 0.06, 0.08), 0.7)]
OLV = dict(color=OLIVE, seed=2.1, touch=0.35, scratch=0.45, edge_k=0.9, floor_z=0.0, dust=0.2, grime=0.42)
HEAT = dict(color=SILVER, bare=kmats.lin((130, 130, 132)), primer=kmats.lin((70, 70, 70)), gloss=0.30, spec=0.30,
            edge_k=0.8, scratch=0.3, floor_z=TOP, dust=0.36, grime=0.45)
# where hands grab: the cabinet door and drawers, the front worktop edge, the panel door
CAB_RUB = [((X0 + 0.40, Y0, 0.66), (0.06, 0.04, 0.10), 0.35), ((0.225, Y0, 0.70), (0.12, 0.04, 0.05), 0.25),
           ((0.225, Y0, 0.50), (0.12, 0.04, 0.05), 0.2), ((0.0, Y0, TOP), (0.45, 0.05, 0.03), 0.3),
           ((0.0, Y0, 0.12), (0.46, 0.05, 0.07), 0.22)]                    # scuffed by feet
# furnace: the bottom of the opening and the door - plates are pushed in and pulled out with
# tongs; by the left fork - a hand on the lever
FRONT_RUB = [((FCX, PANEL_Y, DZ0 - 0.012), (0.17, 0.05, 0.025), 0.35), ((XFORK[0], PANEL_Y, ZP), (0.035, 0.05, 0.05), 0.4)]
DOOR_RUB = [((FCX, DOOR_FACE, DZ0 + 0.012), (0.16, 0.05, 0.03), 0.35)]

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "olive_cab": (build_worn, dict(OLV, rub=CAB_RUB)),
    "olive_front": (build_worn, dict(OLV, seed=2.4, wear=(0.66, 0.71), rub=CAB_RUB, decal_items=STENCIL_DECALS)),
    "olive_box": (build_worn, dict(OLV, seed=2.7, wear=(0.67, 0.72), floor_z=TOP, dust=0.35)),
    "olive_panel": (build_worn, dict(OLV, seed=3.0, wear=(0.68, 0.73), edge_k=0.9, floor_z=TOP,
                                     rub=[((SX1 - 0.085, YS, SZ0 + 0.11), (0.05, 0.03, 0.05), 0.4)])),
    "worktop": (build_worn, dict(color=kmats.lin((70, 72, 66)), bare=kmats.lin((120, 120, 122)),
                                 primer=kmats.lin((60, 58, 54)), seed=3.3, wear=(0.58, 0.64), edge_k=1.1, scratch=0.8,
                                 soot=[((FCX, -0.32, TOP), (0.22, 0.06, 0.02), 0.5)], floor_z=TOP, dust=0.25, grime=0.4)),
    "asbestos": ("plastic", dict(color=kmats.lin((148, 146, 136)), gloss=0.08, spec=0.05, mottle=0.15, dust=0.4,
                                 grime=0.8, scuff=(0.6, 0.7))),
    "heat_body": (build_worn, dict(HEAT, seed=4.2, wear=(0.67, 0.72), soot=SOOT_BODY)),
    "heat_front": (build_worn, dict(HEAT, seed=4.5, wear=(0.66, 0.71), edge_k=0.9, soot=SOOT_FRONT, rub=FRONT_RUB,
                                    decal_items=FRONT_DECALS)),
    "heat_door": (build_worn, dict(HEAT, seed=4.8, wear=(0.62, 0.68), edge_k=1.0, scratch=0.5, soot=SOOT_DOOR,
                                   rub=DOOR_RUB)),
    "heat_house": (build_worn, dict(HEAT, seed=5.1, wear=(0.67, 0.72), decal_items=DIAL_DECALS)),
    "dial": ("paint", dict(CLEAN, color=kmats.lin((150, 146, 136)), gloss=0.5, spec=0.5, decal_items=DIAL_DECALS)),
    "lever": ("steel", dict(seed=5.4, tone=0.34, along="y", gloss=0.55, spec=0.65, dust=0.15, grime=0.35)),
    "bakelite": ("plastic", dict(color=kmats.lin((22, 21, 20)), gloss=0.55, spec=0.4, dust=0.15, scuff=(0.66, 0.74))),
    "bore": ("plastic", dict(color=kmats.lin((14, 14, 14)), gloss=0.1, spec=0.05, dust=0.1)),
    "galv": ("steel", dict(seed=5.7, tone=0.37, along="z", gloss=0.35, spec=0.45, dust=0.4, grime=0.45)),
    "galv_dark": ("steel", dict(seed=6.0, tone=0.30, along="x", gloss=0.4, spec=0.5, dust=0.3, grime=0.4)),
    "porcelain": ("plastic", dict(color=kmats.lin((222, 218, 204)), gloss=0.6, spec=0.5, mottle=0.08, dust=0.3,
                                  grime=0.4)),
    "alu": ("steel", dict(seed=6.3, tone=0.46, along="z", gloss=0.4, spec=0.5, dust=0.3, grime=0.3)),
    "chrome": ("steel", dict(seed=6.6, tone=0.40, along="z", gloss=0.75, spec=0.85, dust=0.1, grime=0.25)),
    "face_t": ("paint", dict(CLEAN, color=kmats.lin((228, 226, 214)), gloss=0.5, spec=0.4, decal_items=METER_DECALS["t"])),
    "face_a": ("paint", dict(CLEAN, color=kmats.lin((228, 226, 214)), gloss=0.5, spec=0.4, decal_items=METER_DECALS["a"])),
    "needle": ("flat", dict(color=kmats.lin((18, 18, 18)), gloss=0.5, spec=0.4)),
    "tag": ("steel", dict(seed=7.2, tone=0.52, along="x", gloss=0.5, spec=0.6, dust=0.1, grime=0.2)),
    # tag in the drawer frame: cardboard without text, faded and greasy
    "card": ("plastic", dict(color=kmats.lin((196, 188, 160)), gloss=0.08, spec=0.05, mottle=0.2, dust=0.3,
                             grime=0.5, scuff=(0.6, 0.7))),
    "lamp_g": ("flat", dict(color=kmats.lin((30, 70, 36)), gloss=0.85, spec=0.8)),
    "lamp_g_on": ("flat", dict(color=kmats.lin((120, 255, 120)), gloss=0.85, spec=0.8)),
    "lamp_r": ("flat", dict(color=kmats.lin((90, 22, 18)), gloss=0.85, spec=0.8)),
    "lamp_r_on": ("flat", dict(color=kmats.lin((255, 80, 56)), gloss=0.85, spec=0.8)),
    # door peephole: mica, dark at rest, orange chamber glow while working
    "peep": ("flat", dict(color=kmats.lin((46, 36, 26)), gloss=0.7, spec=0.6)),
    "peep_on": ("flat", dict(color=kmats.lin((255, 140, 40)), gloss=0.7, spec=0.6)),
    # gap around the door: soot on the seal, glow along the gap while working
    "gap": ("flat", dict(color=kmats.lin((26, 23, 20)), gloss=0.1, spec=0.05)),
    "gap_on": ("flat", dict(color=kmats.lin((255, 112, 30)), gloss=0.1, spec=0.05)),
    "brick": (build_brick, dict(color=kmats.lin((174, 146, 108)), floor_z=TOP, dust=0.25, grime=0.8)),
    "plate": (build_plate, dict(center=(L.PLATE["x"], L.PLATE["y"], TOP + 0.07), radius=(0.20, 0.22, 1.0))),
    "tongs": ("steel", dict(seed=7.8, tone=0.22, along="x", gloss=0.4, spec=0.5, dust=0.1, grime=0.6)),
    "cable": ("plastic", dict(color=kmats.lin((26, 27, 25)), gloss=0.3, spec=0.2, dust=0.35)),
})

OBJ, NAME = "m35_sop_proc_prot", "ozr_sop_proc_prot"
SEL_LAMP, SEL_LAMP2 = "ozl_lamp", "ozl_lamp_2"
BONES = [m["bone"] for m in L.METERS]
ON = dict(remap={"lamp_g": "lamp_g_on", "lamp_r": "lamp_r_on", "peep": "peep_on", "gap": "gap_on"},
          emissive=(1.0, 1.0, 1.0, 1.0))
# needles: the source phase 0..1 is the whole scale (ARC_DEG); while working OZL_WorkFx sways the
# source (wobble)
WORK_ANIMS = tuple(("%s_rot" % m["bone"], dict(type="rotation", source=m["bone"], selection=m["bone"],
                                               axis=m["bone"] + "_axis", memory=1, minValue=0.0, maxValue=1.0,
                                               angle0=0.0, angle1=math.radians(L.ARC_DEG)))
                   for m in L.METERS)
# Vanilla DayZ items: a log and a pen on the panel, tools on the hooks of the panel's left side
SIDE = (-1.0, 0.0, 0.0)
HUNG = [("pliers", 0.140), ("wrench", 0.205), ("screwdriver", 0.265)]   # key, center y; hang jaws down
HOOK_Z = SZ1 - 0.05


def _hung(key, y):
    """Hangs on a hook: the hook goes into the top of the item by 12 mm (between the handles, into
    the wrench hole).
    """
    lo, hi = kv.box(key)
    zc = HOOK_Z + 0.012 - (hi[1] - lo[1]) / 2
    return kv.put(key, (SX0, y, zc), up=(0.0, 0.0, -1.0), fwd=SIDE, normal=SIDE)


def hook_len(key):
    lo, hi = kv.box(key)
    return min(0.030, (hi[2] - lo[2]) * 0.7 + 0.006)


DECOR = [kv.put("paper", (-0.285, 0.200, SZ1), **kv.flat(2)),
         kv.put("pen", (-0.215, 0.165, SZ1 + 0.0003), **kv.flat(38))] + [_hung(k, y) for k, y in HUNG]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.84, 0.86, 0.86), clear=0.04, edge=0.12, smudge=0.10, streaks=0.04),
                 selections=(SEL_LAMP, SEL_LAMP2) + tuple(BONES), hidden=(SEL_LAMP, SEL_LAMP2), states={"on": ON},
                 bones=tuple((b, "") for b in BONES), animations=WORK_ANIMS, decor=DECOR,
                 sources={b: dict(animPeriod=0.2) for b in BONES})
P = M.part
BOUNDS = {}
AXES = {}

# =============================================================================
# Own primitives (the kit is left alone): slabs with rounded corners, frames, solids of revolution,
# bends
# =============================================================================
XA, YA, ZA = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))


def bev(lod, r=0.003, seg=1):
    return dict(r=r, seg=seg) if lod == 0 else {}


def front_frame(o):
    """A plane facing the person (-y): a - x, b - z, c - forward (-y)."""
    return g.Frame(o, XA, ZA, -YA)


def ax_frame(o, axis):
    """Frame for a solid of revolution: u is the axis, v and n are across."""
    u = Vector(axis).normalized()
    v = u.cross(ZA if abs(u.z) < 0.9 else XA).normalized()
    return g.Frame(o, u, v, u.cross(v))


def rrect(w, h, r, nc):
    """Rounded rectangle w x h centered at 0 (counterclockwise, from the upper right corner)."""
    if nc <= 0:
        return [(w / 2, h / 2), (-w / 2, h / 2), (-w / 2, -h / 2), (w / 2, -h / 2)]
    r = max(2e-4, min(r, w / 2 - 1e-5, h / 2 - 1e-5))
    pts = []
    for cx, cz, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180),
                       (w / 2 - r, -h / 2 + r, 270)):
        for k in range(nc + 1):
            a = math.radians(a0 + 90.0 * k / nc)
            pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def _bands(part, rings, closed_caps=(True, True)):
    bm = part.bm
    new = []
    n = len(rings[0])
    for i in range(len(rings) - 1):
        for k in range(n):
            j = (k + 1) % n
            new.append(bm.faces.new([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]))
    if closed_caps[1]:
        new.append(bm.faces.new(rings[-1]))
    if closed_caps[0]:
        new.append(bm.faces.new(rings[0][::-1]))
    import bmesh
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def slab(part, fr, w, h, r, t, bev=0.0, nc=3, nb=2):
    """Slab w x h with rounded corners r in the (u, v) plane of frame fr: the back at c = 0, the
    face at c = t; the front edge is rounded with radius bev in nb steps.
    """
    prof = [(0.0, 0.0)]
    if bev > 0 and nb > 0:
        prof.append((0.0, t - bev))
        for k in range(1, nb + 1):
            a = math.pi / 2 * k / nb
            prof.append((bev * (1 - math.cos(a)), t - bev + bev * math.sin(a)))
    else:
        prof.append((0.0, t))
    rings = [[part.bm.verts.new(fr.p(a, b, c)) for a, b in rrect(w - 2 * ins, h - 2 * ins, r - ins, nc)]
             for ins, c in prof]
    return _bands(part, rings)


def bezel(part, fr, wo, ho, ro, wi, hi, ci=(0.0, 0.0), t=0.01, bev=0.0, nc=2):
    """Frame: outside a rounded rectangle wo x ho, a window wi x hi with the center shifted by ci,
    thickness t (the back at c = 0); the outer front edge is a chamfer bev.
    """
    bm = part.bm

    def ring(w, h, r, c, off=(0.0, 0.0)):
        return [bm.verts.new(fr.p(a + off[0], b + off[1], c)) for a, b in rrect(w, h, r, nc)]
    seq = [ring(wo, ho, ro, 0.0)]
    if bev > 0:
        seq.append(ring(wo, ho, ro, t - bev))
        seq.append(ring(wo - 2 * bev, ho - 2 * bev, ro - bev, t))
    else:
        seq.append(ring(wo, ho, ro, t))
    seq += [ring(wi, hi, 0.0015, t, ci), ring(wi, hi, 0.0015, 0.0, ci)]
    seq.append(seq[0])
    new = []
    n = len(seq[0])
    for i in range(len(seq) - 1):
        for k in range(n):
            j = (k + 1) % n
            new.append(bm.faces.new([seq[i][k], seq[i][j], seq[i + 1][j], seq[i + 1][k]]))
    import bmesh
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def lathe(part, prof, sides, fr, a0=0.0):
    """Solid of revolution around the u axis of frame fr: prof [(r, h)] - the silhouette bottom to
    top along the axis, traversed on the outside (the right side of the traversal looks
    outward: the bottom down, the side outward, the top up, a hole wall toward the axis).
    r = 0 is a point on the axis.
    """
    bm = part.bm
    rings = []
    for r, h in prof:
        if r < 1e-7:
            rings.append([bm.verts.new(fr.p(h, 0.0, 0.0))])
        else:
            rings.append([bm.verts.new(fr.p(h, r * math.cos(a0 + 2 * math.pi * k / sides),
                                            r * math.sin(a0 + 2 * math.pi * k / sides))) for k in range(sides)])
    new = []
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        nr, nh = h1 - h0, -(r1 - r0)
        A, B = rings[i], rings[i + 1]
        if len(A) == 1 and len(B) == 1:
            continue
        for k in range(sides):
            j = (k + 1) % sides
            am = a0 + 2 * math.pi * (k + 0.5) / sides
            want = (fr.v * math.cos(am) + fr.n * math.sin(am)) * nr + fr.u * nh
            if len(A) == 1:
                vs = [A[0], B[k], B[j]]
            elif len(B) == 1:
                vs = [A[k], A[j], B[0]]
            else:
                vs = [A[k], A[j], B[j], B[k]]
            f = bm.faces.new(vs)
            f.normal_update()
            if f.normal.dot(want) < 0:
                f.normal_flip()
            new.append(f)
    bm.normal_update()
    return part.tag(new)


def sphere_prof(r, n):
    return [(r * math.sin(math.pi * k / n), -r * math.cos(math.pi * k / n)) for k in range(n + 1)]


def fillet(pts, rad, nseg=3):
    """Polyline -> smooth: each inner corner is an arc (a quadratic curve) of radius ~rad."""
    v = [Vector(p) for p in pts]
    out = [v[0]]
    for i in range(1, len(v) - 1):
        a, p, b = v[i - 1], v[i], v[i + 1]
        d1, d2 = (a - p), (b - p)
        l1, l2 = d1.length, d2.length
        if l1 < 1e-6 or l2 < 1e-6:
            continue
        d1.normalize()
        d2.normalize()
        ang = d1.angle(d2)
        if ang > math.pi - 1e-3:
            out.append(p)
            continue
        td = min(rad / max(math.tan(ang / 2), 1e-3), 0.45 * l1, 0.45 * l2)
        t1, t2 = p + d1 * td, p + d2 * td
        for k in range(nseg + 1):
            s = k / nseg
            out.append((1 - s) ** 2 * t1 + 2 * (1 - s) * s * p + s * s * t2)
    out.append(v[-1])
    return [tuple(q) for q in out]


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, from M24/M33)."""
    v = [Vector(p) for p in pts]
    if k <= 1:
        return [tuple(q) for q in v]
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


def screw(part, c, axis, r=0.0045, h=0.0022, sides=6):
    """Screw with a half-round head on a face (axis points outward), the base slightly sunk."""
    o = Vector(c) - Vector(axis).normalized() * 0.0003
    lathe(part, [(r, 0.0), (r * 0.78, h * 0.65), (0.0, h)], sides, ax_frame(o, axis))


def hood_louver(part, x_face, sx, y, z0, z1, w=0.012, dep=0.0045):
    """Embossed louvre on the face x = x_face (sx = +-1 - outward): a bump along z, open to the
    back (+y), dark in the open slot.
    """
    poly = [(x_face - sx * 0.0005, y - w / 2), (x_face + sx * dep * 0.6, y - w * 0.15),
            (x_face + sx * dep, y + w * 0.35), (x_face - sx * 0.0005, y + w / 2)]
    fs = g.prism(part, poly, (0, 1), z0, z1)
    slot = part.region_index("slot", "bore", 1.0)
    for f in fs:
        f.normal_update()
        if f.normal.y > 0.6:
            f[part.reg] = slot


def quad_y(part, x0, x1, z0, z1, y):
    """A single face looking toward -y (far LOD)."""
    return g.quad(part, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)])


def yaw_frame(o, deg):
    a = math.radians(deg)
    return g.Frame(o, (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))


# =============================================================================
# Cabinet (after kfurn.lab_cabinet - the same places of the fronts) and the asbestos-cement sheet
# =============================================================================
def build_cabinet(spec):
    lod = spec["lod"]
    t_top, plinth_h, inset, gap, t = 0.03, 0.08, 0.04, 0.004, 0.018
    parts = []
    body = P("cab_body", "cab")
    g.box(body, X0, X1, Y0 + 0.02, Y1, plinth_h if lod < 2 else 0.0, TOP - t_top, **bev(lod, 0.006, 2))
    parts.append(body)
    wt = P("cab_top", "worktop")
    g.box(wt, X0 - 0.01, X1 + 0.01, Y0 - 0.005, Y1 + 0.005, TOP - t_top, TOP,
          **(dict(r=0.008, seg=2) if lod == 0 else dict(r=0.004, seg=1) if lod == 1 else {}))
    parts.append(wt)
    if lod < 2:
        pl = P("cab_plinth", "plinth")
        g.box(pl, X0 + inset, X1 - inset, Y0 + inset, Y1 - inset, 0.0, plinth_h + 0.002)
        parts.append(pl)
    z_lo, z_hi = plinth_h + gap, TOP - t_top - gap
    yb = Y0 + 0.02                                            # front backs; face is yb - t (L.DOOR_Y)
    yf = yb - t
    fr = P("cab_fronts", "cab_front")
    if lod == 2:
        g.box(fr, X0 + gap, X1 - gap, yf, yb, z_lo, z_hi)
        parts.append(fr)
    else:
        hd = P("cab_handles", "handle") if lod == 0 else None
        hw = P("cab_hw", "chrome") if lod == 0 else None
        tg = P("cab_cards", "tag") if lod == 0 else None
        cd = P("cab_card", "card") if lod == 0 else None
        kh = P("cab_keyhole", "slot") if lod == 0 else None
        w = (X1 - X0 - gap) / 2
        # a door on the left, three drawers on the right (1 : 1 : 1.3 from top to bottom)
        cols = [(X0 + gap, X0 + gap + w - gap, [1.0], "door"), (X0 + gap + w, X1 - gap, [1.0, 1.0, 1.3], "drawer")]
        for xa, xb, heights, kind in cols:
            za = z_hi
            hs = sum(heights)
            for h in heights:
                zb = za - (z_hi - z_lo) * h / hs
                z0, z1 = zb + gap / 2, za - gap / 2
                cx, cz = (xa + xb) / 2, (z0 + z1) / 2
                if lod == 0:
                    slab(fr, front_frame((cx, yb, cz)), xb - xa, z1 - z0, 0.007, t, bev=0.004, nc=2, nb=1)
                else:
                    g.box(fr, xa, xb, yf, yb, z0, z1)
                if hd is not None:
                    if kind == "drawer":
                        hx, hz = cx, za - 0.045
                        pts = [(hx - 0.06, yf + 0.002, hz), (hx - 0.06, yf - 0.026, hz), (hx + 0.06, yf - 0.026, hz),
                               (hx + 0.06, yf + 0.002, hz)]
                        for s in (-1, 1):
                            g.cyl(hw, (hx + s * 0.06, yf - 0.002, hz), "y", 0.008, 0.004, 6)        # handle socket
                        # frame for a tag under the handle and a tag without text
                        bx, bz = hx, hz - 0.050
                        g.box(cd, bx - 0.033, bx + 0.033, yf - 0.0008, yf + 0.0005, bz - 0.0125, bz + 0.0125)
                        g.box(tg, bx - 0.037, bx + 0.037, yf - 0.0022, yf, bz - 0.0165, bz - 0.0125)
                        for s in (-1, 1):
                            g.box(tg, bx + s * 0.035 - 0.002, bx + s * 0.035 + 0.002, yf - 0.0022, yf, bz - 0.0125,
                                  bz + 0.0145)
                    else:
                        hx, hz = xb - 0.05, za - 0.12
                        pts = [(hx, yf + 0.002, hz + 0.06), (hx, yf - 0.026, hz + 0.06), (hx, yf - 0.026, hz - 0.06),
                               (hx, yf + 0.002, hz - 0.06)]
                        for s in (-1, 1):
                            g.cyl(hw, (hx, yf - 0.002, hz + s * 0.06), "y", 0.008, 0.004, 6)
                        # keyed lock under the handle, hinges on the left
                        g.cyl(hw, (hx, yf - 0.0015, hz - 0.10), "y", 0.011, 0.003, 12)
                        g.box(kh, hx - 0.0016, hx + 0.0016, yf - 0.0032, yf - 0.0028, hz - 0.108, hz - 0.096)
                        for zc in (z1 - 0.085, z0 + 0.085):
                            g.cyl(hw, (xa - 0.0015, yf + 0.004, zc), "z", 0.0055, 0.050, 8)
                    g.pipe(hd, fillet(pts, 0.010, 2), 0.0045, 6)
                za = zb
        parts.append(fr)
        if lod == 0:
            parts += [hd, hw, tg, cd, kh]
    asb = P("asbestos", "asb")
    g.box(asb, FX0 - 0.03, HX1 + 0.015, FY0 - 0.04, FY1 + 0.015, TOP, TOP + L.ASB_T, **bev(lod, 0.002))
    parts.append(asb)
    return parts


# =============================================================================
# Furnace: shell, front plate with an inner panel, door on forks with a lever, regulator box
# =============================================================================
def build_furnace(spec):
    lod = spec["lod"]
    n = 12 if lod == 0 else 8 if lod == 1 else 6
    parts = []
    bd = P("furnace_body", "f_body")
    g.box(bd, FX0, FX1, FY0, FY1, FZ0, FZ1, **({0: dict(r=0.03, seg=2), 1: dict(r=0.03, seg=1)}.get(lod, {})))
    parts.append(bd)
    fz = (FZ0 + FZ1) / 2
    fr = P("furnace_front", "f_front")
    if lod == 2:
        g.box(fr, FX0 - 0.004, FX1 + 0.004, PANEL_Y, FY0 + 0.004, FZ0 - 0.004, FZ1 + 0.004)
    else:
        slab(fr, front_frame((FCX, FY0 + 0.004, fz)), FX1 - FX0 + 0.008, FZ1 - FZ0 + 0.008, 0.030,
             L.FRONT_T + 0.004, bev=0.004, nc=4 if lod == 0 else 2, nb=1)
        x0, x1, z0, z1 = INNER
        slab(fr, front_frame(((x0 + x1) / 2, PANEL_Y + 0.0003, (z0 + z1) / 2)), x1 - x0, z1 - z0, 0.012,
             INNER_T + 0.0003, bev=0.0015 if lod == 0 else 0.0, nc=3 if lod == 0 else 1, nb=1)
    parts.append(fr)
    dr = P("furnace_door", "f_door")
    if lod == 2:
        g.box(dr, FCX - DW / 2, FCX + DW / 2, DOOR_FACE, DOOR_BACK, DZ0, DZ0 + DH)
    else:
        slab(dr, front_frame((FCX, DOOR_BACK, DZ0 + DH / 2)), DW, DH, 0.016, DT, bev=0.010 if lod == 0 else 0.006,
             nc=4 if lod == 0 else 2, nb=2 if lod == 0 else 1)
    parts.append(dr)
    hs = P("furnace_house", "f_house")
    g.box(hs, HX0 - 0.004, HX1, HY0, HY1, HZ0, HZ1,
          **({0: dict(r=0.016, seg=2), 1: dict(r=0.016, seg=1)}.get(lod, {})))
    parts.append(hs)
    # gap around the door (ozl_lamp: glow along the gap while working)
    if lod < 2:
        gp = P("door_gap", "gap", group=SEL_LAMP)
        bezel(gp, front_frame((FCX, DOOR_BACK + 0.0002, DZ0 + DH / 2)), DW + 0.006, DH + 0.006, 0.019,
              DW - 0.012, DH - 0.012, t=0.0034, nc=2 if lod == 0 else 1)
        parts.append(gp)
    # door peephole: mica (ozl_lamp) in a bushing
    pp = L.PEEP
    pe = P("peep", "peep", group=SEL_LAMP)
    if lod == 2:
        quad_y(pe, pp["x"] - PEEP_R, pp["x"] + PEEP_R, pp["z"] - PEEP_R, pp["z"] + PEEP_R, DOOR_FACE - 0.001)
    else:
        g.cyl(pe, (pp["x"], DOOR_FACE - 0.0006, pp["z"]), "y", PEEP_R, 0.0012, 16 if lod == 0 else 8)
    parts.append(pe)
    # "heating" lamp on the box (ozl_lamp_2 blinks, faces +x)
    hl = P("house_lamp", "lamp_r", group=SEL_LAMP2)
    lr_ = 0.0075
    if lod == 2:
        g.quad(hl, [(HX1 + 0.001, L.HLAMP["y"] + lr_, L.HLAMP["z"] - lr_), (HX1 + 0.001, L.HLAMP["y"] - lr_, L.HLAMP["z"] - lr_),
                    (HX1 + 0.001, L.HLAMP["y"] - lr_, L.HLAMP["z"] + lr_), (HX1 + 0.001, L.HLAMP["y"] + lr_, L.HLAMP["z"] + lr_)])
    elif lod == 1:
        g.cyl(hl, (HX1 + 0.005, L.HLAMP["y"], L.HLAMP["z"]), "x", lr_, 0.010, 8)
    else:
        lathe(hl, [(0.0080, 0.002), (0.0074, 0.0065), (0.0048, 0.0092), (0.0, 0.0102)], 12,
              ax_frame((HX1, L.HLAMP["y"], L.HLAMP["z"]), XA))
    parts.append(hl)
    # regulator dial (a decal) - a disc on the box side
    if lod < 2:
        dl = P("dial", "dial")
        g.cyl(dl, (HX1 + 0.002, L.DIAL["y"], L.DIAL["z"]), "x", L.DIAL["r"], 0.004, 20 if lod == 0 else 12)
        parts.append(dl)
    parts += build_lever(spec)
    if lod == 2:
        return parts
    # skids: bent sheet on the sides, a foot on the asbestos sheet
    ft = P("furnace_feet", "f_feet")
    zb, zt = TOP + L.ASB_T, FZ0 + 0.012
    for x in (FX0 + 0.030, FX1 - 0.030):
        slab(ft, g.Frame((x - 0.002, 0.0, (zb + zt) / 2), YA, ZA, XA), FY1 - FY0 - 0.04, zt - zb, 0.012, 0.004,
             nc=2 if lod == 0 else 1)
        g.box(ft, x - 0.012, x + 0.012, FY0 + 0.032, FY1 - 0.032, zb, zb + 0.003)
    parts.append(ft)
    # regulator knob: a skirt with a tick, a ribbed head
    kb = P("dial_knob", "ball")
    dy, dz = L.DIAL["y"], L.DIAL["z"]
    if lod == 0:
        lathe(kb, [(0.0465, 0.0), (0.0465, 0.004), (0.0430, 0.006), (0.0412, 0.003)], 16,
              ax_frame((HX1, dy, dz), XA))                                                        # dial ring
        g.cyl(kb, (HX1 + 0.0075, dy, dz), "x", 0.020, 0.005, 12)                                  # skirt
        star = [(dy + (0.0150 if k % 2 == 0 else 0.0132) * math.cos(math.pi * k / 10),
                 dz + (0.0150 if k % 2 == 0 else 0.0132) * math.sin(math.pi * k / 10)) for k in range(20)]
        g.prism(kb, star, (1, 2), HX1 + 0.010, HX1 + 0.025)
        lathe(kb, [(0.0132, 0.0), (0.0110, 0.0022), (0.0, 0.0030)], 12, ax_frame((HX1 + 0.025, dy, dz), XA))
        # skirt tick - at the "7" mark
        a = math.radians(-135 + 270 * 0.7)
        cy, cz = dy - 0.017 * math.sin(a), dz + 0.017 * math.cos(a)
        g.box(kb, HX1 + 0.0098, HX1 + 0.0108, cy - 0.0015, cy + 0.0015, cz - 0.0015, cz + 0.0015)
    else:
        g.cyl(kb, (HX1 + 0.010, dy, dz), "x", 0.018, 0.012, n)
        g.cyl(kb, (HX1 + 0.021, dy, dz), "x", 0.014, 0.012, n)
    parts.append(kb)
    if lod == 0:
        lr = P("house_lamp_rim", "chrome")
        lathe(lr, [(0.0115, 0.0), (0.0115, 0.004), (0.0100, 0.006), (0.0080, 0.006), (0.0080, 0.003)], 12,
              ax_frame((HX1, L.HLAMP["y"], L.HLAMP["z"]), XA))
        # peephole bushing: a wide collar, the hole toward the mica
        lathe(lr, [(0.0225, -0.003), (0.0225, 0.0025), (0.0195, 0.0055), (PEEP_R - 0.0003, 0.0055),
                   (PEEP_R - 0.0003, -0.002)], 14, ax_frame((pp["x"], DOOR_FACE, pp["z"]), -YA))
        parts.append(lr)
        # louvres: embossed, on the regulator box at the top and on the shell's left side at the
        # back (as on the KR 170)
        lv = P("louvers_house", "f_house")
        for k in range(7):
            hood_louver(lv, HX1, 1, HY0 + 0.05 + k * 0.032, HZ1 - 0.085, HZ1 - 0.025)
        lb = P("louvers_body", "f_body")
        for k in range(5):
            hood_louver(lb, FX0, -1, FY1 - 0.06 - k * 0.035, FZ1 - 0.12, FZ1 - 0.05)
        parts += [lv, lb]
        # screws: front plate corners, the inner panel, the door, the shell along the bottom of the
        # sides
        rv = P("rivets", "rivet")
        x0, x1, z0, z1 = INNER
        for x, z in ((FX0 + 0.012, FZ0 + 0.012), (FX1 - 0.012, FZ0 + 0.012), (FX0 + 0.012, FZ1 - 0.012),
                     (FCX, FZ1 - 0.012), (FX1 - 0.012, FZ1 - 0.012)):
            screw(rv, (x, PANEL_Y, z), -YA)
        for x in (x0 + 0.010, FCX, x1 - 0.010):
            screw(rv, (x, PANEL_Y - INNER_T, z1 - 0.010), -YA, r=0.004)
        for y in (HY0 + 0.022, HY1 - 0.022):
            for z in (HZ0 + 0.022, HZ1 - 0.022):
                screw(rv, (HX1, y, z), XA, r=0.004)
        for x in (FCX - DW / 2 + 0.024, FCX + DW / 2 - 0.024):
            for z in (DZ0 + 0.024, DZ0 + DH - 0.024):
                screw(rv, (x, DOOR_FACE, z), -YA, r=0.005)
        for y in (FY0 + 0.07, FY1 - 0.07):
            screw(rv, (FX0, y, FZ0 + 0.03), -XA)
        parts.append(rv)
    return parts


def build_lever(spec):
    """The door on two forks (on the inner panel at the door sides): fork ears, pins, door lugs;
    from the left pin a lever of round rod with smooth bends to a black ball; on the right a
    locking hook.
    """
    lod = spec["lod"]
    parts = []
    lv = P("lever", "lever")
    xl = XFORK[0]
    hub_x = xl - 0.006 - 0.005
    pts = [(hub_x + 0.003, YPIN, ZP), (FX0 - 0.030, YPIN - 0.004, ZP - 0.003),
           (KNOB[0] + 0.004, KNOB[1] + 0.075, KNOB[2] + 0.006), (KNOB[0], KNOB[1] + 0.042, KNOB[2])]
    if lod == 0:
        g.pipe(lv, fillet(pts, 0.030, 4), 0.0060, 8)
    elif lod == 1:
        g.pipe(lv, fillet(pts, 0.030, 1), 0.0060, 6)
    else:
        g.pipe(lv, [pts[0], pts[1], pts[3]], 0.0065, 4)
    if lod < 2:
        lf = P("door_forks", "lever")
        for s, xb in zip((-1, 1), XFORK):
            yb0 = PANEL_Y - INNER_T
            g.box(lf, xb - 0.006, xb + 0.006, yb0 - 0.004, yb0, ZP - 0.034, ZP + 0.034)   # foot
            for dz in (-1, 1):
                g.box(lf, xb - 0.006, xb + 0.006, YPIN - 0.011, yb0 - 0.004, ZP + dz * 0.0125 - 0.002,
                      ZP + dz * 0.0125 + 0.002)                                                    # ears
            # door lug between the ears
            xe = FCX + s * DW / 2
            g.box(lf, min(xe, xe + s * 0.0075), max(xe, xe + s * 0.0075), YPIN - 0.009, YPIN + 0.009, ZP - 0.0085,
                  ZP + 0.0085)
            g.cyl(lf, (xb, YPIN, ZP), "x", 0.0036, 0.024, 8 if lod == 0 else 6)                    # pin
            if s > 0:
                g.cyl(lf, (xb + 0.0075, YPIN, ZP), "x", 0.0062, 0.003, 6)                         # pin nut
        g.cyl(lf, (hub_x, YPIN, ZP), "x", 0.0085, 0.010, 10 if lod == 0 else 6)                    # lever hub
        parts.append(lf)
        if lod == 0:
            for xb in XFORK:
                for dz in (-1, 1):
                    screw(lf, (xb, PANEL_Y - INNER_T - 0.004, ZP + dz * 0.026), -YA, r=0.0032, h=0.0016)
            # locking hook on the right: a pivoting rod with a ball
            xr = XFORK[1] + 0.0075
            hk = fillet([(xr, YPIN, ZP), (xr + 0.022, YPIN - 0.006, ZP - 0.006), (xr + 0.026, YPIN - 0.012, ZP - 0.045)],
                        0.010, 3)
            g.pipe(lv, hk, 0.0032, 6)
            lathe(lv, sphere_prof(0.0055, 4), 8, ax_frame(hk[-1], ZA))
    parts.append(lv)
    # lever ball: bakelite, on a brass bushing
    bl = P("lever_ball", "ball")
    ring = 14 if lod == 0 else 8 if lod == 1 else 6
    fb = ax_frame(KNOB, -YA)
    lathe(bl, sphere_prof(0.025, 8 if lod == 0 else 4 if lod == 1 else 3), ring, fb)
    if lod < 2:
        lathe(bl, [(0.0088, -0.046), (0.0088, -0.032), (0.0072, -0.022), (0.0, -0.020)], ring, fb)
    parts.append(bl)
    return parts


# =============================================================================
# Exhaust and thermocouple
# =============================================================================
def build_exhaust(spec):
    lod = spec["lod"]
    n = 12 if lod == 0 else 8 if lod == 1 else 6
    e = L.EXH
    x, y, r, top, back = e["x"], e["y"], e["r"], e["top"], e["back"]
    ex = P("exhaust", "exhaust")
    g.cyl(ex, (x, y, FZ1 + 0.034), "z", r + 0.008, 0.060, n)                                   # stub
    pts = fillet([(x, y, FZ1 + 0.055), (x, y, top), (x, back, top)], 0.085, 6 if lod == 0 else 3 if lod == 1 else 2)
    g.pipe(ex, pts, r, 14 if lod == 0 else n)
    parts = [ex]
    if lod == 2:
        return parts
    cl = P("exhaust_clamps", "clamp")
    g.cyl(cl, (x, y, FZ1 + 0.002), "z", r + 0.030, 0.004, n)                                   # flange on the roof
    g.cyl(cl, (x, back - 0.012, top), "y", r + 0.0045, 0.024, n)                               # wall coupling
    for yc in (y + 0.20,):
        g.cyl(cl, (x, yc, top), "y", r + 0.0035, 0.022, n)                                     # clamp
        if lod == 0:
            for s in (-1, 1):
                g.box(cl, x + r + 0.002, x + r + 0.018, yc - 0.010, yc + 0.010, top + s * 0.0045 - 0.0015,
                      top + s * 0.0045 + 0.0015)                                                # clamp ears
            g.cyl(cl, (x + r + 0.012, yc, top), "z", 0.0045, 0.018, 6)                          # clamp bolt
    if lod == 0:
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            g.cyl(cl, (x + (r + 0.020) * math.cos(a), y + (r + 0.020) * math.sin(a), FZ1 + 0.0055), "z", 0.0055,
                  0.003, 6)                                                                     # flange bolts
        # damper: a pin across the pipe and a flag handle on the right
        zs = FZ1 + 0.105
        g.pipe(cl, [(x - r - 0.006, y, zs), (x + r + 0.030, y, zs)], 0.004, 6)
        slab(cl, g.Frame((x + r + 0.050, y - 0.002, zs), XA, ZA, -YA), 0.045, 0.022, 0.008, 0.004, nc=2)
        g.cyl(cl, (x - r - 0.004, y, zs), "x", 0.0065, 0.004, 6)                               # pin nut
    parts.append(cl)
    # thermocouple: a flange on the roof, a porcelain sleeve, an aluminium head with a cover and a
    # cable gland
    tc = L.TC
    tx, ty = tc["x"], tc["y"]
    sh = P("tc_sheath", "sheath")
    g.cyl(sh, (tx, ty, FZ1 + 0.05), "z", 0.008, 0.10, 10 if lod == 0 else 6)
    parts.append(sh)
    hd = P("tc_head", "tc_head")
    fh = ax_frame((tx, ty, FZ1 + 0.100), ZA)
    if lod == 0:
        lathe(hd, [(0.0100, 0.000), (0.0215, 0.004), (0.0240, 0.009), (0.0240, 0.030), (0.0200, 0.034),
                   (0.0200, 0.040), (0.0145, 0.0458), (0.0, 0.0465)], 12, fh)
        g.cyl(hd, (tx, ty, FZ1 + 0.002), "z", 0.017, 0.004, 12)                                # flange
        for s in (-1, 1):
            screw(hd, (tx + s * 0.012, ty, FZ1 + 0.004), ZA, r=0.003, h=0.0015)
    else:
        g.cyl(hd, (tx, ty, FZ1 + 0.105 + 0.018), "z", 0.024, 0.036, n)
    parts.append(hd)
    if lod == 0:
        gl = P("tc_gland", "clamp")
        g.cyl(gl, (tx - 0.024 - 0.004, ty, FZ1 + 0.120), "x", 0.0085, 0.010, 6)
        g.cyl(gl, (tx - 0.024 - 0.015, ty, FZ1 + 0.120), "x", 0.0050, 0.012, 10, r2=0.0062)
        parts.append(gl)
    return parts


# =============================================================================
# Control panel: body, door-panel, meters, lamps, switch, glands, hooks
# =============================================================================
def meter(m, lod, name):
    w, h, fl = m["w"], m["h"], m["flange"]
    x0, x1, z0, z1 = m["x"] - w / 2, m["x"] + w / 2, m["z"], m["z"] + h
    fx0, fx1 = m["x"] - fl / 2, m["x"] + fl / 2
    fz0 = z0 - (fl - h) * 0.65
    fz1 = fz0 + fl
    yf = YS - 0.012
    bk = P(name + "_case", "black")
    if lod == 2:
        g.box(bk, fx0, fx1, yf, YS, fz0, z0)
        g.box(bk, fx0, fx1, yf, YS, z1, fz1)
    else:
        fc_z = (fz0 + fz1) / 2
        bezel(bk, front_frame((m["x"], YS, fc_z)), fl, fl, 0.009 if lod == 0 else 0.006, w, h,
              ci=(0.0, (z0 + z1) / 2 - fc_z), t=0.012, bev=0.0025 if lod == 0 else 0.0, nc=2 if lod == 0 else 1)
    fc = P(name + "_face", "face_" + m["scale"])
    yface = YS - 0.002
    if lod == 2:
        quad_y(fc, x0, x1, z0, z1, yface)
    else:
        g.box(fc, x0, x1, yface, YS, z0, z1)
    parts = [bk, fc]
    px, pz = m["x"], z0 + L.PIVOT_K * h
    nl = L.NEEDLE_K * h
    nd = P(name + "_needle", "needle", group=m["bone"])
    d = (math.sin(NEEDLE0), math.cos(NEEDLE0))
    pp = (d[1], -d[0])
    hw = 0.0012 * h / 0.056
    poly = [(-0.006, -hw), (nl, -hw * 0.3), (nl, hw * 0.3), (-0.006, hw)]
    poly = [(px + a * d[0] + b * pp[0], pz + a * d[1] + b * pp[1]) for a, b in poly]
    yn = (yface - 0.0025, yface - 0.0017)
    g.prism(nd, poly, (0, 2), *yn)
    if lod < 2:
        g.cyl(nd, (px, yn[0] - 0.0005, pz), "y", 0.004, 0.001, 10 if lod == 0 else 5)
    parts.append(nd)
    if lod == 0:
        gl = P(name + "_glass", "chrome", section="glass")
        yg = yface - 0.0065
        g.box(gl, x0, x1, yg - 0.0005, yg + 0.0005, z0, z1)
        parts.append(gl)
        g.cyl(bk, (m["x"], yf - 0.002, fz0 + 0.009), "y", 0.004, 0.004, 8)                      # zero corrector
        g.box(bk, m["x"] - 0.0028, m["x"] + 0.0028, yf - 0.0045, yf - 0.0035, fz0 + 0.0085, fz0 + 0.0095)   # slot
        for sx_, sz_ in ((fx0 + 0.011, fz1 - 0.011), (fx1 - 0.011, fz0 + 0.011)):
            screw(bk, (sx_, yf, sz_), -YA, r=0.0032, h=0.0015)
    return parts, (px, yn[1], pz)


def build_shield(spec):
    lod = spec["lod"]
    n = 12 if lod == 0 else 8 if lod == 1 else 6
    bx = P("shield_box", "sh_box")
    g.box(bx, SX0, SX1, SY0, SY1, SZ0, SZ1, **({0: dict(r=0.008, seg=2), 1: dict(r=0.006, seg=1)}.get(lod, {})))
    pn = P("shield_panel", "sh_face")
    if lod == 2:
        g.box(pn, SX0 + 0.010, SX1 - 0.010, YS, SY0 + 0.001, SZ0 + 0.012, SZ1 - 0.012)
    else:
        slab(pn, front_frame(((SX0 + SX1) / 2, SY0 + 0.001, (SZ0 + SZ1) / 2)), SX1 - SX0 - 0.020, SZ1 - SZ0 - 0.024,
             0.008, SY0 + 0.001 - YS, bev=0.0025 if lod == 0 else 0.0, nc=3 if lod == 0 else 1, nb=2)
    parts = [bx, pn]
    for i, m in enumerate(L.METERS):
        ps, ax = meter(m, lod, "meter%d" % i)
        parts += ps
        AXES[m["bone"]] = ax
    # "mains" (green, lit while working) and "heating" (red, blinking) lamps
    lamps = [(SX0 + 0.060, SZ0 + 0.120, "g", SEL_LAMP), (SX0 + 0.120, SZ0 + 0.120, "r", SEL_LAMP2)]
    for x, z, c, sel in lamps:
        lp = P("shield_lamp_" + c, "lamp_" + c, group=sel)
        r = 0.010
        if lod == 2:
            quad_y(lp, x - r, x + r, z - r, z + r, YS - 0.001)
        elif lod == 1:
            g.cyl(lp, (x, YS - 0.010, z), "y", r, 0.010, n)
        else:
            lathe(lp, [(0.0118, 0.003), (0.0110, 0.010), (0.0072, 0.0145), (0.0, 0.0160)], 14, ax_frame((x, YS, z), -YA))
        parts.append(lp)
    if lod == 2:
        return parts
    kb = P("shield_knobs", "black")
    # packet switch: a square base, a round washer, a lever handle
    sx, sz = SX1 - 0.085, SZ0 + 0.110
    slab(kb, front_frame((sx, YS, sz)), 0.064, 0.064, 0.008, 0.012, bev=0.003 if lod == 0 else 0.0,
         nc=2 if lod == 0 else 1, nb=1)
    g.cyl(kb, (sx, YS - 0.016, sz), "y", 0.020, 0.008, 12 if lod == 0 else 8)
    slab(kb, front_frame((sx, YS - 0.019, sz)), 0.018, 0.082, 0.0089, 0.019, bev=0.004 if lod == 0 else 0.0,
         nc=2 if lod == 0 else 1, nb=2)
    # cable glands: on top (thermocouple) and on the right (regulator box)
    gx, gy = DUCT["gland_tc"]
    yg, zg = DUCT["gland_side"]
    g.cyl(kb, (gx, gy, SZ1 + 0.005), "z", 0.012, 0.010, 6)
    g.cyl(kb, (gx, gy, SZ1 + 0.017), "z", 0.0078, 0.014, 8 if lod == 0 else 6, r2=0.0058)
    g.cyl(kb, (SX1 + 0.005, yg, zg), "x", 0.012, 0.010, 6)
    g.cyl(kb, (SX1 + 0.017, yg, zg), "x", 0.0085, 0.014, 8 if lod == 0 else 6, r2=0.0068)
    parts.append(kb)
    if lod == 0:
        ch = P("shield_hw", "chrome")
        for x, z, c, sel in lamps:
            lathe(ch, [(0.0170, 0.0), (0.0170, 0.005), (0.0135, 0.008), (0.0118, 0.004)], 10,
                  ax_frame((x, YS, z), -YA))
        # hinges on the left, a keyed lock on the right, panel screws
        for z in (SZ0 + 0.08, SZ1 - 0.08):
            g.cyl(ch, (SX0 - 0.0015, YS + 0.001, z), "z", 0.0055, 0.05, 8)
        g.cyl(ch, (SX1 - 0.030, YS - 0.004, SZ1 - 0.060), "y", 0.009, 0.008, 12)
        g.box(ch, SX1 - 0.0315, SX1 - 0.0285, YS - 0.0085, YS - 0.0075, SZ1 - 0.066, SZ1 - 0.054)
        for x in (SX0 + 0.022, SX1 - 0.022):
            for z in (SZ0 + 0.024, SZ1 - 0.024):
                screw(ch, (x, YS, z), -YA)
        # hooks on the left side for the vanilla tools
        for key, y in HUNG:
            zh, hl_ = HOOK_Z, hook_len(key)
            g.pipe(ch, fillet([(SX0 + 0.003, y, zh), (SX0 - hl_, y, zh), (SX0 - hl_ - 0.005, y, zh + 0.012)], 0.005, 2),
                   0.0024, 5)
        parts.append(ch)
        tg = P("shield_tags", "tag")
        rt = []
        for x, z, w, h in L.TAGS:
            g.box(tg, x - w / 2, x + w / 2, YS - 0.0012, YS, z - h / 2, z + h / 2)
            rt += [(x - w / 2 + 0.005, z), (x + w / 2 - 0.005, z)]
        for x, z, c, sel in lamps:
            g.box(tg, x - 0.022, x + 0.022, YS - 0.0012, YS, z - 0.040, z - 0.028)
        g.box(tg, sx - 0.035, sx + 0.035, YS - 0.0012, YS, sz - 0.062, sz - 0.048)
        for x, z in rt:
            g.cyl(tg, (x, YS - 0.0016, z), "y", 0.0018, 0.0012, 6)                               # nameplate rivets
        parts.append(tg)
    return parts


# =============================================================================
# Sample: bricks, plate, tongs
# =============================================================================
def build_sample(spec):
    lod = spec["lod"]
    p = L.PLATE
    bw, bd, bh = L.BRICK[1], L.BRICK[0], L.BRICK[2]
    bk = P("bricks", "brick")
    for k, dx in enumerate((-0.085, 0.085)):
        fr = yaw_frame((p["x"] + dx, p["y"], TOP), 3.0 if k else -2.0)
        g.box(bk, -bw / 2, bw / 2, -bd / 2, bd / 2, 0.0, bh, frame=fr,
              **({0: dict(r=0.006, seg=1), 1: dict(r=0.006, seg=1)}.get(lod, {})))
    pl = P("plate", "plate")
    fr = yaw_frame((p["x"], p["y"], TOP + bh), 7.0)
    g.box(pl, -p["w"] / 2, p["w"] / 2, -p["d"] / 2, p["d"] / 2, 0.0, p["t"], frame=fr, **bev(lod, 0.002))
    parts = [bk, pl]
    if lod > 0:
        return parts
    # crucible tongs: two arms of round rod on a rivet, the jaws are half-rings, the handles are
    # loops
    tg = P("tongs", "tongs")
    rr = 0.0042
    piv = 0.105
    fr = yaw_frame((TONGS[0], TONGS[1], TOP), 0.0)
    for s in (-1, 1):
        # jaw - a half-ring R 28 mm (together the jaws grip a crucible), beyond the hinge an arm to
        # the handle, at the end of the handle a loop bent back along the arm
        ab = [(0.028 - 0.028 * math.cos(math.radians(th)), s * 0.028 * math.sin(math.radians(th)))
              for th in (12, 50, 90, 130, 165)]
        ab += [(0.075, s * 0.010), (piv, 0.0), (0.140, -s * 0.008), (0.300, -s * 0.018), (0.350, -s * 0.024),
               (0.378, -s * 0.030), (0.394, -s * 0.021), (0.386, -s * 0.010), (0.362, -s * 0.011)]
        pts = []
        for a, b in ab:
            lift = 0.0080 * math.exp(-((a - piv) / 0.035) ** 2) if s > 0 else 0.0
            pts.append(tuple(fr.p(a, b, rr + lift)))
        g.pipe(tg, spline(pts, 2), rr, 5)
    # hinge rivet: a pin through both arms, a half-round head on top
    g.cyl(tg, tuple(fr.p(piv, 0.0, 0.0082)), "z", 0.0048, 0.0160, 8)
    lathe(tg, [(0.0068, 0.0), (0.0052, 0.0020), (0.0, 0.0029)], 10, ax_frame(tuple(fr.p(piv, 0.0, 0.0162)), ZA))
    parts.append(tg)
    return parts


# =============================================================================
# Cables: thermocouple -> panel, regulator box -> panel, power to the floor
# =============================================================================
def build_cables(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    k, sides = (2, 6) if lod == 0 else (1, 4)
    tc = L.TC
    gx, gy = DUCT["gland_tc"]
    yg, zg = DUCT["gland_side"]
    (hx_a, hz_a), (hx_b, hz_b) = HOUSE_GL
    parts = []
    c1 = P("cable_tc", "cable")
    pts = [(tc["x"] - 0.044, tc["y"], FZ1 + 0.120), (tc["x"] - 0.085, tc["y"] + 0.012, FZ1 + 0.105),
           (gx + 0.045, gy + 0.02, SZ1 + 0.10), (gx + 0.004, gy + 0.004, SZ1 + 0.055), (gx, gy, SZ1 + 0.024)]
    g.pipe(c1, spline(pts, k), 0.0045, sides)
    parts.append(c1)
    c2 = P("cable_house", "cable")
    # wires from the box - smooth arcs (fillet: no spline overshoot on short segments)
    nf = 2 if lod == 0 else 1
    pts = [(hx_a, HY1 + 0.010, hz_a), (hx_a, HY1 + 0.075, hz_a - 0.02), (HX0 + 0.010, 0.336, TOP + 0.0065),
           (-0.045, 0.330, TOP + 0.0065), (SX1 + 0.050, yg + 0.02, TOP + 0.0065), (SX1 + 0.026, yg, zg)]
    g.pipe(c2, fillet(pts, 0.035, nf), 0.006, sides)
    parts.append(c2)
    c3 = P("cable_power", "cable")
    pts = [(hx_b, HY1 + 0.010, hz_b), (hx_b + 0.004, Y1 + 0.028, hz_b - 0.02), (0.430, Y1 + 0.034, 0.0065),
           (0.26, Y1 + 0.060, 0.0065)]
    g.pipe(c3, fillet(pts, 0.06, nf + 1), 0.0065, sides)
    parts.append(c3)
    if lod == 0:
        gl = P("house_glands", "clamp")
        for hx, hz in HOUSE_GL:
            g.cyl(gl, (hx, HY1 + 0.004, hz), "y", 0.0090, 0.008, 6)
        parts.append(gl)
    return parts


def build_lod(spec):
    parts = build_cabinet(spec) + build_furnace(spec) + build_exhaust(spec) + build_shield(spec)
    parts += build_sample(spec) + build_cables(spec)
    parts = [p for p in parts if p.bm.faces]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("M35 bounds: x %.3f..%.3f  y %.3f..%.3f  z %.3f..%.3f" % (BOUNDS["lo"][0], BOUNDS["hi"][0],
              BOUNDS["lo"][1], BOUNDS["hi"][1], BOUNDS["lo"][2], BOUNDS["hi"][2]))
        for d in DECOR:
            q = kv.corners(d[5], d[1], d[2], d[3])
            print("decor %-12s x %.3f..%.3f  y %.3f..%.3f  z %.3f..%.3f" % (
                d[5], min(c[0] for c in q), max(c[0] for c in q), min(c[1] for c in q), max(c[1] for c in q),
                min(c[2] for c in q), max(c[2] for c in q)))
    return parts


def collision():
    """The cabinet, the furnace with the box and the lever, the panel - three convex boxes. The
    exhaust pipe and the bricks with the plate are thinner than 0.5 m - not made components
    (as in M33).
    """
    steel = kx.PEN + r"\metalplate.rvmat"
    cab = kx.box_pts(X0 - 0.01, X1 + 0.01, Y0 - 0.01, Y1 + 0.01, 0.0, TOP)
    furn = kx.box_pts(FX0 - 0.10, HX1 + 0.03, FY0 - 0.10, FY1 + 0.01, TOP, FZ1 + 0.01)
    sh = kx.box_pts(SX0, SX1, SY0, SY1, TOP, SZ1)
    comps = [(cab, steel), (furn, steel), (sh, steel)]
    memory = {
        "invView": [(0.0, -2.4, 1.2)],
        "ce_center": [(0.0, 0.0, 0.8)],
        "ce_radius": [(1.0, 0.0, 0.8)],
    }
    for b, (px, py, pz) in AXES.items():
        memory[b + "_axis"] = [(px, py, pz), (px, py - 0.05, pz)]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2] + 0.004)
    return comps, 160.0, memory, bbox


# Preview of the working look (--look): the needles are at their working marks (does not go
# into the p3d: OZL_WorkFx sways them). In the kit a look pose is only a shift (move), so the
# needle rotation is a wrapper over krender.place_look here.
_place_look = krender.place_look


def _place_look_work(parts, kind_table, origin, remap=None, **kw):
    obs = _place_look(parts, kind_table, origin, remap=remap, **kw)
    if remap:
        turn = {m["bone"]: math.radians(L.ARC_DEG) * m["phase"] for m in L.METERS}
        for p, ob in zip(parts, obs):
            if p.group in turn and p.group in AXES:
                c = Vector(AXES[p.group])
                ob.matrix_world = Matrix.Translation(c) @ Matrix.Rotation(turn[p.group], 4, "Y") @ Matrix.Translation(-c)
    return obs


krender.place_look = _place_look_work

# The first five are the --look preview (overall view, furnace, panel, regulator box, sample), the
# working look uses the first three
SHOTS = [
    ("front", (-0.9, -2.6, 1.7), (0.0, 0.0, 0.85), 30),
    ("furnace", (-0.35, -1.25, 1.35), (0.17, -0.2, 1.08), 34),
    ("shield", (-0.62, -0.88, 1.28), (-0.26, 0.10, 1.04), 34),
    ("regulator", (0.95, -0.62, 1.22), (0.38, 0.0, 1.03), 34),
    ("sample", (-0.55, -0.95, 1.30), (-0.25, -0.18, 0.84), 34),
    ("right", (1.6, -1.2, 1.5), (0.25, 0.0, 1.0), 32),
    ("left", (-1.9, -1.0, 1.5), (0.0, 0.0, 0.9), 32),
    ("back", (1.0, 2.2, 1.7), (0.0, 0.0, 0.9), 30),
]

M.look_shots = (5, 3)
M.run(build_lod, collision, SHOTS, row_step=1.6, row_shot=((1.6, -6.0, 2.0), (1.6, 0, 0.8)))
