"""M69 - Detector probe (OZL_Tool_AnomProbe): a module of the "Anomaly" line (packers M03 and M09) - a
portable 2x2 item, it stands in slot OZL_Tool1 (slot 1 of the line) and is visible on the shelf of
the machine through a proxy. Variant A: the remote scintillation detector unit of a geological
radiometer, lying on two V-shaped supports.

    blender --background --python build_m69.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (a round sticker with a radiation sign).

Target: ~0.30 x 0.10 x 0.10 m, metal, a rubber cap at the end, a cable; a module is no larger than
~0.2 x 0.2 m by its base and up to ~0.25 m high, with a flat bottom.

Reference and sizes:
- look: SRP-68-01: a light aluminium tube, a black rubber cap at the end on the crystal side (slightly
  thicker than the tube), a light grey end ring, the cable leaves through a gland nut in a steel
  spring, the cable is light (beige) rubber;
- SRP-68-01 per seller catalogues: the console is 218 x 102 x 130 mm, the detector unit is D60 x
  525 mm, the set weighs up to 3.6 kg (zapadpribor.org, meratest.ru, cirspb.ru - from search results,
  the pages did not open); in a photo the tube is ~2.3 times longer than the console, L/D ~8.6 -
  consistent with 525 / 60. Such a probe is 2.6 times longer than a module platform, while the
  module_N places stand 0.21-0.22 m apart: on M09 the shelf is 0.26 m wide at the cabinet side, on M03
  the shelf is 0.29 m with a rim - about 0.26 m fits along the shelf;
- so the length follows a probe of the same class with a NaI 2 x 2" crystal (SRP-68-01 has a long
  crystal for geology): Ludlum 44-10 - D66 x 279 mm, 1.0 kg, aluminium housing (its data sheet).
  Model: a D60 tube (as in SRP-68-01), 0.226 m with the cap and the end ring, 0.254 m with the spring
  entry; along the shelf (X) no further than +-0.13 m from the module_N point (the M09 cabinet wall is
  at 0.135 m, the M03 rim at 0.135 m);
- V supports: 90 degree prisms on a common steel plate in hammered enamel, with rubber strips in the
  notches (no data sheet; per prism drawings of GOST 12195: height ~0.6 of the width);
- weight in the mod is 800 g (OZL_Tool_Base, unchanged); the mass in Geometry is the same.

Modules: `used but intact, worn paint on the edges`, no faction colour. Marks: a round sticker with a
radiation sign on the tube, an empty riveted nameplate, a lead seal on a wire across the joint of the
tube and the end ring; a red belt mark is the centre of the crystal (no digits). LODs (a small item):
near and middle (no spring coils, screws, rivets, seal, knurling), no far one.

Detailing: "dayz" look (matte, dirtier, coloured AO); solids of revolution with a single profile with
rounded edges (the cap, the end ring, the gland cap, the connector) and 32 faces. kexport and krender
smooth by a 40 degree angle: a rod of 10 or more faces is smooth, fewer are faceted, so the cable has
10 faces (5 read as a flat ribbon in the render) and the spring has 10 points per turn. The gland nut
is a hexagon with chamfers; the connector has a ribbed rubber tail, a body, a knurled union nut and a
black insulator; on the belt of the ring there are three slotted lock screws and an indicator lamp in
a chrome mount (facing the viewer); a crimp sleeve at the spring; the prism screws have hex sockets;
the prisms are chamfered; the plate stands on four round rubber feet. No vanilla DayZ items on the
module: the module is itself a 2x2 item and stands in the machine as a proxy.
Working state: the indicator lamp is the ozl_lamp selection (atlas _on, emission), when working it
blinks in short flashes like a pulse count (OZL_Work, blink); the probe has no moving parts.

Blender axes: X is along the probe (along the module shelf), Y is depth (the front face is -Y), Z is
up. The origin is the centre of the bottom: this is how the module stands on the module_N proxy point
(autocenter = 0 in Geometry).
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
R_T = 0.030                     # tube D60 (SRP-68-01)
Y0 = -0.035                     # probe axis; the cable loop lies at the back
# supports: a plate on rubber feet, two 90 degree prisms with rubber strips in the notch
FOOT_H = 0.002
BASE_Z1 = FOOT_H + 0.006
BASE_X0, BASE_X1, BASE_HW = -0.099, 0.073, 0.036
VB_X = (-0.068, 0.042)          # prism centres
VB_T = 0.022                    # prism thickness along the probe
VB_HW = 0.032                   # prism half-width
VB_APEX = BASE_Z1 + 0.008       # bottom of the notch
VB_TOP = BASE_Z1 + 0.034
VB_CH = 0.0025                  # chamfer of the outer top edges of the prism
PAD = 0.002
ZA = VB_APEX + (PAD + R_T) * math.sqrt(2.0)   # axis of a probe lying in a 90 degree notch
# probe along X
CAP_X0, CAP_X1, R_CAP = -0.128, -0.082, 0.0325  # rubber cap (crystal side)
TUBE_X0, TUBE_X1 = -0.086, 0.081               # the tube goes under the cap and under the ring
BAND_X = -0.0495                # red mark of the crystal centre
STICKER_X, STICKER_D = -0.018, 0.030
PLATE_X0, PLATE_X1, PLATE_A = 0.000, 0.030, 0.30   # nameplate at the front, arc half-angle, rad
RING_X0, RING_X1, RING_X2, R_RING, R_FACE = 0.078, 0.093, 0.098, 0.0303, 0.0255
NUT_X0, NUT_X1, R_NUT = 0.098, 0.104, 0.0105
CABLE_R = 0.0035                # cable D7
SPRING_R, SPRING_W, SPRING_PITCH = 0.0058, 0.0009, 0.0050
SEAL_X = (0.0725, 0.0855)       # seal screws: on the tube and on the ring
SEAL_DZ = 0.008                 # above the axis, at the front
PLUG_X0, PLUG_X1, R_PLUG, PLUG_Y = 0.056, 0.082, 0.0080, Y0 + 0.106
# on the belt of the end ring: the indicator lamp (front top, towards the viewer) and three lock screws
BELT_X = 0.0855
LAMP_A = math.radians(145.0)
RING_SCREW_A = [math.radians(a) for a in (90.0, 210.0, 330.0)]

LOD_SPECS = [
    dict(lod=0, sides=28),
    dict(lod=1, sides=14),
]

REGIONS = {
    "alu": ("alu", 1.0), "cap": ("cap", 1.0), "ring": ("ring", 1.0), "band": ("band", 0.6),
    "sticker": ("sticker", 3.0), "plate": ("plate", 1.5), "chrome": ("chrome", 1.0), "spring": ("spring", 0.6),
    "cable": ("cable", 0.6), "boot": ("rubber", 0.6), "insert": ("black", 0.6), "stand": ("stand", 1.0),
    "pad": ("rubber", 0.6), "screw": ("screw", 0.8), "lead": ("lead", 1.5), "wire": ("wire", 0.5),
    "feet": ("rubber", 0.4), "socket": ("black", 0.5), "led": ("led", 4.0),
}

TREFOIL_DEC = (os.path.join(WORK, "decal_trefoil.png"), "z", 1, ("x", "y"), (STICKER_X, Y0),
               (STICKER_D, STICKER_D), (ZA + 0.020, ZA + 0.040))

# modules: worn at the edges, almost no rust
USED = dict(chip=(0.64, 0.70), rust=(0.99, 1.0), rust_low=0.0, floor_z=0.0, dust=0.22, grime=0.32)
METAL_UNDER = kmats.lin((150, 152, 154))       # paint chips on the aluminium of the tube

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "alu": ("steel", dict(seed=2.4, tone=0.50, along="x", gloss=0.45, spec=0.55, dust=0.25, grime=0.35)),
    "cap": ("plastic", dict(color=kmats.lin((26, 26, 26)), seed=3.1, gloss=0.14, spec=0.07, dust=0.3, grime=0.3,
                            scuff=(0.72, 0.80))),
    "ring": ("paint", dict(USED, color=kmats.lin((206, 206, 200)), under=METAL_UNDER, seed=3.7, gloss=0.4,
                           spec=0.32)),
    "band": ("paint", dict(USED, color=kmats.lin((168, 40, 30)), under=METAL_UNDER, seed=4.3, gloss=0.45,
                           spec=0.3)),
    "sticker": ("paint", dict(USED, chip=(0.74, 0.80), color=kmats.lin((232, 184, 26)), under=METAL_UNDER,
                              seed=4.9, gloss=0.5, spec=0.3, decal_items=[TREFOIL_DEC])),
    "plate": ("steel", dict(seed=5.4, tone=0.62, along="x", gloss=0.5, spec=0.55, dust=0.05, grime=0.1)),
    "chrome": ("steel", dict(seed=5.9, tone=0.56, along="x", gloss=0.75, spec=0.85, dust=0.08, grime=0.15)),
    "spring": ("steel", dict(seed=6.4, tone=0.50, along="x", gloss=0.6, spec=0.7, dust=0.1, grime=0.3)),
    "cable": ("plastic", dict(color=kmats.lin((172, 138, 94)), seed=7.0, gloss=0.3, spec=0.2, dust=0.3,
                              grime=0.5, scuff=(0.85, 0.95))),
    "stand": ("paint", dict(USED, rust=(0.82, 0.87), rust_low=0.15, color=kmats.lin((76, 82, 86)),
                            under=kmats.lin((128, 128, 130)), seed=8.3, gloss=0.35, spec=0.3)),
    "screw": ("steel", dict(seed=8.1, tone=0.45, along="x", gloss=0.55, spec=0.6, dust=0.1, grime=0.3)),
    "lead": ("plastic", dict(color=kmats.lin((112, 114, 116)), seed=8.6, gloss=0.18, spec=0.12, dust=0.1,
                             grime=0.2, scuff=(0.8, 0.9))),
    "wire": ("steel", dict(seed=9.0, tone=0.55, along="x", gloss=0.6, spec=0.6, dust=0.05, grime=0.1)),
    # indicator lamp: "off" is dark red glass, "working" is lit (the mod script makes it blink)
    "led": ("flat", dict(color=kmats.lin((78, 18, 14)), gloss=0.85, spec=0.8)),
    "led_on": ("flat", dict(color=kmats.lin((255, 70, 40)), gloss=0.85, spec=0.8)),
})

def smooth_builder(fn):
    """A kmats builder whose dust on top, streaks and decals are computed from the smoothed normal.
    kmats.Tree.normal() takes the "True Normal", the face normal: on a 28-sided cylinder the dust and
    streaks lie in stripes by face (in the preview the rubber cap shows horizontal stripes). Here, while
    the material is built, the "Normal" (smoothed; at sharp edges it equals the face normal) is used, and
    the kit is unchanged. Baking uses the same material, so the atlas matches the preview."""
    def build(mat, origin, **kw):
        keep = kmats.Tree.normal

        def normal(self):
            geo = self.node("ShaderNodeNewGeometry")
            s = self.node("ShaderNodeSeparateXYZ")
            self.link(geo.outputs["Normal"], s.inputs[0])
            return s
        kmats.Tree.normal = normal
        try:
            return fn(mat, origin, **kw)
        finally:
            kmats.Tree.normal = keep
    return build


KINDS = {k: (smooth_builder(kmats.BUILDERS[b] if isinstance(b, str) else b), prm) for k, (b, prm) in KINDS.items()}

OBJ, NAME = "m69_anom_probe", "ozr_anom_probe"
# "working" state: the lamp is the ozl_lamp selection in hiddenSelections, the _on atlas with emission
SEL_LAMP = "ozl_lamp"
ON = dict(remap={"led": "led_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL_LAMP,), hidden=(SEL_LAMP,), states={"on": ON})
P = M.part
BOUNDS = {}


# --- primitives missing from kgeo -----------------------------------------------------------------
def lathe(part, prof, n, cy=Y0, cz=ZA, a0=0.0):
    """Solid of revolution around an axis parallel to X through (cy, cz): the profile is [(x, r)] or
    [(x, r, d)]. r = 0 as the first or last point gives a flat end as a single face. d is knurling: at
    odd ring vertices the radius is smaller by d. The face normal in the (x, r) plane is (-dr, dx): a
    profile left to right faces outwards, down along the right end faces +X, up along the left end faces
    -X, going back (dx < 0) faces the axis. An edge rounding uses segments turned by no more than 30
    degrees to each other (smoothing is at 40): the edge is smooth, and a flat end gets a support ring
    so that its normals are not pulled towards the rounding."""
    bm = part.bm
    pts = list(prof)
    cap0, cap1 = pts[0][1] <= 0.0, pts[-1][1] <= 0.0
    pts = pts[1 if cap0 else 0:len(pts) - (1 if cap1 else 0)]
    rings = []
    for q in pts:
        x, r = q[0], q[1]
        d = q[2] if len(q) > 2 else 0.0
        ring = []
        for k in range(n):
            a = a0 + 2 * math.pi * k / n
            rr = r - (d if k % 2 else 0.0)
            ring.append(bm.verts.new(Vector((x, cy + rr * math.cos(a), cz + rr * math.sin(a)))))
        rings.append(ring)
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(n):
            j = (k + 1) % n
            faces.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    if cap0:
        faces.append(bm.faces.new(rings[0][::-1]))
    if cap1:
        faces.append(bm.faces.new(rings[-1]))
    return part.tag(faces)


def bend2(x0, r0, x1, r1, a1, a2):
    """Edge rounding in two segments: from (x0, r0) to (x1, r1), the first segment at angle a1 to the X
    axis, the second at a2 (degrees, the sign follows the direction of r). Returns the middle point."""
    d1 = (math.cos(math.radians(a1)), math.sin(math.radians(a1)))
    d2 = (math.cos(math.radians(a2)), math.sin(math.radians(a2)))
    bx, br = x1 - x0, r1 - r0
    det = d1[0] * d2[1] - d1[1] * d2[0]
    l1 = (bx * d2[1] - br * d2[0]) / det
    return (x0 + l1 * d1[0], r0 + l1 * d1[1])


def radial(x, a, r):
    """A local frame on the surface of radius r around the probe axis (angle a runs from +Y to +Z): u along
    the probe, n outwards; a right-handed triple (u x v = n)."""
    return g.Frame((x, Y0 + r * math.cos(a), ZA + r * math.sin(a)), (1, 0, 0),
                   (0, math.sin(a), -math.cos(a)), (0, math.cos(a), math.sin(a)))


def disc(part, x, r, n, sign, cy=Y0, cz=ZA):
    """End face: a single n-gon in an x plane, looking along sign * X."""
    bm = part.bm
    vs = [bm.verts.new(Vector((x, cy + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n))))
          for i in range(n)]
    part.tag([bm.faces.new(vs if sign > 0 else vs[::-1])])


def disc_z(part, x, y, z, r, n, a0=0.0):
    """A flat n-gon in a z plane, looking up (a hex socket)."""
    bm = part.bm
    vs = [bm.verts.new(Vector((x + r * math.cos(a0 + 2 * math.pi * i / n), y + r * math.sin(a0 + 2 * math.pi * i / n), z)))
          for i in range(n)]
    part.tag([bm.faces.new(vs)])


def arc_band(part, x0, x1, r0, r1, a0, a1, k):
    """Arc band (a ring sector r0..r1, angles a0..a1) along X from x0 to x1 - the nameplate."""
    angs = [a0 + (a1 - a0) * i / k for i in range(k + 1)]
    poly = [(Y0 + r1 * math.cos(a), ZA + r1 * math.sin(a)) for a in angs]
    poly += [(Y0 + r0 * math.cos(a), ZA + r0 * math.sin(a)) for a in reversed(angs)]
    g.prism(part, poly, (1, 2), x0, x1)


def sticker_disc(part, n):
    """Round sticker on top of the tube: three rings of vertices in plan, lifted onto the cylinder 0.3 mm
    above the tube - the chord sag (~0.1 mm) is smaller than the gap, so they do not sink in."""
    bm = part.bm
    rs = R_T + 0.0003

    def lift(x, y):
        dy = y - Y0
        return bm.verts.new(Vector((x, y, ZA + math.sqrt(rs * rs - dy * dy))))
    c = lift(STICKER_X, Y0)
    rings = []
    for rr in (STICKER_D / 6, STICKER_D / 3, STICKER_D / 2):
        rings.append([lift(STICKER_X + rr * math.cos(2 * math.pi * i / n), Y0 + rr * math.sin(2 * math.pi * i / n))
                      for i in range(n)])
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new([c, rings[0][i], rings[0][j]]))
        for a, b in zip(rings, rings[1:]):
            faces.append(bm.faces.new([a[i], b[i], b[j], a[j]]))
    part.tag(faces)


# --- supports -------------------------------------------------------------------------------------
def build_stand(spec):
    """A plate on four rubber feet and two prisms with chamfers and rubber strips; each prism has two screws
    with hex sockets."""
    lod = spec["lod"]
    parts = []
    base = P("stand_base", "stand")
    g.box(base, BASE_X0, BASE_X1, Y0 - BASE_HW, Y0 + BASE_HW, FOOT_H, BASE_Z1,
          **({"r": 0.0022, "seg": 1} if lod == 0 else {"r": 0.0015, "seg": 1}))
    parts.append(base)
    hw_top = VB_TOP - VB_APEX                       # half-width of the 45 degree notch at the top
    e = 0.0010                                      # chamfer of the notch edge
    if lod == 0:
        c = VB_CH
        prof = [(Y0 - VB_HW, BASE_Z1), (Y0 + VB_HW, BASE_Z1), (Y0 + VB_HW, VB_TOP - c), (Y0 + VB_HW - c, VB_TOP),
                (Y0 + hw_top + e, VB_TOP), (Y0 + hw_top - e * 0.7, VB_TOP - e * 0.7), (Y0, VB_APEX),
                (Y0 - hw_top + e * 0.7, VB_TOP - e * 0.7), (Y0 - hw_top - e, VB_TOP), (Y0 - VB_HW + c, VB_TOP),
                (Y0 - VB_HW, VB_TOP - c)]
    else:
        prof = [(Y0 - VB_HW, BASE_Z1), (Y0 + VB_HW, BASE_Z1), (Y0 + VB_HW, VB_TOP), (Y0 + hw_top, VB_TOP),
                (Y0, VB_APEX), (Y0 - hw_top, VB_TOP), (Y0 - VB_HW, VB_TOP)]
    # rubber strip: a chevron of thickness PAD along the notch walls (by normal), up to 3 mm from the edge
    s2 = math.sqrt(2.0)
    ep = hw_top - 0.003
    pad = [(Y0 - ep, VB_APEX + ep), (Y0, VB_APEX), (Y0 + ep, VB_APEX + ep),
           (Y0 + ep, VB_APEX + ep + PAD * s2), (Y0, VB_APEX + PAD * s2), (Y0 - ep, VB_APEX + ep + PAD * s2)]
    for i, xc in enumerate(VB_X):
        vb = P("vblock%d" % i, "stand")
        fs = g.prism(vb, prof, (1, 2), xc - VB_T / 2, xc + VB_T / 2)
        if lod == 0:
            # chamfer along the outline of both ends of the prism (the edges are finished, not sharp)
            g.bevel(vb.bm, list(fs[0].edges) + list(fs[1].edges), 0.0008, 1)
        parts.append(vb)
        pd = P("vpad%d" % i, "pad")
        g.prism(pd, pad, (1, 2), xc - VB_T / 2 + 0.001, xc + VB_T / 2 - 0.001)
        parts.append(pd)
    if lod == 0:
        sc = P("stand_screws", "screw")
        sk = P("stand_sockets", "socket")
        for xc in VB_X:
            for dx in (-0.0165, 0.0165):
                x = xc + dx
                # M5 cylindrical-head hex-socket screw: head D7.2, chamfer on top
                g.cyl(sc, (x, Y0, BASE_Z1 + 0.0015), "z", 0.0036, 0.0030, 10, r2=0.0032)
                disc_z(sk, x, Y0, BASE_Z1 + 0.00305, 0.0017, 6, a0=0.3 + dx * 20)
        parts += [sc, sk]
    ft = P("feet", "feet")
    if lod == 0:
        # round rubber feet at the corners of the plate
        for x in (BASE_X0 + 0.011, BASE_X1 - 0.011):
            for y in (Y0 - BASE_HW + 0.011, Y0 + BASE_HW - 0.011):
                g.cyl(ft, (x, y, FOOT_H / 2), "z", 0.0052, FOOT_H, 8, r2=0.0060, cap=False)
    else:
        for y in (Y0 - BASE_HW + 0.011, Y0 + BASE_HW - 0.011):
            g.box(ft, BASE_X0 + 0.006, BASE_X1 - 0.006, y - 0.006, y + 0.006, 0.0, FOOT_H)
    parts.append(ft)
    return parts


# --- probe ----------------------------------------------------------------------------------------
def cap_profile(lod):
    """Rubber cap: an end with a support ring, a rounded edge (60 and 30 degrees to the axis), a cylinder, a
    lip chamfer towards the tube."""
    rr = 0.0045
    a = (CAP_X0, R_CAP - rr)
    b = (CAP_X0 + rr, R_CAP)
    if lod > 0:
        return [(CAP_X0, 0.0), a, b, (CAP_X1 - 0.0015, R_CAP), (CAP_X1, R_T + 0.0004)]
    m = bend2(a[0], a[1], b[0], b[1], 60.0, 30.0)
    return [(CAP_X0, 0.0), (CAP_X0, R_CAP - rr - 0.0010), a, m, b, (CAP_X1 - 0.0015, R_CAP),
            (CAP_X1, R_T + 0.0004)]


def ring_profile(lod):
    """End ring: a belt, a rounded transition (30 and 60 degrees to the axis) to the end, a support ring,
    the end."""
    a = (RING_X1, R_RING)
    b = (RING_X2, R_FACE + 0.0008)
    if lod > 0:
        return [(RING_X0, R_RING), a, b, (RING_X2, 0.0)]
    m = bend2(a[0], a[1], b[0], b[1], -30.0, -60.0)
    return [(RING_X0, R_RING), a, m, b, (RING_X2, R_FACE), (RING_X2, 0.0)]


def build_probe(spec):
    """Tube, cap, mark, sticker, nameplate, end ring with screws and lamp, gland nut with a cap, seal.
    Coaxial bodies are separate parts (an atlas trap: one part gets one atlas rectangle per side, and a
    hidden end would bake over a visible one)."""
    lod, n = spec["lod"], spec["sides"]
    parts = []
    cap = P("cap", "cap")
    lathe(cap, cap_profile(lod), n)
    parts.append(cap)
    tube = P("tube", "alu")
    lathe(tube, [(TUBE_X0, R_T), (TUBE_X1, R_T)], n)
    parts.append(tube)
    band = P("band", "band")
    lathe(band, [(BAND_X - 0.0025, R_T + 0.0004), (BAND_X + 0.0025, R_T + 0.0004)], n)
    parts.append(band)
    st = P("sticker", "sticker")
    sticker_disc(st, 12 if lod == 0 else 8)
    parts.append(st)
    pl = P("plate", "plate")
    arc_band(pl, PLATE_X0, PLATE_X1, R_T - 0.0004, R_T + 0.0009, math.pi - PLATE_A, math.pi + PLATE_A,
             4 if lod == 0 else 2)
    parts.append(pl)
    ring = P("end_ring", "ring")
    lathe(ring, ring_profile(lod), n)
    parts.append(ring)
    # gland nut: a hexagon with chamfers (a solid of revolution on six faces), a flat towards the viewer
    nut = P("gland_nut", "chrome")
    lathe(nut, [(NUT_X0, R_NUT * 0.82), (NUT_X0 + 0.0008, R_NUT), (NUT_X1 - 0.0008, R_NUT),
                (NUT_X1, R_NUT * 0.82), (NUT_X1, 0.0)], 6, a0=math.pi / 6)
    parts.append(nut)
    # gland cap: a dome with a hole for the spring
    col = P("gland_collar", "chrome")
    rs = SPRING_R + SPRING_W + 0.0004
    if lod == 0:
        lathe(col, [(NUT_X1 - 0.0002, 0.0080), (NUT_X1 + 0.0020, 0.0080), (NUT_X1 + 0.0032, 0.0077),
                    (NUT_X1 + 0.0038, rs)], 16)
    else:
        lathe(col, [(NUT_X1 - 0.0002, 0.0080), (NUT_X1 + 0.0030, 0.0078), (NUT_X1 + 0.0036, rs)], 8)
    parts.append(col)
    # indicator lamp on the ring belt: a chrome mount and a lens (the ozl_lamp selection)
    fr = radial(BELT_X, LAMP_A, R_RING)
    bz = P("lamp_bezel", "chrome")
    g.cyl(bz, (0.0, 0.0, 0.0010), "z", 0.0036, 0.0030, 12 if lod == 0 else 8, r2=0.0032, frame=fr)
    parts.append(bz)
    ln = P("lamp_lens", "led", group=SEL_LAMP)
    g.cyl(ln, (0.0, 0.0, 0.0033), "z", 0.0025, 0.0018, 12 if lod == 0 else 8, r2=0.0015, frame=fr)
    parts.append(ln)
    if lod == 0:
        # ring lock screws: slotted along the probe
        rsw = P("ring_screws", "screw")
        rsl = P("ring_slots", "socket")
        for a in RING_SCREW_A:
            f2 = radial(BELT_X, a, R_RING)
            g.cyl(rsw, (0.0, 0.0, 0.0002), "z", 0.0019, 0.0010, 8, r2=0.0016, frame=f2)
            g.box(rsl, -0.0016, 0.0016, -0.00032, 0.00032, 0.00055, 0.00075, frame=f2)
        parts += [rsw, rsl]
        # nameplate rivets: round heads
        rv = P("plate_rivets", "plate")
        for x in (PLATE_X0 + 0.0035, PLATE_X1 - 0.0035):
            g.cyl(rv, (x, Y0 - R_T - 0.0012, ZA), "y", 0.0016, 0.0012, 6, r2=0.0011)
        parts.append(rv)
        # seal: two screws across the joint of the tube and the ring, a wire loop, a lead seal on it
        yz = math.sqrt(R_T * R_T - SEAL_DZ * SEAL_DZ)
        sw = P("seal_screws", "screw")
        heads = []
        for x in SEAL_X:
            g.cyl(sw, (x, Y0 - yz - 0.0008, ZA + SEAL_DZ), "y", 0.0024, 0.0016, 6)
            heads.append((x, Y0 - yz - 0.0018, ZA + SEAL_DZ))
        parts.append(sw)
        sx = (SEAL_X[0] + SEAL_X[1]) / 2
        sy, sz = Y0 - R_T - 0.0045, ZA - 0.006
        wr = P("seal_wire", "wire")
        g.pipe(wr, [heads[0], (heads[0][0] + 0.002, sy + 0.001, ZA + 0.001), (sx - 0.0012, sy, sz + 0.0045)], 0.0005, 3)
        g.pipe(wr, [heads[1], (heads[1][0] - 0.002, sy + 0.001, ZA + 0.001), (sx + 0.0012, sy, sz + 0.0045)], 0.0005, 3)
        parts.append(wr)
        sl = P("seal", "lead")
        g.cyl(sl, (sx, sy, sz), "y", 0.0050, 0.0035, 12)
        parts.append(sl)
    return parts


# --- spring, cable, connector ---------------------------------------------------------------------
def spring_curve():
    """Spring axis: from the gland along the probe, bending back and down (towards the cable on the shelf)."""
    return [(NUT_X1 + 0.001, Y0, ZA), (0.111, Y0 + 0.001, ZA - 0.001), (0.116, Y0 + 0.008, ZA - 0.006),
            (0.118, Y0 + 0.018, ZA - 0.014), (0.118, Y0 + 0.026, ZA - 0.021)]


def cable_points():
    """Cable: inside the spring, down behind the supports, a loop along the shelf at the back, the end with
    the connector at the back right."""
    cr = CABLE_R + 0.0005
    tail = [(0.117, Y0 + 0.036, 0.030), (0.114, Y0 + 0.049, 0.0135), (0.106, Y0 + 0.060, 0.0058),
            (0.092, Y0 + 0.068, cr), (0.064, Y0 + 0.075, cr), (0.022, Y0 + 0.080, cr), (-0.035, Y0 + 0.080, cr), (-0.074, Y0 + 0.084, cr),
            (-0.092, Y0 + 0.098, cr), (-0.078, Y0 + 0.113, cr), (-0.035, Y0 + 0.117, cr), (0.008, Y0 + 0.113, cr),
            (0.030, Y0 + 0.108, 0.0052), (0.046, PLUG_Y, R_PLUG)]
    return [(NUT_X0 + 0.002, Y0, ZA)] + spring_curve() + tail


def resample(pts, step):
    """Polyline -> points at equal steps of length."""
    v = [Vector(p) for p in pts]
    out, acc = [v[0]], 0.0
    for a, b in zip(v, v[1:]):
        L = (b - a).length
        s = step - acc
        while s <= L:
            out.append(a + (b - a) * (s / L))
            s += step
        acc = (acc + L) % step
    out.append(v[-1])
    return out


def thin(pts, max_deg=18.0, max_len=0.035):
    """A smooth curve -> fewer points: a point is kept when the curve has turned (the sum of the step turns)
    by more than max_deg since the last kept one, or the next one is further than max_len - sparser on
    the straight parts of the ring, denser on bends; adjacent rod segments are no more than max_deg to
    each other, below the 40 degree smoothing threshold, so no kink is visible."""
    v = [Vector(p) for p in pts]
    out, turn = [v[0]], 0.0
    for i in range(1, len(v) - 1):
        d0, d1 = v[i] - v[i - 1], v[i + 1] - v[i]
        if d0.length < 1e-9 or d1.length < 1e-9:
            continue
        turn += math.degrees(d0.angle(d1))
        if turn > max_deg or (v[i + 1] - out[-1]).length > max_len:
            out.append(v[i])
            turn = 0.0
    out.append(v[-1])
    return [tuple(q) for q in out]


def helix_pipe(part, curve, R, r, pitch, per_turn, sides):
    """Spring: wire r along a helix of radius R around the axis curve. The section is built from the radial
    direction of the turn rather than from the world axis (as in pipe()), so it does not twist."""
    bm = part.bm
    pts = resample(spline(curve, 4), pitch / per_turn)
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        a = t.cross(Vector((0, 0, 1))).normalized()
        b = t.cross(a).normalized()
        th = 2 * math.pi * i / per_turn
        nrm = a * math.cos(th) + b * math.sin(th)
        w = (-a * math.sin(th) + b * math.cos(th)) * (2 * math.pi * R / per_turn) + t * (pitch / per_turn)
        bi = w.normalized().cross(nrm).normalized()
        h = p + nrm * R
        rings.append([bm.verts.new(h + (nrm * math.cos(2 * math.pi * k / sides) + bi * math.sin(2 * math.pi * k / sides)) * r)
                      for k in range(sides)])
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            faces.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    faces += [bm.faces.new(rings[0][::-1]), bm.faces.new(rings[-1])]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    part.tag(faces)


def build_cable(spec):
    lod = spec["lod"]
    parts = []
    sp = P("spring", "spring")
    if lod == 0:
        helix_pipe(sp, spring_curve(), SPRING_R, SPRING_W, SPRING_PITCH, 10, 3)
    else:
        g.pipe(sp, spring_curve()[::2], SPRING_R + SPRING_W, 6)
    parts.append(sp)
    if lod == 0:
        # crimp sleeve at the end of the spring
        sc = spring_curve()
        end, prev = Vector(sc[-1]), Vector(sc[-2])
        t = (end - prev).normalized()
        fe = P("spring_ferrule", "chrome")
        g.pipe(fe, [tuple(end - t * 0.0045), tuple(end - t * 0.0015), tuple(end + t * 0.0015)],
               SPRING_R + SPRING_W + 0.0006, 10)
        parts.append(fe)
    pts = cable_points()
    cb = P("cable", "cable")
    if lod == 0:
        g.pipe(cb, thin(spline(pts, 6)), CABLE_R, 10)
    else:
        g.pipe(cb, pts, CABLE_R, 6)
    parts.append(cb)
    # connector (like the SR on radiometers): a ribbed rubber tail, a body, a knurled union nut, an
    # insulator in the end
    cy, cz = PLUG_Y, R_PLUG
    bt = P("plug_boot", "boot")
    if lod == 0:
        lathe(bt, [(0.0430, 0.0039), (0.0462, 0.0048), (0.0472, 0.0053), (0.0497, 0.0055), (0.0507, 0.0060),
                   (0.0560, 0.0063)], 10, cy, cz)
    else:
        lathe(bt, [(0.0430, 0.0040), (0.0560, 0.0062)], 6, cy, cz)
    parts.append(bt)
    pb = P("plug_body", "chrome")
    lathe(pb, [(0.0555, 0.0066), (0.0705, 0.0066)], 16 if lod == 0 else 6, cy, cz)
    parts.append(pb)
    nt = P("plug_nut", "chrome")
    if lod == 0:
        kn = 0.0006                                   # knurl depth (10 ribs - 20 ring vertices)
        lathe(nt, [(0.0700, 0.0066), (0.0708, R_PLUG, kn), (0.0812, R_PLUG, kn), (PLUG_X1, 0.0068),
                   (PLUG_X1 - 0.0004, 0.0068)], 20, cy, cz)
        parts.append(nt)
        ins = P("plug_insert", "insert")
        disc(ins, PLUG_X1 - 0.0004, 0.0068, 14, 1, cy, cz)
        parts.append(ins)
    else:
        lathe(nt, [(0.0700, R_PLUG), (PLUG_X1, R_PLUG), (PLUG_X1, 0.0)], 6, cy, cz)
        parts.append(nt)
    return parts


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


def build_lod(spec):
    parts = build_stand(spec) + build_probe(spec) + build_cable(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("bounds: %s .. %s" % (tuple(round(c, 4) for c in BOUNDS["lo"]), tuple(round(c, 4) for c in BOUNDS["hi"])))
    return parts


def collision():
    """One convex hull: the octagon of the probe with the gland and the support plate; the cable has no
    collision (like the M45 cord). The mass is the item weight in the mod, 0.8 kg."""
    pts = []
    for k in range(8):
        a = 2 * math.pi * (k + 0.5) / 8
        for x in (CAP_X0, NUT_X1):
            pts.append((x, Y0 + R_CAP * math.cos(a), ZA + R_CAP * math.sin(a)))
    pts += kx.box_pts(BASE_X0, BASE_X1, Y0 - BASE_HW, Y0 + BASE_HW, 0.0, BASE_Z1)
    comps = [(pts, kx.PEN + r"\metalplate.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    memory = {
        # inventory preview camera: from the front left and above (invView is where the camera is)
        "invView": [(-0.14, -0.48, 0.34)],
        "ce_center": [(0.0, 0.0, 0.045)],
        "ce_radius": [(0.14, 0.0, 0.045)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


# the first four are the --look preview (general view, the gland and connector, top, rear); the
# "working" state uses the first two: the indicator lamp is visible in both
SHOTS = [
    ("front", (-0.14, -0.50, 0.28), (0.0, -0.01, 0.045), 40),
    ("end", (0.27, -0.20, 0.16), (0.095, -0.02, 0.05), 50),
    ("top", (-0.08, -0.22, 0.44), (-0.01, 0.0, 0.04), 40),
    ("back", (0.22, 0.46, 0.28), (0.0, 0.02, 0.04), 40),
    ("cable", (0.32, 0.10, 0.12), (0.11, 0.0, 0.03), 50),
]

M.look_shots = (4, 2)
M.run(build_lod, collision, SHOTS, row_step=0.32, row_shot=((0.16, -1.1, 0.35), (0.16, 0, 0.05)))
