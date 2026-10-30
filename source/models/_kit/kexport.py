"""Export to DayZ: visual LODs, Geometry / View / Fire, Memory, rvmat, glass _ca, model.cfg, and
a folder for binarize (build/model-root with junctions to data and to the vanilla dz).

Axes: Blender (x, y, z) -> p3d (-x, z, -y). The model face looks at -Y in Blender and goes to p3d
+z; the engine rotates the MLOD by 180 degrees around Y, so the face looks at whoever places the
item. conv is a reflection (determinant -1), so the face winding order flips by itself and comes
out inward, as in Bohemia's models; the normals of visual LODs are written INWARD explicitly.
"""
import math
import os
import shutil
import struct
import sys

import bmesh
import bpy
import numpy as np

sys.path.insert(0, r"C:\Users\Crystal\.claude\skills\dayz-modding\scripts")
import p3d  # noqa: E402

VANILLA_DZ = r"D:\modding\PDrive\dz"
PEN = r"dz\data\data\penetration"


def conv(v):
    return (-v[0], v[2], -v[1])


def proxy_points(origin, up=None, fwd=None):
    """The proxy triangle in p3d axes (like Create -> Proxy in Object Builder): vertex 0 is the
    origin, 1 is 2 m along the "up" axis of the inserted model, 2 is 1 m along its "forward" axis
    (the long leg is up: binarize tells the axes apart by length). Without up/fwd - the identity
    rotation: a module built by our pipeline (the face at Blender -Y) looks the same way as the
    machine. up, fwd - unit Blender vectors: where +Y and +Z of the inserted model's p3d point
    (for vanilla items +Y usually runs along the handle). origin - a Blender point."""
    o = conv(origin)
    if up is None:
        return [o, (o[0], o[1] + 2.0, o[2]), (o[0], o[1], o[2] + 1.0)]
    u, f = conv(up), conv(fwd)
    return [o, tuple(o[i] + 2.0 * u[i] for i in range(3)), tuple(o[i] + f[i] for i in range(3))]


def visual_lod(parts, resolution, sections, selections=(), sharp_deg=40.0, proxies=()):
    """sections: part section name -> (texture, rvmat). selections - part groups that become named
    selections (bones, hiddenSelections). proxies - [(proxy model path without .p3d, Blender
    point[, up, forward])]: a proxy triangle and a proxy:<path>.NNN selection (the rotation is
    proxy_points) are added before the selection masks, so the masks cover all points and faces
    of the LOD. The proxy of a vanilla model (\\dz\\...) is drawn only if it has NO Proxy<name>
    class in CfgNonAIVehicles."""
    pts, normals, nmap, faces, sharp = [], [], {}, [], []
    groups = {g: ([], []) for g in selections}
    for p in parts:
        me = bpy.data.meshes.new("tmp")
        p.bm.to_mesh(me)
        me.shade_smooth()
        me.set_sharp_from_angle(angle=math.radians(sharp_deg))
        base = len(pts)
        pts += [conv(v.co) + (0,) for v in me.vertices]
        uvd = me.uv_layers["UVMap"].data
        cn = me.corner_normals
        sh = me.attributes.get("sharp_edge")
        if sh is not None:
            for e, a in zip(me.edges, sh.data):
                if a.value:
                    sharp += [base + e.vertices[0], base + e.vertices[1]]
        tex, mat = sections[p.section]
        f0 = len(faces)
        for poly in me.polygons:
            verts = []
            for li in poly.loop_indices:
                lp = me.loops[li]
                n = tuple(round(-c, 4) + 0.0 for c in conv(cn[li].vector))   # INWARD
                if n not in nmap:
                    nmap[n] = len(normals)
                    normals.append(n)
                u, v = uvd[li].uv
                verts.append((base + lp.vertex_index, nmap[n], float(u), float(1.0 - v)))
            faces.append(p3d.Face(verts, 0, tex, mat))
        if p.group in groups:
            groups[p.group][0].extend(range(base, len(pts)))
            groups[p.group][1].extend(range(f0, len(faces)))
        bpy.data.meshes.remove(me)
    count = {}
    for px in proxies:
        path, origin = px[0], px[1]
        count[path] = count.get(path, 0) + 1
        name = "proxy:%s.%03d" % (path, count[path])
        if name not in groups:
            groups[name] = ([], [])
        base = len(pts)
        pts += [q + (0,) for q in proxy_points(origin, *px[2:4])]
        if (0.0, 0.0, 0.0) not in nmap:
            nmap[(0.0, 0.0, 0.0)] = len(normals)
            normals.append((0.0, 0.0, 0.0))
        n0 = nmap[(0.0, 0.0, 0.0)]
        groups[name][0].extend(range(base, base + 3))
        groups[name][1].append(len(faces))
        faces.append(p3d.Face([(base + i, n0, 0.0, 0.0) for i in range(3)], 0, "", ""))
    taggs = [("#SharpEdges#", struct.pack("<%dI" % len(sharp), *sharp))] if sharp else []
    n_p, n_f = len(pts), len(faces)
    for g, (pi, fi) in groups.items():
        pm, fm = bytearray(n_p), bytearray(n_f)
        for i in pi:
            pm[i] = 1
        for i in fi:
            fm[i] = 1
        taggs.append((g, bytes(pm) + bytes(fm)))
    # Visual LODs carry no shadow properties - the scheme verified in game on the OpenZone Storage crates.
    print("  LOD %.0f: %d tris, %d points, %d sharp edges" % (resolution, n_f, n_p, len(sharp) // 2))
    return p3d.Lod(pts, normals, faces, taggs, resolution)


def hull(points):
    bm = bmesh.new()
    for p in points:
        bm.verts.new(p)
    r = bmesh.ops.convex_hull(bm, input=bm.verts[:])
    dead = {g for g in list(r.get("geom_interior", [])) + list(r.get("geom_unused", []))
            if isinstance(g, bmesh.types.BMVert)}
    if dead:
        bmesh.ops.delete(bm, geom=list(dead), context="VERTS")
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.verts.index_update()
    bm.normal_update()
    pts = [tuple(v.co) for v in bm.verts]
    tris = [[v.index for v in f.verts] for f in bm.faces]
    vn = [tuple(v.normal) for v in bm.verts]
    bm.free()
    return pts, tris, vn


def box_pts(x0, x1, y0, y1, z0, z1):
    return [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]


def prism_pts(poly_yz, x0, x1):
    """Prism points: a profile (y, z) extruded along x."""
    return [(x, y, z) for x in (x0, x1) for y, z in poly_yz]


def geometry_lod(resolution, comps, mass=None, props=()):
    """comps: [(points, surface material rvmat)] - each one is a convex hull, ComponentNN."""
    pts, normals, faces, spans = [], [], [], []
    for comp_pts, mat in comps:
        hp, tris, vn = hull(comp_pts)
        p0, f0 = len(pts), len(faces)
        pts += [conv(q) + (0,) for q in hp]
        normals += [tuple(-c for c in conv(n)) for n in vn]
        for t in tris:
            faces.append(p3d.Face([(p0 + i, p0 + i, 0.0, 0.0) for i in t], 0, "", mat))
        spans.append((p0, len(pts), f0, len(faces)))

    def mask(sel):
        b = bytearray(len(pts) + len(faces))
        for p0, p1, f0, f1 in sel:
            for i in range(p0, p1):
                b[i] = 1
            for i in range(f0, f1):
                b[len(pts) + i] = 1
        return bytes(b)
    taggs = [("Component%02d" % (k + 1), mask([s])) for k, s in enumerate(spans)]
    if mass:
        taggs.append(p3d.mass_tagg(mass, len(pts)))
    for name, value in props:
        taggs.append(p3d.property_tagg(name, value))
    return p3d.Lod(pts, normals, faces, taggs, resolution)


def memory_lod(points):
    """points: name -> [Blender points]."""
    pts, idx = [], {}
    for name, plist in points.items():
        idx[name] = []
        for q in plist:
            idx[name].append(len(pts))
            pts.append(conv(q) + (0,))
    taggs = []
    for name, ii in idx.items():
        b = bytearray(len(pts))
        for i in ii:
            b[i] = 1
        taggs.append((name, bytes(b)))
    return p3d.Lod(pts, [], [], taggs, p3d.MEMORY)


def proxy_model(path):
    """A placeholder proxy model for a slot (OZL_Tool1..3): the engine draws the item model from the
    slot in its place; the model itself is invisible. A tiny triangle in the near LOD and a Geometry
    with autocenter = 0 - like the vanilla proxies (dz\\characters\\proxies: Geometry autocenter=0)."""
    s = 0.001
    vis = p3d.Lod([(0, 0, 0, 0), (0, 0, s, 0), (0, s, 0, 0)], [(-1.0, 0.0, 0.0)],
                  [p3d.Face([(0, 0, 0, 0), (1, 0, 0, 0), (2, 0, 0, 0)], 0, "", "")], [], 1.0)
    geo = p3d.box_lod((-s, 0, -s), (s, 2 * s, s), p3d.GEOMETRY,
                      [p3d.selection_tagg("Component01", 8, 6), p3d.property_tagg("autocenter", "0")])
    write_p3d(path, [vis, geo])


def write_p3d(path, lods):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    n = p3d.write(path, lods)
    print("WROTE %s (%d bytes, %d LODs)" % (path, n, len(lods)))
    _, back = p3d.read(path)
    for lod in back:
        print("   %-16s pts=%5d faces=%5d sel=%s" % (lod.name, len(lod.points), len(lod.faces),
                                                   ",".join(n for n, _ in lod.taggs if not n.startswith("#"))))


def prepare_model_root(model_root, prefix_rel, pbo_obj_dir):
    """build/model-root/<prefix>/<object>/: a real folder for the MLOD, data -> a junction to the
    mod's data, dz -> a junction to the vanilla dz; model.cfg is a copy."""
    import _winapi
    src = os.path.join(model_root, prefix_rel)
    os.makedirs(src, exist_ok=True)
    for link, target in ((os.path.join(src, "data"), os.path.join(pbo_obj_dir, "data")),
                         (os.path.join(model_root, "dz"), VANILLA_DZ)):
        if not os.path.exists(link):
            _winapi.CreateJunction(target, link)
    cfg = os.path.join(pbo_obj_dir, "model.cfg")
    if os.path.exists(cfg):
        shutil.copy2(cfg, os.path.join(src, "model.cfg"))
    return src


# --- rvmat -------------------------------------------------------------------------------------
STAGE = """class Stage%d
{
	texture = "%s";
	uvSource = "tex";
	class uvTransform
	{
		aside[] = {1.0,0.0,0.0};
		up[] = {0.0,1.0,0.0};
		dir[] = {0.0,0.0,0.0};
		pos[] = {0.0,0.0,0.0};
	};
};
"""


# Glow of the "working" state in the game: the glow rgb from the model scripts (1, 1, 1) is
# multiplied by this. At 1 lamps and screens are barely visible at night; the vanilla detonator LED
# (dz\gear\tools\data\remotedetonator_led.rvmat) uses emmisive 10. A material's glow only makes the
# material itself shine and lights nothing around it (wiki: Luminescence).
EMISSIVE_GAIN = 10.0


def write_super(path, nohq, smdi, specular=0.6, power=80.0, fresnel="#(ai,32,128,1)fresnel(1.5,0.2)",
                forced_alpha=0.0, emissive=None):
    """emissive - (r, g, b, a) glow: the texture color shines by itself (like the vanilla
    gaslighton.rvmat: Super, emmisive[] = {1,1,1,0.35}); rgb is multiplied by EMISSIVE_GAIN.
    None - no glow."""
    stages = [nohq, "#(argb,8,8,3)color(0.5,0.5,0.5,0.5,DT)", "#(argb,8,8,3)color(0,0,0,0,MC)",
              "#(argb,8,8,3)color(1,1,1,1,AS)", smdi, fresnel, r"dz\data\data\env_land_co.paa"]
    em = "0.0,0.0,0.0,1.0" if emissive is None else ",".join(
        "%.2f" % (c * (EMISSIVE_GAIN if i < 3 else 1.0)) for i, c in enumerate(emissive))
    head = ("ambient[] = {1.0,1.0,1.0,1.0};\ndiffuse[] = {1.0,1.0,1.0,1.0};\n"
            "forcedDiffuse[] = {0.0,0.0,0.0,%.1f};\nemmisive[] = {%s};\n"
            "specular[] = {%.2f,%.2f,%.2f,1.0};\nspecularPower = %.1f;\n"
            'PixelShaderID = "Super";\nVertexShaderID = "Super";\n' % (forced_alpha, em, specular, specular, specular,
                                                                          power))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as fh:
        fh.write(head + "".join(STAGE % (i + 1, s) for i, s in enumerate(stages)))


def write_glass(path):
    """Glass material as on the OpenZone_Objects meter (verified in game) and on a vanilla stove."""
    write_super(path, "#(argb,8,8,3)color(0.5,0.5,1,1,NOHQ)", "#(argb,8,8,3)color(0,1,1,1,SMDI)",
                specular=1.0, power=100.0, fresnel="#(ai,32,128,1)fresnel(1.74,1.36)", forced_alpha=1.0)


def glass_ca(path_png, size=256, seed=11, base=(0.60, 0.64, 0.62), clear=0.02, edge=0.16, smudge=0.05,
             streaks=0.04):
    """Dusty glass: almost transparent in the middle, dirtier toward the frame and at the bottom, a couple of smudges."""
    import kbake
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size] / (size - 1.0)
    e = np.minimum.reduce([xx, 1 - xx, yy, 1 - yy])

    def vnoise(n):
        g = rng.random((n + 2, n + 2))
        ui, vi = np.clip((xx * n).astype(int), 0, n - 1), np.clip((yy * n).astype(int), 0, n - 1)
        fu, fv = xx * n - ui, yy * n - vi
        fu, fv = fu * fu * (3 - 2 * fu), fv * fv * (3 - 2 * fv)
        a = g[vi, ui] + (g[vi, ui + 1] - g[vi, ui]) * fu
        b = g[vi + 1, ui] + (g[vi + 1, ui + 1] - g[vi + 1, ui]) * fu
        return a + (b - a) * fv
    sm = vnoise(6) * 0.6 + vnoise(17) * 0.4
    st = np.clip(np.sin(xx * 40 + vnoise(5) * 6) * 0.5 + 0.5, 0, 1) ** 8   # vertical streaks
    low = np.clip((yy - 0.6) / 0.4, 0, 1)                                    # grime at the bottom (yy grows downward)
    alpha = clear + smudge * sm + edge * np.exp(-e / 0.035) + streaks * st * low + 0.06 * low * sm
    rgba = np.empty((size, size, 4), np.float32)
    for i in range(3):
        rgba[..., i] = base[i] * (0.9 + 0.1 * sm)
    rgba[..., 3] = np.clip(alpha, 0, 0.6)
    kbake.save_png(path_png, rgba)                # rows run top to bottom: the bottom of the glass is the bottom of the image


def write_model_cfg(path, model_name, skeleton=None, sections=(), bones=(), animations=()):
    """sections - selections whose texture the script and hiddenSelections change. bones - [(bone,
    parent)], animations - [(name, {field: value})] for class Animations (values are numbers or
    strings). Without bones and animations the text is the same as it was before they were
    supported, byte for byte."""
    def val(v):
        return '"%s"' % v if isinstance(v, str) else ("%g" % v)
    anims = "class Animations {};"
    if animations:
        body = "".join("\t\t\tclass %s\n\t\t\t{\n%s\t\t\t};\n" % (
            n, "".join("\t\t\t\t%s = %s;\n" % (k, val(v)) for k, v in fields.items())) for n, fields in animations)
        anims = "class Animations\n\t\t{\n%s\t\t};" % body
    cfg = """// Model configuration for %(name)s.p3d. GENERATED by the asset generator -- edit the script.
class CfgSkeletons
{
	class %(skel)s
	{
		isDiscrete = 1;
		skeletonInherit = "";
		skeletonBones[] = {%(bones)s};
	};
};

class CfgModels
{
	class %(name)s
	{
		skeletonName = "%(skel)s";
		sectionsInherit = "";
		sections[] = {%(sections)s};
		%(anims)s
	};
};
""" % dict(name=model_name, skel=skeleton or (model_name + "_skeleton"),
           sections=", ".join('"%s"' % s for s in sections),
           bones=", ".join('"%s", "%s"' % b for b in bones), anims=anims)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as fh:
        fh.write(cfg)
