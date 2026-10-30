"""M78 - PDA reader (OZL_Tool_PdaReader): a Trail line module, a portable 2x2 item. It sits in an
OZL_Tool1..3 slot of the line's packer (M15, M20) and shows on its shelf through the proxy.
Model: a late-90s PDA in a cradle dock.

    blender --background --python build_m78.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Run make_decals.py (system Python) before the first build: LCD off and the work frames, the
handwriting field, the button pictograms, the sync icon, the inventory label.

Model: a Palm III type PDA in a dock with a sync button and a cable to the computer, everything on
a dock board. Cradle about 0.10 x 0.10 x 0.08 m, PDA about 0.08 x 0.12 x 0.02 m, board about
0.18 x 0.15 m; grey plastic, a green monochrome screen, screens without text, only bars.

Proportions:
- Palm III: 119 x 81 x 18 mm, 160 g; LCD 160 x 160 dots; the glass with the input field is
  3.20 x 2.375" = 81 x 60 mm. Face layout from a photo (PDA width 81 mm as the scale): the glass
  window is 60 mm wide, from 11 to 88 mm from the top, LCD 57 mm, input field 20 mm; four round
  buttons of about 10.5 mm and a figure-eight rocker in the middle (about 8 x 18 mm), centres
  18 mm from the bottom; a green power button at the left edge; an IR window on the top end. The
  stylus has a metal body with a plastic tip and cap and sits in a slot past the right edge; the
  sync port at the bottom is closed by a spring shutter. The case is two halves: a seam on the
  sides, the face and back edges are rounded.
- HotSync dock (no sizes found, so from the same photo): a base about 0.10 m wide with a convex
  front edge and a vertical lip of about 4 mm, a slope down to the pocket with rounded edges, a
  sync button of diameter 16 mm in the middle in front of the pocket, a pocket front wall of about
  11 mm; the PDA is sunk about 5 mm and tilted back; the rear support follows the item card (cradle
  up to 0.08 m high). The cable is grey, leaves the rear of the dock through a ribbed rubber boot
  and ends in a female DE-9 for the computer's COM port.
- DE-9: steel shell size E (flange 30.8 x 12.5 mm), a D-shaped shell with an insulator and nine
  sockets (pitch 2.77 mm, rows 5 + 4 at 2.84 mm), a moulded body of about 31 x 15 x 40 mm with ears
  for two knurled screws and a strain relief. A home-made line-activity LED (3 mm, red: blinks
  while data is exchanged) is glued into the body from above.
- The board is a 180 x 150 x 5 mm glass-fibre laminate sheet on four rubber feet (two extra
  drilled holes); the dock is pressed to it by two aluminium clamps on M3 screws with washers - a
  home-made arrangement, so that the reader is carried and put into the machine as a single item.

Layout (the module front is toward -Y): the dock with the PDA at the left-centre, the screen toward
the player; at the right rear a cable coil (1.5 turns) with a clamp, at the right the DE-9
connector facing forward; in front the stylus and the inventory label with a barcode. Size about
0.18 x 0.15 x 0.14 m. No vanilla items: the 0.18 x 0.15 board has no room for them, and DayZ has
no PDA, dock, DE-9 or stylus.

Machine look: the LCD is ozl_screen with its own texture (section screen, UV 0..1). Off: blank
grey-green glass (decal_lcd_off). Work: the frames decal_lcd_fNN (OZL_WorkFx frames), a green
backlight and a sync screen - the icon arrows rotate, the progress bar grows record by record.
The LED in the connector is ozl_lamp (atlas _on, blinks - blink). No moving parts, no bones.
LODs: near and mid (about 40 %: no screws, feet, IR window, wheel, clamp, label, sockets, ribs;
simpler buttons; fewer sides on the cable and stylus), no far one.

Blender axes: X is width, Y is depth (the front faces -Y), Z is up. The origin is the centre of
the bottom, so the module lands on the module_N proxy point (autocenter = 0 in Geometry).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m ------------------------------------------------------------------------------
# dock board: glass-fibre laminate on rubber feet
PX0, PX1, PY0, PY1 = -0.090, 0.090, -0.075, 0.075
FOOT_H, PLATE_T = 0.0025, 0.005
ZB = FOOT_H + PLATE_T           # top of the board
HOLES = ((-0.082, 0.066), (0.082, -0.066))   # extra drilled holes
# dock (cradle): base
CX = -0.026                     # dock centre along x
BW, BY0, BY1, BAPEX = 0.104, -0.036, 0.040, -0.050   # width, front at the corners, rear, arc apex
BASE_LIP, BASE_TOP, BASE_IN = 0.004, 0.010, 0.004    # lip, top, slope inset
# PDA: tilted back by TILT; the frame origin is the middle of the face's lower edge
TILT = 16.0
PW, PH, PT = 0.081, 0.119, 0.018
PDA_RC = 0.0055                 # corner radius of the case (front view)
# case sections along the thickness (n, edge inset): back, half seam, face
PDA_PROF = [(-PT, 0.0038), (-PT, 0.0030), (-PT + 0.0005, 0.0014), (-PT + 0.0014, 0.0004), (-PT + 0.0030, 0.0),
            (-0.0082, 0.0), (-0.0079, 0.0005), (-0.0074, 0.0005), (-0.0071, 0.0),
            (-0.0028, 0.0), (-0.0011, 0.0005), (-0.0003, 0.0016), (0.0, 0.0034), (0.0, 0.0042)]
PDA_SEAM = (5, 6, 7)            # seam strips (index of the gap between sections)
PDA_PROF1 = [(-PT, 0.0022), (-PT + 0.0022, 0.0), (-0.0022, 0.0), (0.0, 0.0026)]
PDA_O = (CX, -0.014, ZB + 0.016)
# PDA face (u across, v up from the bottom)
WIN_U, WIN_V = 0.0300, (0.0300, 0.1090)      # dark glass frame
LCD_U, LCD_V = 0.0290, (0.0512, 0.1068)      # LCD 160 x 160
SILK_V = (0.0320, 0.0506)                    # input field
KEY_V = 0.0185
KEY_U = (-0.0255, -0.0125, 0.0125, 0.0255)   # buttons (the rocker is in the middle)
ROCK_R, ROCK_E, ROCK_W = 0.0041, 0.0050, 0.0028   # rocker: lobe radius, half-distance, waist
# pocket and support of the dock (in the PDA frame)
COL_U, COL_V, COL_N = 0.044, (-0.008, 0.006), (-0.027, 0.006)
REST_U, REST_V, REST_N = 0.034, (-0.008, 0.068), (-0.026, -0.0183)
HS = (CX, -0.0335)              # sync button
HS_D = 0.016
# clamps
CLAMP_Y, CLAMP_W, CLAMP_T, CLAMP_FOOT = 0.028, 0.010, 0.0015, 0.0095
# cable, coil, connector
CABLE_R = 0.0024
BOOT_Z = ZB + BASE_TOP + 0.0045         # the cable leaves the support back above the base
BOOT_Y0, BOOT_L = BY1 - 0.011, 0.0125   # boot: from the support back rearward
COIL_C, COIL_R0, COIL_R1 = (0.062, 0.043), 0.021, 0.0128
DSUB_C, DSUB_Y0, DSUB_L = 0.060, -0.040, 0.040     # x centre, flange face, body length
DSUB_H = 0.015                          # body height
DSUB_ZC = ZB + 0.0075                   # connector axis
THUMB_X, THUMB_R = 0.0127, 0.0030       # knurled screws behind the body ears
LED_P = (DSUB_C - 0.0060, DSUB_Y0 + 0.0070)   # activity LED in the body cover
# stylus and label
STY_A, STY_B = (-0.046, -0.064), (0.050, -0.059)
LABEL_C, LABEL_W, LABEL_H = (-0.070, -0.064), 0.034, 0.014

LOD_SPECS = [
    dict(lod=0, sides=16, seg=2),
    dict(lod=1, sides=8, seg=1),
]

REGIONS = {
    "pda": ("pda", 1.4), "cradle": ("cradle", 1.0), "bezel": ("bezel", 1.0), "lcd": ("lcd", 1.0),
    "silk": ("silk", 3.0), "keys": ("keys", 3.0), "keyring": ("keyring", 1.5), "power": ("power", 1.5),
    "ir": ("ir", 1.0), "hotsync": ("hotsync", 3.0), "plate": ("plate", 0.8), "plate_edge": ("plate_edge", 0.6),
    "rubber": ("rubber", 0.6), "alu": ("alu", 1.2), "screw": ("screw", 1.0), "cable": ("cable", 0.8),
    "hood": ("hood", 1.2), "shell": ("shell", 1.5), "dsub_face": ("dsub_face", 1.0), "chrome": ("chrome", 1.0),
    "black": ("black", 1.0), "label": ("label", 3.0), "inner": ("inner", 0.05), "led": ("led", 1.0),
    "sticker": ("sticker", 1.5),
}

FRAME = None


def pda_frame():
    t = math.radians(TILT)
    return g.Frame(PDA_O, (1, 0, 0), (0, math.sin(t), math.cos(t)), (0, -math.cos(t), math.sin(t)))


FRAME = pda_frame()
COS_T = math.cos(math.radians(TILT))


def wdecal(name):
    return os.path.join(WORK, name)


def face_decal(name, u_c, v0, v1, w, n=0.0005):
    """Decal on the PDA face: projection along -Y - the image is squeezed in height by cos(tilt)."""
    lo, hi = FRAME.p(u_c, v0, n), FRAME.p(u_c, v1, n)
    zc = (lo.z + hi.z) / 2
    ys = (lo.y, hi.y)
    return (wdecal(name), "y", -1, ("x", "z"), (PDA_O[0] + u_c, zc), (w, (v1 - v0) * COS_T),
            (min(ys) - 0.004, max(ys) + 0.004))


SILK_DEC = face_decal("decal_silk.png", 0.0, *SILK_V, 2 * LCD_U)
KEYS_DEC = face_decal("decal_keys.png", 0.0, KEY_V - 0.010, KEY_V + 0.010, 0.068, n=0.002)
HS_TOP = ZB + BASE_TOP + 0.0034
HS_DEC = (wdecal("decal_hotsync.png"), "z", 1, ("x", "y"), HS, (HS_D, HS_D), (HS_TOP - 0.001, HS_TOP + 0.002))
LABEL_DEC = (wdecal("decal_label.png"), "z", 1, ("x", "y"), LABEL_C, (LABEL_W, LABEL_H), (ZB, ZB + 0.001))

# common instruments: worn, no rust
LIT = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)


def mat_speckle(mat, origin, **kw):
    """Dark grey Palm plastic with sparkles: fine light specks and a slightly grainy relief over plain plastic."""
    outs = kmats.build_plastic(mat, origin, **kw)
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    vec, sep = t.coords(origin, kw.get("seed", 3.0) + 11.0)
    sp = t.step(t.noise(vec, 1400.0, 1.0, 0.5), 0.64, 0.68)
    col = kmats.sock(mat, outs["color"])
    col = t.mixc(t.math("MULTIPLY", sp, 0.45), col, tuple(min(1.0, c * 1.9 + 0.02) for c in kw["color"][:3]) + (1,))
    hh = t.math("ADD", kmats.sock(mat, outs["height"]), t.math("MULTIPLY", sp, 0.05))
    return dict(outs, color=kmats.Tree.ref(col), height=kmats.Tree.ref(hh))


def mat_textolite(mat, origin, **kw):
    """Glass-fibre laminate: yellow-olive, the weave shows through the resin - frequent stripes along x
    and y, dark resin spots, light scuffs.
    """
    outs = kmats.build_plastic(mat, origin, **kw)
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    vec, sep = t.coords(origin, 7.7)
    wx = t.noise(t.stretch(vec, 1.0, 0.03, 1.0), 260.0, 2.0, 0.5)
    wy = t.noise(t.stretch(vec, 0.03, 1.0, 1.0), 260.0, 2.0, 0.5)
    weave = t.maprange(t.math("ADD", wx, wy), 0.85, 1.15, 0.0, 1.0)
    col = kmats.sock(mat, outs["color"])
    col = t.mixc(t.math("MULTIPLY", weave, 0.16), col, tuple(c * 0.70 for c in kw["color"][:3]) + (1,))
    resin = t.step(t.noise(vec, 9.0, 4.0, 0.5), 0.58, 0.70)
    col = t.mixc(t.math("MULTIPLY", resin, 0.22), col, kmats.lin((120, 104, 52)))
    hh = t.math("ADD", kmats.sock(mat, outs["height"]), t.math("MULTIPLY", weave, 0.05))
    return dict(outs, color=kmats.Tree.ref(col), height=kmats.Tree.ref(hh))


KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "pda": (mat_speckle, dict(color=kmats.lin((76, 78, 79)), seed=3.3, gloss=0.38, spec=0.28, dust=0.15, grime=0.35,
                              scuff=(0.76, 0.84))),
    "cradle": (mat_speckle, dict(color=kmats.lin((66, 68, 69)), seed=4.1, gloss=0.32, spec=0.24, floor_z=ZB,
                                 dust=0.45, grime=0.40, scuff=(0.72, 0.80))),
    "bezel": ("plastic", dict(color=kmats.lin((20, 21, 21)), seed=4.6, gloss=0.5, spec=0.35, dust=0.05, grime=0.05,
                              scuff=(0.95, 1.0))),
    # LCD has its own texture (section screen); this kind is a fallback for the grey-shape render
    "lcd": ("flat", dict(color=kmats.lin((138, 148, 128)), gloss=0.72, spec=0.5)),
    "silk": ("paint", dict(LIT, color=kmats.lin((150, 162, 144)), gloss=0.7, spec=0.5, decal_items=[SILK_DEC])),
    "keys": ("paint", dict(LIT, color=kmats.lin((50, 52, 54)), under=kmats.lin((50, 52, 54)), gloss=0.45, spec=0.3,
                           decal_items=[KEYS_DEC])),
    "keyring": ("plastic", dict(color=kmats.lin((26, 27, 28)), seed=5.3, gloss=0.3, spec=0.2, dust=0.1, grime=0.3,
                                scuff=(0.95, 1.0))),
    "power": ("plastic", dict(color=kmats.lin((34, 164, 136)), seed=5.6, gloss=0.5, spec=0.35, dust=0.05, grime=0.1,
                              scuff=(0.86, 0.92))),
    "ir": ("flat", dict(color=kmats.lin((28, 8, 10)), gloss=0.85, spec=0.7)),
    "hotsync": ("paint", dict(LIT, color=kmats.lin((58, 60, 62)), under=kmats.lin((58, 60, 62)), gloss=0.4, spec=0.3,
                              decal_items=[HS_DEC])),
    "plate": (mat_textolite, dict(color=kmats.lin((196, 182, 112)), seed=6.2, gloss=0.42, spec=0.3, dust=0.55,
                                  grime=0.45, mottle=0.14, scuff=(0.62, 0.70))),
    "plate_edge": ("plastic", dict(color=kmats.lin((214, 204, 160)), seed=6.6, gloss=0.2, spec=0.1, dust=0.2,
                                   grime=0.5, mottle=0.12, scuff=(0.8, 0.9))),
    "rubber": ("plastic", dict(color=kmats.lin((26, 26, 27)), seed=6.9, gloss=0.15, spec=0.08, dust=0.3,
                               scuff=(0.9, 1.0))),
    "alu": ("steel", dict(seed=7.1, tone=0.55, along="y", gloss=0.5, spec=0.6, floor_z=ZB, dust=0.2, grime=0.35)),
    "screw": ("steel", dict(seed=7.4, tone=0.40, along="x", gloss=0.55, spec=0.7, dust=0.1, grime=0.4)),
    "cable": ("plastic", dict(color=kmats.lin((122, 124, 122)), seed=8.0, gloss=0.3, spec=0.2, floor_z=ZB, dust=0.25,
                              grime=0.35, scuff=(0.9, 1.0))),
    "hood": ("plastic", dict(color=kmats.lin((176, 172, 158)), seed=8.4, gloss=0.3, spec=0.2, floor_z=ZB, dust=0.4,
                             grime=0.55, scuff=(0.72, 0.80))),
    "shell": ("steel", dict(seed=8.8, tone=0.62, along="x", gloss=0.65, spec=0.8, dust=0.1, grime=0.3)),
    "dsub_face": ("flat", dict(color=kmats.lin((34, 34, 36)), gloss=0.3, spec=0.2)),
    "chrome": ("steel", dict(seed=9.1, tone=0.66, along="x", gloss=0.8, spec=0.9, dust=0.05, grime=0.15)),
    "black": ("plastic", dict(color=kmats.lin((20, 20, 21)), seed=9.4, gloss=0.35, spec=0.25, dust=0.1, grime=0.2,
                              scuff=(0.86, 0.94))),
    "label": ("paint", dict(LIT, color=kmats.lin((226, 222, 206)), gloss=0.25, spec=0.1, decal_items=[LABEL_DEC])),
    # factory sticker on the PDA back: yellowed paper without text, rubbed
    "sticker": ("plastic", dict(color=kmats.lin((206, 200, 178)), seed=9.8, gloss=0.2, spec=0.1, dust=0.1,
                                grime=0.5, mottle=0.12, scuff=(0.72, 0.80))),
    "inner": ("flat", dict(color=kmats.lin((22, 23, 24)), gloss=0.1, spec=0.05)),
    # line activity LED: dark red when off, lit in work (it blinks - mod script)
    "led": ("flat", dict(color=kmats.lin((76, 16, 14)), gloss=0.85, spec=0.8)),
    "led_on": ("flat", dict(color=kmats.lin((255, 64, 44)), gloss=0.85, spec=0.8)),
})

OBJ, NAME = "m78_pda_reader", "ozr_pda_reader"
SEL_SCREEN, SEL_LAMP = "ozl_screen", "ozl_lamp"
# PDA screen has its own texture: off and 8 work frames (OZL_WorkFx frames, 0.25 s each - a circle
# is 2 s)
LCD_FRAMES = 8
SCREEN = dict(off="decal_lcd_off.png", frames=["decal_lcd_f%02d.png" % i for i in range(LCD_FRAMES)], size=256,
              gloss=0.72)
ON = dict(remap={"led": "led_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL_SCREEN, SEL_LAMP), hidden=(SEL_SCREEN, SEL_LAMP), states={"on": ON},
                 panels={"screen": SCREEN})
P = M.part
BOUNDS = {}


# --- shape helpers ---------------------------------------------------------------------------
def boxp(name, region, x0, x1, y0, y1, z0, z1, **kw):
    p = P(name, region)
    g.box(p, x0, x1, y0, y1, z0, z1, **kw)
    return p


def boxp_f(name, region, u0, u1, v0, v1, n0, n1, **kw):
    p = P(name, region)
    g.box(p, u0, u1, v0, v1, n0, n1, frame=FRAME, **kw)
    return p


def retag(part, faces, axis, sign, region, thr=0.99):
    """Faces of the part looking toward (axis, sign) go to another region."""
    part.bm.normal_update()
    idx = part.region_index(region, *M.regions[region])
    for f in faces:
        if f.is_valid and f.normal[axis] * sign > thr:
            f[part.reg] = idx


def face(part, verts, want):
    """A face from bmesh vertices, turned toward `want`."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def axis_frame(origin, n):
    """Right-handed frame with axis n (u x v = n): for solids of revolution along any direction."""
    n = Vector(n).normalized()
    ref = Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))
    u = ref.cross(n).normalized()
    return g.Frame(origin, u, n.cross(u), n)


def loft(part, rings, frame=None, band_reg=None):
    """Solid by sections: rings = [(polygon [(a, b)], c)] bottom to top (along the third axis; with
    frame - local u, v, n), the same vertex count; the ends are closed. band_reg maps a gap index
    between sections to a region.
    """
    bm = part.bm

    def pt(a, b, c):
        return frame.p(a, b, c) if frame else Vector((a, b, c))
    vs = [[bm.verts.new(pt(x, y, z)) for x, y in poly] for poly, z in rings]
    faces = [bm.faces.new(vs[0][::-1]), bm.faces.new(vs[-1])]
    bands = []
    n = len(vs[0])
    for a, b in zip(vs, vs[1:]):
        band = []
        for i in range(n):
            j = (i + 1) % n
            band.append(bm.faces.new([a[i], a[j], b[j], b[i]]))
        bands.append(band)
        faces += band
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    part.tag(faces)
    for k, reg in (band_reg or {}).items():
        part.tag(bands[k], part.region_index(reg, *M.regions[reg]))
    return faces


def lathe(part, prof, sides, frame, cap0=False, cap1=True):
    """Solid of revolution about the axis n of the right-handed frame: prof [(r, h)] from bottom to top
    (h along n from the frame origin). Face winding sets normals outward; cap0/cap1 close the bottom/top.
    """
    bm = part.bm
    rings = []
    for r, h in prof:
        rings.append([bm.verts.new(frame.p(r * math.cos(2 * math.pi * k / sides), r * math.sin(2 * math.pi * k / sides),
                                           h)) for k in range(sides)])
    new = []
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            j = (k + 1) % sides
            new.append(bm.faces.new([a[k], a[j], b[j], b[k]]))
    if cap0:
        new.append(bm.faces.new(rings[0][::-1]))
    if cap1:
        new.append(bm.faces.new(rings[-1]))
    return part.tag(new)


def rrect(hw, hh, r, k, cv=0.0):
    """Rounded rectangle (counter-clockwise) centred at (0, cv): k steps per corner."""
    r = max(1e-5, min(r, hw - 1e-5, hh - 1e-5))
    pts = []
    for sx, sy, a0 in ((1, 1, 0.0), (-1, 1, 90.0), (-1, -1, 180.0), (1, -1, 270.0)):
        ccx, ccy = sx * (hw - r), cv + sy * (hh - r)
        for i in range(k + 1):
            a = math.radians(a0 + 90.0 * i / k)
            pts.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
    return pts


def fillet(poly, d, k, idx=None):
    """Round the polygon corners (at vertices idx, None = all): a quadratic curve through the corner,
    tangent points at d from the corner (no more than 0.45 of the adjacent sides), k steps.
    """
    n = len(poly)
    out = []
    for i, p in enumerate(poly):
        if idx is not None and i not in idx:
            out.append(p)
            continue
        a, b = poly[i - 1], poly[(i + 1) % n]
        da, db = math.hypot(a[0] - p[0], a[1] - p[1]), math.hypot(b[0] - p[0], b[1] - p[1])
        dd = min(d, 0.45 * da, 0.45 * db)
        t1 = (p[0] + (a[0] - p[0]) * dd / da, p[1] + (a[1] - p[1]) * dd / da)
        t2 = (p[0] + (b[0] - p[0]) * dd / db, p[1] + (b[1] - p[1]) * dd / db)
        for j in range(k + 1):
            t = j / k
            out.append(tuple((1 - t) ** 2 * t1[c] + 2 * (1 - t) * t * p[c] + t * t * t2[c] for c in (0, 1)))
    return out


def inset(poly, d):
    """Move the polygon sides (counter-clockwise) inward by d."""
    n = len(poly)
    lines = []
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        L = math.hypot(x1 - x0, y1 - y0)
        lines.append(((x0 - (y1 - y0) / L * d, y0 + (x1 - x0) / L * d), (x1 - x0, y1 - y0)))
    out = []
    for i in range(n):
        (p, dp), (q, dq) = lines[i - 1], lines[i]
        den = dp[0] * dq[1] - dp[1] * dq[0]
        if abs(den) < 1e-14:
            out.append(q)
            continue
        t = ((q[0] - p[0]) * dq[1] - (q[1] - p[1]) * dq[0]) / den
        out.append((p[0] + dp[0] * t, p[1] + dp[1] * t))
    return out


def bend(pts, d, k):
    """Space polyline -> radius bends (sheet clamp): a quadratic curve at each inner point, tangent
    points at d from the corner.
    """
    v = [Vector(p) for p in pts]
    out = [v[0]]
    for i in range(1, len(v) - 1):
        a, p, b = v[i - 1], v[i], v[i + 1]
        dd = min(d, 0.45 * (a - p).length, 0.45 * (b - p).length)
        t1, t2 = p + (a - p).normalized() * dd, p + (b - p).normalized() * dd
        for j in range(k + 1):
            t = j / k
            out.append((1 - t) ** 2 * t1 + 2 * (1 - t) * t * p + t * t * t2)
    out.append(v[-1])
    return [tuple(q) for q in out]


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, as in M38, M45, M70)."""
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


def knurl_poly(ca, cb, r, n, depth):
    """Knurled circle: 2n vertices, every other one sunk by depth (counter-clockwise)."""
    return [(ca + (r - depth * (k % 2)) * math.cos(math.pi * k / n), cb + (r - depth * (k % 2)) * math.sin(math.pi * k / n))
            for k in range(2 * n)]


def peanut(R, e, w, k):
    """Palm III rocker, a figure eight in the face plane (u, v): two lobes of radius R centred at
    KEY_V +- e, a waist of half-width w in the middle; k steps per lobe (counter-clockwise).
    """
    pts = [(w, KEY_V)]
    for i in range(k + 1):
        a = math.radians(-30.0 + 240.0 * i / k)
        pts.append((R * math.cos(a), KEY_V + e + R * math.sin(a)))
    pts.append((-w, KEY_V))
    for i in range(k + 1):
        a = math.radians(150.0 + 240.0 * i / k)
        pts.append((R * math.cos(a), KEY_V - e + R * math.sin(a)))
    return pts


# --- board -------------------------------------------------------------------------------------
def build_plate(spec):
    lod = spec["lod"]
    parts = []
    pl = P("plate", "plate")
    fs = g.box(pl, PX0, PX1, PY0, PY1, FOOT_H, ZB, **({"r": 0.0012, "seg": 1} if lod == 0 else {}))
    for ax in (0, 1):
        for sg in (-1, 1):
            retag(pl, fs, ax, sg, "plate_edge", 0.9)
    retag(pl, fs, 2, -1, "inner")
    parts.append(pl)
    if lod == 0:
        for i, (x, y) in enumerate(((PX0 + 0.013, PY0 + 0.013), (PX1 - 0.013, PY0 + 0.013),
                                    (PX0 + 0.013, PY1 - 0.013), (PX1 - 0.013, PY1 - 0.013))):
            ft = P("foot%d" % i, "rubber", uv_name="foot", uv_origin=(x, y, 0.0))
            g.cyl(ft, (x, y, FOOT_H / 2 + 0.0001), "z", 0.0060, FOOT_H, 6, r2=0.0052)
            parts.append(ft)
        # inventory label
        lx, ly = LABEL_C
        parts.append(boxp("label", "label", lx - LABEL_W / 2, lx + LABEL_W / 2, ly - LABEL_H / 2, ly + LABEL_H / 2,
                          ZB - 0.0001, ZB + 0.0002))
        # two extra drilled holes: a dark circle with a chamfer
        for i, (x, y) in enumerate(HOLES):
            hl = P("hole%d" % i, "inner", uv_name="hole", uv_origin=(x, y, ZB))
            vs = [hl.bm.verts.new((x + 0.0016 * math.cos(2 * math.pi * k / 10), y + 0.0016 * math.sin(2 * math.pi * k / 10),
                                   ZB + 0.00005)) for k in range(10)]
            hl.tag([face(hl, vs, (0, 0, 1))])
            parts.append(hl)
    return parts


# --- dock ---------------------------------------------------------------------------------------
def base_outline(inset_, k, rounded=False):
    """Outline of the dock base: straight sides and rear, a convex front (an arc through the apex);
    rounded - the corners are rounded (rear 4 mm, the side-to-arc transition soft).
    """
    hw = BW / 2 - inset_
    yf, ya, yb = BY0 + inset_ * 0.5, BAPEX + inset_, BY1 - inset_ * 0.25
    pts = [(CX - hw, yb), (CX - hw, yf)]
    for i in range(1, k):
        s = -1 + 2 * i / k
        pts.append((CX + hw * s, yf + (ya - yf) * (1 - s * s)))
    pts += [(CX + hw, yf), (CX + hw, yb)]
    if rounded:
        n = len(pts)
        pts = fillet(pts, 0.0040, 2, idx=(0, n - 1))
        n = len(pts)
        pts = fillet(pts, 0.0060, 2, idx=(3, n - 4))
    return pts[::-1]


# base sections (edge inset, height above the board): vertical lip, slope, rounded top
# the last ring is a flat strip: normals at the edge of the large top face do not sag (otherwise
# dark smoothing stripes run along it)
BASE_RINGS = [(0.0, 0.0), (0.0, BASE_LIP - 0.0007), (0.00035, BASE_LIP), (BASE_IN - 0.0006, BASE_TOP - 0.0005),
              (BASE_IN + 0.0010, BASE_TOP), (BASE_IN + 0.0018, BASE_TOP)]


def build_cradle(spec):
    lod, n, seg = spec["lod"], spec["sides"], spec["seg"]
    parts = []
    base = P("cradle_base", "cradle")
    if lod == 0:
        fs = loft(base, [(base_outline(d, 12, rounded=True), ZB + h) for d, h in BASE_RINGS])
    else:
        fs = loft(base, [(base_outline(0.0, 6), ZB), (base_outline(0.0, 6), ZB + BASE_LIP),
                         (base_outline(BASE_IN, 6), ZB + BASE_TOP)])
    retag(base, fs, 2, -1, "inner")
    parts.append(base)
    # pocket: front wall and sides around the bottom of the PDA
    col = P("cradle_collar", "cradle")
    g.box(col, -COL_U, COL_U, COL_V[0], COL_V[1], COL_N[0], COL_N[1], frame=FRAME,
          **({"r": 0.0025, "seg": 2} if lod == 0 else {}))
    parts.append(col)
    if lod == 0:
        # dark gap between the PDA and the pocket
        gp = P("collar_gap", "inner")
        vv = COL_V[1] + 0.0001
        o = [(-PW / 2 - 0.0010, -PT - 0.0010), (PW / 2 + 0.0010, -PT - 0.0010), (PW / 2 + 0.0010, 0.0010),
             (-PW / 2 - 0.0010, 0.0010)]
        i_ = [(-PW / 2 + 0.0004, -PT + 0.0004), (PW / 2 - 0.0004, -PT + 0.0004), (PW / 2 - 0.0004, -0.0004),
              (-PW / 2 + 0.0004, -0.0004)]
        vo = [gp.bm.verts.new(FRAME.p(u, vv, nn)) for u, nn in o]
        vi = [gp.bm.verts.new(FRAME.p(u, vv, nn)) for u, nn in i_]
        gp.tag([face(gp, [vo[j], vo[(j + 1) % 4], vi[(j + 1) % 4], vi[j]], FRAME.v) for j in range(4)])
        parts.append(gp)

    # support: a sloped back and a wedge to the rear of the base (y-z profile, extruded along x)
    def yz(v, nn):
        q = FRAME.p(0.0, v, nn)
        return (q.y, q.z)
    v0, v1 = REST_V
    n0, n1 = REST_N
    prof = [yz(v0, n1), yz(v1 - 0.003, n1), yz(v1, n1 - 0.003), yz(v1, n0 + 0.002), yz(v1 - 0.004, n0),
            (BY1 - 0.010, ZB + BASE_TOP + 0.012), (BY1 - 0.010, ZB + BASE_TOP - 0.004), yz(v0, n0)]
    rest = P("cradle_rest", "cradle")
    fs = g.prism(rest, prof, (1, 2), CX - REST_U, CX + REST_U)
    if lod == 0:
        # chamfer on the support ends
        rest.bm.normal_update()
        caps = [f for f in fs if abs(f.normal.x) > 0.99]
        g.bevel(rest.bm, list({e for f in caps for e in f.edges}), 0.0010, 2)
    parts.append(rest)
    # sync button: a dark ring socket and a dome pusher with the icon
    hx, hy = HS
    zt = ZB + BASE_TOP
    ring = P("hs_ring", "keyring")
    g.cyl(ring, (hx, hy, zt + 0.0002), "z", HS_D / 2 + 0.0016, 0.0008, 20 if lod == 0 else n)
    parts.append(ring)
    cap = P("hs_cap", "hotsync")
    if lod == 0:
        lathe(cap, [(HS_D / 2, 0.0), (HS_D / 2, 0.0021), (HS_D / 2 - 0.0007, 0.0029), (HS_D / 2 - 0.0020, 0.0033)], 20,
              g.Frame((hx, hy, zt + 0.0001), (1, 0, 0), (0, 1, 0), (0, 0, 1)))
    else:
        g.cyl(cap, (hx, hy, zt + 0.0017), "z", HS_D / 2, HS_TOP - zt - 0.0002, n, r2=HS_D / 2 - 0.0006)
    parts.append(cap)
    # cable exit at the rear: a ribbed rubber boot
    boot = P("cable_boot", "black")
    if lod == 0:
        lathe(boot, [(0.0045, 0.0), (0.0045, 0.0035), (0.0039, 0.0042), (0.0039, 0.0058), (0.0033, 0.0065),
                     (0.0033, 0.0080), (CABLE_R + 0.0004, 0.0110), (CABLE_R + 0.0004, BOOT_L)], 10,
              axis_frame((CX, BOOT_Y0, BOOT_Z), (0, 1, 0)))
    else:
        g.cyl(boot, (CX, BOOT_Y0 + BOOT_L / 2, BOOT_Z), "y", 0.0042, BOOT_L, n // 2 + 2, r2=CABLE_R + 0.0005)
    parts.append(boot)
    return parts


def clamp_paths():
    """Two aluminium clamps: a foot on the board, a rise along the base side, a bend onto the top."""
    out = []
    zt = ZB + BASE_TOP
    for s in (-1, 1):
        xe = CX + s * BW / 2
        xt = CX + s * (BW / 2 - BASE_IN)
        hc = CLAMP_T / 2
        pts = [(xe + s * CLAMP_FOOT, CLAMP_Y, ZB + hc), (xe + s * hc, CLAMP_Y, ZB + hc),
               (xe + s * hc, CLAMP_Y, ZB + BASE_LIP + hc), (xt + s * hc * 0.6, CLAMP_Y, zt + hc),
               (xt - s * 0.007, CLAMP_Y, zt + hc)]
        out.append((s, xe, pts))
    return out


def build_clamps(spec):
    lod = spec["lod"]
    parts = []
    for s, xe, pts in clamp_paths():
        c = P("clamp%d" % (s > 0), "alu", uv_name="clamp%d" % (s > 0))
        g.sweep(c, bend(pts, 0.0020, 1) if lod == 0 else pts, (0, 1, 0), CLAMP_T / 2, CLAMP_W / 2)
        parts.append(c)
        if lod == 0:
            # M3 screw with a dome head, a cross slot and a washer
            sx_ = xe + s * (CLAMP_FOOT - 0.0045)
            z0 = ZB + CLAMP_T
            fr = g.Frame((sx_, CLAMP_Y, z0), (1, 0, 0), (0, 1, 0), (0, 0, 1))
            ws = P("washer%d" % (s > 0), "screw", uv_name="washer", uv_origin=(sx_, CLAMP_Y, z0))
            lathe(ws, [(0.0036, 0.0), (0.0036, 0.0003), (0.0020, 0.0003)], 8, fr, cap1=False)
            parts.append(ws)
            sc = P("screw%d" % (s > 0), "screw", uv_name="screw", uv_origin=(sx_, CLAMP_Y, z0))
            lathe(sc, [(0.0027, 0.0002), (0.0027, 0.0008), (0.0023, 0.0014), (0.0013, 0.0018)], 10, fr)
            parts.append(sc)
            sl = P("slot%d" % (s > 0), "black", uv_name="slot", uv_origin=(sx_, CLAMP_Y, z0))
            zs = z0 + 0.0018
            g.box(sl, sx_ - 0.0016, sx_ + 0.0016, CLAMP_Y - 0.0003, CLAMP_Y + 0.0003, zs - 0.0003, zs + 0.0001)
            g.box(sl, sx_ - 0.0003, sx_ + 0.0003, CLAMP_Y - 0.0016, CLAMP_Y + 0.0016, zs - 0.0003, zs + 0.0001)
            parts.append(sl)
    return parts


# --- PDA ----------------------------------------------------------------------------------------
def build_pda(spec):
    lod, n, seg = spec["lod"], spec["sides"], spec["seg"]
    F = FRAME
    parts = []
    body = P("pda", "pda")
    if lod == 0:
        # two case halves: rounded face and back edges, the seam at mid-thickness
        loft(body, [(rrect(PW / 2 - d, PH / 2 - d, PDA_RC - d, 3, cv=PH / 2), nn) for nn, d in PDA_PROF], frame=F,
             band_reg={k: "keyring" for k in PDA_SEAM})
    else:
        loft(body, [(rrect(PW / 2 - d, PH / 2 - d, PDA_RC - d, 2, cv=PH / 2), nn) for nn, d in PDA_PROF1], frame=F)
    parts.append(body)
    # dark window frame, LCD (ozl_screen, own texture), input field
    parts.append(boxp_f("pda_window", "bezel", -WIN_U, WIN_U, WIN_V[0], WIN_V[1], -0.0004, 0.0003))
    lcd = P("lcd", "lcd", group=SEL_SCREEN, section="screen")
    g.quad(lcd, [F.p(-LCD_U, LCD_V[0], 0.0005), F.p(LCD_U, LCD_V[0], 0.0005), F.p(LCD_U, LCD_V[1], 0.0005),
                 F.p(-LCD_U, LCD_V[1], 0.0005)])
    lcd.glass_frame = (F, -LCD_U, LCD_U, LCD_V[0], LCD_V[1])
    parts.append(lcd)
    silk = P("silk", "silk")
    g.quad(silk, [F.p(-LCD_U, SILK_V[0], 0.0005), F.p(LCD_U, SILK_V[0], 0.0005), F.p(LCD_U, SILK_V[1], 0.0005),
                  F.p(-LCD_U, SILK_V[1], 0.0005)])
    parts.append(silk)
    # buttons: dark sockets and dome pushers; a figure-eight rocker in the middle
    for i, u in enumerate(KEY_U):
        fk = g.Frame(F.p(u, KEY_V, 0.0), F.u, F.v, F.n)
        if lod == 0:
            rg = P("key_ring%d" % i, "keyring", uv_name="key_ring", uv_origin=F.p(u, KEY_V, 0.0))
            lathe(rg, [(0.0064, -0.0002), (0.0051, 0.0006)], 14, fk, cap1=False)
            parts.append(rg)
            kc = P("key%d" % i, "keys")
            lathe(kc, [(0.0050, 0.0002), (0.0050, 0.0013), (0.0038, 0.0020)], 14, fk)
        else:
            kc = P("key%d" % i, "keys")
            g.cyl(kc, (u, KEY_V, 0.0010), "z", 0.0050, 0.0016, 8, r2=0.0046, frame=F)
        parts.append(kc)
    if lod == 0:
        rr = P("rocker_ring", "keyring")
        g.prism(rr, peanut(ROCK_R + 0.0014, ROCK_E, ROCK_W + 0.0012, 7), (0, 1), -0.0002, 0.0004, frame=F)
        parts.append(rr)
        rk = P("rocker", "keys")
        loft(rk, [(peanut(ROCK_R, ROCK_E, ROCK_W, 7), 0.0), (peanut(ROCK_R, ROCK_E, ROCK_W, 7), 0.0013),
                  (peanut(ROCK_R - 0.0006, ROCK_E, ROCK_W - 0.0006, 7), 0.0020)], frame=F)
    else:
        rk = P("rocker", "keys")
        g.prism(rk, peanut(ROCK_R, ROCK_E, ROCK_W, 3), (0, 1), 0.0, 0.0019, frame=F)
    parts.append(rk)
    # power button at the left edge
    pw = P("power", "power")
    g.box(pw, -PW / 2 + 0.0012, -PW / 2 + 0.0058, KEY_V - 0.0045, KEY_V + 0.0045, -0.0004, 0.0010, frame=F,
          **({"r": 0.0005, "seg": 1} if lod == 0 else {}))
    parts.append(pw)
    if lod == 0:
        # IR window on the top end, an empty stylus slot at the rear right, a knurled contrast wheel
        # at the left
        parts.append(boxp_f("ir", "ir", -0.011, 0.011, PH - 0.0006, PH + 0.0004, -0.013, -0.005))
        sh = P("stylus_silo", "inner")
        su, sv, sn_ = PW / 2 - 0.0090, PH + 0.0002, -PT + 0.0045
        g.quad(sh, [F.p(su - 0.0025, sv, sn_ - 0.0025), F.p(su + 0.0025, sv, sn_ - 0.0025),
                    F.p(su + 0.0025, sv, sn_ + 0.0025), F.p(su - 0.0025, sv, sn_ + 0.0025)])
        parts.append(sh)
        wh = P("contrast", "keyring")
        g.prism(wh, knurl_poly(0.088, -0.009, 0.0055, 9, 0.0005), (1, 2), -PW / 2 - 0.0011, -PW / 2 + 0.0007, frame=F)
        parts.append(wh)
        # factory sticker on the back (visible above the support)
        parts.append(boxp_f("sticker", "sticker", -0.017, 0.015, 0.078, 0.099, -PT - 0.00015, -PT + 0.0002))
    return parts


# --- cable, coil, connector ---------------------------------------------------------------------
def cable_path():
    """From the boot to the rear and to the right along the rear edge, one and a half turns of a spiral
    inward (clockwise), the exit over the outer turn in a smooth arc to the connector's strain relief.
    """
    zc = ZB + CABLE_R
    y1 = BOOT_Y0 + BOOT_L
    pts = [(CX, y1 - 0.004, BOOT_Z), (CX, y1 + 0.002, BOOT_Z - 0.0004), (CX + 0.003, y1 + 0.009, ZB + 0.0095),
           (CX + 0.013, BY1 + 0.017, zc), (0.030, COIL_C[1] + COIL_R0 + 0.001, zc)]
    cx, cy = COIL_C
    a0, turns = 95.0, 1.55
    steps = 26
    for i in range(1, steps + 1):
        f = i / steps
        a = math.radians(a0 - 360.0 * turns * f)
        r = COIL_R0 + (COIL_R1 - COIL_R0) * f
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a), zc))
    # exit: over the outer turn, down to the board and straight into the connector's strain relief
    tail_y = DSUB_Y0 + DSUB_L + 0.010
    pts += [(cx - 0.0058, cy - 0.0185, zc + 2 * CABLE_R - 0.0003), (DSUB_C - 0.0012, tail_y + 0.0070, DSUB_ZC - 0.0003),
            (DSUB_C, tail_y + 0.003, DSUB_ZC), (DSUB_C, tail_y, DSUB_ZC)]
    return pts


def build_cable(spec):
    lod = spec["lod"]
    pts = cable_path()
    if lod == 0:
        pts = spline(pts[:6], 2)[:-1] + pts[6:-5] + spline(pts[-5:], 2)
    else:
        pts = pts[:5] + pts[5:-4:4] + pts[-4:]
    cb = P("cable", "cable")
    # 10 sides: the angle between faces is 36 degrees, below the smoothing threshold of 40 (kexport,
    # krender), so the cable looks round
    g.pipe(cb, pts, CABLE_R, 10 if lod == 0 else 5)
    parts = [cb]
    if lod == 0:
        # coil clamp: a black tape across two turns and a lock
        cx, cy = COIL_C
        a = math.radians(140.0)
        ux, uy = math.cos(a), math.sin(a)
        r_mid = (COIL_R0 + COIL_R1 * 0.6) / 2 + 0.002
        tie = P("tie", "black")
        c0 = Vector((cx + r_mid * ux, cy + r_mid * uy, 0.0))
        span = 0.0085
        pts_t = [c0 + Vector((ux, uy, 0)) * (-span) + Vector((0, 0, ZB + 0.0003)),
                 c0 + Vector((ux, uy, 0)) * (-span) + Vector((0, 0, ZB + 2 * CABLE_R + 0.0004)),
                 c0 + Vector((ux, uy, 0)) * span + Vector((0, 0, ZB + 2 * CABLE_R + 0.0004)),
                 c0 + Vector((ux, uy, 0)) * span + Vector((0, 0, ZB + 0.0003))]
        g.sweep(tie, bend([tuple(p) for p in pts_t], 0.0012, 2), (-uy, ux, 0), 0.0005, 0.0018)
        parts.append(tie)
        lk = P("tie_lock", "black")
        q = c0 + Vector((ux, uy, 0)) * (span * 0.2)
        g.box(lk, q.x - 0.0022, q.x + 0.0022, q.y - 0.0022, q.y + 0.0022, ZB + 2 * CABLE_R + 0.0004,
              ZB + 2 * CABLE_R + 0.0030)
        parts.append(lk)
    return parts


def hood_poly(d=0.0, r=0.0025, k=2):
    """Outline of the cast DE-9 body (counter-clockwise): wide ears at the flange, then a waist for the
    screw heads and a strain relief toward the cable; d is the inward offset (rounding of the top),
    the corners are rounded.
    """
    x, y0 = DSUB_C, DSUB_Y0
    poly = [(x - 0.0150, y0 + 0.0015), (x + 0.0150, y0 + 0.0015), (x + 0.0150, y0 + 0.0100), (x + 0.0094, y0 + 0.0118),
            (x + 0.0085, y0 + DSUB_L), (x - 0.0085, y0 + DSUB_L), (x - 0.0094, y0 + 0.0118), (x - 0.0150, y0 + 0.0100)]
    if d > 0:
        poly = inset(poly, d)
    return fillet(poly, max(r - d, 0.0006), k) if k else poly


def dshape(d=0.0, k=2):
    """D-shaped shell in the x-z plane (counter-clockwise): wider at the top."""
    x, zc = DSUB_C, DSUB_ZC
    poly = [(x - 0.0078, zc - 0.0030), (x + 0.0078, zc - 0.0030), (x + 0.0090, zc + 0.0030), (x - 0.0090, zc + 0.0030)]
    if d > 0:
        poly = inset(poly, d)
    return fillet(poly, max(0.0014 - d, 0.0005), k) if k else poly


def build_dsub(spec):
    """DE-9 lies flat, facing forward: a cast body with ears and a strain relief, a steel flange with the
    D-shaped shell, an insulator with nine sockets, knurled screws behind the ears, an LED in the cover.
    """
    lod, n = spec["lod"], spec["sides"]
    parts = []
    x, y0 = DSUB_C, DSUB_Y0
    zc = DSUB_ZC
    zt = ZB + DSUB_H
    hood = P("dsub_hood", "hood")
    if lod == 0:
        loft(hood, [(hood_poly(), ZB), (hood_poly(), zt - 0.0018), (hood_poly(0.0007), zt - 0.0005),
                    (hood_poly(0.0018), zt), (hood_poly(0.0026), zt)])
        # grip ribs across the cover
        rb = P("dsub_ribs", "hood")
        for yy in (0.022, 0.027, 0.032):
            yr = y0 + yy
            hw = 0.0094 - (0.0094 - 0.0085) * (yy - 0.0118) / (DSUB_L - 0.0118) - 0.0032
            g.box(rb, x - hw, x + hw, yr - 0.0006, yr + 0.0006, zt - 0.0002, zt + 0.0006)
        parts.append(rb)
    else:
        g.prism(hood, hood_poly(k=0), (0, 1), ZB, zt)
    parts.append(hood)
    fl = P("dsub_flange", "shell")
    g.box(fl, x - 0.0154, x + 0.0154, y0, y0 + 0.0015, zc - 0.00625, zc + 0.00625,
          **({"r": 0.0004, "seg": 1} if lod == 0 else {}))
    parts.append(fl)
    sh = P("dsub_shield", "shell")
    g.prism(sh, dshape(k=2 if lod == 0 else 0), (0, 2), y0 - 0.0060, y0 + 0.0002)
    parts.append(sh)
    # the socket insulator sits slightly ahead of the shell edge - a steel rim remains
    ins = P("dsub_insert", "dsub_face")
    g.prism(ins, dshape(0.0007, k=2 if lod == 0 else 0), (0, 2), y0 - 0.0063, y0 - 0.0030)
    parts.append(ins)
    if lod == 0:
        holes = P("dsub_holes", "inner")
        for zz, xs in ((zc + 0.00142, (-0.00554, -0.00277, 0.0, 0.00277, 0.00554)),
                       (zc - 0.00142, (-0.004155, -0.001385, 0.001385, 0.004155))):
            for xx in xs:
                vs = [holes.bm.verts.new((x + xx + 0.00052 * math.cos(math.pi * k / 3), y0 - 0.0064,
                                          zz + 0.00052 * math.sin(math.pi * k / 3))) for k in range(6)]
                holes.tag([face(holes, vs, (0, -1, 0))])
        parts.append(holes)
    for i, s in enumerate((-1, 1)):
        tx = x + s * THUMB_X
        th = P("thumb%d" % i, "chrome", uv_name="thumb", uv_origin=(tx, y0, zc))
        if lod == 0:
            g.prism(th, knurl_poly(tx, zc, THUMB_R, 8, 0.0004), (0, 2), y0 + 0.0102, y0 + 0.0162)
        else:
            g.cyl(th, (tx, y0 + 0.0132, zc), "y", THUMB_R, 0.0060, 8)
        parts.append(th)
        sc = P("thumb_shaft%d" % i, "chrome", uv_name="thumb_shaft", uv_origin=(tx, y0, zc))
        g.cyl(sc, (tx, y0 + 0.0017, zc), "y", 0.0015, 0.0174, 10 if lod == 0 else 6)
        parts.append(sc)
    # tail: a ribbed strain relief toward the cable
    tl = P("dsub_tail", "hood")
    if lod == 0:
        lathe(tl, [(0.0055, 0.0), (0.0055, 0.0030), (0.0047, 0.0037), (0.0047, 0.0052), (0.0040, 0.0059),
                   (0.0040, 0.0072), (CABLE_R + 0.0005, 0.0108), (CABLE_R + 0.0005, 0.0130)], 10,
              axis_frame((x, y0 + DSUB_L - 0.001, zc), (0, 1, 0)))
    else:
        g.cyl(tl, (x, y0 + DSUB_L + 0.004, zc), "y", 0.0050, 0.008, n // 2 + 2, r2=CABLE_R + 0.0008)
    parts.append(tl)
    # home-made line-activity LED glued into the cover (ozl_lamp)
    ld = P("dsub_led", "led", group=SEL_LAMP)
    lx, ly = LED_P
    fr = g.Frame((lx, ly, zt - 0.0003), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    if lod == 0:
        lathe(ld, [(0.0019, 0.0), (0.0019, 0.0007), (0.0015, 0.0007), (0.0015, 0.0018), (0.0012, 0.0025),
                   (0.0006, 0.0029)], 8, fr)
    else:
        lathe(ld, [(0.0019, 0.0), (0.0015, 0.0018), (0.0006, 0.0029)], 6, fr)
    parts.append(ld)
    return parts


def build_stylus(spec):
    """Palm III stylus: a metal body with a groove by the cap, black tip and cap."""
    lod = spec["lod"]
    sides = 10 if lod == 0 else 6
    a = Vector((STY_A[0], STY_A[1], ZB + 0.0020))
    b = Vector((STY_B[0], STY_B[1], ZB + 0.0020))
    L = (b - a).length
    fr = axis_frame(a, b - a)
    tip = P("stylus_tip", "black")
    lathe(tip, [(0.0002, 0.0), (0.0007, 0.0008), (0.0016, 0.0060), (0.0019, 0.0100)], sides, fr,
          cap0=True, cap1=False)
    body = P("stylus", "chrome")
    if lod == 0:
        lathe(body, [(0.0020, 0.0098), (0.0020, L - 0.0205), (0.0018, L - 0.0200), (0.0018, L - 0.0192),
                     (0.0020, L - 0.0187), (0.0020, L - 0.0158)], sides, fr, cap0=True, cap1=False)
    else:
        lathe(body, [(0.0020, 0.0098), (0.0020, L - 0.0158)], sides, fr, cap0=True, cap1=False)
    cap = P("stylus_cap", "black")
    lathe(cap, [(0.0021, L - 0.0160), (0.0021, L - 0.0025), (0.0018, L - 0.0008), (0.0011, L)], sides, fr,
          cap0=True, cap1=True)
    return [tip, body, cap]


def build_lod(spec):
    parts = build_plate(spec) + build_cradle(spec) + build_clamps(spec) + build_pda(spec) + build_cable(spec) + \
        build_dsub(spec) + build_stylus(spec)
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("BOUNDS lo %s hi %s" % (tuple(round(c, 4) for c in BOUNDS["lo"]),
                                      tuple(round(c, 4) for c in BOUNDS["hi"])))
    return parts


def collision():
    """Three convex parts: board, dock with the PDA, connector; the cable and stylus have no collision.
    Mass is the item's weight in the mod, 0.8 kg.
    """
    plate = kx.box_pts(PX0, PX1, PY0, PY1, 0.0, ZB)
    F = FRAME
    cradle = [(x, y, ZB) for x, y in base_outline(0.0, 6)]
    cradle += [(x, y, ZB + BASE_TOP) for x, y in base_outline(BASE_IN, 6)]
    cradle += [tuple(F.p(u, v, nn)) for u in (-PW / 2, PW / 2) for v in (0.0, PH) for nn in (-PT, 0.0)]
    cradle += [tuple(F.p(u, REST_V[1], REST_N[0])) for u in (-REST_U, REST_U)]
    dsub = kx.box_pts(DSUB_C - 0.0155, DSUB_C + 0.0155, DSUB_Y0 - 0.006, DSUB_Y0 + DSUB_L, ZB, ZB + DSUB_H)
    comps = [(plate, kx.PEN + r"\plastic.rvmat"), (cradle, kx.PEN + r"\plastic.rvmat"),
             (dsub, kx.PEN + r"\plastic.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    zc = hi[2] / 2
    memory = {
        # inventory preview camera: front-left and from above (invView = camera position)
        "invView": [(-0.30, -0.44, 0.36)],
        "ce_center": [(0.0, 0.0, zc)],
        "ce_radius": [(0.12, 0.0, zc)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


SHOTS = [
    ("front", (-0.20, -0.46, 0.28), (0.0, 0.0, 0.055), 55),
    ("screen", (-0.07, -0.26, 0.17), (CX, -0.004, 0.075), 45),
    ("plug", (0.20, -0.21, 0.15), (0.052, -0.010, 0.012), 50),
    ("right", (0.42, -0.24, 0.30), (0.03, 0.005, 0.03), 40),
    ("back", (0.30, 0.44, 0.32), (0.0, 0.01, 0.05), 40),
    ("top", (0.02, -0.08, 0.52), (0.0, 0.0, 0.0), 40),
]

# --look preview: overall view, PDA face, connector; work look: overall view and PDA face
M.look_shots = (3, 2)
M.run(build_lod, collision, SHOTS, row_step=0.26, row_shot=((0.13, -0.95, 0.36), (0.13, 0, 0.07)))
