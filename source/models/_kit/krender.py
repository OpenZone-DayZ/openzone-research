"""Blender previews: the form in grey and the in-game look with baked textures (atlas + glass _ca).
The preview with the game textures is the oracle for TEXTURE defects: what is visible here sits in
the bake or the unwrap, not in the engine lighting."""
import math
import os

import bpy
from mathutils import Vector


def clear_scene():
    for ob in list(bpy.context.scene.objects):
        bpy.data.objects.remove(ob)


def setup(samples=48, ground=(0.13, 0.13, 0.13)):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    # OZ_CPU_THREADS=N - use at most N CPU threads (see kbake.limit_threads)
    n = int(os.environ.get("OZ_CPU_THREADS", "0") or 0)
    if n > 0:
        sc.render.threads_mode = "FIXED"
        sc.render.threads = n
    sc.cycles.use_denoising = True
    # The OIDN denoiser runs on the GPU: on the CPU it took 7 of the 8 s of a frame on an RTX 4090 and
    # half of a frame on a GTX 1660; the image is the same (m86: a mean difference of 0.15 out of 255,
    # no pixel above 8).
    if hasattr(sc.cycles, "denoising_use_gpu"):
        sc.cycles.denoising_use_gpu = True
    sc.world = bpy.data.worlds.new("w")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.35, 0.37, 0.4, 1)
    bg.inputs["Strength"].default_value = 0.6
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.5
    sun.data.angle = math.radians(6)
    sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
    sc.collection.objects.link(sun)
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -0.0005))
    g = bpy.data.materials.new("ground")
    g.use_nodes = True
    g.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = ground + (1,)
    bpy.context.object.data.materials.append(g)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    return cam


def shoot(cam, path, loc, target, lens=40, res=(1600, 900), ortho=None):
    sc = bpy.context.scene
    cam.location = loc
    cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if ortho:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = ortho
    else:
        cam.data.type = "PERSP"
        cam.data.lens = lens
    sc.render.resolution_x, sc.render.resolution_y = res
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def grey():
    m = bpy.data.materials.new("grey")
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.6, 0.6, 0.6, 1)
    return m


def glass_grey():
    m = bpy.data.materials.new("glass_grey")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.5, 0.6, 0.6, 1)
    b.inputs["Alpha"].default_value = 0.15
    return m


def game_material(tex_dir, name, co=None):
    """One material per atlas: _co, _nohq (DirectX -> Blender: the green channel is inverted), _smdi.
    co - another _co (a machine look); the relief and gloss are the same."""
    m = bpy.data.materials.new("game")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]

    def img(fn, cs):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(os.path.join(tex_dir, fn))
        n.image.colorspace_settings.name = cs
        return n
    co = img(co or (name + "_co.png"), "sRGB")
    nt.links.new(co.outputs["Color"], b.inputs["Base Color"])
    sm = img(name + "_smdi.png", "Non-Color")
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(sm.outputs["Color"], sep.inputs[0])
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "SUBTRACT"
    inv.inputs[0].default_value = 1.0
    nt.links.new(sep.outputs["Blue"], inv.inputs[1])
    nt.links.new(inv.outputs[0], b.inputs["Roughness"])
    nm = img(name + "_nohq.png", "Non-Color")
    sepn = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(nm.outputs["Color"], sepn.inputs[0])
    g = nt.nodes.new("ShaderNodeMath")
    g.operation = "SUBTRACT"
    g.inputs[0].default_value = 1.0
    nt.links.new(sepn.outputs["Green"], g.inputs[1])
    comb = nt.nodes.new("ShaderNodeCombineColor")
    nt.links.new(sepn.outputs["Red"], comb.inputs[0])
    nt.links.new(g.outputs[0], comb.inputs[1])
    nt.links.new(sepn.outputs["Blue"], comb.inputs[2])
    nmap = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(comb.outputs[0], nmap.inputs["Color"])
    nt.links.new(nmap.outputs["Normal"], b.inputs["Normal"])
    return m


def game_glass(path_png):
    m = bpy.data.materials.new("game_glass")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(path_png)
    nt.links.new(n.outputs["Color"], b.inputs["Base Color"])
    nt.links.new(n.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = 0.05
    return m


def place(parts, tag, offset, mats, sharp_deg=40.0, move=None):
    """mats: section -> material (a section without one is grey, like the form atlas). move - group ->
    offset (a machine look in another pose: the head lowered)."""
    obs = []
    for p in parts:
        me = bpy.data.meshes.new("%s_%s" % (tag, p.name))
        p.bm.to_mesh(me)
        me.shade_smooth()
        me.set_sharp_from_angle(angle=math.radians(sharp_deg))
        me.materials.append(mats.get(p.section) or mats["atlas"])
        ob = bpy.data.objects.new(me.name, me)
        d = (move or {}).get(p.group, (0.0, 0.0, 0.0))
        ob.location = tuple(o + c for o, c in zip(offset, d))
        bpy.context.scene.collection.objects.link(ob)
        obs.append(ob)
    return obs


# --- preview without baking ----------------------------------------------------------------------
def place_look(parts, kind_table, origin, remap=None, glow=1.5, sharp_deg=40.0, panels=None, move=None):
    """The near LOD with procedural materials right in the render, without baking: each region gets
    its material from the kind table (kbake.get_mat), wired as "preview" (highlight and gloss as
    they will come out in the game for the kind's profile). remap - the "working" look: the
    replaced kinds glow (glow). Glass is grey and transparent; parts with their own texture (a
    screen) take a material from panels: section -> material."""
    import kbake
    import kmats
    lit = set((remap or {}).values())
    glass = glass_grey()
    obs = []
    for p in parts:
        me = bpy.data.meshes.new("look_" + p.name)
        if p.section == "atlas":
            for f in p.bm.faces:
                f.material_index = f[p.reg]
        p.bm.to_mesh(me)
        me.shade_smooth()
        me.set_sharp_from_angle(angle=math.radians(sharp_deg))
        if p.section == "atlas":
            for r in p.regions:
                kind = (remap or {}).get(r[1], r[1])
                m, outs = kbake.get_mat(kind_table, kind, origin)
                kmats.wire(m, outs, "preview", glow=glow if kind in lit else 0.0)
                me.materials.append(m)
        else:
            me.materials.append((panels or {}).get(p.section, glass))
        ob = bpy.data.objects.new(me.name, me)
        ob.location = (move or {}).get(p.group, (0.0, 0.0, 0.0))
        bpy.context.scene.collection.objects.link(ob)
        obs.append(ob)
    return obs


def panel_material(png, glow=0.0, gloss=0.75):
    """A part with its own texture (a screen): the picture over UV 0..1, with the glow (the "working" look)."""
    m = bpy.data.materials.new("panel_" + os.path.basename(png))
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(png, check_existing=True)
    nt.links.new(n.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 1.0 - gloss
    if glow > 0:
        nt.links.new(n.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = glow
    return m


def our_model(obj, name, origin):
    """Our finished model (a module in a machine slot) in the preview: the near LOD of its MLOD
    from build/model-root (p3d -> Blender: the inverse of kexport.conv) with its baked textures
    (assets/<obj>/work/game_textures). The slot proxy places the module the same way: the model
    origin at the proxy point, without rotation. None - no model or textures."""
    import p3d
    repo = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    fn = os.path.join(repo, "build", "model-root", "OpenZone_ResearchModels", obj, name + ".p3d")
    tex = os.path.join(repo, "assets", obj, "work", "game_textures")
    if not (os.path.exists(fn) and os.path.exists(os.path.join(tex, name + "_co.png"))):
        print("our_model: no MLOD or textures for", obj)
        return None
    _, lods = p3d.read(fn)
    l0 = lods[0]
    verts = [(-p[0] + origin[0], -p[2] + origin[1], p[1] + origin[2]) for p in l0.points]
    # Faces without a texture are the triangles of vanilla item proxies inside the module (1-2 m each,
    # invisible in the game): drawn, they hung as grey "sails" over the machines in previews and tex_ renders.
    faces = [f for f in l0.faces if f.texture]
    me = bpy.data.meshes.new("module_" + name)
    me.from_pydata(verts, [], [[v[0] for v in f.verts] for f in faces])
    uv = me.uv_layers.new(name="UVMap")
    me.materials.append(game_material(tex, name))
    glass_png = os.path.join(tex, name + "_glass_ca.png")
    me.materials.append(game_glass(glass_png) if os.path.exists(glass_png) else glass_grey())
    for poly, f in zip(me.polygons, faces):
        poly.material_index = 1 if "_glass" in f.texture.lower() else 0
        for k, li in enumerate(poly.loop_indices):
            uv.data[li].uv = (f.verts[k][2], 1.0 - f.verts[k][3])
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(40.0))
    ob = bpy.data.objects.new(me.name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def vanilla_tex_material(tex):
    """A part with a vanilla texture by path (dz\\...\\_co.paa): the picture over the part's UV."""
    rel = tex[3:] if tex.lower().startswith("dz\\") else tex
    png = vanilla_png(os.path.splitext(rel)[0])
    m = bpy.data.materials.new("vanilla_" + os.path.basename(rel))
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.7
    if png:
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(png, check_existing=True)
        nt.links.new(n.outputs["Color"], b.inputs["Base Color"])
    return m


def standins(decor, offset=(0.0, 0.0, 0.0)):
    """Vanilla proxy items (kvanilla.put): Blender has no shape for them (ODOL is not read), so a
    semi-transparent blue box the size of the item's near LOD stands in. In the game the item itself is there."""
    import bmesh
    import kvanilla
    m = bpy.data.materials.get("vanilla_standin")
    if m is None:
        m = bpy.data.materials.new("vanilla_standin")
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (0.10, 0.55, 0.85, 1)
        b.inputs["Alpha"].default_value = 0.55
        b.inputs["Roughness"].default_value = 0.6
        b.inputs["Emission Color"].default_value = (0.10, 0.55, 0.85, 1)
        b.inputs["Emission Strength"].default_value = 0.25
    obs = []
    for d in decor:
        key = d[5] if len(d) > 5 else d[0]
        q = kvanilla.corners(key, d[1], d[2], d[3])
        bm = bmesh.new()
        vs = [bm.verts.new(tuple(c + o for c, o in zip(p, offset))) for p in q]
        # corners: index = 4 * ix + 2 * iy + iz
        for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
            bm.faces.new([vs[i] for i in f])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        me = bpy.data.meshes.new("standin_" + str(key).split("\\")[-1])
        bm.to_mesh(me)
        bm.free()
        me.materials.append(m)
        ob = bpy.data.objects.new(me.name, me)
        bpy.context.scene.collection.objects.link(ob)
        obs.append(ob)
    return obs


# Vanilla swatches for comparing the look: the same light, the same highlight rules (G -> specular, B -> gloss).
# (label, path base in dz without _co/_smdi/_nohq, atlas crop u0, u1, v0, v1 - fractions, v from top to bottom).
# Chosen by measuring vanilla textures: workshop furniture and tools of the same kind as the machines.
SWATCHES = [
    ("painted metal (crate)", r"structures\furniture\cases\metalcrate\data\metalcrate", (0.25, 0.75, 0.40, 0.85)),
    ("painted steel (workbench)", r"structures\furniture\various\data\workbench", (0.0, 1.0, 0.76, 1.0)),
    ("planks (workbench)", r"structures\furniture\various\data\workbench", (0.0, 0.70, 0.0, 0.70)),
    ("rusty steel (wrench)", r"gear\tools\data\lugwrench", (0.0, 0.45, 0.35, 0.80)),
    ("black plastic (radio)", r"gear\tools\data\walkietalkie", (0.02, 0.22, 0.45, 0.85)),
    ("plastic (computer)", r"structures\furniture\eletrical_appliances\pc\data\pc", (0.0, 0.30, 0.0, 0.18)),
]


def vanilla_png(rel):
    """dz\\<rel>.paa -> PNG in the build/vanilla_png cache (ImageToPAA converts in both directions). None - no file."""
    import subprocess
    import kbake
    import kexport
    src = os.path.join(kexport.VANILLA_DZ, rel + ".paa")
    cache = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "build", "vanilla_png"))
    dst = os.path.join(cache, rel.replace("\\", "_") + ".png")
    if not os.path.exists(dst):
        if not os.path.exists(src):
            return None
        os.makedirs(cache, exist_ok=True)
        subprocess.run([kbake.IMAGE_TO_PAA, src, dst], capture_output=True, text=True)
    return dst if os.path.exists(dst) else None


def swatch_material(base, crop):
    """Swatch material: color from _co, gloss and highlight from _smdi, relief from _nohq (DirectX -> Blender)."""
    m = bpy.data.materials.new("vanilla_" + os.path.basename(base))
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    u0, u1, v0, v1 = crop
    mp = nt.nodes.new("ShaderNodeMapping")                 # tile UV 0..1 -> a piece of the atlas
    mp.inputs["Location"].default_value = (u0, 1.0 - v1, 0.0)
    mp.inputs["Scale"].default_value = (u1 - u0, v1 - v0, 1.0)
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])

    def img(suffix, cs):
        path = vanilla_png(base + suffix)
        if not path:
            return None
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(path, check_existing=True)
        n.image.colorspace_settings.name = cs
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"])
        return n
    co = img("_co", "sRGB")
    if co:
        nt.links.new(co.outputs["Color"], b.inputs["Base Color"])
    sm = img("_smdi", "Non-Color")
    if sm:
        sep = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(sm.outputs["Color"], sep.inputs[0])
        r = nt.nodes.new("ShaderNodeMath")
        r.operation = "SUBTRACT"
        r.inputs[0].default_value = 1.0
        nt.links.new(sep.outputs["Blue"], r.inputs[1])
        nt.links.new(r.outputs[0], b.inputs["Roughness"])
        s = nt.nodes.new("ShaderNodeMath")                 # vanilla specular[] values differ; take 1.0
        s.operation = "MULTIPLY"
        s.inputs[1].default_value = 2.5
        s.use_clamp = True
        nt.links.new(sep.outputs["Green"], s.inputs[0])
        nt.links.new(s.outputs[0], b.inputs["Specular IOR Level"])
    nm = img("_nohq", "Non-Color")
    if nm:
        sepn = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(nm.outputs["Color"], sepn.inputs[0])
        g = nt.nodes.new("ShaderNodeMath")
        g.operation = "SUBTRACT"
        g.inputs[0].default_value = 1.0
        nt.links.new(sepn.outputs["Green"], g.inputs[1])
        comb = nt.nodes.new("ShaderNodeCombineColor")
        nt.links.new(sepn.outputs["Red"], comb.inputs[0])
        nt.links.new(g.outputs[0], comb.inputs[1])
        nt.links.new(sepn.outputs["Blue"], comb.inputs[2])
        nmap = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(comb.outputs[0], nmap.inputs["Color"])
        nt.links.new(nmap.outputs["Normal"], b.inputs["Normal"])
    return m, (co.image.size[0] if co else 1, co.image.size[1] if co else 1)


def _box(name, x0, x1, y0, y1, z0, z1, mat):
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = x0 + (v.co.x + 0.5) * (x1 - x0)
        v.co.y = y0 + (v.co.y + 0.5) * (y1 - y0)
        v.co.z = z0 + (v.co.z + 0.5) * (z1 - z0)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def _tile(name, x0, x1, z0, z1, y, mat):
    """A tile facing -Y with UV 0..1."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name="UVMap")
    for i, c in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[i].uv = c
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def reference_set(x0, y=0.0):
    """To the right of the model: a board with vanilla swatches (two rows of three, tile height
    0.25 m) and a 1.80 m human silhouette for scale. Returns the right edge of the set along x."""
    dark = bpy.data.materials.new("ref_board")
    dark.use_nodes = True
    dark.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1)
    tiles, h, gap = [], 0.25, 0.04
    for label, base, crop in SWATCHES:
        m, (iw, ih) = swatch_material(base, crop)
        w = min(0.45, h * (crop[1] - crop[0]) * iw / max(1e-6, (crop[3] - crop[2]) * ih))
        tiles.append((label, m, w))
    rows = [tiles[:3], tiles[3:]]
    width = max(sum(t[2] for t in r) + gap * (len(r) + 1) for r in rows)
    _box("ref_board", x0, x0 + width, y + 0.01, y + 0.04, 0.55, 0.55 + 2 * h + 3 * gap, dark)
    _box("ref_post_l", x0 + 0.05, x0 + 0.09, y + 0.04, y + 0.08, 0.0, 0.55, dark)
    _box("ref_post_r", x0 + width - 0.09, x0 + width - 0.05, y + 0.04, y + 0.08, 0.0, 0.55, dark)
    for ri, r in enumerate(rows):
        x = x0 + gap
        z = 0.55 + gap + (1 - ri) * (h + gap)
        for label, m, w in r:
            _tile("ref_" + label, x, x + w, z, z + h, y, m)
            x += w + gap
    # a 1.80 m human silhouette: legs, body, arms, head - grey
    grey_m = bpy.data.materials.new("ref_man")
    grey_m.use_nodes = True
    grey_m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.28, 0.28, 0.28, 1)
    hx = x0 + width + 0.45
    for s in (-1, 1):
        _box("man_leg", hx + s * 0.1 - 0.065, hx + s * 0.1 + 0.065, y - 0.07, y + 0.07, 0.0, 0.86, grey_m)
        _box("man_arm", hx + s * 0.27 - 0.045, hx + s * 0.27 + 0.045, y - 0.05, y + 0.05, 0.80, 1.45, grey_m)
    _box("man_body", hx - 0.22, hx + 0.22, y - 0.12, y + 0.12, 0.86, 1.50, grey_m)
    _box("man_neck", hx - 0.05, hx + 0.05, y - 0.05, y + 0.05, 1.50, 1.58, grey_m)
    _box("man_head", hx - 0.09, hx + 0.09, y - 0.11, y + 0.11, 1.58, 1.80, grey_m)
    return hx + 0.35
