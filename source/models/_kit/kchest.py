"""Chest base: a 1970s-90s shop chest freezer - a body on four feet, a recessed dark plinth, a
hinged lid with an overhang and a gasket, hinges at the back, a lid handle and a lock cylinder at
the front, a compressor grille with louvers on the right end.

Dimensions follow m07 (generator in source/models/m07_sky_pack_bio): 1500 x 860 x 680 mm (width x
height x depth). There are no datasheets of Soviet chest freezers; by volume class, Biryusa chest
freezers of the same design: CF32 (320 l) - 1085 x 885 x 665 mm, B-560KX (510 l) - 1790 x 810 x
665 mm; a ~420 l chest between them is ~1.5 m wide.

The code is the build_chest() of the m07 generator with the constants turned into parameters;
m07 itself still uses its own copy. Everything around the base (panel, lamps, cladding, props)
lives in the model generator.
"""
import kgeo as g

# Dimensions of m07, m
X0, X1, Y0, Y1 = -0.75, 0.75, -0.34, 0.34
ZFOOT, ZG, ZL = 0.03, 0.80, 0.86             # body bottom (feet), lid seam, lid top
LIP = 0.006                                  # lid overhang
GRILLE = (-0.24, 0.24, 0.08, 0.34)           # compressor grille on the right end: y0, y1, z0, z1


def layout(x0=X0, x1=X1, y0=Y0, y1=Y1, zg=ZG, zl=ZL, lip=LIP):
    """Where the chest parts are: lid extents, seam, grille, handle, hinges (so callers need not recompute them)."""
    return dict(lid=(x0 - lip, x1 + lip, y0 - lip, y1 + lip, zg + 0.006, zl), seam=zg, top=zl,
                grille=GRILLE, handle_x=(-0.22, 0.22), hinges_x=(-0.50, 0.50), lock_x=0.30)


def chest(m, spec, x0=X0, x1=X1, y0=Y0, y1=Y1, zfoot=ZFOOT, zg=ZG, zl=ZL, lip=LIP, grille=True,
          handle=True, lock=True, regions=None, prefix="chest"):
    """Chest base. m is a kmodel.Model (parts with regions). The front is at -Y (y0), the feet end at z=0.

    grille - compressor grille with louvers on the right end; handle - lid handle and rear hinges;
    lock - lock cylinder under the lid.
    regions: body, front (the front face as a separate region, for decals), lid, dark (plinth,
    feet), gasket, grille, steel (hinges, lock cylinder), handle.
    spec["lod"]: 0 - everything, 1 - no feet and no lock cylinder, fewer louvers, 2 - no louvers,
    handle and hinges; spec["bev"] - bevel segments (0 - no bevel)."""
    r = dict(body="chest", front="chest_front", lid="lid", dark="dark", gasket="gasket", grille="grille",
             steel="steel", handle="black")
    r.update(regions or {})
    lod, bev = spec["lod"], spec.get("bev", 0)
    rr = 0.012 if bev else 0.0
    parts = []
    # Body: the front is a separate region (decals); sides and back form the rest.
    body = m.part(prefix + "_body", r["body"])
    g.box(body, x0, x1, y0 + 0.002, y1, zfoot, zg, r=rr, seg=bev)
    parts.append(body)
    fr = m.part(prefix + "_front", r["front"])
    g.box(fr, x0 + 0.02, x1 - 0.02, y0, y0 + 0.004, zfoot + 0.05, zg - 0.01)
    parts.append(fr)
    # Plinth: recessed, dark.
    pl = m.part(prefix + "_plinth", r["dark"])
    g.box(pl, x0 + 0.03, x1 - 0.03, y0 - 0.001, y0 + 0.01, zfoot, zfoot + 0.045)
    parts.append(pl)
    # Lid with an overhang, gasket.
    ld = m.part(prefix + "_lid", r["lid"])
    g.box(ld, x0 - lip, x1 + lip, y0 - lip, y1 + lip, zg + 0.006, zl, r=0.015 if bev else 0.0, seg=bev)
    parts.append(ld)
    gs = m.part(prefix + "_gasket", r["gasket"])
    g.box(gs, x0 + 0.004, x1 - 0.004, y0 + 0.004, y1 - 0.004, zg - 0.002, zg + 0.007)
    parts.append(gs)
    if lod == 0:
        ft = m.part(prefix + "_feet", r["dark"])
        for x in (x0 + 0.06, x1 - 0.06):
            for y in (y0 + 0.06, y1 - 0.06):
                g.cyl(ft, (x, y, zfoot / 2), "z", 0.022, zfoot, 6)
        parts.append(ft)
    if grille:
        gr = m.part(prefix + "_grille", r["grille"])
        gy0, gy1, gz0, gz1 = GRILLE
        g.box(gr, x1 - 0.004, x1 + 0.002, gy0, gy1, gz0, gz1)
        parts.append(gr)
        if lod < 2:
            lv = m.part(prefix + "_louvers", r["body"])
            n = 9 if lod == 0 else 5
            for k in range(n):
                z = gz0 + 0.02 + (gz1 - gz0 - 0.04) * k / (n - 1)
                g.box(lv, x1, x1 + 0.012, gy0 + 0.01, gy1 - 0.01, z - 0.004, z + 0.004)
            parts.append(lv)
    if handle and lod < 2:
        hd = m.part(prefix + "_handle", r["handle"])
        g.box(hd, -0.22, 0.22, y0 - lip - 0.03, y0 - lip, zg + 0.012, zg + 0.030, r=0.004 if bev else 0,
              seg=1 if bev else 0)
        g.box(hd, -0.22, -0.19, y0 - lip - 0.03, y0 - lip, zg + 0.012, zl - 0.006)
        g.box(hd, 0.19, 0.22, y0 - lip - 0.03, y0 - lip, zg + 0.012, zl - 0.006)
        hg = m.part(prefix + "_hinges", r["steel"])
        for x in (-0.50, 0.50):
            g.box(hg, x - 0.05, x + 0.05, y1, y1 + 0.02, zg - 0.05, zg + 0.03)
        parts += [hd, hg]
    if lock and lod == 0:
        lk = m.part(prefix + "_lock", r["steel"])
        g.cyl(lk, (0.30, y0 - 0.004, zg - 0.025), "y", 0.011, 0.010, 10)
        parts.append(lk)
    return parts
