"""Primitives of M31 that kgeo lacks: roundings, solids of revolution, lofts through sections,
the coiled handset cord. Some come from the M38 generators (rrect, fillet_poly, inset2,
bulge_rr, keycap, button) and from M16 (ribbon); the kit is left alone.

Blender axes: X - width, Y - depth (front at -Y), Z - up.
"""
import math

import bmesh
import kgeo as g
from mathutils import Vector


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, from M24)."""
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


def face(part, verts, want):
    """Face from bmesh vertices, flipped to look toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def closed(part, faces):
    """Normals of a closed solid point outward."""
    bmesh.ops.recalc_face_normals(part.bm, faces=faces)
    return part.tag(faces)


def turn(cx, cy, z, deg):
    """Local axes rotated about the vertical: u along the object, v across it, n up."""
    a = math.radians(deg)
    return g.Frame((cx, cy, z), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))


def lathe(part, prof, sides, center, axis=(0, 0, 1), cap0=False, cap1=False, a0=0.0, frame=None):
    """Solid of revolution: prof [(r, h)] along the axis from center; the profile goes around the
    section counterclockwise (r to the right, h up), so (dh, -dr) points outward; cap0 / cap1 -
    close the first / last ring. frame - center and axis are in local axes.
    """
    bm = part.bm
    w = Vector(axis).normalized()
    c0 = Vector(center)
    if frame is not None:
        c0 = frame.p(*c0)
        w = (frame.u * w.x + frame.v * w.y + frame.n * w.z).normalized()
    ref = Vector((0, 0, 1)) if abs(w.z) < 0.9 else Vector((1, 0, 0))
    u = w.cross(ref).normalized()
    v = w.cross(u).normalized()

    def rad(a):
        return u * math.cos(a) + v * math.sin(a)
    rings = [[bm.verts.new(c0 + w * h + rad(a0 + 2 * math.pi * k / sides) * r) for k in range(sides)] for r, h in prof]
    new = []
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        if r0 < 1e-7 and r1 < 1e-7:
            continue
        for k in range(sides):
            j = (k + 1) % sides
            want = rad(a0 + 2 * math.pi * (k + 0.5) / sides) * (h1 - h0) - w * (r1 - r0)
            new.append(face(part, [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]], want))
    if cap0:
        new.append(face(part, rings[0], -w))
    if cap1:
        new.append(face(part, rings[-1], w))
    return part.tag(new)


def round_prof(r_out, h0, h1, r_edge, k=2, top=True, bottom=False):
    """Disc profile (r, h) with a rounded edge of radius r_edge on top (and on the bottom)."""
    pts = []
    if bottom:
        for i in range(k + 1):
            a = math.pi / 2 * i / k
            pts.append((r_out - r_edge + r_edge * math.sin(a), h0 + r_edge - r_edge * math.cos(a)))
    else:
        pts.append((r_out, h0))
    if top:
        for i in range(k + 1):
            a = math.pi / 2 * i / k
            pts.append((r_out - r_edge + r_edge * math.cos(a), h1 - r_edge + r_edge * math.sin(a)))
    else:
        pts.append((r_out, h1))
    return pts


def rrect(cx, cy, w, h, r, k):
    """Rounded rectangle, counterclockwise: 4 corners of k + 1 points each."""
    r = max(1e-4, min(r, w / 2 - 1e-4, h / 2 - 1e-4))
    pts = []
    for sx, sy, a in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        ccx, ccy = cx + sx * (w / 2 - r), cy + sy * (h / 2 - r)
        for i in range(k + 1):
            t = math.radians(a + 90.0 * i / max(k, 1))
            pts.append((ccx + r * math.cos(t), ccy + r * math.sin(t)))
    return pts


def fillet_poly(poly, radii, k=3):
    """Polygon [(a, b)] with rounded corners (the radius of corner i is radii[i], 0 - sharp)."""
    out = []
    n = len(poly)
    for i in range(n):
        r = radii[i]
        p = Vector(poly[i])
        if r <= 0:
            out.append((p.x, p.y))
            continue
        a, b = Vector(poly[i - 1]), Vector(poly[(i + 1) % n])
        d1, d2 = (a - p).normalized(), (b - p).normalized()
        ang = math.acos(max(-1.0, min(1.0, d1.dot(d2))))
        t = min(r / math.tan(ang / 2), (a - p).length * 0.45, (b - p).length * 0.45)
        rr = t * math.tan(ang / 2)
        p1, p2 = p + d1 * t, p + d2 * t
        c = p + (d1 + d2).normalized() * (rr / math.sin(ang / 2))
        a1, a2 = math.atan2(p1.y - c.y, p1.x - c.x), math.atan2(p2.y - c.y, p2.x - c.x)
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for s in range(k + 1):
            q = a1 + da * s / k
            out.append((c.x + rr * math.cos(q), c.y + rr * math.sin(q)))
    return out


def inset2(prof, d):
    """Convex polygon moved inward by d (along the corner bisectors; d < 0 - outward)."""
    n = len(prof)
    area = sum(prof[i][0] * prof[(i + 1) % n][1] - prof[(i + 1) % n][0] * prof[i][1] for i in range(n))
    s = 1.0 if area > 0 else -1.0
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(prof[i - 1]), Vector(prof[i]), Vector(prof[(i + 1) % n])
        e1, e2 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n1, n2 = Vector((-e1.y, e1.x)) * s, Vector((-e2.y, e2.x)) * s
        b = n1 + n2
        b = n1 if b.length < 1e-9 else b.normalized()
        q = p1 + b * (d / max(0.3, b.dot(n1)))
        out.append((q.x, q.y))
    return out


AX = {"x": (1, 2, 0), "y": (0, 2, 1), "z": (0, 1, 2)}       # extrusion axis -> (a, b, c axes)


def loft(part, prof, axis, stations, frame=None, cap0=True, cap1=True):
    """Convex section prof [(a, b)] along axis ("x": a = y, b = z; "y": a = x, b = z; "z": a = x,
    b = y) through stations [(c, inset)] - a solid with rounded or chamfered ends. frame - local
    axes (u, v, n instead of x, y, z). cap0 / cap1: True - the end is closed, False - open, a
    number - only a ring of that width (an end hidden inside another part: no atlas space is
    spent).
    """
    ia, ib, ic = AX[axis]
    bm = part.bm

    def P(a, b, c):
        q = [0.0, 0.0, 0.0]
        q[ia], q[ib], q[ic] = a, b, c
        return frame.p(*q) if frame else Vector(q)
    rings = []
    for c, d in stations:
        ring = inset2(prof, d) if abs(d) > 1e-9 else prof
        rings.append([bm.verts.new(P(a, b, c)) for a, b in ring])
    n = len(prof)
    new = []
    for i in range(len(rings) - 1):
        for k in range(n):
            j = (k + 1) % n
            new.append(bm.faces.new([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]))
    for cap, idx, rev in ((cap0, 0, False), (cap1, -1, True)):
        if cap is True:
            new.append(bm.faces.new(rings[idx][::-1] if rev else rings[idx]))
        elif cap:
            c, d = stations[idx]
            inner = [bm.verts.new(P(a, b, c)) for a, b in inset2(prof, d + cap)]
            for k in range(n):
                j = (k + 1) % n
                new.append(bm.faces.new([rings[idx][k], rings[idx][j], inner[j], inner[k]]))
    return closed(part, new)


def ends(c0, c1, r0, r1, k):
    """Stations of loft: end c0 rounded with radius r0, end c1 with r1 (k steps per quarter circle;
    r = 0 - sharp end).
    """
    st = []
    for i in reversed(range(k + 1)) if r0 > 0 else [k]:          # end (inset r0) to full section
        a = math.pi / 2 * i / k
        st.append((c0 + r0 * (1 - math.sin(a)), r0 * (1 - math.cos(a))))
    for i in range(k + 1) if r1 > 0 else [k]:
        a = math.pi / 2 * i / k
        st.append((c1 - r1 * (1 - math.sin(a)), r1 * (1 - math.cos(a))))
    out = []
    for c, d in st:
        if not out or abs(c - out[-1][0]) > 1e-7 or abs(d - out[-1][1]) > 1e-7:
            out.append((c, d))
    return out


def rbox(part, x0, x1, y0, y1, z0, z1, r, k=2, rz=None, frame=None):
    """Box: the edges along z are rounded with radius r, the top and bottom with rz (default r)."""
    rz = r if rz is None else rz
    prof = rrect((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, r, k)
    return loft(part, prof, "z", ends(z0, z1, rz, rz, k), frame=frame)


def hull(part, pts):
    bm = part.bm
    before = set(bm.faces)
    vs = [bm.verts.new(Vector(p)) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    faces = [f for f in bm.faces if f not in before]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return part.tag(faces)


def bulge_rr(part, cx, y_edge, cz, w, h, r, k, sag, n_rings):
    """Convex CRT glass with rounded corners: contour rings from the center to the edge, facing
    -y, the edges at y_edge, the middle is `sag` closer.
    """
    bm = part.bm
    ring0 = rrect(0.0, 0.0, w, h, r, k)
    rings = [[bm.verts.new((cx + a * s, y_edge - sag * (1 - s * s), cz + b * s)) for a, b in ring0]
             for s in [(i + 1) / n_rings for i in range(n_rings)]]
    c = bm.verts.new((cx, y_edge - sag, cz))
    n = len(ring0)
    new = [face(part, [c, rings[0][q], rings[0][(q + 1) % n]], (0, -1, 0)) for q in range(n)]
    for i in range(n_rings - 1):
        for q in range(n):
            j = (q + 1) % n
            new.append(face(part, [rings[i][q], rings[i + 1][q], rings[i + 1][j], rings[i][j]], (0, -1, 0)))
    return part.tag(new)


def button(part, cx, cz, w, h, y_face, depth, ch):
    """Button facing -y: walls from the device face, a chamfer ch on the front edge, the face; no
    back face.
    """
    bm = part.bm

    def ring(dx, dz, y):
        return [bm.verts.new((cx + sx * dx, y, cz + sz * dz)) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    r0 = ring(w / 2, h / 2, y_face)
    r1 = ring(w / 2, h / 2, y_face - depth + ch)
    r2 = ring(w / 2 - ch, h / 2 - ch, y_face - depth)
    new = []
    for a, b, fwd in ((r0, r1, 0.0), (r1, r2, 1.0)):
        for i in range(4):
            j = (i + 1) % 4
            m = Vector(((a[i].co.x + a[j].co.x) / 2 - cx, 0.0, (a[i].co.z + a[j].co.z) / 2 - cz)).normalized()
            new.append(face(part, [a[i], a[j], b[j], b[i]], m + Vector((0.0, -fwd, 0.0))))
    new.append(face(part, r2, (0, -1, 0)))
    return part.tag(new)


def keycap(part, x0, x1, y0, y1, h, ins, zfun, slope):
    """Key on the sloped keyboard top: the bottom is a rectangle on the plate (zfun(y) is its
    top), the top is inset by ins and raised by h along the normal to the slope (slope is the
    angle, rad); no bottom and back (the next row covers it).
    """
    bm = part.bm
    nrm = Vector((0.0, -math.sin(slope), math.cos(slope)))

    def at(x, y):
        return Vector((x, y, zfun(y)))
    b = [at(x0, y0), at(x1, y0), at(x1, y1), at(x0, y1)]
    t = [at(x0 + ins, y0 + ins * 1.4) + nrm * h, at(x1 - ins, y0 + ins * 1.4) + nrm * h,
         at(x1 - ins, y1 - ins * 0.6) + nrm * h, at(x0 + ins, y1 - ins * 0.6) + nrm * h]
    vb, vt = [bm.verts.new(p) for p in b], [bm.verts.new(p) for p in t]
    c = sum(b, Vector()) / 4
    new = [face(part, vt, nrm)]
    for i in (0, 1, 3):
        j = (i + 1) % 4
        m = (b[i] + b[j]) / 2 - c
        new.append(face(part, [vb[i], vb[j], vt[j], vt[i]], (m.x, m.y, 0.0)))
    return part.tag(new)


def ribbon(part, pts, wdir, half_w, half_t):
    """Flat ribbon along pts (antenna tape, insulating tape): the width goes along wdir,
    straightened across the run, the thickness across the ribbon (from M16).
    """
    bm = part.bm
    pts = [Vector(p) for p in pts]
    n = len(pts)
    rings = []
    for i in range(n):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        w = Vector(wdir) - t * Vector(wdir).dot(t)
        w.normalize()
        th = t.cross(w).normalized()
        c = pts[i]
        rings.append([bm.verts.new(c + w * half_w + th * half_t), bm.verts.new(c - w * half_w + th * half_t),
                      bm.verts.new(c - w * half_w - th * half_t), bm.verts.new(c + w * half_w - th * half_t)])
    new = []
    for i in range(n - 1):
        r0, r1 = rings[i], rings[i + 1]
        for q in range(4):
            new.append(bm.faces.new([r0[q], r0[(q + 1) % 4], r1[(q + 1) % 4], r1[q]]))
    new.append(bm.faces.new(rings[0][::-1]))
    new.append(bm.faces.new(rings[-1]))
    return closed(part, new)


def resample(pts, step):
    """Points of a polyline at equal steps (by length)."""
    v = [Vector(p) for p in pts]
    out = [v[0]]
    acc = 0.0
    for a, b in zip(v, v[1:]):
        seg = (b - a).length
        d = step - acc
        while d <= seg:
            out.append(a + (b - a) * (d / seg))
            d += step
        acc = seg - (d - step)
    if (out[-1] - v[-1]).length > step * 0.3:
        out.append(v[-1])
    return out


def coil(part, path, r_coil, pitch, r_wire, per_turn, sides):
    """Coiled cord (the radio handset): a wire r_wire wound as a helix of radius r_coil and pitch
    around the curve path; the coil frame is carried along the curve without twisting, as in
    kgeo.tube_var.
    """
    c = resample(path, pitch / per_turn)
    n = len(c)
    pts = []
    a_prev, t_prev = None, None
    for i in range(n):
        t = (c[min(i + 1, n - 1)] - c[max(i - 1, 0)]).normalized()
        if a_prev is None:
            a = t.cross(Vector((0, 0, 1)))
            if a.length < 0.15:
                a = t.cross(Vector((1, 0, 0)))
        else:
            a = t_prev.rotation_difference(t) @ a_prev
            a -= t * a.dot(t)
        a.normalize()
        b = t.cross(a).normalized()
        a_prev, t_prev = a, t
        ang = 2 * math.pi * i / per_turn
        pts.append(tuple(c[i] + (a * math.cos(ang) + b * math.sin(ang)) * r_coil))
    return g.pipe(part, pts, r_wire, sides)


def blob(part, sections, frame=None, cap0=True, cap1=True):
    """Body by sections along u: [(u, half-width, height, bottom)] - flat below, a half-ellipse
    on top (mouse, radio handset); n points per section.
    """
    bm = part.bm
    n = 10
    rings = []
    for u, hw, h, z0 in sections:
        ring = []
        for k in range(n):
            a = math.pi * k / (n - 1)
            x = hw * math.cos(a)
            z = z0 + h * math.sin(a) ** 0.75
            ring.append((u, x, z))
        ring += [(u, -hw * 0.92, z0), (u, hw * 0.92, z0)]
        rings.append([bm.verts.new(frame.p(*q) if frame else Vector(q)) for q in ring])
    m = len(rings[0])
    new = []
    for i in range(len(rings) - 1):
        for k in range(m):
            j = (k + 1) % m
            new.append(bm.faces.new([rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]))
    if cap0:
        new.append(bm.faces.new(rings[0]))
    if cap1:
        new.append(bm.faces.new(rings[-1][::-1]))
    return closed(part, new)


def knurl(part, center, axis, r, length, n, depth):
    """Knurled cylinder (knob, nut): 2n vertices around, every other one sunk by depth."""
    ia, ib = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}[axis]
    ic = 3 - ia - ib
    poly = [(center[ia] + (r - depth * (k % 2)) * math.cos(math.pi * k / n),
             center[ib] + (r - depth * (k % 2)) * math.sin(math.pi * k / n)) for k in range(2 * n)]
    return g.prism(part, poly, (ia, ib), center[ic] - length / 2, center[ic] + length / 2)
