"""M01 - biosafety cabinet, the Scientists' Bio Packer (OZL_Eco_Pack_Bio).
Packer: cargo 10x10, three module places (module_1..3) and proxies for the modules at the same
places. Each module of the Bio line has its own slot and its own working place: slot 1 - binocular
loupe M44 inside the cabinet at the left, on a lifting table, eyepieces right against the sash glass;
slot 2 - centrifuge M45 on the side shelf at the right, next to an outlet on the cabinet side;
slot 3 - reagent kit M46 inside at the right (the empty place shows wet rings left by test tubes).

    blender --background --python build_m01.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (biohazard sign, gauge dial, panel
screen "off" and the "work" frames).

The device is a class II laminar cabinet on a stand, like a real 1.2 m one: 1.30 x 0.80 m outside,
work surface 0.76 m above the floor, 200 mm work opening under a glass sash inclined by 10 degrees,
control panel above the sash, exhaust filter housing on the roof; total height 2.12 m (sizes follow
real cabinets: Thermo 1300/1500, Labconco Logic). A folding shelf with a mat on the right. Outer
sizes and shape match the version already accepted in game.

Built with kmodel (the "dayz" look: matte, worn, corner shading) from real-cabinet details: rounded
body and chamber edges, an airfoil armrest over the front lip, three removable floor sheets, a glass
sash in an aluminium frame with guides and seal, a control panel (LCD, differential gauge with a
needle bone, buttons, lamps, toggle), a light fixture, a downflow grid, gas taps, a filter housing on
the roof, a 40 x 40 tube stand with adjustable feet, a side shelf with a rolled edge, and a power
cable in a smooth curve (g.pipe along a spline, not g.tube with kinks). Small props are vanilla DayZ
items through proxies (kvanilla: spray, alcohol, syringe, vials, blood test kit, GP-5 gas mask,
paper and pen) plus own detailed ones (Petri dish tray, kidney tray with scalpel and tweezers,
impulse bag sealer, lifting table under the loupe, jerrycan, taped carton).

Work look (the "work" loop; the mod's class OZL_Work):
- ozl_screen - panel LCD (screen section): "off" is dark glass, "work" plays frames _screen_fNN
  (flow speed, bar, spinning fan icon; frames, 8 x 0.25 s);
- ozl_lamp - light diffuser and the green panel lamp: lit in "work" (atlas _on);
- ozl_lamp_2 - yellow heating lamp of the sealer: blinks in "work" (blink);
- ozl_needle - gauge needle, a bone on the source ozl_needle: at rest on zero (fan stopped), in
  "work" it wobbles around 0.55 of the scale (wobble). The axis points from the dial to the face,
  phase 1 is 270 degrees clockwise (as in M08, M14; the sign of the angle is not verified in game);
- ozl_arm - sealer lever, a bone on the source ozl_arm: raised by 9 degrees at rest, pressed down in
  "work" (pose). The axis is along -x (same sign rule).
In the "work" preview the needle and lever are rotated into pose: the kit's move only translates a
part, so this script wraps krender.place_look / place itself (the kit is left untouched).

Blender axes: X is width, Y is depth (face toward -Y), Z is up; kexport.conv converts to p3d.
"""
import math
import os
import sys

import bmesh
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

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
W2, IW2 = 0.65, 0.60            # body: half width outside and inside the chamber
YF, YB = -0.40, 0.40            # front (face) and back
Z_ST = 0.65                     # top of the stand
Z_WORK = 0.76                   # chamber floor
Z_TRAY = 0.765                  # top of the work tray (three sheets on the chamber floor)
Z_ARM = 0.78                    # front lip (bottom of the work opening)
Z_OPEN = 0.98                   # bottom of the glass: 200 mm opening
Z_WIN = 1.58                    # top of the window
Z_CEIL = 1.66                   # chamber ceiling
Z_ROOF = 2.03                   # roof
Z_TOP = 2.12                    # top of the filter housing
Y_IN_F, Y_IN_B = -0.37, 0.33    # chamber: front at the floor and back wall
TILT = 10.0
TAN, COS = math.tan(math.radians(TILT)), math.cos(math.radians(TILT))
FRONT = g.inclined_front(YF, Z_OPEN, TILT)
B_WIN = (Z_WIN - Z_OPEN) / COS
GLASS_C = -0.016                # sash glass sits 16 mm behind the face plane
X_SH0, X_SH1, Z_SH = W2, 0.94, 0.875     # side shelf
SH_TOP = Z_SH + 0.015
MAT_TOP = SH_TOP + 0.004
Z_LOW = 0.172                   # top of the stand's lower shelf
FOOT_Z = 0.045                  # bottom of the stand tubes (adjustable feet below)
PB = B_WIN + 0.10               # panel centre along the slope
C_PANEL = 0.014                 # panel face above the body plane
GAUGE = (-0.42, PB)             # differential pressure gauge
LCD = (-0.296, -0.124, 0.022)   # screen: edges across the width, half height
TRAY_X = ((-0.595, -0.2025), (-0.1975, 0.1975), (0.2025, 0.595))
TRAY_Y = (-0.333, 0.293)
LEGS = ((-1, -1), (1, -1), (-1, 1), (1, 1))


def y_front(z):
    return YF + (z - Z_OPEN) * TAN


def y_glass(z):
    """Inner plane of the sash glass at height z."""
    return YF + (z - Z_OPEN) * TAN - GLASS_C / COS


# Module places (slot N = module N of the Bio line): the module origin is the bottom centre, face toward -Y
EYE_DY, EYE_DZ = -0.0955, 0.2251          # front edge of the M44 eyepieces from the module origin (from its MLOD)
JACK_H = 0.065                            # lifting table: eyepieces sit above the bottom bar of the sash
MX1 = -0.37
MZ1 = Z_TRAY + JACK_H
MY1 = y_glass(MZ1 + EYE_DZ) + 0.004 - EYE_DY   # eyepieces 4 mm from the glass
MX2, MY2 = (X_SH0 + X_SH1) / 2, 0.09
MX3, MY3 = 0.19, -0.03
MODS = [(MX1, MY1, MZ1), (MX2, MY2, MAT_TOP), (MX3, MY3, Z_TRAY)]
MOD_OBJ = [("m44_tool_optics", "ozr_tool_optics"), ("m45_centrifuge", "ozr_centrifuge"), ("m46_reagents", "ozr_reagents")]
# proxies for the modules: the mod's CfgNonAIVehicles binds slots OZL_Tool1..3 to them (Proxyozl_tool1..3);
# no rotation: the modules face the person
PROXIES = [(r"\OpenZone_Research\models\proxies\ozl_tool%d" % (i + 1), m) for i, m in enumerate(MODS)]
# empty slot 3: wet rings on the sheet where the tubes of the removed rack stood
RINGS = [(MX3 + dx, MY3 + dy, 0.0085) for dx, dy in ((-0.080, -0.026), (-0.040, -0.029), (0.001, -0.027),
                                                       (0.042, -0.025), (-0.078, 0.031), (-0.022, 0.029),
                                                       (0.040, 0.030), (0.083, 0.027), (0.047, 0.023))]
SOCK = (0.255, 1.00)            # outlet on the cabinet side by the shelf (y, z), facing +x
# own small props in the chamber and on the stand
PTRAY = (-0.25, 0.05, -0.33, -0.13, 0.020)          # Petri dish tray: x0 x1 y0 y1 h
DISHES = [((-0.180, -0.235), "open"), ((-0.075, -0.275), "lid"), ((0.000, -0.195), "closed")]
KIDNEY = (-0.075, -0.015)                              # kidney tray
SEAL = (0.31, 0.57, 0.125, 0.215)                      # sealer: base x0 x1 y0 y1
SEAL_H = 0.058
HINGE = (SEAL[3] - 0.012, Z_TRAY + SEAL_H + 0.010)     # sealer lever axis (y, z)
ARM_OPEN = 9.0                                         # the lever is raised at rest, degrees
BAG = (0.43, 0.53, 0.035, 0.105)                       # sealed bag with a sample
CAN = (-0.52, -0.29, -0.12, 0.07, 0.30)                # jerrycan: x0 x1 y0 y1 h
CARTON = (0.22, 0.52, -0.15, 0.12, 0.18)
DRAIN = (-0.50, -0.37)                                 # drain tap under the front

LOD_SPECS = [
    dict(lod=0, bev=3, sides=20),
    dict(lod=1, bev=0, sides=10),
    dict(lod=2, bev=0, sides=6),
]

# Regions: name -> (material kind, texel density scale)
REGIONS = {
    "shell": ("enamel", 1.0), "front": ("enamel_front", 2.0), "cav": ("steel_in", 0.55),
    "pillar_l": ("enamel", 1.0), "pillar_r": ("enamel", 1.0), "back": ("enamel", 0.4), "top": ("enamel", 0.5),
    "tray": ("tray", 1.0), "stand": ("enamel_grey", 0.55),
    "steel": ("steel", 0.8), "chrome": ("chrome", 2.0), "alu": ("alu", 0.9),
    "grille_h": ("grille_h", 0.7), "grille_v": ("grille_v", 0.9), "grille_d": ("grille_d", 0.5),
    "panel": ("panel", 2.0), "gauge": ("gauge", 3.2), "black": ("black", 1.2), "rubber": ("rubber", 0.6),
    "lamp_g": ("lamp_g", 2.0), "lamp_r": ("lamp_r", 2.0), "amber": ("amber", 2.0), "needle": ("cap_red", 3.0),
    "diffuser": ("diffuser", 0.5), "lamp_body": ("enamel", 0.5), "plate": ("plate", 1.5),
    "petri": ("petri", 1.5), "tissue": ("tissue", 2.0), "sealer": ("sealer", 1.2), "teflon": ("teflon", 2.0),
    "silicone": ("silicone", 2.0), "bag": ("bag", 1.5), "canister": ("canister", 0.6),
    "cardboard": ("cardboard", 0.6), "tape": ("tape", 0.8), "cap_blue": ("cap_blue", 1.5), "cap_red": ("cap_red", 1.5),
    "knob_yellow": ("knob_yellow", 2.0), "knob_blue": ("knob_blue", 2.0), "bakelite": ("bakelite", 1.5),
    "cable": ("cable", 0.4), "mat": ("mat", 0.7),
}


# =============================================================================
# Materials
# =============================================================================
def build_worn(mat, origin, color, bare=kmats.lin((112, 112, 116)), seed=1.0, gloss=0.32, spec=0.25,
               wear=(0.66, 0.71), edge_k=0.7, rub=(), scratch=0.0, floor_z=0.0, dust=0.15, grime=0.3,
               decal_items=(), yellow=0.0):
    """Enamel worn by hands, without rust (the M23 builder minus streaks, oil and clean patches; chips in
    kmats.build_paint always rust, but this is a clean laboratory): worn down to primer and metal on the
    edges (edge_k) and where people grab (rub - [(centre, half-axes, strength)]: an ellipsoid, weaker
    toward its edge); yellow - old enamel yellowed in patches."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.92 for c in color[:3]) + (1,), color)
    if yellow > 0:
        base = t.mixc(t.math("MULTIPLY", t.maprange(t.noise(vec, 1.2, 4.0, 0.5), 0.35, 0.7, 0.2, 1.0), yellow),
                      base, kmats.lin((206, 190, 150)))
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
    # bare metal: brushing along x, patchy tone; a thin dark primer border at the edge of the worn area
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
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g_, s_, h)


class _Keep(kmats.Tree):
    """Wraps the node tree of a finished material without clearing it, to add a layer over the kit builder."""

    def __init__(self, mat):
        self.nt = mat.node_tree


def build_tray(mat, origin, rings=(), **kw):
    """Work tray sheet - brushed stainless steel (kmats.build_steel); rings - [(x, y, r)] wet rings left by
    test tubes (empty slot 3): a thin dark ring, slightly darker inside, and glossy."""
    outs = kmats.build_steel(mat, origin, **kw)
    if not rings:
        return outs
    t = _Keep(mat)
    tc = t.node("ShaderNodeTexCoord")
    tc.object = origin
    sep = t.node("ShaderNodeSeparateXYZ")
    t.link(tc.outputs["Object"], sep.inputs[0])
    wet = None
    for x, y, r in rings:
        dx = t.math("SUBTRACT", sep.outputs["X"], x)
        dy = t.math("SUBTRACT", sep.outputs["Y"], y)
        d = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", dx, dx), t.math("MULTIPLY", dy, dy)))
        ring = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", d, r)), 0.0006, 0.0018, 1.0, 0.0)
        m = t.math("MAXIMUM", ring, t.maprange(d, r - 0.001, r, 0.35, 0.0))
        wet = m if wet is None else t.math("MAXIMUM", wet, m)

    def sock(v):
        return v if isinstance(v, (int, float)) else kmats.sock(mat, v)
    col = t.mixc(t.math("MULTIPLY", wet, 0.55), sock(outs["color"]), kmats.lin((40, 42, 44)))
    gl = t.math("ADD", sock(outs["gloss"]), t.math("MULTIPLY", wet, 0.25))
    return kmats.out(t, col, gl, sock(outs["spec"]), sock(outs["height"]))


def wall_decal(name, cx, cz, w, h, y0, y1):
    return (os.path.join(WORK, name), "y", -1, ("x", "z"), (cx, cz), (w, h), (y0, y1))


DECALS = [wall_decal("decal_biohazard.png", -0.34, Z_OPEN + 0.86 * COS, 0.12, 0.12 * COS, -0.32, -0.20)]
_DIAL_C = FRONT.p(GAUGE[0], GAUGE[1], C_PANEL + 0.005)
DIAL = [wall_decal("decal_dial.png", _DIAL_C.x, _DIAL_C.z, 0.0804, 0.0804 * COS, _DIAL_C.y - 0.01, _DIAL_C.y + 0.01)]
# wear: front edge of the lip (hands), bottom of the stand legs (kicked)
SHELL_RUB = [((0.0, YF, Z_ARM), (0.55, 0.05, 0.035), 0.35)]
FEET_RUB = [((s_x * 0.58, s_y * 0.32, FOOT_Z + 0.02), (0.035, 0.035, 0.06), 0.40) for s_x, s_y in LEGS]
ENAMEL = dict(color=kmats.lin((224, 222, 212)), bare=kmats.lin((118, 118, 116)), seed=1.0, gloss=0.42, spec=0.30,
              wear=(0.75, 0.80), edge_k=0.5, rub=SHELL_RUB, scratch=0.12, floor_z=Z_ST, dust=0.18, grime=0.18,
              yellow=0.25)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "enamel": (build_worn, ENAMEL),
    "enamel_front": (build_worn, dict(ENAMEL, seed=1.6, decal_items=DECALS)),
    "enamel_grey": (build_worn, dict(color=kmats.lin((150, 153, 150)), bare=kmats.lin((112, 112, 114)), seed=2.3,
                                     gloss=0.35, spec=0.25, wear=(0.70, 0.75), edge_k=0.65, rub=FEET_RUB,
                                     scratch=0.25, floor_z=0.0, dust=0.30, grime=0.45)),
    "steel_in": ("steel", dict(seed=3.1, tone=0.34, along="x", floor_z=Z_WORK, dust=0.15, grime=0.15)),
    # floor sheets: brushed stainless; at the reagent kit's place - wet rings from test tubes
    "tray": (build_tray, dict(seed=3.9, tone=0.33, along="y", floor_z=Z_WORK, dust=0.08, grime=0.12, rings=RINGS)),
    "chrome": ("steel", dict(seed=4.6, tone=0.42, along="z", gloss=0.70, spec=0.85, dust=0.1, grime=0.2)),
    "alu": ("steel", dict(seed=4.9, tone=0.40, along="x", gloss=0.45, spec=0.55, dust=0.15, grime=0.2)),
    "grille_d": ("steel", dict(seed=5.2, tone=0.30, along="x", holes=(("x", "y"), 0.006, 0.30), dust=0.1,
                               grime=0.1)),
    "panel": ("plastic", dict(color=kmats.lin((48, 50, 54)), gloss=0.30, spec=0.20, floor_z=Z_ST, dust=0.15,
                              scuff=(0.70, 0.78))),
    "gauge": ("paint", dict(color=kmats.lin((232, 226, 205)), chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0,
                            gloss=0.7, spec=0.5, dust=0.0, grime=0.0, decal_items=DIAL)),
    "lamp_g_on": ("flat", dict(color=kmats.lin((110, 255, 120)), gloss=0.85, spec=0.8)),
    "amber": ("flat", dict(color=kmats.lin((140, 80, 18)), gloss=0.85, spec=0.8)),
    "amber_on": ("flat", dict(color=kmats.lin((255, 176, 48)), gloss=0.85, spec=0.8)),
    # light diffuser: opal plastic; glows in "work"
    "diffuser": ("plastic", dict(color=kmats.lin((226, 226, 218)), gloss=0.25, spec=0.15, mottle=0.03, dust=0.05,
                                 grime=0.05)),
    "diffuser_on": ("flat", dict(color=kmats.lin((255, 252, 238)), gloss=0.3, spec=0.2)),
    "plate": ("steel", dict(seed=6.0, tone=0.40, along="x", gloss=0.45, spec=0.5, dust=0.1, grime=0.15)),
    "petri": ("flat", dict(color=kmats.lin((196, 212, 208)), gloss=0.85, spec=0.6)),
    # mutant tissue: dark red, wet, mottled
    "tissue": ("plastic", dict(color=kmats.lin((112, 30, 38)), gloss=0.65, spec=0.45, mottle=0.30, dust=0.0,
                               grime=0.0, scuff=(0.95, 1.0))),
    "sealer": ("plastic", dict(color=kmats.lin((198, 190, 166)), gloss=0.35, spec=0.25, floor_z=Z_TRAY, dust=0.15,
                               grime=0.2, scuff=(0.62, 0.70))),
    "teflon": ("plastic", dict(color=kmats.lin((120, 78, 40)), gloss=0.45, spec=0.3, dust=0.0, grime=0.3)),
    "silicone": ("plastic", dict(color=kmats.lin((186, 76, 40)), gloss=0.2, spec=0.1, dust=0.05)),
    "bag": ("plastic", dict(color=kmats.lin((214, 220, 216)), gloss=0.65, spec=0.4, mottle=0.08, dust=0.0,
                            grime=0.0)),
    "canister": ("plastic", dict(color=kmats.lin((214, 206, 176)), gloss=0.30, spec=0.20, floor_z=Z_LOW, dust=0.45,
                                 grime=0.30)),
    "cardboard": ("plastic", dict(color=kmats.lin((150, 114, 74)), gloss=0.08, spec=0.04, mottle=0.12, floor_z=Z_LOW,
                                  dust=0.5, grime=0.4, scuff=(0.70, 0.80))),
    "tape": ("plastic", dict(color=kmats.lin((168, 132, 80)), gloss=0.55, spec=0.35, dust=0.2, grime=0.1)),
    "cap_blue": ("plastic", dict(color=kmats.lin((40, 78, 160)), gloss=0.4, spec=0.3)),
    "knob_yellow": ("plastic", dict(color=kmats.lin((206, 162, 32)), gloss=0.45, spec=0.3, dust=0.1)),
    "knob_blue": ("plastic", dict(color=kmats.lin((40, 80, 170)), gloss=0.45, spec=0.3, dust=0.1)),
    "bakelite": ("plastic", dict(color=kmats.lin((210, 202, 180)), gloss=0.45, spec=0.3, dust=0.25, grime=0.25)),
    "cable": ("plastic", dict(color=kmats.lin((28, 28, 29)), gloss=0.25, spec=0.15, dust=0.35, grime=0.2)),
    "mat": ("plastic", dict(color=kmats.lin((44, 46, 44)), gloss=0.12, spec=0.06, mottle=0.12, dust=0.3, grime=0.3,
                            scuff=(0.66, 0.74))),
})

OBJ, NAME = "m01_biosafety", "ozr_biosafety_cabinet"
# Work look: the screen has its own texture (the mod's script cycles the frames), the light fixture and
# the green lamp use atlas _on, the sealer heating lamp uses _on and blinks; the needle and lever are bones.
SEL_SCREEN, SEL_LAMP, SEL_LAMP2 = "ozl_screen", "ozl_lamp", "ozl_lamp_2"
SEL_NEEDLE, SEL_ARM = "ozl_needle", "ozl_arm"
NEEDLE_MID = 0.55                                      # in "work" the needle sits near this fraction of the scale
NEEDLE_HUB = FRONT.p(GAUGE[0], GAUGE[1], C_PANEL)
ON = dict(remap={"diffuser": "diffuser_on", "lamp_g": "lamp_g_on", "amber": "amber_on"},
          emissive=(1.0, 1.0, 1.0, 1.0), move={SEL_NEEDLE: (0.0, 0.0, 0.0), SEL_ARM: (0.0, 0.0, 0.0)})
NEEDLE_ANIM = ("ozl_needle_rot", dict(type="rotation", source="ozl_needle", selection=SEL_NEEDLE,
                                      axis="ozl_needle_axis", memory=1, minValue=0.0, maxValue=1.0, angle0=0.0,
                                      angle1=math.radians(270.0)))
ARM_ANIM = ("ozl_arm_press", dict(type="rotation", source="ozl_arm", selection=SEL_ARM, axis="ozl_arm_axis",
                                  memory=1, minValue=0.0, maxValue=1.0, angle0=0.0, angle1=math.radians(ARM_OPEN)))
SCREEN = dict(off="decal_lcd_off.png", frames=["decal_lcd_f%02d.png" % i for i in range(8)], size=256, gloss=0.8)
# vanilla props: DayZ medical items - the texture is in the model itself (not from the config)
SPRAY, ALCO = r"dz\gear\medical\DisinfectantSpray", r"dz\gear\medical\alfa"
SYRINGE, VIAL, BTK = r"dz\gear\medical\Syringe_Empty", r"dz\gear\medical\InjectionVial", r"dz\gear\medical\BloodTest_Kit"
DECOR = [
    kv.put(SPRAY, (-0.50, 0.245, Z_TRAY), up=(0, 0, 1), fwd=(0.45, -1, 0)),
    kv.put(ALCO, (-0.39, 0.265, Z_TRAY), up=(0, 0, 1), fwd=(-0.2, -1, 0), lods=(0,)),
    kv.put(SYRINGE, (0.14, -0.235, Z_TRAY), lods=(0,), **kv.flat(4)),
    kv.put(VIAL, (-0.13, 0.20, Z_TRAY), up=(0, 0, 1), fwd=(0, -1, 0), lods=(0,)),
    kv.put(VIAL, (-0.065, 0.225, Z_TRAY), up=(0, 0, 1), fwd=(0.3, -1, 0), lods=(0,)),
    kv.put(BTK, (0.46, -0.24, Z_TRAY), lods=(0,), **kv.flat(100)),
    kv.put("gp5", (-0.03, -0.10, Z_LOW), up=(0.15, 1, 0), fwd=(0, 0, 1)),            # lies on its back, facing up
    kv.put("paper", (MX2 - 0.003, -0.1665, MAT_TOP), **kv.flat(90)),
    kv.put("pen", (MX2 + 0.04, -0.17, MAT_TOP + 0.0004), lods=(0,), **kv.flat(64)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.60, 0.64, 0.62), clear=0.04, edge=0.12, smudge=0.05, streaks=0.03),
                 selections=(SEL_SCREEN, SEL_LAMP, SEL_LAMP2, SEL_NEEDLE, SEL_ARM),
                 hidden=(SEL_SCREEN, SEL_LAMP, SEL_LAMP2), states={"on": ON},
                 bones=((SEL_NEEDLE, ""), (SEL_ARM, "")), animations=(NEEDLE_ANIM, ARM_ANIM),
                 proxies=PROXIES, decor=DECOR, panels={"screen": SCREEN},
                 modules=[(o, n, m) for (o, n), m in zip(MOD_OBJ, MODS)],
                 sources={"ozl_needle": dict(animPeriod=0.2), "ozl_arm": dict(animPeriod=0.8)})
P = M.part
sx = kmodel.sx

# "Work" pose in the preview (render only, not exported to p3d): group -> (axis point, axis, right-hand angle)
POSE = {SEL_NEEDLE: (NEEDLE_HUB, FRONT.n, -math.radians(270.0 * NEEDLE_MID)),
        SEL_ARM: (Vector((0.0, HINGE[0], HINGE[1])), Vector((1.0, 0.0, 0.0)), math.radians(ARM_OPEN))}


def _posed(place):
    """krender.place_look / place that also rotates the parts of the POSE groups in the "work" look
    (move = ON["move"])."""
    def wrap(parts, *a, **kw):
        obs = place(parts, *a, **kw)
        if kw.get("move") is ON["move"]:
            for ob, p in zip(obs, parts):
                if p.group in POSE:
                    piv, ax, ang = POSE[p.group]
                    m = Matrix.Translation(piv) @ Matrix.Rotation(ang, 4, ax) @ Matrix.Translation(-piv)
                    ob.matrix_world = m @ Matrix.Translation(ob.location)
        return obs
    return wrap


krender.place_look = _posed(krender.place_look)
krender.place = _posed(krender.place)


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


def rounded(poly, r, n=3, closed=True):
    """Polyline with rounded corners: each corner becomes an arc of n+1 points (a quadratic curve through
    the vertex), r is the radius (a number or one per vertex); an open polyline (closed=False) keeps its end points."""
    pts = [Vector(p) for p in poly]
    m = len(pts)
    out = []
    for i in range(m):
        ri = r[i] if isinstance(r, (list, tuple)) else r
        if (not closed and i in (0, m - 1)) or ri <= 0:
            out.append(tuple(pts[i]))
            continue
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % m]
        a, b = p0 - p1, p2 - p1
        ang = a.angle(b)
        t = min(ri / max(math.tan(ang / 2), 1e-6), a.length * 0.5, b.length * 0.5)
        q0, q1 = p1 + a.normalized() * t, p1 + b.normalized() * t
        for k in range(n + 1):
            s = k / n
            out.append(tuple((1 - s) ** 2 * q0 + 2 * (1 - s) * s * p1 + s * s * q1))
    return out


def face(part, verts, want):
    """Face from bmesh vertices, turned toward `want`."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def lathe(part, prof, sides, c, axis=(0.0, 0.0, 1.0), inward=False, rib=0.0):
    """Body of revolution: prof [(r, h)] bottom to top along the outer surface (material on the left along
    the path), axis `axis` through point c; a ring with r = 0 is an apex (fan). inward - the surface
    faces the axis; rib - the radius through the vertex is smaller by rib (knurling)."""
    bm = part.bm
    c, ax = Vector(c), Vector(axis).normalized()
    e1 = ax.orthogonal().normalized()
    e2 = ax.cross(e1)

    def rad(t):
        a = 2 * math.pi * t / sides
        return e1 * math.cos(a) + e2 * math.sin(a)
    rings = []
    for r, h in prof:
        if r <= 1e-9:
            rings.append([bm.verts.new(c + ax * h)])
        else:
            rings.append([bm.verts.new(c + rad(k) * (r - (rib if k % 2 else 0.0)) + ax * h) for k in range(sides)])
    new = []
    for i in range(len(prof) - 1):
        A, B = rings[i], rings[i + 1]
        if len(A) == 1 and len(B) == 1:
            continue
        dr, dh = prof[i + 1][0] - prof[i][0], prof[i + 1][1] - prof[i][1]
        for k in range(sides):
            j = (k + 1) % sides
            nrm = rad(k + 0.5) * dh - ax * dr
            if inward:
                nrm = -nrm
            if len(A) == 1:
                q = [A[0], B[k], B[j]]
            elif len(B) == 1:
                q = [A[k], A[j], B[0]]
            else:
                q = [A[k], A[j], B[j], B[k]]
            new.append(face(part, q, nrm))
    part.tag(new)
    return new


def lathe_f(part, prof, sides, a, b, c0=C_PANEL, **kw):
    """Body of revolution on the inclined face (panel): the axis is the face normal through (a, b, c0)
    of the FRONT frame."""
    return lathe(part, prof, sides, FRONT.p(a, b, c0), FRONT.n, **kw)


def open_box(part, x0, x1, y0, y1, z0, z1, t):
    """Open box (no lid): floor and four walls of thickness t."""
    g.box(part, x0, x1, y0, y1, z0, z0 + t)
    g.box(part, x0, x1, y0, y0 + t, z0 + t, z1)
    g.box(part, x0, x1, y1 - t, y1, z0 + t, z1)
    g.box(part, x0, x0 + t, y0 + t, y1 - t, z0 + t, z1)
    g.box(part, x1 - t, x1, y0 + t, y1 - t, z0 + t, z1)


def rot2(pts, cx, cy, deg):
    """Points (x, y) around the centre, rotated by deg and placed at (cx, cy)."""
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    return [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts]


def blob(part, c, rx, ry, h, sides=14, rings=4, seed=0.0):
    """Piece of tissue: a low mound with an uneven edge (the radius wobbles by sines), flat bottom."""
    bm = part.bm
    c = Vector(c)

    def wob(a):
        return 1.0 + 0.16 * math.sin(3 * a + seed) + 0.09 * math.sin(5 * a + 2.3 * seed)
    lay = []
    for j in range(rings):
        f = j / rings
        rr, z = math.cos(f * math.pi / 2), h * math.sin(f * math.pi / 2)
        ring = []
        for k in range(sides):
            a = 2 * math.pi * k / sides
            ring.append(bm.verts.new(c + Vector((rx * rr * wob(a) * math.cos(a), ry * rr * wob(a) * math.sin(a), z))))
        lay.append(ring)
    top = bm.verts.new(c + Vector((0.0, 0.0, h)))
    mid = c + Vector((0.0, 0.0, h * 0.3))
    new = []
    for j in range(rings - 1):
        for k in range(sides):
            q = [lay[j][k], lay[j][(k + 1) % sides], lay[j + 1][(k + 1) % sides], lay[j + 1][k]]
            new.append(face(part, q, sum((v.co for v in q), Vector()) / 4 - mid))
    for k in range(sides):
        q = [lay[-1][k], lay[-1][(k + 1) % sides], top]
        new.append(face(part, q, sum((v.co for v in q), Vector()) / 3 - mid))
    new.append(face(part, lay[0][::-1], (0, 0, -1)))
    part.tag(new)


def transform(part, m):
    for v in part.bm.verts:
        v.co = m @ v.co
    part.bm.normal_update()


def disk(part, c, nrm, r, n=6):
    """Flat polygon (dark outlet hole): a single face oriented along nrm."""
    c, nrm = Vector(c), Vector(nrm).normalized()
    e1 = nrm.orthogonal().normalized()
    e2 = nrm.cross(e1)
    vs = [part.bm.verts.new(c + (e1 * math.cos(2 * math.pi * k / n) + e2 * math.sin(2 * math.pi * k / n)) * r)
          for k in range(n)]
    part.tag([face(part, vs, nrm)])


def sq_tube(part, axis, a0, a1, c1, c2, half, r, n):
    """Square tube with rounded edges along axis ("x", "y", "z") from a0 to a1: the section is a square
    of side 2*half centred at (c1, c2) in the other two axes (in x, y, z order), r is the corner
    radius, n - segments per rounding (a chamfer on all box edges would give three times more triangles)."""
    sq = rounded([(c1 - half, c2 - half), (c1 + half, c2 - half), (c1 + half, c2 + half), (c1 - half, c2 + half)], r, n)
    ia = "xyz".index(axis)
    return g.prism(part, sq, tuple(i for i in range(3) if i != ia), a0, a1)


# =============================================================================
# Body: side-profile prism minus the chamber (boolean difference, a face knows its region)
# =============================================================================
def build_shell(spec):
    bev = spec["bev"]
    outer = [(YF, Z_ST), (YB, Z_ST), (YB, Z_ROOF), (y_front(Z_ROOF), Z_ROOF), (YF, Z_OPEN)]
    base = P("shell_base", "shell")
    g.prism(base, outer, (1, 2), -W2, W2)
    if bev:
        g.bevel(base.bm, base.bm.edges[:], 0.012, bev)
    inner = [(-0.47, Z_ARM), (Y_IN_F, Z_ARM), (Y_IN_F, Z_WORK), (Y_IN_B, Z_WORK), (Y_IN_B, Z_CEIL),
             (y_front(Z_CEIL) + 0.018, Z_CEIL), (y_front(Z_WIN) + 0.018, Z_WIN), (-0.47, Z_WIN)]
    cav = P("cut_cav", "cav")
    g.prism(cav, inner, (1, 2), -IW2, IW2)
    if bev:
        # rounded inner chamber corners and opening corners (real cabinets: for washing)
        g.bevel(cav.bm, cav.bm.edges[:], 0.02, 2)
    shell = M.boolean("shell", base, [cav])
    # the front panel above the window is its own region: it carries the control panel, decal and grille
    # and needs density. After the cut-out the front is a single face shaped like the letter P (panel and
    # two posts at the opening): cut it at the top of the window and give the dense region only to the
    # part above the cut (otherwise the atlas rectangle covers the whole front with the posts). The cut is
    # slightly below the top of the window: it passes through the opening and the posts become separate faces
    fronts = [f for f in shell.bm.faces if f.normal.dot(FRONT.n) > 0.999]
    cut = FRONT.p(0.0, B_WIN - 0.002, 0.0)
    bmesh.ops.bisect_plane(shell.bm, geom=fronts + list({e for f in fronts for e in f.edges}) +
                           list({v for f in fronts for v in f.verts}), dist=1e-6, plane_co=cut, plane_no=FRONT.v)
    # posts at the sides of the opening and the bevels along them - each side its own region (one region for
    # both makes the atlas rectangle span the full width of the front); back and roof with their bevels
    # (barely visible) - sparser
    rid = {r: shell.region_index(r, *REGIONS[r]) for r in ("shell", "front", "pillar_l", "pillar_r", "back", "top")}
    for f in shell.bm.faces:
        if f[shell.reg] != rid["shell"]:
            continue
        n, c = f.normal, f.calc_center_median()
        ax = max(range(3), key=lambda i: abs(n[i]))
        side = rid["pillar_l" if c.x < 0 else "pillar_r"]
        if n.dot(FRONT.n) > 0.999:
            above = min((v.co - cut).dot(FRONT.v) for v in f.verts) > -1e-5
            f[shell.reg] = rid["front"] if above else side
        elif ax == 1 and n.y < 0:
            if c.z > Z_WIN:
                f[shell.reg] = rid["front"]
            elif abs(c.x) > IW2 - 0.01:
                f[shell.reg] = side
        elif ax == 1 and c.y > YB - 0.03:
            f[shell.reg] = rid["back"]
        elif ax == 2 and n.z > 0 and c.z > Z_ROOF - 0.03:
            f[shell.reg] = rid["top"]
    return shell


# =============================================================================
# Sash: glass in a frame, guides, seal; armrest
# =============================================================================
def build_glass():
    p = P("glass", "shell", section="glass")
    b0, b1, a = 0.016, B_WIN - 0.004, IW2 - 0.006
    g.quad(p, [FRONT.p(-a, b0, GLASS_C), FRONT.p(a, b0, GLASS_C), FRONT.p(a, b1, GLASS_C), FRONT.p(-a, b1, GLASS_C)])
    p.glass_frame = (FRONT, -a, a, b0, b1)
    return p


def build_sash(spec):
    """Bottom bar of the frame with a handle lip (profile in the b-c plane of the FRONT frame), end caps,
    side frame profiles, channel guides along the sides of the opening, seal above the glass."""
    lod = spec["lod"]
    a1 = IW2 - 0.004
    parts = []
    rail = P("sash_rail", "alu")
    if lod == 0:
        prof = rounded([(0.022, -0.026), (-0.012, -0.026), (-0.014, 0.004), (0.004, 0.007), (0.006, -0.009),
                        (0.022, -0.009)], [0.003, 0.004, 0.005, 0.004, 0.002, 0.003], 2)
    else:
        prof = [(0.022, -0.026), (-0.014, -0.026), (-0.014, 0.006), (0.022, 0.006)]
    g.prism(rail, prof, (1, 2), -a1 + 0.006, a1 - 0.006, frame=FRONT)
    parts.append(rail)
    if lod == 2:
        return parts
    if lod == 1:
        tr = P("sash_tracks", "steel")
        for s in (-1, 1):
            g.box(tr, *sx(IW2 - 0.016, IW2, s), -0.015, B_WIN, -0.030, -0.002, frame=FRONT)
        return parts + [tr]
    cprof = [(0.022, -0.026), (-0.013, -0.026), (-0.014, 0.004), (0.004, 0.007), (0.006, -0.009), (0.022, -0.009)]
    for s in (-1, 1):
        cap = P("sash_cap%d" % (s + 1), "black", uv_name="sash_cap", uv_origin=FRONT.p(s * a1, 0, 0))
        g.prism(cap, cprof, (1, 2), *sx(a1 - 0.006, a1, s), frame=FRONT)
        fr_ = P("sash_frame%d" % (s + 1), "alu", uv_name="sash_frame", uv_origin=FRONT.p(s * (IW2 - 0.013), 0, 0))
        g.box(fr_, *sx(IW2 - 0.020, IW2 - 0.006, s), 0.020, B_WIN - 0.002, GLASS_C - 0.004, GLASS_C + 0.004,
              frame=FRONT)
        tr = P("sash_track%d" % (s + 1), "steel", uv_name="sash_track", uv_origin=FRONT.p(s * (IW2 - 0.008), 0, 0))
        g.box(tr, *sx(IW2 - 0.003, IW2, s), -0.015, B_WIN, -0.030, -0.002, frame=FRONT)
        g.box(tr, *sx(IW2 - 0.016, IW2 - 0.003, s), -0.015, B_WIN, -0.030, -0.027, frame=FRONT)
        g.box(tr, *sx(IW2 - 0.016, IW2 - 0.003, s), -0.015, B_WIN, -0.005, -0.002, frame=FRONT)
        parts += [cap, fr_, tr]
    wp = P("sash_wiper", "rubber")
    g.box(wp, -IW2, IW2, B_WIN - 0.010, B_WIN + 0.004, -0.013, -0.003, frame=FRONT)
    parts.append(wp)
    return parts


def build_airfoil(spec):
    """Airfoil armrest over the front lip: a teardrop stainless profile on four posts."""
    lod = spec["lod"]
    if lod == 2:
        return []
    af = P("airfoil", "steel")
    n = 6 if lod == 0 else 2
    yc, zc, r = -0.421, 0.8005, 0.0075
    prof = [(yc + r * math.cos(math.pi / 2 + math.pi * k / n), zc + r * math.sin(math.pi / 2 + math.pi * k / n))
            for k in range(n + 1)]
    prof += [(-0.392, 0.7948), (-0.368, 0.7975), (-0.3655, 0.8005), (-0.368, 0.8035), (-0.392, 0.8062)]
    g.prism(af, prof, (1, 2), -IW2 + 0.004, IW2 - 0.004)
    parts = [af]
    if lod == 0:
        for i, x in enumerate((-0.45, -0.15, 0.15, 0.45)):
            st = P("airfoil_post%d" % i, "steel", uv_name="airfoil_post", uv_origin=(x, -0.386, Z_ARM))
            g.box(st, x - 0.012, x + 0.012, -0.392, -0.380, Z_ARM, 0.7955)
            parts.append(st)
    return parts


# =============================================================================
# Panel above the sash: LCD, differential gauge, buttons, lamps, toggle
# =============================================================================
def build_panel(spec):
    lod = spec["lod"]
    c0 = C_PANEL
    parts = []
    pn = P("panel", "panel")
    g.box(pn, -0.50, 0.50, PB - 0.065, PB + 0.065, -0.002, c0, frame=FRONT,
          **(dict(r=0.004, seg=3) if lod == 0 else {}))
    # the rear face with bevels is sunk into the body and never seen, so it needs no atlas space
    bmesh.ops.delete(pn.bm, geom=[f for f in pn.bm.faces if (f.calc_center_median() - FRONT.o).dot(FRONT.n) < 0.0008],
                     context="FACES")
    parts.append(pn)
    if lod == 2:
        return parts
    lx0, lx1, lh = LCD
    if lod == 0:
        bz = P("lcd_bezel", "black")
        for a0, a1, b0, b1 in ((-0.312, -0.108, PB + lh, PB + 0.034), (-0.312, -0.108, PB - 0.034, PB - lh),
                               (-0.312, lx0, PB - lh, PB + lh), (lx1, -0.108, PB - lh, PB + lh)):
            g.box(bz, a0, a1, b0, b1, c0, c0 + 0.0035, frame=FRONT)
        parts.append(bz)
    sc = P("lcd", "black", group=SEL_SCREEN, section="screen")
    cs = c0 + (0.001 if lod == 0 else 0.0005)
    vs = [sc.bm.verts.new(FRONT.p(a, b, cs)) for a, b in ((lx0, PB - lh), (lx1, PB - lh), (lx1, PB + lh), (lx0, PB + lh))]
    sc.tag([face(sc, vs, FRONT.n)])
    sc.glass_frame = (FRONT, lx0, lx1, PB - lh, PB + lh)
    parts.append(sc)
    # differential gauge: chrome rim, scale (a decal in the material), needle - a bone (phase 0 is at zero)
    gx, gb = GAUGE
    n = 20 if lod == 0 else 12
    bzl = P("gauge_bezel", "chrome")
    if lod == 0:
        lathe_f(bzl, [(0.047, 0.0), (0.047, 0.004), (0.0450, 0.0080), (0.0420, 0.0085), (0.0400, 0.0050)], n, gx, gb)
    else:
        g.cyl(bzl, (gx, gb, c0 + 0.0025), "z", 0.047, 0.005, n, frame=FRONT)
    gf = P("gauge_face", "gauge")
    g.cyl(gf, (gx, gb, c0 + 0.0045), "z", 0.0402, 0.001, n, frame=FRONT)
    nd = P("gauge_needle", "needle", group=SEL_NEEDLE)
    ang = math.radians(135.0)                   # start of the make_decals scale (the image: y down, clockwise)
    dx, dy = math.cos(ang), -math.sin(ang)
    px, py = -dy, dx
    L, w, tail = 0.034, 0.0013, 0.008
    poly = [(gx + px * w, gb + py * w), (gx + dx * L, gb + dy * L), (gx - px * w, gb - py * w),
            (gx - dx * tail, gb - dy * tail)]
    g.prism(nd, poly, (0, 1), c0 + 0.0055, c0 + 0.0063, frame=FRONT)
    g.cyl(nd, (gx, gb, c0 + 0.0068), "z", 0.0042, 0.0018, 12 if lod == 0 else 6, frame=FRONT)
    parts += [bzl, gf, nd]
    # lamps: green "work" (ozl_lamp) and red "alarm"
    for a, reg, grp in ((0.215, "lamp_g", SEL_LAMP), (0.265, "lamp_r", "body")):
        lens = P("lamp_" + reg, reg, group=grp)
        if lod == 0:
            ring = P("lamp_ring_" + reg, "chrome", uv_name="lamp_ring", uv_origin=FRONT.p(a, PB - 0.004, 0.0))
            lathe_f(ring, [(0.0120, 0.0), (0.0120, 0.0030), (0.0090, 0.0046)], 10, a, PB - 0.004)
            lathe_f(lens, [(0.0090, 0.0040), (0.0086, 0.0072), (0.0050, 0.0098), (0.0, 0.0106)], 10, a, PB - 0.004)
            parts.append(ring)
        else:
            g.cyl(lens, (a, PB - 0.004, c0 + 0.004), "z", 0.010, 0.008, 8, frame=FRONT)
        parts.append(lens)
    if lod == 1:
        return parts
    # buttons in chrome bushings (the fourth is red)
    for i, a in enumerate((-0.02, 0.035, 0.09, 0.145)):
        o = FRONT.p(a, PB - 0.004, 0.0)
        ring = P("button_ring%d" % i, "chrome", uv_name="button_ring", uv_origin=o)
        lathe_f(ring, [(0.0115, 0.0), (0.0115, 0.0025), (0.0090, 0.0036)], 10, a, PB - 0.004)
        cap = P("button%d" % i, "black" if i < 3 else "needle", uv_name="button" if i < 3 else "button_red", uv_origin=o)
        lathe_f(cap, [(0.0086, 0.0015), (0.0086, 0.0070), (0.0068, 0.0089), (0.0, 0.0092)], 10, a, PB - 0.004)
        parts += [ring, cap]
    # toggle: hex nut, threaded bushing, lever up at 25 degrees, ball at the end
    ta, tb = 0.36, PB - 0.004
    tg = P("toggle", "chrome")
    g.cyl(tg, (ta, tb, c0 + 0.002), "z", 0.0085, 0.004, 6, frame=FRONT)
    g.cyl(tg, (ta, tb, c0 + 0.0075), "z", 0.0052, 0.007, 10, frame=FRONT)
    d = FRONT.n * math.cos(math.radians(25)) + FRONT.v * math.sin(math.radians(25))
    p0, p1 = FRONT.p(ta, tb, c0 + 0.010), FRONT.p(ta, tb, c0 + 0.010) + d * 0.022
    g.tube_var(tg, [tuple(p0), tuple(p1)], [(0.0026, 0.0026), (0.0016, 0.0016)], 8)
    lathe(tg, [(0.0, -0.0032), (0.0028, -0.0016), (0.0028, 0.0016), (0.0, 0.0032)], 8, p1, d)
    parts.append(tg)
    # corner screws
    for i, (a, b) in enumerate(((-0.488, PB + 0.053), (0.488, PB + 0.053), (-0.488, PB - 0.053), (0.488, PB - 0.053))):
        sw = P("panel_screw%d" % i, "chrome", uv_name="panel_screw", uv_origin=FRONT.p(a, b, 0.0))
        lathe_f(sw, [(0.0042, 0.0), (0.0040, 0.0010), (0.0, 0.0022)], 8, a, b)
        parts.append(sw)
    return parts


# =============================================================================
# Top: grille above the panel, filter housing on the roof; nameplate
# =============================================================================
def build_upper(spec):
    lod, bev = spec["lod"], spec["bev"]
    parts = []
    if lod < 2:
        gr = P("front_grille", "grille_v")
        g.box(gr, -0.545, 0.545, 0.972, 1.028, -0.001, 0.002, frame=FRONT)
        parts.append(gr)
    if lod == 0:
        gf = P("front_grille_frame", "steel")
        for a0, a1, b0, b1 in ((-0.555, 0.555, 1.028, 1.036), (-0.555, 0.555, 0.964, 0.972),
                               (-0.555, -0.545, 0.972, 1.028), (0.545, 0.555, 0.972, 1.028)):
            g.box(gf, a0, a1, b0, b1, -0.001, 0.0035, frame=FRONT)
        parts.append(gf)
    roof = P("roof_box", "shell")
    g.box(roof, -0.45, 0.45, 0.0, 0.36, Z_ROOF - 0.002, Z_TOP, **(dict(r=0.008, seg=2) if bev else {}))
    top = roof.region_index("top", *REGIONS["top"])        # top under the grid - sparser
    for f in roof.bm.faces:
        if f.normal.z > 0.7:
            f[roof.reg] = top
    parts.append(roof)
    if lod == 2:
        return parts
    tg = P("roof_grille", "grille_h")
    g.box(tg, -0.40, 0.40, 0.03, 0.33, Z_TOP - 0.003, Z_TOP + 0.0015)
    parts.append(tg)
    if lod == 1:
        return parts
    fl = P("roof_flange", "top")
    g.box(fl, -0.462, 0.462, -0.012, 0.372, Z_ROOF - 0.002, Z_ROOF + 0.010)
    frm = P("roof_grille_frame", "steel")
    for x0, x1, y0, y1 in ((-0.41, 0.41, 0.02, 0.03), (-0.41, 0.41, 0.33, 0.34), (-0.41, -0.40, 0.03, 0.33),
                           (0.40, 0.41, 0.03, 0.33)):
        g.box(frm, x0, x1, y0, y1, Z_TOP - 0.001, Z_TOP + 0.004)
    # filter test port on the face of the housing, red cap
    tp = P("roof_port", "chrome")
    lathe(tp, [(0.012, 0.0), (0.012, 0.004), (0.008, 0.006), (0.008, 0.020)], 10, (0.30, 0.0, 2.075), (0, -1, 0))
    tc = P("roof_port_cap", "cap_red")
    lathe(tc, [(0.0095, 0.016), (0.0095, 0.029), (0.0, 0.031)], 10, (0.30, 0.0, 2.075), (0, -1, 0))
    parts += [fl, frm, tp, tc]
    # nameplate on the lower panel: aluminium on four rivets, no lettering
    pl = P("nameplate", "plate")
    g.box(pl, 0.38, 0.56, YF - 0.0025, YF + 0.001, 0.692, 0.733, r=0.001, seg=1)
    parts.append(pl)
    for i, (x, z) in enumerate(((0.388, 0.700), (0.552, 0.700), (0.388, 0.725), (0.552, 0.725))):
        rv = P("plate_rivet%d" % i, "chrome", uv_name="plate_rivet", uv_origin=(x, YF, z))
        lathe(rv, [(0.0025, 0.0), (0.0, 0.0012)], 6, (x, YF - 0.0025, z), (0, -1, 0))
        parts.append(rv)
    return parts


# =============================================================================
# Chamber: tray, grilles, light, ceiling grid, outlet and taps on the walls
# =============================================================================
def petcock(name, base, nrm, knob):
    """Gas tap on the chamber wall: flange, body out of the wall, barbed nozzle pointing down, a small
    lever on top along the wall (coloured)."""
    base, nrm = Vector(base), Vector(nrm)
    body = P(name, "chrome")
    lathe(body, [(0.016, 0.0), (0.016, 0.003), (0.009, 0.006), (0.009, 0.030), (0.0, 0.031)], 8, base, nrm)
    end = base + nrm * 0.024
    lathe(body, [(0.0055, 0.0), (0.0055, 0.011), (0.0042, 0.013), (0.0048, 0.019), (0.0, 0.024)], 6,
          end - Vector((0.0, 0.0, 0.006)), (0, 0, -1))
    lathe(body, [(0.003, 0.0), (0.003, 0.012)], 6, end + Vector((0.0, 0.0, 0.006)), (0, 0, 1))
    lv = P(name + "_lever", knob)
    g.box(lv, end.x - 0.004, end.x + 0.004, end.y - 0.028, end.y + 0.010, end.z + 0.016, end.z + 0.022,
          r=0.0015, seg=1)
    return [body, lv]


def build_interior(spec):
    lod, bev = spec["lod"], spec["bev"]
    if lod == 2:
        return []
    parts = []
    # floor: three stainless sheets with 5 mm gaps (at the reagent kit's place - wet rings)
    for i, (x0, x1) in enumerate(TRAY_X):
        tp = P("tray%d" % i, "tray")
        g.box(tp, x0, x1, TRAY_Y[0], TRAY_Y[1], Z_WORK, Z_TRAY, **(dict(r=0.0015, seg=1) if lod == 0 else {}))
        parts.append(tp)
    for nm, y0, y1 in (("work_grille_f", -0.369, -0.336), ("work_grille_b", 0.296, 0.329)):
        wg = P(nm, "grille_h", uv_name="work_grille", uv_origin=(0.0, y0, 0.0))
        g.box(wg, -IW2 + 0.02, IW2 - 0.02, y0, y1, Z_WORK, Z_TRAY - 0.0005)
        parts.append(wg)
    # light fixture near the front of the ceiling: housing and diffuser (ozl_lamp - lit in "work")
    lb = P("lamp_box", "lamp_body")
    g.box(lb, -0.52, 0.52, -0.255, -0.135, Z_CEIL - 0.030, Z_CEIL + 0.002, **(dict(r=0.005, seg=1) if bev else {}))
    df = P("lamp_diffuser", "diffuser", group=SEL_LAMP)
    n = 6 if lod == 0 else 2
    prof = [(-0.245 + 0.10 * k / n, Z_CEIL - 0.030 - 0.014 * math.sin(math.pi * k / n)) for k in range(n + 1)]
    prof += [(-0.145, Z_CEIL - 0.029), (-0.245, Z_CEIL - 0.029)]
    g.prism(df, prof, (1, 2), -0.50, 0.50)
    ds = P("downflow", "grille_d")
    g.box(ds, -0.575, 0.575, -0.120, 0.300, Z_CEIL - 0.005, Z_CEIL - 0.001)
    parts += [lb, df, ds]
    if lod == 1:
        return parts
    # right wall: outlet in a box and a tap (blue); left wall - a tap (yellow)
    ob_ = P("outlet_box", "steel")
    g.box(ob_, IW2 - 0.014, IW2, 0.065, 0.135, 0.895, 0.965, r=0.003, seg=1)
    sk = P("outlet", "bakelite")
    lathe(sk, [(0.024, 0.0), (0.024, 0.004), (0.021, 0.008), (0.0, 0.0085)], 16, (IW2 - 0.014, 0.10, 0.93), (-1, 0, 0))
    hl = P("outlet_holes", "black")
    for y in (0.0905, 0.1095):
        disk(hl, (IW2 - 0.0228, y, 0.93), (-1, 0, 0), 0.0024)
    parts += [ob_, sk, hl]
    parts += petcock("petcock_r", (IW2, 0.26, 0.88), (-1, 0, 0), "knob_blue")
    parts += petcock("petcock_l", (-IW2, 0.05, 0.88), (1, 0, 0), "knob_yellow")
    return parts


# =============================================================================
# Stand: tubes, feet, lower shelf; drain tap
# =============================================================================
def build_stand(spec):
    lod = spec["lod"]
    parts = []
    z_leg0 = FOOT_Z if lod < 2 else 0.0
    for i, (s_x, s_y) in enumerate(LEGS):
        cx, cy = s_x * 0.58, s_y * 0.32
        lg = P("leg%d" % i, "stand", uv_name="leg", uv_origin=(cx, cy, 0.0))
        if lod == 0:
            sq_tube(lg, "z", z_leg0, Z_ST - 0.001, cx, cy, 0.02, 0.004, 3)
        else:
            g.box(lg, cx - 0.02, cx + 0.02, cy - 0.02, cy + 0.02, z_leg0, Z_ST - 0.001)
        parts.append(lg)
    sh = P("low_shelf", "stand")
    g.box(sh, -0.56, 0.56, -0.30, 0.30, Z_LOW - 0.003, Z_LOW)
    if lod == 0:
        for s_y in (-1, 1):
            g.box(sh, -0.56, 0.56, *sx(0.2965, 0.2995, s_y), Z_LOW - 0.028, Z_LOW - 0.003)
    parts.append(sh)
    # crossbars: the lower ones under the shelf, the upper ones under the body - near LOD only
    zr0, zr1 = 0.139, Z_LOW - 0.0035
    for s_y in (-1, 1):
        rl = P("rail_x%d" % (s_y + 1), "stand", uv_name="rail_x", uv_origin=(0.0, s_y * 0.32, 0.0))
        if lod == 0:
            sq_tube(rl, "x", -0.56, 0.56, s_y * 0.32, (zr0 + zr1) / 2, 0.015, 0.004, 2)
            ru = P("rail_xu%d" % (s_y + 1), "stand", uv_name="rail_xu", uv_origin=(0.0, s_y * 0.32, 0.0))
            g.box(ru, -0.56, 0.56, *sx(0.30, 0.34, s_y), Z_ST - 0.04, Z_ST - 0.001)
            parts.append(ru)
        else:
            g.box(rl, -0.56, 0.56, *sx(0.30, 0.34, s_y), zr0, zr1)
        parts.append(rl)
    for s_x in (-1, 1):
        rl = P("rail_y%d" % (s_x + 1), "stand", uv_name="rail_y", uv_origin=(s_x * 0.58, 0.0, 0.0))
        if lod == 0:
            sq_tube(rl, "y", -0.30, 0.30, s_x * 0.58, (zr0 + zr1) / 2, 0.015, 0.004, 2)
            ru = P("rail_yu%d" % (s_x + 1), "stand", uv_name="rail_yu", uv_origin=(s_x * 0.58, 0.0, 0.0))
            g.box(ru, *sx(0.56, 0.60, s_x), -0.30, 0.30, Z_ST - 0.04, Z_ST - 0.001)
            parts.append(ru)
        else:
            g.box(rl, *sx(0.56, 0.60, s_x), -0.30, 0.30, zr0, zr1)
        parts.append(rl)
    if lod == 2:
        return parts
    # adjustable feet: tube plug, stud, nut, plastic heel
    for i, (s_x, s_y) in enumerate(LEGS):
        cx, cy = s_x * 0.58, s_y * 0.32
        ft = P("foot%d" % i, "black", uv_name="foot", uv_origin=(cx, cy, 0.0))
        if lod == 1:
            g.box(ft, cx - 0.02, cx + 0.02, cy - 0.02, cy + 0.02, 0.0, FOOT_Z)
            parts.append(ft)
            continue
        st = P("foot_stud%d" % i, "steel", uv_name="foot_stud", uv_origin=(cx, cy, 0.0))
        g.box(ft, cx - 0.0205, cx + 0.0205, cy - 0.0205, cy + 0.0205, FOOT_Z - 0.004, FOOT_Z + 0.002)
        lathe(ft, [(0.0, 0.0), (0.025, 0.0), (0.025, 0.0075), (0.021, 0.0105), (0.0, 0.0105)], 12, (cx, cy, 0.0))
        lathe(st, [(0.0055, 0.010), (0.0055, FOOT_Z - 0.004)], 6, (cx, cy, 0.0))
        g.cyl(st, (cx, cy, 0.030), "z", 0.0115, 0.008, 6)
        parts += [ft, st]
    if lod == 0:
        # drain tap under the front: pipe from the bottom, ball valve, lever with a red handle toward the person
        x, y = DRAIN
        dv = P("drain", "chrome")
        lathe(dv, [(0.0075, 0.0), (0.0075, 0.026)], 8, (x, y, Z_ST - 0.025))
        lathe(dv, [(0.0, 0.0), (0.012, 0.0), (0.013, 0.004), (0.013, 0.026), (0.012, 0.030), (0.0, 0.030)], 10,
              (x, y, Z_ST - 0.055))
        lathe(dv, [(0.0062, 0.0), (0.0062, 0.022), (0.0, 0.022)], 8, (x, y, Z_ST - 0.055), (0, 0, -1))
        g.box(dv, x - 0.004, x + 0.004, y - 0.040, y - 0.010, Z_ST - 0.044, Z_ST - 0.038)
        hd = P("drain_handle", "cap_red")
        g.box(hd, x - 0.006, x + 0.006, y - 0.075, y - 0.036, Z_ST - 0.046, Z_ST - 0.036, r=0.002, seg=1)
        parts += [dv, hd]
    return parts


# =============================================================================
# Side shelf (place of centrifuge M45) and the outlet on the side
# =============================================================================
def build_shelf(spec):
    lod, bev = spec["lod"], spec["bev"]
    parts = []
    sh = P("side_shelf", "steel")
    g.box(sh, X_SH0 + 0.004, X_SH1 - 0.004, -0.32, 0.32, Z_SH, SH_TOP, **(dict(r=0.003, seg=2) if bev else {}))
    parts.append(sh)
    if lod == 2:
        return parts
    br = P("shelf_brackets", "stand")
    for s in (-1, 1):
        y = s * 0.262
        if lod == 0:
            g.sweep(br, [(W2 + 0.006, y, Z_SH - 0.215), (X_SH1 - 0.07, y, Z_SH - 0.010)], (0, 1, 0), 0.011, 0.002)
            g.box(br, X_SH0 + 0.004, X_SH1 - 0.05, y - 0.005, y + 0.005, Z_SH - 0.016, Z_SH)
            g.box(br, W2, W2 + 0.004, y - 0.013, y + 0.013, Z_SH - 0.245, Z_SH - 0.185, r=0.001, seg=1)
        else:
            g.prism(br, [(X_SH0, Z_SH), (X_SH1 - 0.05, Z_SH), (X_SH0, Z_SH - 0.22)], (0, 2), y - 0.008, y + 0.008)
    parts.append(br)
    mt = P("shelf_mat", "mat")
    g.box(mt, X_SH0 + 0.020, X_SH1 - 0.022, -0.296, 0.296, SH_TOP, MAT_TOP, **(dict(r=0.0015, seg=1) if lod == 0 else {}))
    parts.append(mt)
    if lod == 1:
        return parts
    # rolled edge on three sides, piano hinge at the wall
    lip = P("shelf_lip", "steel")
    zl = SH_TOP + 0.002
    path = rounded([(X_SH0 + 0.012, -0.316, zl), (X_SH1 - 0.008, -0.316, zl), (X_SH1 - 0.008, 0.316, zl),
                    (X_SH0 + 0.012, 0.316, zl)], 0.02, 2, closed=False)
    g.pipe(lip, path, 0.0045, 6)
    hg = P("shelf_hinge", "steel")
    for k in range(3):
        y0, y1 = -0.31 + 0.62 * k / 3 + 0.002, -0.31 + 0.62 * (k + 1) / 3 - 0.002
        g.cyl(hg, (X_SH0 + 0.006, (y0 + y1) / 2, Z_SH - 0.002), "y", 0.0055, y1 - y0, 8)
    g.box(hg, W2, W2 + 0.003, -0.31, 0.31, Z_SH - 0.040, Z_SH - 0.004)
    parts += [lip, hg]
    # surface-mounted outlet on the cabinet side (centrifuge cord), the wire tube goes into the wall
    sy, sz = SOCK
    so = P("socket", "bakelite")
    lathe(so, [(0.034, 0.0), (0.034, 0.009), (0.029, 0.018), (0.020, 0.0222), (0.0, 0.0228)], 18, (W2, sy, sz), (1, 0, 0))
    hl = P("socket_holes", "black")
    for y in (sy - 0.0095, sy + 0.0095):
        disk(hl, (W2 + 0.0230, y, sz), (1, 0, 0), 0.0024)
    cd = P("socket_conduit", "bakelite")
    g.pipe(cd, spline([(W2 + 0.012, sy, sz + 0.026), (W2 + 0.012, sy, sz + 0.09), (W2 + 0.008, sy, sz + 0.13),
                       (W2 + 0.001, sy, sz + 0.15)], 2), 0.0065, 6)
    lathe(cd, [(0.011, 0.0), (0.011, 0.004), (0.0, 0.006)], 12, (W2, sy, sz + 0.15), (1, 0, 0))
    parts += [so, hl, cd]
    return parts


# =============================================================================
# Power cable at the back: gland, smooth curve to the floor, plug
# =============================================================================
def build_cable(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    pts = [(0.48, YB + 0.022, 0.70), (0.48, YB + 0.05, 0.685), (0.475, YB + 0.075, 0.62), (0.47, YB + 0.085, 0.40),
           (0.468, YB + 0.09, 0.15), (0.46, YB + 0.10, 0.045), (0.44, YB + 0.13, 0.008), (0.38, YB + 0.22, 0.007),
           (0.28, YB + 0.27, 0.010), (0.17, YB + 0.28, 0.017)]
    c = P("cable", "cable")
    if lod == 1:
        g.pipe(c, pts[::3], 0.0055, 4)
        return [c]
    g.pipe(c, spline(pts, 2), 0.0055, 6)
    gl = P("cable_gland", "black")
    lathe(gl, [(0.0125, 0.0), (0.0125, 0.007), (0.008, 0.024), (0.0065, 0.030)], 10, (0.48, YB, 0.70), (0, 1, 0))
    # plug: body along the cable, two pins
    end, prev = Vector(pts[-1]), Vector(pts[-2])
    d = (end - prev).normalized()
    pl = P("plug", "black")
    lathe(pl, [(0.0062, -0.004), (0.0075, 0.0), (0.014, 0.014), (0.017, 0.022), (0.017, 0.042), (0.0, 0.045)], 12, end, d)
    pins = P("plug_pins", "steel")
    side = d.cross(Vector((0.0, 0.0, 1.0))).normalized()
    for s in (-1, 1):
        a = end + d * 0.044 + side * (0.0095 * s)
        g.pipe(pins, [tuple(a), tuple(a + d * 0.019)], 0.002, 6)
    return [c, gl, pl, pins]


# =============================================================================
# Own props: lifting table under the loupe, Petri dish tray, kidney tray, sealer
# =============================================================================
def build_jack(spec):
    """Laboratory lifting table (slot 1 is empty and stays the loupe's place): two 180 x 180 plates,
    scissors at the sides, a screw with a knurled handle on the left (toward the wall)."""
    lod = spec["lod"]
    if lod == 2:
        return []
    x0, x1, y0, y1 = MX1 - 0.09, MX1 + 0.09, MY1 - 0.09, MY1 + 0.09
    pl = P("jack_plates", "alu")
    rb = dict(r=0.0015, seg=1) if lod == 0 else {}
    g.box(pl, x0, x1, y0, y1, Z_TRAY, Z_TRAY + 0.006, **rb)
    g.box(pl, x0, x1, y0, y1, MZ1 - 0.006, MZ1, **rb)
    if lod == 1:
        g.box(pl, x0 + 0.02, x1 - 0.02, y0 + 0.03, y1 - 0.03, Z_TRAY + 0.006, MZ1 - 0.006)
        return [pl]
    za, zb = Z_TRAY + 0.012, MZ1 - 0.012
    arm = P("jack_arms", "steel")
    hb = P("jack_blocks", "alu")
    for xs in (MX1 - 0.072, MX1 + 0.072):
        for ya, yb, dx in ((MY1 - 0.068, MY1 + 0.068, 0.0035), (MY1 + 0.068, MY1 - 0.068, -0.0035)):
            g.sweep(arm, [(xs + dx, ya, za), (xs + dx, yb, zb)], (1, 0, 0), 0.0055, 0.0015)
        # guides under the plates: the scissor ends run in them
        g.box(hb, xs - 0.009, xs + 0.009, MY1 - 0.078, MY1 + 0.078, Z_TRAY + 0.006, Z_TRAY + 0.016)
        g.box(hb, xs - 0.009, xs + 0.009, MY1 - 0.078, MY1 + 0.078, MZ1 - 0.016, MZ1 - 0.006)
    zc = (za + zb) / 2
    sc = P("jack_screw", "steel")
    g.cyl(sc, (MX1 - 0.01, MY1, zc), "x", 0.0035, 0.19, 8)
    kn = P("jack_knob", "black")
    lathe(kn, [(0.0, 0.0), (0.0125, 0.0), (0.0125, 0.016), (0.010, 0.019), (0.0, 0.0195)], 16,
          (MX1 - 0.105, MY1, zc), (-1, 0, 0), rib=0.0008)
    return [pl, arm, hb, sc, kn]


def build_dishes(spec):
    """Stainless tray with a rolled edge and three Petri dishes: an open one with a piece of tissue, its lid
    next to it upside down, and a closed one."""
    lod = spec["lod"]
    if lod == 2:
        return []
    x0, x1, y0, y1, h = PTRAY
    tr = P("petri_tray", "steel")
    parts = [tr]
    if lod == 1:
        g.box(tr, x0, x1, y0, y1, Z_TRAY, Z_TRAY + 0.006)
    else:
        open_box(tr, x0, x1, y0, y1, Z_TRAY, Z_TRAY + h, 0.0012)
        zr = Z_TRAY + h                                     # edge bent outward
        for a0, a1, b0, b1 in ((x0 - 0.005, x1 + 0.005, y0 - 0.005, y0), (x0 - 0.005, x1 + 0.005, y1, y1 + 0.005),
                               (x0 - 0.005, x0, y0, y1), (x1, x1 + 0.005, y0, y1)):
            g.box(tr, a0, a1, b0, b1, zr - 0.0012, zr)
    zb = Z_TRAY + (0.0012 if lod == 0 else 0.006)
    n = 18 if lod == 0 else 8
    for i, ((cx, cy), kind) in enumerate(DISHES):
        d = P("petri%d" % i, "petri", uv_name="petri_" + kind, uv_origin=(cx, cy, zb))
        c = (cx, cy, zb)
        if lod == 1:
            g.cyl(d, (cx, cy, zb + 0.006), "z", 0.045 if kind != "lid" else 0.047, 0.012 if kind != "lid" else 0.008, n)
        elif kind == "lid":
            lathe(d, [(0.0, 0.0), (0.047, 0.0), (0.047, 0.008), (0.046, 0.008), (0.046, 0.0012), (0.0, 0.0012)], n, c)
        else:
            lathe(d, [(0.0, 0.0), (0.045, 0.0), (0.045, 0.012), (0.0438, 0.012), (0.0438, 0.0018), (0.0, 0.0018)], n, c)
            if kind == "closed":
                lathe(d, [(0.0460, 0.0065), (0.0470, 0.0065), (0.0470, 0.0148), (0.0, 0.0148)], n, c)
        parts.append(d)
        if kind == "open" and lod == 0:
            ts = P("tissue", "tissue")
            blob(ts, (cx + 0.004, cy - 0.003, zb + 0.0018), 0.024, 0.017, 0.008, 12, 4, seed=1.3)
            blob(ts, (cx - 0.022, cy + 0.016, zb + 0.0018), 0.008, 0.006, 0.004, 8, 2, seed=4.1)
            parts.append(ts)
    return parts


def kidney(n, k=1.0, A=0.13, B=0.062, D=0.072):
    """Outline of the kidney tray (counter-clockwise): an ellipse dented on one side."""
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n
        s = math.sin(t)
        out.append((k * A * math.cos(t), k * (B * s - (D * s ** 3 if s > 0 else 0.0))))
    return out


def build_kidney(spec):
    """Stainless kidney tray (walls flare upward, rolled edge) with a scalpel and tweezers in it."""
    lod = spec["lod"]
    if lod == 2:
        return []
    cx, cy = KIDNEY
    kd = P("kidney", "steel")
    n = 20 if lod == 0 else 12
    depth = 0.032
    if lod == 1:
        g.prism(kd, [(cx + x, cy + y) for x, y in kidney(n, 0.95)], (0, 1), Z_TRAY, Z_TRAY + 0.02)
        return [kd]
    bm = kd.bm
    new = []
    for k_bot, k_top, z0, inward in ((0.82, 1.0, 0.0, False), (0.808, 0.988, 0.0012, True)):
        lo = [bm.verts.new((cx + x, cy + y, Z_TRAY + z0)) for x, y in kidney(n, k_bot)]
        hi = [bm.verts.new((cx + x, cy + y, Z_TRAY + depth)) for x, y in kidney(n, k_top)]
        for i in range(n):
            j = (i + 1) % n
            ex, ey = hi[j].co.x - hi[i].co.x, hi[j].co.y - hi[i].co.y
            want = (ey, -ex, 0.0) if not inward else (-ey, ex, 0.0)
            new.append(face(kd, [lo[i], lo[j], hi[j], hi[i]], want))
        new.append(face(kd, lo[::-1], (0, 0, 1) if inward else (0, 0, -1)))
    # flat edge bent outward between the inner and outer wall
    a = [bm.verts.new((cx + x, cy + y, Z_TRAY + depth)) for x, y in kidney(n, 0.988)]
    b = [bm.verts.new((cx + x, cy + y, Z_TRAY + depth)) for x, y in kidney(n, 1.045)]
    for i in range(n):
        j = (i + 1) % n
        new.append(face(kd, [a[i], a[j], b[j], b[i]], (0, 0, 1)))
    kd.tag(new)
    # scalpel: flat handle and a blade with a convex edge; tweezers - two tapering arms
    zf = Z_TRAY + 0.0012
    sc = P("scalpel", "chrome")
    sx0, sy0, sa = cx - 0.035, cy - 0.022, 6.0
    g.prism(sc, rot2([(-0.058, -0.0042), (0.040, -0.0045), (0.044, -0.0030), (0.044, 0.0030), (0.040, 0.0045),
                      (-0.058, 0.0042), (-0.061, 0.0)], sx0, sy0, sa), (0, 1), zf, zf + 0.0025)
    g.prism(sc, rot2([(0.044, 0.0028), (0.074, 0.0028), (0.083, 0.0004), (0.079, -0.0028), (0.064, -0.0042),
                      (0.044, -0.0030)], sx0, sy0, sa), (0, 1), zf + 0.0008, zf + 0.0012)
    fc = P("forceps", "chrome")
    fx0, fy0, fa = cx + 0.020, cy - 0.044, -4.0
    for s in (-1, 1):
        g.prism(fc, rot2([(-0.060, 0.0005 * s), (-0.060, 0.0040 * s), (0.055, 0.0018 * s + 0.0035 * s),
                          (0.058, 0.0035 * s)], fx0, fy0, fa), (0, 1), zf, zf + 0.0022)
    g.prism(fc, rot2([(-0.066, -0.0042), (-0.054, -0.0042), (-0.054, 0.0042), (-0.066, 0.0042)], fx0, fy0, fa), (0, 1),
            zf, zf + 0.0030)
    return [kd, sc, fc]


def build_sealer(spec):
    """Impulse bag sealer (~300 x 90 mm): body with a bevelled front, a Teflon strip over the heater, a
    lever hinged at the back (bone ozl_arm, raised at rest), a silicone pressure strip, a timer knob, a
    heating lamp (ozl_lamp_2), feet; in front of it - a sealed bag with a sample."""
    lod = spec["lod"]
    if lod == 2:
        return []
    x0, x1, y0, y1 = SEAL
    zt = Z_TRAY + SEAL_H
    hy, hz = HINGE
    piv = Vector((0.0, hy, hz))
    lift = Matrix.Translation(piv) @ Matrix.Rotation(-math.radians(ARM_OPEN), 4, (1, 0, 0)) @ Matrix.Translation(-piv)
    body = P("sealer", "sealer")
    arm = P("sealer_arm", "sealer", group=SEL_ARM)
    parts = [body, arm]
    xa0, xa1 = x0 + 0.012, x1 - 0.045                       # lever: the timer panel is on the right
    if lod == 1:
        g.box(body, x0, x1, y0, y1, Z_TRAY, zt)
        g.box(arm, xa0, xa1, y0 + 0.024, y1 - 0.004, zt + 0.004, zt + 0.018)
        transform(arm, lift)
        return parts
    prof = rounded([(y0, Z_TRAY + 0.006), (y1, Z_TRAY + 0.006), (y1, zt), (y0 + 0.030, zt), (y0, zt - 0.022)],
                   [0.003, 0.003, 0.006, 0.006, 0.004], 2)
    g.prism(body, prof, (1, 2), x0, x1)
    g.bevel(body.bm, [e for e in body.bm.edges if all(abs(v.co.x - x0) < 1e-6 for v in e.verts) or
                      all(abs(v.co.x - x1) < 1e-6 for v in e.verts)], 0.004, 1)
    bar = P("sealer_bar", "teflon")
    g.box(bar, xa0 + 0.01, xa1 - 0.01, y0 + 0.032, y0 + 0.044, zt - 0.001, zt + 0.004, r=0.0012, seg=1)
    # lever: flat cover with a visor at the front, a silicone strip underneath over the Teflon
    aprof = rounded([(y1 - 0.004, zt + 0.006), (y0 + 0.030, zt + 0.006), (y0 + 0.022, zt + 0.002),
                     (y0 + 0.020, zt + 0.014), (y0 + 0.034, zt + 0.020), (y1 - 0.004, zt + 0.020)],
                    [0.003, 0.002, 0.002, 0.004, 0.006, 0.005], 2)
    g.prism(arm, aprof, (1, 2), xa0, xa1)
    g.bevel(arm.bm, [e for e in arm.bm.edges if all(abs(v.co.x - xa0) < 1e-6 for v in e.verts) or
                     all(abs(v.co.x - xa1) < 1e-6 for v in e.verts)], 0.003, 1)
    pad = P("sealer_pad", "silicone", group=SEL_ARM)
    g.box(pad, xa0 + 0.012, xa1 - 0.012, y0 + 0.033, y0 + 0.043, zt + 0.0045, zt + 0.0062)
    transform(arm, lift)
    transform(pad, lift)
    hgs = P("sealer_hinges", "chrome")
    for xh in (xa0 + 0.02, xa1 - 0.02):
        g.box(hgs, xh - 0.008, xh + 0.008, hy - 0.008, y1 + 0.002, zt - 0.002, hz + 0.004)
        g.cyl(hgs, (xh, hy, hz), "x", 0.0045, 0.024, 8)
    # panel on the right: timer knob (knurled) and heating lamp
    kn = P("sealer_knob", "black")
    lathe(kn, [(0.0, 0.0), (0.012, 0.0), (0.012, 0.012), (0.0105, 0.015), (0.0, 0.0155)], 12,
          (x1 - 0.022, y0 + 0.060, zt), rib=0.0007)
    lr = P("sealer_lamp_ring", "chrome")
    lathe(lr, [(0.0075, 0.0), (0.0075, 0.0025), (0.0060, 0.0035)], 10, (x1 - 0.022, y1 - 0.022, zt))
    ll = P("sealer_lamp", "amber", group=SEL_LAMP2)
    lathe(ll, [(0.0060, 0.0030), (0.0056, 0.0055), (0.0, 0.0074)], 10, (x1 - 0.022, y1 - 0.022, zt))
    ft = P("sealer_feet", "rubber")
    for fx in (x0 + 0.02, x1 - 0.02):
        for fy in (y0 + 0.015, y1 - 0.015):
            g.box(ft, fx - 0.008, fx + 0.008, fy - 0.008, fy + 0.008, Z_TRAY, Z_TRAY + 0.0065)
    parts += [pad, bar, hgs, kn, lr, ll, ft]
    # sealed bag: film, edge seam, sample inside
    bx0, bx1, by0, by1 = BAG
    bg = P("bag", "bag")
    g.box(bg, bx0, bx1, by0, by1, Z_TRAY, Z_TRAY + 0.0016, r=0.0006, seg=1)
    g.box(bg, bx0 + 0.002, bx1 - 0.002, by1 - 0.012, by1 - 0.004, Z_TRAY + 0.0016, Z_TRAY + 0.0021)
    ts = P("bag_tissue", "tissue")
    blob(ts, ((bx0 + bx1) / 2 - 0.005, (by0 + by1) / 2 - 0.006, Z_TRAY + 0.0016), 0.020, 0.014, 0.006, 12, 3, seed=2.2)
    parts += [bg, ts]
    return parts


# =============================================================================
# Lower stand shelf: jerrycan and carton (the GP-5 is vanilla)
# =============================================================================
def build_lower(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    x0, x1, y0, y1, h = CAN
    cn = P("canister", "canister")
    g.box(cn, x0, x1, y0, y1, Z_LOW, Z_LOW + h, **(dict(r=0.022, seg=3) if lod == 0 else {}))
    cb = P("carton", "cardboard")
    cx0, cx1, cy0, cy1, ch = CARTON
    g.box(cb, cx0, cx1, cy0, cy1, Z_LOW, Z_LOW + ch, **(dict(r=0.003, seg=1) if lod == 0 else {}))
    parts = [cn, cb]
    if lod == 1:
        return parts
    # jerrycan: bracket handle on top, neck with a ribbed cap
    hd = P("canister_handle", "canister")
    yh, zt = y1 - 0.05, Z_LOW + h
    g.pipe(hd, spline([(x0 + 0.05, yh, zt - 0.012), (x0 + 0.065, yh, zt + 0.034), (x0 + 0.09, yh, zt + 0.045),
                       (x1 - 0.05, yh, zt + 0.045), (x1 - 0.025, yh, zt + 0.034), (x1 - 0.012, yh, zt - 0.012)], 2),
           0.010, 6)
    nk = P("canister_neck", "canister")
    lathe(nk, [(0.021, -0.004), (0.021, 0.010)], 12, (x0 + 0.05, y0 + 0.05, zt))
    cp = P("canister_cap", "cap_blue")
    lathe(cp, [(0.021, 0.008), (0.0245, 0.008), (0.0245, 0.027), (0.0, 0.0295)], 20, (x0 + 0.05, y0 + 0.05, zt),
          rib=0.0012)
    # carton: tape along the lid and over the ends
    tp = P("carton_tape", "tape")
    ccy, top = (cy0 + cy1) / 2, Z_LOW + ch
    g.box(tp, cx0 + 0.002, cx1 - 0.002, ccy - 0.024, ccy + 0.024, top, top + 0.0007)
    g.box(tp, cx0 - 0.0007, cx0, ccy - 0.024, ccy + 0.024, top - 0.06, top)
    g.box(tp, cx1, cx1 + 0.0007, ccy - 0.024, ccy + 0.024, top - 0.06, top)
    return parts + [hd, nk, cp, tp]


def build_lod(spec):
    parts = [build_shell(spec)]
    if spec["lod"] < 2:
        parts.append(build_glass())
    parts += build_sash(spec) + build_airfoil(spec) + build_panel(spec) + build_upper(spec)
    parts += build_interior(spec) + build_stand(spec) + build_shelf(spec) + build_cable(spec)
    parts += build_jack(spec) + build_dishes(spec) + build_kidney(spec) + build_sealer(spec) + build_lower(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    return parts


def collision():
    """Geometry LOD as in the version accepted in game: the bottom (stand with shelf) as a box, the top as
    a profile prism with the filter housing."""
    prof = [(YF, 0.91), (YB, 0.91), (YB, Z_ROOF), (y_front(Z_ROOF), Z_ROOF), (YF, Z_OPEN)]
    lower = kx.box_pts(-W2, X_SH1, YF, YB, 0.0, 0.91)
    upper = kx.prism_pts(prof, -W2, W2) + kx.box_pts(-0.45, 0.45, 0.0, 0.36, Z_ROOF, Z_TOP)
    metal = kx.PEN + r"\metalplate.rvmat"
    memory = {
        "invView": [(0.0, -2.6, 1.15)],
        "ce_center": [(0.15, 0.0, Z_TOP / 2)],
        "ce_radius": [(0.15 + 1.25, 0.0, Z_TOP / 2)],
        # needle axis points from the dial to the face (as in M08, M14); lever axis is along -x
        "ozl_needle_axis": [tuple(NEEDLE_HUB + FRONT.n * 0.005), tuple(NEEDLE_HUB + FRONT.n * 0.055)],
        "ozl_arm_axis": [(SEAL[1] - 0.04, HINGE[0], HINGE[1]), (SEAL[0] + 0.01, HINGE[0], HINGE[1])],
    }
    for i, m in enumerate(MODS):
        memory["module_%d" % (i + 1)] = [m]
    # preview and drop framing use the device itself (without the cable), with the armrest
    return [(lower, metal), (upper, metal)], 150.0, memory, (-W2, X_SH1, YF - 0.03, YB, 0.0, Z_TOP)


# the first six are for the --look preview: overview with the modules in place (the same angle with empty slots),
# the panel (in "work": screen frame, needle, green lamp), the sealer close-up through the opening (in
# "work": lever pressed, heating lamp lit), chamber close-up, the shelf with the centrifuge
SHOTS = [
    ("front", (-1.6, -3.0, 1.6), (0.0, 0.0, 1.1), 30),
    ("slots", (0.95, -1.6, 1.50), (0.10, -0.05, 0.92), 30),
    ("panel", (0.0, -1.50, 1.60), (0.0, -0.28, 1.68), 36),
    ("sealer", (0.36, -0.80, 1.00), (0.46, 0.15, 0.80), 45),
    ("inside", (-0.05, -1.10, 1.25), (-0.02, -0.03, 0.84), 30),
    ("shelf", (1.75, -1.05, 1.35), (0.79, 0.05, 0.98), 34),
    ("stand", (-1.0, -1.7, 0.55), (0.0, 0.0, 0.32), 32),
    ("back", (1.8, 2.8, 1.6), (0.0, 0.0, 1.0), 30),
]

M.look_shots = (6, 4)
M.run(build_lod, collision, SHOTS, row_step=2.0, row_shot=((2.0, -7.5, 2.2), (2.0, 0.0, 1.0)))
