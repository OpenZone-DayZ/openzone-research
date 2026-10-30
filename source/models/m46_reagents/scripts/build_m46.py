"""M46 - reagent kit (OZL_Tool_Reagents), a module of the Bio line and the shared lab.

A portable 2x2 item. It sits in the OZL_Tool3 slot of the packer and shows on its shelf through a proxy
(slot 3 is inside the M01 box on the right, in place of the rack, and in the M07 isolator on the right).

    blender --background --python build_m46.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py with the system Python first (comparator scale on the lid, tag). The sample liquid
frames (sample_*.png) are drawn by this generator (sample_pngs).

Model: a polypropylene reagent case with dropper bottles, screw-cap vials, a dry-reagent jar and
pipettes in foam sockets, lid open. The case follows the Hach MultiTest kit case 4660100 (145 x 206 x 66
mm): body 206 x 145 x 50 mm, lid 16 mm. The lid is open at 100 degrees, almost upright, and overhangs
about 4 cm at the back. Envelope 0.21 x 0.19 x 0.19 m, within the module limit (0.2 x 0.2 m footprint,
0.25 m high). The mass in Geometry (0.8 kg) matches OZL_Tool_Base. The case is moulded: rounded corners
and edges, parting-line lips, hinge knuckles with steel pins, open latches (a lever on a pin between two
lugs, a window for the lid hook, finger ribs), a bracket handle. Sample vial 3 is open and its cap lies
on the foam; a vanilla pen (proxy) lies between the rows of foam sockets.

Work view: while the station runs, the sample liquid cycles through frames from pale to crimson and back
(its own texture: section sample, selection ozl_sample, OZL_WorkFx frames, no glow since it is not a
screen) and bubbles rise along the wall (bone ozl_work, looped translation with sourceAddress loop: the
top bubble pops, a new one appears at the bottom).

Surface: slightly yellowed, worn plastic with fine scratches on the edges and dirt in the corners, no
faction colour. Signs: comparator scale digits and a numbered tag; the bottle labels are blank. LODs:
near and mid (no sockets, rounding, lips, lugs, ribs or bubbles), no far LOD.

Blender axes: X is width, Y is depth (the front faces -Y), Z is up. The origin is the centre of the
bottom, so the module sits on the module_N proxy point (autocenter = 0 in Geometry).
"""
import math
import os
import sys

import bmesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kbake  # noqa: E402
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import krender  # noqa: E402
import kvanilla as kv  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m ---------------------------------------------------------------------------
W, D = 0.206, 0.145             # Hach 4660100 case
HX, HY = W / 2, D / 2
BASE_H, LID_H = 0.050, 0.016
WALL = 0.0025
RND = 0.007                     # corner radius of the case in plan
LIP = 0.0012                    # parting-line lip: protrusion
HINGE = (HY + 0.002, BASE_H)    # hinge axis (y, z)
OPEN = -100.0                   # lid opened backwards, degrees about X
FOAM_Z = 0.020                  # top of the foam tray
BOTTLES = [(-0.080 + 0.029 * i, 0.038) for i in range(4)]        # dropper bottles (x, y)
BOT_R = 0.012
VIALS = [(-0.082 + 0.020 * i, -0.030) for i in range(5)]         # vials (x, y)
VIAL_R, VIAL_Z0 = 0.008, 0.008
JAR = (0.028, -0.026, 0.015, 0.046)   # dry-reagent jar (x, y, r, top of the cap)
SAMPLE = 3                      # socket of the sample vial (open, its cap lies on the foam)
VIAL_COL = [("cap_red", "liq_pink", 0.034), ("cap_blue", "liq_blue", 0.040), ("cap_yellow", "liq_amber", 0.028),
            None, ("cap_white", "liq_green", 0.038)]
SAMPLE_LEVEL = 0.037
SAMPLE_CAP = (0.0, -0.008)      # cap of the sample vial lies on the foam
PIPETTES = [0.058, 0.080]       # x of the pipettes, lying along Y in grooves
PIP_Y0, PIP_Y1 = -0.058, 0.054
PIP_ZC = FOAM_Z - 0.0018        # pipette axis
LATCH_X = 0.064
LAT_Y, LAT_Z = -HY - 0.0035, BASE_H - 0.006      # latch lever axis
CHART_W, CHART_H = 0.150, 0.088  # comparator card in the lid (as in make_decals.py)
TAG = (0.0, 0.026)              # tag on the right side (y, z)
TAG_W, TAG_H = 0.032, 0.020
PEN = (-0.035, 0.010)           # DayZ pen on the foam between the rows

# bubbles in the sample: three along the front wall, step BUB_T; the bone lifts them one step per loop
BUB_R = 0.0009
BUB_Z0 = FOAM_Z + 0.0015
BUB_T = (SAMPLE_LEVEL - 0.0012 - BUB_Z0) / 3.0
LIQ_R = VIAL_R - 0.0012

LOD_SPECS = [
    # cs - segments per case corner; sides - bottles, small - vials, tiny - bulbs and hinges, thin -
    # pipettes
    dict(lod=0, cs=4, sides=12, small=12, tiny=10, thin=6, jar=16),
    dict(lod=1, cs=1, sides=8, small=6, tiny=6, thin=4, jar=8),
]

REGIONS = {
    "case": ("case", 1.0), "foam": ("foam", 0.8), "glass_brown": ("glass_brown", 1.5), "label": ("label", 1.5),
    "cap_white": ("cap_white", 1.8), "cap_red": ("cap_red", 1.8), "cap_blue": ("cap_blue", 1.8),
    "cap_yellow": ("cap_yellow", 1.8), "jar": ("jar", 1.5), "bulb": ("bulb", 1.5), "bulb_red": ("bulb_red", 1.5),
    "liq_pink": ("liq_pink", 1.0), "liq_blue": ("liq_blue", 1.0), "liq_amber": ("liq_amber", 1.0),
    "liq_pale": ("liq_pale", 1.0), "liq_green": ("liq_green", 1.0), "latch": ("latch", 1.5), "steel": ("steel", 1.0), "chart": ("chart", 3.0),
    "vial": ("vial", 0.6), "bubble": ("bubble", 1.0),
    # case shell interior: same plastic, separate unwrap region. kuv packs the faces of a part that look
    # to one side (-y ...) into one rectangle, and in a thin hollow box the outer front wall and the
    # inner back wall face the same way, so they shared texels and the baked dark interior landed on the
    # outer wall as triangles
    "case_in": ("case", 1.0),
}


def wdecal(name):
    return os.path.join(WORK, name)


def lid_rot():
    return Matrix.Rotation(math.radians(OPEN), 3, "X")


def lid_point(x, y, z):
    """Lid point, closed position -> open position."""
    c = Vector((0.0, HINGE[0], HINGE[1]))
    return tuple(c + lid_rot() @ (Vector((x, y, z)) - c))


# card on the ceiling of the closed lid -> faces forward once open, tilted 10 degrees
CARD_Z = BASE_H + LID_H - WALL - 0.0008
CARD_Y = -0.006
_cc = lid_point(0.0, CARD_Y, CARD_Z)
CHART_DEC = (wdecal("decal_chart.png"), "y", -1, ("x", "z"), (0.0, _cc[2]),
             (CHART_W, CHART_H * abs(math.cos(math.radians(OPEN + 90)))), (_cc[1] - 0.02, _cc[1] + 0.02))
TAG_DEC = (wdecal("decal_tag.png"), "x", 1, ("y", "z"), TAG, (TAG_W, TAG_H), (HX - 0.003, HX + 0.003))

LIT = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0)
PAPER = kmats.lin((230, 222, 196))


def build_cap(mat, origin, color, seed=6.0, gloss=0.4, spec=0.3, floor_z=0.0, dust=0.1, grime=0.25, ribs=420.0):
    """Screw cap (plastic) with fine vertical ribbing on the side, done as relief (_nohq) instead of
    faces: noise in x, y without z on the cap side gives vertical ribs (~2 mm), darker in the grooves;
    the top edge is worn lighter.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    lo = tuple(c * 0.92 for c in color[:3]) + (1,)
    hi = tuple(min(1.0, c * 1.05) for c in color[:3]) + (1,)
    col = t.mixc(t.maprange(t.noise(vec, 6.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0), lo, hi)
    side = t.maprange(t.math("ABSOLUTE", nsep.outputs["Z"]), 0.35, 0.65, 1.0, 0.0)
    rib = t.maprange(t.noise(t.stretch(vec, 1.0, 1.0, 0.0), ribs, 0.0, 0.5), 0.38, 0.62, 0.0, 1.0)
    groove = t.math("MULTIPLY", t.math("SUBTRACT", 1.0, rib), side)
    col = t.mixc(t.math("MULTIPLY", groove, 0.35), col, tuple(c * 0.55 for c in color[:3]) + (1,))
    edge = t.maprange(t.edge_wear(0.0015), 0.06, 0.25, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.35), col, tuple(min(1.0, c * 1.4 + 0.05) for c in color[:3]) + (1,))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.4)
    g_ = t.math("SUBTRACT", gloss, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.5))
    return kmats.out(t, col, g_, s_, t.math("MULTIPLY", rib, side))


KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    # yellowed polypropylene: 'chips' are light scratches on the edges, no rust
    "case": ("paint", dict(color=kmats.lin((224, 216, 188)), under=kmats.lin((240, 236, 222)), seed=3.3,
                           gloss=0.35, spec=0.22, chip=(0.80, 0.87), rust=(0.99, 1.0), rust_low=0.0, floor_z=0.0,
                           dust=0.3, grime=0.33, yellow=0.4, decal_items=[TAG_DEC])),
    "foam": ("plastic", dict(color=kmats.lin((50, 52, 55)), seed=4.4, gloss=0.04, spec=0.03, mottle=0.18,
                             dust=0.35, grime=0.2, scuff=(0.9, 1.0))),
    # dark glass: glossy, but dusty and dirty near the foam
    "glass_brown": ("plastic", dict(color=kmats.lin((104, 44, 12)), seed=4.9, gloss=0.85, spec=0.7, mottle=0.03,
                                    dust=0.05, grime=0.06, scuff=(0.97, 1.0))),
    "label": ("paint", dict(LIT, color=PAPER, under=PAPER, seed=5.1, gloss=0.15, spec=0.08, dust=0.15, grime=0.35,
                            yellow=0.3)),
    "chart": ("paint", dict(LIT, color=PAPER, under=PAPER, seed=5.7, gloss=0.25, spec=0.12, dust=0.05, grime=0.1,
                            decal_items=[CHART_DEC])),
    "cap_white": (build_cap, dict(color=kmats.lin((228, 226, 216)), seed=6.1, gloss=0.4, spec=0.3, dust=0.1,
                                  grime=0.25)),
    "cap_red": (build_cap, dict(color=kmats.lin((168, 36, 30)), seed=7.2, gloss=0.4, spec=0.3, dust=0.1)),
    "cap_blue": (build_cap, dict(color=kmats.lin((38, 72, 148)), seed=7.5, gloss=0.4, spec=0.3, dust=0.1)),
    "cap_yellow": (build_cap, dict(color=kmats.lin((214, 172, 40)), seed=7.8, gloss=0.4, spec=0.3, dust=0.1)),
    "jar": ("plastic", dict(color=kmats.lin((226, 224, 214)), seed=6.3, gloss=0.35, spec=0.25, dust=0.15, grime=0.3,
                            scuff=(0.85, 0.95))),
    "bulb": ("plastic", dict(color=kmats.lin((24, 23, 23)), seed=6.5, gloss=0.2, spec=0.1, dust=0.1, grime=0.1,
                             scuff=(0.9, 1.0))),
    "bulb_red": ("plastic", dict(color=kmats.lin((142, 38, 28)), seed=6.9, gloss=0.25, spec=0.12, dust=0.1,
                                 grime=0.15, scuff=(0.9, 1.0))),
    "liq_pink": ("flat", dict(color=kmats.lin((196, 64, 112)), gloss=0.7, spec=0.5)),
    "liq_blue": ("flat", dict(color=kmats.lin((52, 86, 168)), gloss=0.7, spec=0.5)),
    "liq_amber": ("flat", dict(color=kmats.lin((196, 128, 34)), gloss=0.7, spec=0.5)),
    "liq_pale": ("flat", dict(color=kmats.lin((206, 210, 192)), gloss=0.7, spec=0.5)),
    "liq_green": ("flat", dict(color=kmats.lin((150, 178, 112)), gloss=0.7, spec=0.5)),
    "latch": ("plastic", dict(color=kmats.lin((30, 30, 31)), seed=8.3, gloss=0.4, spec=0.3, dust=0.15,
                              grime=0.2, scuff=(0.8, 0.9))),
    "vial": ("flat", dict(color=kmats.lin((200, 206, 204)), gloss=0.9, spec=0.8)),   # not visible under the glass
    "bubble": ("flat", dict(color=kmats.lin((236, 238, 236)), gloss=0.9, spec=0.6)),
})

# Work view: the sample liquid has its own texture (section sample, selection ozl_sample in
# hiddenSelections): off is a pale sample, work cycles frames from pale to crimson and back; bubbles are
# bone ozl_work, translated up by BUB_T per loop (axis: one metre up, offset in metres, as in the M16
# feed).
SEL_SAMPLE, SEL_WORK = "ozl_sample", "ozl_work"
SAMPLE_PNG = dict(off="sample_off.png", frames=["sample_f%02d.png" % i for i in range(10)], size=64, gloss=0.6)
SAMPLE_LEVELS = [0.85, 0.72, 0.55, 0.38, 0.24, 0.16, 0.24, 0.38, 0.55, 0.72]   # frame saturation
BUBBLE_ANIM = ("ozl_work_bubbles", dict(type="translation", source="ozl_work", sourceAddress="loop",
                                        selection=SEL_WORK, axis="ozl_work_axis", memory=1, minValue=0.0,
                                        maxValue=1.0, offset0=0.0, offset1=BUB_T))
WORK_MOVE = {SEL_WORK: (0.0, 0.0, BUB_T * 0.5)}          # work preview: bubbles halfway
WORK_SHOTS = ("inside", "sample")
# vanilla item: the pen lies on its side on the foam between the rows
DECOR = [kv.put("pen", (PEN[0], PEN[1], FOAM_Z), up=(1, 0, 0), fwd=(0, -1, 0))]


def sample_pngs():
    """Sample liquid frames (UV 0..1 over the part's bounds, meniscus at the top of the image): colour
    from pale straw to the comparator crimson, denser towards the bottom, lighter at the meniscus. Drawn
    by the generator (not by make_decals.py) and identical on every run.
    """
    import numpy as np
    pale = np.array((236, 229, 212)) / 255.0
    deep = np.array((190, 40, 100)) / 255.0
    n = 32
    v = np.linspace(0.0, 1.0, n)[:, None]                         # 0 = top, 1 = bottom
    os.makedirs(WORK, exist_ok=True)
    for fn, k in [(SAMPLE_PNG["off"], 0.10)] + list(zip(SAMPLE_PNG["frames"], SAMPLE_LEVELS)):
        c = pale + (deep - pale) * k
        col = c * (1.0 - 0.18 * (0.3 + k) * v)
        col = np.where(v < 0.07, np.minimum(1.0, col * 1.10 + 0.03), col)
        img = np.repeat(col[:, None, :], n, axis=1).astype(np.float32)
        kbake.save_png(os.path.join(WORK, fn), img)


class ReagentModel(kmodel.Model):
    """Sample liquid: a part with its own texture (like a screen, kmodel panels) that does not glow: the
    work rvmat has no emission, and neither does the preview. The module has no view with another atlas
    (states are empty), so the work preview is its own: look_work_<view>.png (sample frame, bubbles
    halfway).
    """

    def panel_mats(self, on):
        out = {sec: krender.vanilla_tex_material(tex) for sec, (tex, _) in self.vsections.items()}
        for sec, pd in self.panels.items():
            off, frames = self.panel_pngs(sec)
            out[sec] = krender.panel_material(frames[0] if on else off, glow=0.0, gloss=pd.get("gloss", 0.75))
        return out

    def write_panels(self, data):
        names = kmodel.Model.write_panels(self, data)
        flat = ("#(argb,8,8,3)color(0.5,0.5,1,1,NOHQ)", "#(argb,8,8,3)color(1,0.35,0.75,1,SMDI)")
        for sec in self.panels:
            kx.write_super(os.path.join(data, "%s_%s_on.rvmat" % (self.name, sec)), *flat, specular=0.5, power=60.0)
        return names

    def _render_look(self, lods, shots, scene, n_main=3, n_state=2):
        kmodel.Model._render_look(self, lods, shots, scene, n_main, n_state)
        cam, origin = scene()
        krender.place_look(lods[0], self.kinds, origin, panels=self.panel_mats(True), move=WORK_MOVE)
        self.place_extras()
        for name, loc, target, lens in shots:
            if name in WORK_SHOTS:
                krender.shoot(cam, os.path.join(self.renders, "look_work_%s.png" % name), loc, target, lens,
                              (1400, 1000))


OBJ, NAME = "m46_reagents", "ozr_reagents"
M = ReagentModel(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 glass=dict(base=(0.86, 0.89, 0.88), clear=0.10, edge=0.10, smudge=0.08, streaks=0.03),
                 selections=(SEL_SAMPLE, SEL_WORK), hidden=(SEL_SAMPLE,), bones=((SEL_WORK, ""),),
                 animations=(BUBBLE_ANIM,), panels={"sample": SAMPLE_PNG}, decor=DECOR,
                 sources={"ozl_work": dict(animPeriod=0.6)})
P = M.part
BOUNDS = {}


# --- primitives missing from kgeo --------------------------------------------------------------
def face(part, verts, want):
    """Face from bmesh vertices, oriented towards want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def rrect(hx, hy, r, seg):
    """Rounded rectangle in plan (counter-clockwise): the corners are arcs of seg segments."""
    if seg <= 0 or r <= 0:
        return [(hx, hy), (-hx, hy), (-hx, -hy), (hx, -hy)]
    pts = []
    for cx, cy, a0 in ((hx - r, hy - r, 0.0), (-hx + r, hy - r, 90.0), (-hx + r, -hy + r, 180.0),
                       (hx - r, -hy + r, 270.0)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90.0 * k / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def slab(name, region, poly, z0, z1, bot=None, top=None):
    """Prism over a plan polygon from z0 to z1; bot, top are (radius, segments) roundings of the bottom
    and top edge around the whole perimeter.
    """
    p = P(name, region)
    g.prism(p, poly, (0, 1), z0, z1)
    for sp, z in ((bot, z0), (top, z1)):
        if sp and sp[0] > 0 and sp[1] > 0:
            es = [e for e in p.bm.edges if all(abs(v.co.z - z) < 1e-7 for v in e.verts)]
            g.bevel(p.bm, es, sp[0], sp[1])
    p.tag(p.bm.faces[:])
    bmesh.ops.recalc_face_normals(p.bm, faces=p.bm.faces[:])
    return p


def band(name, z0, z1, cs):
    """Lip around the case perimeter: a ring from z0 to z1 protruding by LIP; its inner edge is hidden
    in the wall (no faces there).
    """
    p = P(name, "case")
    bm = p.bm
    po = rrect(HX + LIP, HY + LIP, RND + LIP, cs)
    pi = rrect(HX - 0.001, HY - 0.001, RND - 0.001, cs)
    o0 = [bm.verts.new((x, y, z0)) for x, y in po]
    o1 = [bm.verts.new((x, y, z1)) for x, y in po]
    i0 = [bm.verts.new((x, y, z0)) for x, y in pi]
    i1 = [bm.verts.new((x, y, z1)) for x, y in pi]
    n = len(po)
    for k in range(n):
        j = (k + 1) % n
        out = ((po[k][0] + po[j][0]) / 2, (po[k][1] + po[j][1]) / 2, 0.0)
        p.tag([face(p, [o0[k], o0[j], o1[j], o1[k]], out),
               face(p, [o1[k], o1[j], i1[j], i1[k]], (0, 0, 1)),
               face(p, [o0[k], i0[k], i0[j], o0[j]], (0, 0, -1))])
    return p


def lathe(part, prof, sides, center, top=False, regions=None, phase=0.5):
    """Body of revolution around the vertical through center (x, y): prof [(r, z)] from bottom to top, r
    = 0 is a pole; regions is a region per band (None - the part's current region); top closes the top.
    """
    bm = part.bm
    cx, cy = center
    keep = part.cur

    def ring(r, z):
        if r <= 0.0:
            return [bm.verts.new((cx, cy, z))]
        return [bm.verts.new((cx + r * math.cos(2 * math.pi * (k + phase) / sides),
                              cy + r * math.sin(2 * math.pi * (k + phase) / sides), z)) for k in range(sides)]
    rings = [ring(r, z) for r, z in prof]
    for i in range(len(rings) - 1):
        if regions and regions[i]:
            part.use(regions[i], *REGIONS[regions[i]])
        (r0, z0), (r1, z1) = prof[i], prof[i + 1]
        a, b = rings[i], rings[i + 1]
        for k in range(sides):
            j = (k + 1) % sides
            th = 2 * math.pi * (k + 0.5 + phase) / sides
            want = (math.cos(th) * (z1 - z0), math.sin(th) * (z1 - z0), -(r1 - r0))
            if len(a) == 1:
                vs = [a[0], b[j], b[k]]
            elif len(b) == 1:
                vs = [a[k], a[j], b[0]]
            else:
                vs = [a[k], a[j], b[j], b[k]]
            part.tag([face(part, vs, want)])
    if top and len(rings[-1]) > 2:
        part.tag([face(part, rings[-1], (0, 0, 1))])
    part.cur = keep
    return part


def boxp(name, region, x0, x1, y0, y1, z0, z1, **kw):
    p = P(name, region)
    g.box(p, x0, x1, y0, y1, z0, z1, **kw)
    return p


def rotate_lid(parts):
    c = Vector((0.0, HINGE[0], HINGE[1]))
    for p in parts:
        bmesh.ops.rotate(p.bm, verts=p.bm.verts[:], cent=c, matrix=lid_rot())
        p.bm.normal_update()
    return parts


# --- case ------------------------------------------------------------------------------------
def shell(name, z0, z1, open_up, spec):
    """Case shell: a moulded box with rounded corners minus the cavity (wall WALL). Body (open_up):
    bottom rounded with a 4 mm radius, the rim slightly; lid: top rounded 5 mm, ceiling inside 3 mm.
    """
    lod0 = spec["lod"] == 0
    cs = spec["cs"]
    po = rrect(HX, HY, RND, cs)
    pi = rrect(HX - WALL, HY - WALL, RND - WALL, cs)
    if open_up:
        outer = slab(name, "case", po, z0, z1, bot=(0.004, 1) if lod0 else None, top=(0.0007, 1) if lod0 else None)
        cut = slab(name + "_cut", "case_in", pi, z0 + WALL, z1 + 0.01)
    else:
        outer = slab(name, "case", po, z0, z1, bot=(0.0007, 1) if lod0 else None, top=(0.005, 2) if lod0 else None)
        cut = slab(name + "_cut", "case_in", pi, z0 - 0.01, z1 - WALL, top=(0.003, 1) if lod0 else None)
    return M.boolean(name, outer, [cut])


def latch(sx, lid, base):
    """Open latch: the lever hangs on a pin between two lugs of the body and its bottom sticks out a bit
    from the wall; a window for the lid hook at the top, two finger ribs at the bottom. The hook is on
    the lid edge.
    """
    x = sx * LATCH_X
    lg = P("lugs", "case")
    for dx in (-0.0135, 0.0135):
        g.box(lg, x + dx - 0.002, x + dx + 0.002, -HY - 0.0065, -HY + 0.0008, LAT_Z - 0.0045, LAT_Z + 0.0045,
              r=0.0008, seg=1)
    base.append(lg)
    bar = P("latch_axle", "latch")
    g.cyl(bar, (x, LAT_Y, LAT_Z), "x", 0.0032, 0.0228, 12)
    base.append(bar)
    t = math.radians(7.0)
    fr = g.Frame((x, LAT_Y, LAT_Z), (1, 0, 0), (0, -math.sin(t), -math.cos(t)), (0, -math.cos(t), math.sin(t)))
    L = 0.036
    W0, W1 = 0.0105, 0.0120                 # half-width of the lever at the top and at the bottom rounding

    def half(b):
        return W0 + (W1 - W0) * b / (L - 0.003)
    # the lever is four pieces around the window (a boolean difference here gives a keyhole-shaped face,
    # and triangulating it fills the window back in)
    bw0, bw1, aw = 0.0075, 0.0140, 0.0065   # window for the hook
    bottom = [(-half(bw1), bw1), (half(bw1), bw1), (W1, L - 0.003)]
    for k in (1, 2):
        a = math.radians(90.0 * k / 2)
        bottom.append((W1 - 0.003 + 0.003 * math.cos(a), L - 0.003 + 0.003 * math.sin(a)))
    for k in (0, 1):
        a = math.radians(90.0 + 90.0 * k / 2)
        bottom.append((-W1 + 0.003 + 0.003 * math.cos(a), L - 0.003 + 0.003 * math.sin(a)))
    bottom.append((-W1, L - 0.003))
    lever = P("lever", "latch")
    for poly in ([(-W0, 0.0), (W0, 0.0), (half(bw0), bw0), (-half(bw0), bw0)],
                 [(-half(bw0), bw0), (-aw, bw0), (-aw, bw1), (-half(bw1), bw1)],
                 [(aw, bw0), (half(bw0), bw0), (half(bw1), bw1), (aw, bw1)], bottom):
        g.prism(lever, poly, (0, 1), -0.0014, 0.0014, frame=fr)
    for b in (0.0285, 0.0320):
        g.box(lever, -0.0095, 0.0095, b - 0.0006, b + 0.0006, 0.0010, 0.0024, frame=fr)
    base.append(lever)
    ck = P("catch", "case")
    g.box(ck, x - 0.0085, x + 0.0085, -HY - 0.0035, -HY + 0.0005, BASE_H + 0.0035, BASE_H + 0.0095)
    lid.append(ck)


def build_case(spec):
    lod = spec["lod"]
    lod0 = lod == 0
    parts = [shell("base", 0.0, BASE_H, True, spec)]
    lid = [shell("lid", BASE_H, BASE_H + LID_H, False, spec)]
    zt = BASE_H + LID_H
    # handle on the lid: an oval bracket on two posts (at the back once open)
    hd = P("handle", "case")
    for sx in (-1, 1):
        g.box(hd, sx * 0.046 - 0.006, sx * 0.046 + 0.006, -0.009, 0.009, zt - 0.001, zt + 0.0095,
              **({"r": 0.002, "seg": 1} if lod0 else {}))
    if lod0:
        xs = (-0.050, -0.036, 0.0, 0.036, 0.050)
        zs = (0.0095, 0.0114, 0.0122, 0.0114, 0.0095)
        g.tube_var(hd, [(x, -0.001, zt + z) for x, z in zip(xs, zs)], [(0.0048, 0.0036)] * len(xs), 6)
    else:
        g.box(hd, -0.050, 0.050, -0.006, 0.004, zt + 0.008, zt + 0.0155)
    lid.append(hd)
    # comparator card on the lid ceiling, held by four corner pockets
    lid.append(boxp("chart", "chart", -CHART_W / 2, CHART_W / 2, CARD_Y - CHART_H / 2, CARD_Y + CHART_H / 2,
                    CARD_Z - 0.0006, CARD_Z + 0.0008))
    if lod0:
        cl = P("chart_clips", "case")
        for cx in (-CHART_W / 2, CHART_W / 2):
            for cy in (CARD_Y - CHART_H / 2, CARD_Y + CHART_H / 2):
                g.box(cl, cx - 0.0040, cx + 0.0040, cy - 0.0040, cy + 0.0040, CARD_Z - 0.0016, CARD_Z + 0.0010)
        lid.append(cl)
        # lips at the parting line
        parts.append(band("base_lip", BASE_H - 0.0045, BASE_H - 0.0003, 2))
        lid.append(band("lid_lip", BASE_H + 0.0003, BASE_H + 0.0043, 2))
    # hinges: body knuckles at the edges, lid knuckles in the middle, a steel pin through each pair
    kn = P("hinge", "case")
    lk = P("lid_hinge", "case")
    n = 8 if lod0 else 6
    for x0, x1 in ((-0.090, -0.062), (0.062, 0.090)):
        g.cyl(kn, ((x0 + x1) / 2, HINGE[0], HINGE[1] - 0.001), "x", 0.0042, x1 - x0, n)
    for x0, x1 in ((-0.060, -0.032), (0.032, 0.060)):
        g.cyl(lk, ((x0 + x1) / 2, HINGE[0], HINGE[1] + 0.001), "x", 0.0042, x1 - x0, n)
    parts.append(kn)
    lid.append(lk)
    if lod0:
        pin = P("pin", "steel")
        for sx in (-1, 1):
            g.cyl(pin, (sx * 0.061, HINGE[0], HINGE[1]), "x", 0.0016, 0.059, 6)
        parts.append(pin)
        for sx in (-1, 1):
            latch(sx, lid, parts)
    else:
        lt = P("latches", "latch")
        for sx in (-1, 1):
            x = sx * LATCH_X
            g.box(lt, x - 0.012, x + 0.012, -HY - 0.0050, -HY - 0.0015, BASE_H - 0.042, BASE_H - 0.004)
        parts.append(lt)
    return parts + rotate_lid(lid)


def build_foam(spec):
    lod = spec["lod"]
    poly = rrect(HX - WALL - 0.0002, HY - WALL - 0.0002, RND - WALL, spec["cs"])
    foam = slab("foam", "foam", poly, WALL, FOAM_Z, top=(0.0015, 1) if lod == 0 else None)
    if lod > 0:
        return [foam]
    cuts = []

    def hole(x, y, r, z0, n):
        c = P("hole", "foam")
        g.cyl(c, (x, y, (z0 + FOAM_Z + 0.01) / 2), "z", r, FOAM_Z + 0.01 - z0, n)
        cuts.append(c)
    for x, y in VIALS:
        hole(x, y, VIAL_R + 0.0008, VIAL_Z0, spec["tiny"])
    hole(JAR[0], JAR[1], JAR[2] + 0.0008, FOAM_Z - 0.006, spec["jar"])
    for x in PIPETTES:
        # U grooves: for the glass tube and a wider one for the bulb
        c = P("groove", "foam")
        y0, y1 = PIP_Y0 - 0.003, PIP_Y1 - 0.025
        g.cyl(c, (x, (y0 + y1) / 2, PIP_ZC), "y", 0.0042, y1 - y0, 8)
        cuts.append(c)
        c = P("groove", "foam")
        y0, y1 = PIP_Y1 - 0.029, PIP_Y1 + 0.003
        g.cyl(c, (x, (y0 + y1) / 2, PIP_ZC), "y", 0.0064, y1 - y0, 8)
        cuts.append(c)
    return [M.boolean("foam", foam, cuts)]


def build_contents(spec):
    lod = spec["lod"]
    lod0 = lod == 0
    n, ns, nt, nj = spec["sides"], spec["small"], spec["tiny"], spec["jar"]
    parts = []
    # dark-glass dropper bottles: body with a band label, shoulder, neck; white cap; black bulb
    bt = P("bottles", "glass_brown")
    cap = P("bottle_caps", "cap_white")
    bl = P("bulbs", "bulb")
    R = BOT_R
    for x, y in BOTTLES:
        if lod0:
            lathe(bt, [(R, FOAM_Z - 0.001), (R, 0.0225), (R, 0.0335), (0.0100, 0.0372), (0.0068, 0.0400)], n,
                  (x, y), regions=["glass_brown", "label", "glass_brown", "glass_brown"])
            lathe(cap, [(0.0088, 0.0396), (0.0088, 0.0505), (0.0079, 0.0513), (0.0050, 0.0513)], n, (x, y))
            lathe(bl, [(0.0046, 0.0511), (0.0052, 0.0535), (0.0050, 0.0568), (0.0040, 0.0593), (0.0021, 0.0608),
                       (0.0, 0.0613)], 8, (x, y))
        else:
            lathe(bt, [(R, FOAM_Z - 0.001), (R, 0.0335), (0.0068, 0.0400)], n, (x, y),
                  regions=["label", "glass_brown"])
            lathe(cap, [(0.0088, 0.0396), (0.0088, 0.0513)], n, (x, y), top=True)
            lathe(bl, [(0.0050, 0.0511), (0.0060, 0.0545), (0.0, 0.0612)], nt, (x, y))
    parts += [bt, cap, bl]
    # vials: glass (section glass), liquid inside, coloured screw cap
    gl = P("vials", "vial", section="glass")
    for i, (x, y) in enumerate(VIALS):
        col = VIAL_COL[i]
        if col is None:
            continue
        cap_reg, liq_reg, level = col
        lathe(gl, [(VIAL_R, FOAM_Z - 0.001), (VIAL_R, 0.0412)], nt, (x, y))
        lq = P("liq_%d" % i, liq_reg)
        lathe(lq, [(LIQ_R, FOAM_Z - 0.001), (LIQ_R, level)], nt, (x, y), top=True)
        parts.append(lq)
        cp = P("vcap_%d" % i, cap_reg)
        if lod0:
            lathe(cp, [(0.0088, 0.0402), (0.0088, 0.0490), (0.0081, 0.0497)], ns, (x, y), top=True)
        else:
            lathe(cp, [(0.0088, 0.0402), (0.0088, 0.0497)], ns, (x, y), top=True)
        parts.append(cp)
    # sample vial: open (neck with a flared rim), the sample has its own texture (ozl_sample), bubbles
    # along the wall (ozl_work); the cap lies on the foam
    sx, sy = VIALS[SAMPLE]
    if lod0:
        lathe(gl, [(VIAL_R, FOAM_Z - 0.001), (VIAL_R, 0.0440), (VIAL_R + 0.0005, 0.0448), (VIAL_R - 0.0006, 0.0451)],
              nt, (sx, sy))
    else:
        lathe(gl, [(VIAL_R, FOAM_Z - 0.001), (VIAL_R, 0.0450)], ns, (sx, sy))
    parts.append(gl)
    sm = P("sample", "liq_pale", group=SEL_SAMPLE, section="sample")
    lathe(sm, [(LIQ_R, FOAM_Z - 0.001), (LIQ_R, SAMPLE_LEVEL)], ns, (sx, sy), top=True)
    parts.append(sm)
    if lod0:
        bb = P("bubbles", "bubble", group=SEL_WORK)
        for i, a in enumerate((-100.0, -84.0, -94.0)):
            r = LIQ_R - 0.0002
            bx, by = sx + r * math.cos(math.radians(a)), sy + r * math.sin(math.radians(a))
            bz = BUB_Z0 + BUB_T * i
            lathe(bb, [(0.0, bz - BUB_R), (BUB_R, bz), (0.0, bz + BUB_R)], 6, (bx, by))
        parts.append(bb)
    sc = P("sample_cap", "cap_white")
    if lod0:
        lathe(sc, [(0.0088, FOAM_Z), (0.0088, FOAM_Z + 0.0086), (0.0081, FOAM_Z + 0.0093)], ns, SAMPLE_CAP, top=True)
    else:
        lathe(sc, [(0.0088, FOAM_Z), (0.0088, FOAM_Z + 0.0093)], ns, SAMPLE_CAP, top=True)
    parts.append(sc)
    # dry-reagent jar: white plastic with a label, red cap
    jx, jy, jr, jz = JAR
    jb = P("jar", "jar")
    if lod0:
        lathe(jb, [(jr, FOAM_Z - 0.001), (jr, 0.0235), (jr, 0.0325), (jr, 0.0368)], nj, (jx, jy),
              regions=["jar", "label", "jar"])
    else:
        lathe(jb, [(jr, FOAM_Z - 0.001), (jr, 0.0368)], nj, (jx, jy), regions=["label"])
    parts.append(jb)
    jc = P("jar_cap", "cap_red")
    if lod0:
        lathe(jc, [(jr + 0.0008, 0.0362), (jr + 0.0008, jz - 0.0008), (jr - 0.0001, jz)], nj, (jx, jy), top=True)
    else:
        lathe(jc, [(jr + 0.0008, 0.0362), (jr + 0.0008, jz)], nj, (jx, jy), top=True)
    parts.append(jc)
    # pipettes in the grooves: glass tube with a drawn-out tip, red bulb at the back
    pg = P("pipettes", "vial", section="glass")
    pb = P("pip_bulbs", "bulb_red")
    s = spec["thin"]
    for x in PIPETTES:
        if lod0:
            ys = (PIP_Y0, PIP_Y0 + 0.007, PIP_Y0 + 0.020, PIP_Y0 + 0.028, PIP_Y1 - 0.022)
            rs = (0.0008, 0.0013, 0.0030, 0.0035, 0.0035)
            g.tube_var(pg, [(x, y, PIP_ZC) for y in ys], [(r, r) for r in rs], s)
            ys = (PIP_Y1 - 0.027, PIP_Y1 - 0.021, PIP_Y1 - 0.007, PIP_Y1 - 0.002, PIP_Y1)
            rs = (0.0040, 0.0057, 0.0058, 0.0042, 0.0014)
            g.tube_var(pb, [(x, y, PIP_ZC + 0.0004) for y in ys], [(r, r) for r in rs], s)
        else:
            g.tube_var(pg, [(x, PIP_Y0, PIP_ZC), (x, PIP_Y0 + 0.025, PIP_ZC), (x, PIP_Y1 - 0.022, PIP_ZC)],
                       [(0.0010, 0.0010), (0.0035, 0.0035), (0.0035, 0.0035)], s)
            g.tube_var(pb, [(x, PIP_Y1 - 0.027, PIP_ZC), (x, PIP_Y1 - 0.004, PIP_ZC), (x, PIP_Y1, PIP_ZC)],
                       [(0.0045, 0.0045), (0.0058, 0.0058), (0.0030, 0.0030)], s)
    parts += [pg, pb]
    return parts


def build_lod(spec):
    parts = [p for p in build_case(spec) + build_foam(spec) + build_contents(spec) if p.bm.faces]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        # vanilla pen: its bounds are on the foam, not in the neighbours (kvanilla.corners)
        for d in DECOR:
            q = kv.corners(d[5], d[1], d[2], d[3])
            print("decor %s: %s .. %s" % (d[5], tuple(round(min(c[i] for c in q), 4) for i in range(3)),
                                          tuple(round(max(c[i] for c in q), 4) for i in range(3))))
    return parts


def collision():
    """One convex hull: the body and the open lid (a wedge). The mass is the item weight in the mod, 0.8
    kg; the impact sound is plastic.
    """
    pts = [(x, y, z) for x in (-HX, HX) for y in (-HY, HY) for z in (0.0, BASE_H)]
    pts += [lid_point(x, y, z) for x in (-HX, HX) for y in (-HY, HY) for z in (BASE_H, BASE_H + LID_H)]
    comps = [(pts, kx.PEN + r"\plastic.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    sx, sy = VIALS[SAMPLE]
    memory = {
        # inventory preview camera: front-left and above (invView is where the camera is)
        "invView": [(-0.26, -0.44, 0.40)],
        "ce_center": [(0.0, 0.0, 0.08)],
        "ce_radius": [(0.13, 0.0, 0.08)],
        # bubble axis of the sample: one metre up (the translation offset is in metres)
        "ozl_work_axis": [(sx, sy, BUB_Z0), (sx, sy, BUB_Z0 + 1.0)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


SHOTS = [
    ("front", (-0.20, -0.50, 0.34), (0.0, 0.0, 0.07), 40),
    ("inside", (0.04, -0.28, 0.30), (-0.01, 0.0, 0.03), 40),
    ("bottles", (-0.12, -0.20, 0.14), (-0.035, 0.01, 0.035), 50),
    ("latch", (0.17, -0.24, 0.085), (0.060, -0.070, 0.034), 55),
    ("sample", (0.030, -0.150, 0.150), (-0.020, -0.028, 0.033), 70),
    ("back", (0.30, 0.46, 0.26), (0.0, 0.02, 0.08), 40),
]
M.look_shots = (4, 2)

sample_pngs()
M.run(build_lod, collision, SHOTS, row_step=0.32, row_shot=((0.16, -1.1, 0.35), (0.16, 0, 0.09)))
