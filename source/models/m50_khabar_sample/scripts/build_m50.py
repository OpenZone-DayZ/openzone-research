"""M50 - Khabar sample (OZL_Sample_06, candidate class): a sample of the Khabar line shared by all
factions - a portable 1x1 item. A tin screw-top can with the lid sealed with wire.

    blender --background --python build_m50.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]
                                                  [--bake-only [--geo-render | --look-render]]

Run make_decals.py with the system Python first (the mark scratched on the lid).

Target: a screw-lid can (from tea, sweets or powder) D 7 x 8 cm, white tinplate, patchily peeled brown
paint without lettering, a small dent, wire crosswise over the lid and through a lug, a lead disc seal
without an imprint (not to be confused with the lead of the anomalous sample M48). Samples: texture 512,
no faction colour, state used but intact.

Prototype and sizes:
- body: a three-piece tinplate can (a shell with a longitudinal seam, the bottom and the top
  double-seamed). Size 211 x 304 (diameter and height in 1/16 inch): Paramount 8oz 211x304 tinplate can,
  D 2 11/16" (68.3 mm) x 3 4/16" (82.6 mm). The D 7 x 8 cm target is this class: shell D 68, double
  seams D 70.6, height with the lid 80 mm;
- a screw lid over the whole neck: a 4.4 oz can with a screw lid has a lid almost the body diameter, its
  height ~0.15 of the can height, and the neck thread shows between the lid and the body; similar tin
  screw-top cans: ADV PAX, D 87 x 87 mm, white tinplate. Here: neck D 61 with a thread, lid D 66 x 12.4
  mm, ribbing on the side, a rolled edge at the bottom, an embossed ring on the end;
- seal: a lead disc on twisted wire hangs at the device (Plombe-01 on Wikimedia Commons). Lead seals of
  D 10 mm go 240 per kg (~4.2 g, ~4.5 mm thick); here D 11 x 4.5 mm, no imprint. The sealing wire is a
  twist, here D 0.9 mm, a double twist D 1.2 at the seal;
- mass in the mod 60 g (shared with OZL_Sample_Base, unchanged: an empty 0.2 mm tinplate can is ~40 g,
  the seal 4 g); the mass in Geometry is the same.

How it is sealed: wire crosswise over the lid, the ends of each bar tucked under the lid and wound round
the neck in the gap above the seam; both ends come out through the lug - a tin strip soldered to the
body under the seam (the paint around it is burnt off) - are twisted and clamped by the seal. The lid
cannot be unscrewed without breaking the wire.

Details: the seal, a mark scratched with a knife on the lid (a circle with a diagonal cross, as on the
stalker map), the longitudinal seam of the shell with a solder strip. Wear: the brown paint has peeled
in patches and along the edges down to the tin, is rubbed by fingers on the lid ribbing, the tin rusts
in scratches and near the bottom; a dent on the side (relief in the texture) and a squashed bottom edge
(geometry).

Design decisions:
- 'dayz' look: highlight and gloss come from the profile, and so does the rvmat (a custom one would
  diverge from the game, because the preview takes the highlight from the profile); muted colour, tone
  blotches, streaks, greasy hand marks - kmats.dayz_layers at the scale of a 7 cm can; bare tin and wire
  are darker (x0.65, like bare steel in the profile).
- the can and the lid have 24 sides (kexport makes an edge sharper than 40 degrees hard: with 24 sides
  neighbours are 15 degrees apart, so the circle shades smooth and the silhouette is almost twice as
  even as with 18 and 22).
- the upper seam is a rounded bead: a crisp step below, the top is three faces with breaks under 40
  degrees (smooth shading, no chamfer rings); the lower seam is three faces, like a real double seam;
  the shoulder runs smoothly into the neck.
- lid: the upper edge is an R 1.6 rounding of three faces instead of one chamfer, the rolled edge at the
  bottom is a geometry bead, the ribbing and the end ring are relief.
- the squashed bottom edge is a smooth dent over four vertices (one vertex looked like a tooth).
- the wire is four-sided (three-sided read as a flat ribbon) and turned with an edge outwards
  (wire_tube: two faces at 45 degrees face the eye, so it reads round); it bends along the lid rounding
  and the seam bead; under the lid and round the neck (not visible) it is three-sided. The twist at the
  seal is smooth (10 sides) along a smooth curve, the turns are relief; the tails are four-sided.
- the lug is a 4 x 0.4 mm tin strip: the feet follow the body curvature, the arch R 2.4 is six chords
  (sweep); the paint is burnt down to the tin only under the lug; the area around it is scorched with an
  uneven edge, flux on the tin.
- the seal is a crimped disc: the sides flattened by jaws (nearly flat), the side rim crisp, the edge
  barrel-shaped and uneven (lead squeezed out unevenly), 16 sides; more whitish oxide on the lead.
- the lid ribbing is rubbed by fingers in patches, not on every rib.
- atlas 1024 (small item: 512-1024): at 512 the fine details - scratches, solder, the mark, the twist
  turns - would blur in game.

No vanilla proxies: the sample itself is a small item in the hands and in the inventory. No states (no
lamps or moving parts), so no work view. LODs (small item, 0.3-1.5k): near ~1.5k triangles, mid ~40 %,
no far LOD. The ribbing, the thread and the dent are relief in _nohq.

Blender axes: X is width, Y is depth (the front faces -Y), Z is up. The origin is the centre of the
bottom, the can stands.
"""
import math
import os
import sys

import bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
MM = 0.001

# --- dimensions, m ---------------------------------------------------------------------------
R_BODY = 0.0340                # shell D 68
R_SEAM = 0.0353                # double seams D 70.6
R_NECK = 0.0305                # neck D 61 with the thread
Z_LID0 = 0.0677                # lid bottom (rolled edge)
R_LID = 0.0330                 # lid D 66
Z_LWALL0, Z_LWALL1 = 0.0690, 0.0784   # ribbed side of the lid: from the bead to the edge rounding
Z_TOP = 0.0800
N_RIB = 96                     # lid ribs, ~2.2 mm pitch

# body-of-revolution profiles, mm: (r, z, region of the segment up to the next point); r = 0 is a point
# on the axis (fan). kexport makes a profile break sharper than 40 degrees a hard edge and a gentler one
# smooth: the roundings below are made of breaks of 15-39 degrees, the crisp edges (the step under the
# seam, the flash) of 45 and more.
BODY_PROF = {
    0: [(0.0, 2.2, "bottom"),                                           # the bottom is sunk into the seam
        (34.1, 0.0, "seam"), (35.3, 1.1, "seam"), (35.22, 2.45, "seam"),  # lower seam: bottom, face, top
        (34.0, 3.3, "body"),                                            # shell
        (34.0, 61.2, "seam"), (35.25, 62.3, "seam"),                    # upper seam: a step outwards,
        (35.3, 64.85, "seam"), (35.08, 65.6, "seam"),                   # face, rounded top
        (34.55, 65.98, "seam"), (33.85, 66.02, "seam"),
        (30.95, 65.2, "neck"),                                          # shoulder, smooth - then the neck
        (30.5, 68.8, "neck")],
    1: [(0.0, 2.2, "bottom"), (34.1, 0.0, "seam"), (35.3, 1.2, "seam"), (34.0, 3.3, "body"),
        (34.0, 61.2, "seam"), (35.3, 62.5, "seam"), (35.3, 64.9, "seam"), (34.6, 65.95, "seam"),
        (30.95, 65.2, "neck"), (30.5, 68.8, "neck")],
}
LID_PROF = {
    0: [(30.3, 68.5, "lid"), (33.25, 67.72, "lid"), (33.45, 68.25, "lid"),   # bottom and the rolled bead
        (33.02, 69.0, "lid"),                                                 # ribbed side
        (33.0, 78.4, "lid_top"), (32.79, 79.2, "lid_top"), (32.2, 79.79, "lid_top"),  # R 1.6 rounding
        (31.4, 80.0, "lid_top"), (0.0, 80.0, "lid_top")],                     # end
    1: [(30.3, 68.5, "lid"), (33.35, 67.8, "lid"), (33.05, 78.6, "lid_top"), (32.3, 79.75, "lid_top"),
        (31.2, 80.0, "lid_top"), (0.0, 80.0, "lid_top")],
}
LC = (31.4, 78.4, 1.6)         # lid edge rounding: centre (r, z) and radius, mm
B1 = (33.92, 68.3)             # wire at the lid bead (r, z), mm
B2 = (33.7, 67.25)             # under the bead - into the gap between the lid and the seam
Z_WRAP = 66.5                  # turns round the neck in the gap above the seam, mm

A_EAR = -70.0                  # lug and seal: front, slightly right (angle from +X counter-clockwise)
Z_EAR = 0.0555
EAR_HW = 0.0020                # 4 mm tin strip
EAR_TH = 0.0004                # tin thickness of the lug
# lug centre line, mm: (along the tangent, above the body) - the feet and an R 2.4 arch of six 30-degree
# chords (the bend at the foot is crisp, the arch itself is smooth)
EAR_PATH = [(-4.6, 0.2)] + [(2.4 * math.cos(math.radians(180 - 30 * i)), 0.2 + 2.4 * math.sin(math.radians(180 - 30 * i)))
                            for i in range(7)] + [(4.6, 0.2)]
SEAL = dict(r=0.0055, t=0.0045, z=0.0378, gap=0.00025)
WR = 0.00045                   # wire D 0.9
TWR = 0.0006                   # twist at the seal D 1.2
A_DENT, Z_DENT = -128.0, 0.030   # dent on the side (relief)
A_RIM, RIM_SIGMA = -150.0, 14.0  # squashed bottom edge (geometry): angle and width of the dent, degrees
RIM_DR = [(0.0, 2.1), (1.1, 1.8), (2.45, 1.2), (3.3, 0.5)]    # how far the edge is pressed in, mm, by height
A_SEAM = 90.0                  # longitudinal seam of the shell - at the back
MARK_A, MARK_R, MARK_D = -115.0, 0.0165, 0.017   # mark on the lid: between the wire bars at the front

# n - sides around the can and the lid; wire / hide - sides of the visible wire and of the wire hidden
# under the lid; k_corner / k_wrap - chords per edge rounding and per turn round the neck
LOD_SPECS = [
    dict(lod=0, n=24, wire=4, hide=3, k_corner=2, k_wrap=3, seal=16, twist=10, tail=4, ear=True),
    dict(lod=1, n=14, wire=3, hide=3, k_corner=2, k_wrap=2, seal=8, twist=3, tail=0, ear=False),
]

REGIONS = {
    "body": ("body", 1.0), "seam": ("seam", 1.0), "bottom": ("bottom", 0.6), "neck": ("neck", 0.8),
    "lid": ("lid", 1.3), "lid_top": ("lid_top", 1.5), "ear": ("ear", 1.6), "seal": ("seal", 1.5),
    "wire": ("wire", 0.8), "twist": ("twist", 1.0),
}

PAINT = kmats.lin((84, 56, 40))
PAINT_DARK = kmats.lin((62, 42, 31))
PAINT_FADE = kmats.lin((106, 82, 64))
TIN = kmats.lin((140, 142, 141))
TIN_DULL = kmats.lin((104, 106, 106))
TIN_STAIN = kmats.lin((134, 124, 96))     # remains of lacquer and yellowing on the tin
TIN_BRIGHT = kmats.lin((184, 186, 186))    # fresh scratch
SCORCH = kmats.lin((40, 28, 20))           # paint scorched by soldering
SOLDER = kmats.lin((118, 120, 122))
LEAD = kmats.lin((86, 89, 95))
LEAD_DARK = kmats.lin((64, 67, 73))
OXIDE = kmats.lin((168, 170, 166))


def wdecal(name):
    return os.path.join(WORK, name)


def cyl_pt(a_deg, r, z):
    a = math.radians(a_deg)
    return (r * math.cos(a), r * math.sin(a), z)


def mpt(a_deg, r_mm, z_mm):
    """cyl_pt in millimetres."""
    return cyl_pt(a_deg, r_mm * MM, z_mm * MM)


def interp(x, table):
    """Piecewise linear over [(x, y)], beyond the ends the end values."""
    if x <= table[0][0]:
        return table[0][1]
    for (x0, y0), (x1, y1) in zip(table, table[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return table[-1][1]


def metal_k():
    """Bare tin and wire are darker in the 'dayz' profile (kmats.LOOKS: steel), in v1 unchanged."""
    return kmats.LOOK.get("steel", 1.0) if kmats.LOOK["name"] == "dayz" else 1.0


def dim(c, k):
    return (c[0] * k, c[1] * k, c[2] * k, 1.0)


# --- materials: pattern at the scale of the item (a 7 cm can, not a metre-sized station) -------------
def small(t, origin, seed, k=20.0):
    vec, sep = t.coords(origin, seed)
    return t.stretch(vec, k, k, k), sep


def tri(t, x):
    """Sawtooth 0..1 -> triangle: 0 at the edges, 1 in the middle."""
    return t.math("SUBTRACT", 1.0, t.math("MULTIPLY", t.math("ABSOLUTE", t.math("SUBTRACT", x, 0.5)), 2.0))


def scratches(t, vec, amount=1.0):
    """Thin scratches: isolines of stretched noise in two directions, masked by sparse fields."""
    out = None
    for st, sc, ms in (((1.0, 1.0, 0.22), 2.6, 1.4), ((0.25, 0.25, 1.0), 2.1, 2.4)):
        n = t.noise(t.stretch(vec, *st), sc, 2.0, 0.5)
        line = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", n, 0.5)), 0.0, 0.0035, 1.0, 0.0)
        mask = t.maprange(t.noise(vec, ms, 3.0, 0.5), 0.58, 0.72, 0.0, 1.0)
        s = t.math("MULTIPLY", line, mask)
        out = s if out is None else t.math("MAXIMUM", out, s)
    return t.math("MULTIPLY", out, amount)


def dist3(t, sep, c, sz=1.0):
    """Distance to point c (stretched sz times along Z)."""
    d = [t.math("SUBTRACT", sep.outputs[i], c[i]) for i in range(3)]
    d[2] = t.math("MULTIPLY", d[2], sz)
    s = t.math("ADD", t.math("ADD", t.math("MULTIPLY", d[0], d[0]), t.math("MULTIPLY", d[1], d[1])),
               t.math("MULTIPLY", d[2], d[2]))
    return t.math("SQRT", s)


def zband(t, z, z0, z1, soft=0.0003):
    return t.math("MULTIPLY", t.maprange(z, z0 - soft, z0, 0.0, 1.0), t.maprange(z, z1, z1 + soft, 1.0, 0.0))


def dayz_grime(t, col, vec, sep, nsep, grime=0.6):
    """'dayz' profile layers (kmats.dayz_layers: muting, tone blotches, streaks, greasy hand marks) at
    the scale of the can: pattern x12 (tone blotches ~6 cm, streaks ~6 mm wide, finger marks ~3 cm).
    Returns (colour, dirt strength) - dirt kills the gloss. Outside the 'dayz' profile (v1) none of them
    are applied.
    """
    if kmats.LOOK["name"] != "dayz":
        return col, 0.0
    return kmats.dayz_layers(t, col, 0.0, t.stretch(vec, 0.6, 0.6, 0.6), sep, nsep, grime)


def mat_can(mat, origin, seed=1.0, paint=1.0, peel=0.0, ribs=False, curl=False, ring=False, mark=False,
            side_seam=False, dent=False, ear=False, thread=False, rust_low=0.3, scratch=1.0, edge_r=0.0008):
    """White tinplate under brown paint: the paint has peeled in patches and along the edges down to the
    tin (the paint edge is slightly higher and darker), scratches down to light tin, rusty specks in the
    peeled areas and scratches (more at the bottom), dirt in recesses, dust on top. paint=0 is bare tin
    (bottom, neck, lug). The flags are the relief and marks of their own region: lid ribbing and rubbed
    paint on its bead, the ring and the mark on the end, the longitudinal seam, the dent, the paint
    burnt off by soldering the lug, the neck thread.
    """
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, seed)
    nsep = t.normal()
    x, y, z = sep.outputs["X"], sep.outputs["Y"], sep.outputs["Z"]
    th = t.math("ARCTAN2", y, x)
    rr = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", x, x), t.math("MULTIPLY", y, y)))
    side = t.maprange(t.math("ABSOLUTE", nsep.outputs["Z"]), 0.5, 0.3, 0.0, 1.0)   # 1 on the side
    h = 0.0
    bias = peel                                 # addition to the paint peeling
    km = metal_k()

    # tin: dull, patches of lacquer yellowing, smudges
    tin = t.mixc(t.maprange(t.noise(vec, 1.4, 6.0, 0.6), 0.3, 0.75, 0.0, 1.0), dim(TIN_DULL, km), dim(TIN, km))
    tin = t.mixc(t.math("MULTIPLY", t.maprange(t.noise(vec, 0.8, 4.0, 0.5), 0.45, 0.75, 0.0, 1.0), 0.6),
                 tin, dim(TIN_STAIN, km))
    bright = dim(TIN_BRIGHT, 0.5 + 0.5 * km)

    if ribs:
        u = t.math("MULTIPLY", th, N_RIB / (2 * math.pi))
        rib = tri(t, t.math("FRACT", u))
        m = t.math("MULTIPLY", zband(t, z, Z_LWALL0 + 0.0002, Z_LWALL1 - 0.0002), side)
        # rubbed by fingers where the lid is gripped and turned: in patches round the circumference, not
        # on every rib
        grip = t.maprange(t.noise(vec, 1.1, 4.0, 0.6), 0.40, 0.70, 0.05, 1.0)
        crest = t.math("MULTIPLY", t.math("MULTIPLY", t.maprange(rib, 0.6, 0.95, 0.0, 1.0), m), grip)
        h = t.math("ADD", h, t.math("MULTIPLY", t.math("MULTIPLY", rib, m), 0.45))
        bias = t.math("ADD", bias, t.math("MULTIPLY", crest, 0.24))
    if curl:
        # the rolled lid bead is geometry; its paint is slightly rubbed (it is gripped)
        bias = t.math("ADD", bias, t.math("MULTIPLY", zband(t, z, Z_LID0 - 0.0002, Z_LWALL0), 0.05))
    if ring:
        rk = t.maprange(rr, 0.0215, 0.0255, 0.0, 1.0)
        h = t.math("ADD", h, t.math("MULTIPLY", tri(t, rk), 0.5))
    if side_seam:
        a = math.radians(A_SEAM)
        # distance along the tangent from the seam line (at the back, +Y)
        dt = t.math("ABSOLUTE", t.math("SUBTRACT", t.math("MULTIPLY", x, math.sin(a)),
                                       t.math("MULTIPLY", y, math.cos(a))))
        back = t.math("GREATER_THAN", t.math("ADD", t.math("MULTIPLY", x, math.cos(a)), t.math("MULTIPLY", y, math.sin(a))), 0.0)
        ridge = t.math("MULTIPLY", t.maprange(dt, 0.0013, 0.0004, 0.0, 1.0), back)
        # solder strip along the lap edge - in patches, not a solid line
        solder = t.math("MULTIPLY", t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", dt, 0.0017)), 0.00035, 0.00012, 0.0, 1.0),
                        t.math("MULTIPLY", back, t.maprange(t.noise(vec, 5.0, 4.0, 0.6), 0.40, 0.60, 0.2, 1.0)))
        h = t.math("ADD", h, t.math("MULTIPLY", ridge, 0.5))
        bias = t.math("ADD", bias, t.math("MULTIPLY", ridge, 0.14))
    dent_m = None
    if dent:
        c = cyl_pt(A_DENT, R_BODY, Z_DENT)
        d = dist3(t, sep, c, 1.3)
        sq = t.maprange(d, 0.0, 0.014, 0.0, 1.0)
        dent_m = t.math("SUBTRACT", 1.0, t.math("MULTIPLY", sq, sq))          # (1 - s^2)^2 - a smooth bowl
        dent_h = t.math("MULTIPLY", dent_m, dent_m)
        # crease across the dent
        crease = t.math("MULTIPLY", t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", z, Z_DENT + 0.0006)), 0.0009, 0.0, 0.0, 1.0),
                        t.maprange(d, 0.008, 0.003, 0.0, 1.0))
        h = t.math("SUBTRACT", h, t.math("ADD", t.math("MULTIPLY", dent_h, 3.2), t.math("MULTIPLY", crease, 0.6)))
        # the paint cracked at the bend and flaked off in small scales, not along a line
        ring = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", d, 0.0080)), 0.0040, 0.0, 0.0, 1.0)
        flakes = t.step(t.noise(vec, 16.0, 4.0, 0.6), 0.55, 0.60)
        bias = t.math("ADD", bias, t.math("MULTIPLY", t.math("MULTIPLY", ring, flakes), 0.6))
    burn = solder_m = None
    if ear:
        # the boundary of the burnt paint is uneven: the soldering iron was moved about, the flux spread
        de = t.math("ADD", dist3(t, sep, cyl_pt(A_EAR, R_BODY, Z_EAR), 1.15),
                    t.math("MULTIPLY", t.math("SUBTRACT", t.noise(vec, 9.0, 3.0, 0.6), 0.5), 0.004))
        burn = t.maprange(de, 0.0068, 0.0045, 0.0, 1.0)
        # the paint burnt down to the tin only under the staple and at the feet; around that it is
        # scorched and blistered
        bias = t.math("ADD", bias, t.math("MULTIPLY", t.maprange(de, 0.0040, 0.0030, 0.0, 1.0), 2.0))
        # solder drops at the lug feet
        sm = None
        for du in (-0.0035, 0.0035):
            a = A_EAR + math.degrees(du / R_BODY)
            ds = dist3(t, sep, cyl_pt(a, R_BODY, Z_EAR), 0.8)
            s = t.maprange(ds, 0.0024, 0.0008, 0.0, 1.0)
            sm = s if sm is None else t.math("MAXIMUM", sm, s)
        solder_m = sm
        h = t.math("ADD", h, t.math("MULTIPLY", sm, 0.6))
    if thread:
        ridge = tri(t, t.math("FRACT", t.math("DIVIDE", t.math("ADD", z, t.math("MULTIPLY", th, 0.0014 / (2 * math.pi))), 0.0014)))
        h = t.math("ADD", h, t.math("MULTIPLY", ridge, 0.45))

    edge = t.maprange(t.edge_wear(edge_r), 0.05, 0.30, 0.0, 1.0)
    low = t.maprange(z, 0.012, 0.0, 0.0, 1.0)
    if paint > 0:
        # peeled in patches of 1-3 cm (on a 7 cm can that is 'in places'), along the edges and in small
        # chips
        patch = t.noise(vec, 1.5, 6.0, 0.65)
        chips = t.noise(vec, 6.5, 6.0, 0.6)
        f = t.math("ADD", t.math("ADD", t.math("MULTIPLY", patch, 0.9), t.math("MULTIPLY", chips, 0.35)),
                   t.math("ADD", t.math("MULTIPLY", edge, 0.55), bias))
        peeled = t.step(f, 0.725, 0.74)
        rim = t.math("SUBTRACT", t.step(f, 0.69, 0.725), peeled)        # paint edge at the peeled area
        pc = t.mixc(t.maprange(t.noise(vec, 1.6, 6.0, 0.6), 0.3, 0.75, 0.0, 1.0), PAINT_DARK, PAINT)
        up = t.maprange(nsep.outputs["Z"], 0.3, 0.9, 0.0, 1.0)
        pc = t.mixc(t.math("MULTIPLY", t.maprange(t.noise(vec, 0.7, 4.0, 0.5), 0.45, 0.8, 0.0, 1.0),
                           t.math("ADD", 0.35, t.math("MULTIPLY", up, 0.3))), pc, PAINT_FADE)
        pc = t.mixc(t.math("MULTIPLY", rim, 0.35), pc, PAINT_DARK)
        col = t.mixc(peeled, pc, tin)
        cover = t.math("MULTIPLY", t.math("SUBTRACT", 1.0, peeled), paint)
        h = t.math("ADD", h, t.math("MULTIPLY", cover, 0.25))
    else:
        peeled = 1.0
        rim = 0.0
        col = tin
        cover = 0.0
    if burn is not None:
        col = t.mixc(t.math("MULTIPLY", burn, t.math("SUBTRACT", 1.0, peeled) if paint > 0 else 0.0), col, SCORCH)
        col = t.mixc(t.math("MULTIPLY", t.maprange(burn, 0.6, 1.0, 0.0, 0.85), peeled if paint > 0 else 1.0), col,
                     kmats.lin((62, 50, 34)))   # flux on the tin round the lug
        col = t.mixc(solder_m, col, SOLDER)
    if side_seam:
        col = t.mixc(t.math("MULTIPLY", solder, 0.6), col, SOLDER)
    if mark:
        a = math.radians(MARK_A)
        c, al = t.image(wdecal("decal_mark.png"), x, y, (MARK_R * math.cos(a), MARK_R * math.sin(a)), (MARK_D, MARK_D))
        mk = t.math("MULTIPLY", al, t.facing(nsep, "Z", 1, 0.5))
        col = t.mixc(t.math("MULTIPLY", mk, 0.9), col, bright)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", mk, 0.35))
        cover = t.math("MULTIPLY", cover, t.math("SUBTRACT", 1.0, mk)) if paint > 0 else cover
    scr = scratches(t, vec, scratch)
    col = t.mixc(t.math("MULTIPLY", scr, 0.5), col, bright)
    h = t.math("SUBTRACT", h, t.math("MULTIPLY", scr, 0.2))
    # rust: specks in the peeled areas and in scratches, under the paint edge, stronger at the bottom
    # and in the dent
    speck = t.step(t.noise(vec, 9.0, 6.0, 0.6), 0.56, 0.64)
    bare = peeled if paint == 0 else t.math("MAXIMUM", peeled, scr)
    ramt = t.math("MULTIPLY", speck, t.math("ADD", 0.45, t.math("MULTIPLY", low, rust_low * 2.0)))
    if dent_m is not None:
        ramt = t.math("ADD", ramt, t.math("MULTIPLY", dent_m, 0.25))
    ramt = t.math("MINIMUM", t.math("MULTIPLY", ramt, bare), 1.0)
    if paint > 0:
        under = t.math("MULTIPLY", t.maprange(rim, 0.2, 0.8, 0.0, 1.0),
                       t.maprange(t.noise(vec, 11.0, 4.0, 0.6), 0.40, 0.55, 0.0, 0.9))
        ramt = t.math("MAXIMUM", ramt, under)
    rlow = t.math("MULTIPLY", t.math("MULTIPLY", low, rust_low), t.maprange(t.noise(vec, 3.0, 6.0, 0.6), 0.4, 0.7, 0.0, 1.0))
    ramt = t.math("MAXIMUM", ramt, rlow)
    rust_col = t.ramp(t.noise(vec, 16.0, 6.0, 0.6), [(0.3, kmats.RUST[0]), (0.55, kmats.RUST[1]), (0.8, kmats.RUST[2])])
    col = t.mixc(t.math("MULTIPLY", ramt, 0.85), col, rust_col)
    h = t.math("ADD", h, t.math("MULTIPLY", ramt, 0.15))
    cav = t.maprange(t.cavity(0.005), 0.15, 0.6, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.55), col, kmats.GRIME)
    up = t.maprange(nsep.outputs["Z"], 0.4, 0.9, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", up, t.noise(vec, 3.0, 4.0, 0.6)), 0.22), col, kmats.DUST)
    col, dirt = dayz_grime(t, col, vec, sep, nsep)
    # gloss: the paint is semi-matte, the tin shines, rust and dirt are matte
    gl = t.mixf(cover, 0.52, 0.34) if paint > 0 else 0.52
    gl = t.math("SUBTRACT", t.math("ADD", gl, t.math("MULTIPLY", scr, 0.2)),
                t.math("ADD", t.math("ADD", t.math("MULTIPLY", ramt, 0.4), t.math("MULTIPLY", cav, 0.15)),
                       t.math("MULTIPLY", dirt, 0.2)))
    sp = t.mixf(cover, 0.62, 0.24) if paint > 0 else 0.62
    sp = t.math("SUBTRACT", t.math("ADD", sp, t.math("MULTIPLY", scr, 0.2)),
                t.math("ADD", t.math("MULTIPLY", ramt, 0.5), t.math("MULTIPLY", dirt, 0.2)))
    return kmats.out(t, col, gl, sp, h)


def mat_lead(mat, origin, seed=7.9):
    """Seal: dull grey-bluish lead, whitish oxide specks, flat sides pressed by smooth jaws (no
    imprint), scratches down to light metal.
    """
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, seed, 30.0)
    nsep = t.normal()
    col = t.mixc(t.maprange(t.noise(vec, 1.2, 6.0, 0.6), 0.3, 0.75, 0.0, 1.0), LEAD_DARK, LEAD)
    speck = t.maprange(t.noise(vec, 9.0, 4.0, 0.6), 0.58, 0.78, 0.0, 1.0)
    blot = t.maprange(t.noise(vec, 0.9, 6.0, 0.6), 0.50, 0.76, 0.0, 1.0)
    ox = t.math("MINIMUM", t.math("ADD", t.math("MULTIPLY", blot, 0.45), t.math("MULTIPLY", speck, 0.55)), 0.8)
    col = t.mixc(ox, col, OXIDE)
    scr = scratches(t, vec, 0.5)
    col = t.mixc(t.math("MULTIPLY", scr, 0.7), col, kmats.lin((158, 162, 170)))
    edge = t.maprange(t.edge_wear(0.0006), 0.05, 0.30, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.5), col, kmats.lin((128, 132, 140)))
    cav = t.maprange(t.cavity(0.004), 0.15, 0.6, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.5), col, kmats.GRIME)
    h = t.math("SUBTRACT", t.math("MULTIPLY", t.noise(vec, 4.0, 4.0, 0.6), 0.15), t.math("MULTIPLY", scr, 0.25))
    gl = t.math("ADD", 0.18, t.math("SUBTRACT", t.math("ADD", t.math("MULTIPLY", scr, 0.25), t.math("MULTIPLY", edge, 0.2)),
                                    t.math("MULTIPLY", ox, 0.12)))
    sp = t.math("ADD", 0.16, t.math("ADD", t.math("MULTIPLY", scr, 0.3), t.math("MULTIPLY", edge, 0.2)))
    return kmats.out(t, col, gl, sp, h)


def mat_wire(mat, origin, seed=8.4, twist=False):
    """Sealing wire: dull galvanising, rusty in places; twist is the double twist at the seal (helical
    grooves as relief).
    """
    t = kmats.Tree(mat)
    vec, sep = small(t, origin, seed, 30.0)
    km = metal_k()
    col = t.mixc(t.maprange(t.noise(vec, 2.0, 6.0, 0.6), 0.3, 0.75, 0.0, 1.0), dim(kmats.lin((96, 98, 100)), km),
                 dim(kmats.lin((150, 152, 152)), km))
    rust = t.step(t.noise(vec, 3.0, 6.0, 0.6), 0.64, 0.72)
    col = t.mixc(t.math("MULTIPLY", rust, 0.7), col, kmats.RUST[1])
    h = 0.0
    if twist:
        x, z = sep.outputs["X"], sep.outputs["Z"]
        hel = tri(t, t.math("FRACT", t.math("DIVIDE", t.math("ADD", z, t.math("MULTIPLY", x, 0.8)), 0.0011)))
        groove = t.maprange(hel, 0.0, 0.35, 1.0, 0.0)
        col = t.mixc(t.math("MULTIPLY", groove, 0.5), col, kmats.GRIME)
        h = t.math("MULTIPLY", hel, 0.5)
    gl = t.math("SUBTRACT", 0.48, t.math("MULTIPLY", rust, 0.35))
    sp = t.math("SUBTRACT", 0.55, t.math("MULTIPLY", rust, 0.45))
    return kmats.out(t, col, gl, sp, h)


KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "body": (mat_can, dict(seed=1.0, side_seam=True, dent=True, ear=True)),
    "seam": (mat_can, dict(seed=2.2, peel=-0.04, rust_low=0.6, edge_r=0.0003)),
    "bottom": (mat_can, dict(seed=3.4, paint=0.0, rust_low=0.7, scratch=0.5)),
    "neck": (mat_can, dict(seed=4.1, paint=0.0, thread=True, rust_low=0.0, scratch=0.3)),
    "lid": (mat_can, dict(seed=5.3, ribs=True, curl=True, peel=0.0, edge_r=0.0005)),
    "lid_top": (mat_can, dict(seed=6.6, ring=True, mark=True, peel=-0.02)),
    "ear": (mat_can, dict(seed=7.2, paint=0.0, rust_low=0.0, scratch=0.3)),
    "seal": (mat_lead, {}),
    "wire": (mat_wire, {}),
    "twist": (mat_wire, dict(seed=9.1, twist=True)),
})

OBJ, NAME = "m50_khabar_sample", "ozr_khabar_sample"
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz")
P = M.part
BOUNDS = {}


# --- geometry ------------------------------------------------------------------------------------
def lathe(p, prof, n, a0=0.0):
    """Body of revolution about Z: prof is [(r, z, region of the segment up to the next point)] from
    bottom to top, r = 0 is a point on the axis (fan). Faces look outward when the profile runs from the
    bottom over the side to the top. Returns the vertex rings.
    """
    bm = p.bm
    rings = []
    for r, z, _ in prof:
        if r < 1e-9:
            rings.append([bm.verts.new((0.0, 0.0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(a0 + 2 * math.pi * k / n), r * math.sin(a0 + 2 * math.pi * k / n), z))
                          for k in range(n)])
    for i in range(len(prof) - 1):
        reg = prof[i][2]
        p.use(reg, *REGIONS[reg])
        A, B = rings[i], rings[i + 1]
        faces = []
        for k in range(n):
            k1 = (k + 1) % n
            if len(A) == 1:
                faces.append(bm.faces.new([A[0], B[k1], B[k]]))
            elif len(B) == 1:
                faces.append(bm.faces.new([A[k], A[k1], B[0]]))
            else:
                faces.append(bm.faces.new([A[k], A[k1], B[k1], B[k]]))
        p.tag(faces)
    bm.normal_update()
    return rings


def radial(a_deg):
    """Local axes at angle a: u is tangent (counter-clockwise), v is up, n is outward."""
    a = math.radians(a_deg)
    return g.Frame((0, 0, 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1), (math.cos(a), math.sin(a), 0))


def mm_prof(prof):
    return [(r * MM, z * MM, reg) for r, z, reg in prof]


def build_body(spec):
    n = spec["n"]
    prof = mm_prof(BODY_PROF[spec["lod"]])
    body = P("body", "body")
    rings = lathe(body, prof, n, a0=math.pi / n)
    # squashed bottom edge: the can was dropped on its edge - the seam is pressed in and slightly
    # raised, the dent fades smoothly round the circumference (Gaussian in angle) and up the seam
    # (RIM_DR)
    for ring, (r, z, _) in zip(rings, prof):
        if r < 1e-9 or z > 0.0035:
            continue
        dr = interp(z / MM, RIM_DR) * MM
        for v in ring:
            d = (math.degrees(math.atan2(v.co.y, v.co.x)) - A_RIM + 180.0) % 360.0 - 180.0
            w = math.exp(-(d / RIM_SIGMA) ** 2)
            if w < 0.02:
                continue
            s = (r - dr * w) / r
            v.co.x *= s
            v.co.y *= s
            if z < 1e-4:
                v.co.z += 0.0006 * w
    body.bm.normal_update()
    return [body]


def build_lid(spec):
    n = spec["n"]
    lid = P("lid", "lid")
    lathe(lid, mm_prof(LID_PROF[spec["lod"]]), n, a0=math.pi / n)
    return [lid]


def build_ear(spec):
    """Lug: a 4 x 0.4 mm tin strip bent into a bracket and soldered by its feet to the body under the
    seam; the bends are smooth, the feet follow the body curvature; both wire ends pass under the
    bracket. LOD2 is a block.
    """
    p = P("ear", "ear")
    fr = radial(A_EAR)
    if not spec["ear"]:
        g.box(p, -0.0040, 0.0040, Z_EAR - EAR_HW, Z_EAR + EAR_HW, R_BODY - 0.0002, R_BODY + 0.0024, frame=fr)
        return p
    R = R_BODY / MM
    pts = [fr.p(u * MM, Z_EAR, (math.sqrt(R * R - u * u) + hh) * MM) for u, hh in EAR_PATH]
    g.sweep(p, pts, (0, 0, 1), EAR_TH / 2, EAR_HW)
    return p


def corner(a, up, k):
    """Wire over the rounding of the lid's upper edge at angle a: from the side to the end (up) or back;
    k chords, inner points on the circumscribed polygon (the wire does not cut in).
    """
    cr, cz, rad = LC
    rr = rad + WR / MM
    pts = []
    for i in range(k + 1):
        th = math.radians(90.0 * i / k)
        ri = rr if i in (0, k) else rr / math.cos(math.radians(45.0 / k))
        pts.append(mpt(a, cr + ri * math.cos(th), cz + ri * math.sin(th)))
    return pts if up else pts[::-1]


def wrap(a0, a1, k):
    """A turn round the neck in the gap under the lid from angle a0 to a1: k chords on the circumscribed
    polygon (chord midpoints touch the neck).
    """
    rv = (R_NECK / MM + WR / MM) / math.cos(math.radians(abs(a1 - a0) / k / 2))
    return [mpt(a0 + (a1 - a0) * i / k, rv, Z_WRAP) for i in range(k + 1)]


def wire_out(p):
    """Which way is 'outwards' from the can at a wire point: from the core - the cylinder r <= 31.4, z
    <= 78.4 mm (the centre of the lid edge rounding): on the side radially, on the end upwards, on the
    edge diagonally.
    """
    r = math.hypot(p.x, p.y)
    dr, dz = r - min(r, LC[0] * MM), p.z - min(p.z, LC[1] * MM)
    u = Vector((p.x / r, p.y / r, 0.0)) if r > 1e-9 else Vector((1.0, 0.0, 0.0))
    return u * dr + Vector((0.0, 0.0, dz))


def wire_tube(part, pts, rad, sides):
    """A rod like kgeo.pipe, but the section is turned with an edge outwards from the can (wire_out):
    for a four-sided wire two faces at 45 degrees face the eye and it reads round, not as a flat ribbon
    (rod faces thinner than 10 sides are always made hard by kexport). Where 'outwards' runs along the
    path (into the gap under the lid), the frame of the previous ring is used.
    """
    bm = part.bm
    pts = [Vector(q) for q in pts]
    n = len(pts)
    rings, a_prev = [], None
    for i in range(n):
        if 0 < i < n - 1:
            t = (pts[i] - pts[i - 1]).normalized() + (pts[i + 1] - pts[i]).normalized()
        else:
            t = (pts[1] - pts[0]) if i == 0 else (pts[-1] - pts[-2])
        t.normalize()
        ref = wire_out(pts[i])
        a = ref - t * ref.dot(t)
        if a.length < 0.3 * ref.length or a.length < 1e-7:
            a = (a_prev if a_prev is not None else Vector((0.0, 0.0, 1.0))).copy()
            a -= t * a.dot(t)
        a.normalize()
        a_prev = a
        b = t.cross(a).normalized()
        rings.append([bm.verts.new(pts[i] + (a * math.cos(2 * math.pi * k / sides) +
                                             b * math.sin(2 * math.pi * k / sides)) * rad) for k in range(sides)])
    new = []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            new.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    new.append(bm.faces.new(rings[0][::-1]))
    new.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def tuck(a, down):
    """At the lid bead and under it, into the gap (down) or out of the gap."""
    pts = [mpt(a, *B1), mpt(a, *B2)]
    return pts if down else pts[::-1]


def wire_pieces(spec):
    """Wire as pieces [(points, sides)]: from the twist up under the lug, over the seam bead, bar 1
    across the end, under the lid and a turn round the neck, bar 2 over the first, under the lid, a turn
    back, over the seam down under the lug to the twist. Under the lid (not visible) it is three-sided.
    Near LOD is five pieces, mid is one three-sided piece.
    """
    a, kc, kw = A_EAR, spec["k_corner"], spec["k_wrap"]
    s0, s1 = a - 1.2, a + 1.2               # two ends under the lug - side by side
    z_ear = Z_EAR / MM
    # the end converges into the twist; along the body under the lug, over the step and the seam face,
    # above its top
    down0 = [mpt(a - 0.3, 34.6, z_ear - 4.1), mpt(s0, 34.55, 60.0), mpt(s0, 35.85, 62.45), mpt(s0, 35.72, 65.95)]
    down1 = [mpt(a + 0.3, 34.6, z_ear - 4.1), mpt(s1, 34.55, 60.0), mpt(s1, 35.85, 62.45), mpt(s1, 35.72, 65.95)]
    apex = (0.0, 0.0, Z_TOP + 3 * WR)       # bar 2 - over the first
    bar1 = down0 + [mpt(a, *B1)] + corner(a, True, kc) + corner(a + 180, False, kc) + tuck(a + 180, True)
    wrap1 = wrap(a + 186, a + 264, kw)
    bar2 = tuck(a + 270, False) + corner(a + 270, True, kc) + [apex] + corner(a + 90, False, kc) + tuck(a + 90, True)
    wrap2 = wrap(a + 84, a + 6, kw)
    out = [mpt(a + 3, 33.9, 66.75)] + down1[::-1]          # out of the gap above the seam, down to the lug
    if spec["lod"] == 0:
        return [(bar1, spec["wire"]), ([bar1[-1]] + wrap1 + [bar2[0]], spec["hide"]), (bar2, spec["wire"]),
                ([bar2[-1]] + wrap2 + [out[0]], spec["hide"]), (out, spec["wire"])]
    path = [down0[0], down0[2], down0[3]] + corner(a, True, kc) + corner(a + 180, False, kc) + [bar1[-1]] + wrap1 + \
        [bar2[0]] + corner(a + 270, True, kc) + [apex] + corner(a + 90, False, kc) + [bar2[-1]] + wrap2 + \
        [out[0], down1[3], down1[2], down1[0]]
    return [(path, spec["wire"])]


def seal_disc(p, fr, c, r, t, n, lod):
    """Crimped lead seal: the sides are flattened by jaws (nearly flat, 0.12 mm dome), the side rim is
    crisp, the edge is barrel-shaped (the original lead disc) and uneven - the lead is squeezed out
    unevenly; the axis is the local n (the disc hangs flat on the can). Mid LOD is three rings.
    """
    bm = p.bm
    if lod == 0:
        prof = [(0.86, 0.5, 0.6), (0.97, 0.25, 0.9), (0.97, -0.25, 0.9), (0.86, -0.5, 0.6)]
        dome = 0.00012
    else:
        prof = [(0.80, 0.5, 0.3), (1.0, 0.0, 1.0), (0.80, -0.5, 0.3)]
        dome = 0.0
    rings = []
    for rf, hf, lw in prof:
        ring = []
        for k in range(n):
            a = 2 * math.pi * (k + 0.5) / n
            lump = 1.0 + lw * (0.035 * math.sin(3 * a + 0.7) + 0.02 * math.sin(5 * a + 2.1))
            rr = r * rf * lump
            ring.append(bm.verts.new(fr.p(c[0] + rr * math.cos(a), c[1] + rr * math.sin(a), c[2] + hf * t)))
        rings.append(ring)
    top = bm.verts.new(fr.p(c[0], c[1], c[2] + t / 2 + dome))
    bot = bm.verts.new(fr.p(c[0], c[1], c[2] - t / 2 - dome))
    faces = [bm.faces.new([top, rings[0][k], rings[0][(k + 1) % n]]) for k in range(n)]
    for A, B in zip(rings, rings[1:]):
        faces += [bm.faces.new([A[k], B[k], B[(k + 1) % n], A[(k + 1) % n]]) for k in range(n)]
    faces += [bm.faces.new([bot, rings[-1][(k + 1) % n], rings[-1][k]]) for k in range(n)]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    p.tag(faces)


def build_seal(spec):
    """Seal on the twist: both ends from the lug are twisted into one (D 1.2), threaded through the lead
    disc and crimped; two short tails stick out below.
    """
    lod = spec["lod"]
    parts = [build_ear(spec)]
    w = P("wire", "wire")
    for pts, sides in wire_pieces(spec):
        wire_tube(w, pts, WR, sides)
    rc = R_BODY + SEAL["gap"] + SEAL["t"] / 2
    zs, rs = SEAL["z"], SEAL["r"]
    if spec["tail"]:
        for da, dr, dz in ((-2.4, -0.00025, -0.0033), (2.0, 0.00045, -0.0030)):
            wire_tube(w, [cyl_pt(A_EAR + 0.4, rc, zs - rs + 0.0008), cyl_pt(A_EAR + 0.4 + da, rc + dr, zs - rs + dz)],
                      WR, spec["tail"])
    parts.append(w)
    tw = P("twist", "twist")
    z_ear = Z_EAR / MM
    tpts = [mpt(A_EAR, 34.75, z_ear - 3.5), mpt(A_EAR + 0.2, 34.95, 48.9), mpt(A_EAR + 0.5, 35.75, 45.8),
            cyl_pt(A_EAR + 0.4, rc, zs + rs - 0.0010)]
    g.pipe(tw, tpts if lod == 0 else [tpts[0], tpts[2], tpts[3]], TWR, spec["twist"])
    parts.append(tw)
    s = P("seal", "seal")
    seal_disc(s, radial(A_EAR + 0.4), (0.0, zs, rc), rs, SEAL["t"], spec["seal"], lod)
    parts.append(s)
    return parts


def build_lod(spec):
    parts = build_body(spec) + build_lid(spec) + build_seal(spec)
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """One convex octagonal prism circumscribed around the double seams (D 70.6), from the bottom to the
    lid end; the lug and the seal have no collision. The mass is the item weight in the mod, 60 g.
    """
    ro = R_SEAM / math.cos(math.pi / 8)
    ring = [(ro * math.cos(2 * math.pi * (k + 0.5) / 8), ro * math.sin(2 * math.pi * (k + 0.5) / 8)) for k in range(8)]
    pts = [(x, y, z) for x, y in ring for z in (0.0, Z_TOP)]
    comps = [(pts, kx.PEN + r"\metalplate.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    memory = {
        # inventory preview camera: front-left and above - the seal and the wire cross on the lid are
        # visible (invView is where the camera is)
        "invView": [(-0.12, -0.27, 0.22)],
        "ce_center": [(0.0, 0.0, 0.040)],
        "ce_radius": [(0.045, 0.0, 0.040)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.06, memory, bbox


# the first four are the --look previews: overview, seal close-up, lid from above, seam at the back
SHOTS = [
    ("front", (-0.13, -0.32, 0.17), (0.0, 0.0, 0.040), 60),
    ("seal", (0.06, -0.17, 0.085), (0.010, -0.030, 0.050), 70),
    ("top", (0.03, -0.14, 0.30), (0.0, 0.0, 0.075), 60),
    ("back", (0.20, 0.28, 0.13), (0.0, 0.0, 0.040), 60),
]

M.look_shots = (4, 2)
M.run(build_lod, collision, SHOTS, row_step=0.10, row_shot=((0.05, -0.30, 0.13), (0.05, 0, 0.040)))
