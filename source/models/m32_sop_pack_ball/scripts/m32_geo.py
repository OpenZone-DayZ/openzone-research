"""Primitives of the M32 weapon cabinet that kgeo lacks: faces, solids of revolution and smooth
curves. The PSO-1 sight lives in its own module, pso1.py, shared with M23 and M27.

Blender axes: X - width, Y - depth (front at -Y), Z - up.
"""
import math

import bmesh
from mathutils import Vector

import kgeo as g


def fbox(part, a0, a1, b0, b1, c0, c1, frame, r=0.0, seg=0):
    """Chamfered box inside a tilted frame (a door leaf). In a frame, kgeo.box computes the chamfer
    from the normals of the not-yet-rotated cube and inflates the box by r in every direction (in
    a door frame b 0.0045..0.065 becomes -0.0075..0.077; in world axes it is unchanged). Here the
    box is built with its chamfer in local axes and then moved into the frame; normals are redone.
    """
    bm = part.bm
    before = set(bm.verts)
    faces = g.box(part, a0, a1, b0, b1, c0, c1, r=r, seg=seg)
    for v in bm.verts:
        if v not in before:
            v.co = frame.p(v.co.x, v.co.y, v.co.z)
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    bm.normal_update()
    return faces


def rod(part, a, b, r, sides):
    """Cylinder between points a and b."""
    return g.pipe(part, [tuple(a), tuple(b)], r, sides)


def face(part, verts, want):
    """Face from bmesh vertices, flipped to look toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def lathe(part, prof, sides, inward=False, center=(0.0, 0.0, 0.0), axis="z", cap=False):
    """Solid of revolution: prof [(r, h)] along the axis, ends open; inward - surface faces
    the axis; cap - close the last end. axis is "z" or "x".
    """
    bm = part.bm
    c0 = Vector(center)

    def pt(r, h, k):
        a = 2 * math.pi * k / sides
        if axis == "z":
            return c0 + Vector((r * math.cos(a), r * math.sin(a), h))
        return c0 + Vector((h, r * math.cos(a), r * math.sin(a)))
    rings = [[bm.verts.new(pt(r, h, k)) for k in range(sides)] for r, h in prof]
    new = []
    for i in range(len(rings) - 1):
        for k in range(sides):
            j = (k + 1) % sides
            q = [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]
            c = sum((v.co for v in q), Vector()) / 4 - c0
            out = Vector((c.x, c.y, 0)) if axis == "z" else Vector((0, c.y, c.z))
            new.append(face(part, q, -out if inward else out))
    if cap:
        sign = 1 if prof[-1][1] >= prof[0][1] else -1
        want = Vector((0, 0, sign)) if axis == "z" else Vector((sign, 0, 0))
        new.append(face(part, rings[-1], want))
    bm.normal_update()
    part.tag(new)
    return new


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, as in M04/M16)."""
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


def arc(c, r, a0, a1, n, plane="xz"):
    """Points of an arc of radius r around c from angle a0 to a1 (degrees) in the given plane."""
    i, j = {"xz": (0, 2), "yz": (1, 2), "xy": (0, 1)}[plane]
    out = []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        p = list(c)
        p[i] += r * math.cos(a)
        p[j] += r * math.sin(a)
        out.append(tuple(p))
    return out
