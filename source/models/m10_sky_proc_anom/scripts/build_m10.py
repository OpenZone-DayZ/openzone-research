"""M10 - washing-machine centrifuge: the Clear Sky Anomaly Analyzer (OZL_Sky_Proc_Anom).
Analyzer: cargo 4x4, no modules (no module_1..3 points, as in M02, M04, M06 and M08).

    blender --background --python build_m10.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (panel scales, instrument scale, the
unit's front panel, signs, dosimeter display frames). Where things are - m10_layout.py (shared with
make_decals.py).

Look: "dayz" (matte, dirtier, coloured AO). The machine is its own copy of the B4 base, more
detailed (m10_washer.py: rounded body and deck, an opening collar, turned knobs, hinges, moulding; at
the back finned motors, a belt, suspension springs, a pump, a corrugated hose to the floor, a
capacitor, a terminal box and a harness); the drum is perforated. The detector unit has a front panel
on screws, lamps in chrome bezels, a toggle, a knurled knob, a probe socket, a side handle, vents and
cable glands; the probe (a counter in a tube) sits on a bracket above the centrifuge opening with its
cable to the unit socket. Small props are vanilla DayZ items through proxies (kvanilla): a sheet of
paper on the centrifuge lid (on tape), a pen on the unit, 9 V batteries (Krona - the power of the
RKSB-104) on the tank lid, on the floor an electrician kit with pliers, a screwdriver, tape, a rag
by the end of the drain hose.

A Clear Sky makeshift built from real things:
- washing machine - the B4 base (m10_washer.py on top of kwasher.layout), Sibir-5: 675 x 700 x 375 mm
  (W x H x D), 40 kg (data sheet; the Sibir-5M is 670 x 700 x 375, the Sibir-6 680 x 700 x 380). The
  washing tank under a lid is at the left, the centrifuge at the right; the panel with the
  "wash / spin / mode" knobs follows a photo of the panel. The back wall is removed and the
  centrifuge lid is permanently tilted open: the drum is visible, with three sample containers in it
  (the analyzer's sample chamber);
- detector unit - a home-made steel box 240 x 160 x 130 mm on the tank lid, with a panel
  microammeter M42100 (80 x 80 x 50 mm), lamps "power" and "count", a toggle, a sensitivity knob, a
  probe socket; a telescopic antenna from a receiver (4 sections, 0.48 m), a "high voltage" sign; the
  cables from the unit are taped together and go into the open back of the machine to a terminal box;
- probe - a tube of diameter 32 x 135 mm (like the remote detector units of the DP-5 and home-made
  counters on the SBM-20 - an estimate), on a bracket at the centrifuge opening, looking into the
  drum above the samples;
- dosimeter on the unit - a household RKSB-104 (1990s); no data-sheet sizes were found, so the
  envelope 165 x 83 x 30 mm is taken from the proportions of a photo - check it in the shared pass;
- crate stand - a low plank one 0.72 x 0.13 x 0.42 m, unpainted, a yellow-black stripe at the front.
Total 0.72 x 1.45 (with the antenna; 1.15 without it, to the open lid) x 0.42 m.

Work look: the instrument scale and the "power" lamp are ozl_screen (steady in "work"), the "count"
lamp is ozl_lamp_work (blinks), the dosimeter display is ozl_lcd (own texture, section lcd: "off" is
empty, "work" plays frames with readings); the drum is the bone ozl_drum on the source ozl_work - a
model.cfg loop (sourceAddress loop, 6 turns per 2 s pass - 3 rev/s); the instrument needle is the
bone ozl_meter on its own source (wobble); the "spin" knob on the machine panel (ozl_knob) and the
unit toggle (ozl_toggle) take the "work" pose on the source ozl_pose (turned for the duration of
the work).

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
import kwasher  # noqa: E402
import kwood  # noqa: E402
import m10_washer as W  # noqa: E402
from m10_geo import (box_to, frame_at, frame_axis, hexagon, knurl_poly, lathe, screw,  # noqa: E402
                     spline)
from m10_layout import (ARC_R, BNC, BOARD, CX0, CX1, CY0, CY1, DIAL_H, DIAL_W, DOS, DOS_BTN,  # noqa: E402
                        DOS_GRILLE, DOS_TOP, DX0, DX1, DXC, DY0, DY1, DZ0, DZ1, DZF, HM, KNOB, LAMP_G, LAMP_R,
                        LCD, MX, MZ, PIVOT_DZ, PLATE, TOGGLE, WIN, X0, X1, Y0, Y1, YF, ZS)

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m (the rest is in m10_layout.py)
# =============================================================================
INS = W.inner(X0, X1, Y0, Y1, ZS, HM)
LAY = INS["lay"]
ZT = LAY["zt"]
ZD = INS["zd"]
SCX, SCY = LAY["spin_c"]
SR = LAY["spin_r"]
PANEL = LAY["panel"]
# microammeter: frame face, window bottom, scale face, needle
YB = YF - 0.010
YDIAL = YF - 0.005
YD = YDIAL - 0.0003
YNEED = YD - 0.0012
PIVOT = (MX, WIN[2] - PIVOT_DZ)
# probe: rear end (cable) and the tip above the drum, bracket
PROBE_B = Vector((0.070, -0.145, ZT + 0.060))
PROBE_T = Vector((0.140, -0.055, ZT - 0.012))
PROBE_D = (PROBE_T - PROBE_B).normalized()
PROBE_L = (PROBE_T - PROBE_B).length
PROBE_C = PROBE_B + PROBE_D * (0.20 * PROBE_L)                 # bracket clamp
# unit cables: offsets from the middle, heights of the entries on the back
DET_CABLES = [(-0.06, 0.0045), (0.0, 0.0035), (0.06, 0.0040)]
BX = -0.17                                                     # bundle at the rear deck edge
# drain hose outside: down the crate and along the floor
PX, PY, PZ = INS["pump"]
HOSE_OUT = [(PX - 0.030, CY1 + 0.025, ZS + 0.017), (PX - 0.060, CY1 + 0.032, 0.075), (PX - 0.090, CY1 + 0.060, 0.019),
            (PX - 0.120, CY1 + 0.110, 0.0128), (PX - 0.130, CY1 + 0.140, 0.0128)]

LOD_SPECS = [
    dict(lod=0, bev=2, sides=24),
    dict(lod=1, bev=0, sides=12),
    dict(lod=2, bev=0, sides=8),
]

REGIONS = {
    # machine (m10_washer)
    "tt_body": ("enamel", 0.6), "tt_deck": ("enamel_deck", 0.7), "tt_panel": ("panel", 1.4), "tt_lid": ("lid", 0.8),
    "chrome": ("chrome", 1.0), "tt_knob": ("knob", 2.0), "black": ("black", 0.6), "tt_inner": ("inner", 0.2),
    "tt_tank": ("tank", 0.5), "tt_drum": ("drum", 0.9), "rubber": ("rubber", 0.5), "motor": ("motor", 0.6),
    "collar": ("collar", 1.0), "belt": ("rubber", 0.8), "spring": ("spring", 1.5), "hose": ("hose", 0.8),
    "cap_white": ("capacitor", 1.2), "jbox": ("jbox", 1.0), "dark": ("dark", 0.5),
    # crate
    "crate": ("crate", 0.6), "crate_front": ("crate_front", 0.9), "nail": ("nail", 2.0),
    # rotor with samples
    "rotor": ("rotor", 1.5), "can": ("can", 1.5), "cap": ("cap_red", 1.5), "label": ("label", 1.5),
    # detector unit, probe, dosimeter
    "det": ("det", 1.0), "det_side": ("det_side", 1.2), "det_panel": ("det_panel", 1.6), "bezel": ("bezel", 2.0),
    "dial": ("dial", 7.0), "needle": ("needle", 2.0), "lamp": ("lamp", 2.0), "lamp_g": ("lamp_g", 2.0),
    "steel": ("steel", 1.0), "tape": ("tape", 1.2), "cable": ("rubber", 0.5), "cable_grey": ("cable_grey", 0.5),
    "probe": ("probe", 1.5), "probe_band": ("chrome", 1.5), "dos": ("dos", 1.6), "dos_btn": ("dos_btn", 2.0),
    "plug": ("black", 1.2), "mark": ("label", 2.0),
}

# =============================================================================
# Materials
# =============================================================================


def decal(name, ax, sign, uv, center, size, face, eps=0.003):
    return (os.path.join(WORK, name), ax, sign, uv, center, size, (face - eps, face + eps))


def build_drum(mat, origin, center=(0.0, 0.0), r_wall=0.1, z_lo=0.0, z_hi=1.0, n_around=54, pitch_z=0.012,
               hole=0.27, seed=6.6, tone=0.50, gloss=0.6, spec=0.7, floor_z=0.0, dust=0.05, grime=0.25):
    """Centrifuge drum: stainless steel, brushing along the axis, the wall with holes - a grid in the
    cylinder unwrap (angle per radius, height), rows shifted by a half step, a whole number of holes
    around - no seam; the bottom, ribs and hub have no holes."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    if kmats.LOOK["name"] == "dayz":
        tone *= kmats.LOOK["steel"]
    brush = t.noise(t.stretch(vec, 1.0, 1.0, 0.02), 120.0, 4.0, 0.7)
    smudge = t.noise(vec, 3.5, 6.0, 0.6)
    v = t.math("ADD", tone, t.math("ADD", t.math("MULTIPLY", t.math("SUBTRACT", brush, 0.5), 0.10),
                                   t.math("MULTIPLY", t.math("SUBTRACT", smudge, 0.5), 0.12)))
    comb = t.node("ShaderNodeCombineColor")
    for i in range(3):
        t.link(v, comb.inputs[i])
    col = t.mixc(0.12, comb.outputs[0], (0.30, 0.31, 0.33, 1))
    dx = t.math("SUBTRACT", sep.outputs["X"], center[0])
    dy = t.math("SUBTRACT", sep.outputs["Y"], center[1])
    zz = t.math("DIVIDE", t.math("SUBTRACT", sep.outputs["Z"], z_lo), pitch_z)
    a = t.math("MULTIPLY", t.math("ARCTAN2", dy, dx), n_around / (2 * math.pi))
    a = t.math("ADD", a, t.math("FRACT", t.math("MULTIPLY", t.math("FLOOR", zz), 0.5)))
    da = t.math("SUBTRACT", t.math("FRACT", a), 0.5)
    db = t.math("SUBTRACT", t.math("FRACT", zz), 0.5)
    holes = t.math("LESS_THAN", t.math("ADD", t.math("MULTIPLY", da, da), t.math("MULTIPLY", db, db)), hole * hole)
    rad = t.math("SQRT", t.math("ADD", t.math("MULTIPLY", dx, dx), t.math("MULTIPLY", dy, dy)))
    wall = t.math("MULTIPLY", t.math("GREATER_THAN", rad, r_wall - 0.004),
                  t.math("LESS_THAN", t.math("ABSOLUTE", nsep.outputs["Z"]), 0.5))
    band = t.math("MULTIPLY", t.math("GREATER_THAN", sep.outputs["Z"], z_lo), t.math("LESS_THAN", sep.outputs["Z"], z_hi))
    holes = t.math("MULTIPLY", holes, t.math("MULTIPLY", wall, band))
    col = t.mixc(holes, col, (0.006, 0.006, 0.007, 1))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime, 0.45)
    gl = t.math("SUBTRACT", gloss, t.math("MULTIPLY", t.math("ADD", dirt, t.math("MULTIPLY", smudge, 0.3)), gloss * 0.6))
    s = t.math("SUBTRACT", spec, t.math("MULTIPLY", dirt, spec * 0.6))
    gl = t.mixf(holes, gl, 0.0)
    s = t.mixf(holes, s, 0.0)
    h = t.math("SUBTRACT", t.math("MULTIPLY", brush, 0.08), holes)
    return kmats.out(t, col, gl, s, h)


KINDS = kmats.std_kinds(floor_z=ZS)
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# white enamel of an old machine: chips down to dark metal, rust at the bottom and along the edges
# (Clear Sky: dirt and rust on the bodies of old equipment)
WHITE = dict(color=kmats.lin((222, 216, 198)), under=kmats.lin((66, 64, 62)), seed=2.4, gloss=0.50, spec=0.40,
             chip=(0.56, 0.62), rust=(0.56, 0.64), rust_low=1.0, floor_z=ZS, dust=0.40, grime=0.95, yellow=0.55)
# light blue Clear Sky paint over the factory white: the panel and lids (a changeable colour)
BLUE = dict(color=kmats.lin((150, 192, 214)), under=kmats.lin((222, 220, 210)), seed=3.3, gloss=0.42, spec=0.32,
            chip=(0.60, 0.66), rust=(0.70, 0.78), rust_low=0.0, floor_z=ZS, dust=0.25, grime=0.3)
PANEL_C = ((PANEL[0] + PANEL[1]) / 2, (PANEL[2] + PANEL[3]) / 2)
PANEL_S = (PANEL[1] - PANEL[0], PANEL[3] - PANEL[2])
WOOD = dict(color=kmats.lin((132, 104, 72)), seed=4.4, along="x", floor_z=0.0, dust=0.45, grime=0.9, knots=0.6)
DIAL_C = ((WIN[0] + WIN[1]) / 2, (WIN[2] + WIN[3]) / 2)
# detector unit: a steel box in grey hammer enamel, the front panel is light aluminium with signs; the
# instrument and the workplace are clean
DET = dict(color=kmats.lin((92, 100, 106)), under=kmats.lin((170, 172, 170)), seed=7.1, gloss=0.35, spec=0.3,
           chip=(0.66, 0.72), rust=(0.99, 1.0), rust_low=0.0, dust=0.18, grime=0.15)
PLATE_C = ((PLATE[0] + PLATE[1]) / 2, (PLATE[2] + PLATE[3]) / 2)
PLATE_S = (PLATE[1] - PLATE[0], PLATE[3] - PLATE[2])
KINDS.update({
    "enamel": ("paint", WHITE),
    "enamel_deck": ("paint", dict(WHITE, seed=2.9, rust_low=0.0, dust=0.45, grime=0.4)),
    "panel": ("paint", dict(BLUE, decal_items=[decal("decal_panel.png", "y", -1, ("x", "z"), PANEL_C, PANEL_S,
                                                     LAY["panel_y"])])),
    "lid": ("paint", dict(BLUE, seed=3.8)),
    "chrome": ("steel", dict(seed=6.1, tone=0.60, along="x", gloss=0.75, spec=0.85, floor_z=ZS, dust=0.2, grime=0.4)),
    "knob": ("plastic", dict(color=kmats.lin((226, 218, 196)), gloss=0.45, spec=0.35, dust=0.15, grime=0.3,
                             scuff=(0.66, 0.74))),
    "inner": ("flat", dict(color=kmats.lin((26, 26, 27)), gloss=0.15, spec=0.08)),
    # tank and centrifuge casing: grey enamel, dirt and rust streaks
    "tank": ("paint", dict(color=kmats.lin((168, 170, 164)), under=kmats.lin((60, 58, 56)), seed=5.2, gloss=0.35,
                           spec=0.3, chip=(0.56, 0.62), rust=(0.56, 0.64), rust_low=1.0, floor_z=ZS, dust=0.2,
                           grime=0.8)),
    "drum": (build_drum, dict(center=(SCX, SCY), r_wall=SR - 0.016, z_lo=ZD - 0.37, z_hi=ZT - 0.062, seed=6.6,
                              tone=0.50, gloss=0.6, spec=0.7, floor_z=ZS, dust=0.05, grime=0.25)),
    "motor": ("paint", dict(color=kmats.lin((58, 64, 72)), under=kmats.lin((40, 40, 40)), seed=5.8, gloss=0.3,
                            spec=0.25, chip=(0.6, 0.66), rust=(0.6, 0.68), rust_low=1.0, floor_z=ZS, dust=0.4,
                            grime=0.8)),
    "collar": ("plastic", dict(color=kmats.lin((214, 210, 198)), gloss=0.35, spec=0.25, dust=0.3, grime=0.5,
                               scuff=(0.66, 0.74))),
    "spring": ("steel", dict(seed=7.3, tone=0.22, along="z", gloss=0.45, spec=0.5, floor_z=ZS, dust=0.4, grime=0.8)),
    "hose": ("plastic", dict(color=kmats.lin((64, 66, 68)), gloss=0.2, spec=0.12, dust=0.45, grime=0.7,
                             scuff=(0.75, 0.85))),
    "capacitor": ("plastic", dict(color=kmats.lin((176, 178, 170)), gloss=0.35, spec=0.25, dust=0.4, grime=0.5)),
    "jbox": ("plastic", dict(color=kmats.lin((112, 116, 118)), gloss=0.3, spec=0.2, dust=0.4, grime=0.5)),
    "dark": ("flat", dict(color=kmats.lin((14, 14, 15)), gloss=0.1, spec=0.05)),
    "crate": (kwood.build_wood, WOOD),
    "crate_front": (kwood.build_wood, dict(WOOD, decal_items=[decal("decal_stripes.png", "y", -1, ("x", "z"),
                                                                    (0.0, 0.062), (0.46, 0.090), CY0)])),
    "nail": ("steel", dict(seed=8.8, tone=0.16, along="z", gloss=0.4, spec=0.4, dust=0.3, grime=0.6)),
    "rotor": ("steel", dict(seed=6.9, tone=0.45, along="x", gloss=0.6, spec=0.7, floor_z=ZS, dust=0.05, grime=0.3)),
    "can": ("steel", dict(seed=8.4, tone=0.62, along="z", gloss=0.5, spec=0.6, dust=0.05, grime=0.1)),
    "label": ("plastic", dict(color=kmats.lin((226, 222, 206)), gloss=0.2, spec=0.1, mottle=0.08, dust=0.1, grime=0.2)),
    "det": ("paint", DET),
    "det_side": ("paint", dict(DET, decal_items=[decal("decal_bolt.png", "x", 1, ("y", "z"),
                                                       ((DY0 + DY1) / 2, DZ0 + 0.068), (0.075, 0.075), DX1)])),
    "det_panel": ("paint", dict(color=kmats.lin((168, 170, 166)), under=kmats.lin((120, 122, 120)), seed=7.7,
                                gloss=0.4, spec=0.35, chip=(0.70, 0.78), rust=(0.99, 1.0), rust_low=0.0, dust=0.12,
                                grime=0.1, decal_items=[decal("decal_detpanel.png", "y", -1, ("x", "z"), PLATE_C,
                                                              PLATE_S, YF)])),
    "bezel": ("plastic", dict(color=kmats.lin((22, 21, 20)), gloss=0.5, spec=0.4, dust=0.05, scuff=(0.8, 0.9))),
    # instrument scale: "off" (the main atlas) and "work" (backlight; atlas _on)
    "dial": ("paint", dict(CLEAN, color=kmats.lin((196, 192, 176)), gloss=0.6, spec=0.4,
                           decal_items=[decal("decal_dial_off.png", "y", -1, ("x", "z"), DIAL_C, (DIAL_W, DIAL_H), YD)])),
    "dial_on": ("paint", dict(CLEAN, color=kmats.lin((252, 238, 196)), gloss=0.6, spec=0.4,
                              decal_items=[decal("decal_dial_on.png", "y", -1, ("x", "z"), DIAL_C, (DIAL_W, DIAL_H), YD)])),
    "needle": ("flat", dict(color=kmats.lin((24, 24, 24)), gloss=0.4, spec=0.3)),
    "lamp": ("flat", dict(color=kmats.lin((86, 22, 16)), gloss=0.85, spec=0.8)),
    "lamp_on": ("flat", dict(color=kmats.lin((255, 70, 40)), gloss=0.85, spec=0.8)),
    "lamp_g": ("flat", dict(color=kmats.lin((26, 64, 30)), gloss=0.85, spec=0.8)),
    "lamp_g_on": ("flat", dict(color=kmats.lin((90, 255, 110)), gloss=0.85, spec=0.8)),
    "tape": ("plastic", dict(color=kmats.lin((38, 62, 128)), gloss=0.5, spec=0.35, dust=0.2, grime=0.2, scuff=(0.7, 0.8))),
    "cable_grey": ("plastic", dict(color=kmats.lin((120, 122, 120)), gloss=0.2, spec=0.1, dust=0.4, grime=0.6)),
    # probe: a tube in dark enamel, worn to aluminium on the edges
    "probe": ("paint", dict(color=kmats.lin((70, 76, 80)), under=kmats.lin((150, 150, 148)), seed=9.1, gloss=0.35,
                            spec=0.3, chip=(0.62, 0.70), rust=(0.99, 1.0), rust_low=0.0, dust=0.15, grime=0.3)),
    # dosimeter: dark plastic, signs on top (decal_dos)
    "dos": ("paint", dict(color=kmats.lin((54, 52, 48)), under=kmats.lin((96, 94, 90)), seed=9.4, gloss=0.35, spec=0.3,
                          chip=(0.72, 0.80), rust=(0.99, 1.0), rust_low=0.0, dust=0.12, grime=0.2,
                          decal_items=[decal("decal_dos.png", "z", 1, ("x", "y"), (DOS[0], DOS[1]), (DOS[2], DOS[3]),
                                             DOS_TOP)])),
    "dos_btn": ("plastic", dict(color=kmats.lin((36, 36, 36)), gloss=0.35, spec=0.25, dust=0.1, scuff=(0.7, 0.8))),
})

OBJ, NAME = "m10_sky_proc_anom", "ozr_sky_proc_anom"
# Work look: the instrument scale and the "power" lamp are ozl_screen, the "count" lamp is
# ozl_lamp_work, the dosimeter display is ozl_lcd (own texture, frames) - all three in
# hiddenSelections; "off" by default. The drum is the bone ozl_drum on ozl_work (loop), the needle is
# the bone ozl_meter on its own source (wobble), the "spin" knob and the toggle are the bones ozl_knob
# and ozl_toggle on ozl_pose (the "work" pose).
SEL_SCREEN, SEL_LAMP, SEL_LCD = "ozl_screen", "ozl_lamp_work", "ozl_lcd"
SEL_DRUM, SEL_METER, SEL_KNOB, SEL_TOGGLE = "ozl_drum", "ozl_meter", "ozl_knob", "ozl_toggle"
DRUM_TURNS = 6                                       # turns per loop pass (2 s) - 3 rev/s
METER_SPAN = math.pi / 2                             # M42100 scale - 90 degrees
METER_REST = 135.0                                   # needle at zero - left end of the scale (make_decals: 135 -> 45)
METER_TIP = ARC_R * 1.08                             # needle length from the axis
METER_MID, METER_AMP = 0.62, 0.07                    # needle in "work": wobble mid +- amp
KNOB_TURN = math.radians(105.0)                      # the "spin" knob 0 -> 3 (make_decals scale: 100 -> -15 degrees)
TOGGLE_TURN = math.radians(50.0)                     # toggle lever: down 25 -> up 25 degrees
TOGGLE_PIVOT = (TOGGLE[0], YF - 0.009, TOGGLE[1])
KNOB_MID = LAY["knobs"][1]
# The axes of the needle, "spin" knob and toggle bones are memory points (collision below). The engine
# rotates a bone right-handed in DayZ axes (kexport.conv, determinant -1); in Blender axes that is a
# left-handed rotation about the axis from the first point to the second: the axis looks at the
# person, a positive angle goes clockwise for them (as in M08, M12, M14, M33 - their needles are right
# in game). Axes pointing from the face into the machine (the toggle axis pointing left) make the
# needle go counter-clockwise, past zero and off the scale, the knob miss its digits and the lever go
# down.
AXES = {
    "ozl_meter_axis": [(PIVOT[0], YNEED, PIVOT[1]), (PIVOT[0], YNEED - 0.05, PIVOT[1])],
    "ozl_knob_axis": [(KNOB_MID[0], LAY["panel_y"], KNOB_MID[1]), (KNOB_MID[0], LAY["panel_y"] - 0.05, KNOB_MID[1])],
    "ozl_toggle_axis": [TOGGLE_PIVOT, (TOGGLE_PIVOT[0] + 0.05, TOGGLE_PIVOT[1], TOGGLE_PIVOT[2])],
}


def engine_turn(axis, ang):
    """Rotation of a bone by angle ang as the engine does it about the memory axis axis: (point on the
    axis, Blender axis for Matrix.Rotation - right-handed, angle). The Blender axis is opposite to the
    memory axis (from the second point to the first)."""
    a, b = (Vector(q) for q in AXES[axis])
    return tuple(a), tuple(a - b), ang


# preview of the "work" look: the needle, knob and toggle in the work pose - by the engine rotation
# (engine_turn, the _posed wrapper below), so the preview shows what will be in game; it does not go
# into the p3d
ON_MOVE = {}
POSE_ON = {
    SEL_METER: engine_turn("ozl_meter_axis", METER_MID * METER_SPAN),
    SEL_KNOB: engine_turn("ozl_knob_axis", KNOB_TURN),
    SEL_TOGGLE: engine_turn("ozl_toggle_axis", TOGGLE_TURN),
}


def check_turns():
    """Numeric check, like check_axes of the Storage boxes: the engine rotation at phases 0, mid +- amp and
    1 moves the needle along the scale clockwise (from the front 135 -> 45 degrees), the tip stays in
    the scale window; the "spin" knob goes from 0 to 3 clockwise, the toggle lever goes up. If it does
    not hold, the build fails."""
    def turn(axis, ang, p):
        c, ax, _ = engine_turn(axis, ang)
        return Vector(c) + Matrix.Rotation(ang, 3, Vector(ax)) @ (Vector(p) - Vector(c))
    c = Vector(AXES["ozl_meter_axis"][0])
    a = math.radians(METER_REST)
    tip = c + Vector((math.cos(a), 0.0, math.sin(a))) * METER_TIP
    seen = []
    for ph in (0.0, METER_MID - METER_AMP, METER_MID, METER_MID + METER_AMP, 1.0):
        q = turn("ozl_meter_axis", ph * METER_SPAN, tip)
        deg = math.degrees(math.atan2(q.z - c.z, q.x - c.x))
        assert abs(deg - (METER_REST - math.degrees(METER_SPAN) * ph)) < 0.01, "needle goes the wrong way: %.1f" % deg
        assert WIN[0] < q.x < WIN[1] and WIN[2] < q.z < WIN[3], "needle tip outside the scale window: phase %.2f" % ph
        seen.append("%.2f -> %.1f" % (ph, deg))
    k = Vector(AXES["ozl_knob_axis"][0])
    q = turn("ozl_knob_axis", KNOB_TURN, k + Vector((math.cos(math.radians(100.0)), 0.0, math.sin(math.radians(100.0)))))
    assert abs(math.degrees(math.atan2(q.z - k.z, q.x - k.x)) - (100.0 - 105.0)) < 0.01, "the spin knob goes the wrong way"
    t = Vector(TOGGLE_PIVOT)
    q = turn("ozl_toggle_axis", TOGGLE_TURN, t + Vector((0.0, -math.cos(math.radians(25.0)), -math.sin(math.radians(25.0)))))
    assert q.z > t.z + 0.3 and q.y < t.y, "the toggle lever does not go up"
    print("turns ok: needle (phase -> degrees from the front) " + ", ".join(seen) + "; knob 0 -> 3, toggle up")


check_turns()
ON = dict(remap={"dial": "dial_on", "lamp": "lamp_on", "lamp_g": "lamp_g_on"}, emissive=(1.0, 1.0, 1.0, 1.0),
          move=ON_MOVE)
DRUM_ANIM = ("ozl_drum_spin", dict(type="rotation", source="ozl_work", sourceAddress="loop", selection=SEL_DRUM,
                                   axis="ozl_drum_axis", memory=1, minValue=0.0, maxValue=1.0 / DRUM_TURNS,
                                   angle0=0.0, angle1=2 * math.pi))
METER_ANIM = ("ozl_meter_needle", dict(type="rotation", source="ozl_meter", selection=SEL_METER, axis="ozl_meter_axis",
                                       memory=1, minValue=0.0, maxValue=1.0, angle0=0.0, angle1=METER_SPAN))
KNOB_ANIM = ("ozl_knob_turn", dict(type="rotation", source="ozl_pose", selection=SEL_KNOB, axis="ozl_knob_axis",
                                   memory=1, minValue=0.0, maxValue=1.0, angle0=0.0, angle1=KNOB_TURN))
TOGGLE_ANIM = ("ozl_toggle_flip", dict(type="rotation", source="ozl_pose", selection=SEL_TOGGLE,
                                       axis="ozl_toggle_axis", memory=1, minValue=0.0, maxValue=1.0, angle0=0.0,
                                       angle1=TOGGLE_TURN))
LCD_PANEL = dict(off="lcd_off.png", frames=["lcd_f%02d.png" % i for i in range(8)], size=256, gloss=0.5)

# vanilla DayZ items through proxies: a sheet on the centrifuge lid, a pen on the unit, Krona batteries
# on the tank lid, on the floor an electrician kit with pliers, a screwdriver, tape, a rag by the drain hose
LID_FR = kwasher.lid_frame(LAY["hinge_y"], ZT + 0.004, 100.0)
PAPER_AT = LID_FR.p((LAY["spin"][0] + LAY["spin"][1]) / 2, 0.165, W.LID_T)
DECOR = [
    kv.put("paper", tuple(PAPER_AT), up=tuple(LID_FR.v), fwd=tuple(LID_FR.n), normal=tuple(LID_FR.n), lift=0.0006),
    kv.put("pen", (DX0 + 0.095, -0.0785, DZ1), **kv.flat(183)),
    kv.put("battery9v", (-0.287, 0.096, DZF), up=(0, 0, 1), fwd=(0.3, -1, 0)),
    kv.put("battery9v", (-0.255, 0.100, DZF), **kv.flat(20)),
    kv.put("electrickit", (0.475, -0.085, 0.0), **kv.flat(88)),
    kv.put("pliers", (0.475, -0.090, kv.box("electrickit")[1][2] - kv.box("electrickit")[0][2]), **kv.flat(75)),
    kv.put("screwdriver", (0.43, -0.29, 0.0), **kv.flat(8)),
    kv.put("ducttape", (-0.47, -0.10, 0.0), **kv.flat(90)),
    kv.put("rags", (-0.31, 0.37, 0.0), **kv.flat(15)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.82, 0.86, 0.88), clear=0.05, edge=0.10, smudge=0.06, streaks=0.03),
                 selections=(SEL_SCREEN, SEL_LAMP, SEL_LCD, SEL_DRUM, SEL_METER, SEL_KNOB, SEL_TOGGLE),
                 hidden=(SEL_SCREEN, SEL_LAMP, SEL_LCD), states={"on": ON},
                 bones=((SEL_DRUM, ""), (SEL_METER, ""), (SEL_KNOB, ""), (SEL_TOGGLE, "")),
                 animations=(DRUM_ANIM, METER_ANIM, KNOB_ANIM, TOGGLE_ANIM), decor=DECOR, panels={"lcd": LCD_PANEL},
                 sources={"ozl_work": dict(animPeriod=2.0), "ozl_meter": dict(animPeriod=0.2),
                          "ozl_pose": dict(animPeriod=0.5)})
P = M.part
BOUNDS = {}


def _posed(place):
    """Preview of the "work" look: the parts of the POSE_ON groups are in the work pose (rotation about the
    bone axis). kmodel can only translate (move), so the rotation is here, by a wrapper over krender; it
    does not go into the p3d - there the animations are in model.cfg."""
    def wrapped(parts, *a, **kw):
        obs = place(parts, *a, **kw)
        if kw.get("move") is ON_MOVE:
            for p, ob in zip(parts, obs):
                if p.group in POSE_ON:
                    c, ax, ang = POSE_ON[p.group]
                    loc = Vector(ob.location)
                    c = Vector(c) + loc
                    ob.matrix_world = (Matrix.Translation(c) @ Matrix.Rotation(ang, 4, Vector(ax)) @
                                       Matrix.Translation(-c) @ Matrix.Translation(loc))
        return obs
    return wrapped


krender.place_look = _posed(krender.place_look)
krender.place = _posed(krender.place)


# =============================================================================
# Crate stand
# =============================================================================
def build_crate(spec):
    """Low plank crate: two boards per side with a gap, a lid of five boards, corner blocks, end battens,
    nails. Far LOD - a box."""
    lod = spec["lod"]
    if lod == 2:
        b = P("crate", "crate")
        g.box(b, CX0, CX1, CY0, CY1, 0.0, ZS)
        return [b]
    zu = ZS - BOARD
    rows = [(0.012, 0.060), (0.064, zu)] if lod == 0 else [(0.012, zu)]
    fr = P("crate_front", "crate_front")
    sd = P("crate_boards", "crate")
    for za, zb in rows:
        g.box(fr, CX0, CX1, CY0, CY0 + BOARD, za, zb, **(dict(r=0.002, seg=1) if lod == 0 else {}))
        g.box(sd, CX0, CX1, CY1 - BOARD, CY1, za, zb)
        for xa, xb in ((CX0, CX0 + BOARD), (CX1 - BOARD, CX1)):
            g.box(sd, xa, xb, CY0 + BOARD, CY1 - BOARD, za, zb)
    n = 5 if lod == 0 else 1
    gap = 0.008 if lod == 0 else 0.0
    tw = ((CY1 - CY0) - gap * (n - 1)) / n
    for j in range(n):
        ya = CY0 + j * (tw + gap)
        g.box(sd, CX0, CX1, ya, ya + tw, zu, ZS)
    parts = [fr, sd]
    bl = P("crate_blocks", "crate")
    for x in (CX0 + 0.01, CX1 - 0.07):
        for y in (CY0 + 0.01, CY1 - 0.07):
            g.box(bl, x, x + 0.06, y, y + 0.06, 0.0, zu)
    parts.append(bl)
    if lod == 0:
        # end battens, darkness inside, nails at the board ends
        for s in (-1, 1):
            xa, xb = sorted((s * CX1, s * (CX1 + 0.012)))
            for yc in (-0.12, 0.12):
                g.box(sd, xa, xb, yc - 0.025, yc + 0.025, 0.014, zu - 0.004)
        core = P("crate_core", "tt_inner")
        g.box(core, CX0 + BOARD, CX1 - BOARD, CY0 + BOARD, CY1 - BOARD, 0.012, zu)
        nl = P("crate_nails", "nail")
        for za, zb in rows:
            zm = (za + zb) / 2
            for x in (CX0 + 0.009, CX1 - 0.009):
                g.cyl(nl, (x, CY0 - 0.0004, zm), "y", 0.0028, 0.0012, 4)
                g.cyl(nl, (x, CY1 + 0.0004, zm), "y", 0.0028, 0.0012, 4)
            for s in (-1, 1):
                for y in (CY0 + 0.040, CY1 - 0.040):
                    g.cyl(nl, (s * (CX1 + 0.0004), y, zm), "x", 0.0028, 0.0012, 4)
        parts += [core, nl]
    return parts


# =============================================================================
# Centrifuge: rotor with sample containers in the drum (bone ozl_drum)
# =============================================================================
def build_samples(spec):
    """Rotor with samples: a post from the hub, a disc with a nut, three arms, ring sockets at the ends, in
    them aluminium cups with a rolled rim, knurled red caps and blank tags. It is raised toward the
    opening: the samples are visible through the open lid, and the rotation is visible on them."""
    lod = spec["lod"]
    if lod == 2:
        return []
    za = ZD - 0.125                                            # crosspiece
    hub = ZD - 0.371
    rt = P("drum_rotor", "rotor", group=SEL_DRUM)
    cn = P("drum_cans", "can", group=SEL_DRUM)
    parts = [rt, cn]
    fz = frame_at((SCX, SCY, 0.0), "z")
    if lod == 0:
        lathe(rt, [(0.0, hub), (0.016, hub), (0.011, hub + 0.018), (0.011, za - 0.006), (0.0, za - 0.006)], 8, fz)
        lathe(rt, [(0.0, za - 0.006), (0.0245, za - 0.006), (0.0245, za + 0.006), (0.0, za + 0.006)], 12, fz)
        g.prism(rt, [(SCX + px, SCY + py) for px, py in hexagon(0.0125)], (0, 1), za + 0.006, za + 0.016)
    else:
        g.cyl(rt, (SCX, SCY, (hub + za) / 2), "z", 0.011, za - hub, 6)
        g.cyl(rt, (SCX, SCY, za), "z", 0.024, 0.012, 8)
    caps = P("drum_caps", "cap", group=SEL_DRUM) if lod == 0 else None
    labels = P("drum_labels", "label", group=SEL_DRUM) if lod == 0 else None
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.3 + math.pi / 3
        ca, sa = math.cos(a), math.sin(a)
        cx, cy = SCX + 0.062 * ca, SCY + 0.062 * sa
        fc = frame_at((cx, cy, 0.0), "z")
        box_to(rt, (SCX + 0.018 * ca, SCY + 0.018 * sa, za), (SCX + 0.040 * ca, SCY + 0.040 * sa, za), 0.012, 0.010)
        if lod == 0:
            lathe(rt, [(0.0235, za - 0.010), (0.0285, za - 0.010), (0.0285, za + 0.010), (0.0235, za + 0.010)], 8, fc,
                  closed=True)
            lathe(cn, [(0.0, za - 0.084), (0.019, za - 0.084), (0.0222, za - 0.077), (0.0222, za + 0.012),
                       (0.0205, za + 0.016), (0.0, za + 0.016)], 10, fc)
            g.prism(caps, [(cx + px, cy + py) for px, py in knurl_poly(0.0236, 9, 0.0012)], (0, 1), za + 0.014,
                    za + 0.031)
            lathe(labels, [(0.0221, za - 0.060), (0.0228, za - 0.060), (0.0228, za - 0.028), (0.0221, za - 0.028)], 8,
                  fc, closed=True)
        else:
            g.cyl(cn, (cx, cy, za - 0.030), "z", 0.0225, 0.10, 6)
    if caps is not None:
        parts += [caps, labels]
    return parts


# =============================================================================
# Detector unit
# =============================================================================
def build_detector(spec):
    lod = spec["lod"]
    parts = []
    bx = P("det_box", "det")
    g.box(bx, DX0, DX1 - 0.002, DY0, DY1, DZ0, DZ1,
          **(dict(r=0.005, seg=2) if lod == 0 else dict(r=0.004, seg=1) if lod == 1 else {}))
    side = P("det_side", "det_side")
    g.box(side, DX1 - 0.002, DX1, DY0 + 0.007, DY1 - 0.007, DZ0 + 0.007, DZ1 - 0.007)
    parts += [bx, side]
    # front panel on screws (the signs are the decal_detpanel decal)
    fp = P("det_plate", "det_panel")
    g.box(fp, PLATE[0], PLATE[1], YF, DY0 + 0.0005, PLATE[2], PLATE[3], **(dict(r=0.001, seg=1) if lod == 0 else {}))
    parts.append(fp)
    if lod == 0:
        ft = P("det_feet", "rubber")
        for fx in (DX0 + 0.020, DX1 - 0.020):
            for fy in (DY0 + 0.020, DY1 - 0.020):
                g.cyl(ft, (fx, fy, (DZF + DZ0) / 2 + 0.0005), "z", 0.008, DZ0 - DZF + 0.001, 6)
        parts.append(ft)
        st = P("det_screws", "steel")
        for x in (PLATE[0] + 0.006, PLATE[1] - 0.006):
            for z in (PLATE[2] + 0.006, PLATE[3] - 0.006):
                screw(st, (x, YF, z), "-y", 0.0028)
        parts.append(st)

    # microammeter: a frame with a window (boolean difference), the scale (ozl_screen), glass, the needle
    # (ozl_meter), the zero corrector screw
    bz = P("meter_bezel", "bezel")
    if lod == 0:
        g.box(bz, MX - 0.040, MX + 0.040, YB, YF + 0.0005, MZ - 0.040, MZ + 0.040, r=0.004, seg=2)
        cut = P("meter_cut", "bezel")
        g.box(cut, WIN[0], WIN[1], YB - 0.01, YDIAL, WIN[2], WIN[3])
        bz = M.boolean("meter_bezel", bz, [cut])
    elif lod == 1:
        h = 0.040
        g.box(bz, MX - h, MX + h, YB, YF, WIN[3], MZ + h)
        g.box(bz, MX - h, MX + h, YB, YF, MZ - h, WIN[2])
        g.box(bz, MX - h, WIN[0], YB, YF, WIN[2], WIN[3])
        g.box(bz, WIN[1], MX + h, YB, YF, WIN[2], WIN[3])
        g.box(bz, WIN[0], WIN[1], YDIAL, YF, WIN[2], WIN[3])
    else:
        g.box(bz, MX - 0.040, MX + 0.040, YD + 0.0006, YF, MZ - 0.040, MZ + 0.040)
    parts.append(bz)
    dl = P("meter_dial", "dial", group=SEL_SCREEN)
    g.box(dl, WIN[0], WIN[1], YD, YD + 0.0008, WIN[2], WIN[3])
    parts.append(dl)
    if lod == 0:
        gl = P("meter_glass", "steel", section="glass")
        g.box(gl, WIN[0], WIN[1], YB + 0.0015, YB + 0.0025, WIN[2], WIN[3])
        parts.append(gl)
        zs = P("meter_zero", "bezel")
        zz = (MZ - 0.040 + WIN[2]) / 2
        lathe(zs, [(0.0, 0.0), (0.0042, 0.0), (0.0034, 0.0020), (0.0, 0.0022)], 8, frame_at((MX, YB, zz), "-y"))
        sl = P("meter_zero_slot", "dark")
        g.box(sl, MX - 0.0030, MX + 0.0030, YB - 0.0024, YB - 0.0016, zz - 0.0005, zz + 0.0005)
        parts += [zs, sl]
    nd = P("meter_needle", "needle", group=SEL_METER)
    a = math.radians(METER_REST)                   # at zero - the left end of the scale
    fr = g.Frame((PIVOT[0], YNEED, PIVOT[1]), (math.cos(a), 0.0, math.sin(a)), (-math.sin(a), 0.0, math.cos(a)),
                 (0, -1, 0))
    tip = METER_TIP
    blade = [(-0.008, -0.0012), (0.004, -0.0009), (tip, -0.00025), (tip + 0.001, 0.0), (tip, 0.00025),
             (0.004, 0.0009), (-0.008, 0.0012)] if lod == 0 else [(0.006, -0.0007), (tip, -0.0007), (tip, 0.0007),
                                                                  (0.006, 0.0007)]
    g.prism(nd, blade, (0, 1), -0.0004, 0.0004, frame=fr)
    parts.append(nd)

    # lamps "power" (green, ozl_screen - lit in work) and "count" (red, ozl_lamp_work - blinks) in chrome bezels
    for (lx, lz), grp, reg in ((LAMP_G, SEL_SCREEN, "lamp_g"), (LAMP_R, SEL_LAMP, "lamp")):
        lens = P("det_lens_" + reg, reg, group=grp)
        if lod == 0:
            lathe(lens, [(0.0, -0.001), (0.0068, -0.001), (0.0068, 0.0015), (0.0056, 0.0045), (0.0032, 0.0062),
                         (0.0, 0.0068)], 8, frame_at((lx, YF - 0.006, lz), "-y"))
        else:
            g.cyl(lens, (lx, YF - 0.007, lz), "y", 0.0068, 0.010, (8, 6)[lod - 1])
        parts.append(lens)
        if lod < 2:
            rg = P("det_ring_" + reg, "chrome")
            if lod == 0:
                lathe(rg, [(0.0066, 0.0), (0.0105, 0.0), (0.0105, 0.004), (0.0094, 0.0063), (0.0066, 0.0063)], 8,
                      frame_at((lx, YF, lz), "-y"), closed=True)
            else:
                g.cyl(rg, (lx, YF - 0.003, lz), "y", 0.0105, 0.006, 8)
            parts.append(rg)

    if lod < 2:
        # toggle: a bushing with a nut; the lever (ozl_toggle) is down, up in work
        tx, tz = TOGGLE
        tb = P("det_toggle", "chrome")
        lathe(tb, [(0.0, 0.0), (0.0058, 0.0), (0.0058, 0.009), (0.0, 0.009)], (8, 6)[lod], frame_at((tx, YF, tz), "-y"))
        if lod == 0:
            g.prism(tb, [(tx + px, tz + pz) for px, pz in hexagon(0.0080)], (0, 2), YF - 0.0035, YF)
        parts.append(tb)
        lv = P("det_toggle_lever", "chrome", group=SEL_TOGGLE)
        d = Vector((0.0, -math.cos(math.radians(25.0)), -math.sin(math.radians(25.0))))
        if lod == 0:
            lathe(lv, [(0.0, -0.001), (0.0026, -0.001), (0.0018, 0.010), (0.0021, 0.017), (0.0026, 0.0195),
                       (0.0018, 0.0225), (0.0, 0.0235)], 6, frame_axis(TOGGLE_PIVOT, d))
        else:
            g.pipe(lv, [TOGGLE_PIVOT, tuple(Vector(TOGGLE_PIVOT) + d * 0.022)], 0.0022, 4)
        parts.append(lv)
        # sensitivity knob: a skirt with a mark, a knurled cap
        kx_, kz_ = KNOB
        kb = P("det_knob", "bezel")
        if lod == 0:
            lathe(kb, [(0.0, 0.0), (0.0175, 0.0), (0.0175, 0.003), (0.0145, 0.005), (0.0, 0.005)], 16,
                  frame_at((kx_, YF, kz_), "-y"))
            g.prism(kb, [(kx_ + px, kz_ + pz) for px, pz in knurl_poly(0.0125, 12, 0.0010)], (0, 2), YF - 0.019,
                    YF - 0.004)
            mk = P("det_knob_mark", "mark")
            g.box(mk, kx_ - 0.0007, kx_ + 0.0007, YF - 0.0053, YF - 0.0047, kz_ + 0.0128, kz_ + 0.0143)
            parts.append(mk)
        else:
            g.cyl(kb, (kx_, YF - 0.009, kz_), "y", 0.0150, 0.018, 8)
        parts.append(kb)
        # probe socket (SR-50) and the probe cable plug
        bnx, bnz = BNC
        bn = P("det_bnc", "chrome")
        if lod == 0:
            lathe(bn, [(0.0, 0.0), (0.0085, 0.0), (0.0085, 0.0022), (0.0062, 0.0022), (0.0062, 0.010), (0.0, 0.010)], 8,
                  frame_at((bnx, YF, bnz), "-y"))
            lathe(bn, [(0.0, 0.0), (0.0072, 0.0), (0.0072, 0.010), (0.0060, 0.018), (0.0, 0.026)], 8,
                  frame_at((bnx, YF - 0.010, bnz), "-y"))
        else:
            g.cyl(bn, (bnx, YF - 0.018, bnz), "y", 0.0075, 0.036, 6)
        parts.append(bn)
        # antenna from a receiver: a hinge on the roof at the back right, four sections with couplings, a ball
        an = P("det_antenna", "chrome")
        base = Vector((DX1 - 0.025, DY1 - 0.022, DZ1))
        if lod == 0:
            lathe(an, [(0.0, 0.0), (0.011, 0.0), (0.011, 0.004), (0.0075, 0.008), (0.0065, 0.016), (0.0, 0.018)], 10,
                  frame_at(tuple(base), "z"))
        else:
            g.box(an, base.x - 0.010, base.x + 0.010, base.y - 0.010, base.y + 0.010, DZ1, DZ1 + 0.014)
        d = Vector((0.22, 0.30, 1.0)).normalized()
        p = base + Vector((0, 0, 0.016))
        for rr in (0.0048, 0.0039, 0.0031, 0.0024)[:4 if lod == 0 else 1]:
            ln = 0.12 if lod == 0 else 0.46
            g.pipe(an, [tuple(p), tuple(p + d * ln)], rr, 6 if lod == 0 else 4)
            if lod == 0:
                lathe(an, [(0.0, -0.003), (rr + 0.0009, -0.003), (rr + 0.0009, 0.003), (0.0, 0.003)], 6,
                      frame_axis(tuple(p + d * (ln - 0.0035)), d))
            p = p + d * (ln - 0.004)
        if lod == 0:
            lathe(an, [(0.0, -0.004), (0.0042, -0.002), (0.0042, 0.002), (0.0, 0.004)], 6, frame_axis(tuple(p + d * 0.004), d))
        parts.append(an)
    if lod == 0:
        # handle on the left side, ventilation slots under it
        hd = P("det_handle", "chrome")
        zh = DZ0 + 0.088
        for y in (-0.052, 0.022):
            g.box(hd, DX0 - 0.010, DX0 + 0.001, y - 0.007, y + 0.007, zh - 0.009, zh + 0.009)
        g.pipe(hd, spline([(DX0 - 0.006, -0.052, zh), (DX0 - 0.019, -0.049, zh), (DX0 - 0.023, -0.036, zh),
                           (DX0 - 0.023, 0.006, zh), (DX0 - 0.019, 0.019, zh), (DX0 - 0.006, 0.022, zh)], 2), 0.0042, 6)
        parts.append(hd)
        vt = P("det_vents", "dark")
        for k in range(7):
            y = -0.066 + 0.017 * k
            g.box(vt, DX0 - 0.0004, DX0 + 0.001, y - 0.0022, y + 0.0022, DZ0 + 0.020, DZ0 + 0.058)
        parts.append(vt)
        # cable glands on the back
        gd = P("det_glands", "black")
        for i, (dx, _) in enumerate(DET_CABLES):
            lathe(gd, [(0.0, 0.0), (0.0078, 0.0), (0.0078, 0.005), (0.0056, 0.016), (0.0, 0.016)], 6,
                  frame_at((DX0 + 0.11 + dx, DY1, DZ0 + 0.045 + 0.012 * i), "y"))
        parts.append(gd)
    # tape: a patch on the rear left corner of the roof
    if lod < 2:
        tp = P("det_tape", "tape")
        g.box(tp, DX0 + 0.004, DX0 + 0.044, DY1 - 0.035, DY1 + 0.0008, DZ1, DZ1 + 0.0012)
        g.box(tp, DX0 + 0.004, DX0 + 0.044, DY1, DY1 + 0.0012, DZ1 - 0.045, DZ1)
        parts.append(tp)
    # cables from the back: they gather into a bundle above the rear deck edge, down the back of the machine and
    # into the terminal box
    jx0, jx1, jy0, jy1, jz0, jz1 = INS["jbox"]
    jym = (jy0 + jy1) / 2
    if lod < 2:
        for i, (dx, rr) in enumerate(DET_CABLES):
            gx = jx0 + 0.010 + 0.009 * i
            pts = [(DX0 + 0.11 + dx, DY1 + 0.015, DZ0 + 0.045 + 0.012 * i), (DX0 + 0.11 + dx, DY1 + 0.045, DZ0 + 0.014),
                   (BX + dx * 0.15, Y1 + 0.010, ZT + 0.014), (BX + dx * 0.12, Y1 + 0.016, ZT - 0.035),
                   (-0.25 + dx * 0.10, Y1 + 0.014, ZT - 0.11), (-0.30 + dx * 0.05, Y1 - 0.004, jz1 + 0.05),
                   (gx, jym, jz1 + 0.022), (gx, jym, jz1 + 0.006)]
            c = P("det_cable%d" % i, "cable")
            g.pipe(c, spline(pts, 2) if lod == 0 else pts, rr, 4)
            parts.append(c)
        bd = P("det_cable_tape", "tape")
        g.cyl(bd, (BX, Y1 + 0.016, ZT - 0.035), "z", 0.0128, 0.024, (12, 6)[lod])
        parts.append(bd)
    return parts


# =============================================================================
# Probe above the drum
# =============================================================================
def build_probe(spec):
    """Probe - a tube with a window at the tip on a bracket at the centrifuge opening, looking into the
    drum; the cable goes over the deck and the tank lid to the detector unit socket."""
    lod = spec["lod"]
    if lod == 2:
        return []
    L = PROBE_L
    fp = frame_axis(tuple(PROBE_B), PROBE_D)
    pr = P("probe_body", "probe")
    parts = [pr]
    if lod == 0:
        lathe(pr, [(0.0, 0.0), (0.0148, 0.0), (0.0160, 0.003), (0.0160, 0.052), (0.0150, 0.054), (0.0160, 0.056),
                   (0.0160, L - 0.006), (0.0120, L), (0.0, L + 0.0015)], 14, fp)
        bn = P("probe_sleeve", "probe_band")
        lathe(bn, [(0.0158, 0.068), (0.0172, 0.070), (0.0172, 0.082), (0.0158, 0.083)], 12, fp, closed=True)
        wn = P("probe_window", "dark")
        lathe(wn, [(0.0158, 0.083), (0.0164, 0.083), (0.0164, L - 0.020), (0.0158, L - 0.020)], 12, fp, closed=True)
        gl = P("probe_gland", "rubber")
        lathe(gl, [(0.0, -0.024), (0.0042, -0.024), (0.0088, -0.004), (0.0, 0.002)], 8, fp)
        parts += [bn, wn, gl]
    else:
        g.pipe(pr, [tuple(PROBE_B), tuple(PROBE_T)], 0.016, 8)
    # bracket: a pad on the deck, a post, a clamp
    bk = P("probe_bracket", "steel")
    c = PROBE_C
    g.box(bk, c.x - 0.014, c.x + 0.014, c.y - 0.012, c.y + 0.012, ZT, ZT + 0.003, **(dict(r=0.001, seg=1) if lod == 0 else {}))
    box_to(bk, (c.x, c.y, ZT + 0.002), (c.x, c.y, c.z - 0.0165), 0.012, 0.004, up=(PROBE_D.x, PROBE_D.y, 0.0))
    if lod == 0:
        lathe(bk, [(0.0161, -0.006), (0.0195, -0.006), (0.0195, 0.006), (0.0161, 0.006)], 12,
              frame_axis(tuple(c), PROBE_D), closed=True)
        for s in (-1, 1):
            screw(bk, (c.x + s * 0.0085, c.y, ZT + 0.003), "z", 0.0028, 6)
    parts.append(bk)
    # probe cable: from the plug on the socket of the unit sideways, onto the tank lid, along its front to
    # the right, from the lid edge onto the deck, to the bracket and up into the probe entry
    bnx, bnz = BNC
    tail = PROBE_B - PROBE_D * 0.024
    pts = [(bnx, YF - 0.034, bnz), (bnx + 0.020, YF - 0.044, bnz - 0.012), (bnx + 0.045, -0.132, DZF + 0.0045),
           (-0.030, -0.128, DZF + 0.0045), (LAY["wash"][1] - 0.002, -0.130, DZF + 0.004),
           (LAY["wash"][1] + 0.010, -0.132, ZT + 0.0045), (0.045, -0.140, ZT + 0.0045), (0.052, -0.168, ZT + 0.006),
           (0.050, -0.172, ZT + 0.030), (tail.x - 0.003, tail.y - 0.006, tail.z - 0.012), tuple(tail)]
    cb = P("probe_cable", "cable")
    g.pipe(cb, spline(pts, 2) if lod == 0 else pts, 0.0028, 4)
    parts.append(cb)
    return parts


# =============================================================================
# Dosimeter
# =============================================================================
def build_dosimeter(spec):
    """Household RKSB-104 dosimeter lying on the unit: a rounded body, a display in a frame (ozl_lcd, own
    texture: "off" is empty, "work" plays frames with readings), two buttons, a beeper grille."""
    lod = spec["lod"]
    x, y, ln, wd, ht = DOS
    ds = P("dos_body", "dos")
    g.box(ds, x - ln / 2, x + ln / 2, y - wd / 2, y + wd / 2, DZ1, DOS_TOP, **(dict(r=0.006, seg=2) if lod == 0 else {}))
    parts = [ds]
    if lod < 2:
        bz = P("dos_bezel", "black")
        g.box(bz, LCD[0] - 0.031, LCD[0] + 0.031, LCD[1] - 0.0145, LCD[1] + 0.0145, DOS_TOP - 0.0005, DOS_TOP + 0.0010,
              **(dict(r=0.002, seg=1) if lod == 0 else {}))
        parts.append(bz)
    zl = DOS_TOP + (0.0013 if lod < 2 else 0.0004)
    lc = P("dos_lcd", "black", group=SEL_LCD, section="lcd")
    fr = g.Frame((LCD[0], LCD[1], zl), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    hw, hh = LCD[2] / 2, LCD[3] / 2
    vs = [lc.bm.verts.new(fr.p(a, b, 0.0)) for a, b in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]
    lc.tag([lc.bm.faces.new(vs)])
    lc.glass_frame = (fr, -hw, hw, -hh, hh)
    parts.append(lc)
    if lod == 0:
        bt = P("dos_buttons", "dos_btn")
        for bx_, by_ in DOS_BTN:
            lathe(bt, [(0.0, DOS_TOP - 0.0005), (0.0050, DOS_TOP - 0.0005), (0.0050, DOS_TOP + 0.0016),
                       (0.0, DOS_TOP + 0.0027)], 10, frame_at((bx_, by_, 0.0), "z"))
        parts.append(bt)
        gr = P("dos_grille", "dark")
        x0, x1, y0, y1 = DOS_GRILLE
        for k in range(5):
            xc = x0 + (x1 - x0) * (k + 0.5) / 5
            g.box(gr, xc - 0.0013, xc + 0.0013, y0, y1, DOS_TOP - 0.0003, DOS_TOP + 0.0003)
        parts.append(gr)
    return parts


def build_power(spec):
    """Power cord: from the capacitor down and out of the open back, over the crate to the floor; a plug at the end."""
    lod = spec["lod"]
    if lod == 2:
        return []
    cx_, cy_ = X1 - W.T - 0.030, Y1 - 0.040
    route = [(cx_, cy_, ZD - 0.322), (cx_ - 0.010, cy_ + 0.004, ZD - 0.40), (X1 - 0.07, Y1 + 0.012, ZS + 0.07),
             (0.25, CY1 + 0.012, ZS + 0.007), (0.255, CY1 + 0.010, 0.070), (0.27, CY1 + 0.045, 0.0055),
             (0.36, 0.33, 0.0055), (0.46, 0.40, 0.0055), (0.52, 0.425, 0.012), (0.545, 0.432, 0.0165)]
    c = P("power_cord", "cable_grey")
    g.pipe(c, spline(route, 2) if lod == 0 else route, 0.0055, 5 if lod == 0 else 4)
    parts = [c]
    end, prev = Vector(route[-1]), Vector(route[-2])
    d = (end - prev)
    d.z = 0.0
    d.normalize()
    pl = P("power_plug", "plug")
    lathe(pl, [(0.0, -0.002), (0.0070, -0.002), (0.0125, 0.008), (0.0165, 0.012), (0.0165, 0.040), (0.0150, 0.044),
               (0.0, 0.044)], (10, 6)[lod], frame_axis(tuple(end), d))
    parts.append(pl)
    if lod == 0:
        pn = P("power_pins", "chrome")
        side = d.cross(Vector((0, 0, 1))).normalized()
        for s in (-1, 1):
            a = end + d * 0.044 + side * (s * 0.0095)
            g.pipe(pn, [tuple(a), tuple(a + d * 0.019)], 0.002, 4)
        parts.append(pn)
    return parts


def build_paper_tape(spec):
    """Two strips of tape on the upper corners of the vanilla sheet on the centrifuge lid."""
    if spec["lod"] != 0:
        return []
    tp = P("paper_tape", "tape")
    xm = (LAY["spin"][0] + LAY["spin"][1]) / 2
    for s in (-1, 1):
        c = LID_FR.p(xm + s * 0.105, 0.165 + 0.137, W.LID_T + 0.0010)
        a = math.radians(-45.0 * s)
        u = LID_FR.u * math.cos(a) + LID_FR.v * math.sin(a)
        v = LID_FR.n.cross(u)
        g.box(tp, -0.016, 0.016, -0.006, 0.006, -0.0004, 0.0004, frame=g.Frame(c, u, v, LID_FR.n))
    return [tp]


def build_lod(spec):
    parts = build_crate(spec)
    parts += W.twin_tub(M, spec, X0, X1, Y0, Y1, ZS, HM, drum_group=SEL_DRUM, knob_group=SEL_KNOB, hose_end=HOSE_OUT)
    parts += build_samples(spec) + build_detector(spec) + build_probe(spec) + build_dosimeter(spec)
    parts += build_power(spec) + build_paper_tape(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    wood = kx.PEN + r"\wood.rvmat"
    metal = kx.PEN + r"\metalplate.rvmat"
    crate = kx.box_pts(CX0, CX1, CY0, CY1, 0.0, ZS)
    body = kx.box_pts(X0 - 0.004, X1 + 0.004, Y0 - 0.025, Y1, ZS, ZT)
    # a component thinner than 0.5 m does not work: the unit and the lid go down into the machine
    det = kx.box_pts(DX0, DX1, YB, DY1, ZT - 0.4, DOS_TOP)
    sa, sb, _, _ = LAY["spin"]
    lid = kx.box_pts(sa, sb, Y0 + 0.03, LAY["hinge_y"] + 0.07, ZT - 0.25, ZT + 0.32)
    comps = [(crate, wood), (body, metal), (det, metal), (lid, metal)]
    memory = {
        "invView": [(0.0, -2.4, 1.0)],
        "ce_center": [(0.0, 0.0, 0.55)],
        "ce_radius": [(0.65, 0.0, 0.55)],
        # bone axes: the drum - vertical along the centrifuge axis; the needle and the "spin" knob - from the
        # axis toward the person (-Y: clockwise looking from the front), the toggle - to the right along the
        # lever axis (AXES above)
        "ozl_drum_axis": [(SCX, SCY, ZD - 0.40), (SCX, SCY, ZT)],
        **AXES,
    }
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 55.0, memory, bbox


# the first ones are for the --look preview: the detector unit and the machine panel (and in "work":
# needle, lamps, display, toggle, "spin" knob), overview, the drum from above, the open back
SHOTS = [
    ("detector", (-0.50, -0.78, 1.22), (DXC + 0.04, DY0, DZ0 + 0.06), 34),
    ("panel", (0.25, -1.0, 0.75), (0.0, Y0, ZT - 0.11), 36),
    ("front", (-0.75, -1.95, 1.35), (0.0, 0.0, 0.66), 30),
    ("drum_top", (SCX + 0.12, SCY - 0.30, 1.50), (SCX, SCY + 0.01, ZD - 0.14), 36),
    ("back", (0.95, 1.65, 1.05), (0.0, 0.08, 0.42), 32),
    ("drum", (SCX - 0.10, -0.62, 1.42), (SCX, SCY, 0.70), 34),
]

M.look_shots = (5, 2)
M.run(build_lod, collision, SHOTS, row_step=1.2, row_shot=((1.2, -5.2, 1.4), (1.2, 0, 0.6)))
