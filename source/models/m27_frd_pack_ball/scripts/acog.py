"""A compact prism sight of the ACOG TA31 4x32 class on a quick-release base with two thumb screws -
an own model with its own material (M27): the vanilla PO 4x34 proxy would be white in our model, and
an own shape with a vanilla texture comes out with smears. The companion of the PSO-1 at Freedom:
Soviet optics for the SVD and Western optics for STANAG magazines and 5.56 cartridges on the same
table.

Dimensions: TA31 with the TA51 base ~150 x 51 x 64 mm (5.9 x 2.0 x 2.5 inches - shop listings; 4x32,
~0.42 kg). The shape is by photos of the class: an eyepiece with a rubber ring dia. 35, the middle of the
body is a rounded square ~38 mm with knurled adjustment caps on top and on the right, an objective
bell dia. 43 with a hood, below it the body foot and a base for the rail with two cross bolts and thumb
screws on the left. The material is black anodizing rubbed to light aluminum on the edges, dust and
greasy spots; no lettering.

Axes are as in pso1.py: a - from the eyepiece to the objective, b - left (toward the thumb screws),
c - up; the tube axis is b = c = 0, mm. The geometry, placement and materials are functions of
pso1.py (the same module as in M23 and M32).
"""
import math

from mathutils import Matrix, Vector

import kgeo as g
import kmats
import pso1

LEN = 150.0
A_ADJ = 74.0                     # adjustment caps along a
C_BOT = -38.5                    # bottom of the base (support)
B_MIN, B_MAX = -25.5, 21.4       # windage cap on the right, objective bell on the left
C_TOP = 25.5
NUTS = (56.0, 100.0)             # cross bolts of the base along a
C_NUT = -30.0                    # bolt axis: a thumb screw dia. 16.8 not below the base

RING = [(14.6, 0.4), (16.6, 0.0), (17.4, 1.2), (17.4, 6.0), (16.8, 7.0)]
BODY = [(16.8, 7.0), (16.8, 24.0), (17.8, 26.0), (17.8, 98.0), (16.6, 104.0), (16.6, 110.0), (20.6, 121.0),
        (21.4, 124.5), (21.4, LEN), (19.8, LEN)]
BODY_MID = [(16.8, 0.0), (17.8, 26.0), (17.8, 98.0), (16.6, 108.0), (21.4, 124.5), (21.4, LEN), (19.8, LEN)]
A_CELL, R_IN = 136.0, 19.8
# middle of the body is a rounded square (b, c): half-width 18.6, corner radius 9; the ends are rounded (bevel)
_Q = [(9.6 + 9.0 * math.cos(math.radians(t)), 9.6 + 9.0 * math.sin(math.radians(t))) for t in (0, 45, 90)]
MID = []
for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
    q = [(sx * x, sy * y) for x, y in _Q]
    MID += q if sx * sy > 0 else q[::-1]

REGIONS = {
    "acog_body": ("acog_body", 3.0), "acog_mount": ("acog_mount", 2.6), "acog_rubber": ("acog_rubber", 2.6),
    "acog_cap_t": ("acog_cap_t", 3.5), "acog_cap_r": ("acog_cap_r", 3.5), "acog_nut": ("acog_nut", 3.0),
}


class Pose(pso1.Pose):
    """Like pso1.Pose: at - the middle of the extent along a and b, yaw - the objective angle from +X,
    z0 - the bottom of the base."""

    def __init__(self, at, yaw, z0):
        self.R = Matrix.Rotation(math.radians(yaw), 4, "Z")
        c = Vector((LEN / 2, (B_MIN + B_MAX) / 2, C_BOT))
        self.o = Vector((at[0], at[1], z0)) - (self.R @ c) * pso1.MM
        self.M = Matrix.Translation(self.o) @ self.R @ Matrix.Scale(pso1.MM, 4)

    def corners(self):
        return [self.world((a, b, c)) for a in (0.0, LEN) for b in (B_MIN, B_MAX) for c in (C_BOT, C_TOP)]


def _glass(P, name, lod):
    n = 12 if lod == 0 else 8
    out = []
    for nm, c, ax, r in ((name + "_glass_eye", (1.4, 0, 0), (-1, 0, 0), 14.4),
                         (name + "_glass_obj", (A_CELL + 0.4, 0, 0), (1, 0, 0), 17.0)):
        gl = P(nm, "pso_lens", section="glass")
        pso1._disk(gl, c, Vector(ax), r, n, 0.5)
        u, v = pso1._perp(Vector(ax))
        gl.glass_frame = (g.Frame(Vector(c), u, v, Vector(ax)), -r * pso1.MM, r * pso1.MM, -r * pso1.MM, r * pso1.MM)
        out.append(gl)
    return out


def build(P, lod, pose, name="acog"):
    """Sight parts for LOD lod at pose (P is the model's M.part)."""
    X = (1, 0, 0)
    lathe, disk = pso1.lathe, pso1._disk
    if lod >= 2:
        tb = P(name + "_body", "acog_body")
        lathe(tb, [(0.0, 0.0), (17.4, 0.0), (17.8, 100.0), (21.4, 124.5), (21.4, LEN), (0.0, LEN)], 6, (0, 0, 0), X)
        mb = P(name + "_mount", "acog_mount")
        pso1.box(mb, 40.0, 116.0, -12.5, 12.5, C_BOT, -17.0)
        parts = [tb, mb]
    elif lod == 1:
        rg = P(name + "_ring", "acog_rubber")
        lathe(rg, [RING[0], RING[2], RING[3], RING[4]], 8, (0, 0, 0), X)
        tb = P(name + "_body", "acog_body")
        lathe(tb, BODY_MID, 8, (0, 0, 0), X)
        hi = P(name + "_hood_in", "pso_in")
        lathe(hi, [(R_IN, LEN), (R_IN, A_CELL)], 8, (0, 0, 0), X)
        ln = P(name + "_lenses", "pso_lens")
        disk(ln, (A_CELL, 0, 0), Vector(X), R_IN, 8, 0.5)
        disk(ln, (2.2, 0, 0), Vector((-1, 0, 0)), 14.8, 8, 0.5)
        md = P(name + "_mid", "acog_body")
        g.prism(md, [(b, c) for b, c in MID[1::3]], (1, 2), 52.0, 96.0)
        ct = P(name + "_cap_t", "acog_cap_t")
        lathe(ct, [(9.6, 14.0), (9.6, 25.5), (0.0, 25.5)], 8, (A_ADJ, 0, 0), (0, 0, 1))
        cr = P(name + "_cap_r", "acog_cap_r")
        lathe(cr, [(9.6, 14.0), (9.6, 25.5), (0.0, 25.5)], 8, (A_ADJ, 0, 0), (0, -1, 0))
        mb = P(name + "_mount", "acog_mount")
        pso1.box(mb, 56.0, 100.0, -10.0, 10.0, -24.0, -16.0)
        pso1.box(mb, 36.0, 120.0, -12.5, 12.5, C_BOT, -24.0)
        parts = [rg, tb, hi, ln] + _glass(P, name, 1) + [md, ct, cr, mb]
    else:
        # rubber ring of the eyepiece, the eyepiece lens in it
        rg = P(name + "_ring", "acog_rubber")
        lathe(rg, RING, 12, (0, 0, 0), X)
        tb = P(name + "_body", "acog_body")
        lathe(tb, BODY, 12, (0, 0, 0), X)
        hi = P(name + "_hood_in", "pso_in")
        lathe(hi, [(R_IN, LEN), (R_IN, A_CELL)], 12, (0, 0, 0), X)
        ln = P(name + "_lenses", "pso_lens")
        disk(ln, (A_CELL, 0, 0), Vector(X), R_IN, 12, 0.5)
        disk(ln, (2.2, 0, 0), Vector((-1, 0, 0)), 14.8, 12, 0.5)
        # middle of the body as a rounded square, adjustment caps on top and on the right (knurled)
        md = P(name + "_mid", "acog_body")
        g.prism(md, MID, (1, 2), 52.0, 96.0)
        ends = [e for f in md.bm.faces if abs(f.normal.x) > 0.9 for e in f.edges]
        g.bevel(md.bm, ends, 3.0, 2)
        ct = P(name + "_cap_t", "acog_cap_t")
        lathe(ct, [(9.6, 14.0), (9.6, 24.7), (8.8, 25.5), (0.0, 25.5)], 10, (A_ADJ, 0, 0), (0, 0, 1))
        cr = P(name + "_cap_r", "acog_cap_r")
        lathe(cr, [(9.6, 14.0), (9.6, 24.7), (8.8, 25.5), (0.0, 25.5)], 10, (A_ADJ, 0, 0), (0, -1, 0))
        # body foot and the rail base (bevelled ends seen from the side)
        ft = P(name + "_foot", "acog_mount")
        pso1.box(ft, 56.0, 100.0, -10.0, 10.0, -24.0, -16.0)
        mb = P(name + "_mount", "acog_mount")
        g.prism(mb, [(40.0, C_BOT), (116.0, C_BOT), (120.0, -34.5), (120.0, -28.0), (116.0, -24.0), (40.0, -24.0),
                     (36.0, -28.0), (36.0, -34.5)], (0, 2), -12.5, 12.5)
        # thumb screws of the cross bolts on the left, bolt ends on the right
        nt = P(name + "_nuts", "acog_nut")
        for a in NUTS:
            lathe(nt, [(8.4, 0.0), (8.4, 6.0), (7.6, 7.0), (0.0, 7.0)], 8, (a, 12.5, C_NUT), (0, 1, 0), 0.0)
            disk(nt, (a, -12.9, C_NUT), Vector((0, -1, 0)), 3.4, 6, 0.0)
        parts = [rg, tb, hi, ln] + _glass(P, name, 0) + [md, ct, cr, ft, mb, nt]
    pso1.place(parts, pose)
    for gl in parts:
        if gl.section == "glass":
            fr, a0, a1, b0, b1 = gl.glass_frame
            u, v, n = (pose.dir(x) for x in (fr.u, fr.v, fr.n))
            gl.glass_frame = (g.Frame(pose.world(fr.o), u, v, n), a0, a1, b0, b1)
    return parts


def kinds(pose, floor_z=0.0, wear=1.0):
    """Materials (pso1.build_*): black anodizing rubbed to light aluminum, rubber, knurling of the caps."""
    lin = kmats.lin
    ct = pose.world((A_ADJ, 0.0, 0.0))
    cr = pose.world((A_ADJ, 0.0, 0.0))
    ex, ey, ez = pose.dir((1, 0, 0)), pose.dir((0, 1, 0)), Vector((0.0, 0.0, 1.0))
    rub = [(pose.world((10.0, 0.0, 0.0)), 0.022, 0.2 * wear), (pose.world((A_ADJ, -14.0, 14.0)), 0.02, 0.22 * wear),
           (pose.world((NUTS[0], 16.0, C_NUT)), 0.015, 0.2 * wear)]
    anod = dict(color=lin((24, 24, 26)), bare=lin((176, 176, 172)), primer=lin((58, 58, 58)), gloss=0.27, spec=0.25,
                crinkle=0.06, oil=0.2)
    return {
        "acog_body": (pso1.build_enamel, dict(anod, seed=41.3, wear=(0.67 - 0.04 * wear, 0.71 - 0.04 * wear), edge_k=1.05,
                                              rub=rub, floor_z=floor_z)),
        "acog_mount": (pso1.build_enamel, dict(anod, seed=42.1, wear=(0.64 - 0.04 * wear, 0.69 - 0.04 * wear), edge_k=1.1,
                                               floor_z=floor_z, grime=0.45)),
        "acog_rubber": (pso1.build_rubber, dict(color=lin((26, 26, 26)), seed=42.9, floor_z=floor_z, dust=0.12, grime=0.2)),
        "acog_cap_t": (pso1.build_knurl, dict(color=lin((26, 26, 28)), bare=lin((150, 150, 148)), seed=43.7,
                                              center=tuple(ct), e1=tuple(ex), e2=tuple(ey), axis=tuple(ez), n=40,
                                              floor_z=floor_z)),
        "acog_cap_r": (pso1.build_knurl, dict(color=lin((26, 26, 28)), bare=lin((150, 150, 148)), seed=44.3,
                                              center=tuple(cr), e1=tuple(ex), e2=tuple(ez), axis=tuple(ey), n=40,
                                              floor_z=floor_z)),
        "acog_nut": (pso1.build_metal, dict(color=lin((40, 40, 42)), seed=44.9, gloss=0.4, spec=0.45, floor_z=floor_z,
                                            grime=0.4)),
    }
