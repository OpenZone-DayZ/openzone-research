"""M09 - lead cabinet with a manipulator: the Clear Sky Anomaly Packer (OZL_Sky_Pack_Anom).
Packer: cargo 10x10, three module places (module_1..3) and proxies for the modules at the same
places. Each module of the Anomaly line has its own slot and working place: slot 1 - probe-detector
M69 on a new small shelf under the hatch with the manipulator (they measure what they pull out with
the tongs; empty: the shelf and a coiled cable); slot 2 - dosimeter-radiometer M70 on a new small
shelf on the left side where the DP-5V was (the same kind of instrument: the DP-5V is gone, an empty
hook of its strap remains above the shelf); slot 3 - lead shield M71 on the right side shelf closer
to the hatch.

    blender --background --python build_m09.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (radiation sign, draft gauge scale, tag).

The cabinet is the B3 base: a double-door metal clothes cabinet of the 1970-90s, 800 x 1800 x 500 mm
(width x height x depth) - after catalogues of the same kind: ShMDO 900 x 1800 x 500, Garnelle
1850 x 800 x 500; the base is a photo of a bunker cabinet. The door layout is klocker.layout; the
cabinet itself is its own, more detailed than klocker.locker (the kit is not changed: the accepted
models are built on it): rounded edges of the body and doors, surface barrel hinges, turn handles on
spacers (the doors are clad) and a lock cylinder, bent louvre visors over the slots, feet of 40 x 40
tube with pads.

The rigging is a makeshift "hot cell" after photos (Heidelberg: lead blocks, inclined viewing
windows in boxes, a through manipulator with a pistol grip; and a cabinet lined with lead):
- cladding - 4 mm lead sheets on M10 bolts with a press washer (lead is soft): three overlapping rows
  of 40 mm on the doors, two rows on the left side, one on the right. The sheets are bent by hand:
  bulged between the rows of bolts (up to 8 mm), the free bottom edge waves (up to 9 mm), hammer
  dents, a dimple at each bolt, pressed flat under screwed-on parts;
- viewing window in the left door - an inclined lead box, thick clear glass, an opening through the
  door and the body face into the interior;
- interior (the upper compartment above the inner shelf at 0.92): a wall of lead bricks 200 x 100 x
  50 on edge at the back (as in the M71 module), an open lead container of diameter 120 x 130 with
  its lid, a sample tray, a lamp in a cage;
- hatch in the right door - on a flange frame, two hinges, a turn latch; in it a ball through-port
  (sizes from the photo and the DIN 25409-1 tongs / DIN 25407-2 ball bushing standards, not from a
  data sheet): a flange of diameter 132 on six bolts, a ball of diameter 90, a rod of diameter 18;
  outside a pistol grip with a trigger and a linkage, inside - tongs;
- on the left side two pairs of tongs on hooks (after the Mirion Niptongs 36", 91 cm) and an empty
  hook of the DP-5V strap;
- by the hatch a red signal lamp in a guard cage, a cable in clips over the top of the cabinet to a
  box on the roof (the power is in it); under the window the draft gauge (vacuum in the cabinet): a
  round radial-type case of diameter 60 mm, a scale with zero in the middle, a copper impulse tube
  into the door;
- radiation sign on the right door; on the roof a steel box with a blank inventory tag;
- the module shelf 0.26 x 0.68 m is welded to the right side at 0.92 m; the new shelves - under the
  hatch at 0.72 (0.36 x 0.21) and on the left side at 1.10 (0.23 x 0.26), on gussets, bolted through
  the lead;
- light blue Clear Sky enamel over the grey factory one, rust and dirt at the bottom.

Look: the "dayz" look (matte, dirtier, coloured AO); the DP-5V is removed (the M70 module takes its
place); vanilla DayZ items through proxies: a GP-5 gas mask on a hook under the right shelf; on the
right side above the shelf on a bar with hooks - an adjustable wrench, pliers, a screwdriver, a
hammer; on the right shelf behind the module - tape, a flashlight, two D batteries, a bottle of vodka.

Work look: the red lamp by the hatch is ozl_lamp (blinks); the upper compartment behind the window
(walls, shelf, bricks, container, tray, lamp) is ozl_light: in "work" it glows, a light burns
inside; the draft gauge needle is the bone ozl_needle on the source ozl_needle (sways near the
vacuum mark); the manipulator rod with tongs and the grip is the bone ozl_arm on the source ozl_arm:
in "work" it feeds 8 cm inward and the tongs take a sample from the tray (a pose, like the M16
head), after the work - back.

Blender axes: X is width, Y is depth (face toward -Y), Z is up.
"""
import math
import os
import random
import sys

import bmesh
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import klocker  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import krender  # noqa: E402
import kvanilla as kv  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
CX0, CX1, CY0, CY1 = -0.40, 0.40, -0.25, 0.25                # cabinet
H, FOOT = 1.80, 0.06                                         # top, feet
DOOR_T, GAP = klocker.DOOR_T, klocker.GAP
LAY = klocker.layout(CX0, CX1, CY0, H, FOOT)
DOORS = LAY["doors"]
YB = CY0 + DOOR_T                                            # body face behind the doors
T = 0.004                                                    # lead sheet
ROWS = ((0.24, 0.68), (0.64, 1.10), (1.06, 1.58))            # rows of sheets on the doors, bottom to top
LAP = 0.04                                                   # overlap of the rows
YR = [CY0 - T * k for k in range(3)]                         # back of the row-k sheet (the higher row lies on top)
YTOP = CY0 - 3 * T                                           # face of the top row
# viewing window in the left door: a box, the face tilted back (as in the reference photo)
WX, WW = (DOORS[0][0] + DOORS[0][1]) / 2, 0.13               # centre, half width
WZ0, WZ1 = 1.25, 1.47
WYB, WYT = -0.38, -0.32                                      # box face: bottom and top in y
WIN = 0.035                                                  # frame width
# interior: the upper compartment above the inner shelf (a cut in the body)
CHAMBER = (CX0 + 0.016, CX1 - 0.016, YB + 0.006, CY1 - 0.014, 0.92, H - 0.024)
# hatch with a ball port in the right door
HX, HZ, HS = 0.215, 1.00, 0.115                              # centre, half side of the opening
FR_Y0, FR_Y1 = YTOP + 0.003, YTOP - 0.008                    # flange frame: back and face
FR_W = 0.032                                                 # frame width around the opening
LID_Y1 = FR_Y1 - 0.012                                       # hatch face
BALL = Vector((HX, LID_Y1 - 0.010, HZ))                      # port ball centre
BALL_R = 0.045
TRAY = (0.10, 0.14)                                          # sample tray on the interior shelf
ARM_D = Vector((TRAY[0] - HX, TRAY[1] - BALL.y, 0.972 - HZ)).normalized()   # rod inward: tongs toward the sample
ARM_OUT, ARM_IN, ARM_TRAVEL = 0.21, 0.37, 0.08               # outward to the grip, inward to the tongs, feed
# radiation sign on the right door
SGX, SGZ, SGS = HX, 1.36, 0.08
SGY = YTOP - 0.006
# signal lamp by the hatch, draft gauge under the window
LAMP_X, LAMP_Z = 0.33, 1.20
GAUGE_X, GAUGE_Z, GAUGE_R = WX, 1.115, 0.032
GAUGE_FACE = YTOP - 0.029                                    # scale face
NEEDLE_MID, NEEDLE_ANG = 0.6, -0.9                           # needle: swing middle, angle at phase 1, rad
NEEDLE_AMP = 0.07                                            # swing amplitude (wobble amp)
# The needle axis is given by memory points (collision). The engine rotates a bone right-handed in
# DayZ axes (kexport.conv, determinant -1); in Blender axes that is a left-handed rotation about the
# axis from the first point to the second: the axis looks at the person, a positive angle is clockwise
# for them, a negative one counter-clockwise (as in M08, M12, M14, M33, whose needles are right in
# game). An axis pointing from the face into the cabinet would send the needle to the right, toward
# "+" (pressure), instead of to the left, into the red vacuum zone as in the preview. So the axis
# points to the person (-Y) and a negative angle goes left.
NEEDLE_AXIS = [(GAUGE_X, GAUGE_FACE, GAUGE_Z), (GAUGE_X, GAUGE_FACE - 0.1, GAUGE_Z)]
# left side: tongs on hooks, an empty hook of the DP-5V strap
TONGS = ((-0.19, 1.66), (-0.085, 1.60))                      # (y, z of the hook)
STRAP_HOOK = (0.127, 1.44)
# module shelf on the right side (slot 3), the new ones - under the hatch (slot 1) and on the left side (slot 2)
SX0, SX1, SY0, SY1, SZ = CX1, CX1 + 0.26, -0.34, 0.34, 0.92
FS = (0.03, 0.385, YR[1] - T - 0.001, -0.465, 0.72)          # x0, x1, back (on the sheet), face, top
LS = (CX0, CX0 - 0.23, -0.015, 0.245, 1.10)                  # x at the wall, x of the edge, y0, y1, top
MODS = [(0.24, -0.355, FS[4]), (CX0 - 0.015 - 0.083, 0.115, LS[4]), (0.535, -0.225, SZ)]
MOD_OBJ = [("m69_anom_probe", "ozr_anom_probe"), ("m70_radiometer", "ozr_radiometer"),
           ("m71_lead_shield", "ozr_lead_shield")]
# bar with tools on the right side above the shelf
RACK_Z, RACK_Y = 1.62, (-0.15, -0.055, 0.035, 0.135)
# box on the roof
BX0, BX1, BY0, BY1, BZ1 = -0.30, 0.20, -0.16, 0.14, H + 0.19

LOD_SPECS = [
    dict(lod=0, bev=1, sides=16),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "lk": ("enamel", 0.6), "lk_door": ("enamel_door", 0.6), "vent": ("dark", 0.3), "foot": ("dark", 0.4),
    "pad": ("rubber", 0.3), "steel": ("steel", 0.8), "hinge": ("hinge", 0.8), "bolt": ("bolt", 0.12),
    "lead": ("lead", 0.6), "lead_box": ("lead_box", 0.8), "sign": ("sign", 1.5), "tongs": ("steel", 0.6),
    "grip": ("black", 0.9), "ball": ("chrome", 0.8), "shelf": ("enamel_shelf", 0.8), "box": ("box", 0.8),
    "cable": ("rubber", 0.5), "lamp": ("lamp", 1.2), "lamp_body": ("lamp_body", 1.0), "gauge": ("gauge", 1.2),
    "dial": ("dial", 6.0), "needle": ("needle", 1.0), "copper": ("copper", 0.8), "wire": ("steel", 0.4),
    # cabinet interior (ozl_light): its own looks - they glow in "work" (atlas _on)
    "inner": ("inner", 0.18), "inner_floor": ("inner_floor", 0.3), "brick": ("lead_in", 0.4),
    "pot": ("lead_in", 0.5), "tray": ("steel_in", 0.6), "sample": ("sample", 1.0), "bulb": ("bulb", 1.0),
    "bulb_base": ("steel_in", 0.6),
}

# =============================================================================
# Materials
# =============================================================================


def decal(name, ax, sign, uv, center, size, face, eps=0.003):
    return (os.path.join(WORK, name), ax, sign, uv, center, size, (face - eps, face + eps))


KINDS = kmats.std_kinds(floor_z=0.0)
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# light blue Clear Sky enamel over the grey factory paint of the cabinet: grey and rust in the chips,
# rust and dirt at the bottom
BLUE = dict(color=kmats.lin((150, 192, 214)), under=kmats.lin((128, 132, 130)), seed=2.6, gloss=0.40, spec=0.30,
            chip=(0.57, 0.63), rust=(0.64, 0.72), rust_low=1.0, floor_z=0.0, dust=0.3, grime=1.0)
LEAD = dict(color=kmats.lin((100, 103, 106)), under=kmats.lin((168, 170, 172)), seed=6.1, gloss=0.22, spec=0.25,
            chip=(0.67, 0.72), rust=(0.99, 1.0), rust_low=0.0, dust=0.4, grime=0.6, yellow=0.14)
INNER = dict(color=kmats.lin((92, 96, 94)), under=kmats.lin((70, 60, 50)), seed=12.1, gloss=0.3, spec=0.2,
             chip=(0.66, 0.72), rust=(0.70, 0.78), rust_low=0.0, floor_z=0.92, dust=0.3, grime=0.6)
# in "work" a lamp burns inside: the same surfaces are lighter and warmer (atlas _on, glowing)
WARM = kmats.lin((255, 236, 196))


def lit(c, k=1.9):
    return tuple(min(1.0, a * k * w) for a, w in zip(c[:3], WARM[:3])) + (1.0,)


KINDS.update({
    "enamel": ("paint", BLUE),
    "enamel_door": ("paint", dict(BLUE, seed=3.1)),
    "enamel_shelf": ("paint", dict(BLUE, seed=4.7, chip=(0.56, 0.62), dust=0.3, grime=0.3)),
    "dark": ("flat", dict(color=kmats.lin((22, 23, 24)), gloss=0.2, spec=0.1)),
    # lead: dull grey, light in the scratches, whitish oxide patches, does not rust
    "lead": ("paint", LEAD),
    "lead_box": ("paint", dict(LEAD, seed=6.7, chip=(0.66, 0.72))),
    "bolt": ("steel", dict(seed=7.3, tone=0.22, along="z", dust=0.3, grime=0.5)),
    "hinge": ("paint", dict(BLUE, seed=7.9, chip=(0.52, 0.58), rust=(0.60, 0.68))),
    "chrome": ("steel", dict(seed=8.1, tone=0.42, along="z", gloss=0.7, spec=0.8, dust=0.15, grime=0.2)),
    "sign": ("paint", dict(CLEAN, color=kmats.lin((226, 184, 30)), gloss=0.4, spec=0.3, dust=0.1,
                           decal_items=[decal("decal_trefoil.png", "y", -1, ("x", "z"), (SGX, SGZ), (2 * SGS, 2 * SGS),
                                              SGY)])),
    "lamp": ("flat", dict(color=kmats.lin((120, 22, 18)), gloss=0.85, spec=0.8)),
    "lamp_on": ("flat", dict(color=kmats.lin((255, 60, 40)), gloss=0.85, spec=0.8)),
    "lamp_body": ("paint", dict(color=kmats.lin((40, 42, 40)), under=kmats.lin((120, 120, 116)), seed=8.5, gloss=0.3,
                                spec=0.25, chip=(0.66, 0.72), rust=(0.70, 0.78), rust_low=0.0, dust=0.3, grime=0.3)),
    "gauge": ("paint", dict(color=kmats.lin((34, 34, 34)), under=kmats.lin((140, 140, 136)), seed=9.3, gloss=0.35,
                            spec=0.3, chip=(0.64, 0.70), rust=(0.99, 1.0), rust_low=0.0, dust=0.2, grime=0.2)),
    "dial": ("paint", dict(CLEAN, color=kmats.lin((232, 228, 214)), gloss=0.6, spec=0.4,
                           decal_items=[decal("decal_gauge.png", "y", -1, ("x", "z"), (GAUGE_X, GAUGE_Z),
                                              (2 * GAUGE_R * 0.92, 2 * GAUGE_R * 0.92), GAUGE_FACE)])),
    "needle": ("flat", dict(color=kmats.lin((20, 20, 20)), gloss=0.5, spec=0.3)),
    "copper": ("paint", dict(color=kmats.lin((176, 104, 66)), under=kmats.lin((80, 110, 90)), seed=9.7, gloss=0.5,
                             spec=0.5, chip=(0.55, 0.62), rust=(0.99, 1.0), rust_low=0.0, dust=0.2, grime=0.4)),
    "box": ("paint", dict(color=kmats.lin((112, 118, 116)), under=kmats.lin((70, 50, 36)), seed=5.9, gloss=0.35,
                          spec=0.25, chip=(0.60, 0.66), rust=(0.64, 0.72), rust_low=0.0, dust=0.5, grime=0.3,
                          decal_items=[decal("decal_tag.png", "y", -1, ("x", "z"), (-0.12, H + 0.13), (0.10, 0.04),
                                             BY0)])),
    # interior: walls and shelf in grey primer, lead, tray, sample (green-grey stone), lamp
    "inner": ("paint", INNER),
    "inner_on": ("paint", dict(INNER, color=lit(INNER["color"]))),
    "inner_floor": ("paint", dict(INNER, seed=12.7, color=kmats.lin((84, 86, 84)))),
    "inner_floor_on": ("paint", dict(INNER, seed=12.7, color=lit(kmats.lin((84, 86, 84))))),
    "lead_in": ("paint", dict(LEAD, seed=13.3, floor_z=0.92)),
    "lead_in_on": ("paint", dict(LEAD, seed=13.3, floor_z=0.92, color=lit(LEAD["color"]))),
    "steel_in": ("steel", dict(seed=13.9, tone=0.28, along="x", floor_z=0.92, dust=0.2, grime=0.3)),
    "steel_in_on": ("steel", dict(seed=13.9, tone=0.55, along="x", floor_z=0.92, dust=0.2, grime=0.3)),
    "sample": ("plastic", dict(color=kmats.lin((88, 104, 72)), gloss=0.3, spec=0.2, mottle=0.35, dust=0.1, grime=0.5)),
    "sample_on": ("plastic", dict(color=kmats.lin((150, 210, 110)), gloss=0.3, spec=0.2, mottle=0.35, dust=0.1,
                                  grime=0.5)),
    "bulb": ("flat", dict(color=kmats.lin((200, 196, 184)), gloss=0.7, spec=0.6)),
    "bulb_on": ("flat", dict(color=kmats.lin((255, 246, 214)), gloss=0.7, spec=0.6)),
})

OBJ, NAME = "m09_sky_pack_anom", "ozr_sky_pack_anom"
# Work look: the lamp by the hatch is ozl_lamp (blinks), the interior behind the window is ozl_light
# (glows), the needle is the bone ozl_needle (sways), the manipulator rod is the bone ozl_arm (pose:
# feeds inward).
SEL_LAMP, SEL_LIGHT, SEL_NEEDLE, SEL_ARM = "ozl_lamp", "ozl_light", "ozl_needle", "ozl_arm"
ON = dict(remap={"lamp": "lamp_on", "inner": "inner_on", "inner_floor": "inner_floor_on", "lead_in": "lead_in_on",
                 "steel_in": "steel_in_on", "sample": "sample_on", "bulb": "bulb_on"},
          emissive=(1.0, 1.0, 1.0, 1.0), move={SEL_ARM: tuple(ARM_D * ARM_TRAVEL)})
NEEDLE_ANIM = ("ozl_gauge_needle", dict(type="rotation", source=SEL_NEEDLE, selection=SEL_NEEDLE,
                                        axis="ozl_needle_axis", memory=1, minValue=0.0, maxValue=1.0, angle0=0.0,
                                        angle1=NEEDLE_ANG))
# feed axis - a metre along the rod inward from the ball centre: offset in metres
ARM_ANIM = ("ozl_arm_feed", dict(type="translation", source=SEL_ARM, selection=SEL_ARM, axis="ozl_arm_axis",
                                 memory=1, minValue=0.0, maxValue=1.0, offset0=0.0, offset1=ARM_TRAVEL))
# proxies for the modules: the mod's CfgNonAIVehicles binds slots OZL_Tool1..3 to them (Proxyozl_tool1..3);
# slot N is module N of the Anomaly line (M69, M70, M71), no rotation: the module face looks along the cabinet face
PROXIES = [(r"\OpenZone_Research\models\proxies\ozl_tool%d" % (i + 1), m) for i, m in enumerate(MODS)]


def tool_hung(key, y, top, x=CX1 + 0.005):
    """Tool on the bar of the right side: working end down, facing out (+x), the top at top."""
    lo, hi = kv.box(key)
    return kv.put(key, (x, y, top - (hi[1] - lo[1]) / 2), up=(0, 0, -1), fwd=(1, 0, 0), normal=(1, 0, 0))


# vanilla items
DECOR = [
    # GP-5 gas mask on a hook under the right shelf, facing out
    kv.put("gp5", (CX1 + T + 0.014, 0.0, 0.50), up=(0, 0, 1), fwd=(1, 0, 0), normal=(1, 0, 0)),
    # bar above the right shelf: wrench, pliers, screwdriver, hammer
    tool_hung("wrench", RACK_Y[0], RACK_Z + 0.006),
    tool_hung("pliers", RACK_Y[1], RACK_Z + 0.006),
    tool_hung("screwdriver", RACK_Y[2], RACK_Z + 0.006),
    tool_hung("hammer", RACK_Y[3], RACK_Z + 0.006),
    # right shelf behind the module: tape, flashlight, D batteries, vodka
    kv.put("ducttape", (0.48, -0.058, SZ), **kv.flat(0)),
    kv.put("flashlight", (0.615, -0.03, SZ), **kv.flat(0)),
    kv.put("batteryd", (0.45, 0.10, SZ), up=(0, 0, 1), fwd=(0, -1, 0)),
    kv.put("batteryd", (0.452, 0.19, SZ), up=(0, 0, 1), fwd=(0.3, -1, 0)),
    kv.put("vodka", (0.60, 0.22, SZ), up=(0, 0, 1), fwd=(0, -1, 0)),
]
SOURCES = {SEL_NEEDLE: dict(animPeriod=0.2), SEL_ARM: dict(animPeriod=1.5)}
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.86, 0.85, 0.74), clear=0.015, edge=0.10, smudge=0.02, streaks=0.01),
                 selections=(SEL_LAMP, SEL_LIGHT, SEL_NEEDLE, SEL_ARM), hidden=(SEL_LAMP, SEL_LIGHT),
                 states={"on": ON}, bones=((SEL_NEEDLE, ""), (SEL_ARM, "")), animations=(NEEDLE_ANIM, ARM_ANIM),
                 proxies=PROXIES, decor=DECOR, sources=SOURCES,
                 modules=[(o, n, m) for (o, n), m in zip(MOD_OBJ, MODS)])
P = M.part
BOUNDS = {}


# =============================================================================
# Primitives missing from kgeo
# =============================================================================
def face(part, verts, want):
    """Face from bmesh vertices, turned toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    part.tag([f])
    return f


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


def perp(axis):
    """Two axes perpendicular to axis: (axis, u, v) - a right-handed triple; for axis = -y u = +x, v = +z."""
    a = Vector(axis).normalized()
    r = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    u = r.cross(a).normalized()
    return u, a.cross(u).normalized()


def lathe(part, prof, sides, origin, axis=(0, 0, 1), cap0=False, cap1=False, phase=0.5):
    """Body of revolution about axis through origin: prof [(r, h)] - radius and distance along the axis.
    A ring with r = 0 is a pole. Faces look outward along the profile (a reversed profile - inward);
    cap0, cap1 - flat ends of the first and last ring."""
    bm = part.bm
    a = Vector(axis).normalized()
    u, v = perp(a)
    o = Vector(origin)

    def ring(r, h):
        c = o + a * h
        if r < 1e-7:
            return [bm.verts.new(c)]
        return [bm.verts.new(c + (u * math.cos(2 * math.pi * (k + phase) / sides) +
                                  v * math.sin(2 * math.pi * (k + phase) / sides)) * r) for k in range(sides)]
    rings = [ring(r, h) for r, h in prof]
    new = []
    for i in range(len(prof) - 1):
        dr, dh = prof[i + 1][0] - prof[i][0], prof[i + 1][1] - prof[i][1]
        A, B = rings[i], rings[i + 1]
        if len(A) == 1 and len(B) == 1:
            continue
        for k in range(sides):
            j = (k + 1) % sides
            if len(A) == 1:
                q = [A[0], B[j], B[k]]
            elif len(B) == 1:
                q = [A[k], A[j], B[0]]
            else:
                q = [A[k], A[j], B[j], B[k]]
            f = bm.faces.new(q)
            f.normal_update()
            c = sum((x.co for x in q), Vector()) / len(q) - o
            rad = c - a * c.dot(a)
            rad = rad.normalized() if rad.length > 1e-9 else u
            if f.normal.dot(rad * dh - a * dr) < 0:
                f.normal_flip()
            new.append(f)
    for cap, rg, sgn in ((cap0, rings[0], -1), (cap1, rings[-1], 1)):
        if cap and len(rg) > 2:
            d = prof[1][1] - prof[0][1] if sgn < 0 else prof[-1][1] - prof[-2][1]
            f = bm.faces.new(rg)
            f.normal_update()
            if f.normal.dot(a * (sgn * (1 if d >= 0 else -1))) < 0:
                f.normal_flip()
            new.append(f)
    part.tag(new)
    return new


def rod(part, a, b, r, sides, cap=True):
    """Cylinder between points a and b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    return lathe(part, [(r, 0.0), (r, d.length)], sides, a, d, cap0=cap, cap1=cap)


def ball(part, c, r, sides, axis=(0, 0, 1), hole=0.0, rings=6):
    """Ball (hole > 0 - with holes for the rod at the poles of axis)."""
    t0 = math.asin(min(0.95, hole / r)) if hole > 0 else 0.0
    prof = [(r * math.sin(t0 + (math.pi - 2 * t0) * i / rings), -r * math.cos(t0 + (math.pi - 2 * t0) * i / rings))
            for i in range(rings + 1)]
    return lathe(part, prof, sides, c, axis)


def rrect(c, u, v, w, h, r, k):
    """Rounded rectangle w x h in the (u, v) plane centred at c: 4 (k + 1) points counter-clockwise (k = 0
    or r = 0 - sharp corners, 4 points)."""
    c, u, v = Vector(c), Vector(u), Vector(v)
    if k <= 0 or r <= 0:
        return [c + u * (sx * w / 2) + v * (sy * h / 2) for sx, sy in ((1, -1), (1, 1), (-1, 1), (-1, -1))]
    pts = []
    for sx, sy, a0 in ((1, -1, -90), (1, 1, 0), (-1, 1, 90), (-1, -1, 180)):
        cx, cy = sx * (w / 2 - r), sy * (h / 2 - r)
        for i in range(k + 1):
            t = math.radians(a0 + 90.0 * i / k)
            pts.append(c + u * (cx + r * math.cos(t)) + v * (cy + r * math.sin(t)))
    return pts


def verts(part, pts):
    return [part.bm.verts.new(Vector(p)) for p in pts]


def bridge(part, A, B, want):
    """Ring of quads between vertex loops A and B of equal length; want is a vector or want(centre)."""
    new = []
    n = len(A)
    for i in range(n):
        j = (i + 1) % n
        q = [A[i], A[j], B[j], B[i]]
        f = part.bm.faces.new(q)
        f.normal_update()
        c = sum((x.co for x in q), Vector()) / 4
        w = want(c) if callable(want) else Vector(want)
        if f.normal.dot(w) < 0:
            f.normal_flip()
        new.append(f)
    part.tag(new)
    return new


def fill(part, A, want):
    return face(part, A, want)


def radial(p0, axis, outward=True):
    """want(c) for walls around an axis: away from the axis (or toward it)."""
    p0, a = Vector(p0), Vector(axis).normalized()

    def w(c):
        d = c - p0
        d -= a * d.dot(a)
        return d if outward else -d
    return w


def bprism(part, poly, axes, c0, c1, r, seg=1, frame=None):
    """g.prism with rounded edges (r is the chamfer radius, seg - segments)."""
    bm = part.bm
    before = set(bm.faces)
    fs = g.prism(part, poly, axes, c0, c1, frame=frame)
    if r > 0 and seg > 0:
        g.bevel(bm, list({e for f in fs for e in f.edges}), r, seg)
    new = [f for f in bm.faces if f not in before]
    bmesh.ops.recalc_face_normals(bm, faces=new)
    part.tag(new)
    return new


def rbox(part, x0, x1, y0, y1, z0, z1, r, seg):
    """Box; on the near LOD with rounded edges."""
    return g.box(part, x0, x1, y0, y1, z0, z1, **(dict(r=r, seg=seg) if seg > 0 and r > 0 else {}))


def screw(part, c, n, r=0.0045, h=0.002, sides=6):
    """Screw or rivet head along the normal n: a low dome (the bottom toward the sheet, no end cap)."""
    return lathe(part, [(r, 0.0), (r, h * 0.45), (0.0, h)], sides, c, n)


def bolt(head, washer, c, n, lod):
    """M10 bolt with a 17 mm hex head (with a press washer - lead is soft) and a rounded top; washer - the
    washer part of diameter 24 (only on shelves, where there are few bolts)."""
    n = Vector(n).normalized()
    if washer is not None:
        lathe(washer, [(0.012, -0.0005), (0.0095, 0.0016)], 8, c, n)
    lathe(head, [(0.0095, -0.0005), (0.0095, 0.0038), (0.0, 0.0058)], 6, c, n, phase=0.0)


def hook(part, base, out, up, sides, reach=0.045, rise=0.035, r=0.004):
    """Hook of rod welded to a wall: from the wall along out, bent up along up; a heel washer at the wall."""
    b, o, u = Vector(base), Vector(out).normalized(), Vector(up).normalized()
    pts = [b - o * 0.002, b + o * reach * 0.55, b + o * reach * 0.9 + u * 0.004, b + o * reach + u * rise * 0.45,
           b + o * reach * 0.96 + u * rise]
    g.pipe(part, spline(pts, 2) if sides > 4 else pts, r, sides)
    if sides > 4 and r >= 0.004:
        lathe(part, [(r * 2.4, 0.0), (r * 2.4, 0.003), (r * 1.2, 0.004)], 6, b - o * 0.001, o)


def split_regions(part, regions, name, group):
    """Faces of the regions regions go into a new part name with group group (the interior cut in the body)."""
    out = g.Part(name, group=group)
    vm = {}
    moved = [f for f in part.bm.faces if part.regions[f[part.reg]][0] in regions]
    for f in moved:
        rn, kind, sc = part.regions[f[part.reg]]
        idx = out.region_index(rn, kind, sc)
        vs = []
        for v in f.verts:
            if v not in vm:
                vm[v] = out.bm.verts.new(v.co)
            vs.append(vm[v])
        nf = out.bm.faces.new(vs)
        nf[out.reg] = idx
    bmesh.ops.delete(part.bm, geom=moved, context="FACES")
    out.bm.normal_update()
    return out


# =============================================================================
# Cabinet (B3 base, its own, more detailed than klocker.locker)
# =============================================================================
def window_geom():
    """Window box: the face (centre fc, axes ux and vf along the face, out - outward, height hf), the back centre
    bc."""
    fo0, fo3 = Vector((WX, WYB, WZ0)), Vector((WX, WYT, WZ1))
    vf = (fo3 - fo0).normalized()
    ux = Vector((1, 0, 0))
    return dict(fc=(fo0 + fo3) / 2, ux=ux, vf=vf, out=ux.cross(vf).normalized(), hf=(fo3 - fo0).length,
                bc=Vector((WX, YTOP + 0.002, (WZ0 + WZ1) / 2)))


def glass_loop(k):
    w = window_geom()
    return rrect(w["fc"] - w["out"] * 0.012, w["ux"], w["vf"], 2 * WW - 2 * WIN, w["hf"] - 2 * WIN, 0.006, k)


def opening():
    """Window opening in the x, z axes (by the glass, the opening is straight along y) - shared by the box,
    sheet, door and body."""
    pts = glass_loop(0)
    return min(p.x for p in pts), max(p.x for p in pts), min(p.z for p in pts), max(p.z for p in pts)


OPEN = opening()


def build_cabinet(spec):
    lod = spec["lod"]
    k = 2 if lod == 0 else 0
    parts = []
    # --- body: on near and middle LODs with the upper compartment cut and the window opening
    bd = P("lk_body", "lk")
    if lod == 2:
        g.box(bd, CX0, CX1, YB, CY1, 0.0, H)
        parts.append(bd)
    else:
        rbox(bd, CX0, CX1, YB, CY1, FOOT, H, 0.006, k)
        x0, x1, y0, y1, z0, z1 = CHAMBER
        ch = P("cut_chamber", "inner")
        g.box(ch, x0, x1, y0, y1, z0, z1)
        for f in ch.bm.faces:
            if f.normal.z < -0.5:
                f[ch.reg] = ch.region_index("inner_floor", *REGIONS["inner_floor"])
        op = P("cut_open", "inner")
        g.box(op, OPEN[0] - 0.005, OPEN[1] + 0.005, CY0 - 0.06, y0 + 0.01, OPEN[2] - 0.005, OPEN[3] + 0.005)
        bd = M.boolean("lk_body_l%d" % lod, bd, [ch, op])
        bd.uv_name = "lk_body"                     # middle LOD - the same atlas places as the near one
        chm = split_regions(bd, ("inner", "inner_floor"), "chamber_l%d" % lod, SEL_LIGHT)
        chm.uv_name = "chamber"
        parts += [chm, bd]
        # feet of 40 x 40 tube, pads
        ft, pd = P("lk_feet", "foot"), P("lk_pads", "pad")
        for x in (CX0 + 0.015, CX1 - 0.055):
            for y in (YB + 0.01, CY1 - 0.05):
                g.box(ft, x, x + 0.04, y, y + 0.04, 0.006, FOOT + 0.002)
                g.box(pd, x - 0.002, x + 0.042, y - 0.002, y + 0.042, 0.0, 0.006)
        parts += [ft, pd]

    # --- doors (the left one has the window opening)
    if lod == 2:
        dr = P("lk_doors", "lk_door")
        (xa, _, za, zb), (_, xb, _, _) = DOORS
        g.box(dr, xa, xb, CY0, YB + 0.002, za, zb)
        return parts + [dr]
    for i, (xa, xb, za, zb) in enumerate(DOORS):
        dr = P("lk_door%d_l%d" % (i, lod), "lk_door")
        rbox(dr, xa, xb, CY0, YB + 0.002, za, zb, 0.004, k)
        if i == 0:
            op = P("cut_door", "lk_door")
            g.box(op, OPEN[0] - 0.005, OPEN[1] + 0.005, CY0 - 0.02, YB + 0.02, OPEN[2] - 0.005, OPEN[3] + 0.005)
            dr = M.boolean("lk_door0_l%d" % lod, dr, [op])
        dr.uv_name = "lk_door%d" % i
        parts.append(dr)

    # --- slots: a dark slit, over it a bent visor (dark underneath - the opening shows)
    vt = P("lk_vents", "vent")
    lv = P("lk_louvers", "lk_door") if lod == 0 else None
    for xa, xb, _, _ in DOORS:
        xc = (xa + xb) / 2
        for zc in LAY["vents"]:
            for kk in ((-1, 0, 1) if lod == 0 else (0,)):
                z = zc + kk * 0.026
                g.box(vt, xc - 0.07, xc + 0.07, CY0 - 0.0008, CY0 + 0.001, z - 0.006, z + 0.006)
                if lv is not None:
                    arc = [(CY0 + 0.0005, z + 0.0085)] + [
                        (CY0 - 0.0075 * math.sin(math.pi / 2 * i / 4), z + 0.0085 - 0.0135 * (1 - math.cos(math.pi / 2 * i / 4)))
                        for i in range(1, 5)] + [(CY0 - 0.0068, z - 0.0055), (CY0 + 0.0005, z - 0.0045)]
                    fs = bprism(lv, arc, (1, 2), xc - 0.072, xc + 0.072, 0.0, 0)
                    for f in fs:
                        if f.normal.z < -0.7:
                            f[lv.reg] = lv.region_index("vent", *REGIONS["vent"])
    parts.append(vt)
    if lv is not None:
        parts.append(lv)

    # --- surface barrel hinges on the outer edges: three knuckles, an axle, axle heads
    if lod == 0:
        hg = P("lk_hinges", "hinge")
        for (xa, xb, za, zb), xe in zip(DOORS, (CX0 + 0.004, CX1 - 0.004)):
            for z in (za + 0.12, (za + zb) / 2, zb - 0.12):
                lathe(hg, [(0.0068, -0.045), (0.0068, 0.045)], 8, (xe, CY0 - 0.0015, z), (0, 0, 1), cap0=True,
                      cap1=True)
                lathe(hg, [(0.0035, 0.0), (0.0035, 0.0035), (0.0, 0.005)], 6, (xe, CY0 - 0.0015, z + 0.045), (0, 0, 1))
        parts.append(hg)

    # --- turn handles on spacers (the doors are clad with lead); a lock cylinder above the handle of the right door
    hd = P("lk_handles", "steel")
    zh = LAY["handle_z"]
    yf = YTOP - 0.001                                       # back of the plate is on the sheet
    for (xa, xb, _, _), s in zip(DOORS, (-1, 1)):
        xh = (xb - 0.05) if s < 0 else (xa + 0.05)
        g.box(hd, xh - 0.011, xh + 0.011, yf, CY0 + 0.001, zh - 0.045, zh + 0.08)        # spacer through the lead
        pl = rrect((xh, yf - 0.002, zh + 0.018), (1, 0, 0), (0, 0, 1), 0.036, 0.13, 0.008, 1 if lod == 0 else 0)
        A = verts(hd, [p + Vector((0, 0.002, 0)) for p in pl])
        B = verts(hd, [p + Vector((0, -0.002, 0)) for p in pl])
        bridge(hd, A, B, radial((xh, 0, zh), (0, 1, 0)))
        fill(hd, B, (0, -1, 0))
        # hub and lever: a flat strip with rounded ends, down from the hub
        lathe(hd, [(0.012, 0.0), (0.012, 0.008), (0.0, 0.0125)], 10 if lod == 0 else 6,
              (xh, yf - 0.004, zh + 0.025), (0, -1, 0))
        lever = [(xh - 0.008, zh + 0.03), (xh + 0.008, zh + 0.03), (xh + 0.007, zh - 0.050), (xh + 0.004, zh - 0.058),
                 (xh - 0.004, zh - 0.058), (xh - 0.007, zh - 0.050)]
        bprism(hd, lever, (0, 2), yf - 0.021, yf - 0.013, 0.002 if lod == 0 else 0.0, 1)
        if s > 0 and lod == 0:
            lathe(hd, [(0.0085, 0.0), (0.0085, 0.010), (0.0, 0.011)], 10, (xh, yf - 0.004, zh + 0.063),
                  (0, -1, 0))
    parts.append(hd)
    if lod == 0:
        ks = P("lk_keyway", "vent")
        xh = DOORS[1][0] + 0.05
        g.box(ks, xh - 0.0012, xh + 0.0012, yf - 0.0153, yf - 0.0143, zh + 0.057, zh + 0.069)
        parts.append(ks)
    return parts


# =============================================================================
# Lead cladding: curved sheets, bolts with washers
# =============================================================================
def smooth01(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


class Sheet:
    """Curved 4 mm lead sheet: o is the corner, u and v are the edges (full-length vectors), n is outward.
    The sheet is bulged between the rows of bolts, the free bottom edge waves off between the bolts,
    dents; pulled in a dimple at the bolts. flat - rectangles in the sheet axes (m from the corner: x0,
    x1, y0, y1) where something flat is screwed on - there it is pressed. under - how much of the bottom
    lies on the sheet of the row below (overlap: there bolts go through both sheets), cover - how much
    of the top is covered by the row above (there it is flat and without bolts). hole - an opening
    (x0, x1, y0, y1) in the sheet axes."""

    def __init__(self, o, u, v, n, seed, bulge=0.012, wave=0.012, under=0.0, cover=0.0, flat=(), hole=None,
                 dents=3, warped=True):
        self.o, self.n = Vector(o), Vector(n).normalized()
        self.W, self.Hh = Vector(u).length, Vector(v).length
        self.ue, self.ve = Vector(u).normalized(), Vector(v).normalized()
        self.bulge, self.wave, self.seed = bulge, wave, seed
        self.under, self.cover = under, cover
        self.hole, self.warped = hole, warped
        self.flat = list(flat)
        # bolts: across the width - at the edges and in the middle; in height - in the overlap at the bottom
        # (or at the bottom edge) and at the top edge, if the row above does not cover it
        self.ba = [0.05, 0.5, 0.95]
        self.bb = [(under / 2 if under > 0 else 0.03) / self.Hh] + ([] if cover > 0 else [1 - 0.03 / self.Hh])
        rnd = random.Random(seed)
        self.dents = [(rnd.uniform(0.15, 0.85) * self.W, rnd.uniform(0.25, 0.8) * self.Hh, rnd.uniform(0.02, 0.045),
                       rnd.uniform(0.002, 0.0045)) for _ in range(dents)]
        # one bottom corner is bent out (lead is soft: someone caught it and it came away)
        self.dog = (rnd.choice((0.0, 1.0)), rnd.uniform(0.007, 0.012))

    def local(self, p):
        d = Vector(p) - self.o
        return d.dot(self.ue), d.dot(self.ve)

    def flat_box(self, lo, hi, pad=0.004):
        """Press the sheet under an object with envelope lo..hi (world points)."""
        xs, ys = zip(*[self.local((x, y, z)) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
        self.flat.append((min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad))

    def warp(self, a, b):
        if not self.warped:
            return 0.0
        x, y = a * self.W, b * self.Hh
        b_lo = self.bb[0]
        b_hi = self.bb[1] if len(self.bb) > 1 else 1 - self.cover / self.Hh
        w = 0.0
        if b_lo < b < b_hi:
            t = (b - b_lo) / (b_hi - b_lo)
            w += self.bulge * math.sin(math.pi * t) * (0.62 + 0.38 * math.sin(math.pi * a)) * \
                (1 + 0.3 * math.sin(2.3 * math.pi * a + self.seed) * math.sin(1.7 * math.pi * t + 0.5 * self.seed))
        if b < b_lo:
            t = 1 - b / b_lo
            if 0.05 <= a <= 0.95:
                s = abs(math.sin(math.pi * (a - 0.05) / 0.45))
            else:
                s = 0.55
            w += self.wave * t * t * s * (0.8 + 0.2 * math.sin(3.1 * a + self.seed))
        for dx, dy, r, dep in self.dents:
            w -= dep * math.exp(-((x - dx) ** 2 + (y - dy) ** 2) / (r * r))
        ca, amp = self.dog
        dc = math.hypot(x - ca * self.W, y)
        w += amp * max(0.0, 1 - dc / 0.09) ** 2
        dmin = min(math.hypot(x - ba * self.W, y - bb * self.Hh) for ba in self.ba for bb in self.bb)
        w *= 1 - math.exp(-(dmin / 0.026) ** 2)
        m = 1.0
        if self.cover > 0:
            m = min(m, smooth01((self.Hh - self.cover - y) / 0.03))
        for x0, x1, y0, y1 in self.flat:
            d = math.hypot(max(x0 - x, 0.0, x - x1), max(y0 - y, 0.0, y - y1))
            m = min(m, smooth01(d / 0.03))
        return max(w * m, -0.0015)

    def at(self, a, b, off=T):
        return self.o + self.ue * (a * self.W) + self.ve * (b * self.Hh) + self.n * (self.warp(a, b) + off)

    def lines(self, n, extra, length):
        """Grid lines 0..1: uniform and mandatory (bolts, opening), without ones that are too close."""
        keep = sorted({round(e, 6) for e in extra if 0.0 < e < 1.0})
        res = [0.0, 1.0] + keep
        for i in range(1, n):
            t = i / n
            if all(abs(t - e) > 0.35 / n for e in keep):
                res.append(t)
        return sorted(set(res))

    def build(self, part, nu, nv):
        bm = part.bm
        ea, eb = (list(self.ba), list(self.bb)) if self.warped else ([], [])
        if self.cover > 0 and self.warped:
            eb.append(1 - self.cover / self.Hh)
        if self.hole:
            hx0, hx1, hy0, hy1 = self.hole
            ea += [hx0 / self.W, hx1 / self.W]
            eb += [hy0 / self.Hh, hy1 / self.Hh]
        A, B = self.lines(nu, ea, self.W), self.lines(nv, eb, self.Hh)
        front = [[bm.verts.new(self.at(a, b)) for b in B] for a in A]
        back = {}

        def bk(i, j):
            if (i, j) not in back:
                back[(i, j)] = bm.verts.new(self.at(A[i], B[j], 0.0))
            return back[(i, j)]

        def in_hole(i, j):
            if not self.hole:
                return False
            am, bmid = (A[i] + A[i + 1]) / 2 * self.W, (B[j] + B[j + 1]) / 2 * self.Hh
            return self.hole[0] < am < self.hole[1] and self.hole[2] < bmid < self.hole[3]
        for i in range(len(A) - 1):
            for j in range(len(B) - 1):
                if in_hole(i, j):
                    continue
                face(part, [front[i][j], front[i + 1][j], front[i + 1][j + 1], front[i][j + 1]], self.n)
                # back - only where the sheet has come away from the base (visible from below under the edge)
                if max(self.warp(A[ii], B[jj]) for ii in (i, i + 1) for jj in (j, j + 1)) > 0.002:
                    face(part, [bk(i, j), bk(i, j + 1), bk(i + 1, j + 1), bk(i + 1, j)], -self.n)
        nA, nB = len(A) - 1, len(B) - 1
        for i in range(nA):
            face(part, [front[i][0], front[i + 1][0], bk(i + 1, 0), bk(i, 0)], -self.ve)
            face(part, [front[i][nB], front[i + 1][nB], bk(i + 1, nB), bk(i, nB)], self.ve)
        for j in range(nB):
            face(part, [front[0][j], front[0][j + 1], bk(0, j + 1), bk(0, j)], -self.ue)
            face(part, [front[nA][j], front[nA][j + 1], bk(nA, j + 1), bk(nA, j)], self.ue)
        bm.normal_update()

    def bolts(self):
        return [self.at(a, b) for a in self.ba for b in self.bb]


def door_sheet(d, k):
    """Row k sheet on door d (0 - left, 1 - right); each door has its own (the doors open)."""
    xa, xb, _, _ = DOORS[d]
    z0, z1 = ROWS[k]
    sx = 0.006 * ((k + d) % 2)
    return Sheet((xa + 0.004 + sx, YR[k], z0), (xb - xa - 0.010 - sx, 0, 0), (0, 0, z1 - z0), (0, -1, 0),
                 seed=1.7 * k + 3.1 * d + 0.4, under=LAP if k > 0 else 0.0, cover=LAP if k < 2 else 0.0)


def flat_items():
    """What is screwed to the door sheets: envelopes (lo, hi) in the world - the sheet is pressed under them."""
    xh = [DOORS[0][1] - 0.05, DOORS[1][0] + 0.05]
    zh = LAY["handle_z"]
    fw = HS + FR_W
    out = [((WX - WW, -0.3, WZ0), (WX + WW, -0.2, WZ1)),                                    # window box
           ((HX - fw, -0.3, HZ - fw), (HX + fw, -0.2, HZ + fw)),                              # hatch frame
           ((SGX - SGS, -0.3, SGZ - SGS), (SGX + SGS, -0.2, SGZ + SGS)),                        # sign
           ((LAMP_X - 0.042, -0.3, LAMP_Z - 0.042), (LAMP_X + 0.042, -0.3, LAMP_Z + 0.042)),     # lamp
           ((GAUGE_X - 0.034, -0.3, GAUGE_Z - 0.10), (GAUGE_X + 0.05, -0.3, GAUGE_Z + 0.034)),  # draft gauge, tube
           ((LAMP_X + 0.005, -0.3, LAMP_Z), (LAMP_X + 0.04, -0.3, 1.60)),                        # lamp cable in clips
           ((FS[0], -0.3, FS[4] - 0.005), (FS[1], -0.3, FS[4] + 0.035))]                       # shelf of slot 1
    out += [((x - 0.02, -0.3, zh - 0.05), (x + 0.02, -0.3, zh + 0.085)) for x in xh]         # handles
    out += [((x - 0.012, -0.3, FS[4] - 0.155), (x + 0.012, -0.3, FS[4])) for x in (FS[0] + 0.03, FS[1] - 0.03)]
    return out


def side_sheets():
    """Side sheets: the left one - two rows under the hooks, the right one - one under the shelf."""
    out = []
    for k, (z0, z1) in enumerate(((0.14, 0.62), (0.58, 1.08))):
        out.append(("lead_l%d" % k, Sheet((CX0 - T * k, CY0 + 0.012, z0), (0, CY1 - CY0 - 0.024, 0), (0, 0, z1 - z0),
                                          (-1, 0, 0), seed=2.3 + k, bulge=0.010, wave=0.011,
                                          under=LAP if k > 0 else 0.0, cover=LAP if k == 0 else 0.0)))
    r0 = Sheet((CX1, CY0 + 0.015, 0.14), (0, CY1 - CY0 - 0.03, 0), (0, 0, 0.70), (1, 0, 0), seed=4.4, bulge=0.010,
               wave=0.011)
    for y in (-0.17, 0.17):
        r0.flat_box((CX1, y - 0.012, SZ - 0.235), (CX1, y + 0.012, SZ))                      # shelf gussets
    r0.flat_box((CX1, -0.02, 0.60), (CX1, 0.02, 0.66))                                      # gas mask hook
    out.append(("lead_r0", r0))
    l1 = out[1][1]
    for y in (LS[2] + 0.02, LS[3] - 0.02):
        l1.flat_box((CX0, y - 0.012, LS[4] - 0.16), (CX0, y + 0.012, LS[4]))                 # small shelf gussets
    for y, z in TONGS:
        l1.flat_box((CX0, y - 0.01, z - 0.02), (CX0, y + 0.01, z + 0.01))
    return out


def sheets(lod):
    out = []
    items = flat_items()
    for d in range(2):
        for k in range(3):
            sh = door_sheet(d, k)
            for lo, hi in items:
                sh.flat_box(lo, hi)
            if d == 0 and k == 2 and lod < 2:
                x0, y0 = sh.local((OPEN[0] - 0.008, 0, OPEN[2] - 0.008))
                x1, y1 = sh.local((OPEN[1] + 0.008, 0, OPEN[3] + 0.008))
                sh.hole = (x0, x1, y0, y1)
            out.append(("lead_f%d%d" % (d, k), sh))
    return out + side_sheets()


def build_cladding(spec):
    lod = spec["lod"]
    parts = []
    if lod == 2:
        # far LOD: one plate per door and side, the same parts - the same atlas rectangles
        for name, sh in sheets(lod):
            if name[-1] != "0":
                continue
            p = P(name, "lead")
            tall = {"lead_l0": 0.94, "lead_r0": 0.70}.get(name, ROWS[2][1] - ROWS[0][0])
            lo = sh.o
            hi = sh.o + sh.ue * sh.W + Vector((0, 0, tall)) + sh.n * 3 * T
            g.box(p, min(lo.x, hi.x), max(lo.x, hi.x), min(lo.y, hi.y), max(lo.y, hi.y), lo.z, hi.z)
            parts.append(p)
        return parts
    hd = P("lead_bolts", "bolt") if lod == 0 else None
    ws = None
    for name, sh in sheets(lod):
        p = P(name, "lead")
        if lod == 0:
            sh.build(p, *((5, 4) if name.startswith("lead_f") else (4, 3)))
            for c in sh.bolts():
                bolt(hd, ws, c, sh.n, lod)
        else:
            sh.warped = False
            sh.build(p, 1, 1)
        parts.append(p)
    if hd is not None:
        parts.append(hd)
    return parts


# =============================================================================
# Viewing window: inclined box, glass, opening into the interior
# =============================================================================
def build_window(spec):
    lod = spec["lod"]
    k = 2 if lod == 0 else 0
    w = window_geom()
    fc, ux, vf, out, hf, bc = w["fc"], w["ux"], w["vf"], w["out"], w["hf"], w["bc"]   # face: forward and up
    axis = (fc - bc).normalized()
    wb = P("win_box", "lead_box")
    L0 = verts(wb, rrect(bc, ux, (0, 0, 1), 2 * WW, WZ1 - WZ0, 0.014, k))
    L1 = verts(wb, rrect(fc - out * 0.004, ux, vf, 2 * WW, hf, 0.014, k))
    L2 = verts(wb, rrect(fc, ux, vf, 2 * WW - 0.008, hf - 0.008, 0.010, k))
    L3 = verts(wb, rrect(fc, ux, vf, 2 * WW - 2 * WIN, hf - 2 * WIN, 0.006, k))
    gl_pts = glass_loop(k)
    L4 = verts(wb, gl_pts)
    bridge(wb, L0, L1, radial(bc, axis))
    bridge(wb, L1, L2, lambda c: radial(bc, axis)(c).normalized() + out)
    bridge(wb, L2, L3, out)
    bridge(wb, L3, L4, radial(fc, out, outward=False))
    parts = [wb]
    if lod == 2:
        dk = P("win_inner", "inner", group=SEL_LIGHT)
        fill(dk, verts(dk, gl_pts), out)
        return parts + [dk]
    # opening through the sheet, door and body - straight along y, to the interior
    L5 = verts(wb, [Vector((p.x, CHAMBER[2] + 0.002, p.z)) for p in gl_pts])
    bridge(wb, L4, L5, radial((WX, 0, (OPEN[2] + OPEN[3]) / 2), (0, 1, 0), outward=False))
    gl = P("win_glass", "steel", section="glass")
    fill(gl, verts(gl, [p + out * 0.001 for p in gl_pts]), out)
    parts.append(gl)
    if lod == 0:
        sc = P("win_screws", "bolt")
        for p in rrect(fc, ux, vf, 2 * WW - WIN, hf - WIN, 0.0, 0):
            screw(sc, p, out, 0.0055, 0.0025)
        parts.append(sc)
    return parts


# =============================================================================
# Interior behind the window: bricks, container, sample tray, lamp (ozl_light)
# =============================================================================
def build_inside(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    zf = CHAMBER[4]
    yb = CHAMBER[3]
    n = 10 if lod == 0 else 5
    parts = []
    # wall of lead bricks 200 x 100 x 50 on edge at the back wall, three courses with a running bond
    br = P("in_bricks", "brick", group=SEL_LIGHT)
    for row in range(3):
        for col in range(2):
            x0 = CHAMBER[0] + 0.012 + col * 0.202 + (0.01 if row % 2 else 0.0)
            z0 = zf + row * 0.1005
            g.box(br, x0, x0 + 0.2, yb - 0.052, yb - 0.002, z0, z0 + 0.1)
    parts.append(br)
    # open lead container of diameter 120 x 130, the lid beside it on the floor
    pt = P("in_pot", "pot", group=SEL_LIGHT)
    px, py = -0.17, 0.03
    lathe(pt, [(0.0, 0.0), (0.058, 0.0), (0.060, 0.004), (0.060, 0.122), (0.057, 0.13), (0.040, 0.13), (0.038, 0.126),
               (0.038, 0.04)], n, (px, py, zf), (0, 0, 1))
    lathe(pt, [(0.038, 0.04), (0.0, 0.04)], n, (px, py, zf), (0, 0, 1))
    lathe(pt, [(0.0, 0.0), (0.061, 0.0), (0.063, 0.004), (0.063, 0.03), (0.050, 0.034), (0.034, 0.034), (0.034, 0.038),
               (0.016, 0.046), (0.0, 0.046)], n, (-0.30, -0.10, zf), (0, 0, 1))
    parts.append(pt)
    # sample tray: the tongs take the sample in "work"
    tx, ty = TRAY
    tr = P("in_tray", "tray", group=SEL_LIGHT)
    lathe(tr, [(0.0, 0.0), (0.040, 0.0), (0.046, 0.016), (0.050, 0.018), (0.047, 0.019), (0.040, 0.004), (0.0, 0.004)],
          n, (tx, ty, zf), (0, 0, 1), phase=0.0)
    parts.append(tr)
    sp = P("in_sample", "sample", group=SEL_LIGHT)
    lump = []
    rnd = random.Random(9)
    for i in range(7):
        t = math.pi * i / 6
        lump.append((0.022 * math.sin(t) * (0.85 + 0.3 * rnd.random()), -0.017 * math.cos(t)))
    lump[0], lump[-1] = (0.0, lump[0][1]), (0.0, lump[-1][1])
    lathe(sp, lump, 7 if lod == 0 else 5, (tx, ty, zf + 0.004 + 0.017), (0.3, 0.2, 1), phase=0.3)
    parts.append(sp)
    # lamp on the back wall: a socket on a bracket, a bulb, a cage
    lx, lz = WX, 1.42
    bb = P("in_lamp_base", "bulb_base", group=SEL_LIGHT)
    g.box(bb, lx - 0.03, lx + 0.03, yb - 0.004, yb, lz + 0.035, lz + 0.065)
    lathe(bb, [(0.016, 0.0), (0.016, 0.03), (0.012, 0.036)], 10 if lod == 0 else 6, (lx, yb - 0.035, lz + 0.065),
          (0, 0, -1), cap1=True)
    g.box(bb, lx - 0.006, lx + 0.006, yb - 0.04, yb - 0.004, lz + 0.05, lz + 0.062)
    parts.append(bb)
    bl = P("in_bulb", "bulb", group=SEL_LIGHT)
    lathe(bl, [(0.012, 0.0), (0.028, 0.02), (0.031, 0.04), (0.024, 0.062), (0.0, 0.07)], 10 if lod == 0 else 6,
          (lx, yb - 0.035, lz + 0.029), (0, 0, -1))
    parts.append(bl)
    return parts


# =============================================================================
# Hatch, ball port, manipulator (ozl_arm), sign
# =============================================================================
def arm_frame():
    """Rod axes: e - outward along the rod, zl - up across, side - sideways."""
    e = -ARM_D
    zl = (Vector((0, 0, 1)) - e * e.z).normalized()
    return e, zl, e.cross(zl).normalized()


def build_hatch(spec):
    """Hatch flange frame on the sheets, a hatch on two hinges at the left, a turn latch at the right; in
    the hatch - the ball port flange on bolts and the ball."""
    lod = spec["lod"]
    k = 2 if lod == 0 else 0
    sd = (16, 8, 6)[lod]
    parts = []
    fr = P("hatch_frame", "lead_box")
    c0, c1 = Vector((HX, FR_Y0, HZ)), Vector((HX, FR_Y1, HZ))
    ux, uz = (1, 0, 0), (0, 0, 1)
    so, si = 2 * (HS + FR_W), 2 * HS
    if lod == 2:
        g.box(fr, HX - HS - FR_W, HX + HS + FR_W, LID_Y1, FR_Y0, HZ - HS - FR_W, HZ + HS + FR_W)
        return [fr]
    O0 = verts(fr, rrect(c0, ux, uz, so, so, 0.016, k))
    O1 = verts(fr, rrect(c1 + Vector((0, 0.002, 0)), ux, uz, so, so, 0.016, k))
    O2 = verts(fr, rrect(c1, ux, uz, so - 0.004, so - 0.004, 0.014, k))
    I1 = verts(fr, rrect(c1, ux, uz, si, si, 0.008, k))
    I0 = verts(fr, rrect(c0, ux, uz, si, si, 0.008, k))
    bridge(fr, O0, O1, radial(c0, (0, 1, 0)))
    bridge(fr, O1, O2, lambda c: radial(c0, (0, 1, 0))(c).normalized() + Vector((0, -1, 0)))
    bridge(fr, O2, I1, (0, -1, 0))
    bridge(fr, I1, I0, radial(c0, (0, 1, 0), outward=False))
    parts.append(fr)
    # hatch: a 12 mm plate, rounded (it covers the opening and overlaps the frame by 11 mm)
    ld = P("hatch_lid", "lead_box")
    rbox(ld, HX - HS - 0.011, HX + HS + 0.011, LID_Y1, FR_Y1 + 0.0005, HZ - HS - 0.011, HZ + HS + 0.011, 0.004, k)
    parts.append(ld)
    st = P("hatch_steel", "steel")
    # port flange of diameter 132 and the ball cage
    lathe(st, [(0.040, 0.0), (0.066, 0.0), (0.066, 0.008), (0.058, 0.010), (0.046, 0.016), (0.040, 0.016)],
          12 if lod == 0 else 6, (HX, LID_Y1, HZ), (0, -1, 0))
    # hinges at the left (knuckles on the hatch edge, tabs on the hatch and the frame), the latch at the right on
    # the frame
    lid_h = HS + 0.011
    xh = HX - lid_h - 0.004
    for z in (HZ - 0.075, HZ + 0.075):
        lathe(st, [(0.0072, -0.022), (0.0072, 0.022)], 8 if lod == 0 else 5, (xh, LID_Y1 + 0.004, z), (0, 0, 1),
              cap0=True, cap1=True)
        g.box(st, xh, xh + 0.05, LID_Y1 - 0.003, LID_Y1, z - 0.017, z + 0.017)
        g.box(st, HX - HS - FR_W + 0.003, xh, FR_Y1 - 0.003, FR_Y1, z - 0.017, z + 0.017)
    xl = HX + lid_h + 0.011
    lathe(st, [(0.0095, 0.0), (0.0095, 0.010), (0.0, 0.0145)], 8 if lod == 0 else 6,
          (xl, FR_Y1, HZ), (0, -1, 0))
    bprism(st, [(xl - 0.008, HZ - 0.006), (xl + 0.002, HZ - 0.007), (xl + 0.010, HZ - 0.005), (xl + 0.010, HZ + 0.005),
                (xl + 0.002, HZ + 0.007), (xl - 0.034, HZ + 0.006), (xl - 0.036, HZ - 0.004)], (0, 2), LID_Y1 - 0.0065,
           LID_Y1 - 0.003, 0.0012 if lod == 0 else 0.0, 1)
    parts.append(st)
    if lod == 0:
        # frame bolts along the strip between the hatch and the outer edge (except the hinge and latch
        # places), six port flange bolts
        hd = P("hatch_bolts", "bolt")
        e = (lid_h + HS + FR_W) / 2
        for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1), (0, -1), (0, 1)):
            bolt(hd, None, c1 + Vector((sx * e, 0, sz * e)), (0, -1, 0), lod)
        for i in range(6):
            t = math.pi / 6 + math.pi / 3 * i
            bolt(hd, None, Vector((HX + 0.055 * math.cos(t), LID_Y1 - 0.010, HZ + 0.055 * math.sin(t))), (0, -1, 0), lod)
        parts.append(hd)
    # port ball: the rod goes through the poles
    bp = P("hatch_ball", "ball")
    ball(bp, BALL, BALL_R, 12 if lod == 0 else 8, axis=ARM_D, hole=0.0105, rings=6 if lod == 0 else 4)
    parts.append(bp)
    return parts


def grip_frame(origin):
    e, zl, side = arm_frame()
    return g.Frame(origin, e, zl, side)


def build_arm(spec):
    """Manipulator (bone ozl_arm, in "work" it feeds inward along the rod): outside a rod of diameter 18, a
    stop ring, a grip body, a pistol grip with a trigger and a trigger linkage along the rod; inside - a
    rod of diameter 14 and tongs with two jaws."""
    lod = spec["lod"]
    if lod == 2:
        return []
    sd = 10 if lod == 0 else 6
    e, zl, side = arm_frame()
    parts = []
    rd = P("arm_rod", "tongs", group=SEL_ARM)
    end = BALL + e * ARM_OUT
    rod(rd, BALL + e * 0.0, end, 0.009, sd)
    tip = BALL - e * ARM_IN
    rod(rd, BALL, BALL - e * (ARM_IN - 0.05), 0.007, sd)
    lathe(rd, [(0.0, -0.004), (0.014, -0.002), (0.014, 0.010), (0.0, 0.012)], 8 if lod == 0 else 5,
          BALL + e * 0.135, e)                                                                     # stop ring
    lathe(rd, [(0.0, 0.0), (0.011, 0.0), (0.011, 0.022), (0.0, 0.022)], 8 if lod == 0 else 5,
          BALL - e * (ARM_IN - 0.06), -e)                                                          # tongs coupling
    # tong jaws: two, converging to the tip
    for s in (-1, 1):
        q0 = BALL - e * (ARM_IN - 0.04)
        pts = [q0 + side * (s * 0.006), q0 - e * 0.02 + side * (s * 0.012) - zl * 0.003,
               q0 - e * 0.035 + side * (s * 0.008) - zl * 0.008, q0 - e * 0.042 + side * (s * 0.003) - zl * 0.011]
        g.tube_var(rd, pts, [(0.0045, 0.003)] * 4, 5 if lod == 0 else 3)
    parts.append(rd)
    # body and grip: a profile in the rod plane (along e, up zl), thickness sideways
    fr = grip_frame(end)
    gp = P("arm_grip", "grip", group=SEL_ARM)
    housing = [(-0.035, -0.017), (0.016, -0.017), (0.022, -0.010), (0.022, 0.012), (0.016, 0.017), (-0.035, 0.017),
               (-0.040, 0.012), (-0.040, -0.012)]
    bprism(gp, housing, (0, 1), -0.016, 0.016, 0.004 if lod == 0 else 0.0, 1, frame=fr)
    handle = [(-0.004, -0.015), (0.020, -0.015), (0.032, -0.036), (0.046, -0.080), (0.056, -0.118), (0.050, -0.128),
              (0.030, -0.128), (0.022, -0.105), (0.015, -0.083), (0.008, -0.060), (0.0, -0.034), (-0.006, -0.022)]
    bprism(gp, handle if lod == 0 else handle[::3], (0, 1), -0.0135, 0.0135, 0.005 if lod == 0 else 0.0, 1,
           frame=fr)
    trig = [(-0.030, -0.016), (-0.016, -0.016), (-0.010, -0.040), (-0.006, -0.070), (-0.010, -0.086), (-0.018, -0.088),
            (-0.022, -0.072), (-0.024, -0.045), (-0.032, -0.024)]
    bprism(gp, trig if lod == 0 else trig[::2], (0, 1), -0.005, 0.005, 0.0018 if lod == 0 else 0.0, 1, frame=fr)
    parts.append(gp)
    if lod == 0:
        # trigger linkage along the rod from below, to the stop ring; body screws
        lk = P("arm_link", "steel", group=SEL_ARM)
        g.pipe(lk, [fr.p(-0.034, -0.019, 0.0), fr.p(-0.05, -0.0185, 0.0), BALL + e * 0.15 - zl * 0.0175], 0.0026, 6)
        for a in (-0.028, 0.008):
            screw(lk, fr.p(a, 0.0, 0.016), side, 0.0035, 0.0015, 6)
        parts.append(lk)
    return parts


def build_sign(spec):
    lod = spec["lod"]
    sg = P("sign", "sign")
    rbox(sg, SGX - SGS, SGX + SGS, SGY, YTOP + 0.001, SGZ - SGS, SGZ + SGS, 0.002, 1 if lod == 0 else 0)
    parts = [sg]
    if lod == 0:
        sc = P("sign_screws", "bolt")
        for sx in (-1, 1):
            for sz in (-1, 1):
                screw(sc, (SGX + sx * SGS * 0.84, SGY, SGZ + sz * SGS * 0.84), (0, -1, 0), 0.0045, 0.002)
        parts.append(sc)
    return parts


# =============================================================================
# Signal lamp by the hatch (ozl_lamp), cable to the box on the roof; draft gauge (ozl_needle)
# =============================================================================
def build_lamp(spec):
    lod = spec["lod"]
    sd = (16, 8, 6)[lod]
    c = Vector((LAMP_X, YTOP, LAMP_Z))
    out = Vector((0, -1, 0))
    bd = P("lamp_body", "lamp_body")
    if lod == 2:
        g.box(bd, LAMP_X - 0.03, LAMP_X + 0.03, YTOP - 0.03, YTOP, LAMP_Z - 0.03, LAMP_Z + 0.03)
        ln = P("lamp_lens", "lamp", group=SEL_LAMP)
        g.box(ln, LAMP_X - 0.02, LAMP_X + 0.02, YTOP - 0.05, YTOP - 0.03, LAMP_Z - 0.02, LAMP_Z + 0.02)
        return [bd, ln]
    lathe(bd, [(0.042, 0.0), (0.042, 0.008), (0.038, 0.010), (0.034, 0.011), (0.034, 0.032), (0.032, 0.034)], sd, c, out)
    parts = [bd]
    ln = P("lamp_lens", "lamp", group=SEL_LAMP)
    dome = [(0.031, 0.034)] + [(0.031 * math.cos(math.pi / 2 * i / 4), 0.034 + 0.034 * math.sin(math.pi / 2 * i / 4))
                               for i in range(1, 5)]
    lathe(ln, dome if lod == 0 else dome[::2], sd, c, out)
    parts.append(ln)
    if lod == 0:
        gd = P("lamp_guard", "wire")
        ring = [c + out * 0.036 + (Vector((math.cos(t), 0, math.sin(t))) * 0.035)
                for t in (2 * math.pi * i / 10 for i in range(11))]
        g.pipe(gd, ring, 0.0016, 4)
        for t in (math.pi / 4, 3 * math.pi / 4):
            d = Vector((math.cos(t), 0, math.sin(t)))
            arc = [c + out * 0.036 + d * 0.035] + [c + out * (0.037 + 0.038 * math.sin(math.pi * i / 4)) +
                                                   d * (0.036 * math.cos(math.pi * i / 4)) for i in range(1, 4)] + \
                  [c + out * 0.036 - d * 0.035]
            g.pipe(gd, arc, 0.0014, 4)
        for sx in (-1, 1):
            screw(gd, c + out * 0.008 + Vector((sx * 0.036, 0, 0)), out, 0.004, 0.002, 6)
        parts.append(gd)
    # cable: from the lamp up the door in clips, over the top of the cabinet to the box on the roof
    cb = P("lamp_cable", "cable")
    xc = LAMP_X + 0.02
    yc = YTOP - 0.004
    pts = [(LAMP_X + 0.012, YTOP - 0.012, LAMP_Z + 0.022), (xc, yc - 0.002, LAMP_Z + 0.05), (xc, yc, LAMP_Z + 0.12),
           (xc, yc, ROWS[2][1] - 0.03), (xc, CY0 - 0.006, ROWS[2][1] + 0.02), (xc, CY0 - 0.004, DOORS[1][3] - 0.02),
           (xc, CY0 - 0.004, H - 0.006), (xc, CY0 + 0.004, H + 0.0055), (xc - 0.004, YB + 0.015, H + 0.0045),
           (xc - 0.03, YB + 0.07, H + 0.0045), (BX1 + 0.06, -0.03, H + 0.0045), (BX1 + 0.025, -0.03, H + 0.03),
           (BX1 + 0.004, -0.03, H + 0.075)]
    g.pipe(cb, spline(pts, 2) if lod == 0 else pts, 0.004, 5 if lod == 0 else 4)
    parts.append(cb)
    if lod == 0:
        cl = P("lamp_clips", "steel")
        for z in (LAMP_Z + 0.20, DOORS[1][3] - 0.07):
            y_surf = YTOP if z < ROWS[2][1] else CY0
            arc = [(xc + 0.0055 * math.cos(math.pi * i / 6), y_surf - 0.004 - 0.0055 * math.sin(math.pi * i / 6), z)
                   for i in range(7)]
            g.sweep(cl, arc, (0, 0, 1), 0.0007, 0.005)
            g.box(cl, xc + 0.005, xc + 0.016, y_surf - 0.0012, y_surf + 0.0005, z - 0.005, z + 0.005)
            screw(cl, (xc + 0.0115, y_surf - 0.0012, z), (0, -1, 0), 0.003, 0.0015, 6)
        # entry into the box: a gland nut
        lathe(cl, [(0.009, 0.0), (0.009, 0.007), (0.006, 0.016), (0.0045, 0.02)], 6, (BX1, -0.03, H + 0.075), (1, 0, 0),
              phase=0.0)
        parts.append(cl)
    return parts


def build_gauge(spec):
    """Draft gauge under the window: a case of diameter 64 on a bracket, a scale (a decal), the needle is
    the bone ozl_needle, a copper impulse tube into the door."""
    lod = spec["lod"]
    if lod == 2:
        return []
    sd = 14 if lod == 0 else 8
    c = Vector((GAUGE_X, YTOP, GAUGE_Z))
    out = Vector((0, -1, 0))
    R = GAUGE_R
    cs = P("gauge_case", "gauge")
    hd = YTOP - GAUGE_FACE                                   # scale depth from the sheet
    lathe(cs, [(0.0, 0.0), (R - 0.004, 0.0), (R, 0.003), (R, hd - 0.002), (R + 0.002, hd - 0.001),
               (R + 0.002, hd + 0.004), (R - 0.001, hd + 0.0055), (R - 0.004, hd + 0.0055), (R - 0.004, hd)], sd, c, out)
    if lod == 0:
        lathe(cs, [(0.006, 0.0), (0.006, 0.012), (0.0045, 0.014)], 6, (GAUGE_X, YTOP - 0.014, GAUGE_Z - R + 0.002),
              (0, 0, -1), cap1=True, phase=0.0)
    parts = [cs]
    dl = P("gauge_dial", "dial")
    lathe(dl, [(R - 0.004, 0.0), (0.0, 0.0)], sd, Vector((GAUGE_X, GAUGE_FACE, GAUGE_Z)), out)
    parts.append(dl)
    nd = P("gauge_needle", "needle", group=SEL_NEEDLE)
    yn = GAUGE_FACE - 0.002
    g.prism(nd, [(GAUGE_X - 0.0016, GAUGE_Z - 0.007), (GAUGE_X + 0.0016, GAUGE_Z - 0.007), (GAUGE_X + 0.0005, GAUGE_Z + 0.026),
                 (GAUGE_X - 0.0005, GAUGE_Z + 0.026)], (0, 2), yn - 0.0006, yn + 0.0006)
    lathe(nd, [(0.0035, 0.0), (0.0035, 0.002), (0.0, 0.0028)], 8, (GAUGE_X, yn + 0.0004, GAUGE_Z), out)
    parts.append(nd)
    if lod == 0:
        cu = P("gauge_tube", "copper")
        y0 = YTOP - 0.016
        g.pipe(cu, spline([(GAUGE_X, y0, GAUGE_Z - R - 0.012), (GAUGE_X, y0, GAUGE_Z - R - 0.03),
                           (GAUGE_X + 0.015, y0 + 0.004, GAUGE_Z - R - 0.05), (GAUGE_X + 0.03, YTOP - 0.004, GAUGE_Z - R - 0.06),
                           (GAUGE_X + 0.04, YTOP + 0.004, GAUGE_Z - R - 0.062)], 2), 0.003, 5)
        lathe(cu, [(0.0065, 0.0), (0.0065, 0.008), (0.004, 0.01)], 6, (GAUGE_X + 0.04, YTOP + 0.001, GAUGE_Z - R - 0.062),
              (0, -1, 0), phase=0.0)
        parts.append(cu)
    return parts


# =============================================================================
# Left side: hooks, tongs; M70 shelf (slot 2), the empty hook of the DP-5V strap
# =============================================================================
def build_tongs(spec):
    """Long tongs (36", 0.91 m): two arms on a pivot, finger rings at the top, jaws at the bottom; they
    hang by the ring on a hook."""
    lod = spec["lod"]
    if lod == 2:
        return []
    sd = 5 if lod == 0 else 4
    parts = []
    hk = P("hooks", "steel")
    for y, z in TONGS:
        hook(hk, (CX0, y, z - 0.012), (-1, 0, 0), (0, 0, 1), sd)
    hook(hk, (CX0, STRAP_HOOK[0], STRAP_HOOK[1]), (-1, 0, 0), (0, 0, 1), sd, reach=0.035, rise=0.03)
    parts.append(hk)
    x = CX0 - 0.05
    for i, (y, zh) in enumerate(TONGS):
        tg = P("tongs%d" % i, "tongs", uv_name="tongs", uv_origin=(0, y, zh))
        zr = zh - 0.012                      # centre of the ring hanging on the hook
        zp = zr - 0.16                       # pivot
        zj = zr - 0.91 + 0.03                # jaws
        for s in (-1, 1):
            cy = y + s * 0.013
            arm = [(x, cy, zr - 0.02), (x, y + s * 0.006, zp + 0.05), (x, y - s * 0.003, zp - 0.035),
                   (x, y - s * 0.0045, zj + 0.12), (x, y - s * 0.0022, zj)]
            g.pipe(tg, spline(arm, 2) if lod == 0 else [arm[i] for i in (0, 2, 4)], 0.0048, 5 if lod == 0 else 3)
            n = 8 if lod == 0 else 6
            rr = 0.017
            g.pipe(tg, [(x, cy + rr * math.sin(2 * math.pi * kk / n), zr + rr * math.cos(2 * math.pi * kk / n))
                        for kk in range(n + 1)], 0.0036, 4 if lod == 0 else 3)
            jaw = [(y - s * 0.0045 - 0.0055, zj - 0.026), (y - s * 0.0045 + 0.0055, zj - 0.026),
                   (y - s * 0.0045 + 0.006, zj + 0.012), (y - s * 0.0045 - 0.006, zj + 0.012)]
            g.prism(tg, jaw, (1, 2), x - 0.0075, x + 0.0075)
        if lod == 0:
            lathe(tg, [(0.0, -0.011), (0.0095, -0.009), (0.0095, 0.009), (0.0, 0.011)], 8, (x, y, zp), (1, 0, 0))
        parts.append(tg)
    return parts


def gusset(part, base, out, down, depth, height, t, lod):
    """Gusset triangle under a shelf: full height at the wall, tapering to nothing at the edge; with a bent-down
    tab."""
    b, o, d = Vector(base), Vector(out).normalized(), Vector(down).normalized()
    side = o.cross(d).normalized()
    pts = [b, b + o * depth, b + d * height]
    poly = [(0.0, 0.0), (depth, 0.0), (0.0, height)]
    fr = g.Frame(b, o, d, side)
    g.prism(part, poly, (0, 1), -t / 2, t / 2, frame=fr)
    return pts


def build_shelves(spec):
    """Module shelves: the right one (slot 3) is welded to the side, with gussets; the new ones - under the
    hatch (slot 1) and on the left side (slot 2): bolted through the lead, a bent edge, gussets."""
    lod = spec["lod"]
    k = 1 if lod == 0 else 0
    parts = []
    sh = P("shelves", "shelf")
    # right
    rbox(sh, SX0, SX1, SY0, SY1, SZ - 0.003, SZ, 0.0012, k)
    if lod < 2:
        g.box(sh, SX1 - 0.003, SX1, SY0, SY1, SZ - 0.03, SZ - 0.002)
        for y in (-0.17, 0.17):
            gusset(sh, (SX0, y, SZ - 0.003), (1, 0, 0), (0, 0, -1), 0.23, 0.22, 0.006, lod)
    # under the hatch (on the right door)
    x0, x1, yb, yf, zt = FS
    rbox(sh, x0, x1, yf, yb, zt - 0.003, zt, 0.0012, k)
    if lod < 2:
        g.box(sh, x0, x1, yf, yf + 0.003, zt - 0.025, zt - 0.002)                          # bent edge
        g.box(sh, x0, x1, yb - 0.003, yb, zt - 0.002, zt + 0.03)                           # shelf to the door
        for x in (x0 + 0.03, x1 - 0.03):
            gusset(sh, (x, yb, zt - 0.003), (0, -1, 0), (0, 0, -1), 0.18, 0.15, 0.005, lod)
    # on the left side
    xw, xe, y0, y1, zl = LS
    rbox(sh, xe, xw, y0, y1, zl - 0.003, zl, 0.0012, k)
    if lod < 2:
        g.box(sh, xe, xe + 0.003, y0, y1, zl - 0.025, zl - 0.002)
        g.box(sh, xw - 0.003, xw, y0, y1, zl - 0.002, zl + 0.03)
        for y in (y0 + 0.02, y1 - 0.02):
            gusset(sh, (xw, y, zl - 0.003), (-1, 0, 0), (0, 0, -1), 0.20, 0.15, 0.005, lod)
    parts.append(sh)
    if lod == 0:
        hd, ws = P("shelf_bolts", "bolt"), P("shelf_washers", "steel")
        for x in (x0 + 0.08, x1 - 0.08):
            bolt(hd, ws, (x, yb - 0.003, zt + 0.016), (0, -1, 0), lod)
        for y in (y0 + 0.06, y1 - 0.06):
            bolt(hd, ws, (xw - 0.003, y, zl + 0.016), (-1, 0, 0), lod)
        parts += [hd, ws]
        # slot 1: a coiled cable on the free edge of the shelf (to the probe)
        cb = P("coil", "cable")
        cx, cy = x0 + 0.042, (yb + yf) / 2 + 0.01
        coil = [(cx + (0.030 - 0.0025 * (i / 9)) * math.cos(2 * math.pi * i / 9),
                 cy + (0.030 - 0.0025 * (i / 9)) * math.sin(2 * math.pi * i / 9) * 1.25,
                 zt + 0.004 + 0.005 * (i / 18)) for i in range(19)]
        g.pipe(cb, coil, 0.0035, 5)
        lathe(cb, [(0.0, 0.0), (0.0075, 0.0), (0.0075, 0.03), (0.005, 0.034), (0.005, 0.05), (0.0, 0.05)], 6,
              Vector(coil[-1]), (-0.2, 1.0, 0.0))
        parts.append(cb)
    return parts


def build_rack(spec):
    """Bar with hooks above the right shelf: the vanilla tools hang on it (DECOR); the gas mask hook is under the
    shelf."""
    lod = spec["lod"]
    if lod == 2:
        return []
    sd = 5 if lod == 0 else 4
    rk = P("tool_rack", "steel")
    rbox(rk, CX1, CX1 + 0.004, -0.21, 0.21, RACK_Z, RACK_Z + 0.025, 0.001, 1 if lod == 0 else 0)
    for y in RACK_Y:
        hook(rk, (CX1 + 0.004, y, RACK_Z + 0.008), (1, 0, 0), (0, 0, 1), 4, reach=0.018, rise=0.014, r=0.0025)
    hook(rk, (CX1 + T, 0.0, 0.615), (1, 0, 0), (0, 0, 1), sd, reach=0.03, rise=0.025)
    if lod == 0:
        for y in (-0.19, 0.19):
            screw(rk, (CX1 + 0.004, y, RACK_Z + 0.0125), (1, 0, 0), 0.0045, 0.002)
    return [rk]


# =============================================================================
# Box on the roof
# =============================================================================
def build_box(spec):
    """Steel box: a body on two skids, an overlapping lid, stamped ribs, folding handles on the ends, two
    latches at the front, hinges at the back; the lamp cable entry is on the right end."""
    lod = spec["lod"]
    k = 2 if lod == 0 else 0
    bx = P("roof_box", "box")
    z0 = H + (0.012 if lod < 2 else 0.0)
    rbox(bx, BX0, BX1, BY0, BY1, z0, BZ1, 0.006, k)
    rbox(bx, BX0 - 0.006, BX1 + 0.006, BY0 - 0.006, BY1 + 0.006, BZ1 - 0.012, BZ1 + 0.045, 0.006, k)
    parts = [bx]
    if lod == 2:
        return parts
    st = P("roof_box_steel", "steel")
    for y in (BY0 + 0.03, BY1 - 0.03):
        g.box(st, BX0 + 0.01, BX1 - 0.01, y - 0.015, y + 0.015, H, z0)
    for x in (BX0 + 0.08, BX1 - 0.08):
        # latch: a base on the body, a lever, a hook on the lid
        g.box(st, x - 0.016, x + 0.016, BY0 - 0.004, BY0 + 0.001, BZ1 - 0.06, BZ1 - 0.016)
        g.box(st, x - 0.008, x + 0.008, BY0 - 0.011, BY0 - 0.004, BZ1 - 0.055, BZ1 - 0.005)
        g.box(st, x - 0.006, x + 0.006, BY0 - 0.012, BY0 - 0.006, BZ1 - 0.008, BZ1 + 0.025)
    if lod == 0:
        for x, s in ((BX0, -1), (BX1, 1)):
            for y in (-0.06, 0.04):
                lathe(st, [(0.007, 0.0), (0.007, 0.008), (0.0, 0.009)], 6, (x, y, BZ1 - 0.03), (s, 0, 0))
            g.pipe(st, spline([(x + s * 0.008, -0.06, BZ1 - 0.03), (x + s * 0.016, -0.055, BZ1 - 0.06),
                               (x + s * 0.017, -0.01, BZ1 - 0.075), (x + s * 0.016, 0.035, BZ1 - 0.06),
                               (x + s * 0.008, 0.04, BZ1 - 0.03)], 2), 0.0045, 4)
        for x in (BX0 + 0.10, BX1 - 0.10):
            lathe(st, [(0.0065, -0.03), (0.0065, 0.03)], 6, (x, BY1 + 0.008, BZ1 + 0.012), (1, 0, 0), cap0=True,
                  cap1=True)
        rb = P("roof_box_ribs", "box")
        for y, s in ((BY0, -1), (BY1, 1)):
            for z in (z0 + 0.035, z0 + 0.075):
                g.pipe(rb, [(BX0 + 0.04, y + s * 0.0005, z), (BX1 - 0.04, y + s * 0.0005, z)], 0.0045, 6)
        parts.append(rb)
    parts.append(st)
    return parts


def build_lod(spec):
    parts = build_cabinet(spec) + build_cladding(spec) + build_window(spec) + build_inside(spec)
    parts += build_hatch(spec) + build_arm(spec) + build_sign(spec) + build_lamp(spec) + build_gauge(spec)
    parts += build_tongs(spec) + build_shelves(spec) + build_rack(spec) + build_box(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    metal = kx.PEN + r"\metalplate.rvmat"
    body = kx.box_pts(CX0 - 0.02, CX1 + 0.01, CY0 - 3 * T, CY1, 0.0, H)
    # a component thinner than 0.5 m does not work: the protrusions go into the cabinet
    front = kx.box_pts(WX - WW - 0.01, FS[1], -0.57, CY0 + 0.30, FS[4] - 0.17, WZ1 + 0.02)
    left = kx.box_pts(LS[1] - 0.005, CX0 + 0.40, CY0, CY1, 0.70, 1.70)
    right = kx.box_pts(SX0 - 0.25, SX1, SY0, SY1, 0.36, RACK_Z + 0.03)
    box = kx.box_pts(BX0 - 0.025, BX1 + 0.025, BY0 - 0.014, BY0 + 0.50, BZ1 + 0.045 - 0.50, BZ1 + 0.045)
    comps = [(body, metal), (front, metal), (left, metal), (right, metal), (box, metal)]
    e = ARM_D
    memory = {
        "invView": [(0.0, -2.8, 1.2)],
        "ce_center": [(0.0, 0.0, 1.0)],
        "ce_radius": [(1.0, 0.0, 1.0)],
        "ozl_needle_axis": NEEDLE_AXIS,                      # toward the person (-Y), see NEEDLE_AXIS
        "ozl_arm_axis": [tuple(BALL), tuple(BALL + e * 1.0)],
    }
    for i, m in enumerate(MODS):
        memory["module_%d" % (i + 1)] = [m]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 160.0, memory, bbox


# preview: the window glass is almost transparent, as in game (glass_ca: clear 0.015), not the grey
# kit preview glass; in "work" the draft gauge needle is at the vacuum mark (model.cfg rotates the
# bone itself; the preview can only shift groups - the needle rotation is here, in the frames only)
_place_look = krender.place_look


def _clear_glass():
    import bpy
    m = bpy.data.materials.get("m09_glass_clear")
    if m is None:
        m = bpy.data.materials.new("m09_glass_clear")
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (0.86, 0.85, 0.74, 1)
        b.inputs["Alpha"].default_value = 0.05
        b.inputs["Roughness"].default_value = 0.05
    return m


def _place_look_posed(parts, kind_table, origin, remap=None, **kw):
    obs = _place_look(parts, kind_table, origin, remap=remap, **kw)
    for ob in obs:
        if ob.name.startswith("look_win_glass"):
            ob.data.materials.clear()
            ob.data.materials.append(_clear_glass())
    if remap:
        # engine rotation by memory points (engine_rot): the preview shows what will be in game
        rot = engine_rot(NEEDLE_MID * NEEDLE_ANG)
        for ob in obs:
            if ob.name.startswith("look_gauge_needle"):
                ob.matrix_world = rot @ ob.matrix_world
    return obs


def engine_rot(ang):
    """Rotation matrix of the needle bone by angle ang, as the engine does it about the memory axis
    NEEDLE_AXIS: in Blender axes - right-handed about the reverse axis (from the second point to the first)."""
    a, b = Vector(NEEDLE_AXIS[0]), Vector(NEEDLE_AXIS[1])
    return Matrix.Translation(a) @ Matrix.Rotation(ang, 4, a - b) @ Matrix.Translation(-a)


def check_needle():
    """Numeric check, like check_axes of the Storage boxes: the needle at rest points up (zero), at phases
    mid +- amp and 1 the engine rotation takes it left, toward the red vacuum zone (counter-clockwise
    from the front), and not past the scale edge (135 degrees). If it does not hold, the build fails."""
    c = Vector((GAUGE_X, GAUGE_FACE - 0.002, GAUGE_Z))
    tip = c + Vector((0.0, 0.0, 0.026))
    seen = []
    for ph in (0.0, NEEDLE_MID - NEEDLE_AMP, NEEDLE_MID, NEEDLE_MID + NEEDLE_AMP, 1.0):
        q = engine_rot(ph * NEEDLE_ANG) @ tip
        deg = math.degrees(math.atan2(q.z - c.z, q.x - c.x))              # front view: right is +X
        assert abs(deg - (90.0 - math.degrees(NEEDLE_ANG) * ph)) < 0.01, "needle goes the wrong way: %.1f" % deg
        assert deg <= 90.0 + 135.0, "needle past the scale edge: %.1f" % deg
        seen.append("%.2f -> %.1f" % (ph, deg))
    print("turns ok: needle (phase -> degrees from the front, 90 is zero at the top) " + ", ".join(seen))


check_needle()
krender.place_look = _place_look_posed

# the first ones are for the --look preview: overview, all three module places from the front (and
# again empty), the hatch with the manipulator, window, lamp and draft gauge, the right side (tools,
# gas mask), the window close-up
SHOTS = [
    ("front", (-1.3, -3.2, 1.8), (0.0, 0.0, 1.0), 30),
    ("slots", (0.0, -3.4, 1.40), (0.0, -0.15, 1.0), 38),
    ("hatch", (0.35, -1.55, 1.30), (0.05, -0.30, 1.05), 32),
    ("right", (1.70, -1.30, 1.45), (0.45, 0.0, 1.02), 28),
    ("window", (-0.32, -0.80, 1.62), (-0.12, 0.05, 1.06), 40),
    ("left", (-1.75, -0.85, 1.45), (-0.45, 0.0, 1.05), 32),
    ("back", (1.5, 2.6, 2.0), (0.0, 0.0, 0.95), 30),
]

M.look_shots = (5, 3)
M.run(build_lod, collision, SHOTS, row_step=1.5, row_shot=((2.2, -7.5, 2.0), (1.5, 0, 0.9)))
