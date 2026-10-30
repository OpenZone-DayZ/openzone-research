"""M18 - bartender's safe: Khabar Sample-Prep Station of the Neutrals (OZL_Lnr_Pack_Khabar).
Packer: cargo 10x10, three module places on the roof (module_1..3) and module proxies there.

    blender --background --python build_m18.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: system Python make_decals.py (code dial scale, enamel wear at the handle, blank
nameplate, golden trim of the door and sides, leather pad). Sizes shared with the decals - m18_layout.py;
own geometry - m18_geo.py, own materials - m18_mats.py.

The device is an old Soviet fireproof cabinet (look-alikes: a bank cabinet with a dial and a wheel; a
Russian "Meller" cabinet in brown enamel on a cast plinth with golden trim on the panels; a
mid-20th-century Samson cabinet: smooth door, dial, T-handle).
Sizes: no datasheets of Soviet fireproof cabinets could be found (only modern cabinets and listings
without sizes). Width and depth follow a sales listing of a 1982 Soviet safe-type metal cabinet,
757 x 425 x 1515 mm (W x D x H), 120-150 kg; a second reference is a Soviet safe at 600 x 400 x 1600.
The height is 1.40 m, not 1.515: the modules stand on the roof, and from a 1.5 m roof they are barely
visible; cabinets of this class are 1.4-1.6 m. Result: 0.757 x 1.40 x 0.425 m, 0.50 m with the wheel at
the front, a cast plinth on four feet.

Look:
- the "dayz" look: matte, dirtier, streaks and patches, shadows in corners; for small things on the roof
  the dirt pattern is finer (m18_mats, scale), otherwise one patch covers a whole mug;
- the safe in detail: body edges rounded R25 in 4 segments, around the door a rebate frame (a bead with a
  rounded top) and a dark gap, on the door a moulding of semicircular section and golden trim (a double
  frame with concave corners; worn at the wheel), the same on the sides; barrel hinges of two halves with
  a pin, cast brackets, screws and brass caps; wheel: a brass rosette on four screws, a cast hub with a
  nut, four oval spokes bent toward the door, a round-section rim; code dial: a rosette with a mark, a
  disc with a 0-99 scale, a knurled handle with a dome; keyhole cover - a shaped plate with a shutter on a
  pin and two screws; a nameplate on four rivets; the feet of the cast plinth are turned "buns", two
  bolts on the plinth; bronze and brass - with dark patina in recesses and rubbed bright by hands on the
  edges;
- modules in their places: slot 1 - dosimeter M75 in the middle at the front, slot 2 - loupe M76 under
  the lamp (at the left: the shade faces its lens), slot 3 - lead case M77 at the right. Empty places are
  not empty: under M75 on the dusty roof a clean spot from the box and a spare "Krona" behind it; under
  the loupe a leather pad with stitching and a ring pressed by the bell; under the case (23 kg) a
  backing board. There is no cloth over the whole roof;
- small things - vanilla DayZ items as proxies (there is no Proxy<name> class): a vodka bottle, a 9 V
  battery (a spare for the dosimeter), a bunch of keys; own - jars with bolts (glass with a neck and
  thread, a heap of bolts with heads, the heads at the wall are visible through the glass; one jar is
  closed with its lid, the lid of the other lies beside it upside down), a bolt and a nut on the roof, an
  enamelled mug with a blue rim, a strap handle, tea and an aluminium spoon;
- a desk lamp: a cast base with a switch, a chromed stand, a joint with a wing nut, an elbow, a conical
  shade with a rolled edge and a socket, a bulb; a cord in a cloth braid - from the base behind the
  roof, down the back in a smooth curve, along the floor to the plug.

Work look: the lamp (bulb and the white inside of the shade) is ozl_lamp in hiddenSelections, "work" is
the _on atlas and an rvmat with glow (lit while the station works). The code dial is the bone ozl_work on
the source ozl_work (0..1 is a full turn; in "work" - wobble: the dial goes back and forth, someone is
"dialling the code"). The wheel is the bone ozl_wheel on the source ozl_wheel (pose: in "work" it turns
by 60 degrees in 1.2 s - the bolts are drawn back, then back again). Class OZL_Work is described in the
mod.

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
import kvanilla as kv  # noqa: E402
import m18_geo as G  # noqa: E402
import m18_layout as L  # noqa: E402
import m18_mats as MT  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m (shared with the decals - m18_layout.py)
# =============================================================================
X0, X1, Y0, Y1 = L.X0, L.X1, L.Y0, L.Y1
ZB, ZR, R_BODY = L.ZB, L.ZR, L.R_BODY
DX0, DX1, DZ0, DZ1, YD, GAP = L.DX0, L.DX1, L.DZ0, L.DZ1, L.YD, L.GAP
DCX, DCZ = (DX0 + DX1) / 2, (DZ0 + DZ1) / 2
# rebate frame (offset outward from the gap, height above the body face) and door moulding (across the bead)
BAND_PROF = [(0.0, 0.0), (0.0, 0.0028), (0.0025, 0.0042), (0.008, 0.0048), (0.016, 0.0044), (0.023, 0.0028),
             (0.027, 0.0008), (0.028, 0.0)]
BEAD_PROF = [(-0.0045, 0.0), (-0.0038, 0.0017), (-0.0022, 0.0033), (0.0, 0.0040), (0.0022, 0.0033), (0.0038, 0.0017),
             (0.0045, 0.0)]
# hinges: barrel axis, radius, half height; hinge centres by height
HINGES = (0.36, 1.12)
HX, HY, HR, HH = DX0 - 0.004, YD - 0.012, 0.016, 0.072
FIN_PROF = [(0.013, 0.0), (0.009, 0.006), (0.0075, 0.009), (0.0105, 0.0150), (0.0060, 0.0235), (0.0, 0.027)]
PLATE_Z, PLATE = L.PLATE_Z, L.PLATE
DIAL_Z, DIAL_R, ROSE_R = L.DIAL_Z, L.DIAL_R, L.ROSE_R
WHEEL_Z, WHEEL_R, WHEEL_T = L.WHEEL_Z, L.WHEEL_R, L.WHEEL_T
WHEEL_Y = YD - 0.065                                        # plane of the rim
KEY_Z = L.KEY_Z
# plinth: a cast plate and four "bun" feet
PL_IN, FOOT_H = 0.015, 0.038
FOOT_PROF = [(0.034, 0.0), (0.046, 0.004), (0.0515, 0.015), (0.049, 0.026), (0.040, 0.035), (0.034, 0.038)]
FEET = [(sx * (X1 - 0.075), sy * (Y1 - 0.075)) for sx in (-1, 1) for sy in (-1, 1)]

# roof: module places (slot N = module N of the "Khabar" line: M75, M76, M77)
MODS = [(L.SLOT1[0], L.SLOT1[1], ZR), (L.SLOT2[0], L.SLOT2[1], ZR + L.PAD[4]),
        (L.SLOT3[0], L.SLOT3[1], ZR + L.BOARD[4])]
MOD_OBJ = [("m75_dosimeter", "ozr_dosimeter"), ("m76_jeweler_loupe", "ozr_jeweler_loupe"),
           ("m77_lead_case", "ozr_lead_case")]
# module extents in plan from the proxy point (their near LODs, build/model-root): for checking the layout
MOD_BOX = [(-0.104, 0.100, -0.074, 0.071, 0.166), (-0.097, 0.097, -0.090, 0.097, 0.224),
           (-0.102, 0.099, -0.076, 0.078, 0.113)]
# empty slot 1: a clean spot from the dosimeter box (box 0.200 x 0.114, shifted forward by 15 mm - build_m75)
CLEAN1 = (L.SLOT1[0] - 0.100, L.SLOT1[0] + 0.100, L.SLOT1[1] - 0.072, L.SLOT1[1] + 0.042)
# lamp: base at the rear left, the shade faces the lens of the M76 loupe (build_m76: L = (0.034, -0.036, 0.092))
LAMP_C = (-0.26, 0.11)
JOINT = Vector((LAMP_C[0], LAMP_C[1], ZR + 0.35))
SHADE_DIR = Vector((0.12, -0.42, -0.90)).normalized()      # shade axis toward the flare
LENS = Vector((MODS[1][0] + 0.034, MODS[1][1] - 0.036, MODS[1][2] + 0.092))
SHADE_LEN = 0.125
APEX = LENS - SHADE_DIR * (0.25 + SHADE_LEN)                # cone apex; the flare is 0.25 m from the lens
# 0.5 l jars with bolts: centre, bolt height, with a lid; the lid of the open jar is on the roof upside down
JARS = [((-0.13, 0.13), 0.088, True), ((-0.035, 0.125), 0.062, False)]
JAR_R, JAR_H = 0.045, 0.130
LID_LOOSE = (0.06, 0.13)
MUG_C, MUG_R, MUG_H = (0.165, 0.125), 0.041, 0.087
LOOSE_BOLT = ((0.205, 0.058), 8.0)                          # bolt on the roof: head start, heading, degrees
LOOSE_NUT = (0.128, 0.072)

LOD_SPECS = [
    dict(lod=0, sides=24),
    dict(lod=1, sides=10),
    dict(lod=2, sides=6),
]

REGIONS = {
    "enamel": ("enamel", 0.6), "frame": ("frame", 1.0), "door": ("door", 0.8), "bead": ("frame", 1.2),
    "hinge": ("hinge", 1.6), "iron": ("iron", 0.7), "iron_bolt": ("iron", 2.0), "dark": ("dark", 1.0),
    "bronze": ("bronze", 2.0), "brass": ("brass", 2.2), "dial": ("dial", 5.0), "plate": ("plate", 4.0),
    "tag": ("tag", 3.0), "pad": ("pad", 1.6), "board": ("board", 1.4),
    "shade": ("shade", 1.5), "shade_in": ("shade_in", 1.5), "bulb": ("bulb", 3.0), "chrome": ("chrome", 1.5),
    "lamp_base": ("lamp_base", 1.5), "black": ("black", 1.5), "cord": ("cord", 1.0),
    "bolts": ("bolts", 3.0), "lid": ("lid", 3.0), "mug": ("mug", 2.0), "mug_rim": ("mug_rim", 2.0),
    "tea": ("tea", 2.0), "alu": ("alu", 3.0), "glass_jar": ("steel", 1.0),
}

# =============================================================================
# Materials
# =============================================================================


def decal(name, ax, sign, uv, center, size, rng=None):
    return (os.path.join(WORK, name), ax, sign, uv, center, size, rng)


lin = kmats.lin
FACE = (YD - 0.002, YD + 0.002)                             # door face (decals only on it)
PIN_DOOR = decal("decal_pin_door.png", "y", -1, ("x", "z"), (DCX, DCZ), (DX1 - DX0, DZ1 - DZ0), FACE)
WEAR = decal("decal_door_wear.png", "y", -1, ("x", "z"), L.WEAR_C, L.WEAR_S, FACE)
PIN_SIDES = [decal("decal_pin_side.png", "x", s, ("y", "z"), (0.0, (ZB + ZR) / 2), (Y1 - Y0, ZR - ZB),
                   (s * X1 - 0.002, s * X1 + 0.002)) for s in (-1, 1)]
DIAL_D = decal("decal_dial.png", "y", -1, ("x", "z"), (0.0, DIAL_Z), (2 * DIAL_R, 2 * DIAL_R))
PLATE_D = decal("decal_plate.png", "y", -1, ("x", "z"), (0.0, PLATE_Z), PLATE)
PAD_D = decal("decal_pad.png", "z", 1, ("x", "y"), L.PAD[:2], L.PAD[2:4], (ZR + L.PAD[4] - 0.001, ZR + L.PAD[4] + 0.001))

# Neutrals' brown enamel (no green) over a dark primer: lived-in - chips along the edges down to the primer
# and metal, moderate rust, more at the floor; dust on the roof
ENAMEL = dict(color=lin((92, 54, 32)), under=lin((66, 56, 48)), bare=lin((92, 90, 86)), seed=1.3, gloss=0.40,
              spec=0.30, chip=(0.55, 0.61), rust=(0.59, 0.67), rust_low=0.9, floor_z=0.0, dust=0.28, grime=0.85)
SMALL = dict(floor_z=ZR, rust_low=0.0, low_h=0.01)          # small things on the roof
KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "enamel": (MT.enamel, dict(ENAMEL, decal_items=PIN_SIDES, clean=[CLEAN1])),
    "frame": (MT.enamel, dict(ENAMEL, seed=1.9, chip=(0.52, 0.58))),
    "door": (MT.enamel, dict(ENAMEL, seed=1.6, decal_items=[PIN_DOOR, WEAR])),
    "hinge": (MT.enamel, dict(ENAMEL, seed=2.4, chip=(0.47, 0.54), metal=0.8)),
    # cast plinth and feet: black paint over cast iron, rust at the floor
    "iron": (MT.enamel, dict(color=lin((40, 36, 34)), under=lin((96, 58, 34)), bare=lin((70, 68, 64)), seed=2.2,
                             gloss=0.30, spec=0.25, chip=(0.55, 0.62), rust=(0.56, 0.64), rust_low=1.0, floor_z=0.0,
                             dust=0.3, grime=0.9)),
    "dark": ("flat", dict(color=lin((14, 12, 11)), gloss=0.2, spec=0.1)),
    # wheel and dial-handle bronze, brass of rosettes, nameplate and keyhole: patina in recesses, rubbed by hands
    "bronze": (MT.brass, dict(color=lin((100, 66, 30)), seed=3.1, gloss=0.40, spec=0.45, polish=0.8, tarnish=0.75,
                              dust=0.05, scale=3.0)),
    "brass": (MT.brass, dict(color=lin((136, 98, 44)), seed=3.5, gloss=0.42, spec=0.48, polish=0.6, tarnish=0.6,
                             dust=0.05, scale=3.0)),
    "dial": (MT.brass, dict(color=lin((146, 110, 56)), seed=3.7, gloss=0.42, spec=0.45, polish=0.4, tarnish=0.35,
                            dust=0.05, scale=3.0, decal_items=[DIAL_D])),
    "plate": (MT.brass, dict(color=lin((150, 114, 58)), seed=3.9, gloss=0.42, spec=0.45, polish=0.4, tarnish=0.45,
                             dust=0.05, scale=3.0, decal_items=[PLATE_D])),
    "tag": (MT.steel, dict(seed=4.4, tone=0.42, along="x", gloss=0.45, spec=0.5, dust=0.2, grime=0.3, scale=3.0)),
    # pad under the loupe: dark brown leather; board under the case: dark stained pine
    "pad": (MT.leather, dict(color=lin((92, 58, 36)), seed=5.1, scale=3.0, floor_z=ZR, low_h=0.003,
                             decal_items=[PAD_D])),
    "board": (MT.wood, dict(color=lin((104, 72, 46)), seed=5.5, along="x", floor_z=ZR, dust=0.25, grime=0.3,
                            knots=0.4)),
    # lamp: the shade is dark brown enamel, white inside ("off" / "work" - glows)
    "shade": (MT.enamel, dict(SMALL, color=lin((58, 42, 32)), under=lin((150, 146, 138)), bare=lin((120, 118, 112)),
                              seed=6.3, gloss=0.42, spec=0.32, chip=(0.62, 0.68), rust=(0.72, 0.80), dust=0.15,
                              grime=0.2, scale=4.0)),
    "shade_in": (MT.plastic, dict(color=lin((214, 208, 190)), gloss=0.5, spec=0.4, dust=0.15, grime=0.2, scale=4.0,
                                  floor_z=ZR, low_h=0.01)),
    "shade_in_on": ("flat", dict(color=lin((255, 238, 190)), gloss=0.5, spec=0.4)),
    "bulb": ("flat", dict(color=lin((200, 196, 182)), gloss=0.9, spec=0.7)),
    "bulb_on": ("flat", dict(color=lin((255, 246, 214)), gloss=0.9, spec=0.7)),
    "chrome": (MT.steel, dict(seed=6.1, tone=0.40, along="z", gloss=0.62, spec=0.78, floor_z=ZR, dust=0.25,
                              grime=0.3, scale=4.0, low_h=0.02)),
    "lamp_base": (MT.enamel, dict(SMALL, color=lin((44, 36, 30)), under=lin((70, 64, 58)), bare=lin((110, 106, 100)),
                                  seed=6.7, gloss=0.35, spec=0.3, chip=(0.58, 0.64), rust=(0.70, 0.78), dust=0.10,
                                  grime=0.25, scale=4.0)),
    "black": (MT.plastic, dict(color=lin((22, 21, 20)), gloss=0.35, spec=0.25, dust=0.2, grime=0.2, scale=4.0,
                               floor_z=ZR, low_h=0.01)),
    # cord in a cloth braid, dusty on the floor
    "cord": (MT.plastic, dict(color=lin((34, 28, 24)), gloss=0.12, spec=0.08, dust=0.3, grime=0.5, mottle=0.12,
                              scuff=(0.70, 0.80), scale=3.0)),
    # bolts: galvanized with rust; jar lids - golden lacquer on tin
    "bolts": (MT.enamel, dict(SMALL, color=lin((104, 102, 96)), under=lin((112, 62, 30)), bare=lin((140, 138, 132)),
                              seed=7.7, gloss=0.40, spec=0.45, chip=(0.48, 0.56), rust=(0.45, 0.55), dust=0.05,
                              grime=0.3, scale=6.0)),
    "lid": (MT.enamel, dict(SMALL, color=lin((176, 150, 86)), under=lin((150, 150, 146)), bare=lin((150, 150, 146)),
                            seed=8.1, gloss=0.55, spec=0.5, chip=(0.58, 0.64), rust=(0.66, 0.74), dust=0.10,
                            grime=0.3, scale=6.0)),
    # enamelled mug: white enamel, blue rim, chips down to black and rust
    "mug": (MT.enamel, dict(SMALL, color=lin((222, 218, 206)), under=lin((26, 26, 30)), bare=lin((26, 26, 30)),
                            seed=9.2, gloss=0.6, spec=0.4, chip=(0.57, 0.63), rust=(0.72, 0.80), dust=0.08,
                            grime=0.4, scale=6.0)),
    "mug_rim": (MT.enamel, dict(SMALL, color=lin((38, 52, 92)), under=lin((26, 26, 30)), bare=lin((26, 26, 30)),
                                seed=9.6, gloss=0.6, spec=0.4, chip=(0.52, 0.58), rust=(0.70, 0.80), dust=0.1,
                                grime=0.3, scale=6.0)),
    "tea": ("flat", dict(color=lin((70, 38, 18)), gloss=0.9, spec=0.6)),
    "alu": (MT.steel, dict(seed=9.9, tone=0.45, along="z", gloss=0.45, spec=0.5, floor_z=ZR, dust=0.1, grime=0.3,
                           scale=6.0, low_h=0.01)),
})

OBJ, NAME = "m18_lnr_pack_khabar", "ozr_lnr_pack_khabar"
# Work look: the lamp is ozl_lamp (in hiddenSelections), "work" is the _on_co atlas and the _on rvmat with
# glow. Bones: the code dial ozl_work (source ozl_work, wobble), the wheel ozl_wheel (source ozl_wheel,
# pose).
SEL_LAMP, SEL_DIAL, SEL_WHEEL = "ozl_lamp", "ozl_work", "ozl_wheel"
ON = dict(remap={"shade_in": "shade_in_on", "bulb": "bulb_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
DIAL_ANIM = ("ozl_work_dial", dict(type="rotation", source="ozl_work", selection=SEL_DIAL, axis="ozl_work_axis",
                                   memory=1, minValue=0.0, maxValue=1.0, angle0=0.0, angle1=2 * math.pi))
WHEEL_TURN = math.radians(60.0)
# In "work" the wheel turns by 60 degrees counter-clockwise. The axis is the memory points
# ozl_wheel_axis, from the door toward the person (-Y). The engine rotates a bone as a right-hand screw in
# DayZ axes (kexport.conv, determinant -1); in Blender axes that is a left-hand screw about the axis from
# the first point to the second: the axis looks at the person, a plus angle is clockwise for him, a minus
# one counter-clockwise (checked by check_wheel).
WHEEL_AXIS = [(0.0, YD, WHEEL_Z), (0.0, YD - 0.06, WHEEL_Z)]
WHEEL_ANIM = ("ozl_wheel_turn", dict(type="rotation", source="ozl_wheel", selection=SEL_WHEEL, axis="ozl_wheel_axis",
                                     memory=1, minValue=0.0, maxValue=1.0, angle0=0.0, angle1=-WHEEL_TURN))


def engine_turn(axis_pts, ang):
    """Rotation of a bone by angle ang as the engine will do it about the memory axis axis_pts: (point on
    the axis, Blender axis for Matrix.Rotation - a right-hand screw, angle). The Blender axis is opposite
    to the memory axis (from the second point to the first)."""
    a, b = Vector(axis_pts[0]), Vector(axis_pts[1])
    return a, a - b, ang


def check_wheel():
    """By numbers, like check_axes of the Storage boxes: in the "work" pose the engine rotation takes the
    top of the wheel to the left - counter-clockwise seen facing the door. If they do not match, the build
    fails."""
    c, ax, ang = engine_turn(WHEEL_AXIS, WHEEL_ANIM[1]["angle1"])
    q = c + Matrix.Rotation(ang, 3, ax) @ Vector((0.0, 0.0, WHEEL_R))
    assert q.x < c.x - 0.5 * WHEEL_R, "wheel turns clockwise, not counter-clockwise as in the preview"
    print("turns ok: wheel - counter-clockwise from the front, by %.0f degrees" % math.degrees(-ang))


check_wheel()
# "work" in the preview (rotation; the kit can only shift): the wheel is rotated by the engine rotation
# (engine_turn: the preview shows what will be in game). The dial is not: the preview draws the scale in
# place, not by part (in game the scale is baked into the atlas and moves with the dial)
POSE = {SEL_WHEEL: engine_turn(WHEEL_AXIS, WHEEL_ANIM[1]["angle1"])}
# module proxies: slots OZL_Tool1..3 are linked to them by the mod's CfgNonAIVehicles (Proxyozl_tool1..3)
PROXIES = [(r"\OpenZone_Research\models\proxies\ozl_tool%d" % (i + 1), m) for i, m in enumerate(MODS)]
# vanilla items: a vodka at the rear edge on the right, the spare "Krona" of the dosimeter and keys
KEYS = r"dz\gear\tools\ShippingContainerKeys"
DECOR = [
    kv.put("vodka", (0.300, 0.135, ZR), up=(0, 0, 1), fwd=(-0.35, -1.0, 0.0)),
    kv.put("battery9v", (-0.070, 0.035, ZR), **kv.flat(4)),
    kv.put(KEYS, (0.070, 0.045, ZR), **kv.flat(-28)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.62, 0.66, 0.62), clear=0.10, edge=0.14, smudge=0.12, streaks=0.03),
                 selections=(SEL_LAMP, SEL_DIAL, SEL_WHEEL), hidden=(SEL_LAMP,), states={"on": ON},
                 bones=((SEL_DIAL, ""), (SEL_WHEEL, "")), animations=(DIAL_ANIM, WHEEL_ANIM), proxies=PROXIES,
                 decor=DECOR, modules=[(o, n, m) for (o, n), m in zip(MOD_OBJ, MODS)],
                 sources={"ozl_work": dict(animPeriod=0.25), "ozl_wheel": dict(animPeriod=1.2)})
P = M.part
BOUNDS = {}


# =============================================================================
# Body, plinth, door
# =============================================================================
def build_body(spec):
    lod = spec["lod"]
    bd = P("body", "enamel")
    g.box(bd, X0, X1, Y0, Y1, ZB, ZR, **{0: dict(r=R_BODY, seg=4), 1: dict(r=R_BODY, seg=1)}.get(lod, {}))
    parts = [bd]
    # rebate: a dark gap around the door
    gp = P("door_gap", "dark")
    g.box(gp, DX0 - GAP, DX1 + GAP, Y0 - 0.0015, Y0 + 0.002, DZ0 - GAP, DZ1 + GAP)
    parts.append(gp)
    if lod < 2:
        # rebate frame: a bead with a rounded top around the gap
        fr = P("door_band", "frame")
        prof = BAND_PROF if lod == 0 else [BAND_PROF[0], BAND_PROF[3], BAND_PROF[-1]]
        G.frame_molding(fr, DCX, DCZ, DX1 - DX0 + 2 * GAP, DZ1 - DZ0 + 2 * GAP, 0.006, 3 if lod == 0 else 1, prof, Y0)
        parts.append(fr)
    return parts


def build_plinth(spec):
    """Cast plinth: a plate under the body (recessed 15 mm) on four turned feet, two bolts."""
    lod = spec["lod"]
    pl = P("plinth", "iron")
    x0, x1, y0, y1 = X0 + PL_IN, X1 - PL_IN, Y0 + PL_IN, Y1 - PL_IN
    if lod == 2:
        g.box(pl, x0, x1, y0, y1, 0.0, ZB)
        return [pl]
    g.box(pl, x0, x1, y0, y1, FOOT_H, ZB, **(dict(r=0.006, seg=2) if lod == 0 else {}))
    parts = [pl]
    prof = FOOT_PROF if lod == 0 else [FOOT_PROF[0], FOOT_PROF[3], FOOT_PROF[-1]]
    for i, (fx, fy) in enumerate(FEET):
        ft = P("foot%d" % i, "iron", uv_name="foot", uv_origin=(fx, fy, 0.0))
        G.lathe(ft, prof, 12 if lod == 0 else 6, (fx, fy, 0.0), cap0=True)
        parts.append(ft)
    if lod == 0:
        bt = P("plinth_bolts", "iron_bolt")
        for sx in (-1, 1):
            G.hexhead(bt, (sx * 0.31, y0, (FOOT_H + ZB) / 2), (0, -1, 0), 0.017, 0.007)
        parts.append(bt)
    return parts


def build_door(spec):
    """Door in the rebate: a plate with rounded edges, a moulding (a bead of semicircular section) along it."""
    lod = spec["lod"]
    dr = P("door", "door")
    g.box(dr, DX0, DX1, YD, Y0 + 0.002, DZ0, DZ1,
          **{0: dict(r=0.006, seg=2), 1: dict(r=0.004, seg=1)}.get(lod, {}))
    parts = [dr]
    if lod < 2:
        bd = P("door_bead", "bead")
        prof = BEAD_PROF if lod == 0 else [BEAD_PROF[0], BEAD_PROF[3], BEAD_PROF[-1]]
        G.frame_molding(bd, DCX, DCZ, DX1 - DX0 - 2 * L.MOLD, DZ1 - DZ0 - 2 * L.MOLD, 0.012, 3 if lod == 0 else 1,
                        prof, YD)
        parts.append(bd)
    return parts


def build_hinges(spec):
    """Two hinges on the left: a barrel of two halves (the lower on the body, the upper on the door) with a
    pin in the gap, cast brackets to the body face and to the door edge, brass caps, screws."""
    lod = spec["lod"]
    if lod == 2:
        return []
    n = 12 if lod == 0 else 8
    parts = []
    for i, hz in enumerate(HINGES):
        hg = P("hinge%d" % i, "hinge", uv_name="hinge", uv_origin=(0.0, 0.0, hz))
        c = (HX, HY, hz)
        G.lathe(hg, [(HR, -HH), (HR, -0.0015)], n, c, cap0=True, cap1=True)
        G.lathe(hg, [(HR, 0.0015), (HR, HH)], n, c, cap0=True, cap1=True)
        bev = dict(r=0.002, seg=1) if lod == 0 else {}
        g.box(hg, X0 + 0.027, HX, HY - 0.009, Y0 + 0.0005, hz - HH + 0.006, hz - 0.006, **bev)
        g.box(hg, HX, DX0 + 0.014, HY - 0.009, YD + 0.0005, hz + 0.006, hz + HH - 0.006, **bev)
        parts.append(hg)
        if lod == 0:
            fn = P("hinge_fin%d" % i, "brass", uv_name="hinge_fin", uv_origin=(0.0, 0.0, hz))
            G.lathe(fn, FIN_PROF, 10, (HX, HY, hz + HH), cap0=True)
            G.lathe(fn, FIN_PROF, 10, (HX, HY, hz - HH), axis=(0, 0, -1), cap0=True)
            parts.append(fn)
            pin = P("hinge_pin%d" % i, "tag", uv_name="hinge_pin", uv_origin=(0.0, 0.0, hz))
            G.rod(pin, (HX, HY, hz - 0.003), (HX, HY, hz + 0.003), 0.0095, 10, cap=False)
            parts.append(pin)
            sc = P("hinge_screws%d" % i, "hinge", uv_name="hinge_screws", uv_origin=(0.0, 0.0, hz))
            sl = P("hinge_slots%d" % i, "dark", uv_name="hinge_slots", uv_origin=(0.0, 0.0, hz))
            for zz in (hz - HH * 0.72, hz - HH * 0.28):
                G.slotted(sc, sl, (X0 + 0.0405, HY - 0.009, zz), (0, -1, 0), r=0.0048, h=0.002, ang=0.4 + zz * 9)
            parts += [sc, sl]
    return parts


def build_plate(spec):
    """Blank brass nameplate on four rivets (inscriptions rubbed off - decal decal_plate)."""
    lod = spec["lod"]
    pt = P("plate", "plate")
    poly = G.rrect2(0.0, PLATE_Z, PLATE[0], PLATE[1], 0.008, 3 if lod == 0 else 1)
    if lod == 2:
        g.prism(pt, poly, (0, 2), YD + 0.0005, YD - 0.003)
        return [pt]
    G.bprism(pt, poly, (0, 2), YD + 0.0005, YD - 0.003, 0.0008 if lod == 0 else 0.0)
    parts = [pt]
    if lod == 0:
        rv = P("plate_rivets", "brass")
        for sx in (-1, 1):
            for sz in (-1, 1):
                G.screw(rv, (sx * 0.066, YD - 0.003, PLATE_Z + sz * 0.0255), (0, -1, 0), r=0.0034, h=0.0016, sides=6)
        parts.append(rv)
    return parts


def build_dial(spec):
    """Combination lock: a brass rosette with a mark (on the door) and a disc with a scale and a knurled
    handle - bone ozl_work."""
    lod = spec["lod"]
    n = {0: 32, 1: 14, 2: 8}[lod]
    c = (0.0, YD, DIAL_Z)
    ax = (0, -1, 0)
    rs = P("dial_rose", "brass")
    rose = [(ROSE_R, 0.0), (ROSE_R, 0.0025), (ROSE_R - 0.003, 0.0055), (ROSE_R - 0.009, 0.0068), (0.0715, 0.0068),
            (0.0700, 0.0040)]
    G.lathe(rs, rose if lod == 0 else [rose[0], rose[2], rose[4], rose[5]], n, c, ax)
    parts = [rs]
    if lod < 2:
        # mark at the top: a triangle with the point toward the disc
        poly = [(-0.005, DIAL_Z + ROSE_R - 0.0035), (0.005, DIAL_Z + ROSE_R - 0.0035), (0.0, DIAL_Z + 0.0705)]
        g.prism(rs, poly, (0, 2), YD - 0.0066, YD - 0.0084)
    dl = P("dial", "dial", group=SEL_DIAL)
    disc = [(0.066, 0.002), (0.066, 0.015), (0.0645, 0.0185), (0.0615, 0.020), (0.0, 0.020)]
    G.lathe(dl, disc if lod == 0 else [disc[0], disc[1], disc[-1]], n, c, ax)
    parts.append(dl)
    kn = P("dial_knob", "bronze", group=SEL_DIAL)
    if lod == 0:
        G.star_prism(kn, c, ax, 0.029, 0.0016, 12, 0.020, 0.042, cap1=False)
        G.lathe(kn, [(0.029, 0.042), (0.0270, 0.0475), (0.019, 0.0515), (0.0, 0.053)], 24, c, ax)
    else:
        G.lathe(kn, [(0.029, 0.020), (0.029, 0.042), (0.0, 0.050)], 8 if lod == 1 else 6, c, ax)
    parts.append(kn)
    return parts


def build_wheel(spec):
    """Wheel: a brass rosette on four screws (on the door); spindle, cast hub with a nut, four oval spokes
    bent toward the door and a round-section rim - bone ozl_wheel."""
    lod = spec["lod"]
    c = Vector((0.0, YD, WHEEL_Z))
    ax = Vector((0.0, -1.0, 0.0))
    parts = []
    rs = P("wheel_rose", "brass")
    rose = [(0.052, 0.0), (0.052, 0.003), (0.047, 0.0058), (0.036, 0.0075), (0.020, 0.0085), (0.015, 0.0085)]
    G.lathe(rs, rose if lod == 0 else [rose[0], rose[2], rose[4]], {0: 24, 1: 12, 2: 8}[lod], c, ax)
    parts.append(rs)
    if lod == 0:
        sc = P("wheel_screws", "brass")
        sl = P("wheel_slots", "dark")
        for k in range(4):
            a = k * math.pi / 2
            G.slotted(sc, sl, c + Vector((0.043 * math.cos(a), 0.0, 0.043 * math.sin(a))) + ax * 0.0052, ax,
                      r=0.0042, h=0.0018, ang=0.7 * k + 0.3)
        parts += [sc, sl]
    wh = P("wheel", "bronze", group=SEL_WHEEL)
    hub = [(0.016, 0.014), (0.025, 0.017), (0.030, 0.024), (0.0305, 0.031), (0.028, 0.038), (0.021, 0.0445),
           (0.014, 0.047)]
    if lod == 0:
        G.lathe(wh, [(0.011, 0.007), (0.011, 0.016)], 8, c, ax)
        G.lathe(wh, hub, 16, c, ax, cap1=True)
        G.hexhead(wh, c + ax * 0.047, ax, 0.020, 0.008)
    else:
        G.lathe(wh, [(0.016, 0.008), (0.030, 0.026), (0.016, 0.047)], 8 if lod == 1 else 6, c, ax, cap1=True)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        d = Vector((math.cos(a), 0.0, math.sin(a)))
        pts = [c + d * 0.022 + ax * 0.030, c + d * 0.058 + ax * 0.046, c + d * 0.090 + ax * 0.059,
               c + d * (WHEEL_R - 0.004) + ax * 0.065]
        if lod == 0:
            pts = G.spline(pts, 2)
            m = len(pts) - 1
            radii = [(0.0115 - 0.0035 * i / m, 0.0076 - 0.0016 * i / m) for i in range(m + 1)]
            G.oval_tube(wh, pts, radii, 6, ax, caps=False)
        else:
            G.oval_tube(wh, [pts[0], pts[-1]], [(0.010, 0.007)] * 2, 4, ax, caps=False)
    G.torus(wh, c + ax * 0.065, ax, WHEEL_R, WHEEL_T, {0: 40, 1: 14, 2: 8}[lod], {0: 10, 1: 5, 2: 3}[lod])
    parts.append(wh)
    return parts


def shield(cx, cz, w, h, k):
    """Keyhole cover plate: a semicircle at the top, the sides converging downward to a rounded nose."""
    r = w / 2
    top = cz + h / 2 - r
    pts = [(cx + r * math.cos(math.pi * i / k), top + r * math.sin(math.pi * i / k)) for i in range(k + 1)]
    pts += [(cx - r, cz - h * 0.10), (cx - r * 0.62, cz - h * 0.36), (cx - r * 0.18, cz - h * 0.49),
            (cx + r * 0.18, cz - h * 0.49), (cx + r * 0.62, cz - h * 0.36), (cx + r, cz - h * 0.10)]
    return pts


def build_keyhole(spec):
    """Keyhole cover: a brass plate, a dark keyhole, a shutter on a pin swung aside, two screws."""
    lod = spec["lod"]
    kp = P("keyplate", "brass")
    poly = shield(0.0, KEY_Z, 0.052, 0.098, 6 if lod == 0 else 3)
    if lod == 0:
        G.bprism(kp, poly, (0, 2), YD + 0.0005, YD - 0.0035, 0.001)
    else:
        g.prism(kp, poly, (0, 2), YD + 0.0005, YD - 0.0035)
    parts = [kp]
    if lod == 2:
        return parts
    kh = P("keyhole", "dark")
    g.cyl(kh, (0.0, YD - 0.0037, KEY_Z + 0.006), "y", 0.0062, 0.0006, 12 if lod == 0 else 6)
    g.box(kh, -0.003, 0.003, YD - 0.0040, YD - 0.0034, KEY_Z - 0.020, KEY_Z + 0.006)
    parts.append(kh)
    if lod == 0:
        # shutter: a drop on a pin above the keyhole, swung aside by 70 degrees - the keyhole is open
        piv = (0.0, KEY_Z + 0.025)
        a = math.radians(-70.0)
        loc = [(0.0105 * math.cos(math.pi * i / 6), 0.0105 * math.sin(math.pi * i / 6)) for i in range(7)]
        loc += [(-0.0105, -0.012), (-0.004, -0.030), (0.004, -0.030), (0.0105, -0.012)]
        rot = [(piv[0] + x * math.cos(a) - z * math.sin(a), piv[1] + x * math.sin(a) + z * math.cos(a)) for x, z in loc]
        g.prism(kp, rot, (0, 2), YD - 0.0036, YD - 0.0052)
        G.screw(kp, (0.0, YD - 0.0052, piv[1]), (0, -1, 0), r=0.0032, h=0.0018, sides=8)
        sl = P("keyplate_slots", "dark")
        G.slotted(kp, sl, (0.0, YD - 0.0035, KEY_Z - 0.036), (0, -1, 0), r=0.0038, h=0.0016, ang=1.1)
        parts.append(sl)
    return parts


def build_tag(spec):
    """Blank inventory tag on the right side on two screws."""
    if spec["lod"] != 0:
        return []
    tg = P("inv_tag", "tag")
    g.prism(tg, G.rrect2(0.0, 1.1625, 0.08, 0.045, 0.004, 1), (1, 2), X1 - 0.0005, X1 + 0.0012)
    for yy in (-0.032, 0.032):
        G.screw(tg, (X1 + 0.0012, yy, 1.1625), (1, 0, 0), r=0.003, h=0.0012, sides=6)
    return [tg]


# =============================================================================
# Roof: module places, lamp, jars, mug
# =============================================================================
def build_slots(spec):
    """Slot 2 - a leather pad under the loupe (stitching, bell trace - a decal); slot 3 - a board under the
    lead case; slot 1 - only a clean spot on the roof (material enamel, clean)."""
    lod = spec["lod"]
    if lod == 2:
        return []
    cx, cy, w, d, t = L.PAD
    pd = P("slot2_pad", "pad")
    poly = G.rrect2(cx, cy, w, d, 0.012, 3 if lod == 0 else 1)
    if lod == 0:
        G.bprism(pd, poly, (0, 1), ZR, ZR + t, 0.0012)
    else:
        g.prism(pd, poly, (0, 1), ZR, ZR + t)
    bx, by, bw, bd, bt = L.BOARD
    bo = P("slot3_board", "board")
    g.box(bo, bx - bw / 2, bx + bw / 2, by - bd / 2, by + bd / 2, ZR, ZR + bt, **(dict(r=0.003, seg=2) if lod == 0 else {}))
    return [pd, bo]


def build_lamp(spec):
    """Desk lamp: a cast base with a switch, a chromed stand, a joint with a wing nut, an elbow to the shade;
    a conical shade with a rolled edge and a socket, the white inside and the bulb - ozl_lamp; the cord is a
    smooth curve from the base behind the roof, down the back, along the floor to the plug."""
    lod = spec["lod"]
    cx, cy = LAMP_C
    n = {0: 20, 1: 10, 2: 6}[lod]
    parts = []
    bs = P("lamp_base", "lamp_base")
    base = [(0.074, 0.0), (0.0752, 0.004), (0.069, 0.013), (0.055, 0.021), (0.036, 0.0265), (0.016, 0.029)]
    G.lathe(bs, base if lod == 0 else [base[0], base[2], base[4], base[-1]], n, (cx, cy, ZR), cap1=True)
    parts.append(bs)
    st = P("lamp_stem", "chrome")
    sock = APEX - SHADE_DIR * 0.040
    if lod == 0:
        G.lathe(st, [(0.0135, 0.028), (0.0135, 0.036), (0.010, 0.040), (0.0072, 0.042)], 12, (cx, cy, ZR))
        G.rod(st, (cx, cy, ZR + 0.03), JOINT, 0.0068, 10)
        G.rod(st, JOINT, sock, 0.0058, 10)
    else:
        G.rod(st, (cx, cy, ZR + 0.02), JOINT, 0.008, 4 if lod == 2 else 6)
        G.rod(st, JOINT, sock, 0.007, 4 if lod == 2 else 6)
    parts.append(st)
    if lod == 0:
        jt = P("lamp_joint", "black")
        G.lathe(jt, [(0.0115, -0.016), (0.0115, 0.016)], 10, JOINT, (1, 0, 0), cap0=True, cap1=True)
        # wing nut on the joint axis
        G.lathe(jt, [(0.0065, 0.016), (0.0060, 0.022), (0.0040, 0.025)], 6, JOINT, (1, 0, 0), cap1=True)
        for s in (-1, 1):
            g.box(jt, JOINT.x + 0.017, JOINT.x + 0.0215, JOINT.y - 0.0015, JOINT.y + 0.0015, JOINT.z + s * 0.004,
                  JOINT.z + s * 0.016)
        # switch on the base: a block and a lever
        g.box(jt, cx + 0.010, cx + 0.030, cy - 0.058, cy - 0.038, ZR + 0.012, ZR + 0.026, **dict(r=0.002, seg=1))
        G.rod(jt, (cx + 0.020, cy - 0.048, ZR + 0.025), (cx + 0.020, cy - 0.056, ZR + 0.037), 0.0022, 5)
        parts.append(jt)
    # shade along SHADE_DIR from the apex: a socket neck at the back, a cone, a rolled flare edge
    shade = [(0.0, -0.044), (0.0160, -0.040), (0.0172, -0.032), (0.0172, -0.010), (0.0235, 0.0), (0.031, 0.012),
             (0.046, 0.040), (0.062, 0.073), (0.077, 0.104), (0.0880, 0.1245), (0.0895, 0.1275), (0.0860, 0.1310)]
    inner = [(0.0855, 0.1300), (0.0805, 0.116), (0.0605, 0.074), (0.0365, 0.026), (0.0215, 0.002), (0.0, 0.0)]
    if lod == 1:
        shade = [shade[i] for i in (0, 2, 3, 4, 7, 10, 11)]
        inner = [inner[i] for i in (0, 2, 4, 5)]
    elif lod == 2:
        shade = [(0.0, -0.040), (0.018, -0.010), (0.088, 0.128)]
        inner = [(0.086, 0.128), (0.0, 0.0)]
    sh = P("lamp_shade", "shade")
    G.lathe(sh, shade, n, APEX, SHADE_DIR)
    parts.append(sh)
    si = P("lamp_shade_in", "shade_in", group=SEL_LAMP)
    G.lathe(si, inner, n, APEX, SHADE_DIR)
    parts.append(si)
    if lod < 2:
        bl = P("lamp_bulb", "bulb", group=SEL_LAMP)
        bulb = [(0.0105, 0.016), (0.0105, 0.030), (0.020, 0.046), (0.0295, 0.068), (0.0275, 0.088), (0.016, 0.100),
                (0.0, 0.1045)]
        G.lathe(bl, bulb if lod == 0 else [bulb[0], bulb[3], bulb[-1]], 12 if lod == 0 else 6, APEX, SHADE_DIR)
        parts.append(bl)
    if lod == 0:
        sk = P("lamp_socket", "black")
        G.lathe(sk, [(0.0178, 0.0), (0.0178, 0.017), (0.0125, 0.019)], 12, APEX, SHADE_DIR, cap1=True)
        parts.append(sk)
        # cord: from the base backward, over the rear roof edge, down the back, along the floor to the plug
        cd = P("lamp_cord", "cord")
        ctrl = [(cx + 0.010, cy + 0.068, ZR + 0.0045), (cx + 0.022, Y1 - 0.016, ZR + 0.0034),
                (cx + 0.030, Y1 + 0.0005, ZR + 0.0010), (cx + 0.035, Y1 + 0.0080, ZR - 0.012),
                (cx + 0.040, Y1 + 0.0062, ZR - 0.07), (cx + 0.050, Y1 + 0.0058, 0.95), (cx + 0.038, Y1 + 0.0060, 0.45),
                (cx + 0.052, Y1 + 0.0080, 0.14), (cx + 0.085, Y1 + 0.040, 0.012), (cx + 0.135, Y1 + 0.100, 0.0034),
                (cx + 0.200, Y1 + 0.138, 0.0050), (cx + 0.240, Y1 + 0.148, 0.0168)]
        pts = G.spline(ctrl, 3)
        g.pipe(cd, pts, 0.0032, 5)
        parts.append(cd)
        # plug: a bakelite body and two pins (19 mm apart), lies on the floor
        pg = P("lamp_plug", "black")
        e = Vector(pts[-1])
        dv = (e - Vector(pts[-3]))
        dv = Vector((dv.x, dv.y, 0.0)).normalized()
        G.lathe(pg, [(0.0036, -0.002), (0.0085, 0.004), (0.0155, 0.014), (0.0168, 0.022), (0.0168, 0.040),
                     (0.0150, 0.043)], 12, e, dv, cap1=True)
        side = dv.cross(Vector((0.0, 0.0, 1.0))).normalized()
        pins = P("lamp_plug_pins", "chrome")
        for s in (-1, 1):
            q = e + dv * 0.043 + side * (s * 0.0095)
            G.rod(pins, q, q + dv * 0.019, 0.002, 6)
        parts += [pg, pins]
    return parts


def bolt_heap(i, jx, jy, fill, sides, lod):
    """Bolts in a jar: a heap (a cylinder with an uneven top), heads
    on top and at the wall (visible through the glass)."""
    bt = P("jar%d_bolts" % i, "bolts")
    R = 0.038
    G.lathe(bt, [(R, 0.004), (R, fill - 0.006)], sides, (jx, jy, ZR), phase=0.0)

    def h(r, a):
        s = r / R
        return fill - 0.006 + 0.008 * (1 - s * s) + 0.012 * math.sin(3 * a + 1.7 * i) * s * (1 - s) + \
            0.002 * math.cos(5 * a + i) * (1 - s)
    G.disc_grid(bt, (jx, jy, ZR), [R, 0.022, 0.0] if lod == 0 else [R, 0.0], sides, h)
    if lod == 0:
        rnd = [(0.6 + 2.39 * k + i, 0.004 + 0.024 * ((k * 0.618 + i * 0.3) % 1.0)) for k in range(5)]
        for a, r in rnd:
            tilt = Vector((0.45 * math.cos(a * 1.7), 0.45 * math.sin(a * 1.3), 1.0)).normalized()
            G.hexhead(bt, (jx + r * math.cos(a), jy + r * math.sin(a), ZR + h(r, a) - 0.002), tilt, 0.013, 0.0055)
        for k in range(4):
            a = 1.6 * k + 0.4 + i
            z = 0.014 + (fill - 0.03) * ((k * 0.37 + 0.2 * i) % 1.0)
            n = Vector((math.cos(a), math.sin(a), 0.25 * math.sin(3 * a))).normalized()
            G.hexhead(bt, (jx + (R - 0.001) * math.cos(a), jy + (R - 0.001) * math.sin(a), ZR + z), n, 0.013, 0.0038)
    return bt


def build_jars(spec):
    """0.5 l jars (dia. 90 x 130) with bolts: glass with a neck and thread (section glass), a heap of bolts,
    a screw lid; the open jar's lid lies beside it upside down. A bolt and a nut on the roof."""
    lod = spec["lod"]
    if lod == 2:
        return []
    sides = 14 if lod == 0 else 8
    parts = []
    outer = [(0.036, 0.0), (0.0435, 0.005), (0.045, 0.016), (0.045, 0.098), (0.0365, 0.1135), (0.0360, 0.118),
             (0.0378, 0.1205), (0.0360, 0.124), (0.0360, 0.130)]
    inner = [(0.0338, 0.130), (0.0338, 0.1135), (0.0425, 0.098), (0.0425, 0.010), (0.0, 0.004)]
    for i, ((jx, jy), fill, closed) in enumerate(JARS):
        o = (jx, jy, ZR)
        gl = P("jar%d_glass" % i, "glass_jar", section="glass")
        G.lathe(gl, outer if lod == 0 else [outer[0], outer[2], outer[3], outer[4], outer[-1]], sides, o, cap0=True)
        if lod == 0 and not closed:
            # the open jar's neck is visible: the glass thickness - an edge and an inner wall
            G.lathe(gl, [(0.036, 0.130), (0.0338, 0.130)], sides, o)
            G.lathe(gl, inner, sides, o)
        parts.append(gl)
        parts.append(bolt_heap(i, jx, jy, fill, sides, lod))
        ld = P("jar%d_lid" % i, "lid")
        if closed:
            G.lathe(ld, [(0.0386, 0.1175), (0.0396, 0.1190), (0.0396, 0.1310), (0.033, 0.1335), (0.0, 0.1335)], sides, o)
        else:
            lx, ly = LID_LOOSE
            G.lathe(ld, [(0.0, 0.0), (0.033, 0.0), (0.0396, 0.0025), (0.0396, 0.0145), (0.0384, 0.0158),
                         (0.0372, 0.0150), (0.0372, 0.0030), (0.0, 0.0030)], sides, (lx, ly, ZR))
        parts.append(ld)
    if lod == 0:
        lb = P("loose_bolts", "bolts")
        (bx, by), deg = LOOSE_BOLT
        d = Vector((math.cos(math.radians(deg)), math.sin(math.radians(deg)), 0.0))
        hc = Vector((bx, by, ZR + 0.0065))
        G.hexhead(lb, hc, -d, 0.013, 0.0055, chamfer=False)
        G.lathe(lb, [(0.0042, 0.0), (0.0042, 0.044), (0.0034, 0.046)], 8, hc, d + Vector((0.0, 0.0, -0.05)), cap1=True)
        nx, ny = LOOSE_NUT
        G.hexhead(lb, (nx, ny, ZR), (0, 0, 1), 0.013, 0.0065)
        hole = P("loose_nut_hole", "dark")
        g.cyl(hole, (nx, ny, ZR + 0.0066), "z", 0.0040, 0.0004, 8)
        parts += [lb, hole]
    return parts


def build_mug(spec):
    """Enamelled mug (dia. 82 x 87): white, a blue rim with a rolled edge, a strap handle, tea, an aluminium
    spoon leaning on the rim."""
    lod = spec["lod"]
    if lod == 2:
        return []
    sides = 16 if lod == 0 else 8
    mx, my = MUG_C
    o = (mx, my, ZR)
    mg = P("mug", "mug")
    outer = [(0.0, 0.0), (0.034, 0.0), (0.0392, 0.004), (0.0400, 0.012), (0.0412, 0.080)]
    G.lathe(mg, outer if lod == 0 else [outer[0], outer[1], outer[3], outer[-1]], sides, o)
    rim = P("mug_rim", "mug_rim")
    rp = [(0.0412, 0.080), (0.0419, 0.0850), (0.0402, 0.0870), (0.0390, 0.083)]
    G.lathe(rim, rp if lod == 0 else [rp[0], rp[1], rp[-1]], sides, o)
    G.lathe(mg, [(0.0390, 0.083), (0.0390, 0.062)], sides, o)
    tea = P("mug_tea", "tea")
    G.lathe(tea, [(0.0390, 0.062), (0.0, 0.062)], sides, o)
    # strap handle on the right: wider along the mug axis, thin across
    hp = [(0.0395, 0.071), (0.056, 0.0735), (0.0665, 0.061), (0.0665, 0.036), (0.0535, 0.0225), (0.0395, 0.021)]
    pts = [(mx + x, my, ZR + z) for x, z in hp]
    if lod == 0:
        pts = G.spline(pts, 2)
        G.oval_tube(mg, pts, [(0.0021, 0.0064)] * len(pts), 6, (0, 1, 0))
    else:
        G.oval_tube(mg, pts[::2] + [pts[-1]], [(0.003, 0.006)] * 4, 4, (0, 1, 0))
    parts = [mg, rim, tea]
    if lod == 0:
        # spoon: a strip handle, a wider end; the bottom is in the tea
        sp = P("mug_spoon", "alu")
        b = Vector((mx - 0.010, my + 0.008, ZR + 0.058))
        touch = Vector((mx - 0.0272, my + 0.0272, ZR + 0.0890))
        d = (touch - b).normalized()
        pts = [b + d * (0.125 * k / 6) for k in range(7)]
        radii = [(0.0040 + 0.0016 * (k / 6) ** 2, 0.0011) for k in range(7)]
        # flat to the tilt plane: the thin side is in the vertical plane of the spoon
        G.oval_tube(sp, pts, radii, 6, d.cross(Vector((d.y, -d.x, 0.0))))
        parts.append(sp)
    return parts


def build_lod(spec):
    parts = build_body(spec) + build_plinth(spec) + build_door(spec) + build_hinges(spec) + build_plate(spec)
    parts += build_dial(spec) + build_wheel(spec) + build_keyhole(spec) + build_tag(spec)
    parts += build_slots(spec) + build_lamp(spec) + build_jars(spec) + build_mug(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        check_layout()
    return parts


def check_layout():
    """Things on the roof do not intersect (extents in plan and height): modules by their near LODs,
    vanilla ones by kv.corners, own ones by their sizes."""
    boxes = []
    for (x, y, z), (a0, a1, b0, b1, h), (o, _) in zip(MODS, MOD_BOX, MOD_OBJ):
        boxes.append((o, x + a0, x + a1, y + b0, y + b1, z, z + h))
    for d in DECOR:
        q = kv.corners(d[5], d[1], d[2], d[3])
        boxes.append((str(d[5]).split("\\")[-1], min(p[0] for p in q), max(p[0] for p in q), min(p[1] for p in q),
                      max(p[1] for p in q), min(p[2] for p in q), max(p[2] for p in q)))
    for nm, (x, y), r, h in [("lamp_base", LAMP_C, 0.0752, 0.04), ("jar0", JARS[0][0], JAR_R, 0.134),
                             ("jar1", JARS[1][0], JAR_R, 0.134), ("lid", LID_LOOSE, 0.0396, 0.016),
                             ("nut", LOOSE_NUT, 0.0075, 0.0065)]:
        boxes.append((nm, x - r, x + r, y - r, y + r, ZR, ZR + h))
    boxes.append(("mug", MUG_C[0] - MUG_R, MUG_C[0] + 0.069, MUG_C[1] - MUG_R, MUG_C[1] + MUG_R, ZR, ZR + MUG_H))
    (bx, by), deg = LOOSE_BOLT
    ex, ey = bx + 0.05 * math.cos(math.radians(deg)), by + 0.05 * math.sin(math.radians(deg))
    boxes.append(("bolt", min(bx, ex) - 0.008, max(bx, ex) + 0.008, min(by, ey) - 0.008, max(by, ey) + 0.008, ZR, ZR + 0.013))
    bad = 0
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if a[1] < b[2] and b[1] < a[2] and a[3] < b[4] and b[3] < a[4] and a[5] < b[6] and b[5] < a[6]:
                print("layout: %s overlaps %s" % (a[0], b[0]))
                bad += 1
    flat = (X0 + R_BODY, X1 - R_BODY, Y0 + R_BODY, Y1 - R_BODY)
    for b in boxes:
        if b[1] < flat[0] or b[2] > flat[1] or b[3] < flat[2] or b[4] > flat[3]:
            print("layout: %s leaves the flat roof (%.3f..%.3f, %.3f..%.3f)" % (b[0], b[1], b[2], b[3], b[4]))
    print("layout: %d overlaps" % bad)


def collision():
    """One convex piece - the body with the plinth and the wheel; the roof props are small, without collision."""
    metal = kx.PEN + r"\metalplate.rvmat"
    body = kx.box_pts(X0, X1, WHEEL_Y - WHEEL_T, Y1, 0.0, ZR)
    comps = [(body, metal)]
    memory = {
        "invView": [(0.0, -2.6, 1.3)],
        "ce_center": [(0.0, 0.0, 0.75)],
        "ce_radius": [(1.0, 0.0, 0.75)],
        "ozl_work_axis": [(0.0, YD, DIAL_Z), (0.0, YD - 0.06, DIAL_Z)],
        "ozl_wheel_axis": WHEEL_AXIS,                    # toward the person (the angle sign is in WHEEL_ANIM)
    }
    for i, m in enumerate(MODS):
        memory["module_%d" % (i + 1)] = [m]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 150.0, memory, bbox


# "work" look preview: the bones are turned as in the middle of the loop (the kit shifts groups but does
# not rotate - the rotation is here, only in the frames, like the M09 needle)
_place_look = krender.place_look


def _place_look_posed(parts, kind_table, origin, remap=None, **kw):
    obs = _place_look(parts, kind_table, origin, remap=remap, **kw)
    if remap:
        for p, ob in zip(parts, obs):
            if p.group in POSE:
                c, ax, ang = POSE[p.group]
                ob.matrix_world = Matrix.Translation(c) @ Matrix.Rotation(ang, 4, ax) @ \
                    Matrix.Translation(-c) @ ob.matrix_world
    return obs


krender.place_look = _place_look_posed

# the first ones are for the --look preview: overview, the roof with the modules in place (also empty), the
# door close up, the lamp over the loupe; the "work" looks are the first three
SHOTS = [
    ("front", (-1.25, -2.9, 1.65), (0.0, 0.0, 0.82), 30),
    ("roof", (0.40, -1.10, 2.20), (0.0, -0.01, ZR + 0.07), 32),
    ("door", (-0.42, -1.12, 1.10), (0.0, YD, 0.86), 34),
    ("lamp", (-0.88, -0.72, 1.95), (-0.17, -0.02, ZR + 0.14), 36),
    ("right", (1.9, -1.3, 1.5), (0.0, 0.0, 0.8), 30),
    ("back", (1.3, 2.4, 1.8), (0.0, 0.0, 0.85), 30),
    ("plinth", (-0.85, -1.15, 0.42), (0.0, -0.05, 0.16), 34),
]

M.look_shots = (4, 3)
M.run(build_lod, collision, SHOTS, row_step=1.2, row_shot=((1.2, -5.0, 1.8), (1.2, 0, 0.85)))
