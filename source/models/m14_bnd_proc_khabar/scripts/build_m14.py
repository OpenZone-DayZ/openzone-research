"""M14 - buyer's scale: Loot Analyzer of the Bandits (OZL_Bnd_Proc_Khabar).
Analyzer: cargo 4x4, no modules (no module_1..3 points, as in M02, M04, M06, M08, M10).

    blender --background --python build_m14.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: system Python make_decals.py (the scale, the dosimeter and calculator displays
with "work" frames, hryvnias - the design and sizes of the notes are in uah.py).

The scale is base B7 (kscale.py in the kit, sizes and layout): a Soviet mobile dial commodity scale
RP-150Ts13, platform 630 x 800 mm, height 1680 mm, up to 185 kg (the construction follows photos of the
RP-2Ts13M of the same series). Scale 0-150 kg per turn, division 0.5 kg, no inscriptions. Repainted
dirty black over the factory grey enamel (Bandits): grey and rust in the chips, the ribbed platform sheet
is worn down to metal, chromed dial rim.

Look: the "dayz" look; the shape of the scale is detailed in m14_scale.py (B7 in the kit is left alone),
the trim is in m14_props.py, the primitives in m14_geo.py.

Trim of the buyer (Bandits: battered, dirty, piled with loot):
- on the platform a tray 340 x 260 x 45 mm, in it on a dark rag a heap: eight watches (case dia. 34 mm,
  like the Pobeda/Vostok of the 1970s-90s) on straps and bracelets, three gold chains (one hangs over the
  rim), a signet ring and a ring;
- brass weights 2 kg, 1 kg, 500 g (GOST 7328 class M2: dia. 64 / 50 / 40 mm), a 10x watchmaker's loupe
  (dia. 34 mm);
- the DRG-01T1 dosimeter is taped to the column with blue insulating tape: 175 x 90 x 55 mm, 0.6 kg
  (as in M13), display in front;
- instead of the zero-adjust screw on the lever box a rusty M16 bolt with a washer and a nut; on the left
  the arrester (platform stop, like the levers on the RP-2Ts13M box);
- on the right a stool 320 x 320 x 450 mm (Soviet kitchen stool, pine) with a 1990s calculator
  (85 x 140 x 18 mm, pocket size like the Citizen / "Elektronika MK"), hryvnia bundles under a rubber
  band (500, 200 and 100 UAH: notes 154 / 148 / 142 x 75 mm, NBU - uah.py) and a tin ashtray dia. 110
  with cigarette butts;
- DayZ items as proxies: a spare 9 V battery of the dosimeter on the lever box lid, a pen and a petrol
  lighter on the stool, vodka bottles on the floor; the "Chernomorka" pack is an own box with the
  vanilla texture by path (as in M16: the config sets the brand of a DayZ pack, a proxy cannot be
  repainted).

Work look: the dosimeter display is ozl_screen, the calculator display is ozl_screen_2 (own textures with
frames, OZL_WorkFx frames). "Work": the arrester is released (bone ozl_lever, the first quarter of the
ozl_weigh source), the needle goes to a weight of 14 kg (bone ozl_weigh, pose) and breathes around it by
0.8 kg (bone ozl_needle - a child, wobble); after the work - back to zero. There is no "work" atlas of
its own: nothing lights up in the atlas, only the dosimeter display glows (own textures). The "work"
preview is the wrapper below (Model).

Blender axes: X is width, Y is depth (face toward -Y), Z is up.
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
import kscale as ks  # noqa: E402
import kvanilla as kv  # noqa: E402
import kwood  # noqa: E402
import m14_props as pr  # noqa: E402
import m14_scale as sc  # noqa: E402
import uah  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
LAY = ks.layout()
HC = ks.HEAD_C

LOD_SPECS = [
    dict(lod=0, bev=2, sides=16),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    # scale
    "sc_body": ("paint_black", 0.6), "sc_frame": ("paint_frame", 0.5), "sc_deck": ("deck", 0.7),
    "chrome": ("chrome", 1.2), "sc_dial": ("dial", 3.2), "sc_needle": ("needle", 2.0), "sc_inner": ("inner", 0.2),
    "rubber": ("rubber", 0.8), "steel": ("steel", 1.4), "black": ("black", 1.5), "plate": ("plate", 3.0),
    # loot
    "tray": ("tray", 1.0), "rag": ("rag", 1.0), "gold": ("gold", 2.5), "silver": ("silver", 2.5),
    "watch_face": ("watch_face", 4.0), "watch_face_dark": ("watch_face_dark", 4.0), "hand_light": ("hand_light", 4.0),
    "strap": ("strap", 2.5), "onyx": ("onyx", 4.0), "brass": ("brass", 1.6), "loupe": ("loupe", 2.5), "lens": ("lens", 3.0),
    # dosimeter, bolt
    "bolt": ("bolt", 2.0), "dos": ("dos", 1.6), "dos_dark": ("dos_dark", 2.5), "dos_key": ("dos_key", 3.0),
    "tape": ("tape", 1.4),
    # stool and what is on it
    "wood_x": ("wood_x", 0.8), "wood_y": ("wood_y", 0.8), "wood_z": ("wood_z", 0.8), "nail": ("nail", 3.0),
    "calc_body": ("calc_body", 2.0), "calc_dark": ("calc_dark", 2.5), "solar": ("solar", 3.0),
    "key_dark": ("key_dark", 3.0), "key_light": ("key_light", 3.0), "key_orange": ("key_orange", 3.0),
    "paper_edge": ("paper_edge", 2.5), "band": ("band", 2.5), "ashtray": ("ashtray", 1.6), "ash": ("ash", 2.0),
    "ash_dark": ("ash_dark", 3.0), "butt_filter": ("butt_filter", 3.0), "butt_paper": ("butt_paper", 3.0),
    "carton": ("carton", 2.0),
}
for _nm, *_ in pr.CASH:
    REGIONS[_nm] = (_nm, 5.0)


# =============================================================================
# Materials
# =============================================================================
def decal(name, ax, sign, uv, center, size, rng=None):
    return (os.path.join(WORK, name), ax, sign, uv, center, size, rng)


def top_decal(name, center, size):
    """Decal on a top face: a part with a decal has its own area, hence no range."""
    return decal(name, "z", 1, ("x", "y"), center, size)


def build_tread(mat, origin, pitch=0.030, **paint):
    """Ribbed platform sheet: painted metal from kmats.build_paint with a "checker plate" pattern over it
    (raised oblong ribs in a staggered order, pitch `pitch`): the rib tops are worn down to metal, bumps in
    the _nohq relief. Only on faces looking up."""
    refs = kmats.build_paint(mat, origin, **paint)
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    vec, sep = t.coords(origin, 7.3)
    u = t.math("DIVIDE", sep.outputs["X"], pitch)
    v = t.math("DIVIDE", sep.outputs["Y"], pitch)
    par = t.math("ABSOLUTE", t.math("MODULO", t.math("ADD", t.math("FLOOR", u), t.math("FLOOR", v)), 2.0))
    fu = t.math("SUBTRACT", t.math("FRACT", u), 0.5)
    fv = t.math("SUBTRACT", t.math("FRACT", v), 0.5)

    def ell(ra, rb):
        a, b = t.math("DIVIDE", fu, ra), t.math("DIVIDE", fv, rb)
        return t.math("ADD", t.math("MULTIPLY", a, a), t.math("MULTIPLY", b, b))
    d = t.mixf(par, ell(0.36, 0.10), ell(0.10, 0.36))
    bump = t.math("MULTIPLY", t.maprange(d, 1.0, 0.45, 0.0, 1.0), t.facing(t.normal(), "Z", 1, 0.7))
    wear = t.maprange(t.noise(vec, 3.0, 4.0, 0.6), 0.35, 0.7, 0.35, 0.9)
    col = t.mixc(t.math("MULTIPLY", bump, wear), kmats.sock(mat, refs["color"]), kmats.lin((104, 102, 96)))
    h = t.math("ADD", kmats.sock(mat, refs["height"]), t.math("MULTIPLY", bump, 0.6))
    gl = t.math("MAXIMUM", kmats.sock(mat, refs["gloss"]), t.math("MULTIPLY", bump, 0.42))
    return kmats.out(t, col, gl, kmats.sock(mat, refs["spec"]), h)


def build_paper_edge(mat, origin, color=kmats.lin((200, 194, 172))):
    """Cut of a bundle of notes: thin stripes of sheets across the height, yellowed spots, dirt."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 2.0)
    nsep = t.normal()
    lines = t.math("SINE", t.math("MULTIPLY", sep.outputs["Z"], 2 * math.pi / 0.0005))
    col = t.mixc(t.maprange(lines, -1.0, 1.0, 0.0, 1.0), tuple(c * 0.80 for c in color[:3]) + (1,), color)
    col = t.mixc(t.maprange(t.noise(vec, 40.0, 4.0, 0.6), 0.3, 0.7, 0.0, 0.3), col, kmats.lin((150, 138, 112)))
    col, _ = kmats.weather(t, col, vec, sep, nsep, 0.0, 0.1, 0.3, 0.4)
    return kmats.out(t, col, 0.12, 0.06, t.math("MULTIPLY", lines, 0.05))


KINDS = kmats.std_kinds(floor_z=0.0)
lin = kmats.lin
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# dirty black paint over the factory grey enamel (Bandits; on the RP-2Ts13M photo it is grey-lilac): chips
# down to grey, rust in the chips and at the floor, dirt at the bottom and in corners
BLACK = dict(color=lin((40, 40, 38)), under=lin((128, 128, 124)), seed=1.4, gloss=0.28, spec=0.22,
             chip=(0.55, 0.61), rust=(0.58, 0.66), rust_low=1.0, floor_z=0.0, dust=0.45, grime=0.9)
RUSTY = dict(color=lin((62, 50, 42)), under=lin((112, 66, 36)), seed=8.1, gloss=0.25, spec=0.25,
             chip=(0.45, 0.55), rust=(0.40, 0.50), rust_low=1.0, floor_z=0.0, dust=0.4, grime=0.7)
DIAL_SIZE = (2 * LAY["dial_r"], 2 * LAY["dial_r"])
WOOD = dict(color=lin((126, 96, 64)), floor_z=0.0, dust=0.45, grime=1.0, knots=0.5)
KINDS.update({
    "paint_black": ("paint", BLACK),
    "paint_frame": ("paint", dict(BLACK, seed=2.2, chip=(0.50, 0.57))),
    # the ribbed sheet is worn down to metal by the weights, remnants of black paint and rust in the corners
    "deck": (build_tread, dict(BLACK, color=lin((46, 45, 42)), under=lin((112, 110, 104)), seed=3.1,
                               chip=(0.40, 0.47), rust=(0.52, 0.60), gloss=0.35, spec=0.35)),
    "chrome": ("steel", dict(seed=6.1, tone=0.46, along="z", gloss=0.70, spec=0.80, dust=0.40, grime=0.8)),
    # scale: cream enamel under glass, rust spots, as on the Ts13 photo
    "dial": ("paint", dict(color=lin((218, 208, 180)), under=lin((128, 82, 44)), seed=5.7, gloss=0.5,
                           spec=0.35, chip=(0.66, 0.74), rust=(0.56, 0.64), rust_low=0.0, dust=0.05, grime=0.25,
                           yellow=0.4, decal_items=[decal("decal_dial.png", "y", -1, ("x", "z"), (HC[0], HC[2]),
                                                          DIAL_SIZE, (LAY["dial_y"] - 0.003, LAY["dial_y"] + 0.003))])),
    "needle": ("flat", dict(color=lin((22, 22, 22)), gloss=0.4, spec=0.3)),
    "inner": ("flat", dict(color=lin((22, 22, 22)), gloss=0.15, spec=0.08)),
    "steel": ("steel", dict(seed=4.2, tone=0.26, along="x", gloss=0.5, spec=0.6, dust=0.35, grime=0.8)),
    "plate": ("steel", dict(seed=8.8, tone=0.38, along="x", gloss=0.45, spec=0.5, dust=0.5, grime=1.0)),
    # tray: calcined steel with soot, worn to metal on the edges and the rim
    "tray": ("paint", dict(color=lin((46, 42, 38)), under=lin((104, 100, 94)), seed=7.7, gloss=0.30, spec=0.35,
                           chip=(0.50, 0.58), rust=(0.56, 0.64), rust_low=0.0, floor_z=0.0, dust=0.35, grime=1.0)),
    "rag": ("plastic", dict(color=lin((96, 22, 30)), gloss=0.06, spec=0.03, mottle=0.16, dust=0.2, grime=0.45,
                            scuff=(0.9, 1.0))),
    "gold": ("paint", dict(CLEAN, color=lin((214, 156, 38)), under=lin((160, 108, 28)), seed=9.3, gloss=0.95,
                           spec=1.0, chip=(0.75, 0.85), dust=0.08, grime=0.30)),
    "silver": ("steel", dict(seed=9.8, tone=0.40, along="y", gloss=0.75, spec=0.85, dust=0.10, grime=0.4)),
    "watch_face": ("flat", dict(color=lin((222, 214, 190)), gloss=0.6, spec=0.4)),
    "watch_face_dark": ("flat", dict(color=lin((26, 28, 32)), gloss=0.6, spec=0.4)),
    "hand_light": ("flat", dict(color=lin((214, 212, 200)), gloss=0.6, spec=0.5)),
    "strap": ("plastic", dict(color=lin((62, 38, 24)), gloss=0.22, spec=0.12, dust=0.1, grime=0.5, scuff=(0.6, 0.72))),
    "onyx": ("flat", dict(color=lin((14, 14, 16)), gloss=0.9, spec=0.8)),
    "brass": ("paint", dict(color=lin((176, 136, 64)), under=lin((96, 74, 36)), seed=6.6, gloss=0.55, spec=0.65,
                            chip=(0.62, 0.70), rust=(0.99, 1.0), rust_low=0.0, dust=0.35, grime=0.8)),
    "loupe": ("plastic", dict(color=lin((24, 24, 25)), gloss=0.35, spec=0.25, dust=0.3, grime=0.5)),
    "lens": ("flat", dict(color=lin((120, 136, 142)), gloss=0.95, spec=0.95)),
    "bolt": ("paint", RUSTY),
    "dos": ("plastic", dict(color=lin((176, 172, 156)), gloss=0.35, spec=0.25, mottle=0.08, dust=0.4, grime=0.6,
                            scuff=(0.62, 0.70))),
    "dos_dark": ("plastic", dict(color=lin((30, 31, 32)), gloss=0.4, spec=0.3, dust=0.2, grime=0.3)),
    "dos_key": ("plastic", dict(color=lin((70, 70, 72)), gloss=0.3, spec=0.2, dust=0.3, grime=0.5, scuff=(0.6, 0.7))),
    "tape": ("plastic", dict(color=lin((38, 62, 128)), gloss=0.5, spec=0.35, dust=0.35, grime=0.5, scuff=(0.7, 0.8))),
    "wood_x": (kwood.build_wood, dict(WOOD, seed=4.4, along="x")),
    "wood_y": (kwood.build_wood, dict(WOOD, seed=4.9, along="y")),
    "wood_z": (kwood.build_wood, dict(WOOD, color=lin((118, 90, 60)), seed=5.3, along="z")),
    "nail": ("steel", dict(seed=3.3, tone=0.14, along="x", gloss=0.3, spec=0.3, dust=0.3, grime=0.8)),
    "calc_body": ("plastic", dict(color=lin((40, 40, 42)), gloss=0.3, spec=0.2, dust=0.25, grime=0.4, scuff=(0.62, 0.70))),
    "calc_dark": ("plastic", dict(color=lin((18, 18, 20)), gloss=0.4, spec=0.3, dust=0.1)),
    "solar": ("flat", dict(color=lin((44, 30, 26)), gloss=0.75, spec=0.6)),
    "key_dark": ("plastic", dict(color=lin((62, 62, 66)), gloss=0.3, spec=0.2, dust=0.2, scuff=(0.55, 0.65))),
    "key_light": ("plastic", dict(color=lin((176, 172, 160)), gloss=0.3, spec=0.2, dust=0.2, scuff=(0.55, 0.65))),
    "key_orange": ("plastic", dict(color=lin((196, 92, 36)), gloss=0.3, spec=0.2, dust=0.2)),
    "paper_edge": (build_paper_edge, {}),
    "band": ("plastic", dict(color=lin((150, 96, 60)), gloss=0.3, spec=0.2, dust=0.1)),
    # tin ashtray: smoked tin
    "ashtray": ("steel", dict(seed=3.6, tone=0.22, along="z", gloss=0.35, spec=0.40, dust=0.3, grime=1.0)),
    "ash": ("plastic", dict(color=lin((112, 110, 104)), gloss=0.04, spec=0.02, mottle=0.30, dust=0.0, grime=0.2,
                            scuff=(0.9, 1.0))),
    "ash_dark": ("flat", dict(color=lin((34, 32, 30)), gloss=0.05, spec=0.02)),
    "butt_filter": ("plastic", dict(color=lin((196, 140, 80)), gloss=0.15, spec=0.08, mottle=0.12, dust=0.1, grime=0.4)),
    "butt_paper": ("plastic", dict(color=lin((214, 208, 194)), gloss=0.12, spec=0.06, mottle=0.1, dust=0.1, grime=0.4)),
    "carton": ("plastic", dict(color=lin((214, 208, 196)), gloss=0.3, spec=0.2)),
})
# the top note of a bundle is a hryvnia of its denomination (make_decals.py: decal_uah<denomination>.png,
# design in uah.py), the sides are light paper with the denomination ink
for _nm, (_cx, _cy), _dz, _t, _den in pr.CASH:
    _pal = uah.PAL[_den]
    _edge = lin(tuple(int(c * 0.90) for c in uah.mix(_pal["paper"], _pal["field"], 0.40)))
    KINDS[_nm] = ("paint", dict(CLEAN, color=_edge, gloss=0.15, spec=0.08, dust=0.1,
                                decal_items=[top_decal("decal_uah%d.png" % _den, (_cx, _cy), uah.SIZE[_den])]))

# =============================================================================
# Model: looks, bones, DayZ items
# =============================================================================
OBJ, NAME = "m14_bnd_proc_khabar", "ozr_bnd_proc_khabar"
SEL_SCREEN, SEL_SCREEN2 = "ozl_screen", "ozl_screen_2"
SEL_WEIGH, SEL_NEEDLE, SEL_LEVER = "ozl_weigh", "ozl_needle", "ozl_lever"
WEIGH_KG, WOB_KG = 14.0, 0.8                                 # loot weight, needle "breathing" swing
WEIGH_ANG = 2 * math.pi * WEIGH_KG / 150.0
WOB_ANG = 2 * math.pi * WOB_KG / 150.0
LEVER_ANG = math.radians(90.0)
LEVER_SHARE = 0.25                                           # share of the ozl_weigh source for the arrester
NEEDLE_AXIS, LEVER_AXIS = "ozl_needle_axis", "ozl_lever_axis"
ANIMS = (
    ("ozl_lever_turn", dict(type="rotation", source="ozl_weigh", selection=SEL_LEVER, axis=LEVER_AXIS, memory=1,
                            minValue=0.0, maxValue=LEVER_SHARE, angle0=0.0, angle1=LEVER_ANG)),
    ("ozl_weigh_turn", dict(type="rotation", source="ozl_weigh", selection=SEL_WEIGH, axis=NEEDLE_AXIS, memory=1,
                            minValue=LEVER_SHARE, maxValue=1.0, angle0=0.0, angle1=WEIGH_ANG)),
    ("ozl_needle_wobble", dict(type="rotation", source="ozl_needle", selection=SEL_NEEDLE, axis=NEEDLE_AXIS, memory=1,
                               minValue=0.0, maxValue=1.0, angle0=0.0, angle1=2 * WOB_ANG)),
)
BONES = ((SEL_WEIGH, ""), (SEL_NEEDLE, SEL_WEIGH), (SEL_LEVER, ""))
SOURCES = {"ozl_weigh": dict(animPeriod=1.8), "ozl_needle": dict(animPeriod=0.2)}
LCD_PANEL = dict(off="decal_lcd_off.png", frames=["decal_lcd_f%02d.png" % i for i in range(8)], size=256, gloss=0.6)
CALC_PANEL = dict(off="decal_calc_off.png", frames=["decal_calc_f%02d.png" % i for i in range(10)], size=256, gloss=0.5)
# "work" pose in the preview (not exported to p3d - the bones of model.cfg set it): by rotation, the wrapper
# below recognises the look by this dict; the needle goes to the weight plus the middle of the "breathing"
# (wobble mid = 0.5)
ON_MOVE = {SEL_NEEDLE: (0.0, 0.0, 0.0)}
ON = dict(remap={}, emissive=(1.0, 1.0, 1.0, 1.0), move=ON_MOVE)
PIV = (HC[0], 0.0, HC[2])
TURNS = {SEL_WEIGH: (PIV, (0.0, 1.0, 0.0), WEIGH_ANG), SEL_NEEDLE: (PIV, (0.0, 1.0, 0.0), WEIGH_ANG + WOB_ANG),
         SEL_LEVER: (sc.LEVER_C, (0.0, 1.0, 0.0), LEVER_ANG)}
LIGHTER = r"dz\gear\cooking\petrol_lighter"


def lay(deg):
    """Flat on the wide face (lighter): the item's +Y is along the support at angle deg, +X is down."""
    a = math.radians(deg)
    return dict(up=(math.cos(a), math.sin(a), 0.0), fwd=(-math.sin(a), math.cos(a), 0.0))


DECOR = [
    kv.put("battery9v", (-0.118, 0.318, sc.ZCAP), **kv.flat(96)),             # spare 9 V battery of the dosimeter
    kv.put("pen", (0.600, -0.100, pr.SZ), **kv.flat(176)),                     # pen by the calculator
    kv.put(LIGHTER, (0.722, -0.112, pr.SZ), **lay(12)),                        # lighter by the ashtray
    kv.put("vodka", (0.392, -0.330, 0.0), up=(0, 0, 1), fwd=(0.4, -1, 0)),     # half-full, between scale and stool
    kv.put("vodka", (0.700, 0.150, 0.0), **kv.flat(160)),                      # empty - on the floor behind the stool
]


class Model(kmodel.Model):
    """The "work" look without its own atlas: nothing lights up in the atlas, so states is empty (no extra
    _on atlas is baked). The "work" preview (look_on_*, tex_on_* after baking) is here: the same atlas, the
    display in the "work" frame, the bone pose by rotation (TURNS)."""

    def render_look(self, lods, shots):
        self.states = {"on": ON}
        try:
            super().render_look(lods, shots)
        finally:
            self.states = {}

    def render(self, lods, shots, row_step, row_shot, textured):
        super().render(lods, shots, row_step, row_shot, textured)
        if not textured:
            return
        krender.clear_scene()
        cam = krender.setup(64)
        mats = {"atlas": krender.game_material(self.game_tex, self.name)}
        if self.glass is not None:
            mats["glass"] = krender.game_glass(os.path.join(self.game_tex, self.name + "_glass_ca.png"))
        mats.update(self.panel_mats(True))
        krender.place(lods[0], "l0", (0, 0, 0), mats, move=ON_MOVE)
        self.place_extras()
        for name, loc, target, lens in shots:
            krender.shoot(cam, os.path.join(self.renders, "tex_on_%s.png" % name), loc, target, lens, (1400, 1000))

    def panel_mats(self, on):
        """Work: the dosimeter display glows (in OZL_Work it is in onSelections), the calculator does not (an
        LCD without a backlight, only its frames change); frames - with digits."""
        out = super().panel_mats(on)
        if on:
            _, frames = self.panel_pngs("lcd")
            out["lcd"] = krender.panel_material(frames[3], glow=1.6, gloss=LCD_PANEL["gloss"])
            _, frames = self.panel_pngs("calc")
            out["calc"] = krender.panel_material(frames[4], glow=0.0, gloss=CALC_PANEL["gloss"])
        return out


M = Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
          glass=dict(base=(0.80, 0.82, 0.80), clear=0.06, edge=0.14, smudge=0.16, streaks=0.06),
          selections=(SEL_SCREEN, SEL_SCREEN2, SEL_WEIGH, SEL_NEEDLE, SEL_LEVER), hidden=(SEL_SCREEN, SEL_SCREEN2),
          bones=BONES, animations=ANIMS, sources=SOURCES, decor=DECOR,
          panels={"lcd": LCD_PANEL, "calc": CALC_PANEL}, vsections={"cigs": pr.CIGS})
P = M.part
BOUNDS = {}


# --- preview: "work" pose by rotation ---------------------------------------------------------------
# krender places the look pose by a shift only (move); the needle and the arrester need a rotation. The
# wrappers are here, the library is unchanged (as in M04): the look is recognised by the same move dict (ON_MOVE).
def _turn(parts, obs, move):
    if move is not ON_MOVE:
        return obs
    for p, ob in zip(parts, obs):
        t = TURNS.get(p.group)
        if t:
            piv, ax, ang = Vector(t[0]), Vector(t[1]), t[2]
            ob.matrix_world = (Matrix.Translation(piv) @ Matrix.Rotation(ang, 4, ax) @ Matrix.Translation(-piv) @
                               Matrix.Translation(ob.location))
    return obs


_place_look, _place = krender.place_look, krender.place


def _place_look_turn(parts, *a, **kw):
    return _turn(parts, _place_look(parts, *a, **kw), kw.get("move"))


def _place_turn(parts, *a, **kw):
    return _turn(parts, _place(parts, *a, **kw), kw.get("move"))


krender.place_look, krender.place = _place_look_turn, _place_turn


# =============================================================================
# LODs, collision, camera angles
# =============================================================================
def build_lod(spec):
    parts = sc.build_scale(P, spec, dict(lever=SEL_LEVER, weigh=SEL_WEIGH, needle=SEL_NEEDLE))
    parts += pr.build_tray(P, spec) + pr.build_rag(P, spec) + pr.build_watches(P, spec) + pr.build_chains(P, spec)
    parts += pr.build_rings(P, spec) + pr.build_weights(P, spec)
    parts += pr.build_dosimeter(P, spec, SEL_SCREEN) + pr.build_tape(P, spec) + pr.build_bolt(P, spec)
    parts += pr.build_stool(P, spec) + pr.build_calc(P, spec, SEL_SCREEN2) + pr.build_cash(P, spec)
    parts += pr.build_ashtray(P, spec) + pr.build_cigs(P, spec)
    parts = [p for p in parts if len(p.bm.faces)]           # in the middle LOD some parts are empty
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """Convex components no thinner than 0.5 m (a thinner one does not
    work), packed symmetrically around the real ones."""
    metal = kx.PEN + r"\metalplate.rvmat"
    wood = kx.PEN + r"\wood.rvmat"
    x0, x1, y0, y1, _, _ = LAY["bounds"]
    plat = kx.box_pts(x0, x1, y0, LAY["housing"][2], 0.06 - 0.25, 0.06 + 0.25)
    yc = (pr.DOS[2] + LAY["housing"][3]) / 2
    col = kx.box_pts(-0.25, 0.25, yc - 0.25, yc + 0.25, 0.0, LAY["top"])
    stool = kx.box_pts(pr.SX - 0.25, pr.SX + 0.25, pr.SY - 0.25, pr.SY + 0.25, 0.0, 0.50)
    comps = [(plat, metal), (col, metal), (stool, wood)]
    ny = sum(ks.NEEDLE_Y) / 2
    lx, ly, lz = sc.LEVER_C
    memory = {
        "invView": [(0.2, -2.6, 1.1)],
        "ce_center": [(0.2, 0.0, 0.84)],
        "ce_radius": [(1.2, 0.0, 0.84)],
        # axes from the face toward the person (as in M01, M08, M10, M11): a plus angle is clockwise for the person
        NEEDLE_AXIS: [(HC[0], ny, HC[2]), (HC[0], ny - 0.05, HC[2])],
        LEVER_AXIS: [(lx, ly - 0.012, lz), (lx, ly - 0.062, lz)],
    }
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 200.0, memory, bbox


# the first ones are for the --look preview: overview, the head with the dosimeter and the lever box (arrester,
# bolt, nameplate) - also in "work", the tray close up, the stool; then the dosimeter and the view from behind
SHOTS = [
    ("front", (-1.0, -2.7, 1.65), (0.2, 0.0, 0.80), 30),
    ("head", (-0.42, -1.05, 1.42), (0.02, 0.26, 1.17), 32),
    ("housing", (0.30, -0.80, 0.62), (0.0, 0.24, 0.20), 34),
    ("tray", (0.20, -0.72, 0.62), (-0.03, -0.12, 0.15), 34),
    ("stool", (1.15, -0.95, 1.05), (0.60, -0.12, 0.45), 34),
    ("dosimeter", (-0.40, -0.55, 1.05), (0.0, 0.24, 0.92), 38),
    ("back", (1.4, 2.4, 1.5), (0.2, 0.0, 0.8), 30),
]

M.look_shots = (5, 3)
M.run(build_lod, collision, SHOTS, row_step=1.6, row_shot=((1.6, -6.4, 1.5), (1.6, 0, 0.8)))
