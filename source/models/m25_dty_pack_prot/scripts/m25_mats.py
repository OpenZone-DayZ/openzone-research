"""M25 materials that kmats does not have: Duty paint worn without rust (from M23), the galvanizing
of the tank, and the solvent with an oil film. The builders are as in kmats:
build_<kind>(mat, origin, **parameters) -> kmats.out(color, gloss, spec, height); the "dayz" look
layers are added by kmats.weather.
"""
import kmats


def near(t, pos, c, r):
    """1 at the center of an ellipsoid (c, semi-axes r), 0 toward the edge."""
    d = t.node("ShaderNodeVectorMath")
    d.operation = "SUBTRACT"
    t.link(pos, d.inputs[0])
    d.inputs[1].default_value = c
    q = t.node("ShaderNodeVectorMath")
    q.operation = "DIVIDE"
    t.link(d.outputs[0], q.inputs[0])
    q.inputs[1].default_value = r
    ln = t.node("ShaderNodeVectorMath")
    ln.operation = "LENGTH"
    t.link(q.outputs[0], ln.inputs[0])
    return t.maprange(ln.outputs["Value"], 0.25, 1.0, 1.0, 0.0)


def build_worn(mat, origin, color, bare=kmats.lin((112, 112, 116)), seed=1.0, gloss=0.32, spec=0.25,
               wear=(0.66, 0.71), edge_k=0.7, rub=(), stripes=(), scratch=0.0, oil=0.0, floor_z=0.0,
               dust=0.15, grime=0.3, decal_items=()):
    """Paint worn by frequent use, without rust (from M23): rubbed down to metal on the edges (edge_k) and
    where hands take it (rub - [(center, semi-axes, strength)]: an ellipsoid, weaker toward the edge);
    scratches along x, oil spots on top (oil); stripes of another color - stripes
    [((x0, x1, y0, y1, z0, z1), color)] in model coordinates. Bare metal does not rust."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.9 for c in color[:3]) + (1,), color)
    for (x0, x1, y0, y1, z0, z1), scol in stripes:
        inside = 1.0
        for i, (a, b) in enumerate(((x0, x1), (y0, y1), (z0, z1))):
            w = sep.outputs[i]
            m = t.math("MULTIPLY", t.math("GREATER_THAN", w, a), t.math("LESS_THAN", w, b))
            inside = m if isinstance(inside, float) else t.math("MULTIPLY", inside, m)
        base = t.mixc(inside, base, scol)
    col = kmats.decals(t, base, sep, nsep, decal_items)
    edge = t.maprange(t.edge_wear(0.004), 0.05, 0.22, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 11.0, 10.0, 0.7), 0.75), t.math("MULTIPLY", edge, edge_k))
    grain = t.maprange(t.noise(vec, 34.0, 8.0, 0.7), 0.3, 0.7, 0.55, 1.0)
    for c, r, k in rub:
        f = t.math("ADD", f, t.math("MULTIPLY", t.math("MULTIPLY", near(t, pos, c, r), grain), k))
    worn = t.step(f, wear[0], wear[1])
    brush = t.noise(t.stretch(vec, 0.04, 1.0, 1.0), 90.0, 4.0, 0.7)
    dk = kmats.LOOK.get("steel", 1.0) if kmats.LOOK["name"] == "dayz" else 1.0
    metal = t.mixc(t.maprange(brush, 0.3, 0.7, 0.0, 1.0), tuple(c * 0.75 * dk for c in bare[:3]) + (1,),
                   tuple(min(1.0, c * 1.15 * dk) for c in bare[:3]) + (1,))
    rim = t.math("SUBTRACT", t.step(f, wear[0] - 0.05, wear[0]), worn)
    col = t.mixc(t.math("MULTIPLY", rim, 0.6), col, kmats.lin((52, 50, 46)))
    col = t.mixc(worn, col, metal)
    h = t.math("MULTIPLY", worn, -0.3)
    g_ = t.math("ADD", gloss, t.math("MULTIPLY", worn, 0.62 - gloss))
    s_ = t.math("ADD", spec, t.math("MULTIPLY", worn, 0.70 - spec))
    if scratch > 0:
        sc = t.step(t.noise(t.stretch(vec, 0.02, 1.0, 1.0), 260.0, 2.0, 0.5), 0.70, 0.73)
        sc = t.math("MULTIPLY", sc, t.maprange(t.noise(vec, 5.0, 4.0, 0.5), 0.35, 0.65, 0.0, scratch))
        col = t.mixc(t.math("MULTIPLY", sc, 0.7), col, metal)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", sc, 0.15))
    if oil > 0:
        up = t.maprange(nsep.outputs["Z"], 0.5, 0.9, 0.0, 1.0)
        ol = t.math("MULTIPLY", t.step(t.noise(vec, 4.0, 6.0, 0.6), 0.62, 0.70), t.math("MULTIPLY", up, oil))
        col = t.mixc(t.math("MULTIPLY", ol, 0.55), col, kmats.lin((14, 12, 10)))
        g_ = t.math("ADD", g_, t.math("MULTIPLY", ol, 0.25))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g_, s_, h)


def build_galv(mat, origin, seed=1.0, tone=0.33, gloss=0.38, spec=0.45, edge_k=0.8, rub=(), stain=0.0,
               floor_z=0.0, dust=0.2, grime=0.35, clean=()):
    """Galvanizing: zinc crystals (Voronoi cells) as blotches of tone, rubbed down to light metal on the
    edges and at the handles (rub); solvent streaks from top to bottom (stain); no rust. In the "dayz"
    look the tone is darker, like bare steel in kmats (LOOK steel): vanilla tin and galvanizing are
    90..130 in sRGB, not 150+. clean - [(x0, x1, y0, y1)]: where something usually stands (an empty
    module place) - cleaner, no dust."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    dk = kmats.LOOK.get("steel", 1.0) if kmats.LOOK["name"] == "dayz" else 1.0
    tone *= dk
    vor = t.node("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 38.0
    t.link(vec, vor.inputs["Vector"])
    cell = t.bw(vor.outputs["Color"])
    smudge = t.noise(vec, 3.0, 6.0, 0.6)
    v = t.math("ADD", tone, t.math("ADD", t.math("MULTIPLY", t.math("SUBTRACT", cell, 0.5), 0.05 * dk),
                                   t.math("MULTIPLY", t.math("SUBTRACT", smudge, 0.5), 0.10 * dk)))
    comb = t.node("ShaderNodeCombineColor")
    for i in range(3):
        t.link(v, comb.inputs[i])
    col = t.mixc(0.15, comb.outputs[0], (0.30 * dk, 0.32 * dk, 0.34 * dk, 1))
    edge = t.maprange(t.edge_wear(0.004), 0.05, 0.22, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 12.0, 8.0, 0.7), 0.5), t.math("MULTIPLY", edge, edge_k))
    for c, r, k in rub:
        f = t.math("ADD", f, t.math("MULTIPLY", near(t, pos, c, r), k))
    worn = t.step(f, 0.62, 0.72)
    col = t.mixc(t.math("MULTIPLY", worn, 0.7), col, tuple(c * (0.75 + 0.25 * dk) for c in kmats.lin((178, 180, 184))[:3]) + (1,))
    g_ = t.math("ADD", gloss, t.math("MULTIPLY", worn, 0.25))
    s_ = t.math("ADD", spec, t.math("MULTIPLY", worn, 0.3))
    if stain > 0:
        drip = t.step(t.noise(t.stretch(vec, 1.0, 1.0, 0.10), 9.0, 8.0, 0.65), 0.55, 0.70)
        drip = t.math("MULTIPLY", drip, stain)
        col = t.mixc(t.math("MULTIPLY", drip, 0.55), col, kmats.lin((74, 62, 44)))
        g_ = t.math("ADD", g_, t.math("MULTIPLY", drip, 0.15))
    spot = 0.0
    for x0, x1, y0, y1 in clean:
        m = 1.0
        for i, (a, b) in enumerate(((x0, x1), (y0, y1))):
            w = sep.outputs[i]
            e = t.math("MULTIPLY", t.maprange(w, a - 0.006, a + 0.006, 0.0, 1.0), t.maprange(w, b + 0.006, b - 0.006, 0.0, 1.0))
            m = e if isinstance(m, float) else t.math("MULTIPLY", m, e)
        spot = m if isinstance(spot, float) else t.math("MAXIMUM", spot, m)
    base = col
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.5)
    if not isinstance(spot, float):
        col = t.mixc(t.math("MULTIPLY", spot, 0.7), col, base)
        dirt = t.math("MULTIPLY", dirt, t.math("SUBTRACT", 1.0, spot))
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.5))
    h = t.math("ADD", t.math("MULTIPLY", cell, 0.04), t.math("MULTIPLY", worn, -0.05))
    return kmats.out(t, col, g_, s_, h)


def build_solvent(mat, origin, color, sheen=kmats.lin((96, 86, 60)), gloss=0.92, spec=0.8):
    """Solvent in the tank: dark amber, with streaks of an oil film and rare spots of dirt over the
    mirror, shiny. No dust: it is a liquid."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 6.1)
    swirl = t.noise(t.stretch(vec, 1.0, 2.2, 1.0), 6.0, 6.0, 0.65)
    film = t.maprange(t.noise(vec, 2.2, 4.0, 0.5), 0.40, 0.75, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", t.maprange(swirl, 0.45, 0.62, 0.0, 1.0), t.math("MULTIPLY", film, 0.55)), color, sheen)
    blot = t.step(t.noise(vec, 9.0, 6.0, 0.6), 0.66, 0.72)
    col = t.mixc(t.math("MULTIPLY", blot, 0.6), col, kmats.lin((26, 22, 16)))
    g_ = t.math("SUBTRACT", gloss, t.math("MULTIPLY", blot, 0.35))
    return kmats.out(t, col, g_, spec, 0.0)
