"""M02 - automatic biochemistry analyzer on a laboratory cabinet: the Scientists' Bio Analyzer
(OZL_Eco_Proc_Bio). Processor: cargo 4x4, no modules.

    blender --background --python build_m02.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (display with "work" frames, key
symbols, rotor slot numbers, printer tape, nameplate, inventory tag). Shared sizes are in m02_layout.py.

The device follows 1980s benchtop auto-analyzers, first of all the Roche Cobas Mira (about
74 x 58 x 66 cm, 82 kg): beige body, a sample carousel at the left under a hinged smoked lid (cups
13.9 x 24.7 mm, as in the Technicon RA-1000), a dispenser arm with a needle above it, a photometer
tower at the back with a display and ventilation, a keypad on the slope at the front, a printer with
a tape on the right. It stands on a Soviet laboratory cabinet: three drawers and a door, a worktop
for chemical-resistant plastic at 0.80 m. Total height 1.25 m. Sizes and overall shape match the
version already accepted.

Built with kmodel (the "dayz" look: matte, body yellowed in places, dust on top, wear), visible edges
rounded or chamfered. The 57 mm printer tape (dot-matrix columns of digits, as on the M62 carrier)
comes out of the slot, lies on the deck and hangs from the front; cables run in smooth curves behind
the cabinet to the floor. Vanilla DayZ items through proxies (kvanilla): blood test kit and pen on the
deck, syringe, injection vial, alcohol and disinfectant spray on the worktop.

Work look:
- the display is ozl_screen with its own texture (section vfd): "off" is idle (thermostat 37.0,
  dashes), "work" plays frames _vfd_fNN (OZL_WorkFx frames: test N of 8, optical density grows, a
  progress bar); the yellow LEDs on the tower and at the start key are ozl_lamp (atlas _on, blink);
- the carousel rotor with cups and bottles is the bone ozl_work on the source ozl_work: a model.cfg
  loop (sourceAddress loop, maxValue 1), one turn per 6 s pass;
- the dispenser arm is the bone ozl_arm on the source ozl_arm (OZL_WorkFx wobble): it swings
  -30..+30 degrees around the post from the model pose, so the needle moves between the bushing
  above the slots and the wash cell; the sign of the angle is not verified in game, hence the
  symmetric swing (both ends are valid places).

Blender axes: X is width, Y is depth (face toward -Y), Z is up.
"""
import math
import os
import sys

from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import kvanilla as kv  # noqa: E402
import m02_layout as L  # noqa: E402
from m02_layout import (AX0, AX1, AY0, AY1, CCX, CCY, CX0, CX1, CY0, CY1, R_BASE, R_CUPS, R_LID,  # noqa: E402
                        R_REAG, R_ROT, SLOPE_DY, SLOPE_DZ, YT, Z_ROT, ZA, ZB, ZD, ZT)

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
PX, PY = L.POST

LOD_SPECS = [
    dict(lod=0, bev=2, sides=16),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    # cabinet
    "cab": ("cab", 0.6), "cab_front": ("cab_front", 0.9), "worktop": ("worktop", 0.7), "plinth": ("black", 0.5),
    "chrome": ("chrome", 1.4), "card": ("card", 2.0), "dark": ("dark", 1.0),
    # device body
    "case": ("case", 1.2), "case_dark": ("case_dark", 1.2), "seam": ("seam", 0.8), "black": ("black", 1.2),
    "steel": ("steel", 1.2), "rubber": ("rubber", 0.8), "grille": ("grille_v", 1.0), "plate": ("plate", 2.5),
    "lamp_g": ("lamp_g", 2.0), "led_amber": ("led_amber", 2.0),
    # carousel and dispenser arm
    "carousel": ("carousel", 2.4), "cups": ("cups", 2.0), "cup_empty": ("cup_empty", 2.0),
    "bottle": ("bottle", 1.6), "label": ("label", 1.6), "cap_b": ("cap_b", 1.6), "cap_r": ("cap_r", 1.6),
    "cap_g": ("cap_g", 1.6), "cap_y": ("cap_y", 1.6), "cap_v": ("cap_v", 1.6), "needle": ("needle", 2.0),
    "ptfe": ("ptfe", 2.0),
    # keypad, printer, tape
    "key": ("key", 3.0), "key_dark": ("key_dark", 3.0), "key_green": ("key_green", 3.0),
    "key_red": ("key_red", 3.0), "window": ("window", 1.5), "tape": ("tape", 3.0), "paper_back": ("paper_back", 0.8),
    # small items on the worktop and cables
    "glass_brown": ("glass_brown", 1.4), "tube_a": ("tube_a", 2.0), "tube_b": ("tube_b", 2.0), "rack": ("rack", 1.4),
    "ldpe": ("ldpe", 1.2), "cable_grey": ("cable_grey", 0.8),
}


# =============================================================================
# Materials
# =============================================================================
def mat_serum(z_top):
    """Serum cup: cloudy white plastic, straw-yellow liquid below the level."""
    def build(mat, origin):
        t = kmats.Tree(mat)
        vec, sep = t.coords(origin, 7.0)
        liquid = t.math("LESS_THAN", sep.outputs["Z"], z_top)
        col = t.mixc(liquid, kmats.lin((214, 218, 216)), kmats.lin((214, 168, 62)))
        return kmats.out(t, col, 0.7, 0.55, 0.0)
    return build


def mat_blood(z_cells, z_serum):
    """Vacuum tube after the centrifuge: dark red cells at the bottom, white gel, yellow serum, empty glass above."""
    def build(mat, origin):
        t = kmats.Tree(mat)
        vec, sep = t.coords(origin, 7.5)
        z = sep.outputs["Z"]
        col = t.mixc(t.math("LESS_THAN", z, z_serum), kmats.lin((198, 204, 206)), kmats.lin((206, 160, 58)))
        col = t.mixc(t.math("LESS_THAN", z, z_cells + 0.003), col, kmats.lin((226, 224, 214)))
        col = t.mixc(t.math("LESS_THAN", z, z_cells), col, kmats.lin((92, 14, 12)))
        return kmats.out(t, col, 0.75, 0.6, 0.0)
    return build


def attr_uv(t, name="pp"):
    """Coordinates of a point on the tape (vertex attribute, as on the M62 tape): x across,
    y is minus the path from the slot."""
    a = t.node("ShaderNodeAttribute")
    a.attribute_type = "GEOMETRY"
    a.attribute_name = name
    sep = t.node("ShaderNodeSeparateXYZ")
    t.link(a.outputs["Vector"], sep.inputs[0])
    return sep.outputs["X"], sep.outputs["Y"]


def mat_tape(mat, origin, img, paper, gloss=0.18, spec=0.10):
    """Thermal paper: dot-matrix print by tape coordinates, fibre; clean (just printed)."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 4.1)
    u, v = attr_uv(t)
    c, a = t.image(img, u, v, (0.0, -L.TAPE_LEN / 2), (L.TAPE_W, L.TAPE_LEN))
    col = t.mixc(a, paper, c)
    col = t.mixc(t.math("MULTIPLY", t.noise(vec, 220.0, 3.0, 0.6), 0.08), col, kmats.lin((206, 200, 184)))
    return kmats.out(t, col, gloss, spec, t.math("MULTIPLY", t.noise(vec, 300.0, 2.0, 0.5), 0.04))


def decal(name, ax, sign, uv, center, size, rng=None):
    return (os.path.join(WORK, name), ax, sign, uv, center, size, rng)


_ka0, _ka1, _kb0, _kb1 = L.KEYPAD
KEYS_DECAL = [decal("decal_keys.png", "z", 1, ("x", "y"),
                    ((_ka0 + _ka1) / 2, L.slope_xy(0.0, (_kb0 + _kb1) / 2, L.KEY_C1)[1]),
                    (_ka1 - _ka0, (_kb1 - _kb0) * L.COS_S))]
ROTOR_DECAL = [decal("decal_rotor.png", "z", 1, ("x", "y"), (CCX, CCY), (2 * R_ROT, 2 * R_ROT),
                     (Z_ROT - 0.002, Z_ROT + 0.002))]
_px0, _px1, _pz0, _pz1 = L.PLATE
PLATE_DECAL = [decal("decal_plate.png", "y", 1, ("x", "z"), ((_px0 + _px1) / 2, (_pz0 + _pz1) / 2),
                     (_px1 - _px0, _pz1 - _pz0), (AY1, AY1 + 0.003))]
LABEL_DECAL = [decal("decal_label.png", "y", -1, ("x", "z"), (0.10, 0.66), (0.09, 0.045), (-0.345, -0.32))]

KINDS = kmats.std_kinds(floor_z=0.0)
LAB = dict(KINDS["enamel_lab"][1])
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.15, grime=0.10)
KINDS.update({
    "cab": ("paint", LAB),
    "cab_front": ("paint", dict(LAB, decal_items=LABEL_DECAL)),
    # body: beige paint over plastic, yellowed in places; chips are rare and show grey plastic
    "case": ("paint", dict(color=kmats.lin((214, 206, 186)), under=kmats.lin((140, 136, 126)), seed=2.9, gloss=0.32,
                           spec=0.24, yellow=0.30, chip=(0.70, 0.76), rust=(0.99, 1.0), rust_low=0.0, floor_z=ZB,
                           dust=0.35, grime=0.30)),
    "case_dark": ("plastic", dict(color=kmats.lin((84, 76, 66)), gloss=0.30, spec=0.22, floor_z=ZB, dust=0.30,
                                  scuff=(0.62, 0.70))),
    "seam": ("flat", dict(color=kmats.lin((34, 32, 30)), gloss=0.2, spec=0.1)),
    "dark": ("flat", dict(color=kmats.lin((16, 16, 16)), gloss=0.2, spec=0.1)),
    "chrome": ("steel", dict(seed=6.1, tone=0.42, along="x", gloss=0.62, spec=0.70, floor_z=0.0, dust=0.25,
                             grime=0.4)),
    "needle": ("steel", dict(seed=6.6, tone=0.48, along="z", gloss=0.70, spec=0.75, dust=0.02, grime=0.05)),
    "plate": ("paint", dict(CLEAN, color=kmats.lin((178, 180, 180)), gloss=0.45, spec=0.40, decal_items=PLATE_DECAL)),
    "led_amber": ("flat", dict(color=kmats.lin((110, 62, 10)), gloss=0.85, spec=0.8)),
    "led_amber_on": ("flat", dict(color=kmats.lin((255, 176, 40)), gloss=0.85, spec=0.8)),
    # carousel: grey rotor with slot numbers, cloudy cups with serum, reagent bottles
    "carousel": ("paint", dict(CLEAN, color=kmats.lin((170, 172, 170)), gloss=0.38, spec=0.28,
                               decal_items=ROTOR_DECAL)),
    "cups": (mat_serum(Z_ROT + 0.0120), {}),
    "cup_empty": ("plastic", dict(color=kmats.lin((228, 230, 226)), gloss=0.5, spec=0.35, dust=0.05, grime=0.0)),
    "bottle": ("plastic", dict(color=kmats.lin((222, 222, 214)), gloss=0.35, spec=0.25, dust=0.12, grime=0.05)),
    "label": ("plastic", dict(color=kmats.lin((226, 212, 172)), gloss=0.12, spec=0.06, dust=0.10, grime=0.0,
                              mottle=0.05, scuff=(0.9, 1.0))),
    "cap_b": ("plastic", dict(color=kmats.lin((40, 110, 190)), gloss=0.45, spec=0.35, dust=0.1)),
    "cap_r": ("plastic", dict(color=kmats.lin((196, 48, 38)), gloss=0.45, spec=0.35, dust=0.1)),
    "cap_g": ("plastic", dict(color=kmats.lin((60, 150, 70)), gloss=0.45, spec=0.35, dust=0.1)),
    "cap_y": ("plastic", dict(color=kmats.lin((220, 178, 40)), gloss=0.45, spec=0.35, dust=0.1)),
    "cap_v": ("plastic", dict(color=kmats.lin((126, 84, 168)), gloss=0.45, spec=0.35, dust=0.1)),
    "ptfe": ("plastic", dict(color=kmats.lin((226, 226, 218)), gloss=0.55, spec=0.35, dust=0.05, grime=0.0,
                             mottle=0.03)),
    # keypad: light digit keys, dark function keys, start and stop; the symbols are an image on top
    "key": ("paint", dict(CLEAN, color=kmats.lin((206, 200, 184)), gloss=0.30, spec=0.22, decal_items=KEYS_DECAL)),
    "key_dark": ("paint", dict(CLEAN, color=kmats.lin((78, 74, 68)), gloss=0.30, spec=0.22, decal_items=KEYS_DECAL)),
    "key_green": ("paint", dict(CLEAN, color=kmats.lin((58, 132, 66)), gloss=0.35, spec=0.25, decal_items=KEYS_DECAL)),
    "key_red": ("paint", dict(CLEAN, color=kmats.lin((176, 48, 38)), gloss=0.35, spec=0.25, decal_items=KEYS_DECAL)),
    "window": ("flat", dict(color=kmats.lin((26, 24, 22)), gloss=0.9, spec=0.6)),
    "tape": (mat_tape, dict(img=os.path.join(WORK, "decal_tape.png"), paper=kmats.lin((240, 239, 232)))),
    "paper_back": ("plastic", dict(color=kmats.lin((236, 234, 224)), gloss=0.10, spec=0.05, dust=0.05, grime=0.0,
                                   mottle=0.03, scuff=(0.95, 1.0))),
    # small items: dark glass bottle, tubes, rack, wash bottle, RS-232 cable
    "glass_brown": ("plastic", dict(color=kmats.lin((76, 38, 14)), gloss=0.75, spec=0.6, dust=0.2, grime=0.1,
                                    mottle=0.04, scuff=(0.9, 1.0))),
    "tube_a": (mat_blood(ZB + 0.040, ZB + 0.074), {}),
    "tube_b": (mat_blood(ZB + 0.048, ZB + 0.082), {}),
    "rack": ("plastic", dict(color=kmats.lin((232, 232, 228)), gloss=0.35, spec=0.25, dust=0.2, grime=0.2)),
    "ldpe": ("plastic", dict(color=kmats.lin((222, 228, 230)), gloss=0.40, spec=0.28, dust=0.15, grime=0.05,
                             mottle=0.05)),
    "cable_grey": ("plastic", dict(color=kmats.lin((150, 150, 144)), gloss=0.3, spec=0.2, dust=0.3)),
    "card": ("plastic", dict(color=kmats.lin((232, 226, 206)), gloss=0.10, spec=0.05, dust=0.15, grime=0.05,
                             mottle=0.06)),
})

OBJ, NAME = "m02_bioanalyzer", "ozr_bioanalyzer"
SEL_SCREEN, SEL_LAMP, SEL_ROTOR, SEL_ARM = "ozl_screen", "ozl_lamp", "ozl_work", "ozl_arm"
ON = dict(remap={"led_amber": "led_amber_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
ROTOR_ANIM = ("ozl_work_rotor", dict(type="rotation", source="ozl_work", sourceAddress="loop", selection=SEL_ROTOR,
                                     axis="ozl_work_axis", memory=1, minValue=0.0, maxValue=1.0, angle0=0.0,
                                     angle1=2 * math.pi))
ARM_ANIM = ("ozl_arm_swing", dict(type="rotation", source="ozl_arm", selection=SEL_ARM, axis="ozl_arm_axis", memory=1,
                                  minValue=0.0, maxValue=1.0, angle0=-math.radians(L.ARM_SWING / 2),
                                  angle1=math.radians(L.ARM_SWING / 2)))
VFD_PANEL = dict(off="decal_vfd_off.png", frames=["decal_vfd_f%02d.png" % i for i in range(8)], size=512, gloss=0.85)
DECOR = [
    kv.put(r"dz\gear\medical\BloodTest_Kit", (0.165, 0.062, ZD), **kv.flat(18)),         # next to the dispenser arm
    kv.put("pen", (0.160, -0.040, ZD), **kv.flat(-8)),
    kv.put(r"dz\gear\medical\Syringe_Empty", (0.442, -0.140, ZB), **kv.flat(3)),
    kv.put(r"dz\gear\medical\InjectionVial", (0.440, 0.040, ZB), up=(0, 0, 1), fwd=(0, -1, 0)),
    kv.put(r"dz\gear\medical\alfa", (0.440, 0.272, ZB), up=(0, 0, 1), fwd=(0.3, -1, 0)),
    kv.put(r"dz\gear\medical\DisinfectantSpray", (-0.440, 0.245, ZB), up=(0, 0, 1), fwd=(-1, -0.3, 0)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.22, 0.15, 0.10), clear=0.30, edge=0.14, smudge=0.06, streaks=0.03),
                 selections=(SEL_SCREEN, SEL_LAMP, SEL_ROTOR, SEL_ARM), hidden=(SEL_SCREEN, SEL_LAMP),
                 states={"on": ON}, bones=((SEL_ROTOR, ""), (SEL_ARM, "")), animations=(ROTOR_ANIM, ARM_ANIM),
                 decor=DECOR, panels={"vfd": VFD_PANEL},
                 sources={"ozl_work": dict(animPeriod=6.0), "ozl_arm": dict(animPeriod=0.2)})
P = M.part
KEYS_FR = g.Frame((0.0, AY0, ZD - SLOPE_DZ), (1, 0, 0), (0, L.COS_S, L.SIN_S), (0, -L.SIN_S, L.COS_S))


# =============================================================================
# Primitives missing from kgeo
# =============================================================================
def use(part, region):
    return part.use(region, *M.regions[region])


def R(r, seg, lod):
    """Chamfer of all g.box edges - near LOD only."""
    return dict(r=r, seg=seg) if lod == 0 else {}


def face(part, verts, want):
    """Face from bmesh vertices toward want, in the part's current region."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    f[part.reg] = part.cur
    return f


def basis(axis):
    e3 = Vector(axis).normalized()
    ref = Vector((0, 0, 1)) if abs(e3.z) < 0.9 else Vector((1, 0, 0))
    e1 = ref.cross(e3).normalized()
    return e1, e3.cross(e1).normalized(), e3


def lathe(part, prof, sides, center, axis=(0, 0, 1), regs=None):
    """Body of revolution: prof [(r, h)] along axis from center; r = 0 is an apex on the axis (fan). The
    profile runs with the material on the left: from the axis outward at the bottom, up, back to the
    axis - faces point outward. regs - the region of each strip between neighbouring profile points."""
    bm = part.bm
    c0 = Vector(center)
    e1, e2, e3 = basis(axis)
    rings = []
    for r, h in prof:
        if r < 1e-7:
            rings.append([bm.verts.new(c0 + e3 * h)])
        else:
            rings.append([bm.verts.new(c0 + e3 * h + (e1 * math.cos(2 * math.pi * k / sides) +
                                                     e2 * math.sin(2 * math.pi * k / sides)) * r)
                          for k in range(sides)])
    for i in range(len(prof) - 1):
        dr, dh = prof[i + 1][0] - prof[i][0], prof[i + 1][1] - prof[i][1]
        if regs:
            use(part, regs[i])
        r0, r1 = rings[i], rings[i + 1]
        if len(r0) == 1 and len(r1) == 1:
            continue
        for k in range(sides):
            j = (k + 1) % sides
            if len(r0) == 1:
                q = [r0[0], r1[k], r1[j]]
            elif len(r1) == 1:
                q = [r0[k], r0[j], r1[0]]
            else:
                q = [r0[k], r0[j], r1[j], r1[k]]
            cen = sum((v.co for v in q), Vector()) / len(q) - c0
            rad = cen - e3 * cen.dot(e3)
            rad = rad.normalized() if rad.length > 1e-9 else e1
            face(part, q, rad * dh - e3 * dr)


def rbox(part, fr, x0, x1, y0, y1, z0, z1, r, seg):
    """Box with rounded edges in the inclined frame fr. g.box(..., r, seg, frame=...) in a frame rotated by
    about 180 degrees turns the faces inside out (kgeo moves the cube vertices and bevels the edges along
    its old normals; seen on the dispenser arm), so build in local axes without a frame and transfer to fr."""
    before = set(part.bm.verts)
    g.box(part, x0, x1, y0, y1, z0, z1, r=r, seg=seg)
    m = fr.matrix()
    for v in part.bm.verts:
        if v not in before:
            v.co = m @ v.co
    part.bm.normal_update()


def knurl(part, cx, cy, z0, z1, r, n, depth):
    """Knurled cover around Z: 2n vertices on a circle, every other one sunk by depth (from M16)."""
    poly = [(cx + (r - depth * (k % 2)) * math.cos(math.pi * k / n), cy + (r - depth * (k % 2)) * math.sin(math.pi * k / n))
            for k in range(2 * n)]
    return g.prism(part, poly, (0, 1), z0, z1)


def screw(name, region, at, axis, r=0.0032, sides=6):
    """Screw with a round head on a plane: at - on the surface, axis - outward. Each screw is its own part
    sharing one atlas place (uv_name), so the projections do not overlap."""
    key = "screw_%s_%.4f" % ("".join("%+d" % round(c) for c in axis), r)
    p = P(name, region, uv_name=key, uv_origin=at)
    lathe(p, [(r, 0.0), (r, 0.0006), (r * 0.72, 0.0014), (0.0, 0.0018)], sides, at, axis)
    return p


def frame4(part, ox0, ox1, oz0, oz1, ix0, ix1, iz0, iz1, y0, y1, lod):
    """Frame in the X-Z plane made of four bars: outer ox/oz, opening ix/iz, along Y from y0 to y1."""
    kw = R(0.0012, 1, lod)
    g.box(part, ox0, ox1, y0, y1, oz0, iz0, **kw)
    g.box(part, ox0, ox1, y0, y1, iz1, oz1, **kw)
    g.box(part, ox0, ix0, y0, y1, iz0, iz1, **kw)
    g.box(part, ix1, ox1, y0, y1, iz0, iz1, **kw)


def keycap(part, fr, a, b, w, h, c0, c1, inset):
    """Key cap in frame fr: the bottom w x h at c0, the top smaller by inset on every side at c1."""
    bm = part.bm
    corners = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    lo = [bm.verts.new(fr.p(a + sa * w / 2, b + sb * h / 2, c0)) for sa, sb in corners]
    hi = [bm.verts.new(fr.p(a + sa * (w / 2 - inset), b + sb * (h / 2 - inset), c1)) for sa, sb in corners]
    face(part, hi, fr.n)
    mid = fr.p(a, b, c0)
    for i in range(4):
        j = (i + 1) % 4
        out = ((lo[i].co + lo[j].co) / 2 - mid).normalized()
        face(part, [lo[i], lo[j], hi[j], hi[i]], out + fr.n * 0.3)


def pull(part, base, axis, half, depth=0.028, r=0.0046, sides=6):
    """Bracket handle: base is the middle on the face of the front, axis runs along the handle, the legs
    point to the person (-Y); corners are rounded; pads under the legs."""
    c, ax, out = Vector(base), Vector(axis), Vector((0.0, -1.0, 0.0))
    pts = []
    for s in (-1, 1):
        seq = [(half, 0.0), (half, depth - 0.008), (half - 0.0022, depth - 0.0022), (half - 0.008, depth)]
        if s == 1:
            seq = seq[::-1]
        pts += [c + ax * (s * a) + out * d for a, d in seq]
    g.pipe(part, [tuple(p) for p in pts], r, sides)
    hx, hz = (0.005, 0.008) if abs(ax.x) > 0.5 else (0.008, 0.005)
    for s in (-1, 1):
        q = c + ax * (s * half)
        g.box(part, q.x - hx, q.x + hx, q.y - 0.003, q.y, q.z - hz, q.z + hz)


def lock(name, at, r=0.0085):
    """Cylinder lock on the front: chrome head and a dark keyhole (shared places in the atlas)."""
    x, y, z = at
    hw = P(name, "chrome", uv_name="lock", uv_origin=at)
    lathe(hw, [(r, 0.0), (r, 0.0022), (r - 0.0013, 0.0034), (0.0, 0.0036)], 10, (x, y, z), axis=(0, -1, 0))
    dk = P(name + "_hole", "dark", uv_name="lock_hole", uv_origin=at)
    g.box(dk, x - 0.0011, x + 0.0011, y - 0.0039, y - 0.0034, z - 0.0042, z + 0.0018)
    return [hw, dk]


def tape_strip(part, pts):
    """Tape: two sheets at TAPE_TH - the face (print) and the back; attribute pp = (x - PAPER_X, -s) is the
    place on the tape for the print image (s is the path from the slot). Face: on the hanging part toward
    the person, on the deck up."""
    bm = part.bm
    lay = bm.verts.layers.float_vector.new("pp")
    s = L.arclen(pts)
    x0, x1 = L.PAPER_X - L.TAPE_W / 2, L.PAPER_X + L.TAPE_W / 2
    rows = []
    for i, (y, z) in enumerate(pts):
        a, b = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
        t = Vector((0.0, b[0] - a[0], b[1] - a[1])).normalized()
        n = t.cross(Vector((1.0, 0.0, 0.0)))
        ring = []
        for side in (1, -1):
            for x in (x0, x1):
                v = bm.verts.new(Vector((x, y, z)) + n * (side * L.TAPE_TH / 2))
                v[lay] = (x - L.PAPER_X, -s[i], 0.0)
                ring.append(v)
        rows.append((ring, n))
    for (r0, n0), (r1, n1) in zip(rows, rows[1:]):
        nn = (n0 + n1).normalized()
        use(part, "tape")
        face(part, [r0[0], r0[1], r1[1], r1[0]], nn)
        use(part, "paper_back")
        face(part, [r0[2], r0[3], r1[3], r1[2]], -nn)


# =============================================================================
# Cabinet
# =============================================================================
def build_cabinet(spec):
    """Soviet laboratory cabinet (sizes as kfurn.lab_cabinet in the accepted model): body on a recessed
    plinth, worktop with a rounded edge, three drawers and a door; handles are chrome brackets on pads,
    the drawers have card frames, the top drawer and the door have locks, door hinges."""
    lod = spec["lod"]
    t_top, plinth_h, inset = 0.03, 0.08, 0.04
    body = P("cab_body", "cab")
    g.box(body, CX0, CX1, CY0 + 0.02, CY1, plinth_h if lod < 2 else 0.0, ZB - t_top, **R(0.003, 1, lod))
    top = P("cab_top", "worktop")
    g.box(top, CX0 - 0.01, CX1 + 0.01, CY0 - 0.005, CY1 + 0.005, ZB - t_top, ZB, **R(0.006, 2, lod))
    fr = P("cab_fronts", "cab_front")
    parts = [body, top, fr]
    gap, t = 0.004, 0.018
    z_lo, z_hi = plinth_h + gap, ZB - t_top - gap
    yb, yf = CY0 + 0.02, CY0 + 0.02 - t                       # back and face of the fronts
    if lod == 2:
        g.box(fr, CX0 + gap, CX1 - gap, yf, yb, z_lo, z_hi)
        return parts
    pl = P("cab_plinth", "plinth")
    g.box(pl, CX0 + inset, CX1 - inset, CY0 + inset, CY1 - inset, 0.0, plinth_h + 0.002)
    parts.append(pl)
    fronts = []
    xa = CX0 + gap
    for share, heights, kind in ((0.42, (1, 1, 1), "drawer"), (0.58, (1,), "door")):
        xb = xa + (CX1 - CX0 - gap) * share - gap
        za = z_hi
        for h in heights:
            zb = za - (z_hi - z_lo) * h / sum(heights)
            fronts.append((xa, xb, zb + gap / 2, za - gap / 2, kind))
            za = zb
        xa = xb + gap
    for x0, x1, z0, z1, kind in fronts:
        g.box(fr, x0, x1, yf, yb, z0, z1, **R(0.0025, 1, lod))
    for i, (x0, x1, z0, z1, kind) in enumerate(fronts):
        if kind == "drawer":
            cx, cz = (x0 + x1) / 2, z1 - 0.065
            hd = P("pull%d" % i, "chrome", uv_name="pull_h", uv_origin=(cx, yf, cz))
            if lod == 0:
                pull(hd, (cx, yf, cz), (1, 0, 0), 0.064)
            else:
                g.box(hd, cx - 0.066, cx + 0.066, yf - 0.028, yf, cz - 0.004, cz + 0.004)
        else:
            cx, cz = x1 - 0.045, z1 - 0.16
            hd = P("pull_door", "chrome")
            if lod == 0:
                pull(hd, (cx, yf, cz), (0, 0, 1), 0.064)
            else:
                g.box(hd, cx - 0.004, cx + 0.004, yf - 0.028, yf, cz - 0.066, cz + 0.066)
        parts.append(hd)
    if lod == 1:
        return parts
    for i, (x0, x1, z0, z1, kind) in enumerate(fronts):
        if kind == "drawer":
            cx, zc = (x0 + x1) / 2, z1 - 0.030
            # card frame: bottom, sides and tabs on top (the card is inserted from above)
            cd = P("card%d" % i, "card", uv_name="card", uv_origin=(cx, yf, zc))
            g.box(cd, cx - 0.033, cx + 0.033, yf - 0.0008, yf, zc - 0.012, zc + 0.012)
            hw = P("card_frame%d" % i, "chrome", uv_name="card_frame", uv_origin=(cx, yf, zc))
            g.box(hw, cx - 0.036, cx + 0.036, yf - 0.0022, yf, zc - 0.0145, zc - 0.0115)
            for s in (-1, 1):
                g.box(hw, *sorted((cx + s * 0.033, cx + s * 0.036)), yf - 0.0022, yf, zc - 0.0145, zc + 0.0125)
                g.box(hw, *sorted((cx + s * 0.036, cx + s * 0.027)), yf - 0.0022, yf - 0.0010, zc + 0.0105, zc + 0.0125)
            parts += [cd, hw]
            if i == 0:
                parts += lock("lock_drawer", (cx + 0.13, yf, zc))
        else:
            parts += lock("lock_door", (x1 - 0.045, yf, z1 - 0.07))
            for k, zz in enumerate((z0 + 0.10, z1 - 0.10)):
                hg = P("hinge%d" % k, "chrome", uv_name="hinge", uv_origin=(x0, yf, zz))
                g.cyl(hg, (x0 - 0.0015, yf - 0.002, zz), "z", 0.0055, 0.055, 10)
                parts.append(hg)
    return parts


# =============================================================================
# Device body and tower
# =============================================================================
def build_body(spec):
    """Tray and lid of the body with a seam between them, the slope at the front, rubber feet, ventilation
    slots on the sides and at the back."""
    lod, bev = spec["lod"], spec["bev"]
    if lod == 2:
        deck = P("deck", "case")
        g.prism(deck, [(AY0, ZB), (AY1, ZB), (AY1, ZD), (AY0 + SLOPE_DY, ZD), (AY0, ZD - SLOPE_DZ)], (1, 2), AX0, AX1)
        return [deck]
    zc = ZA + L.TRAY_H + (0.004 if lod == 0 else 0.0)            # bottom of the lid
    tray = P("tray", "case")
    g.box(tray, AX0, AX1, AY0, AY1, ZA, ZA + L.TRAY_H, **R(0.004, 2, lod))
    deck = P("deck", "case")
    g.prism(deck, [(AY0, zc), (AY1, zc), (AY1, ZD), (AY0 + SLOPE_DY, ZD), (AY0, ZD - SLOPE_DZ)], (1, 2), AX0, AX1)
    if bev:
        g.bevel(deck.bm, deck.bm.edges[:], 0.008, 3)
    parts = [tray, deck]
    if lod == 1:
        ft = P("afeet", "rubber")
        g.box(ft, AX0 + 0.03, AX1 - 0.03, AY0 + 0.03, AY1 - 0.03, ZB, ZA + 0.001)
        return parts + [ft]
    for i, (fx, fy) in enumerate([(fx, fy) for fx in (AX0 + 0.05, AX1 - 0.05) for fy in (AY0 + 0.05, AY1 - 0.05)]):
        ft = P("afoot%d" % i, "rubber", uv_name="afoot", uv_origin=(fx, fy, 0.0))
        lathe(ft, [(0.0135, ZB), (0.016, ZB + 0.0025), (0.016, ZA + 0.001)], 8, (fx, fy, 0.0))
        parts.append(ft)
    seam = P("seam", "seam")
    g.box(seam, AX0 + 0.004, AX1 - 0.004, AY0 + 0.004, AY1 - 0.004, ZA + L.TRAY_H - 0.002, zc + 0.003)
    parts.append(seam)
    # slots: each is its own part sharing one atlas place (identical, projections do not overlap)
    for k in range(6):
        z0 = zc + 0.022 + k * 0.012
        for x, s, side in ((AX0, -1, "l"), (AX1, 1, "r")):
            vt = P("vent_%s%d" % (side, k), "dark", uv_name="vent_" + side, uv_origin=(x, -0.135, z0))
            g.box(vt, *sorted((x - s * 0.0005, x + s * 0.0006)), -0.20, -0.07, z0, z0 + 0.005)
            parts.append(vt)
    for k in range(5):
        z0 = zc + 0.030 + k * 0.014
        vt = P("vent_b%d" % k, "dark", uv_name="vent_b", uv_origin=(-0.20, AY1, z0))
        g.box(vt, -0.30, -0.10, AY1 - 0.0005, AY1 + 0.0006, z0, z0 + 0.005)
        parts.append(vt)
    return parts


def build_tower(spec):
    """Photometer tower: display in a frame (own texture, ozl_screen), LEDs in bezels (the yellow one is
    ozl_lamp), louvres on the left, access hatch with screws and an empty plate under the display,
    hinged photometer cover and slots on top, mains switch on the right side."""
    lod = spec["lod"]
    tw = P("tower", "case")
    g.box(tw, AX0, AX1, YT, AY1, ZD - 0.002, ZT, **R(0.015, 3, lod))
    parts = [tw]
    if lod == 2:
        return parts
    x0, x1, z0, z1 = L.VFD
    bz = P("vfd_bezel", "black")
    frame4(bz, x0 - 0.010, x1 + 0.010, z0 - 0.008, z1 + 0.008, x0, x1, z0, z1, YT - 0.006, YT + 0.001, lod)
    vf = P("vfd", "dark", group=SEL_SCREEN, section="vfd")
    yv = YT - 0.0035
    face(vf, [vf.bm.verts.new((x, yv, z)) for x, z in ((x0, z0), (x1, z0), (x1, z1), (x0, z1))], (0, -1, 0))
    vf.glass_frame = (g.Frame((0.0, yv, 0.0), (1, 0, 0), (0, 0, 1), (0, -1, 0)), x0, x1, z0, z1)
    parts += [bz, vf]
    # LEDs: green "power", yellow "measuring" (blinks at work)
    for z, reg, grp in ((1.175, "lamp_g", "body"), (1.150, "led_amber", SEL_LAMP)):
        ld = P("tower_" + reg, reg, group=grp)
        if lod == 0:
            bzl = P("led_bezel_" + reg, "chrome", uv_name="led_bezel", uv_origin=(0.335, YT, z))
            lathe(bzl, [(0.0046, 0.0), (0.0066, 0.0), (0.0066, 0.0016), (0.0050, 0.0026)], 12, (0.335, YT, z),
                  axis=(0, -1, 0))
            parts.append(bzl)
            lathe(ld, [(0.0044, 0.0), (0.0044, 0.0018), (0.0036, 0.0034), (0.0020, 0.0043), (0.0, 0.0046)], 12,
                  (0.335, YT, z), axis=(0, -1, 0))
        else:
            g.box(ld, 0.331, 0.339, YT - 0.003, YT, z - 0.004, z + 0.004)
        parts.append(ld)
    # louvres above the carousel lid hinge
    gx0, gx1, gz0, gz1 = -0.330, -0.050, 1.080, 1.205
    gf = P("grille_frame", "case")
    frame4(gf, gx0, gx1, gz0, gz1, gx0 + 0.010, gx1 - 0.010, gz0 + 0.008, gz1 - 0.008, YT - 0.009, YT + 0.001, 1)
    gb = P("grille_back", "dark")
    g.box(gb, gx0 + 0.010, gx1 - 0.010, YT - 0.0012, YT + 0.0005, gz0 + 0.008, gz1 - 0.008)
    parts += [gf, gb]
    if lod == 1:
        return parts
    n = 7
    for k in range(n):
        zk = gz0 + 0.0115 + k * (gz1 - gz0 - 0.023) / n
        sl = P("slat%d" % k, "case", uv_name="slat", uv_origin=(0.0, 0.0, zk))
        g.prism(sl, [(YT - 0.0012, zk + 0.0070), (YT - 0.0012, zk + 0.0105), (YT - 0.0085, zk + 0.0035),
                     (YT - 0.0085, zk)], (1, 2), gx0 + 0.010, gx1 - 0.010)
        parts.append(sl)
    # hatch under the display: two screws, empty plate
    ap = P("access_panel", "case")
    g.box(ap, 0.058, 0.302, YT - 0.0016, YT + 0.001, 1.020, 1.102, r=0.0012, seg=1)
    for k, x in enumerate((0.068, 0.292)):
        parts.append(screw("panel_screw%d" % k, "steel", (x, YT - 0.0016, 1.061), (0, -1, 0)))
    npl = P("nameplate", "case_dark")
    g.box(npl, 0.12, 0.24, YT - 0.0024, YT - 0.0012, 1.078, 1.090)
    # photometer cover on top: hinges at the back, a finger notch; ventilation slots on the right
    tc = P("top_cover", "case")
    g.box(tc, -0.320, 0.040, 0.142, 0.262, ZT - 0.001, ZT + 0.004, r=0.003, seg=2)
    for k, x in enumerate((-0.28, 0.0)):
        hg = P("top_hinge%d" % k, "case_dark", uv_name="top_hinge", uv_origin=(x, 0.262, ZT))
        g.cyl(hg, (x, 0.262, ZT + 0.002), "x", 0.0035, 0.030, 10)
        parts.append(hg)
    dk = P("top_notch", "dark")
    g.box(dk, -0.160, -0.120, 0.1415, 0.1445, ZT + 0.0025, ZT + 0.0042)
    for k in range(6):
        yk = 0.152 + k * 0.0185
        ts = P("top_slot%d" % k, "dark", uv_name="top_slot", uv_origin=(0.0, yk, ZT))
        g.box(ts, 0.085, 0.325, yk, yk + 0.006, ZT - 0.0005, ZT + 0.0006)
        parts.append(ts)
    # mains switch on the right side: frame and key, the top pressed outward
    sw = P("power_switch", "black")
    g.box(sw, AX1 - 0.001, AX1 + 0.0035, 0.203, 0.227, 1.088, 1.122, r=0.0012, seg=1)
    g.box(sw, AX1 + 0.0035, AX1 + 0.0065, 0.207, 0.223, 1.105, 1.118)
    g.box(sw, AX1 + 0.0035, AX1 + 0.0048, 0.207, 0.223, 1.092, 1.105)
    return parts + [ap, npl, tc, dk, sw]


def build_back(spec):
    """Back wall of the tower: fan behind a perforated grille in a rim, RS-232 connector with a cable plug
    (screw posts), mains connector with a cord plug and tail, nameplate on rivets, screws in the corners."""
    if spec["lod"] > 0:
        return []
    y = AY1
    fg = P("fan_grille", "grille")
    lathe(fg, [(0.044, 0.0004), (0.0, 0.0004)], 20, (-0.20, y, 1.12), axis=(0, 1, 0))
    rim = P("fan_rim", "black")
    lathe(rim, [(0.0440, 0.0), (0.0500, 0.0), (0.0500, 0.0030), (0.0455, 0.0042), (0.0440, 0.0030)], 20,
          (-0.20, y, 1.12), axis=(0, 1, 0))
    con = P("connectors", "steel")
    blk = P("conn_black", "black")
    # RS-232 (DB-25): flange, cable plug in a grey hood, screw posts
    cx, cz, w = 0.040, 1.090, 0.053
    g.box(con, cx - w / 2 - 0.007, cx + w / 2 + 0.007, y - 0.0005, y + 0.0012, cz - 0.0105, cz + 0.0105)
    hood = P("serial_hood", "cable_grey")
    g.box(hood, cx - w / 2 - 0.001, cx + w / 2 + 0.001, y + 0.0012, y + 0.020, cz - 0.0085, cz + 0.0085,
          r=0.003, seg=1)
    extra = []
    for k, s in enumerate((-1, 1)):
        at = (cx + s * (w / 2 + 0.0035), y, cz)
        st = P("standoff%d" % k, "steel", uv_name="standoff", uv_origin=at)
        lathe(st, [(0.0028, 0.0012), (0.0028, 0.0060), (0.0, 0.0060)], 6, at, axis=(0, 1, 0))
        th = P("thumbscrew%d" % k, "cable_grey", uv_name="thumbscrew", uv_origin=at)
        lathe(th, [(0.0035, 0.0045), (0.0035, 0.0175), (0.0028, 0.0190), (0.0, 0.0192)], 10, at, axis=(0, 1, 0))
        extra += [st, th]
    # mains connector: socket body and a plug with the cord tail
    ix, iz = 0.250, 1.060
    g.box(blk, ix - 0.024, ix + 0.024, y - 0.0005, y + 0.008, iz - 0.016, iz + 0.016, r=0.002, seg=1)
    plug = P("power_plug", "black")
    g.box(plug, ix - 0.0165, ix + 0.0165, y + 0.008, y + 0.050, iz - 0.0125, iz + 0.0125, r=0.004, seg=2)
    lathe(plug, [(0.0080, 0.0500), (0.0062, 0.0600), (0.0050, 0.0660)], 10, (ix, y, iz), axis=(0, 1, 0))
    # nameplate on four rivets, screws in the tower corners
    pl = P("rating_plate", "plate")
    x0, x1, z0, z1 = L.PLATE
    g.box(pl, x0, x1, y - 0.0003, y + 0.0009, z0, z1)
    for xx in (x0 + 0.004, x1 - 0.004):
        for zz in (z0 + 0.004, z1 - 0.004):
            extra.append(screw("rivet%d" % len(extra), "steel", (xx, y + 0.0009, zz), (0, 1, 0), r=0.0016))
    for xx in (AX0 + 0.03, AX1 - 0.03):
        for zz in (ZD + 0.03, ZT - 0.03):
            extra.append(screw("back_screw%d" % len(extra), "steel", (xx, y, zz), (0, 1, 0)))
    return [fg, rim, con, blk, hood, plug, pl] + extra


# =============================================================================
# Sample carousel
# =============================================================================
def build_carousel(spec):
    """Bath, rotor with slot numbers (bone ozl_work: rotor, cups, bottles, knob), smoked lid (glass) with a
    tab, a hinge and a needle bushing."""
    lod = spec["lod"]
    nb = 32 if lod == 0 else 16 if lod == 1 else 8
    c0 = (CCX, CCY, 0.0)
    tub = P("car_tub", "case_dark")
    if lod == 0:
        lathe(tub, [(R_BASE, ZD), (R_BASE, ZD + 0.014), (0.146, ZD + 0.014), (0.146, ZD + 0.008), (0.138, ZD + 0.008)],
              28, c0)
    else:
        lathe(tub, [(R_BASE, ZD), (R_BASE, ZD + 0.014), (0.0, ZD + 0.014)], nb, c0)
    rot = P("car_rotor", "carousel", group=SEL_ROTOR)
    if lod == 0:
        lathe(rot, [(R_ROT, ZD + 0.0085), (R_ROT, ZD + 0.0200), (R_ROT - 0.0025, Z_ROT), (0.0225, Z_ROT)], nb, c0)
    else:
        lathe(rot, [(R_ROT, ZD + 0.014), (R_ROT, Z_ROT), (0.0, Z_ROT)], nb, c0)
    parts = [tub, rot]
    if lod == 2:
        return parts
    # cups: wall, rim, serum inside (the empty ones show the bottom)
    # each cup and each bottle is its own part sharing one atlas place (uv_name): identical, projections
    # do not overlap
    for i in range(L.N_CUPS):
        a = 2 * math.pi * i / L.N_CUPS
        c = (CCX + R_CUPS * math.cos(a), CCY + R_CUPS * math.sin(a), Z_ROT)
        reg = "cup_empty" if i in L.EMPTY_CUPS else "cups"
        cp = P("cup%d" % i, reg, group=SEL_ROTOR, uv_name="cup_" + reg, uv_origin=c)
        if lod == 0:
            # wall, rim (bent outward), inner wall, serum (empty cups: bottom)
            bottom = (0.0054, 0.0030) if reg == "cup_empty" else (0.0058, 0.0118)
            lathe(cp, [(0.0066, -0.002), (0.0068, 0.0150), (0.0083, 0.0158), (0.0061, 0.0172), bottom,
                       (0.0, bottom[1])], 10, c)
        else:
            lathe(cp, [(0.0070, 0.0), (0.0070, 0.0172), (0.0, 0.0172)], 6, c)
        parts.append(cp)
    # reagent bottles: label, shoulder and neck, cap in the reagent colour
    caps = ("cap_b", "cap_r", "cap_g", "cap_y", "cap_v", "cap_b")
    for i in range(6):
        a = 2 * math.pi * (i + 0.5) / 6
        c = (CCX + R_REAG * math.cos(a), CCY + R_REAG * math.sin(a), Z_ROT)
        bt = P("reagent%d" % i, "bottle", group=SEL_ROTOR, uv_name="reagent", uv_origin=c)
        ck = P("reagent_cap%d" % i, caps[i], group=SEL_ROTOR, uv_name="reagent_cap", uv_origin=c)
        if lod == 0:
            lathe(bt, [(0.0155, -0.001), (0.0155, 0.009), (0.0155, 0.027), (0.0155, 0.035), (0.0080, 0.0455)], 10, c,
                  regs=["bottle", "label", "bottle", "bottle"])
            lathe(ck, [(0.0094, 0.0455), (0.0094, 0.0545), (0.0, 0.0560)], 10, c)
        else:
            lathe(bt, [(0.0155, 0.0), (0.0155, 0.035), (0.0094, 0.046)], 6, c)
            lathe(ck, [(0.0094, 0.046), (0.0094, 0.056), (0.0, 0.056)], 6, c)
        parts += [bt, ck]
    # rotor knob: flange, knurled head, dome
    hb = P("car_hub", "steel", group=SEL_ROTOR)
    if lod == 0:
        lathe(hb, [(0.0225, Z_ROT - 0.0005), (0.0225, Z_ROT + 0.0020), (0.0150, Z_ROT + 0.0030)], 16, c0)
        kn = P("car_knob", "black", group=SEL_ROTOR)
        knurl(kn, CCX, CCY, Z_ROT + 0.0030, Z_ROT + 0.0190, 0.0135, 14, 0.0012)
        lathe(kn, [(0.0123, Z_ROT + 0.0190), (0.0095, Z_ROT + 0.0215), (0.0, Z_ROT + 0.0225)], 14, c0)
        parts.append(kn)
    else:
        lathe(hb, [(0.0140, Z_ROT), (0.0140, Z_ROT + 0.020), (0.0, Z_ROT + 0.022)], 8, c0)
    parts.append(hb)
    # lid: glass, rounded edge
    lid = P("lid", "case", section="glass")
    if lod == 0:
        lathe(lid, [(R_LID, ZD + 0.004), (R_LID, ZD + 0.0790), (R_LID - 0.0020, ZD + 0.0855), (R_LID - 0.0075, ZD + 0.0893),
                    (R_LID - 0.0140, ZD + 0.0900), (0.0, ZD + 0.0900)], 32, c0)
    else:
        lathe(lid, [(R_LID, ZD + 0.004), (R_LID, ZD + 0.084), (R_LID - 0.008, ZD + 0.090), (0.0, ZD + 0.090)], 16, c0)
    parts.append(lid)
    if lod == 1:
        return parts
    lt = P("lid_parts", "black")
    # tab at the front
    g.box(lt, -0.018, 0.018, -0.003, 0.003, -0.001, 0.008, r=0.002, seg=1,
          frame=g.Frame((CCX, CCY - R_LID, ZD + 0.012), (1, 0, 0), (0, 0, 1), (0, -1, 0)))
    # hinge at the back: leaf on the lid, pivot, bridge and leaf on the tower
    yh = YT - 0.008
    g.box(lt, CCX - 0.016, CCX + 0.016, YT - 0.025, yh, ZD + 0.0898, ZD + 0.0912)
    g.cyl(lt, (CCX, yh, ZD + 0.0920), "x", 0.0040, 0.040, 12)
    g.box(lt, CCX - 0.016, CCX + 0.016, yh, YT - 0.0012, ZD + 0.0895, ZD + 0.0945)
    g.box(lt, CCX - 0.016, CCX + 0.016, YT - 0.0016, YT, ZD + 0.0820, ZD + 0.1000)
    # needle bushing above the slot ring
    gx, gy = L.NEEDLE_CUP
    lathe(lt, [(0.0062, ZD + 0.0898), (0.0062, ZD + 0.0915), (0.0050, ZD + 0.0926), (0.0026, ZD + 0.0926),
               (0.0026, ZD + 0.0905)], 10, (gx, gy, 0.0))
    parts.append(lt)
    return parts


# =============================================================================
# Dispenser arm and wash cell
# =============================================================================
def build_arm(spec):
    """Post: flange, bellows, chrome column; rotating head with the arm, needle holder, needle and PTFE
    tube - the bone ozl_arm (the model pose is mid-swing); wash cell."""
    lod = spec["lod"]
    if lod == 2:
        return []
    d = Vector((math.cos(math.radians(L.ANG_MID)), math.sin(math.radians(L.ANG_MID)), 0.0))
    fr = g.Frame((PX, PY, ZD + 0.120), d, Vector((-d.y, d.x, 0.0)), (0, 0, 1))
    nx, ny = L.arm_point(L.ANG_MID)
    c0 = (PX, PY, 0.0)
    if lod == 1:
        st = P("arm_post", "case")
        g.cyl(st, (PX, PY, ZD + 0.070), "z", 0.016, 0.140, 8)
        am = P("arm", "case_dark", group=SEL_ARM)
        g.box(am, -0.012, L.ARM_L + 0.012, -0.0115, 0.0115, 0.002, 0.0245, frame=fr)
        ws = P("wash", "case_dark")
        wx, wy = L.NEEDLE_WASH
        g.box(ws, wx - 0.015, wx + 0.015, wy - 0.015, wy + 0.015, ZD - 0.001, ZD + 0.012)
        return [st, am, ws]
    base = P("arm_base", "case_dark")
    lathe(base, [(0.024, ZD), (0.024, ZD + 0.004), (0.0215, ZD + 0.0065), (0.0170, ZD + 0.0065)], 16, c0)
    boot = P("arm_boot", "rubber")
    prof = [(0.0170 if k % 2 == 0 else 0.0142, ZD + 0.0065 + k * 0.0054) for k in range(8)]
    lathe(boot, prof + [(0.0105, prof[-1][1])], 12, c0)
    col = P("arm_column", "chrome")
    lathe(col, [(0.0105, ZD + 0.040), (0.0105, ZD + 0.118)], 16, c0)
    hd = P("arm_head", "case_dark", group=SEL_ARM)
    lathe(hd, [(0.0185, ZD + 0.116), (0.0195, ZD + 0.1185), (0.0195, ZD + 0.1420), (0.0170, ZD + 0.1465),
               (0.0090, ZD + 0.1480), (0.0, ZD + 0.1480)], 16, c0)
    rbox(hd, fr, -0.006, L.ARM_L + 0.012, -0.0115, 0.0115, 0.004, 0.0245, 0.006, 2)
    hl = P("arm_holder", "black", group=SEL_ARM)
    lathe(hl, [(0.0016, ZD + 0.1080), (0.0042, ZD + 0.1090), (0.0055, ZD + 0.1120), (0.0055, ZD + 0.1250)], 12,
          (nx, ny, 0.0))
    nd = P("needle", "needle", group=SEL_ARM)
    lathe(nd, [(0.0, ZD + 0.0962), (0.0009, ZD + 0.0970), (0.0009, ZD + 0.1085)], 6, (nx, ny, 0.0))
    tb = P("arm_tube", "ptfe", group=SEL_ARM)
    pts = [fr.p(L.ARM_L, 0.0, 0.0230), fr.p(L.ARM_L - 0.004, 0.002, 0.0300), fr.p(L.ARM_L - 0.020, 0.008, 0.0365),
           fr.p(0.065, 0.011, 0.0370), fr.p(0.030, 0.009, 0.0340), fr.p(0.010, 0.004, 0.0310),
           fr.p(0.002, 0.0, 0.0270)]
    g.pipe(tb, L.spline([tuple(q) for q in pts], 2), 0.0013, 6)
    # wash cell: block, steel ring, dark well
    wx, wy = L.NEEDLE_WASH
    ws = P("wash", "case_dark")
    g.box(ws, wx - 0.015, wx + 0.015, wy - 0.015, wy + 0.015, ZD - 0.001, ZD + 0.012, r=0.003, seg=1)
    wl = P("wash_well", "steel")
    lathe(wl, [(0.0085, ZD + 0.0121), (0.0052, ZD + 0.0121), (0.0048, ZD + 0.0060), (0.0, ZD + 0.0060)], 14,
          (wx, wy, 0.0), regs=["steel", "dark", "dark"])
    return [base, boot, col, hd, hl, nd, tb, ws, wl]


# =============================================================================
# Keypad, printer, tape
# =============================================================================
def build_keypad(spec):
    """Keypad frame on the slope, key caps with symbols (digits, functions, start and stop on two rows),
    LEDs "measuring" (yellow, ozl_lamp) and "power", operator lock."""
    lod = spec["lod"]
    if lod == 2:
        return []
    a0, a1, b0, b1 = L.KEYPAD
    pn = P("keypad", "case_dark")
    g.box(pn, a0, a1, b0, b1, -0.001, L.KEY_C0, frame=KEYS_FR, **R(0.0015, 1, lod))
    parts = [pn]
    if lod == 1:
        kb = P("keys", "key")
        for b in L.KEY_ROWS:
            g.box(kb, L.NUM_COLS[0] - L.KEY_W / 2, L.FUN_COLS[-1] + L.KEY_W / 2, b - L.KEY_H / 2, b + L.KEY_H / 2,
                  L.KEY_C0, L.KEY_C1, frame=KEYS_FR)
        return parts + [kb]
    kp = {}
    for a, b, w, h, kind, _leg in L.keys():
        if kind not in kp:
            kp[kind] = P("keys_" + kind, kind)
        keycap(kp[kind], KEYS_FR, a, b, w, h, L.KEY_C0, L.KEY_C1, 0.0012)
    parts += list(kp.values())
    for (a, b), reg, grp in ((L.LED_RUN, "led_amber", SEL_LAMP), (L.LED_PWR, "lamp_g", "body")):
        ld = P("keypad_" + reg, reg, group=grp)
        lathe(ld, [(0.0028, 0.0), (0.0028, 0.0010), (0.0020, 0.0024), (0.0, 0.0029)], 10,
              tuple(KEYS_FR.p(a, b, L.KEY_C0)), axis=tuple(KEYS_FR.n))
        parts.append(ld)
    a, b = L.KEYLOCK
    kl = P("keylock", "chrome")
    lathe(kl, [(0.0068, 0.0), (0.0068, 0.0030), (0.0058, 0.0042), (0.0, 0.0044)], 16,
          tuple(KEYS_FR.p(a, b, L.KEY_C0)), axis=tuple(KEYS_FR.n))
    ks = P("keylock_slot", "dark")
    g.box(ks, a - 0.0010, a + 0.0010, b - 0.0035, b + 0.0035, L.KEY_C0 + 0.0040, L.KEY_C0 + 0.0046, frame=KEYS_FR)
    return parts + [kl, ks]


def build_printer(spec):
    """Built-in printer: cover, slot, toothed tear-off blade, roll window, feed button, LED."""
    lod = spec["lod"]
    if lod == 2:
        return []
    x0, x1, y0, y1 = L.PRINTER
    zt = ZD + L.PRINTER_H
    pr = P("printer", "case_dark")
    g.box(pr, x0, x1, y0, y1, ZD - 0.001, zt, **R(0.004, 2, lod))
    sx0, sx1, sy0, sy1 = L.SLOT
    sl = P("printer_slot", "black")
    g.box(sl, sx0, sx1, sy0, sy1, zt - 0.0003, zt + 0.0006)
    parts = [pr, sl]
    if lod == 1:
        return parts
    tb = P("tear_bar", "steel")
    n = 12
    xa, xb = sx0 - 0.002, sx1 + 0.002
    poly = [(xa, zt), (xb, zt)] + [(xa + (xb - xa) * k / (2 * n), zt + (0.0034 if k % 2 == 0 else 0.0022))
                                   for k in range(2 * n, -1, -1)]
    g.prism(tb, poly, (0, 2), sy0 - 0.0016, sy0 - 0.0004)
    wn = P("printer_window", "window")
    g.box(wn, 0.255, 0.335, -0.098, -0.046, zt - 0.0002, zt + 0.0004)
    bt = P("printer_button", "key")
    lathe(bt, [(0.0050, zt), (0.0050, zt + 0.0025), (0.0042, zt + 0.0036), (0.0, zt + 0.0038)], 14, (0.250, -0.152, 0.0))
    ld = P("printer_led", "lamp_g")
    lathe(ld, [(0.0022, zt), (0.0022, zt + 0.0008), (0.0015, zt + 0.0020), (0.0, zt + 0.0024)], 10, (0.250, -0.128, 0.0))
    return parts + [tb, wn, bt, ld]


def build_tape(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    tp = P("tape", "tape")
    tape_strip(tp, L.spline(L.TAPE_PATH, 3 if lod == 0 else 1))
    return [tp]


# =============================================================================
# Small items on the worktop and cables
# =============================================================================
TUBES = [(-0.195, "cap_r", "tube_a"), (-0.165, "cap_y", "tube_b"), (-0.105, "cap_v", "tube_a"),
         (-0.075, "cap_g", "tube_b")]          # y, cap, content; slots -0.135 and -0.045 are empty


def build_props(spec):
    """Rack with vacuum tubes (front left), wash bottle (left), dark glass bottle (right)."""
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    rx0, rx1, ry0, ry1 = -0.466, -0.414, -0.215, -0.025
    if lod == 0:
        for nm, z0, z1 in (("rack_base", ZB, ZB + 0.004), ("rack_mid", ZB + 0.030, ZB + 0.033),
                           ("rack_top", ZB + 0.056, ZB + 0.060)):
            rk = P(nm, "rack")
            g.box(rk, rx0, rx1, ry0, ry1, z0, z1, r=0.0012, seg=1)
            parts.append(rk)
        for k, (y0, y1) in enumerate(((ry0, ry0 + 0.004), (ry1 - 0.004, ry1))):
            rk = P("rack_end%d" % k, "rack", uv_name="rack_end", uv_origin=(0.0, y0, 0.0))
            g.box(rk, rx0, rx1, y0, y1, ZB + 0.004, ZB + 0.056)
            parts.append(rk)
    else:
        rk = P("rack", "rack")
        g.box(rk, rx0, rx1, ry0, ry1, ZB, ZB + 0.060)
        parts.append(rk)
    for k, (y, cap, cont) in enumerate(TUBES):
        c = ((rx0 + rx1) / 2, y, 0.0)
        tb = P("tube%d" % k, cont, uv_name="tube", uv_origin=c)
        tc = P("tube_cap%d" % k, cap, uv_name="tube_cap", uv_origin=c)
        if lod == 0:
            lathe(tb, [(0.0065, ZB + 0.0060), (0.0065, ZB + 0.0990)], 10, c)
            lathe(tc, [(0.0068, ZB + 0.0960), (0.0082, ZB + 0.0975), (0.0082, ZB + 0.1135), (0.0074, ZB + 0.1155),
                       (0.0, ZB + 0.1160)], 10, c)
        else:
            lathe(tb, [(0.0065, ZB + 0.006), (0.0065, ZB + 0.099)], 6, c)
            lathe(tc, [(0.0082, ZB + 0.096), (0.0082, ZB + 0.116), (0.0, ZB + 0.116)], 6, c)
        parts += [tb, tc]
    # wash bottle: soft bottle, red cap, bent spout
    wx, wy = -0.44, 0.08
    wb = P("wash_bottle", "ldpe")
    if lod == 0:
        lathe(wb, [(0.0, ZB), (0.0280, ZB), (0.0310, ZB + 0.004), (0.0320, ZB + 0.014), (0.0320, ZB + 0.104),
                   (0.0290, ZB + 0.121), (0.0200, ZB + 0.133), (0.0125, ZB + 0.138), (0.0125, ZB + 0.145)], 14, (wx, wy, 0.0))
        cp = P("wash_cap", "cap_r")
        lathe(cp, [(0.0150, ZB + 0.143), (0.0150, ZB + 0.157), (0.0132, ZB + 0.160), (0.0060, ZB + 0.1615)], 14,
              (wx, wy, 0.0))
        nz = P("wash_nozzle", "ldpe")
        pts = L.spline([(wx, wy, ZB + 0.158), (wx, wy, ZB + 0.182), (wx, wy - 0.006, ZB + 0.197),
                        (wx, wy - 0.022, ZB + 0.203), (wx, wy - 0.040, ZB + 0.197), (wx, wy - 0.050, ZB + 0.186)], 2)
        g.tube_var(nz, pts, [(0.0034 - 0.0018 * i / (len(pts) - 1),) * 2 for i in range(len(pts))], 6)
        parts += [wb, cp, nz]
    else:
        lathe(wb, [(0.032, ZB), (0.032, ZB + 0.12), (0.0125, ZB + 0.145), (0.0, ZB + 0.160)], 8, (wx, wy, 0.0))
        parts.append(wb)
    # dark glass bottle with a label and a knurled cap
    bx, by = 0.44, 0.15
    rb = P("reagent_bottle", "glass_brown")
    if lod == 0:
        lathe(rb, [(0.0, ZB), (0.0290, ZB), (0.0320, ZB + 0.004), (0.0320, ZB + 0.030), (0.0320, ZB + 0.075),
                   (0.0320, ZB + 0.088), (0.0290, ZB + 0.100), (0.0180, ZB + 0.110), (0.0135, ZB + 0.113),
                   (0.0135, ZB + 0.124)], 18, (bx, by, 0.0),
              regs=["glass_brown"] * 3 + ["label"] + ["glass_brown"] * 5)
        ck = P("reagent_bottle_cap", "black")
        knurl(ck, bx, by, ZB + 0.121, ZB + 0.139, 0.0155, 16, 0.0007)
        parts += [rb, ck]
    else:
        lathe(rb, [(0.032, ZB), (0.032, ZB + 0.09), (0.0135, ZB + 0.115), (0.0135, ZB + 0.139), (0.0, ZB + 0.139)], 8,
              (bx, by, 0.0))
        parts.append(rb)
    return parts


def build_cables(spec):
    """Mains cord and RS-232 cable - smoothly from the connectors behind the cabinet and along the floor."""
    lod = spec["lod"]
    if lod == 2:
        return []
    k, sides = (2, 6) if lod == 0 else (1, 4)
    pw = P("cable_power", "black")
    g.pipe(pw, L.spline([(0.250, AY1 + 0.064, 1.060), (0.250, AY1 + 0.074, 1.052), (0.246, CY1 + 0.012, 1.020),
                         (0.243, CY1 + 0.014, 0.900), (0.240, CY1 + 0.013, 0.600), (0.236, CY1 + 0.015, 0.200),
                         (0.232, CY1 + 0.020, 0.030), (0.245, CY1 + 0.050, 0.0042), (0.290, CY1 + 0.110, 0.0042)], k),
           0.0042, sides)
    sr = P("cable_serial", "cable_grey")
    g.pipe(sr, L.spline([(0.040, AY1 + 0.018, 1.090), (0.040, AY1 + 0.030, 1.086), (0.044, CY1 + 0.013, 1.050),
                         (0.050, CY1 + 0.015, 0.900), (0.058, CY1 + 0.014, 0.500), (0.064, CY1 + 0.017, 0.120),
                         (0.066, CY1 + 0.023, 0.020), (0.050, CY1 + 0.060, 0.0036), (-0.020, CY1 + 0.110, 0.0036)], k),
           0.0036, sides)
    return [pw, sr]


def build_lod(spec):
    parts = build_cabinet(spec) + build_body(spec) + build_tower(spec) + build_back(spec) + build_carousel(spec)
    parts += build_arm(spec) + build_keypad(spec) + build_printer(spec) + build_tape(spec) + build_props(spec)
    parts += build_cables(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    return parts


def collision():
    lower = kx.box_pts(CX0 - 0.01, CX1 + 0.01, CY0 - 0.01, CY1 + 0.01, 0.0, ZD)
    tower = kx.box_pts(AX0, AX1, YT, AY1, ZD, ZT)
    comps = [(lower + tower, kx.PEN + r"\plastic.rvmat")]
    memory = {
        "invView": [(0.0, -2.2, 1.0)],
        "ce_center": [(0.0, 0.0, ZT / 2)],
        "ce_radius": [(0.8, 0.0, ZT / 2)],
        "ozl_work_axis": [(CCX, CCY, ZD), (CCX, CCY, ZD + 0.1)],
        "ozl_arm_axis": [(PX, PY, ZD + 0.10), (PX, PY, ZD + 0.20)],
    }
    bbox = (CX0 - 0.01, CX1 + 0.01, CY0 - 0.03, CY1 + 0.01, 0.0, ZT + 0.004)
    return comps, 120.0, memory, bbox


# the first five are the --look preview (the work look uses the first two): overview, carousel with arm
# and display, keypad and printer, tape close-up, back wall
SHOTS = [
    ("front", (-1.3, -2.1, 1.6), (0.0, 0.0, 0.85), 32),
    ("carousel", (-0.52, -0.80, 1.40), (CCX + 0.07, CCY + 0.01, ZD + 0.05), 38),
    ("printer", (0.95, -0.95, 1.32), (0.22, -0.13, 0.96), 40),
    ("keys", (0.30, -0.70, 1.16), (0.18, -0.24, 0.93), 45),
    ("back", (1.3, 1.8, 1.5), (0.0, 0.0, 0.85), 32),
    ("top", (0.15, -1.0, 1.75), (0.0, -0.02, 1.0), 32),
    ("left", (-1.15, -0.55, 1.20), (-0.42, 0.0, 0.88), 40),
]

M.look_shots = (5, 2)
M.run(build_lod, collision, SHOTS, row_step=1.4, row_shot=((1.4, -4.6, 1.8), (1.4, 0, 0.65)))
