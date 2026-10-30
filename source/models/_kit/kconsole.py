"""Console base: a floor-standing army instrument console of the 1970s-90s. The first model on it
is m24 (source/models/m24_dty_proc_ball), which also holds the dimensions and references.

Side profile: a plinth, a lower compartment with doors, a setback at the knees; above it an
inclined desk (toggles, knobs, buttons), above that an upper panel tilted back (a round screen and
dial gauges), on top a roof shelf with a visor over the upper panel. At the sides are cheeks that
follow the profile and stand about 1.5 cm above the panels. Close to the vanilla radar_panel.

Parameters: width (x0, x1), depth (y0, y1), height, desk height, tilt of the desk and of the upper
panel, desk length, number of dial gauges (gauges) and whether there is a round screen. The rest
of the fittings (toggles, lamps, readouts) is placed by the model generator in the panel
coordinate frames that console() returns; the helpers toggle / knob / lamp / button / panel_decal
are here for that.

Blender axes: X - width, Y - depth (the front at -Y), Z - up.
"""
import math

from mathutils import Vector

import kgeo as g

CHEEK, PLINTH, CAP_T, TOE = 0.022, 0.07, 0.035, 0.07     # cheek, plinth, roof, setback at the knees
PLATE_T, CHEEK_OUT = 0.004, 0.014                        # panel thickness, how far the cheek rises above the panel
GF = PLATE_T + 0.0065                                    # dial face above the panel (under the bezel ring)


def _offset_poly(poly, offs):
    """Polygon (y, z), counterclockwise: each edge i -> i+1 is moved outward by offs[i]; the
    vertices are the intersections of neighboring moved edges."""
    n = len(poly)
    lines = []
    for i in range(n):
        a, b = Vector(poly[i]), Vector(poly[(i + 1) % n])
        d = (b - a).normalized()
        nrm = Vector((d.y, -d.x))                        # outward for a counterclockwise walk
        lines.append((a + nrm * offs[i], d))
    out = []
    for i in range(n):
        (p1, d1), (p2, d2) = lines[i - 1], lines[i]
        den = d1.x * d2.y - d1.y * d2.x
        if abs(den) < 1e-9:
            out.append(tuple(p2))
            continue
        t = ((p2.x - p1.x) * d2.y - (p2.y - p1.y) * d2.x) / den
        q = p1 + d1 * t
        out.append((q.x, q.y))
    return out


def layout(y0, y1, height, desk_z=0.76, desk_deg=25.0, desk_len=0.30, upper_deg=12.0):
    """Key points of the profile (y, z): the desk goes from (yd0, zd0) up the slope to (yd1, zd1),
    the upper panel up to (yu1, zu1), the roof is above it. Coordinate frames: desk and upper
    (kgeo.Frame, a - world x, b - up along the panel from its lower edge, c - outward)."""
    yd0, zd0 = y0 + 0.02, desk_z
    t = math.radians(desk_deg)
    yd1, zd1 = yd0 + desk_len * math.cos(t), zd0 + desk_len * math.sin(t)
    zu1 = height - CAP_T
    u = math.radians(upper_deg)
    up_len = (zu1 - zd1) / math.cos(u)
    yu1 = yd1 + up_len * math.sin(u)
    return dict(yd0=yd0, zd0=zd0, yd1=yd1, zd1=zd1, yu1=yu1, zu1=zu1, up_len=up_len, desk_len=desk_len,
                yt=y0 + TOE, desk=g.inclined_front(yd0, zd0, 90.0 - desk_deg),
                upper=g.inclined_front(yd1, zd1, upper_deg))


def profile(y0, y1, L):
    """Side outline of the body (y, z), counterclockwise when viewed from +x."""
    return [(y1, PLINTH), (y1, L["zu1"]), (L["yu1"], L["zu1"]), (L["yd1"], L["zd1"]), (L["yd0"], L["zd0"]),
            (y0, L["zd0"] - 0.02), (y0, L["zd0"] - 0.045), (L["yt"], L["zd0"] - 0.075), (L["yt"], PLINTH)]


def disc(part, fr, a, b, c, r, sides):
    """A flat disc facing outward (+c) in frame fr - the glass of a gauge."""
    bm = part.bm
    vs = [bm.verts.new(fr.p(a + r * math.cos(2 * math.pi * k / sides), b + r * math.sin(2 * math.pi * k / sides), c))
          for k in range(sides)]
    f = bm.faces.new(vs)
    f.normal_update()
    if f.normal.dot(fr.n) < 0:
        f.normal_flip()
    return part.tag([f])


def toggle(m, name, fr, a, b, lod, region="steel", down=True):
    """Toggle switch: a nut and a lever tilted down along the panel (down) or up."""
    if lod > 0:
        return []
    p = m.part(name, region, uv_name="cs_toggle", uv_origin=tuple(fr.p(a, b, 0)))
    g.cyl(p, (a, b, 0.003), "z", 0.0065, 0.006, 6, frame=fr)
    s = -1 if down else 1
    g.pipe(p, [tuple(fr.p(a, b, 0.005)), tuple(fr.p(a, b + s * 0.008, 0.024))], 0.0022, 6)
    return [p]


def knob(m, name, fr, a, b, r, lod, region="black", ptr="steel"):
    """Knob with a skirt and a pointer line."""
    kb = m.part(name, region, uv_name="cs_knob%d" % round(r * 1000), uv_origin=tuple(fr.p(a, b, 0)))
    sides = (12 if r >= 0.013 else 10) if lod == 0 else 6
    if lod == 0:
        g.cyl(kb, (a, b, 0.003), "z", r * 1.3, 0.006, sides, frame=fr)
    g.cyl(kb, (a, b, 0.012), "z", r, 0.018, sides, frame=fr)
    parts = [kb]
    if lod == 0:
        pt = m.part(name + "_ptr", ptr, uv_name="cs_knob_ptr", uv_origin=tuple(fr.p(a, b, 0)))
        g.box(pt, a - 0.0014, a + 0.0014, b + r * 0.25, b + r * 0.85, 0.0208, 0.0216, frame=fr)
        parts.append(pt)
    return parts


def lamp(m, name, fr, a, b, region, group, lod, r=0.0065):
    """Indicator lamp: the lens is in the selection group on all LODs, the rim on the near LOD."""
    lens = m.part(name, region, uv_name="cs_lamp_" + region, uv_origin=tuple(fr.p(a, b, 0)), group=group)
    g.cyl(lens, (a, b, 0.006), "z", r, 0.008, (10, 6, 4)[lod], frame=fr)
    if lod > 0:
        return [lens]
    rim = m.part(name + "_rim", "steel", uv_name="cs_lamp_rim%d" % round(r * 1000), uv_origin=tuple(fr.p(a, b, 0)))
    g.cyl(rim, (a, b, 0.002), "z", r * 1.45, 0.004, 10, frame=fr)
    return [rim, lens]


def button(m, name, fr, a, b, region, lod, w=0.009):
    """Button with a square cap."""
    if lod > 0:
        return []
    p = m.part(name, region, uv_name="cs_button_" + region, uv_origin=tuple(fr.p(a, b, 0)))
    g.box(p, a - w, a + w, b - w, b + w, 0.0, 0.010, frame=fr)
    return [p]


def panel_decal(path, fr, a0, a1, b0, b1, c=0.0, slack=0.012):
    """Decal (kmats.decals) on a rectangle of panel fr: projected along the world axis (z up or -y
    toward the front) that the panel is closer to; the range along that axis covers the panel only."""
    p, q = fr.p(a0, b0, c), fr.p(a1, b1, c)
    if abs(fr.n.z) >= abs(fr.n.y):
        return (path, "z", 1, ("x", "y"), ((p.x + q.x) / 2, (p.y + q.y) / 2), (abs(q.x - p.x), abs(q.y - p.y)),
                (min(p.z, q.z) - slack, max(p.z, q.z) + slack))
    return (path, "y", -1, ("x", "z"), ((p.x + q.x) / 2, (p.z + q.z) / 2), (abs(q.x - p.x), abs(q.z - p.z)),
            (min(p.y, q.y) - slack, max(p.y, q.y) + slack))


def _needle(m, group, fr, a, b, c, ln, rest_deg, region, lod=0):
    t = math.radians(rest_deg)
    d = fr.u * math.cos(t) + fr.v * math.sin(t)
    s = fr.u * -math.sin(t) + fr.v * math.cos(t)
    nf = g.Frame(fr.p(a, b, c), d, s, fr.n)
    nd = m.part(group + "_part", region, group=group)
    g.box(nd, -0.15 * ln, ln, -0.0008, 0.0008, 0.0, 0.0008, frame=nf)
    if lod == 0:
        g.cyl(nd, (0, 0, 0.0006), "z", 0.0035, 0.0012, 8, frame=nf)
    return nd


def console(m, spec, x0, x1, y0, y1, height, desk_z=0.76, desk_deg=25.0, desk_len=0.30, upper_deg=12.0,
            gauges=3, gauge_r=0.042, sweep=240.0, screen_r=0.07, doors=2, needles=(), screen_group="ozl_screen",
            regions=None, prefix="cs"):
    """Console base. m is a kmodel.Model. The front is at -Y (y0).

    gauges - how many round dial gauges in a row on the upper panel (right of the screen);
    gauge_r - dial radius; sweep - dial arc in degrees (zero at the bottom left, grows clockwise);
    screen_r - radius of the round screen at the left of the upper panel (0 - no screen); doors -
    doors of the lower compartment (1 or 2). needles - names of the needle bone selections (one per
    gauge; if shorter, the remaining needles are part of the body). Dial faces and the screen are
    in the screen_group selection (the off / working light state is applied to it).
    regions: frame (cheeks, body, roof), desk, upper (upper panel), front (doors), accent (false
      panel of the roof above the screen), handle, foot (plinth), bezel (gauge bezels), dial (dial
      faces), screen, needle, rubber (desk bumper), vent (rear grille), gland (cable gland).
    spec["lod"]: 0 - everything, 1 - no grille, gland and needle caps, door handles as boxes, 2 -
      the body as one prism; roof, panels, dial faces and screen without bezels and glass.

    Returns (parts, info): info is layout() plus xi0/xi1 (panels between the cheeks), gauges -
    [dict(a, b, r, group)], screen - dict(a, b, r) or None, free - (a0, a1, b0, b1) the free room
    on the upper panel below the gauges, right of the screen, for the generator's readouts and lamps."""
    r = dict(frame="cs", desk="cs_desk", upper="cs_upper", front="cs_front", accent="cs_accent", handle="steel",
             foot="black", bezel="black", dial="dial", screen="screen", needle="needle", rubber="rubber",
             vent="grille_v", gland="black")
    r.update(regions or {})
    lod = spec["lod"]
    L = layout(y0, y1, height, desk_z, desk_deg, desk_len, upper_deg)
    poly = profile(y0, y1, L)
    xi0, xi1 = x0 + CHEEK, x1 - CHEEK
    parts = []
    bev = dict(r=0.003, seg=1) if lod == 0 else {}

    # --- body, cheeks, plinth, roof
    body = m.part(prefix + "_body", r["frame"])
    if lod == 2:
        g.prism(body, poly, (1, 2), x0, x1)
    else:
        g.prism(body, poly, (1, 2), xi0, xi1)
        # The cheek is taller than the panels and the face at the front, flush at the back and the
        # bottom; it goes from the plinth down to the floor.
        cheek = _offset_poly(poly, [0.0, 0.0] + [CHEEK_OUT] * 6 + [0.0])
        cheek = [(y, 0.0) if abs(z - PLINTH) < 1e-6 else (y, z) for y, z in cheek]
        for xa, xb in ((x0, xi0), (xi1, x1)):
            g.prism(body, cheek, (1, 2), xa, xb)
    parts.append(body)
    ft = m.part(prefix + "_plinth", r["foot"])
    g.box(ft, xi0, xi1, L["yt"] + 0.03, y1 - 0.01, 0.0, PLINTH + 0.002)
    parts.append(ft)
    cap = m.part(prefix + "_cap", r["frame"])
    yc0 = L["yu1"] - 0.045
    g.box(cap, x0 - 0.004, x1 + 0.004, yc0, y1 + 0.004, L["zu1"], height, **bev)
    parts.append(cap)
    ac = m.part(prefix + "_accent", r["accent"])             # false panel / visor above the upper panel
    g.box(ac, xi0, xi1, yc0 - 0.004, yc0, L["zu1"] - 0.050, height - 0.004)
    if lod < 2:
        g.box(ac, xi0, xi1, yc0, L["yu1"] - 0.010, L["zu1"] - 0.050, L["zu1"] - 0.046)
    parts.append(ac)

    # --- desk panel and upper panel
    dk = m.part(prefix + "_desk_plate", r["desk"])
    g.box(dk, xi0, xi1, 0.0, L["desk_len"], 0.0, PLATE_T, frame=L["desk"])
    up = m.part(prefix + "_upper_plate", r["upper"])
    g.box(up, xi0, xi1, 0.0, L["up_len"] - 0.050 / math.cos(math.radians(upper_deg)), 0.0, PLATE_T, frame=L["upper"])
    parts += [dk, up]
    if lod < 2:
        rb = m.part(prefix + "_bumper", r["rubber"])            # bumper on the front edge of the desk
        g.cyl(rb, ((x0 + x1) / 2, y0 + 0.012, L["zd0"] - 0.016), "x", 0.018, x1 - x0 - 0.004, 12 if lod == 0 else 6)
        parts.append(rb)

    # --- lower compartment doors, handles, rear grille and gland
    fr = m.part(prefix + "_doors", r["front"])
    yt, zt = L["yt"], L["zd0"] - 0.085
    gap = 0.003
    xs = [xi0 + 0.006, xi1 - 0.006] if doors == 1 or lod == 2 else [xi0 + 0.006, (xi0 + xi1) / 2, xi1 - 0.006]
    for i in range(len(xs) - 1):
        g.box(fr, xs[i] + (gap / 2 if i else 0), xs[i + 1] - (gap / 2 if i < len(xs) - 2 else 0), yt - 0.004, yt,
              PLINTH + 0.012, zt, **(dict(r=0.0015, seg=1) if lod == 0 else {}))
    parts.append(fr)
    info = dict(L, xi0=xi0, xi1=xi1, handles=[])
    if lod < 2:
        hd = m.part(prefix + "_handles", r["handle"])
        hz = (PLINTH + zt) / 2 + 0.08
        for hx in ((xs[1] - 0.040, xs[1] + 0.040) if doors == 2 else (xs[1] - 0.045,)):
            info["handles"].append((hx, yt - 0.004, hz))
            if lod == 0:
                g.cyl(hd, (hx, yt - 0.006, hz), "y", 0.012, 0.004, 10)
                g.box(hd, hx - 0.004, hx + 0.004, yt - 0.022, yt - 0.006, hz - 0.030, hz + 0.030)
            else:
                g.box(hd, hx - 0.006, hx + 0.006, yt - 0.016, yt, hz - 0.028, hz + 0.028)
        parts.append(hd)
    if lod == 0:
        vt = m.part(prefix + "_vent", r["vent"])
        g.box(vt, xi0 + 0.06, xi1 - 0.06, y1, y1 + 0.0015, 0.75, 1.05)
        gl = m.part(prefix + "_gland", r["gland"])
        g.cyl(gl, ((x0 + x1) / 2, y1 + 0.012, 0.16), "y", 0.030, 0.024, 10)
        parts += [vt, gl]

    # --- round screen and dial gauges on the upper panel
    U = L["upper"]
    ul = L["up_len"] - 0.050
    sides = lambda n0: n0 if lod == 0 else 8 if lod == 1 else 6   # noqa: E731
    info["screen"] = None
    a_free = xi0 + 0.03
    if screen_r > 0:
        sa, sb = xi0 + 0.035 + screen_r * 1.3, ul * 0.52
        info["screen"] = dict(a=sa, b=sb, r=screen_r)
        if lod < 2:
            bz = m.part(prefix + "_screen_bezel", r["bezel"])
            g.cyl(bz, (sa, sb, PLATE_T + 0.006), "z", screen_r * 1.30, 0.012, sides(24), frame=U)
            g.cyl(bz, (sa, sb, PLATE_T + 0.026), "z", screen_r * 1.12, 0.030, sides(24), cap=False, frame=U)
            parts.append(bz)
        sc = m.part(prefix + "_screen", r["screen"], group=screen_group)
        disc(sc, U, sa, sb, PLATE_T + 0.0125, screen_r, sides(24))
        parts.append(sc)
        if lod < 2:
            gl = m.part(prefix + "_screen_glass", "black", section="glass")
            disc(gl, U, sa, sb, PLATE_T + 0.0145, screen_r, sides(24))
            parts.append(gl)
        a_free = sa + screen_r * 1.3 + 0.03
    info["gauges"] = []
    if gauges:
        step = (xi1 - 0.02 - a_free) / gauges
        gb = ul * 0.74
        for i in range(gauges):
            ga = a_free + step * (i + 0.5)
            grp = needles[i] if i < len(needles) else None
            info["gauges"].append(dict(a=ga, b=gb, r=gauge_r, group=grp))
            if lod < 2:
                bz = m.part("%s_gauge%d_bezel" % (prefix, i), r["bezel"], uv_name=prefix + "_gauge_bezel",
                            uv_origin=tuple(U.p(ga, gb, 0)))
                g.cyl(bz, (ga, gb, PLATE_T + 0.003), "z", gauge_r * 1.22, 0.006, sides(20), frame=U)
                if lod == 0:
                    g.cyl(bz, (ga, gb, PLATE_T + 0.0085), "z", gauge_r * 1.10, 0.005, 20, cap=False, frame=U)
                parts.append(bz)
            fc = m.part("%s_gauge%d_face" % (prefix, i), r["dial"], group=screen_group)
            disc(fc, U, ga, gb, GF, gauge_r, sides(20))
            parts.append(fc)
            if lod < 2 and grp:
                parts.append(_needle(m, grp, U, ga, gb, GF + 0.0006, gauge_r * 0.82, 90.0 + sweep / 2, r["needle"], lod))
            if lod < 2:
                gl = m.part("%s_gauge%d_glass" % (prefix, i), "black", section="glass")
                disc(gl, U, ga, gb, GF + 0.004, gauge_r * 1.1, sides(20))
                parts.append(gl)
        info["free"] = (a_free, xi1 - 0.02, 0.025, gb - gauge_r * 1.22 - 0.02)
    else:
        info["free"] = (a_free, xi1 - 0.02, 0.025, ul - 0.03)
    # Needle axis (memory points): from the axis into the panel.
    info["needle_axis"] = lambda gd: (tuple(U.p(gd["a"], gd["b"], GF + 0.0006)), tuple(U.p(gd["a"], gd["b"], GF - 0.02)))
    return parts, info
