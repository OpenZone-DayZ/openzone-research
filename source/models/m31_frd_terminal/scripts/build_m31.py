"""M31 - a computer on cases, the Freedom terminal (OZL_Frd_Terminal): result media are handed
in here and the research tree is opened. A terminal: an explicit screen, no modules.

    blender --background --python build_m31.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: make_decals.py with the system Python (the decals on the cases, tower,
monitor and radio, the keyboard, the screen - "off" and the "working" frames). Positions are
in layout.py (shared with make_decals.py), own primitives in m31_geo.py.

Card: the Freedom HQ computer - a table made of a board on two bright green NATO cases; on
it a beige 15" CRT monitor and a 90s system unit, a keyboard, speakers, a radio, a mug, a
tangle of cables, overlapping stickers. ~1.2 x 1.4 x 0.7 m.

Look: "dayz" (matte, dustier, colored AO). No angular parts: the cases are cast, with rounded
ribs, a seam rim, double-action latches, a folding handle, a back hinge and wheels; the
monitor has a rounded body, a chamfered tube window, convex glass with rounded corners, a
flare to the back, slots, buttons and a disc stand; the system unit has a plastic front
panel, drives with a tray and a shutter, buttons, louvres on the side, a back with a PSU, a
fan behind a grille, cards and connectors; the keyboard has 101 separate keys and three
LEDs; the radio has a cast body with a battery box on latches, knobs with skirts, scale
windows, headset connectors, a spring antenna base and the antenna itself - a steel tape;
the handset is cast, with capsules and a push-to-talk bar, a coiled cord; speakers, mouse,
mug, pad, floppies and a power strip with plugs have no boxes. Small items are vanilla
proxy things (kvanilla): a sheet of paper with a pen and a 9 V battery under the handset,
insulating tape at a table corner, an electrician's kit on the system unit, two cassettes on
the monitor, a vodka bottle under the table.

Reference and dimensions:
- a home PC of the second half of the 90s and a beige tower with a CRT on a worn table -
  look and proportions; there are no brands or logos in the model;
- a Pelican 1620 class case: 630 x 492 x 352 mm outside (24.81 x 19.37 x 13.87"), stands
  on its end - 0.630 high; the lid seam, two latches and the handle are on the front, the
  hinge on the back, wheels (~dia 80) at the rear bottom corner, the telescoping handle is
  not modeled (the end is under the tabletop); bright green (Freedom, no olive);
- the tabletop - plywood 1220 x 610 x 18 (a quarter of a 2440 x 1220 sheet), top at 0.648;
- a 15" CRT monitor: body 360 x 362 x 387 mm with the stand (Philips 105S 36 x 38.7 x 36.2
  cm; Compaq V570 35.6 x 37.9 x 36.9 cm); image 250 x 187 mm (Sun 15"), visible glass
  285 x 215, bulge 14 mm - estimated from photos;
- a mini-tower system unit: 203 x 406 x 406 mm (Dell Dimension XPS P75/P90/P100, 1995:
  40.64 x 20.32 x 40.64 cm); 5.25" bays - 148 mm, 3.5" - 102 mm (the drive size); PSU fan
  80 mm;
- an IBM Model M class keyboard: 455 x 180 x 50 mm, 101 keys (New Model M; the original
  weighs 2.0-2.5 kg);
- speakers 95 x 140 x 235 mm - an estimate (the height after the Labtec LCS-1030, 9.5");
- an AN/PRC-77 class radio: 273 x 273 x 100 mm, 6.2 kg, the AT-892 antenna - a flexible
  3 ft tape on a spring base AB-591, ~0.9 m: upright it would lift the top to ~1.8 m, so the
  tape is bent in an arc sideways over the speaker - top at 1.40, as on the card, and it
  does not stick out past the table. The body is dark grey, not olive: olive would clash
  with the bright green of Freedom; a handset of the H-189 class (~0.22) with a coiled cord;
- mug dia 82 x 95, mouse 110 x 63 x 35, pad 230 x 185, 3.5" floppies 90 x 94 x 3.3 mm
  (standard), power strip - estimates.

Freedom (as M27-M29): shabby, dusty, a bit careless - scratches, overlapping stickers (some
with short English words; a peace sign and LEGALIZE), the tabletop slightly rotated, cables
in a tangle and on insulating tape; no rust. The builder build_scuffed comes from M27/M28.

Machine look and "working" - a loop: the CRT screen is ozl_screen, with its own texture (the
screen section): "off" - dark glass, "working" - the _screen_fNN frames (OZL_WorkFx frames:
in the research tree the next block fills in, the cursor blinks, the receiving log lines
crawl, the bar grows); ozl_lamp - steady (power of the unit and the monitor, keyboard LEDs,
speaker, the power strip key), ozl_lamp_blink - blinking (the unit's disk, the radio lamp);
the PSU fan behind the grille on the back is the bone ozl_fan on the source ozl_work: a
model.cfg loop (sourceAddress loop). LODs: the middle one has no small items and no separate
keys (the keys are a picture), the far one has boxes, no cables and no small items.

Blender axes: X - width, Y - depth (front at -Y), Z - up.
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
import kwood  # noqa: E402
import layout as L  # noqa: E402
from m31_geo import (blob, bulge_rr, button, coil, ends, fillet_poly, hull, keycap, lathe, loft, rbox,  # noqa: E402
                     ribbon, round_prof, rrect, spline, turn)

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
DZ = L.DZ
HC = L.CASE[2]

LOD_SPECS = [
    dict(lod=0, sides=16),
    dict(lod=1, sides=8),
    dict(lod=2, sides=5),
]

REGIONS = {
    "case": ("case", 1.4), "case_plain": ("case_plain", 0.6), "case_hw": ("case_hw", 1.4), "wheel": ("rubber", 1.0),
    "wood": ("wood", 0.9),
    "beige": ("beige", 1.6), "beige_plain": ("beige_plain", 0.9), "beige_dark": ("beige_dark", 1.4),
    "keyboard": ("keyboard", 3.0), "key_beige": ("key_beige", 1.2), "key_grey": ("key_grey", 1.2),
    "grille": ("grille", 1.0), "screen": ("black", 1.0),
    "radio": ("radio", 1.6), "radio_plain": ("radio_plain", 0.8), "radio_panel": ("radio_panel", 1.4),
    "knob": ("black", 1.4), "black": ("black", 0.8), "dial": ("dial", 2.0), "rubber": ("rubber", 0.6),
    "metal": ("metal", 1.0), "tape_ant": ("tape_ant", 0.8), "fan": ("fan", 1.0),
    "led_g": ("led_g", 1.0), "led_a": ("led_a", 1.0), "led_r": ("led_r", 1.0),
    "mug": ("mug", 1.4), "coffee": ("coffee", 1.0), "mousepad": ("mousepad", 0.8),
    "floppy": ("floppy", 1.2), "floppy_blue": ("floppy_blue", 1.2), "label": ("label", 1.0),
    "strip": ("strip", 0.9), "strip_dark": ("black", 0.9),
    "tape": ("tape", 1.2), "tape_blue": ("tape_blue", 1.2),
    "cable": ("cable", 0.6), "cable_beige": ("cable_beige", 0.6),
}

# =============================================================================
# Materials
# =============================================================================


def build_scuffed(mat, origin, color, bare=kmats.lin((112, 112, 116)), seed=1.0, gloss=0.32, spec=0.25,
                  wear=(0.66, 0.71), edge_k=0.7, rub=(), scratch=0.0, floor_z=0.0, dust=0.3, grime=0.3,
                  decal_items=()):
    """Paint (plastic), shabby and careless, no rust (Freedom) - the builder of M27 through M28:
    worn to the base on the edges (edge_k) and in the places that get grabbed (rub - [(center,
    half-axes, strength)]), scratches along x; the stickers go over the wear (the sticker
    itself is already worn in the PNG), dust and grime go over everything.
    """
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


def decal_y(name, x0, x1, z0, z1, y, depth=0.002):
    """A sticker on a face looking toward -y; depth - how far below the face (it wraps onto the
    edge rounding).
    """
    return (wdecal(name), "y", -1, ("x", "z"), ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0),
            (y - 0.002, y + depth))


def decal_x(name, y0, y1, z0, z1, x, sign, depth=0.002):
    """A sticker on a face looking toward +x (sign=1) or -x (sign=-1). Looking at a -x face, y
    grows to the left - the picture is mirrored by a negative width.
    """
    rng = (x - 0.002, x + depth) if sign < 0 else (x - depth, x + 0.002)
    return (wdecal(name), "x", sign, ("y", "z"), ((y0 + y1) / 2, (z0 + z1) / 2), (sign * (y1 - y0), z1 - z0), rng)


def decal_z(name, x0, x1, y0, y1, z0, z1):
    return (wdecal(name), "z", 1, ("x", "y"), ((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0, y1 - y0), (z0, z1))


CASE_DECALS = [decal_y("decal_case%d_front.png" % i, *L.CASE_FRONT[i], L.CY0, 0.014) for i in (0, 1)]
CASE_DECALS += [decal_x("decal_case%d_side.png" % i, *L.CASE_SIDE, L.case_out(i)[0], L.case_out(i)[1], 0.014)
                for i in (0, 1)]
BEIGE_DECALS = [decal_x("decal_tower_side.png", *L.TOWER_SIDE, L.TX1, 1, 0.004),
                decal_y("decal_tower_front.png", *L.TOWER_FRONT, L.TY0, 0.004),
                decal_z("decal_mon_top.png", *L.MON_TOP, L.MZ1 - 0.012, L.MZ1 + 0.002)]
RADIO_DECALS = [decal_x("decal_radio.png", *L.RADIO_SIDE, L.RX0, -1, 0.012)]
KEYS_DECAL = decal_z("decal_keys.png", *L.KEYS, L.KZ_F - 0.003, L.KZ_B + 0.004)


def flat(rgb, gloss=0.85, spec=0.8):
    return ("flat", dict(color=kmats.lin(rgb), gloss=gloss, spec=spec))


GREEN = kmats.lin((62, 152, 44))
CASE = dict(color=GREEN, bare=kmats.lin((112, 176, 96)), seed=10.3, gloss=0.3, spec=0.2, wear=(0.70, 0.76),
            edge_k=0.8, scratch=0.6, dust=0.45, grime=0.35)
# beige plastic of the 90s: slightly yellowed, worn to a light tone around buttons and on edges
BEIGE = dict(color=kmats.lin((204, 194, 166)), bare=kmats.lin((226, 220, 200)), seed=6.1, gloss=0.28, spec=0.2,
             wear=(0.72, 0.78), edge_k=0.7, scratch=0.35, floor_z=DZ, dust=0.5, grime=0.25,
             rub=[((L.T_POWER[0], L.TY0, L.T_POWER[1]), (0.03, 0.02, 0.03), 0.35),
                  ((L.MX + 0.12, L.MY0, L.MZ0 + 0.026), (0.05, 0.02, 0.02), 0.3)])
RADIO = dict(color=kmats.lin((52, 54, 52)), bare=kmats.lin((108, 110, 106)), seed=7.3, gloss=0.25, spec=0.2,
             wear=(0.69, 0.75), edge_k=0.9, scratch=0.5, floor_z=DZ, dust=0.4, grime=0.3)
# small items 5-20 cm: the dust and grime of the "dayz" profile are tuned for 1-2 m machines -
# weaker on small items
SMALL = dict(dust=0.12, grime=0.12)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "case": (build_scuffed, dict(CASE, decal_items=CASE_DECALS)),
    "case_plain": (build_scuffed, CASE),
    "case_hw": ("plastic", dict(color=kmats.lin((30, 30, 32)), gloss=0.35, spec=0.25, dust=0.3, grime=0.3,
                                scuff=(0.64, 0.72))),
    "wood": (kwood.build_wood, dict(color=kmats.lin((184, 150, 106)), seed=3.3, along="x", floor_z=L.PZ0,
                                    dust=0.45, grime=0.35, rings=0.35, knots=0.4)),
    "beige": (build_scuffed, dict(BEIGE, decal_items=BEIGE_DECALS)),
    "beige_plain": (build_scuffed, BEIGE),
    "beige_dark": (build_scuffed, dict(BEIGE, color=kmats.lin((168, 160, 138)), seed=6.7, rub=())),
    "keyboard": (build_scuffed, dict(BEIGE, color=kmats.lin((150, 144, 126)), seed=6.9, rub=(), dust=0.3,
                                     decal_items=[KEYS_DECAL])),
    # keys: the middle is rubbed by fingers (scuff), dust between the keys
    "key_beige": ("plastic", dict(color=kmats.lin((210, 202, 180)), seed=9.1, gloss=0.35, spec=0.25, mottle=0.06,
                                  dust=0.15, grime=0.25, scuff=(0.66, 0.78))),
    "key_grey": ("plastic", dict(color=kmats.lin((148, 146, 138)), seed=9.3, gloss=0.35, spec=0.25, mottle=0.06,
                                 dust=0.15, grime=0.25, scuff=(0.68, 0.80))),
    "grille": ("plastic", dict(color=kmats.lin((40, 40, 42)), gloss=0.10, spec=0.06, mottle=0.14, dust=0.4)),
    "radio": (build_scuffed, dict(RADIO, decal_items=RADIO_DECALS)),
    "radio_plain": (build_scuffed, RADIO),
    "radio_panel": (build_scuffed, dict(RADIO, color=kmats.lin((44, 46, 44)), seed=7.7, edge_k=1.0, dust=0.5)),
    "dial": flat((16, 18, 18), 0.8, 0.6),
    "metal": ("steel", dict(seed=5.1, tone=0.34, along="z", gloss=0.6, spec=0.7, floor_z=DZ, dust=0.15, grime=0.2)),
    "tape_ant": ("plastic", dict(color=kmats.lin((40, 42, 38)), seed=5.3, gloss=0.4, spec=0.3, dust=0.2, grime=0.2,
                                 scuff=(0.60, 0.68))),
    "fan": ("plastic", dict(color=kmats.lin((22, 22, 23)), seed=5.7, gloss=0.3, spec=0.2, dust=0.6, grime=0.5)),
    "led_g": flat((34, 64, 40)), "led_g_on": flat((130, 255, 140)),
    "led_a": flat((80, 56, 22)), "led_a_on": flat((255, 176, 40)),
    "led_r": flat((80, 22, 18)), "led_r_on": flat((255, 60, 40)),
    "mug": ("plastic", dict(color=kmats.lin((226, 222, 208)), gloss=0.6, spec=0.45, mottle=0.04, floor_z=DZ,
                            dust=0.1, grime=0.3, scuff=(0.70, 0.78))),
    "coffee": flat((46, 26, 14), 0.9, 0.6),
    "mousepad": ("plastic", dict(color=kmats.lin((30, 42, 96)), gloss=0.1, spec=0.05, mottle=0.12, dust=0.2,
                                 grime=0.2, scuff=(0.66, 0.72))),
    "floppy": ("plastic", dict(color=kmats.lin((26, 26, 28)), gloss=0.4, spec=0.3, **SMALL)),
    "floppy_blue": ("plastic", dict(color=kmats.lin((40, 70, 150)), gloss=0.4, spec=0.3, **SMALL)),
    "label": ("plastic", dict(color=kmats.lin((230, 226, 210)), gloss=0.2, spec=0.1, scuff=(0.66, 0.74), **SMALL)),
    "strip": ("plastic", dict(color=kmats.lin((222, 220, 212)), gloss=0.35, spec=0.25, dust=0.4, grime=0.4,
                              scuff=(0.66, 0.74))),
    "tape": ("plastic", dict(color=kmats.lin((148, 150, 150)), gloss=0.5, spec=0.35, scuff=(0.66, 0.74), **SMALL)),
    "tape_blue": ("plastic", dict(color=kmats.lin((34, 74, 168)), gloss=0.55, spec=0.35, scuff=(0.7, 0.78), **SMALL)),
    "cable": ("plastic", dict(color=kmats.lin((24, 24, 24)), gloss=0.35, spec=0.25, dust=0.25)),
    "cable_beige": ("plastic", dict(color=kmats.lin((196, 188, 166)), gloss=0.3, spec=0.2, dust=0.25, grime=0.3)),
})

OBJ, NAME = "m31_frd_terminal", "ozr_frd_terminal"
# Machine look: the screen has its own texture (the mod script cycles the frames), the lamps
# use the _on atlas (ozl_lamp steady, ozl_lamp_blink blinking), the PSU fan is a model.cfg loop.
SEL_SCREEN, SEL_LAMP, SEL_BLINK, SEL_FAN = "ozl_screen", "ozl_lamp", "ozl_lamp_blink", "ozl_fan"
ON = dict(remap={"led_g": "led_g_on", "led_a": "led_a_on", "led_r": "led_r_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
FAN_TURNS = 4                                                  # turns per loop pass (a pass is 2.5 s - 1.6 rev/s)
FAN_ANIM = ("ozl_fan_spin", dict(type="rotation", source="ozl_work", sourceAddress="loop", selection=SEL_FAN,
                                 axis="ozl_fan_axis", memory=1, minValue=0.0, maxValue=1.0 / FAN_TURNS,
                                 angle0=0.0, angle1=2 * math.pi))
SCREEN = dict(off="decal_screen_off.png", frames=["decal_screen_f%02d.png" % i for i in range(12)], size=256,
              gloss=0.8)

# Vanilla items: a paper sheet under the handset (with a pen and a 9 V battery on it),
# insulating tape at a table corner, an electrician's kit on the system unit, two cassettes
# on the monitor, vodka under the table
PAPER_AT = (-0.475, -0.157)
DECOR = [
    kv.put("paper", (PAPER_AT[0], PAPER_AT[1], DZ), lift=0.0003, **kv.flat(86)),
    kv.put("pen", (-0.425, -0.262, DZ), lift=0.0006, **kv.flat(18)),
    kv.put("battery9v", (-0.548, -0.070, DZ), lift=0.0006, **kv.flat(64)),
    kv.put("ducttape", (0.515, 0.185, DZ), **kv.flat(0)),
    kv.put("electrickit", (L.TXC, 0.115, L.TZ1), **kv.flat(93)),
    kv.put("cassette", (L.MX + 0.075, L.MY0 + 0.054, L.MZ1), **kv.flat(95)),
    kv.put("cassette", (L.MX + 0.082, L.MY0 + 0.057, L.MZ1), lift=0.0105, **kv.flat(84)),
    kv.put("vodka", (0.09, -0.11, 0.0), up=(0, 0, 1), fwd=(0.3, -1, 0)),
]

M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 selections=(SEL_SCREEN, SEL_LAMP, SEL_BLINK, SEL_FAN), hidden=(SEL_SCREEN, SEL_LAMP, SEL_BLINK),
                 states={"on": ON}, bones=((SEL_FAN, ""),), animations=(FAN_ANIM,), decor=DECOR,
                 panels={"screen": SCREEN}, sources={"ozl_work": dict(animPeriod=2.5)})
P = M.part
BOUNDS = {}


def use(part, region):
    """The following primitives of the part go into another region."""
    return part.use(region, *REGIONS[region])


def cable(name, region, pts, r, lod, k=2):
    """A cable as a smooth curve (g.pipe, not g.tube: that one twists the rings)."""
    c = P(name, region)
    g.pipe(c, spline(pts, k) if lod == 0 else spline(pts, 1), r, 5 if lod == 0 else 4)
    return [c]


def led_dome(part, x, y, z, r, axis, lod):
    """LED - a dome on the body (axis points outward)."""
    if lod == 0:
        lathe(part, [(r, -0.0005), (r, 0.0008), (r * 0.7, 0.0018), (0.0, 0.0023)], 8, (x, y, z), axis)
    else:
        lathe(part, [(r, -0.0005), (r * 0.6, 0.0015)], 5, (x, y, z), axis, cap1=True)


# =============================================================================
# Table: two cases on end and plywood
# =============================================================================
def case_prof(k, grow=0.0):
    """Case outline in the y-z plane (a = y, b = z), grow - outward."""
    return rrect(L.CASE_Y, HC / 2, L.CASE[1] + 2 * grow, HC + 2 * grow, L.CASE_R + grow, k)


def build_cases(spec):
    lod = spec["lod"]
    parts = []
    k = 2 if lod == 0 else 1
    for i in (0, 1):
        x0, x1 = L.case_x(i)
        sx = L.seam_x(i)
        xo, so = L.case_out(i)                             # outer side (base bottom), outward
        if lod == 2:
            # far LOD is a box; the unwrap is the same part as in the near LOD (front and side in
            # the decals)
            body = P("case%d" % i, "case")
            g.box(body, x0, x1, L.CY0, L.CY1, 0.0, HC)
            parts.append(body)
            continue
        prof = case_prof(k)
        # base: from the bottom (rounded by CASE_END_R[0]) to the seam; lid: from the seam to the
        # top (CASE_END_R[1])
        body = P("case%d" % i, "case")
        lid = P("case%d_lid" % i, "case_plain")
        rb, rl = L.CASE_END_R
        # the ends at the seam are hidden in the rim: only a ring there (its edge shows through the
        # rim gap)
        if i == 0:
            loft(body, prof, "x", ends(x0, sx, rb, 0.004, k), cap1=0.012)
            loft(lid, prof, "x", ends(sx, x1, 0.004, rl, k), cap0=0.012)
        else:
            loft(lid, prof, "x", ends(x0, sx, rl, 0.004, k), cap1=0.012)
            loft(body, prof, "x", ends(sx, x1, 0.004, rb, k), cap0=0.012)
        parts += [body, lid]
        # seam rim: at the base and at the lid, a gap between them
        rim = P("case%d_rim" % i, "case_plain")
        rp = case_prof(k, L.RIM[0])
        for s in (-so, so):                                 # toward the lid, toward the base
            a, b = sorted((sx + s * 0.0015, sx + s * (0.0015 + L.RIM[1])))
            loft(rim, rp, "x", ends(a, b, 0.002, 0.002, 1) if lod == 0 else [(a, 0.0), (b, 0.0)],
                 cap0=L.RIM[0] + 0.006, cap1=L.RIM[0] + 0.006)
        parts.append(rim)
        hw = P("case%d_hw" % i, "case_hw")
        parts.append(hw)
        xi = x1 if i == 0 else x0                           # lid top (toward the table middle)
        si = -so
        # lid top: a convex cast panel
        pan = P("case%d_panel" % i, "case_plain")
        pp = rrect(L.CASE_Y, HC / 2, L.CASE[1] - 0.11, HC - 0.13, 0.03, k)
        a, b = sorted((xi - si * 0.001, xi + si * 0.006))
        loft(pan, pp, "x", ends(a, b, 0.0, 0.004, 1) if si > 0 else ends(a, b, 0.004, 0.0, 1))
        parts.append(pan)
        if lod > 0:
            for z in L.LATCH_Z:
                g.box(hw, sx - 0.03, sx + 0.03, L.CY0 - 0.016, L.CY0, z - 0.024, z + 0.024)
            continue
        y0 = L.CY0
        # double-action latches: a body on the base, a lever across the seam, a catch on the lid
        for z in L.LATCH_Z:
            xa, xb = sorted((sx + so * 0.004, sx + so * 0.034))
            g.box(hw, xa, xb, y0 - 0.011, y0 + 0.002, z - 0.027, z + 0.027, r=0.004, seg=1)
            xa, xb = sorted((sx - so * 0.024, sx + so * 0.030))
            g.box(hw, xa, xb, y0 - 0.019, y0 - 0.010, z - 0.022, z + 0.022, r=0.003, seg=1)
            g.cyl(hw, (sx - so * 0.020, y0 - 0.019, z), "z", 0.0055, 0.040, 8)               # lever roller
            xa, xb = sorted((sx - so * 0.028, sx - so * 0.006))
            g.box(hw, xa, xb, y0 - 0.009, y0 + 0.001, z - 0.018, z + 0.018)                  # catch
        # folding handle on the lid: two brackets and the grip arc
        hx = sx - so * 0.016
        zc = L.HANDLE_Z
        for s in (-1, 1):
            g.box(hw, hx - 0.014, hx + 0.014, y0 - 0.012, y0 + 0.002, zc + s * 0.07 - 0.012, zc + s * 0.07 + 0.012,
                  r=0.004, seg=1)
        path = spline([(hx, y0 - 0.006, zc - 0.068), (hx, y0 - 0.016, zc - 0.056), (hx, y0 - 0.020, zc - 0.03),
                       (hx, y0 - 0.020, zc + 0.03), (hx, y0 - 0.016, zc + 0.056), (hx, y0 - 0.006, zc + 0.068)], 2)
        g.tube_var(hw, path, [(0.0065, 0.0085)] * len(path), 6)
        # pressure valve at the upper corner of the base: a ring with a dome
        vx = xo - so * 0.05
        lathe(hw, [(0.016, 0.0), (0.016, 0.005), (0.010, 0.008), (0.004, 0.0105), (0.0, 0.011)], 10,
              (vx, y0 + 0.001, HC * 0.8), (0, -1, 0))
        # back hinge: four knuckles along the seam
        y1 = L.CY1
        for q in range(4):
            za = 0.06 + q * 0.13
            g.cyl(hw, (sx + (so if q % 2 else -so) * 0.004, y1 + 0.004, za + 0.06), "z", 0.0085, 0.118, 8)
        # wheels at the rear bottom corner of the base, axis along x
        wh = P("case%d_wheels" % i, "wheel")
        r, w = L.WHEEL
        for xw in (xo - so * (0.012 + w / 2), sx + so * (0.016 + w / 2)):
            lathe(wh, round_prof(r, -w / 2, w / 2, 0.006, 1, top=True, bottom=True), 10, (xw, y1 - 0.030, r), (1, 0, 0),
                  cap0=True, cap1=True)
        parts.append(wh)
    return parts


def build_plank(spec):
    wd = P("plank", "wood")
    fr = turn(0.0, 0.0, L.PZ0, L.PLANK_DEG)
    g.box(wd, L.PX0, L.PX1, L.PY0, L.PY1, 0.0, DZ - L.PZ0, frame=fr,
          **(dict(r=0.003, seg=2) if spec["lod"] == 0 else {}))
    return [wd]


# =============================================================================
# Monitor: a rounded body, a chamfered tube window, convex glass, a flare to the back, a stand
# =============================================================================
def build_monitor(spec):
    lod = spec["lod"]
    mx, y0, w = L.MX, L.MY0, L.MW / 2
    y1 = y0 + L.M_FRONT
    pw, ph, pr, pd = L.POCKET
    sz0, sz1 = L.SCR_Z - ph / 2, L.SCR_Z + ph / 2
    zc = (L.MZ0 + L.MZ1) / 2
    parts = []
    if lod == 0:
        base = P("mon_front_base", "beige")
        g.box(base, mx - w, mx + w, y0, y1, L.MZ0, L.MZ1, r=L.M_R, seg=2)
        cut = P("mon_pocket", "beige_dark")
        loft(cut, rrect(mx, L.SCR_Z, pw, ph, pr, 4), "y", [(y0 - 0.01, 0.0), (y0 + 0.004, 0.0), (y0 + pd, 0.008)])
        parts.append(M.boolean("mon_front", base, [cut]))
    elif lod == 1:
        fr = P("mon_front", "beige")
        sx0, sx1 = mx - pw / 2, mx + pw / 2
        g.box(fr, mx - w, sx0, y0, y1, L.MZ0, L.MZ1)
        g.box(fr, sx1, mx + w, y0, y1, L.MZ0, L.MZ1)
        g.box(fr, sx0, sx1, y0, y1, sz1, L.MZ1)
        g.box(fr, sx0, sx1, y0, y1, L.MZ0, sz0)
        pk = P("mon_pocket", "beige_dark")
        g.box(pk, sx0, sx1, y0 + pd - 0.004, y0 + pd, sz0, sz1)
        parts += [fr, pk]
    else:
        fr = P("mon_front", "beige")
        g.box(fr, mx - w, mx + w, y0, y1, L.MZ0, L.MZ1)
        parts.append(fr)
    # flare to the back: three rings of rounded rectangles; a hump with connectors
    bw, bz0, bz1 = L.M_BACK
    yb = y0 + L.MD - 0.04
    kk = 2 if lod == 0 else 1
    back = P("mon_back", "beige_plain")
    rings = [(y1 - 0.002, rrect(mx, zc, 2 * w - 0.012, L.MZ1 - L.MZ0 - 0.012, 0.02, kk)),
             (y1 + 0.09, rrect(mx, zc - 0.008, 2 * w - 0.05, L.MZ1 - L.MZ0 - 0.05, 0.045, kk)),
             (yb, rrect(mx, (bz0 + bz1) / 2, 2 * bw, bz1 - bz0, 0.035, kk))]
    if lod == 2:
        rings = [rings[0], rings[2]]
    hull(back, [(a, y, b) for y, ring in rings for a, b in ring])
    parts.append(back)
    if lod < 2:
        hump = P("mon_hump", "beige_plain")
        rbox(hump, mx - 0.08, mx + 0.08, yb - 0.01, y0 + L.MD - 0.002, bz0 + 0.008, bz0 + 0.115, 0.014, kk, rz=0.01)
        parts.append(hump)
    # tube glass has its own texture (the screen section): the mod script cycles the working frames
    sc = P("mon_screen", "screen", group=SEL_SCREEN, section="screen")
    y_edge = y0 + pd - 0.001
    if lod == 2:
        y_edge = y0 - 0.002
        g.quad(sc, [(mx - L.SCR_W / 2, y_edge, L.SCR_Z - L.SCR_H / 2), (mx + L.SCR_W / 2, y_edge, L.SCR_Z - L.SCR_H / 2),
                    (mx + L.SCR_W / 2, y_edge, L.SCR_Z + L.SCR_H / 2), (mx - L.SCR_W / 2, y_edge, L.SCR_Z + L.SCR_H / 2)])
    else:
        bulge_rr(sc, mx, y_edge, L.SCR_Z, L.SCR_W, L.SCR_H, L.SCR_R, 4 if lod == 0 else 1, L.SCR_SAG, 3 if lod == 0 else 2)
    sc.glass_frame = (g.Frame((mx, y_edge, L.SCR_Z), (1, 0, 0), (0, 0, 1), (0, -1, 0)), -L.SCR_W / 2, L.SCR_W / 2,
                      -L.SCR_H / 2, L.SCR_H / 2)
    parts.append(sc)
    ld = P("mon_led", "led_g", group=SEL_LAMP)
    lx, lz = L.M_LED
    if lod == 2:
        g.quad(ld, [(lx - 0.003, y0 - 0.001, lz - 0.003), (lx + 0.003, y0 - 0.001, lz - 0.003),
                    (lx + 0.003, y0 - 0.001, lz + 0.003), (lx - 0.003, y0 - 0.001, lz + 0.003)])
    else:
        led_dome(ld, lx, y0, lz, 0.0028, (0, -1, 0), lod)
    parts.append(ld)
    # stand: a disc with a rounded edge and a neck
    st = P("mon_stand", "beige_dark")
    by = L.M_STAND_Y
    if lod < 2:
        prof = [(0.118, 0.0), (0.121, 0.003), (0.119, 0.008), (0.110, 0.013), (0.080, 0.019), (0.062, 0.022)]
        lathe(st, prof if lod == 0 else prof[::2] + [prof[-1]], 20 if lod == 0 else 10, (mx, by, DZ), cap1=True)
        rbox(st, mx - 0.062, mx + 0.062, by - 0.06, by + 0.05, DZ + 0.018, L.MZ0 + 0.03, 0.014 if lod == 0 else 0.0,
             2 if lod == 0 else 1, rz=0.0)
    else:
        g.box(st, mx - 0.06, mx + 0.06, by - 0.06, by + 0.05, DZ, L.MZ0 + 0.02)
    parts.append(st)
    if lod > 0:
        return parts
    bt = P("mon_buttons", "beige_dark")
    for q in range(4):                                                               # menu buttons
        button(bt, mx - 0.075 + 0.026 * q, L.MZ0 + 0.026, 0.017, 0.008, y0, 0.0028, 0.0008)
    lathe(bt, [(0.0095, -0.001), (0.0095, 0.0025), (0.0075, 0.0045), (0.0, 0.005)], 14,
          (mx + 0.125, y0, L.MZ0 + 0.026), (0, -1, 0))                                # power button
    parts.append(bt)
    dk = P("mon_slots", "black")
    # vent slots on the roof of the flare, along the slope between the first and second rings
    (ya, _), (yb2, _) = rings[0], rings[1]
    za, zb = L.MZ1 - 0.006, zc - 0.008 + (L.MZ1 - L.MZ0 - 0.05) / 2
    for q in range(6):
        yy = ya + 0.012 + 0.013 * q
        zt = za + (yy - ya) / (yb2 - ya) * (zb - za)
        g.box(dk, mx - 0.11, mx + 0.11, yy - 0.0035, yy + 0.0035, zt - 0.003, zt + 0.0006)
    # on the hump: slots on the back, the power socket
    for q in range(5):
        zz = bz0 + 0.05 + 0.011 * q
        g.box(dk, mx - 0.055, mx + 0.055, y0 + L.MD - 0.0025, y0 + L.MD - 0.0010, zz - 0.0028, zz + 0.0028)
    rbox(dk, mx + 0.04, mx + 0.066, y0 + L.MD - 0.004, y0 + L.MD + 0.002, bz0 + 0.02, bz0 + 0.04, 0.003, 1)
    parts.append(dk)
    return parts


# =============================================================================
# System unit: mini-tower
# =============================================================================
TC = {                                                     # back connectors: x, z
    "power": (L.TX0 + 0.045, L.TZ1 - 0.045), "kbd": (L.TX0 + 0.030, DZ + 0.235), "mouse": (L.TX0 + 0.075, DZ + 0.235),
    "vga": (L.TX0 + 0.105, DZ + 0.125), "audio": (L.TX0 + 0.135, DZ + 0.095),
}


def build_tower(spec):
    lod = spec["lod"]
    x0, x1, y0, y1, z1 = L.TX0, L.TX1, L.TY0, L.TY1, L.TZ1
    yf = y0 + L.T_BEZEL
    tw = P("tower", "beige")                                                      # shell (side decals)
    bz = P("tower_bezel", "beige")                                                # front panel (bottom decals)
    parts = [tw, bz]
    if lod == 2:
        g.box(tw, x0, x1, yf, y1, DZ, z1)
        g.box(bz, x0, x1, y0, yf, DZ, z1)
    else:
        k = 2 if lod == 0 else 1
        rbox(tw, x0, x1, yf - 0.004, y1, DZ + 0.006, z1, 0.004, k)
        rbox(bz, x0 - 0.002, x1 + 0.002, y0, yf, DZ + 0.004, z1 + 0.003, 0.008, k)
    leds = P("tower_led", "led_g", group=SEL_LAMP)
    hdd = P("tower_hdd", "led_a", group=SEL_BLINK)
    for (lx, lz, c), part in zip(L.T_LEDS, (leds, hdd)):
        if lod == 2:
            g.quad(part, [(lx - 0.003, y0 - 0.001, lz - 0.002), (lx + 0.003, y0 - 0.001, lz - 0.002),
                          (lx + 0.003, y0 - 0.001, lz + 0.002), (lx - 0.003, y0 - 0.001, lz + 0.002)])
        else:
            led_dome(part, lx, y0, lz, 0.0026, (0, -1, 0), lod)
    parts += [leds, hdd]
    parts += build_fan(spec)
    if lod == 2:
        return parts
    dk = P("tower_bays", "beige_dark")
    bx0, bx1 = L.BAY_X
    fx0, fx1, fz0, fz1 = L.FDD
    rbox(dk, bx0, bx1, y0 - 0.003, y0 + 0.002, L.BAYS[0], L.BAYS[1], 0.002, 1, rz=0.002)          # CD drive
    rbox(dk, bx0 + 0.002, bx1 - 0.002, y0 - 0.0015, y0 + 0.002, L.BAYS[2], L.BAYS[3], 0.002, 1, rz=0.002)  # blank
    rbox(dk, fx0, fx1, y0 - 0.003, y0 + 0.002, fz0, fz1, 0.002, 1, rz=0.002)                    # FDD
    parts.append(dk)
    if lod == 1:
        return parts
    bk = P("tower_bits", "black")
    # CD tray (a gap around the perimeter), the floppy slot with a shutter
    g.box(bk, bx0 + 0.008, bx1 - 0.036, y0 - 0.0034, y0 - 0.0026, L.BAYS[0] + 0.009, L.BAYS[0] + 0.0105)
    g.box(bk, bx0 + 0.008, bx1 - 0.036, y0 - 0.0034, y0 - 0.0026, L.BAYS[1] - 0.006, L.BAYS[1] - 0.0045)
    g.box(bk, fx0 + 0.010, fx1 - 0.016, y0 - 0.0034, y0 - 0.0024, fz0 + 0.012, fz0 + 0.018)
    g.cyl(bk, (bx0 + 0.012, y0 - 0.003, L.BAYS[0] + 0.005), "y", 0.0022, 0.002, 8)               # headphone jack
    # louvres on the left side near the front, at the bottom
    for c in range(2):
        for q in range(6):
            yy = y0 + 0.05 + c * 0.03
            zz = DZ + 0.04 + q * 0.016
            g.box(bk, x0 - 0.0006, x0 + 0.002, yy - 0.011, yy + 0.011, zz - 0.0025, zz + 0.0025)
    parts.append(bk)
    sh = P("tower_shutter", "beige_dark")
    g.box(sh, fx0 + 0.011, fx1 - 0.017, y0 - 0.0030, y0 - 0.0020, fz0 + 0.0125, fz0 + 0.0175)
    parts.append(sh)
    bt = P("tower_buttons", "beige_dark")
    px, pz = L.T_POWER
    lathe(bt, [(0.0135, -0.001), (0.0135, 0.002), (0.0115, 0.0045), (0.0, 0.006)], 16, (px, y0, pz), (0, -1, 0))
    g.cyl(bt, (px, y0 - 0.0005, pz), "y", 0.016, 0.001, 16)                                      # rim
    button(bt, px, pz - 0.032, 0.012, 0.007, y0, 0.002, 0.0007)                                 # reset
    button(bt, bx1 - 0.017, L.BAYS[0] + 0.008, 0.014, 0.005, y0 - 0.003, 0.0018, 0.0006)        # open the tray
    button(bt, fx1 - 0.011, fz0 + 0.006, 0.010, 0.005, y0 - 0.003, 0.0018, 0.0006)              # floppy eject
    parts.append(bt)
    # feet
    rb = P("tower_feet", "rubber")
    for x in (x0 + 0.022, x1 - 0.022):
        for y in (y0 + 0.035, y1 - 0.03):
            g.cyl(rb, (x, y, DZ + 0.003), "z", 0.011, 0.006, 8)
    parts.append(rb)
    # back: the PSU (a plate with a socket), card slot covers, connectors, shell screws
    mt = P("tower_back", "metal")
    g.box(mt, x0 + 0.008, x1 - 0.008, y1 - 0.001, y1 + 0.0015, z1 - 0.15, z1 - 0.012)
    for q in range(6):                                                                           # slot covers
        xs = x0 + 0.06 + q * 0.021
        g.box(mt, xs - 0.008, xs + 0.008, y1 - 0.001, y1 + 0.0025, DZ + 0.03, DZ + 0.165)
    g.box(mt, x0 + 0.012, x0 + 0.105, y1 - 0.001, y1 + 0.0015, DZ + 0.205, DZ + 0.27)           # connector panel
    for x in (x0 + 0.012, x1 - 0.012):                                                           # shell screws
        for z in (DZ + 0.03, z1 - 0.012):
            g.cyl(mt, (x, y1 + 0.002, z), "y", 0.0035, 0.004, 8)
    parts.append(mt)
    cn = P("tower_ports", "black")
    rbox(cn, TC["power"][0] - 0.014, TC["power"][0] + 0.014, y1, y1 + 0.004, TC["power"][1] - 0.010,
         TC["power"][1] + 0.010, 0.002, 1)
    g.cyl(cn, (TC["kbd"][0], y1 + 0.002, TC["kbd"][1]), "y", 0.0075, 0.004, 12)
    g.box(cn, TC["mouse"][0] - 0.012, TC["mouse"][0] + 0.012, y1, y1 + 0.004, TC["mouse"][1] - 0.005, TC["mouse"][1] + 0.005)
    g.box(cn, TC["vga"][0] - 0.010, TC["vga"][0] + 0.010, y1, y1 + 0.004, TC["vga"][1] - 0.005, TC["vga"][1] + 0.005)
    for q in range(3):
        g.cyl(cn, (TC["audio"][0], y1 + 0.003, TC["audio"][1] + q * 0.016), "y", 0.004, 0.003, 10)
    parts.append(cn)
    return parts


def build_fan(spec):
    """An 80 mm PSU fan behind a grille (the ozl_fan bone spins, the grille stands still)."""
    lod = spec["lod"]
    fx, fz, r = L.FAN
    y = L.TY1
    parts = []
    hole = P("fan_hole", "black")
    g.cyl(hole, (fx, y + 0.0012, fz), "y", r + 0.002, 0.0006, 16 if lod == 0 else 8)
    parts.append(hole)
    fan = P("fan", "fan", group=SEL_FAN)
    nb = 7 if lod < 2 else 3
    g.cyl(fan, (fx, y + 0.0025, fz), "y", 0.014, 0.003, 12 if lod == 0 else 6)
    for q in range(nb):
        a = 2 * math.pi * q / nb
        # blade: a quadrilateral from the hub to the rim, turned along the rotation and tilted
        pts = []
        for rr, da, dy in ((0.013, -0.18, 0.0010), (0.013, 0.22, -0.0010), (r - 0.002, 0.38, -0.0012), (r - 0.002, -0.28, 0.0012)):
            pts.append((fx + rr * math.cos(a + da), y + 0.0025 + dy, fz + rr * math.sin(a + da)))
        if lod == 0:
            g.prism(fan, [(p[0], p[2]) for p in pts], (0, 2), y + 0.0018, y + 0.0032)
        else:
            g.quad(fan, [pts[0], pts[1], pts[2], pts[3]])
    parts.append(fan)
    if lod < 2:
        gr = P("fan_grille", "metal")
        rings = (0.019, r) if lod == 0 else (r,)
        for rr in rings:
            n = 16 if lod == 0 else 8
            g.pipe(gr, [(fx + rr * math.cos(2 * math.pi * q / n), y + 0.0055, fz + rr * math.sin(2 * math.pi * q / n))
                        for q in range(n + 1)], 0.0012, 3)
        for a in (math.pi / 4, 3 * math.pi / 4):
            g.pipe(gr, [(fx - r * math.cos(a), y + 0.0055, fz - r * math.sin(a)),
                        (fx + r * math.cos(a), y + 0.0055, fz + r * math.sin(a))], 0.0012, 3)
        parts.append(gr)
    return parts


# =============================================================================
# Keyboard, mouse, speakers
# =============================================================================
KSLOPE = math.atan2(L.KZ_B - L.KZ_F, L.KY1 - L.KY0)


def build_keyboard(spec):
    lod = spec["lod"]
    parts = []
    kb = P("kbd_case", "beige_plain")
    prof = [(L.KY0, DZ), (L.KY1, DZ), (L.KY1, L.KZ_B), (L.KY0, L.KZ_F)]
    if lod == 0:
        loft(kb, fillet_poly(prof, (0.003, 0.003, 0.007, 0.010), 3), "x", ends(L.KX0, L.KX1, 0.004, 0.004, 2))
    else:
        g.prism(kb, prof, (1, 2), L.KX0, L.KX1)
    parts.append(kb)
    if lod == 2:
        return parts
    pl = P("kbd_plate", "keyboard")
    ya, yb = L.KEYS[2] - 0.003, L.KEYS[3] + 0.003
    g.prism(pl, [(ya, L.key_zs(ya) - 0.002), (yb, L.key_zs(yb) - 0.002), (yb, L.key_zs(yb) + 0.0015),
                 (ya, L.key_zs(ya) + 0.0015)], (1, 2), L.KEYS[0] - 0.003, L.KEYS[1] + 0.003)
    parts.append(pl)
    ld = P("kbd_leds", "led_g", group=SEL_LAMP)
    for lx, ly in L.K_LEDS:
        z = L.key_zs(ly)
        g.box(ld, lx - 0.0028, lx + 0.0028, ly - 0.0018, ly + 0.0018, z - 0.0005, z + 0.0009)
    parts.append(ld)
    if lod == 1:
        return parts
    kk = {False: P("kbd_keys", "key_beige"), True: P("kbd_keys_grey", "key_grey")}
    for x0, x1, y0, y1, grey in L.key_rects():
        keycap(kk[grey], x0, x1, y0, y1, 0.0088, 0.0013, lambda y: L.key_zs(y) + 0.0015, KSLOPE)
    parts += list(kk.values())
    return parts


def build_desk_bits(spec):
    """Mouse pad and mouse, mug, floppies, radio handset."""
    lod, n = spec["lod"], spec["sides"]
    parts = []
    x0, x1, y0, y1 = L.PAD
    pd = P("mousepad", "mousepad")
    fr = turn((x0 + x1) / 2, (y0 + y1) / 2, DZ, 4.0)
    if lod < 2:
        loft(pd, rrect(0, 0, x1 - x0, y1 - y0, 0.012, 2 if lod == 0 else 1), "z",
             ends(0.0, 0.003, 0.0, 0.0012 if lod == 0 else 0.0, 1), frame=fr)
        parts.append(pd)
    # mouse: cast, with two buttons and the cord forward
    mx, my, md = L.MOUSE
    fr = turn(mx, my, DZ + 0.003, md + 90.0)
    ms = P("mouse", "beige_plain")
    secs = [(-0.055, 0.012, 0.010, 0), (-0.052, 0.022, 0.020, 0), (-0.042, 0.029, 0.029, 0), (-0.025, 0.0315, 0.034, 0),
            (0.0, 0.0315, 0.035, 0), (0.025, 0.030, 0.031, 0), (0.042, 0.027, 0.024, 0), (0.051, 0.022, 0.016, 0),
            (0.0555, 0.013, 0.007, 0)]
    if lod == 2:
        g.box(ms, -0.055, 0.055, -0.031, 0.031, 0.0, 0.032, frame=fr)
    else:
        blob(ms, secs if lod == 0 else secs[::2], frame=fr)
    parts.append(ms)
    if lod == 0:
        sm = P("mouse_seams", "black")

        def top(u, x):
            for (ua, wa, ha, _), (ub, wb, hb, _) in zip(secs, secs[1:]):
                if ua <= u <= ub:
                    t = (u - ua) / (ub - ua)
                    hw, h = wa + (wb - wa) * t, ha + (hb - ha) * t
                    c = max(-1.0, min(1.0, x / hw))
                    return h * math.sqrt(max(0.0, 1 - c * c)) ** 0.75
            return 0.0
        g.pipe(sm, [tuple(fr.p(u, 0.0, top(u, 0.0) - 0.0002)) for u in (0.004, 0.02, 0.035, 0.047, 0.054)], 0.0006, 4)
        g.pipe(sm, [tuple(fr.p(0.004, x, top(0.004, x) - 0.0002)) for x in (-0.026, -0.015, 0.0, 0.015, 0.026)],
               0.0006, 4)
        parts.append(sm)
    # mug: a wall with a rim, the inside, coffee, a handle
    cx, cy, r, h = L.MUG
    mg = P("mug", "mug")
    if lod == 0:
        lathe(mg, [(r - 0.006, 0.0), (r - 0.002, 0.0015), (r - 0.0005, 0.006), (r, 0.088), (r + 0.0003, h - 0.0025),
                   (r - 0.0015, h), (r - 0.0035, h - 0.0012), (r - 0.0040, h - 0.012), (r - 0.0045, h - 0.02)],
              24, (cx, cy, DZ), cap0=True)
    else:
        g.cyl(mg, (cx, cy, DZ + h / 2), "z", r, h, max(6, n))
    parts.append(mg)
    if lod < 2:
        cf = P("mug_coffee", "coffee")
        g.cyl(cf, (cx, cy, DZ + h - (0.02 if lod == 0 else -0.0005)), "z", r - 0.004, 0.001, 24 if lod == 0 else n)
        parts.append(cf)
        hd = P("mug_handle", "mug")
        path = [(cx + r - 0.004, cy, DZ + h - 0.018), (cx + r + 0.020, cy, DZ + h - 0.022),
                (cx + r + 0.027, cy, DZ + h * 0.55), (cx + r + 0.018, cy, DZ + 0.026), (cx + r - 0.004, cy, DZ + 0.022)]
        pts = spline(path, 3) if lod == 0 else path
        g.tube_var(hd, pts, [(0.0065, 0.0045)] * len(pts), 8 if lod == 0 else 4)
        parts.append(hd)
    if lod > 0:
        return parts
    # floppies in a crooked stack on a sheet: a cut corner, a shutter, a label
    fx, fy = L.FLOPPY
    poly = [(-0.045, -0.047), (0.045, -0.047), (0.045, 0.043), (0.041, 0.047), (-0.045, 0.047)]
    for k, (reg, deg) in enumerate((("floppy", -7.0), ("floppy_blue", 9.0), ("floppy", 22.0))):
        fd = P("floppy%d" % k, reg)
        fr = turn(fx + 0.008 * k, fy + 0.005 * k, DZ + 0.0006 + 0.0034 * k, deg)
        g.prism(fd, poly, (0, 1), 0.0, 0.0033, frame=fr)
        parts.append(fd)
        sh = P("floppy%d_bits" % k, "metal")
        g.box(sh, -0.025, 0.012, 0.010, 0.0475, -0.0003, 0.0037, frame=fr)
        use(sh, "label")
        g.box(sh, -0.037, 0.037, -0.044, -0.004, 0.0033, 0.0036, frame=fr)
        parts.append(sh)
    return parts


def build_speakers(spec):
    lod = spec["lod"]
    parts = []
    w, d, h = L.SPK
    for i, (cx, cy, deg) in enumerate(L.SPEAKERS):
        fr = turn(cx, cy, DZ, deg)
        sp = P("speaker%d" % i, "beige_plain")
        gr = P("speaker%d_grille" % i, "grille")
        if lod == 2:
            g.box(sp, -w / 2, w / 2, -d / 2, d / 2, 0.0, h, frame=fr)
            parts.append(sp)
            continue
        rbox(sp, -w / 2, w / 2, -d / 2, d / 2, 0.0, h, 0.006 if lod == 0 else 0.0, 2 if lod == 0 else 1, frame=fr)
        gp = rrect(0.0, (0.052 + h - 0.012) / 2, w - 0.018, h - 0.064, 0.008, 2 if lod == 0 else 1)
        loft(gr, gp, "y", [(-d / 2 - 0.0022, 0.0015), (-d / 2 - 0.0008, 0.0), (-d / 2 + 0.002, 0.0)], frame=fr)
        parts += [sp, gr]
        if lod == 0 and i == 1:
            kn = P("speaker_knob", "knob")
            lathe(kn, [(0.0115, -0.001), (0.0115, 0.006), (0.0100, 0.0095), (0.0, 0.010)], 14,
                  (0.016, -d / 2, 0.027), (0, -1, 0), frame=fr)
            g.box(kn, 0.015, 0.017, -d / 2 - 0.0102, -d / 2 - 0.0095, 0.031, 0.036, frame=fr)    # tick
            parts.append(kn)
            ld = P("speaker_led", "led_r", group=SEL_LAMP)
            p0 = fr.p(-0.024, -d / 2, 0.027)
            led_dome(ld, p0.x, p0.y, p0.z, 0.0025, tuple(-fr.v), lod)
            parts.append(ld)
    return parts


# =============================================================================
# Radio of the AN/PRC-77 class: a battery box on latches, the transceiver, the top panel, a tape
# antenna
# =============================================================================
def build_radio(spec):
    lod, n = spec["lod"], spec["sides"]
    x0, x1, y0, y1, z1 = L.RX0, L.RX1, L.RY0, L.RY1, L.RZ1
    zb = L.R_BAT
    rd = P("radio", "radio")
    parts = [rd]
    lp = P("radio_lamp", "led_a", group=SEL_BLINK)
    lx, ly = L.R_LAMP
    ax, ay = L.ANT
    za = z1 + L.ANT_BASE
    an = P("radio_antenna", "tape_ant")
    apts = [(ax + dx, ay + dy, za + dz) for dx, dy, dz in L.ANT_PATH]
    if lod == 2:
        g.box(rd, x0, x1, y0, y1, DZ, z1)
        g.quad(lp, [(lx - 0.004, ly - 0.004, z1 + 0.001), (lx + 0.004, ly - 0.004, z1 + 0.001),
                    (lx + 0.004, ly + 0.004, z1 + 0.001), (lx - 0.004, ly + 0.004, z1 + 0.001)])
        g.pipe(an, [(ax, ay, z1)] + apts[::2], 0.005, 3)
        return parts + [lp, an]
    k = 2 if lod == 0 else 1
    rbox(rd, x0, x1, y0, y1, DZ, zb - 0.002, 0.008 if lod == 0 else 0.0, k, rz=0.005 if lod == 0 else 0.0)  # box
    rbox(rd, x0 + 0.002, x1 - 0.002, y0 + 0.002, y1 - 0.002, zb + 0.002, z1 - 0.004, 0.008 if lod == 0 else 0.0, k,
         rz=0.004 if lod == 0 else 0.0)                                                                   # body
    band = P("radio_band", "radio_plain")
    rbox(band, x0 - 0.003, x1 + 0.003, y0 - 0.003, y1 + 0.003, zb - 0.006, zb + 0.004, 0.010 if lod == 0 else 0.0, 1,
         rz=0.002 if lod == 0 else 0.0)
    parts.append(band)
    pn = P("radio_panel", "radio_panel")
    rbox(pn, x0 + 0.004, x1 - 0.004, y0 + 0.004, y1 - 0.004, z1 - 0.008, z1, 0.006 if lod == 0 else 0.0, 1,
         rz=0.0015 if lod == 0 else 0.0)
    parts.append(pn)
    if lod == 0:
        lathe(lp, [(0.0055, 0.0), (0.0055, 0.003), (0.0045, 0.006), (0.0025, 0.0085), (0.0, 0.009)], 10, (lx, ly, z1))
    else:
        g.cyl(lp, (lx, ly, z1 + 0.004), "z", 0.0045, 0.008, 5)
    parts.append(lp)
    # knobs: frequency (two large ones with a skirt), mode, volume
    kn = P("radio_knobs", "knob")
    for q, (kx_, ky_, r) in enumerate(L.R_KNOBS):
        if lod == 0:
            hk = 0.017 if q < 2 else 0.013
            lathe(kn, [(r + 0.004, 0.0), (r + 0.004, 0.003), (r, 0.006), (r, hk), (r * 0.8, hk + 0.002), (0.0, hk + 0.002)],
                  12, (kx_, ky_, z1))
            hgt = 0.019 if q < 2 else 0.015
            g.box(kn, kx_ - 0.0012, kx_ + 0.0012, ky_ - r * 0.75, ky_ + 0.002, z1 + hgt - 0.0005, z1 + hgt + 0.002)  # pointer
        else:
            g.cyl(kn, (kx_, ky_, z1 + 0.009), "z", r, 0.018, n)
    # antenna socket: a nut and the AB-591 spring base
    if lod == 0:
        lathe(kn, [(0.015, 0.0), (0.015, 0.009), (0.012, 0.012), (0.009, 0.013)], 6, (ax, ay, z1), cap1=True)
        sp = [(0.0085, 0.013)]
        for q in range(9):
            sp.append((0.0085 if q % 2 else 0.0072, 0.016 + q * (L.ANT_BASE - 0.026) / 8))
        sp += [(0.0045, L.ANT_BASE), (0.0, L.ANT_BASE + 0.002)]
        lathe(kn, sp, 8, (ax, ay, z1))
    else:
        g.cyl(kn, (ax, ay, z1 + L.ANT_BASE / 2), "z", 0.009, L.ANT_BASE, n)
    parts.append(kn)
    # AT-892 antenna - a steel tape bent in an arc sideways (the width is across the bend, along y)
    ribbon(an, spline(apts, 3) if lod == 0 else apts, (0, 1, 0), 0.0065, 0.0006)
    parts.append(an)
    if lod == 1:
        return parts
    # frequency scale windows, headset connectors (U-229: a bushing with lugs; the first has the
    # handset plug, the second a cap)
    dl = P("radio_dials", "dial")
    for kx_, ky_, r in L.R_KNOBS[:2]:
        rbox(dl, x1 - 0.026, x1 - 0.010, ky_ - 0.011, ky_ + 0.011, z1 - 0.002, z1 + 0.0012, 0.002, 1, rz=0.0)
    parts.append(dl)
    cn = P("radio_conn", "metal")
    for q, (cx_, cy_) in enumerate(L.R_AUDIO):
        lathe(cn, [(0.0115, 0.0), (0.0115, 0.004), (0.0098, 0.005), (0.0098, 0.014), (0.0088, 0.016)], 10, (cx_, cy_, z1),
              cap1=q == 1)
        for s in (-1, 1):                                                            # bayonet lugs
            g.box(cn, cx_ + s * 0.0098 - 0.0012, cx_ + s * 0.0098 + 0.0012, cy_ - 0.0015, cy_ + 0.0015, z1 + 0.010,
                  z1 + 0.013)
    pg = P("radio_plug", "black")
    cx_, cy_ = L.R_AUDIO[0]
    lathe(pg, [(0.0125, 0.012), (0.0125, 0.024), (0.0105, 0.028), (0.006, 0.034), (0.0042, 0.045), (0.0, 0.046)], 10,
          (cx_, cy_, z1))
    cx_, cy_ = L.R_AUDIO[1]
    lathe(pg, [(0.0122, 0.012), (0.0122, 0.020), (0.0100, 0.022), (0.0, 0.0225)], 10, (cx_, cy_, z1))
    g.pipe(pg, spline([(cx_ + 0.0122, cy_, z1 + 0.017), (cx_ + 0.02, cy_ + 0.004, z1 + 0.012),
                       (cx_ + 0.022, cy_ + 0.012, z1 + 0.004)], 3), 0.0009, 4)          # cap chain
    parts += [cn, pg]
    # panel screws
    sw = P("radio_screws", "metal")
    for x in (x0 + 0.010, x1 - 0.010):
        for y in (y0 + 0.010, y1 - 0.010):
            g.cyl(sw, (x, y, z1 + 0.0004), "z", 0.0032, 0.0012, 6)
    parts.append(sw)
    # battery box latches: two per side, a lever across the joint onto the body, a catch roller
    cl = P("radio_clamps", "radio_plain")
    ym = (y0 + y1) / 2
    for xs, s in ((x0, -1), (x1, 1)):
        for dy in (-0.075, 0.075):
            yc = ym + dy
            xa, xb = sorted((xs, xs + s * 0.006))
            g.box(cl, xa, xb, yc - 0.017, yc + 0.017, zb - 0.040, zb - 0.010)
            xa, xb = sorted((xs + s * 0.004, xs + s * 0.0085))
            g.box(cl, xa, xb, yc - 0.013, yc + 0.013, zb - 0.030, zb + 0.022, r=0.0018, seg=1)
            g.cyl(cl, (xs + s * 0.006, yc, zb + 0.020), "y", 0.0035, 0.024, 6)
    parts.append(cl)
    return parts


def handset_frame():
    hx, hy, hdg = L.HANDSET
    return turn(hx, hy, DZ + 0.0006, hdg)


def build_handset(spec):
    """H-189 class handset lying on a sheet: capsules down, the grip in an arc, a push-to-talk bar
    at the side, a coiled cord to the headset connector of the radio.
    """
    lod = spec["lod"]
    if lod == 2:
        return []
    fr = handset_frame()
    hs = P("handset", "black")
    n = 12 if lod == 0 else 6
    ear = [(0.018, 0.0), (0.026, 0.003), (0.0285, 0.010), (0.027, 0.019), (0.019, 0.027), (0.012, 0.030)]
    mouth = [(0.014, 0.0), (0.020, 0.003), (0.0215, 0.010), (0.019, 0.018), (0.012, 0.024)]
    lathe(hs, ear if lod == 0 else ear[::2], n, (0.085, 0.0, 0.0), (0, 0, 1), cap0=True, frame=fr)
    lathe(hs, mouth if lod == 0 else mouth[::2], n, (-0.088, 0.0, 0.0), (0, 0, 1), cap0=True, frame=fr)
    path = [(0.080, 0.0, 0.026), (0.045, 0.0, 0.038), (0.0, 0.0, 0.041), (-0.045, 0.0, 0.037), (-0.083, 0.0, 0.022)]
    pts = [tuple(fr.p(*q)) for q in (spline(path, 2) if lod == 0 else path)]
    g.tube_var(hs, pts, [(0.0115, 0.0095)] * len(pts), 8 if lod == 0 else 5)
    parts = [hs]
    if lod == 0:
        pt = P("handset_ptt", "rubber")
        rbox(pt, -0.028, 0.026, -0.0135, -0.006, 0.030, 0.045, 0.003, 1, rz=0.002, frame=fr)
        parts.append(pt)
        # cord bushing at the microphone capsule
        lathe(hs, [(0.0055, 0.0), (0.0048, 0.010), (0.0035, 0.018)], 8, (-0.100, 0.0, 0.012), (-1, 0, 0), frame=fr)
    # cord: along the table to the radio, a spiral up its face, into the headset connector plug
    he = fr.p(-0.118, 0.0, 0.012)
    cx_, cy_ = L.R_AUDIO[0]
    z1 = L.RZ1
    flat_run = [tuple(he), (he.x - 0.015, he.y + 0.025, DZ + 0.005), (L.RX0 + 0.02, L.RY0 - 0.075, DZ + 0.005),
                (L.RX0 + 0.024, L.RY0 - 0.040, DZ + 0.03)]
    rise = [(L.RX0 + 0.024, L.RY0 - 0.040, DZ + 0.03), (L.RX0 + 0.026, L.RY0 - 0.022, DZ + 0.12),
            (L.RX0 + 0.028, L.RY0 - 0.016, z1 - 0.02)]
    top = [(L.RX0 + 0.028, L.RY0 - 0.016, z1 - 0.02), (L.RX0 + 0.029, L.RY0 - 0.006, z1 + 0.035),
           (cx_, cy_ - 0.004, z1 + 0.058), (cx_, cy_, z1 + 0.046)]
    cd = P("handset_cord", "black")
    if lod == 0:
        g.pipe(cd, spline(flat_run, 3), 0.0026, 5)
        coil(cd, spline(rise, 4), 0.0055, 0.0115, 0.0017, 5, 3)
        g.pipe(cd, spline(top, 3), 0.0026, 5)
    else:
        g.pipe(cd, flat_run + rise[1:] + top[1:], 0.004, 4)
    parts.append(cd)
    return parts


# =============================================================================
# Wires, tangle, power strip, insulating tape
# =============================================================================
def strip_frame():
    sx, sy, sd = L.STRIP
    return turn(sx, sy, 0.0, sd)


def build_wires(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    yb = L.MY0 + L.MD                                                              # monitor back
    tb = L.TY1 + 0.004                                                             # system unit back
    yp = 0.31                                                                      # beyond plywood
    # power strip on the floor between the cases, at the back: sockets on top, plugs in three, a key
    # with a lamp
    fr = strip_frame()
    st = P("power_strip", "strip")
    rbox(st, -0.15, 0.15, -0.028, 0.028, 0.0, 0.040, 0.010 if lod == 0 else 0.0, 2 if lod == 0 else 1,
         rz=0.006 if lod == 0 else 0.0, frame=fr)
    parts.append(st)
    sp = [fr.p(-0.09 + 0.06 * k, 0.0, 0.040) for k in range(4)]                   # sockets
    tops = [tuple(fr.p(-0.09 + 0.06 * k, 0.0, 0.040 + 0.030)) for k in range(4)]  # plug tops
    if lod == 0:
        sk = P("strip_sockets", "strip_dark")
        for p in sp:
            g.cyl(sk, (p.x, p.y, p.z + 0.0002), "z", 0.0175, 0.001, 10)
        g.cyl(sk, tuple(fr.p(0.09, 0.0, 0.0404)), "z", 0.0035, 0.002, 6)          # empty socket: holes
        parts.append(sk)
        pl = P("strip_plugs", "black")
        for p in sp[:3]:
            lathe(pl, [(0.019, 0.0), (0.019, 0.004), (0.0155, 0.007), (0.015, 0.025), (0.0, 0.030)], 10,
                  (p.x, p.y, p.z))
        parts.append(pl)
        sw = P("strip_switch", "led_r", group=SEL_LAMP)
        rbox(sw, 0.118, 0.140, -0.011, 0.011, 0.038, 0.046, 0.003, 1, rz=0.002, frame=fr)
        parts.append(sw)
    # power strip cord to the wall behind the table
    parts += cable("cable_strip", "cable", [tuple(fr.p(0.15, 0.0, 0.02)), tuple(fr.p(0.18, 0.02, 0.006)),
                                           (0.22, 0.30, 0.006), (0.25, 0.42, 0.006)], 0.004, lod)
    # power of the monitor and the system unit: from the back along the plywood edge down to the
    # plugs
    pts = [(L.MX + 0.053, yb + 0.010, L.M_BACK[1] + 0.03), (L.MX + 0.06, yb + 0.03, L.MZ0 + 0.02),
           (L.MX + 0.08, yp + 0.012, DZ - 0.005), (L.MX + 0.10, yp + 0.03, 0.45), (0.0, 0.26, 0.18),
           (tops[0][0], tops[0][1] - 0.02, 0.11), tops[0]]
    parts += cable("cable_mon_power", "cable", pts, 0.0035, lod)
    px, pz = TC["power"]
    pts = [(px, tb + 0.012, pz), (px + 0.01, tb + 0.04, pz - 0.06), (L.TX0 + 0.12, yp + 0.02, DZ - 0.01),
           (0.18, yp + 0.04, 0.40), (0.14, 0.27, 0.16), (tops[1][0] + 0.01, tops[1][1] - 0.02, 0.11), tops[1]]
    parts += cable("cable_pc_power", "cable", pts, 0.0035, lod)
    # monitor VGA to the system unit card
    vx, vz = TC["vga"]
    pts = [(L.MX - 0.03, yb - 0.002, L.M_BACK[1] + 0.02), (L.MX - 0.02, yb + 0.02, DZ + 0.02),
           (L.MX + 0.10, 0.285, DZ + 0.006), (0.16, 0.30, DZ + 0.006), (vx - 0.02, tb + 0.035, vz - 0.06),
           (vx, tb + 0.020, vz)]
    parts += cable("cable_vga", "cable_beige", pts, 0.0045, lod)
    # keyboard: from the back along the table under the monitor to the DIN socket
    kx_, kz_ = TC["kbd"]
    pts = [((L.KX0 + L.KX1) / 2 + 0.12, L.KY1 + 0.002, DZ + 0.03), ((L.KX0 + L.KX1) / 2 + 0.13, L.KY1 + 0.03, DZ + 0.004),
           (0.075, -0.05, DZ + 0.003), (0.17, 0.0, DZ + 0.003), (0.175, 0.20, DZ + 0.003),
           (kx_ - 0.01, tb + 0.03, kz_ - 0.12), (kx_, tb + 0.02, kz_)]
    parts += cable("cable_keyboard", "cable_beige", pts, 0.0028, lod, k=3)
    # mouse: from its nose to the serial port
    mx, my, _ = L.MOUSE
    ox, oz = TC["mouse"]
    pts = [(mx - 0.004, my + 0.056, DZ + 0.006), (mx - 0.01, my + 0.085, DZ + 0.004), (0.185, -0.06, DZ + 0.003),
           (0.185, 0.12, DZ + 0.003), (ox - 0.02, tb + 0.03, oz - 0.13), (ox, tb + 0.02, oz)]
    parts += cable("cable_mouse", "cable_beige", pts, 0.0022, lod, k=3)
    # speakers: the left one to the right one behind the monitor, the right one to the sound card
    w, d, h = L.SPK
    (lx, ly, _), (rx, ry, _) = L.SPEAKERS
    pts = [(lx + 0.01, ly + d / 2 + 0.004, DZ + 0.03), (lx + 0.03, 0.17, DZ + 0.003), (L.MX, yb + 0.012, DZ + 0.003),
           (rx - 0.01, 0.14, DZ + 0.003), (rx, ry + d / 2 + 0.004, DZ + 0.03)]
    parts += cable("cable_speakers", "cable", pts, 0.0022, lod)
    ax_, az_ = TC["audio"]
    pts = [(rx + 0.01, ry + d / 2 + 0.004, DZ + 0.05), (rx + 0.03, 0.14, DZ + 0.003), (0.18, 0.26, DZ + 0.004),
           (ax_ - 0.01, tb + 0.03, az_ - 0.06), (ax_, tb + 0.016, az_)]
    parts += cable("cable_audio", "cable", pts, 0.0022, lod)
    # radio power - to the power strip, hangs from the left edge
    pts = [(L.RX1, L.RY1 - 0.03, DZ + 0.04), (L.RX1 + 0.03, 0.30, DZ + 0.004), (-0.40, yp + 0.012, DZ - 0.006),
           (-0.30, yp + 0.04, 0.42), (-0.16, 0.27, 0.18), (tops[2][0] - 0.02, tops[2][1] - 0.02, 0.11), tops[2]]
    parts += cable("cable_radio_power", "cable", pts, 0.003, lod)
    if lod == 0:
        # plugs at the ends: VGA hoods, DIN, the mouse connector, the speaker jack, the system unit
        # power plug
        pg = P("plugs", "black")
        for (cx, cz), w_, h_ in ((TC["vga"], 0.030, 0.014), (TC["mouse"], 0.030, 0.013)):
            rbox(pg, cx - w_ / 2, cx + w_ / 2, tb - 0.002, tb + 0.020, cz - h_ / 2, cz + h_ / 2, 0.003, 1, rz=0.002)
        lathe(pg, [(0.0085, 0.0), (0.0085, 0.020), (0.005, 0.030)], 10, (TC["kbd"][0], tb - 0.002, TC["kbd"][1]), (0, 1, 0))
        lathe(pg, [(0.004, 0.0), (0.004, 0.014), (0.0028, 0.02)], 8, (ax_, tb - 0.003, az_), (0, 1, 0))
        rbox(pg, px - 0.016, px + 0.016, tb - 0.002, tb + 0.014, pz - 0.012, pz + 0.012, 0.003, 1, rz=0.003)
        rbox(pg, L.MX - 0.048, L.MX - 0.012, yb - 0.006, yb + 0.006, L.M_BACK[1] + 0.012, L.M_BACK[1] + 0.028, 0.002, 1)
        rbox(pg, L.MX + 0.040, L.MX + 0.066, yb - 0.004, yb + 0.012, L.M_BACK[1] + 0.019, L.M_BACK[1] + 0.041, 0.003, 1)
        parts.append(pg)
        # tangle: loops of spare wire on the floor by the power strip and a loop hanging from the
        # plywood edge
        for k, (cx, cy, r, z, tilt) in enumerate(((-0.10, 0.17, 0.09, 0.012, 0.25), (-0.07, 0.20, 0.065, 0.024, -0.3))):
            pts = [(cx + r * math.cos(2 * math.pi * s / 10 + k) * (1 + 0.15 * math.sin(3 * s)),
                    cy + r * math.sin(2 * math.pi * s / 10 + k) * 0.8,
                    z + tilt * r * math.cos(2 * math.pi * s / 10 + k) * 0.3 + 0.004) for s in range(11)]
            parts += cable("tangle%d" % k, "cable" if k != 1 else "cable_beige", pts, 0.003, lod)
        pts = [(0.02, yp - 0.04, DZ + 0.004), (0.02, yp + 0.012, DZ - 0.004), (0.03, yp + 0.03, DZ - 0.12),
               (-0.04, yp + 0.03, DZ - 0.24), (-0.10, yp + 0.02, DZ - 0.15), (-0.08, yp + 0.012, DZ - 0.02),
               (-0.07, yp - 0.03, DZ + 0.004)]
        parts += cable("tangle_loop", "cable", pts, 0.003, lod)
        # insulating tape: a strip across the plywood edge, pinning the wires
        for k, (x, reg) in enumerate(((-0.30, "tape"), (0.10, "tape_blue"), (0.20, "tape"))):
            tp = P("tape%d" % k, reg)
            a = math.radians(L.PLANK_DEG)                                       # rear edge of rotated plywood
            ye = (x + L.PY1 * math.sin(a)) * math.tan(a) + L.PY1 * math.cos(a)
            path = [(x, ye - 0.032, DZ + 0.0007), (x, ye - 0.004, DZ + 0.0007), (x, ye + 0.0035, DZ - 0.003),
                    (x, ye + 0.0045, L.PZ0 + 0.004), (x, ye - 0.002, L.PZ0 - 0.0006), (x, ye - 0.020, L.PZ0 - 0.0006)]
            ribbon(tp, spline(path, 2), (1, 0, 0), 0.0095, 0.0004)
            parts.append(tp)
    return parts


def build_lod(spec):
    parts = build_cases(spec) + build_plank(spec) + build_monitor(spec) + build_tower(spec)
    parts += build_keyboard(spec) + build_speakers(spec) + build_radio(spec) + build_desk_bits(spec)
    parts += build_handset(spec) + build_wires(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """One box: the table with the cases and everything on it, up to the top of the system unit. A
    component thinner than 0.5 m does not work in the engine; the antenna has no collision.
    """
    comps = [(kx.box_pts(L.PX0 - 0.01, L.PX1 + 0.01, -0.31, 0.31, 0.0, L.TZ1), kx.PEN + r"\plastic.rvmat")]
    fx, fz, _ = L.FAN
    memory = {
        "invView": [(0.0, -2.3, 1.4)],
        "ce_center": [(0.0, 0.0, 0.6)],
        "ce_radius": [(0.9, 0.0, 0.6)],
        "ozl_fan_axis": [(fx, L.TY1, fz), (fx, L.TY1 + 0.05, fz)],
    }
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 70.0, memory, bbox


# The first ones are for the --look preview: overall view, the table (the same in
# "working"), the radio with the handset, the system unit, the cases from below, the back
SHOTS = [
    ("front", (-0.9, -2.4, 1.6), (0.0, 0.0, 0.7), 32),
    ("desk", (-0.02, -1.0, 1.22), (-0.06, 0.0, 0.84), 32),
    ("radio", (-1.0, -0.78, 1.18), (-0.46, 0.02, 0.83), 34),
    ("tower", (0.78, -0.82, 1.12), (0.30, -0.02, 0.84), 34),
    ("cases", (0.9, -1.6, 0.6), (0.0, 0.0, 0.35), 30),
    ("back", (1.1, 1.6, 1.3), (0.12, 0.12, 0.72), 32),
    ("right", (1.9, -0.6, 1.2), (0.0, 0.0, 0.7), 32),
    ("top", (0.1, -0.9, 2.4), (0.0, 0.0, 0.7), 30),
]

M.look_shots = (6, 2)
M.run(build_lod, collision, SHOTS, row_step=1.7, row_shot=((1.7, -6.4, 2.0), (1.7, 0, 0.8)))
