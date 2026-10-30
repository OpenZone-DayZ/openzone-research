"""M13 materials that kmats does not provide: lead sheet, rusty hot-rolled steel, worn lock paint.
Procedural, as in kmats: the atlas is baked from them (the "dayz" look comes from kmats.weather: dust,
dirt in corners, stains, streaks, scratches).

Lead follows mat_lead of the M75 module (the same colour as the M48 probe and the M71 hut: the "Khabar"
line shares one lead family), but is darker, dustier and oxidised, plus a clean rectangle in the dust
where the instrument lay (empty slot 1).
"""
import kmats

LEAD_C = kmats.lin((96, 99, 105))
LEAD_DARK = kmats.lin((66, 69, 74))
OXIDE = kmats.lin((168, 170, 164))
BRIGHT = kmats.lin((150, 154, 162))
POLISH = kmats.lin((118, 122, 130))
MILL = kmats.lin((58, 60, 62))                # mill scale of hot-rolled steel
MILL_DARK = kmats.lin((40, 41, 44))


def rotated(t, vec, euler):
    m = t.node("ShaderNodeMapping")
    m.inputs["Rotation"].default_value = euler
    t.link(vec, m.inputs["Vector"])
    return m.outputs[0]


def scratches(t, vec, nsep, amount=1.0):
    """Short straight scratches (from M71/M75): contours of stretched noise, masked to 2-3 cm segments."""
    out = None
    fams = [((0.03, 1.0, 1.0), 0, None, 2.2, 3.4), ((1.0, 0.03, 1.0), 1, None, 2.4, 3.9),
            ((1.0, 1.0, 0.03), 2, None, 2.0, 3.1), ((0.03, 1.0, 1.0), None, (0.62, 0.45, 0.80), 2.6, 4.4)]
    for st, ax, rot, sc, ms in fams:
        v = rotated(t, vec, rot) if rot else vec
        n = t.noise(t.stretch(v, *st), sc, 2.0, 0.5)
        line = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", n, 0.5)), 0.0, 0.007, 1.0, 0.0)
        mask = t.maprange(t.noise(v, ms, 3.0, 0.5), 0.60, 0.70, 0.0, 1.0)
        s = t.math("MULTIPLY", line, mask)
        if ax is not None:
            s = t.math("MULTIPLY", s, t.maprange(t.math("ABSOLUTE", nsep.outputs[ax]), 0.4, 0.8, 1.0, 0.0))
        out = s if out is None else t.math("MAXIMUM", out, s)
    return t.math("MULTIPLY", out, amount)


def dents(t, vec, scale, amount):
    """Small hammer dents: Voronoi cells, a bowl in a few cells (from M71)."""
    vor = t.node("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = scale
    t.link(vec, vor.inputs["Vector"])
    bowl = t.maprange(vor.outputs["Distance"], 0.05, 0.38, 1.0, 0.0)
    pick = t.math("GREATER_THAN", t.bw(vor.outputs["Color"]), 1.0 - amount)
    return t.math("MULTIPLY", t.math("MULTIPLY", bowl, bowl), pick)


def rect_mask(t, sep, rect, soft):
    """1 inside the rectangle (x0, x1, y0, y1) in model coordinates, soft edge `soft`."""
    x0, x1, y0, y1 = rect
    m = None
    for i, (a, b) in enumerate(((x0, x1), (y0, y1))):
        w = sep.outputs[i]
        e = t.math("MULTIPLY", t.maprange(w, a - soft, a + soft, 0.0, 1.0), t.maprange(w, b + soft, b - soft, 0.0, 1.0))
        m = e if m is None else t.math("MULTIPLY", m, e)
    return m


def build_lead(mat, origin, seed=1.0, color=LEAD_C, decal_items=(), clean=(), floor_z=0.0, dust=0.45, grime=0.6,
               oxide=0.35, rust_streaks=0.0):
    """3 mm lead sheet, crudely nailed to the chest: dull, whitish oxide in patches, small dents, scratches
    down to bright metal, worn edges, dust on top, dirt in corners and streaks (weather).
    clean - [(x0, x1, y0, y1)]: an instrument lay there for a long time - lead without dust, dust piled up
    along the edge. rust_streaks - rusty streaks running down from the steel rivets (verticals)."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    v10 = t.stretch(vec, 10.0, 10.0, 10.0)
    col = t.mixc(t.maprange(t.noise(v10, 1.2, 6.0, 0.6), 0.3, 0.75, 0.0, 1.0), LEAD_DARK, color)
    dn = dents(t, v10, 9.0, 0.35)
    col = t.mixc(t.math("MULTIPLY", dn, 0.25), col, POLISH)
    blot = t.maprange(t.noise(v10, 0.9, 6.0, 0.6), 0.55, 0.78, 0.0, 1.0)
    speck = t.maprange(t.noise(v10, 9.0, 4.0, 0.6), 0.64, 0.80, 0.0, 1.0)
    ox = t.math("MINIMUM", t.math("ADD", t.math("MULTIPLY", blot, oxide), t.math("MULTIPLY", speck, 0.45)), 0.7)
    col = t.mixc(ox, col, OXIDE)
    col = kmats.decals(t, col, sep, nsep, decal_items)
    if rust_streaks > 0:
        vert = t.maprange(t.math("ABSOLUTE", nsep.outputs["Z"]), 0.3, 0.6, 1.0, 0.0)
        st = t.step(t.noise(t.stretch(vec, 1.0, 1.0, 0.06), 22.0, 5.0, 0.6), 0.64, 0.74)
        st = t.math("MULTIPLY", t.math("MULTIPLY", st, vert), rust_streaks)
        col = t.mixc(st, col, kmats.RUST[1])
    scr = scratches(t, v10, nsep, 0.8)
    col = t.mixc(t.math("MULTIPLY", scr, 0.7), col, BRIGHT)
    edge = t.maprange(t.edge_wear(0.002), 0.05, 0.30, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.5), col, POLISH)
    col0 = col
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    spot = None
    for rect in clean:
        inner = rect_mask(t, sep, rect, 0.004)
        x0, x1, y0, y1 = rect
        outer = rect_mask(t, sep, (x0 - 0.012, x1 + 0.012, y0 - 0.012, y1 + 0.012), 0.006)
        rim = t.math("MAXIMUM", t.math("SUBTRACT", outer, inner), 0.0)
        up = t.maprange(nsep.outputs["Z"], 0.5, 0.9, 0.0, 1.0)
        col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", rim, up), 0.45), col, kmats.DUST)
        col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", inner, up), 0.9), col, col0)
        spot = inner if spot is None else t.math("MAXIMUM", spot, inner)
    if spot is not None:
        dirt = t.math("MULTIPLY", dirt, t.math("SUBTRACT", 1.0, spot))
    gl = t.math("ADD", 0.16, t.math("SUBTRACT", t.math("ADD", t.math("MULTIPLY", scr, 0.25), t.math("MULTIPLY", edge, 0.2)),
                                    t.math("ADD", t.math("MULTIPLY", ox, 0.10), t.math("MULTIPLY", dirt, 0.08))))
    sp = t.math("ADD", 0.12, t.math("SUBTRACT", t.math("ADD", t.math("MULTIPLY", scr, 0.3), t.math("MULTIPLY", edge, 0.2)),
                                    t.math("MULTIPLY", dirt, 0.06)))
    h = t.math("SUBTRACT", 0.0, t.math("ADD", t.math("MULTIPLY", scr, 0.25), t.math("MULTIPLY", dn, 0.6)))
    return kmats.out(t, col, gl, sp, h)


def build_rusty(mat, origin, seed=1.0, rust=0.5, floor_z=0.0, dust=0.3, grime=0.5, bright=0.0, scale=1.0):
    """Hot-rolled steel in the open air (angles, lugs, chain, weld): dark mill scale in patches, orange rust
    (rust is a fraction; more at the bottom and along edges), brown streaks, bare metal on the edges (bright:
    the chain rubs on its links)."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    vs = t.stretch(vec, scale, scale, scale)
    col = t.mixc(t.maprange(t.noise(vs, 5.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0), MILL_DARK, MILL)
    edge = t.maprange(t.edge_wear(0.003), 0.05, 0.25, 0.0, 1.0)
    low = t.maprange(sep.outputs["Z"], floor_z + 0.4, floor_z, 0.0, 0.25)
    f = t.math("ADD", t.math("ADD", t.noise(vs, 7.0, 8.0, 0.7), t.math("MULTIPLY", edge, 0.25)), low)
    patch = t.step(f, 1.0 - rust, 1.0 - rust + 0.12)
    rust_col = t.ramp(t.noise(vs, 28.0, 6.0, 0.6), [(0.3, kmats.RUST[0]), (0.55, kmats.RUST[1]), (0.8, kmats.RUST[2])])
    col = t.mixc(t.math("MULTIPLY", patch, 0.92), col, rust_col)
    drip = t.step(t.noise(t.stretch(vec, 1.0, 1.0, 0.10), 10.0, 6.0, 0.6), 0.64, 0.74)
    vert = t.maprange(t.math("ABSOLUTE", nsep.outputs["Z"]), 0.3, 0.6, 1.0, 0.0)
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", drip, vert), 0.5), col, kmats.RUST[0])
    if bright > 0:
        col = t.mixc(t.math("MULTIPLY", edge, bright), col, kmats.lin((112, 108, 102)))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g_ = t.math("SUBTRACT", 0.30, t.math("ADD", t.math("MULTIPLY", patch, 0.18), t.math("MULTIPLY", dirt, 0.1)))
    s_ = t.math("SUBTRACT", 0.30, t.math("ADD", t.math("MULTIPLY", patch, 0.20), t.math("MULTIPLY", dirt, 0.1)))
    if bright > 0:
        g_ = t.math("ADD", g_, t.math("MULTIPLY", edge, bright * 0.3))
        s_ = t.math("ADD", s_, t.math("MULTIPLY", edge, bright * 0.4))
    h = t.math("MULTIPLY", patch, t.math("SUBTRACT", t.noise(vs, 90.0, 4.0, 0.6), 0.5))
    return kmats.out(t, col, g_, s_, h)
