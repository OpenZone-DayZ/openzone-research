"""M45 - the Centrifuge (OZL_Tool_Centrifuge): a module of the "Bio" line and of the shared
laboratory - a portable 2x2 item that stands in the OZL_Tool1..3 slots of the packer and is
seen on its shelf through a proxy.

    blender --background --python build_m45.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: make_decals.py with the system Python (the timer scale, the
tachometer "off" and "working" - without a needle, which is a part now; the rotation arrow,
the tag).

Card: a benchtop laboratory centrifuge - a cylindrical body with a lid, a timer knob, a
cable, light enamel; ~0.22 x 0.18 x 0.22 m. A module fits ~0.2 x 0.2 m at the base and up
to ~0.25 m tall (the module_N pad).

Reference and dimensions:
- the look - MPW-2 (Poland, 1970s): a cylinder of light enamel on short feet, a lid hinged
  at the back, flat panels at the front bottom with a timer knob and a dial tachometer; a
  second photo shows the same class in grey enamel with the cable at the back and a round
  hole in the center of the lid;
- benchtop clinical centrifuges of the era: OPn-3 - 445 x 430 x 235 mm, ~15 kg; BD Clay
  Adams Compact II (420225, 1980s) - 10 1/2 x 14 1/2 x 8 1/2" = 267 x 368 x 216 mm; Hettich
  EBA 20 (until 2015) - 231 x 292 x 216 mm, ~4 kg. The smallest are ~0.23 m at the base and
  ~0.22 m tall, which does not fit the 0.2 x 0.2 module pad. So the module is a centrifuge
  of the EBA 20 / Compact II class scaled down to about 0.8: body D 190 mm, height with the
  lid 181 mm; timer knob D 25 mm, tachometer window 34 x 28 mm (MPW-2 proportions). The
  cable goes back and lies on the floor behind the body, the plug is at the rear left (~3 cm
  beyond the pad - the module rules allow this);
- the in-mod weight is 800 g (OZL_Tool_Base, unchanged); the mass in Geometry is the same.

Look: "dayz" (matte, more worn); the body, lid, knobs and lamp are solids of revolution with
rounded edges (drum 32 sides, lid 28, was 24), the bottom is a rounded "circle with a chord"
for the panel with a rubber gasket along its outline; small instrument details - panel
screws, a nameplate on rivets, a hinge of three knuckles with a pin and plates on screws, a
bracket latch with a mushroom, a vent grille and a fuse holder at the back, a ribbed cord
inlet, a round plug with two pins, the tachometer glass, a knurled timer knob with a
pointer. The cord is a smooth curve (g.pipe). There are no vanilla items: the module is
taken in the hands and put into a slot, nothing lies on it.

"Working" look of the machine: the "mains" signal lamp and the tachometer scale are
ozl_lamp_work (working - the _on atlas: the lamp is lit red, the scale is lit, steadily,
onSelections). Moving parts:
- the rotor under the round window in the lid (glass, the glass section; the window is a
  hole in the lid): hub with a nut and a red mark, a spider, four cups with test tubes - the
  bone ozl_work on the source ozl_work: a model.cfg loop (sourceAddress loop, maxValue 1/5)
  - 5 turns per pass, a pass takes 2 s (animPeriod in the mod config), 2.5 turns per second:
  at 30 fps the mark moves 30 degrees per frame - the rotation reads, it does not "run
  backwards". Clockwise from above, like the arrow on the lid: the axis goes from bottom to
  top, angle1 = 2 pi (with the axis pointing top-down the engine turned counterclockwise;
  the sign rule is at ROTOR_AXIS);
- the tachometer needle - the bone ozl_needle on the source ozl_needle (OZL_WorkFx wobble,
  mid 0.58 - 3500 rpm, amp 0.025, period 2.3 s; animPeriod 0.8 s - run-up to the working
  speed in ~0.5 s). Phase 0 is the scale zero, 1 is the scale end (6): a 90 degree
  clockwise turn as seen from the front. The needle is no longer drawn in the decals
  (make_decals.py) - otherwise its drawn copy would stay at zero while working.
LODs: near 4145 triangles (above the 1.5k small-item guide - for the roundings and small
details) and middle 1380 (33%: no feet, nameplate, screws, grille, fuse, toggle, rotor
cups; the needle is there - it wobbles from afar too), no far LOD.

Blender axes: X - width, Y - depth (front at -Y), Z - up. The origin is the center of the
bottom: this is how the module sits on the module_N proxy point (autocenter = 0 in
Geometry).
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

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- Dimensions, m ----------------------------------------------------------------------------
R = 0.095                       # body
FOOT_H = 0.008                  # rubber feet
BASE_Z1 = 0.062                 # bottom with the panel
SEAM_H = 0.003
DRUM_Z0 = BASE_Z1 + SEAM_H
WALL_Z1 = 0.155                 # straight drum wall, the shoulder is above
SHOULDER_Z, SHOULDER_R = 0.168, 0.0875
CHAMBER_R, CHAMBER_Z0 = 0.0745, 0.088
LID_R, LID_Z1 = 0.083, 0.176
DOME_R, DOME_Z1 = 0.066, 0.181
WIN_R = 0.026                   # round window in the lid (D 52)
WIN_Z = 0.1797                  # window glass
FY = 0.072                      # panel face: the chord of the bottom circle at y = -FY
RF = 0.010                      # rounding of the bottom corners at the chord
PANEL_W, PANEL_H, PANEL_ZC = 0.112, 0.044, 0.035
PY = -FY - 0.0015               # face of the panel plate
TIMER = (-0.032, PANEL_ZC)      # timer knob (x, z)
TIMER_D = 0.054                 # scale square, as in make_decals.py
METER = (0.014, PANEL_ZC + 0.001)
METER_W, METER_H = 0.034, 0.028  # frame; face 0.028 x 0.022 (make_decals.py)
MFD = PY - 0.006                # face of the tachometer frame
MFACE = MFD + 0.003             # scale face
# needle axis: make_decals.py, the arc center is 0.92 of the face height from the top; the
# length is 1.08 of the scale radius
NEEDLE_PIVOT = (METER[0], METER[1] + 0.011 - 0.92 * 0.022)
NEEDLE_L = 0.0145 * 1.08
LAMP = (0.043, 0.046)
TOGGLE = (0.043, 0.022)
ARROW_D = 0.150                 # rotation arrow on the lid: an arc around the window (R ~0.046)
TAG = (0.0, 0.112)              # tag on the right side (y, z)
TAG_W, TAG_H = 0.032, 0.020
CABLE_Z = 0.030
CY = math.sqrt(R * R - 0.03 * 0.03)     # body back at the cord inlet (x = +-0.03)
PLUG = (-0.035, 0.1152, 0.0085)         # start of the plug (cord inlet), the plug lies along -X
ROTOR_TURNS = 5
ROTOR_TOP = 0.1590              # rotor hub top; nut and shaft to 0.1673, chamber open to 0.168

LOD_SPECS = [
    dict(lod=0, sides=32, lid_sides=28, fine=True),
    dict(lod=1, sides=24, lid_sides=24, fine=False),
]

REGIONS = {
    "enamel": ("enamel", 1.0), "lid": ("lid", 1.0), "panel": ("panel", 2.0), "seam": ("seam", 0.6),
    "chrome": ("chrome", 1.0), "knob": ("knob", 2.0), "bezel": ("bezel", 1.5), "meter": ("meter", 4.0),
    "lamp": ("lamp", 1.0), "plate": ("plate", 1.5), "rubber": ("rubber", 0.6), "cable": ("cable", 0.6),
    "plug": ("plug", 1.0), "chamber": ("chamber", 0.3), "rotor": ("rotor", 0.6),
    "rotor_mark": ("rotor_mark", 0.6), "tube_cap": ("tube_cap", 0.5), "grille": ("grille", 1.5),
    "needle": ("needle", 1.0), "pointer": ("pointer", 1.0), "black": ("black", 1.0),
}


def wdecal(name):
    return os.path.join(WORK, name)


TIMER_DEC = (wdecal("decal_timer.png"), "y", -1, ("x", "z"), TIMER, (TIMER_D, TIMER_D), (PY - 0.002, PY + 0.001))
METER_DEC = {st: (wdecal("decal_meter_%s.png" % st), "y", -1, ("x", "z"), METER, (0.028, 0.022),
                  (PY - 0.010, PY - 0.002)) for st in ("off", "on")}
ARROW_DEC = (wdecal("decal_arrow.png"), "z", 1, ("x", "y"), (0.0, 0.0), (ARROW_D, ARROW_D), (LID_Z1 - 0.001, 0.2))
TAG_DEC = (wdecal("decal_tag.png"), "x", 1, ("y", "z"), TAG, (TAG_W, TAG_H), (R - 0.003, R + 0.003))

# Shared instruments: worn on the edges, chips, a little rust at the bottom (worn more than
# before, the enamel darker and yellower - next to the vanilla samples the earlier cream one
# glowed)
USED = dict(chip=(0.56, 0.62), rust=(0.70, 0.77), rust_low=0.45, floor_z=0.0, dust=0.40, grime=0.70)
LIT = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
CREAM = kmats.lin((198, 194, 176))

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "enamel": ("paint", dict(USED, color=CREAM, under=kmats.lin((70, 72, 74)), seed=2.2, gloss=0.45, spec=0.32,
                             yellow=0.35, decal_items=[TAG_DEC])),
    "lid": ("paint", dict(USED, color=kmats.lin((192, 189, 172)), under=kmats.lin((70, 72, 74)), seed=2.9,
                          gloss=0.45, spec=0.32, yellow=0.30, dust=0.45, decal_items=[ARROW_DEC])),
    "panel": ("paint", dict(USED, color=kmats.lin((150, 152, 146)), under=kmats.lin((60, 62, 64)), seed=3.6,
                            gloss=0.4, spec=0.3, rust_low=0.0, decal_items=[TIMER_DEC])),
    "seam": ("plastic", dict(color=kmats.lin((34, 34, 34)), seed=4.1, gloss=0.2, spec=0.15, dust=0.2, grime=0.4,
                             scuff=(0.85, 0.95))),
    "chrome": ("steel", dict(seed=5.2, tone=0.62, along="z", gloss=0.7, spec=0.8, dust=0.15, grime=0.35)),
    "knob": ("plastic", dict(color=kmats.lin((26, 24, 23)), seed=5.8, gloss=0.5, spec=0.4, dust=0.1, grime=0.25,
                             scuff=(0.74, 0.82))),
    "bezel": ("plastic", dict(color=kmats.lin((32, 32, 33)), seed=6.3, gloss=0.45, spec=0.35, dust=0.1, grime=0.2,
                              scuff=(0.84, 0.94))),
    "meter": ("paint", dict(LIT, color=kmats.lin((214, 210, 194)), gloss=0.7, spec=0.5,
                            decal_items=[METER_DEC["off"]])),
    "meter_on": ("paint", dict(LIT, color=kmats.lin((252, 240, 204)), gloss=0.7, spec=0.5,
                               decal_items=[METER_DEC["on"]])),
    "needle": ("flat", dict(color=kmats.lin((20, 20, 20)), gloss=0.4, spec=0.3)),
    "pointer": ("plastic", dict(color=kmats.lin((226, 222, 210)), seed=6.6, gloss=0.4, spec=0.3, dust=0.1,
                                grime=0.2, scuff=(0.9, 1.0))),
    "lamp": ("flat", dict(color=kmats.lin((96, 26, 20)), gloss=0.85, spec=0.8)),
    "lamp_on": ("flat", dict(color=kmats.lin((255, 70, 40)), gloss=0.85, spec=0.8)),
    "plate": ("steel", dict(seed=7.1, tone=0.62, along="x", gloss=0.5, spec=0.55, dust=0.1, grime=0.2)),
    "grille": ("steel", dict(seed=7.5, tone=0.42, along="x", holes=(("x", "z"), 0.0045, 0.28), gloss=0.4, spec=0.45,
                             dust=0.5, grime=0.5)),
    "cable": ("plastic", dict(color=kmats.lin((30, 30, 31)), seed=8.2, gloss=0.25, spec=0.15, dust=0.3, grime=0.35,
                              scuff=(0.85, 0.95))),
    "plug": ("plastic", dict(color=kmats.lin((34, 33, 32)), seed=8.7, gloss=0.35, spec=0.25, dust=0.2,
                             grime=0.3, scuff=(0.78, 0.88))),
    # rotor chamber: grey enamel, grime and dust on the bottom
    "chamber": ("paint", dict(USED, color=kmats.lin((92, 94, 92)), under=kmats.lin((150, 150, 146)), seed=9.1,
                              gloss=0.25, spec=0.2, chip=(0.76, 0.82), dust=0.45, grime=0.7)),
    # rotor: cast aluminium; the mark is red paint; the test tube caps are blue plastic
    "rotor": ("steel", dict(seed=9.4, tone=0.55, along="z", gloss=0.5, spec=0.6, dust=0.1, grime=0.35)),
    "rotor_mark": ("paint", dict(LIT, color=kmats.lin((176, 40, 30)), gloss=0.4, spec=0.3)),
    "tube_cap": ("plastic", dict(color=kmats.lin((40, 76, 150)), seed=9.8, gloss=0.4, spec=0.3, dust=0.1, grime=0.2)),
})

OBJ, NAME = "m45_centrifuge", "ozr_centrifuge"
SEL_LAMP, SEL_ROTOR, SEL_NEEDLE = "ozl_lamp_work", "ozl_work", "ozl_needle"
NEEDLE_MID, NEEDLE_AMP = 0.58, 0.025            # needle while working: wobble mid +- amp
# Bone axes are memory points (collision). The engine turns a bone with a right-hand screw in
# DayZ axes (kexport.conv, determinant -1); in Blender axes this is a left-hand screw around
# the axis from the first point to the second: an axis pointing at the viewer gives a
# positive angle clockwise for them (as in M08, M12, M14, M33). So the needle axis points to
# the viewer (-Y) and the rotor axis goes from bottom to top (toward someone looking from
# above); the reverse directions turn the needle counterclockwise, past zero and off the
# scale, and the rotor against the arrow on the lid.
NEEDLE_AXIS = [(NEEDLE_PIVOT[0], MFD, NEEDLE_PIVOT[1]), (NEEDLE_PIVOT[0], MFD - 0.010, NEEDLE_PIVOT[1])]
ROTOR_AXIS = [(0.0, 0.0, ROTOR_TOP - 0.040), (0.0, 0.0, ROTOR_TOP + 0.010)]


def engine_turn(axis_pts, ang):
    """Turn of a bone by angle ang as the engine would do it by the memory axis axis_pts: (a point
    on the axis, the Blender axis for Matrix.Rotation - a right-hand screw, the angle). The
    Blender axis is opposite to the memory axis (from the second point to the first).
    """
    a, b = Vector(axis_pts[0]), Vector(axis_pts[1])
    return a, a - b, ang


def check_turns():
    """Numeric check: the engine's turn takes the tachometer needle at phases 0, mid +- amp and 1
    clockwise along the scale (from the front 135 -> 45 degrees), the tip stays in the scale
    window (face 0.028 x 0.022); the rotor turns clockwise as seen from above (like the arrow
    on the lid). If it does not match, the build fails.
    """
    c = Vector(NEEDLE_AXIS[0])
    tip = c + Vector((math.cos(math.radians(135)), 0.0, math.sin(math.radians(135)))) * NEEDLE_L
    seen = []
    for ph in (0.0, NEEDLE_MID - NEEDLE_AMP, NEEDLE_MID, NEEDLE_MID + NEEDLE_AMP, 1.0):
        o, ax, ang = engine_turn(NEEDLE_AXIS, ph * math.pi / 2)
        q = o + Matrix.Rotation(ang, 3, ax) @ (tip - o)
        deg = math.degrees(math.atan2(q.z - c.z, q.x - c.x))
        assert abs(deg - (135.0 - 90.0 * ph)) < 0.01, "the needle goes the wrong way: %.1f" % deg
        assert abs(q.x - METER[0]) < 0.014 and abs(q.z - METER[1]) < 0.011, "the needle tip is outside the scale: phase %.2f" % ph
        seen.append("%.2f -> %.1f" % (ph, deg))
    o, ax, ang = engine_turn(ROTOR_AXIS, math.radians(10.0))
    q = o + Matrix.Rotation(ang, 3, ax) @ Vector((0.05, 0.0, 0.0))
    assert q.y < -0.005, "the rotor turns counterclockwise as seen from above"
    print("turns ok: needle (phase -> degrees from the front) " + ", ".join(seen) + "; rotor clockwise from above")


check_turns()
# preview of the working look: the needle at the middle of its sway - by the engine turn
# (the _posed wrapper below)
ON_MOVE = {}
ON = dict(remap={"lamp": "lamp_on", "meter": "meter_on"}, emissive=(1.0, 1.0, 1.0, 1.0), move=ON_MOVE)
# rotor is a loop: 5 turns per pass of the ozl_work source (2 s); the axis goes from bottom to top
# (ROTOR_AXIS)
ROTOR_ANIM = ("ozl_work_rotor", dict(type="rotation", source="ozl_work", sourceAddress="loop", selection=SEL_ROTOR,
                                     axis="ozl_work_axis", memory=1, minValue=0.0, maxValue=1.0 / ROTOR_TURNS,
                                     angle0=0.0, angle1=2 * math.pi))
# needle: phase 0 is the scale zero, 1 is "6" (90 degrees clockwise facing the front); the axis
# points from the face to the viewer (NEEDLE_AXIS)
NEEDLE_ANIM = ("ozl_needle_turn", dict(type="rotation", source="ozl_needle", selection=SEL_NEEDLE,
                                       axis="ozl_needle_axis", memory=1, minValue=0.0, maxValue=1.0,
                                       angle0=0.0, angle1=math.pi / 2))
# glass of the lid window and tachometer: nearly clear, dusty near the frame
GLASS = dict(base=(0.62, 0.66, 0.64), clear=0.03, edge=0.12, smudge=0.06, streaks=0.03)
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz", glass=GLASS,
                 selections=(SEL_LAMP, SEL_ROTOR, SEL_NEEDLE), hidden=(SEL_LAMP,), states={"on": ON},
                 bones=((SEL_ROTOR, ""), (SEL_NEEDLE, "")), animations=(ROTOR_ANIM, NEEDLE_ANIM),
                 sources={"ozl_work": dict(animPeriod=2.0), "ozl_needle": dict(animPeriod=0.8)})
P = M.part
BOUNDS = {}


# =============================================================================
# Primitives that kgeo lacks
# =============================================================================
AXES = {"x": (1, 0, 0), "-x": (-1, 0, 0), "y": (0, 1, 0), "-y": (0, -1, 0), "z": (0, 0, 1), "-z": (0, 0, -1)}


def use(p, region):
    """The following primitives of the part go into this region (look and scale: REGIONS)."""
    return p.use(region, *REGIONS[region])


def _basis(axis):
    a = Vector(AXES[axis] if isinstance(axis, str) else axis).normalized()
    ref = Vector((1, 0, 0)) if abs(a.z) > 0.9 else Vector((0, 0, 1))
    e1 = (ref - a * ref.dot(a)).normalized()
    return a, e1, a.cross(e1)            # e1 x e2 = a


def lathe(part, prof, sides, center=(0.0, 0.0, 0.0), axis="z", closed=False, a0=0.0, a1=None, flute=None,
          regions=None):
    """Solid of revolution: prof [(r, h)] around axis from center. The profile goes counterclockwise
    in the plane (r to the right, h up): from the bottom along the outer side up, along the top
    toward the axis - normals outward. r = 0 is a pole. closed - the profile is closed. a0..a1 -
    part of a turn (plates on the body; for a closed profile the ends are capped). flute =
    (number of ribs, fraction of the radius, {ring numbers}) - fluting. regions - a region per
    profile belt.
    """
    bm = part.bm
    ax, e1, e2 = _basis(axis)
    c0 = Vector(center)
    full = a1 is None
    n_ang = sides if full else sides + 1
    span = 2 * math.pi if full else (a1 - a0)
    angs = [a0 + span * k / sides for k in range(n_ang)]
    rings = []
    for i, (r, h) in enumerate(prof):
        if r < 1e-9:
            rings.append(bm.verts.new(c0 + ax * h))
            continue
        ring = []
        for a in angs:
            rr = r * (1.0 + flute[1] * math.cos(flute[0] * a)) if flute and i in flute[2] else r
            ring.append(bm.verts.new(c0 + (e1 * math.cos(a) + e2 * math.sin(a)) * rr + ax * h))
        rings.append(ring)
    nb = len(prof) if closed else len(prof) - 1
    new = []
    for i in range(nb):
        r0, r1 = rings[i], rings[(i + 1) % len(prof)]
        idx = part.region_index(regions[i], *REGIONS[regions[i]]) if regions else part.cur
        p0, p1 = not isinstance(r0, list), not isinstance(r1, list)
        if p0 and p1:
            continue
        for k in range(sides):
            j = (k + 1) % n_ang
            vs = [r0, r1[j], r1[k]] if p0 else ([r0[k], r0[j], r1] if p1 else [r0[k], r0[j], r1[j], r1[k]])
            f = bm.faces.new(vs)
            f[part.reg] = idx
            new.append(f)
    if not full and closed:
        for k in (0, n_ang - 1):
            f = bm.faces.new([rg[k] if isinstance(rg, list) else rg for rg in rings])
            f[part.reg] = part.cur
            new.append(f)
        bmesh.ops.recalc_face_normals(bm, faces=new)
    return new


def loft(part, rings, cap0=False, cap1=False, closed=False, recalc=False):
    """Surface through closed contours rings (the same number of points; the contour is
    counterclockwise seen from above, the rings go from the bottom up: normals outward). closed -
    the last ring joins the first (a frame), recalc - recompute the normals (a closed body).
    """
    bm = part.bm
    vr = [[bm.verts.new(Vector(q)) for q in ring] for ring in rings]
    n = len(vr[0])
    new = []
    for i in range(len(vr) if closed else len(vr) - 1):
        r0, r1 = vr[i], vr[(i + 1) % len(vr)]
        for k in range(n):
            j = (k + 1) % n
            new.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    if cap0:
        new.append(bm.faces.new(vr[0][::-1]))
    if cap1:
        new.append(bm.faces.new(vr[-1]))
    for f in new:
        f[part.reg] = part.cur
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=new)
    return new


def base_outline(d, n_arc, n_fil, n_ch):
    """Bottom outline: circle R with a chord at the front (y = -FY) and rounded corners RF, inset
    by d; counterclockwise from above, from the left end of the chord.
    """
    rc, yc, rf = R - d, FY - d, max(RF - d, 0.0015)
    xc, ycf = math.sqrt((rc - rf) ** 2 - (yc - rf) ** 2), -yc + rf
    phi = math.atan2(ycf, xc)
    pts = [(-xc + 2 * xc * i / n_ch, -yc) for i in range(n_ch)]
    pts += [(xc + rf * math.cos(-math.pi / 2 + (phi + math.pi / 2) * i / n_fil),
             ycf + rf * math.sin(-math.pi / 2 + (phi + math.pi / 2) * i / n_fil)) for i in range(n_fil)]
    pts += [(rc * math.cos(phi + (math.pi - 2 * phi) * i / n_arc), rc * math.sin(phi + (math.pi - 2 * phi) * i / n_arc))
            for i in range(n_arc)]
    b0 = math.pi - phi
    pts += [(-xc + rf * math.cos(b0 + (1.5 * math.pi - b0) * i / n_fil),
             ycf + rf * math.sin(b0 + (1.5 * math.pi - b0) * i / n_fil)) for i in range(n_fil)]
    return pts


def rrect(cx, cz, w, h, rc, y, n=2):
    """Rounded rectangle in the x-z plane at depth y: n + 1 points per corner."""
    pts = []
    for sx, sz, a0 in ((1, -1, -90), (1, 1, 0), (-1, 1, 90), (-1, -1, 180)):
        ccx, ccz = cx + sx * (w / 2 - rc), cz + sz * (h / 2 - rc)
        for i in range(n + 1):
            a = math.radians(a0 + 90.0 * i / max(n, 1))
            pts.append((ccx + rc * math.cos(a), y, ccz + rc * math.sin(a)))
    return pts


def frame_on(pos, nrm):
    """Local system: origin pos, n is the surface normal."""
    n = Vector(nrm).normalized()
    ref = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = ref.cross(n).normalized()
    return g.Frame(pos, u, n.cross(u), n)


def screw(part, pos, nrm, r=0.0020, h=0.0010, sides=8):
    """Screw head (rivet) - a low truncated cone along the normal nrm, slightly sunk."""
    g.cyl(part, (0, 0, h / 2 - 0.0003), "z", r, h, sides, r2=r * 0.72, frame=frame_on(pos, nrm))


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, as in M38)."""
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


def boxp(name, region, x0, x1, y0, y1, z0, z1, **kw):
    p = P(name, region)
    g.box(p, x0, x1, y0, y1, z0, z1, **kw)
    return p


def arc_deg(a):
    return math.radians(a)


# =============================================================================
# Body
# =============================================================================
def build_body(spec):
    lod, n, fine = spec["lod"], spec["sides"], spec["fine"]
    parts = []
    # bottom: a "circle with a chord", rounded below; the top is covered by the gasket and the drum
    base = P("base", "enamel")
    if fine:
        oc, prof = (30, 3, 3), [(0.003, FOOT_H), (0.0011, FOOT_H + 0.0011), (0.0, FOOT_H + 0.003), (0.0, BASE_Z1)]
    else:
        oc, prof = (16, 1, 2), [(0.002, FOOT_H), (0.0, FOOT_H + 0.002), (0.0, BASE_Z1)]
    loft(base, [[(x, y, z) for x, y in base_outline(d, *oc)] for d, z in prof], cap0=True)
    parts.append(base)
    # rubber gasket between the bottom and the drum - along the bottom outline
    seam = P("seam", "seam")
    ring = base_outline(0.0018, *oc)
    loft(seam, [[(x, y, z) for x, y in ring] for z in (BASE_Z1 - 0.0008, DRUM_Z0 + 0.002)])
    parts.append(seam)
    # drum: the bottom with a rounded edge (an overhang above the panel), wall, shoulder, ring for
    # the lid
    drum = P("drum", "enamel")
    if fine:
        prof = [(0.070, DRUM_Z0), (R - 0.004, DRUM_Z0), (R - 0.00146, DRUM_Z0 + 0.00146), (R, DRUM_Z0 + 0.004),
                (R, WALL_Z1), (0.0940, 0.1615), (0.09125, 0.16626), (SHOULDER_R, SHOULDER_Z), (0.0755, SHOULDER_Z)]
    else:
        prof = [(0.070, DRUM_Z0), (R - 0.003, DRUM_Z0), (R, DRUM_Z0 + 0.003), (R, WALL_Z1 + 0.002), (0.0915, 0.1652),
                (SHOULDER_R, SHOULDER_Z), (0.0755, SHOULDER_Z)]
    lathe(drum, prof, n)
    parts.append(drum)
    # rotor chamber (visible only through the lid window)
    ch = P("chamber", "chamber")
    if fine:
        lathe(ch, [(0.0755, SHOULDER_Z), (CHAMBER_R, SHOULDER_Z - 0.0015), (CHAMBER_R, CHAMBER_Z0 + 0.003),
                   (CHAMBER_R - 0.0025, CHAMBER_Z0), (0.0, CHAMBER_Z0)], 12)
    else:
        lathe(ch, [(0.0755, SHOULDER_Z), (CHAMBER_R, CHAMBER_Z0 + 0.002), (0.0, CHAMBER_Z0)], 8)
    parts.append(ch)
    # lid: a chrome rim at the bottom, a rounded edge, a step to the shallow dome, a window in the
    # center
    lid = P("lid", "lid")
    if fine:
        prof = [(LID_R + 0.0017, 0.1686), (LID_R + 0.0017, 0.1716), (LID_R + 0.0003, 0.1730), (LID_R - 0.0004, 0.1748),
                (LID_R - 0.002, LID_Z1), (DOME_R + 0.0012, LID_Z1), (DOME_R, 0.1774), (0.0635, 0.1800),
                (0.0590, DOME_Z1), (WIN_R, DOME_Z1), (WIN_R, 0.1700)]
        regs = ["chrome", "chrome"] + ["lid"] * 8
    else:
        prof = [(LID_R + 0.0016, 0.1685), (LID_R + 0.0016, 0.1718), (LID_R, 0.1735), (LID_R - 0.0015, LID_Z1),
                (DOME_R + 0.001, LID_Z1), (DOME_R - 0.003, 0.1802), (0.058, DOME_Z1), (WIN_R, DOME_Z1),
                (WIN_R, 0.1700)]
        regs = ["chrome", "chrome"] + ["lid"] * 6
    lathe(lid, prof, spec["lid_sides"], regions=regs)
    parts.append(lid)
    # window: a chrome ring and the glass
    bz = P("win_ring", "chrome")
    if fine:
        lathe(bz, [(WIN_R - 0.0012, WIN_Z - 0.0002), (WIN_R - 0.0012, 0.1812), (WIN_R + 0.0018, 0.1821),
                   (WIN_R + 0.0042, 0.1806)], 20)
    else:
        lathe(bz, [(WIN_R - 0.0012, WIN_Z - 0.0002), (WIN_R + 0.0010, 0.1820), (WIN_R + 0.0042, 0.1806)], 14)
    parts.append(bz)
    gl = P("win_glass", "black", section="glass")
    lathe(gl, [(WIN_R - 0.0006, WIN_Z), (0.0, WIN_Z)], 20 if fine else 14)
    gl.glass_frame = (g.Frame((0, 0, WIN_Z), (1, 0, 0), (0, 1, 0), (0, 0, 1)), -WIN_R, WIN_R, -WIN_R, WIN_R)
    parts.append(gl)
    parts += build_hinge(spec) + build_latch(spec)
    if fine:
        ft = P("feet", "rubber")
        for k in range(4):
            a = math.radians(45 + 90 * k)
            lathe(ft, [(0.0090, 0.0), (0.0108, 0.0022), (0.0103, FOOT_H + 0.0006)], 6,
                  center=(0.066 * math.cos(a), 0.066 * math.sin(a), 0.0))
        parts.append(ft)
        # blank nameplate on the drum front - following the body curvature, on two rivets
        pl = P("plate", "plate")
        lathe(pl, [(R - 0.0004, 0.118), (R + 0.0008, 0.118), (R + 0.0008, 0.134), (R - 0.0004, 0.134)], 6,
              closed=True, a0=arc_deg(-90 - 12.2), a1=arc_deg(-90 + 12.2))
        use(pl, "chrome")
        for s in (-1, 1):
            a = arc_deg(-90 + s * 10.4)
            screw(pl, (math.cos(a) * (R + 0.0008), math.sin(a) * (R + 0.0008), 0.126), (math.cos(a), math.sin(a), 0),
                  r=0.0013, h=0.0007, sides=6)
        parts.append(pl)
        # body screws on the sides and the motor vent grille at the back
        sc = P("body_screws", "chrome")
        for s in (-1, 1):
            screw(sc, (s * (R - 0.0002), 0.0, 0.075), (s, 0, 0))
        parts.append(sc)
        gr = P("grille", "grille")
        lathe(gr, [(R - 0.0006, 0.019), (R + 0.0007, 0.019), (R + 0.0007, 0.049), (R - 0.0006, 0.049)], 8,
              closed=True, a0=arc_deg(90 - 12), a1=arc_deg(90 + 12))
        parts.append(gr)
        # fuse holder at the rear left: a flange and a ribbed cap
        fu = P("fuse", "knob")
        fx = -0.030
        lathe(fu, [(0.0058, 0.0), (0.0058, 0.0028), (0.0043, 0.0034), (0.0043, 0.0104), (0.0, 0.0112)], 10,
              center=(fx, math.sqrt(R * R - fx * fx) - 0.0006, 0.030), axis="y", flute=(8, 0.06, {3}))
        parts.append(fu)
    else:
        parts.append(boxp("feet", "rubber", -0.07, 0.07, -0.05, 0.05, 0.0, FOOT_H))
    return parts


def build_hinge(spec):
    """Hinge at the back: a plate on the drum following its curvature, two posts with knuckles, the
    middle knuckle on the lid plate (two screws), a pin through.
    """
    fine = spec["fine"]
    parts = []
    hy, hz, hr = 0.0985, 0.1705, 0.0042
    hg = P("hinge", "chrome")
    if fine:
        lathe(hg, [(R - 0.0008, 0.1460), (R + 0.0012, 0.1460), (R + 0.0012, 0.1572), (R - 0.0008, 0.1572)], 8,
              closed=True, a0=arc_deg(90 - 20), a1=arc_deg(90 + 20))
        for s in (-1, 1):
            g.box(hg, s * 0.0165, s * 0.0265, 0.0925, 0.0975, 0.1480, 0.1712)
            g.cyl(hg, (s * 0.0215, hy, hz), "x", hr, 0.0110, 8)
            g.cyl(hg, (s * 0.0280, hy, hz), "x", 0.0019, 0.0016, 6)           # pin ends
        g.cyl(hg, (0.0, hy, hz), "x", hr, 0.0300, 8)
        g.box(hg, -0.0125, 0.0125, 0.0690, 0.0960, 0.1758, 0.1772, r=0.0005, seg=1)   # lid plate
        g.box(hg, -0.0090, 0.0090, 0.0930, 0.0992, 0.1700, 0.1772)           # tongue to the knuckle
        for s in (-1, 1):
            screw(hg, (s * 0.0065, 0.0760, 0.1772), (0, 0, 1))
    else:
        g.box(hg, -0.030, 0.030, 0.0905, 0.0965, 0.1460, 0.1572)
        g.cyl(hg, (0.0, hy, hz), "x", hr, 0.0560, 6)
        g.box(hg, -0.0125, 0.0125, 0.0690, 0.0990, 0.1700, 0.1772)
    parts.append(hg)
    return parts


def build_latch(spec):
    """Front latch: a plate on the drum, a bracket over the lid edge, a black mushroom."""
    fine = spec["fine"]
    parts = []
    lt = P("latch", "chrome")
    ky, kz = -(R + 0.0034), 0.1530
    if fine:
        lathe(lt, [(R - 0.0008, 0.1390), (R + 0.0012, 0.1390), (R + 0.0012, 0.1545), (R - 0.0008, 0.1545)], 4,
              closed=True, a0=arc_deg(-90 - 9), a1=arc_deg(-90 + 9))
        g.box(lt, -0.0060, 0.0060, ky, -(R + 0.0010), 0.1440, 0.1778, r=0.0006, seg=1)
        g.box(lt, -0.0060, 0.0060, ky, -(LID_R - 0.0040), 0.1758, 0.1778, r=0.0006, seg=1)
    else:
        g.box(lt, -0.0060, 0.0060, ky, -(R - 0.001), 0.1400, 0.1778)
        g.box(lt, -0.0060, 0.0060, ky, -(LID_R - 0.0040), 0.1758, 0.1778)
    parts.append(lt)
    kn = P("latch_knob", "knob")
    if fine:
        lathe(kn, [(0.0040, -0.0002), (0.0062, 0.0018), (0.0065, 0.0058), (0.0054, 0.0086), (0.0, 0.0098)], 10,
              center=(0.0, ky, kz), axis="-y")
    else:
        g.cyl(kn, (0.0, ky - 0.005, kz), "y", 0.0064, 0.010, 8)
    parts.append(kn)
    return parts


# =============================================================================
# Rotor (bone ozl_work)
# =============================================================================
def build_rotor(spec):
    """Hub with a nut and a red mark, a spider, four cups with blue test tube caps. The mark breaks
    the symmetry - the rotation is visible even on rare frames.
    """
    fine = spec["fine"]
    z = ROTOR_TOP                       # top of the hub: ~2 cm under the window glass
    rt = P("rotor", "rotor", group=SEL_ROTOR)
    if fine:
        lathe(rt, [(0.016, z - 0.027), (0.016, z - 0.0024), (0.0150, z - 0.0006), (0.0128, z), (0.0, z)], 12)
        g.cyl(rt, (0, 0, z + 0.0029), "z", 0.0080, 0.0058, 6)                # nut
        g.cyl(rt, (0, 0, z + 0.0070), "z", 0.0034, 0.0026, 8)                # shaft end
        for k in range(4):
            a = math.radians(45 + 90 * k)
            fr = g.Frame((0, 0, 0), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))
            g.prism(rt, [(0.012, -0.008), (0.050, -0.0055), (0.050, 0.0055), (0.012, 0.008)], (0, 1), z - 0.0102,
                    z - 0.0030, frame=fr)
            c = (0.056 * math.cos(a), 0.056 * math.sin(a), 0.0)
            lathe(rt, [(0.0085, z - 0.031), (0.0085, z - 0.0027), (0.0060, z - 0.0027), (0.0, z - 0.0020)], 6,
                  center=c, regions=["rotor", "rotor", "tube_cap"])
    else:
        g.cyl(rt, (0, 0, z - 0.0136), "z", 0.016, 0.0272, 8)
        for a in (45, 135):
            fr = frame_z(a)
            g.box(rt, -0.050, 0.050, -0.0060, 0.0060, z - 0.0102, z - 0.0030, frame=fr)
    # red stripe on one blade and on the hub - the rotation mark
    use(rt, "rotor_mark")
    g.box(rt, 0.0088, 0.0150, -0.0018, 0.0018, z - 0.0003, z + 0.0006, frame=frame_z(135))
    g.box(rt, 0.0150, 0.0460, -0.0018, 0.0018, z - 0.0034, z - 0.0024, frame=frame_z(135))
    return [rt]


def frame_z(deg):
    """Rotation about the vertical by deg (a frame for g.box / g.prism)."""
    a = math.radians(deg)
    return g.Frame((0, 0, 0), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))


# =============================================================================
# Panel
# =============================================================================
def build_panel(spec):
    fine = spec["fine"]
    parts = []
    pn = P("panel", "panel")
    g.box(pn, -PANEL_W / 2, PANEL_W / 2, PY, -FY + 0.001, PANEL_ZC - PANEL_H / 2, PANEL_ZC + PANEL_H / 2,
          **({"r": 0.0009, "seg": 1} if fine else {}))
    parts.append(pn)
    if fine:
        sc = P("panel_screws", "chrome")
        for sx in (-1, 1):
            for sz in (-1, 1):
                screw(sc, (sx * 0.0525, PY, PANEL_ZC + sz * 0.0195), (0, -1, 0), r=0.0019, sides=6)
        parts.append(sc)
    # timer knob: a skirt, a ribbed cap with a pointer, a white mark on the skirt (set to 15 min)
    tx, tz = TIMER
    kn = P("timer_knob", "knob")
    if fine:
        # the skirt goes under the cap as a ring: the cap fluting leaves no gaps
        lathe(kn, [(0.0125, 0.0), (0.0125, 0.0025), (0.0112, 0.0039), (0.0094, 0.0042), (0.0080, 0.0042)], 16,
              center=(tx, PY, tz), axis="-y")
        lathe(kn, [(0.0094, 0.0040), (0.0089, 0.0150), (0.0081, 0.0162), (0.0, 0.0168)], 20,
              center=(tx, PY, tz), axis="-y", flute=(10, 0.05, {0, 1}))
        g.box(kn, tx - 0.0015, tx + 0.0015, PY - 0.0190, PY - 0.0150, tz - 0.0080, tz + 0.0080, r=0.0006, seg=1)
        use(kn, "pointer")
        g.box(kn, tx - 0.0006, tx + 0.0006, PY - 0.0041, PY - 0.0026, tz + 0.0097, tz + 0.0124)
    else:
        g.cyl(kn, (tx, PY - 0.002, tz), "y", 0.0125, 0.004, 10)
        g.cyl(kn, (tx, PY - 0.010, tz), "y", 0.0092, 0.013, 10, r2=0.0085)
    parts.append(kn)
    # tachometer: a black frame with rounded corners, the face (lit by the "working" lamp), glass,
    # the needle on its own bone
    mx, mz = METER
    bz = P("meter_bezel", "bezel")
    if fine:
        rings = [rrect(mx, mz, METER_W, METER_H, 0.0030, PY + 0.0004), rrect(mx, mz, METER_W, METER_H, 0.0030, MFD + 0.0009),
                 rrect(mx, mz, METER_W - 0.0016, METER_H - 0.0016, 0.0022, MFD),
                 rrect(mx, mz, 0.0290, 0.0230, 0.0008, MFD), rrect(mx, mz, 0.0290, 0.0230, 0.0008, MFD + 0.0036)]
    else:
        rings = [rrect(mx, mz, METER_W, METER_H, 0.0, PY + 0.0004, 0), rrect(mx, mz, METER_W, METER_H, 0.0, MFD, 0),
                 rrect(mx, mz, 0.0290, 0.0230, 0.0, MFD, 0), rrect(mx, mz, 0.0290, 0.0230, 0.0, MFD + 0.0036, 0)]
    loft(bz, rings, closed=True, recalc=True)
    parts.append(bz)
    face = P("meter_face", "meter", group=SEL_LAMP)
    g.quad(face, [(mx - 0.0145, MFACE, mz - 0.0115), (mx + 0.0145, MFACE, mz - 0.0115),
                  (mx + 0.0145, MFACE, mz + 0.0115), (mx - 0.0145, MFACE, mz + 0.0115)])
    parts.append(face)
    mg = P("meter_glass", "black", section="glass")
    gy = MFD + 0.0010
    g.quad(mg, [(mx - 0.0145, gy, mz - 0.0115), (mx + 0.0145, gy, mz - 0.0115),
                (mx + 0.0145, gy, mz + 0.0115), (mx - 0.0145, gy, mz + 0.0115)])
    mg.glass_frame = (g.Frame((mx, gy, mz), (1, 0, 0), (0, 0, 1), (0, -1, 0)), -0.0145, 0.0145, -0.0115, 0.0115)
    parts.append(mg)
    # needle at rest - at the scale zero (135 degrees in the x-z plane), the axis is NEEDLE_PIVOT;
    # it is in the middle LOD too, so the sway is visible from afar
    nd = P("needle", "needle", group=SEL_NEEDLE)
    px, pz = NEEDLE_PIVOT
    u = (math.cos(math.radians(135)), math.sin(math.radians(135)))
    w = (-u[1], u[0])
    poly = [(px + a * u[0] + b * w[0], pz + a * u[1] + b * w[1])
            for a, b in ((-0.0022, -0.0005), (NEEDLE_L, -0.00012), (NEEDLE_L, 0.00012), (-0.0022, 0.0005))]
    g.prism(nd, poly, (0, 2), MFD + 0.0022, MFD + 0.0027)
    g.cyl(nd, (px, MFD + 0.0021, pz), "y", 0.0011, 0.0010, 10 if fine else 6)
    parts.append(nd)
    # "mains" lamp: a chrome ring and a red dome lens
    lx, lz = LAMP
    ring = P("lamp_ring", "chrome")
    lp = P("lamp", "lamp", group=SEL_LAMP)
    if fine:
        lathe(ring, [(0.0068, 0.0), (0.0068, 0.0016), (0.0060, 0.0029), (0.0049, 0.0031)], 12, center=(lx, PY, lz),
              axis="-y")
        lathe(lp, [(0.0050, 0.0022), (0.0049, 0.0046), (0.0039, 0.0064), (0.0, 0.0072)], 12, center=(lx, PY, lz),
              axis="-y")
    else:
        g.cyl(ring, (lx, PY - 0.0015, lz), "y", 0.0068, 0.003, 8)
        g.cyl(lp, (lx, PY - 0.0050, lz), "y", 0.0048, 0.004, 8, r2=0.0040)
    parts += [ring, lp]
    if fine:
        # toggle: a hex nut, a bushing, a lever pointing down
        tg = P("toggle", "chrome")
        ox, oz = TOGGLE
        g.cyl(tg, (ox, PY - 0.0013, oz), "y", 0.0056, 0.0026, 6)
        g.cyl(tg, (ox, PY - 0.0045, oz), "y", 0.0030, 0.0040, 10)
        g.tube_var(tg, [(ox, PY - 0.0060, oz), (ox, PY - 0.0095, oz - 0.0030), (ox, PY - 0.0125, oz - 0.0058)],
                   [(0.0016, 0.0016), (0.0013, 0.0013), (0.0011, 0.0011)], 6)
        parts.append(tg)
    return parts


# =============================================================================
# Cord
# =============================================================================
CABLE_PTS = [(0.030, CY + 0.0130, CABLE_Z), (0.030, CY + 0.0175, 0.0285), (0.033, CY + 0.0290, 0.0105),
             (0.034, CY + 0.0317, 0.0042), (0.029, 0.1262, 0.0033), (0.016, 0.1290, 0.0033),
             (-0.002, 0.1274, 0.0033), (-0.017, 0.1212, 0.0033), (-0.027, 0.1168, 0.0042),
             (-0.032, 0.1155, 0.0068), (-0.0375, 0.1152, 0.0085)]


def build_cable(spec):
    """Ribbed cord inlet at the back bottom right, the cord goes down to the floor and lies in an
    arc behind the body, a round plug with two pins lies on its side at the rear left.
    """
    fine = spec["fine"]
    parts = []
    rb = P("cable_boot", "rubber")
    if fine:
        lathe(rb, [(0.0062, 0.0), (0.0062, 0.0028), (0.0048, 0.0034), (0.0046, 0.0068), (0.0040, 0.0080),
                   (0.0040, 0.0118), (0.0035, 0.0150)], 8, center=(0.030, CY - 0.0006, CABLE_Z), axis="y")
    else:
        g.cyl(rb, (0.030, CY + 0.007, CABLE_Z), "y", 0.0060, 0.015, 6, r2=0.0036)
    parts.append(rb)
    cb = P("cable", "cable")
    if fine:
        g.pipe(cb, spline(CABLE_PTS, 2), 0.0032, 6)
    else:
        pts = CABLE_PTS[::2] if len(CABLE_PTS) % 2 else CABLE_PTS[::2] + CABLE_PTS[-1:]
        g.pipe(cb, pts, 0.0032, 4)
    parts.append(cb)
    pl = P("plug", "plug")
    if fine:
        lathe(pl, [(0.0034, -0.0030), (0.0046, 0.0030), (0.0075, 0.0100), (0.0085, 0.0140), (0.0085, 0.0250),
                   (0.0075, 0.0290), (0.0, 0.0296)], 8, center=PLUG, axis="-x")
        use(pl, "chrome")
        x0 = PLUG[0] - 0.0296
        for s in (-1, 1):
            g.cyl(pl, (x0 - 0.0075, PLUG[1] + s * 0.00705, PLUG[2] + s * 0.00257), "x", 0.0019, 0.0160, 6)
    else:
        g.cyl(pl, (PLUG[0] - 0.0145, PLUG[1], PLUG[2]), "x", 0.0085, 0.029, 6)
    parts.append(pl)
    return parts


def build_lod(spec):
    parts = build_body(spec) + build_rotor(spec) + build_panel(spec) + build_cable(spec)
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """One convex hull of the body (an octagonal prism up to the top of the dome); the cord has no
    collision. The mass is the item's weight in the mod, 0.8 kg.
    """
    ring = [(R * math.cos(2 * math.pi * k / 8), R * math.sin(2 * math.pi * k / 8)) for k in range(8)]
    pts = [(x, y, z) for x, y in ring for z in (0.0, 0.160)]
    pts += [(0.088 * math.cos(2 * math.pi * k / 8), 0.088 * math.sin(2 * math.pi * k / 8), DOME_Z1)
            for k in range(8)]
    comps = [(pts, kx.PEN + r"\metalplate.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    memory = {
        # inventory preview camera: front left and above (invView = where the camera is)
        "invView": [(-0.30, -0.46, 0.36)],
        "ce_center": [(0.0, 0.0, 0.09)],
        "ce_radius": [(0.12, 0.0, 0.09)],
        # bone axes: the rotor - bottom to top through the center, the needle - from the face to the
        # viewer through its axis (see ROTOR_AXIS, NEEDLE_AXIS - the turn direction in the game)
        "ozl_work_axis": ROTOR_AXIS,
        "ozl_needle_axis": NEEDLE_AXIS,
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


SHOTS = [
    ("front", (-0.22, -0.52, 0.30), (0.0, 0.0, 0.09), 40),
    ("panel", (-0.06, -0.30, 0.10), (0.005, -0.07, 0.035), 45),
    ("window", (0.10, -0.20, 0.40), (0.0, -0.005, 0.15), 50),
    ("back", (0.30, 0.46, 0.26), (0.0, 0.02, 0.07), 40),
]
M.look_shots = (4, 2)


def _posed(place):
    """Preview of the working look: the tachometer needle at the middle of its sway - by the engine
    turn (engine_turn: the preview shows what will be in the game). kmodel only knows a shift
    (move), so the turn is here, a wrapper over krender (as in M10); it does not go into the p3d
    - there model.cfg animates.
    """
    def wrapped(parts, *a, **kw):
        obs = place(parts, *a, **kw)
        if kw.get("move") is ON_MOVE:
            o, ax, ang = engine_turn(NEEDLE_AXIS, NEEDLE_MID * math.pi / 2)
            for p, ob in zip(parts, obs):
                if p.group == SEL_NEEDLE:
                    loc = Vector(ob.location)
                    cc = o + loc
                    ob.matrix_world = (Matrix.Translation(cc) @ Matrix.Rotation(ang, 4, ax) @ Matrix.Translation(-cc) @
                                       Matrix.Translation(loc))
        return obs
    return wrapped


krender.place_look = _posed(krender.place_look)
krender.place = _posed(krender.place)

M.run(build_lod, collision, SHOTS, row_step=0.32, row_shot=((0.16, -1.1, 0.35), (0.16, 0, 0.09)))
