"""Procedural wood: plank, beam, plywood crate (the "wood" material kind for kmats).

A separate module rather than a builder inside kmats. kmats.make accepts a builder function
instead of a name, so a model's kind table can use it:

    "board": (kwood.build_wood, dict(color=kmats.lin((168, 128, 84)), along="x"))

The builder returns the same outputs as kmats (color, gloss, spec, height). Pattern: fibers
along `along` (noise squeezed across), annual rings (distorted wave), rare knots, a per-plank
tone variation; edges are lighter (worn wood), dust on top and grime near the floor come from
the shared kmats.weather.
"""
import kmats


def build_wood(mat, origin, color=kmats.lin((160, 120, 78)), seed=1.0, along="x", gloss=0.18, spec=0.10,
               floor_z=0.0, dust=0.3, grime=0.4, rings=0.45, knots=0.5, decal_items=()):
    """color - mean wood tone (linear RGBA), along - fiber axis ("x" / "y" / "z"),
    rings - strength of the annual rings 0..1, knots - amount of knots 0..1."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    # The pattern is stretched along the fibers: the coordinate along the axis is squeezed 25 times.
    k = {"x": (0.04, 1.0, 1.0), "y": (1.0, 0.04, 1.0), "z": (1.0, 1.0, 0.04)}[along]
    fib = t.stretch(vec, *k)
    fibers = t.noise(fib, 160.0, 4.0, 0.7)
    wave = t.node("ShaderNodeTexWave", Scale=9.0, Distortion=6.0, **{"Detail": 3.0, "Detail Scale": 1.5})
    wave.wave_type = "RINGS"
    t.link(fib, wave.inputs["Vector"])
    ring = t.math("MULTIPLY", wave.outputs["Fac"], rings)
    tone = t.maprange(t.noise(vec, 1.6, 3.0, 0.5), 0.3, 0.7, 0.0, 1.0)
    dark = tuple(c * 0.62 for c in color[:3]) + (1,)
    light = tuple(min(1.0, c * 1.25) for c in color[:3]) + (1,)
    base = t.mixc(tone, tuple(c * 0.88 for c in color[:3]) + (1,), tuple(min(1.0, c * 1.08) for c in color[:3]) + (1,))
    col = t.mixc(t.math("MULTIPLY", ring, 0.8), base, dark)
    col = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", fibers, 0.35), 0.5), col, dark)
    # Knots: rare dark spots elongated along the fibers.
    knot = t.step(t.noise(t.stretch(vec, *[0.4 if x < 1 else 1.0 for x in k]), 6.0, 2.0, 0.5),
                  1.0 - 0.06 * knots, 1.0 - 0.03 * knots)
    col = t.mixc(t.math("MULTIPLY", knot, 0.85), col, tuple(c * 0.35 for c in color[:3]) + (1,))
    col = kmats.decals(t, col, sep, nsep, decal_items)
    # Worn edges are lighter.
    edge = t.maprange(t.edge_wear(0.004), 0.06, 0.25, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.45), col, light)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.5)
    g = t.math("SUBTRACT", gloss, t.math("MULTIPLY", dirt, gloss * 0.6))
    s = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.5))
    h = t.math("ADD", t.math("MULTIPLY", fibers, 0.25), t.math("MULTIPLY", ring, -0.25))
    h = t.math("SUBTRACT", h, t.math("MULTIPLY", knot, 0.3))
    return kmats.out(t, col, g, s, h)
