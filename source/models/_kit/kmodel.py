"""Common model pipeline: arguments, parts with regions, boolean difference, atlas, baking, PAA,
p3d (visual LODs + Geometry/View/Fire + Memory), rvmat, glass, previews.

A model describes only its own things: regions (name -> material kind, scale), materials, the LOD
build, collision, memory points and preview angles.

    blender --background --python build_mNN.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]
                                                  [--bake-only] [--uv-hash]

--look - a preview without baking: procedural materials right in the render, the light and angles
as in tex_*, plus look_compare - the model next to vanilla swatches and a human silhouette. It
writes nothing into the mod: the model stops at the preview and waits for approval.

Baking on a remote machine: --bake-only - geometry, unwrap and atlas baking (the main atlas and
the states looks, the fast mode kbake.FAST, per-part passes in 4 Blender copies kbake.Split,
--no-split - in one) into work/game_textures; with --bake-render also the tex_* renders into
work/renders (bakery_render); it writes nothing else. Neither P: nor the mod is needed (the vanilla
extents come from the job's kvanilla vanilla_boxes.json). --uv-hash - the lines "uvhash: <sha256>"
(the fingerprint of the near-LOD unwrap, kuv.uv_hash) and "vanilla_boxes: {...}", without baking.
--bake-only prints the same uvhash: if it differs from the one computed here, the atlas from there
is not taken. --bake-only --look-render and --bake-only --geo-render - the --look preview and the
--geo form on the remote machine, without baking.
"""
import json
import math
import os
import sys
import time

import bmesh
import bpy

import kbake
import kexport as kx
import kgeo as g
import kmats
import krender
import kuv
import p3d

ARGV = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MOD = "OpenZone_ResearchModels"


class Model:
    def __init__(self, script_file, obj, name, regions, kinds, lod_specs, atlas=2048,
                 glass=None, rvmat=None, selections=(), hidden=(), states=None,
                 bones=(), animations=(), proxies=(), look="v1", decor=(), panels=None, sources=None,
                 modules=(), vsections=None):
        # Look profile (kmats.LOOKS): "v1" - the original look (accepted models), "dayz" - more
        # matte, dirtier, AO in the color; the default rvmat comes from the profile.
        # OZ_LOOK=dayz - view any finished model in the new profile (a before/after preview) without
        # changing its generator; a build without the variable is not affected.
        kmats.use_look(os.environ.get("OZ_LOOK", look))
        rvmat = rvmat or dict(kmats.LOOK["rvmat"])
        # Vanilla proxy items: [(path \dz\... without .p3d, point, up, forward, LODs[, kvanilla key])]
        # - drawn by the engine, no geometry or textures of our own are needed; LODs are the numbers
        # of the visual LODs. In the preview they are blue boxes of their size (krender.standins).
        self.decor = tuple(decor)
        # Parts with their own texture (a screen with frames): section -> dict(off=the "off" PNG
        # from work, frames=[PNGs of the "working" frames], size=PAA side, gloss=gloss). The section
        # is Part(section=...), UV 0..1 over the part's glass_frame (kuv). Textures
        # <name>_<section>_co.paa and _f<N>_co.paa, rvmat <name>_<section>.rvmat and _on.rvmat
        # (glow); the frames are cycled by the mod script (OZL_WorkFx, frames).
        self.panels = dict(panels or {})
        # Animation sources for the mod config: name -> dict(animPeriod=seconds).
        self.sources = dict(sources or {})
        # Modules in slots - for the preview only: [(folder, p3d name, proxy point)] - their finished
        # MLODs with textures stand in their places (krender.our_model); in the game the slot proxy
        # places them, and they are not part of the machine's p3d.
        self.modules = tuple(modules)
        # Parts with a vanilla texture by path: section -> (dz\...\_co.paa, dz\...\.rvmat); the
        # generator sets the UV (Part.fixed_uv), they are not baked.
        self.vsections = dict(vsections or {})
        self.here = os.path.dirname(os.path.abspath(script_file))
        self.asset = os.path.normpath(os.path.join(self.here, ".."))
        self.work = os.path.join(self.asset, "work")
        self.game_tex = os.path.join(self.work, "game_textures")
        self.renders = os.path.join(self.work, "renders")
        self.repo = os.path.normpath(os.path.join(self.asset, "..", ".."))
        self.obj, self.name = obj, name
        self.pbo_dir = os.path.join(self.repo, MOD, obj)
        self.model_root = os.path.join(self.repo, "build", "model-root")
        self.prefix = MOD + "\\" + obj + "\\data"
        self.regions, self.kinds, self.lod_specs, self.atlas = regions, kinds, lod_specs, atlas
        self.glass = glass                # kexport.glass_ca parameters, or None - no glass
        self.rvmat = rvmat
        # Part groups (Part.group) that become named selections of the visual LODs: model.cfg
        # bones, hiddenSelections, Show/HideSelection from the script.
        self.selections = tuple(selections)
        # Machine looks: hidden - selections whose texture the script or hiddenSelectionsTextures
        # changes (they go into sections[] of model.cfg). states - other looks: name ->
        # dict(remap={kind: kind}, emissive=(r, g, b, a)); each has its own atlas
        # <name>_<state>_co.paa (the same atlas, the kinds from remap get another color) and
        # <name>_<state>.rvmat (the same _nohq and _smdi, with glow). The main atlas is the default
        # look ("off"). move - group -> offset for the look preview (the "working" pose: the
        # machine head lowered), it does not go into the p3d.
        self.hidden = tuple(hidden)
        self.states = dict(states or {})
        # model.cfg bones and animations: bones [(bone, parent)], animations [(name, {field: value})]
        self.bones, self.animations = tuple(bones), tuple(animations)
        # Proxies for modules: [(proxy model path without .p3d, Blender point)] - in all visual
        # LODs; the placeholder models are written next to the MLOD (see write_p3d).
        self.proxies = tuple(proxies)
        self.sections = {"atlas": (self.prefix + "\\" + name + "_co.paa", self.prefix + "\\" + name + ".rvmat")}
        if glass is not None:
            self.sections["glass"] = (self.prefix + "\\" + name + "_glass_ca.paa",
                                      self.prefix + "\\" + name + "_glass.rvmat")
        self.sections.update(self.vsections)
        for sec in self.panels:
            self.sections[sec] = (self.prefix + "\\%s_%s_co.paa" % (name, sec),
                                  self.prefix + "\\%s_%s.rvmat" % (name, sec))
        self.geo_only = "--geo" in ARGV
        self.stats = "--stats" in ARGV
        self.skip_bake = "--skip-bake" in ARGV
        self.no_paa = "--no-paa" in ARGV
        self.preview = "--preview" in ARGV
        self.look_preview = "--look" in ARGV
        self.bake_only = "--bake-only" in ARGV
        self.uv_hash = "--uv-hash" in ARGV
        # a Blender copy for kbake.Split: --bake-part <folder> <atlas:look,...> <main pid>
        i = ARGV.index("--bake-part") if "--bake-part" in ARGV else -1
        self.bake_part = tuple(ARGV[i + 1:i + 4]) if i >= 0 else None
        self.script = os.path.abspath(script_file)
        # how many angles in the --look preview: the first n of shots; the first m for machine looks
        self.look_shots = (3, 2)

    def path_work(self, fn):
        return os.path.join(self.work, fn)

    # --- parts ----------------------------------------------------------------------------
    def part(self, name, region, **kw):
        kind, scale = self.regions[region]
        return g.Part(name, region, kind, scale, **kw)

    def _mesh_object(self, name, p, coll=None):
        me = bpy.data.meshes.new(name)
        for f in p.bm.faces:
            f.material_index = f[p.reg]
        p.bm.to_mesh(me)
        for r in p.regions:
            me.materials.append(bpy.data.materials.get("rg_" + r[0]) or bpy.data.materials.new("rg_" + r[0]))
        ob = bpy.data.objects.new(name, me)
        (coll or bpy.context.scene.collection).objects.link(ob)
        return ob

    def boolean(self, name, base, cutters):
        """base minus cutters (EXACT, the materials are transferred): a face knows its region."""
        coll = bpy.data.collections.new("cut_" + name)
        bpy.context.scene.collection.children.link(coll)
        for i, c in enumerate(cutters):
            self._mesh_object("%s_c%d" % (name, i), c, coll)
        coll.hide_viewport = coll.hide_render = True
        ob = self._mesh_object(name, base)
        mod = ob.modifiers.new("cut", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.operand_type = "COLLECTION"
        mod.collection = coll
        mod.solver = "EXACT"
        mod.material_mode = "TRANSFER"
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        p = g.Part(name)
        names = [m.name[3:] for m in me.materials]
        for rn in names:
            p.region_index(rn, *self.regions[rn])
        p.bm.from_mesh(me)
        p.reg = p.bm.faces.layers.int.get("region") or p.bm.faces.layers.int.new("region")
        for f in p.bm.faces:
            f[p.reg] = p.region_index(names[f.material_index])
        bpy.data.objects.remove(ob)
        for o in list(coll.objects):
            bpy.data.objects.remove(o)
        bpy.data.collections.remove(coll)
        bpy.data.meshes.remove(me)
        bmesh.ops.dissolve_degenerate(p.bm, dist=1e-6, edges=p.bm.edges[:])
        p.bm.normal_update()
        return p

    # --- p3d -------------------------------------------------------------------------------
    def write_p3d(self, lods, comps, mass, memory, bbox, drawimportance="0.05"):
        """comps: [(Blender points, surface rvmat for Fire Geometry)]; memory: name -> [Blender
        points]; bbox: (x0, x1, y0, y1, z0, z1) in Blender - the box of the preview and of the item's fall."""
        vis = [kx.visual_lod(parts, float(i + 1), self.sections, self.selections,
                             proxies=self.proxies + tuple(d[:4] for d in self.decor if i in d[4]))
               for i, parts in enumerate(lods)]
        props = [("autocenter", "0"), ("drawimportance", drawimportance)]
        vis.append(kx.geometry_lod(p3d.GEOMETRY, [(c, "") for c, _ in comps], mass=mass, props=props))
        vis.append(kx.geometry_lod(p3d.VIEW_GEOMETRY, [(c, "") for c, _ in comps]))
        vis.append(kx.geometry_lod(p3d.FIRE_GEOMETRY, comps))
        corners = [kx.conv(q) for q in kx.box_pts(*bbox)]
        bmin = tuple(min(c[i] for c in corners) for i in range(3))
        bmax = tuple(max(c[i] for c in corners) for i in range(3))
        mlod = kx.memory_lod(memory)
        for nm, q in (("boundingbox_min", bmin), ("boundingbox_max", bmax)):
            mlod = add_raw_point(mlod, nm, q)
        vis.append(mlod)
        src = kx.prepare_model_root(self.model_root, MOD + "\\" + self.obj, self.pbo_dir)
        kx.write_p3d(os.path.join(src, self.name + ".p3d"), vis)
        # Proxy placeholders: the proxy path is relative to the models root (the same root as
        # binarize uses); vanilla proxies (\dz\...) need no placeholders - their models are in the
        # game and in P:\dz.
        for path in sorted({px[0] for px in self.proxies}):
            if not path.lower().startswith("\\dz\\"):
                kx.proxy_model(os.path.join(self.model_root, path.lstrip("\\") + ".p3d"))

    # --- run ---------------------------------------------------------------------------------
    def run(self, build_lod, collision, shots, row_step=1.6, row_shot=None):
        """build_lod(spec) -> [Part]; collision() -> (comps, mass, memory, bbox);
        shots: [(name, camera, target, lens)] - angles of the near LOD."""
        if self.bake_only:
            # The remote machine reads the log as it goes (the runner window, step timing): lines are flushed at once, unbuffered.
            try:
                sys.stdout.reconfigure(line_buffering=True)
            except (AttributeError, ValueError):
                pass
        bpy.ops.wm.read_factory_settings(use_empty=True)
        lods = [build_lod(s) for s in self.lod_specs]
        layout = kuv.Layout(self.atlas)
        layout.build(lods[0])
        for parts in lods:
            kuv.apply_uv(parts, layout)
        for i, parts in enumerate(lods):
            print("LOD%d: %d tris (%s)" % (i + 1, g.tri_count(parts),
                                           ", ".join("%s %d" % (p.name, len(p.bm.faces)) for p in parts)))
        if os.environ.get("OZ_PART_VOLUMES"):
            # Check: the signed volume of a near-LOD part is negative for an inverted one (normals
            # inward in Blender, hence outward in the MLOD, so the in-game lighting is inside out).
            for p in lods[0]:
                print("partvol %s %.6f" % (p.name, p.bm.calc_volume(signed=True)))
        if self.bake_part:
            kbake.FAST = os.environ.get("OZ_BAKE_FAST", "1") == "1"
            origin = bpy.data.objects.new("origin", None)
            bpy.context.scene.collection.objects.link(origin)
            kbake.bake_part(lods[0], self.kinds, origin, self.atlas, *self.bake_part, remaps=self.remaps())
            return
        if self.uv_hash or self.bake_only:
            print("uvhash: %s" % kuv.uv_hash(lods[0], layout))
        if self.uv_hash:
            kv = sys.modules.get("kvanilla")
            if kv is not None and kv._BOX:
                print("vanilla_boxes: %s" % json.dumps(kv._BOX))
            # Renders on the remote machine (--bake-render) need the modules in slots (their MLODs
            # and textures come from the project) and the vanilla textures of parts - PNGs in the
            # build/vanilla_png cache next to the kit.
            vpng = [krender.vanilla_png(os.path.splitext(t[3:] if t.lower().startswith("dz\\") else t)[0])
                    for t, _ in self.vsections.values()]
            # the --look preview on the remote machine also needs the vanilla swatches of look_compare
            spng = ([krender.vanilla_png(base + s) for _, base, _ in krender.SWATCHES for s in ("_co", "_smdi", "_nohq")]
                    if "--look-inputs" in ARGV else [])
            print("render_inputs: %s" % json.dumps({"modules": [[o, n] for o, n, _ in self.modules],
                                                     "vanilla": [p for p in vpng if p],
                                                     "swatches": [p for p in spng if p]}))
            return
        if self.stats:
            return
        if self.bake_only and "--look-render" in ARGV:
            # The preview without baking on the remote machine: the same as --look here, but on an
            # RTX card a frame is several times faster; no baking, the frames go to work/renders.
            self.render_look(lods, shots)
            return
        if self.bake_only and "--geo-render" in ARGV:
            # The grey form on the remote machine: like --geo, but on that machine's GPU.
            sc = bpy.context.scene
            kbake.use_device(sc)
            with kbake.gpu_slot(sc):
                self.render(lods, shots, row_step, row_shot, textured=False)
            return
        if self.bake_only:
            kbake.FAST = os.environ.get("OZ_BAKE_FAST", "1") == "1"
            # --no-split - a single copy (for before/after timing on the remote machine: the flag
            # travels with the job, environment variables do not)
            kbake.SPLIT = 1 if "--no-split" in ARGV else int(os.environ.get("OZ_BAKE_SPLIT", "4"))
            origin = bpy.data.objects.new("origin", None)
            bpy.context.scene.collection.objects.link(origin)
            self.bake_atlas(lods[0], origin)
            if "--bake-render" in ARGV:
                self.bakery_render(lods, shots, row_step, row_shot)
            return
        if self.geo_only:
            self.render(lods, shots, row_step, row_shot, textured=False)
            return
        if self.look_preview:
            self.render_look(lods, shots)
            return
        data = os.path.join(self.pbo_dir, "data")
        kx.write_super(os.path.join(data, self.name + ".rvmat"), self.prefix + "\\" + self.name + "_nohq.paa",
                       self.prefix + "\\" + self.name + "_smdi.paa", **self.rvmat)
        kx.write_model_cfg(os.path.join(self.pbo_dir, "model.cfg"), self.name, sections=self.hidden,
                           bones=self.bones, animations=self.animations)
        os.makedirs(self.game_tex, exist_ok=True)
        names = [self.name + "_co", self.name + "_nohq", self.name + "_smdi"]
        for st, sd in self.states.items():
            kx.write_super(os.path.join(data, "%s_%s.rvmat" % (self.name, st)), self.prefix + "\\" + self.name + "_nohq.paa",
                           self.prefix + "\\" + self.name + "_smdi.paa", emissive=sd.get("emissive"), **self.rvmat)
            names.append("%s_%s_co" % (self.name, st))
        if self.glass is not None:
            kx.write_glass(os.path.join(data, self.name + "_glass.rvmat"))
            kx.glass_ca(os.path.join(self.game_tex, self.name + "_glass_ca.png"), **self.glass)
            names.append(self.name + "_glass_ca")
        names += self.write_panels(data)
        self.write_install_info(lods[0])
        origin = bpy.data.objects.new("origin", None)
        bpy.context.scene.collection.objects.link(origin)
        if not self.skip_bake:
            self.bake_atlas(lods[0], origin)
        elif self.preview:
            # The atlas already exists (baked on the remote machine): renders use the same device as
            # after baking, otherwise Cycles stays on the CPU.
            kbake.use_device(bpy.context.scene)
        if not self.no_paa:
            kbake.to_paa(self.game_tex, data, names)
        comps, mass, memory, bbox = collision()
        self.write_p3d(lods, comps, mass, memory, bbox)
        if self.preview:
            self.render(lods, shots, row_step, row_shot, textured=True)

    def bakery_render(self, lods, shots, row_step, row_shot):
        """The tex_* renders on the remote machine (--bake-only --bake-render): on an RTX card they are
        several times faster than here on a GTX 1660. The glass goes into game_textures, as with
        --skip-bake here; the frames go to work/renders; the GPU is taken by kbake.gpu_slot, as in
        baking. PAA and p3d stay here (--skip-bake without --preview)."""
        if self.glass is not None:
            kx.glass_ca(os.path.join(self.game_tex, self.name + "_glass_ca.png"), **self.glass)
        sc = bpy.context.scene
        kbake.use_device(sc)
        t0 = time.perf_counter()
        with kbake.gpu_slot(sc):
            self.render(lods, shots, row_step, row_shot, textured=True)
        print("rendered previews: %.1f s (denoiser on %s)" % (time.perf_counter() - t0,
              "GPU" if getattr(sc.cycles, "denoising_use_gpu", False) else "CPU"))

    def remaps(self):
        """Atlas -> the remap of its look (None for the main one)."""
        out = {self.name: None}
        out.update({"%s_%s" % (self.name, st): sd["remap"] for st, sd in self.states.items()})
        return out

    def bake_atlas(self, parts, origin):
        """The main atlas and the atlases of the states looks - PNGs in work/game_textures. With
        --bake-only the per-part passes are also handed to other Blender copies (kbake.SPLIT, kbake.Split)."""
        texs = [(self.name, False)] + [("%s_%s" % (self.name, st), True) for st in self.states]
        split = None
        if self.bake_only and kbake.SPLIT > 1:
            tasks = [(t, m) for t, color_only in texs for m in kbake.modes_for(color_only) if m in kbake.PART_MODES]
            split = kbake.Split(self.script, ARGV, tasks, kbake.SPLIT)
        try:
            for t, color_only in texs:
                kbake.bake(parts, self.kinds, origin, self.atlas, self.game_tex, t, remap=self.remaps()[t],
                           color_only=color_only, elsewhere=split)
        finally:
            if split:
                split.close()

    # --- parts with their own texture (a screen with frames) -----------------------------------
    def panel_pngs(self, sec):
        """The PNGs of a section in work: "off" and the "working" frames (drawn by the model's make_decals.py)."""
        pd = self.panels[sec]
        return self.path_work(pd["off"]), [self.path_work(f) for f in pd["frames"]]

    def write_panels(self, data):
        """The rvmats for "off" and "working" (glow), the PNGs in game_textures under the PAA names;
        returns the names for to_paa."""
        names = []
        flat = ("#(argb,8,8,3)color(0.5,0.5,1,1,NOHQ)", "#(argb,8,8,3)color(1,0.35,0.75,1,SMDI)")
        for sec, pd in self.panels.items():
            kx.write_super(os.path.join(data, "%s_%s.rvmat" % (self.name, sec)), *flat, specular=0.5, power=60.0)
            kx.write_super(os.path.join(data, "%s_%s_on.rvmat" % (self.name, sec)), *flat, specular=0.5, power=60.0,
                           emissive=(1.0, 1.0, 1.0, 1.0))
            off, frames = self.panel_pngs(sec)
            outs = [("%s_%s_co" % (self.name, sec), off)] + \
                   [("%s_%s_f%d_co" % (self.name, sec, i), f) for i, f in enumerate(frames)]
            for n, src in outs:
                kbake.resize_png(src, os.path.join(self.game_tex, n + ".png"), pd.get("size", 256))
                names.append(n)
        return names

    def write_install_info(self, parts):
        """install.json next to model.cfg: the "off" textures and rvmats of the hiddenSelections
        selections (a selection on a part with its own texture gets that one, otherwise the atlas),
        the animPeriod of the sources and the frames of parts with their own texture - for
        installing the model into the mod."""
        import json
        hidden = {}
        for sel in self.hidden:
            secs = {p.section for p in parts if p.group == sel}
            sec = next(iter(secs)) if len(secs) == 1 and next(iter(secs)) in self.panels else "atlas"
            hidden[sel] = list(self.sections[sec])
        info = dict(hidden=hidden, sources=self.sources,
                    panels={sec: dict(off=self.sections[sec][0],
                                      on_rvmat=self.prefix + "\\%s_%s_on.rvmat" % (self.name, sec),
                                      frames=[self.prefix + "\\%s_%s_f%d_co.paa" % (self.name, sec, i)
                                              for i in range(len(pd["frames"]))])
                            for sec, pd in self.panels.items()})
        with open(os.path.join(self.pbo_dir, "install.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(info, fh, ensure_ascii=False, indent=1)

    def panel_mats(self, on):
        """Preview materials of parts with their own texture: "off", or the first frame with glow;
        parts with a vanilla texture use its picture."""
        out = {sec: krender.vanilla_tex_material(tex) for sec, (tex, _) in self.vsections.items()}
        for sec, pd in self.panels.items():
            off, frames = self.panel_pngs(sec)
            out[sec] = krender.panel_material(frames[0] if on else off, glow=1.6 if on else 0.0,
                                              gloss=pd.get("gloss", 0.75))
        return out

    def lod0_decor(self):
        return [d for d in self.decor if 0 in d[4]]

    def place_extras(self, with_modules=True):
        """Preview: blue boxes of the vanilla items and the modules in slots."""
        krender.standins(self.lod0_decor())
        for obj, name, at in self.modules if with_modules else ():
            krender.our_model(obj, name, at)

    def render_look(self, lods, shots):
        """The preview without baking: the near LOD with procedural materials, the light and angles
        as in tex_* (look_<angle>.png), the machine looks as look_<state>_*.png (the replaced kinds
        glow), and look_compare.png - the model next to vanilla swatches and a 1.80 m human
        silhouette. No baking, PAA or p3d."""
        def scene():
            krender.clear_scene()
            kbake.MATS.clear()                 # the materials hold the empty "origin" of the previous scene
            cam = krender.setup(64)
            origin = bpy.data.objects.new("origin", None)
            bpy.context.scene.collection.objects.link(origin)
            return cam, origin
        sc = bpy.context.scene
        sc.render.engine = "CYCLES"
        kbake.use_device(sc)                   # the GPU, as in baking; the slot is taken from the same two
        with kbake.gpu_slot(sc):
            self._render_look(lods, shots, scene, *self.look_shots)
        print("look preview written to", self.renders)

    def _render_look(self, lods, shots, scene, n_main=3, n_state=2):
        """The first n_main angles, the first n_state for machine looks: a person looks at this preview, ~25 s per frame."""
        res = (1400, 1000)
        cam, origin = scene()
        krender.place_look(lods[0], self.kinds, origin, panels=self.panel_mats(False))
        self.place_extras()
        for name, loc, target, lens in shots[:n_main]:
            krender.shoot(cam, os.path.join(self.renders, "look_%s.png" % name), loc, target, lens, res)
        if self.modules:
            # the same places empty (slots without modules): the second angle
            cam, origin = scene()
            krender.place_look(lods[0], self.kinds, origin, panels=self.panel_mats(False))
            self.place_extras(with_modules=False)
            name, loc, target, lens = shots[min(1, len(shots) - 1)]
            krender.shoot(cam, os.path.join(self.renders, "look_empty_%s.png" % name), loc, target, lens, res)
        for st, sd in self.states.items():
            cam, origin = scene()
            krender.place_look(lods[0], self.kinds, origin, remap=sd["remap"], panels=self.panel_mats(True),
                               move=sd.get("move"))
            self.place_extras()
            for name, loc, target, lens in shots[:n_state]:
                krender.shoot(cam, os.path.join(self.renders, "look_%s_%s.png" % (st, name)), loc, target, lens, res)
        cam, origin = scene()
        krender.place_look(lods[0], self.kinds, origin, panels=self.panel_mats(False))
        self.place_extras()
        xs = [v.co.x for p in lods[0] for v in p.bm.verts]
        zs = [v.co.z for p in lods[0] for v in p.bm.verts]
        x0, x1, top = min(xs), max(xs), max(zs)
        right = krender.reference_set(x1 + 0.35)
        cx, width = (x0 + right) / 2, right - x0
        dist = max(width, top * 1.6) * 0.95 + 0.8
        krender.shoot(cam, os.path.join(self.renders, "look_compare.png"), (cx, -dist, 1.35), (cx, 0.0, 0.85), 35,
                      (1600, 900))

    def render(self, lods, shots, row_step, row_shot, textured):
        krender.clear_scene()
        cam = krender.setup(64 if textured else 16)
        if textured:
            mats = {"atlas": krender.game_material(self.game_tex, self.name)}
            if self.glass is not None:
                mats["glass"] = krender.game_glass(os.path.join(self.game_tex, self.name + "_glass_ca.png"))
            mats.update(self.panel_mats(False))
        else:
            mats = {"atlas": krender.grey(), "glass": krender.glass_grey()}
        tag = "tex" if textured else "geo"
        krender.place(lods[0], "l0", (0, 0, 0), mats)
        self.place_extras()
        for name, loc, target, lens in shots:
            krender.shoot(cam, os.path.join(self.renders, "%s_%s.png" % (tag, name)), loc, target, lens, (1400, 1000))
        # other machine looks: the same angle with the atlas of the look (the preview does not show the glow)
        for st, sd in self.states.items() if textured else ():
            krender.clear_scene()
            cam = krender.setup(64)
            smats = dict(mats, atlas=krender.game_material(self.game_tex, self.name, co="%s_%s_co.png" % (self.name, st)))
            smats.update(self.panel_mats(True))
            krender.place(lods[0], "l0", (0, 0, 0), smats, move=sd.get("move"))
            self.place_extras()
            for name, loc, target, lens in shots:
                krender.shoot(cam, os.path.join(self.renders, "%s_%s_%s.png" % (tag, st, name)), loc, target, lens,
                              (1400, 1000))
        krender.clear_scene()
        cam = krender.setup(48 if textured else 16)
        for i, parts in enumerate(lods):
            krender.place(parts, "l%d" % i, (i * row_step, 0, 0), mats)
        loc, target = row_shot or ((row_step, -row_step * 4.0, row_step * 1.2), (row_step, 0, 0.6))
        krender.shoot(cam, os.path.join(self.renders, tag + "_lods.png"), loc, target, 32, (1800, 800))


def add_raw_point(lod, name, q):
    """A memory point in DayZ axes as is (the box is already converted)."""
    pts = list(lod.points) + [tuple(q) + (0,)]
    taggs = [(n, bytes(mask) + b"\x00") for n, mask in lod.taggs]
    m = bytearray(len(pts))
    m[-1] = 1
    taggs.append((name, bytes(m)))
    return p3d.Lod(pts, lod.normals, lod.faces, taggs, lod.resolution)


def sx(a, b, s):
    """A coordinate pair mirrored by the sign s and sorted."""
    return tuple(sorted((s * a, s * b)))
