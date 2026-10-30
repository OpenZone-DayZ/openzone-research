"""M72 - Oscilloscope (OZL_Tool_Oscilloscope): a module of the "Electronics" line - a portable 2x2 item,
it stands in slot OZL_Tool1 of the line's packers (M05 Scientists, M11 CN; slot 1 = M72) and is
visible on their shelf through a proxy.

    blender --background --python build_m72.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (panel, screen, sides, slots). The
layout of the face and sides is m72_layout.py, shared with make_decals.py. The "working" screen frames
are drawn by m72_screen.py directly in the build (from decal_screen.png, numpy in Blender).

Target, variant A: a Soviet compact oscilloscope S1-94 - a grey case, a screen with a green grid,
knobs, two probes; longer than the module platform, it stands along the depth of the shelf.

Detailing: "dayz" look (matte, dirtier, coloured AO); a case with rounded edges and screws at the
back, block feet with bevels, a CRT window with a bevelled mask, knurled knobs with chrome caps,
switch caps with a chamfer, buttons with a rounded face, a neon "power" lamp in a mount; probes with a
connector with a bayonet sleeve and a tail, a body with a finger stop, a tip with a hook sleeve, a
ground wire with an alligator clip; a round Soviet mains plug with a tail; the cables are smooth
(spline, 10 faces, a coil of 18 points per turn).
"Working" (modules in slots work together with the machine): the screen ozl_screen has its own
texture (section screen, flat UV 0..1): "off" is a blanked tube with a grid (decal_screen.png),
"working" is 12 frames with a running signal (OZL_WorkFx frames); the "power" lamp ozl_lamp is the _on
atlas (burns steadily, onSelections). The device has no moving parts - no bones.
There are no vanilla items (proxies) in the model: the module is picked up and carried in the
inventory, so the items would travel with it; small items by the slot belong to the machine.

Reference and sizes:
- S1-94 (USSR State Register of Measuring Instruments No. 6791-78, type description; belgim 06791-78
  from search results - the file itself did not open): 100 x 190 x 300 mm, 3.5 kg; the working part of
  the screen is 60 x 40 mm (the same line in M05). The current ProfKiP S1-94M is 130 x 190 x 280 mm,
  3 kg (eskomp.ru, the ProfKiP description), i.e. the same order. Photos of the front and the left
  side (a lot listing): the front proportions 325 x 603 px (1 : 1.86) match 100 x 190, the side
  matches 300 in length including the knobs and the power supply box.
- From the photos: a grey-green U-shaped cover (top and sides) on a tray with two rows of slots, black
  block feet underneath and a fold-out chrome stand bracket; the face is a light grey-green control
  panel (the "time / div." and "volt / div." switches with aluminium caps and beak-shaped skirts, small
  knobs, the Y input and external trigger sockets, six buttons, a case terminal, the dot of the "power"
  lamp above the power button), above it a black screen panel (a CRT window 69 x 55 mm with a 10 x 8
  division grid, focus and brightness knobs) and a light strip without captions; at the back a
  perforated power supply box, a fuse holder, a cord entry, an angle bracket; on the left side two
  trimmer holes and a slot.
- Probes: a divider probe ~D 11 x 90 mm with a hook and a ground wire on a clip; cable D 4.4. One
  probe is plugged into the Y input, the cable goes left along the shelf, the probe lies at the left
  side tip back, with the ground wire and clip behind it; the second is wound into a round coil at the
  back edge of the roof, the probe and connector lie in front of it. The mains cord is white, a round
  plug at the right side (pins 4 mm at 19 mm).

Fit: the module_N platforms of M05 and M11 are on a shelf 0.30 m deep with a 15 mm rim along the front
edge, the proxy is in the middle of the depth. The oscilloscope stands at the centre of the proxy: the
knobs are at the shelf edge (y -0.150), the power supply box at its back edge (+0.149), so it does
not hang off the shelf although the platform (0.22 x 0.24) is shorter; only the probe connector in the
Y input with the bend of the cable goes past the edge to -0.164 - at a height of 0.02-0.04, above the
rim. Everything is above z 0, the probes and cord lie on the shelf within the platform in width
(x -0.096..0.086). The height with the coil, probe and connector on the roof is 0.205 m (0.25
available).

Shared instruments and modules: enamel worn at the edges, small chips, a little rust at the bottom, the
button plastic slightly yellowed; everything intact. No faction colour. Marks: scales with digits,
pictograms without letters, an empty light strip, an inventory sticker with a number, a drop of
locking paint on the slot.

LODs (a small item): near - 4.96 k triangles (the guideline for modules is 0.5-1.5 k; almost half is
cables: 10 faces, otherwise they shade faceted), middle - 1.09 k (~22 %: no bracket, small knob caps,
fuse holder, angle bracket, screws, ground wire, plug pins; cables and solids of revolution coarser),
no far one.

Blender axes: X is width, Y is depth (the front face is -Y), Z is up. The origin is the centre of the
bottom: this is how the module stands on the module_N proxy point (autocenter = 0 in Geometry).
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
import m72_layout as L  # noqa: E402
import m72_screen  # noqa: E402
from mathutils import Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

# --- dimensions, m --------------------------------------------------------------------------------
X0, X1 = -L.W / 2, L.W / 2
ZC0 = 0.020                     # bottom of the cover (the tray is under it)
YF = -0.137                     # face of the cover frame
YB = -0.135                     # face of the black screen panel
YL = -0.1345                    # face of the light strip
YP = -0.134                     # face of the control panel
YC0 = -0.130                    # front of the cover (behind the panels)
YR = 0.123                      # back of the cover
YSCR = -0.1315                  # CRT glass in the window
MASK = 0.0015                   # bevel of the CRT window mask (it reaches onto the screen field beyond the grid)
KNOB_R, KNOB_L = 0.0050, 0.013  # small knobs
CABLE_R = 0.0022                # probe cable
CORD_R = 0.0025                 # mains cord
LEAD_R = 0.0009                 # probe ground wire
PROBE_R = 0.0058                # probe body
PROBE_LIE = PROBE_R + 0.0017    # axis of a lying probe: it rests on the finger stop
PLUG_R, PLUG_L = 0.0068, 0.021  # probe connector with a tail
ZT = L.Z_TOP + CABLE_R          # axis of the coil on the roof
LAMP = (0.0262, L.BUTTONS[0] + 0.0055)                    # "power" lamp at the dot by the power button
# mains plug: lies on its side, the axis along -y; tail, face, pins
PLUG_X, PLUG_BR = 0.074, 0.0105
PLUG_Y0, PLUG_Y1 = -0.006, -0.038
CLIP_O, CLIP_Z = (-0.068, 0.095), 0.0026                  # tip of the ground clip (tail towards -y), axis height

LOD_SPECS = [
    dict(lod=0, sides=16),
    dict(lod=1, sides=8),
]

REGIONS = {
    "case": ("case", 1.0), "tray": ("tray", 1.0), "psu": ("psu", 1.0), "panel": ("panel", 2.6),
    "bezel": ("bezel", 1.0), "strip": ("strip", 1.0), "screen": ("screen", 1.0), "knob": ("knob", 1.5),
    "chrome": ("chrome", 1.5), "skirt": ("skirt", 1.5), "button": ("button", 1.5), "socket": ("socket", 1.0),
    "rubber": ("rubber", 0.6), "cable": ("cable", 0.6), "cord": ("cord", 0.6), "probe": ("probe", 1.0),
    "plug": ("plug", 1.0), "fuse": ("fuse", 1.0), "seal": ("seal", 1.0), "lamp": ("lamp", 3.0),
    "clip": ("clip", 2.0),
}


def wdecal(name):
    return os.path.join(WORK, name)


def mid(a):
    return (a[0] + a[1]) / 2


PANEL_DEC = (wdecal("decal_panel.png"), "y", -1, ("x", "z"), (mid(L.PANEL_X), mid(L.PANEL_Z)),
             (L.PANEL_X[1] - L.PANEL_X[0], L.PANEL_Z[1] - L.PANEL_Z[0]), (YP - 0.001, YP + 0.001))
SIDE_DEC = (wdecal("decal_side.png"), "x", -1, ("y", "z"), L.SIDE_C, L.SIDE_WH, (X0 - 0.001, X0 + 0.001))
TAG_DEC = (wdecal("decal_tag.png"), "x", 1, ("y", "z"), L.SIDE_TAG, L.TAG_WH, (X1 - 0.001, X1 + 0.001))
VENT_DECS = [(wdecal("decal_vents.png"), "x", s, ("y", "z"), L.VENT_C, L.VENT_WH, (s * 0.049 - 0.001, s * 0.049 + 0.001))
             for s in (1, -1)]
PSU_ZC, PSU_H = mid(L.PSU_Z), L.PSU_Z[1] - L.PSU_Z[0]
PSU_DECS = [(wdecal("decal_psu_back.png"), "y", 1, ("x", "z"), (mid(L.PSU_X), PSU_ZC), (L.PSU_X[1] - L.PSU_X[0], PSU_H),
             (L.PSU_Y[1] - 0.001, L.PSU_Y[1] + 0.001))]
PSU_DECS += [(wdecal("decal_psu_side.png"), "x", s, ("y", "z"), (mid(L.PSU_Y), PSU_ZC), (L.PSU_Y[1] - L.PSU_Y[0], PSU_H),
              (s * L.PSU_X[1] - 0.001, s * L.PSU_X[1] + 0.001)) for s in (1, -1)]

# worn, small chips, a little rust at the bottom
USED = dict(chip=(0.66, 0.72), rust=(0.80, 0.86), rust_low=0.25, floor_z=0.0, dust=0.25, grime=0.40)
CASE = kmats.lin((150, 157, 147))       # grey-green enamel of the cover
UNDER = kmats.lin((70, 72, 74))

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "case": ("paint", dict(USED, color=CASE, under=UNDER, seed=2.2, gloss=0.40, spec=0.30,
                           decal_items=[SIDE_DEC, TAG_DEC])),
    "tray": ("paint", dict(USED, color=kmats.lin((128, 134, 126)), under=UNDER, seed=2.7, gloss=0.35, spec=0.25,
                           decal_items=VENT_DECS)),
    "psu": ("paint", dict(USED, color=CASE, under=UNDER, seed=3.1, gloss=0.40, spec=0.30, decal_items=PSU_DECS)),
    "panel": ("paint", dict(USED, color=kmats.lin((170, 188, 180)), under=kmats.lin((150, 152, 150)), seed=3.6,
                            gloss=0.40, spec=0.30, chip=(0.78, 0.82), rust_low=0.0, decal_items=[PANEL_DEC])),
    "bezel": ("plastic", dict(color=kmats.lin((36, 40, 46)), seed=4.1, gloss=0.35, spec=0.25, dust=0.1, grime=0.15,
                              scuff=(0.85, 0.95))),
    "strip": ("steel", dict(seed=4.6, tone=0.62, along="x", gloss=0.5, spec=0.55, dust=0.08, grime=0.1)),
    # the screen is a section of its own (panels): not in the atlas, only the part needs to see it
    "screen": ("flat", dict(color=kmats.lin((34, 92, 76)), gloss=0.85, spec=0.7)),
    "knob": ("plastic", dict(color=kmats.lin((24, 24, 25)), seed=5.8, gloss=0.5, spec=0.4, dust=0.05, grime=0.1,
                             scuff=(0.80, 0.88))),
    "chrome": ("steel", dict(seed=5.2, tone=0.52, along="z", gloss=0.7, spec=0.8, dust=0.08, grime=0.15)),
    "skirt": ("plastic", dict(color=kmats.lin((208, 206, 196)), seed=6.3, gloss=0.45, spec=0.35, dust=0.05,
                              grime=0.15, scuff=(0.85, 0.95))),
    "button": ("plastic", dict(color=kmats.lin((232, 218, 194)), seed=6.9, gloss=0.45, spec=0.35, dust=0.05,
                               grime=0.2, scuff=(0.8, 0.9))),
    "socket": ("flat", dict(color=kmats.lin((12, 12, 12)), gloss=0.2, spec=0.1)),
    "cable": ("plastic", dict(color=kmats.lin((40, 40, 42)), seed=8.2, gloss=0.35, spec=0.2, dust=0.15, grime=0.2,
                              scuff=(0.9, 1.0))),
    "cord": ("plastic", dict(color=kmats.lin((224, 220, 204)), seed=8.6, gloss=0.3, spec=0.2, dust=0.25, grime=0.3,
                             scuff=(0.9, 1.0))),
    "probe": ("plastic", dict(color=kmats.lin((30, 30, 32)), seed=9.1, gloss=0.45, spec=0.35, dust=0.05, grime=0.1,
                              scuff=(0.82, 0.9))),
    "plug": ("plastic", dict(color=kmats.lin((232, 228, 214)), seed=9.6, gloss=0.4, spec=0.3, dust=0.2, grime=0.3,
                             scuff=(0.85, 0.95))),
    "fuse": ("plastic", dict(color=kmats.lin((112, 34, 26)), seed=10.1, gloss=0.5, spec=0.35, dust=0.1, grime=0.2)),
    "seal": ("plastic", dict(color=kmats.lin((150, 40, 30)), seed=10.6, gloss=0.6, spec=0.4, dust=0.1, grime=0.1)),
    # neon "power" lamp: off is brownish glass, when working it burns orange
    "lamp": ("flat", dict(color=kmats.lin((92, 46, 30)), gloss=0.85, spec=0.8)),
    "lamp_on": ("flat", dict(color=kmats.lin((255, 132, 52)), gloss=0.85, spec=0.8)),
    # alligator clip of the ground wire: nickel-plated steel
    "clip": ("steel", dict(seed=11.2, tone=0.46, along="y", gloss=0.6, spec=0.7, dust=0.1, grime=0.35)),
})

OBJ, NAME = "m72_oscilloscope", "ozr_oscilloscope"
SEL_SCREEN, SEL_LAMP = "ozl_screen", "ozl_lamp"
# "working" state: the lamp is lit (atlas _on), the screen shows frames (its own screen texture)
ON = dict(remap={"lamp": "lamp_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
SCREEN = dict(off="decal_screen.png", frames=[m72_screen.FRAME % i for i in range(m72_screen.N_FRAMES)], size=512,
              gloss=0.8)
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL_SCREEN, SEL_LAMP), hidden=(SEL_SCREEN, SEL_LAMP), states={"on": ON},
                 panels={"screen": SCREEN})
M.look_shots = (4, 2)
P = M.part
BOUNDS = {}


# =============================================================================
# Primitives missing from kgeo
# =============================================================================
def boxp(name, region, x0, x1, y0, y1, z0, z1, **kw):
    p = P(name, region, **{k: kw.pop(k) for k in ("uv_name", "uv_origin", "group") if k in kw})
    g.box(p, x0, x1, y0, y1, z0, z1, **kw)
    return p


def face(part, verts, want):
    """Face from bmesh vertices, oriented towards want (as in M16)."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def basis(d):
    d = Vector(d).normalized()
    a = d.cross(Vector((0.0, 0.0, 1.0)))
    if a.length < 0.1:
        a = d.cross(Vector((1.0, 0.0, 0.0)))
    a.normalize()
    return a, a.cross(d).normalized()


def ring(c, d, r, n, depth=0.0):
    """A ring of points around axis d at point c; depth is knurling: 2n points, every other one sunk."""
    a, b = basis(d)
    m = 2 * n if depth else n
    return [Vector(c) + (a * math.cos(2 * math.pi * k / m) + b * math.sin(2 * math.pi * k / m)) *
            (r - depth * (k % 2)) for k in range(m)]


def lathe(part, o, d, prof, n, depth=0.0, cap0=False, cap1=True):
    """Solid of revolution along d from o: prof is [(distance, radius)]; the end cap0 is at o (usually
    hidden in the panel, not needed), cap1 at the far end. The sides face outwards from the axis."""
    bm = part.bm
    o, d = Vector(o), Vector(d).normalized()
    vs = [[bm.verts.new(q) for q in ring(o + d * t, d, r, n, depth)] for t, r in prof]
    new = []
    m = len(vs[0])
    for i in range(len(vs) - 1):
        for k in range(m):
            j = (k + 1) % m
            q = [vs[i][k], vs[i][j], vs[i + 1][j], vs[i + 1][k]]
            c = sum((v.co for v in q), Vector()) / 4 - o
            new.append(face(part, q, c - d * c.dot(d)))
    if cap0:
        new.append(face(part, vs[0], -d))
    if cap1:
        new.append(face(part, vs[-1], d))
    bm.normal_update()
    return part.tag(new)


def front_bevel_box(part, x0, x1, y0, y1, z0, z1, r):
    """A box with a rounded (two-step chamfer) face at -Y: buttons, keys."""
    bm = part.bm
    before = set(bm.faces)
    g.box(part, x0, x1, y0, y1, z0, z1)
    new = [f for f in bm.faces if f not in before]
    front = [f for f in new if f.normal.y < -0.9]
    g.bevel(bm, list(front[0].edges), r, 2)
    new = [f for f in bm.faces if f not in before]
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


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
    out.append(v[-1])
    return [tuple(q) for q in out]


def thin(pts, deg=9.0):
    """Drop points where the cable barely turns: a ring is kept when the turn accumulated since the last
    ring has reached deg - on a bend the kink of each ring is ~deg, straight runs get no extra rings."""
    v = [Vector(p) for p in pts]
    out, acc = [v[0]], 0.0
    for i in range(1, len(v) - 1):
        a, b = v[i] - v[i - 1], v[i + 1] - v[i]
        if a.length > 1e-9 and b.length > 1e-9:
            acc += math.degrees(a.angle(b, 0.0))
        if acc >= deg:
            out.append(v[i])
            acc = 0.0
    out.append(v[-1])
    return [tuple(q) for q in out]


def lift(pts, r):
    """Cable on the shelf: the spline sags below the points on a bend - but not below the floor (z >= r)."""
    return [(x, y, max(z, r)) for x, y, z in pts]


def disc(part, x, y, z, r, n):
    """A flat n-gon facing -Y (a cap, a hole): one face instead of a thin cylinder."""
    return g.quad(part, [(x + r * math.cos(2 * math.pi * k / n), y, z + r * math.sin(2 * math.pi * k / n))
                         for k in range(n)])


# =============================================================================
# Case: cover, face frame, tray, feet, bracket
# =============================================================================
def build_case(spec):
    lod = spec["lod"]
    # the cover is a bent sheet: the edges are rounded (two bevel steps read as a radius in the light)
    bev = dict(r=0.003, seg=2) if lod == 0 else {}
    parts = [boxp("cover", "case", X0, X1, YC0, YR, ZC0, L.Z_TOP, **bev)]
    # the frame is the front edge of the cover around the panels; three separate parts so that the inner
    # and outer side faces do not share one atlas rectangle
    t = 0.0025
    parts.append(boxp("frame_l", "case", X0, X0 + t, YF, YC0, L.FOOT_H + 0.001, L.Z_TOP))
    parts.append(boxp("frame_r", "case", X1 - t, X1, YF, YC0, L.FOOT_H + 0.001, L.Z_TOP))
    parts.append(boxp("frame_t", "case", X0 + t, X1 - t, YF, YC0, L.Z_TOP - t, L.Z_TOP))
    parts.append(boxp("tray", "tray", X0 + 0.001, X1 - 0.001, YC0 + 0.001, YR - 0.002, L.FOOT_H, ZC0,
                      **(dict(r=0.0012, seg=1) if lod == 0 else {})))
    # feet: black blocks across the bottom at the front and back, bevelled below
    for i, (y0, y1) in enumerate(((-0.132, -0.102), (0.091, 0.121))):
        ft = P("foot%d" % i, "rubber", uv_name="foot", uv_origin=(0.0, mid((y0, y1)), 0.0))
        zt = L.FOOT_H + 0.001
        poly = [(y0 + 0.004, 0.0), (y1 - 0.004, 0.0), (y1, 0.004), (y1, zt), (y0, zt), (y0, 0.004)]
        g.prism(ft, poly if lod == 0 else [(y0, 0.0), (y1, 0.0), (y1, zt), (y0, zt)], (1, 2), -0.046, 0.046)
        parts.append(ft)
    if lod == 0:
        # fold-out stand bracket: folded under the bottom, its axes at the front feet
        bl = P("bail", "chrome")
        xs = 0.0515
        g.pipe(bl, [(-xs, -0.112, 0.013), (-xs, -0.060, 0.010), (-xs + 0.002, -0.050, 0.0065), (-0.040, -0.046, 0.0045),
                    (0.040, -0.046, 0.0045), (xs - 0.002, -0.050, 0.0065), (xs, -0.060, 0.010), (xs, -0.112, 0.013)], 0.0015, 6)
        parts.append(bl)
        # the bracket axes are rivets in the sides of the front block
        for s in (-1, 1):
            pv = P("bail_pivot%d" % (s > 0), "chrome", uv_name="bail_pivot", uv_origin=(s * 0.046, -0.112, 0.013))
            lathe(pv, (s * 0.046, -0.112, 0.013), (s, 0, 0), [(0.0, 0.0024), (0.0060, 0.0018)], 6)
            parts.append(pv)
    return parts


# =============================================================================
# Face: panels, screen, knobs, buttons, sockets, lamp
# =============================================================================
def small_knob(name, x, yb, z, lod):
    """Small knob: a knurled black cylinder with a chrome cap on the end."""
    kb = P(name, "knob", uv_name="knob", uv_origin=(x, yb, z))
    out = [kb]
    if lod == 0:
        lg = KNOB_L * 0.84
        lathe(kb, (x, yb, z), (0, -1, 0), [(0.0, KNOB_R), (lg, KNOB_R)], 14, depth=0.00035)
        cp = P(name + "_cap", "chrome", uv_name="knob_cap", uv_origin=(x, yb, z))
        lathe(cp, (x, yb, z), (0, -1, 0), [(lg - 0.0003, KNOB_R * 0.74), (KNOB_L, KNOB_R * 0.66)], 10)
        out.append(cp)
    else:
        lathe(kb, (x, yb, z), (0, -1, 0), [(0.0, KNOB_R), (KNOB_L, KNOB_R * 0.9)], 6)
    return out


def build_front(spec):
    lod = spec["lod"]
    parts = [boxp("panel", "panel", L.PANEL_X[0], L.PANEL_X[1], YP, YC0, L.PANEL_Z[0], L.PANEL_Z[1]),
             boxp("strip", "strip", L.PANEL_X[0], L.PANEL_X[1], YL, YC0, L.STRIP_Z[0], L.STRIP_Z[1])]
    # the black screen panel is four bars around the window (each a part of its own: the top of the lower
    # bar is visible in the window, the top of the upper one is hidden under the strip - in one rectangle
    # they would conflict)
    (cx, cz), (w, h) = L.SCREEN_C, L.SCREEN_WH
    sx0, sx1, sz0, sz1 = cx - w / 2, cx + w / 2, cz - h / 2, cz + h / 2
    bx0, bx1 = L.PANEL_X
    bz0, bz1 = L.BEZEL_Z
    for name, x0, x1, z0, z1 in (("bezel_b", bx0, bx1, bz0, sz0), ("bezel_t", bx0, bx1, sz1, bz1),
                                 ("bezel_l", bx0, sx0, sz0, sz1), ("bezel_r", sx1, bx1, sz0, sz1)):
        parts.append(boxp(name, "bezel", x0, x1, YB, YC0, z0, z1))
    # window mask: a bevel from the panel face to the CRT glass, reaching onto the dark screen field beyond
    # the grid
    mk = P("screen_mask", "bezel")
    ys = YSCR - 0.0003
    outer = [(sx0, YB, sz0), (sx1, YB, sz0), (sx1, YB, sz1), (sx0, YB, sz1)]
    inner = [(sx0 + MASK, ys, sz0 + MASK), (sx1 - MASK, ys, sz0 + MASK), (sx1 - MASK, ys, sz1 - MASK),
             (sx0 + MASK, ys, sz1 - MASK)]
    vo = [mk.bm.verts.new(q) for q in outer]
    vi = [mk.bm.verts.new(q) for q in inner]
    mk.tag([face(mk, [vo[k], vo[(k + 1) % 4], vi[(k + 1) % 4], vi[k]], (0, -1, 0)) for k in range(4)])
    parts.append(mk)
    # screen: its own texture (section screen, UV 0..1 over the x-z extent), selection ozl_screen
    sc = P("screen", "screen", group=SEL_SCREEN, section="screen")
    g.quad(sc, [(sx0, YSCR, sz0), (sx1, YSCR, sz0), (sx1, YSCR, sz1), (sx0, YSCR, sz1)])
    parts.append(sc)
    # small knobs: focus and brightness by the screen, X shift, level, Y shift on the panel
    for i, ((x, z), yb) in enumerate([(q, YB) for q in L.SCR_KNOBS] +
                                     [(q, YP) for q in (L.KNOB_POS_X, L.KNOB_LEVEL, L.KNOB_POS_Y)]):
        parts += small_knob("knob%d" % i, x, yb, z, lod)
    # large switches: a beak-shaped skirt with a black mark and an aluminium cap with a chamfer
    for i, ((x, z), ptr, nlab) in enumerate(((L.BIG_T, L.T_POINTER, len(L.T_LABELS)),
                                             (L.BIG_V, L.V_POINTER, len(L.V_LABELS)))):
        a_ptr = math.radians(L.SCALE_A0 + (L.SCALE_A1 - L.SCALE_A0) * ptr / (nlab - 1))
        poly = []
        m = 16 if lod == 0 else 8
        for k in range(m):
            a = a_ptr + 2 * math.pi * k / m
            d = abs((a - a_ptr + math.pi) % (2 * math.pi) - math.pi)
            r = L.BIG_SKIRT_R + 0.0045 * max(0.0, 1.0 - d / math.radians(36)) ** 1.4
            poly.append((x + r * math.cos(a), z + r * math.sin(a)))
        sk = P("skirt%d" % i, "skirt")
        g.prism(sk, poly, (0, 2), YP, YP - 0.005)
        parts.append(sk)
        ca, sa = math.cos(a_ptr), math.sin(a_ptr)
        r0, r1, hw = L.BIG_CAP_R + 0.0008, L.BIG_SKIRT_R + 0.0038, 0.0007
        pt = P("pointer%d" % i, "knob")
        g.prism(pt, [(x + r0 * ca + hw * sa, z + r0 * sa - hw * ca), (x + r1 * ca + hw * sa, z + r1 * sa - hw * ca),
                     (x + r1 * ca - hw * sa, z + r1 * sa + hw * ca), (x + r0 * ca - hw * sa, z + r0 * sa + hw * ca)],
                (0, 2), YP - 0.005, YP - 0.0056)
        parts.append(pt)
        cp = P("bigcap%d" % i, "chrome", uv_name="bigcap", uv_origin=(x, YP, z))
        R = L.BIG_CAP_R
        if lod == 0:
            lathe(cp, (x, YP - 0.005, z), (0, -1, 0), [(0.0, R * 0.97), (0.0094, R), (0.0110, R * 0.95), (0.0120, R * 0.78)], 14)
        else:
            lathe(cp, (x, YP - 0.005, z), (0, -1, 0), [(0.0, R), (0.012, R * 0.93)], 8)
        parts.append(cp)
    # buttons: light plastic, a rounded face
    bw, bh = L.BTN_WH
    for i, z in enumerate(L.BUTTONS):
        bt = P("btn%d" % i, "button", uv_name="btn", uv_origin=(L.BTN_X, YP, z))
        if lod == 0:
            front_bevel_box(bt, L.BTN_X - bw / 2, L.BTN_X + bw / 2, YP - 0.006, YP, z - bh / 2, z + bh / 2, 0.0009)
        else:
            g.box(bt, L.BTN_X - bw / 2, L.BTN_X + bw / 2, YP - 0.006, YP, z - bh / 2, z + bh / 2)
        parts.append(bt)
    # neon "power" lamp in a chrome mount (selection ozl_lamp: lit when working)
    lx, lz = LAMP
    if lod == 0:
        lb = P("lamp_bezel", "chrome")
        lathe(lb, (lx, YP, lz), (0, -1, 0), [(0.0, 0.0021), (0.0010, 0.0021), (0.0012, 0.0016)], 10)
        parts.append(lb)
    ln = P("lamp", "lamp", group=SEL_LAMP)
    lathe(ln, (lx, YP, lz), (0, -1, 0), [(0.0010, 0.0012), (0.0020, 0.00112), (0.0026, 0.0004)]
          if lod == 0 else [(0.0010, 0.0013), (0.0024, 0.0008)], 10 if lod == 0 else 6)
    parts.append(ln)
    # external trigger socket: a hex nut and a dark hole
    jx, jz = L.JACK_TRIG
    if lod == 0:
        jk = P("jack", "chrome")
        lathe(jk, (jx, YP, jz), (0, -1, 0), [(0.0, 0.0047), (0.0026, 0.0047), (0.0031, 0.0040)], 6)
        parts.append(jk)
        jh = P("jack_hole", "socket")
        disc(jh, jx, YP - 0.0032, jz, 0.0021, 8)
        parts.append(jh)
    # Y input: the socket ring (the probe connector sits in it, build_probes)
    ix, iz = L.INPUT_Y
    ir = P("input_ring", "chrome")
    g.cyl(ir, (ix, YP - 0.0015, iz), "y", 0.0080, 0.003, 12 if lod == 0 else 6)
    parts.append(ir)
    # case terminal: a nut and a knurled cap
    gx, gz = L.GROUND
    gn = P("ground_nut", "chrome")
    g.cyl(gn, (gx, YP - 0.0015, gz), "y", 0.0046, 0.003, 6)
    parts.append(gn)
    if lod == 0:
        gc = P("ground_cap", "chrome")
        lathe(gc, (gx, YP, gz), (0, -1, 0), [(0.0029, 0.0038), (0.0082, 0.0038), (0.0090, 0.0031)], 10)
        parts.append(gc)
    return parts


# =============================================================================
# Back: power supply box, fuse, cord entry, bracket, seal, screws
# =============================================================================
def build_rear(spec):
    lod = spec["lod"]
    parts = [boxp("psu", "psu", L.PSU_X[0], L.PSU_X[1], L.PSU_Y[0] - 0.001, L.PSU_Y[1], L.PSU_Z[0], L.PSU_Z[1],
                  **(dict(r=0.0012, seg=1) if lod == 0 else {}))]
    if lod == 0:
        gr = P("grommet", "rubber")
        lathe(gr, (0.022, YR, 0.040), (0, 1, 0), [(0.0, 0.0046), (0.0030, 0.0042), (0.0090, 0.0030)], 10)
        parts.append(gr)
        # fuse holder: a hex nut and a knurled head
        fn = P("fuse_nut", "chrome")
        lathe(fn, (-0.022, YR, 0.050), (0, 1, 0), [(0.0, 0.0056), (0.0026, 0.0056)], 6)
        parts.append(fn)
        fu = P("fuse", "fuse")
        lathe(fu, (-0.022, YR, 0.050), (0, 1, 0), [(0.0024, 0.0044), (0.0118, 0.0040)], 6, depth=0.0004)
        parts.append(fu)
        # angle bracket at the bottom back: a post, a shelf, a bent edge
        parts.append(boxp("bracket_v", "case", -0.026, 0.026, YR - 0.001, YR + 0.0015, 0.013, 0.040))
        parts.append(boxp("bracket_h", "case", -0.026, 0.026, YR + 0.0015, 0.149, 0.013, 0.0148))
        parts.append(boxp("bracket_lip", "case", -0.026, 0.026, 0.1472, 0.149, 0.0148, 0.024))
        # cover screws at the back corners; the top right one has a mastic seal
        for i, (x, z) in enumerate(((-0.042, 0.183), (-0.042, 0.030), (0.042, 0.030))):
            sw = P("screw%d" % i, "chrome", uv_name="screw", uv_origin=(x, YR, z))
            lathe(sw, (x, YR, z), (0, 1, 0), [(0.0, 0.0029), (0.0006, 0.0028), (0.0013, 0.0017)], 6)
            parts.append(sw)
        se = P("seal", "seal")
        lathe(se, (0.042, YR, 0.183), (0, 1, 0), [(0.0, 0.0036), (0.0010, 0.0034), (0.0020, 0.0024), (0.0025, 0.0010)], 6)
        parts.append(se)
    return parts


# =============================================================================
# Probes and cord
# =============================================================================
def along(o, d, t):
    return (o[0] + d[0] * t, o[1] + d[1] * t, o[2] + d[2] * t)


def plug(name, o, d, lod):
    """Probe connector: end o, along d a bayonet sleeve (nickel), a body and a tail (black); the cable
    leaves at along(o, d, PLUG_L)."""
    sl = P(name + "_sleeve", "chrome", uv_name="plug_sleeve", uv_origin=o)
    bd = P(name, "probe", uv_name="plug_body", uv_origin=o)
    if lod == 0:
        lathe(sl, o, d, [(0.0, PLUG_R - 0.0007), (0.0007, PLUG_R), (0.0072, PLUG_R), (0.0080, PLUG_R - 0.0006)], 10,
              cap0=True)
        lathe(bd, o, d, [(0.0076, 0.0058), (0.0126, 0.0058), (0.0136, 0.0045), (0.0160, 0.0040), (PLUG_L, 0.0029)], 10)
    else:
        lathe(sl, o, d, [(0.0, PLUG_R), (0.008, PLUG_R)], 6, cap0=True)
        lathe(bd, o, d, [(0.008, 0.0058), (PLUG_L, 0.0030)], 6)
    return [sl, bd]


def probe_body(name, o, d, lod):
    """Divider probe from the tail o (where the cable enters) to the tip along d: a soft tail, a body, a
    finger stop, a tip."""
    prof = [(0.0, 0.0026), (0.010, 0.0034), (0.0135, 0.0047), (0.019, PROBE_R), (0.058, PROBE_R),
            (0.0612, PROBE_R + 0.0017), (0.0650, PROBE_R + 0.0012), (0.0800, 0.0033), (0.0880, 0.0022)]
    if lod > 0:
        prof = [prof[0], prof[3], prof[5], prof[6], prof[8]]
    p = P(name, "probe")
    lathe(p, o, d, prof, 10 if lod == 0 else 5, cap0=True)
    return p


def probe_tip(name, o, d):
    """At the tip o along d: a sleeve and a steel hook bent up and back."""
    sv = P(name + "_sleeve", "chrome", uv_name="tip_sleeve", uv_origin=o)
    lathe(sv, o, d, [(-0.0005, 0.0013), (0.0040, 0.0011)], 6)
    hk = P(name, "chrome")
    up = (0.0, 0.0, 1.0)
    e = along(o, d, 0.0095)
    g.pipe(hk, [along(o, d, 0.003), e, along(along(o, d, 0.0118), up, 0.0010), along(along(o, d, 0.0122), up, 0.0024),
                along(along(o, d, 0.0110), up, 0.0034), along(along(o, d, 0.0093), up, 0.0036)], 0.00065, 4)
    return [sv, hk]


def ground_clip(lod):
    """The alligator clip of the ground wire lies on its side: the jaws are two steel strips (closed at the
    tip, spreading towards the rivet), a rivet, a soft black cap on the tail."""
    ox, oy = CLIP_O
    if lod > 0:
        return [boxp("clip1", "clip", ox - 0.0025, ox + 0.0025, oy - 0.024, oy, 0.0, 0.0045)]
    fr = g.Frame((ox, oy, CLIP_Z), (0, -1, 0), (0, 0, 1), (1, 0, 0))
    jaw = P("clip1", "clip")
    prof = [(0.0, 0.0004), (0.010, 0.0008), (0.016, 0.0016), (0.022, 0.0030), (0.028, 0.0040)]
    for s in (1, -1):
        g.sweep(jaw, [fr.p(a, 0.0, s * c) for a, c in prof], fr.v, 0.00028, 0.0021)
    g.cyl(jaw, (0.0165, 0.0, 0.0), "y", 0.0008, 0.0050, 6, frame=fr)        # rivet
    boot = P("clip1_boot", "probe")
    sec = [(0.0185, 0.0030, 0.0021), (0.0225, 0.0042, 0.0025), (0.0310, 0.0044, 0.0025), (0.0370, 0.0034, 0.0021),
           (0.0410, 0.0016, 0.0013)]
    g.tube_var(boot, [fr.p(a, 0.0, 0.0) for a, _, _ in sec], [(rh, rv) for _, rh, rv in sec], 8)
    return [jaw, boot]


def build_probes(spec):
    lod = spec["lod"]
    # cables: 10 faces - under 40 degrees between faces, so the LOD and the preview shade them smooth
    # (kexport, krender: a sharp edge starts at 40 degrees); fewer rings - the spline is sparser, straight
    # runs have no rings
    ks = 4 if lod == 0 else 1
    cs = 10 if lod == 0 else 5
    tdeg = 11.0 if lod == 0 else 24.0
    parts = []
    r = CABLE_R
    # probe 1: the connector is in the Y input, the cable goes left and along the shelf by the left side to
    # the probe tail; the probe lies by the side, tip back (taken out and put aside), the ground wire with
    # the clip behind it
    ix, iz = L.INPUT_Y
    o1 = (ix, YP - 0.001, iz)
    parts += plug("plug1", o1, (0, -1, 0), lod)
    px, pz, py = -0.088, PROBE_LIE, -0.056
    path = [along(o1, (0, -1, 0), PLUG_L), (ix - 0.005, -0.162, iz - 0.002), (-0.053, -0.161, iz - 0.006),
            (-0.060, -0.152, 0.017), (-0.062, -0.138, 0.009), (-0.063, -0.122, r + 0.0015), (-0.065, -0.100, r),
            (-0.072, -0.082, r), (-0.082, -0.068, r + 0.001), (px, py - 0.004, pz - 0.0008), (px, py + 0.002, pz)]
    cb = P("cable1", "cable")
    g.pipe(cb, lift(thin(spline(path, ks), tdeg), r), r, cs)
    parts.append(cb)
    parts.append(probe_body("probe1", (px, py, pz), (0, 1, 0), lod))
    if lod == 0:
        parts += probe_tip("tip1", (px, py + 0.088, pz), (0, 1, 0))
        # ground wire: from the probe stop along the shelf to the clip
        gl = P("glead1", "cable")
        g.pipe(gl, lift(thin(spline([(px + 0.0045, py + 0.060, pz - 0.0005), (-0.0790, py + 0.068, 0.0030),
                                     (-0.0745, py + 0.080, 0.0), (-0.0705, py + 0.094, 0.0), (CLIP_O[0], CLIP_O[1] - 0.0405, CLIP_Z)], 3),
                             15.0), LEAD_R), LEAD_R, 6)
        parts.append(gl)
    parts += ground_clip(lod)
    # probe 2: the cable is wound into a round coil at the back edge of the roof (two turns from the
    # outside in, counter-clockwise); the probe lies in front of the coil, tip forward, the inner end is
    # thrown across the turns to the connector on the right
    ccx, ccy, turns = 0.0, 0.078, 2.0
    m = 18 if lod == 0 else 7
    coil = []
    for k in range(int(m * turns) + 1):
        t = k / m
        a = -math.pi / 2 + 2 * math.pi * t
        rr = 0.037 - 0.0045 * t
        coil.append((ccx + rr * math.cos(a), ccy + rr * math.sin(a), ZT))
    zp, zg = L.Z_TOP + PROBE_LIE, L.Z_TOP + PLUG_R
    pb = (-0.012, 0.028, zp)                                  # probe tail, the tip points forward
    lead_probe = [pb, (-0.012, 0.034, zp - 0.002), (-0.007, 0.039, ZT + 0.001), coil[0]]
    o2 = (0.022, -0.001, zg)                                  # end of the connector, the tail points back
    e2 = along(o2, (0, 1, 0), PLUG_L)
    xover = ZT + 2 * r + 0.0003                               # above the two turns
    lead_plug = [coil[-1], (0.011, coil[-1][1] + 0.001, ZT + 0.002), (0.021, 0.047, xover), (0.026, 0.040, xover),
                 (0.024, 0.030, zg - 0.002), e2]
    c2 = P("cable2", "cable")
    g.pipe(c2, thin(spline(lead_probe, ks), tdeg + 2)[:-1] + coil + thin(spline(lead_plug, ks), tdeg + 2)[1:], r, cs)
    parts.append(c2)
    parts += plug("plug2", o2, (0, 1, 0), lod)
    parts.append(probe_body("probe2", pb, (0, -1, 0), lod))
    if lod == 0:
        parts += probe_tip("tip2", along(pb, (0, -1, 0), 0.088), (0, -1, 0))
    # mains cord: entry at the back, through the bracket onto the shelf, along the right side, the plug lies
    # by the side
    q = CORD_R
    cord = [(0.022, YR + 0.008, 0.040), (0.022, 0.133, 0.035), (0.024, 0.138, 0.024), (0.028, 0.140, 0.0148 + q),
            (0.036, 0.141, 0.0148 + q), (0.044, 0.142, 0.011), (0.052, 0.139, 0.005), (0.060, 0.130, q),
            (0.066, 0.110, q), (0.068, 0.075, q), (0.069, 0.035, q), (0.071, 0.012, q), (0.073, 0.002, 0.0060),
            (PLUG_X, PLUG_Y0 + 0.002, PLUG_BR)]
    cd = P("cord", "cord")
    g.pipe(cd, lift(thin(spline(cord, ks), tdeg + 3), q), q, cs)
    parts.append(cd)
    # plug: a round Soviet one, lying on its side; the tail towards the cord, the face with pins forward
    pl = P("cord_plug", "plug")
    po = (PLUG_X, PLUG_Y0, PLUG_BR)
    ln = PLUG_Y0 - PLUG_Y1
    lathe(pl, po, (0, -1, 0), [(0.0, 0.0031), (0.006, 0.0040), (0.010, 0.0072), (0.013, 0.0098), (ln - 0.002, PLUG_BR),
                               (ln, PLUG_BR - 0.0012)] if lod == 0 else [(0.0, 0.0035), (0.012, PLUG_BR), (ln, PLUG_BR)],
          10 if lod == 0 else 6, cap0=True)
    parts.append(pl)
    if lod == 0:
        for i, dx in enumerate((-0.0095, 0.0095)):
            pn = P("cord_pin%d" % i, "chrome", uv_name="cord_pin", uv_origin=(PLUG_X + dx, PLUG_Y1, PLUG_BR))
            lathe(pn, (PLUG_X + dx, PLUG_Y1 + 0.001, PLUG_BR), (0, -1, 0),
                  [(0.0, 0.0020), (0.0170, 0.0020), (0.0185, 0.0012)], 6)
            parts.append(pn)
    return parts


def build_lod(spec):
    parts = build_case(spec) + build_front(spec) + build_rear(spec) + build_probes(spec)
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """Three convex parts: the case with the knobs, the box at the back and the coil on the roof; the probe
    with the cable on the left of the shelf; the cord with the plug on the right. The mass is the item
    weight in the mod, 0.8 kg."""
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    body = kx.box_pts(X0, X1, -0.152, 0.149, 0.0, hi[2])
    left = kx.box_pts(-0.101, X0, -0.165, 0.101, 0.0, 0.014)
    right = kx.box_pts(X1, 0.087, -0.058, 0.145, 0.0, 0.021)
    comps = [(body, kx.PEN + r"\metalplate.rvmat"), (left, kx.PEN + r"\plastic.rvmat"),
             (right, kx.PEN + r"\plastic.rvmat")]
    memory = {
        # inventory preview camera: from the front left and above (invView is where the camera is)
        "invView": [(-0.36, -0.56, 0.42)],
        "ce_center": [(0.0, 0.0, 0.10)],
        "ce_radius": [(0.17, 0.0, 0.10)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


SHOTS = [
    ("front", (-0.26, -0.58, 0.34), (0.0, -0.01, 0.10), 40),
    ("panel", (-0.03, -0.34, 0.12), (0.0, -0.13, 0.095), 45),
    ("probes", (-0.27, -0.30, 0.17), (-0.072, -0.040, 0.012), 50),
    ("top", (0.30, -0.38, 0.52), (0.0, 0.0, 0.12), 40),
    ("left", (-0.52, 0.10, 0.24), (-0.04, 0.0, 0.08), 40),
    ("back", (0.34, 0.50, 0.30), (0.0, 0.04, 0.09), 40),
]

# the "working" screen frames come from the blanked screen of make_decals.py; --bake-part copies and
# quick checks do not need them
if not any(a in ARGV for a in ("--stats", "--uv-hash", "--bake-part")):
    m72_screen.make_frames(WORK, os.path.join(WORK, "renders") if ("--look" in ARGV or "--look-render" in ARGV) else None)

M.run(build_lod, collision, SHOTS, row_step=0.40, row_shot=((0.20, -1.35, 0.42), (0.20, 0, 0.10)))
