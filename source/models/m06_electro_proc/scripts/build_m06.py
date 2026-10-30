"""M06 - instrument rack: the Scientists' Electronics Analyzer (OZL_Eco_Proc_Electro).
Analyzer: cargo 4x4, no modules (analyzers and terminals have none).

    blender --background --python build_m06.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (screens "off" and the "work" frames,
instrument faces, the display, windows, limbs, the board, the tag, signs).

The rack is the B5 base: a floor instrument cabinet 800 x 2000 x 700 mm - width and height from the
GOST 28601.2-90 row of cabinets (IEC 297: width 600/800, height ~2000 at 42 units), depth between
the rows 600 and 800 - for the deepest instrument (S1-65A, 502 mm) with cables behind it. The opening
between the rails is 690 mm - two benchtop instruments ~312 mm wide side by side.

The contents are benchtop instruments on the shelves of the cells (sizes W x H x D from instrument
sellers' data sheets and type descriptions):
- oscilloscope S1-65A - 348 x 200 x 502 mm, 16 kg, screen 8 x 10 divisions;
- oscilloscope S1-94 - 100 x 190 x 300 mm, screen 60 x 40 mm (USSR State Register of Measuring
  Instruments 06791-78, as in M05);
- millivoltmeter V3-38 - ~125 x 185 x 270 mm (the V3-38M case is the same);
- AF signal generator G3-118 - 312 x 133 x 322 mm, 7.5 kg, decade frequency setting, an output voltmeter;
- frequency counter Ch3-63 - 312 x 95 x 335 mm, 6 kg, 8-digit display;
- recorder KSP4 - 400 x 400 x 367 mm, field 250 mm (State Register 04244-81, as in M04).
Below the instruments is a pull-out shelf at 0.83 m: a block with a knife-edge connector holding the
probe board, the oscilloscope and voltmeter probes. Under the shelf a compartment with doors, above
the recorder a ventilation grille.

Look: "dayz" (matte, dirtier, coloured AO); the Scientists' equipment is clean: no rust, enamel worn
at the handles. The rack is its own copy of the B5 base with cabinet details (m06_rack.py). The
recorder tape in the window has its own texture with "work" frames, the 0..100 scale lies exactly
above the tape field, and the pen trace on the tape is only under the pen. On the shelf the probe
board stands in a textolite block with a knife-edge connector; the oscilloscope probe hangs on the
board's test loop with its ground clip on the block terminal, the voltmeter probe lies on the record
sheet. Small props are vanilla DayZ items through proxies (kvanilla): pliers, screwdriver, a record
sheet and pen, a 9 V battery on the shelf; tape on the counter; an electrician kit on the generator.

Work look (the "work" loop, OZL_WorkFx):
- ozl_screen, ozl_screen_2, ozl_screen_3 - the screens of the S1-65A, S1-94 and the Ch3-63 display:
  own textures (sections crt, crt2, led; flat UV 0..1): "off" and "work" frames (frames);
- ozl_screen_4 - the recorder tape in the window: own texture (section chart), 72 frames of 0.1 s -
  the tape creeps down, under the pen is the trace the pen writes in that same second (m06_chart.py);
  it does not glow (it is not in onSelections);
- ozl_lamp - "power" lamps (lit at work), ozl_lamp_2 - the Ch3-63 count lamp and the red panel lamp
  (blink): atlas _on;
- the V3-38 and G3-118 needles are the bones ozl_needle and ozl_needle_2 (rotation, 0 is the scale
  zero, 1 is the end, 80 degrees clockwise, the axis points to the person, as in M08); at work they
  wobble (wobble) on their own sources;
- the recorder pen is the bone ozl_pen (translation along the scale, a 1 m axis from the field zero:
  offset in metres); three translations on three sources ozl_pen, ozl_pen_2, ozl_pen_3 add up (each
  wobble) - the pen writes an irregular curve, the same as on the tape frames; at rest the pen is at
  the field zero (on "0" of the scale).
In the "work" preview (states on, move) the needles are rotated and the pen is shifted to the middle
of the swing: krender.place_look and place are extended here with a group rotation (pose_move), the
kit is untouched.

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
import m06_bits as b  # noqa: E402
import m06_chart as CHT  # noqa: E402
import m06_rack as rk  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
X0, X1, Y0, Y1, H = -0.40, 0.40, -0.35, 0.35, 2.00          # rack
XI0, XI1 = rk.rack_opening(X0, X1)                           # opening between the rails
ST = rk.SHELF_T
YF = Y0 + 0.012                                              # face of the instruments
Y_FACE = YF - 0.0015                                         # faces of the screens, instruments, display
# cells from bottom to top
Z_DOOR, Z_SLIDE, Z_A, Z_B, Z_P, Z_R, Z_V, Z_TOP = 0.10, 0.76, 0.86, 1.06, 1.30, 1.38, 1.84, 1.96
CELLS = [(Z_DOOR, Z_SLIDE, "doors"), (Z_SLIDE, Z_A, "slide"), (Z_A, Z_B, "open"), (Z_B, Z_P, "open"),
         (Z_P, Z_R, "blank"), (Z_R, Z_V, "open"), (Z_V, Z_TOP, "vent")]
# pull-out shelf, the mat on it
ZS, PULL, SDEPTH = 0.825, 0.30, 0.45
TY0, TY1 = Y0 - PULL, Y0 - PULL + SDEPTH
ZM = ZS + 0.003
# doors: face, handles, lock, tag (as in m06_rack)
YD = Y0 - 0.018
XM = 0.0
ZH = Z_DOOR + 0.003 + 0.40                                   # middle of the door handles
ZL = Z_SLIDE - 0.003 - 0.10                                  # lock
TAG = (-0.21, Z_SLIDE - 0.075)
# instruments: (x0, x1, z0, z1, depth); the case stands on feet FOOT
FOOT = 0.006
G3 = (-0.335, -0.023, Z_A + ST, Z_A + ST + 0.133, 0.322)     # G3-118
CH = (0.023, 0.335, Z_A + ST, Z_A + ST + 0.095, 0.335)       # Ch3-63
C1 = (-0.335, 0.013, Z_B + ST, Z_B + ST + 0.200, 0.502)      # S1-65A
C94 = (0.050, 0.150, Z_B + ST, Z_B + ST + 0.190, 0.300)      # S1-94
V3 = (0.195, 0.320, Z_B + ST, Z_B + ST + 0.185, 0.270)       # V3-38
KS = (-0.200, 0.200, Z_R + ST, Z_R + ST + 0.400, 0.367)      # KSP4
# instrument faces: screens, meters, display (x0, x1, z0, z1)
CRT = (C1[0] + 0.030, C1[0] + 0.155, C1[2] + 0.050, C1[2] + 0.150)
CRT94 = (C94[0] + 0.017, C94[1] - 0.017, C94[3] - 0.068, C94[3] - 0.024)
M_G3 = (G3[0] + 0.020, G3[0] + 0.100, G3[3] - 0.070, G3[3] - 0.014)
WIN_G3 = (G3[0] + 0.111, G3[0] + 0.239, G3[3] - 0.040, G3[3] - 0.012)
M_V3 = (V3[0] + 0.012, V3[1] - 0.012, V3[3] - 0.092, V3[3] - 0.014)
LED = (CH[0] + 0.055, CH[0] + 0.235, CH[3] - 0.050, CH[3] - 0.020)
# recorder
WX0, WX1, WZ0, WZ1 = KS[0] + 0.02, KS[1] - 0.02, KS[2] + 0.115, KS[2] + 0.385
TX0, TX1 = -0.14, 0.14
TAPE_X = 0.0
FX0 = TX0 + CHT.FIELD_X0                                     # tape field zero = the pen at rest
Y_CHART = Y0 + 0.030
CH_Z1 = WZ0 + CHT.CHART_H                                    # top of the visible tape (the scale is above)
Z_PEN = CH_Z1 - CHT.PEN_D                                    # pen line
SCALE = (WX0 + 0.01, WX1 - 0.01, WZ1 - 0.035, WZ1 - 0.008)
YDR = Y0 - 0.010                                             # face of the recorder door
# the tape and scale are the same as in m06_chart.py (make_decals.py draws the tape frames): the 0..100 scale is
# above the field
assert abs(TX1 - TX0 - CHT.CHART_W) < 1e-9 and abs(CH_Z1 - (WZ1 - 0.036)) < 1e-9 and abs(Z_PEN - (WZ1 - 0.066)) < 1e-9
assert abs(SCALE[1] - SCALE[0] - CHT.SCALE_W) < 1e-9 and abs((SCALE[0] + SCALE[1]) / 2 - FX0 - CHT.FIELD_W / 2) < 1e-9
# block and board on the shelf
FX = (-0.21, 0.07)                                           # block along x
FY0, FY1 = TY0 + 0.15, TY0 + 0.23
FZ1 = ZM + 0.035                                             # top of the block
BX0, BX1, BZ1 = -0.18, 0.04, FZ1 + 0.11                       # board: x, top
BY = (FY0 + FY1) / 2                                         # board plane
YB = BY - 0.0008                                             # board face
TP = (BX0 + 0.030, YB - 0.005, 0.925)                        # test loop: the oscilloscope probe sits on it
GND = (FX[0] + 0.018, FY0 + 0.018)                           # block ground terminal
FBNC = (FX[1] - 0.030, ZM + 0.018)                           # block input socket (face y = FY0)


def meter_pivot(r, wpx, hpx):
    """Needle axis and scale radius from the face picture (make_decals.make_meter): (x, z, r)."""
    x0, x1, z0, z1 = r
    rp = min(hpx * 0.80, wpx * 0.50)
    cy = hpx * 0.10 + rp * 1.27
    return (x0 + x1) / 2, z1 - cy / hpx * (z1 - z0), rp / wpx * (x1 - x0)


PIV_V3 = meter_pivot(M_V3, 384, 288)
PIV_G3 = meter_pivot(M_G3, 320, 224)
Y_NEEDLE = YF - 0.0026                                       # needles are between the scale and the glass
NEEDLE_REST = -40.0                                          # scale zero: 40 degrees left of vertical
NEEDLE_SWEEP = math.radians(80.0)                            # phase 1 is the scale end (clockwise)

LOD_SPECS = [
    dict(lod=0, bev=2, sides=16),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "rk": ("hammer", 0.5), "rk_rail": ("rail", 0.8), "rk_panel": ("hammer_panel", 0.6), "rk_door": ("hammer_door", 0.6),
    "rk_front": ("hammer_front", 0.8), "rk_inner": ("dark", 0.3), "grille_v": ("grille_v", 0.8),
    "steel": ("steel", 1.2), "chrome": ("chrome", 1.4), "black": ("black", 1.2), "rubber": ("rubber", 0.6),
    "tag": ("tag", 6.0), "mat": ("mat", 0.6), "seal": ("seal", 2.0),
    "inst": ("inst", 0.6), "inst_frame": ("inst_frame", 1.0), "cream": ("cream", 1.6),
    "dial": ("dial", 4.0), "windows": ("windows", 4.0), "needle": ("needle", 3.0),
    "knob": ("knob", 1.6), "knob_red": ("knob_red", 2.0), "ptr": ("ptr", 3.0), "key": ("key", 1.6),
    "lamp_g": ("lamp_g_off", 2.0), "lamp_r": ("lamp_r_off", 2.0), "bezel": ("bezel", 1.2),
    "rec_case": ("rec_case", 1.0), "chart": ("chart", 2.2), "pen": ("pen", 2.0), "drum": ("rubber", 1.0),
    "fixture": ("fixture", 1.6), "pcb": ("pcb", 6.0), "chip": ("chip", 4.0), "lead": ("lead", 3.0),
    "resistor": ("resistor", 4.0), "cap_el": ("cap_el", 3.0), "cap_top": ("lead", 3.0), "can": ("can", 3.0),
    "trim": ("trim", 4.0), "brass": ("brass", 2.0), "cap_red": ("cap_red", 2.0),
    "probe_g": ("probe_g", 1.6), "probe_r": ("probe_r", 1.6), "cable": ("cable", 0.6),
    "cable_grey": ("cable_grey", 0.6),
}

# =============================================================================
# Materials
# =============================================================================


def decal(name, center, size, y_face, eps=0.0012):
    return (os.path.join(WORK, name), "y", -1, ("x", "z"), center, size, (y_face - eps, y_face + eps))


def rect(name, r, y_face):
    x0, x1, z0, z1 = r
    return decal(name, ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0), y_face)


DIALS = [rect("decal_meter_g3.png", M_G3, Y_FACE), rect("decal_meter_v3.png", M_V3, Y_FACE),
         rect("decal_scale.png", SCALE, Y0 + 0.022)]
WINDOWS = [rect("decal_g3_windows.png", WIN_G3, Y_FACE)]
PCBD = [rect("decal_pcb.png", (BX0, BX1, FZ1 + 0.002, BZ1), YB)]
TAGD = [rect("decal_tag.png", (TAG[0] - 0.034, TAG[0] + 0.034, TAG[1] - 0.014, TAG[1] + 0.014), YD - 0.0008)]
GROUND = (0.29, 0.24)                                        # ground bolt on the left side panel: y, z
GNDD = [(os.path.join(WORK, "decal_ground.png"), "x", -1, ("y", "z"), (GROUND[0], GROUND[1] + 0.038), (0.030, 0.030),
         (X0 - 0.002, X0 + 0.0005))]
HV = [rect("decal_hv.png", (0.303, 0.333, 1.325, 1.351), Y0 - 0.003)]

# knobs with limbs: (x, z, radius, kind, limb, mark angle)
K_C1 = [(C1[0] + 0.190 + 0.045 * i, C1[2] + 0.160 - 0.045 * j, (0.011 if j == 1 or (i, j) == (1, 2) else 0.009),
         ("skirt" if j == 1 else ("dual" if (i, j) == (1, 2) else "plain")),
         ("ring11" if j == 1 else ("ring6" if (i, j) == (1, 2) else None)), (-60, 35, 120, -15, 80, -100)[(i + 2 * j) % 6])
        for i in range(4) for j in range(3)]
# frequency decades have no limbs (the digit is in the window above the knob), the multiplier and amplitude are on
# the right
K_G3 = [(G3[0] + 0.127 + 0.032 * i, G3[2] + 0.050, 0.010, "plain", None, (0, 90, -30, 45)[i]) for i in range(4)] + \
       [(G3[0] + 0.260, G3[2] + 0.076, 0.013, "skirt", "ring6", 30), (G3[0] + 0.250, G3[2] + 0.035, 0.010, "plain", None, -45)]
K_V3 = [(V3[0] + 0.045, V3[2] + 0.055, 0.016, "skirt", "ring6", 40)]
K_94 = [(C94[0] + 0.025, C94[3] - 0.095, 0.009, "plain", None, -20), (C94[0] + 0.075, C94[3] - 0.095, 0.009, "plain", None, 70),
        (C94[0] + 0.025, C94[3] - 0.130, 0.011, "skirt", None, 110), (C94[0] + 0.075, C94[3] - 0.130, 0.011, "skirt", None, -35)]
K_CH = [(CH[0] + 0.267, CH[2] + 0.060, 0.012, "skirt", "ring6", -50)]
KNOBS = K_C1 + K_G3 + K_V3 + K_94 + K_CH
RINGS = [decal("decal_%s.png" % rg, (x, z), (r * 4.4, r * 4.4), YF) for x, z, r, _, rg, _ in KNOBS if rg]
# face controls: BNC sockets (x, z, plug present), toggles, lamps (x, z, region, selection)
BNC_C1 = [(C1[0] + 0.050, C1[2] + 0.025, True), (C1[0] + 0.110, C1[2] + 0.025, False)]
BNC_94 = [(C94[0] + 0.050, C94[2] + 0.025, False)]
BNC_V3 = [(V3[1] - 0.022, V3[2] + 0.030, True)]
BNC_G3 = [(G3[1] - 0.027, G3[2] + 0.035, True), (G3[1] - 0.027, G3[2] + 0.096, True)]
BNC_CH = [(CH[0] + 0.035, CH[2] + 0.027, True)]
SEL_SCREEN, SEL_SCREEN2, SEL_SCREEN3 = "ozl_screen", "ozl_screen_2", "ozl_screen_3"
SEL_CHART = "ozl_screen_4"                                   # recorder tape in the window (frames, no glow)
SEL_LAMP, SEL_LAMP2 = "ozl_lamp", "ozl_lamp_2"
SEL_NEEDLE, SEL_NEEDLE2, SEL_PEN = "ozl_needle", "ozl_needle_2", "ozl_pen"
LAMPS = [("c1_lamp", C1[0] + 0.150, C1[2] + 0.025, "lamp_g", SEL_LAMP),
         ("g3_lamp", G3[0] + 0.060, G3[2] + 0.030, "lamp_r", SEL_LAMP),
         ("ch_gate", CH[0] + 0.035, CH[3] - 0.031, "lamp_r", SEL_LAMP2)]

KINDS = kmats.std_kinds(floor_z=0.0)
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# grey hammer enamel: even, rare chips (laboratory), no rust; worn at the knobs
HAMMER = dict(color=kmats.lin((122, 128, 128)), under=kmats.lin((70, 74, 74)), seed=2.6, gloss=0.42, spec=0.32,
              chip=(0.70, 0.76), rust=(0.99, 1.0), rust_low=0.0, floor_z=0.0, dust=0.25, grime=0.35)
INST = dict(color=kmats.lin((112, 120, 126)), under=kmats.lin((60, 60, 62)), seed=3.3, gloss=0.42, spec=0.32,
            chip=(0.72, 0.78), rust=(0.99, 1.0), rust_low=0.0, floor_z=Z_A, dust=0.30, grime=0.25)
CREAM = dict(color=kmats.lin((214, 206, 182)), under=kmats.lin((110, 108, 100)), seed=4.4, gloss=0.40, spec=0.30,
             chip=(0.76, 0.82), rust=(0.99, 1.0), rust_low=0.0, floor_z=Z_A, dust=0.12, grime=0.15, decal_items=RINGS)
DOOR_RUB = [((XM + s * 0.04, YD - 0.01, ZH), (0.026, 0.05, 0.085), 0.55) for s in (-1, 1)] + \
           [((XM + 0.04, YD - 0.01, ZL), (0.020, 0.05, 0.020), 0.5)]
TRAY_RUB = [((0.0, TY0 - 0.02, ZS - 0.012), (0.11, 0.05, 0.025), 0.55)]


def mat_hammer(mat, origin, rub=(), bare=kmats.lin((150, 152, 150)), **kw):
    """Hammer enamel: painted metal (kmats.build_paint) with hammered dimples (dark edges, light bottoms)
    and relief; rub - [(centre, half-axes, strength)]: enamel worn by hands to primer and metal (at the
    door handles, the shelf and the lock)."""
    outs = kmats.build_paint(mat, origin, **kw)
    t = kmats.Tree.__new__(kmats.Tree)
    t.nt = mat.node_tree
    vec, sep = t.coords(origin, 17.0)
    cells = t.noise(vec, 55.0, 2.0, 0.45)
    pit = t.maprange(cells, 0.38, 0.62, 0.0, 1.0)
    col = kmats.sock(mat, outs["color"])
    col = t.mixc(t.math("MULTIPLY", pit, 0.22), col, tuple(min(1.0, c * 1.25) for c in kw["color"][:3]) + (1,))
    col = t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", 1.0, pit), 0.18), col,
                 tuple(c * 0.72 for c in kw["color"][:3]) + (1,))
    h = outs["height"]
    hh = t.math("ADD", kmats.sock(mat, h) if not isinstance(h, (int, float)) else h, t.math("MULTIPLY", pit, 0.35))
    res = dict(outs, color=kmats.Tree.ref(col), height=kmats.Tree.ref(hh))
    if rub:
        pos = sep.inputs[0].links[0].from_socket
        grain = t.maprange(t.noise(vec, 34.0, 8.0, 0.7), 0.3, 0.7, 0.55, 1.0)
        f = None
        for c, r, k in rub:
            d = t.node("ShaderNodeVectorMath")
            d.operation = "SUBTRACT"
            t.link(pos, d.inputs[0])
            d.inputs[1].default_value = c
            q = t.node("ShaderNodeVectorMath")
            q.operation = "DIVIDE"
            t.link(d.outputs[0], q.inputs[0])
            q.inputs[1].default_value = r
            ln = t.node("ShaderNodeVectorMath")
            ln.operation = "LENGTH"
            t.link(q.outputs[0], ln.inputs[0])
            near = t.maprange(ln.outputs["Value"], 0.3, 1.0, 1.0, 0.0)
            v = t.math("MULTIPLY", t.math("MULTIPLY", near, grain), k)
            f = v if f is None else t.math("MAXIMUM", f, v)
        f = t.math("ADD", f, t.math("MULTIPLY", t.noise(vec, 11.0, 10.0, 0.7), 0.25))
        prim = t.step(f, 0.42, 0.48)
        worn = t.step(f, 0.56, 0.62)
        col = t.mixc(t.math("MULTIPLY", prim, 0.75), col, kw.get("under", HAMMER["under"]))
        col = t.mixc(worn, col, bare)
        g0 = kmats.sock(mat, outs["gloss"]) if isinstance(outs["gloss"], tuple) else outs["gloss"]
        s0 = kmats.sock(mat, outs["spec"]) if isinstance(outs["spec"], tuple) else outs["spec"]
        res.update(color=kmats.Tree.ref(col), gloss=kmats.Tree.ref(t.mixf(worn, g0, 0.58)),
                   spec=kmats.Tree.ref(t.mixf(worn, s0, 0.62)))
    return res


def mat_chart(mat, origin):
    """KSP4 chart tape (atlas: the tape loop under the slot, the far-LOD tape): paper, field grid every 10
    and 50 mm, a violet pen trace only below the pen: above it the paper is still clean. The trace is
    the same curve the pen writes on the tape frames in the window (m06_chart.pen_x; the tape point at
    length L was written at the moment -L / v)."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 9.0)
    X = sep.outputs["X"]
    L = t.math("ADD", sep.outputs["Y"], sep.outputs["Z"])

    def lines(c, pitch, half):
        f = t.math("FRACT", t.math("DIVIDE", c, pitch))
        d = t.math("MINIMUM", f, t.math("SUBTRACT", 1.0, f))
        return t.math("LESS_THAN", d, half / pitch)

    field = t.math("LESS_THAN", t.math("ABSOLUTE", t.math("SUBTRACT", X, TAPE_X)), 0.1255)
    u = t.math("SUBTRACT", X, FX0)
    fine = t.math("MULTIPLY", t.math("MAXIMUM", lines(u, 0.01, 0.0006), lines(L, 0.01, 0.0006)), field)
    bold = t.math("MULTIPLY", t.math("MAXIMUM", lines(u, 0.05, 0.0011), lines(L, 0.05, 0.0011)), field)
    tx = FX0
    for _, mid, amp, n, dd in CHT.PEN:
        sw = t.math("SINE", t.math("MULTIPLY", L, -2 * math.pi * n / CHT.TAPE_RUN))
        tx = t.math("ADD", tx, t.math("MULTIPLY", t.math("ADD", mid, t.math("MULTIPLY", sw, amp)), dd))
    ink = t.math("LESS_THAN", t.math("ABSOLUTE", t.math("SUBTRACT", X, tx)), 0.0012)
    ink = t.math("MULTIPLY", ink, t.math("LESS_THAN", sep.outputs["Z"], Z_PEN + 0.0008))
    paper = t.mixc(t.maprange(t.noise(vec, 14.0, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0), kmats.lin((240, 236, 222)),
                   kmats.lin((228, 222, 200)))
    col = t.mixc(t.math("MULTIPLY", fine, 0.7), paper, kmats.lin((226, 164, 142)))
    col = t.mixc(bold, col, kmats.lin((198, 112, 90)))
    col = t.mixc(ink, col, kmats.lin((72, 48, 140)))
    return kmats.out(t, col, 0.12, 0.06, 0.0)


KINDS.update({
    "hammer": (mat_hammer, HAMMER),
    "hammer_panel": (mat_hammer, dict(HAMMER, color=kmats.lin((134, 140, 140)), seed=3.1, floor_z=Z_A, decal_items=HV)),
    "hammer_door": (mat_hammer, dict(HAMMER, seed=3.7, rub=DOOR_RUB)),
    "hammer_front": (mat_hammer, dict(HAMMER, color=kmats.lin((134, 140, 140)), seed=4.0, floor_z=Z_A, rub=TRAY_RUB)),
    "rail": ("steel", dict(seed=6.1, tone=0.30, along="z", holes=(("x", "z"), 0.016, 0.28), dust=0.2)),
    "dark": ("flat", dict(color=kmats.lin((22, 22, 24)), gloss=0.2, spec=0.1)),
    "chrome": ("steel", dict(seed=7.1, tone=0.36, along="z", gloss=0.70, spec=0.80, dust=0.1, grime=0.2)),
    "tag": ("paint", dict(CLEAN, color=kmats.lin((186, 188, 184)), gloss=0.45, spec=0.40, dust=0.1,
                          decal_items=TAGD + GNDD)),
    # shelf rubber mat: dark grey-green, worn at the edge
    "mat": ("plastic", dict(color=kmats.lin((46, 56, 52)), gloss=0.10, spec=0.06, mottle=0.10, dust=0.3, grime=0.4,
                            scuff=(0.70, 0.80))),
    "seal": ("steel", dict(seed=8.8, tone=0.24, along="z", gloss=0.30, spec=0.35, dust=0.2, grime=0.4)),
    "inst": ("paint", INST),
    "inst_frame": ("paint", dict(INST, color=kmats.lin((86, 92, 98)), seed=3.9, chip=(0.68, 0.74))),
    "cream": ("paint", CREAM),
    "dial": ("paint", dict(CLEAN, color=kmats.lin((236, 234, 224)), gloss=0.7, spec=0.5, decal_items=DIALS)),
    "windows": ("paint", dict(CLEAN, color=kmats.lin((18, 18, 18)), gloss=0.6, spec=0.4, decal_items=WINDOWS)),
    "needle": ("flat", dict(color=kmats.lin((20, 20, 20)), gloss=0.4, spec=0.3)),
    "knob": ("plastic", dict(color=kmats.lin((26, 25, 24)), gloss=0.45, spec=0.35, dust=0.15, grime=0.2,
                             scuff=(0.66, 0.74))),
    "knob_red": ("plastic", dict(color=kmats.lin((150, 30, 26)), gloss=0.45, spec=0.35, dust=0.1)),
    "ptr": ("flat", dict(color=kmats.lin((226, 224, 214)), gloss=0.4, spec=0.3)),
    "key": ("plastic", dict(color=kmats.lin((200, 196, 186)), gloss=0.40, spec=0.30, dust=0.15)),
    "bezel": ("plastic", dict(color=kmats.lin((24, 24, 25)), gloss=0.35, spec=0.25, dust=0.2, scuff=(0.7, 0.78))),
    "lamp_g_off": ("flat", dict(color=kmats.lin((34, 64, 40)), gloss=0.85, spec=0.8)),
    "lamp_r_off": ("flat", dict(color=kmats.lin((72, 24, 22)), gloss=0.85, spec=0.8)),
    "lamp_g_on": ("flat", dict(color=kmats.lin((130, 255, 140)), gloss=0.85, spec=0.8)),
    "lamp_r_on": ("flat", dict(color=kmats.lin((255, 86, 60)), gloss=0.85, spec=0.8)),
    "rec_case": ("paint", dict(INST, color=kmats.lin((52, 55, 58)), under=kmats.lin((110, 112, 114)), seed=5.1,
                               floor_z=Z_R)),
    "pen": ("plastic", dict(color=kmats.lin((170, 30, 30)), gloss=0.5, spec=0.4, dust=0.1)),
    "fixture": ("plastic", dict(color=kmats.lin((66, 50, 36)), gloss=0.40, spec=0.30, dust=0.2, mottle=0.10,
                                scuff=(0.66, 0.74))),
    "pcb": ("paint", dict(CLEAN, color=kmats.lin((34, 92, 52)), gloss=0.6, spec=0.45, decal_items=PCBD)),
    "chip": ("plastic", dict(color=kmats.lin((22, 22, 24)), gloss=0.35, spec=0.25, dust=0.1, grime=0.1,
                             scuff=(0.8, 0.9))),
    "lead": ("steel", dict(seed=7.7, tone=0.46, along="z", gloss=0.65, spec=0.7, dust=0.05, grime=0.15)),
    # MLT resistors - red-brown enamel
    "resistor": ("plastic", dict(color=kmats.lin((150, 66, 50)), gloss=0.5, spec=0.35, dust=0.05, grime=0.1)),
    "cap_el": ("plastic", dict(color=kmats.lin((40, 52, 92)), gloss=0.5, spec=0.35, dust=0.05, grime=0.1)),
    "can": ("steel", dict(seed=8.1, tone=0.42, along="z", gloss=0.6, spec=0.7, dust=0.05, grime=0.15)),
    "trim": ("plastic", dict(color=kmats.lin((46, 66, 150)), gloss=0.45, spec=0.3, dust=0.05)),
    "brass": ("paint", dict(CLEAN, color=kmats.lin((176, 140, 70)), under=kmats.lin((110, 80, 40)), seed=6.6,
                            gloss=0.6, spec=0.6)),
    "probe_g": ("plastic", dict(color=kmats.lin((92, 94, 96)), gloss=0.40, spec=0.30, dust=0.15, grime=0.2,
                                scuff=(0.64, 0.72))),
    "probe_r": ("plastic", dict(color=kmats.lin((168, 36, 28)), gloss=0.45, spec=0.3, dust=0.15)),
    "cable": ("plastic", dict(color=kmats.lin((24, 24, 25)), gloss=0.35, spec=0.25, dust=0.25)),
    "cable_grey": ("plastic", dict(color=kmats.lin((118, 120, 118)), gloss=0.30, spec=0.2, dust=0.3)),
    "chart": (mat_chart, {}),
})

OBJ, NAME = "m06_electro_proc", "ozr_electro_proc"
# screens - own textures with frames (kmodel panels): PNGs from make_decals.py
PANELS = {
    "crt": dict(off="decal_crt_off.png", frames=["decal_crt_f%02d.png" % i for i in range(12)], size=256, gloss=0.8),
    "crt2": dict(off="decal_crt2_off.png", frames=["decal_crt2_f%02d.png" % i for i in range(12)], size=256, gloss=0.8),
    "led": dict(off="decal_led_off.png", frames=["decal_led_f%02d.png" % i for i in range(8)], size=256, gloss=0.6),
    # recorder tape: the paper does not glow, only its frames change
    "chart": dict(off="decal_chart_off.png", frames=["decal_chart_f%02d.png" % i for i in range(CHT.CHART_FRAMES)],
                  size=256, gloss=0.15),
}
# needle wobble at "work" (OZL_WorkFx wobble): source -> (middle, swing, period, s); pen - m06_chart.PEN
WOBBLE = {"ozl_needle": (0.62, 0.08, 1.9), "ozl_needle_2": (0.55, 0.025, 3.1)}
PEN_PIV = (FX0, Y0 + 0.016, Z_PEN + 0.019)                   # pen at rest is on the field zero


def needle_axis(piv):
    return (piv[0], Y_NEEDLE, piv[1])


# preview of the "work" look: the needles at mid-swing, the pen where its trace is on tape frame 0
# (pose_move below)
ON = dict(remap={"lamp_g_off": "lamp_g_on", "lamp_r_off": "lamp_r_on"}, emissive=(1.0, 1.0, 1.0, 1.0),
          move={SEL_PEN: (CHT.pen_x(CHT.frame_time(0)), 0.0, 0.0),
                SEL_NEEDLE: ("rot", needle_axis(PIV_V3), (0.0, 1.0, 0.0), NEEDLE_SWEEP * WOBBLE["ozl_needle"][0]),
                SEL_NEEDLE2: ("rot", needle_axis(PIV_G3), (0.0, 1.0, 0.0), NEEDLE_SWEEP * WOBBLE["ozl_needle_2"][0])})
# pen: the axis is a metre along +x from the field zero, offset in metres; three translations of one
# bone on three sources add up (m06_chart.PEN): the main travel - phase = fraction of the field, the
# other two - ripple by D metres
ANIMS = (
    ("ozl_needle", dict(type="rotation", source="ozl_needle", selection=SEL_NEEDLE, axis="ozl_needle_axis", memory=1,
                        minValue=0.0, maxValue=1.0, angle0=0.0, angle1=NEEDLE_SWEEP)),
    ("ozl_needle_2", dict(type="rotation", source="ozl_needle_2", selection=SEL_NEEDLE2, axis="ozl_needle_2_axis",
                          memory=1, minValue=0.0, maxValue=1.0, angle0=0.0, angle1=NEEDLE_SWEEP)),
) + tuple((src, dict(type="translation", source=src, selection=SEL_PEN, axis="ozl_pen_axis", memory=1,
                     minValue=0.0, maxValue=1.0, offset0=0.0, offset1=dd)) for src, _, _, _, dd in CHT.PEN)
SOURCES = {"ozl_needle": dict(animPeriod=0.2), "ozl_needle_2": dict(animPeriod=0.2)}
SOURCES.update({src: dict(animPeriod=CHT.PEN_ANIM_PERIOD[src]) for src, *_ in CHT.PEN})
# vanilla items: tools, a record sheet with a pen and a battery on the shelf; tape on the counter, an
# electrician kit on the generator (there are 5-9 cm of cell above them up to the shelf)
DECOR = [
    kv.put("pliers", (-0.215, -0.603, ZM), **kv.flat(-6)),
    kv.put("screwdriver", (0.035, -0.613, ZM), **kv.flat(8)),
    kv.put("paper", (0.206, -0.497, ZM), **kv.flat(93)),
    kv.put("pen", (0.262, -0.560, ZM), **kv.flat(118)),
    kv.put("battery9v", (0.135, -0.392, ZM), up=(0, 0, 1), fwd=(0.3, -1, 0)),
    kv.put("ducttape", (0.250, -0.235, CH[3]), **kv.flat(0)),
    kv.put("electrickit", (-0.180, -0.190, G3[3]), **kv.flat(88)),
]
class Model(kmodel.Model):
    def panel_mats(self, on):
        """Preview of "work": the recorder tape does not glow (OZL_Work has only frames for it, the material is
        unchanged)."""
        out = super().panel_mats(on)
        if on:
            _, frames = self.panel_pngs("chart")
            out["chart"] = krender.panel_material(frames[0], glow=0.0, gloss=PANELS["chart"]["gloss"])
        return out


# ozl_screen_4 goes last in hiddenSelections: the indices of the earlier selections in the mod config do not shift
M = Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
          glass=dict(base=(0.58, 0.62, 0.60), clear=0.06, edge=0.14, smudge=0.06, streaks=0.03),
          selections=(SEL_SCREEN, SEL_SCREEN2, SEL_SCREEN3, SEL_LAMP, SEL_LAMP2, SEL_NEEDLE, SEL_NEEDLE2, SEL_PEN,
                      SEL_CHART),
          hidden=(SEL_SCREEN, SEL_SCREEN2, SEL_SCREEN3, SEL_LAMP, SEL_LAMP2, SEL_CHART), states={"on": ON},
          bones=((SEL_NEEDLE, ""), (SEL_NEEDLE2, ""), (SEL_PEN, "")), animations=ANIMS, decor=DECOR,
          panels=PANELS, sources=SOURCES)
P = M.part
BOUNDS = {}


# =============================================================================
# Look pose in the preview: group rotation about an axis (needles) - on top of the kmodel shift (move)
# =============================================================================
def _split_move(move):
    tr, rot = {}, {}
    for k, v in (move or {}).items():
        if isinstance(v, tuple) and v and v[0] == "rot":
            rot[k] = v[1:]
        else:
            tr[k] = v
    return tr, rot


def _pose(parts, obs, rot):
    for p, ob in zip(parts, obs):
        if p.group in rot:
            piv, axis, ang = rot[p.group]
            pv = Vector(piv)
            ob.matrix_world = Matrix.Translation(pv) @ Matrix.Rotation(ang, 4, Vector(axis)) @ \
                Matrix.Translation(-pv) @ ob.matrix_world


_PLACE_LOOK, _PLACE = krender.place_look, krender.place


def pose_place_look(parts, kind_table, origin, remap=None, glow=1.5, sharp_deg=40.0, panels=None, move=None):
    tr, rot = _split_move(move)
    obs = _PLACE_LOOK(parts, kind_table, origin, remap=remap, glow=glow, sharp_deg=sharp_deg, panels=panels,
                      move=tr or None)
    _pose(parts, obs, rot)
    return obs


def pose_place(parts, tag, offset, mats, sharp_deg=40.0, move=None):
    tr, rot = _split_move(move)
    obs = _PLACE(parts, tag, offset, mats, sharp_deg=sharp_deg, move=tr or None)
    _pose(parts, obs, rot)
    return obs


krender.place_look, krender.place = pose_place_look, pose_place


# =============================================================================
# Face details of an instrument
# =============================================================================
def knobs(prefix, lst, lod):
    """Knobs from a list (x, z, r, kind, limb, angle): body, marks, the small knob of the dual one."""
    parts = []
    for i, (x, z, r, kind, _, ang) in enumerate(lst):
        if lod == 2:
            continue
        kb = P("%s_knob%d" % (prefix, i), "knob", uv_name="knob_%s%d" % (kind, round(r * 1000)), uv_origin=(x, YF, z))
        pt = P("%s_knob%d_ptr" % (prefix, i), "ptr", uv_name="knob_ptr_%d" % i, uv_origin=(x, YF, z))
        cp = P("%s_knob%d_cap" % (prefix, i), "knob_red", uv_name="knob_cap", uv_origin=(x, YF, z)) \
            if kind == "dual" else None
        b.knob(kb, pt, x, YF, z, r, kind, lod, angle=ang, cap=cp)
        parts += [p for p in (kb, pt, cp) if p is not None and p.bm.faces]
    return parts


def sockets(prefix, lst, lod, yf=YF):
    """BNC sockets; occupied ones have a plug with a boot (build_cables builds the cable to it). Near LOD only."""
    parts = []
    if lod > 0:
        return parts
    for i, (x, z, plugged) in enumerate(lst):
        nut = P("%s_bnc%d_nut" % (prefix, i), "steel", uv_name="bnc_nut", uv_origin=(x, yf, z))
        bd = P("%s_bnc%d" % (prefix, i), "chrome", uv_name="bnc_body", uv_origin=(x, yf, z))
        b.bnc_socket(nut, bd, x, yf, z, lod, studs=not plugged)
        parts += [p for p in (nut, bd) if p.bm.faces]
        if plugged and lod < 2:
            sl = P("%s_plug%d" % (prefix, i), "chrome", uv_name="plug_sleeve", uv_origin=(x, yf, z))
            bt = P("%s_plug%d_boot" % (prefix, i), "rubber", uv_name="plug_boot", uv_origin=(x, yf, z))
            b.bnc_plug(sl, bt, x, yf, z, lod)
            parts += [sl, bt]
    return parts


def toggles(prefix, lst, lod, yf=YF):
    parts = []
    if lod == 2:
        return parts
    for i, (x, z) in enumerate(lst):
        nut = P("%s_tg%d" % (prefix, i), "steel", uv_name="toggle_nut", uv_origin=(x, yf, z))
        lv = P("%s_tg%d_lever" % (prefix, i), "chrome", uv_name="toggle_lever", uv_origin=(x, yf, z))
        b.toggle(nut, lv, x, yf, z, lod)
        parts += [p for p in (nut, lv) if p.bm.faces]
    return parts


def lamp(name, x, z, reg, sel, lod, yf=YF):
    """Signal lamp: the lens is in the lamp selection on all LODs, the bezel on the near one."""
    lens = P(name, reg, uv_name="lamp_" + reg, uv_origin=(x, yf, z), group=sel)
    rim = P(name + "_rim", "chrome", uv_name="lamp_rim", uv_origin=(x, yf, z)) if lod == 0 else None
    b.lamp(rim, lens, x, yf, z, lod)
    return [p for p in (rim, lens) if p is not None]


def keys(name, x0, z, n, pitch, lod, dark=()):
    if lod > 0:
        return []
    parts = []
    for i in range(n):
        x = x0 + pitch * i
        reg = "knob" if i in dark else "key"
        k = P("%s%d" % (name, i), reg, uv_name="key_" + reg, uv_origin=(x, YF, z))
        b.plate(k, x, z, 0.016, 0.014, 0.0028, YF + 0.001, YF - 0.009, n=1)
        parts.append(k)
    return parts


def screen(name, r, sec, sel, lod, hood=0.012, margin=0.008, radius=0.010, glass=True):
    """Screen: a face with its own texture (section sec, selection sel; on the far LOD a black atlas face
    without selection), a tube with rounded corners, glass."""
    x0, x1, z0, z1 = r
    cx, cz, w, h = (x0 + x1) / 2, (z0 + z1) / 2, x1 - x0, z1 - z0
    parts = []
    if lod == 2:
        fc = P(name, "black")
        g.box(fc, x0, x1, Y_FACE, YF - 0.0005, z0, z1)
        return [fc]
    fc = P(name, "black", group=sel, section=sec)
    g.quad(fc, [(x0, Y_FACE, z0), (x1, Y_FACE, z0), (x1, Y_FACE, z1), (x0, Y_FACE, z1)])
    parts.append(fc)
    hd = P(name + "_hood", "bezel")
    b.bezel(hd, cx, cz, (w + 2 * margin, h + 2 * margin, radius), (w + 0.002, h + 0.002, radius * 0.55), YF,
            YF - hood, y_in=Y_FACE, n=2 if lod == 0 else 1)
    parts.append(hd)
    if glass:
        gl = P(name + "_glass", "inst", section="glass")
        y = YF - 0.0045
        g.quad(gl, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)])
        parts.append(gl)
    return parts


def meter(name, r, piv, sel, lod):
    """Pointer instrument: a face with a scale, a ring with rounded corners, glass, the needle (bone sel)
    with an axle cap; the zero corrector screw is under the ring."""
    x0, x1, z0, z1 = r
    cx, cz, w, h = (x0 + x1) / 2, (z0 + z1) / 2, x1 - x0, z1 - z0
    fc = P(name, "dial")
    g.box(fc, x0, x1, Y_FACE, YF - 0.0005, z0, z1)
    parts = [fc]
    if lod == 2:
        return parts
    bz = P(name + "_bezel", "bezel")
    b.bezel(bz, cx, cz, (w + 0.010, h + 0.010, 0.005), (w, h, 0.002), YF, YF - 0.005, y_in=Y_FACE,
            n=2 if lod == 0 else 1)
    parts.append(bz)
    gl = P(name + "_glass", "inst", section="glass")
    y = YF - 0.0045
    g.quad(gl, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)])
    parts.append(gl)
    px, pz, rr = piv
    nd = P(name + "_needle", "needle", group=sel)
    th = math.radians(NEEDLE_REST)
    u = Vector((math.sin(th), 0.0, math.cos(th)))
    fr = g.Frame((px, Y_NEEDLE, pz), u, b.FRONT.cross(u), b.FRONT)
    poly = [(-0.16 * rr, -0.0012), (0.0, -0.0009), (1.0 * rr, -0.00025), (1.0 * rr, 0.00025), (0.0, 0.0009),
            (-0.16 * rr, 0.0012)]
    g.prism(nd, poly, (0, 1), 0.0, 0.0005, frame=fr)
    parts.append(nd)
    if lod == 0:
        cp = P(name + "_pivot", "needle")
        b.lathe(cp, (px, Y_FACE, pz), b.FRONT, [(0.0030, 0.0), (0.0030, 0.0008), (0.0018, 0.0016)], 10)
        parts.append(cp)
    return parts


def instrument(name, box, lod, handles=False):
    """Instrument case on feet, a cast frame with rounded corners, a cream panel; on the near LOD panel
    screws (or knobs on the face for instruments of the unified case). On the far LOD - the panel only."""
    x0, x1, z0, z1, depth = box
    za = z0 + FOOT
    cx, cz = (x0 + x1) / 2, (za + z1) / 2
    parts = []
    pn = P(name + "_panel", "cream")
    g.box(pn, x0 + 0.004, x1 - 0.004, YF, YF + 0.006, za + 0.004, z1 - 0.004)
    parts.append(pn)
    if lod == 2:
        return parts
    cs = P(name + "_case", "inst")
    g.box(cs, x0, x1, YF + 0.006, YF + depth, za, z1, **(dict(r=0.004, seg=1) if lod == 0 else {}))
    parts.append(cs)
    fr = P(name + "_frame", "inst_frame")
    b.bezel(fr, cx, cz, (x1 - x0, z1 - za, 0.006), (x1 - x0 - 0.009, z1 - za - 0.009, 0.0025), YF + 0.0065,
            YF - 0.003, y_in=YF, n=2 if lod == 0 else 1)
    parts.append(fr)
    if lod == 0:
        ft = P(name + "_feet", "rubber")
        for x in (x0 + 0.03, x1 - 0.03):
            b.lathe(ft, (x, YF + 0.03, z0), (0, 0, 1), [(0.009, 0.0), (0.009, FOOT - 0.0015), (0.0075, FOOT)], 8)
        parts.append(ft)
        if not handles:
            sc = P(name + "_screws", "steel")
            for x in (x0 + 0.0095, x1 - 0.0095):
                for z in (za + 0.0095, z1 - 0.0095):
                    b.lathe(sc, (x, YF, z), b.FRONT, [(0.0026, 0.0), (0.0024, 0.0006), (0.0, 0.0009)], 8)
            parts.append(sc)
    if handles:
        hp = P(name + "_handles", "chrome")
        for xh in (x0 + 0.0075, x1 - 0.0075):
            b.u_handle(hp, (xh, YF - 0.003, za + 0.016), (xh, YF - 0.003, z1 - 0.012), (0, -1, 0), 0.022, 0.0040,
                       lod=lod, smooth=False)
        parts.append(hp)
    return parts


# =============================================================================
# Rack (B5 base, its own copy with details - m06_rack.py)
# =============================================================================
def build_rack(spec):
    parts = rk.instrument_rack(M, spec, X0, X1, Y0, Y1, H, CELLS, slide=dict(z=ZS, pull=PULL, depth=SDEPTH),
                               regions=dict(front="rk_front"), tag=TAG, ground=GROUND)
    lod = spec["lod"]
    # panels at the sides of the recorder (its face is narrower than the opening)
    fl = P("rec_fill", "rk_panel")
    for xa, xb in ((XI0 - 0.012, KS[0] - 0.002), (KS[1] + 0.002, XI1 + 0.012)):
        g.box(fl, xa, xb, Y0 - 0.003, Y0, Z_R + 0.003, Z_V - 0.003, **(dict(r=0.0015, seg=1) if lod == 0 else {}))
    g.box(fl, KS[0] - 0.002, KS[1] + 0.002, Y0 - 0.003, Y0, KS[3] + 0.002, Z_V - 0.003)
    parts.append(fl)
    if lod == 0:
        fs = P("rec_fill_screws", "steel")
        for xs in (XI0 - 0.0, XI1 + 0.0):
            for zs in (Z_R + 0.03, Z_V - 0.03):
                b.screw(fs, xs, Y0 - 0.003, zs, 0.0034)
        parts.append(fs)
    zp = (Z_P + Z_R) / 2
    parts += lamp("patch_lamp_g", 0.17, zp, "lamp_g", SEL_LAMP, lod, yf=Y0 - 0.003)
    parts += lamp("patch_lamp_r", 0.21, zp, "lamp_r", SEL_LAMP2, lod, yf=Y0 - 0.003)
    if lod == 2:
        return parts
    # patch panel: a row of sockets (two occupied by jumpers), a rocker mains switch
    parts += sockets("patch", [(-0.26 + 0.05 * i, zp, i in (0, 3, 4, 6)) for i in range(8)], lod, yf=Y0 - 0.003)
    sw = P("patch_switch", "black")
    g.box(sw, 0.248, 0.292, Y0 - 0.008, Y0 - 0.003, zp - 0.019, zp + 0.019, **(dict(r=0.002, seg=1) if lod == 0 else {}))
    if lod == 0:
        # rocker pressed at the top: two slopes
        fr = g.Frame((0.270, Y0 - 0.008, zp), (1, 0, 0), (0, 0, 1), (0, -1, 0))
        g.prism(sw, [(-0.012, -0.014), (-0.012, 0.014), (0.0, 0.016), (0.0, -0.016)], (1, 2), -0.0, 0.0,
                frame=fr) if False else None
        g.box(sw, 0.256, 0.284, Y0 - 0.014, Y0 - 0.008, zp - 0.001, zp + 0.013, r=0.0015, seg=1)
        g.box(sw, 0.256, 0.284, Y0 - 0.011, Y0 - 0.008, zp - 0.013, zp - 0.001, r=0.0012, seg=1)
    parts.append(sw)
    return parts


# =============================================================================
# Instruments
# =============================================================================
def build_c1_65(spec):
    """S1-65A: the screen on the left in a tube, knobs in a 4 x 3 grid on the right, inputs, a power lamp and
    buttons below."""
    lod = spec["lod"]
    parts = instrument("c1", C1, lod)
    parts += screen("c1_screen", CRT, "crt", SEL_SCREEN, lod)
    parts += lamp("c1_lamp", *LAMPS[0][1:], lod)
    if lod == 2:
        return parts
    parts += knobs("c1", K_C1, lod) + sockets("c1", BNC_C1, lod)
    parts += toggles("c1_power", [(C1[1] - 0.025, C1[2] + 0.025)], lod)
    parts += keys("c1_key", C1[0] + 0.190, C1[2] + 0.025, 4, 0.024, lod, dark=(0,))
    return parts


def build_c1_94(spec):
    lod = spec["lod"]
    parts = instrument("c94", C94, lod)
    parts += screen("c94_screen", CRT94, "crt2", SEL_SCREEN2, lod, hood=0.009, margin=0.006, radius=0.007)
    if lod == 2:
        return parts
    parts += knobs("c94", K_94, lod) + sockets("c94", BNC_94, lod)
    return parts


def build_v3(spec):
    """V3-38: a large meter on top, a range switch, an input, a mains toggle, a zero corrector."""
    lod = spec["lod"]
    parts = instrument("v3", V3, lod) + meter("v3_meter", M_V3, PIV_V3, SEL_NEEDLE, lod)
    if lod == 2:
        return parts
    parts += knobs("v3", K_V3, lod) + sockets("v3", BNC_V3, lod)
    parts += toggles("v3_power", [(V3[1] - 0.022, V3[2] + 0.075)], lod)
    if lod == 0:
        zs = P("v3_zero", "knob")
        b.lathe(zs, (PIV_V3[0], YF, M_V3[2] - 0.011), b.FRONT, [(0.0042, 0.0), (0.0042, 0.0025), (0.0034, 0.0032)], 12)
        sl = P("v3_zero_slot", "ptr")
        g.box(sl, PIV_V3[0] - 0.0030, PIV_V3[0] + 0.0030, YF - 0.0036, YF - 0.0030, M_V3[2] - 0.0115, M_V3[2] - 0.0105)
        parts += [zs, sl]
    return parts


def build_g3(spec):
    """G3-118: an output voltmeter (the needle is a bone), frequency decade windows and their knobs, a
    multiplier, an amplitude knob, two outputs, a lamp and a mains toggle, knobs on the face."""
    lod = spec["lod"]
    parts = instrument("g3", G3, lod, handles=True) + meter("g3_meter", M_G3, PIV_G3, SEL_NEEDLE2, lod)
    wf = P("g3_windows", "windows")
    g.box(wf, WIN_G3[0], WIN_G3[1], Y_FACE, YF - 0.0005, WIN_G3[2], WIN_G3[3])
    parts.append(wf)
    parts += lamp("g3_lamp", *LAMPS[1][1:], lod)
    if lod == 2:
        return parts
    wb = P("g3_windows_bezel", "bezel")
    x0, x1, z0, z1 = WIN_G3
    b.bezel(wb, (x0 + x1) / 2, (z0 + z1) / 2, (x1 - x0 + 0.008, z1 - z0 + 0.008, 0.003), (x1 - x0, z1 - z0, 0.0015),
            YF, YF - 0.003, y_in=Y_FACE, n=2 if lod == 0 else 1)
    parts.append(wb)
    parts += knobs("g3", K_G3, lod) + sockets("g3", BNC_G3, lod)
    parts += toggles("g3_power", [(G3[0] + 0.030, G3[2] + 0.030)], lod)
    return parts


def build_ch(spec):
    """Ch3-63: input A with a jumper from the generator, a count lamp (blinks), a display (own texture) in
    a frame, mode buttons, a count time knob, a mains toggle, knobs on the face."""
    lod = spec["lod"]
    parts = instrument("ch", CH, lod, handles=True)
    parts += screen("ch_led", LED, "led", SEL_SCREEN3, lod, hood=0.004, margin=0.005, radius=0.003, glass=False)
    parts += lamp("ch_gate", *LAMPS[2][1:], lod)
    if lod == 2:
        return parts
    parts += keys("ch_key", CH[0] + 0.070, CH[2] + 0.023, 7, 0.024, lod, dark=(0, 4))
    parts += knobs("ch", K_CH, lod) + sockets("ch", BNC_CH, lod)
    parts += toggles("ch_power", [(CH[0] + 0.267, CH[2] + 0.022)], lod)
    return parts


def build_recorder(spec):
    """KSP4 (as in M04): body, a door with a window and moulding on hinges, a latch; behind the glass the
    tape on a drum, a scale, a pen carriage on two rails (bone ozl_pen); under the window toggles, a
    power lamp and a knob; the tape comes out of the slot in a short loop."""
    lod = spec["lod"]
    x0, x1, z0, z1, depth = KS
    wx, wz, ww, wh = (WX0 + WX1) / 2, (WZ0 + WZ1) / 2, WX1 - WX0, WZ1 - WZ0
    parts = []
    if lod == 2:
        bz = P("rec_bezel", "rec_case")
        g.box(bz, x0, x1, Y0 - 0.006, Y0 + 0.004, z0, z1)
        ch = P("rec_chart", "chart")
        g.box(ch, TX0, TX1, Y0 - 0.008, Y0 - 0.006, WZ0, CH_Z1)
        return [bz, ch]
    bev = dict(r=0.004, seg=2) if lod == 0 else {}
    # the body is behind the window niche (its face does not cover the tape)
    yb_ = Y0 + 0.042
    cs = P("rec_case", "rec_case")
    g.box(cs, x0 + 0.006, x1 - 0.006, yb_, YF + depth, z0 + 0.004, z1 - 0.004, **bev)
    parts.append(cs)
    # door: a frame with a window the full depth of the niche (the window is above the middle), moulding around the
    # window
    dr = P("rec_door", "rec_case")
    b.bezel(dr, (x0 + x1) / 2, (z0 + z1) / 2, (x1 - x0, z1 - z0, 0.010), (ww, wh, 0.006), yb_, YDR,
            y_in=yb_, n=2 if lod == 0 else 1, ic=(wx, wz))
    b.bezel(dr, wx, wz, (ww + 0.014, wh + 0.014, 0.010), (ww, wh, 0.006), YDR, YDR - 0.003, y_in=YDR,
            n=2 if lod == 0 else 1)
    parts.append(dr)
    # niche back is dark
    dk = P("rec_inside", "rk_inner")
    g.box(dk, WX0, WX1, yb_ - 0.004, yb_, WZ0, WZ1)
    parts.append(dk)
    # tape in the window - own texture (section chart, "work" frames), UV 0..1 over the visible tape (as in M04)
    ch = P("rec_chart", "black", group=SEL_CHART, section="chart")
    g.quad(ch, [(TX0, Y_CHART, WZ0), (TX1, Y_CHART, WZ0), (TX1, Y_CHART, CH_Z1), (TX0, Y_CHART, CH_Z1)])
    ch.glass_frame = (g.WORLD, TX0, TX1, WZ0, CH_Z1)
    parts.append(ch)
    sc = P("rec_scale", "dial")
    g.box(sc, SCALE[0], SCALE[1], Y0 + 0.022, Y0 + 0.026, SCALE[2], SCALE[3])
    parts.append(sc)
    # pen carriage: a block on the rails, a scale pointer, the pen down to the paper (bone ozl_pen)
    pn = P("rec_pen", "pen", group=SEL_PEN)
    px, py, pz = PEN_PIV
    g.box(pn, px - 0.012, px + 0.012, Y0 + 0.008, Y0 + 0.021, Z_PEN + 0.006, Z_PEN + 0.032,
          **(dict(r=0.0015, seg=1) if lod == 0 else {}))
    g.box(pn, px - 0.0009, px + 0.0009, Y0 + 0.018, Y0 + 0.0215, Z_PEN + 0.032, SCALE[2] + 0.014)
    b.lathe(pn, (px, Y0 + 0.016, Z_PEN), (0, 1, 0), [(0.0034, 0.0), (0.0030, 0.008), (0.0012, Y_CHART - Y0 - 0.017),
                                                     (0.0005, Y_CHART - Y0 - 0.0165)], 8 if lod == 0 else 5)
    g.box(pn, px - 0.0015, px + 0.0015, Y0 + 0.012, Y0 + 0.018, Z_PEN, Z_PEN + 0.006)
    parts.append(pn)
    rd = P("rec_rods", "chrome")
    for zr, rr in ((Z_PEN + 0.012, 0.0030), (Z_PEN + 0.026, 0.0030)):
        g.pipe(rd, [(WX0, Y0 + 0.016, zr), (WX1, Y0 + 0.016, zr)], rr, 8 if lod == 0 else 4)
    parts.append(rd)
    dm = P("rec_drum", "drum")
    b.lathe(dm, (TX0 - 0.012, Y_CHART - 0.008, WZ0 + 0.010), (1, 0, 0), [(0.0085, 0.0), (0.0085, TX1 - TX0 + 0.024)],
            14 if lod == 0 else 6, cap0=True)
    parts.append(dm)
    gl = P("rec_glass", "rec_case", section="glass")
    yg = Y0 - 0.006
    g.quad(gl, [(WX0, yg, WZ0), (WX1, yg, WZ0), (WX1, yg, WZ1), (WX0, yg, WZ1)])
    parts.append(gl)
    sl = P("rec_slot", "black")
    g.box(sl, TX0 - 0.008, TX1 + 0.008, YDR - 0.0005, YDR + 0.001, z0 + 0.094, z0 + 0.104)
    parts.append(sl)
    # tape from the slot: a short loop forward and down (the controls under it stay visible)
    pts = [(TAPE_X, YDR + 0.002, z0 + 0.099), (TAPE_X, YDR - 0.020, z0 + 0.097), (TAPE_X, YDR - 0.036, z0 + 0.088),
           (TAPE_X, YDR - 0.044, z0 + 0.074), (TAPE_X, YDR - 0.040, z0 + 0.061), (TAPE_X, YDR - 0.028, z0 + 0.056)]
    tp = P("tape", "chart")
    g.sweep(tp, b.spline(pts, 3) if lod == 0 else pts[::2] + [pts[-1]], (1, 0, 0), 0.0004, (TX1 - TX0) / 2)
    parts.append(tp)
    parts += lamp("rec_lamp", x0 + 0.105, z0 + 0.030, "lamp_g", SEL_LAMP, lod, yf=YDR)
    parts += toggles("rec", [(x0 + 0.035, z0 + 0.030), (x0 + 0.070, z0 + 0.030)], lod, yf=YDR)
    kb = P("rec_knob", "knob")
    pt = P("rec_knob_ptr", "ptr")
    b.knob(kb, pt, x1 - 0.045, YDR, z0 + 0.040, 0.016, "skirt", lod, angle=20)
    parts += [p for p in (kb, pt) if p.bm.faces]
    if lod == 0:
        hg = P("rec_hinges", "chrome")
        for zh in (WZ0 + 0.03, WZ1 - 0.07):
            b.hinge(hg, x0 - 0.0035, YDR + 0.004, zh, zh + 0.04, 0.0042)
        lt = P("rec_latch", "chrome")
        b.lathe(lt, (x1 - 0.020, YDR, wz), b.FRONT, [(0.0080, 0.0), (0.0080, 0.0035), (0.0058, 0.0085),
                                                    (0.0068, 0.0150), (0.0050, 0.0175), (0.0, 0.0185)], 14)
        parts += [hg, lt]
    return parts


# =============================================================================
# Pull-out shelf: block, probe board, probes; cables between instruments
# =============================================================================
def build_fixture(spec):
    """Textolite block: a knife-edge connector, board guides with extractors, a ground terminal, a BNC
    input socket, a harness into the rack; the probe board with parts."""
    lod = spec["lod"]
    parts = []
    fx = P("fixture", "fixture")
    g.box(fx, FX[0], FX[1], FY0, FY1, ZM, FZ1, **(dict(r=0.003, seg=2) if lod == 0 else {}))
    parts.append(fx)
    sk = P("fixture_socket", "black")
    g.box(sk, BX0 - 0.002, BX1 + 0.002, BY - 0.0075, BY + 0.0075, FZ1, FZ1 + 0.012,
          **(dict(r=0.0015, seg=1) if lod == 0 else {}))
    parts.append(sk)
    pc = P("probe_pcb", "pcb")
    g.box(pc, BX0, BX1, YB, BY + 0.0008, FZ1 + 0.004, BZ1)
    parts.append(pc)
    if lod == 2:
        return parts
    # board guides (channel) and red extractors on them
    cg = P("fixture_guides", "steel")
    ej = P("fixture_ejectors", "cap_red")
    for s, xe in ((-1, BX0), (1, BX1)):
        xa, xb = sorted((xe + s * 0.002, xe + s * 0.013))
        xw = sorted((xe + s * 0.011, xe + s * 0.013))
        for ya, yb in ((BY - 0.0065, BY - 0.0045), (BY + 0.0045, BY + 0.0065)):
            g.box(cg, xa, xb, ya, yb, FZ1, FZ1 + 0.085)
        g.box(cg, xw[0], xw[1], BY - 0.0065, BY + 0.0065, FZ1, FZ1 + 0.085)
        g.box(ej, xa - 0.001, xb + 0.001, BY - 0.0075, BY + 0.0075, FZ1 + 0.085, FZ1 + 0.097,
              **(dict(r=0.0015, seg=1) if lod == 0 else {}))
        if lod == 0:
            g.box(ej, *sorted((xe - s * 0.004, xe + s * 0.002)), BY - 0.0040, BY + 0.0040, FZ1 + 0.090, FZ1 + 0.096)
    parts += [cg, ej]
    # block harness at the back - a flat cable into the rack
    rb = P("fixture_cable", "cable_grey")
    pts = [(FX[0] + 0.05, FY1, ZM + 0.020), (FX[0] + 0.05, FY1 + 0.04, ZM + 0.012), (FX[0] + 0.06, Y0 + 0.02, ZM + 0.006),
           (FX[0] + 0.07, Y0 + 0.12, ZM + 0.006)]
    g.sweep(rb, b.spline(pts, 3) if lod == 0 else pts, (0, 0, 1), 0.025, 0.0015)
    parts.append(rb)
    # BNC socket on the block face (generator signal input)
    parts += sockets("fixture", [(FBNC[0], FBNC[1], False)], lod, yf=FY0)
    if lod > 0:
        return parts
    sc = P("fixture_screws", "steel")
    for x in (FX[0] + 0.012, FX[1] - 0.012):
        for y in (FY0 + 0.010, FY1 - 0.010):
            if (x, y) != (GND[0], GND[1]):
                b.screw(sc, x, y, FZ1, 0.0030, axis=(0, 0, 1))
    parts.append(sc)
    # ground terminal: a brass stud with a knurled nut
    gn = P("fixture_ground", "brass")
    b.lathe(gn, (GND[0], GND[1], FZ1), (0, 0, 1), [(0.0050, 0.0), (0.0028, 0.0030), (0.0062, 0.0060),
                                                    (0.0062, 0.0110), (0.0026, 0.0120), (0.0026, 0.0180),
                                                    (0.0018, 0.0190)], 10, knurl=(2, 3), depth=0.0006)
    parts.append(gn)
    parts += build_pcb_parts()
    return parts


def build_pcb_parts():
    """Parts on the board face (near LOD only): four DIP ICs, a metal-can transistor, two electrolytics,
    MLT resistors, a trimmer, a test loop for the probe (left of the board middle)."""
    parts = []
    ic = P("pcb_chips", "chip")
    lg = P("pcb_legs", "lead")
    for x, z, n in ((-0.112, 0.952, 16), (-0.068, 0.952, 14), (-0.030, 0.952, 8), (-0.100, 0.918, 14)):
        b.dip(ic, lg, x, YB, z, n)
    rs = P("pcb_resistors", "resistor")
    for x, z, al in ((-0.150, 0.890, "x"), (-0.120, 0.890, "x"), (-0.072, 0.918, "z"), (-0.064, 0.918, "z"),
                     (-0.056, 0.918, "z")):
        b.resistor(rs, lg, x, YB, z, along=al)
    ce = P("pcb_caps", "cap_el")
    ct = P("pcb_cap_tops", "cap_top")
    b.can_cap(ce, ct, 0.018, YB, 0.948, r=0.0040, L=0.011)
    b.can_cap(ce, ct, 0.020, YB, 0.900, r=0.0032, L=0.009)
    tr = P("pcb_transistor", "can")
    b.transistor(tr, -0.012, YB, 0.920)
    tm = P("pcb_trimmer", "trim")
    g.box(tm, -0.0385, -0.0315, YB - 0.0045, YB, 0.9145, 0.9215, r=0.0005, seg=1)
    b.lathe(tm, (-0.035, YB - 0.0045, 0.918), b.FRONT, [(0.0024, 0.0), (0.0024, 0.0008)], 8)
    tp = P("pcb_testpoint", "lead")
    x, y, z = TP
    g.pipe(tp, b.spline([(x - 0.003, YB, z - 0.002), (x - 0.003, y + 0.002, z), (x, y - 0.0005, z + 0.002),
                         (x + 0.003, y + 0.002, z), (x + 0.003, YB, z - 0.002)], 2), 0.0005, 5)
    parts += [ic, lg, rs, ce, ct, tr, tm, tp]
    return parts


def probe_scope(lod):
    """Oscilloscope divider probe: a hook on the test loop, a cap, a stop, a knurled body, a tail - it lies
    on the mat (the probe hangs diagonally). Returns (parts, tail end, direction)."""
    tip = Vector(TP) + Vector((0.0, -0.0015, -0.0020))
    dz = -(tip.z - (ZM + 0.0026)) / 0.125
    dx = 0.08
    d = Vector((dx, -math.sqrt(1.0 - dz * dz - dx * dx), dz))
    parts = []
    bd = P("probe_scope", "probe_g")
    prof = [(0.0, 0.0), (0.0022, 0.0035), (0.0034, 0.0060), (0.0034, 0.0200), (0.0072, 0.0215), (0.0072, 0.0250),
            (0.0056, 0.0280), (0.0058, 0.0820), (0.0036, 0.0960), (0.0030, 0.1100), (0.0026, 0.1250)]
    if lod > 0:
        prof = [prof[i] for i in (0, 3, 4, 7, 8, 10)]
    b.lathe(bd, tip, d, prof, 10 if lod == 0 else 6)
    parts.append(bd)
    if lod == 0:
        hk = P("probe_scope_hook", "lead")
        g.pipe(hk, b.spline([tuple(tip), tuple(tip - d * 0.003), (TP[0], TP[1] - 0.001, TP[2] + 0.0015),
                             (TP[0], TP[1] + 0.0025, TP[2] + 0.0010), (TP[0], TP[1] + 0.003, TP[2] - 0.002)], 2), 0.0005, 5)
        parts.append(hk)
    return parts, tip + d * 0.125, d


def probe_volt(lod):
    """Millivoltmeter probe: a needle, a stop, a red body, a tail; lies on the record sheet."""
    d = Vector((0.55, 0.65, 0.0)).normalized()
    tip = Vector((0.140, -0.560, ZM + 0.0066))
    parts = []
    nd = P("probe_volt_tip", "lead")
    b.lathe(nd, tip, d, [(0.0, 0.0), (0.0008, 0.002), (0.0010, 0.016)], 6)
    parts.append(nd)
    bd = P("probe_volt", "probe_r")
    prof = [(0.0010, 0.016), (0.0030, 0.018), (0.0030, 0.021), (0.0066, 0.022), (0.0066, 0.026), (0.0050, 0.029),
            (0.0050, 0.098), (0.0034, 0.108), (0.0026, 0.125)]
    if lod > 0:
        prof = [prof[i] for i in (0, 3, 4, 6, 8)]
    b.lathe(bd, tip, d, prof, 10 if lod == 0 else 6)
    parts.append(bd)
    return parts, tip + d * 0.125, d


def cable(name, pts, r, lod, region="cable"):
    c = P(name, region)
    if lod == 0:
        g.pipe(c, b.spline(pts, 2), r, 6)
    else:
        g.pipe(c, [pts[i] for i in range(0, len(pts), 2)] + ([pts[-1]] if (len(pts) - 1) % 2 else []), r, 4)
    return [c]


def plug_end(x, z, yf=YF):
    """End of a BNC plug cap in the socket (x, z) on the face yf - where the cable starts."""
    return (x, yf - 0.045, z)


def hang(a, c, drop, out=0.012, n=6):
    """Sagging wire between the ends of caps a and c: leaves the cap forward, sags by drop and bulges
    forward by out in the middle (a smooth arc, not a tick mark)."""
    a, c = Vector(a), Vector(c)
    pts = [tuple(a), tuple(a + Vector((0.0, -0.008, -0.003)))]
    for i in range(1, n):
        t = i / n
        k = math.sin(math.pi * t)
        pts.append(tuple(a.lerp(c, t) + Vector((0.0, -0.008 - out * k, -0.003 - drop * k ** 1.2))))
    pts += [tuple(c + Vector((0.0, -0.008, -0.003))), tuple(c)]
    return pts


def build_cables(spec):
    """Probes and cables: S1-65A - a probe on the board (the cable over the mat between the block and the
    pliers and up to the left of the G3-118); V3-38 - a probe on the record sheet; G3-118 - the block
    input and input A of the counter; patch-panel jumpers; the probe "ground" is a clip on the block terminal."""
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    sp, e1, d1 = probe_scope(lod)
    parts += sp
    x, z = BNC_C1[0][:2]
    s = Vector(plug_end(x, z))
    zm = ZM + 0.0028
    pts = [tuple(e1), (e1.x - 0.008, e1.y + 0.004, zm), (-0.195, -0.533, zm), (-0.255, -0.520, zm),
           (-0.302, -0.497, 0.842), (-0.326, -0.468, 0.900), (-0.336, -0.440, 0.975), (-0.326, -0.420, 1.035),
           (x - 0.008, s.y - 0.020, z - 0.036), tuple(s)]
    parts += cable("probe_scope_cable", pts, 0.0028, lod)
    vp, e2, d2 = probe_volt(lod)
    parts += vp
    x, z = BNC_V3[0][:2]
    s = Vector(plug_end(x, z))
    pts = [tuple(e2), tuple(e2 + d2 * 0.014), (0.256, -0.444, zm), (0.284, -0.426, 0.846), (0.300, -0.405, 0.940),
           (0.301, -0.398, 1.040), (x + 0.001, s.y - 0.016, z - 0.024), tuple(s)]
    parts += cable("probe_volt_cable", pts, 0.0028, lod, region="probe_r")
    # G3-118 -> block input: a plug in the block socket, the cable over the mat and up to the generator output
    fsl = P("fixture_plug", "chrome")
    fbt = P("fixture_plug_boot", "rubber")
    fe = b.plug_along(fsl, fbt, (FBNC[0], FY0 - 0.0135, FBNC[1]), (0.25, -1.0, 0.0), lod)
    parts += [fsl, fbt]
    x, z = BNC_G3[0][:2]
    s = Vector(plug_end(x, z))
    pts = [tuple(fe), (fe.x + 0.008, fe.y - 0.012, ZM + 0.006), (fe.x + 0.030, fe.y - 0.004, ZM + 0.0030),
           (0.084, -0.505, ZM + 0.0030), (0.080, -0.445, 0.842), (0.050, -0.410, 0.870), (0.000, -0.402, 0.882),
           (x + 0.004, s.y - 0.018, z - 0.016), tuple(s)]
    parts += cable("gen_cable", pts, 0.0030, lod)
    # G3-118 -> Ch3-63 input A: a jumper sags between the generator and counter knobs
    x, z = BNC_G3[1][:2]
    x2, z2 = BNC_CH[0][:2]
    parts += cable("ch_patch", hang(plug_end(x, z), plug_end(x2, z2), 0.050, out=0.010, n=6), 0.0028, lod)
    if lod == 0:
        # jumpers on the patch panel
        zp = (Z_P + Z_R) / 2
        for k, (xa, xb) in enumerate(((-0.26, -0.11), (-0.06, 0.04))):
            pts = hang(plug_end(xa, zp, Y0 - 0.003), plug_end(xb, zp, Y0 - 0.003), 0.040 + 0.15 * (xb - xa) * 0.3,
                       out=0.010, n=6)
            parts += cable("patch_cord%d" % k, pts, 0.0028, lod)
        # probe "ground": a wire from the stop in a loop to the clip on the block terminal
        jw = P("ground_clip_jaws", "lead")
        bt = P("ground_clip_boot", "cable")
        tip = Vector((GND[0], GND[1] - 0.001, FZ1 + 0.014))
        tail = b.alligator(jw, bt, tip, (0.30, -0.75, 0.45), (0.0, 0.3, 1.0), lod, size=0.85)
        parts += [jw, bt]
        gs = Vector(TP) + Vector((0.0, -0.0015, -0.002)) + d1 * 0.028
        pts = [tuple(gs), tuple(gs + Vector((-0.006, -0.010, -0.006))), (gs.x - 0.010, -0.528, 0.884),
               (tail.x + 0.012, tail.y - 0.020, tail.z - 0.010), tuple(tail + Vector((0.004, -0.006, -0.001))), tuple(tail)]
        c = P("ground_lead", "cable")
        g.pipe(c, b.spline(pts, 2), 0.0012, 5)
        parts.append(c)
    return parts


def build_lod(spec):
    parts = build_rack(spec)
    parts += build_c1_65(spec) + build_c1_94(spec) + build_v3(spec) + build_g3(spec) + build_ch(spec)
    parts += build_recorder(spec) + build_fixture(spec) + build_cables(spec)
    parts = [p for p in parts if p is not None and len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    rack = kx.box_pts(X0, X1, Y0 - 0.05, Y1, 0.0, H)
    # a component thinner than 0.5 m does not work: the shelf goes inside the rack and down
    shelf = kx.box_pts(XI0 - 0.012, XI1 + 0.012, TY0 - 0.06, Y0 + 0.20, 0.40, ZS + 0.13)
    metal = kx.PEN + r"\metalplate.rvmat"
    comps = [(rack, metal), (shelf, metal)]
    memory = {
        "invView": [(0.0, -2.8, 1.2)],
        "ce_center": [(0.0, 0.0, H / 2)],
        "ce_radius": [(0.8, 0.0, H / 2)],
        # needle axes - from the axis toward the person (as M08: phase > 0 is clockwise), the pen - along the scale,
        # 1 m
        "ozl_needle_axis": [needle_axis(PIV_V3), (PIV_V3[0], Y_NEEDLE - 0.05, PIV_V3[1])],
        "ozl_needle_2_axis": [needle_axis(PIV_G3), (PIV_G3[0], Y_NEEDLE - 0.05, PIV_G3[1])],
        "ozl_pen_axis": [PEN_PIV, (PEN_PIV[0] + 1.0, PEN_PIV[1], PEN_PIV[2])],
    }
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (X0, X1, min(lo[1], TY0 - 0.06), max(hi[1], Y1), 0.0, H)
    return comps, 260.0, memory, bbox


# the first ones are for the --look preview: overview, instruments, recorder, shelf, board, doors; the
# "work" look - overview, instruments, recorder
SHOTS = [
    ("front", (-1.1, -3.0, 1.55), (0.0, 0.0, 1.0), 30),
    ("instruments", (-0.35, -1.25, 1.25), (0.0, Y0, 1.08), 34),
    ("recorder", (0.25, -1.10, 1.70), (0.0, Y0, 1.55), 36),
    ("shelf", (0.45, -1.15, 1.20), (-0.02, TY0 + 0.15, 0.88), 36),
    ("pcb", (0.22, -0.92, 1.12), (-0.07, -0.47, 0.90), 46),
    ("doors", (-0.85, -1.55, 0.95), (0.0, Y0, 0.45), 32),
    ("back", (1.5, 2.3, 1.5), (0.0, 0.0, 0.9), 30),
]

M.look_shots = (6, 3)
M.run(build_lod, collision, SHOTS, row_step=1.2, row_shot=((1.2, -6.5, 1.6), (1.2, 0, 1.0)))
