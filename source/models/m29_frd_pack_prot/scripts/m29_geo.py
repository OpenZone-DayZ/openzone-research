"""M29 geometry that kgeo does not have: solids of revolution along any axis, plates with rounded
corners and edges, a bent polyline with radii at the bends (tubes, handles, brackets), hexagons,
rivets, a torus, a clamp, a fan impeller. It is a copy of m25_geo.py of M25 (the same "Protection"
line; part of it is from M07 and M13), so as not to depend on another model's file. Added: a solid of
revolution with an elliptical section (lathe_f), placing a vanilla item by
the origin of its p3d and a point in its axes (the GP-5 mask on the mannequin, a hose in place of the
filter), the group rotation in the preview of the "working" pose (the gauge needle; like install_pose
in M84 - the kit is untouched). The parts are kgeo.Part, faces point outward (kexport flips them for
p3d itself).

Blender axes: X is width, Y is depth (the face looks to -Y), Z is up.
"""
import math

import bmesh
from mathutils import Matrix, Vector

import kgeo as g
import kvanilla as kv


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


def fillet(pts, r, n):
    """Polyline -> the same polyline with an arc of radius r (n segments) at every bend: a bent pipe, a
    rod, a bar handle. The arc is shorter than half of the adjacent segments."""
    P = [Vector(p) for p in pts]
    out = [P[0]]
    for i in range(1, len(P) - 1):
        a, b, c = P[i - 1], P[i], P[i + 1]
        d1, d2 = (b - a).normalized(), (c - b).normalized()
        ang = math.acos(max(-1.0, min(1.0, d1.dot(d2))))
        if ang < 1e-3:
            out.append(b)
            continue
        t = min(r * math.tan(ang / 2), (b - a).length * 0.5, (c - b).length * 0.5)
        rr = t / math.tan(ang / 2)
        p1 = b - d1 * t
        side = (d2 - d1 * d1.dot(d2)).normalized()
        cen = p1 + side * rr
        v1 = p1 - cen
        ax = v1.cross((b + d2 * t) - cen).normalized()
        for k in range(n + 1):
            out.append(cen + Matrix.Rotation(ang * k / n, 3, ax) @ v1)
    out.append(P[-1])
    return [tuple(p) for p in out]


def basis(axis):
    """Axis (from M07): (a, b, w) - two transverse unit vectors and the longitudinal one; axis is "x",
    "-y", ... or a vector."""
    if isinstance(axis, str):
        w = Vector([1.0 if c == axis[-1] else 0.0 for c in "xyz"]) * (-1.0 if axis.startswith("-") else 1.0)
    else:
        w = Vector(axis).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(w.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    a = ref.cross(w).normalized()
    return a, w.cross(a).normalized(), w


def lathe(part, prof, sides, center, axis="z", closed=False, caps=(False, False), phase=0.0, inward=False):
    """Solid of revolution (from M07): prof [(r, h)] - the section (r from the axis, h along axis from
    center), traversed along the outer surface in the direction of growing h: faces look outward (inward
    - toward the axis: the inside of a casing). r = 0 is a point on the axis (a fan). caps - caps of the
    first and last ring."""
    a, b, w = basis(axis)
    c = Vector(center)
    bm = part.bm
    angs = [phase + 2 * math.pi * k / sides for k in range(sides)]
    rings = []
    for r, h in prof:
        if r < 1e-7:
            rings.append(bm.verts.new(c + w * h))
        else:
            rings.append([bm.verts.new(c + (a * math.cos(t) + b * math.sin(t)) * r + w * h) for t in angs])
    idx = list(range(len(prof))) + ([0] if closed else [])
    new = []
    sg = -1.0 if inward else 1.0
    for i0, i1 in zip(idx, idx[1:]):
        (r0, h0), (r1, h1) = prof[i0], prof[i1]
        nr, nh = h1 - h0, -(r1 - r0)
        R0, R1 = rings[i0], rings[i1]
        for k in range(sides):
            j = (k + 1) % sides
            tm = angs[k] + math.pi / sides
            want = ((a * math.cos(tm) + b * math.sin(tm)) * nr + w * nh) * sg
            if isinstance(R0, list) and isinstance(R1, list):
                vs = [R0[k], R0[j], R1[j], R1[k]]
            elif isinstance(R0, list):
                vs = [R0[k], R0[j], R1]
            elif isinstance(R1, list):
                vs = [R0, R1[j], R1[k]]
            else:
                continue
            new.append(face(part, vs, want))
    for cap, i, o in ((caps[0], 0, 1), (caps[1], len(prof) - 1, len(prof) - 2)):
        if cap and isinstance(rings[i], list):
            new.append(face(part, rings[i], w * (1.0 if prof[i][1] > prof[o][1] else -1.0)))
    return new


def lathe_f(part, prof, sides, frame, caps=(False, False), kv_=1.0, kn=1.0):
    """Solid of revolution around axis u of system frame with an elliptical section (r*kv_ along v, r*kn
    along n): the mannequin head, the helmet sides. prof [(r, h)], r = 0 is a
    point on the axis."""
    bm = part.bm
    rings = []
    for r, h in prof:
        if r < 1e-7:
            rings.append(bm.verts.new(frame.p(h, 0.0, 0.0)))
        else:
            rings.append([bm.verts.new(frame.p(h, r * kv_ * math.cos(2 * math.pi * k / sides),
                                               r * kn * math.sin(2 * math.pi * k / sides))) for k in range(sides)])
    new = []
    for i in range(len(rings) - 1):
        R0, R1 = rings[i], rings[i + 1]
        for k in range(sides):
            j = (k + 1) % sides
            if isinstance(R0, list) and isinstance(R1, list):
                q = [R0[k], R0[j], R1[j], R1[k]]
            elif isinstance(R0, list):
                q = [R0[k], R0[j], R1]
            elif isinstance(R1, list):
                q = [R0, R1[j], R1[k]]
            else:
                continue
            c = sum((v.co for v in q), Vector()) / len(q)
            ax = frame.o + frame.u * (c - frame.o).dot(frame.u)
            out = c - ax
            if out.length < 1e-9:
                out = frame.u * (1.0 if i > 0 else -1.0)
            new.append(face(part, q, out))
    for cap, i, s in ((caps[0], 0, -1.0), (caps[1], len(rings) - 1, 1.0)):
        if cap and isinstance(rings[i], list):
            new.append(face(part, rings[i], frame.u * s))
    bm.normal_update()
    return new


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
    new = []
    n = len(rings[0])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(n):
            j = (k + 1) % n
            q = [r0[k], r0[j], r1[j], r1[k]]
            loc = sum((e[1] for e in q), Vector()) / 4 - ctr
            new.append(face(part, [e[0] for e in q], d3(*loc)))
    if caps[0]:
        new.append(face(part, [e[0] for e in rings[0]], d3(0, 0, -1)))
    if caps[1]:
        new.append(face(part, [e[0] for e in rings[-1]], d3(0, 0, 1)))
    return new


def rivet(part, c, n, r=0.004, h=0.0025, sides=6):
    """Rivet or a round-head screw on a surface with normal n (the bottom is sunk 0.6 mm into the sheet)."""
    n = Vector(n).normalized()
    lathe(part, [(r, 0.0), (r * 0.72, h * 0.70), (0.0, h + 0.0006)], sides, Vector(c) - n * 0.0006, n)


def hex_prism(part, center, axis, s, h, phase=0.0):
    """Hexagon (nut, bolt head): s is the width across flats, h the height, center the middle."""
    R = s / math.sqrt(3.0)
    lathe(part, [(R, -h / 2), (R, h / 2)], 6, center, axis, caps=(True, True), phase=phase + math.pi / 6)


def torus(part, fr, R, r, nu, nv, squash=1.0):
    """Torus in the (u, v) plane of system fr: R is the radius of the center line, r of the rod; squash
    flattens it along n."""
    bm = part.bm
    rings = []
    for i in range(nu):
        a = 2 * math.pi * i / nu
        d = fr.u * math.cos(a) + fr.v * math.sin(a)
        c = fr.o + d * R
        rings.append([bm.verts.new(c + d * (r * math.cos(2 * math.pi * k / nv)) +
                                   fr.n * (r * squash * math.sin(2 * math.pi * k / nv))) for k in range(nv)])
    for i in range(nu):
        r0, r1 = rings[i], rings[(i + 1) % nu]
        a = 2 * math.pi * (i + 0.5) / nu
        mid = fr.o + (fr.u * math.cos(a) + fr.v * math.sin(a)) * R
        for k in range(nv):
            j = (k + 1) % nv
            q = [r0[k], r0[j], r1[j], r1[k]]
            face(part, q, sum((v.co for v in q), Vector()) / 4 - mid)


def axis_frame(c, axis):
    """System with origin c: u, v across the axis, n along it."""
    a, b, w = basis(axis)
    return g.Frame(c, a, b, w)


def hose_clamp(part, c, axis, r, w=0.009, sides=12, lod=0):
    """Worm-drive clamp on a hose of radius r: a band, the worm housing and the screw on the side (along a)."""
    a, b, ww = basis(axis)
    rb = r + 0.0012
    lathe(part, [(rb, -w / 2), (rb, w / 2)], sides, c, axis)
    if lod > 0:
        return
    hc = Vector(c) + a * (rb + 0.0028)
    g.box(part, -w / 2 - 0.0008, w / 2 + 0.0008, -0.0065, 0.0065, -0.0028, 0.0028, frame=g.Frame(hc, ww, b, a))
    lathe(part, [(0.0026, -0.0055), (0.0026, 0.0055)], 6, hc + a * 0.0006 + b * 0.0085, b, caps=(True, True))


def handwheel(part, c, axis, R, r, spokes=3, hub_r=0.008, hub_h=0.014, nu=18, nv=6):
    """Valve handwheel: rim, hub, spokes."""
    a, b, w = basis(axis)
    torus(part, g.Frame(c, a, b, w), R, r, nu, nv)
    lathe(part, [(hub_r, -hub_h / 2), (hub_r * 0.85, hub_h / 2)], 8, c, axis, caps=(True, True))
    for k in range(spokes):
        t = 2 * math.pi * (k + 0.25) / spokes
        d = a * math.cos(t) + b * math.sin(t)
        g.pipe(part, [tuple(Vector(c) + d * hub_r * 0.7), tuple(Vector(c) + d * (R - r * 0.4) - w * 0.004)],
               r * 0.75, 5)


def fan(part, c, axis, R, hub_r, blades, chord, pitch_deg, t=0.0022, lod=0):
    """Engine fan impeller: a hub and flat blades at an angle of attack."""
    a, b, w = basis(axis)
    lathe(part, [(hub_r, -0.010), (hub_r, 0.006), (hub_r * 0.6, 0.010)], 12 if lod == 0 else 6, c, axis,
          caps=(True, True))
    p = math.radians(pitch_deg)
    for k in range(blades):
        th = 2 * math.pi * k / blades
        d = a * math.cos(th) + b * math.sin(th)
        tg = w.cross(d).normalized()
        u = tg * math.cos(p) + w * math.sin(p)
        nrm = d.cross(u).normalized()
        L = R - hub_r * 0.8
        fr = g.Frame(Vector(c) + d * (hub_r * 0.8 + L / 2), d, u, nrm)
        g.box(part, -L / 2, L / 2, -chord / 2, chord / 2, -t / 2, t / 2, frame=fr)


def frame_z(cx, cy, deg, z):
    """System of an item lying on a horizontal support: u along the item at angle deg from +X, v across,
    n up."""
    a = math.radians(deg)
    return g.Frame((cx, cy, z), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))


def rod(part, a, b, r, sides):
    """Cylinder between points a and b."""
    return g.pipe(part, [tuple(a), tuple(b)], r, sides)


def bar(part, a, b, w, h, up=(0.0, 0.0, 1.0)):
    """Bar from point a to point b with section w (across) x h (along up)."""
    a, b = Vector(a), Vector(b)
    u = (b - a).normalized()
    n = Vector(up) - u * Vector(up).dot(u)
    n.normalize()
    v = n.cross(u)
    return g.box(part, 0.0, (b - a).length, -w / 2, w / 2, -h / 2, h / 2, frame=g.Frame(a, u, v, n))


# --- vanilla item by the origin of its p3d (not by the extent, like kvanilla.put) ----------------------
def vanilla_at(key, origin, up, fwd, lods=(0, 1)):
    """A decor entry for kmodel.Model: the item's p3d origin at point origin, the item's +Y is up, +Z is
    fwd. The extent is read at once: kvanilla remembers it, and --uv-hash passes it to the bakery (which
    has no P: drive)."""
    kv.box(key)
    return (kv.path(key), tuple(origin), tuple(up), tuple(fwd), tuple(lods), key)


def vanilla_point(local, origin, up, fwd):
    """A point in the item's p3d axes (x, y, z) -> Blender."""
    return Vector(kv.to_blender(local, origin, up, fwd))


def vanilla_dir(local, up, fwd):
    """A direction in the item's p3d axes -> Blender."""
    return Vector(kv.to_blender(local, (0.0, 0.0, 0.0), up, fwd))


# --- "working" pose in the preview: group rotation ------------------------------------------------------
def rot_about(point, axis, angle):
    """Rotation matrix by angle about the given axis through the given point (as in M84)."""
    p = Vector(point)
    return Matrix.Translation(p) @ Matrix.Rotation(angle, 4, Vector(axis)) @ Matrix.Translation(-p)


def install_pose():
    """krender.place_look and krender.place: the look's move - group -> a shift (as in the kit) or a 4x4
    matrix (rotation about an axis). For the preview and renders only: in the p3d the pose is set by
    model.cfg. As in M84 and M06."""
    import krender
    if getattr(krender.place_look, "_m29_pose", False):
        return
    orig_look, orig_place = krender.place_look, krender.place

    def split(move):
        move = dict(move or {})
        return ({k: v for k, v in move.items() if isinstance(v, Matrix)},
                {k: v for k, v in move.items() if not isinstance(v, Matrix)} or None)

    def pose(parts, obs, mats):
        for p, ob in zip(parts, obs):
            if p.group in mats:
                ob.matrix_world = mats[p.group] @ ob.matrix_world

    def place_look(parts, kind_table, origin, remap=None, glow=1.5, sharp_deg=40.0, panels=None, move=None):
        mats, shifts = split(move)
        obs = orig_look(parts, kind_table, origin, remap=remap, glow=glow, sharp_deg=sharp_deg, panels=panels,
                        move=shifts)
        pose(parts, obs, mats)
        return obs

    def place(parts, tag, offset, mats_, sharp_deg=40.0, move=None):
        mats, shifts = split(move)
        obs = orig_place(parts, tag, offset, mats_, sharp_deg=sharp_deg, move=shifts)
        pose(parts, obs, mats)
        return obs
    place_look._m29_pose = True
    krender.place_look, krender.place = place_look, place
