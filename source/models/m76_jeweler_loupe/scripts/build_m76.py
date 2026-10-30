"""M76 - jeweler's loupe (OZL_Tool_JewelerLoupe): a Khabar line module, a portable 2x2 item.
It sits in an OZL_Tool1..3 slot of the packer (M13, M18) and shows in the slot's module place
through the module_N proxy. Model: a watchmaker's stand loupe on a velvet pad.

    blender --background --python build_m76.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py (system Python) before the first build: the base number and the hallmark tag.

Size: the module pad is about 0.2 x 0.2 m with about 0.25 m free above it. Everything together is
0.195 x 0.226 x 0.186 m. Against real stand loupes the stand is shortened to 0.226 m and the arm to
0.15 m; the bell is 95 mm across, the rim 77 mm (lens 65 mm).
Proportions come from real loupes on a cast-iron bell base: bell about 100 mm across and 70 mm
high, neck 37 mm, stand 7-8 mm, arm 5 mm, rim 80 mm. A 10 dpt lens has a 100 mm focus, so the rim
sits about 85 mm above the pad. On the pad: stone tweezers (115 mm), a small dark-blue velvet pad
(118 x 86 x 8 mm, sized to the module pad) and a folded stone parcel paper (60 x 36 mm).

Work look: the loupe has no moving part, so the work look lights a home-made LED ring (frosted
diffuser, 70 mm) under the rim. Selection ozl_lamp; the lit state uses the _on atlas. The ring's
terminal block and a red and black wire lead to a 9 V battery on the pad.
Vanilla DayZ items are proxies (kvanilla): the 9 V battery (its snap with the wire is custom) and
a ballpoint pen (it wrote the tag).

Condition: used but intact - wrinkle enamel worn to bare iron on the bell edge, bluing rubbed off
the stand edges, nickel worn to brass, velvet pressed and rubbed in the middle. Markings are
digits only: an inventory number in white paint on the bell and a text-free tag on a thread by the
ring with the "585" hallmark in pen. LODs: near and mid, no far one.

Blender axes: X is width, Y is depth (the front faces -Y), Z is up. The origin is the centre of
the pad bottom, so the module lands on the module_N proxy point (autocenter = 0 in Geometry).
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
import kvanilla as kv  # noqa: E402
from mathutils import Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m ------------------------------------------------------------------------------
B = Vector((-0.050, 0.050, 0.0))        # stand axis = bell centre
R_FOOT, H_LIP = 0.0475, 0.005           # bell: foot lip radius, lip height
R_DOME, Z_DOME0, Z_DOME1 = 0.0462, 0.0062, 0.0442
R_NECK, Z_NECK1, Z_TOP = 0.0190, 0.0585, 0.0605
R_ROD, Z_ROD = 0.0040, 0.224            # stand: radius, top height
Z_ARM = 0.168                           # arm axis height in the clamp
ARM_OFF = 0.012                         # the arm runs in front of the stand (beside it)
ARM_R, ARM_TAIL = 0.0026, 0.040
SPRING = (0.1790, 0.2110, 0.0068, 0.0009, 5.5)  # bottom, top, coil radius, wire radius, turns
COLLAR = (0.2112, 0.2185, 0.0072)
L = Vector((0.034, -0.036, 0.092))      # lens centre
TILT = math.radians(22)                 # the rim is tilted toward the viewer (-Y)
R_IN, R_OUT, RIM_H = 0.0325, 0.0385, 0.012
GL_EDGE, GL_MID = 0.0010, 0.0034        # lens half-thickness at the edge and in the centre
PAD_C, PAD, PAD_ROT = (0.036, -0.044), (0.118, 0.086, 0.008), math.radians(-3.0)
Z_PAD = PAD[2]
RING_C, RING_R, RING_T, RING_PHI = (0.031, -0.035), 0.0098, 0.0016, math.radians(-120)
BEZEL_R = 0.0030
TAG_C, TAG, TAG_T = (0.058, -0.024), (0.024, 0.013), 0.0004
TWZ = ((-0.020, -0.077), (0.092, -0.060), 0.115)   # tweezers: rear point, tip point, length
PARCEL_C, PARCEL = (-0.062, -0.044), (0.060, 0.036, 0.0035)
# LED ring under the rim (work look): inner and outer radius, height. It sticks out 2 mm past the
# rim, so the glowing band shows from the front and the side, not only from below. Wire block on the
# ring: angle from LF.u to LF.v. The 9 V battery lies on the pad behind the velvet, terminals toward
# the lens (-Y). The wire is a pair of cores from the ring block to the battery block.
LED = (R_IN + 0.0010, R_OUT + 0.0022, 0.0034)
LED_PSI = math.radians(45)
BAT_C, BAT_DEG = (0.060, 0.028), -90.0
PEN_C, PEN_DEG = (0.040, 0.074), -20.0  # pen: rear right, clear of the bell and the battery
WIRE_R = 0.00075

LF = g.Frame(L, (1, 0, 0), (0, math.cos(TILT), math.sin(TILT)), (0, -math.sin(TILT), math.cos(TILT)))
BOUNDS = {}

LOD_SPECS = [
    dict(lod=0),
    dict(lod=1),
]

REGIONS = {
    "iron": ("iron", 1.0), "blued": ("blued", 1.4), "nickel": ("nickel", 1.4), "spring": ("spring", 0.6),
    "velvet": ("velvet", 0.9), "gold": ("gold", 2.0), "garnet": ("garnet", 2.0), "tag": ("tag", 3.0),
    "string": ("string", 0.5), "tweezers": ("tweezers", 1.5), "paper": ("paper", 1.2), "glass": ("nickel", 1.0),
    "led": ("led", 1.2), "black": ("black", 1.2), "wire_red": ("wire_red", 0.5), "wire_black": ("wire_black", 0.5),
}

SEL_LAMP = "ozl_lamp"
# work look: the LED ring glows (_on atlas, rvmat with emission); no moving parts
ON = dict(remap={"led": "led_on"}, emissive=(1.0, 1.0, 1.0, 1.0))

# vanilla DayZ items: 9 V battery lying, terminals toward the lens; pen lying, clip up
DECOR = [
    kv.put("battery9v", (BAT_C[0], BAT_C[1], 0.0), **kv.flat(BAT_DEG)),
    kv.put("pen", (PEN_C[0], PEN_C[1], 0.0), up=(math.cos(math.radians(PEN_DEG)), math.sin(math.radians(PEN_DEG)), 0.0),
           fwd=(0.0, 0.0, -1.0)),
]


def wdecal(name):
    return os.path.join(WORK, name)


# decals: (image, normal axis, sign, (u axis, v axis), centre (u, v), size (w, h), range along the
# normal)
NUM_DEC = (wdecal("decal_num.png"), "y", -1, ("x", "z"), (B.x + 0.002, 0.020), (0.016, 0.010),
           (B.y - R_FOOT - 0.003, B.y - 0.015))
TAG_DEC = (wdecal("decal_tag.png"), "z", 1, ("x", "y"), TAG_C, TAG, (Z_PAD + TAG_T - 0.001, Z_PAD + TAG_T + 0.001))


# =============================================================================
# Materials
# =============================================================================
def scaled(color, k):
    return tuple(min(1.0, c * k) for c in color[:3]) + (1,)


def mat_wrinkle(mat, origin, **kw):
    """Black wrinkle enamel over cast iron (as on 1950-80s instruments): a net of small winding ridges
    about 4 mm wide over the painted metal. The ridges catch light; the relief is in the normals.
    """
    outs = kmats.build_paint(mat, origin, **kw)
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    vec, sep = t.coords(origin, 19.0)
    n = t.noise(vec, 260.0, 3.0, 0.55)
    ridge = t.math("SUBTRACT", 1.0, t.math("ABSOLUTE", t.math("SUBTRACT", t.math("MULTIPLY", n, 2.0), 1.0)))
    ridge = t.maprange(ridge, 0.55, 0.95, 0.0, 1.0)
    col = kmats.sock(mat, outs["color"])
    col = t.mixc(t.math("MULTIPLY", ridge, 0.35), col, scaled(kw["color"], 2.2))
    h = outs["height"]
    hh = t.math("ADD", kmats.sock(mat, h) if not isinstance(h, (int, float)) else h, t.math("MULTIPLY", ridge, 0.12))
    return dict(outs, color=kmats.Tree.ref(col), height=kmats.Tree.ref(hh))


def mat_nickel(mat, origin, brass=kmats.lin((162, 126, 60)), **kw):
    """Nickel over brass (rim, hinge, screws): brushed metal, worn to yellow brass on the edges and in
    patches, dark tarnish in the corners. Replaces light chrome, which rendered as white plastic in
    the preview.
    """
    outs = kmats.build_steel(mat, origin, **kw)
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    vec, sep = t.coords(origin, kw.get("seed", 2.0) + 0.7)
    edge = t.maprange(t.edge_wear(0.0012), 0.04, 0.22, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 140.0, 6.0, 0.7), 0.75), t.math("MULTIPLY", edge, 0.75))
    worn = t.step(f, 0.58, 0.64)
    col = kmats.sock(mat, outs["color"])
    col = t.mixc(t.math("MULTIPLY", worn, 0.85), col, brass)
    tar = t.maprange(t.noise(vec, 30.0, 5.0, 0.6), 0.45, 0.75, 0.0, 0.35)
    col = t.mixc(tar, col, kmats.lin((62, 56, 40)))
    return dict(outs, color=kmats.Tree.ref(col))


def mat_tweezers(mat, origin, **kw):
    """Tweezers: steel along the length, a cross-ribbed grip in the middle (dark grooves at a 1.2 mm pitch)."""
    outs = kmats.build_steel(mat, origin, **kw)
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    vec, sep = t.coords(origin, 0.0)
    (x0, y0), (x1, y1), ln = TWZ
    ux, uy = x1 - x0, y1 - y0
    m = math.hypot(ux, uy)
    ux, uy = ux / m, uy / m
    s = t.math("ADD", t.math("MULTIPLY", t.math("SUBTRACT", sep.outputs["X"], x0), ux),
               t.math("MULTIPLY", t.math("SUBTRACT", sep.outputs["Y"], y0), uy))
    zone = t.math("MULTIPLY", t.math("GREATER_THAN", s, 0.034), t.math("LESS_THAN", s, 0.066))
    groove = t.step(t.math("SINE", t.math("MULTIPLY", s, 2 * math.pi / 0.0012)), 0.2, 0.5)
    g_ = t.math("MULTIPLY", zone, groove)
    col = t.mixc(t.math("MULTIPLY", g_, 0.6), kmats.sock(mat, outs["color"]), kmats.lin((40, 40, 42)))
    h = outs["height"]
    hh = t.math("SUBTRACT", kmats.sock(mat, h) if not isinstance(h, (int, float)) else h, t.math("MULTIPLY", g_, 0.3))
    return dict(outs, color=kmats.Tree.ref(col), height=kmats.Tree.ref(hh))


def mat_velvet(mat, origin, color, seed=7.7):
    """Dark-blue velvet: patches of pressed nap, nap lighter on rounded edges, a rubbed spot in the middle
    where stones are laid out, rare fibres and dust specks.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nap = t.maprange(t.noise(vec, 60.0, 6.0, 0.65), 0.30, 0.72, 0.0, 1.0)
    col = t.mixc(nap, scaled(color, 0.72), scaled(color, 1.35))
    fine = t.noise(vec, 1400.0, 2.0, 0.5)
    col = t.mixc(t.maprange(fine, 0.3, 0.7, 0.0, 0.30), col, scaled(color, 0.55))
    edge = t.maprange(t.edge_wear(0.003), 0.03, 0.20, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.55), col, scaled(color, 2.1))
    dx = t.math("SUBTRACT", sep.outputs["X"], RING_C[0])
    dy = t.math("SUBTRACT", sep.outputs["Y"], RING_C[1])
    rad = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", dx, dx), t.math("MULTIPLY", dy, dy)))
    worn = t.math("MULTIPLY", t.maprange(rad, 0.012, 0.042, 1.0, 0.0),
                  t.maprange(t.noise(vec, 25.0, 4.0, 0.6), 0.3, 0.7, 0.4, 1.0))
    col = t.mixc(t.math("MULTIPLY", worn, 0.45), col, kmats.lin((70, 74, 98)))
    lint = t.step(t.noise(vec, 500.0, 2.0, 0.5), 0.80, 0.81)
    col = t.mixc(t.math("MULTIPLY", lint, 0.35), col, kmats.lin((120, 118, 112)))
    # patchy dust (no shared "dayz" layers: their scratches and streaks suit metal and paint)
    dust = t.math("MULTIPLY", t.maprange(t.noise(vec, 9.0, 6.0, 0.6), 0.45, 0.75, 0.0, 0.22),
                  t.maprange(t.math("ABSOLUTE", sep.outputs["X"]), 0.02, 0.09, 0.4, 1.0))
    col = t.mixc(dust, col, kmats.lin((96, 92, 86)))
    gloss = t.math("ADD", 0.10, t.math("MULTIPLY", worn, 0.12))
    spec = t.math("ADD", 0.05, t.math("MULTIPLY", worn, 0.05))
    return kmats.out(t, col, gloss, spec, t.math("MULTIPLY", fine, 0.15))


def mat_gold(mat, origin, color, seed=8.1, gloss=0.78, spec=0.9):
    """585 gold of the ring: warm yellow with a red tint, polished lighter on the edges, dark tarnish in
    the corners of the setting, fine hairline scratches on the shank.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    base = t.mixc(t.maprange(t.noise(vec, 400.0, 4.0, 0.6), 0.3, 0.7, 0.0, 1.0), scaled(color, 0.85), color)
    edge = t.maprange(t.edge_wear(0.0006), 0.05, 0.30, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.5), base, scaled(color, 1.25))
    sc = t.step(t.noise(t.stretch(vec, 0.05, 1.0, 1.0), 900.0, 2.0, 0.5), 0.70, 0.72)
    col = t.mixc(t.math("MULTIPLY", sc, 0.3), col, scaled(color, 1.3))
    cav = t.maprange(t.cavity(0.004), 0.10, 0.50, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.6), col, kmats.lin((60, 40, 18)))
    g_ = t.math("SUBTRACT", gloss, t.math("MULTIPLY", cav, 0.3))
    return kmats.out(t, col, g_, spec, 0.0)


def mat_parcel(mat, origin, **kw):
    """Stone parcel paper: white paper, fold lines of the tucked flaps near the ends, a blue lining
    showing at the end.
    """
    outs = kmats.build_plastic(mat, origin, **kw)
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    vec, sep = t.coords(origin, 0.0)
    x = sep.outputs["X"]
    x0, x1 = PARCEL_C[0] - PARCEL[0] / 2, PARCEL_C[0] + PARCEL[0] / 2
    fold = None
    for c in (x0 + 0.007, x1 - 0.007):
        f = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", x, c)), 0.0, 0.0006, 1.0, 0.0)
        fold = f if fold is None else t.math("MAXIMUM", fold, f)
    col = kmats.sock(mat, outs["color"])
    col = t.mixc(t.math("MULTIPLY", fold, 0.15), col, kmats.lin((150, 146, 136)))
    liner = t.math("MULTIPLY", t.math("GREATER_THAN", x, x1 - 0.0015),
                   t.math("LESS_THAN", sep.outputs["Z"], PARCEL[2] - 0.0006))
    col = t.mixc(liner, col, kmats.lin((150, 180, 214)))
    h = t.math("MULTIPLY", fold, -0.2)
    return dict(outs, color=kmats.Tree.ref(col), height=kmats.Tree.ref(h))


def mat_tag(mat, origin, decal_items=(), **kw):
    """Cardboard tag: cardboard (plastic without gloss) with the pen entry on top."""
    outs = kmats.build_plastic(mat, origin, **kw)
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    vec, sep = t.coords(origin, 0.0)
    col = kmats.decals(t, kmats.sock(mat, outs["color"]), sep, t.normal(), decal_items)
    return dict(outs, color=kmats.Tree.ref(col))


KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    # bell: black wrinkle enamel, the edge worn to grey cast iron, almost no rust
    "iron": (mat_wrinkle, dict(color=kmats.lin((24, 24, 25)), under=kmats.lin((70, 68, 66)), seed=4.6, gloss=0.35,
                               spec=0.25, chip=(0.72, 0.78), rust=(0.92, 0.96), rust_low=0.08, dust=0.18,
                               grime=0.15, decal_items=[NUM_DEC])),
    # blued steel of the stand, clamp and arm: rubbed to bare steel on the edges
    "blued": ("paint", dict(color=kmats.lin((36, 38, 46)), under=kmats.lin((108, 108, 112)), seed=6.1, gloss=0.55,
                            spec=0.50, chip=(0.78, 0.84), rust=(0.94, 0.98), rust_low=0.0, dust=0.10, grime=0.10)),
    # nickel over brass (rim, hinge, screws): darker than bright steel, brass on the edges
    "nickel": (mat_nickel, dict(seed=7.1, tone=0.30, along="z", gloss=0.70, spec=0.80, dust=0.10, grime=0.15)),
    # spring: dark spring steel in oil and dust
    "spring": ("steel", dict(seed=6.4, tone=0.17, along="z", gloss=0.40, spec=0.50, dust=0.15, grime=0.4)),
    "velvet": (mat_velvet, dict(color=kmats.lin((26, 34, 78)))),
    # 585 gold - slightly reddish, worn (lighter on the edges), tarnish in the corners
    "gold": (mat_gold, dict(color=kmats.lin((204, 150, 62)))),
    "garnet": ("flat", dict(color=kmats.lin((110, 10, 22)), gloss=0.92, spec=0.9)),
    "tag": (mat_tag, dict(color=kmats.lin((214, 198, 156)), seed=8.8, gloss=0.08, spec=0.05, mottle=0.10,
                          dust=0.05, grime=0.10, scuff=(0.85, 0.95), decal_items=[TAG_DEC])),
    "string": ("plastic", dict(color=kmats.lin((178, 162, 128)), seed=8.4, gloss=0.08, spec=0.05, mottle=0.15,
                               dust=0.05, grime=0.2)),
    "tweezers": (mat_tweezers, dict(seed=9.1, tone=0.30, along="x", gloss=0.65, spec=0.7, dust=0.06, grime=0.10)),
    "paper": (mat_parcel, dict(color=kmats.lin((232, 230, 220)), seed=9.9, gloss=0.10, spec=0.05, mottle=0.04,
                               dust=0.10, grime=0.12, scuff=(0.9, 1.0))),
    # LED ring: matte milky diffuser; warm white when lit in the work look
    "led": ("plastic", dict(color=kmats.lin((206, 206, 198)), seed=9.4, gloss=0.45, spec=0.30, mottle=0.05,
                            dust=0.15, grime=0.25)),
    "led_on": ("flat", dict(color=kmats.lin((255, 248, 228)), gloss=0.45, spec=0.30)),
    "wire_red": ("plastic", dict(color=kmats.lin((150, 26, 22)), seed=9.6, gloss=0.40, spec=0.25, dust=0.1,
                                 grime=0.2)),
    "wire_black": ("plastic", dict(color=kmats.lin((24, 24, 26)), seed=9.7, gloss=0.40, spec=0.25, dust=0.1,
                                   grime=0.2)),
})

M = kmodel.Model(__file__, "m76_jeweler_loupe", "ozr_jeweler_loupe", REGIONS, KINDS, LOD_SPECS, atlas=1024,
                 look="dayz", glass=dict(base=(0.72, 0.78, 0.80), clear=0.02, edge=0.07, smudge=0.06, streaks=0.0),
                 selections=(SEL_LAMP,), hidden=(SEL_LAMP,), states={"on": ON}, decor=DECOR)
P = M.part


# =============================================================================
# Primitives missing from kgeo: solid of revolution, torus, variable-width strip, curve
# =============================================================================
def lathe(part, fr, prof, sides, cap_lo=False, cap_hi=False, phase=0.0):
    """Solid of revolution around the axis fr.n. The profile [(r, h)] is traversed so that the outside is
    on the right (segment normal (dh, -dr)); faces turn outward along that normal, caps along the axis.
    """
    bm = part.bm
    angs = [2 * math.pi * (k + phase) / sides for k in range(sides)]
    rings = [[bm.verts.new(fr.p(r * math.cos(a), r * math.sin(a), h)) for a in angs] for r, h in prof]
    faces = []
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        for k in range(sides):
            j = (k + 1) % sides
            f = bm.faces.new([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]])
            am = 2 * math.pi * (k + 0.5 + phase) / sides
            want = (fr.u * math.cos(am) + fr.v * math.sin(am)) * (h1 - h0) - fr.n * (r1 - r0)
            f.normal_update()
            if f.normal.dot(want) < 0:
                f.normal_flip()
            faces.append(f)
    for ring, sign, on in ((rings[0], -1, cap_lo), (rings[-1], 1, cap_hi)):
        if on:
            f = bm.faces.new(ring)
            f.normal_update()
            if f.normal.dot(fr.n) * sign < 0:
                f.normal_flip()
            faces.append(f)
    return part.tag(faces)


def torus(part, fr, R, r, n_major, n_minor):
    """Torus around the axis fr.n with major radius R and section radius r."""
    bm = part.bm
    rings = []
    for i in range(n_major):
        a = 2 * math.pi * i / n_major
        d = fr.u * math.cos(a) + fr.v * math.sin(a)
        rings.append([bm.verts.new(fr.o + d * (R + r * math.cos(b)) + fr.n * (r * math.sin(b)))
                      for b in [2 * math.pi * j / n_minor for j in range(n_minor)]])
    faces = []
    for i in range(n_major):
        i2 = (i + 1) % n_major
        am = 2 * math.pi * (i + 0.5) / n_major
        d = fr.u * math.cos(am) + fr.v * math.sin(am)
        for j in range(n_minor):
            j2 = (j + 1) % n_minor
            f = bm.faces.new([rings[i][j], rings[i2][j], rings[i2][j2], rings[i][j2]])
            bm_ = 2 * math.pi * (j + 0.5) / n_minor
            f.normal_update()
            if f.normal.dot(d * math.cos(bm_) + fr.n * math.sin(bm_)) < 0:
                f.normal_flip()
            faces.append(f)
    return part.tag(faces)


def strip(part, pts, normal, half_t, half_w):
    """Strip along a polyline in a plane with the given normal: thickness 2*half_t in the plane, width
    2*half_w[i] along the normal (g.sweep has a constant width).
    """
    bm = part.bm
    pts = [Vector(p) for p in pts]
    nrm = Vector(normal).normalized()
    n = len(pts)
    rings = []
    for i in range(n):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        side = t.cross(nrm).normalized() * half_t
        up = nrm * half_w[i]
        c = pts[i]
        rings.append([bm.verts.new(c + side + up), bm.verts.new(c - side + up),
                      bm.verts.new(c - side - up), bm.verts.new(c + side - up)])
    new = []
    for i in range(n - 1):
        r0, r1 = rings[i], rings[i + 1]
        for q in range(4):
            new.append(bm.faces.new([r0[q], r0[(q + 1) % 4], r1[(q + 1) % 4], r1[q]]))
    new.append(bm.faces.new(rings[0][::-1]))
    new.append(bm.faces.new(rings[-1]))

    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, as in M16)."""
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


def axis_frame(p0, p1):
    p0, p1 = Vector(p0), Vector(p1)
    n = (p1 - p0).normalized()
    ref = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = ref.cross(n).normalized()
    return g.Frame(p0, u, n.cross(u), n), (p1 - p0).length


def rod(part, p0, p1, r, sides, r2=None, cap=True):
    """Cylinder (cone r -> r2) from point p0 to p1."""
    fr, ln = axis_frame(p0, p1)
    return g.cyl(part, (0, 0, ln / 2), "z", r, ln, sides, r2=r2, cap=cap, frame=fr)


def flat_frame(c, rot, z=0.0):
    return g.Frame((c[0], c[1], z), (math.cos(rot), math.sin(rot), 0), (-math.sin(rot), math.cos(rot), 0), (0, 0, 1))


def screw_head(part, p, axis, r, h, sides):
    """Screw head or wing nut with chamfers: from point p along axis for length h."""
    a = Vector(axis).normalized()
    fr, _ = axis_frame(p, Vector(p) + a)
    c = min(r * 0.25, h * 0.3)
    return lathe(part, fr, [(r - c, 0.0), (r, c), (r, h - c), (r - c, h)], sides, cap_lo=True, cap_hi=True)


# =============================================================================
# Arm nodes: where the clamp is, where the arm runs, where it enters the rim
# =============================================================================
def arm_geometry():
    """The arm runs from the rim hinge to the clamp; the clamp sits on the stand, and the arm passes in
    front of the stand by ARM_OFF. The clamp point is refined iteratively: the arm direction depends on it.
    """
    to_b = Vector((B.x - L.x, B.y - L.y, 0.0))
    rad = (to_b - LF.n * to_b.dot(LF.n)).normalized()          # toward the stand, in the rim plane
    a_rim = L + rad * (R_OUT - 0.001)
    a_knk = L + rad * (R_OUT + 0.0075)                           # rim hinge
    c = Vector((B.x, B.y, Z_ARM))
    for _ in range(6):
        d = Vector((a_knk.x - c.x, a_knk.y - c.y, 0.0)).normalized()
        q = d.cross(Vector((0, 0, 1)))                           # sideways, forward-left
        c = Vector((B.x, B.y, Z_ARM)) + q * ARM_OFF
    u = (c - a_knk).normalized()
    e = c + u * ARM_TAIL
    h = LF.n.cross(rad).normalized()                             # hinge axis (toward the viewer)
    return dict(rad=rad, a_rim=a_rim, a_knk=a_knk, c=c, d=d, q=q, e=e, u=u, h=h)


AG = arm_geometry()


# =============================================================================
# Base, stand, clamp, spring
# =============================================================================
def bell_profile(hi):
    """Bell profile from the bottom up: cast lip with a rounded edge, dome, transition into the neck,
    rounded neck top and the stand socket.
    """
    def dome(t):
        a = t * math.pi / 2
        return (R_NECK + (R_DOME - R_NECK) * math.cos(a), Z_DOME0 + (Z_DOME1 - Z_DOME0) * math.sin(a))
    if hi:
        return ([(R_FOOT, 0.0), (R_FOOT, H_LIP - 0.0011), (R_FOOT - 0.0012, H_LIP + 0.0003)]
                + [dome(t) for t in (0.25, 0.55, 0.82)]
                + [(R_NECK + 0.0009, Z_DOME1 + 0.0012), (R_NECK, Z_NECK1 - 0.0016), (R_NECK - 0.0016, Z_NECK1),
                   (R_ROD + 0.0010, Z_TOP), (R_ROD, Z_TOP - 0.0030)])
    return ([(R_FOOT, 0.0), (R_FOOT, H_LIP), (R_DOME - 0.0004, Z_DOME0)] + [dome(t) for t in (0.4, 0.78)]
            + [(R_NECK, Z_DOME1 + 0.001), (R_NECK, Z_NECK1 - 0.0012), (R_NECK - 0.0012, Z_NECK1), (R_ROD, Z_TOP)])


def build_stand(lod):
    hi = lod == 0
    parts = []
    fr = g.Frame(B, (1, 0, 0), (0, 1, 0), (0, 0, 1))
    base = P("base", "iron")
    lathe(base, fr, bell_profile(hi), 24 if hi else 14, cap_lo=True, cap_hi=not hi)
    parts.append(base)
    rd = P("rod", "blued")
    if hi:
        lathe(rd, fr, [(R_ROD, Z_TOP - 0.003), (R_ROD, Z_ROD - 0.0008), (R_ROD - 0.0008, Z_ROD)], 12, cap_hi=True)
    else:
        g.cyl(rd, (B.x, B.y, (Z_NECK1 + Z_ROD) / 2), "z", R_ROD, Z_ROD - Z_NECK1, 6)
    parts.append(rd)
    # locking collar above the spring: chamfered outer edges
    z0, z1, rc = COLLAR
    col = P("collar", "blued")
    if hi:
        lathe(col, fr, [(R_ROD, z0), (rc, z0), (rc, z1 - 0.0007), (rc - 0.0007, z1), (R_ROD, z1)], 12)
    else:
        g.cyl(col, (B.x, B.y, (z0 + z1) / 2), "z", rc, z1 - z0, 6)
    parts.append(col)
    sz0, sz1, sr, sw, turns = SPRING
    sp = P("spring", "spring")
    # coils with pinched ends: the first and last 0.75 turn are tight (pitch = wire thickness)
    per = 10 if hi else 4                  # 36 degrees per segment keeps the coil smooth, no kinks
    n = int(round(turns * per))
    closed = 0.75
    p_c = 2 * sw
    p_a = (sz1 - sz0 - 2 * sw - 2 * closed * p_c) / (turns - 2 * closed)

    def zf(ph):
        if ph < closed:
            return sz0 + sw + ph * p_c
        if ph > turns - closed:
            return sz1 - sw - (turns - ph) * p_c
        return sz0 + sw + closed * p_c + (ph - closed) * p_a
    pts = []
    for i in range(n + 1):
        ph = turns * i / n
        a = 2 * math.pi * ph + 0.6
        pts.append((B.x + sr * math.cos(a), B.y + sr * math.sin(a), zf(ph)))
    g.pipe(sp, pts, sw if hi else sw * 1.3, 4 if hi else 3)
    if hi:
        # collar lock screw, forward-left: thread and a chamfered head
        cs = P("collar_screw", "nickel")
        cz = (z0 + z1) / 2
        q = AG["q"]
        rod(cs, (B.x + q.x * rc * 0.8, B.y + q.y * rc * 0.8, cz), (B.x + q.x * (rc + 0.0012), B.y + q.y * (rc + 0.0012), cz),
            0.0011, 6, cap=False)
        screw_head(cs, (B.x + q.x * (rc + 0.0010), B.y + q.y * (rc + 0.0010), cz), q, 0.0024, 0.0026, 8)
        parts.append(cs)
    parts.append(sp)
    # clamp on the stand: a block along the arm; the stand passes through it (behind) and the arm
    # (in front)
    bf = g.Frame((B.x, B.y, 0.0), AG["d"], (0, 0, 1), AG["q"])
    cl = P("clamp", "blued")
    g.box(cl, -0.0075, 0.0075, Z_ARM - 0.010, Z_ARM + 0.010, -0.0085, ARM_OFF + 0.0075,
          **({"r": 0.0012, "seg": 2} if hi else {}), frame=bf)
    parts.append(cl)
    if hi:
        # wing screw clamping the arm, on the clamp's front face: thread, boss, two round wings
        sh = P("wing_shaft", "nickel")
        g.cyl(sh, (0.0, Z_ARM, ARM_OFF + 0.0095), "z", 0.0016, 0.0040, 8, cap=False, frame=bf)
        lathe(sh, g.Frame(bf.p(0.0, Z_ARM, ARM_OFF + 0.0110), bf.u, bf.v, bf.n),
              [(0.0018, 0.0), (0.0026, 0.0006), (0.0026, 0.0040), (0.0020, 0.0048)], 8, cap_hi=True)
        parts.append(sh)
        wg = P("wing", "nickel")
        qw = ARM_OFF + 0.0114
        half = [(0.0021, 0.0000), (0.0052, 0.0022), (0.0074, 0.0044), (0.0080, 0.0062), (0.0071, 0.0076),
                (0.0050, 0.0078), (0.0026, 0.0068)]
        wing = [(Z_ARM + b, qw + c) for b, c in half] + [(Z_ARM - b, qw + c) for b, c in reversed(half)]
        g.prism(wg, wing, (1, 2), -0.0008, 0.0008, frame=bf)
        parts.append(wg)
    else:
        wg = P("wing", "nickel")
        g.prism(wg, [(Z_ARM - 0.0020, ARM_OFF + 0.0075), (Z_ARM + 0.0020, ARM_OFF + 0.0075),
                     (Z_ARM + 0.0075, ARM_OFF + 0.0185), (Z_ARM - 0.0075, ARM_OFF + 0.0185)], (1, 2), -0.0009, 0.0009,
                frame=bf)
        parts.append(wg)
    return parts


# =============================================================================
# Arm and rim with the lens, LED ring
# =============================================================================
def build_lens(lod):
    hi = lod == 0
    parts = []
    arm = P("arm", "blued")
    rod(arm, AG["a_knk"], AG["e"], ARM_R, 10 if hi else 5)
    parts.append(arm)
    # tail knob of the arm: turned, rounded
    knob = P("arm_knob", "blued")
    kf, _ = axis_frame(AG["e"], AG["e"] + AG["u"])
    if hi:
        lathe(knob, kf, [(ARM_R + 0.0002, -0.0020), (0.0039, -0.0013), (0.0042, 0.0004), (0.0039, 0.0058),
                         (0.0030, 0.0075), (0.0014, 0.0082)], 10, cap_hi=True)
    else:
        lathe(knob, kf, [(0.0042, -0.0020), (0.0042, 0.0050), (0.0024, 0.0080)], 6, cap_lo=True, cap_hi=True)
    parts.append(knob)
    # rim hinge: a boss from the rim, an axle across it, a wing nut toward the viewer
    boss = P("boss", "nickel")
    rod(boss, AG["a_rim"], AG["a_knk"], 0.0034, 10 if hi else 5, cap=not hi)
    parts.append(boss)
    kn = P("knuckle", "nickel")
    h = AG["h"]
    rod(kn, AG["a_knk"] - h * 0.0050, AG["a_knk"] + h * 0.0050, 0.0042, 10 if hi else 6)
    if hi:
        screw_head(kn, AG["a_knk"] + h * 0.0049, h, 0.0050, 0.0030, 10)
    parts.append(kn)
    n = 28 if hi else 16
    hh = RIM_H / 2
    rim = P("rim", "nickel")
    if hi:
        # front edge rounded in two steps (the highlight runs along the edge without a break), back
        # edge chamfered
        prof = [(R_IN, -hh), (R_OUT - 0.0012, -hh), (R_OUT, -hh + 0.0012),
                (R_OUT, hh - 0.0014), (R_OUT - 0.0004, hh - 0.0004), (R_OUT - 0.0014, hh), (R_IN, hh)]
    else:
        prof = [(R_IN, -hh), (R_OUT - 0.0012, -hh), (R_OUT, -hh + 0.0012), (R_OUT, hh - 0.0012),
                (R_OUT - 0.0012, hh), (R_IN, hh)]
    lathe(rim, LF, prof, n)
    parts.append(rim)
    # inner wall is a separate part: its faces point the same way as the outer faces on the opposite
    # side of the rim, and in one part they would share one atlas rectangle (the M44 pitfall)
    rin = P("rim_in", "nickel")
    lathe(rin, LF, [(R_IN, hh), (R_IN, -hh)], n)
    parts.append(rin)
    gl = P("lens", "glass", section="glass")
    r2 = R_IN * 0.5
    lathe(gl, LF, [(r2, -GL_MID + 0.0004), (R_IN - 0.0002, -GL_EDGE), (R_IN - 0.0002, GL_EDGE), (r2, GL_MID - 0.0004)],
          14 if hi else 10, cap_lo=True, cap_hi=True)
    gl.glass_frame = (LF, -R_IN, R_IN, -R_IN, R_IN)
    parts.append(gl)
    # LED ring under the rim (selection ozl_lamp): the diffuser is the bottom face, both walls and
    # the top of the ledge past the rim (under the rim chamfer)
    led = P("led_ring", "led", group=SEL_LAMP)
    r0, r1, lh = LED
    lathe(led, LF, [(r0, -hh), (r0, -hh - lh), (r1, -hh - lh), (r1, -hh), (R_OUT - 0.0012, -hh)], n)
    parts.append(led)
    # ring wire block (black plastic) and the wire to the battery
    rm = (r0 + r1) / 2
    cdir = LF.u * math.cos(LED_PSI) + LF.v * math.sin(LED_PSI)
    ctan = LF.n.cross(cdir)
    lo_ = LF.p(0, 0, -hh - lh) + cdir * rm
    cf = g.Frame(lo_, cdir, ctan, -LF.n)
    st = P("led_plug", "black")
    g.box(st, -0.0030, 0.0030, -0.0035, 0.0035, -0.0004, 0.0030, **({"r": 0.0006, "seg": 1} if hi else {}), frame=cf)
    parts.append(st)
    parts += build_lead(lod, cf.p(0, 0, 0.0028), -LF.n)
    return parts


def battery_snap_box():
    """9 V battery snap: fitted on the terminals (the end of the vanilla battery's bounds facing the lens)."""
    lo, hi = kv.box("battery9v")
    y_end = BAT_C[1] - (hi[1] - (lo[1] + hi[1]) / 2)              # terminal end (item +Y -> Blender -Y)
    top = hi[2] - lo[2]
    return (BAT_C[0] - 0.0141, BAT_C[0] + 0.0141, y_end - 0.0020, y_end + 0.0045, 0.0002, top + 0.0005)


def build_lead(lod, start, sdir):
    """Snap on the battery and a pair of cores to the LED ring. The wire leaves the snap forward, at once
    rises over the back edge of the pad and goes up to the ring block with a slight slack.
    """
    hi = lod == 0
    parts = []
    x0, x1, y0, y1, z0, z1 = battery_snap_box()
    sn = P("bat_snap", "black")
    g.box(sn, x0, x1, y0, y1, z0, z1, **({"r": 0.0012, "seg": 1} if hi else {}))
    parts.append(sn)
    zc = (z0 + z1) / 2
    bx = BAT_C[0]
    s = Vector(start)
    ctrl = [(bx, y0 + 0.0008, zc), (bx, y0 - 0.0018, zc + 0.0016), (bx + 0.0012, y0 - 0.0036, zc + 0.0090),
            (bx + 0.0050, y0 - 0.0062, 0.048), tuple(s + sdir * 0.010), tuple(s - sdir * 0.001)]
    if hi:
        path = spline(ctrl, 2)
        for j, reg in enumerate(("wire_red", "wire_black")):
            off = Vector(((j - 0.5) * 2.2 * WIRE_R, 0.0, 0.0))
            w = P("lead_%d" % j, reg)
            g.pipe(w, [tuple(Vector(p) + off) for p in path], WIRE_R, 4)
            parts.append(w)
    else:
        w = P("lead", "wire_black")
        g.pipe(w, spline([ctrl[0], ctrl[2], ctrl[3], ctrl[4], ctrl[5]], 1), WIRE_R * 1.8, 3)
        parts.append(w)
    return parts


# =============================================================================
# Pad: velvet, ring with a tag, tweezers, stone parcel paper
# =============================================================================
def ring_frame():
    """The ring lies on the velvet, resting on the lower edge of the stone setting and the far side of the
    shank: tilted setting-up by atan((rb - r) / 2R).
    """
    alpha = math.atan((BEZEL_R - RING_T) / (2 * RING_R))
    dh = Vector((math.cos(RING_PHI), math.sin(RING_PHI), 0.0))
    w = dh * math.cos(alpha) + Vector((0, 0, 1)) * math.sin(alpha)
    s = Vector((0, 0, 1)).cross(dh).normalized()
    cz = Z_PAD + RING_R * math.sin(alpha) + RING_T * math.cos(alpha)
    return g.Frame((RING_C[0], RING_C[1], cz), w, s, w.cross(s))


def build_ring(lod):
    """Gold ring: torus shank, setting cup, a garnet with a cut (table and crown) in four prongs."""
    hi = lod == 0
    parts = []
    rf = ring_frame()
    ring = P("ring", "gold")
    torus(ring, rf, RING_R, RING_T, 20 if hi else 10, 5 if hi else 3)
    parts.append(ring)
    # setting: its axis points outward from the shank (rf.u)
    sf = g.Frame(rf.p(RING_R + RING_T * 0.6, 0, 0), rf.v, rf.n, rf.u)
    bz = P("bezel", "gold")
    if hi:
        lathe(bz, sf, [(0.0012, -0.0004), (BEZEL_R * 0.80, 0.0008), (BEZEL_R, 0.0022), (BEZEL_R - 0.0003, 0.0027)], 8,
              cap_lo=True)
        for k in range(4):
            a = 2 * math.pi * (k + 0.5) / 4
            d = sf.u * math.cos(a) + sf.v * math.sin(a)
            rod(bz, sf.o + d * (BEZEL_R - 0.0001) + sf.n * 0.0020, sf.o + d * (BEZEL_R - 0.0010) + sf.n * 0.0041,
                0.00045, 4)
    else:
        lathe(bz, sf, [(BEZEL_R, -0.0004), (BEZEL_R, 0.0027)], 6, cap_lo=True, cap_hi=True)
    parts.append(bz)
    st = P("stone", "garnet")
    if hi:
        # cut: an octagonal crown from the girdle to the table
        lathe(st, sf, [(BEZEL_R - 0.0006, 0.0024), (BEZEL_R - 0.0006, 0.0030), (0.0013, 0.0044)], 8, cap_hi=True,
              phase=0.5)
    else:
        lathe(st, sf, [(BEZEL_R - 0.0006, 0.0027), (0.0012, 0.0042)], 6, cap_hi=True)
    parts.append(st)
    return parts, rf


def build_pad(lod):
    hi = lod == 0
    parts = []
    pad = P("pad", "velvet")
    w, d, h = PAD
    g.box(pad, -w / 2, w / 2, -d / 2, d / 2, 0.0, h, **({"r": 0.0028, "seg": 2} if hi else {}),
          frame=flat_frame(PAD_C, PAD_ROT))
    parts.append(pad)
    rparts, rf = build_ring(lod)
    parts += rparts
    # tag on a thread: hole on the left, toward the ring
    tg = P("tag", "tag")
    tx, ty = TAG_C
    tw, th = TAG[0] / 2, TAG[1] / 2
    poly = [(tx - tw, ty - th + 0.002), (tx - tw + 0.003, ty - th), (tx + tw, ty - th), (tx + tw, ty + th),
            (tx - tw + 0.003, ty + th), (tx - tw, ty + th - 0.002)]
    g.prism(tg, poly, (0, 1), Z_PAD, Z_PAD + TAG_T)
    parts.append(tg)
    if hi:
        hole = Vector((tx - tw + TAG[1] * 0.42, ty, Z_PAD + TAG_T + 0.0003))
        band = rf.p(RING_R * math.cos(math.radians(150)), RING_R * math.sin(math.radians(150)), 0.0)
        mid = (hole + band) / 2 + Vector((0.0, 0.004, 0.0))
        sg = P("string", "string")
        g.pipe(sg, spline([hole, hole.lerp(mid, 0.5) + Vector((0, 0, 0.0004)), mid + Vector((0, 0, 0.0006)),
                           mid.lerp(band, 0.6) + Vector((0, 0, 0.0008)), band], 2), 0.00045, 3)
        parts.append(sg)
    parts += build_tweezers(lod)
    # parcel folded in three along its length: the outer flap is on top, its edge sits slightly back
    # (shadow under it)
    pc = P("parcel", "paper")
    px, py, pz = PARCEL
    x0, x1, y0, y1 = PARCEL_C[0] - px / 2, PARCEL_C[0] + px / 2, PARCEL_C[1] - py / 2, PARCEL_C[1] + py / 2
    g.box(pc, x0, x1, y0, y1, 0.0, pz - 0.0006, **({"r": 0.0006, "seg": 1} if hi else {}))
    parts.append(pc)
    if hi:
        fl = P("parcel_flap", "paper")
        yf = PARCEL_C[1] - 0.004
        g.prism(fl, [(yf, pz - 0.0002), (y1 - 0.0004, pz - 0.0006), (y1 - 0.0004, pz - 0.0002), (yf, pz + 0.0003)],
                (1, 2), x0 + 0.0004, x1 - 0.0004)
        parts.append(fl)
    return parts


def build_tweezers(lod):
    """Stone tweezers lie on the velvet on the lower arm; the upper arm is above it, spread toward the
    tips. The arms are soldered at the back (rounded end), widest in the ribbed middle, tapering to
    thin tips.
    """
    (x0, y0), (x1, y1), ln = TWZ
    u = Vector((x1 - x0, y1 - y0, 0.0)).normalized()
    s = Vector((0, 0, 1)).cross(u)
    o = Vector((x0, y0, Z_PAD))
    th = 0.00055
    if lod == 0:
        aa = (0.0, 0.003, 0.014, 0.040, 0.070, 0.092, 0.106, ln)
        ww = (0.0016, 0.0029, 0.0033, 0.0035, 0.0032, 0.0021, 0.0011, 0.0005)
    else:
        aa, ww = (0.0, 0.014, 0.060, 0.098, ln), (0.0022, 0.0033, 0.0034, 0.0018, 0.0006)
    a0 = 0.014                                                   # the arms are soldered up to here
    parts = []
    for i, lift in enumerate((0.0, 0.0060)):
        cz = []
        for a in aa:
            k = max(0.0, a - a0) / (ln - a0)
            # upper arm: a smooth bend at the solder, then straight to the tip
            cz.append(th + ((2 * th + lift * (k - 0.12 * math.sin(math.pi * k))) if i else 0.0))
        pts = [o + u * a + Vector((0, 0, c)) for a, c in zip(aa, cz)]
        leg = P("tweezer%d" % i, "tweezers")
        strip(leg, pts, s, th, ww)
        parts.append(leg)
    return parts


def build_lod(spec):
    lod = spec["lod"]
    parts = build_stand(lod) + build_lens(lod) + build_pad(lod)
    g.triangulate(parts)
    if lod == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        vs += [Vector(q) for d in DECOR for q in kv.corners(d[5], d[1], d[2], d[3])]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("bounds: %s .. %s" % (tuple(round(c, 4) for c in BOUNDS["lo"]),
                                   tuple(round(c, 4) for c in BOUNDS["hi"])))
        for d in DECOR:
            q = kv.corners(d[5], d[1], d[2], d[3])
            print("decor %s: %s .. %s" % (d[5], tuple(round(min(p[i] for p in q), 4) for i in range(3)),
                                         tuple(round(max(p[i] for p in q), 4) for i in range(3))))
    return parts


def collision():
    """Convex parts: bell, stand with the clamp, arm with the rim and LED ring, pad with the ring and
    tweezers, battery with its snap. Mass is the item's weight in the mod (0.8 kg); module rules are
    not touched.
    """
    circ = [(math.cos(2 * math.pi * k / 12), math.sin(2 * math.pi * k / 12)) for k in range(12)]
    base = ([(B.x + R_FOOT * c, B.y + R_FOOT * s, z) for c, s in circ for z in (0.0, H_LIP)]
            + [(B.x + R_NECK * c, B.y + R_NECK * s, Z_TOP) for c, s in circ]
            + [(B.x + 0.033 * c, B.y + 0.033 * s, 0.036) for c, s in circ])
    q, d = AG["q"], AG["d"]
    post = [tuple(Vector((B.x, B.y, z)) + q * a + d * b) for z in (Z_TOP, Z_ROD + 0.002) for a in (-0.0085, 0.0085)
            for b in (-0.0075, 0.0075)]
    post += [tuple(Vector((B.x, B.y, z)) + q * (ARM_OFF + 0.0075) + d * b) for z in (Z_ARM - 0.010, Z_ARM + 0.010)
             for b in (-0.0075, 0.0075)]
    arm = [tuple(AG["e"] + AG["u"] * 0.008), tuple(AG["c"])]
    arm += [tuple(LF.p(r * c, r * s, h)) for c, s in circ for r, h in ((LED[1], -RIM_H / 2 - LED[2]), (R_OUT, RIM_H / 2))]
    pad = [tuple(flat_frame(PAD_C, PAD_ROT).p(a, b, z)) for a in (-PAD[0] / 2, PAD[0] / 2)
           for b in (-PAD[1] / 2, PAD[1] / 2) for z in (0.0, Z_PAD + 0.004)]
    x0, x1, y0, y1, z0, z1 = battery_snap_box()
    bat = kv.corners(DECOR[0][5], DECOR[0][1], DECOR[0][2], DECOR[0][3])
    bat += [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    comps = [(base, kx.PEN + r"\castiron.rvmat"), (post, kx.PEN + r"\metal.rvmat"),
             (arm, kx.PEN + r"\metal.rvmat"), (pad, kx.PEN + r"\cloth.rvmat"), (bat, kx.PEN + r"\metal.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    memory = {
        # inventory preview camera: front-left and from above (as on M71)
        "invView": [(-0.26, -0.46, 0.40)],
        "ce_center": [(0.0, 0.0, 0.11)],
        "ce_radius": [(0.15, 0.0, 0.11)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


# camera angles: the first three are the --look preview (overall view, lens with the ring, clamp);
# the work look uses the first two
SHOTS = [
    ("front", (-0.16, -0.55, 0.32), (0.0, 0.0, 0.10), 40),
    ("lens", (0.06, -0.24, 0.24), (0.030, -0.030, 0.05), 50),
    ("clamp", (-0.20, -0.17, 0.25), (-0.055, 0.045, 0.175), 70),
    ("right", (0.44, -0.34, 0.30), (0.0, 0.0, 0.10), 40),
    ("left", (-0.50, -0.26, 0.30), (0.0, 0.0, 0.10), 40),
    ("top", (0.05, -0.18, 0.55), (0.0, -0.005, 0.05), 40),
    ("back", (0.40, 0.44, 0.30), (0.0, 0.0, 0.10), 40),
]
M.look_shots = (4, 2)

M.run(build_lod, collision, SHOTS, row_step=0.32, row_shot=((0.16, -1.1, 0.35), (0.16, 0, 0.10)))
