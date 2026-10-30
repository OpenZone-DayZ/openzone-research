"""M79 - radio scanner (OZL_Tool_RadioScanner): a Trail line module (packers M15 and M20), a portable
2x2 item. It sits in the OZL_Tool2 slot (slot 2 of the line) and shows on the machine shelf
through the module_N proxy. A late-80s desktop scanning receiver of the AOR AR3000A type: a case
with an LCD display, a keypad and a dial, a telescopic antenna at the back. Listening to the air
by a trail record: an earphone is plugged into the jack, on the roof lie a tape with frequencies
and a pen.

    blender --background --python build_m79.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py (system Python) before the first build: the bezel and keypad print, the LCD off
and 12 work frames, the frequency tape, the rear panel. Layout: m79_layout.py.

Size: about 0.14 x 0.08 x 0.20 m, black metal; the module pad is about 0.2 x 0.2 m at the base and
up to about 0.25 m high.

Reference data:
- AOR AR3000A: 138 x 80 x 200 mm without protrusions, 1.2 kg; 12-14 V DC power (up to 300 mA);
  antenna 50 ohm on a BNC; RS-232C on a DB-25 (female); external speaker on a 3.5 mm mini jack.
  One source gives a depth of 120 mm, which disagrees with the others and with the photos (the
  roof is clearly deeper than wide), so 200 is used.
- Face layout from nearly front-on photos (m79_layout.py): a left column with the power button,
  squelch and volume knobs and the headphone jack; at the right a nameplate, an LCD with two
  buttons, a 4 x 5 keypad and two keys "down / up", a 25 mm dial at the lower right.
- Colour: case and bezel dark grey (one photo shows a light grey variant), the keypad is a dark
  satin plate with orange print, the keys are black with a ribbed face. The display has a
  yellow-green backlight in both photos, not amber - the model follows the instrument.
- The cover is a U-shaped sheet: the roof bends into the sides with a radius of about 6 mm, the
  lower corners are almost sharp; the rear panel is held by four screws.
- Antenna: telescopic on a BNC with a hinge, sections with crimped collars. It is extended to
  0.19 m and tilted back by 9 degrees so that the module does not exceed 0.25 m of height (the
  ~0.3 m of the item card would raise it to 0.36 m).
- The 12 V supply is a plug-in mains adapter (about 56 x 40 x 34 mm, a body of two halves with a
  seam, a Euro plug of 2 x diameter 4 with insulated pin bases) lying behind the receiver, its cord
  in the power jack. The earphone is a single "drop" type with a mini jack in the face socket,
  lying on the left, mesh up.
Everything together is about 0.17 x 0.29 x 0.25 m (with the earphone and adapter); it fits the
module_N place of M15 (shelf 0.30, place 0.125 m from the edge) and of M20 (0.144 to the edge,
0.177 to the rolls at the back).

Condition (no faction colour): used but intact, worn paint on the edges. Markings: display digits
and the S-meter scale, orange keypad digits, tick scales by the knobs, a blank nameplate,
frequencies in marker on the tape, icons by the connectors and a numbered label on the rear panel.
Details: the rounded cover, bezel seams, rear panel screws, knobs, dial, plugs and earphone are
solids of revolution with chamfers and ribs; ribbed key faces, antenna collars, cords as smooth
curves. A vanilla DayZ pen (Pen) is a proxy on the roof by the tape.

Work look: the display is a part with its own texture (section lcd, selection ozl_screen). Off is
blanked glass; work is 12 frames of 0.15 s (OZL_WorkFx frames, m79_layout.LCD_FRAMES): the
receiver listens to 145.5250, the S-meter dances, then a search runs over the bank channels. The
instrument has no moving parts and no separate lamp - the display backlight glows.
LODs: near and mid (no feet, screws, antenna collars, tick marks on the knobs, the dial dimple,
DB-25 standoffs, the antenna ball, the adapter label; solids of revolution and cords are
sparser), no far one.

Blender axes: X is width, Y is depth (the front faces -Y), Z is up. The instrument is built in the
axes of m79_layout.py and shifted by (OX, OY): the origin is the middle of the pad at the base,
so the module lands on the module_N proxy point (autocenter = 0 in Geometry).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import bmesh  # noqa: E402
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import kvanilla as kv  # noqa: E402
import m79_layout as L  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m ------------------------------------------------------------------------------
OX, OY = 0.015, 0.010           # instrument shift: the earphone on the left and the adapter at the back balance each other
FY = L.BEZ_Y[0]                 # face plane
KP_Y = FY + L.KEYPAD_DEPTH      # bottom of the keypad recess
LCD_Y = FY + L.LCD_DEPTH        # bottom of the display window
TOP = L.CASE_Z[1]
CASE_R = (0.0015, 0.0060)       # cover rounding: bottom, roof
# antenna: hinge behind the BNC plug, the axis tilted back and a bit sideways; stages (s0, s1, r,
# part)
KNUCKLE_Y = L.REAR_Y + 0.0235
ANT_D = Vector((0.04, 0.16, 1.0)).normalized()
ANT = [(0.000, 0.012, 0.0040, "ant_collar"), (0.012, 0.082, 0.0033, "ant_tube1"),
       (0.082, 0.124, 0.0027, "ant_tube2"), (0.124, 0.158, 0.0021, "ant_tube3"),
       (0.158, 0.186, 0.0016, "ant_tube4")]
ANT_BALL_S, ANT_BALL_R = 0.189, 0.0028
# power adapter behind the receiver: (x0, x1, y0, y1, h), the plug points to -X; the seam of the
# body halves is at ADP_SEAM_Z
ADP = (-0.060, -0.004, 0.112, 0.152, 0.034)
ADP_PIN_Z, ADP_PIN_DY = 0.017, 0.0095
ADP_R, ADP_SEAM_Z = 0.0045, 0.023
EAR = (-0.090, -0.053)          # earphone, a "drop" type
EAR_R, EAR_H = 0.0080, 0.0060
CORD_R, EAR_CORD_R = 0.0018, 0.0011
# rear panel on four screws at the corners, feet
REAR_SCREWS = [(sx * (L.CASE_X - 0.0060), z) for sx in (-1, 1) for z in (0.0090, 0.0720)]
FEET = ((-0.052, -0.078), (0.052, -0.078), (-0.052, 0.084), (0.052, 0.084))
FRONT, BACK, UP = (0.0, -1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)

# sides - large solids of revolution, knob - knobs, small / tiny - small parts; seg - chamfers; cord
# - (spline points per segment, 0 = thinned; sides of the power cord; sides of the earphone cord)
LOD_SPECS = [
    dict(lod=0, sides=24, knob=20, small=12, tiny=8, seg=3, cord=(3, 6, 5)),
    dict(lod=1, sides=12, knob=10, small=8, tiny=6, seg=1, cord=(0, 4, 3)),
]

REGIONS = {
    "case": ("case", 1.0), "rear": ("rear", 1.4), "bezel": ("bezel", 2.0), "keypad": ("keypad", 4.0),
    "plate": ("plate", 1.0), "lcd": ("lcd", 1.0), "lcd_wall": ("lcd_wall", 0.6), "key": ("key", 6.0),
    "knurl_sql": ("knurl_sql", 3.0), "knurl_vol": ("knurl_vol", 3.0), "knurl_dial": ("knurl_dial", 2.5),
    "knurl_bnc": ("knurl_bnc", 2.0), "knob": ("knob", 1.5), "pointer": ("pointer", 0.5), "chrome": ("chrome", 1.2),
    "nickel": ("nickel", 1.0), "screw": ("screw", 1.0), "antenna": ("antenna", 1.0), "hole": ("hole", 0.3),
    "db_insert": ("db_insert", 0.6), "cord": ("cord", 0.6), "adapter": ("adapter", 0.8), "label": ("label", 0.6),
    "earbud": ("earbud", 1.2), "grille": ("grille", 1.5), "feet": ("rubber", 0.4), "tape": ("tape", 4.0),
    "inner": ("inner", 0.05),
}


def X(x):
    return x + OX


def Y(y):
    return y + OY


def wdecal(name):
    return os.path.join(WORK, name)


def front_decal(img, xr, zr, y):
    return (wdecal(img), "y", -1, ("x", "z"), (X((xr[0] + xr[1]) / 2), (zr[0] + zr[1]) / 2),
            (xr[1] - xr[0], zr[1] - zr[0]), (Y(y) - 0.0004, Y(y) + 0.0004))


BEZEL_DEC = front_decal("decal_bezel.png", (-L.W / 2, L.W / 2), L.BEZ_Z, FY)
KEYPAD_DEC = front_decal("decal_keypad.png", L.KEYPAD_X, L.KEYPAD_Z, KP_Y)
# the rear panel faces +Y: the image is drawn as seen from behind - the width has a minus sign
REAR_DEC = (wdecal("decal_rear.png"), "y", 1, ("x", "z"), (X(0.0), (L.CASE_Z[0] + L.CASE_Z[1]) / 2),
            (-2 * L.CASE_X, L.CASE_Z[1] - L.CASE_Z[0]), (Y(L.REAR_Y) - 0.0005, Y(L.REAR_Y) + 0.0005))
# tape: the image is rotated with a canvas expansion (make_decals.py) - the size follows the
# rotation
_A = math.radians(abs(L.TAPE_ROT))
TAPE_IMG = (L.TAPE_WH[0] * math.cos(_A) + L.TAPE_WH[1] * math.sin(_A),
            L.TAPE_WH[0] * math.sin(_A) + L.TAPE_WH[1] * math.cos(_A))
TAPE_DEC = (wdecal("decal_tape.png"), "z", 1, ("x", "y"), (X(L.TAPE_C[0]), Y(L.TAPE_C[1])), TAPE_IMG,
            (TOP - 0.0005, TOP + 0.001))

# --- materials ----------------------------------------------------------------------------------
# modules: worn on the edges, small chips, almost no rust
USED = dict(chip=(0.70, 0.75), rust=(0.92, 0.96), rust_low=0.1, floor_z=0.0, dust=0.18, grime=0.22)
LIT = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
METAL = kmats.lin((150, 152, 154))


def mat_knurl(mat, origin, center, ribs, color, seed=1.0, gloss=0.35, spec=0.25, dust=0.08, grime=0.15):
    """Knob with a ribbed side (axis along Y): the ribs are the sine of the angle around the knob axis
    center = (x, z) in world coordinates; the end face has no ribs; the rib tops are rubbed by fingers.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    dx = t.math("SUBTRACT", sep.outputs["X"], center[0])
    dz = t.math("SUBTRACT", sep.outputs["Z"], center[1])
    ang = t.math("ARCTAN2", dz, dx)
    rib = t.math("ADD", 0.5, t.math("MULTIPLY", t.math("SINE", t.math("MULTIPLY", ang, float(ribs))), 0.5))
    side = t.maprange(t.math("ABSOLUTE", nsep.outputs["Y"]), 0.5, 0.8, 1.0, 0.0)
    r = t.math("MULTIPLY", rib, side)
    groove = t.math("MULTIPLY", t.math("SUBTRACT", 1.0, rib), side)
    col = t.mixc(t.maprange(t.noise(vec, 6.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                 tuple(c * 0.92 for c in color[:3]) + (1,), color)
    col = t.mixc(t.math("MULTIPLY", groove, 0.6), col, tuple(c * 0.45 for c in color[:3]) + (1,))
    worn = t.math("MULTIPLY", t.math("MULTIPLY", r, r), t.maprange(t.noise(vec, 14.0, 4.0, 0.6), 0.45, 0.7, 0.0, 0.5))
    col = t.mixc(worn, col, tuple(min(1.0, c * 2.2 + 0.03) for c in color[:3]) + (1,))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, 0.0, dust, grime, 0.4)
    gl = t.math("SUBTRACT", gloss, t.math("ADD", t.math("MULTIPLY", groove, gloss * 0.4),
                                          t.math("MULTIPLY", dirt, gloss * 0.5)))
    return kmats.out(t, col, gl, spec, t.math("MULTIPLY", r, 0.8))


def mat_keytop(mat, origin, color, seed=4.4, gloss=0.35, spec=0.25, pitch=0.00075, row=0.0013, dust=0.03,
               grime=0.08, scuff=(0.84, 0.92)):
    """Key: black plastic. The face is ribbed with rows of short vertical strokes (the ridges are lighter
    than the key in the photos), with a smooth frame at the face edge (a Bevel node along the chamfer),
    the strokes rubbed by fingers; no ribs on the sides. Little dirt in the corners: on black plastic
    it lightens (GRIME is lighter than the key).
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    face = t.maprange(t.math("ABSOLUTE", nsep.outputs["Y"]), 0.90, 0.97, 0.0, 1.0)
    inner = t.maprange(t.edge_wear(0.0009), 0.03, 0.10, 1.0, 0.0)
    sx = t.math("SINE", t.math("MULTIPLY", sep.outputs["X"], 2 * math.pi / pitch))
    sz = t.math("SINE", t.math("MULTIPLY", sep.outputs["Z"], 2 * math.pi / row))
    dash = t.math("MULTIPLY", t.math("GREATER_THAN", sx, 0.1), t.math("GREATER_THAN", sz, -0.25))
    rub = t.maprange(t.noise(vec, 9.0, 4.0, 0.6), 0.45, 0.70, 1.0, 0.35)
    rib = t.math("MULTIPLY", t.math("MULTIPLY", dash, rub), t.math("MULTIPLY", face, inner))
    col = t.mixc(t.maprange(t.noise(vec, 6.0, 6.0, 0.6), 0.3, 0.7, 0.0, 1.0),
                 tuple(c * 0.92 for c in color[:3]) + (1,), color)
    col = t.mixc(t.math("MULTIPLY", rib, 0.8), col, tuple(c * 2.4 + 0.008 for c in color[:3]) + (1,))
    edge = t.maprange(t.edge_wear(0.002), 0.06, 0.25, 0.0, 1.0)
    sc = t.step(t.math("ADD", t.math("MULTIPLY", t.noise(vec, 18.0, 8.0, 0.7), 0.7), t.math("MULTIPLY", edge, 0.6)),
                scuff[0], scuff[1])
    col = t.mixc(t.math("MULTIPLY", sc, 0.35), col, tuple(min(1.0, c * 1.6 + 0.04) for c in color[:3]) + (1,))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, 0.0, dust, grime, 0.12)
    gl = t.math("SUBTRACT", gloss, t.math("MULTIPLY", t.math("ADD", dirt, rib), gloss * 0.5))
    s = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.5))
    return kmats.out(t, col, gl, s, t.math("MULTIPLY", rib, 0.6))


GUN = kmats.lin((72, 74, 79))           # case: dark grey enamel (photo)
KNOB_BLACK = kmats.lin((24, 24, 25))
NICKEL = dict(along="y", gloss=0.55, spec=0.65, dust=0.08, grime=0.3)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "case": ("paint", dict(USED, color=GUN, under=METAL, seed=1.6, gloss=0.40, spec=0.30)),
    "rear": ("paint", dict(USED, color=kmats.lin((66, 68, 72)), under=METAL, seed=2.2, gloss=0.35, spec=0.28,
                           chip=(0.80, 0.86), decal_items=[REAR_DEC])),
    # bezel is cast plastic: rubbed to light on the edges
    "bezel": ("paint", dict(USED, color=kmats.lin((68, 70, 75)), under=kmats.lin((112, 114, 118)), seed=2.9,
                            gloss=0.30, spec=0.22, chip=(0.78, 0.84), decal_items=[BEZEL_DEC])),
    "keypad": ("paint", dict(USED, color=kmats.lin((60, 58, 55)), under=kmats.lin((128, 126, 120)), seed=3.4,
                             gloss=0.45, spec=0.40, chip=(0.88, 0.93), dust=0.08, decal_items=[KEYPAD_DEC])),
    # nameplate without text: a brushed brass-plated plate
    "plate": ("paint", dict(USED, color=kmats.lin((128, 116, 92)), under=kmats.lin((176, 162, 128)), seed=3.9,
                            gloss=0.60, spec=0.55, chip=(0.82, 0.88), dust=0.08)),
    # the display is a part with its own texture (section lcd): this kind does not go into the atlas
    "lcd": ("flat", dict(color=kmats.lin((104, 112, 96)), gloss=0.75, spec=0.55)),
    "lcd_wall": ("flat", dict(color=kmats.lin((16, 17, 18)), gloss=0.5, spec=0.3)),
    "key": (mat_keytop, dict(color=kmats.lin((19, 19, 20)), seed=4.4, gloss=0.35, spec=0.25)),
    "knurl_sql": (mat_knurl, dict(center=(X(L.SQL[0]), L.SQL[1]), ribs=36, color=KNOB_BLACK, seed=5.1)),
    "knurl_vol": (mat_knurl, dict(center=(X(L.VOL[0]), L.VOL[1]), ribs=36, color=KNOB_BLACK, seed=5.4)),
    "knurl_dial": (mat_knurl, dict(center=(X(L.DIAL[0]), L.DIAL[1]), ribs=48, color=kmats.lin((30, 30, 31)),
                                   seed=5.8, gloss=0.15, spec=0.10)),
    # BNC bayonet nut: nickel, ribs along the axis
    "knurl_bnc": (mat_knurl, dict(center=(X(L.BNC[0]), L.BNC[1]), ribs=24, color=kmats.lin((112, 114, 118)),
                                  seed=6.1, gloss=0.50, spec=0.55, dust=0.1, grime=0.3)),
    "knob": ("plastic", dict(color=KNOB_BLACK, seed=6.2, gloss=0.55, spec=0.45, dust=0.06, grime=0.1,
                             scuff=(0.80, 0.88))),
    "pointer": ("flat", dict(color=kmats.lin((222, 222, 216)), gloss=0.5, spec=0.3)),
    "chrome": ("steel", dict(seed=6.8, tone=0.52, along="z", gloss=0.70, spec=0.80, dust=0.06, grime=0.2)),
    "nickel": ("steel", dict(NICKEL, seed=7.3, tone=0.48)),
    # rear panel and BNC flange screws: blued steel
    "screw": ("steel", dict(seed=11.2, tone=0.20, along="z", gloss=0.45, spec=0.5, dust=0.15, grime=0.45)),
    "antenna": ("steel", dict(seed=7.9, tone=0.56, along="z", gloss=0.70, spec=0.8, dust=0.06, grime=0.18)),
    "hole": ("flat", dict(color=kmats.lin((8, 8, 9)), gloss=0.1, spec=0.05)),
    "db_insert": ("plastic", dict(color=kmats.lin((34, 34, 36)), seed=8.4, gloss=0.25, spec=0.15, dust=0.1)),
    "cord": ("plastic", dict(color=kmats.lin((28, 28, 29)), seed=8.9, gloss=0.25, spec=0.15, dust=0.2, grime=0.2,
                             scuff=(0.9, 1.0))),
    "adapter": ("plastic", dict(color=kmats.lin((36, 36, 38)), seed=9.4, gloss=0.30, spec=0.2, mottle=0.08,
                                dust=0.25, grime=0.25, scuff=(0.80, 0.88))),
    # adapter label without text: silver film, rubbed
    "label": ("paint", dict(USED, color=kmats.lin((108, 110, 106)), under=kmats.lin((70, 70, 68)), seed=12.3,
                            gloss=0.25, spec=0.18, chip=(0.74, 0.80), dust=0.35, grime=0.5)),
    "earbud": ("plastic", dict(color=kmats.lin((22, 22, 23)), seed=9.9, gloss=0.55, spec=0.4, dust=0.08,
                               grime=0.12, scuff=(0.84, 0.92))),
    "grille": ("steel", dict(seed=10.3, tone=0.10, along="x", gloss=0.3, spec=0.3, dust=0.1, grime=0.2,
                             holes=(("x", "y"), 0.0011, 0.30))),
    "tape": ("paint", dict(LIT, color=kmats.lin((212, 200, 158)), gloss=0.12, spec=0.06, dust=0.08,
                           decal_items=[TAPE_DEC])),
    "inner": ("flat", dict(color=kmats.lin((26, 27, 28)), gloss=0.1, spec=0.05)),
})

OBJ, NAME = "m79_radio_scanner", "ozr_radio_scanner"
SEL_SCREEN = "ozl_screen"
# the display has its own texture: off, and the work frames are stepped through by the mod script
# (frames); frame 0 is decal_lcd_on.png, the others are drawn by make_decals.py
# (m79_layout.LCD_FRAMES)
LCD_PANEL = dict(off="decal_lcd_off.png",
                 frames=["decal_lcd_on.png"] + ["decal_lcd_f%02d.png" % i for i in range(1, len(L.LCD_FRAMES))],
                 size=256, gloss=0.75)
# work look in the preview: the display glows (frame 0); nothing changes in the atlas
ON = dict(remap={}, emissive=(1.0, 1.0, 1.0, 1.0))
# vanilla DayZ pen on the roof by the frequency tape (the frequencies were written with it): lies on
# its side, clip sideways
_PA = math.radians(-18.0)
DECOR = [kv.put("pen", (X(0.0), Y(-0.002), TOP), up=(math.cos(_PA), math.sin(_PA), 0.0),
                fwd=(-math.sin(_PA), math.cos(_PA), 0.0))]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL_SCREEN,), hidden=(SEL_SCREEN,), states={"on": ON}, decor=DECOR,
                 panels={"lcd": LCD_PANEL})
P = M.part
BOUNDS = {}


def retag(part, test, region="inner"):
    """Hidden faces go to the dark "inner" region with a small scale (they need no atlas room)."""
    part.bm.normal_update()
    idx = part.region_index(region, *M.regions[region])
    for f in part.bm.faces:
        if f.is_valid and test(f):
            f[part.reg] = idx


def facing(axis, sign, thr=0.99):
    return lambda f: f.normal[axis] * sign > thr


def boxp(name, region, x0, x1, y0, y1, z0, z1, **kw):
    """Box in instrument axes (the OX, OY shift is applied here)."""
    p = P(name, region, **{k: kw.pop(k) for k in ("uv_name", "uv_origin", "group") if k in kw})
    g.box(p, X(x0), X(x1), Y(y0), Y(y1), z0, z1, **kw)
    return p


def cylp(name, region, c, axis, r, length, sides, **kw):
    p = P(name, region, **{k: kw.pop(k) for k in ("uv_name", "uv_origin") if k in kw})
    g.cyl(p, (X(c[0]), Y(c[1]), c[2]), axis, r, length, sides, **kw)
    return p


def lathe(part, c, axis, prof, sides):
    """Solid of revolution: prof is [(r, d)] along the axis `axis` (a vector) from point c in instrument
    axes (the OX, OY shift is applied here), d grows along the axis; r = 0 is a pole (the end is
    closed by a fan), otherwise the end is closed by a face.
    """
    bm = part.bm
    a = Vector(axis).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(a.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    e1 = (ref - a * ref.dot(a)).normalized()
    e2 = a.cross(e1)
    o = Vector((X(c[0]), Y(c[1]), c[2]))
    rings = []
    for r, d in prof:
        p0 = o + a * d
        if r < 1e-7:
            rings.append([bm.verts.new(p0)])
        else:
            rings.append([bm.verts.new(p0 + (e1 * math.cos(2 * math.pi * k / sides) +
                                             e2 * math.sin(2 * math.pi * k / sides)) * r) for k in range(sides)])
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            if len(r0) == 1:
                faces.append(bm.faces.new([r0[0], r1[j], r1[k]]))
            elif len(r1) == 1:
                faces.append(bm.faces.new([r0[k], r0[j], r1[0]]))
            else:
                faces.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    if len(rings[0]) > 1:
        faces.append(bm.faces.new(rings[0][::-1]))
    if len(rings[-1]) > 1:
        faces.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    part.tag(faces)
    return faces


def rrect(a0, a1, b0, b1, corners):
    """Rounded rectangle, counter-clockwise; corners are (r, seg) for the corners left-bottom,
    right-bottom, right-top, left-top.
    """
    out = []
    for (oa, ob, start), (r, seg) in zip(((a0, b0, math.pi), (a1, b0, 1.5 * math.pi), (a1, b1, 0.0),
                                         (a0, b1, 0.5 * math.pi)), corners):
        ca = oa + (r if oa == a0 else -r)
        cb = ob + (r if ob == b0 else -r)
        for k in range(seg + 1):
            t = start + 0.5 * math.pi * k / seg
            out.append((ca + r * math.cos(t), cb + r * math.sin(t)))
    return out


def loft(part, axes, rect, corners, rings):
    """Prism of the rounded section rect (in axes `axes` = (ia, ib)) along the third axis: rings are
    [(c, d)], the section is shrunk by d (chamfers, seams); the ends are closed by a face.
    """
    bm = part.bm
    ia, ib = axes
    ic = 3 - ia - ib
    a0, a1, b0, b1 = rect
    loops = []
    for c, d in rings:
        vs = []
        for a, b in rrect(a0 + d, a1 - d, b0 + d, b1 - d, [(max(r - d, 0.0002), s) for r, s in corners]):
            q = [0.0, 0.0, 0.0]
            q[ia], q[ib], q[ic] = a, b, c
            vs.append(bm.verts.new(Vector(q)))
        loops.append(vs)
    n = len(loops[0])
    faces = [bm.faces.new(loops[0][::-1]), bm.faces.new(loops[-1])]
    for l0, l1 in zip(loops, loops[1:]):
        for i in range(n):
            j = (i + 1) % n
            faces.append(bm.faces.new([l0[i], l0[j], l1[j], l1[i]]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    part.tag(faces)
    return faces


def frustum(part, cx, cz, w, h, yb, yf, inset, back=True):
    """Key: a w x h rectangle at the panel (yb) narrowing by inset on each side toward the face (yf);
    faces outward by winding order; the back one (back) goes to "inner" at the caller.
    """
    bm = part.bm
    before = set(bm.faces)
    vs = []
    for y, d in ((yb, 0.0), (yf, inset)):
        vs.append([bm.verts.new(Vector((X(cx + sx * (w / 2 - d)), Y(y), cz + sz * (h / 2 - d))))
                   for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    b, f = vs
    faces = [bm.faces.new(f)] + ([bm.faces.new(b[::-1])] if back else [])
    for i in range(4):
        j = (i + 1) % 4
        faces.append(bm.faces.new([b[i], b[j], f[j], f[i]]))
    part.tag([q for q in bm.faces if q not in before])


def sphere(part, c, r, seg):
    bm = part.bm
    before = set(bm.faces)
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(3, seg // 2), radius=r,
                              matrix=Matrix.Translation(c))
    faces = [q for q in bm.faces if q not in before]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    part.tag(faces)


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, as in M45, M69, M73)."""
    v = [Vector(p) for p in pts]
    out = []
    for i in range(len(v) - 1):
        p0 = v[i - 1] if i > 0 else 2 * v[i] - v[i + 1]
        p1, p2 = v[i], v[i + 1]
        p3 = v[i + 2] if i + 2 < len(v) else 2 * v[i + 1] - v[i]
        for s in range(k):
            t = s / k
            out.append(0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (3 * p1 - p0 - 3 * p2 + p3) * t ** 3))
    out.append(v[-1])
    return [tuple(q) for q in out]


def shifted(pts):
    return [(X(x), Y(y), z) for x, y, z in pts]


def sparse(pts):
    """Cord for the mid LOD: every second point, and always the last one (no double point at the end)."""
    return pts[::2] if (len(pts) - 1) % 2 == 0 else pts[::2] + pts[-1:]


def ribs(d0, d1, r_hi, r_lo, n):
    """Profile of a ribbed strain relief (ring ribs) from d0 to d1: n ribs, radius r_hi -> r_lo."""
    out = []
    step = (d1 - d0) / max(n, 1)
    for i in range(n):
        r = r_hi + (r_lo - r_hi) * i / max(n - 1, 1)
        a = d0 + i * step
        out += [(r, a + step * 0.15), (r, a + step * 0.65), (r * 0.88, a + step * 0.85)]
    return out


# --- body ---------------------------------------------------------------------------------------
def build_body(spec):
    """Cover (roof with rounded corners, sides, a rear panel with a chamfered edge), the front bezel with
    the display and keypad recesses and the column seams, the display, the nameplate, feet, the tape
    on the roof.
    """
    lod, seg = spec["lod"], spec["seg"]
    parts = []
    case = P("case", "case")
    rear = Y(L.REAR_Y)
    rings = [(Y(L.BEZ_Y[1] - 0.0005), 0.0)] + ([(rear - 0.0008, 0.0), (rear, 0.0008)] if lod == 0 else [(rear, 0.0)])
    loft(case, (0, 2), (X(-L.CASE_X), X(L.CASE_X), L.CASE_Z[0], L.CASE_Z[1]),
         [(CASE_R[0], 1), (CASE_R[0], 1), (CASE_R[1], seg + 1), (CASE_R[1], seg + 1)], rings)
    retag(case, facing(1, 1), "rear")
    retag(case, lambda f: facing(1, -1)(f) or facing(2, -1)(f))
    parts.append(case)
    # bezel: a box with a chamfer minus the display and keypad recesses (the walls and bottoms of
    # the recesses are cutter regions) and the column seams (as on the bezel print)
    bz = P("bezel_raw", "bezel")
    g.box(bz, X(-L.W / 2), X(L.W / 2), Y(L.BEZ_Y[0]), Y(L.BEZ_Y[1]), L.BEZ_Z[0], L.BEZ_Z[1], r=0.0030, seg=seg)
    c_lcd = P("cut_lcd", "lcd_wall")
    g.box(c_lcd, X(L.LCD_X[0]), X(L.LCD_X[1]), Y(FY - 0.005), Y(LCD_Y), L.LCD_Z[0], L.LCD_Z[1])
    c_kp = P("cut_keypad", "keypad")
    g.box(c_kp, X(L.KEYPAD_X[0]), X(L.KEYPAD_X[1]), Y(FY - 0.005), Y(KP_Y), L.KEYPAD_Z[0], L.KEYPAD_Z[1])
    cuts = [c_lcd, c_kp]
    if lod == 0:
        for nm, (x0, x1, z0, z1) in (
                ("cut_col", (L.LEFT_X[1] - 0.00035, L.LEFT_X[1] + 0.00035, L.BEZ_Z[0] + 0.0016, L.BEZ_Z[1] - 0.0016)),
                ("cut_phone", (L.LEFT_X[0] + 0.0016, L.LEFT_X[1], L.PHONE_DIV_Z - 0.00035, L.PHONE_DIV_Z + 0.00035))):
            c = P(nm, "lcd_wall")
            g.box(c, X(x0), X(x1), Y(FY - 0.005), Y(FY + 0.0006), z0, z1)
            cuts.append(c)
    bezel = M.boolean("bezel_%d" % lod, bz, cuts)
    retag(bezel, facing(1, 1))
    parts.append(bezel)
    # display: a face at the bottom of the window (ozl_screen), own texture - section lcd with a
    # flat UV 0..1
    lcd = P("lcd", "lcd", group=SEL_SCREEN, section="lcd")
    y = Y(LCD_Y - 0.0001)
    x0, x1, z0, z1 = X(L.LCD_X[0]), X(L.LCD_X[1]), L.LCD_Z[0], L.LCD_Z[1]
    g.quad(lcd, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)])
    parts.append(lcd)
    parts.append(boxp("plate", "plate", L.PLATE_X[0], L.PLATE_X[1], FY - 0.0006, FY + 0.0003, L.PLATE_Z[0],
                      L.PLATE_Z[1], **(dict(r=0.0003, seg=1) if lod == 0 else {})))
    if lod == 0:
        # rubber feet with a chamfer
        for i, (fx, fy) in enumerate(FEET):
            ft = P("foot%d" % i, "feet", uv_name="foot", uv_origin=(X(fx), Y(fy), 0.0))
            lathe(ft, (fx, fy, 0.0), UP, [(0.0, 0.0), (0.0050, 0.0), (0.0058, 0.0008), (0.0060, L.FOOT_H + 0.0003),
                                          (0.0, L.FOOT_H + 0.0003)], 8)
            parts.append(ft)
        # rear panel screws: a countersunk head with a chamfer
        for i, (sx, sz) in enumerate(REAR_SCREWS):
            sc = P("rear_screw%d" % i, "screw", uv_name="rear_screw", uv_origin=(X(sx), Y(L.REAR_Y), sz))
            lathe(sc, (sx, L.REAR_Y, sz), BACK, [(0.0, -0.0003), (0.0017, -0.0003), (0.0017, 0.0003), (0.0012, 0.0007),
                                                 (0.0, 0.0008)], 8)
            parts.append(sc)
    # frequency tape: a thin face above the roof, rotated as in the image
    tp = P("tape", "tape")
    a = math.radians(L.TAPE_ROT)
    u, v = Vector((math.cos(a), math.sin(a), 0)), Vector((-math.sin(a), math.cos(a), 0))
    c = Vector((X(L.TAPE_C[0]), Y(L.TAPE_C[1]), TOP + 0.0002))
    hw, hh = L.TAPE_WH[0] / 2 * 0.985, L.TAPE_WH[1] / 2 * 0.95
    g.quad(tp, [tuple(c + u * su * hw + v * sv * hh) for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    parts.append(tp)
    return parts


# --- face: buttons, knobs, keypad, dial, jack ----------------------------------------------------
def knob_pointer(part, c, y, r, deg):
    """White tick on the knob end: from the middle to the edge at angle deg (0 is to the right, counter-clockwise)."""
    a = math.radians(deg)
    fr = g.Frame((X(c[0]), Y(y), c[1]), (math.cos(a), 0, math.sin(a)), (-math.sin(a), 0, math.cos(a)), (0, -1, 0))
    g.box(part, 0.0018, r - 0.0010, -0.00045, 0.00045, -0.0001, 0.0003, frame=fr)


def build_front(spec):
    lod, n, nk, ns, nt = spec["lod"], spec["sides"], spec["knob"], spec["small"], spec["tiny"]
    parts = []
    # power button
    pw = P("power", "key")
    frustum(pw, L.POWER[0], L.POWER[1], L.POWER_WH[0], L.POWER_WH[1], FY + 0.0005, FY - 0.0022, 0.0006)
    retag(pw, facing(1, 1))
    parts.append(pw)
    # squelch and volume knobs: a chrome skirt with a rounded edge, a ribbed knob with a chamfer on
    # the end, a tick
    kr, sr = L.KNOB_R, L.SKIRT_R
    for nm, c, reg, deg in (("sql", L.SQL, "knurl_sql", 150.0), ("vol", L.VOL, "knurl_vol", 75.0)):
        sk = P("skirt_" + nm, "chrome")
        lathe(sk, (c[0], FY, c[1]), FRONT, [(0.0, -0.0002), (sr - 0.0004, -0.0002), (sr, 0.0004),
                                            (sr - 0.0005, 0.0017), (0.0, 0.0017)], nk - 4 if lod == 0 else nk)
        parts.append(sk)
        kb = P("knob_" + nm, reg)
        lathe(kb, (c[0], FY, c[1]), FRONT,
              [(0.0, 0.0015), (kr, 0.0015), (kr * 0.985, 0.0112)] +
              ([(kr * 0.95, 0.0126), (kr * 0.94 - 0.0007, 0.0135)] if lod == 0 else [(kr * 0.94, 0.0135)]) +
              [(0.0, 0.0135)], nk)
        parts.append(kb)
        if lod == 0:
            pt = P("pointer_" + nm, "pointer")
            knob_pointer(pt, c, FY - 0.0135, kr * 0.94 - 0.0007, deg)
            parts.append(pt)
    # two round buttons right of the display - with a dome (absent on the mid LOD)
    for i, (bx, bz) in enumerate(L.SMALL_BTN if lod == 0 else ()):
        sb = P("small_btn%d" % i, "key", uv_name="small_btn", uv_origin=(X(bx), Y(FY), bz))
        lathe(sb, (bx, FY, bz), FRONT, [(0.0, -0.0002), (L.SMALL_R, -0.0002), (L.SMALL_R, 0.0011),
                                        (L.SMALL_R * 0.7, 0.0018), (0.0, 0.0020)], nt + 2)
        parts.append(sb)
    # keypad: each key is a separate part sharing one atlas place (ribbed face - mat_keytop)
    kw, kh = L.KEY_WH
    keys = [(x, z) for z in L.KEY_ROWS for x in L.KEY_COLS] + L.KEY_EXTRA
    for i, (x, z) in enumerate(keys):
        k = P("key%02d" % i, "key", uv_name="key", uv_origin=(X(x), Y(KP_Y), z))
        frustum(k, x, z, kw, kh, KP_Y + 0.0002, KP_Y - L.KEY_H, 0.0005 if lod == 0 else 0.0003, back=lod == 0)
        retag(k, facing(1, 1))
        parts.append(k)
    # dial: a chrome flange with a rounded edge, ribbed rubber, an end washer, a dimple for a finger
    dx, dz = L.DIAL
    dr, gr = L.DIAL_R, L.GRIP_R
    fl = P("dial_flange", "chrome")
    lathe(fl, (dx, KP_Y, dz), FRONT, [(0.0, -0.0002), (dr - 0.0005, -0.0002), (dr, 0.0004), (dr, 0.0013),
                                      (dr - 0.0012, 0.0022), (0.0, 0.0022)], n)
    parts.append(fl)
    gp = P("dial_grip", "knurl_dial")
    lathe(gp, (dx, KP_Y, dz), FRONT, [(0.0, 0.0020), (gr, 0.0020), (gr * 0.985, 0.0122), (gr * 0.95, 0.0130),
                                      (0.0, 0.0130)], n + 8 if lod == 0 else n)
    parts.append(gp)
    if lod == 0:
        cp = P("dial_cap", "knob")
        lathe(cp, (dx, KP_Y, dz), FRONT, [(0.0, 0.0126), (0.0086, 0.0126), (0.0086, 0.0141), (0.0080, 0.0148),
                                          (0.0, 0.0150)], n)
        parts.append(cp)
        dm = P("dial_dimple", "earbud")
        lathe(dm, (dx + 0.0036, KP_Y, dz + 0.0030), FRONT, [(0.0, 0.0146), (0.0026, 0.0146), (0.0024, 0.0151),
                                                            (0.0, 0.0151)], ns + 4)
        parts.append(dm)
    # headphone jack: a bushing with a chamfer
    jx, jz = L.JACK
    jr = P("jack_ring", "nickel")
    lathe(jr, (jx, FY, jz), FRONT, [(0.0, -0.0002), (L.JACK_R, -0.0002), (L.JACK_R, 0.0006),
                                    (L.JACK_R - 0.0005, 0.0010), (0.0, 0.0010)], ns)
    parts.append(jr)
    return parts


# --- rear panel: connectors, BNC plug, hinge, antenna ---------------------------------------------
def ant_frame():
    """Antenna axis: the origin is above the hinge, n points up along the antenna."""
    o = Vector((X(L.BNC[0]), Y(KNUCKLE_Y), L.BNC[1] + 0.002))
    u = Vector((1, 0, 0)) - ANT_D * ANT_D.x
    u.normalize()
    return g.Frame(o, u, ANT_D.cross(u), ANT_D)


def build_rear(spec):
    lod, n, ns, nt = spec["lod"], spec["sides"], spec["small"], spec["tiny"]
    parts = []
    bx, bz = L.BNC
    R = L.REAR_Y
    # BNC: a square flange on four screws, the socket, the plug - a ribbed bayonet nut and a strain
    # relief
    parts.append(boxp("bnc_flange", "nickel", bx - 0.0055, bx + 0.0055, R - 0.0005, R + 0.0012, bz - 0.0055,
                      bz + 0.0055, **(dict(r=0.0004, seg=1) if lod == 0 else {})))
    if lod == 0:
        for i, (sx, sz) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
            cx, cz = bx + sx * 0.0040, bz + sz * 0.0040
            sc = P("bnc_screw%d" % i, "screw", uv_name="bnc_screw", uv_origin=(X(cx), Y(R), cz))
            lathe(sc, (cx, R, cz), BACK, [(0.0, 0.0010), (0.0009, 0.0010), (0.0009, 0.0015), (0.0006, 0.0018),
                                          (0.0, 0.0019)], 6)
            parts.append(sc)
    so = P("bnc_socket", "nickel")
    lathe(so, (bx, R, bz), BACK, [(0.0, 0.0010), (0.0046, 0.0010), (0.0046, 0.0050), (0.0, 0.0050)], nt)
    parts.append(so)
    nut = P("bnc_plug", "knurl_bnc")
    lathe(nut, (bx, R, bz), BACK, [(0.0, 0.0045), (0.0055, 0.0045), (0.0060, 0.0051), (0.0060, 0.0138),
                                   (0.0055, 0.0145), (0.0, 0.0145)], n - 8 if lod == 0 else ns)
    parts.append(nut)
    pb = P("bnc_plug_back", "chrome")
    lathe(pb, (bx, R, bz), BACK, [(0.0, 0.0143), (0.0042, 0.0143), (0.0040, 0.0192), (0.0033, 0.0200),
                                  (0.0, 0.0200)], ns)
    parts.append(pb)
    kn = P("ant_knuckle", "chrome")
    lathe(kn, (bx, KNUCKLE_Y, bz), (1.0, 0.0, 0.0), [(0.0, -0.0050), (0.0039, -0.0050), (0.0045, -0.0043),
                                                     (0.0045, 0.0043), (0.0039, 0.0050), (0.0, 0.0050)], ns)
    parts.append(kn)
    if lod == 0:
        ks = P("ant_knuckle_screw", "screw")
        lathe(ks, (bx, KNUCKLE_Y, bz), (1.0, 0.0, 0.0), [(0.0, 0.0048), (0.0022, 0.0048), (0.0022, 0.0055),
                                                         (0.0016, 0.0059), (0.0, 0.0060)], nt)
        parts.append(ks)
    # antenna: sections with crimped collars on the upper ends (near LOD) and a ball
    fr = ant_frame()
    for i, (s0, s1, r, nm) in enumerate(ANT):
        p = P(nm, "antenna")
        g.cyl(p, (0, 0, (s0 + s1) / 2), "z", r, s1 - s0, ns if r > 0.0025 else max(6, ns - 4), frame=fr)
        parts.append(p)
        if lod == 0 and 0 < i < len(ANT) - 1:
            fe = P(nm + "_ferrule", "antenna")
            g.cyl(fe, (0, 0, s1 - 0.0012), "z", r + 0.00035, 0.0024, ns - 2 if r > 0.0025 else ns - 4, frame=fr)
            parts.append(fe)
    ball = P("ant_ball", "antenna")
    if lod == 0:
        sphere(ball, fr.p(0, 0, ANT_BALL_S), ANT_BALL_R, 10)
    else:
        g.cyl(ball, (0, 0, ANT_BALL_S), "z", ANT_BALL_R, 0.005, 5, frame=fr)
    parts.append(ball)
    # RS-232: a flange, a D-shaped shell, a dark insert, hex standoffs
    dx, dz = L.DB25
    hw, hh = L.DB25_WH[0] / 2, L.DB25_WH[1] / 2
    parts.append(boxp("db_flange", "nickel", dx - 0.0265, dx + 0.0265, R - 0.0005, R + 0.0008, dz - 0.0065,
                      dz + 0.0065, **(dict(r=0.0004, seg=1) if lod == 0 else {})))
    sh = P("db_shell", "nickel")
    g.prism(sh, [(X(dx - hw * 0.88), dz - hh), (X(dx + hw * 0.88), dz - hh), (X(dx + hw), dz + hh),
                 (X(dx - hw), dz + hh)], (0, 2), Y(R + 0.0008), Y(R + 0.0062))
    parts.append(sh)
    ins = P("db_insert", "db_insert")
    k = 0.0012
    g.prism(ins, [(X(dx - hw * 0.88 + k), dz - hh + k), (X(dx + hw * 0.88 - k), dz - hh + k),
                  (X(dx + hw - k), dz + hh - k), (X(dx - hw + k), dz + hh - k)], (0, 2), Y(R + 0.0008), Y(R + 0.0066))
    parts.append(ins)
    if lod == 0:
        for i, sx in enumerate((-1, 1)):
            parts.append(cylp("db_post%d" % i, "nickel", (dx + sx * 0.0235, R + 0.0038, dz), "y", 0.0024, 0.0060, 6,
                              uv_name="db_post", uv_origin=(X(dx + sx * 0.0235), Y(R), dz)))
    # external speaker and record jacks: a hex nut, a bushing, a dark hole
    for nm, (jx, jz) in (("extsp", L.EXTSP), ("rec", L.RECJ)):
        parts.append(cylp("jack_" + nm, "nickel", (jx, R + 0.0009, jz), "y", 0.0040, 0.0018, 6,
                          uv_name="rear_jack", uv_origin=(X(jx), Y(R), jz)))
        if lod == 0:
            bu = P("bush_" + nm, "nickel", uv_name="rear_bush", uv_origin=(X(jx), Y(R), jz))
            lathe(bu, (jx, R, jz), BACK, [(0.0, 0.0015), (0.0026, 0.0015), (0.0026, 0.0028), (0.0021, 0.0032),
                                          (0.0, 0.0032)], nt)
            parts.append(bu)
            parts.append(cylp("hole_" + nm, "hole", (jx, R + 0.0033, jz), "y", 0.0016, 0.0002, 8,
                              uv_name="rear_hole", uv_origin=(X(jx), Y(R), jz)))
    # power plug in the jack: a chamfered body and a ribbed strain relief
    px, pz = L.DCJ
    dc = P("dc_plug", "cord")
    tail = (ribs(0.0182, 0.0236, 0.0033, 0.0026, 3) + [(0.0022, 0.0256)]) if lod == 0 else [(0.0032, 0.0180),
                                                                                           (0.0021, 0.0256)]
    lathe(dc, (px, R, pz), BACK, [(0.0, 0.0), (0.0040, 0.0), (0.0046, 0.0012), (0.0046, 0.0166), (0.0040, 0.0180)] +
          tail + [(0.0, 0.0262)], 12 if lod == 0 else 8)
    parts.append(dc)
    return parts


# --- adapter and cords --------------------------------------------------------------------------
def dc_cord_points():
    """Power cord: from the plug's strain relief to the rear, down to the shelf, a loop to the inlet on
    the adapter's right end.
    """
    px, pz = L.DCJ
    y0 = L.REAR_Y + 0.0260
    gx = ADP[1] + 0.0080
    return shifted([(px, y0, pz), (px, y0 + 0.006, pz - 0.002), (px + 0.003, y0 + 0.013, pz - 0.009),
                    (px + 0.001, y0 + 0.020, 0.0045), (px - 0.006, y0 + 0.023, CORD_R + 0.0002),
                    (px - 0.013, y0 + 0.019, CORD_R + 0.0004), (gx + 0.002, 0.140, 0.0070), (gx, 0.140, 0.0100)])


def ear_cord_points():
    """Earphone cord: from the mini jack's strain relief down to the shelf, an arc to the left and back to the earphone."""
    jx, jz = L.JACK
    r = EAR_CORD_R
    ex, ey = EAR
    return shifted([(jx, FY - 0.0215, jz), (jx, FY - 0.0255, jz - 0.002), (jx - 0.0015, FY - 0.028, 0.0035),
                    (jx - 0.005, FY - 0.0285, r), (jx - 0.014, FY - 0.026, r), (jx - 0.025, FY - 0.019, r),
                    (jx - 0.034, FY - 0.007, r), (ex, ey - 0.040, r), (ex - 0.002, ey - 0.027, r + 0.0001),
                    (ex - 0.001, ey - 0.020, 0.0022), (ex, ey - EAR_R - 0.0075, EAR_H / 2)])


def build_extras(spec):
    lod, n, ns, nt, seg = spec["lod"], spec["sides"], spec["small"], spec["tiny"], spec["seg"]
    k_sp, s_dc, s_ear = spec["cord"]
    parts = []
    # 12 V adapter: a body of two halves with a seam, rounded corners, chamfers at the top and
    # bottom; a Euro plug toward -X (pins insulated at the base), the cord inlet with a ribbed
    # strain relief on +X
    x0, x1, y0, y1, h = ADP
    ad = P("adapter", "adapter")
    s = ADP_SEAM_Z
    rings = ([(0.0, 0.0010), (0.0010, 0.0), (s - 0.0004, 0.0), (s - 0.0004, 0.0006), (s + 0.0004, 0.0006),
              (s + 0.0004, 0.0), (h - 0.0016, 0.0), (h, 0.0014)] if lod == 0 else
             [(0.0, 0.0008), (0.0008, 0.0), (h - 0.0012, 0.0), (h, 0.0012)])
    loft(ad, (0, 1), (X(x0), X(x1), Y(y0), Y(y1)), [(ADP_R, max(1, seg - 1))] * 4, rings)
    retag(ad, facing(2, -1))
    parts.append(ad)
    if lod == 0:
        parts.append(boxp("adp_label", "label", x0 + 0.014, x1 - 0.008, y0 + 0.009, y1 - 0.009, h - 0.0001,
                          h + 0.0002))
    yc = (y0 + y1) / 2
    for i, sy in enumerate((-1, 1)):
        py = yc + sy * ADP_PIN_DY
        sl = P("adp_sleeve%d" % i, "adapter", uv_name="adp_sleeve", uv_origin=(X(x0), Y(py), ADP_PIN_Z))
        lathe(sl, (x0, py, ADP_PIN_Z), (-1.0, 0.0, 0.0), [(0.0, -0.0005), (0.0021, -0.0005), (0.0021, 0.0100),
                                                          (0.0, 0.0100)], nt)
        parts.append(sl)
        pn = P("adp_pin%d" % i, "nickel", uv_name="adp_pin", uv_origin=(X(x0), Y(py), ADP_PIN_Z))
        lathe(pn, (x0, py, ADP_PIN_Z), (-1.0, 0.0, 0.0), [(0.0, 0.0095), (0.0019, 0.0095), (0.0019, 0.0176),
                                                          (0.0014, 0.0186), (0.0, 0.0190)], nt)
        parts.append(pn)
    gm = P("adp_grommet", "cord")
    lathe(gm, (x1, 0.140, 0.0100), (1.0, 0.0, 0.0),
          [(0.0, -0.0005), (0.0040, -0.0005), (0.0040, 0.0015)] +
          (ribs(0.0016, 0.0064, 0.0034, 0.0027, 2) if lod == 0 else []) + [(0.0023, 0.0080), (0.0, 0.0082)], nt)
    parts.append(gm)
    pts = dc_cord_points()
    cd = P("dc_cord", "cord")
    g.pipe(cd, spline(pts, k_sp) if k_sp else sparse(pts), CORD_R, s_dc)
    parts.append(cd)
    # earphone: a mini jack in the socket (bushing, chamfered body, ribbed strain relief), the cord,
    # a "drop" mesh-up: a rounded body with a rim, a sunk mesh, a stub toward the cord
    jx, jz = L.JACK
    if lod == 0:
        co = P("ear_collar", "nickel")
        lathe(co, (jx, FY, jz), FRONT, [(0.0, 0.0), (0.0024, 0.0), (0.0024, 0.0025), (0.0, 0.0025)], nt)
        parts.append(co)
    ep = P("ear_plug", "earbud")
    tail = (ribs(0.0136, 0.0172, 0.0027, 0.0022, 2) + [(0.0019, 0.0202)]) if lod == 0 else [(0.0026, 0.0140)]
    lathe(ep, (jx, FY, jz), FRONT, [(0.0, 0.0024), (0.0030, 0.0024), (0.0034, 0.0030), (0.0034, 0.0126),
                                    (0.0030, 0.0133)] + tail + [(0.0014, 0.0214), (0.0, 0.0216)], 10 if lod == 0 else 6)
    parts.append(ep)
    pts = ear_cord_points()
    ec = P("ear_cord", "cord")
    g.pipe(ec, spline(pts, k_sp) if k_sp else sparse(pts), EAR_CORD_R, s_ear)
    parts.append(ec)
    ex, ey = EAR
    er, eh = EAR_R, EAR_H
    eb = P("ear_body", "earbud")
    lathe(eb, (ex, ey, 0.0), UP,
          [(0.0, 0.0), (er * 0.55, 0.0), (er * 0.85, 0.0008)] +
          ([(er * 0.97, 0.0022), (er, 0.0036), (er * 0.97, eh - 0.0007)] if lod == 0 else [(er, 0.0030)]) +
          [(er * 0.90, eh), (er * 0.84, eh), (er * 0.82, eh - 0.0006), (0.0, eh - 0.0006)],
          n - 8 if lod == 0 else ns)
    parts.append(eb)
    gr = P("ear_grille", "grille")
    lathe(gr, (ex, ey, 0.0), UP, [(0.0, eh - 0.0007), (er * 0.80, eh - 0.0007), (er * 0.80, eh - 0.0003),
                                  (0.0, eh - 0.0002)], n - 8 if lod == 0 else ns)
    parts.append(gr)
    st = P("ear_stem", "earbud")
    g.tube_var(st, shifted([(ex, ey - er * 0.55, eh * 0.45), (ex, ey - er - 0.0010, eh * 0.47),
                            (ex, ey - er - 0.0045, eh * 0.49), (ex, ey - er - 0.0075, eh / 2)]),
               [(0.0030, 0.0024), (0.0026, 0.0021), (0.0019, 0.0017), (0.0014, 0.0014)], nt)
    parts.append(st)
    return parts


def build_lod(spec):
    parts = build_body(spec) + build_front(spec) + build_rear(spec) + build_extras(spec)
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("bounds", tuple(round(c, 4) for c in BOUNDS["lo"]), tuple(round(c, 4) for c in BOUNDS["hi"]))
        # vanilla items: the bounds sit on the roof, neither hanging nor sunk (kv.corners)
        for d in DECOR:
            q = kv.corners(d[5], d[1], d[2], d[3])
            print("decor %s: x %.4f..%.4f y %.4f..%.4f z %.4f..%.4f (roof %.4f, case x %.4f..%.4f)" % (
                d[5], min(p[0] for p in q), max(p[0] for p in q), min(p[1] for p in q), max(p[1] for p in q),
                min(p[2] for p in q), max(p[2] for p in q), TOP, X(-L.CASE_X + CASE_R[1]), X(L.CASE_X - CASE_R[1])))
    return parts


def collision():
    """Three convex parts: the receiver with knobs, the antenna with the BNC plug, the adapter with pins;
    cords and the earphone have no collision (as in M45, M69, M73). Mass is the item's weight in the
    mod, 0.8 kg.
    """
    body = kx.box_pts(X(-L.W / 2), X(L.W / 2), Y(FY), Y(L.REAR_Y), 0.0, L.BEZ_Z[1])
    body += kx.box_pts(X(L.SQL[0] - L.SKIRT_R), X(L.DIAL[0] + L.DIAL_R), Y(KP_Y - 0.0155), Y(FY), 0.005, 0.0565)
    fr = ant_frame()
    ant = kx.box_pts(X(L.BNC[0] - 0.006), X(L.BNC[0] + 0.006), Y(L.REAR_Y), Y(KNUCKLE_Y + 0.0045),
                     L.BNC[1] - 0.006, L.BNC[1] + 0.006)
    for s, r in ((0.0, 0.0045), (ANT_BALL_S, ANT_BALL_R)):
        for k in range(6):
            a = 2 * math.pi * (k + 0.5) / 6
            ant.append(tuple(fr.p(r * math.cos(a), r * math.sin(a), s)))
    x0, x1, y0, y1, h = ADP
    adp = kx.box_pts(X(x0 - 0.019), X(x1), Y(y0), Y(y1), 0.0, h)
    comps = [(body, kx.PEN + r"\metalplate.rvmat"), (ant, kx.PEN + r"\metalplate.rvmat"),
             (adp, kx.PEN + r"\plastic.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    memory = {
        # inventory preview camera: front-left and from above (invView = camera position)
        "invView": [(-0.28, -0.52, 0.38)],
        "ce_center": [(0.0, 0.0, 0.10)],
        "ce_radius": [(0.16, 0.0, 0.10)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


# --look preview: the first four angles (overall view, face, rear with antenna and adapter, roof
# with tape and pen); the work look uses the first two
SHOTS = [
    ("front", (-0.22, -0.56, 0.32), (0.0, 0.0, 0.09), 40),
    ("panel", (-0.03, -0.30, 0.12), (X(0.0), Y(FY), 0.040), 45),
    ("back", (0.34, 0.50, 0.30), (0.0, 0.04, 0.09), 40),
    ("top", (0.06, -0.24, 0.56), (0.0, 0.0, 0.07), 40),
    ("keys", (0.08, -0.22, 0.10), (X(0.020), Y(FY), 0.025), 50),
    ("left", (-0.50, -0.14, 0.22), (-0.03, 0.0, 0.08), 42),
]
M.look_shots = (4, 2)

M.run(build_lod, collision, SHOTS, row_step=0.32, row_shot=((0.16, -1.15, 0.40), (0.16, 0, 0.10)))
