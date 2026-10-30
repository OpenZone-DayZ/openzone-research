"""M73 - Soldering station (OZL_Tool_SolderStation): a module of the "Electronics" line (packers M05 and
M11) - a portable 2x2 item, it stands in slot OZL_Tool2 and is visible on the shelf of the machine
through a proxy (in M05 it is on the table at the right in place of the soldering station, in M11 in
place of the EPSN). Variant A: a 1980-90s soldering station with a thermoregulator - a power unit
with a temperature knob, on the right a stand with a coil and a sponge, the iron in the coil.

    blender --background --python build_m73.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (temperature scale, soldering iron
pictogram, "hot" triangle, slots, sponge).

Target: ~0.20 x 0.12 x 0.18 m with the stand, grey or blue metal, a black iron handle, a yellow
sponge, a temperature scale - digits only; a module is no larger than ~0.2 x 0.2 m by its base and up
to ~0.25 m high, with a flat bottom.

Reference and sizes:
- look: Weller WTCP-S: a unit with a rounded cover, a dark front panel in a light frame, slots on the
  sides at the top, a red mains key with a backlight, the iron socket at the bottom, a solder reel on
  the roof; to the right of the unit a stand - a black tray with a sponge at the front, a chrome
  conical coil at the back, the iron lies in it tip down, handle up;
- the temperature knob: on the electronic station of the same line, the Weller WECP-20: a
  potentiometer, smooth setting of 150-450 C, a heating indicator lamp (it blinks while the regulator
  holds the temperature), an LR-21 iron 24 V / 50 W, the stand is placed to the left or right of the
  unit; the unit is 115 x 150 x 94 mm (W x D x H), 2.1 kg (the WECP-20 manual - found via search
  results, the files did not open). A check of the class: the WTCP 51 unit is 166 x 115 x 101 mm,
  1.46 kg (element14, RS 332-0357), the PU120T (WTCPT) is 114 x 151 x 92 mm (testequity.com); the
  related WTCPT as a whole (with the stand) is 136 x 270 x 235 mm, 1.76 kg (ibselectronics.com);
- the LR-21 iron: box 275 x 65 x 43 mm, 0.18 kg (distrelec.ch, digitec.ch) - the iron itself ~0.23 m
  with the tip; the LR-21 set with a stand is 195 x 165 x 98 mm (distrelec.ch);
- the model is life-size: a unit of 115 x 150 x 94 mm, a stand of 80 x 145 mm beside it on the right,
  the iron 0.232 m at 40 degrees, handle forward; together ~0.21 x 0.19 x 0.20 m without cords (the
  iron sticks out 0.04 m forward over the sponge). The iron cord hangs on the right and lies on the
  shelf in front of the unit (up to 0.13 m from the centre forward), the mains cord is a loop behind
  the unit with a plug (up to 0.13 m back): the module_N platform of M05 and M11 is 0.22 x 0.24 m on a
  shelf 0.30 deep, neighbouring places 0.28 m apart;
- weight in the mod is 800 g (OZL_Tool_Base, unchanged); the mass in Geometry is the same.

Detailing: "dayz" look (matte, dirtier, coloured AO). In more
detail: the cover is a U-shaped sheet with rounded top edges (R 10 mm), the frame of the same
outline, the opening and the panel with rounded corners; the slots on the sides are real slits (a
boolean difference, the decal under them stays); cover screws, an unlabeled nameplate and two rivets
at the back, round rubber feet; the temperature knob is knurled (12 ribs) with a skirt and a chamfer;
the lamp is a dome lens in a chrome ring; the mains key is concave; the fuse is a cap with a slot; the
iron plug is a knurled nut and a ribbed tail; the solder reel has chamfered flanges, a winding, a hub
hole; the iron is a single solid of revolution in steps (a tip with a tinned point, a sleeve, a nut,
a thermal ring, a knurled handle, a tail); the coil is wire of 8 faces, the step per turn is a 6.5 mm
chord (wide upper turns are round, not polygons); the tray is cast, rounded; the cords are smooth
curves (Catmull-Rom, a ring per 11 degrees of turn, 10 faces - under 40 degrees between faces, no
kinks in the kit's smoothing), lying on the shelf, with ribbed entries; a Euro plug with insulated
pins. No vanilla proxy items: the module is itself a 2x2 inventory item, small things around it are
placed by the M05 and M11 machines.

Marks: digits of the 150-450 scale, a soldering iron pictogram above the socket, a yellow triangle
with a flame ("hot surface") on the left side, an empty nameplate at the back - not the ones of M05
(there are tags and instrument scales).
"Working" state: the mains key is ozl_lamp_work (burns steadily, onSelections), the heating lamp is
ozl_lamp_heat (blinks - blink: the regulator holds the temperature); the _on atlas - the key is red,
the lamp green. The device has no moving parts, no bones.
LODs (a small item): near and middle (~40 %: no feet, screws, slits, nameplate, fuse, solder tip; the
coil, cords and solids of revolution sparser), no far one.

Blender axes: X is width, Y is depth (the front face is -Y), Z is up. The origin is the centre of the
bottom: this is how the module stands on the module_N proxy point (autocenter = 0 in Geometry).
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
from mathutils import Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m --------------------------------------------------------------------------------
FOOT_H = 0.004
# power unit (WECP-20: 115 x 150 x 94)
UX0, UX1, UY0, UY1, UZ1 = -0.100, 0.015, -0.075, 0.075, 0.094
SEAM_Z = 0.018                  # top of the lower tray
FRAME_T = 0.007                 # panel frame
COVER_R = 0.010                 # bend of the cover at the top (a U-shaped sheet)
YP = UY0 + 0.003                # face of the black panel (recessed 3 mm into the frame)
OPEN = (-0.091, 0.006, 0.014, 0.085)            # frame opening (x0, x1, z0, z1)
OPEN_R = 0.003
KNOB = (-0.050, 0.050)          # temperature knob (x, z)
SCALE_D = 0.056                 # scale square, as in make_decals.py
LED = (-0.082, 0.077)           # heating lamp
FUSE = (-0.082, 0.022)
ROCKER = (-0.008, 0.071)        # mains key
ICON = (-0.008, 0.049)
ICON_W, ICON_H = 0.012, 0.010
SOCK = (-0.008, 0.026)          # iron socket with the plug
PLUG_L = 0.036                  # plug with a tail from the panel
WARN = (-0.034, 0.046)          # triangle on the left side (y, z)
WARN_D = 0.026
SLOTS = (0.034, 0.0708)         # slots on the sides (y, z) - the decal, as in make_decals.py
SLOTS_W, SLOTS_H = 0.046, 0.030
# the slits are where the dark stripes of the decal are (make_decals.make_slots: axes 5.8 mm apart)
SLOT_Z = [SLOTS[1] - SLOTS_H / 2 + 0.0035 + i * 0.0058 for i in range(5)]
SLOT_Y = (SLOTS[0] - SLOTS_W / 2 + 0.0032, SLOTS[0] + SLOTS_W / 2 - 0.0032)
SLOT_HH, SLOT_D = 0.0011, 0.0012
SCREWS = [(-0.052, SEAM_Z + 0.006), (0.058, SEAM_Z + 0.006)]     # cover screws on the sides (y, z)
PLATE = (-0.034, 0.050, 0.040, 0.024)          # nameplate at the back: centre (x, z), width, height
SPOOL = (-0.050, 0.014)         # solder reel on the roof (x, y)
# stand on the right
RX0, RX1, RY0, RY1 = 0.021, 0.101, -0.075, 0.070
TRAY_Y1, TRAY_H, BASE_H = -0.022, 0.019, 0.008
SPONGE = (RX0 + 0.0055, RX1 - 0.0055, RY0 + 0.0055, TRAY_Y1 - 0.0055, 0.024)
# iron: the axis in the plane x = XA, the tip at the back and low, the handle forward and up at ELEV
XA, ELEV = 0.061, math.radians(40.0)
T0 = Vector((XA, 0.066, 0.036))                 # end of the tip
D = Vector((0.0, -math.cos(ELEV), math.sin(ELEV)))
# iron profile from the end of the tip: (part, region, [(s, r)]) - LR-21; the steps are butt-jointed
# (the end ring of one = the start ring of the next), no ends inside (an atlas trap: a hidden end of
# one part bakes over a visible one)
IRON = [
    ("iron_tin", "tin", [(0.0000, 0.0006), (0.0015, 0.0010), (0.0040, 0.0014)]),
    ("iron_tip", "tip", [(0.0040, 0.0014), (0.0100, 0.0018), (0.0180, 0.0022), (0.0226, 0.0027), (0.0240, 0.0030)]),
    ("iron_sleeve", "chrome", [(0.0240, 0.0030), (0.0244, 0.0045), (0.0810, 0.0045)]),
    ("iron_nut", "chrome", [(0.0810, 0.0045), (0.0810, 0.0064), (0.0816, 0.0068), (0.0894, 0.0068),
                            (0.0900, 0.0064)]),
    ("iron_collar", "grip", [(0.0900, 0.0064), (0.0902, 0.0100), (0.0912, 0.0116), (0.0950, 0.0118),
                             (0.0962, 0.0108)]),
    ("iron_grip", "grip", [(0.0962, 0.0108), (0.1000, 0.0104), (0.1030, 0.0108), (0.1060, 0.0104),
                           (0.1090, 0.0108), (0.1120, 0.0104), (0.1150, 0.0108), (0.1180, 0.0104),
                           (0.1500, 0.0101)]),
    ("iron_handle", "handle", [(0.1500, 0.0101), (0.1520, 0.0102), (0.1800, 0.0097), (0.2000, 0.0091),
                               (0.2050, 0.0086)]),
    ("iron_relief", "grip", [(0.2050, 0.0086), (0.2056, 0.0066), (0.2120, 0.0060), (0.2130, 0.0054),
                             (0.2200, 0.0049), (0.2210, 0.0044), (0.2320, 0.0032)]),
]
S_END = 0.232
# coil: a cone along the iron axis
SP_S0, SP_S1, SP_R0, SP_R1, SP_W, SP_PITCH = 0.027, 0.113, 0.0068, 0.0196, 0.0014, 0.0115
CABLE_R, CORD_R = 0.0024, 0.0028

# lod is the number; iron, small, cable are the faces of solids of revolution and cords; spiral is
# (chord of the step per turn, faces, turn pitch x); spool is the reel faces; flutes are the handle
# ribs (0 is smooth)
LOD_SPECS = [
    dict(lod=0, iron=10, small=12, cable=10, spiral=(0.0065, 8, 1), spool=20, flutes=12),
    dict(lod=1, iron=8, small=8, cable=6, spiral=(0.012, 5, 1), spool=12, flutes=0),
]

REGIONS = {
    "cover": ("cover", 1.0), "pan": ("pan", 0.6), "frame": ("frame", 1.0), "panel": ("panel", 2.5),
    "knob": ("knob", 1.5), "pointer": ("pointer", 0.5), "chrome": ("chrome", 1.0),
    "lamp": ("lamp", 0.8), "rocker": ("rocker", 1.0), "bezel": ("black", 0.6), "fuse": ("knob", 0.6),
    "plug": ("plug", 0.8), "cable": ("cable", 0.6), "cord": ("cord", 0.5), "rest": ("rest", 1.0),
    "sponge": ("sponge", 2.0), "spiral": ("spiral", 0.6), "tip": ("tip", 1.0), "tin": ("tin", 1.0),
    "grip": ("grip", 1.0), "handle": ("handle", 1.0), "spool": ("spool", 1.2), "solder": ("solder", 1.0),
    "hub": ("black", 0.5), "feet": ("rubber", 0.4), "slot": ("slot", 0.4), "screw": ("screw", 1.0),
    "plate": ("plate", 1.5),
}


def wdecal(name):
    return os.path.join(WORK, name)


SCALE_DEC = (wdecal("decal_scale.png"), "y", -1, ("x", "z"), KNOB, (SCALE_D, SCALE_D), (YP - 0.001, YP + 0.001))
ICON_DEC = (wdecal("decal_icon.png"), "y", -1, ("x", "z"), ICON, (ICON_W, ICON_H), (YP - 0.001, YP + 0.001))
WARN_DEC = (wdecal("decal_warn.png"), "x", -1, ("y", "z"), WARN, (WARN_D, WARN_D), (UX0 - 0.002, UX0 + 0.002))
SLOT_DECS = [(wdecal("decal_slots.png"), "x", sg, ("y", "z"), SLOTS, (SLOTS_W, SLOTS_H), (x - 0.002, x + 0.002))
             for sg, x in ((-1, UX0), (1, UX1))]
SPONGE_DEC = (wdecal("decal_sponge.png"), "z", 1, ("x", "y"), ((SPONGE[0] + SPONGE[1]) / 2, (SPONGE[2] + SPONGE[3]) / 2),
              (SPONGE[1] - SPONGE[0], SPONGE[3] - SPONGE[2]), (SPONGE[4] - 0.003, SPONGE[4] + 0.002))

# modules: worn at the edges, small chips, almost no rust
USED = dict(chip=(0.66, 0.72), rust=(0.92, 0.96), rust_low=0.1, floor_z=0.0, dust=0.22, grime=0.34)
LIT = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
METAL = kmats.lin((150, 152, 154))

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "cover": ("paint", dict(USED, color=kmats.lin((112, 130, 146)), under=METAL, seed=2.6, gloss=0.42, spec=0.32,
                            decal_items=[WARN_DEC] + SLOT_DECS)),
    "pan": ("plastic", dict(color=kmats.lin((62, 64, 66)), seed=3.2, gloss=0.25, spec=0.18, dust=0.15, grime=0.3,
                            scuff=(0.8, 0.9))),
    "frame": ("plastic", dict(color=kmats.lin((176, 184, 186)), seed=3.8, gloss=0.35, spec=0.25, dust=0.3,
                              grime=0.45, scuff=(0.66, 0.76))),
    "panel": ("paint", dict(USED, chip=(0.86, 0.92), color=kmats.lin((32, 33, 35)), under=METAL, seed=4.4,
                            gloss=0.3, spec=0.2, dust=0.08, decal_items=[SCALE_DEC, ICON_DEC])),
    "knob": ("plastic", dict(color=kmats.lin((24, 24, 24)), seed=5.0, gloss=0.5, spec=0.4, dust=0.05, grime=0.1,
                             scuff=(0.80, 0.88))),
    "pointer": ("flat", dict(color=kmats.lin((228, 228, 222)), gloss=0.5, spec=0.3)),
    "chrome": ("steel", dict(seed=5.6, tone=0.62, along="z", gloss=0.75, spec=0.85, dust=0.06, grime=0.15)),
    "lamp": ("flat", dict(color=kmats.lin((34, 62, 36)), gloss=0.85, spec=0.8)),
    "lamp_on": ("flat", dict(color=kmats.lin((110, 255, 120)), gloss=0.85, spec=0.8)),
    "rocker": ("flat", dict(color=kmats.lin((112, 26, 22)), gloss=0.8, spec=0.7)),
    "rocker_on": ("flat", dict(color=kmats.lin((255, 72, 46)), gloss=0.8, spec=0.7)),
    "plug": ("plastic", dict(color=kmats.lin((28, 28, 29)), seed=6.2, gloss=0.35, spec=0.25, dust=0.1, grime=0.1,
                             scuff=(0.85, 0.95))),
    "cable": ("plastic", dict(color=kmats.lin((204, 192, 164)), seed=6.8, gloss=0.3, spec=0.2, dust=0.25,
                              grime=0.35, scuff=(0.85, 0.95))),
    "cord": ("plastic", dict(color=kmats.lin((30, 30, 31)), seed=7.3, gloss=0.25, spec=0.15, dust=0.2, grime=0.2,
                             scuff=(0.9, 1.0))),
    "rest": ("paint", dict(USED, color=kmats.lin((40, 40, 42)), under=kmats.lin((112, 112, 114)), seed=7.9,
                           gloss=0.25, spec=0.2, dust=0.2, grime=0.3)),
    "sponge": ("paint", dict(LIT, color=kmats.lin((196, 150, 58)), gloss=0.15, spec=0.08,
                             decal_items=[SPONGE_DEC])),
    "spiral": ("steel", dict(seed=8.4, tone=0.60, along="z", gloss=0.7, spec=0.8, dust=0.08, grime=0.25)),
    "tip": ("steel", dict(seed=8.9, tone=0.24, along="y", gloss=0.45, spec=0.5, dust=0.0, grime=0.35)),
    "tin": ("steel", dict(seed=9.3, tone=0.74, along="y", gloss=0.85, spec=0.9, dust=0.0, grime=0.05)),
    "grip": ("plastic", dict(color=kmats.lin((22, 22, 22)), seed=9.8, gloss=0.12, spec=0.08, dust=0.15,
                             grime=0.2, scuff=(0.86, 0.94))),
    "handle": ("plastic", dict(color=kmats.lin((27, 27, 28)), seed=10.4, gloss=0.42, spec=0.35, dust=0.1,
                               grime=0.15, scuff=(0.8, 0.9))),
    "spool": ("plastic", dict(color=kmats.lin((34, 86, 170)), seed=11.0, gloss=0.4, spec=0.3, dust=0.1, grime=0.1,
                              scuff=(0.8, 0.9))),
    # winding: turns across the reel axis (vertical) - sanding marks along x
    "solder": ("steel", dict(seed=11.6, tone=0.52, along="x", gloss=0.5, spec=0.55, dust=0.05, grime=0.2)),
    "slot": ("flat", dict(color=kmats.lin((14, 14, 15)), gloss=0.2, spec=0.1)),
    # galvanized screws and an empty aluminium nameplate
    "screw": ("steel", dict(seed=12.2, tone=0.42, along="x", gloss=0.5, spec=0.6, dust=0.1, grime=0.35)),
    "plate": ("steel", dict(seed=12.8, tone=0.56, along="x", gloss=0.45, spec=0.5, dust=0.15, grime=0.3)),
})

OBJ, NAME = "m73_solder_station", "ozr_solder_station"
SEL_LAMP = "ozl_lamp_work"      # mains key: lit steadily when working
SEL_HEAT = "ozl_lamp_heat"      # heating lamp: blinks when working (blink)
ON = dict(remap={"lamp": "lamp_on", "rocker": "rocker_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL_LAMP, SEL_HEAT), hidden=(SEL_LAMP, SEL_HEAT), states={"on": ON})
P = M.part
BOUNDS = {}

# coordinate system of the iron axis: n runs along the axis from the tip to the handle
IFRAME = g.Frame(T0, (1, 0, 0), D.cross(Vector((1, 0, 0))), D)


def on_axis(s):
    return T0 + D * s


# --- primitives missing from kgeo -----------------------------------------------------------------
def frame_n(o, n, u):
    """Right-handed coordinate system with axis n: u is made perpendicular to n, v = n x u (u x v = n)."""
    n = Vector(n).normalized()
    u = Vector(u)
    u = (u - n * u.dot(n)).normalized()
    return g.Frame(o, u, n.cross(u), n)


def lathe(part, fr, prof, sides, cap0=False, cap1=False, rfun=None):
    """Solid of revolution about the axis fr.n from fr.o: prof [(h, r)] is the walk of the body's
    half-section (outwards, along, inwards), faces look outwards; rfun(i, k, r) is the radius of vertex k
    of ring i (knurling). cap0 / cap1 close the first / last ring."""
    bm = part.bm
    rings = []
    for i, (h, r) in enumerate(prof):
        ring = []
        for k in range(sides):
            a = 2 * math.pi * k / sides
            rr = rfun(i, k, r) if rfun else r
            ring.append(bm.verts.new(fr.o + fr.n * h + (fr.u * math.cos(a) + fr.v * math.sin(a)) * rr))
        rings.append(ring)
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            faces.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    if cap0:
        faces.append(bm.faces.new(rings[0][::-1]))
    if cap1:
        faces.append(bm.faces.new(rings[-1]))
    bm.normal_update()
    return part.tag(faces)


def thin(prof, keep_every=2):
    """Middle LOD profile: every second point, the ends stay in place (the joint with the neighbouring part)."""
    if len(prof) <= 3:
        return prof
    return [prof[0]] + prof[1:-1][1::keep_every] + [prof[-1]]


def rrect(a0, a1, b0, b1, r, n, r_bot=None):
    """Rectangle with rounded corners (counter-clockwise): the top corners r, the bottom ones r_bot."""
    rb = r if r_bot is None else r_bot
    pts = []
    for ca, cb, rad, a_start in ((a1 - rb, b0 + rb, rb, -90.0), (a1 - r, b1 - r, r, 0.0),
                                 (a0 + r, b1 - r, r, 90.0), (a0 + rb, b0 + rb, rb, 180.0)):
        if rad <= 0:
            pts.append((ca, cb))
            continue
        for s in range(n + 1):
            t = math.radians(a_start + 90.0 * s / n)
            pts.append((ca + rad * math.cos(t), cb + rad * math.sin(t)))
    return pts


def slab(part, poly, axes, c0, c1, bev=0.0, seg=0, ends=(1, -1)):
    """A kgeo.prism with a chamfer on the end edges (ends: +1 is the end c1, -1 the end c0)."""
    bm = part.bm
    before = set(bm.faces)
    g.prism(part, poly, axes, c0, c1)
    ic = 3 - axes[0] - axes[1]
    if bev > 0 and seg > 0:
        bm.normal_update()
        caps = [f for f in bm.faces if f not in before and any(f.normal[ic] * s > 0.99 for s in ends)]
        g.bevel(bm, list({e for f in caps for e in f.edges}), bev, seg)
    faces = [f for f in bm.faces if f not in before]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    bm.normal_update()
    return part.tag(faces)


def boxp(name, region, x0, x1, y0, y1, z0, z1, **kw):
    p = P(name, region)
    g.box(p, x0, x1, y0, y1, z0, z1, **kw)
    return p


def disc_z(part, cx, cy, z, r, n):
    """Disc: a single n-gon face in a z plane, looking up."""
    bm = part.bm
    vs = [bm.verts.new(Vector((cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z)))
          for i in range(n)]
    part.tag([bm.faces.new(vs)])


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, as in M38 and M45)."""
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
    out.append(v[-1].copy())
    return out


def smooth_path(pts, turn_deg=18.0, seg=0.03, floor=None):
    """A smooth cord curve with an economical ring count: a dense Catmull-Rom, then a ring wherever the
    direction has turned by turn_deg since the last ring or seg has been covered. floor is the minimum
    height (the cord lies on the shelf rather than sinking into it)."""
    dense = spline(pts, 12)
    if floor is not None:
        for q in dense:
            q.z = max(q.z, floor)
    out = [dense[0]]
    d0 = (dense[1] - dense[0]).normalized()
    cos_t = math.cos(math.radians(turn_deg))
    for i in range(1, len(dense) - 1):
        di = (dense[i + 1] - dense[i]).normalized()
        if di.dot(d0) < cos_t or (dense[i] - out[-1]).length > seg:
            out.append(dense[i])
            d0 = di
    out.append(dense[-1])
    return [tuple(q) for q in out]


# --- unit -----------------------------------------------------------------------------------------
def build_unit(spec):
    """Cover (a U-shaped sheet, slits on the sides, screws), tray, frame with an opening, panel, feet,
    nameplate at the back, solder reel on the roof."""
    lod = spec["lod"]
    parts = []
    # cover: an x-z profile with rounded top edges, along y; the back end has a bend chamfer
    cv = P("cover", "cover")
    slab(cv, rrect(UX0, UX1, SEAM_Z, UZ1, COVER_R, 5 if lod == 0 else 2, r_bot=0.0), (0, 2), UY0 + FRAME_T, UY1,
         bev=0.002, seg=2 if lod == 0 else 1, ends=(1,))
    if lod == 0:
        cut = P("slot_cut", "slot")
        for x0, x1 in ((UX0 - 0.002, UX0 + SLOT_D), (UX1 - SLOT_D, UX1 + 0.002)):
            for z in SLOT_Z:
                g.box(cut, x0, x1, SLOT_Y[0], SLOT_Y[1], z - SLOT_HH, z + SLOT_HH)
        cv = M.boolean("cover_%d" % lod, cv, [cut])
    parts.append(cv)
    parts.append(boxp("pan", "pan", UX0 + 0.0015, UX1 - 0.0015, UY0 + FRAME_T, UY1 - 0.0015, FOOT_H, SEAM_Z + 0.002,
                      **({"r": 0.002, "seg": 1} if lod == 0 else {})))
    # frame: the same outline as the cover, a chamfer on the face, an opening with rounded corners
    fr = P("frame", "frame")
    slab(fr, rrect(UX0, UX1, FOOT_H, UZ1, COVER_R, 5 if lod == 0 else 2, r_bot=0.003), (0, 2), UY0,
         UY0 + FRAME_T + 0.002, bev=0.0025, seg=2 if lod == 0 else 1, ends=(-1,))
    cut = P("frame_cut", "frame")
    x0, x1, z0, z1 = OPEN
    slab(cut, rrect(x0, x1, z0, z1, OPEN_R, 3 if lod == 0 else 1), (0, 2), UY0 - 0.01, UY0 + FRAME_T + 0.01)
    parts.append(M.boolean("frame_%d" % lod, fr, [cut]))
    pn = P("panel", "panel")
    slab(pn, rrect(x0 - 0.0005, x1 + 0.0005, z0 - 0.0005, z1 + 0.0005, OPEN_R, 3 if lod == 0 else 1), (0, 2),
         YP, UY0 + FRAME_T + 0.001)
    parts.append(pn)
    if lod == 0:
        # round rubber feet
        ft = P("feet", "feet")
        for x in (UX0 + 0.014, UX1 - 0.014):
            for y in (UY0 + 0.022, UY1 - 0.016):
                g.cyl(ft, (x, y, FOOT_H / 2), "z", 0.0068, FOOT_H, 8, r2=0.0060)
        parts.append(ft)
        # cover screws on the sides: a dome (the 3 mm slot is not modelled)
        sc = P("cover_screws", "screw")
        for sg, x in ((-1, UX0), (1, UX1)):
            for y, z in SCREWS:
                lathe(sc, frame_n((x, y, z), (sg, 0, 0), (0, 1, 0)),
                      [(0.0, 0.0030), (0.0008, 0.0027), (0.0013, 0.0014)], 8, cap1=True)
        parts.append(sc)
        # empty nameplate at the back on two rivets
        px, pz, pw, ph = PLATE
        pl = P("back_plate", "plate")
        slab(pl, rrect(px - pw / 2, px + pw / 2, pz - ph / 2, pz + ph / 2, 0.002, 2), (0, 2), UY1 - 0.0002,
             UY1 + 0.0005)
        parts.append(pl)
        rv = P("plate_rivets", "screw")
        for dx in (-pw / 2 + 0.0035, pw / 2 - 0.0035):
            lathe(rv, frame_n((px + dx, UY1 + 0.0004, pz), (0, 1, 0), (1, 0, 0)),
                  [(0.0, 0.0016), (0.0005, 0.0013), (0.0008, 0.0006)], 6, cap1=True)
        parts.append(rv)
    parts += build_spool(spec)
    return parts


def build_spool(spec):
    """Solder reel: a lower flange, the winding, an upper flange with a chamfer and a hub hole, the bottom of
    the hole; the wire end arcs outwards."""
    lod, n = spec["lod"], spec["spool"]
    sx, sy = SPOOL
    fr = frame_n((sx, sy, UZ1), (0, 0, 1), (1, 0, 0))
    parts = []
    lo = P("spool_bottom", "spool")
    lathe(lo, fr, [(0.0, 0.0260), (0.0026, 0.0260), (0.0026, 0.0205)], n)
    parts.append(lo)
    sd = P("spool_solder", "solder")
    lathe(sd, fr, [(0.0026, 0.0205), (0.0120, 0.0209), (0.0214, 0.0205)] if lod == 0 else
          [(0.0026, 0.0205), (0.0214, 0.0205)], n)
    parts.append(sd)
    hi = P("spool_top", "spool")
    prof = [(0.0214, 0.0205), (0.0214, 0.0260), (0.0236, 0.0260), (0.0241, 0.0253), (0.0241, 0.0112),
            (0.0110, 0.0112)]
    lathe(hi, fr, prof if lod == 0 else [prof[0], prof[1], (0.0241, 0.0260), prof[4], prof[5]], n)
    parts.append(hi)
    hb = P("spool_hub", "hub")
    disc_z(hb, sx, sy, UZ1 + 0.0110, 0.0113, n)
    parts.append(hb)
    if lod == 0:
        # solder wire end: from the winding outwards, up over the flange and down
        a = math.radians(-35)
        x0, y0 = sx + 0.0208 * math.cos(a), sy + 0.0208 * math.sin(a)
        wire = [(x0, y0, UZ1 + 0.016), (x0 + 0.0045, y0 - 0.0035, UZ1 + 0.019), (x0 + 0.0055, y0 - 0.007, UZ1 + 0.030),
                (x0 - 0.001, y0 - 0.0085, UZ1 + 0.0385), (x0 - 0.011, y0 - 0.0075, UZ1 + 0.040),
                (x0 - 0.018, y0 - 0.005, UZ1 + 0.034)]
        sw = P("solder_end", "solder")
        g.pipe(sw, smooth_path(wire, 22.0, 0.008), 0.0008, 6)
        parts.append(sw)
    return parts


def build_panel(spec):
    """Knurled temperature knob with a scale (the panel decal), heating lamp, fuse, mains key, a socket with
    the iron plug."""
    lod, ns = spec["lod"], spec["small"]
    parts = []
    out = (0, -1, 0)
    # knob: a skirt with a chamfer, a knurled body, a chamfer to the end; a mark on the end and on the skirt
    kx_, kz = KNOB
    kn = P("knob", "knob")
    kprof = [(0.0, 0.0150), (0.0022, 0.0150), (0.0029, 0.0143), (0.0029, 0.0126), (0.0152, 0.0118),
             (0.0166, 0.0105)]
    nfl = spec["flutes"]
    if nfl:
        lathe(kn, frame_n((kx_, YP, kz), out, (1, 0, 0)), kprof, 2 * nfl, cap1=True,
              rfun=lambda i, k, r: r - 0.0007 * (k % 2) if i in (3, 4) else r)
    else:
        lathe(kn, frame_n((kx_, YP, kz), out, (1, 0, 0)), [kprof[0], kprof[2], kprof[3], kprof[4], kprof[5]], 10,
              cap1=True)
    parts.append(kn)
    if lod == 0:
        pt = P("knob_pointer", "pointer")
        g.box(pt, kx_ - 0.0007, kx_ + 0.0007, YP - 0.0170, YP - 0.0163, kz + 0.0015, kz + 0.0098)
        g.box(pt, kx_ - 0.0007, kx_ + 0.0007, YP - 0.0033, YP - 0.0026, kz + 0.0127, kz + 0.0145)
        parts.append(pt)
    # heating lamp: a chrome ring and a green dome lens (ozl_lamp_heat)
    lx, lz = LED
    lf = frame_n((lx, YP, lz), out, (1, 0, 0))
    rg = P("led_ring", "chrome")
    lathe(rg, lf, [(0.0, 0.0048), (0.0012, 0.0046), (0.0016, 0.0033)], ns)
    parts.append(rg)
    ld = P("led", "lamp", group=SEL_HEAT)
    lathe(ld, lf, [(0.0010, 0.0033), (0.0024, 0.0031), (0.0033, 0.0024), (0.0038, 0.0013)] if lod == 0 else
          [(0.0010, 0.0033), (0.0030, 0.0027), (0.0038, 0.0013)], ns, cap1=True)
    parts.append(ld)
    # mains key: a black frame and a red backlit key, pressed by its upper half, the face concave
    rx, rz = ROCKER
    parts.append(boxp("rocker_bezel", "bezel", rx - 0.0076, rx + 0.0076, YP - 0.0028, YP + 0.0005, rz - 0.0106,
                      rz + 0.0106, **({"r": 0.0011, "seg": 1} if lod == 0 else {})))
    rk = P("rocker", "rocker", group=SEL_LAMP)
    face = [(-0.0068, -0.0086), (-0.0060, -0.0043), (-0.0053, 0.0), (-0.0048, 0.0043), (-0.0044, 0.0086)]
    if lod:
        face = face[::2]
    prof = [(YP - 0.0026, rz - 0.0086)] + [(YP + a, rz + b) for a, b in face] + [(YP - 0.0026, rz + 0.0086)]
    g.prism(rk, prof, (1, 2), rx - 0.0058, rx + 0.0058)
    parts.append(rk)
    if lod == 0:
        # fuse: a cap with a slot
        fx, fz = FUSE
        fu = P("fuse", "fuse")
        lathe(fu, frame_n((fx, YP, fz), out, (1, 0, 0)),
              [(0.0, 0.0056), (0.0030, 0.0054), (0.0042, 0.0050), (0.0050, 0.0043)], 12, cap1=True)
        parts.append(fu)
        fs = P("fuse_slot", "slot")
        g.box(fs, fx - 0.0030, fx + 0.0030, YP - 0.0052, YP - 0.0048, fz - 0.0005, fz + 0.0005)
        parts.append(fs)
    # socket: a chrome flange; the plug is a knurled nut, a body, a ribbed tail along -Y
    cx, cz = SOCK
    sf = frame_n((cx, YP, cz), out, (1, 0, 0))
    fl = P("socket_flange", "chrome")
    lathe(fl, sf, [(0.0, 0.0102), (0.0012, 0.0102), (0.0020, 0.0094), (0.0020, 0.0088)], 16 if lod == 0 else 8)
    parts.append(fl)
    pb = P("plug_body", "plug")
    pprof = [(0.0018, 0.0088), (0.0100, 0.0088), (0.0112, 0.0082), (0.0118, 0.0076), (0.0195, 0.0071),
             (0.0200, 0.0064), (0.0215, 0.0061), (0.0222, 0.0055), (0.0245, 0.0052), (0.0252, 0.0046),
             (0.0280, 0.0042), (PLUG_L, 0.0029)]
    if lod == 0:
        lathe(pb, sf, pprof, 12, cap1=True, rfun=lambda i, k, r: r - 0.0005 * (k % 2) if i in (0, 1) else r)
    else:
        lathe(pb, sf, [pprof[0], pprof[2], pprof[4], pprof[6], pprof[10], pprof[11]], 8, cap1=True)
    parts.append(pb)
    return parts


# --- stand ----------------------------------------------------------------------------------------
def build_rest(spec):
    """Stand: a cast plate, a tray with a sponge at the front, a steel fin under the coil, the coil."""
    lod = spec["lod"]
    parts = []
    bs = P("rest_base", "rest")
    slab(bs, rrect(RX0 + 0.003, RX1 - 0.003, TRAY_Y1 - 0.004, RY1, 0.004, 2 if lod == 0 else 1), (0, 1), 0.0,
         BASE_H, bev=0.0018 if lod == 0 else 0.0, seg=1, ends=(1,))
    parts.append(bs)
    tr = P("tray", "rest")
    slab(tr, rrect(RX0, RX1, RY0, TRAY_Y1, 0.006, 3 if lod == 0 else 1), (0, 1), 0.0, TRAY_H,
         bev=0.0015 if lod == 0 else 0.0, seg=1, ends=(1,))
    cut = P("tray_cut", "rest")
    slab(cut, rrect(RX0 + 0.005, RX1 - 0.005, RY0 + 0.005, TRAY_Y1 - 0.005, 0.0035, 2 if lod == 0 else 1), (0, 1),
         0.006, TRAY_H + 0.01)
    parts.append(M.boolean("tray_%d" % lod, tr, [cut]))
    x0, x1, y0, y1, z1 = SPONGE
    parts.append(boxp("sponge", "sponge", x0, x1, y0, y1, 0.006, z1, **({"r": 0.0025, "seg": 2} if lod == 0 else {})))
    # fin: a 2 mm steel sheet in the plane x = XA from the plate to the bottom of the coil, the top follows
    # the coil
    fin = P("fin", "rest")
    prof = []
    ys = [0.040 - 0.007 * i for i in range(7)] if lod == 0 else [0.040, 0.026, 0.012, -0.002]
    for y in ys:
        s = (T0.y - y) / math.cos(ELEV)
        prof.append((y, T0.z + s * math.sin(ELEV) - (spiral_r(s) + SP_W) / math.cos(ELEV) + 0.0008))
    prof = [(0.044, BASE_H - 0.001)] + prof + [(-0.006, BASE_H - 0.001)]
    g.prism(fin, prof, (1, 2), XA - 0.001, XA + 0.001)
    parts.append(fin)
    if lod == 0:
        # fin flange on the plate and two screws
        parts.append(boxp("fin_foot", "rest", XA - 0.009, XA + 0.009, -0.006, 0.044, BASE_H - 0.0005, BASE_H + 0.0015,
                          r=0.0008, seg=1))
        sc = P("fin_screws", "screw")
        for y, sxx in ((0.002, -1), (0.036, 1)):
            lathe(sc, frame_n((XA + sxx * 0.0055, y, BASE_H + 0.0015), (0, 0, 1), (1, 0, 0)),
                  [(0.0, 0.0022), (0.0008, 0.0019), (0.0012, 0.0009)], 8, cap1=True)
        parts.append(sc)
    sp = P("spiral", "spiral")
    chord, sides, k = spec["spiral"]
    helix(sp, chord, sides, SP_PITCH * k)
    parts.append(sp)
    return parts


def spiral_r(s):
    t = min(max((s - SP_S0) / (SP_S1 - SP_S0), 0.0), 1.0)
    return SP_R0 + (SP_R1 - SP_R0) * t


def helix(part, chord, sides, pitch):
    """Conical coil around the iron axis: wire SP_W, the section is built from the radial direction of the
    turn (like the M69 spring), so it does not twist. The step per turn is the chord chord (at least 8
    steps per turn): wide upper turns are not faceted, narrow lower ones do not waste faces."""
    bm = part.bm
    th_end = 2 * math.pi * (SP_S1 - SP_S0) / pitch
    ths = [0.0]
    while ths[-1] < th_end - 1e-9:
        s = SP_S0 + ths[-1] * pitch / (2 * math.pi)
        ths.append(min(th_end, ths[-1] + min(2 * math.pi / 8, chord / spiral_r(s))))
    a = Vector((1, 0, 0))
    b = D.cross(a).normalized()
    rings = []
    for th in ths:
        s = SP_S0 + th * pitch / (2 * math.pi)
        r = spiral_r(s)
        nrm = a * math.cos(th) + b * math.sin(th)
        tan = (-a * math.sin(th) + b * math.cos(th)) * (2 * math.pi * r) + D * pitch
        bi = tan.normalized().cross(nrm).normalized()
        h = on_axis(s) + nrm * r
        rings.append([bm.verts.new(h + (nrm * math.cos(2 * math.pi * k / sides) + bi * math.sin(2 * math.pi * k / sides))
                                   * SP_W) for k in range(sides)])
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            faces.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    faces += [bm.faces.new(rings[0][::-1]), bm.faces.new(rings[-1])]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    part.tag(faces)


def build_iron(spec):
    """Iron along axis D: each coaxial step is a part of its own, solids of revolution butt-jointed."""
    lod = spec["lod"]
    parts = []
    for i, (name, region, prof) in enumerate(IRON):
        p = P(name, region)
        small = prof[-1][1] < 0.004
        n = (10 if lod == 0 else 6) if small else spec["iron"]
        lathe(p, IFRAME, prof if lod == 0 else thin(prof), n, cap0=(i == 0), cap1=(i == len(IRON) - 1))
        parts.append(p)
    return parts


# --- cords ----------------------------------------------------------------------------------------
MAINS_PLUG = (0.040, UY1 + 0.037)       # cord-side end of the Euro plug (x, y); flat, pins to the right


def iron_cable_points():
    """Iron cord: from the tail along the axis, in an arc to the right and down past the stand, along the
    shelf in front of the unit to the tail of the plug in the socket (the last segment follows the plug
    axis, along +Y)."""
    e = on_axis(S_END)
    e1 = on_axis(S_END + 0.012)
    cx, cz = SOCK
    yb = YP - PLUG_L                    # end of the plug tail
    r = CABLE_R + 0.0002
    return [tuple(e), tuple(e1), (0.068, e1.y - 0.007, e1.z + 0.005), (0.083, e1.y - 0.012, e1.z),
            (0.097, e1.y - 0.013, e1.z - 0.024), (0.105, e1.y - 0.011, 0.120), (0.108, e1.y - 0.008, 0.070),
            (0.107, e1.y - 0.005, 0.030), (0.099, e1.y - 0.003, 0.008), (0.084, -0.124, r), (0.050, -0.127, r),
            (0.024, -0.128, r + 0.0004), (0.009, -0.127, 0.008), (-0.002, -0.123, 0.0175),
            (cx + 0.001, -0.116, 0.0243), (cx, yb - 0.005, cz - 0.0003), (cx, yb, cz)]


def mains_points():
    """Mains cord: from the entry at the back left along its axis, down to the shelf, along the back edge to
    the right, to the tail of the plug."""
    r = CORD_R + 0.0002
    vx, vy = MAINS_PLUG
    return [(-0.082, UY1 + 0.013, 0.028), (-0.082, UY1 + 0.019, 0.0265), (-0.081, UY1 + 0.026, 0.018),
            (-0.077, UY1 + 0.031, 0.007), (-0.068, UY1 + 0.034, r), (-0.045, UY1 + 0.037, r), (-0.015, UY1 + 0.041, r),
            (0.008, UY1 + 0.042, r), (0.020, vy + 0.001, r + 0.0005), (vx - 0.010, vy, 0.007)]


def build_cables(spec):
    lod, n = spec["lod"], spec["cable"]
    parts = []
    turn, seg = (11.0, 0.022) if lod == 0 else (30.0, 0.05)
    cb = P("iron_cable", "cable")
    g.pipe(cb, smooth_path(iron_cable_points(), turn, seg, floor=CABLE_R + 0.0002), CABLE_R, n)
    parts.append(cb)
    # mains cord entry (ribbed) and the cord
    gr = P("cord_grommet", "cord")
    gprof = [(0.0, 0.0062), (0.0030, 0.0060), (0.0040, 0.0050), (0.0065, 0.0046), (0.0072, 0.0039), (0.0135, 0.0030)]
    lathe(gr, frame_n((-0.082, UY1, 0.028), (0, 1, 0), (1, 0, 0)), gprof if lod == 0 else thin(gprof),
          spec["small"], cap1=True)
    parts.append(gr)
    cd = P("mains_cord", "cord")
    g.pipe(cd, smooth_path(mains_points(), turn, seg, floor=CORD_R + 0.0002), CORD_R, 8 if lod == 0 else 5)
    parts.append(cd)
    # the Euro plug lies flat: a body, a tail towards the cord, insulated pins to the right
    vx, vy = MAINS_PLUG
    pl = P("mains_plug", "plug")
    g.box(pl, vx, vx + 0.036, vy - 0.0115, vy + 0.0115, 0.0, 0.014, **({"r": 0.004, "seg": 1} if lod == 0 else {}))
    lathe(pl, frame_n((vx + 0.001, vy, 0.007), (-1, 0, 0), (0, 1, 0)),
          [(0.0, 0.0054), (0.0045, 0.0046), (0.0110, 0.0030)] if lod == 0 else
          [(0.0, 0.0054), (0.0110, 0.0030)], spec["small"], cap1=True)
    parts.append(pl)
    pins = P("mains_pins", "chrome")
    sl = P("mains_pin_sleeves", "plug")
    for dy in (-0.0095, 0.0095):
        pf = frame_n((vx + 0.036 - 0.001, vy + dy, 0.007), (1, 0, 0), (0, 1, 0))
        if lod == 0:
            lathe(sl, pf, [(0.0, 0.0021), (0.0100, 0.0021)], 8)
            lathe(pins, pf, [(0.0100, 0.0020), (0.0180, 0.0020), (0.0195, 0.0011)], 8, cap1=True)
        else:
            lathe(pins, pf, [(0.0, 0.0020), (0.0195, 0.0012)], 6, cap1=True)
    parts.append(pins)
    if lod == 0:
        parts.append(sl)
    return parts


def build_lod(spec):
    parts = build_unit(spec) + build_panel(spec) + build_rest(spec) + build_iron(spec) + build_cables(spec)
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("bounds", BOUNDS)
    return parts


def collision():
    """One convex hull: the unit with the reel, the stand and the iron with the coil; the cords have no
    collision (as in M45 and M69). The mass is the item weight in the mod, 0.8 kg."""
    pts = kx.box_pts(UX0, UX1, UY0, UY1, 0.0, UZ1 + 0.024)
    pts += kx.box_pts(RX0, RX1, RY0, RY1, 0.0, TRAY_H)
    for s, r in ((0.0, 0.004), (SP_S1, SP_R1 + SP_W), (S_END, 0.011)):
        c = on_axis(s)
        for k in range(8):
            a = 2 * math.pi * (k + 0.5) / 8
            pts.append(tuple(c + IFRAME.u * (r * math.cos(a)) + IFRAME.v * (r * math.sin(a))))
    comps = [(pts, kx.PEN + r"\metalplate.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    memory = {
        # inventory preview camera: from the front left and above (invView is where the camera is)
        "invView": [(-0.24, -0.46, 0.34)],
        "ce_center": [(0.0, 0.0, 0.09)],
        "ce_radius": [(0.14, 0.0, 0.09)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


# the first four are the --look preview (general view, panel, stand with the iron, rear); the "working"
# state uses the first two (general view, panel: the key and the heating lamp are lit)
SHOTS = [
    ("front", (-0.18, -0.52, 0.30), (0.0, -0.01, 0.07), 40),
    ("panel", (-0.07, -0.30, 0.10), (-0.042, -0.075, 0.050), 45),
    ("rest", (0.32, -0.28, 0.22), (0.060, -0.01, 0.08), 45),
    ("back", (0.30, 0.46, 0.26), (0.0, 0.02, 0.06), 40),
    ("top", (0.08, -0.26, 0.55), (0.0, 0.0, 0.08), 40),
    ("left", (-0.48, -0.12, 0.17), (-0.04, 0.0, 0.06), 45),
]

M.look_shots = (4, 2)
M.run(build_lod, collision, SHOTS, row_step=0.32, row_shot=((0.16, -1.1, 0.35), (0.16, 0, 0.09)))
