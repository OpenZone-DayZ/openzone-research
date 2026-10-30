"""PSO-1 - an own optical scope with its own material: a module shared by M23, M32 and M27.

Why own: in our model the DayZ scope proxies render white, without a texture, and an own
shape wearing the vanilla texture came out with stretched streaks. So both the shape and a
procedural material (kmats, like the other parts) are our own: black shagreen enamel worn
to metal on the edges, the rubber of the eyecup, an aluminium handwheel scale with ticks,
blued fasteners, lenses as a glass section. No vanilla textures or foreign geometry; no
lettering (only the scale ticks).

Dimensions: Wikipedia "PSO-1": 4x24, length 337 mm without the eyecup and hood, 375 mm
with them, width 70-72, mass 0.6 kg; the bracket on the left is a dovetail mount of the
weapon (grooves, a stop, a clamp screw with a lever), the elevation handwheel (1-10) on
top, the windage one on the right (AWM REL29835.002: "horizontal turret on the right
side"), a rubber eyecup, a hood. The shape and proportions of the parts follow photos: AWM
REL29835.002 (right side), Wikimedia Commons "SVD rifle detail.jpg" (right side on an SVD)
and "Tigr pso 1 med.jpg" (left side with the bracket). The height from the base bottom to
the handwheel is ~0.5 of the length in all photos (~170 mm; the 132-136 mm of reference
books apparently leaves out the bracket base) - taken from the photos.

Layout (scope axes: a - along the axis from the eyecup to the objective, b - left, toward
the bracket, c - up; 0 along a is the rear edge of the eyecup, the tube axis is b = c = 0;
mm):
- eyecup 0-35 (flare dia 62, neck, bead), eyepiece - a bell dia 45 with a groove, a cone to
  the tube dia 26, body dia 46 (151-245) with a belt at the rear, the objective tube dia 40
  and hood dia 42 in front of it up to 375; the lenses are recessed in their cells (the
  eyepiece deep in the eyecup, the objective 23 mm inside the hood);
- on the body: the elevation handwheel on top (a square base, an aluminium scale with ticks,
  a knurled cap), the windage handwheel on the right (a flange on four screws, a flat drum
  with three holes and a screw), the backlight bulb socket on the top left;
- the bracket on the left: a plate with a foot on four screws to the body, two posts, a
  140 mm base with a dovetail groove, a clamp screw lever with a nut on the base, the
  backlight switch box with a rotary disc on the front post, the battery bay (a tube with a
  knurled cap facing back) under the eyepiece through the rear post.

The scope stands on the bracket base (the base bottom on the support), as on a gunsmith's
table. The position is a Pose: the middle of the extent along a and b above a table point,
the objective turned from Blender +X. Triangles: near LOD 1584, middle 484, far - the tube
and the base (60).

    import pso1
    POSE = pso1.Pose((x, y), yaw, z_bottom)
    REGIONS.update(pso1.REGIONS); KINDS.update(pso1.kinds(POSE, floor_z))
    kmodel.Model(..., glass=pso1.GLASS)           # lens glass - the glass section of the model
    parts += pso1.build(M.part, lod, POSE)

Blender axes: X - width, Y - depth (front at -Y), Z - up.
"""
import math

import bmesh
from mathutils import Matrix, Vector

import kgeo as g
import kmats

MM = 0.001

# --- Dimensions, mm (scope axes: a, b, c) -----------------------------------------------------
LEN = 375.0
A_T = 196.0                      # handwheels (top and right) along a
A_L, C_L = 224.0, 13.0           # backlight bulb socket: along a, axis height
BASE = (150.0, 290.0)            # bracket base along a
C_BOT = -126.0                   # bottom of the base (the support)
B_MIN, B_MAX = -28.9, 39.3       # extent along b: windage drum right, switch disc left
BAT = (14.0, -40.0)              # battery bay axis (b, c)

# Eyecup: outside (rear end, flare rim, flare, neck, bead, sleeve on the eyepiece) and inside
EC_OUT = [(28.6, 0.5), (31.0, 1.0), (29.8, 3.0), (24.0, 8.0), (22.8, 12.5), (23.6, 16.0), (23.2, 33.0), (22.3, 34.6)]
EC_IN = [(15.2, 14.0), (17.0, 9.0), (28.6, 0.5)]
# Tube: eyepiece bell with a groove, cone, tube with a coupling, body with a belt, coupling,
# objective tube, hood (the end is a ring down to the inner wall)
TUBE = [(22.3, 34.0), (22.3, 44.5), (21.8, 45.5), (21.9, 68.0), (20.6, 77.0), (16.0, 89.0), (13.2, 100.0),
        (13.2, 143.5), (14.8, 144.5), (14.8, 150.5), (19.6, 152.0), (22.6, 155.0), (23.0, 158.0), (23.8, 159.0),
        (23.8, 171.0), (23.0, 172.0), (23.0, 237.0), (20.6, 244.5), (21.3, 245.5), (21.3, 252.0), (20.2, 253.0),
        (20.2, 299.0), (21.2, 300.0), (21.2, 375.0), (19.8, 375.0)]
TUBE_MID = [(22.3, 34.0), (21.9, 68.0), (18.4, 83.0), (13.2, 100.0), (13.2, 150.5), (21.5, 153.5), (23.0, 158.0),
            (23.0, 237.0), (20.2, 245.0), (20.2, 299.0), (21.2, 300.0), (21.2, 375.0), (19.8, 375.0)]
TUBE_FAR = [(21.0, 30.0), (22.5, 150.0), (22.5, 240.0), (21.2, 375.0)]
R_IN, A_CELL = 19.8, 352.0       # hood inside, objective cell

# rounded square (handwheel base, windage flange): half-width 16, corner radius 5
_SQ = [(16.0 - 5.0 + 5.0 * math.cos(math.radians(a)), 16.0 - 5.0 + 5.0 * math.sin(math.radians(a))) for a in (0, 45, 90)]
SQUARE = []
for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
    pts = [(sx * x, sy * y) for x, y in _SQ]
    SQUARE += pts if sx * sy > 0 else pts[::-1]
SQUARE_MID = [(16.0, 16.0), (-16.0, 16.0), (-16.0, -16.0), (16.0, -16.0)]

REGIONS = {
    "pso_body": ("pso_enamel", 2.6), "pso_mount": ("pso_mount", 2.2), "pso_rubber": ("pso_rubber", 2.4),
    "pso_rubber_in": ("pso_rubber", 1.2), "pso_in": ("pso_black", 0.8), "pso_black": ("pso_black", 2.0),
    "pso_scale": ("pso_scale", 4.0), "pso_alu": ("pso_alu", 3.0), "pso_knurl": ("pso_knurl", 3.0),
    "pso_knurl_b": ("pso_knurl_b", 3.0), "pso_steel": ("pso_steel", 3.0), "pso_lens": ("pso_lens", 2.0),
}
# lens glass (kexport.glass_ca): bluish-violet coating, nearly clear, smudged
GLASS = dict(base=(0.30, 0.34, 0.46), clear=0.16, edge=0.06, smudge=0.10, streaks=0.0)


class Pose:
    """Scope pose: at - (x, y) of the center of the extent along a and b, yaw - the angle of axis
    a (toward the objective) from Blender +X, degrees (180 - objective toward -x, bracket
    toward the player, -y); z0 - height of the base bottom.
    """

    def __init__(self, at, yaw, z0):
        self.R = Matrix.Rotation(math.radians(yaw), 4, "Z")
        c = Vector((LEN / 2, (B_MIN + B_MAX) / 2, C_BOT))
        self.o = Vector((at[0], at[1], z0)) - (self.R @ c) * MM
        self.M = Matrix.Translation(self.o) @ self.R @ Matrix.Scale(MM, 4)

    def world(self, p):
        """Scope point (mm) -> Blender (m)."""
        return self.M @ Vector(p)

    def dir(self, d):
        return (self.R @ Vector(d)).normalized()

    def corners(self):
        """Corners of the extent in Blender - to check the neighbors."""
        return [self.world((a, b, c)) for a in (0.0, LEN) for b in (B_MIN, B_MAX) for c in (C_BOT, 44.0)]


# =============================================================================
# Geometry (in scope axes, mm; build moves it to Blender)
# =============================================================================
def _perp(axis):
    a = Vector(axis).normalized()
    r = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    u = r.cross(a).normalized()
    return u, a.cross(u).normalized()


def lathe(part, prof, sides, origin, axis=(1, 0, 0), phase=0.5):
    """Solid of revolution around the axis through origin: prof [(r, h)], h along the axis. A
    ring with r = 0 is a pole. Faces look outward along the profile direction (the reverse
    direction - inward, toward the axis; moving outward at constant h - against the axis).
    """
    bm = part.bm
    a = Vector(axis).normalized()
    u, v = _perp(a)
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
    part.tag(new)
    return new


def _disk(part, center, a, r, sides, phase):
    """Flat disc facing along axis a."""
    u, v = _perp(a)
    c = Vector(center)
    vs = [part.bm.verts.new(c + (u * math.cos(2 * math.pi * (k + phase) / sides) +
                                 v * math.sin(2 * math.pi * (k + phase) / sides)) * r) for k in range(sides)]
    f = part.bm.faces.new(vs)
    f.normal_update()
    if f.normal.dot(a) < 0:
        f.normal_flip()
    part.tag([f])
    return [f]


def box(part, a0, a1, b0, b1, c0, c1, r=0.0):
    return g.box(part, a0, a1, b0, b1, c0, c1, r=r, seg=1 if r > 0 else 0)


SHARP_DEG = 40.0                 # as in kexport.visual_lod: sharper - an edge, softer - smoothed


def place(parts, pose):
    """Parts from scope axes (mm) to Blender: rotation and translation (determinant +1 - the same
    normals). Faces are smoothed, edges sharper than 40 degrees stay sharp, as in the game LODs
    (kexport): baking (kbake bakes the objects as they are) and the preview take the same
    normal, so dust and wear do not lie in stripes across the faces of round parts.
    """
    cos_sharp = math.cos(math.radians(SHARP_DEG))
    for p in parts:
        bm = p.bm
        bmesh.ops.transform(bm, matrix=pose.M, verts=bm.verts[:])
        bm.normal_update()
        for f in bm.faces:
            f.smooth = True
        for e in bm.edges:
            lf = e.link_faces
            e.smooth = len(lf) == 2 and lf[0].normal.dot(lf[1].normal) > cos_sharp
    return parts


def build(P, lod, pose, name="pso"):
    """Scope parts for LOD lod (0 - near) at pose. P is the model's M.part."""
    parts = _build_far(P, name) if lod >= 2 else (_build_mid(P, name) if lod == 1 else _build_near(P, name))
    place(parts, pose)
    # glass UV frame (kuv: flat 0..1 by Part.glass_frame) - in scope axes; in Blender after the move
    for gl in parts:
        if gl.section == "glass":
            fr, a0, a1, b0, b1 = gl.glass_frame
            u, v, n = (pose.dir(x) for x in (fr.u, fr.v, fr.n))
            gl.glass_frame = (g.Frame(pose.world(fr.o), u, v, n), a0, a1, b0, b1)
    return parts


def _glass(P, name, lod):
    """Eyepiece and objective glass (in scope axes before the move; build recomputes the frame)."""
    n = 12 if lod == 0 else 8
    out = []
    for nm, c, ax, r in ((name + "_glass_eye", (13.4, 0, 0), (-1, 0, 0), 11.6),
                         (name + "_glass_obj", (A_CELL + 0.4, 0, 0), (1, 0, 0), 13.6)):
        gl = P(nm, "pso_lens", section="glass")
        _disk(gl, c, Vector(ax), r, n, 0.5)
        u, v = _perp(Vector(ax))
        gl.glass_frame = (g.Frame(Vector(c), u, v, Vector(ax)), -r * MM, r * MM, -r * MM, r * MM)
        out.append(gl)
    return out


def _xprism(part, outline, b0, b1):
    """Plate by an outline from the side (a, c), thick along b from b0 to b1."""
    return g.prism(part, outline, (0, 2), b0, b1)


def _build_near(P, name):
    X = (1, 0, 0)
    parts = []
    # --- Eyecup (rubber): rear end, flare, neck, bead, sleeve; inside - to the eyepiece cell
    ec = P(name + "_eyecup", "pso_rubber")
    lathe(ec, EC_OUT, 14, (0, 0, 0), X)
    ei = P(name + "_eyecup_in", "pso_rubber_in")
    lathe(ei, EC_IN, 14, (0, 0, 0), X)
    parts += [ec, ei]
    # --- Tube (enamel)
    tb = P(name + "_tube", "pso_body")
    lathe(tb, TUBE, 12, (0, 0, 0), X)
    parts.append(tb)
    # hood inside (its own region - otherwise it shares texels with the outer wall); the lenses
    # with their cells are dark discs (the coated glass shines through the glass section on top)
    hi = P(name + "_hood_in", "pso_in")
    lathe(hi, [(R_IN, LEN), (R_IN, A_CELL)], 12, (0, 0, 0), X)
    ln = P(name + "_lenses", "pso_lens")
    _disk(ln, (A_CELL, 0, 0), Vector(X), R_IN, 12, 0.5)
    _disk(ln, (14.0, 0, 0), Vector((-1, 0, 0)), 15.2, 12, 0.5)
    parts += [hi, ln] + _glass(P, name, 0)
    # --- Elevation handwheel: base, scale (aluminium, ticks), knurled cap
    tp = P(name + "_turret_base", "pso_body")
    g.prism(tp, [(A_T + x, y) for x, y in SQUARE], (0, 1), 16.0, 27.0)
    tr = P(name + "_turret_scale", "pso_scale")
    lathe(tr, [(15.0, 26.5), (15.0, 34.0)], 12, (A_T, 0, 0), (0, 0, 1))
    tc = P(name + "_turret_cap", "pso_knurl")
    lathe(tc, [(16.0, 34.0), (16.0, 41.8), (15.0, 42.6), (0.0, 42.6)], 12, (A_T, 0, 0), (0, 0, 1))
    parts += [tp, tr, tc]
    # --- Windage handwheel on the right: flange, a flat drum with three holes
    wf = P(name + "_wind_flange", "pso_body")
    g.prism(wf, [(A_T + x, z) for x, z in SQUARE], (0, 2), -25.5, -15.0)
    wd = P(name + "_wind_drum", "pso_alu")
    lathe(wd, [(14.0, 0.0), (14.0, 2.6), (13.0, 3.4), (0.0, 3.4)], 12, (A_T, -25.5, 0), (0, -1, 0))
    wh = P(name + "_wind_holes", "pso_black")
    for k in range(3):
        a = math.radians(90 + 120 * k)
        _disk(wh, (A_T + 8.0 * math.cos(a), -29.0, 8.0 * math.sin(a)), Vector((0, -1, 0)), 1.6, 6, 0.0)
    parts += [wf, wd, wh]
    # --- Backlight bulb socket (top left, toward the objective from the handwheel), rounded end
    lp = P(name + "_lamp", "pso_body")
    lathe(lp, [(7.0, 12.0), (7.0, 22.5), (6.0, 24.2), (0.0, 24.6)], 10, (A_L, 0, C_L), (0, 1, 0))
    parts.append(lp)
    # --- Bracket (enamel, worn more): a foot to the body, a plate, posts (wider at the top), a
    # base with a dovetail groove
    mp = P(name + "_mount_plate", "pso_mount")
    _xprism(mp, [(184.0, -21.0), (208.0, -21.0), (208.0, 2.0), (205.0, 5.0), (187.0, 5.0), (184.0, 2.0)], 20.5, 25.0)
    mb = P(name + "_mount_bar", "pso_mount")
    _xprism(mb, [(156.0, -26.0), (160.0, -30.0), (280.0, -30.0), (284.0, -26.0), (284.0, -22.0), (156.0, -22.0)],
            11.0, 26.0)
    ar = P(name + "_mount_arm_r", "pso_mount")
    _xprism(ar, [(158.0, -29.5), (181.0, -29.5), (181.0, -38.0), (177.0, -50.0), (177.0, -96.5), (161.0, -96.5),
                 (161.0, -50.0), (158.0, -40.0)], 17.0, 26.0)
    af = P(name + "_mount_arm_f", "pso_mount")
    _xprism(af, [(262.0, -29.5), (283.0, -29.5), (283.0, -40.0), (280.0, -50.0), (280.0, -96.5), (265.0, -96.5),
                 (265.0, -50.0), (262.0, -38.0)], 17.0, 26.0)
    bs = P(name + "_mount_base", "pso_mount")
    prof = [(34.0, -126.0), (34.0, -98.5), (31.5, -96.0), (8.0, -96.0), (5.0, -99.0), (5.0, -104.0), (11.0, -108.0),
            (11.0, -113.0), (2.0, -117.0), (2.0, -126.0)]
    g.prism(bs, prof, (1, 2), BASE[0], BASE[1])
    parts += [mp, mb, ar, af, bs]
    # backlight switch box on the front post, a rotary disc with holes facing back
    sb = P(name + "_switch_box", "pso_mount")
    box(sb, 258.0, 284.0, 26.0, 37.0, -84.0, -48.0, r=1.2)
    sd = P(name + "_switch_disk", "pso_steel")
    lathe(sd, [(7.5, 0.0), (7.5, 2.0), (0.0, 2.0)], 8, (258.0, 31.5, -62.0), (-1, 0, 0))
    sh = P(name + "_switch_holes", "pso_black")
    for k in range(3):
        a = math.radians(30 + 120 * k)
        _disk(sh, (255.9, 31.5 + 4.2 * math.cos(a), -62.0 + 4.2 * math.sin(a)), Vector((-1, 0, 0)), 1.3, 6, 0.0)
    parts += [sb, sd, sh]
    # battery bay: a knurled cap facing back, a tube through the rear post
    bk = P(name + "_battery_cap", "pso_knurl_b")
    lathe(bk, [(0.0, 0.0), (6.4, 0.0), (9.0, 1.4), (9.0, 15.0), (8.2, 16.0)], 8, (112.0, BAT[0], BAT[1]), X)
    bt = P(name + "_battery", "pso_mount")
    lathe(bt, [(8.2, 16.0), (8.2, 69.0), (6.4, 71.5), (0.0, 72.2)], 8, (112.0, BAT[0], BAT[1]), X)
    parts += [bk, bt]
    # clamp screw lever on the base, the screw nut and stud (blued steel)
    st = P(name + "_steel", "pso_steel")
    g.prism(st, [(204.0, 17.5), (215.0, 17.0), (250.0, 24.0), (253.0, 28.0), (249.0, 31.0), (206.0, 25.5)], (0, 1),
            -96.0, -92.8)
    lathe(st, [(5.2, 0.0), (5.2, 4.8), (0.0, 4.8)], 6, (211.0, 21.5, -96.0), (0, 0, 1), 0.0)
    parts.append(st)
    # screw heads (a hexagon 0.4 mm above the part): windage flange on the right, drum screw,
    # foot on the left
    sc = P(name + "_screws", "pso_steel")
    for da in (-11.5, 11.5):
        for dc in (-11.5, 11.5):
            _disk(sc, (A_T + da, -25.9, dc), Vector((0, -1, 0)), 2.2, 6, 0.0)
    _disk(sc, (A_T, -29.3, 0.0), Vector((0, -1, 0)), 2.6, 6, 0.0)
    for da in (-6.5, 6.5):
        for dc in (-15.0, -1.0):
            _disk(sc, (A_T + da, 25.4, dc), Vector((0, 1, 0)), 2.2, 6, 0.0)
    for a, b, c in ((165.0, 34.4, -111.0), (275.0, 34.4, -111.0), (169.0, 26.4, -88.0), (272.5, 26.4, -90.0)):
        _disk(sc, (a, b, c), Vector((0, 1, 0)), 2.4, 6, 0.0)                 # base and posts, outside
    parts.append(sc)
    return parts


def _build_mid(P, name):
    X = (1, 0, 0)
    ec = P(name + "_eyecup", "pso_rubber")
    lathe(ec, [EC_OUT[0], EC_OUT[1], EC_OUT[3], EC_OUT[4], EC_OUT[6], EC_OUT[7]], 8, (0, 0, 0), X)
    ei = P(name + "_eyecup_in", "pso_rubber_in")
    lathe(ei, [EC_IN[0], EC_IN[2]], 8, (0, 0, 0), X)
    tb = P(name + "_tube", "pso_body")
    lathe(tb, TUBE_MID, 8, (0, 0, 0), X)
    hi = P(name + "_hood_in", "pso_in")
    lathe(hi, [(R_IN, LEN), (R_IN, A_CELL)], 8, (0, 0, 0), X)
    ln = P(name + "_lenses", "pso_lens")
    _disk(ln, (A_CELL, 0, 0), Vector(X), R_IN, 8, 0.5)
    _disk(ln, (14.0, 0, 0), Vector((-1, 0, 0)), 15.2, 8, 0.5)
    tp = P(name + "_turret_base", "pso_body")
    g.prism(tp, [(A_T + x, y) for x, y in SQUARE_MID], (0, 1), 16.0, 27.0)
    tc = P(name + "_turret_cap", "pso_knurl")
    lathe(tc, [(15.5, 26.5), (15.5, 42.6), (0.0, 42.6)], 8, (A_T, 0, 0), (0, 0, 1))
    wf = P(name + "_wind_flange", "pso_body")
    g.prism(wf, [(A_T + x, z) for x, z in SQUARE_MID], (0, 2), -25.5, -15.0)
    wd = P(name + "_wind_drum", "pso_alu")
    lathe(wd, [(14.0, 0.0), (14.0, 3.4), (0.0, 3.4)], 8, (A_T, -25.5, 0), (0, -1, 0))
    mb = P(name + "_mount", "pso_mount")
    box(mb, 156.0, 284.0, 11.0, 26.0, -30.0, -22.0)
    box(mb, 160.0, 177.0, 17.0, 26.0, -96.5, -29.5)
    box(mb, 264.0, 281.0, 17.0, 26.0, -96.5, -29.5)
    box(mb, BASE[0], BASE[1], 2.0, 34.0, C_BOT, -96.0)
    box(mb, 258.0, 284.0, 26.0, 37.0, -84.0, -48.0)
    bt = P(name + "_battery", "pso_mount")
    lathe(bt, [(0.0, 0.0), (9.0, 0.0), (8.2, 72.0), (0.0, 72.0)], 6, (112.0, BAT[0], BAT[1]), X)
    return [ec, ei, tb, hi, ln] + _glass(P, name, 1) + [tp, tc, wf, wd, mb, bt]


def _build_far(P, name):
    tb = P(name + "_tube", "pso_body")
    lathe(tb, [(0.0, TUBE_FAR[0][1])] + TUBE_FAR + [(0.0, LEN)], 6, (0, 0, 0), (1, 0, 0))
    mb = P(name + "_mount", "pso_mount")
    box(mb, BASE[0], BASE[1], 2.0, 34.0, C_BOT, -24.0)
    return [tb, mb]


# =============================================================================
# Materials (procedural, kmats; baked into the model atlas)
# =============================================================================
def _vnode(t, op, a, b):
    n = t.node("ShaderNodeVectorMath")
    n.operation = op
    for i, x in enumerate((a, b)):
        if isinstance(x, (tuple, list, Vector)):
            n.inputs[i].default_value = tuple(x)
        else:
            t.link(x, n.inputs[i])
    return n


def angle_about(t, pos, center, e1, e2):
    """Angle of a point around the axis (through center, basis e1, e2 across the axis), -pi..pi."""
    d = _vnode(t, "SUBTRACT", pos, center).outputs[0]
    x = _vnode(t, "DOT_PRODUCT", d, e1).outputs["Value"]
    y = _vnode(t, "DOT_PRODUCT", d, e2).outputs["Value"]
    return t.math("ARCTAN2", y, x)


def along(t, nvec, axis):
    """abs(cos) of the angle between the normal and the axis: 1 - end face, 0 - side surface."""
    return t.math("ABSOLUTE", _vnode(t, "DOT_PRODUCT", nvec, axis).outputs["Value"])


def _normal_vec(t):
    """Normal of a smoothed face (place: faces are smooth, sharp edges stay, as in the game)."""
    gn = t.node("ShaderNodeNewGeometry")
    return gn.outputs["Normal"]


def smooth_normal(t):
    """Like kmats.Tree.normal(), but smoothed (kmats takes the face normal - stripes on round
    parts).
    """
    s = t.node("ShaderNodeSeparateXYZ")
    t.link(_normal_vec(t), s.inputs[0])
    return s


def weather(t, col, vec, sep, nsep, floor_z, dust, grime, small, cav=0.5, cav_dist=0.010, low_h=0.05):
    """Dust, grime in corners and layers of the "dayz" look at the scale of a 0.4 m object
    (kmats.weather is tuned for 1-2 m machines: its blotch would cover the whole scope).
    """
    look = kmats.LOOK
    if look["name"] == "dayz":
        dust, cav = dust * look["dust_k"], cav * look["cav_k"]
    sv = t.stretch(vec, small, small, small)
    up = t.maprange(nsep.outputs["Z"], 0.4, 0.9, 0.0, 1.0)
    dn = t.maprange(t.noise(sv, 4.0, 6.0, 0.6), 0.35, 0.7, 0.4, 1.0)
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", up, dn), dust), col, kmats.DUST)
    c = t.maprange(t.cavity(cav_dist), 0.15, 0.6, 0.0, 1.0)
    low = t.maprange(sep.outputs["Z"], floor_z, floor_z + low_h, 1.0, 0.0)
    gr = t.math("MAXIMUM", t.math("MULTIPLY", c, cav), t.math("MULTIPLY", low, grime))
    gr = t.math("MULTIPLY", gr, t.maprange(t.noise(sv, 7.0, 8.0, 0.6), 0.3, 0.7, 0.5, 1.0))
    col = t.mixc(gr, col, kmats.GRIME)
    if look["name"] == "dayz":
        # the tone blotches of the "dayz" look mix the color with white (0.4 x mottle): black enamel
        # would turn grey, up to ~80/255, so they are weaker here; the material itself sets the tone
        old = {k: look[k] for k in ("streaks", "smudge", "scratches", "mottle")}
        look.update(streaks=old["streaks"] * 0.5, smudge=old["smudge"] * 0.7, scratches=old["scratches"] * 0.25,
                    mottle=old["mottle"] * 0.2)
        try:
            col, gr = kmats.dayz_layers(t, col, gr, t.stretch(vec, small * 0.6, small * 0.6, small * 0.6), sep, nsep,
                                        grime)
        finally:
            look.update(old)
    return col, gr


def _rub(t, pos, rub):
    """Spots grabbed by hands: [(center, radius, strength)] - weaker toward the edge."""
    f = 0.0
    for c, r, k in rub:
        d = _vnode(t, "SUBTRACT", pos, tuple(c)).outputs[0]
        ln = _vnode(t, "LENGTH", d, (0, 0, 0)).outputs["Value"]
        near = t.math("MULTIPLY", t.maprange(ln, r * 0.25, r, 1.0, 0.0), k)
        f = near if isinstance(f, float) else t.math("ADD", f, near)
    return f


def build_enamel(mat, origin, color, bare, primer, seed, gloss=0.34, spec=0.30, wear=(0.62, 0.68), edge_k=0.95,
                 crinkle=0.30, rub=(), oil=0.3, floor_z=0.0, dust=0.06, grime=0.35, small=2.6):
    """Black shagreen enamel of optics over metal: shagreen bumps (relief, tops lighter), blotchy
    tone, worn to bare metal on the edges and where hands grab (a thin rim of primer), oil
    stains on top, dust in the corners.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = smooth_normal(t)
    pos = sep.inputs[0].links[0].from_socket
    sv = t.stretch(vec, small, small, small)
    base = t.mixc(t.maprange(t.noise(sv, 2.2, 5.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.80 for c in color[:3]) + (1,), color)
    cr = t.noise(vec, 520.0, 3.0, 0.5)
    crn = t.maprange(cr, 0.4, 0.7, 0.0, 1.0)
    base = t.mixc(t.math("MULTIPLY", crn, 0.30), base, tuple(min(1.0, c * 1.7 + 0.004) for c in color[:3]) + (1,))
    edge = t.maprange(t.edge_wear(0.0012), 0.04, 0.20, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(sv, 9.0, 10.0, 0.7), 0.75), t.math("MULTIPLY", edge, edge_k))
    r_ = _rub(t, pos, rub)
    if not isinstance(r_, float):
        grain = t.maprange(t.noise(vec, 60.0, 8.0, 0.7), 0.3, 0.7, 0.5, 1.0)
        f = t.math("ADD", f, t.math("MULTIPLY", r_, grain))
    worn = t.step(f, wear[0], wear[1])
    rim = t.math("SUBTRACT", t.step(f, wear[0] - 0.05, wear[0]), worn)
    brush = t.noise(t.stretch(vec, 0.05, 1.0, 1.0), 160.0, 4.0, 0.7)
    metal = t.mixc(t.maprange(brush, 0.3, 0.7, 0.0, 1.0), tuple(c * 0.72 for c in bare[:3]) + (1,),
                   tuple(min(1.0, c * 1.12) for c in bare[:3]) + (1,))
    col = t.mixc(t.math("MULTIPLY", rim, 0.7), base, primer)
    col = t.mixc(worn, col, metal)
    # rare short scratches to the metal (not along one axis: the scope lies in different ways)
    sc = t.step(t.noise(vec, 140.0, 2.0, 0.5), 0.745, 0.76)
    sc = t.math("MULTIPLY", sc, t.maprange(t.noise(sv, 5.0, 4.0, 0.5), 0.45, 0.7, 0.0, 0.7))
    col = t.mixc(t.math("MULTIPLY", sc, 0.6), col, metal)
    g_ = t.math("ADD", gloss, t.math("MULTIPLY", worn, 0.58 - gloss))
    s_ = t.math("ADD", spec, t.math("MULTIPLY", worn, 0.62 - spec))
    if oil > 0:
        up = t.maprange(nsep.outputs["Z"], 0.3, 0.9, 0.0, 1.0)
        ol = t.math("MULTIPLY", t.step(t.noise(sv, 3.5, 6.0, 0.6), 0.60, 0.70), t.math("MULTIPLY", up, oil))
        col = t.mixc(t.math("MULTIPLY", ol, 0.5), col, kmats.lin((10, 9, 8)))
        g_ = t.math("ADD", g_, t.math("MULTIPLY", ol, 0.3))
    col, dirt = weather(t, col, vec, sep, nsep, floor_z, dust, grime, small)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    h = t.math("ADD", t.math("MULTIPLY", t.math("SUBTRACT", cr, 0.5), crinkle),
               t.math("ADD", t.math("MULTIPLY", worn, -0.25), t.math("MULTIPLY", sc, -0.15)))
    return kmats.out(t, col, g_, s_, h)


def build_rubber(mat, origin, color, seed, gloss=0.14, spec=0.07, bloom=0.15, floor_z=0.0, dust=0.25, grime=0.3,
                 small=2.6):
    """Old rubber: blotchy tone, a grey bloom (faded), edges worn to a shine, fine roughness, dust
    in the folds.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = smooth_normal(t)
    sv = t.stretch(vec, small, small, small)
    col = t.mixc(t.maprange(t.noise(sv, 5.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                 tuple(c * 0.85 for c in color[:3]) + (1,), tuple(min(1.0, c * 1.15) for c in color[:3]) + (1,))
    bl = t.step(t.noise(sv, 2.4, 5.0, 0.55), 0.50, 0.72)
    col = t.mixc(t.math("MULTIPLY", bl, bloom), col, kmats.lin((78, 78, 78)))
    edge = t.maprange(t.edge_wear(0.0012), 0.05, 0.25, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.35), col, tuple(min(1.0, c * 2.0 + 0.01) for c in color[:3]) + (1,))
    col, dirt = weather(t, col, vec, sep, nsep, floor_z, dust, grime, small, cav=0.6)
    g_ = t.math("ADD", t.math("SUBTRACT", gloss, t.math("MULTIPLY", dirt, gloss * 0.6)), t.math("MULTIPLY", edge, 0.15))
    h = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 700.0, 2.0, 0.5), 0.12), t.math("MULTIPLY", bl, -0.05))
    return kmats.out(t, col, g_, spec, h)


def build_metal(mat, origin, color, seed, gloss=0.50, spec=0.55, brush_axis=(1.0, 1.0, 0.05), ticks=None,
                floor_z=0.0, dust=0.08, grime=0.3, small=2.6):
    """Aluminium (scale, windage drum) or blued steel: grinding, tone, wear. ticks - scale ticks:
    dict(center, z0, z1, n) - n ticks around the vertical through center, every fifth longer,
    black (engraving with paint), on the side surface between z0 and z1.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = smooth_normal(t)
    pos = sep.inputs[0].links[0].from_socket
    sv = t.stretch(vec, small, small, small)
    brush = t.noise(t.stretch(vec, *brush_axis), 240.0, 4.0, 0.7)
    col = t.mixc(t.maprange(brush, 0.3, 0.7, 0.0, 1.0), tuple(c * 0.80 for c in color[:3]) + (1,),
                 tuple(min(1.0, c * 1.10) for c in color[:3]) + (1,))
    col = t.mixc(t.maprange(t.noise(sv, 3.0, 5.0, 0.6), 0.35, 0.7, 0.0, 0.35), col,
                 tuple(c * 0.6 for c in color[:3]) + (1,))
    g_, h = gloss, t.math("MULTIPLY", brush, 0.06)
    if ticks:
        ang = angle_about(t, pos, ticks["center"], (1.0, 0.0, 0.0), (0.0, 1.0, 0.0))
        n = float(ticks["n"])
        zr = t.maprange(sep.outputs["Z"], ticks["z0"], ticks["z1"], 0.0, 1.0)
        side = t.math("LESS_THAN", along(t, _normal_vec(t), (0.0, 0.0, 1.0)), 0.5)
        fr = t.math("FRACT", t.math("MULTIPLY", ang, n / (2 * math.pi)))
        minor = t.math("MULTIPLY", t.math("LESS_THAN", fr, 0.16), t.math("GREATER_THAN", zr, 0.55))
        fr5 = t.math("FRACT", t.math("MULTIPLY", ang, n / 5.0 / (2 * math.pi)))
        major = t.math("MULTIPLY", t.math("LESS_THAN", fr5, 0.045), t.math("GREATER_THAN", zr, 0.18))
        tk = t.math("MULTIPLY", t.math("MAXIMUM", minor, major), side)
        col = t.mixc(tk, col, kmats.lin((16, 16, 16)))
        g_ = t.math("SUBTRACT", gloss, t.math("MULTIPLY", tk, gloss * 0.7))
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", tk, 0.2))
    col, dirt = weather(t, col, vec, sep, nsep, floor_z, dust, grime, small, cav=0.4)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    return kmats.out(t, col, g_, spec, h)


def build_knurl(mat, origin, color, bare, seed, center, e1, e2, axis, n=48, gloss=0.40, spec=0.45, floor_z=0.0,
                dust=0.1, grime=0.5, small=2.6):
    """Knurling (handwheel cap, battery cap): n flutes around the axis through center (relief),
    crests worn to metal, grime in the valleys; the end face is smooth.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = smooth_normal(t)
    pos = sep.inputs[0].links[0].from_socket
    ang = angle_about(t, pos, center, e1, e2)
    fr = t.math("FRACT", t.math("MULTIPLY", ang, n / (2 * math.pi)))
    tri = t.math("MULTIPLY", t.math("ABSOLUTE", t.math("SUBTRACT", fr, 0.5)), 2.0)
    side = t.maprange(along(t, _normal_vec(t), axis), 0.5, 0.7, 1.0, 0.0)
    ridge = t.math("MULTIPLY", t.maprange(tri, 0.15, 0.85, 0.0, 1.0), side)
    sv = t.stretch(vec, small, small, small)
    col = t.mixc(t.maprange(t.noise(sv, 4.0, 5.0, 0.6), 0.3, 0.7, 0.0, 1.0), tuple(c * 0.85 for c in color[:3]) + (1,),
                 color)
    top = t.math("MULTIPLY", t.step(ridge, 0.75, 0.95), t.maprange(t.noise(sv, 12.0, 6.0, 0.6), 0.3, 0.6, 0.2, 1.0))
    col = t.mixc(t.math("MULTIPLY", top, 0.8), col, bare)
    valley = t.math("MULTIPLY", t.math("SUBTRACT", 1.0, ridge), side)
    col = t.mixc(t.math("MULTIPLY", valley, 0.45), col, kmats.GRIME)
    edge = t.maprange(t.edge_wear(0.0010), 0.05, 0.22, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.6), col, bare)
    col, dirt = weather(t, col, vec, sep, nsep, floor_z, dust, grime, small, cav=0.4)
    g_ = t.math("ADD", gloss, t.math("MULTIPLY", top, 0.15))
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    h = t.math("MULTIPLY", ridge, 0.55)
    return kmats.out(t, col, g_, spec, h)


def kinds(pose, floor_z=0.0, wear=1.0):
    """Scope materials at pose (scale and knurl centers - in Blender). wear - the wear strength
    (1 - like a gunsmith who uses the scope every day).
    """
    lin = kmats.lin
    ct = pose.world((A_T, 0.0, 0.0))
    z0, z1 = pose.world((A_T, 0.0, 26.5)).z, pose.world((A_T, 0.0, 34.0)).z
    cb = pose.world((112.0, BAT[0], BAT[1]))
    ax = pose.dir((1, 0, 0))
    eb1, eb2 = pose.dir((0, 1, 0)), Vector((0.0, 0.0, 1.0))
    # where hands grab: the eyepiece bell, handwheels, bracket foot, clamp lever
    rub = [(pose.world((52.0, 0.0, 0.0)), 0.024, 0.22 * wear), (pose.world((A_T, -14.0, 16.0)), 0.022, 0.25 * wear),
           (pose.world((305.0, 0.0, 0.0)), 0.026, 0.14 * wear)]
    mrub = [(pose.world((232.0, 30.0, -100.0)), 0.020, 0.16 * wear), (pose.world((272.0, 34.0, -70.0)), 0.015, 0.14 * wear)]
    black = lin((34, 34, 36))
    alu = lin((138, 138, 134))
    return {
        "pso_enamel": (build_enamel, dict(color=black, bare=lin((128, 128, 132)), primer=lin((48, 46, 42)), seed=31.3,
                                          wear=(0.66 - 0.04 * wear, 0.71 - 0.04 * wear), rub=rub, floor_z=floor_z)),
        "pso_mount": (build_enamel, dict(color=lin((32, 32, 34)), bare=lin((122, 122, 126)), primer=lin((46, 44, 40)),
                                         seed=32.7, wear=(0.62 - 0.04 * wear, 0.67 - 0.04 * wear), edge_k=1.1,
                                         rub=mrub, oil=0.45, floor_z=floor_z, grime=0.5)),
        "pso_rubber": (build_rubber, dict(color=lin((28, 28, 28)), seed=33.1, floor_z=floor_z, dust=0.12, grime=0.2)),
        "pso_scale": (build_metal, dict(color=alu, seed=33.9, ticks=dict(center=tuple(ct), z0=z0, z1=z1, n=20),
                                        floor_z=floor_z)),
        "pso_alu": (build_metal, dict(color=lin((132, 132, 128)), seed=34.3, brush_axis=(1.0, 0.05, 1.0),
                                      floor_z=floor_z)),
        "pso_steel": (build_metal, dict(color=lin((58, 60, 64)), seed=34.9, gloss=0.42, spec=0.5, floor_z=floor_z,
                                        grime=0.45)),
        "pso_knurl": (build_knurl, dict(color=lin((30, 30, 32)), bare=lin((118, 118, 120)), seed=35.3, center=tuple(ct),
                                        e1=(1.0, 0.0, 0.0), e2=(0.0, 1.0, 0.0), axis=(0.0, 0.0, 1.0), n=48,
                                        floor_z=floor_z)),
        "pso_knurl_b": (build_knurl, dict(color=lin((30, 30, 32)), bare=lin((118, 118, 120)), seed=35.9,
                                          center=tuple(cb), e1=tuple(eb1), e2=tuple(eb2), axis=tuple(ax), n=32,
                                          floor_z=floor_z)),
        "pso_black": (build_rubber, dict(color=lin((11, 11, 12)), seed=36.3, gloss=0.06, spec=0.04, bloom=0.0,
                                         floor_z=floor_z, dust=0.0, grime=0.1)),
        "pso_lens": ("flat", dict(color=lin((22, 28, 40)), gloss=0.95, spec=0.9)),
    }
