"""M75 - Dosimeter (OZL_Tool_Dosimeter): a module of the "Khabar" line - a portable 2x2 item, it stands
in slot OZL_Tool1..3 of the line's packer (M13, M18) and is visible on its lid or roof through the
module_N proxy. Variant A: a portable DRG-01T1 dosimeter in a home-made box with a cradle and a
shield lid - the buyer's dosimeter, "does the khabar glow". It differs from M70 (the laboratory
"Beta" radiometer in a lead house): the device is portable, the box is a household wooden one.

    blender --background --python build_m75.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (switch panel, marker on the case, the
LCD "off", the sign and the tape of readings on the lead sheet, nail heads). The display frames for
the "working" state are drawn by the generator itself (lcd_frames.py, in Blender) - make_decals.py is
not needed for them.

Target: a device of ~0.21 x 0.04 x 0.08 m in a wooden or tin box ~0.22 x 0.08 x 0.12 m, a display -
digits; the module platform is ~0.2 x 0.2 m, up to ~0.25 m high.

Reference and sizes:
- the DRG-01T1 dosimeter (a CC BY-SA 3.0 Wikimedia Commons photo): dimensions 175 x 90 x 55 mm,
  0.6 kg per a shop catalogue; 169 x 76 x 46 mm, no more than 600 g per a lab card. There is no data
  sheet online (the type description did not open). Checked against the photo: the case without the
  strap screws is 1385 x 670 pixels, ratio 2.07; with the screws 1.94. 175 x 90 matches (90 includes
  the strap screws), 169 x 76 (2.22) does not. The model: the case is 175 x 85 mm, thickness 46 mm
  per the lab card (the catalogue's 55 is "not more than"): case 42 mm and a display visor of 4 mm;
- the face layout follows the photo (scale 7.91 pixels per mm): at the top a visor 68 x 46 mm with
  sloped walls, with a 49 x 17 mm LCD in it; below it a field for writing; the middle part is a 39 mm
  ridge with the switch panel, on the sides gutters ~6 mm deep: in the upper ones the "range" slider
  (mR/h, R/h, OFF - left) and the "mode" slider (MEASURE, SEARCH, CONTROL - right) in slots with a
  yellow window, in the lower ones the backlight and reset buttons; at the bottom the 33 mm battery
  cover behind a protruding belt, its screw in a half-round boss under the panel; the case corners are
  rounded in plan (~7 mm), the face edges ~3 mm;
- the case is grey-green (in the photo (143, 150, 131) against a background of (205, 202, 185) -
  ~(160, 168, 156) corrected for the background), not black as in the target: the model follows the
  device. In the photo the case is written on in violet marker - here only digits (an inventory
  number, a "tick 2" mark);
- a metal case, a "Korund" (Krona-type) 9 V battery, a carrying strap (shop listings).

The box is home-made, no data sheet, sizes derive from the device: a box of 8 mm pine boards on a 5 mm
plywood bottom, a foam cradle inside, the device lies display up with its face 7 mm above the rim
(the device is taken by the ends with fingers); 0.200 x 0.114 x 0.052 m. The lid-shield is an 8 mm
board on two surface hinges, thrown back by 100 degrees and standing behind the box; inside it is
covered with a 1.5 mm lead sheet on wallpaper nails - a radiation sign is slapped on the sheet in red
enamel, on the tape a column of readings in pencil. The lid is held by a wire stay on the left, a
turn-button at the front. Overall ~0.20 x 0.15 x 0.17 m. The device is longer than the box in the
target (0.22 x 0.12 with a device of 0.175 x 0.09), but 0.2 x 0.2 holds.

Detailing: "dayz" look (matte, dirtier, coloured AO). The device case is slabs with rounded corners in
plan and a rounded face edge, the visor with rounded corners and sloped outer walls; the boards of the
box and the lid have rounded (worn) edges; the hinges are three knuckles on an axis and screws in the
leaves; the turn-button is a bar with rounded ends on a screw; the wire stay is bent in loops under
the screw heads; the lead sheet is cut with shears (an uneven edge, cut corners), wallpaper nails with
round heads. Small items: on the lid under a black rubber band on two nails is a spare 9 V battery
(the vanilla DayZ 9v_battery proxy: the DRG-01T1 runs on a "Korund"); in the cradle in front of the
device is a stub of a hexagonal pencil used to write the readings on the tape.

Shared instruments and modules: used but intact - the case enamel rubbed down to aluminium at the
edges, the panel scratched; boards worn, nails with a rusty halo; the lead dull, a whitish oxide,
dents, scratches. No faction colour. Marks: display digits, a brushed radiation sign, a column of
digits on the tape, an inventory number in marker; the panel ticks and icons have no captions.

Machine states: the LCD display is ozl_screen, its own texture (section lcd, flat UV 0..1): "off" is
blank glass (decal_lcd_off.png), "working" is a backlight (rvmat _lcd_on with emission) and frames of
readings (lcd_frames, OZL_WorkFx frames). The "range" slider (upper left) is the bone ozl_switch: at
rest it stands at "OFF", when working it moves to "mR/h" (7.5 mm travel along the device, the
ozl_switch source is the OZL_WorkFx pose, like the M16 feed). There is no "working" atlas: when
working only the display (its own texture) and the slider change, so the state "on" is created only
for the preview (--look), to avoid baking and shipping an extra atlas in the mod.
LODs (a small item): near and middle (no chamfers, belt, nails, screws, slot windows, hinge
knuckles), no far one.

Blender axes: X is width (the device lies along X, the display on the right), Y is depth (the front
face is -Y), Z is up. The origin is the centre of the extent at the base: this is how the module
stands on the module_N proxy point (autocenter = 0 in Geometry). The device is not visible below the
foam - there is no geometry there.
"""
import math
import os
import random
import sys

import bmesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import kvanilla as kv  # noqa: E402
import kwood  # noqa: E402
import lcd_frames  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m --------------------------------------------------------------------------------
# box
OY = -0.015                             # the box is shifted forward: the open lid stands behind it
BX0, BX1 = -0.100, 0.100
BY0, BY1 = OY - 0.057, OY + 0.057
T = 0.008                               # wall boards
ZB = 0.005                              # plywood bottom
ZR = 0.052                              # top of the walls
IX0, IX1, IY0, IY1 = BX0 + T, BX1 - T, BY0 + T, BY1 - T
ZF = 0.046                              # top of the foam
ZF0 = 0.030                             # the foam is not visible below this
BOARD_R = 0.0016                        # worn board edges
# device: u runs along from the battery end to the display (+X), v across (to the right when the display
# is held up; in the world this is -Y), w from the bottom of the device up
DL, DW = 0.175, 0.085
DX0 = -DL / 2
ZD = 0.013                              # bottom of the device on the foam
WF, WC = 0.042, 0.036                   # case face, bottom of the side gutters
W0 = 0.026                              # below this it is in the foam
RH, RB = 0.007, 0.007                   # case corners in plan: the head (by the display), the compartment cover
VIS = (0.124, 0.170, 0.0345)            # visor: u0, u1, half-width
VIS_H = 0.004
LCD = (0.1385, 0.1555, 0.0245)          # display glass: u0, u1, half-width
LEG = (0.038, 0.095, 0.0175)            # switch panel
MARK = (0.110, 0.022, 0.060)            # marker: centre along u, height, width
SLIDE = [(-0.030, 0.0700), (0.030, 0.0775)]     # sliders: v, slider bottom along u; the first is "range" at "OFF"
SW_TRAVEL = 0.0075                      # "OFF" -> "mR/h": towards the top of the slot (0.069..0.085), along +u
SCREW_U = 0.0366                        # battery compartment cover screw
# display readings when working (mR/h, a dot after the first digit): measurement after measurement, the
# khabar glows slightly
LCD_VALUES = ["0152", "0148", "0155", "0161", "0157", "0150", "0163", "0158"]
LCD_PERIOD = 0.8                        # seconds per frame (OZL_WorkFx frames)
# lid
LID_T = 0.008
LID_A = math.radians(100.0)
PIV = Vector((0.0, BY1 + 0.0015, ZR))   # hinge axis
HINGE_X = (-0.060, 0.060)
KNUCKLES = ((-0.011, -0.0039), (-0.0035, 0.0035), (0.0039, 0.011))   # hinge knuckles from its middle
KN_R = 0.0019
LEAD = (0.088, 0.045, 0.0015)           # lead sheet: half-width, half-depth, thickness
TACKS = [(-0.083, -0.040), (0.083, -0.040), (-0.083, 0.040), (0.083, 0.040)]
# spare battery on the lid (closed-lid axes): between the sign (up to x -0.005) and the tape (from
# 0.034), the middle is 50 mm from the top edge of the sheet on the open lid; a rubber band across the
# battery
_BLO, _BHI = kv.box("battery9v")
BAT_HW, BAT_T = max(-_BLO[0], _BHI[0]), _BHI[2] - _BLO[2]
BAT_X = 0.0145
BAT_YC = OY - LEAD[1] + 0.050
BAND = (0.003, 0.0009)                  # rubber band: half-width, thickness
# pencil stub in the cradle: in the slot in front of the device, standing on edge, pressed 1 mm into the foam
PEN_R = 0.0035                          # across the hexagon corners; 6.1 mm across flats - the slot is 6.5
PEN_Y = (IY0 + OY - DW / 2) / 2
PEN_Z = ZF - 0.001 + PEN_R
PEN_X = (-0.072, 0.018, 0.033, 0.036)   # end, start of the sharpening, tip of the wood, tip of the lead

LOD_SPECS = [
    dict(lod=0, sides=12, seg=2),
    dict(lod=1, sides=6, seg=0),
]

REGIONS = {
    "case": ("case", 2.2), "legend": ("legend", 3.0), "lcd": ("lcd", 4.0), "knob": ("knob", 1.5),
    "amber": ("amber", 1.5), "screw": ("screw", 1.5), "wood_x": ("wood_x", 1.0), "wood_y": ("wood_y", 1.0),
    "wood_lid": ("wood_lid", 0.8), "ply": ("ply", 0.5), "foam": ("foam", 1.0), "lead": ("lead", 1.6),
    "tack": ("tack", 1.0), "hinge": ("hinge", 1.2), "wire": ("wire", 0.8), "latch": ("latch", 1.5),
    "band": ("band", 1.5), "pencil": ("pencil", 2.0), "pencil_wood": ("pencil_wood", 2.0),
    "graphite": ("graphite", 2.0), "inner": ("inner", 0.05),
}


def wdecal(name):
    return os.path.join(WORK, name)


def lid_matrix():
    """Rotation of the lid on its hinges: the front edge goes up and back (about the X axis)."""
    return Matrix.Translation(PIV) @ Matrix.Rotation(-LID_A, 4, "X") @ Matrix.Translation(-PIV)


_ROT = lid_matrix().to_3x3()
LID_N = tuple(_ROT @ Vector((0.0, 0.0, -1.0)))   # face of the lead sheet on the open lid (towards the viewer)
LID_UP = tuple(_ROT @ Vector((0.0, -1.0, 0.0)))  # up along the open lid


def lead_face():
    """The inner side of the lead sheet on the open lid: (centre z, height along z, min y, max y)."""
    m = lid_matrix()
    pts = [m @ Vector((0.0, OY + s * LEAD[1], ZR - LEAD[2])) for s in (-1, 1)]
    zs, ys = [p.z for p in pts], [p.y for p in pts]
    return (min(zs) + max(zs)) / 2, max(zs) - min(zs), min(ys), max(ys)


# decals on the device face: the images are drawn display up - the image "up" axis runs along world +X,
# "right" along -Y (a negative width is a mirror)
def face_decal(img, uc, length, width, w_face):
    return (wdecal(img), "z", 1, ("y", "x"), (OY, DX0 + uc), (-width, length),
            (ZD + w_face - 0.0005, ZD + w_face + 0.0009))


LEGEND_DEC = face_decal("decal_legend.png", (LEG[0] + LEG[1]) / 2, LEG[1] - LEG[0], 2 * LEG[2], WF)
MARKS_DEC = face_decal("decal_marks.png", MARK[0], MARK[1], MARK[2], WF)
_LZ, _LH, _LY0, _LY1 = lead_face()
LEAD_DEC = (wdecal("decal_lead.png"), "y", -1, ("x", "z"), (0.0, _LZ), (2 * LEAD[0], _LH), (_LY0 - 0.004, _LY1 + 0.004))
NAILS_F = (wdecal("decal_nails.png"), "y", -1, ("x", "z"), (0.0, ZB + 0.0235), (0.200, 0.047), (BY0 - 0.002, BY0 + 0.002))
NAILS_B = (wdecal("decal_nails.png"), "y", 1, ("x", "z"), (0.0, ZB + 0.0235), (-0.200, 0.047), (BY1 - 0.002, BY1 + 0.002))

# --- materials ------------------------------------------------------------------------------------
LEAD_C = kmats.lin((96, 99, 105))        # as for the M48 sample and the M71 house
LEAD_DARK = kmats.lin((70, 73, 79))
OXIDE = kmats.lin((176, 178, 172))
BRIGHT = kmats.lin((158, 162, 170))
POLISH = kmats.lin((126, 130, 138))


def rotated(t, vec, euler):
    m = t.node("ShaderNodeMapping")
    m.inputs["Rotation"].default_value = euler
    t.link(vec, m.inputs["Vector"])
    return m.outputs[0]


def scratches(t, vec, nsep, amount=1.0):
    """Short straight scratches (from M71): iso-lines of stretched noise, masked - segments of 2-3 cm."""
    out = None
    fams = [((0.03, 1.0, 1.0), 0, None, 2.2, 3.4), ((1.0, 0.03, 1.0), 1, None, 2.4, 3.9),
            ((1.0, 1.0, 0.03), 2, None, 2.0, 3.1), ((0.03, 1.0, 1.0), None, (0.62, 0.45, 0.80), 2.6, 4.4)]
    for st, ax, rot, sc, ms in fams:
        v = rotated(t, vec, rot) if rot else vec
        n = t.noise(t.stretch(v, *st), sc, 2.0, 0.5)
        line = t.maprange(t.math("ABSOLUTE", t.math("SUBTRACT", n, 0.5)), 0.0, 0.007, 1.0, 0.0)
        mask = t.maprange(t.noise(v, ms, 3.0, 0.5), 0.60, 0.70, 0.0, 1.0)
        s = t.math("MULTIPLY", line, mask)
        if ax is not None:
            s = t.math("MULTIPLY", s, t.maprange(t.math("ABSOLUTE", nsep.outputs[ax]), 0.4, 0.8, 1.0, 0.0))
        out = s if out is None else t.math("MAXIMUM", out, s)
    return t.math("MULTIPLY", out, amount)


def dents(t, vec, scale, amount):
    """Dents: Voronoi cells, a bowl in rare cells (from M71)."""
    vor = t.node("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = scale
    t.link(vec, vor.inputs["Vector"])
    bowl = t.maprange(vor.outputs["Distance"], 0.05, 0.38, 1.0, 0.0)
    pick = t.math("GREATER_THAN", t.bw(vor.outputs["Color"]), 1.0 - amount)
    return t.math("MULTIPLY", t.math("MULTIPLY", bowl, bowl), pick)


def mat_lead(mat, origin, seed=1.0, decal_items=()):
    """A 1.5 mm lead sheet straightened with a hammer on a board: dull, a whitish oxide in patches, small
    dents, scratches down to light metal (and across the sign's paint), worn edges, dust in the corners."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    vec = t.stretch(vec, 10.0, 10.0, 10.0)
    nsep = t.normal()
    col = t.mixc(t.maprange(t.noise(vec, 1.2, 6.0, 0.6), 0.3, 0.75, 0.0, 1.0), LEAD_DARK, LEAD_C)
    dn = dents(t, vec, 9.0, 0.35)
    col = t.mixc(t.math("MULTIPLY", dn, 0.25), col, POLISH)
    blot = t.maprange(t.noise(vec, 0.9, 6.0, 0.6), 0.55, 0.78, 0.0, 1.0)
    speck = t.maprange(t.noise(vec, 9.0, 4.0, 0.6), 0.64, 0.80, 0.0, 1.0)
    ox = t.math("MINIMUM", t.math("ADD", t.math("MULTIPLY", blot, 0.35), t.math("MULTIPLY", speck, 0.5)), 0.7)
    col = t.mixc(ox, col, OXIDE)
    col = kmats.decals(t, col, sep, nsep, decal_items)
    scr = scratches(t, vec, nsep, 0.8)
    col = t.mixc(t.math("MULTIPLY", scr, 0.7), col, BRIGHT)
    edge = t.maprange(t.edge_wear(0.0015), 0.05, 0.30, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", edge, 0.5), col, POLISH)
    cav = t.maprange(t.cavity(0.012), 0.15, 0.6, 0.0, 1.0)
    col = t.mixc(t.math("MULTIPLY", cav, 0.5), col, kmats.GRIME)
    gl = t.math("ADD", 0.16, t.math("SUBTRACT", t.math("ADD", t.math("MULTIPLY", scr, 0.25),
                                                       t.math("MULTIPLY", edge, 0.2)), t.math("MULTIPLY", ox, 0.10)))
    sp = t.math("ADD", 0.12, t.math("ADD", t.math("MULTIPLY", scr, 0.3), t.math("MULTIPLY", edge, 0.2)))
    h = t.math("SUBTRACT", 0.0, t.math("ADD", t.math("MULTIPLY", scr, 0.25), t.math("MULTIPLY", dn, 0.6)))
    return kmats.out(t, col, gl, sp, h)


# pine, darkened by hands and time; darker and greyer (next to the vanilla workbench boards in
# look_compare the earlier tone 150, 116, 82 came out light and pinkish)
WOOD = kmats.lin((124, 100, 78))
STEEL = dict(along="x", gloss=0.55, spec=0.7, dust=0.12, grime=0.35)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    # case: grey-green enamel over cast aluminium, rubbed to metal at the edges, marker across the face
    "case": ("paint", dict(color=kmats.lin((160, 168, 156)), under=kmats.lin((178, 180, 178)), seed=1.7, gloss=0.38,
                           spec=0.30, chip=(0.70, 0.76), rust=(0.99, 1.0), rust_low=0.0, floor_z=ZD, dust=0.20,
                           grime=0.40, decal_items=[MARKS_DEC])),
    "legend": ("paint", dict(color=kmats.lin((174, 180, 170)), under=kmats.lin((178, 180, 178)), seed=2.4, gloss=0.32,
                             spec=0.25, chip=(0.86, 0.92), rust=(0.99, 1.0), rust_low=0.0, floor_z=ZD, dust=0.10,
                             grime=0.15, decal_items=[LEGEND_DEC])),
    # display glass: a section of its own with a picture (panels); the look is needed only for the part's region
    "lcd": ("flat", dict(color=kmats.lin((142, 150, 128)), gloss=0.75, spec=0.55)),
    "knob": ("plastic", dict(color=kmats.lin((22, 21, 20)), seed=3.1, gloss=0.45, spec=0.35, dust=0.08, grime=0.1,
                             scuff=(0.80, 0.88))),
    # slider slot window: yellowed transparent plastic
    "amber": ("plastic", dict(color=kmats.lin((156, 104, 40)), seed=3.6, gloss=0.6, spec=0.45, mottle=0.12, dust=0.05,
                              grime=0.1, scuff=(0.95, 1.0))),
    "screw": ("steel", dict(STEEL, seed=4.4, tone=0.55)),
    "wood_x": (kwood.build_wood, dict(color=WOOD, seed=1.3, along="x", rings=0.40, knots=0.5, dust=0.35, grime=0.65,
                                      decal_items=[NAILS_F, NAILS_B])),
    "wood_y": (kwood.build_wood, dict(color=WOOD, seed=2.1, along="y", rings=0.40, knots=0.5, dust=0.35, grime=0.65)),
    "wood_lid": (kwood.build_wood, dict(color=kmats.lin((116, 92, 70)), seed=3.3, along="x", rings=0.45, knots=0.6,
                                        dust=0.25, grime=0.60)),
    "ply": (kwood.build_wood, dict(color=kmats.lin((128, 104, 80)), seed=4.7, along="x", rings=0.25, knots=0.2,
                                   dust=0.15, grime=0.65)),
    # cradle foam: dark grey, matte, in patches
    "foam": ("plastic", dict(color=kmats.lin((52, 53, 55)), seed=5.2, gloss=0.06, spec=0.03, mottle=0.16, dust=0.25,
                             grime=0.1, scuff=(0.95, 1.0))),
    "lead": (mat_lead, dict(seed=6.1, decal_items=[LEAD_DEC])),
    "tack": ("steel", dict(STEEL, seed=6.8, tone=0.30, grime=0.5)),
    "hinge": ("steel", dict(STEEL, seed=7.3, tone=0.42, grime=0.45)),
    "wire": ("steel", dict(STEEL, seed=7.9, tone=0.40, grime=0.4)),
    "latch": ("steel", dict(STEEL, seed=8.5, tone=0.48, grime=0.4)),
    # rubber band (a strip of bicycle inner tube): black, matte, worn at the battery corners
    "band": ("plastic", dict(color=kmats.lin((28, 28, 27)), seed=9.0, gloss=0.12, spec=0.06, mottle=0.10, dust=0.25,
                             grime=0.2, scuff=(0.80, 0.90))),
    # pencil: dark green lacquer, chipped to the wood; a knife-sharpened tip - wood, lead
    "pencil": ("paint", dict(color=kmats.lin((46, 78, 54)), under=kmats.lin((176, 138, 96)), seed=9.4, gloss=0.45,
                             spec=0.30, chip=(0.62, 0.70), rust=(0.99, 1.0), rust_low=0.0, floor_z=ZF, dust=0.10,
                             grime=0.35)),
    "pencil_wood": ("plastic", dict(color=kmats.lin((178, 140, 98)), seed=9.7, gloss=0.10, spec=0.05, mottle=0.14,
                                    dust=0.1, grime=0.3, scuff=(0.9, 1.0))),
    "graphite": ("flat", dict(color=kmats.lin((44, 44, 48)), gloss=0.55, spec=0.45)),
    "inner": ("flat", dict(color=kmats.lin((26, 27, 28)), gloss=0.1, spec=0.05)),
})

OBJ, NAME = "m75_dosimeter", "ozr_dosimeter"
SEL_SCREEN, SEL_SWITCH = "ozl_screen", "ozl_switch"
# the display frames are drawn by lcd_frames (in Blender); the bake machine's copies (--bake-part) do not
# write them
_FRAMES = ["decal_lcd_f%02d.png" % i for i in range(len(LCD_VALUES))]
if "--bake-part" not in kmodel.ARGV:
    _FRAMES = lcd_frames.write(WORK, LCD_VALUES, src=os.path.abspath(__file__))
LCD_PANEL = dict(off="decal_lcd_off.png", frames=_FRAMES, size=256, gloss=0.75)
# the "working" state is for the preview only: the atlas does not change when working (the display has its
# own texture, the slider is a bone)
LOOK_RUN = "--look" in kmodel.ARGV or "--look-render" in kmodel.ARGV
ON = dict(remap={}, emissive=(1.0, 1.0, 1.0, 1.0), move={SEL_SWITCH: (SW_TRAVEL, 0.0, 0.0)})
# "range" slider: the axis is a metre along +X, the offset is in metres
SWITCH_ANIM = ("ozl_switch_on", dict(type="translation", source=SEL_SWITCH, selection=SEL_SWITCH,
                                     axis="ozl_switch_axis", memory=1, minValue=0.0, maxValue=1.0, offset0=0.0,
                                     offset1=SW_TRAVEL))
# spare 9 V battery on the lead sheet of the open lid: the item's +Y (towards the terminals) goes up the
# lid, facing the viewer; held by the rubber band (build_band)
DECOR = [kv.put("battery9v", tuple(lid_matrix() @ Vector((BAT_X, BAT_YC, ZR - LEAD[2]))), up=LID_UP, fwd=LID_N,
                normal=LID_N, lods=(0, 1))]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL_SCREEN, SEL_SWITCH), hidden=(SEL_SCREEN,),
                 states={"on": ON} if LOOK_RUN else {}, bones=((SEL_SWITCH, ""),), animations=(SWITCH_ANIM,),
                 decor=DECOR, panels={"lcd": LCD_PANEL}, sources={SEL_SWITCH: dict(animPeriod=0.25)})
P = M.part
BOUNDS = {}


# --- primitives missing from kgeo -----------------------------------------------------------------
def retag(part, test, region="inner"):
    """Hidden faces go to the dark "inner" at a small scale (they need no atlas space). test(face)."""
    part.bm.normal_update()
    idx = part.region_index(region, *M.regions[region])
    for f in part.bm.faces:
        if f.is_valid and test(f):
            f[part.reg] = idx


def below(z):
    return lambda f: max(v.co.z for v in f.verts) < z


def facing(axis, sign, thr=0.99):
    return lambda f: f.normal[axis] * sign > thr


def rrect(x0, x1, y0, y1, r, n):
    """Rounded rectangle, counter-clockwise seen from above: r are the corner radii (x0y0, x1y0, x1y1, x0y1),
    n is arc segments per corner (a number or per corner; 0 for all gives sharp corners)."""
    ns = (n,) * 4 if isinstance(n, int) else tuple(n)
    if not any(ns):
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    spec = (((x0 + r[0], y0 + r[0]), r[0], 180.0), ((x1 - r[1], y0 + r[1]), r[1], 270.0),
            ((x1 - r[2], y1 - r[2]), r[2], 0.0), ((x0 + r[3], y1 - r[3]), r[3], 90.0))
    out = []
    for ((cx, cy), rr, a0), nk in zip(spec, ns):
        for k in range(max(nk, 1) + 1):
            a = math.radians(a0 + 90.0 * k / max(nk, 1))
            out.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return out


def loft_rings(part, rings, cap_top=True, cap_bottom=False):
    """Belts of faces between rings with the same number of points (a ring is counter-clockwise when seen
    from the side of the next one; the next one is higher or inside); caps follow the last and first rings."""
    bm = part.bm
    vs = [[bm.verts.new(Vector(c)) for c in r] for r in rings]
    faces = []
    n = len(vs[0])
    for a, b in zip(vs, vs[1:]):
        for i in range(n):
            j = (i + 1) % n
            faces.append(bm.faces.new([a[i], a[j], b[j], b[i]]))
    if cap_top:
        faces.append(bm.faces.new(vs[-1]))
    if cap_bottom:
        faces.append(bm.faces.new(vs[0][::-1]))
    return part.tag(faces)


def rslab(part, x0, x1, y0, y1, z0, z1, rc, nc, rt=0.0, nt=0):
    """A slab with corners rounded in plan (rc are the corner radii x0y0, x1y0, x1y1, x0y1; nc is segments
    per corner, one for small ones up to 2 mm) and a rounded top edge (rt, nt segments); the bottom is
    open - it is in the foam or on the floor."""
    ns = tuple(nc if r >= 0.002 else min(nc, 1) for r in rc)

    def ring(d, z):
        return [(x, y, z) for x, y in rrect(x0 + d, x1 - d, y0 + d, y1 - d, [max(r - d, 1e-4) for r in rc], ns)]
    rings = [ring(0.0, z0)]
    if nt and rt > 0:
        for k in range(nt + 1):
            phi = 0.5 * math.pi * k / nt
            rings.append(ring(rt * (1 - math.cos(phi)), z1 - rt + rt * math.sin(phi)))
    else:
        rings.append(ring(0.0, z1))
    return loft_rings(part, rings)


DOME = ((1.0, 0.0), (0.80, 0.55), (0.42, 0.92))
DOME_LOW = ((1.0, 0.0), (0.55, 1.0))     # low head (hinge screws, band nails)


def dome(part, base, axis, r0, h, sides, prof=DOME):
    """Round head (a nail, a screw): the base rests on the support at base, height h along axis; the bottom
    is open."""
    ax = Vector(axis).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(ax.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    e1 = ax.cross(ref).normalized()
    e2 = ax.cross(e1)
    o = Vector(base)
    rings = [[tuple(o + ax * (z * h) + (e1 * math.cos(2 * math.pi * i / sides) + e2 * math.sin(2 * math.pi * i / sides))
                    * (k * r0)) for i in range(sides)] for k, z in prof]
    return loft_rings(part, rings)


def stadium(cx, cz, hl, r, n):
    """A bar with rounded ends in the x-z plane: middle (cx, cz), half-length hl, end radius r."""
    pts = []
    for k in range(n + 1):
        a = math.radians(-90.0 + 180.0 * k / n)
        pts.append((cx + hl - r + r * math.cos(a), cz + r * math.sin(a)))
    for k in range(n + 1):
        a = math.radians(90.0 + 180.0 * k / n)
        pts.append((cx - hl + r + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def dbox(part, u0, u1, v0, v1, w0, w1, **kw):
    """A box in the device axes (u, v, w from the battery end, the axis and the bottom of the device)."""
    return g.box(part, DX0 + u0, DX0 + u1, OY - v1, OY - v0, ZD + w0, ZD + w1, **kw)


def ring(u0, u1, hv, w):
    """A rectangular ring in the device axes, counter-clockwise seen from above."""
    x0, x1, y0, y1, z = DX0 + u0, DX0 + u1, OY - hv, OY + hv, ZD + w
    return [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]


def vring(u0, u1, hv, w, r, n):
    """The rounded ring of the visor in the device axes."""
    return [(x, y, ZD + w) for x, y in rrect(DX0 + u0, DX0 + u1, OY - hv, OY + hv, (r,) * 4, n)]


def boxp(name, region, x0, x1, y0, y1, z0, z1, **kw):
    p = P(name, region)
    g.box(p, x0, x1, y0, y1, z0, z1, **kw)
    return p


# --- box and cradle -------------------------------------------------------------------------------
def build_box(spec):
    hi = spec["lod"] == 0
    parts = []
    bottom = boxp("bottom", "ply", BX0, BX1, BY0, BY1, 0.0, ZB, **(dict(r=0.0008, seg=1) if hi else {}))
    parts.append(bottom)

    def board(nm, region, x0, x1, y0, y1):
        """Wall board: the top edges are rounded, the ends chamfered; the bottom is on the floor, no faces
        there."""
        w = P(nm, region)
        if hi:
            rslab(w, x0, x1, y0, y1, ZB, ZR, (BOARD_R,) * 4, 1, BOARD_R, 2)
        else:
            g.box(w, x0, x1, y0, y1, ZB, ZR)
            retag(w, facing(2, -1))
        return w
    for nm, y0, y1 in (("wall_f", BY0, BY0 + T), ("wall_b", BY1 - T, BY1)):
        parts.append(board(nm, "wood_x", BX0, BX1, y0, y1))
    for nm, x0, x1 in (("wall_l", BX0, BX0 + T), ("wall_r", BX1 - T, BX1)):
        w = board(nm, "wood_y", x0, x1, BY0 + T, BY1 - T)
        retag(w, lambda f: abs(f.normal[1]) > 0.99)               # the ends are at the joint with the long walls
        parts.append(w)
    # foam: a frame around the device, visible only from above
    foam = P("foam", "foam")
    yd0, yd1 = OY - DW / 2, OY + DW / 2
    for x0, x1, y0, y1 in ((IX0, DX0, IY0, IY1), (DX0 + DL, IX1, IY0, IY1), (DX0, DX0 + DL, IY0, yd0),
                           (DX0, DX0 + DL, yd1, IY1)):
        g.box(foam, x0, x1, y0, y1, ZF0, ZF)
    retag(foam, lambda f: f.normal[2] < 0.5)
    parts.append(foam)
    # turn-button on the front wall: a steel bar with rounded ends on a screw, turned along the rim (the
    # lid is open)
    lt = P("latch", "latch")
    if hi:
        g.prism(lt, stadium(0.0, 0.045, 0.011, 0.0025, 4), (0, 2), BY0 - 0.0014, BY0 - 0.0002)
    else:
        g.box(lt, -0.011, 0.011, BY0 - 0.0014, BY0 - 0.0002, 0.0425, 0.0475)
    parts.append(lt)
    if hi:
        sc = P("latch_screw", "screw")
        dome(sc, (0.0, BY0 - 0.0014, 0.045), (0, -1, 0), 0.0021, 0.0009, 8)
        parts.append(sc)
    # hinges: a leaf on the back wall, knuckles on the axis (the leaf on the lid is in build_lid)
    for i, hx in enumerate(HINGE_X):
        parts.append(boxp("hinge_w%d" % i, "hinge", hx - 0.011, hx + 0.011, BY1, BY1 + 0.0009, ZR - 0.012,
                          ZR - 0.0004))
        kn = P("hinge_k%d" % i, "hinge", uv_name="hinge_k", uv_origin=(hx, PIV.y, PIV.z))
        for a0, a1 in (KNUCKLES if hi else ((KNUCKLES[0][0], KNUCKLES[-1][1]),)):
            g.cyl(kn, (hx + (a0 + a1) / 2, PIV.y, PIV.z), "x", KN_R, a1 - a0, 6 if hi else 5)
        parts.append(kn)
        if hi:
            hs = P("hinge_ws%d" % i, "screw", uv_name="hinge_ws", uv_origin=(hx, BY1, ZR))
            for dx in (-0.0068, 0.0068):
                dome(hs, (hx + dx, BY1 + 0.0009, ZR - 0.0064), (0, 1, 0), 0.0016, 0.0007, 6, DOME_LOW)
            parts.append(hs)
    parts.append(build_pencil(hi))
    return parts


def build_pencil(hi):
    """A stub of a hexagonal pencil in the cradle slot in front of the device: standing on edge, sharpened
    with a knife."""
    p = P("pencil", "pencil")
    x0, x1, x2, x3 = PEN_X

    def hexring(x, r):
        return [(x, PEN_Y + r * math.cos(math.radians(90 + 60 * k)), PEN_Z + r * math.sin(math.radians(90 + 60 * k)))
                for k in range(6)]
    loft_rings(p, [hexring(x0, PEN_R), hexring(x1, PEN_R)], cap_top=False, cap_bottom=True)
    p.use("pencil_wood", *M.regions["pencil_wood"])
    loft_rings(p, [hexring(x1, PEN_R), hexring(x2, 0.0011)], cap_top=not hi)
    if hi:
        p.use("graphite", *M.regions["graphite"])
        loft_rings(p, [hexring(x2, 0.0011), hexring(x3, 0.00015)])
    return p


# --- dosimeter ------------------------------------------------------------------------------------
def dxy(u0, u1, v0, v1):
    """A rectangle in the device axes -> world x0, x1, y0, y1."""
    return DX0 + u0, DX0 + u1, OY - v1, OY - v0


def build_dosimeter(spec):
    lod, n, seg = spec["lod"], spec["sides"], spec["seg"]
    hi = lod == 0

    def bev(r, s=None):
        return dict(r=r, seg=s or seg) if seg else {}
    parts = []
    case = P("case", "case")
    nc, nt = (3, 2) if hi else (1, 1)
    # the battery compartment cover and the head are slabs with rounded corners and a face edge; between
    # them the gutter floor and the ridge
    rslab(case, *dxy(0.0, 0.0334, -0.0423, 0.0423), ZD + W0, ZD + WF - 0.0004, (RB, 0.0012, 0.0012, RB), nc, 0.0035, nt)
    dbox(case, 0.0354, 0.0960, -DW / 2, DW / 2, W0, WC, **bev(0.003, 1))                  # gutter floor
    dbox(case, 0.0354, 0.0960, -0.0195, 0.0195, W0, WF, **bev(0.002, 1))                  # ridge
    rslab(case, *dxy(0.0955, DL, -DW / 2, DW / 2), ZD + W0, ZD + WF, (0.0015, RH, RH, 0.0015), nc, 0.003, nt)
    retag(case, facing(2, -1))
    parts.append(case)
    if hi:
        belt = P("belt", "case")                                                           # belt by the compartment
        dbox(belt, 0.0334, 0.0354, -0.0430, 0.0430, W0, WF + 0.0003, r=0.0008, seg=1)
        retag(belt, facing(2, -1))
        parts.append(belt)
    # display visor: sloped outer walls, a rounded edge, sloped walls down to the glass
    vis = P("visor", "case")
    u0, u1, hv = VIS
    vn = 2 if hi else 0
    rings = [vring(u0 - 0.001, u1 + 0.001, hv + 0.001, WF - 0.0003, 0.0035, vn),
             vring(u0, u1, hv, WF + VIS_H - 0.0006, 0.003, vn)]
    if hi:
        rings.append(vring(u0 + 0.0006, u1 - 0.0006, hv - 0.0006, WF + VIS_H, 0.0024, vn))
    rings += [vring(u0 + 0.0022, u1 - 0.0022, hv - 0.0022, WF + VIS_H, 0.0012, vn),
              vring(LCD[0], LCD[1], LCD[2], WF + 0.0001, 0.0004, vn)]
    loft_rings(vis, rings, cap_top=False)
    parts.append(vis)
    # display glass: its own texture (the "working" frames): UV 0..1, the image "up" runs along +X, "right"
    # along -Y
    lcd = P("lcd", "lcd", group=SEL_SCREEN, section="lcd")
    g.quad(lcd, ring(LCD[0], LCD[1], LCD[2], WF + 0.00015))
    hl = (LCD[1] - LCD[0]) / 2
    lcd.glass_frame = (g.Frame((DX0 + (LCD[0] + LCD[1]) / 2, OY, 0.0), (0, -1, 0), (1, 0, 0), (0, 0, 1)),
                       -LCD[2], LCD[2], -hl, hl)
    parts.append(lcd)
    # switch panel
    leg = P("legend", "legend")
    dbox(leg, LEG[0], LEG[1], -LEG[2], LEG[2], WF - 0.0004, WF + 0.0006, **bev(0.0004, 1))
    retag(leg, facing(2, -1))
    parts.append(leg)
    # boss and screw of the battery compartment cover
    boss = P("boss", "case")
    g.cyl(boss, (DX0 + SCREW_U, OY, ZD + WF - 0.002), "z", 0.0044, 0.0046, n)
    parts.append(boss)
    sc = P("screw", "screw")
    g.cyl(sc, (DX0 + SCREW_U, OY, ZD + WF + 0.0006), "z", 0.0025, 0.0008, n, r2=0.0022)
    parts.append(sc)
    # sliders in the upper gutters and buttons in the lower ones; "range" (the first) is the bone ozl_switch
    kn = P("knobs", "knob")
    sw = P("switch", "knob", group=SEL_SWITCH)
    for k, (v, u) in enumerate(SLIDE):
        dbox(sw if k == 0 else kn, u, u + 0.007, v - 0.0027, v + 0.0027, WC - 0.0002, WC + 0.0035, **bev(0.0006, 1))
        dbox(kn, 0.039, 0.047, v - 0.0023, v + 0.0023, WC - 0.0002, WC + 0.0024, **bev(0.0005, 1))
    for p in (kn, sw):
        retag(p, facing(2, -1))
    parts += [kn, sw]
    if hi:
        slot = P("slots", "amber")
        for v, _ in SLIDE:
            dbox(slot, 0.069, 0.085, v - 0.0022, v + 0.0022, WC - 0.0002, WC + 0.0003)
        retag(slot, facing(2, -1))
        parts.append(slot)
        sl = P("screw_slot", "knob")
        dbox(sl, SCREW_U - 0.0003, SCREW_U + 0.0003, -0.0021, 0.0021, WF + 0.0009, WF + 0.00145)
        parts.append(sl)
    return parts


# --- shield lid -----------------------------------------------------------------------------------
def lead_outline(hi):
    """A lead sheet cut with shears: cut corners, the edge wanders slightly (in the x, y axes of the closed
    lid)."""
    hx, hy = LEAD[0], LEAD[1]
    if not hi:
        pts = [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)]
    else:
        rnd = random.Random(7575)
        c = 0.0022
        pts = []
        for p0, p1, k, nrm in (((-hx + c, -hy), (hx - c, -hy), 4, (0, 1)), ((hx, -hy + c), (hx, hy - c), 2, (1, 0)),
                               ((hx - c, hy), (-hx + c, hy), 4, (0, 1)), ((-hx, hy - c), (-hx, -hy + c), 2, (1, 0))):
            pts.append(p0)
            for i in range(1, k + 1):
                t, j = i / (k + 1), rnd.uniform(-0.0006, 0.0006)
                pts.append((p0[0] + (p1[0] - p0[0]) * t + nrm[0] * j, p0[1] + (p1[1] - p0[1]) * t + nrm[1] * j))
            pts.append(p1)
    return [(x, OY + y) for x, y in pts]


def build_band(hi):
    """A rubber band across the spare battery (closed-lid axes: the sheet face is down, the battery under
    it): the ends are nailed to the sheet. The path is in the x-z plane, the band width is along y."""
    zl = ZR - LEAD[2]
    a0, a1 = BAT_X - BAT_HW, BAT_X + BAT_HW
    t = BAND[1]
    R, rb = t / 2 + 0.0002, 0.0015                       # clearance to the battery, rounding of its corners
    if hi:
        q = math.sqrt(0.5) * (rb + R)
        left = [(a0 - 0.0075, t / 2), (a0 - 0.003, t / 2), (a0 - R - 0.0006, 0.0014), (a0 - R, BAT_T - rb),
                (a0 + rb - q, BAT_T - rb + q), (a0 + rb, BAT_T + R)]
    else:
        left = [(a0 - 0.0075, t / 2), (a0 - R, t / 2), (a0 - R, BAT_T + R)]
    path = left + [(2 * BAT_X - a, c) for a, c in reversed(left)]
    bd = P("band", "band")
    g.sweep(bd, [(a, BAT_YC, zl - c) for a, c in path], (0, 1, 0), t / 2, BAND[0])
    parts = [bd]
    if hi:
        tk = P("band_tacks", "tack")
        for a in (a0 - 0.0055, a1 + 0.0055):
            dome(tk, (a, BAT_YC, zl - t), (0, 0, -1), 0.0022, 0.0009, 6, DOME_LOW)
        parts.append(tk)
    return parts


def stay_path(a, b, hi):
    """Wire stay: loops around screws a and b (300 degrees), a tangent between them bowed slightly outwards.
    All in the plane x = xw by the left wall and the left edge of the lid."""
    xw = BX0 - 0.0009
    if not hi:
        return [(xw, a.y, a.z), (xw, b.y, b.z)]
    d = Vector((b.y - a.y, b.z - a.z)).normalized()
    phi = math.atan2(-d.x, d.y)                  # the circle point where the counter-clockwise tangent is d
    R = 0.0021

    def on(c, ang):
        return (xw, c.y + R * math.cos(ang), c.z + R * math.sin(ang))
    pts = [on(a, phi + math.radians(75 * k - 300)) for k in range(5)]
    pa, pb = Vector(pts[-1]), Vector(on(b, phi))
    pts.append(tuple((pa + pb) / 2 + Vector((-0.0012, 0.0, 0.0))))
    pts += [on(b, phi + math.radians(75 * k)) for k in range(5)]
    return pts


def build_lid(spec):
    hi = spec["lod"] == 0
    parts = []
    lid = boxp("lid", "wood_lid", BX0, BX1, BY0, BY1, ZR, ZR + LID_T, **(dict(r=BOARD_R, seg=2) if hi else {}))
    parts.append(lid)
    zl = ZR - LEAD[2]
    lead = P("lead", "lead")
    g.prism(lead, lead_outline(hi), (0, 1), zl, ZR)
    retag(lead, facing(2, 1))
    parts.append(lead)
    if hi:
        for i, (tx, ty) in enumerate(TACKS):
            tk = P("tack%d" % i, "tack", uv_name="tack", uv_origin=(tx, OY + ty, zl))
            dome(tk, (tx, OY + ty, zl), (0, 0, -1), 0.0034, 0.0013, 8)
            parts.append(tk)
    for i, hx in enumerate(HINGE_X):
        parts.append(boxp("hinge_l%d" % i, "hinge", hx - 0.011, hx + 0.011, BY1, BY1 + 0.0009, ZR + 0.0004,
                          ZR + LID_T - 0.0004))
        if hi:
            hs = P("hinge_ls%d" % i, "screw", uv_name="hinge_ls", uv_origin=(hx, BY1, ZR))
            for dx in (-0.0068, 0.0068):
                dome(hs, (hx + dx, BY1 + 0.0009, ZR + LID_T / 2), (0, 1, 0), 0.0016, 0.0007, 6, DOME_LOW)
            parts.append(hs)
    parts += build_band(hi)
    m = lid_matrix()
    for p in parts:
        bmesh.ops.transform(p.bm, matrix=m, verts=p.bm.verts[:])
        p.bm.normal_update()
        p.uv_origin = m @ p.uv_origin            # identical parts are one island, also on the lid
    # wire stay on the left: a screw on the wall - a screw on the lid edge
    a = Vector((BX0, OY + 0.030, 0.044))
    b = m @ Vector((BX0, OY - 0.010, ZR + 0.004))
    w = P("stay", "wire")
    g.pipe(w, stay_path(a, b, hi), 0.0008, 5 if hi else 3)
    parts.append(w)
    if hi:
        for i, c in enumerate((a, b)):
            s = P("stay_screw%d" % i, "screw", uv_name="stay_screw", uv_origin=(BX0, c.y, c.z))
            dome(s, (BX0 - 0.0017, c.y, c.z), (-1, 0, 0), 0.0024, 0.0009, 8)
            parts.append(s)
    return parts


def build_lod(spec):
    parts = build_box(spec) + build_dosimeter(spec) + build_lid(spec)
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        check_decor(parts)
    return parts


def check_decor(parts):
    """Check of the proxy items (kv.corners): the battery lies on the lead sheet (its bottom is on the sheet
    plane) and does not sink into the rubber band."""
    n = Vector(LID_N)
    face = lid_matrix() @ Vector((0.0, OY, ZR - LEAD[2]))
    band = [v.co for p in parts if p.name == "band" for v in p.bm.verts]
    for d in DECOR:
        q = [Vector(c) for c in kv.corners(d[5], d[1], d[2], d[3])]
        h = [(c - face).dot(n) for c in q]
        lo, hi = kv.box(d[5])
        ax = [Vector(a) for a in kv.axes(d[2], d[3])]
        loc = [[(v - Vector(d[1])).dot(a) for a in ax] for v in band]
        inside = [c for c in loc if all(lo[i] + 1e-4 < c[i] < hi[i] - 1e-4 for i in range(3))]
        print("decor %s: above the sheet %.4f..%.4f m, band vertices inside the extent: %d of %d"
              % (d[5], min(h), max(h), len(inside), len(band)))


def collision():
    """Two convex parts: the box with the device and the open lid with the battery. The mass is the item
    weight in the mod, 0.8 kg."""
    box = kx.box_pts(BX0, BX1, BY0, BY1, 0.0, ZR)
    box += kx.box_pts(DX0, DX0 + DL, OY - DW / 2, OY + DW / 2, ZR, ZD + WF + VIS_H)
    m = lid_matrix()
    lid = [tuple(m @ Vector(q)) for q in kx.box_pts(BX0, BX1, BY0, BY1, ZR - LEAD[2] - BAT_T, ZR + LID_T)]
    pen = kx.PEN + r"\wood.rvmat"
    comps = [(box, pen), (lid, pen)]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    v, u = SLIDE[0]
    memory = {
        # inventory preview camera: from the front left and above (invView is where the camera is)
        "invView": [(-0.28, -0.46, 0.40)],
        "ce_center": [(0.0, 0.0, 0.085)],
        "ce_radius": [(0.13, 0.0, 0.085)],
        # "range" slider: a metre along +X (towards the display)
        "ozl_switch_axis": [(DX0 + u + 0.0035, OY - v, ZD + WC + 0.0017),
                            (DX0 + u + 0.0035 + 1.0, OY - v, ZD + WC + 0.0017)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


SHOTS = [
    ("front", (-0.22, -0.52, 0.40), (0.0, 0.0, 0.07), 40),
    ("face", (0.02, -0.21, 0.33), (0.01, OY, 0.055), 40),
    ("lid", (0.10, -0.42, 0.17), (0.0, 0.04, 0.10), 42),
    ("left", (-0.48, 0.06, 0.24), (-0.05, 0.02, 0.07), 40),
    ("back", (0.32, 0.46, 0.30), (0.0, 0.02, 0.07), 40),
]

M.run(build_lod, collision, SHOTS, row_step=0.30, row_shot=((0.15, -1.1, 0.40), (0.15, 0, 0.08)))
