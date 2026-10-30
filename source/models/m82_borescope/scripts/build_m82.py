"""M82 - borescope (OZL_Tool_Borescope): a Ballistic line module (packers M23, M27, M32), a portable
2x2 item. It sits in an OZL_Tool1..3 slot and shows on the machine shelf through the proxy.
A rigid gun borescope in an open case.

    blender --background --python build_m82.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py (system Python) before the first build: the diagram card without text, the
cotton swab pack, the inventory number.

Size: an open case of about 0.22 x 0.06 x 0.16 m (the lid back, not higher than about 0.2 m), a
probe of D ~6 mm across the case, chrome and black. The module is at most ~0.2 x 0.2 m at the
base and up to ~0.25 m high, flat bottom.

Look: the "dayz" look (more matte, dirtier, corner shading in colour). The case has rounded bottom
and top edges, a bumper band at the halves' joint, a rim, a piano hinge on rivets, a handle on
two bosses (an arc of elliptical section, no kinks) and flip-open latches: a plastic lever with a
thumb stop, an axle, a wire bail, a mating hook on the lid. The instruments are solids of
revolution by profile (revolve): an eyecup with a cup and a sunk lens, a focus ring with knurling,
steps and chamfers, a light-guide fitting with a groove. The flashlight has a rounded tail, a
knurled body, an adapter sleeve, a nose with a socket, and in the socket a reflector and a bulb.
Batteries have a crimp, a stripe and a "plus"; the seal has a rounded edge and a wire twisted
into a strand. The foam has pores, the cut-outs have rounded corners. The strap in the lid holds
the card, the swab pack and the vanilla DayZ pen (a kv.put proxy; in the preview a light-blue
box of its bounds).
Work look: the illuminator's bulb and the socket reflector glow (selection ozl_lamp_work, the _on
atlas and an rvmat with emission); the loop is a short blink (blink), like a flashlight with a
loose contact. The borescope has no moving parts.

Proportions:
- The instrument is a Hawkeye Classic Rigid (Gradient Lens Corp., USA): a black anodized eyepiece
  with a DIN 32 mm eyecup and a focus ring, a stainless body with a light-guide fitting at the
  side, a cone and a rigid probe. The Hardy probe is D 6.35 mm, the mirror tube D 8.0 mm; the
  eyecup is DIN 32 mm. The body with the eyepiece is ~80 mm, from a photo scaled by the 32 mm eyecup.
- The illuminator is a Mini Maglite AA with a Hawkeye adapter instead of the head: datasheet
  146 mm, body D 18 mm, head D 25.4 mm. Here: a body with a 110 mm tail, a silver adapter sleeve
  D 24 with knurling and a nose D 13 with a socket for the light-guide fitting.
- A mirror tube D 8 with a knurled head and a mirror window at the end, two AA batteries
  (D 14.5 x 50.5), cotton swabs in a pack - as in the case in the photo.
- The case is black ABS, a blue foam insert with cut-outs shaped like the instruments, egg-crate
  foam in the lid. Sellers and the maker give no case sizes (only the packaging of the Hardy 7"
  kit: 22 x 6 x 3").
Length. The shortest Hawkeye is 7" (a 180 mm probe): with the body and eyepiece it is ~0.26 m, a
case for it would be ~0.28 m, while the module_N places on M32 are 0.25 m apart (0.28 on M23/M27)
and the pad is 0.22 m. So the probe is shortened to 0.12 m (rigid rod-lens borescopes exist from
~50 mm of working length): the whole instrument is 0.20 m, the closed case 0.222 x 0.140 x
0.058 m. The lid is opened by 100 degrees: the top at ~0.18 m, the whole module ~0.22 x 0.20 m at
the base (the lid hangs back, which is allowed); the base centre is shifted forward so that the
bounds stand at the centre of the module point. The band at the halves' joint follows the bounds
0.222 x 0.140, the walls below and above it are sunk by 1.5 mm: the bounds are unchanged.

Condition (no faction colour): used but intact, worn paint on the edges (the blue foam is the
material colour, as in the photo, not the light-blue faction colour). Markings: the card in the
lid is a diagram and pictograms without words; a broken lead seal on a wire lies on the insert
(the case was sealed in the armoury); the inventory number in white paint on the case face -
digits only.
LODs: near and mid (~40 %: solids of revolution with fewer sides and steps, no insert cut-outs,
bails, hinge, seal and strap), no far one.

Blender axes: X is along the shelf, Y is depth (the face at -Y, the hinges at the back), Z is up.
The origin is the centre of the bottom of the bounds, so the module lands on the module_N proxy
point (autocenter = 0 in Geometry).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import bmesh  # noqa: E402
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import kvanilla as kv  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))


def _smooth_normal(self):
    """The normal for dust, streaks, decals and knurling is the smooth one (Geometry Normal), not the
    face one (True Normal, as in kmats.Tree.normal): on solids of revolution each face would otherwise
    get its own share of dust and a cylinder in colour would look faceted. The substitution is only in
    this generator, the kit is untouched; on flat faces there is no difference.
    """
    gn = self.node("ShaderNodeNewGeometry")
    s = self.node("ShaderNodeSeparateXYZ")
    self.link(gn.outputs["Normal"], s.inputs[0])
    return s


kmats.Tree.normal = _smooth_normal

# --- dimensions, m ------------------------------------------------------------------------------
# case: two halves on a hinge at the back, the lid opened back
W, D = 0.222, 0.140
HX, HY = W / 2, D / 2
YB = -0.020                     # base centre: the bounds with the lid are centred on the module point
BASE_H, LID_H = 0.036, 0.022
WALL = 0.003
RC = 0.012                      # corner rounding in plan
BAND, BAND_H = 0.0015, 0.007    # band at the halves' joint: the walls below and above are sunk by BAND
FIL_B, FIL_L = 0.003, 0.004     # rounding of the base bottom and the lid top
RIM = 0.0008                    # rim chamfer
CAV = BAND + WALL               # cavity - from the bounds
HINGE = (YB + HY + 0.003, BASE_H)
OPEN = -100.0                   # degrees about X
FOAM_Z = 0.028                  # insert top
LF = 0.012                      # lid foam
ZF = BASE_H + LID_H - WALL - LF  # lid foam face (looks down when closed)
YF = YB - HY                    # case face (band)
YW = YF + BAND                  # face wall under the band
XI = HX - CAV                   # interior along X
C30, S30 = math.cos(math.radians(30)), math.sin(math.radians(30))
# half profiles (height, sink from the bounds); for the lid - in the closed position
BASE_PROF = [(0.0, BAND + FIL_B), (FIL_B * (1 - C30), BAND + FIL_B * (1 - S30)),
             (FIL_B * (1 - S30), BAND + FIL_B * (1 - C30)), (FIL_B, BAND),
             (BASE_H - BAND_H, BAND), (BASE_H - BAND_H + 0.001, 0.0), (BASE_H - RIM, 0.0), (BASE_H, RIM)]
_ZT = BASE_H + LID_H
LID_PROF = [(BASE_H, RIM), (BASE_H + RIM, 0.0), (BASE_H + BAND_H - 0.001, 0.0), (BASE_H + BAND_H, BAND),
            (_ZT - FIL_L, BAND), (_ZT - FIL_L + FIL_L * S30, BAND + FIL_L * (1 - C30)),
            (_ZT - FIL_L + FIL_L * C30, BAND + FIL_L * (1 - S30)), (_ZT, BAND + FIL_L)]
BASE_LO = [(0.0, BAND + 0.0015), (0.0015, BAND), (BASE_H - BAND_H, BAND), (BASE_H - BAND_H, 0.0), (BASE_H, 0.0)]
LID_LO = [(BASE_H, 0.0), (BASE_H + BAND_H, 0.0), (BASE_H + BAND_H, BAND), (_ZT - 0.0015, BAND), (_ZT, BAND + 0.0015)]

# Profiles of solids of revolution: (along the axis, radius, region of the segment up to the next
# point). Traversal such that the material is on the right: along the axis forward - the surface
# outward; r = 0 - the end converges to a point.
# borescope: axis along X
SY, SZ = YB + 0.038, FOAM_Z - 0.003
SCOPE = [
    (-0.0985, 0.0, "eyelens"),        # ocular lens sunk in the eyecup cup
    (-0.0985, 0.0085, "rubber_eye"),  # cup
    (-0.1008, 0.0106, "rubber_eye"),  # DIN 32 eyecup lip
    (-0.1012, 0.0140, "rubber_eye"),
    (-0.1004, 0.0156, "rubber_eye"),
    (-0.0988, 0.0161, "rubber_eye"),
    (-0.0966, 0.0158, "rubber_eye"),
    (-0.0956, 0.0140, "anod"),        # eyecup fitted on the eyepiece
    (-0.0956, 0.0130, "anod"),
    (-0.0925, 0.0130, "anod"),
    (-0.0921, 0.0139, "knurl_eye"),   # focus ring with knurling
    (-0.0839, 0.0139, "anod"),
    (-0.0835, 0.0130, "anod"),
    (-0.0672, 0.0130, "anod"),
    (-0.0666, 0.0122, "anod"),
    (-0.0666, 0.0114, "anod"),        # neck
    (-0.0606, 0.0114, "stainless"),
    (-0.0602, 0.0105, "stainless"),   # stainless body
    (-0.0310, 0.0105, "stainless"),
    (-0.0300, 0.0100, "stainless"),   # cone
    (-0.0215, 0.0042, "stainless"),
    (-0.0215, 0.0, None),
]
SCOPE_LO = [(-0.1012, 0.0, "eyelens"), (-0.1012, 0.0100, "rubber_eye"), (-0.1012, 0.0160, "rubber_eye"),
            (-0.0956, 0.0160, "anod"), (-0.0956, 0.0132, "anod"), (-0.0606, 0.0132, "stainless"),
            (-0.0606, 0.0105, "stainless"), (-0.0300, 0.0105, "stainless"), (-0.0215, 0.0042, "stainless"),
            (-0.0215, 0.0, None)]
PROBE = [(-0.0218, 0.00318, "stainless"), (0.0986, 0.00318, "stainless"), (0.0998, 0.0026, "fiber"),
         (0.0998, 0.0, None)]                                       # Hardy probe D 6.35, the end is a window
PROBE_LO = [(-0.0218, 0.0032, "stainless"), (0.0998, 0.0032, "stainless"), (0.0998, 0.0, None)]
FOCUS_R = 0.0139
# light-guide fitting: forward (-Y) from the body, from the borescope axis
POST_X = -0.044
POST = [(0.0090, 0.0042, "stainless"), (0.0130, 0.0042, "stainless"), (0.0133, 0.0035, "stainless"),
        (0.0143, 0.0035, "stainless"), (0.0146, 0.0040, "stainless"), (0.0243, 0.0040, "stainless"),
        (0.0250, 0.0024, "fiber"), (0.0250, 0.0, None)]
POST_LO = [(0.0090, 0.0041, "stainless"), (0.0250, 0.0041, "stainless"), (0.0250, 0.0, None)]
POST_END = 0.0250
# illuminator: an AA flashlight with an adapter
LY, LZ = YB - 0.042, FOAM_Z - 0.004
LIGHT = [
    (-0.0640, 0.0, "anod"),           # tail end
    (-0.0640, 0.0072, "anod"),
    (-0.0636, 0.0091, "anod"),
    (-0.0627, 0.0098, "anod"),
    (-0.0549, 0.0098, "anod"),
    (-0.0545, 0.0090, "anod"),        # joint of tail and body
    (-0.0400, 0.0090, "knurl_light"),  # body knurling
    (0.0320, 0.0090, "anod"),
    (0.0445, 0.0090, "alu"),          # adapter sleeve
    (0.0445, 0.0112, "alu"),
    (0.0453, 0.0120, "knurl_collar"),
    (0.0672, 0.0120, "alu"),
    (0.0680, 0.0111, "alu"),
    (0.0680, 0.0066, "alu"),          # nose
    (0.0935, 0.0066, "alu"),
    (0.0948, 0.0056, "alu"),
    (0.0948, 0.0043, None),           # further the socket (in the lamp selection)
]
LIGHT_LO = [(-0.0640, 0.0, "anod"), (-0.0640, 0.0095, "anod"), (0.0445, 0.0092, "alu"),
            (0.0445, 0.0120, "knurl_collar"), (0.0680, 0.0120, "alu"), (0.0680, 0.0066, "alu"),
            (0.0948, 0.0066, "alu"), (0.0948, 0.0045, None)]
LAMP = [(0.0948, 0.0043, "alu_in"), (0.0910, 0.0043, "lens"), (0.0910, 0.0, None)]  # socket, reflector at the bottom
LAMP_LO = [(0.0948, 0.0045, "lens"), (0.0948, 0.0, None)]
BULB = [(0.0911, 0.0022, "bulb"), (0.0922, 0.0021, "bulb"), (0.0930, 0.0013, "bulb"), (0.0933, 0.0, None)]
LENS_END = 0.0948
# mirror tube
MY, MZ = YB + 0.002, FOAM_Z - 0.0015
MIRROR = [
    (-0.0312, 0.0, "alu"),
    (-0.0312, 0.0056, "alu"),
    (-0.0307, 0.0065, "knurl_knob"),  # knurled head
    (-0.0205, 0.0065, "alu"),
    (-0.0200, 0.0055, "alu"),
    (-0.0200, 0.0048, "stainless"),
    (-0.0165, 0.0048, "stainless"),
    (-0.0158, 0.0040, "stainless"),
    (0.0975, 0.0040, "stainless"),
    (0.0985, 0.0031, "stainless"),
    (0.0985, 0.0, None),
]
MIRROR_LO = [(-0.0312, 0.0, "alu"), (-0.0312, 0.0065, "knurl_knob"), (-0.0200, 0.0065, "alu"),
             (-0.0200, 0.0040, "stainless"), (0.0985, 0.0040, "stainless"), (0.0985, 0.0, None)]
# AA batteries along Y, plus ends opposite (from minus to plus)
BAT_X, BAT_Y, BAT_Z, BAT_R = (-0.0940, -0.0780), YB - 0.012, FOAM_Z - 0.002, 0.00725
BAT = [(-0.0252, 0.0, "steel"), (-0.0252, 0.0063, "battery"), (-0.0246, BAT_R, "battery"),
       (0.0170, BAT_R, "battery_top"), (0.0246, BAT_R, "battery_top"), (0.0252, 0.0063, "steel"),
       (0.0252, 0.0029, "steel"), (0.0264, 0.0026, "steel"), (0.0264, 0.0, None)]
BAT_LO = [(-0.0252, 0.0, "battery"), (-0.0252, BAT_R, "battery"), (0.0252, BAT_R, "battery"), (0.0252, 0.0, None)]
BAT_HALF = 0.0264
# seal on the insert: a lead washer and a wire
SEAL = (0.036, YB - 0.016, 0.0050, 0.0031)
SEAL_PROF = [(0.0, 0.0046, "lead"), (0.0005, 0.0050, "lead"), (0.0024, 0.0050, "lead"), (0.0030, 0.0042, "lead"),
             (0.0031, 0.0, None)]
# lid: the card and the swab pack under the strap (closed-lid coordinates)
CARD = (-0.100, -0.010, YB - 0.026, YB + 0.036)          # 90 x 62 mm
PACK = (0.010, 0.086, YB - 0.026, YB + 0.004)            # 76 x 30 mm
PACK_T = 0.004
STRAP_Y, STRAP_W, STRAP_T = YB - 0.028, 0.012, 0.0012
PEN_X, PEN_Y = 0.0975, YB                                # vanilla pen under the strap
PEN_H = 0.0070                                            # its thickness above the foam (bounds along X)
# handle and latches on the face
HANDLE_X, HANDLE_Z = 0.047, 0.0215
LATCH_X = 0.082
INV_X, INV_Z, INV_W, INV_H = -0.0625, 0.019, 0.018, 0.0060   # narrow so that the left latch does not cover the "5"

LOD_SPECS = [
    dict(lod=0, sides=14, seg=3),
    dict(lod=1, sides=8, seg=1),
]

REGIONS = {
    "case": ("case", 0.8), "case_in": ("case", 0.5), "foam": ("foam", 0.7), "foam_cut": ("foam", 0.7),
    "foam_lid": ("foam_lid", 0.8), "anod": ("anod", 1.5), "rubber_eye": ("rubber_eye", 1.5),
    "knurl_eye": ("knurl_eye", 2.5), "knurl_light": ("knurl_light", 2.5), "knurl_collar": ("knurl_collar", 2.5),
    "knurl_knob": ("knurl_knob", 2.5), "stainless": ("stainless", 1.5), "alu": ("alu", 1.5), "alu_in": ("alu_in", 1.0),
    "eyelens": ("eyelens", 1.0), "fiber": ("fiber", 1.0), "lens": ("lens", 1.0), "bulb": ("bulb", 1.0),
    "battery": ("battery", 1.5), "battery_top": ("battery_top", 1.5),
    "steel": ("steel", 1.0), "hinge": ("hinge", 1.2), "latch_pl": ("latch_pl", 1.4), "black": ("black", 1.2),
    "lead": ("lead", 2.0), "wire": ("wire", 1.0), "card": ("card", 2.2), "pack": ("pack", 2.0),
    "strap": ("strap", 1.0), "dark": ("dark", 0.6),
}


def wdecal(name):
    return os.path.join(WORK, name)


def lid_rot():
    return Matrix.Rotation(math.radians(OPEN), 3, "X")


def lid_point(x, y, z):
    """A lid point in the closed position -> in the open one."""
    c = Vector((0.0, HINGE[0], HINGE[1]))
    return tuple(c + lid_rot() @ (Vector((x, y, z)) - c))


def lid_vec(v):
    """A lid direction in the closed position -> in the open one."""
    return tuple(lid_rot() @ Vector(v))


COS_T = abs(math.cos(math.radians(OPEN + 90)))   # vertical size of the lid decal


def lid_decal(fn, rect, z):
    x0, x1, y0, y1 = rect
    c = lid_point((x0 + x1) / 2, (y0 + y1) / 2, z)
    return (wdecal(fn), "y", -1, ("x", "z"), (c[0], c[2]), (x1 - x0, (y1 - y0) * COS_T), (c[1] - 0.02, c[1] + 0.02))


CARD_DEC = lid_decal("decal_card.png", CARD, ZF - 0.0008)
PACK_DEC = lid_decal("decal_swabs.png", PACK, ZF - PACK_T)
INV_DEC = (wdecal("decal_inv.png"), "y", -1, ("x", "z"), (INV_X, INV_Z), (INV_W, INV_H), (YF - 0.002, YF + 0.002))

LIT = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0)
PAPER = kmats.lin((234, 230, 216))
ANOD = dict(color=kmats.lin((24, 24, 26)), under=kmats.lin((150, 152, 154)), chip=(0.80, 0.86), floor_z=0.0,
            gloss=0.50, spec=0.45, dust=0.12, grime=0.18)
SILVER = dict(tone=0.40, along="x", gloss=0.55, spec=0.6, dust=0.08, grime=0.2)


def _tree(mat):
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    return t


def _height(t, mat, outs):
    h = outs["height"]
    return kmats.sock(mat, h) if not isinstance(h, (int, float)) else h


def build_coat(mat, origin, color, under, seed=1.0, gloss=0.45, spec=0.35, chip=(0.60, 0.66), floor_z=0.0,
               dust=0.35, grime=0.5, decal_items=(), **_):
    """As kmats.build_paint (tone patches, decals, chips along edges down to `under`, dust and dirt), but
    without rust: build_paint rusts its chips, while the case plastic and anodized aluminium do not
    rust - the chips on them are light.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.93 for c in color[:3]) + (1,), color)
    col = kmats.decals(t, base, sep, nsep, decal_items)
    edge = t.maprange(t.edge_wear(0.004), 0.06, 0.25, 0.0, 1.0)
    blot = t.noise(vec, 11.0, 10.0, 0.7)
    chips = t.step(t.math("ADD", t.math("MULTIPLY", blot, 0.75), t.math("MULTIPLY", edge, 0.55)), chip[0], chip[1])
    col = t.mixc(chips, col, under)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g = t.math("SUBTRACT", gloss, t.math("MULTIPLY", dirt, gloss * 0.5))
    s = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g, s, t.math("MULTIPLY", chips, -0.3))


def mat_knurl(mat, origin, base, axis, r, n, depth=0.45, **kw):
    """Straight cross-hatch knurling on a cylinder along X with the axis axis = (y, z): two helical
    groove systems (n starts around the circumference, the pitch along the axis is 2 pi r / n,
    diamonds at 45 degrees); no knurling on the ends. On top of the ordinary base material
    ("paint" / "steel").
    """
    outs = (base if callable(base) else kmats.BUILDERS[base])(mat, origin, **kw)
    t = _tree(mat)
    _, sep = t.coords(origin, 0.0)
    nsep = t.normal()
    th = t.math("ARCTAN2", t.math("SUBTRACT", sep.outputs["Z"], axis[1]), t.math("SUBTRACT", sep.outputs["Y"], axis[0]))
    a = t.math("MULTIPLY", th, n / (2 * math.pi))
    xs = t.math("DIVIDE", sep.outputs["X"], 2 * math.pi * r / n)

    def groove(q):
        f = t.math("FRACT", q)
        return t.maprange(t.math("MINIMUM", f, t.math("SUBTRACT", 1.0, f)), 0.0, 0.17, 1.0, 0.0)
    gr = t.math("MAXIMUM", groove(t.math("ADD", xs, a)), groove(t.math("SUBTRACT", xs, a)))
    side = t.maprange(t.math("ABSOLUTE", nsep.outputs["X"]), 0.3, 0.6, 1.0, 0.0)
    gm = t.math("MULTIPLY", gr, side)
    col = t.mixc(t.math("MULTIPLY", gm, 0.55), kmats.sock(mat, outs["color"]), (0.008, 0.008, 0.009, 1))
    hh = t.math("SUBTRACT", _height(t, mat, outs), t.math("MULTIPLY", gm, depth))
    return dict(outs, color=kmats.Tree.ref(col), height=kmats.Tree.ref(hh))


def add_pores(mat, outs, origin, scale=1100.0, dark=0.32, depth=0.5):
    """Polyurethane foam pores: Voronoi cells of ~1 mm, a dark dimple in the middle of a cell."""
    t = _tree(mat)
    tc = t.node("ShaderNodeTexCoord")
    tc.object = origin
    vo = t.node("ShaderNodeTexVoronoi")
    vo.feature = "F1"
    vo.inputs["Scale"].default_value = scale
    t.link(tc.outputs["Object"], vo.inputs["Vector"])
    p = t.maprange(vo.outputs["Distance"], 0.10, 0.32, 1.0, 0.0)
    col = t.mixc(t.math("MULTIPLY", p, dark), kmats.sock(mat, outs["color"]), (0.004, 0.010, 0.026, 1))
    hh = t.math("SUBTRACT", _height(t, mat, outs), t.math("MULTIPLY", p, depth))
    return dict(outs, color=kmats.Tree.ref(col), height=kmats.Tree.ref(hh))


def mat_foam(mat, origin, **kw):
    """Insert foam: plastic without gloss, with pores."""
    return add_pores(mat, kmats.build_plastic(mat, origin, **kw), origin)


def mat_eggcrate(mat, origin, pitch, **kw):
    """Egg-crate foam in the lid: bumps and hollows at a pitch in X and in height (the lid stands almost
    vertical), darker in the hollows; pores on top.
    """
    outs = kmats.build_plastic(mat, origin, **kw)
    t = _tree(mat)
    _, sep = t.coords(origin, 0.0)
    sx = t.math("SINE", t.math("MULTIPLY", sep.outputs["X"], 2 * math.pi / pitch))
    sz = t.math("SINE", t.math("MULTIPLY", sep.outputs["Z"], 2 * math.pi / pitch))
    b = t.math("MULTIPLY", sx, sz)
    col = t.mixc(t.maprange(b, -1.0, 0.3, 0.5, 0.0), kmats.sock(mat, outs["color"]), (0.004, 0.012, 0.03, 1))
    hh = t.math("ADD", _height(t, mat, outs), t.math("MULTIPLY", b, 0.6))
    return add_pores(mat, dict(outs, color=kmats.Tree.ref(col), height=kmats.Tree.ref(hh)), origin)


KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    # black ABS: scuffs lighter on the edges, the number in paint on the face
    "case": (build_coat, dict(color=kmats.lin((30, 30, 32)), under=kmats.lin((84, 84, 86)), seed=3.1, gloss=0.30,
                              spec=0.18, chip=(0.80, 0.86), floor_z=0.0, dust=0.25, grime=0.22,
                              decal_items=[INV_DEC])),
    "latch_pl": (build_coat, dict(color=kmats.lin((24, 24, 26)), under=kmats.lin((80, 80, 82)), seed=8.4, gloss=0.34,
                                  spec=0.2, chip=(0.78, 0.84), floor_z=0.0, dust=0.2, grime=0.3)),
    "foam": (mat_foam, dict(color=kmats.lin((30, 92, 162)), seed=4.2, gloss=0.05, spec=0.03, mottle=0.16,
                            dust=0.12, grime=0.25, scuff=(0.95, 1.0))),
    "foam_lid": (mat_eggcrate, dict(pitch=0.016, color=kmats.lin((28, 86, 150)), seed=4.6, gloss=0.05, spec=0.03,
                                    mottle=0.16, dust=0.15, grime=0.25, scuff=(0.95, 1.0))),
    # black anodizing: worn to aluminium on the edges; the eyecup is rubber
    "anod": (build_coat, dict(ANOD, seed=5.3)),
    "rubber_eye": ("plastic", dict(color=kmats.lin((21, 21, 22)), seed=5.1, gloss=0.14, spec=0.08, mottle=0.08,
                                   dust=0.3, grime=0.3, scuff=(0.85, 0.95))),
    "knurl_eye": (mat_knurl, dict(ANOD, base=build_coat, axis=(SY, SZ), r=FOCUS_R, n=44, seed=5.7)),
    "knurl_light": (mat_knurl, dict(ANOD, base=build_coat, axis=(LY, LZ), r=0.0090, n=36, seed=6.1)),
    "knurl_collar": (mat_knurl, dict(SILVER, base="steel", axis=(LY, LZ), r=0.012, n=44, seed=6.5)),
    "knurl_knob": (mat_knurl, dict(SILVER, base="steel", axis=(MY, MZ), r=0.0065, n=26, seed=6.9)),
    "stainless": ("steel", dict(seed=7.3, tone=0.33, along="x", gloss=0.72, spec=0.85, dust=0.06, grime=0.15)),
    "alu": ("steel", dict(SILVER, seed=7.7)),
    "alu_in": ("flat", dict(color=kmats.lin((52, 52, 54)), gloss=0.45, spec=0.35)),
    "alu_in_on": ("flat", dict(color=kmats.lin((236, 206, 150)), gloss=0.45, spec=0.35)),
    "eyelens": ("flat", dict(color=kmats.lin((22, 28, 38)), gloss=0.92, spec=0.9)),
    "fiber": ("flat", dict(color=kmats.lin((78, 74, 64)), gloss=0.6, spec=0.5)),
    "lens": ("flat", dict(color=kmats.lin((150, 140, 108)), gloss=0.9, spec=0.85)),
    "lens_on": ("flat", dict(color=kmats.lin((255, 238, 196)), gloss=0.9, spec=0.85)),
    "bulb": ("flat", dict(color=kmats.lin((176, 170, 150)), gloss=0.9, spec=0.8)),
    "bulb_on": ("flat", dict(color=kmats.lin((255, 244, 214)), gloss=0.9, spec=0.8)),
    "battery": (build_coat, dict(color=kmats.lin((44, 74, 50)), under=kmats.lin((150, 152, 148)), seed=8.1,
                                 gloss=0.5, spec=0.4, chip=(0.84, 0.90), floor_z=0.0, dust=0.1, grime=0.15)),
    "battery_top": (build_coat, dict(color=kmats.lin((126, 128, 130)), under=kmats.lin((170, 170, 168)), seed=8.3,
                                     gloss=0.55, spec=0.5, chip=(0.88, 0.94), floor_z=0.0, dust=0.1, grime=0.15)),
    "hinge": ("steel", dict(seed=8.7, tone=0.30, along="x", gloss=0.45, spec=0.55, dust=0.15, grime=0.45)),
    "lead": ("plastic", dict(color=kmats.lin((116, 118, 120)), seed=8.9, gloss=0.25, spec=0.2, mottle=0.22,
                             dust=0.2, grime=0.35, scuff=(0.7, 0.8))),
    "wire": ("steel", dict(seed=9.3, tone=0.32, along="x", gloss=0.5, spec=0.5, dust=0.1, grime=0.3)),
    "card": ("paint", dict(LIT, color=PAPER, under=PAPER, seed=9.7, gloss=0.55, spec=0.35, dust=0.05, grime=0.1,
                           decal_items=[CARD_DEC])),
    "pack": ("paint", dict(LIT, color=kmats.lin((146, 168, 190)), under=PAPER, seed=10.1, gloss=0.7, spec=0.5,
                           dust=0.05, grime=0.1, decal_items=[PACK_DEC])),
    "strap": ("plastic", dict(color=kmats.lin((26, 26, 28)), seed=10.5, gloss=0.12, spec=0.06, mottle=0.1,
                              dust=0.2, grime=0.2, scuff=(0.85, 0.95))),
    "dark": ("flat", dict(color=kmats.lin((10, 10, 12)), gloss=0.3, spec=0.2)),
})

# vanilla DayZ pen under the lid strap: lies on its side (the pen's X axis along the foam normal,
# 7 mm), clip up on the open lid; LODs - near and mid
PEN = kv.put("pen", lid_point(PEN_X, PEN_Y, ZF), up=lid_vec((0, -1, 0)), fwd=lid_vec((1, 0, 0)),
             normal=lid_vec((0, 0, -1)), lods=(0, 1))
DECOR = [PEN]

OBJ, NAME = "m82_borescope", "ozr_borescope"
SEL_LAMP = "ozl_lamp_work"
ON = dict(remap={"lens": "lens_on", "bulb": "bulb_on", "alu_in": "alu_in_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL_LAMP,), hidden=(SEL_LAMP,), states={"on": ON}, decor=DECOR)
P = M.part
BOUNDS = {}
AX = {"x": (1.0, 0.0, 0.0), "y": (0.0, 1.0, 0.0), "z": (0.0, 0.0, 1.0)}


# =============================================================================
# Primitives missing from kgeo
# =============================================================================
def use(part, region):
    return part.use(region, *M.regions[region])


def face(part, verts, want):
    """A face from bmesh vertices, turned toward `want`."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def revolve(part, prof, sides, center, axis="x", phase=0.5):
    """Solid of revolution by the profile prof [(h, r, region)] along the axis `axis` ("x"/"y"/"z" or a
    vector) from the point center: the region of a point is that of the segment up to the next one;
    r = 0 is a pole. The material is to the right of the traversal in the (h, r) plane: the segment
    normal is (-dr, dh).
    """
    A = Vector(AX[axis]) if isinstance(axis, str) else Vector(axis).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(A.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    U = A.cross(ref).normalized()
    V = A.cross(U)
    c = Vector(center)
    bm = part.bm

    def ring_dir(k):
        a = 2 * math.pi * k / sides
        return U * math.cos(a) + V * math.sin(a)
    rings = []
    for h, r, _ in prof:
        if r < 1e-7:
            rings.append([bm.verts.new(c + A * h)])
        else:
            rings.append([bm.verts.new(c + A * h + ring_dir(k + phase) * r) for k in range(sides)])
    for i in range(len(prof) - 1):
        (h0, r0, reg), (h1, r1, _) = prof[i], prof[i + 1]
        use(part, reg)
        nh, nr = -(r1 - r0), (h1 - h0)
        R0, R1 = rings[i], rings[i + 1]
        new = []
        for k in range(sides):
            j = (k + 1) % sides
            want = A * nh + ring_dir(k + phase + 0.5) * nr
            if len(R0) == 1:
                vs = [R0[0], R1[j], R1[k]]
            elif len(R1) == 1:
                vs = [R0[k], R0[j], R1[0]]
            else:
                vs = [R0[k], R0[j], R1[j], R1[k]]
            new.append(face(part, vs, want))
        part.tag(new)
    bm.normal_update()
    return part


def wire(part, pts, r, sides):
    """Round wire along a polyline with a transported section frame (no twists for any path direction),
    with end caps.
    """
    bm = part.bm
    pts = [Vector(p) for p in pts]
    n = len(pts)
    tans = []
    for i in range(n):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == n - 1:
            t = pts[-1] - pts[-2]
        else:
            t = (pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized()
        tans.append(t.normalized())
    ref = Vector((0.0, 0.0, 1.0)) if abs(tans[0].z) < 0.9 else Vector((1.0, 0.0, 0.0))
    a = (ref - tans[0] * ref.dot(tans[0])).normalized()
    rings = []
    for i in range(n):
        t = tans[i]
        a = (a - t * a.dot(t)).normalized()
        b = t.cross(a)
        rings.append([bm.verts.new(pts[i] + (a * math.cos(2 * math.pi * k / sides) +
                                             b * math.sin(2 * math.pi * k / sides)) * r) for k in range(sides)])
    new = [bm.faces.new(rings[0][::-1]), bm.faces.new(rings[-1])]
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            new.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def rrect(x0, x1, y0, y1, r, seg):
    """Rectangle with rounded corners (counter-clockwise), seg segments per corner."""
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(seg + 1):
            a = math.radians(a0 + 90.0 * i / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def plan(d, seg):
    """Case outline in plan, sunk by d from the bounds."""
    return rrect(-HX + d, HX - d, YB - HY + d, YB + HY - d, max(RC - d, 0.0005), seg)


def slab(part, prof, seg):
    """Box with plan-rounded corners by profile [(z, sink)]: rings of the plan() outline, the bottom and
    top are caps.
    """
    bm = part.bm
    rings = [[bm.verts.new((x, y, z)) for x, y in plan(d, seg)] for z, d in prof]
    faces = [bm.faces.new(rings[0][::-1]), bm.faces.new(rings[-1])]
    n = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            faces.append(bm.faces.new([a[i], a[j], b[j], b[i]]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return part.tag(faces)


def boxp(name, region, x0, x1, y0, y1, z0, z1, **kw):
    p = P(name, region)
    g.box(p, x0, x1, y0, y1, z0, z1, **kw)
    return p


def rbox(name, region, x0, x1, y0, y1, z0, z1, r, seg):
    """A tile with plan-rounded corners (card, pack)."""
    p = P(name, region)
    g.prism(p, rrect(x0, x1, y0, y1, r, seg), (0, 1), z0, z1)
    return p


def rotate_lid(parts):
    c = Vector((0.0, HINGE[0], HINGE[1]))
    for p in parts:
        bmesh.ops.rotate(p.bm, verts=p.bm.verts[:], cent=c, matrix=lid_rot())
        p.bm.normal_update()
    return parts


def disc(part, center, normal, r, n):
    """A flat disc (one n-gon face) facing along normal - a rivet, an end."""
    c, nv = Vector(center), Vector(normal).normalized()
    a = nv.cross(Vector((0, 0, 1)) if abs(nv.z) < 0.9 else Vector((1, 0, 0))).normalized()
    b = nv.cross(a)
    vs = [part.bm.verts.new(c + (a * math.cos(2 * math.pi * i / n) + b * math.sin(2 * math.pi * i / n)) * r)
          for i in range(n)]
    f = part.bm.faces.new(vs)
    f.normal_update()
    if f.normal.dot(nv) < 0:
        f.normal_flip()
    return part.tag([f])


# --- case -------------------------------------------------------------------------------------
def shell(name, prof, open_up, seg):
    """A case half: a rounded box by profile minus the cavity (wall WALL)."""
    outer = P(name, "case")
    slab(outer, prof, seg)
    cut = P(name + "_cut", "case_in")
    z0, z1 = prof[0][0], prof[-1][0]
    if open_up:
        g.prism(cut, plan(CAV, seg), (0, 1), z0 + WALL, z1 + 0.01)
    else:
        g.prism(cut, plan(CAV, seg), (0, 1), z0 - 0.01, z1 - WALL)
    return M.boolean(name, outer, [cut])


def build_handle(lod):
    """Handle on the face, lowered: two bosses on the wall under the band and an arc - thin arms, a thick
    grip in the middle (elliptical section).
    """
    hm = P("handle_mounts", "case")
    for s in (-1, 1):
        prof = ([(0.0, 0.0065, "case"), (0.0063, 0.0065, "case"), (0.0072, 0.0056, "case"), (0.0072, 0.0, None)]
                if lod == 0 else [(0.0, 0.0065, "case"), (0.0072, 0.0065, "case"), (0.0072, 0.0, None)])
        revolve(hm, prof, 12 if lod == 0 else 6, (s * HANDLE_X, YW + 0.0005, HANDLE_Z), (0, -1, 0))
    hd = P("handle", "black")
    ya, yg = YW - 0.0035, YW - 0.0046
    # (x, y, z, thickness from the wall, width in the arc plane)
    left = [(-0.0470, ya, HANDLE_Z, 0.0022, 0.0034), (-0.0457, ya, 0.0150, 0.0022, 0.0034),
            (-0.0446, ya - 0.0004, 0.0108, 0.0023, 0.0035), (-0.0428, yg + 0.0003, 0.0078, 0.0030, 0.0040),
            (-0.0395, yg, 0.0063, 0.0037, 0.0044), (-0.0300, yg, 0.0058, 0.0042, 0.0046)]
    if lod > 0:
        left = [left[0], left[2], left[4]]
    pts = left + [(-x, y, z, a, b) for x, y, z, a, b in reversed(left)]
    g.tube_var(hd, [q[:3] for q in pts], [q[3:] for q in pts], 10 if lod == 0 else 6)
    return [hm, hd]


def latch_frame(x):
    """Latch lever flipped down and lying on the wall: the axle at the band, the bottom at the wall."""
    p = Vector((x, YW - 0.0030, 0.0262))
    v = (Vector((x, YW - 0.0016, 0.0060)) - p).normalized()
    return g.Frame(p, (1, 0, 0), v, v.cross(Vector((1, 0, 0))))


def build_latches(lod):
    """Latches flipped open: a plastic lever with a thumb stop on a steel axle in two lugs, a wire bail
    lies on the lever; the mating hooks are on the lid band (in the lid list).
    """
    lv = P("latch_levers", "latch_pl")
    pn = P("latch_pins", "steel")
    lg = P("latch_lugs", "case")
    bl = P("latch_bails", "wire")
    ck = P("latch_catches", "latch_pl")
    for s in (-1, 1):
        x = s * LATCH_X
        fr = latch_frame(x)
        if lod == 0:
            g.box(lv, -0.0085, 0.0085, -0.0015, 0.0205, -0.0012, 0.0012, r=0.0006, seg=1, frame=fr)
            g.box(lv, -0.0080, 0.0080, 0.0185, 0.0212, 0.0010, 0.0034, frame=fr)
            g.cyl(pn, tuple(fr.o), "x", 0.0013, 0.0210, 6)
            for q in (-1, 1):
                a0, a1 = sorted((q * 0.0090, q * 0.0108))
                g.box(lg, x + a0, x + a1, YW - 0.0046, YW + 0.0005, 0.0238, 0.0286)
            path = [(-0.0068, 0.0005), (-0.0068, 0.0115), (-0.0045, 0.0148), (0.0045, 0.0148),
                    (0.0068, 0.0115), (0.0068, 0.0005)]
            wire(bl, [fr.p(a, b, 0.0024) for a, b in path], 0.0008, 4)
            g.box(ck, x - 0.0075, x + 0.0075, YF - 0.0040, YF + 0.0005, BASE_H + 0.0015, BASE_H + 0.0082,
                  r=0.0006, seg=1)
        else:
            g.box(lv, -0.0085, 0.0085, -0.0015, 0.0205, -0.0012, 0.0012, frame=fr)
            g.box(ck, x - 0.0075, x + 0.0075, YF - 0.0040, YF + 0.0005, BASE_H + 0.0015, BASE_H + 0.0082)
    base = [lv] + ([pn, lg, bl] if lod == 0 else [])
    return base, [ck]


def build_hinge(lod):
    """Piano hinge at the back: five knuckles on an axle (the end ones and the middle one belong to the
    base, two to the lid), straps on the bands of both halves on rivets.
    """
    kb = P("hinge_base", "hinge")
    kl = P("hinge_lid", "hinge")
    c = (0.0, HINGE[0], HINGE[1])
    x0, x1, gap, n, r = -0.090, 0.090, 0.001, 5, 0.0032
    if lod > 0:
        revolve(kb, [(x0, 0.0, "hinge"), (x0, r, "hinge"), (x1, r, "hinge"), (x1, 0.0, None)], 6, c)
        return [kb], []
    L = (x1 - x0 - (n - 1) * gap) / n
    for i in range(n):
        a = x0 + i * (L + gap)
        prof = [(a, r, "hinge"), (a + L, r, "hinge")]
        if i == 0:
            prof = [(a, 0.0, "hinge")] + prof
        if i == n - 1:
            prof = prof + [(a + L, 0.0, None)]
        revolve(kb if i % 2 == 0 else kl, prof, 10, c)
    yb = YB + HY
    for part, z0, z1 in ((kb, BASE_H - 0.0066, BASE_H - 0.0020), (kl, BASE_H + 0.0020, BASE_H + 0.0066)):
        use(part, "hinge")
        g.box(part, x0, x1, yb - 0.0002, yb + 0.0012, z0, z1)
        for xr in (-0.060, 0.0, 0.060):
            disc(part, (xr, yb + 0.0013, (z0 + z1) / 2), (0, 1, 0), 0.0013, 6)
    return [kb], [kl]


def build_lid_inside(lod, seg):
    """Lid foam, the card and the swab pack under the strap (with the lid closed)."""
    out = [boxp_poly("lid_foam", "foam_lid", ZF, ZF + LF - 0.0004, min(seg, 2))]
    if lod == 0:
        out.append(rbox("card", "card", CARD[0], CARD[1], CARD[2], CARD[3], ZF - 0.0008, ZF, 0.003, 2))
        pk = rbox("swabs", "pack", PACK[0], PACK[1], PACK[2], PACK[3], ZF - PACK_T, ZF, 0.002, 1)
        g.box(pk, PACK[1] - 0.001, PACK[1] + 0.0025, PACK[2] + 0.001, PACK[3] - 0.001, ZF - 0.0006, ZF)  # pack seam
        out.append(pk)
    else:
        out.append(boxp("card", "card", CARD[0], CARD[1], CARD[2], CARD[3], ZF - 0.0008, ZF))
        out.append(boxp("swabs", "pack", PACK[0], PACK[1], PACK[2], PACK[3], ZF - PACK_T, ZF))
    st = P("strap", "strap")
    xi = XI - 0.0005
    zs = [(-xi, ZF + 0.0004), (CARD[0] - 0.002, ZF - 0.0015), (PACK[0] - 0.003, ZF - 0.0016),
          (PACK[0] + 0.002, ZF - PACK_T - 0.0007), (PACK[1] - 0.002, ZF - PACK_T - 0.0007),
          (PEN_X - 0.0050, ZF - PEN_H - 0.0008), (PEN_X + 0.0045, ZF - PEN_H - 0.0008), (xi, ZF + 0.0004)]
    if lod > 0:
        zs = [zs[0], zs[3], zs[4], zs[-1]]
    g.sweep(st, [(x, STRAP_Y, z) for x, z in zs], (0, 1, 0), STRAP_T / 2, STRAP_W / 2)
    if lod == 0:
        use(st, "steel")
        for s in (-1, 1):       # strap rivets on the side walls
            disc(st, (s * (XI - 0.0003), STRAP_Y, ZF - 0.0012), (-s, 0, 0), 0.0018, 6)
    out.append(st)
    return out


def build_case(spec):
    lod, seg = spec["lod"], spec["seg"]
    parts = [shell("base", BASE_PROF if lod == 0 else BASE_LO, True, seg)]
    lid = [shell("lid", LID_PROF if lod == 0 else LID_LO, False, seg)]
    parts += build_handle(lod)
    lb, ll = build_latches(lod)
    hb, hl = build_hinge(lod)
    parts += lb + hb
    lid += ll + hl + build_lid_inside(lod, seg)
    if lod == 0:
        # outside on the lid - a cast raised pad (as on ABS cases), 0.8 mm
        lid.append(rbox("lid_panel", "case", -HX + 0.0115, HX - 0.0115, YB - HY + 0.0115, YB + HY - 0.0115,
                        _ZT - 0.0005, _ZT + 0.0008, RC - 0.006, 2))
    return parts + rotate_lid(lid)


def boxp_poly(name, region, z0, z1, seg, inset=CAV + 0.0005):
    p = P(name, region)
    g.prism(p, plan(inset, seg), (0, 1), z0, z1)
    return p


# --- foam insert ---------------------------------------------------------------------------
def pocket_boxes():
    """Cut-outs in the foam shaped like the instruments: (x0, x1, y0, y1, bottom, segments per corner)."""
    m = 0.0012
    bx0, bx1 = min(BAT_X) - BAT_R - m, max(BAT_X) + BAT_R + m
    return [
        (-0.1012 - m, -0.0210, SY - 0.0161 - m, SY + 0.0161 + m, SZ - 0.0161, 2),    # eyepiece and body
        (-0.0220, 0.0998 + m, SY - 0.0045, SY + 0.0045, SZ - 0.0045, 1),             # probe
        (POST_X - 0.0055, POST_X + 0.0055, SY - POST_END - m, SY - 0.009, SZ - 0.0052, 1),  # light-guide fitting
        (0.0435, LENS_END + m, LY - 0.0120 - m, LY + 0.0120 + m, LZ - 0.0120, 2),    # sleeve and nose
        (-0.0640 - m, 0.0450, LY - 0.0098 - m, LY + 0.0098 + m, LZ - 0.0098, 2),     # flashlight body
        (-0.0312 - m, -0.0195, MY - 0.0065 - m, MY + 0.0065 + m, MZ - 0.0065, 1),    # tube head
        (-0.0200, 0.0985 + m, MY - 0.0040 - m, MY + 0.0040 + m, MZ - 0.0040, 1),     # tube
        (bx0, bx1, BAT_Y - BAT_HALF - m, BAT_Y + BAT_HALF + m, BAT_Z - BAT_R, 2),     # batteries
        # finger notches
        (-0.085, -0.073, SY + 0.015, SY + 0.0245, SZ - 0.0160, 1),
        (-0.012, 0.002, LY + 0.009, LY + 0.0175, LZ - 0.0098, 1),
    ]


def build_foam(spec):
    lod, seg = spec["lod"], spec["seg"]
    foam = boxp_poly("foam", "foam", WALL, FOAM_Z, min(seg, 2))
    if lod > 0:
        return [foam]
    cuts = []
    for x0, x1, y0, y1, z, s in pocket_boxes():
        c = P("pocket", "foam_cut")
        rr = min(0.0025, (x1 - x0) / 2 - 1e-4, (y1 - y0) / 2 - 1e-4)
        g.prism(c, rrect(x0, x1, y0, y1, rr, s), (0, 1), z, FOAM_Z + 0.01)
        cuts.append(c)
    return [M.boolean("foam", foam, cuts)]


# --- contents ----------------------------------------------------------------------------------
def build_scope(spec):
    lod, n = spec["lod"], spec["sides"]
    sc = P("scope", "anod")
    revolve(sc, SCOPE if lod == 0 else SCOPE_LO, n, (0.0, SY, SZ))
    pr = P("probe", "stainless")
    revolve(pr, PROBE if lod == 0 else PROBE_LO, 10 if lod == 0 else 6, (0.0, SY, SZ))
    po = P("light_post", "stainless")
    revolve(po, POST if lod == 0 else POST_LO, 10 if lod == 0 else 6, (POST_X, SY, SZ), (0, -1, 0))
    return [sc, pr, po]


def build_light(spec):
    lod, n = spec["lod"], spec["sides"]
    lt = P("light", "anod")
    revolve(lt, LIGHT if lod == 0 else LIGHT_LO, n, (0.0, LY, LZ))
    ln = P("lamp", "alu_in", group=SEL_LAMP)
    revolve(ln, LAMP if lod == 0 else LAMP_LO, n, (0.0, LY, LZ))
    if lod == 0:
        use(ln, "bulb")
        revolve(ln, BULB, 8, (0.0, LY, LZ))
    return [lt, ln]


def build_mirror(spec):
    lod = spec["lod"]
    mt = P("mirror", "stainless")
    revolve(mt, MIRROR if lod == 0 else MIRROR_LO, 10 if lod == 0 else 6, (0.0, MY, MZ))
    # mirror window on top near the tube end
    wn = P("mirror_window", "dark")
    x1 = MIRROR[-3][0] - 0.0015
    r = 0.0040
    g.quad(wn, [(x1 - 0.008, MY - 0.0022, MZ + r + 0.0002), (x1, MY - 0.0022, MZ + r + 0.0002),
                (x1, MY + 0.0022, MZ + r + 0.0002), (x1 - 0.008, MY + 0.0022, MZ + r + 0.0002)])
    return [mt, wn]


def build_batteries(spec):
    lod = spec["lod"]
    bt = P("batteries", "battery")
    for i, x in enumerate(BAT_X):
        sg = 1 if i == 0 else -1
        revolve(bt, BAT if lod == 0 else BAT_LO, 12 if lod == 0 else 6, (x, BAT_Y, BAT_Z), (0, sg, 0))
    return [bt]


def build_seal(spec):
    if spec["lod"] > 0:
        return []
    x, y, r, h = SEAL
    sl = P("seal", "lead")
    revolve(sl, SEAL_PROF, 10, (x, y, FOAM_Z), "z")
    wr = P("seal_wire", "wire")
    zw = FOAM_Z + 0.0007
    loop = [(x + r - 0.001, y - 0.0008, zw)]
    cx, cy, rr = x + r + 0.009, y + 0.001, 0.0075
    for i in range(11):
        a = math.radians(200 - 300 * i / 10)
        loop.append((cx + rr * math.cos(a), cy + rr * math.sin(a), zw))
    loop.append((x + r - 0.001, y + 0.0008, zw))
    wire(wr, loop, 0.0006, 4)
    # wire tails from the other side of the seal - two cores twisted into a strand
    a, b = Vector((x - r + 0.001, y, FOAM_Z + 0.0012)), Vector((x - r - 0.011, y - 0.0025, FOAM_Z + 0.0012))
    d = (b - a).normalized()
    side = d.cross(Vector((0, 0, 1))).normalized()
    for ph in (0.0, math.pi):
        pts = []
        for k in range(5):
            q = k / 4
            th = ph + q * 3 * math.pi
            off = (side * math.cos(th) + Vector((0, 0, 1)) * math.sin(th)) * 0.0006 * (0.3 + 0.7 * min(1.0, q * 3))
            pts.append(a + (b - a) * q + off)
        wire(wr, pts, 0.00055, 4)
    return [sl, wr]


def check_pen():
    """The pen lies on the lid foam (the bottom of its bounds on the face), not above the strap and clear
    of the wall and the pack: a printout for --stats.
    """
    path, o, up, fwd = PEN[:4]
    cs = kv.corners("pen", o, up, fwd)
    nrm = Vector(lid_vec((0, 0, -1)))
    plane = Vector(lid_point(PEN_X, PEN_Y, ZF))
    inv = lid_rot().inverted()
    c0 = Vector((0.0, HINGE[0], HINGE[1]))
    loc = [c0 + inv @ (Vector(q) - c0) for q in cs]
    h = [nrm.dot(Vector(q) - plane) for q in cs]
    print("pen: height over foam %.4f..%.4f, closed x %.4f..%.4f, y %.4f..%.4f (wall x %.4f, pack x1 %.4f, y %.4f..%.4f)"
          % (min(h), max(h), min(v.x for v in loc), max(v.x for v in loc), min(v.y for v in loc),
             max(v.y for v in loc), XI, PACK[1] + 0.0025, YB - HY + CAV, YB + HY - CAV))


def build_lod(spec):
    parts = (build_case(spec) + build_foam(spec) + build_scope(spec) + build_light(spec) + build_mirror(spec) +
             build_batteries(spec) + build_seal(spec))
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("bounds lo %s hi %s" % (tuple(round(c, 4) for c in BOUNDS["lo"]),
                                      tuple(round(c, 4) for c in BOUNDS["hi"])))
        check_pen()
    return parts


def collision():
    """One convex hull: the base and the opened lid. Mass is the item's weight in the mod, 0.8 kg; the
    hit sound is plastic.
    """
    pts = [(x, y, z) for x in (-HX, HX) for y in (YF - 0.007, YB + HY) for z in (0.0, BASE_H)]
    pts += [lid_point(x, y, z) for x in (-HX, HX) for y in (YB - HY, YB + HY) for z in (BASE_H, BASE_H + LID_H)]
    comps = [(pts, kx.PEN + r"\plastic.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    memory = {
        # inventory preview camera: front-left and from above (invView = camera position)
        "invView": [(-0.24, -0.46, 0.38)],
        "ce_center": [(0.0, 0.0, 0.08)],
        "ce_radius": [(0.14, 0.0, 0.08)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


# angles: the first is the illuminator (the work look in the preview shows only it, the socket looks
# to +X), then the overall view, the interior, a close-up of the eyepiece (the --look preview takes
# the first four)
SHOTS = [
    ("light", (0.28, -0.20, 0.30), (0.075, LY, 0.028), 60),
    ("front", (-0.20, -0.50, 0.36), (0.0, 0.0, 0.07), 40),
    ("inside", (0.02, -0.30, 0.34), (0.0, YB, 0.03), 45),
    ("scope", (-0.20, -0.24, 0.20), (-0.060, SY - 0.012, 0.030), 55),
    ("lid", (0.06, -0.42, 0.14), (0.0, 0.05, 0.10), 45),
    ("top", (0.0, -0.06, 0.55), (0.0, 0.0, 0.03), 40),
    ("back", (0.22, 0.46, 0.30), (0.0, 0.03, 0.07), 40),
]
M.look_shots = (4, 1)

M.run(build_lod, collision, SHOTS, row_step=0.32, row_shot=((0.16, -1.1, 0.35), (0.16, 0, 0.08)))
