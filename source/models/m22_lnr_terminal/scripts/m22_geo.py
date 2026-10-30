"""M22 geometry that kgeo does not have: solids of revolution along any axis with regions by profile
segments (from M07/M13), faceted solids (each face has its own vertices, so faces stay faces under
smoothing: a faceted glass, a mug), a plate with rounded corners and edges (from M07), nail and screw
heads, a torus, layered prisms, knurled knobs, a corrugated sheet unwrapped for a vanilla texture.
The parts are kgeo.Part, faces point outward (kexport flips them for p3d itself).

Blender axes: X is width, Y is depth (the face, the player's side, is at -Y), Z is up.
"""
import math

import bmesh
from mathutils import Vector

import kgeo as g


def face(part, verts, want):
    """Face from bmesh vertices, oriented toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    part.tag([f])
    return f


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, from M04): k points per segment."""
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


def basis(axis):
    """Rotation axis (from M07): (a, b, w) - two transverse unit vectors and the longitudinal one; axis
    is "x", "-y", ... or a vector."""
    if isinstance(axis, str):
        w = Vector([1.0 if c == axis[-1] else 0.0 for c in "xyz"]) * (-1.0 if axis.startswith("-") else 1.0)
    else:
        w = Vector(axis).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(w.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    a = ref.cross(w).normalized()
    return a, w.cross(a).normalized(), w


def lathe(part, prof, sides, center, axis="z", caps=(False, False), phase=0.0, tags=None, rad=None):
    """Solid of revolution (from M07/M13): prof [(r, h)] - the section (r from the axis, h along axis from
    center), traversed along the outer surface; on a descent inward (a wall seen from inside) the faces
    look toward the axis, as they should. r = 0 is a point on the axis (a fan). caps - caps of the first
    and last ring. tags[i] - the region index of segment i (None - the part's current region). rad(k, i)
    - the radius multiplier of vertex k of ring i (lumps, dents). Returns the vertex rings."""
    a, b, w = basis(axis)
    c = Vector(center)
    bm = part.bm
    angs = [phase + 2 * math.pi * k / sides for k in range(sides)]
    rings = []
    for i, (r, h) in enumerate(prof):
        if r < 1e-7:
            rings.append(bm.verts.new(c + w * h))
        else:
            rings.append([bm.verts.new(c + (a * math.cos(t) + b * math.sin(t)) * (r * (rad(k, i) if rad else 1.0)) + w * h)
                          for k, t in enumerate(angs)])
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        nr, nh = h1 - h0, -(r1 - r0)
        R0, R1 = rings[i], rings[i + 1]
        for k in range(sides):
            j = (k + 1) % sides
            tm = angs[k] + math.pi / sides
            want = (a * math.cos(tm) + b * math.sin(tm)) * nr + w * nh
            if isinstance(R0, list) and isinstance(R1, list):
                vs = [R0[k], R0[j], R1[j], R1[k]]
            elif isinstance(R0, list):
                vs = [R0[k], R0[j], R1]
            elif isinstance(R1, list):
                vs = [R0, R1[j], R1[k]]
            else:
                continue
            f = face(part, vs, want)
            if tags is not None and tags[i] is not None:
                part.tag([f], tags[i])
    for cap, i, o in ((caps[0], 0, 1), (caps[1], len(prof) - 1, len(prof) - 2)):
        if cap and isinstance(rings[i], list):
            face(part, rings[i], w * (1.0 if prof[i][1] > prof[o][1] else -1.0))
    return rings


def facet_lathe(part, prof, sides, center, axis="z", phase=0.0, caps=(False, False)):
    """Faceted solid of revolution: each face has its own vertices around the circle, so smoothing (in
    the game and in the preview) does not blur them - the facets stay visible, like on a faceted glass.
    prof is as in lathe (r is to the facet edge)."""
    a, b, w = basis(axis)
    c = Vector(center)
    bm = part.bm
    angs = [phase + 2 * math.pi * k / sides for k in range(sides + 1)]
    for k in range(sides):
        cols = []
        for r, h in prof:
            cols.append([bm.verts.new(c + (a * math.cos(t) + b * math.sin(t)) * r + w * h) for t in (angs[k], angs[k + 1])])
        tm = angs[k] + math.pi / sides
        for i in range(len(prof) - 1):
            (r0, h0), (r1, h1) = prof[i], prof[i + 1]
            want = (a * math.cos(tm) + b * math.sin(tm)) * (h1 - h0) + w * (-(r1 - r0))
            face(part, [cols[i][0], cols[i][1], cols[i + 1][1], cols[i + 1][0]], want)
    for cap, i, o in ((caps[0], 0, 1), (caps[1], len(prof) - 1, len(prof) - 2)):
        if cap:
            r, h = prof[i]
            vs = [bm.verts.new(c + (a * math.cos(t) + b * math.sin(t)) * r + w * h) for t in angs[:-1]]
            face(part, vs, w * (1.0 if prof[i][1] > prof[o][1] else -1.0))


def ribbed(part, center, axis, r_out, r_in, h0, h1, ribs, top=True):
    """Knurled knob: a ring of 2*ribs vertices alternating between r_out and r_in from h0 to h1 along
    axis, a cap on top."""
    a, b, w = basis(axis)
    c = Vector(center)
    bm = part.bm
    n = 2 * ribs
    pts = [(a * math.cos(2 * math.pi * k / n) + b * math.sin(2 * math.pi * k / n)) * (r_out if k % 2 == 0 else r_in)
           for k in range(n)]
    lo = [bm.verts.new(c + p + w * h0) for p in pts]
    hi = [bm.verts.new(c + p + w * h1) for p in pts]
    for k in range(n):
        j = (k + 1) % n
        mid = (pts[k] + pts[j]) / 2
        face(part, [lo[k], lo[j], hi[j], hi[k]], mid)
    if top:
        face(part, hi, w)


def rrect(x0, x1, y0, y1, r, n):
    """Rectangle with rounded corners (n segments per corner), counterclockwise; n = 0 - sharp."""
    if n <= 0 or r <= 1e-6:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    out = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90.0), (x1 - r, y1 - r, 0.0), (x0 + r, y1 - r, 90.0), (x0 + r, y0 + r, 180.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def slab(part, x0, x1, y0, y1, z0, z1, rc=0.0, nc=0, re=0.0, ne=0, rb=0.0, nb=0, frame=None, caps=(True, True)):
    """Slab (from M07): in plan a rectangle with corners rounded by rc (nc segments), the top edge
    rounded by re (ne segments), the bottom by rb (nb). frame - a local system: x -> u, y -> v, z -> n."""
    rows = []
    if rb > 0 and nb > 0:
        rows += [(rb * (1 - math.sin(math.pi / 2 * k / nb)), z0 + rb * (1 - math.cos(math.pi / 2 * k / nb)))
                 for k in range(nb + 1)]
    else:
        rows.append((0.0, z0))
    top = [(re * (1 - math.cos(math.pi / 2 * k / ne)), z1 - re + re * math.sin(math.pi / 2 * k / ne))
           for k in range(ne + 1)] if re > 0 and ne > 0 else [(0.0, z1)]
    for r in top:
        if abs(r[0] - rows[-1][0]) > 1e-7 or abs(r[1] - rows[-1][1]) > 1e-7:
            rows.append(r)
    bm = part.bm

    def p3(a, b, c):
        return frame.p(a, b, c) if frame else Vector((a, b, c))

    def d3(a, b, c):
        return (frame.u * a + frame.v * b + frame.n * c) if frame else Vector((a, b, c))
    ctr = Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    rings = []
    for d, h in rows:
        pts = rrect(x0 + d, x1 - d, y0 + d, y1 - d, max(rc - d, 0.0005) if nc else 0.0, nc)
        rings.append([(bm.verts.new(p3(a, b, h)), Vector((a, b, h))) for a, b in pts])
    n = len(rings[0])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(n):
            j = (k + 1) % n
            q = [r0[k], r0[j], r1[j], r1[k]]
            loc = sum((e[1] for e in q), Vector()) / 4 - ctr
            face(part, [e[0] for e in q], d3(*loc))
    if caps[0]:
        face(part, [e[0] for e in rings[0]], d3(0, 0, -1))
    if caps[1]:
        face(part, [e[0] for e in rings[-1]], d3(0, 0, 1))


def loft(part, rings_2d, levels, P, caps=(True, True)):
    """Prism by layers (from M13): rings_2d[i] is the contour (the same number of points) at level
    levels[i]; P(a, b, c) -> point. The caps are n-gons; faces outward (recalc)."""
    bm = part.bm
    before = set(bm.faces)
    rings = [[bm.verts.new(P(a, b, c)) for a, b in poly] for poly, c in zip(rings_2d, levels)]
    n = len(rings[0])
    faces = []
    for i in range(len(rings) - 1):
        for k in range(n):
            j = (k + 1) % n
            faces.append(bm.faces.new([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]))
    if caps[0]:
        faces.append(bm.faces.new(rings[0][::-1]))
    if caps[1]:
        faces.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    part.tag([f for f in bm.faces if f not in before])
    return faces


def keycap(part, fr, a, b, wa, wb, h, top=0.8, n0=0.0):
    """Key on plane fr: base wa x wb, a smaller top (top is the fraction), height h from n0; no bottom."""
    def P(x, y, z):
        return fr.p(a + x, b + y, z)
    base = [(-wa / 2, -wb / 2), (wa / 2, -wb / 2), (wa / 2, wb / 2), (-wa / 2, wb / 2)]
    up = [(x * top, y * top) for x, y in base]
    return loft(part, [base, up], [n0, n0 + h], P, caps=(False, True))


def nail(part, c, n, r=0.0034, h=0.0018, sides=5):
    """Nail (screw) head on a surface with normal n: a ring at the board, a ring at 2/3 and the crown;
    the bottom is sunk 0.6 mm into the board (no gap)."""
    n = Vector(n).normalized()
    lathe(part, [(r, 0.0), (r * 0.7, h * 0.7), (0.0, h + 0.0006)], sides, Vector(c) - n * 0.0006, n)


def hexhead(part, c, n, r=0.0045, h=0.003, washer=0.0):
    """Bolt head (hexagon) on a surface with normal n; washer > 0 adds a washer under it."""
    n = Vector(n).normalized()
    c = Vector(c) - n * 0.0005
    if washer > 0:
        lathe(part, [(washer, 0.0), (washer, 0.0012), (0.0, 0.0012)], 6, c, n)
        c = c + n * 0.0012
    lathe(part, [(r, 0.0), (r, h), (0.0, h)], 6, c, n, phase=math.pi / 6)


def torus(part, fr, R, r, nu, nv, a0=0.0, a1=2 * math.pi):
    """Torus (or an arc of a torus from a0 to a1) in the (u, v) plane of system fr: R is the radius of
    the center line, r of the rod."""
    bm = part.bm
    full = abs(a1 - a0 - 2 * math.pi) < 1e-6
    cnt = nu if full else nu + 1
    rings = []
    for i in range(cnt):
        a = a0 + (a1 - a0) * i / nu
        d = fr.u * math.cos(a) + fr.v * math.sin(a)
        cc = fr.o + d * R
        rings.append([bm.verts.new(cc + d * (r * math.cos(2 * math.pi * k / nv)) + fr.n * (r * math.sin(2 * math.pi * k / nv)))
                      for k in range(nv)])
    for i in range(nu):
        r0, r1 = rings[i], rings[(i + 1) % cnt]
        a = a0 + (a1 - a0) * (i + 0.5) / nu
        mid = fr.o + (fr.u * math.cos(a) + fr.v * math.sin(a)) * R
        for k in range(nv):
            j = (k + 1) % nv
            q = [r0[k], r0[j], r1[j], r1[k]]
            face(part, q, sum((v.co for v in q), Vector()) / 4 - mid)
    if not full:
        for i, s in ((0, -1), (cnt - 1, 1)):
            a = a0 if i == 0 else a1
            t = -fr.u * math.sin(a) + fr.v * math.cos(a)
            face(part, rings[i], t * s)


def crimp_cap(part, c, r_hi, r_lo, h, n=12):
    """Crown cap: a skirt with corrugation (2n vertices alternating between r_hi and r_lo), a cap on top."""
    ribbed(part, c, "z", r_hi, r_lo, 0.0, h * 0.75, n, top=False)
    lathe(part, [(r_hi * 0.98, h * 0.75), (r_hi * 0.85, h), (0.0, h)], 2 * n, c, "z")


def corrugated_uv(part, x0, x1, z0, z1, yb, amp, period, seg, tile, crest_u, v0=0.0):
    """Corrugated sheet facing -y (a sine along x, the back at yb, crests at yb - amp) unwrapped for a
    vanilla sheet texture: tile - meters per tile, crest_u - where on the tile the crest is (a fraction
    of the wave); v0 - the bottom of the sheet on the tile. The part is fixed_uv, the UVMap layer is
    created here."""
    bm = part.bm
    uvl = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    n = max(1, int(round((x1 - x0) / period * seg)))
    cols = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        y = yb - amp * (1 - math.cos(2 * math.pi * (x - x0) / period)) / 2
        cols.append((x, bm.verts.new((x, y, z0)), bm.verts.new((x, y, z1))))
    # the geometry crest is at (x - x0) / period = 0.5; on the tile - at crest_u of the wave
    shift = (crest_u - 0.5) * period
    for i in range(n):
        xa, a0, a1 = cols[i]
        xb, b0, b1 = cols[i + 1]
        f = face(part, [a0, b0, b1, a1], (0, -1, 0))
        for lp in f.loops:
            co = lp.vert.co
            lp[uvl].uv = ((co.x - x0 + shift) / tile, v0 + (co.z - z0) / tile)
    return [(x0 + (k + 0.5) * period, yb - amp) for k in range(int((x1 - x0) / period))]


def box_uv(part, x0, x1, y0, y1, z0, z1, tile, u0=0.0, v0=0.0):
    """Box with an unwrap in meters (a part with a vanilla texture, the far LOD of the sheet): each face
    is a projection onto its own plane, tile meters per tile."""
    bm = part.bm
    uvl = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    new = g.box(part, x0, x1, y0, y1, z0, z1)
    for f in new:
        ax = max(range(3), key=lambda i: abs(f.normal[i]))
        ia, ib = [(1, 2), (0, 2), (0, 1)][ax]
        for lp in f.loops:
            co = lp.vert.co
            lp[uvl].uv = (u0 + (co[ia] - (x0, y0, z0)[ia]) / tile, v0 + (co[ib] - (x0, y0, z0)[ib]) / tile)
    return new
