"""M24 - ballistic stand with a chronograph: Ballistic Sample Analyzer of Duty (OZL_Dty_Proc_Ball).
An analyzer: 4x4 cargo, no modules (no module_1..3 points, as in M06, M21).

    blender --background --python build_m24.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (gauge scales, the CRT screen and
display frames, toggle marks, limbs, the printer tape, the rail ruler, hatching).

Composition: 2.0 x 1.3 x 0.7 m. On the left a measurement console (a detailed copy of
kconsole.console - m24_console.py) reduced to 0.80 x 1.30 x 0.70; on the right a 1.20 m rail bed on
two trestles with a barrel clamp, a suppressor on the barrel, along the rail two U-shaped optical
frames of the chronograph; cables from the frames, the pressure sensor and the trigger solenoid go
to the connectors on the right cheek of the console.

References:
- a universal ballistic test rig shown at SHOT Show 2015: a heavy steel plate on a bed, two
  round guides, a receiver block with a lever, red end blocks on screws, a red clamp around the
  barrel, a V-block with a bolted cover, a red pressure sensor cable. The clamp dimensions (plate
  0.30 x 0.16, guides dia. 22) are estimated from a photo with a person next to it;
- Oehler Skyscreen III optical frames: below a trapezoidal sensor body with a window, uprights going
  up, on top an orange diffuser bar (red here: the Duty accent). Here a U-frame: vertical uprights,
  an opening of 0.31 x 0.32 m; the body 0.08 x 0.34 x 0.04 is estimated from a photo;
- the Oehler Model 35P chronograph unit (a 1988 design): a speed display, buttons, a built-in tape
  printer in a stepped case - hence the display and printer on the console. The Oehler 35P base is
  a 4-foot rail, 1219 mm between the screens; it is repeated by Freedom's chronograph M28 (a 1.4 m
  rail on tripods). Here the base is 0.40 m, shorter: a longer one does not fit with the clamp on a
  1.2 m bed, and short bases (~0.3 m) occur in compact chronographs. This way the stands do not
  repeat each other: M28 has a light rail on tripods, M24 a heavy bed on trestles;
- the console is an army instrument console of the 1970-90s (a sloped desk with toggles, a top panel
  with a round CRT screen and needle gauges, a roof shelf), close to the vanilla radar_panel
  (DZ/structures/furniture/radar_equipment; its texture is the look sample: screwed panels,
  instrument holders). The width is reduced to 0.80; the desk height 0.76 is as for consoles for
  seated work (GOST 22269-76: work surface 0.72-0.80);
- the suppressor is a vanilla PB (dz\\weapons\\attachments\\muzzle\\suppressor_pb6p9, a proxy:
  150 x dia. 33 mm by the model's extent - almost exactly the PBS-1, 152 mm); the barrel is dia. 25 at the
  muzzle end - an estimate; the barrel axis is at 0.905 m.

Detail: the "dayz" look (matte, dirtier, colored AO). The console is the detailed one (m24_console.py:
screwed panels, hinges, latch handles, a lock, louvers, a CRT in a holder with a rubber tube, gauges
in flanges); on the desk toggles with a nut and a ball, knurled knobs with a skirt, an emergency
mushroom button on a yellow ring, a trigger switch under a red hinged cover, a printer with a step
and three keys (like the Oehler 35P). The bed has support heels on screws, gussets, rail end caps, a
ruler with divisions, a lower shelf; on the shelf in front of the rags lies a brass cleaning rod
with a loop (build_rod), the rags are pushed to the back wall of the shelf; a cartridge tray at the
breech. The clamp has socket-head screws, retaining rings, a clamp on a screw, a pressure sensor on
the barrel, the trigger solenoid. The frames have a trapezoidal body with a window, round uprights
in sockets, BNC connectors. The cables are smooth curves along clips and along the trestle legs on
ties. The small stuff is vanilla items as proxies (kvanilla, DECOR).

Duty: black and gray with a red accent, no olive; worn by frequent use - paint worn down to metal on
the edges, at the console toggles and knobs, at the door handles, on the top of the rail where the
clamp and frames travel; scratches, oil spots; no rust. The paint builder build_worn is from the
M23 generator (where the reason is explained: in kmats.build_paint chips always rust).

No readable lettering: gauge scales with digits, the display, blank nameplates under the toggles
(numbers only), a printer tape with digits, a ruler with digits, yellow-black hazard hatching on the
rail by the muzzle, a lead seal on the doors.

Working look: the CRT face is ozl_screen (own texture, section crt: "off" and 20 frames - shot,
measurement, trace fade, triggered sweep; make_decals.CRT_SEQ); the speed and shot number display is
ozl_screen_2 (section led: dashes while the beam runs, then the speed - a series of five shots,
make_decals.LED_SEQ); the scale backlight, green lamps, the yellow "armed" lamp and the printer light
are ozl_lamp; the red "shot" lamp and the flashing beacon on the roof are ozl_lamp_blink (_on atlas,
they blink). The needles are bones ozl_needle_1..3 on sources ozl_needle_1..3 (wobble, phase 0 is
the scale zero, 1 is the whole scale). The "armed" pose (source ozl_pose, pose): the hinged cover of
the trigger switch opens (bone ozl_guard, the first half of the travel), the toggle under it goes up
(ozl_master, the second half), the clamp lever goes down, "closed" (ozl_lever).

Blender axes: X is width, Y is depth (the face looks to -Y), Z is up.
"""
import math
import os
import sys

from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kconsole as kc  # noqa: E402
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import krender  # noqa: E402
import kvanilla as kv  # noqa: E402
import m24_bits as b  # noqa: E402
import m24_console as mc  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
CX0, CX1, CY0, CY1, CH = -1.01, -0.21, -0.35, 0.35, 1.30      # console
CONSOLE = dict(desk_z=0.76, desk_deg=25.0, desk_len=0.30, upper_deg=12.0, gauges=3, gauge_r=0.040, sweep=240.0,
               screen_r=0.065, doors=2)
L = kc.layout(CY0, CY1, CH, CONSOLE["desk_z"], CONSOLE["desk_deg"], CONSOLE["desk_len"], CONSOLE["upper_deg"])
D, U = L["desk"], L["upper"]                                    # desk and top panel systems
XI0, XI1 = CX0 + kc.CHEEK, CX1 - kc.CHEEK
PT = kc.PLATE_T
SCR, GAUGES, _ = mc.gauge_places(L, XI0, XI1, CONSOLE["gauges"], CONSOLE["screen_r"])
# bed: rail, trestles (legs - 35 mm square tube, splayed), lower shelf
RX0, RX1 = -0.19, 1.01                                          # rail 1.20 m
ZR = 0.80                                                       # top of the rail
TRESTLES = (-0.10, 0.92)                                        # trestle axes
LEG_TOP, LEG_FOOT, LEG_H = 0.045, 0.235, 0.0175                 # leg axis: y at the rail and at the floor; half-thickness
LEG_Z0 = 0.046                                                  # bottom of the leg: a support plate, a leveling screw under it
SHELF = (-0.105, 0.925, -0.142, 0.142, 0.25, 0.022)             # x0 x1 y0 y1 bottom, side height
# barrel clamp (after the SHOT Show rig): plate, end blocks, guides, block, V-block; barrel axis
ZB = 0.905
CL0, CL1 = -0.15, 0.15
BLOCK = (-0.10, -0.02)
VBLK = (0.04, 0.10)
BARREL = (-0.06, 0.20, 0.0125)                                  # x0, x1, radius at the muzzle end
SUPP = (0.165, 0.315, 0.0165)                                   # suppressor PB (vanilla): 150 mm, dia. 33
SENSOR_X = 0.019                                                # pressure sensor on the barrel at the chamber
LEVER_PIV = (-0.06, -0.083, 0.94)                               # lever axis on the side of the block
LEVER_REST, LEVER_LOCK = 15.0, 65.0                             # lever: from the vertical backward at rest; travel when "working"
TRAY = (0.0, 0.22, -0.155, -0.0535, 0.735, 0.022)               # cartridge tray at the breech: x0 x1 y0 y1 bottom side
# chronograph frames: x axes, sensor body, uprights, bar
FRAMES = (0.57, 0.97)                                           # base 0.40
FZ0, FZ1, FTOP = 0.81, 0.85, 1.17                               # body bottom and top, bar bottom
FHW = 0.17                                                      # half-width of the body and the bar along y
POST_Y = FHW - 0.015
# connectors on the right cheek of the console: y, z - the pressure sensor, the trigger solenoid, frame 1, frame 2
CONN = [(-0.025, 0.22), (0.045, 0.22), (0.115, 0.22), (0.185, 0.22)]
# console desk (in desk axes: a is world x, b is up the desk)
TOG_B, TOG_A = 0.215, [-0.94 + 0.065 * i for i in range(6)]
MASTER = (-0.535, 0.215)
KNOB_B, KNOBS = 0.10, [(-0.92, 0.016, "ring11"), (-0.80, 0.016, "ring11"), (-0.68, 0.014, "ring6")]
ESTOP, BUTTON = (-0.585, 0.10), (-0.545, 0.10)
PRN = (-0.40, -0.27, 0.05, 0.22, 0.062)                         # printer: a0 a1 b0 b1 step height
PRN_BASE = 0.030                                                # base height (keys)
SLOT_B = PRN[3] - 0.038                                         # slot on the step (along the desk slope)
PAPER_A, PAPER_W = -0.335, 0.057                                # 57 mm tape
# top panel (in its axes): the speed and shot number display, lamps, a nameplate
SPEED = (-0.735, -0.565, 0.118, 0.160)                          # make_decals.LED_WIN
N_SHOTS = (-0.540, -0.445, 0.118, 0.160)
DISP_FLANGE = (-0.755, -0.425, 0.105, 0.173)                    # common display holder on four screws
DISP_T = 0.0025                                                 # holder thickness
# where the display windows are on its image (make_decals.LED_RECTS, 512 x 512): u0 u1 v0 v1 (v is up) -
# speed on top, shot number below, an 8 px gap between them
LED_UV = {"speed": (0.0, 1.0, 260.0 / 512, 1.0), "shots": (0.0, 286.0 / 512, 0.0, 252.0 / 512)}
PLATE = (-0.405, -0.275, 0.095, 0.155)
FUSES = [(-0.385, 0.048), (-0.345, 0.048)]                      # fuse holders under the nameplate
BEACON = (-0.33, 0.20)                                          # roof beacon: x, y
# cleaning rod on the lower shelf in front of the rags: a brass rod dia. 6, a loop ring at one end (outer dia. 34,
# for a finger) with a crimp sleeve, a slotted eye for a rag patch at the other; total length 0.71 m,
# like one-piece rifle cleaning rods. It lies on the shelf bottom: the axis is ROD_R above the sheet
ROD_Y = -0.090                                                  # rod axis on the shelf
ROD_X0, ROD_X1 = -0.031, 0.625                                  # from the loop to the eye
ROD_R, LOOP_R = 0.003, 0.014                                    # rod, loop center line


def leg_y(z):
    """Trestle leg axis (|y|) at height z."""
    return LEG_TOP + (LEG_FOOT - LEG_TOP) * (0.72 - z) / (0.72 - 0.008)


LEG_T = Vector((0.0, LEG_FOOT - LEG_TOP, -(0.72 - 0.008))).normalized()   # along the rear leg, downward


def paper_pts():
    """Center line of the tape: from the printer slot upward and curling back."""
    p0 = D.p(PAPER_A, SLOT_B, PT + PRN[4])
    n, v = D.n, D.v
    return [tuple(q) for q in (p0 - n * 0.004, p0 + n * 0.020, p0 + n * 0.038 + v * 0.010, p0 + n * 0.043 + v * 0.031,
                               p0 + n * 0.030 + v * 0.050)]


PAPER_Z = (min(q[2] for q in paper_pts()), max(q[2] for q in paper_pts()))

LOD_SPECS = [
    dict(lod=0, bev=1, sides=12),
    dict(lod=1, bev=0, sides=8),
    dict(lod=2, bev=0, sides=6),
]

REGIONS = {
    "cs": ("cs_paint", 0.5), "cs_desk": ("desk_paint", 1.2), "cs_upper": ("upper_paint", 1.1),
    "cs_front": ("front_paint", 0.6), "cs_accent": ("accent", 0.8), "steel": ("steel", 1.0), "black": ("black", 1.0),
    "rubber": ("rubber", 0.5), "grille_v": ("grille_v", 0.8), "dial": ("dial", 4.0), "needle": ("needle", 2.0),
    "lamp_g": ("lamp_g_off", 1.6), "lamp_y": ("lamp_y_off", 1.6), "lamp_r": ("lamp_r_off", 1.6),
    "led_g": ("led_g_off", 2.0), "beacon": ("beacon", 1.2), "cap_red": ("cap_red", 1.6), "estop_y": ("estop_y", 1.6),
    "plate": ("plate", 2.0), "printer": ("printer", 1.4), "paper": ("paper", 3.0), "seal": ("seal", 2.0),
    "rail": ("rail", 1.0), "bench": ("bench", 0.6), "shelf": ("shelf", 0.6), "red": ("red", 1.4),
    "chrome": ("chrome", 1.4), "barrel": ("barrel", 2.0), "housing": ("housing", 1.4),
    "lens": ("lens", 2.0), "diffuser": ("diffuser", 1.4), "diffuser_in": ("plastic_white", 1.0),
    "cable": ("cable", 0.8), "cable_red": ("cable_red", 0.8), "screw": ("screw", 2.0), "bolt": ("bolt", 2.0),
    "knob": ("knob", 2.0), "ptr": ("plastic_white", 2.0), "ruler": ("ruler", 2.5), "zip": ("zip", 1.2),
    "rod": ("brass_rod", 2.0),
}


# =============================================================================
# Materials
# =============================================================================
def build_worn(mat, origin, color, bare=kmats.lin((112, 112, 116)), seed=1.0, gloss=0.32, spec=0.25,
               wear=(0.66, 0.71), edge_k=0.7, rub=(), stripes=(), scratch=0.0, oil=0.0, floor_z=0.0,
               dust=0.15, grime=0.3, decal_items=()):
    """Paint worn by frequent use, without rust - from the M23 generator: rubbed down to metal on the
    edges (edge_k) and where hands take it (rub - [(center, semi-axes, strength)]: an ellipsoid, weaker
    toward the edge); scratches along x, oil spots on top (oil); stripes of another color - stripes
    [((x0, x1, y0, y1, z0, z1), color)]. Bare metal shines and does not rust."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.9 for c in color[:3]) + (1,), color)
    for (x0, x1, y0, y1, z0, z1), scol in stripes:
        inside = 1.0
        for i, (a, bb) in enumerate(((x0, x1), (y0, y1), (z0, z1))):
            w = sep.outputs[i]
            m = t.math("MULTIPLY", t.math("GREATER_THAN", w, a), t.math("LESS_THAN", w, bb))
            inside = m if isinstance(inside, float) else t.math("MULTIPLY", inside, m)
        base = t.mixc(inside, base, scol)
    col = kmats.decals(t, base, sep, nsep, decal_items)
    edge = t.maprange(t.edge_wear(0.004), 0.05, 0.22, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 11.0, 10.0, 0.7), 0.75), t.math("MULTIPLY", edge, edge_k))
    grain = t.maprange(t.noise(vec, 34.0, 8.0, 0.7), 0.3, 0.7, 0.55, 1.0)
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
        near = t.maprange(ln.outputs["Value"], 0.25, 1.0, 1.0, 0.0)
        f = t.math("ADD", f, t.math("MULTIPLY", t.math("MULTIPLY", near, grain), k))
    worn = t.step(f, wear[0], wear[1])
    brush = t.noise(t.stretch(vec, 0.04, 1.0, 1.0), 90.0, 4.0, 0.7)
    metal = t.mixc(t.maprange(brush, 0.3, 0.7, 0.0, 1.0), tuple(c * 0.75 for c in bare[:3]) + (1,),
                   tuple(min(1.0, c * 1.15) for c in bare[:3]) + (1,))
    rim = t.math("SUBTRACT", t.step(f, wear[0] - 0.05, wear[0]), worn)
    col = t.mixc(t.math("MULTIPLY", rim, 0.6), col, kmats.lin((52, 50, 46)))
    col = t.mixc(worn, col, metal)
    h = t.math("MULTIPLY", worn, -0.3)
    g_ = t.math("ADD", gloss, t.math("MULTIPLY", worn, 0.62 - gloss))
    s_ = t.math("ADD", spec, t.math("MULTIPLY", worn, 0.70 - spec))
    if scratch > 0:
        sc = t.step(t.noise(t.stretch(vec, 0.02, 1.0, 1.0), 260.0, 2.0, 0.5), 0.70, 0.73)
        sc = t.math("MULTIPLY", sc, t.maprange(t.noise(vec, 5.0, 4.0, 0.5), 0.35, 0.65, 0.0, scratch))
        col = t.mixc(t.math("MULTIPLY", sc, 0.7), col, metal)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", sc, 0.15))
    if oil > 0:
        up = t.maprange(nsep.outputs["Z"], 0.5, 0.9, 0.0, 1.0)
        ol = t.math("MULTIPLY", t.step(t.noise(vec, 4.0, 6.0, 0.6), 0.62, 0.70), t.math("MULTIPLY", up, oil))
        col = t.mixc(t.math("MULTIPLY", ol, 0.55), col, kmats.lin((14, 12, 10)))
        g_ = t.math("ADD", g_, t.math("MULTIPLY", ol, 0.25))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g_, s_, h)


def wdecal(name):
    return os.path.join(WORK, name)


def rubs_desk():
    """Where the desk is worn: at the toggles, the knobs, the buttons, the front edge."""
    r = [(tuple(D.p((TOG_A[0] + TOG_A[-1]) / 2, TOG_B, 0)), (0.22, 0.05, 0.05), 0.40),
         (tuple(D.p(MASTER[0], MASTER[1], 0)), (0.04, 0.04, 0.04), 0.55),
         (tuple(D.p(-0.80, L["desk_len"] * 0.02, 0)), (0.32, 0.05, 0.04), 0.35)]
    r += [(tuple(D.p(a, KNOB_B, 0)), (0.04, 0.04, 0.04), 0.55) for a, _, _ in KNOBS]
    r += [(tuple(D.p(a, bb, 0)), (0.025, 0.025, 0.025), 0.45) for a, bb in (ESTOP, BUTTON)]
    return r


def desk_decals():
    items = [kc.panel_decal(wdecal("decal_toggles.png"), D, TOG_A[0] - 0.0325, TOG_A[-1] + 0.0325,
                            TOG_B - 0.058, TOG_B + 0.032, PT)]
    for a, r, rg in KNOBS:
        s = r * 2.2
        items.append(kc.panel_decal(wdecal("decal_%s.png" % rg), D, a - s, a + s, KNOB_B - s, KNOB_B + s, PT))
    return items


def dial_decals(state):
    gr = CONSOLE["gauge_r"] * 1.02
    return [kc.panel_decal(wdecal("decal_gauge%d_%s.png" % (i + 1, state)), U, a - gr, a + gr, bb - gr, bb + gr, kc.GF)
            for i, (a, bb) in enumerate(GAUGES)]


BLACK = kmats.lin((30, 30, 32))
GREY = kmats.lin((70, 74, 78))
RED = kmats.lin((140, 24, 20))
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
FRAME = dict(color=BLACK, seed=2.1, wear=(0.67, 0.72), edge_k=0.7, scratch=0.3, floor_z=0.0, dust=0.15, grime=0.3)
HANDLE_RUB = [(((XI0 + XI1) / 2 + s * 0.04, L["yt"] - 0.004, (kc.PLINTH + L["zd0"] - 0.085) / 2 + 0.08),
               (0.06, 0.04, 0.06), 0.45) for s in (-1, 1)]
# rail: the top is worn where the clamp and frames travel; in front at the muzzle - hatching
RAIL_RUB = [((0.0, 0.0, ZR), (0.22, 0.07, 0.03), 0.45)] + [((x, 0.0, ZR), (0.10, 0.07, 0.03), 0.40) for x in FRAMES]
HAZARD = (wdecal("decal_hazard.png"), "y", -1, ("x", "z"), (0.42, 0.752), (0.14, 0.05), (-0.054, -0.046))
RULER = (0.20, 1.00, 0.7862, 0.7988)                            # ruler on the face of the rail's front lip: x0 x1 z0 z1
RULER_DECAL = (wdecal("decal_ruler.png"), "y", -1, ("x", "z"), ((RULER[0] + RULER[1]) / 2, (RULER[2] + RULER[3]) / 2),
               (RULER[1] - RULER[0], RULER[3] - RULER[2]), (-0.0625, -0.0595))

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "cs_paint": (build_worn, FRAME),
    "front_paint": (build_worn, dict(FRAME, seed=2.9, edge_k=0.8, rub=HANDLE_RUB)),
    "desk_paint": (build_worn, dict(FRAME, color=GREY, seed=3.3, wear=(0.66, 0.71), edge_k=0.9, rub=rubs_desk(),
                                    scratch=0.5, oil=0.25, floor_z=L["zd0"], dust=0.08, grime=0.15,
                                    decal_items=desk_decals())),
    "upper_paint": (build_worn, dict(FRAME, color=GREY, seed=3.9, wear=(0.71, 0.76), edge_k=0.6, scratch=0.15,
                                     floor_z=L["zd1"], dust=0.12, grime=0.1)),
    "accent": (build_worn, dict(FRAME, color=RED, seed=4.6, wear=(0.70, 0.75), edge_k=0.8, scratch=0.2,
                                floor_z=L["zu1"], dust=0.25, grime=0.1)),
    "dial": ("paint", dict(CLEAN, color=kmats.lin((22, 22, 22)), gloss=0.5, spec=0.35, decal_items=dial_decals("off"))),
    "dial_on": ("paint", dict(CLEAN, color=kmats.lin((34, 14, 12)), gloss=0.5, spec=0.35, decal_items=dial_decals("on"))),
    "needle": ("flat", dict(color=kmats.lin((228, 226, 216)), gloss=0.5, spec=0.3)),
    "lamp_g_off": ("flat", dict(color=kmats.lin((34, 64, 40)), gloss=0.85, spec=0.8)),
    "lamp_y_off": ("flat", dict(color=kmats.lin((86, 70, 26)), gloss=0.85, spec=0.8)),
    "lamp_r_off": ("flat", dict(color=kmats.lin((72, 24, 22)), gloss=0.85, spec=0.8)),
    "led_g_off": ("flat", dict(color=kmats.lin((30, 52, 34)), gloss=0.85, spec=0.8)),
    "lamp_g_on": ("flat", dict(color=kmats.lin((130, 255, 140)), gloss=0.85, spec=0.8)),
    "lamp_y_on": ("flat", dict(color=kmats.lin((255, 214, 90)), gloss=0.85, spec=0.8)),
    "lamp_r_on": ("flat", dict(color=kmats.lin((255, 86, 60)), gloss=0.85, spec=0.8)),
    "led_g_on": ("flat", dict(color=kmats.lin((120, 255, 130)), gloss=0.85, spec=0.8)),
    "beacon": ("plastic", dict(color=kmats.lin((120, 22, 18)), gloss=0.8, spec=0.7, dust=0.3)),
    "beacon_on": ("flat", dict(color=kmats.lin((255, 70, 46)), gloss=0.8, spec=0.7)),
    "estop_y": ("plastic", dict(color=kmats.lin((200, 156, 30)), gloss=0.4, spec=0.3, dust=0.15, scuff=(0.64, 0.72))),
    "plate": ("steel", dict(seed=5.9, tone=0.42, along="x", gloss=0.5, spec=0.6, floor_z=L["zd1"], dust=0.1, grime=0.2)),
    "printer": ("plastic", dict(color=kmats.lin((58, 60, 62)), gloss=0.3, spec=0.2, dust=0.2, scuff=(0.62, 0.7))),
    "paper": ("paint", dict(CLEAN, color=kmats.lin((232, 230, 220)), gloss=0.1, spec=0.05,
                            decal_items=[(wdecal("decal_paper.png"), "y", -1, ("x", "z"),
                                          (PAPER_A, (PAPER_Z[0] + PAPER_Z[1]) / 2), (PAPER_W, PAPER_Z[1] - PAPER_Z[0]),
                                          None)])),
    "seal": ("plastic", dict(color=kmats.lin((120, 120, 118)), gloss=0.35, spec=0.3, dust=0.1)),
    "rail": (build_worn, dict(FRAME, seed=6.2, wear=(0.64, 0.69), edge_k=1.0, rub=RAIL_RUB, scratch=0.9, oil=0.5,
                              floor_z=0.0, dust=0.05, grime=0.2, decal_items=[HAZARD])),
    "bench": (build_worn, dict(FRAME, seed=6.7, wear=(0.68, 0.73), edge_k=0.8, scratch=0.2, dust=0.2, grime=0.45)),
    # lower shelf: crates stand on it and rags lie on it - dust, oil, worn in the middle
    "shelf": (build_worn, dict(FRAME, seed=9.4, wear=(0.66, 0.71), edge_k=0.9, scratch=0.6, oil=0.35,
                               rub=[((0.41, 0.0, SHELF[4]), (0.45, 0.12, 0.03), 0.30)], floor_z=0.0, dust=0.3,
                               grime=0.4)),
    "red": (build_worn, dict(FRAME, color=RED, seed=7.1, wear=(0.65, 0.70), edge_k=1.0, scratch=0.5, oil=0.3,
                             floor_z=ZR, dust=0.05, grime=0.25)),
    "chrome": ("steel", dict(seed=7.5, tone=0.32, along="x", gloss=0.75, spec=0.85, floor_z=ZR, dust=0.05, grime=0.2)),
    "barrel": ("steel", dict(seed=7.9, tone=0.14, along="x", gloss=0.5, spec=0.55, floor_z=ZR, dust=0.0, grime=0.25)),
    "housing": (build_worn, dict(FRAME, color=kmats.lin((58, 60, 62)), seed=8.8, wear=(0.70, 0.75), edge_k=0.8,
                                 scratch=0.2, floor_z=ZR, dust=0.2, grime=0.15)),
    "lens": ("flat", dict(color=kmats.lin((20, 26, 32)), gloss=0.95, spec=0.9)),
    "diffuser": ("plastic", dict(color=kmats.lin((168, 30, 22)), gloss=0.55, spec=0.4, dust=0.3, scuff=(0.6, 0.68))),
    "cable": ("plastic", dict(color=kmats.lin((26, 26, 26)), gloss=0.30, spec=0.2, dust=0.4, scuff=(0.8, 0.9))),
    "cable_red": ("plastic", dict(color=kmats.lin((150, 28, 22)), gloss=0.4, spec=0.3, dust=0.3, scuff=(0.8, 0.9))),
    # fasteners: the console's galvanizing has darkened; the bed and clamp bolts are blued
    "screw": ("steel", dict(seed=9.1, tone=0.26, along="z", gloss=0.45, spec=0.5, floor_z=0.0, dust=0.1, grime=0.35)),
    "bolt": ("steel", dict(seed=9.7, tone=0.13, along="z", gloss=0.45, spec=0.5, floor_z=ZR, dust=0.05, grime=0.35)),
    # knobs: black carbolite, the edges rubbed to a shine
    "knob": ("plastic", dict(color=kmats.lin((24, 24, 25)), gloss=0.38, spec=0.28, dust=0.12, grime=0.2,
                             scuff=(0.58, 0.66))),
    "ruler": ("paint", dict(CLEAN, color=kmats.lin((150, 150, 146)), gloss=0.5, spec=0.45, dust=0.05,
                            decal_items=[RULER_DECAL])),
    "zip": ("plastic", dict(color=kmats.lin((18, 18, 19)), gloss=0.3, spec=0.2, dust=0.2)),
    # cleaning rod: the brass has darkened, rubbed to a shine where it is held and where it rubs the barrel
    "brass_rod": (build_worn, dict(color=kmats.lin((138, 108, 54)), bare=kmats.lin((210, 174, 96)), seed=10.3,
                                   gloss=0.45, spec=0.55, wear=(0.54, 0.61), edge_k=0.5, scratch=0.3,
                                   floor_z=SHELF[4], dust=0.15, grime=0.3)),
})

OBJ, NAME = "m24_dty_proc_ball", "ozr_dty_proc_ball"
SEL_SCREEN, SEL_SCREEN2, SEL_LAMP, SEL_BLINK = "ozl_screen", "ozl_screen_2", "ozl_lamp", "ozl_lamp_blink"
SEL_GUARD, SEL_MASTER, SEL_LEVER = "ozl_guard", "ozl_master", "ozl_lever"
# top panel lamps: (a, b, region, selection) - power, frames ready, "armed", "shot"
LAMPS = [(-0.715, 0.065, "lamp_g", SEL_LAMP), (-0.675, 0.065, "lamp_g", SEL_LAMP), (-0.635, 0.065, "lamp_y", SEL_LAMP),
         (-0.595, 0.065, "lamp_r", SEL_BLINK)]
# screens have their own frame textures (kmodel panels): PNGs from make_decals.py. Distinct frames: the
# screen has 20, the display 10; the playback order when "working" (a shot is 5.0 s: the screen has 50
# entries of 0.1 s, the display 5 of 1.0 s) is make_decals.CRT_SEQ, LED_SEQ. The display is 512 x 512
# (256 for a 0.29 x 0.04 m strip would blur the digits), its windows have their own
# unwrap (LED_UV)
CRT_FRAMES, LED_FRAMES = 20, 10                                 # make_decals.CRT_FRAMES, LED_FRAMES
PANELS = {
    "crt": dict(off="decal_crt_off.png", frames=["decal_crt_f%02d.png" % i for i in range(CRT_FRAMES)], size=256,
                gloss=0.85),
    "led": dict(off="decal_led_off.png", frames=["decal_led_f%02d.png" % i for i in range(LED_FRAMES)], size=512,
                gloss=0.7),
}
# needles (selection = source; phase 1 is the whole 240-degree scale) and their wobble when "working"
# (OZL_WorkFx wobble: middle, amplitude, period, s): bullet speed ~715 out of 1000 m/s, frame supply
# 13.5 out of 30 V (steady), chamber pressure - in jerks with each shot
NEEDLES = ["ozl_needle_1", "ozl_needle_2", "ozl_needle_3"]
WOBBLE = {"ozl_needle_1": (0.715, 0.012, 2.4), "ozl_needle_2": (0.45, 0.004, 3.7), "ozl_needle_3": (0.52, 0.06, 1.2)}
SWEEP = math.radians(CONSOLE["sweep"])
# "armed" pose (source ozl_pose, 1 s): the cover is the first half of the travel, the toggle the second,
# the lever the whole
GUARD_HINGE = D.p(MASTER[0], MASTER[1] + 0.028, PT + 0.034)
MASTER_PIV = D.p(MASTER[0], MASTER[1], PT + 0.002) + D.n * 0.0094
GUARD_OPEN, MASTER_UP = math.radians(-95.0), math.radians(-36.0)
LEVER_ANG = math.radians(-LEVER_LOCK)


def rot_anim(name, sel, src, axis, ang, lo=0.0, hi=1.0):
    return (name, dict(type="rotation", source=src, selection=sel, axis=axis, memory=1, minValue=lo, maxValue=hi,
                       angle0=0.0, angle1=ang))


# Bone axes are memory points: needles - mc.needle_axis (toward the person), the toggle cover, the
# toggle and the lever - AXES below. The engine rotates a bone right-handed in DayZ axes (kexport.conv,
# determinant -1); in Blender axes this is left-handed about the axis from the first point to the
# second: the axis looks at the person - a positive angle is clockwise for him (as in M08, M12, M14,
# M33 - their needles are right in the game). The axes must not go the other way: the needles would
# then turn counterclockwise in the game, past zero and past the scale, and the cover, toggle and
# lever would go not where the preview shows. A positive needle angle is clockwise, to the right along
# the scale (checked by check_turns).
ANIMS = tuple(rot_anim(n + "_rot", n, n, n + "_axis", SWEEP) for n in NEEDLES) + (
    rot_anim("ozl_guard_open", SEL_GUARD, "ozl_pose", "ozl_guard_axis", GUARD_OPEN, 0.0, 0.5),
    rot_anim("ozl_master_up", SEL_MASTER, "ozl_pose", "ozl_master_axis", MASTER_UP, 0.5, 1.0),
    rot_anim("ozl_lever_lock", SEL_LEVER, "ozl_pose", "ozl_lever_axis", LEVER_ANG, 0.0, 1.0),
)
SOURCES = dict({n: dict(animPeriod=0.2) for n in NEEDLES}, ozl_pose=dict(animPeriod=1.0))
# "working" preview: the needles are mid-wobble, the "armed" pose (the rotation is done by the wrapper
# below; it does not go into the p3d - the pose is set by the bones)
ON_MOVE = {n: ("rot", tuple(mc.needle_pivot(U, a, bb)), tuple(U.n), -SWEEP * WOBBLE[n][0])
           for n, (a, bb) in zip(NEEDLES, GAUGES)}
ON_MOVE.update({SEL_GUARD: ("rot", tuple(GUARD_HINGE), (1.0, 0.0, 0.0), GUARD_OPEN),
                SEL_MASTER: ("rot", tuple(MASTER_PIV), (1.0, 0.0, 0.0), MASTER_UP),
                SEL_LEVER: ("rot", LEVER_PIV, (0.0, 1.0, 0.0), LEVER_ANG)})
# memory points of the axes of the toggle cover, the toggle and the lever: in this order the engine
# rotates them as the preview does
AXES = {SEL_GUARD + "_axis": [tuple(GUARD_HINGE + D.u * 0.02), tuple(GUARD_HINGE - D.u * 0.02)],
        SEL_MASTER + "_axis": [tuple(MASTER_PIV + D.u * 0.01), tuple(MASTER_PIV - D.u * 0.01)],
        SEL_LEVER + "_axis": [(LEVER_PIV[0], LEVER_PIV[1] + 0.02, LEVER_PIV[2]), LEVER_PIV]}
AXES.update({n + "_axis": list(mc.needle_axis(U, a, bb)) for n, (a, bb) in zip(NEEDLES, GAUGES)})


def check_turns():
    """By number, like check_axes of the Storage crates: for each bone the preview pose (ON_MOVE) and the
    engine rotation by its animation and memory axis (in Blender axes - right-handed about the reversed
    axis, from the second point to the first) go the same way; the needles at phases mid +- amp are
    inside the scale (0..1), clockwise for the person (the axis toward him is +U.n). If they disagree -
    the build fails."""
    seen = []
    for name, d in ANIMS:
        sel = d["selection"]
        a, b = (Vector(q) for q in AXES[d["axis"]])
        eng = (a - b).normalized() * math.copysign(1.0, d["angle1"] - d["angle0"])
        _, _, ax, ang = ON_MOVE[sel]
        pre = Vector(ax).normalized() * math.copysign(1.0, ang)
        assert eng.dot(pre) > 0.99, "%s: preview and game rotate in opposite directions" % name
        if sel in WOBBLE:
            mid, amp, _ = WOBBLE[sel]
            assert 0.0 <= mid - amp and mid + amp <= 1.0, "%s: wobble goes past the scale" % sel
            assert eng.dot(U.n) < -0.99, "%s: the needle does not go clockwise" % sel
            seen.append("%s %.0f-%.0f°" % (sel[-1], math.degrees(SWEEP * (mid - amp)), math.degrees(SWEEP * (mid + amp))))
        else:
            seen.append(sel)
    print("turns ok: preview and engine rotate the same way - " + ", ".join(seen))


check_turns()
ON = dict(remap={"dial": "dial_on", "lamp_g_off": "lamp_g_on", "lamp_y_off": "lamp_y_on", "lamp_r_off": "lamp_r_on",
                 "led_g_off": "led_g_on", "beacon": "beacon_on"},
          emissive=(1.0, 1.0, 1.0, 1.0), move=ON_MOVE)

# vanilla items: the PB suppressor on the barrel; on the lower shelf rags, a gun cleaning kit with an
# adjustable wrench, an ammo crate; in the tray at the breech a 7.62 x 39 box and loose cartridges; on
# the console roof a shot log with a pen and safety glasses
PB = r"dz\weapons\attachments\muzzle\suppressor_pb6p9"
AMMOBOX = r"dz\gear\containers\300RoundBox"
BOX762 = r"dz\weapons\ammunition\762x39_20RoundBox"
GOGGLES = r"dz\characters\glasses\TacGoggles_g"
SHELF_Z = SHELF[4] + 0.002
TRAY_Z = TRAY[4] + 0.0015


def _thick(key):
    lo, hi = kv.box(key)
    return hi[2] - lo[2]


DECOR = [
    kv.put(PB, ((SUPP[0] + SUPP[1]) / 2, 0.0, ZB), up=(1, 0, 0), fwd=(0, 0, 1), lift=-_thick(PB) / 2),
    kv.put("rags", (0.08, 0.035, SHELF_Z), **kv.flat(0)),     # against the back wall: the cleaning rod lies in front
    kv.put("cleaningkit", (0.42, 0.005, SHELF_Z), **kv.flat(2)),
    kv.put("wrench", (0.44, -0.035, SHELF_Z + _thick("cleaningkit")), **kv.flat(-8)),
    kv.put(AMMOBOX, (0.75, 0.0, SHELF_Z)),
    kv.put(BOX762, (0.068, -0.104, TRAY_Z), **kv.flat(0)),
    kv.put("rounds762", (0.168, -0.104, TRAY_Z), up=(0, 0, 1), fwd=(0.3, -1, 0)),
    kv.put("paper", (-0.85, 0.165, CH), **kv.flat(88)),
    kv.put("pen", (-0.80, 0.10, CH + 0.0003), **kv.flat(62)),
    kv.put(GOGGLES, (-0.58, 0.17, CH), **kv.flat(95)),
]


class Model(kmodel.Model):
    def panel_mats(self, on):
        """Preview of "working": on the screen the measurement stage (trace, cursors, interval bracket), on
        the display the speed of the third shot of the series."""
        out = super().panel_mats(on)
        if on:
            _, frames = self.panel_pngs("crt")
            out["crt"] = krender.panel_material(frames[11], glow=1.6, gloss=PANELS["crt"]["gloss"])
            _, frames = self.panel_pngs("led")
            out["led"] = krender.panel_material(frames[7], glow=1.6, gloss=PANELS["led"]["gloss"])
        return out


M = Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
          glass=dict(base=(0.58, 0.60, 0.58), clear=0.08, edge=0.14, smudge=0.12, streaks=0.04),
          selections=(SEL_SCREEN, SEL_SCREEN2, SEL_LAMP, SEL_BLINK) + tuple(NEEDLES) + (SEL_GUARD, SEL_MASTER, SEL_LEVER),
          hidden=(SEL_SCREEN, SEL_SCREEN2, SEL_LAMP, SEL_BLINK), states={"on": ON},
          bones=tuple((n, "") for n in NEEDLES) + ((SEL_GUARD, ""), (SEL_MASTER, ""), (SEL_LEVER, "")),
          animations=ANIMS, decor=DECOR, panels=PANELS, sources=SOURCES)
P = M.part
BOUNDS = {}


# =============================================================================
# Preview pose: group rotation about an axis (needles, cover, toggle, lever) on top of the kmodel shift
# (move); as in M06, the library is not changed
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


def piece(name, region, uvn, origin, **kw):
    """Identical parts share a place in the atlas (uv_name) - in their own coordinates from origin."""
    return P(name, region, uv_name=uvn, uv_origin=tuple(origin), **kw)


def bev(lod, r=0.002, seg=1):
    return dict(r=r, seg=seg) if lod == 0 else {}


# =============================================================================
# Console (the detailed one) and its contents
# =============================================================================
def build_console(spec):
    parts, info = mc.console(M, spec, CX0, CX1, CY0, CY1, CH, needles=NEEDLES, dial_group=SEL_LAMP,
                             crt_group=SEL_SCREEN, crt_section="crt", **CONSOLE)
    BOUNDS["info"] = info
    parts += build_displays(spec) + build_lamps(spec) + build_desk(spec) + build_printer(spec)
    parts += build_beacon(spec) + build_connectors(spec) + build_front_bits(spec)
    return parts


def window_quad(part, win, c):
    """Display window (a0 a1 b0 b1 in top panel axes) - one face outward at height c."""
    xa, xb, ya, yb = win
    return g.quad(part, [tuple(U.p(xa, ya, c)), tuple(U.p(xb, ya, c)), tuple(U.p(xb, yb, c)), tuple(U.p(xa, yb, c))])


def build_displays(spec):
    """Speed and shot number display: a common holder with rounded corners on four screws, on it the
    window frames, and in the windows 5.6 mm deeper than the frame edge - the display face. The face is
    one part with its own 512 x 512 texture (the "working" frames - make_decals) and its own unwrap: the
    speed window is the top of the image, the number window the bottom (LED_UV); a 0.29 x 0.04 m strip
    would otherwise land on 256 x 256 and give ~30 px of width per digit. There is no glass over the
    display: the model's gray dusty glass (section glass) veiled the dark display; the display face
    shines by itself like a filter (the section material has specular 0.5)."""
    lod = spec["lod"]
    if lod == 2:
        led = P("cs_led", "black")
        for win in (SPEED, N_SHOTS):
            window_quad(led, win, PT + 0.001)
        return [led]
    c_face, c_rim = PT + DISP_T + 0.0002, PT + DISP_T + 0.0058
    led = P("cs_led", "black", group=SEL_SCREEN2, section="led")
    led.fixed_uv = True
    uvl = led.bm.loops.layers.uv.get("UVMap") or led.bm.loops.layers.uv.new("UVMap")
    for key, win in (("speed", SPEED), ("shots", N_SHOTS)):
        xa, xb, ya, yb = win
        u0, u1, v0, v1 = LED_UV[key]
        for f in window_quad(led, win, c_face):
            for lp in f.loops:
                d = lp.vert.co - U.o
                a, bb = d.dot(U.u), d.dot(U.v)
                lp[uvl].uv = (u0 + (u1 - u0) * (a - xa) / (xb - xa), v0 + (v1 - v0) * (bb - ya) / (yb - ya))
    parts = [led]
    fa0, fa1, fb0, fb1 = DISP_FLANGE
    fca, fcb = (fa0 + fa1) / 2, (fb0 + fb1) / 2
    fl = P("cs_disp_flange", "black")
    b.plate(fl, U, fca, fcb, fa1 - fa0, fb1 - fb0, 0.004, PT, PT + DISP_T, n=2 if lod == 0 else 1)
    parts.append(fl)
    for nm, (xa, xb, ya, yb) in (("speed", SPEED), ("shots", N_SHOTS)):
        ca, cb, w, h = (xa + xb) / 2, (ya + yb) / 2, xb - xa, yb - ya
        bz = P("cs_%s_bezel" % nm, "black")
        b.bezel(bz, U, ca, cb, (w + 0.010, h + 0.010, 0.0035), (w + 0.0008, h + 0.0008, 0.001), PT + DISP_T, c_rim,
                c_in=PT + DISP_T, n=2 if lod == 0 else 1)
        parts.append(bz)
    if lod == 0:
        for k, (su, sv) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
            q = U.p(fca + su * ((fa1 - fa0) / 2 - 0.0055), fcb + sv * ((fb1 - fb0) / 2 - 0.0055), PT + DISP_T)
            sc = piece("cs_disp_screw%d" % k, "screw", "cs_screw_upper", q)
            b.screw(sc, q, U.n, r=0.0026, sides=6)
            parts.append(sc)
        # blank nameplate on rivets
        pl = P("cs_plate", "plate")
        b.plate(pl, U, (PLATE[0] + PLATE[1]) / 2, (PLATE[2] + PLATE[3]) / 2, PLATE[1] - PLATE[0], PLATE[3] - PLATE[2],
                0.004, PT, PT + 0.0015, n=2)
        for a in (PLATE[0] + 0.008, PLATE[1] - 0.008):
            for bb in (PLATE[2] + 0.008, PLATE[3] - 0.008):
                b.lathe(pl, U.p(a, bb, PT + 0.0015), U.n, [(0.0024, 0.0), (0.0016, 0.0010), (0.0, 0.0014)], 8)
        parts.append(pl)
        # fuse holders: a nut and a knurled cap
        for i, (a, bb) in enumerate(FUSES):
            fs = piece("cs_fuse%d" % i, "black", "cs_fuse", U.p(a, bb, 0))
            b.lathe(fs, U.p(a, bb, PT), U.n, [(0.0082, 0.0), (0.0082, 0.0030)], 6, ref=U.u)
            b.lathe(fs, U.p(a, bb, PT + 0.003), U.n, [(0.0062, 0.0), (0.0062, 0.0125), (0.0048, 0.0142)], 12,
                    knurl=(0, 1), depth=0.0006)
            parts.append(fs)
    return parts


def build_lamps(spec):
    lod = spec["lod"]
    if lod == 2:
        return []                                               # on the far LOD ozl_lamp is the scales, blink is the beacon
    parts = []
    for i, (a, bb, reg, sel) in enumerate(LAMPS):
        org = U.p(a, bb, 0)
        lens = piece("cs_lamp%d" % i, reg, "cs_lamp_" + reg, org, group=sel)
        rim = piece("cs_lamp%d_rim" % i, "chrome", "cs_lamp_rim", org)
        b.lamp(rim, lens, U, a, bb, PT, lod=lod)
        parts += [rim, lens] if lod == 0 else [lens]
    return parts


def build_desk(spec):
    """Desk: six toggles, the trigger switch under a hinged cover, three knobs with limbs, an emergency
    mushroom button on a yellow ring, a black button."""
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    for i, a in enumerate(TOG_A):
        org = D.p(a, TOG_B, 0)
        nut = piece("cs_tog%d_nut" % i, "steel", "cs_tog_nut", org)
        lev = piece("cs_tog%d_lever" % i, "chrome", "cs_tog_lever", org)
        b.toggle(nut, lev if lod == 0 else None, D, a, TOG_B, PT, lod=lod, up=i in (0, 3))
        parts += [nut] + ([lev] if lod == 0 else [])
    # trigger switch: a toggle (bone ozl_master) under a red hinged cover (bone ozl_guard)
    a, bb = MASTER
    org = D.p(a, bb, 0)
    gb = P("cs_guard_base", "cap_red")
    b.plate(gb, D, a, bb + 0.005, 0.040, 0.062, 0.004, PT, PT + 0.002, n=2 if lod == 0 else 1)
    parts.append(gb)
    nut = piece("cs_master_nut", "steel", "cs_tog_nut", org)
    lev = P("cs_master_lever", "chrome", group=SEL_MASTER)
    b.toggle(nut, lev, D, a, bb, PT + 0.002, lod=0, up=False, scale=0.8)
    parts += [nut, lev]
    gd = P("cs_guard", "cap_red", group=SEL_GUARD)
    c0, c1 = PT + 0.002, PT + 0.034
    g.box(gd, a - 0.017, a + 0.017, bb - 0.022, bb + 0.026, c1 - 0.002, c1, frame=D, **bev(lod, 0.0008))
    g.box(gd, a - 0.017, a + 0.017, bb - 0.022, bb - 0.020, c0, c1 - 0.002, frame=D)
    for s in (-1, 1):
        g.box(gd, a + s * 0.016 - 0.001, a + s * 0.016 + 0.001, bb - 0.020, bb + 0.026, c0, c1 - 0.002, frame=D)
    parts.append(gd)
    if lod == 0:
        hg = P("cs_guard_hinge", "cap_red")
        for s in (-1, 1):
            g.box(hg, a + s * 0.0195 - 0.0015, a + s * 0.0195 + 0.0015, bb + 0.023, bb + 0.033, c0, c1 + 0.003, frame=D,
                  r=0.0008, seg=1)
        b.lathe(hg, GUARD_HINGE - D.u * 0.022, D.u, [(0.0022, 0.0), (0.0022, 0.044)], 8, cap0=True)
        parts.append(hg)
    for i, (a, rr, _) in enumerate(KNOBS):
        org = D.p(a, KNOB_B, 0)
        kb = piece("cs_knob%d" % i, "knob", "cs_knob%d" % round(rr * 1000), org)
        pt = piece("cs_knob%d_ptr" % i, "ptr", "cs_knob_ptr", org)
        b.knob(kb, pt, D, a, KNOB_B, PT, rr, kind="skirt", lod=lod, angle=(-40.0, 25.0, 70.0)[i])
        parts += [kb] + ([pt] if lod == 0 else [])
    ring = P("cs_estop_ring", "estop_y")
    head = P("cs_estop", "cap_red")
    b.mushroom(ring, head, D, ESTOP[0], ESTOP[1], PT, lod=lod)
    bz = P("cs_button_bezel", "chrome")
    cap = P("cs_button", "black")
    b.push_button(bz, cap, D, BUTTON[0], BUTTON[1], PT, lod=lod)
    parts += [ring, head, cap] + ([bz] if lod == 0 else [])
    return parts


def build_printer(spec):
    """Built-in tape printer (like the Oehler 35P): a base with three keys and a light, a step with a slot
    and a toothed tear-off bar; the 57 mm tape comes out and curls back."""
    lod = spec["lod"]
    a0, a1, b0, b1, h = PRN
    pr = P("cs_printer", "printer")
    if lod == 2:
        g.box(pr, a0, a1, b0, b1, PT, PT + h, frame=D)
        return [pr]
    g.box(pr, a0, a1, b0, b1, PT, PT + PRN_BASE, frame=D, **bev(lod, 0.005))
    g.box(pr, a0 + 0.006, a1 - 0.006, b1 - 0.090, b1 - 0.004, PT + PRN_BASE - 0.004, PT + h, frame=D, **bev(lod, 0.007))
    parts = [pr]
    top = PT + h
    sl = P("cs_printer_slot", "black")
    g.box(sl, PAPER_A - 0.034, PAPER_A + 0.034, SLOT_B - 0.006, SLOT_B + 0.006, top - 0.0015, top + 0.0004, frame=D)
    parts.append(sl)
    if lod == 0:
        tb = P("cs_printer_tear", "steel")
        g.box(tb, PAPER_A - 0.036, PAPER_A + 0.036, SLOT_B - 0.0095, SLOT_B - 0.0065, top, top + 0.0018, frame=D)
        parts.append(tb)
        for i, da in enumerate((-0.036, 0.0, 0.036)):
            ca = (a0 + a1) / 2 + da
            k = piece("cs_prn_key%d" % i, "black", "cs_prn_key", D.p(ca, b0 + 0.028, 0))
            g.box(k, ca - 0.0085, ca + 0.0085, b0 + 0.0195, b0 + 0.0365, PT + PRN_BASE - 0.001, PT + PRN_BASE + 0.0042,
                  frame=D, r=0.0012, seg=1)
            parts.append(k)
        led = piece("cs_prn_led", "led_g", "cs_prn_led", D.p(a1 - 0.014, b0 + 0.028, 0), group=SEL_LAMP)
        b.lathe(led, D.p(a1 - 0.014, b0 + 0.028, PT + PRN_BASE), D.n, [(0.0028, 0.0), (0.0028, 0.0018), (0.0, 0.0034)], 8)
        parts.append(led)
    pp = P("cs_paper", "paper")
    g.sweep(pp, b.spline(paper_pts(), 3 if lod == 0 else 1), (1, 0, 0), 0.0004, PAPER_W / 2)
    parts.append(pp)
    return parts


def build_beacon(spec):
    """Flashing "shooting" beacon on the roof: a base, a knurled red cap (ozl_lamp_blink), a wire guard."""
    lod = spec["lod"]
    bx, by = BEACON
    dm = P("beacon_dome", "beacon", group=SEL_BLINK)
    prof = [(0.036, 0.020), (0.036, 0.024), (0.0365, 0.068), (0.034, 0.080), (0.026, 0.090), (0.012, 0.0955), (0.0, 0.0965)]
    if lod == 0:
        b.lathe(dm, (bx, by, CH), (0, 0, 1), prof, 16, knurl=(1, 2), depth=0.0012)
    else:
        b.lathe(dm, (bx, by, CH), (0, 0, 1), [prof[0], prof[3], prof[-1]], 8 if lod == 1 else 6)
    parts = [dm]
    if lod == 2:
        return parts
    bs = P("beacon_base", "black")
    b.lathe(bs, (bx, by, CH), (0, 0, 1), [(0.046, 0.0), (0.046, 0.006), (0.041, 0.012), (0.037, 0.020)],
            16 if lod == 0 else 8, cap1=False)
    parts.append(bs)
    if lod == 0:
        cg = P("beacon_cage", "steel")
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            ca, sa = math.cos(a), math.sin(a)
            pts = [(bx + rr * ca, by + rr * sa, CH + z) for rr, z in ((0.0405, 0.014), (0.0405, 0.072), (0.034, 0.090),
                                                                     (0.020, 0.0995), (0.012, 0.1015))]
            g.pipe(cg, pts, 0.0017, 4)
        ring = [(bx + 0.012 * math.cos(2 * math.pi * k / 8), by + 0.012 * math.sin(2 * math.pi * k / 8), CH + 0.1015)
                for k in range(9)]
        g.pipe(cg, ring, 0.0017, 4)
        parts.append(cg)
    return parts


def conn_base(i):
    y, z = CONN[i]
    return Vector((CX1 + 0.004, y, z))


def build_connectors(spec):
    """Connectors on the right cheek of the console: a strip on screws and four round connectors with
    cable plugs."""
    lod = spec["lod"]
    if lod == 2:
        return []
    pl = P("cs_conn_plate", "plate")
    g.box(pl, CX1, CX1 + 0.004, -0.06, 0.25, 0.16, 0.28, **bev(lod, 0.001))
    parts = [pl]
    if lod == 0:
        for k, (yy, zz) in enumerate(((-0.05, 0.17), (0.24, 0.17), (-0.05, 0.27), (0.24, 0.27))):
            sc = piece("cs_conn_screw%d" % k, "screw", "cs_screw_side", (CX1 + 0.004, yy, zz))
            b.screw(sc, (CX1 + 0.004, yy, zz), (1, 0, 0), r=0.0030)
            parts.append(sc)
    for i in range(len(CONN)):
        q = conn_base(i)
        fl = piece("cs_conn%d_flange" % i, "black", "cs_conn_flange", q)
        bd = piece("cs_conn%d_body" % i, "chrome", "cs_conn_body", q)
        nt = piece("cs_conn%d_nut" % i, "black", "cs_conn_nut", q)
        bt = piece("cs_conn%d_boot" % i, "rubber", "cs_conn_boot", q)
        b.mil_connector(fl, bd, nt, bt, q, (1, 0, 0), ref=(0, 0, 1), lod=lod)
        parts += [bd, bt] + ([fl, nt] if lod == 0 else [])
    return parts


def build_front_bits(spec):
    """Seal on the doors: wire through the lugs, a lead cup."""
    lod = spec["lod"]
    if lod > 0:
        return []
    sx = (XI0 + XI1) / 2
    yt = L["yt"]
    zs = (kc.PLINTH + L["zd0"] - 0.085) / 2 + 0.14
    sl = P("cs_seal", "seal")
    b.lathe(sl, (sx, yt - 0.006, zs - 0.025), (0, -1, 0), [(0.0062, 0.0), (0.0062, 0.0035), (0.0050, 0.0050)], 10)
    wr = P("cs_seal_wire", "steel")
    g.pipe(wr, b.spline([(sx - 0.012, yt - 0.006, zs), (sx - 0.004, yt - 0.010, zs - 0.020),
                         (sx + 0.004, yt - 0.010, zs - 0.020), (sx + 0.012, yt - 0.006, zs)], 3), 0.0008, 4)
    for s in (-1, 1):
        b.lathe(wr, (sx + s * 0.012, yt - 0.004, zs), (0, -1, 0), [(0.0035, 0.0), (0.0035, 0.004)], 8)
    return [sl, wr]


# =============================================================================
# Bed: a rail on trestles, the lower shelf, the tray at the breech
# =============================================================================
def leg_poly(sgn):
    """Trestle leg in the y-z plane: a 35 mm square tube from the rail to the support plate, splayed."""
    yt, yf = sgn * leg_y(0.72), sgn * leg_y(LEG_Z0)
    return [(yt - LEG_H, 0.72), (yt + LEG_H, 0.72), (yf + LEG_H, LEG_Z0), (yf - LEG_H, LEG_Z0)]


def build_bench(spec):
    lod = spec["lod"]
    parts = []
    rl = P("rail", "rail")
    # channel: the body and two lips on top with a groove; the ends are welded caps on bolts
    g.box(rl, RX0, RX1, -0.05, 0.05, 0.72, 0.785, **bev(lod, 0.002))
    if lod < 2:
        for ya, yb in ((-0.06, -0.009), (0.009, 0.06)):
            g.box(rl, RX0, RX1, ya, yb, 0.785, ZR, **bev(lod, 0.0015))
    else:
        g.box(rl, RX0, RX1, -0.06, 0.06, 0.785, ZR)
    parts.append(rl)
    if lod < 2:
        ec = P("rail_ends", "bench")
        for xa, xb in ((RX0 - 0.008, RX0), (RX1, RX1 + 0.008)):
            g.box(ec, xa, xb, -0.066, 0.066, 0.714, ZR + 0.002, **bev(lod, 0.002))
        parts.append(ec)
    if lod == 0:
        for k, (xx, sg) in enumerate(((RX0 - 0.008, -1), (RX1 + 0.008, 1))):
            for yy in (-0.036, 0.036):
                bt = piece("rail_bolt%d_%d" % (k, yy > 0), "bolt", "bench_bolt_x", (xx, yy, 0.752))
                b.hex_bolt(bt, (xx, yy, 0.752), (sg, 0, 0), r=0.0075, h=0.005, lod=lod)
                parts.append(bt)
        rr = P("rail_ruler", "ruler")
        g.box(rr, RULER[0], RULER[1], -0.0608, -0.0600, RULER[2], RULER[3])
        parts.append(rr)
        for k, xx in enumerate((RULER[0] + 0.01, (RULER[0] + RULER[1]) / 2, RULER[1] - 0.01)):
            sc = piece("rail_ruler_rivet%d" % k, "screw", "rail_rivet", (xx, -0.0608, 0.7925))
            b.lathe(sc, (xx, -0.0608, 0.7925), (0, -1, 0), [(0.0022, 0.0), (0.0015, 0.0008), (0.0, 0.0011)], 6)
            parts.append(sc)
    bn = P("bench", "bench")
    for tx in TRESTLES:
        for s in (-1, 1):
            b.prism_bev(bn, leg_poly(s), (1, 2), tx - LEG_H, tx + LEG_H, *((0.0025, 1) if lod == 0 else (0.0, 0)))
        g.box(bn, tx - 0.03, tx + 0.03, -0.075, 0.075, 0.70, 0.72, **bev(lod, 0.002))
        if lod < 2:
            g.box(bn, tx - 0.0125, tx + 0.0125, -0.17, 0.17, 0.22, 0.25)
            # gusset under the support plate between the legs
            g.prism(bn, [(-0.033, 0.70), (0.033, 0.70), (0.050, 0.632), (-0.050, 0.632)], (1, 2), tx - 0.003, tx + 0.003)
            # leg support plates
            for s in (-1, 1):
                yf = s * leg_y(LEG_Z0)
                g.box(bn, tx - 0.030, tx + 0.030, yf - 0.030, yf + 0.030, LEG_Z0 - 0.006, LEG_Z0)
    if lod < 2:
        g.box(bn, TRESTLES[0] + LEG_H, TRESTLES[1] - LEG_H, -0.015, 0.015, 0.22, 0.25)
    parts.append(bn)
    # leveling screws with heels
    ft = P("bench_feet", "rubber")
    st = P("bench_feet_screw", "bolt")
    for tx in TRESTLES:
        for s in (-1, 1):
            yf = s * leg_y(LEG_Z0)
            if lod == 0:
                b.lathe(ft, (tx, yf, 0.0), (0, 0, 1), [(0.027, 0.0), (0.027, 0.006), (0.022, 0.0115), (0.009, 0.0135)], 10)
                b.lathe(st, (tx, yf, 0.012), (0, 0, 1), [(0.0062, 0.0), (0.0062, LEG_Z0 - 0.018)], 8)
                b.hex_bolt(st, (tx, yf, 0.022), (0, 0, 1), r=0.0105, h=0.006, lod=1, washer=False)
            elif lod == 1:
                b.lathe(ft, (tx, yf, 0.0), (0, 0, 1), [(0.025, 0.0), (0.025, 0.012)], 6)
                b.lathe(st, (tx, yf, 0.012), (0, 0, 1), [(0.0065, 0.0), (0.0065, LEG_Z0 - 0.018)], 4)
            else:
                g.box(ft, tx - 0.025, tx + 0.025, yf - 0.025, yf + 0.025, 0.0, LEG_Z0 - 0.006)
    parts.append(ft)
    if lod < 2:
        parts.append(st)
    if lod == 0:
        for tx in TRESTLES:
            for k, yy in enumerate((-0.06, 0.06)):
                bt = piece("bench_bolt%d_%d" % (int(tx * 100), k), "bolt", "bench_bolt_z", (tx, yy, 0.70))
                b.hex_bolt(bt, (tx, yy, 0.70), (0, 0, -1), r=0.0085, h=0.0055, lod=lod)
                parts.append(bt)
    parts += build_shelf(spec) + build_tray(spec) + build_rod(spec)
    return parts


def build_shelf(spec):
    """Lower shelf - a steel tray with sides on the trestle crosspieces."""
    lod = spec["lod"]
    x0, x1, y0, y1, z0, h = SHELF
    sh = P("shelf", "shelf")
    t = 0.002
    if lod == 2:
        g.box(sh, x0, x1, y0, y1, z0, z0 + t)
        return [sh]
    g.box(sh, x0, x1, y0, y1, z0, z0 + t)
    for ya, yb in ((y0, y0 + t), (y1 - t, y1)):
        g.box(sh, x0, x1, ya, yb, z0 + t, z0 + h)
    for xa, xb in ((x0, x0 + t), (x1 - t, x1)):
        g.box(sh, xa, xb, y0 + t, y1 - t, z0 + t, z0 + h)
    if lod == 0:
        # bent edge of the sides
        for ya, yb in ((y0 - 0.004, y0 + t), (y1 - t, y1 + 0.004)):
            g.box(sh, x0, x1, ya, yb, z0 + h - t, z0 + h)
    return [sh]


def build_tray(spec):
    """Cartridge tray at the breech: stands on two bent brackets screwed to the front face of the rail;
    the sides have a rolled edge."""
    lod = spec["lod"]
    if lod == 2:
        return []
    x0, x1, y0, y1, z0, h = TRAY
    tr = P("tray", "bench")
    t = 0.0018
    g.box(tr, x0, x1, y0, y1, z0, z0 + t)
    for ya, yb in ((y0, y0 + t), (y1 - t, y1)):
        g.box(tr, x0, x1, ya, yb, z0 + t, z0 + h)
    for xa, xb in ((x0, x0 + t), (x1 - t, x1)):
        g.box(tr, xa, xb, y0 + t, y1 - t, z0 + t, z0 + h)
    if lod == 0:
        g.pipe(tr, [(x0, y0, z0 + h), (x1, y0, z0 + h), (x1, y1, z0 + h), (x0, y1, z0 + h), (x0, y0, z0 + h)], 0.0018, 6)
    parts = [tr]
    # brackets: a strap on the rail face, a bend under the tray bottom
    br = P("tray_brackets", "bench")
    for xx in (x0 + 0.03, x1 - 0.03):
        g.box(br, xx - 0.008, xx + 0.008, y1, -0.050, 0.725, 0.776)
        g.box(br, xx - 0.008, xx + 0.008, y0 + 0.006, -0.050, z0 - 0.0035, z0)
    parts.append(br)
    if lod == 0:
        for k, xx in enumerate((x0 + 0.03, x1 - 0.03)):
            bt = piece("tray_bolt%d" % k, "bolt", "tray_bolt", (xx, y1, 0.763))
            b.hex_bolt(bt, (xx, y1, 0.763), (0, -1, 0), r=0.0062, h=0.0042, lod=lod)
            parts.append(bt)
    return parts


def build_rod(spec):
    """Cleaning rod on the lower shelf in front of the rags: a brass rod lies on the shelf sheet, at one
    end a loop ring in the shelf plane (the ring seam is under the crimp sleeve at the joint with the
    rod), at the working end the rod is flattened into a blade with a slot for a rag patch. The far LOD
    does not need it."""
    lod = spec["lod"]
    if lod == 2:
        return []
    top = SHELF[4] + 0.002                                      # top of the shelf sheet
    zc = top + ROD_R
    sides = 6 if lod == 0 else 4
    rd = P("shelf_rod", "rod")
    b.lathe(rd, (ROD_X0, ROD_Y, zc), (1, 0, 0), [(ROD_R, 0.0), (ROD_R, ROD_X1 - ROD_X0)], sides, cap0=True)
    n = 16 if lod == 0 else 8
    cx = ROD_X0 - LOOP_R
    g.pipe(rd, [(cx + LOOP_R * math.cos(2 * math.pi * k / n), ROD_Y + LOOP_R * math.sin(2 * math.pi * k / n), zc)
                for k in range(n + 1)], ROD_R, sides)
    if lod == 1:
        return [rd]
    # crimp sleeve at the joint of the loop and the rod
    b.lathe(rd, (ROD_X0 - 0.003, ROD_Y, zc), (1, 0, 0),
            [(0.0034, 0.0), (0.0041, 0.0015), (0.0041, 0.0135), (0.0034, 0.015)], 8, cap0=True)
    # eye: a transition to a cone, a 6.4 x 2.2 mm blade at the shelf sheet with a 14 x 2.2 mm slot
    b.lathe(rd, (ROD_X1, ROD_Y, zc), (1, 0, 0), [(ROD_R, 0.0), (0.0022, 0.005)], 6)
    e0, e1 = ROD_X1 + 0.003, ROD_X1 + 0.027
    z0, z1 = top + 0.0003, top + 0.0025
    g.box(rd, e0, e0 + 0.005, ROD_Y - 0.0032, ROD_Y + 0.0032, z0, z1)
    g.box(rd, e1 - 0.003, e1, ROD_Y - 0.0032, ROD_Y + 0.0032, z0, z1)
    for ya, yb in ((ROD_Y - 0.0032, ROD_Y - 0.0011), (ROD_Y + 0.0011, ROD_Y + 0.0032)):
        g.box(rd, e0 + 0.005, e1 - 0.003, ya, yb, z0, z1)
    return [rd]


# =============================================================================
# Barrel clamp with the barrel (the suppressor is vanilla, a proxy)
# =============================================================================
def build_clamp(spec):
    lod = spec["lod"]
    parts = []
    bs = P("clamp_base", "bench")
    g.box(bs, CL0, CL1, -0.08, 0.08, ZR, ZR + 0.025, **bev(lod, 0.003, 2))
    parts.append(bs)
    if lod < 2:
        rd = P("clamp_ends", "red")
        for xa, xb in ((CL0, CL0 + 0.03), (CL1 - 0.03, CL1)):
            g.box(rd, xa, xb, -0.08, 0.08, ZR + 0.025, ZR + 0.09, **bev(lod, 0.003))
        parts.append(rd)
    # barrel block on the guides
    bk = P("clamp_block", "bench")
    g.box(bk, BLOCK[0], BLOCK[1], -0.075, 0.075, ZR + 0.03, ZB + 0.06, **bev(lod, 0.004, 2))
    parts.append(bk)
    # V-block and the red cover on bolts
    if lod < 2:
        vb = P("clamp_vblock", "bench")
        g.box(vb, VBLK[0], VBLK[1], -0.06, 0.06, ZR + 0.025, ZB - 0.003, **bev(lod, 0.003, 2))
        parts.append(vb)
    cp = P("clamp_cap", "red")
    g.box(cp, VBLK[0], VBLK[1], -0.06, 0.06, ZB + 0.003 if lod < 2 else ZR + 0.025, ZB + 0.04, **bev(lod, 0.003, 2))
    parts.append(cp)
    # barrel: thicker at the chamber, thinner toward the muzzle, a thread for the suppressor
    br = P("barrel", "barrel")
    x0, x1, r = BARREL
    if lod == 0:
        prof = [(0.0165, 0.0), (0.0165, 0.045), (0.0152, 0.060), (0.0138, 0.100), (0.0125, 0.150), (0.0125, x1 - x0 - 0.016),
                (0.0110, x1 - x0 - 0.013), (0.0110, x1 - x0)]
        b.lathe(br, (x0, 0.0, ZB), (1, 0, 0), prof, 16)
    else:
        g.cyl(br, ((x0 + x1) / 2, 0.0, ZB), "x", r, x1 - x0, (8, 6)[lod - 1])
    parts.append(br)
    if lod == 2:
        sp = P("suppressor", "black")                           # nearer - the vanilla PB suppressor (a proxy)
        g.cyl(sp, ((SUPP[0] + SUPP[1]) / 2, 0.0, ZB), "x", SUPP[2], SUPP[1] - SUPP[0], 6)
        parts.append(sp)
        return parts
    gr = P("clamp_rods", "chrome")
    for y in (-0.055, 0.055):
        b.lathe(gr, (CL0 + 0.03, y, ZR + 0.06), (1, 0, 0), [(0.011, 0.0), (0.011, CL1 - CL0 - 0.06)], 12 if lod == 0 else 6,
                cap1=False)
    parts.append(gr)
    # red collar around the barrel on the block face, its clamp screw
    col = P("clamp_collar", "red")
    prof = [(0.0170, 0.0), (0.0300, 0.0), (0.0340, 0.003), (0.0340, 0.015), (0.0300, 0.018), (0.0170, 0.018)]
    b.lathe(col, (BLOCK[1], 0.0, ZB), (1, 0, 0), prof if lod == 0 else [prof[1], prof[2], prof[3], prof[4]],
            14 if lod == 0 else 8, cap1=False)
    if lod == 0:
        g.box(col, BLOCK[1] + 0.003, BLOCK[1] + 0.015, -0.009, 0.009, ZB + 0.030, ZB + 0.041, r=0.0012, seg=1)
    parts.append(col)
    # lever on the block side (bone ozl_lever): at rest - up and slightly back, when "working" - down, "closed"
    piv = Vector(LEVER_PIV)
    boss = P("clamp_lever_boss", "steel")
    b.lathe(boss, (piv.x, -0.075, piv.z), (0, -1, 0), [(0.0125, 0.0), (0.0125, 0.006), (0.0095, 0.0085)],
            12 if lod == 0 else 6)
    parts.append(boss)
    t = math.radians(LEVER_REST)
    d = Vector((-math.sin(t), 0.0, math.cos(t)))
    lv = P("clamp_lever", "steel", group=SEL_LEVER)
    b.lathe(lv, piv, (0, -1, 0), [(0.0085, -0.002), (0.0085, 0.006), (0.0070, 0.0075)], 10 if lod == 0 else 6, cap0=True)
    g.pipe(lv, [tuple(piv + d * 0.006), tuple(piv + d * 0.080)], 0.0060, 8 if lod == 0 else 4)
    parts.append(lv)
    gp = P("clamp_grip", "rubber", group=SEL_LEVER)
    if lod == 0:
        b.lathe(gp, piv + d * 0.078, d, [(0.0085, 0.0), (0.0105, 0.006), (0.0110, 0.030), (0.0100, 0.040), (0.0070, 0.046),
                                         (0.0, 0.0485)], 12, cap0=True)
    else:
        b.lathe(gp, piv + d * 0.078, d, [(0.010, 0.0), (0.010, 0.046)], 6, cap0=True)
    parts.append(gp)
    if lod == 1:
        return parts
    # socket-head screws: the plate on the rail, the end blocks, the V-block cover, the collar
    sock = P("clamp_sockets", "black")
    k = 0
    heads = [((x, y, ZR + 0.025), 0.0062, 0.0055) for x in (-0.11, 0.11) for y in (-0.07, 0.07)]
    heads += [((x, y, ZR + 0.09), 0.0068, 0.0065) for x in (CL0 + 0.015, CL1 - 0.015) for y in (-0.05, 0.05)]
    heads += [((x, y, ZB + 0.04), 0.0068, 0.0065) for x in (VBLK[0] + 0.015, VBLK[1] - 0.015) for y in (-0.042, 0.042)]
    heads += [((BLOCK[1] + 0.009, 0.0, ZB + 0.041), 0.0050, 0.0050)]
    for q, rr, hh in heads:
        hd = piece("clamp_shcs%d" % k, "bolt", "clamp_shcs%d" % round(rr * 1e4), q)
        b.shcs(hd, sock, q, (0, 0, 1), r=rr, h=hh, lod=lod)
        parts.append(hd)
        k += 1
    parts.append(sock)
    # retaining rings on the guides at the block
    for y in (-0.055, 0.055):
        for xa in (BLOCK[0] - 0.008, BLOCK[1]):
            ck = piece("clamp_stop%d_%d" % (int(xa * 1000), y > 0), "bolt", "clamp_stop", (xa, y, ZR + 0.06))
            b.lathe(ck, (xa, y, ZR + 0.06), (1, 0, 0), [(0.0172, 0.0), (0.0172, 0.008)], 12, cap0=True)
            parts.append(ck)
    # pressure sensor on the barrel at the chamber: a hexagon, a body, a coupling nut, a cable tail
    sn = P("clamp_sensor", "steel")
    z0 = ZB + 0.0125 - 0.002
    b.lathe(sn, (SENSOR_X, 0.0, z0), (0, 0, 1), [(0.0088, 0.0), (0.0088, 0.0105)], 6, ref=(1, 0, 0))
    b.lathe(sn, (SENSOR_X, 0.0, z0 + 0.0105), (0, 0, 1), [(0.0062, 0.0), (0.0062, 0.018)], 12)
    parts.append(sn)
    sk = P("clamp_sensor_nut", "black")
    b.lathe(sk, (SENSOR_X, 0.0, z0 + 0.0285), (0, 0, 1), [(0.0074, 0.0), (0.0074, 0.010), (0.0062, 0.0115)], 14,
            knurl=(0, 1), depth=0.0006, cap0=True)
    parts.append(sk)
    sb = P("clamp_sensor_boot", "cable_red")
    b.lathe(sb, (SENSOR_X, 0.0, z0 + 0.040), (0, 0, 1), [(0.0060, 0.0), (0.0052, 0.008), (0.0042, 0.014)], 10)
    parts.append(sb)
    # trigger solenoid behind the block, along the bore axis
    so = P("clamp_solenoid", "black")
    b.lathe(so, (BLOCK[0], 0.0, ZB), (-1, 0, 0), [(0.0125, 0.0), (0.0125, 0.034), (0.0105, 0.037), (0.0062, 0.0375),
                                                (0.0062, 0.046), (0.0048, 0.048)], 10)
    b.lathe(so, (BLOCK[0] - 0.012, 0.0, ZB), (-1, 0, 0), [(0.0132, 0.0), (0.0132, 0.003)], 10, cap0=True)
    parts.append(so)
    return parts


# =============================================================================
# Chronograph frames (Skyscreen III, U-shaped)
# =============================================================================
def build_frames(spec):
    lod = spec["lod"]
    parts = []
    for i, fx in enumerate(FRAMES):
        org = (fx, 0.0, 0.0)
        hs = P("frame%d_housing" % i, "housing", uv_name="frame_housing", uv_origin=org)
        poly = [(fx - 0.034, FZ0 if lod < 2 else ZR), (fx + 0.034, FZ0 if lod < 2 else ZR), (fx + 0.042, FZ1),
                (fx - 0.042, FZ1)]
        b.prism_bev(hs, poly, (0, 2), -FHW, FHW, *((0.003, 1) if lod == 0 else (0.0, 0)))
        if lod < 2:
            g.box(hs, fx - 0.035, fx + 0.035, -0.05, 0.05, ZR, FZ0 + 0.001, **bev(lod, 0.002))
        parts.append(hs)
        up = P("frame%d_posts" % i, "bench", uv_name="frame_posts", uv_origin=org)
        for s in (-1, 1):
            b.lathe(up, (fx, s * POST_Y, FZ1 + 0.008), (0, 0, 1), [(0.0050, 0.0), (0.0050, FTOP - FZ1 - 0.002)],
                    10 if lod == 0 else (6 if lod == 1 else 4), cap0=False, cap1=False)
        parts.append(up)
        tb = P("frame%d_bar" % i, "diffuser", uv_name="frame_bar", uv_origin=org)
        g.box(tb, fx - 0.02, fx + 0.02, -FHW - 0.005, FHW + 0.005, FTOP, FTOP + 0.022, **bev(lod, 0.004))
        parts.append(tb)
        if lod == 2:
            continue
        df = P("frame%d_diff" % i, "diffuser_in", uv_name="frame_diff", uv_origin=org)
        g.box(df, fx - 0.013, fx + 0.013, -FHW + 0.02, FHW - 0.02, FTOP - 0.0012, FTOP)
        parts.append(df)
        ln = P("frame%d_window" % i, "lens", uv_name="frame_window", uv_origin=org)
        g.box(ln, fx - 0.012, fx + 0.012, -0.13, 0.13, FZ1 - 0.001, FZ1 + 0.0008)
        parts.append(ln)
        if lod == 1:
            continue
        wf = P("frame%d_window_frame" % i, "black", uv_name="frame_window_frame", uv_origin=org)
        b.bezel(wf, g.Frame((0, 0, FZ1), (1, 0, 0), (0, 1, 0), (0, 0, 1)), fx, 0.0, (0.034, 0.272, 0.004),
                (0.0242, 0.2622, 0.0015), 0.0, 0.0022, c_in=-0.0005, n=1)
        parts.append(wf)
        so = P("frame%d_sockets" % i, "black", uv_name="frame_sockets", uv_origin=org)
        for s in (-1, 1):
            b.lathe(so, (fx, s * POST_Y, FZ1), (0, 0, 1), [(0.0095, 0.0), (0.0095, 0.010), (0.0072, 0.0135)], 10)
        parts.append(so)
        # thumbscrew fixing to the rail
        kn = P("frame%d_knob" % i, "black", uv_name="frame_knob", uv_origin=org)
        b.lathe(kn, (fx, -0.05, ZR + 0.005), (0, -1, 0), [(0.0045, 0.0), (0.0045, 0.012)], 8)
        b.lathe(kn, (fx, -0.062, ZR + 0.005), (0, -1, 0), [(0.0155, 0.0), (0.0155, 0.007), (0.0120, 0.0095)], 12,
                knurl=(0, 1), depth=0.0028, cap0=True)
        parts.append(kn)
        # BNC jack on the end of the body and a plug
        q = (fx, FHW, (FZ0 + FZ1) / 2)
        nut = P("frame%d_bnc_nut" % i, "steel", uv_name="frame_bnc_nut", uv_origin=q)
        bd = P("frame%d_bnc_body" % i, "chrome", uv_name="frame_bnc_body", uv_origin=q)
        sv = P("frame%d_bnc_sleeve" % i, "chrome", uv_name="frame_bnc_sleeve", uv_origin=q)
        bt = P("frame%d_bnc_boot" % i, "rubber", uv_name="frame_bnc_boot", uv_origin=q)
        b.bnc(nut, bd, sv, bt, q, (0, 1, 0), lod=lod)
        parts += [nut, bd, sv, bt]
    return parts


# =============================================================================
# Cables: from the frames - along clips on the rear face of the rail and along the rear leg of the left
# trestle on ties; from the pressure sensor - along the front leg; from the solenoid - behind the rail
# to the rear leg; all go to the connectors on the right cheek of the console
# =============================================================================
def leg_pt(sgn, z, w=0.0, dx=0.0):
    """A point on the outer (-x) face of a leg of the left trestle: w - a shift across the leg (toward +y
    for the rear one), dx - farther from the face."""
    tx = TRESTLES[0]
    t = Vector((0.0, sgn * (LEG_FOOT - LEG_TOP), -(0.72 - 0.008))).normalized()
    wv = Vector((1.0, 0.0, 0.0)).cross(t) * sgn
    c = Vector((tx - LEG_H - 0.0050 - dx, sgn * leg_y(z), z))
    return tuple(c + wv * w)


def plug_end(i):
    return conn_base(i) + Vector((0.055, 0.0, 0.0))


def to_plug(i, start):
    """Cable tail from the leg to the plug of connector i: smoothly to the cheek, the last segment along
    the plug axis."""
    e = plug_end(i)
    s = Vector(start)
    return [tuple(s.lerp(e, 0.45) + Vector((0.010, 0.0, -0.010))), tuple(e + Vector((0.020, 0.0, -0.004))),
            tuple(e + Vector((0.008, 0.0, 0.0))), tuple(e)]


def build_cables(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    zl = [0.60, 0.45, 0.31]                                     # down the leg
    # from the frames: BNC on the end of the body -> back under the rail lip -> to the left trestle -> along the rear leg
    for i, fx in enumerate(FRAMES):
        yr = 0.072 + 0.012 * i
        w = (0.0, 0.0098)[i]
        s = (fx, FHW + 0.045, (FZ0 + FZ1) / 2)
        pts = [s, (fx, FHW + 0.060, 0.822), (fx - 0.018, FHW + 0.048, 0.798), (fx - 0.06, yr + 0.022, 0.770),
               (fx - 0.12, yr, 0.753)]
        pts += [(x, yr, 0.752) for x in (0.45, 0.20, -0.02) if x < fx - 0.16]
        pts += [(-0.060, yr + 0.004, 0.748), (-0.092, 0.090 + 0.004 * i, 0.725), (-0.112, 0.092 + 0.004 * i, 0.700),
                (-0.127, 0.086 + 0.003 * i, 0.655)]
        pts += [leg_pt(1, z, w) for z in zl]
        cb = P("cable_frame%d" % i, "cable")
        b.cable(cb, pts + to_plug(2 + i, pts[-1]), 0.0045, lod)
        parts.append(cb)
    # from the trigger solenoid: back behind the rail, down to the rear leg
    so = (BLOCK[0] - 0.048, 0.0, ZB)
    pts = [so, (BLOCK[0] - 0.060, 0.004, ZB - 0.002), (-0.170, 0.030, 0.892), (-0.172, 0.075, 0.862), (-0.160, 0.094, 0.810),
           (-0.142, 0.098, 0.755), (-0.128, 0.094, 0.706), (-0.131, 0.080, 0.655)]
    pts += [leg_pt(1, z, -0.0098) for z in zl]
    cb = P("cable_solenoid", "cable")
    b.cable(cb, pts + to_plug(1, pts[-1]), 0.0040, lod)
    parts.append(cb)
    # from the pressure sensor: up and forward, down in front of the clamp, along the front leg
    z0 = ZB + 0.0125 - 0.002 + 0.054
    pts = [(SENSOR_X, 0.0, z0), (SENSOR_X, -0.004, z0 + 0.014), (SENSOR_X - 0.004, -0.030, z0 + 0.026),
           (0.004, -0.070, 0.975), (-0.012, -0.100, 0.920), (-0.026, -0.112, 0.850), (-0.040, -0.110, 0.785),
           (-0.068, -0.098, 0.735), (-0.098, -0.088, 0.705), (-0.124, -0.090, 0.665)]
    pts += [leg_pt(-1, z) for z in zl]
    cb = P("cable_sensor", "cable_red")
    b.cable(cb, pts + to_plug(0, pts[-1]), 0.0040, lod)
    parts.append(cb)
    if lod == 1:
        return parts
    # clips on the rear face of the rail, ties on the legs
    cl = P("cable_clips", "steel")
    for x in (0.75, 0.45, 0.20, -0.02):
        g.box(cl, x - 0.006, x + 0.006, 0.050, 0.053, 0.736, 0.774)
        g.box(cl, x - 0.006, x + 0.006, 0.053, 0.0935, 0.7428, 0.7445)
        g.box(cl, x - 0.006, x + 0.006, 0.0920, 0.0935, 0.7445, 0.7625)
        g.box(cl, x - 0.006, x + 0.006, 0.060, 0.0935, 0.7625, 0.7642)
    parts.append(cl)
    tz = P("cable_ties", "zip")
    for sgn in (1, -1):
        t = Vector((0.0, sgn * (LEG_FOOT - LEG_TOP), -(0.72 - 0.008))).normalized()
        for z in (0.56, 0.45, 0.35):
            c = Vector((TRESTLES[0], sgn * leg_y(z), z))
            b.tie(tz, c, t, (-1.0, 0.0, 0.0), (-LEG_H - 0.0012, LEG_H + 0.0107), LEG_H * 1.035 + 0.0012)
    parts.append(tz)
    return parts


def build_lod(spec):
    parts = build_console(spec) + build_bench(spec) + build_clamp(spec) + build_frames(spec) + build_cables(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    poly = kc.profile(CY0, CY1, L)
    cons = kx.prism_pts([(y, 0.0 if abs(z - kc.PLINTH) < 1e-6 else z) for y, z in poly] + [(CY1, CH), (L["yu1"] - 0.05, CH)],
                        CX0, CX1)
    bench = kx.box_pts(RX0, RX1, -0.27, 0.27, 0.0, FTOP + 0.022)
    metal = kx.PEN + r"\metalplate.rvmat"
    comps = [(cons, metal), (bench, metal)]
    memory = {
        "invView": [(0.0, -3.0, 1.1)],
        "ce_center": [(0.0, 0.0, CH / 2)],
        "ce_radius": [(1.05, 0.0, CH / 2)],
    }
    info = BOUNDS["info"]
    for gd in info["gauges"]:
        if gd["group"]:
            memory[gd["group"] + "_axis"] = list(info["needle_axis"](gd))
    # toggle cover, toggle, lever - the point order of AXES (as in the preview)
    for sel in (SEL_GUARD, SEL_MASTER, SEL_LEVER):
        memory[sel + "_axis"] = AXES[sel + "_axis"]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (min(lo[0], CX0), max(hi[0], RX1), min(lo[1], CY0), max(hi[1], CY1), 0.0, max(hi[2], CH))
    return comps, 250.0, memory, bbox


# the first ones are for the --look preview (M.look_shots): the console, the display close up, the
# clamp, overall, the frames, the lower shelf, the cleaning rod on it; the "working" look: the console,
# the display and the clamp
SHOTS = [
    ("console", (-0.25, -1.45, 1.45), (-0.61, -0.10, 0.95), 34),
    ("displays", (-0.50, -0.46, 1.17), (-0.60, -0.03, 1.01), 42),
    ("clamp", (0.42, -0.92, 1.18), (0.06, -0.02, 0.86), 34),
    ("front", (-1.3, -3.2, 1.75), (0.0, 0.0, 0.75), 30),
    ("frames", (1.6, -1.2, 1.35), (0.72, 0.0, 0.95), 32),
    ("shelf", (0.95, -1.25, 0.80), (0.42, 0.0, 0.36), 32),
    ("rod", (-0.12, -0.62, 0.62), (0.13, -0.07, 0.27), 38),
    ("desk", (-0.55, -0.85, 1.35), (-0.62, -0.25, 0.83), 34),
    ("cables", (0.38, 0.92, 0.62), (-0.15, 0.08, 0.36), 30),
    ("back", (1.5, 2.6, 1.6), (0.0, 0.0, 0.7), 30),
]

M.look_shots = (7, 3)
M.run(build_lod, collision, SHOTS, row_step=2.4, row_shot=((2.4, -8.0, 1.8), (2.4, 0, 0.7)))
