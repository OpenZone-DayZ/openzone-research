"""Laboratory furniture for models where an instrument stands on a cabinet: a body on a recessed
plinth, a worktop with an overhang, fronts - drawers and doors with bracket handles.

A Soviet laboratory cabinet: an enameled body, a worktop in chemical-resistant plastic, chrome
bracket handles. The working surface is 0.75-0.90 m high.

workbench - the workbench base (m05, m11, m15, m23, m27): an electronics assembler's table with a
cabinet and a superstructure board. The dimensions are in the m05 generator
(source/models/m05_electro_pack).

instrument_rack - the instrument rack base (m06, m21): a rack cabinet with cells for instruments,
a pull-out shelf and cables at the back. The dimensions and contents are in the m06 generator
(source/models/m06_electro_proc).
"""
import kgeo as g


def lab_cabinet(m, spec, x0, x1, y0, y1, top, columns, regions=None, prefix="cab"):
    """m is a kmodel.Model (parts with regions). The facade is at -Y (y0). top - the worktop height.
    columns: [(width share, [facade height shares, ...], "drawer" | "door"), ...] left to right:
    a column of drawers ("drawer") or a single door ("door"). regions: body, top, front, handle, plinth.
    spec["lod"]: 0 - all parts, 1 - no handles and gaps, 2 - the body and the worktop."""
    r = dict(body="cab", top="worktop", front="cab_front", handle="steel", plinth="black")
    r.update(regions or {})
    lod = spec["lod"]
    parts = []
    t_top, plinth_h, inset = 0.03, 0.08, 0.04
    body = m.part(prefix + "_body", r["body"])
    g.box(body, x0, x1, y0 + 0.02, y1, plinth_h if lod < 2 else 0.0, top - t_top)
    parts.append(body)
    wt = m.part(prefix + "_top", r["top"])
    g.box(wt, x0 - 0.01, x1 + 0.01, y0 - 0.005, y1 + 0.005, top - t_top, top,
          r=0.004 if lod == 0 else 0, seg=1 if lod == 0 else 0)
    parts.append(wt)
    if lod < 2:
        pl = m.part(prefix + "_plinth", r["plinth"])
        g.box(pl, x0 + inset, x1 - inset, y0 + inset, y1 - inset, 0.0, plinth_h + 0.002)
        parts.append(pl)
    gap, t = 0.004, 0.018
    z_lo, z_hi = plinth_h + gap, top - t_top - gap
    if lod == 2:
        # One slab in place of the fronts: the same part and the same face as the fronts of the near
        # LOD, hence the same atlas rectangle - the drawers and the door show, not the bare body behind them.
        fr = m.part(prefix + "_fronts", r["front"])
        g.box(fr, x0 + gap, x1 - gap, y0 - t + 0.02, y0 + 0.02, z_lo, z_hi)
        parts.append(fr)
        return parts
    # fronts
    fr = m.part(prefix + "_fronts", r["front"])
    hd = m.part(prefix + "_handles", r["handle"]) if lod == 0 else None
    total = sum(c[0] for c in columns)
    xa = x0 + gap
    for share, heights, kind in columns:
        w = (x1 - x0 - gap) * share / total
        xb = xa + w - gap
        if kind == "door":
            heights = [1.0]
        hs = sum(heights)
        za = z_hi
        for h in heights:
            zb = za - (z_hi - z_lo) * h / hs
            g.box(fr, xa, xb, y0 - t + 0.02, y0 + 0.02, zb + gap / 2, za - gap / 2)
            if hd is not None:
                cx = (xa + xb) / 2 if kind == "drawer" else (xb - 0.05)
                cz = (za - 0.045) if kind == "drawer" else (za - 0.12)
                if kind == "drawer":
                    pts = [(cx - 0.06, y0 + 0.02 - t, cz), (cx - 0.06, y0 - t - 0.008, cz),
                           (cx + 0.06, y0 - t - 0.008, cz), (cx + 0.06, y0 + 0.02 - t, cz)]
                    g.sweep(hd, pts, (0, 0, 1), 0.004, 0.004)
                else:
                    pts = [(cx, y0 + 0.02 - t, cz + 0.06), (cx, y0 - t - 0.008, cz + 0.06),
                           (cx, y0 - t - 0.008, cz - 0.06), (cx, y0 + 0.02 - t, cz - 0.06)]
                    g.sweep(hd, pts, (1, 0, 0), 0.004, 0.004)
            za = zb
        xa = xb + gap
    parts.append(fr)
    if hd is not None:
        parts.append(hd)
    return parts


def _drawer_handle(hd, cx, y_face, cz, half=0.06):
    """A drawer bracket handle: out of the facade, along X, back into the facade."""
    pts = [(cx - half, y_face, cz), (cx - half, y_face - 0.028, cz),
           (cx + half, y_face - 0.028, cz), (cx + half, y_face, cz)]
    g.sweep(hd, pts, (0, 0, 1), 0.004, 0.004)


def workbench(m, spec, x0, x1, y0, y1, top, panel_top, shelf_d, cab_w=0.42, drawers=(1.0, 1.0, 1.0, 1.4),
              worktop="metal", outlets=4, lamp=True, regions=None, prefix="wb"):
    """Workbench base: a steel assembler's table, a cabinet with drawers on the right, a
    superstructure board at the back with a shelf on top, a socket strip on the board and a light
    under the shelf. Props (the fittings of the machine) live in the model generator, not here.

    m is a kmodel.Model. The facade is at -Y (y0), the cabinet is at x1. top - the working surface
    height, panel_top - the top of the superstructure shelf, shelf_d - the shelf depth (from y1
    forward). drawers - shares of the cabinet drawer heights from top to bottom. worktop: "metal" -
    a steel sheet with a bent edge, "board" - planks (the model assigns a wood kind to the top
    region). outlets - how many sockets on the strip (0 - no strip), lamp - the light under the shelf.
    regions: frame (frame, cabinet, shelf), top, front (drawer fronts), panel (the board), handle,
    foot, outlet (body of the strip and sockets), socket (socket holes), lamp (light body),
    diffuser, switch (switch key).
    spec["lod"]: 0 - all parts, 1 - no handles, socket holes and feet, 2 - one section: the
    worktop, the left post, the cabinet, the board with the shelf.

    Where things are (so callers need not recompute): the worktop is on top at top; the shelf has
    its top at panel_top and spans y from y1 - shelf_d to y1; the board face is y1 - 0.02; the
    socket strip is on the board at z top + 0.06 .. top + 0.12, x from x0 + 0.30, 0.12 m per
    socket and 0.08 for the switch."""
    r = dict(frame="wb", top="wb_top", front="wb_front", panel="wb_panel", handle="steel", foot="black",
             outlet="outlet", socket="black", lamp="wb", diffuser="plastic_white", switch="lamp_r")
    r.update(regions or {})
    lod = spec["lod"]
    parts = []
    t_top = 0.04 if worktop == "board" else 0.03
    zu = top - t_top                       # underside of the worktop
    leg, apron = 0.04, 0.06
    cx0 = x1 - cab_w                       # cabinet: cx0..x1
    yp = y1 - 0.02                         # board face

    # --- worktop
    wt = m.part(prefix + "_top", r["top"])
    if worktop == "board":
        n_pl = 4
        w = (y1 - y0 + 0.015) / n_pl
        for k in range(n_pl):
            ya = y0 - 0.01 + k * w + (0.0015 if k else 0.0)
            yb = y0 - 0.01 + (k + 1) * w - (0.0015 if k < n_pl - 1 else 0.0)
            g.box(wt, x0 - 0.01, x1 + 0.01, ya, yb, zu, top)
    else:
        g.box(wt, x0 - 0.01, x1 + 0.01, y0 - 0.01, y1 + 0.005, zu, top,
              r=0.004 if lod == 0 else 0, seg=1 if lod == 0 else 0)
    parts.append(wt)

    # --- frame: left legs, aprons, braces, a modesty panel for the knee space, the cabinet
    fr = m.part(prefix + "_frame", r["frame"])
    z_leg = 0.02 if lod == 0 else 0.0
    if lod == 2:
        g.box(fr, x0 + 0.01, x0 + 0.01 + leg, y0 + 0.03, y1 - 0.03, 0.0, zu)
    else:
        for y in (y0 + 0.03, y1 - 0.03 - leg):
            g.box(fr, x0 + 0.01, x0 + 0.01 + leg, y, y + leg, z_leg, zu)
        g.box(fr, x0 + 0.015, x0 + 0.005 + leg, y0 + 0.03 + leg, y1 - 0.03 - leg, 0.10, 0.14)
        g.box(fr, x0 + 0.01 + leg, cx0, y0 + 0.03, y0 + 0.05, zu - apron, zu)
        g.box(fr, x0 + 0.015, x0 + 0.005 + leg, y0 + 0.03 + leg, y1 - 0.03 - leg, zu - apron, zu)
        g.box(fr, x0 + 0.01 + leg, cx0, y1 - 0.07, y1 - 0.04, 0.10, 0.13)
        g.box(fr, x0 + 0.01 + leg, cx0, y1 - 0.042, y1 - 0.032, 0.40, zu)
    plinth = 0.08 if lod < 2 else 0.0
    g.box(fr, cx0, x1, y0 + 0.02, y1 - 0.01, plinth, zu)
    parts.append(fr)
    if lod < 2:
        pl = m.part(prefix + "_plinth", r["foot"])
        g.box(pl, cx0 + 0.03, x1 - 0.03, y0 + 0.05, y1 - 0.04, 0.0, plinth + 0.002)
        if lod == 0:
            for y in (y0 + 0.03 + leg / 2, y1 - 0.03 - leg / 2):
                g.cyl(pl, (x0 + 0.01 + leg / 2, y, 0.01), "z", 0.022, 0.02, 8)
        parts.append(pl)

    # --- cabinet drawer fronts
    gap, t = 0.004, 0.018
    yf = y0 + 0.02                         # cabinet body face
    z_lo, z_hi = plinth + gap, zu - gap
    fo = m.part(prefix + "_fronts", r["front"])
    if lod == 2:
        # one slab in place of the fronts - the same part and face, the same atlas rectangle
        g.box(fo, cx0 + gap, x1 - gap, yf - t, yf, z_lo, z_hi)
    else:
        hd = m.part(prefix + "_handles", r["handle"]) if lod == 0 else None
        hs = sum(drawers)
        za = z_hi
        for h in drawers:
            zb = za - (z_hi - z_lo) * h / hs
            g.box(fo, cx0 + gap, x1 - gap, yf - t, yf, zb + gap / 2, za - gap / 2)
            if hd is not None:
                cxm = (cx0 + x1) / 2
                _drawer_handle(hd, cxm, yf - t, za - 0.055)
                # an empty frame for a label above the handle
                g.box(hd, cxm - 0.035, cxm + 0.035, yf - t - 0.002, yf - t, za - 0.035, za - 0.015)
            za = zb
        if hd is not None:
            parts.append(hd)
    parts.append(fo)

    # --- superstructure: posts, the board, a shelf with a rim and gussets
    ys0 = y1 - shelf_d                     # front of the shelf
    t_sh = 0.02
    zs = panel_top - t_sh                  # underside of the shelf
    pn = m.part(prefix + "_panel", r["panel"])
    g.box(pn, x0 + 0.03, x1 - 0.03, yp, y1 - 0.008, top, zs)
    parts.append(pn)
    sh = m.part(prefix + "_shelf", r["frame"])
    g.box(sh, x0, x1, ys0, y1, zs, panel_top)
    for xa in (x0, x1 - 0.03):
        g.box(sh, xa, xa + 0.03, y1 - 0.035, y1, top, zs)              # posts
    if lod < 2:
        g.box(sh, x0, x1, ys0, ys0 + 0.004, panel_top, panel_top + 0.015)   # rim
        if lod == 0:
            for xa in (x0 + 0.005, x1 - 0.025, (x0 + x1) / 2 - 0.01):
                g.prism(sh, [(yp, zs - 0.16), (yp, zs), (ys0 + 0.03, zs)], (1, 2), xa, xa + 0.02)
    parts.append(sh)
    if lod == 2:
        return parts

    # --- socket strip with a switch
    if outlets:
        ox0 = x0 + 0.30
        ox1 = ox0 + 0.12 * outlets + 0.08
        za, zb = top + 0.06, top + 0.12
        zc = (za + zb) / 2
        ol = m.part(prefix + "_outlets", r["outlet"])
        g.box(ol, ox0, ox1, yp - 0.04, yp, za, zb, r=0.004 if lod == 0 else 0, seg=1 if lod == 0 else 0)
        if lod == 0:
            for k in range(outlets):
                g.cyl(ol, (ox0 + 0.06 + 0.12 * k, yp - 0.043, zc), "y", 0.021, 0.006, 12)
        parts.append(ol)
        if lod == 0:
            sk = m.part(prefix + "_sockets", r["socket"])
            for k in range(outlets):
                xc = ox0 + 0.06 + 0.12 * k
                for s in (-1, 1):
                    g.cyl(sk, (xc + s * 0.0095, yp - 0.0455, zc), "y", 0.0028, 0.002, 6)
            parts.append(sk)
        sw = m.part(prefix + "_switch", r["switch"])
        g.box(sw, ox1 - 0.06, ox1 - 0.02, yp - 0.048, yp - 0.039, zc - 0.018, zc + 0.018)
        parts.append(sw)

    # --- light under the shelf (a fluorescent tube in a housing)
    if lamp:
        lx0, lx1 = x0 + 0.12, x1 - 0.12
        ly0, ly1 = ys0 + 0.02, ys0 + 0.11
        lm = m.part(prefix + "_lamp", r["lamp"])
        g.box(lm, lx0, lx1, ly0, ly1, zs - 0.045, zs)
        parts.append(lm)
        df = m.part(prefix + "_diffuser", r["diffuser"])
        g.box(df, lx0 + 0.01, lx1 - 0.01, ly0 + 0.01, ly1 - 0.01, zs - 0.05, zs - 0.044)
        parts.append(df)
    return parts


SHELF_T = 0.012                            # thickness of a cell shelf: an instrument stands at z0 + SHELF_T


def rack_opening(x0, x1, side=0.025, rail=0.03):
    """The rack opening between the front rails: (xi0, xi1)."""
    return x0 + side + rail, x1 - side - rail


def instrument_rack(m, spec, x0, x1, y0, y1, height, cells, plinth=0.08, side=0.025, rail=0.03, slide=None,
                    cables=True, regions=None, prefix="rk"):
    """Instrument rack base: a rack cabinet of side walls, a roof, a back wall and a plinth,
    perforated rails at the front, the opening divided into cells. Instruments (the contents) live
    in the model generator, not here: the base provides the cell shelves, panels, doors, a pull-out
    shelf and cables at the back.

    m is a kmodel.Model. The facade is at -Y (y0). cells: [(z0, z1, kind)] from bottom to top, kind:
      "open"  - a shelf at z0, the generator places the instrument: it stands at z0 + SHELF_T, its
                face is at y0 + 0.012, its width is rack_opening;
      "blank" - a blind panel on the rails; "vent" - a panel with a grille; "doors" - two doors
                with handles and a lock (the lower compartment); "slide" - the pull-out shelf compartment.
    slide: dict(z=top of the shelf, pull=how far it is pulled out of the rack, depth=depth) - a tray
      with rims and a front bar with a handle on telescopic slides. The generator places the shelf
      contents (a block, probes): the tray spans rack_opening -/+ 0.005 in x and y0 - pull to
      y0 - pull + depth in y.
    cables: a harness from the cable gland at the bottom of the back wall to the floor and backward,
      and a cable from the upper gland down the back wall on brackets into the same lower gland.
    regions: frame (side walls, roof, back wall, shelves), rail (rails), panel (cell panels),
      vent (grilles), door, handle (handles, screws, lock, brackets), inner (the dark behind
      instruments), foot (plinth), tray, front (tray bar), slider (slides), gland (glands), cable.
    spec["lod"]: 0 - all parts, 1 - no screws, handles, grilles and brackets, 2 - one section: the
      body as a box, the plinth, slabs in place of panels and doors, the tray with a bar.

    For several racks in a row, call this once per rack with shifted x0/x1 and its own prefix:
    parts with different names take the atlas separately, and each rack has its own contents."""
    r = dict(frame="rk", rail="rk_rail", panel="rk_panel", vent="grille_v", door="rk_door", handle="steel",
             inner="rk_inner", foot="black", tray="rk", front="rk_panel", slider="steel", gland="black",
             cable="rubber")
    r.update(regions or {})
    lod = spec["lod"]
    parts = []
    xi0, xi1 = rack_opening(x0, x1, side, rail)
    zc = height - 0.04                     # underside of the roof
    xp0, xp1 = xi0 - 0.012, xi1 + 0.012    # panels and doors overlap the rails
    gap = 0.003
    bev = dict(r=0.003, seg=1) if lod == 0 else {}

    # --- plinth
    pl = m.part(prefix + "_plinth", r["foot"])
    g.box(pl, x0 + 0.03, x1 - 0.03, y0 + 0.03, y1 - 0.03, 0.0, plinth + 0.002)
    parts.append(pl)

    # --- body: side walls, roof, back wall, bottom, shelves of the open cells
    fr = m.part(prefix + "_frame", r["frame"])
    if lod == 2:
        g.box(fr, x0, x1, y0 + 0.02, y1, plinth, height)
    else:
        for xa, xb in ((x0, x0 + side), (x1 - side, x1)):
            g.box(fr, xa, xb, y0, y1, plinth, zc, **bev)
        g.box(fr, x0, x1, y0, y1, zc, height, **bev)
        g.box(fr, x0 + side, x1 - side, y1 - 0.015, y1, plinth, zc)
        g.box(fr, x0 + side, x1 - side, y0, y1 - 0.015, plinth, plinth + 0.02)
        for z0, z1, kind in cells:
            if kind in ("open", "slide"):
                g.box(fr, x0 + side, x1 - side, y0 + 0.025, y1 - 0.015, z0, z0 + SHELF_T)
    parts.append(fr)
    if lod < 2:
        rl = m.part(prefix + "_rails", r["rail"])
        for xa in (x0 + side, x1 - side - rail):
            g.box(rl, xa, xa + rail, y0, y0 + 0.02, plinth + 0.02, zc)
        parts.append(rl)
        # the dark behind instruments: the back wall seen from inside in the open cells
        inn = m.part(prefix + "_inner", r["inner"])
        for z0, z1, kind in cells:
            if kind in ("open", "slide"):
                g.box(inn, x0 + side, x1 - side, y1 - 0.017, y1 - 0.015, z0 + SHELF_T, z1)
        parts.append(inn)

    # --- panels, grilles, doors
    pn = m.part(prefix + "_panels", r["panel"])
    vt = m.part(prefix + "_vents", r["vent"]) if lod < 2 else None
    dr = m.part(prefix + "_doors", r["door"])
    hd = m.part(prefix + "_handles", r["handle"]) if lod == 0 else None
    for z0, z1, kind in cells:
        za, zb = z0 + gap, z1 - gap
        if kind in ("blank", "vent"):
            g.box(pn, xp0, xp1, y0 - 0.003, y0, za, zb)
            if kind == "vent" and vt is not None:
                g.box(vt, xp0 + 0.04, xp1 - 0.04, y0 - 0.0045, y0 - 0.003, za + 0.015, zb - 0.015)
            if hd is not None:
                for xs in (xp0 + 0.012, xp1 - 0.012):
                    for zs in ((za + 0.015, zb - 0.015) if zb - za > 0.06 else ((za + zb) / 2,)):
                        g.cyl(hd, (xs, y0 - 0.0045, zs), "y", 0.0045, 0.003, 8)
        elif kind == "doors":
            xm = (xp0 + xp1) / 2
            for xa, xb in ((xp0, xm - gap / 2), (xm + gap / 2, xp1)):
                g.box(dr, xa, xb, y0 - 0.018, y0, za, zb, **bev)
            if hd is not None:
                zh = min(zb - 0.12, za + 0.55)
                for s in (-1, 1):
                    xh = xm + s * 0.04
                    g.sweep(hd, [(xh, y0 - 0.018, zh - 0.07), (xh, y0 - 0.045, zh - 0.07), (xh, y0 - 0.045, zh + 0.07),
                                 (xh, y0 - 0.018, zh + 0.07)], (1, 0, 0), 0.005, 0.005)
                g.cyl(hd, (xm + 0.04, y0 - 0.022, zb - 0.05), "y", 0.011, 0.008, 10)
    for p in (pn, vt, dr, hd):
        if p is not None and p.bm.faces:
            parts.append(p)

    # --- pull-out shelf
    if slide:
        zs, pull, depth = slide["z"], slide["pull"], slide["depth"]
        ya, yb = y0 - pull, y0 - pull + depth
        tr = m.part(prefix + "_tray", r["tray"])
        g.box(tr, xi0 + 0.005, xi1 - 0.005, ya, yb, zs - 0.012, zs)
        if lod < 2:
            for xa in (xi0 + 0.005, xi1 - 0.017):
                g.box(tr, xa, xa + 0.012, ya, yb, zs, zs + 0.015)
            g.box(tr, xi0 + 0.017, xi1 - 0.017, yb - 0.012, yb, zs, zs + 0.015)
        parts.append(tr)
        fp = m.part(prefix + "_tray_front", r["front"])
        g.box(fp, xp0 + 0.004, xp1 - 0.004, ya - 0.016, ya, zs - 0.045, zs + 0.025, **bev)
        parts.append(fp)
        if lod < 2:
            sl = m.part(prefix + "_slides", r["slider"])
            for s, xe in ((-1, xi0 + 0.005), (1, xi1 - 0.005)):
                # the moving part is under the tray rim, the fixed part is on the side wall
                xa, xb = sorted((xe, xe + s * 0.013))
                g.box(sl, xa, xb, ya + 0.03, yb - 0.02, zs - 0.040, zs - 0.012)
                xa, xb = sorted((xe + s * 0.013, xe + s * 0.022))
                g.box(sl, xa, xb, y0 + 0.02, y0 + depth - 0.04, zs - 0.046, zs - 0.006)
            parts.append(sl)
            if hd is not None:
                gr = m.part(prefix + "_tray_grip", r["handle"])
                xm = (xi0 + xi1) / 2
                g.sweep(gr, [(xm - 0.10, ya - 0.016, zs - 0.010), (xm - 0.10, ya - 0.040, zs - 0.010),
                             (xm + 0.10, ya - 0.040, zs - 0.010), (xm + 0.10, ya - 0.016, zs - 0.010)],
                        (0, 0, 1), 0.005, 0.005)
                parts.append(gr)

    # --- cables at the back
    if cables and lod < 2:
        xm = (x0 + x1) / 2
        zg0, zg1 = plinth + 0.06, plinth + 0.16
        zm = (zg0 + zg1) / 2
        if lod == 0:
            # louvers of the back wall: at the top above the instruments and at the bottom
            rv = m.part(prefix + "_back_vents", r["vent"])
            for za, zb in ((zc - 0.62, zc - 0.16), (plinth + 0.24, plinth + 0.52)):
                g.box(rv, x0 + side + 0.06, x1 - side - 0.06, y1, y1 + 0.0015, za, zb)
            parts.append(rv)
        gl = m.part(prefix + "_glands", r["gland"])
        g.box(gl, xm - 0.12, xm + 0.12, y1, y1 + 0.012, zg0, zg1)
        g.box(gl, xm - 0.10, xm + 0.10, y1, y1 + 0.006, zc - 0.10, zc - 0.04)
        parts.append(gl)
        cb = m.part(prefix + "_cables", r["cable"])
        sd = 6 if lod == 0 else 4
        for k, (dx, rr) in enumerate(((-0.07, 0.009), (-0.02, 0.006), (0.03, 0.007), (0.08, 0.005))):
            # from the gland backward and down in an arc, then along the floor with a bend to the side
            xe = xm + dx * 2.5 + 0.05 * k
            pts = [(xm + dx, y1 + 0.006, zm), (xm + dx, y1 + 0.035, zm - 0.004), (xm + dx * 1.05, y1 + 0.065, zm - 0.03),
                   (xm + dx * 1.15, y1 + 0.09, plinth * 0.8), (xm + dx * 1.3, y1 + 0.11, plinth * 0.3),
                   (xm + dx * 1.5, y1 + 0.15, rr), (xm + dx * 2.0 + 0.02 * k, y1 + 0.28, rr), (xe, y1 + 0.45 + 0.08 * k, rr)]
            g.pipe(cb, pts if lod == 0 else [pts[i] for i in (0, 2, 4, 5, 7)], rr, sd)
        xv = xm + 0.10
        pts = [(xm + 0.04, y1 + 0.004, zc - 0.07), (xm + 0.08, y1 + 0.03, zc - 0.10), (xv, y1 + 0.03, zc - 0.25),
               (xv, y1 + 0.03, zg1 + 0.12), (xm + 0.09, y1 + 0.02, zg1 + 0.02), (xm + 0.08, y1 + 0.006, zm + 0.02)]
        g.pipe(cb, pts if lod == 0 else [pts[i] for i in (0, 2, 3, 5)], 0.007, sd)
        parts.append(cb)
        if lod == 0:
            cl = m.part(prefix + "_clips", r["handle"])
            for z in (zc - 0.45, (zc + zg1) / 2, zg1 + 0.30):
                g.box(cl, xv - 0.014, xv + 0.014, y1, y1 + 0.042, z - 0.008, z + 0.008)
            parts.append(cl)
    return parts
