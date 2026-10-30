"""M60 - the field HQ of the Clear Sky: the terminal OZL_Sky_Terminal (it replaces the chemistry bench
M39). Result carriers are handed in here and the research tree is opened from here. A communications
desk, no modules.

    blender --background --python build_m60.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py with the system Python first (the laptop screen 'off' and the 12 'work' frames, a
hand-drawn map, crate stencils, the radio strip and panel, a lightning sign). layout.py (shared with
make_decals.py) says what goes where; the model's own primitives (rounded bodies, bodies of revolution,
ribbing, key caps) are in m60_geo.py.

Target: the HQ of a field camp in a swamp - a table of boards on army crates, on it an OPEN rugged
laptop of the late 90s and an army portable radio, a map on a tablet board, an antenna mast on guy lines
next to it. ~1.8 x 2.3 x 0.9 m, the table ~1.6 x 0.8, the top at ~0.75.

Look: the 'dayz' profile (matte, dirtier, AO in the colour). No angularity: rounded edges on boards,
crates, laptop bodies, radio, PTT key and power supply; the R-159 ribs are stamped with rounding;
connectors, handles and insulators are bodies of revolution with ribbing. Small details of real objects:
separate key caps, the CF-27 bracket handle on wire links, the touchpad surround, bezel screws, the lid
latch, hinges; the crimp belt and lever latches of the R-159 battery compartment, headset cups with pads
and a double headband, the PTT key with a ribbed key and a headset fork, the tablet's spring clip, a
crate handle on posts (a guy line is wound round it), tension sliders on the guys, a guy ring, clamps
and a pin insulator on the mast, the coax taped on; cables are smooth curves. Vanilla DayZ items as
proxies (kvanilla): a flashlight (instead of a custom tube) and batteries, binoculars, a compass at the
tablet, a sheet of paper - the comms log - with a pen (instead of a custom pencil), duct tape, an
electrician's kit, a canteen under the table. Their textures are in the model itself (not from the
config): checked against the p3d.

Work (an OZL_WorkFx loop): the laptop screen has its own texture (section screen, kmodel panels) with 12
frames of 0.25 s (a route crawls, the group mark pulses, anomaly marks blink, link bars jump, the active
node of the research tree blinks, a carrier reception bar grows, a block runs in the status line); the
radio transmit lamp and the laptop disk lamp blink (ozl_lamp_work, blink); the laptop power lamps burn
(ozl_lamp). The comms desk has no moving parts.

Prototypes and sizes:
- radio R-159 (company VHF; photo on Wikimedia Commons): transceiver 305 x 160 x 170 mm (greenradio.de;
  the mass there is 19 kg, which looks like the whole set; armsnet says 16 kg). It stands as in the
  photo: a wide face with stamped ribs towards the player, below it a battery compartment of the same
  section (a bit narrower, as in the photo) - its height of 0.20 is estimated from the photo -, a crimp
  belt and lever latches at the sides between them, the top of the body with a bead and a recessed
  panel. On top (from the photo, mirrored: the antenna is towards the mast) an antenna input with a
  white insulator and a ribbed nut, two orange terminals on brass posts, a lid-handle at the back, a big
  headset connector with a ribbed nut and a fork; four frequency wafer switches with digit windows and a
  transmit lamp are added (the station look). The headset hangs at the left end: a double headband
  across the top, cups with rubber pads on the front and back, the cord to the fork in the PTT socket;
  the PTT key lies on the table and its cord goes to the connector (in the photo the headset is plugged
  into the PTT key). Grey-green factory paint, worn to aluminium on the ribs, a pale-blue CS stripe
  painted with a brush, an empty nameplate on rivets;
- rugged laptop of the Panasonic Toughbook CF-27 class (1997-2000; photo on Wikimedia Commons): ~0.30 x
  0.06 x 0.24 closed (no datasheet with dimensions in open sources - as for M36), screen 12.1" 4:3 (246
  x 184 mm), base 36, lid 24 mm; from the photo - large corner rounding, a seam on the side, a bracket
  handle at the front on wire links to axes on the sides, a latch at the front and top of the lid, a
  screen bezel on screws, two hinges, a 15 x 6 keyboard - light keys and grey function keys without
  letters, a touchpad in a surround with two buttons, lamps; no brands. Open, the screen towards the
  player. The power supply is on the table;
- mast, after a photo of a portable guyed mast: a telescopic tube 45/36/28 mm in a sand crate, section
  clamps with wing nuts, a guy ring, an insulator and a pin on top, the top at 2.30 (no higher than ~2.3 -
  stations stand in buildings), three guys of orange cord with tension sliders (as in the photo) - to
  the handle of the table crate and to two bricks on the floor (brick 250 x 120 x 65, GOST 530), within
  ~0.5 m of the table;
- table: four 40 mm boards (190-200 mm wide) on two crates standing on end; a 12 mm plywood sheet under
  the laptop and radio (a tarpaulin or plywood on top). The crate is 0.40 x 0.35 x 0.71 (no datasheet -
  the dimensions are chosen so that the boards lie at 0.75), its face is a former lid with straps,
  hinges and latches, straps all round at the ends, on the outer side a handle - a bar on two posts;
- next to it: a 0.23 x 0.32 tablet board for an A4 (210 x 297) sheet of graph paper with a swamp map in
  coloured pencils (unreadable; the exercise-book sheet with a map is the M51 sample) under a spring
  clip, an enamelled mug D 85 x 85 with a rolled blue rim, under the table an extension reel (D 0.27)
  with a crank handle, a socket block and a cable to the generator, and a spare R-159 battery
  compartment - all estimated from ordinary objects.
Overall ~2.3 x 2.30 x 1.0 m with the guys and bricks; the table with everything on it ~1.6 x 1.13 x 0.8.

Clear Sky look: home-made on old equipment, clean workplaces. The crates, the mast crate and the mast
are light-blue paint (as M08/M12) over wood and steel, wood and rust in the chips, dirt at the bottom;
boards and plywood are clean; the laptop, radio and map are clean. Unreadable details: numbers and a
stripe by stencil on the crates, 'up' arrows on the sides (the crates stand on end, so they look
sideways), frequency digits in the windows, the empty radio nameplate, a lightning sign on the extension
reel.

Station look: laptop screen ozl_screen (own texture, 'work' frames), radio lamp and laptop disk lamp
ozl_lamp_work (blink), laptop power lamps ozl_lamp (burn); the 'work' of the lamps is the _on atlas and
an _on rvmat with emission. LODs: the mid LOD has no small things (nails, hinges, screws, keys as a
slab, terminals, latches) and simpler wires and cords; the far LOD is boxes, with no wires, cords or
pin.

Blender axes: X is width, Y is depth (the front faces -Y), Z is up.
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
import m60_geo as G  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
TOP, TOP_B, ZP = L.TOP, L.TOP_B, L.RZP

LOD_SPECS = [
    dict(lod=0, sides=16),
    dict(lod=1, sides=8),
    dict(lod=2, sides=5),
]

REGIONS = {
    "board": ("board", 0.8), "cleat": ("cleat", 0.4), "ply": ("ply", 0.8), "nail": ("nail", 1.0),
    "crate": ("crate", 0.6), "crate_front": ("crate_front", 0.9), "crate_side": ("crate_side", 0.8),
    "gap": ("gap", 0.2), "iron": ("iron", 1.2),
    "lap": ("laptop", 1.4), "lap_lid": ("laptop_lid", 1.2), "grip": ("grip", 1.2), "kbd": ("kbd", 1.0),
    "key": ("keycap", 2.4), "key_grey": ("keycap_grey", 2.4), "pad": ("touchpad", 2.0), "black": ("black", 1.2),
    "wire": ("wire_steel", 1.4), "psu": ("psu", 0.8),
    "radio": ("radio", 1.0), "radio_front": ("radio_front", 1.6), "radio_top": ("radio_top", 3.0),
    "radio_seam": ("radio_seam", 1.0), "tag": ("tag", 2.0), "orange": ("orange", 1.6), "chrome": ("chrome", 1.4),
    "brass": ("brass", 1.6), "white": ("plastic_white", 1.6), "knob": ("knob", 1.8), "rubber": ("rubber", 0.8),
    "tangent": ("tangent", 1.4),
    "clipboard": ("clipboard", 0.8), "paper": ("paper", 5.0),
    "mug": ("mug", 1.4), "mug_rim": ("mug_rim", 1.4), "tea": ("tea", 1.0),
    "mast": ("mast", 0.8), "steel_dark": ("steel_dark", 1.0), "ballast": ("crate", 0.7), "sand": ("sand", 0.6),
    "rope": ("rope", 0.4), "brick": ("brick", 0.8), "ant": ("ant", 0.8), "slider": ("slider", 1.2),
    "tape": ("tape", 1.0),
    "reel": ("reel", 0.9), "coil": ("coil", 0.7), "socket": ("socket", 1.6), "cable": ("cable", 0.5),
    "lamp_r": ("lamp_r", 1.0), "led_g": ("led_g", 1.0), "led_a": ("led_a", 1.0),
}

# =============================================================================
# Materials
# =============================================================================


def wdecal(name):
    return os.path.join(WORK, name)


def decal_y(name, cx, cz, w, h, y, depth=(-0.004, 0.002)):
    """A decal on faces looking at -y at depth y + depth."""
    return (wdecal(name), "y", -1, ("x", "z"), (cx, cz), (w, h), (y + depth[0], y + depth[1]))


def decal_x(name, sign, cy, cz, w, h, x, depth=0.003):
    """A decal on faces looking at sign*x (u runs along y)."""
    return (wdecal(name), "x", sign, ("y", "z"), (cy, cz), (w, h), (x - depth, x + depth))


def decal_z(name, cx, cy, w, h, z, eps=0.0008):
    """A decal on faces looking up: the top of the picture points to the back (+y)."""
    return (wdecal(name), "z", 1, ("x", "y"), (cx, cy), (w, h), (z - eps, z + eps))


def map_decal():
    """The map on the tablet: the picture is already rotated by MAP_DEG (make_decals.py), here is its
    frame in world axes.
    """
    pw, ph, off = L.MAP_PAPER
    a = math.radians(L.MAP_DEG)
    cx = L.MAP_C[0] - off * math.sin(a)
    cy = L.MAP_C[1] + off * math.cos(a)
    w = pw * abs(math.cos(a)) + ph * abs(math.sin(a))
    h = pw * abs(math.sin(a)) + ph * abs(math.cos(a))
    return [decal_z("decal_map.png", cx, cy, w, h, TOP_B + MAP_T + PAPER_T)]


MAP_T, PAPER_T = 0.008, 0.0008
CRATE_DECALS = [decal_y("decal_crate%d.png" % i, (x0 + x1) / 2, 0.42, 0.30, 0.40, L.CY0)
                for i, (x0, x1) in enumerate(L.CRATES)]
ARROW_DECALS = [decal_x("decal_arrows.png", -1, 0.0, 0.55, 0.12, 0.16, L.CRATES[0][0]),
                decal_x("decal_arrows.png", 1, 0.0, 0.55, 0.12, 0.16, L.CRATES[1][1])]
BAND_DECAL = [decal_y("decal_radio_band.png", L.RXC, sum(L.BAND_Z) / 2, L.RX1 - L.RX0, L.BAND_Z[1] - L.BAND_Z[0],
                      L.RY0, depth=(-0.003, 0.003))]
_px0, _px1, _py0, _py1 = L.R_PANEL
RTOP_DECAL = [decal_z("decal_radio_top.png", (_px0 + _px1) / 2, (_py0 + _py1) / 2, _px1 - _px0, _py1 - _py0, ZP)]
_s = L.SOCK
BOLT_DECAL = [decal_y("decal_bolt.png", (_s[0] + _s[1]) / 2, _s[5] - 0.028, 0.034, 0.034, _s[2])]

KINDS = kmats.std_kinds(floor_z=0.0)
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
WOOD = kmats.lin((150, 116, 76))
# CS light-blue paint on wood (as M08): wood in the chips, dirt from below; no rust on wood
BLUE_WOOD = dict(color=kmats.lin((150, 192, 214)), under=WOOD, seed=2.2, gloss=0.22, spec=0.12, chip=(0.58, 0.64),
                 rust=(0.99, 1.0), rust_low=0.0, floor_z=0.0, dust=0.3, grime=0.9)
# grey-green factory paint of the radio: worn to aluminium on the ribs, clean
RADIO = dict(color=kmats.lin((96, 108, 92)), under=kmats.lin((168, 170, 166)), seed=7.1, gloss=0.32, spec=0.26,
             chip=(0.64, 0.70), rust=(0.99, 1.0), rust_low=0.0, floor_z=TOP, dust=0.14, grime=0.2)
KINDS.update({
    # boards and plywood are clean (a workplace), the bars under the table are darker
    "board": (kwood.build_wood, dict(color=kmats.lin((172, 136, 96)), seed=1.4, along="x", floor_z=0.0, dust=0.15,
                                     grime=0.3, knots=0.7)),
    "cleat": (kwood.build_wood, dict(color=kmats.lin((136, 104, 72)), seed=1.9, along="y", floor_z=0.0, dust=0.2,
                                     grime=0.45)),
    "ply": (kwood.build_wood, dict(color=kmats.lin((186, 154, 110)), seed=2.6, along="x", floor_z=0.0, dust=0.12,
                                   grime=0.2, rings=0.4, knots=0.15)),
    "clipboard": (kwood.build_wood, dict(color=kmats.lin((118, 82, 50)), seed=3.3, along="y", floor_z=0.0, dust=0.05,
                                         grime=0.12, rings=0.2, knots=0.1)),
    "nail": ("steel", dict(seed=3.3, tone=0.22, along="z", gloss=0.4, spec=0.45, dust=0.2, grime=0.6)),
    "crate": ("paint", BLUE_WOOD),
    "crate_front": ("paint", dict(BLUE_WOOD, decal_items=CRATE_DECALS)),
    "crate_side": ("paint", dict(BLUE_WOOD, seed=2.7, decal_items=ARROW_DECALS)),
    "gap": ("flat", dict(color=kmats.lin((40, 32, 24)), gloss=0.05, spec=0.03)),
    "iron": ("paint", dict(color=kmats.lin((38, 40, 40)), under=kmats.lin((90, 70, 52)), seed=3.6, gloss=0.3, spec=0.3,
                           chip=(0.56, 0.62), rust=(0.60, 0.68), rust_low=1.0, floor_z=0.0, dust=0.3, grime=0.6)),
    # laptop: graphite moulded body, rubbed lighter at the handle and along the edges
    "laptop": ("plastic", dict(color=kmats.lin((50, 51, 52)), seed=6.1, gloss=0.28, spec=0.22, mottle=0.08, floor_z=TOP,
                               dust=0.10, grime=0.12, scuff=(0.60, 0.68))),
    "laptop_lid": ("plastic", dict(color=kmats.lin((52, 53, 54)), seed=6.4, gloss=0.28, spec=0.22, mottle=0.08,
                                   floor_z=TOP, dust=0.12, grime=0.06, scuff=(0.64, 0.72))),
    "grip": ("plastic", dict(color=kmats.lin((30, 30, 31)), seed=6.3, gloss=0.14, spec=0.08, mottle=0.1, floor_z=TOP,
                             dust=0.12, scuff=(0.60, 0.68))),
    "kbd": ("plastic", dict(color=kmats.lin((22, 22, 23)), gloss=0.2, spec=0.15, dust=0.2)),
    # CF-27 keys (photo): light yellowed, the function ones grey; the middle is rubbed to a shine
    "keycap": ("plastic", dict(color=kmats.lin((214, 205, 178)), seed=6.7, gloss=0.30, spec=0.2, mottle=0.10, dust=0.08,
                               grime=0.25, scuff=(0.58, 0.66))),
    "keycap_grey": ("plastic", dict(color=kmats.lin((150, 150, 145)), seed=6.9, gloss=0.30, spec=0.2, mottle=0.08,
                                    dust=0.08, grime=0.25, scuff=(0.58, 0.66))),
    "touchpad": ("plastic", dict(color=kmats.lin((36, 36, 37)), gloss=0.15, spec=0.1, mottle=0.1, dust=0.1,
                                 scuff=(0.6, 0.7))),
    "wire_steel": ("steel", dict(seed=6.2, tone=0.22, along="x", gloss=0.45, spec=0.5, dust=0.1, grime=0.3)),
    "psu": ("plastic", dict(color=kmats.lin((28, 28, 29)), gloss=0.25, spec=0.2, mottle=0.06, floor_z=TOP, dust=0.15)),
    "radio": ("paint", RADIO),
    "radio_front": ("paint", dict(RADIO, decal_items=BAND_DECAL)),
    "radio_top": ("paint", dict(RADIO, seed=7.4, decal_items=RTOP_DECAL)),
    "radio_seam": ("steel", dict(seed=7.7, tone=0.30, along="x", gloss=0.45, spec=0.5, dust=0.1, grime=0.25)),
    "tag": ("steel", dict(seed=7.2, tone=0.55, along="y", gloss=0.5, spec=0.6, dust=0.05, grime=0.1)),
    "orange": ("plastic", dict(color=kmats.lin((206, 88, 30)), gloss=0.5, spec=0.35, dust=0.05, scuff=(0.66, 0.76))),
    "chrome": ("steel", dict(seed=6.6, tone=0.30, along="z", gloss=0.62, spec=0.75, dust=0.05, grime=0.2)),
    "brass": ("paint", dict(CLEAN, color=kmats.lin((168, 128, 62)), gloss=0.55, spec=0.5)),
    "knob": ("plastic", dict(color=kmats.lin((22, 21, 20)), gloss=0.45, spec=0.35, dust=0.08, scuff=(0.64, 0.72))),
    "tangent": ("paint", dict(color=kmats.lin((112, 114, 114)), under=kmats.lin((150, 152, 150)), seed=8.3, gloss=0.35,
                              spec=0.3, chip=(0.68, 0.74), rust=(0.99, 1.0), rust_low=0.0, floor_z=TOP, dust=0.06,
                              grime=0.12)),
    "paper": ("paint", dict(CLEAN, color=kmats.lin((236, 234, 224)), gloss=0.06, spec=0.03, decal_items=map_decal())),
    # mug: white enamel with a blue rim, chips down to black iron
    "mug": ("paint", dict(color=kmats.lin((226, 228, 224)), under=kmats.lin((26, 26, 28)), seed=9.1, gloss=0.6,
                          spec=0.5, chip=(0.70, 0.75), rust=(0.99, 1.0), rust_low=0.0, floor_z=TOP_B, dust=0.05,
                          grime=0.1)),
    "mug_rim": ("paint", dict(color=kmats.lin((40, 70, 150)), under=kmats.lin((26, 26, 28)), seed=9.4, gloss=0.6,
                              spec=0.5, chip=(0.62, 0.68), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)),
    "tea": ("flat", dict(color=kmats.lin((64, 34, 14)), gloss=0.9, spec=0.6)),
    # mast: CS light-blue paint on steel, steel and rust in the chips
    "mast": ("paint", dict(color=kmats.lin((150, 192, 214)), under=kmats.lin((96, 100, 102)), seed=4.6, gloss=0.35,
                           spec=0.28, chip=(0.62, 0.68), rust=(0.70, 0.78), rust_low=0.8, floor_z=0.0, dust=0.15,
                           grime=0.5)),
    "steel_dark": ("paint", dict(color=kmats.lin((36, 38, 38)), under=kmats.lin((120, 120, 118)), seed=5.1, gloss=0.35,
                                 spec=0.35, chip=(0.62, 0.68), rust=(0.72, 0.80), rust_low=0.5, floor_z=0.0,
                                 dust=0.15, grime=0.3)),
    "ant": ("plastic", dict(color=kmats.lin((26, 26, 26)), gloss=0.35, spec=0.25, dust=0.12)),
    "slider": ("plastic", dict(color=kmats.lin((44, 46, 40)), gloss=0.3, spec=0.2, dust=0.15, scuff=(0.7, 0.8))),
    "tape": ("plastic", dict(color=kmats.lin((20, 20, 22)), gloss=0.45, spec=0.3, mottle=0.08, dust=0.12,
                             scuff=(0.7, 0.8))),
    "sand": ("plastic", dict(color=kmats.lin((150, 132, 100)), seed=4.9, gloss=0.05, spec=0.02, mottle=0.35, dust=0.0,
                             grime=0.2, scuff=(0.9, 1.0))),
    "rope": ("plastic", dict(color=kmats.lin((236, 104, 26)), gloss=0.2, spec=0.1, mottle=0.12, dust=0.1,
                             scuff=(0.9, 1.0))),
    "brick": ("plastic", dict(color=kmats.lin((150, 70, 46)), seed=5.7, gloss=0.08, spec=0.04, mottle=0.3, dust=0.3,
                              grime=0.4, scuff=(0.6, 0.68))),
    # extension reel: red-brown cheeks, black cable, a carbolite socket block
    "reel": ("paint", dict(color=kmats.lin((150, 46, 32)), under=kmats.lin((60, 60, 62)), seed=8.8, gloss=0.4,
                           spec=0.3, chip=(0.62, 0.68), rust=(0.68, 0.76), rust_low=0.8, floor_z=0.0, dust=0.3,
                           grime=0.6)),
    "coil": ("plastic", dict(color=kmats.lin((28, 28, 28)), gloss=0.35, spec=0.2, mottle=0.15, dust=0.4, grime=0.4)),
    # socket block - carbolite; the lightning sign is a decal (the 'plastic' builder has no decals -
    # 'paint' without rust)
    "socket": ("paint", dict(color=kmats.lin((64, 44, 32)), under=kmats.lin((40, 30, 22)), seed=8.6, gloss=0.5, spec=0.35,
                             chip=(0.80, 0.86), rust=(0.99, 1.0), rust_low=0.0, floor_z=0.0, dust=0.2, grime=0.3,
                             decal_items=BOLT_DECAL)),
    "cable": ("plastic", dict(color=kmats.lin((24, 24, 24)), gloss=0.35, spec=0.25, dust=0.25)),
    "lamp_r": ("flat", dict(color=kmats.lin((90, 22, 18)), gloss=0.85, spec=0.8)),
    "lamp_r_on": ("flat", dict(color=kmats.lin((255, 80, 56)), gloss=0.85, spec=0.8)),
    "led_g": ("flat", dict(color=kmats.lin((34, 64, 40)), gloss=0.85, spec=0.8)),
    "led_g_on": ("flat", dict(color=kmats.lin((130, 255, 140)), gloss=0.85, spec=0.8)),
    "led_a": ("flat", dict(color=kmats.lin((80, 56, 22)), gloss=0.85, spec=0.8)),
    "led_a_on": ("flat", dict(color=kmats.lin((255, 176, 40)), gloss=0.85, spec=0.8)),
})

OBJ, NAME = "m60_sky_terminal", "ozr_sky_terminal"
# Station look: the laptop screen is ozl_screen, its own texture (section screen): off is a dark panel,
# work is 12 frames (OZL_WorkFx frames). The radio lamp and the laptop disk lamp are ozl_lamp_work (they
# blink in work - blink), the laptop power and battery lamps are ozl_lamp (burn). The work of the lamps
# is the _on_co atlas and an _on rvmat with emission.
SEL_SCREEN, SEL_LAMP, SEL_BLINK = "ozl_screen", "ozl_lamp", "ozl_lamp_work"
ON = dict(remap={"lamp_r": "lamp_r_on", "led_g": "led_g_on", "led_a": "led_a_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
SCREEN = dict(off="decal_screen_off.png", frames=["decal_screen_f%02d.png" % i for i in range(12)], size=256,
              gloss=0.8)
# vanilla DayZ items as proxies: all have their texture in the model itself (not from the config); the
# bounds are checked with kv.corners: they sit on their support, do not hang over the edge and do not
# intersect
BINOC, COMPASS, CANTEEN = r"dz\gear\optics\binoculars", r"dz\gear\navigation\compass", r"dz\gear\drinks\Canteen"
DECOR = [
    kv.put("flashlight", (-0.700, 0.098, TOP_B), **kv.flat(94.0)),
    kv.put("batteryd", (-0.622, 0.300, TOP_B), up=(0, 0, 1), fwd=(0, -1, 0)),          # flashlight batteries
    kv.put(BINOC, (-0.800, 0.268, TOP_B), **kv.flat(98.0)),
    kv.put(COMPASS, (-0.653, -0.290, TOP_B), up=(0, 0, 1), fwd=(1, 0.12, 0)),          # by the map tablet
    kv.put("paper", (-0.080, -0.205, TOP), **kv.flat(98.0)),                          # comms log
    kv.put("pen", (-0.045, -0.175, TOP + 0.0004), **kv.flat(52.0)),                   # on the log
    kv.put("ducttape", (0.477, -0.300, TOP_B), **kv.flat(0.0)),                       # it tapes the coax
    kv.put("electrickit", (0.476, 0.022, TOP_B), **kv.flat(90.0)),
    kv.put(CANTEEN, (-0.500, -0.215, 0.0), up=(0, 0, 1), fwd=(-1, 0.18, 0)),          # under the table
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 selections=(SEL_SCREEN, SEL_LAMP, SEL_BLINK), hidden=(SEL_SCREEN, SEL_LAMP, SEL_BLINK),
                 states={"on": ON}, decor=DECOR, panels={"screen": SCREEN})
P = M.part
BOUNDS = {}


def use(part, region):
    """The next primitives of the part go to another region."""
    return part.use(region, *REGIONS[region])


def top_quad(part, x0, x1, y0, y1, z):
    return g.quad(part, [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)])


# =============================================================================
# Table: boards, bars, plywood
# =============================================================================
def build_table(spec):
    lod = spec["lod"]
    parts = []
    if lod == 2:
        b = P("boards", "board")
        g.box(b, L.TX0, L.TX1, L.TY0, L.TY1, L.CRATE_H, TOP_B)
        parts.append(b)
    else:
        for i, (y0, y1, x0, x1) in enumerate(L.BOARDS):
            b = P("board%d" % i, "board")
            if lod == 0:
                G.rbox(b, x0, x1, y0, y1, L.CRATE_H, TOP_B, 0.005, 2)
            else:
                g.box(b, x0, x1, y0, y1, L.CRATE_H, TOP_B)
            parts.append(b)
        if lod == 0:
            cl = P("cleats", "cleat")
            for x0, x1 in L.CLEATS:
                G.rbox(cl, x0, x1, L.TY0 + 0.03, L.TY1 - 0.03, L.CRATE_H - L.CLEAT_T, L.CRATE_H + 0.0005, 0.003, 1)
            parts.append(cl)
    pl = P("plywood", "ply")
    if lod == 0:
        G.rbox(pl, L.PX0, L.PX1, L.PY0, L.PY1, TOP_B - 0.0005, TOP, 0.0025, 1)
    else:
        g.box(pl, L.PX0, L.PX1, L.PY0, L.PY1, TOP_B, TOP)
    parts.append(pl)
    if lod == 0:
        # nails: two per board above each crate (where the board is not under plywood) and along the
        # plywood edges
        nl = P("nails", "nail")
        for y0, y1, x0, x1 in L.BOARDS:
            for cx0, cx1 in L.CRATES:
                for xx in (cx0 + 0.03, cx1 - 0.03):
                    for yy in (y0 + 0.035, y1 - 0.035):
                        if L.PX0 - 0.01 < xx < L.PX1 + 0.01 and L.PY0 - 0.01 < yy < L.PY1 + 0.01:
                            continue
                        G.disk(nl, (xx, yy, TOP_B + 0.0005), (0, 0, 1), 0.0042, 6)
        for xx in (L.PX0 + 0.02, (L.PX0 + L.PX1) / 2, L.PX1 - 0.02):
            for yy in (L.PY0 + 0.02, L.PY1 - 0.02):
                G.disk(nl, (xx, yy, TOP + 0.0004), (0, 0, 1), 0.0030, 6)
        parts.append(nl)
    return parts


# =============================================================================
# Crates on end
# =============================================================================
def crate(i, lod):
    """Army crate on end: the face (a former lid) - three boards along the height, straps near the ends
    all round (on the face, back and outer side), hinges on the left edge and latches on the right;
    sides and back are boards; on the outer side a handle - a bar on two posts with a gap to the wall.
    """
    x0, x1 = L.CRATES[i]
    y0, y1, h = L.CY0, L.CY1, L.CRATE_H
    T, gap = L.CRATE_T, 0.005
    pre = "crate%d" % i
    outer = x0 if i == 0 else x1
    so = -1 if i == 0 else 1
    if lod == 2:
        b = P(pre, "crate_front")
        g.box(b, x0, x1, y0, y1, 0.0, h)
        return [b]
    parts = []
    if lod == 1:
        fr = P(pre + "_front", "crate_front")
        g.box(fr, x0, x1, y0, y0 + T, 0.0, h)
        rest = P(pre + "_body", "crate_side")
        g.box(rest, x0, x1, y0 + T, y1, 0.0, h)
        parts += [fr, rest]
    else:
        core = P(pre + "_core", "gap")
        g.box(core, x0 + 0.006, x1 - 0.006, y0 + 0.006, y1 - 0.006, 0.002, h - 0.002)
        fr = P(pre + "_front", "crate_front")
        bk = P(pre + "_back", "crate")
        bw = (x1 - x0 - 2 * gap) / 3
        for k in range(3):
            xa = x0 + k * (bw + gap)
            G.rbox(fr, xa, xa + bw, y0, y0 + T, 0.0, h, 0.003, 1)
            g.box(bk, xa + 0.001, xa + bw - 0.001, y1 - T, y1, 0.0, h)
        parts += [core, fr, bk]
        sw = (y1 - y0 - 2 * T - gap) / 2
        for s, xs in (("l", x0), ("r", x1 - T)):
            sd = P(pre + "_side_" + s, "crate_side")
            for k in range(2):
                ya = y0 + T + k * (sw + gap)
                g.box(sd, xs, xs + T, ya + 0.001, ya + sw - 0.001, 0.0, h)
            parts.append(sd)
    # straps near the ends: on the face (and on the back and outer side at the near LOD)
    for s, ya, yb in (("f", y0 - 0.015, y0), ("b", y1, y1 + 0.015))[:2 if lod == 0 else 1]:
        bt = P(pre + "_battens_" + s, "crate")
        for za, zb in L.BATTENS:
            if lod == 0 and s == "f":
                G.rbox(bt, x0 - 0.001, x1 + 0.001, ya, yb + 0.001, za, zb, 0.003, 1)
            else:
                g.box(bt, x0, x1, ya, yb, za, zb)
        parts.append(bt)
    if lod == 0:
        bs = P(pre + "_battens_side", "crate")
        xa, xb = sorted((outer - so * 0.001, outer + so * 0.015))
        for za, zb in L.BATTENS:
            g.box(bs, xa, xb, y0 - 0.015, y1 + 0.015, za, zb)
        parts.append(bs)
    # handle on the outer side: a bar on two posts (the guy line is tied to the right one - a gap for
    # the cord)
    hd = P(pre + "_handle", "crate")
    za, zb = L.HANDLE_Z
    ho0, ho1 = L.HANDLE_OUT
    if lod == 0:
        for yy in (-L.HANDLE_Y + 0.012, L.HANDLE_Y - 0.012):
            xs0, xs1 = sorted((outer - so * 0.001, outer + so * (ho0 + 0.002)))
            g.box(hd, xs0, xs1, yy - 0.012, yy + 0.012, za - 0.004, zb + 0.004)
        xg0, xg1 = sorted((outer + so * ho0, outer + so * ho1))
        G.rbox(hd, xg0, xg1, -L.HANDLE_Y, L.HANDLE_Y, za, zb, 0.0045, 1)
    else:
        xg0, xg1 = sorted((outer, outer + so * ho1))
        g.box(hd, xg0, xg1, -L.HANDLE_Y, L.HANDLE_Y, za, zb)
    parts.append(hd)
    if lod == 1:
        return parts
    # handle bolts
    bo = P(pre + "_bolts", "iron")
    for yy in (-L.HANDLE_Y + 0.012, L.HANDLE_Y - 0.012):
        G.disk(bo, (outer + so * (ho1 + 0.0004), yy, (za + zb) / 2), (so, 0, 0), 0.0045, 6)
    parts.append(bo)
    ir = P(pre + "_iron", "iron", uv_name="crate_iron", uv_origin=(x0, y0, 0.0))
    for zc in L.HINGE_Z:
        # hinge: a strip on the face, a knuckle on the corner, a strip on the side; screws
        g.box(ir, x0 + 0.004, x0 + 0.075, y0 - 0.003, y0 + 0.0005, zc - 0.016, zc + 0.016)
        g.cyl(ir, (x0 - 0.0005, y0 - 0.0025, zc), "z", 0.0055, 0.040, 8)
        g.box(ir, x0 - 0.003, x0 + 0.0005, y0 + 0.004, y0 + 0.060, zc - 0.016, zc + 0.016)
        # latch: a plate on the face, a flip lever, a staple on the side
        g.box(ir, x1 - 0.050, x1 - 0.004, y0 - 0.003, y0 + 0.0005, zc - 0.015, zc + 0.015)
        g.box(ir, x1 - 0.040, x1 - 0.012, y0 - 0.0085, y0 - 0.0025, zc - 0.011, zc + 0.011)
        g.box(ir, x1 - 0.0005, x1 + 0.003, y0 + 0.004, y0 + 0.050, zc - 0.014, zc + 0.014)
        for xx in (x0 + 0.032, x0 + 0.064, x1 - 0.046):
            G.disk(ir, (xx, y0 - 0.0033, zc), (0, -1, 0), 0.0030, 6)
    parts.append(ir)
    return parts


def build_crates(spec):
    lod = spec["lod"]
    return crate(0, lod) + crate(1, lod)


# =============================================================================
# CF-27 class laptop and power supply
# =============================================================================
def lid_frame():
    o, u, v, n = L.lid_axes()
    return g.Frame(o, u, v, n)


def key_rects():
    """CF-27 keys (photo): 15 columns; the function row is lower, then four rows and a bottom one with a
    space bar; grey ones are function keys. (x, width, y, depth, grey).
    """
    kx0, kx1, ky0, ky1 = L.KEYS
    u = (kx1 - kx0) / 15.0
    kh = (ky1 - ky0) / 5.7
    rows = [(0.7, [(i, 1, i in (0, 13, 14)) for i in range(15)]),
            (1.0, [(i, 1, False) for i in range(13)] + [(13, 2, True)]),
            (1.0, [(0, 1.5, True)] + [(1.5 + i, 1, False) for i in range(12)] + [(13.5, 1.5, True)]),
            (1.0, [(0, 1.75, True)] + [(1.75 + i, 1, False) for i in range(11)] + [(12.75, 2.25, True)]),
            (1.0, [(0, 2.25, True)] + [(2.25 + i, 1, False) for i in range(10)] + [(12.25, 1.75, True), (14, 1, True)]),
            (1.0, [(0, 1, True), (1, 1, True), (2, 1, True), (3, 1, True), (4, 5, False), (9, 1, True), (10, 1, True),
                   (11, 1, True), (12, 1, True), (13, 1, True), (14, 1, True)])]
    out = []
    y = ky1
    for hf, keys in rows:
        d = kh * hf
        for x, w, grey in keys:
            out.append((kx0 + x * u, w * u, y - d, d, grey))
        y -= d
    return out


def build_laptop(spec):
    lod = spec["lod"]
    x0, x1, y0, y1 = L.LX0, L.LX1, L.LY0, L.LY1
    zt = TOP + L.LB_H
    R = L.LAP_R
    fr = lid_frame()
    a0, a1 = L.LXC - L.LCD_W / 2, L.LXC + L.LCD_W / 2
    b0, b1 = L.LCD_B, L.LCD_B + L.LCD_H
    parts = []
    bs = P("laptop", "lap")
    ld = P("laptop_lid", "lap_lid")
    if lod == 0:
        # base: rounded in plan, rounded edges, a seam on the side
        G.rr_loft(bs, x0, x1, y0, y1, [(TOP, 0.003), (TOP + 0.003, 0.0), (TOP + 0.0165, 0.0), (TOP + 0.017, 0.0012),
                                        (TOP + 0.0185, 0.0012), (TOP + 0.019, 0.0), (zt - 0.004, 0.0),
                                        (zt - 0.0012, 0.0012), (zt, 0.004)], R, 3)
        G.rr_loft(ld, x0, x1, 0.0, L.LID_D, [(-L.LID_T, 0.003), (-L.LID_T + 0.003, 0.0), (-0.0035, 0.0),
                                              (-0.001, 0.0012), (0.0, 0.0035)], R, 3, frame=fr)
    elif lod == 1:
        G.rr_loft(bs, x0, x1, y0, y1, [(TOP, 0.0), (zt, 0.0)], R, 1)
        G.rr_loft(ld, x0, x1, 0.0, L.LID_D, [(-L.LID_T, 0.0), (0.0, 0.0)], R, 1, frame=fr)
    else:
        g.box(bs, x0, x1, y0, y1, TOP, zt)
        g.box(ld, x0, x1, 0.0, L.LID_D, -L.LID_T, 0.0, frame=fr)
    parts += [bs, ld]
    # screen - its own texture (section screen), UV 0..1 over the lid frame
    sc = P("laptop_screen", "black", group=SEL_SCREEN, section="screen")
    vs = [sc.bm.verts.new(fr.p(a, b, 0.0006)) for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
    sc.tag([G.face(sc, vs, fr.n)])
    sc.glass_frame = (fr, a0, a1, b0, b1)
    parts.append(sc)
    # lamps on the front edge: power and battery burn, disk blinks
    led = P("laptop_leds", "led_g", group=SEL_LAMP)
    hdd = P("laptop_hdd", "led_a", group=SEL_BLINK)
    for dx, part in ((-0.016, led), (-0.005, led), (0.008, hdd)):
        lx, ly = L.LXC + dx, L.LED_Y
        if lod == 0:
            g.box(part, lx - 0.0032, lx + 0.0032, ly - 0.0018, ly + 0.0018, zt - 0.0005, zt + 0.0011)
        else:
            top_quad(part, lx - 0.0032, lx + 0.0032, ly - 0.0018, ly + 0.0018, zt + 0.0008)
    parts += [led, hdd]
    if lod == 2:
        return parts
    # screen bezel: the screen is recessed
    bz = P("laptop_bezel", "lap_lid")
    e = 0.010
    for qa0, qa1, qb0, qb1 in ((a0 - e, a1 + e, b0 - e, b0), (a0 - e, a1 + e, b1, b1 + e),
                               (a0 - e, a0, b0, b1), (a1, a1 + e, b0, b1)):
        g.box(bz, qa0, qa1, qb0, qb1, -0.0008, 0.0024, frame=fr)
    parts.append(bz)
    # lid hinges
    hg = P("laptop_hinge", "black")
    for s in (-1, 1):
        g.cyl(hg, (L.LXC + s * 0.088, y1 - 0.011, zt + 0.003), "x", 0.0095, 0.058, 12 if lod == 0 else 6)
    if lod == 0:
        g.cyl(hg, (L.LXC, y1 - 0.011, zt + 0.002), "x", 0.0080, 0.112, 12)
    parts.append(hg)
    # keyboard: a well and key caps (a slab at the mid LOD)
    kx0, kx1, ky0, ky1 = L.KEYS
    kw = P("laptop_kbd", "kbd")
    G.rr_loft(kw, kx0 - 0.003, kx1 + 0.003, ky0 - 0.003, ky1 + 0.003, [(zt - 0.0006, 0.0), (zt + 0.0006, 0.0)], 0.003, 1,
              cap0=False)
    parts.append(kw)
    if lod == 0:
        kl, kg = P("laptop_keys", "key"), P("laptop_keys_grey", "key_grey")
        for kx, kwd, ky, kd, grey in key_rects():
            G.keycap(kg if grey else kl, kx + 0.0006, kx + kwd - 0.0006, ky + 0.0006, ky + kd - 0.0006, zt + 0.0006,
                     0.0034, 0.0012)
        parts += [kl, kg]
    else:
        kl = P("laptop_keys", "key")
        g.box(kl, kx0, kx1, ky0, ky1, zt, zt + 0.003)
        parts.append(kl)
    # touchpad in a surround and two buttons
    px, py, pw, pd = L.TPAD
    tp = P("laptop_pad", "pad")
    if lod == 0:
        tr = P("laptop_padring", "lap")
        G.rr_ring(tr, (px - pw / 2 - 0.007, px + pw / 2 + 0.007, py - pd / 2 - 0.021, py + pd / 2 + 0.007),
                  (px - pw / 2, px + pw / 2, py - pd / 2 - 0.0145, py + pd / 2), zt - 0.0004, zt + 0.0014, 0.012, 0.005, 2)
        parts.append(tr)
        G.flat_rr(tp, px - pw / 2, px + pw / 2, py - pd / 2, py + pd / 2, zt + 0.0003, 0.005, 2)
        for s in (-1, 1):
            G.rr_loft(tp, *sorted((px + s * 0.0015, px + s * 0.031)), py - pd / 2 - 0.0135, py - pd / 2 - 0.0025,
                      [(zt, 0.0), (zt + 0.0009, 0.0006)], 0.003, 2, cap0=False)
    else:
        top_quad(tp, px - pw / 2, px + pw / 2, py - pd / 2 - 0.014, py + pd / 2, zt + 0.0004)
    parts.append(tp)
    # bracket handle at the front on wire links to the axes on the sides
    hd = P("laptop_handle", "grip")
    gy, gz, hx = y0 - 0.025, TOP + 0.013, 0.082
    pts = [(L.LXC - hx, gy + 0.004, gz), (L.LXC - 0.04, gy - 0.0005, gz), (L.LXC, gy - 0.0015, gz),
           (L.LXC + 0.04, gy - 0.0005, gz), (L.LXC + hx, gy + 0.004, gz)]
    pp = G.spline(pts, 2) if lod == 0 else pts
    d0 = (Vector(pp[0]) - Vector(pp[1])).normalized()
    d1 = (Vector(pp[-1]) - Vector(pp[-2])).normalized()
    pp = ([tuple(Vector(pp[0]) + d0 * 0.005), tuple(Vector(pp[0]) + d0 * 0.0028)] + list(pp) +
          [tuple(Vector(pp[-1]) + d1 * 0.0028), tuple(Vector(pp[-1]) + d1 * 0.005)])
    rad = [(0.0035, 0.0045), (0.0068, 0.0085)] + [(0.0080, 0.0100)] * (len(pp) - 4) + [(0.0068, 0.0085), (0.0035, 0.0045)]
    g.tube_var(hd, pp, rad, 8 if lod == 0 else 6)
    parts.append(hd)
    wr = P("laptop_bails", "wire")
    for s in (-1, 1):
        xe = L.LXC + s * hx
        xs = x0 if s < 0 else x1
        pv = (xs + s * 0.0055, y0 + 0.030, TOP + 0.019)
        bail = [(xe + s * 0.002, gy + 0.004, gz), (xe + s * 0.024, gy + 0.006, gz + 0.001),
                (xs - s * 0.012, y0 - 0.014, TOP + 0.016), (xs + s * 0.0045, y0 + 0.004, TOP + 0.018),
                (xs + s * 0.0055, y0 + 0.020, TOP + 0.019), pv]
        G.cord(wr, bail, 0.0022, 5 if lod == 0 else 4, k=3 if lod == 0 else 1)
        if lod == 0:
            g.cyl(wr, (xs + s * 0.0025, pv[1], pv[2]), "x", 0.0055, 0.005, 8)
    parts.append(wr)
    if lod == 1:
        return parts
    # small things of the near LOD: latches, bezel screws, a grille, the power socket
    lt = P("laptop_latches", "grip")
    G.rbox(lt, L.LXC - 0.026, L.LXC + 0.026, y0 - 0.005, y0 + 0.003, TOP + 0.007, TOP + 0.028, 0.002, 1)
    G.rbox(lt, L.LXC - 0.024, L.LXC + 0.024, L.LID_D - 0.010, L.LID_D + 0.004, -0.015, 0.004, 0.003, 1, frame=fr)
    parts.append(lt)
    sw = P("laptop_screws", "black")
    for a in (x0 + 0.009, x1 - 0.009):
        for b in (0.014, L.LID_D / 2, L.LID_D - 0.012):
            G.disk(sw, fr.p(a, b, 0.0004), fr.n, 0.0024, 6)
    for a in (L.LXC - 0.10, L.LXC + 0.10):
        G.disk(sw, fr.p(a, 0.016, 0.0004), fr.n, 0.0024, 6)
    for k in range(5):                                                         # grille on the left side
        yy = y0 + 0.05 + 0.011 * k
        g.box(sw, x0 - 0.0008, x0 + 0.001, yy, yy + 0.006, TOP + 0.022, TOP + 0.030)
    jx, jy, jz = L.DC_JACK
    G.lathe(sw, [(0.0048, 0.0), (0.0048, 0.010), (0.0040, 0.014), (0.0030, 0.020)], 8, center=(jx - 0.0005, jy, jz),
            axis="-x", cap1=True)
    parts.append(sw)
    return parts


def build_psu(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    x, y, ln, w, h = L.BRICK_PSU
    ps = P("psu", "psu")
    G.rbox(ps, x - ln / 2, x + ln / 2, y - w / 2, y + w / 2, TOP, TOP + h, 0.008 if lod == 0 else 0.006,
           2 if lod == 0 else 1)
    parts = [ps]
    if lod == 0:
        bt = P("psu_boots", "black")
        for s, ax in ((-1, "-x"), (1, "x")):
            G.lathe(bt, [(0.0062, 0.0), (0.0056, 0.008), (0.0040, 0.016), (0.0032, 0.022)], 8,
                    center=(x + s * (ln / 2 - 0.002), y, TOP + h / 2), axis=ax, cap1=True)
        lb = P("psu_label", "tag")
        G.flat_rr(lb, x - 0.045, x + 0.045, y - 0.022, y + 0.022, TOP + h + 0.0003, 0.003, 1)
        parts += [bt, lb]
    return parts


# =============================================================================
# R-159 radio
# =============================================================================
def build_radio(spec):
    lod = spec["lod"]
    x0, x1, y0, y1 = L.RX0, L.RX1, L.RY0, L.RY1
    bi, zs, z1 = L.BAT_IN, L.RZS, L.RZ1
    parts = []
    lo = P("radio_bat", "radio")
    up = P("radio_body", "radio_front")
    if lod == 0:
        G.rr_loft(lo, x0 + bi, x1 - bi, y0 + bi, y1 - bi, [(TOP, 0.004), (TOP + 0.0012, 0.0012), (TOP + 0.004, 0.0),
                                                         (zs - 0.008, 0.0)], 0.013, 3)
        # top of the body with a bead, the panel is recessed
        G.rr_loft(up, x0, x1, y0, y1, [(zs + 0.006, 0.0), (z1 - 0.0145, 0.0), (z1 - 0.013, -0.0016),
                                        (z1 - 0.0025, -0.0016), (z1, 0.0008), (z1, 0.0065), (z1 - 0.003, 0.0095)],
                  0.014, 3)
    elif lod == 1:
        G.rr_loft(lo, x0 + bi, x1 - bi, y0 + bi, y1 - bi, [(TOP, 0.0), (zs - 0.008, 0.0)], 0.013, 1)
        G.rr_loft(up, x0, x1, y0, y1, [(zs + 0.006, 0.0), (z1, 0.0), (z1, 0.008), (z1 - 0.003, 0.0095)], 0.014, 1)
    else:
        g.box(lo, x0 + bi, x1 - bi, y0 + bi, y1 - bi, TOP, zs)
        g.box(up, x0, x1, y0, y1, zs, z1)
    parts += [lo, up]
    lx, ly = L.R_LAMP
    lp = P("radio_lamp", "lamp_r", group=SEL_BLINK)
    if lod == 2:
        top_quad(lp, lx - 0.005, lx + 0.005, ly - 0.005, ly + 0.005, z1 + 0.001)
    else:
        G.lathe(lp, [(0.0058, 0.0), (0.0058, 0.0050), (0.0049, 0.0078), (0.0030, 0.0096)], 10 if lod == 0 else 6,
                center=(lx, ly, ZP + 0.0025), cap1=True)
    parts.append(lp)
    if lod == 2:
        return parts
    # crimp belt between the compartment and the transceiver
    sm = P("radio_seam", "radio_seam")
    G.rr_loft(sm, x0 - 0.0012, x1 + 0.0012, y0 - 0.0012, y1 + 0.0012,
              [(zs - 0.0085, 0.0012), (zs - 0.007, 0.0), (zs + 0.007, 0.0), (zs + 0.0085, 0.0012)] if lod == 0 else
              [(zs - 0.008, 0.0), (zs + 0.008, 0.0)], 0.0152, 3 if lod == 0 else 1)
    parts.append(sm)
    # stamped ribs on the face and back (at the mid LOD only the face, as boxes)
    for s, sg in (("f", -1), ("b", 1))[:2 if lod == 0 else 1]:
        rb = P("radio_ribs_" + s, "radio")
        faces = [(z, y0 if sg < 0 else y1) for z in L.RIBS_UP] + [(z, y0 + bi if sg < 0 else y1 - bi) for z in L.RIBS_LO]
        for (za, zb), yf in faces:
            ff = G.face_frame(yf, sg)
            if lod == 0 and sg < 0:
                G.rr_loft(rb, x0 + 0.022, x1 - 0.022, za, zb, [(0.0, 0.0), (0.0022, 0.0010), (0.0034, 0.0032)],
                          (zb - za) * 0.46, 2, frame=ff, cap0=False)
            elif lod == 0:
                G.rr_loft(rb, x0 + 0.022, x1 - 0.022, za, zb, [(0.0, 0.0), (0.0034, 0.0018)], 0.005, 1, frame=ff,
                          cap0=False)
            else:
                g.box(rb, x0 + 0.022, x1 - 0.022, za, zb, 0.0, 0.003, frame=ff)
        parts.append(rb)
    # panel on top (a decal: wafer switch windows with digits, the volume scale, socket frames)
    pn = P("radio_panel", "radio_top")
    px0, px1, py0, py1 = L.R_PANEL
    G.rr_loft(pn, px0, px1, py0, py1, [(z1 - 0.0035, 0.0), (ZP, 0.0)], 0.005, 2, cap0=False)
    parts.append(pn)
    # lid-handle at the back
    hx0, hx1, hy0, hy1 = L.R_HANDLE
    hb = P("radio_handle", "radio")
    G.rbox(hb, hx0, hx1, hy0, hy1, ZP - 0.002, ZP + 0.024, 0.0065 if lod == 0 else 0.004, 2 if lod == 0 else 1)
    parts.append(hb)
    cx, cy = L.R_CONN
    ax, ay = L.R_ANT
    if lod == 1:
        cn = P("radio_conn", "chrome")
        g.cyl(cn, (cx, cy, ZP + 0.015), "z", 0.019, 0.030, 8)
        g.cyl(cn, (ax, ay, ZP + 0.016), "z", 0.012, 0.032, 6)
        pg = P("radio_plug", "black")
        g.cyl(pg, (cx, cy, ZP + 0.045), "z", 0.015, 0.030, 8)
        g.cyl(pg, (ax, ay, ZP + 0.045), "z", 0.009, 0.026, 6)
        kn = P("radio_knobs", "knob")
        g.cyl(kn, (L.R_KNOB[0], L.R_KNOB[1], ZP + 0.008), "z", 0.011, 0.016, 8)
        parts += [cn, pg, kn]
        return parts
    # headset connector: flange, body, ribbed nut, the PTT cord fork
    cn = P("radio_conn", "chrome")
    G.lathe(cn, [(0.0215, 0.0), (0.0215, 0.003), (0.0178, 0.0042), (0.0178, 0.016)], 12, center=(cx, cy, ZP), cap1=True)
    G.knurl(cn, (cx, cy, ZP), "z", 0.0188, 0.016, 0.029, 9, 0.0011)
    pg = P("radio_plug", "black")
    G.lathe(pg, [(0.0150, 0.0), (0.0150, 0.014), (0.0128, 0.021), (0.0080, 0.031), (0.0060, 0.040)], 12,
            center=(cx, cy, ZP + 0.029), cap1=True)
    # antenna input: white insulator, bushing, ribbed nut, the coax fork
    iw = P("radio_ant_ins", "white")
    G.lathe(iw, [(0.0175, 0.0), (0.0175, 0.0035), (0.0150, 0.0055), (0.0150, 0.0095), (0.0128, 0.0115),
                 (0.0110, 0.013)], 12, center=(ax, ay, ZP), cap1=True)
    G.lathe(cn, [(0.0105, 0.013), (0.0105, 0.023), (0.0088, 0.0255), (0.0088, 0.032)], 10, center=(ax, ay, ZP),
            cap1=True)
    G.knurl(cn, (ax, ay, ZP), "z", 0.0108, 0.032, 0.043, 7, 0.0008)
    G.lathe(pg, [(0.0090, 0.0), (0.0090, 0.006), (0.0068, 0.012), (0.0052, 0.020)], 10, center=(ax, ay, ZP + 0.043),
            cap1=True)
    # orange terminals on brass posts
    tm = P("radio_terms", "orange")
    br = P("radio_brass", "brass")
    for tx, ty in L.R_TERM:
        G.lathe(br, [(0.0062, 0.0), (0.0062, 0.0035), (0.0040, 0.0045), (0.0040, 0.0090)], 8, center=(tx, ty, ZP),
                cap1=True)
        G.knurl(tm, (tx, ty, ZP), "z", 0.0095, 0.009, 0.0215, 8, 0.0009)
        G.lathe(tm, [(0.0086, 0.0215), (0.0070, 0.0245), (0.0040, 0.0260)], 8, center=(tx, ty, ZP), cap1=True)
    # frequency wafer switches (the pointer is towards the digit window) and the volume knob
    kn = P("radio_knobs", "knob")
    for sx, sy in L.R_SWITCH:
        G.lathe(kn, [(0.0105, 0.0), (0.0105, 0.0025), (0.0080, 0.0035), (0.0068, 0.0128)], 8, center=(sx, sy, ZP),
                cap1=True)
        g.box(kn, sx - 0.0011, sx + 0.0011, sy, sy + 0.0076, ZP + 0.0122, ZP + 0.0140)
    kx_, ky_ = L.R_KNOB
    G.knurl(kn, (kx_, ky_, ZP), "z", 0.0112, 0.0, 0.015, 8, 0.0009)
    G.lathe(kn, [(0.0104, 0.015), (0.0085, 0.0172), (0.0040, 0.0180)], 8, center=(kx_, ky_, ZP), cap1=True)
    # lamp bezel
    G.lathe(cn, [(0.0090, 0.0), (0.0090, 0.0016), (0.0072, 0.0034), (0.0060, 0.0038)], 10, center=(lx, ly, ZP),
            cap1=True)
    parts += [cn, pg, iw, tm, br, kn]
    # lever latches of the compartment at the sides: a body on the transceiver, a lever across the belt,
    # a hook on the compartment
    lt = P("radio_latches", "radio_seam")
    for xs, sg in ((x0, -1), (x1, 1)):
        xb = xs - sg * bi                                    # side of the compartment
        for yy in (y0 + 0.042, y1 - 0.042):
            g.box(lt, *sorted((xs - sg * 0.0005, xs + sg * 0.004)), yy - 0.013, yy + 0.013, zs + 0.012, zs + 0.034)
            g.box(lt, *sorted((xs + sg * 0.0012, xs + sg * 0.0075)), yy - 0.0095, yy + 0.0095, zs - 0.024, zs + 0.020)
            g.box(lt, *sorted((xb - sg * 0.0005, xb + sg * 0.0045)), yy - 0.011, yy + 0.011, zs - 0.032, zs - 0.020)
    parts.append(lt)
    # empty nameplate on rivets on the right side
    tg = P("radio_tag", "tag")
    ty, tz, tw, th = L.R_TAG
    G.rbox(tg, x1 - 0.0005, x1 + 0.0012, ty - tw / 2, ty + tw / 2, tz - th / 2, tz + th / 2, 0.0006, 1)
    for dy in (-tw / 2 + 0.005, tw / 2 - 0.005):
        for dz in (-th / 2 + 0.005, th / 2 - 0.005):
            G.disk(tg, (x1 + 0.0013, ty + dy, tz + dz), (1, 0, 0), 0.0016, 6)
    parts.append(tg)
    return parts


# =============================================================================
# Headset on the radio and PTT key on the table
# =============================================================================
HS_YF, HS_YB = L.RY0 - 0.004, L.RY1 + 0.004                    # cups over the ribs (they protrude 3.4 mm)


def tangent_frame():
    tx, ty, deg = L.TANGENT
    return G.turn(tx, ty, TOP, deg)


def headset_cup(name, y_face, sg, lod):
    """Telephone cup at the face y_face (sg = -1 on the front, +1 on the back): rubber pad, body, boss."""
    x, z = L.HS_X, L.HS_Z
    c = (x, y_face, z)
    axis = "y" if sg > 0 else "-y"
    cp = P(name, "rubber")
    if lod == 0:
        G.lathe(cp, [(0.0205, 0.0), (0.0330, 0.0010), (0.0385, 0.0066), (0.0360, 0.0110), (0.0305, 0.0124)], 16,
                center=c, axis=axis)
        use(cp, "black")
        G.lathe(cp, [(0.0310, 0.0122), (0.0322, 0.0172), (0.0290, 0.0238), (0.0118, 0.0296)], 16, center=c, axis=axis,
                cap1=True)
        G.lathe(cp, [(0.0112, 0.0294), (0.0112, 0.0338), (0.0082, 0.0358)], 8, center=c, axis=axis, cap1=True)
    else:
        G.lathe(cp, [(0.0380, 0.0), (0.0380, 0.012)], 7, center=c, axis=axis, cap1=True)
        use(cp, "black")
        G.lathe(cp, [(0.0310, 0.012), (0.0300, 0.028), (0.0120, 0.032)], 7, center=c, axis=axis, cap1=True)
    return cp


def build_headset(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = [headset_cup("hs_cup_f", HS_YF, -1, lod), headset_cup("hs_cup_b", HS_YB, 1, lod)]
    x, z = L.HS_X, L.HS_Z
    # double headband across the top: flat straps from the cup on the front over the edge to the cup on
    # the back
    half = [(HS_YF - 0.018, z + 0.030), (HS_YF - 0.016, z + 0.046), (HS_YF - 0.008, ZP + 0.010),
            (HS_YF + 0.016, ZP + 0.040), (L.RYC - 0.035, ZP + 0.051)]
    prof = half + [(L.RYC, ZP + 0.0535)] + [(L.RY0 + L.RY1 - yy, zz) for yy, zz in reversed(half)]
    bd = P("hs_band", "black")
    for dx in (-0.0045, 0.0045):
        pts = [(x + dx, yy, zz) for yy, zz in prof]
        pp = G.spline(pts, 2) if lod == 0 else pts
        g.tube_var(bd, pp, [(0.0040, 0.0013)] * len(pp), 4)
    parts.append(bd)
    # cords: cup -> fork in the PTT socket (across the table), PTT key -> fork of the connector on the
    # radio
    fr = tangent_frame()
    k = 4 if lod == 0 else 1
    e1 = fr.p(0.044, 0.0, 0.053)
    cordp = [(x, HS_YF - 0.024, z - 0.030), (x - 0.003, HS_YF - 0.034, z - 0.090), (x - 0.006, HS_YF - 0.050, TOP + 0.12),
             (x - 0.004, HS_YF - 0.066, TOP + 0.0032), (e1.x - 0.030, e1.y + 0.060, TOP + 0.0032),
             (e1.x - 0.010, e1.y + 0.022, TOP + 0.030), tuple(e1)]
    hc = P("hs_cord", "cable")
    G.cord(hc, cordp if lod == 0 else cordp[::2] + [cordp[-1]], 0.0026, 5 if lod == 0 else 4, k=k)
    parts.append(hc)
    e2 = fr.p(-0.089, 0.0, 0.014)
    cx, cy = L.R_CONN
    pttp = [tuple(e2), (e2.x - 0.012, e2.y + 0.020, TOP + 0.0034), (e2.x - 0.050, e2.y + 0.070, TOP + 0.0034),
            (L.RX0 - 0.016, L.RY0 + 0.020, TOP + 0.0034), (L.RX0 - 0.016, cy - 0.010, TOP + 0.050),
            (L.RX0 - 0.013, cy, L.RZ1 - 0.060), (L.RX0 - 0.006, cy, ZP + 0.060), (cx - 0.016, cy, ZP + 0.084),
            (cx, cy, ZP + 0.080), (cx, cy, ZP + 0.069)]
    pc = P("ptt_cord", "cable")
    G.cord(pc, pttp if lod == 0 else pttp[::2] + [pttp[-1]], 0.0032, 5 if lod == 0 else 4, k=k)
    parts.append(pc)
    return parts


def build_tangent(spec):
    """PTT key (photo): a moulded grey body with rounded ends, a ribbed key on top, a headset socket
    with a fork at the front end, a cord entry with a cap at the back.
    """
    lod = spec["lod"]
    if lod == 2:
        return []
    fr = tangent_frame()
    tg = P("tangent", "tangent")
    if lod == 0:
        G.rr_loft(tg, -0.066, 0.066, -0.027, 0.027, [(0.0, 0.0055), (0.0025, 0.0016), (0.006, 0.0), (0.021, 0.0),
                                                    (0.0265, 0.0028), (0.0300, 0.0080), (0.0312, 0.0130)], 0.024, 3,
                  frame=fr)
    else:
        G.rr_loft(tg, -0.066, 0.066, -0.027, 0.027, [(0.0, 0.0), (0.028, 0.0)], 0.022, 1, frame=fr)
    parts = [tg]
    if lod == 0:
        tk = P("tangent_key", "knob")
        G.rr_loft(tk, -0.044, 0.010, -0.0125, 0.0125, [(0.0285, 0.0), (0.0336, 0.0010), (0.0346, 0.0026)], 0.008, 2,
                  frame=fr, cap0=False)
        for i in range(5):
            a = -0.036 + 0.0095 * i
            g.box(tk, a - 0.0012, a + 0.0012, -0.0085, 0.0085, 0.0340, 0.0358, frame=fr)
        cn = P("tangent_socket", "chrome")
        G.lathe(cn, [(0.0088, 0.0), (0.0088, 0.0032), (0.0072, 0.0044)], 12, center=(0.044, 0.0, 0.0290), cap1=True,
                frame=fr)
        bt = P("tangent_boots", "black")
        G.lathe(bt, [(0.0064, 0.0), (0.0064, 0.010), (0.0052, 0.015), (0.0040, 0.021)], 10, center=(0.044, 0.0, 0.0320),
                cap1=True, frame=fr)
        G.lathe(bt, [(0.0082, 0.0), (0.0076, 0.008), (0.0054, 0.018), (0.0040, 0.026)], 10, center=(-0.063, 0.0, 0.014),
                axis="-x", cap1=True, frame=fr)
        parts += [tk, cn, bt]
    return parts


# =============================================================================
# Left on the boards: tablet with a map, mug
# =============================================================================
def build_desk_bits(spec):
    lod = spec["lod"]
    bw, bh = L.MAP_BOARD
    pw, ph, off = L.MAP_PAPER
    fm = G.turn(L.MAP_C[0], L.MAP_C[1], TOP_B, L.MAP_DEG)
    cb = P("clipboard", "clipboard")
    if lod == 0:
        G.rr_loft(cb, -bw / 2, bw / 2, -bh / 2, bh / 2, [(0.0, 0.0012), (0.0012, 0.0), (MAP_T - 0.0012, 0.0),
                                                        (MAP_T, 0.0012)], 0.012, 2, frame=fm)
    else:
        g.box(cb, -bw / 2, bw / 2, -bh / 2, bh / 2, 0.0, MAP_T, frame=fm)
    pp = P("map_paper", "paper")
    g.box(pp, -pw / 2, pw / 2, off - ph / 2, off + ph / 2, MAP_T, MAP_T + PAPER_T, frame=fm)
    parts = [cb, pp]
    if lod < 2:
        # spring clip: a plate on rivets, a spring axis, a jaw on the paper, a wire loop
        cl = P("clip", "chrome")
        yb = bh / 2 - 0.013
        G.rbox(cl, -0.058, 0.058, bh / 2 - 0.024, bh / 2 - 0.004, MAP_T, MAP_T + 0.0016, 0.0008 if lod == 0 else 0.0, 1,
               frame=fm)
        if lod == 0:
            g.cyl(cl, (0.0, yb, MAP_T + 0.0055), "x", 0.0042, 0.104, 10, frame=fm)
            jaw = [fm.p(0.0, yb - 0.002, MAP_T + 0.0090), fm.p(0.0, yb - 0.012, MAP_T + 0.0072),
                   fm.p(0.0, yb - 0.026, MAP_T + 0.0035), fm.p(0.0, yb - 0.036, MAP_T + PAPER_T + 0.0008)]
            G.ribbon(cl, G.spline(jaw, 3), fm.u, 0.050, 0.0006)
            loop = [(-0.032, yb, MAP_T + 0.006), (-0.034, yb + 0.006, MAP_T + 0.020), (-0.020, yb + 0.010, MAP_T + 0.026),
                    (0.020, yb + 0.010, MAP_T + 0.026), (0.034, yb + 0.006, MAP_T + 0.020), (0.032, yb, MAP_T + 0.006)]
            G.cord(cl, [tuple(fm.p(*p)) for p in loop], 0.0014, 4, k=2)
            for a in (-0.045, 0.045):
                G.disk(cl, fm.p(a, bh / 2 - 0.009, MAP_T + 0.0017), fm.n, 0.0022, 6)
        parts.append(cl)
    # mug: enamel outside, rolled rim, enamel inside, tea, a strap handle
    mx, my, mr, mh = L.MUG
    z0 = TOP_B
    mg = P("mug", "mug")
    if lod == 0:
        G.lathe(mg, [(mr - 0.006, 0.0), (mr - 0.0018, 0.0006), (mr - 0.0002, 0.003), (mr, 0.008), (mr, mh - 0.006)], 14,
                center=(mx, my, z0), cap0=True)
        rm = P("mug_rim", "mug_rim")
        G.lathe(rm, [(mr, mh - 0.006), (mr + 0.0006, mh - 0.0042), (mr + 0.0011, mh - 0.0020), (mr + 0.0006, mh - 0.0003),
                     (mr - 0.0011, mh), (mr - 0.0024, mh - 0.0013), (mr - 0.0026, mh - 0.0055)], 14, center=(mx, my, z0))
        G.lathe(mg, [(mr - 0.0026, mh - 0.0055), (mr - 0.0026, mh - 0.022)], 14, center=(mx, my, z0))
        te = P("mug_tea", "tea")
        G.disk(te, (mx, my, z0 + mh - 0.022), (0, 0, 1), mr - 0.0026, 14, phase=0.5)
        parts += [mg, rm, te]
    else:
        g.cyl(mg, (mx, my, z0 + mh / 2), "z", mr, mh, 8 if lod == 1 else 6)
        parts.append(mg)
    if lod < 2:
        hd = P("mug_handle", "mug")
        a = math.radians(45.0)
        ux, uy = math.cos(a), math.sin(a)
        hp = [(mx + ux * (mr - 0.002), my + uy * (mr - 0.002), z0 + mh - 0.015),
              (mx + ux * (mr + 0.016), my + uy * (mr + 0.016), z0 + mh - 0.016),
              (mx + ux * (mr + 0.027), my + uy * (mr + 0.027), z0 + mh - 0.030),
              (mx + ux * (mr + 0.026), my + uy * (mr + 0.026), z0 + 0.040),
              (mx + ux * (mr + 0.014), my + uy * (mr + 0.014), z0 + 0.024),
              (mx + ux * (mr - 0.002), my + uy * (mr - 0.002), z0 + 0.021)]
        hp = G.spline(hp, 2) if lod == 0 else hp
        g.tube_var(hd, hp, [(0.0062, 0.0026)] * len(hp), 6 if lod == 0 else 4)
        parts.append(hd)
    return parts


# =============================================================================
# Mast in a sand crate, guy lines, bricks
# =============================================================================
COAX_DIR = Vector((math.cos(math.radians(165.0)), math.sin(math.radians(165.0)), 0.0))   # direction of the coax up the mast


def mast_pt(r, z):
    return (L.MX + COAX_DIR.x * r, L.MY + COAX_DIR.y * r, z)


def build_mast(spec):
    lod = spec["lod"]
    bx0, bx1, by0, by1, bh = L.BALLAST
    T = 0.018
    parts = []
    if lod == 2:
        b = P("ballast", "ballast")
        g.box(b, bx0, bx1, by0, by1, 0.0, bh)
        parts.append(b)
    else:
        for s, box in (("f", (bx0, bx1, by0, by0 + T)), ("b", (bx0, bx1, by1 - T, by1)),
                       ("l", (bx0, bx0 + T, by0 + T, by1 - T)), ("r", (bx1 - T, bx1, by0 + T, by1 - T))):
            w = P("ballast_" + s, "ballast")
            if lod == 0:
                for za, zb in ((0.0, bh / 2 - 0.0015), (bh / 2 + 0.0015, bh)):         # wall of two boards
                    G.rbox(w, *box, za, zb, 0.0025 if s in "fr" else 0.0, 1)
            else:
                g.box(w, *box, 0.0, bh)
            parts.append(w)
        sd = P("sand", "sand")
        if lod == 0:
            def sand_z(x, y):
                d = math.hypot(x - L.MX, y - L.MY)
                return (L.SAND_Z + 0.004 * math.sin(37 * x + 11 * y) * math.cos(23 * y - 7 * x) +
                        0.014 * math.exp(-(d / 0.045) ** 2))
            G.grid(sd, bx0 + T, bx1 - T, by0 + T, by1 - T, 6, 6, sand_z)
            nl = P("ballast_nails", "nail")
            for xx in (bx0 + 0.009, bx1 - 0.009):
                for zz in (0.06, 0.18):
                    G.disk(nl, (xx, by0 - 0.0004, zz), (0, -1, 0), 0.0035, 6)
                    G.disk(nl, (xx, by1 + 0.0004, zz), (0, 1, 0), 0.0035, 6)
            parts.append(nl)
        else:
            top_quad(sd, bx0 + T, bx1 - T, by0 + T, by1 - T, L.SAND_Z)
        parts.append(sd)
    sides = 12 if lod == 0 else (8 if lod == 1 else 5)
    for i, (r, z0, z1) in enumerate(L.MAST):
        ms = P("mast%d" % i, "mast")
        g.pipe(ms, [(L.MX, L.MY, z0), (L.MX, L.MY, z1)], r, sides)
        parts.append(ms)
    if lod < 2:
        hw = P("mast_hw", "steel_dark")
        for (r, z0, z1), rin, rout in zip(L.COLLARS, (L.MAST[0][0], L.MAST[1][0]), (L.MAST[1][0], L.MAST[2][0])):
            if lod == 0:
                # clamp of a section: chamfers, a wing nut on the side
                G.lathe(hw, [(rin + 0.0005, z0 - 0.002), (r - 0.002, z0), (r, z0 + 0.003), (r, z1 - 0.003),
                             (r - 0.003, z1), (rout + 0.0005, z1 + 0.003)], 12, center=(L.MX, L.MY, 0.0))
                zc = (z0 + z1) / 2
                g.box(hw, L.MX + r - 0.001, L.MX + r + 0.012, L.MY - 0.003, L.MY + 0.003, zc - 0.004, zc + 0.004)
                g.box(hw, L.MX + r + 0.010, L.MX + r + 0.014, L.MY - 0.011, L.MY + 0.011, zc - 0.006, zc + 0.006)
            else:
                g.pipe(hw, [(L.MX, L.MY, z0), (L.MX, L.MY, z1)], r, sides)
        # guy ring
        r2, gz = L.MAST[2][0], L.GUY_Z
        if lod == 0:
            G.lathe(hw, [(r2 + 0.0004, gz - 0.008), (r2 + 0.0060, gz - 0.006), (r2 + 0.0075, gz - 0.003),
                         (r2 + 0.0075, gz + 0.003), (r2 + 0.0060, gz + 0.006), (r2 + 0.0004, gz + 0.008)], 12,
                    center=(L.MX, L.MY, 0.0))
        else:
            g.pipe(hw, [(L.MX, L.MY, gz - 0.006), (L.MX, L.MY, gz + 0.006)], r2 + 0.0075, sides)
        parts.append(hw)
    # pin insulator, coax entry, a pin with a ball
    ab = P("ant_base", "ant")
    z0, z1 = L.ANT_BASE
    if lod == 0:
        G.lathe(ab, [(0.0145, z0), (0.0195, z0 + 0.004), (0.0195, z0 + 0.014), (0.0160, z0 + 0.018), (0.0180, z0 + 0.022),
                     (0.0180, z0 + 0.044), (0.0090, z1)], 10, center=(L.MX, L.MY, 0.0), cap1=True)
    else:
        g.pipe(ab, [(L.MX, L.MY, z0), (L.MX, L.MY, z1)], 0.019, sides)
    parts.append(ab)
    if lod < 2:
        wp = P("ant_whip", "steel_dark")
        pts = [(L.MX, L.MY, z1 + (L.ANT_TOP - 0.006 - z1) * k / 4) for k in range(5)]
        g.tube_var(wp, pts, [(r, r) for r in (0.0042, 0.0036, 0.0031, 0.0027, 0.0024)], 6 if lod == 0 else 4)
        if lod == 0:
            G.lathe(wp, [(0.0012, L.ANT_TOP - 0.0085), (0.0040, L.ANT_TOP - 0.0070), (0.0046, L.ANT_TOP - 0.0040),
                         (0.0040, L.ANT_TOP - 0.0012), (0.0015, L.ANT_TOP)], 8, center=(L.MX, L.MY, 0.0), cap0=True,
                    cap1=True)
            cx_ = P("ant_conn", "chrome")
            G.lathe(cx_, [(0.0068, 0.0), (0.0068, 0.012), (0.0056, 0.016)], 10,
                    center=mast_pt(0.017, z0 + 0.024), axis=tuple(COAX_DIR), cap1=True)
            parts.append(cx_)
        parts.append(wp)
    return parts


def crate_loop():
    """Guy loop round the handle bar of the right crate (an ellipse round the section of the bar) and
    its top-outwards point.
    """
    xo = L.CRATES[1][1]
    cx = xo + (L.HANDLE_OUT[0] + L.HANDLE_OUT[1]) / 2
    cz = sum(L.HANDLE_Z) / 2
    rx = (L.HANDLE_OUT[1] - L.HANDLE_OUT[0]) / 2 + 0.0035
    rz = (L.HANDLE_Z[1] - L.HANDLE_Z[0]) / 2 + 0.0035
    pts = [(cx + rx * math.cos(2 * math.pi * k / 8 + math.pi / 4), -0.004 + 0.008 * k / 8,
            cz + rz * math.sin(2 * math.pi * k / 8 + math.pi / 4)) for k in range(9)]
    return pts, pts[0]


def guy_targets():
    """Where the guys go: a loop on the handle of the right crate and the top of two bricks at their end
    nearer the mast.
    """
    out = [crate_loop()[1]]
    for bx, by, deg in L.BRICKS:
        a = math.radians(deg)
        u = Vector((math.cos(a), math.sin(a), 0.0))
        to = Vector((L.MX - bx, L.MY - by, 0.0)).normalized()
        k = 1 if u.dot(to) > 0 else -1
        end = Vector((bx, by, 0.0)) + u * k * (L.BRICK[0] / 2 - 0.04)
        out.append((end.x, end.y, L.BRICK[2] + 0.003))
    return out


def build_guys(spec):
    lod = spec["lod"]
    parts = []
    if lod < 2:
        rp = P("guy_ropes", "rope")
        sl = P("guy_sliders", "slider")
        sides = 4 if lod == 0 else 3
        r2 = L.MAST[2][0]
        for gx, gy, gz in guy_targets():
            d = Vector((gx - L.MX, gy - L.MY, 0.0)).normalized()
            a = Vector((L.MX, L.MY, L.GUY_Z)) + d * (r2 + 0.009)
            b = Vector((gx, gy, gz))
            n = 9 if lod == 0 else 3
            pts = [a + (b - a) * (k / (n - 1)) + Vector((0, 0, -0.010 * math.sin(math.pi * k / (n - 1))))
                   for k in range(n)]
            g.pipe(rp, [tuple(p) for p in pts], 0.0022, sides)
            if lod == 0:
                # tension slider: the cord passes it and returns doubled to a knot
                t = 0.82
                s0 = a + (b - a) * t + Vector((0, 0, -0.010 * math.sin(math.pi * t)))
                u = (b - a).normalized()
                v = Vector((-u.y, u.x, 0.0)).normalized()
                w = u.cross(v).normalized()
                G.rbox(sl, -0.020, 0.020, -0.0065, 0.0065, -0.0022, 0.0022, 0.0015, 1, frame=g.Frame(s0, u, v, w))
                g.pipe(rp, [tuple(s0 + u * 0.016 + v * 0.004), tuple(b + v * 0.004 - u * 0.006)], 0.0020, 4)
        if lod == 0:
            g.pipe(rp, crate_loop()[0], 0.0022, 4)
            parts += [rp, sl]
        else:
            parts.append(rp)
    for i, (bx, by, deg) in enumerate(L.BRICKS):
        fr = G.turn(bx, by, 0.0, deg)
        bl, bw, bhh = L.BRICK
        bk = P("brick%d" % i, "brick")
        if lod == 0:
            G.rbox(bk, -bl / 2, bl / 2, -bw / 2, bw / 2, 0.0, bhh, 0.005, 2, frame=fr)
        else:
            g.box(bk, -bl / 2, bl / 2, -bw / 2, bw / 2, 0.0, bhh, frame=fr)
        parts.append(bk)
        if lod == 0:
            # the guy is wound round the brick
            rl = P("brick%d_rope" % i, "rope")
            a = math.radians(deg)
            u = Vector((math.cos(a), math.sin(a), 0.0))
            k = 1 if u.dot(Vector((L.MX - bx, L.MY - by, 0.0))) > 0 else -1
            lu = k * (bl / 2 - 0.04)
            loop = [fr.p(lu, -bw / 2 - 0.003, bhh + 0.003), fr.p(lu + 0.002, -bw / 2 - 0.0035, bhh / 2),
                    fr.p(lu + 0.004, -bw / 2 - 0.003, 0.003), fr.p(lu + 0.008, bw / 2 + 0.003, 0.003),
                    fr.p(lu + 0.010, bw / 2 + 0.0035, bhh / 2), fr.p(lu + 0.012, bw / 2 + 0.003, bhh + 0.003),
                    fr.p(lu, -bw / 2 - 0.003, bhh + 0.003)]
            g.pipe(rl, [tuple(p) for p in loop], 0.0024, 5)
            parts.append(rl)
    return parts


# =============================================================================
# Under the table: extension reel, spare battery compartment
# =============================================================================
def build_reel(spec):
    lod = spec["lod"]
    r = L.REEL
    x, y, z, w = r["x"], r["y"], r["z"], r["w"]
    R, fl = r["r"], r["flange"]
    rs = 16 if lod == 0 else (8 if lod == 1 else 6)
    parts = []
    for s, sg in (("l", -1), ("r", 1)):
        f = P("reel_flange_" + s, "reel")
        if lod == 0:
            # cheek with a rolled edge and a hub
            G.lathe(f, [(0.016, 0.0), (R - 0.004, 0.0), (R, 0.003), (R - 0.004, fl), (0.030, fl),
                        (0.028, fl + 0.008), (0.012, fl + 0.010)], rs, center=(x + sg * (w / 2 - fl), y, z),
                    axis="x" if sg > 0 else "-x", cap1=True)
        else:
            g.cyl(f, (x + sg * (w / 2 - fl / 2), y, z), "x", R, fl, rs)
        parts.append(f)
    cl = P("reel_coil", "coil")
    hl = w / 2 - fl
    G.lathe(cl, [(r["coil"], -hl), (r["coil"] + 0.003, -hl * 0.5), (r["coil"] + 0.003, hl * 0.5), (r["coil"], hl)], rs,
            center=(x, y, z), axis="x")
    parts.append(cl)
    fr = P("reel_frame", "iron")
    ts = 6 if lod == 0 else 4
    k = 2 if lod == 0 else 1
    xs = (x - w / 2 - 0.016, x + w / 2 + 0.016)
    for xx in xs:
        G.cord(fr, [(xx, y - 0.125, 0.009), (xx, y - 0.070, 0.075), (xx, y - 0.014, z - 0.012), (xx, y, z + 0.030),
                    (xx, y, z + 0.20)], 0.0085, ts, k=k)
        G.cord(fr, [(xx, y + 0.125, 0.009), (xx, y + 0.070, 0.075), (xx, y + 0.014, z - 0.012), (xx, y + 0.002, z + 0.02)],
               0.0085, ts, k=k)
    g.pipe(fr, [(xs[0] - 0.008, y, z), (xs[1] + 0.008, y, z)], 0.009, ts)
    g.pipe(fr, [(xs[0], y, z + 0.20), (xs[1], y, z + 0.20)], 0.010, ts)
    parts.append(fr)
    sk = P("reel_socket", "socket")
    s0 = L.SOCK
    G.rbox(sk, s0[0], s0[1], s0[2], s0[3], s0[4], s0[5], 0.006 if lod == 0 else 0.0, 1)
    parts.append(sk)
    if lod == 2:
        return parts
    bl = P("reel_black", "black")
    if lod == 0:
        g.pipe(bl, [(x - 0.05, y, z + 0.20), (x + 0.05, y, z + 0.20)], 0.015, 8)               # carrying handle
        for yy in (0.055, 0.105):                                                               # sockets
            G.lathe(bl, [(0.019, 0.0), (0.019, 0.0025), (0.016, 0.003)], 10, center=(s0[1], yy, 0.150), axis="x",
                    cap1=True)
        # crank on the left cheek: a lever and a handle
        xo = x - w / 2 - 0.003
        a = math.radians(-125.0)
        tip = (y + 0.085 * math.cos(a), z + 0.085 * math.sin(a))
        cr = P("reel_crank", "iron")
        g.pipe(cr, [(xo - 0.002, y, z), (xo - 0.002, tip[0], tip[1])], 0.0045, 6)
        G.lathe(bl, [(0.0075, 0.0), (0.0085, 0.010), (0.0085, 0.032), (0.0060, 0.038)], 8,
                center=(xo - 0.004, tip[0], tip[1]), axis="-x", cap1=True)
        parts.append(cr)
    # plug from the power supply in the lower socket (goes into the block from the side)
    G.lathe(bl, [(0.0165, 0.0), (0.0165, 0.018), (0.0135, 0.026), (0.0070, 0.034), (0.0050, 0.042)], 10 if lod == 0 else 6,
            center=(s0[1], 0.105, 0.150), axis="x", cap1=True)
    parts.append(bl)
    return parts


def build_spare(spec):
    """Spare R-159 battery compartment under the table: the same body with ribs, turned along the depth;
    a handle and a connector.
    """
    lod = spec["lod"]
    x0, x1, y0, y1, h = L.SPARE
    fr = G.turn((x0 + x1) / 2, (y0 + y1) / 2, 0.0, 90.0)
    hl, hw = (y1 - y0) / 2, (x1 - x0) / 2
    bt = P("spare_bat", "radio")
    if lod == 0:
        G.rr_loft(bt, -hl, hl, -hw, hw, [(0.0, 0.004), (0.004, 0.0), (h - 0.006, 0.0), (h - 0.0015, 0.0015), (h, 0.005)],
                  0.013, 2, frame=fr)
    elif lod == 1:
        G.rr_loft(bt, -hl, hl, -hw, hw, [(0.0, 0.0), (h, 0.0)], 0.013, 1, frame=fr)
    else:
        g.box(bt, x0, x1, y0, y1, 0.0, h)
    parts = [bt]
    if lod == 2:
        return parts
    hd = P("spare_handle", "steel_dark")
    hp = [(-0.085, 0.0, h - 0.002), (-0.080, 0.0, h + 0.020), (-0.060, 0.0, h + 0.028), (0.060, 0.0, h + 0.028),
          (0.080, 0.0, h + 0.020), (0.085, 0.0, h - 0.002)]
    G.cord(hd, [tuple(fr.p(*p)) for p in hp], 0.0045, 6 if lod == 0 else 4, k=2 if lod == 0 else 1)
    parts.append(hd)
    if lod == 0:
        for a in (-0.085, 0.085):                                                  # handle lugs
            g.box(hd, a - 0.008, a + 0.008, -0.007, 0.007, h - 0.004, h + 0.006, frame=fr)
        rb = P("spare_ribs", "radio")
        for sv in (-1, 1):
            ff = G.compose(fr, (0.0, sv * hw, 0.0), (1, 0, 0), (0, 0, 1), (0, sv, 0))
            for za, zb in ((0.030, 0.058), (0.082, 0.110), (0.134, 0.162)):
                G.rr_loft(rb, -hl + 0.022, hl - 0.022, za, zb, [(0.0, 0.0), (0.0034, 0.0018)], 0.005, 1, frame=ff,
                          cap0=False)
        cn = P("spare_conn", "chrome")
        G.lathe(cn, [(0.014, 0.0), (0.014, 0.010), (0.011, 0.014), (0.011, 0.022)], 12, center=(0.115, 0.0, h - 0.001),
                cap1=True, frame=fr)
        parts += [rb, cn]
    return parts


# =============================================================================
# Wires
# =============================================================================
def build_wires(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    k = 4 if lod == 0 else 1

    def cab(name, pts, r, region="cable", sides=5):
        c = P(name, region)
        G.cord(c, pts if lod == 0 else pts[::2] + ([pts[-1]] if len(pts) % 2 == 0 else []), r, sides if lod == 0 else 4,
               k=k)
        parts.append(c)
    bx, by, bl, bw, bh = L.BRICK_PSU
    jx, jy, jz = L.DC_JACK
    # laptop -> power supply: from the socket on the left side backwards over the plywood
    cab("cable_laptop", [(jx - 0.020, jy, jz), (jx - 0.034, jy + 0.004, TOP + 0.0045), (jx - 0.040, jy + 0.030, TOP + 0.003),
                         (jx - 0.030, 0.050, TOP + 0.003), (bx - bl / 2 - 0.060, by - 0.015, TOP + 0.003),
                         (bx - bl / 2 - 0.030, by, TOP + 0.009), (bx - bl / 2 - 0.022, by, TOP + bh / 2)], 0.0028)
    # power supply -> plug in the extension block: backwards over the plywood, over the table edge down
    # and under the table
    s0 = L.SOCK
    cab("cable_psu", [(bx + bl / 2 + 0.022, by, TOP + bh / 2), (bx + bl / 2 + 0.040, by + 0.012, TOP + 0.006),
                      (-0.190, 0.300, TOP + 0.0038), (-0.195, 0.344, TOP + 0.0038), (-0.198, 0.356, TOP_B + 0.0038),
                      (-0.200, 0.392, TOP_B + 0.0038), (-0.202, 0.405, TOP_B - 0.012), (-0.205, 0.412, TOP_B - 0.10),
                      (-0.200, 0.402, 0.40), (-0.185, 0.372, 0.10), (-0.170, 0.320, 0.010), (-0.152, 0.230, 0.0040),
                      (-0.144, 0.150, 0.030), (-0.150, 0.112, 0.120), (-0.162, 0.105, 0.148),
                      (s0[1] + 0.042, 0.105, 0.150)], 0.0038)
    # coax: antenna input -> sags to the mast -> up the mast to the input at the insulator; goes round
    # the clamps
    ax, ay = L.R_ANT
    z0 = L.ANT_BASE[0]
    c0, c1 = Vector((ax + 0.030, ay + 0.010, ZP + 0.098)), Vector(mast_pt(0.050, 1.065))
    sag = [tuple(c0 + (c1 - c0) * (i / 6) - Vector((0, 0, 0.09 * 4 * (i / 6) * (1 - i / 6)))) for i in range(1, 6)]
    up_mast = [tuple(c1), mast_pt(0.0275, 1.092), mast_pt(0.0340, 1.123), mast_pt(0.0235, 1.165), mast_pt(0.0230, 1.400),
               mast_pt(0.0230, 1.680), mast_pt(0.0290, 1.741), mast_pt(0.0275, 1.785), mast_pt(0.0190, 1.830),
               mast_pt(0.0190, 1.905), mast_pt(0.0450, z0 + 0.005), mast_pt(0.0400, z0 + 0.022), mast_pt(0.0335, z0 + 0.024)]
    cab("cable_coax", [(ax, ay, ZP + 0.063), (ax + 0.006, ay + 0.004, ZP + 0.083), tuple(c0)] + sag + up_mast, 0.0045)
    if lod == 0:
        # tape: wraps the mast and the coax (a stadium in plan)
        tp = P("coax_tape", "tape")
        for zc, rt in ((1.30, L.MAST[1][0]), (1.55, L.MAST[1][0]), (1.87, L.MAST[2][0])):
            fr = g.Frame((L.MX, L.MY, 0.0), tuple(COAX_DIR), (-COAX_DIR.y, COAX_DIR.x, 0.0), (0, 0, 1))
            G.rr_loft(tp, -rt - 0.0012, rt + 0.0105, -rt - 0.0012, rt + 0.0012, [(zc - 0.012, 0.0), (zc + 0.012, 0.0)],
                      rt + 0.0011, 3, frame=fr)
        parts.append(tp)
    # generator cable: from the drum backwards along the floor, a plug at the end
    r = L.REEL
    cab("cable_gen", [(r["x"], r["y"] + 0.035, r["z"] - r["coil"] + 0.006), (r["x"] + 0.004, r["y"] + 0.075, 0.075),
                      (r["x"] + 0.008, r["y"] + 0.125, 0.0075), (r["x"] - 0.020, 0.330, 0.0075),
                      (r["x"] + 0.030, 0.470, 0.0075), (r["x"] + 0.020, 0.545, 0.0080), (r["x"] + 0.018, 0.574, 0.020)],
        0.0065, sides=6)
    gp = P("gen_plug", "black")
    if lod == 0:
        G.lathe(gp, [(0.0075, 0.0), (0.0110, 0.012), (0.0200, 0.016), (0.0200, 0.044), (0.0170, 0.048)], 12,
                center=(r["x"] + 0.018, 0.574, 0.020), axis="y", cap1=True)
        use(gp, "chrome")
        for dx in (-0.0095, 0.0095):
            g.cyl(gp, (r["x"] + 0.018 + dx, 0.574 + 0.057, 0.020), "y", 0.0024, 0.019, 6)
    else:
        g.cyl(gp, (r["x"] + 0.018, 0.598, 0.020), "y", 0.020, 0.045, 5)
    parts.append(gp)
    return parts


def build_lod(spec):
    parts = build_table(spec) + build_crates(spec) + build_laptop(spec) + build_psu(spec) + build_radio(spec)
    parts += build_headset(spec) + build_tangent(spec) + build_desk_bits(spec) + build_mast(spec) + build_guys(spec)
    parts += build_reel(spec) + build_spare(spec) + build_wires(spec)
    parts = [p for p in parts if p.bm.faces]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """The table with everything under it, up to the boards; a box above the table - the laptop and
    radio (extended downwards to a 0.5 m thickness); the mast crate - a 0.5 x 0.5 x 0.5 box around it.
    The mast, guys, bricks and wires have no collision (a component thinner than 0.5 m does not work).
    """
    wood = kx.PEN + r"\wood.rvmat"
    metal = kx.PEN + r"\metalplate.rvmat"
    tbl = kx.box_pts(L.TX0 - 0.03, L.TX1 + 0.01, L.TY0 - 0.01, L.TY1 + 0.01, 0.0, TOP_B)
    up = kx.box_pts(L.LX0 - 0.01, L.RX1 + 0.01, L.LY0 - 0.035, L.RY1 + 0.01, L.RZ1 + 0.02 - 0.50, L.RZ1 + 0.02)
    bal = kx.box_pts(L.MX - 0.25, L.MX + 0.25, L.MY - 0.25, L.MY + 0.25, 0.0, 0.50)
    comps = [(tbl, wood), (up, metal), (bal, wood)]
    memory = {
        "invView": [(-0.2, -2.6, 1.5)],
        "ce_center": [(0.0, 0.05, 0.8)],
        "ce_radius": [(1.2, 0.05, 0.8)],
    }
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2] + 0.004)
    return comps, 90.0, memory, bbox


# the first ones are for the --look preview: the table (and the screen, lamps in work), the laptop,
# overview, the radio, the tablet
SHOTS = [
    ("table", (-0.15, -1.35, 1.45), (-0.10, 0.0, 0.88), 34),
    ("laptop", (-0.38, -0.80, 1.16), (-0.37, -0.12, 0.86), 36),
    ("front", (-0.30, -3.4, 1.85), (0.0, 0.05, 1.0), 30),
    ("radio", (0.55, -0.72, 1.30), (0.18, 0.18, 1.0), 34),
    ("map", (-0.85, -0.74, 1.30), (-0.82, -0.04, 0.76), 36),
    ("mast", (2.3, -1.7, 1.5), (0.85, 0.1, 1.15), 28),
    ("under", (-0.10, -1.8, 0.48), (-0.20, 0.05, 0.30), 30),
    ("back", (1.5, 2.8, 1.8), (0.0, 0.1, 0.9), 30),
    ("left", (-2.7, -1.1, 1.5), (-0.3, 0.0, 0.85), 30),
]

M.look_shots = (5, 2)
M.run(build_lod, collision, SHOTS, row_step=2.6, row_shot=((2.6, -9.0, 2.4), (2.6, 0, 1.0)))
