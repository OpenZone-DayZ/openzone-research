"""Procedural materials: the game texture (_co, _smdi, _nohq) is baked from them.

Each builder - build_<kind>(mat, origin, **params) - assembles nodes and returns outputs:
    color  RGBA  diffuse color (linear)
    gloss  float gloss 0..1 (the blue channel of _smdi)
    spec   float highlight strength 0..1 (the green channel of _smdi)
    height float relief height (Bump -> _nohq)
An output is a pair (node name, output index): the baking passes (wire) rebuild the material
output several times, and sockets do not survive a rebuild of the tree. Hence the Tree wrapper.

The pattern is defined in the coordinates of the empty `origin` (the model origin), so parts
match by pattern. Dust settles on up-facing surfaces, grime goes toward the floor and into
corners, chips go onto sharp edges.
"""
import os

import bpy


class Tree:
    def __init__(self, mat):
        mat.use_nodes = True
        self.nt = mat.node_tree
        self.nt.nodes.clear()

    def node(self, kind, loc=(0, 0), **inputs):
        n = self.nt.nodes.new(kind)
        n.location = loc
        for k, v in inputs.items():
            n.inputs[k].default_value = v
        return n

    def link(self, a, b):
        self.nt.links.new(a, b)

    def math(self, op, a, b=None, c=None):
        m = self.node("ShaderNodeMath")
        m.operation = op
        for i, x in enumerate((a, b, c)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                m.inputs[i].default_value = x
            else:
                self.link(x, m.inputs[i])
        return m.outputs[0]

    def ramp(self, fac, stops):
        r = self.node("ShaderNodeValToRGB")
        cr = r.color_ramp
        while len(cr.elements) < len(stops):
            cr.elements.new(0.5)
        for el, (pos, col) in zip(cr.elements, stops):
            el.position = pos
            el.color = col if isinstance(col, tuple) else (col, col, col, 1)
        self.link(fac, r.inputs["Fac"])
        return r.outputs["Color"]

    def step(self, fac, a, b):
        """0 below a, 1 above b, smooth in between (via a ramp)."""
        return self.bw(self.ramp(fac, [(a, 0.0), (b, 1.0)]))

    def bw(self, col):
        s = self.node("ShaderNodeSeparateColor")
        self.link(col, s.inputs[0])
        return s.outputs[0]

    def maprange(self, val, a, b, c, d):
        m = self.node("ShaderNodeMapRange")
        m.inputs["From Min"].default_value = a
        m.inputs["From Max"].default_value = b
        m.inputs["To Min"].default_value = c
        m.inputs["To Max"].default_value = d
        m.clamp = True
        self.link(val, m.inputs["Value"])
        return m.outputs["Result"]

    def mixc(self, fac, a, b):
        m = self.node("ShaderNodeMix")
        m.data_type = "RGBA"
        if isinstance(fac, (int, float)):
            m.inputs["Factor"].default_value = fac
        else:
            self.link(fac, m.inputs["Factor"])
        for sock, v in ((m.inputs[6], a), (m.inputs[7], b)):
            if isinstance(v, tuple):
                sock.default_value = v
            else:
                self.link(v, sock)
        return m.outputs[2]

    def mixf(self, fac, a, b):
        m = self.node("ShaderNodeMix")
        m.data_type = "FLOAT"
        if isinstance(fac, (int, float)):
            m.inputs["Factor"].default_value = fac
        else:
            self.link(fac, m.inputs["Factor"])
        for sock, v in ((m.inputs[2], a), (m.inputs[3], b)):
            if isinstance(v, (int, float)):
                sock.default_value = v
            else:
                self.link(v, sock)
        return m.outputs[0]

    def coords(self, origin, seed):
        tc = self.node("ShaderNodeTexCoord")
        tc.object = origin
        shift = self.node("ShaderNodeVectorMath")
        shift.inputs[1].default_value = (seed * 3.1, seed * 1.7, seed * 0.9)
        self.link(tc.outputs["Object"], shift.inputs[0])
        sep = self.node("ShaderNodeSeparateXYZ")
        self.link(tc.outputs["Object"], sep.inputs[0])
        return shift.outputs[0], sep

    def stretch(self, vec, sx, sy, sz):
        v = self.node("ShaderNodeVectorMath")
        v.operation = "MULTIPLY"
        v.inputs[1].default_value = (sx, sy, sz)
        self.link(vec, v.inputs[0])
        return v.outputs[0]

    def noise(self, vec, scale, detail=8.0, rough=0.6):
        n = self.node("ShaderNodeTexNoise", Scale=scale, Detail=detail, Roughness=rough)
        self.link(vec, n.inputs["Vector"])
        return n.outputs["Fac"]

    def normal(self):
        g = self.node("ShaderNodeNewGeometry")
        s = self.node("ShaderNodeSeparateXYZ")
        self.link(g.outputs["True Normal"], s.inputs[0])
        return s

    def facing(self, nsep, axis, sign, thr=0.7):
        comp = nsep.outputs["XYZ".index(axis)]
        return self.math("GREATER_THAN", self.math("MULTIPLY", comp, float(sign)), thr)

    def edge_wear(self, radius=0.004):
        """0 on flat surfaces, toward 1 on sharp edges (Bevel against the true normal)."""
        bev = self.node("ShaderNodeBevel")
        bev.samples = 8
        bev.inputs["Radius"].default_value = radius
        g = self.node("ShaderNodeNewGeometry")
        dot = self.node("ShaderNodeVectorMath")
        dot.operation = "DOT_PRODUCT"
        self.link(bev.outputs["Normal"], dot.inputs[0])
        self.link(g.outputs["True Normal"], dot.inputs[1])
        return self.math("SUBTRACT", 1.0, dot.outputs["Value"])

    def cavity(self, distance=0.03):
        ao = self.node("ShaderNodeAmbientOcclusion")
        ao.samples = 16
        ao.inputs["Distance"].default_value = distance
        return self.math("SUBTRACT", 1.0, ao.outputs["AO"])

    def image(self, path, u, v, center, size):
        """An RGBA image on a plane: u, v are the point coordinates, center and size say where the
        image lies in those coordinates. Outside its edges it is transparent."""
        (cu, cv), (w, h) = center, size
        uu = self.math("ADD", self.math("DIVIDE", self.math("SUBTRACT", u, cu), w), 0.5)
        vv = self.math("ADD", self.math("DIVIDE", self.math("SUBTRACT", v, cv), h), 0.5)
        comb = self.node("ShaderNodeCombineXYZ")
        self.link(uu, comb.inputs[0])
        self.link(vv, comb.inputs[1])
        img = self.node("ShaderNodeTexImage")
        img.image = bpy.data.images.load(path, check_existing=True)
        img.image.colorspace_settings.name = "sRGB"
        img.extension = "CLIP"
        img.interpolation = "Cubic"
        self.link(comb.outputs[0], img.inputs["Vector"])
        return img.outputs["Color"], img.outputs["Alpha"]

    @staticmethod
    def ref(sock):
        return (sock.node.name, list(sock.node.outputs).index(sock))


def out(t, color, gloss, spec, height):
    return {k: (Tree.ref(v) if not isinstance(v, (int, float)) else v)
            for k, v in dict(color=color, gloss=gloss, spec=spec, height=height).items()}


def lin(rgb):
    """sRGB 0..255 or 0..1 -> linear RGBA."""
    c = [x / 255.0 if max(rgb) > 1.0 else x for x in rgb]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (c[0], c[1], c[2], 1.0)


RUST = ((0.060, 0.026, 0.012, 1), (0.150, 0.060, 0.022, 1), (0.250, 0.110, 0.040, 1))
DUST = lin((150, 140, 122))
GRIME = lin((52, 46, 38))


# --- look profile ------------------------------------------------------------------------------
# "v1" is the original look (the default: accepted and built models do not change). "dayz" is
# more matte and dirtier, with corner shading (AO) in the color.
# The numbers come from measuring vanilla items of the same kind: vanilla painted metal has
# specular x G of 0.01..0.07, ours was 0.15..0.23.
# Enabled by the generator: kmodel.Model(look="dayz") (or use_look("dayz") before building materials).
LOOKS = {
    "v1": dict(name="v1", rvmat=dict(specular=0.6, power=80.0)),
    "dayz": dict(name="dayz",
                 spec=(0.03, 0.30, 2.0),     # highlight strength in _smdi (G): G' = a + b * G^p
                 gloss=0.85,                 # gloss in _smdi (B): B' = B * k
                 ao=0.6,                     # color *= 1 - ao + ao * AO (corner shading, baked)
                 patina=(0.12, 0.90),        # color: desaturate by a share, multiply the brightness (in weather)
                 steel=0.65,                 # bare steel, chrome, tin - darker (tone x k)
                 rvmat=dict(specular=1.0, power=80.0),
                 dust_k=1.8, cav_k=1.5,      # dust on top and grime in corners - stronger
                 mottle=0.20,                # blotchy tone: sun-faded, worn, greasy
                 streaks=0.50,               # grime streaks on vertical faces
                 smudge=0.35,                # greasy stains from hands and parts
                 scratches=0.25,             # fine scratches in two directions
                 micro=0.10),                # fine relief (pitting, grain) in _nohq
}
LOOK = LOOKS["v1"]


def use_look(name):
    """The look profile for all following materials, baking and previews."""
    global LOOK
    LOOK = LOOKS[name]
    return LOOK


def spec_out(g):
    """Highlight strength for _smdi (G) by profile: number -> number (a numpy array works too)."""
    if LOOK["name"] != "dayz":
        return g
    a, b, p = LOOK["spec"]
    return a + b * g ** p


def dayz_layers(t, col, g, vec, sep, nsep, grime):
    """Layers of the "dayz" profile on top of weather(): a subdued color (patina), tone blotches,
    streaks, greasy stains, scratches."""
    k = LOOK
    d, v = k["patina"]
    gray = t.node("ShaderNodeRGBToBW")
    t.link(col, gray.inputs[0])
    col = t.mixc(d, col, gray.outputs[0])
    col = t.mixc(1.0 - v, col, (0, 0, 0, 1))
    n1 = t.maprange(t.noise(vec, 1.7, 5.0, 0.6), 0.3, 0.7, 0.0, 1.0)
    col = t.mixc(n1, t.mixc(k["mottle"], col, (0, 0, 0, 1)), t.mixc(k["mottle"] * 0.4, col, (1, 1, 1, 1)))
    vert = t.maprange(t.math("ABSOLUTE", nsep.outputs["Z"]), 0.35, 0.6, 1.0, 0.0)
    st = t.step(t.noise(t.stretch(vec, 1.0, 1.0, 0.07), 16.0, 6.0, 0.6), 0.60, 0.70)
    st = t.math("MULTIPLY", t.math("MULTIPLY", st, vert), k["streaks"] * min(1.0, 0.4 + grime))
    col = t.mixc(st, col, GRIME)
    sm = t.math("MULTIPLY", t.step(t.noise(vec, 3.2, 4.0, 0.5), 0.64, 0.74), k["smudge"])
    col = t.mixc(sm, col, lin((40, 36, 30)))
    s1 = t.step(t.noise(t.stretch(vec, 0.03, 1.0, 1.0), 220.0, 2.0, 0.5), 0.71, 0.725)
    s2 = t.step(t.noise(t.stretch(vec, 1.0, 0.03, 1.0), 220.0, 2.0, 0.5), 0.71, 0.725)
    sc = t.math("MULTIPLY", t.math("MAXIMUM", s1, s2),
                t.maprange(t.noise(vec, 6.0, 4.0, 0.5), 0.4, 0.7, 0.0, k["scratches"]))
    col = t.mixc(sc, col, t.mixc(0.5, col, (0.55, 0.55, 0.55, 1)))
    g = t.math("MAXIMUM", g, t.math("MAXIMUM", st, sm))
    return col, g


# --- shared grime layers ---------------------------------------------------------------------
def weather(t, col, vec, sep, nsep, floor_z=0.0, dust=0.35, grime=0.5, cav=0.5, low_h=0.25):
    """Dust on up-facing surfaces, grime near the floor and in corners. Returns (color, grime
    strength). The "dayz" profile has more dust and corner grime, and adds dayz_layers() on top."""
    if LOOK["name"] == "dayz":
        dust, cav = dust * LOOK["dust_k"], cav * LOOK["cav_k"]
    up = t.maprange(nsep.outputs["Z"], 0.4, 0.9, 0.0, 1.0)
    dn = t.maprange(t.noise(vec, 4.0, 6.0, 0.6), 0.35, 0.7, 0.4, 1.0)
    col = t.mixc(t.math("MULTIPLY", t.math("MULTIPLY", up, dn), dust), col, DUST)
    c = t.maprange(t.cavity(0.04), 0.15, 0.6, 0.0, 1.0)
    low = t.maprange(sep.outputs["Z"], floor_z, floor_z + low_h, 1.0, 0.0)
    g = t.math("MAXIMUM", t.math("MULTIPLY", c, cav), t.math("MULTIPLY", low, grime))
    g = t.math("MULTIPLY", g, t.maprange(t.noise(vec, 7.0, 8.0, 0.6), 0.3, 0.7, 0.5, 1.0))
    col = t.mixc(g, col, GRIME)
    if LOOK["name"] == "dayz":
        col, g = dayz_layers(t, col, g, vec, sep, nsep, grime)
    return col, g


def decals(t, col, sep, nsep, items):
    """Decals: [(RGBA PNG path, normal axis "x"/"y"/"z", sign, (u axis, v axis),
    center (u, v), size (w, h), (min, max) along the third axis or None)]."""
    for path, ax, sign, (au, av), center, size, rng in items:
        gate = t.facing(nsep, ax.upper(), sign, 0.5)
        if rng is not None:
            w = sep.outputs["XYZ".index(ax.upper())]
            gate = t.math("MULTIPLY", gate, t.math("MULTIPLY", t.math("GREATER_THAN", w, rng[0]),
                                                   t.math("LESS_THAN", w, rng[1])))
        c, a = t.image(path, sep.outputs["XYZ".index(au.upper())], sep.outputs["XYZ".index(av.upper())],
                       center, size)
        col = t.mixc(t.math("MULTIPLY", a, gate), col, c)
    return col


# --- builders --------------------------------------------------------------------------------
def build_paint(mat, origin, color, under=(0.05, 0.05, 0.055, 1), seed=1.0, gloss=0.45, spec=0.35,
                chip=(0.60, 0.66), rust=(0.62, 0.70), rust_low=0.5, floor_z=0.0, dust=0.35,
                grime=0.5, yellow=0.0, decal_items=()):
    """Painted metal (enamel, powder coat): blotchy tone, chips along the edges down to the primer,
    rare rust (more near the floor), dust on top, grime at the bottom and in corners, decals."""
    t = Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.93 for c in color[:3]) + (1,), color)
    if yellow > 0:
        base = t.mixc(t.math("MULTIPLY", t.maprange(t.noise(vec, 1.2, 4.0, 0.5), 0.35, 0.7, 0.2, 1.0), yellow),
                      base, lin((206, 190, 150)))
    col = decals(t, base, sep, nsep, decal_items)
    edge = t.maprange(t.edge_wear(0.004), 0.06, 0.25, 0.0, 1.0)
    blot = t.noise(vec, 11.0, 10.0, 0.7)
    chips = t.step(t.math("ADD", t.math("MULTIPLY", blot, 0.75), t.math("MULTIPLY", edge, 0.55)), chip[0], chip[1])
    col = t.mixc(chips, col, under)
    low = t.maprange(sep.outputs["Z"], floor_z + 0.5, floor_z, 0.0, rust_low)
    speck = t.step(t.noise(vec, 24.0, 8.0, 0.7), rust[0], rust[1])
    rust_amt = t.math("MAXIMUM", t.math("MULTIPLY", chips, 0.6), t.math("MULTIPLY", speck, t.math("ADD", 0.25, low)))
    drip = t.step(t.noise(t.stretch(vec, 1.0, 1.0, 0.12), 9.0, 8.0, 0.65), 0.62, 0.72)
    rust_amt = t.math("MAXIMUM", rust_amt, t.math("MULTIPLY", drip, low))
    rust_col = t.ramp(t.noise(vec, 30.0, 6.0, 0.6), [(0.3, RUST[0]), (0.55, RUST[1]), (0.8, RUST[2])])
    col = t.mixc(t.math("MULTIPLY", rust_amt, 0.9), col, rust_col)
    col, dirt = weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g = t.math("SUBTRACT", gloss, t.math("ADD", t.math("MULTIPLY", rust_amt, gloss * 0.8),
                                        t.math("MULTIPLY", dirt, gloss * 0.5)))
    s = t.math("SUBTRACT", spec, t.math("ADD", t.math("MULTIPLY", rust_amt, spec * 0.8),
                                       t.math("MULTIPLY", dirt, spec * 0.4)))
    h = t.math("ADD", t.math("MULTIPLY", chips, -0.4), t.math("MULTIPLY", rust_amt, t.noise(vec, 90.0, 4.0, 0.6)))
    return out(t, col, g, s, h)


def build_steel(mat, origin, seed=2.0, tone=0.30, along="x", gloss=0.55, spec=0.75, floor_z=0.0,
                dust=0.25, grime=0.35, holes=None):
    """Stainless steel: brushing in stripes along `along`, smears, dust; holes = (axes (a, b),
    pitch, radius as a share of the pitch) - perforation (dark holes in a regular grid)."""
    t = Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    if LOOK["name"] == "dayz":
        tone *= LOOK["steel"]
    k = {"x": (0.02, 1.0, 1.0), "y": (1.0, 0.02, 1.0), "z": (1.0, 1.0, 0.02)}[along]
    brush = t.noise(t.stretch(vec, *k), 120.0, 4.0, 0.7)
    smudge = t.noise(vec, 3.5, 6.0, 0.6)
    v = t.math("ADD", tone, t.math("ADD", t.math("MULTIPLY", t.math("SUBTRACT", brush, 0.5), 0.10),
                                   t.math("MULTIPLY", t.math("SUBTRACT", smudge, 0.5), 0.12)))
    comb = t.node("ShaderNodeCombineColor")
    for i in range(3):
        t.link(v, comb.inputs[i])
    col = t.mixc(0.12, comb.outputs[0], (0.30, 0.31, 0.33, 1))
    hole = None
    if holes:
        (aa, ab), pitch, rad = holes
        sa, sb = sep.outputs["XYZ".index(aa.upper())], sep.outputs["XYZ".index(ab.upper())]

        def frac_dist(c, off):
            q = t.math("DIVIDE", t.math("ADD", c, off), pitch)
            return t.math("SUBTRACT", t.math("FRACT", q), 0.5)
        da, db = frac_dist(sa, 0.0), frac_dist(sb, 0.0)
        r2 = t.math("ADD", t.math("MULTIPLY", da, da), t.math("MULTIPLY", db, db))
        hole = t.math("LESS_THAN", r2, rad * rad)
        col = t.mixc(hole, col, (0.006, 0.006, 0.007, 1))
    col, dirt = weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.45)
    g = t.math("SUBTRACT", gloss, t.math("MULTIPLY", t.math("ADD", dirt, t.math("MULTIPLY", smudge, 0.3)), gloss * 0.6))
    s = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.6))
    h = t.math("MULTIPLY", brush, 0.08)
    if hole is not None:
        g = t.mixf(hole, g, 0.0)
        s = t.mixf(hole, s, 0.0)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", hole, 1.0))
    return out(t, col, g, s, h)


def build_plastic(mat, origin, color, seed=3.0, gloss=0.35, spec=0.25, floor_z=0.0, dust=0.3, grime=0.3,
                  mottle=0.06, scuff=(0.62, 0.70)):
    """Plastic / bakelite / rubber: an even color, light blotchiness, lighter scuffs."""
    t = Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    col = t.mixc(t.maprange(t.noise(vec, 6.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                 tuple(c * (1 - mottle) for c in color[:3]) + (1,), tuple(min(1.0, c * (1 + mottle)) for c in color[:3]) + (1,))
    edge = t.maprange(t.edge_wear(0.002), 0.06, 0.25, 0.0, 1.0)
    sc = t.step(t.math("ADD", t.math("MULTIPLY", t.noise(vec, 18.0, 8.0, 0.7), 0.7), t.math("MULTIPLY", edge, 0.6)),
                scuff[0], scuff[1])
    col = t.mixc(t.math("MULTIPLY", sc, 0.35), col, tuple(min(1.0, c * 1.6 + 0.04) for c in color[:3]) + (1,))
    col, dirt = weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.4)
    g = t.math("SUBTRACT", gloss, t.math("MULTIPLY", t.math("ADD", dirt, sc), gloss * 0.5))
    s = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.5))
    return out(t, col, g, s, t.math("MULTIPLY", sc, -0.2))


def build_flat(mat, origin, color, gloss=0.6, spec=0.6, emissive=False):
    """An even color without wear: lamp lenses, indicators, dials under glass."""
    t = Tree(mat)
    vec, sep = t.coords(origin, 5.0)
    col = t.mixc(t.maprange(t.noise(vec, 40.0, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0),
                 tuple(c * 0.9 for c in color[:3]) + (1,), color)
    return out(t, col, gloss, spec, 0.0)


def std_kinds(floor_z=0.0):
    """Kinds that repeat from model to model (the values are those of the accepted m01)."""
    return {
        "steel": ("steel", dict(seed=4.2, tone=0.30, along="x", floor_z=floor_z, dust=0.25, grime=0.3)),
        "grille_h": ("steel", dict(seed=5.0, tone=0.30, along="x", holes=(("x", "y"), 0.008, 0.30), dust=0.4)),
        "grille_v": ("steel", dict(seed=5.5, tone=0.28, along="x", holes=(("x", "z"), 0.010, 0.32), dust=0.2)),
        "black": ("plastic", dict(color=lin((20, 20, 21)), gloss=0.30, spec=0.25, dust=0.25)),
        "rubber": ("plastic", dict(color=lin((24, 24, 24)), gloss=0.10, spec=0.05, dust=0.4, scuff=(0.9, 1.0))),
        "lamp_g": ("flat", dict(color=lin((40, 150, 60)), gloss=0.85, spec=0.8)),
        "lamp_r": ("flat", dict(color=lin((185, 30, 25)), gloss=0.85, spec=0.8)),
        "plastic_white": ("plastic", dict(color=lin((222, 222, 215)), gloss=0.35, spec=0.25)),
        "cap_red": ("plastic", dict(color=lin((170, 34, 28)), gloss=0.4, spec=0.3)),
        "enamel_lab": ("paint", dict(color=lin((196, 199, 196)), under=lin((60, 60, 62)), seed=2.3, gloss=0.40,
                                     spec=0.30, chip=(0.62, 0.68), rust=(0.64, 0.72), rust_low=0.6,
                                     floor_z=floor_z, dust=0.30, grime=0.5)),
        "worktop": ("plastic", dict(color=lin((58, 60, 62)), gloss=0.25, spec=0.2, mottle=0.08, dust=0.35,
                                    scuff=(0.66, 0.72))),
    }


BUILDERS = {
    "paint": build_paint,
    "steel": build_steel,
    "plastic": build_plastic,
    "flat": build_flat,
}


def make(kind_table, kind, mat, origin):
    """kind_table: kind -> (builder, parameters) - the model's material table."""
    builder, params = kind_table[kind]
    fn = BUILDERS[builder] if isinstance(builder, str) else builder
    return fn(mat, origin, **params)


def sock(mat, ref):
    name, idx = ref
    return mat.node_tree.nodes[name].outputs[idx]


def feed(t, mat, ref, dst):
    if isinstance(ref, (int, float)):
        dst.default_value = ref
    else:
        t.link(sock(mat, ref), dst)


def wire(mat, outs, mode, target_image=None, glow=0.0):
    """Rebuild the material output for a pass: cover / color / smdi (EMIT), normal (Principled
    with relief), preview (a preview without baking: highlight and gloss as they will come out in
    _smdi and rvmat for the look profile; glow > 0 - the part glows, the "working" look)."""
    nt = mat.node_tree
    for n in [n for n in nt.nodes if n.get("oz_wire")]:
        nt.nodes.remove(n)
    t = Tree.__new__(Tree)
    t.nt = nt

    def tag(n):
        n["oz_wire"] = 1
        return n
    out_n = tag(t.node("ShaderNodeOutputMaterial", (1800, 0)))
    if mode in ("preview", "normal"):
        bsdf = tag(t.node("ShaderNodeBsdfPrincipled", (1400, 0)))
        feed(t, mat, outs["color"], bsdf.inputs["Base Color"])
        dayz = LOOK["name"] == "dayz"
        rough = tag(t.node("ShaderNodeMath", (1200, -200)))
        rough.operation = "MULTIPLY_ADD"
        rough.inputs[1].default_value = -(LOOK["gloss"] if dayz else 1.0)
        rough.inputs[2].default_value = 1.0
        feed(t, mat, outs["gloss"], rough.inputs[0])
        t.link(rough.outputs[0], bsdf.inputs["Roughness"])
        if mode == "preview":
            # the game highlight = rvmat specular[] x the G of _smdi; in Principled, 0.5 is an ordinary dielectric (4 %)
            k = LOOK["rvmat"]["specular"] * 2.5
            sp = tag(t.node("ShaderNodeMath", (1000, -100)))
            if dayz:
                a, b, p = LOOK["spec"]
                sp.operation = "POWER"
                feed(t, mat, outs["spec"], sp.inputs[0])
                sp.inputs[1].default_value = p
                sp2 = tag(t.node("ShaderNodeMath", (1100, -100)))
                sp2.operation = "MULTIPLY_ADD"
                t.link(sp.outputs[0], sp2.inputs[0])
                sp2.inputs[1].default_value = b * k
                sp2.inputs[2].default_value = a * k
                sp = sp2
            else:
                sp.operation = "MULTIPLY"
                feed(t, mat, outs["spec"], sp.inputs[0])
                sp.inputs[1].default_value = k
            sp.use_clamp = True
            t.link(sp.outputs[0], bsdf.inputs["Specular IOR Level"])
            if glow > 0:
                feed(t, mat, outs["color"], bsdf.inputs["Emission Color"])
                bsdf.inputs["Emission Strength"].default_value = glow
        bump = tag(t.node("ShaderNodeBump", (1200, -400), Strength=0.45, Distance=0.0015))
        feed(t, mat, outs["height"], bump.inputs["Height"])
        if dayz and LOOK.get("micro", 0) > 0:
            # fine relief over the whole surface: casting pitting, paint grain
            tc = tag(t.node("ShaderNodeTexCoord", (600, -600)))
            nz = tag(t.node("ShaderNodeTexNoise", (800, -600), Scale=900.0, Detail=2.0, Roughness=0.5))
            t.link(tc.outputs["Object"], nz.inputs["Vector"])
            mb = tag(t.node("ShaderNodeBump", (1000, -600), Strength=LOOK["micro"], Distance=0.0004))
            t.link(nz.outputs["Fac"], mb.inputs["Height"])
            t.link(mb.outputs["Normal"], bump.inputs["Normal"])
        t.link(bump.outputs["Normal"], bsdf.inputs["Normal"])
        t.link(bsdf.outputs[0], out_n.inputs["Surface"])
    else:
        em = tag(t.node("ShaderNodeEmission", (1400, 0)))
        if mode == "cover":
            em.inputs["Color"].default_value = (1, 1, 1, 1)
        elif mode == "color":
            feed(t, mat, outs["color"], em.inputs["Color"])
        elif mode == "smdi":
            comb = tag(t.node("ShaderNodeCombineXYZ", (1200, 0)))
            feed(t, mat, outs["spec"], comb.inputs[0])
            feed(t, mat, outs["gloss"], comb.inputs[1])
            t.link(comb.outputs[0], em.inputs["Color"])
        t.link(em.outputs[0], out_n.inputs["Surface"])
    if target_image is not None:
        img = tag(t.node("ShaderNodeTexImage", (1800, 400)))
        img.image = target_image
        nt.nodes.active = img
