"""Geometry of the M60 field HQ beyond _kit/kgeo: rounded boxes and bodies over a rounded rectangle with
inset rings (the edges are rounded, not cut), frames with a cutout, bodies of revolution in any frame,
ribbed bushings, key caps, smooth curves, an uneven surface (sand), a ribbon. The shared kit is not
modified - the model's own functions live here.

Face normals are set by the 'outward' direction, not by vertex order: for a profile (r, h) or rings
(height, inset) the outward normal is (dh, -dr) in the profile plane, so a profile can run from the
outside up, over the edge and down the inside (a mug), and all faces look the right way.
"""
import math

from mathutils import Vector

import kgeo as g

AXES = {"x": (1.0, 0.0, 0.0), "-x": (-1.0, 0.0, 0.0), "y": (0.0, 1.0, 0.0), "-y": (0.0, -1.0, 0.0),
        "z": (0.0, 0.0, 1.0), "-z": (0.0, 0.0, -1.0)}


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, k steps per segment)."""
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
    """Face from vertices, oriented towards want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def turn(cx, cy, z, deg):
    """Local axes rotated about the vertical: u along the object, v across, n up."""
    a = math.radians(deg)
    return g.Frame((cx, cy, z), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))


def compose(fr, o, u, v, n):
    """A frame given in the local axes of frame fr: o is a point, u, v, n are vectors in the axes of fr."""
    def vec(w):
        return fr.u * w[0] + fr.v * w[1] + fr.n * w[2]
    return g.Frame(fr.p(*o), vec(u), vec(v), vec(n))


def face_frame(y, sign):
    """Plane of the face or back (a face looking at sign*y at depth y): a along x, b up, c outward."""
    return g.Frame((0.0, y, 0.0), (1, 0, 0), (0, 0, 1), (0, sign, 0))


def side_frame(x, sign):
    """Plane of a side (a face looking at sign*x): a along y, b up, c outward."""
    return g.Frame((x, 0.0, 0.0), (0, 1, 0), (0, 0, 1), (sign, 0, 0))


def _pt(frame):
    if frame is None:
        return lambda a, b, c: Vector((a, b, c))
    return frame.p


def _axis(frame):
    return Vector(frame.n) if frame is not None else Vector((0.0, 0.0, 1.0))


def rr_outline(x0, x1, y0, y1, r, seg):
    """Rounded rectangle, counter-clockwise: seg + 1 points per corner (seg = 0 - sharp corners)."""
    if seg <= 0 or r <= 1e-7:
        return [(x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    r = min(r, (x1 - x0) / 2 * 0.98, (y1 - y0) / 2 * 0.98)
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90.0), (x1 - r, y1 - r, 0.0), (x0 + r, y1 - r, 90.0), (x0 + r, y0 + r, 180.0)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90.0 * k / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def rr_loft(part, x0, x1, y0, y1, rings, r, seg, frame=None, cap0=True, cap1=True):
    """A body over a rounded rectangle (the a-b plane of the frame; without a frame x-y) over rings [(c,
    inset)] from bottom to top: c is the height along the third axis, inset is inward (rounding and
    chamfer of the edges, a recessed panel); a negative inset is a protrusion (a bead). The corner
    radius of a ring is r minus the inset (not less than 0.3 r).
    """
    P = _pt(frame)
    ax = _axis(frame)
    bm = part.bm
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    loops = []
    for c, d in rings:
        rr = max(r - d, r * 0.3) if r > 0 else 0.0
        pts = rr_outline(x0 + d, x1 - d, y0 + d, y1 - d, rr, seg if r > 0 else 0)
        loops.append([bm.verts.new(P(a, b, c)) for a, b in pts])
    new = []
    m = len(loops[0])
    for i in range(len(loops) - 1):
        dc = rings[i + 1][0] - rings[i][0]
        dr = -(rings[i + 1][1] - rings[i][1])
        center = P(cx, cy, (rings[i][0] + rings[i + 1][0]) / 2)
        for k in range(m):
            j = (k + 1) % m
            q = [loops[i][k], loops[i][j], loops[i + 1][j], loops[i + 1][k]]
            rad = sum((v.co for v in q), Vector()) / 4 - center
            rad -= ax * rad.dot(ax)
            if rad.length > 1e-12:
                rad.normalize()
            new.append(face(part, q, rad * dc - ax * dr))
    if cap0:
        new.append(face(part, loops[0], -ax))
    if cap1:
        new.append(face(part, loops[-1], ax))
    part.tag(new)
    return new


def rbox(part, x0, x1, y0, y1, z0, z1, r=0.0, seg=1, frame=None, cap0=True, cap1=True):
    """A box with rounded edges: the vertical ones with radius r in plan, the top and bottom ones a
    quarter circle in seg steps. It is built directly in the frame (without bmesh.bevel: with kgeo.box
    chamfered in a rotated frame the faces turn inside out).
    """
    if r <= 0 or seg <= 0:
        return g.box(part, x0, x1, y0, y1, z0, z1, frame=frame)
    r = min(r, (x1 - x0) * 0.45, (y1 - y0) * 0.45, (z1 - z0) * 0.45)
    rings = []
    for k in range(seg + 1):
        a = math.pi / 2 * k / seg
        rings.append((z0 + r - r * math.cos(a), r - r * math.sin(a)))
    for k in range(seg + 1):
        a = math.pi / 2 * k / seg
        rings.append((z1 - r + r * math.sin(a), r - r * math.cos(a)))
    return rr_loft(part, x0, x1, y0, y1, rings, r, seg, frame, cap0, cap1)


def rr_ring(part, outer, inner, z0, z1, r_out, r_in, seg, frame=None):
    """A frame with a cutout: between the rounded rectangles outer and inner (x0, x1, y0, y1) from z0 to
    z1 - the outer and inner walls and the top; no bottom (it lies on a surface).
    """
    P = _pt(frame)
    ax = _axis(frame)
    bm = part.bm
    po, pi = rr_outline(*outer, r_out, seg), rr_outline(*inner, r_in, seg)
    ob = [bm.verts.new(P(a, b, z0)) for a, b in po]
    ot = [bm.verts.new(P(a, b, z1)) for a, b in po]
    ib = [bm.verts.new(P(a, b, z0)) for a, b in pi]
    it = [bm.verts.new(P(a, b, z1)) for a, b in pi]
    center = P((outer[0] + outer[1]) / 2, (outer[2] + outer[3]) / 2, (z0 + z1) / 2)
    new = []
    m = len(po)
    for k in range(m):
        j = (k + 1) % m
        for q, sign in (([ob[k], ob[j], ot[j], ot[k]], 1.0), ([ib[k], ib[j], it[j], it[k]], -1.0)):
            rad = sum((v.co for v in q), Vector()) / 4 - center
            rad -= ax * rad.dot(ax)
            new.append(face(part, q, rad * sign))
        new.append(face(part, [ot[k], ot[j], it[j], it[k]], ax))
    part.tag(new)
    return new


def flat_rr(part, x0, x1, y0, y1, c, r, seg, frame=None):
    """A single flat face - a rounded rectangle at height c, facing along the third axis."""
    P = _pt(frame)
    vs = [part.bm.verts.new(P(a, b, c)) for a, b in rr_outline(x0, x1, y0, y1, r, seg)]
    return part.tag([face(part, vs, _axis(frame))])


def keycap(part, x0, x1, y0, y1, z0, h, inset):
    """Key cap: a truncated pyramid without a bottom (the top is smaller than the bottom by inset on
    each side).
    """
    bm = part.bm
    b = [bm.verts.new(v) for v in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0))]
    t = [bm.verts.new(v) for v in ((x0 + inset, y0 + inset, z0 + h), (x1 - inset, y0 + inset, z0 + h),
                                   (x1 - inset, y1 - inset, z0 + h), (x0 + inset, y1 - inset, z0 + h))]
    outs = ((0, -1, 0), (1, 0, 0), (0, 1, 0), (-1, 0, 0))
    new = [face(part, t, (0, 0, 1))]
    for k in range(4):
        j = (k + 1) % 4
        new.append(face(part, [b[k], b[j], t[j], t[k]], outs[k]))
    part.tag(new)
    return new


def disk(part, center, nrm, r, sides, phase=0.0):
    """A flat polygon (a nail head, screw, rivet) facing nrm - in world axes."""
    n = Vector(nrm).normalized()
    e1 = n.orthogonal().normalized()
    e2 = n.cross(e1).normalized()
    c = Vector(center)
    vs = [part.bm.verts.new(c + (e1 * math.cos(2 * math.pi * (k + phase) / sides) +
                                 e2 * math.sin(2 * math.pi * (k + phase) / sides)) * r) for k in range(sides)]
    return part.tag([face(part, vs, n)])


def _lathe_axes(center, axis, frame):
    a = Vector(AXES[axis]) if isinstance(axis, str) else Vector(axis).normalized()
    e1 = a.orthogonal().normalized()
    e2 = a.cross(e1).normalized()
    if frame is not None:
        def conv(w):
            return frame.u * w.x + frame.v * w.y + frame.n * w.z
        return frame.p(*center), conv(a), conv(e1), conv(e2)
    return Vector(center), a, e1, e2


def lathe(part, prof, sides, center=(0.0, 0.0, 0.0), axis="z", cap0=False, cap1=False, frame=None, phase=0.5):
    """Body of revolution: prof [(r, h)] along the direction axis ("x", "-y", ... or a vector) from
    center (with frame - in its local axes). Normals point outwards along the profile; cap0 / cap1 close
    the first / last ring.
    """
    c0, a, e1, e2 = _lathe_axes(center, axis, frame)
    bm = part.bm
    rings = []
    for r, h in prof:
        rings.append([bm.verts.new(c0 + a * h + (e1 * math.cos(2 * math.pi * (k + phase) / sides) +
                                                 e2 * math.sin(2 * math.pi * (k + phase) / sides)) * r)
                      for k in range(sides)])
    new = []
    for i in range(len(prof) - 1):
        dh = prof[i + 1][1] - prof[i][1]
        dr = prof[i + 1][0] - prof[i][0]
        cpt = c0 + a * ((prof[i][1] + prof[i + 1][1]) / 2)
        for k in range(sides):
            j = (k + 1) % sides
            q = [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]
            rad = sum((v.co for v in q), Vector()) / 4 - cpt
            rad -= a * rad.dot(a)
            if rad.length > 1e-12:
                rad.normalize()
            new.append(face(part, q, rad * dh - a * dr))
    if cap0:
        new.append(face(part, rings[0], -a))
    if cap1:
        new.append(face(part, rings[-1], a))
    part.tag(new)
    return new


def knurl(part, center, axis, r, h0, h1, n, depth, frame=None):
    """Ribbed bushing (nut, knob): 2n faces around, every other one recessed by depth; the ends are
    closed.
    """
    c0, a, e1, e2 = _lathe_axes(center, axis, frame)
    bm = part.bm

    def ring(h):
        return [bm.verts.new(c0 + a * h + (e1 * math.cos(math.pi * k / n) + e2 * math.sin(math.pi * k / n)) *
                             (r - depth * (k % 2))) for k in range(2 * n)]
    lo, hi = ring(h0), ring(h1)
    new = []
    for k in range(2 * n):
        j = (k + 1) % (2 * n)
        q = [lo[k], lo[j], hi[j], hi[k]]
        rad = sum((v.co for v in q), Vector()) / 4 - (c0 + a * ((h0 + h1) / 2))
        rad -= a * rad.dot(a)
        new.append(face(part, q, rad))
    new.append(face(part, lo, -a))
    new.append(face(part, hi, a))
    part.tag(new)
    return new


def grid(part, x0, x1, y0, y1, nx, ny, zf):
    """Uneven surface facing up: an nx x ny grid, height zf(x, y)."""
    bm = part.bm
    vs = [[bm.verts.new((x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny,
                         zf(x0 + (x1 - x0) * i / nx, y0 + (y1 - y0) * j / ny))) for j in range(ny + 1)]
          for i in range(nx + 1)]
    new = []
    for i in range(nx):
        for j in range(ny):
            new.append(face(part, [vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]], (0, 0, 1)))
    part.tag(new)
    return new


def ribbon(part, pts, wdir, half_w, half_t):
    """Flat ribbon along pts (headband, the spring jaw of the clip): the width runs along wdir
    straightened across the path, the thickness across the ribbon (from M16).
    """
    import bmesh
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
    bmesh.ops.recalc_face_normals(bm, faces=new)
    return part.tag(new)


def simplify(pts, deg=4.0):
    """Remove curve points where it hardly turns (less than deg degrees): straight wire runs get no
    extra rings, bends stay smooth.
    """
    out = [tuple(pts[0])]
    for i in range(1, len(pts) - 1):
        a = Vector(pts[i]) - Vector(out[-1])
        b = Vector(pts[i + 1]) - Vector(pts[i])
        if a.length < 1e-9 or b.length < 1e-9:
            continue
        if a.angle(b) > math.radians(deg):
            out.append(tuple(pts[i]))
    out.append(tuple(pts[-1]))
    return out


def cord(part, pts, r, sides, k=3):
    """Wire or cord: a smooth curve through the support points (k steps per segment) with a round
    section; straight runs need no rings - simplify.
    """
    pp = simplify(spline(pts, k), 5.0) if k > 1 else [tuple(p) for p in pts]
    return g.pipe(part, pp, r, sides)
