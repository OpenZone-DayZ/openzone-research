"""M15 primitives of its own (the shared kit stays unchanged): smooth curves, solids of revolution with
correct normals on horizontal runs, a sheet of paper with a fold, a flat ribbon, a bar between points,
polygons with rounded corners, a "Chernomorka" pack with the vanilla texture (as in M16)."""
import math

import bmesh
from mathutils import Vector

import kgeo as g


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, as in M16)."""
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


def cable(part, pts, r, sides, k=3):
    """Cable as a smooth curve through the points."""
    return g.pipe(part, spline(pts, k), r, sides)


def rod(part, a, b, r, sides):
    """Cylinder between points a and b."""
    return g.pipe(part, [tuple(a), tuple(b)], r, sides)


def frame_z(cx, cy, deg, z):
    """Local axes of an item lying on the table: u along it, turned by deg from +x, n up."""
    a = math.radians(deg)
    return g.Frame((cx, cy, z), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))


def face(part, verts, want):
    """Face from bmesh vertices, turned to look toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def basis(axis):
    a = Vector(axis).normalized()
    t = Vector((1, 0, 0)) if abs(a.x) < 0.9 else Vector((0, 1, 0))
    e1 = (t - a * t.dot(a)).normalized()
    return a, e1, a.cross(e1)


def lathe(part, prof, sides, center=(0.0, 0.0, 0.0), axis=(0, 0, 1), cap0=False, cap1=False, inward=False,
          phase=0.0, closed=False):
    """Solid of revolution: prof [(r, h)] along axis from center (r > 0). The face normal follows the
    profile: a rise - outward, a horizontal run toward the axis - up, away from the axis - down (traversed
    bottom to top, the solid on the left). inward - the opposite (inside of a mug); closed - the profile is
    closed (a ring with thickness); cap0 / cap1 - a disc at the first / last ring."""
    bm = part.bm
    a, e1, e2 = basis(axis)
    c0 = Vector(center)
    pr = list(prof) + ([prof[0]] if closed else [])
    rings = []
    for r, h in (prof if not closed else prof):
        rings.append([bm.verts.new(c0 + a * h + (e1 * math.cos(2 * math.pi * k / sides + phase) +
                                                 e2 * math.sin(2 * math.pi * k / sides + phase)) * r)
                      for k in range(sides)])
    if closed:
        rings.append(rings[0])
    new = []
    for i in range(len(pr) - 1):
        dr, dh = pr[i + 1][0] - pr[i][0], pr[i + 1][1] - pr[i][1]
        for k in range(sides):
            j = (k + 1) % sides
            q = [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]
            c = sum((v.co for v in q), Vector()) / 4 - c0
            rad = c - a * c.dot(a)
            rad = rad.normalized() if rad.length > 1e-9 else e1
            want = rad * dh - a * dr
            new.append(face(part, q, -want if inward else want))
    if cap0:
        new.append(face(part, rings[0], a if inward else -a))
    if cap1:
        new.append(face(part, rings[-1], -a if inward else a))
    bm.normal_update()
    part.tag(new)
    return new


def ring(part, center, axis, R, r, n, sides):
    """Torus (key ring, wire loop): axis circle R, section r."""
    a, e1, e2 = basis(axis)
    c = Vector(center)
    pts = [tuple(c + (e1 * math.cos(2 * math.pi * k / n) + e2 * math.sin(2 * math.pi * k / n)) * R) for k in range(n + 1)]
    return g.pipe(part, pts, r, sides)


def rounded_rect(w, h, r, n=3):
    """Rectangle w x h centred at zero with rounded corners (n segments per quarter)."""
    r = min(r, w / 2 - 1e-5, h / 2 - 1e-5)
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0.0), (-w / 2 + r, h / 2 - r, 90.0), (-w / 2 + r, -h / 2 + r, 180.0),
                       (w / 2 - r, -h / 2 + r, 270.0)):
        for k in range(n + 1):
            t = math.radians(a0 + 90.0 * k / n)
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return pts


def plate(part, poly, z0, z1, fr):
    """Prism of polygon poly (local a, b) from z0 to z1 along n of frame fr."""
    return g.prism(part, poly, (0, 1), z0, z1, frame=fr)


def sheet(part, fr, w, h, t, lift=None, ss=(0.0, 0.5, 1.0), qs=(0.0, 0.5, 1.0)):
    """Sheet w x h of thickness t in the axes of fr (u - width, v - sheet height, n - up, origin - middle of
    the sheet bottom). lift(s, q) - lift of the bottom in fractions s, q 0..1 (a folded corner, a wave);
    ss, qs - grid lines in fractions (denser near the fold)."""
    bm = part.bm
    top, bot = {}, {}
    nx, ny = len(ss) - 1, len(qs) - 1
    for i in range(nx + 1):
        for j in range(ny + 1):
            s, q = ss[i], qs[j]
            a, b = (s - 0.5) * w, (q - 0.5) * h
            z = lift(s, q) if lift else 0.0
            top[i, j] = bm.verts.new(fr.p(a, b, z + t))
            bot[i, j] = bm.verts.new(fr.p(a, b, z))
    new = []
    for i in range(nx):
        for j in range(ny):
            new.append(face(part, [top[i, j], top[i + 1, j], top[i + 1, j + 1], top[i, j + 1]], fr.n))
            new.append(face(part, [bot[i, j], bot[i + 1, j], bot[i + 1, j + 1], bot[i, j + 1]], -fr.n))
    edge = [(i, 0) for i in range(nx)] + [(nx, j) for j in range(ny)] + [(i, ny) for i in range(nx, 0, -1)] + \
           [(0, j) for j in range(ny, 0, -1)]
    nxt = edge[1:] + edge[:1]
    for p0, p1 in zip(edge, nxt):
        mid = (top[p0].co + top[p1].co) / 2 - fr.o
        out = mid - fr.n * mid.dot(fr.n)
        new.append(face(part, [bot[p0], bot[p1], top[p1], top[p0]], out))
    bm.normal_update()
    part.tag(new)
    return new


def ribbon(part, pts, wdir, half_w, half_t):
    """Flat ribbon along pts (rag tail, trailing end): the width is along wdir, straightened across the
    path (from M16)."""
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


def box_to(part, a, b, w, h, up=(0, 0, 1)):
    """Bar from point a to point b with cross-section w (across) x h (along up)."""
    a, b = Vector(a), Vector(b)
    u = (b - a).normalized()
    n = Vector(up) - u * Vector(up).dot(u)
    n.normalize()
    v = n.cross(u)
    fr = g.Frame(a, u, v, n)
    return g.box(part, 0.0, (b - a).length, -w / 2, w / 2, -h / 2, h / 2, frame=fr)


def frame_plate(part, outer, inner, z0, z1, frame=None, bevel=0.0):
    """Slab with a rectangular cutout: outer, inner - (x0, x1, y0, y1), thickness z0..z1 (in world axes or
    in the local frame). bevel - chamfer of the outer top edges."""
    bm = part.bm
    before = set(bm.faces)

    def P(x, y, z):
        return frame.p(x, y, z) if frame else Vector((x, y, z))
    (ox0, ox1, oy0, oy1), (ix0, ix1, iy0, iy1) = outer, inner
    oc = [(ox0, oy0), (ox1, oy0), (ox1, oy1), (ox0, oy1)]
    ic = [(ix0, iy0), (ix1, iy0), (ix1, iy1), (ix0, iy1)]
    ot = [bm.verts.new(P(x, y, z1)) for x, y in oc]
    ob = [bm.verts.new(P(x, y, z0)) for x, y in oc]
    it = [bm.verts.new(P(x, y, z1)) for x, y in ic]
    ib = [bm.verts.new(P(x, y, z0)) for x, y in ic]
    nrm = (frame.n if frame else Vector((0, 0, 1)))
    cen = P((ox0 + ox1) / 2, (oy0 + oy1) / 2, (z0 + z1) / 2)
    new = []
    for k in range(4):
        j = (k + 1) % 4
        new.append(face(part, [ot[k], ot[j], it[j], it[k]], nrm))
        new.append(face(part, [ob[k], ob[j], ib[j], ib[k]], -nrm))
        mo = (ot[k].co + ot[j].co) / 2 - cen
        new.append(face(part, [ob[k], ob[j], ot[j], ot[k]], mo - nrm * mo.dot(nrm)))
        mi = (it[k].co + it[j].co) / 2 - cen
        new.append(face(part, [ib[k], ib[j], it[j], it[k]], -(mi - nrm * mi.dot(nrm))))
    if bevel > 0:
        es = {e for v in ot for e in v.link_edges if (e.other_vert(v) in ot or e.other_vert(v) in ob)}
        g.bevel(bm, list(es), bevel, 1)
    new = [f for f in bm.faces if f not in before]
    part.tag(new)
    bm.normal_update()
    return new


def open_box(part, x0, x1, y0, y1, z0, z1, t, frame=None):
    """Open-top box: bottom and four walls of thickness t."""
    g.box(part, x0, x1, y0, y1, z0, z0 + t, frame=frame)
    g.box(part, x0, x1, y0, y0 + t, z0 + t, z1, frame=frame)
    g.box(part, x0, x1, y1 - t, y1, z0 + t, z1, frame=frame)
    g.box(part, x0, x0 + t, y0 + t, y1 - t, z0 + t, z1, frame=frame)
    g.box(part, x1 - t, x1, y0 + t, y1 - t, z0 + t, z1, frame=frame)


# DayZ "Chernomorka" pack: pieces of the vanilla texture (fractions of the image x0, x1, y0, y1 top to
# bottom) - the face with the coat of arms and a map, the side with the barcode, the end is a blue field
# (measured in M16 from pack_of_cigs_cherno_co.paa)
CIGS = (r"dz\gear\medical\data\pack_of_cigs_cherno_co.paa", r"dz\gear\medical\data\pack_of_cigs.rvmat")
CIGS_UV = {"front": (0.117, 0.462, 0.43, 1.0), "side": (0.885, 0.970, 0.60, 1.0), "end": (0.26, 0.45, 0.20, 0.30)}


def cig_pack(part, fr, L=0.088, W=0.055, H=0.022, skip=()):
    """Pack lying face up in frame fr (u along the pack, v across, n up), the bottom at fr.o: each face has
    its UV on its own piece of the vanilla texture; the top of the face picture is toward +u (from M16).
    skip - faces that are not visible (names: top, bottom, sides, ends)."""
    bm = part.bm
    uvl = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    hl, hw = L / 2, W / 2
    sides = [
        ("top", [(a, b, H) for a, b in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))], (0, 0, 1), "front",
         lambda a, b, c: ((hw - b) / W, (a + hl) / L)),
        ("bottom", [(a, b, 0.0) for a, b in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))], (0, 0, -1), "front",
         lambda a, b, c: ((b + hw) / W, (a + hl) / L)),
        ("sides", [(a, -hw, c) for a, c in ((-hl, 0.0), (hl, 0.0), (hl, H), (-hl, H))], (0, -1, 0), "side",
         lambda a, b, c: (c / H, (a + hl) / L)),
        ("sides", [(a, hw, c) for a, c in ((-hl, 0.0), (hl, 0.0), (hl, H), (-hl, H))], (0, 1, 0), "side",
         lambda a, b, c: (1.0 - c / H, (a + hl) / L)),
        ("ends", [(-hl, b, c) for b, c in ((-hw, 0.0), (hw, 0.0), (hw, H), (-hw, H))], (-1, 0, 0), "end",
         lambda a, b, c: ((b + hw) / W, c / H)),
        ("ends", [(hl, b, c) for b, c in ((-hw, 0.0), (hw, 0.0), (hw, H), (-hw, H))], (1, 0, 0), "end",
         lambda a, b, c: ((hw - b) / W, c / H)),
    ]
    new = []
    for nm, corners, nrm, rect, st in sides:
        if nm in skip:
            continue
        vs = [bm.verts.new(fr.p(*q)) for q in corners]
        loc = {v: q for v, q in zip(vs, corners)}
        f = face(part, vs, fr.u * nrm[0] + fr.v * nrm[1] + fr.n * nrm[2])
        x0, x1, y0, y1 = CIGS_UV[rect]
        for lp in f.loops:
            s, t = st(*loc[lp.vert])
            lp[uvl].uv = (x0 + (x1 - x0) * s, 1.0 - (y1 - (y1 - y0) * t))
        new.append(f)
    part.tag(new)
    return new
