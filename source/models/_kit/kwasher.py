"""Twin-tub washing machine base: a Soviet machine with a centrifuge of the "Sibir-5/5M" type - a
body on a plinth, a lid deck on top with two compartments: on the left the washing tub under a
rectangular lid, on the right the centrifuge - a round opening in the deck with a casing and a
drum below it; both lids have hinges at the back. At the front under the deck are a chrome
molding and a control panel with three knobs ("wash" 0-5, "spin" 0-3, "mode" 1-2).

Dimensions follow the Sibir-5 datasheet: 675 x 700 x 375 mm (W x H x D), 40 kg; Sibir-5M -
670 x 700 x 375, Sibir-6 - 680 x 700 x 380. The compartments, the panel and the centrifuge
opening follow the datasheet photo and the panel photo: the washing compartment is wider (~0.55
of the width), the panel spans almost the whole width under the deck.

The back wall can be removed (back_open): the tub, the centrifuge casing, motors and the hose
are visible - as on m10. The centrifuge lid can stay open (spin_open, permanently): the drum is
visible. The drum is its own group (a machine bone). Fittings (props, wires) live in the model
generator, not here.
"""
import math

import kgeo as g

T = 0.012                                  # body wall (face, sides, floor)
DECK_H = 0.030                             # deck thickness
PLINTH = 0.030                             # plinth height
# Panel knobs: fractions of the panel width (the generator's make_decals draws the scales at the same fractions).
KNOB_FR = (0.20, 0.50, 0.80)
KNOB_R, WELL_R = 0.026, 0.036


def layout(x0, x1, y0, y1, z0, height=0.70, split=0.55):
    """Where the machine parts are: the deck top zt, the compartment border xs, the lids
    [(xa, xb, ya, yb)], the center and radius of the centrifuge opening, the panel
    (xa, xb, za, zb) and its face, the knob centers, the hinge axis."""
    zt = z0 + height
    xs = x0 + (x1 - x0) * split
    wash = (x0 + 0.025, xs - 0.012, y0 + 0.028, y1 - 0.030)
    spin = (xs + 0.012, x1 - 0.025, y0 + 0.028, y1 - 0.030)
    sc = ((spin[0] + spin[1]) / 2, (y0 + y1) / 2 - 0.004)
    panel = (x0 + 0.040, x1 - 0.040, zt - 0.175, zt - 0.048)
    yp = y0 - 0.006                                      # panel face
    zk = (panel[2] + panel[3]) / 2
    knobs = [(panel[0] + (panel[1] - panel[0]) * f, zk) for f in KNOB_FR]
    return dict(zt=zt, xs=xs, wash=wash, spin=spin, spin_c=sc, spin_r=0.118, house_r=0.132,
                panel=panel, panel_y=yp, knobs=knobs, hinge_y=y1 - 0.030, trim_z=zt - 0.034)


def cup(part, cx, cy, r_out, r_in, z0, z1, z_floor, sides):
    """A cup with a thick wall: an outer cylinder z0..z1, a ring on top, an inner wall down to the
    floor z_floor. A closed body, so the normals are computed automatically; the inside is visible
    (casing, drum)."""
    bm = part.bm
    ring = lambda r, z: [bm.verts.new((cx + r * math.cos(2 * math.pi * k / sides),
                                       cy + r * math.sin(2 * math.pi * k / sides), z)) for k in range(sides)]
    ob, ot, it, ib = ring(r_out, z0), ring(r_out, z1), ring(r_in, z1), ring(r_in, z_floor)
    faces = [bm.faces.new(ob[::-1]), bm.faces.new(ib)]
    for k in range(sides):
        j = (k + 1) % sides
        faces.append(bm.faces.new([ob[k], ob[j], ot[j], ot[k]]))
        faces.append(bm.faces.new([ot[k], ot[j], it[j], it[k]]))
        faces.append(bm.faces.new([it[k], it[j], ib[j], ib[k]]))
    import bmesh
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return part.tag(faces)


def lid_frame(hinge_y, z, open_deg):
    """Frame of an open lid: the hinges are at (y = hinge_y, z), b runs along the lid from the
    hinges upward (tilted back by open_deg - 90 from the vertical), c is the thickness toward the
    front of the machine."""
    t = math.radians(open_deg - 90.0)
    return g.Frame((0, hinge_y, z), (1, 0, 0), (0, math.sin(t), math.cos(t)), (0, -math.cos(t), math.sin(t)))


def twin_tub(m, spec, x0, x1, y0, y1, z0, height=0.70, split=0.55, back_open=True, spin_open=True,
             open_deg=100.0, drum_group="body", regions=None, prefix="tt"):
    """Twin-tub base. m is a kmodel.Model. The front is at -Y (y0), the plinth bottom is at z0.

    regions: body (body enamel), deck, panel and lid (the faction color: the panel and the lids),
    trim (chrome: molding, hinges, knob inserts), knob (knobs), well (knob sockets, plinth), inner
    (the darkness inside the body), tank (the tub, the centrifuge casing from inside), drum, motor,
    hose. spec["lod"]: 0 - everything, 1 - no motors and hinges, 2 - a box, deck, lids and panel;
    the centrifuge opening is a dark disc, the drum is a disc. drum_group - the drum group (bone)."""
    r = dict(body="tt_body", deck="tt_deck", panel="tt_panel", lid="tt_lid", trim="chrome", knob="tt_knob",
             well="black", inner="tt_inner", tank="tt_tank", drum="tt_drum", motor="black", hose="rubber")
    r.update(regions or {})
    lod, sd = spec["lod"], spec.get("sides", 16)
    lay = layout(x0, x1, y0, y1, z0, height, split)
    zt, xs = lay["zt"], lay["xs"]
    zd = zt - DECK_H
    (scx, scy), sr, hr = lay["spin_c"], lay["spin_r"], lay["house_r"]
    bev = dict(r=0.004, seg=1) if lod == 0 else {}         # less than half the wall T: the bevels do not meet
    parts = []

    # --- body: face, sides, floor; the back is open (back_open) or closed
    bd = m.part(prefix + "_body", r["body"])
    zb = z0 + PLINTH
    if back_open and lod < 2:
        g.box(bd, x0, x1, y0, y0 + T, zb, zd, **bev)
        for xa, xb in ((x0, x0 + T), (x1 - T, x1)):
            g.box(bd, xa, xb, y0 + T, y1, zb, zd, **bev)
        g.box(bd, x0 + T, x1 - T, y0 + T, y1, zb, zb + T)
    else:
        g.box(bd, x0, x1, y0, y1, zb, zd, **bev)
    parts.append(bd)
    pl = m.part(prefix + "_plinth", r["well"])
    g.box(pl, x0 + 0.012, x1 - 0.012, y0 + 0.012, y1 - (0.0 if back_open else 0.012), z0, zb + 0.002)
    parts.append(pl)

    # --- deck: with the centrifuge opening (boolean difference); on the far LOD it is solid with a dark disc
    dk = m.part(prefix + "_deck", r["deck"])
    g.box(dk, x0 - 0.004, x1 + 0.004, y0 - 0.008, y1, zd, zt, **(dict(r=0.010, seg=2) if lod == 0 else {}))
    if lod < 2 and spin_open:
        cut = m.part(prefix + "_deck_cut", r["deck"])
        g.cyl(cut, (scx, scy, (zd + zt) / 2), "z", sr, DECK_H + 0.04, sd)
        dk = m.boolean(prefix + "_deck", dk, [cut])
    parts.append(dk)
    if lod == 2 and spin_open:
        hole = m.part(prefix + "_spin_hole", r["inner"])
        g.cyl(hole, (scx, scy, zt + 0.0006), "z", sr, 0.0012, sd)
        parts.append(hole)

    # --- molding under the deck at the front
    tr = m.part(prefix + "_trim", r["trim"])
    g.box(tr, x0 + 0.002, x1 - 0.002, y0 - 0.004, y0 + 0.001, lay["trim_z"] - 0.007, lay["trim_z"])
    parts.append(tr)

    # --- control panel, sockets and knobs
    pa, pb, pza, pzb = lay["panel"]
    yp = lay["panel_y"]
    pn = m.part(prefix + "_panel", r["panel"])
    g.box(pn, pa, pb, yp, y0 + 0.001, pza, pzb, **(dict(r=0.003, seg=1) if lod == 0 else {}))
    parts.append(pn)
    if lod < 2:
        wl = m.part(prefix + "_wells", r["well"])
        kn = m.part(prefix + "_knobs", r["knob"])
        ki = m.part(prefix + "_knob_bars", r["trim"])
        n = (16, 8)[lod]
        for kx, kz in lay["knobs"]:
            g.cyl(wl, (kx, yp - 0.0005, kz), "y", WELL_R, 0.002, n)
            g.cyl(kn, (kx, yp - 0.006, kz), "y", KNOB_R, 0.010, n)
            g.box(kn, kx - 0.008, kx + 0.008, yp - 0.024, yp - 0.010, kz - 0.030, kz + 0.030,
                  **(dict(r=0.003, seg=1) if lod == 0 else {}))
            if lod == 0:
                g.box(ki, kx - 0.0025, kx + 0.0025, yp - 0.0245, yp - 0.020, kz - 0.024, kz + 0.024)
        parts += [wl, kn] + ([ki] if lod == 0 else [])
        if lod == 0:
            sc = m.part(prefix + "_screws", r["trim"])
            for x in (pa + 0.012, pb - 0.012):
                g.cyl(sc, (x, yp - 0.001, (pza + pzb) / 2), "y", 0.0045, 0.003, 8)
            parts.append(sc)

    # --- lid of the washing compartment (closed) with a handle
    wa, wb, wya, wyb = lay["wash"]
    wlid = m.part(prefix + "_wash_lid", r["lid"])
    g.box(wlid, wa, wb, wya, wyb, zt, zt + 0.014, **(dict(r=0.006, seg=1) if lod == 0 else {}))
    parts.append(wlid)
    if lod < 2:
        wh = m.part(prefix + "_wash_handle", r["trim"])
        xm = (wa + wb) / 2
        g.box(wh, xm - 0.04, xm + 0.04, wya + 0.006, wya + 0.024, zt + 0.014, zt + 0.024)
        parts.append(wh)

    # --- centrifuge lid: open on the hinges at the back (spin_open) or closed
    sa, sb, sya, syb = lay["spin"]
    slid = m.part(prefix + "_spin_lid", r["lid"])
    ld = syb - sya
    if spin_open:
        fr = lid_frame(lay["hinge_y"], zt + 0.004, open_deg)
        g.box(slid, sa, sb, 0.0, ld, 0.0, 0.014, frame=fr, **(dict(r=0.006, seg=1) if lod == 0 else {}))
        if lod < 2:
            # a handle on the edge, hinges
            sh = m.part(prefix + "_spin_handle", r["trim"])
            xm = (sa + sb) / 2
            g.box(sh, xm - 0.035, xm + 0.035, ld - 0.024, ld - 0.006, -0.010, 0.0, frame=fr)
            if lod == 0:
                for x in (sa + 0.05, sb - 0.05):
                    g.box(sh, x - 0.03, x + 0.03, -0.004, 0.022, 0.014, 0.020, frame=fr)
            parts.append(sh)
    else:
        g.box(slid, sa, sb, sya, syb, zt, zt + 0.014)
    parts.append(slid)

    # --- centrifuge: the casing under the opening and the drum (group drum_group)
    if spin_open:
        if lod < 2:
            hs = m.part(prefix + "_spin_house", r["tank"])
            cup(hs, scx, scy, hr, sr - 0.001, zd - 0.43, zd + 0.001, zd - 0.42, sd)
            parts.append(hs)
        dr = m.part(prefix + "_drum", r["drum"], group=drum_group)
        if lod < 2:
            cup(dr, scx, scy, sr - 0.010, sr - 0.016, zd - 0.40, zt - 0.045, zd - 0.392, sd)
            # ribs on the bottom and a hub: they make the rotation visible
            for k in range(3 if lod == 0 else 0):
                a = 2 * math.pi * k / 3 + 0.3
                f = g.Frame((scx, scy, 0.0), (-math.sin(a), math.cos(a), 0), (0, 0, 1), (math.cos(a), math.sin(a), 0))
                g.box(dr, -0.006, 0.006, zd - 0.392, zd - 0.374, 0.02, sr - 0.017, frame=f)
            g.cyl(dr, (scx, scy, zd - 0.382), "z", 0.030, 0.022, (12, 8)[lod])
        else:
            g.cyl(dr, (scx, scy, zt + 0.0016), "z", sr - 0.016, 0.0006, sd)
        parts.append(dr)

    # --- with the back wall removed: tub, motors, hose
    if back_open and lod < 2:
        tk = m.part(prefix + "_tank", r["tank"])
        g.box(tk, x0 + T + 0.010, xs - 0.008, y0 + T + 0.012, y1 - 0.055, zd - 0.40, zd - 0.002,
              **(dict(r=0.020, seg=2) if lod == 0 else {}))
        parts.append(tk)
        inn = m.part(prefix + "_inner", r["inner"])
        # darkness behind the tub and the casing: a partition at the face
        g.box(inn, x0 + T, x1 - T, y0 + T, y0 + T + 0.010, zb + T, zd)
        parts.append(inn)
        if lod == 0:
            mt = m.part(prefix + "_motors", r["motor"])
            # the activator motor (lying, toward the pulley) and the centrifuge motor under the casing (standing)
            g.cyl(mt, ((x0 + xs) / 2, y1 - 0.12, zb + T + 0.065), "y", 0.060, 0.13, 12)
            g.cyl(mt, ((x0 + xs) / 2, y1 - 0.045, zb + T + 0.065), "y", 0.040, 0.012, 12)
            g.cyl(mt, (scx, scy, zd - 0.48), "z", 0.055, 0.12, 12)
            g.box(mt, xs - 0.06, xs + 0.02, y1 - 0.12, y1 - 0.04, zb + T, zb + T + 0.07)   # pump
            parts.append(mt)
            hz = m.part(prefix + "_hose", r["hose"])
            pts = [(xs - 0.02, y1 - 0.08, zb + T + 0.05), (xs - 0.03, y1 + 0.02, zb + T + 0.05),
                   (xs - 0.10, y1 + 0.06, zb + 0.20), (x0 + 0.10, y1 + 0.03, zd - 0.06), (x0 + 0.06, y1 - 0.01, zd - 0.05)]
            g.pipe(hz, pts, 0.012, 8)
            parts.append(hz)
    return parts
