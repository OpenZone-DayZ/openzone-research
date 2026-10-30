"""M19 material that the kit does not have: veneer under lacquer, rubbed by hands (Neutrals: lived-in,
wood rubbed by hands). The wood pattern is as in kwood.build_wood; over it a lacquer: on edges and where
hands take hold (rub) it is worn down to light matte wood, on the roof - mug rings (cups) and decals.
"""
import kmats


def build_veneer(mat, origin, color=kmats.lin((78, 44, 26)), seed=1.0, along="x", gloss=0.55, spec=0.35,
                 floor_z=0.0, dust=0.3, grime=0.4, rings=0.35, knots=0.1, edge_k=0.9, wear=(0.62, 0.70), rub=(),
                 cups=(), decal_items=()):
    """rub - [(centre, semi-axes, strength)]: an ellipsoid, weaker toward the edge; cups - [(x, y, r)]: ring
    traces on faces looking up; wear - the threshold after which the lacquer is worn (lower - more worn)."""
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
    tone = t.maprange(t.noise(vec, 1.6, 3.0, 0.5), 0.3, 0.7, 0.0, 1.0)
    dark = tuple(c * 0.62 for c in color[:3]) + (1,)
    base = t.mixc(tone, tuple(c * 0.88 for c in color[:3]) + (1,), tuple(min(1.0, c * 1.08) for c in color[:3]) + (1,))
    col = t.mixc(t.math("MULTIPLY", ring, 0.8), base, dark)
    col = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", fibers, 0.35), 0.5), col, dark)
    knot = t.step(t.noise(t.stretch(vec, *[0.4 if x < 1 else 1.0 for x in k]), 6.0, 2.0, 0.5),
                  1.0 - 0.06 * knots, 1.0 - 0.03 * knots)
    col = t.mixc(t.math("MULTIPLY", knot, 0.85), col, tuple(c * 0.35 for c in color[:3]) + (1,))
    col = kmats.decals(t, col, sep, nsep, decal_items)
    # lacquer worn: edges, patches from hands; under the lacquer - light dry wood
    edge = t.maprange(t.edge_wear(0.005), 0.05, 0.22, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 9.0, 8.0, 0.7), 0.75), t.math("MULTIPLY", edge, edge_k))
    grain = t.maprange(t.noise(fib, 40.0, 6.0, 0.6), 0.3, 0.7, 0.6, 1.0)
    for c, r, s in rub:
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
        f = t.math("ADD", f, t.math("MULTIPLY", t.math("MULTIPLY", near, grain), s))
    worn = t.step(f, wear[0], wear[1])
    bare = tuple(min(1.0, c * 1.9 + 0.02) for c in color[:3]) + (1,)
    col = t.mixc(t.math("MULTIPLY", worn, 0.75), col, t.mixc(t.math("MULTIPLY", fibers, 0.6), bare, color))
    g_ = t.math("SUBTRACT", gloss, t.math("MULTIPLY", worn, gloss * 0.75))
    s_ = t.math("SUBTRACT", spec, t.math("MULTIPLY", worn, spec * 0.7))
    # rings from a hot mug on the roof: the lacquer turned cloudy with a whitish rim, broken in places
    up = t.maprange(nsep.outputs["Z"], 0.6, 0.9, 0.0, 1.0)
    brk = t.maprange(t.noise(vec, 30.0, 4.0, 0.6), 0.35, 0.6, 0.2, 1.0)
    for cx, cy, r in cups:
        d = t.node("ShaderNodeVectorMath")
        d.operation = "SUBTRACT"
        t.link(pos, d.inputs[0])
        d.inputs[1].default_value = (cx, cy, 0.0)
        m = t.node("ShaderNodeVectorMath")
        m.operation = "MULTIPLY"
        t.link(d.outputs[0], m.inputs[0])
        m.inputs[1].default_value = (1.0, 1.0, 0.0)
        ln = t.node("ShaderNodeVectorMath")
        ln.operation = "LENGTH"
        t.link(m.outputs[0], ln.inputs[0])
        band = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", ln.outputs["Value"], r)), 0.0012, 0.0034, 1.0, 0.0)
        inner = t.maprange(ln.outputs["Value"], r * 0.95, r * 0.6, 0.0, 0.25)
        stain = t.math("MULTIPLY", t.math("MULTIPLY", t.math("MAXIMUM", band, inner), brk), up)
        col = t.mixc(t.math("MULTIPLY", stain, 0.45), col, kmats.lin((150, 128, 108)))
        g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", stain, gloss * 0.5))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.5)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.6))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.5))
    h = t.math("ADD", t.math("MULTIPLY", fibers, 0.25), t.math("MULTIPLY", ring, -0.25))
    h = t.math("SUBTRACT", h, t.math("ADD", t.math("MULTIPLY", knot, 0.3), t.math("MULTIPLY", worn, 0.15)))
    return kmats.out(t, col, g_, s_, h)
