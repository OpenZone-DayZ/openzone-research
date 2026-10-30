"""Shared by the two M86 (plate clamp) variants: materials and geometry helpers.

build_m86.py (variant A, a screw press clamp) and build_m86b.py (variant B, an angle plate with two
F-clamps) live in one folder and take from here: worn enamel over cast iron and beech (from the M81
generator), scaled steel, the screw thread and a solid of revolution (lathe - from the M76/M81
generators).

Shape helpers without angularity: a polygon with rounded corners (round_poly), its inward/outward
offset (offset_poly), a body by rings (loft), a slab with rounded edges and a cast pocket on the
side (slab, pocket_slab), a bolt head with a chamfer and a washer, geometric thread - a helical
grid (helix_thread) and its material (mat_helix). The kit has none of them and is shared by all
models, so they are kept here.
"""
import math
import random

import bmesh
from mathutils import Vector

import kgeo as g
import kmats


# --- geometry -----------------------------------------------------------------------------------
def lathe(part, fr, prof, sides, cap_lo=False, cap_hi=False):
    """Solid of revolution about the axis fr.n (from the M76 generator): the profile [(r, h)] goes so that
    the outside is on the right (segment normal (dh, -dr)); the cap of the first ring looks to -n, the
    last to +n.
    """
    bm = part.bm
    angs = [2 * math.pi * k / sides for k in range(sides)]
    rings = [[bm.verts.new(fr.p(r * math.cos(a), r * math.sin(a), h)) for a in angs] for r, h in prof]
    faces = []
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        for k in range(sides):
            j = (k + 1) % sides
            f = bm.faces.new([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]])
            am = (k + 0.5) * 2 * math.pi / sides
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


def axis_frame(o, n):
    """Rotation axis n from the point o: u, v are any perpendiculars (the solid of revolution is symmetric)."""
    n = tuple(float(c) for c in n)
    ref = (0.0, 0.0, 1.0) if abs(n[2]) < 0.9 else (1.0, 0.0, 0.0)
    u = (ref[1] * n[2] - ref[2] * n[1], ref[2] * n[0] - ref[0] * n[2], ref[0] * n[1] - ref[1] * n[0])
    v = (n[1] * u[2] - n[2] * u[1], n[2] * u[0] - n[0] * u[2], n[0] * u[1] - n[1] * u[0])
    return g.Frame(o, u, v, n)


def hexagon(part, center, axis_n, af, h, frame_u=None):
    """A hexagon (bolt head, nut) across flats af, height h, axis axis_n from center (the bottom)."""
    fr = axis_frame(center, axis_n)
    r = af / math.sqrt(3.0)
    poly = [(r * math.cos(math.pi / 6 + k * math.pi / 3), r * math.sin(math.pi / 6 + k * math.pi / 3))
            for k in range(6)]
    return g.prism(part, poly, (0, 1), 0.0, h, frame=fr)


def retag(part, faces, test, region):
    """Faces from `faces` for which test(normal) is true go to the region `region` (the part already has it)."""
    idx = part.region_index(region)
    for f in faces:
        if f.is_valid:
            f.normal_update()
            if test(f.normal):
                f[part.reg] = idx


def bev(spec, r=0.002):
    return {"r": r, "seg": 1} if spec["lod"] == 0 else {}


def ccw(poly):
    """Polygon counter-clockwise (signed area > 0)."""
    a = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
            for i in range(len(poly)))
    return list(poly) if a > 0 else list(poly)[::-1]


def offset_poly(poly, d):
    """Counter-clockwise polygon: every edge moved outward by d (d < 0 - inward), the vertices are the
    intersections of the neighbouring moved edges (like a chamfer: corners stay corners).
    """
    n = len(poly)
    lines = []
    for i in range(n):
        a, b = Vector(poly[i]), Vector(poly[(i + 1) % n])
        e = (b - a).normalized()
        lines.append((a + Vector((e.y, -e.x)) * d, e))
    out = []
    for i in range(n):
        (p1, d1), (p2, d2) = lines[i - 1], lines[i]
        den = d1.x * d2.y - d1.y * d2.x
        if abs(den) < 1e-9:
            out.append((p2.x, p2.y))
            continue
        t = ((p2.x - p1.x) * d2.y - (p2.y - p1.y) * d2.x) / den
        q = p1 + d1 * t
        out.append((q.x, q.y))
    return out


def round_poly(poly, r, n=2):
    """Polygon corners -> arcs of radius r in n segments (n = 1 is a chamfer). r is a number or a
    per-vertex list (0 keeps the corner sharp), n likewise. Convex and concave corners alike: the arc
    touches both edges, the radius shrinks on a short edge.
    """
    m = len(poly)
    rs = list(r) if isinstance(r, (list, tuple)) else [r] * m
    ns = list(n) if isinstance(n, (list, tuple)) else [n] * m
    out = []
    for i in range(m):
        P, A, B = Vector(poly[i]), Vector(poly[i - 1]), Vector(poly[(i + 1) % m])
        ri, ni = rs[i], max(1, ns[i])
        u1, u2 = A - P, B - P
        l1, l2 = u1.length, u2.length
        if ri <= 0 or l1 < 1e-9 or l2 < 1e-9:
            out.append((P.x, P.y))
            continue
        u1.normalize()
        u2.normalize()
        phi = math.acos(max(-1.0, min(1.0, u1.dot(u2))))
        if phi > math.pi - 1e-3 or phi < 1e-3:
            out.append((P.x, P.y))
            continue
        t = ri / math.tan(phi / 2)
        tmax = 0.49 * min(l1, l2)
        if t > tmax:
            t = tmax
            ri = t * math.tan(phi / 2)
        t1, t2 = P + u1 * t, P + u2 * t
        c = P + (u1 + u2).normalized() * (ri / math.sin(phi / 2))
        a1 = math.atan2(t1.y - c.y, t1.x - c.x)
        da = math.atan2(t2.y - c.y, t2.x - c.x) - a1
        while da > math.pi:
            da -= 2 * math.pi
        while da < -math.pi:
            da += 2 * math.pi
        for k in range(ni + 1):
            a = a1 + da * k / ni
            out.append((c.x + ri * math.cos(a), c.y + ri * math.sin(a)))
    return out


def loft(part, rings, cap_lo=True, cap_hi=True):
    """Body by rings: rings are closed point rings (same count), neighbouring rings give a strip of quads,
    the first and last are caps. Normals outward: the body is built closed, and a cap that cannot be
    seen (cap_lo / cap_hi = False - the end sits in another part) is removed after the normals are
    flipped.
    """
    bm = part.bm
    vs = [[bm.verts.new(tuple(p)) for p in ring] for ring in rings]
    n = len(rings[0])
    faces = []
    for i in range(len(vs) - 1):
        for k in range(n):
            j = (k + 1) % n
            faces.append(bm.faces.new([vs[i][k], vs[i][j], vs[i + 1][j], vs[i + 1][k]]))
    lo, hi = bm.faces.new(vs[0][::-1]), bm.faces.new(vs[-1])
    bmesh.ops.recalc_face_normals(bm, faces=faces + [lo, hi])
    hidden = [f for f, keep in ((lo, cap_lo), (hi, cap_hi)) if not keep]
    if hidden:
        bmesh.ops.delete(bm, geom=hidden, context="FACES_ONLY")
    faces += [f for f, keep in ((lo, cap_lo), (hi, cap_hi)) if keep]
    return part.tag(faces)


def _plane_pt(axes, frame):
    ia, ib = axes
    ic = 3 - ia - ib

    def P(a, b, c):
        q = [0.0, 0.0, 0.0]
        q[ia], q[ib], q[ic] = a, b, c
        return frame.p(*q) if frame else Vector(q)
    return P


def _round_steps(r, seg):
    """Edge rounding: (how far inward the polygon moves, how far from the end) per arc step."""
    return [(r * (1 - math.sin(0.5 * math.pi * k / seg)), r * (1 - math.cos(0.5 * math.pi * k / seg)))
            for k in range(seg + 1)]


def slab(part, poly, axes, c0, c1, r=0.0, seg=1, r1=None, seg1=None, frame=None, caps=(True, True)):
    """Prism of the polygon poly in the plane of axes `axes` (like kgeo.prism) from c0 to c1, the end
    edges are rounded: r, seg at the c0 end (seg - arc segments, 1 is a chamfer), r1, seg1 at c1 (None -
    as at c0); caps says whether ends are needed (an invisible end lying on another part is not needed).
    """
    poly = ccw(poly)
    P = _plane_pt(axes, frame)
    r1 = r if r1 is None else r1
    seg1 = seg if seg1 is None else seg1
    lim = 0.49 * (c1 - c0)
    r, r1 = min(r, lim), min(r1, lim)

    def ring(off, c):
        pts = offset_poly(poly, -off) if off > 1e-9 else poly
        return [P(a, b, c) for a, b in pts]
    rings = [ring(o, c0 + d) for o, d in _round_steps(r, seg)] if r > 0 else [ring(0.0, c0)]
    rings += [ring(o, c1 - d) for o, d in reversed(_round_steps(r1, seg1))] if r1 > 0 else [ring(0.0, c1)]
    return loft(part, rings, cap_lo=caps[0], cap_hi=caps[1])


def pocket_slab(part, poly, axes, c0, c1, rim=0.002, depth=0.0015, edge=0.0, frame=None):
    """Cast part with a pocket on both sides (a clamp bracket, as in the photo): the outline poly from c0
    to c1, a rim of width rim along the outline, a pocket of depth depth inside; edge - a chamfer of the
    outer edge (0 - sharp).
    """
    poly = ccw(poly)
    P = _plane_pt(axes, frame)
    inner = offset_poly(poly, -rim)

    def ring(pts, c):
        return [P(a, b, c) for a, b in pts]
    rings = [ring(inner, c0 + depth), ring(inner, c0)]
    if edge > 0:
        rings += [ring(offset_poly(poly, -edge), c0), ring(poly, c0 + edge), ring(poly, c1 - edge),
                  ring(offset_poly(poly, -edge), c1)]
    else:
        rings += [ring(poly, c0), ring(poly, c1)]
    rings += [ring(inner, c1), ring(inner, c1 - depth)]
    return loft(part, rings)


def hex_head(part, fr, af, h, chamfer=0.0008):
    """Bolt head across flats af, height h from fr.o along fr.n: the top edge has a chamfer (the hexagon
    converges to a smaller one), as on a real bolt - the corners are cut by a cone.
    """
    rr = af / math.sqrt(3.0)
    hexa = [(rr * math.cos(math.pi / 6 + k * math.pi / 3), rr * math.sin(math.pi / 6 + k * math.pi / 3))
            for k in range(6)]
    rings = [[fr.p(a, b, 0.0) for a, b in hexa], [fr.p(a, b, h - chamfer) for a, b in hexa],
             [fr.p(a * 0.84, b * 0.84, h) for a, b in hexa]]
    return loft(part, rings)


def washer(part, fr, r_out, t, sides=8):
    """Washer under a head: a ring with a chamfer on top (the inner edge is hidden by the head)."""
    return lathe(part, fr, [(r_out, 0.0), (r_out, t * 0.7), (r_out - t * 0.4, t)], sides, cap_hi=True)


def helix_thread(part, fr, h0, h1, r_major, depth, pitch, cols=10, rows=2):
    """Geometric thread: a helical grid around the axis fr.n. Column k (angle 2 pi k / cols) is raised by
    pitch*k/cols, rows go every pitch/rows (rows = 2 gives the turn crest and the valley, a V profile),
    the column seam is shifted by one turn. It covers [h0, h1] fully; the ends are toothed and extend
    past the segment by less than half a turn - neighbouring parts (the foot, the boss) hide them.
    Normals point away from the axis.
    """
    bm = part.bm
    n_rows = int(math.ceil(rows * ((h1 - h0) / pitch + 1.0))) + 1
    base = h0 - pitch
    vs = []
    for j in range(n_rows):
        f = (j % rows) / rows
        rr = r_major - depth * (1.0 - abs(1.0 - 2.0 * f))
        row = []
        for k in range(cols):
            a = 2 * math.pi * k / cols
            row.append(bm.verts.new(fr.p(rr * math.cos(a), rr * math.sin(a), base + pitch * (j / rows + k / cols))))
        vs.append(row)
    quads = []
    for j in range(n_rows - 1):
        for k in range(cols - 1):
            quads.append([vs[j][k], vs[j][k + 1], vs[j + 1][k + 1], vs[j + 1][k]])
        if j + rows + 1 < n_rows:
            quads.append([vs[j][cols - 1], vs[j + rows][0], vs[j + rows + 1][0], vs[j + 1][cols - 1]])
    # faces entirely below h0 or above h1 are not needed: a tooth smaller than half a turn remains
    ax = fr.n

    def hgt(v):
        return (v.co - fr.o).dot(ax)
    faces = [bm.faces.new(q) for q in quads
             if max(hgt(v) for v in q) > h0 and min(hgt(v) for v in q) < h1]
    for v in [v for row in vs for v in row if not v.link_faces]:
        bm.verts.remove(v)
    for f in faces:
        f.normal_update()
        d = f.calc_center_median() - fr.o
        radial = d - fr.n * d.dot(fr.n)
        if f.normal.dot(radial) < 0:
            f.normal_flip()
    return part.tag(faces)


def jitter_poly(poly, amp, seed):
    rnd = random.Random(seed)
    return [(x + rnd.uniform(-amp, amp), y + rnd.uniform(-amp, amp)) for x, y in poly]


# --- materials ----------------------------------------------------------------------------------
def mat_worn(mat, origin, color, under, seed=1.0, gloss=0.38, spec=0.28, chip=(0.60, 0.66), rub=0.0,
             chip_rust=0.15, rust=(0.70, 0.78), rust_low=0.2, floor_z=0.0, dust=0.3, grime=0.45, decal_items=(),
             edge_r=0.003, edge_k=(0.06, 0.25), sat=1.0):
    """Enamel over cast iron worn by work (from the M81 generator): chips along the edges and large
    patches where the paint was rubbed off by hands and workpieces (rub is their strength, more on
    faces looking up); grey cast iron under the enamel, polished where worn; rust only in part of the
    chips (chip_rust) and as rare specks. kmats.build_paint paints every chip with rust at 60 % - on a
    tool in use the metal in the chips is grey.
    edge_r, edge_k - the radius at which edges are found (kmats.edge_wear) and the threshold: on
    rounded edges the normal changes smoothly (in 45-degree steps), and with the old 3 mm /
    (0.06..0.25) the chips on them almost vanish. sat is the saturation after the layers of the dayz
    look (their white tone patches make a saturated red pink; 1 is as is).
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.88 for c in color[:3]) + (1,), color)
    col = kmats.decals(t, base, sep, nsep, decal_items)
    edge = t.maprange(t.edge_wear(edge_r), edge_k[0], edge_k[1], 0.0, 1.0)
    blot = t.noise(vec, 11.0, 10.0, 0.7)
    up = t.maprange(nsep.outputs["Z"], 0.2, 0.9, 0.4, 1.0)
    big = t.math("MULTIPLY", t.maprange(t.noise(vec, 2.2, 5.0, 0.6), 0.45, 0.75, 0.0, 1.0), t.math("MULTIPLY", up, rub))
    w = t.math("ADD", t.math("ADD", t.math("MULTIPLY", blot, 0.75), t.math("MULTIPLY", edge, 0.55)), big)
    chips = t.step(w, chip[0], chip[1])
    metal = t.mixc(t.maprange(t.noise(vec, 28.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                   tuple(c * 0.80 for c in under[:3]) + (1,), tuple(min(1.0, c * 1.25) for c in under[:3]) + (1,))
    col = t.mixc(chips, col, metal)
    low = t.maprange(sep.outputs["Z"], floor_z + 0.5, floor_z, 0.0, rust_low)
    speck = t.step(t.noise(vec, 24.0, 8.0, 0.7), rust[0], rust[1])
    some = t.step(t.noise(vec, 6.0, 4.0, 0.6), 0.55, 0.70)
    rust_amt = t.math("MAXIMUM", t.math("MULTIPLY", t.math("MULTIPLY", chips, some), chip_rust),
                      t.math("MULTIPLY", speck, t.math("ADD", 0.25, low)))
    rust_col = t.ramp(t.noise(vec, 30.0, 6.0, 0.6), [(0.3, kmats.RUST[0]), (0.55, kmats.RUST[1]), (0.8, kmats.RUST[2])])
    col = t.mixc(t.math("MULTIPLY", rust_amt, 0.9), col, rust_col)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    if sat != 1.0:
        hsv = t.node("ShaderNodeHueSaturation", Saturation=sat)
        t.link(col, hsv.inputs["Color"])
        col = hsv.outputs["Color"]
    gl = t.math("SUBTRACT", t.mixf(chips, gloss, 0.50), t.math("ADD", t.math("MULTIPLY", rust_amt, 0.3),
                                                               t.math("MULTIPLY", dirt, gloss * 0.5)))
    sp = t.math("SUBTRACT", t.mixf(chips, spec, 0.55), t.math("ADD", t.math("MULTIPLY", rust_amt, 0.3),
                                                              t.math("MULTIPLY", dirt, spec * 0.4)))
    h = t.math("ADD", t.math("MULTIPLY", chips, -0.4), t.math("MULTIPLY", rust_amt, t.noise(vec, 90.0, 4.0, 0.6)))
    return kmats.out(t, col, gl, sp, h)


def mat_wood(mat, origin, color, seed=1.0, scale=7.0, along="x", gloss=0.16, spec=0.10, floor_z=0.0, dust=0.2,
             grime=0.5, rings=0.6, knots=0.4, oil=0.35, decal_items=()):
    """Beech at a small scale (from the M81 generator): the kwood pattern is made for furniture boards
    (growth rings about every 10 cm) and is invisible on a 3 cm handle; here the coordinates are
    multiplied by scale. oil is the greasiness: dark spots from hands.
    """
    t = kmats.Tree(mat)
    vec0, sep = t.coords(origin, seed)
    vec = t.stretch(vec0, scale, scale, scale)
    nsep = t.normal()
    k = {"x": (0.04, 1.0, 1.0), "y": (1.0, 0.04, 1.0), "z": (1.0, 1.0, 0.04)}[along]
    fib = t.stretch(vec, *k)
    fibers = t.noise(fib, 60.0, 4.0, 0.7)
    wave = t.node("ShaderNodeTexWave", Scale=4.0, Distortion=5.0, **{"Detail": 3.0, "Detail Scale": 1.5})
    wave.wave_type = "RINGS"
    t.link(fib, wave.inputs["Vector"])
    ring = t.math("MULTIPLY", wave.outputs["Fac"], rings)
    tone = t.maprange(t.noise(vec, 0.8, 3.0, 0.5), 0.3, 0.7, 0.0, 1.0)
    dark = tuple(c * 0.62 for c in color[:3]) + (1,)
    light = tuple(min(1.0, c * 1.22) for c in color[:3]) + (1,)
    col = t.mixc(tone, tuple(c * 0.90 for c in color[:3]) + (1,), tuple(min(1.0, c * 1.06) for c in color[:3]) + (1,))
    col = t.mixc(t.math("MULTIPLY", ring, 0.8), col, dark)
    col = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", fibers, 0.35), 0.6), col, dark)
    knot = t.step(t.noise(t.stretch(vec, *[0.4 if x < 1 else 1.0 for x in k]), 3.0, 2.0, 0.5),
                  1.0 - 0.06 * knots, 1.0 - 0.03 * knots)
    col = t.mixc(t.math("MULTIPLY", knot, 0.85), col, tuple(c * 0.35 for c in color[:3]) + (1,))
    stain = t.math("MULTIPLY", t.maprange(t.noise(vec0, 18.0, 4.0, 0.6), 0.48, 0.70, 0.0, 1.0), oil)
    col = t.mixc(stain, col, tuple(c * 0.45 for c in color[:3]) + (1,))
    col = kmats.decals(t, col, sep, nsep, decal_items)
    edge = t.maprange(t.edge_wear(0.002), 0.06, 0.25, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.40), col, light)
    col, dirt = kmats.weather(t, col, vec0, sep, nsep, floor_z, dust, grime, 0.5)
    gl = t.math("ADD", t.math("SUBTRACT", gloss, t.math("MULTIPLY", dirt, gloss * 0.6)), t.math("MULTIPLY", stain, 0.2))
    s = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.5))
    h = t.math("ADD", t.math("MULTIPLY", fibers, 0.25), t.math("MULTIPLY", ring, -0.25))
    h = t.math("SUBTRACT", h, t.math("MULTIPLY", knot, 0.3))
    return kmats.out(t, col, gl, s, h)


SCALE_DARK = kmats.lin((40, 42, 46))      # scale: a blue-black rolling film
SCALE_MID = kmats.lin((70, 72, 76))
STEEL_BARE = kmats.lin((128, 128, 126))   # metal under the flaked scale


def mat_scale(mat, origin, seed=1.0, flake=(0.62, 0.70), bright=0.5, rust=(0.74, 0.82), rust_low=0.25,
              oil=0.3, floor_z=0.0, dust=0.25, grime=0.45, gloss=0.30, spec=0.30, decal_items=(),
              edge_r=0.003, edge_k=(0.08, 0.30)):
    """Unpainted hot-rolled steel: the scale is a dark blue-grey film in patches of different tone, flaked
    down to grey metal in places (flake), edges rubbed to a shine (bright), reddish rust as specks and
    in the flaked spots, more toward the bottom; oil stains are darker and smoother. edge_r, edge_k are
    as in mat_worn (rounded edges).
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    # scale patches are centimetres, not metres: the item is 0.2 m and a large pattern is not
    # visible on it
    col = t.mixc(t.maprange(t.noise(vec, 14.0, 8.0, 0.65), 0.3, 0.7, 0.0, 1.0), SCALE_DARK, SCALE_MID)
    col = t.mixc(t.math("MULTIPLY", t.maprange(t.noise(vec, 45.0, 4.0, 0.6), 0.45, 0.75, 0.0, 1.0), 0.5), col,
                 kmats.lin((86, 84, 80)))
    col = kmats.decals(t, col, sep, nsep, decal_items)
    fl = t.step(t.noise(vec, 28.0, 10.0, 0.72), flake[0], flake[1])
    bare = t.mixc(t.maprange(t.noise(vec, 40.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                  tuple(c * 0.75 for c in STEEL_BARE[:3]) + (1,), STEEL_BARE)
    col = t.mixc(t.math("MULTIPLY", fl, 0.85), col, bare)
    edge = t.maprange(t.edge_wear(edge_r), edge_k[0], edge_k[1], 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, bright), col, tuple(min(1.0, c * 1.3) for c in STEEL_BARE[:3]) + (1,))
    low = t.maprange(sep.outputs["Z"], floor_z + 0.2, floor_z, 0.0, rust_low)
    speck = t.step(t.noise(vec, 22.0, 8.0, 0.7), rust[0], rust[1])
    rust_amt = t.math("MAXIMUM", t.math("MULTIPLY", t.math("MULTIPLY", fl, speck), 1.0),
                      t.math("MULTIPLY", speck, t.math("ADD", 0.35, low)))
    rust_col = t.ramp(t.noise(vec, 30.0, 6.0, 0.6), [(0.3, kmats.RUST[0]), (0.55, kmats.RUST[1]), (0.8, kmats.RUST[2])])
    col = t.mixc(t.math("MULTIPLY", rust_amt, 0.85), col, rust_col)
    st = t.math("MULTIPLY", t.maprange(t.noise(vec, 12.0, 4.0, 0.6), 0.55, 0.75, 0.0, 1.0), oil)
    col = t.mixc(t.math("MULTIPLY", st, 0.6), col, tuple(c * 0.55 for c in SCALE_DARK[:3]) + (1,))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    gl = t.math("SUBTRACT", t.math("ADD", t.mixf(edge, gloss, 0.55), t.math("MULTIPLY", st, 0.2)),
                t.math("ADD", t.math("MULTIPLY", rust_amt, 0.25), t.math("MULTIPLY", dirt, gloss * 0.5)))
    sp = t.math("SUBTRACT", t.mixf(t.math("MAXIMUM", edge, fl), spec, 0.55),
                t.math("ADD", t.math("MULTIPLY", rust_amt, 0.25), t.math("MULTIPLY", dirt, spec * 0.4)))
    h = t.math("ADD", t.math("MULTIPLY", fl, -0.25), t.math("MULTIPLY", t.noise(vec, 60.0, 6.0, 0.7), 0.15))
    return kmats.out(t, col, gl, sp, h)


def mat_thread(mat, origin, color, axis="z", pitch=0.004, seed=1.0, crest=1.5, gloss=0.55, spec=0.55,
               dust=0.1, grime=0.35, floor_z=0.0):
    """Screw thread: stripes along the axis with the pitch `pitch` (Wave BANDS along the axis:
    n = 20 * Scale * coordinate, period 2*pi / (20 * Scale)), crests rubbed lighter, oil with dirt in
    the valleys; the relief is for the normal map.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    wv = t.node("ShaderNodeTexWave", Scale=2 * math.pi / (20.0 * pitch), Distortion=0.0, Detail=0.0)
    wv.wave_type = "BANDS"
    wv.bands_direction = axis.upper()
    wv.wave_profile = "TRI"
    t.link(vec, wv.inputs["Vector"])
    crestv = t.maprange(wv.outputs["Fac"], 0.25, 0.85, 0.0, 1.0)
    tone = t.maprange(t.noise(vec, 30.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0)
    base = t.mixc(tone, tuple(c * 0.85 for c in color[:3]) + (1,), color)
    col = t.mixc(crestv, tuple(c * 0.45 for c in color[:3]) + (1,),
                 tuple(min(1.0, c * crest) for c in color[:3]) + (1,))
    col = t.mixc(0.5, base, col)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.4)
    gl = t.math("SUBTRACT", t.mixf(crestv, gloss * 0.7, gloss), t.math("MULTIPLY", dirt, gloss * 0.5))
    sp = t.math("SUBTRACT", t.mixf(crestv, spec * 0.6, spec), t.math("MULTIPLY", dirt, spec * 0.4))
    h = t.math("MULTIPLY", crestv, 0.9)
    return kmats.out(t, col, gl, sp, h)


def mat_helix(mat, origin, color, bare, r_root, r_crest, center=(0.0, 0.0), seed=1.0, gloss=0.55, spec=0.55,
              dust=0.06, grime=0.6, floor_z=0.0):
    """Geometric thread (helix_thread, the axis along Z through center): the turn crest is rubbed by the
    nut down to light steel, the valley is bluing with oil and dirt. The crest is recognised by the
    distance from the axis (r_root -> r_crest), not by edges: Bevel in edge_wear also sees the concave
    valleys.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    dx = t.math("SUBTRACT", sep.outputs["X"], center[0])
    dy = t.math("SUBTRACT", sep.outputs["Y"], center[1])
    rad = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", dx, dx), t.math("MULTIPLY", dy, dy)))
    crest = t.maprange(rad, r_root + 0.45 * (r_crest - r_root), r_crest - 0.05 * (r_crest - r_root), 0.0, 1.0)
    tone = t.maprange(t.noise(vec, 30.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0)
    base = t.mixc(tone, tuple(c * 0.80 for c in color[:3]) + (1,), color)
    worn = t.mixc(t.maprange(t.noise(vec, 60.0, 4.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                  tuple(c * 0.78 for c in bare[:3]) + (1,), bare)
    col = t.mixc(t.math("MULTIPLY", crest, 0.85), base, worn)
    oil = t.math("MULTIPLY", t.math("SUBTRACT", 1.0, crest), t.maprange(t.noise(vec, 14.0, 4.0, 0.6), 0.35, 0.7, 0.2, 0.7))
    col = t.mixc(oil, col, kmats.lin((30, 27, 22)))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.7)
    gl = t.math("SUBTRACT", t.mixf(crest, gloss * 0.8, gloss), t.math("MULTIPLY", dirt, gloss * 0.3))
    sp = t.math("SUBTRACT", t.mixf(crest, spec * 0.5, spec), t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, gl, sp, t.math("MULTIPLY", crest, 0.3))
