"""M20 geometry that kgeo does not provide: smooth curves, a solid of revolution about any axis, sheets,
slabs with only the visible edges rounded, paper rolls with a hollow end, stacks of exercise books, an
inspection lamp. Partly as in M11 (m11_geo.py), copied here so that the models do not depend on each
other.
Blender axes: X is width, Y is depth (face toward -Y), Z is up.
"""
import math

import bmesh
from mathutils import Vector

import kgeo as g


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom)."""
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


def cable(part, pts, r, lod, k=3, sides=(8, 5)):
    """Cable through points: the near LOD is a smooth curve with sides[0] faces, farther - a polyline."""
    return g.pipe(part, spline(pts, k) if lod == 0 else pts, r, sides[0] if lod == 0 else sides[1])


def rod(part, a, b, r, sides):
    """Cylinder between points a and b."""
    return g.pipe(part, [tuple(a), tuple(b)], r, sides)


def face(part, verts, want):
    """Face from bmesh vertices, turned to look toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def basis(axis):
    """An axis and two axes perpendicular to it."""
    a = Vector(axis).normalized()
    ref = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    u = a.cross(ref).normalized()
    return a, u, a.cross(u).normalized()


def lathe(part, prof, sides, center, axis=(0, 0, 1), cap0=False, cap1=False, inward=False, phase=0.0):
    """Solid of revolution: prof [(r, h)] from the start to the end along axis from center (r = 0 is a pole);
    cap0 / cap1 close the start / end with a disc; inward - the surface faces the axis."""
    a, u, v = basis(axis)
    c0 = Vector(center)
    bm = part.bm
    angs = [phase + 2 * math.pi * k / sides for k in range(sides)]
    rings = []
    for r, h in prof:
        if r <= 1e-7:
            rings.append([bm.verts.new(c0 + a * h)])
        else:
            rings.append([bm.verts.new(c0 + a * h + (u * math.cos(t) + v * math.sin(t)) * r) for t in angs])
    new = []
    for i in range(len(rings) - 1):
        r0, r1 = rings[i], rings[i + 1]
        dr, dh = prof[i + 1][0] - prof[i][0], prof[i + 1][1] - prof[i][1]
        if len(r0) == 1 and len(r1) == 1:
            continue
        for k in range(sides):
            j = (k + 1) % sides
            if len(r0) == 1:
                q = [r0[0], r1[j], r1[k]]
            elif len(r1) == 1:
                q = [r0[k], r0[j], r1[0]]
            else:
                q = [r0[k], r0[j], r1[j], r1[k]]
            cen = sum((vv.co for vv in q), Vector()) / len(q) - c0
            rad = cen - a * cen.dot(a)
            rad = rad.normalized() if rad.length > 1e-9 else u
            n = rad * dh - a * dr
            new.append(face(part, q, -n if inward else n))
    if cap0 and len(rings[0]) > 1:
        new.append(face(part, rings[0], a if inward else -a))
    if cap1 and len(rings[-1]) > 1:
        new.append(face(part, rings[-1], -a if inward else a))
    part.tag(new)
    return new


def ring(part, center, axis, R, r, n, sides, phase=0.0):
    """Closed wire ring of radius R and rod r (lamp mesh)."""
    a, u, v = basis(axis)
    c = Vector(center)
    pts = [tuple(c + (u * math.cos(phase + 2 * math.pi * k / n) + v * math.sin(phase + 2 * math.pi * k / n)) * R)
           for k in range(n + 1)]
    return g.pipe(part, pts, r, sides)


def dome(part, center, axis, r, h, sides=6):
    """Domed head (screw plug, button, nail) of height h outward along axis."""
    return lathe(part, [(r, 0.0), (r * 0.78, h * 0.7), (0.0, h)], sides, center, axis)


def sheet(part, grid, t):
    """Sheet of thickness t over a grid of points grid[i][j]: front, back (offset along the grid normal), edges."""
    bm = part.bm
    ni, nj = len(grid), len(grid[0])
    G = [[Vector(p) for p in row] for row in grid]

    def nrm(i, j):
        du = G[min(i + 1, ni - 1)][j] - G[max(i - 1, 0)][j]
        dv = G[i][min(j + 1, nj - 1)] - G[i][max(j - 1, 0)]
        return du.cross(dv).normalized()
    top = [[bm.verts.new(G[i][j]) for j in range(nj)] for i in range(ni)]
    bot = [[bm.verts.new(G[i][j] - nrm(i, j) * t) for j in range(nj)] for i in range(ni)]
    new = []
    for i in range(ni - 1):
        for j in range(nj - 1):
            new.append(bm.faces.new([top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1]]))
            new.append(bm.faces.new([bot[i][j + 1], bot[i + 1][j + 1], bot[i + 1][j], bot[i][j]]))
    border = ([(i, 0) for i in range(ni)] + [(ni - 1, j) for j in range(1, nj)] +
              [(i, nj - 1) for i in range(ni - 2, -1, -1)] + [(0, j) for j in range(nj - 2, 0, -1)])
    for k in range(len(border)):
        (a, b), (c, d) = border[k], border[(k + 1) % len(border)]
        new.append(bm.faces.new([top[a][b], bot[a][b], bot[c][d], top[c][d]]))
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def open_box(part, x0, x1, y0, y1, z0, z1, t, frame=None):
    """Open-top box: bottom and four walls of thickness t."""
    g.box(part, x0, x1, y0, y1, z0, z0 + t, frame=frame)
    g.box(part, x0, x1, y0, y0 + t, z0 + t, z1, frame=frame)
    g.box(part, x0, x1, y1 - t, y1, z0 + t, z1, frame=frame)
    g.box(part, x0, x0 + t, y0 + t, y1 - t, z0 + t, z1, frame=frame)
    g.box(part, x1 - t, x1, y0 + t, y1 - t, z0 + t, z1, frame=frame)


def flap(part, x0, x1, y_hinge, z_hinge, length, deg, t, side=-1, sag=0.0, frame=None):
    """Box flap: hinge along x at (y_hinge, z_hinge), opened outward (side is the sign of y) by deg from
    vertical; sag is the sag of the middle (cardboard is soft). frame - the local axes of the box."""
    a = math.radians(deg)
    dy, dz = side * math.sin(a) * length, math.cos(a) * length
    grid = []
    for s in (0.0, 0.35, 0.7, 1.0):
        bend = sag * math.sin(math.pi * s)
        row = [(x, y_hinge + dy * s - side * bend * math.cos(a), z_hinge + dz * s - bend * math.sin(a))
               for x in (x0, (x0 + x1) / 2, x1)]
        grid.append([tuple(frame.p(*p)) if frame else p for p in row])
    return sheet(part, grid, t)


def frame_z(cx, cy, deg, z):
    """Local axes on the shelf: u at angle deg from +x, v across, n up."""
    a = math.radians(deg)
    return g.Frame((cx, cy, z), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))


def frame_lean(cx, cy, z, deg):
    """Axes at the bottom edge at (cx, cy, z), tilted sideways about y by deg (a folder falls to the right
    when deg > 0): u across, v along the depth, n up along the folder."""
    a = math.radians(deg)
    return g.Frame((cx, cy, z), (math.cos(a), 0, -math.sin(a)), (0, 1, 0), (math.sin(a), 0, math.cos(a)))


# --- body slabs ---------------------------------------------------------------------------
def box_bev(part, x0, x1, y0, y1, z0, z1, r, seg, pick):
    """Slab with only the visible edges rounded: pick(a, b) says whether to take the edge with ends a, b (in
    world coordinates). The other edges are sharp - they are in joints and not visible."""
    bm = part.bm
    before = set(bm.faces)
    ret = bmesh.ops.create_cube(bm, size=1.0)
    vs = ret["verts"]
    for v in vs:
        v.co = Vector((x0 + (v.co.x + 0.5) * (x1 - x0), y0 + (v.co.y + 0.5) * (y1 - y0), z0 + (v.co.z + 0.5) * (z1 - z0)))
    edges = [e for e in {e for v in vs for e in v.link_edges} if pick(e.verts[0].co, e.verts[1].co)]
    if r > 0 and seg > 0 and edges:
        g.bevel(bm, edges, r, seg)
    faces = [f for f in bm.faces if f not in before]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    bm.normal_update()
    return part.tag(faces)


def retag(part, region, faces):
    """Faces `faces` go into region `region` (name, kind, scale): the front edge of a slab, notebook pages."""
    idx = part.region_index(*region)
    for f in faces:
        f[part.reg] = idx


def kill(part, faces):
    """Remove faces (covered by neighbours: their place in the atlas would land on visible ones)."""
    if faces:
        bmesh.ops.delete(part.bm, geom=list(faces), context="FACES")


# --- paper rolls --------------------------------------------------------------------------------
def _axes(axis):
    """Axis, "side" and "up" of the section: up is the projection of
    the world vertical (the roll is flattened along it)."""
    a = Vector(axis).normalized()
    up = Vector((0, 0, 1)) - a * a.z
    if up.length < 1e-4:
        up = Vector((0, 1, 0)) - a * a.y
    up.normalize()
    return a, up.cross(a).normalized(), up


def _ring(bm, c, side, up, r, sq, n, phase):
    return [bm.verts.new(c + side * (r * math.cos(phase + 2 * math.pi * k / n)) +
                         up * (r * sq * math.sin(phase + 2 * math.pi * k / n))) for k in range(n)]


def paper_roll(parts, a, b, r, n, ends=(True, True), hole=0.40, depth=0.03, squash=1.0, phase=0.0, simple=False):
    """Paper roll from a to b, radius r, n faces around; squash - flattened vertically (lies under others).
    parts - (side, ends, holes): the side is its own part for each roll (in the atlas the sides of rolls in
    a heap do not overlap, the shading is right), the ends and holes are shared parts of the heap (an even
    colour: they can share atlas space). The end is a ring of paper layers, inside is a dark funnel of the
    given depth (the roll is wound without a core); ends - which ends are visible (a wall end has none).
    simple - flat ends without a hole (middle LOD). The vertices of each part are its own."""
    a, b = Vector(a), Vector(b)
    ax, side, up = _axes(b - a)
    sp, ep, hp = parts
    new = []
    R0 = _ring(sp.bm, a, side, up, r, squash, n, phase)
    R1 = _ring(sp.bm, b, side, up, r, squash, n, phase)
    for k in range(n):
        j = (k + 1) % n
        q = [R0[k], R0[j], R1[j], R1[k]]
        c = sum((v.co for v in q), Vector()) / 4 - a
        new.append(face(sp, q, c - ax * c.dot(ax)))
    sp.tag(new)
    for which, c, sgn in ((0, a, -1.0), (1, b, 1.0)):
        if not ends[which]:
            continue
        out = ax * sgn
        rr = _ring(ep.bm, c, side, up, r, squash, n, phase)
        if simple:
            ep.tag([face(ep, rr, out)])
            continue
        inner = _ring(ep.bm, c, side, up, r * hole, squash, n, phase)
        ep.tag([face(ep, [rr[k], rr[(k + 1) % n], inner[(k + 1) % n], inner[k]], out) for k in range(n)])
        ring_h = _ring(hp.bm, c, side, up, r * hole, squash, n, phase)
        tip = hp.bm.verts.new(c - out * depth)
        nf = []
        for k in range(n):
            q = [ring_h[k], ring_h[(k + 1) % n], tip]
            cc = sum((v.co for v in q), Vector()) / 3 - c
            nf.append(face(hp, q, out - (cc - ax * cc.dot(ax)) * 4.0))
        hp.tag(nf)


def band(part, c, axis, r, w, n, squash=1.0, phase=0.0, t=0.0013):
    """Rubber band or string on a roll: a ring slightly thicker than the roll, edges bevelled."""
    ax, side, up = _axes(axis)
    c = Vector(c)
    bm = part.bm
    prof = [(r - 0.0006, -w / 2 - 0.0009), (r + t, 0.0), (r - 0.0006, w / 2 + 0.0009)]
    rings = [_ring(bm, c + ax * h, side, up, rr, squash, n, phase) for rr, h in prof]
    new = []
    for i in range(len(rings) - 1):
        for k in range(n):
            j = (k + 1) % n
            q = [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]
            cc = sum((v.co for v in q), Vector()) / 4 - c
            new.append(face(part, q, cc - ax * cc.dot(ax)))
    return part.tag(new)


# --- exercise books -----------------------------------------------------------------------
def notebooks(part, covers, pages, cx, cy, z, n, rnd, w=0.17, d=0.205, t=0.009, rot=7.0):
    """Stack of general notebooks: each is a bar with a cover on top and a spine, the pages are three ends
    (the spine of each faces its own way). The top and bottom are covered by neighbours - they have no faces
    (otherwise in the atlas they would land on the visible cover of the upper one); only the top one has a
    top. Returns the height of the top of the stack."""
    bm = part.bm
    for i in range(n):
        fr = frame_z(cx + rnd.uniform(-0.006, 0.006), cy + rnd.uniform(-0.006, 0.006), rnd.uniform(-rot, rot),
                     z + i * t)
        part.use(*covers[(i * 7 + n) % len(covers)])
        fs = g.box(part, -w / 2, w / 2, -d / 2, d / 2, 0.0, t * 0.98, frame=fr)
        spine = rnd.choice((fr.u, -fr.u, -fr.v, -fr.v, -fr.v))
        drop, pg = [], []
        for f in fs:
            nz = f.normal.dot(fr.n)
            if nz < -0.7 or (nz > 0.7 and i < n - 1):
                drop.append(f)
            elif abs(nz) <= 0.7 and f.normal.dot(spine) < 0.7:
                pg.append(f)
        retag(part, pages, pg)
        kill(part, drop)
    bm.normal_update()
    return z + n * t


# --- jar with bolts ----------------------------------------------------------------------------
def hex_bolt(part, head_c, axis, d, length, lod):
    """Bolt: a hexagonal head d (across flats) and a shaft, axis from the head to the end."""
    a = Vector(axis).normalized()
    h = Vector(head_c)
    s = 6
    g.pipe(part, [tuple(h - a * d * 0.33), tuple(h + a * d * 0.33)], d * 0.55, s)
    if lod == 0:
        g.pipe(part, [tuple(h + a * d * 0.33), tuple(h + a * (d * 0.33 + length))], d * 0.34, s)
