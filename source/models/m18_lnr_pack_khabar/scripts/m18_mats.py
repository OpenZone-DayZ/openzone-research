"""M18 safe materials ("dayz" look): builders in the style of kmats, with what the kit does not have.
The existing kit files are left unchanged, so everything of its own is here.

- enamel - enamel on metal (like kmats.build_paint): chips along the edges down to the primer, deep
  ones down to metal; clean - rectangles on the roof where something usually stands (an empty module
  slot): no dust or dirt there, the paint is fresher;
- brass - brass and bronze: dark patina in recesses and patches, edges and ridges rubbed bright by hands
  (without it bronze looks flat, as if painted);
- leather - pad leather: tone creases and patches, light scuffs, stitching as a decal;
- plastic, steel, wood - as in the kit, but with a pattern scale `scale`.

scale: the dirt layers of the "dayz" look (tone patches, grease patches, streaks, scratches) are tuned
for machines of 1-2 m; on an 8 cm mug one patch would cover everything. For small things on the roof the
pattern is `scale` times finer (like SMALL in M62), the patches and streaks are proportional to the item.
"""
import contextlib

import kmats
import kwood

lin = kmats.lin


def coords(t, origin, seed, scale=1.0):
    vec, sep = t.coords(origin, seed)
    if scale != 1.0:
        vec = t.stretch(vec, scale, scale, scale)
    return vec, sep


@contextlib.contextmanager
def look_tweak(**kw):
    """While a material is built, other strengths of the "dayz" look layers (as in M62); the kit is unchanged."""
    look = kmats.LOOK
    if look["name"] != "dayz" or not kw:
        yield
        return
    old = {k: look[k] for k in kw}
    look.update(kw)
    try:
        yield
    finally:
        look.update(old)


def rect_mask(t, sep, rects, soft=0.006):
    """1 inside the rectangles (x0, x1, y0, y1) in plan, smooth toward the edge (soft)."""
    out = 0.0
    for x0, x1, y0, y1 in rects:
        m = 1.0
        for i, (a, b) in enumerate(((x0, x1), (y0, y1))):
            w = sep.outputs[i]
            e = t.math("MULTIPLY", t.maprange(w, a - soft, a + soft, 0.0, 1.0), t.maprange(w, b + soft, b - soft, 0.0, 1.0))
            m = e if isinstance(m, float) else t.math("MULTIPLY", m, e)
        out = m if isinstance(out, float) else t.math("MAXIMUM", out, m)
    return out


def enamel(mat, origin, color, under=lin((86, 44, 28)), bare=lin((92, 90, 86)), seed=1.0, gloss=0.40, spec=0.30,
           chip=(0.56, 0.62), metal=0.6, rust=(0.60, 0.68), rust_low=0.8, floor_z=0.0, dust=0.4, grime=0.7,
           decal_items=(), clean=(), scale=1.0, low_h=0.25):
    """Enamel on metal: mottled tone, decals, chips along the edges down to the primer `under`, the middle of
    a chip down to bare metal (the fraction `metal`), rust in the chips and at the floor, dust on top, dirt
    at the bottom and in corners (kmats.weather); clean - [(x0, x1, y0, y1)] on faces looking up: something
    stands there."""
    t = kmats.Tree(mat)
    vec, sep = coords(t, origin, seed, scale)
    nsep = t.normal()
    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.92 for c in color[:3]) + (1,), color)
    col = kmats.decals(t, base, sep, nsep, decal_items)
    edge = t.maprange(t.edge_wear(0.004), 0.06, 0.25, 0.0, 1.0)
    blot = t.noise(vec, 11.0, 10.0, 0.7)
    f = t.math("ADD", t.math("MULTIPLY", blot, 0.75), t.math("MULTIPLY", edge, 0.55))
    chips = t.step(f, chip[0], chip[1])
    deep = t.math("MULTIPLY", t.step(f, chip[1] + 0.04, chip[1] + 0.08), metal)
    col = t.mixc(chips, col, under)
    col = t.mixc(deep, col, bare)
    low = t.maprange(sep.outputs["Z"], floor_z + 0.5, floor_z, 0.0, rust_low)
    speck = t.step(t.noise(vec, 24.0, 8.0, 0.7), rust[0], rust[1])
    rust_amt = t.math("MAXIMUM", t.math("MULTIPLY", deep, 0.7), t.math("MULTIPLY", speck, t.math("ADD", 0.25, low)))
    rust_amt = t.math("MAXIMUM", rust_amt, t.math("MULTIPLY", chips, t.math("MULTIPLY", low, 0.8)))
    drip = t.step(t.noise(t.stretch(vec, 1.0, 1.0, 0.12), 9.0, 8.0, 0.65), 0.62, 0.72)
    rust_amt = t.math("MAXIMUM", rust_amt, t.math("MULTIPLY", drip, low))
    rust_col = t.ramp(t.noise(vec, 30.0, 6.0, 0.6), [(0.3, kmats.RUST[0]), (0.55, kmats.RUST[1]), (0.8, kmats.RUST[2])])
    col = t.mixc(t.math("MULTIPLY", rust_amt, 0.85), col, rust_col)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.5, low_h)
    if clean:
        # not bare paint, but less dust: dust does not collect under a box, while the roof around it is the same
        up = t.maprange(nsep.outputs["Z"], 0.5, 0.9, 0.0, 1.0)
        spot = t.math("MULTIPLY", rect_mask(t, sep, clean, soft=0.012), up)
        fresh = tuple(c * 0.90 * 0.78 + d * 0.22 for c, d in zip(color[:3], kmats.DUST[:3])) + (1,)
        col = t.mixc(t.math("MULTIPLY", spot, 0.75), col, fresh)
        dirt = t.math("MULTIPLY", dirt, t.math("SUBTRACT", 1.0, spot))
    bare_k = t.math("SUBTRACT", deep, t.math("MULTIPLY", rust_amt, 0.7))
    g_ = t.math("ADD", gloss, t.math("MULTIPLY", bare_k, 0.15))
    g_ = t.math("SUBTRACT", g_, t.math("ADD", t.math("MULTIPLY", rust_amt, gloss * 0.8), t.math("MULTIPLY", dirt, gloss * 0.5)))
    s_ = t.math("ADD", spec, t.math("MULTIPLY", bare_k, 0.25))
    s_ = t.math("SUBTRACT", s_, t.math("ADD", t.math("MULTIPLY", rust_amt, spec * 0.8), t.math("MULTIPLY", dirt, spec * 0.4)))
    h = t.math("ADD", t.math("MULTIPLY", chips, -0.4), t.math("MULTIPLY", rust_amt, t.noise(vec, 90.0, 4.0, 0.6)))
    return kmats.out(t, col, g_, s_, h)


def brass(mat, origin, color, seed=3.0, gloss=0.55, spec=0.60, polish=0.7, tarnish=0.5, floor_z=0.0, dust=0.15,
          grime=0.4, decal_items=(), scale=1.0, low_h=0.25):
    """Brass, bronze: patchy tone, patina (dark, in recesses and patches - tarnish), rubbed bright on edges
    and ridges (polish), dust and dirt of small things."""
    t = kmats.Tree(mat)
    vec, sep = coords(t, origin, seed, scale)
    nsep = t.normal()
    base = t.mixc(t.maprange(t.noise(vec, 3.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                  tuple(c * 0.80 for c in color[:3]) + (1,), color)
    col = kmats.decals(t, base, sep, nsep, decal_items)
    cav = t.maprange(t.cavity(0.012), 0.08, 0.40, 0.0, 1.0)
    spots = t.maprange(t.noise(vec, 9.0, 6.0, 0.6), 0.48, 0.74, 0.0, tarnish)
    tar = t.math("MINIMUM", t.math("ADD", t.math("MULTIPLY", cav, 0.9), spots), 1.0)
    col = t.mixc(t.math("MULTIPLY", tar, 0.8), col, lin((44, 34, 18)))
    # rubbed only on protruding edges (a thin rim is all "edge" by edge_wear, the threshold is higher)
    edge = t.maprange(t.edge_wear(0.003), 0.12, 0.32, 0.0, 1.0)
    rub = t.maprange(t.noise(vec, 5.0, 4.0, 0.5), 0.40, 0.70, 0.2, 1.0)
    pol = t.math("MULTIPLY", t.math("MULTIPLY", edge, rub), polish)
    col = t.mixc(pol, col, tuple(min(1.0, c * 1.65 + 0.015) for c in color[:3]) + (1,))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.4, low_h)
    g_ = t.math("ADD", gloss, t.math("MULTIPLY", pol, 0.25))
    g_ = t.math("SUBTRACT", g_, t.math("ADD", t.math("MULTIPLY", tar, gloss * 0.5), t.math("MULTIPLY", dirt, gloss * 0.5)))
    s_ = t.math("ADD", spec, t.math("MULTIPLY", pol, 0.25))
    s_ = t.math("SUBTRACT", s_, t.math("ADD", t.math("MULTIPLY", tar, spec * 0.6), t.math("MULTIPLY", dirt, spec * 0.4)))
    h = t.math("SUBTRACT", t.math("MULTIPLY", t.noise(vec, 60.0, 4.0, 0.6), 0.05), t.math("MULTIPLY", tar, 0.05))
    return kmats.out(t, col, g_, s_, h)


def plastic(mat, origin, color, seed=3.0, gloss=0.35, spec=0.25, floor_z=0.0, dust=0.3, grime=0.3, mottle=0.06,
            scuff=(0.62, 0.70), scale=1.0, low_h=0.25):
    """kmats.build_plastic with a pattern scale `scale`."""
    t = kmats.Tree(mat)
    vec, sep = coords(t, origin, seed, scale)
    nsep = t.normal()
    col = t.mixc(t.maprange(t.noise(vec, 6.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                 tuple(c * (1 - mottle) for c in color[:3]) + (1,), tuple(min(1.0, c * (1 + mottle)) for c in color[:3]) + (1,))
    edge = t.maprange(t.edge_wear(0.002), 0.06, 0.25, 0.0, 1.0)
    sc = t.step(t.math("ADD", t.math("MULTIPLY", t.noise(vec, 18.0, 8.0, 0.7), 0.7), t.math("MULTIPLY", edge, 0.6)),
                scuff[0], scuff[1])
    col = t.mixc(t.math("MULTIPLY", sc, 0.35), col, tuple(min(1.0, c * 1.6 + 0.04) for c in color[:3]) + (1,))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.4, low_h)
    g_ = t.math("SUBTRACT", gloss, t.math("MULTIPLY", t.math("ADD", dirt, sc), gloss * 0.5))
    s_ = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.5))
    return kmats.out(t, col, g_, s_, t.math("MULTIPLY", sc, -0.2))


def steel(mat, origin, seed=2.0, tone=0.30, along="x", gloss=0.55, spec=0.75, floor_z=0.0, dust=0.25, grime=0.35,
          scale=1.0, low_h=0.25):
    """kmats.build_steel (without perforation) with a pattern scale `scale`."""
    t = kmats.Tree(mat)
    vec, sep = coords(t, origin, seed, scale)
    nsep = t.normal()
    if kmats.LOOK["name"] == "dayz":
        tone *= kmats.LOOK["steel"]
    k = {"x": (0.02, 1.0, 1.0), "y": (1.0, 0.02, 1.0), "z": (1.0, 1.0, 0.02)}[along]
    brush = t.noise(t.stretch(vec, *k), 120.0, 4.0, 0.7)
    smudge = t.noise(vec, 3.5, 6.0, 0.6)
    v = t.math("ADD", tone, t.math("ADD", t.math("MULTIPLY", t.math("SUBTRACT", brush, 0.5), 0.10),
                                   t.math("MULTIPLY", t.math("SUBTRACT", smudge, 0.5), 0.12)))
    comb = t.node("ShaderNodeCombineColor")
    for i in range(3):
        t.link(v, comb.inputs[i])
    col = t.mixc(0.12, comb.outputs[0], (0.30, 0.31, 0.33, 1))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.45, low_h)
    g_ = t.math("SUBTRACT", gloss, t.math("MULTIPLY", t.math("ADD", dirt, t.math("MULTIPLY", smudge, 0.3)), gloss * 0.6))
    s_ = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.6))
    return kmats.out(t, col, g_, s_, t.math("MULTIPLY", brush, 0.08))


def leather(mat, origin, color, seed=4.0, gloss=0.30, spec=0.15, floor_z=0.0, dust=0.15, grime=0.4, decal_items=(),
            scale=1.0, low_h=0.25):
    """Leather: patchy tone, dark creases, fine grain in the relief, edges and middle scuffed lighter,
    decals (stitching, the loupe trace)."""
    t = kmats.Tree(mat)
    vec, sep = coords(t, origin, seed, scale)
    nsep = t.normal()
    col = t.mixc(t.maprange(t.noise(vec, 4.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                 tuple(c * 0.78 for c in color[:3]) + (1,), tuple(min(1.0, c * 1.12) for c in color[:3]) + (1,))
    crease = t.step(t.noise(t.stretch(vec, 1.0, 0.15, 1.0), 14.0, 4.0, 0.6), 0.62, 0.66)
    col = t.mixc(t.math("MULTIPLY", crease, 0.5), col, tuple(c * 0.45 for c in color[:3]) + (1,))
    edge = t.maprange(t.edge_wear(0.002), 0.06, 0.25, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.5), col, tuple(min(1.0, c * 1.7 + 0.03) for c in color[:3]) + (1,))
    col = kmats.decals(t, col, sep, nsep, decal_items)
    with look_tweak(scratches=0.08, streaks=0.1):
        col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.4, low_h)
    grain = t.noise(vec, 400.0, 2.0, 0.5)
    g_ = t.math("SUBTRACT", gloss, t.math("ADD", t.math("MULTIPLY", dirt, gloss * 0.5), t.math("MULTIPLY", crease, 0.1)))
    s_ = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.5))
    h = t.math("SUBTRACT", t.math("MULTIPLY", grain, 0.12), t.math("MULTIPLY", crease, 0.2))
    return kmats.out(t, col, g_, s_, h)


def wood(mat, origin, **kw):
    """kwood.build_wood on a small board: the "dayz" layers are
    weaker - otherwise one patch covers the whole board."""
    with look_tweak(smudge=0.12, streaks=0.15, mottle=0.10, scratches=0.15):
        return kwood.build_wood(mat, origin, **kw)
