"""Cabinet base with a folding table: an army steel two-door cabinet on a plinth, the doors flung
open (a single fixed pose), a partition and shelves inside as the model specifies; the lower
boundary of the upper compartment is a folding panel on a piano hinge, lowered on two chains into
a work table. Raised, the panel closes the bottom of the upper compartment (behind the doors);
lowered, it continues the compartment floor forward, so the table and the compartment floor are
one plane.

Dimensions: 1.0 x 1.9 x 0.5 m, table 1.0 x 0.5 at a height of 0.85. No datasheet of a Soviet army
rifle cabinet (ShKhO/OSh) exists in open sources, so the body follows cabinets of the same design:
ShMDO 900 x 1800 x 500 mm; the UKhL-MASh rifle cabinet (two tiers of AK, a plinth, shelves) is
taken from a photo; the folding panel on chains follows the Caron RAD GunWorks gun-cleaning
cabinet. Body steel is 1.5 mm, the doors are a box with a 25 mm flange.

The model's fittings (cradles, props, lamp) live in the model generator, not here.
Blender axes: X - width, Y - depth (the front at -Y), Z - up.
"""
import math

from mathutils import Vector

import kgeo as g

T = 0.02                                   # body walls (with the flange they look thicker than the sheet)
DOOR_T = 0.025                             # a door is a box with a flange
FOOT = 0.06                                # plinth height
LIP = 0.03                                 # frame of the opening at the front


def layout(x0, x1, y0, y1, height, table_z=0.85, table_d=0.50, door_deg=105.0, chain_z=None):
    """Where the cabinet parts are: the opening (inner x, y, z), the doors - a kgeo.Frame each
    (a - along the door width from the hinge, b - thickness, from the face to the inside, c -
    height) and their width, the table, the chain points. y0 is the body face (behind the doors),
    y1 the back."""
    xi0, xi1 = x0 + T, x1 - T
    th = math.radians(door_deg)
    w = (x1 - x0) / 2 - 0.002
    zd0, zd1 = FOOT + 0.005, height - 0.005
    frames = []
    for s, xh in ((1, x0), (-1, x1)):
        u = (s * math.cos(th), -math.sin(th), 0.0)
        v = (s * math.sin(th), math.cos(th), 0.0)
        o = (xh, y0 - DOOR_T, 0.0)
        frames.append(g.Frame(o, u, v, (0, 0, 1)))
    chain_z = chain_z if chain_z is not None else table_z + 0.48
    # The table is 2 cm narrower than the opening on each side: the chains run in this gap, from
    # the lugs on the side edge of the table to the gussets on the frame of the opening.
    tx0, tx1 = xi0 + 0.02, xi1 - 0.02
    ty0 = y0 - table_d
    chains = [((xi0 + 0.010, ty0 + 0.04, table_z - 0.015), (xi0 + 0.010, y0 - 0.006, chain_z)),
              ((xi1 - 0.010, ty0 + 0.04, table_z - 0.015), (xi1 - 0.010, y0 - 0.006, chain_z))]
    return dict(inner=(xi0, xi1, y0, y1 - T, FOOT + T, height - T), doors=frames, door_w=w,
                door_z=(zd0, zd1), table=(tx0, tx1, ty0, y0, table_z), chains=chains, face=y0)


def fbox(part, x0, x1, y0, y1, z0, z1, frame, **kw):
    """kgeo.box in an inclined frame (a door) with a side check: kgeo.box in such a frame,
    especially a mirrored one (the right door), has its box turned inside out by the normal
    recalculation; here the sign of the volume of the new faces is checked and an inverted box is
    flipped."""
    bm = part.bm
    before = set(bm.faces)
    g.box(part, x0, x1, y0, y1, z0, z1, frame=frame, **kw)
    new = [f for f in bm.faces if f not in before]
    vol = 0.0
    for f in new:
        vs = [v.co for v in f.verts]
        for i in range(1, len(vs) - 1):
            vol += vs[0].dot(vs[i].cross(vs[i + 1]))
    if vol < 0:
        for f in new:
            f.normal_flip()
    bm.normal_update()


def _link_pts(c, side, along, h, w):
    """Four corners of a chain link: center c, along the chain `along`, across it `side` (the plane of the link)."""
    return [c + along * h + side * w, c - along * h + side * w, c - along * h - side * w, c + along * h - side * w]


def chain(part, a, b, lod, pitch=0.042, wire=0.0035):
    """Chain from a to b: links alternate between two planes (near LOD); a plain rod on the farther LODs."""
    a, b = Vector(a), Vector(b)
    d = b - a
    ln = d.length
    t = d.normalized()
    s1 = t.cross(Vector((0, 0, 1)))
    if s1.length < 0.1:
        s1 = t.cross(Vector((1, 0, 0)))
    s1.normalize()
    s2 = t.cross(s1).normalized()
    if lod > 0:
        g.pipe(part, [a, b], 0.0045, 4)
        return
    n = max(2, int(ln / pitch))
    step = ln / n
    for k in range(n):
        c = a + t * (step * (k + 0.5))
        side = s1 if k % 2 == 0 else s2
        nrm = s2 if k % 2 == 0 else s1
        pts = _link_pts(c, side, t, step * 0.62, 0.011)
        g.sweep(part, pts, nrm, wire, wire, closed=True)


def cabinet(m, spec, x0, x1, y0, y1, height, table_z=0.85, table_d=0.50, door_deg=105.0, chain_z=None,
            shelves=(), partitions=(), handles=True, regions=None, prefix="cb"):
    """Cabinet base. m is a kmodel.Model. The body face is y0 (the doors are flung forward and
    outward), the plinth bottom is at 0.

    shelves - [(xa, xb, z)]: shelves (top at z) with an edge bent down; the floor of the upper
    compartment at table_z is always added (a continuation of the table). partitions -
    [(x, za, zb)]: vertical partitions. handles - a handle with a lock cylinder on the right door
    and a seal lug.
    regions: body (outside of the body), body_in (inside, shelves), door (doors outside), door_in
    (doors inside), table, steel (hinges, handle, lugs), chain, foot (plinth).
    spec["lod"]: 0 - everything, 1 - no hinges and bevels, doors as a box without a flange, chains
    as a rod, 2 - the body as a box without a frame, shelves without edges, doors and table as
    slabs, no chains."""
    r = dict(body="cb", body_in="cb_in", door="cb_door", door_in="cb_door_in", table="cb_table", steel="steel",
             chain="steel", foot="black")
    r.update(regions or {})
    lod = spec["lod"]
    lay = layout(x0, x1, y0, y1, height, table_z, table_d, door_deg, chain_z)
    xi0, xi1, yi0, yi1, zi0, zi1 = lay["inner"]
    bev = dict(r=0.003, seg=1) if lod == 0 else {}
    # 4 mm sheets: the bevel is less than half the thickness, otherwise it overlaps itself and the
    # normal recalculation turns the sheet inside out (the door face was baked onto the hidden side).
    bev_t = dict(r=0.0015, seg=1) if lod == 0 else {}
    parts = []

    def own(name, region, *box, **kw):
        """A separate part per sheet: an atlas rectangle is keyed by part / region / side, so sheets
        of one side lying one behind another (two side walls, shelves one above another, door
        flanges) would otherwise share the same texels - the bake writes there the one that is
        covered (dark)."""
        p = m.part(prefix + "_" + name, r[region])
        if "frame" in kw:
            fbox(p, *box, **kw)
        else:
            g.box(p, *box, **kw)
        parts.append(p)
        return p

    # --- outside of the body: sides, roof, back, plinth
    own("side_l", "body", x0, xi0, y0, y1, FOOT, height, **bev)
    own("side_r", "body", xi1, x1, y0, y1, FOOT, height, **bev)
    own("roof", "body", xi0, xi1, y0, y1, zi1, height, **bev)
    own("back", "body", xi0, xi1, yi1, y1, FOOT, zi1)
    own("foot", "foot", x0 + 0.02, x1 - 0.02, y0 + 0.02, y1 - 0.01, 0.0, FOOT + 0.001)

    # --- inside: floor, floor of the upper compartment (at table level), shelves, partitions
    own("floor", "body_in", xi0, xi1, y0, yi1, FOOT, zi0)
    own("floor_up", "body_in", xi0, xi1, y0 + 0.012, yi1, table_z - T, table_z)
    for i, (xa, xb, z) in enumerate(shelves):
        sh = own("shelf%d" % i, "body_in", xa, xb, y0 + 0.03, yi1, z - 0.004, z)
        if lod < 2:
            g.box(sh, xa, xb, y0 + 0.03, y0 + 0.042, z - 0.028, z - 0.004)                 # edge bent down
    for i, (x, za, zb) in enumerate(partitions):
        own("wall%d" % i, "body_in", x - 0.003, x + 0.003, y0 + 0.02, yi1, za, zb)
    if lod < 2:
        # frame of the opening: the body face flanged inward
        own("lip_l", "body", xi0, xi0 + LIP, y0, y0 + 0.012, zi0, zi1)
        own("lip_r", "body", xi1 - LIP, xi1, y0, y0 + 0.012, zi0, zi1)
        own("lip_t", "body", xi0 + LIP, xi1 - LIP, y0, y0 + 0.012, zi1 - LIP, zi1)
        own("lip_b", "body", xi0 + LIP, xi1 - LIP, y0, y0 + 0.012, zi0, zi0 + 0.05)

    # --- doors: a box - the sheet outside, a flange along the contour, a stiffening rib across
    zd0, zd1 = lay["door_z"]
    w = lay["door_w"]
    e = 0.022
    zm = (zd0 + zd1) / 2
    for f, sd in zip(lay["doors"], "lr"):
        if lod == 2:
            own("door_" + sd, "door", 0.0, w, 0.0, DOOR_T, zd0, zd1, frame=f)
            continue
        own("door_" + sd, "door", 0.0, w, 0.0, 0.004, zd0, zd1, frame=f, **bev_t)
        if lod == 1:
            own("door_in_" + sd, "door_in", 0.0, w, 0.004, DOOR_T, zd0, zd1, frame=f)
            continue
        fl = own("door_edge_" + sd, "door_in", 0.0, e, 0.004, DOOR_T, zd0, zd1, frame=f)
        fbox(fl, w - e, w, 0.004, DOOR_T, zd0, zd1, frame=f)
        own("door_bot_" + sd, "door_in", e, w - e, 0.004, DOOR_T, zd0, zd0 + e, frame=f)
        own("door_top_" + sd, "door_in", e, w - e, 0.004, DOOR_T, zd1 - e, zd1, frame=f)
        own("door_rib_" + sd, "door_in", e, w - e, 0.004, 0.016, zm - 0.03, zm + 0.03, frame=f)
        # The inside of the door between the flanges is the sheet itself seen from inside.
        own("door_in_" + sd, "door_in", e, w - e, 0.004, 0.0045, zd0 + e, zd1 - e, frame=f)

    # --- hinges: three on each side, the axis at the outer edge of the body
    if lod == 0:
        hg = m.part(prefix + "_hinges", r["steel"])
        for xe in (x0 - 0.004, x1 + 0.004):
            for zc in (zd0 + 0.16, (zd0 + zd1) / 2, zd1 - 0.16):
                g.cyl(hg, (xe, y0 - DOOR_T, zc), "z", 0.008, 0.10, 8)
        parts.append(hg)

    # --- lever handle and lock cylinder on the right door (outside), seal lugs
    if handles and lod < 2:
        hd = m.part(prefix + "_handle", r["steel"])
        f = lay["doors"][1]
        zh = FOOT + 0.98
        ah = w - 0.055
        fbox(hd, ah - 0.022, ah + 0.022, -0.004, 0.0, zh - 0.07, zh + 0.07, frame=f)
        fbox(hd, ah - 0.010, ah + 0.010, -0.030, -0.004, zh + 0.02, zh + 0.04, frame=f)
        fbox(hd, ah - 0.010, ah + 0.010, -0.030, -0.018, zh - 0.10, zh + 0.04, frame=f)
        if lod == 0:
            fbox(hd, ah - 0.009, ah + 0.009, -0.009, -0.004, zh - 0.055, zh - 0.035, frame=f)  # lock cylinder
        parts.append(hd)

    # --- folding table: the sheet on top, the flange down, a piano hinge at the body face
    tx0, tx1, ty0, ty1, tz = lay["table"]
    if lod == 2:
        own("table", "table", tx0, tx1, ty0, ty1, tz - 0.03, tz)
        return parts, lay
    own("table", "table", tx0, tx1, ty0, ty1 - 0.004, tz - 0.004, tz, **bev_t)
    own("table_front", "body_in", tx0, tx1, ty0, ty0 + 0.004, tz - 0.03, tz - 0.004)
    own("table_side_l", "body_in", tx0, tx0 + 0.004, ty0 + 0.004, ty1 - 0.004, tz - 0.03, tz - 0.004)
    own("table_side_r", "body_in", tx1 - 0.004, tx1, ty0 + 0.004, ty1 - 0.004, tz - 0.03, tz - 0.004)
    own("table_rib", "body_in", tx0 + 0.004, tx1 - 0.004, ty0 + 0.25, ty0 + 0.27, tz - 0.022, tz - 0.004)
    st = m.part(prefix + "_table_steel", r["steel"])
    g.cyl(st, ((tx0 + tx1) / 2, ty1, tz - 0.008), "x", 0.006, tx1 - tx0 - 0.02, 8 if lod == 0 else 4)
    ch = m.part(prefix + "_chains", r["chain"])
    for a, b in lay["chains"]:
        chain(ch, a, b, lod)
        if lod == 0:
            # a lug on the side edge of the table and a gusset on the frame of the opening
            sx = 1 if b[0] < (x0 + x1) / 2 else -1
            xe = tx0 if sx > 0 else tx1
            g.box(st, *sorted((xe, xe - sx * 0.014)), a[1] - 0.014, a[1] + 0.014, tz - 0.028, tz - 0.006)
            xw = xi0 if sx > 0 else xi1
            g.box(st, *sorted((xw + sx * 0.002, xw + sx * 0.024)), y0 - 0.012, y0, b[2] - 0.022, b[2] + 0.022)
    parts += [st, ch]
    return parts, lay
