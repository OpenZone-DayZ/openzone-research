"""M15 - spotter's table: Trail Packer of the Bandits (OZL_Bnd_Pack_Trail).
Packer: cargo 10x10, three module places (module_1..3) and module proxies in the same places. Each
module of the "Trails" line has its own place where it is used: slot 1 - PDA reader M78 on the table at
the left, slot 2 - radio scanner M79 on the shelf at the right, on a rubber mat, slot 3 - tablet with maps
M80 on the table in the middle in front of the map. Empty places: on the boards at slots 1 and 3 a trace
(a clean spot in a dusty rim), at slot 2 the mat and the tape recorder cable with a plug.

    blender --background --python build_m15.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: system Python make_decals.py (map, photos, notes, papers, pager display, tape
recorder strip and scale, cassette label, module-place traces). Where things lie - layout.py (shared
with make_decals.py); the tape recorder - m15_rec.py, own primitives - m15_geo.py.

Table - base B1 (kfurn.workbench, worktop="board") of the same size as M05, M11, M23: an electronics
assembler's bench IZhSK.296375.001 ("Signal" catalogue, version -03), top 1600 x 710 mm, height
785-810 mm. Here 1.60 x 0.72 m, work surface at 0.78, cabinet 0.42 wide with four drawers, back panel
and shelf at 1.40, shelf depth 0.30. Bandit variant: the table is repainted dirty black over grey
factory enamel, grey and rust in the chips; the edges of the frame, cabinet, back panel and shelf are
chamfered; on top four 40 mm boards of different tones, with rounded edges and screws, worn and stained.
No power strip; under the shelf a luminaire with a fluorescent tube (LPO type, box ~1.36 m, convex milky
diffuser, end caps, cord behind the table) that lights the map.

Props and sizes:
- on the back panel a 1.18 x 0.385 m fibreboard sheet on nails, on it a map 0.84 x 0.34 (own,
  unreadable: forest, river, roads, a grid with digits, no names), two photos 9 x 13 and two notes;
  12 pins with ball heads dia. 6, red threads between them with sag;
- on the table board papers (A4 210 x 297, A5 148 x 210, A3 sketch 420 x 297, a photo), some with a
  folded corner; on the sketch M12 x 80 marker bolts (GOST 7798: hexagonal head, 18 mm wrench size,
  chamfered, height 7.5, thread over 30 mm) with strips of red rag tied on;
- PDAs: Palm III (1998, 119 x 81 x 18) face down with the compartment cover removed and two AAA cells
  (dia. 10.5 x 44.5) beside it, Psion Series 5 (1997, closed 170 x 90 x 23); the third PDA is in
  module M78;
- flash drives ~42 x 18 x 8 with caps and a loop (one has its cap off - the connector is visible), a
  digital pager ~62 x 45 x 18 (as in M13: display, three buttons, LED), a folded butterfly knife (handles
  130 with slots, pivots, latch), a bunch of keys on a ring (Yale-type, lever, padlock), a tin ashtray
  dia. 115 with a rolled edge, rests and butts, an enamelled mug 0.4 l (dia. 85 x 85, rolled edge, chips
  down to black), an opened carton of cigarettes 280 x 90 x 48 (packs inside, two on top are missing),
  packs 88 x 55 x 22; the packs and the carton have the vanilla "Chernomorka" texture
  (pack_of_cigs_cherno_co.paa, section cigs, as in M16: the DayZ pack model is another brand and a proxy
  cannot be repainted);
- on the shelf at the left - three map rolls (ends, string) and a tin money box (~250 x 170 x 90) with a
  hinged lid, a handle and a padlock in the hasp; in the middle - the "Elektronika-302" cassette
  recorder (m15_rec.py) with a cable to the radio scanner place; under the table a cardboard box with
  open flaps, rags and a coil of wire inside;
- vanilla DayZ items - proxies (kvanilla; blue boxes in the preview): a partly drunk and an empty
  vodka bottle, a folded Chernarus map, a pen, a petrol lighter, two cigarettes, on the shelf binoculars
  and two cassettes.

Work look (class OZL_Work):
- ozl_lamp - the luminaire diffuser: lit in "work" (atlas _on);
- ozl_screen - the pager display, own texture (section pager): "off" is blank, "work" is 8 frames
  (digits run, the envelope blinks);
- ozl_lamp_2 - the pager LED: blinks (blink);
- tape recorder: the cassette reels are bones ozl_reel_l / ozl_reel_r on the source ozl_work (model.cfg
  loop, supply reel 2, take-up reel 4 turns per 6 s pass), the indicator needle is ozl_needle (wobble),
  the "record" and "play" keys are ozl_keys (pose, pressed in by 4 mm).

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
import kfurn  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import krender  # noqa: E402
import kvanilla as kv  # noqa: E402
import kwood  # noqa: E402
import layout as L  # noqa: E402
import m15_rec as R  # noqa: E402
from m15_geo import (CIGS, basis, box_to, cable, cig_pack, frame_plate, frame_z, lathe, open_box, plate,  # noqa: E402
                     ribbon, ring, rod, rounded_rect, sheet, spline)

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
X0, X1, Y0, Y1 = L.X0, L.X1, L.Y0, L.Y1                      # table
ZT, ZP, SHD, CAB_W = L.ZT, L.ZP, L.SHD, L.CAB_W              # tabletop, shelf top, shelf depth, cabinet
ZU = ZT - 0.04                                               # underside of the boards
YP, YS = L.YP, L.YS                                          # face of the back panel, front of the shelf
ZS = ZP - 0.02                                               # underside of the shelf
# luminaire under the shelf (in front of the gussets: the middle one goes into its rear wall)
LX0, LX1, LY0, LY1 = X0 + 0.12, X1 - 0.12, YS + 0.005, YS + 0.095
# under the table: a box
FBOX = (-0.66, -0.34, -0.20, 0.12, 0.24)
NEEDLE_MID = 0.55                                             # indicator needle in "work"

LOD_SPECS = [
    dict(lod=0, bev=1, sides=12),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "wb": ("paint_black", 0.6), "wb_front": ("paint_black_front", 0.9), "wb_panel": ("paint_black_panel", 0.6),
    "wb_top": ("plank_a", 0.8), "plank_a": ("plank_a", 0.8), "plank_b": ("plank_b", 0.8), "plank_c": ("plank_c", 0.8),
    "screw": ("screw", 2.0), "steel": ("steel", 1.0), "black": ("black", 1.0), "rubber": ("rubber", 0.5),
    "mat": ("mat", 0.8), "lamp_box": ("paint_black", 0.6), "diffuser": ("diffuser", 1.0),
    "cork": ("cork", 0.8), "map": ("map", 4.0),
    "pin_red": ("cap_red", 2.0), "pin_yellow": ("pin_yellow", 2.0), "pin_blue": ("pin_blue", 2.0),
    "string": ("string", 0.8), "rag": ("rag", 1.5), "bolt": ("bolt", 2.0),
    "pda": ("pda", 2.5), "psion": ("psion", 2.0), "dark": ("dark", 1.0), "cell": ("cell", 2.5),
    "flash": ("flash", 2.5), "flash_cap": ("flash_cap", 2.5), "pager": ("pager", 2.5), "pager_btn": ("pager_btn", 3.0),
    "led": ("led", 4.0), "brass": ("brass", 1.5), "tin": ("tin", 1.2), "ash": ("ash", 1.0), "butt": ("butt", 2.0),
    "filter": ("filter", 2.0), "mug": ("mug", 1.4), "mug_rim": ("mug_rim", 2.0), "tea": ("tea", 1.0),
    "knife": ("knife", 2.0), "carton": ("carton", 1.5), "carton_band": ("carton_band", 1.5),
    "notebook": ("notebook", 1.5), "pages": ("pages", 2.0), "deck": ("deck", 2.0), "roll": ("roll", 0.8),
    "roll_end": ("roll_end", 2.0), "twine": ("twine", 2.0), "cashbox": ("cashbox", 1.2), "card": ("card", 0.8),
    "junk": ("junk", 0.6),
    # tape recorder
    "rec_body": ("rec_body", 1.2), "rec_alu": ("rec_alu", 3.0), "rec_cloth": ("rec_cloth", 1.5),
    "rec_grille": ("rec_grille", 2.0), "rec_lid": ("rec_lid", 2.0), "rec_plate": ("rec_plate", 3.0),
    "rec_handle": ("rec_handle", 1.5), "cassette": ("cassette", 3.0), "cass_label": ("cass_label", 4.0),
    "hub": ("hub", 4.0), "tape": ("tape", 3.0), "vu": ("vu", 8.0), "needle": ("needle", 6.0),
    "knob": ("knob", 3.0), "knob_cap": ("rec_alu_plain", 4.0), "knob_mark": ("plastic_white", 6.0),
    "key": ("key", 3.0), "dot_red": ("cap_red", 6.0), "dot_blue": ("pin_blue", 6.0),
}
for _nm, *_ in L.PINNED:
    REGIONS[_nm] = (_nm, 5.0)
for _nm, *_ in L.PAPERS:
    REGIONS[_nm] = (_nm, 3.0)

# =============================================================================
# Materials
# =============================================================================


def decal(name, ax, sign, uv, center, size, rng=None):
    return (os.path.join(WORK, name), ax, sign, uv, center, size, rng)


def top_decal(name, center, size):
    """Decal on a top face: a part with a decal has its own area, hence no range."""
    return decal(name, "z", 1, ("x", "y"), center, size)


def wall_decal(name, x0, x1, z0, z1, y):
    """Decal on the back panel (facing -y), only on the face at depth y."""
    return decal(name, "y", -1, ("x", "z"), ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0), (y - 0.002, y + 0.002))


def rot_box(w, h, deg):
    a = math.radians(deg)
    return (w * abs(math.cos(a)) + h * abs(math.sin(a)), w * abs(math.sin(a)) + h * abs(math.cos(a)))


def trace_decal(i):
    """Trace on the boards at the empty place of module i (make_decals.make_traces)."""
    (x0, y0), (x1, y1) = L.MOD_BOX[i]
    mx, my, _ = L.MODS[i]
    return top_decal("decal_trace%d.png" % (i + 1), (mx + (x0 + x1) / 2, my + (y0 + y1) / 2), (x1 - x0 + 0.03, y1 - y0 + 0.03))


def vu_box():
    """Indicator scale in plan view: the middle and size (for the decal)."""
    sf, s_c, piv = R.vu_geom()
    vx, vw, vh = L.VU
    a, b = sf.p(vx, s_c - vh / 2, 0.0006), sf.p(vx, s_c + vh / 2, 0.0006)
    return (vx + L.REC[0], (a.y + b.y) / 2), (vw, abs(b.y - a.y))


KINDS = kmats.std_kinds(floor_z=0.0)
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# dirty black paint over the grey factory enamel of the table (Bandits): chips down to grey, rust at the
# floor and in the chips, dirt at the bottom and in corners; the back panel and shelf have less rust but are dusty
BLACK = dict(color=kmats.lin((38, 38, 36)), under=kmats.lin((128, 132, 130)), seed=2.1, gloss=0.30, spec=0.22,
             chip=(0.55, 0.61), rust=(0.60, 0.68), rust_low=1.0, floor_z=0.0, dust=0.45, grime=0.9)
TRACES = [trace_decal(0), trace_decal(2)]
_SY0, _SY1, _, _ = L.REC_STRIP
_CX, _CY, _CW, _CH, _ = L.CASS
KINDS.update({
    "paint_black": ("paint", BLACK),
    "paint_black_front": ("paint", dict(BLACK, seed=2.9, chip=(0.52, 0.58))),
    "paint_black_panel": ("paint", dict(BLACK, seed=3.7, chip=(0.60, 0.66), rust_low=0.0, floor_z=ZT, grime=0.4)),
    # boards: pine of different tones, darkened and worn, stained and dusty; traces of the places of modules 1 and 3
    "plank_a": (kwood.build_wood, dict(color=kmats.lin((126, 94, 62)), seed=2.3, along="x", floor_z=ZT, dust=0.5,
                                       grime=0.8, knots=0.7, decal_items=TRACES)),
    "plank_b": (kwood.build_wood, dict(color=kmats.lin((106, 80, 54)), seed=3.1, along="x", floor_z=ZT, dust=0.5,
                                       grime=0.9, knots=0.5, decal_items=TRACES)),
    "plank_c": (kwood.build_wood, dict(color=kmats.lin((138, 104, 70)), seed=4.7, along="x", floor_z=ZT, dust=0.45,
                                       grime=0.7, knots=0.8, decal_items=TRACES)),
    "screw": ("steel", dict(seed=5.1, tone=0.22, along="z", gloss=0.4, spec=0.5, floor_z=ZT, dust=0.3, grime=0.7)),
    "mat": ("plastic", dict(color=kmats.lin((30, 30, 30)), gloss=0.12, spec=0.06, mottle=0.15, dust=0.5, grime=0.5,
                            scuff=(0.66, 0.74))),
    "diffuser": ("plastic", dict(color=kmats.lin((206, 204, 192)), gloss=0.4, spec=0.3, dust=0.5, grime=0.3)),
    "diffuser_on": ("flat", dict(color=kmats.lin((255, 252, 236)), gloss=0.6, spec=0.4)),
    # fibreboard: brown, a blotchy tone with pin holes
    "cork": ("plastic", dict(color=kmats.lin((122, 92, 62)), gloss=0.08, spec=0.05, mottle=0.25, dust=0.3, grime=0.3)),
    "map": ("paint", dict(CLEAN, color=kmats.lin((226, 222, 200)), gloss=0.15, spec=0.08, dust=0.15,
                          decal_items=[wall_decal("decal_map.png", *L.MAP[:2], *L.MAP[2:], L.Y_MAP)])),
    "pin_yellow": ("plastic", dict(color=kmats.lin((220, 180, 30)), gloss=0.6, spec=0.5)),
    "pin_blue": ("plastic", dict(color=kmats.lin((40, 70, 170)), gloss=0.6, spec=0.5)),
    "string": ("plastic", dict(color=kmats.lin((176, 24, 22)), gloss=0.15, spec=0.08)),
    "rag": ("plastic", dict(color=kmats.lin((150, 36, 30)), gloss=0.06, spec=0.04, mottle=0.25, dust=0.3, grime=0.6,
                            scuff=(0.6, 0.7))),
    "bolt": ("paint", dict(color=kmats.lin((70, 68, 64)), under=kmats.lin((120, 72, 40)), seed=8.8, gloss=0.35,
                           spec=0.45, chip=(0.50, 0.58), rust=(0.45, 0.55), rust_low=0.0, floor_z=ZT, dust=0.2,
                           grime=0.5)),
    "pda": ("plastic", dict(color=kmats.lin((70, 72, 74)), gloss=0.35, spec=0.25, dust=0.3, grime=0.4,
                            scuff=(0.62, 0.70))),
    "psion": ("plastic", dict(color=kmats.lin((44, 46, 50)), gloss=0.4, spec=0.3, dust=0.3, scuff=(0.6, 0.7))),
    "cell": ("paint", dict(CLEAN, color=kmats.lin((40, 90, 150)), gloss=0.5, spec=0.4, dust=0.1)),
    "flash": ("plastic", dict(color=kmats.lin((40, 44, 52)), gloss=0.4, spec=0.3, dust=0.2, scuff=(0.6, 0.7))),
    "flash_cap": ("plastic", dict(color=kmats.lin((60, 100, 160)), gloss=0.45, spec=0.35, dust=0.2)),
    "pager": ("plastic", dict(color=kmats.lin((34, 36, 38)), gloss=0.35, spec=0.25, dust=0.25, grime=0.4,
                              scuff=(0.6, 0.7))),
    "pager_btn": ("plastic", dict(color=kmats.lin((92, 94, 96)), gloss=0.2, spec=0.1, dust=0.3, scuff=(0.6, 0.7))),
    # pager LED: "off" is dark red, "work" is lit (blinking is done by the mod script)
    "led": ("flat", dict(color=kmats.lin((70, 14, 12)), gloss=0.85, spec=0.8)),
    "led_on": ("flat", dict(color=kmats.lin((255, 60, 40)), gloss=0.85, spec=0.8)),
    "dark": ("flat", dict(color=kmats.lin((20, 20, 20)), gloss=0.2, spec=0.1)),
    "brass": ("paint", dict(CLEAN, color=kmats.lin((150, 124, 66)), gloss=0.55, spec=0.55, dust=0.15, grime=0.35)),
    "tin": ("steel", dict(seed=6.4, tone=0.30, along="z", gloss=0.45, spec=0.5, floor_z=ZT, dust=0.4, grime=0.6)),
    "ash": ("plastic", dict(color=kmats.lin((96, 94, 90)), gloss=0.05, spec=0.03, mottle=0.3)),
    "butt": ("plastic", dict(color=kmats.lin((226, 224, 214)), gloss=0.15, spec=0.1, dust=0.3, grime=0.4)),
    "filter": ("plastic", dict(color=kmats.lin((196, 140, 70)), gloss=0.15, spec=0.1, mottle=0.2)),
    # enamelled mug: white, chips down to black, blue rim
    "mug": ("paint", dict(color=kmats.lin((226, 224, 214)), under=kmats.lin((26, 26, 30)), seed=5.5, gloss=0.55,
                          spec=0.45, chip=(0.54, 0.60), rust=(0.80, 0.86), rust_low=0.0, floor_z=ZT, dust=0.2,
                          grime=0.5)),
    "mug_rim": ("paint", dict(color=kmats.lin((40, 56, 110)), under=kmats.lin((26, 26, 30)), seed=5.9, gloss=0.55,
                              spec=0.45, chip=(0.50, 0.56), rust=(0.80, 0.86), rust_low=0.0, floor_z=ZT, dust=0.1,
                              grime=0.4)),
    "tea": ("flat", dict(color=kmats.lin((60, 34, 16)), gloss=0.9, spec=0.7)),
    "knife": ("steel", dict(seed=6.9, tone=0.36, along="x", gloss=0.55, spec=0.65, floor_z=ZT, dust=0.1, grime=0.5)),
    "carton": ("plastic", dict(color=kmats.lin((214, 208, 196)), gloss=0.3, spec=0.2, mottle=0.06, dust=0.3,
                               grime=0.3)),
    "carton_band": ("plastic", dict(color=kmats.lin((150, 30, 30)), gloss=0.35, spec=0.25, dust=0.25)),
    "notebook": ("plastic", dict(color=kmats.lin((46, 64, 52)), gloss=0.35, spec=0.2, dust=0.3, scuff=(0.58, 0.68))),
    "pages": ("plastic", dict(color=kmats.lin((214, 208, 186)), gloss=0.1, spec=0.05, mottle=0.1, dust=0.3,
                              grime=0.3)),
    "deck": ("plastic", dict(color=kmats.lin((150, 40, 36)), gloss=0.3, spec=0.2, mottle=0.1, dust=0.2)),
    "roll": ("plastic", dict(color=kmats.lin((212, 204, 176)), gloss=0.1, spec=0.05, mottle=0.12, dust=0.45)),
    "roll_end": ("plastic", dict(color=kmats.lin((168, 160, 134)), gloss=0.08, spec=0.05, mottle=0.3, dust=0.5)),
    "twine": ("plastic", dict(color=kmats.lin((150, 128, 88)), gloss=0.08, spec=0.05, mottle=0.25, dust=0.3)),
    "cashbox": ("paint", dict(color=kmats.lin((66, 84, 70)), under=kmats.lin((150, 150, 150)), seed=7.2, gloss=0.4,
                              spec=0.35, chip=(0.55, 0.61), rust=(0.62, 0.70), rust_low=0.0, floor_z=ZP, dust=0.4,
                              grime=0.5)),
    "card": ("plastic", dict(color=kmats.lin((150, 118, 80)), gloss=0.08, spec=0.05, mottle=0.18, dust=0.4, grime=0.7,
                             scuff=(0.60, 0.70))),
    "junk": ("plastic", dict(color=kmats.lin((78, 74, 60)), gloss=0.08, spec=0.05, mottle=0.3, dust=0.4, grime=0.6)),
    # "Elektronika-302" tape recorder: black plastic, aluminium strip, grille, lid with a window
    "rec_body": ("plastic", dict(color=kmats.lin((26, 26, 28)), gloss=0.30, spec=0.22, dust=0.45, grime=0.5,
                                 scuff=(0.58, 0.66))),
    "rec_handle": ("plastic", dict(color=kmats.lin((24, 24, 26)), gloss=0.35, spec=0.25, dust=0.3, grime=0.6,
                                   scuff=(0.50, 0.60))),
    "rec_grille": ("plastic", dict(color=kmats.lin((22, 22, 24)), gloss=0.28, spec=0.2, dust=0.6, grime=0.5,
                                   scuff=(0.62, 0.70))),
    "rec_cloth": ("plastic", dict(color=kmats.lin((12, 12, 13)), gloss=0.05, spec=0.03, mottle=0.2, dust=0.4)),
    "rec_lid": ("plastic", dict(color=kmats.lin((20, 20, 22)), gloss=0.55, spec=0.4, dust=0.4, grime=0.3,
                                scuff=(0.60, 0.70))),
    "rec_alu": ("paint", dict(CLEAN, color=kmats.lin((190, 192, 188)), gloss=0.45, spec=0.5, dust=0.25, grime=0.3,
                              decal_items=[top_decal("decal_rec_strip.png", (L.REC[0], L.REC[1] + (_SY0 + _SY1) / 2),
                                                     (L.REC_W, _SY1 - _SY0))])),
    "rec_alu_plain": ("steel", dict(seed=8.4, tone=0.55, along="x", gloss=0.55, spec=0.6, dust=0.2, grime=0.3)),
    "rec_plate": ("steel", dict(seed=8.8, tone=0.50, along="x", gloss=0.6, spec=0.6, dust=0.3, grime=0.2)),
    "cassette": ("plastic", dict(color=kmats.lin((52, 52, 56)), gloss=0.45, spec=0.3, dust=0.2)),
    "cass_label": ("paint", dict(CLEAN, color=kmats.lin((226, 220, 196)), gloss=0.2, spec=0.1, dust=0.1,
                                 decal_items=[top_decal("decal_cass_label.png", (L.REC[0] + _CX, L.REC[1] + _CY),
                                                        (_CW, _CH))])),
    "hub": ("plastic", dict(color=kmats.lin((224, 222, 214)), gloss=0.45, spec=0.3, dust=0.1)),
    "tape": ("plastic", dict(color=kmats.lin((52, 34, 24)), gloss=0.7, spec=0.5, mottle=0.05)),
    "vu": ("paint", dict(CLEAN, color=kmats.lin((232, 226, 200)), gloss=0.3, spec=0.2,
                         decal_items=[top_decal("decal_vu.png", *vu_box())])),
    "needle": ("flat", dict(color=kmats.lin((24, 22, 20)), gloss=0.3, spec=0.2)),
    "knob": ("plastic", dict(color=kmats.lin((22, 22, 24)), gloss=0.4, spec=0.3, dust=0.3, grime=0.4,
                             scuff=(0.55, 0.65))),
    "key": ("plastic", dict(color=kmats.lin((24, 24, 26)), gloss=0.4, spec=0.3, dust=0.3, grime=0.5,
                            scuff=(0.50, 0.60))),
})
for _nm, x0, x1, z0, z1 in L.PINNED:
    KINDS[_nm] = ("paint", dict(CLEAN, color=kmats.lin((226, 222, 204)), gloss=0.15, spec=0.08, dust=0.1,
                                decal_items=[wall_decal("decal_%s.png" % _nm, x0, x1, z0, z1, L.Y_PIN)]))
for _nm, (cx, cy), deg, (w, h), dz, kind, _c in L.PAPERS:
    KINDS[_nm] = ("paint", dict(CLEAN, color=kmats.lin((222, 218, 200)), gloss=0.12, spec=0.06, dust=0.1,
                                decal_items=[top_decal("decal_%s.png" % _nm, (cx, cy), rot_box(w, h, deg))]))

OBJ, NAME = "m15_bnd_pack_trail", "ozr_bnd_pack_trail"
# Work look: the luminaire is ozl_lamp, the pager display is ozl_screen (own texture, frames), the pager
# LED is ozl_lamp_2 (blinks); the tape recorder - bones of the reels, the needle and the keys
SEL_LAMP, SEL_SCREEN, SEL_LED = "ozl_lamp", "ozl_screen", "ozl_lamp_2"
SEL = dict(reel_l="ozl_reel_l", reel_r="ozl_reel_r", needle="ozl_needle", keys="ozl_keys")
# "work" look preview: the diffuser and the LED are lit, the first frame on the display, the keys are
# pressed (move), the needle is rotated in _posed (its shift is zero - a marker)
ON = dict(remap={"diffuser": "diffuser_on", "led": "led_on"}, emissive=(1.0, 1.0, 1.0, 1.0),
          move={SEL["keys"]: R.keys_move(), SEL["needle"]: (0.0, 0.0, 0.0)})
# reel loops: the supply (full) reel makes 2 turns per pass, the take-up (empty) one 4; the angle sign follows
# the rule of M01, M08, M14 (axis toward the person is up, plus is
# clockwise): minus is counter-clockwise, as the tape runs
REEL_ANIMS = tuple(("ozl_work_reel_%s" % s, dict(type="rotation", source="ozl_work", sourceAddress="loop",
                                                   selection=SEL["reel_" + s], axis="ozl_reel_%s_axis" % s, memory=1,
                                                   minValue=0.0, maxValue=mv, angle0=0.0, angle1=-2 * math.pi))
                   for s, mv in (("l", 0.5), ("r", 0.25)))
NEEDLE_ANIM = ("ozl_needle_vu", dict(type="rotation", source="ozl_needle", selection=SEL["needle"],
                                     axis="ozl_needle_axis", memory=1, minValue=0.0, maxValue=1.0, angle0=0.0,
                                     angle1=math.radians(R.NEEDLE_SWEEP)))
KEYS_ANIM = ("ozl_keys_press", dict(type="translation", source="ozl_keys", selection=SEL["keys"], axis="ozl_keys_axis",
                                    memory=1, minValue=0.0, maxValue=1.0, offset0=0.0, offset1=R.KEY_TRAVEL))
PANELS = {"pager": dict(off="decal_pager_off.png", frames=["decal_pager_f%02d.png" % i for i in range(8)], size=128,
                        gloss=0.7)}
# module proxies: slots OZL_Tool1..3 are linked to them by the mod's CfgNonAIVehicles (Proxyozl_tool1..3);
# slot N is module N of the "Trails" line (M78, M79, M80), no rotation: modules face the person
PROXIES = [(r"\OpenZone_Research\models\proxies\ozl_tool%d" % (i + 1), m) for i, m in enumerate(L.MODS)]
BOUNDS = {}


def in_rect(x, y, c, deg, w, h):
    a = math.radians(deg)
    dx, dy = x - c[0], y - c[1]
    u = dx * math.cos(a) + dy * math.sin(a)
    v = -dx * math.sin(a) + dy * math.cos(a)
    return abs(u) <= w / 2 and abs(v) <= h / 2


def top_at(x, y):
    """Table top at a point: the board or the topmost paper under it."""
    z = ZT
    for nm, c, deg, (w, h), dz, kind, curl in L.PAPERS:
        if in_rect(x, y, c, deg, w, h):
            z = max(z, ZT + dz + L.PAPER_T)
    return z


def on_desk(key, x, y, **kw):
    """A vanilla item on the table: the bottom rests on the top paper beneath it."""
    return kv.put(key, (x, y, top_at(x, y)), **kw)


# vanilla DayZ items (kvanilla; none has a Proxy<name> class; the texture is in the model itself, not in the
# config): on the table - a partly drunk vodka, a folded Chernarus map by the tablet, a pen on the sketch, a
# lighter and two cigarettes by the packs; on the shelf - binoculars and two cassettes by the tape
# recorder; under the table - an empty vodka lying on its side
DECOR = [
    on_desk("vodka", 0.722, 0.252, up=(0, 0, 1), fwd=(0.4, -1, 0)),
    on_desk(r"dz\gear\navigation\Map_chernarus", 0.150, 0.222, **kv.flat(98)),
    on_desk("pen", -0.430, -0.268, **kv.flat(10)),
    on_desk(r"dz\gear\cooking\petrol_lighter", 0.372, 0.022, up=(math.cos(math.radians(14)), math.sin(math.radians(14)), 0),
            fwd=(-math.sin(math.radians(14)), math.cos(math.radians(14)), 0)),
    on_desk(r"dz\gear\medical\Cigarettes_unlit", 0.258, 0.122, **kv.flat(35)),
    on_desk(r"dz\gear\medical\Cigarettes_unlit", 0.340, 0.148, **kv.flat(-18)),
    kv.put(r"dz\gear\optics\binoculars", (-0.185, 0.205, ZP), **kv.flat(90)),
    kv.put("cassette", (0.392, 0.112, ZP), **kv.flat(94)),
    kv.put("cassette", (0.404, 0.287, ZP), **kv.flat(82)),
    kv.put("vodka", (-0.12, -0.24, 0.0), **kv.flat(165)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.34, 0.34, 0.36), clear=0.16, edge=0.12, smudge=0.10, streaks=0.03),
                 selections=(SEL_LAMP, SEL_SCREEN, SEL_LED) + tuple(SEL.values()), hidden=(SEL_LAMP, SEL_SCREEN, SEL_LED),
                 states={"on": ON}, bones=tuple((s, "") for s in SEL.values()),
                 animations=REEL_ANIMS + (NEEDLE_ANIM, KEYS_ANIM), proxies=PROXIES, decor=DECOR, panels=PANELS,
                 modules=[(o, n, m) for (o, n), m in zip(L.MOD_OBJ, L.MODS)], vsections={"cigs": CIGS},
                 sources={"ozl_work": dict(animPeriod=6.0), "ozl_needle": dict(animPeriod=0.2),
                          "ozl_keys": dict(animPeriod=0.15)})
P = M.part

# "Work" pose in the preview (render only, not exported to p3d): the indicator needle goes from the stop to the middle
POSE = {SEL["needle"]: R.needle_pose(NEEDLE_MID)}


def _posed(place):
    """krender.place_look / place that rotates the POSE group parts in the "work" look (move = ON["move"])."""
    def wrap(parts, *a, **kw):
        obs = place(parts, *a, **kw)
        if kw.get("move") is ON["move"]:
            for ob, p in zip(obs, parts):
                if p.group in POSE:
                    piv, ax, ang = POSE[p.group]
                    m = Matrix.Translation(piv) @ Matrix.Rotation(ang, 4, ax) @ Matrix.Translation(-piv)
                    ob.matrix_world = m @ Matrix.Translation(ob.location)
        return obs
    return wrap


krender.place_look = _posed(krender.place_look)
krender.place = _posed(krender.place)


def bev(lod, r=0.003, seg=1):
    return dict(r=r, seg=seg) if lod == 0 else {}


# =============================================================================
# Table (base B1, boards), luminaire, slot 2 mat
# =============================================================================
BEVEL = {"wb_frame": 0.003, "wb_fronts": 0.0025, "wb_shelf": 0.0015, "wb_panel": 0.003}
PLANKS = ("plank_a", "plank_b", "plank_c", "plank_b")


def build_bench(spec):
    lod = spec["lod"]
    parts = [p for p in kfurn.workbench(M, spec, X0, X1, Y0, Y1, ZT, ZP, SHD, cab_w=CAB_W, worktop="board",
                                        outlets=0, lamp=False) if p.name != "wb_top"]
    for p in parts:
        # chamfers on the edges (the kfurn base is boxes with sharp edges): near LOD only
        if lod == 0 and p.name in BEVEL:
            g.bevel(p.bm, p.bm.edges[:], BEVEL[p.name], 1)
    # boards: four planed 40 mm boards with rounded edges and gaps, each with its own tone
    w = (Y1 - Y0 + 0.015) / 4
    if lod == 2:
        pl = P("planks", "plank_a")
        g.box(pl, X0 - 0.01, X1 + 0.01, Y0 - 0.01, Y1 + 0.005, ZU, ZT)
        return parts + [pl]
    for k in range(4):
        ya = Y0 - 0.01 + k * w + (0.0015 if k else 0.0)
        yb = Y0 - 0.01 + (k + 1) * w - (0.0015 if k < 3 else 0.0)
        pl = P("plank%d" % k, PLANKS[k])
        g.box(pl, X0 - 0.01, X1 + 0.01, ya, yb, ZU, ZT, **bev(lod, 0.004))
        parts.append(pl)
    if lod == 0:
        # screws: two per board over the left legs and at the right edge; feet under the left legs
        sc = P("plank_screws", "screw")
        for k in range(4):
            yc = Y0 - 0.01 + (k + 0.5) * w
            for x in (X0 + 0.03, X1 - 0.03):
                lathe(sc, [(0.0042, 0.0), (0.0036, 0.0007)], 6, center=(x, yc + 0.03 * ((k % 2) - 0.5), ZT - 0.0003),
                      cap1=True)
        parts.append(sc)
        ft = P("wb_feet", "steel")
        for y in (Y0 + 0.05, Y1 - 0.05):
            g.cyl(ft, (X0 + 0.03, y, 0.016), "z", 0.009, 0.010, 6)
        parts.append(ft)
        # self-tapping screws on the back-panel posts and the shelf gussets
        st = P("shelf_screws", "screw")
        for xa in (X0 + 0.015, X1 - 0.015):
            for z in (ZT + 0.06, ZS - 0.05):
                g.cyl(st, (xa, Y1 - 0.0355, z), "y", 0.0045, 0.0012, 8)
        parts.append(st)
    return parts


def build_lamp(spec):
    """Luminaire under the shelf: a box with a chamfer, end caps, a convex diffuser (ozl_lamp in all LODs),
    the cord - along the shelf behind the right post and down behind the table."""
    lod = spec["lod"]
    zb = ZS - 0.045
    lm = P("lamp_box", "lamp_box")
    g.box(lm, LX0, LX1, LY0, LY1, zb, ZS, **bev(lod, 0.004))
    parts = [lm]
    df = P("lamp_diffuser", "diffuser", group=SEL_LAMP)
    n = 6 if lod == 0 else 2
    ya, yb = LY0 + 0.006, LY1 - 0.006
    poly = [(ya + (yb - ya) * k / n, zb + 0.001 - 0.012 * math.sin(math.pi * k / n)) for k in range(n + 1)]
    g.prism(df, poly, (1, 2), LX0 + 0.016, LX1 - 0.016)
    parts.append(df)
    if lod == 2:
        return parts
    ec = P("lamp_caps", "black")
    for xa, xb in ((LX0, LX0 + 0.016), (LX1 - 0.016, LX1)):
        g.box(ec, xa, xb, LY0 + 0.003, LY1 - 0.003, zb - 0.013, zb + 0.001, **bev(lod, 0.002))
    parts.append(ec)
    if lod == 0:
        cd = P("lamp_cord", "black")
        cable(cd, [(LX1 - 0.006, LY0 + 0.060, zb - 0.007), (LX1 + 0.022, LY0 + 0.068, zb - 0.003),
                   (X1 - 0.050, YP - 0.040, ZS - 0.008), (X1 - 0.012, Y1 + 0.009, ZS - 0.030),
                   (X1 - 0.012, Y1 + 0.010, ZT + 0.25), (X1 - 0.016, Y1 + 0.012, ZT - 0.12)], 0.003, 6)
        parts.append(cd)
    return parts


def build_slot2(spec):
    """Slot 2 on the shelf at the right: a rubber mat under the radio
    scanner M79 (empty - the mat and the cable plug)."""
    if spec["lod"] == 2:
        return []
    x0, x1, y0, y1, t = L.MAT2
    mt = P("slot2_mat", "mat")
    g.box(mt, x0, x1, y0, y1, ZP, ZP + t, **bev(spec["lod"], 0.0012))
    return [mt]


# =============================================================================
# Back panel: fibreboard, map, photos, notes, pins, threads
# =============================================================================
def pin_root(x, z):
    return Vector((x, L.Y_PIN - 0.0012, z))


def build_board(spec):
    lod = spec["lod"]
    x0, x1, z0, z1 = L.CORK
    ck = P("cork", "cork")
    g.box(ck, x0, x1, L.Y_CORK, YP, z0, z1, **bev(lod, 0.002))
    mp = P("map", "map")
    mx0, mx1, mz0, mz1 = L.MAP
    g.box(mp, mx0, mx1, L.Y_MAP, L.Y_CORK, mz0, mz1)
    parts = [ck, mp]
    if lod == 2:
        return parts
    for nm, a0, a1, b0, b1 in L.PINNED:
        pp = P(nm, nm)
        g.box(pp, a0, a1, L.Y_PIN, L.Y_CORK, b0, b1)
        parts.append(pp)
    if lod > 0:
        return parts
    nl = P("cork_nails", "steel")
    for x in (x0 + 0.015, x1 - 0.015):
        for z in (z0 + 0.015, z1 - 0.015):
            lathe(nl, [(0.0038, 0.0), (0.0036, 0.0008), (0.0026, 0.0013)], 6, center=(x, L.Y_CORK, z), axis=(0, -1, 0),
                  cap1=True)
    parts.append(nl)
    # pins: a ball on a needle; the threads are tied round the needle under the ball, with sag
    heads = {c: P("pins_" + c, "pin_" + c) for c in ("red", "yellow", "blue")}
    nd = P("pin_needles", "steel")
    for x, z, c in L.PINS:
        base = Vector((x, L.Y_PIN - 0.0016, z))
        lathe(heads[c], [(0.0014, 0.0), (0.0030, 0.0016), (0.0028, 0.0044), (0.0012, 0.0060)], 7, center=base,
              axis=(0, -1, 0), cap0=True, cap1=True)
        rod(nd, (x, L.Y_PIN + 0.0002, z), base, 0.0005, 3)
    parts += list(heads.values()) + [nd]
    st = P("strings", "string")
    for i, j in L.STRINGS:
        a, b = pin_root(*L.PINS[i][:2]), pin_root(*L.PINS[j][:2])
        sag = 0.002 + 0.008 * (a - b).length
        pts = [a + (b - a) * t - Vector((0, 0, 4 * sag * t * (1 - t))) for t in (0.0, 0.25, 0.5, 0.75, 1.0)]
        g.pipe(st, [tuple(p) for p in pts], 0.0007, 3)
    parts.append(st)
    return parts


# =============================================================================
# Shelf: map rolls, a box with a lock
# =============================================================================
def build_shelf(spec):
    lod, sd = spec["lod"], spec["sides"]
    if lod == 2:
        return []
    rl = P("rolls", "roll")
    parts = [rl]
    re_ = P("roll_ends", "roll_end") if lod == 0 else None
    tw = P("roll_twine", "twine") if lod == 0 else None
    for k, (x, y, r, ln) in enumerate(L.ROLLS):
        z = ZP + r + (0.035 if k == 2 else 0.0)
        g.cyl(rl, (x, y, z), "x", r, ln, sd if lod == 0 else 6, cap=lod > 0)
        if lod == 0:
            for s in (-1, 1):
                # end: a rolled sheet - dark turns (no decal, an end tone) and a hole in the middle
                xe = x + s * ln / 2
                lathe(re_, [(r - 0.0006, 0.0), (0.0045, 0.0)], sd, center=(xe, y, z), axis=(s, 0, 0))
                lathe(re_, [(0.0045, -0.03), (0.0045, 0.0)], 8, center=(xe, y, z), axis=(s, 0, 0), inward=True,
                      cap0=True)

    if lod == 0:
        for x, y, r, ln in L.ROLLS[:1] + L.ROLLS[2:]:
            z = ZP + r + (0.035 if r == L.ROLLS[2][2] else 0.0)
            ring(tw, (x + 0.04, y, z), (1, 0, 0), r + 0.0006, 0.0011, 10, 3)
        parts += [re_, tw]
    # box: body, lid with a rim on a hinge at the back, handle, hasp with a padlock
    x0, x1, y0, y1, h = L.TIN
    tb = P("cashbox", "cashbox")
    g.box(tb, x0, x1, y0, y1, ZP, ZP + h - 0.014, **bev(lod, 0.004, 2))
    g.box(tb, x0 - 0.003, x1 + 0.003, y0 - 0.003, y1 + 0.003, ZP + h - 0.016, ZP + h, **bev(lod, 0.003, 1))
    parts.append(tb)
    if lod == 0:
        cx = (x0 + x1) / 2
        hg = P("cashbox_steel", "steel")
        g.cyl(hg, (cx, y1 + 0.004, ZP + h - 0.014), "x", 0.004, x1 - x0 - 0.04, 8)
        # bracket handle on the lid
        g.pipe(hg, spline([(cx - 0.045, (y0 + y1) / 2, ZP + h), (cx - 0.040, (y0 + y1) / 2 - 0.004, ZP + h + 0.010),
                           (cx + 0.040, (y0 + y1) / 2 - 0.004, ZP + h + 0.010), (cx + 0.045, (y0 + y1) / 2, ZP + h)], 3),
               0.0028, 6)
        # hasp on the face: a plate and a ring (the hole is along x), the padlock shackle goes through it
        zs = ZP + h - 0.020
        g.box(hg, cx - 0.010, cx + 0.010, y0 - 0.0035, y0 - 0.0005, zs - 0.012, zs + 0.006, r=0.001, seg=1)
        ring(hg, (cx, y0 - 0.0085, zs), (1, 0, 0), 0.0045, 0.0013, 8, 4)
        ys = y0 - 0.0085
        arc = [(cx + 0.0095 * math.cos(math.pi * k / 6), ys, zs - 0.0095 + 0.0095 * math.sin(math.pi * k / 6))
               for k in range(7)]
        g.pipe(hg, [(cx + 0.0095, ys, zs - 0.024)] + arc + [(cx - 0.0095, ys, zs - 0.024)], 0.0022, 5)
        parts.append(hg)
        lk = P("cashbox_lock", "brass")
        g.box(lk, cx - 0.018, cx + 0.018, ys - 0.007, ys + 0.007, zs - 0.052, zs - 0.022, r=0.004, seg=2)
        g.cyl(lk, (cx, ys - 0.0072, zs - 0.042), "y", 0.0035, 0.0012, 10)
        parts.append(lk)
    return parts


# =============================================================================
# Table board: papers, bolts, PDAs, flash drives, pager, knife, keys, ashtray, mug, cigarettes
# =============================================================================
def build_papers(spec):
    lod = spec["lod"]
    parts = []
    for nm, (cx, cy), deg, (w, h), dz, kind, curl in L.PAPERS:
        if lod == 2 and kind != "sketch":
            continue
        pp = P(nm, nm)
        fr = frame_z(cx, cy, deg, ZT + dz)
        if lod == 0 and curl:
            ci, amt = curl
            cs, cq = ((0, 0), (1, 0), (1, 1), (0, 1))[ci]
            ss = (0.0, 0.3, 1.0) if cs == 0 else (0.0, 0.7, 1.0)
            qs = (0.0, 0.3, 1.0) if cq == 0 else (0.0, 0.7, 1.0)
            sheet(pp, fr, w, h, L.PAPER_T, lambda s, q, cs=cs, cq=cq, amt=amt: amt if (s, q) == (cs, cq) else 0.0, ss, qs)
        else:
            g.box(pp, -w / 2, w / 2, -h / 2, h / 2, 0.0, L.PAPER_T, frame=fr)
        parts.append(pp)
    return parts


def bolt(bt, fr, lod):
    """M12 x 80 bolt in the axes of fr (u - from the head to the end along the axis, n - up): a hexagonal
    head with a chamfer (lies on a face), a plain shank, thread over 30 mm, a chamfered end."""
    ax, e1, e2 = basis(fr.u)
    dn = -fr.n
    ph = math.atan2(dn.dot(e2), dn.dot(e1)) - math.pi / 6
    hx = [(0.0098, 0.0), (0.0104, 0.0007), (0.0104, 0.0068), (0.0095, 0.0075)]
    lathe(bt, hx, 6, center=fr.o, axis=fr.u, cap0=True, cap1=True, phase=ph)
    prof = [(0.0060, 0.0075), (0.0060, 0.0575)]
    if lod == 0:
        for k in range(4):
            u = 0.0575 + 0.0065 * k
            prof += [(0.0053, u + 0.00325), (0.0060, u + 0.0065)]
    prof += [(0.0060, 0.0865), (0.0050, 0.0875)]
    lathe(bt, prof, 7, center=fr.o, axis=fr.u, cap1=True)


def build_bolts(spec):
    """Marker bolts on the sketch and by the ashtray: some have a strip of red rag tied at the head, the
    ends lie on the paper."""
    lod = spec["lod"]
    if lod > 0:
        return []
    bt = P("bolts", "bolt")
    rg = P("bolt_rags", "rag")
    for (cx, cy), deg, rag in L.BOLTS:
        z0 = top_at(cx, cy)
        a = math.radians(deg)
        d = Vector((math.cos(a), math.sin(a), -0.0375)).normalized()
        v = Vector((0, 0, 1)).cross(d).normalized()
        n = d.cross(v).normalized()
        fr = g.Frame(Vector((cx, cy, z0 + 0.009)), d, v, n)
        bolt(bt, fr, lod)
        if rag:
            kc = fr.p(0.024, 0.0, 0.0)
            ring(rg, kc, fr.u, 0.0068, 0.0019, 7, 4)
            for s, ln, bend in ((1, 0.046, 0.5), (-1, 0.034, -0.7)):
                side = Vector((math.cos(a + s * math.pi / 2), math.sin(a + s * math.pi / 2), 0.0))
                fwd = Vector((math.cos(a), math.sin(a), 0.0))
                base = Vector((kc.x, kc.y, 0.0)) + side * 0.0070
                pts = []
                for k in range(4):
                    t = k / 3
                    p = base + side * (ln * t) + fwd * (bend * 0.02 * t * t)
                    zz = top_at(p.x, p.y) + 0.0007 + (0.006 * (1 - t) ** 2 if k < 2 else 0.0)
                    pts.append((p.x, p.y, zz))
                ribbon(rg, pts, (fwd.x, fwd.y, 0.0), 0.0036, 0.0006)
    return [bt, rg]


def build_pdas(spec):
    """Palm face down: body, battery compartment without the cover (springs), the cover beside, two AAA
    cells; Psion Series 5 closed: two halves with a dark seam, hinge at the back."""
    lod, sd = spec["lod"], spec["sides"]
    if lod == 2:
        return []
    w, h, t = L.PALM
    parts = []
    (cx, cy), deg = L.PDA_DOWN
    fr = frame_z(cx, cy, deg, top_at(cx, cy))
    pb = P("pda_down", "pda")
    g.box(pb, -w / 2, w / 2, -h / 2, h / 2, 0.0, t, frame=fr, **bev(lod, 0.005, 2))
    parts.append(pb)
    if lod == 0:
        dk = P("pda_bay", "dark")
        g.box(dk, -0.026, 0.026, -0.042, -0.004, t - 0.0004, t + 0.0004, frame=fr)
        sp = P("pda_springs", "steel")
        for xa in (-0.022, 0.022):
            for ya in (-0.033, -0.013):
                g.cyl(sp, (xa, ya, t + 0.0006), "z", 0.0022, 0.0006, 8, frame=fr)
        parts += [dk, sp]
        cv = P("pda_cover", "pda")
        g.box(cv, 0.052, 0.108, -0.050, -0.010, 0.0, 0.0016, frame=fr, r=0.0007, seg=1)
        g.box(cv, 0.056, 0.064, -0.034, -0.026, 0.0016, 0.0030, frame=fr)
        parts.append(cv)
        # AAA cells: blue sleeve, steel ends and the "plus" nub
        ce = P("pda_cells", "cell")
        ct = P("pda_cell_ends", "steel")
        for k in range(2):
            c = fr.p(0.056 + 0.0115 * k, 0.012 - 0.002 * k, 0.00525)
            lathe(ce, [(0.0050, 0.0), (0.00525, 0.0008), (0.00525, 0.0437), (0.0050, 0.0445)], 10, center=c, axis=fr.v)
            lathe(ct, [(0.0048, 0.0), (0.0048, 0.0003)], 8, center=c, axis=-fr.v, cap1=True)
            lathe(ct, [(0.0048, 0.0445), (0.0048, 0.0448)], 8, center=c, axis=fr.v, cap1=True)
            lathe(ct, [(0.0018, 0.0448), (0.0018, 0.0458)], 8, center=c, axis=fr.v, cap1=True)
        parts += [ce, ct]
    (cx, cy), deg, (pw, ph, pt) = L.PSION
    fr = frame_z(cx, cy, deg, top_at(cx, cy))
    ps = P("psion", "psion")
    g.box(ps, -pw / 2, pw / 2, -ph / 2, ph / 2, 0.0, pt * 0.48, frame=fr, **bev(lod, 0.005, 1))
    g.box(ps, -pw / 2, pw / 2, -ph / 2, ph / 2, pt * 0.52, pt, frame=fr, **bev(lod, 0.005, 1))
    parts.append(ps)
    if lod == 0:
        sm = P("psion_seam", "dark")
        g.box(sm, -pw / 2 + 0.003, pw / 2 - 0.003, -ph / 2 + 0.003, ph / 2 - 0.003, pt * 0.46, pt * 0.54, frame=fr)
        g.cyl(ps, (0.0, ph / 2 - 0.006, pt / 2), "x", 0.0075, pw - 0.03, 12, frame=fr)
        parts.append(sm)
    return parts


def build_flash(spec):
    """Flash drives: body with rounded edges and a loop, cap; on the second one the cap is off and lies
    beside - the steel connector with a tongue is visible."""
    lod = spec["lod"]
    if lod > 0:
        return []
    fb = P("flash", "flash")
    fc = P("flash_caps", "flash_cap")
    st = P("flash_plugs", "steel")
    dk = P("flash_tongue", "dark")
    for i, ((cx, cy), deg) in enumerate(L.FLASH):
        z = top_at(cx, cy)
        fr = frame_z(cx, cy, deg, z)
        g.box(fb, -0.030, 0.012, -0.009, 0.009, 0.0, 0.008, frame=fr, r=0.002, seg=1)
        ring(fb, fr.p(-0.033, 0.0, 0.004), fr.n, 0.0045, 0.0011, 6, 3)
        if i == 1:
            g.box(st, 0.012, 0.024, -0.006, 0.006, 0.0018, 0.0063, frame=fr)
            g.box(dk, 0.0135, 0.0243, -0.005, 0.005, 0.0032, 0.0049, frame=fr)
            fz = frame_z(*L.local((cx, cy), deg, 0.046, 0.016), deg + 18, z)
            g.box(fc, -0.010, 0.010, -0.0095, 0.0095, 0.0, 0.009, frame=fz, r=0.002, seg=1)
        else:
            g.box(fc, 0.011, 0.031, -0.0095, 0.0095, 0.0, 0.009, frame=fr, r=0.002, seg=1)
    return [fb, fc, st, dk]


def build_pager(spec):
    """Pager face up: rounded body, display frame, display (ozl_screen, own texture pager), three buttons,
    LED (ozl_lamp_2), a lanyard loop."""
    lod = spec["lod"]
    if lod == 2:
        return []
    (cx, cy), deg = L.PAGER
    fr = frame_z(cx, cy, deg, top_at(cx, cy))
    pg = P("pager", "pager")
    g.box(pg, -0.031, 0.031, -0.0225, 0.0225, 0.0, 0.018, frame=fr, **bev(lod, 0.005, 2))
    parts = [pg]
    (sx, sy), (sw, sh) = L.PAGER_SCR
    if lod == 0:
        bz = P("pager_bezel", "dark")
        frame_plate(bz, (sx - sw / 2 - 0.003, sx + sw / 2 + 0.003, sy - sh / 2 - 0.003, sy + sh / 2 + 0.003),
                    (sx - sw / 2, sx + sw / 2, sy - sh / 2, sy + sh / 2), 0.0176, 0.0186, frame=fr)
        parts.append(bz)
    lc = P("pager_lcd", "dark", group=SEL_SCREEN, section="pager")
    zl = 0.0181
    vs = [lc.bm.verts.new(fr.p(a, b, zl)) for a, b in ((sx - sw / 2, sy - sh / 2), (sx + sw / 2, sy - sh / 2),
                                                       (sx + sw / 2, sy + sh / 2), (sx - sw / 2, sy + sh / 2))]
    f = lc.bm.faces.new(vs)
    f.normal_update()
    if f.normal.dot(fr.n) < 0:
        f.normal_flip()
    lc.tag([f])
    lc.glass_frame = (fr, sx - sw / 2, sx + sw / 2, sy - sh / 2, sy + sh / 2)
    parts.append(lc)
    ld = P("pager_led", "led", group=SEL_LED)
    lathe(ld, [(0.0019, 0.0), (0.0017, 0.0010), (0.0008, 0.0016)], 8 if lod == 0 else 5, center=fr.p(0.024, 0.016, 0.018),
          axis=fr.n, cap1=True)
    parts.append(ld)
    if lod == 0:
        bn = P("pager_buttons", "pager_btn")
        for a in (-0.016, 0.0, 0.016):
            g.box(bn, a - 0.006, a + 0.006, -0.0185, -0.0110, 0.0175, 0.0195, frame=fr, r=0.0009, seg=1)
        ring(pg, fr.p(-0.0335, 0.012, 0.009), fr.v, 0.0035, 0.0012, 8, 4)
        parts.append(bn)
    return parts


def build_knife(spec):
    """Folded butterfly knife (as in M13): two handles with slots and rounded ends, the blade between them,
    pivots, latch."""
    lod = spec["lod"]
    (cx, cy), deg = L.KNIFE
    fr = frame_z(cx, cy, deg, top_at(cx, cy))
    kn = P("knife", "knife")
    if lod > 0:
        g.box(kn, -0.065, 0.065, -0.013, 0.013, 0.0, 0.012, frame=fr)
        return [kn] if lod == 1 else []
    outline = rounded_rect(0.130, 0.024, 0.008, 3)
    plate(kn, outline, 0.0, 0.0048, fr)
    plate(kn, outline, 0.0078, 0.0126, fr)
    g.box(kn, -0.046, 0.058, -0.0105, 0.0085, 0.0048, 0.0078, frame=fr)               # blade between the handles
    dk = P("knife_slots", "dark")
    for a in (-0.046, -0.030, -0.014, 0.002, 0.018):
        plate(dk, [(a + x, y) for x, y in rounded_rect(0.011, 0.0065, 0.003, 1)], 0.0126, 0.0130, fr)
    parts = [kn, dk]
    pn = P("knife_pins", "brass")
    for a in (0.055, 0.044):
        g.cyl(pn, (a, 0.0, 0.0130), "z", 0.0024, 0.0010, 10, frame=fr)
    box_to(pn, fr.p(-0.0645, -0.008, 0.0128), fr.p(-0.0645, 0.008, 0.0128), 0.003, 0.0016, up=fr.n)
    parts.append(pn)
    return parts


def build_keys(spec):
    """Bunch of keys on a split ring: Yale-type (flat, with a bit), lever (a shaft with a bit), a small
    padlock key - lie fanned out flat."""
    if spec["lod"] > 0:
        return []
    (cx, cy), deg = L.KEYS
    z0 = top_at(cx, cy)
    ky = P("keys", "brass")
    st = P("keys_steel", "steel")
    rr = 0.0145
    ring(st, (cx, cy, z0 + 0.0013), (0, 0, 1), rr, 0.0012, 14, 4)
    # Yale-type key: a head with a hole (ring), a blade with notches along the bottom edge
    for k, (a, ln, t, kind) in enumerate(((-110.0, 0.056, 0.0022, "flat"), (-62.0, 0.070, 0.0, "warded"),
                                          (-20.0, 0.036, 0.0018, "flat"))):
        b = math.radians(a)
        o = (cx + rr * math.cos(b), cy + rr * math.sin(b))
        fr = frame_z(o[0], o[1], a, z0 + 0.0008 * k)
        if kind == "flat":
            hr = 0.010 if ln > 0.05 else 0.0075
            lathe(ky, [(0.0030, 0.0), (hr, 0.0), (hr, t), (0.0030, t)], 10, center=fr.p(hr, 0, 0), closed=True)
            teeth = [(hr * 1.7, -0.004)]
            xb = hr * 1.7
            for j in range(5):
                xb2 = hr * 1.7 + (ln - hr * 1.9) * (j + 1) / 5
                teeth += [((xb + xb2) / 2, -0.004 + 0.0018 * ((j * 7) % 3) / 2), (xb2, -0.004)]
                xb = xb2
            poly = [(hr * 1.6, 0.0035)] + [(ln, 0.0030), (ln, -0.0022)] + teeth[::-1][:-1] + [(hr * 1.6, -0.004)]
            g.prism(ky, poly, (0, 1), 0.0, t, frame=fr)
        else:
            # lever key: head ring, round shaft, a flag bit at the end
            ring(ky, fr.p(0.010, 0, 0.0018), fr.n, 0.0085, 0.0017, 10, 4)
            rod(ky, fr.p(0.018, 0, 0.0024), fr.p(ln, 0, 0.0024), 0.0024, 8)
            g.box(ky, ln - 0.012, ln - 0.002, -0.011, -0.0015, 0.0, 0.0040, frame=fr)
    return [st, ky]


def build_ashtray_mug(spec):
    """Tin ashtray dia. 115 with a rolled edge and three rests, ash, butts (filter, crumpled tip);
    enamelled mug 0.4 l: rolled blue rim, a handle in a smooth arc, tea."""
    lod, sd = spec["lod"], spec["sides"]
    if lod == 2:
        return []
    parts = []
    ax, ay = L.ASHTRAY
    z0 = top_at(ax, ay)
    n = 16 if lod == 0 else sd
    at = P("ashtray", "tin")
    prof = [(0.046, 0.0), (0.050, 0.003), (0.055, 0.019), (0.0565, 0.0205)]
    lathe(at, prof if lod == 0 else prof[::3], n, center=(ax, ay, z0), cap0=True)
    if lod == 0:
        lathe(at, [(r - 0.0009, h + 0.0004) for r, h in prof], n, center=(ax, ay, z0), inward=True)
        ring(at, (ax, ay, z0 + 0.0212), (0, 0, 1), 0.0567, 0.0012, n, 4)
        for k in range(3):
            b = math.radians(30 + 120 * k)
            d = Vector((math.cos(b), math.sin(b), 0))
            box_to(at, Vector((ax, ay, z0 + 0.0222)) + d * 0.059, Vector((ax, ay, z0 + 0.0222)) + d * 0.046, 0.009, 0.0012)
    parts.append(at)
    ah = P("ash", "ash")
    g.cyl(ah, (ax, ay, z0 + 0.0025), "z", 0.0455, 0.003, n)
    parts.append(ah)
    if lod == 0:
        bt = P("butts", "butt")
        fl = P("butt_filters", "filter")
        dk = P("butt_tips", "dark")
        for k, (a, ln, tilt) in enumerate(((20, 0.026, 0.12), (95, 0.022, 0.20), (160, 0.030, 0.08), (250, 0.018, 0.25),
                                           (310, 0.024, 0.15))):
            b = math.radians(a)
            d = Vector((math.cos(b), math.sin(b), tilt)).normalized()
            p0 = Vector((ax + 0.010 * math.cos(b), ay + 0.010 * math.sin(b), z0 + 0.0078))
            lathe(dk, [(0.0026, 0.0), (0.0037, 0.0022)], 8, center=p0, axis=d, cap0=True)
            lathe(bt, [(0.0037, 0.0022), (0.0038, ln - 0.013)], 8, center=p0, axis=d)
            lathe(fl, [(0.0038, ln - 0.013), (0.0039, ln - 0.0005), (0.0034, ln)], 8, center=p0, axis=d, cap1=True)
        parts += [bt, fl, dk]
    # mug
    mx, my = L.MUG
    z0 = top_at(mx, my)
    n = 18 if lod == 0 else sd
    mg = P("mug", "mug")
    out = [(0.0390, 0.0), (0.0418, 0.0018), (0.0425, 0.008), (0.0425, 0.0805)]
    lathe(mg, out if lod == 0 else [out[0], out[-1]], n, center=(mx, my, z0), cap0=True)
    if lod == 0:
        lathe(mg, [(0.0411, 0.006), (0.0411, 0.0810)], n, center=(mx, my, z0), inward=True)
        rm = P("mug_rim", "mug_rim")
        ring(rm, (mx, my, z0 + 0.0812), (0, 0, 1), 0.0420, 0.0016, n, 4)
        parts.append(rm)
    hp = [(mx + 0.0418, my, z0 + 0.068), (mx + 0.060, my, z0 + 0.066), (mx + 0.0665, my, z0 + 0.046),
          (mx + 0.060, my, z0 + 0.024), (mx + 0.0418, my, z0 + 0.018)]
    g.pipe(mg, spline(hp, 2) if lod == 0 else hp[::2], 0.0042, 8 if lod == 0 else 4)
    parts.append(mg)
    te = P("tea", "tea")
    g.cyl(te, (mx, my, z0 + 0.058), "z", 0.0412, 0.002, n)
    parts.append(te)
    return parts


def build_cigs(spec):
    """Opened carton of cigarettes: a cardboard box without a top, the lid folded back, packs inside (two
    are missing on top - the lower ones show); on the table two packs, cigarettes stick out of one. The packs
    use the vanilla "Chernomorka" texture (section cigs)."""
    lod = spec["lod"]
    if lod == 2:
        return []
    (cx, cy), deg, (bw, bh, bt) = L.CARTON
    zc = top_at(cx, cy)
    fr = frame_z(cx, cy, deg, zc)
    ct = P("carton", "carton")
    parts = [ct]
    if lod == 0:
        open_box(ct, -bw / 2, bw / 2, -bh / 2, bh / 2, 0.0, bt, 0.0012, frame=fr)
        # lid on a hinge along the back edge, folded back by 100 degrees
        hinge = fr.p(0.0, bh / 2, bt)
        t = math.radians(100.0)
        ld = -fr.v * math.cos(t) + fr.n * math.sin(t)
        lid = g.Frame(hinge, fr.u, ld, fr.u.cross(ld))
        g.box(ct, -bw / 2, bw / 2, 0.0, bh, -0.0012, 0.0, frame=lid)
        cb = P("carton_band", "carton_band")
        for s in (-1, 1):
            g.box(cb, -0.05, 0.05, *sorted((s * bh / 2, s * (bh / 2 + 0.0006))), 0.0, bt, frame=fr)
        parts.append(cb)
    else:
        g.box(ct, -bw / 2, bw / 2, -bh / 2, bh / 2, 0.0, bt, frame=fr)
    pk = P("packs", "carton", section="cigs")
    pk.fixed_uv = True
    pk.bm.loops.layers.uv.new("UVMap")
    if lod == 0:
        # packs across the carton: the top row - except 2 and 4, where the lower ones show
        for k in range(5):
            u = -bw / 2 + 0.0012 + 0.0555 * (k + 0.5)
            low = k in (2, 4)
            f = g.Frame(fr.p(u, 0.0, 0.0012 + (0.0 if low else 0.022)), fr.v, -fr.u, fr.n)
            cig_pack(pk, f, skip=("bottom",) + (("sides", "ends") if low else ()))
    for i, ((px, py), pdeg) in enumerate(L.PACKS):
        f = frame_z(px, py, pdeg, top_at(px, py))
        cig_pack(pk, f)
        if i == 0 and lod == 0:
            fl = P("pack_filters", "filter")
            for j, (dy, out_) in enumerate(((-0.012, 0.016), (0.0, 0.010), (0.013, 0.006))):
                lathe(fl, [(0.0039, 0.0), (0.0039, out_ + 0.002)], 8, center=f.p(0.044 - 0.002, dy, 0.011), axis=f.u,
                      cap1=True)
            parts.append(fl)
    parts.append(pk)
    return parts


def build_notebook_deck(spec):
    """Exercise book in an oilcloth cover (covers with rounded corners, page block, spine) and a deck of
    cards (white edges, back on top)."""
    lod = spec["lod"]
    if lod == 2:
        return []
    (cx, cy), deg, (w, h, t) = L.NOTEBOOK
    fr = frame_z(cx, cy, deg, top_at(cx, cy))
    nb = P("notebook", "notebook")
    parts = [nb]
    if lod == 0:
        cover = rounded_rect(w, h, 0.004, 2)
        plate(nb, cover, 0.0, 0.0016, fr)
        plate(nb, cover, t - 0.0016, t, fr)
        g.box(nb, -w / 2, -w / 2 + 0.004, -h / 2 + 0.002, h / 2 - 0.002, 0.0016, t - 0.0016, frame=fr)
        pg = P("notebook_pages", "pages")
        g.box(pg, -w / 2 + 0.002, w / 2 - 0.0025, -h / 2 + 0.0025, h / 2 - 0.0025, 0.0016, t - 0.0016, frame=fr)
        parts.append(pg)
    else:
        g.box(nb, -w / 2, w / 2, -h / 2, h / 2, 0.0, t, frame=fr)
    (cx, cy), deg, (w, h, t) = L.DECK
    fr = frame_z(cx, cy, deg, top_at(cx, cy))
    dk = P("deck_edges", "pages")
    cards = rounded_rect(w, h, 0.003, 2 if lod == 0 else 1)
    plate(dk, cards, 0.0, t - 0.0005, fr)
    tp = P("deck", "deck")
    plate(tp, cards, t - 0.0005, t, fr)
    parts += [dk, tp]
    return parts


# =============================================================================
# Under the table
# =============================================================================
def build_floor(spec):
    """Cardboard box with open flaps: a heap of rags and a coil of wire inside, one end hangs out."""
    lod = spec["lod"]
    if lod == 2:
        return []
    x0, x1, y0, y1, h = FBOX
    fb = P("box_floor", "card")
    parts = [fb]
    if lod > 0:
        g.box(fb, x0, x1, y0, y1, 0.0, h)
        return parts
    open_box(fb, x0, x1, y0, y1, 0.0, h, 0.004)
    # flaps: hinged on the top edges, opened outward at different angles
    for (a, b), (o, du, dv), ang in ((((x0, x1)), ((x0, y0, h), (1, 0, 0), (0, -1, 0)), 120.0),
                                     (((x0, x1)), ((x0, y1, h), (1, 0, 0), (0, 1, 0)), 95.0),
                                     (((y0, y1)), ((x0, y0, h), (0, 1, 0), (-1, 0, 0)), 60.0),
                                     (((y0, y1)), ((x1, y0, h), (0, 1, 0), (1, 0, 0)), 80.0)):
        t = math.radians(ang)
        u, v0 = Vector(du), Vector(dv)
        vv = v0 * math.sin(t) + Vector((0, 0, 1)) * math.cos(t)
        nn = u.cross(vv)
        if nn.z < 0:
            nn = -nn
        L_ = (y1 - y0) / 2 if du[0] else (x1 - x0) / 2
        fr = g.Frame(Vector(o), u, vv, nn)
        g.box(fb, 0.0, b - a, 0.0, L_ * 0.9, -0.002, 0.002, frame=fr)
    jk = P("box_junk", "junk")
    g.box(jk, x0 + 0.006, x1 - 0.006, y0 + 0.006, y1 - 0.006, 0.004, h - 0.05)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2

    def bump(s, q):
        d = math.hypot(s - 0.45, q - 0.55)
        return 0.07 * max(0.0, 1.0 - d / 0.55) ** 1.5 + 0.008 * math.sin(s * 11.0) * math.cos(q * 9.0)
    sheet(jk, g.Frame(Vector((cx, cy, h - 0.05)), Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))),
          x1 - x0 - 0.014, y1 - y0 - 0.014, 0.004, bump, ss=[k / 6 for k in range(7)], qs=[k / 6 for k in range(7)])
    parts.append(jk)
    cb = P("box_cable", "black")
    zc = h - 0.020
    for k in range(2):
        ring(cb, (cx + 0.05 + 0.005 * k, cy - 0.04 + 0.004 * k, zc + 0.0055 * k), (0.15, 0.1, 1.0), 0.045, 0.0028, 12, 4)
    cable(cb, [(cx + 0.05 + 0.045, cy - 0.04, zc + 0.011), (cx + 0.02, cy - 0.10, zc + 0.006), (cx - 0.04, cy - 0.11, zc)],
          0.0028, 5)
    parts.append(cb)
    return parts


def build_lod(spec):
    parts = build_bench(spec) + build_lamp(spec) + build_slot2(spec) + build_board(spec) + build_shelf(spec)
    parts += R.build_recorder(P, spec, SEL)
    parts += build_papers(spec) + build_bolts(spec) + build_pdas(spec) + build_flash(spec) + build_pager(spec)
    parts += build_knife(spec) + build_keys(spec) + build_ashtray_mug(spec) + build_cigs(spec)
    parts += build_notebook_deck(spec) + build_floor(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        check_places()
    return parts


def check_places():
    """Vanilla items must not enter the module places or each other (extents kv.corners, in plan) - printed
    to the log, near LOD only."""
    boxes = []
    for d in DECOR:
        cs = kv.corners(d[5], d[1], d[2], d[3])
        boxes.append((d[5].split("\\")[-1], tuple(min(c[i] for c in cs) for i in range(3)),
                      tuple(max(c[i] for c in cs) for i in range(3))))
    for i, ((mx, my, mz), ((a0, b0), (a1, b1))) in enumerate(zip(L.MODS, L.MOD_BOX)):
        boxes.append(("module%d" % (i + 1), (mx + a0, my + b0, mz), (mx + a1, my + b1, mz + 0.25)))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            (na, la, ha), (nb, lb, hb) = boxes[i], boxes[j]
            if all(la[k] < hb[k] - 0.001 and lb[k] < ha[k] - 0.001 for k in range(3)):
                print("place check: %s overlaps %s" % (na, nb))
    for nm, lo, hi in boxes:
        print("place: %-22s x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f" % (nm, lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))


def collision():
    metal = kx.PEN + r"\metalplate.rvmat"
    table = kx.box_pts(X0 - 0.03, X1 + 0.01, Y0 - 0.03, Y1 + 0.005, 0.0, ZT)
    # a component thinner than 0.5 m does not work: the upper block goes down into the table and forward over the
    # board - the parts overlap, each one is convex
    top = kx.box_pts(X0 - 0.03, X1, Y1 - 0.51, Y1, 0.40, ZP + 0.10)
    comps = [(table, metal), (top, metal)]
    memory = {
        "invView": [(-0.2, -2.6, 1.3)],
        "ce_center": [(0.0, 0.0, ZP / 2)],
        "ce_radius": [(1.1, 0.0, ZP / 2)],
        "ozl_reel_l_axis": [tuple(p) for p in R.reel_axis(0)],
        "ozl_reel_r_axis": [tuple(p) for p in R.reel_axis(1)],
        "ozl_needle_axis": [tuple(p) for p in R.needle_axis()],
        "ozl_keys_axis": [tuple(p) for p in R.keys_axis()],
    }
    for i, m in enumerate(L.MODS):
        memory["module_%d" % (i + 1)] = [m]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2] + 0.004)
    return comps, 140.0, memory, bbox


# the first ones are for the --look preview: overview, the table with the modules (also empty), the shelf
# with the tape recorder and the radio scanner, the pager and small things on the right (the first four for
# the "work" look), the back panel with the map, papers and PDAs on the left, the sketch with bolts
SHOTS = [
    ("front", (-1.0, -2.4, 1.75), (0.0, 0.0, 1.0), 32),
    ("desk", (-0.05, -1.32, 1.72), (-0.05, 0.04, 1.02), 30),
    ("shelf", (0.26, -0.40, 1.92), (0.28, 0.20, 1.44), 34),
    ("pager", (0.52, -0.66, 1.18), (0.45, -0.02, 0.80), 36),
    ("map", (0.0, -1.1, 1.20), (-0.05, 0.30, 1.03), 32),
    ("papers", (-0.58, -0.78, 1.22), (-0.48, -0.02, 0.80), 36),
    ("sketch", (-0.06, -0.70, 1.28), (-0.05, -0.06, 0.80), 36),
    ("right", (0.95, -1.0, 1.45), (0.45, 0.0, 0.85), 34),
    ("under", (-0.6, -1.5, 0.75), (-0.35, 0.0, 0.20), 32),
    ("back", (1.4, 1.9, 1.6), (0.0, 0.0, 0.9), 32),
]

M.look_shots = (7, 4)
M.run(build_lod, collision, SHOTS, row_step=1.9, row_shot=((1.9, -6.2, 2.0), (1.9, 0, 0.80)))
