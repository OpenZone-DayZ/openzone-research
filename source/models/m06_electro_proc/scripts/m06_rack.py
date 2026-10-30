"""B5 base "Instrument rack" for M06: the same rack as kfurn.instrument_rack (sizes, cells,
the pull-out shelf, cables at the back - the same parameters), but with the small details of a real
cabinet: chamfers on the edges, stamped louvres and screws on the side panels, eyebolts on the roof,
a ground bolt, screws with cup washers on the panels, a grille frame; the doors get hinges, bracket
handles of rod, a lock with a seal, an inventory tag and louvres; the pull-out shelf has three-section
slides, a bracket handle and a rubber mat; cables at the back are smooth, with rubber bushings in
the entries.

kfurn.instrument_rack is untouched: M21 and M40 still use it. This function could replace the
original in kfurn (same parameters, new ones with defaults), after which M21 and M40 would get the
same details.

Blender axes: X is width, Y is depth (face toward -Y), Z is up.
"""
import kgeo as g
import m06_bits as b

SHELF_T = 0.012                            # as kfurn.SHELF_T: an instrument stands on z0 + SHELF_T


def rack_opening(x0, x1, side=0.025, rail=0.03):
    """Rack opening between the front rails: (xi0, xi1)."""
    return x0 + side + rail, x1 - side - rail


def instrument_rack(m, spec, x0, x1, y0, y1, height, cells, plinth=0.08, side=0.025, rail=0.03, slide=None,
                    cables=True, regions=None, prefix="rk", tag=None, ground=None, eyebolts=True):
    """Like kfurn.instrument_rack (see there: cells, slide, cables, regions, LODs), plus: tag - (x, z) of
    the middle of the inventory tag on the left door or None; ground - (y, z) of the ground bolt on the
    left side panel or None; eyebolts - eyebolts on the roof. New regions: screw (screws), hinge
    (hinges), tag (the tag; the ground sign is a decal on it), mat (shelf mat), seal (seal)."""
    r = dict(frame="rk", rail="rk_rail", panel="rk_panel", vent="grille_v", door="rk_door", handle="steel",
             inner="rk_inner", foot="black", tray="rk", front="rk_panel", slider="steel", gland="black",
             cable="rubber", screw="steel", hinge="steel", tag="tag", mat="mat", seal="seal", grommet="rubber")
    r.update(regions or {})
    P = m.part
    lod = spec["lod"]
    parts = []
    xi0, xi1 = rack_opening(x0, x1, side, rail)
    zc = height - 0.04                     # bottom of the roof
    xp0, xp1 = xi0 - 0.012, xi1 + 0.012    # panels and doors reach onto the rails
    gap = 0.003
    big = dict(r=0.004, seg=2) if lod == 0 else (dict(r=0.004, seg=1) if lod == 1 else {})
    small = dict(r=0.0015, seg=1) if lod == 0 else {}

    def keep(*ps):
        for p in ps:
            if p is not None and p.bm.faces:
                parts.append(p)

    # --- plinth
    pl = P(prefix + "_plinth", r["foot"])
    g.box(pl, x0 + 0.03, x1 - 0.03, y0 + 0.03, y1 - 0.03, 0.0, plinth + 0.002, **small)
    keep(pl)

    # --- body: side panels, roof, back wall, bottom, shelves of open cells
    fr = P(prefix + "_frame", r["frame"])
    if lod == 2:
        g.box(fr, x0, x1, y0 + 0.02, y1, plinth, height)
    else:
        for xa, xb in ((x0, x0 + side), (x1 - side, x1)):
            g.box(fr, xa, xb, y0, y1, plinth, zc, **big)
        g.box(fr, x0, x1, y0, y1, zc, height, **big)
        g.box(fr, x0 + side, x1 - side, y1 - 0.015, y1, plinth, zc)
        g.box(fr, x0 + side, x1 - side, y0, y1 - 0.015, plinth, plinth + 0.02)
        for z0, z1, kind in cells:
            if kind in ("open", "slide"):
                g.box(fr, x0 + side, x1 - side, y0 + 0.025, y1 - 0.015, z0, z0 + SHELF_T)
    keep(fr)
    if lod == 0:
        # stamped louvres at the top and bottom of the side panels, side panel screws
        lv = P(prefix + "_louvers", r["frame"])
        for fx, sg in ((x0, -1), (x1, 1)):
            for zb in (plinth + 0.13, zc - 0.33):
                b.louvers(lv, fx, sg, y0 + 0.17, y1 - 0.17, zb, 6, 0.034)
        sc = P(prefix + "_side_screws", r["screw"])
        for fx, sg in ((x0, -1), (x1, 1)):
            for yy in (y0 + 0.045, y1 - 0.045):
                for zz in (plinth + 0.05, zc - 0.05):
                    b.screw(sc, fx, yy, zz, 0.0042, axis=(sg, 0, 0))
        keep(lv, sc)
        if eyebolts:
            eb = P(prefix + "_eyebolts", r["screw"])
            for xx, yy, yaw in ((x0 + 0.06, y0 + 0.06, 0.0), (x1 - 0.06, y0 + 0.06, 0.0), (x0 + 0.06, y1 - 0.06, 0.0),
                                (x1 - 0.06, y1 - 0.06, 0.0)):
                b.eye_bolt(eb, xx, yy, height, yaw=yaw)
            keep(eb)
        if ground:
            # ground bolt: washer, nut, stud; a sign plate above it
            gy, gz = ground
            gb = P(prefix + "_ground", r["screw"])
            b.lathe(gb, (x0, gy, gz), (-1, 0, 0), [(0.010, 0.0), (0.010, 0.0015)], 10)
            b.lathe(gb, (x0, gy, gz), (-1, 0, 0), [(0.0095, 0.0015), (0.0095, 0.0075)], 6, ref=(0, 0, 1))
            b.lathe(gb, (x0, gy, gz), (-1, 0, 0), [(0.0045, 0.0075), (0.0045, 0.016), (0.0035, 0.017)], 8)
            gt = P(prefix + "_ground_plate", r["tag"])
            g.box(gt, x0 - 0.0008, x0, gy - 0.016, gy + 0.016, gz + 0.022, gz + 0.054)
            keep(gb, gt)
    if lod < 2:
        rl = P(prefix + "_rails", r["rail"])
        for xa in (x0 + side, x1 - side - rail):
            g.box(rl, xa, xa + rail, y0, y0 + 0.02, plinth + 0.02, zc, **small)
        keep(rl)
        inn = P(prefix + "_inner", r["inner"])
        for z0, z1, kind in cells:
            if kind in ("open", "slide"):
                g.box(inn, x0 + side, x1 - side, y1 - 0.017, y1 - 0.015, z0 + SHELF_T, z1)
        keep(inn)

    # --- panels, grilles, doors
    pn = P(prefix + "_panels", r["panel"])
    vt = P(prefix + "_vents", r["vent"]) if lod < 2 else None
    dr = P(prefix + "_doors", r["door"])
    hd = P(prefix + "_handles", r["handle"]) if lod < 2 else None
    bo = P(prefix + "_bosses", r["handle"]) if lod == 0 else None
    ps = P(prefix + "_panel_screws", r["screw"]) if lod == 0 else None
    for z0, z1, kind in cells:
        za, zb = z0 + gap, z1 - gap
        if kind in ("blank", "vent"):
            g.box(pn, xp0, xp1, y0 - 0.003, y0, za, zb, **small)
            if kind == "vent" and vt is not None:
                w, h = xp1 - xp0 - 0.08, zb - za - 0.03
                cx, cz = (xp0 + xp1) / 2, (za + zb) / 2
                g.box(vt, cx - w / 2, cx + w / 2, y0 - 0.0042, y0 - 0.003, cz - h / 2, cz + h / 2)
                if lod == 0:
                    b.bezel(pn, cx, cz, (w + 0.014, h + 0.014, 0.006), (w, h, 0.002), y0 - 0.003, y0 - 0.0062,
                            y_in=y0 - 0.0042)
            if ps is not None:
                for xs in (xp0 + 0.012, xp1 - 0.012):
                    for zs in ((za + 0.015, zb - 0.015) if zb - za > 0.06 else ((za + zb) / 2,)):
                        b.screw(ps, xs, y0 - 0.003, zs, 0.0034)
        elif kind == "doors":
            xm = (xp0 + xp1) / 2
            yd = y0 - 0.018                                      # face of the doors
            for xa, xb in ((xp0, xm - gap / 2), (xm + gap / 2, xp1)):
                g.box(dr, xa, xb, yd, y0, za, zb, **big)
            # handles at hand height, the lock above the right one (in kfurn the lock sits on the upper end of the
            # handle)
            zh = min(zb - 0.20, za + 0.40)
            if hd is not None:
                for s in (-1, 1):
                    xh = xm + s * 0.04
                    b.u_handle(hd, (xh, yd, zh - 0.07), (xh, yd, zh + 0.07), (0, -1, 0), 0.030, 0.0052, lod=lod,
                               bosses=bo)
            if lod == 0:
                # hinges on the outer edges
                hg = P(prefix + "_hinges", r["hinge"])
                for xh, sg in ((xp0, -1), (xp1, 1)):
                    for zh0 in (za + 0.07, zb - 0.12):
                        b.hinge(hg, xh + sg * 0.0035, y0 - 0.013, zh0, zh0 + 0.05, 0.0050)
                        g.box(hg, *sorted((xh + sg * 0.003, xh - sg * 0.020)), yd - 0.0008, yd, zh0 + 0.004, zh0 + 0.046)
                # lock on the right door: a cylinder, a keyway plug; a seal on a wire to the left door
                lk = P(prefix + "_lock", r["handle"])
                xl, zl = xm + 0.04, zb - 0.10
                b.lathe(lk, (xl, yd, zl), b.FRONT, [(0.0125, 0.0), (0.0125, 0.0040), (0.0110, 0.0060),
                                                    (0.0080, 0.0062)], 12)
                ks = P(prefix + "_lock_slot", r["inner"])
                g.box(ks, xl - 0.0011, xl + 0.0011, yd - 0.0066, yd - 0.0058, zl - 0.0045, zl + 0.0045)
                ey = P(prefix + "_seal_eyes", r["handle"])
                for xe in (xm - 0.012, xm + 0.012):
                    b.lathe(ey, (xe, yd, zl + 0.022), b.FRONT, [(0.0028, 0.0), (0.0028, 0.006), (0.0, 0.0065)], 6)
                sw = P(prefix + "_seal_wire", r["handle"])
                g.pipe(sw, b.spline([(xm - 0.012, yd - 0.005, zl + 0.022), (xm - 0.004, yd - 0.007, zl + 0.012),
                                     (xm, yd - 0.008, zl - 0.004), (xm + 0.004, yd - 0.007, zl + 0.012),
                                     (xm + 0.012, yd - 0.005, zl + 0.022)], 2), 0.0005, 4)
                sl = P(prefix + "_seal", r["seal"])
                b.lathe(sl, (xm, yd - 0.0045, zl - 0.010), b.FRONT, [(0.0062, 0.0), (0.0062, 0.0035)], 12, cap0=True)
                keep(hg, lk, ks, ey, sw, sl)
                # stamped louvres at the bottom of each door
                dl = P(prefix + "_door_louvers", r["door"])
                for xa, xb in ((xp0, xm - gap / 2), (xm + gap / 2, xp1)):
                    b.louvers_y(dl, yd, xa + 0.06, xb - 0.06, za + 0.05, 5, 0.026)
                keep(dl)
                if tag:
                    # inventory tag: an aluminium plate on two rivets (the number is the tag decal)
                    tx, tz = tag
                    tg = P(prefix + "_tag", r["tag"])
                    b.plate(tg, tx, tz, 0.070, 0.030, 0.003, yd, yd - 0.0008)
                    rv = P(prefix + "_tag_rivets", r["screw"])
                    for xr in (tx - 0.029, tx + 0.029):
                        b.lathe(rv, (xr, yd - 0.0008, tz), b.FRONT, [(0.0020, 0.0), (0.0016, 0.0008), (0.0, 0.0012)], 8)
                    keep(tg, rv)
    keep(pn, vt, dr, hd, bo, ps)

    # --- pull-out shelf
    if slide:
        zs, pull, depth = slide["z"], slide["pull"], slide["depth"]
        ya, yb = y0 - pull, y0 - pull + depth
        tr = P(prefix + "_tray", r["tray"])
        g.box(tr, xi0 + 0.005, xi1 - 0.005, ya, yb, zs - 0.012, zs, **small)
        if lod < 2:
            for xa in (xi0 + 0.005, xi1 - 0.017):
                g.box(tr, xa, xa + 0.012, ya, yb, zs, zs + 0.015, **small)
            g.box(tr, xi0 + 0.017, xi1 - 0.017, yb - 0.012, yb, zs, zs + 0.015, **small)
        keep(tr)
        fp = P(prefix + "_tray_front", r["front"])
        g.box(fp, xp0 + 0.004, xp1 - 0.004, ya - 0.016, ya, zs - 0.045, zs + 0.025, **big)
        keep(fp)
        if lod < 2:
            mt = P(prefix + "_tray_mat", r["mat"])
            g.box(mt, xi0 + 0.019, xi1 - 0.019, ya + 0.004, yb - 0.014, zs, zs + 0.003,
                  **(dict(r=0.0012, seg=1) if lod == 0 else {}))
            keep(mt)
            # three-section slides: on the tray, intermediate, on the rack
            sl = P(prefix + "_slides", r["slider"])
            for s, xe in ((-1, xi0 + 0.005), (1, xi1 - 0.005)):
                for (da, db), (za_, zb_), (ys0, ys1) in (((0.0, 0.007), (zs - 0.036, zs - 0.010), (ya + 0.02, yb - 0.02)),
                                                        ((0.007, 0.013), (zs - 0.040, zs - 0.006),
                                                         (ya + 0.13, y0 + 0.17)),
                                                        ((0.013, 0.019), (zs - 0.044, zs - 0.002),
                                                         (y0 + 0.02, y0 + depth - 0.03))):
                    g.box(sl, *sorted((xe + s * da, xe + s * db)), ys0, ys1, za_, zb_)
            keep(sl)
            if lod == 0:
                st = P(prefix + "_slide_stops", r["screw"])
                for s, xe in ((-1, xi0 + 0.005), (1, xi1 - 0.005)):
                    for yy in (ya + 0.03, ya + 0.14):
                        b.screw(st, xe + s * 0.007, yy, zs - 0.023, 0.0022, axis=(s, 0, 0))
                keep(st)
            xm = (xi0 + xi1) / 2
            gr = P(prefix + "_tray_grip", r["handle"])
            gb = P(prefix + "_tray_grip_bosses", r["handle"]) if lod == 0 else None
            b.u_handle(gr, (xm - 0.10, ya - 0.016, zs - 0.012), (xm + 0.10, ya - 0.016, zs - 0.012), (0, -1, 0), 0.026,
                       0.0052, lod=lod, bosses=gb)
            keep(gr, gb)

    # --- cables at the back
    if cables and lod < 2:
        xm = (x0 + x1) / 2
        zg0, zg1 = plinth + 0.06, plinth + 0.16
        zm = (zg0 + zg1) / 2
        if lod == 0:
            rv = P(prefix + "_back_vents", r["vent"])
            for za, zb in ((zc - 0.62, zc - 0.16), (plinth + 0.24, plinth + 0.52)):
                g.box(rv, x0 + side + 0.06, x1 - side - 0.06, y1, y1 + 0.0015, za, zb)
            keep(rv)
        gl = P(prefix + "_glands", r["gland"])
        g.box(gl, xm - 0.12, xm + 0.12, y1, y1 + 0.012, zg0, zg1, **small)
        g.box(gl, xm - 0.10, xm + 0.10, y1, y1 + 0.006, zc - 0.10, zc - 0.04, **small)
        keep(gl)
        cb = P(prefix + "_cables", r["cable"])
        gm = P(prefix + "_grommets", r["grommet"]) if lod == 0 else None
        sd = 6 if lod == 0 else 4
        for k, (dx, rr) in enumerate(((-0.07, 0.009), (-0.02, 0.006), (0.03, 0.007), (0.08, 0.005))):
            xe = xm + dx * 2.5 + 0.05 * k
            pts = [(xm + dx, y1 + 0.006, zm), (xm + dx, y1 + 0.035, zm - 0.004), (xm + dx * 1.05, y1 + 0.065, zm - 0.03),
                   (xm + dx * 1.15, y1 + 0.09, plinth * 0.8), (xm + dx * 1.3, y1 + 0.11, plinth * 0.3),
                   (xm + dx * 1.5, y1 + 0.15, rr), (xm + dx * 2.0 + 0.02 * k, y1 + 0.28, rr), (xe, y1 + 0.45 + 0.08 * k, rr)]
            g.pipe(cb, pts if lod == 0 else [pts[i] for i in (0, 2, 4, 5, 7)], rr, sd)
            if gm is not None:
                b.lathe(gm, (xm + dx, y1 + 0.012, zm), (0, 1, 0), [(rr + 0.003, 0.0), (rr + 0.004, 0.003),
                                                                   (rr + 0.0015, 0.006)], 8, cap1=False)
        xv = xm + 0.10
        pts = [(xm + 0.04, y1 + 0.004, zc - 0.07), (xm + 0.08, y1 + 0.03, zc - 0.10), (xv, y1 + 0.03, zc - 0.25),
               (xv, y1 + 0.03, zg1 + 0.12), (xm + 0.09, y1 + 0.02, zg1 + 0.02), (xm + 0.08, y1 + 0.006, zm + 0.02)]
        g.pipe(cb, b.spline(pts, 2) if lod == 0 else [pts[i] for i in (0, 2, 3, 5)], 0.007, sd)
        keep(cb, gm)
        if lod == 0:
            cl = P(prefix + "_clips", r["handle"])
            for z in (zc - 0.45, (zc + zg1) / 2, zg1 + 0.30):
                g.box(cl, xv - 0.014, xv + 0.014, y1, y1 + 0.042, z - 0.008, z + 0.008)
            keep(cl)
    return parts
