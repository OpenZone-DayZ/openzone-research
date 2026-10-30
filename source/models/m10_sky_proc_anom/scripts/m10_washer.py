"""B4 base "two-tub washing machine" for M10: the same Sibir-5 as kwasher.twin_tub (sizes, compartments,
panel, centrifuge opening - kwasher.layout), but without the angularity and with the small details
of a real machine:
- body - an enamelled sheet, front corners rounded (R16), the rear edges of the sides bent inward
  (flanges of the removed wall), frame rails at the top and bottom at the back; the plinth is rounded;
- deck - cast, edges rounded (R12), the centrifuge opening in a plastic collar, a dark seal along the
  deck/body seam, screws along the front edge;
- moulding - a half-round chrome profile; the panel with rounded edges and screws; knobs - turned
  discs with a domed top and a cross bar with a chrome insert (photo of the panel);
- lids are rounded, handles streamlined, hinges surface-mounted with an axle;
- the centrifuge drum with a rolled rim (the wall holes are in the generator's material);
- the interior without the back wall (what shows from behind): a tank with a rim, the activator
  motor standing with fins and a pulley, a V-belt on the activator pulley under the tank, the
  centrifuge motor on three suspension springs, a pump, a corrugated drain hose out to the floor, a
  capacitor on a clamp, a terminal box and a wire harness from the panel.
The far LOD is a box with a deck, lids, a panel and a dark circle of the opening, as in kwasher.

It is its own module in the model folder rather than an edit of kwasher: the existing kit files are
not changed. It can be moved into the kit later.
"""
import math

import kgeo as g
import kwasher
from m10_geo import frame_at, helix, hull2, lathe, resample, rrect, screw, spline, u_shell

T = 0.004                    # enamelled body sheet
R_CORNER = 0.016             # rounding of the front body corners
DECK_H = kwasher.DECK_H
PLINTH = kwasher.PLINTH
KNOB_R, WELL_R = kwasher.KNOB_R, kwasher.WELL_R
LID_T = 0.014


def inner(x0, x1, y0, y1, z0, height=0.70, split=0.55):
    """Where things are inside (for the model rigging): the tank, the activator motor, the belt plane, the
    centrifuge motor (bottom, top), the pump, the terminal box."""
    lay = kwasher.layout(x0, x1, y0, y1, z0, height, split)
    zt, xs = lay["zt"], lay["xs"]
    zd = zt - DECK_H
    zb = z0 + PLINTH
    tank = (x0 + T + 0.010, xs - 0.008, y0 + T + 0.012, y1 - 0.055, zd - 0.40, zd - 0.002)
    return dict(lay=lay, zd=zd, zb=zb, tank=tank,
                tank_c=((tank[0] + tank[1]) / 2, (tank[2] + tank[3]) / 2),
                wash_motor=(x0 + 0.0975, y1 - 0.0875), z_belt=zb + T + 0.171,
                spin_motor=(zb + T + 0.086, zd - 0.43),
                pump=(xs - 0.02, y1 - 0.06, zb + T + 0.045),
                jbox=(x0 + T + 0.002, x0 + T + 0.040, y1 - 0.045, y1 - 0.005, zd - 0.24, zd - 0.16))


def ribs(part, cx, cy, r, z0, z1, n):
    """Cooling fins along the motor cylinder: n plates along the axis."""
    for k in range(n):
        a = 2 * math.pi * (k + 0.5) / n
        f = g.Frame((cx + r * math.cos(a), cy + r * math.sin(a), 0.0), (-math.sin(a), math.cos(a), 0), (0, 0, 1),
                    (math.cos(a), math.sin(a), 0))
        g.box(part, -0.0018, 0.0018, z0, z1, -0.002, 0.006, frame=f)


def twin_tub(m, spec, x0, x1, y0, y1, z0, height=0.70, split=0.55, open_deg=100.0, drum_group="body",
             knob_group="body", regions=None, prefix="tt", hose_end=None):
    """B4 base, the back wall removed, the centrifuge lid tilted open permanently. m is a kmodel.Model. The
    face is toward -Y (y0), the plinth bottom at z0. knob_group is the group of the middle knob ("spin":
    the "work" pose), drum_group is the drum. hose_end - [(x, y, z)] - where the drain hose goes outside
    (over the crate and onto the floor)."""
    r = dict(body="tt_body", deck="tt_deck", panel="tt_panel", lid="tt_lid", trim="chrome", knob="tt_knob",
             well="black", inner="tt_inner", tank="tt_tank", drum="tt_drum", motor="motor", hose="hose",
             collar="collar", gasket="black", belt="belt", spring="spring", cap="cap_white", jbox="jbox",
             dark="dark", wire="cable")
    r.update(regions or {})
    lod = spec["lod"]
    ins = inner(x0, x1, y0, y1, z0, height, split)
    lay = ins["lay"]
    zt, xs, zd, zb = lay["zt"], lay["xs"], ins["zd"], ins["zb"]
    (scx, scy), sr, hr = lay["spin_c"], lay["spin_r"], lay["house_r"]
    nr = (32, 16, 12)[lod]                         # segments at the opening, collar, drum
    fz = frame_at((scx, scy, 0.0), "z")
    P = m.part
    parts = []

    # --- body: a sheet as a U-profile (face and sides), bottom; far LOD - a box
    bd = P(prefix + "_body", r["body"])
    if lod < 2:
        g.prism(bd, u_shell(x0, x1, y0, y1, T, R_CORNER, (6, 2)[lod]), (0, 1), zb, zd)
        g.box(bd, x0 + T, x1 - T, y0 + T, y1, zb, zb + T)
    else:
        g.prism(bd, rrect(x0, x1, y0, y1, R_CORNER, 1), (0, 1), zb, zd)
    parts.append(bd)
    if lod == 0:
        # rear edges of the sides bent inward, frame rails at the top and bottom
        fl = P(prefix + "_frame", r["body"])
        for xa, xb in ((x0 + T, x0 + T + 0.018), (x1 - T - 0.018, x1 - T)):
            g.box(fl, xa, xb, y1 - 0.0015, y1, zb + T, zd - 0.024)
        g.box(fl, x0 + T, x1 - T, y1 - 0.024, y1, zd - 0.024, zd)
        g.box(fl, x0 + T, x1 - T, y1 - 0.016, y1, zb + T, zb + T + 0.024)
        parts.append(fl)

    # --- maker's plate on the face at the bottom left (chrome, no lettering; the real Sibir has its name there)
    if lod == 0:
        bg = P(prefix + "_badge", r["trim"])
        g.box(bg, x0 + 0.055, x0 + 0.165, y0 - 0.0018, y0 + 0.001, zb + 0.100, zb + 0.128, r=0.0012, seg=1)
        dk_ = P(prefix + "_badge_inlay", r["dark"])
        g.box(dk_, x0 + 0.062, x0 + 0.158, y0 - 0.0021, y0 - 0.0015, zb + 0.1125, zb + 0.1155)
        parts += [bg, dk_]

    # --- plinth (dark, recessed)
    pl = P(prefix + "_plinth", r["well"])
    g.prism(pl, rrect(x0 + 0.010, x1 - 0.010, y0 + 0.010, y1 - 0.004, 0.010, (3, 1, 1)[lod]), (0, 1), z0, zb + 0.002)
    parts.append(pl)

    # --- seal along the deck/body seam (a dark strip under the deck overhang)
    if lod < 2:
        gk = P(prefix + "_gasket", r["gasket"])
        g.box(gk, x0 - 0.0012, x1 + 0.0012, y0 - 0.0012, y0 + 0.006, zd - 0.0045, zd)
        for xa, xb in ((x0 - 0.0012, x0 + 0.006), (x1 - 0.006, x1 + 0.0012)):
            g.box(gk, xa, xb, y0 + 0.006, y1 - 0.002, zd - 0.0045, zd)
        parts.append(gk)

    # --- deck: a rounded slab with the centrifuge opening (boolean difference); far LOD - a dark circle
    dk = P(prefix + "_deck", r["deck"])
    g.box(dk, x0 - 0.004, x1 + 0.004, y0 - 0.008, y1, zd, zt,
          **(dict(r=0.012, seg=2) if lod == 0 else dict(r=0.008, seg=1) if lod == 1 else {}))
    if lod < 2:
        cut = P(prefix + "_deck_cut", r["deck"])
        g.cyl(cut, (scx, scy, (zd + zt) / 2), "z", sr, DECK_H + 0.04, nr)
        dk = m.boolean(prefix + "_deck", dk, [cut])
    parts.append(dk)
    if lod == 2:
        hole = P(prefix + "_spin_hole", r["inner"])
        g.cyl(hole, (scx, scy, zt + 0.0006), "z", sr, 0.0012, nr)
        parts.append(hole)
    else:
        # plastic collar of the opening: rounded on top, goes 16 mm into the opening
        cl = P(prefix + "_collar", r["collar"])
        prof = ([(sr - 0.003, -0.016), (sr - 0.003, 0.003), (sr + 0.0015, 0.0066), (sr + 0.009, 0.0052),
                 (sr + 0.013, 0.0)] if lod == 0 else
                [(sr - 0.003, -0.016), (sr - 0.003, 0.004), (sr + 0.013, 0.0)])
        lathe(cl, prof, nr, frame_at((scx, scy, zt), "z"), closed=True)
        parts.append(cl)
    if lod == 0:
        sc = P(prefix + "_deck_screws", r["trim"])
        for x in (x0 + 0.014, xs, x1 - 0.014):
            screw(sc, (x, y0 + 0.010, zt), "z", 0.0042)
        parts.append(sc)

    # --- moulding under the deck: a half-round chrome profile across the whole width
    tr = P(prefix + "_trim", r["trim"])
    tz0, tz1 = lay["trim_z"] - 0.008, lay["trim_z"]
    zc, rr = (tz0 + tz1) / 2, (tz1 - tz0) / 2
    if lod < 2:
        n = (8, 3)[lod]
        poly = [(y0 - 0.9 * rr * math.sin(math.pi * k / n), zc - rr * math.cos(math.pi * k / n)) for k in range(n + 1)]
        poly += [(y0 + 0.002, tz1), (y0 + 0.002, tz0)]
        g.prism(tr, poly, (1, 2), x0 + 0.003, x1 - 0.003)
    else:
        g.box(tr, x0 + 0.003, x1 - 0.003, y0 - 0.004, y0 + 0.001, tz0, tz1)
    parts.append(tr)

    # --- control panel: a plate with rounded edges, screws, sockets, knobs
    pa, pb, pza, pzb = lay["panel"]
    yp = lay["panel_y"]
    pn = P(prefix + "_panel", r["panel"])
    g.box(pn, pa, pb, yp, y0 + 0.001, pza, pzb, **(dict(r=0.0025, seg=2) if lod == 0 else {}))
    parts.append(pn)
    if lod < 2:
        wl = P(prefix + "_wells", r["well"])
        for kx, kz in lay["knobs"]:
            g.cyl(wl, (kx, yp - 0.0005, kz), "y", WELL_R, 0.002, (20, 8)[lod])
        parts.append(wl)
        for i, (kx, kz) in enumerate(lay["knobs"]):
            grp = knob_group if i == 1 else "body"
            kn = P("%s_knob%d" % (prefix, i), r["knob"], group=grp)
            fr = frame_at((kx, yp - 0.0015, kz), "-y")
            if lod == 0:
                # turned disc with a domed top and a handle bar across (photo of the panel)
                lathe(kn, [(0.0, 0.0), (KNOB_R + 0.0012, 0.0), (KNOB_R + 0.0012, 0.0032), (KNOB_R - 0.0035, 0.0092),
                           (0.0, 0.0102)], 20, fr)
                g.box(kn, -0.0082, 0.0082, -0.030, 0.030, 0.008, 0.0235, frame=fr, r=0.0034, seg=1)
                ins_ = P("%s_knob_insert%d" % (prefix, i), r["trim"], group=grp)
                g.box(ins_, -0.0022, 0.0022, -0.0235, 0.0235, 0.0234, 0.0241, frame=fr)
                parts += [kn, ins_]
            else:
                g.cyl(kn, (kx, yp - 0.0065, kz), "y", KNOB_R, 0.010, 8)
                g.box(kn, -0.008, 0.008, -0.030, 0.030, 0.009, 0.023, frame=fr)
                parts.append(kn)
        if lod == 0:
            ps = P(prefix + "_panel_screws", r["trim"])
            sl = P(prefix + "_panel_slots", r["dark"])
            for x in (pa + 0.012, pb - 0.012):
                zm = (pza + pzb) / 2
                screw(ps, (x, yp, zm), "-y", 0.0045, 8)
                g.box(sl, x - 0.0032, x + 0.0032, yp - 0.0033, yp - 0.0027, zm - 0.0005, zm + 0.0005)
            parts += [ps, sl]

    # --- tank lid (closed; the detector unit is on it): rounded, a handle at the front, hinges at the back
    wa, wb, wya, wyb = lay["wash"]
    wlid = P(prefix + "_wash_lid", r["lid"])
    g.box(wlid, wa, wb, wya, wyb, zt, zt + LID_T, **(dict(r=0.006, seg=2) if lod == 0 else {}))
    parts.append(wlid)
    if lod < 2:
        wh = P(prefix + "_wash_handle", r["trim"])
        xm = (wa + wb) / 2
        g.box(wh, xm - 0.040, xm + 0.040, wya + 0.005, wya + 0.023, zt + LID_T - 0.001, zt + LID_T + 0.0085,
              **(dict(r=0.004, seg=1) if lod == 0 else {}))
        parts.append(wh)
    hy = lay["hinge_y"]
    if lod == 0:
        hg = P(prefix + "_hinges", r["trim"])
        for x in (wa + 0.055, wb - 0.055):
            g.cyl(hg, (x, hy + 0.004, zt + LID_T - 0.002), "x", 0.0048, 0.044, 8)
            g.box(hg, x - 0.0215, x + 0.0215, hy + 0.004, hy + 0.024, zt, zt + 0.0016)
            g.box(hg, x - 0.0215, x + 0.0215, hy - 0.018, hy + 0.002, zt + LID_T, zt + LID_T + 0.0016)
        parts.append(hg)

    # --- centrifuge lid: tilted open by open_deg, rounded, a handle on the far edge, hinges
    sa, sb, sya, syb = lay["spin"]
    fr = kwasher.lid_frame(hy, zt + 0.004, open_deg)
    ld = syb - sya
    sl_ = P(prefix + "_spin_lid", r["lid"])
    g.box(sl_, sa, sb, 0.0, ld, 0.0, LID_T, frame=fr, **(dict(r=0.006, seg=2) if lod == 0 else {}))
    parts.append(sl_)
    if lod < 2:
        sh = P(prefix + "_spin_handle", r["trim"])
        xm = (sa + sb) / 2
        g.box(sh, xm - 0.035, xm + 0.035, ld - 0.026, ld - 0.008, -0.0085, 0.001, frame=fr,
              **(dict(r=0.004, seg=1) if lod == 0 else {}))
        parts.append(sh)
        if lod == 0:
            hs = P(prefix + "_spin_hinges", r["trim"])
            for x in (sa + 0.05, sb - 0.05):
                g.cyl(hs, (x, hy, zt + 0.004), "x", 0.0048, 0.044, 8)
                g.box(hs, x - 0.0215, x + 0.0215, hy + 0.002, hy + 0.024, zt, zt + 0.0016)
                g.box(hs, x - 0.0215, x + 0.0215, 0.004, 0.024, -0.0016, 0.0, frame=fr)
            parts.append(hs)

    # --- centrifuge casing and drum (group drum_group): rolled rim, ribs and hub
    if lod == 0:
        hs_ = P(prefix + "_spin_house", r["tank"])
        kwasher.cup(hs_, scx, scy, hr, sr - 0.001, zd - 0.43, zd + 0.001, zd - 0.42, 16)
        parts.append(hs_)
    dr = P(prefix + "_drum", r["drum"], group=drum_group)
    top = zt - 0.045
    if lod < 2:
        kwasher.cup(dr, scx, scy, sr - 0.010, sr - 0.016, zd - 0.40, top, zd - 0.392, nr)
        if lod == 0:
            lathe(dr, [(sr - 0.0175, top - 0.001), (sr - 0.0170, top + 0.0035), (sr - 0.0125, top + 0.0055),
                       (sr - 0.0090, top - 0.001)], nr, fz, closed=True)
        lathe(dr, [(0.0, zd - 0.393), (0.032, zd - 0.393), (0.028, zd - 0.374), (0.0, zd - 0.371)], (12, 8)[lod], fz)
    else:
        g.cyl(dr, (scx, scy, zt + 0.0016), "z", sr - 0.016, 0.0006, nr)
    parts.append(dr)

    if lod == 2:
        return parts

    # --- interior: a tank with a rim, a partition at the face (darkness behind the tank)
    tx0, tx1, ty0, ty1, tz0_, tz1_ = ins["tank"]
    tk = P(prefix + "_tank", r["tank"])
    g.box(tk, tx0, tx1, ty0, ty1, tz0_, tz1_, **(dict(r=0.025, seg=2) if lod == 0 else {}))
    if lod == 0:
        g.box(tk, tx0 - 0.005, tx1 + 0.005, ty0 - 0.005, ty1 + 0.005, tz1_ - 0.010, tz1_)
    parts.append(tk)
    inn = P(prefix + "_inner", r["inner"])
    g.box(inn, x0 + T, x1 - T, y0 + T, y0 + T + 0.004, zb + T, zd)
    parts.append(inn)

    # --- activator motor standing, pulley, belt on the activator pulley under the tank
    mx, my = ins["wash_motor"]
    zm0, zm1 = zb + T, zb + T + 0.13
    zbelt = ins["z_belt"]
    (tcx, tcy) = ins["tank_c"]
    mt = P(prefix + "_motors", r["motor"])
    if lod == 0:
        lathe(mt, [(0.0, zm0 + 0.004), (0.046, zm0 + 0.004), (0.055, zm0 + 0.018), (0.055, zm1 - 0.018), (0.046, zm1),
                   (0.0, zm1 + 0.003)], 14, frame_at((mx, my, 0.0), "z"))
        g.box(mt, mx - 0.068, mx + 0.068, my - 0.045, my + 0.045, zm0, zm0 + 0.004)
        ribs(mt, mx, my, 0.055, zm0 + 0.024, zm1 - 0.024, 8)
        g.box(mt, mx - 0.020, mx + 0.020, my + 0.052, my + 0.072, zm0 + 0.07, zm0 + 0.105)
    else:
        g.cyl(mt, (mx, my, (zm0 + zm1) / 2), "z", 0.055, zm1 - zm0, 8)
    parts.append(mt)
    if lod == 0:
        pu = P(prefix + "_pulleys", r["trim"])
        g.cyl(pu, (mx, my, (zm1 + zbelt) / 2 + 0.005), "z", 0.006, zbelt - zm1 + 0.01, 6)
        lathe(pu, [(0.0, zbelt - 0.009), (0.022, zbelt - 0.009), (0.017, zbelt), (0.022, zbelt + 0.009), (0.0, zbelt + 0.009)],
              14, frame_at((mx, my, 0.0), "z"))
        lathe(pu, [(0.0, zbelt - 0.009), (0.060, zbelt - 0.009), (0.055, zbelt), (0.060, zbelt + 0.009), (0.0, zbelt + 0.009)],
              20, frame_at((tcx, tcy, 0.0), "z"))
        g.cyl(pu, (tcx, tcy, (zbelt + tz0_) / 2), "z", 0.022, tz0_ - zbelt, 10)
        parts.append(pu)
        bl = P(prefix + "_belt", r["belt"])
        loop = hull2([(mx, my, 0.0185), (tcx, tcy, 0.0565)], 16)
        g.sweep(bl, [(x, y, zbelt) for x, y in loop], (0, 0, 1), 0.0042, 0.0045, closed=True)
        parts.append(bl)

    # --- centrifuge motor under the casing on three suspension springs
    zs0, zs1 = ins["spin_motor"]
    sm = P(prefix + "_spin_motor", r["motor"])
    if lod == 0:
        lathe(sm, [(0.0, zs0), (0.042, zs0), (0.050, zs0 + 0.014), (0.050, zs1 - 0.016), (0.030, zs1), (0.0, zs1)], 14, fz)
        lathe(sm, [(0.0, zs0 - 0.006), (0.094, zs0 - 0.006), (0.094, zs0), (0.0, zs0)], 14, fz)
        g.box(sm, scx - 0.075, scx - 0.050, scy - 0.018, scy + 0.018, zs0 + 0.04, zs0 + 0.07)
    else:
        g.cyl(sm, (scx, scy, (zs0 + zs1) / 2), "z", 0.050, zs1 - zs0, 8)
    parts.append(sm)
    if lod == 0:
        spg = P(prefix + "_springs", r["spring"])
        for k in range(3):
            a = math.radians(90.0 + 120.0 * k)
            c = (scx + 0.075 * math.cos(a), scy + 0.075 * math.sin(a))
            g.pipe(spg, helix(c, 0.0115, zb + T + 0.003, zs0 - 0.008, 2.5, 5, a), 0.0022, 4)
        parts.append(spg)

    # --- pump, hose from the tank, corrugated drain hose out
    px, py, pz = ins["pump"]
    pm = P(prefix + "_pump", r["motor"])
    if lod == 0:
        lathe(pm, [(0.0, -0.015), (0.032, -0.015), (0.032, 0.015), (0.0, 0.015)], 12, frame_at((px, py, pz), "y"))
        lathe(pm, [(0.0, 0.0), (0.023, 0.0), (0.023, 0.052), (0.0, 0.054)], 10, frame_at((px - 0.012, py, pz), "-x"))
        lathe(pm, [(0.0, 0.010), (0.0105, 0.010), (0.0125, 0.050), (0.0, 0.050)], 6, frame_at((px, py, pz), "y"))
        lathe(pm, [(0.0, 0.020), (0.0095, 0.020), (0.0095, 0.046), (0.0, 0.046)], 6, frame_at((px, py, pz), "z"))
    else:
        g.box(pm, px - 0.06, px + 0.03, py - 0.02, py + 0.02, pz - 0.03, pz + 0.03)
    parts.append(pm)
    hs2 = P(prefix + "_hoses", r["hose"])
    if lod == 0:
        g.pipe(hs2, spline([(tcx + 0.10, ty1 - 0.020, tz0_ + 0.004), (tcx + 0.11, ty1 - 0.012, tz0_ - 0.06),
                            (px - 0.004, py - 0.004, pz + 0.10), (px, py, pz + 0.046)], 3), 0.0095, 6)
    out = [(px, py + 0.050, pz), (px - 0.002, y1 + 0.016, pz - 0.004)] + list(hose_end or [])
    if len(out) > 2:
        if lod == 0:
            pts = resample(spline(out, 6), 0.014)
            radii = [(0.0128, 0.0128) if i % 2 == 0 else (0.0110, 0.0110) for i in range(len(pts))]
            g.tube_var(hs2, pts, radii, 6)
        else:
            g.pipe(hs2, out, 0.012, 5)
    parts.append(hs2)

    if lod == 0:
        # capacitor on a clamp at the right side, terminal box at the left, a harness from the panel and to the
        # motor
        cp = P(prefix + "_capacitor", r["cap"])
        ccx, ccy = x1 - T - 0.030, y1 - 0.040
        lathe(cp, [(0.0, zd - 0.32), (0.020, zd - 0.32), (0.022, zd - 0.316), (0.022, zd - 0.250), (0.020, zd - 0.246),
                   (0.0, zd - 0.246)], 10, frame_at((ccx, ccy, 0.0), "z"))
        parts.append(cp)
        cb = P(prefix + "_cap_strap", r["trim"])
        lathe(cb, [(0.0218, zd - 0.292), (0.0234, zd - 0.292), (0.0234, zd - 0.280), (0.0218, zd - 0.280)], 10,
              frame_at((ccx, ccy, 0.0), "z"), closed=True)
        g.box(cb, ccx + 0.020, x1 - T, ccy - 0.012, ccy + 0.012, zd - 0.292, zd - 0.280)
        parts.append(cb)
        jx0, jx1, jy0, jy1, jz0, jz1 = ins["jbox"]
        jb = P(prefix + "_jbox", r["jbox"])
        g.box(jb, jx0, jx1, jy0, jy1, jz0, jz1 - 0.004, r=0.003, seg=1)
        g.box(jb, jx0 + 0.001, jx1 + 0.002, jy0 - 0.001, jy1 + 0.001, jz1 - 0.005, jz1)
        for k in range(3):
            lathe(jb, [(0.0, jz1), (0.0055, jz1), (0.0045, jz1 + 0.009), (0.0, jz1 + 0.009)], 6,
                  frame_at((jx0 + 0.010 + 0.009 * k, (jy0 + jy1) / 2, 0.0), "z"))
        parts.append(jb)
        wire = P(prefix + "_harness", r["wire"])
        jxm, jym = (jx0 + jx1) / 2, (jy0 + jy1) / 2
        routes = [
            [(0.040, y0 + T + 0.010, zt - 0.11), (0.040, y0 + 0.05, zd - 0.022), (xs + 0.004, -0.06, zd - 0.015),
             (xs + 0.004, 0.10, zd - 0.016), (xs - 0.004, y1 - 0.020, zd - 0.060), (-0.12, y1 - 0.018, zd - 0.13),
             (jx1 + 0.020, jym, jz0 + 0.050), (jx1, jym, jz0 + 0.040)],
            [(jxm, jym, jz0), (jxm + 0.006, jym - 0.004, jz0 - 0.10), (mx - 0.02, my + 0.075, zm1 - 0.010),
             (mx, my + 0.072, zm0 + 0.105)],
        ]
        for pts in routes:
            g.pipe(wire, spline(pts, 3), 0.0032, 4)
        parts.append(wire)
    return parts
