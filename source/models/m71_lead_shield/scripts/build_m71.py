"""M71 - Lead shield (OZL_Tool_LeadShield): a module of the "Anomaly" line - a portable 2x2 item, it
stands in slot OZL_Tool3 of the packer (M03: inside at the centre by the glass, M09: on the right
shelf by the hatch) and is visible there through the module_3 proxy. Variant A: a house of lead
bricks.

    blender --background --python build_m71.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (the sticker with the sign, brick
numbers).

Target: a "house" wall of standard 50 x 100 x 200 mm lead bricks in a U shape in two courses, a steel
plate on top, a place for a sample inside; ~0.20 x 0.15 x 0.20 m, 6-8 bricks, dull grey lead with a
white bloom and dents. The module platform is ~0.2 x 0.2 m, up to ~0.25 m.

Reference and sizes:
- look: a wall of lead bricks around a Cs-137 source under a plate (a public-domain Wikimedia Commons
  photo "Lead shielding.jpg"): the bricks stand on edge and on end, the edges are cast and rounded,
  the lead is dark, scratched and whitish where worn, a yellow sticker with a sign on a brick;
- brick: the standard 2 x 4 x 8" = 50 x 100 x 200 mm (catalogues: Ultraray "2 x 4 x 8 in, 26 lbs";
  Mirion/Capintec 7410-0001 "2 x 4 x 8 in"). The mass from a density of 11.34 g/cm3 is 11.3 kg
  (1 dm3), not a data sheet figure;
- no ready 2 x 4 x 4" halves were found in catalogues (there are 2 x 4 x 6 and 2 x 4 x 12, Ultraray),
  and lead is soft - bricks are sawn on site. So the sides are halves of 50 x 100 x 100, sawn from
  standard bricks: one end is cast (rounded), the other is a flat saw cut with saw marks.
Layout: the back wall is two standard bricks on edge (200 x 50 x 100) one on top of the other, the
sides are two halves each on edge along the depth (50 x 100 x 100) in front of it. Six bricks, two
courses, the masonry measures 0.200 x 0.150 x 0.200 m, exactly the target; the cavity of
100 x 100 x 200 mm is open at the front. On top is a 6 mm steel plate with a D 32 hole for a sensor
above the cavity, below is a 3 mm steel tray sheet (without it a portable module has no floor at the
sample place). The masonry with the plates is 0.206 x 0.158 x 0.210 m. Inside is an aluminium D 60
stand with a D 40 dish and a piece of rock. The bricks are stacked by hand: gaps of 0.5-2 mm,
rotations up to 0.7 degrees. Real masonry weighs ~45 kg; the item weight is the 800 g of the
OZL_Tool_Base class (the module rules are untouched), the mass in Geometry is the same.

Detailing: "dayz" look; the cast brick edges of R 5 mm in two steps of ~30 degrees (22.5/45/22.5
degrees would give a sharp kink at the edge - angular); each brick's cast side is a shallow
bowl with a rim (casting shrinkage) and rougher than the others, the vertices are slightly uneven
(the bricks are cast, not milled); the lead is darker (as in the photo, the tone of the vanilla
workshop 31-78), the bloom is in patches rather than a solid haze; the stand and the dish are turned,
with chamfers; next to the sensor hole lies the removed lead plug with a collar (real houses close
the port with one).
"Working" state: on the plate is a battery-powered magnetic beacon with a red cap, as on portable
masonry with an open source (it blinks when working). It can be removed: BEACON = False. No vanilla
proxy items on the module: the module itself stands as a proxy in someone else's machine, so its
items would repeat in all packers of the line and in the inventory, and a nested proxy has not been
checked on the stand.

State (modules without a faction colour): used but intact - dull lead with a white oxide bloom,
scratches down to light metal, dents and crushed corners, worn edges; the plate paint chipped down to
steel with rust along the chips. Marks: a trefoil on the sticker without a caption, brick numbers in
white paint - digits only. LODs (a small item): near and middle (a one-step chamfer, no dents, no
cast bowl, no plate hole, no dish), no far one.

Blender axes: X is width, Y is depth (the face, the open side of the house, is -Y), Z is up. The
origin is the centre of the bottom: this is how the module stands on the module_N proxy point
(autocenter = 0 in Geometry).
"""
import math
import os
import sys

import bmesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
from mathutils import Matrix, Vector, noise  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m --------------------------------------------------------------------------------
BASE_T = 0.003                          # tray sheet
BASE = (0.206, 0.158)
Z0 = BASE_T                             # the bricks stand on the tray
COURSE = 0.100                          # course: a brick on edge
GAP_Z = 0.0005
BEV = 0.005                             # cast brick edge
# bmesh bevel profile (0.5 is an arc, 0.25 is straight): two arc steps give angles of 22.5/45/22.5
# degrees, and kexport and the preview leave edges with an angle above 40 degrees sharp - a kink on the
# edge. 0.40 gives three transitions of ~30 degrees, a smooth edge (the "bevel max" print in the log)
BEV_PROFILE = 0.40
POUR_RIM, POUR_DEPTH = 0.007, 0.0007    # cast side: the rim and the depth of the shrinkage bowl
JITTER = 0.00025                        # casting unevenness, the amplitude of the vertex shift
STD = (0.200, 0.050, 0.100)             # standard brick on edge along X (length, thickness, height)
HALF = (0.050, 0.100, 0.100)            # half brick on edge along Y
ZT = Z0 + 2 * COURSE + GAP_Z            # top of the masonry
PLATE = (0.204, 0.156, 0.006)           # steel plate on top
PLATE_C, PLATE_ROT = (0.002, -0.001), 1.2
PLATE_Z = ZT + 0.0005
ZP = PLATE_Z + PLATE[2]                 # top of the plate
HOLE_C, HOLE_R = (0.0, -0.026), 0.016   # sensor hole above the middle of the cavity
STAGE_C, STAGE_R, STAGE_H = (0.0, -0.030), 0.030, 0.020
DISH_R, DISH_H = 0.020, 0.005
# port plug: lead, a collar D 42 x 6 and a rod D 30 x 13 - lies collar down beside the hole
PLUG_C = (0.058, -0.040)
# "source open" beacon: a body D 52 x 16 on a magnet, a cap D 41 x 22 - 38 mm together, the top of the
# module is 0.248 m (the space above the platform is ~0.25 m)
BEACON = True
BEACON_C = (-0.056, 0.038)

# bricks: name, region, size, centre (x, y), course, rotation (degrees), saw cut (the sign of the end
# along local Y, or 0), crushed corners [(corner x, y, z signs, depth)], cast side (axis, sign)
BRICKS = [
    ("back_1", "lead_a", STD, (0.001, 0.0500), 0, 0.3, 0, [(-1, 1, -1, 0.004), (1, -1, 1, 0.003)], ("y", 1)),
    ("back_2", "lead_b", STD, (-0.0015, 0.0505), 1, -0.4, 0, [(1, 1, 1, 0.005), (-1, -1, 1, 0.002)], ("y", -1)),
    ("left_1", "lead_c", HALF, (-0.0755, -0.0270), 0, -0.6, -1, [(-1, 1, 1, 0.003)], ("x", -1)),
    ("left_2", "lead_a", HALF, (-0.0745, -0.0280), 1, 0.5, 1, [(-1, -1, 1, 0.005), (1, -1, -1, 0.002)], ("x", 1)),
    ("right_1", "lead_b", HALF, (0.0755, -0.0275), 0, 0.4, 1, [(1, -1, -1, 0.004)], ("x", 1)),
    ("right_2", "lead_c", HALF, (0.0760, -0.0265), 1, -0.5, -1, [(1, 1, 1, 0.004), (-1, 1, 1, 0.002)], ("x", -1)),
]

LOD_SPECS = [
    dict(lod=0, sides=16),
    dict(lod=1, sides=8),
]

REGIONS = {
    "lead_a": ("lead_a", 1.0), "lead_b": ("lead_b", 1.0), "lead_c": ("lead_c", 1.0), "lead_saw": ("lead_saw", 1.0),
    "lead_pour": ("lead_pour", 1.0), "plug": ("plug", 1.5),
    "plate": ("plate", 0.9), "base": ("base", 0.7), "alu": ("alu", 1.2), "dish": ("dish", 1.5),
    "rock": ("rock", 2.0), "beacon_body": ("beacon_body", 1.5), "beacon": ("beacon", 2.0),
}

# "working" state: the beacon cap is ozl_lamp (in hiddenSelections); when working, the _on atlas (the
# cap is lit), the blinking is blink in OZL_Work of the mod config
SEL_LAMP = "ozl_lamp"
ON = dict(remap={"beacon": "beacon_on"}, emissive=(1.0, 1.0, 1.0, 1.0))


def wdecal(name):
    return os.path.join(WORK, name)


def brick_face(name, axis, sign):
    """Coordinate of the face of brick name along axis (without rotation), for the sticker range."""
    for nm, _, size, (cx, cy), _, _, _, _, _ in BRICKS:
        if nm == name:
            c = {"x": cx, "y": cy}[axis]
            return c + sign * size["xy".index(axis)] / 2
    raise KeyError(name)


def zc(course):
    return Z0 + course * (COURSE + GAP_Z) + COURSE / 2


# stickers: (image, normal axis, sign, (u axis, v axis), centre (u, v), size (w, h; a negative w mirrors
# it so the image reads from outside), range along the normal axis)
def _dec(img, ax, sign, uv, center, size, face):
    return (wdecal(img), ax, sign, uv, center, size, (face - 0.005, face + 0.005))


STICKER = _dec("decal_sticker.png", "x", -1, ("y", "z"), (-0.030, zc(1) + 0.004), (-0.040, 0.054),
               brick_face("left_2", "x", -1))
NUM_12 = _dec("decal_num_12.png", "y", -1, ("x", "z"), (0.076, zc(0) - 0.012), (0.032, 0.021),
              brick_face("right_1", "y", -1))
NUM_7 = _dec("decal_num_7.png", "y", 1, ("x", "z"), (0.050, zc(0) + 0.006), (-0.024, 0.034),
             brick_face("back_1", "y", 1))
NUM_31 = _dec("decal_num_31.png", "x", 1, ("y", "z"), (-0.030, zc(1) - 0.010), (0.036, 0.024),
              brick_face("right_2", "x", 1))
LEAD_DECALS = [(STICKER, "sticker"), (NUM_12, "paint"), (NUM_7, "paint"), (NUM_31, "paint")]

# --- materials: the pattern at the scale of the item (a 20 cm brick, not a metre-sized machine) ---
# lead is dark: in the reference photo the masonry is almost black-grey, only the scratches and bloom
# are light; the vanilla workshop is L 31..78
LEAD = kmats.lin((70, 73, 79))
LEAD_DARK = kmats.lin((50, 52, 58))
OXIDE = kmats.lin((168, 170, 164))       # whitish bloom
BRIGHT = kmats.lin((150, 154, 162))      # fresh lead cut in a scratch
POLISH = kmats.lin((106, 110, 118))      # rubbed by hands
SAWN = kmats.lin((88, 92, 100))          # saw cut: slightly lighter metal, thin oxide (the cut is not new)


def small(t, origin, seed, k=10.0):
    vec, sep = t.coords(origin, seed)
    return t.stretch(vec, k, k, k), sep


def tri(t, x):
    """Sawtooth 0..1 -> triangle: 0 at the edges, 1 in the middle."""
    return t.math("SUBTRACT", 1.0, t.math("MULTIPLY", t.math("ABSOLUTE", t.math("SUBTRACT", x, 0.5)), 2.0))


def rotated(t, vec, euler):
    m = t.node("ShaderNodeMapping")
    m.inputs["Rotation"].default_value = euler
    t.link(vec, m.inputs["Vector"])
    return m.outputs[0]


def scratches(t, vec, nsep, amount=1.0):
    """Short straight scratches: iso-lines of noise strongly stretched along the scratch direction, masked -
    segments of 2-3 cm. The families along X, Y, Z are suppressed on faces perpendicular to their
    direction (the iso-lines would swirl like marble there); the fourth family is diagonal, to which all
    faces are oblique."""
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
    """Dents from impacts: Voronoi cells, a bowl in rare cells (0 around, 1 in the middle)."""
    vor = t.node("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = scale
    t.link(vec, vor.inputs["Vector"])
    bowl = t.maprange(vor.outputs["Distance"], 0.05, 0.38, 1.0, 0.0)
    pick = t.math("GREATER_THAN", t.bw(vor.outputs["Color"]), 1.0 - amount)
    return t.math("MULTIPLY", t.math("MULTIPLY", bowl, bowl), pick)


def mat_lead(mat, origin, seed=1.0, tone=1.0, saw=False, pour=False, scratch=1.0):
    """Cast lead of a brick: dull dark grey with a blue tint, patches and specks of white oxide (more near
    the bottom), scratches down to light metal, dents, rubbed edges, dirt in the gaps; in the "dayz"
    profile also its layers (tonal blotches, streaks, grease spots, small scratches). saw is the sawn
    end: lighter metal, thin oxide, parallel blade marks. pour is the cast side (the bottom of the
    shrinkage bowl): rough, with solidification waves and pores, with more oxide in the pores. On top,
    the sticker and the paint numbers."""
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, seed)
    nsep = t.normal()
    base = tuple(min(1.0, c * tone) for c in (SAWN if saw else LEAD)[:3]) + (1,)
    dark = tuple(min(1.0, c * tone) for c in LEAD_DARK[:3]) + (1,)
    col = t.mixc(t.maprange(t.noise(vec, 1.2, 6.0, 0.6), 0.3, 0.75, 0.0, 0.6 if saw else 1.0), dark, base)
    h = 0.0
    if saw:
        # blade marks across the end (along X) with a slight wave, pitch ~1.5 mm; the depth is uneven - it was
        # sawn by hand, worn in places
        wave = t.math("MULTIPLY", t.noise(t.stretch(vec, 0.3, 0.3, 0.3), 2.0, 2.0, 0.5), 0.6)
        ridge = tri(t, t.math("FRACT", t.math("ADD", t.math("DIVIDE", sep.outputs["Z"], 0.0015), wave)))
        ridge = t.math("MULTIPLY", ridge, t.maprange(t.noise(vec, 2.5, 3.0, 0.5), 0.35, 0.65, 0.2, 1.0))
        col = t.mixc(t.math("MULTIPLY", ridge, 0.07), col, BRIGHT)
        h = t.math("MULTIPLY", ridge, 0.12)
    pores = None
    if pour:
        # solidification waves (stretched noise) and casting pores: relief and dark dots
        ripple = t.noise(t.stretch(vec, 1.0, 0.25, 1.0), 6.0, 3.0, 0.55)
        pores = t.maprange(t.noise(vec, 28.0, 2.0, 0.5), 0.66, 0.74, 0.0, 1.0)
        col = t.mixc(t.math("MULTIPLY", pores, 0.6), col, LEAD_DARK)
        h = t.math("SUBTRACT", t.math("MULTIPLY", ripple, 0.45), t.math("MULTIPLY", pores, 0.5))
    # oxide: patches, specks, denser near the bottom (damp from the floor)
    blot = t.maprange(t.noise(vec, 0.9, 6.0, 0.6), 0.58, 0.80, 0.0, 1.0)
    speck = t.maprange(t.noise(vec, 9.0, 4.0, 0.6), 0.64, 0.80, 0.0, 1.0)
    low = t.maprange(sep.outputs["Z"], Z0, Z0 + 0.05, 0.35, 0.0)
    ox = t.math("ADD", t.math("MULTIPLY", blot, 0.25), t.math("MULTIPLY", speck, 0.50))
    if pores is not None:
        ox = t.math("ADD", ox, t.math("MULTIPLY", pores, 0.35))
    ox = t.math("MINIMUM", t.math("ADD", ox, t.math("MULTIPLY", low, t.noise(vec, 3.0, 5.0, 0.6))), 0.75)
    if saw:
        ox = t.math("MULTIPLY", ox, 0.35)
    col = t.mixc(ox, col, OXIDE)
    # sticker and numbers: over the oxide, under the scratches and dirt
    stick = None
    for (path, ax, sign, (au, av), center, size, rng), kind in LEAD_DECALS:
        gate = t.facing(nsep, ax.upper(), sign, 0.5)
        w = sep.outputs["XYZ".index(ax.upper())]
        gate = t.math("MULTIPLY", gate, t.math("MULTIPLY", t.math("GREATER_THAN", w, rng[0]),
                                               t.math("LESS_THAN", w, rng[1])))
        c, a = t.image(path, sep.outputs["XYZ".index(au.upper())], sep.outputs["XYZ".index(av.upper())],
                       center, size)
        m = t.math("MULTIPLY", a, gate)
        col = t.mixc(m, col, c)
        if kind == "sticker":
            stick = m
    cav = t.maprange(t.cavity(0.012), 0.15, 0.6, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.55), col, kmats.GRIME)
    dirt = cav
    if kmats.LOOK["name"] == "dayz":
        col, dirt = kmats.dayz_layers(t, col, cav, vec, sep, nsep, 0.5)
    scr = scratches(t, vec, nsep, scratch)
    col = t.mixc(t.math("MULTIPLY", scr, 0.75), col, BRIGHT)
    dn = dents(t, vec, 6.5, 0.22)
    col = t.mixc(t.math("MULTIPLY", dn, 0.35), col, POLISH)
    edge = t.maprange(t.edge_wear(0.0025), 0.05, 0.30, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.50), col, POLISH)
    h = t.math("SUBTRACT", h, t.math("ADD", t.math("MULTIPLY", scr, 0.25), t.math("MULTIPLY", dn, 0.7)))
    up = t.maprange(nsep.outputs["Z"], 0.4, 0.9, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", up, t.noise(vec, 3.0, 4.0, 0.6)), 0.40), col, kmats.DUST)
    gl = t.math("ADD", 0.18, t.math("SUBTRACT", t.math("ADD", t.math("MULTIPLY", scr, 0.25),
                                                       t.math("MULTIPLY", edge, 0.20)),
                                     t.math("ADD", t.math("MULTIPLY", ox, 0.12), t.math("MULTIPLY", dirt, 0.1))))
    sp = t.math("ADD", 0.14, t.math("ADD", t.math("MULTIPLY", scr, 0.3), t.math("MULTIPLY", edge, 0.2)))
    if saw:
        gl = t.math("ADD", gl, 0.08)
        sp = t.math("ADD", sp, 0.08)
    if pour:
        gl = t.math("SUBTRACT", gl, 0.06)
    if stick is not None:
        gl = t.mixf(stick, gl, 0.35)
        sp = t.mixf(stick, sp, 0.22)
    return kmats.out(t, col, gl, sp, h)


def mat_lens(mat, origin, color, seed=6.6, lit=False):
    """Beacon cap: red moulded plastic with Fresnel lens rings (relief and tone stripes), dust on top; lit is
    the "working" state (the lamp is lit: a brighter colour, less dust)."""
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, seed)
    nsep = t.normal()
    rib = tri(t, t.math("FRACT", t.math("DIVIDE", sep.outputs["Z"], 0.0022)))
    lo = tuple(c * (0.80 if lit else 0.62) for c in color[:3]) + (1,)
    col = t.mixc(t.math("MULTIPLY", rib, 0.8), lo, color)
    up = t.maprange(nsep.outputs["Z"], 0.3, 0.9, 0.0, 1.0)
    dust = t.math("MULTIPLY", t.math("MULTIPLY", up, t.noise(vec, 4.0, 4.0, 0.6)), 0.06 if lit else 0.40)
    col = t.mixc(dust, col, kmats.DUST)
    return kmats.out(t, col, 0.60, 0.45, t.math("MULTIPLY", rib, 0.30))


# less dust than on a machine: the "dayz" profile multiplies it by 1.8, and a 20 cm plate came out light grey
PLATE_PAINT = dict(color=kmats.lin((46, 48, 50)), under=kmats.lin((122, 120, 114)), gloss=0.30, spec=0.25,
                   chip=(0.50, 0.58), rust=(0.58, 0.66), rust_low=0.3, floor_z=0.0, dust=0.12, grime=0.45)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "lead_a": (mat_lead, dict(seed=1.0, tone=0.84)),
    "lead_b": (mat_lead, dict(seed=2.7, tone=0.77)),
    "lead_c": (mat_lead, dict(seed=4.1, tone=0.91, scratch=0.8)),
    "lead_saw": (mat_lead, dict(seed=5.3, saw=True, scratch=0.6)),
    "lead_pour": (mat_lead, dict(seed=3.3, tone=0.80, pour=True, scratch=0.5)),
    "plug": (mat_lead, dict(seed=7.7, tone=0.86, scratch=1.2)),
    # plate and tray: dark enamel over steel, chips down to metal, rust along the chips
    "plate": ("paint", dict(PLATE_PAINT, seed=6.2)),
    "base": ("paint", dict(PLATE_PAINT, seed=7.4, dust=0.10, grime=0.6)),
    # tarnished aluminium, not white
    "alu": ("steel", dict(seed=8.1, tone=0.25, along="z", gloss=0.35, spec=0.45, dust=0.35, grime=0.6)),
    "dish": ("steel", dict(seed=8.7, tone=0.30, along="x", gloss=0.50, spec=0.60, dust=0.1, grime=0.45)),
    # sample: dark rock with rusty veins
    "rock": ("plastic", dict(color=kmats.lin((96, 82, 66)), seed=9.3, gloss=0.22, spec=0.15, mottle=0.45,
                             dust=0.15, grime=0.5, scuff=(0.52, 0.62))),
    # beacon: a black plastic body, a red cap (lit when working)
    "beacon_body": ("plastic", dict(color=kmats.lin((28, 28, 29)), seed=6.9, gloss=0.30, spec=0.22, dust=0.45,
                                    grime=0.45, scuff=(0.60, 0.68))),
    "beacon": (mat_lens, dict(color=kmats.lin((150, 26, 18)))),
    # lit is deep red: a lighter one makes the preview turn red into pink
    "beacon_on": (mat_lens, dict(color=kmats.lin((205, 24, 10)), lit=True)),
})

OBJ, NAME = "m71_lead_shield", "ozr_lead_shield"
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL_LAMP,) if BEACON else (), hidden=(SEL_LAMP,) if BEACON else (),
                 states={"on": ON} if BEACON else None)
P = M.part
BOUNDS = {}


# =============================================================================
# Primitives missing from kgeo
# =============================================================================
def face(part, verts, want):
    """Face from bmesh vertices, oriented towards want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def lathe(part, prof, sides, center, cap=None):
    """Solid of revolution about a vertical through center: prof [(r, h)] in walk order, outwards is to the
    right of the walk direction in the (r, h) plane (up along the outer wall, inwards across the top, down
    along the inner one); cap is a disc on the last ring with its normal up (+1) or down (-1)."""
    bm = part.bm
    c0 = Vector(center)

    def pt(r, h, k):
        a = 2 * math.pi * k / sides
        return c0 + Vector((r * math.cos(a), r * math.sin(a), h))
    rings = [[bm.verts.new(pt(r, h, k)) for k in range(sides)] for r, h in prof]
    new = []
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        nr, nh = h1 - h0, -(r1 - r0)
        for k in range(sides):
            j = (k + 1) % sides
            a = 2 * math.pi * (k + 0.5) / sides
            new.append(face(part, [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]],
                            (nr * math.cos(a), nr * math.sin(a), nh)))
    if cap:
        new.append(face(part, rings[-1], (0.0, 0.0, float(cap))))
    bm.normal_update()
    return part.tag(new)


def rbox(part, x0, x1, y0, y1, z0, z1, r, seg=2, profile=BEV_PROFILE):
    """A box with rounded edges: like kgeo.box, but the bevel profile is a parameter (kgeo always uses an arc
    of 0.5: with two steps the middle kink is 45 degrees, which stays sharp)."""
    bm = part.bm
    before = set(bm.faces)
    vs = bmesh.ops.create_cube(bm, size=1.0)["verts"]
    for v in vs:
        v.co = Vector((x0 + (v.co.x + 0.5) * (x1 - x0), y0 + (v.co.y + 0.5) * (y1 - y0),
                       z0 + (v.co.z + 0.5) * (z1 - z0)))
    # edges without repeats in a fixed order: a set has a different order from run to run (memory
    # addresses), so the bevel built the faces differently each time and the uvhash in the bake did not
    # match the snapshot
    edges = list(dict.fromkeys(e for v in vs for e in v.link_edges))
    bmesh.ops.bevel(bm, geom=vs + edges, offset=r, offset_type="OFFSET", segments=seg, profile=profile,
                    affect="EDGES", clamp_overlap=True)
    faces = [f for f in bm.faces if f not in before]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    bm.normal_update()
    return part.tag(faces)


def max_angle(bm):
    """The largest angle between adjacent faces, degrees (an edge smoothness check)."""
    return max((math.degrees(e.calc_face_angle(0.0)) for e in bm.edges if len(e.link_faces) == 2), default=0.0)


def place(p, center, rot_deg):
    """Rotate a part around Z (about its own origin) and move it to center."""
    bmesh.ops.rotate(p.bm, verts=p.bm.verts[:], cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(rot_deg), 3, "Z"))
    bmesh.ops.translate(p.bm, verts=p.bm.verts[:], vec=Vector(center))
    p.bm.normal_update()
    return p


def crush(p, corner, depth, radius=0.016):
    """Crushed corner: vertices near the corner shift towards the brick middle, more strongly towards the
    corner."""
    c = Vector(corner)
    inward = -c.normalized()
    for v in p.bm.verts:
        d = (v.co - c).length
        if d < radius:
            v.co += inward * depth * (1.0 - d / radius) ** 2


def pour_face(p, axis, sign, region):
    """Cast side: the large face with normal (axis, sign) sinks as a shallow bowl inside a rim (lead
    shrinkage when cast in an open mould) and gets a region of its own."""
    n = Vector([float(sign) if a == axis else 0.0 for a in "xyz"])
    cands = [f for f in p.bm.faces if f.normal.dot(n) > 0.999]
    f = max(cands, key=lambda q: q.calc_area())
    bmesh.ops.inset_individual(p.bm, faces=[f], thickness=POUR_RIM, depth=-POUR_DEPTH, use_even_offset=True)
    f[p.reg] = p.region_index(region, *REGIONS[region])
    p.bm.normal_update()


def jitter(p, seed, amp=JITTER):
    """Slightly uneven vertices: a cast brick, not a milled one."""
    off = Vector((seed * 7.1, seed * 3.3, seed * 5.9))
    # noise_vector without seed_set differs in each Blender process (noise does not): the bricks came out
    # different every time, and the bake rejected the atlas because the uvhash did not match the snapshot
    noise.seed_set(71)
    for v in p.bm.verts:
        v.co += noise.noise_vector(v.co * 30.0 + off) * amp
    p.bm.normal_update()


def brick(spec, entry, idx):
    name, region, (lx, ly, lz), (cx, cy), course, rot, saw, crushed, (pax, psign) = entry
    lod = spec["lod"]
    y0, y1 = -ly / 2, ly / 2
    if saw and lod == 0:
        # the cast brick is longer, the saw cut removes it together with the cast edge - the end is flat and
        # sharp
        y0, y1 = (y0, y1 + 0.02) if saw > 0 else (y0 - 0.02, y1)
    p = P(name, region)
    if lod == 0:
        rbox(p, -lx / 2, lx / 2, y0, y1, -lz / 2, lz / 2, BEV)
        if idx == 0:
            print("bevel max angle (brick %s): %.1f deg" % (name, max_angle(p.bm)))
        pour_face(p, pax, psign, "lead_pour")
        jitter(p, idx + 1.0)
        for sx, sy, sz, depth in crushed:
            if sy != saw:
                crush(p, (sx * lx / 2, sy * ly / 2, sz * lz / 2), depth * 1.5)
        if saw:
            cut = P(name + "_cut", "lead_saw")
            ys = sorted((saw * ly / 2, saw * (ly / 2 + 0.05)))
            g.box(cut, -lx, lx, ys[0], ys[1], -lz, lz)
            p = M.boolean(name, p, [cut])
    else:
        g.box(p, -lx / 2, lx / 2, y0, y1, -lz / 2, lz / 2, r=0.003, seg=1)
        if saw:
            si = p.region_index("lead_saw", *REGIONS["lead_saw"])
            for f in p.bm.faces:
                if f.normal.y * saw > 0.9:
                    f[p.reg] = si
    p = place(p, (cx, cy, 0.0), rot)
    bmesh.ops.translate(p.bm, verts=p.bm.verts[:], vec=Vector((0, 0, zc(course))))
    return p


def to_local(xy, center, rot_deg):
    """World point (x, y) -> local coordinates of a part rotated by rot_deg about center."""
    v = Matrix.Rotation(math.radians(-rot_deg), 3, "Z") @ Vector((xy[0] - center[0], xy[1] - center[1], 0.0))
    return v.x, v.y


def build_plates(spec):
    lod = spec["lod"]
    parts = []
    px, py, pt = PLATE
    top = P("plate", "plate")
    if lod == 0:
        rbox(top, -px / 2, px / 2, -py / 2, py / 2, 0.0, pt, 0.0018)
        hx, hy = to_local(HOLE_C, PLATE_C, PLATE_ROT)
        hole = P("plate_hole", "plate")
        g.cyl(hole, (hx, hy, pt / 2), "z", HOLE_R, pt + 0.01, 16)
        top = M.boolean("plate", top, [hole])
    else:
        g.box(top, -px / 2, px / 2, -py / 2, py / 2, 0.0, pt)
    top = place(top, (PLATE_C[0], PLATE_C[1], PLATE_Z), PLATE_ROT)
    parts.append(top)
    bx, by = BASE
    base = P("base", "base")
    g.box(base, -bx / 2, bx / 2, -by / 2, by / 2, 0.0, BASE_T, **({"r": 0.001, "seg": 1} if lod == 0 else {}))
    parts.append(base)
    return parts


def build_top_items(spec):
    """On the plate: the removed port plug (lead) and the "source open" beacon (the cap is ozl_lamp)."""
    lod = spec["lod"]
    parts = []
    ux, uy = PLUG_C
    pl = P("plug", "plug")
    if lod == 0:
        # collar down: a cast collar D 42 x 6 with rounding, a rod D 30 with a chamfer at the end
        lathe(pl, [(0.0210, 0.0), (0.0204, 0.0058), (0.0150, 0.0066), (0.0150, 0.0178), (0.0136, 0.0192)], 16,
              (ux, uy, ZP), cap=1)
    else:
        g.cyl(pl, (ux, uy, ZP + 0.0096), "z", 0.018, 0.0192, 8)
    parts.append(pl)
    if not BEACON:
        return parts
    bx, by = BEACON_C
    body = P("beacon_body", "beacon_body")
    dome = P("beacon_dome", "beacon", group=SEL_LAMP)
    if lod == 0:
        lathe(body, [(0.0260, 0.0), (0.0248, 0.0140), (0.0232, 0.0160), (0.0208, 0.0160)], 14, (bx, by, ZP))
        # cap: four belts up to the top - all transitions are below 40 degrees, the dome is smooth
        lathe(dome, [(0.0205, 0.0160), (0.0205, 0.0215), (0.0182, 0.0312), (0.0108, 0.0372), (0.0050, 0.0390)], 14,
              (bx, by, ZP), cap=1)
    else:
        g.cyl(body, (bx, by, ZP + 0.008), "z", 0.026, 0.016, 8, r2=0.0235)
        g.cyl(dome, (bx, by, ZP + 0.0270), "z", 0.0205, 0.0220, 8, r2=0.0115)
    parts += [body, dome]
    return parts


def rock(part, center, size, subdiv, seed=3.0):
    """A piece of rock: a noisy icosphere with a flattened bottom - it lies in the dish."""
    bm = part.bm
    before = set(bm.faces)
    ret = bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    c = Vector(center)
    for v in ret["verts"]:
        d = v.co.normalized()
        k = 1.0 + 0.34 * noise.noise(d * 1.7 + Vector((seed, 0, 0))) + 0.16 * noise.noise(d * 4.5)
        v.co = c + Vector((d.x * size[0] * k, d.y * size[1] * k, max(d.z * size[2] * k, -size[2] * 0.6)))
    faces = [f for f in bm.faces if f not in before]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return part.tag(faces)


def build_sample(spec):
    """Sample place in the cavity: a turned aluminium stand with a chamfer, a dish with a rim on it, and a
    piece of rock."""
    lod, n = spec["lod"], spec["sides"]
    sx, sy = STAGE_C
    st = P("stage", "alu")
    zd = Z0 + STAGE_H
    dish = P("dish", "dish")
    if lod == 0:
        lathe(st, [(STAGE_R, 0.0), (STAGE_R, STAGE_H - 0.0022), (STAGE_R - 0.0012, STAGE_H - 0.0004),
                   (STAGE_R - 0.0030, STAGE_H)], n, (sx, sy, Z0), cap=1)
        # dish: a wall, a rolled rim, an inner wall, a bottom (the underside rests on the stand and is not
        # needed)
        lathe(dish, [(DISH_R, 0.0), (DISH_R, DISH_H - 0.0006), (DISH_R - 0.0007, DISH_H),
                     (DISH_R - 0.0013, 0.0012)], n, (sx, sy, zd), cap=1)
    else:
        g.cyl(st, (sx, sy, Z0 + STAGE_H / 2), "z", STAGE_R, STAGE_H, n)
        g.cyl(dish, (sx, sy, zd + DISH_H / 2), "z", DISH_R, DISH_H, n)
    rk = P("rock", "rock")
    floor = zd + (0.0012 if lod == 0 else DISH_H)     # dish bottom (in the middle LOD the dish is a disc)
    rock(rk, (sx + 0.002, sy - 0.001, floor + 0.0039), (0.012, 0.009, 0.007), 2 if lod == 0 else 1)
    return [st, dish, rk]


def build_lod(spec):
    parts = [brick(spec, e, i) for i, e in enumerate(BRICKS)] + build_plates(spec) + build_top_items(spec) + \
        build_sample(spec)
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("bounds: %s .. %s" % (tuple(round(c, 4) for c in BOUNDS["lo"]),
                                   tuple(round(c, 4) for c in BOUNDS["hi"])))
    return parts


def collision():
    """One convex hull: the masonry with the plates up to the top of the plate (the front cavity, the plug
    and the beacon do not matter for the item). The mass is the item weight in the mod, 0.8 kg; the sound
    and penetration are thick metal (castiron: the bullet does not pass). The preview and drop frame
    cover the whole item."""
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    pts = kx.box_pts(lo[0], hi[0], lo[1], hi[1], 0.0, ZP)
    comps = [(pts, kx.PEN + r"\castiron.rvmat")]
    memory = {
        # inventory preview camera: from the front left and above (invView is where the camera is)
        "invView": [(-0.28, -0.46, 0.40)],
        "ce_center": [(0.0, 0.0, 0.115)],
        "ce_radius": [(0.15, 0.0, 0.115)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


SHOTS = [
    ("front", (-0.16, -0.55, 0.32), (0.0, 0.0, 0.11), 40),
    ("left", (-0.46, -0.30, 0.30), (0.0, 0.0, 0.11), 40),
    ("inside", (0.03, -0.30, 0.14), (0.0, -0.01, 0.05), 45),
    ("top", (0.12, -0.26, 0.48), (0.0, -0.005, 0.19), 42),
    ("back", (0.40, 0.44, 0.32), (0.0, 0.0, 0.11), 40),
]
# --look preview: general view, the side with the sticker, the cavity, the plate from above; the "working"
# state uses the front and the left
M.look_shots = (4, 2)

M.run(build_lod, collision, SHOTS, row_step=0.32, row_shot=((0.16, -1.1, 0.35), (0.16, 0, 0.10)))
