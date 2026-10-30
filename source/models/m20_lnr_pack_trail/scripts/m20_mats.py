"""M20 materials that the kit does not have: the lacquered wood of a school cabinet. The pattern is as
in kwood.build_wood (grain, annual rings, knots, patchy tone), but with more contrast (otherwise from a
distance the cabinet looks almost uniform): dark strands of texture along the grain and a wider board
tone. In addition the lacquer is worn by hands down to light wood - on the edges and where hands take
hold (rub), and clean places on the shelves where a device usually stands (clean: an empty module slot -
a trace without dust).
"""
import kmats


def _rect(t, sep, lo, hi, axis, soft):
    """0..1: the coordinate along axis within [lo, hi], edges soft by `soft`."""
    w = sep.outputs[axis]
    return t.math("MULTIPLY", t.maprange(w, lo - soft, lo + soft, 0.0, 1.0), t.maprange(w, hi + soft, hi - soft, 0.0, 1.0))


def build_lacquer(mat, origin, color=kmats.lin((104, 64, 40)), seed=1.0, along="x", gloss=0.40, spec=0.28,
                  floor_z=0.0, dust=0.35, grime=0.5, rings=0.65, knots=0.25, figure=0.45, tone=0.16, bare=None,
                  rub=(), wear=(0.74, 0.80), edge_k=0.55, clean=(), decal_items=()):
    """color - lacquer tone (linear RGBA), along - grain axis, rings / figure - strength of the annual rings
    and dark strands, tone - tone spread in patches (a fraction); bare - the colour of wood under the worn
    lacquer (lighter and greyer than the lacquer by default); rub - [(centre, semi-axes, strength)]
    ellipsoids where the lacquer is worn by hands; wear - the worn threshold; clean - [(x0, x1, y0, y1, z0,
    z1)] top faces where a device usually stands: no dust or dirt there."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    k = {"x": (0.04, 1.0, 1.0), "y": (1.0, 0.04, 1.0), "z": (1.0, 1.0, 0.04)}[along]
    fib = t.stretch(vec, *k)
    fibers = t.noise(fib, 160.0, 4.0, 0.7)
    wave = t.node("ShaderNodeTexWave", Scale=9.0, Distortion=6.0, **{"Detail": 3.0, "Detail Scale": 1.5})
    wave.wave_type = "RINGS"
    t.link(fib, wave.inputs["Vector"])
    ring = t.math("MULTIPLY", wave.outputs["Fac"], rings)
    # texture strands: long dark stripes along the grain, wider than the annual rings
    strand = t.step(t.noise(t.stretch(vec, *[0.12 if x < 1 else 1.0 for x in k]), 26.0, 5.0, 0.65), 0.50, 0.66)
    tn = t.maprange(t.noise(vec, 1.6, 3.0, 0.5), 0.28, 0.72, 0.0, 1.0)
    dark = tuple(c * 0.50 for c in color[:3]) + (1,)
    base = t.mixc(tn, tuple(c * (1 - tone) for c in color[:3]) + (1,), tuple(min(1.0, c * (1 + tone)) for c in color[:3]) + (1,))
    col = t.mixc(t.math("MULTIPLY", ring, 0.85), base, dark)
    col = t.mixc(t.math("MULTIPLY", strand, figure), col, dark)
    col = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", fibers, 0.35), 0.55), col, dark)
    knot = t.step(t.noise(t.stretch(vec, *[0.4 if x < 1 else 1.0 for x in k]), 6.0, 2.0, 0.5),
                  1.0 - 0.06 * knots, 1.0 - 0.03 * knots)
    col = t.mixc(t.math("MULTIPLY", knot, 0.85), col, tuple(c * 0.35 for c in color[:3]) + (1,))
    col = kmats.decals(t, col, sep, nsep, decal_items)
    # lacquer worn: sharp edges and places that hands take hold of (rub
    # ellipsoids; weaker toward the edge, ragged along the grain)
    edge = t.maprange(t.edge_wear(0.004), 0.05, 0.22, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 9.0, 8.0, 0.7), 0.7), t.math("MULTIPLY", edge, edge_k))
    grain = t.maprange(t.noise(fib, 40.0, 6.0, 0.7), 0.3, 0.7, 0.45, 1.0)
    for c, r, kk in rub:
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
        near = t.maprange(ln.outputs["Value"], 0.2, 1.0, 1.0, 0.0)
        f = t.math("ADD", f, t.math("MULTIPLY", t.math("MULTIPLY", near, grain), kk))
    worn = t.step(f, wear[0], wear[1])
    bare = bare or tuple(min(1.0, c * 1.7) for c in color[:3]) + (1,)
    bare_col = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", fibers, 0.3), 0.7), bare,
                      tuple(c * 0.72 for c in bare[:3]) + (1,))
    # at the border of the worn area the lacquer is darker (greasy from hands)
    rim = t.math("SUBTRACT", t.step(f, wear[0] - 0.08, wear[0]), worn)
    col = t.mixc(t.math("MULTIPLY", rim, 0.45), col, tuple(c * 0.6 for c in color[:3]) + (1,))
    col = t.mixc(t.math("MULTIPLY", worn, 0.85), col, bare_col)
    pre = col
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.5)
    if clean:
        # device trace: on a top face inside the rectangle - no dust or dirt (the profile colour is muted as
        # everywhere else, otherwise the spot would come out brighter)
        up = t.maprange(nsep.outputs["Z"], 0.6, 0.9, 0.0, 1.0)
        spot = 0.0
        for x0, x1, y0, y1, z0, z1 in clean:
            m = t.math("MULTIPLY", _rect(t, sep, x0, x1, 0, 0.012), _rect(t, sep, y0, y1, 1, 0.012))
            m = t.math("MULTIPLY", m, _rect(t, sep, z0, z1, 2, 0.0005))
            spot = m if isinstance(spot, float) else t.math("MAXIMUM", spot, m)
        spot = t.math("MULTIPLY", spot, up)
        cl = pre
        if kmats.LOOK["name"] == "dayz":
            d_, v_ = kmats.LOOK["patina"]
            gray = t.node("ShaderNodeRGBToBW")
            t.link(pre, gray.inputs[0])
            cl = t.mixc(d_, pre, gray.outputs[0])
            cl = t.mixc(1.0 - v_, cl, (0, 0, 0, 1))
        col = t.mixc(t.math("MULTIPLY", spot, 0.7), col, cl)
        dirt = t.math("MULTIPLY", dirt, t.math("SUBTRACT", 1.0, t.math("MULTIPLY", spot, 0.7)))
    g = t.math("SUBTRACT", t.math("ADD", gloss, t.math("MULTIPLY", worn, 0.14 - gloss)), t.math("MULTIPLY", dirt, gloss * 0.6))
    s = t.math("SUBTRACT", t.math("ADD", spec, t.math("MULTIPLY", worn, 0.08 - spec)), t.math("MULTIPLY", dirt, spec * 0.5))
    h = t.math("ADD", t.math("MULTIPLY", fibers, 0.25), t.math("MULTIPLY", ring, -0.25))
    h = t.math("SUBTRACT", h, t.math("ADD", t.math("MULTIPLY", knot, 0.3), t.math("MULTIPLY", worn, 0.12)))
    return kmats.out(t, col, g, s, h)
