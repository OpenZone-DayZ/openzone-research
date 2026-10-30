"""Locker base: a two-door 1970s-90s metal cabinet - a body on four feet, two doors on piano
hinges, ventilation slots with louvers above and below in the doors, turn handles with plates,
a lock cylinder at the right door.

Dimensions follow catalogs of clothes lockers of the same design: ShMDO 900 x 1800 x 500 mm,
Garnelle 1850 x 800 x 500 mm; the base uses 800 x 1800 x 500. Everything around the base
(cladding, props) lives in the model generator, not here.
"""
import kgeo as g

DOOR_T = 0.018                             # door thickness: the door face is at y0, the body starts at y0 + DOOR_T
GAP = 0.004                                # gap between the doors and along the contour


def layout(x0, x1, y0, height, foot=0.06):
    """Where the locker parts are (so callers need not recompute them): doors [(xa, xb, za, zb)]
    left to right, the door face y0, heights of the slot rows (bottom, top) - their centers, the
    handle height."""
    zd0, zd1 = foot + 0.025, height - 0.025
    xm = (x0 + x1) / 2
    doors = [(x0 + 0.012, xm - GAP / 2, zd0, zd1), (xm + GAP / 2, x1 - 0.012, zd0, zd1)]
    return dict(doors=doors, face=y0, vents=(zd0 + 0.085, zd1 - 0.095), handle_z=foot + 0.95, xm=xm)


def locker(m, spec, x0, x1, y0, y1, height, foot=0.06, vents=True, handles=True, handle_out=0.0,
           regions=None, prefix="lk"):
    """Locker base. m is a kmodel.Model (parts with regions). The facade is at -Y (y0), the feet end at z=0.

    vents - slots with louvers in the doors (three above and three below; one each at the middle
    LOD); handles - turn handles, plates and the lock cylinder; handle_out - how far the handles
    stand off the door face on spacers (so cladding on the doors does not cover them).
    regions: body, door, vent (slots), handle (handles, hinges), foot (feet).
    spec["lod"]: 0 - all parts, 1 - no hinges and plates, slots without louvers, 2 - body and
    doors as one slab, no feet (the body goes down to the floor)."""
    r = dict(body="lk", door="lk_door", vent="black", handle="steel", foot="black")
    r.update(regions or {})
    lod = spec["lod"]
    lay = layout(x0, x1, y0, height, foot)
    parts = []
    bev = dict(r=0.004, seg=1) if lod == 0 else {}

    # --- body
    bd = m.part(prefix + "_body", r["body"])
    g.box(bd, x0, x1, y0 + DOOR_T, y1, foot if lod < 2 else 0.0, height, **bev)
    parts.append(bd)
    if lod < 2:
        ft = m.part(prefix + "_feet", r["foot"])
        for x in (x0 + 0.015, x1 - 0.055):
            for y in (y0 + DOOR_T + 0.01, y1 - 0.05):
                g.box(ft, x, x + 0.04, y, y + 0.04, 0.0, foot + 0.002)
        parts.append(ft)

    # --- doors
    dr = m.part(prefix + "_doors", r["door"])
    if lod == 2:
        # One slab in place of the doors: same part and face, so the same atlas rectangle.
        (xa, _, za, zb), (_, xb, _, _) = lay["doors"]
        g.box(dr, xa, xb, y0, y0 + DOOR_T + 0.002, za, zb)
        parts.append(dr)
        return parts
    for xa, xb, za, zb in lay["doors"]:
        g.box(dr, xa, xb, y0, y0 + DOOR_T + 0.002, za, zb, **bev)
    parts.append(dr)

    # --- slots: a dark gap with a louver above it (near LOD)
    if vents:
        vt = m.part(prefix + "_vents", r["vent"])
        lv = m.part(prefix + "_louvers", r["door"]) if lod == 0 else None
        for xa, xb, _, _ in lay["doors"]:
            xc = (xa + xb) / 2
            for zc in lay["vents"]:
                for k in ((-1, 0, 1) if lod == 0 else (0,)):
                    z = zc + k * 0.026
                    g.box(vt, xc - 0.07, xc + 0.07, y0 - 0.0008, y0 + 0.001, z - 0.006, z + 0.006)
                    if lv is not None:
                        g.prism(lv, [(y0, z + 0.007), (y0 - 0.008, z + 0.004), (y0, z - 0.002)], (1, 2), xc - 0.072, xc + 0.072)
        parts.append(vt)
        if lv is not None:
            parts.append(lv)

    # --- hinges on the outer edges
    if lod == 0:
        hg = m.part(prefix + "_hinges", r["handle"])
        for (xa, xb, za, zb), xe in zip(lay["doors"], (x0 + 0.004, x1 - 0.004)):
            for z in (za + 0.12, (za + zb) / 2, zb - 0.12):
                g.cyl(hg, (xe, y0 + 0.006, z), "z", 0.0065, 0.09, 8)
        parts.append(hg)

    # --- turn handles at the middle gap, the lock cylinder on the right door
    if handles:
        hd = m.part(prefix + "_handles", r["handle"])
        zh = lay["handle_z"]
        yf = y0 - handle_out
        for (xa, xb, _, _), s in zip(lay["doors"], (-1, 1)):
            xh = (xb - 0.05) if s < 0 else (xa + 0.05)
            if handle_out > 0:
                g.box(hd, xh - 0.012, xh + 0.012, yf, y0 + 0.001, zh - 0.05, zh + 0.05)
            # The plate is thinner than the body bevel: it gets its own bevel, otherwise the faces collapse.
            g.box(hd, xh - 0.018, xh + 0.018, yf - 0.004, yf, zh - 0.045, zh + 0.045, **(dict(r=0.0012, seg=1) if lod == 0 else {}))
            g.cyl(hd, (xh, yf - 0.012, zh), "y", 0.011, 0.016, 10 if lod == 0 else 6)
            g.box(hd, xh - 0.008, xh + 0.008, yf - 0.024, yf - 0.012, zh - 0.075, zh + 0.006)
            if s > 0 and lod == 0:
                g.cyl(hd, (xh, yf - 0.006, zh + 0.09), "y", 0.009, 0.012, 10)
        parts.append(hd)
    return parts
