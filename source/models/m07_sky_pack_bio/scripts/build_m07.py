"""M07 - freezer chest with a film isolator: the Clear Sky Bio Packer (OZL_Sky_Pack_Bio).
Packer: cargo 10x10, three module places (module_1..3) and proxies for the modules at the same
places. Each module of the Bio line has its own slot and working place: slot 1 - binocular loupe M44
in the isolator at the left, eyepieces right against the face film; slot 2 - centrifuge M45 on the
shelf of the left end, its cord goes to an outlet on the end; slot 3 - reagent kit M46 in the
isolator at the right, by the airlock. The built-in box and the tube rack are gone (M46 replaces
them); an empty slot shows a rubber mat (and the outlet at slot 2).

    blender --background --python build_m07.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (thermometer display and its frames,
panel scale, sign, tag).

Look: "dayz" (matte, dirtier, coloured AO). The chest is rounded (R32 corners, a lid with a rounded
edge, a recessed plinth on feet). Foil is wrapped around the front left corner (crumpled, torn edges,
pressed with tape), a separate sheet at the back. The isolator film is inflated into pillows between
the frame arcs; the sleeve rings and the airlock cut through it (holes under the flanges); the
sleeves with hands lie on the board. The corrugated hose goes around the airlock on the right and
below (it does not cover it) to the fan. The cables are smooth: a thick one to the generator (plug on
the floor), the fan cord and the end outlet cable are spliced into it under tape. Small props are
vanilla items through proxies (kvanilla): in the isolator a syringe, a vial, a blood test kit, a
disinfectant spray; paper with a pen on the shelf; tape on the lid.

The chest is the B2 base: a shop freezer chest of the 1970-90s, 1500 x 860 x 680 mm (width x height
x depth). No data sheets of Soviet chests of that era were found (LN-400, Snezhinka, GDR dkk GT -
only photos), so the sizes follow the volume class of the Biryusa of the same type: CF32 (320 l) -
1085 x 885 x 665 mm, B-560KX (510 l) - 1790 x 810 x 665 mm. A chest of ~420 l between them is ~1.5 m
wide; depth is ~0.665 for all, height 0.81-0.89. Rounded corners and the bracket handle on the front
edge of the lid follow photos of GDR chests.

The isolator follows flexible film isolators (CBC, UTMB): a soft transparent hood on a tube frame, a
rigid tray, glove sleeve rings with clamps, a cylindrical airlock at the side with a clamp and lid,
a filter cartridge, a blower on a hose. The Tailin LS1-2S-G4 chamber is 1500 x 780 x 870 mm; on the
chest the hood is shortened to the lid: 1.20 x 0.62 x 0.50 m, glove axes at 1.15 m above the floor
0.45 m apart (as in M03), sleeve rings of diameter 0.21 m (flange 0.23). The airlock is diameter
0.24 m (flange 0.29), the filter cartridge diameter 0.11 on its collar, a corrugated hose of
diameter 52 to an axial fan of diameter 0.18 m on the chest lid.

Work look: the thermometer display is ozl_screen, own texture (section screen): "off" is an empty
display, "work" plays frames _screen_fN (OZL_WorkFx frames, 0.5 s each); the "power" lamp (green) is
ozl_lamp_work, lit (onSelections); the compressor lamp (yellow) is ozl_lamp, blinks (blink); the fan
blades are the bone ozl_fan on the source ozl_work: a model.cfg loop (sourceAddress loop, maxValue
1/4) - 4 turns per 2 s pass (animPeriod in the mod config), 2 rev/s: with five blades (72 degrees
apart) at 30 fps it is 24 degrees per frame, so the rotation does not appear to run backward. At
rest everything is off and still.

Blender axes: X is width, Y is depth (face toward -Y), Z is up.
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

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
CX0, CX1, CY0, CY1 = -0.75, 0.75, -0.34, 0.34                # chest
ZFOOT, ZB, ZG, ZL = 0.03, 0.075, 0.80, 0.86                  # plinth bottom, body bottom, lid seam, lid top
LIP, RCH = 0.006, 0.032                                      # lid overhang, rounding of the vertical corners
# isolator
XI0, XI1 = -0.68, 0.52                                       # hood along x
XIC = (XI0 + XI1) / 2
YF, YB = -0.31, 0.31                                         # film: face and back
ZT = ZL + 0.035                                              # top of the tray, bottom of the film
ZW, RC = 1.27, 0.13                                          # top of the vertical wall, bend radius
ZR = ZW + RC                                                 # hood roof
PX, PZ = (XIC - 0.225, XIC + 0.225), 1.15                    # glove rings
RH = 0.090                                                   # film hole under a ring (in the wall of the ring tube)
HOOPS = (XI0, XIC, XI1)                                      # frame arcs
TR, HOFF = 0.011, 0.020                                      # frame tube, its axis outside the film
# airlock (x axis) and filter
LZ, LR = 1.13, 0.12                                          # airlock axis, collar radius
LC1, LS1 = XI1 + 0.082, XI1 + 0.215                          # collar end, sleeve end
LCAP = LS1 + 0.020                                           # start of the lid
RHL = 0.112                                                  # end film hole under the airlock (collar wall)
FX = XI1 + 0.04                                              # filter cartridge on the collar
FZ0, FZ1 = LZ + LR + 0.006, LZ + LR + 0.19                   # bottom and top of the cartridge
FSZ = FZ1 - 0.06                                             # filter nozzle axis (sideways, toward the hose)
# fan: axis along y, the guard toward the player
FAN = Vector((0.655, -0.24, ZL + 0.112))
FAN_TURNS = 4                                                # blade turns per loop pass
# module shelf on the left end, the outlet above it
SX0, SX1, SZ = CX0 - 0.28, CX0 - 0.014, 0.70
SOCK = (0.040, 0.755)                                        # y, z
# board in the isolator
BDX, BDY, BDZ = (-0.42, 0.24), (-0.20, 0.26), ZT + 0.02
# chest control panel, thermometer
PNX, PNZ = (0.40, 0.70), (0.66, 0.76)
KNOB = (0.48, 0.71)
LAMPS = ((0.655, "lamp_g"), (0.61, "lamp_o"))                # x and region; z as for the knob
TH = (0.10, 0.21, 0.56, 0.62)                                # thermometer x0, x1, z0, z1
LCD = (TH[0] + 0.012, TH[1] - 0.012, TH[2] + 0.018, TH[3] - 0.010)
# module places (the proxy point is the middle of the module bottom): slot 1 - loupe M44 (its
# eyepieces are 0.096 ahead of the origin) - 12 mm from the film; slot 2 - centrifuge M45 on the
# shelf; slot 3 - kit M46 by the airlock
MODS = [(-0.53, YF + 0.096 + 0.012, ZT + 0.003), ((SX0 + SX1) / 2, -0.135, SZ + 0.001), (0.37, 0.01, ZT + 0.003)]
MOD_OBJ = [("m44_tool_optics", "ozr_tool_optics"), ("m45_centrifuge", "ozr_centrifuge"), ("m46_reagents", "ozr_reagents")]
# thick cable on the floor (to the generator) and the splices on it: the fan cord, the end outlet cable
MAIN = [(0.58, CY1 + 0.004, 0.20), (0.585, CY1 + 0.035, 0.19), (0.59, CY1 + 0.075, 0.12), (0.58, CY1 + 0.11, 0.035),
        (0.52, 0.50, 0.012), (0.40, 0.56, 0.012), (0.31, 0.61, 0.012), (0.22, 0.66, 0.012), (0.12, 0.76, 0.012),
        (0.05, 0.90, 0.016), (0.02, 1.02, 0.018)]
SPL = (5, 7)                                                 # splices - points of MAIN
# corrugated hose: filter nozzle -> right and down past the airlock lid -> under the airlock -> fan nozzle
HOSE = [(FX + 0.088, 0.0, FSZ), (0.72, 0.008, FSZ + 0.005), (0.805, 0.03, FSZ - 0.03), (0.845, 0.042, 1.26),
        (0.845, 0.03, 1.13), (0.82, -0.03, 0.998), (0.73, -0.072, 0.976), (FAN.x, -0.11, FAN.z),
        (FAN.x, FAN.y + 0.082, FAN.z)]
HOSE_R = 0.026

LOD_SPECS = [dict(lod=0), dict(lod=1), dict(lod=2)]

REGIONS = {
    "chest": ("enamel", 0.6), "chest_front": ("enamel_front", 0.9), "lid": ("enamel_lid", 0.6),
    "plinth": ("plinth", 0.3), "gasket": ("rubber", 0.5), "grille": ("grille", 1.0), "grille_frame": ("enamel", 1.0),
    "steel": ("steel", 1.0), "chrome": ("chrome", 1.6), "alu": ("alu", 0.9), "foil": ("foil", 0.7),
    "tape": ("tape", 1.2), "tape_y": ("tape_y", 1.6), "glove": ("glove", 0.8), "rubber": ("rubber", 0.6),
    "black": ("black", 1.0), "wood": ("wood", 1.0), "board": ("board", 0.8), "fan": ("fan_body", 1.2),
    "blade": ("blade", 1.4), "hose": ("hose", 0.9), "filter": ("filter", 1.0), "thermo": ("thermo", 2.0),
    "panel": ("panel", 2.0), "white": ("white", 2.0), "lamp_g": ("lamp_g_off", 2.0), "lamp_o": ("lamp_o_off", 2.0),
    "cable": ("cable", 0.5), "keyhole": ("keyhole", 2.0), "socket": ("socket", 1.6),
}

# =============================================================================
# Materials
# =============================================================================


def decal(name, center, size, y_face, eps=0.003):
    return (os.path.join(WORK, name), "y", -1, ("x", "z"), center, size, (y_face - eps, y_face + eps))


def rect(name, r, y_face, eps=0.003):
    x0, x1, z0, z1 = r
    return decal(name, ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0), y_face, eps)


def build_foil(mat, origin, seed=7.7, tone=0.36, floor_z=0.0, dust=0.25, grime=0.6, gloss=0.5, spec=0.6):
    """Foil-faced insulation (foil on a foam base): dull grey metal. The sheet is wrapped around the chest -
    folds along the wrapping (across the height - bands of tone and relief), small dents-facets (Voronoi
    cells, tone and relief only, no crease grid - it read as stone cracks), tone patches; dust and dirt
    come from the common weather."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    if kmats.LOOK["name"] == "dayz":
        tone *= kmats.LOOK["steel"]
    cell = t.node("ShaderNodeTexVoronoi")
    cell.feature = "F1"
    cell.inputs["Scale"].default_value = 48.0
    t.link(vec, cell.inputs["Vector"])
    dent = t.bw(cell.outputs["Color"])
    wrinkle = t.maprange(t.noise(t.stretch(vec, 1.0, 1.0, 6.0), 5.0, 5.0, 0.6), 0.3, 0.7, 0.0, 1.0)
    mottle = t.maprange(t.noise(vec, 3.0, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0)
    v = t.math("ADD", tone * 0.84, t.math("MULTIPLY", dent, tone * 0.14))
    v = t.math("ADD", v, t.math("MULTIPLY", wrinkle, tone * 0.12))
    v = t.math("ADD", v, t.math("MULTIPLY", mottle, tone * 0.10))
    comb = t.node("ShaderNodeCombineColor")
    for i in range(3):
        t.link(v, comb.inputs[i])
    col = t.mixc(0.10, comb.outputs[0], (0.26, 0.25, 0.22, 1))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.45)
    gl = t.math("SUBTRACT", gloss, t.math("MULTIPLY", dirt, gloss * 0.6))
    sp = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.6))
    h = t.math("ADD", t.math("MULTIPLY", dent, 0.35), t.math("MULTIPLY", wrinkle, 0.45))
    return kmats.out(t, col, gl, sp, h)


FRONT = [decal("decal_biohazard.png", (-0.06, 0.58), (0.15, 0.15), CY0),
         decal("decal_tag.png", (0.55, 0.30), (0.10, 0.04), CY0)]
PANEL = rect("decal_panel.png", (PNX[0], PNX[1], PNZ[0], PNZ[1]), CY0 - 0.006, eps=0.002)

KINDS = kmats.std_kinds(floor_z=0.0)
# light blue Clear Sky enamel over the white factory one: white and rust in the chips, dirt only at the bottom
BLUE = dict(color=kmats.lin((142, 184, 206)), under=kmats.lin((226, 226, 218)), seed=2.2, gloss=0.42, spec=0.30,
            chip=(0.59, 0.65), rust=(0.68, 0.76), rust_low=1.1, floor_z=0.0, dust=0.25, grime=0.9)
KINDS.update({
    "enamel": ("paint", BLUE),
    "enamel_front": ("paint", dict(BLUE, decal_items=FRONT)),
    "enamel_lid": ("paint", dict(BLUE, seed=3.4, rust_low=0.0, chip=(0.64, 0.70), dust=0.15, grime=0.2)),
    "plinth": ("plastic", dict(color=kmats.lin((34, 34, 34)), gloss=0.15, spec=0.08, dust=0.4, grime=0.8,
                               scuff=(0.70, 0.78))),
    "grille": ("paint", dict(color=kmats.lin((40, 42, 42)), under=kmats.lin((80, 50, 30)), seed=5.2, gloss=0.3,
                             spec=0.2, chip=(0.62, 0.68), rust=(0.60, 0.68), rust_low=0.8, dust=0.4, grime=0.6)),
    "chrome": ("steel", dict(seed=6.1, tone=0.42, along="z", gloss=0.75, spec=0.85, dust=0.1, grime=0.2)),
    "alu": ("steel", dict(seed=6.4, tone=0.50, along="x", gloss=0.5, spec=0.55, dust=0.05, grime=0.05)),
    "foil": (build_foil, dict(seed=7.7, floor_z=0.0)),
    "tape": ("plastic", dict(color=kmats.lin((128, 130, 128)), gloss=0.35, spec=0.25, mottle=0.10, dust=0.3,
                             grime=0.4, scuff=(0.66, 0.74))),
    "tape_y": ("plastic", dict(color=kmats.lin((222, 180, 34)), gloss=0.35, spec=0.25, mottle=0.08, dust=0.1,
                               grime=0.1)),
    "glove": ("plastic", dict(color=kmats.lin((30, 30, 30)), gloss=0.35, spec=0.25, dust=0.0, grime=0.0,
                              mottle=0.06, scuff=(0.9, 1.0))),
    "wood": (kwood.build_wood, dict(color=kmats.lin((160, 124, 82)), seed=4.6, along="y", floor_z=0.0, dust=0.3,
                                    grime=0.3, knots=0.4)),
    "board": (kwood.build_wood, dict(color=kmats.lin((176, 140, 94)), seed=5.3, along="x", floor_z=ZT, dust=0.05,
                                     grime=0.05, knots=0.3)),
    "fan_body": ("paint", dict(color=kmats.lin((78, 92, 84)), under=kmats.lin((150, 150, 146)), seed=4.4, gloss=0.4,
                               spec=0.3, chip=(0.64, 0.70), rust=(0.80, 0.88), rust_low=0.0, dust=0.3, grime=0.2)),
    "blade": ("plastic", dict(color=kmats.lin((52, 54, 56)), gloss=0.4, spec=0.3, dust=0.2)),
    "hose": ("plastic", dict(color=kmats.lin((112, 116, 116)), gloss=0.3, spec=0.2, dust=0.2, grime=0.2)),
    "filter": ("paint", dict(color=kmats.lin((206, 206, 198)), under=kmats.lin((90, 90, 92)), seed=8.3, gloss=0.4,
                             spec=0.3, chip=(0.70, 0.76), rust=(0.99, 1.0), rust_low=0.0, dust=0.15, grime=0.1)),
    "thermo": ("plastic", dict(color=kmats.lin((214, 210, 196)), gloss=0.4, spec=0.3, dust=0.1, grime=0.1)),
    "panel": ("paint", dict(color=kmats.lin((38, 40, 42)), under=kmats.lin((90, 90, 92)), seed=8.8, gloss=0.35,
                            spec=0.25, chip=(0.72, 0.78), rust=(0.99, 1.0), rust_low=0.0, dust=0.15, grime=0.2,
                            decal_items=[PANEL])),
    "white": ("plastic", dict(color=kmats.lin((220, 220, 212)), gloss=0.3, spec=0.2, dust=0.1)),
    "cable": ("plastic", dict(color=kmats.lin((26, 26, 26)), gloss=0.2, spec=0.1, dust=0.35, grime=0.4,
                              scuff=(0.8, 0.9))),
    "socket": ("plastic", dict(color=kmats.lin((200, 196, 182)), gloss=0.35, spec=0.25, dust=0.25, grime=0.35,
                               mottle=0.08)),
    "keyhole": ("flat", dict(color=kmats.lin((10, 10, 10)), gloss=0.1, spec=0.1)),
    "lamp_g_off": ("flat", dict(color=kmats.lin((34, 64, 40)), gloss=0.85, spec=0.8)),
    "lamp_g_on": ("flat", dict(color=kmats.lin((130, 255, 140)), gloss=0.85, spec=0.8)),
    "lamp_o_off": ("flat", dict(color=kmats.lin((96, 64, 20)), gloss=0.85, spec=0.8)),
    "lamp_o_on": ("flat", dict(color=kmats.lin((255, 190, 60)), gloss=0.85, spec=0.8)),
})

OBJ, NAME = "m07_sky_pack_bio", "ozr_sky_pack_bio"
# Work look: the thermometer display has its own texture with frames (section screen), the lamps use
# atlas _on (the green one lit, the yellow one blinks), the fan blades are a model.cfg loop.
SEL_SCREEN, SEL_LAMP_W, SEL_LAMP, SEL_FAN = "ozl_screen", "ozl_lamp_work", "ozl_lamp", "ozl_fan"
ON = dict(remap={"lamp_g_off": "lamp_g_on", "lamp_o_off": "lamp_o_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
FAN_ANIM = ("ozl_work_fan", dict(type="rotation", source="ozl_work", sourceAddress="loop", selection=SEL_FAN,
                                 axis="ozl_fan_axis", memory=1, minValue=0.0, maxValue=1.0 / FAN_TURNS, angle0=0.0,
                                 angle1=2 * math.pi))
SCREEN = dict(off="decal_lcd_off.png", frames=["decal_lcd_f%02d.png" % i for i in range(6)], size=128, gloss=0.6)
# proxies for the modules: the mod's CfgNonAIVehicles binds slots OZL_Tool1..3 to them (Proxyozl_tool1..3);
# slot N is module N of the Bio line (M44, M45, M46), no rotation: the modules face the person
PROXIES = [(r"\OpenZone_Research\models\proxies\ozl_tool%d" % (i + 1), m) for i, m in enumerate(MODS)]
# vanilla items: DayZ medicine in the isolator (the textures are in the p3d files themselves, there
# are no Proxy<name> classes), paper with a pen on the shelf, tape on the lid by the fan
SYRINGE, VIAL = r"dz\gear\medical\Syringe_Empty", r"dz\gear\medical\InjectionVial"
BLOODKIT, SPRAY = r"dz\gear\medical\BloodTest_Kit", r"dz\gear\medical\DisinfectantSpray"
DECOR = [
    kv.put(SYRINGE, (-0.06, -0.13, BDZ), up=(0, 0, 1), fwd=(0.25, -1, 0)),
    kv.put(VIAL, (0.035, 0.10, BDZ)),
    kv.put(BLOODKIT, (-0.15, 0.12, BDZ), **kv.flat(25)),
    kv.put(SPRAY, (-0.56, 0.17, ZT), up=(0, 0, 1), fwd=(0.3, -1, 0)),
    kv.put("paper", (MODS[1][0] - 0.004, 0.165, SZ - 0.003), **kv.flat(93)),
    kv.put("pen", (MODS[1][0] + 0.03, 0.19, SZ - 0.003), lift=0.0006, **kv.flat(68)),
    kv.put("ducttape", (0.635, 0.21, ZL), **kv.flat(0)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.82, 0.86, 0.88), clear=0.05, edge=0.10, smudge=0.08, streaks=0.03),
                 selections=(SEL_SCREEN, SEL_LAMP_W, SEL_LAMP, SEL_FAN), hidden=(SEL_SCREEN, SEL_LAMP_W, SEL_LAMP),
                 states={"on": ON}, bones=((SEL_FAN, ""),), animations=(FAN_ANIM,), proxies=PROXIES, decor=DECOR,
                 modules=[(o, n, m) for (o, n), m in zip(MOD_OBJ, MODS)], panels={"screen": SCREEN},
                 sources={"ozl_work": dict(animPeriod=2.0)})
P = M.part
BOUNDS = {}

# local face frames of the chest: a is along the face, b is up, c is outward
FRONT_F = g.Frame((0.0, CY0, 0.0), (1, 0, 0), (0, 0, 1), (0, -1, 0))
LID_F = g.Frame((0.0, CY0 - LIP, 0.0), (1, 0, 0), (0, 0, 1), (0, -1, 0))
LEFT_F = g.Frame((CX0, 0.0, 0.0), (0, -1, 0), (0, 0, 1), (-1, 0, 0))
BACK_F = g.Frame((0.0, CY1, 0.0), (-1, 0, 0), (0, 0, 1), (0, 1, 0))


# =============================================================================
# Primitives missing from kgeo
# =============================================================================
def face(part, verts, want):
    """Face from bmesh vertices, turned toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def rrect(x0, x1, y0, y1, r, n):
    """Rectangle with rounded corners (n segments per corner), counter-clockwise; n = 0 - sharp."""
    if n <= 0 or r <= 1e-6:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    out = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90.0), (x1 - r, y1 - r, 0.0), (x0 + r, y1 - r, 90.0), (x0 + r, y0 + r, 180.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def slab(part, x0, x1, y0, y1, z0, z1, rc=0.0, nc=0, re=0.0, ne=0, rb=0.0, nb=0, frame=None, caps=(True, True)):
    """Slab: in plan a rectangle with rounded corners rc (nc segments), the top edge rounded re (ne
    segments), the bottom rb (nb). frame is a local system: x -> u, y -> v, z -> n. caps are the bottom
    and top covers (they can be skipped on a side pressed against something)."""
    rows = []
    if rb > 0 and nb > 0:
        rows += [(rb * (1 - math.sin(math.pi / 2 * k / nb)), z0 + rb * (1 - math.cos(math.pi / 2 * k / nb)))
                 for k in range(nb + 1)]
    else:
        rows.append((0.0, z0))
    top = [(re * (1 - math.cos(math.pi / 2 * k / ne)), z1 - re + re * math.sin(math.pi / 2 * k / ne))
           for k in range(ne + 1)] if re > 0 and ne > 0 else [(0.0, z1)]
    for r in top:
        if abs(r[0] - rows[-1][0]) > 1e-7 or abs(r[1] - rows[-1][1]) > 1e-7:
            rows.append(r)
    bm = part.bm

    def p3(a, b, c):
        return frame.p(a, b, c) if frame else Vector((a, b, c))

    def d3(a, b, c):
        return (frame.u * a + frame.v * b + frame.n * c) if frame else Vector((a, b, c))
    ctr = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    rings = []
    for d, h in rows:
        pts = rrect(x0 + d, x1 - d, y0 + d, y1 - d, max(rc - d, 0.0005) if nc else 0.0, nc)
        rings.append([(bm.verts.new(p3(a, b, h)), Vector((a, b, h))) for a, b in pts])
    new = []
    n = len(rings[0])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(n):
            j = (k + 1) % n
            q = [r0[k], r0[j], r1[j], r1[k]]
            loc = sum((e[1] for e in q), Vector()) / 4 - ctr
            new.append(face(part, [e[0] for e in q], d3(*loc)))
    if caps[0]:
        new.append(face(part, [e[0] for e in rings[0]], d3(0, 0, -1)))
    if caps[1]:
        new.append(face(part, [e[0] for e in rings[-1]], d3(0, 0, 1)))
    part.tag(new)
    return new


def basis(axis):
    """Rotation axis: (a, b, w) - two transverse and a longitudinal unit vectors; axis is "x", "-y", ... or a
    vector."""
    if isinstance(axis, str):
        w = Vector([1.0 if c == axis[-1] else 0.0 for c in "xyz"]) * (-1.0 if axis.startswith("-") else 1.0)
    else:
        w = Vector(axis).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(w.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    a = ref.cross(w).normalized()
    return a, w.cross(a).normalized(), w


def lathe(part, prof, sides, center, axis="z", closed=False, caps=(False, False), phase=0.0):
    """Body of revolution: prof [(r, h)] - the section (r from the axis, h along axis from center),
    traversed along the outer surface in the direction of growing h (a closed one counter-clockwise in
    the r, h axes): then faces point outward. r = 0 is a point on the axis (a triangle fan). caps are
    the covers of the first and last ring."""
    a, b, w = basis(axis)
    c = Vector(center)
    bm = part.bm
    angs = [phase + 2 * math.pi * k / sides for k in range(sides)]
    rings = []
    for r, h in prof:
        if r < 1e-7:
            rings.append(bm.verts.new(c + w * h))
        else:
            rings.append([bm.verts.new(c + (a * math.cos(t) + b * math.sin(t)) * r + w * h) for t in angs])
    idx = list(range(len(prof))) + ([0] if closed else [])
    new = []
    for i0, i1 in zip(idx, idx[1:]):
        (r0, h0), (r1, h1) = prof[i0], prof[i1]
        nr, nh = h1 - h0, -(r1 - r0)
        R0, R1 = rings[i0], rings[i1]
        for k in range(sides):
            j = (k + 1) % sides
            tm = angs[k] + math.pi / sides
            want = (a * math.cos(tm) + b * math.sin(tm)) * nr + w * nh
            if isinstance(R0, list) and isinstance(R1, list):
                vs = [R0[k], R0[j], R1[j], R1[k]]
            elif isinstance(R0, list):
                vs = [R0[k], R0[j], R1]
            elif isinstance(R1, list):
                vs = [R0, R1[j], R1[k]]
            else:
                continue
            new.append(face(part, vs, want))
    for cap, i, o in ((caps[0], 0, 1), (caps[1], len(prof) - 1, len(prof) - 2)):
        if cap and isinstance(rings[i], list):
            new.append(face(part, rings[i], w * (1.0 if prof[i][1] > prof[o][1] else -1.0)))
    part.tag(new)
    return new


def fquad(part, frame, a0, a1, b0, b1, c):
    """Rectangle in the local system frame at offset c, facing outward (frame.n)."""
    vs = [part.bm.verts.new(frame.p(a, b, c)) for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
    return part.tag([face(part, vs, frame.n)])


def bolt(name, center, axis, r=0.0045, h=0.003, region="steel", sides=6):
    """Bolt or screw head - its own part with a shared unwrap (uv_name): many small heads take one
    rectangle in the atlas."""
    b = P(name, region, uv_name="bolt_%s_%s" % (region, axis), uv_origin=center)
    g.cyl(b, center, axis, r, h, sides)
    return b


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom)."""
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


def resample(pts, step):
    """Polyline -> points at an equal step along the length."""
    v = [Vector(p) for p in pts]
    seg = [(v[i + 1] - v[i]).length for i in range(len(v) - 1)]
    total = sum(seg)
    n = max(2, int(round(total / step)))
    out, i, acc = [], 0, 0.0
    for k in range(n + 1):
        d = total * k / n
        while i < len(seg) - 1 and acc + seg[i] < d:
            acc += seg[i]
            i += 1
        t = (d - acc) / max(seg[i], 1e-9)
        out.append(tuple(v[i].lerp(v[i + 1], min(max(t, 0.0), 1.0))))
    return out


def cable(part, pts, r, sides, k=2):
    """Cable, cord: a smooth curve through points (no kinks), round."""
    g.pipe(part, spline(pts, k) if k > 1 else pts, r, sides)


def crumple(x, s, amp, seed=0.0):
    """Crumpled film: normal displacement, smooth folds of different scales."""
    return amp * (0.55 * math.sin(23.0 * x + 7.0 * s + seed) * math.sin(17.0 * s + 3.1 * x + seed * 0.7) +
                  0.30 * math.sin(51.0 * x - 29.0 * s + seed * 1.3) + 0.15 * math.sin(83.0 * s + 61.0 * x))


def film_sheet(part, verts, quads, normals, thick=0.0015):
    """Film with two sides: verts - {key: point}, normals - {key: outward}, quads - [keys around]. The
    outer sheet faces outward, the inner one (thick inward) faces inward: a transparent material is
    drawn from one side only, and without the second sheet the far wall of the hood disappears."""
    bm = part.bm
    used = sorted({k for q in quads for k in q}, key=str)
    new = []
    for side in (1, -1):
        vs = {k: bm.verts.new(Vector(verts[k]) - Vector(normals[k]) * (thick if side < 0 else 0.0)) for k in used}
        for q in quads:
            n = sum((Vector(normals[k]) for k in q), Vector()) * side
            new.append(face(part, [vs[k] for k in q], n))
    bm.normal_update()
    return part.tag(new)


# =============================================================================
# Chest (B2 base)
# =============================================================================
def build_chest(spec):
    lod = spec["lod"]
    nc = (4, 2, 1)[lod]
    parts = []
    body = P("chest_body", "chest")
    slab(body, CX0, CX1, CY0, CY1, ZB, ZG, rc=RCH, nc=nc, rb=0.008 if lod == 0 else 0.0, nb=2 if lod == 0 else 0,
         caps=(True, False))
    # the flat part of the face is its own region (decals)
    fi = body.region_index("chest_front", *REGIONS["chest_front"])
    for f in body.bm.faces:
        if f.normal.y < -0.999:
            f[body.reg] = fi
    parts.append(body)
    # the plinth is recessed and dark; feet under it
    pl = P("chest_plinth", "plinth")
    slab(pl, CX0 + 0.012, CX1 - 0.012, CY0 + 0.012, CY1 - 0.012, ZFOOT, ZB + 0.004, rc=RCH - 0.012, nc=nc,
         caps=(True, False))
    parts.append(pl)
    if lod == 0:
        ft = P("chest_feet", "plinth")
        for x in (CX0 + 0.07, CX1 - 0.07):
            for y in (CY0 + 0.07, CY1 - 0.07):
                g.cyl(ft, (x, y, ZFOOT / 2), "z", 0.02, ZFOOT, 6)
        parts.append(ft)
    # lid with an overhang and a rounded edge, a gasket in the seam
    ld = P("chest_lid", "lid")
    slab(ld, CX0 - LIP, CX1 + LIP, CY0 - LIP, CY1 + LIP, ZG + 0.006, ZL, rc=RCH + LIP, nc=nc,
         re=(0.014, 0.012, 0.0)[lod], ne=(3, 1, 0)[lod], rb=0.003 if lod == 0 else 0.0, nb=1 if lod == 0 else 0)
    parts.append(ld)
    gs = P("chest_gasket", "gasket")
    slab(gs, CX0 + 0.003, CX1 - 0.003, CY0 + 0.003, CY1 - 0.003, ZG - 0.002, ZG + 0.008, rc=RCH - 0.003, nc=nc,
         caps=(False, False))
    parts.append(gs)
    # compressor grille on the right end: a dark opening, a frame, slanted louvres, screws
    gy0, gy1, gz0, gz1 = -0.235, 0.235, 0.085, 0.335
    gr = P("chest_grille", "grille")
    g.box(gr, CX1 - 0.002, CX1 + 0.002, gy0, gy1, gz0, gz1)
    parts.append(gr)
    fr = P("chest_grille_frame", "grille_frame")
    w, t = 0.014, 0.010
    g.box(fr, CX1, CX1 + t, gy0 - w, gy1 + w, gz1, gz1 + w)
    g.box(fr, CX1, CX1 + t, gy0 - w, gy1 + w, gz0 - w, gz0)
    g.box(fr, CX1, CX1 + t, gy0 - w, gy0, gz0, gz1)
    g.box(fr, CX1, CX1 + t, gy1, gy1 + w, gz0, gz1)
    if lod < 2:
        n = 9 if lod == 0 else 5
        for k in range(n):
            z = gz0 + 0.016 + (gz1 - gz0 - 0.032) * k / (n - 1)
            g.prism(fr, [(CX1 + 0.001, z + 0.011), (CX1 + 0.009, z + 0.004), (CX1 + 0.009, z - 0.001),
                         (CX1 + 0.001, z + 0.006)], (0, 2), gy0, gy1)
    parts.append(fr)
    if lod == 0:
        for y in (gy0 - w / 2, gy1 + w / 2):
            for z in (gz0 - w / 2, gz1 + w / 2):
                parts.append(bolt("grille_screw", (CX1 + t + 0.0012, y, z), "x", 0.0035, 0.0024))
    if lod < 2:
        # bracket handle on pads along the front edge of the lid
        hd = P("lid_handle", "black")
        yf = CY0 - LIP
        pts = [(-0.235, yf + 0.004, 0.823), (-0.235, yf - 0.014, 0.822), (-0.222, yf - 0.025, 0.821),
               (-0.12, yf - 0.027, 0.820), (0.12, yf - 0.027, 0.820), (0.222, yf - 0.025, 0.821),
               (0.235, yf - 0.014, 0.822), (0.235, yf + 0.004, 0.823)]
        path = spline(pts, 2) if lod == 0 else pts
        g.tube_var(hd, path, [(0.0075, 0.011)] * len(path), 8 if lod == 0 else 4)
        for s in (-1, 1):
            slab(hd, s * 0.235 - 0.02, s * 0.235 + 0.02, 0.808, 0.852, 0.0, 0.010, rc=0.006, nc=1 if lod == 0 else 0,
                 re=0.003 if lod == 0 else 0.0, ne=1 if lod == 0 else 0, frame=LID_F, caps=(False, True))
        parts.append(hd)
        # hinges at the back: leaves on the body and lid, an axle
        hg = P("lid_hinges", "steel")
        for x in (-0.50, 0.50):
            g.box(hg, x - 0.034, x + 0.034, CY1, CY1 + 0.003, ZG - 0.046, ZG - 0.004)
            g.box(hg, x - 0.034, x + 0.034, CY1 + LIP, CY1 + LIP + 0.003, ZG + 0.012, ZL - 0.016)
            g.cyl(hg, (x, CY1 + 0.011, ZG + 0.004), "x", 0.0075, 0.072, 10 if lod == 0 else 6)
        parts.append(hg)
    if lod == 0:
        for x in (-0.50, 0.50):
            parts.append(bolt("hinge_screw", (x, CY1 + 0.0042, ZG - 0.025), "y", 0.004, 0.0024))
            parts.append(bolt("hinge_screw", (x, CY1 + LIP + 0.0042, ZG + 0.032), "y", 0.004, 0.0024))
        # lock cylinder, drain plug
        lk = P("lid_lock", "chrome")
        lathe(lk, [(0.0125, 0.0), (0.0125, 0.004), (0.010, 0.0065), (0.0, 0.007)], 12, (0.30, CY0, ZG - 0.028), "-y")
        parts.append(lk)
        kh = P("lid_keyhole", "keyhole")
        g.box(kh, 0.30 - 0.0012, 0.30 + 0.0012, CY0 - 0.0074, CY0 - 0.0066, ZG - 0.034, ZG - 0.022)
        parts.append(kh)
        dp = P("drain_plug", "black")
        lathe(dp, [(0.012, 0.0), (0.012, 0.006), (0.0085, 0.009), (0.0, 0.0095)], 10, (0.62, CY0, 0.11), "-y")
        parts.append(dp)
    return parts


def build_panel(spec):
    """Control panel on the face: the face with the thermostat scale (a decal), a knurled knob, lamps
    "power" (ozl_lamp_work) and compressor (ozl_lamp) in chrome bezels, two screws."""
    lod = spec["lod"]
    parts = []
    pn = P("panel", "panel")
    slab(pn, PNX[0], PNX[1], PNZ[0], PNZ[1], 0.0, 0.006, rc=0.010, nc=2 if lod == 0 else 0,
         re=0.002 if lod == 0 else 0.0, ne=1 if lod == 0 else 0, frame=FRONT_F, caps=(False, True))
    parts.append(pn)
    kx_, kz = KNOB
    if lod < 2:
        kb = P("thermostat_knob", "black")
        if lod == 0:
            lathe(kb, [(0.0235, 0.006), (0.0235, 0.009), (0.0195, 0.0105)], 16, (kx_, CY0, kz), "-y")
            poly = [(kx_ + (0.0185 - 0.0016 * (k % 2)) * math.cos(math.pi * k / 12),
                     kz + (0.0185 - 0.0016 * (k % 2)) * math.sin(math.pi * k / 12)) for k in range(24)]
            g.prism(kb, poly, (0, 1), 0.0105, 0.026, frame=FRONT_F)
            # knob mark: at "5"
            mk = P("knob_mark", "white")
            a = math.radians(45.0)
            u, v = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
            g.prism(mk, [(kx_ + u[0] * r + v[0] * s, kz + u[1] * r + v[1] * s)
                         for r, s in ((0.005, -0.0013), (0.0165, -0.0013), (0.0165, 0.0013), (0.005, 0.0013))],
                    (0, 1), 0.026, 0.0264, frame=FRONT_F)
            parts.append(mk)
        else:
            g.cyl(kb, (kx_, CY0 - 0.016, kz), "y", 0.02, 0.02, 8)
        parts.append(kb)
    for lx, reg in LAMPS:
        ln = P("lamp_" + reg, reg, group=SEL_LAMP_W if reg == "lamp_g" else SEL_LAMP)
        if lod == 0:
            lathe(ln, [(0.0078, 0.0095), (0.0074, 0.013), (0.0045, 0.0158), (0.0, 0.0165)], 10, (lx, CY0, kz), "-y")
        else:
            g.cyl(ln, (lx, CY0 - 0.010, kz), "y", 0.008, 0.008, (6, 4)[lod - 1])
        parts.append(ln)
        if lod == 0:
            rm = P("lamp_rim_" + reg, "chrome", uv_name="lamp_rim", uv_origin=(lx, 0.0, kz))
            lathe(rm, [(0.0076, 0.006), (0.0125, 0.006), (0.0125, 0.0085), (0.0098, 0.0115), (0.0076, 0.011)], 10,
                  (lx, CY0, kz), "-y", closed=True)
            parts.append(rm)
    if lod == 0:
        for x in (PNX[0] + 0.011, PNX[1] - 0.011):
            parts.append(bolt("panel_screw", (x, CY0 - 0.0072, kz), "y", 0.0035, 0.0024))
    return parts


# =============================================================================
# Wrap: foil and tape
# =============================================================================
FOIL_XA, FOIL_YB = -0.36, 0.29                               # foil: face x, corner, end y
FOIL_Z = (0.105, 0.735)
TAPE_Z = (0.70, 0.26)                                        # tape around the corner


def wrap_path(off, xa, yb, n_arc=4, n_front=1, n_side=1):
    """Path around the front left corner of the chest at offset off (top view): along the face from x = xa,
    along the corner arc, along the left end to y = yb. [(x, y, nx, ny)]; straight sections are split
    into n_front and n_side parts."""
    r = RCH + off
    cx, cy = CX0 + RCH, CY0 + RCH
    out = [(xa + (cx - xa) * k / n_front, CY0 - off, 0.0, -1.0) for k in range(n_front)]
    for k in range(n_arc + 1):
        a = math.radians(-90.0 - 90.0 * k / n_arc)
        out.append((cx + r * math.cos(a), cy + r * math.sin(a), math.cos(a), math.sin(a)))
    out += [(CX0 - off, cy + (yb - cy) * k / n_side, -1.0, 0.0) for k in range(1, n_side + 1)]
    return out


def foil_wrap(lod):
    """Foil sheet wrapped around the front left corner: an uneven edge (torn by hand), the folds are normal
    displacement; pressed down at the edges and under the tape."""
    cols = wrap_path(0.003, FOIL_XA, FOIL_YB, n_arc=(4, 2)[lod], n_front=(6, 2)[lod], n_side=(10, 3)[lod])
    nv = (9, 3)[lod]
    amp = (0.0065, 0.002)[lod]
    p = P("foil_wrap", "foil")
    bm = p.bm
    L = [0.0]
    for i in range(1, len(cols)):
        L.append(L[-1] + math.hypot(cols[i][0] - cols[i - 1][0], cols[i][1] - cols[i - 1][1]))
    vs = []
    for (x, y, nx, ny), d_ in zip(cols, L):
        u = d_ / L[-1]
        zb = FOIL_Z[0] + 0.012 * math.sin(9.0 * u + 1.0) + 0.006 * math.sin(23.0 * u)
        zt = FOIL_Z[1] + 0.010 * math.sin(7.0 * u + 2.0) + 0.005 * math.sin(19.0 * u + 1.0)
        col = []
        for j in range(nv + 1):
            v = j / nv
            z = zb + (zt - zb) * v
            edge = min(d_, L[-1] - d_, z - zb, zt - z)               # to the sheet edge, m
            press = min([1.0] + [abs(z - tz) / 0.035 for tz in TAPE_Z])
            d = amp * (0.5 + 0.5 * math.sin(31 * u + 17 * v + 1.0) * math.sin(13 * v - 7 * u + 1.0))
            d *= min(1.0, edge / 0.04) * press
            col.append(bm.verts.new((x + nx * d, y + ny * d, z)))
        vs.append((col, (nx, ny)))
    new = []
    for i in range(len(vs) - 1):
        (c0, n0), (c1, n1) = vs[i], vs[i + 1]
        for j in range(nv):
            new.append(face(p, [c0[j], c1[j], c1[j + 1], c0[j + 1]], ((n0[0] + n1[0]) / 2, (n0[1] + n1[1]) / 2, 0.0)))
    p.tag(new)
    return p


def foil_back(lod):
    """Foil sheet on the back (the left part: the right one was not covered - there are the cable and the
    compressor)."""
    a0, a1, b0, b1 = -0.32, 0.70, 0.125, 0.725
    nu, nv = (12, 7) if lod == 0 else (3, 2)
    amp = (0.0065, 0.002)[lod]
    p = P("foil_back", "foil")
    bm = p.bm
    vs = []
    for i in range(nu + 1):
        u = i / nu
        col = []
        for j in range(nv + 1):
            v = j / nv
            a = a0 + (a1 - a0) * u
            b = b0 + (b1 - b0) * v + (0.010 * math.sin(8.0 * u + 0.5) if j in (0, nv) else 0.0)
            edge = min((a - a0), (a1 - a), (b1 - b0) * min(v, 1 - v))   # to the sheet edge, m
            press = min(1.0, abs(b - 0.715) / 0.035)
            d = 0.003 + amp * (0.5 + 0.5 * math.sin(29 * u + 13 * v + 2.0) * math.sin(11 * v - 5 * u + 2.0)) * \
                min(1.0, edge / 0.04) * press
            col.append(bm.verts.new(BACK_F.p(a, b, d)))
        vs.append(col)
    new = []
    for i in range(nu):
        for j in range(nv):
            new.append(face(p, [vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]], BACK_F.n))
    p.tag(new)
    return p


def build_wrap(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = [foil_wrap(lod), foil_back(lod)]
    tp = P("tape", "tape")
    w, t = 0.048, 0.0006
    lo, hi = 0.0072, 0.0086                                   # vertical tapes are lower, ring tapes on top
    # along the sheet edge on the face, on the end; tapes around the corner
    g.sweep(tp, [(FOIL_XA + 0.012, CY0 - lo, 0.09), (FOIL_XA + 0.012, CY0 - lo, 0.75)], (1, 0, 0), t, w / 2)
    g.sweep(tp, [(CX0 - lo, FOIL_YB - 0.012, 0.09), (CX0 - lo, FOIL_YB - 0.012, 0.75)], (0, 1, 0), t, w / 2)
    for z, xa, yb in ((TAPE_Z[0], FOIL_XA + 0.03, 0.10), (TAPE_Z[1], FOIL_XA - 0.08, -0.06))[:(2, 1)[lod]]:
        pts = [(x, y, z) for x, y, _, _ in wrap_path(hi, xa, yb, n_arc=(4, 2)[lod])]
        g.sweep(tp, pts, (0, 0, 1), t, w / 2)
    # at the back: across the top of the sheet and along its right edge
    g.sweep(tp, [BACK_F.p(-0.335, 0.715, hi), BACK_F.p(0.715, 0.715, hi)], (0, 0, 1), t, w / 2)
    if lod == 0:
        g.sweep(tp, [BACK_F.p(-0.31, 0.11, lo), BACK_F.p(-0.31, 0.74, lo)], (1, 0, 0), t, w / 2)
    parts.append(tp)
    return parts


def build_thermometer(spec):
    """Digital thermometer on tape: a body, the display (ozl_screen, own texture), buttons, the probe wire
    under the lid."""
    lod = spec["lod"]
    x0, x1, z0, z1 = TH
    cs = P("thermo_case", "thermo")
    slab(cs, x0, x1, z0, z1, 0.0015, 0.021, rc=0.008, nc=2 if lod == 0 else 0, re=0.004 if lod == 0 else 0.0,
         ne=1 if lod == 0 else 0, frame=FRONT_F, caps=(False, True))
    parts = [cs]
    if lod < 2:
        bz = P("thermo_bezel", "black")
        fquad(bz, FRONT_F, LCD[0] - 0.003, LCD[1] + 0.003, LCD[2] - 0.003, LCD[3] + 0.003, 0.0212)
        parts.append(bz)
    lcd = P("thermo_lcd", "black", group=SEL_SCREEN, section="screen")
    fquad(lcd, FRONT_F, LCD[0], LCD[1], LCD[2], LCD[3], 0.0222 if lod < 2 else 0.0215)
    parts.append(lcd)
    if lod == 2:
        return parts
    if lod == 0:
        bt = P("thermo_buttons", "white")
        for x in (x0 + 0.035, x0 + 0.055):
            lathe(bt, [(0.0035, 0.021), (0.0035, 0.0228), (0.0, 0.0232)], 8, (x, CY0, z0 + 0.0095), "-y")
        parts.append(bt)
    if lod == 1:
        return parts
    # tape on top and bottom, over the body edges onto the chest
    tp = P("thermo_tape", "tape")
    xm = (x0 + x1) / 2
    for zs, sg in ((z1, 1), (z0, -1)):
        pts = [(xm, CY0 - 0.0008, zs + sg * 0.032), (xm, CY0 - 0.0008, zs + sg * 0.003),
               (xm, CY0 - 0.0218, zs + sg * 0.0006), (xm, CY0 - 0.0218, zs - sg * (0.007 if sg > 0 else 0.005))]
        g.sweep(tp, pts, (1, 0, 0), 0.0004, 0.045)
    parts.append(tp)
    cb = P("thermo_wire", "cable")
    pts = [(x1 - 0.012, CY0 - 0.012, z1 + 0.001), (x1 - 0.004, CY0 - 0.014, z1 + 0.05), (x1 + 0.012, CY0 - 0.010, z1 + 0.12),
           (x1 + 0.020, CY0 - 0.004, ZG - 0.004), (x1 + 0.022, CY0 + 0.01, ZG + 0.003)]
    cable(cb, pts, 0.0022, 5 if lod == 0 else 4, k=3 if lod == 0 else 1)
    parts.append(cb)
    return parts


# =============================================================================
# Cables: thick one to the generator, splices, plug
# =============================================================================
def build_cables(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    mc = P("main_cable", "cable")
    cable(mc, MAIN, 0.011, 6 if lod == 0 else 4, k=2 if lod == 0 else 1)
    parts.append(mc)
    if lod == 1:
        return parts
    # rubber grommet in the chest back
    gm = P("cable_grommet", "black")
    lathe(gm, [(0.017, 0.0), (0.017, 0.006), (0.013, 0.012), (0.0118, 0.022)], 10, (MAIN[0][0], CY1, MAIN[0][2]), "y")
    parts.append(gm)
    # splices under tape: a swelling on the cable
    sp = P("cable_splices", "tape")
    for i in SPL:
        c, a, b = Vector(MAIN[i]), Vector(MAIN[i - 1]), Vector(MAIN[i + 1])
        d = (b - a).normalized()
        pts = [tuple(c + d * s) for s in (-0.05, -0.032, -0.012, 0.012, 0.032, 0.05)]
        g.tube_var(sp, pts, [(0.0112, 0.0112), (0.0155, 0.0150), (0.0175, 0.0168), (0.0172, 0.0165),
                             (0.0150, 0.0146), (0.0112, 0.0112)], 6)
    parts.append(sp)
    # plug at the end (lies on the floor, toward the generator)
    pg = P("main_plug", "black")
    end, prev = Vector(MAIN[-1]), Vector(MAIN[-2])
    d = (end - prev).normalized()
    lathe(pg, [(0.0112, 0.0), (0.0135, 0.010), (0.0175, 0.018), (0.0175, 0.050), (0.0158, 0.054), (0.0, 0.0555)], 10,
          tuple(end), tuple(d))
    a_, b_, _ = basis(tuple(d))
    for s in (-1, 1):
        g.pipe(pg, [tuple(end + d * 0.054 + a_ * (0.0095 * s)), tuple(end + d * 0.073 + a_ * (0.0095 * s))], 0.002, 5)
    parts.append(pg)
    return parts


# =============================================================================
# Module shelf on the left end (slot 2), the outlet above it
# =============================================================================
def build_shelf(spec):
    lod = spec["lod"]
    parts = []
    bd = P("shelf_board", "wood")
    slab(bd, SX0, SX1, CY0 + 0.01, CY1 - 0.01, SZ - 0.022, SZ - 0.003, rc=0.012, nc=(2, 1, 0)[lod],
         re=0.003 if lod == 0 else 0.0, ne=1 if lod == 0 else 0, rb=0.003 if lod == 0 else 0.0, nb=1 if lod == 0 else 0)
    parts.append(bd)
    mx, my, _ = MODS[1]
    mt = P("shelf_mat", "rubber")
    g.box(mt, mx - 0.115, mx + 0.115, my - 0.125, my + 0.125, SZ - 0.003, SZ + 0.001,
          **(dict(r=0.0015, seg=1) if lod == 0 else {}))
    parts.append(mt)
    br = P("shelf_brackets", "steel")
    for y in (CY0 + 0.07, CY1 - 0.07):
        g.box(br, CX0 - 0.014, CX0 - 0.010, y - 0.014, y + 0.014, SZ - 0.25, SZ - 0.022)
        g.box(br, SX0 + 0.02, CX0 - 0.010, y - 0.014, y + 0.014, SZ - 0.026, SZ - 0.022)
        if lod < 2:
            g.sweep(br, [(CX0 - 0.012, y, SZ - 0.235), (SX0 + 0.05, y, SZ - 0.028)], (0, 1, 0), 0.002, 0.011)
    parts.append(br)
    if lod == 0:
        for y in (CY0 + 0.07, CY1 - 0.07):
            for z in (SZ - 0.07, SZ - 0.20):
                parts.append(bolt("shelf_screw", (CX0 - 0.0152, y, z), "x", 0.005, 0.0024))
    if lod == 2:
        return parts
    # surface outlet on the end: the M45 centrifuge cord goes into it; the outlet cable goes behind the chest to the
    # splice
    sy, sz = SOCK
    sk = P("socket", "socket")
    slab(sk, -sy - 0.032, -sy + 0.032, sz - 0.032, sz + 0.032, 0.010, 0.030, rc=0.008, nc=2 if lod == 0 else 0,
         re=0.004 if lod == 0 else 0.0, ne=1 if lod == 0 else 0, frame=LEFT_F, caps=(False, True))
    if lod == 0:
        lathe(sk, [(0.0255, 0.030), (0.0255, 0.033), (0.022, 0.0348), (0.0, 0.035)], 14, (CX0, sy, sz), "-x")
    parts.append(sk)
    if lod == 0:
        hl = P("socket_holes", "keyhole")
        for s in (-1, 1):
            g.cyl(hl, (CX0 - 0.0352, sy + s * 0.0095, sz), "x", 0.0032, 0.0008, 8)
        parts.append(hl)
    if lod == 1:
        return parts
    cb = P("socket_cable", "cable")
    pts = [(CX0 - 0.02, sy + 0.03, sz), (CX0 - 0.018, sy + 0.07, sz - 0.006), (CX0 - 0.0175, 0.30, sz - 0.014),
           (CX0 - 0.02, CY1 + 0.025, sz - 0.04), (CX0 - 0.02, CY1 + 0.026, 0.40), (CX0 - 0.016, CY1 + 0.03, 0.06),
           (CX0 + 0.03, CY1 + 0.075, 0.0045), (-0.40, CY1 + 0.14, 0.0045), (0.0, CY1 + 0.22, 0.0045),
           tuple(Vector(MAIN[SPL[1]]) + Vector((-0.03, -0.004, -0.004)))]
    cable(cb, pts, 0.0035, 5 if lod == 0 else 4, k=2 if lod == 0 else 1)
    parts.append(cb)
    return parts


# =============================================================================
# Film isolator
# =============================================================================
def profile(nwf, nwb, n_arc, n_roof):
    """Hood section (y, z, ny, nz, s) from the bottom of the face over the roof to the bottom of the back;
    s is the arc length; nwf / nwb - parts of the face / back wall."""
    pts = []
    for k in range(nwf + 1):
        pts.append((YF, ZT + (ZW - ZT) * k / nwf, -1.0, 0.0))
    for k in range(1, n_arc + 1):
        a = math.pi - (math.pi / 2) * k / n_arc
        pts.append((YF + RC + RC * math.cos(a), ZW + RC * math.sin(a), math.cos(a), math.sin(a)))
    for k in range(1, n_roof + 1):
        pts.append((YF + RC + (YB - YF - 2 * RC) * k / n_roof, ZR, 0.0, 1.0))
    for k in range(1, n_arc + 1):
        a = math.pi / 2 - (math.pi / 2) * k / n_arc
        pts.append((YB - RC + RC * math.cos(a), ZW + RC * math.sin(a), math.cos(a), math.sin(a)))
    for k in range(1, nwb + 1):
        pts.append((YB, ZW - (ZW - ZT) * k / nwb, 1.0, 0.0))
    s, out = 0.0, []
    for i, (y, z, ny, nz) in enumerate(pts):
        if i:
            s += math.hypot(y - pts[i - 1][0], z - pts[i - 1][1])
        out.append((y, z, ny, nz, s))
    return out


FILM = {0: dict(prof=(6, 2, 4, 3), amp=0.010, wr=0.0022, rings=2),
        1: dict(prof=(2, 1, 3, 2), amp=0.006, wr=0.0, rings=1)}


def film_xs(lod):
    """Columns of the film grid along x (on the near LOD - squares around the rings for the holes) and columns of
    squares."""
    if lod > 0:
        return [XI0, (XI0 + XIC) / 2, XIC, (XIC + XI1) / 2, XI1], ()
    a = (ZW - ZT) / 2

    def lin(p, q, n):
        return [p + (q - p) * k / n for k in range(n + 1)]
    xs = [XI0] + lin(PX[0] - a, PX[0] + a, 4) + [XIC] + lin(PX[1] - a, PX[1] + a, 4) + [XI1]
    return xs, ((1, 5), (7, 11))


def bump(v, marks):
    """0 at the marks marks, 1 midway between them (a half sine wave)."""
    for m0, m1 in zip(marks, marks[1:]):
        if m0 - 1e-9 <= v <= m1 + 1e-9:
            return math.sin(math.pi * min(max((v - m0) / (m1 - m0), 0.0), 1.0))
    return 0.0


def port_fade(x, z):
    """0 at the edge of a ring hole, 1 farther than 9 cm from it: there the flange holds the film."""
    f = 1.0
    for px in PX:
        f = min(f, max(0.0, min(1.0, (math.hypot(x - px, z - PZ) - RH) / 0.09)))
    return f


def film_disp(x, z, s, marks, fl, front):
    """Outward film displacement: inflated into pillows between the arcs and between the clamps (bottom,
    roof ribs), small folds; pressed down at the rings."""
    hx = bump(x, sorted(HOOPS))
    d = fl["amp"] * hx * bump(s, marks)
    w = fl["wr"] * crumple(x, s, 1.0, 0.3) * min(1.0, hx * 3.0) * min(1.0, max(0.0, z - ZT) / 0.03)
    if front:
        f = port_fade(x, z)
        d, w = d * f, w * f
    return d + w


def build_film(spec):
    """Hood film: face, roof, back - a grid (on the near LOD with holes under the rings: around each one -
    rings from a grid square to the hole circle), the ends - rings toward the middle (the right one -
    toward the airlock hole)."""
    lod = spec["lod"]
    if lod not in FILM:
        return []                                              # far LOD - no film
    fl = FILM[lod]
    nwf, nwb, na, nr = fl["prof"]
    prof = profile(nwf, nwb, na, nr)
    marks = [0.0, prof[nwf + na][4], prof[nwf + na + nr][4], prof[-1][4]]
    xs, holes = film_xs(lod)
    verts, nrm, quads = {}, {}, []
    for i, x in enumerate(xs):
        for k, (y, z, ny, nz, s) in enumerate(prof):
            d = film_disp(x, z, s, marks, fl, k <= nwf)
            verts[(i, k)] = (x, y + ny * d, z + nz * d)
            nrm[(i, k)] = (0.0, ny, nz)
    for i in range(len(xs) - 1):
        for k in range(len(prof) - 1):
            if k < nwf and any(i0 <= i < i1 for i0, i1 in holes):
                continue
            quads.append([(i, k), (i + 1, k), (i + 1, k + 1), (i, k + 1)])
    for pi, (i0, i1) in enumerate(holes):
        px = PX[pi]
        loop = [(i, 0) for i in range(i0, i1 + 1)] + [(i1, k) for k in range(1, nwf + 1)] + \
               [(i, nwf) for i in range(i1 - 1, i0 - 1, -1)] + [(i0, k) for k in range(nwf - 1, 0, -1)]
        rings = [loop]
        for t in (0.5, 0.0):
            ring = []
            for j, (i, k) in enumerate(loop):
                bx, bz = xs[i], prof[k][1]
                ang = math.atan2(bz - PZ, bx - px)
                hx_, hz_ = px + RH * math.cos(ang), PZ + RH * math.sin(ang)
                x, z = hx_ + (bx - hx_) * t, hz_ + (bz - hz_) * t
                key = ("port", pi, t, j)
                d = film_disp(x, z, z - ZT, marks, fl, True)
                verts[key] = (x, YF - d, z)
                nrm[key] = (0.0, -1.0, 0.0)
                ring.append(key)
            rings.append(ring)
        for r0, r1 in zip(rings, rings[1:]):
            n = len(r0)
            quads += [[r0[j], r0[(j + 1) % n], r1[(j + 1) % n], r1[j]] for j in range(n)]
    fm = P("iso_film", "steel", section="glass")
    film_sheet(fm, verts, quads, nrm)
    parts = [fm]
    # ends: the contour is the section and the bottom back to the face
    loop = [(y, z) for y, z, _, _, _ in prof]
    nb = 3 if lod == 0 else 1
    loop += [(YB + (YF - YB) * k / (nb + 1), ZT) for k in range(1, nb + 1)]
    amp = fl["amp"] * 0.8
    for name, x, sgn, hole in (("iso_film_l", XI0, -1, False), ("iso_film_r", XI1, 1, lod == 0)):
        ev, en, eq = {}, {}, []
        n = len(loop)
        R = fl["rings"]
        cy, cz = (0.0, LZ) if hole else ((YF + YB) / 2, (ZT + ZR) / 2)
        for j, (y, z) in enumerate(loop):
            if hole:
                ang = math.atan2(z - cz, y - cy)
                ty, tz = cy + RHL * math.cos(ang), cz + RHL * math.sin(ang)
            else:
                ty, tz = cy, cz
            for r in range(R + (1 if hole else 0)):
                t = r / R
                yy, zz = y + (ty - y) * t, z + (tz - z) * t
                d = amp * (math.sin(math.pi * t) if hole else math.sin(math.pi / 2 * t))
                d += crumple(yy * 1.7, zz * 1.3, fl["wr"], 1.1 + x) * min(1.0, t * 4) * (1 - t if hole else 1.0)
                ev[(j, r)] = (x + sgn * d, yy, zz)
                en[(j, r)] = (sgn, 0.0, 0.0)
        if not hole:
            ev["c"] = (x + sgn * amp, cy, cz)
            en["c"] = (sgn, 0.0, 0.0)
        for j in range(n):
            jj = (j + 1) % n
            for r in range(R if hole else R - 1):
                eq.append([(j, r), (jj, r), (jj, r + 1), (j, r + 1)])
            if not hole:
                eq.append([(j, R - 1), (jj, R - 1), "c"])
        ep = P(name, "steel", section="glass")
        film_sheet(ep, ev, eq, en)
        parts.append(ep)
    return parts


def build_tray(spec):
    """Stainless tray, the clamp strip of the film bottom on bolts, arc feet."""
    lod = spec["lod"]
    tr = P("iso_tray", "steel")
    slab(tr, XI0 - 0.035, XI1 + 0.035, -0.341, 0.341, ZL, ZT, rc=0.02, nc=(2, 1, 0)[lod], re=0.004 if lod == 0 else 0.0,
         ne=1 if lod == 0 else 0, caps=(False, True))
    parts = [tr]
    if lod == 2:
        return parts
    cs = P("iso_clamp", "steel")
    t0, t1, h = 0.0015, 0.0045, 0.022
    g.box(cs, XI0 - t1, XI1 + t1, YF - t1, YF - t0, ZT, ZT + h)
    g.box(cs, XI0 - t1, XI1 + t1, YB + t0, YB + t1, ZT, ZT + h)
    g.box(cs, XI0 - t1, XI0 - t0, YF - t0, YB + t0, ZT, ZT + h)
    g.box(cs, XI1 + t0, XI1 + t1, YF - t0, YB + t0, ZT, ZT + h)
    parts.append(cs)
    if lod == 0:
        for x in (-0.50, -0.20, 0.30):
            parts.append(bolt("clamp_bolt", (x, YF - t1 - 0.0015, ZT + h / 2), "y", 0.0045, 0.003))
            parts.append(bolt("clamp_bolt", (x, YB + t1 + 0.0015, ZT + h / 2), "y", 0.0045, 0.003))
        ft = P("frame_feet", "alu")
        for hx in HOOPS:
            for yc in (YF - HOFF, YB + HOFF):
                g.box(ft, hx - 0.013, hx + 0.013, yc - 0.011, yc + 0.011, ZT, ZT + 0.004)
        parts.append(ft)
    return parts


def build_frame(spec):
    """Frame: three arcs along the section outside the film, two longitudinal tubes along the roof ribs,
    crosspieces, film ties on the arcs."""
    lod = spec["lod"]
    tsd = (8, 5, 3)[lod]
    na = (4, 2, 1)[lod]
    hp = profile(1, 1, na, 1)
    hoop = [(y + ny * HOFF, z + nz * HOFF) for y, z, ny, nz, _ in hp]
    fr = P("iso_frame", "alu")
    for x in HOOPS:
        g.pipe(fr, [(x, y, z) for y, z in hoop], TR, tsd)
    ridge = [hoop[1 + na], hoop[2 + na]]
    for y, z in ridge:
        g.pipe(fr, [(XI0 - 0.016, y, z), (XI1 + 0.016, y, z)], TR, tsd)
    parts = [fr]
    if lod == 2:
        return parts
    jt = P("frame_joints", "black")
    for x in HOOPS:
        for y, z in ridge:
            g.box(jt, x - 0.015, x + 0.015, y - 0.015, y + 0.015, z - 0.015, z + 0.015)
    parts.append(jt)
    if lod == 0:
        tie = P("frame_ties", "black")
        rr = TR + 0.0013
        for x in HOOPS:
            for yc in (YF - HOFF,):
                z = ZT + 0.11
                g.pipe(tie, [(x + rr * math.cos(2 * math.pi * k / 6), yc + rr * math.sin(2 * math.pi * k / 6), z)
                             for k in range(7)], 0.0016, 3)
        parts.append(tie)
    return parts


def build_ports(spec):
    """Sleeve rings on the hood face: a turned ring with a flange (the tube passes through the film), a
    clamp with a lock."""
    lod = spec["lod"]
    n = (20, 12, 6)[lod]
    parts = []
    for i, px in enumerate(PX):
        c = (px, YF, PZ)
        rg = P("port_ring%d" % i, "steel", uv_name="port_ring", uv_origin=c)
        if lod == 0:
            prof = [(0.086, -0.030), (0.094, -0.030), (0.094, -0.005), (0.113, -0.003), (0.113, 0.004), (0.094, 0.006),
                    (0.094, 0.040), (0.086, 0.042)]
        else:
            prof = [(0.086, -0.020), (0.105, -0.020), (0.105, 0.040), (0.086, 0.040)]
        lathe(rg, prof, n, c, "-y", closed=True)
        parts.append(rg)
        if lod == 0:
            bd = P("port_band%d" % i, "black", uv_name="port_band", uv_origin=c)
            lathe(bd, [(0.094, 0.016), (0.0975, 0.017), (0.0975, 0.029), (0.094, 0.030)], n, c, "-y")
            g.box(bd, px - 0.009, px + 0.009, YF - 0.031, YF - 0.015, PZ - 0.1035, PZ - 0.0955)
            parts.append(bd)
    return parts


def build_gloves(spec):
    """Sleeves from the rings sag inward and lie on the board, at the end a rigid cuff, the glove palm
    down: a hand, four fingers, a thumb (the left glove in the left ring)."""
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    for i, (px, s) in enumerate(zip(PX, (-1, 1))):
        ctrl = [(px, YF + 0.022, PZ), (px, YF + 0.075, PZ - 0.012), (px + 0.008 * s, YF + 0.13, PZ - 0.06),
                (px + 0.016 * s, YF + 0.17, PZ - 0.13), (px + 0.024 * s, YF + 0.205, BDZ + 0.072),
                (px + 0.030 * s, YF + 0.25, BDZ + 0.036), (px + 0.034 * s, YF + 0.30, BDZ + 0.031),
                (px + 0.036 * s, YF + 0.34, BDZ + 0.058)]
        rad = [(0.084, 0.084), (0.082, 0.079), (0.078, 0.070), (0.073, 0.060), (0.069, 0.046), (0.066, 0.034),
               (0.062, 0.030), (0.052, 0.052)]
        k = 2 if lod == 0 else 1
        pts = spline(ctrl, k) if k > 1 else ctrl
        rr = []
        for j in range(len(ctrl) - 1):
            for q in range(k):
                t = q / k
                rr.append(tuple(a + (b - a) * t for a, b in zip(rad[j], rad[j + 1])))
        rr.append(rad[-1])
        if lod == 0:
            # soft sleeve: folds in waves along the length
            rr = [rr[0]] + [(a * (1 + 0.045 * math.sin(2.7 * j)), b * (1 + 0.06 * math.sin(2.7 * j + 0.8)))
                            for j, (a, b) in enumerate(rr[1:-1], 1)] + [rr[-1]]
        sl = P("sleeve%d" % i, "glove")
        g.tube_var(sl, pts, rr, 10 if lod == 0 else 5)
        parts.append(sl)
        c_end = Vector(ctrl[-1])
        ax = (c_end - Vector(pts[-2])).normalized()
        if lod == 0:
            cf = P("cuff%d" % i, "black")
            lathe(cf, [(0.050, -0.009), (0.057, -0.009), (0.057, 0.009), (0.050, 0.009)], 12, tuple(c_end), tuple(ax),
                  closed=True)
            parts.append(cf)
        # hand: along the sleeve axis, slightly toward the middle of the hood
        hd = Vector((ax.x, ax.y, 0.0)).normalized()
        turn = math.radians(-8.0 * s)
        hd = Vector((hd.x * math.cos(turn) - hd.y * math.sin(turn), hd.x * math.sin(turn) + hd.y * math.cos(turn), 0.0))
        sv = Vector((hd.y, -hd.x, 0.0))
        thumb = -s                                             # thumb: on the left glove it is on the right
        gl = P("glove%d" % i, "glove")

        def at(along, z, side=0.0):
            q = c_end + hd * along + sv * side
            return (q.x, q.y, z)
        if lod == 0:
            g.tube_var(gl, [at(0.004, c_end.z), at(0.045, BDZ + 0.034), at(0.090, BDZ + 0.022), at(0.122, BDZ + 0.019)],
                       [(0.047, 0.047), (0.045, 0.031), (0.049, 0.020), (0.049, 0.017)], 10)
            for o, ln, rw, rv in ((0.033, 0.070, 0.0105, 0.0092), (0.011, 0.078, 0.0108, 0.0095),
                                  (-0.011, 0.073, 0.0102, 0.0090), (-0.033, 0.057, 0.0090, 0.0080)):
                o *= thumb
                fa = o * 2.0
                fd = Vector((hd.x * math.cos(fa) - hd.y * math.sin(fa), hd.x * math.sin(fa) + hd.y * math.cos(fa), 0.0))
                b0 = c_end + hd * 0.114 + sv * o
                fp = [(b0 + fd * f) for f in (0.0, ln * 0.45, ln * 0.85, ln + 0.006)]
                zs = (BDZ + 0.0115, BDZ + 0.0098, BDZ + 0.0092, BDZ + 0.0075)
                g.tube_var(gl, [(q.x, q.y, z) for q, z in zip(fp, zs)],
                           [(rw, rv), (rw * 0.95, rv * 0.93), (rw * 0.88, rv * 0.86), (rw * 0.45, rv * 0.42)], 5)
            ta = math.radians(48.0) * thumb
            td = Vector((hd.x * math.cos(ta) - hd.y * math.sin(ta), hd.x * math.sin(ta) + hd.y * math.cos(ta), 0.0))
            b0 = c_end + hd * 0.058 + sv * (0.036 * thumb)
            tp = [(b0 + td * f) for f in (0.0, 0.028, 0.050, 0.060)]
            g.tube_var(gl, [(q.x, q.y, z) for q, z in zip(tp, (BDZ + 0.016, BDZ + 0.0125, BDZ + 0.0105, BDZ + 0.0085))],
                       [(0.0125, 0.0115), (0.0115, 0.0105), (0.0100, 0.0092), (0.0050, 0.0045)], 5)
        else:
            g.tube_var(gl, [at(0.004, c_end.z), at(0.090, BDZ + 0.022), at(0.19, BDZ + 0.012)],
                       [(0.047, 0.047), (0.049, 0.020), (0.045, 0.010)], 6)
        parts.append(gl)
    return parts


def build_inside(spec):
    """Inside the hood: the board-worktop between the modules, rubber mats of slots 1 and 3."""
    lod = spec["lod"]
    bd = P("iso_board", "board")
    slab(bd, BDX[0], BDX[1], BDY[0], BDY[1], ZT, BDZ, rc=0.010, nc=1 if lod < 2 else 0, re=0.003 if lod == 0 else 0.0,
         ne=1 if lod == 0 else 0, caps=(False, True))
    parts = [bd]
    if lod < 2:
        mt = P("slot_mats", "rubber")
        x, y, _ = MODS[0]
        g.box(mt, x - 0.10, x + 0.10, y - 0.098, y + 0.10, ZT, ZT + 0.003)
        x, y, _ = MODS[2]
        g.box(mt, x - 0.115, x + 0.115, y - 0.10, y + 0.12, ZT, ZT + 0.003)
        parts.append(mt)
    return parts


def build_lock(spec):
    """Airlock on the right end: a collar with a flange on bolts (through the film), a film sleeve, a ring
    with a clamp and a latch, a dish lid with a handle."""
    lod = spec["lod"]
    n = (22, 12, 6)[lod]
    c = (XI1, 0.0, LZ)
    parts = []
    cl = P("lock_collar", "steel")
    fr = (0.146, 0.140, 0.136)[lod]
    lathe(cl, [(0.106, -0.004), (fr, -0.004), (fr, 0.007), (0.120, 0.010), (0.120, LC1 - XI1), (0.106, LC1 - XI1)],
          n, c, "x", closed=True)
    parts.append(cl)
    if lod == 0:
        for k in range(6):
            a = math.radians(30 + 60 * k)
            parts.append(bolt("lock_bolt", (XI1 + 0.0085, 0.133 * math.cos(a), LZ + 0.133 * math.sin(a)), "x",
                              0.0055, 0.003))
    if lod < 2:
        nu, nv = (4, 20) if lod == 0 else (1, 10)
        verts, nrm, quads = {}, {}, []
        x0, x1 = LC1 - 0.006, LS1 + 0.006
        for i in range(nu + 1):
            x = x0 + (x1 - x0) * i / nu
            for k in range(nv):
                a = 2 * math.pi * k / nv
                rr = 0.1215 + ((crumple(x * 2.0, a * 0.12, 0.005, 2.0) + 0.004 * math.sin(math.pi * i / nu))
                               if 0 < i < nu else 0.0)
                verts[(i, k)] = (x, rr * math.cos(a), LZ + rr * math.sin(a))
                nrm[(i, k)] = (0.0, math.cos(a), math.sin(a))
        for i in range(nu):
            quads += [[(i, k), (i, (k + 1) % nv), (i + 1, (k + 1) % nv), (i + 1, k)] for k in range(nv)]
        sl = P("lock_sleeve", "steel", section="glass")
        film_sheet(sl, verts, quads, nrm)
        parts.append(sl)
    er = P("lock_ring", "steel")
    h0, h1 = LS1 - XI1 - 0.006, LCAP - XI1
    lathe(er, [(0.106, h0), (0.1205, h0), (0.1205, h1), (0.106, h1)], (n, 10, n)[lod], c, "x", closed=True)
    parts.append(er)
    if lod == 0:
        bd = P("lock_band", "black")
        hb0, hb1 = LS1 - XI1 - 0.003, LS1 - XI1 + 0.011
        lathe(bd, [(0.1215, hb0), (0.1245, hb0 + 0.001), (0.1245, hb1 - 0.001), (0.1215, hb1)], n, c, "x")
        g.box(bd, LS1 - 0.004, LS1 + 0.016, -0.008, 0.008, LZ + 0.123, LZ + 0.133)
        parts.append(bd)
    cp = P("lock_cap", "steel")
    hc = LCAP - XI1
    lathe(cp, [(0.1215, hc), (0.1215, hc + 0.010), (0.112, hc + 0.018), (0.060, hc + 0.025), (0.0, hc + 0.027)] if lod < 2
          else [(0.1215, hc), (0.1215, hc + 0.012), (0.0, hc + 0.024)], n, c, "x")
    # the back of the lid is visible from inside the hood through the sleeve (it faces -x)
    lathe(cp, [(0.0, hc + 0.0005), (0.106, hc + 0.0005)], n, c, "x")
    parts.append(cp)
    if lod < 2:
        hd = P("lock_handle", "black")
        cx_ = LCAP + 0.025
        pts = [(cx_ - 0.004, 0.0, LZ - 0.055), (cx_ + 0.012, 0.0, LZ - 0.052), (cx_ + 0.020, 0.0, LZ - 0.032),
               (cx_ + 0.020, 0.0, LZ + 0.032), (cx_ + 0.012, 0.0, LZ + 0.052), (cx_ - 0.004, 0.0, LZ + 0.055)]
        cable(hd, pts, 0.0065, 6 if lod == 0 else 4, k=2 if lod == 0 else 1)
        parts.append(hd)
    return parts


def build_filter(spec):
    """Filter cartridge on the airlock collar: a neck, a can with rolled edges, yellow tape, a side nozzle
    (to the corrugated hose) with a clamp."""
    lod = spec["lod"]
    n = (16, 10, 6)[lod]
    c = (FX, 0.0, 0.0)
    fl = P("filter", "filter")
    if lod == 0:
        prof = [(0.027, LZ + 0.105), (0.027, FZ0 + 0.004), (0.052, FZ0 + 0.006), (0.0575, FZ0 + 0.011),
                (0.0575, FZ0 + 0.021), (0.055, FZ0 + 0.025), (0.055, FZ1 - 0.025), (0.0575, FZ1 - 0.021),
                (0.0575, FZ1 - 0.011), (0.050, FZ1 - 0.003), (0.020, FZ1), (0.0, FZ1 + 0.001)]
    else:
        prof = [(0.027, LZ + 0.105), (0.027, FZ0), (0.056, FZ0 + 0.004), (0.056, FZ1 - 0.004), (0.045, FZ1),
                (0.0, FZ1 + 0.001)]
    lathe(fl, prof, n, c, "z")
    parts = [fl]
    if lod == 2:
        return parts
    if lod == 0:
        yb = P("filter_tape", "tape_y")
        zb = FZ0 + 0.04
        lathe(yb, [(0.0552, zb), (0.0562, zb + 0.002), (0.0562, zb + 0.024), (0.0552, zb + 0.026)], n, c, "z")
        parts.append(yb)
    sp = P("filter_spigot", "steel")
    g.cyl(sp, (FX + 0.075, 0.0, FSZ), "x", 0.024, 0.05, (12, 8)[lod])
    parts.append(sp)
    return parts


def hose_path():
    return resample(spline(HOSE, 6), 0.017)


def hose_clamp(name, at, axis, lod):
    cp = P(name, "steel", uv_name="hose_clamp", uv_origin=at)
    lathe(cp, [(0.0262, -0.0065), (0.0287, -0.0055), (0.0287, 0.0055), (0.0262, 0.0065)], 12, at, axis)
    a, b, w = basis(axis)
    q = Vector(at) + b * 0.029
    g.box(cp, q.x - 0.006, q.x + 0.006, q.y - 0.006, q.y + 0.006, q.z - 0.004, q.z + 0.004)
    return cp


def build_hose(spec):
    """Corrugated hose: corrugation rings every half step, radius is crest and valley; clamps at the ends."""
    lod = spec["lod"]
    hp = hose_path()
    hs = P("hose", "hose")
    if lod == 0:
        g.tube_var(hs, hp, [((HOSE_R if k % 2 == 0 else HOSE_R * 0.87),) * 2 for k in range(len(hp))], 9)
    else:
        g.pipe(hs, hp[::6] + ([hp[-1]] if (len(hp) - 1) % 6 else []), HOSE_R * 0.95, (6, 4)[lod - 1])
    parts = [hs]
    if lod == 0:
        a0 = Vector(hp[0])
        parts.append(hose_clamp("hose_clamp_f", (a0.x + 0.008, a0.y, a0.z), "x", lod))
        e = Vector(hp[-1])
        parts.append(hose_clamp("hose_clamp_v", (e.x, e.y + 0.008, e.z), "y", lod))
    return parts


def build_fan(spec):
    """Axial fan on the chest lid: a shroud, a cone with a nozzle to the hose, a motor on stays, five
    twisted blades with a hub (bone ozl_fan), a guard, a fork stand, a cord with a switch."""
    lod = spec["lod"]
    c = tuple(FAN)
    n = (20, 10, 6)[lod]
    a_, b_, w_ = basis("y")
    parts = []
    sh = P("fan_shroud", "fan")
    if lod == 0:
        lathe(sh, [(0.084, -0.030), (0.090, -0.030), (0.093, -0.027), (0.093, 0.027), (0.090, 0.030), (0.084, 0.030)], n,
              c, "y", closed=True)
        lathe(sh, [(0.090, 0.030), (0.074, 0.046), (0.046, 0.062), (0.030, 0.068), (0.026, 0.074), (0.026, 0.106)], 14,
              c, "y")
    else:
        lathe(sh, [(0.085, -0.030), (0.093, -0.030), (0.093, 0.030), (0.085, 0.030)], n, c, "y", closed=True)
        lathe(sh, [(0.093, 0.030), (0.040, 0.066), (0.026, 0.106)], n, c, "y")
    parts.append(sh)
    # motor, back wall (it is seen through the blades instead of emptiness), stays
    mo = P("fan_motor", "black")
    if lod < 2:
        lathe(mo, [(0.0, -0.007), (0.029, -0.007), (0.032, -0.004), (0.032, 0.022), (0.026, 0.028)], (14, 6)[lod], c, "y")
    lathe(mo, [(0.0, 0.029), (0.0845, 0.029)], n, c, "y")
    if lod == 0:
        for k in range(3):
            t = math.pi / 2 + 2 * math.pi * k / 3
            u = a_ * math.cos(t) + b_ * math.sin(t)
            g.pipe(mo, [tuple(Vector(c) + u * 0.030 + w_ * 0.024), tuple(Vector(c) + u * 0.086 + w_ * 0.024)], 0.003, 4)
    parts.append(mo)
    # blades and hub: bone ozl_fan (rotation about the axis ozl_fan_axis)
    bl = P("fan_blades", "blade", group=SEL_FAN)
    if lod == 2:
        # far LOD: the blades are a disc (the same bone)
        lathe(bl, [(0.0, -0.016), (0.078, -0.013)], 6, c, "y")
        parts.append(bl)
    else:
        lathe(bl, [(0.0, -0.031), (0.007, -0.030), (0.016, -0.025), (0.021, -0.016), (0.021, -0.004)], (12, 6)[lod], c,
              "y")
    nr, nx = ((3, 2), (1, 1), (0, 0))[lod]
    r0, r1, hb = 0.022, 0.080, -0.013
    for kb in range(5 if lod < 2 else 0):
        th = 2 * math.pi * kb / 5 + 0.3
        ur = a_ * math.cos(th) + b_ * math.sin(th)
        ut = -a_ * math.sin(th) + b_ * math.cos(th)

        def blade_pt(rho, xi, side):
            q = (rho - r0) / (r1 - r0)
            cl, beta, sw = 0.030 + 0.022 * q, math.radians(40.0 - 18.0 * q), 0.010 * q * q
            nrm = -ut * math.sin(beta) + w_ * math.cos(beta)
            return (Vector(c) + ur * rho + ut * (sw + xi * cl * math.cos(beta)) + w_ * (hb + xi * cl * math.sin(beta)) +
                    nrm * (0.001 * side)), nrm, ut * math.cos(beta) + w_ * math.sin(beta)
        bm = bl.bm
        vs = {(i, j, sd): bm.verts.new(blade_pt(r0 + (r1 - r0) * i / nr, -0.5 + j / nx, sd)[0])
              for i in range(nr + 1) for j in range(nx + 1) for sd in (-1, 1)}
        new = []
        for i in range(nr):
            for j in range(nx):
                _, nrm, _ = blade_pt(r0 + (r1 - r0) * (i + 0.5) / nr, 0.0, 0)
                for sd in (-1, 1):
                    new.append(face(bl, [vs[(i, j, sd)], vs[(i + 1, j, sd)], vs[(i + 1, j + 1, sd)], vs[(i, j + 1, sd)]],
                                    nrm * sd))
            for j, sg in ((0, -1), (nx, 1)):
                _, _, ch = blade_pt(r0 + (r1 - r0) * (i + 0.5) / nr, 0.0, 0)
                new.append(face(bl, [vs[(i, j, -1)], vs[(i + 1, j, -1)], vs[(i + 1, j, 1)], vs[(i, j, 1)]], ch * sg))
        for j in range(nx):
            new.append(face(bl, [vs[(nr, j, -1)], vs[(nr, j + 1, -1)], vs[(nr, j + 1, 1)], vs[(nr, j, 1)]], ur))
        bl.tag(new)
    if lod < 2:
        parts.append(bl)
    if lod < 2:
        # guard: rings, spokes, a boss
        gd = P("fan_guard", "steel")
        hg = -0.037
        for rr, m in (((0.089, 16), (0.052, 10)) if lod == 0 else ((0.089, 10),)):
            g.pipe(gd, [tuple(Vector(c) + (a_ * math.cos(2 * math.pi * k / m) + b_ * math.sin(2 * math.pi * k / m)) * rr +
                              w_ * hg) for k in range(m + 1)], 0.0016, 3)
        for k in range(6 if lod == 0 else 0):
            t = 2 * math.pi * k / 6 + math.pi / 6
            u = a_ * math.cos(t) + b_ * math.sin(t)
            g.pipe(gd, [tuple(Vector(c) + u * 0.012 + w_ * (hg - 0.001)), tuple(Vector(c) + u * 0.089 + w_ * hg)], 0.0015, 3)
        parts.append(gd)
        if lod == 0:
            bg = P("fan_badge", "chrome")
            lathe(bg, [(0.0, -0.040), (0.016, -0.0395), (0.016, -0.036)], 10, c, "y")
            parts.append(bg)
    # stand: a plate on the lid, a fork at the sides of the shroud, wing nuts on the axis
    st = P("fan_stand", "fan")
    slab(st, c[0] - 0.075, c[0] + 0.075, c[1] - 0.045, c[1] + 0.045, ZL, ZL + 0.006, rc=0.012, nc=(2, 1, 0)[lod],
         re=0.002 if lod == 0 else 0.0, ne=1 if lod == 0 else 0, caps=(False, True))
    for s in (-1, 1):
        x = c[0] + s * 0.099
        g.box(st, x - 0.003, x + 0.003, c[1] - 0.012, c[1] + 0.012, ZL + 0.006, c[2] + 0.012)
    parts.append(st)
    if lod == 0:
        kn = P("fan_knobs", "black")
        for s, ax in ((1, "x"), (-1, "-x")):
            lathe(kn, [(0.010, 0.0), (0.010, 0.008), (0.006, 0.011), (0.0, 0.012)], (10, 6)[lod],
                  (c[0] + s * 0.102, c[1], c[2]), ax)
        parts.append(kn)
    if lod == 0:
        for x in (c[0] - 0.058, c[0] + 0.058):
            parts.append(bolt("fan_bolt", (x, c[1] - 0.028, ZL + 0.0072), "z", 0.0045, 0.0024))
    if lod == 0:
        # cord: from the cone down, along the lid to the right edge, over the back edge, along the back, to the
        # splice on the floor
        cd = P("fan_cord", "cable")
        r_ = 0.0035
        pts = [(c[0] + 0.02, c[1] + 0.052, c[2] - 0.060), (c[0] + 0.035, c[1] + 0.075, ZL + 0.030),
               (c[0] + 0.055, c[1] + 0.12, ZL + r_ + 0.001), (0.734, -0.02, ZL + r_ + 0.001), (0.737, 0.29, ZL + r_ + 0.001),
               (0.737, 0.331, ZL + r_ + 0.001), (0.737, 0.3445, 0.8585), (0.737, CY1 + LIP + r_ + 0.001, 0.846),
               (0.736, CY1 + LIP + r_ + 0.001, 0.62), (0.73, CY1 + 0.012, 0.20), (0.71, CY1 + 0.045, r_ + 0.001),
               (0.58, 0.50, r_ + 0.001), tuple(Vector(MAIN[SPL[0]]) + Vector((0.03, -0.004, -0.004)))]
        cable(cd, pts, r_, 5 if lod == 0 else 4, k=2 if lod == 0 else 1)
        parts.append(cd)
        swc = P("fan_switch", "socket")
        slab(swc, 0.736 - 0.012, 0.736 + 0.012, 0.07, 0.13, ZL, ZL + 0.018, rc=0.005, nc=1 if lod == 0 else 0,
             re=0.004 if lod == 0 else 0.0, ne=1 if lod == 0 else 0, caps=(False, True))
        parts.append(swc)
        if lod == 0:
            kb = P("fan_switch_key", "black")
            g.box(kb, 0.736 - 0.006, 0.736 + 0.006, 0.088, 0.104, ZL + 0.017, ZL + 0.0215, r=0.0015, seg=1)
            parts.append(kb)
    return parts


def build_lod(spec):
    parts = build_chest(spec) + build_panel(spec) + build_wrap(spec) + build_thermometer(spec) + build_cables(spec)
    parts += build_shelf(spec) + build_tray(spec) + build_film(spec) + build_frame(spec) + build_ports(spec)
    parts += build_gloves(spec) + build_inside(spec) + build_lock(spec) + build_filter(spec) + build_hose(spec)
    parts += build_fan(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        if M.stats:
            check_layout()
    return parts


# modules in the slots: the near-LOD envelope in Blender from the proxy point (their MLOD) - for the check
MOD_BOX = [((-0.085, -0.096, 0.0), (0.085, 0.085, 0.241)), ((-0.095, -0.109, 0.0), (0.095, 0.129, 0.181)),
           ((-0.103, -0.080, 0.0), (0.103, 0.118, 0.198))]


def check_layout():
    """--stats: vanilla items and modules do not intersect each other (envelopes along the axes)."""
    boxes = []
    for d in DECOR:
        q = kv.corners(d[5], d[1], d[2], d[3])
        boxes.append((str(d[5]).split("\\")[-1], tuple(min(p[i] for p in q) for i in range(3)),
                      tuple(max(p[i] for p in q) for i in range(3))))
    for (o, _), m, (lo, hi) in zip(MOD_OBJ, MODS, MOD_BOX):
        boxes.append((o, tuple(m[i] + lo[i] for i in range(3)), tuple(m[i] + hi[i] for i in range(3))))
    for n, lo, hi in boxes:
        print("layout: %-16s x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f" % (n, lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if all(a[1][k] < b[2][k] - 0.002 and b[1][k] < a[2][k] - 0.002 for k in range(3)):
                print("layout: OVERLAP %s / %s" % (a[0], b[0]))


def collision():
    metal = kx.PEN + r"\metalplate.rvmat"
    chest = kx.box_pts(CX0 - LIP, CX1 + LIP, CY0 - LIP, CY1 + LIP, 0.0, ZL)
    # a component thinner than 0.5 m does not work: the hood and the shelf go down into the chest
    iso = kx.box_pts(XI0 - 0.04, 0.88, YF - 0.04, YB + 0.04, 0.40, ZR + 0.03)
    shelf = kx.box_pts(SX0, CX0 + 0.25, CY0, CY1, SZ - 0.50, SZ)
    comps = [(chest, metal), (iso, metal), (shelf, metal)]
    memory = {
        "invView": [(0.0, -2.8, 1.1)],
        "ce_center": [(0.0, 0.0, 0.75)],
        "ce_radius": [(1.0, 0.0, 0.75)],
        # blade rotation axis (ozl_work): from the hub along the fan axis
        "ozl_fan_axis": [(FAN.x, FAN.y, FAN.z), (FAN.x, FAN.y + 0.05, FAN.z)],
    }
    for i, m in enumerate(MODS):
        memory["module_%d" % (i + 1)] = [m]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], min(hi[1], CY1 + 0.05), 0.0, hi[2])
    return comps, 120.0, memory, bbox


# the first ones are for the --look preview: overview, all three slots (and the same empty), the
# airlock with the fan (and in "work"), the isolator close-up, the chest face, the shelf, the back
SHOTS = [
    ("front", (-1.35, -2.9, 1.75), (0.0, 0.0, 0.88), 30),
    ("slots", (-1.30, -1.50, 1.62), (-0.42, -0.04, 0.96), 32),
    ("lock_fan", (1.45, -1.20, 1.42), (0.58, -0.06, 1.06), 34),
    ("isolator", (-0.25, -1.30, 1.50), (-0.10, 0.0, 1.06), 32),
    ("chest", (0.62, -1.20, 0.92), (0.36, -0.34, 0.66), 36),
    ("shelf", (-1.85, -0.95, 1.30), (-0.88, 0.0, 0.76), 34),
    ("back", (1.5, 2.3, 1.5), (0.0, 0.2, 0.6), 30),
]

M.look_shots = (6, 3)
M.run(build_lod, collision, SHOTS, row_step=2.0, row_shot=((2.0, -7.0, 1.8), (2.0, 0, 0.8)))
