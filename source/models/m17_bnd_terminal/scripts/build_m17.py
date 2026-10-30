"""M17 - exchange window booth: Terminal of the Bandits (OZL_Bnd_Terminal). Terminal: no modules.

    blender --background --python build_m17.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: system Python make_decals.py (crack in the glass, bullet marks on the lower wall,
the board "off" and "work" frames).

Look: the "dayz" look (matte, dirtier, coloured AO); sizes and overall shape are fixed, corners and edges
are rounded, small things are real:
- booth: 50 x 5 angles with a fillet on the edges, ribs of 40 angle and a plinth on the lower wall, a
  stiffening strip on the sides and the back, a drip edge on the roof; bullet marks on the lower wall (a
  decal: paint chipped down to metal, holes, rusty streaks - Bandits); at the back a door with a stamped
  panel, a box frame of strip, three hinges, a bracket handle and a padlock on a lug; on the right side
  a patch on rivets with domed heads;
- customer shelf: three boards with rounded edges on an angle frame, two brackets (an angle and a gusset
  brace of strip, welded), bolts through the boards; the LK-1 tray is stamped - rounded corners of the
  well and the bottom, a frame on screws; behind it a shutter with a rib - the inside is not visible;
- partition: a frame, panes on glazing beads with a rubber seal; the crack on the right pane is taped
  crosswise with 48 mm reinforced tape; the speaking grille is a convex perforated disc in a ring on
  screws;
- a grille of dia. 12 rebar: the rod opposite the speaking grille is cut out and a ring is welded in
  instead; one rod on the right is bent outward (it was broken - the crack in the glass is next to it);
  weld tacks on the lower and upper strips;
- the lamp above the window is a caged bulkhead light (after dust- and moisture-proof NPP luminaires; the
  size follows the 7.5 cm canopy, an estimate): a cast body on screws, a glass dome, a ring and two arcs
  of the cage, the wire goes into a gland in the canopy;
- the board (own, no inscriptions - only digits): a 1990s LED exchange-rate board, 420 x 200 x 50
  (estimate), hangs on two hooks on a strip of the grille in front of the left pane, the wire goes
  through the grille into the frame post;
- the exhaust fan on the left side (axial dia. 200 in a 260 square plate, estimate): a duct with a dark
  inside and a blind bottom (the booth interior is not visible), the motor on three posts, a rotor with
  five blades, a wire guard on four bolts;
- small things: a tin ashtray with three notches and butts (filter, paper, ash), "Chernomorka" packs (own
  88 x 55 x 22 box with the vanilla texture by path, as in M16), butts on the ground; vanilla DayZ items
  as proxies (kvanilla): a sheet of paper with a pen, matches, a roll of insulating tape, a partly drunk
  vodka on the shelf, an empty vodka and an open can of sardines on the ground under the shelf.

A 1990s exchange booth (an underpass booth, a cash window with a tray, a cashier's grille). The window is
opaque, the inside is not visible, there is no teller, the interior is not modelled. The glass has two
variants: "A" (main atlas, OZL_Bnd_Terminal) - dark tinted armoured glass; "B" (atlas _painted,
OZL_Bnd_Terminal_Painted replaces the texture of the ozl_glass selection) - painted cream on the inside,
the paint scraped off in places. No inscriptions.

Sizes (layout.py): box 1.80 x 2.10 x 1.40 m (with the shelf), shelf at 1.0 m, glazing up to 2.0 m (bank
cash booths), LK-1 tray 500 x 300 mm, well 90 mm, frame 50 mm at the LK-1 - here 35 (shelf 0.26);
speaking grille dia. 160 mm on the middle panel.

Work look: ozl_lamp_work - the lamp dome (atlas _on, lit); ozl_screen - the board, own texture (section
screen): "off" is dark glass with unlit segments, "work" is frames _screen_fN (the sum is counted, digits
lit; OZL_WorkFx frames); the fan rotor is the bone ozl_fan on the source ozl_work: a model.cfg loop
(sourceAddress loop, maxValue 1/4) - 4 turns per 2 s pass, 2 turns per second (five blades: at 30 frames
24 degrees per frame - the rotation does not appear to run backwards); at rest it stands still.
ozl_glass is three panes (a hiddenSelection of the glass look, not a state).

Blender axes: X is width, Y is depth (the customer side is -Y), Z is up.
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
import krender  # noqa: E402
import kvanilla as kv  # noqa: E402
import kwood  # noqa: E402
import layout as L  # noqa: E402
import m17_geo as G  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
X0, X1, Y0, Y1, H = L.X0, L.X1, L.Y0, L.Y1, L.H
YB = L.YP                         # face of the lower wall and the partition (the customer side)
YBACK = Y1                        # back wall
ZC, ZG = L.ZC, L.ZG               # shelf, top of the glazing
T = 0.02                          # wall sheet
HR = H - 0.025                    # bottom of the roof
LY0 = L.LEDGE[0]                  # front of the shelf
Z0B = ZC - 0.04                   # bottom of the shelf boards
# shelf boards along x (front, middle, back); the middle and back ones are at the sides of the tray well
TX0, TX1, TY0, TD = -0.25, 0.25, LY0 + 0.08, 0.09      # tray: the well up to the partition
ZB = ZC - TD                      # bottom of the well
TYB = YB + 0.01                   # the well goes behind the shutter
FL = 0.035                        # tray frame
BOARDS = [(LY0, TY0 - 0.0015), (TY0 + 0.002, -0.512), (-0.508, YB - T)]
RAIL = 0.06                       # lower chord of the frame above the shelf
YF0, YF1 = YB - 0.04, YB          # partition frame along Y
YGL = YB - 0.012                  # glass (face)
YR = YB - 0.075                   # axis of the grille rods
MULL = (-0.30, 0.30)              # frame posts between the panels
GZ0, GZ1 = ZC + RAIL, ZG - 0.04   # panes by height
PANES = ((X0 + 0.04, MULL[0] - 0.02), (MULL[0] + 0.02, MULL[1] - 0.02), (MULL[1] + 0.02, X1 - 0.04))
BW = 0.018                        # glazing bead
CRACK = (0.60, 1.55)              # crack on the right panel
# tape over the crack: a cross and a short piece across the lower ray; strip ends (x, z)
TAPE = [((0.47, 1.43), (0.75, 1.69)), ((0.45, 1.67), (0.76, 1.44)), ((0.55, 1.33), (0.69, 1.37))]
# grille: dia. 12 rods at pitch 0.12, strips 40 x 6
RODS = [round(X0 + 0.06 + 0.12 * i, 4) for i in range(15)]
RZ0, RZ1 = ZC + RAIL + 0.01, ZG - 0.05
FLATS = (RZ0 + 0.02, 1.25, 1.75, RZ1 - 0.02)
FW = 0.02                         # half-height of a strip
TALK = (0.0, 1.42)                # speaking grille dia. 160 (x, z)
TALK_R = 0.108                    # ring in the grille around it: the rod at x = 0 is cut out
BENT = 0.48                       # bent rod
# board on the grille in front of the left pane
BRD = (-0.80, -0.38, 1.52, 1.72)  # x0 x1 z0 z1
BRD_Y1 = YR - 0.012 - 0.002       # back of the case - 2 mm in front of the grille strip
BRD_Y0 = BRD_Y1 - 0.05
BEZ = 0.02                        # board window frame
# lamp on the canopy
LY = YB - 0.10                    # face of the canopy
LZ = ZG + 0.037                   # lamp axis
# fan on the left side
FY, FZ = -0.12, 1.70              # opening centre
FH = 0.11                         # half-opening
FR = 0.098                        # duct radius
FAN_TURNS = 4                     # turns per loop pass (2 s)
# door at the back
DX0, DX1, DZ0, DZ1 = -0.42, 0.30, 0.04, 1.94
# small things on the shelf
ASH = (0.44, -0.565)              # ashtray
PACKS = [((-0.80, -0.60), 12.0, 0.0), ((-0.788, -0.588), -16.0, 0.022)]

LOD_SPECS = [
    dict(lod=0, bev=1, sides=8),
    dict(lod=1, bev=0, sides=6),
    dict(lod=2, bev=0, sides=4),
]

REGIONS = {
    "wall": ("paint_black", 0.6), "wall_front": ("paint_black_front", 0.8), "frame": ("paint_frame", 1.0),
    "angle": ("paint_angle", 1.0), "weld": ("weld", 1.5), "board": ("board", 0.8), "rebar": ("rebar", 1.2),
    "tray": ("tray", 1.2), "shutter": ("shutter", 1.0), "glass": ("glass_a", 1.0), "bead": ("paint_frame", 1.5),
    "seal": ("rubber", 1.5), "tape": ("tape", 2.0), "talk": ("grille_v", 2.0), "roof": ("paint_black", 0.3),
    "lamp_body": ("lamp_body", 2.0), "lamp_glass": ("lamp_glass", 3.0), "cage": ("cage", 2.0),
    "door": ("paint_door", 0.6), "hinge": ("steel", 2.0), "lock": ("lock", 3.0), "shackle": ("steel", 3.0),
    "patch": ("patch", 0.8), "rivet": ("rivet", 2.0), "screw": ("screw", 2.0),
    "tin": ("tin", 1.5), "butt": ("butt", 2.0), "filter": ("filter", 2.0), "ash": ("ash", 2.0),
    "carton": ("carton", 2.0),
    "led_case": ("led_case", 1.5), "cable": ("cable", 1.5), "gland": ("black", 2.0), "wire": ("wire", 2.0),
    "duct": ("duct", 1.0), "fan_plate": ("fan_plate", 1.5), "fan_blade": ("fan_blade", 2.0),
    "fan_motor": ("fan_motor", 2.0), "guard": ("guard", 2.0),
}


def decal(name, ax, sign, uv, center, size, rng=None):
    return (os.path.join(WORK, name), ax, sign, uv, center, size, rng)


CRACK_DECAL = decal("decal_crack.png", "y", -1, ("x", "z"), CRACK, (0.36, 0.36), (YGL - 0.006, YGL + 0.006))
# bullet marks on the face of the lower wall: an image for the whole wall (make_decals.py, SHOTS - the same places)
SHOTS_DECAL = decal("decal_shots.png", "y", -1, ("x", "z"), (0.0, 0.50), (1.76, 0.88), (YB - T - 0.003, YB - T + 0.003))


def build_glass(mat, origin, base, seed=4.0, gloss=0.85, spec=0.9, painted=None, decal_items=()):
    """Armoured glass: base is the colour behind the glass (tint or paint from the inside). painted is the
    paint colour: brush strokes and scraped spots (the dark void of the booth is there). On top - scratches
    (thin light strokes in different directions), smears, dust on top, dirt toward the bottom, the crack
    (a decal)."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    col = t.mixc(t.maprange(t.noise(vec, 3.0, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0),
                 tuple(c * 0.85 for c in base[:3]) + (1,), base)
    if painted is not None:
        strokes = t.noise(t.stretch(vec, 1.0, 1.0, 14.0), 6.0, 6.0, 0.6)        # strokes along x
        col = t.mixc(t.maprange(strokes, 0.3, 0.7, 0.0, 0.25), painted, tuple(c * 0.8 for c in painted[:3]) + (1,))
        scraped = t.step(t.noise(vec, 9.0, 8.0, 0.7), 0.62, 0.66)
        col = t.mixc(t.maprange(t.noise(vec, 4.0, 6.0, 0.6), 0.4, 0.8, 0.0, 0.5), col, kmats.lin((150, 132, 96)))   # yellowed
        edge = t.maprange(sep.outputs["Z"], ZC + RAIL + 0.03, ZC + RAIL, 0.0, 1.0)
        col = t.mixc(t.math("MAXIMUM", scraped, t.math("MULTIPLY", edge, 0.8)), col, kmats.lin((14, 14, 16)))
    sc = 0.0
    for k, (sx, sz) in enumerate(((0.06, 1.0), (1.0, 0.06), (0.5, 0.08))):
        n = t.noise(t.stretch(vec, sx * 30, 30.0, sz * 30), 4.0 + k, 2.0, 0.5)
        line = t.math("SUBTRACT", 1.0, t.step(t.math("ABSOLUTE", t.math("SUBTRACT", n, 0.5)), 0.0, 0.012))
        sc = line if k == 0 else t.math("MAXIMUM", sc, line)
    sc = t.math("MULTIPLY", sc, t.step(t.noise(vec, 2.0, 2.0, 0.5), 0.55, 0.7))
    col = t.mixc(t.math("MULTIPLY", sc, 0.30), col, kmats.lin((150, 152, 150)))
    smear = t.maprange(t.noise(vec, 1.6, 3.0, 0.5), 0.5, 0.8, 0.0, 0.25 if painted is None else 0.45)
    col = t.mixc(smear, col, kmats.lin((92, 88, 78)))
    col = kmats.decals(t, col, sep, nsep, decal_items)
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z=ZC + RAIL, dust=0.4, grime=0.6, low_h=0.35)
    gl = t.math("SUBTRACT", gloss, t.math("ADD", t.math("MULTIPLY", smear, 0.6), t.math("MULTIPLY", dirt, 0.5)))
    sp = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, 0.4))
    return kmats.out(t, col, gl, sp, t.math("MULTIPLY", sc, -0.3))


KINDS = kmats.std_kinds(floor_z=0.0)
# dirty black paint over the grey factory paint (Bandits): chips, rust at the floor, dirt
BLACK = dict(color=kmats.lin((38, 38, 36)), under=kmats.lin((128, 132, 130)), seed=2.1, gloss=0.30, spec=0.22,
             chip=(0.55, 0.61), rust=(0.58, 0.66), rust_low=1.0, floor_z=0.0, dust=0.45, grime=0.9)
KINDS.update({
    "paint_black": ("paint", BLACK),
    "paint_black_front": ("paint", dict(BLACK, seed=2.9, chip=(0.50, 0.57), rust=(0.55, 0.63), decal_items=[SHOTS_DECAL])),
    "paint_frame": ("paint", dict(BLACK, seed=3.7, chip=(0.52, 0.58), rust_low=0.3, floor_z=ZC, grime=0.6)),
    "paint_angle": ("paint", dict(BLACK, seed=4.4, chip=(0.48, 0.55), rust=(0.52, 0.60))),
    # weld: a bead in scale, the paint came off, it rusts
    "weld": ("paint", dict(BLACK, color=kmats.lin((46, 42, 38)), under=kmats.lin((96, 58, 34)), seed=8.8,
                           chip=(0.38, 0.46), rust=(0.40, 0.50), rust_low=0.3, floor_z=ZC)),
    "paint_door": ("paint", dict(BLACK, color=kmats.lin((52, 54, 50)), seed=5.1, chip=(0.54, 0.60))),
    "patch": ("paint", dict(BLACK, color=kmats.lin((96, 98, 92)), under=kmats.lin((110, 60, 30)), seed=6.6,
                            chip=(0.50, 0.56), rust=(0.50, 0.58))),
    "rivet": ("paint", dict(BLACK, color=kmats.lin((96, 98, 92)), under=kmats.lin((110, 60, 30)), seed=6.9,
                            chip=(0.45, 0.52), rust=(0.45, 0.55))),
    "board": (kwood.build_wood, dict(color=kmats.lin((120, 90, 62)), seed=2.3, along="x", floor_z=ZC, dust=0.5,
                                     grime=0.8, knots=0.7)),
    # rebar: the black paint has almost come off, rust
    "rebar": ("paint", dict(color=kmats.lin((34, 32, 30)), under=kmats.lin((100, 50, 26)), seed=7.7, gloss=0.25,
                            spec=0.3, chip=(0.42, 0.50), rust=(0.40, 0.50), rust_low=0.4, floor_z=ZC, dust=0.4,
                            grime=0.5)),
    "tray": ("steel", dict(seed=8.1, tone=0.26, along="x", gloss=0.5, spec=0.6, floor_z=ZB, dust=0.5, grime=0.8)),
    "shutter": ("paint", dict(BLACK, color=kmats.lin((22, 22, 22)), seed=9.3, gloss=0.2, floor_z=ZB)),
    "glass_a": (build_glass, dict(base=kmats.lin((16, 19, 24)), decal_items=[CRACK_DECAL])),
    "glass_b": (build_glass, dict(base=kmats.lin((14, 14, 16)), painted=kmats.lin((198, 186, 150)),
                                  decal_items=[CRACK_DECAL])),
    # reinforced tape: silver-grey, worn and greasy at the edges
    "tape": ("plastic", dict(color=kmats.lin((108, 110, 106)), gloss=0.30, spec=0.22, mottle=0.18, dust=0.6, grime=1.0,
                             scuff=(0.58, 0.68))),
    # cast lamp body: grey paint over aluminium
    "lamp_body": ("paint", dict(BLACK, color=kmats.lin((88, 90, 86)), under=kmats.lin((150, 150, 146)), seed=5.9,
                                chip=(0.55, 0.61), rust=(0.62, 0.70), rust_low=0.0, floor_z=ZG, dust=0.5, grime=0.6)),
    "lamp_glass": ("plastic", dict(color=kmats.lin((196, 190, 168)), gloss=0.5, spec=0.4, dust=0.6, grime=0.4)),
    "lamp_on": ("flat", dict(color=kmats.lin((255, 236, 190)), gloss=0.7, spec=0.5)),
    "cage": ("paint", dict(BLACK, color=kmats.lin((40, 40, 38)), seed=6.2, chip=(0.46, 0.54), rust=(0.48, 0.56),
                           rust_low=0.0, floor_z=ZG)),
    # padlock: grey paint over cast iron, rusting in the chips
    "lock": ("paint", dict(BLACK, color=kmats.lin((70, 72, 70)), under=kmats.lin((110, 60, 32)), seed=9.9,
                           chip=(0.50, 0.56), rust=(0.46, 0.54), rust_low=0.0, floor_z=0.9, gloss=0.35, spec=0.35)),
    "screw": ("steel", dict(seed=7.1, tone=0.26, along="z", gloss=0.4, spec=0.5, floor_z=ZC, dust=0.4, grime=0.7)),
    "tin": ("steel", dict(seed=6.4, tone=0.30, along="z", gloss=0.45, spec=0.5, floor_z=ZC, dust=0.4, grime=0.6)),
    "butt": ("plastic", dict(color=kmats.lin((222, 218, 206)), gloss=0.12, spec=0.08, mottle=0.12, dust=0.3, grime=0.4)),
    "filter": ("plastic", dict(color=kmats.lin((204, 146, 82)), gloss=0.10, spec=0.05, mottle=0.15, dust=0.2, grime=0.3)),
    "ash": ("plastic", dict(color=kmats.lin((64, 62, 58)), gloss=0.05, spec=0.03, mottle=0.3, dust=0.1, grime=0.2)),
    "carton": ("plastic", dict(color=kmats.lin((214, 208, 196)), gloss=0.3, spec=0.2, mottle=0.06, dust=0.3,
                               grime=0.3)),
    # board: sheet-metal case, the black paint worn off
    "led_case": ("paint", dict(BLACK, color=kmats.lin((30, 30, 30)), under=kmats.lin((96, 98, 96)), seed=7.3,
                               chip=(0.58, 0.64), rust=(0.66, 0.74), rust_low=0.0, floor_z=1.5, grime=0.6)),
    "cable": ("plastic", dict(color=kmats.lin((24, 24, 24)), gloss=0.3, spec=0.2, dust=0.35, grime=0.5, scuff=(0.8, 0.9))),
    "wire": ("steel", dict(seed=8.4, tone=0.30, along="z", gloss=0.45, spec=0.5, floor_z=1.5, dust=0.3, grime=0.6)),
    # fan: dark duct inside, blades of grey plastic in dust
    "duct": ("plastic", dict(color=kmats.lin((20, 20, 20)), gloss=0.12, spec=0.08, dust=0.7, grime=0.9)),
    "fan_plate": ("paint", dict(BLACK, color=kmats.lin((60, 62, 58)), seed=7.9, chip=(0.50, 0.56), rust=(0.52, 0.60),
                                rust_low=0.0, floor_z=1.5)),
    "fan_blade": ("plastic", dict(color=kmats.lin((96, 98, 96)), gloss=0.3, spec=0.25, dust=0.8, grime=0.8,
                                  scuff=(0.7, 0.8))),
    "fan_motor": ("paint", dict(BLACK, color=kmats.lin((50, 52, 50)), seed=8.1, rust_low=0.0, floor_z=1.5)),
    "guard": ("paint", dict(color=kmats.lin((34, 32, 30)), under=kmats.lin((100, 50, 26)), seed=8.9, gloss=0.25,
                            spec=0.3, chip=(0.44, 0.52), rust=(0.42, 0.52), rust_low=0.0, floor_z=1.5, dust=0.4,
                            grime=0.5)),
})

OBJ, NAME = "m17_bnd_terminal", "ozr_bnd_terminal"
SEL_LAMP = "ozl_lamp_work"
SEL_GLASS = "ozl_glass"           # glass is its own hiddenSelection: look B is set by a child class of the mod
SEL_SCREEN = "ozl_screen"         # the board is its own texture with frames
SEL_FAN = "ozl_fan"               # fan rotor - a bone on the source ozl_work
PAINTED = dict(remap={"glass_a": "glass_b"})
STATES = {
    "on": dict(remap={"lamp_glass": "lamp_on"}, emissive=(1.0, 1.0, 1.0, 1.0)),
    # glass "B", painted from the inside (both looks go into the mod, the main one is dark A): the atlas and rvmat
    # for hiddenSelectionsTextures of the class OZL_Bnd_Terminal_Painted
    "painted": PAINTED,
}
BOARD_FRAMES = 12                 # board "work" frames: 12 of 0.25 s - a cycle in 3 s
SCREEN = dict(off="decal_board_off.png", frames=["decal_board_f%02d.png" % i for i in range(BOARD_FRAMES)],
              size=256, gloss=0.7)
FAN_ANIM = ("ozl_fan_spin", dict(type="rotation", source="ozl_work", sourceAddress="loop", selection=SEL_FAN,
                                 axis="ozl_fan_axis", memory=1, minValue=0.0, maxValue=1.0 / FAN_TURNS,
                                 angle0=0.0, angle1=2 * math.pi))
CIGS = (r"dz\gear\medical\data\pack_of_cigs_cherno_co.paa", r"dz\gear\medical\data\pack_of_cigs.rvmat")
# pieces of the pack texture (fractions of the image: x0, x1, y0, y1 top to bottom) - as in M16
CIGS_UV = {"front": (0.117, 0.462, 0.43, 1.0), "side": (0.885, 0.970, 0.60, 1.0), "end": (0.26, 0.45, 0.20, 0.30)}
SARDINES = r"dz\gear\food\can_sardines_open"
DECOR = [
    kv.put("paper", (-0.555, -0.562, ZC), lift=0.0008, **kv.flat(3)),             # form: clear of the bracket bolts
    kv.put("pen", (-0.52, -0.54, ZC + 0.0008), **kv.flat(-35)),                    # on the form
    kv.put("matchbox", (-0.33, -0.51, ZC), **kv.flat(80)),
    kv.put("ducttape", (0.60, -0.585, ZC), **kv.flat(20)),                         # the crack was taped with it
    kv.put("vodka", (0.79, -0.545, ZC), up=(0, 0, 1), fwd=(0.3, -1, 0)),            # half-full, by the grille
    kv.put("vodka", (0.30, -0.56, 0.0), **kv.flat(170)),                            # empty, under the shelf
    kv.put(SARDINES, (-0.35, -0.56, 0.0), up=(0, 0, 1), fwd=(0.2, -1, 0)),          # a can instead of an ashtray
]


class Model(kmodel.Model):
    def panel_mats(self, on):
        """Look B (painted glass) is a glass variant, not "work": on its frames the board is unlit
        (tex_painted_* when baking; the --look preview is the place_look wrapper below)."""
        if on and _LAST_CO[0] and "_painted_" in _LAST_CO[0]:
            on = False
        return super().panel_mats(on)


M = Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
          selections=(SEL_LAMP, SEL_GLASS, SEL_SCREEN, SEL_FAN), hidden=(SEL_LAMP, SEL_GLASS, SEL_SCREEN),
          states=STATES, bones=((SEL_FAN, ""),), animations=(FAN_ANIM,), decor=DECOR,
          panels={"screen": SCREEN}, vsections={"cigs": CIGS}, sources={"ozl_work": dict(animPeriod=2.0)})
P = M.part
BOUNDS = {}

# preview of look B: the board is unlit (the kit draws all station looks with the "work" frame on the screens)
_place_look, _game_material = krender.place_look, krender.game_material
_LAST_CO = [None]


def _place_look_variant(parts, kinds, origin, remap=None, panels=None, **kw):
    if remap == PAINTED["remap"]:
        panels = M.panel_mats(False)
    return _place_look(parts, kinds, origin, remap=remap, panels=panels, **kw)


def _game_material_track(tex_dir, name, co=None):
    _LAST_CO[0] = co
    return _game_material(tex_dir, name, co=co)


krender.place_look, krender.game_material = _place_look_variant, _game_material_track


def angle_at(part, sec, x, y, sa, sb, z0, z1):
    """Vertical angle: the outer corner at (x, y), legs toward sa along x and sb along y."""
    G.prism_poly(part, sec, lambda a, b, c: Vector((x + sa * a, y + sb * b, c)), z0, z1)


# =============================================================================
# Shell: lower wall, sides, back wall with the door, roof, canopy
# =============================================================================
def build_shell(spec):
    lod, bev = spec["lod"], spec["bev"]
    r = 0.004 if bev else 0.0
    parts = []
    fw = P("front_wall", "wall_front")
    g.box(fw, X0, X1, YB - T, YB, 0.0, Z0B, r=r, seg=bev)
    parts.append(fw)
    sw = P("side_walls", "wall")
    g.box(sw, X1 - T, X1, YB - T, YBACK, 0.0, HR, r=r, seg=bev)                    # right side
    g.box(sw, X0 + T, X1 - T, YBACK - T, YBACK, 0.0, HR)                           # back wall
    if lod < 2:                                                                     # left side: the fan opening
        for y0, y1, z0, z1 in ((YB - T, YBACK, 0.0, FZ - FH), (YB - T, YBACK, FZ + FH, HR),
                               (YB - T, FY - FH, FZ - FH, FZ + FH), (FY + FH, YBACK, FZ - FH, FZ + FH)):
            g.box(sw, X0, X0 + T, y0, y1, z0, z1)
    else:
        g.box(sw, X0, X0 + T, YB - T, YBACK, 0.0, HR)
    parts.append(sw)
    rf = P("roof", "roof")
    g.box(rf, X0 - 0.02, X1 + 0.02, LY, YBACK + 0.02, HR, H, r=r, seg=bev)
    if lod == 0:                                                                    # drip edge: sides and back
        g.box(rf, X0 - 0.024, X0 - 0.02, LY, YBACK + 0.024, HR - 0.02, H - 0.004)
        g.box(rf, X1 + 0.02, X1 + 0.024, LY, YBACK + 0.024, HR - 0.02, H - 0.004)
        g.box(rf, X0 - 0.02, X1 + 0.02, YBACK + 0.02, YBACK + 0.024, HR - 0.02, H - 0.004)
    parts.append(rf)
    hd = P("header", "frame")
    g.box(hd, X0, X1, LY, YB - 0.04, ZG, HR, r=r, seg=bev)
    parts.append(hd)
    dr = P("door", "door")
    g.box(dr, DX0, DX1, YBACK, YBACK + 0.012, DZ0, DZ1, r=r, seg=bev)
    parts.append(dr)
    pt = P("patch", "patch")
    g.box(pt, X1, X1 + 0.004, 0.05, 0.50, 0.30, 0.85, r=0.0015 if bev else 0.0, seg=bev)
    parts.append(pt)
    if lod == 2:
        return parts
    # 50 x 5 angles on the edges (at the front - up to the shelf), plinth
    an = P("angles", "angle")
    sec = G.angle_section(0.05, 0.005, 0.006, 2 if lod == 0 else 0)
    for x, sa in ((X0 - 0.004, 1), (X1 + 0.004, -1)):
        angle_at(an, sec, x, YB - T - 0.004, sa, 1, 0.0, Z0B - 0.004)
        angle_at(an, sec, x, YBACK + 0.004, sa, -1, 0.0, HR)
    g.box(an, X0 + 0.046, X1 - 0.046, YB - T - 0.012, YB - T, 0.0, 0.08, r=0.002 if bev else 0.0, seg=bev)
    parts.append(an)
    if lod == 1:
        return parts
    # ribs of the lower wall - a 40 angle with a leg to the sheet; the middle one up to the tray well
    sec4 = G.angle_section(0.04, 0.004, 0.004, 2)
    for xs in (-0.45, 0.0, 0.45):
        top = ZB - 0.012 if abs(xs) < 0.3 else Z0B - 0.004
        G.prism_poly(an, sec4, lambda a, b, c, xs=xs: Vector((xs - 0.002 + a, YB - T - b, c)), 0.08, top)
    # stiffening strips on the sides and the back (at the back - clear of the door)
    for xa, xb in ((X0 - 0.004, X0), (X1, X1 + 0.004)):
        g.box(an, xa, xb, YB - T + 0.05, YBACK - 0.05, 0.98, 1.02)
    for xa, xb in ((X0 + 0.05, DX0 - 0.04), (DX1 + 0.04, X1 - 0.05)):
        g.box(an, xa, xb, YBACK, YBACK + 0.004, 0.98, 1.02)
    # weld tacks along the bottom of the ribs
    wd = P("shell_welds", "weld")
    for k, xs in enumerate((-0.45, 0.0, 0.45)):
        G.blob(wd, (xs + 0.018, YB - T - 0.004, 0.083), (0, -0.4, 1), 0.007, 0.004, 5, seed=k * 1.7)
    parts.append(wd)
    # door: stamped panel and a rib along the leaf, a box frame of
    # strip, three hinges, a bracket handle, a lug with a lock
    df = P("door_ribs", "door")
    for a0, a1, b0, b1 in ((DX0 + 0.05, DX0 + 0.075, DZ0 + 0.05, DZ1 - 0.05), (DX1 - 0.075, DX1 - 0.05, DZ0 + 0.05, DZ1 - 0.05),
                           (DX0 + 0.075, DX1 - 0.075, DZ1 - 0.075, DZ1 - 0.05), (DX0 + 0.075, DX1 - 0.075, DZ0 + 0.05, DZ0 + 0.075),
                           (DX0 + 0.075, DX1 - 0.075, 0.95, 0.975)):
        g.box(df, a0, a1, YBACK + 0.012, YBACK + 0.0145, b0, b1)
    parts.append(df)
    jb = P("door_jamb", "angle")
    for a0, a1, b0, b1 in ((DX0 - 0.032, DX0 - 0.003, DZ0 - 0.02, DZ1 + 0.03), (DX1 + 0.003, DX1 + 0.032, DZ0 - 0.02, DZ1 + 0.03),
                           (DX0 - 0.032, DX1 + 0.032, DZ1 + 0.003, DZ1 + 0.03)):
        g.box(jb, a0, a1, YBACK, YBACK + 0.004, b0, b1)
    parts.append(jb)
    hg = P("hinges", "hinge")
    for zc in (0.25, 1.00, 1.75):
        for z0, z1 in ((zc - 0.05, zc - 0.002), (zc + 0.002, zc + 0.05)):
            g.cyl(hg, (DX0 - 0.008, YBACK + 0.011, (z0 + z1) / 2), "z", 0.011, z1 - z0, 8)
        g.cyl(hg, (DX0 - 0.008, YBACK + 0.011, zc + 0.054), "z", 0.006, 0.008, 6)        # pin head
    g.pipe(hg, G.spline([(0.20, YBACK + 0.010, 0.90), (0.20, YBACK + 0.048, 0.925), (0.20, YBACK + 0.056, 1.0),
                         (0.20, YBACK + 0.048, 1.075), (0.20, YBACK + 0.010, 1.10)], 2), 0.009, 6)
    for zz in (0.90, 1.10):                                                         # handle feet
        g.box(hg, 0.185, 0.215, YBACK + 0.012, YBACK + 0.016, zz - 0.015, zz + 0.015)
    # lug: a plate on the door, a staple on the frame
    g.box(hg, 0.25, 0.365, YBACK + 0.012, YBACK + 0.016, 0.995, 1.045)
    parts.append(hg)
    sh = P("padlock_shackle", "shackle")
    g.pipe(sh, [(0.345, YBACK + 0.014, 1.003), (0.345, YBACK + 0.030, 1.003), (0.345, YBACK + 0.038, 1.012),
                (0.345, YBACK + 0.038, 1.028), (0.345, YBACK + 0.030, 1.037), (0.345, YBACK + 0.014, 1.037)], 0.0035, 5)
    ysh = YBACK + 0.026
    g.pipe(sh, G.spline([(0.331, ysh, 0.982), (0.331, ysh, 1.008), (0.336, ysh, 1.020), (0.345, ysh, 1.025),
                         (0.354, ysh, 1.020), (0.359, ysh, 1.008), (0.359, ysh, 0.982)], 1), 0.004, 5)
    parts.append(sh)
    lk = P("padlock", "lock")
    G.slab(lk, 0.32, 0.37, ysh - 0.011, ysh + 0.011, 0.935, 0.985, rc=0.006, nc=2, re=0.004, ne=1, rb=0.004, nb=1)
    g.box(lk, 0.341, 0.349, ysh + 0.011, ysh + 0.0125, 0.947, 0.962)              # keyhole
    parts.append(lk)
    # patch rivets
    rv = P("rivets", "rivet")
    pts = [(y, z) for y in (0.07, 0.17, 0.27, 0.38, 0.48) for z in (0.32, 0.83)] + \
          [(y, z) for z in (0.45, 0.58, 0.70) for y in (0.07, 0.48)]
    for y, z in pts:
        G.rivet(rv, (X1 + 0.004, y, z), (1, 0, 0), r=0.006, h=0.004, sides=6)
    parts.append(rv)
    return parts


# =============================================================================
# Fan on the left side (bone ozl_fan)
# =============================================================================
def build_fan(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    n = 16 if lod == 0 else 8
    c = Vector((X0, FY, FZ))
    parts = []
    # plate with a round window on the outer side of the wall: a 260 square, the window follows the duct
    pl = P("fan_plate", "fan_plate")
    bm = pl.bm
    xs = X0 - 0.003
    sq = G.square_ring(0.13, n)
    ci = [(FR * math.cos(2 * math.pi * k / n), FR * math.sin(2 * math.pi * k / n)) for k in range(n)]
    vo = [bm.verts.new((xs, FY + a, FZ + b)) for a, b in sq]
    vi = [bm.verts.new((xs, FY + a, FZ + b)) for a, b in ci]
    vb = [bm.verts.new((X0 + 0.0005, FY + a, FZ + b)) for a, b in sq]
    for k in range(n):
        j = (k + 1) % n
        G.face(pl, [vi[k], vi[j], vo[j], vo[k]], (-1, 0, 0))
        G.face(pl, [vo[k], vo[j], vb[j], vb[k]], (0, (sq[k][0] + sq[j][0]) / 2, (sq[k][1] + sq[j][1]) / 2))
    parts.append(pl)
    # duct: dark inside (faces inward), a blind bottom at the back - the booth interior is not visible
    du = P("fan_duct", "duct")
    G.lathe(du, [(FR, 0.10), (FR, -0.003)], n, c, "x")
    G.lathe(du, [(0.0, 0.10), (FR, 0.10)], n, c, "x")
    parts.append(du)
    # motor on three posts
    mt = P("fan_motor", "fan_motor")
    g.cyl(mt, (X0 + 0.079, FY, FZ), "x", 0.042, 0.032, n)
    if lod == 0:
        for k in range(3):
            t = math.radians(90 + 120 * k)
            d = Vector((0.0, math.cos(t), math.sin(t)))
            G.rod(mt, c + Vector((0.079, 0, 0)) + d * 0.038, c + Vector((0.079, 0, 0)) + d * (FR + 0.002), 0.004, 4)
    parts.append(mt)
    # rotor: hub with a cone and five twisted blades
    rt = P("fan_rotor", "fan_blade", group=SEL_FAN)
    hub = c + Vector((0.050, 0, 0))
    if lod == 0:
        G.lathe(rt, [(0.026, -0.012), (0.026, 0.002), (0.020, 0.009), (0.010, 0.012), (0.0, 0.013)], n, hub, "-x")
        st = [(0.024, 0.010, 40.0), (0.055, 0.020, 30.0), (0.086, 0.026, 22.0)]
    else:
        g.cyl(rt, tuple(hub), "x", 0.026, 0.02, 6)
        st = [(0.024, 0.010, 35.0), (0.086, 0.024, 25.0)]
    ax_a, ax_b, ax_w = Vector((0, 1, 0)), Vector((0, 0, 1)), Vector((-1, 0, 0))
    for k in range(5):
        G.fan_blade(rt, hub, ax_a, ax_b, ax_w, 2 * math.pi * k / 5 + 0.3, st, 0.0025)
    parts.append(rt)
    # wire guard on four bolts
    gd = P("fan_guard", "guard")
    xg = X0 - 0.016
    G.torus(gd, g.Frame((xg, FY, FZ), (0, 1, 0), (0, 0, 1), (-1, 0, 0)), 0.100, 0.0025, 20 if lod == 0 else 12,
            4 if lod == 0 else 3)
    if lod == 0:
        G.torus(gd, g.Frame((xg - 0.003, FY, FZ), (0, 1, 0), (0, 0, 1), (-1, 0, 0)), 0.058, 0.0025, 12, 4)
        g.cyl(gd, (xg - 0.004, FY, FZ), "x", 0.014, 0.003, 8)
    for k in range(4 if lod == 0 else 2):
        t = math.pi / 4 + k * math.pi / (2 if lod == 0 else 1)
        d = Vector((0.0, math.cos(t), math.sin(t)))
        g.pipe(gd, [tuple(c + Vector((-0.019, 0, 0)) + d * 0.012), tuple(c + Vector((-0.016, 0, 0)) + d * 0.10),
                    tuple(c + Vector((-0.004, 0, 0)) + d * 0.150)], 0.0025, 4 if lod == 0 else 3)
    parts.append(gd)
    if lod == 0:
        bt = P("fan_bolts", "screw")
        for sy in (-1, 1):
            for sz in (-1, 1):
                g.cyl(bt, (X0 - 0.0055, FY + sy * 0.11, FZ + sz * 0.11), "x", 0.008, 0.005, 6)
        parts.append(bt)
    return parts


# =============================================================================
# Customer shelf, tray with a shutter
# =============================================================================
def build_ledge(spec):
    lod, bev = spec["lod"], spec["bev"]
    parts = []
    bd = P("ledge", "board")
    if lod == 0:
        for i, (y0, y1) in enumerate(BOARDS):
            spans = [(X0 + 0.02, X1 - 0.02)] if i == 0 else [(X0 + 0.02, TX0 - 0.0015), (TX1 + 0.0015, X1 - 0.02)]
            for x0, x1 in spans:
                G.slab(bd, x0, x1, y0, y1, Z0B, ZC, re=0.005, ne=2, rb=0.002, nb=1)
    else:
        g.box(bd, X0 + 0.02, TX0, TY0, YB - T, Z0B, ZC)
        g.box(bd, TX1, X1 - 0.02, TY0, YB - T, Z0B, ZC)
        g.box(bd, X0 + 0.02, X1 - 0.02, LY0, TY0, Z0B, ZC)
    parts.append(bd)
    # shelf frame: a 50 x 4 angle along the front edge - the leg up covers the board ends
    fa = P("ledge_edge", "angle")
    if lod < 2:
        sec = G.angle_section(0.05, 0.004, 0.004, 2 if lod == 0 else 0)
        G.prism_poly(fa, sec, lambda a, b, c: Vector((c, LY0 - 0.004 + a, Z0B - 0.004 + b)), X0 + 0.02, X1 - 0.02)
    else:
        g.box(fa, X0 + 0.02, X1 - 0.02, LY0 - 0.004, LY0, Z0B - 0.004, ZC + 0.006)
    parts.append(fa)
    # brackets: an angle under the boards, an angle along the wall, a strip brace, welded
    br = P("brackets", "angle")
    if lod == 0:
        sec4 = G.angle_section(0.04, 0.004, 0.004, 1)
        for bx in (-0.70, 0.70):
            s = 1 if bx > 0 else -1
            G.prism_poly(br, sec4, lambda a, b, c, bx=bx, s=s: Vector((bx + s * a, c, Z0B - b)), LY0 + 0.046, YB - T - 0.004)
            G.prism_poly(br, sec4, lambda a, b, c, bx=bx, s=s: Vector((bx + s * a, YB - T - b, c)), Z0B - 0.26, Z0B)
            G.box_to(br, (bx + s * 0.0045, YB - T - 0.02, Z0B - 0.235), (bx + s * 0.0045, LY0 + 0.06, Z0B - 0.035),
                     0.035, 0.005, up=(1, 0, 0))
    else:
        for bx in (-0.70, 0.70):
            g.prism(br, [(YB - T, Z0B), (LY0 + 0.03, Z0B), (YB - T, Z0B - 0.22)], (1, 2), bx - 0.005, bx + 0.005)
    parts.append(br)
    if lod == 0:
        wd = P("ledge_welds", "weld")
        for k, bx in enumerate((-0.70, 0.70)):
            s = 1 if bx > 0 else -1
            G.blob(wd, (bx + s * 0.008, YB - T - 0.03, Z0B - 0.25), (s, -0.3, 0.2), 0.008, 0.005, 5, seed=k)
            G.blob(wd, (bx + s * 0.008, LY0 + 0.07, Z0B - 0.042), (s, -0.2, -0.3), 0.008, 0.005, 5, seed=k + 3)
        parts.append(wd)
        bt = P("ledge_bolts", "screw")
        for bx, s in ((-0.70, -1), (0.70, 1)):
            for y0, y1 in BOARDS:
                G.rivet(bt, (bx + s * 0.02, (y0 + y1) / 2, ZC), (0, 0, 1), r=0.0085, h=0.004, sides=6)
        parts.append(bt)
    # LK-1 tray: a stamped well (rounded corners and bottom), a screwed frame, an outer box
    tr = P("tray", "tray")
    sh = P("shutter", "shutter")
    if lod == 2:                                   # far LOD: the well is a box under the boards
        g.box(tr, TX0, TX1, TY0, YB, ZB, Z0B)
        g.box(sh, TX0, TX1, YB - 0.006, YB, ZB, ZC + RAIL)
        return parts + [tr, sh]
    nc = 3 if lod == 0 else 1
    rc, rf = 0.016, 0.012
    ctr = (0.0, (TY0 + TYB) / 2, ZB)

    def outl(d):
        return G.rrect(TX0 + d, TX1 - d, TY0 + d, TYB - d, max(rc - d, 0.002), nc)
    rings = [[(a, b, ZC) for a, b in outl(0.0)], [(a, b, ZB + rf) for a, b in outl(0.0)]]
    if lod == 0:
        d1 = rf * (1 - math.cos(math.radians(45)))
        rings.append([(a, b, ZB + rf * (1 - math.sin(math.radians(45)))) for a, b in outl(d1)])
    rings.append([(a, b, ZB) for a, b in outl(rf)])
    G.loft_inner(tr, rings, ctr, extra_cap=True)
    shell = G.rrect(TX0 - 0.003, TX1 + 0.003, TY0 - 0.003, TYB + 0.003, rc + 0.003, nc)
    G.wall_band(tr, shell, ZB - 0.003, Z0B, ctr)
    G.face(tr, [tr.bm.verts.new((a, b, ZB - 0.003)) for a, b in shell], (0, 0, -1))
    fl_in = outl(0.0)
    fl_out = G.rrect(TX0 - FL, TX1 + FL, TY0 - FL, TYB + FL, rc + FL, nc)
    G.ring_flat(tr, fl_in, fl_out, ZC + 0.003)
    G.wall_band(tr, fl_out, ZC, ZC + 0.003, ctr)
    G.loft_inner(tr, [[(a, b, ZC + 0.003) for a, b in fl_in], [(a, b, ZC) for a, b in fl_in]], ctr)
    parts.append(tr)
    if lod == 0:
        sc = P("tray_screws", "screw")
        for x, y in ((TX0 - FL / 2, TY0 + 0.03), (TX0 - FL / 2, YB - 0.06), (TX1 + FL / 2, TY0 + 0.03),
                     (TX1 + FL / 2, YB - 0.06), (-0.12, TY0 - FL / 2), (0.12, TY0 - FL / 2)):
            g.cyl(sc, (x, y, ZC + 0.0036), "z", 0.0045, 0.0012, 8)
        parts.append(sc)
    # shutter behind the well: a dark sheet with a rib
    g.box(sh, TX0, TX1, YB - 0.006, YB, ZB, ZC + RAIL, r=0.0015 if bev else 0.0, seg=bev)
    if lod == 0:
        g.box(sh, TX0 + 0.012, TX1 - 0.012, YB - 0.009, YB - 0.006, ZB + 0.040, ZB + 0.052, r=0.001, seg=1)
    parts.append(sh)
    return parts


# =============================================================================
# Partition: frame, panes on glazing beads, tape over the crack, speaking grille
# =============================================================================
def build_partition(spec):
    lod, bev = spec["lod"], spec["bev"]
    r = 0.003 if bev else 0.0
    parts = []
    fr = P("frame", "frame")
    g.box(fr, X0, X1, YF0, YF1, ZC, ZC + RAIL, r=r, seg=bev)                       # lower chord above the shelf
    g.box(fr, X0, X1, YF0, YF1, ZG - 0.04, ZG, r=r, seg=bev)
    for xa, xb in ((X0, X0 + 0.04), (X1 - 0.04, X1)) + tuple((m - 0.02, m + 0.02) for m in MULL):
        g.box(fr, xa, xb, YF0, YF1, ZC + RAIL, ZG - 0.04, r=r, seg=bev)
    parts.append(fr)
    gl = P("glass", "glass", group=SEL_GLASS)
    for xa, xb in PANES:
        g.box(gl, xa, xb, YGL, YGL + 0.012, GZ0, GZ1)
    parts.append(gl)
    if lod == 0:
        bd = P("beads", "bead")
        sl = P("seals", "seal")
        for xa, xb in PANES:
            for a0, a1, b0, b1 in ((xa, xb, GZ1 - BW, GZ1), (xa, xb, GZ0, GZ0 + BW), (xa, xa + BW, GZ0 + BW, GZ1 - BW),
                                   (xb - BW, xb, GZ0 + BW, GZ1 - BW)):
                g.box(bd, a0, a1, YGL - 0.016, YGL, b0, b1)
            # seal - only a 4 mm strip at the bead edge is visible: one face
            ia0, ia1, ib0, ib1 = xa + BW, xb - BW, GZ0 + BW, GZ1 - BW
            ys = YGL - 0.0008
            for a0, a1, b0, b1 in ((ia0, ia1, ib1 - 0.004, ib1), (ia0, ia1, ib0, ib0 + 0.004),
                                   (ia0, ia0 + 0.004, ib0 + 0.004, ib1 - 0.004), (ia1 - 0.004, ia1, ib0 + 0.004, ib1 - 0.004)):
                g.quad(sl, [(a0, ys, b0), (a1, ys, b0), (a1, ys, b1), (a0, ys, b1)])
        parts += [bd, sl]
    if lod < 2:
        tp = P("tape", "tape")
        for (ax, az), (bx, bz) in TAPE:
            u = Vector((bx - ax, 0.0, bz - az))
            ln = u.length
            u.normalize()
            v = Vector((-u.z, 0.0, u.x))
            g.box(tp, 0.0, ln, -0.024, 0.024, 0.0002, 0.0008, frame=g.Frame((ax, YGL, az), u, v, (0, -1, 0)))
        parts.append(tp)
    # dia. 160 speaking grille: a convex perforated disc in a ring on screws
    tk = P("talk", "talk")
    c = Vector((TALK[0], YGL, TALK[1]))
    if lod == 0:
        G.lathe(tk, [(0.071, 0.0), (0.071, 0.0035), (0.050, 0.0048), (0.0, 0.0055)], 16, c, "-y")
        rg = P("talk_ring", "frame")
        G.lathe(rg, [(0.086, 0.0), (0.086, 0.004), (0.082, 0.0085), (0.076, 0.0085), (0.071, 0.0045)], 16, c, "-y")
        for t in (45, 135, 225, 315):
            a = math.radians(t)
            G.rivet(rg, c + Vector((0.079 * math.cos(a), -0.0085, 0.079 * math.sin(a))), (0, -1, 0), r=0.004,
                    h=0.0015, sides=6)
        parts += [tk, rg]
    else:
        g.cyl(tk, (TALK[0], YGL - 0.003, TALK[1]), "y", 0.08, 0.006, 8)
        parts.append(tk)
    return parts


# =============================================================================
# Rebar grille: rods, strips, speaking-grille ring, tacks
# =============================================================================
def build_rebar(spec):
    lod, sd = spec["lod"], spec["sides"]
    rb = P("rebar", "rebar")
    parts = [rb]
    za, zb = RZ0 - 0.012, RZ1 + 0.012
    for x in RODS:
        segs = [(za, zb)]
        if abs(x - TALK[0]) < 1e-6 and lod < 2:
            segs = [(za, TALK[1] - TALK_R), (TALK[1] + TALK_R, zb)]
        for s0, s1 in segs:
            if lod == 2:
                g.quad(rb, [(x - 0.006, YR - 0.006, s0), (x + 0.006, YR - 0.006, s0), (x + 0.006, YR - 0.006, s1),
                            (x - 0.006, YR - 0.006, s1)])
            elif lod == 1:
                g.box(rb, x - 0.006, x + 0.006, YR - 0.006, YR + 0.006, s0, s1)
            elif abs(x - BENT) < 1e-6:                                    # bent outward: it was broken
                g.pipe(rb, G.spline([(x, YR, s0), (x, YR, 1.25), (x, YR - 0.012, 1.36), (x, YR - 0.030, 1.50),
                                     (x, YR - 0.014, 1.64), (x, YR, 1.75), (x, YR, s1)], 2), 0.006, sd)
            else:
                G.rod(rb, (x, YR, s0), (x, YR, s1), 0.006, sd)
    if lod < 2:
        G.torus(rb, g.Frame((TALK[0], YR, TALK[1]), (1, 0, 0), (0, 0, 1), (0, -1, 0)), TALK_R, 0.006,
                24 if lod == 0 else 10, 6 if lod == 0 else 3)
    for z in FLATS:
        g.box(rb, X0 + 0.03, X1 - 0.03, YR - 0.012, YR - 0.006, z - FW, z + FW, **(dict(r=0.002, seg=1) if lod == 0 else {}))
    if lod == 0:
        for x in (X0 + 0.03, X1 - 0.07):                                   # tacks to the frame
            for z in FLATS:
                g.box(rb, x, x + 0.04, YR - 0.006, YF0, z - 0.015, z + 0.015)
    if lod == 0:
        wd = P("rebar_welds", "weld")
        for k, x in enumerate(RODS):
            G.blob(wd, (x, YR - 0.009, FLATS[0] + FW), (0, -0.4, 1), 0.0065, 0.004, 5, seed=k)
            G.blob(wd, (x, YR - 0.009, FLATS[3] - FW), (0, -0.4, -1), 0.0065, 0.004, 5, seed=k + 20)
        for (px, pz), nn in (((0.0, TALK[1] + TALK_R), (0, -0.3, 1)), ((0.0, TALK[1] - TALK_R), (0, -0.3, -1)),
                             ((-TALK_R - 0.005, TALK[1]), (-1, -0.3, 0)), ((TALK_R + 0.005, TALK[1]), (1, -0.3, 0))):
            G.blob(wd, (px, YR - 0.004, pz), nn, 0.007, 0.004, 5, seed=px * 10 + pz)
        parts.append(wd)
    return parts


# =============================================================================
# Lamp above the window, board, wires
# =============================================================================
def build_lamp(spec):
    lod = spec["lod"]
    n = 16 if lod == 0 else (8 if lod == 1 else 6)
    c = Vector((0.0, LY, LZ))
    lb = P("lamp_body", "lamp_body")
    lg = P("lamp_glass", "lamp_glass", group=SEL_LAMP)
    if lod == 2:
        g.cyl(lb, (0.0, LY - 0.011, LZ), "y", 0.056, 0.022, n)
        g.cyl(lg, (0.0, LY - 0.040, LZ), "y", 0.044, 0.036, n, r2=0.03)
        return [lb, lg]
    # cast body on the canopy: base, rim, ring for the dome
    G.lathe(lb, [(0.058, 0.0), (0.058, 0.012), (0.055, 0.018), (0.049, 0.022)], n, c, "-y", caps=(False, True))
    G.lathe(lg, [(0.045, 0.021), (0.044, 0.036), (0.037, 0.052), (0.024, 0.063), (0.0, 0.067)] if lod == 0 else
            [(0.045, 0.021), (0.036, 0.052), (0.0, 0.066)], n, c, "-y")
    parts = [lb, lg]
    cg = P("lamp_cage", "cage")
    G.torus(cg, g.Frame(c + Vector((0, -0.024, 0)), (1, 0, 0), (0, 0, 1), (0, -1, 0)), 0.050, 0.003,
            16 if lod == 0 else 8, 4 if lod == 0 else 3)
    m = 8 if lod == 0 else 4
    for t in (math.radians(45), math.radians(135)):                        # two arcs crosswise
        d = Vector((math.cos(t), 0.0, math.sin(t)))
        pts = [c + d * (0.050 * math.cos(math.pi * k / m)) + Vector((0, -1, 0)) * (0.024 + 0.050 * math.sin(math.pi * k / m))
               for k in range(m + 1)]
        g.pipe(cg, pts, 0.0028, 5 if lod == 0 else 4)
    parts.append(cg)
    if lod == 0:
        for t in (45, 135, 225, 315):                                      # base screws
            a = math.radians(t)
            G.rivet(lb, c + Vector((0.052 * math.cos(a), -0.0198, 0.052 * math.sin(a))), (0, -1, 0), r=0.004, h=0.002,
                    sides=6, dome=False)
    return parts


def build_board(spec):
    """Exchange-rate board: sheet-metal case, window frame, screen (section screen, frames), hooks on the strip."""
    lod = spec["lod"]
    x0, x1, z0, z1 = BRD
    y0, y1 = BRD_Y0, BRD_Y1
    parts = []
    cs = P("board_case", "led_case")
    if lod == 0:
        g.box(cs, x0, x1, y0 + 0.004, y1, z0, z1, r=0.004, seg=1)
        for a0, a1, b0, b1 in ((x0 + 0.002, x1 - 0.002, z1 - BEZ, z1 - 0.002), (x0 + 0.002, x1 - 0.002, z0 + 0.002, z0 + BEZ),
                               (x0 + 0.002, x0 + BEZ, z0 + BEZ, z1 - BEZ), (x1 - BEZ, x1 - 0.002, z0 + BEZ, z1 - BEZ)):
            g.box(cs, a0, a1, y0, y0 + 0.005, b0, b1)
    else:
        g.box(cs, x0, x1, y0, y1, z0, z1)
    parts.append(cs)
    sc = P("board_screen", "led_case", group=SEL_SCREEN, section="screen")
    a0, a1, b0, b1 = x0 + BEZ, x1 - BEZ, z0 + BEZ, z1 - BEZ
    ys = y0 + 0.0035 if lod == 0 else y0 - 0.0006
    vs = [sc.bm.verts.new((a, ys, b)) for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
    G.face(sc, vs, (0, -1, 0))
    sc.glass_frame = (g.Frame((0.0, ys, 0.0), (1, 0, 0), (0, 0, 1), (0, -1, 0)), a0, a1, b0, b1)
    parts.append(sc)
    if lod == 0:
        hk = P("board_hooks", "wire")
        zt = FLATS[2] + FW
        for hx in (x0 + 0.06, x1 - 0.06):
            g.pipe(hk, G.spline([(hx, y1 - 0.016, z1 - 0.003), (hx, y1 - 0.016, z1 + 0.04), (hx, YR - 0.010, zt + 0.012),
                                 (hx, YR - 0.0035, zt + 0.004), (hx, YR - 0.0035, zt - 0.02)], 2), 0.002, 4)
        parts.append(hk)
    return parts


def build_cables(spec):
    """The lamp wire goes to the canopy gland; the board wire goes
    through the grille to the gland of the frame post."""
    lod = spec["lod"]
    if lod == 2:
        return []
    k, sd = (2, 6) if lod == 0 else (1, 4)
    x0, x1, z0, z1 = BRD
    ym = (BRD_Y0 + BRD_Y1) / 2
    cb = P("cables", "cable")
    g.pipe(cb, G.spline([(-0.070, LY - 0.008, LZ), (-0.10, LY - 0.013, LZ - 0.022), (-0.15, LY - 0.013, LZ - 0.030),
                         (-0.19, LY - 0.010, LZ - 0.016), (-0.20, LY - 0.012, LZ - 0.006)], k), 0.0045, sd)
    g.pipe(cb, G.spline([(x1 + 0.010, ym, z0 + 0.05), (x1 + 0.032, ym - 0.004, z0 + 0.018), (-0.33, -0.502, z0 - 0.035),
                         (-0.30, -0.476, z0 - 0.045), (-0.30, YF0 - 0.012, 1.50)], k), 0.004, sd)
    parts = [cb]
    if lod == 0:
        gl = P("glands", "gland")
        g.cyl(gl, (-0.064, LY - 0.008, LZ), "x", 0.007, 0.014, 8)                 # lamp gland
        g.cyl(gl, (-0.20, LY - 0.006, LZ - 0.006), "y", 0.008, 0.012, 8)          # canopy gland
        g.cyl(gl, (x1 + 0.006, ym, z0 + 0.05), "x", 0.006, 0.012, 8)               # board gland
        g.cyl(gl, (-0.30, YF0 - 0.006, 1.50), "y", 0.007, 0.012, 8)               # frame post gland
        parts.append(gl)
    return parts


# =============================================================================
# Small things: ashtray, butts, cigarette packs
# =============================================================================
def ashtray(part, cx, cy, z, n, notches=True):
    """Stamped tin ashtray dia. 116: bottom, sloped wall, rolled edge with three notches for a cigarette;
    traversed outside upward, over the edge, inward and onto the bottom."""
    prof = [(0.047, 0.0), (0.052, 0.003), (0.056, 0.017), (0.058, 0.020), (0.056, 0.0225), (0.053, 0.020),
            (0.049, 0.006), (0.042, 0.003), (0.0, 0.003)]
    wgt = [0.0, 0.0, 0.7, 1.0, 1.0, 0.9, 0.0, 0.0, 0.0]
    bm = part.bm
    rings = []
    for i, (r, h) in enumerate(prof):
        if r < 1e-7:
            rings.append(bm.verts.new((cx, cy, z + h)))
            continue
        ring = []
        for k in range(n):
            t = 2 * math.pi * k / n
            dip = max(0.0, math.cos(3 * t)) ** 10 if notches else 0.0
            ring.append(bm.verts.new((cx + r * math.cos(t), cy + r * math.sin(t), z + h - 0.008 * wgt[i] * dip)))
        rings.append(ring)
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        R0, R1 = rings[i], rings[i + 1]
        for k in range(n):
            j = (k + 1) % n
            tm = 2 * math.pi * (k + 0.5) / n
            want = Vector((math.cos(tm) * (h1 - h0), math.sin(tm) * (h1 - h0), -(r1 - r0)))
            vs = [R0[k], R0[j], R1[j], R1[k]] if isinstance(R1, list) else [R0[k], R0[j], R1]
            G.face(part, vs, want)
    G.face(part, rings[0], (0, 0, -1))


def butt(fl, bt, ah, p, d, length, sd=5):
    """Cigarette butt dia. 7.8: filter 20 mm, crumpled paper with a kink, ash at the end."""
    p, d = Vector(p), Vector(d).normalized()
    side = Vector((-d.y, d.x, 0.0))
    a = p + d * 0.02
    g.pipe(fl, [tuple(p), tuple(a)], 0.0039, sd)
    m = a + d * ((length - 0.02) * 0.55) + side * 0.002
    e = a + d * (length - 0.02) + side * 0.004 + Vector((0, 0, -0.0012))
    g.pipe(bt, [tuple(a), tuple(m), tuple(e)], 0.0037, sd)
    g.pipe(ah, [tuple(e), tuple(e + (e - m).normalized() * 0.003)], 0.0034, sd)


# butts: (filter, direction, length) - in the ashtray, one in a notch, and on the ground under the shelf
BUTTS = [((ASH[0] + 0.030, ASH[1] + 0.000, ZC + 0.0072), (-1.0, 0.2, 0.0), 0.032),
         ((ASH[0] - 0.025, ASH[1] + 0.020, ZC + 0.0072), (0.8, -0.5, 0.0), 0.028),
         ((ASH[0] + 0.005, ASH[1] - 0.030, ZC + 0.0072), (0.1, 1.0, 0.0), 0.035),
         ((ASH[0] + 0.074, ASH[1] + 0.000, ZC + 0.0205), (-1.0, 0.0, -0.22), 0.050),
         ((-0.26, -0.62, 0.0039), (1.0, 0.3, 0.0), 0.030),
         ((-0.46, -0.50, 0.0039), (0.3, -1.0, 0.0), 0.025),
         ((-0.20, -0.48, 0.0039), (-0.7, 0.7, 0.0), 0.032),
         ((0.10, -0.62, 0.0039), (1.0, -0.2, 0.0), 0.028),
         ((0.58, -0.52, 0.0039), (-0.4, -1.0, 0.0), 0.030)]


def cig_pack(part, fr, L=0.088, W=0.055, H=0.022):
    """A "Chernomorka" pack lying face up in frame fr (u along the pack, v across, n up): a box, each face has
    its UV on its own piece of the vanilla texture (CIGS_UV); the top of the face picture is toward +u (from M16)."""
    bm = part.bm
    uvl = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    hl, hw = L / 2, W / 2
    sides = [
        ([(a, b, H) for a, b in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))], (0, 0, 1), "front",
         lambda a, b, c: ((hw - b) / W, (a + hl) / L)),
        ([(a, b, 0.0) for a, b in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))], (0, 0, -1), "front",
         lambda a, b, c: ((b + hw) / W, (a + hl) / L)),
        ([(a, -hw, c) for a, c in ((-hl, 0.0), (hl, 0.0), (hl, H), (-hl, H))], (0, -1, 0), "side",
         lambda a, b, c: (c / H, (a + hl) / L)),
        ([(a, hw, c) for a, c in ((-hl, 0.0), (hl, 0.0), (hl, H), (-hl, H))], (0, 1, 0), "side",
         lambda a, b, c: (1.0 - c / H, (a + hl) / L)),
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


def build_clutter(spec):
    """On the customer shelf: an ashtray with butts, "Chernomorka" packs; butts on the ground under the shelf
    (the rest are vanilla DECOR items)."""
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    tn = P("ashtray", "tin")
    if lod == 0:
        ashtray(tn, ASH[0], ASH[1], ZC, 18)                  # 18 faces: notches (0, 120, 240 deg) fall on vertices
    else:
        g.cyl(tn, (ASH[0], ASH[1], ZC + 0.011), "z", 0.052, 0.022, 8, r2=0.058)
    parts.append(tn)
    pk = P("packs", "carton", section="cigs")
    pk.fixed_uv = True
    for (cx, cy), deg, dz in PACKS:
        cig_pack(pk, G.frame_z(cx, cy, deg, ZC + dz))
    parts.append(pk)
    if lod == 0:
        fl, bt, ah = P("butt_filters", "filter"), P("butt_paper", "butt"), P("butt_ash", "ash")
        for p, d, ln in BUTTS:
            butt(fl, bt, ah, p, d, ln, 5 if p[2] > ZC - 0.01 else 4)      # smoother on shelf, simpler on ground
        parts += [fl, bt, ah]
    return parts


def build_lod(spec):
    parts = build_shell(spec) + build_fan(spec) + build_ledge(spec) + build_partition(spec) + build_rebar(spec)
    parts += build_lamp(spec) + build_board(spec) + build_cables(spec) + build_clutter(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """Booth - two convex pieces: the bottom with the shelf and the top with
    the partition and the canopy (both thicker than 0.5 m)."""
    metal = kx.PEN + r"\metalplate.rvmat"
    low = kx.box_pts(X0, X1, LY0, YBACK + 0.02, 0.0, ZC)
    top = kx.box_pts(X0, X1, YR - 0.02, YBACK + 0.02, ZC, H)
    memory = {
        "invView": [(0.0, -2.6, 1.4)],
        "ce_center": [(0.0, 0.0, H / 2)],
        "ce_radius": [(1.3, 0.0, H / 2)],
        "ozl_fan_axis": [(X0 + 0.05, FY, FZ), (X0 - 0.05, FY, FZ)],
    }
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    return [(low, metal), (top, metal)], 400.0, memory, (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2] + 0.004)


# the first ones are for the --look preview: overview, the board with the lamp (also in "work", and look B),
# the shelf with the tray, at an angle (the fan), the glass with tape, the fan close up; then for the shape and baking
SHOTS = [
    ("front", (0.0, -3.4, 1.5), (0.0, 0.0, 1.05), 32),
    ("board", (-0.10, -1.60, 1.70), (-0.32, -0.45, 1.66), 32),
    ("tray", (0.35, -1.25, 1.45), (0.0, -0.45, 1.0), 35),
    ("angle", (-1.3, -2.3, 1.7), (0.0, -0.3, 1.05), 32),
    ("glass", (0.85, -1.45, 1.62), (0.55, -0.42, 1.52), 35),
    ("fan", (-1.55, -0.75, 1.80), (-0.90, -0.12, 1.70), 40),
    ("ground", (0.20, -1.55, 0.70), (0.0, -0.50, 0.30), 32),
    ("back", (1.8, 2.8, 1.8), (0.0, 0.0, 1.0), 32),
]

M.look_shots = (6, 2)
M.run(build_lod, collision, SHOTS, row_step=2.2, row_shot=((2.2, -7.0, 2.2), (2.2, 0, 1.0)))
