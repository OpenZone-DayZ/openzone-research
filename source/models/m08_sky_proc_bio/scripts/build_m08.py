"""M08 - field autoclave: the Clear Sky Bio Analyzer (OZL_Sky_Proc_Bio).
Analyzer: cargo 4x4, no modules (no module_1..3 points, as in M02, M04 and M06).

    blender --background --python build_m08.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (pressure gauge, KFK-2 scale, KFK-2
panels and hotplate, sign, tag). Where things are on the instrument faces - layout.py (shared with
make_decals.py).

A Clear Sky makeshift built from real things:
- pressure-cooker autoclave after the All American 921 (21.5 quart): inner diameter 12 1/4" (311 mm),
  inner height 10 1/2" (267 mm), overall height 15 3/8" (391 mm) with the handle, 15" (381 mm) to the
  lid with clamps. Body outside diameter 0.335 m, six wing-nut clamps, a gauge on a post, a weight
  valve, a petcock, a lid handle; clean aluminium;
- two-burner hotplate after the EPCh-2 (enamelled steel, burners of diameter 145 and 180 mm; overall
  505 x 285 x 96 mm); there is no data sheet for the "Mechta 212". Open coils in ceramic, as on old
  hotplates;
- KFK-2 photocolorimeter (ZOMZ) - 435 x 355 x 330 mm, 12-14 kg: a base, a cuvette compartment with a
  lid in the middle, a scale housing at the back, an illuminator on the left, filter and sensitivity
  knobs;
- crates - home-made plank ones, sized to the hotplate and the instrument: 0.56 x 0.56 x 0.46 and
  0.45 x 0.40 x 0.40 m, light blue Clear Sky paint over wood.
Total 1.05 x 1.13 x 0.48 m (deeper with the extension cord on the floor). The hotplate crate and the
KFK-2 crate side by side are wider than 0.9 m, and the 0.39 m cooker on the hotplate and the crate
makes 1.1 m, hence the overall size.

Look: the "dayz" look (matte, dirtier, coloured AO); sizes and arrangement are as accepted on the
stand. The cooker is built from bodies of revolution (each of the six clamps has a fork boss, an axle,
a swing bolt, a washer and a wing nut). The hotplate has chrome burner rings, ceramic with a coil in
a groove and knurled knobs with step digits; its cord is cloth-braided. The KFK-2 has face panels with
outlines and wavelength digits (a decal, no letters), a hinged cuvette lid, a recessed scale window
(behind the glass the scale and the needle bone) and a rack with four cuvettes beside it. The crates
are boards with rounded edges, batten frames, rope handles and nails, with Clear Sky paint over wood
(the grain shows beneath it, wood in the chips). The extension cord is a Soviet three-socket strip
with smooth cords that do not cross. Small props are vanilla DayZ items through proxies (kvanilla): a
water bottle (to top up the autoclave), iodine and disinfectant spray behind the hotplate, a
thermometer in front of it, a blood test kit on the KFK-2, a GP-5 gas mask hanging on the rope handle
of the left crate.

Work look: the burner coils, the hotplate lamp and the KFK-2 indicator are ozl_lamp_work, the KFK-2
scale window is ozl_screen (both in hiddenSelections: "work" is atlas _on and an emissive rvmat).
"Work" is a loop (OZL_WorkFx, class OZL_Work): the gauge needle (bone ozl_needle, source ozl_needle)
rises to ~1.1 kgf/cm2 and breathes (wobble), the weight valve swings on its tube (bone ozl_weight,
source ozl_weight, wobble 0..8 degrees), the KFK-2 needle (bone ozl_meter, source ozl_meter) goes to
62 % and trembles slightly. Phase 0 is rest for all: needles at zero, the valve stands level.

Blender axes: X is width, Y is depth (face toward -Y), Z is up.
"""
import math
import os
import random
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
# Dimensions, m
# =============================================================================
XA0, XA1, YA0, YA1, ZA = L.XA0, L.XA1, L.YA0, L.YA1, L.ZA
XB0, XB1, YB0, YB1, ZB = L.XB0, L.XB1, L.YB0, L.YB1, L.ZB
BOARD, BT = 0.018, 0.014                                    # crate board, batten on top
# hotplate
XP, YP, PW, PD, ZP0, ZPT, BURN = L.XP, L.YP, L.PW, L.PD, L.ZP0, L.ZPT, L.BURN
YBN = YP + 0.005
ZCER = ZPT + 0.0045                                         # top of the ceramic
ZCOIL = ZCER + 0.0003                                       # coil axis: half sunk in the groove
# pressure cooker (All American 921)
XC, YC = BURN[1][0], YBN
RC_ = 0.1675                                                # body outside
ZC0 = ZCOIL + 0.003
ZC1 = ZC0 + 0.272                                           # top of the body, bottom of the lid flange
ZF1 = ZC1 + 0.014                                           # top of the flange
RF, ZD = 0.181, ZF1 + 0.052                                 # flange, top of the lid dome
CLAMPS = [math.radians(30 + 60 * k) for k in range(6)]
RCL = 0.195                                                 # clamp axis
# gauge on a post, facing the player: centre, radius, case depth
GX, GY = XC - 0.07, YC - 0.06
GR, GDEP = 0.036, 0.026
GZ = ZD + 0.085
YG_BACK = GY + GDEP / 2                                     # back of the case
YDIAL = YG_BACK - (GDEP - 0.0042)                           # dial plane
# weight valve on a tube at the front right, petcock and safety plug at the back
VX, VY = XC + 0.070, YC - 0.058
ZLID_V = ZD - 0.003                                         # lid surface at the valve
ZPIPE = ZLID_V + 0.034                                      # top of the tube - the weight swing axis
# KFK-2
XK, YK, KW, KD, KH, KB, ZK0 = L.XK, L.YK, L.KW, L.KD, L.KH, L.KB, L.ZK0
WIN, YWIN, HOUSE_W = L.WIN, L.YWIN, L.HOUSE_W
YSCALE = YWIN + 0.0095                                      # scale in the depth of the window
YMETER = YWIN + 0.0062                                      # needle between the scale and the glass
# extension cord on the floor in front of the crates: sockets, two of them with the hotplate and KFK-2 plugs
EXT = Vector((0.06, -0.34, 0.0))
EXT_H = 0.035
SOCKETS = [-0.07, 0.0, 0.07]                                # socket offsets along x
PLUG_TOP = EXT_H + 0.055
CORD_X = (0.052, 0.068)                                     # hotplate and KFK-2 cords in the gap between the crates

LOD_SPECS = [
    dict(lod=0, bev=1, sides=28),
    dict(lod=1, bev=0, sides=16),
    dict(lod=2, bev=0, sides=10),
]

REGIONS = {
    "crate": ("crate", 0.6), "crate_front": ("crate_front", 0.9), "crate_y": ("crate_y", 0.6),
    "crate_z": ("crate_z", 0.6), "gap": ("gap", 0.3), "nail": ("nail", 1.5), "rope": ("rope", 1.2),
    "plate": ("plate", 1.0), "plate_front": ("plate_front", 1.4), "plate_top": ("plate_top", 1.0),
    "ceramic": ("ceramic", 1.2), "coil": ("coil", 1.0), "chrome": ("chrome", 1.2), "pilot": ("pilot", 2.0),
    "knob": ("knob", 2.0), "knob_mark": ("plastic_white", 2.0), "rubber": ("rubber", 0.6),
    "cord_cloth": ("cord_cloth", 0.6), "cable": ("rubber", 0.5), "dark": ("dark", 0.5),
    "alu": ("alu", 0.7), "alu_lid": ("alu_lid", 0.8), "alu_cast": ("alu_cast", 1.2), "steel": ("steel", 1.2),
    "bakelite": ("bakelite", 1.2), "gauge": ("gauge", 5.0), "needle": ("needle", 2.0),
    "kfk": ("kfk", 0.8), "kfk_front": ("kfk_front", 1.4), "kfk_blue": ("kfk_blue", 0.8), "kfk_vent": ("kfk_vent", 1.0),
    "kfk_side_vent": ("kfk_side_vent", 1.2), "scale": ("scale", 6.0), "needle_k": ("needle_k", 2.0),
    "tag": ("tag", 4.0), "liquid_a": ("liquid_a", 2.0), "liquid_b": ("liquid_b", 2.0), "rack": ("rack", 2.0),
    "ext": ("ext", 1.5), "ext_plug": ("ext_plug", 1.5),
}

# =============================================================================
# Materials
# =============================================================================


def decal(name, center, size, y_face, eps=0.003):
    return (os.path.join(WORK, name), "y", -1, ("x", "z"), center, size, (y_face - eps, y_face + eps))


def rect(name, r, y_face, eps=0.003):
    x0, x1, z0, z1 = r
    return decal(name, ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0), y_face, eps)


def build_paint_wood(mat, origin, color, wood=kmats.lin((150, 116, 76)), seed=2.2, along="x", gloss=0.22, spec=0.12,
                     chip=(0.62, 0.68), floor_z=0.0, dust=0.25, grime=0.85, decal_items=()):
    """Clear Sky paint on boards (its own builder: kmats paint is for metal): the grain and growth rings
    show through a thin layer (tone and relief), brush strokes along the board, wood in the chips (on
    the board edges and in patches), dirt from below. along is the grain axis ("x" / "y" / "z")."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    k = {"x": (0.04, 1.0, 1.0), "y": (1.0, 0.04, 1.0), "z": (1.0, 1.0, 0.04)}[along]
    fib = t.stretch(vec, *k)
    fibers = t.noise(fib, 160.0, 4.0, 0.7)
    wave = t.node("ShaderNodeTexWave", Scale=9.0, Distortion=6.0, **{"Detail": 3.0, "Detail Scale": 1.5})
    wave.wave_type = "RINGS"
    t.link(fib, wave.inputs["Vector"])
    ring = wave.outputs["Fac"]
    wdark = tuple(c * 0.58 for c in wood[:3]) + (1,)
    wood_col = t.mixc(t.math("MULTIPLY", ring, 0.55), wood, wdark)
    wood_col = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", fibers, 0.35), 0.6), wood_col, wdark)
    tone = t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0)
    paint = t.mixc(tone, tuple(c * 0.90 for c in color[:3]) + (1,), color)
    strokes = t.maprange(t.noise(t.stretch(vec, *[q * 2.0 if q < 1 else 1.0 for q in k]), 30.0, 3.0, 0.6),
                         0.35, 0.7, 0.0, 1.0)
    paint = t.mixc(t.math("MULTIPLY", strokes, 0.12), paint, tuple(c * 0.80 for c in color[:3]) + (1,))
    paint = t.mixc(t.math("MULTIPLY", ring, 0.10), paint, tuple(c * 0.82 for c in color[:3]) + (1,))
    paint = kmats.decals(t, paint, sep, nsep, decal_items)
    edge = t.maprange(t.edge_wear(0.004), 0.06, 0.25, 0.0, 1.0)
    blot = t.noise(vec, 9.0, 10.0, 0.7)
    f = t.math("ADD", t.math("MULTIPLY", blot, 0.75), t.math("MULTIPLY", edge, 0.6))
    chips = t.step(f, chip[0], chip[1])
    # rim of flaked paint around a chip - lighter
    rim = t.math("SUBTRACT", t.step(f, chip[0] - 0.04, chip[0]), chips)
    col = t.mixc(t.math("MULTIPLY", rim, 0.5), paint, tuple(min(1.0, c * 1.18) for c in color[:3]) + (1,))
    col = t.mixc(chips, col, wood_col)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    gl = t.math("SUBTRACT", gloss, t.math("ADD", t.math("MULTIPLY", chips, gloss * 0.6), t.math("MULTIPLY", dirt, gloss * 0.5)))
    sp = t.math("SUBTRACT", spec, t.math("ADD", t.math("MULTIPLY", chips, spec * 0.5), t.math("MULTIPLY", dirt, spec * 0.4)))
    h = t.math("ADD", t.math("MULTIPLY", fibers, 0.18), t.math("MULTIPLY", ring, -0.16))
    h = t.math("SUBTRACT", h, t.math("MULTIPLY", chips, 0.35))
    return kmats.out(t, col, gl, sp, h)


def build_dial(mat, origin, color, decal_items=(), gloss=0.5, spec=0.3):
    """Dial and scale under glass: a picture on a flat field, without the dirt and scratches of the "dayz"
    profile (otherwise the digits get blotchy)."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 1.0)
    nsep = t.normal()
    col = kmats.decals(t, color, sep, nsep, decal_items)
    return kmats.out(t, col, gloss, spec, 0.0)


KX0, KX1 = XK - KW / 2, XK + KW / 2
KY0, KY1 = L.KY0, YK + KD / 2
ZKB = ZK0 + KB                                              # top of the KFK-2 base
TAG = (KY0 + 0.075, KY0 + 0.135, ZK0 + 0.085, ZK0 + 0.109)  # tag on the right side: y0, y1, z0, z1
KINDS = kmats.std_kinds(floor_z=0.0)
# light blue Clear Sky paint on wood: wood in the chips, no rust, dirt at the bottom of the crates
BLUE = dict(color=kmats.lin((150, 192, 214)), seed=2.2, gloss=0.22, spec=0.12, chip=(0.58, 0.64), floor_z=0.0,
            dust=0.32, grime=0.95)
CRATE_FRONT = [decal("decal_biohazard.png", ((XA0 + XA1) / 2, 0.30), (0.20, 0.20), YA0)]
GAUGE = [decal("decal_gauge.png", (GX, GZ), (2 * (GR - 0.004), 2 * (GR - 0.004)), YDIAL, eps=0.0012)]
PLATE_FRONT = [rect("decal_plate_front.png", (XP - PW / 2, XP + PW / 2, ZP0, ZPT), L.PY0)]
KFK_FRONT = [rect("decal_kfk_panel_l.png", L.PANEL_L, KY0), rect("decal_kfk_panel_r.png", L.PANEL_R, KY0)]
TAG_DECAL = [(os.path.join(WORK, "decal_tag.png"), "x", 1, ("y", "z"), ((TAG[0] + TAG[1]) / 2, (TAG[2] + TAG[3]) / 2),
              (TAG[1] - TAG[0], TAG[3] - TAG[2]), (KX1 - 0.001, KX1 + 0.003))]
KFK_PAINT = dict(color=kmats.lin((206, 210, 208)), under=kmats.lin((70, 72, 76)), seed=7.3, gloss=0.42, spec=0.32,
                 chip=(0.70, 0.76), rust=(0.99, 1.0), rust_low=0.0, dust=0.12, grime=0.10)
PLATE = dict(color=kmats.lin((222, 218, 200)), under=kmats.lin((58, 56, 54)), seed=5.1, gloss=0.45, spec=0.35,
             chip=(0.56, 0.62), rust=(0.58, 0.66), rust_low=1.0, floor_z=ZA, dust=0.3, grime=0.8)
KINDS.update({
    "crate": (build_paint_wood, dict(BLUE, along="x")),
    "crate_front": (build_paint_wood, dict(BLUE, along="x", decal_items=CRATE_FRONT)),
    "crate_y": (build_paint_wood, dict(BLUE, along="y", seed=2.7)),
    "crate_z": (build_paint_wood, dict(BLUE, along="z", seed=3.1, chip=(0.55, 0.61))),
    "gap": ("flat", dict(color=kmats.lin((44, 36, 28)), gloss=0.05, spec=0.03)),
    "dark": ("flat", dict(color=kmats.lin((14, 14, 14)), gloss=0.1, spec=0.05)),
    # nail heads: black steel, they rust
    "nail": ("paint", dict(color=kmats.lin((60, 58, 56)), under=kmats.lin((110, 60, 30)), seed=3.7, gloss=0.3,
                           spec=0.3, chip=(0.45, 0.55), rust=(0.40, 0.50), rust_low=0.5, dust=0.2, grime=0.5)),
    "rope": ("plastic", dict(color=kmats.lin((126, 104, 72)), gloss=0.06, spec=0.04, mottle=0.25, dust=0.3, grime=0.6,
                             scuff=(0.8, 0.9))),
    # hotplate enamel: old, cream, rust and dirt at the bottom (the hotplate bottom sits on the crate)
    "plate": ("paint", PLATE),
    "plate_front": ("paint", dict(PLATE, decal_items=PLATE_FRONT)),
    "plate_top": ("paint", dict(color=kmats.lin((214, 208, 188)), under=kmats.lin((58, 56, 54)), seed=5.7, gloss=0.4,
                                spec=0.3, chip=(0.54, 0.60), rust=(0.56, 0.64), rust_low=0.0, dust=0.35, grime=0.6,
                                yellow=0.6)),
    "ceramic": ("plastic", dict(color=kmats.lin((188, 170, 140)), gloss=0.12, spec=0.06, mottle=0.18, dust=0.2,
                                grime=0.65, scuff=(0.7, 0.8))),
    # burner coil: "off" - dark wire, "work" - glowing (atlas _on)
    "coil": ("flat", dict(color=kmats.lin((70, 62, 56)), gloss=0.3, spec=0.3)),
    "coil_on": ("flat", dict(color=kmats.lin((255, 96, 24)), gloss=0.3, spec=0.3)),
    "pilot": ("flat", dict(color=kmats.lin((80, 30, 14)), gloss=0.85, spec=0.8)),
    "pilot_on": ("flat", dict(color=kmats.lin((255, 120, 40)), gloss=0.85, spec=0.8)),
    "chrome": ("steel", dict(seed=6.1, tone=0.55, along="x", gloss=0.65, spec=0.8, dust=0.2, grime=0.45)),
    "knob": ("plastic", dict(color=kmats.lin((24, 23, 22)), gloss=0.45, spec=0.35, dust=0.1, grime=0.2,
                             scuff=(0.75, 0.85))),
    # hotplate cord in a cloth braid (like household appliances of the 70s)
    "cord_cloth": ("plastic", dict(color=kmats.lin((58, 46, 36)), gloss=0.06, spec=0.04, mottle=0.3, dust=0.3,
                                   grime=0.5, scuff=(0.8, 0.9))),
    # the cooker is clean (the Clear Sky instrument and workplace are clean): cast aluminium, slightly darker toward
    # the bottom
    "alu": ("steel", dict(seed=6.4, tone=0.66, along="z", gloss=0.40, spec=0.55, floor_z=ZC0, dust=0.06, grime=0.18)),
    "alu_lid": ("steel", dict(seed=6.9, tone=0.68, along="x", gloss=0.45, spec=0.6, dust=0.10, grime=0.05)),
    "alu_cast": ("steel", dict(seed=7.2, tone=0.56, along="z", gloss=0.35, spec=0.45, dust=0.1, grime=0.3)),
    "bakelite": ("plastic", dict(color=kmats.lin((22, 20, 19)), gloss=0.45, spec=0.35, dust=0.05, grime=0.1,
                                 scuff=(0.7, 0.8))),
    "gauge": (build_dial, dict(color=kmats.lin((236, 233, 222)), decal_items=GAUGE, gloss=0.6, spec=0.4)),
    "needle": ("flat", dict(color=kmats.lin((176, 32, 26)), gloss=0.5, spec=0.4)),
    # KFK-2: light grey enamel, dark blue cuvette compartment, housing sides and illuminator; clean
    "kfk": ("paint", KFK_PAINT),
    "kfk_front": ("paint", dict(KFK_PAINT, dust=0.08, decal_items=KFK_FRONT)),
    "kfk_blue": ("paint", dict(color=kmats.lin((40, 62, 92)), under=kmats.lin((150, 150, 150)), seed=7.9, gloss=0.42,
                               spec=0.32, chip=(0.68, 0.74), rust=(0.99, 1.0), rust_low=0.0, dust=0.12, grime=0.1)),
    "kfk_vent": ("steel", dict(seed=8.2, tone=0.66, along="x", holes=(("x", "y"), 0.011, 0.21), gloss=0.35, spec=0.3,
                               dust=0.2, grime=0.05)),
    "kfk_side_vent": ("steel", dict(seed=8.6, tone=0.12, along="z", holes=(("y", "z"), 0.016, 0.30), gloss=0.35,
                                    spec=0.3, dust=0.1, grime=0.05)),
    # scale window: "off" (the main atlas) and "work" (atlas _on, backlight)
    "scale": (build_dial, dict(color=kmats.lin((150, 150, 140)), decal_items=[rect("decal_scale_off.png", WIN, YSCALE, 0.0008)])),
    "scale_on": (build_dial, dict(color=kmats.lin((246, 240, 214)), decal_items=[rect("decal_scale_on.png", WIN, YSCALE, 0.0008)])),
    "needle_k": ("flat", dict(color=kmats.lin((20, 20, 20)), gloss=0.4, spec=0.3)),
    "tag": (build_dial, dict(color=kmats.lin((178, 182, 184)), decal_items=TAG_DECAL, gloss=0.5, spec=0.5)),
    # solutions in the cuvettes: reaction colours (pink, yellow)
    "liquid_a": ("flat", dict(color=kmats.lin((214, 84, 120)), gloss=0.7, spec=0.5)),
    "liquid_b": ("flat", dict(color=kmats.lin((222, 186, 60)), gloss=0.7, spec=0.5)),
    "rack": ("plastic", dict(color=kmats.lin((222, 222, 212)), gloss=0.35, spec=0.25, dust=0.2, grime=0.2)),
    "ext": ("plastic", dict(color=kmats.lin((214, 206, 186)), gloss=0.35, spec=0.25, mottle=0.08, dust=0.4, grime=0.7,
                            scuff=(0.64, 0.72))),
    "ext_plug": ("plastic", dict(color=kmats.lin((30, 27, 25)), gloss=0.4, spec=0.3, dust=0.3, grime=0.5,
                                 scuff=(0.7, 0.8))),
})

OBJ, NAME = "m08_sky_proc_bio", "ozr_sky_proc_bio"
# Work look: the KFK-2 scale window is ozl_screen, the burner coils, the hotplate lamp and the KFK-2
# indicator are ozl_lamp_work (both in hiddenSelections); "off" by default, "work" is atlas _on_co and
# rvmat _on with glow. Bones (OZL_WorkFx wobble, phase 0 is rest): the gauge needle ozl_needle, the
# weight valve ozl_weight, the KFK-2 needle ozl_meter - each on its own source.
SEL_SCREEN, SEL_LAMP = "ozl_screen", "ozl_lamp_work"
SEL_NEEDLE, SEL_WEIGHT, SEL_METER = "ozl_needle", "ozl_weight", "ozl_meter"
# move={} - preview of the "work" look without shifts; _turned recognises this look by it and poses the bones
ON = dict(remap={"scale": "scale_on", "coil": "coil_on", "pilot": "pilot_on"}, emissive=(1.0, 1.0, 1.0, 1.0), move={})
WEIGHT_TILT = 0.14                                          # weight tilt at phase 1, rad (8 degrees)
METER_SPAN = math.radians(L.SCALE_A[1] - L.SCALE_A[0])      # KFK-2 scale arc: 0..100 %
ANIMS = (
    ("ozl_needle", dict(type="rotation", source="ozl_needle", selection=SEL_NEEDLE, axis="ozl_needle_axis", memory=1,
                        minValue=0.0, maxValue=1.0, angle0=0.0, angle1=math.radians(L.GAUGE_SPAN))),
    ("ozl_weight", dict(type="rotation", source="ozl_weight", selection=SEL_WEIGHT, axis="ozl_weight_axis", memory=1,
                        minValue=0.0, maxValue=1.0, angle0=0.0, angle1=WEIGHT_TILT)),
    ("ozl_meter", dict(type="rotation", source="ozl_meter", selection=SEL_METER, axis="ozl_meter_axis", memory=1,
                       minValue=0.0, maxValue=1.0, angle0=0.0, angle1=METER_SPAN)),
)
# animPeriod of the sources: the gauge needle rises in ~0.8 s and keeps up with the slow breathing; the
# weight swings fast (2 swings per second) - the source keeps up within 0.1 s; the KFK-2 needle
# reaches its reading in ~1 s
SOURCES = {"ozl_needle": dict(animPeriod=3.0), "ozl_weight": dict(animPeriod=0.1), "ozl_meter": dict(animPeriod=1.5)}
MED = r"dz\gear\medical"
DECOR = [
    # behind the hotplate on the crate: water to top up the autoclave, iodine, disinfectant spray
    kv.put("waterbottle", (-0.470, 0.183, ZA), up=(0, 0, 1), fwd=(0.3, -1, 0)),
    kv.put(MED + r"\IodineTincture", (-0.388, 0.186, ZA), up=(0, 0, 1), fwd=(0, -1, 0)),
    kv.put(MED + r"\DisinfectantSpray", (-0.272, 0.192, ZA), up=(0, 0, 1), fwd=(0, -1, 0)),
    # in front of the hotplate: a thermometer between the knobs
    kv.put(MED + r"\med_tmeter", (-0.245, -0.205, ZA), **kv.flat(2)),
    # on the KFK-2 base at the left: a blood test kit
    kv.put(MED + r"\BloodTest_Kit", (KX0 + 0.075, KY0 + 0.052, ZKB), **kv.flat(14)),
    # GP-5 gas mask hangs on the rope handle of the left crate, facing out
    kv.put(r"dz\characters\masks\GP5GasMask_g", (XA0 - BT - 0.004, 0.0, 0.305), up=(0, 0, 1), fwd=(-1, 0, 0),
           normal=(-1, 0, 0)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.82, 0.86, 0.88), clear=0.05, edge=0.10, smudge=0.06, streaks=0.03),
                 selections=(SEL_SCREEN, SEL_LAMP, SEL_NEEDLE, SEL_WEIGHT, SEL_METER), hidden=(SEL_SCREEN, SEL_LAMP),
                 states={"on": ON}, bones=((SEL_NEEDLE, ""), (SEL_WEIGHT, ""), (SEL_METER, "")), animations=ANIMS,
                 decor=DECOR, sources=SOURCES)
P = M.part
BOUNDS = {}


# =============================================================================
# Primitives missing from kgeo
# =============================================================================
def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, from M04)."""
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


def use(part, region):
    """The following primitives of the part go into this region."""
    return part.use(region, *REGIONS[region])


def retag(part, region, pred):
    """Faces of the part for which pred(normal) holds go into another region (the face with a decal, the blue
    sides)."""
    part.bm.normal_update()
    idx = part.region_index(region, *REGIONS[region])
    for f in part.bm.faces:
        if pred(f.normal):
            f[part.reg] = idx


def axis_frame(o, n, u=(1.0, 0.0, 0.0)):
    """Right-handed system with axis n (the third axis of Frame): u is across, v = n x u."""
    n = Vector(n).normalized()
    u = Vector(u)
    u = (u - n * u.dot(n)).normalized()
    return g.Frame(o, u, n.cross(u), n)


Z_UP = (0.0, 0.0, 1.0)


def lathe(part, prof, sides, fr, a0=0.0):
    """Body of revolution about the axis n of the system fr: prof [(r, h)] - the profile along the outer
    side from bottom to top (so normals point outward); r = 0 is a pole (the bottom or top is closed by a fan)."""
    bm = part.bm
    rings = []
    for r, h in prof:
        if r < 1e-7:
            rings.append([bm.verts.new(fr.p(0.0, 0.0, h))])
        else:
            rings.append([bm.verts.new(fr.p(r * math.cos(a0 + 2 * math.pi * k / sides),
                                            r * math.sin(a0 + 2 * math.pi * k / sides), h)) for k in range(sides)])
    new = []
    for i in range(len(rings) - 1):
        r0, r1 = rings[i], rings[i + 1]
        if len(r0) == 1 and len(r1) == 1:
            continue
        for k in range(sides):
            j = (k + 1) % sides
            if len(r0) == 1:
                q = [r0[0], r1[j], r1[k]]
            elif len(r1) == 1:
                q = [r0[k], r0[j], r1[0]]
            else:
                q = [r0[k], r0[j], r1[j], r1[k]]
            new.append(bm.faces.new(q))
    part.tag(new)
    return new


def lathe_z(part, prof, sides, x, y, a0=0.0):
    """Body of revolution about the vertical through (x, y): h in the profile is the height z."""
    return lathe(part, prof, sides, g.Frame((x, y, 0.0), (1, 0, 0), (0, 1, 0), Z_UP), a0)


def rr_ring(x0, x1, y0, y1, r, n):
    """Rounded rectangle counter-clockwise (top view): n segments per corner, n = 0 - sharp corners."""
    if n <= 0:
        return [(x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    r = max(1e-4, min(r, (x1 - x0) / 2 - 1e-4, (y1 - y0) / 2 - 1e-4))
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90.0), (x1 - r, y1 - r, 0.0), (x0 + r, y1 - r, 90.0), (x0 + r, y0 + r, 180.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def rr_loft(part, rc, r, prof, n, top_region=None, cap_lo=True):
    """Body of rounded rectangles rc = (x0, x1, y0, y1) along the height: prof [(inset, z)] bottom to top -
    the inset of the rings rounds the edges (bent sheet, casting). The top is its own region top_region."""
    bm = part.bm
    x0, x1, y0, y1 = rc
    rings = []
    for d, z in prof:
        poly = rr_ring(x0 + d, x1 - d, y0 + d, y1 - d, max(r - d, 0.0015), n)
        rings.append([bm.verts.new((a, b, z)) for a, b in poly])
    m = len(rings[0])
    new = []
    for i in range(len(rings) - 1):
        for k in range(m):
            j = (k + 1) % m
            new.append(bm.faces.new([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]))
    if cap_lo:
        new.append(bm.faces.new(rings[0][::-1]))
    part.tag(new)
    top = bm.faces.new(rings[-1])
    part.tag([top], part.region_index(top_region, *REGIONS[top_region]) if top_region else None)
    return new + [top]


def knurl(part, fr, r, depth, n, h0, h1):
    """Knurled belt about the axis n of the system fr: 2n vertices on a circle, every other one sunk by depth."""
    poly = [((r - depth * (k % 2)) * math.cos(math.pi * k / n), (r - depth * (k % 2)) * math.sin(math.pi * k / n))
            for k in range(2 * n)]
    return g.prism(part, poly, (0, 1), h0, h1, frame=fr)


def hexagon(part, fr, r, h0, h1):
    """Hexagon (nut) about the axis n of the system fr."""
    poly = [(r * math.cos(math.pi * k / 3 + math.pi / 6), r * math.sin(math.pi * k / 3 + math.pi / 6)) for k in range(6)]
    return g.prism(part, poly, (0, 1), h0, h1, frame=fr)


def rod(part, a, b, r, sides):
    return g.pipe(part, [tuple(a), tuple(b)], r, sides)


def radial(a, x=XC, y=YC):
    """System at the cooker axis at angle a: u is tangent, v is up (z), n is outward."""
    return g.Frame((x, y, 0.0), (-math.sin(a), math.cos(a), 0.0), Z_UP, (math.cos(a), math.sin(a), 0.0))


def screw(part, fr, x, y, h, r=0.0032, sides=6):
    """Screw with a round head: (x, y) in the u-v plane of the system fr, h along the normal."""
    f2 = g.Frame(fr.p(x, y, h), fr.u, fr.v, fr.n)
    return lathe(part, [(r, 0.0), (r * 0.7, r * 0.35), (0.0, r * 0.42)], sides, f2)


def cable(name, region, pts, r, lod, k=4):
    """Smooth-curve cord (middle LOD - by the points themselves, far LOD - no cord)."""
    if lod == 2:
        return []
    c = P(name, region)
    g.pipe(c, spline(pts, k) if lod == 0 else pts, r, 5 if lod == 0 else 4)
    return [c]


# =============================================================================
# Crates
# =============================================================================
def nail(part, p, axis):
    """Nail head of diameter 7 on a face: axis is "x" or "y" (the face normal), p is the head centre."""
    g.cyl(part, tuple(p), axis, 0.0035, 0.0014, 4)


def crate(name, x0, x1, y0, y1, h, lod, front_region, rope_end, top_bev, rnd):
    """Plank crate: boards of the face, back, ends and lid with gaps (edges rounded, the fit slightly
    different), a frame of battens on the face and back, two posts on the ends; on the end rope_end (-1
    left, 1 right) two blocks and a rope handle, on the other a block (it is in the gap between the
    crates). Rounding only on the visible parts (the face, the end with the handle, the lid with
    top_bev), nails on the posts of the face and the end with the handle. Middle LOD - a box, boards and
    a face frame, end posts; far - a box."""
    if lod == 2:
        b = P(name, "crate")
        g.box(b, x0, x1, y0 - BT, y1 + BT, 0.0, h)
        return [b]
    n = max(3, int(round(h / 0.14)))
    gap = 0.007
    bw = (h - gap * (n - 1)) / n
    zs = []
    for i in range(n):
        z0 = i * (bw + gap)
        zs.append((z0, min(h - BOARD if i == n - 1 else h, z0 + bw)))
    w, wr = 0.05, 0.055
    yc = (y0 + y1) / 2
    xe = x0 if rope_end < 0 else x1                       # end with the handle
    se = -1 if rope_end < 0 else 1
    if lod == 1:
        b = P(name + "_body", "crate")
        g.box(b, x0 + 0.003, x1 - 0.003, y0 + 0.003, y1 - 0.003, 0.0, h)
        fr = P(name + "_front", front_region)
        for z0, z1 in zs:
            g.box(fr, x0, x1, y0, y0 + BOARD, z0, z1)
        bt = P(name + "_battens", "crate_z")
        for xa in (x0, x1 - w):
            g.box(bt, xa, xa + w, y0 - BT, y0, 0.0, h)
        for za in (0.0, h - wr):
            g.box(bt, x0 + w, x1 - w, y0 - BT, y0, za, za + wr)
        xa, xb = sorted((xe, xe + se * BT))
        for ya, yb in ((y0 + 0.03, y0 + 0.07), (y1 - 0.07, y1 - 0.03)):
            g.box(bt, xa, xb, ya, yb, 0.0, h)
        ca, cb = sorted((xe, xe + se * 0.024))
        g.box(bt, ca, cb, yc - 0.073, yc + 0.073, h - 0.125, h - 0.075)
        return [b, fr, bt]
    bev = dict(r=0.0025, seg=1)
    core = P(name + "_core", "gap")
    g.box(core, x0 + 0.004, x1 - 0.004, y0 + 0.004, y1 - 0.004, 0.0, h - 0.004)
    fr = P(name + "_front", front_region)
    bk = P(name + "_back", "crate")
    en = P(name + "_ends", "crate_y")
    tp = P(name + "_top", "crate")

    def j():
        return rnd.uniform(-0.0012, 0.0012)
    for z0, z1 in zs:
        g.box(fr, x0, x1, y0 + j(), y0 + BOARD, z0, z1, **bev)
        g.box(bk, x0, x1, y1 - BOARD, y1, z0, z1)
        for xx, s_ in ((x0, -1), (x1, 1)):
            xa, xb = sorted((xx, xx - s_ * BOARD))
            if s_ == se:
                g.box(en, xa + (j() if s_ < 0 else 0.0), xb + (j() if s_ > 0 else 0.0), y0 + BOARD, y1 - BOARD, z0, z1, **bev)
            else:
                g.box(en, xa, xb, y0 + BOARD, y1 - BOARD, z0, z1)
    m = max(3, int(round((y1 - y0) / 0.12)))
    tw = ((y1 - y0) - gap * (m - 1)) / m
    for k in range(m):
        ya = y0 + k * (tw + gap)
        g.box(tp, x0, x1, ya, ya + tw, h - BOARD, h + rnd.uniform(0.0, 0.0012), **(bev if top_bev else {}))
    parts = [core, fr, bk, en, tp]
    # face and back frame: corner posts and top and bottom battens between them
    bt = P(name + "_battens", "crate_z")
    rl = P(name + "_rails", "crate")
    for yy, s_ in ((y0, -1), (y1, 1)):
        ya, yb = sorted((yy, yy + s_ * BT))
        b_ = bev if s_ < 0 else {}
        for xa in (x0, x1 - w):
            g.box(bt, xa, xa + w, ya, yb, 0.0, h, **b_)
        for za in (0.0, h - wr):
            g.box(rl, x0 + w, x1 - w, ya, yb, za, za + wr, **b_)
    parts += [bt, rl]
    # ends: two posts; on the end with the handle two blocks, on the other one block
    eb = P(name + "_end_battens", "crate_z")
    cl = P(name + "_cleats", "crate_y")
    for xx, s_ in ((x0, -1), (x1, 1)):
        xa, xb = sorted((xx, xx + s_ * BT))
        b_ = bev if s_ == se else {}
        for ya, yb in ((y0 + 0.03, y0 + 0.07), (y1 - 0.07, y1 - 0.03)):
            g.box(eb, xa, xb, ya, yb, 0.0, h, **b_)
        if s_ == se:
            ca, cb = sorted((xx, xx + s_ * 0.024))
            for dy in (-0.055, 0.055):
                g.box(cl, ca, cb, yc + dy - 0.018, yc + dy + 0.018, h - 0.125, h - 0.075, **bev)
        else:
            g.box(cl, xa, xb, y0 + 0.07, y1 - 0.07, h - 0.13, h - 0.08)
    parts += [eb, cl]
    # nails: one per board in each post of the face and of the end with the handle
    nl = P(name + "_nails", "nail")
    for xa in (x0 + w / 2, x1 - w / 2):
        for z0, z1 in zs:
            nail(nl, (xa, y0 - BT - 0.0004, (z0 + z1) / 2), "y")
    xn = xe + se * (BT + 0.0004)
    for ya in (y0 + 0.05, y1 - 0.05):
        for z0, z1 in zs:
            nail(nl, (xn, ya, (z0 + z1) / 2), "x")
    parts.append(nl)
    # rope handle: knots on the blocks, the loop sags
    rp = P(name + "_rope", "rope")
    xr, xo = xe + se * 0.012, xe + se * 0.016
    pts = [(xr, yc - 0.055, h - 0.068), (xr, yc - 0.055, h - 0.100), (xr, yc - 0.055, h - 0.128),
           (xo, yc - 0.046, h - 0.160), (xo, yc - 0.022, h - 0.181), (xo, yc, h - 0.186),
           (xo, yc + 0.022, h - 0.181), (xo, yc + 0.046, h - 0.160), (xr, yc + 0.055, h - 0.128),
           (xr, yc + 0.055, h - 0.100), (xr, yc + 0.055, h - 0.068)]
    g.pipe(rp, spline(pts, 2), 0.0055, 5)
    for dy in (-0.055, 0.055):
        lathe_z(rp, [(0.0, h - 0.0752), (0.0070, h - 0.0745), (0.0108, h - 0.0712), (0.0110, h - 0.0668),
                     (0.0082, h - 0.0626), (0.0, h - 0.0612)], 8, xr, yc + dy, a0=0.4)
    parts.append(rp)
    return parts


def build_crates(spec):
    lod = spec["lod"]
    rnd = random.Random(8)
    return (crate("crate_a", XA0, XA1, YA0, YA1, ZA, lod, "crate_front", -1, True, rnd) +
            crate("crate_b", XB0, XB1, YB0, YB1, ZB, lod, "crate", 1, False, rnd))


# =============================================================================
# Hotplate
# =============================================================================
def spiral_pts(x, y, z, r0, r1, turns, per_turn):
    n = int(turns * per_turn)
    return [(x + (r0 + (r1 - r0) * k / n) * math.cos(2 * math.pi * k / per_turn),
             y + (r0 + (r1 - r0) * k / n) * math.sin(2 * math.pi * k / per_turn), z) for k in range(n + 1)]


def knob(parts, name, cx, y_face, cz, r, lod, point_deg, region="knob", mark=True):
    """Bakelite knob on the face (axis toward the person): a skirt, a knurled belt, an end with a white
    mark at point_deg (from +x counter-clockwise, front view)."""
    fr = axis_frame((cx, y_face, cz), (0, -1, 0))
    kb = P(name, region)
    if lod == 0:
        big = r > 0.015
        lathe(kb, [(r, -0.001), (r, 0.0032), (r * 0.80, 0.0048)], 14 if big else 12, fr)
        knurl(kb, fr, r * 0.80, r * 0.06, 9 if big else 8, 0.0046, r * 1.05)
        lathe(kb, [(r * 0.76, r * 1.05), (r * 0.70, r * 1.15), (0.0, r * 1.18)], 14 if big else 12, fr)
    else:
        lathe(kb, [(r, -0.001), (r * 0.8, r * 1.1), (0.0, r * 1.15)], 8, fr)
    parts.append(kb)
    if lod == 0 and mark:
        mk = P(name + "_mark", "knob_mark")
        a = math.radians(point_deg)
        d = fr.u * math.cos(a) + fr.v * math.sin(a)
        f2 = g.Frame(fr.o, d, d.cross(fr.n) * -1.0, fr.n)
        g.box(mk, r * 0.12, r * 0.70, -r * 0.08, r * 0.08, r * 1.165, r * 1.20, frame=f2)
        parts.append(mk)


def lamp(parts, name, cx, y_face, cz, r, lod):
    """Lamp in a chrome rim on the face: the lens is ozl_lamp_work (glows in "work")."""
    fr = axis_frame((cx, y_face, cz), (0, -1, 0))
    if lod == 0:
        bz = P(name + "_bezel", "chrome")
        lathe(bz, [(r * 1.45, -0.001), (r * 1.45, 0.0018), (r * 1.02, 0.0032)], 12, fr)
        parts.append(bz)
    ln = P(name, "pilot", group=SEL_LAMP)
    if lod == 0:
        lathe(ln, [(r, 0.0020), (r * 0.92, 0.0050), (r * 0.5, 0.0071), (0.0, 0.0075)], 10, fr)
    else:
        lathe(ln, [(r * 1.2, -0.001), (r, 0.004), (0.0, 0.006)], 6 if lod == 1 else 4, fr)
    parts.append(ln)


def build_plate(spec):
    lod, sd = spec["lod"], spec["sides"]
    x0, x1, y0, y1 = XP - PW / 2, XP + PW / 2, YP - PD / 2, YP + PD / 2
    parts = []
    body = P("plate_body", "plate")
    if lod == 2:
        g.box(body, x0, x1, y0, y1, ZP0, ZPT)
        parts.append(body)
        for bx, br in BURN:
            cr = P("burner_far%d" % len(parts), "ceramic")
            g.cyl(cr, (bx, YBN, ZPT + 0.002), "z", br, 0.004, 8)
            parts.append(cr)
        return parts
    prof = ([(0.004, ZP0), (0.0, ZP0 + 0.005), (0.0, ZPT - 0.009), (0.0025, ZPT - 0.0025), (0.008, ZPT)] if lod == 0
            else [(0.0, ZP0), (0.0, ZPT)])
    rr_loft(body, (x0, x1, y0, y1), 0.024, prof, 4 if lod == 0 else 1, top_region="plate_top")
    retag(body, "plate_front", lambda nrm: nrm.y < -0.9)
    parts.append(body)
    for i, (bx, br) in enumerate(BURN):
        # chrome ring, ceramic with a disc in the middle, a coil in a groove (ozl_lamp_work)
        rim = P("burner_rim%d" % i, "chrome")
        lathe_z(rim, [(br + 0.011, ZPT - 0.0008), (br + 0.008, ZPT + 0.0032), (br + 0.002, ZPT + 0.0044),
                      (br - 0.0015, ZPT + 0.0008)], sd, bx, YBN)
        cr = P("burner%d" % i, "ceramic")
        lathe_z(cr, [(br - 0.0005, ZPT + 0.0005), (br - 0.003, ZCER), (0.0, ZCER)], sd, bx, YBN)
        parts += [rim, cr]
        cl = P("coil%d" % i, "coil", group=SEL_LAMP)
        if lod == 0:
            turns, per = (3.0, 20) if i == 0 else (2.0, 10)
            g.pipe(cl, spiral_pts(bx, YBN, ZCOIL, 0.019, br - 0.011, turns, per), 0.0024, 4)
            hub = P("burner_hub%d" % i, "chrome")
            lathe_z(hub, [(0.0125, ZCER - 0.0004), (0.0115, ZCER + 0.0022), (0.007, ZCER + 0.0032), (0.0, ZCER + 0.0034)],
                    12, bx, YBN)
            parts.append(hub)
        elif i == 0:
            g.pipe(cl, spiral_pts(bx, YBN, ZCOIL, 0.019, br - 0.012, 2.0, 8), 0.003, 3)
        else:
            g.cyl(cl, (bx, YBN, ZCER + 0.0006), "z", br - 0.012, 0.0012, sd)
        parts.append(cl)
    # step switch knobs and the lamp on the face
    for i, (bx, _) in enumerate(BURN):
        knob(parts, "plate_knob%d" % i, bx, y0, L.PKNOB_Z, L.PKNOB_R, lod, (110.0, 30.0)[i])
    lamp(parts, "plate_pilot", L.PILOT[0], y0, L.PILOT[1], 0.0060, lod)
    if lod == 0:
        ft = P("plate_feet", "rubber")
        for x in (x0 + 0.03, x1 - 0.03):
            for y in (y0 + 0.03, y1 - 0.03):
                lathe_z(ft, [(0.0, ZA), (0.012, ZA), (0.0095, ZP0 + 0.001), (0.0, ZP0 + 0.001)], 8, x, y)
        parts.append(ft)
        # slots on the sides of the body
        sl = P("plate_slots", "dark")
        for xx, s in ((x0, -1), (x1, 1)):
            for k in range(3):
                yk = YP - 0.05 + k * 0.05
                xa, xb = sorted((xx, xx + s * 0.0006))
                g.box(sl, xa, xb, yk - 0.013, yk + 0.013, ZP0 + 0.030, ZP0 + 0.036)
        parts.append(sl)
        # cord entry: a rubber grommet at the back right
        gr = P("plate_grommet", "rubber")
        lathe(gr, [(0.0075, -0.001), (0.0072, 0.006), (0.0058, 0.016), (0.0048, 0.028)], 10,
              axis_frame((x1 - 0.06, y1, ZP0 + 0.030), (0, 1, 0)))
        parts.append(gr)
    # hotplate cord (cloth braid): from the back over the crate edge down, along the floor into the gap
    # between the crates and to the plug in the extension
    px, py = EXT.x + SOCKETS[0], EXT.y
    cx = CORD_X[0]
    yb = YA1 + BT + 0.0045                                  # crate back (by the battens)
    pts = [(x1 - 0.06, y1 + 0.026, ZP0 + 0.030), (x1 - 0.058, y1 + 0.060, ZP0 + 0.008), (x1 - 0.054, yb - 0.002, ZA + 0.006),
           (x1 - 0.050, yb + 0.002, ZA - 0.035), (x1 - 0.040, yb + 0.001, 0.30), (x1 - 0.020, yb + 0.002, 0.07),
           (x1 + 0.010, yb + 0.012, 0.0045), (cx - 0.012, yb + 0.010, 0.0045), (cx, YA1 + 0.004, 0.0045),
           (cx, 0.05, 0.0045), (cx, YA0 - 0.04, 0.0045), (px + 0.012, py + 0.075, 0.0045), (px + 0.003, py + 0.024, 0.022),
           (px, py + 0.008, PLUG_TOP + 0.006), (px, py, PLUG_TOP - 0.004)]
    parts += cable("plate_cord", "cord_cloth", pts, 0.0042, lod, 2)
    return parts


# =============================================================================
# Pressure-cooker autoclave
# =============================================================================
def build_cooker(spec):
    lod, sd = spec["lod"], spec["sides"]
    ax = g.Frame((XC, YC, 0.0), (1, 0, 0), (0, 1, 0), Z_UP)
    parts = []
    body = P("cooker_body", "alu")
    if lod == 0:
        prof = [(0.0, ZC0), (RC_ - 0.014, ZC0), (RC_ - 0.004, ZC0 + 0.002), (RC_, ZC0 + 0.010), (RC_, ZC1 - 0.034),
                (RC_ + 0.004, ZC1 - 0.028), (RC_ + 0.011, ZC1 - 0.023), (RC_ + 0.012, ZC1 - 0.003), (RC_ + 0.010, ZC1),
                (RC_ - 0.006, ZC1), (0.0, ZC1)]
    elif lod == 1:
        prof = [(0.0, ZC0), (RC_ - 0.006, ZC0), (RC_, ZC0 + 0.008), (RC_, ZC1 - 0.026), (RC_ + 0.012, ZC1 - 0.020),
                (RC_ + 0.012, ZC1), (0.0, ZC1)]
    else:
        prof = [(0.0, ZC0), (RC_, ZC0), (RC_, ZC1), (0.0, ZC1)]
    lathe(body, prof, sd, ax)
    parts.append(body)
    lid = P("cooker_lid", "alu_lid")
    if lod < 2:
        prof = [(0.0, ZC1 + 0.0005), (RF, ZC1 + 0.0005), (RF, ZF1 - 0.003), (RF - 0.003, ZF1), (RF - 0.014, ZF1 + 0.001),
                (0.162, ZF1 + 0.009), (0.150, ZF1 + 0.022), (0.136, ZF1 + 0.034), (0.120, ZF1 + 0.043),
                (0.100, ZF1 + 0.049), (0.070, ZD), (0.0, ZD + 0.002)]
        if lod == 1:
            prof = prof[:5] + prof[6::2] + [prof[-1]]
    else:
        prof = [(0.0, ZC1), (RF, ZC1), (RF, ZF1), (0.10, ZD), (0.0, ZD)]
    lathe(lid, prof, sd, ax)
    parts.append(lid)
    if lod < 2:
        parts += build_clamps(lod)
    parts += build_handle(lod)
    if lod < 2:
        parts += build_valves(lod)
    return parts


def build_clamps(lod):
    """Six clamps: on the lid a fork lug in the flange, on the body a fork boss with an axle; a swing bolt
    with an eye on the axle passes into the lid fork, on top a washer and a wing nut (hub and a T-shaped wing)."""
    ears = P("cooker_ears", "alu_cast")
    wings = P("cooker_wings", "bakelite")
    parts = [ears, wings]
    if lod == 0:
        lugs = P("cooker_lugs", "alu_cast")
        bolts = P("cooker_bolts", "steel")
        parts += [lugs, bolts]
    zp = ZC1 - 0.022                                            # bolt hinge axis
    for a in CLAMPS:
        f = radial(a)
        if lod == 1:
            g.box(ears, -0.0125, 0.0125, ZC1, ZF1, RF - 0.006, RCL + 0.014, frame=f)
            g.box(wings, -0.030, 0.030, ZF1 + 0.012, ZF1 + 0.040, RCL - 0.005, RCL + 0.005, frame=f)
            continue
        # fork in the lid: two teeth and a bridge at the flange
        for s_ in (-1, 1):
            g.box(ears, *sorted((s_ * 0.0055, s_ * 0.0125)), ZC1 + 0.0005, ZF1, RF - 0.006, RCL + 0.014, frame=f)
        g.box(ears, -0.0125, 0.0125, ZC1 + 0.0005, ZF1, RF - 0.006, RF + 0.007, frame=f)
        # boss on the body: two cheeks; the bolt runs from the axle between the cheeks to the wing nut
        for s_ in (-1, 1):
            g.box(lugs, *sorted((s_ * 0.0055, s_ * 0.0115)), ZC1 - 0.042, ZC1 - 0.006, RC_ - 0.003, RCL + 0.009, frame=f)
        pin = f.p(0.0, zp, RCL)
        rod(bolts, pin, f.p(0.0, ZF1 + 0.004, RCL), 0.0045, 6)
        c = f.p(0.0, 0.0, RCL)
        # wing nut: hub (the bottom is a washer) and a T wing with a sloped bottom
        lathe_z(wings, [(0.0, ZF1 - 0.0002), (0.0108, ZF1 - 0.0002), (0.0104, ZF1 + 0.021), (0.0078, ZF1 + 0.0265),
                        (0.0, ZF1 + 0.0265)], 8, c.x, c.y)
        g.prism(wings, WING, (0, 1), RCL - 0.0055, RCL + 0.0055, frame=f)
    return parts


# wing nut outline (u, z): a T with a sloped bottom, rounded top corners
WING = [(0.012, ZF1 + 0.016), (0.033, ZF1 + 0.030), (0.0335, ZF1 + 0.0375), (0.0315, ZF1 + 0.041), (0.028, ZF1 + 0.042),
        (-0.028, ZF1 + 0.042), (-0.0315, ZF1 + 0.041), (-0.0335, ZF1 + 0.0375), (-0.033, ZF1 + 0.030), (-0.012, ZF1 + 0.016)]


def build_handle(lod):
    """Bakelite handle on the lid: finger grooves below, rounded ends; wire brackets in the lid bosses."""
    yh = YC + 0.02
    hd = P("cooker_handle", "bakelite")
    if lod == 2:
        g.box(hd, XC - 0.095, XC + 0.095, yh - 0.012, yh + 0.012, ZD, ZD + 0.083)
        return [hd]
    n = 15 if lod == 0 else 7
    pts, radii = [], []
    for i in range(n):
        u = -1.0 + 2.0 * i / (n - 1)
        x = XC + 0.098 * u
        top = ZD + 0.086 - 0.007 * u * u
        hgt = 0.024
        if lod == 0 and abs(u) < 0.78:
            hgt -= 0.006 * max(0.0, math.cos(4.0 * math.pi * 0.098 * u / 0.155)) ** 2
        rx = 0.0135
        if abs(u) > 0.9:                                        # rounded ends
            k = (1.0 - abs(u)) / 0.1
            rx, hgt = 0.007 + 0.0065 * k, hgt * (0.55 + 0.45 * k)
        pts.append((x, yh, top - hgt / 2))
        radii.append((rx, hgt / 2))
    g.tube_var(hd, pts, radii, 8 if lod == 0 else 6)
    parts = [hd]
    st = P("cooker_handle_wire", "steel")
    for s in (-1, 1):
        wp = [(XC + s * 0.078, yh, ZD - 0.002), (XC + s * 0.084, yh, ZD + 0.022), (XC + s * 0.091, yh, ZD + 0.046),
              (XC + s * 0.088, yh, ZD + 0.066)]
        g.pipe(st, spline(wp, 2) if lod == 0 else wp, 0.0032, 5 if lod == 0 else 4)
        if lod == 0:
            lathe_z(st, [(0.0, ZD - 0.006), (0.0115, ZD - 0.006), (0.0100, ZD + 0.005), (0.0, ZD + 0.0072)],
                    10, XC + s * 0.078, yh)
    parts.append(st)
    return parts


def build_valves(lod):
    """Weight valve at the front right: a nut, a tube, a weight (bone ozl_weight, swings on the top of the
    tube) with three holes; at the back a petcock with a lever and a safety plug."""
    parts = []
    vl = P("cooker_vent", "steel")
    hexagon(vl, g.Frame((VX, VY, 0.0), (1, 0, 0), (0, 1, 0), Z_UP), 0.0085, ZLID_V - 0.002, ZLID_V + 0.006)
    g.cyl(vl, (VX, VY, (ZLID_V + 0.006 + ZPIPE) / 2), "z", 0.0032, ZPIPE - ZLID_V - 0.006, 8)
    parts.append(vl)
    wt = P("cooker_weight", "steel", group=SEL_WEIGHT)
    zw = ZPIPE - 0.020                                          # bottom of the weight: it is slid onto the tube
    if lod == 0:
        lathe_z(wt, [(0.0, zw), (0.0135, zw), (0.0152, zw + 0.003), (0.0152, zw + 0.019), (0.0128, zw + 0.023),
                     (0.0062, zw + 0.025), (0.0056, zw + 0.031), (0.0, zw + 0.032)], 14, VX, VY)
        ho = P("cooker_weight_holes", "dark", group=SEL_WEIGHT)
        for k in range(3):
            a = math.radians(-90.0 + 120.0 * k)
            d = Vector((math.cos(a), math.sin(a), 0.0))
            c = Vector((VX, VY, zw + 0.011)) + d * 0.0150
            rod(ho, c - d * 0.0004, c + d * 0.0006, 0.0018 + 0.0006 * k, 6)
        parts.append(ho)
    else:
        lathe_z(wt, [(0.0, zw), (0.015, zw), (0.015, zw + 0.022), (0.0, zw + 0.03)], 8, VX, VY)
    parts.append(wt)
    if lod == 0:
        # petcock at the back left: body and lever
        pc = P("cooker_petcock", "steel")
        cx, cy = XC - 0.030, YC + 0.085
        lathe_z(pc, [(0.0, ZLID_V - 0.002), (0.0075, ZLID_V - 0.002), (0.0070, ZLID_V + 0.010), (0.0055, ZLID_V + 0.012),
                     (0.0055, ZLID_V + 0.024), (0.0, ZLID_V + 0.025)], 10, cx, cy)
        g.box(pc, cx - 0.002, cx + 0.032, cy - 0.003, cy + 0.003, ZLID_V + 0.017, ZLID_V + 0.021, r=0.001, seg=1)
        parts.append(pc)
        # safety plug: black rubber mushroom
        pl = P("cooker_plug", "rubber")
        lathe_z(pl, [(0.0, ZLID_V - 0.002), (0.0065, ZLID_V - 0.002), (0.0065, ZLID_V + 0.004), (0.0092, ZLID_V + 0.005),
                     (0.0088, ZLID_V + 0.009), (0.0, ZLID_V + 0.0105)], 12, XC + 0.042, YC + 0.080)
        parts.append(pl)
    return parts


def build_gauge(spec):
    """Gauge on a post: a chrome case with a rim, a dial in the depth, glass, the needle (bone ozl_needle)
    between them; a post with a nut in the lid."""
    lod = spec["lod"]
    n = (20, 12, 8)[lod]
    fr = axis_frame((GX, YG_BACK, GZ), (0, -1, 0))
    parts = []
    cs = P("gauge_case", "chrome")
    if lod == 0:
        lathe(cs, [(0.0, 0.0), (GR - 0.006, 0.0), (GR, 0.0050), (GR, GDEP - 0.0045), (GR + 0.0023, GDEP - 0.0030),
                   (GR + 0.0012, GDEP + 0.0004), (GR - 0.0035, GDEP - 0.0006), (GR - 0.0038, GDEP - 0.0040)], n, fr)
        st = P("gauge_stem", "steel")
        g.cyl(st, (GX, GY, (ZD + GZ - GR) / 2), "z", 0.0042, GZ - GR - ZD + 0.004, 8)
        hexagon(st, g.Frame((GX, GY, 0.0), (1, 0, 0), (0, 1, 0), Z_UP), 0.0085, ZD - 0.004, ZD + 0.005)
        hexagon(st, g.Frame((GX, GY, 0.0), (1, 0, 0), (0, 1, 0), Z_UP), 0.0065, GZ - GR - 0.008, GZ - GR + 0.002)
        parts.append(st)
    elif lod == 1:
        lathe(cs, [(0.0, 0.0), (GR, 0.0), (GR, GDEP), (GR - 0.004, GDEP - 0.004)], n, fr)
        g.cyl(cs, (GX, GY, (ZD + GZ - GR) / 2), "z", 0.0045, GZ - GR - ZD + 0.004, 4)
    else:
        lathe(cs, [(0.0, 0.0), (GR, 0.0), (GR, GDEP), (0.0, GDEP)], n, fr)
    parts.append(cs)
    if lod == 2:
        return parts
    fc = P("gauge_face", "gauge")
    lathe(fc, [(GR - 0.0036, GDEP - 0.0042), (0.0, GDEP - 0.0042)], n, fr)
    parts.append(fc)
    if lod == 0:
        gl = P("gauge_glass", "steel", section="glass")
        lathe(gl, [(GR - 0.0032, GDEP - 0.0008), (0.0, GDEP - 0.0008)], n, fr)
        gl.glass_frame = (g.Frame((GX, YDIAL, GZ), (1, 0, 0), Z_UP, (0, -1, 0)), -GR, GR, -GR, GR)
        parts.append(gl)
    # needle at zero points left-down (225 degrees, as the dial): a blade and a cap
    nd = P("gauge_needle", "needle", group=SEL_NEEDLE)
    a = math.radians(L.GAUGE_ZERO)
    d = fr.u * math.cos(a) + fr.v * math.sin(a)
    c = fr.p(0.0, 0.0, GDEP - 0.0028)
    f2 = g.Frame(c, d, fr.n.cross(d), fr.n)
    poly = [(-0.0075, -0.0017), (GR * 0.80, -0.0005), (GR * 0.84, 0.0), (GR * 0.80, 0.0005), (-0.0075, 0.0017)]
    g.prism(nd, poly, (0, 1), -0.0003, 0.0003, frame=f2)
    if lod == 0:
        lathe(nd, [(0.0032, 0.0002), (0.0030, 0.0010), (0.0, 0.0013)], 10, g.Frame(c, fr.u, fr.v, fr.n))
    parts.append(nd)
    return parts


# =============================================================================
# KFK-2 photocolorimeter
# =============================================================================
def build_kfk(spec):
    lod, sd = spec["lod"], spec["sides"]
    x0, x1, y0, y1 = KX0, KX1, KY0, KY1
    zb = ZKB
    cx0, cx1 = L.CUV
    hx0, hx1 = XK - HOUSE_W / 2, XK + HOUSE_W / 2
    zt = ZK0 + KH
    parts = []
    base = P("kfk_base", "kfk")
    if lod == 2:
        g.box(base, x0, x1, y0, y1, ZK0, zb)
        g.box(base, cx0, cx1, y0 - 0.006, YK + 0.02, ZK0 + 0.02, zb + 0.04)
        g.box(base, hx0, hx1, YWIN, YK + 0.14, zb, zt)
        g.box(base, x0 - 0.045, x0, y0 + 0.05, y1 - 0.08, ZK0 + 0.022, zb - 0.012)
        return [base]
    prof = ([(0.003, ZK0), (0.0, ZK0 + 0.004), (0.0, zb - 0.006), (0.0025, zb - 0.0015), (0.006, zb)] if lod == 0
            else [(0.0, ZK0), (0.0, zb)])
    rr_loft(base, (x0, x1, y0, y1), L.KR, prof, 4 if lod == 0 else 1)
    retag(base, "kfk_front", lambda nrm: nrm.y < -0.9)
    parts.append(base)
    # cuvette compartment in the middle: blue, rounded at the front; a hinged lid, a tab handle
    cu = P("kfk_cuvette", "kfk_blue")
    rr_loft(cu, (cx0, cx1, y0 - 0.006, YK + 0.020), 0.022,
            [(0.0, ZK0 + 0.018), (0.0, zb + 0.036), (0.003, zb + 0.040)] if lod == 0 else [(0.0, ZK0 + 0.018), (0.0, zb + 0.040)],
            4 if lod == 0 else 1)
    parts.append(cu)
    cl = P("kfk_cuvette_lid", "kfk")
    bv = dict(r=0.0012, seg=1) if lod == 0 else {}
    g.box(cl, cx0 - 0.004, cx1 + 0.004, y0 - 0.010, YK + 0.024, zb + 0.040, zb + 0.043, **bv)
    if lod == 0:
        g.box(cl, cx0 - 0.004, cx1 + 0.004, y0 - 0.010, y0 - 0.0075, zb + 0.028, zb + 0.043, **bv)
        g.box(cl, XK - 0.016, XK + 0.016, y0 - 0.017, y0 - 0.010, zb + 0.031, zb + 0.042, r=0.002, seg=1)
    parts.append(cl)
    # scale housing: a profile with a rounded back, blue sides; the face is a frame around the window (the
    # window is deep: behind the glass the needle, behind it the scale)
    hs = P("kfk_scale_house", "kfk")
    yb = YK + 0.140
    if lod == 0:
        rb = 0.045
        poly = [(YWIN + 0.010, zb - 0.004), (yb, zb - 0.004)]
        poly += [(yb - rb + rb * math.cos(math.radians(a)), zt - rb + rb * math.sin(math.radians(a))) for a in range(0, 91, 15)]
        poly += [(YWIN + 0.010, zt)]
    else:
        poly = [(YWIN + 0.010, zb - 0.004), (yb, zb - 0.004), (yb, zt - 0.03), (yb - 0.03, zt), (YWIN + 0.010, zt)]
    g.prism(hs, poly, (1, 2), hx0, hx1)
    retag(hs, "kfk_blue", lambda nrm: abs(nrm.x) > 0.9)
    bz = P("kfk_bezel", "kfk")
    bvb = dict(r=0.0015, seg=1) if lod == 0 else {}
    g.box(bz, hx0, hx1, YWIN, YWIN + 0.0105, zb - 0.004, WIN[2], **bvb)
    g.box(bz, hx0, hx1, YWIN, YWIN + 0.0105, WIN[3], zt, **bvb)
    g.box(bz, hx0, WIN[0], YWIN, YWIN + 0.0105, WIN[2] - 0.002, WIN[3] + 0.002, **bvb)
    g.box(bz, WIN[1], hx1, YWIN, YWIN + 0.0105, WIN[2] - 0.002, WIN[3] + 0.002, **bvb)
    parts += [hs, bz]
    tr = P("kfk_window_trim", "kfk_blue")
    t = 0.006
    for a0, a1, b0, b1 in ((WIN[0] - t, WIN[1] + t, WIN[3], WIN[3] + t), (WIN[0] - t, WIN[1] + t, WIN[2] - t, WIN[2]),
                           (WIN[0] - t, WIN[0], WIN[2], WIN[3]), (WIN[1], WIN[1] + t, WIN[2], WIN[3])):
        g.box(tr, a0, a1, YWIN - 0.0015, YWIN + 0.0005, b0, b1)
    parts.append(tr)
    sc = P("kfk_scale", "scale", group=SEL_SCREEN)
    g.box(sc, WIN[0] - 0.004, WIN[1] + 0.004, YSCALE, YSCALE + 0.001, WIN[2] - 0.004, WIN[3] + 0.004)
    parts.append(sc)
    if lod == 0:
        gl = P("kfk_glass", "steel", section="glass")
        g.box(gl, WIN[0], WIN[1], YWIN + 0.0025, YWIN + 0.0032, WIN[2], WIN[3])
        parts.append(gl)
    # microammeter needle (bone ozl_meter): the axis is under the window, at zero it is the left end of the scale
    mt = P("kfk_meter_needle", "needle_k", group=SEL_METER)
    a = math.radians(L.SCALE_A[0])
    d = Vector((math.cos(a), 0.0, -math.sin(a)))
    pv = Vector((L.METER_PIVOT[0], YMETER, L.METER_PIVOT[1]))
    f2 = g.Frame(pv, d, Vector((0, -1, 0)).cross(d), (0, -1, 0))
    poly = [(L.METER_R * 0.56, -0.0007), (L.METER_R * 1.035, -0.00035), (L.METER_R * 1.045, 0.0), (L.METER_R * 1.035, 0.00035),
            (L.METER_R * 0.56, 0.0007)]
    g.prism(mt, poly, (0, 1), -0.00025, 0.00025, frame=f2)
    parts.append(mt)
    # illuminator on the left: a blue housing, a perforated wall, a slot
    lh = P("kfk_lamp_house", "kfk_blue")
    g.box(lh, x0 - 0.045, x0 + 0.004, y0 + 0.05, y1 - 0.08, ZK0 + 0.022, zb - 0.012,
          **(dict(r=0.006, seg=2) if lod == 0 else {}))
    parts.append(lh)
    if lod == 0:
        lv = P("kfk_lamp_vent", "kfk_side_vent")
        g.box(lv, x0 - 0.0475, x0 - 0.0445, y0 + 0.068, y1 - 0.098, ZK0 + 0.036, zb - 0.026)
        parts.append(lv)
        ks = P("kfk_slot", "dark")
        g.box(ks, x0 - 0.0480, x0 - 0.0470, y0 + 0.13, y0 + 0.15, ZK0 + 0.030, ZK0 + 0.034)
        parts.append(ks)
    # perforated covers on top at the sides of the scale housing, on screws
    tv = P("kfk_top_vent", "kfk_vent")
    vents = ((x0 + 0.018, hx0 - 0.010), (hx1 + 0.010, x1 - 0.018))
    for xa, xb in vents:
        g.box(tv, xa, xb, YK - 0.065, y1 - 0.022, zb - 0.0005, zb + 0.0015)
    parts.append(tv)
    if lod == 0:
        sw = P("kfk_screws", "steel")
        top = g.Frame((0.0, 0.0, zb + 0.0015), (1, 0, 0), (0, 1, 0), Z_UP)
        for xa, xb in vents:
            for xx in (xa + 0.007, xb - 0.007):
                for yy in (YK - 0.058, y1 - 0.029):
                    screw(sw, top, xx, yy, 0.0)
        parts.append(sw)
        # cuvette slide handle: a steel lever from the slot under the cuvette compartment
        lv = P("kfk_cuvette_lever", "steel")
        g.box(lv, XK + 0.026, XK + 0.034, y0 - 0.040, y0 - 0.006, ZK0 + 0.027, ZK0 + 0.031, r=0.001, seg=1)
        g.cyl(lv, (XK + 0.030, y0 - 0.042, ZK0 + 0.029), "z", 0.0055, 0.006, 10)
        parts.append(lv)
        ks2 = P("kfk_lever_slot", "dark")
        g.box(ks2, XK + 0.018, XK + 0.042, y0 - 0.0068, y0 - 0.0058, ZK0 + 0.024, ZK0 + 0.034)
        parts.append(ks2)
        # tag on the right side
        tg = P("kfk_tag", "tag")
        g.box(tg, x1 - 0.0005, x1 + 0.0008, TAG[0], TAG[1], TAG[2], TAG[3])
        parts.append(tg)
    # knobs (marks as in the photo: the filters at the bottom left, the others up) and the power indicator
    for (kx_, kz, kr, nm), deg in zip(L.KNOBS, (205.0, 95.0, 90.0, 90.0)):
        knob(parts, "kfk_knob_" + nm, kx_, y0, kz, kr, lod, deg)
    lamp(parts, "kfk_lamp", L.KLAMP[0], y0, L.KLAMP[1], 0.0055, lod)
    if lod == 0:
        ft = P("kfk_feet", "rubber")
        for x in (x0 + 0.04, x1 - 0.04):
            for y in (y0 + 0.04, y1 - 0.04):
                lathe_z(ft, [(0.0, ZB), (0.014, ZB), (0.0105, ZK0 + 0.001), (0.0, ZK0 + 0.001)], 8, x, y)
        parts.append(ft)
        gr = P("kfk_grommet", "rubber")
        lathe(gr, [(0.0065, -0.001), (0.0062, 0.006), (0.0050, 0.014), (0.0040, 0.024)], 10,
              axis_frame((x1 - 0.07, y1, ZK0 + 0.040), (0, 1, 0)))
        parts.append(gr)
        parts += build_cuvettes()
    # KFK-2 cord: from the back down behind the crate, along the floor into the gap between the crates and
    # to the plug in the extension
    px, py = EXT.x + SOCKETS[1], EXT.y
    cx = CORD_X[1]
    yb = YB1 + BT + 0.0035                                  # back of crate B (by the battens)
    pts = [(x1 - 0.07, y1 + 0.022, ZK0 + 0.040), (x1 - 0.072, y1 + 0.034, ZK0 + 0.010), (x1 - 0.078, yb - 0.002, ZB + 0.005),
           (x1 - 0.085, yb + 0.002, ZB - 0.035), (x1 - 0.10, yb + 0.001, 0.22), (x1 - 0.13, yb + 0.002, 0.06),
           (x1 - 0.17, yb + 0.012, 0.0035), (cx + 0.06, yb + 0.014, 0.0035), (cx + 0.012, yb + 0.006, 0.0035),
           (cx, YB1 - 0.01, 0.0035), (cx, 0.0, 0.0035), (cx, YA0 - 0.03, 0.0035), (px + 0.008, py + 0.072, 0.0035),
           (px + 0.003, py + 0.024, 0.020), (px, py + 0.008, PLUG_TOP + 0.006), (px, py, PLUG_TOP - 0.004)]
    parts += cable("kfk_cord", "cable", pts, 0.0035, lod, 2)
    return parts


def build_cuvettes():
    """Rack with four cuvettes (glass 12.5 x 12.5 x 45 mm) on the KFK-2 base at the front right: solutions - pink
    and yellow."""
    x0, x1, y0, y1 = KX1 - 0.118, KX1 - 0.022, KY0 + 0.022, KY0 + 0.054
    rk = P("kfk_rack", "rack")
    g.box(rk, x0, x1, y0, y1, ZKB, ZKB + 0.022, r=0.002, seg=1)
    gl = P("kfk_cuvettes", "steel", section="glass")
    lq = P("kfk_liquid", "liquid_a")
    parts = [rk, gl, lq]
    yc = (y0 + y1) / 2
    for k in range(4):
        xc = x0 + 0.015 + k * 0.022
        g.box(gl, xc - 0.00625, xc + 0.00625, yc - 0.00625, yc + 0.00625, ZKB + 0.006, ZKB + 0.051)
        use(lq, "liquid_a" if k % 2 == 0 else "liquid_b")
        g.box(lq, xc - 0.0052, xc + 0.0052, yc - 0.0052, yc + 0.0052, ZKB + 0.007, ZKB + 0.040 - 0.004 * k)
    return parts


# =============================================================================
# Extension
# =============================================================================
def build_extension(spec):
    """Soviet three-socket strip on the floor: two round plugs (the hotplate and the KFK-2; a knurled body,
    a neck, the cord up and down to the floor) are in it, the third socket is empty; the cord to the
    generator goes right and back."""
    lod = spec["lod"]
    if lod == 2:
        return []
    e = EXT
    bx = P("ext_block", "ext")
    rc = (e.x - 0.105, e.x + 0.105, e.y - 0.028, e.y + 0.028)
    if lod == 0:
        rr_loft(bx, rc, 0.014, [(0.002, 0.0), (0.0, 0.003), (0.0, EXT_H - 0.006), (0.003, EXT_H - 0.0015), (0.007, EXT_H)], 3)
    else:
        g.box(bx, *rc, 0.0, EXT_H)
    parts = [bx]
    pl = P("ext_plugs", "ext_plug")
    parts.append(pl)
    if lod == 0:
        sk = P("ext_sockets", "ext")
        dk = P("ext_socket_holes", "dark")
        parts += [sk, dk]
    for k, dx in enumerate(SOCKETS):
        x, y = e.x + dx, e.y
        if lod == 0:
            lathe_z(sk, [(0.0195, EXT_H - 0.0006), (0.0195, EXT_H + 0.0016), (0.0168, EXT_H + 0.0024), (0.0160, EXT_H + 0.0014),
                         (0.0, EXT_H + 0.0014)], 12, x, y)
        if k == 2:
            if lod == 0:
                for s in (-1, 1):
                    g.cyl(dk, (x + s * 0.0095, y, EXT_H + 0.0016), "z", 0.0026, 0.0006, 6)
            continue
        if lod == 0:
            fr = g.Frame((x, y, 0.0), (1, 0, 0), (0, 1, 0), Z_UP)
            lathe(pl, [(0.0, EXT_H + 0.0014), (0.0164, EXT_H + 0.0014), (0.0170, EXT_H + 0.005), (0.0168, EXT_H + 0.008)], 10, fr)
            knurl(pl, fr, 0.0168, 0.0011, 6, EXT_H + 0.008, EXT_H + 0.030)
            lathe(pl, [(0.0166, EXT_H + 0.030), (0.0125, EXT_H + 0.039), (0.0068, EXT_H + 0.046), (0.0060, PLUG_TOP - 0.002),
                       (0.0, PLUG_TOP)], 10, fr)
        else:
            g.cyl(pl, (x, y, (EXT_H + PLUG_TOP) / 2), "z", 0.016, PLUG_TOP - EXT_H, 8)
    # cord to the generator: entry at the end, along the floor right and back
    if lod == 0:
        gr = P("ext_grommet", "ext_plug")
        lathe(gr, [(0.0075, -0.001), (0.0070, 0.006), (0.0058, 0.016), (0.0052, 0.024)], 10,
              axis_frame((e.x + 0.105, e.y, EXT_H / 2), (1, 0, 0), (0, 1, 0)))
        parts.append(gr)
    pts = [(e.x + 0.125, e.y, EXT_H / 2), (e.x + 0.16, e.y + 0.004, 0.012), (e.x + 0.24, e.y + 0.03, 0.0055),
           (e.x + 0.40, e.y + 0.07, 0.0055), (0.60, -0.14, 0.0055), (0.65, 0.10, 0.0055), (0.70, 0.40, 0.0055)]
    parts += cable("ext_lead", "cable", pts, 0.0055, lod, 3)
    return parts


def build_lod(spec):
    parts = build_crates(spec) + build_plate(spec) + build_cooker(spec) + build_gauge(spec)
    parts += build_kfk(spec) + build_extension(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    wood = kx.PEN + r"\wood.rvmat"
    metal = kx.PEN + r"\metalplate.rvmat"
    crate_a = kx.box_pts(XA0 - BT, XA1 + BT, YA0 - BT, YA1 + BT, 0.0, ZA)
    crate_b = kx.box_pts(XB0 - BT, XB1 + BT, YB0 - BT, YB1 + BT, 0.0, ZB)
    # a component thinner than 0.5 m does not work: the hotplate, cooker and instrument go down into the crates
    plate = kx.box_pts(XP - PW / 2, XP + PW / 2, YP - PD / 2, YP + PD / 2, ZPT - 0.5, ZPT)
    cooker = kx.box_pts(XC - RCL - 0.02, XC + RCL + 0.02, YC - RCL - 0.02, YC + RCL + 0.02, ZPT - 0.3, ZD + 0.08)
    kfk = kx.box_pts(KX0 - 0.045, KX1, KY0 - 0.02, KY1, ZB - 0.2, ZK0 + KH)
    comps = [(crate_a, wood), (crate_b, wood), (plate, metal), (cooker, metal), (kfk, metal)]
    memory = {
        "invView": [(0.0, -2.6, 1.0)],
        "ce_center": [(0.0, 0.0, 0.55)],
        "ce_radius": [(0.75, 0.0, 0.55)],
        # bone axes: the gauge needle - from the dial centre toward the player; the weight - along y through
        # the top of the tube (swings left-right), also toward the player; the KFK-2 needle - from its axis
        # under the window toward the player (AXES)
        **AXES,
    }
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 70.0, memory, bbox


# =============================================================================
# Preview of the "work" look: bones in pose (render only; in the p3d the bones are at phase 0, model.cfg rotates
# them)
# =============================================================================
# group -> (point on the axis, Blender axis, angle): clockwise for someone looking from the front is plus about +Y
TURN = {
    SEL_NEEDLE: ((GX, YDIAL, GZ), (0.0, 1.0, 0.0), math.radians(L.GAUGE_SPAN * L.GAUGE_WORK)),
    SEL_METER: ((L.METER_PIVOT[0], YMETER, L.METER_PIVOT[1]), (0.0, 1.0, 0.0), METER_SPAN * L.METER_WORK),
    SEL_WEIGHT: ((VX, VY, ZPIPE), (0.0, 1.0, 0.0), WEIGHT_TILT * 0.5),
}
# Bone axes are memory points (collision). The engine rotates a bone right-handed in DayZ axes
# (kexport.conv, determinant -1); in Blender axes that is a left-handed rotation about the axis from
# the first point to the second: the axis looks at the player, a positive angle is clockwise for them.
# All three axes point to the player (-Y), like the needles; with the weight axis pointing away from
# the player the weight would swing in game the other way than in the preview (checked by check_turns).
AXES = {
    "ozl_needle_axis": [(GX, YDIAL, GZ), (GX, YDIAL - 0.05, GZ)],
    "ozl_weight_axis": [(VX, VY + 0.02, ZPIPE), (VX, VY - 0.02, ZPIPE)],
    "ozl_meter_axis": [(L.METER_PIVOT[0], YMETER, L.METER_PIVOT[1]), (L.METER_PIVOT[0], YMETER - 0.05, L.METER_PIVOT[1])],
}


def check_turns():
    """Numeric check, like check_axes of the Storage boxes: the preview pose (TURN) of each bone rotates the
    same way as the engine does by its animation and memory axis (in Blender axes - right-handed about
    the reverse axis, from the second point to the first). If it does not hold, the build fails."""
    seen = []
    for name, d in ANIMS:
        if d.get("type") != "rotation" or d["selection"] not in TURN:
            continue
        a, b = (Vector(q) for q in AXES[d["axis"]])
        eng = (a - b).normalized() * math.copysign(1.0, d["angle1"] - d["angle0"])
        _, ax, ang = TURN[d["selection"]]
        pre = Vector(ax).normalized() * math.copysign(1.0, ang)
        assert eng.dot(pre) > 0.99, "%s: the preview and the game rotate in different directions" % name
        seen.append(d["selection"])
    print("turns ok: the preview and the engine rotate the same way - " + ", ".join(seen))


check_turns()
_place_look, _place = krender.place_look, krender.place


def _turned(parts, obs, move):
    """kmodel places the look in the preview only by translation (move); the needles and the weight need
    rotation: the objects of the parts of these bones are rotated about their axes when the "work" look
    is drawn (move is its dictionary)."""
    if move is not ON["move"]:
        return obs
    for p, ob in zip(parts, obs):
        t = TURN.get(p.group)
        if t:
            c, axis, ang = t
            tm = Matrix.Translation(Vector(c))
            ob.matrix_basis = tm @ Matrix.Rotation(ang, 4, Vector(axis)) @ tm.inverted() @ ob.matrix_basis
    return obs


def place_look_turned(parts, kind_table, origin, remap=None, glow=1.5, sharp_deg=40.0, panels=None, move=None):
    return _turned(parts, _place_look(parts, kind_table, origin, remap=remap, glow=glow, sharp_deg=sharp_deg,
                                      panels=panels, move=move), move)


def place_turned(parts, tag, offset, mats, sharp_deg=40.0, move=None):
    return _turned(parts, _place(parts, tag, offset, mats, sharp_deg=sharp_deg, move=move), move)


krender.place_look = place_look_turned
krender.place = place_turned

# the first ones are for the --look preview: overview, cooker, KFK-2, hotplate, the left end with the
# gas mask (in "work" - the first four)
SHOTS = [
    ("front", (-0.9, -2.6, 1.45), (0.0, 0.0, 0.62), 30),
    ("cooker", (-0.50, -0.85, 1.36), (XC, YC, 0.94), 34),
    ("kfk", (0.62, -0.92, 0.95), (XK, YK, 0.60), 34),
    ("plate", (-0.75, -0.80, 1.05), (XP - 0.08, YP, 0.68), 34),
    ("left", (-1.55, -0.95, 0.95), (-0.40, 0.0, 0.48), 32),
    ("back", (1.3, 2.2, 1.4), (0.0, 0.0, 0.6), 30),
]

M.look_shots = (5, 4)
M.run(build_lod, collision, SHOTS, row_step=1.4, row_shot=((1.4, -6.0, 1.5), (1.4, 0, 0.6)))
