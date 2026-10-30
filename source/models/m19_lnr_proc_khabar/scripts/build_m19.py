"""M19 - TV-set detector: Khabar Analyzer of the Neutrals (OZL_Lnr_Proc_Khabar).
Analyzer: cargo 4x4, a sample tray on the TV roof. No modules (analyzers have none).

    blender --background --python build_m19.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: system Python make_decals.py (the screen "off" and 12 "work" frames, the
instrument scale, the detector block panel, the board, the channel dial, decals without text). Where
things are - m19_layout.py (shared with make_decals.py).

Look: the "dayz" look (matte, dirtier, coloured AO); the cabinet is a single shell with rounded corners
and edges, the lacquer rubbed by hands (m19_mats.build_veneer: light wood on the edges, by the knobs on
the side, along the front edge of the roof; mug rings); the mask is a smooth funnel to the screen with an
aluminium trim; the speaker grille - ribs over cloth; the knobs are turned, with a skirt and knurling,
the channel selector has a chromed skirt and a wing knob. Behind the removed wall: a picture tube with a
band on lugs, an anode cap and a wire to the flyback transformer, a deflection yoke with copper
windings, convergence rings, a socket on the neck; a chassis with a power transformer (core, coil,
brackets), tubes with glass and a silver getter, tube shields, electrolytic cans, the flyback in a
perforated cage with a kenotron; boards with parts; a speaker (basket, magnet) and the PTK behind the
strip. The detector block is a box in brown hammer enamel, an aluminium panel, a microammeter with a
needle, a lamp, a toggle, a knob, a radiation sign; on top of the block two SBM-20 counters in holders.
On the TV roof - a tray on a board with a pickup coil, a mug, a loop antenna on a rotary motor. Cables
are smooth curves. Stool: pipe legs, an apron, a spacer ring, rubber caps, a plywood seat with rounded
corners. Small things are vanilla DayZ items as proxies (kvanilla): a screwdriver and a pen on the roof,
an electrician's kit with pliers and insulating tape on the floor; the power cord with a plug on the
floor is own.

The device is a gutted Soviet tube TV set "Rubin" on a stool with a detector built inside (look-alikes:
"Rubin-106" in a wooden cabinet, the screen on the left, a strip with a grille and a knob on the right;
"Rubin 61TTs403D" with the back wall removed: boards of brown laminate at the sides, the picture tube
with a neck in the middle, chipboard inside; "Rubin-111", 1969).
The cabinet size follows the "Rubin-401": 746 x 518 x 495 mm (W x H x D), 65 kg (no datasheets of the late
"Rubin" sets were found; the "Rubin-102" is smaller - 495 x 480 x 435 mm). Picture tube 59 cm diagonal
(like the 59LK of "Rubin" sets of this size): visible window 0.47 x 0.36 m. The stool is a kitchen one
on steel legs, height 450 mm (GOST 13025.2-85 gives a seat height of 400-450, not checked), a plywood
seat 400 x 400. Result: a 0.746 x 0.968 x 0.495 m cabinet on a stool, 1.18 m with the loop antenna on the
roof.
Detector block: M42100 microammeter - 80 x 80 x 50 mm (as in M10); SBM-20 counter - 108 +- 3.5 x dia.
10 +- 1 mm (datasheet); the 210 x 135 x 120 box is home-made, an estimate. The dia. 125 speaker and the
PTK 108 x 112 x 90 are estimated from photos.

Work look: the picture tube screen is ozl_screen, own texture (section screen): "off" is dark grey glass,
"work" is 12 sweep frames (OZL_WorkFx frames); the detector block lamp is ozl_lamp (atlas _on, blinks);
the microammeter needle is the bone ozl_needle on its own source (wobble); the loop antenna on the motor
is the bone ozl_work on the source ozl_work: a model.cfg loop (sourceAddress loop, one turn per 3 s
pass) - the antenna turns, "searching" for a signal.
Neutrals (no green): lived-in - lacquer worn on the edges and on top, the stool chipped.

Blender axes: X is width, Y is depth (face toward -Y), Z is up.
"""
import math
import os
import random
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
import kwood  # noqa: E402
from m19_geo import (band_xy, box_to, bridge_rings, fan, frame_at, frame_axis, hexagon, knob, knurl_poly,  # noqa: E402
                     lathe, profile_xy, rr_xz, screw, se_ring, spline, torus)
from m19_layout import (ANT, ANT_BASE, ANT_R, ANT_Z, ARC_R, BOLT, BULGE, CH, CHASSIS, CUPS, DET, DIAL_H,  # noqa: E402
                        DIAL_W, GM_BOARD, GM_X, GM_Y, GRILLE, KNOB, LAMP, LEG_BOT, LEG_TOP, MA, MB, MUG_C, MUG_H,
                        MUG_R, MX, MZ, PCB_L, PCB_R, PICKUP, PIVOT, PLATE, R_CAB, RAD, RING_Z, SA, SB, SCR_A, SCR_B,
                        SCX, SCZ, SEAT, SIDE_KNOBS, SMALL, SN, SPEAKER, SUN, T, TOGGLE, TRAY, TUNER, WIN, X0, X1,
                        XS0, XS1, Y0, Y1, YBI, YF, YM, YSR, ZB, ZS, ZSEAT, ZT)
from m19_mats import build_veneer  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
DX0, DX1, DY0, DY1, DZ0, DZ1 = DET
CZ = (ZS + ZT) / 2                                          # middle of the cabinet in height
# picture tube: bulb rings (y, semi-axes a, b, superellipse exponent) from the screen to the neck
CRT = [(YBI + 0.012, SCR_A + 0.002, SCR_B + 0.002, SN), (-0.15, 0.236, 0.183, 4.6), (-0.10, 0.200, 0.155, 4.0),
       (-0.05, 0.155, 0.125, 3.2), (0.0, 0.100, 0.085, 2.5), (0.03, 0.060, 0.056, 2.2), (0.05, 0.035, 0.035, 2.0)]
ANODE_Y, ANODE_TH = -0.05, math.radians(62.0)               # anode cap: on the cone, top right
FLY, FLY_H = (0.02, 0.095, 0.15, 0.225), 0.085              # flyback in a cage: x0 x1 y0 y1, height
# chassis tubes: x, y, bulb height, in a shield
TUBES = [(-0.30, 0.19, 0.085, False), (-0.255, 0.195, 0.07, True), (-0.21, 0.19, 0.07, False),
         (-0.30, 0.135, 0.06, True), (-0.16, 0.135, 0.085, False), (-0.165, 0.195, 0.05, False)]
CAPS = [(0.0, 0.06, 0.075), (0.045, 0.045, 0.06), (-0.045, 0.06, 0.07)]   # electrolytic cans: x, y, height
GLAND_PICK, GLAND_ANT, GLAND_SIG = (0.315, 0.222), (0.315, 0.200), (0.135, 0.225)   # inlets on the roof of the block

LOD_SPECS = [
    dict(lod=0, sides=16, n=48, cn=3, rings=(0.35, 0.65, 0.88, 1.0)),
    dict(lod=1, sides=8, n=24, cn=2, rings=(0.6, 1.0)),
    dict(lod=2, sides=6, n=16, cn=1, rings=(1.0,)),
]

REGIONS = {
    "wood": ("wood", 0.6), "wood_side": ("wood_side", 0.6), "wood_top": ("wood_top", 0.7), "chip": ("chip", 0.4),
    "rail": ("rail", 0.8), "mask": ("mask", 0.8), "trim": ("trim", 1.2), "strip": ("strip", 1.6),
    "cloth": ("cloth", 1.2), "grille": ("grille", 2.0), "knob": ("knob", 2.5), "chrome": ("chrome", 2.0),
    "mark": ("mark", 3.0), "black": ("black", 1.2), "crt": ("crt", 0.5), "band": ("band", 1.0), "neck": ("neck", 2.0),
    "yoke": ("yoke", 1.5), "copper": ("copper", 2.0), "chassis": ("chassis", 0.8), "core": ("core", 1.2),
    "paper": ("paper", 1.5), "tube": ("tube", 2.5), "getter": ("getter", 2.5), "alu": ("alu", 1.5),
    "grille_v": ("grille_v", 1.2), "pcb": ("pcb", 1.5), "board_plain": ("board_plain", 1.5),
    "cap_blue": ("cap_blue", 2.0), "cap_orange": ("cap_orange", 2.0), "res": ("res", 2.0),
    "speaker": ("speaker", 1.2), "magnet": ("magnet", 1.5), "tin": ("tin", 1.2), "det": ("det", 1.2),
    "det_panel": ("det_panel", 2.5), "bezel": ("bezel", 2.0), "dial": ("dial", 6.0), "needle": ("needle", 2.0),
    "lamp": ("lamp", 3.0), "gm": ("gm", 2.5), "gm_board": ("gm_board", 1.5), "brass": ("brass", 2.0),
    "steel": ("steel", 1.5), "wire_red": ("wire_red", 1.0), "wire_white": ("wire_white", 1.0),
    "wire_black": ("black", 1.0), "wire_grey": ("wire_grey", 1.0), "wire_hv": ("wire_hv", 1.0), "cord": ("cord", 0.8),
    "tape": ("tape", 1.5), "stool": ("stool", 0.8), "seat": ("seat", 0.6), "rubber": ("rubber", 1.0),
    "tray": ("tray", 1.2), "ply": ("ply", 1.2), "mug": ("mug", 2.0), "tea": ("tea", 2.0), "ant": ("ant", 1.5),
    "ant_base": ("ant_base", 1.5), "motor": ("motor", 1.5),
}

# =============================================================================
# Materials
# =============================================================================


def decal(name, ax, sign, uv, center, size, rng=None):
    return (os.path.join(WORK, name), ax, sign, uv, center, size, rng)


KINDS = kmats.std_kinds(floor_z=0.0)
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# veneer under the Neutrals' dark brown lacquer (no green)
WOOD = dict(color=kmats.lin((78, 44, 26)), seed=1.9, along="x", gloss=0.55, spec=0.35, floor_z=0.0, dust=0.35,
            grime=0.5, rings=0.35, knots=0.1)
# where the lacquer is worn by hands: (centre, semi-axes, strength) - by the
# knobs on the side, along the roof edges, under the tray and the mug
FRONT_RUB = [((X1 - 0.08, Y0, 0.62), (0.10, 0.03, 0.22), 0.30), ((0.0, Y0, ZT), (0.42, 0.03, 0.03), 0.35)]
SIDE_RUB = [((X1, SIDE_KNOBS[0][0], 0.62), (0.03, 0.08, 0.10), 0.55), ((X1, -0.05, ZT), (0.03, 0.25, 0.03), 0.25),
            ((X0, -0.05, ZT), (0.03, 0.25, 0.03), 0.25)]
TOP_RUB = [((0.0, Y0, ZT), (0.42, 0.06, 0.03), 0.35), ((TRAY[0], TRAY[1], ZT), (0.17, 0.13, 0.03), 0.25),
           ((MUG_C[0], MUG_C[1], ZT), (0.08, 0.08, 0.03), 0.20)]
TOP_DECALS = [decal("decal_sun.png", "z", 1, ("x", "y"), SUN[0], (SUN[1], SUN[1]), (ZT - 0.002, ZT + 0.002)),
              decal("decal_bolt.png", "z", 1, ("x", "y"), BOLT[0], BOLT[1], (ZT - 0.002, ZT + 0.002))]
PCB_DECALS = [decal("decal_pcb.png", "y", 1, ("x", "z"), ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0),
                    (y - 0.002, y + 0.002)) for x0, x1, z0, z1, y in (PCB_L, PCB_R)]
DIAL_Y = YF + 0.0026                                        # face of the instrument scale
KINDS.update({
    "wood": (build_veneer, dict(WOOD, rub=FRONT_RUB)),
    "wood_side": (build_veneer, dict(WOOD, along="y", seed=2.3, rub=SIDE_RUB)),
    "wood_top": (build_veneer, dict(WOOD, seed=2.7, dust=0.18, grime=0.4, rub=TOP_RUB, cups=CUPS, decal_items=TOP_DECALS)),
    # chipboard inside: light blotchy shavings; the bar for the back wall is pine
    "chip": ("plastic", dict(color=kmats.lin((146, 108, 70)), gloss=0.08, spec=0.05, mottle=0.30, dust=0.5,
                             grime=0.4, scuff=(0.8, 0.9))),
    "rail": (kwood.build_wood, dict(color=kmats.lin((168, 128, 84)), seed=3.3, along="x", dust=0.5, grime=0.4,
                                    knots=0.4)),
    # mask: light grey plastic, yellowed; the trim is aluminium
    "mask": ("plastic", dict(color=kmats.lin((196, 192, 178)), gloss=0.35, spec=0.25, mottle=0.06, dust=0.3,
                             grime=0.35, scuff=(0.66, 0.74))),
    "trim": ("steel", dict(seed=3.4, tone=0.46, along="x", gloss=0.5, spec=0.6, dust=0.3, grime=0.4)),
    "strip": ("paint", dict(CLEAN, color=kmats.lin((64, 60, 56)), gloss=0.4, spec=0.3, dust=0.2, grime=0.3,
                            decal_items=[decal("decal_dial.png", "y", -1, ("x", "z"), CH, (0.10, 0.10))])),
    # speaker grille: cloth and ribs of silver plastic
    "cloth": ("plastic", dict(color=kmats.lin((44, 36, 30)), gloss=0.05, spec=0.03, mottle=0.2, dust=0.4, grime=0.3,
                              scuff=(0.9, 1.0))),
    "grille": ("plastic", dict(color=kmats.lin((178, 176, 168)), gloss=0.45, spec=0.35, mottle=0.05, dust=0.35,
                               grime=0.4, scuff=(0.66, 0.74))),
    # knobs: cream plastic, worn by fingers; chrome skirt; marks
    "knob": ("plastic", dict(color=kmats.lin((198, 190, 168)), gloss=0.45, spec=0.3, mottle=0.08, dust=0.2,
                             scuff=(0.6, 0.7))),
    "chrome": ("steel", dict(seed=6.1, tone=0.60, along="x", gloss=0.75, spec=0.85, dust=0.2, grime=0.4)),
    "mark": ("flat", dict(color=kmats.lin((228, 224, 210)), gloss=0.3, spec=0.2)),
    # picture tube: graphite coating of the cone, band, neck glass, yoke with copper
    "crt": ("plastic", dict(color=kmats.lin((34, 34, 36)), gloss=0.2, spec=0.15, mottle=0.15, dust=0.6, grime=0.2)),
    "band": ("steel", dict(seed=4.4, tone=0.36, along="y", gloss=0.45, spec=0.55, dust=0.4, grime=0.5)),
    "neck": ("flat", dict(color=kmats.lin((96, 104, 104)), gloss=0.9, spec=0.7)),
    "yoke": ("plastic", dict(color=kmats.lin((46, 40, 34)), gloss=0.35, spec=0.25, dust=0.45, grime=0.3)),
    "copper": ("paint", dict(CLEAN, color=kmats.lin((170, 94, 46)), gloss=0.6, spec=0.55, dust=0.3, grime=0.3)),
    # chassis: cadmium-plated steel in dust; transformer - varnished iron and a winding in varnished cloth
    "chassis": ("steel", dict(seed=4.8, tone=0.40, along="x", gloss=0.5, spec=0.6, floor_z=ZB, dust=0.6, grime=0.5)),
    "core": ("paint", dict(color=kmats.lin((52, 52, 54)), under=kmats.lin((96, 92, 86)), seed=5.1, gloss=0.3,
                           spec=0.3, chip=(0.60, 0.66), rust=(0.60, 0.68), rust_low=0.3, floor_z=ZB, dust=0.5,
                           grime=0.4)),
    "paper": ("plastic", dict(color=kmats.lin((176, 140, 84)), gloss=0.3, spec=0.2, mottle=0.2, dust=0.5, grime=0.4)),
    # tubes: grey glass and a silver getter on top; tube shields and cans - aluminium
    "tube": ("flat", dict(color=kmats.lin((96, 98, 100)), gloss=0.9, spec=0.75)),
    "getter": ("flat", dict(color=kmats.lin((176, 178, 182)), gloss=0.95, spec=0.9)),
    "alu": ("steel", dict(seed=5.6, tone=0.55, along="z", gloss=0.5, spec=0.6, floor_z=ZB, dust=0.5, grime=0.4)),
    "pcb": ("paint", dict(CLEAN, color=kmats.lin((112, 46, 34)), gloss=0.5, spec=0.35, dust=0.3, grime=0.2,
                          decal_items=PCB_DECALS)),
    "board_plain": ("plastic", dict(color=kmats.lin((112, 52, 36)), gloss=0.45, spec=0.3, dust=0.4, grime=0.3)),
    "cap_blue": ("plastic", dict(color=kmats.lin((60, 92, 150)), gloss=0.45, spec=0.35, dust=0.4)),
    "cap_orange": ("plastic", dict(color=kmats.lin((196, 110, 40)), gloss=0.45, spec=0.35, dust=0.3)),
    "res": ("plastic", dict(color=kmats.lin((176, 150, 110)), gloss=0.35, spec=0.25, dust=0.3)),
    # speaker: basket in black paint, magnet; PTK - tinned sheet
    "speaker": ("paint", dict(color=kmats.lin((40, 40, 40)), under=kmats.lin((110, 108, 104)), seed=6.2, gloss=0.35,
                              spec=0.3, chip=(0.62, 0.68), rust=(0.62, 0.70), rust_low=0.0, dust=0.5, grime=0.3)),
    "magnet": ("steel", dict(seed=6.4, tone=0.24, along="z", gloss=0.45, spec=0.5, dust=0.5, grime=0.4)),
    "tin": ("steel", dict(seed=6.9, tone=0.50, along="y", gloss=0.55, spec=0.6, dust=0.5, grime=0.5)),
    # detector block: brown hammer enamel (Neutrals), chips down to grey primer; the panel is aluminium with marks
    "det": ("paint", dict(color=kmats.lin((92, 74, 58)), under=kmats.lin((110, 108, 104)), seed=4.6, gloss=0.35,
                          spec=0.35, chip=(0.62, 0.68), rust=(0.70, 0.78), rust_low=0.2, floor_z=ZB, dust=0.35,
                          grime=0.4)),
    "det_panel": ("paint", dict(color=kmats.lin((170, 172, 170)), under=kmats.lin((120, 122, 120)), seed=7.7,
                                gloss=0.4, spec=0.35, chip=(0.70, 0.78), rust=(0.99, 1.0), rust_low=0.0, dust=0.15,
                                grime=0.15, decal_items=[
                                    decal("decal_detpanel.png", "y", 1, ("x", "z"),
                                          ((PLATE[0] + PLATE[1]) / 2, (PLATE[2] + PLATE[3]) / 2),
                                          (PLATE[1] - PLATE[0], PLATE[3] - PLATE[2]), (YF - 0.002, YF + 0.002)),
                                    decal("decal_radiation.png", "y", 1, ("x", "z"), RAD[:2], (RAD[2], RAD[2]),
                                          (YF - 0.002, YF + 0.002))])),
    "bezel": ("plastic", dict(color=kmats.lin((22, 21, 20)), gloss=0.5, spec=0.4, dust=0.15, scuff=(0.8, 0.9))),
    "dial": ("paint", dict(CLEAN, color=kmats.lin((226, 220, 202)), gloss=0.5, spec=0.35,
                           decal_items=[decal("decal_meter.png", "y", 1, ("x", "z"),
                                              ((WIN[0] + WIN[1]) / 2, (WIN[2] + WIN[3]) / 2), (DIAL_W, DIAL_H),
                                              (DIAL_Y - 0.0006, DIAL_Y + 0.0006))])),
    "needle": ("flat", dict(color=kmats.lin((24, 24, 24)), gloss=0.4, spec=0.3)),
    # lamp: unlit - dark amber glass, "work" - lit (blinking by the mod script)
    "lamp": ("flat", dict(color=kmats.lin((86, 48, 16)), gloss=0.85, spec=0.8)),
    "lamp_on": ("flat", dict(color=kmats.lin((255, 176, 70)), gloss=0.85, spec=0.8)),
    # SBM-20: a thin steel tube, holders - brass, the board - laminate
    "gm": ("steel", dict(seed=7.9, tone=0.32, along="x", gloss=0.55, spec=0.6, dust=0.3, grime=0.3)),
    "gm_board": ("paint", dict(CLEAN, color=kmats.lin((150, 120, 70)), gloss=0.4, spec=0.3, dust=0.4, grime=0.3)),
    "brass": ("paint", dict(CLEAN, color=kmats.lin((170, 140, 80)), gloss=0.6, spec=0.6, dust=0.2, grime=0.3)),
    "wire_red": ("plastic", dict(color=kmats.lin((150, 40, 30)), gloss=0.45, spec=0.3, dust=0.3)),
    "wire_white": ("plastic", dict(color=kmats.lin((196, 190, 172)), gloss=0.4, spec=0.3, dust=0.3)),
    "wire_grey": ("plastic", dict(color=kmats.lin((120, 118, 112)), gloss=0.3, spec=0.2, dust=0.4, grime=0.4)),
    "wire_hv": ("plastic", dict(color=kmats.lin((168, 44, 34)), gloss=0.5, spec=0.35, dust=0.4)),
    "cord": ("plastic", dict(color=kmats.lin((86, 60, 44)), gloss=0.3, spec=0.2, dust=0.4, grime=0.6)),
    "tape": ("plastic", dict(color=kmats.lin((26, 26, 28)), gloss=0.45, spec=0.3, dust=0.3, grime=0.3,
                             scuff=(0.7, 0.8))),
    # stool: steel legs in dark brown enamel with chips, a plywood seat rubbed
    "stool": ("paint", dict(color=kmats.lin((70, 56, 46)), under=kmats.lin((120, 118, 114)), seed=5.3, gloss=0.4,
                            spec=0.35, chip=(0.56, 0.62), rust=(0.62, 0.70), rust_low=0.8, floor_z=0.0, dust=0.3,
                            grime=0.8)),
    "seat": (kwood.build_wood, dict(color=kmats.lin((168, 128, 86)), seed=3.1, along="x", gloss=0.25, spec=0.12,
                                    floor_z=0.0, dust=0.2, grime=0.3, knots=0.3)),
    # tray: white enamel, chips down to black; the board with a coil - plywood and copper wire
    "tray": ("paint", dict(color=kmats.lin((222, 220, 210)), under=kmats.lin((26, 26, 30)), seed=6.4, gloss=0.6,
                           spec=0.45, chip=(0.58, 0.64), rust=(0.72, 0.80), rust_low=0.0, floor_z=ZT, dust=0.15,
                           grime=0.3)),
    "ply": (kwood.build_wood, dict(color=kmats.lin((176, 140, 96)), seed=6.8, along="x", gloss=0.2, spec=0.1,
                                   floor_z=ZT, dust=0.3, grime=0.4, knots=0.2)),
    "mug": ("paint", dict(color=kmats.lin((150, 52, 38)), under=kmats.lin((26, 26, 30)), seed=9.2, gloss=0.6,
                          spec=0.4, chip=(0.57, 0.63), rust=(0.70, 0.78), rust_low=0.0, floor_z=ZT, dust=0.15,
                          grime=0.4)),
    "tea": ("flat", dict(color=kmats.lin((70, 38, 18)), gloss=0.9, spec=0.6)),
    # loop antenna: copper wire in brown lacquer; motor box - bakelite
    "ant": ("plastic", dict(color=kmats.lin((120, 70, 40)), gloss=0.5, spec=0.45, mottle=0.12, dust=0.3)),
    "ant_base": ("plastic", dict(color=kmats.lin((44, 34, 28)), gloss=0.45, spec=0.35, dust=0.4, grime=0.3,
                                 scuff=(0.66, 0.74))),
    "motor": ("paint", dict(color=kmats.lin((70, 74, 70)), under=kmats.lin((130, 130, 126)), seed=8.1, gloss=0.4,
                            spec=0.4, chip=(0.62, 0.70), rust=(0.66, 0.74), rust_low=0.0, dust=0.3, grime=0.3)),
})

OBJ, NAME = "m19_lnr_proc_khabar", "ozr_lnr_proc_khabar"
# Work look: the screen is its own texture (the frames are stepped by the mod script), the lamp is the _on
# atlas (blinks), the needle is the bone ozl_needle (swaying), the antenna is the bone ozl_work (model.cfg loop).
SEL_SCREEN, SEL_LAMP, SEL_ANT, SEL_NEEDLE = "ozl_screen", "ozl_lamp", "ozl_work", "ozl_needle"
ANT_TURNS = 1                                               # turns per loop pass (3 s)
METER_SPAN = math.pi / 2                                    # M42100 scale - 90 degrees
METER_REST = 45.0                       # zero: 45 degrees from +X (left end of the scale seen from the back)
METER_TIP = ARC_R * 1.08                                    # needle length from the axis
METER_MID, METER_AMP = 0.55, 0.08                           # needle in "work": wobble mid +- amp
NEEDLE_O = (PIVOT[0], YF + 0.0035, PIVOT[1])
# The needle axis is memory points (collision below). The engine rotates a bone as a right-hand screw in
# DayZ axes (kexport.conv, determinant -1); in Blender axes that is a left-hand screw about the axis from
# the first point to the second: the axis looks at the person, a plus angle goes clockwise for him (as in
# M08, M12, M14, M33 - their needles are right in game). The detector block faces the open back (+Y) - the
# axis toward the person is +Y too.
NEEDLE_AXIS = [NEEDLE_O, (NEEDLE_O[0], NEEDLE_O[1] + 0.05, NEEDLE_O[2])]


def engine_turn(axis_pts, ang):
    """Rotation of a bone by angle ang as the engine will do it about the memory axis axis_pts: (point on
    the axis, Blender axis for Matrix.Rotation - a right-hand screw, angle). The Blender axis is opposite
    to the memory axis (from the second point to the first)."""
    a, b = Vector(axis_pts[0]), Vector(axis_pts[1])
    return tuple(a), tuple(a - b), ang


# "work" look preview: the needle is deflected by the engine rotation (engine_turn - the preview shows
# what will be in game), the antenna is turned (the rotation is _posed below); not exported to p3d
ON_MOVE = {}
POSE_ON = {
    SEL_NEEDLE: engine_turn(NEEDLE_AXIS, METER_MID * METER_SPAN),
    SEL_ANT: ((ANT[0], ANT[1], ZT), (0.0, 0.0, 1.0), math.radians(40.0)),
}


def check_needle():
    """By numbers, like check_axes of the Storage boxes: the engine rotation takes the needle at phases 0,
    mid +- amp and 1 along the scale clockwise for whoever looks at the block from behind the TV set
    (135 -> 45 degrees), the tip does not leave the scale window. If they do not match, the build fails."""
    c = Vector(NEEDLE_O)
    a = math.radians(METER_REST)
    tip = c + Vector((math.cos(a), 0.0, math.sin(a))) * METER_TIP
    seen = []
    for ph in (0.0, METER_MID - METER_AMP, METER_MID, METER_MID + METER_AMP, 1.0):
        o, ax, ang = engine_turn(NEEDLE_AXIS, ph * METER_SPAN)
        q = Vector(o) + Matrix.Rotation(ang, 3, Vector(ax)) @ (tip - Vector(o))
        deg = math.degrees(math.atan2(q.z - c.z, -(q.x - c.x)))          # for the viewer behind, right is -X
        assert abs(deg - (135.0 - math.degrees(METER_SPAN) * ph)) < 0.01, "needle goes the wrong way: %.1f" % deg
        assert WIN[0] < q.x < WIN[1] and WIN[2] < q.z < WIN[3], "needle tip outside the scale window: phase %.2f" % ph
        seen.append("%.2f -> %.1f" % (ph, deg))
    print("turns ok: needle (phase -> degrees for the viewer) " + ", ".join(seen))


check_needle()
ON = dict(remap={"lamp": "lamp_on"}, emissive=(1.0, 1.0, 1.0, 1.0), move=ON_MOVE)
ANT_ANIM = ("ozl_antenna_spin", dict(type="rotation", source="ozl_work", sourceAddress="loop", selection=SEL_ANT,
                                     axis="ozl_work_axis", memory=1, minValue=0.0, maxValue=1.0 / ANT_TURNS,
                                     angle0=0.0, angle1=2 * math.pi))
NEEDLE_ANIM = ("ozl_needle_swing", dict(type="rotation", source="ozl_needle", selection=SEL_NEEDLE,
                                        axis="ozl_needle_axis", memory=1, minValue=0.0, maxValue=1.0, angle0=0.0,
                                        angle1=METER_SPAN))
SCREEN = dict(off="decal_screen_off.png", frames=["decal_screen_f%02d.png" % i for i in range(12)], size=512,
              gloss=0.85)
# vanilla DayZ items as proxies: a screwdriver and a pen on the roof, an electrician's kit with pliers and
# insulating tape on the floor by the stool
KIT_H = kv.box("electrickit")[1][2] - kv.box("electrickit")[0][2]
DECOR = [
    kv.put("screwdriver", (0.25, -0.04, ZT), **kv.flat(70)),
    kv.put("pen", (0.02, -0.19, ZT), **kv.flat(5)),
    kv.put("electrickit", (-0.33, -0.36, 0.0), **kv.flat(12)),
    kv.put("pliers", (-0.33, -0.365, KIT_H), **kv.flat(-60)),
    kv.put("ducttape", (0.33, 0.27, 0.0), **kv.flat(0)),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 selections=(SEL_SCREEN, SEL_LAMP, SEL_ANT, SEL_NEEDLE), hidden=(SEL_SCREEN, SEL_LAMP),
                 states={"on": ON}, bones=((SEL_ANT, ""), (SEL_NEEDLE, "")), animations=(ANT_ANIM, NEEDLE_ANIM),
                 decor=DECOR, panels={"screen": SCREEN},
                 sources={"ozl_work": dict(animPeriod=3.0), "ozl_needle": dict(animPeriod=0.2)})
P = M.part
BOUNDS = {}


def _posed(place):
    """Preview of the "work" look: parts of the POSE_ON groups are in the work pose (rotation about the
    bone axis). kmodel can only shift (move), so the rotation is here, a wrapper over krender (as in M10);
    not exported to p3d - the model.cfg animations do that."""
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


def cable(name, region, pts, r, lod, k=2, sides=None):
    """Cable as a smooth curve (near LOD - a spline through the points, middle - a polyline)."""
    c = P(name, region)
    g.pipe(c, spline(pts, k) if lod == 0 else pts, r, sides or (6 if lod == 0 else 4))
    return c


# =============================================================================
# TV cabinet: a single shell (sides, roof, bottom) with rounded corners and edges
# =============================================================================
def cab_ring(off, y, n, inner=False):
    """Cabinet contour in the plane y: outer (off - inward, the edge) or inner (off - into the wall)."""
    hw, hh = (X1 - X0) / 2, (ZT - ZS) / 2
    if inner:
        return rr_xz(0.0, CZ, hw - T + off, hh - T + off, 0.004 + off, n, y)
    return rr_xz(0.0, CZ, hw - off, hh - off, R_CAB - off, n, y)


def build_cabinet(spec):
    lod, n = spec["lod"], spec["cn"]
    yi = YM + 0.004
    # rings around: face, edge, outer wall, rear edge, end, inside; where the belt looks
    if lod == 0:
        seq = [(0.0, Y0 + 0.0015, True), (0.0015, Y0, True), (0.004, Y0, False), (0.0012, Y0 + 0.0012, False),
               (0.0, Y0 + 0.004, False), (0.0, Y1 - 0.004, False), (0.0012, Y1 - 0.0012, False), (0.004, Y1, False),
               (0.0015, Y1, True), (0.0, Y1 - 0.0015, True), (0.0, yi, True)]
        wants = [("-y", "in"), ("-y",), ("-y", "out"), ("-y", "out"), ("out",), ("+y", "out"), ("+y", "out"),
                 ("+y",), ("+y", "in"), ("in",), ("in",)]
    elif lod == 1:
        seq = [(0.0, Y0, True), (0.002, Y0, False), (0.0, Y0 + 0.002, False), (0.0, Y1 - 0.002, False),
               (0.002, Y1, False), (0.0, Y1, True), (0.0, yi, True)]
        wants = [("-y",), ("-y", "out"), ("out",), ("+y", "out"), ("+y",), ("in",), ("in",)]
    else:
        seq = [(0.0, Y0, True), (0.0, Y0, False), (0.0, Y1, False), (0.0, Y1, True)]
        wants = [("-y",), ("out",), ("+y",), ("in",)]

    def want(i, c):
        r = Vector((c.x, 0.0, c.z - CZ))
        if r.length > 1e-9:
            r.normalize()
        w = Vector()
        for k in wants[i]:
            w += {"-y": Vector((0, -1, 0)), "+y": Vector((0, 1, 0)), "out": r, "in": -r}[k]
        return w
    sh = P("cabinet", "wood")
    bridge_rings(sh, [cab_ring(off, y, n, inner) for off, y, inner in seq], want, closed_loop=True)
    # regions: inside - chipboard (veneer near the face), roof - with traces and decals, sides - grain along y
    ids = {r: sh.region_index(r, *REGIONS[r]) for r in ("wood", "wood_side", "wood_top", "chip")}
    hw, hh = (X1 - X0) / 2 - T, (ZT - ZS) / 2 - T
    for f in sh.bm.faces:
        c, nn = f.calc_center_median(), f.normal
        if abs(nn.y) < 0.5 and abs(c.x) < hw + 0.0008 and abs(c.z - CZ) < hh + 0.0008:
            reg = "chip" if c.y > YM + 0.002 else "wood"
        elif nn.z > 0.7:
            reg = "wood_top"
        elif abs(nn.x) > 0.7:
            reg = "wood_side"
        else:
            reg = "wood"
        f[sh.reg] = ids[reg]
    # panel behind the mask (the picture tube goes through it): closes the mask and the screen from the inside
    fp = P("cab_front_in", "chip")
    g.box(fp, X0 + T, X1 - T, YBI + 0.006, YBI + 0.012, ZS + T, ZT - T)
    parts = [sh, fp]
    if lod < 2:
        # bar under the roof at the rear edge - the back wall was held on it, the screws remain
        rl = P("cab_rail", "rail")
        g.box(rl, X0 + T, X1 - T, Y1 - 0.026, Y1 - 0.006, ZT - T - 0.016, ZT - T)
        parts.append(rl)
    if lod == 0:
        sc = P("cab_screws", "steel")
        for x in (-0.30, -0.10, 0.10, 0.28):
            screw(sc, (x, Y1 - 0.006, ZT - T - 0.008), "y", 0.0042)
        parts.append(sc)
    return parts


# =============================================================================
# Front: mask with a bevel to the window, screen (ozl_screen), trim, strip with a grille, knobs
# =============================================================================
def build_front(spec):
    lod, N = spec["lod"], spec["n"]
    parts = []
    mk = P("mask", "mask")
    outer = se_ring(YM, MA, MB, SN, N, SCX, SCZ, rect=True)
    win = se_ring(YBI, SA + 0.012, SB + 0.012, SN, N, SCX, SCZ)

    def mid(t, y):
        return [Vector((o.x + (w.x - o.x) * t, y, o.z + (w.z - o.z) * t)) for o, w in zip(outer, win)]
    # a flat belt at the mask edge, then a funnel to the window (steeper toward the screen)
    if lod == 0:
        rings = [outer, mid(0.06, YM)] + [mid(0.06 + 0.94 * s, YM + (YBI - YM) * s ** 1.5) for s in (0.3, 0.65)]
        rings.append(win)
    elif lod == 1:
        rings = [outer, mid(0.06, YM), mid(0.55, YM + (YBI - YM) * 0.55 ** 1.5), win]
    else:
        rings = [outer, win]
    lip = [Vector((p.x, YBI + 0.008, p.z)) for p in win]
    nb = len(rings) - 1
    bridge_rings(mk, rings + [lip], lambda i, c: (0, -1, 0) if i < nb else (SCX - c.x, 0.0, SCZ - c.z))
    parts.append(mk)
    # picture tube: convex glass, the rim is behind the window edge; own texture ("work" frames), UV over the frame
    sc = P("screen", "black", group=SEL_SCREEN, section="screen")
    srings = [se_ring(YSR - BULGE * (1 - rho * rho), SCR_A * rho, SCR_B * rho, SN, N, SCX, SCZ) for rho in spec["rings"]]
    vr = bridge_rings(sc, srings, lambda i, c: (0, -1, 0))
    fan(sc, vr[0], (SCX, YSR - BULGE, SCZ), (0, -1, 0))
    sc.glass_frame = (g.Frame((SCX, YSR, SCZ), (1, 0, 0), (0, 0, 1), (0, -1, 0)), -SCR_A, SCR_A, -SCR_B, SCR_B)
    parts.append(sc)
    if lod < 2:
        # aluminium trim of the opening and a bridge between the mask and the strip
        tr = P("trim", "trim")
        w = 0.006
        xa, xb, za, zb = X0 + T, X1 - T, ZS + T, ZT - T
        for x0, x1, z0, z1 in ((xa, xb, zb - w, zb), (xa, xb, za, za + w), (xa, xa + w, za + w, zb - w),
                               (xb - w, xb, za + w, zb - w), (XS0 - w / 2, XS0 + w / 2, za + w, zb - w)):
            g.box(tr, x0, x1, YM - 0.002, YM + 0.001, z0, z1)
        parts.append(tr)
    # strip on the right: channel dial (decal), speaker grille - ribs over cloth in a frame
    st = P("strip", "strip")
    g.box(st, XS0, XS1, YM, YM + 0.04, ZS + T, ZT - T)
    parts.append(st)
    gx, gz, gw, gh = GRILLE
    gx0, gx1, gz0, gz1 = gx - gw / 2, gx + gw / 2, gz - gh / 2, gz + gh / 2
    if lod < 2:
        cl = P("grille_cloth", "cloth")
        g.box(cl, gx0, gx1, YM - 0.0008, YM + 0.0002, gz0, gz1)
        gr = P("grille", "grille")
        nrib = 13 if lod == 0 else 7
        for k in range(nrib):
            x = gx0 + (k + 0.5) * gw / nrib
            g.box(gr, x - 0.00175, x + 0.00175, YM - 0.0048, YM - 0.0008, gz0 + 0.002, gz1 - 0.002)
        f = 0.004
        for x0, x1, z0, z1 in ((gx0 - f, gx1 + f, gz1, gz1 + f), (gx0 - f, gx1 + f, gz0 - f, gz0),
                               (gx0 - f, gx0, gz0, gz1), (gx1, gx1 + f, gz0, gz1)):
            g.box(gr, x0, x1, YM - 0.0055, YM, z0, z1)
        parts += [cl, gr]
    # knobs: the channel selector (chromed skirt, knurled cap, wing knob with a mark), two small ones on the
    # strip, two on the right side
    kn = P("knobs", "knob")
    mk_ = P("knob_marks", "mark") if lod == 0 else None
    parts.append(kn)
    if lod == 0:
        ch = P("knob_chrome", "chrome")
        fr = frame_at((CH[0], YM, CH[1]), "-y")
        lathe(ch, [(0.031, 0.0), (0.031, 0.003), (0.0285, 0.0055), (0.0, 0.0055)], 24, fr)
        g.prism(kn, knurl_poly(0.022, 14, 0.001), (0, 1), 0.0055, 0.020, frame=fr)
        lathe(kn, [(0.0212, 0.020), (0.018, 0.0225), (0.0, 0.0242)], 16, fr)
        g.box(kn, -0.0055, 0.0055, -0.0235, 0.0235, 0.021, 0.036, r=0.0025, seg=1, frame=fr)
        g.box(mk_, -0.0009, 0.0009, 0.008, 0.020, 0.0360, 0.0366, frame=fr)
        parts.append(ch)
    else:
        g.cyl(kn, (CH[0], YM - 0.012, CH[1]), "y", 0.026 if lod == 1 else 0.024, 0.024, 12 if lod == 1 else 6)
    if lod < 2:
        for x, z in SMALL:
            knob(kn, mk_, (x, YM, z), "-y", 0.0170, 0.0125, 0.014, lod, ribs=8, sides=12 if lod == 0 else None)
        for y, z in SIDE_KNOBS:
            knob(kn, mk_, (X1, y, z), "x", 0.0170, 0.0125, 0.014, lod, plain=True, sides=10 if lod == 0 else None)
    if mk_ is not None:
        parts.append(mk_)
    return parts


# =============================================================================
# Picture tube behind the removed back wall
# =============================================================================
def crt_abn(y):
    """Semi-axes and exponent of the bulb contour at depth y (between the CRT rings - straight)."""
    for (y0, a0, b0, n0), (y1, a1, b1, n1) in zip(CRT, CRT[1:]):
        if y <= y1:
            t = max(0.0, min(1.0, (y - y0) / (y1 - y0)))
            return a0 + (a1 - a0) * t, b0 + (b1 - b0) * t, n0 + (n1 - n0) * t
    return CRT[-1][1:]


def crt_at(y, th, grow=0.0):
    a, b, n = crt_abn(y)
    sx, sz = math.cos(th), math.sin(th)
    lam = (abs(sx) ** n + abs(sz) ** n) ** (-1.0 / n)
    return Vector((SCX + (a + grow) * sx * lam, y, SCZ + (b + grow) * sz * lam))


def crt_normal(y, th):
    """A bulb point and the outward normal (from the neighbouring points)."""
    p = crt_at(y, th)
    dy = crt_at(y + 0.003, th) - crt_at(y - 0.003, th)
    dt = crt_at(y, th + 0.01) - crt_at(y, th - 0.01)
    nrm = dt.cross(dy).normalized()
    if nrm.dot(Vector((p.x - SCX, 0.0, p.z - SCZ))) < 0:
        nrm = -nrm
    return p, nrm


def build_crt(spec):
    lod, s = spec["lod"], spec["sides"]
    N = {0: 32, 1: 16, 2: 12}[lod]
    idx = {0: (0, 1, 2, 3, 4, 6), 1: (0, 2, 4, 6), 2: (0, 4, 6)}[lod]
    cr = P("crt_cone", "crt")
    vr = bridge_rings(cr, [se_ring(CRT[i][0], CRT[i][1], CRT[i][2], CRT[i][3], N, SCX, SCZ) for i in idx],
                      lambda i, c: (c.x - SCX, 0.0, c.z - SCZ))
    fan(cr, vr[-1], (SCX, CRT[-1][0], SCZ), (0, 1, 0))
    parts = [cr]
    fy = frame_at((SCX, 0.0, SCZ), "y")                      # h - depth y along the picture tube axis
    nk = P("crt_neck", "neck")
    lathe(nk, [(0.0145, CRT[-1][0] - 0.01), (0.0145, 0.200), (0.0120, 0.206), (0.0, 0.208)], s, fy)
    parts.append(nk)
    if lod < 2:
        # bulb band: a steel strap at the screen, four lugs on screws into the panel behind the mask
        bd = P("crt_band", "band")
        ya, yb = YBI + 0.0125, YBI + 0.036

        def ring_at(y, grow):
            a, b, n = crt_abn(y)
            return se_ring(y, a + grow, b + grow, n, N, SCX, SCZ)
        bridge_rings(bd, [ring_at(ya, 0.0035), ring_at(yb, 0.0035), ring_at(yb, 0.0006)],
                     lambda i, c: (c.x - SCX, 0.0, c.z - SCZ) if i == 0 else (0, 1, 0))
        parts.append(bd)
        # anode cap
        p, nrm = crt_normal(ANODE_Y, ANODE_TH)
        an = P("crt_anode", "rubber")
        lathe(an, [(0.0, -0.001), (0.019, -0.001), (0.0175, 0.004), (0.011, 0.0095), (0.005, 0.0125), (0.0, 0.013)],
              16 if lod == 0 else 8, frame_axis(tuple(p), nrm))
        parts.append(an)
        # deflection yoke: the housing widens toward the bulb
        yk = P("crt_yoke", "yoke")
        lathe(yk, [(0.0, 0.040), (0.054, 0.040), (0.056, 0.044), (0.050, 0.054), (0.037, 0.076), (0.031, 0.094),
                   (0.0, 0.094)] if lod == 0 else [(0.0, 0.040), (0.055, 0.040), (0.033, 0.090), (0.0, 0.090)],
              20 if lod == 0 else 10, fy)
        so = P("crt_socket", "black")
        lathe(so, [(0.0, 0.200), (0.0165, 0.200), (0.0175, 0.214), (0.0150, 0.226), (0.0, 0.226)],
              16 if lod == 0 else 8, fy)
        parts += [yk, so]
    if lod == 0:
        er = P("crt_ears", "band")
        sw = P("crt_ear_screws", "steel")
        for k in range(4):
            th = math.radians(45 + 90 * k)
            p_in = crt_at(YBI + 0.0135, th, 0.003)
            d = Vector((p_in.x - SCX, 0.0, p_in.z - SCZ)).normalized()
            p_out = p_in + d * 0.024
            yy = YBI + 0.0135
            box_to(er, (p_in.x, yy, p_in.z), (p_out.x, yy, p_out.z), 0.016, 0.003, up=(0, 1, 0))
            q = p_out - d * 0.008
            screw(sw, (q.x, YBI + 0.015, q.z), "y", 0.0042)
        # copper windings behind the yoke housing, a clamp with a screw, convergence rings with tabs
        cu = P("crt_windings", "copper")
        lathe(cu, [(0.0300, 0.093), (0.0400, 0.0945), (0.0425, 0.1005), (0.0370, 0.1075), (0.0290, 0.1060)], 16, fy,
              closed=True)
        bk = P("crt_rings", "black")
        lathe(bk, [(0.0152, 0.112), (0.0195, 0.112), (0.0195, 0.121), (0.0152, 0.121)], 12, fy, closed=True)
        box_to(bk, (SCX, 0.1165, SCZ + 0.019), (SCX, 0.1165, SCZ + 0.028), 0.007, 0.006, up=(0, 1, 0))
        for k, y0 in enumerate((0.128,)):
            lathe(bk, [(0.0152, y0), (0.0265, y0), (0.0265, y0 + 0.004), (0.0152, y0 + 0.004)], 12, fy, closed=True)
            a = math.radians(70 + 40 * k)
            box_to(bk, (SCX + 0.025 * math.cos(a), y0 + 0.002, SCZ + 0.025 * math.sin(a)),
                   (SCX + 0.035 * math.cos(a), y0 + 0.002, SCZ + 0.035 * math.sin(a)), 0.006, 0.004, up=(0, 1, 0))
        # socket board at the end of the neck
        sb = P("crt_socket_board", "board_plain")
        lathe(sb, [(0.0, 0.226), (0.031, 0.226), (0.031, 0.2285), (0.0, 0.2285)], 20, fy)
        cp = P("crt_socket_parts", "res")
        for k in range(4):
            a = math.radians(30 + 90 * k)
            g.cyl(cp, (SCX + 0.022 * math.cos(a), 0.2304, SCZ + 0.022 * math.sin(a)), "x", 0.0018, 0.009, 6)
        parts += [er, sw, cu, bk, sb, cp]
    return parts


# =============================================================================
# Chassis on the bottom: transformer, tubes, electrolytics, flyback; boards; speaker and PTK
# =============================================================================
def build_chassis(spec):
    lod = spec["lod"]
    x0, x1, y0, y1 = CHASSIS
    z0 = ZB
    cs = P("chassis", "chassis")
    g.box(cs, x0, x1, y0, y1, z0, z0 + 0.003)
    parts = [cs]
    if lod == 2:
        g.box(cs, -0.115, -0.025, 0.115, 0.215, z0 + 0.003, z0 + 0.078)
        return parts
    g.box(cs, x0, x1, y1 - 0.003, y1, z0 + 0.003, z0 + 0.030)                      # flange at the back
    # power transformer: iron stack, a coil in varnished cloth, tie angles with nuts
    tc = P("trans_core", "core")
    g.box(tc, -0.115, -0.025, 0.135, 0.195, z0 + 0.003, z0 + 0.078, **(dict(r=0.0015, seg=1) if lod == 0 else {}))
    tw = P("trans_coil", "paper")
    g.box(tw, -0.097, -0.043, 0.115, 0.215, z0 + 0.012, z0 + 0.066, **(dict(r=0.004, seg=2) if lod == 0 else {}))
    parts += [tc, tw]
    # tubes: socket, bulb (glass, a silver getter on top); two under aluminium shields
    gl, gt, sk, shd = P("tubes_glass", "tube"), P("tubes_getter", "getter"), P("tube_sockets", "black"), \
        P("tube_shields", "alu")
    for x, y, h, shield in TUBES:
        fz = frame_at((x, y, z0 + 0.003), "z")
        zb = 0.009
        if lod == 0:
            lathe(sk, [(0.0165, 0.0), (0.0165, 0.007), (0.0, 0.009)], 8, fz)
        else:
            g.cyl(sk, (x, y, z0 + 0.0075), "z", 0.016, 0.009, 6)
        if shield:
            if lod == 0:
                lathe(shd, [(0.0, zb), (0.0155, zb), (0.0155, zb + 0.008), (0.0135, zb + 0.009), (0.0135, zb + h),
                            (0.0115, zb + h + 0.006), (0.0, zb + h + 0.007)], 10, fz)
            else:
                g.cyl(shd, (x, y, z0 + 0.003 + zb + h / 2), "z", 0.0135, h, 6)
        elif lod == 0:
            lathe(gl, [(0.0108, zb), (0.0115, zb + 0.003), (0.0115, zb + h - 0.014)], 8, fz)
            lathe(gt, [(0.0115, zb + h - 0.014), (0.0085, zb + h - 0.003), (0.0030, zb + h + 0.0025),
                       (0.0, zb + h + 0.0035)], 8, fz)
        else:
            g.cyl(gl, (x, y, z0 + 0.003 + zb + h / 2), "z", 0.0115, h, 6)
    parts += [gl, gt, sk, shd]
    # flyback in a perforated cage, a kenotron on the lid
    fx0, fx1, fy0, fy1 = FLY
    fc = P("flyback_cage", "grille_v")
    g.box(fc, fx0, fx1, fy0, fy1, z0 + 0.003, z0 + FLY_H)
    parts.append(fc)
    if lod == 0:
        tb = P("trans_brackets", "steel")
        for ya, yb in ((0.131, 0.139), (0.191, 0.199)):
            g.box(tb, -0.119, -0.021, ya, yb, z0 + 0.074, z0 + 0.080)
            for x in (-0.112, -0.028):
                g.cyl(tb, (x, (ya + yb) / 2, z0 + 0.083), "z", 0.0042, 0.006, 6)
        ec = P("chassis_caps", "alu")
        for x, y, h in CAPS:
            lathe(ec, [(0.0170, 0.0), (0.0170, h - 0.007), (0.0158, h - 0.0055), (0.0170, h - 0.004), (0.0, h + 0.001)],
                  10, frame_at((x, y, z0 + 0.003), "z"))
        ft = P("flyback_top", "chassis")
        g.box(ft, fx0 - 0.002, fx1 + 0.002, fy0 - 0.002, fy1 + 0.002, z0 + FLY_H, z0 + FLY_H + 0.002)
        fz = frame_at(((fx0 + fx1) / 2, (fy0 + fy1) / 2, z0 + FLY_H + 0.002), "z")
        lathe(sk, [(0.0, 0.0), (0.012, 0.0), (0.012, 0.007), (0.0, 0.007)], 10, fz)
        lathe(gl, [(0.0, 0.007), (0.0085, 0.007), (0.0090, 0.010), (0.0090, 0.030)], 10, fz)
        lathe(gt, [(0.0090, 0.030), (0.0078, 0.037), (0.0040, 0.0405), (0.0, 0.042)], 10, fz)
        # on the flange: the power cord inlet and a fuse holder
        bf = P("chassis_back_parts", "black")
        for x in (-0.30, -0.20):
            lathe(bf, [(0.0075, 0.0), (0.0075, 0.010), (0.0055, 0.016), (0.0, 0.016)], 8,
                  frame_at((x, y1, z0 + 0.017), "y"))
        parts += [tb, ec, ft, bf]
    return parts


def build_boards(spec):
    """Laminate boards facing the removed wall, in corners; at the near LOD - parts on the board."""
    lod = spec["lod"]
    if lod == 2:
        return []
    pb = P("boards", "pcb")
    parts = [pb]
    for x0, x1, z0, z1, y in (PCB_L, PCB_R):
        g.box(pb, x0, x1, y - 0.003, y, z0, z1)
    if lod > 0:
        return parts
    fr = P("board_frames", "steel")
    for x0, x1, z0, z1, y in (PCB_L, PCB_R):
        for xa, xb in ((x0 - 0.008, x0), (x1, x1 + 0.008)):
            zf = ZB + 0.003 if xa < CHASSIS[1] else ZB
            g.box(fr, xa, xb, y - 0.030, y - 0.003, zf, z1)
    parts.append(fr)
    kinds = {k: P("board_" + k, k) for k in ("cap_blue", "cap_orange", "res", "alu", "core")}
    for (x0, x1, z0, z1, y), seed in ((PCB_L, 3), (PCB_R, 5)):
        rnd = random.Random(seed)
        placed = []
        # a large electrolytic, coil cans, resistors, discs, electrolytics
        todo = [("big", 0.009)] + [("can", 0.009)] * 2 + [("res", 0.007)] * 4 + [("disc", 0.005)] * 2 + \
            [("ecap", 0.007)] * 3 + ([("trafo", 0.016)] if seed == 5 else [])
        for kind, rr in todo:
            for _ in range(40):
                x = rnd.uniform(x0 + 0.012 + rr, x1 - 0.012 - rr)
                z = rnd.uniform(z0 + 0.035 + rr, z1 - 0.012 - rr)
                if all((x - px) ** 2 + (z - pz) ** 2 > (rr + pr + 0.004) ** 2 for px, pz, pr in placed):
                    break
            placed.append((x, z, rr))
            if kind == "big":
                g.cyl(kinds["cap_blue"], (x, y + 0.015, z), "y", 0.009, 0.030, 10)
            elif kind == "ecap":
                h = rnd.uniform(0.010, 0.018)
                g.cyl(kinds["cap_blue"], (x, y + h / 2, z), "y", rnd.uniform(0.0045, 0.0065), h, 8)
            elif kind == "can":
                g.box(kinds["alu"], x - 0.006, x + 0.006, y, y + 0.018, z - 0.006, z + 0.006)
            elif kind == "res":
                g.cyl(kinds["res"], (x, y + 0.0035, z), "x", 0.0019, 0.011, 6)
            elif kind == "disc":
                g.cyl(kinds["cap_orange"], (x, y + 0.006, z), "x", 0.0045, 0.002, 8)
            else:
                g.box(kinds["core"], x - 0.015, x + 0.015, y, y + 0.022, z - 0.012, z + 0.012)
    parts += list(kinds.values())
    return parts


def build_speaker_tuner(spec):
    """Behind the strip: the speaker facing the grille (basket, magnet), the PTK behind the channel knob,
    variable resistors behind the small knobs."""
    lod = spec["lod"]
    if lod == 2:
        return []
    sx, sz, sr = SPEAKER
    fy = frame_at((sx, YM + 0.04, sz), "y")
    bk = P("speaker_basket", "speaker")
    mg = P("speaker_magnet", "magnet")
    if lod == 0:
        lathe(bk, [(0.0, 0.0), (sr + 0.002, 0.0), (sr + 0.002, 0.004), (sr - 0.008, 0.007), (0.031, 0.040),
                   (0.027, 0.046), (0.0, 0.046)], 16, fy)
        lathe(mg, [(0.030, 0.046), (0.031, 0.049), (0.031, 0.066), (0.028, 0.069), (0.0, 0.069)], 16, fy)
    else:
        lathe(bk, [(0.0, 0.0), (sr, 0.0), (0.03, 0.045), (0.0, 0.045)], 8, fy)
        lathe(mg, [(0.0, 0.045), (0.03, 0.045), (0.03, 0.066), (0.0, 0.066)], 8, fy)
    x0, x1, y0, y1, z0, z1 = TUNER
    tu = P("tuner", "tin")
    g.box(tu, x0, x1, y0, y1, z0, z1, **(dict(r=0.002, seg=1) if lod == 0 else {}))
    parts = [bk, mg, tu]
    if lod == 0:
        tk = P("tuner_parts", "black")
        for k, z in enumerate((z0 + 0.025, z0 + 0.045, z0 + 0.065)):
            g.cyl(tk, (x0 + 0.03 + 0.025 * k, y1 + 0.0008, z), "y", 0.004, 0.002, 8)       # trimmer windows
        g.box(tk, x0 + 0.004, x1 - 0.004, y0 + 0.055, y0 + 0.057, z1 - 0.0005, z1 + 0.0004)   # lid seam
        g.box(tk, sx - 0.012, sx + 0.012, YM + 0.058, YM + 0.064, sz - 0.047, sz - 0.040)   # speaker tabs
        sw = P("tuner_screws", "steel")
        for x in (x0 + 0.010, x1 - 0.010):
            for y in (y0 + 0.012, y1 - 0.012):
                screw(sw, (x, y, z1), "z", 0.003)
        pt = P("pots", "alu")
        for x, z in SMALL:
            g.cyl(pt, (x, YM + 0.04 + 0.006, z), "y", 0.012, 0.012, 12)
        parts += [tk, sw, pt]
    return parts


# =============================================================================
# Detector block: box, panel, microammeter (needle - ozl_needle), lamp
# (ozl_lamp), toggle, knob; on the roof - SBM-20 counters
# =============================================================================
def build_detector(spec):
    lod = spec["lod"]
    parts = []
    db = P("det_box", "det")
    g.box(db, DX0, DX1, DY0, DY1, DZ0, DZ1, **{0: dict(r=0.004, seg=2), 1: dict(r=0.003, seg=1)}.get(lod, {}))
    parts.append(db)
    if lod == 2:
        g.box(db, DX0, DX1, DY0, DY1, ZB, DZ0)
    if lod == 0:
        ft = P("det_feet", "rubber")
        for x in (DX0 + 0.02, DX1 - 0.02):
            for y in (DY0 + 0.02, DY1 - 0.02):
                g.cyl(ft, (x, y, (ZB + DZ0) / 2 + 0.0005), "z", 0.008, DZ0 - ZB + 0.001, 6)
        st = P("det_screws", "steel")
        for x in (PLATE[0] + 0.006, PLATE[1] - 0.006):
            for z in (PLATE[2] + 0.006, PLATE[3] - 0.006):
                screw(st, (x, YF, z), "y", 0.0028)
        parts += [ft, st]
    if lod < 2:
        pl = P("det_plate", "det_panel")
        g.box(pl, PLATE[0], PLATE[1], DY1 - 0.0005, YF, PLATE[2], PLATE[3], **(dict(r=0.0008, seg=1) if lod == 0 else {}))
        parts.append(pl)
    # microammeter: a frame with a window (face, the window rim inward), scale, needle
    bz = P("meter_bezel", "bezel")
    wcx, wcz = (WIN[0] + WIN[1]) / 2, (WIN[2] + WIN[3]) / 2
    if lod < 2:
        n = 3 if lod == 0 else 1
        rings = [rr_xz(MX, MZ, 0.040, 0.040, 0.004, n, YF), rr_xz(MX, MZ, 0.040, 0.040, 0.004, n, YF + 0.006),
                 rr_xz(wcx, wcz, DIAL_W / 2, DIAL_H / 2, 0.0025, n, YF + 0.006),
                 rr_xz(wcx, wcz, DIAL_W / 2, DIAL_H / 2, 0.0025, n, YF + 0.0025)]
        bridge_rings(bz, rings, lambda i, c: [(c.x - MX, 0.0, c.z - MZ), (0, 1, 0), (wcx - c.x, 0.0, wcz - c.z)][i])
        dy = DIAL_Y
    else:
        g.box(bz, MX - 0.04, MX + 0.04, YF, YF + 0.003, MZ - 0.04, MZ + 0.04)
        dy = YF + 0.0034
    dl = P("meter_dial", "dial")
    g.box(dl, WIN[0], WIN[1], dy - 0.0008, dy, WIN[2], WIN[3])
    parts += [bz, dl]
    # needle: zero is on the left seen from behind (+X); bone ozl_needle, the axis toward the person (+Y, NEEDLE_AXIS)
    nd = P("meter_needle", "needle", group=SEL_NEEDLE)
    d0 = Vector((math.cos(math.radians(METER_REST)), 0.0, math.sin(math.radians(METER_REST))))
    o = Vector(NEEDLE_O) + Vector((0.0, 0.0 if lod < 2 else 0.0008, 0.0))
    nrm = Vector((0.0, 1.0, 0.0))
    fr = g.Frame(o, d0, nrm.cross(d0), nrm)
    tip = METER_TIP
    blade = [(-0.008, -0.0012), (0.004, -0.0009), (tip, -0.00025), (tip + 0.001, 0.0), (tip, 0.00025),
             (0.004, 0.0009), (-0.008, 0.0012)] if lod == 0 else [(0.004, -0.0008), (tip, -0.0008), (tip, 0.0008),
                                                                  (0.004, 0.0008)]
    g.prism(nd, blade, (0, 1), -0.0003, 0.0003, frame=fr)
    parts.append(nd)
    # lamp in a chromed bezel
    fl = frame_at((LAMP[0], YF, LAMP[1]), "y")
    ln = P("det_lamp", "lamp", group=SEL_LAMP)
    if lod == 0:
        lathe(ln, [(0.0, -0.001), (0.0064, -0.001), (0.0064, 0.0025), (0.0056, 0.0058), (0.0032, 0.0078),
                   (0.0, 0.0084)], 12, fl)
    else:
        lathe(ln, [(0.0, 0.0), (0.0064, 0.0), (0.0064, 0.004), (0.0, 0.007)], 8 if lod == 1 else 6, fl)
    parts.append(ln)
    if lod == 2:
        return parts
    rg = P("det_lamp_ring", "chrome")
    if lod == 0:
        lathe(rg, [(0.0062, 0.0), (0.0100, 0.0), (0.0100, 0.0030), (0.0088, 0.0055), (0.0062, 0.0055)], 12, fl,
              closed=True)
    else:
        lathe(rg, [(0.0062, 0.0), (0.010, 0.0), (0.010, 0.004), (0.0062, 0.004)], 8, fl, closed=True)
    # toggle: bushing, nut, lever down (off); a sensitivity knob with a mark
    tg = P("det_toggle", "chrome")
    ftg = frame_at((TOGGLE[0], YF, TOGGLE[1]), "y")
    lathe(tg, [(0.0, 0.0), (0.0058, 0.0), (0.0058, 0.009), (0.0, 0.009)], 8 if lod == 0 else 6, ftg)
    kb = P("det_knob", "bezel")
    mk = P("det_knob_mark", "mark") if lod == 0 else None
    knob(kb, mk, (KNOB[0], YF, KNOB[1]), "y", 0.016, 0.011, 0.012, lod)
    parts += [rg, tg, kb] + ([mk] if mk is not None else [])
    if lod == 0:
        g.prism(tg, hexagon(0.0080), (0, 1), 0.0, 0.0035, frame=ftg)
        d = Vector((0.0, math.cos(math.radians(25.0)), -math.sin(math.radians(25.0))))
        lathe(tg, [(0.0, -0.001), (0.0026, -0.001), (0.0018, 0.010), (0.0021, 0.017), (0.0026, 0.0195), (0.0018, 0.0225),
                   (0.0, 0.0235)], 6, frame_axis((TOGGLE[0], YF + 0.009, TOGGLE[1]), d))
    # on the block roof: a laminate board on posts, two SBM-20 in holders
    bx0, bx1, by0, by1 = GM_BOARD
    gb = P("gm_board", "gm_board")
    g.box(gb, bx0, bx1, by0, by1, DZ1 + 0.006, DZ1 + 0.0075)
    tbm, tcp = P("gm_tubes", "gm"), P("gm_caps", "steel")
    zc = DZ1 + 0.0155
    xa, xb = GM_X
    for y in GM_Y:
        g.cyl(tbm, ((xa + xb) / 2, y, zc), "x", 0.005, xb - xa - 0.012, 10 if lod == 0 else 6)
        for x in (xa + 0.003, xb - 0.003):
            g.cyl(tcp, (x, y, zc), "x", 0.0055, 0.006, 8 if lod == 0 else 6)
    parts += [gb, tbm, tcp]
    if lod == 0:
        so = P("gm_standoffs", "brass")
        for x in (bx0 + 0.006, bx1 - 0.006):
            for y in (by0 + 0.006, by1 - 0.006):
                g.cyl(so, (x, y, DZ1 + 0.003), "z", 0.0025, 0.006, 6)
        for y in GM_Y:
            for x in (xa + 0.003, xb - 0.003):
                g.box(so, x - 0.004, x + 0.004, y - 0.0068, y - 0.0058, DZ1 + 0.0075, zc + 0.002)
                g.box(so, x - 0.004, x + 0.004, y + 0.0058, y + 0.0068, DZ1 + 0.0075, zc + 0.002)
                g.box(so, x - 0.004, x + 0.004, y - 0.0068, y + 0.0068, DZ1 + 0.0075, DZ1 + 0.0085)
        gd = P("det_glands", "black")
        for x, y in (GLAND_PICK, GLAND_ANT, GLAND_SIG):
            lathe(gd, [(0.0065, 0.0), (0.0065, 0.004), (0.0045, 0.012), (0.0, 0.012)], 6,
                  frame_at((x, y, DZ1), "z"))
        parts += [so, gd]
    return parts


# =============================================================================
# Wires and cables: all smooth curves
# =============================================================================
def build_wires(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    # to the board with a coil on the roof and to the antenna: up the right rear corner, over the rear roof edge
    px, py = PICKUP[0], PICKUP[1] + PICKUP[3] / 2
    zt = ZT + PICKUP[4]
    pick = [(GLAND_PICK[0], GLAND_PICK[1], DZ1 + 0.012), (0.318, 0.230, DZ1 + 0.045), (0.336, 0.238, 0.72),
            (0.338, Y1 + 0.0045, 0.915), (0.335, Y1 + 0.004, ZT - 0.004), (0.330, Y1 - 0.003, ZT + 0.0029),
            (0.300, Y1 - 0.030, ZT + 0.0029), (0.10, 0.205, ZT + 0.0029), (-0.08, 0.150, ZT + 0.0029),
            (px + 0.010, py + 0.014, ZT + 0.0029), (px + 0.006, py + 0.004, ZT + 0.008),
            (px + 0.006, py - 0.0005, zt + 0.004)]
    parts.append(cable("cable_pickup", "wire_grey", pick, 0.0028, lod, sides=5 if lod == 0 else None))
    ab = ANT[1] + ANT_BASE[1] / 2
    ant = [(GLAND_ANT[0], GLAND_ANT[1], DZ1 + 0.012), (0.324, 0.222, DZ1 + 0.06), (0.346, 0.236, 0.72),
           (0.346, Y1 + 0.0045, 0.915), (0.343, Y1 + 0.004, ZT - 0.004), (0.338, Y1 - 0.003, ZT + 0.0026),
           (0.310, Y1 - 0.024, ZT + 0.0026), (0.272, 0.176, ZT + 0.0026), (ANT[0] + 0.02, ab + 0.008, ZT + 0.0026),
           (ANT[0] + 0.02, ab + 0.001, ZT + 0.012)]
    parts.append(cable("cable_antenna", "wire_black", ant, 0.0025, lod, sides=5 if lod == 0 else None))
    # high-voltage wire: the anode cap - the kenotron on the flyback cage (from below under the board)
    p, nrm = crt_normal(ANODE_Y, ANODE_TH)
    top = p + nrm * 0.013
    fx, fy = (FLY[0] + FLY[1]) / 2, (FLY[2] + FLY[3]) / 2
    hv = [tuple(top), tuple(top + nrm * 0.02 + Vector((0.01, 0.01, 0.0))), (0.07, 0.0, 0.78), (0.085, 0.06, 0.66),
          (0.075, 0.11, 0.60), (fx, fy - 0.012, ZB + FLY_H + 0.032), (fx, fy, ZB + FLY_H + 0.046)]
    parts.append(cable("cable_hv", "wire_hv", hv, 0.0035, lod))
    # power cord: from the chassis inlet, down behind the cabinet, along the floor; the plug lies on the
    # floor: the axis at the body radius height, the cord rises to it slightly
    cord = [(-0.30, CHASSIS[3] + 0.016, ZB + 0.017), (-0.30, Y1 + 0.014, ZB + 0.012), (-0.305, Y1 + 0.034, ZS - 0.03),
            (-0.315, 0.290, 0.30), (-0.328, 0.300, 0.12), (-0.342, 0.318, 0.012), (-0.37, 0.345, 0.0035),
            (-0.405, 0.385, 0.0035), (-0.44, 0.43, 0.0152)]
    parts.append(cable("power_cord", "cord", cord, 0.0035, lod))
    end, prev = Vector(cord[-1]), Vector(cord[-2])
    d = end - prev
    d.z = 0.0
    d.normalize()
    pl = P("power_plug", "black")
    lathe(pl, [(0.0, -0.002), (0.0055, -0.002), (0.0115, 0.008), (0.0150, 0.012), (0.0150, 0.036), (0.0135, 0.040),
               (0.0, 0.040)], 10 if lod == 0 else 6, frame_axis(tuple(end), d))
    parts.append(pl)
    if lod > 0:
        return parts
    pn = P("power_pins", "chrome")
    side = d.cross(Vector((0, 0, 1))).normalized()
    for s in (-1, 1):
        a = end + d * 0.040 + side * (s * 0.0095)
        g.pipe(pn, [tuple(a), tuple(a + d * 0.019)], 0.002, 6)
    parts.append(pn)
    # block signal to the video amplifier board - three thin wires
    for k, reg in enumerate(("wire_red", "wire_white", "wire_black")):
        dx = (k - 1) * 0.003
        pts = [(GLAND_SIG[0] + dx, GLAND_SIG[1], DZ1 + 0.012), (0.142 + dx, 0.214, DZ1 + 0.04),
               (0.168 + dx, 0.16, 0.638), (0.185 + dx, 0.115, 0.652), (0.188 + dx, PCB_R[4] + 0.0015, 0.664)]
        parts.append(cable("wire_sig%d" % k, reg, pts, 0.0012, lod, sides=4))
    # from the neck socket to the boards
    for k, (reg, pts) in enumerate((
            ("wire_red", [(SCX - 0.012, 0.2295, SCZ + 0.004), (-0.11, 0.21, 0.70), (-0.15, 0.14, 0.715),
                          (-0.19, 0.08, 0.705), (-0.205, PCB_L[4] + 0.0015, 0.70)]),
            ("wire_white", [(SCX - 0.010, 0.2295, SCZ - 0.006), (-0.105, 0.21, 0.69), (-0.145, 0.14, 0.70),
                            (-0.185, 0.08, 0.69), (-0.20, PCB_L[4] + 0.0015, 0.686)]),
            ("wire_black", [(SCX + 0.012, 0.2295, SCZ + 0.004), (-0.03, 0.21, 0.74), (0.02, 0.15, 0.79),
                            (0.05, 0.11, 0.80), (0.06, PCB_R[4] + 0.0015, 0.80)]),
            ("wire_white", [(SCX + 0.010, 0.2295, SCZ - 0.006), (-0.026, 0.21, 0.735), (0.024, 0.15, 0.783),
                            (0.054, 0.11, 0.792), (0.064, PCB_R[4] + 0.0015, 0.792)]))):
        parts.append(cable("wire_neck%d" % k, reg, pts, 0.0011, lod, sides=4))
    # speaker and PTK - to the right board
    sx, sz, sr = SPEAKER
    for k, reg in enumerate(("wire_red", "wire_black")):
        dz = k * 0.004
        pts = [(sx - 0.004 + 0.006 * k, YM + 0.061, sz - 0.047), (0.27, -0.10, 0.775 + dz), (0.22, 0.03, 0.79 + dz),
               (0.192, 0.09, 0.80 + dz), (0.19, PCB_R[4] + 0.0015, 0.80 + dz)]
        parts.append(cable("wire_spk%d" % k, reg, pts, 0.0011, lod, sides=4))
    coax = [(0.29, TUNER[3] + 0.002, 0.63), (0.27, -0.03, 0.66), (0.20, 0.06, 0.73), (0.168, 0.095, 0.748),
            (0.165, PCB_R[4] + 0.002, 0.75)]
    parts.append(cable("cable_tuner", "wire_grey", coax, 0.002, lod))
    # insulating tape: the cables to the roof are tied together behind the rear edge
    tp = P("cable_tape", "tape")
    g.cyl(tp, (0.342, Y1 + 0.0045, 0.885), "z", 0.0078, 0.018, 10)
    parts.append(tp)
    return parts


# =============================================================================
# Stool
# =============================================================================
def leg_at(sx, sy, z):
    """Leg axis point (sx, sy = +-1) at height z: the legs are splayed toward the bottom."""
    zt = ZS - ZSEAT - 0.012
    k = (zt - z) / zt
    d = LEG_TOP + (LEG_BOT - LEG_TOP) * k
    return (sx * d, sy * d, z)


def build_stool(spec):
    lod, s = spec["lod"], spec["sides"]
    zb = ZS - ZSEAT
    st = P("stool_seat", "seat")
    if lod == 0:
        profile_xy(st, 0.0, 0.0, SEAT, SEAT, 0.025, 4, [(-0.003, 0.0), (0.0, 0.003), (0.0, ZSEAT - 0.003),
                                                         (-0.003, ZSEAT)], z0=zb)
    elif lod == 1:
        profile_xy(st, 0.0, 0.0, SEAT, SEAT, 0.025, 2, [(0.0, 0.0), (0.0, ZSEAT)], z0=zb)
    else:
        g.box(st, -SEAT, SEAT, -SEAT, SEAT, zb, ZS)
    fr = P("stool_frame", "stool")
    zt = zb - 0.012                                          # apron axis from a 20 x 20 profile
    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    if lod < 2:
        for i in range(4):
            box_to(fr, leg_at(*corners[i], zt), leg_at(*corners[(i + 1) % 4], zt), 0.02, 0.02, up=(0, 0, 1))
    for sx, sy in corners:
        g.pipe(fr, [leg_at(sx, sy, zt + 0.008), leg_at(sx, sy, 0.012)], 0.011, {0: 10, 1: 8, 2: 4}[lod])
    if lod < 2:
        for i in range(4):
            g.pipe(fr, [leg_at(*corners[i], RING_Z), leg_at(*corners[(i + 1) % 4], RING_Z)], 0.008, 6 if lod == 0 else 4)
    parts = [st, fr]
    if lod < 2:
        # rubber caps along the leg axis
        rb = P("stool_feet", "rubber")
        for sx, sy in corners:
            a, b = Vector(leg_at(sx, sy, 0.0)), Vector(leg_at(sx, sy, 0.1))
            d = (b - a).normalized()
            prof = [(0.0, 0.0), (0.0125, 0.0), (0.0135, 0.004), (0.0132, 0.026), (0.0118, 0.030), (0.0, 0.030)]
            lathe(rb, prof if lod == 0 else prof[::2] + [prof[-1]], 8 if lod == 0 else 6,
                  frame_axis(tuple(a + Vector((0.0, 0.0, 0.0012))), d))
        parts.append(rb)
    return parts


# =============================================================================
# Roof: a board with a coil and a tray, a mug, a loop antenna on a motor (ozl_work)
# =============================================================================
def build_pickup(spec):
    """Plywood board, a copper winding along the edge (the pickup coil under the sample), two strips of
    insulating tape, a terminal block at the rear edge."""
    lod = spec["lod"]
    cx, cy, L, W, H = PICKUP
    pb = P("pickup_board", "ply")
    if lod == 0:
        profile_xy(pb, cx, cy, L / 2, W / 2, 0.010, 3, [(-0.0015, 0.0), (0.0, 0.0015), (0.0, H - 0.0015),
                                                        (-0.0015, H)], z0=ZT)
    elif lod == 1:
        profile_xy(pb, cx, cy, L / 2, W / 2, 0.010, 1, [(0.0, 0.0), (0.0, H)], z0=ZT)
    else:
        g.box(pb, cx - L / 2, cx + L / 2, cy - W / 2, cy + W / 2, ZT, ZT + H)
    parts = [pb]
    if lod == 0:
        cu = P("pickup_coil", "copper")
        band_xy(cu, cx, cy, L / 2, W / 2, 0.010, 3, [(0.0, 0.003), (0.0016, 0.0036), (0.0024, 0.006), (0.0016, 0.0084),
                                                     (0.0, 0.009)], z0=ZT)
        tp = P("pickup_tape", "tape")
        for s in (-1, 1):
            g.box(tp, cx + s * (L / 2) - 0.004, cx + s * (L / 2) + 0.004, cy - 0.014, cy + 0.014, ZT + 0.0015, ZT + 0.0105)
        tb = P("pickup_terminal", "black")
        g.box(tb, cx - 0.016, cx + 0.016, cy + W / 2 - 0.014, cy + W / 2 - 0.001, ZT + H, ZT + H + 0.009, r=0.0015, seg=1)
        sw = P("pickup_screws", "steel")
        for s in (-1, 1):
            screw(sw, (cx + s * 0.009, cy + W / 2 - 0.0075, ZT + H + 0.009), "z", 0.0032)
        parts += [cu, tp, tb, sw]
    return parts


def build_tray(spec):
    """Photo tray of enamelled steel: rounded corners, sloped walls, a rolled rim."""
    lod = spec["lod"]
    cx, cy, L, W, H = TRAY
    z0 = ZT + PICKUP[4]
    tr = P("tray", "tray")
    if lod == 0:
        profile_xy(tr, cx, cy, L / 2, W / 2, 0.018, 3,
                   [(-0.007, 0.0), (-0.005, 0.0015), (0.0, H - 0.002), (0.0025, H + 0.0005), (0.0015, H + 0.0022),
                    (-0.0012, H + 0.0008), (-0.0015, H - 0.002), (-0.008, 0.003), (-0.0095, 0.0018)], z0=z0)
    elif lod == 1:
        profile_xy(tr, cx, cy, L / 2, W / 2, 0.018, 2, [(-0.007, 0.0), (0.0, H), (-0.0015, H), (-0.0085, 0.002)], z0=z0)
    else:
        g.box(tr, cx - L / 2, cx + L / 2, cy - W / 2, cy + W / 2, z0, z0 + H)
    return [tr]


def build_mug(spec):
    """Enamelled mug: rolled edge, tea inside, a strap handle."""
    lod = spec["lod"]
    if lod == 2:
        return []
    cx, cy = MUG_C
    fr = frame_at((cx, cy, ZT), "z")
    mg = P("mug", "mug")
    if lod == 0:
        lathe(mg, [(0.0, 0.0), (0.036, 0.0), (0.0400, 0.0025), (MUG_R, 0.010), (MUG_R, 0.079), (0.0436, 0.0815),
                   (0.0426, 0.0848), (0.0404, 0.0828), (0.0402, 0.062)], 16, fr)
        hp = spline([(cx - 0.0415, cy, ZT + 0.072), (cx - 0.060, cy, ZT + 0.071), (cx - 0.066, cy, ZT + 0.050),
                     (cx - 0.060, cy, ZT + 0.028), (cx - 0.0415, cy, ZT + 0.022)], 2)
        g.tube_var(mg, hp, [(0.0055, 0.0022)] * len(hp), 6)
    else:
        lathe(mg, [(0.0, 0.0), (0.040, 0.0), (MUG_R, MUG_H), (0.040, MUG_H), (0.040, 0.062)], 8, fr)
        g.pipe(mg, [(cx - 0.041, cy, ZT + 0.07), (cx - 0.064, cy, ZT + 0.06), (cx - 0.064, cy, ZT + 0.035),
                    (cx - 0.041, cy, ZT + 0.024)], 0.004, 4)
    tea = P("mug_tea", "tea")
    g.cyl(tea, (cx, cy, ZT + 0.0624), "z", 0.0400, 0.0008, 16 if lod == 0 else 8)
    return [mg, tea]


def build_antenna(spec):
    """Loop antenna on a rotary motor: a bakelite box, the motor housing; the hub, the post, the input box
    and the copper-wire loop in the xz plane with insulating tape turn (bone ozl_work)."""
    lod = spec["lod"]
    ax, ay = ANT
    bl, bw, bh = ANT_BASE
    bs = P("ant_base", "ant_base")
    g.box(bs, ax - bl / 2, ax + bl / 2, ay - bw / 2, ay + bw / 2, ZT, ZT + bh, **(dict(r=0.005, seg=2) if lod == 0 else {}))
    mt = P("ant_motor", "motor")
    zm = ZT + bh
    if lod == 0:
        lathe(mt, [(0.0, 0.0), (0.022, 0.0), (0.022, 0.018), (0.019, 0.022), (0.0, 0.022)], 16, frame_at((ax, ay, zm), "z"))
    else:
        g.cyl(mt, (ax, ay, zm + 0.011), "z", 0.022, 0.022, 8 if lod == 1 else 6)
    parts = [bs, mt]
    hub = P("ant_hub", "black", group=SEL_ANT)
    g.cyl(hub, (ax, ay, zm + 0.026), "z", 0.010, 0.008, 12 if lod == 0 else 6)
    zr0 = ANT_Z - ANT_R
    g.pipe(hub, [(ax, ay, zm + 0.029), (ax, ay, zr0 - 0.010)], 0.004, 8 if lod == 0 else 4)
    g.box(hub, ax - 0.013, ax + 0.013, ay - 0.009, ay + 0.009, zr0 - 0.012, zr0 + 0.006,
          **(dict(r=0.002, seg=1) if lod == 0 else {}))
    rg = P("ant_loop", "ant", group=SEL_ANT)
    fr = g.Frame((ax, ay, ANT_Z), (1, 0, 0), (0, 0, 1), (0, -1, 0))
    torus(rg, fr, ANT_R, 0.0045 if lod < 2 else 0.006, {0: 30, 1: 12, 2: 8}[lod], {0: 5, 1: 4, 2: 3}[lod])
    parts += [hub, rg]
    if lod == 0:
        tp = P("ant_tape", "tape", group=SEL_ANT)
        for deg in (-62.0, -118.0, 30.0):
            a = math.radians(deg)
            c = fr.p(ANT_R * math.cos(a), ANT_R * math.sin(a), 0.0)
            t = fr.u * -math.sin(a) + fr.v * math.cos(a)
            g.cyl(tp, (0.0, 0.0, 0.0), "z", 0.0062, 0.012, 8, frame=frame_axis(tuple(c), t))
        sw = P("ant_screws", "steel")
        for sx in (-1, 1):
            screw(sw, (ax + sx * (bl / 2 - 0.010), ay - bw / 2 + 0.010, ZT + bh), "z", 0.0032)
        parts += [tp, sw]
    return parts


def build_lod(spec):
    parts = build_cabinet(spec) + build_front(spec) + build_crt(spec) + build_chassis(spec) + build_boards(spec)
    parts += build_speaker_tuner(spec) + build_detector(spec) + build_wires(spec) + build_stool(spec)
    parts += build_pickup(spec) + build_tray(spec) + build_mug(spec) + build_antenna(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """Two convex pieces: the stool and the TV cabinet with the knobs. The roof props have no collision."""
    wood = kx.PEN + r"\wood.rvmat"
    metal = kx.PEN + r"\metalplate.rvmat"
    stool = kx.box_pts(-LEG_BOT - 0.014, LEG_BOT + 0.014, -LEG_BOT - 0.014, LEG_BOT + 0.014, 0.0, ZS - 0.002)
    tv = kx.box_pts(X0, X1 + 0.02, YM - 0.038, Y1, ZS, ZT)
    comps = [(stool, metal), (tv, wood)]
    memory = {
        "invView": [(0.0, -2.2, 1.0)],
        "ce_center": [(0.0, 0.0, 0.55)],
        "ce_radius": [(0.75, 0.0, 0.55)],
        # bone axes: antenna - vertical along the post; needle - from the axis to the person behind the TV set
        # (+Y: clockwise turn seen from behind; NEEDLE_AXIS above)
        "ozl_work_axis": [(ANT[0], ANT[1], ZT + ANT_BASE[2]), (ANT[0], ANT[1], ANT_Z)],
        "ozl_needle_axis": NEEDLE_AXIS,
    }
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 40.0, memory, bbox


# the first ones are for the --look preview: overview, the open back, the detector block close up (also in
# "work": the screen, the antenna turned, the lamp lit, the needle deflected), the roof, the screen with the knobs
SHOTS = [
    ("front", (-1.0, -2.3, 1.35), (0.0, 0.0, 0.66), 30),
    ("back", (0.85, 1.45, 1.20), (-0.02, 0.10, 0.68), 32),
    ("detector", (0.42, 0.66, 0.78), (0.225, 0.235, 0.545), 40),
    ("roof", (0.55, -0.85, 1.55), (0.0, 0.0, ZT + 0.06), 32),
    ("screen", (-0.35, -1.05, 0.95), (-0.03, -0.2, 0.71), 34),
    ("right", (1.9, -1.0, 1.0), (0.0, 0.0, 0.6), 30),
    ("under", (-0.9, -1.2, 0.35), (0.0, 0.0, 0.25), 30),
]

M.look_shots = (5, 3)
M.run(build_lod, collision, SHOTS, row_step=1.0, row_shot=((1.0, -4.2, 1.4), (1.0, 0, 0.6)))
