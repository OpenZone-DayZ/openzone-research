"""Detailed console for M24: the same parameters, profile and dimensions as kconsole.console (in the
kit; the library is not changed here), plus the small things of a real army console of the 1970-90s
(the look comes from the vanilla radar_panel: screwed panels, instrument holders, wear):
- cheeks, body and roof have rounded edges; the desk and top panels are screwed, with a hinge between
  them; the false panel and the roof are screwed; the desk bumper has rounded ends;
- doors: hinges, latch handles with a rosette, a lock, stamped louvers at the bottom (the seal is in
  the generator);
- the side walls have stamped louvers; at the back a grille in a screwed frame and a cable entry
  with a nut;
- top panel: a CRT screen in a square screwed holder with a rubber tube (the screen face has its own
  texture, section crt_section: "off" and the "working" frames), under it the brightness and focus
  knobs; needle gauges in square screwed flanges: a shaped holder, glass, a needle with a
  counterweight and an axis cap.
A candidate to be moved into kconsole.

Blender axes: X is width, Y is depth (the face looks to -Y), Z is up.
"""
import math

from mathutils import Vector

import kconsole as kc
import kgeo as g
import m24_bits as b

CHEEK, PLINTH, CAP_T, PLATE_T, CHEEK_OUT, GF = kc.CHEEK, kc.PLINTH, kc.CAP_T, kc.PLATE_T, kc.CHEEK_OUT, kc.GF
ROLES = dict(frame="cs", desk="cs_desk", upper="cs_upper", front="cs_front", accent="cs_accent", handle="steel",
             foot="black", bezel="black", dial="dial", needle="needle", rubber="rubber", vent="grille_v",
             gland="black", screw="screw", hinge="steel", lock="chrome", knob="knob", ptr="ptr")


def upper_len(L, upper_deg):
    """Length of the top panel along the slope (the false panel is under the roof)."""
    return L["up_len"] - 0.050 / math.cos(math.radians(upper_deg))


def gauge_places(L, xi0, xi1, gauges, screen_r):
    """Where the screen and the gauges will stand (as in kconsole.console): (a screen (a, b, r) or None,
    [(a, b)])."""
    ul = L["up_len"] - 0.050
    scr = None
    a_free = xi0 + 0.03
    if screen_r > 0:
        sa, sb = xi0 + 0.035 + screen_r * 1.3, ul * 0.52
        scr = (sa, sb, screen_r)
        a_free = sa + screen_r * 1.3 + 0.03
    step = (xi1 - 0.02 - a_free) / max(gauges, 1)
    return scr, [(a_free + step * (i + 0.5), ul * 0.74) for i in range(gauges)], a_free


def needle_pivot(U, a, bb):
    return U.p(a, bb, GF + 0.0006)


def needle_axis(U, a, bb):
    """Needle axis (memory points): from behind the panel through the needle pivot toward the person
    (+U.n). The engine rotates a bone right-handed in DayZ axes (kexport.conv, determinant -1); in
    Blender axes it is left-handed about the axis from the first point to the second: the axis looks at
    the person - a positive angle is clockwise for him. The axis must not point into the panel: the
    needles would then turn counterclockwise in the game, past zero."""
    return tuple(U.p(a, bb, GF - 0.02)), tuple(U.p(a, bb, GF + 0.0006))


def console(m, spec, x0, x1, y0, y1, height, desk_z=0.76, desk_deg=25.0, desk_len=0.30, upper_deg=12.0,
            gauges=3, gauge_r=0.042, sweep=240.0, screen_r=0.07, doors=2, needles=(), dial_group="body",
            crt_group="ozl_screen", crt_section="crt", regions=None, prefix="cs"):
    """Detailed console. m is a kmodel.Model. The face is at -Y (y0). The parameters are as in
    kconsole.console; dial_group - the selection of the dial faces (backlight when "working"), crt_group
    and crt_section - the selection and the section of the screen face (own texture with frames).
    Returns (parts, info) like kconsole.console."""
    r = dict(ROLES)
    r.update(regions or {})
    lod = spec["lod"]
    P = m.part
    L = kc.layout(y0, y1, height, desk_z, desk_deg, desk_len, upper_deg)
    poly = kc.profile(y0, y1, L)
    xi0, xi1 = x0 + CHEEK, x1 - CHEEK
    D, U = L["desk"], L["upper"]
    ul = upper_len(L, upper_deg)
    parts = []

    def piece(name, region, uvn, origin, **kw):
        return P(name, region, uv_name=uvn, uv_origin=tuple(origin), **kw)

    def sides(n0):
        return n0 if lod == 0 else (max(6, n0 // 2) if lod == 1 else 6)

    # --- body and cheeks by the profile, with rounded edges
    body = P(prefix + "_body", r["frame"])
    if lod == 2:
        g.prism(body, poly, (1, 2), x0, x1)
    else:
        b.prism_bev(body, poly, (1, 2), xi0, xi1, *((0.003, 1) if lod == 0 else (0.0, 0)))
        cheek = kc._offset_poly(poly, [0.0, 0.0] + [CHEEK_OUT] * 6 + [0.0])
        cheek = [(yy, 0.0) if abs(zz - PLINTH) < 1e-6 else (yy, zz) for yy, zz in cheek]
        for xa, xb in ((x0, xi0), (xi1, x1)):
            b.prism_bev(body, cheek, (1, 2), xa, xb, *((0.005, 1) if lod == 0 else (0.0, 0)))
    parts.append(body)
    ft = P(prefix + "_plinth", r["foot"])
    g.box(ft, xi0, xi1, L["yt"] + 0.03, y1 - 0.01, 0.0, PLINTH + 0.002)
    parts.append(ft)

    # --- roof and the false panel-visor over the top panel
    cap = P(prefix + "_cap", r["frame"])
    yc0 = L["yu1"] - 0.045
    g.box(cap, x0 - 0.004, x1 + 0.004, yc0, y1 + 0.004, L["zu1"], height, **(dict(r=0.004, seg=2) if lod == 0 else {}))
    parts.append(cap)
    ac = P(prefix + "_accent", r["accent"])
    za0, za1 = L["zu1"] - 0.050, height - 0.004
    g.box(ac, xi0, xi1, yc0 - 0.004, yc0, za0, za1, **(dict(r=0.0015, seg=1) if lod == 0 else {}))
    if lod < 2:
        g.box(ac, xi0, xi1, yc0, L["yu1"] - 0.010, za0, za0 + 0.004)
    parts.append(ac)

    # --- desk and top panels, the hinge between them, the desk bumper
    dk = P(prefix + "_desk_plate", r["desk"])
    g.box(dk, xi0, xi1, 0.0, L["desk_len"], 0.0, PLATE_T, frame=D, **(dict(r=0.0012, seg=1) if lod == 0 else {}))
    up = P(prefix + "_upper_plate", r["upper"])
    g.box(up, xi0, xi1, 0.0, ul, 0.0, PLATE_T, frame=U, **(dict(r=0.0012, seg=1) if lod == 0 else {}))
    parts += [dk, up]
    if lod < 2:
        hn = P(prefix + "_joint", r["hinge"])
        nav = (D.n + U.n).normalized()
        cpt = Vector((0.0, L["yd1"], L["zd1"])) + nav * (PLATE_T + 0.0012)
        b.lathe(hn, (xi0 + 0.002, cpt.y, cpt.z), (1, 0, 0), [(0.0042, 0.0), (0.0042, xi1 - xi0 - 0.004)],
                10 if lod == 0 else 6, cap0=True)
        parts.append(hn)
        rb = P(prefix + "_bumper", r["rubber"])
        ln = x1 - x0 - 0.004
        prof = [(0.0, 0.0), (0.012, 0.0), (0.0175, 0.0045), (0.018, 0.009), (0.018, ln - 0.009), (0.0175, ln - 0.0045),
                (0.012, ln), (0.0, ln)]
        b.lathe(rb, (x0 + 0.002, y0 + 0.012, L["zd0"] - 0.016), (1, 0, 0), prof if lod == 0 else prof[3:5],
                12 if lod == 0 else 6, cap0=lod > 0)
        parts.append(rb)
    if lod == 0:
        # screws: desk and top panels, the false panel, the roof
        k = 0
        for fr, lp in ((D, L["desk_len"]), (U, ul)):
            for aa in (xi0 + 0.012, (xi0 + xi1) / 2, xi1 - 0.012):
                for bb in (0.012, lp - 0.012):
                    sc = piece("%s_screw%d" % (prefix, k), r["screw"], prefix + "_screw_panel", fr.p(aa, bb, PLATE_T))
                    b.screw(sc, fr.p(aa, bb, PLATE_T), fr.n, r=0.0032)
                    parts.append(sc)
                    k += 1
        for xx in (xi0 + 0.016, xi1 - 0.016):
            for zz in (za0 + 0.011, za1 - 0.011):
                q = (xx, yc0 - 0.004, zz)
                sc = piece("%s_screw%d" % (prefix, k), r["screw"], prefix + "_screw_front", q)
                b.screw(sc, q, (0, -1, 0), r=0.0032)
                parts.append(sc)
                k += 1
        for xx in (x0 + 0.022, x1 - 0.022):
            for yy in (yc0 + 0.020, y1 - 0.016):
                q = (xx, yy, height)
                sc = piece("%s_screw%d" % (prefix, k), r["screw"], prefix + "_screw_top", q)
                b.screw(sc, q, (0, 0, 1), r=0.0036)
                parts.append(sc)
                k += 1

    # --- lower compartment doors: hinges, latch handles, a lock, louvers
    fd = P(prefix + "_doors", r["front"])
    yt, zt = L["yt"], L["zd0"] - 0.085
    gap = 0.003
    xs = [xi0 + 0.006, xi1 - 0.006] if doors == 1 or lod == 2 else [xi0 + 0.006, (xi0 + xi1) / 2, xi1 - 0.006]
    for i in range(len(xs) - 1):
        xa = xs[i] + (gap / 2 if i else 0)
        xb = xs[i + 1] - (gap / 2 if i < len(xs) - 2 else 0)
        g.box(fd, xa, xb, yt - 0.004, yt, PLINTH + 0.012, zt, **(dict(r=0.0015, seg=1) if lod == 0 else {}))
        if lod == 0:
            b.louvers_y(fd, yt - 0.004, xa + 0.05, xb - 0.05, PLINTH + 0.055, 5, 0.021, h=0.011, d=0.0038)
    parts.append(fd)
    info = dict(L, xi0=xi0, xi1=xi1, handles=[], doors_x=xs)
    if lod < 2:
        hg = P(prefix + "_hinges", r["hinge"])
        for hx in (xs[0] - 0.0015, xs[-1] + 0.0015):
            for hz0 in (PLINTH + 0.06, zt - 0.11):
                if lod == 0:
                    b.hinge(hg, hx, yt - 0.0052, hz0, hz0 + 0.05, r=0.0055, lod=lod)
                else:
                    g.box(hg, hx - 0.005, hx + 0.005, yt - 0.010, yt - 0.002, hz0, hz0 + 0.05)
        parts.append(hg)
        hd = P(prefix + "_handles", r["handle"])
        hz = (PLINTH + zt) / 2 + 0.08
        fwd = Vector((0.0, -1.0, 0.0))
        for hx in ((xs[1] - 0.040, xs[1] + 0.040) if len(xs) == 3 else (xs[1] - 0.045,)):
            info["handles"].append((hx, yt - 0.004, hz))
            base = Vector((hx, yt - 0.004, hz))
            if lod == 0:
                b.lathe(hd, base, fwd, [(0.0155, 0.0), (0.0155, 0.0022), (0.0125, 0.0042), (0.0062, 0.0048)], 10,
                        cap1=False)
                b.lathe(hd, base + fwd * 0.004, fwd, [(0.0052, 0.0), (0.0052, 0.010)], 6, cap1=False)
                p0 = base + fwd * 0.016
                b.lathe(hd, p0 - fwd * 0.004, fwd, [(0.0078, 0.0), (0.0078, 0.0085), (0.0062, 0.0105)], 8, cap0=True)
                pts = [p0, p0 + Vector((0.0, -0.0010, -0.014)), p0 + Vector((0.0, -0.0035, -0.034)),
                       p0 + Vector((0.0, -0.0050, -0.054))]
                g.pipe(hd, b.spline([tuple(q) for q in pts], 2), 0.0050, 6)
                tip = pts[-1]
                d = (pts[-1] - pts[-2]).normalized()
                b.lathe(hd, tip - d * 0.001, d, [(0.0050, 0.0), (0.0058, 0.0030), (0.0042, 0.0072), (0.0, 0.0086)], 6)
            else:
                g.box(hd, hx - 0.006, hx + 0.006, yt - 0.016, yt, hz - 0.028, hz + 0.028)
        parts.append(hd)
        if lod == 0 and len(xs) == 3:
            lk = P(prefix + "_lock", r["lock"])
            q = Vector((xs[1] + 0.040, yt - 0.004, hz + 0.066))
            b.lathe(lk, q, fwd, [(0.0098, 0.0), (0.0098, 0.0028), (0.0082, 0.0042)], 12)
            parts.append(lk)
            ks = P(prefix + "_lock_slot", "black")
            g.box(ks, q.x - 0.0008, q.x + 0.0008, q.y - 0.0044, q.y - 0.0040, q.z - 0.0045, q.z + 0.0045)
            parts.append(ks)
            info["lock"] = tuple(q)

    # --- side walls: louvers; at the back: a grille in a frame, a cable entry
    if lod == 0:
        lv = P(prefix + "_louvers", r["frame"])
        for fx, sg in ((x0, -1), (x1, 1)):
            b.louvers(lv, fx, sg, -0.11, 0.13, 0.42, 5, 0.026, h=0.016, d=0.0045)
        parts.append(lv)
        vt = P(prefix + "_vent", r["vent"])
        vx0, vx1, vz0, vz1 = xi0 + 0.06, xi1 - 0.06, 0.75, 1.05
        g.box(vt, vx0, vx1, y1, y1 + 0.0015, vz0, vz1)
        vf = P(prefix + "_vent_frame", r["frame"])
        w = 0.014
        for xa, xb, za, zb in ((vx0 - w, vx1 + w, vz1, vz1 + w), (vx0 - w, vx1 + w, vz0 - w, vz0), (vx0 - w, vx0, vz0, vz1),
                               (vx1, vx1 + w, vz0, vz1)):
            g.box(vf, xa, xb, y1, y1 + 0.004, za, zb)
        parts += [vt, vf]
        for i, (xx, zz) in enumerate(((vx0 - w / 2, vz0 - w / 2), (vx1 + w / 2, vz0 - w / 2), (vx0 - w / 2, vz1 + w / 2),
                                      (vx1 + w / 2, vz1 + w / 2))):
            q = (xx, y1 + 0.004, zz)
            sc = piece("%s_vscrew%d" % (prefix, i), r["screw"], prefix + "_screw_back", q)
            b.screw(sc, q, (0, 1, 0), r=0.0030)
            parts.append(sc)
        gl = P(prefix + "_gland", r["gland"])
        q = Vector(((x0 + x1) / 2, y1, 0.16))
        b.lathe(gl, q, (0, 1, 0), [(0.030, 0.0), (0.030, 0.008)], 6, ref=(1, 0, 0))
        b.lathe(gl, q + Vector((0, 0.008, 0)), (0, 1, 0), [(0.022, 0.0), (0.022, 0.012), (0.015, 0.022), (0.010, 0.036)],
                12)
        parts.append(gl)

    # --- CRT screen: a screwed holder, a rubber tube, a face with its own texture, glass
    scr, places, a_free = gauge_places(L, xi0, xi1, gauges, screen_r)
    info["screen"] = None
    if scr:
        sa, sb, R = scr
        info["screen"] = dict(a=sa, b=sb, r=R)
        if lod < 2:
            pl = P(prefix + "_crt_plate", r["bezel"])
            b.plate(pl, U, sa, sb, 2.7 * R, 2.7 * R, 0.012, PLATE_T, PLATE_T + 0.004, n=2 if lod == 0 else 1)
            parts.append(pl)
            hood = P(prefix + "_crt_hood", r["rubber"])
            prof = [(1.12 * R, 0.0), (1.13 * R, 0.014), (1.23 * R, 0.030), (1.21 * R, 0.0345), (1.12 * R, 0.030),
                    (1.04 * R, 0.012), (1.02 * R, 0.0)]
            b.lathe(hood, U.p(sa, sb, PLATE_T + 0.004), U.n, prof if lod == 0 else [prof[i] for i in (0, 2, 4, 6)],
                    sides(24), cap1=False)
            parts.append(hood)
        if lod < 2:
            fc = P(prefix + "_crt", r["bezel"], group=crt_group, section=crt_section)
            b.disc(fc, U, sa, sb, PLATE_T + 0.0062, R * 1.03, sides(24))
            fc.glass_frame = (U, sa - R * 1.03, sa + R * 1.03, sb - R * 1.03, sb + R * 1.03)
            gl = P(prefix + "_crt_glass", "black", section="glass")
            b.disc(gl, U, sa, sb, PLATE_T + 0.0105, R * 1.04, sides(24))
            parts += [fc, gl]
        else:
            fc = P(prefix + "_crt", "black")
            b.disc(fc, U, sa, sb, PLATE_T + 0.001, R, 6)
            parts.append(fc)
        if lod == 0:
            for i, (su, sv) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
                q = U.p(sa + su * 1.16 * R, sb + sv * 1.16 * R, PLATE_T + 0.004)
                sc = piece("%s_crt_screw%d" % (prefix, i), r["screw"], prefix + "_screw_upper", q)
                b.screw(sc, q, U.n, r=0.0032)
                parts.append(sc)
            # brightness and focus knobs under the screen
            for i, da in enumerate((-0.036, 0.036)):
                kb = piece("%s_crt_knob%d" % (prefix, i), r["knob"], prefix + "_crt_knob", U.p(sa + da, 0.043, 0))
                pt = piece("%s_crt_knob%d_ptr" % (prefix, i), r["ptr"], prefix + "_crt_knob_ptr", U.p(sa + da, 0.043, 0))
                b.knob(kb, pt, U, sa + da, 0.043, PLATE_T, 0.0085, kind="plain", lod=lod, angle=(-50.0, 35.0)[i])
                parts += [kb, pt]

    # --- needle gauges: a flange on screws, a holder, a dial face, a needle, glass
    info["gauges"] = []
    gr = gauge_r
    for i, (ga, gb) in enumerate(places):
        grp = needles[i] if i < len(needles) else None
        info["gauges"].append(dict(a=ga, b=gb, r=gr, group=grp))
        org = U.p(ga, gb, 0)
        if lod < 2:
            fl = piece("%s_gauge%d_flange" % (prefix, i), r["bezel"], prefix + "_gauge_flange", org)
            b.plate(fl, U, ga, gb, 2.7 * gr, 2.7 * gr, 0.22 * gr, PLATE_T, PLATE_T + 0.003, n=2 if lod == 0 else 1)
            bz = piece("%s_gauge%d_bezel" % (prefix, i), r["bezel"], prefix + "_gauge_bezel", org)
            prof = [(1.24 * gr, 0.0), (1.22 * gr, 0.0055), (1.12 * gr, 0.0088), (1.04 * gr, 0.0074), (1.02 * gr, 0.0035)]
            b.lathe(bz, U.p(ga, gb, PLATE_T + 0.003), U.n, prof if lod == 0 else [prof[0], prof[2], prof[4]],
                    sides(18), cap1=False)
            parts += [fl, bz]
        fc = piece("%s_gauge%d_face" % (prefix, i), r["dial"], prefix + "_gauge%d_face" % i, org, group=dial_group)
        b.disc(fc, U, ga, gb, GF if lod < 2 else PLATE_T + 0.001, gr * 1.02, sides(20))
        parts.append(fc)
        if lod < 2 and grp:
            parts.append(_needle(m, grp, U, ga, gb, GF + 0.0006, gr * 0.84, 90.0 + sweep / 2, r["needle"], lod))
        if lod < 2:
            gl = piece("%s_gauge%d_glass" % (prefix, i), "black", prefix + "_gauge_glass", org, section="glass")
            b.disc(gl, U, ga, gb, PLATE_T + 0.0098, gr * 1.06, sides(20))
            parts.append(gl)
        if lod == 0:
            for k, (su, sv) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
                q = U.p(ga + su * 1.08 * gr, gb + sv * 1.08 * gr, PLATE_T + 0.003)
                sc = piece("%s_gauge%d_screw%d" % (prefix, i, k), r["screw"], prefix + "_screw_upper", q)
                b.screw(sc, q, U.n, r=0.0027, sides=6)
                parts.append(sc)
    if places:
        gb = places[0][1]
        info["free"] = (a_free, xi1 - 0.02, 0.025, gb - gr * 1.35 - 0.02)
    else:
        info["free"] = (a_free, xi1 - 0.02, 0.025, ul - 0.03)
    # needle axis (memory points): toward the person (needle_axis)
    info["needle_axis"] = lambda gd: needle_axis(U, gd["a"], gd["b"])
    return parts, info


def _needle(m, group, fr, a, bb, c, ln, rest_deg, region, lod=0):
    """Needle: tapering to the tip, with a counterweight and an axis cap; at rest it is at the scale zero."""
    t = math.radians(rest_deg)
    d = fr.u * math.cos(t) + fr.v * math.sin(t)
    s = fr.n.cross(d)
    nf = g.Frame(fr.p(a, bb, c), d, s, fr.n)
    nd = m.part(group + "_part", region, group=group)
    poly = [(-0.24 * ln, -0.0017), (-0.06 * ln, -0.0011), (ln, -0.00022), (ln, 0.00022), (-0.06 * ln, 0.0011),
            (-0.24 * ln, 0.0017)]
    g.prism(nd, poly, (0, 1), 0.0, 0.0006, frame=nf)
    if lod == 0:
        b.lathe(nd, fr.p(a, bb, c - 0.0004), fr.n, [(0.0033, 0.0), (0.0033, 0.0012), (0.0019, 0.0021)], 10)
    return nd
