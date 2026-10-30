"""M44 - a binocular magnifier on a column: the Optical module (OZL_Tool_Optics), a module of
the "Bio" line. A portable 2x2 item that stands in the OZL_Tool1 slot of the machine (the
proxy sits where module_1 is): the origin is at the center of the bottom, the bottom is
flat, the front (eyepieces) faces -Y, as on the machine.

    blender --background --python build_m44.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

The instrument follows the tripod binocular magnifiers of the 1960-80s: a Carl Zeiss Jena on
a column with a side bracket (a round cast-iron base with a stage ring, a chrome column with
a sleeve at the bottom, a clamp bracket with a knurled thumbscrew, a knurled focus
handwheel, two prism housings in black leatherette, conical objectives pointing down,
eyecups with a "wing"); the eyepieces are tilted toward the observer, as on the LOMO MBS-10
(which also has the stage clips and the light from below).

Dimensions:
- binocular body - after the Zeiss 6x15 (case 20.5 x 12 x 7 cm): two prism housings
  ~4.2 x 4.4 x 6 cm, interpupillary distance 64 mm;
- eyepiece - a 23.2 mm fit (the standard eyepiece tube), outside ~dia 24-30 mm with the
  eyecup;
- base: in the reference photo the base diameter is ~2.7 widths of a prism housing and the
  instrument height ~6 widths (~32 cm). For the module (a 0.2 x 0.2 pad with 0.25 m free
  above it) the column is shortened: base dia 0.17, total height 0.245 m; the magnifier is
  shorter than a real one, this is the module's tolerance;
- slide - the standard 76 x 26 x 1 mm (GOST 9284), the stage clips as on the MBS-10;
- the table clamp is replaced by a heavy base: the module stands on a shelf without an
  edge, so it needs a flat bottom.

Look: no angular parts - the base, sleeve, column, objectives and eyepieces are solids of
revolution with chamfers and roundings, the prism housings are a rounded section with
leather between enamel caps, the head bridge is an oval with rounded edges; the focus
handwheels and thumbscrews are knurled (the fluting is geometry). Small details of the
real instrument: nameplate rivets, accessory holes, a hinge with lugs between the housings,
stage clips with the slide and a smear, a toggle switch and a pilot lamp of the light, a tag
on twine (a smooth curve). There are no vanilla items on the module: it is carried in the
hands and put into a slot, the DayZ small items belong on the machines.

State - shared instruments and modules: `used but intact, worn paint on the edges` - the
enamel is worn on the edges of the base, clamp and bridge, the anodizing of the eyepieces
down to silver on the ribs, the leather scuffed at the corners, the chrome intact.

"Working" look: ozl_lamp - the stage glass, the slide and the pilot lamp (the _on atlas:
the light from below is on, the smear shows through, the lamp is red); the head moves on
focusing (the bone ozl_focus - bridge, objectives, housings, eyepieces, hinge - down by
FOCUS_TRAVEL along the axis ozl_focus_axis) and the handwheels turn (the bone ozl_knob,
the axis ozl_knob_axis), both on the source ozl_focus: OZL_WorkFx wobble - the focus
"wanders" around the middle of the travel.

Blender axes: X - width, Y - depth (front at -Y), Z - up.
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

# =============================================================================
# Dimensions, m
# =============================================================================
R_BASE, Z_BASE = 0.085, 0.019            # base
STAGE_Y = -0.024                         # stage center (under the objectives)
Z_SLIDE = Z_BASE + 0.0022                # bottom of the slide (top of the stage ring)
POST_Y = 0.052                           # column
Z_POST = 0.196
ARM_Z0, ARM_Z1 = 0.150, 0.168            # bracket
HEAD_Y = -0.022                          # objective axis
CAR_Y, CAR_R = -0.024, 0.021             # head bridge: an oval around the objective axes
BR_Z0, BR_Z1 = 0.132, 0.152              # head bridge
OBJ_Z = 0.095                            # bottom of the objectives
EYE_X = 0.032                            # half the interpupillary distance
TILT = math.radians(34)                  # eyepiece tilt from vertical toward the observer
DIR = (0.0, -math.sin(TILT), math.cos(TILT))
NRM = (0.0, -math.cos(TILT), -math.sin(TILT))
PR_Y, PR_Z = -0.028, 0.150               # start of the prism housings
FH = (-0.012, 0.012, -0.003, 0.018, 0.134, 0.174)   # focus box at the end of the arm
KNOB_Y, KNOB_Z = 0.0105, 0.158           # focus handwheel axis (along X)
WING = 0.009                             # eyecup "wing" - higher on the outer side
FOCUS_TRAVEL = 0.006                     # focus travel while working, m
KNOB_TURN = 1.2                          # handwheel turn over the whole travel (gear ~dia 10), rad
CTRL = (0.060, -0.021)                   # toggle and lamp pad on the base, right

LOD_SPECS = [
    dict(lod=0, bev=1, sides=16),
    dict(lod=1, bev=0, sides=10),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "enamel": ("enamel", 1.0), "anod": ("anod", 1.4), "chrome": ("chrome", 1.4), "leather": ("leather", 1.6),
    "rubber": ("rubber", 1.2), "rubber_in": ("rubber", 0.6), "lens": ("lens", 1.4), "stage": ("stage", 1.2),
    "scale": ("scale", 2.4), "scale_in": ("scale", 0.6), "plate": ("plate", 1.6), "tag": ("tag", 1.4), "string": ("string", 0.6),
    "slide": ("slide", 1.2), "label": ("label", 1.2), "smear": ("smear", 2.0), "pilot": ("pilot", 2.0),
    "steel_dark": ("steel_dark", 1.4), "dark": ("dark", 0.5),
}


# =============================================================================
# Materials
# =============================================================================
def mat_scale(mat, origin):
    """Stage ring: black enamel with white graduations around the circumference (every fifth is
    longer).
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 6.0)
    dx = t.math("SUBTRACT", sep.outputs["X"], 0.0)
    dy = t.math("SUBTRACT", sep.outputs["Y"], STAGE_Y)
    ang = t.math("DIVIDE", t.math("ARCTAN2", dy, dx), 2 * math.pi)
    rad = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", dx, dx), t.math("MULTIPLY", dy, dy)))
    tick = t.math("LESS_THAN", t.math("FRACT", t.math("MULTIPLY", ang, 60.0)), 0.18)
    major = t.math("LESS_THAN", t.math("FRACT", t.math("MULTIPLY", ang, 12.0)), 0.04)
    outer = t.math("GREATER_THAN", rad, 0.0372)
    long_ = t.math("GREATER_THAN", rad, 0.0354)
    ink = t.math("MAXIMUM", t.math("MULTIPLY", tick, outer), t.math("MULTIPLY", major, long_))
    # the graduation paint is worn in places
    ink = t.math("MULTIPLY", ink, t.maprange(t.noise(vec, 60.0, 4.0, 0.6), 0.30, 0.42, 0.0, 1.0))
    col = t.mixc(ink, kmats.lin((22, 22, 23)), kmats.lin((206, 204, 192)))
    col, dirt = kmats.weather(t, col, vec, sep, t.normal(), 0.0, 0.25, 0.3, 0.4)
    return kmats.out(t, col, 0.40, 0.30, 0.0)


def build_leather(mat, origin, color, seed=6.6, gloss=0.30, spec=0.16, dust=0.2, grime=0.35):
    """Leather of the prism housings (as on the Zeiss): fine grain - Voronoi cell bumps of ~1.3
    mm, darker pores, leather rubbed to grey-brown on the edges and in patches, dust in the
    pores.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    vor = t.node("ShaderNodeTexVoronoi", Scale=780.0)
    t.link(vec, vor.inputs["Vector"])
    cell = t.maprange(vor.outputs["Distance"], 0.05, 0.55, 1.0, 0.0)
    col = t.mixc(t.maprange(t.noise(vec, 5.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                 tuple(c * 0.85 for c in color[:3]) + (1,), tuple(min(1.0, c * 1.25) for c in color[:3]) + (1,))
    col = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", 1.0, cell), 0.55), col, tuple(c * 0.5 for c in color[:3]) + (1,))
    edge = t.maprange(t.edge_wear(0.003), 0.05, 0.22, 0.0, 1.0)
    wear = t.step(t.math("ADD", t.math("MULTIPLY", t.noise(vec, 22.0, 6.0, 0.6), 0.6), t.math("MULTIPLY", edge, 0.7)),
                  0.60, 0.74)
    col = t.mixc(t.math("MULTIPLY", wear, 0.55), col, kmats.lin((72, 64, 56)))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, 0.0, dust, grime, 0.4)
    g_ = t.math("SUBTRACT", t.math("ADD", gloss * 0.6, t.math("MULTIPLY", cell, gloss * 0.4)),
                t.math("MULTIPLY", t.math("ADD", dirt, wear), gloss * 0.5))
    s = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.5))
    h = t.math("ADD", t.math("MULTIPLY", cell, 0.35), t.math("MULTIPLY", wear, -0.15))
    return kmats.out(t, col, g_, s, h)


KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    # black enamel of the base, clamp and bridge: worn to grey cast iron on the edges, almost no
    # rust
    "enamel": ("paint", dict(color=kmats.lin((24, 24, 25)), under=kmats.lin((88, 88, 90)), seed=4.4, gloss=0.50,
                             spec=0.40, chip=(0.74, 0.80), rust=(0.90, 0.95), rust_low=0.08, dust=0.16, grime=0.35)),
    # black anodizing of the optics (housing caps, objectives, eyepieces): to silver on the ribs
    "anod": ("paint", dict(color=kmats.lin((18, 18, 19)), under=kmats.lin((150, 150, 152)), seed=5.3, gloss=0.40,
                           spec=0.32, chip=(0.80, 0.86), rust=(0.99, 1.0), rust_low=0.0, dust=0.12, grime=0.3)),
    "chrome": ("steel", dict(seed=7.1, tone=0.38, along="z", gloss=0.80, spec=0.85, dust=0.15, grime=0.25)),
    "leather": (build_leather, dict(color=kmats.lin((24, 23, 22)), seed=6.6)),
    "rubber": ("plastic", dict(color=kmats.lin((22, 22, 22)), gloss=0.12, spec=0.06, dust=0.22, grime=0.4,
                               scuff=(0.86, 0.94))),
    # coated glass: dark with a blue-violet tint
    "lens": ("flat", dict(color=kmats.lin((30, 36, 58)), gloss=0.95, spec=0.95)),
    # milky stage glass; working - lit from below
    "stage": ("flat", dict(color=kmats.lin((168, 170, 166)), gloss=0.55, spec=0.45)),
    "stage_on": ("flat", dict(color=kmats.lin((255, 240, 210)), gloss=0.55, spec=0.45)),
    "scale": (mat_scale, {}),
    "plate": ("steel", dict(seed=8.3, tone=0.50, along="x", gloss=0.6, spec=0.6, dust=0.15, grime=0.2)),
    "tag": ("plastic", dict(color=kmats.lin((214, 200, 160)), gloss=0.1, spec=0.05, mottle=0.12, dust=0.15,
                            grime=0.4, scuff=(0.8, 0.9))),
    "string": ("plastic", dict(color=kmats.lin((150, 138, 112)), gloss=0.1, spec=0.05, dust=0.1, scuff=(0.9, 1.0))),
    # slide with a stained smear (hematoxylin-eosin): shows through while working
    "slide": ("flat", dict(color=kmats.lin((176, 190, 184)), gloss=0.85, spec=0.7)),
    "slide_on": ("flat", dict(color=kmats.lin((236, 244, 236)), gloss=0.85, spec=0.7)),
    "smear": ("flat", dict(color=kmats.lin((150, 74, 120)), gloss=0.5, spec=0.3)),
    "smear_on": ("flat", dict(color=kmats.lin((232, 120, 190)), gloss=0.5, spec=0.3)),
    "label": ("plastic", dict(color=kmats.lin((222, 220, 210)), gloss=0.08, spec=0.05, mottle=0.08, dust=0.1,
                              scuff=(0.9, 1.0))),
    # light pilot lamp: dark red glass, lit while working
    "pilot": ("flat", dict(color=kmats.lin((86, 18, 14)), gloss=0.85, spec=0.8)),
    "pilot_on": ("flat", dict(color=kmats.lin((255, 70, 36)), gloss=0.85, spec=0.8)),
    "steel_dark": ("steel", dict(seed=9.1, tone=0.20, along="z", gloss=0.6, spec=0.6, dust=0.15, grime=0.4)),
    "dark": ("flat", dict(color=kmats.lin((10, 10, 10)), gloss=0.2, spec=0.1)),
})

OBJ, NAME = "m44_tool_optics", "ozr_tool_optics"
SEL_LAMP, SEL_FOCUS, SEL_KNOB = "ozl_lamp", "ozl_focus", "ozl_knob"
# Preview of the working look: the light is on, the head is at the middle of the focus
# travel (does not go into the p3d - model.cfg does that)
ON = dict(remap={"stage": "stage_on", "slide": "slide_on", "smear": "smear_on", "pilot": "pilot_on"},
          emissive=(1.0, 1.0, 1.0, 1.0), move={SEL_FOCUS: (0.0, 0.0, -FOCUS_TRAVEL * 0.5)})
# focus axis - one meter down from the top of the bridge: offset in meters
FOCUS_ANIM = ("ozl_focus_move", dict(type="translation", source="ozl_focus", selection=SEL_FOCUS,
                                     axis="ozl_focus_axis", memory=1, minValue=0.0, maxValue=1.0, offset0=0.0,
                                     offset1=FOCUS_TRAVEL))
KNOB_ANIM = ("ozl_focus_knob", dict(type="rotation", source="ozl_focus", selection=SEL_KNOB, axis="ozl_knob_axis",
                                    memory=1, minValue=0.0, maxValue=1.0, angle0=0.0, angle1=KNOB_TURN))
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL_LAMP, SEL_FOCUS, SEL_KNOB), hidden=(SEL_LAMP,), states={"on": ON},
                 bones=((SEL_FOCUS, ""), (SEL_KNOB, "")), animations=(FOCUS_ANIM, KNOB_ANIM),
                 sources={"ozl_focus": dict(animPeriod=0.2)})
P = M.part
EYE = [g.Frame((s * EYE_X, PR_Y, PR_Z), (1, 0, 0), DIR, NRM) for s in (-1, 1)]


# =============================================================================
# Primitives that kgeo lacks
# =============================================================================
def reg(part, rname):
    return part.region_index(rname, *REGIONS[rname])


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, from M16)."""
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


def zframe(c):
    """Frame of a solid of revolution around world Z through c: v is the axis, u and n are radii."""
    return g.Frame(c, (1, 0, 0), (0, 0, 1), (0, -1, 0))


def xframe(c, s):
    return g.Frame(c, (0, 1, 0), (s, 0, 0), (0, 0, 1))


def yframe(c, s):
    return g.Frame(c, (1, 0, 0), (0, s, 0), (0, 0, 1))


def _oriented(part, verts, fr, n2):
    """Face from vertices, turned outward: n2 is the profile normal (radius, axis)."""
    f = part.bm.faces.new(verts)
    c = sum((v.co for v in verts), Vector()) / len(verts)
    d = c - fr.o
    rd = d - fr.v * d.dot(fr.v)
    rd = rd.normalized() if rd.length > 1e-9 else Vector((0.0, 0.0, 0.0))
    want = rd * n2.x + fr.v * n2.y
    f.normal_update()
    if f.normal.dot(want) < 0:
        f.normal_flip()
    f[part.reg] = part.cur
    return f


def lathe(part, fr, prof, sides, regs=None, phase=0.0, hfun=None):
    """Solid of revolution around the v axis of frame fr: prof [(r, h[, knurl[, wing]])] - from the
    bottom along the outer side to the top (r = 0 - a point on the axis, a fan). Knurl - a
    depth: every other ring vertex is sunk (fluting as geometry, the edge count is sides/2).
    Wing - a fraction of hfun(angle), an addition to h (the eyecup). regs - a region per strip
    (len(prof) - 1) or None.
    """
    bm = part.bm
    rings = []
    for q in prof:
        r, h = q[0], q[1]
        kn = q[2] if len(q) > 2 else 0.0
        w = q[3] if len(q) > 3 else 0.0
        if r < 1e-7:
            rings.append([bm.verts.new(fr.p(0.0, h, 0.0))])
            continue
        ring = []
        for k in range(sides):
            a = phase + 2 * math.pi * k / sides
            rr = r - (kn if k % 2 else 0.0)
            hh = h + (w * hfun(a) if (hfun and w) else 0.0)
            ring.append(bm.verts.new(fr.p(rr * math.cos(a), hh, rr * math.sin(a))))
        rings.append(ring)
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i][:2], prof[i + 1][:2]
        n2 = Vector((h1 - h0, -(r1 - r0)))
        if n2.length < 1e-12:
            continue
        n2.normalize()
        if regs:
            part.cur = reg(part, regs[i])
        A, B = rings[i], rings[i + 1]
        if len(A) == 1 and len(B) == 1:
            continue
        for k in range(sides):
            j = (k + 1) % sides
            if len(A) == 1:
                _oriented(part, [A[0], B[k], B[j]], fr, n2)
            elif len(B) == 1:
                _oriented(part, [A[k], A[j], B[0]], fr, n2)
            else:
                _oriented(part, [A[k], A[j], B[j], B[k]], fr, n2)
    bm.normal_update()


def loft(part, fr, poly, prof, regs=None, cap0=None, cap1=None):
    """Bar of variable section along the v axis of frame fr: poly(inset) -> [(a, c)] (in the u, n
    axes), prof [(inset, b)] - from the bottom to the top; cap0 / cap1 - the end region (None -
    open).
    """
    bm = part.bm
    rings = [[bm.verts.new(fr.p(a, b, c)) for a, c in poly(ins)] for ins, b in prof]
    n = len(rings[0])
    for i in range(len(prof) - 1):
        (i0, b0), (i1, b1) = prof[i], prof[i + 1]
        n2 = Vector((b1 - b0, i1 - i0))
        if n2.length < 1e-12:
            continue
        n2.normalize()
        if regs:
            part.cur = reg(part, regs[i])
        A, B = rings[i], rings[i + 1]
        for k in range(n):
            j = (k + 1) % n
            _oriented(part, [A[k], A[j], B[j], B[k]], fr, n2)
    for ring, rname, sgn in ((rings[0], cap0, -1.0), (rings[-1], cap1, 1.0)):
        if rname:
            part.cur = reg(part, rname)
            f = bm.faces.new(ring)
            f.normal_update()
            if f.normal.dot(fr.v * sgn) < 0:
                f.normal_flip()
            f[part.reg] = part.cur
    bm.normal_update()


def rrect(hx, hy, r, n):
    """Rounded rectangle 2hx x 2hy: n segments per corner (0 - sharp corners, 1 - a chamfer)."""
    if n == 0:
        return [(hx, hy), (-hx, hy), (-hx, -hy), (hx, -hy)]
    r = min(r, hx, hy)
    pts = []
    for cx, cy, a0 in ((hx - r, hy - r, 0.0), (-(hx - r), hy - r, 90.0), (-(hx - r), -(hy - r), 180.0),
                       (hx - r, -(hy - r), 270.0)):
        for s in range(n + 1):
            a = math.radians(a0 + 90.0 * s / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def stadium(xc, r, n):
    """Bridge oval: semicircles of radius r around (+-xc, 0), n segments per semicircle."""
    pts = [(xc + r * math.cos(math.radians(-90 + 180.0 * s / n)), r * math.sin(math.radians(-90 + 180.0 * s / n)))
           for s in range(n + 1)]
    pts += [(-xc + r * math.cos(math.radians(90 + 180.0 * s / n)), r * math.sin(math.radians(90 + 180.0 * s / n)))
            for s in range(n + 1)]
    return pts


# =============================================================================
# Base, stage, column
# =============================================================================
def build_stand(spec):
    lod = spec["lod"]
    parts = []
    R = R_BASE
    base = P("base", "enamel")
    if lod == 0:
        # cast disc: a chamfer at the bottom, rounding at the top in two steps
        lathe(base, zframe((0, 0, 0)), [(0, 0), (R - 0.002, 0), (R, 0.002), (R, 0.0128), (R - 0.0022, 0.0177),
                                        (R - 0.0068, Z_BASE), (0, Z_BASE)], 40)
    else:
        lathe(base, zframe((0, 0, 0)), [(0, 0), (R, 0), (R, 0.0140), (R - 0.0050, Z_BASE), (0, Z_BASE)],
              20 if lod == 1 else 10)
    parts.append(base)
    if lod == 0:
        # accessory holes (along the base edge)
        hl = P("base_holes", "dark")
        for x, y in ((-0.026, POST_Y + 0.006), (0.026, POST_Y + 0.006), (-0.062, -0.028)):
            lathe(hl, zframe((x, y, 0)), [(0.0016, Z_BASE + 0.0003), (0, Z_BASE + 0.0003)], 8)
        parts.append(hl)
    # stage: graduation ring, milky glass (the light from below is ozl_lamp)
    sf = zframe((0, STAGE_Y, 0))
    if lod < 2:
        ring = P("stage_ring", "scale")
        # inner wall is its own region: it faces the axis and in the atlas would overlap the
        # opposite outer wall
        if lod == 0:
            lathe(ring, sf, [(0.0410, Z_BASE - 0.0003), (0.0400, Z_SLIDE), (0.0338, Z_SLIDE), (0.0328, Z_BASE + 0.0010)],
                  32, regs=["scale", "scale", "scale_in"])
        else:
            lathe(ring, sf, [(0.0410, Z_BASE - 0.0003), (0.0400, Z_SLIDE), (0.0335, Z_SLIDE), (0.0330, Z_BASE + 0.0010)],
                  16, regs=["scale", "scale", "scale_in"])
        parts.append(ring)
    st = P("stage", "stage", group=SEL_LAMP)
    zg = Z_BASE + (0.0010 if lod < 2 else 0.0006)
    lathe(st, sf, [(0.0330, zg), (0, zg)], (32, 16, 8)[lod])
    parts.append(st)
    if lod < 2:
        # 76 x 26 x 1 slide with a smear (shows through while working) and a frosted label field
        sl = P("slide", "slide", group=SEL_LAMP)
        g.box(sl, -0.038, 0.038, STAGE_Y - 0.013, STAGE_Y + 0.013, Z_SLIDE, Z_SLIDE + 0.001)
        if lod == 0:
            # smear: an uneven blot elongated along the slide
            sl.use("smear", *REGIONS["smear"])
            mf = zframe((-0.004, STAGE_Y, 0))
            zs = Z_SLIDE + 0.00105
            c0 = sl.bm.verts.new((-0.004, STAGE_Y, zs))
            rim = []
            for k in range(14):
                a = 2 * math.pi * k / 14
                r = 0.0056 * (1 + 0.16 * math.sin(3 * a + 0.7) + 0.09 * math.sin(5 * a + 2.1))
                rim.append(sl.bm.verts.new((-0.004 + 1.25 * r * math.cos(a), STAGE_Y + r * math.sin(a), zs)))
            for k in range(14):
                _oriented(sl, [c0, rim[k], rim[(k + 1) % 14]], mf, Vector((0.0, 1.0)))
            sl.use("slide")
        parts.append(sl)
    if lod == 0:
        lb = P("slide_label", "label")
        g.box(lb, 0.019, 0.0376, STAGE_Y - 0.0126, STAGE_Y + 0.0126, Z_SLIDE + 0.001, Z_SLIDE + 0.00118)
        parts.append(lb)
        # stage clips: a post with a dome and a spring finger on the slide edge
        for s in (-1, 1):
            cl = P("clip%d" % (s > 0), "steel_dark")
            px, py = s * 0.047, STAGE_Y + 0.012
            lathe(cl, zframe((px, py, 0)), [(0.0026, Z_BASE - 0.0003), (0.0026, Z_BASE + 0.0048),
                                            (0.0016, Z_BASE + 0.0060), (0, Z_BASE + 0.0063)], 8)
            cl.use("chrome", *REGIONS["chrome"])
            g.sweep(cl, [(px, py, Z_BASE + 0.0052), (s * 0.041, STAGE_Y + 0.0062, Z_BASE + 0.0049),
                         (s * 0.0345, STAGE_Y + 0.0012, Z_SLIDE + 0.0013)], (0, 0, 1), 0.0022, 0.0003)
            parts.append(cl)
    parts += build_controls(spec)
    # column: a flange on the base, a sleeve, a chrome rod with a dome
    cf = zframe((0, POST_Y, 0))
    if lod < 2:
        fl = P("flange", "enamel")
        if lod == 0:
            lathe(fl, cf, [(0.0182, Z_BASE - 0.0003), (0.0182, Z_BASE + 0.0034), (0.0166, Z_BASE + 0.0052),
                           (0.0122, Z_BASE + 0.0060)], 20)
        else:
            lathe(fl, cf, [(0.0182, Z_BASE - 0.0003), (0.0182, Z_BASE + 0.004), (0.0122, Z_BASE + 0.006)], 12)
        parts.append(fl)
    sl = P("sleeve", "chrome")
    if lod == 0:
        lathe(sl, cf, [(0.0120, Z_BASE + 0.004), (0.0120, 0.0736), (0.0109, 0.0752), (0.0080, 0.0752)], 20)
    elif lod == 1:
        lathe(sl, cf, [(0.0120, Z_BASE + 0.004), (0.0120, 0.0750), (0.0080, 0.0750)], 12)
    else:
        lathe(sl, cf, [(0.0120, Z_BASE), (0.0120, 0.0750)], 6)
    parts.append(sl)
    rod = P("rod", "chrome")
    if lod == 0:
        lathe(rod, cf, [(0.0080, 0.0745), (0.0080, Z_POST + 0.0012), (0.0069, Z_POST + 0.0034),
                        (0.0036, Z_POST + 0.0044), (0, Z_POST + 0.0046)], 16)
    elif lod == 1:
        lathe(rod, cf, [(0.0080, 0.0745), (0.0080, Z_POST + 0.002), (0.0050, Z_POST + 0.0042), (0, Z_POST + 0.0045)], 10)
    else:
        lathe(rod, cf, [(0.0080, 0.0745), (0.0080, Z_POST + 0.004), (0, Z_POST + 0.004)], 6)
    parts.append(rod)
    if lod == 0:
        # inventory tag without text on twine: a loop around the sleeve, a knot, a free end
        st = P("tag_string", "string")
        pts = [(0.0124 * math.cos(math.radians(a)), POST_Y + 0.0124 * math.sin(math.radians(a)),
                0.0625 + 0.0006 * math.sin(math.radians(a * 2)))
               for a in range(-60, 301, 60)]
        pts += [(0.0150, POST_Y - 0.0135, 0.0585), (0.0185, POST_Y - 0.0175, 0.0528), (0.0200, POST_Y - 0.0190, 0.0505)]
        g.pipe(st, spline(pts, 2), 0.0007, 4)
        parts.append(st)
        tg = P("tag", "tag")
        tf = g.Frame((0.020, POST_Y - 0.019, 0.0505), (0.70, -0.70, 0), (0.0, 0.0, -1.0), (-0.70, -0.70, 0))
        g.box(tg, -0.011, 0.011, 0.0, 0.026, -0.0004, 0.0004, frame=tf)
        parts.append(tg)
    return parts


def build_controls(spec):
    """Pad on the right of the base: the light toggle and the pilot lamp in a chrome bezel."""
    lod = spec["lod"]
    parts = []
    cx, cy = CTRL
    zp = Z_BASE + 0.0022
    pl = P("ctrl_plate", "anod")
    g.box(pl, cx - 0.0075, cx + 0.0075, cy - 0.013, cy + 0.013, Z_BASE - 0.0003, zp,
          r=0.001 if lod == 0 else 0.0, seg=1 if lod == 0 else 0)
    parts.append(pl)
    lf = zframe((cx, cy - 0.0065, 0))
    lp = P("pilot", "pilot", group=SEL_LAMP)
    if lod == 0:
        bz = P("pilot_bezel", "chrome")
        lathe(bz, lf, [(0.0046, zp - 0.0002), (0.0046, zp + 0.0012), (0.0039, zp + 0.0019), (0.0033, zp + 0.0016)], 12)
        parts.append(bz)
        lathe(lp, lf, [(0.0034, zp + 0.0014), (0.0029, zp + 0.0036), (0.0016, zp + 0.0047), (0, zp + 0.0050)], 12)
    else:
        lathe(lp, lf, [(0.0034, zp + 0.0014), (0, zp + 0.0045)], 8 if lod == 1 else 6)
    parts.append(lp)
    if lod < 2:
        tx, ty = cx, cy + 0.0065
        # nut, bushing and lever are different parts/regions: their tops face up above one another
        if lod == 0:
            tg = P("toggle", "chrome")
            hexa = [(tx + 0.0036 * math.cos(math.radians(30 + 60 * k)), ty + 0.0036 * math.sin(math.radians(30 + 60 * k)))
                    for k in range(6)]
            g.prism(tg, hexa, (0, 1), zp - 0.0002, zp + 0.0024)
            tg.use("steel_dark", *REGIONS["steel_dark"])
            lathe(tg, zframe((tx, ty, 0)), [(0.0024, zp + 0.0023), (0.0024, zp + 0.0040), (0, zp + 0.0040)], 10)
            parts.append(tg)
        lv = P("toggle_lever", "chrome")
        if lod == 0:
            g.pipe(lv, [(tx, ty, zp + 0.0035), (tx, ty + 0.0028, zp + 0.0105), (tx, ty + 0.0036, zp + 0.0125)],
                   0.0011, 6)
        else:
            g.pipe(lv, [(tx, ty, zp), (tx, ty + 0.0036, zp + 0.0120)], 0.0012, 4)
        parts.append(lv)
    return parts


# =============================================================================
# Bracket: a clamp on the column with a thumbscrew, an arm, the focus box, handwheels
# =============================================================================
def build_arm(spec):
    lod = spec["lod"]
    parts = []
    cl = P("clamp", "enamel")
    g.box(cl, -0.017, 0.017, POST_Y - 0.018, POST_Y + 0.018, ARM_Z0 - 0.008, ARM_Z1 + 0.012,
          r=(0.0035, 0.002, 0.0)[lod], seg=(2, 1, 0)[lod])
    parts.append(cl)
    # arm: cast, with a waist in the middle (goes into the clamp and the focus box)
    arm = P("arm", "enamel")
    af = g.Frame((0, POST_Y - 0.016, 0.159), (1, 0, 0), (0, -1, 0), (0, 0, 1))
    nc = (2, 1, 0)[lod]
    loft(arm, af, lambda ins: rrect(0.010 - ins, 0.008 - ins, max(0.003 - ins, 0.0004), nc),
         [(0.0, 0.0), (0.0010, 0.010), (0.0, 0.020)] if lod == 0 else [(0.0, 0.0), (0.0, 0.020)])
    parts.append(arm)
    fh = P("focus_box", "enamel")
    g.box(fh, *FH, r=(0.003, 0.0015, 0.0)[lod], seg=(2, 1, 0)[lod])
    parts.append(fh)
    # focus handwheels on one axis at the box sides: knurling, a hub with a screw (bone ozl_knob)
    for s in (-1, 1):
        fw = P("focus%d" % (s > 0), "chrome", group=SEL_KNOB)
        wf = xframe((s * FH[1], KNOB_Y, KNOB_Z), s)
        if lod == 0:
            # 20 knurl ribs; the ends are slightly dished - the ribs run out onto them, as on a real
            # handwheel
            lathe(fw, wf, [(0.0042, 0.0003), (0.0145, 0.0012, 0.0009), (0.0145, 0.0074, 0.0009), (0.0045, 0.0084),
                           (0, 0.0092)], 40)
        elif lod == 1:
            lathe(fw, wf, [(0.0042, 0.0003), (0.0145, 0.0010), (0.0145, 0.0075), (0, 0.0085)], 12)
        else:
            lathe(fw, wf, [(0.0145, 0.0003), (0.0145, 0.0075), (0, 0.0075)], 6)
        parts.append(fw)
    if lod == 2:
        return parts
    # clamp thumbscrew on the right: a knurled head
    lk = P("lock_knob", "chrome")
    kf = xframe((0.017, POST_Y, (ARM_Z0 + ARM_Z1) / 2 + 0.002), 1)
    if lod == 0:
        lathe(lk, kf, [(0.0078, -0.0003), (0.0088, 0.0012, 0.0006), (0.0088, 0.0072, 0.0006), (0.0034, 0.0089),
                       (0, 0.0095)], 32)
    else:
        lathe(lk, kf, [(0.0078, -0.0003), (0.0088, 0.0012), (0.0088, 0.0075), (0, 0.0090)], 10)
    parts.append(lk)
    # blank nameplate on the clamp face, on two rivets
    pl = P("nameplate", "plate")
    yp = POST_Y - 0.018
    g.box(pl, -0.011, 0.011, yp - 0.0009, yp + 0.0002, 0.1645, 0.1760)
    if lod == 0:
        pl.use("chrome", *REGIONS["chrome"])
        for x in (-0.0085, 0.0085):
            lathe(pl, yframe((x, yp - 0.0009, 0.1702), -1), [(0.0011, -0.0002), (0.0009, 0.0004), (0, 0.0006)], 8)
    parts.append(pl)
    return parts


# =============================================================================
# Head: bridge, objectives down, prism housings in leather, eyepieces with eyecups, hinge (bone
# ozl_focus)
# =============================================================================
def build_head(spec):
    lod = spec["lod"]
    parts = []
    br = P("bridge", "enamel", group=SEL_FOCUS)
    bf = g.Frame((0, CAR_Y, 0), (1, 0, 0), (0, 0, 1), (0, 1, 0))
    nseg = (10, 5, 2)[lod]
    if lod == 0:
        loft(br, bf, lambda ins: stadium(EYE_X, CAR_R - ins, nseg),
             [(0.0018, BR_Z0), (0.0, BR_Z0 + 0.0018), (0.0, BR_Z1 - 0.0022), (0.0022, BR_Z1)], cap0="enamel",
             cap1="enamel")
    else:
        loft(br, bf, lambda ins: stadium(EYE_X, CAR_R - ins, nseg), [(0.0, BR_Z0), (0.0, BR_Z1)], cap0="enamel",
             cap1="enamel")
    parts.append(br)
    for s in (-1, 1):
        x = s * EYE_X
        ob = P("objective%d" % (s > 0), "anod", group=SEL_FOCUS, uv_name="objective", uv_origin=(x, HEAD_Y, 0))
        of = zframe((x, HEAD_Y, 0))
        if lod == 0:
            # the lens is recessed (concave), the cell has a chamfer, a cone, a ring at the bridge
            lathe(ob, of, [(0, OBJ_Z + 0.0011), (0.0080, OBJ_Z + 0.0005), (0.0098, OBJ_Z), (0.0112, OBJ_Z + 0.0010),
                           (0.0150, BR_Z0 - 0.0075), (0.0157, BR_Z0 - 0.0068), (0.0157, BR_Z0 - 0.0010),
                           (0.0148, BR_Z0 + 0.0010)], 16,
                  regs=["lens", "anod", "anod", "anod", "anod", "anod", "anod"])
        elif lod == 1:
            lathe(ob, of, [(0, OBJ_Z + 0.0008), (0.0090, OBJ_Z), (0.0112, OBJ_Z + 0.0010), (0.0155, BR_Z0 - 0.007),
                           (0.0155, BR_Z0 + 0.001)], 10, regs=["lens", "anod", "anod", "anod"])
        else:
            lathe(ob, of, [(0, OBJ_Z), (0.0110, OBJ_Z), (0.0155, BR_Z0 + 0.001)], 6)
        parts.append(ob)
    nc = (3, 1, 0)[lod]
    for i, f in enumerate(EYE):
        o = f.o
        # prism housing: a rounded section, leather between enamel caps (the lower one goes into the
        # bridge)
        pr = P("prism%d" % i, "anod", group=SEL_FOCUS, uv_name="prism", uv_origin=tuple(o))
        sec = (lambda ins: rrect(0.021 - ins, 0.022 - ins, max(0.009 - ins, 0.0004), nc))
        if lod == 0:
            loft(pr, f, sec, [(0.0, -0.006), (0.0, 0.0040), (0.0009, 0.0040), (0.0009, 0.0500), (0.0, 0.0500),
                              (0.0, 0.0600), (0.0016, 0.0634), (0.0045, 0.0652)],
                 regs=["anod", "leather", "leather", "leather", "anod", "anod", "anod"], cap0="anod", cap1="anod")
        elif lod == 1:
            loft(pr, f, sec, [(0.0, -0.006), (0.0, 0.0600), (0.0040, 0.0650)], regs=["leather", "anod"],
                 cap0="anod", cap1="anod")
        else:
            loft(pr, f, sec, [(0.0, -0.006), (0.0, 0.0650)], regs=["leather"], cap0="anod", cap1="anod")
        parts.append(pr)
        # eyepiece: a tube, a chrome diopter ring, a body, a rubber eyecup with the "wing" outward,
        # the lens deep in the eyecup
        ep = P("eyepiece%d" % i, "anod", group=SEL_FOCUS)
        a_out = 0.0 if i == 1 else math.pi

        def wing(a, a_out=a_out):
            return WING * max(0.0, math.cos(a - a_out)) ** 2
        if lod == 0:
            lathe(ep, f, [(0.0108, 0.0640), (0.0108, 0.0705), (0.0134, 0.0718), (0.0134, 0.0772), (0.0119, 0.0786),
                          (0.0119, 0.0870), (0.0153, 0.0982, 0.0, 0.75), (0.0138, 0.1004, 0.0, 1.0),
                          (0.0098, 0.0968, 0.0, 0.6), (0, 0.0960)], 20,
                  regs=["anod", "chrome", "chrome", "chrome", "anod", "rubber", "rubber", "rubber_in", "lens"],
                  hfun=wing)
        elif lod == 1:
            lathe(ep, f, [(0.0108, 0.0640), (0.0134, 0.0715), (0.0134, 0.0775), (0.0119, 0.0786),
                          (0.0150, 0.0995, 0.0, 0.9), (0, 0.0975)], 10,
                  regs=["anod", "chrome", "anod", "rubber", "lens"], hfun=wing)
        else:
            lathe(ep, f, [(0.0120, 0.0640), (0.0145, 0.0990), (0, 0.0990)], 6, regs=["anod", "lens"])
        parts.append(ep)
    if lod == 2:
        return parts
    # folding axis between the housings: a hinge with a dome and two lugs to the housings
    hf = g.Frame(Vector((0, PR_Y, PR_Z)) + Vector(NRM) * -0.006, (1, 0, 0), DIR, NRM)
    hg = P("hinge", "anod", group=SEL_FOCUS)
    if lod == 0:
        lathe(hg, hf, [(0.0070, -0.002), (0.0070, 0.0565), (0.0061, 0.0592), (0.0036, 0.0606), (0, 0.0610)], 16)
        # lugs are their own part: their ends inside the housings face sideways, like the hinge
        # sides
        lg = P("hinge_lugs", "anod", group=SEL_FOCUS)
        for b0, b1 in ((0.008, 0.016), (0.040, 0.048)):
            g.box(lg, -0.0115, 0.0115, b0, b1, -0.0040, 0.0040, frame=hf)
        parts.append(lg)
    else:
        lathe(hg, hf, [(0.0070, -0.002), (0.0070, 0.0590), (0, 0.0605)], 8)
    parts.append(hg)
    # head clamp screw in the bridge, left
    sc = P("bridge_screw", "chrome", group=SEL_FOCUS)
    sf = xframe((-(EYE_X + CAR_R), CAR_Y, (BR_Z0 + BR_Z1) / 2), -1)
    if lod == 0:
        lathe(sc, sf, [(0.0050, -0.0003), (0.0052, 0.0008, 0.0004), (0.0052, 0.0062, 0.0004), (0, 0.0075)], 24)
    else:
        lathe(sc, sf, [(0.0050, -0.0003), (0.0050, 0.0060), (0, 0.0070)], 8)
    parts.append(sc)
    return parts


def build_lod(spec):
    parts = build_stand(spec) + build_arm(spec) + build_head(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    return parts


def collision():
    base = kx.box_pts(-R_BASE, R_BASE, -R_BASE, R_BASE, 0.0, Z_BASE)
    # column, clamp, arm and focus box with handwheels are one convex shape; the head with the
    # eyepieces is the second
    post = kx.box_pts(-0.022, 0.027, FH[2], POST_Y + 0.018, Z_BASE, Z_POST + 0.005)
    head = (kx.box_pts(-(EYE_X + CAR_R), EYE_X + CAR_R, CAR_Y - CAR_R, CAR_Y + CAR_R, OBJ_Z, BR_Z1)
            + [tuple(f.p(a, 0.100, c)) for f in EYE for a in (-0.021, 0.021) for c in (-0.022, 0.022)])
    comps = [(base, kx.PEN + r"\metal.rvmat"), (post, kx.PEN + r"\metal.rvmat"),
             (head, kx.PEN + r"\plastic.rvmat")]
    top = max(q[2] for q in head)
    front = min(q[1] for q in head)
    memory = {
        "invView": [(0.0, -0.60, 0.42)],
        "ozl_focus_axis": [(0.0, CAR_Y, BR_Z1), (0.0, CAR_Y, BR_Z1 - 1.0)],
        "ozl_knob_axis": [(-0.02, KNOB_Y, KNOB_Z), (0.02, KNOB_Y, KNOB_Z)],
    }
    bbox = (-R_BASE, R_BASE, min(-R_BASE, front), R_BASE, 0.0, top)
    print("top %.3f, front %.3f" % (top, front))
    return comps, 0.8, memory, bbox


# The first ones are for the --look preview: overall view, the stage with the light and the
# toggle (also working), the head close up, from the side; the rest - from behind
SHOTS = [
    ("front", (-0.30, -0.48, 0.34), (0.0, 0.0, 0.12), 50),
    ("stage", (0.20, -0.26, 0.15), (0.020, -0.022, 0.030), 60),
    ("head", (-0.16, -0.24, 0.32), (0.0, -0.04, 0.17), 60),
    ("side", (0.55, 0.02, 0.18), (0.0, 0.01, 0.12), 50),
    ("back", (0.30, 0.45, 0.30), (0.0, 0.0, 0.12), 50),
]

M.look_shots = (4, 2)
M.run(build_lod, collision, SHOTS, row_step=0.3, row_shot=((0.3, -1.1, 0.40), (0.3, 0, 0.11)))
