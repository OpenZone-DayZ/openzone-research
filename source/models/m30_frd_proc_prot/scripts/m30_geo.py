"""M30 primitives that kgeo does not have: local axes, a solid of revolution (an elliptical section),
a shell with an egg-shaped section (the mask), a torus, a smooth curve. lathe, along, upright, face
and spline come from M29 and M24; the torus is as in M03/M04.

Blender axes: X is width, Y is depth (the face looks to -Y), Z is up.
"""
import math

from mathutils import Vector

import kgeo as g


def turn(cx, cy, z, deg):
    """Local axes rotated about the vertical: u along deg, v across, n up."""
    a = math.radians(deg)
    return g.Frame((cx, cy, z), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))


def along(o, d):
    """Local axes with u along d (an inclined solid of revolution)."""
    d = Vector(d).normalized()
    ref = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    v = d.cross(ref).normalized()
    return g.Frame(o, d, v, d.cross(v))


def upright(o, deg=0.0):
    """Local axes of a vertical body: u is up, v is right, n is forward (toward -y at deg 0)."""
    a = math.radians(deg)
    return g.Frame(o, (0, 0, 1), (math.cos(a), math.sin(a), 0), (math.sin(a), -math.cos(a), 0))


def face(part, verts, want):
    """Face from bmesh vertices, oriented toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def lathe(part, prof, sides, frame, inward=False, caps=(False, False), kv=1.0, kn=1.0, want=None, phase=0.0):
    """Solid of revolution around axis u of local axes frame: prof [(r, h)] - radius and place along u; the
    section is an ellipse r*kv along v and r*kn along n. inward - the surface looks toward the axis (the
    inside); caps - the ends (start, end) are closed; want - where all the faces look (a flat ring)."""
    bm = part.bm
    rings = []
    for r, h in prof:
        rings.append([bm.verts.new(frame.p(h, r * kv * math.cos(2 * math.pi * k / sides + phase),
                                           r * kn * math.sin(2 * math.pi * k / sides + phase)))
                      for k in range(sides)])
    new = []
    for i in range(len(rings) - 1):
        for k in range(sides):
            j = (k + 1) % sides
            q = [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]
            c = sum((v.co for v in q), Vector()) / 4
            ax = frame.o + frame.u * (c - frame.o).dot(frame.u)
            out = c - ax
            new.append(face(part, q, want if want is not None else (-out if inward else out)))
    if caps[0]:
        new.append(face(part, rings[0], -frame.u if not inward else frame.u))
    if caps[1]:
        new.append(face(part, rings[-1], frame.u if not inward else -frame.u))
    bm.normal_update()
    part.tag(new)
    return new


def shell_dims(rings, h):
    """Half-width a, depth forward f and backward b of the shell at height h (linear between rings)."""
    for (h0, a0, f0, b0), (h1, a1, f1, b1) in zip(rings, rings[1:]):
        if h0 <= h <= h1:
            t = (h - h0) / max(h1 - h0, 1e-9)
            return a0 + (a1 - a0) * t, f0 + (f1 - f0) * t, b0 + (b1 - b0) * t
    h0, a0, f0, b0 = rings[-1] if h > rings[-1][0] else rings[0]
    return a0, f0, b0


def shell_point(frame, rings, h, phi):
    """A shell point: height h, angle phi from +v (right) to +n (forward)."""
    a, f, b = shell_dims(rings, h)
    s = math.sin(phi)
    return frame.p(h, a * math.cos(phi), (f if s >= 0 else b) * s)


def shell_normal(frame, rings, h, phi):
    """Outward normal of the shell in the section plane (without the tilt along the height)."""
    a, f, b = shell_dims(rings, h)
    s, c = math.sin(phi), math.cos(phi)
    d = f if s >= 0 else b
    return (frame.v * (c / a) + frame.n * (s / d)).normalized()


def shell(part, rings, sides, frame, top=None):
    """Smooth shell (the mask): rings [(h, a, f, b)] - height along u, half-width along v, depth forward
    (n) and backward; the section is two half-ellipses (front and back). top - the crown height: the rings
    converge to one vertex; the bottom is open."""
    bm = part.bm
    ring_v = [[bm.verts.new(shell_point(frame, rings, h, 2 * math.pi * k / sides)) for k in range(sides)]
              for h, _, _, _ in rings]
    new = []
    for i in range(len(ring_v) - 1):
        for k in range(sides):
            j = (k + 1) % sides
            q = [ring_v[i][k], ring_v[i][j], ring_v[i + 1][j], ring_v[i + 1][k]]
            c = sum((v.co for v in q), Vector()) / 4
            ax = frame.o + frame.u * (c - frame.o).dot(frame.u)
            new.append(face(part, q, c - ax))
    if top is not None:
        tip = bm.verts.new(frame.p(top, 0.0, 0.0))
        for k in range(sides):
            j = (k + 1) % sides
            new.append(face(part, [ring_v[-1][k], ring_v[-1][j], tip], frame.u))
    bm.normal_update()
    part.tag(new)
    return new


def torus(part, frame, R, r, seg, sides, h=0.0):
    """Torus around axis u of local axes frame at height h: ring radius R, rod r."""
    bm = part.bm
    rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        cdir = frame.v * math.cos(a) + frame.n * math.sin(a)
        c = frame.o + frame.u * h + cdir * R
        rings.append([bm.verts.new(c + (cdir * math.cos(2 * math.pi * k / sides) +
                                        frame.u * math.sin(2 * math.pi * k / sides)) * r) for k in range(sides)])
    new = []
    for i in range(seg):
        i2 = (i + 1) % seg
        for k in range(sides):
            j = (k + 1) % sides
            q = [rings[i][k], rings[i][j], rings[i2][j], rings[i2][k]]
            c = sum((v.co for v in q), Vector()) / 4
            a = 2 * math.pi * (i + 0.5) / seg
            cen = frame.o + frame.u * h + (frame.v * math.cos(a) + frame.n * math.sin(a)) * R
            new.append(face(part, q, c - cen))
    bm.normal_update()
    part.tag(new)
    return new


def rod(part, a, b, r, sides):
    return g.pipe(part, [tuple(a), tuple(b)], r, sides)


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


def bev(lod, r=0.003, seg=2):
    """Chamfer of box edges on the near LOD only."""
    return dict(r=r, seg=seg) if lod == 0 else {}


def front_quad(part, x0, x1, z0, z1, y):
    """A single face facing -y (far LOD: the lamp, the display)."""
    return g.quad(part, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)])
