"""M11 geometry that kgeo does not provide: solids of revolution about any axis, smooth curves, cardboard
sheets and boxes, crocodile clips, screws. Blender axes: X is width, Y is depth (face toward -Y), Z is up.
"""
import math

import bmesh
from mathutils import Vector

import kgeo as g


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, as in M04 and M16)."""
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
    """Cable through points: the near LOD is a smooth spline with sides[0] faces, farther LODs are a
    polyline with sides[1]."""
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
    """Solid of revolution: prof [(r, h)] is the outer profile from the start to the end along axis from
    center (r = 0 is a pole, faces meet in a point); cap0 / cap1 close the start / end with a disc; inward -
    the surface faces the axis (inside of a cup). Faces follow the profile normal: up the axis = outward."""
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
    """Closed wire ring of radius R and rod radius r (lamp mesh, fan grille)."""
    a, u, v = basis(axis)
    c = Vector(center)
    pts = [tuple(c + (u * math.cos(phase + 2 * math.pi * k / n) + v * math.sin(phase + 2 * math.pi * k / n)) * R)
           for k in range(n + 1)]
    return g.pipe(part, pts, r, sides)


def screw(part, center, axis, r, h, sides=8):
    """Screw head: domed cap of height h, outward along axis."""
    return lathe(part, [(r, 0.0), (r, h * 0.35), (r * 0.72, h * 0.85), (0.0, h)], sides, center, axis)


def sheet(part, grid, t):
    """Sheet of thickness t over a grid of points grid[i][j] (i along, j across): front face, back face
    (offset along the grid normal) and edges. Tarpaulin, box flaps."""
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


def flap(part, x0, x1, y_hinge, z_hinge, length, deg, t, side=-1, sag=0.0):
    """Box flap: hinge along x at (y_hinge, z_hinge), opened outward (side is the sign of y) by deg
    from vertical; sag is the sag of the middle (cardboard is soft)."""
    a = math.radians(deg)
    dy, dz = side * math.sin(a) * length, math.cos(a) * length
    grid = []
    for s in (0.0, 0.35, 0.7, 1.0):
        bend = sag * math.sin(math.pi * s)
        grid.append([(x, y_hinge + dy * s - side * bend * math.cos(a), z_hinge + dz * s - bend * math.sin(a))
                     for x in (x0, (x0 + x1) / 2, x1)])
    return sheet(part, grid, t)


def box_to(part, a, b, w, h, up=(0, 0, 1)):
    """Bar from point a to point b with cross-section w (across) x h (along up)."""
    a, b = Vector(a), Vector(b)
    u = (b - a).normalized()
    n = Vector(up) - u * Vector(up).dot(u)
    n.normalize()
    v = n.cross(u)
    fr = g.Frame(a, u, v, n)
    return g.box(part, 0.0, (b - a).length, -w / 2, w / 2, -h / 2, h / 2, frame=fr)


def frame_z(cx, cy, deg, z):
    """Local axes on the table: u at angle deg from +x, v across, n up."""
    a = math.radians(deg)
    return g.Frame((cx, cy, z), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))


# 50 mm crocodile clip (as in M16): profile of the upper jaw (a from tip to tail, c up) and the cap
CLIP_PROF = [(0.0, 0.0006), (0.008, 0.0009), (0.017, 0.0012), (0.023, 0.0028), (0.030, 0.0042), (0.042, 0.0066),
             (0.050, 0.0082)]
CLIP_BOOT = [(0.027, 0.0040, 0.0044), (0.031, 0.0048, 0.0058), (0.042, 0.0050, 0.0064), (0.052, 0.0046, 0.0058),
             (0.058, 0.0032, 0.0036), (0.061, 0.0022, 0.0023)]
CLIP_LOW = 0.0086                    # jaw/cap bottom below the axis (the clip lies on the table)


def croc(jaw, boot, fr, lod, k=1.0):
    """Crocodile clip ~50 x k mm: two jaws from a strip (tips closed, spreading at the rivet, tails
    spread by the spring), rivet with spring, soft cap on the tail. fr: origin at the jaw tips,
    u toward the tail, n up (jaws open along n), v across. The cap tail is fr.p(0.061 k, 0, 0):
    the wire leaves there. No teeth: 0.7 mm is invisible from a metre and would triple the triangles."""
    prof = CLIP_PROF[::2] if lod == 0 else CLIP_PROF[::3]
    for s in (1, -1):
        g.sweep(jaw, [fr.p(a * k, 0.0, s * c * k) for a, c in prof], fr.v, 0.0003 * k, 0.0030 * k)
    if lod == 0:
        g.cyl(jaw, (0.0255 * k, 0.0, 0.0), "y", 0.0019 * k, 0.0074 * k, 6, frame=fr)         # rivet with spring
    sec = CLIP_BOOT[::2] + [CLIP_BOOT[-1]]
    g.tube_var(boot, [fr.p(a * k, 0.0, 0.0) for a, _, _ in sec], [(rb * k, rc * k) for _, rb, rc in sec],
               8 if lod == 0 else 5)
    return fr.p(0.061 * k, 0.0, 0.0)


def knurl_ring(part, center, axis, r, h, n, depth):
    """Knurled ring (lamp nut, knob): 2n ribs around, every other one recessed by depth."""
    a, u, v = basis(axis)
    c = Vector(center)
    poly = []
    for k in range(2 * n):
        t = math.pi * k / n
        rr = r - depth * (k % 2)
        poly.append(c + (u * math.cos(t) + v * math.sin(t)) * rr)
    bm = part.bm
    bot = [bm.verts.new(p - a * (h / 2)) for p in poly]
    top = [bm.verts.new(p + a * (h / 2)) for p in poly]
    new = [face(part, bot, -a), face(part, top, a)]
    m = len(poly)
    for i in range(m):
        j = (i + 1) % m
        q = [bot[i], bot[j], top[j], top[i]]
        cen = sum((vv.co for vv in q), Vector()) / 4 - c
        new.append(face(part, q, cen - a * cen.dot(a)))
    part.tag(new)
    return new
