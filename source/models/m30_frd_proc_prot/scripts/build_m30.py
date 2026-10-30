"""M30 - Freedom's gas mask test stand: Protection Sample Analyzer of Freedom (OZL_Frd_Proc_Prot).
An analyzer: 4x4 cargo, no modules. The sample socket is a mannequin head under a transparent dome.

    blender --background --python build_m30.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (decals on the table apron, the
control unit and the compressor receiver, the gauge dial, the display "off" and the "working" frames).
The layout is in layout.py (shared with make_decals.py), the primitives are in m30_geo.py.

The prop is a gas mask leak test stand. A metal table with a shelf; on the table a mannequin head in a
gas mask under a transparent dome on a round base, hoses from the base to a control unit with a gauge,
a display, valves, toggles and a lamp; on the shelf a compressor, spare filters and a gas mask.
1.00 x 1.37 x 0.60 m.

Sources and sizes:
- the real device is a mask leakage tester JSMLT (Joint Service Mask Leakage Tester, ATI TDA-99M) of
  the US Air Force and Navy: a mask on a mannequin head under a transparent dome, a unit with a
  display, hoses (photos: a mask test, a mannequin head with a hose, a unit with a dome). There are no
  datasheet sizes (neither for the JSMLT nor for the ATI TDA-99M/99B); from photos the dome is
  ~dia. 0.35-0.4, the benchtop unit ~0.5 x 0.4. Here the dome is dia. 0.35 x 0.45, the base dia. 0.41 x 0.04; the
  floor-standing ATI 99B is 762 x 1321 x 914 mm (from search results, unverified) - a hint of the
  overall height;
- the table is a metal laboratory table 1000 x 600, height 850 (an ordinary range of lab furniture):
  the tabletop is a sheet with a downward flange of 28 mm and an overhang of 15 mm, the legs are
  35 x 35 tube with rounded corners on adjustable feet (a stud, a nut, a rubber heel), a bolted
  apron, the shelf at 0.20;
- the mannequin head is a smooth blank without a face (as in M29): the neck on a chrome flange is
  visible, on the head a GP-5 class mask - a rubber helmet-mask ~0.19 x 0.21 x 0.29 (an own smooth
  shell: the vanilla GP5GasMask_g is the "lying on the ground" model, flattened by its LOD extents to
  0.12-0.21 thick against ~0.27 for the worn one; it cannot be put on a head under the dome), dia. 45
  lenses in metal rims, a valve box with a threaded neck; for the test the filter is taken off (it
  stands on the table - vanilla), in its place an adapter with a fitting and a tube to the base;
- the dome is 4 mm acrylic with a flange, held on the base by four folding latches, a handle on top;
- the gauge is a dia. 100 dial (a row of GOST 2405 cases: 40, 50, 63, 100, 160), a 0-6 scale over 270
  degrees, a chrome rim, glass;
- the display is a 3-digit LCD 90 x 34 mm in a frame (a homemade unit, an estimate);
- the compressor is a desktop piston one with a 3 l receiver of the Fengda AS-186 class:
  310 x 135 x 310 mm, 5 kg: a receiver dia. 0.124 along the width on stamped feet with a drain cock, on it
  a motor with a fan behind a grille (on the left), a crankcase, a finned cylinder with a head on
  bolts, a copper tube to a block with a dia. 40 gauge, a regulator, a safety valve and a moisture
  separator, a carrying handle, a rocker switch;
- the control unit 0.32 x 0.24 x 0.18 (homemade, an estimate): a case in gray hammer-finish enamel, an
  aluminum panel on screws, valves with dia. 0.04 handwheels, toggles, a lamp, louvers on the left side.
Vanilla DayZ items (proxies): on the shelf a spare GP-5 gas mask, two GP-5 filters, rags; on the table
a filter taken off the mask, tape, a screwdriver, pliers.

The Freedom look (as in M27/M28): a bright green table (no olive), rubbed to metal on the edges and
where it is worked on; decals overlap on the apron, the unit and the compressor (a peace sign and
LEGALIZE), some with short English words (CAUTION, FRAGILE, HIGH PRESSURE, NO OIL, ...; allowed on
Freedom only); the hose is taped with blue tape; dusty, no rust (build_scuffed is from M27). Detail:
the "dayz" look, no angularity, small items more detailed or from DayZ, "working" is a loop.

Working look: ozl_lamp is the unit lamp (blinks when "working", _on atlas); the display is ozl_screen,
an own texture (section lcd): "off" - a dark LCD, "working" - pressure frames _lcd_fNN (frames); the
needles of the unit and compressor gauges are the bones ozl_needle and ozl_cneedle on one source
ozl_needle (wobble: they tremble around 2.4 and 4 divisions); the compressor motor fan is the bone
ozl_work on the source ozl_work: a model.cfg loop (sourceAddress loop, maxValue 1/3) - 3 turns per
2 s pass, 1.5 rev/s: six blades advance by 18 degrees per frame at 30 fps (less than half of the blade
pitch - the rotation does not appear to go backward). The mask "breathes": the stand inflates it and
lets the air out - the cheeks and temples swell and sag; bubbles under the shell (bones
ozl_puff_1..4 on the source ozl_breath, wobble), details at PUFFS. LODs: the mid LOD has no small
stuff or bubbles, the far one has no glass, hoses or shelf props.

Blender axes: X is width, Y is depth (the face looks to -Y), Z is up.
"""
import math
import os
import sys

from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import krender  # noqa: E402
import kvanilla as kv  # noqa: E402
import layout as L  # noqa: E402
from m30_geo import (along, bev, face, front_quad, lathe, rod, shell, shell_dims, shell_normal,  # noqa: E402
                     shell_point, spline, torus, turn, upright)

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m (the rest is in layout.py)
# =============================================================================
TX0, TX1, TY0, TY1, ZT, ZA, ZS, LEG = L.TX0, L.TX1, L.TY0, L.TY1, L.ZT, L.ZA, L.ZS, L.LEG
LX0, LX1, LY0, LY1 = L.LX0, L.LX1, L.LY0, L.LY1
DX, DY, ZB = L.DX, L.DY, L.ZB
BX0, BX1, BY0, BY1, BZ0, BZ1 = L.BLK
YP = BY0 - 0.002                                             # face of the aluminum unit panel
GX, GZ = L.GAUGE
GR = L.GAUGE_D / 2
G_FACE = YP - 0.002                                          # dial
G_NEEDLE = (YP - 0.0048, YP - 0.0036)                        # needle: y at the front, at the back
G_GLASS = YP - 0.0075
NEEDLE0 = math.radians(225.0)                                # scale zero: down-left (in x, z axes)
NEEDLE_SPAN = math.radians(270.0)                            # phase 1 is the whole scale (6 divisions)
NEEDLE_MID = 0.40                                            # when "working" - 2.4 divisions (wobble mid)
CNEEDLE_READ = 4.0                                           # compressor gauge when "working" - 4 divisions
CNEEDLE_SPAN = math.radians(270.0 * CNEEDLE_READ / 6.0) / NEEDLE_MID
FAN_TURNS = 3                                                # fan turns per loop pass
CMX, CMY = L.CMX, L.CMY
TANK_R, TANK_Z = L.TANK_R, L.TANK_Z
MX0, MX1, MZ, MR = L.MOTOR
CGX, CGY, CGZ = L.CGAUGE
CG_R = L.CGAUGE_D / 2
CG_FACE = CGY + 0.0015                                       # compressor gauge dial
FITS = ((DY - 0.05, ZT + 0.02), (DY + 0.04, ZT + 0.026))     # base fittings on the right: y, z
NIPS = ((-0.07, BZ0 + 0.05), (0.03, BZ0 + 0.075))            # unit fittings on the left: y, z
BACK_FIT = (0.40, BZ0 + 0.06)                                # fitting on the back of the unit: x, z
GLAND = (0.25, BZ0 + 0.03)                                   # unit power cable entry: x, z
TUBE_FIT = (DX + 0.075, DY - 0.115)                          # mask tube fitting on the base
OUTLET = (L.CGAUGE[0] + 0.0555, CMY, L.TANK_Z + L.TANK_R + 0.034)   # compressor outlet (the start of the barb)

LOD_SPECS = [
    dict(lod=0, sides=16),
    dict(lod=1, sides=8),
    dict(lod=2, sides=6),
]

REGIONS = {
    "top": ("top", 0.9), "apron": ("apron", 1.4), "frame": ("frame", 0.9), "shelf": ("shelf", 0.9),
    "feet": ("rubber", 0.8), "chrome": ("chrome", 1.6), "zinc": ("zinc", 1.6), "base": ("base", 1.3),
    "head": ("head", 1.4), "mask": ("mask", 1.8), "mask_ring": ("mask_ring", 2.5), "lens": ("lens", 2.5),
    "mask_puff": ("mask_puff", 1.8),
    "valve": ("valve", 2.0), "blk": ("blk", 1.6), "panel": ("panel", 1.8), "gauge_face": ("gauge_face", 4.0),
    "needle": ("needle", 2.0), "lamp": ("lamp_off", 2.5), "toggle": ("black", 1.6), "lcd": ("black", 1.0),
    "wheel_red": ("cap_red", 1.6), "wheel_black": ("black", 1.6), "hose_amber": ("hose_amber", 1.4),
    "hose": ("hose", 1.2), "tube": ("tube", 1.6), "cable": ("cable", 1.0), "tape": ("tape", 1.6),
    "comp_tank": ("comp_tank", 1.5), "comp_body": ("comp_body", 1.4), "comp_alu": ("alu", 1.6),
    "brass": ("brass", 2.0), "copper": ("copper", 2.0), "grille": ("grille", 2.0), "fan": ("fan", 1.6),
    "rocker": ("cap_red", 2.0), "bowl": ("tube", 2.0),
}

# =============================================================================
# Materials
# =============================================================================


def build_scuffed(mat, origin, color, bare=kmats.lin((112, 112, 116)), seed=1.0, gloss=0.32, spec=0.25,
                  wear=(0.66, 0.71), edge_k=0.7, rub=(), scratch=0.0, floor_z=0.0, dust=0.3, grime=0.3,
                  decal_items=()):
    """Scuffed, careless paint (plastic) without rust - the M27 builder, without stripes and oil: rubbed to
    the base on the edges (edge_k) and where hands take it (rub - [(center, semi-axes, strength)]),
    scratches along x; decals go over the wear (the decal itself is already worn in the PNG), dust and
    grime go over everything."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    col = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                 tuple(c * 0.9 for c in color[:3]) + (1,), color)
    edge = t.maprange(t.edge_wear(0.004), 0.05, 0.22, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 11.0, 10.0, 0.7), 0.75), t.math("MULTIPLY", edge, edge_k))
    grain = t.maprange(t.noise(vec, 34.0, 8.0, 0.7), 0.3, 0.7, 0.55, 1.0)
    for c, r, k in rub:
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
        near = t.maprange(ln.outputs["Value"], 0.25, 1.0, 1.0, 0.0)
        f = t.math("ADD", f, t.math("MULTIPLY", t.math("MULTIPLY", near, grain), k))
    worn = t.step(f, wear[0], wear[1])
    brush = t.noise(t.stretch(vec, 0.04, 1.0, 1.0), 90.0, 4.0, 0.7)
    metal = t.mixc(t.maprange(brush, 0.3, 0.7, 0.0, 1.0), tuple(c * 0.75 for c in bare[:3]) + (1,),
                   tuple(min(1.0, c * 1.15) for c in bare[:3]) + (1,))
    rim = t.math("SUBTRACT", t.step(f, wear[0] - 0.05, wear[0]), worn)
    col = t.mixc(t.math("MULTIPLY", rim, 0.6), col, kmats.lin((52, 50, 46)))
    col = t.mixc(worn, col, metal)
    h = t.math("MULTIPLY", worn, -0.3)
    g_ = t.math("ADD", gloss, t.math("MULTIPLY", worn, 0.62 - gloss))
    s_ = t.math("ADD", spec, t.math("MULTIPLY", worn, 0.70 - spec))
    if scratch > 0:
        sc = t.step(t.noise(t.stretch(vec, 0.02, 1.0, 1.0), 260.0, 2.0, 0.5), 0.70, 0.73)
        sc = t.math("MULTIPLY", sc, t.maprange(t.noise(vec, 5.0, 4.0, 0.5), 0.35, 0.65, 0.0, scratch))
        col = t.mixc(t.math("MULTIPLY", sc, 0.7), col, metal)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", sc, 0.15))
    col = kmats.decals(t, col, sep, nsep, decal_items)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g_, s_, h)


def wdecal(name):
    return os.path.join(WORK, name)


def decal_y(name, x0, x1, z0, z1, ya, yb):
    """Decal on faces facing -y between ya and yb (the projection depth)."""
    return (wdecal(name), "y", -1, ("x", "z"), ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0), (ya, yb))


def decal_x(name, y0, y1, z0, z1, x):
    return (wdecal(name), "x", 1, ("y", "z"), ((y0 + y1) / 2, (z0 + z1) / 2), (y1 - y0, z1 - z0),
            (x - 0.002, x + 0.002))


def decal_z(name, x0, x1, y0, y1, z):
    return (wdecal(name), "z", 1, ("x", "y"), ((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0, y1 - y0),
            (z - 0.002, z + 0.002))


APRON_DECALS = [decal_y("decal_apron_f.png", *L.APRON_F, LY0 - 0.002, LY0 + 0.002),
                decal_x("decal_apron_r.png", *L.APRON_R, LX1)]
BLK_DECALS = [decal_z("decal_blk_top.png", *L.BLK_TOP, BZ1), decal_x("decal_blk_side.png", *L.BLK_SIDE, BX1)]
COMP_DECAL = decal_y("decal_comp.png", *L.COMP_FRONT, CMY - TANK_R - 0.004, CMY - 0.03)
GAUGE_DECALS = [decal_y("decal_gauge.png", GX - GR, GX + GR, GZ - GR, GZ + GR, G_FACE - 0.002, G_FACE + 0.001),
                decal_y("decal_gauge.png", CGX - CG_R, CGX + CG_R, CGZ - CG_R, CGZ + CG_R, CG_FACE - 0.002,
                        CG_FACE + 0.001)]

GREEN = kmats.lin((62, 152, 44))
GREEN_BARE = kmats.lin((150, 150, 154))
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# the tabletop is worn in front of the dome and the unit (that is where people work), the shelf - where things stand
TOP_RUB = [((DX, -0.22, ZT), (0.20, 0.08, 0.02), 0.30), ((0.29, -0.20, ZT), (0.14, 0.07, 0.02), 0.26),
           ((0.0, TY0, ZT), (0.45, 0.02, 0.02), 0.2)]
SHELF_RUB = [((CMX, CMY, ZS), (0.17, 0.09, 0.02), 0.35), ((-0.32, -0.10, ZS), (0.16, 0.12, 0.02), 0.3)]
PAINT = dict(color=GREEN, bare=GREEN_BARE, gloss=0.32, spec=0.25, edge_k=0.8)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "top": (build_scuffed, dict(PAINT, seed=1.3, wear=(0.70, 0.75), rub=TOP_RUB, scratch=0.8, floor_z=ZT - 0.2,
                                dust=0.35, grime=0.25)),
    "apron": (build_scuffed, dict(PAINT, seed=1.9, wear=(0.70, 0.76), scratch=0.5, floor_z=0.0, dust=0.3,
                                  grime=0.3, decal_items=APRON_DECALS)),
    "frame": (build_scuffed, dict(PAINT, seed=2.5, wear=(0.71, 0.77), scratch=0.3, floor_z=0.0, dust=0.3, grime=0.45)),
    "shelf": (build_scuffed, dict(PAINT, seed=3.1, wear=(0.70, 0.76), rub=SHELF_RUB, scratch=0.5, floor_z=0.0,
                                  dust=0.5, grime=0.4)),
    "chrome": ("steel", dict(seed=3.7, tone=0.34, along="z", gloss=0.75, spec=0.85, dust=0.1, grime=0.2)),
    "zinc": ("steel", dict(seed=3.9, tone=0.28, along="z", gloss=0.45, spec=0.5, dust=0.25, grime=0.45)),
    "base": ("plastic", dict(color=kmats.lin((30, 30, 32)), gloss=0.35, spec=0.25, dust=0.4, grime=0.2,
                             scuff=(0.66, 0.74))),
    # the head is a smooth blank without a face (as in M29), the mask is black matte rubber
    "head": ("plastic", dict(color=kmats.lin((196, 182, 160)), gloss=0.3, spec=0.2, mottle=0.05, dust=0.2,
                             grime=0.2)),
    "mask": ("plastic", dict(color=kmats.lin((36, 38, 38)), gloss=0.20, spec=0.12, mottle=0.14, dust=0.35,
                             grime=0.25, scuff=(0.70, 0.78))),
    # "breathing" bubbles (bones ozl_puff_*): the same rubber, but at rest they are under the shell and bake
    # almost without light (AO ~0: color x0.4 against ~x0.7-1.0 for the shell beside them). The "plastic"
    # rubber does not suit them: its grime in corners (weather: cavity, AO over 4 cm) sees the shell above
    # a bubble and lays grime almost everywhere - the color of a bubble hardly depends on the base color
    # (x1.5 and x1.75 gave the same in the atlas, dark blotches on inhale). So a flat color without layers:
    # the tone of the shell around the bubbles in the baked _co (linear 0.059, gray) / 0.4 (AO) / 0.95
    # (the build_flat mean)
    "mask_puff": ("flat", dict(color=(0.155, 0.156, 0.155, 1.0), gloss=0.20, spec=0.12)),
    "mask_ring": ("steel", dict(seed=4.3, tone=0.20, along="z", gloss=0.45, spec=0.5, dust=0.15, grime=0.4)),
    "lens": ("flat", dict(color=kmats.lin((44, 52, 56)), gloss=0.92, spec=0.85)),
    "valve": ("plastic", dict(color=kmats.lin((40, 42, 42)), gloss=0.3, spec=0.25, dust=0.3, grime=0.3,
                              scuff=(0.66, 0.74))),
    # control unit - gray hammer-finish enamel, the top and side in decals; the panel is aluminum
    "blk": (build_scuffed, dict(color=kmats.lin((70, 74, 78)), bare=kmats.lin((150, 150, 154)), seed=5.5,
                                wear=(0.69, 0.75), edge_k=0.9, scratch=0.5, floor_z=BZ0, dust=0.4, grime=0.2,
                                decal_items=BLK_DECALS)),
    "panel": ("steel", dict(seed=5.8, tone=0.42, along="x", gloss=0.4, spec=0.45, floor_z=BZ0, dust=0.3, grime=0.35)),
    "gauge_face": (build_scuffed, dict(color=kmats.lin((228, 226, 216)), seed=6.1, gloss=0.6, spec=0.5,
                                       wear=(0.99, 1.0), edge_k=0.0, dust=0.1, grime=0.0, decal_items=GAUGE_DECALS)),
    "needle": ("flat", dict(color=kmats.lin((20, 20, 20)), gloss=0.5, spec=0.4)),
    "lamp_off": ("flat", dict(color=kmats.lin((34, 64, 40)), gloss=0.85, spec=0.8)),
    "lamp_on": ("flat", dict(color=kmats.lin((130, 255, 140)), gloss=0.85, spec=0.8)),
    "hose_amber": ("plastic", dict(color=kmats.lin((196, 160, 70)), gloss=0.7, spec=0.5, dust=0.25, grime=0.3)),
    "hose": ("plastic", dict(color=kmats.lin((26, 26, 27)), gloss=0.35, spec=0.25, dust=0.35)),
    "tube": ("plastic", dict(color=kmats.lin((214, 212, 196)), gloss=0.7, spec=0.5, dust=0.1)),
    "cable": ("plastic", dict(color=kmats.lin((24, 24, 24)), gloss=0.35, spec=0.25, dust=0.35)),
    "tape": ("plastic", dict(color=kmats.lin((34, 74, 168)), gloss=0.55, spec=0.35, dust=0.15, grime=0.3,
                             scuff=(0.7, 0.78))),
    # compressor: a silver receiver in decals, a black motor, cast aluminum of the crankcase and cylinder
    "comp_tank": (build_scuffed, dict(color=kmats.lin((176, 178, 178)), bare=kmats.lin((120, 120, 124)), seed=7.3,
                                      gloss=0.45, spec=0.4, wear=(0.70, 0.76), edge_k=0.6, scratch=0.4, floor_z=ZS,
                                      dust=0.4, grime=0.3, decal_items=[COMP_DECAL])),
    "comp_body": ("plastic", dict(color=kmats.lin((28, 28, 30)), gloss=0.35, spec=0.25, dust=0.45, grime=0.2,
                                  scuff=(0.7, 0.78))),
    "alu": ("steel", dict(seed=7.9, tone=0.40, along="z", gloss=0.3, spec=0.4, dust=0.35, grime=0.55)),
    "brass": ("paint", dict(CLEAN, color=kmats.lin((156, 128, 70)), gloss=0.55, spec=0.55, dust=0.15, grime=0.3)),
    "copper": ("paint", dict(CLEAN, color=kmats.lin((150, 86, 52)), gloss=0.5, spec=0.5, dust=0.15, grime=0.35)),
    "grille": ("steel", dict(seed=8.3, tone=0.22, along="z", gloss=0.4, spec=0.45, dust=0.4, grime=0.3)),
    "fan": ("plastic", dict(color=kmats.lin((52, 54, 56)), gloss=0.3, spec=0.2, dust=0.5, grime=0.3)),
})

OBJ, NAME = "m30_frd_proc_prot", "ozr_frd_proc_prot"
# Working look: the lamp is ozl_lamp, the display is ozl_screen (own texture, frames); the needles are
# the bones ozl_needle and ozl_cneedle on the source ozl_needle (wobble), the fan is the bone ozl_work (a loop).
SEL_LAMP, SEL_SCREEN = "ozl_lamp", "ozl_screen"
SEL_NEEDLE, SEL_CNEEDLE, SEL_FAN = "ozl_needle", "ozl_cneedle", "ozl_work"
# fan axis - along the motor toward the grille (-x); needle axes - from the dial toward the person (-y)
FAN_O = (MX0 - 0.010, CMY, MZ)
NEEDLE_O = (GX, G_NEEDLE[1], GZ)
CNEEDLE_O = (CGX, CG_FACE - 0.0012, CGZ)
# "working" preview: the needles deflected, the fan rotated (the rotation is in _posed below); does not go into the p3d
ON_MOVE = {}
POSE_ON = {
    SEL_NEEDLE: (NEEDLE_O, (0.0, 1.0, 0.0), NEEDLE_MID * NEEDLE_SPAN),
    SEL_CNEEDLE: (CNEEDLE_O, (0.0, 1.0, 0.0), NEEDLE_MID * CNEEDLE_SPAN),
    SEL_FAN: (FAN_O, (1.0, 0.0, 0.0), math.radians(20.0)),
}
ON = dict(remap={"lamp_off": "lamp_on"}, emissive=(1.0, 1.0, 1.0, 1.0), move=ON_MOVE)
NEEDLE_ANIM = ("ozl_needle_swing", dict(type="rotation", source="ozl_needle", selection=SEL_NEEDLE,
                                        axis="ozl_needle_axis", memory=1, minValue=0.0, maxValue=1.0, angle0=0.0,
                                        angle1=NEEDLE_SPAN))
CNEEDLE_ANIM = ("ozl_cneedle_swing", dict(type="rotation", source="ozl_needle", selection=SEL_CNEEDLE,
                                          axis="ozl_cneedle_axis", memory=1, minValue=0.0, maxValue=1.0, angle0=0.0,
                                          angle1=CNEEDLE_SPAN))
FAN_ANIM = ("ozl_work_fan", dict(type="rotation", source="ozl_work", sourceAddress="loop", selection=SEL_FAN,
                                 axis="ozl_work_axis", memory=1, minValue=0.0, maxValue=1.0 / FAN_TURNS, angle0=0.0,
                                 angle1=2 * math.pi))
# "Breathing" of the mask under the dome: the stand inflates the mask and lets the air out - the rubber
# cheeks and temples swell and sag. The own mask is a smooth shell and a bone cannot stretch it (the
# bones of a static model only move and rotate), so at each place under the shell lies a bubble - a
# piece of the same surface pressed inward by 1.5 mm in the middle and by 7.5 mm at the edge. The bone
# ozl_puff_N moves it outward along the normal by PUFF_D (6 mm): the middle comes out above the shell
# by ~5 mm as a smooth dome ~5 cm across, the edge stays inside (the seam is not visible); at rest the
# bubble is entirely under the shell. All four are on one source ozl_breath (wobble in OZL_Work:
# phase 0 -> 1 -> 0 along a sine)
PUFFS = [(0.112, 38.0, 0.030), (0.112, 142.0, 0.030), (0.195, 12.0, 0.032), (0.195, 168.0, 0.032)]  # h, phi, R
PUFF_D, PUFF_D0, PUFF_D1 = 0.006, 0.0015, 0.0075
SEL_PUFFS = tuple("ozl_puff_%d" % (i + 1) for i in range(len(PUFFS)))
# shift axis - a meter along the bubble normal: offset in meters (like the M25 stream)
PUFF_ANIMS = tuple(("ozl_puff_%d_out" % (i + 1), dict(type="translation", source="ozl_breath", selection=sel,
                                                       axis="ozl_puff_%d_axis" % (i + 1), memory=1, minValue=0.0,
                                                       maxValue=1.0, offset0=0.0, offset1=PUFF_D))
                   for i, sel in enumerate(SEL_PUFFS))
LCD = dict(off="decal_lcd_off.png", frames=["decal_lcd_f%02d.png" % i for i in range(8)], size=256, gloss=0.6)
# vanilla DayZ items as proxies: on the shelf a spare GP-5 (lying, as on the ground), two filters and
# rags; on the table a filter taken off the mask, tape, a screwdriver, pliers
DECOR = [
    kv.put("gp5", (-0.25, 0.115, ZS), **kv.flat(90)),
    kv.put("gp5filter", (-0.385, -0.175, ZS), up=(0, 0, 1), fwd=(0, -1, 0)),
    kv.put("gp5filter", (-0.25, -0.19, ZS), up=(0, 0, 1), fwd=(0, -1, 0)),
    kv.put("rags", (-0.04, -0.17, ZS), **kv.flat(0)),
    kv.put("gp5filter", (-0.425, -0.215, ZT), up=(0, 0, 1), fwd=(0.3, -1, 0)),
    kv.put("ducttape", (0.06, 0.215, ZT), **kv.flat(0)),
    kv.put("screwdriver", (0.14, -0.255, ZT), **kv.flat(172)),
    kv.put("pliers", (0.38, -0.215, ZT), **kv.flat(150)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.84, 0.86, 0.86), clear=0.04, edge=0.12, smudge=0.10, streaks=0.04),
                 selections=(SEL_LAMP, SEL_SCREEN, SEL_NEEDLE, SEL_CNEEDLE, SEL_FAN) + SEL_PUFFS,
                 hidden=(SEL_SCREEN, SEL_LAMP), states={"on": ON},
                 bones=((SEL_NEEDLE, ""), (SEL_CNEEDLE, ""), (SEL_FAN, "")) + tuple((s, "") for s in SEL_PUFFS),
                 animations=(NEEDLE_ANIM, CNEEDLE_ANIM, FAN_ANIM) + PUFF_ANIMS, decor=DECOR, panels={"lcd": LCD},
                 sources={"ozl_work": dict(animPeriod=2.0), "ozl_needle": dict(animPeriod=0.2),
                          "ozl_breath": dict(animPeriod=0.2)})
P = M.part
BOUNDS = {}


def _posed(place):
    """Preview of "working": the parts of groups POSE_ON in the working pose (rotation about the bone
    axis). kmodel only does a shift (move), so the rotation is here, as a wrapper over krender (as in
    M19); it does not go into the p3d - the model.cfg animations do that."""
    def wrapped(parts, *a, **kw):
        obs = place(parts, *a, **kw)
        if kw.get("move") is ON_MOVE:
            for p, ob in zip(parts, obs):
                if p.group in POSE_ON:
                    c, ax, ang = POSE_ON[p.group]
                    loc = Vector(ob.location)
                    c = Vector(c) + loc
                    ob.matrix_world = (Matrix.Translation(c) @ Matrix.Rotation(ang, 4, Vector(ax)) @
                                       Matrix.Translation(-c) @ Matrix.Translation(loc))
        return obs
    return wrapped


krender.place_look = _posed(krender.place_look)
krender.place = _posed(krender.place)


def hose(name, region, pts, r, lod, sides=6, k=4):
    """A smooth-curve hose (near LOD - a spline through the points, mid LOD - coarser)."""
    h = P(name, region)
    if lod == 0:
        g.pipe(h, spline(pts, k), r, sides)
    else:
        g.pipe(h, spline(pts, 1), r, 5)
    return h


def band(part, pts, k, i0, i1, r):
    """Wrapping (tape) or a clamp on a hose: a piece of the same curve thicker than the hose."""
    sp = spline(pts, k)
    g.pipe(part, sp[i0:i1 + 1], r, 6)


def barb(part, o, d, r, n=6):
    """Hose barb along d from o: a neck and two barbs for a hose of (inner) radius r."""
    lathe(part, [(r * 0.9, 0.0), (r * 0.9, 0.004), (r * 1.25, 0.0055), (r * 0.95, 0.009), (r * 1.25, 0.0105),
                 (r * 0.9, 0.015)], n, along(o, d), caps=(False, True))


def hexnut(part, o, d, r, t):
    """Hexagon (a nut, a fitting body) along d."""
    g.cyl(part, (t / 2, 0, 0), "x", r, t, 6, frame=along(o, d))


# =============================================================================
# Table: flanged tabletop, bolted apron, legs on adjustable feet, shelf
# =============================================================================
def build_table(spec):
    lod = spec["lod"]
    tp = P("table_top", "top")
    g.box(tp, TX0, TX1, TY0, TY1, ZT - L.TOP_T, ZT, **bev(lod, 0.006, 2))
    za1 = ZT - L.TOP_T
    if lod == 2:
        ap = P("table_apron", "apron")
        g.box(ap, LX0, LX1, LY0, LY1, ZA, za1)
        aprons = [ap]
    else:
        # each apron board is a part of its own: otherwise the front face and the inside of the back one share
        # an atlas rectangle and the decals get smeared (as in M27)
        aprons = []
        k = 0.02
        # apron boards - between the legs (the leg face and the apron face are in one plane - otherwise the faces flicker)
        xa, xb, ya, yb = LX0 + LEG, LX1 - LEG, LY0 + LEG, LY1 - LEG
        for nm, rg, box in (("front", "apron", (xa, xb, LY0, LY0 + k)), ("back", "frame", (xa, xb, LY1 - k, LY1)),
                            ("left", "frame", (LX0, LX0 + k, ya, yb)), ("right", "apron", (LX1 - k, LX1, ya, yb))):
            ap = P("table_apron_" + nm, rg)
            g.box(ap, *box, ZA, za1, **bev(lod, 0.002, 1))
            aprons.append(ap)
    fr = P("table_legs", "frame")
    z0 = 0.032 if lod == 0 else 0.0
    for x0, x1 in ((LX0, LX0 + LEG), (LX1 - LEG, LX1)):
        for y0, y1 in ((LY0, LY0 + LEG), (LY1 - LEG, LY1)):
            g.box(fr, x0, x1, y0, y1, z0, za1, **bev(lod, 0.005, 2))
    sh = P("table_shelf", "shelf")
    g.box(sh, LX0 + LEG, LX1 - LEG, LY0, LY1, ZS - 0.025, ZS, **bev(lod, 0.004, 2))
    parts = [tp, fr, sh] + aprons
    if lod == 2:
        return parts
    ft = P("table_feet", "feet")
    ch = P("table_bolts", "zinc")
    for x in (LX0 + LEG / 2, LX1 - LEG / 2):
        for y in (LY0 + LEG / 2, LY1 - LEG / 2):
            if lod == 0:
                # adjustable foot: a rubber heel, a stud, a nut under the leg
                lathe(ft, [(0.017, 0.0), (0.020, 0.003), (0.020, 0.009), (0.016, 0.012), (0.008, 0.013)], 10,
                      upright((x, y, 0.0)), caps=(True, True))
                g.cyl(ch, (x, y, 0.019), "z", 0.0055, 0.014, 8)
                g.cyl(ch, (x, y, 0.028), "z", 0.0105, 0.008, 6)
    if lod == 0:
        # apron bolts into the legs: front and right
        for x in (LX0 + LEG / 2, LX1 - LEG / 2):
            for z in (ZA + 0.018, za1 - 0.018):
                hexnut(ch, (x, LY0, z), (0, -1, 0), 0.0062, 0.004)
        # gusset angles of the shelf to the legs
        for x0, x1 in ((LX0 + LEG, LX0 + LEG + 0.04), (LX1 - LEG - 0.04, LX1 - LEG)):
            for y0, y1 in ((LY0, LY0 + 0.003), (LY1 - 0.003, LY1)):
                g.box(fr, x0, x1, y0, y1, ZS - 0.06, ZS - 0.025)
    return parts + [ft, ch]


# =============================================================================
# Dome on the base, mannequin head in a GP-5 class mask
# =============================================================================
# mask shell: (height from the bottom edge, half-width, depth forward, backward) - a rubber helmet-mask
# of the GP-5 class ~0.19 x 0.21 x 0.29, the bottom edge is a bead around the neck
MASK_RINGS = [(0.000, 0.057, 0.058, 0.055), (0.006, 0.061, 0.063, 0.058), (0.012, 0.060, 0.064, 0.058),
              (0.030, 0.066, 0.078, 0.064), (0.060, 0.077, 0.094, 0.077), (0.095, 0.086, 0.102, 0.089),
              (0.130, 0.092, 0.104, 0.097), (0.165, 0.094, 0.102, 0.100), (0.200, 0.091, 0.096, 0.099),
              # crown - along an ellipse (semi-axis 0.087 in height): the rings are denser, the silhouette has no facets
              (0.228, 0.086, 0.089, 0.094), (0.240, 0.081, 0.084, 0.088), (0.252, 0.073, 0.076, 0.080),
              (0.262, 0.064, 0.066, 0.070), (0.270, 0.054, 0.056, 0.059), (0.277, 0.042, 0.044, 0.046),
              (0.282, 0.030, 0.031, 0.033), (0.2855, 0.019, 0.020, 0.021)]
MASK_TOP = 0.2875
MASK_FR = upright((DX, DY + 0.01, L.MASK_Z))
EYE_H, EYE_X = 0.168, 0.034
VALVE_H = 0.072


def dome_prof(r, k):
    """Dome: a cylinder up to DOME_H - DOME_R, on top a quarter ellipse to the top; k steps along the arc."""
    hc = L.DOME_H - L.DOME_R
    prof = [(r, 0.0), (r, hc)]
    for i in range(1, k + 1):
        a = math.radians(90.0 * i / k * 0.93)
        prof.append((r * math.cos(a), hc + r * math.sin(a)))
    return prof


def valve_geo():
    """Valve box: the axis origin, the neck (origin, direction), the end of the adapter fitting."""
    fm = MASK_FR
    _, f, _ = shell_dims(MASK_RINGS, VALVE_H)
    c0 = fm.p(VALVE_H, 0.0, f - 0.012)
    pn = fm.p(VALVE_H - 0.016, 0.0, f + 0.012)
    dn = (fm.n * 0.5 - fm.u * 0.866).normalized()
    return c0, pn, dn, pn + dn * 0.056


def puff_geo(h, deg):
    """A "breathing" bubble on the mask shell (PUFFS): the middle on the shell, the outward normal (the
    bone axis), the shell arc length per unit h and per radian phi - by differences (between rings the
    shell is linear in h)."""
    fm = MASK_FR
    phi = math.radians(deg)
    c = shell_point(fm, MASK_RINGS, h, phi)
    e = 0.002
    th = (shell_point(fm, MASK_RINGS, h + e, phi) - shell_point(fm, MASK_RINGS, h - e, phi)) / (2 * e)
    tp = (shell_point(fm, MASK_RINGS, h, phi + e) - shell_point(fm, MASK_RINGS, h, phi - e)) / (2 * e)
    n = tp.cross(th).normalized()
    if n.dot(c - (fm.o + fm.u * h)) < 0:
        n = -n
    return c, n, th.length, tp.length


PUFF_GEO = [puff_geo(h, deg) for h, deg, _ in PUFFS]
# "working" preview: the bubbles are at the peak of the inhale (kmodel move shift; the needles are rotated by _posed)
ON_MOVE.update({sel: tuple(n * PUFF_D) for sel, (_, n, _, _) in zip(SEL_PUFFS, PUFF_GEO)})


def build_puffs():
    """The "breathing" bubbles (near LOD only; on the mid and far LODs the cheeks do not swell - they
    cannot be seen from afar): a piece of the mask shell of radius R pressed inward along the normal by
    PUFF_D0 in the middle and by PUFF_D1 at the edge (a parabola) - at rest entirely under the shell; the
    bone moves it outward by PUFF_D."""
    fm = MASK_FR
    parts = []
    for sel, (h, deg, R), (c, n, lh, lp) in zip(SEL_PUFFS, PUFFS, PUFF_GEO):
        pt = P("mask_" + sel, "mask_puff", group=sel)
        bm = pt.bm
        phi = math.radians(deg)

        def at(rho, t):
            k = rho / R
            p = shell_point(fm, MASK_RINGS, h + rho * math.cos(t) / lh, phi + rho * math.sin(t) / lp)
            return p - n * (PUFF_D0 + (PUFF_D1 - PUFF_D0) * k * k)
        ns = 12
        mid = bm.verts.new(c - n * PUFF_D0)
        rings = [[bm.verts.new(at(R * k, 2 * math.pi * j / ns)) for j in range(ns)] for k in (0.3, 0.55, 0.78, 1.0)]
        new = []
        for j in range(ns):
            j2 = (j + 1) % ns
            new.append(face(pt, [mid, rings[0][j], rings[0][j2]], n))
            for i in range(len(rings) - 1):
                new.append(face(pt, [rings[i][j], rings[i + 1][j], rings[i + 1][j2], rings[i][j2]], n))
        bm.normal_update()
        pt.tag(new)
        parts.append(pt)
    return parts


def build_mask(lod):
    """GP-5 class mask on the mannequin head: a smooth shell, lenses in rims, a valve box with a neck; for
    the test, instead of the filter - an adapter with a fitting (the tube is in build_dome)."""
    fm = MASK_FR
    mk = P("mask", "mask")
    if lod == 0:
        shell(mk, MASK_RINGS, 24, fm, top=MASK_TOP)
    elif lod == 1:
        shell(mk, [MASK_RINGS[i] for i in (0, 3, 5, 7, 9, 12, 15)], 12, fm, top=MASK_TOP)
    else:
        shell(mk, [MASK_RINGS[i] for i in (0, 4, 7, 11, 15)], 8, fm, top=MASK_TOP)
    parts = [mk]
    if lod == 2:
        return parts
    n = 16 if lod == 0 else 8
    rg = P("mask_rings", "mask_ring")
    ln = P("mask_lens", "lens")
    a = shell_dims(MASK_RINGS, EYE_H)[0]
    for s in (-1, 1):
        phi = math.acos(s * EYE_X / a)
        c = shell_point(fm, MASK_RINGS, EYE_H, phi)
        d = (shell_normal(fm, MASK_RINGS, EYE_H, phi) - fm.u * 0.08).normalized()
        fe = along(c, d)
        if lod == 0:
            # rubber boss around the rim, the rim, the glass
            lathe(mk, [(0.035, -0.006), (0.034, 0.002), (0.031, 0.0045)], n, fe)
            lathe(rg, [(0.0305, 0.002), (0.031, 0.0075), (0.0285, 0.0105), (0.0238, 0.0105), (0.0228, 0.008)], n, fe)
        else:
            lathe(rg, [(0.031, -0.004), (0.031, 0.009), (0.023, 0.009)], n, fe)
        lathe(ln, [(0.0229, 0.0066), (0.0226, 0.0076)], n, fe, caps=(False, True))
    parts += [rg, ln]
    # valve box: the body forward, the exhalation cover, a threaded neck down-forward, an adapter
    vb = P("mask_valve", "valve")
    c0, pn, dn, port = valve_geo()
    fv = along(c0, fm.n)
    nv = 16 if lod == 0 else 8
    lathe(vb, [(0.021, 0.0), (0.0245, 0.004), (0.0245, 0.026), (0.022, 0.031), (0.016, 0.034), (0.010, 0.035)],
          nv, fv, caps=(False, True))
    if lod == 0:
        lathe(rg, [(0.0255, 0.019), (0.0255, 0.024)], nv, fv)                       # crimp ring
    fn = along(pn, dn)
    lathe(vb, [(0.018, -0.004), (0.018, 0.004), (0.0195, 0.006), (0.018, 0.008), (0.0195, 0.010), (0.018, 0.012),
               (0.018, 0.014)] if lod == 0 else [(0.018, -0.004), (0.018, 0.014)], nv, fn)
    ad = P("mask_adapter", "chrome")
    lathe(ad, [(0.0212, 0.012), (0.0212, 0.030), (0.016, 0.034), (0.0068, 0.036)], nv, fn, caps=(False, False))
    if lod == 0:
        barb(ad, pn + dn * 0.036, dn, 0.0034)
    parts += [vb, ad]
    if lod == 0:
        parts += build_puffs()
    return parts


def build_dome(spec):
    lod = spec["lod"]
    n = 24 if lod == 0 else 12 if lod == 1 else 8
    parts = []
    bs = P("dome_base", "base")
    fz = upright((DX, DY, ZT))
    if lod == 0:
        lathe(bs, [(L.BASE_R - 0.007, 0.0), (L.BASE_R - 0.002, 0.0012), (L.BASE_R, 0.005), (L.BASE_R, L.BASE_H - 0.009),
                   (L.BASE_R - 0.0025, L.BASE_H - 0.0025), (L.BASE_R - 0.009, L.BASE_H)], n, fz, caps=(True, True))
    else:
        g.cyl(bs, (DX, DY, ZT + L.BASE_H / 2), "z", L.BASE_R, L.BASE_H, n)
    parts.append(bs)
    # mannequin head: a flange on the base, a neck (the mask sits on it)
    ch = P("dome_hw", "chrome")
    hd = P("dome_head", "head")
    fb = upright((DX, DY, ZB))
    neck_top = L.MASK_Z - ZB + 0.03
    if lod == 0:
        lathe(ch, [(0.046, 0.0), (0.046, 0.005), (0.043, 0.008), (0.040, 0.008)], 20, fb, caps=(False, True))
        lathe(hd, [(0.055, 0.008), (0.0535, 0.014), (0.0515, 0.035), (0.0505, 0.06), (0.0505, neck_top)], 20, fb,
              caps=(False, True))
    else:
        g.cyl(ch, (DX, DY, ZB + 0.004), "z", 0.046, 0.008, n)
        g.cyl(hd, (DX, DY, ZB + 0.008 + (neck_top - 0.008) / 2), "z", 0.052, neck_top - 0.008, n)
    parts += [ch, hd] + build_mask(lod)
    if lod == 2:
        return parts
    # dome: 4 mm acrylic with a flange, the outer and inner surface, the edge at the bottom
    gl = P("dome_glass", "chrome", section="glass")
    lathe(gl, dome_prof(L.DOME_R, 8 if lod == 0 else 3), n, fb, caps=(False, True))
    lathe(gl, [(L.DOME_R + 0.012, 0.0), (L.DOME_R + 0.012, 0.010), (L.DOME_R, 0.010)], n, fb)        # flange
    if lod == 0:
        lathe(gl, dome_prof(L.DOME_R - L.DOME_T, 6), n, fb, inward=True, caps=(False, True))
        lathe(gl, [(L.DOME_R + 0.012, 0.0), (L.DOME_R - L.DOME_T, 0.0)], n, fb, want=-fb.u)
    parts.append(gl)
    # handle on top of the dome
    kb = P("dome_knob", "base")
    lathe(kb, [(0.014, 0.0), (0.017, 0.004), (0.022, 0.011), (0.022, 0.019), (0.018, 0.025), (0.008, 0.027)],
          16 if lod == 0 else 6, upright((DX, DY, ZB + L.DOME_H - 0.004)), caps=(False, True))
    parts.append(kb)
    if lod > 0:
        return parts
    # dome latches: a bracket on the base, a folding lever, a wire hook onto the flange
    for ang in (45.0, 135.0, 225.0, 315.0):
        fr = turn(DX, DY, ZT, ang)
        g.box(ch, L.BASE_R - 0.002, L.BASE_R + 0.007, -0.011, 0.011, 0.008, 0.030, frame=fr, r=0.0015, seg=1)
        pts = [fr.p(u, 0, w) for u, w in ((L.BASE_R + 0.007, 0.026), (L.BASE_R + 0.011, L.BASE_H + 0.004),
                                          (L.BASE_R + 0.006, L.BASE_H + 0.014), (L.DOME_R + 0.020, L.BASE_H + 0.0135))]
        g.sweep(ch, pts, fr.v, 0.0015, 0.0075)
        for s in (-1, 1):
            g.pipe(ch, [tuple(fr.p(L.DOME_R + 0.021, s * 0.006, L.BASE_H + 0.013)),
                        tuple(fr.p(L.DOME_R + 0.006, s * 0.006, L.BASE_H + 0.0118))], 0.0014, 5)
    # hose fittings on the right: a nut and a barb
    for (y, z), rb_ in zip(FITS, (0.0036, 0.0045)):
        hexnut(ch, (DX + L.BASE_R - 0.002, y, z), (1, 0, 0), 0.0085, 0.007)
        barb(ch, (DX + L.BASE_R + 0.005, y, z), (1, 0, 0), rb_)
    # tube from the mask adapter down to the fitting on the base
    fx, fy = TUBE_FIT
    hexnut(ch, (fx, fy, ZB), (0, 0, 1), 0.0075, 0.005)
    barb(ch, (fx, fy, ZB + 0.005), (0, 0, 1), 0.0035)
    _, _, dn, port = valve_geo()
    tb = P("dome_tube", "tube")
    a = Vector(port) - dn * 0.012
    pts = [tuple(a), tuple(a + dn * 0.03), (DX + 0.035, DY - 0.15, ZB + 0.07), (fx - 0.004, fy - 0.012, ZB + 0.035),
           (fx, fy, ZB + 0.016)]
    g.pipe(tb, spline(pts, 4), 0.0045, 6)
    parts.append(tb)
    return parts


# =============================================================================
# Control unit: panel, gauge, display, lamp, toggles, valves, fittings, louvers
# =============================================================================
def build_block(spec):
    lod = spec["lod"]
    parts = []
    bx = P("blk", "blk")
    g.box(bx, BX0, BX1, BY0, BY1, BZ0, BZ1, **bev(lod, 0.006, 2))
    parts.append(bx)
    n = 28 if lod == 0 else 12 if lod == 1 else 8
    # needle (bone ozl_needle): at zero it points down-left; a tail with a counterweight, an axis cap
    nd = P("blk_needle", "needle", group=SEL_NEEDLE)
    c, s = math.cos(NEEDLE0), math.sin(NEEDLE0)
    poly = [(-0.014, -0.0035), (-0.006, -0.0022), (GR * 0.84, -0.0007), (GR * 0.86, 0.0), (GR * 0.84, 0.0007),
            (-0.006, 0.0022), (-0.014, 0.0035)]
    poly = [(GX + a * c - b * s, GZ + a * s + b * c) for a, b in poly]
    g.prism(nd, poly, (0, 2), G_NEEDLE[0], G_NEEDLE[1])
    if lod < 2:
        lathe(nd, [(0.0048, 0.0), (0.0045, 0.0012), (0.003, 0.0022)], 10 if lod == 0 else 5,
              g.Frame((GX, G_NEEDLE[0], GZ), (0, -1, 0), (1, 0, 0), (0, 0, 1)), caps=(False, True))
    parts.append(nd)
    gf = P("blk_gauge_face", "gauge_face")
    g.cyl(gf, (GX, G_FACE + 0.0004, GZ), "y", GR, 0.0008, n)
    parts.append(gf)
    # display (ozl_screen): its own texture, flat UV 0..1 over the frame
    x0, x1, z0, z1 = L.LCD
    lc = P("blk_lcd", "lcd", group=SEL_SCREEN, section="lcd")
    yq = YP - 0.0008 if lod < 2 else BY0 - 0.001
    front_quad(lc, x0, x1, z0, z1, yq)
    lc.glass_frame = (g.Frame((0.0, yq, 0.0), (1, 0, 0), (0, 0, 1), (0, -1, 0)), x0, x1, z0, z1)
    parts.append(lc)
    # "working" lamp (ozl_lamp)
    lx, lz = L.LAMP
    lp = P("blk_lamp", "lamp", group=SEL_LAMP)
    if lod == 2:
        front_quad(lp, lx - 0.009, lx + 0.009, lz - 0.009, lz + 0.009, BY0 - 0.001)
        return parts + [lp]
    fl = g.Frame((lx, YP, lz), (0, -1, 0), (1, 0, 0), (0, 0, 1))
    lathe(lp, [(0.0092, 0.004), (0.009, 0.0078), (0.0068, 0.0108), (0.0035, 0.0121), (0.0015, 0.0124)],
          16 if lod == 0 else 6, fl, caps=(False, True))
    parts.append(lp)
    # aluminum panel on screws
    pn = P("blk_panel", "panel")
    g.box(pn, BX0 + 0.008, BX1 - 0.008, YP, BY0 + 0.001, BZ0 + 0.008, BZ1 - 0.008, **bev(lod, 0.001, 1))
    parts.append(pn)
    ch = P("blk_hw", "chrome")
    fg = g.Frame((GX, YP, GZ), (0, -1, 0), (1, 0, 0), (0, 0, 1))
    if lod == 0:
        # gauge rim: an outer bead and an inner wall down to the dial, glass
        lathe(ch, [(GR + 0.003, 0.0), (GR + 0.0068, 0.0015), (GR + 0.008, 0.005), (GR + 0.0066, 0.0086),
                   (GR + 0.002, 0.0098), (GR - 0.0016, 0.0086)], n, fg)
        lathe(ch, [(GR - 0.0016, 0.0086), (GR + 0.0002, 0.0018)], n, fg, inward=True)
        gl = P("blk_gauge_glass", "chrome", section="glass")
        g.cyl(gl, (GX, G_GLASS, GZ), "y", GR - 0.001, 0.0008, n)
        parts.append(gl)
        lathe(ch, [(0.0135, 0.0), (0.0135, 0.0042), (0.012, 0.0066), (0.0094, 0.0066), (0.0092, 0.0048)], 14, fl)
        # panel screws
        for x in (BX0 + 0.016, BX1 - 0.016):
            for z in (BZ0 + 0.016, BZ1 - 0.016):
                g.cyl(ch, (x, YP - 0.0007, z), "y", 0.0036, 0.0014, 6)
    else:
        g.cyl(ch, (GX, YP - 0.004, GZ), "y", GR + 0.006, 0.008, n)
        g.cyl(ch, (lx, YP - 0.003, lz), "y", 0.0135, 0.006, 6)
    # display frame
    bz = P("blk_lcd_bezel", "toggle")
    for a0, a1, b0, b1 in ((x0 - 0.005, x1 + 0.005, z1, z1 + 0.005), (x0 - 0.005, x1 + 0.005, z0 - 0.005, z0),
                           (x0 - 0.005, x0, z0, z1), (x1, x1 + 0.005, z0, z1)):
        g.box(bz, a0, a1, YP - 0.0028, YP + 0.0005, b0, b1)
    parts.append(bz)
    # toggles: a nut, a bushing, a lever with a ball down (off), a blank nameplate
    tx, tz = L.TOGGLES
    for x in tx:
        hexnut(ch, (x, YP, tz), (0, -1, 0), 0.0075, 0.003)
        if lod == 0:
            g.cyl(ch, (x, YP - 0.0065, tz), "y", 0.0045, 0.007, 10)
            d = Vector((0, -0.62, -0.78))
            o = Vector((x, YP - 0.009, tz))
            lathe(ch, [(0.0024, 0.0), (0.0017, 0.020), (0.0027, 0.0215), (0.0028, 0.0245), (0.0012, 0.026)], 6,
                  along(o, d), caps=(False, True))
            g.box(bz, x - 0.016, x + 0.016, YP - 0.0012, YP, tz - 0.030, tz - 0.020)
    # valves on top: a body, a gland nut, a stem, a handwheel with spokes
    vx, vy = L.VALVES
    for i, x in enumerate(vx):
        g.cyl(ch, (x, vy, BZ1 + 0.006), "z", 0.011, 0.012, 6)
        g.cyl(ch, (x, vy, BZ1 + 0.0155), "z", 0.0075, 0.007, 6)
        g.cyl(ch, (x, vy, BZ1 + 0.024), "z", 0.003, 0.012, 8)
        wh = P("blk_wheel%d" % i, "wheel_red" if i == 0 else "wheel_black")
        fw = upright((x, vy, BZ1 + 0.030))
        if lod == 0:
            torus(wh, fw, 0.0185, 0.0034, 14, 5)
            lathe(wh, [(0.0065, -0.004), (0.0065, 0.004)], 8, fw, caps=(True, True))
            for k in range(4):
                a = math.radians(45 + 90 * k)
                dv = fw.v * math.cos(a) + fw.n * math.sin(a)
                rod(wh, fw.o + dv * 0.006, fw.o + dv * 0.016, 0.0022, 5)
        else:
            g.cyl(wh, (x, vy, BZ1 + 0.030), "z", 0.021, 0.007, 8)
        parts.append(wh)
    if lod == 0:
        # fittings on the left - to the dome, at the back - from the compressor; the power cable entry
        for (y, z), rb_ in zip(NIPS, (0.0036, 0.0045)):
            hexnut(ch, (BX0 + 0.002, y, z), (-1, 0, 0), 0.0085, 0.007)
            barb(ch, (BX0 - 0.005, y, z), (-1, 0, 0), rb_)
        hexnut(ch, (BACK_FIT[0], BY1 - 0.002, BACK_FIT[1]), (0, 1, 0), 0.0085, 0.007)
        barb(ch, (BACK_FIT[0], BY1 + 0.005, BACK_FIT[1]), (0, 1, 0), 0.0045)
        ft = P("blk_feet", "feet")
        lathe(ft, [(0.009, 0.0), (0.0075, 0.012)], 8, along((GLAND[0], BY1 - 0.002, GLAND[1]), (0, 1, 0)),
              caps=(False, True))
        for x in (BX0 + 0.03, BX1 - 0.03):
            for y in (BY0 + 0.03, BY1 - 0.03):
                lathe(ft, [(0.012, -0.012), (0.012, -0.004), (0.010, 0.0)], 10, upright((x, y, BZ0)),
                      caps=(True, False))
        # louvers on the left side
        dk = P("blk_vents", "toggle")
        for k in range(5):
            zk = BZ0 + 0.105 + k * 0.012
            g.box(dk, BX0 - 0.0004, BX0 + 0.001, -0.075, 0.055, zk, zk + 0.005)
            g.box(bx, BX0 - 0.0032, BX0 + 0.001, -0.075, 0.055, zk + 0.005, zk + 0.0075, r=0.0008, seg=1)
        parts += [ft, dk]
    parts.append(ch)
    return parts


# =============================================================================
# Fengda AS-186 class compressor on the shelf on the right
# =============================================================================
def build_compressor(spec):
    lod = spec["lod"]
    n = 16 if lod == 0 else 10 if lod == 1 else 6
    tx0, tx1 = L.TANK_X
    r, tz, cy = TANK_R, TANK_Z, CMY
    Lt = tx1 - tx0
    parts = []
    tk = P("comp_tank", "comp_tank")
    ft = along((tx0, cy, tz), (1, 0, 0))
    prof = [(0.010, 0.0), (0.032, 0.004), (0.048, 0.011), (0.058, 0.023), (r, 0.04), (r, Lt - 0.04),
            (0.058, Lt - 0.023), (0.048, Lt - 0.011), (0.032, Lt - 0.004), (0.010, Lt)]
    lathe(tk, prof if lod == 0 else [prof[i] for i in (0, 2, 4, 5, 7, 9)] if lod == 1 else
          [prof[i] for i in (0, 4, 5, 9)], n, ft, caps=(True, True))
    parts.append(tk)
    bd = P("comp_body", "comp_body")
    al = P("comp_pump", "comp_alu")
    if lod == 2:
        g.box(bd, MX0, MX1 + 0.06, cy - 0.05, cy + 0.05, tz + r, MZ + MR)
        return parts + [bd]
    # feet: stamped legs under the receiver, rubber pads
    rb = P("comp_rubber", "feet")
    for x in (tx0 + 0.05, tx1 - 0.05):
        g.box(bd, x - 0.012, x + 0.012, cy - 0.06, cy + 0.06, ZS + 0.005, ZS + 0.009, **bev(lod, 0.0015, 1))
        g.box(bd, x - 0.0025, x + 0.0025, cy - 0.035, cy + 0.035, ZS + 0.009, tz - 0.045)
        for s in (-1, 1):
            g.cyl(rb, (x, cy + s * 0.048, ZS + 0.0025), "z", 0.009, 0.005, 8 if lod == 0 else 5)
    parts.append(rb)
    # motor platform on the receiver, the motor along x, the fan shroud on the left
    g.box(bd, MX0 - 0.012, MX1 + 0.062, cy - 0.046, cy + 0.046, tz + r - 0.004, tz + r + 0.006, **bev(lod, 0.002, 1))
    Lm = MX1 - MX0
    fm = along((MX0, cy, MZ), (1, 0, 0))
    lathe(bd, [(MR - 0.006, 0.0), (MR - 0.001, 0.003), (MR, 0.008), (MR, Lm - 0.006), (MR - 0.004, Lm)] if lod == 0 else
          [(MR, 0.0), (MR, Lm)], n, fm)
    for x in (MX0 + 0.02, MX1 - 0.02):                                                  # motor feet
        g.box(bd, x - 0.008, x + 0.008, cy - 0.032, cy + 0.032, tz + r + 0.006, MZ - MR + 0.01)
    # fan shroud: a shell, a bottom (dark)
    lathe(bd, [(MR + 0.003, -0.022), (MR + 0.003, 0.006)], n, fm)
    if lod == 0:
        lathe(bd, [(MR + 0.003, -0.022), (MR - 0.0005, -0.022)], n, fm, want=-fm.u)
        lathe(bd, [(MR - 0.0005, -0.022), (MR - 0.0005, -0.002)], n, fm, inward=True)
    fn_ = P("comp_fan_bg", "fan")
    lathe(fn_, [(MR - 0.0005, -0.002), (0.004, -0.002)], n, fm, want=-fm.u)
    parts.append(fn_)
    # fan (bone ozl_work): a hub and six blades at an angle
    fan = P("comp_fan", "fan", group=SEL_FAN)
    xf = MX0 - 0.010
    lathe(fan, [(0.008, -0.007), (0.013, -0.004), (0.013, 0.004)], 12 if lod == 0 else 6,
          along((xf, cy, MZ), (-1, 0, 0)), caps=(True, True))
    for k in range(6):
        a = 2 * math.pi * k / 6
        er = Vector((0, math.cos(a), math.sin(a)))
        et = Vector((0, -math.sin(a), math.cos(a)))
        p = math.radians(28.0)
        ch_ = et * math.cos(p) + Vector((1, 0, 0)) * math.sin(p)
        fb = g.Frame((xf, cy, MZ), er, ch_, er.cross(ch_))
        g.box(fan, 0.011, 0.049, -0.010, 0.010, -0.0008, 0.0008, frame=fb)
    parts.append(fan)
    # shroud grille: rings and spokes
    if lod == 0:
        gr = P("comp_grille", "grille")
        fgr = along((MX0 - 0.021, cy, MZ), (1, 0, 0))
        for R in (0.016, 0.030, 0.044):
            torus(gr, fgr, R, 0.0013, 16, 3)
        for k in range(4):
            a = math.radians(45 + 90 * k)
            dv = fgr.v * math.cos(a) + fgr.n * math.sin(a)
            rod(gr, fgr.o + dv * 0.006, fgr.o + dv * (MR + 0.002), 0.0014, 4)
        lathe(gr, [(0.007, 0.0), (0.007, 0.002)], 8, fgr, caps=(True, False))
        parts.append(gr)
    # crankcase, finned cylinder, head on bolts
    cz0, cz1 = MZ + 0.03, MZ + 0.09
    g.box(al, MX1 - 0.004, MX1 + 0.058, cy - 0.042, cy + 0.042, tz + r + 0.006, cz0, **bev(lod, 0.006, 2))
    xc = MX1 + 0.027
    if lod == 0:
        prof = [(0.022, 0.0)]
        for k in range(5):
            h = 0.006 + k * 0.0105
            prof += [(0.022, h), (0.034, h + 0.001), (0.034, h + 0.0045), (0.022, h + 0.0055)]
        prof.append((0.022, cz1 - cz0 - 0.002))
        lathe(al, prof, 12, upright((xc, cy, cz0)))
    else:
        g.cyl(al, (xc, cy, (cz0 + cz1) / 2), "z", 0.03, cz1 - cz0, 8)
    g.box(al, xc - 0.034, xc + 0.034, cy - 0.034, cy + 0.034, cz1 - 0.003, cz1 + 0.016, **bev(lod, 0.004, 2))
    parts += [bd, al]
    if lod > 0:
        return parts
    ch = P("comp_hw", "chrome")
    for sx in (-1, 1):
        for sy in (-1, 1):
            g.cyl(ch, (xc + sx * 0.024, cy + sy * 0.024, cz1 + 0.018), "z", 0.0045, 0.005, 6)
    # copper tube from the head to the block on the receiver
    cu = P("comp_pipe", "copper")
    mb = (CGX - 0.0175, CGX + 0.0175, cy - 0.025, cy + 0.025, tz + r + 0.012, tz + r + 0.055)   # manifold block
    pts = [(xc + 0.034, cy + 0.016, cz1 + 0.006), (xc + 0.05, cy + 0.016, cz1 + 0.002), (mb[0] - 0.008, cy + 0.016, cz1 - 0.03),
           (mb[0] - 0.006, cy + 0.016, mb[5] - 0.02), (mb[0] + 0.002, cy + 0.016, mb[5] - 0.014)]
    g.pipe(cu, spline(pts, 4), 0.0035, 6)
    hexnut(ch, (xc + 0.034, cy + 0.016, cz1 + 0.006), (1, 0, 0), 0.0065, 0.006)
    parts.append(cu)
    # manifold block: a riser from the receiver, a gauge, a regulator, a safety valve, a moisture separator
    br = P("comp_brass", "brass")
    g.cyl(br, (CGX, cy, tz + r + 0.004), "z", 0.008, 0.018, 10)
    g.box(br, mb[0], mb[1], mb[2], mb[3], mb[4], mb[5], r=0.002, seg=1)
    g.cyl(br, (CGX - 0.012, cy + 0.018, mb[5] + 0.008), "z", 0.0045, 0.016, 8)          # safety valve
    lathe(br, [(0.0065, 0.0), (0.0065, 0.004)], 8, upright((CGX - 0.012, cy + 0.018, mb[5] + 0.016)), caps=(True, True))
    zt = mb[4] + 0.022
    g.cyl(br, (mb[1] + 0.008, cy, zt), "x", 0.0075, 0.016, 10)                          # tee to the right
    parts.append(br)
    g.cyl(ch, (CGX, mb[2] - 0.0045, CGZ), "y", 0.004, 0.009, 8)                            # gauge nipple
    lathe(ch, [(CG_R, 0.0), (CG_R + 0.002, 0.003), (CG_R + 0.002, 0.011), (CG_R + 0.0012, 0.0135), (CG_R - 0.001, 0.0138)],
          16, g.Frame((CGX, CGY + 0.0135, CGZ), (0, -1, 0), (1, 0, 0), (0, 0, 1)), caps=(True, False))
    gf = P("comp_gauge_face", "gauge_face")
    g.cyl(gf, (CGX, CG_FACE + 0.0004, CGZ), "y", CG_R - 0.001, 0.0008, 20)
    parts.append(gf)
    nd = P("comp_needle", "needle", group=SEL_CNEEDLE)
    c, s = math.cos(NEEDLE0), math.sin(NEEDLE0)
    poly = [(-0.004, -0.0012), (CG_R * 0.8, -0.0004), (CG_R * 0.8, 0.0004), (-0.004, 0.0012)]
    g.prism(nd, [(CGX + a * c - b * s, CGZ + a * s + b * c) for a, b in poly], (0, 2), CG_FACE - 0.0016, CG_FACE - 0.0008)
    g.cyl(nd, (CGX, CG_FACE - 0.0015, CGZ), "y", 0.0018, 0.0008, 8)
    parts.append(nd)
    gl = P("comp_gauge_glass", "chrome", section="glass")
    g.cyl(gl, (CGX, CGY - 0.0009, CGZ), "y", CG_R - 0.0005, 0.0006, 20)
    parts.append(gl)
    kn = P("comp_knob", "valve")
    g.cyl(ch, (CGX + 0.006, cy - 0.004, mb[5] + 0.005), "z", 0.0035, 0.01, 8)
    lathe(kn, [(0.010, 0.0), (0.0125, 0.002), (0.0125, 0.013), (0.011, 0.016), (0.004, 0.017)], 18,
          upright((CGX + 0.006, cy - 0.004, mb[5] + 0.008)), caps=(True, True))
    # moisture separator under the tee: a cap, a transparent cup, a drain cock
    xb = mb[1] + 0.016
    g.cyl(kn, (xb, cy, zt - 0.006), "z", 0.0135, 0.008, 14)
    bw = P("comp_bowl", "bowl")
    lathe(bw, [(0.003, 0.0), (0.0105, 0.006), (0.0118, 0.03), (0.0118, 0.036)], 14, upright((xb, cy, zt - 0.046)),
          caps=(True, False))
    parts.append(bw)
    # outlet: a quick-release coupling on the tee
    g.cyl(ch, (xb + 0.008, cy, zt), "x", 0.0068, 0.012, 6)
    lathe(ch, [(0.0075, 0.0), (0.0075, 0.006), (0.0055, 0.008)], 12, along((xb + 0.014, cy, zt), (1, 0, 0)))
    barb(ch, (xb + 0.022, cy, zt), (1, 0, 0), 0.0045)
    # rocker switch on the motor face, a carrying handle with a rubber pad
    g.box(bd, MX0 + 0.035, MX0 + 0.075, cy - MR - 0.012, cy - MR + 0.012, MZ - 0.022, MZ + 0.012, r=0.002, seg=1)
    rk = P("comp_rocker", "rocker")
    g.box(rk, MX0 + 0.043, MX0 + 0.067, cy - MR - 0.0155, cy - MR - 0.011, MZ - 0.014, MZ + 0.004, r=0.0012, seg=1)
    parts.append(rk)
    zh = MZ + MR + 0.045
    pts = [(MX0 + 0.018, cy, MZ + MR - 0.004), (MX0 + 0.018, cy, zh - 0.018), (MX0 + 0.032, cy, zh),
           (MX1 - 0.032, cy, zh), (MX1 - 0.018, cy, zh - 0.018), (MX1 - 0.018, cy, MZ + MR - 0.004)]
    g.pipe(ch, spline(pts, 2), 0.0055, 6)
    g.cyl(rb, ((MX0 + MX1) / 2, cy, zh), "x", 0.0095, 0.07, 10)
    # drain cock under the receiver
    g.cyl(br, (tx1 - 0.03, cy, tz - r - 0.006), "z", 0.0045, 0.012, 8)
    g.box(br, tx1 - 0.036, tx1 - 0.024, cy - 0.0015, cy + 0.0015, tz - r - 0.016, tz - r - 0.011)
    parts.append(ch)
    return parts


# =============================================================================
# Hoses, cables, tape, plugs
# =============================================================================
def plug(part, end, d, lod):
    """Plug at the end of a cord: a body along d, two pins."""
    if lod > 0:
        return
    fr = along(end, d)
    lathe(part, [(0.0045, 0.0), (0.011, 0.012), (0.0175, 0.028), (0.0185, 0.044), (0.016, 0.046)], 10, fr,
          caps=(False, True))
    for s in (-1, 1):
        rod(part, fr.p(0.046, s * 0.0095, 0.0), fr.p(0.065, s * 0.0095, 0.0), 0.002, 5)


def build_hoses(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    bx = DX + L.BASE_R + 0.010
    (y0, z0), (y1, z1) = FITS
    (ny0, nz0), (ny1, nz1) = NIPS
    # transparent amber tube - with a loop forward on the table; the black hose - in an arc
    pa = [(bx, y0, z0), (bx + 0.016, y0 - 0.02, ZT + 0.009), (bx + 0.03, -0.15, ZT + 0.0068),
          (bx + 0.055, -0.155, ZT + 0.0068), (BX0 - 0.012, -0.11, nz0 - 0.018), (BX0 - 0.02, ny0, nz0),
          (BX0 - 0.008, ny0, nz0)]
    pb = [(bx, y1, z1), (bx + 0.016, y1, z1 + 0.002), (bx + 0.034, (y1 + ny1) / 2, (z1 + nz1) / 2 + 0.006),
          (BX0 - 0.034, ny1, nz1 + 0.002), (BX0 - 0.008, ny1, nz1)]
    xo, yo, zo = OUTLET
    fx, fz = BACK_FIT
    pc = [(xo, yo, zo), (xo + 0.022, yo + 0.01, zo + 0.012), (xo + 0.03, yo + 0.08, zo + 0.06),
          (0.425, TY1 + 0.03, 0.42), (0.415, TY1 + 0.035, ZT - 0.06), (0.41, TY1 + 0.02, ZT + 0.03),
          (fx, BY1 + 0.07, fz + 0.025), (fx, BY1 + 0.008, fz)]
    ha = hose("hose_amber", "hose_amber", pa, 0.005, lod)
    hb = hose("hose_black", "hose", pb, 0.0065, lod)
    hc = hose("hose_comp", "hose", pc, 0.0065, lod)
    parts += [ha, hb, hc]
    if lod > 0:
        return parts
    # clamps at the ends, blue tape: on the tube at the base and on the compressor hose behind the table
    zc = P("hose_clamps", "zinc")
    for pts, r in ((pa, 0.005), (pb, 0.0065)):
        band(zc, pts, 4, 1, 2, r + 0.0016)
        band(zc, pts, 4, len(spline(pts, 4)) - 3, len(spline(pts, 4)) - 2, r + 0.0016)
    band(zc, pc, 4, len(spline(pc, 4)) - 3, len(spline(pc, 4)) - 2, 0.0081)
    tp = P("tape", "tape")
    band(tp, pa, 4, 2, 5, 0.0068)
    band(tp, pc, 4, 14, 17, 0.0085)
    parts += [zc, tp]
    # power cords of the unit and the compressor - behind the table onto the floor, plugs at the ends
    cb = P("cables", "cable")
    gx, gz = GLAND
    pts = [(gx, BY1 + 0.010, gz), (gx - 0.005, BY1 + 0.05, gz - 0.008), (gx - 0.02, TY1 - 0.01, ZT + 0.004),
           (gx - 0.035, TY1 + 0.04, ZT - 0.08), (gx - 0.08, TY1 + 0.08, 0.30), (gx - 0.13, TY1 + 0.12, 0.0035),
           (-0.05, TY1 + 0.16, 0.0035), (-0.09, TY1 + 0.155, 0.006), (-0.12, TY1 + 0.15, 0.018)]
    g.pipe(cb, spline(pts, 2), 0.0035, 5)
    plug(cb, pts[-1], (-1, -0.1, 0), lod)
    pts = [(MX0 + 0.03, CMY + MR - 0.004, MZ - 0.02), (MX0 + 0.025, CMY + 0.085, MZ - 0.06),
           (MX0 + 0.02, LY1 - 0.01, ZS + 0.004), (MX0 + 0.01, TY1 + 0.03, ZS - 0.05), (MX0 - 0.01, TY1 + 0.09, 0.0035),
           (-0.10, TY1 + 0.20, 0.0035), (-0.15, TY1 + 0.215, 0.006), (-0.18, TY1 + 0.22, 0.018)]
    g.pipe(cb, spline(pts, 2), 0.0035, 5)
    plug(cb, pts[-1], (-1, 0.15, 0), lod)
    parts.append(cb)
    return parts


def build_lod(spec):
    parts = build_table(spec) + build_dome(spec) + build_block(spec) + build_compressor(spec) + build_hoses(spec)
    parts = [p for p in parts if p.bm.faces]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        if M.stats:
            check_decor()
    return parts


def check_decor():
    """Vanilla items do not intersect each other or the dome (extents kv.corners)."""
    boxes = []
    for d in DECOR:
        q = kv.corners(d[5], d[1], d[2], d[3])
        lo = tuple(min(c[i] for c in q) for i in range(3))
        hi = tuple(max(c[i] for c in q) for i in range(3))
        boxes.append((d[5], lo, hi))
        print("decor %-12s x %.3f..%.3f  y %.3f..%.3f  z %.3f..%.3f" % (d[5], lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
    for i, (a, alo, ahi) in enumerate(boxes):
        for b, blo, bhi in boxes[i + 1:]:
            if all(alo[k] < bhi[k] - 1e-4 and blo[k] < ahi[k] - 1e-4 for k in range(3)):
                print("decor overlap: %s / %s" % (a, b))


def collision():
    """Two boxes: the whole table and, above the tabletop, the dome with the unit (a component thinner
    than 0.5 m does not work in the engine, so the upper one is 0.5 m deep)."""
    steel = kx.PEN + r"\metalplate.rvmat"
    low = kx.box_pts(TX0, TX1, TY0, TY1, 0.0, ZT)
    up = kx.box_pts(DX - L.BASE_R, BX1 + 0.005, -0.25, 0.25, ZT, ZB + L.DOME_H + 0.024)
    comps = [(low, steel), (up, steel)]
    memory = {
        "invView": [(0.0, -2.2, 1.4)],
        "ce_center": [(0.0, 0.0, 0.68)],
        "ce_radius": [(0.9, 0.0, 0.68)],
        # needle axes (from the dial toward the person) and the fan axis (toward the grille)
        "ozl_needle_axis": [NEEDLE_O, (GX, G_NEEDLE[1] - 0.05, GZ)],
        "ozl_cneedle_axis": [CNEEDLE_O, (CGX, CNEEDLE_O[1] - 0.05, CGZ)],
        "ozl_work_axis": [FAN_O, (FAN_O[0] - 0.05, FAN_O[1], FAN_O[2])],
    }
    # axes of the "breathing" bubbles: a meter along the outward normal from the middle (the animation offset is in meters)
    for i, (c, n, _, _) in enumerate(PUFF_GEO):
        memory["ozl_puff_%d_axis" % (i + 1)] = [tuple(c), tuple(c + n * 1.0)]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2] + 0.004)
    return comps, 60.0, memory, bbox


# the first ones are for the --look preview: the unit (and when "working": display, lamp, needle), the
# shelf with the compressor (when "working" - the fan and the needle), the mask close up (when "working"
# - cheeks and temples inflated), the mask under the dome, overall
SHOTS = [
    ("block", (0.55, -0.78, 1.18), (0.30, -0.05, 0.95), 40),
    ("shelf", (-0.48, -1.05, 0.58), (0.10, 0.0, 0.33), 30),
    ("mask", (-0.33, -0.62, 1.19), (-0.17, 0.01, 1.11), 60),
    ("dome", (-0.50, -0.95, 1.30), (-0.17, 0.0, 1.07), 38),
    ("front", (-0.9, -2.6, 1.75), (0.0, 0.0, 0.70), 30),
    ("comp", (0.02, -0.72, 0.56), (0.27, 0.02, 0.36), 40),
    ("right", (1.9, -0.9, 1.25), (0.0, 0.0, 0.70), 32),
    ("top", (0.1, -0.9, 2.4), (0.0, 0.0, 0.85), 30),
    ("back", (1.3, 2.1, 1.6), (0.0, 0.0, 0.70), 32),
]

M.look_shots = (5, 3)
M.run(build_lod, collision, SHOTS, row_step=1.5, row_shot=((1.5, -5.8, 1.9), (1.5, 0, 0.7)))
