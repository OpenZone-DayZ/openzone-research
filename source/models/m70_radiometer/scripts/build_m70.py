"""M70 - Dosimeter-radiometer (OZL_Tool_Radiometer): a module of the "Anomaly" line - a portable 2x2
item, it stands in slot OZL_Tool2 of the line's packer (M03, M09) and is visible on its shelf through
a proxy (slot 2 = module 2 of the line). Variant B: a laboratory radiometer with a lead house.

    blender --background --python build_m70.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (the console face, the LCD display
"off" and the "working" frames, the radiation hazard sign, the inventory plate, the tape with a sample
number).

Target: a 1980s desktop radiometer (like the "Beta", RKB4-1eM) with a scale or a display, next to it a
lead house with a cuvette for the sample; ~0.20 x 0.10 x 0.22 m; a module is no larger than ~0.2 x
0.2 m by its base and up to ~0.25 m high (the module_N platform).

Reference and sizes:
- the "Beta" beta-radiation radiometer set (state register 11076-87, the Etalon Pilot Plant, Kyiv,
  1987): a console with a digital LCD display, a remote unit with an end-window counter SBT-10A, a
  lead house in a steel casing, cuvettes, a power supply unit;
- the lead house is 19.0 kg per the type description 11076-87 (found via search results; the file
  itself did not open). There are no dimensions in the available sources: from a photo (the detector
  unit ~90 mm as a measure) the house face is ~160 mm and the height ~200 mm, from another photo the
  depth is almost equal to the width. A mass check: a casing of 160 x 165 x 200 mm and ~10 mm of lead
  give ~18-20 kg - consistent;
- console: "a cast aluminium housing, roughly the size of the 'Pripyat'" (a forum thread, from search
  results); the RKS-20.03 "Pripyat" is 145 x 73 x 37 mm, 0.25 kg. In a photo the "Beta" console is
  slightly wider (length : width ~1.86) - the model is 145 x 78 x 34 mm. The face layout follows a
  photo: the display on top, two buttons staggered below it, the mode table below, the cable
  connector on the top end, an LED in the top left corner; the housing corners are rounded in plan
  (~12 mm), the cast housing is of two halves - a step of the joint on the side;
- cuvette: a black plastic tray with a flanged rim and sloped walls (a photo) for the window of the
  SBT-10A counter (~88 x 68 mm per pocketmagic.net); the model is 82 x 60 x 20 mm - it stands on the
  roof of the house beside the console.

Module layout. The house and the console do not fit side by side on the shelf (0.16 + 0.08 > 0.2 m),
so the console lies on the roof of the house with the display towards the back wall (readable from the
front), the cuvette with a sample beside it; the cable from the console connector (a knurled union nut,
a rubber tail) sags behind the house, goes around the back left corner and enters the gland on the
left side (a washer, a nut, a rubber tail; the detector unit is inside the house). Overall ~0.19 x
0.21 x 0.24 m (with the cable). The house door is the face of the module: two removable hinges on the
right (in the photo the door is swung open to the right; two links, with a leaf on the door and on the
side), a turn latch on the left (a rosette, a washer, a wing nut), four screws at the door corners
(holding the lead insert, per the photo); closed (doors have a single position). On the roof behind
the cuvette is a spare 9 V battery ("Krona", as for the "Pripyat") - a vanilla DayZ item as a proxy.

Shared instruments and modules: used but intact - hammered enamel with small chips down to a red-brown
primer (photo), dust on the roof, almost no rust. No faction colour. Marks: a radiation hazard sign on
the door, the digits of the mode table and display, an aluminium inventory plate with a stamped
number, a hand-written sample number on the cuvette tape. The console face has no device name - an
empty frame is in its place.

Detailing: "dayz" look; the console housing and the cuvette are rounded shapes; the buttons, LED,
screws, rivets, hinges, latch, connector and gland are turned profiles; rubber feet under the bottom
(the house sits 4 mm above the shelf); the cable is a smooth curve (a B-spline, a turn at a joint of
no more than 20 degrees, 10 faces - round rather than hexagonal pipe). "Working" is a loop: the LCD
display is a section of its own, lcd (like the M16 screen), with frames of readings (decal_lcd_on.png
is frame 0, decal_lcd_f01..f07 come from make_decals.py), the counting LED blinks (ozl_lamp_work,
atlas _on). The device has no moving parts - no bones.
LODs (a small item): near and middle (~25 %: no screws, rivets, plate, tape, knurling, washers;
simpler rounding and cable), no far one.

Blender axes: X is width, Y is depth (the front face is -Y), Z is up. The origin is the centre of the
bottom: this is how the module stands on the module_N proxy point (autocenter = 0 in Geometry).
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
import kvanilla as kv  # noqa: E402
from mathutils import Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m --------------------------------------------------------------------------------
# lead house
X0, X1 = -0.080, 0.080
Y0, Y1 = -0.0825, 0.0825
HH = 0.200
FOOT_H = 0.004                  # rubber feet: the bottom of the house is 4 mm above the shelf
FEET = [(sx * 0.064, sy * 0.066) for sx in (-1, 1) for sy in (-1, 1)]
DOOR_T = 0.010
YB = Y0 + DOOR_T                # body face behind the door
R_BOX, R_DOOR = 0.006, 0.004
SIGN = (0.0, 0.130)             # sticker on the door (x, z)
SIGN_D = 0.052
LATCH = (X0 + 0.016, 0.110)     # turn latch (x, z)
HINGES = (0.045, 0.155)         # hinge centres along z
HINGE_AX = (X1 + 0.0010, Y0 + 0.0028)           # hinge axis (x, y)
DOOR_SCREWS = [(sx * 0.066, z) for z in (0.016, 0.184) for sx in (-1, 1)]
GLAND = (0.052, 0.170)          # cable entry on the left side (y, z)
PLATE = (0.0, 0.122)            # plate on the right side (y, z)
PLATE_W, PLATE_H = 0.040, 0.024
# console on the roof
PW, PL, PT = 0.078, 0.145, 0.034
PX, PY = -0.034, 0.003          # console centre
ZP = HH + PT                    # console face
P_RC = 0.012                    # corner rounding in plan
P_TOP = 0.003                   # rounding of the face edge
P_STEP = 0.0006                 # step at the joint of the housing halves
LCD_C, LCD_W, LCD_H = 0.0475, 0.054, 0.019      # display centre along y from the face centre, glass
BTN = [(-0.017, 0.014), (0.017, 0.022)]        # "mode" and "start" buttons (x, y from the face centre)
LED = (-0.026, 0.066)
CONN_X = -0.020                 # cable connector on the top end
CONN_Z = HH + PT * 0.5
# cuvette on the roof: the rim top is 60 x 82, the bottom is 3 mm smaller on each side (wall slope)
CX0, CX1 = 0.014, 0.074
CY0, CY1 = -0.052, 0.030
TCX, TCY = (CX0 + CX1) / 2, (CY0 + CY1) / 2
T_HW, T_HL = (CX1 - CX0) / 2, (CY1 - CY0) / 2
CZ_SOIL, CZ_TOP = HH + 0.014, HH + 0.020
TAPE_W, TAPE_H = 0.030, 0.011
TAPE_Z = HH + 0.0095
CABLE_R = 0.0026

LOD_SPECS = [
    dict(lod=0, sides=12, seg=2),
    dict(lod=1, sides=8, seg=1),
]

REGIONS = {
    "hammer": ("hammer", 1.0), "door": ("door", 1.2), "inner": ("inner", 0.05), "hinge": ("hinge", 1.5),
    "knob": ("knob", 1.5), "pult": ("pult", 1.6), "bezel": ("bezel", 1.5),
    "lamp": ("lamp", 1.0), "chrome": ("chrome", 1.2), "screw": ("screw", 1.5), "plate": ("plate", 2.0),
    "tray": ("tray", 1.0), "soil": ("soil", 1.2), "tape": ("tape", 3.0), "cable": ("cable", 0.8),
    "rubber": ("rubber", 0.8),
}


def wdecal(name):
    return os.path.join(WORK, name)


# tape on the sloped wall of the cuvette: a region of its own, so no range
_T_SLOPE = math.atan2(0.0022, 0.017)
PANEL_DEC = (wdecal("decal_panel.png"), "z", 1, ("x", "y"), (PX, PY), (PW, PL), (ZP - 0.002, ZP + 0.0035))
SIGN_DEC = (wdecal("decal_sign.png"), "y", -1, ("x", "z"), SIGN, (SIGN_D, SIGN_D), (Y0 - 0.002, Y0 + 0.003))
PLATE_DEC = (wdecal("decal_plate.png"), "x", 1, ("y", "z"), PLATE, (PLATE_W, PLATE_H), (X1, X1 + 0.002))
TAPE_DEC = (wdecal("decal_tape.png"), "y", -1, ("x", "z"), (TCX, TAPE_Z), (TAPE_W, TAPE_H * math.cos(_T_SLOPE)),
            None)

# worn, small chips, almost no rust (it stands in a laboratory)
LIT = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# the hammered enamel of the house is grey-blue, chips down to a red-brown primer
HAMMER = dict(color=kmats.lin((134, 142, 146)), under=kmats.lin((126, 50, 38)), seed=2.6, gloss=0.34, spec=0.26,
              chip=(0.48, 0.54), rust=(0.92, 0.96), rust_low=0.10, floor_z=0.0, dust=0.40, grime=0.55)


def mat_hammer(mat, origin, **kw):
    """Hammered enamel (from M06, with finer dimples and weaker relief - for an item of 0.2 m): over painted
    metal, small dimples (dark rims, light bottoms) and relief in the normals."""
    outs = kmats.build_paint(mat, origin, **kw)
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    vec, sep = t.coords(origin, 17.0)
    cells = t.noise(vec, 320.0, 2.0, 0.40)
    pit = t.maprange(cells, 0.38, 0.62, 0.0, 1.0)
    col = kmats.sock(mat, outs["color"])
    col = t.mixc(t.math("MULTIPLY", pit, 0.20), col, tuple(min(1.0, c * 1.22) for c in kw["color"][:3]) + (1,))
    col = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", 1.0, pit), 0.16), col,
                 tuple(c * 0.74 for c in kw["color"][:3]) + (1,))
    h = outs["height"]
    hh = t.math("ADD", kmats.sock(mat, h) if not isinstance(h, (int, float)) else h, t.math("MULTIPLY", pit, 0.08))
    return dict(outs, color=kmats.Tree.ref(col), height=kmats.Tree.ref(hh))


def mat_soil(mat, origin, **kw):
    """Sample in the cuvette - dry soil: small light and dark grains over even plastic."""
    outs = kmats.build_plastic(mat, origin, **kw)
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    vec, sep = t.coords(origin, 23.0)
    col = kmats.sock(mat, outs["color"])
    dark = t.step(t.noise(vec, 900.0, 1.0, 0.5), 0.62, 0.66)
    light = t.step(t.noise(vec, 700.0, 1.0, 0.5), 0.66, 0.70)
    col = t.mixc(t.math("MULTIPLY", dark, 0.7), col, kmats.lin((44, 38, 32)))
    col = t.mixc(t.math("MULTIPLY", light, 0.6), col, kmats.lin((170, 156, 128)))
    hh = t.math("SUBTRACT", t.math("MULTIPLY", light, 0.15), t.math("MULTIPLY", dark, 0.15))
    return dict(outs, color=kmats.Tree.ref(col), height=kmats.Tree.ref(hh))


KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "hammer": (mat_hammer, HAMMER),
    "door": (mat_hammer, dict(HAMMER, seed=3.4, decal_items=[SIGN_DEC])),
    "inner": ("flat", dict(color=kmats.lin((26, 27, 28)), gloss=0.1, spec=0.05)),
    # the hinges were painted together with the house, the enamel on them is thinner and darker, worn off
    # the links
    "hinge": ("paint", dict(HAMMER, color=kmats.lin((112, 118, 122)), under=kmats.lin((92, 90, 86)), seed=5.2,
                            chip=(0.50, 0.58))),
    "knob": ("plastic", dict(color=kmats.lin((24, 23, 22)), seed=5.8, gloss=0.42, spec=0.32, dust=0.10, grime=0.15,
                             scuff=(0.74, 0.84))),
    # console: cast aluminium in light grey enamel, chips down to metal
    "pult": ("paint", dict(color=kmats.lin((176, 180, 180)), under=kmats.lin((150, 152, 150)), seed=6.6,
                           gloss=0.34, spec=0.26, chip=(0.60, 0.67), rust=(0.99, 1.0), rust_low=0.0, floor_z=HH,
                           dust=0.22, grime=0.45, decal_items=[PANEL_DEC])),
    "bezel": ("plastic", dict(color=kmats.lin((40, 42, 42)), seed=6.9, gloss=0.40, spec=0.30, dust=0.08, grime=0.10,
                              scuff=(0.85, 0.95))),
    "lamp": ("flat", dict(color=kmats.lin((84, 22, 18)), gloss=0.85, spec=0.8)),
    "lamp_on": ("flat", dict(color=kmats.lin((255, 60, 36)), gloss=0.85, spec=0.8)),
    # nickel-plated connector, nuts, latch rosette
    "chrome": ("steel", dict(seed=7.2, tone=0.62, along="y", gloss=0.65, spec=0.75, dust=0.12, grime=0.25)),
    # galvanized screws and rivets: darker than nickel
    "screw": ("steel", dict(seed=7.6, tone=0.46, along="z", gloss=0.50, spec=0.60, dust=0.15, grime=0.35)),
    "plate": ("paint", dict(LIT, color=kmats.lin((188, 190, 186)), gloss=0.45, spec=0.45, decal_items=[PLATE_DEC])),
    "tray": ("plastic", dict(color=kmats.lin((22, 22, 23)), seed=8.1, gloss=0.32, spec=0.22, dust=0.30, grime=0.25,
                             scuff=(0.74, 0.84))),
    "soil": (mat_soil, dict(color=kmats.lin((98, 86, 70)), seed=8.6, gloss=0.08, spec=0.04, dust=0.0, grime=0.0,
                            mottle=0.20, scuff=(0.99, 1.0))),
    "tape": ("paint", dict(LIT, color=kmats.lin((222, 210, 168)), gloss=0.2, spec=0.1, decal_items=[TAPE_DEC])),
    "cable": ("plastic", dict(color=kmats.lin((196, 196, 190)), seed=9.2, gloss=0.28, spec=0.18, dust=0.25,
                              grime=0.40, scuff=(0.85, 0.95))),
    "rubber": ("plastic", dict(color=kmats.lin((32, 32, 33)), seed=9.7, gloss=0.22, spec=0.12, dust=0.20, grime=0.25,
                               scuff=(0.85, 0.95))),
})

OBJ, NAME = "m70_radiometer", "ozr_radiometer"
SEL_SCREEN, SEL_LAMP = "ozl_screen", "ozl_lamp_work"
# "Working" state: the display is a section of its own, lcd, with frames of readings (OZL_WorkFx steps
# through them, frames); the counting LED is the _on atlas and blinks (blink). Frame 0 is the base reading
# 0.274.
LCD_FRAMES = ["decal_lcd_on.png"] + ["decal_lcd_f%02d.png" % i for i in range(1, 8)]
LCD_PANEL = dict(off="decal_lcd_off.png", frames=LCD_FRAMES, size=256, gloss=0.6)
ON = dict(remap={"lamp": "lamp_on"}, emissive=(1.0, 1.0, 1.0, 1.0))
# vanilla small item: a spare "Krona" battery lying flat on the roof behind the cuvette
DECOR = [kv.put("battery9v", (0.047, 0.057, HH), **kv.flat(-8))]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL_SCREEN, SEL_LAMP), hidden=(SEL_SCREEN, SEL_LAMP), states={"on": ON},
                 decor=DECOR, panels={"lcd": LCD_PANEL})
P = M.part
BOUNDS = {}


# =============================================================================
# Primitives missing from kgeo
# =============================================================================
def basis(w):
    """A right-handed triple (u, v, w) around axis w: rings go u -> v counter-clockwise when seen from +w."""
    w = Vector(w).normalized()
    a = Vector((1, 0, 0)) if abs(w.x) < 0.9 else Vector((0, 1, 0))
    u = (a - w * a.dot(w)).normalized()
    return u, w.cross(u), w


def loft(part, rings, cap0=True, cap1=True):
    """A shell over rings (all rings have the same number of points; a single-point ring is a pole). The
    rings run counter-clockwise around the run axis; a face looks outwards if the profile goes along the
    outer side from the start of the axis to the end (reversed at a hole). cap0 looks backwards along the
    axis, cap1 forwards; the caps come last in the face list."""
    bm = part.bm
    vr = [[bm.verts.new(Vector(p)) for p in r] for r in rings]
    faces = []
    for a, b in zip(vr, vr[1:]):
        n = max(len(a), len(b))
        for k in range(n):
            q = []
            for v in (a[k % len(a)], a[(k + 1) % len(a)], b[(k + 1) % len(b)], b[k % len(b)]):
                if v not in q:
                    q.append(v)
            if len(q) >= 3:
                faces.append(bm.faces.new(q))
    if cap0 and len(vr[0]) > 2:
        faces.append(bm.faces.new(vr[0][::-1]))
    if cap1 and len(vr[-1]) > 2:
        faces.append(bm.faces.new(vr[-1]))
    bm.normal_update()
    return part.tag(faces)


def lathe(part, c, w, prof, sides, cap0=False, cap1=False, phase=0.0):
    """Solid of revolution: the profile [(radius, height along w)] from the centre c; radius 0 is a pole."""
    u, v, w = basis(w)
    c = Vector(c)
    rings = []
    for r, h in prof:
        if r < 1e-7:
            rings.append([c + w * h])
        else:
            rings.append([c + w * h + (u * math.cos(a) + v * math.sin(a)) * r
                          for a in (2 * math.pi * (k + phase) / sides for k in range(sides))])
    return loft(part, rings, cap0, cap1)


def rrect(cx, cy, hw, hl, rc, nc):
    """Rounded rectangle, counter-clockwise: nc segments per corner (0 gives sharp corners)."""
    if nc <= 0 or rc <= 1e-6:
        return [(cx + hw, cy + hl), (cx - hw, cy + hl), (cx - hw, cy - hl), (cx + hw, cy - hl)]
    rc = min(rc, hw * 0.999, hl * 0.999)
    out = []
    for j, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
        ox, oy = cx + sx * (hw - rc), cy + sy * (hl - rc)
        for s in range(nc + 1):
            a = math.pi / 2 * (j + s / nc)
            out.append((ox + rc * math.cos(a), oy + rc * math.sin(a)))
    return out


def ring_z(cx, cy, hw, hl, rc, nc, z, inset=0.0):
    return [(x, y, z) for x, y in rrect(cx, cy, hw - inset, hl - inset, rc - inset, nc)]


def slab(part, cx, cy, hw, hl, rc, nc, prof, cap0=True, cap1=True):
    """Rounded slab by the profile [(z, inset)] from bottom to top."""
    return loft(part, [ring_z(cx, cy, hw, hl, rc, nc, z, d) for z, d in prof], cap0, cap1)


def knurl(part, c, w, r_out, r_in, n, h0, h1):
    """Knurled nut: a star-shaped prism of n teeth along w from h0 to h1."""
    u, v, w = basis(w)
    c = Vector(c)
    pts = [(u * math.cos(math.pi * k / n) + v * math.sin(math.pi * k / n)) * (r_out if k % 2 == 0 else r_in)
           for k in range(2 * n)]
    return loft(part, [[c + w * h0 + p for p in pts], [c + w * h1 + p for p in pts]])


def retag(part, faces, axis, sign, region):
    """Faces of a part looking strictly in the direction (axis, sign) go to another region (hidden faces go
    to the dark "inner" at a small scale: they need no atlas space)."""
    part.bm.normal_update()
    idx = part.region_index(region, *M.regions[region])
    for f in faces:
        if f.is_valid and f.normal[axis] * sign > 0.99:
            f[part.reg] = idx


def hide(part, faces):
    """These faces (the bottom on the roof, the lid under the sample) go to "inner"."""
    idx = part.region_index("inner", *M.regions["inner"])
    for f in faces:
        f[part.reg] = idx


# =============================================================================
# House
# =============================================================================
def build_house(spec):
    lod, seg = spec["lod"], spec["seg"]
    parts = []
    # body: the front face is covered by the door - dark, visible as a seam in the gap around the door
    # rubber feet only in the near LOD; in the middle one the house stands directly on the shelf
    z0 = FOOT_H if lod == 0 else 0.0
    body = P("house", "hammer")
    fs = g.box(body, X0, X1, YB, Y1, z0, HH, r=R_BOX, seg=seg)
    retag(body, fs, 1, -1, "inner")
    retag(body, fs, 2, -1, "inner")
    parts.append(body)
    door = P("door", "door")
    fs = g.box(door, X0 + 0.001, X1 - 0.001, Y0, YB + 0.002, z0 + 0.0012, HH - 0.0012, r=R_DOOR, seg=seg)
    retag(door, fs, 1, 1, "inner")
    parts.append(door)
    if lod == 0:
        # rubber feet under the bottom (19 kg do not slide on the shelf)
        for i, (fx, fy) in enumerate(FEET):
            ft = P("foot%d" % i, "rubber", uv_name="foot", uv_origin=(fx, fy, 0.0))
            g.box(ft, fx - 0.006, fx + 0.006, fy - 0.006, fy + 0.006, 0.0, FOOT_H + 0.0004)
            parts.append(ft)
    parts += build_hinges(lod)
    parts += build_latch(lod)
    parts += build_gland(lod)
    if lod == 0:
        # screws of the lead insert at the door corners: round heads
        for i, (sx, sz) in enumerate(DOOR_SCREWS):
            s = P("door_screw%d" % i, "screw", uv_name="door_screw", uv_origin=(sx, Y0, sz))
            lathe(s, (sx, Y0, sz), (0, -1, 0), [(0.0030, -0.0002), (0.0030, 0.0004), (0.0021, 0.0010), (0.0, 0.0012)],
                  8)
            parts.append(s)
        # inventory plate on the right side on two rivets
        py_, pz = PLATE
        pl = P("plate", "plate")
        g.box(pl, X1 - 0.0004, X1 + 0.0006, py_ - PLATE_W / 2, py_ + PLATE_W / 2, pz - PLATE_H / 2, pz + PLATE_H / 2)
        parts.append(pl)
        for i, dy in enumerate((-0.0168, 0.0168)):
            rv = P("rivet%d" % i, "screw", uv_name="rivet", uv_origin=(X1, py_ + dy, pz))
            lathe(rv, (X1 + 0.0006, py_ + dy, pz), (1, 0, 0), [(0.0016, -0.0001), (0.0016, 0.0003), (0.0, 0.0009)], 6)
            parts.append(rv)
    return parts


def build_hinges(lod):
    """Two removable hinges on the right: two links on a pin with a rounded head, a leaf on the door face (to
    the upper link) and a leaf on the side of the body (to the lower one)."""
    hx, hy = HINGE_AX
    parts = []
    for i, zc in enumerate(HINGES):
        h = P("hinge%d" % i, "hinge", uv_name="hinge", uv_origin=(hx, hy, zc))
        if lod == 0:
            lathe(h, (hx, hy, zc), (0, 0, 1),
                  [(0.0030, -0.0155), (0.0040, -0.0147), (0.0040, -0.0006), (0.0033, 0.0), (0.0040, 0.0006),
                   (0.0040, 0.0147), (0.0016, 0.0157), (0.0, 0.0160)], 6, cap0=True, phase=0.5)
            # leaves: on the door face towards the axis from the right, on the side of the body back from
            # the axis
            g.box(h, X1 - 0.016, hx - 0.0025, Y0 - 0.0010, Y0 + 0.0002, zc + 0.0006, zc + 0.0145)
            g.box(h, X1 - 0.0001, X1 + 0.0009, hy + 0.0025, Y0 + 0.024, zc - 0.0145, zc - 0.0006)
        else:
            g.cyl(h, (hx, hy, zc), "z", 0.0040, 0.031, 6)
        parts.append(h)
    return parts


def build_latch(lod):
    """Turn latch: a nickel-plated rosette, a black washer and a wing nut across."""
    lx, lz = LATCH
    parts = []
    if lod == 0:
        ros = P("latch_rosette", "chrome")
        lathe(ros, (lx, Y0, lz), (0, -1, 0), [(0.0100, -0.0003), (0.0100, 0.0005), (0.0086, 0.0011), (0.0066, 0.0011)],
              8)
        parts.append(ros)
        boss = P("latch", "knob")
        lathe(boss, (lx, Y0, lz), (0, -1, 0), [(0.0066, 0.0006), (0.0066, 0.0032), (0.0057, 0.0041), (0.0036, 0.0043)],
              10, cap1=True)
        parts.append(boss)
        # wing nut: a rounded plate in the y-z plane, the thickness along x with a chamfer
        wing = P("latch_wing", "knob")
        yc, hw, hl, rc = Y0 - 0.0085, 0.0045, 0.0115, 0.0035
        rings = []
        for x, d in ((lx - 0.0024, 0.0005), (lx - 0.0019, 0.0), (lx + 0.0019, 0.0), (lx + 0.0024, 0.0005)):
            rings.append([(x, a, b) for a, b in rrect(yc, lz, hw - d, hl - d, rc - d, 1)])
        loft(wing, rings)
        parts.append(wing)
    else:
        boss = P("latch", "knob")
        g.cyl(boss, (lx, Y0 - 0.002, lz), "y", 0.0070, 0.004, 8)
        parts.append(boss)
        wing = P("latch_wing", "knob")
        g.box(wing, lx - 0.0022, lx + 0.0022, Y0 - 0.013, Y0 - 0.004, lz - 0.011, lz + 0.011)
        parts.append(wing)
    return parts


def build_gland(lod):
    """Cable gland on the left side: a washer, a hex nut, a rubber tail."""
    gy, gz = GLAND
    c = (X0, gy, gz)
    parts = []
    nut = P("gland_nut", "chrome")
    if lod == 0:
        lathe(nut, c, (-1, 0, 0), [(0.0080, -0.0003), (0.0080, 0.0009), (0.0062, 0.0011)], 10)
        lathe(nut, c, (-1, 0, 0), [(0.0072, 0.0009), (0.0072, 0.0052), (0.0062, 0.0060), (0.0048, 0.0061)], 6,
              phase=0.5)
        boot = P("gland_boot", "rubber")
        lathe(boot, c, (-1, 0, 0), [(0.0048, 0.0058), (0.0046, 0.0072), (0.0038, 0.0090), (CABLE_R + 0.0003, 0.0110)], 8)
        parts += [nut, boot]
    else:
        g.cyl(nut, (X0 - 0.003, gy, gz), "x", 0.0072, 0.006, 6)
        boot = P("gland_boot", "rubber")
        g.cyl(boot, (X0 - 0.009, gy, gz), "x", CABLE_R + 0.0004, 0.006, 6, r2=0.0046)
        parts += [nut, boot]
    return parts


# =============================================================================
# Console
# =============================================================================
def build_pult(spec):
    lod, n = spec["lod"], spec["sides"]
    parts = []
    body = P("pult", "pult")
    if lod == 0:
        a45 = math.radians(45)
        prof = [(HH, 0.0012), (HH + 0.0012, 0.0), (HH + 0.0125, 0.0), (HH + 0.0127, P_STEP),
                (ZP - P_TOP, P_STEP), (ZP - P_TOP + P_TOP * math.sin(a45), P_STEP + P_TOP * (1 - math.cos(a45))),
                (ZP, P_STEP + P_TOP)]
        fs = slab(body, PX, PY, PW / 2, PL / 2, P_RC, 3, prof)
    else:
        fs = slab(body, PX, PY, PW / 2, PL / 2, P_RC, 2, [(HH, 0.0), (ZP - P_TOP, 0.0), (ZP, P_TOP)])
    hide(body, [fs[-2]])
    parts.append(body)
    # display: a dark frame with a window and the glass (ozl_screen, a section of its own, lcd, with frames)
    ly = PY + LCD_C
    bz = P("lcd_bezel", "bezel")
    if lod == 0:
        iw, ih = LCD_W / 2 + 0.0008, LCD_H / 2 + 0.0008
        loft(bz, [ring_z(PX, ly, 0.031, 0.0135, 0.003, 2, ZP - 0.0004), ring_z(PX, ly, 0.031, 0.0135, 0.003, 2, ZP + 0.0012),
                  ring_z(PX, ly, iw, ih, 0.0012, 2, ZP + 0.0012), ring_z(PX, ly, iw, ih, 0.0012, 2, ZP + 0.0003)],
             cap0=False, cap1=False)
        z = ZP + 0.0004
    else:
        g.box(bz, PX - 0.031, PX + 0.031, ly - 0.0135, ly + 0.0135, ZP - 0.001, ZP + 0.0010)
        z = ZP + 0.0011
    parts.append(bz)
    face = P("lcd", "bezel", group=SEL_SCREEN, section="lcd")
    g.quad(face, [(PX - LCD_W / 2, ly - LCD_H / 2, z), (PX + LCD_W / 2, ly - LCD_H / 2, z),
                  (PX + LCD_W / 2, ly + LCD_H / 2, z), (PX - LCD_W / 2, ly + LCD_H / 2, z)])
    face.glass_frame = (g.Frame((PX, ly, z), (1, 0, 0), (0, 1, 0), (0, 0, 1)), -LCD_W / 2, LCD_W / 2,
                        -LCD_H / 2, LCD_H / 2)
    parts.append(face)
    # buttons: a light housing ring and a black plunger with a spherical top
    for i, (bx, by) in enumerate(BTN):
        c = (PX + bx, PY + by, ZP)
        cp = P("btn_cap%d" % i, "knob", uv_name="btn_cap", uv_origin=c)
        if lod == 0:
            bs = P("btn_boss%d" % i, "pult", uv_name="btn_boss", uv_origin=c)
            lathe(bs, c, (0, 0, 1), [(0.0080, -0.0004), (0.0080, 0.0010), (0.0054, 0.0010)], 10)
            parts.append(bs)
            lathe(cp, c, (0, 0, 1), [(0.0047, 0.0), (0.0047, 0.0030), (0.0040, 0.0038), (0.0, 0.0041)], 10)
        else:
            g.cyl(cp, (c[0], c[1], ZP + 0.0018), "z", 0.0047, 0.0036, n)
        parts.append(cp)
    # cable connector on the top end: a base, a knurled union nut, a rubber tail
    cx, cz = PX + CONN_X, CONN_Z
    y_end = PY + PL / 2
    con = P("conn", "chrome")
    if lod == 0:
        lathe(con, (cx, y_end, cz), (0, 1, 0), [(0.0065, -0.0004), (0.0065, 0.0012), (0.0056, 0.0016), (0.0056, 0.0046)],
              10)
        knurl(con, (cx, y_end, cz), (0, 1, 0), 0.0062, 0.0057, 8, 0.0045, 0.0105)
        tail = P("conn_tail", "rubber")
        lathe(tail, (cx, y_end, cz), (0, 1, 0), [(0.0046, 0.0104), (0.0044, 0.0125), (0.0036, 0.0175), (0.0030, 0.0215),
                                                 (CABLE_R + 0.0003, 0.0240)], 8)
        parts += [con, tail]
    else:
        g.cyl(con, (cx, y_end + 0.005, cz), "y", 0.0062, 0.010, n)
        tail = P("conn_tail", "rubber")
        g.cyl(tail, (cx, y_end + 0.016, cz), "y", 0.0045, 0.012, 6, r2=CABLE_R + 0.0004)
        parts += [con, tail]
    lx, ly2 = PX + LED[0], PY + LED[1]
    led = P("led", "lamp", group=SEL_LAMP)
    if lod == 0:
        # counting LED (ozl_lamp_work) in a nickel-plated ring
        ring = P("led_ring", "chrome")
        lathe(ring, (lx, ly2, ZP), (0, 0, 1), [(0.0026, -0.0003), (0.0026, 0.0008), (0.0019, 0.0008)], 8)
        parts.append(ring)
        lathe(led, (lx, ly2, ZP), (0, 0, 1), [(0.0018, 0.0), (0.0018, 0.0008), (0.0011, 0.0015), (0.0, 0.0017)], 8)
        parts.append(led)
        # power socket on the bottom end
        jk = P("jack", "bezel")
        g.box(jk, PX + 0.012, PX + 0.024, PY - PL / 2 - 0.0008, PY - PL / 2 + 0.0004, HH + 0.010, HH + 0.018)
        parts.append(jk)
    else:
        g.quad(led, [(lx - 0.002, ly2 - 0.002, ZP + 0.0005), (lx + 0.002, ly2 - 0.002, ZP + 0.0005),
                     (lx + 0.002, ly2 + 0.002, ZP + 0.0005), (lx - 0.002, ly2 + 0.002, ZP + 0.0005)])
        parts.append(led)
    return parts


# =============================================================================
# Cuvette with a sample
# =============================================================================
def soil_z(u, v):
    """Sample as a mound: flush at the walls, up to 1.5 mm higher towards the middle, small bumps."""
    m = (math.sin(math.pi * u) * math.sin(math.pi * v)) ** 0.7
    q = math.sin(u * 91.7 + v * 47.3) * 43758.5453
    q -= math.floor(q)
    return CZ_SOIL + 0.0003 + m * (0.0012 + 0.0006 * (q - 0.5))


def build_tray(spec):
    """Cuvette: a black tray, sloped walls, a flanged rim; the sample mound lies below the rim."""
    lod = spec["lod"]
    parts = []
    nc = 2 if lod == 0 else 1
    tr = P("tray", "tray")
    prof = [(HH, 0.0030), (HH + 0.0170, 0.0008), (HH + 0.0170, -0.0012), (CZ_TOP, -0.0012), (CZ_TOP, 0.0022),
            (CZ_SOIL, 0.0038)]
    fs = slab(tr, TCX, TCY, T_HW, T_HL, 0.005, nc, prof)
    hide(tr, fs[-2:])
    parts.append(tr)
    soil = P("soil", "soil")
    sx0, sx1 = TCX - T_HW + 0.0040, TCX + T_HW - 0.0040
    sy0, sy1 = TCY - T_HL + 0.0040, TCY + T_HL - 0.0040
    nx, ny = (4, 6) if lod == 0 else (1, 1)
    bm = soil.bm
    vs = [[bm.verts.new((sx0 + (sx1 - sx0) * i / nx, sy0 + (sy1 - sy0) * j / ny,
                         soil_z(i / nx, j / ny) if lod == 0 else CZ_SOIL + 0.0008))
           for i in range(nx + 1)] for j in range(ny + 1)]
    soil.tag([bm.faces.new([vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]])
              for j in range(ny) for i in range(nx)])
    parts.append(soil)
    if lod == 0:
        # tape with a sample number on the sloped front wall
        ins = 0.0030 - (TAPE_Z - HH) / 0.017 * 0.0022
        fr = g.Frame((TCX, TCY - T_HL + ins, TAPE_Z), (1, 0, 0), (0, -math.sin(_T_SLOPE), math.cos(_T_SLOPE)),
                     (0, -math.cos(_T_SLOPE), -math.sin(_T_SLOPE)))
        tp = P("tape", "tape")
        g.box(tp, -TAPE_W / 2, TAPE_W / 2, -TAPE_H / 2, TAPE_H / 2, 0.00012, 0.00042, frame=fr)
        parts.append(tp)
    return parts


# =============================================================================
# Cable
# =============================================================================
def cable_ctrl():
    """Control points of the cable (the curve does not pass through them but smooths them - a B-spline):
    from the connector tail straight back, in an arc down to the back wall, along it with a slight sag to
    the back left corner, around the corner in a free arc (not touching: a semi-rigid cable, bend radius
    ~20 mm) and along the left side into the gland tail straight along its axis."""
    cx, cz = PX + CONN_X, CONN_Z
    ys = PY + PL / 2 + 0.022
    gy, gz = GLAND
    return [(cx, ys, cz), (cx, ys + 0.0105, cz - 0.0005), (cx - 0.002, ys + 0.0135, cz - 0.0210),
            (cx - 0.006, Y1 + 0.0135, 0.176), (cx - 0.014, Y1 + 0.0055, 0.163), (X0 - 0.0060, Y1 + 0.0095, 0.157),
            (X0 - 0.0160, Y1 + 0.0005, 0.158), (X0 - 0.0195, gy + 0.0120, 0.163), (X0 - 0.0175, gy + 0.0010, 0.168),
            (X0 - 0.0150, gy, gz), (X0 - 0.0090, gy, gz)]


def bspline(ctrl, max_deg, max_len, n=24):
    """Uniform cubic B-spline over control points (the ends at the end points, the tangent towards the
    neighbour), thinned: a point is placed when the tangent has turned by max_deg or the segment has grown
    to max_len. No kinks: the turn at each joint is no more than max_deg."""
    q = [Vector(ctrl[0])] * 2 + [Vector(p) for p in ctrl] + [Vector(ctrl[-1])] * 2
    dense = []
    for i in range(len(q) - 3):
        a, b, c, d = q[i:i + 4]
        for s in range(n):
            t = s / n
            dense.append(((1 - t) ** 3 * a + (3 * t ** 3 - 6 * t * t + 4) * b + (-3 * t ** 3 + 3 * t * t + 3 * t + 1) * c +
                          t ** 3 * d) / 6.0)
    dense.append(Vector(ctrl[-1]))
    pts = [dense[0]]
    for p in dense[1:]:
        if (p - pts[-1]).length > 1e-5:
            pts.append(p)
    out, tan = [pts[0]], (pts[1] - pts[0]).normalized()
    lim = math.radians(max_deg)
    for j in range(1, len(pts) - 1):
        tj = (pts[j + 1] - pts[j - 1]).normalized()
        if tan.angle(tj, 0.0) > lim or (pts[j] - out[-1]).length > max_len:
            out.append(pts[j])
            tan = tj
    out.append(pts[-1])
    return [tuple(p) for p in out]


def build_cable(spec):
    lod = spec["lod"]
    # 10 faces: neighbours are 36 degrees apart, below the sharp-edge threshold (40), so the cable is round,
    # not hexagonal
    if lod == 0:
        pts = bspline(cable_ctrl(), 20.0, 0.035)
    else:
        pts = bspline(cable_ctrl(), 40.0, 0.060)
    cb = P("cable", "cable")
    g.pipe(cb, pts, CABLE_R, 10 if lod == 0 else 4)
    if lod == 0:
        BOUNDS["cable_gap"] = min(house_sdf(Vector(p)) for p in pts[1:-2]) - CABLE_R
        print("cable: %d points" % len(pts))
    return [cb]


def house_sdf(p):
    """Distance from a point to the rounded body of the house (a check that the cable does not cut through
    it)."""
    c, hlf = Vector((0.0, 0.0, HH / 2)), Vector((X1, Y1, HH / 2))
    q = Vector([abs(p[i] - c[i]) - (hlf[i] - R_BOX) for i in range(3)])
    out = Vector([max(a, 0.0) for a in q]).length
    return out + min(max(q), 0.0) - R_BOX


def build_lod(spec):
    parts = build_house(spec) + build_pult(spec) + build_tray(spec) + build_cable(spec)
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
        print("bounds: %s .. %s; cable clearance to house %.1f mm" % (
            tuple(round(a, 4) for a in BOUNDS["lo"]), tuple(round(a, 4) for a in BOUNDS["hi"]),
            BOUNDS["cable_gap"] * 1000))
        for d in DECOR:
            q = kv.corners(d[5], d[1], d[2], d[3])
            print("decor %s: x %.4f..%.4f y %.4f..%.4f z %.4f..%.4f" % (
                d[5], min(p[0] for p in q), max(p[0] for p in q), min(p[1] for p in q), max(p[1] for p in q),
                min(p[2] for p in q), max(p[2] for p in q)))
    return parts


def collision():
    """Two convex parts: the house and the layer on the roof (the console with the connector and the
    cuvette); the cable has no collision. The mass is the item weight in the mod, 0.8 kg."""
    house = kx.box_pts(X0, X1, Y0, Y1, 0.0, HH)
    top = kx.box_pts(PX - PW / 2, PX + PW / 2, PY - PL / 2, PY + PL / 2 + 0.024, HH, ZP + 0.003)
    top += kx.box_pts(CX0 - 0.0015, CX1 + 0.0015, CY0 - 0.0015, CY1 + 0.0015, HH, CZ_TOP)
    pen = kx.PEN + r"\metalplate.rvmat"
    comps = [(house, pen), (top, pen)]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    memory = {
        # inventory preview camera: from the front left and above (invView is where the camera is)
        "invView": [(-0.32, -0.50, 0.46)],
        "ce_center": [(0.0, 0.0, 0.117)],
        "ce_radius": [(0.13, 0.0, 0.117)],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


SHOTS = [
    ("front", (-0.24, -0.54, 0.40), (0.0, 0.0, 0.115), 40),
    ("top", (-0.06, -0.24, 0.50), (-0.010, 0.0, 0.222), 42),
    ("left", (-0.50, 0.10, 0.34), (-0.04, 0.03, 0.14), 40),
    ("back", (0.34, 0.46, 0.36), (0.0, 0.02, 0.11), 40),
]
# preview: all four angles (hinges and plate only from the back right), the "working" state uses the front
# and the console
M.look_shots = (4, 2)

M.run(build_lod, collision, SHOTS, row_step=0.30, row_shot=((0.15, -1.1, 0.40), (0.15, 0, 0.11)))
