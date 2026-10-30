"""M22 - bar counter: Terminal of the Neutrals (OZL_Lnr_Terminal). Research result carriers are handed in
here and the research tree is opened; no modules (a terminal).

    blender --background --python build_m22.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (digits on the register keys, the
register display - idle and the "working" frames, the radio scale in two versions, the speaker
grille, stains on the countertop). The layout is in layout.py (shared with make_decals.py), the own
geometry in m22_geo.py.

Detail: the "dayz" look (matte, dirtier, colored AO). The counter boards have chamfers, differ in
width and sit on forged nails; the front sheet is corrugated galvanized steel with the vanilla DayZ
sheet texture (dz\\structures\\data\\metal_plate_wave_co.paa by path, section wave; the geometry waves
match the drawn ones: 30 waves of 76.2 mm per tile), on self-tapping screws with washers; the footrail
is a pipe with domes at the ends on three brackets with clamps; the countertop has mug rings, burns
and cuts. The "Oka" register: a case with rounded edges, a keyboard well with raised keys (digits and
signs on them), a receipt window with a roll and tape, the cashier and customer displays (own
texture, frames), a crank, a nameplate without lettering, a cash drawer with cells, coins and
coupons inside the case. VEF-202: a rounded case, a silver panel, a scale under glass in a frame
(the needle is a separate part), knurled knobs, band keys, a knob, a five-section telescopic antenna.
Dishes and containers are smooth solids of revolution (beer bottles with crown caps, port wine,
three-liter jars with contents, seamed tin cans), faceted mugs and glasses with real facets. The
small stuff is vanilla DayZ items as proxies (kvanilla): vodka (on the counter and three on the
shelf), "Veterok", "Tuna", honey, jam, a lantern, rags, a sheet of paper with a pen, matches, open
sardines; the "Chernomorka" pack is its own box with a vanilla texture (as in M16, M13).

The prop is a homemade bar counter of boards and iron. There is no "100 roentgen" sign and no
lettering: the name comes from the game strings. Size: 2.2 x 1.1 x 0.7 m (a bar counter is usually
1.05-1.15 m high; a homemade piece has no datasheet). Top 2.20 x 0.68, boards 45 mm; frame
2.16 x 0.62, the cladding face is 6 cm deeper than the edge of the top, in front of it a footrail of
dia. 42 pipe at 0.20 m.
Prop references:
- "Oka" register (made in Kursk / Ryazan, 1970-80s; there is no datasheet online, only cash register
  registries): a 9-row keyboard at a pitch of ~19 mm and seven-segment digits behind dark glass (from
  photos), hence 340 x 380 x 330 mm with the cash drawer;
- VEF-202 radio (Riga, 1971-1980): 305 x 240 x 105 mm;
- 0.5 l beer bottle: height 245 mm, O ~70 (GOST 10117-91, type IV); the 0.7 l port bottle is
  estimated from the same; crown cap dia. 32 (neck 26 mm); the labels are blank, without text;
- 0.5 l faceted beer mug: height ~155 mm (a ceramic 0.5 l mug is 155 mm, a glass one 160 mm), O 84
  across the facets - by eye;
- 250 ml faceted glass: height ~90, O ~72 (commonly known sizes, unverified);
- 3 l jar: O ~150, height ~245; stewed meat can O 100 x 65, condensed milk O 76 x 78 (unverified);
- corrugated sheet: wave 76.2 mm (3 inches), wave height 16 mm - by eye from photos.

Working look: the radio scale is ozl_screen (_on atlas: backlight), the register display is
ozl_screen_2 (own texture, section disp: two windows, the customer's and the cashier's; "working" -
frames _disp_fNN, OZL_WorkFx frames: a sum is typed in, then the total), the register lamp is
ozl_lamp (blinks); the scale needle is the bone ozl_needle (source ozl_needle, wobble: it sweeps the
scale, "looking for a station"), the tuning knob turns with it - the bone ozl_knob; the cash drawer
is the bone ozl_drawer (source ozl_drawer, pose: it slides out toward the bartender by 12 cm while
working, then back).

Glass (mugs, glasses, three-liter jars, the receipt window, the scale glass) is the glass section
(_ca + glass rvmat, as in M01/M02); beer and port bottles are dark - atlas. On the mid LOD bottles
and jars are simple prisms, on the far LOD one mass per shelf.

Blender axes: X is width, Y is depth (the face, the player's side, is at -Y), Z is up.
"""
import math
import os
import random
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
import m22_geo as G  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
X0, X1 = -1.10, 1.10                                        # countertop
XC = 1.08                                                   # frame outside (sides 1.06..1.08)
XS = 1.06                                                   # inner face of the side boards
XP = 1.00                                                   # inner face of the corner posts
YT0, YT1 = -0.33, 0.35                                      # countertop
YF, YFB = -0.27, -0.25                                      # cladding face, its back
YK = -0.244                                                 # back of the lining (inside the spans)
YB = 0.35                                                   # rear posts
ZT = L.ZT                                                   # 1.10
ZU = ZT - 0.045                                             # underside of the countertop boards
ZS0, ZS1 = 0.10, 0.48                                       # corrugated sheet
ZR0, ZR1 = 0.47, 0.51                                       # strip above the sheet
ZTR = 1.00                                                  # top strip of the face
DIVX = (-0.37, 0.37)                                        # partitions (center), 20 mm
SH = (0.10, 0.46, 0.80)                                     # top of the shelves
TS = 0.02
SY0, SY1 = YK, 0.33                                         # shelf depth
BAYS = ((-XP, DIVX[0] - 0.01), (DIVX[0] + 0.01, DIVX[1] - 0.01), (DIVX[1] + 0.01, XP))
RAIL_Y, RAIL_Z, RAIL_R = -0.315, 0.20, 0.021                # footrail
RAIL_X = 0.95
# corrugated sheet: wave 76.2 mm, height 16 mm; the vanilla texture has 30 waves per tile (2.286 m), the
# crest in the image is at 0.797 of a wave (measured by brightness)
WAVE, WAVE_AMP = 0.0762, 0.016
WAVE_TILE, WAVE_CREST = 30 * WAVE, 0.797
WAVE_TEX = (r"dz\structures\data\metal_plate_wave_co.paa",
            r"dz\structures\residential\houses\data\housev2_03b_metal_plates.rvmat")
CIGS = (r"dz\gear\medical\data\pack_of_cigs_cherno_co.paa", r"dz\gear\medical\data\pack_of_cigs.rvmat")
CIGS_UV = {"front": (0.117, 0.462, 0.43, 1.0), "side": (0.885, 0.970, 0.60, 1.0), "end": (0.26, 0.45, 0.20, 0.30)}
PACK = (0.088, 0.055, 0.022)
PACK_AT = (0.80, -0.115, 24.0)                              # pack by the ashtray: center, rotation
KNOB_T = (L.QX + 0.100, L.QY - 0.020)                       # radio tuning knob
KNOB_TURN = 3 * 2 * math.pi                                 # three turns over the whole needle travel

LOD_SPECS = [
    dict(lod=0, sides=12),
    dict(lod=1, sides=6),
    dict(lod=2, sides=4),
]

REGIONS = {
    # counter
    "top": ("top", 0.6), "plank": ("plank", 0.5), "plank_b": ("plank_b", 0.5), "plank_c": ("plank_c", 0.5),
    "plank_new": ("plank_new", 0.5), "rail_w": ("rail_w", 0.5),
    "side": ("side", 0.4), "side_b": ("side_b", 0.4), "shelf": ("shelf", 0.4), "post": ("post", 0.4),
    "plinth": ("plinth", 0.4),
    "backing": ("backing", 0.25), "tin": ("tin", 1.0), "tin_patch": ("tin_patch", 1.0),
    "nail": ("nail", 2.0), "screw": ("screw", 2.0), "footrail": ("footrail", 1.0), "bracket": ("bracket", 1.5),
    "wave": ("tin", 1.0),
    # register
    "reg": ("reg", 2.0), "reg_base": ("reg_base", 1.5), "reg_inner": ("reg_inner", 0.5), "reg_well": ("reg_well", 2.5),
    "reg_tray": ("reg_tray", 0.8), "bezel": ("bezel", 3.0), "plate": ("plate", 3.0), "lamp": ("lamp", 4.0),
    "key_black": ("key_black", 4.0), "key_cream": ("key_cream", 4.0), "key_orange": ("key_orange", 3.0),
    "key_blue": ("key_blue", 3.0), "key_teal": ("key_teal", 3.0), "key_red": ("key_red", 3.0),
    "black": ("black", 2.0), "chrome": ("chrome", 2.0), "rubber": ("rubber", 1.0), "paper": ("paper", 2.0),
    "coin": ("coin", 3.0), "bill_a": ("bill_a", 1.5), "bill_b": ("bill_b", 1.5), "grip": ("grip", 2.0),
    "disp": ("black", 1.0),
    # tray, radio
    "tray": ("tray", 1.2),
    "radio": ("radio", 1.5), "radio_front": ("radio_front", 3.0), "scale": ("scale", 5.0), "knob": ("knob", 3.0),
    "needle": ("needle", 3.0), "mark": ("mark", 3.0), "mount": ("black", 2.0),
    # containers, dishes
    "glass": ("steel", 1.0), "bottle_brown": ("bottle_brown", 0.8), "bottle_port": ("bottle_port", 0.8),
    "label_a": ("label_a", 3.0), "label_b": ("label_b", 3.0), "label_n": ("label_n", 3.0),
    "crown": ("crown", 2.0), "cork": ("cork", 2.0), "beer": ("beer", 1.0), "foam": ("foam", 1.0),
    "tomato": ("tomato", 0.6), "compote": ("compote", 0.6), "cabbage": ("cabbage", 0.6),
    "lid": ("lid", 1.5), "can": ("can", 1.0), "label_milk": ("label_milk", 2.0), "label_meat": ("label_meat", 2.0),
    "carton": ("carton", 0.5), "tape": ("tape", 1.0), "crate": ("crate", 0.6), "crate_end": ("crate_end", 0.6),
    "ashtray": ("ashtray", 2.0), "ash": ("ash", 2.0), "butt": ("butt", 3.0), "butt_paper": ("butt_paper", 3.0),
}


# =============================================================================
# Materials
# =============================================================================
def decal(name, ax, sign, uv, center, size, rng=None):
    return (os.path.join(WORK, name), ax, sign, uv, center, size, rng)


lin = kmats.lin
KINDS = kmats.std_kinds(floor_z=0.0)
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# dark brown wood of the Neutrals (no green): old varnish, rubbed by hands, dirtier near the floor
WOOD = dict(color=lin((72, 44, 28)), seed=1.3, gloss=0.25, spec=0.16, floor_z=0.0, dust=0.3, grime=0.8,
            rings=0.55, knots=0.4)
GALV = dict(under=lin((112, 62, 30)), gloss=0.45, spec=0.55, floor_z=0.0)
TOP_DECAL = decal("decal_top.png", "z", 1, ("x", "y"), L.TOP_C, L.TOP_S, (ZT - 0.006, ZT + 0.004))
KEYS_DECAL = decal("decal_keys.png", "z", 1, ("x", "y"), L.KEYS_C, L.KEYS_S, L.KEYS_RNG)
SCALE_RNG = (L.SCALE_Y - 0.001, L.SCALE_Y + 0.001)


def key_kind(rgb, grime=0.35):
    """Key: plastic with a digit (decal); the paint builder, since plastic in the kit has no decals;
    chips are rare, down to a darker tone, no rust."""
    return ("paint", dict(color=lin(rgb), under=tuple(c * 0.55 for c in lin(rgb)[:3]) + (1.0,), seed=6.7 + rgb[0] / 100,
                          gloss=0.45, spec=0.3, chip=(0.80, 0.86), rust=(0.99, 1.0), rust_low=0.0, floor_z=ZT,
                          dust=0.08, grime=grime, decal_items=[KEYS_DECAL]))


KINDS.update({
    # countertop: the varnish is worn by elbows in the middle - lighter and matter; mug rings, burns, cuts
    "top": (kwood.build_wood, dict(WOOD, color=lin((84, 52, 32)), seed=2.1, along="x", gloss=0.32, spec=0.2,
                                   dust=0.05, grime=0.5, decal_items=[TOP_DECAL])),
    # the face and sides are made of different boards: each has its own tone, varnish and dirt
    "plank": (kwood.build_wood, dict(WOOD, along="z", grime=1.0, dust=0.4)),
    "plank_b": (kwood.build_wood, dict(WOOD, color=lin((86, 52, 32)), seed=11.7, along="z", gloss=0.2, grime=1.0,
                                       dust=0.4, knots=0.6)),
    "plank_c": (kwood.build_wood, dict(WOOD, color=lin((62, 44, 32)), seed=12.9, along="z", gloss=0.12, spec=0.1,
                                       grime=1.1, dust=0.5, rings=0.7)),
    # new board in place of a broken one: light, unvarnished
    "plank_new": (kwood.build_wood, dict(WOOD, color=lin((118, 86, 56)), seed=6.3, along="z", gloss=0.1,
                                         spec=0.06, rings=0.5, knots=0.6, grime=0.5)),
    "rail_w": (kwood.build_wood, dict(WOOD, color=lin((64, 40, 26)), seed=3.4, along="x")),
    "side": (kwood.build_wood, dict(WOOD, seed=4.2, along="z", grime=1.0, dust=0.4)),
    "side_b": (kwood.build_wood, dict(WOOD, color=lin((64, 42, 30)), seed=13.3, along="z", gloss=0.14, grime=1.1,
                                      dust=0.5, rings=0.7)),
    "shelf": (kwood.build_wood, dict(WOOD, color=lin((80, 54, 36)), seed=5.1, along="x", gloss=0.15,
                                     dust=0.45, grime=0.4)),
    "post": (kwood.build_wood, dict(WOOD, color=lin((62, 40, 26)), seed=7.2, along="z")),
    "plinth": (kwood.build_wood, dict(WOOD, color=lin((46, 32, 22)), seed=8.0, along="x", grime=1.0)),
    # lining from inside: dark untreated boards
    "backing": (kwood.build_wood, dict(WOOD, color=lin((48, 34, 24)), seed=9.3, along="z", gloss=0.08,
                                       spec=0.05, rings=0.3, knots=0.2, dust=0.4)),
    "tin": ("paint", dict(GALV, color=lin((132, 132, 126)), seed=3.3, chip=(0.56, 0.63), rust=(0.58, 0.66),
                          rust_low=0.0, dust=0.15, grime=0.7)),
    # patches are old tin: dark, rusty at the edges and nails
    "tin_patch": ("paint", dict(GALV, color=lin((96, 94, 88)), seed=4.9, chip=(0.47, 0.55),
                                rust=(0.48, 0.56), rust_low=0.0, dust=0.25, grime=0.9)),
    # forged nails - rusty heads; sheet screws - galvanized, with a rubber washer
    "nail": ("paint", dict(color=lin((58, 52, 46)), under=lin((112, 62, 30)), seed=3.9, gloss=0.3, spec=0.3,
                           chip=(0.45, 0.55), rust=(0.40, 0.50), rust_low=0.0, floor_z=0.0, dust=0.1, grime=0.5)),
    "screw": ("steel", dict(seed=4.4, tone=0.34, along="z", gloss=0.45, spec=0.55, floor_z=0.0, dust=0.2, grime=0.5)),
    # footrail: steel pipe, the paint worn down to metal by boots
    "footrail": ("paint", dict(color=lin((52, 40, 32)), under=lin((150, 150, 146)), seed=5.7, gloss=0.45,
                               spec=0.5, chip=(0.44, 0.52), rust=(0.60, 0.68), rust_low=0.6, floor_z=0.0, dust=0.1,
                               grime=0.4)),
    "bracket": ("paint", dict(color=lin((40, 36, 32)), under=lin((120, 118, 112)), seed=5.9, gloss=0.35, spec=0.3,
                              chip=(0.50, 0.58), rust=(0.48, 0.58), rust_low=0.8, floor_z=0.0, dust=0.15, grime=0.6)),
    # "Oka" register: light gray enamel, yellowed by tobacco smoke, chips down to the dark primer, rusty
    # spots; the base is darker
    "reg": ("paint", dict(color=lin((168, 170, 160)), under=lin((52, 50, 48)), seed=6.1, gloss=0.45, spec=0.38,
                          chip=(0.55, 0.61), rust=(0.57, 0.65), rust_low=0.0, floor_z=ZT, dust=0.3, grime=0.65,
                          yellow=0.35)),
    "reg_base": ("paint", dict(color=lin((128, 130, 124)), under=lin((60, 58, 56)), seed=6.6, gloss=0.42, spec=0.38,
                               chip=(0.53, 0.60), rust=(0.55, 0.63), rust_low=0.0, floor_z=ZT, dust=0.25, grime=0.75)),
    "reg_inner": ("flat", dict(color=lin((34, 33, 31)), gloss=0.15, spec=0.1)),
    "reg_well": ("paint", dict(color=lin((44, 44, 46)), under=lin((120, 120, 118)), seed=6.4, gloss=0.35, spec=0.3,
                               chip=(0.62, 0.70), rust=(0.70, 0.80), rust_low=0.0, floor_z=ZT, dust=0.35, grime=0.6)),
    "reg_tray": ("paint", dict(color=lin((112, 114, 110)), under=lin((60, 58, 56)), seed=6.9, gloss=0.35, spec=0.3,
                               chip=(0.58, 0.66), rust=(0.62, 0.70), rust_low=0.0, floor_z=ZT, dust=0.1, grime=0.5)),
    "bezel": ("steel", dict(seed=7.0, tone=0.50, along="x", gloss=0.6, spec=0.7, floor_z=ZT, dust=0.2, grime=0.35)),
    "plate": ("steel", dict(seed=7.3, tone=0.56, along="x", gloss=0.65, spec=0.75, floor_z=ZT, dust=0.15, grime=0.3)),
    # register lamp: off - dark red glass, "working" - lit
    "lamp": ("flat", dict(color=lin((86, 22, 16)), gloss=0.85, spec=0.8)),
    "lamp_on": ("flat", dict(color=lin((255, 70, 40)), gloss=0.85, spec=0.8)),
    "key_black": key_kind((26, 26, 26)),
    "key_cream": key_kind((222, 210, 166), grime=0.5),
    "key_orange": key_kind((214, 104, 34)),
    "key_blue": key_kind((50, 104, 180)),
    "key_teal": key_kind((70, 116, 112)),
    "key_red": key_kind((182, 38, 32)),
    "chrome": ("steel", dict(seed=7.7, tone=0.62, along="x", gloss=0.8, spec=0.9, dust=0.2, grime=0.2)),
    "paper": ("plastic", dict(color=lin((222, 216, 198)), gloss=0.1, spec=0.05, mottle=0.08, dust=0.1, grime=0.25)),
    "coin": ("paint", dict(CLEAN, color=lin((204, 184, 124)), gloss=0.6, spec=0.6)),
    "bill_a": ("plastic", dict(color=lin((140, 160, 120)), gloss=0.1, spec=0.05, mottle=0.2, dust=0.1, grime=0.3)),
    "bill_b": ("plastic", dict(color=lin((190, 146, 118)), gloss=0.1, spec=0.05, mottle=0.2, dust=0.1, grime=0.3)),
    "grip": ("plastic", dict(color=lin((34, 28, 24)), gloss=0.45, spec=0.3, dust=0.1, grime=0.3, scuff=(0.6, 0.7))),
    "tray": ("paint", dict(GALV, color=lin((116, 118, 112)), seed=8.8, chip=(0.50, 0.57), rust=(0.55, 0.63),
                           rust_low=0.0, dust=0.15, grime=0.85)),
    # VEF-202: a black leatherette case, a silver panel with a grille, the scale under glass
    "radio": ("plastic", dict(color=lin((30, 29, 28)), gloss=0.3, spec=0.2, dust=0.35, grime=0.3, mottle=0.14,
                              scuff=(0.58, 0.66))),
    "radio_front": ("paint", dict(CLEAN, color=lin((170, 172, 170)), gloss=0.5, spec=0.5, dust=0.2,
                                  grime=0.2, decal_items=[
                                      decal("decal_grille.png", "y", -1, ("x", "z"), L.GRILLE_C, L.GRILLE_S,
                                            (L.Q_PANEL - 0.002, L.Q_PANEL + 0.001))])),
    "scale": ("paint", dict(CLEAN, color=lin((104, 98, 84)), gloss=0.85, spec=0.6, decal_items=[
        decal("decal_scale_off.png", "y", -1, ("x", "z"), L.SCALE_C, L.SCALE_S, SCALE_RNG)])),
    "scale_on": ("paint", dict(CLEAN, color=lin((250, 222, 150)), gloss=0.85, spec=0.6, decal_items=[
        decal("decal_scale_on.png", "y", -1, ("x", "z"), L.SCALE_C, L.SCALE_S, SCALE_RNG)])),
    "knob": ("plastic", dict(color=lin((24, 24, 24)), gloss=0.45, spec=0.3, dust=0.25, grime=0.3)),
    "needle": ("flat", dict(color=lin((196, 34, 24)), gloss=0.5, spec=0.4)),
    "mark": ("flat", dict(color=lin((226, 222, 210)), gloss=0.4, spec=0.3)),
    # containers: dark bottle glass (opaque in the atlas), blank labels, caps
    "bottle_brown": ("flat", dict(color=lin((58, 30, 12)), gloss=0.92, spec=0.85)),
    "bottle_port": ("flat", dict(color=lin((40, 20, 18)), gloss=0.92, spec=0.85)),
    # labels are a flat color: wear would make stripes along the edges on a narrow strip
    "label_a": ("flat", dict(color=lin((206, 190, 150)), gloss=0.1, spec=0.05)),
    "label_b": ("flat", dict(color=lin((176, 72, 46)), gloss=0.12, spec=0.05)),
    "label_n": ("flat", dict(color=lin((190, 160, 84)), gloss=0.15, spec=0.08)),
    "crown": ("paint", dict(color=lin((176, 150, 86)), under=lin((150, 150, 146)), seed=8.1, gloss=0.55,
                            spec=0.5, chip=(0.58, 0.64), rust=(0.66, 0.74), rust_low=0.0, floor_z=0.0, dust=0.2,
                            grime=0.3)),
    "cork": ("plastic", dict(color=lin((176, 146, 100)), gloss=0.2, spec=0.1, mottle=0.2)),
    "beer": ("flat", dict(color=lin((176, 104, 22)), gloss=0.9, spec=0.6)),
    "foam": ("plastic", dict(color=lin((236, 226, 200)), gloss=0.3, spec=0.2, mottle=0.1, dust=0.0, grime=0.0)),
    "tomato": ("plastic", dict(color=lin((170, 56, 30)), gloss=0.7, spec=0.5, mottle=0.35, dust=0.0)),
    "compote": ("flat", dict(color=lin((96, 22, 28)), gloss=0.9, spec=0.6)),
    "cabbage": ("plastic", dict(color=lin((206, 192, 128)), gloss=0.5, spec=0.3, mottle=0.3, dust=0.0)),
    "lid": ("paint", dict(color=lin((176, 150, 86)), under=lin((150, 150, 146)), seed=8.1, gloss=0.55,
                          spec=0.5, chip=(0.58, 0.64), rust=(0.66, 0.74), rust_low=0.0, floor_z=0.0, dust=0.25,
                          grime=0.3)),
    "can": ("steel", dict(seed=9.1, tone=0.52, along="z", gloss=0.6, spec=0.75, dust=0.3, grime=0.3)),
    # condensed milk - a white and blue paper label, stewed meat - a faded yellow one; no text
    "label_milk": ("plastic", dict(color=lin((70, 110, 176)), gloss=0.15, spec=0.08, mottle=0.12, dust=0.3)),
    "label_meat": ("plastic", dict(color=lin((204, 178, 110)), gloss=0.12, spec=0.06, mottle=0.18, dust=0.3,
                                   scuff=(0.56, 0.66))),
    "carton": ("plastic", dict(color=lin((150, 112, 72)), gloss=0.08, spec=0.05, mottle=0.18, dust=0.5,
                               grime=0.5, scuff=(0.60, 0.70))),
    "tape": ("plastic", dict(color=lin((178, 146, 96)), gloss=0.5, spec=0.3, mottle=0.1, dust=0.3)),
    # beer crate: gray unpainted slats, darker ends
    "crate": (kwood.build_wood, dict(color=lin((124, 104, 80)), seed=10.2, along="x", gloss=0.08, spec=0.05,
                                     floor_z=0.0, dust=0.4, grime=0.6, rings=0.4, knots=0.5)),
    "crate_end": (kwood.build_wood, dict(color=lin((104, 86, 66)), seed=10.7, along="y", gloss=0.08, spec=0.05,
                                         floor_z=0.0, dust=0.4, grime=0.7, rings=0.4, knots=0.5)),
    "ashtray": ("paint", dict(color=lin((116, 118, 116)), under=lin((60, 58, 56)), seed=9.9, gloss=0.4,
                              spec=0.45, chip=(0.56, 0.64), rust=(0.70, 0.80), rust_low=0.0, floor_z=ZT, dust=0.0,
                              grime=0.7)),
    "ash": ("plastic", dict(color=lin((112, 110, 106)), gloss=0.05, spec=0.03, mottle=0.4, dust=0.0, grime=0.0)),
    "butt": ("plastic", dict(color=lin((206, 160, 96)), gloss=0.1, spec=0.05, mottle=0.15, dust=0.0)),
    "butt_paper": ("plastic", dict(color=lin((214, 208, 192)), gloss=0.1, spec=0.05, mottle=0.2, dust=0.0, grime=0.4)),
})

OBJ, NAME = "m22_lnr_terminal", "ozr_lnr_terminal"
# Working look: the scale is ozl_screen (_on atlas), the register display is ozl_screen_2 (own texture,
# frames), the lamp is ozl_lamp (_on atlas, blinks); bones: the needle, the tuning knob, the cash drawer.
SEL_SCREEN, SEL_DISP, SEL_LAMP = "ozl_screen", "ozl_screen_2", "ozl_lamp"
SEL_NEEDLE, SEL_KNOB, SEL_DRAWER = "ozl_needle", "ozl_knob", "ozl_drawer"
# "working" preview: the needle is mid-travel, the drawer is out (does not go into the p3d - model.cfg does that)
ON = dict(remap={"scale": "scale_on", "lamp": "lamp_on"}, emissive=(1.0, 1.0, 1.0, 1.0),
          move={SEL_NEEDLE: (L.NEEDLE_TRAVEL * 0.45, 0.0, 0.0), SEL_DRAWER: (0.0, L.DRAWER_TRAVEL, 0.0)})
DISP = dict(off="decal_disp_off.png", frames=["decal_disp_f%02d.png" % i for i in range(len(L.DISP_FRAMES))],
            size=256, gloss=0.8)
# axes - one meter from the point: offset in meters
NEEDLE_ANIM = ("ozl_needle_move", dict(type="translation", source="ozl_needle", selection=SEL_NEEDLE,
                                       axis="ozl_needle_axis", memory=1, minValue=0.0, maxValue=1.0, offset0=0.0,
                                       offset1=L.NEEDLE_TRAVEL))
KNOB_ANIM = ("ozl_needle_knob", dict(type="rotation", source="ozl_needle", selection=SEL_KNOB, axis="ozl_knob_axis",
                                     memory=1, minValue=0.0, maxValue=1.0, angle0=0.0, angle1=KNOB_TURN))
DRAWER_ANIM = ("ozl_drawer_open", dict(type="translation", source="ozl_drawer", selection=SEL_DRAWER,
                                       axis="ozl_drawer_axis", memory=1, minValue=0.0, maxValue=1.0, offset0=0.0,
                                       offset1=L.DRAWER_TRAVEL))
# vanilla items: on the counter - vodka on a tin patch, rags, a sheet with a pen by the register,
# matches by the ashtray, open sardines by the mugs; on the shelves - vodka, "Veterok", "Tuna", honey, jam, a lantern
DECOR = [
    kv.put("vodka", (-0.92, 0.17, ZT + 0.0012), up=(0, 0, 1), fwd=(0.3, -1, 0)),
    kv.put("rags", (-0.36, 0.225, ZT), **kv.flat(8)),
    kv.put("paper", (0.72, 0.19, ZT), **kv.flat(96)),
    kv.put("pen", (0.745, 0.16, ZT + 0.0005), lods=(0,), **kv.flat(58)),
    kv.put("matchbox", (0.80, -0.255, ZT), lods=(0,), **kv.flat(-18)),
    kv.put(r"dz\gear\food\can_sardines_open", (-0.37, -0.205, ZT), lods=(0,), up=(0, 0, 1), fwd=(0.4, -1, 0)),
    kv.put("vodka", (-0.92, 0.245, SH[1]), up=(0, 0, 1), fwd=(0, 1, 0)),
    kv.put("vodka", (-0.835, 0.215, SH[1]), up=(0, 0, 1), fwd=(0.25, 1, 0)),
    kv.put("vodka", (-0.75, 0.25, SH[1]), up=(0, 0, 1), fwd=(-0.3, 1, 0)),
    kv.put(r"dz\gear\food\BakedBeans", (0.79, 0.245, SH[1]), up=(0, 0, 1), fwd=(0.2, 1, 0)),
    kv.put(r"dz\gear\food\Tuna", (0.915, 0.235, SH[1]), lods=(0,), up=(0, 0, 1), fwd=(0, 1, 0)),
    kv.put(r"dz\gear\food\Honey", (0.48, 0.235, SH[2]), up=(0, 0, 1), fwd=(0, 1, 0)),
    kv.put(r"dz\gear\food\Marmalade", (0.60, 0.245, SH[2]), up=(0, 0, 1), fwd=(0.3, 1, 0)),
    kv.put("flashlight", (0.775, 0.225, SH[2]), up=(0, 0, 1), fwd=(0, 1, 0)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.62, 0.66, 0.62), clear=0.10, edge=0.14, smudge=0.12, streaks=0.03),
                 selections=(SEL_SCREEN, SEL_DISP, SEL_LAMP, SEL_NEEDLE, SEL_KNOB, SEL_DRAWER),
                 hidden=(SEL_SCREEN, SEL_DISP, SEL_LAMP), states={"on": ON},
                 bones=((SEL_NEEDLE, ""), (SEL_KNOB, ""), (SEL_DRAWER, "")),
                 animations=(NEEDLE_ANIM, KNOB_ANIM, DRAWER_ANIM), decor=DECOR, panels={"disp": DISP},
                 vsections={"wave": WAVE_TEX, "cigs": CIGS},
                 sources={"ozl_needle": dict(animPeriod=0.2), "ozl_drawer": dict(animPeriod=0.6)})
P = M.part
BOUNDS = {}
FR_KB = g.Frame(L.KB_O, (1, 0, 0), L.KB_V, L.KB_N)          # sloped register panel
FR_CASH = g.Frame(L.KB_O, (-1, 0, 0), L.KB_V, L.KB_N)       # cashier window: u points to his right hand
FR_BACK = g.Frame((0.0, L.REG_YB, 0.0), (1, 0, 0), (0, 0, 1), (0, -1, 0))   # rear of the superstructure (toward the player)


def reg(part, name):
    """Index of one more region of the part (kind and scale come from REGIONS)."""
    return part.region_index(name, *REGIONS[name])


def use(part, name):
    return part.use(name, *REGIONS[name])


def bev(r, lod):
    return dict(r=r, seg=1) if lod == 0 else {}


# board systems: u along the width, v along the length, n outward (thickness from the back)
FR_FRONT = g.Frame((0.0, YFB, 0.0), (1, 0, 0), (0, 0, 1), (0, -1, 0))
FR_UP = g.Frame((0.0, 0.0, 0.0), (1, 0, 0), (0, 1, 0), (0, 0, 1))


def plank(part, fr, a0, a1, b0, b1, n0, n1, ch, back=False):
    """Board with a chamfer ch on the edges of the face (n1); the back (n0) has no face if it is not visible (back=False)."""
    G.slab(part, a0, a1, b0, b1, n0, n1, re=ch, ne=1, frame=fr, caps=(back, True))


# =============================================================================
# Counter
# =============================================================================
def build_top(spec):
    """Countertop: five boards along with chamfers and gaps, a dark panel under them; a tin edging of the
    front edge (bent onto the face and under the bottom, the bend is rounded), a patch on the left, forged nails."""
    lod = spec["lod"]
    tp = P("top", "top")
    if lod > 0:
        g.box(tp, X0, X1, YT0, YT1, ZU, ZT)
        if lod == 2:
            return [tp]
    else:
        rnd = random.Random(22)
        gap = 0.004
        w = (YT1 - YT0 - gap * 4) / 5
        for i in range(5):
            y0 = YT0 + i * (w + gap)
            dz = (0.0015 if i % 2 else 0.0) + rnd.uniform(0.0, 0.0008)
            plank(tp, FR_UP, X0 + rnd.uniform(0.0, 0.004), X1 - rnd.uniform(0.0, 0.004), y0, y0 + w, ZU, ZT - dz,
                  0.004, back=True)
        g.box(tp, X0 + 0.02, X1 - 0.02, YT0 + 0.02, YT1 - 0.02, ZU - 0.012, ZU + 0.002)       # panel under the boards
    parts = [tp]
    tn = P("top_band", "tin")
    g.box(tn, X0, X1, YT0 - 0.0025, YT0 - 0.0004, ZT - 0.032, ZT)
    g.box(tn, X0, X1, YT0 - 0.0004, YT0 + 0.018, ZT, ZT + 0.0012)
    if lod == 0:
        g.box(tn, X0, X1, YT0 - 0.0025, YT0 + 0.010, ZT - 0.0335, ZT - 0.0315)             # underside fold
        g.pipe(tn, [(X0, YT0 - 0.0012, ZT - 0.0002), (X1, YT0 - 0.0012, ZT - 0.0002)], 0.0017, 6)   # bend
    parts.append(tn)
    tpp = P("top_patch", "tin_patch")
    g.box(tpp, -1.02, -0.74, -0.06, 0.21, ZT, ZT + 0.0012, **bev(0.0005, lod))
    parts.append(tpp)
    if lod == 0:
        nl = P("top_nails", "nail")
        for x in (-1.02, -0.66, -0.30, 0.06, 0.42, 0.78, 1.04):
            G.nail(nl, (x, YT0 - 0.0025, ZT - 0.016), (0, -1, 0), sides=4)
        for x, y in ((-1.008, -0.048), (-0.752, -0.048), (-1.008, 0.198), (-0.752, 0.198), (-0.88, -0.048),
                     (-0.752, 0.075)):
            G.nail(nl, (x, y, ZT + 0.0012), (0, 0, 1), sides=4)
        parts.append(nl)
    return parts


def build_front(spec):
    """Face toward the player: baseboard, corrugated sheet (vanilla texture) on screws, a strip, boards on
    nails, the top strip, a tin patch; lining from inside."""
    lod = spec["lod"]
    parts = []
    pl = P("plinth", "plinth")
    g.box(pl, -XS, XS, YFB, YFB + 0.02, 0.0, ZS0, **bev(0.003, lod))
    parts.append(pl)
    bk = P("backing", "backing")
    g.box(bk, -XS, XS, YFB, YK, ZS0, ZU)
    parts.append(bk)
    if lod == 2:
        pk = P("front_planks", "plank")
        g.box(pk, -XS, XS, YF, YFB, ZS0, ZU)
        return parts + [pk]
    sh = P("sheet", "wave", section="wave")
    sh.fixed_uv = True
    crests = []
    if lod == 0:
        crests = G.corrugated_uv(sh, -XS, XS, ZS0, ZS1, YFB - 0.004, WAVE_AMP, WAVE, 6, WAVE_TILE, WAVE_CREST)
    else:
        G.box_uv(sh, -XS, XS, YF + 0.008, YFB, ZS0, ZS1, WAVE_TILE)
    parts.append(sh)
    rw = P("front_rails", "rail_w")
    if lod == 0:
        plank(rw, FR_FRONT, -XS, XS, ZR0, ZR1, 0.0, YFB - (YF - 0.008), 0.003)
        plank(rw, FR_FRONT, -XS, XS, ZTR, ZU, 0.0, YFB - (YF - 0.006), 0.003)
    else:
        g.box(rw, -XS, XS, YF - 0.008, YFB, ZR0, ZR1)
        g.box(rw, -XS, XS, YF - 0.006, YFB, ZTR, ZU)
    parts.append(rw)
    pk = P("front_planks", "plank")
    tp = P("front_patch", "tin_patch")
    if lod == 1:
        g.box(pk, -XS, XS, YF, YFB, ZR1, ZTR)
        g.box(tp, 0.55, 0.80, YF - 0.0035, YF, 0.60, 0.80)
        return parts + [pk, tp]
    rnd = random.Random(221)
    pn = P("front_plank_new", "plank_new")
    nl = P("front_nails", "nail")
    x, i = -XS, 0
    while x < XS - 0.02:
        w = min(rnd.uniform(0.11, 0.15), XS - x)
        if XS - (x + w) < 0.06:
            w = XS - x
        dy = rnd.uniform(-0.002, 0.002)
        if i != 9:
            use(pk, ("plank", "plank_b", "plank", "plank_c")[(i * 7 + 3) % 4 if i % 5 else 3])
        plank(pn if i == 9 else pk, FR_FRONT, x, x + w - 0.004, ZR1 + 0.001, ZTR - 0.001, 0.0, YFB - (YF + dy), 0.003)
        xc = x + (w - 0.004) / 2
        # a nail into the top strip (the lower ones are not visible under the footrail), slightly staggered
        G.nail(nl, (xc + rnd.uniform(-0.02, 0.02), YF + dy, ZTR - 0.022), (0, -1, 0), sides=4)
        x += w
        i += 1
    # tin patch over two boards on the right: edges bent, nails along the rim
    g.box(tp, 0.55, 0.80, YF - 0.0040, YF - 0.0022, 0.60, 0.80, r=0.0006, seg=1)
    for xx in (0.562, 0.675, 0.788):
        for zz in (0.612, 0.788):
            G.nail(nl, (xx, YF - 0.004, zz), (0, -1, 0), sides=4)
    # sheet screws - on the crests at the bottom and top, every five waves
    sc = P("sheet_screws", "screw")
    for k, (xc, yc) in enumerate(crests):
        if k % 5 == 1:
            for zz in (ZS0 + 0.028, ZS1 - 0.026):
                G.hexhead(sc, (xc, yc, zz), (0, -1, 0), r=0.0052, h=0.0028)
    parts += [pk, pn, tp, nl, sc]
    return parts


def build_sides(spec):
    """Sides: vertical boards with chamfers, lining and corner posts from inside."""
    lod = spec["lod"]
    sd = P("sides", "side")
    parts = [sd]
    for s in (-1, 1):
        xa, xb = sorted((s * XS, s * XC))
        if lod > 0:
            g.box(sd, xa, xb, YF, YB, 0.0, ZU)
            continue
        n, gap = 5, 0.004
        w = (YB - YF - gap * (n - 1)) / n
        fr = g.Frame((s * XS, 0.0, 0.0), (0, 1, 0), (0, 0, 1), (s, 0, 0))
        for i in range(n):
            y0 = YF + i * (w + gap)
            use(sd, "side_b" if (i + (s > 0)) % 3 == 1 else "side")
            plank(sd, fr, y0, y0 + w, 0.0, ZU - (0.0 if i % 3 else 0.004), 0.0, XC - XS - (0.0015 if i % 2 else 0.0),
                  0.003)
        g.box(sd, *sorted((s * (XS - 0.006), s * XS)), YF + 0.01, YB - 0.01, 0.0, ZU)       # lining
    ps = P("posts", "post")
    for s in (-1, 1):
        xa, xb = sorted((s * XP, s * XS))
        g.box(ps, xa, xb, YB - 0.06, YB, 0.0, ZU, **bev(0.003, lod))
        if lod < 2:
            g.box(ps, xa, xb, YK, YK + 0.06, ZS0, ZU)
    g.box(ps, -XP, XP, YB - 0.05, YB - 0.004, ZU - 0.07, ZU, **bev(0.003, lod))          # rail under the countertop
    g.box(ps, -XP, XP, YB - 0.05, YB - 0.03, 0.0, SH[0] - TS)                             # lower rail
    parts.append(ps)
    return parts


def build_inside(spec):
    """Partitions and shelves of the spans, battens under the shelves."""
    lod = spec["lod"]
    dv = P("dividers", "post")
    for x in DIVX:
        g.box(dv, x - 0.01, x + 0.01, YK, SY1, 0.0, ZU, **bev(0.003, lod))
    sh = P("shelves", "shelf")
    for xa, xb in BAYS:
        for z in SH:
            if lod == 0:
                plank(sh, FR_UP, xa, xb, SY0, SY1, z - TS, z, 0.003, back=True)
            else:
                g.box(sh, xa, xb, SY0, SY1, z - TS, z)
    parts = [dv, sh]
    if lod == 0:
        cl = P("shelf_cleats", "post")
        for xa, xb in BAYS:
            for z in SH[1:]:
                for xe, s in ((xa, 1), (xb, -1)):
                    g.box(cl, *sorted((xe, xe + s * 0.022)), SY0 + 0.03, SY1 - 0.02, z - TS - 0.022, z - TS)
        parts.append(cl)
    return parts


def build_footrail(spec):
    """Footrail: a dia. 42 pipe with domes at the ends on three brackets: a plate on the sheet with two nails,
    a strap to the pipe, a clamp."""
    lod = spec["lod"]
    fr = P("footrail", "footrail")
    n = 16 if lod == 0 else (8 if lod == 1 else 4)
    if lod == 0:
        e = RAIL_X
        G.lathe(fr, [(0.0, -e - 0.010), (RAIL_R * 0.72, -e - 0.007), (RAIL_R * 0.95, -e - 0.002), (RAIL_R, -e),
                     (RAIL_R, e), (RAIL_R * 0.95, e + 0.002), (RAIL_R * 0.72, e + 0.007), (0.0, e + 0.010)],
                n, (0.0, RAIL_Y, RAIL_Z), "x")
    else:
        g.cyl(fr, (0.0, RAIL_Y, RAIL_Z), "x", RAIL_R, 2 * RAIL_X, n)
    parts = [fr]
    if lod == 2:
        return parts
    br = P("rail_brackets", "bracket")
    yb = RAIL_Y + RAIL_R + 0.0025
    for x in (-0.80, 0.0, 0.80):
        g.box(br, x - 0.022, x + 0.022, YF - 0.005, YF + 0.0005, RAIL_Z - 0.045, RAIL_Z + 0.025, **bev(0.0015, lod))
        g.box(br, x - 0.012, x + 0.012, yb - 0.002, YF - 0.005, RAIL_Z - 0.0025, RAIL_Z + 0.0025)
        if lod == 0:
            G.lathe(br, [(RAIL_R + 0.0004, -0.012), (RAIL_R + 0.0025, -0.010), (RAIL_R + 0.0025, 0.010),
                         (RAIL_R + 0.0004, 0.012)], 12, (x, RAIL_Y, RAIL_Z), "x")              # clamp
            G.nail(br, (x, YF - 0.005, RAIL_Z - 0.035), (0, -1, 0), r=0.0042, h=0.0022, sides=4)
    parts.append(br)
    return parts


# =============================================================================
# Containers and dishes
# =============================================================================
# beer 0.5 l: heel, body (the label is segment 2), shoulder, neck (the ring label is segment 5); the lip
# is closed with a crown cap
BEER = [(0.0335, 0.0), (0.0345, 0.006), (0.0345, 0.050), (0.0345, 0.122), (0.031, 0.158), (0.0215, 0.180),
        (0.0158, 0.197), (0.0136, 0.214), (0.0136, 0.236)]
BEER_LBL = (2, 5)
# port 0.7 l: body (the label is segment 2), shoulder, a long neck (segment 6), a plastic stopper
PORT = [(0.0365, 0.0), (0.0375, 0.008), (0.0375, 0.065), (0.0375, 0.150), (0.0375, 0.190), (0.034, 0.210),
        (0.022, 0.232), (0.0165, 0.246), (0.0150, 0.262), (0.0150, 0.284)]
PORT_LBL = (2, 6)


def bottle(part, prof, lbl, x, y, z, sides, label=None, from_h=0.0, crown=True):
    """Bottle by profile: the label is the regions of segments lbl (label - the region name or None), on
    top a crown cap (8 faces: with smoothing up to 40 degrees the facets stay, like a corrugation) or a
    plastic stopper. from_h - only the part above it is visible (bottles in the crate)."""
    pr = [p for p in prof if p[1] >= from_h - 1e-6]
    if from_h > 0 and pr[0][1] > from_h:
        pr = [(pr[0][0], from_h)] + pr
    tags = None
    if label:
        off = len(prof) - len(pr)
        li, ln = reg(part, label), reg(part, "label_n")
        tags = [None] * (len(pr) - 1)
        for k, idx in ((lbl[0], li), (lbl[1], ln)):
            if 0 <= k - off < len(tags):
                tags[k - off] = idx
    G.lathe(part, pr, sides, (x, y, z), tags=tags)
    r, h = prof[-1]
    if crown:
        use(part, "crown")
        rc, h0 = r + 0.0016, h - 0.0045
        G.lathe(part, [(rc, h0), (rc, h0 + 0.0055), (rc * 0.82, h0 + 0.0068), (0.0, h0 + 0.0071)], 8, (x, y, z),
                phase=math.pi / 8)
    else:
        use(part, "cork")
        G.lathe(part, [(r + 0.0006, h - 0.004), (r + 0.0012, h), (r + 0.0012, h + 0.012), (r - 0.001, h + 0.0155),
                       (0.0, h + 0.016)], 8, (x, y, z))


def bottle_lod1(part, prof, x, y, z, from_h=0.0):
    """Mid LOD: body and neck as two prisms."""
    rb = max(p[0] for p in prof)
    sh = max(p[1] for p in prof if p[0] >= rb * 0.95)
    if from_h < sh:
        g.cyl(part, (x, y, z + (from_h + sh) / 2), "z", rb, sh - from_h, 5)
    top = prof[-1][1] + 0.006
    g.cyl(part, (x, y, z + (max(sh, from_h) + top) / 2), "z", prof[-1][0] + 0.003, top - max(sh, from_h), 3)


def mug(part, x, y, z, ang, beer=None, foam=None, upside=False, lod=0):
    """Beer mug 0.5 l: 10 faces outside (own vertices - the facets are visible), smooth inside, a thick
    bottom, a handle as a smooth curve; upside - bottom up (on the shelf). beer/foam - the parts of the
    beer with foam."""
    H, R, RI = 0.152, 0.042, 0.0375
    c = (x, y, z + H) if upside else (x, y, z)
    ax = "-z" if upside else "z"
    if lod > 0:
        g.cyl(part, (x, y, z + H / 2), "z", R, H, 6)
        if beer is not None:
            g.cyl(beer, (x, y, z + 0.066), "z", RI - 0.002, 0.11, 6)
            g.cyl(foam, (x, y, z + 0.124), "z", RI - 0.002, 0.016, 6)
        return
    G.facet_lathe(part, [(R * 0.965, 0.0), (R, 0.007), (R, H - 0.004), (R * 0.99, H)], 10, c, ax, phase=0.0)
    if upside:
        G.lathe(part, [(R * 0.99, H), (RI, H - 0.001)], 10, c, ax)            # rim on the shelf, the inside is not visible
    else:
        G.lathe(part, [(R * 0.99, H), (RI, H - 0.001), (RI, 0.018), (0.0, 0.018)], 10, c, ax)
    G.lathe(part, [(0.0, 0.0), (R * 0.965, 0.0)], 10, c, ax)
    a = math.radians(ang)
    e, s = Vector((math.cos(a), math.sin(a), 0.0)), (-1.0 if upside else 1.0)
    base = Vector(c)
    pts = [base + e * (R - 0.003 + dr) + Vector((0, 0, s * h)) for dr, h in
           ((0.0, H - 0.020), (0.020, H - 0.024), (0.032, H - 0.052), (0.031, 0.060), (0.016, 0.034), (0.0, 0.030))]
    hp = G.spline([tuple(p) for p in pts], 2)
    g.tube_var(part, hp, [(0.0072, 0.0052)] * len(hp), 4)
    if beer is not None and not upside:
        g.cyl(beer, (x, y, z + 0.018 + 0.05), "z", RI - 0.0008, 0.10, 10)
        G.lathe(foam, [(RI - 0.0007, 0.116), (RI - 0.0005, 0.128), (RI * 0.75, 0.1335), (0.0, 0.135)], 10, (x, y, z))


def glass_tumbler(part, x, y, z, lod=0):
    """Faceted 250 ml glass, bottom up: 12 faces (own vertices), a smooth band at the rim."""
    H = 0.090
    c = (x, y, z + H)
    if lod > 0:
        g.cyl(part, (x, y, z + H / 2), "z", 0.035, H, 4, r2=0.030)
        return
    G.facet_lathe(part, [(0.0275, 0.0), (0.0285, 0.004), (0.0345, 0.073)], 10, c, "-z")
    G.lathe(part, [(0.0345, 0.073), (0.0358, 0.076), (0.0358, 0.090)], 10, c, "-z")
    G.lathe(part, [(0.0, 0.0), (0.0275, 0.0)], 10, c, "-z")


def jar3(spec, glass, lid, fill, x, y, z, lumpy):
    """Three-liter jar dia. 150 x 245: heel, body, shoulder, neck with a lip, a tin lid; inside - the contents
    in lumps (lumpy) or level (compote)."""
    lod = spec["lod"]
    if lod > 0:
        g.cyl(glass, (x, y, z + 0.1125), "z", 0.075, 0.225, 6, r2=0.06)
        g.cyl(lid, (x, y, z + 0.233), "z", 0.0455, 0.016, 6)
        return
    G.lathe(glass, [(0.0, 0.0), (0.066, 0.0), (0.073, 0.008), (0.075, 0.022), (0.075, 0.168), (0.068, 0.195),
                    (0.0545, 0.211), (0.0442, 0.219), (0.0436, 0.229)], 12, (x, y, z))
    G.lathe(lid, [(0.0472, 0.228), (0.0478, 0.231), (0.0478, 0.243), (0.0, 0.2465)], 12, (x, y, z))
    rnd = random.Random(int(x * 100 + 7))
    bumps = [rnd.uniform(-1, 1) for _ in range(200)]

    def rad(k, i):
        return 1.0 + (0.055 * bumps[(k * 7 + i * 13) % 200] if lumpy else 0.0)
    # lumps are no farther than 70 mm from the axis: the glass is 72..75 mm from inside
    rf = 0.066 if lumpy else 0.071
    G.lathe(fill, [(0.0, 0.007), (rf - 0.004, 0.007), (rf, 0.03), (rf, 0.10), (rf, 0.16), (rf - 0.007, 0.176),
                   (0.0, 0.181 if lumpy else 0.178)], 10, (x, y, z), rad=rad)


def tin_can(part, label, x, y, z, r, h, lod=0):
    """Tin can with seams at the top and bottom, a paper label (region label) around the body."""
    if lod > 0:
        g.cyl(part, (x, y, z + h / 2), "z", r, h, 4)
        return
    li = reg(part, label)
    G.lathe(part, [(r - 0.004, 0.0), (r, 0.0035), (r - 0.001, 0.006), (r - 0.001, h - 0.006), (r, h - 0.0035),
                   (r - 0.004, h), (0.0, h - 0.0008)], 10, (x, y, z), tags=[None, None, li, None, None, None])


def row_mass(part, x0, x1, y0, y1, z, h):
    g.box(part, x0, x1, y0, y1, z, z + h)


def build_bay_left(spec):
    """Left span (on the bartender's right): at the bottom a crate with beer and port, on the middle
    shelf vanilla vodka and two beers, at the top faceted glasses bottom up."""
    lod = spec["lod"]
    xa, xb = BAYS[0]
    parts = []
    cx0, cx1, cy0, cy1, ch = xa + 0.03, xa + 0.37, 0.02, 0.30, 0.16
    z0 = SH[0]
    cr = P("crate", "crate")
    if lod == 2:
        g.box(cr, cx0, cx1, cy0, cy1, z0, z0 + ch)
        ms = P("bayl_mass", "bottle_brown")
        g.box(ms, cx0 + 0.02, cx1 - 0.02, cy0 + 0.02, cy1 - 0.02, z0 + ch, z0 + 0.245)
        row_mass(ms, xa + 0.42, xb - 0.03, 0.18, 0.30, z0, 0.28)
        row_mass(ms, xa + 0.28, xb - 0.03, 0.20, 0.30, SH[1], 0.25)
        row_mass(ms, xa + 0.03, xa + 0.45, 0.20, 0.30, SH[2], 0.09)
        return [cr, ms]
    # crate: bottom, two slats per side with a gap, ends with a handle cutout, a grid of cells
    g.box(cr, cx0, cx1, cy0, cy1, z0, z0 + 0.012)
    for ya, yb in ((cy0, cy0 + 0.012), (cy1 - 0.012, cy1)):
        for za, zb in ((z0 + 0.012, z0 + 0.07), (z0 + 0.09, z0 + ch)):
            g.box(cr, cx0 + 0.015, cx1 - 0.015, ya, yb, za, zb, **bev(0.002, lod))
    ce = P("crate_ends", "crate_end")
    for xa_, xb_ in ((cx0, cx0 + 0.015), (cx1 - 0.015, cx1)):
        g.box(ce, xa_, xb_, cy0, cy1, z0, z0 + ch + 0.01, **bev(0.002, lod))
    parts += [cr, ce]
    if lod == 0:
        hole = P("crate_holes", "reg_inner")
        for xe, s in ((cx0, -1), (cx1, 1)):
            g.box(hole, *sorted((xe + s * 0.0006, xe - s * 0.004)), (cy0 + cy1) / 2 - 0.045, (cy0 + cy1) / 2 + 0.045,
                  z0 + ch - 0.035, z0 + ch - 0.012)
        parts.append(hole)
        for k in (1, 2, 3):
            xx = cx0 + (cx1 - cx0) * k / 4
            g.box(cr, xx - 0.003, xx + 0.003, cy0 + 0.012, cy1 - 0.012, z0 + 0.012, z0 + 0.11)
        for k in (1, 2):
            yy = cy0 + (cy1 - cy0) * k / 3
            g.box(cr, cx0 + 0.015, cx1 - 0.015, yy - 0.003, yy + 0.003, z0 + 0.012, z0 + 0.11)
    skip = {(0, 3), (2, 1), (1, 0), (0, 0), (2, 2)}
    if lod == 1:
        bb = P("crate_bottles", "bottle_brown")
        for i in range(4):
            for j in range(3):
                if (j, i) not in skip:
                    bottle_lod1(bb, BEER, cx0 + (cx1 - cx0) * (i + 0.5) / 4, cy0 + (cy1 - cy0) * (j + 0.5) / 3,
                                z0 + 0.012, from_h=0.14)
        parts.append(bb)
    else:
        for i in range(4):
            for j in range(3):
                if (j, i) in skip:
                    continue
                bx = cx0 + (cx1 - cx0) * (i + 0.5) / 4
                by = cy0 + (cy1 - cy0) * (j + 0.5) / 3
                bt = P("crate_bottle_%d%d" % (i, j), "bottle_brown", uv_name="crate_bottle", uv_origin=(bx, by, z0 + 0.012))
                bottle(bt, BEER, BEER_LBL, bx, by, z0 + 0.012, 8, from_h=0.14)
                parts.append(bt)
    # port: two bottles, burgundy labels
    for k, (x, y) in enumerate(((xa + 0.47, 0.26), (xa + 0.55, 0.22))):
        pb = P("port_%d" % k, "bottle_port", uv_name="port_bottle", uv_origin=(x, y, z0))
        if lod == 1:
            bottle_lod1(pb, PORT, x, y, z0)
        else:
            bottle(pb, PORT, PORT_LBL, x, y, z0, 10, label="label_b", crown=False)
        parts.append(pb)
    # middle shelf: the vodka is vanilla (DECOR), two beers beside it
    for k, (x, y) in enumerate(((xb - 0.115, 0.245), (xb - 0.05, 0.215))):
        bt = P("shelf_beer_l%d" % k, "bottle_brown", uv_name="beer_bottle", uv_origin=(x, y, SH[1]))
        if lod == 1:
            bottle_lod1(bt, BEER, x, y, SH[1])
        else:
            bottle(bt, BEER, BEER_LBL, x, y, SH[1], 10, label="label_a" if k == 0 else None)
        parts.append(bt)
    # glasses bottom up
    gl = P("glasses", "glass", section="glass")
    for k in range(5):
        glass_tumbler(gl, xa + 0.075 + k * 0.08, 0.255 if k % 2 else 0.215, SH[2], lod)
    parts.append(gl)
    return parts


def build_bay_mid(spec):
    """Middle span: at the bottom three 3 l jars, on the middle shelf beer, at the top mugs bottom up."""
    lod = spec["lod"]
    xa, xb = BAYS[1]
    if lod == 2:
        ms = P("baym_mass", "tomato")
        row_mass(ms, xa + 0.04, xb - 0.04, 0.10, 0.27, SH[0], 0.24)
        mb = P("baym_mass_b", "bottle_brown")
        row_mass(mb, xa + 0.04, xb - 0.04, 0.19, 0.29, SH[1], 0.245)
        return [ms, mb]
    parts = []
    gl = P("jars3_glass", "glass", section="glass")
    lids = P("jars3_lids", "lid")
    fills = [P("jar3_" + k, k) for k in ("tomato", "compote", "cabbage")]
    for k, x in enumerate((-0.22, 0.0, 0.22)):
        jar3(spec, gl, lids, fills[k], x, 0.19 - (k % 2) * 0.02, SH[0], lumpy=k != 1)
    parts += [gl, lids] + (fills if lod == 0 else [])
    # beer: five bottles, three with blank labels
    for k in range(5):
        x = xa + 0.085 + k * 0.13
        y = 0.245 - (k % 3) * 0.016
        bt = P("shelf_beer_m%d" % k, "bottle_brown", uv_name="beer_bottle", uv_origin=(x, y, SH[1]))
        if lod == 1:
            bottle_lod1(bt, BEER, x, y, SH[1])
        else:
            bottle(bt, BEER, BEER_LBL, x, y, SH[1], 10, label="label_a" if k % 2 == 0 else None)
        parts.append(bt)
    mg = P("mugs_shelf", "glass", section="glass")
    for k, x in enumerate((-0.22, -0.07, 0.08)):
        mug(mg, x, 0.235 - (k % 2) * 0.03, SH[2], 200.0 + 50 * k, upside=True, lod=lod)
    parts.append(mg)
    return parts


def build_bay_right(spec):
    """Right span: at the bottom a cardboard box with condensed milk on it, on the middle shelf a heap of
    stewed meat and the vanilla "Veterok" and "Tuna", at the top vanilla honey, jam, a lantern and a can
    of stewed meat."""
    lod = spec["lod"]
    xa, xb = BAYS[2]
    parts = []
    cb = P("bayr_box", "carton")
    bx0, bx1, by0, by1, bh = xa + 0.04, xa + 0.44, 0.0, 0.31, 0.18
    g.box(cb, bx0, bx1, by0, by1, SH[0], SH[0] + bh, **bev(0.003, lod))
    parts.append(cb)
    if lod == 2:
        ms = P("bayr_mass", "can")
        row_mass(ms, xa + 0.04, xa + 0.30, 0.16, 0.30, SH[1], 0.13)
        return parts + [ms]
    if lod == 0:
        tp = P("bayr_tape", "tape")
        g.box(tp, bx0 - 0.0008, bx1 + 0.0008, (by0 + by1) / 2 - 0.025, (by0 + by1) / 2 + 0.025, SH[0] + bh - 0.0005,
              SH[0] + bh + 0.0006)
        g.box(tp, bx0 - 0.0008, bx0 + 0.0002, (by0 + by1) / 2 - 0.025, (by0 + by1) / 2 + 0.025, SH[0] + bh - 0.06,
              SH[0] + bh)
        g.box(tp, bx1 - 0.0002, bx1 + 0.0008, (by0 + by1) / 2 - 0.025, (by0 + by1) / 2 + 0.025, SH[0] + bh - 0.06,
              SH[0] + bh)
        parts.append(tp)
    zc = SH[0] + bh
    cans = [("milk", xa + 0.12, 0.22, zc, 0.038, 0.078), ("milk", xa + 0.205, 0.245, zc, 0.038, 0.078),
            ("milk", xa + 0.12, 0.22, zc + 0.078, 0.038, 0.078)]
    for k in range(3):
        cans.append(("meat", xa + 0.07 + k * 0.102, 0.245, SH[1], 0.050, 0.065))
    for k in range(2):
        cans.append(("meat", xa + 0.121 + k * 0.102, 0.245, SH[1] + 0.065, 0.050, 0.065))
    if lod == 1:
        body = P("cans", "can")
        for kind, x, y, z, r, h in cans:
            tin_can(body, None, x, y, z, r, h, lod=1)
        return parts + [body]
    for k, (kind, x, y, z, r, h) in enumerate(cans):
        cp = P("can_%s_%d" % (kind, k), "can", uv_name="can_" + kind, uv_origin=(x, y, z))
        tin_can(cp, "label_" + kind, x, y, z, r, h)
        parts.append(cp)
    return parts


# =============================================================================
# "Oka" register
# =============================================================================
def fillet_poly(poly, radii, n):
    """Polygon (counterclockwise) with rounded corners: radii[i] is the radius of corner i (0 - sharp)."""
    out = []
    m = len(poly)
    for i in range(m):
        c = Vector(poly[i])
        r = radii[i]
        if r <= 0:
            out.append(tuple(c))
            continue
        a, b = Vector(poly[i - 1]), Vector(poly[(i + 1) % m])
        d1, d2 = (a - c).normalized(), (b - c).normalized()
        th = math.acos(max(-1.0, min(1.0, d1.dot(d2))))
        t = r / math.tan(th / 2)
        bis = (d1 + d2).normalized()
        cen = c + bis * (r / math.sin(th / 2))
        p1, p2 = c + d1 * t, c + d2 * t
        a1, a2 = math.atan2(p1.y - cen.y, p1.x - cen.x), math.atan2(p2.y - cen.y, p2.x - cen.x)
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for k in range(n + 1):
            aa = a1 + da * k / n
            out.append((cen.x + r * math.cos(aa), cen.y + r * math.sin(aa)))
    return out


def inset_poly(poly, d):
    """Convex polygon (counterclockwise) moved inward by d (joints along the bisector)."""
    m = len(poly)
    out = []
    for i in range(m):
        p0, p1, p2 = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % m])
        e1, e2 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n1, n2 = Vector((-e1.y, e1.x)), Vector((-e2.y, e2.x))
        k = n1 + n2
        out.append(tuple(p1 + k * (d / max(1.0 + n1.dot(n2), 0.2))))
    return out


def build_register(spec):
    """The "Oka" register: a base box with a cash drawer (bone ozl_drawer: a drawer with cells, coins and
    coupons), a case with rounded edges and side chamfers, a panel sloping toward the bartender: a well
    with raised keys, locks, the cashier display, a receipt window with a roll and tape, a nameplate; at
    the top rear a superstructure with the customer display and a lamp (ozl_lamp); a crank to the
    cashier's right; feet."""
    lod = spec["lod"]
    hw = L.REG_W / 2
    x0, x1 = L.RX - hw, L.RX + hw
    zf, zd = ZT + L.REG_FEET, ZT + L.REG_ZD
    zk, zh = ZT + L.REG_ZK, ZT + L.REG_ZH
    yb, yf = L.REG_YB, L.REG_YF
    ye = yf + 0.012                                          # face of the base (drawer opening)
    parts = []
    bs = P("reg_base", "reg_base")
    t = 0.006
    if lod == 0:
        g.box(bs, x0, x1, yb, ye, zd - t, zd, r=0.002, seg=1)
        g.box(bs, x0, x1, yb, ye, zf, zf + t, r=0.002, seg=1)
        for xa, xb_ in ((x0, x0 + t), (x1 - t, x1)):
            g.box(bs, xa, xb_, yb, ye, zf + t, zd - t)
        g.box(bs, x0 + t, x1 - t, yb, yb + t, zf + t, zd - t)
        g.box(bs, x0 + t, x1 - t, ye - 0.006, ye, zd - t - 0.007, zd - t)
        g.box(bs, x0 + t, x1 - t, ye - 0.006, ye, zf + t, zf + t + 0.005)
        ft = P("reg_feet", "rubber")
        for xx in (x0 + 0.02, x1 - 0.02):
            for yy in (yb + 0.02, ye - 0.02):
                g.cyl(ft, (xx, yy, ZT + L.REG_FEET / 2), "z", 0.009, L.REG_FEET, 6)
        parts.append(ft)
    else:
        g.box(bs, x0, x1, yb, ye, ZT, zd)
    parts.append(bs)
    # cash drawer: face, bar handle, lock; inside - a tray with cells, coins, coupons
    fr_dr = g.Frame((0.0, ye, 0.0), (1, 0, 0), (0, 0, 1), (0, 1, 0))
    dr = P("reg_drawer", "reg_base", group=SEL_DRAWER)
    if lod == 0:
        G.slab(dr, x0 + 0.003, x1 - 0.003, zf + 0.003, zd - 0.003, 0.0, 0.012, rc=0.004, nc=1, re=0.002, ne=1,
               frame=fr_dr)
    elif lod == 1:
        g.box(dr, x0 + 0.003, x1 - 0.003, ye, ye + 0.012, zf + 0.003, zd - 0.003)
    if lod < 2:
        parts.append(dr)
    zc = (zf + zd) / 2
    if lod == 0:
        hd = P("reg_drawer_handle", "chrome", group=SEL_DRAWER)
        hp = G.spline([(L.RX - 0.055, ye + 0.012, zc - 0.004), (L.RX - 0.05, ye + 0.030, zc - 0.004),
                       (L.RX + 0.05, ye + 0.030, zc - 0.004), (L.RX + 0.055, ye + 0.012, zc - 0.004)], 3)
        g.pipe(hd, hp, 0.0042, 5)
        G.lathe(hd, [(0.0075, 0.0), (0.0075, 0.003), (0.006, 0.0042), (0.0, 0.0042)], 10, (x1 - 0.045, ye + 0.012, zc + 0.012), "y")
        kh = P("reg_drawer_keyhole", "black", group=SEL_DRAWER)
        g.box(kh, x1 - 0.0458, x1 - 0.0442, ye + 0.0162, ye + 0.0168, zc + 0.008, zc + 0.016)
        tr = P("reg_drawer_tray", "reg_tray", group=SEL_DRAWER)
        xa, xb_ = x0 + 0.009, x1 - 0.009
        ya = yb + 0.07
        za, zb = zf + 0.008, zd - 0.015
        g.box(tr, xa, xb_, ya, ye, za, za + 0.003)
        g.box(tr, xa, xa + 0.003, ya, ye, za, zb)
        g.box(tr, xb_ - 0.003, xb_, ya, ye, za, zb)
        g.box(tr, xa, xb_, ya, ya + 0.003, za, zb)
        yc = ye - 0.068                                     # partition: coin cups in front
        g.box(tr, xa, xb_, yc - 0.0015, yc + 0.0015, za, zb - 0.008)
        for k in range(1, 5):
            xk = xa + (xb_ - xa) * k / 5
            g.box(tr, xk - 0.0015, xk + 0.0015, yc, ye, za, zb - 0.012)
        for k in range(1, 4):
            xk = xa + (xb_ - xa) * k / 4
            g.box(tr, xk - 0.0015, xk + 0.0015, ya, yc, za, zb - 0.008)
        cn = P("reg_coins", "coin", group=SEL_DRAWER)
        for k, cnt in ((0, 3), (1, 1), (2, 2), (4, 2)):
            xc = xa + (xb_ - xa) * (k + 0.5) / 5
            for j in range(cnt):
                g.cyl(cn, (xc + 0.004 * math.sin(j * 2.1 + k), ye - 0.034 + 0.005 * math.cos(j * 1.7 + k),
                           za + 0.0038 + 0.0017 * j), "z", 0.0115 - 0.0015 * (k % 2), 0.0016, 6)
        bl = P("reg_bills", "bill_a", group=SEL_DRAWER)
        for k, rg in ((0, "bill_a"), (1, "bill_b"), (3, "bill_a")):
            xc = xa + (xb_ - xa) * (k + 0.5) / 4
            use(bl, rg)
            g.box(bl, xc - 0.03, xc + 0.03, yc - 0.15, yc - 0.006, za + 0.003, za + 0.009 + 0.003 * k)
        parts += [hd, kh, tr, cn, bl]
    # case: a profile in the y-z plane with rounded edges, chamfered at the sides
    poly = [(yb, zd), (yf, zd), (yf, zk), (L.KEY_Y0, zh), (yb, zh)]
    rg = P("reg", "reg")
    if lod == 0:
        prof = fillet_poly(poly, [0.0, 0.0, 0.006, 0.016, 0.010], 3)
        ch = 0.0035

        def PP(a, b, c):
            return Vector((c, a, b))
        G.loft(rg, [inset_poly(prof, ch), prof, prof, inset_poly(prof, ch)], [x0, x0 + ch, x1 - ch, x1], PP)
    else:
        g.prism(rg, poly, (1, 2), x0, x1)
    parts.append(rg)
    # superstructure: the customer display and the lamp
    hdp = P("reg_head", "reg")
    hx0, hx1, hy0, hy1, hz0, hz1 = L.HEAD
    if lod == 0:
        G.slab(hdp, hx0, hx1, hy0, hy1, hz0 - 0.002, hz1, rc=0.006, nc=2, re=0.008, ne=2)
    else:
        g.box(hdp, hx0, hx1, hy0, hy1, hz0, hz1)
    parts.append(hdp)
    dx0, dx1, dz0, dz1 = L.DISP
    if lod == 0:
        dfr = P("reg_disp_frame", "black")
        G.slab(dfr, dx0 - 0.006, dx1 + 0.006, dz0 - 0.005, dz1 + 0.005, 0.0, 0.002, rc=0.002, nc=1, frame=FR_BACK)
        parts.append(dfr)
    dp = P("reg_disp_back", "disp", group=SEL_DISP, section="disp")
    yd = hy0 - (0.0021 if lod == 0 else 0.0006)
    vs = [dp.bm.verts.new((xx, yd, zz)) for xx, zz in ((dx0, dz0), (dx1, dz0), (dx1, dz1), (dx0, dz1))]
    G.face(dp, vs, (0, -1, 0))
    parts.append(dp)
    lp = P("reg_lamp", "lamp", group=SEL_LAMP)
    G.lathe(lp, [(0.0086, 0.0), (0.0083, 0.0022), (0.006, 0.0046), (0.0, 0.0056)], 12 if lod == 0 else 6,
            (L.LAMP_C[0], hy0 - 0.0012, L.LAMP_C[1]), "-y")
    parts.append(lp)
    if lod == 2:
        return parts
    # sloped panel
    a0, a1, b0, b1 = L.WELL
    wl = P("reg_well", "reg_well")
    G.slab(wl, a0, a1, b0, b1, 0.0, L.WELL_H, rc=0.004 if lod == 0 else 0.0, nc=1 if lod == 0 else 0, frame=FR_KB)
    parts.append(wl)
    ca0, ca1, cb0, cb1 = L.CASH_WIN
    if lod == 0:
        bz = P("reg_bezel", "bezel")
        w_, h_ = 0.003, L.WELL_H + 0.0022
        for qa0, qa1, qb0, qb1 in ((a0 - w_, a1 + w_, b0 - w_, b0), (a0 - w_, a1 + w_, b1, b1 + w_),
                                   (a0 - w_, a0, b0, b1), (a1, a1 + w_, b0, b1)):
            g.box(bz, qa0, qa1, qb0, qb1, 0.0, h_, frame=FR_KB)
        # lamp rim of the locks and the locks: chrome cylinders with a slot
        for bb in L.LOCK_B:
            c = FR_KB.p(L.LONG_A, bb, L.WELL_H)
            G.lathe(bz, [(0.0066, 0.0), (0.0066, 0.0032), (0.0056, 0.0044), (0.0, 0.0044)], 10, tuple(c), L.KB_N)
        parts.append(bz)
        sl = P("reg_lock_slots", "black")
        for bb in L.LOCK_B:
            g.box(sl, L.LONG_A - 0.0007, L.LONG_A + 0.0007, bb - 0.0038, bb + 0.0038, L.WELL_H + 0.0042,
                  L.WELL_H + 0.0048, frame=FR_KB)
        parts.append(sl)
        keys = {}
        for col, a, b, wa, wb, mark in L.keys():
            kp = keys.get(col)
            if kp is None:
                kp = keys[col] = P("reg_keys_" + col, "key_" + col)
            G.keycap(kp, FR_KB, a, b, wa, wb, L.KEY_H, top=0.82, n0=L.WELL_H)
        parts += list(keys.values())
        # cashier display: a frame and a window (the same texture as the customer's)
        cf = P("reg_cash_frame", "black")
        G.slab(cf, ca0 - 0.005, ca1 + 0.005, cb0 - 0.0045, cb1 + 0.0045, 0.0, 0.0016, rc=0.002, nc=1, frame=FR_KB)
        parts.append(cf)
        # receipt window: a box frame above the panel, glass, dark inside, a paper roll; the tape comes out of a slot
        ka0, ka1, kb0, kb1 = L.CHECK_WIN
        hk = 0.014
        kf = P("reg_check_frame", "bezel")
        for qa0, qa1, qb0, qb1 in ((ka0, ka1, kb0, kb0 + 0.004), (ka0, ka1, kb1 - 0.004, kb1),
                                   (ka0, ka0 + 0.004, kb0, kb1), (ka1 - 0.004, ka1, kb0, kb1)):
            g.box(kf, qa0, qa1, qb0, qb1, 0.0, hk, frame=FR_KB)
        parts.append(kf)
        ki = P("reg_check_inner", "reg_inner")
        g.box(ki, ka0 + 0.004, ka1 - 0.004, kb0 + 0.004, kb1 - 0.004, 0.0, 0.001, frame=FR_KB)
        parts.append(ki)
        pr = P("reg_paper", "paper")
        rc = FR_KB.p((ka0 + ka1) / 2, (kb0 + kb1) / 2 + 0.006, -0.001)
        g.cyl(pr, tuple(rc), "x", 0.0115, ka1 - ka0 - 0.012, 12)
        am = (ka0 + ka1) / 2
        strip = [FR_KB.p(am, kb1 - 0.002, hk - 0.001), FR_KB.p(am, kb1 + 0.010, hk + 0.004),
                 FR_KB.p(am, kb1 + 0.017, hk + 0.016), FR_KB.p(am, kb1 + 0.013, hk + 0.031),
                 FR_KB.p(am, kb1 + 0.001, hk + 0.040), FR_KB.p(am, kb1 - 0.013, hk + 0.036)]
        g.sweep(pr, [tuple(p) for p in G.spline([tuple(p) for p in strip], 2)], (1, 0, 0), 0.00025, 0.021)
        parts.append(pr)
        kg = P("reg_check_glass", "glass", section="glass")
        vs = [kg.bm.verts.new(FR_KB.p(aa, bb, hk - 0.0015)) for aa, bb in
              ((ka0 + 0.003, kb0 + 0.003), (ka1 - 0.003, kb0 + 0.003), (ka1 - 0.003, kb1 - 0.003), (ka0 + 0.003, kb1 - 0.003))]
        G.face(kg, vs, L.KB_N)
        parts.append(kg)
        pl = P("reg_plate", "plate")
        pa0, pa1, pb0, pb1 = L.PLATE
        G.slab(pl, pa0, pa1, pb0, pb1, 0.0, 0.0009, rc=0.002, nc=1, frame=FR_KB)
        parts.append(pl)
        # crank to the cashier's right (the -x side): hub, crank arm, handle
        ck = P("reg_crank", "chrome")
        hub = (x0, 0.165, ZT + 0.200)
        G.lathe(ck, [(0.0, 0.0), (0.0135, 0.0), (0.0135, 0.010), (0.0105, 0.0145), (0.0, 0.0145)], 12, hub, "-x")
        piv = (x0 - 0.019, 0.2165, ZT + 0.1475)
        g.sweep(ck, [(x0 - 0.019, hub[1], hub[2]), piv], (1, 0, 0), 0.006, 0.0028)
        g.cyl(ck, (piv[0] - 0.003, piv[1], piv[2]), "x", 0.0045, 0.008, 8)
        parts.append(ck)
        gp = P("reg_crank_grip", "grip")
        G.lathe(gp, [(0.0, 0.0), (0.006, 0.0008), (0.0094, 0.007), (0.009, 0.033), (0.0066, 0.039), (0.0, 0.040)], 10,
                (piv[0] - 0.006, piv[1], piv[2]), "-x")
        # power cord: from the side of the base along the counter to the bartender's edge, over the edge to the
        # socket on the corner post
        cd = P("reg_cord", "black")
        path = [(x1 - 0.004, 0.045, zf + 0.022), (x1 + 0.022, 0.052, ZT + 0.0035), (0.53, 0.13, ZT + 0.0032),
                (0.555, 0.27, ZT + 0.0032), (0.60, 0.338, ZT + 0.0032), (0.66, 0.3565, ZT - 0.012),
                (0.74, 0.361, ZT - 0.075), (0.88, 0.377, 0.975), (0.985, 0.394, 0.948), (1.03, 0.396, 0.941)]
        g.pipe(cd, G.spline(path, 3), 0.0032, 6)
        so = P("reg_socket", "grip")
        G.lathe(so, [(0.0, 0.0), (0.030, 0.0), (0.030, 0.012), (0.026, 0.020), (0.0, 0.021)], 12, (1.03, YB, 0.94), "y")
        G.lathe(so, [(0.0, 0.021), (0.0165, 0.021), (0.0165, 0.040), (0.011, 0.0455), (0.0, 0.046)], 10, (1.03, YB, 0.94), "y")
        # rear of the case (toward the player): louver slots, screws at the corners, an empty nameplate
        lv = P("reg_vents", "reg_inner")
        for k in range(5):
            zz = zd + 0.05 + k * 0.016
            g.box(lv, L.RX - 0.085, L.RX + 0.085, yb - 0.0004, yb + 0.001, zz, zz + 0.0045)
        bs_sc = P("reg_screws", "bezel")
        for xx in (x0 + 0.014, x1 - 0.014):
            for zz in (zd + 0.016, zh - 0.022):
                G.hexhead(bs_sc, (xx, yb, zz), (0, -1, 0), r=0.0032, h=0.0018)
        G.slab(bs_sc, L.RX + 0.095, L.RX + 0.150, zd + 0.040, zd + 0.068, 0.0, 0.0008, rc=0.002, nc=1, frame=FR_BACK)
        parts += [gp, cd, so, lv, bs_sc]
    else:
        kp = P("reg_keys_black", "key_black")
        g.box(kp, L.LONG_A - 0.01, L.COL_A[0] + 0.01, L.KEY_ROWS_B0 - 0.01, L.row_b(0) + 0.01, L.WELL_H, L.WELL_H + 0.006,
              frame=FR_KB)
        parts.append(kp)
    cp = P("reg_disp_cash", "disp", group=SEL_DISP, section="disp")
    nz = 0.0017 if lod == 0 else 0.0006
    vs = [cp.bm.verts.new(FR_KB.p(aa, bb, nz)) for aa, bb in ((ca0, cb0), (ca1, cb0), (ca1, cb1), (ca0, cb1))]
    G.face(cp, vs, L.KB_N)
    cp.glass_frame = (FR_CASH, -ca1, -ca0, cb0, cb1)
    parts.append(cp)
    return parts


def build_tray(spec):
    """Receiving tray in front of the register - the "hand-in point": a stamped galvanized pan, flared
    walls, rounded corners, a rolled rim."""
    lod = spec["lod"]
    tr = P("tray", "tray")
    x0, x1, y0, y1, h = 0.14, 0.46, -0.30, -0.10, 0.032
    if lod == 2:
        g.box(tr, x0, x1, y0, y1, ZT, ZT + h * 0.5)
        return [tr]
    if lod == 1:
        g.box(tr, x0, x1, y0, y1, ZT, ZT + 0.0015)
        for ya, yb in ((y0, y0 + 0.0015), (y1 - 0.0015, y1)):
            g.box(tr, x0, x1, ya, yb, ZT, ZT + h)
        for xa, xb in ((x0, x0 + 0.0015), (x1 - 0.0015, x1)):
            g.box(tr, xa, xb, y0, y1, ZT, ZT + h)
        return [tr]

    def ring(d, r):
        return G.rrect(x0 + d, x1 - d, y0 + d, y1 - d, r, 3)
    G.loft(tr, [ring(0.006, 0.010), ring(0.0, 0.016), ring(0.0016, 0.0144), ring(0.0075, 0.0085)],
           [ZT, ZT + h, ZT + h, ZT + 0.0015], lambda a, b, c: Vector((a, b, c)))
    rim = ring(-0.0006, 0.0166)
    g.pipe(tr, [(a, b, ZT + h) for a, b in rim + rim[:1]], 0.0021, 4)
    return [tr]


def build_radio(spec):
    """VEF-202 with the scale toward the player: a leatherette case with rounded edges, a silver panel with
    a grille, the scale (ozl_screen) in a frame under glass, the needle (bone ozl_needle), knurled volume
    and tuning knobs (bone ozl_knob), band keys, a handle on brackets, a telescopic antenna, feet."""
    lod = spec["lod"]
    hw, hd = L.Q_W / 2, L.Q_D / 2
    z0 = ZT + L.Q_FEET
    zt = z0 + L.Q_H
    parts = []
    bd = P("radio", "radio")
    if lod == 0:
        # the case is 4 mm above the counter - on rubber feet (not visible under the case, so no own geometry)
        G.slab(bd, L.QX - hw, L.QX + hw, L.QY - hd, L.QY + hd, z0, zt, rc=0.014, nc=3, re=0.008, ne=2, rb=0.004, nb=1)
        ft = P("radio_feet", "rubber")
        g.box(ft, L.QX - hw + 0.02, L.QX + hw - 0.02, L.QY - hd + 0.015, L.QY + hd - 0.015, ZT, z0 + 0.001)
        parts.append(ft)
    else:
        g.box(bd, L.QX - hw, L.QX + hw, L.QY - hd, L.QY + hd, ZT, zt)
    parts.append(bd)
    fr_front = g.Frame((0.0, L.Q_YF + 0.0005, 0.0), (1, 0, 0), (0, 0, 1), (0, -1, 0))
    fp = P("radio_front", "radio_front")
    depth = L.Q_YF + 0.0005 - L.Q_PANEL
    if lod == 0:
        G.slab(fp, L.QX - 0.142, L.QX + 0.142, z0 + 0.012, z0 + 0.228, 0.0, depth, rc=0.008, nc=2, re=0.0012, ne=1,
               frame=fr_front)
    else:
        g.box(fp, L.QX - 0.142, L.QX + 0.142, L.Q_PANEL, L.Q_YF, z0 + 0.012, z0 + 0.228)
    parts.append(fp)
    (cx, cz), (w, h) = L.SCALE_C, L.SCALE_S
    sc = P("radio_scale", "scale", group=SEL_SCREEN)
    ys = L.SCALE_Y if lod < 2 else L.Q_PANEL - 0.001
    vs = [sc.bm.verts.new((xx, ys, zz)) for xx, zz in ((cx - w / 2, cz - h / 2), (cx + w / 2, cz - h / 2),
                                                        (cx + w / 2, cz + h / 2), (cx - w / 2, cz + h / 2))]
    G.face(sc, vs, (0, -1, 0))
    parts.append(sc)
    if lod == 2:
        return parts
    nd = P("radio_needle", "needle", group=SEL_NEEDLE)
    g.box(nd, L.NEEDLE_X0 - 0.0008, L.NEEDLE_X0 + 0.0008, ys - 0.0013, ys - 0.0006, cz - h / 2 + 0.003, cz + h / 2 - 0.003)
    parts.append(nd)
    if lod == 0:
        bz = P("radio_bezel", "chrome")
        e = 0.004
        for xa, xb, za, zb in ((cx - w / 2 - e, cx + w / 2 + e, cz - h / 2 - e, cz - h / 2),
                               (cx - w / 2 - e, cx + w / 2 + e, cz + h / 2, cz + h / 2 + e),
                               (cx - w / 2 - e, cx - w / 2, cz - h / 2, cz + h / 2),
                               (cx + w / 2, cx + w / 2 + e, cz - h / 2, cz + h / 2)):
            g.box(bz, xa, xb, ys - 0.003, L.Q_PANEL + 0.0002, za, zb)
        parts.append(bz)
        gl = P("radio_glass", "glass", section="glass")
        vs = [gl.bm.verts.new((xx, ys - 0.0024, zz)) for xx, zz in ((cx - w / 2, cz - h / 2), (cx + w / 2, cz - h / 2),
                                                                    (cx + w / 2, cz + h / 2), (cx - w / 2, cz + h / 2))]
        G.face(gl, vs, (0, -1, 0))
        parts.append(gl)
    # knobs: volume and tuning (bone ozl_knob, turns with the needle)
    for dx, grp in ((0.062, "body"), (0.100, SEL_KNOB)):
        kn = P("radio_knob_t" if grp == SEL_KNOB else "radio_knob_v", "knob", group=grp)
        c = (L.QX + dx, KNOB_T[1], zt)
        if lod == 0:
            G.lathe(kn, [(0.0172, 0.0), (0.0172, 0.0032), (0.0158, 0.0042)], 12, c)
            G.ribbed(kn, c, "z", 0.0148, 0.0137, 0.0042, 0.0165, 12, top=False)
            G.lathe(kn, [(0.0144, 0.0165), (0.0118, 0.019), (0.0, 0.0195)], 12, c)
            if grp == SEL_KNOB:
                use(kn, "mark")
                g.box(kn, c[0] - 0.0011, c[0] + 0.0011, c[1] - 0.0115, c[1] - 0.003, zt + 0.0188, zt + 0.0198)
        else:
            g.cyl(kn, (c[0], c[1], zt + 0.008), "z", 0.016, 0.016, 6)
        parts.append(kn)
    if lod == 0:
        pk = P("radio_keys", "key_cream")
        for k in range(5):
            xk = L.QX - 0.118 + k * 0.0165
            hk = 0.0035 if k == 2 else 0.0075
            G.keycap(pk, g.Frame((xk, KNOB_T[1], zt - 0.001), (1, 0, 0), (0, 1, 0), (0, 0, 1)), 0.0, 0.0, 0.0125, 0.032,
                     hk, top=0.86)
        parts.append(pk)
    # handle on two brackets, folded back
    mt = P("radio_mounts", "mount")
    for s in (-1, 1):
        g.box(mt, L.QX + s * 0.118 - 0.008, L.QX + s * 0.118 + 0.008, L.QY + 0.024, L.QY + 0.040, zt - 0.002, zt + 0.011,
              **bev(0.002, lod))
    parts.append(mt)
    ch = P("radio_handle", "chrome")
    hp = [(L.QX - 0.118, L.QY + 0.032, zt + 0.007), (L.QX - 0.108, L.QY + 0.034, zt + 0.015),
          (L.QX, L.QY + 0.036, zt + 0.017), (L.QX + 0.108, L.QY + 0.034, zt + 0.015), (L.QX + 0.118, L.QY + 0.032, zt + 0.007)]
    g.pipe(ch, G.spline(hp, 3) if lod == 0 else hp, 0.004, 5 if lod == 0 else 3)
    parts.append(ch)
    # antenna: a swivel base, five sections with sleeves, a ball at the end
    an = P("radio_antenna", "chrome")
    base = Vector((L.QX - 0.138, L.QY + 0.030, zt + 0.010))
    d = Vector((-0.30, 0.18, 0.94)).normalized()
    s = 0.0
    for k, (r, ln) in enumerate(((0.0045, 0.115), (0.0039, 0.110), (0.0033, 0.105), (0.0027, 0.100), (0.0021, 0.095))):
        a0, a1 = base + d * s, base + d * (s + ln)
        g.pipe(an, [tuple(a0), tuple(a1)], r, 6 if lod == 0 else 3)
        if lod == 0 and k < 4:
            g.pipe(an, [tuple(a1 - d * 0.005), tuple(a1 + d * 0.001)], r + 0.0007, 6)
        s += ln - 0.012
    tip = base + d * (s + 0.012)
    if lod == 0:
        G.lathe(an, [(0.0, -0.004), (0.003, -0.003), (0.004, 0.0), (0.003, 0.003), (0.0, 0.004)], 8, tuple(tip), d)
        am = P("radio_antenna_mount", "mount")
        G.lathe(am, [(0.0085, 0.0), (0.0085, 0.006), (0.006, 0.0105), (0.0, 0.011)], 10, (base.x, base.y, zt - 0.001))
        parts.append(am)
    parts.append(an)
    return parts


# =============================================================================
# On the counter: mugs, ashtray, pack
# =============================================================================
def cig_pack(part, fr, Lp, W, H):
    """A "Chernomorka" pack lying face up in system fr (u along the pack, v across, n up): a box, each
    face has UV onto its own piece of the vanilla texture (CIGS_UV); from M16 and M13."""
    bm = part.bm
    uvl = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    hl, hw = Lp / 2, W / 2
    sides = [
        ([(a, b, H) for a, b in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))], (0, 0, 1), "front",
         lambda a, b, c: ((hw - b) / W, (a + hl) / Lp)),
        ([(a, b, 0.0) for a, b in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))], (0, 0, -1), "front",
         lambda a, b, c: ((b + hw) / W, (a + hl) / Lp)),
        ([(a, -hw, c) for a, c in ((-hl, 0.0), (hl, 0.0), (hl, H), (-hl, H))], (0, -1, 0), "side",
         lambda a, b, c: (c / H, (a + hl) / Lp)),
        ([(a, hw, c) for a, c in ((-hl, 0.0), (hl, 0.0), (hl, H), (-hl, H))], (0, 1, 0), "side",
         lambda a, b, c: (1.0 - c / H, (a + hl) / Lp)),
        ([(-hl, b, c) for b, c in ((-hw, 0.0), (hw, 0.0), (hw, H), (-hw, H))], (-1, 0, 0), "end",
         lambda a, b, c: ((b + hw) / W, c / H)),
        ([(hl, b, c) for b, c in ((-hw, 0.0), (hw, 0.0), (hw, H), (-hw, H))], (1, 0, 0), "end",
         lambda a, b, c: ((hw - b) / W, c / H)),
    ]
    for corners, nrm, rect, st in sides:
        vs = [bm.verts.new(fr.p(*q)) for q in corners]
        loc = {v: q for v, q in zip(vs, corners)}
        f = G.face(part, vs, fr.u * nrm[0] + fr.v * nrm[1] + fr.n * nrm[2])
        x0, x1, y0, y1 = CIGS_UV[rect]
        for lp in f.loops:
            s, t = st(*loc[lp.vert])
            lp[uvl].uv = (x0 + (x1 - x0) * s, 1.0 - (y1 - (y1 - y0) * t))


def build_counter_props(spec):
    """Mugs with beer and an empty one, a stamped ashtray with three rests (butts, ash, a half-smoked
    cigarette on a rest), a "Chernomorka" pack."""
    lod = spec["lod"]
    parts = []
    br = P("mugs_beer", "beer")
    if lod == 2:
        for x, y, _, beer in L.MUGS_TOP:
            if beer:
                g.cyl(br, (x, y, ZT + 0.07), "z", 0.04, 0.14, 4)
        return [br]
    mg = P("mugs_top", "glass", section="glass")
    fm = P("mugs_foam", "foam")
    for x, y, ang, beer in L.MUGS_TOP:
        mug(mg, x, y, ZT, ang, br if beer else None, fm if beer else None, lod=lod)
    parts += [mg, br, fm]
    ax, ay = L.ASHTRAY
    at = P("ashtray", "ashtray")
    if lod == 0:
        n = 15
        rings = G.lathe(at, [(0.0, 0.0), (0.047, 0.0), (0.051, 0.004), (0.052, 0.021), (0.0505, 0.0255), (0.048, 0.024),
                             (0.0465, 0.008), (0.0435, 0.0065), (0.0, 0.0065)], n, (ax, ay, ZT), phase=-math.pi / 2)
        # three rests for a cigarette: the rim is pressed in (the first faces the player, under the half-smoked cigarette)
        for i in (3, 4, 5):
            for k, v in enumerate(rings[i]):
                for c in (0, 5, 10):
                    dk = min(abs(k - c), n - abs(k - c))
                    if dk <= 1:
                        v.co.z -= 0.0075 * (1.0 if dk == 0 else 0.35) * (1.0 if i != 3 else 0.6)
        ash = P("ash", "ash")
        rnd = random.Random(66)
        lumps = [rnd.uniform(-1, 1) for _ in range(60)]
        G.lathe(ash, [(0.0, 0.0115), (0.022, 0.011), (0.040, 0.0088), (0.0445, 0.0072)], 12, (ax, ay, ZT),
                rad=lambda k, i: 1.0 + 0.06 * lumps[(k * 5 + i * 7) % 60])
        bt = P("butts", "butt")
        pp = P("butt_tips", "butt_paper")
        for dx, dy, deg, ln in ((-0.014, 0.012, 20.0, 0.018), (0.012, -0.016, 110.0, 0.014), (0.018, 0.014, 60.0, 0.02)):
            a = math.radians(deg)
            e = Vector((math.cos(a), math.sin(a), 0.0))
            c = Vector((ax + dx, ay + dy, ZT + 0.0145))
            g.pipe(bt, [tuple(c - e * 0.012), tuple(c)], 0.0039, 6)
            g.pipe(pp, [tuple(c), tuple(c + e * ln + Vector((0, 0, -0.001)))], 0.0037, 6)
        # half-smoked cigarette on the rest toward the player
        a = math.radians(-90.0)
        e = Vector((math.cos(a), math.sin(a), 0.0))
        c0 = Vector((ax, ay, ZT + 0.0125)) + e * 0.008
        c1 = c0 + e * 0.034 + Vector((0, 0, 0.006))
        g.pipe(pp, [tuple(c0), tuple(c1)], 0.0039, 6)
        g.pipe(bt, [tuple(c1), tuple(c1 + (c1 - c0).normalized() * 0.02)], 0.004, 6)
        parts += [ash, bt, pp]
        # "Chernomorka" pack by the ashtray
        pk = P("cig_pack", "carton", section="cigs")
        pk.fixed_uv = True
        pk.bm.loops.layers.uv.new("UVMap")
        px_, py_, pdeg = PACK_AT
        a = math.radians(pdeg)
        cig_pack(pk, g.Frame((px_, py_, ZT), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1)),
                 *PACK)
        parts.append(pk)
    else:
        g.cyl(at, (ax, ay, ZT + 0.012), "z", 0.051, 0.024, 6)
    parts.append(at)
    return parts


def build_lod(spec):
    parts = build_top(spec) + build_front(spec) + build_sides(spec) + build_inside(spec) + build_footrail(spec)
    parts += build_bay_left(spec) + build_bay_mid(spec) + build_bay_right(spec)
    parts += build_register(spec) + build_tray(spec) + build_radio(spec) + build_counter_props(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """One convex part - the counter with the footrail; the register, the radio and the props have no collision."""
    wood = kx.PEN + r"\wood.rvmat"
    body = kx.box_pts(X0, X1, RAIL_Y - RAIL_R, YT1, 0.0, ZT)
    comps = [(body, wood)]
    zn = L.SCALE_C[1]
    yd = L.REG_YF + 0.024
    memory = {
        "invView": [(0.0, -3.4, 1.5)],
        "ce_center": [(0.0, 0.0, 0.6)],
        "ce_radius": [(1.2, 0.0, 0.6)],
        # bone axes: one meter along the travel - offset in meters
        "ozl_needle_axis": [(L.NEEDLE_X0, L.SCALE_Y, zn), (L.NEEDLE_X0 + 1.0, L.SCALE_Y, zn)],
        "ozl_knob_axis": [(KNOB_T[0], KNOB_T[1], ZT + L.Q_FEET + L.Q_H), (KNOB_T[0], KNOB_T[1], ZT + L.Q_FEET + L.Q_H + 0.02)],
        "ozl_drawer_axis": [(L.RX, yd, ZT + L.REG_ZD / 2), (L.RX, yd + 1.0, ZT + L.REG_ZD / 2)],
    }
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 120.0, memory, bbox


# the first ones are for the --look preview (and the "working" look): the counter from the player side
# close up (display, lamp, radio), the register from the bartender side (keyboard, cashier display,
# drawer), overall, the bartender side, shelves, the radio
SHOTS = [
    ("counter", (0.05, -1.30, 1.78), (-0.05, 0.02, 1.20), 28),
    ("register", (0.66, 0.98, 1.64), (0.27, 0.13, 1.25), 34),
    ("front", (-1.7, -3.4, 1.9), (0.0, 0.0, 0.75), 30),
    ("bar", (1.4, 2.9, 1.5), (0.0, 0.0, 0.6), 30),
    ("shelves", (-0.25, 1.55, 0.85), (-0.30, 0.10, 0.50), 30),
    ("radio", (-0.36, -0.78, 1.45), (-0.57, 0.04, 1.24), 38),
    ("side", (3.0, -1.4, 1.4), (0.0, 0.0, 0.7), 30),
    ("drawer", (0.50, 0.80, 1.32), (0.30, 0.26, 1.16), 40),
]

M.look_shots = (6, 2)
M.run(build_lod, collision, SHOTS, row_step=2.6, row_shot=((2.6, -9.5, 2.4), (2.6, 0, 0.6)))
