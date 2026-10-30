"""M77 - lead capsule (OZL_Tool_LeadCapsule): a Khabar line module, a portable 2x2 item. It sits in the
OZL_Tool3 slot of the packer (M13 - rear left, M18 - right) and shows there through the module_3
proxy. A rectangular lead case with a hinged lid.

    blender --background --python build_m77.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py (system Python) before the first build: the stencilled sign, the nameplate, the tag.

Layout: the module pad is about 0.2 x 0.2 m, up to about 0.25 m high, flat bottom.
- Body casting 176 x 136 x 82 mm, walls and floor 20 mm (as in boxes for gamma sources - thicker
  than in boxes for beta vials), nest 136 x 96 x 62 mm. Lid casting 176 x 136 x 26 mm with a
  132 x 92 x 8 mm plug going into the nest (a labyrinth: the gap under the lid does not shine through).
- The cage is welded from 2 mm strip and angle: a tray with a 22 mm rim and a floor, an upper band
  18 mm, four corner angles 18 mm, a lid band 12 mm along the lower edge. The strip is bent round
  the corners (outer radius 6 mm), the angles have the same rounded back; lead shows between them,
  at the ends and on the lid top.
- Two hinges: on the rear band a leaf with a rounded end and a hinge on an axle with heads; on the
  lid a strap bent over the rounded casting edge, riveted. At the front a toggle latch: a base with
  lugs and axle, a lever of bent channel with a bent-out tongue, a wire bail on the hook of the lid
  band. Handles on the sides: drop-down trapezoid bails of diameter 7 in eyes with a round lug.
- Real lead mass would be about 21.5 kg (23 kg with the cage); the in-game weight is 800 g of the
  OZL_Tool_Base class (module rules untouched), the mass in Geometry is the same.
- Size 0.180 x 0.140 x 0.116 m without handles and hinges; with the side handles, rear hinges and
  front latch 0.203 x 0.156 x 0.113 m (measured by --stats).

The lid is closed at rest: the same line has an open box on the same stations already (M75
dosimeter: lid open, a lead sheet with a sign inside it), an open case would repeat it.
Work look (a pose, like the head feed of M16): while the machine works the latch is flipped open
(lever 150 degrees down, the bail leaves the hook) and the lid rises on the hinges by 35 degrees,
showing the lead nest and the lid plug; after work the lid closes and the latch snaps shut. Bones
ozl_latch and ozl_lid share one source, ozl_lid (OZL_WorkFx pose, 1.2 s): the lever takes the first
40 % of the travel, the lid 30 % to the end. That is why the nest and the underside of the lid are
modelled (not visible at rest). In the preview the pose is the "work" state (--look only: there is
no work atlas, the textures are the same).

Condition (modules have no faction colour): used but intact, worn paint on the edges - cage enamel
chipped to steel on the edges and handles, rust at the chips; dull lead with a white oxide bloom,
scratches, dents; hinges and latch of tarnished zinc plating. Markings differ from M71 and M75: a
trefoil stencilled straight onto the lead, yellow with black (on the lid and the front), a blank
aluminium nameplate on rivets, an aluminium inventory tag with a punched number on the handle -
digits only.
No vanilla DayZ props are attached: the module itself stands on the slot proxy's station, nested
proxies are unverified, and modules get no props.
LODs: near and mid (cage and lid corners chamfered, no rivets, tag, latch bail and axle heads;
handles and hinges coarser), no far one. Round parts have at least 10 sides: kexport smooths edges
up to 40 degrees, and 8 sides (45) would show facets.

Blender axes: X is width, Y is depth (the front faces -Y, the lid hinges are at the back), Z is up.
The origin is the centre of the bottom, so the module lands on the module_N proxy point
(autocenter = 0 in Geometry).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import bmesh  # noqa: E402
import bpy  # noqa: E402
import kbake  # noqa: E402
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import krender  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m -----------------------------------------------------------------------------
LW, LD = 0.176, 0.136                # casting footprint (body and lid)
T = 0.002                            # strip and angle of the cage
FX, FY = LW / 2 + T, LD / 2 + T      # outer faces of the cage: 0.090 / 0.070
R_OUT = 0.006                        # outer bend radius of the strip at the corners (inner 4 mm)
Z_L0, ZB = 0.002, 0.084              # bottom and top of the body casting (the tray floor is under it)
TRAY_Z = 0.022                       # tray rim height
BAND = (0.066, ZB)                   # upper band
ANG = 0.018                          # angle flange
ZL0 = ZB + 0.0005                    # the lid rests on the body (the gap is a dark line)
ZL1 = ZL0 + 0.026
LID_BAND = 0.012                     # lid band: narrow, along the lower edge, so the lead ends show
LID_R = 0.003                        # rounding of the lid casting's top edge
NEST = (0.068, 0.048, ZB - 0.062)    # nest 136 x 96 x 62: half-width, half-depth, floor
PLUG = (0.066, 0.046, 0.008)         # lid plug 132 x 92 x 8
STRAP_X, STRAP_W, STRAP_T = 0.052, 0.016, 0.0015
HY, HZ, HR = FY + 0.004, ZL0, 0.004  # hinge axis
# side handles: drop-down trapezoid bails of diameter 7 in eyes of the upper band, hanging down
H_R, H_X = 0.0035, FX + 0.0055
H_PIV, H_TOP, H_BOT, H_LEG = 0.036, 0.074, 0.040, 0.024
EYE_R = 0.0055                       # eye lug around the handle axis
# latch: base on the body band, lever axis, hook on the lid band
LATCH_Y, LATCH_PIV = -FY - 0.0035, 0.0690
HOOK_Z = ZL0 + 0.0035                # hook shelf (mid-thickness)

LOD_SPECS = [
    dict(lod=0, seg=3, fil=3, rod=10, knuckle=10, fine=True),
    dict(lod=1, seg=1, fil=1, rod=6, knuckle=6, fine=False),
]

REGIONS = {
    "lead": ("lead", 1.0), "lead_lid": ("lead_lid", 1.2),
    "lead_in": ("lead_in", 0.5), "lead_lid_in": ("lead_lid_in", 0.5),
    "enamel": ("enamel", 0.8), "enamel_lid": ("enamel_lid", 0.8), "handle": ("handle", 1.0),
    "zinc": ("zinc", 1.2), "plate": ("plate", 2.2), "tag": ("tag", 2.2),
}


def wdecal(name):
    return os.path.join(WORK, name)


# decals: (image, normal axis, sign, (u axis, v axis), centre (u, v), size (w, h; the sign is the
# direction, so that the image reads from outside), range along the normal)
TREFOIL_FRONT = (wdecal("decal_trefoil.png"), "y", -1, ("x", "z"), (-0.042, 0.044), (0.034, 0.034),
                 (-LD / 2 - 0.004, -LD / 2 + 0.004))
TREFOIL_LID = (wdecal("decal_trefoil.png"), "z", 1, ("x", "y"), (0.0, -0.006), (0.044, 0.044),
               (ZL1 - 0.004, ZL1 + 0.004))
PLATE_C, PLATE_S = (0.044, 0.044), (0.040, 0.022)
PLATE_DECAL = (wdecal("decal_plate.png"), "y", -1, ("x", "z"), PLATE_C, PLATE_S, None)
TAG_C, TAG_S = (0.010, 0.0205), (0.016, 0.030)     # (y, z) of the tag centre, (width, height)
TAG_DECAL = (wdecal("decal_tag.png"), "x", -1, ("z", "y"), (TAG_C[1], TAG_C[0]), (-TAG_S[1], -TAG_S[0]), None)

# --- materials ----------------------------------------------------------------------------------
LEAD = kmats.lin((96, 99, 105))          # same lead as the M48 sample and the M71 shield - one lead throughout
LEAD_DARK = kmats.lin((70, 73, 79))
OXIDE = kmats.lin((176, 178, 172))       # whitish bloom
BRIGHT = kmats.lin((158, 162, 170))      # fresh cut in a scratch
POLISH = kmats.lin((126, 130, 138))      # rubbed by hands


def rotated(t, vec, euler):
    m = t.node("ShaderNodeMapping")
    m.inputs["Rotation"].default_value = euler
    t.link(vec, m.inputs["Vector"])
    return m.outputs[0]


def scratches(t, vec, nsep, amount=1.0):
    """Short straight scratches (as on M71): contours of stretched noise masked into 2-3 cm segments;
    the X, Y and Z families are suppressed on faces perpendicular to their direction.
    """
    out = None
    fams = [((0.03, 1.0, 1.0), 0, None, 2.2, 3.4), ((1.0, 0.03, 1.0), 1, None, 2.4, 3.9),
            ((1.0, 1.0, 0.03), 2, None, 2.0, 3.1), ((0.03, 1.0, 1.0), None, (0.62, 0.45, 0.80), 2.6, 4.4)]
    for st, ax, rot, sc, ms in fams:
        v = rotated(t, vec, rot) if rot else vec
        n = t.noise(t.stretch(v, *st), sc, 2.0, 0.5)
        line = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", n, 0.5)), 0.0, 0.007, 1.0, 0.0)
        mask = t.maprange(t.noise(v, ms, 3.0, 0.5), 0.60, 0.70, 0.0, 1.0)
        s = t.math("MULTIPLY", line, mask)
        if ax is not None:
            s = t.math("MULTIPLY", s, t.maprange(t.math("ABSOLUTE", nsep.outputs[ax]), 0.4, 0.8, 1.0, 0.0))
        out = s if out is None else t.math("MAXIMUM", out, s)
    return t.math("MULTIPLY", out, amount)


def dents(t, vec, scale, amount):
    """Dents: Voronoi cells, a bowl in the rare cells."""
    vor = t.node("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = scale
    t.link(vec, vor.inputs["Vector"])
    bowl = t.maprange(vor.outputs["Distance"], 0.05, 0.38, 1.0, 0.0)
    pick = t.math("GREATER_THAN", t.bw(vor.outputs["Color"]), 1.0 - amount)
    return t.math("MULTIPLY", t.math("MULTIPLY", bowl, bowl), pick)


def mat_lead(mat, origin, seed=1.0, tone=1.0, scratch=1.0, decal_items=(), z0=0.0, oxide=1.0, dust=0.30):
    """Cast lead: dull grey-blue, patches and specks of white oxide (denser toward the bottom), scratches
    down to bright metal, dents, rubbed edges, dirt in the corners. The stencil lies over the oxide and
    under the scratches; paint holds badly on lead - it is worn in patches, and the lead shines like
    lead, not like enamel. The dayz look: kmats.dayz_layers (mute, tone patches, streaks, grease spots),
    as in the kit builders via weather().
    """
    t = kmats.Tree(mat)
    vec0, sep = t.coords(origin, seed)
    vec = t.stretch(vec0, 10.0, 10.0, 10.0)
    nsep = t.normal()
    base = tuple(min(1.0, c * tone) for c in LEAD[:3]) + (1,)
    dark = tuple(min(1.0, c * tone) for c in LEAD_DARK[:3]) + (1,)
    col = t.mixc(t.maprange(t.noise(vec, 1.2, 6.0, 0.6), 0.3, 0.75, 0.0, 1.0), dark, base)
    blot = t.maprange(t.noise(vec, 0.9, 6.0, 0.6), 0.52, 0.76, 0.0, 1.0)
    speck = t.maprange(t.noise(vec, 9.0, 4.0, 0.6), 0.62, 0.80, 0.0, 1.0)
    low = t.maprange(sep.outputs["Z"], z0, z0 + 0.05, 0.35, 0.0)
    ox = t.math("ADD", t.math("MULTIPLY", blot, 0.40 * oxide), t.math("MULTIPLY", speck, 0.60 * oxide))
    ox = t.math("MINIMUM", t.math("ADD", ox, t.math("MULTIPLY", low, t.noise(vec, 3.0, 5.0, 0.6))), 0.85)
    col = t.mixc(ox, col, OXIDE)
    paint = None
    for path, ax, sign, (au, av), center, size, rng in decal_items:
        gate = t.facing(nsep, ax.upper(), sign, 0.5)
        w = sep.outputs["XYZ".index(ax.upper())]
        gate = t.math("MULTIPLY", gate, t.math("MULTIPLY", t.math("GREATER_THAN", w, rng[0]),
                                               t.math("LESS_THAN", w, rng[1])))
        c, a = t.image(path, sep.outputs["XYZ".index(au.upper())], sep.outputs["XYZ".index(av.upper())],
                       center, size)
        # stencil worn in patches down to the lead, translucent in places
        wear = t.maprange(t.noise(vec0, 22.0, 5.0, 0.6), 0.38, 0.52, 0.12, 0.92)
        m = t.math("MULTIPLY", t.math("MULTIPLY", a, gate), wear)
        col = t.mixc(m, col, c)
        paint = m if paint is None else t.math("MAXIMUM", paint, m)
    scr = scratches(t, vec, nsep, scratch)
    col = t.mixc(t.math("MULTIPLY", scr, 0.75), col, BRIGHT)
    dn = dents(t, vec, 6.5, 0.22)
    col = t.mixc(t.math("MULTIPLY", dn, 0.35), col, POLISH)
    edge = t.maprange(t.edge_wear(0.0025), 0.05, 0.30, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.55), col, POLISH)
    h = t.math("MULTIPLY", -1.0, t.math("ADD", t.math("MULTIPLY", scr, 0.25), t.math("MULTIPLY", dn, 0.7)))
    cav = t.maprange(t.cavity(0.012), 0.15, 0.6, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.55), col, kmats.GRIME)
    up = t.maprange(nsep.outputs["Z"], 0.4, 0.9, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", up, t.noise(vec, 3.0, 4.0, 0.6)), dust), col, kmats.DUST)
    if kmats.LOOK["name"] == "dayz":
        col, dirt = kmats.dayz_layers(t, col, t.math("MULTIPLY", cav, 0.55), vec0, sep, nsep, 0.5)
        cav = t.math("MAXIMUM", cav, dirt)
    gl = t.math("ADD", 0.18,t.math("SUBTRACT", t.math("ADD", t.math("MULTIPLY", scr, 0.25),
                                                       t.math("MULTIPLY", edge, 0.20)),
                                     t.math("ADD", t.math("MULTIPLY", ox, 0.12), t.math("MULTIPLY", cav, 0.1))))
    sp = t.math("ADD", 0.14, t.math("ADD", t.math("MULTIPLY", scr, 0.3), t.math("MULTIPLY", edge, 0.2)))
    if paint is not None:
        gl = t.mixf(paint, gl, 0.26)
        sp = t.mixf(paint, sp, 0.16)
    return kmats.out(t, col, gl, sp, h)


ENAMEL = dict(color=kmats.lin((86, 88, 89)), under=kmats.lin((118, 116, 110)), gloss=0.30, spec=0.24,
              chip=(0.56, 0.63), rust=(0.60, 0.68), rust_low=0.25, floor_z=0.0, dust=0.30, grime=0.55)
ALU = dict(color=kmats.lin((166, 168, 166)), under=kmats.lin((120, 122, 120)), gloss=0.40, spec=0.40,
           chip=(0.80, 0.86), rust=(0.98, 0.99), rust_low=0.0, floor_z=0.0, dust=0.15, grime=0.35)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    # dayz look: the lead is darker than before (was 0.86 / 0.80) - beside vanilla samples the lid
    # top
    # came out almost white
    "lead": (mat_lead, dict(seed=1.3, tone=0.74, decal_items=[TREFOIL_FRONT], z0=Z_L0)),
    "lead_lid": (mat_lead, dict(seed=3.7, tone=0.68, scratch=0.8, decal_items=[TREFOIL_LID], z0=ZL0, dust=0.22)),
    # nest and underside of the lid: darker, less oxide, scratches from the lid and the samples
    "lead_in": (mat_lead, dict(seed=2.2, tone=0.70, scratch=0.6, z0=NEST[2] - 0.05, oxide=0.5)),
    "lead_lid_in": (mat_lead, dict(seed=4.4, tone=0.72, scratch=0.5, z0=ZL0 - 0.06, oxide=0.4)),
    # cage: grey enamel over steel, chipped to metal on the edges, rust at the chips
    "enamel": ("paint", dict(ENAMEL, seed=6.4)),
    "enamel_lid": ("paint", dict(ENAMEL, seed=8.9, dust=0.2)),
    # handles: enamel rubbed off to metal by palms
    "handle": ("paint", dict(ENAMEL, seed=7.7, chip=(0.42, 0.50), rust=(0.62, 0.72), grime=0.6)),
    # hinges, latch, rivets: tarnished zinc plating (the dayz look darkens steel by x0.65, so the
    # tone is higher)
    "zinc": ("steel", dict(seed=9.1, tone=0.30, along="z", gloss=0.36, spec=0.40, dust=0.30, grime=0.55)),
    "plate": ("paint", dict(ALU, seed=5.6, decal_items=[PLATE_DECAL])),
    "tag": ("paint", dict(ALU, seed=6.1, decal_items=[TAG_DECAL])),
})

# --- work look: pose (like the M16 head feed) ---------------------------------------------------
SEL_LID, SEL_LATCH = "ozl_lid", "ozl_latch"
LID_DEG, LATCH_DEG = 35.0, 150.0
LID_AXIS = ((-0.060, HY, HZ), (0.060, HY, HZ))
LATCH_AXIS = ((-0.012, LATCH_Y, LATCH_PIV), (0.012, LATCH_Y, LATCH_PIV))
# Angles are right-handed about the axis from the first point to the second, in Blender axes (lid:
# minus lifts the front edge; lever: plus swings the lever top forward and down). The engine rotates
# a bone right-handed in DayZ axes (kexport.conv, determinant -1), which in Blender axes is a
# left-handed turn about the memory-point axis. So that in game the lid goes up and the lever
# forward and down, as in the preview, the axis memory points are in reverse order (MEM_AXES
# below); check_turns verifies it.
MEM_AXES = {"ozl_lid_axis": [LID_AXIS[1], LID_AXIS[0]], "ozl_latch_axis": [LATCH_AXIS[1], LATCH_AXIS[0]]}
POSE = {SEL_LID: ("ozl_lid_axis", -LID_DEG), SEL_LATCH: ("ozl_latch_axis", LATCH_DEG)}
LID_ANIM = ("ozl_lid_open", dict(type="rotation", source="ozl_lid", selection=SEL_LID, axis="ozl_lid_axis",
                                 memory=1, minValue=0.3, maxValue=1.0, angle0=0.0, angle1=math.radians(-LID_DEG)))
LATCH_ANIM = ("ozl_latch_open", dict(type="rotation", source="ozl_lid", selection=SEL_LATCH, axis="ozl_latch_axis",
                                     memory=1, minValue=0.0, maxValue=0.4, angle0=0.0,
                                     angle1=math.radians(LATCH_DEG)))
# material kinds on the lid only: in the pose preview they have their own origins, rotated with the
# lid, otherwise the stencil on the lid (tied to the height ZL1) disappears
ROT_KINDS = {"lead_lid": SEL_LID, "lead_lid_in": SEL_LID, "enamel_lid": SEL_LID}


def pose_matrix(axis, deg):
    """Bone rotation by deg degrees as the engine does it from the memory points MEM_AXES[axis] (the pose
    preview is what the game will show): in Blender axes, right-handed about the reversed axis (from
    the second point to the first).
    """
    a, b = (Vector(q) for q in MEM_AXES[axis])
    return Matrix.Translation(a) @ Matrix.Rotation(math.radians(deg), 4, (a - b).normalized()) @ Matrix.Translation(-a)


def check_turns():
    """Numeric check, as check_axes of the Storage boxes: the engine rotation (pose_matrix) by the
    model.cfg animations moves the lid's front edge up (not into the body) and the latch lever top
    forward, toward the person, and down. If it does not hold, the build fails.
    """
    front = pose_matrix("ozl_lid_axis", math.degrees(LID_ANIM[1]["angle1"])) @ Vector((0.0, -FY, ZL1))
    top = pose_matrix("ozl_latch_axis", math.degrees(LATCH_ANIM[1]["angle1"])) @ Vector((0.0, LATCH_Y, 0.0835))
    assert front.z > ZL1 + 0.05, "the lid does not go up: front edge at z %.3f" % front.z
    assert top.y < LATCH_Y - 0.005 and top.z < LATCH_PIV, "the latch lever does not go forward and down"
    print("turns ok: lid front edge up by %.0f mm, lever forward and down" % ((front.z - ZL1) * 1000))


check_turns()
LOOKING ="--look" in kmodel.ARGV or "--look-render" in kmodel.ARGV
# the "work" look exists only in the --look preview (bone pose; same atlas, nothing to bake):
# without
# --look there is no such look, and baking, PAA and p3d are as for a model without looks
STATES = {"work": dict(remap={}, move={sel: pose_matrix(*POSE[sel]) for sel in POSE})} if LOOKING else None

OBJ, NAME = "m77_lead_case", "ozr_lead_case"
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL_LID, SEL_LATCH), bones=((SEL_LID, ""), (SEL_LATCH, "")),
                 animations=(LATCH_ANIM, LID_ANIM), sources={"ozl_lid": dict(animPeriod=1.2)}, states=STATES)
M.look_shots = (4, 2)
P = M.part
BOUNDS = {}

_place_look = krender.place_look


def place_look_pose(parts, kind_table, origin, remap=None, glow=1.5, sharp_deg=40.0, panels=None, move=None):
    """krender.place_look with group rotation: move holds a matrix instead of a shift (the work pose on
    the hinges). The ROT_KINDS kinds have a rotated origin, so the procedural pattern moves with the lid.
    """
    mats = {grp: m for grp, m in (move or {}).items() if isinstance(m, Matrix)}
    shift = {grp: d for grp, d in (move or {}).items() if not isinstance(d, Matrix)}
    for kind, grp in ROT_KINDS.items():
        if grp in mats:
            o2 = bpy.data.objects.new("origin_" + kind, None)
            bpy.context.scene.collection.objects.link(o2)
            o2.matrix_world = mats[grp]
            m = bpy.data.materials.new("oz_" + kind)
            kbake.MATS[kind] = (m, kmats.make(kind_table, kind, m, o2))
    obs = _place_look(parts, kind_table, origin, remap=remap, glow=glow, sharp_deg=sharp_deg, panels=panels,
                      move=shift)
    for p, ob in zip(parts, obs):
        if p.group in mats:
            ob.matrix_world = mats[p.group] @ ob.matrix_world
    return obs


krender.place_look = place_look_pose


# --- helpers ------------------------------------------------------------------------------------
def drop(p, pred):
    """Remove hidden faces (pred(centre, normal) -> True): those pressed against the lead or a neighbouring part."""
    p.bm.normal_update()
    dead = [f for f in p.bm.faces if pred(f.calc_center_median(), f.normal)]
    bmesh.ops.delete(p.bm, geom=dead, context="FACES")
    return p


def face(p, verts, want):
    """A face from bmesh vertices, turned toward `want`."""
    f = p.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def rrect(hx, hy, r, seg):
    """Rounded rectangle +-hx, +-hy counter-clockwise: [(x, y, nx, ny)] - a point and its outward normal;
    each corner is an arc of radius r in seg segments (seg = 1 gives a chamfer).
    """
    out = []
    for k, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        cx, cy = sx * (hx - r), sy * (hy - r)
        for i in range(seg + 1):
            a = k * math.pi / 2 + (math.pi / 2) * i / seg
            out.append((cx + r * math.cos(a), cy + r * math.sin(a), math.cos(a), math.sin(a)))
    return out


def inset(c):
    """How far a point is inside the outer outline of the cage (rounded rectangle FX, FY, R_OUT)."""
    qx, qy = abs(c.x) - (FX - R_OUT), abs(c.y) - (FY - R_OUT)
    if qx > 0 and qy > 0:
        return R_OUT - math.hypot(qx, qy)
    return min(FX - abs(c.x), FY - abs(c.y))


def inner(c, n):
    """A vertical cage face that looks inward and lies on the cage's inner side (pressed against the lead)."""
    return abs(n.z) < 0.5 and n.x * c.x + n.y * c.y < 0 and inset(c) > 0.7 * T


def fillet(pts, r, seg, corners):
    """Polyline with rounded corners (point indices in `corners`): an arc of radius r in seg segments."""
    v = [Vector(q) for q in pts]
    out = [v[0]]
    for i in range(1, len(v) - 1):
        if i not in corners:
            out.append(v[i])
            continue
        u, w = (v[i - 1] - v[i]).normalized(), (v[i + 1] - v[i]).normalized()
        half = u.angle(w) / 2
        t1 = v[i] + u * (r / math.tan(half))
        c = v[i] + (u + w).normalized() * (r / math.sin(half))
        a1, a2 = t1 - c, v[i] + w * (r / math.tan(half)) - c
        phi = a1.angle(a2)
        for k in range(seg + 1):
            s = k / seg
            out.append(c + (a1 * math.sin((1 - s) * phi) + a2 * math.sin(s * phi)) / math.sin(phi))
    out.append(v[-1])
    return [tuple(q) for q in out]


def arc_xz(cx, cz, r, a0, a1, n):
    """Arc in the XZ plane from angle a0 to a1 (degrees), n segments."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def rivet(p, c, axis, r=0.0024, h=0.0011, n=6):
    """Dome rivet head (axle, screw): a low cone of n sides, the bottom sunk in."""
    bm = p.bm
    a, c = Vector(axis).normalized(), Vector(c)
    u = a.orthogonal().normalized()
    w = a.cross(u)
    ring = [bm.verts.new(c - a * 0.0002 + (u * math.cos(2 * math.pi * k / n) + w * math.sin(2 * math.pi * k / n)) * r)
            for k in range(n)]
    top = bm.verts.new(c + a * h)
    below = c - a * r
    faces = []
    for k in range(n):
        f = bm.faces.new([ring[k], ring[(k + 1) % n], top])
        f.normal_update()
        if f.normal.dot(f.calc_center_median() - below) < 0:
            f.normal_flip()
        faces.append(f)
    return p.tag(faces)


def ring(p, z0, z1, seg, bottom=False):
    """A band of strip T around the cage (corners bent with radius R_OUT), from z0 to z1; inner faces are
    removed, and so is the lower edge if it is not visible (bottom=False).
    """
    pts = [(x - nx * T / 2, y - ny * T / 2, (z0 + z1) / 2) for x, y, nx, ny in rrect(FX, FY, R_OUT, seg)]
    g.sweep(p, pts, (0, 0, 1), T / 2, (z1 - z0) / 2, closed=True)
    return drop(p, lambda c, n: inner(c, n) or (not bottom and n.z < -0.9))


def annulus(p, outline, hx, hy, z, want):
    """Flat ring at height z from the outline (rrect, equal point count per corner) to the rectangle
    +-hx, +-hy: a fan to the rectangle corner at the corners, quads on the sides.
    """
    bm = p.bm
    n = len(outline) // 4
    ov = [bm.verts.new((x, y, z)) for x, y, _, _ in outline]
    cv = [bm.verts.new((sx * hx, sy * hy, z)) for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
    faces = []
    for k in range(4):
        arc = ov[k * n:(k + 1) * n]
        for j in range(n - 1):
            faces.append(face(p, [cv[k], arc[j], arc[j + 1]], want))
        faces.append(face(p, [arc[-1], ov[((k + 1) % 4) * n], cv[(k + 1) % 4], cv[k]], want))
    return p.tag(faces)


def slab(p, outline, z0, z1, rt, fil):
    """Casting with a rounded top edge: walls from z0 up along the outline (rrect), at the top an arc of
    radius rt in fil segments (fil = 1 gives a chamfer), the top is a single face. No bottom.
    """
    bm = p.bm
    prof = [(0.0, z0), (0.0, z1 - rt)] + [(-rt * (1 - math.cos(math.pi / 2 * i / fil)), z1 - rt + rt * math.sin(math.pi / 2 * i / fil))
                                         for i in range(1, fil + 1)]
    rings = [[bm.verts.new((x + nx * d, y + ny * d, z)) for x, y, nx, ny in outline] for d, z in prof]
    faces = []
    m = len(outline)
    for i in range(len(rings) - 1):
        for k in range(m):
            j = (k + 1) % m
            nx, ny = outline[k][2] + outline[j][2], outline[k][3] + outline[j][3]
            faces.append(face(p, [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]], (nx, ny, 0.3 * i)))
    faces.append(face(p, rings[-1], (0, 0, 1)))
    return p.tag(faces)


def nest(p, hx, hy, z0, z1):
    """The nest is a box without a top, faces looking inward."""
    fs = g.box(p, -hx, hx, -hy, hy, z0, z1)
    bmesh.ops.delete(p.bm, geom=[f for f in fs if f.normal.z > 0.9], context="FACES")
    bmesh.ops.reverse_faces(p.bm, faces=[f for f in fs if f.is_valid])
    p.bm.normal_update()


# --- body ---------------------------------------------------------------------------------
def build_body(spec):
    """Casting (the top of the walls and the nest are visible only in the work pose; the bottom rests on
    the tray floor and is removed) and the welded cage: tray with a floor, upper band, corner angles
    with a rounded back.
    """
    seg = spec["seg"]
    lead = P("lead", "lead")
    g.box(lead, -LW / 2, LW / 2, -LD / 2, LD / 2, Z_L0, ZB)
    drop(lead, lambda c, n: abs(n.z) > 0.9)
    lead.use("lead_in", *REGIONS["lead_in"])
    annulus(lead, rrect(LW / 2, LD / 2, R_OUT - T, seg), NEST[0], NEST[1], ZB, (0, 0, 1))
    nest(lead, NEST[0], NEST[1], NEST[2], ZB)
    tray = ring(P("tray", "enamel"), 0.0, TRAY_Z, seg)
    bot = [tray.bm.verts.new((x, y, 0.0)) for x, y, _, _ in rrect(FX - T, FY - T, R_OUT - T, seg)]
    tray.tag([face(tray, bot, (0, 0, -1))])
    band = ring(P("band", "enamel"), BAND[0], BAND[1], seg)
    ang = P("angles", "enamel")
    R, Ri = R_OUT, R_OUT - T
    cx, cy = FX - R, FY - R
    outer = [(FX - ANG, FY)] + [(cx + R * math.cos(math.radians(90 - 90 * i / seg)), cy + R * math.sin(math.radians(90 - 90 * i / seg)))
                                for i in range(seg + 1)] + [(FX, FY - ANG)]
    inn = [(FX - T, FY - ANG)] + [(cx + Ri * math.cos(math.radians(90 * i / seg)), cy + Ri * math.sin(math.radians(90 * i / seg)))
                                  for i in range(seg + 1)] + [(FX - ANG, FY - T)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            g.prism(ang, [(sx * a, sy * b) for a, b in outer + inn], (0, 1), TRAY_Z, BAND[0])
    drop(ang, lambda c, n: abs(n.z) > 0.9 or inner(c, n))
    return [lead, tray, band, ang]


def build_hinges(spec):
    """Two hinges: on the body's rear band a leaf with a rounded end and a hinge on an axle with heads;
    on the lid a strap bent over the rounded casting edge, riveted (it rises with the lid).
    """
    fine = spec["fine"]
    hw = P("hinge", "zinc")
    hl = P("hinge_lid", "zinc", group=SEL_LID)
    ys, ya = FY + STRAP_T / 2, LD / 2 + STRAP_T / 2          # strap middle on the band and on the lead
    for sx in (-1, 1):
        x = sx * STRAP_X
        g.cyl(hw, (x, HY, HZ), "x", HR, STRAP_W + 0.004, spec["knuckle"])
        # leaf on the body band: rounded bottom
        poly = [(x - STRAP_W / 2, HZ)] + arc_xz(x, 0.068, STRAP_W / 2, 180, 360, 4 if fine else 2) + [(x + STRAP_W / 2, HZ)]
        g.prism(hw, poly, (0, 2), FY, FY + STRAP_T)
        if fine:
            arc = [(LD / 2 - LID_R + (LID_R + STRAP_T / 2) * math.cos(math.radians(a)),
                    ZL1 - LID_R + (LID_R + STRAP_T / 2) * math.sin(math.radians(a))) for a in (0, 30, 60, 90)]
            path = [(ys, HZ), (ys, ZL0 + LID_BAND), (ya, ZL0 + LID_BAND + 0.0025)] + arc + [(-0.030, ZL1 + STRAP_T / 2)]
        else:
            path = [(ys, HZ), (ys, ZL1 - 0.002), (LD / 2 - 0.001, ZL1 + STRAP_T / 2), (-0.030, ZL1 + STRAP_T / 2)]
        g.sweep(hl, [(x, y, z) for y, z in path], (1, 0, 0), STRAP_T / 2, STRAP_W / 2)
        if fine:
            rivet(hw, (x, FY + STRAP_T, 0.0715), (0, 1, 0))
            for y in (0.040, -0.022):
                rivet(hl, (x, y, ZL1 + STRAP_T), (0, 0, 1))
            for dx in (-1, 1):       # axle heads
                rivet(hw, (x + dx * (STRAP_W / 2 + 0.002), HY, HZ), (dx, 0, 0), r=HR * 0.8, h=0.0012)
    # the leaf is pressed to the band, its top is in the hinge; the underside of the lid strap is
    # pressed
    # to the band and the lead
    drop(hw, lambda c, n: (n.y < -0.9 and abs(c.y - FY) < 1e-4) or (n.z > 0.9 and abs(c.z - HZ) < 1e-4))
    drop(hl, lambda c, n: in_lid(c + n * 0.002))
    return [hw, hl]


def in_lid(q):
    """A point inside the lid at rest: the casting or its band (roundings ignored - for the underside of the straps)."""
    if ZL0 < q.z < ZL1 and abs(q.x) < LW / 2 and abs(q.y) < LD / 2:
        return True
    return ZL0 < q.z < ZL0 + LID_BAND and abs(q.x) < FX and abs(q.y) < FY


def build_latch(spec):
    """Front toggle latch, fastened: a base with lugs and axle on the body band; the lever is a bent
    channel with a bent-out tongue (bone ozl_latch); a wire bail on the lever pins pulls the hook on
    the lid band (the hook rises with the lid).
    """
    fine = spec["fine"]
    y0 = -FY
    base = P("latch", "zinc")
    g.box(base, -0.012, 0.012, y0 - 0.0015, y0, 0.0665, 0.0835)
    g.cyl(base, (0.0, LATCH_Y, LATCH_PIV), "x", 0.0022, 0.021, 6 if fine else 4)
    if fine:
        for sx in (-1, 1):           # lugs for the axle and the base rivets
            g.box(base, *sorted((sx * 0.0081, sx * 0.0105)), LATCH_Y - 0.0012, y0 - 0.0015, 0.0655, 0.0725)
            rivet(base, (sx * 0.0098, y0 - 0.0015, 0.0790), (0, -1, 0), r=0.0016, h=0.0008, n=6)
    # underside of the base and lugs is pressed to the band and to the base
    drop(base, lambda c, n: n.y > 0.9 and (abs(c.y - y0) < 2e-4 or abs(c.y - (y0 - 0.0015)) < 2e-4))
    lever = P("lever", "zinc", group=SEL_LATCH)
    yo, yi = y0 - 0.0055, y0 - 0.0030             # lever face, shelf edges
    if fine:
        w, wi = 0.0075, 0.0067
        poly = [(-w, yi), (-w, yo), (w, yo), (w, yi), (wi, yi), (wi, yo + 0.0008), (-wi, yo + 0.0008), (-wi, yi)]
        g.prism(lever, poly, (0, 1), LATCH_PIV - 0.0025, 0.0835)
        g.box(lever, -0.0075, 0.0075, yo - 0.0025, yo, 0.0822, 0.0835)          # tongue
        drop(lever, lambda c, n: n.y > 0.9 and abs(c.y - yo) < 2e-4 and c.z > 0.082)
        for sx in (-1, 1):           # bail pins
            rivet(lever, (sx * 0.0075, y0 - 0.0042, 0.0770), (sx, 0, 0), r=0.0013, h=0.0010, n=6)
        yw, zt = y0 - 0.0040, HOOK_Z + 0.0005 + 0.0011
        pts = [(-0.0086, yw, 0.0770), (-0.0086, yw, zt - 0.0022), (-0.0074, yw, zt),
               (0.0074, yw, zt), (0.0086, yw, zt - 0.0022), (0.0086, yw, 0.0770)]
        g.pipe(lever, pts, 0.0011, 5)
    else:
        g.box(lever, -0.0075, 0.0075, yo, yi, LATCH_PIV - 0.0025, 0.0835)
    keeper = P("keeper", "zinc", group=SEL_LID)
    path = [(y0 - 0.0005, ZL0 + LID_BAND - 0.0005), (y0 - 0.0005, HOOK_Z), (y0 - 0.0060, HOOK_Z), (y0 - 0.0060, HOOK_Z + 0.0045)]
    g.sweep(keeper, [(0.0, y, z) for y, z in path], (1, 0, 0), 0.0005, 0.007)
    if fine:
        rivet(keeper, (0.0, y0 - 0.0010, ZL0 + LID_BAND - 0.0035), (0, -1, 0), r=0.0016, h=0.0008, n=6)
    return [base, lever, keeper]


def build_plate(spec):
    """Blank nameplate on two rivets (the rivets are in the image)."""
    p = P("plate", "plate")
    (cx, cz), (w, h) = PLATE_C, PLATE_S
    g.box(p, cx - w / 2, cx + w / 2, -LD / 2 - 0.0008, -LD / 2 + 0.0002, cz - h / 2, cz + h / 2)
    return [drop(p, lambda c, n: n.y > 0.9)]


def build_handles(spec):
    """Drop-down handles on both sides: eyes with a round lug on the band, a trapezoid bail of diameter 7
    hanging down, axle ends sticking out of the lugs; the tag is on the left one.
    """
    fine = spec["fine"]
    lug = P("lugs", "enamel")
    hd = P("handles", "handle")
    for sx in (-1, 1):
        x = sx * H_X
        for sy in (-1, 1):
            ear = arc_xz(H_X, H_TOP, EYE_R, -90, 90, 4 if fine else 2)
            poly = [(FX - 0.0005, H_TOP - EYE_R - 0.0005)] + ear + [(FX - 0.0005, H_TOP + EYE_R + 0.0005)]
            g.prism(lug, [(sx * a, b) for a, b in poly], (0, 2), sy * H_PIV - 0.0015, sy * H_PIV + 0.0015)
        ctrl = [(x, -H_PIV - 0.0035, H_TOP), (x, -H_PIV, H_TOP), (x, -H_LEG, H_BOT),
                (x, H_LEG, H_BOT), (x, H_PIV, H_TOP), (x, H_PIV + 0.0035, H_TOP)]
        g.pipe(hd, fillet(ctrl, 0.006, 2, (2, 3)) if fine else ctrl[1:-1], H_R, spec["rod"])
    drop(lug, lambda c, n: abs(n.x) > 0.9 and abs(c.x) < FX + 1e-4)
    parts = [lug, hd]
    if fine:
        # tag: a wire ring around the bail, the tag hangs on it by its hole (the hole is in the
        # image)
        x, yb = -H_X, TAG_C[0]
        r = 0.006
        zc = H_BOT + H_R + 0.0006 - r
        ringp = P("tag_ring", "zinc")
        g.pipe(ringp, [(x + r * math.sin(2 * math.pi * k / 8), yb, zc + r * math.cos(2 * math.pi * k / 8))
                       for k in range(9)], 0.0006, 3)
        tag = P("tag", "tag")
        (ty, tz), (tw, th) = TAG_C, TAG_S
        g.box(tag, x - 0.0004, x + 0.0004, ty - tw / 2, ty + tw / 2, tz - th / 2, tz + th / 2)
        parts += [ringp, tag]
    return parts


def build_lid(spec):
    """Lid (bone ozl_lid): cast lead with a rounded top edge and corners, a plug below going into the nest;
    a narrow band along the lower edge with bent corners.
    """
    seg, fil = spec["seg"], spec["fil"]
    lead = P("lid_lead", "lead_lid", group=SEL_LID)
    outline = rrect(LW / 2, LD / 2, R_OUT - T, seg)
    slab(lead, outline, ZL0, ZL1, LID_R, fil)
    lead.use("lead_lid_in", *REGIONS["lead_lid_in"])
    annulus(lead, outline, PLUG[0], PLUG[1], ZL0, (0, 0, -1))
    fs = g.box(lead, -PLUG[0], PLUG[0], -PLUG[1], PLUG[1], ZL0 - PLUG[2], ZL0)
    bmesh.ops.delete(lead.bm, geom=[f for f in fs if f.normal.z > 0.9], context="FACES")
    # the band's lower edge (2 mm) is visible only from below in the work pose - the casting wall is
    # behind it
    band = ring(P("lid_band", "enamel_lid", group=SEL_LID), ZL0, ZL0 + LID_BAND, seg)
    return [lead, band]


def build_lod(spec):
    parts = (build_body(spec) + build_hinges(spec) + build_latch(spec) + build_plate(spec)
             + build_handles(spec) + build_lid(spec))
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("bounds: %s .. %s" % (tuple(round(c, 4) for c in BOUNDS["lo"]),
                                   tuple(round(c, 4) for c in BOUNDS["hi"])))
    return parts


def collision():
    """One convex hull - the case with handles, hinges and latch (the lid is closed at rest; the work
    pose is cosmetic). Mass is the item's weight in the mod, 0.8 kg; penetration and sound are thick
    metal (castiron).
    """
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    pts = kx.box_pts(lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    comps = [(pts, kx.PEN + r"\castiron.rvmat")]
    memory = {
        # inventory preview camera: front-left and from above (invView = camera position)
        "invView": [(-0.26, -0.40, 0.36)],
        "ce_center": [(0.0, 0.0, 0.058)],
        "ce_radius": [(0.13, 0.0, 0.058)],
        # work bone axes: lid hinges and the latch lever axis
        "ozl_lid_axis": MEM_AXES["ozl_lid_axis"],         # point order is set by MEM_AXES (the lid goes up in game)
        "ozl_latch_axis": MEM_AXES["ozl_latch_axis"],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


# the first four are the --look preview (M.look_shots), the first two also the work look
SHOTS = [
    ("front", (-0.17, -0.50, 0.28), (0.0, 0.0, 0.055), 40),
    ("top", (0.05, -0.30, 0.42), (0.0, 0.0, 0.07), 40),
    ("latch", (-0.05, -0.26, 0.13), (0.0, -0.06, 0.075), 50),
    ("left", (-0.46, -0.22, 0.22), (0.0, 0.0, 0.055), 40),
    ("back", (0.34, 0.44, 0.26), (0.0, 0.0, 0.06), 40),
]

M.run(build_lod, collision, SHOTS, row_step=0.30, row_shot=((0.15, -0.95, 0.30), (0.15, 0, 0.06)))
