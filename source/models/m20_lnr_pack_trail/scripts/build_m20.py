"""M20 - map cabinet: Trail Sample-Prep Station of the Neutrals (OZL_Lnr_Pack_Trail).
Packer: cargo 10x10, three module places (module_1..3) and module proxies in the same places. Each
module of the "Trails" line has its own slot and place where it is used: slot 1 - PDA reader M78 on the
top shelf by the box; slot 2 - radio scanner M79 on the middle shelf at the left; slot 3 - tablet with
maps M80 on the middle shelf in the centre, the map facing out. Empty slot 1 - a box and a cable with a
DE-9 connector hanging from the shelf; empty slots 2 and 3 - a shelf with a device trace in the dust
(map rolls behind).

    blender --background --python build_m20.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: system Python make_decals.py (the map on the side, the crack, the tag).

Look: the "dayz" look (matte, dirtier, coloured AO); the wood is own lacquered (m20_mats.build_lacquer):
a higher-contrast pattern, lacquer worn by hands on the edges and where hands take hold, clean device
traces on the shelves. The body is slabs with rounded visible edges, light worn ends, screw plugs on the
sides, angles on screws, a tag with a punched number, a patch on nails over the crack. The props are
detailed: rolls with a hollow end, rubber bands and string, "Delo" case-file folders with papers and
labels on the spines, stacks of exercise books, an open box with flaps, jars with bolts (hexagonal
heads), markers. Small things are vanilla DayZ items as proxies (kvanilla): a globe on the cabinet (a
school desk globe, Desk_Globe), folded Chernarus maps, a compass, a sheet of paper and a pen under the
lamp, cassettes by the scanner, a flashlight and insulating tape on the exercise books.
Work look: an inspection lamp on a nail of the right side (as in M11: PL - a ribbed rubber handle, a
bulb in a wire cage, a hook) lights the middle shelf - ozl_lamp, atlas _on.

The device is an open wooden cabinet for teaching aids from a school classroom (look-alikes: classrooms
of a school in Pripyat (Wikimedia Commons "Pripyat Abandoned School.jpg"): open cabinets of lacquered
wood, light edges, a brown back wall, a divider, four tiers; tall open racks in the same photos).
Sizes: no datasheet of a Soviet cabinet was found (only modern ones). The limits are GOST 18666-95
"Cabinets for teaching aids. Functional dimensions", tables 1-2: section width 450-1350 mm, depth
200-600, the lower zone not lower than 80 mm from the floor, 350-500 mm between shelves for folders and
large-format books. Within them - 0.95 x 1.8 x 0.45 m: plinth 80 mm, four tiers of 405 mm, slabs
22 mm, shelves 20 mm, the back wall is 4 mm fibreboard in a rebate.
Props: "Delo" folder 240 x 320 mm, general notebook 170 x 205 mm, 0.5 l jar dia. 90 x 130, map roll
dia. 60-70; the inspection lamp as in M11 (handle dia. 35, cage dia. ~75); DE-9 connector with a
31 x 16 x 42 mm body.

Blender axes: X is width, Y is depth (face toward -Y), Z is up.
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
import layout as L  # noqa: E402
import m20_geo as G  # noqa: E402
import m20_mats as MM  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
X0, X1, Y0, Y1 = L.X0, L.X1, L.Y0, L.Y1                     # body 950 x 450
H = 1.80
T = 0.022                                                   # sides and roof
TS = 0.020                                                  # shelves
XI0, XI1 = X0 + T, X1 - T                                   # inside
ZB = 0.080                                                  # plinth
ZTOP = H - T                                                # underside of the roof
SY0, SY1 = Y0 + 0.006, Y1 - 0.010                           # shelves: face recessed 6 mm, board behind
BACK = (Y1 - 0.009, Y1 - 0.005)                             # 4 mm fibreboard in a rebate
# top of the shelves by tier: bottom, three shelves (tiers of 405 mm)
Z1, Z2, Z3, Z4 = ZB + TS, 0.525, 0.950, 1.375
SHELVES = (Z2, Z3, Z4)
DIV = 0.009                                                 # half thickness of the divider
MAP_Y0, MAP_Y1, MAP_Z0, MAP_Z1 = L.MAP
EPS = 1e-6

# slots (the proxy point = the module model origin, no rotation: modules face the person): 1 - M78 on the
# top shelf; 2 - M79 on the middle shelf at the left; 3 - M80 in the centre
S1, S2, S3 = (0.25, -0.135, Z4), (-0.245, -0.075, Z3), (0.0, -0.075, Z3)
MODS = [S1, S2, S3]
MOD_OBJ = [("m78_pda_reader", "ozr_pda_reader"), ("m79_radio_scanner", "ozr_radio_scanner"),
           ("m80_map_board", "ozr_map_board")]
# device trace in the dust - the module footprint from the slot point
# (x0, x1, y0, y1; the module MLOD extent without cables)
FOOT = [(-0.09, 0.09, -0.075, 0.075), (-0.072, 0.072, -0.105, 0.10), (-0.10, 0.10, -0.10, 0.09)]
CLEAN = [(s[0] + a, s[0] + b, s[1] + c, s[1] + d, s[2] - 0.002, s[2] + 0.002) for s, (a, b, c, d) in zip(MODS, FOOT)]
# inspection lamp on a nail of the right side, in the middle tier at
# the face: a hook on the nail, a cage, the handle down
LX, LY = XI1 - 0.048, -0.150
NAIL = (XI1, LY, 1.322)
LC = Vector((LX, LY, 1.222))                                # centre of the cage
LR, LHALF = 0.038, 0.06                                     # cage radius, half height
GRIP_Z = LC.z - LHALF + 0.012                               # top of the handle (bottom of the socket)
GROM_LAMP = (XI1 - 0.028, Z3 + 0.022)                       # inlet of the lamp cable in the back wall
GROM_SER = (0.125, Z4 + 0.022)                              # inlet of the slot 1 cable
SER_X = 0.146                                               # slot 1 cable on the shelf (between books and M78)
DB = (0.032, 0.016, 0.042)                                  # DE-9 connector body: width, thickness, height

LOD_SPECS = [
    dict(lod=0, sides=12),
    dict(lod=1, sides=6),
    dict(lod=2, sides=4),
]

REGIONS = {
    "wood_side": ("wood_side", 0.6), "wood_top": ("wood_top", 0.6), "wood_shelf": ("wood_shelf", 0.7),
    "wood_div": ("wood_div", 0.6), "edge_v": ("edge_v", 1.2), "edge_h": ("edge_h", 1.2), "back": ("back", 0.45),
    "back_out": ("back", 0.12), "plinth": ("plinth", 0.6), "patch": ("patch", 1.0), "steel": ("bracket", 2.0),
    "screw": ("screw", 2.0), "cap": ("cap", 2.0), "tag": ("tag", 6.0), "nail": ("nail", 2.0), "grommet": ("rubber", 2.0),
    "roll": ("roll", 0.55), "roll_blue": ("roll_blue", 0.55), "roll_old": ("roll_old", 0.55),
    "roll_end": ("roll_end", 1.0), "hole": ("dark", 0.4), "band": ("band", 1.2), "string": ("string", 1.2),
    "folder": ("folder", 1.0), "folder_blue": ("folder_blue", 1.0), "folder_red": ("folder_red", 1.0),
    "folder_black": ("folder_black", 1.0), "label": ("label", 2.0),
    "nb_blue": ("nb_blue", 1.5), "nb_brown": ("nb_brown", 1.5), "nb_red": ("nb_red", 1.5), "pages": ("pages", 1.5),
    "carton": ("carton", 0.8), "carton_in": ("carton_in", 0.8), "tape": ("tape", 1.5),
    "glass_jar": ("steel", 1.0), "bolts": ("bolts", 3.0), "bolt_heap": ("bolt_heap", 2.0), "lid": ("lid", 3.0),
    "marker": ("plastic_white", 3.0), "cap_red": ("cap_red", 3.0), "cap_blue": ("cap_blue", 3.0), "black": ("black", 2.0),
    "dark": ("dark", 1.0),
    "bulb": ("bulb", 3.0), "cage": ("cage", 1.2), "lamp_grip": ("lamp_grip", 1.4), "socket": ("socket", 2.0),
    "cable_black": ("cable_black", 1.0), "cable_grey": ("cable_grey", 1.0), "db_hood": ("db_hood", 3.0),
    "db_shell": ("db_shell", 3.0),
    "map": ("map", 2.2), "tack": ("tack", 3.0),
}


def R(name):
    """Region for Part.use / G.retag: (name, kind, scale)."""
    return (name,) + REGIONS[name]


# =============================================================================
# Materials
# =============================================================================
def decal(name, ax, sign, uv, center, size, rng=None):
    return (os.path.join(WORK, name), ax, sign, uv, center, size, rng)


KINDS = kmats.std_kinds(floor_z=0.0)
FLAT = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# brown lacquered wood (Neutrals): dark lacquer, edges and places under hands worn to light wood
LAC = kmats.lin((106, 64, 40))
WOOD = dict(color=LAC, gloss=0.40, spec=0.28, dust=0.35, grime=0.5, rings=0.65, knots=0.25, figure=0.55, tone=0.20)
EDGE = kmats.lin((142, 106, 74))
# where hands take hold: side edges at hand height, the middle of shelf edges, the front of the middle shelf
# (modules are put and taken there) and the M78 place on the top one
RUB_V = [((x, Y0, 1.10), (0.05, 0.06, 0.42), 0.42) for x in (X0 + T / 2, X1 - T / 2)]
RUB_H = [((0.0, SY0, z), (0.36, 0.05, 0.05), 0.45) for z in (Z2, Z3, Z4)] + [((0.0, Y0, H), (0.45, 0.05, 0.05), 0.30)]
RUB_TOP = [((0.0, SY0 + 0.05, Z3), (0.42, 0.09, 0.02), 0.30), ((S1[0], SY0 + 0.04, Z4), (0.14, 0.07, 0.02), 0.25)]
CRACK = decal("decal_crack.png", "x", 1, ("y", "z"), ((L.CRACK[0] + L.CRACK[1]) / 2, (L.CRACK[2] + L.CRACK[3]) / 2),
              (L.CRACK[1] - L.CRACK[0], L.CRACK[3] - L.CRACK[2]), (X1 - 0.002, X1 + 0.002))
TAGD = decal("decal_tag.png", "x", -1, ("y", "z"), ((L.TAG[0] + L.TAG[1]) / 2, (L.TAG[2] + L.TAG[3]) / 2),
             (L.TAG[1] - L.TAG[0], L.TAG[3] - L.TAG[2]), (X0 - 0.0025, X0 - 0.0005))
KINDS.update({
    "wood_side": (MM.build_lacquer, dict(WOOD, seed=1.7, along="z", rub=RUB_V, decal_items=[CRACK])),
    "wood_top": (MM.build_lacquer, dict(WOOD, seed=2.4, along="x", dust=0.55)),
    "wood_shelf": (MM.build_lacquer, dict(WOOD, seed=3.3, along="x", rub=RUB_TOP, clean=CLEAN)),
    "wood_div": (MM.build_lacquer, dict(WOOD, seed=4.1, along="z")),
    # slab ends: lacquer worn by hands to light wood, the end is lighter than the face
    "edge_v": (MM.build_lacquer, dict(WOOD, color=EDGE, seed=5.2, along="z", rub=RUB_V, wear=(0.60, 0.68), edge_k=0.9,
                                      rings=0.3, figure=0.25)),
    "edge_h": (MM.build_lacquer, dict(WOOD, color=EDGE, seed=5.8, along="x", rub=RUB_H, wear=(0.60, 0.68), edge_k=0.9,
                                      rings=0.3, figure=0.25)),
    "plinth": (MM.build_lacquer, dict(WOOD, color=kmats.lin((70, 44, 30)), seed=6.6, along="x", dust=0.2, grime=1.0)),
    # back wall: fibreboard, smooth side inward, lighter than the lacquer - the shelves read
    "back": ("plastic", dict(color=kmats.lin((166, 130, 90)), gloss=0.12, spec=0.06, mottle=0.16, dust=0.3, grime=0.35,
                             scuff=(0.85, 0.95))),
    # plywood patch: light, unlacquered
    "patch": (MM.build_lacquer, dict(color=kmats.lin((176, 140, 96)), seed=6.6, along="z", gloss=0.12, spec=0.06,
                                     rings=0.5, knots=0.4, figure=0.2, tone=0.12, dust=0.3, grime=0.5)),
    "bracket": ("steel", dict(seed=4.2, tone=0.26, along="x", gloss=0.4, spec=0.45, dust=0.3, grime=0.4)),
    "screw": ("steel", dict(seed=4.6, tone=0.20, along="z", gloss=0.35, spec=0.4, dust=0.2, grime=0.5)),
    "cap": ("plastic", dict(color=kmats.lin((76, 50, 34)), gloss=0.35, spec=0.2, dust=0.3)),
    "tag": ("paint", dict(FLAT, color=kmats.lin((176, 178, 176)), gloss=0.45, spec=0.5, dust=0.15, decal_items=[TAGD])),
    "nail": ("steel", dict(seed=6.1, tone=0.20, along="z", gloss=0.35, spec=0.4, dust=0.2, grime=0.5)),
    "roll": ("plastic", dict(color=kmats.lin((222, 214, 188)), gloss=0.1, spec=0.05, mottle=0.10, dust=0.45)),
    "roll_blue": ("plastic", dict(color=kmats.lin((168, 186, 200)), gloss=0.1, spec=0.05, mottle=0.12, dust=0.45)),
    "roll_old": ("plastic", dict(color=kmats.lin((196, 176, 132)), gloss=0.08, spec=0.05, mottle=0.18, dust=0.5,
                                 grime=0.4)),
    # roll end: paper layers - darker, with shadow between turns
    "roll_end": ("plastic", dict(color=kmats.lin((176, 166, 138)), gloss=0.06, spec=0.04, mottle=0.25, dust=0.2,
                                 grime=0.6, scuff=(0.9, 1.0))),
    "band": ("plastic", dict(color=kmats.lin((150, 74, 46)), gloss=0.25, spec=0.15, dust=0.3)),
    "string": ("plastic", dict(color=kmats.lin((168, 146, 104)), gloss=0.06, spec=0.04, mottle=0.2, dust=0.3)),
    # "Delo" folders: cardboard, blue and burgundy cloth, black leatherette; labels on the spines are blank
    "folder": ("plastic", dict(color=kmats.lin((180, 164, 128)), gloss=0.08, spec=0.05, mottle=0.15, dust=0.4,
                               scuff=(0.58, 0.68))),
    "folder_blue": ("plastic", dict(color=kmats.lin((52, 66, 104)), gloss=0.2, spec=0.1, mottle=0.12, dust=0.4,
                                    scuff=(0.56, 0.66))),
    "folder_red": ("plastic", dict(color=kmats.lin((118, 44, 36)), gloss=0.2, spec=0.1, mottle=0.12, dust=0.4,
                                   scuff=(0.56, 0.66))),
    "folder_black": ("plastic", dict(color=kmats.lin((34, 32, 30)), gloss=0.35, spec=0.2, dust=0.4,
                                     scuff=(0.56, 0.66))),
    "label": ("plastic", dict(color=kmats.lin((222, 216, 196)), gloss=0.08, spec=0.05, mottle=0.12, dust=0.25,
                              grime=0.3)),
    "nb_blue": ("plastic", dict(color=kmats.lin((44, 60, 96)), gloss=0.3, spec=0.2, dust=0.3, scuff=(0.58, 0.68))),
    "nb_brown": ("plastic", dict(color=kmats.lin((96, 64, 40)), gloss=0.3, spec=0.2, dust=0.3, scuff=(0.58, 0.68))),
    "nb_red": ("plastic", dict(color=kmats.lin((140, 52, 40)), gloss=0.3, spec=0.2, dust=0.3, scuff=(0.58, 0.68))),
    "pages": ("plastic", dict(color=kmats.lin((214, 206, 182)), gloss=0.05, spec=0.03, mottle=0.1, dust=0.3)),
    "carton": ("plastic", dict(color=kmats.lin((150, 112, 72)), gloss=0.08, spec=0.05, mottle=0.18, dust=0.5,
                               grime=0.5, scuff=(0.60, 0.70))),
    "carton_in": ("plastic", dict(color=kmats.lin((126, 94, 62)), gloss=0.06, spec=0.04, mottle=0.2, dust=0.3,
                                  grime=0.6)),
    "tape": ("plastic", dict(color=kmats.lin((176, 150, 104)), gloss=0.55, spec=0.35, mottle=0.1, dust=0.3)),
    "bolts": ("paint", dict(color=kmats.lin((96, 94, 90)), under=kmats.lin((112, 62, 30)), seed=7.7, gloss=0.35,
                            spec=0.4, chip=(0.48, 0.56), rust=(0.45, 0.55), rust_low=0.0, floor_z=0.0, dust=0.1,
                            grime=0.3)),
    # heap of small fasteners under the bolts: washers and nuts - mixed, rusty
    "bolt_heap": ("paint", dict(color=kmats.lin((86, 84, 80)), under=kmats.lin((104, 58, 30)), seed=7.9, gloss=0.3,
                                spec=0.35, chip=(0.40, 0.50), rust=(0.40, 0.52), rust_low=0.0, floor_z=0.0, dust=0.1,
                                grime=0.5)),
    "lid": ("paint", dict(color=kmats.lin((176, 150, 86)), under=kmats.lin((150, 150, 146)), seed=8.1, gloss=0.55,
                          spec=0.5, chip=(0.58, 0.64), rust=(0.66, 0.74), rust_low=0.0, floor_z=0.0, dust=0.25,
                          grime=0.3)),
    "cap_blue": ("plastic", dict(color=kmats.lin((40, 64, 150)), gloss=0.4, spec=0.3)),
    "dark": ("flat", dict(color=kmats.lin((22, 18, 16)), gloss=0.2, spec=0.1)),
    # inspection lamp: the bulb "off" is frosted glass, "work" is a warm glow (atlas _on)
    "bulb": ("flat", dict(color=kmats.lin((196, 192, 176)), gloss=0.8, spec=0.7)),
    "bulb_on": ("flat", dict(color=kmats.lin((255, 222, 150)), gloss=0.8, spec=0.7)),
    "cage": ("steel", dict(seed=7.4, tone=0.30, along="z", gloss=0.45, spec=0.5, dust=0.2, grime=0.3)),
    "lamp_grip": ("plastic", dict(color=kmats.lin((28, 28, 28)), gloss=0.15, spec=0.08, dust=0.3, grime=0.4,
                                  scuff=(0.8, 0.9))),
    "socket": ("steel", dict(seed=7.6, tone=0.32, along="z", gloss=0.4, spec=0.45, dust=0.2, grime=0.4)),
    "cable_black": ("plastic", dict(color=kmats.lin((26, 26, 28)), gloss=0.3, spec=0.2, dust=0.35, grime=0.3)),
    "cable_grey": ("plastic", dict(color=kmats.lin((150, 148, 140)), gloss=0.3, spec=0.2, dust=0.35, grime=0.4)),
    "db_hood": ("plastic", dict(color=kmats.lin((156, 150, 136)), gloss=0.35, spec=0.25, dust=0.3, grime=0.4,
                                scuff=(0.66, 0.74))),
    "db_shell": ("steel", dict(seed=8.8, tone=0.40, along="x", gloss=0.5, spec=0.55, dust=0.1, grime=0.3)),
    "map": ("paint", dict(FLAT, color=kmats.lin((226, 222, 200)), gloss=0.15, spec=0.08, dust=0.2,
                          decal_items=[decal("decal_map.png", "x", 1, ("y", "z"),
                                             ((MAP_Y0 + MAP_Y1) / 2, (MAP_Z0 + MAP_Z1) / 2),
                                             (MAP_Y1 - MAP_Y0, MAP_Z1 - MAP_Z0))])),
    "tack": ("paint", dict(FLAT, color=kmats.lin((168, 140, 72)), gloss=0.6, spec=0.6, dust=0.2)),
})

OBJ, NAME = "m20_lnr_pack_trail", "ozr_lnr_pack_trail"
# Work look: the lamp bulb is ozl_lamp (in hiddenSelections); "off" by default, "work" is the _on_co atlas
# and the _on rvmat with glow.
SEL_LAMP = "ozl_lamp"
ON = dict(remap={"bulb": "bulb_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
# module proxies: slots OZL_Tool1..3 are linked to them by the mod's CfgNonAIVehicles (Proxyozl_tool1..3)
PROXY = r"\OpenZone_Research\models\proxies\ozl_tool%d"
PROXIES = [(PROXY % (i + 1), m) for i, m in enumerate(MODS)]
# vanilla items (none has a Proxy<name> class)
GLOBE = r"dz\structures\furniture\school_equipment\Desk_Globe"
MAPDZ = r"dz\gear\navigation\Map_chernarus"
COMPASS = r"dz\gear\navigation\compass"
NB4_TOP = Z4 + 5 * 0.009                                     # top of the exercise-book stack on the top shelf
NB2 = ((0.115, -0.05, 12), (0.31, 0.05, 7))                  # stacks of the second tier: centre, how many
DECOR = [
    # on the cabinet - a school globe
    kv.put(GLOBE, (-0.25, -0.035, H), up=(0, 0, 1), fwd=(0.26, -1, 0)),
    # middle shelf at the right, under the lamp: a sheet of paper, a folded map, a compass, a pen
    kv.put("paper", (0.27, -0.078, Z3), lift=0.0004, **kv.flat(92)),
    kv.put(MAPDZ, (0.30, -0.020, Z3 + 0.0004), lift=0.0004, **kv.flat(72)),
    kv.put(COMPASS, (0.190, -0.155, Z3 + 0.0004), up=(0, 0, 1), fwd=(0, -1, 0)),
    kv.put("pen", (0.355, -0.160, Z3 + 0.0004), **kv.flat(118)),
    # middle shelf at the left, by the scanner: cassettes with air recordings
    kv.put("cassette", (-0.392, -0.130, Z3), **kv.flat(0)),
    kv.put("cassette", (-0.388, -0.126, Z3), lift=0.0102, **kv.flat(7)),
    # top shelf: a folded map on the exercise books
    kv.put(MAPDZ, (0.048, -0.112, NB4_TOP), **kv.flat(14)),
    # second tier at the right: a flashlight on a stack of exercise books, insulating tape on the second stack
    kv.put("flashlight", (NB2[0][0], NB2[0][1] - 0.01, Z2 + NB2[0][2] * 0.009), up=(0, 0, 1), fwd=(0.08, -1, 0)),
    kv.put("ducttape", (NB2[1][0] - 0.005, NB2[1][1] + 0.005, Z2 + NB2[1][2] * 0.009), **kv.flat(20)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.62, 0.66, 0.62), clear=0.10, edge=0.14, smudge=0.12, streaks=0.03),
                 selections=(SEL_LAMP,), hidden=(SEL_LAMP,), states={"on": ON}, proxies=PROXIES, decor=DECOR,
                 modules=[(o, n, m) for (o, n), m in zip(MOD_OBJ, MODS)])
P = M.part
BOUNDS = {}


def PU(name, region, origin, uv):
    """Identical small things (plug, nail, button, screw, rubber band): each its own part, and the atlas
    place is one for all with the same uv (in local coordinates from origin). As one part, small things
    scattered over the cabinet would take a rectangle of their whole span in the atlas (the kuv layout is
    by the extent of the part's faces)."""
    return M.part(name, region, uv_name=uv, uv_origin=tuple(origin))


def front_faces(fs, k=0.5):
    return [f for f in fs if f.normal.y < -k]


def is_vertical_at_y(y):
    """Face edges at depth y running up (side edge, dividers)."""
    return lambda a, b: abs(a.y - y) < EPS and abs(b.y - y) < EPS and abs(a.z - b.z) > EPS


def is_horizontal_at_y(y):
    """Face edges at depth y along x (shelf nose)."""
    return lambda a, b: abs(a.y - y) < EPS and abs(b.y - y) < EPS and abs(a.z - b.z) < EPS


# =============================================================================
# Body: slabs, edges, fasteners, lived-in details
# =============================================================================
def build_body(spec):
    lod = spec["lod"]
    rs = (0.003, 3) if lod == 0 else (0.0, 0)
    parts = []
    # sides - each its own part (in the atlas they do not overlap: different shading)
    for nm, xa, xb in (("side_l", X0, XI0), ("side_r", XI1, X1)):
        sv = P(nm, "wood_side")
        fs = G.box_bev(sv, xa, xb, Y0, Y1, 0.0, ZTOP, *rs, is_vertical_at_y(Y0))
        G.retag(sv, R("edge_v"), front_faces(fs))
        parts.append(sv)
    # roof: the top edges at the front and sides and the bottom front one are rounded
    rf = P("roof", "wood_top")
    fs = G.box_bev(rf, X0, X1, Y0, Y1, ZTOP, H, 0.004 if lod == 0 else 0.0, 3 if lod == 0 else 0,
                   lambda a, b: (abs(a.z - H) < EPS and abs(b.z - H) < EPS and not (a.y > Y1 - EPS and b.y > Y1 - EPS)) or
                   (abs(a.z - ZTOP) < EPS and abs(b.z - ZTOP) < EPS and a.y < Y0 + EPS and b.y < Y0 + EPS))
    G.retag(rf, R("edge_h"), front_faces(fs))
    parts.append(rf)
    # bottom and shelves - each its own part; the nose is rounded at the top and bottom
    for nm, z in (("bottom", Z1), ("shelf2", Z2), ("shelf3", Z3), ("shelf4", Z4)):
        sh = P(nm, "wood_shelf")
        z0 = ZB if nm == "bottom" else z - TS
        fs = G.box_bev(sh, XI0, XI1, SY0, SY1, z0, z, *rs, is_horizontal_at_y(SY0))
        G.retag(sh, R("edge_h"), front_faces(fs))
        parts.append(sh)
    # divider in the two lower tiers
    dv = P("divider", "wood_div")
    for za, zb in ((Z1, Z2 - TS), (Z2, Z3 - TS)):
        fs = G.box_bev(dv, -DIV, DIV, SY0, SY1, za, zb, *rs, is_vertical_at_y(SY0))
        G.retag(dv, R("edge_v"), front_faces(fs))
    parts.append(dv)
    bk = P("back", "back")
    fs = g.box(bk, XI0 - 0.008, XI1 + 0.008, BACK[0], BACK[1], ZB, ZTOP + 0.008)
    G.retag(bk, R("back_out"), [f for f in fs if f.normal.y > 0.5])        # back side at the wall: hardly visible
    parts.append(bk)
    pl = P("plinth", "plinth")
    G.box_bev(pl, XI0, XI1, Y0 + 0.030, Y0 + 0.048, 0.0, ZB, 0.002 if lod == 0 else 0.0, 2 if lod == 0 else 0,
              lambda a, b: abs(a.y - (Y0 + 0.030)) < EPS and abs(b.y - (Y0 + 0.030)) < EPS and abs(a.z - ZB) < EPS
              and abs(b.z - ZB) < EPS)
    parts.append(pl)
    if lod == 2:
        return parts
    # steel angles on the top corners of the face (the cabinet came loose) on three screws
    for s in (-1, 1):
        xo = X1 if s > 0 else X0
        st = PU("bracket_%d" % (s > 0), "steel", (xo, Y0, H), "bracket")
        poly = [(xo - s * 0.002, H - 0.003), (xo - s * 0.050, H - 0.003), (xo - s * 0.050, H - 0.019),
                (xo - s * 0.019, H - 0.019), (xo - s * 0.019, H - 0.070), (xo - s * 0.002, H - 0.070)]
        if s < 0:
            poly = poly[::-1]
        g.prism(st, poly, (0, 2), Y0 - 0.0022, Y0 - 0.0002)
        parts.append(st)
        if lod == 0:
            for i, (px, pz) in enumerate(((0.040, H - 0.011), (0.0105, H - 0.011), (0.0105, H - 0.056))):
                c = (xo - s * px, Y0 - 0.0022, pz)
                sc = PU("bscrew_%d_%d" % (s > 0, i), "screw", c, "bscrew")
                G.dome(sc, c, (0, -1, 0), 0.0032, 0.0016, 6)
                parts.append(sc)
    # plywood patch over the crack of the right side, on nails
    pt = P("patch", "patch")
    py0, py1, pz0, pz1 = L.PATCH
    G.box_bev(pt, X1, X1 + 0.004, py0, py1, pz0, pz1, 0.0015 if lod == 0 else 0.0, 1 if lod == 0 else 0,
              lambda a, b: abs(a.x - (X1 + 0.004)) < EPS and abs(b.x - (X1 + 0.004)) < EPS)
    parts.append(pt)
    if lod == 0:
        # shelf screw plugs on the sides (outside): at the face and at the back wall
        for z in (Z1, Z2, Z3, Z4):
            for y in (Y0 + 0.035, Y1 - 0.045):
                for x, ax in ((X0, (-1, 0, 0)), (X1, (1, 0, 0))):
                    c = (x, y, z - TS / 2)
                    cp = PU("cap_%d_%d_%d" % (round(z * 1000), y > 0, x > 0), "cap", c, "cap")
                    G.dome(cp, c, ax, 0.0058, 0.0016, 6)
                    parts.append(cp)
        heads = [((X1 + 0.004, py, pz), (1, 0, 0), 0.0028) for py in (py0 + 0.012, py1 - 0.012)
                 for pz in (pz0 + 0.015, (pz0 + pz1) / 2, pz1 - 0.015)]
        # inventory tag on the left side on two small nails, the number punched (a decal)
        tg = P("inv_tag", "tag")
        g.box(tg, X0 - 0.0015, X0, L.TAG[0], L.TAG[1], L.TAG[2], L.TAG[3])
        parts.append(tg)
        heads += [((X0 - 0.0015, ty, (L.TAG[2] + L.TAG[3]) / 2), (-1, 0, 0), 0.0022)
                  for ty in (L.TAG[0] + 0.0048, L.TAG[1] - 0.0048)]
        for i, (c, ax, r) in enumerate(heads):
            nl = PU("nail_%d" % i, "nail", c, "nail")
            G.dome(nl, c, ax, r, 0.0010, 5)
            parts.append(nl)
        # rubber bushings in the back wall: the inlet of the lamp cable and of the slot 1 cable
        for i, (gx, gz) in enumerate((GROM_LAMP, GROM_SER)):
            c = (gx, BACK[0], gz)
            gr = PU("grommet_%d" % i, "grommet", c, "grommet")
            G.lathe(gr, [(0.0085, 0.0), (0.0085, -0.002), (0.005, -0.0028), (0.0045, 0.0)], 8, c, (0, 1, 0))
            G.lathe(gr, [(0.0045, 0.0), (0.0045, 0.006)], 8, c, (0, 1, 0), cap1=True, inward=True)
            parts.append(gr)
    return parts


# =============================================================================
# Map on the side: the sheet waves slightly, pressed at the pins, the lower right corner comes off
# =============================================================================
TACKS = [(MAP_Y0 + 0.012, MAP_Z0 + 0.012), (MAP_Y1 - 0.012, MAP_Z0 + 0.012), (MAP_Y0 + 0.012, MAP_Z1 - 0.012),
         (MAP_Y1 - 0.012, MAP_Z1 - 0.012)]


def map_off(y, z):
    """Sheet lift from the side: a wave, zero at the pins, the corner at the face bottom is bent away."""
    near = min(math.hypot(y - ty, z - tz) for ty, tz in TACKS)
    w = 0.0011 * (0.5 + 0.5 * math.sin(y * 31.0 + 0.7) * math.sin(z * 23.0 + 1.9))
    w *= min(1.0, near / 0.06)
    s = max(0.0, 1.0 - math.hypot(y - MAP_Y0, z - MAP_Z0) / 0.07)
    return 0.0004 + w + 0.006 * s * s


def build_map(spec):
    lod = spec["lod"]
    mp = P("map", "map")
    if lod == 0:
        ny, nz = 6, 8
        grid = [[(X1 + L.MAP_T + map_off(MAP_Y0 + (MAP_Y1 - MAP_Y0) * i / ny, MAP_Z0 + (MAP_Z1 - MAP_Z0) * j / nz),
                  MAP_Y0 + (MAP_Y1 - MAP_Y0) * i / ny, MAP_Z0 + (MAP_Z1 - MAP_Z0) * j / nz) for j in range(nz + 1)]
                for i in range(ny + 1)]
        # grid in y and z: the face is toward +x
        G.sheet(mp, grid, 0.0005)
        mp.bm.normal_update()
    else:
        g.box(mp, X1, L.X_MAP, MAP_Y0, MAP_Y1, MAP_Z0, MAP_Z1)
    parts = [mp]
    if lod < 2:
        for i, (ty, tz) in enumerate(TACKS):
            c = (X1 + L.MAP_T + 0.0004, ty, tz)
            tk = PU("tack_%d" % i, "tack", c, "tack")
            if lod == 0:
                G.lathe(tk, [(0.0058, 0.0), (0.0058, 0.0008), (0.0045, 0.0022), (0.0, 0.0030)], 8, c, (1, 0, 0))
            else:
                g.cyl(tk, (L.X_MAP + 0.0015, ty, tz), "x", 0.0055, 0.003, 5)
            parts.append(tk)
    return parts


# =============================================================================
# Map rolls
# =============================================================================
ROLL_KINDS = ("roll", "roll_old", "roll_blue", "roll", "roll_old")


def roll_ends(tag):
    """Shared parts of the ends and holes of the roll heap (an even colour - one atlas place for all)."""
    return P(tag + "_ends", "roll_end"), P(tag + "_holes", "hole")


def tie(tag, kind, c, axis, r, sd, sq, ph, string=False):
    """Rubber band or string on a roll - its own part with a shared atlas place."""
    p = PU(tag, kind, c, kind + ("_x" if axis[0] else "_y"))
    G.band(p, c, axis, r, 0.004 if string else 0.006, sd, squash=sq, phase=ph, t=0.0016 if string else 0.0013)
    return p


def build_rolls_low(spec):
    """Lower tier at the left: a heap of 14 rolls with the ends outward; the ends slightly in disorder, some
    with a rubber band at the end, the lower ones slightly flattened. The side of each roll is its own part
    (in the atlas the sides of the heap do not overlap)."""
    lod, sd = spec["lod"], spec["sides"]
    xa, xb = XI0 + 0.004, -DIV - 0.004
    if lod > 0:
        ms = P("rolls_low_mass", "roll")
        if lod == 1:
            # middle LOD: the heap is thick cylinders in three rows
            ends = P("rolls_low_ends", "roll_end")
            for j, (cnt, xo) in enumerate(((3, 0.0), (3, 0.066), (2, 0.132))):
                for i in range(cnt):
                    r = 0.062 if j < 2 else 0.05
                    x = xa + 0.068 + xo + i * 0.132
                    z = Z1 + 0.066 + j * 0.1
                    if x + r < xb:
                        G.paper_roll((ms, ends, None), (x, SY0 + 0.01, z), (x, SY1 - 0.03, z), r, 6, ends=(True, False),
                                     simple=True)
            return [ms, ends]
        g.prism(ms, [(xa, Z1), (xb, Z1), (xb - 0.07, Z1 + 0.17), (xa + 0.07, Z1 + 0.17)], (0, 2), SY0 + 0.01,
                SY1 - 0.02)
        return [ms]
    rnd = random.Random(201)
    ends, holes = roll_ends("rolls_low")
    parts = [ends, holes]
    R0 = 0.033
    rows = [(6, 0.0), (5, R0), (3, 3 * R0)]
    k = 0
    for j, (n, xo) in enumerate(rows):
        z = Z1 + R0 + j * R0 * math.sqrt(3)
        for i in range(n):
            x = xa + R0 + 0.004 + xo + i * 2 * R0
            r = R0 - rnd.uniform(0.0, 0.004)
            sq = (0.93, 0.96, 1.0)[j]
            y0 = SY0 + rnd.uniform(-0.016, 0.03)
            y1 = min(BACK[0] - 0.004, y0 + rnd.uniform(0.34, 0.40))
            zc = z - (R0 - r) - r * (1 - sq)
            kind = ROLL_KINDS[k % 5]
            rl = P("rl_%d" % k, kind)
            ph = rnd.uniform(0, 1)
            G.paper_roll((rl, ends, holes), (x, y0, zc), (x, y1, zc), r, sd, ends=(True, False), squash=sq,
                         hole=rnd.uniform(0.30, 0.45), phase=ph)
            parts.append(rl)
            if k % 3 == 1:
                parts.append(tie("rl_band_%d" % k, "band", (x, y0 + rnd.uniform(0.04, 0.07), zc), (0, 1, 0), r, sd, sq, ph))
            k += 1
    return parts


def build_rolls_top(spec):
    """Top tier at the left: a heap of long rolls along the shelf (4 + 3 + 2), some with a rubber band or
    string near the visible end; the left ends are at the side (they are absent), the right ones are visible."""
    lod, sd = spec["lod"], spec["sides"]
    if lod == 2:
        ms = P("rolls_top_mass", "roll_old")
        g.box(ms, XI0 + 0.01, -0.06, SY0 + 0.03, SY1 - 0.03, Z4, Z4 + 0.16)
        return [ms]
    rnd = random.Random(204)
    ends, holes = roll_ends("rolls_top")
    parts = [ends] + ([holes] if lod == 0 else [])
    by_kind = {}
    R0 = 0.034
    n_side = 10 if lod == 0 else sd
    k = 0
    for j, n in enumerate((4, 3, 2)):
        z = Z4 + R0 + j * R0 * math.sqrt(3)
        for i in range(n):
            y = SY0 + 0.05 + R0 * j + i * 2 * R0 + 0.02
            ln = rnd.uniform(0.33, 0.37)
            x0 = XI0 + 0.008 + rnd.uniform(0.0, 0.02)
            r = R0 - rnd.uniform(0.0, 0.004)
            sq = (0.94, 0.97, 1.0)[j]
            zc = z - (R0 - r) - r * (1 - sq)
            kind = ROLL_KINDS[(k + 1) % 5]
            if lod == 0:
                rl = P("rt_%d" % k, kind)
                ph = rnd.uniform(0, 1)
                G.paper_roll((rl, ends, holes), (x0, y, zc), (x0 + ln, y, zc), r, n_side, ends=(False, True), squash=sq,
                             hole=rnd.uniform(0.30, 0.45), phase=ph)
                parts.append(rl)
                if k % 3 != 1:
                    string = k % 4 == 2
                    parts.append(tie("rt_tie_%d" % k, "string" if string else "band", (x0 + ln * 0.74, y, zc), (1, 0, 0),
                                     r, n_side, sq, ph, string))
            else:
                rl = by_kind.get(kind) or by_kind.setdefault(kind, P("rolls_top_" + kind, kind))
                G.paper_roll((rl, ends, None), (x0, y, zc), (x0 + ln, y, zc), r, n_side, ends=(False, True), simple=True)
            k += 1
    return parts + list(by_kind.values())


# =============================================================================
# Lower tier at the right: boxes
# =============================================================================
BOX_LO = (DIV + 0.012, DIV + 0.412, SY0 + 0.04, SY0 + 0.38, Z1, Z1 + 0.17)
BOX_UP = (BOX_LO[0] + 0.20, SY0 + 0.20, -5.0)                # centre and rotation of the upper one


def build_boxes_low(spec):
    """Lower tier at the right: a closed box taped with tape at the bottom; on it an open one - flaps folded
    back, inside a stack of papers and a roll at an angle."""
    lod = spec["lod"]
    x0, x1, y0, y1, z0, z1 = BOX_LO
    cb = P("box_lo", "carton")
    g.box(cb, x0, x1, y0, y1, z0, z1, **(dict(r=0.003, seg=1) if lod == 0 else {}))
    parts = [cb]
    fr = G.frame_z(BOX_UP[0], BOX_UP[1], BOX_UP[2], z1)
    ub = P("box_up", "carton")
    if lod == 2:
        g.box(ub, -0.17, 0.17, -0.14, 0.14, 0.0, 0.12, frame=fr)
        return parts + [ub]
    if lod == 1:
        g.box(ub, -0.17, 0.17, -0.14, 0.14, 0.0, 0.12, frame=fr)
        parts.append(ub)
        return parts
    tp = P("box_lo_tape", "tape")
    cx = (x0 + x1) / 2
    g.box(tp, cx - 0.024, cx + 0.024, y0 - 0.0008, y0, z1 - 0.07, z1 + 0.0008)
    g.box(tp, cx - 0.024, cx + 0.024, y1, y1 + 0.0008, z1 - 0.07, z1 + 0.0008)
    parts.append(tp)
    # open box: walls, flaps (the front one folded forward and down, the rear one back), papers inside
    G.open_box(ub, -0.17, 0.17, -0.14, 0.14, 0.0, 0.12, 0.003, frame=fr)
    ub.use(*R("carton_in"))
    G.flap(ub, -0.168, 0.168, -0.14, 0.12, 0.115, 155.0, 0.003, side=-1, sag=0.006, frame=fr)
    G.flap(ub, -0.168, 0.168, 0.14, 0.12, 0.10, 30.0, 0.003, side=1, sag=0.004, frame=fr)
    parts.append(ub)
    pg = P("box_up_papers", "pages")
    rnd = random.Random(205)
    for i in range(3):
        g.box(pg, -0.155 + rnd.uniform(0, 0.01), 0.150 - rnd.uniform(0, 0.01), -0.125 + rnd.uniform(0, 0.01),
              0.125 - rnd.uniform(0, 0.01), 0.003 + 0.025 * i, 0.003 + 0.025 * i + 0.024,
              frame=G.frame_z(*tuple(fr.p(rnd.uniform(-0.004, 0.004), rnd.uniform(-0.004, 0.004), 0.0))[:2],
                              BOX_UP[2] + rnd.uniform(-3, 3), z1))
    parts.append(pg)
    # roll at an angle out of the box
    rl = P("box_up_roll", "roll_blue")
    ends, holes = roll_ends("box_up_roll")
    a, b = fr.p(-0.12, 0.07, 0.02), fr.p(0.08, -0.03, 0.19)
    G.paper_roll((rl, ends, holes), a, b, 0.026, spec["sides"], ends=(False, True), hole=0.35)
    parts += [rl, ends, holes]
    return parts


# =============================================================================
# Second tier at the left: "Delo" folders
# =============================================================================
# (kind, thickness, height, sideways tilt, pulled out forward, papers stick out of the top)
FOLDERS = [("folder_black", 0.030, 0.315, -14.0, 0.0, 0.0), ("folder", 0.035, 0.31, 0.0, 0.012, 0.012),
           ("folder", 0.028, 0.31, 0.0, -0.004, 0.0), ("folder_blue", 0.040, 0.32, 0.0, 0.0, 0.008),
           ("folder", 0.022, 0.31, 0.0, 0.020, 0.0), ("folder_red", 0.034, 0.32, 0.0, 0.004, 0.014),
           ("folder", 0.030, 0.31, 0.0, -0.006, 0.0), ("folder_blue", 0.026, 0.32, 0.0, 0.010, 0.0),
           ("folder", 0.036, 0.31, 0.0, 0.0, 0.010)]


def build_folders(spec):
    """Second tier at the left: "Delo" folders with the spines outward, in disorder in depth; blank labels on
    the spines, sheets stick out of some; the end one has fallen on its side, another lies on top."""
    lod = spec["lod"]
    xa, xb = XI0 + 0.003, -DIV - 0.003
    yb, ye = SY0 + 0.02, SY0 + 0.26
    if lod > 0:
        ms = P("folders_mass", "folder")
        g.box(ms, xa + 0.08, xb - 0.02, yb, ye, Z2, Z2 + 0.31)
        if lod == 1:
            g.box(ms, xb - 0.10, xb - 0.02, yb, ye, Z2 + 0.31, Z2 + 0.33)
        return [ms]
    parts = []
    pg = P("folder_papers", "pages")
    x = xa
    last = len(FOLDERS) - 1
    for i, (kind, t, h, lean, dy, paper) in enumerate(FOLDERS):
        p = P("folder_%d" % i, kind)
        if lean:
            # fell to the left onto its side: the bottom edge at the floor on the right
            a = math.radians(-lean)
            fr = G.frame_lean(x + h * math.sin(a) + t, yb, Z2, lean)
            g.box(p, -t, 0.0, 0.0, ye - yb, 0.0, h, frame=fr, r=0.0015, seg=1)
            lc = fr.p(-t / 2, 0.0, h - 0.07)
            lb = PU("folder_label_%d" % i, "label", lc, "label")
            g.box(lb, -t * 0.8, -t * 0.2, -0.0006, 0.0, h - 0.10, h - 0.04, frame=fr)
            x = x + h * math.sin(a) + t + 0.002
        else:
            y0 = yb - dy
            fs = g.box(p, x, x + t, y0, ye - dy, Z2, Z2 + h, r=0.0015, seg=1)
            # sides pressed against neighbouring folders are not visible -
            # they have no faces (the atlas place goes to the visible ones)
            G.kill(p, [f for f in fs if (f.normal.x > 0.9 and i < last) or (f.normal.x < -0.9 and i > 1)])
            lb = PU("folder_label_%d" % i, "label", (x + t / 2, y0, Z2 + h - 0.07), "label")
            g.box(lb, x + t * 0.18, x + t * 0.82, y0 - 0.0006, y0, Z2 + h - 0.10, Z2 + h - 0.04)
            if paper:
                g.box(pg, x + 0.003, x + t - 0.003, y0 + 0.02, ye - dy - 0.03, Z2 + h - 0.02, Z2 + h + paper)
            x += t + 0.001
        parts += [p, lb]
    # a folder flat on top of the standing ones
    fl = P("folder_flat", "folder")
    g.box(fl, -0.16, 0.16, -0.12, 0.12, 0.0, 0.016, frame=G.frame_z(xb - 0.20, yb + 0.12, 6.0, Z2 + 0.322), r=0.0015, seg=1)
    return parts + [fl, pg]


# =============================================================================
# Second tier at the right: exercise books, a small box, a jar
# =============================================================================
JAR_R, JAR_H = 0.045, 0.13                                  # 0.5 l jar


def jar(spec, tag, c, z, fill, closed, seed, bolts=True):
    """0.5 l jar (dia. 90 x 130): glass (section glass) with a shoulder and a neck; inside a heap of small
    fasteners and bolts with hexagonal heads on top (bolts) or empty (the marker jar); the lid is tin,
    rolled."""
    lod = spec["lod"]
    cx, cy = c
    if lod == 2:
        bt = P(tag + "_bolts", "bolt_heap")
        g.cyl(bt, (cx, cy, z + JAR_H / 2), "z", JAR_R, JAR_H, 5)
        return [bt]
    n = 12 if lod == 0 else 6
    gl = P(tag + "_glass", "glass_jar", section="glass")
    prof = [(JAR_R - 0.005, 0.0), (JAR_R, 0.006), (JAR_R, 0.098), (JAR_R - 0.004, 0.108), (JAR_R - 0.009, 0.114),
            (JAR_R - 0.009, JAR_H - 0.004)]
    if lod > 0:
        prof = [prof[0], prof[2], prof[4], prof[5]]
    G.lathe(gl, prof, n, (cx, cy, z), cap0=True)
    parts = [gl]
    top = 0.004 + fill
    if bolts:
        bt = P(tag + "_heap", "bolt_heap")
        G.lathe(bt, [(JAR_R - 0.0045, 0.004), (JAR_R - 0.0045, top), (JAR_R * 0.6, top + 0.007), (0.0, top + 0.011)],
                n, (cx, cy, z))
        parts.append(bt)
    if lod == 0 and bolts:
        bl = P(tag + "_bolts", "bolts")
        rnd = random.Random(seed)
        for k in range(3):
            a = rnd.uniform(0, 2 * math.pi)
            rr = rnd.uniform(0.004, 0.018)
            hz = z + top + 0.009 - rr * 0.25
            b = a + math.pi + rnd.uniform(-0.9, 0.9)                 # shaft toward the middle
            G.hex_bolt(bl, (cx + rr * math.cos(a), cy + rr * math.sin(a), hz),
                       (math.cos(b), math.sin(b), rnd.uniform(-0.35, 0.05)), rnd.uniform(0.010, 0.013),
                       rnd.uniform(0.018, 0.028), lod)
        parts.append(bl)
    if closed:
        ld = P(tag + "_lid", "lid")
        lp = [(JAR_R - 0.0075, JAR_H - 0.012), (JAR_R - 0.0055, JAR_H - 0.0105), (JAR_R - 0.0055, JAR_H - 0.001),
              (JAR_R - 0.010, JAR_H + 0.0012), (0.0, JAR_H + 0.0016)]
        G.lathe(ld, lp if lod == 0 else [lp[1], lp[2], lp[4]], n, (cx, cy, z))
        parts.append(ld)
    return parts


def build_shelf2_right(spec):
    """Second tier at the right: two stacks of exercise books (a vanilla flashlight and insulating tape on
    them), a small box, a jar of bolts."""
    lod = spec["lod"]
    jar2 = jar(spec, "jar2", (XI1 - 0.050, SY0 + 0.060), Z2, 0.08, True, 22)
    if lod > 0:
        ms = P("nb2_mass", "nb_brown")
        for cx, cy, n in NB2:
            g.box(ms, cx - 0.085, cx + 0.085, cy - 0.10, cy + 0.10, Z2, Z2 + n * 0.009)
        return [ms] + jar2
    parts = []
    for i, (cx, cy, n) in enumerate(NB2):
        nb = P("nb2_%d" % i, "nb_blue")
        G.notebooks(nb, [R("nb_blue"), R("nb_brown"), R("nb_red"), R("nb_brown")], R("pages"), cx, cy, Z2, n,
                    random.Random(202 + i))
        parts.append(nb)
    cb = P("box2", "carton")
    g.box(cb, -0.06, 0.06, -0.045, 0.045, 0.0, 0.07, frame=G.frame_z(0.285, -0.158, 12.0, Z2), r=0.002, seg=1)
    parts.append(cb)
    return parts + jar2


# =============================================================================
# Middle shelf: modules M79 and M80 (slots 2 and 3), a jar of bolts, a jar of markers, rolls at the back,
# under the lamp - a sheet, a map, a compass (vanilla)
# =============================================================================
MK_JAR = (0.27, 0.135)


def build_shelf3(spec):
    lod, sd = spec["lod"], spec["sides"]
    parts = []
    # two rolls along the shelf at the back wall (behind the modules; on the right - the place of the lamp cable)
    rows = ((-0.42, 0.08, SY1 - 0.040, 0.030, "roll_blue", (True, True)),
            (-0.30, 0.14, SY1 - 0.085, 0.028, "roll", (True, True)))
    if lod < 2:
        ends, holes = roll_ends("rolls3")
        parts += [ends] + ([holes] if lod == 0 else [])
        for i, (xa, xb, y, r, kind, ee) in enumerate(rows):
            rl = P("rolls3_%d" % i, kind)
            G.paper_roll((rl, ends, holes), (xa, y, Z3 + r), (xb, y, Z3 + r), r, sd, ends=ee, simple=lod > 0)
            parts.append(rl)
            if lod == 0:
                for t in (0.2, 0.8):
                    parts.append(tie("rolls3_band_%d_%d" % (i, t * 10), "band", (xa + (xb - xa) * t, y, Z3 + r), (1, 0, 0),
                                     r, sd, 1.0, 0.0))
    else:
        rl = P("rolls3", "roll_blue")
        g.box(rl, -0.42, 0.14, SY1 - 0.12, SY1 - 0.01, Z3, Z3 + 0.06)
        parts.append(rl)
    parts += jar(spec, "jar3", (XI0 + 0.050, 0.035), Z3, 0.09, True, 33)
    # jar with markers (open) at the back right
    mx, my = MK_JAR
    parts += jar(spec, "jar3m", (mx, my), Z3, 0.0, False, 34, bolts=False)
    if lod < 2:
        mk = P("markers", "marker")
        caps = {"black": P("marker_caps_k", "black"), "cap_red": P("marker_caps_r", "cap_red"),
                "cap_blue": P("marker_caps_b", "cap_blue")}
        for k, (dx, dy, tilt, cap) in enumerate(((-0.015, -0.01, 8, "black"), (0.012, -0.014, -10, "cap_red"),
                                                  (0.0, 0.016, 5, "cap_blue"), (0.02, 0.01, -4, "black"),
                                                  (-0.018, 0.014, 12, "cap_red"))):
            a = math.radians(tilt)
            fr = g.Frame((mx + dx, my + dy, Z3 + 0.004), (math.cos(a), 0, -math.sin(a)), (0, 1, 0),
                         (math.sin(a), 0, math.cos(a)))
            n = 6 if lod == 0 else 4
            g.cyl(mk, (0, 0, 0.065), "z", 0.008, 0.13, n, frame=fr)
            g.cyl(caps[cap], (0, 0, 0.143), "z", 0.0086, 0.032, n, frame=fr)
            if lod == 0:
                # cap clip
                g.box(caps[cap], -0.0016, 0.0016, 0.0082, 0.0104, 0.132, 0.156, frame=fr)
        parts += [mk] + list(caps.values())
    return parts


# =============================================================================
# Middle shelf at the right: inspection lamp on a nail, the cable along the shelf into the back wall
# =============================================================================
def build_lamp(spec):
    """The lamp hangs on a hook (as in M11): the hook above the cage is hooked on a nail in the side, the
    cage of rings and ribs, the bulb (ozl_lamp in all LODs) in the socket, a ribbed rubber handle, from the
    handle a cable down to the shelf and along it into the back-wall bushing."""
    lod, sd = spec["lod"], spec["sides"]
    parts = []
    z0, z1 = LC.z - LHALF, LC.z + LHALF
    bl = P("lamp_bulb", "bulb", group=SEL_LAMP)
    prof = [(0.0, 0.0), (0.009, 0.004), (0.0145, 0.014), (0.0185, 0.030), (0.019, 0.042), (0.016, 0.054),
            (0.009, 0.062), (0.0, 0.065)]
    G.lathe(bl, prof if lod == 0 else prof[::2] + [prof[-1]], 10 if lod == 0 else 6, (LX, LY, z0 + 0.026))
    parts.append(bl)
    gp = P("lamp_grip", "lamp_grip")
    if lod == 0:
        prof = [(0.0, -0.140), (0.0060, -0.137), (0.0095, -0.118), (0.0145, -0.104)]
        for k in range(4):                                         # grip ribs
            zk = -0.094 + 0.019 * k
            prof += [(0.0174, zk), (0.0162, zk + 0.0095)]
        prof += [(0.0175, -0.018), (0.0225, -0.006), (0.0245, 0.0), (0.0245, 0.010), (0.0, 0.010)]
        G.lathe(gp, prof, 10, (LX, LY, GRIP_Z))
    else:
        G.lathe(gp, [(0.008, -0.135), (0.017, -0.10), (0.018, -0.02), (0.024, 0.0), (0.024, 0.010), (0.0, 0.010)],
                sd, (LX, LY, GRIP_Z))
    parts.append(gp)
    sk = P("lamp_socket", "socket")
    G.lathe(sk, [(0.0135, 0.0), (0.0135, 0.016), (0.0105, 0.019)], 10 if lod == 0 else 6, (LX, LY, GRIP_Z))
    parts.append(sk)
    cg = P("lamp_cage", "cage")
    hook = [(LX, LY, z1 + 0.008), (LX, LY, z1 + 0.030), (LX + 0.012, LY, NAIL[2] + 0.012),
            (XI1 - 0.012, LY, NAIL[2] + 0.017), (XI1 - 0.021, LY, NAIL[2] - 0.002)]
    if lod == 2:
        g.cyl(cg, (LX, LY, LC.z), "z", LR, 2 * LHALF, 5, cap=False)
        G.rod(cg, (LX, LY, z1), hook[2], 0.003, 3)
        return parts + [cg]
    rings = ((LC.z - 0.03, LR), (LC.z + 0.015, LR), (z1, 0.022)) if lod == 0 else \
        ((LC.z - 0.02, LR), (LC.z + 0.025, LR))
    for z, r in rings:
        G.ring(cg, (LX, LY, z), (0, 0, 1), r, 0.0016, 12 if lod == 0 else 6, 3)
    nr = 5 if lod == 0 else 4
    for k in range(nr):
        a = 2 * math.pi * (k + 0.5) / nr
        c, s = math.cos(a), math.sin(a)
        pts = [(LX + 0.025 * c, LY + 0.025 * s, z0 + 0.016), (LX + LR * c, LY + LR * s, LC.z - 0.03),
               (LX + LR * c, LY + LR * s, LC.z + 0.015), (LX + 0.022 * c, LY + 0.022 * s, z1)]
        G.cable(cg, pts, 0.0016, lod, 1, (3, 3))
    # cage cap and the hook through the nail
    G.lathe(cg, [(0.022, 0.0), (0.016, 0.006), (0.006, 0.010), (0.0, 0.011)], 10 if lod == 0 else 6, (LX, LY, z1))
    G.cable(cg, hook, 0.0022, lod, 2, (5, 4))
    parts.append(cg)
    # cable: from the handle down, along the shelf by the side to the back, into the back-wall bushing
    cb = P("lamp_cable", "cable_black")
    gb = GRIP_Z - 0.140
    gx, gz = GROM_LAMP
    pts = [(LX, LY, gb + 0.002), (LX, LY - 0.003, gb - 0.030), (LX - 0.010, LY + 0.012, Z3 + 0.016),
           (LX - 0.008, LY + 0.050, Z3 + 0.0034), (LX + 0.004, 0.010, Z3 + 0.0034), (gx - 0.004, 0.120, Z3 + 0.0034),
           (gx, BACK[0] - 0.030, Z3 + 0.006), (gx, BACK[0] - 0.008, gz - 0.002), (gx, BACK[0] + 0.001, gz)]
    G.cable(cb, pts, 0.0033, lod, 2, (6, 4))
    parts.append(cb)
    if lod == 0:
        nl = P("lamp_nail", "nail")
        g.cyl(nl, (XI1 - 0.012, LY, NAIL[2]), "x", 0.002, 0.024, 6)
        g.cyl(nl, (XI1 - 0.0235, LY, NAIL[2]), "x", 0.0038, 0.0012, 6)
        parts.append(nl)
    return parts


# =============================================================================
# Top tier: rolls, exercise books, a box, a jar; slot 1 (M78) and its cable from the shelf
# =============================================================================
BOX4 = (0.165, XI1 - 0.012, -0.032, SY1 - 0.006, 0.150)


def build_shelf4(spec):
    lod, sd = spec["lod"], spec["sides"]
    parts = build_rolls_top(spec)
    x0, x1, y0, y1, h = BOX4
    cb = P("box4", "carton")
    g.box(cb, x0, x1, y0, y1, Z4, Z4 + h, **(dict(r=0.003, seg=1) if lod == 0 else {}))
    parts.append(cb)
    if lod == 0:
        tp = P("box4_tape", "tape")
        cx = (x0 + x1) / 2
        g.box(tp, cx - 0.024, cx + 0.024, y0 - 0.0008, y1 + 0.0008, Z4 + h, Z4 + h + 0.0008)
        g.box(tp, cx - 0.024, cx + 0.024, y0 - 0.0008, y0, Z4 + h - 0.06, Z4 + h)
        parts.append(tp)
        nb = P("nb4", "nb_blue")
        G.notebooks(nb, [R("nb_blue"), R("nb_red"), R("nb_brown")], R("pages"), 0.045, -0.108, Z4, 5,
                    random.Random(214), w=0.15, d=0.20)
        parts.append(nb)
    elif lod == 1:
        ms = P("nb4_mass", "nb_blue")
        g.box(ms, -0.03, 0.12, -0.21, -0.012, Z4, NB4_TOP)
        parts.append(ms)
    parts += jar(spec, "jar4", (XI1 - 0.048, -0.150), Z4, 0.07, True, 44)
    parts += build_slot1_cable(spec)
    return parts


def build_slot1_cable(spec):
    """Empty slot 1: a grey computer cable from the back-wall bushing runs along the shelf between the
    exercise books and the M78 place and hangs over the edge; at the end a DE-9 connector (body, screws,
    metal "D")."""
    lod = spec["lod"]
    if lod == 2:
        return []
    gx, gz = GROM_SER
    r = 0.003
    yh = SY0 - 0.011                                          # the hanging end is in front of the shelf edge
    pts = [(gx, BACK[0] + 0.001, gz), (gx, BACK[0] - 0.010, gz - 0.004), (gx + 0.006, BACK[0] - 0.045, Z4 + r + 0.002),
           (SER_X - 0.006, 0.08, Z4 + r), (SER_X - 0.001, -0.08, Z4 + r), (SER_X, SY0 + 0.012, Z4 + r),
           (SER_X + 0.0005, SY0 - 0.0018, Z4 + 0.0016), (SER_X + 0.001, SY0 - 0.0060, Z4 - 0.012),
           (SER_X + 0.0015, yh, Z4 - 0.050), (SER_X + 0.002, yh, Z4 - 0.086)]
    cb = P("ser_cable", "cable_grey")
    G.cable(cb, pts, r, lod, 2, (6, 4))
    parts = [cb]
    hx, hw, hd, hh = SER_X + 0.002, DB[0] / 2, DB[1] / 2, DB[2]
    zt = Z4 - 0.084                                           # top of the connector body
    hd_ = P("ser_db", "db_hood")
    g.box(hd_, hx - hw, hx + hw, yh - hd, yh + hd, zt - hh, zt, **(dict(r=0.002, seg=1) if lod == 0 else {}))
    if lod == 0:
        g.cyl(hd_, (hx, yh, zt + 0.004), "z", 0.0048, 0.008, 8)              # shank for the cable
    parts.append(hd_)
    if lod == 0:
        sh = P("ser_db_shell", "db_shell")
        poly = [(hx - 0.0115, zt - hh - 0.0002), (hx + 0.0115, zt - hh - 0.0002), (hx + 0.0095, zt - hh - 0.0062),
                (hx - 0.0095, zt - hh - 0.0062)]
        g.prism(sh, poly, (0, 2), yh - 0.0042, yh + 0.0042)
        g.box(sh, hx - 0.0155, hx + 0.0155, yh - 0.0055, yh + 0.0055, zt - hh - 0.0012, zt - hh)   # flange
        for s in (-1, 1):
            g.cyl(sh, (hx + s * 0.0125, yh, zt - hh - 0.004), "z", 0.0016, 0.007, 6)   # screws
            g.cyl(hd_, (hx + s * 0.0125, yh, zt - hh + 0.003), "z", 0.0034, 0.006, 8)   # thumbscrews
        parts.append(sh)
    return parts


def build_roof(spec):
    """On the roof: a vanilla globe (DECOR), a roll along the rear edge with rubber bands, a folder flat."""
    lod, sd = spec["lod"], spec["sides"]
    if lod == 2:
        return []
    rl = P("roof_roll", "roll_old")
    ends, holes = roll_ends("roof_roll")
    a, b = (X0 + 0.06, Y1 - 0.06, H + 0.032), (X1 - 0.18, Y1 - 0.06, H + 0.032)
    G.paper_roll((rl, ends, holes), a, b, 0.032, sd, ends=(True, True), simple=lod > 0)
    parts = [rl, ends] + ([holes] if lod == 0 else [])
    if lod == 0:
        for t in (0.15, 0.85):
            parts.append(tie("roof_band_%d" % (t * 100), "band", (a[0] + (b[0] - a[0]) * t, a[1], a[2]), (1, 0, 0), 0.032,
                             sd, 1.0, 0.0))
    fd = P("roof_folder", "folder")
    g.box(fd, -0.12, 0.12, -0.165, 0.165, 0.0, 0.018, frame=G.frame_z(0.27, -0.065, -12.0, H),
          **(dict(r=0.0015, seg=1) if lod == 0 else {}))
    parts.append(fd)
    return parts


def build_lod(spec):
    parts = build_body(spec) + build_map(spec) + build_rolls_low(spec) + build_boxes_low(spec)
    parts += build_folders(spec) + build_shelf2_right(spec) + build_shelf3(spec) + build_lamp(spec)
    parts += build_shelf4(spec) + build_roof(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """One convex piece - the cabinet body; the props inside and the globe and roll on the roof have no collision."""
    wood = kx.PEN + r"\wood.rvmat"
    body = kx.box_pts(X0, X1, Y0, Y1, 0.0, H)
    comps = [(body, wood)]
    memory = {
        "invView": [(0.0, -2.8, 1.2)],
        "ce_center": [(0.0, 0.0, 0.9)],
        "ce_radius": [(1.0, 0.0, 0.9)],
    }
    for i, m in enumerate(MODS):
        memory["module_%d" % (i + 1)] = [m]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    # the frame includes the globe on the roof (the engine draws it, our vertices do not have it)
    top = max([hi[2]] + [q[2] for q in kv.corners(GLOBE, *DECOR[0][1:4])])
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, top)
    return comps, 90.0, memory, bbox


# the first ones are for the --look preview: overview, the shelves with the modules (also empty), the lamp
# close up, the bottom, the map on the side; the "work" look is the first three
SHOTS = [
    ("front", (-1.3, -3.0, 1.55), (0.0, 0.0, 0.95), 30),
    ("slots", (0.30, -1.30, 1.50), (0.02, 0.0, 1.18), 32),
    ("lamp", (-0.20, -0.95, 1.40), (0.30, -0.05, 1.10), 36),
    ("low", (-0.45, -1.25, 0.80), (0.0, 0.0, 0.42), 32),
    ("map", (1.6, -0.6, 1.45), (L.X_MAP, 0.0, 1.25), 34),
    ("top", (0.55, -1.15, 2.15), (0.0, 0.0, 1.62), 32),
    ("back", (1.3, 2.6, 1.7), (0.0, 0.0, 0.9), 30),
]

M.look_shots = (5, 3)
M.run(build_lod, collision, SHOTS, row_step=1.3, row_shot=((1.3, -5.2, 1.8), (1.3, 0, 0.9)))
