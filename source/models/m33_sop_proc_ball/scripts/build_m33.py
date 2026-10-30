"""M33 - the SOP ballistic rack case: the Ballistic Sample Analyzer (OZL_Sop_Proc_Ball). An
analyzer: cargo 4x4, no modules. The sample socket is a pulled-out tray drawer with a
cradle for cartridges.

    blender --background --python build_m33.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: make_decals.py with the system Python (meter scales, displays,
stencils). Positions are in layout.py (shared with make_decals.py).

The device: an army measuring complex, still of Soviet make, in a steel case-rack
0.60 x 1.20 x 0.60 m with rims for lids at the front and back; both lids are off (the front
one leans on the left side). Inside - a 19" rack with five units with grey panels; a
velocity sensor on a short tripod is connected to them with cables. There is no exact
"ballistic complex in a case" in open sources; it is assembled from analogs:
- the body - a Soviet army instrument in a steel case with a removable lid, a rim, "frog"
  latches, corner pieces and folding handles (reference photo: Wikimedia Commons
  File:Moscow_-_Bunker_703_(34094).jpg, CC0); skids under the bottom and ribs on the sides
  as on transport spares boxes;
- the rack - 19" per GOST 28601.2-90 (IEC 60297): panel 482.6 mm, 1U pitch 44.45 mm; the
  units from the bottom up: power 4U, sample drawer 3U, time meter 5U, sensor amplifiers
  4U, control 5U, spares shelf 3U;
- the unit panels - grey-green enamel of Soviet military equipment with chrome handles, a
  dial meter in a square black case, toggles, lamps and fuse caps (a Soviet test set);
  meters - an M4200 class case 80 x 80 mm (window 66 x 56, estimated from photos), a
  90 degree scale;
- the displays - red seven-segment indicators of the late 80s (ALS324 class) behind a red
  filter;
- the velocity sensor - inductive (two solenoid coils on one tube, base 0.30 m - the bullet
  passes through the tube); on a short tripod with telescopic legs, the head at 0.52 m. It
  does not repeat M24 (the Duty stand with a console and a rail) or M28 (Freedom's optical
  frames on tripods - only an analog in how it stands on a tripod).

SOP look (as M32 - the first SOP model): olive, heavily worn - rim edges, corner pieces,
handles, skids; a red-brown primer under the worn olive, then metal; touched up in places;
no rust (the build_worn builder comes from M32). The unit panels are grey, worn at the
handles. Unreadable details (no legible text): the case number by stencil and white stripes
on the side, a marking frame and "up" arrows on the lid, blank aluminium nameplates, a lead
seal on the control unit; digits of the scales and displays.

Look: "dayz"; no angular parts - the case corner pieces are rounded and on rivets, the ribs
are half-round, the folding handles and panel handles are brackets with rounded bends on
bosses, "frog" latches with a hinge, a lever and a loop, meter and display frames with a
chamfer, knobs with fluting and a tick, toggles with a nut, a washer and a conical lever,
lamps are convex lenses in ribbed rims, connectors of the 2RM class (a flange on screws, a
knurled coupling nut, a plug, a rubber boot), slotted panel screws; the cables are smooth
curves (they sag from the connectors, lie on the floor, rise to the coils); the tripod has
a cast head, leg hinges, flag clamps and rubber heels; the sensor has grooved coils, a
saddle with a collar and a nameplate; the spare cable coil is a spiral with a plug at the
tail; the cradle is a rubber bar with V-grooves. Small items are vanilla proxy things
(kvanilla): on the case roof a sheet of paper with a pen, a box and loose 7.62 x 39
cartridges, on the spares shelf insulating tape and pliers, in the sample drawer loose
cartridges. At the back of the power unit - an 80 mm fan with a grille (spins while working).

The two displays are one part with its own 512 x 512 texture (the lcd section, its own
unwrap: the time meter window is the top of the picture, the speed window the bottom,
layout.LCD_RECTS) and the working frames from make_decals.py: "ready" - zeros and dashes,
counting - the time grows, result - the flight time over the sensor base (us) and the speed
(m/s); four shots of 3 s.

Machine look: the displays are ozl_screen (the lcd section: a red filter / frames), the
steady lamps (green: power, ready) are ozl_lamp, the blinking ones (red "count", yellow
"signal", red "start") are ozl_lamp_2 (the _on atlas, the _on rvmat with a glow). The
needles of the four meters are the bones ozl_work..ozl_work_4, each with its own source of
the same name: phase 0 - at zero (the left edge of the scale), 1 - the scale end (90 degrees
around ozl_work*_axis); while working OZL_WorkFx wobbles them, each around its own middle.
The fan is the bone ozl_fan on the source ozl_fan: a model.cfg loop (sourceAddress loop,
maxValue 1/4) - 4 turns per 2 s pass, 2 rev/s: 5 blades (every 72 degrees) shift by 24
degrees per frame at 30 fps, so the rotation does not "run backwards". LODs: the middle one
has no small items (screws, nameplates, cartridges, latches, the fan without a grille), the
far one has the body, panels, displays, lamps and needles, no glass.

Blender axes: X - width, Y - depth (front at -Y), Z - up.
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
import layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m (the rest is in layout.py)
# =============================================================================
CX, X0, X1, Y0, Y1, H = L.CX, L.X0, L.X1, L.Y0, L.Y1, L.H
ZB0, WALL, RIM = L.ZB0, L.WALL, L.RIM_W
PX0, PX1, YP, U = L.PX0, L.PX1, L.YP, L.U
UNITS = L.UNITS
XI0, XI1 = X0 + WALL, X1 - WALL                              # inside of the body
ZI1 = H - WALL
NEEDLE0 = -math.radians(L.ARC_DEG / 2)                       # scale zero: from vertical to the left
NEEDLE_ARC = math.radians(L.ARC_DEG) * L.NEEDLE_PHASE1
Y_FACE = YP - 0.0015                                         # meter scale behind the glass
Y_NEEDLE = (YP - 0.0040, YP - 0.0032)
Y_GLASS = YP - 0.0085
HANDLE_Z = 0.87                                              # folding handles on the sides
LID_A = math.radians(L.LID_DEG)
# lid: local axes - u along y, v up the lid (toward the wall), n outward; c = 0 is the edge at the
# wall
LID_FR = g.Frame((X0 - 0.003 - L.LID_H * math.sin(LID_A), 0.0, 0.0), (0, 1, 0),
                 (math.sin(LID_A), 0, math.cos(LID_A)), (-math.cos(LID_A), 0, math.sin(LID_A)))
DR_Y = YP - L.DRAWER_OUT                                     # face of the pulled-out drawer
DR_Z0, DR_Z1 = UNITS["drawer"]
TRAY = (PX0 + 0.035, PX1 - 0.035, DR_Y + 0.003, DR_Y + 0.33)  # drawer tray: x0, x1, y0, y1
ZB_TRAY = DR_Z0 + 0.010                                      # bottom of the tray sheet
CRADLE_Y = (TRAY[2] + 0.05, TRAY[2] + 0.18)                  # cradle along y
COIL_Y = (L.TRI_Y - 0.15, L.TRI_Y + 0.15)                    # sensor coils along y
COIL_R, TUBE_R, BORE_R = 0.065, 0.034, 0.024
AMP_CONN = [(CX + 0.165, UNITS["amp"][0] + 0.125), (CX + 0.165, UNITS["amp"][0] + 0.060)]
CABLE_R = 0.0045
# 80 mm fan on the back wall of the power unit (blows backward, into the open rear opening of the
# case)
FAN_X, FAN_Y, FAN_Z = CX - 0.075, L.UNIT_Y1, sum(UNITS["psu"]) / 2
FAN_H, FAN_RO, FAN_D = 0.040, 0.038, 0.025                    # half-body, window, body depth
FAN_TURNS = 4                                                 # turns per loop pass (2 s)

LOD_SPECS = [
    dict(lod=0, sides=12),
    dict(lod=1, sides=8),
    dict(lod=2, sides=6),
]

REGIONS = {
    "case": ("olive_case", 0.7), "case_r": ("olive_side", 0.9), "case_top": ("olive_top", 0.7),
    "case_in": ("olive_in", 0.5), "rim": ("olive_rim", 1.0), "corner": ("olive_corner", 1.2),
    "skid": ("olive_skid", 0.8), "lid": ("olive_lid", 0.8), "lid_in": ("olive_in", 0.4),
    "panel": ("panel", 1.5), "unit": ("unit", 0.5), "rail": ("rail", 1.0), "chrome": ("chrome", 1.6),
    "black": ("bakelite", 1.6), "face": ("meter_face", 5.0), "needle": ("needle", 2.0),
    "lamp_g": ("lamp_g", 1.6), "lamp_r": ("lamp_r", 1.6), "lamp_y": ("lamp_y", 1.6), "fuse": ("fuse", 1.6),
    "conn": ("conn", 1.6), "tag": ("tag", 2.5), "seal": ("seal", 3.0), "latch": ("latch", 1.6),
    "rubber": ("rubber", 1.0), "cable": ("cable", 1.0), "cradle": ("cradle", 1.6), "brass": ("brass", 2.4),
    "bullet": ("bullet", 2.4), "zip": ("olive_zip", 1.2), "sensor": ("olive_sensor", 1.6), "bore": ("bore", 1.0),
    "tripod": ("olive_tripod", 1.4), "tri_steel": ("tri_steel", 1.4), "fan": ("fan", 2.0), "vent": ("vent", 1.2),
}

# =============================================================================
# Materials
# =============================================================================


def build_worn(mat, origin, color, bare=kmats.lin((104, 104, 106)), primer=kmats.lin((96, 46, 34)), seed=1.0,
               gloss=0.28, spec=0.22, wear=(0.68, 0.73), edge_k=0.75, rub=(), touch=0.0, scratch=0.0, oil=0.0,
               floor_z=0.0, dust=0.2, grime=0.3, decal_items=()):
    """SOP olive - the M32 builder: old army paint, heavily worn - worn off on the edges (edge_k)
    and in the places that get grabbed (rub - [(center, half-axes, strength)]); a red-brown
    primer under the olive (a rim around the worn spot), bare metal in the middle of the spot.
    touch - the share of touch-up patches: fresh olive of a slightly different tone, with no
    wear under it. No rust.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.88 for c in color[:3]) + (1,), color)
    # sun-faded paint in larger patches
    base = t.mixc(t.math("MULTIPLY", t.maprange(t.noise(vec, 0.9, 4.0, 0.5), 0.45, 0.75, 0.0, 1.0), 0.35), base,
                  tuple(min(1.0, c * 1.25 + 0.01) for c in color[:3]) + (1,))
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
    tp = None
    if touch > 0:
        # touch-up: patches of fresh olive, the wear under them is reset
        tp = t.step(t.noise(vec, 3.2, 5.0, 0.55), 1.0 - touch * 0.5, 1.0 - touch * 0.5 + 0.02)
        f = t.math("SUBTRACT", f, t.math("MULTIPLY", tp, 0.6))
    worn = t.step(f, wear[0], wear[1])
    deep = t.step(f, wear[1] + 0.05, wear[1] + 0.09)                 # spot center - bare metal
    brush = t.noise(t.stretch(vec, 0.04, 1.0, 1.0), 90.0, 4.0, 0.7)
    metal = t.mixc(t.maprange(brush, 0.3, 0.7, 0.0, 1.0), tuple(c * 0.75 for c in bare[:3]) + (1,),
                   tuple(min(1.0, c * 1.15) for c in bare[:3]) + (1,))
    rim = t.math("SUBTRACT", t.step(f, wear[0] - 0.05, wear[0]), worn)
    col = t.mixc(t.math("MULTIPLY", rim, 0.55), col, kmats.lin((44, 46, 34)))
    if tp is not None:
        col = t.mixc(t.math("MULTIPLY", tp, 0.85), col, tuple(c * 1.06 for c in color[:3]) + (1,))
    col = t.mixc(worn, col, primer)
    col = t.mixc(deep, col, metal)
    h = t.math("MULTIPLY", worn, -0.3)
    g_ = t.math("ADD", gloss, t.math("MULTIPLY", deep, 0.58 - gloss))
    s_ = t.math("ADD", spec, t.math("MULTIPLY", deep, 0.66 - spec))
    if scratch > 0:
        sc = t.step(t.noise(t.stretch(vec, 0.02, 1.0, 1.0), 260.0, 2.0, 0.5), 0.70, 0.73)
        sc = t.math("MULTIPLY", sc, t.maprange(t.noise(vec, 5.0, 4.0, 0.5), 0.35, 0.65, 0.0, scratch))
        col = t.mixc(t.math("MULTIPLY", sc, 0.7), col, metal)
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", sc, 0.15))
    if oil > 0:
        up = t.maprange(nsep.outputs["Z"], 0.5, 0.9, 0.0, 1.0)
        ol = t.math("MULTIPLY", t.step(t.noise(vec, 4.0, 6.0, 0.6), 0.62, 0.70), t.math("MULTIPLY", up, oil))
        col = t.mixc(t.math("MULTIPLY", ol, 0.5), col, kmats.lin((16, 14, 10)))
        g_ = t.math("ADD", g_, t.math("MULTIPLY", ol, 0.25))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g_, s_, h)


def wdecal(name):
    return os.path.join(WORK, name)


def decal_y(name, cx, cz, w, h, ya, yb):
    """A decal on faces looking toward -y between ya and yb (the projection depth)."""
    return (wdecal(name), "y", -1, ("x", "z"), (cx, cz), (w, h), (ya, yb))


METER_DECALS = [decal_y("decal_meter_%s.png" % m["scale"], m["x"], m["z"] + L.MH / 2, L.MW, L.MH,
                        Y_FACE - 0.002, Y_FACE + 0.001) for m in L.METERS]


# right side (facing +x): number and stripes; lid (facing -x, to the viewer's right is -y): frame
# and arrows
SIDE_DECALS = [(wdecal(n), "x", 1, ("y", "z"), (d["y"], d["z"]), (d["w"], d["h"]), (X1 - 0.002, X1 + 0.004))
               for n, d in (("decal_side_num.png", L.SIDE_NUM), ("decal_side_band.png", L.SIDE_BAND))]
_ld = L.LID_DECAL
LID_DECALS = [(wdecal("decal_lid.png"), "x", -1, ("y", "z"), (_ld["y"], _ld["z"]), (-_ld["w"], _ld["h"]),
               (X0 - 0.40, X0 - 0.04))]

OLIVE = kmats.lin((80, 86, 56))                              # M32 olive
GREY = kmats.lin((116, 122, 116))                            # grey-green panel enamel
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
# where hands grab: the folding handles on the sides, the rim edges (the lids are taken off), the
# skids
CASE_RUB = [((X0 - 0.02, 0.0, HANDLE_Z), (0.05, 0.12, 0.08), 0.5), ((X1 + 0.02, 0.0, HANDLE_Z), (0.05, 0.12, 0.08), 0.5),
            ((CX, Y0, H), (0.32, 0.04, 0.05), 0.25)]
RIM_RUB = [((CX, Y0, 0.6), (0.34, 0.03, 0.7), 0.25), ((CX, Y1, 0.6), (0.34, 0.03, 0.7), 0.2)]
# panels: worn at the handles
PANEL_RUB = [((x, YP, (z0 + z1) / 2), (0.03, 0.03, (z1 - z0) * 0.5), 0.45)
             for z0, z1 in UNITS.values() for x in (PX0 + 0.022, PX1 - 0.022)]
OLV = dict(color=OLIVE, seed=2.1, touch=0.35, scratch=0.3, floor_z=0.0, dust=0.18, grime=0.3)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "olive_case": (build_worn, dict(OLV, rub=CASE_RUB)),
    "olive_side": (build_worn, dict(OLV, seed=2.4, rub=CASE_RUB, decal_items=SIDE_DECALS)),
    "olive_top": (build_worn, dict(OLV, seed=2.7, wear=(0.66, 0.71), rub=CASE_RUB, scratch=0.7, dust=0.4)),
    "olive_in": (build_worn, dict(OLV, seed=3.0, wear=(0.73, 0.78), edge_k=0.6, touch=0.1, scratch=0.1, dust=0.3,
                                  grime=0.2)),
    "olive_rim": (build_worn, dict(OLV, seed=3.3, wear=(0.64, 0.69), edge_k=1.0, rub=RIM_RUB, scratch=0.6)),
    "olive_corner": (build_worn, dict(OLV, seed=3.6, wear=(0.60, 0.66), edge_k=1.1, touch=0.2, scratch=0.5)),
    "olive_skid": (build_worn, dict(OLV, seed=3.9, wear=(0.58, 0.64), edge_k=1.1, touch=0.1, scratch=0.8, dust=0.3,
                                    grime=0.6)),
    "olive_lid": (build_worn, dict(OLV, seed=4.2, wear=(0.66, 0.71), edge_k=0.9, scratch=0.5,
                                   decal_items=LID_DECALS)),
    "olive_zip": (build_worn, dict(OLV, seed=4.5, wear=(0.65, 0.70), edge_k=1.0, floor_z=UNITS["shelf"][0], dust=0.4)),
    "olive_sensor": (build_worn, dict(OLV, seed=4.8, wear=(0.66, 0.71), edge_k=0.9, touch=0.25, floor_z=0.0)),
    "olive_tripod": (build_worn, dict(OLV, seed=5.1, wear=(0.62, 0.68), edge_k=1.0, touch=0.2, scratch=0.6,
                                      floor_z=0.0, grime=0.5)),
    "panel": (build_worn, dict(color=GREY, bare=kmats.lin((150, 150, 152)), primer=kmats.lin((78, 80, 76)), seed=5.4,
                               gloss=0.34, spec=0.28, wear=(0.71, 0.76), edge_k=0.8, rub=PANEL_RUB, touch=0.1,
                               scratch=0.35, floor_z=0.0, dust=0.15, grime=0.2)),
    "unit": (build_worn, dict(color=kmats.lin((96, 100, 96)), bare=kmats.lin((140, 140, 142)),
                              primer=kmats.lin((70, 70, 68)), seed=5.7, wear=(0.74, 0.79), edge_k=0.6, dust=0.35,
                              grime=0.25)),
    "rail": ("steel", dict(seed=6.0, tone=0.30, along="z", gloss=0.45, spec=0.55, dust=0.2, grime=0.3)),
    "chrome": ("steel", dict(seed=6.3, tone=0.40, along="z", gloss=0.75, spec=0.85, dust=0.1, grime=0.25)),
    "tri_steel": ("steel", dict(seed=6.6, tone=0.28, along="z", gloss=0.5, spec=0.6, dust=0.2, grime=0.4)),
    "bakelite": ("plastic", dict(color=kmats.lin((22, 21, 20)), gloss=0.5, spec=0.35, dust=0.2, scuff=(0.66, 0.74))),
    "meter_face": ("paint", dict(CLEAN, color=kmats.lin((228, 226, 214)), gloss=0.5, spec=0.4,
                                 decal_items=METER_DECALS)),
    "needle": ("flat", dict(color=kmats.lin((18, 18, 18)), gloss=0.5, spec=0.4)),
    "lamp_g": ("flat", dict(color=kmats.lin((30, 70, 36)), gloss=0.85, spec=0.8)),
    "lamp_g_on": ("flat", dict(color=kmats.lin((120, 255, 120)), gloss=0.85, spec=0.8)),
    "lamp_r": ("flat", dict(color=kmats.lin((90, 22, 18)), gloss=0.85, spec=0.8)),
    "lamp_r_on": ("flat", dict(color=kmats.lin((255, 80, 56)), gloss=0.85, spec=0.8)),
    "lamp_y": ("flat", dict(color=kmats.lin((96, 74, 22)), gloss=0.85, spec=0.8)),
    "lamp_y_on": ("flat", dict(color=kmats.lin((255, 206, 80)), gloss=0.85, spec=0.8)),
    # fuse caps - red-brown bakelite
    "fuse": ("plastic", dict(color=kmats.lin((104, 36, 22)), gloss=0.45, spec=0.3, dust=0.2, scuff=(0.7, 0.78))),
    "conn": (build_worn, dict(color=kmats.lin((70, 76, 52)), bare=kmats.lin((150, 150, 150)), seed=6.9,
                              wear=(0.64, 0.70), edge_k=1.0, dust=0.1, grime=0.3)),
    "tag": ("steel", dict(seed=7.2, tone=0.52, along="x", gloss=0.5, spec=0.6, dust=0.1, grime=0.2)),
    "seal": ("plastic", dict(color=kmats.lin((92, 94, 98)), gloss=0.35, spec=0.3, mottle=0.15, dust=0.1)),
    "latch": (build_worn, dict(color=kmats.lin((62, 66, 46)), bare=kmats.lin((130, 130, 130)), seed=7.5,
                               wear=(0.62, 0.68), edge_k=1.1, dust=0.1, grime=0.3)),
    "cable": ("plastic", dict(color=kmats.lin((26, 27, 25)), gloss=0.3, spec=0.2, dust=0.35)),
    "cradle": ("plastic", dict(color=kmats.lin((34, 36, 34)), gloss=0.1, spec=0.05, mottle=0.15, dust=0.15,
                               scuff=(0.8, 0.9))),
    "brass": ("paint", dict(CLEAN, color=kmats.lin((176, 136, 64)), gloss=0.6, spec=0.7)),
    "bullet": ("paint", dict(CLEAN, color=kmats.lin((150, 96, 60)), gloss=0.55, spec=0.6)),
    "bore": ("plastic", dict(color=kmats.lin((18, 18, 18)), gloss=0.2, spec=0.1, dust=0.1)),
    # fan impeller and housing: black plastic in dust (it blows - dust collects on the edges)
    "fan": ("plastic", dict(color=kmats.lin((30, 30, 30)), gloss=0.3, spec=0.2, dust=0.6, grime=0.5,
                            scuff=(0.8, 0.9))),
    # perforated grilles on the back walls of the units (10 mm pitch)
    "vent": ("steel", dict(seed=7.8, tone=0.30, along="z", holes=(("x", "z"), 0.010, 0.30), gloss=0.4, spec=0.45,
                           dust=0.45, grime=0.4)),
})

OBJ, NAME = "m33_sop_proc_ball", "ozr_sop_proc_ball"
# Machine look: the displays are ozl_screen (own texture, the lcd section, frames), the lamps
# are ozl_lamp (steady) and ozl_lamp_2 (blinking), all in hiddenSelections; off by default,
# working - for the lamps the _on_co atlas and the _on rvmat with a glow, for the displays
# the lcd_f* frames and lcd_on.rvmat. The needles are the bones ozl_work..._4, each with its
# own source (wobble sway); the fan is the ozl_fan loop.
SEL_SCREEN, SEL_LAMP, SEL_LAMP2, SEL_FAN = "ozl_screen", "ozl_lamp", "ozl_lamp_2", "ozl_fan"
BONES = [m["bone"] for m in L.METERS if m["bone"]]
ON = dict(remap={"lamp_g": "lamp_g_on", "lamp_r": "lamp_r_on", "lamp_y": "lamp_y_on"},
          emissive=(1.0, 1.0, 1.0, 1.0))
# Displays have their own texture with frames (kmodel panels): PNGs from make_decals.py, 17
# different frames; the show order while working (48 records of 0.25 s, a 12 s cycle) is
# make_decals.LCD_SEQ
LCD_FRAMES = 17                                              # make_decals.LCD_FRAMES
PANELS = {"lcd": dict(off="decal_lcd_off.png", frames=["decal_lcd_f%02d.png" % i for i in range(LCD_FRAMES)],
                      size=L.LCD_PX, gloss=0.75)}
# Needle sway while working (OZL_WorkFx wobble): the middle and the amplitude are fractions of
# the scale, the period is in s. The make_decals scales: a 0..10, b 0..50, c 0..100 (red zone
# from 80), d 0..30 (power, red zone from 27)
WOBBLE = {"ozl_work": (0.55, 0.06, 1.9), "ozl_work_2": (0.70, 0.04, 2.6), "ozl_work_3": (0.45, 0.08, 3.3),
          "ozl_work_4": (0.80, 0.012, 0.7)}
NEEDLE_ANIMS = tuple(("%s_needle" % b, dict(type="rotation", source=b, selection=b, axis=b + "_axis", memory=1,
                                            minValue=0.0, maxValue=1.0, angle0=0.0, angle1=NEEDLE_ARC)) for b in BONES)
FAN_ANIM = ("ozl_fan_spin", dict(type="rotation", source=SEL_FAN, sourceAddress="loop", selection=SEL_FAN,
                                 axis="ozl_fan_axis", memory=1, minValue=0.0, maxValue=1.0 / FAN_TURNS, angle0=0.0,
                                 angle1=2 * math.pi))
SOURCES = {b: dict(animPeriod=0.2) for b in BONES}
SOURCES[SEL_FAN] = dict(animPeriod=2.0)

# Vanilla proxy items (sizes come from vanilla_boxes.json of the kit): the case roof - a
# measurement log (a sheet and a pen), a box and loose 7.62 x 39; the spares shelf -
# insulating tape, pliers; the sample drawer - loose cartridges next to the cradle
Z_SHELF = UNITS["shelf"][0] + 0.004                          # top of the spares shelf sheet
Z_TRAY = ZB_TRAY + 0.003                                     # top of the tray sheet
DECOR = [
    kv.put("paper", (CX - 0.08, -0.03, H), **kv.flat(80)),
    kv.put("pen", (CX - 0.03, -0.10, H + 0.0005), **kv.flat(35)),
    kv.put("ammobox762", (CX + 0.14, 0.10, H), **kv.flat(95)),
    kv.put("rounds762", (CX + 0.13, -0.10, H), up=(0, 0, 1), fwd=(0, -1, 0)),
    kv.put("ducttape", (CX - 0.14, -0.175, Z_SHELF), **kv.flat(0)),
    kv.put("pliers", (CX + 0.115, -0.195, Z_SHELF), **kv.flat(8)),
    kv.put("rounds762", (CX + 0.15, TRAY[2] + 0.11, Z_TRAY), up=(0, 0, 1), fwd=(0, -1, 0)),
]
class Model(kmodel.Model):
    def panel_mats(self, on):
        """Working preview: the displays show the result of the first shot (the flight time and
        the speed).
        """
        out = super().panel_mats(on)
        if on:
            _, frames = self.panel_pngs("lcd")
            out["lcd"] = krender.panel_material(frames[4], glow=1.6, gloss=PANELS["lcd"]["gloss"])
        return out


M = Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
          glass=dict(base=(0.84, 0.86, 0.86), clear=0.04, edge=0.12, smudge=0.10, streaks=0.04),
          selections=(SEL_SCREEN, SEL_LAMP, SEL_LAMP2, SEL_FAN) + tuple(BONES),
          hidden=(SEL_SCREEN, SEL_LAMP, SEL_LAMP2), states={"on": ON},
          bones=tuple((b, "") for b in BONES) + ((SEL_FAN, ""),), animations=NEEDLE_ANIMS + (FAN_ANIM,),
          decor=DECOR, sources=SOURCES, panels=PANELS)
P = M.part
BOUNDS = {}

# Preview of the working look (--look): the needles are at the middle of their sway, the
# impeller is turned slightly. The pose is by rotation (states move only knows a shift): a
# wrapper over krender.place_look only in this script, it does not go into the p3d - there the
# needles are at zero and model.cfg drives them.
WORK_POSE = {m["bone"]: (Vector((m["x"], Y_NEEDLE[1], m["z"] + L.PIVOT_DZ)), WOBBLE[m["bone"]][0] * NEEDLE_ARC)
             for m in L.METERS if m["bone"]}
WORK_POSE[SEL_FAN] = (Vector((FAN_X, FAN_Y, FAN_Z)), math.radians(30.0))
if M.look_preview or "--look-render" in kmodel.ARGV:
    _place_look = krender.place_look

    def _place_look_work(parts, kind_table, origin, remap=None, **kw):
        obs = _place_look(parts, kind_table, origin, remap=remap, **kw)
        for p, ob in zip(parts, obs) if remap else ():
            if p.group in WORK_POSE:
                c, a = WORK_POSE[p.group]
                # +y goes from the face inward: a clockwise turn as seen facing the panel
                ob.matrix_world = (Matrix.Translation(ob.location) @ Matrix.Translation(c) @
                                   Matrix.Rotation(a, 4, Vector((0, 1, 0))) @ Matrix.Translation(-c))
        return obs
    krender.place_look = _place_look_work


# =============================================================================
# Primitives that kgeo lacks (lathe, along, face, spline - as in M30)
# =============================================================================
def along(o, d):
    """Local axes with u along d (a tilted solid of revolution)."""
    d = Vector(d).normalized()
    ref = Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
    v = d.cross(ref).normalized()
    return g.Frame(o, d, v, d.cross(v))


def front(x, z, y=YP):
    """Local axes of a control on a panel: u - from the panel toward the person (-y), v - x,
    n - z.
    """
    return g.Frame((x, y, z), (0, -1, 0), (1, 0, 0), (0, 0, 1))


def face(part, verts, want):
    """A face from bmesh vertices, turned to face toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def lathe(part, prof, sides, frame, inward=False, want=None, base=None, tip=None):
    """Solid of revolution around the u axis of the local axes frame: prof [(r, h)] - the radius
    and the place along u; inward - the surface looks toward the axis (the inside); want -
    where all faces look (a flat ring); base / tip - the place (h) of the cap vertex on the
    axis for the first / last ring (an end, a nose).
    """
    bm = part.bm
    rings = [[bm.verts.new(frame.p(h, r * math.cos(2 * math.pi * k / sides), r * math.sin(2 * math.pi * k / sides)))
              for k in range(sides)] for r, h in prof]
    new = []
    for i in range(len(rings) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        flat = abs(h1 - h0) < 1e-9
        for k in range(sides):
            j = (k + 1) % sides
            q = [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]]
            if want is not None:
                w = want
            elif flat:
                # flat ring: a step down looks forward along u, up - backward
                w = frame.u * (1.0 if r1 < r0 else -1.0) * (-1.0 if inward else 1.0)
            else:
                c = sum((v.co for v in q), Vector()) / 4
                ax = frame.o + frame.u * (c - frame.o).dot(frame.u)
                w = (ax - c) if inward else (c - ax)
            new.append(face(part, q, w))
    for h, ring, sgn in ((base, rings[0], -1.0), (tip, rings[-1], 1.0)):
        if h is None:
            continue
        cv = bm.verts.new(frame.p(h, 0.0, 0.0))
        for k in range(sides):
            new.append(face(part, [cv, ring[k], ring[(k + 1) % sides]], frame.u * sgn))
    bm.normal_update()
    part.tag(new)


def rod(part, a, b, r, sides):
    return g.pipe(part, [tuple(a), tuple(b)], r, sides)


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, from M24)."""
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


def dedup(pts, eps=1e-6):
    out = []
    for p in pts:
        if not out or (Vector(p) - Vector(out[-1])).length > eps:
            out.append(tuple(p))
    return out


def smooth(pts, k=10, deg=7.0, step=0.12):
    """Smooth curve (Catmull-Rom) with points where it turns: a point per deg degrees of turn or
    per step meters. Cables without kinks and without extra rings on straight runs.
    """
    dense = [Vector(p) for p in spline(pts, k)]
    out = [dense[0]]
    for i in range(1, len(dense) - 1):
        a, b, c = out[-1], dense[i], dense[i + 1]
        if (b - a).length < 1e-6 or (c - b).length < 1e-6:
            continue
        if math.degrees((b - a).angle(c - b)) > deg or (b - a).length > step:
            out.append(b)
    out.append(dense[-1])
    return dedup(out)


def round_path(pts, r, n=4):
    """Polyline with rounded corners: at each bend an arc of radius r of n segments (handle
    brackets, lock loops). The ends are as is.
    """
    v = [Vector(p) for p in pts]
    out = [v[0]]
    for i in range(1, len(v) - 1):
        a, b, c = v[i - 1], v[i], v[i + 1]
        d1, d2 = a - b, c - b
        l1, l2 = d1.length, d2.length
        d1.normalize()
        d2.normalize()
        ang = d1.angle(d2)
        if ang > math.pi - 1e-3 or ang < 1e-3:
            out.append(b)
            continue
        t = min(r / math.tan(ang / 2), l1 * 0.45, l2 * 0.45)
        p1, p2 = b + d1 * t, b + d2 * t
        for k in range(n + 1):
            s = k / n
            out.append((1 - s) ** 2 * p1 + 2 * (1 - s) * s * b + s * s * p2)
    out.append(v[-1])
    return dedup(out)


def knurl(part, fr, r, depth, teeth, a0, a1):
    """Knurled ring (a handle, a coupling nut, a lamp rim): a star of `teeth` teeth r / r - depth
    in the v-n plane of the local axes fr, from a0 to a1 along u.
    """
    poly = []
    for k in range(2 * teeth):
        rr = r if k % 2 == 0 else r - depth
        poly.append((rr * math.cos(math.pi * k / teeth), rr * math.sin(math.pi * k / teeth)))
    g.prism(part, poly, (1, 2), a0, a1, frame=fr)


def rivet(part, at, d, r=0.0055, h=0.004, sides=6):
    """A rivet with a half-round head: a low truncated cone, d is outward from the sheet (half of
    it sits in the sheet).
    """
    g.cyl(part, (0.0, 0.0, 0.0), "x", r, h, sides, r2=r * 0.5, frame=along(at, d))


def bezel(part, x0, x1, z0, z1, ix0, ix1, iz0, iz1, yf, yb, ch=0.0):
    """Frame facing -y (a device body, a display): outer rectangle x0..x1 z0..z1 with a chamfer ch
    on the front edge, window ix0..ix1 iz0..iz1, face at yf, back (toward the panel) at yb; the
    window walls go to yb.
    """
    bm = part.bm

    def rect(a0, a1, b0, b1, y):
        return [bm.verts.new((a0, y, b0)), bm.verts.new((a1, y, b0)), bm.verts.new((a1, y, b1)),
                bm.verts.new((a0, y, b1))]
    win_f, win_b = rect(ix0, ix1, iz0, iz1, yf), rect(ix0, ix1, iz0, iz1, yb)
    out_f = rect(x0 + ch, x1 - ch, z0 + ch, z1 - ch, yf)
    out_c = rect(x0, x1, z0, z1, yf + ch) if ch > 0 else out_f
    out_b = rect(x0, x1, z0, z1, yb)
    outward = [Vector((0, 0, -1)), Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((-1, 0, 0))]
    new = []
    for i in range(4):
        j = (i + 1) % 4
        new.append(face(part, [win_f[i], win_f[j], out_f[j], out_f[i]], (0, -1, 0)))
        if ch > 0:
            new.append(face(part, [out_f[i], out_f[j], out_c[j], out_c[i]], outward[i] + Vector((0, -1, 0))))
        new.append(face(part, [out_c[i], out_c[j], out_b[j], out_b[i]], outward[i]))
        new.append(face(part, [win_f[i], win_f[j], win_b[j], win_b[i]], -outward[i]))
    bm.normal_update()
    part.tag(new)


def bev(lod, r=0.003, seg=1):
    return dict(r=r, seg=seg) if lod == 0 else {}


def front_quad(part, x0, x1, z0, z1, y):
    """A single face looking toward -y (far LOD: displays, lamps)."""
    return g.quad(part, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)])


def plug(cn, ch, cb, fr, lod, base=None, cable=True):
    """2RM class connector along fr.u from a = 0: the base (base: "flange" - a square flange on
    four screws, "boss" - a round boss), the socket, a knurled coupling nut and (cable) a plug
    with a rubber boot. Returns the point where the cable leaves the boot (the end center).
    """
    n = 10
    a = 0.0
    if base == "flange":
        if lod == 0:
            g.box(cn, 0.0, 0.003, -0.018, 0.018, -0.018, 0.018, frame=fr, **(dict(r=0.0012, seg=1) if ch else {}))
            for b, c in ((-0.013, -0.013), (0.013, -0.013), (0.013, 0.013), (-0.013, 0.013)) if ch else ():
                g.cyl(ch, (0.0036, b, c), "x", 0.0022, 0.0016, 6, r2=0.0015, frame=fr)
        a = 0.003
    elif base == "boss":
        g.cyl(cn, (0.005, 0.0, 0.0), "x", 0.017, 0.010, n if lod == 0 else 6, frame=fr)
        a = 0.010
    if lod > 0:
        # middle LOD: the socket with the nut and the plug are one cylinder
        g.cyl(cn, (a + 0.024, 0.0, 0.0), "x", 0.015, 0.048, 6, frame=fr)
        return fr.p(a + 0.054, 0.0, 0.0)
    g.cyl(cn, (a + 0.004, 0.0, 0.0), "x", 0.0135, 0.008, n, frame=fr)               # socket
    a += 0.008
    if not cable:
        return fr.p(a, 0.0, 0.0)
    knurl(cn, fr, 0.0165, 0.0012, 9, a, a + 0.016)                                   # coupling nut
    a += 0.016
    lathe(cn, [(0.0125, a), (0.0125, a + 0.010), (0.0105, a + 0.014)], n, fr)          # plug body
    lathe(cb, [(0.0105, a + 0.014), (0.0080, a + 0.020), (0.0056, a + 0.030)], 8, fr)   # boot
    return fr.p(a + 0.030, 0.0, 0.0)


# =============================================================================
# Case: walls, rims, corner pieces, skids, handles, latches
# =============================================================================
def latch(lt, xw, s, ye, z, lod, loop=True):
    """A "frog" latch without a lid: the base, a hinge, the lever folded down, a wire loop hangs
    (loop - at the front rim; at the back the loops were taken off with the lid).
    """
    xa, xb = (xw - 0.006, xw) if s < 0 else (xw, xw + 0.006)
    g.box(lt, xa, xb, ye - 0.020, ye + 0.020, z - 0.034, z + 0.022, **(bev(lod, 0.0015) if loop else {}))
    xc = xw + s * 0.0095
    g.cyl(lt, (xc, ye, z - 0.026), "y", 0.0042, 0.030, 6)
    a = math.radians(10.0)
    fr = g.Frame((xc, ye, z - 0.026), (0, 1, 0), (s * math.sin(a), 0, -math.cos(a)), (s * math.cos(a), 0, math.sin(a)))
    g.box(lt, -0.0145, 0.0145, 0.0, 0.052, -0.002, 0.002, frame=fr)
    if loop:
        g.pipe(lt, round_path([fr.p(-0.010, 0.014, 0.0035), fr.p(-0.010, 0.070, 0.0055), fr.p(0.010, 0.070, 0.0055),
                               fr.p(0.010, 0.014, 0.0035)], 0.006, 2), 0.0018, 4)


def build_case(spec):
    lod = spec["lod"]
    parts = []
    # walls - each its own part: the face of the left one and the inside of the right one (the
    # same side) must not share the atlas
    for nm, rg, box in (("left", "case", (X0, X0 + WALL, Y0, Y1, ZB0, H)),
                        ("right", "case_r", (X1 - WALL, X1, Y0, Y1, ZB0, H)),
                        ("top", "case_top", (X0 + WALL, X1 - WALL, Y0, Y1, H - WALL, H)),
                        ("bottom", "case_in", (X0 + WALL, X1 - WALL, Y0, Y1, ZB0, ZB0 + WALL))):
        p = P("case_" + nm, rg)
        g.box(p, *box)
        parts.append(p)
    # opening rims: a frame with a flange, protruding 4 mm past the walls
    for side, (ya, yb) in (("front", (Y0 - 0.008, Y0 + 0.022)), ("back", (Y1 - 0.022, Y1 + 0.008))):
        rm = P("rim_" + side, "rim")
        o = 0.004
        g.box(rm, X0 - o, X0 + RIM, ya, yb, ZB0 - o, H + o, **bev(lod, 0.004))
        g.box(rm, X1 - RIM, X1 + o, ya, yb, ZB0 - o, H + o, **bev(lod, 0.004))
        g.box(rm, X0 + RIM, X1 - RIM, ya, yb, H - RIM, H + o, **bev(lod, 0.004))
        g.box(rm, X0 + RIM, X1 - RIM, ya, yb, ZB0 - o, ZB0 + RIM, **bev(lod, 0.004))
        parts.append(rm)
    # skids under the bottom
    sk = P("skids", "skid")
    for x in (CX - 0.22, CX + 0.22):
        g.box(sk, x - 0.025, x + 0.025, Y0 + 0.01, Y1 - 0.01, 0.0, ZB0, **bev(lod, 0.006))
    parts.append(sk)
    if lod == 2:
        return parts
    # stamped corner pieces on all eight corners, rounded, on rivets (side and end; on top for
    # the upper ones); the left and right ones are different parts (the +-x sides)
    c, o = 0.078, 0.007
    for nm, xs, sx in (("left", (X0 - o, X0 + c), -1), ("right", (X1 - c, X1 + o), 1)):
        cn = P("corners_" + nm, "corner")
        for ys, sy in (((Y0 - 0.012, Y0 + c), -1), ((Y1 - c, Y1 + 0.012), 1)):
            for zs, sz in (((ZB0 - o, ZB0 + c), -1), ((H - c, H + o), 1)):
                g.box(cn, *xs, *ys, *zs, **bev(lod, 0.011))
                if lod == 0:
                    xm, ym, zm = (sum(xs) / 2, sum(ys) / 2, sum(zs) / 2)
                    xo, yo, zo = xs[1] if sx > 0 else xs[0], ys[1] if sy > 0 else ys[0], zs[1] if sz > 0 else zs[0]
                    rivet(cn, (xo, ym, zm), (sx, 0, 0))
                    rivet(cn, (xm, yo, zm), (0, sy, 0))
                    if sz > 0:
                        rivet(cn, (xm, ym, zo), (0, 0, 1))
        parts.append(cn)
    # side ribs - half-round, tapering off toward the ends (middle LOD - strips); folding handles
    for nm, s, xw in (("left", -1, X0), ("right", 1, X1)):
        rb = P("ribs_" + nm, "case" if s < 0 else "case_r")
        ys = [Y0 + 0.09, Y0 + 0.11, Y1 - 0.11, Y1 - 0.09]
        rs = [0.002, 0.009, 0.009, 0.002]
        for z in (0.58, 1.06):
            if lod == 0:
                g.tube_var(rb, [(xw, y, z) for y in ys], [(r, r) for r in rs], 6)
            else:
                g.box(rb, min(xw, xw + s * 0.006), max(xw, xw + s * 0.006), Y0 + 0.09, Y1 - 0.09, z - 0.009, z + 0.009)
        parts.append(rb)
        hd = P("handle_" + nm, "latch")
        xo = xw + s * 0.004
        g.box(hd, min(xw, xo), max(xw, xo), -0.10, 0.10, HANDLE_Z - 0.025, HANDLE_Z + 0.03, **bev(lod, 0.0015))
        xl = xw + s * 0.018
        for yl in (-0.079, 0.079):                                                   # lugs
            g.box(hd, min(xo, xl), max(xo, xl), yl - 0.007, yl + 0.007, HANDLE_Z - 0.012, HANDLE_Z + 0.014)
        xp = xw + s * 0.013
        pts = [(xp, -0.086, HANDLE_Z), (xp + s * 0.006, -0.086, HANDLE_Z - 0.066),
               (xp + s * 0.006, 0.086, HANDLE_Z - 0.066), (xp, 0.086, HANDLE_Z)]
        g.pipe(hd, round_path(pts, 0.016, 3) if lod == 0 else pts, 0.005, 6 if lod == 0 else 4)
        parts.append(hd)
        if lod == 0:
            gr = P("grip_" + nm, "rubber")
            lathe(gr, [(0.0085, -0.055), (0.0115, -0.050), (0.0115, 0.050), (0.0085, 0.055)], 8,
                  g.Frame((xp + s * 0.006, 0.0, HANDLE_Z - 0.066), (0, 1, 0), (1, 0, 0), (0, 0, 1)))
            parts.append(gr)
    if lod == 1:
        return parts
    # "frog" latches at both rims (the lids are off - the levers are folded down)
    lt = P("latches", "latch")
    for s, xw in ((-1, X0), (1, X1)):
        for ye in (Y0 + 0.050, Y1 - 0.050):
            for z in (0.32, 0.98):
                latch(lt, xw, s, ye, z, lod, loop=ye < 0)
    parts.append(lt)
    return parts


# =============================================================================
# Rack 19 in: front and rear posts with angles to the side walls
# =============================================================================
def build_rack(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    rl = P("rails", "rail")
    z0, z1 = L.Z_STACK - 0.01, ZI1 - 0.005
    for ys in (L.RAIL_Y, L.RAIL_BACK_Y):
        for xa, xb, xw in ((PX0, PX0 + 0.016, XI0), (PX1 - 0.016, PX1, XI1)):
            g.box(rl, xa, xb, *ys, z0, z1)
            # angle: from the post to the side wall
            g.box(rl, min(xw, xa), max(xw, xb), ys[1], ys[1] + 0.002, z0, z1)
    parts = [rl]
    if lod == 0:
        # square holes of the posts in the free places - dark dots (the spares shelf is on top)
        bk = P("rail_holes", "black")
        for xa in (PX0 + 0.008, PX1 - 0.008):
            for k in range(3):
                z = UNITS["shelf"][1] + 0.006 + 0.012 * k
                if z < z1 - 0.006:
                    g.box(bk, xa - 0.003, xa + 0.003, L.RAIL_Y[0] - 0.0005, L.RAIL_Y[0], z - 0.003, z + 0.003)
        parts.append(bk)
    return parts


# =============================================================================
# Units: panel, body, handles, meters, displays, lamps, controls
# =============================================================================
def panel(name, z0, z1, lod, y=YP, depth=L.UNIT_Y1, handles=True):
    """A 19" unit panel with the body behind it, bracket handles on bosses and slotted screws
    on the ears.
    """
    pn = P(name + "_panel", "panel")
    g.box(pn, PX0, PX1, y, y + L.PANEL_T, z0 + 0.0005, z1 - 0.0005, **bev(lod, 0.0012))
    parts = [pn]
    if depth is not None:
        bd = P(name + "_body", "unit")
        g.box(bd, PX0 + 0.024, PX1 - 0.024, y + L.PANEL_T, depth, z0 + 0.003, z1 - 0.003)
        parts.append(bd)
    if handles and lod < 2:
        ch = P(name + "_handles", "chrome")
        zm, sp = (z0 + z1) / 2, min(0.05, (z1 - z0) / 2 - 0.025)
        for x in (PX0 + 0.022, PX1 - 0.022):
            pts = [(x, y + 0.001, zm - sp), (x, y - 0.030, zm - sp), (x, y - 0.030, zm + sp), (x, y + 0.001, zm + sp)]
            if lod == 0:
                g.pipe(ch, round_path(pts, 0.009, 2), 0.0045, 6)
            else:
                g.pipe(ch, pts, 0.0045, 4)
        if lod == 0:
            for x in (PX0 + 0.008, PX1 - 0.008):
                for z in (z0 + 0.012, z1 - 0.012):
                    g.cyl(ch, (x, y - 0.0013, z), "y", 0.0048, 0.0026, 6, r2=0.0040)
        parts.append(ch)
    return parts


def meter(m, lod, name, ch):
    """M4200-class dial meter: a black square body-frame with a chamfer, the scale, the needle (a
    bone), the glass, the corrector screw, two mounting screws.
    """
    x0, x1, z0, z1 = m["x"] - L.MW / 2, m["x"] + L.MW / 2, m["z"], m["z"] + L.MH
    fz0, fz1 = z0 - 0.017, z0 - 0.017 + L.FLANGE
    fx0, fx1 = m["x"] - L.FLANGE / 2, m["x"] + L.FLANGE / 2
    bk = P(name + "_case", "black")
    yf = YP - 0.010
    if lod == 2:
        g.box(bk, fx0, fx1, yf, YP, fz0, z0)
    else:
        bezel(bk, fx0, fx1, fz0, fz1, x0, x1, z0, z1, yf, YP, ch=0.0025 if lod == 0 else 0.0)
    parts = [bk]
    fc = P(name + "_face", "face")
    g.box(fc, x0, x1, Y_FACE, YP, z0, z1)
    parts.append(fc)
    # needle: at zero it points up-left from the axis; the axis cap
    px, pz = m["x"], z0 + L.PIVOT_DZ
    nd = P(name + "_needle", "needle", group=m["bone"] or "body")
    d = (math.sin(NEEDLE0), math.cos(NEEDLE0))
    pp = (d[1], -d[0])
    poly = [(-0.006, -0.0010), (L.NEEDLE_L, -0.0003), (L.NEEDLE_L, 0.0003), (-0.006, 0.0010)]
    poly = [(px + a * d[0] + b * pp[0], pz + a * d[1] + b * pp[1]) for a, b in poly]
    g.prism(nd, poly, (0, 2), *Y_NEEDLE)
    if lod < 2:
        g.cyl(nd, (px, Y_NEEDLE[0] - 0.0005, pz), "y", 0.0035, 0.001, 8 if lod == 0 else 5)
    parts.append(nd)
    if lod == 0:
        gl = P(name + "_glass", "chrome", section="glass")
        g.box(gl, x0, x1, Y_GLASS - 0.0005, Y_GLASS + 0.0005, z0, z1)
        parts.append(gl)
        g.cyl(bk, (m["x"], yf - 0.002, z0 - 0.009), "y", 0.0042, 0.004, 8, r2=0.0038)       # zero corrector
        g.box(bk, m["x"] - 0.003, m["x"] + 0.003, yf - 0.0042, yf - 0.0038, z0 - 0.0095, z0 - 0.0085)
        for x in (fx0 + 0.0075, fx1 - 0.0075):
            g.cyl(ch, (x, yf - 0.0008, fz0 + 0.0075), "y", 0.0028, 0.0016, 6, r2=0.0022)
    return parts


def readouts(lod):
    """Displays of the time meter and the speed (ozl_screen): the faces of both are one part with
    its own texture (the lcd section, working frames) and its own unwrap - the timer window on
    the top half of the picture, the speed on the bottom half (layout.lcd_uv); black frames
    with a chamfer around.
    """
    sc = P("screen_lcd", "black", group=SEL_SCREEN, section="lcd")
    sc.fixed_uv = True
    uvl = sc.bm.loops.layers.uv.get("UVMap") or sc.bm.loops.layers.uv.new("UVMap")
    parts = [sc]
    for key, r in L.READOUTS.items():
        x0, x1, z0, z1 = r["x"] - r["w"] / 2, r["x"] + r["w"] / 2, r["z"] - r["h"] / 2, r["z"] + r["h"] / 2
        u0, u1, v0, v1 = L.lcd_uv(key)
        for f in front_quad(sc, x0, x1, z0, z1, YP - (0.001 if lod == 2 else 0.002)):
            for lp in f.loops:
                co = lp.vert.co
                lp[uvl].uv = (u0 + (u1 - u0) * (co.x - x0) / (x1 - x0), v0 + (v1 - v0) * (co.z - z0) / (z1 - z0))
        if lod < 2:
            bz = P("bezel_" + key, "black")
            b = 0.006
            bezel(bz, x0 - b, x1 + b, z0 - b, z1 + b, x0, x1, z0, z1, YP - 0.007, YP, ch=0.0018 if lod == 0 else 0.0)
            parts.append(bz)
    return parts


def lamps(name, items, lod):
    """Signal lamps: [(x, z, color, r, blinks)] - a convex lens in a ribbed rim; the blinking ones
    are ozl_lamp_2, the others ozl_lamp.
    """
    parts = []
    by = {}
    for x, z, col, r, bl in items:
        by.setdefault((col, bl), []).append((x, z, r))
    for (col, bl), its in by.items():
        lp = P("%s_lamp_%s%s" % (name, col, "_b" if bl else ""), "lamp_" + col, group=SEL_LAMP2 if bl else SEL_LAMP)
        for x, z, r in its:
            if lod == 2:
                front_quad(lp, x - r, x + r, z - r, z + r, YP - 0.001)
            elif lod == 1:
                g.cyl(lp, (x, YP - 0.010, z), "y", r, 0.008, 6)
            else:
                lathe(lp, [(r, 0.005), (r, 0.0098), (r * 0.70, 0.0136)], 8, front(x, z), tip=0.0150)
        parts.append(lp)
    if lod == 0:
        ch = P(name + "_lamp_rims", "chrome")
        for x, z, col, r, bl in items:
            g.cyl(ch, (0.0038, 0, 0), "x", r + 0.0045, 0.0075, 8, r2=r + 0.0035, frame=front(x, z))
        parts.append(ch)
    return parts


def toggles(part, items, lod):
    """Toggles: a washer, a nut, a bushing and a conical lever with a ball; items [(x, z, up)]."""
    for x, z, up in items if lod == 0 else ():
        f = front(x, z)
        g.cyl(part, (0.0035, 0, 0), "x", 0.0068, 0.006, 6, frame=f)                    # nut
        base = Vector((x, YP - 0.006, z))
        tip = Vector((x, YP - 0.027, z + (0.011 if up else -0.011)))
        dv = tip - base
        g.cyl(part, (0, 0, 0), "x", 0.0024, dv.length, 6, r2=0.0017, frame=along(base + dv / 2, dv))
        g.cyl(part, (0, 0, 0), "x", 0.0029, 0.005, 6, r2=0.0022, frame=along(tip, dv))


def knob(part, tg, x, z, r, lod, pointer=False):
    """Knob: a skirt, fluting, a conical cap with a tick; pointer - a selector switch knob
    with a beak.
    """
    if lod > 0:
        g.cyl(part, (x, YP - 0.012, z), "y", r, 0.024, 6)
        return
    f = front(x, z)
    if pointer:
        g.cyl(part, (0.002, 0, 0), "x", r * 1.18, 0.004, 12, r2=r * 1.12, frame=f)
    knurl(part, f, r, r * 0.08, 12 if pointer else 9, 0.0 if not pointer else 0.004, 0.016)
    g.cyl(part, (0.019, 0, 0), "x", r * 0.93, 0.006, 10, r2=r * 0.82, frame=f)
    g.box(tg, -0.0007, 0.0007, r * 0.22, r * 0.76, 0.0218, 0.0223, frame=g.Frame((x, YP, z), (1, 0, 0), (0, 0, 1),
                                                                                  (0, -1, 0)))
    if pointer:
        g.box(part, -0.0035, 0.0035, r * 0.85, r * 1.6, 0.006, 0.020, r=0.0012, seg=1,
              frame=g.Frame((x, YP, z), (1, 0, 0), (0, 0, 1), (0, -1, 0)))


def tag(part, x0, x1, z0, z1):
    """A blank aluminium nameplate (no text)."""
    g.box(part, x0, x1, YP - 0.0012, YP, z0, z1)


def build_units(spec):
    lod = spec["lod"]
    parts = []
    ch = P("units_hw", "chrome")
    kb = P("units_knobs", "black")
    for i, m in enumerate(L.METERS):
        parts += meter(m, lod, "meter%d" % i, ch)
    parts += readouts(lod)
    # --- Power unit ---------------------------------------------------------------------------
    z0, z1 = UNITS["psu"]
    parts += panel("psu", z0, z1, lod)
    lamp_items = [(CX + 0.020, z0 + 0.110, "g", 0.010, False)]
    # --- Time meter ---------------------------------------------------------------------------
    t0, t1 = UNITS["timer"]
    parts += panel("timer", t0, t1, lod)
    lamp_items += [(CX + 0.050, t0 + 0.070, "r", 0.0065, True)]
    # --- Sensor amplifiers --------------------------------------------------------------------
    a0, a1 = UNITS["amp"]
    parts += panel("amp", a0, a1, lod)
    lamp_items += [(CX + 0.040, a0 + 0.050, "y", 0.0065, True), (CX + 0.090, a0 + 0.050, "g", 0.0065, False)]
    # --- Control ------------------------------------------------------------------------------
    c0, c1 = UNITS["ctrl"]
    parts += panel("ctrl", c0, c1, lod)
    lamp_items += [(CX - 0.050, c0 + 0.165, "r", 0.0065, True), (CX - 0.050, c0 + 0.115, "g", 0.0065, False)]
    parts += lamps("units", lamp_items, lod)
    if lod == 2:
        return parts
    tg = P("units_tags", "tag")
    # power: the mains toggle, fuses in holders with ribbed caps, a connector at the back
    toggles(ch, [(CX - 0.040, z0 + 0.100, False)], lod)
    fu = P("psu_fuses", "fuse")
    for x in (CX + 0.075, CX + 0.115, CX + 0.155):
        zf = z0 + 0.050
        if lod == 0:
            g.cyl(ch, (x, YP - 0.002, zf), "y", 0.0115, 0.004, 8)
            knurl(fu, front(x, zf), 0.0090, 0.0007, 8, 0.004, 0.019)
            g.cyl(fu, (0.0205, 0, 0), "x", 0.0080, 0.003, 8, r2=0.0068, frame=front(x, zf))
        else:
            g.cyl(fu, (x, YP - 0.011, zf), "y", 0.009, 0.022, 5)
    parts.append(fu)
    # time meter: buttons in frames, a wafer switch, a knob
    for i, x in enumerate((CX - 0.130, CX - 0.095, CX - 0.060, CX - 0.025)):
        bt = kb if i < 3 else fu
        g.box(bt, x - 0.010, x + 0.010, YP - 0.012, YP, t0 + 0.060, t0 + 0.080, **bev(lod, 0.002 if i == 3 else 0.0))
        if lod == 0:
            g.box(ch, x - 0.0125, x + 0.0125, YP - 0.002, YP, t0 + 0.0575, t0 + 0.0825)
    knob(kb, tg, CX + 0.125, t0 + 0.150, 0.018, lod, pointer=True)
    knob(kb, tg, CX + 0.125, t0 + 0.065, 0.012, lod)
    # amplifiers: two gain knobs, sensor cable connectors
    knob(kb, tg, CX + 0.040, a0 + 0.115, 0.013, lod)
    knob(kb, tg, CX + 0.090, a0 + 0.115, 0.013, lod)
    cn = P("amp_conn", "conn")
    cb = P("amp_boots", "cable")
    for x, z in AMP_CONN:
        plug(cn, ch, cb, front(x, z), lod, base="flange")
    parts += [cn, cb]
    # control: toggles
    toggles(ch, [(CX + 0.020, c0 + 0.075, True), (CX + 0.060, c0 + 0.075, False), (CX + 0.100, c0 + 0.075, False),
                 (CX + 0.140, c0 + 0.075, True)], lod)
    parts += [ch, kb]
    if lod == 0:
        tag(tg, CX + 0.060, CX + 0.170, z0 + 0.074, z0 + 0.084)
        tag(tg, CX - 0.140, CX + 0.020, t0 + 0.098, t0 + 0.108)
        for x in (CX + 0.020, CX + 0.060, CX + 0.100, CX + 0.140):
            tag(tg, x - 0.014, x + 0.014, c0 + 0.040, c0 + 0.050)
        tag(tg, CX + 0.030, CX + 0.120, a0 + 0.020, a0 + 0.030)
        # lead seal on a screw of the control unit: wire and a disc
        sl = P("seal", "seal")
        sx, sz = PX1 - 0.008, c0 + 0.012
        g.pipe(sl, spline([(sx, YP - 0.003, sz), (sx - 0.006, YP - 0.006, sz - 0.012), (sx - 0.010, YP - 0.008, sz - 0.022)],
                          3), 0.0007, 5)
        g.cyl(sl, (sx - 0.010, YP - 0.008, sz - 0.028), "y", 0.006, 0.004, 12, r2=0.0055)
        parts.append(sl)
        # unit back walls: connectors (power - with a plug and cable, build_cables)
        rc = P("rear_conn", "conn")
        rb = P("rear_boots", "cable")
        for i, (u0, u1) in enumerate((UNITS["psu"], UNITS["timer"], UNITS["amp"])):
            plug(rc, None, rb, along((CX + 0.12, L.UNIT_Y1, (u0 + u1) / 2), (0, 1, 0)), lod, base="flange",
                 cable=(i == 0))
        parts += [rc, rb]
        # unit back walls: perforated grilles (the rear opening of the case is open)
        vt = P("rear_vents", "vent")
        for u0, u1 in (UNITS["timer"], UNITS["amp"], UNITS["ctrl"]):
            g.box(vt, CX - 0.19, CX + 0.07, L.UNIT_Y1, L.UNIT_Y1 + 0.0012, u0 + 0.022, u1 - 0.022)
        parts.append(vt)
    parts.append(tg)
    return parts


# =============================================================================
# Fan on the back wall of the power unit (bone ozl_fan)
# =============================================================================
def build_fan(spec):
    """80 mm fan: a square housing (a flange with a round window on four posts, a shroud), the
    stator on three spokes, a 5-blade impeller (ozl_fan), a wire grille.
    """
    lod = spec["lod"]
    if lod == 2:
        return []
    fr = g.Frame((FAN_X, FAN_Y, FAN_Z), (0, 1, 0), (1, 0, 0), (0, 0, 1))          # u: back, away from wall
    hs = P("fan_housing", "fan")
    hh, ro, dd = FAN_H, FAN_RO, FAN_D
    if lod == 0:
        # housing - a square with a round window through its full depth: four corner inserts and the
        # window shroud
        for qa, qb in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
            arc = [(qa * ro * math.cos(t), qb * ro * math.sin(t)) for t in (math.radians(a) for a in (67.5, 45.0, 22.5))]
            poly = [(qa * ro, 0.0), (qa * hh, 0.0), (qa * hh, qb * hh), (0.0, qb * hh), (0.0, qb * ro)] + arc
            g.prism(hs, poly, (1, 2), 0.0, dd, frame=fr)
        lathe(hs, [(ro, 0.0), (ro, dd)], 16, fr, inward=True)
        # stator: a disc on three spokes by the wall
        g.cyl(hs, (0.004, 0, 0), "x", 0.013, 0.006, 8, frame=fr)
        for k in range(3):
            a = math.radians(90 + 120 * k)
            sfr = g.Frame(fr.p(0.003, 0, 0), (math.cos(a), 0, math.sin(a)), (0, 1, 0), (-math.sin(a), 0, math.cos(a)))
            g.box(hs, 0.012, ro, -0.002, 0.002, -0.0025, 0.0025, frame=sfr)
    else:
        g.box(hs, 0.0, dd, -hh, hh, -hh, hh, frame=fr)
    parts = [hs]
    rt = P("fan_rotor", "fan", group=SEL_FAN)
    g.cyl(rt, (0.0125, 0, 0), "x", 0.0145, 0.011, 12 if lod == 0 else 6, frame=fr)
    pitch = math.radians(30.0)
    for k in range(5 if lod == 0 else 0):
        a = 2 * math.pi * k / 5
        er = Vector((math.cos(a), 0, math.sin(a)))
        et = Vector((-math.sin(a), 0, math.cos(a)))
        v = et * math.cos(pitch) + fr.u * math.sin(pitch)
        bfr = g.Frame(fr.p(0.0125, 0, 0), er, v, er.cross(v))
        g.prism(rt, [(0.012, -0.010), (0.035, -0.014), (0.036, 0.004), (0.033, 0.012), (0.012, 0.009)], (0, 1),
                -0.0008, 0.0008, frame=bfr)
    parts.append(rt)
    if lod == 0:
        gd = P("fan_guard", "rail")
        for r in (FAN_RO - 0.002, 0.021):
            g.pipe(gd, [fr.p(dd + 0.0025, r * math.cos(2 * math.pi * i / 12), r * math.sin(2 * math.pi * i / 12))
                        for i in range(13)], 0.0011, 3)
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            rod(gd, fr.p(dd + 0.0025, 0.008 * math.cos(a), 0.008 * math.sin(a)),
                fr.p(dd + 0.0025, (FAN_RO + 0.001) * math.cos(a), (FAN_RO + 0.001) * math.sin(a)), 0.0011, 3)
        g.cyl(gd, (dd + 0.0025, 0, 0), "x", 0.009, 0.0016, 8, frame=fr)
        parts.append(gd)
    return parts


# =============================================================================
# Sample drawer (pulled out): tray, slides, cradle with cartridges
# =============================================================================
def build_drawer(spec):
    """Pull-out sample shelf (like the shelves of 19" racks on telescopic slides): a sheet with a
    low rim and handles on the front rim, behind it an empty 3U cell with a back wall. The
    cradle is a rubber bar with V-grooves: cartridges lie in three, the fourth is empty; two
    extracted bullets stand on the bar on the right, next to them on the sheet are the vanilla
    loose cartridges (DECOR).
    """
    lod = spec["lod"]
    tx0, tx1, ty0, ty1 = TRAY
    zb = ZB_TRAY
    tr = P("drawer_tray", "panel")
    g.box(tr, tx0, tx1, DR_Y, ty1, zb, zb + 0.003)                                   # shelf sheet
    g.box(tr, PX0 + 0.03, PX1 - 0.03, DR_Y - 0.003, DR_Y, zb, zb + 0.040, **bev(lod, 0.001))  # front rim
    parts = [tr]
    bk = P("drawer_back", "unit")
    g.box(bk, PX0 + 0.024, PX1 - 0.024, L.UNIT_Y1 - 0.003, L.UNIT_Y1, DR_Z0 + 0.003, DR_Z1 - 0.003)
    parts.append(bk)
    if lod == 2:
        return parts
    sd = P("drawer_sides", "unit")
    for xa, xb in ((tx0, tx0 + 0.003), (tx1 - 0.003, tx1)):
        g.box(sd, xa, xb, DR_Y, ty1, zb + 0.003, zb + 0.022, **bev(lod, 0.001))
    g.box(sd, tx0 + 0.003, tx1 - 0.003, ty1 - 0.003, ty1, zb + 0.003, zb + 0.022)
    parts.append(sd)
    ch = P("drawer_pulls", "chrome")
    for x in (PX0 + 0.075, PX1 - 0.075):
        pts = [(x - 0.03, DR_Y - 0.002, zb + 0.020), (x - 0.03, DR_Y - 0.022, zb + 0.020),
               (x + 0.03, DR_Y - 0.022, zb + 0.020), (x + 0.03, DR_Y - 0.002, zb + 0.020)]
        g.pipe(ch, round_path(pts, 0.007, 2) if lod == 0 else pts, 0.004, 6 if lod == 0 else 4)
    parts.append(ch)
    # telescopic slides: the outer one in the post, the inner one on the tray, narrower and lower
    sl = P("drawer_slides", "rail")
    for s, (xa, xb) in ((-1, (tx0 - 0.012, tx0)), (1, (tx1, tx1 + 0.012))):
        g.box(sl, xa, xb, ty0 + 0.10, 0.20, zb, zb + 0.030, **bev(lod, 0.0015))
        xi = (xa + 0.002, xb - 0.002)
        g.box(sl, xi[0], xi[1], ty0 + 0.02, ty0 + 0.12, zb + 0.005, zb + 0.025, **bev(lod, 0.001))
    parts.append(sl)
    # cradle
    cr = P("drawer_cradle", "cradle")
    cy0, cy1 = CRADLE_Y
    xa, xb = tx0 + 0.035, CX + 0.08
    zc0, zc1 = zb + 0.003, zb + 0.025
    grooves = [CX - 0.13 + 0.05 * k for k in range(4)]
    gd = 0.0032                                                                     # V-groove depth
    if lod == 0:
        poly = [(xa, zc0), (xb, zc0), (xb, zc1)]
        for xg in reversed(grooves):
            poly += [(xg + gd, zc1), (xg, zc1 - gd), (xg - gd, zc1)]
        poly.append((xa, zc1))
        g.prism(cr, poly, (0, 2), cy0, cy1)
    else:
        g.box(cr, xa, xb, cy0, cy1, zc0, zc1)
    parts.append(cr)
    if lod == 1:
        return parts
    br = P("drawer_brass", "brass")
    bl = P("drawer_bullets", "bullet")
    # 7.62x39 class cartridge: case 38.7 x dia 11.3, length 56; lies in the V-groove (90 degrees,
    # 3.2 mm deep): the axis is 4.7 mm above the top of the bar
    zc = zc1 - gd + 0.0056 / math.sin(math.radians(45))
    for xg in grooves[:3]:
        fr = g.Frame((xg, cy0 + 0.030, zc), (0, 1, 0), (1, 0, 0), (0, 0, 1))
        lathe(br, [(0.0057, 0.0), (0.0057, 0.0012), (0.0048, 0.0018), (0.0056, 0.0033), (0.0051, 0.0300),
                   (0.0042, 0.0340), (0.0041, 0.0387)], 8, fr, base=0.0)
        lathe(bl, [(0.0040, 0.0387), (0.0040, 0.0450), (0.0030, 0.0505), (0.0012, 0.0550)], 8, fr, tip=0.0560)
    # extracted bullets - flattened, stand on the bar on the right
    for x in (CX + 0.045, CX + 0.064):
        lathe(bl, [(0.0040, 0.0), (0.0046, 0.009), (0.0060, 0.015), (0.0032, 0.0205)], 8,
              g.Frame((x, cy0 + 0.065, zc1), (0, 0, 1), (1, 0, 0), (0, 1, 0)), tip=0.0212)
    parts += [br, bl]
    return parts


# =============================================================================
# Spares shelf: a cable coil and a box
# =============================================================================
def build_shelf(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    z0, z1 = UNITS["shelf"]
    sh = P("shelf", "unit")
    g.box(sh, PX0 + 0.004, PX1 - 0.004, YP + 0.01, L.UNIT_Y1, z0, z0 + 0.004)
    g.box(sh, PX0 + 0.004, PX1 - 0.004, YP + 0.01, YP + 0.013, z0, z0 + 0.03, **bev(lod, 0.001))   # rim
    parts = [sh]
    # spare cable coil: a three-turn spiral (turn lies on turn), the tail with a plug hangs over the
    # rim
    cb = P("shelf_coil", "cable")
    cx, cy = CX - 0.105, -0.02
    rc = 0.0055
    turns, n = 3.0, (27 if lod == 0 else 12)
    pts = []
    for i in range(n + 1):
        t = i / n
        a = 2 * math.pi * turns * t
        r = 0.082 - 0.010 * t
        pts.append((cx + r * math.cos(a), cy + r * 0.8 * math.sin(a), z0 + 0.004 + rc + 0.0098 * turns * t))
    g.pipe(cb, pts, rc, 5 if lod == 0 else 4)
    if lod == 0:
        e = Vector(pts[-1])
        tail = smooth([tuple(e), (e.x + 0.012, e.y - 0.03, e.z - 0.006), (cx + 0.088, cy - 0.10, z0 + 0.004 + rc),
                       (cx + 0.094, YP + 0.035, z0 + 0.004 + rc), (cx + 0.098, YP + 0.008, z0 + 0.03 + rc),
                       (cx + 0.100, YP - 0.008, z0 + 0.008), (cx + 0.101, YP - 0.010, z0 - 0.025)], k=10, deg=12.0)
        g.pipe(cb, tail, rc, 5)
        d = Vector(tail[-1]) - Vector(tail[-2])
        lathe(cb, [(0.0056, 0.0), (0.0085, 0.010), (0.0105, 0.016), (0.0105, 0.042)], 8, along(tail[-1], d),
              tip=0.044)
    parts.append(cb)
    zp = P("shelf_zip", "zip")
    g.box(zp, CX + 0.04, CX + 0.20, -0.14, -0.02, z0 + 0.004, z0 + 0.084, **bev(lod, 0.005))
    if lod == 0:
        g.box(zp, CX + 0.037, CX + 0.203, -0.143, -0.017, z0 + 0.074, z0 + 0.088, r=0.003, seg=1)   # lid
        lt = P("shelf_zip_latch", "latch")
        g.box(lt, CX + 0.11, CX + 0.13, -0.147, -0.140, z0 + 0.052, z0 + 0.080, r=0.0015, seg=1)
        g.cyl(lt, (CX + 0.12, -0.1455, z0 + 0.079), "x", 0.0025, 0.022, 6)
        # handle on the lid: the bracket lies, in two lugs
        for x in (CX + 0.085, CX + 0.155):
            g.box(lt, x - 0.006, x + 0.006, -0.088, -0.072, z0 + 0.088, z0 + 0.094)
        g.pipe(lt, round_path([(CX + 0.085, -0.080, z0 + 0.092), (CX + 0.085, -0.118, z0 + 0.092),
                               (CX + 0.155, -0.118, z0 + 0.092), (CX + 0.155, -0.080, z0 + 0.092)], 0.008, 2),
               0.0028, 5)
        parts.append(lt)
    parts.append(zp)
    return parts


# =============================================================================
# Front lid leaning on the left side
# =============================================================================
def build_lid(spec):
    lod = spec["lod"]
    fr = LID_FR
    hw, hh, t = 0.30 + 0.004, L.LID_H, L.LID_T
    sk = P("lid_skin", "lid")
    g.box(sk, -hw, hw, 0.0, hh, t - 0.004, t, frame=fr, **bev(lod, 0.0015))
    parts = [sk]
    if lod == 2:
        return parts
    # lid rims (toward the wall) are their own parts: the inside is out of sight
    bd = P("lid_rim", "lid_in")
    w = 0.010
    for a in ((-hw, -hw + w, 0.0, hh), (hw - w, hw, 0.0, hh), (-hw + w, hw - w, 0.0, w), (-hw + w, hw - w, hh - w, hh)):
        g.box(bd, a[0], a[1], a[2], a[3], 0.0, t - 0.004, frame=fr)
    parts.append(bd)
    cn = P("lid_corners", "corner")
    c = 0.078
    for us in ((-hw - 0.006, -hw + c), (hw - c, hw + 0.006)):
        for vs in ((-0.006, c), (hh - c, hh + 0.006)):
            g.box(cn, us[0], us[1], vs[0], vs[1], t - 0.03, t + 0.006, frame=fr, **bev(lod, 0.011))
            if lod == 0:
                rivet(cn, fr.p(sum(us) / 2, sum(vs) / 2, t + 0.006), fr.n)
    parts.append(cn)
    rb = P("lid_ribs", "lid")
    us = [-hw + 0.09, -hw + 0.11, hw - 0.11, hw - 0.09]
    rs = [0.002, 0.009, 0.009, 0.002]
    for v in (0.30, 0.95):
        if lod == 0:
            g.tube_var(rb, [tuple(fr.p(u, v, t)) for u in us], [(r, r) for r in rs], 6)
        else:
            g.box(rb, -hw + 0.09, hw - 0.09, v - 0.009, v + 0.009, t, t + 0.006, frame=fr)
    parts.append(rb)
    if lod == 0:
        lt = P("lid_keepers", "latch")
        # latch keepers on the rims
        for u in (-hw - 0.006, hw):
            for v in (0.30, 0.95):
                g.box(lt, u, u + 0.006, v - 0.016, v + 0.016, 0.01, 0.04, frame=fr)
                g.box(lt, u - 0.002, u + 0.008, v - 0.010, v + 0.010, 0.016, 0.024, frame=fr)
        # folding lid handle - folded, lies on the face above the marking frame
        vh = 0.84
        for u in (-0.085, 0.085):
            g.box(lt, u - 0.009, u + 0.009, vh - 0.012, vh + 0.012, t, t + 0.008, frame=fr, r=0.002, seg=1)
        g.pipe(lt, round_path([fr.p(-0.085, vh, t + 0.006), fr.p(-0.085, vh - 0.055, t + 0.011),
                               fr.p(0.085, vh - 0.055, t + 0.011), fr.p(0.085, vh, t + 0.006)], 0.014, 3), 0.0045, 6)
        parts.append(lt)
        gr = P("lid_grip", "rubber")
        lathe(gr, [(0.0075, -0.048), (0.0105, -0.044), (0.0105, 0.044), (0.0075, 0.048)], 8,
              g.Frame(fr.p(0.0, vh - 0.055, t + 0.011), fr.u, fr.v, fr.n))
        parts.append(gr)
    return parts


# =============================================================================
# Tripod and the inductive speed sensor
# =============================================================================
LEG_DEG = (55.0, 185.0, 305.0)


def build_tripod(spec):
    """Tripod: a cast head with three hinges, legs - an olive tube and a sliding steel one, a flag
    clamp at the joint, rubber heels; a central column with a lock thumbscrew.
    """
    lod = spec["lod"]
    n = 8 if lod == 0 else 5
    tx, ty, hz = L.TRI_X, L.TRI_Y, L.TRI_HEAD
    parts = []
    tp = P("tripod", "tripod")
    ts = P("tripod_low", "tri_steel")
    ft = P("tripod_feet", "rubber")
    kb = P("tripod_knob", "black")
    for a in LEG_DEG:
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        top = Vector((tx + 0.034 * c, ty + 0.034 * s, hz - 0.012))
        foot = Vector((tx + L.TRI_R * c, ty + L.TRI_R * s, 0.016))
        d = (foot - top).normalized()
        mid = top + (foot - top) * 0.55
        rod(tp, top, mid + d * 0.015, 0.012, n)
        rod(ts, mid - d * 0.02, foot, 0.0085, n)
        if lod == 0:
            # clamp at the joint: a collar and a flag lever
            cfr = along(mid, d)
            lathe(tp, [(0.0125, -0.004), (0.0158, 0.0), (0.0158, 0.030), (0.0125, 0.034)], n, cfr)
            g.box(tp, 0.004, 0.028, 0.0150, 0.0195, -0.006, 0.006, frame=cfr)
            # hinge at the head: a fork of two cheeks and a pin
            radial = Vector((c, s, 0.0))
            tang = Vector((-s, c, 0.0))
            hfr = g.Frame(top, tang, Vector((0, 0, 1)), radial)
            for sg in (-1, 1):
                g.box(tp, sg * 0.0125, sg * 0.0165, -0.016, 0.012, -0.010, 0.016, frame=hfr)
            g.cyl(tp, (0, 0, 0.002), "x", 0.0045, 0.040, 6, frame=hfr)
            # heel: a rubber bell
            lathe(ft, [(0.0095, 0.0), (0.0105, 0.008), (0.0150, 0.0150)], n,
                  g.Frame(foot, (0, 0, -1), (1, 0, 0), (0, 1, 0)), tip=0.016)
        elif lod == 1:
            g.cyl(ft, tuple(foot - Vector((0, 0, 0.006))), "z", 0.014, 0.012, n)
    # cast head and central column
    if lod == 0:
        lathe(tp, [(0.030, 0.0), (0.046, 0.007), (0.046, 0.025), (0.040, 0.031), (0.016, 0.034)], 12,
              g.Frame((tx, ty, hz - 0.017), (0, 0, 1), (1, 0, 0), (0, 1, 0)), base=0.0, tip=0.034)
        # column lock: a thumbscrew in the head, between the legs
        a = math.radians(120.0)
        rdir = Vector((math.cos(a), math.sin(a), 0.0))
        sfr = along(Vector((tx, ty, hz + 0.004)) + rdir * 0.044, rdir)
        g.cyl(kb, (0.007, 0, 0), "x", 0.0045, 0.014, 6, frame=sfr)
        g.box(kb, 0.012, 0.018, -0.016, 0.016, -0.004, 0.004, frame=sfr, r=0.002, seg=1)
    else:
        g.cyl(tp, (tx, ty, hz), "z", 0.045, 0.03, 6)
    zc1 = L.SENSOR_Z - COIL_R + 0.01 - 0.012
    g.cyl(ts, (tx, ty, (hz + zc1) / 2), "z", 0.012, zc1 - hz, n)
    parts += [tp, ts]
    if lod < 2:
        parts.append(ft)
    if lod == 0:
        parts.append(kb)
    return parts


def build_sensor(spec):
    """Sensor: a tube with two coils (bodies with grooves and rounded edges), the ends on four
    screws, a saddle on the column with a collar, 2RM connectors on top of the coils, a
    nameplate.
    """
    lod = spec["lod"]
    n = 16 if lod == 0 else 8
    tx, ty, zs = L.TRI_X, L.TRI_Y, L.SENSOR_Z
    sn = P("sensor", "sensor")
    fr = g.Frame((tx, ty - L.SENSOR_L / 2, zs), (0, 1, 0), (1, 0, 0), (0, 0, 1))
    ln = L.SENSOR_L
    cl = 0.05
    R = COIL_R
    if lod == 0:
        half = [(BORE_R, 0.0), (R - 0.004, 0.0), (R, 0.004), (R, 0.016), (R - 0.0025, 0.0185), (R, 0.021),
                (R, cl - 0.004), (R - 0.004, cl), (TUBE_R + 0.004, cl), (TUBE_R, cl + 0.008)]
    else:
        half = [(BORE_R, 0.0), (R, 0.004), (R, cl - 0.004), (TUBE_R, cl)]
    prof = half + [(r, ln - h) for r, h in reversed(half)]
    lathe(sn, prof, n, fr)
    parts = [sn]
    bo = P("sensor_bore", "bore")
    lathe(bo, [(BORE_R, 0.0), (BORE_R, ln)], n, fr, inward=True)
    parts.append(bo)
    # saddle on the tripod column and a collar over the tube
    yk = P("sensor_yoke", "tri_steel")
    zy = zs - COIL_R + 0.01
    g.box(yk, tx - 0.030, tx + 0.030, ty - 0.05, ty + 0.05, zy - 0.012, zy, **bev(lod, 0.002))
    g.box(yk, tx - 0.024, tx + 0.024, ty - 0.036, ty + 0.036, zy - 0.001, zs - TUBE_R + 0.007, **bev(lod, 0.002))
    if lod == 0:
        for yb in (ty - 0.028, ty + 0.028):
            arc = [(tx + (TUBE_R + 0.0025) * math.cos(math.radians(a)), yb, zs + (TUBE_R + 0.0025) * math.sin(math.radians(a)))
                   for a in range(-25, 206, 33)]
            g.pipe(yk, [(arc[0][0], yb, zy + 0.002)] + arc + [(arc[-1][0], yb, zy + 0.002)], 0.0028, 4)
            for x in (tx - 0.030, tx + 0.030):
                g.cyl(yk, (x, yb, zy - 0.006), "x", 0.0045, 0.004, 6)                       # collar nuts
    else:
        for s in (-1, 1):
            g.box(yk, tx + s * TUBE_R, tx + s * (TUBE_R + 0.006), ty - 0.03, ty + 0.03, zy - 0.012, zs)
    parts.append(yk)
    if lod == 2:
        return parts
    # connectors on top of the coils
    cn = P("sensor_conn", "conn")
    ch = P("sensor_screws", "chrome")
    cb = P("sensor_boots", "cable")
    for y in COIL_Y:
        plug(cn, ch, cb, g.Frame((tx, y, zs + COIL_R - 0.004), (0, 0, 1), (1, 0, 0), (0, 1, 0)), lod, base="boss")
    parts += [cn, cb]
    if lod == 0:
        # coil tie screws on the ends, a nameplate on the tube (toward the person, -x)
        for y, sy in ((ty - ln / 2, -1), (ty + ln / 2, 1)):
            for k in range(4):
                a = math.pi / 4 + k * math.pi / 2
                g.cyl(ch, (0, 0, 0), "x", 0.0042, 0.003, 6, r2=0.0034,
                      frame=along((tx + 0.050 * math.cos(a), y + sy * 0.001, zs + 0.050 * math.sin(a)), (0, sy, 0)))
        tg = P("sensor_tag", "tag")
        g.box(tg, tx - TUBE_R - 0.0015, tx - TUBE_R + 0.0008, ty - 0.020, ty + 0.020, zs - 0.010, zs + 0.010,
              r=0.0006, seg=1)
        for y in (ty - 0.015, ty + 0.015):
            rivet(tg, (tx - TUBE_R - 0.0015, y, zs), (-1, 0, 0), r=0.0018, h=0.0014)
        parts.append(tg)
    parts.append(ch)
    return parts


# =============================================================================
# Cables: from the amplifiers to the coils, power at the back
# =============================================================================
R_FLOOR = CABLE_R + 0.0002
# Path from the amplifier connector (the boot) to the coil connector: it sags in front of the
# time meter panel, lies on the floor to the right of the case, runs along the floor to the
# tripod (past a leg heel), rises to the coil on the left (-x) and enters the plug from above
# in an arc. The upper connector is the front coil, the lower one the rear coil. The bends at
# the floor and above the coil have a radius of 4-6 cm (control points every 1-3 cm),
# otherwise a support point makes a kink. The rise to the coil: (z, shift along x, fraction
# of the y path to the connector out of 0.036)
_RISE = [(0.006, 0.012, 0.002), (0.020, 0.022, 0.005), (0.045, 0.029, 0.008), (0.09, 0.034, 0.012),
         (0.20, 0.038, 0.017), (0.45, 0.046, 0.023), (0.64, 0.057, 0.027), (0.735, 0.071, 0.031),
         (0.768, 0.085, 0.033), (0.782, 0.101, 0.035), (0.785, 0.118, 0.036), (0.776, 0.132, 0.036),
         (0.760, 0.139, 0.036), (0.741, 0.139, 0.036)]


def _rise(x0, y0, yc):
    """Rise from the floor to the coil connector yc: from (x0, y0) at the floor - up on the left
    of the coil, an arc over the top into the plug (the last points are exactly above the plug,
    x = TRI_X).
    """
    return [(x0 + (L.TRI_X - x0) * dx / 0.139, y0 + (yc - y0) * k / 0.036, z) for z, dx, k in _RISE]


# descent from the amplifier connector: sags in front of the time meter panel and settles smoothly
# on the floor
CABLE_PATHS = [
    [(0.045, -0.315, 0.7384), (0.045, -0.335, 0.7380), (0.050, -0.355, 0.728), (0.075, -0.385, 0.68),
     (0.135, -0.410, 0.54), (0.185, -0.425, 0.33), (0.198, -0.430, 0.18), (0.207, -0.433, 0.09),
     (0.216, -0.435, 0.040), (0.228, -0.437, 0.014), (0.245, -0.437, R_FLOOR + 0.001), (0.27, -0.435, R_FLOOR),
     (0.30, -0.426, R_FLOOR), (0.325, -0.410, R_FLOOR), (0.344, -0.392, R_FLOOR)] + _rise(0.354, -0.378, COIL_Y[0]),
    [(0.045, -0.315, 0.6734), (0.045, -0.335, 0.6730), (0.052, -0.352, 0.663), (0.080, -0.375, 0.615),
     (0.130, -0.392, 0.49), (0.175, -0.402, 0.30), (0.188, -0.404, 0.17), (0.197, -0.405, 0.085),
     (0.206, -0.404, 0.038), (0.218, -0.401, 0.013), (0.234, -0.394, R_FLOOR + 0.001), (0.252, -0.378, R_FLOOR),
     (0.265, -0.350, R_FLOOR), (0.276, -0.31, R_FLOOR), (0.292, -0.24, R_FLOOR), (0.312, -0.16, R_FLOOR),
     (0.330, -0.11, R_FLOOR), (0.342, -0.087, R_FLOOR), (0.352, -0.073, R_FLOOR)] + _rise(0.362, -0.062, COIL_Y[1]),
]
# power: from the plug on the back wall of the power unit backward through the rim, to the
# floor and sideways; at the end a plug lies on the floor
POWER_PATH = [(CX + 0.12, 0.268, 0.1689), (CX + 0.12, 0.285, 0.168), (CX + 0.122, 0.305, 0.158),
              (CX + 0.126, 0.325, 0.12), (CX + 0.130, 0.338, 0.07), (CX + 0.134, 0.348, 0.032),
              (CX + 0.140, 0.358, 0.012), (CX + 0.152, 0.372, R_FLOOR + 0.001), (CX + 0.18, 0.395, R_FLOOR),
              (CX + 0.26, 0.43, R_FLOOR), (CX + 0.38, 0.44, R_FLOOR), (CX + 0.42, 0.455, R_FLOOR + 0.001),
              (CX + 0.455, 0.468, 0.0108)]


def build_cables(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    sides = 5 if lod == 0 else 4
    parts = []
    for i, pts in enumerate(CABLE_PATHS):
        cb = P("cable_sensor%d" % i, "cable")
        # middle LOD - every other control point, no smoothing
        g.pipe(cb, smooth(pts, deg=7.0, step=0.10) if lod == 0 else pts[:2] + pts[3:-3:2] + pts[-3:], CABLE_R, sides)
        parts.append(cb)
    pw = P("cable_power", "cable")
    pts = smooth(POWER_PATH, deg=8.0, step=0.12) if lod == 0 else POWER_PATH[:3] + POWER_PATH[4::2]
    g.pipe(pw, pts, 0.0055, sides)
    if lod == 0:
        d = Vector(POWER_PATH[-1]) - Vector(POWER_PATH[-2])
        d.z = 0.0
        fr = along(pts[-1], d)
        lathe(pw, [(0.0058, -0.004), (0.0085, 0.008), (0.0108, 0.017), (0.0108, 0.052), (0.0095, 0.056)], 8, fr,
              tip=0.056)
        kb = P("plug_pins", "chrome")
        for b in (-0.0045, 0.0045):
            g.cyl(kb, (0.063, b, 0.0), "x", 0.0018, 0.014, 6, frame=fr)
        parts.append(kb)
    parts.append(pw)
    return parts


def build_lod(spec):
    parts = build_case(spec) + build_rack(spec) + build_units(spec) + build_fan(spec) + build_drawer(spec)
    parts += build_shelf(spec) + build_lid(spec) + build_tripod(spec) + build_sensor(spec) + build_cables(spec)
    parts = [p for p in parts if p.bm.faces]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """The case with the lid at its side (one box) and the tripod with the sensor (a second one,
    0.5 x 0.5). The pulled-out drawer is thinner than 0.5 m - not made a component (engine
    rule).
    """
    steel = kx.PEN + r"\metalplate.rvmat"
    lid_x = X0 - L.LID_OUT - L.LID_T - 0.01
    case = kx.box_pts(lid_x, X1 + 0.01, Y0 - 0.01, Y1 + 0.01, 0.0, H + 0.005)
    tri = kx.box_pts(L.TRI_X - 0.25, L.TRI_X + 0.25, L.TRI_Y - 0.25, L.TRI_Y + 0.25, 0.0, L.SENSOR_Z + COIL_R + 0.04)
    comps = [(case, steel), (tri, steel)]
    memory = {
        "invView": [(0.0, -2.4, 1.2)],
        "ce_center": [(0.0, 0.0, 0.6)],
        "ce_radius": [(0.9, 0.0, 0.6)],
        # fan axis: from the unit wall backward
        "ozl_fan_axis": [(FAN_X, FAN_Y + 0.005, FAN_Z), (FAN_X, FAN_Y + 0.055, FAN_Z)],
    }
    # needle axes (ozl_work...): from the needle axis to the face
    for m in L.METERS:
        if m["bone"]:
            px, pz = m["x"], m["z"] + L.PIVOT_DZ
            memory[m["bone"] + "_axis"] = [(px, Y_NEEDLE[1], pz), (px, Y_NEEDLE[1] - 0.05, pz)]
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2] + 0.004)
    return comps, 95.0, memory, bbox


# The first five are the --look preview (overall view, panels, sample drawer, tripod with the
# sensor, fan at the back), the working look uses the first two
SHOTS = [
    ("front", (-0.9, -2.6, 1.5), (0.05, 0.0, 0.62), 30),
    ("panels", (-0.35, -1.25, 0.95), (-0.12, -0.26, 0.68), 34),
    ("drawer", (0.05, -1.0, 0.85), (-0.12, -0.45, 0.33), 32),
    ("tripod", (1.2, -1.3, 0.95), (0.50, -0.18, 0.45), 32),
    ("back", (0.42, 1.10, 0.62), (CX - 0.04, 0.20, 0.30), 30),
    ("meters", (-0.25, -0.75, 0.85), (-0.17, -0.26, 0.78), 34),
    ("left", (-1.9, -1.0, 1.2), (-0.45, 0.0, 0.6), 32),
    ("right", (1.8, 0.4, 1.0), (0.1, 0.0, 0.55), 32),
    ("top", (-0.55, -1.0, 1.85), (-0.10, -0.05, 1.10), 32),
]

M.look_shots = (5, 2)
M.run(build_lod, collision, SHOTS, row_step=1.6, row_shot=((1.6, -6.0, 1.8), (1.6, 0, 0.6)))
