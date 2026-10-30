"""M74 - Programmer (OZL_Tool_Programmer): a module of the "Electronics" line (packers M05 and M11) - a
portable 2x2 item, it stands in slot OZL_Tool3 and is visible on the shelf of the machine through a
proxy. Variant A: a home-made Soviet EPROM programmer (K573RF) and beside it an ultraviolet eraser - a
small box with a window.

    blender --background --python build_m74.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (ZIF slots, the IC window, the paper
slip on the spare IC, scale and inventory number digits, the "optical radiation" triangle).

Detailing: "dayz" look (matte, dirtier, shadows in corners); parts are solids of revolution with
chamfers and many sides (LEDs with a dome and a flange, MT-1 toggles with a nut, a bushing and a
thickened lever, knurled knobs, slotted screws, sockets, feet); ICs with leads and a glass-solder seam
between the ceramic halves; the case on a bottom plate, screws on the sides, ventilation slots; the
eraser has a timer, a window frame made of angle, a bracket handle, slots on the side; the cord is a
smooth curve straight into the plug tail (no kink at the plug). No vanilla DayZ items in the module:
the 0.21 x 0.20 platform is fully occupied by the devices, small items around belong to the machine.

Target: a programmer ~0.20 x 0.07 x 0.15 m + an eraser ~0.10 x 0.06 x 0.08 m, getinax or bare
aluminium, a green lever ZIF socket, toggles, LEDs, a grey ribbon; a module is no larger than ~0.2 x
0.2 m by its base, up to ~0.25 m high, with a flat bottom.

Reference and sizes. There are no data sheets for a home-made device (the photos are analogues), so
the case is built around parts with data-sheet sizes:
- 40-pin 0.6" lever socket (Textool 240-1280 and clones, as in the reference photo): body 66 x 24 x
  11.5 mm, lever 15 mm (protosupplies.com, "ZIF socket 40 pin 0.6 wide"; the 3M Textool
  240-1280-00-0602 per RS 1010727 is 77.9 mm with the lever, 22.9 x 11.9 mm); slots at a 2.54 mm
  pitch, rows 15.24 mm apart;
- ICs: K573RF5 (a 2716 analogue, DIP-24, 0.6") and KS573RF4 (a 2764 analogue, DIP-28) in ceramic
  packages with a quartz window: the package length is 31.5 and 36.5 mm, the width 15 mm (a standard
  ceramic DIP 0.6": 2.54 mm x (n/2) + ~1 mm), the height ~4 mm; two ceramic halves on glass solder, the
  leads leave the seam and go down into rows 15.24 mm apart;
- MT-1 type toggles (a nut ~9 mm across flats, an M6 bushing, a lever ~11 mm with a thickening at the
  end), AL307 LEDs (D 5 mm, flange D 5.8), a wafer switch with a D 18 mm knob; 4 mm "banana" sockets;
- ribbon: 25 cores at a 1.27 mm pitch (31.75 mm) to a DB-25 connector (a 90s PC parallel port; flange
  53 mm, body D 39 x 8 mm);
- eraser: the factory compact ones - Spectroline PE-140 8.3 x 20.3 x 9.5 cm, tray 5.1 x 16.8 x 1.6 cm
  (the PE series data sheet), Lawtronics ME5E 190 x 165 x 95 mm (RS 0547877) - are longer than the
  platform: they hold a 4 W tube lamp (134 mm) and a timer on the face. A home-made one uses a short
  quartz emitter, hence ~0.10 x 0.06 x 0.08 m; the window is dark UVS glass (shows whether the lamp is
  on), a tray at the front, a mechanical timer with a D 14 mm knob (like the ME5).
The module_N platform of M05 and M11 is 0.22 x 0.24 m, places 0.28 m apart, the shelf is 0.30 m deep;
two devices of the target size do not fit side by side, so the programmer is narrower (0.13 x
0.14 m), and the eraser is turned with its long side along the depth (0.076 x 0.10 m): together
0.21 x 0.20 m, the ribbon is folded accordion-style behind the programmer, the eraser plug lies behind
the eraser.

Modules: `used but intact, worn paint on the edges`, no faction colour. Marks: scale digits at the
wafer switch, timer ticks, an inventory number in paint, a paper slip with a pencil number on the
window of the spare IC, a yellow triangle with a radiation pictogram on the eraser; a marker stroke
on the ZIF.
"Working" state (a loop): ozl_lamp_work - the green "power" LED, the neon lamp and the eraser window
burn steadily (atlas _on, onSelections); ozl_lamp - the red "write" LED blinks (blink); ozl_work - the
eraser timer knob turns slowly (a bone, a model.cfg loop: sourceAddress loop, maxValue 1 - one turn
per pass, a pass is animPeriod 30 s in the mod config). The yellow LED stays off when working. At
rest everything is off and still.
LODs (a small item): near and middle (no screws, leads, slots, ticks, smoothing), no far one.

Blender axes: X is along the shelf, Y is depth (the front face is -Y), Z is up. The origin is the
centre of the bottom: this is how the module stands on the module_N proxy point (autocenter = 0 in
Geometry).
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
from mathutils import Matrix, Vector  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# --- dimensions, m --------------------------------------------------------------------------------
# programmer: an aluminium case on a bottom plate, a 2.5 mm getinax panel on top protruding by 1 mm
PX0, PX1, PY0, PY1 = -0.104, 0.024, -0.096, 0.040
FOOT = 0.003
BASE_T = 0.0016                 # bottom plate (visible as a strip under the cover)
ZC = 0.041                      # top of the aluminium case
ZP = ZC + 0.0025                # top of the panel
LIP = 0.001
# 40-pin lever ZIF socket
ZIF_CX, ZIF_CY, ZIF_L, ZIF_W, ZIF_H = -0.050, 0.014, 0.064, 0.024, 0.0115
ZIF_T = ZP + ZIF_H
LEV_X0, LEV_X1 = ZIF_CX + 0.030, ZIF_CX + 0.012      # lever axis and ball: the lever is lowered along the face
LEV_Y, LEV_Z = ZIF_CY - ZIF_W / 2 - 0.0028, ZP + 0.0052
# K573RF5 in the socket: 12 rows on the lever side; the package is 0.9 mm above the socket, the leads are
# visible
CHIP_L, CHIP_W = 0.0315, 0.0150
CHIP_CX = ZIF_CX + 0.01016
CHIP_Z0 = ZIF_T + 0.0009
CHIP_Z1 = CHIP_Z0 + 0.0040
ROW = 0.00762                   # half the distance between lead rows of 0.6"
PITCH = 0.00254
# spare KS573RF4 in a piece of antistatic foam (along Y), leads stuck into the foam
FOAM = (-0.004, 0.020, -0.026, 0.016, ZP, ZP + 0.006)
SPARE_L, SPARE_W = 0.0365, 0.0150
SP_CX, SP_CY = 0.008, -0.00425
SP_Z0 = FOAM[5] + 0.0008
SP_Z1 = SP_Z0 + 0.0040
# AL307 LEDs: red ("write", blinks), yellow, green ("power")
LEDS = [(-0.092, "led_r"), (-0.081, "led_y"), (-0.070, "led_g")]
LED_Y = -0.024
# MT-1 toggles: lever tilt (+1 is back, -1 is forward)
TOGGLES = [(-0.091, -1), (-0.074, 1), (-0.057, -1)]
TOG_Y = -0.066
TOG_TILT = math.radians(20)
# IC-type wafer switch, the pointer is at "2"
KNOB_X, KNOB_Y = -0.022, -0.062
KNOB_A = math.radians(120)
SCALE_D = 0.036
INV_X, INV_Y, INV_W, INV_H = -0.078, -0.087, 0.024, 0.009
# programming voltage test sockets on the face
JACKS = [(-0.030, "jack_r"), (-0.016, "jack_k")]
JACK_Z = 0.022
# 25-core ribbon to the DB-25
RXC, RW, RT = -0.058, 0.032, 0.0012
EXIT_Z = 0.024
F1_Y, F2_Y = 0.099, 0.066                         # accordion folds
HOOD_Y0, HOOD_Y1, HOOD_Z0, HOOD_Z1 = 0.0645, 0.1005, 0.0036, 0.0196
HOOD_ZM = (HOOD_Z0 + HOOD_Z1) / 2
# eraser: a case in light enamel, a tray at the front, a UVS window on top
EX0, EX1, EY0, EY1, EFOOT, EZ1 = 0.030, 0.106, -0.088, 0.012, 0.002, 0.062
WIN = (0.046, 0.090, -0.074, -0.046)
UV_X, UV_Y, UV_W, UV_H = 0.068, -0.020, 0.030, 0.027
NEON = (0.046, 0.046)                              # x, z on the face
ETOG = (0.088, 0.046)
TIMER = (0.067, 0.046)                             # timer knob on the face (bone ozl_work)
TIMER_A = math.radians(65)                         # knob mark at rest
# eraser cord and plug
PLUG = (0.034, 0.066, 0.064, 0.092, 0.0, 0.016)
PLUG_ZM = 0.008
CORD_R = 0.0022

LOD_SPECS = [
    dict(lod=0, sides=12),
    dict(lod=1, sides=6),
]

REGIONS = {
    "alu": ("alu", 1.0), "getinax": ("getinax", 1.5), "zif": ("zif", 2.5), "zifknob": ("zifknob", 0.8),
    "lever": ("chrome", 0.6), "chip": ("chip", 3.0), "spare": ("spare", 3.0), "foam": ("foam", 0.8),
    "seal": ("seal", 2.0), "leads": ("pins", 2.0),
    "led_r": ("led_r", 0.6), "led_y": ("led_y", 0.6), "led_g": ("led_g", 0.6), "ledring": ("black", 0.5),
    "toggle": ("chrome", 0.8), "nut": ("nut", 0.8), "knob": ("knob", 1.0), "pointer": ("pointer", 0.5),
    "tick": ("pointer", 0.6),
    "screw": ("screw", 0.6), "feet": ("rubber", 0.4), "grommet": ("rubber", 0.5), "jack_r": ("jack_r", 0.6),
    "jack_k": ("black", 0.6), "hole": ("hole", 0.4), "din": ("nut", 0.6), "insert": ("black", 0.5),
    "ribbon": ("ribbon", 1.5), "hood": ("hood", 1.0), "dshell": ("dshell", 1.0), "thumb": ("chrome", 0.6),
    "enamel": ("enamel", 1.2), "drawer": ("enamel", 1.2), "handle": ("chrome", 0.8), "bezel": ("chrome", 0.6),
    "neon": ("neon", 0.6), "frame": ("frame", 0.8), "uvglass": ("uvglass", 0.8), "cord": ("cord", 0.6),
    "plug": ("plug", 0.8), "pins": ("pins", 0.5),
}


def dec(fn, center, size, z):
    """A decal on an up-facing face in the layer z +- 1 mm."""
    return (os.path.join(WORK, fn), "z", 1, ("x", "y"), center, size, (z - 0.001, z + 0.001))


ZIF_DEC = dec("decal_zif.png", (ZIF_CX, ZIF_CY), (ZIF_L, ZIF_W), ZIF_T)
CHIP_DEC = dec("decal_chip.png", (CHIP_CX, ZIF_CY), (CHIP_L, CHIP_W), CHIP_Z1)
LABEL_DEC = dec("decal_label.png", (SP_CX, SP_CY), (SPARE_W, SPARE_L), SP_Z1)
SCALE_DEC = (os.path.join(WORK, "decal_scale.png"), "z", 1, ("x", "y"), (KNOB_X, KNOB_Y), (SCALE_D, SCALE_D),
             (ZP - 0.0005, ZP + 0.0005))
INV_DEC = (os.path.join(WORK, "decal_inv.png"), "z", 1, ("x", "y"), (INV_X, INV_Y), (INV_W, INV_H),
           (ZP - 0.0005, ZP + 0.0005))
# countersunk panel screws are flush with the getinax, so they are a decal
SCREW_D = 0.0056
SCREW_DECS = [(os.path.join(WORK, "decal_screw.png"), "z", 1, ("x", "y"), (x, y), (SCREW_D, SCREW_D),
               (ZP - 0.0005, ZP + 0.0005)) for x in (PX0 + 0.005, PX1 - 0.005) for y in (PY0 + 0.005, PY1 - 0.005)]
UV_DEC = (os.path.join(WORK, "decal_uv.png"), "z", 1, ("x", "y"), (UV_X, UV_Y), (UV_W, UV_H),
          (EZ1 - 0.0005, EZ1 + 0.0005))

# modules: worn at the edges, almost no rust
USED = dict(chip=(0.64, 0.70), rust=(0.99, 1.0), rust_low=0.0, floor_z=0.0, dust=0.30, grime=0.50)
CLEAN = dict(chip=(0.88, 0.94), rust=(0.99, 1.0), rust_low=0.0, floor_z=0.0, dust=0.15, grime=0.25)


def mat_ribbon(mat, origin, pitch=0.00127, x0=RXC - RW / 2, **kw):
    """Grey ribbon: over even plastic, grooves between the cores at a 1.27 mm pitch (dark lines and relief
    across X) and a red first core at the -X edge."""
    outs = kmats.build_plastic(mat, origin, **kw)
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    vec, sep = t.coords(origin, 31.0)
    x = t.math("SUBTRACT", sep.outputs["X"], x0)
    q = t.math("FRACT", t.math("DIVIDE", x, pitch))
    d = t.math("ABSOLUTE", t.math("SUBTRACT", t.math("MULTIPLY", q, 2.0), 1.0))   # 1 at the middle of a core
    groove = t.maprange(d, 0.45, 0.0, 0.0, 1.0)
    col = kmats.sock(mat, outs["color"])
    col = t.mixc(t.math("MULTIPLY", groove, 0.45), col, kmats.lin((96, 96, 92)))
    red = t.math("LESS_THAN", x, pitch)
    col = t.mixc(t.math("MULTIPLY", red, 0.85), col, kmats.lin((150, 34, 30)))
    h = outs["height"]
    hh = t.math("SUBTRACT", kmats.sock(mat, h) if not isinstance(h, (int, float)) else h,
                t.math("MULTIPLY", groove, 0.25))
    return dict(outs, color=kmats.Tree.ref(col), height=kmats.Tree.ref(hh))


KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "alu": ("steel", dict(seed=2.4, tone=0.34, along="x", gloss=0.40, spec=0.45, dust=0.5, grime=0.8)),
    # getinax: brown laminated plastic, lighter at the edges (chips down to the paper layers)
    "getinax": ("paint", dict(USED, chip=(0.68, 0.74), dust=0.4, grime=0.7, color=kmats.lin((132, 76, 38)), under=kmats.lin((170, 124, 80)),
                              seed=3.3, gloss=0.42, spec=0.22, decal_items=[SCALE_DEC, INV_DEC] + SCREW_DECS)),
    "zif": ("paint", dict(CLEAN, color=kmats.lin((62, 150, 128)), under=kmats.lin((110, 182, 162)), seed=3.9,
                          gloss=0.40, spec=0.30, decal_items=[ZIF_DEC])),
    "zifknob": ("plastic", dict(color=kmats.lin((62, 150, 128)), seed=4.1, gloss=0.5, spec=0.35, dust=0.05, grime=0.1,
                                scuff=(0.85, 0.92))),
    "chrome": ("steel", dict(seed=5.9, tone=0.46, along="z", gloss=0.80, spec=0.90, dust=0.06, grime=0.12)),
    "chip": ("paint", dict(CLEAN, color=kmats.lin((222, 216, 198)), under=kmats.lin((190, 186, 172)), seed=4.4,
                           gloss=0.35, spec=0.25, decal_items=[CHIP_DEC])),
    "spare": ("paint", dict(CLEAN, color=kmats.lin((62, 60, 58)), under=kmats.lin((92, 90, 86)), seed=4.7,
                            gloss=0.30, spec=0.20, decal_items=[LABEL_DEC])),
    # glass-solder seam between the ceramic halves
    "seal": ("flat", dict(color=kmats.lin((46, 44, 40)), gloss=0.55, spec=0.35)),
    "foam": ("plastic", dict(color=kmats.lin((26, 26, 28)), seed=5.1, gloss=0.05, spec=0.03, mottle=0.14, dust=0.3,
                             grime=0.2, scuff=(0.95, 1.0))),
    "led_r": ("flat", dict(color=kmats.lin((112, 26, 22)), gloss=0.85, spec=0.8)),
    "led_r_on": ("flat", dict(color=kmats.lin((255, 52, 34)), gloss=0.85, spec=0.8)),
    "led_g": ("flat", dict(color=kmats.lin((36, 94, 32)), gloss=0.85, spec=0.8)),
    "led_g_on": ("flat", dict(color=kmats.lin((96, 255, 72)), gloss=0.85, spec=0.8)),
    "led_y": ("flat", dict(color=kmats.lin((128, 100, 22)), gloss=0.85, spec=0.8)),
    "nut": ("steel", dict(seed=6.4, tone=0.50, along="x", gloss=0.55, spec=0.6, dust=0.1, grime=0.25)),
    "knob": ("plastic", dict(color=kmats.lin((22, 21, 20)), seed=6.8, gloss=0.5, spec=0.4, dust=0.25, grime=0.3,
                             scuff=(0.80, 0.88))),
    "pointer": ("flat", dict(color=kmats.lin((230, 226, 214)), gloss=0.4, spec=0.3)),
    "screw": ("steel", dict(seed=8.1, tone=0.48, along="x", gloss=0.55, spec=0.6, dust=0.1, grime=0.3)),
    "jack_r": ("plastic", dict(color=kmats.lin((170, 34, 28)), seed=7.6, gloss=0.45, spec=0.3, dust=0.1, grime=0.2)),
    "hole": ("flat", dict(color=kmats.lin((8, 8, 8)), gloss=0.1, spec=0.05)),
    "ribbon": (mat_ribbon, dict(color=kmats.lin((178, 176, 168)), seed=7.3, gloss=0.35, spec=0.2, dust=0.2,
                                grime=0.25, scuff=(0.88, 0.95))),
    "hood": ("plastic", dict(color=kmats.lin((156, 150, 138)), seed=8.4, gloss=0.35, spec=0.25, dust=0.35, grime=0.45,
                             scuff=(0.80, 0.88))),
    "dshell": ("steel", dict(seed=9.2, tone=0.56, along="x", gloss=0.6, spec=0.7, dust=0.05, grime=0.15)),
    # eraser: a steel case in light enamel, chips down to metal
    "enamel": ("paint", dict(USED, chip=(0.58, 0.64), dust=0.45, grime=0.8, color=kmats.lin((200, 190, 164)), under=kmats.lin((122, 124, 124)), seed=4.6,
                             gloss=0.42, spec=0.30, decal_items=[UV_DEC])),
    "frame": ("steel", dict(seed=9.8, tone=0.40, along="x", gloss=0.5, spec=0.5, dust=0.15, grime=0.3)),
    # UVS glass: almost black with violet, the lamp behind it glows when working
    "uvglass": ("flat", dict(color=kmats.lin((42, 28, 60)), gloss=0.92, spec=0.9)),
    "uvglass_on": ("flat", dict(color=kmats.lin((168, 108, 255)), gloss=0.92, spec=0.9)),
    "neon": ("flat", dict(color=kmats.lin((124, 48, 20)), gloss=0.85, spec=0.8)),
    "neon_on": ("flat", dict(color=kmats.lin((255, 130, 42)), gloss=0.85, spec=0.8)),
    "cord": ("plastic", dict(color=kmats.lin((196, 192, 180)), seed=10.3, gloss=0.3, spec=0.2, dust=0.35, grime=0.55,
                             scuff=(0.85, 0.95))),
    "plug": ("plastic", dict(color=kmats.lin((34, 30, 28)), seed=10.8, gloss=0.42, spec=0.3, dust=0.15, grime=0.2,
                             scuff=(0.78, 0.86))),
    "pins": ("steel", dict(seed=11.2, tone=0.62, along="x", gloss=0.65, spec=0.7, dust=0.05, grime=0.2)),
})

OBJ, NAME = "m74_programmer", "ozr_programmer"
# "Working" state (a loop): burning steadily - ozl_lamp_work (the green LED, the neon lamp, the
# window), blinking - ozl_lamp (the red "write" LED), turning - ozl_work (the eraser timer knob)
SEL_LAMP, SEL_BLINK, SEL_WORK = "ozl_lamp_work", "ozl_lamp", "ozl_work"
ON = dict(remap={"led_r": "led_r_on", "led_g": "led_g_on", "uvglass": "uvglass_on", "neon": "neon_on"},
          emissive=(1.0, 1.0, 1.0, 1.0))
TIMER_ANIM = ("ozl_work_timer", dict(type="rotation", source="ozl_work", sourceAddress="loop", selection=SEL_WORK,
                                     axis="ozl_work_axis", memory=1, minValue=0.0, maxValue=1.0, angle0=0.0,
                                     angle1=2 * math.pi))
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=1024, look="dayz",
                 selections=(SEL_LAMP, SEL_BLINK, SEL_WORK), hidden=(SEL_LAMP, SEL_BLINK),
                 states={"on": ON}, bones=((SEL_WORK, ""),), animations=(TIMER_ANIM,),
                 sources={"ozl_work": dict(animPeriod=30.0)})
P = M.part
BOUNDS = {}


# --- own primitives -------------------------------------------------------------------------------
def use(part, region):
    """The following faces of the part go to another region."""
    return part.use(region, *REGIONS[region])


def basis(axis):
    """An axis and two transverse directions: u x v = axis."""
    a = Vector(axis).normalized()
    ref = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    u = ref.cross(a).normalized()
    return a, u, a.cross(u)


def lathe(part, base, axis, prof, sides, phase=0.0, flute=None):
    """Solid of revolution: the profile [(r, h)] around axis from point base (r = 0 is a pole). Faces look to
    the right along the profile: up the axis on the outside they face outwards, towards the axis across
    the top they face up, down on the inside they face the axis. flute = (ring numbers, k): on these
    rings every second vertex lies at radius r*k (knob knurling)."""
    bm = part.bm
    a, u, v = basis(axis)
    o = Vector(base)
    rings_fl, fk = flute if flute else ((), 1.0)
    rings = []
    for i, (r, h) in enumerate(prof):
        c = o + a * h
        if r < 1e-9:
            rings.append([bm.verts.new(c)])
            continue
        ring = []
        for k in range(sides):
            t = phase + 2 * math.pi * k / sides
            rr = r * (fk if (i in rings_fl and k % 2) else 1.0)
            ring.append(bm.verts.new(c + (u * math.cos(t) + v * math.sin(t)) * rr))
        rings.append(ring)
    faces = []
    for r0, r1 in zip(rings, rings[1:]):
        if len(r0) == 1 and len(r1) == 1:
            continue
        for k in range(sides):
            j = (k + 1) % sides
            if len(r0) == 1:
                faces.append(bm.faces.new([r0[0], r1[j], r1[k]]))
            elif len(r1) == 1:
                faces.append(bm.faces.new([r0[k], r0[j], r1[0]]))
            else:
                faces.append(bm.faces.new([r0[k], r0[j], r1[j], r1[k]]))
    return part.tag(faces)


def face_quad(part, c, n, u, hu, hv):
    """A flat rectangle facing n: +-hu along u, +-hv across (a slot, a tick, a lead)."""
    n, u, c = Vector(n).normalized(), Vector(u).normalized(), Vector(c)
    v = n.cross(u)
    return g.quad(part, [c - u * hu - v * hv, c + u * hu - v * hv, c + u * hu + v * hv, c - u * hu + v * hv])


def screw(part, c, n, r=0.0027, h=0.0012, sides=10, ang=0.0):
    """Screw with a round head and a slot (the slot is the hole region of the same part)."""
    use(part, "screw")
    lathe(part, c, n, [(r, 0.0), (0.72 * r, h), (0.0, h)], sides, phase=ang)  # sides >= 10: round
    use(part, "hole")
    a, u, v = basis(n)
    d = u * math.cos(ang + 0.6) + v * math.sin(ang + 0.6)
    face_quad(part, Vector(c) + a * (h + 0.00004), a, d, 0.6 * r, 0.12 * r)


def ball(part, center, r, u, v):
    """Ball (the head of the ZIF lever): a u x v UV sphere."""
    bm = part.bm
    before = set(bm.faces)
    bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=v, radius=r, matrix=Matrix.Translation(center))
    faces = [f for f in bm.faces if f not in before]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    part.tag(faces)


def rot_frame(cx, cy, z, a):
    """Local axes rotated about Z by a: u across, v along direction a, n up."""
    d = Vector((math.cos(a), math.sin(a), 0.0))
    return g.Frame((cx, cy, z), (d.y, -d.x, 0.0), d, (0, 0, 1))


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, as in M38, M45 and M69)."""
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


def arc(cy, cz, r, a0, a1, n):
    """An arc in the YZ plane: points (y, z) = centre + r (cos a, sin a), a from a0 to a1 (degrees)."""
    return [(cy + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def toggle(hw, lev, base, n, lever_dir, fine):
    """MT-1 toggle on a face with normal n: a hex nut, a threaded bushing, a chrome lever with a thickening
    at the end (in the near LOD)."""
    n = Vector(n).normalized()
    b = Vector(base)
    if fine:
        lathe(hw, b, n, [(0.0045, 0.0), (0.0045, 0.0020), (0.0030, 0.0024)], 6, phase=math.pi / 6)
        lathe(hw, b, n, [(0.0030, 0.0024), (0.0030, 0.0046), (0.0016, 0.0049)], 6)
        lathe(lev, b + n * 0.0046, lever_dir, [(0.0016, -0.0008), (0.0011, 0.0100), (0.0008, 0.0115),
                                               (0.0, 0.0119)], 10)
    else:
        lathe(hw, b, n, [(0.0045, 0.0), (0.0045, 0.0022), (0.0, 0.0022)], 6, phase=math.pi / 6)
        lathe(lev, b + n * 0.0030, lever_dir, [(0.0016, -0.0030), (0.0011, 0.0110), (0.0, 0.0119)], 4)


def chip_leads(part, cx, cy, along, n_side, z_top, z_bot, half_w):
    """DIP leads along the two long sides: a 0.5 mm strip facing outwards from the seam to the socket."""
    for s in (-1, 1):
        for k in range(n_side):
            d = (k - (n_side - 1) / 2) * PITCH
            if along == "x":
                c, nn, u = (cx + d, cy + s * half_w, (z_top + z_bot) / 2), (0, s, 0), (1, 0, 0)
            else:
                c, nn, u = (cx + s * half_w, cy + d, (z_top + z_bot) / 2), (s, 0, 0), (0, 1, 0)
            face_quad(part, c, nn, u, 0.00025, (z_top - z_bot) / 2)


def dip(name, region, cx, cy, along, length, z0, z1, n_side, z_leads, fine):
    """Ceramic DIP: the lower half is narrower, a dark glass-solder seam, the upper half with a chamfer,
    leads from the seam downwards (near LOD); a single box in the middle LOD."""
    hw = CHIP_W / 2
    lx, ly = (length / 2, hw) if along == "x" else (hw, length / 2)
    if not fine:
        b = P(name, region)
        g.box(b, cx - lx, cx + lx, cy - ly, cy + ly, z0, z1)
        return [b]
    sx, sy = (0.0002, 0.0004) if along == "x" else (0.0004, 0.0002)    # the lower half is narrower across
    zs0, zs1 = z0 + 0.0017, z0 + 0.0021
    lo = P(name + "_low", region)
    g.box(lo, cx - lx + sx, cx + lx - sx, cy - ly + sy, cy + ly - sy, z0, zs0)
    sl = P(name + "_seal", "seal")
    g.box(sl, cx - lx + sx / 2, cx + lx - sx / 2, cy - ly + sy / 2, cy + ly - sy / 2, zs0, zs1)
    tp = P(name, region)
    g.box(tp, cx - lx, cx + lx, cy - ly, cy + ly, zs1, z1, r=0.0003, seg=1)
    ld = P(name + "_leads", "leads")
    chip_leads(ld, cx, cy, along, n_side, (zs0 + zs1) / 2, z_leads, ROW + 0.00003)
    return [lo, sl, tp, ld]


# --- programmer -----------------------------------------------------------------------------------
def build_programmer(spec):
    fine = spec["lod"] == 0
    parts = []
    ch = P("chassis", "alu")
    if fine:
        g.box(ch, PX0, PX1, PY0, PY1, FOOT + BASE_T * 0.5, ZC, r=0.002, seg=2)
        bp = P("base_plate", "alu")
        g.box(bp, PX0 - 0.0005, PX1 + 0.0005, PY0 - 0.0005, PY1 + 0.0005, FOOT, FOOT + BASE_T)
        parts.append(bp)
    else:
        g.box(ch, PX0, PX1, PY0, PY1, FOOT, ZC, r=0.002, seg=1)
    parts.append(ch)
    pn = P("panel", "getinax")
    g.box(pn, PX0 - LIP, PX1 + LIP, PY0 - LIP, PY1 + LIP, ZC, ZP, **({"r": 0.0005, "seg": 1} if fine else {}))
    parts.append(pn)
    if fine:
        ft = P("prog_feet", "feet")
        for x in (PX0 + 0.012, PX1 - 0.012):
            for y in (PY0 + 0.012, PY1 - 0.012):
                lathe(ft, (x, y, 0.0), (0, 0, 1), [(0.0066, 0.0), (0.0078, FOOT)], 4, phase=math.pi / 4)
        parts.append(ft)
        # cover screws to the bottom plate: on the face and on the left side; ventilation slots on the left side
        sf = P("prog_screws_front", "screw")
        for i, x in enumerate((PX0 + 0.010, PX1 - 0.010)):
            screw(sf, (x, PY0, 0.010), (0, -1, 0), ang=0.4 + 1.1 * i)
        sl = P("prog_screws_side", "screw")
        for i, y in enumerate((PY0 + 0.020, PY1 - 0.020)):
            screw(sl, (PX0, y, 0.012), (-1, 0, 0), ang=1.3 - 0.9 * i)
        vt = P("prog_vents", "hole")
        for k in range(7):
            face_quad(vt, (PX0 - 0.00005, -0.046 + 0.0075 * k, 0.027), (-1, 0, 0), (0, 0, 1), 0.0065, 0.0009)
        parts += [sf, sl, vt]
    # lever socket: a base, a top plate with slots (the decal), the lever boss, the axis, the lever, the ball
    zb = P("zif_base", "zif")
    g.box(zb, ZIF_CX - ZIF_L / 2, ZIF_CX + ZIF_L / 2, ZIF_CY - ZIF_W / 2, ZIF_CY + ZIF_W / 2, ZP, ZP + 0.0055,
          **({"r": 0.0004, "seg": 1} if fine else {}))
    parts.append(zb)
    zt = P("zif_top", "zif")
    g.box(zt, ZIF_CX - ZIF_L / 2 + 0.0006, ZIF_CX + ZIF_L / 2 - 0.0006, ZIF_CY - ZIF_W / 2 + 0.0006,
          ZIF_CY + ZIF_W / 2 - 0.0006, ZP + 0.0055, ZIF_T, **({"r": 0.0008, "seg": 1} if fine else {}))
    parts.append(zt)
    zh = P("zif_lever_boss", "zif")
    g.box(zh, LEV_X0 - 0.004, LEV_X0 + 0.0035, LEV_Y - 0.0012, ZIF_CY - ZIF_W / 2 + 0.001, ZP, ZP + 0.0078,
          **({"r": 0.0005, "seg": 1} if fine else {}))
    if fine:
        # latch that the lowered lever lies in
        g.box(zh, LEV_X1 + 0.0055, LEV_X1 + 0.0085, LEV_Y - 0.0006, ZIF_CY - ZIF_W / 2 + 0.0005, ZP,
              LEV_Z + 0.0004)
    parts.append(zh)
    lv = P("zif_lever", "lever")
    g.pipe(lv, [(LEV_X0 + 0.0005, LEV_Y - 0.0016, LEV_Z), (LEV_X0 - 0.004, LEV_Y - 0.0016, LEV_Z),
                (LEV_X1 + 0.004, LEV_Y - 0.0017, LEV_Z), (LEV_X1 + 0.0012, LEV_Y - 0.0017, LEV_Z)],
           0.0011, 10 if fine else 4)
    if fine:
        g.cyl(lv, (LEV_X0 - 0.0002, LEV_Y - 0.0013, LEV_Z), "y", 0.0019, 0.0008, 10)      # lever axis
    parts.append(lv)
    kb = P("zif_knob", "zifknob")
    ball(kb, (LEV_X1, LEV_Y - 0.0017, LEV_Z), 0.0029, 8 if fine else 5, 5 if fine else 3)
    parts.append(kb)
    # K573RF5 in the socket (window and key as a decal), leads in the ZIF slots
    parts += dip("chip", "chip", CHIP_CX, ZIF_CY, "x", CHIP_L, CHIP_Z0, CHIP_Z1, 12, ZIF_T, fine)
    # spare IC, leads in the foam
    fm = P("foam", "foam")
    g.box(fm, *FOAM, **({"r": 0.0012, "seg": 1} if fine else {}))
    parts.append(fm)
    parts += dip("spare", "spare", SP_CX, SP_CY, "y", SPARE_L, SP_Z0, SP_Z1, 14, FOAM[5] - 0.0003, fine)
    # AL307 LEDs in black holders: red blinks (ozl_lamp), green burns (ozl_lamp_work)
    for i, (x, reg) in enumerate(LEDS):
        grp = {"led_r": SEL_BLINK, "led_g": SEL_LAMP}.get(reg, "body")
        led = P("led%d" % i, reg, group=grp)
        if fine:
            lathe(led, (x, LED_Y, ZP), (0, 0, 1), [(0.0029, 0.0010), (0.0029, 0.0020), (0.0025, 0.0022),
                                                    (0.0025, 0.0054), (0.0018, 0.0071), (0.0, 0.0078)], 10)
        else:
            lathe(led, (x, LED_Y, ZP), (0, 0, 1), [(0.0029, 0.0), (0.0025, 0.0022), (0.0025, 0.0054), (0.0, 0.0078)], 6)
        parts.append(led)
    if fine:
        rg = P("led_rings", "ledring")
        for x, _ in LEDS:
            lathe(rg, (x, LED_Y, ZP), (0, 0, 1), [(0.0036, 0.0), (0.0029, 0.0010)], 10)
        parts.append(rg)
    # toggles
    hw = P("tog_hw", "nut")
    tg = P("tog_levers", "toggle")
    for x, s in TOGGLES:
        toggle(hw, tg, (x, TOG_Y, ZP), (0, 0, 1), (0.0, s * math.sin(TOG_TILT), math.cos(TOG_TILT)), fine)
    parts += [hw, tg]
    # wafer switch: a skirt with a chamfer, a cap, a white mark at "2"
    kn = P("knob", "knob")
    if fine:
        lathe(kn, (KNOB_X, KNOB_Y, ZP), (0, 0, 1),
              [(0.0090, 0.0), (0.0090, 0.0012), (0.0083, 0.0027), (0.0066, 0.0031), (0.0066, 0.0118),
               (0.0060, 0.0128), (0.0, 0.0130)], 20)
    else:
        lathe(kn, (KNOB_X, KNOB_Y, ZP), (0, 0, 1),
              [(0.0090, 0.0), (0.0066, 0.0031), (0.0062, 0.0130), (0.0, 0.0130)], 10)
    parts.append(kn)
    pt = P("pointer", "pointer")
    g.box(pt, -0.0006, 0.0006, 0.0010, 0.0055, 0.0, 0.0003, frame=rot_frame(KNOB_X, KNOB_Y, ZP + 0.0130, KNOB_A))
    parts.append(pt)
    # the ribbon leaves through a rubber strip in the back wall
    gr = P("ribbon_grommet", "grommet")
    g.box(gr, RXC - RW / 2 - 0.002, RXC + RW / 2 + 0.002, PY1, PY1 + 0.0015, EXIT_Z - 0.004, EXIT_Z + 0.004)
    parts.append(gr)
    if not fine:
        for i, (x, reg) in enumerate(JACKS):
            jk = P("jack%d" % i, reg)
            lathe(jk, (x, PY0, JACK_Z), (0, -1, 0), [(0.0042, 0.0), (0.0035, 0.0030), (0.0, 0.0030)], 6)
            parts.append(jk)
    else:
        # "banana" sockets on the face: a coloured bushing with a chamfer and a dark hole
        for i, (x, reg) in enumerate(JACKS):
            jk = P("jack%d" % i, reg)
            lathe(jk, (x, PY0, JACK_Z), (0, -1, 0), [(0.0042, 0.0), (0.0042, 0.0016), (0.0035, 0.0030),
                                                      (0.0019, 0.0030)], 8)
            use(jk, "hole")
            lathe(jk, (x, PY0, JACK_Z), (0, -1, 0), [(0.0019, 0.0030), (0.0019, 0.0008), (0.0, 0.0008)], 8)
            parts.append(jk)
        # SG-5 power socket on the back wall: a flange and a black insert
        dn = P("din", "din")
        lathe(dn, (0.002, PY1, 0.022), (0, 1, 0), [(0.0090, 0.0), (0.0090, 0.0008), (0.0074, 0.0012)], 6)
        use(dn, "insert")
        lathe(dn, (0.002, PY1, 0.022), (0, 1, 0), [(0.0074, 0.0012), (0.0062, 0.0014), (0.0062, 0.0006),
                                                   (0.0, 0.0006)], 6)
        parts.append(dn)
    return parts


def ribbon_path(lod):
    """Ribbon axis in the YZ plane (x = RXC): from the back wall down to the shelf, an accordion of two
    layers back and forth, and a fold up into the connector body lying on the ribbon."""
    k = 0 if lod else 1
    yz = [(PY1 - 0.004, EXIT_Z)]
    yz += arc(PY1 + 0.004, EXIT_Z - 0.009, 0.009, 90, 0, 2 * k + 1)
    r1 = 0.0069
    yz += arc(PY1 + 0.013 + r1, 0.0075, r1, 180, 270, 2 * k + 1)
    zl1, zl2 = RT / 2, RT / 2 + 0.0024
    rf = (zl2 - zl1) / 2
    yz += arc(F1_Y, zl1 + rf, rf, -90, 90, 2 * k + 2)
    r2 = (HOOD_ZM - zl2) / 2
    yz += arc(F2_Y, zl2 + r2, r2, 270, 90, 3 * k + 2)
    yz += [(HOOD_Y0 + 0.006, HOOD_ZM), (HOOD_Y0 + 0.011, HOOD_ZM)]
    return [(RXC, y, z) for y, z in yz]


def build_ribbon(spec):
    fine = spec["lod"] == 0
    parts = []
    rb = P("ribbon", "ribbon")
    g.sweep(rb, ribbon_path(spec["lod"]), (1, 0, 0), RT / 2, RW / 2)
    parts.append(rb)
    # connector body: a hood with a chamfer and a ribbon clamp tail
    hd = P("dsub_hood", "hood")
    if fine:
        g.box(hd, RXC - 0.019, RXC + 0.019, HOOD_Y0 + 0.005, HOOD_Y1, HOOD_Z0, HOOD_Z1, r=0.0015, seg=1)
        g.box(hd, RXC - 0.0175, RXC + 0.0175, HOOD_Y0, HOOD_Y0 + 0.0058, HOOD_Z0 + 0.0011, HOOD_Z1 - 0.0011,
              r=0.0008, seg=1)
    else:
        g.prism(hd, [(RXC - 0.016, HOOD_Y0), (RXC + 0.016, HOOD_Y0), (RXC + 0.020, HOOD_Y1),
                     (RXC - 0.020, HOOD_Y1)], (0, 1), HOOD_Z0, HOOD_Z1)
    parts.append(hd)
    fl = P("dsub_flange", "dshell")
    g.box(fl, RXC - 0.0265, RXC + 0.0265, HOOD_Y1, HOOD_Y1 + 0.0008, HOOD_ZM - 0.00625, HOOD_ZM + 0.00625)
    parts.append(fl)
    ds = P("dsub_shell", "dshell")
    g.prism(ds, [(RXC - 0.0195, HOOD_ZM + 0.004), (RXC - 0.0170, HOOD_ZM - 0.004), (RXC + 0.0170, HOOD_ZM - 0.004),
                 (RXC + 0.0195, HOOD_ZM + 0.004)], (0, 2), HOOD_Y1 + 0.0008, HOOD_Y1 + 0.0068)
    parts.append(ds)
    di = P("dsub_insert", "insert")
    g.prism(di, [(RXC - 0.0185, HOOD_ZM + 0.0032), (RXC - 0.0162, HOOD_ZM - 0.0032), (RXC + 0.0162, HOOD_ZM - 0.0032),
                 (RXC + 0.0185, HOOD_ZM + 0.0032)], (0, 2), HOOD_Y1 + 0.0010, HOOD_Y1 + 0.0071)
    parts.append(di)
    # thumb screws with heads at the sides of the hood
    th = P("dsub_thumbscrews", "thumb")
    for s in (-1, 1):
        c = (RXC + s * 0.0235, HOOD_Y1 - 0.0004, HOOD_ZM)
        if fine:
            lathe(th, c, (0, -1, 0), [(0.0034, 0.0), (0.0036, 0.0006), (0.0036, 0.0050), (0.0028, 0.0057),
                                      (0.0, 0.0058)], 6)
        else:
            lathe(th, c, (0, -1, 0), [(0.0036, 0.0), (0.0036, 0.0050), (0.0, 0.0058)], 6)
    parts.append(th)
    return parts


# --- eraser ---------------------------------------------------------------------------------------
def frame_bar(part, along, a0, a1, c, out_s, b, z0, z1):
    """Window frame bar along along from a0 to a1: the section is an angle of width b outwards from the
    glass edge c (out_s says which way), with a chamfer towards the glass."""
    poly = [(c, z0), (c + out_s * b, z0), (c + out_s * b, z1), (c + out_s * 0.0009, z1), (c, z1 - 0.0006)]
    return g.prism(part, poly, (1, 2) if along == "x" else (0, 2), a0, a1)


def build_eraser(spec):
    fine = spec["lod"] == 0
    parts = []
    bx = P("eraser_box", "enamel")
    g.box(bx, EX0, EX1, EY0, EY1, EFOOT, EZ1, r=0.002, seg=2 if fine else 1)
    parts.append(bx)
    if fine:
        ft = P("eraser_feet", "feet")
        for x in (EX0 + 0.010, EX1 - 0.010):
            for y in (EY0 + 0.012, EY1 - 0.012):
                lathe(ft, (x, y, 0.0), (0, 0, 1), [(0.0056, 0.0), (0.0066, EFOOT)], 4, phase=math.pi / 4)
        parts.append(ft)
        # cover screws on the right side, slots above the lamp
        ss = P("eraser_screws", "screw")
        for i, y in enumerate((EY0 + 0.012, EY1 - 0.012)):
            screw(ss, (EX1, y, 0.053), (1, 0, 0), ang=0.2 + 1.4 * i)
        vt = P("eraser_vents", "hole")
        for k in range(6):
            face_quad(vt, (EX1 + 0.00005, -0.062 + 0.010 * k, 0.033), (1, 0, 0), (0, 0, 1), 0.0075, 0.0010)
        parts += [ss, vt]
    # tray: a face with a chamfer, a dark gap around it, a bracket handle made of a strip
    dr = P("drawer", "drawer")
    g.box(dr, EX0 + 0.006, EX1 - 0.006, EY0 - 0.0015, EY0 + 0.0002, 0.008, 0.030,
          **({"r": 0.0006, "seg": 1} if fine else {}))
    parts.append(dr)
    if fine:
        gp = P("drawer_gap", "hole")
        face_quad(gp, ((EX0 + EX1) / 2, EY0 - 0.00005, 0.019), (0, -1, 0), (1, 0, 0), (EX1 - EX0) / 2 - 0.0054,
                  0.0115)
        parts.append(gp)
    hd = P("drawer_handle", "handle")
    hy = EY0 - 0.0015
    if fine:
        pts = [(0.0570, hy + 0.0004), (0.0570, hy - 0.0040), (0.0576, hy - 0.0054), (0.0590, hy - 0.0060),
               (0.0760, hy - 0.0060), (0.0774, hy - 0.0054), (0.0780, hy - 0.0040), (0.0780, hy + 0.0004)]
    else:
        pts = [(0.0570, hy + 0.0004), (0.0575, hy - 0.0058), (0.0775, hy - 0.0058), (0.0780, hy + 0.0004)]
    g.sweep(hd, [(x, y, 0.019) for x, y in pts], (0, 0, 1), 0.0005, 0.0022)
    parts.append(hd)
    # neon lamp in a chrome fitting with a knurled ring: the orange lens is ozl_lamp_work
    bz = P("neon_bezel", "bezel")
    ln = P("neon_lens", "neon", group=SEL_LAMP)
    nb = (NEON[0], EY0, NEON[1])
    if fine:
        lathe(bz, nb, (0, -1, 0), [(0.0055, 0.0), (0.0055, 0.0016), (0.0047, 0.0028), (0.0038, 0.0029)], 8,
              flute=((0, 1), 0.93))
        lathe(ln, nb, (0, -1, 0), [(0.0038, 0.0029), (0.0036, 0.0040), (0.0025, 0.0049), (0.0, 0.0052)], 10)
    else:
        lathe(bz, nb, (0, -1, 0), [(0.0055, 0.0), (0.0050, 0.0029), (0.0038, 0.0029)], 6)
        lathe(ln, nb, (0, -1, 0), [(0.0038, 0.0029), (0.0, 0.0052)], 6)
    parts += [bz, ln]
    # power toggle on the face, lever forward and up
    hw = P("etog_hw", "nut")
    tg = P("etog_lever", "toggle")
    toggle(hw, tg, (ETOG[0], EY0, ETOG[1]), (0, -1, 0), (0.0, -math.cos(TOG_TILT), math.sin(TOG_TILT)), fine)
    parts += [hw, tg]
    # timer: a knob with a skirt and a white mark (bone ozl_work turns when working), scale ticks on the face
    tb = (TIMER[0], EY0, TIMER[1])
    tk = P("timer_knob", "knob", group=SEL_WORK)
    if fine:
        lathe(tk, tb, (0, -1, 0), [(0.0070, 0.0), (0.0070, 0.0015), (0.0061, 0.0024), (0.0050, 0.0027),
                                   (0.0050, 0.0090), (0.0045, 0.0099), (0.0, 0.0101)], 16)
    else:
        lathe(tk, tb, (0, -1, 0), [(0.0070, 0.0), (0.0052, 0.0026), (0.0050, 0.0101), (0.0, 0.0101)], 6)
    parts.append(tk)
    tp = P("timer_pointer", "pointer", group=SEL_WORK)
    d = Vector((math.cos(TIMER_A), 0.0, math.sin(TIMER_A)))
    fr = g.Frame((TIMER[0], EY0 - 0.0101, TIMER[1]), (-d.z, 0.0, d.x), d, (0, -1, 0))
    g.box(tp, -0.0005, 0.0005, 0.0008, 0.0041, 0.0, 0.0003, frame=fr)
    parts.append(tp)
    if fine:
        tt = P("timer_ticks", "tick")
        for k in range(12):
            t = math.radians(90 - 30 * k)
            big = k % 3 == 0
            rc = 0.0088 if big else 0.0084
            face_quad(tt, (TIMER[0] + rc * math.cos(t), EY0 - 0.00005, TIMER[1] + rc * math.sin(t)), (0, -1, 0),
                      (math.cos(t), 0, math.sin(t)), 0.0009 if big else 0.0005, 0.00022)
        parts.append(tt)
    # window: an angle frame (the glass is recessed) and the UVS glass (ozl_lamp_work)
    x0, x1, y0, y1 = WIN
    fm = P("win_frame", "frame")
    b = 0.003
    gl = P("uv_glass", "uvglass", group=SEL_LAMP)
    if fine:
        zt = EZ1 + 0.0012
        frame_bar(fm, "x", x0 - b, x1 + b, y0, -1, b, EZ1 - 0.0002, zt)
        frame_bar(fm, "x", x0 - b, x1 + b, y1, 1, b, EZ1 - 0.0002, zt)
        frame_bar(fm, "y", y0, y1, x0, -1, b, EZ1 - 0.0002, zt)
        frame_bar(fm, "y", y0, y1, x1, 1, b, EZ1 - 0.0002, zt)
        g.box(gl, x0, x1, y0, y1, EZ1 - 0.0002, EZ1 + 0.0005)
    else:
        g.box(fm, x0 - b, x1 + b, y0 - b, y1 + b, EZ1 - 0.0002, EZ1 + 0.0007)
        g.box(gl, x0, x1, y0, y1, EZ1 + 0.0007, EZ1 + 0.0011)
    parts += [fm, gl]
    gr = P("cord_grommet", "grommet")
    if fine:
        lathe(gr, (0.092, EY1, 0.014), (0, 1, 0), [(0.0042, 0.0), (0.0042, 0.0010), (0.0034, 0.0022),
                                                   (0.0024, 0.0024)], 8)
    else:
        g.cyl(gr, (0.092, EY1 + 0.0012, 0.014), "y", 0.0040, 0.0024, 6, r2=0.0032)
    parts.append(gr)
    return parts


def cord_points():
    """Eraser cord: from the bushing in the back wall down to the shelf, back along the right edge, in a
    loop to the left - and the last segment along the axis of the plug tail (no kink at the plug)."""
    zr = CORD_R
    return [(0.092, EY1 + 0.0005, 0.014), (0.092, EY1 + 0.006, 0.0138), (0.0925, EY1 + 0.012, 0.0115),
            (0.0935, EY1 + 0.018, 0.0072), (0.095, EY1 + 0.025, 0.0036), (0.0965, 0.046, zr), (0.098, 0.058, zr),
            (0.0975, 0.068, zr), (0.0950, 0.0755, 0.0024), (0.0895, 0.0795, 0.0032), (0.0835, 0.0795, 0.0050),
            (0.0785, 0.0785, 0.0069), (0.0755, 0.0780, 0.0078), (0.0725, 0.0780, PLUG_ZM)]


def build_cord(spec):
    fine = spec["lod"] == 0
    parts = []
    cd = P("cord", "cord")
    pts = cord_points()
    g.pipe(cd, spline(pts, 2) if fine else pts, CORD_R, 6 if fine else 4)
    parts.append(cd)
    x0, x1, y0, y1, z0, z1 = PLUG
    yc = (y0 + y1) / 2
    pl = P("plug", "plug")
    g.box(pl, x0, x1, y0, y1, z0, z1, **({"r": 0.004, "seg": 1} if fine else {}))
    if fine:
        lathe(pl, (x1 - 0.0005, yc, PLUG_ZM), (1, 0, 0), [(0.0062, 0.0), (0.0062, 0.0010), (0.0040, 0.0050),
                                                          (0.0024, 0.0090)], 8)
    else:
        lathe(pl, (x1 - 0.0005, yc, PLUG_ZM), (1, 0, 0), [(0.0062, 0.0), (0.0024, 0.0090)], 4)
    parts.append(pl)
    pn = P("plug_pins", "pins")
    for y in (y0 + 0.0045, y1 - 0.0045):
        lathe(pn, (x0 + 0.0005, y, PLUG_ZM), (-1, 0, 0), [(0.0020, 0.0), (0.0020, 0.0170), (0.0013, 0.0188),
                                                         (0.0, 0.0190)] if fine else
              [(0.0020, 0.0), (0.0020, 0.0175), (0.0, 0.0190)], 6 if fine else 4)
    parts.append(pn)
    return parts


def build_lod(spec):
    parts = build_programmer(spec) + build_ribbon(spec) + build_eraser(spec) + build_cord(spec)
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """Three convex hulls: the programmer (with the ZIF and the knob), the eraser (with the timer knob and
    the tray), the ribbon with the connector; the cord and plug have no collision (like the M69 cable).
    The mass is the item weight in the mod, 0.8 kg."""
    prog = kx.box_pts(PX0 - LIP, PX1 + LIP, PY0 - LIP, PY1 + LIP, 0.0, ZP)
    prog += kx.box_pts(ZIF_CX - ZIF_L / 2, ZIF_CX + ZIF_L / 2, ZIF_CY - ZIF_W / 2, ZIF_CY + ZIF_W / 2, ZP, CHIP_Z1)
    prog += kx.box_pts(KNOB_X - 0.009, KNOB_X + 0.009, KNOB_Y - 0.009, KNOB_Y + 0.009, ZP, ZP + 0.013)
    eras = kx.box_pts(EX0, EX1, EY0 - 0.0105, EY1, 0.0, EZ1 + 0.0012)
    conn = kx.box_pts(RXC - 0.0265, RXC + 0.0265, PY1 + 0.002, HOOD_Y1 + 0.0071, 0.0, HOOD_Z1)
    comps = [(prog, kx.PEN + r"\metalplate.rvmat"), (eras, kx.PEN + r"\metalplate.rvmat"),
             (conn, kx.PEN + r"\metalplate.rvmat")]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    memory = {
        # inventory preview camera: from the front left and above (invView is where the camera is)
        "invView": [(-0.15, -0.46, 0.33)],
        "ce_center": [(0.0, 0.005, 0.03)],
        "ce_radius": [(0.15, 0.005, 0.03)],
        # axis of the timer knob (bone ozl_work): from the eraser face outwards
        "ozl_work_axis": [(TIMER[0], EY0, TIMER[1]), (TIMER[0], EY0 - 0.02, TIMER[1])],
    }
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 0.8, memory, bbox


# camera angles: the --look preview uses the first four (the "working" state the first two)
SHOTS = [
    ("front", (-0.16, -0.48, 0.30), (0.0, -0.005, 0.03), 60),
    ("eraser", (0.24, -0.26, 0.17), (0.068, -0.045, 0.035), 70),
    ("panel", (-0.07, -0.25, 0.25), (-0.045, -0.035, 0.045), 55),
    ("zif", (-0.03, -0.11, 0.14), (-0.045, 0.008, 0.05), 50),
    ("top", (0.0, -0.08, 0.52), (0.0, 0.002, 0.03), 45),
    ("back", (0.18, 0.46, 0.28), (0.0, 0.03, 0.02), 50),
]
M.look_shots = (4, 2)

M.run(build_lod, collision, SHOTS, row_step=0.30, row_shot=((0.15, -1.0, 0.33), (0.15, 0, 0.04)))
