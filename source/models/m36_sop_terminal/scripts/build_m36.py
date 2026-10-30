"""M36 - the SOP staff monitor: a rugged field terminal (OZL_Sop_Terminal). Result media are
handed in here and the research tree is opened. A terminal: an explicit screen, no modules.

    blender --background --python build_m36.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: make_decals.py with the system Python (the CRT and laptop screens -
"off" and "working", the keyboard, the stencil numbers, the radio panel). Positions are in
layout.py (shared with make_decals.py). The "working" frames of the screens are made by
frames.py from the same decals, in Blender, before the build (Pillow is not needed).

Card: a field terminal of the post-Soviet army - a rugged laptop of the late 90s and a CRT
monitor in a steel shell on a folding army table, iron boxes under the table, a field
telephone, a radio and a tripod antenna next to them, a cable reel. 1.2 x 1.5 x 0.7 m. The
layout is like a signals post on a table (a Finnish army photo: a rugged laptop, a radio
with an antenna on a table).

Reference and dimensions:
- a folding table 1.00 x 0.60 (card), top at 0.74 - an ordinary table height; X-shaped
  supports of 25 mm tube at the ends, a longitudinal brace through their axes, 18 mm
  plywood on a frame of 45 mm angle (estimates from folding field tables);
- a rugged laptop of the Panasonic Toughbook CF-27 class (1997): ~0.30 x 0.06 x 0.24 closed
  (no passport found in open sources), screen 12.1" (a 1999 Toughbook 27 review) -
  246 x 184 mm 4:3; a handle at the front, a lid latch on top, light keys, a touchpad, a row
  of LEDs; base 36, lid 24 mm - from the photo; no brands;
- a 14" CRT in a steel shell: 0.36 x 0.36 x 0.375 - from a 14" monitor body
  (~0.35 x 0.35 x 0.37; the 15" of M31 is 0.36 x 0.36 x 0.39) and the shell wall; visible
  area 268 x 201 (13" visible); handles at the front like a rack instrument, louvres, a
  stencil number - estimates;
- an R-107 class radio: 375 x 185 x 270 mm, 17 kg (the R-107T; the R-107 is 19.5 kg with the
  kit), stands on the table at the right, the long side along the depth; the control panel
  on top: two frequency knobs with limbs, counter windows, small knobs, headset sockets, a
  lamp, an antenna socket - the layout from photos (an estimate); the dial indicator in
  place of the upper nameplate - an estimate;
- a TA-57 field telephone: 222 x 165 x 79 mm (as in M61), here opened as in the photo: a
  body with a panel, an inductor and terminals, a handset in the lid; M61 stands closed -
  the models do not repeat each other;
- a tripod antenna: a whip up to 1.50 (the model top per the card), a 28 mm mast with a
  matching unit at 0.86, a tripod at 0.47 with legs at 0.135 from the axis - estimates (the
  R-107 whip is 1.5 m);
- a field cable reel of the P-274 class: cheeks dia 0.28, width 0.18, a frame with a handle
  and a crank - an estimate from photos of army reels (no passport found), a two-wire cable
  to the TA-57;
- iron boxes: a spares box 0.50 x 0.32 x 0.30 and a battery one 0.28 x 0.24 x 0.25 -
  estimates; an A5 log, a pencil, the radio handset (~0.21) - a standard and estimates.
The extent ~1.27 x 1.50 x 0.64 m: the tripod at the side is a bit wider than the card (1.2)
- the legs cannot be brought closer, otherwise a 1 m whip on 0.47 would tip over.

SOP look (the build_worn builder is from M32/M33/M35): olive, heavily worn (edges, handles,
box corners, the tabletop edge), primer under the paint, touched up in places, no rust. The
laptop is dark grey, worn to a light tone on the ribs and at the handle. Unreadable details:
stencil numbers on the boxes and the CRT shell, a stripe, frequency digits and limbs on the
radio, blank nameplates, a lead seal on a box.

Look: "dayz"; the visible edges are rounded (table, laptop, CRT shell, radio, boxes), the
CRT front frame is one part with a rounded window (a boolean difference), handles and
brackets are arcs, cables are smooth curves with plugs at the ends; the laptop has a
recessed screen, rubber corners, a handle of a grip and links, port covers; the radio has
bay latches with levers, panel screws, a dial indicator, handset and antenna plugs; the
TA-57 has a smooth handset shape, an inductor crank with a handle, latches; the boxes have
locks with a lever and a bracket, handles on brackets, corner pieces; the reel has a hub,
windows in the cheeks, cable turns; the antenna has a clamp with a thumbscrew and a
matching unit. Small items are vanilla proxy things (DECOR): papers, a flashlight, a D
battery, insulating tape, pliers, a screwdriver, an electrician's kit, rags.

Machine look: the CRT screen is ozl_screen, its own screen section (frames.py frames: lines
crawl, the progress bar grows, a sweep runs, the cursor blinks), the laptop screen is
ozl_screen_2, the screen_2 section (the selection frame walks over the tree, the progress
line grows); the power lamps (CRT, laptop) are ozl_lamp, steady (the _on atlas); the laptop
disk lamp and the radio transmit lamp are ozl_lamp_2, blinking; the radio indicator needle
is the bone ozl_needle on the source ozl_needle (wobble), drawn in the middle of the scale,
the swing is +-NEEDLE_A. LODs: the middle one has no small items (louvres, terminals,
pencil, seal, plugs) and simpler wires; the far one has boxes, no wires and no whip
antenna.

Blender axes: X - width, Y - depth (front at -Y), Z - up.
"""
import math
import os
import sys

from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import frames as kf  # noqa: E402
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import krender  # noqa: E402
import kvanilla as kv  # noqa: E402
import layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
TOP = L.TOP

LOD_SPECS = [
    dict(lod=0, sides=12),
    dict(lod=1, sides=6),
    dict(lod=2, sides=4),
]

REGIONS = {
    "t_top": ("olive_top", 0.9), "t_frame": ("olive_frame", 0.8), "rubber": ("rubber", 0.5),
    "box1": ("olive_box1", 0.9), "box2": ("olive_box2", 0.9), "box_plain": ("olive_box", 0.6),
    "hw": ("steel_dark", 1.2), "seal": ("lead", 2.0),
    "reel": ("olive_reel", 0.9), "coil": ("coil", 1.0),
    "crt_case": ("olive_crt", 1.0), "crt_bezel": ("olive_bezel", 1.4), "mask": ("black", 1.0),
    "tag": ("tag", 2.0), "vent": ("vent", 1.0),
    "lap": ("laptop", 1.4), "lap_lid": ("laptop_lid", 1.2), "keys": ("keys", 3.5),
    "pad": ("touchpad", 2.0), "black": ("black", 1.2),
    "radio": ("radio", 1.6), "radio_plain": ("radio_plain", 0.7), "knob": ("knob", 1.8), "metal": ("chrome", 1.4),
    "meter": ("meter_face", 4.0),
    "bake": ("bakelite", 1.2), "ph_inner": ("ph_inner", 1.4), "ph_lid_in": ("bakelite_in", 1.2),
    "white": ("plastic_white", 1.5),
    "book": ("book", 1.2), "paper": ("paper", 1.2), "pencil": ("pencil", 1.5),
    "cable": ("cable", 0.8), "cable_f": ("cable_field", 0.8), "ant": ("ant", 1.0),
    "led_g": ("led_g", 1.0), "led_a": ("led_a", 1.0), "lamp_r": ("lamp_r", 1.0),
}

# =============================================================================
# Materials
# =============================================================================


def build_worn(mat, origin, color, bare=kmats.lin((104, 104, 106)), primer=kmats.lin((96, 46, 34)), seed=1.0,
               gloss=0.28, spec=0.22, wear=(0.68, 0.73), edge_k=0.75, rub=(), touch=0.0, scratch=0.0,
               floor_z=0.0, dust=0.2, grime=0.3, decal_items=()):
    """SOP olive - the builder of M32/M33/M35 (without soot): old army paint, worn off on the
    edges (edge_k) and where hands grab (rub - [(center, half-axes, strength)]), primer under
    it, bare metal in the middle of a spot; touch - touch-up patches. No rust.
    """
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket

    def near(c, r):
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
        return t.maprange(ln.outputs["Value"], 0.25, 1.0, 1.0, 0.0)

    base = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                  tuple(c * 0.88 for c in color[:3]) + (1,), color)
    base = t.mixc(t.math("MULTIPLY", t.maprange(t.noise(vec, 0.9, 4.0, 0.5), 0.45, 0.75, 0.0, 1.0), 0.35), base,
                  tuple(min(1.0, c * 1.25 + 0.01) for c in color[:3]) + (1,))
    col = kmats.decals(t, base, sep, nsep, decal_items)
    edge = t.maprange(t.edge_wear(0.004), 0.05, 0.22, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 11.0, 10.0, 0.7), 0.75), t.math("MULTIPLY", edge, edge_k))
    grain = t.maprange(t.noise(vec, 34.0, 8.0, 0.7), 0.3, 0.7, 0.55, 1.0)
    for c, r, k in rub:
        f = t.math("ADD", f, t.math("MULTIPLY", t.math("MULTIPLY", near(c, r), grain), k))
    tp = None
    if touch > 0:
        tp = t.step(t.noise(vec, 3.2, 5.0, 0.55), 1.0 - touch * 0.5, 1.0 - touch * 0.5 + 0.02)
        f = t.math("SUBTRACT", f, t.math("MULTIPLY", tp, 0.6))
    worn = t.step(f, wear[0], wear[1])
    deep = t.step(f, wear[1] + 0.05, wear[1] + 0.09)
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
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g_, s_, h)


def wdecal(name):
    return os.path.join(WORK, name)


def decal_y(name, x0, x1, z0, z1, y, depth=(-0.003, 0.003)):
    """A decal on a face looking toward -y at depth y + depth."""
    return (wdecal(name), "y", -1, ("x", "z"), ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0),
            (y + depth[0], y + depth[1]))


def decal_spec_y(name, s, y):
    return decal_y(name, s["x"] - s["w"] / 2, s["x"] + s["w"] / 2, s["z"] - s["h"] / 2, s["z"] + s["h"] / 2, y)


def decal_z(name, x0, x1, y0, y1, z0, z1):
    return (wdecal(name), "z", 1, ("x", "y"), ((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0, y1 - y0), (z0, z1))


B1, B2 = L.BOX1, L.BOX2
BOX1_DECALS = [decal_spec_y("decal_box1.png", L.BOX1_NUM, B1["y0"]), decal_spec_y("decal_box1_band.png", L.BOX1_BAND,
                                                                               B1["y0"])]
BOX2_DECALS = [decal_spec_y("decal_box2.png", L.BOX2_NUM, B2["y0"])]
_cn = L.CRT_NUM
CRT_DECALS = [(wdecal("decal_crt_num.png"), "x", -1, ("y", "z"), (_cn["y"], _cn["z"]), (-_cn["w"], _cn["h"]),
               (L.MX0 - 0.003, L.MX0 + 0.003))]
RADIO_DECALS = [decal_z("decal_radio.png", *L.R_PANEL, L.RZ1 - 0.002, L.RZ1 + 0.002)]
KEYS_DECAL = decal_z("decal_keys.png", *L.KEYS, TOP + L.LB_H, TOP + L.LB_H + 0.004)

OLIVE = kmats.lin((80, 86, 56))                              # M32-M35 olive
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
OLV = dict(color=OLIVE, seed=2.1, touch=0.35, scratch=0.3, floor_z=0.0, dust=0.18, grime=0.3)
# where hands grab: the front table edge by the laptop and the telephone, the CRT handles, the box
# lids
TOP_RUB = [((L.LXC, L.TY0, TOP), (0.20, 0.05, 0.03), 0.45), ((0.0, L.TY0, TOP), (0.18, 0.05, 0.03), 0.35),
           ((0.35, L.TY0, TOP), (0.15, 0.06, 0.03), 0.3), ((0.0, 0.0, TOP), (0.45, 0.25, 0.02), 0.12)]
CRT_RUB = [((L.MX0 + 0.017, L.MY0, TOP + 0.18), (0.03, 0.04, 0.14), 0.45),
           ((L.MX1 - 0.017, L.MY0, TOP + 0.18), (0.03, 0.04, 0.14), 0.45),
           ((L.MX, L.MY0, TOP + 0.05), (0.10, 0.03, 0.03), 0.3)]
BOX_RUB = [((B1["x0"] + 0.10, B1["y0"], B1["h"] - 0.03), (0.05, 0.04, 0.05), 0.4),
           ((B1["x1"] - 0.10, B1["y0"], B1["h"] - 0.03), (0.05, 0.04, 0.05), 0.4),
           ((B2["x0"] + 0.14, (B2["y0"] + B2["y1"]) / 2, B2["h"]), (0.06, 0.04, 0.03), 0.4)]
LAPTOP = dict(color=kmats.lin((44, 45, 46)), bare=kmats.lin((118, 118, 116)), primer=kmats.lin((64, 64, 64)), seed=6.1,
              gloss=0.30, spec=0.25, wear=(0.70, 0.75), edge_k=0.8, scratch=0.4, floor_z=TOP, dust=0.25, grime=0.25,
              rub=[((L.LXC, L.LY0, TOP + 0.02), (0.12, 0.03, 0.03), 0.45),
                   ((L.LXC, L.LY0 + 0.05, TOP + L.LB_H), (0.12, 0.05, 0.01), 0.3)])
RADIO = dict(color=kmats.lin((76, 84, 70)), bare=kmats.lin((120, 122, 118)), seed=7.3, wear=(0.69, 0.74), edge_k=0.9,
             touch=0.25, scratch=0.4, floor_z=TOP, dust=0.2, grime=0.3)

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "olive_top": (build_worn, dict(OLV, seed=1.7, bare=kmats.lin((168, 140, 98)), primer=kmats.lin((122, 100, 70)),
                                   wear=(0.66, 0.71), edge_k=1.0, scratch=0.7, rub=TOP_RUB, floor_z=TOP, dust=0.2)),
    "olive_frame": (build_worn, dict(OLV, seed=1.9, wear=(0.66, 0.71), edge_k=0.9)),
    "olive_box1": (build_worn, dict(OLV, seed=2.3, rub=BOX_RUB, decal_items=BOX1_DECALS)),
    "olive_box2": (build_worn, dict(OLV, seed=2.6, rub=BOX_RUB, decal_items=BOX2_DECALS)),
    "olive_box": (build_worn, dict(OLV, seed=2.9, wear=(0.64, 0.70), edge_k=1.0, rub=BOX_RUB)),
    "olive_reel": (build_worn, dict(OLV, seed=3.2, wear=(0.64, 0.70), edge_k=1.0, scratch=0.5)),
    "olive_crt": (build_worn, dict(OLV, seed=3.5, floor_z=TOP, decal_items=CRT_DECALS, rub=CRT_RUB)),
    "olive_bezel": (build_worn, dict(OLV, seed=3.8, wear=(0.67, 0.72), edge_k=0.9, floor_z=TOP, rub=CRT_RUB)),
    # hardware (handles, locks, tripod, reel frame): steel under black paint, worn on the edges
    "steel_dark": (build_worn, dict(color=kmats.lin((34, 35, 33)), bare=kmats.lin((112, 112, 110)),
                                    primer=kmats.lin((58, 58, 56)), seed=5.1, wear=(0.62, 0.68), edge_k=1.1,
                                    gloss=0.32, spec=0.3, dust=0.2, grime=0.3)),
    "lead": ("plastic", dict(color=kmats.lin((108, 108, 110)), gloss=0.35, spec=0.3, mottle=0.2, dust=0.2, grime=0.3)),
    "coil": ("plastic", dict(color=kmats.lin((44, 50, 38)), gloss=0.3, spec=0.2, mottle=0.25, dust=0.35, grime=0.3)),
    "tag": ("steel", dict(seed=7.2, tone=0.52, along="x", gloss=0.5, spec=0.6, dust=0.1, grime=0.2)),
    "vent": ("plastic", dict(color=kmats.lin((16, 16, 15)), gloss=0.1, spec=0.05, dust=0.2)),
    "laptop": (build_worn, LAPTOP),
    "laptop_lid": (build_worn, dict(LAPTOP, seed=6.4, rub=())),
    "keys": ("paint", dict(CLEAN, color=kmats.lin((20, 20, 21)), gloss=0.35, spec=0.25, decal_items=[KEYS_DECAL])),
    "touchpad": ("plastic", dict(color=kmats.lin((34, 34, 35)), gloss=0.15, spec=0.1, mottle=0.1, dust=0.2,
                                 scuff=(0.6, 0.7))),
    "radio": (build_worn, dict(RADIO, decal_items=RADIO_DECALS)),
    "radio_plain": (build_worn, dict(RADIO, seed=7.6)),
    "knob": ("plastic", dict(color=kmats.lin((22, 21, 20)), gloss=0.5, spec=0.4, dust=0.15, scuff=(0.66, 0.74))),
    "chrome": ("steel", dict(seed=6.6, tone=0.24, along="z", gloss=0.7, spec=0.8, dust=0.1, grime=0.25)),
    # dial indicator scale: cream, yellowed, no text
    "meter_face": ("plastic", dict(color=kmats.lin((206, 198, 170)), gloss=0.35, spec=0.2, mottle=0.1, dust=0.08,
                                   grime=0.2, scuff=(0.9, 1.0))),
    # TA-57: bakelite, brown-black with streaks (from M61), the inside of the body is black, the
    # lids are brown
    "bakelite": ("plastic", dict(color=kmats.lin((60, 32, 22)), gloss=0.62, spec=0.45, mottle=0.3, floor_z=TOP,
                                 dust=0.1, grime=0.25, scuff=(0.62, 0.7))),
    "bakelite_in": ("plastic", dict(color=kmats.lin((88, 40, 24)), gloss=0.7, spec=0.5, mottle=0.45, floor_z=TOP,
                                    dust=0.05, grime=0.15, scuff=(0.7, 0.78))),
    "ph_inner": ("plastic", dict(color=kmats.lin((18, 18, 18)), gloss=0.45, spec=0.35, mottle=0.1, dust=0.1,
                                 scuff=(0.7, 0.78))),
    "book": ("plastic", dict(color=kmats.lin((66, 80, 58)), gloss=0.15, spec=0.08, mottle=0.2, dust=0.15,
                             grime=0.35, scuff=(0.62, 0.7))),
    "paper": ("plastic", dict(color=kmats.lin((212, 202, 172)), gloss=0.06, spec=0.03, mottle=0.12, dust=0.1,
                              grime=0.2, scuff=(0.9, 1.0))),
    "pencil": ("plastic", dict(color=kmats.lin((150, 40, 28)), gloss=0.5, spec=0.35, dust=0.1, scuff=(0.7, 0.8))),
    "cable": ("plastic", dict(color=kmats.lin((24, 24, 24)), gloss=0.35, spec=0.25, dust=0.3)),
    "cable_field": ("plastic", dict(color=kmats.lin((40, 48, 34)), gloss=0.3, spec=0.2, dust=0.35, grime=0.3)),
    "ant": ("steel", dict(seed=8.1, tone=0.20, along="z", gloss=0.45, spec=0.55, dust=0.15, grime=0.2)),
    "led_g": ("flat", dict(color=kmats.lin((34, 64, 40)), gloss=0.85, spec=0.8)),
    "led_g_on": ("flat", dict(color=kmats.lin((130, 255, 140)), gloss=0.85, spec=0.8)),
    "led_a": ("flat", dict(color=kmats.lin((80, 56, 22)), gloss=0.85, spec=0.8)),
    "led_a_on": ("flat", dict(color=kmats.lin((255, 176, 40)), gloss=0.85, spec=0.8)),
    "lamp_r": ("flat", dict(color=kmats.lin((90, 22, 18)), gloss=0.85, spec=0.8)),
    "lamp_r_on": ("flat", dict(color=kmats.lin((255, 80, 56)), gloss=0.85, spec=0.8)),
})

OBJ, NAME = "m36_sop_terminal", "ozr_sop_terminal"
# Machine look: the screens are their own sections with frames (OZL_WorkFx frames), the
# power lamps use the _on atlas (steady), the disk lamp and the transmit lamp alternate the
# _on atlas with the normal one (blink), the indicator needle is a bone on the source
# ozl_needle (wobble).
SEL_SCREEN, SEL_SCREEN2, SEL_LAMP, SEL_LAMP2 = "ozl_screen", "ozl_screen_2", "ozl_lamp", "ozl_lamp_2"
SEL_NEEDLE = "ozl_needle"
NEEDLE_A = math.radians(45)                                  # needle swing from the scale middle: to the end ticks
NEEDLE_MID, NEEDLE_AMP = 0.62, 0.07                          # needle while working: wobble mid +- amp
# The needle is drawn in the middle of the scale: phase 0 is the left edge (zero), 1 the
# right one (red ticks). The axis is the memory points ozl_needle_axis, up, toward someone
# looking at the radio from above. The engine turns a bone with a right-hand screw in DayZ
# axes (kexport.conv, determinant -1); in Blender axes this is a left-hand screw around the
# axis from the first point to the second: an axis pointing at the viewer gives a positive
# angle clockwise for them (as in M08, M12, M14, M33). So angle0 = -45 degrees (the left
# tick), angle1 = +45 degrees (the right one): the swing follows the scale ticks exactly.
NEEDLE_ANIM = ("ozl_needle_swing", dict(type="rotation", source="ozl_needle", selection=SEL_NEEDLE,
                                        axis="ozl_needle_axis", memory=1, minValue=0.0, maxValue=1.0,
                                        angle0=-NEEDLE_A, angle1=NEEDLE_A))
FR = kf.make(WORK)                                           # frames from decals (Blender, numpy)
SCREEN = dict(off="decal_crt_off.png", frames=FR["crt"], size=256, gloss=0.85)
SCREEN2 = dict(off="decal_lcd_off.png", frames=FR["lcd"], size=256, gloss=0.6)
ON_MOVE = {}                                                 # working look marker for the needle pose (_posed below)
ON = dict(remap={"led_g": "led_g_on", "led_a": "led_a_on", "lamp_r": "lamp_r_on"}, emissive=(1.0, 1.0, 1.0, 1.0),
          move=ON_MOVE)

# Dial indicator on the radio panel - in place of the upper blank nameplate (make_decals:
# x0 + 0.03 .. + 0.10, y 0.234 .. 0.256): body 74 x 34, scale 62 x 24, the needle axis at the
# near edge
MET_X, MET_Y = L.RX0 + 0.075, 0.249
MET_PIV = (MET_X, MET_Y - 0.0095)
MET_Z = L.RZ1 + 0.009                                        # scale face
NEEDLE_L = 0.0185
NEEDLE_AXIS = [(MET_PIV[0], MET_PIV[1], MET_Z), (MET_PIV[0], MET_PIV[1], MET_Z + 0.02)]   # up, toward the person


def engine_rot(phase):
    """Rotation matrix of the needle bone at a source phase, as the engine would make it by the
    memory axis NEEDLE_AXIS: the angle angle0 + (angle1 - angle0) * phase, in Blender axes - a
    right-hand screw around the opposite axis (from the second point to the first).
    """
    d = NEEDLE_ANIM[1]
    ang = d["angle0"] + (d["angle1"] - d["angle0"]) * phase
    a, b = Vector(NEEDLE_AXIS[0]), Vector(NEEDLE_AXIS[1])
    return Matrix.Translation(a) @ Matrix.Rotation(ang, 4, a - b) @ Matrix.Translation(-a)


def check_needle():
    """Numeric check: the engine's turn puts the needle at phase 0 on the left tick of the scale,
    at mid +- amp to the right of the middle, at 1 on the right (red) tick: clockwise as seen
    looking at the radio from above. If it does not match, the build fails.
    """
    c = Vector((MET_PIV[0], MET_PIV[1], MET_Z + 0.001))
    tip = c + Vector((0.0, NEEDLE_L, 0.0))                                       # drawn in the middle, toward +Y
    seen = []
    for ph in (0.0, NEEDLE_MID - NEEDLE_AMP, NEEDLE_MID, NEEDLE_MID + NEEDLE_AMP, 1.0):
        q = engine_rot(ph) @ tip
        deg = math.degrees(math.atan2(q.x - c.x, q.y - c.y))                     # from the middle, clockwise, above
        assert abs(deg - (-45.0 + 90.0 * ph)) < 0.01, "the needle goes the wrong way: %.1f" % deg
        seen.append("%.2f -> %.1f" % (ph, deg))
    print("turns ok: needle (phase -> degrees from the scale middle, plus is right) " + ", ".join(seen))


check_needle()

# Vanilla DayZ proxy items (kvanilla): the preview shows blue boxes of their size. Flat ones
# - kv.flat. The table brace runs 0.34 above the spares box: on the lid only flat things in
# front of it and behind it (a GP-5 0.26 high and 0.21 deep does not fit on any box - so
# there is none).
DECOR = [
    kv.put("paper", (-0.335, 0.125, TOP), lift=0.0006, **kv.flat(86)),            # two sheets behind laptop
    kv.put("paper", (-0.330, 0.140, TOP), lift=0.0012, **kv.flat(97)),
    kv.put("batteryd", (0.247, -0.020, TOP)),                                      # between CRT, radio
    kv.put("flashlight", (0.247, 0.170, TOP), up=(0, 0, 1), fwd=(-1, 0, 0)),
    kv.put("ducttape", (0.105, 0.215, L.MZ1), lift=0.0013, **kv.flat(0)),         # CRT shell, rear
    kv.put("pliers", (-0.270, -0.090, B1["h"]), **kv.flat(180)),                  # box lid, before brace
    kv.put("screwdriver", (-0.025, -0.095, B1["h"]), **kv.flat(172)),
    kv.put("electrickit", (-0.250, 0.100, B1["h"]), **kv.flat(3)),                # box lid, behind brace
    kv.put("rags", (-0.240, -0.255, 0.0), **kv.flat(4)),                           # floor, in front of box
]

M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 selections=(SEL_SCREEN, SEL_SCREEN2, SEL_LAMP, SEL_LAMP2, SEL_NEEDLE),
                 hidden=(SEL_SCREEN, SEL_SCREEN2, SEL_LAMP, SEL_LAMP2), states={"on": ON},
                 bones=((SEL_NEEDLE, ""),), animations=(NEEDLE_ANIM,), decor=DECOR,
                 panels={"screen": SCREEN, "screen_2": SCREEN2}, sources={"ozl_needle": dict(animPeriod=0.2)})
P = M.part
BOUNDS = {}


def use(part, region):
    """The following primitives of the part go into another region."""
    return part.use(region, *REGIONS[region])


# =============================================================================
# Primitives that kgeo lacks
# =============================================================================
def turn(cx, cy, z, deg):
    """Local axes rotated about the vertical: u along the object, v across it, n up."""
    a = math.radians(deg)
    return g.Frame((cx, cy, z), (math.cos(a), math.sin(a), 0), (-math.sin(a), math.cos(a), 0), (0, 0, 1))


def spline(pts, k):
    """Polyline -> smooth curve through the same points (Catmull-Rom, from M24/M31)."""
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


def rounded(pts, r, k=3):
    """Polyline -> the same straight runs with rounded corners (an arc of radius ~r, k segments):
    handles, brackets, frames.
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
        t = min(r / max(math.tan(ang / 2), 1e-3), l1 * 0.45, l2 * 0.45)
        p1, p2 = b + d1 * t, b + d2 * t
        for s in range(k + 1):
            u = s / k
            out.append((1 - u) ** 2 * p1 + 2 * (1 - u) * u * b + u * u * p2)
    out.append(v[-1])
    return [tuple(q) for q in out]


def cable(name, region, pts, r, lod, sides=6):
    c = P(name, region)
    if lod == 0:
        g.pipe(c, spline(pts, 2), r, sides)
    else:
        g.pipe(c, pts[::2] + ([pts[-1]] if len(pts) % 2 == 0 else []), r, 3)
    return [c]


def rnd(lod, r, seg=2):
    """Rounding of visible edges: only in the near LOD (middle and far are boxes, ~20 and ~6%)."""
    return dict(r=r, seg=seg) if lod == 0 else {}


def front_quad(part, x0, x1, z0, z1, y):
    """A single face looking toward -y (far LOD: screen, lamp)."""
    return g.quad(part, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)])


def top_quad(part, x0, x1, y0, y1, z):
    return g.quad(part, [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)])


def bulge(part, x0, x1, z0, z1, y_edge, sag, nu, nv):
    """Convex CRT glass: an nu x nv grid facing -y, the edges at y_edge, the center at
    y_edge - sag (from M31).
    """
    bm = part.bm
    vs = []
    for j in range(nv + 1):
        row = []
        for i in range(nu + 1):
            a, b = 2.0 * i / nu - 1.0, 2.0 * j / nv - 1.0
            y = y_edge - sag * (1 - a * a) * (1 - b * b)
            row.append(bm.verts.new((x0 + (x1 - x0) * i / nu, y, z0 + (z1 - z0) * j / nv)))
        vs.append(row)
    faces = []
    for j in range(nv):
        for i in range(nu):
            faces.append(bm.faces.new([vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]]))
    return part.tag(faces)


def mark(part, cx, cy, z, deg, r0, r1, w=0.0007):
    """A tick on the knob end: from r0 to r1 from the axis toward deg, a thin plate above the
    end.
    """
    g.box(part, r0, r1, -w, w, 0.0, 0.0005, frame=turn(cx, cy, z, deg))


# =============================================================================
# Folding table
# =============================================================================
def build_table(spec):
    lod, n = spec["lod"], spec["sides"]
    top = P("table_top", "t_top")
    g.box(top, L.TX0, L.TX1, L.TY0, L.TY1, TOP - L.PLY, TOP, **rnd(lod, 0.004))
    parts = [top]
    zb = TOP - L.PLY - L.APRON
    fr = P("table_frame", "t_frame")
    if lod == 2:
        g.box(fr, L.TX0 + 0.004, L.TX1 - 0.004, L.TY0 + 0.004, L.TY1 - 0.004, zb, TOP - L.PLY)
    else:
        w = 0.004
        g.box(fr, L.TX0 + 0.002, L.TX1 - 0.002, L.TY0 + 0.002, L.TY0 + 0.002 + w, zb, TOP - L.PLY)
        g.box(fr, L.TX0 + 0.002, L.TX1 - 0.002, L.TY1 - 0.002 - w, L.TY1 - 0.002, zb, TOP - L.PLY)
        g.box(fr, L.TX0 + 0.002, L.TX0 + 0.002 + w, L.TY0 + 0.006, L.TY1 - 0.006, zb, TOP - L.PLY)
        g.box(fr, L.TX1 - 0.002 - w, L.TX1 - 0.002, L.TY0 + 0.006, L.TY1 - 0.006, zb, TOP - L.PLY)
        if lod == 0:                                                             # bottom angle shelf
            for y0, y1 in ((L.TY0 + 0.006, L.TY0 + 0.032), (L.TY1 - 0.032, L.TY1 - 0.006)):
                g.box(fr, L.TX0 + 0.006, L.TX1 - 0.006, y0, y1, zb, zb + 0.004)
    parts.append(fr)
    # X-shaped supports at the ends and the brace through the axes
    lg = P("table_legs", "t_frame")
    zt = zb - 0.004
    zc = (L.LEG_R + zt) / 2
    sides = 10 if lod == 0 else (5 if lod == 1 else 4)
    for sx in (-1, 1):
        x = sx * L.LEG_X
        g.pipe(lg, [(x - 0.016, -L.LEG_Y, L.LEG_R), (x - 0.016, L.LEG_Y, zt)], L.LEG_R, sides)
        g.pipe(lg, [(x + 0.016, L.LEG_Y, L.LEG_R), (x + 0.016, -L.LEG_Y, zt)], L.LEG_R, sides)
    g.pipe(lg, [(-L.LEG_X + 0.004, 0.0, zc), (L.LEG_X - 0.004, 0.0, zc)], 0.011, sides)
    parts.append(lg)
    if lod > 0:
        return parts
    hw = P("table_hw", "hw")
    for sx in (-1, 1):
        x = sx * L.LEG_X
        g.cyl(hw, (x, 0.0, zc), "x", 0.014, 0.05, 12)                            # support pin
        for y in (-L.LEG_Y, L.LEG_Y):                                            # brackets at the frame
            g.box(hw, x - 0.032, x + 0.032, y - 0.025, y + 0.025, zt - 0.004, zb + 0.002)
    # angle plates at the tabletop corners: outside and below, the top flush with the plywood
    # (they do not protrude onto the table)
    for sx in (-1, 1):
        for sy in (-1, 1):
            X, Y = sx * L.TX1, sy * L.TY1
            g.box(hw, *sorted((X - sx * 0.03, X + sx * 0.0015)), *sorted((Y - sy * 0.03, Y + sy * 0.0015)),
                  TOP - L.PLY - 0.003, TOP - 0.0006)
    parts.append(hw)
    rb = P("table_feet", "rubber")                                               # rubber shoes at the support ends
    for sx in (-1, 1):
        x = sx * L.LEG_X
        for dx, y in ((-0.016, -L.LEG_Y), (0.016, L.LEG_Y)):
            g.cyl(rb, (x + dx, y, 0.011), "z", 0.017, 0.022, 10)
    parts.append(rb)
    return parts


# =============================================================================
# Laptop of the CF-27 class
# =============================================================================
def build_laptop(spec):
    lod, n = spec["lod"], spec["sides"]
    x0, x1, y0, y1 = L.LX0, L.LX1, L.LY0, L.LY1
    zt = TOP + L.LB_H
    bs = P("laptop", "lap")
    g.box(bs, x0, x1, y0, y1, TOP, zt, **rnd(lod, 0.007))
    o, u, v, nn = L.lid_axes()
    fr = g.Frame(o, u, v, nn)
    ld = P("laptop_lid", "lap_lid")
    a0, a1 = L.LXC - L.LCD_W / 2, L.LXC + L.LCD_W / 2
    b0, b1 = L.LCD_B, L.LCD_B + L.LCD_H
    if lod == 2:
        g.box(ld, x0, x1, 0.0, L.LID_D, -L.LID_T, 0.0, frame=fr)
        cs = 0.001
    else:
        # lid back and the screen frame; the screen is recessed by 2.5 mm
        g.box(ld, x0, x1, 0.0, L.LID_D, -L.LID_T, -0.003, frame=fr, **rnd(lod, 0.007))
        e = 0.004 if lod == 0 else 0.0
        for q in ((x0 + e, x1 - e, e, b0), (x0 + e, x1 - e, b1, L.LID_D - e), (x0 + e, a0, b0, b1), (a1, x1 - e, b0, b1)):
            g.box(ld, q[0], q[1], q[2], q[3], -0.0035, 0.0, frame=fr)
        cs = -0.0025
    sc = P("laptop_lcd", "black", group=SEL_SCREEN2, section="screen_2")
    g.quad(sc, [tuple(fr.p(a0, b0, cs)), tuple(fr.p(a1, b0, cs)), tuple(fr.p(a1, b1, cs)), tuple(fr.p(a0, b1, cs))])
    sc.glass_frame = (fr, a0, a1, b0, b1)
    # LEDs: power and battery are steady (ozl_lamp), the disk blinks (ozl_lamp_2)
    led = P("laptop_leds", "led_g", group=SEL_LAMP)
    hdd = P("laptop_led_hdd", "led_a", group=SEL_LAMP2)
    for dx, part in ((-0.014, led), (0.0, led), (0.014, hdd)):
        lx, ly = L.LXC + dx, y0 + 0.016
        if lod == 2:
            top_quad(part, lx - 0.003, lx + 0.003, ly - 0.002, ly + 0.002, zt + 0.0008)
        else:
            g.box(part, lx - 0.003, lx + 0.003, ly - 0.002, ly + 0.002, zt - 0.001, zt + 0.0012)
    parts = [bs, ld, sc, led, hdd]
    # handle at the front, folded down: a grip, links, hinges on the body
    hd = P("laptop_handle", "black")
    if lod == 0:
        g.box(hd, L.LXC - 0.078, L.LXC + 0.078, y0 - 0.030, y0 - 0.014, TOP + 0.006, TOP + 0.026, r=0.006, seg=2)
        for s in (-1, 1):
            g.box(hd, *sorted((L.LXC + s * 0.070, L.LXC + s * 0.094)), y0 - 0.026, y0 - 0.004, TOP + 0.010,
                  TOP + 0.022)
            g.box(hd, *sorted((L.LXC + s * 0.088, L.LXC + s * 0.124)), y0 - 0.013, y0 + 0.001, TOP + 0.006,
                  TOP + 0.030, r=0.003, seg=1)
    else:
        g.box(hd, L.LXC - 0.085, L.LXC + 0.085, y0 - 0.030, y0 - 0.012, TOP + 0.004, TOP + 0.028)
    parts.append(hd)
    if lod == 2:
        return parts
    kb = P("laptop_keys", "keys")
    kx0, kx1, ky0, ky1 = L.KEYS
    g.box(kb, kx0, kx1, ky0, ky1, zt - 0.001, zt + 0.0015)
    parts.append(kb)
    tp = P("laptop_pad", "pad")
    px, py, pw, pd = L.TPAD
    g.box(tp, px - pw / 2, px + pw / 2, py - pd / 2, py + pd / 2, zt - 0.001, zt + 0.0006)
    for s in (-1, 1):                                                            # touchpad buttons
        g.box(tp, px + s * 0.016 - 0.014, px + s * 0.016 + 0.014, py - pd / 2 - 0.016, py - pd / 2 - 0.004,
              zt - 0.001, zt + 0.0012)
    parts.append(tp)
    if lod > 0:
        return parts
    bp = P("laptop_bumpers", "rubber")                                           # rubber corners
    for xa, xb in ((x0 - 0.003, x0 + 0.022), (x1 - 0.022, x1 + 0.003)):
        g.box(bp, xa, xb, y0 - 0.003, y0 + 0.022, TOP + 0.001, zt + 0.0015, r=0.004, seg=1)
        g.box(bp, xa, xb, L.LID_D - 0.022, L.LID_D + 0.003, -L.LID_T - 0.002, 0.0012, frame=fr, r=0.004, seg=1)
    parts.append(bp)
    bk = P("laptop_bits", "black")
    for s in (-1, 1):                                                            # lid hinges
        g.cyl(bk, (L.LXC + s * 0.085, y1 - 0.010, zt + 0.008), "x", 0.010, 0.06, 12)
    g.box(bk, L.LXC - 0.03, L.LXC + 0.03, L.LID_D - 0.006, L.LID_D + 0.006, -0.020, 0.002, frame=fr,
          r=0.002, seg=1)                                                        # lid latch
    for a, b in ((x0 + 0.012, 0.012), (x1 - 0.012, 0.012), (x0 + 0.030, L.LID_D - 0.010),
                 (x1 - 0.030, L.LID_D - 0.010)):                                 # screen frame screws
        g.cyl(bk, (a, b, 0.0006), "z", 0.0025, 0.0012, 6, frame=fr)
    for k in range(4):                                                           # grille on the left side
        yy = y0 + 0.05 + 0.012 * k
        g.box(bk, x0 - 0.0012, x0 + 0.001, yy, yy + 0.006, TOP + 0.010, TOP + 0.026)
    for xs, sg in ((x0, -1), (x1, 1)):                                           # port covers on the sides
        g.box(bk, *sorted((xs - sg * 0.001, xs + sg * 0.0015)), y0 + 0.11, y0 + 0.18, TOP + 0.009, TOP + 0.027)
    parts.append(bk)
    return parts


# =============================================================================
# 14 in CRT in a steel shell
# =============================================================================
def build_crt(spec):
    lod, n = spec["lod"], spec["sides"]
    x0, x1, y0, y1, z0, z1 = L.MX0, L.MX1, L.MY0, L.MY1, L.MZ0, L.MZ1
    yb = y0 + L.BEZ_T
    wx0, wx1 = L.MX - L.WIN_W / 2, L.MX + L.WIN_W / 2
    wz0, wz1 = L.WIN_Z - L.WIN_H / 2, L.WIN_Z + L.WIN_H / 2
    cs = P("crt_case", "crt_case")
    g.box(cs, x0, x1, yb - 0.002, y1, z0, z1, **rnd(lod, 0.008))
    if lod == 0:
        # front frame is one part: a rounded box minus a window with rounded corners and a lip
        base = P("crt_bezel_raw", "crt_bezel")
        g.box(base, x0, x1, y0, yb, z0, z1, r=0.006, seg=2)
        cut = P("crt_bezel_cut", "crt_bezel")
        g.box(cut, wx0, wx1, y0 - 0.002, yb + 0.010, wz0, wz1, r=0.012, seg=2)
        bz = M.boolean("crt_bezel", base, [cut])
    else:
        bz = P("crt_bezel", "crt_bezel")
        if lod == 2:
            g.box(bz, x0, x1, y0, yb, z0, z1)
        else:
            g.box(bz, x0, wx0, y0, yb, z0, z1)
            g.box(bz, wx1, x1, y0, yb, z0, z1)
            g.box(bz, wx0, wx1, y0, yb, wz1, z1)
            g.box(bz, wx0, wx1, y0, yb, z0, wz0)
    parts = [cs, bz]
    sx0, sx1 = L.MX - L.CRT_W / 2, L.MX + L.CRT_W / 2
    sz0, sz1 = L.WIN_Z - L.CRT_H / 2, L.WIN_Z + L.CRT_H / 2
    sc = P("crt_glass", "black", group=SEL_SCREEN, section="screen")
    if lod == 2:
        front_quad(sc, sx0, sx1, sz0, sz1, y0 - 0.001)
    else:
        mk = P("crt_mask", "mask")
        g.box(mk, wx0 + 0.001, wx1 - 0.001, y0 + L.CRT_EDGE, yb, wz0 + 0.001, wz1 - 0.001)
        parts.append(mk)
        nu, nv = (10, 8) if lod == 0 else (4, 3)
        bulge(sc, sx0, sx1, sz0, sz1, y0 + L.CRT_EDGE - 0.001, L.CRT_SAG, nu, nv)
    sc.glass_frame = (g.WORLD, sx0, sx1, sz0, sz1)
    parts.append(sc)
    ld = P("crt_led", "led_g", group=SEL_LAMP)
    lx, lz = x1 - 0.055, z0 + 0.040
    if lod == 2:
        front_quad(ld, lx - 0.003, lx + 0.003, lz - 0.003, lz + 0.003, y0 - 0.001)
    else:
        g.cyl(ld, (lx, y0 - 0.0015, lz), "y", 0.003, 0.003, 8 if lod == 0 else 5)
    parts.append(ld)
    # handles at the front, like a rack instrument: a bracket of arcs on two feet
    hd = P("crt_handles", "hw")
    hz0, hz1 = z0 + 0.05, z1 - 0.05
    for hx in (x0 + 0.017, x1 - 0.017):
        if lod > 0:
            g.box(hd, hx - 0.006, hx + 0.006, y0 - 0.035, y0, hz0, hz1)
            continue
        g.pipe(hd, rounded([(hx, y0 + 0.002, hz0), (hx, y0 - 0.034, hz0), (hx, y0 - 0.034, hz1),
                            (hx, y0 + 0.002, hz1)], 0.012, 3), 0.0065, 8)
        for z in (hz0, hz1):
            g.box(hd, hx - 0.011, hx + 0.011, y0 - 0.005, y0 + 0.001, z - 0.013, z + 0.013)
    parts.append(hd)
    if lod > 0:
        return parts
    rb = P("crt_feet", "rubber")
    for fx in (x0 + 0.03, x1 - 0.03):
        for fy in (y0 + 0.04, y1 - 0.04):
            g.box(rb, fx - 0.02, fx + 0.02, fy - 0.02, fy + 0.02, TOP, z0 + 0.001)
    parts.append(rb)
    kn = P("crt_knobs", "knob")                                                  # brightness, contrast, size
    wm = P("crt_marks", "white")
    for k, kx in enumerate((L.MX - 0.10, L.MX - 0.07, L.MX - 0.04)):
        g.cyl(kn, (kx, y0 - 0.0015, z0 + 0.040), "y", 0.0105, 0.003, 10)       # skirt
        g.cyl(kn, (kx, y0 - 0.0085, z0 + 0.040), "y", 0.0082, 0.011, 10, r2=0.0074)
        g.box(wm, kx - 0.0007, kx + 0.0007, y0 - 0.0145, y0 - 0.0139, z0 + 0.0405, z0 + 0.0465)
    parts += [kn, wm]
    mt = P("crt_metal", "metal")
    g.cyl(mt, (x1 - 0.085, y0 - 0.003, z0 + 0.040), "y", 0.007, 0.006, 10)        # mains toggle bushing
    g.pipe(mt, [(x1 - 0.085, y0 - 0.006, z0 + 0.040), (x1 - 0.085, y0 - 0.020, z0 + 0.046)], 0.0022, 6)
    for sx_, sz_ in ((x0 + 0.011, z0 + 0.011), (x1 - 0.011, z0 + 0.011), (x0 + 0.011, z1 - 0.011),
                     (x1 - 0.011, z1 - 0.011)):                                  # frame screws
        g.cyl(mt, (sx_, y0 - 0.0008, sz_), "y", 0.0042, 0.002, 6)
    for rx in (L.MX + 0.046, L.MX + 0.104):                                      # nameplate rivets
        g.cyl(mt, (rx, y0 - 0.0018, z1 - 0.031), "y", 0.0018, 0.0012, 6)
    parts.append(mt)
    tg = P("crt_tag", "tag")
    g.box(tg, L.MX + 0.04, L.MX + 0.11, y0 - 0.0015, y0, z1 - 0.040, z1 - 0.022)  # blank nameplate
    parts.append(tg)
    # louvres: on top and on both sides at the back, connectors on the back
    vt = P("crt_vents", "vent")
    for k in range(9):
        yy = y0 + 0.11 + 0.022 * k
        g.box(vt, x0 + 0.05, x1 - 0.05, yy, yy + 0.008, z1 - 0.001, z1 + 0.0012)
    for xs, sg in ((x0, -1), (x1, 1)):
        for k in range(6):
            zz = z0 + 0.06 + 0.035 * k
            g.box(vt, xs - 0.0012, xs + 0.0012, y1 - 0.13, y1 - 0.03, zz, zz + 0.010)
    g.box(vt, L.MX - 0.10, L.MX + 0.08, y1 - 0.001, y1 + 0.0015, z0 + 0.04, z0 + 0.12)
    parts.append(vt)
    return parts


# =============================================================================
# Radio of the R-107 class
# =============================================================================
def build_radio(spec):
    lod, n = spec["lod"], spec["sides"]
    x0, x1, y0, y1, z1 = L.RX0, L.RX1, L.RY0, L.RY1, L.RZ1
    zs = TOP + 0.088                                                             # battery bay seam
    lo = P("radio_bat", "radio_plain")
    g.box(lo, x0, x1, y0, y1, TOP, zs, **rnd(lod, 0.006))
    up = P("radio", "radio")
    g.box(up, x0, x1, y0, y1, zs + 0.002, z1, **rnd(lod, 0.006))
    lp = P("radio_lamp", "lamp_r", group=SEL_LAMP2)                              # transmit lamp - blinks
    lx, ly = L.R_LAMP
    if lod == 2:
        top_quad(lp, lx - 0.005, lx + 0.005, ly - 0.005, ly + 0.005, z1 + 0.001)
    else:
        g.cyl(lp, (lx, ly, z1 + 0.005), "z", 0.0055, 0.010, 10 if lod == 0 else 5)
    parts = [lo, up, lp]
    if lod == 2:
        return parts
    sm = P("radio_seam", "radio_plain")
    g.box(sm, x0 - 0.003, x1 + 0.003, y0 - 0.003, y1 + 0.003, zs - 0.006, zs + 0.006, **rnd(lod, 0.003, 1))
    parts.append(sm)
    # dial indicator: body, scale, rim; the needle is the bone ozl_needle (wobble)
    mb = P("radio_meter", "black")
    g.box(mb, MET_X - 0.037, MET_X + 0.037, MET_Y - 0.017, MET_Y + 0.017, z1 - 0.001, MET_Z, **rnd(lod, 0.002, 1))
    mf = P("radio_meter_face", "meter")
    g.box(mf, MET_X - 0.031, MET_X + 0.031, MET_Y - 0.012, MET_Y + 0.012, MET_Z - 0.001, MET_Z + 0.0004)
    nd = P("radio_needle", "black", group=SEL_NEEDLE)
    px, py = MET_PIV
    g.box(nd, -0.002, NEEDLE_L, -0.0004, 0.0004, 0.0008, 0.0013, frame=turn(px, py, MET_Z, 90.0))
    parts += [mb, mf, nd]
    if lod == 0:
        for q in ((MET_X - 0.037, MET_X + 0.037, MET_Y - 0.017, MET_Y - 0.012),
                  (MET_X - 0.037, MET_X + 0.037, MET_Y + 0.012, MET_Y + 0.017),
                  (MET_X - 0.037, MET_X - 0.031, MET_Y - 0.012, MET_Y + 0.012),
                  (MET_X + 0.031, MET_X + 0.037, MET_Y - 0.012, MET_Y + 0.012)):   # rim above the scale
            g.box(mb, *q, MET_Z, MET_Z + 0.002)
        g.cyl(nd, (px, py, MET_Z + 0.0012), "z", 0.0016, 0.0014, 8)             # axis cap
        tk = P("radio_ticks", "black")
        rz = P("radio_ticks_red", "pencil")
        for i in range(7):                                                       # scale ticks; the last two are red
            a = math.radians(-45 + 15 * i)
            g.box(rz if i >= 5 else tk, -0.0013, 0.0013, -0.00035, 0.00035, 0.0004, 0.0007,
                  frame=turn(px + 0.0165 * math.sin(a), py + 0.0165 * math.cos(a), MET_Z, 90.0 - math.degrees(a)))
        parts += [tk, rz]
    kn = P("radio_knobs", "knob")
    for kx, ky, r in L.R_KNOBS:                                                  # frequency: skirt and knob
        if lod == 0:
            g.cyl(kn, (kx, ky, z1 + 0.003), "z", r + 0.004, 0.006, 16)
            g.cyl(kn, (kx, ky, z1 + 0.0165), "z", r - 0.003, 0.021, 16, r2=r - 0.006)
        else:
            g.cyl(kn, (kx, ky, z1 + 0.015), "z", r - 0.004, 0.028, max(6, n))
    for kx, ky, r in L.R_SMALL if lod == 0 else ():
        g.cyl(kn, (kx, ky, z1 + 0.009), "z", r, 0.018, 10, r2=r - 0.0015)
    parts.append(kn)
    mt = P("radio_metal", "metal")
    ax, ay = L.R_ANT
    g.cyl(mt, (ax, ay, z1 + 0.015), "z", 0.011, 0.030, 12 if lod == 0 else max(6, n))  # antenna socket
    for sx, sy in L.R_SOCK if lod == 0 else ():                                  # headset sockets
        g.cyl(mt, (sx, sy, z1 + 0.006), "z", 0.011, 0.012, 12)
    if lod == 0:
        for sx in (x0, x1):                                                      # bay latches: bracket and lever
            sg = -1 if sx == x0 else 1
            for yy in (y0 + 0.07, y1 - 0.07):
                g.box(mt, *sorted((sx, sx + sg * 0.0035)), yy - 0.017, yy + 0.017, zs - 0.036, zs - 0.008)
                g.box(mt, *sorted((sx + sg * 0.0035, sx + sg * 0.0095)), yy - 0.012, yy + 0.012, zs - 0.024,
                      zs + 0.034, r=0.0015, seg=1)
        for yy in (y0 + 0.05, y1 - 0.05):                                        # strap brackets on the right side
            g.box(mt, x1, x1 + 0.008, yy - 0.02, yy + 0.02, z1 - 0.04, z1 - 0.025)
            g.box(mt, x1, x1 + 0.008, yy - 0.02, yy + 0.02, TOP + 0.03, TOP + 0.045)
        g.cyl(mt, (L.RXC + 0.035, L.R_LAMP[1], z1 + 0.003), "z", 0.006, 0.006, 8)  # power toggle
        g.pipe(mt, [(L.RXC + 0.035, L.R_LAMP[1], z1 + 0.005), (L.RXC + 0.035, L.R_LAMP[1] - 0.006, z1 + 0.020)],
               0.002, 6)
        for rx in (L.RXC - 0.027, L.RXC + 0.027):                                # front nameplate rivets
            g.cyl(mt, (rx, y0 - 0.0016, z1 - 0.06), "y", 0.0022, 0.0012, 6)
    parts.append(mt)
    if lod == 0:
        hw = P("radio_screws", "hw")                                             # top panel screws
        for sx, sy in ((x0 + 0.010, y0 + 0.010), (x1 - 0.010, y0 + 0.010), (x0 + 0.010, y1 - 0.010),
                       (x1 - 0.010, y1 - 0.010)):
            g.cyl(hw, (sx, sy, z1 + 0.0008), "z", 0.0036, 0.0016, 6)
        wm = P("radio_marks", "white")                                           # ticks on the knobs
        for (kx, ky, r), deg in zip(L.R_KNOBS + L.R_SMALL, (120.0, 70.0, 100.0, 40.0, 140.0)):
            ztop = z1 + (0.027 if r > 0.015 else 0.018)
            mark(wm, kx, ky, ztop, deg, 0.002, (r - 0.0065) if r > 0.015 else (r - 0.003))
        tg = P("radio_tag", "tag")                                               # blank front nameplate
        g.box(tg, L.RXC - 0.032, L.RXC + 0.032, y0 - 0.0012, y0 + 0.0003, z1 - 0.075, z1 - 0.045)
        bl = P("radio_sock_in", "black")
        for sx, sy in L.R_SOCK:
            g.cyl(bl, (sx, sy, z1 + 0.0125), "z", 0.0065, 0.001, 8)
        rb = P("radio_feet", "rubber")
        for fx in (x0 + 0.025, x1 - 0.025):
            for fy in (y0 + 0.03, y1 - 0.03):
                g.box(rb, fx - 0.015, fx + 0.015, fy - 0.015, fy + 0.015, TOP - 0.0, TOP + 0.004)
        parts += [hw, wm, tg, bl, rb]
    return parts


# =============================================================================
# Opened TA-57
# =============================================================================
def build_phone(spec):
    """TA-57 field telephone opened: on the left the body with a black panel - a cup, an inductor
    with a crank, terminals, a dummy block; on the right the lid in brown bakelite with the
    handset in it.
    """
    lod, n = spec["lod"], spec["sides"]
    x0, xh, x1, y0, y1 = L.PH_X0, L.PH_XH, L.PH_X1, L.PH_Y0, L.PH_Y1
    zb, zl = TOP + L.PH_HB, TOP + L.PH_HL
    rr = dict(r=0.010, seg=2) if lod == 0 else {}
    bs = P("phone", "bake")
    g.box(bs, x0, xh, y0, y1, TOP, zb - 0.003, **rr)
    lid = P("phone_lid", "bake")
    g.box(lid, xh + 0.002, x1, y0, y1, TOP, zl - 0.003, **rr)
    parts = [bs, lid]
    if lod == 2:
        return parts
    pn = P("phone_panel", "ph_inner")
    g.box(pn, x0 + 0.009, xh - 0.009, y0 + 0.009, y1 - 0.009, zb - 0.010, zb)
    li = P("phone_lid_in", "ph_lid_in")
    g.box(li, xh + 0.011, x1 - 0.009, y0 + 0.009, y1 - 0.009, zl - 0.010, zl - 0.0015)
    parts += [pn, li]
    # handset in the lid: a smooth-shaped grip (thinner in the middle), the earpiece at the back,
    # the microphone at the front
    hx = (xh + x1) / 2 + 0.008
    fr = turn(hx, (y0 + y1) / 2, zl - 0.0015, 98.0)
    hs = P("phone_handset", "black")
    if lod == 0:
        pts = [tuple(fr.p(a, 0.0, 0.013)) for a in (-0.074, -0.040, 0.0, 0.040, 0.074)]
        g.tube_var(hs, pts, [(0.0150, 0.0100), (0.0128, 0.0088), (0.0118, 0.0082), (0.0128, 0.0088),
                             (0.0160, 0.0105)], 12)
        g.cyl(hs, tuple(fr.p(0.080, 0.0, 0.016)), "z", 0.031, 0.030, 16)
        g.cyl(hs, tuple(fr.p(-0.082, 0.0, 0.014)), "z", 0.022, 0.026, 14)
        g.cyl(hs, tuple(fr.p(0.080, 0.0, 0.0315)), "z", 0.024, 0.001, 14)       # earpiece grille
    else:
        g.box(hs, -0.07, 0.07, -0.016, 0.016, 0.0, 0.020, frame=fr)
        g.cyl(hs, tuple(fr.p(0.080, 0.0, 0.016)), "z", 0.031, 0.030, max(8, n + 4))
        g.cyl(hs, tuple(fr.p(-0.082, 0.0, 0.014)), "z", 0.022, 0.026, max(8, n))
    parts.append(hs)
    bk = P("phone_bits", "black")
    g.cyl(bk, (x0 + 0.052, y1 - 0.060, zb + 0.004), "z", 0.036, 0.008, max(8, n + 4) if lod else 20)  # cup
    g.cyl(bk, (xh - 0.045, y0 + 0.090, zb + 0.016), "y", 0.016, 0.090, 12 if lod == 0 else 4)  # inductor
    if lod == 0:
        g.cyl(bk, (xh - 0.045, y0 + 0.040, zb + 0.020), "y", 0.026, 0.012, 12)    # inductor crank disc
        g.box(bk, xh - 0.049, xh - 0.041, y0 + 0.028, y0 + 0.034, zb + 0.016, zb + 0.046)
        g.cyl(bk, (xh - 0.045, y0 + 0.020, zb + 0.042), "y", 0.0055, 0.018, 8)   # crank handle
    g.box(bk, xh - 0.085, xh - 0.015, y1 - 0.125, y1 - 0.060, zb, zb + 0.020, **rnd(lod, 0.002, 1))  # dummy block
    parts.append(bk)
    if lod > 0:
        return parts
    mt = P("phone_metal", "metal")
    for y in (y1 - 0.030, y1 - 0.070):                                         # spare terminals
        g.cyl(mt, (xh - 0.045, y, zb + 0.0015), "z", 0.016, 0.003, 12)
    for y in ((y0 + y1) / 2 - 0.05, (y0 + y1) / 2 + 0.05):                      # hinges
        g.cyl(mt, (xh + 0.001, y, TOP + 0.008), "y", 0.005, 0.032, 8)
    g.box(mt, x0 + 0.010, x0 + 0.040, y0 + 0.020, y0 + 0.050, zb, zb + 0.006)  # line terminal block
    g.box(mt, xh - 0.060, xh - 0.030, y0 + 0.008, y0 + 0.022, zb + 0.006, zb + 0.012)  # inductor lever
    yc = (y0 + y1) / 2                                                         # latches on the free edges
    g.box(mt, x0 - 0.004, x0 + 0.002, yc - 0.012, yc + 0.012, TOP + 0.022, zb - 0.004)
    g.box(mt, x1 - 0.002, x1 + 0.004, yc - 0.010, yc + 0.010, TOP + 0.016, zl - 0.005)
    parts.append(mt)
    wt = P("phone_cones", "white")
    for y in (y1 - 0.030, y1 - 0.070):
        g.cyl(wt, (xh - 0.045, y, zb + 0.013), "z", 0.008, 0.020, 10, r2=0.003)
    parts.append(wt)
    cb = P("phone_cord", "cable")
    a = fr.p(-0.105, 0.0, 0.012)
    g.pipe(cb, spline([tuple(a), (a.x + 0.01, y0 + 0.012, zl + 0.004), (xh - 0.01, y0 + 0.014, zb + 0.002),
                       (x0 + 0.06, y0 + 0.016, zb + 0.004), (x0 + 0.030, y0 + 0.036, zb + 0.008)], 3), 0.003, 6)
    parts.append(cb)
    return parts


# =============================================================================
# Log, pencil, radio handset
# =============================================================================
def build_desk_bits(spec):
    lod, n = spec["lod"], spec["sides"]
    bx, by, bw, bd, deg = L.BOOK
    fr = turn(bx, by, TOP, deg)
    bk = P("book", "book")
    g.box(bk, -bw / 2, bw / 2, -bd / 2, bd / 2, 0.0, 0.0085 if lod == 2 else 0.0015, frame=fr)
    parts = [bk]
    if lod < 2:
        pp = P("book_pages", "paper")
        g.box(pp, -bw / 2 + 0.002, bw / 2 - 0.003, -bd / 2 + 0.002, bd / 2 - 0.002, 0.0015, 0.0070, frame=fr)
        use(bk, "book")
        g.box(bk, -bw / 2, bw / 2, -bd / 2, bd / 2, 0.0070, 0.0085, frame=fr)
        if lod == 0:
            g.cyl(bk, (-bw / 2, 0.0, 0.00425), "y", 0.00425, bd, 10, frame=fr)  # spine
        lb = P("book_label", "paper")
        g.box(lb, -0.035, 0.035, 0.02, 0.05, 0.0085, 0.0092, frame=fr)          # blank label on the cover
        parts += [pp, lb]
    else:
        return parts
    zt = TOP + 0.0085
    hx, hy, hdg = L.HANDSET
    hf = turn(hx, hy, zt, hdg)
    hs = P("handset", "black")
    if lod == 0:
        g.box(hs, -0.070, 0.070, -0.017, 0.017, 0.010, 0.032, frame=hf, r=0.008, seg=2)
        g.cyl(hs, tuple(hf.p(0.080, 0.0, 0.016)), "z", 0.028, 0.032, 16, r2=0.026)
        g.cyl(hs, tuple(hf.p(-0.080, 0.0, 0.016)), "z", 0.024, 0.032, 14, r2=0.022)
        g.box(hs, -0.032, 0.008, 0.017, 0.024, 0.014, 0.028, frame=hf, r=0.002, seg=1)  # push-to-talk key
        g.cyl(hs, tuple(hf.p(0.080, 0.0, 0.0325)), "z", 0.020, 0.001, 10)       # earpiece grille
    else:
        g.box(hs, -0.075, 0.075, -0.018, 0.018, 0.008, 0.034, frame=hf)
        for s in (-1, 1):
            g.cyl(hs, tuple(hf.p(s * 0.080, 0.0, 0.016)), "z", 0.028 if s > 0 else 0.024, 0.032, max(6, n + 2))
    parts.append(hs)
    if lod == 0:
        pc = P("pencil", "pencil")
        pf = turn(0.255, -0.255, zt + 0.004, 74.0)
        g.cyl(pc, (0.0, 0.0, 0.0), "x", 0.0038, 0.15, 6, frame=pf)
        use(pc, "paper")
        g.cyl(pc, (0.085, 0.0, 0.0), "x", 0.0038, 0.02, 6, r2=0.0008, frame=pf)
        parts.append(pc)
    return parts


# =============================================================================
# Tripod antenna
# =============================================================================
ANT_UNIT_Z0 = L.ANT_MAST[1] - 0.004                         # matching unit on the mast: 70 x 50 x 60
ANT_UNIT_Z1 = ANT_UNIT_Z0 + 0.060
ANT_WHIP_Z0 = ANT_UNIT_Z1 + 0.026                           # whip from insulator above unit
ANT_SOCK = (L.ANT_C[0] - 0.035, L.ANT_C[1], ANT_UNIT_Z0 + 0.030)   # coax socket on the unit side


def build_antenna(spec):
    lod, n = spec["lod"], spec["sides"]
    cx, cy = L.ANT_C
    hd = L.ANT_HEAD
    lg = P("ant_tripod", "hw")
    sides = 8 if lod == 0 else (4 if lod == 1 else 3)
    for k in range(3):
        a = math.radians(120 * k)
        d = Vector((math.cos(a), math.sin(a), 0))
        g.pipe(lg, [(cx + 0.016 * d.x, cy + 0.016 * d.y, hd - 0.012),
                    (cx + L.ANT_FOOT * d.x, cy + L.ANT_FOOT * d.y, 0.010)], 0.008, sides)
        if lod == 0:                                                             # leg lug on the hub
            g.box(lg, -0.009, 0.009, -0.006, 0.006, -0.012, 0.010,
                  frame=turn(cx + 0.026 * d.x, cy + 0.026 * d.y, hd - 0.012, 120 * k))
    g.cyl(lg, (cx, cy, hd), "z", 0.024, 0.045, 12 if lod == 0 else max(6, n))
    if lod == 0:
        g.cyl(lg, (cx, cy, hd + 0.034), "z", 0.019, 0.024, 12)                    # mast clamp
        g.cyl(lg, (cx + 0.026, cy, hd + 0.034), "x", 0.006, 0.016, 8)            # clamp screw
        g.cyl(lg, (cx + 0.036, cy, hd + 0.034), "y", 0.0042, 0.032, 6)          # thumbscrew
    parts = [lg]
    ms = P("ant_mast", "t_frame")
    g.pipe(ms, [(cx, cy, L.ANT_MAST[0]), (cx, cy, L.ANT_MAST[1])], 0.014, 12 if lod == 0 else (max(6, n) if lod < 2 else 4))
    if lod == 0:
        g.cyl(ms, (cx, cy, 0.66), "z", 0.0165, 0.022, 12)                        # mast section joint
    parts.append(ms)
    mu = P("ant_unit", "radio_plain")
    g.box(mu, cx - 0.035, cx + 0.035, cy - 0.025, cy + 0.025, ANT_UNIT_Z0, ANT_UNIT_Z1, **rnd(lod, 0.004, 1))
    parts.append(mu)
    bl = P("ant_base", "black")
    g.cyl(bl, (cx, cy, ANT_UNIT_Z1 + 0.014), "z", 0.012, 0.030, 10 if lod == 0 else max(4, n))  # whip insulator
    parts.append(bl)
    if lod == 2:
        return parts
    wp = P("ant_whip", "ant")
    z0 = ANT_WHIP_Z0
    pts = [(cx, cy, z0 + (L.ANT_TOP - 0.006 - z0) * k / 3) for k in range(4)]
    g.tube_var(wp, pts, [(r, r) for r in (0.005, 0.004, 0.0032, 0.0025)], 8 if lod == 0 else 4)
    if lod == 0:
        g.cyl(wp, (cx, cy, L.ANT_TOP - 0.006), "z", 0.0045, 0.012, 8)
        for k, r in ((1, 0.0056), (2, 0.0045)):                                  # whip section couplings
            g.cyl(wp, pts[k], "z", r, 0.016, 8)
        g.cyl(wp, (ANT_SOCK[0] - 0.005, ANT_SOCK[1], ANT_SOCK[2]), "x", 0.0075, 0.010, 10)  # coax socket
        rb = P("ant_feet", "rubber")
        for k in range(3):
            a = math.radians(120 * k)
            g.cyl(rb, (cx + L.ANT_FOOT * math.cos(a), cy + L.ANT_FOOT * math.sin(a), 0.006), "z", 0.012, 0.012, 8)
        parts.append(rb)
    parts.append(wp)
    return parts


# =============================================================================
# Under the table: boxes and the reel
# =============================================================================
def steel_box(name, reg, b, lod, top_handle=False, corners=False):
    x0, x1, y0, y1, h, lt = b["x0"], b["x1"], b["y0"], b["y1"], b["h"], b["lid"]
    bd = P(name, reg)
    g.box(bd, x0, x1, y0, y1, 0.0, h - lt, **rnd(lod, 0.006))
    ld = P(name + "_lid", "box_plain")
    g.box(ld, x0 - 0.004, x1 + 0.004, y0 - 0.004, y1 + 0.004, h - lt, h, **rnd(lod, 0.006))
    parts = [bd, ld]
    if lod == 2:
        return parts
    hw = P(name + "_hw", "hw")
    zl = h - lt
    for hx in ((x0 + 0.08, x1 - 0.08) if x1 - x0 > 0.35 else ((x0 + x1) / 2,)) if lod == 0 else ():  # locks
        g.box(hw, hx - 0.018, hx + 0.018, y0 - 0.006, y0 + 0.0005, zl - 0.058, zl - 0.006)            # base
        g.box(hw, hx - 0.013, hx + 0.013, y0 - 0.012, y0 - 0.005, zl - 0.050, zl + 0.004, r=0.002, seg=1)  # lever
        g.box(hw, hx - 0.011, hx + 0.011, y0 - 0.0085, y0 - 0.0035, zl + 0.004, zl + 0.026)          # bracket
    yc = (y0 + y1) / 2
    for xs, sg in ((x0, -1), (x1, 1)):                                           # handles on the ends, folded
        zh = zl - 0.04
        pts = [(xs + sg * 0.003, yc - 0.06, zh), (xs + sg * 0.016, yc - 0.06, zh - 0.06),
               (xs + sg * 0.016, yc + 0.06, zh - 0.06), (xs + sg * 0.003, yc + 0.06, zh)]
        g.pipe(hw, rounded(pts, 0.010, 2) if lod == 0 else pts, 0.005, 6 if lod == 0 else 3)
        if lod == 0:
            for yy in (yc - 0.06, yc + 0.06):                                    # handle brackets
                g.box(hw, *sorted((xs, xs + sg * 0.007)), yy - 0.011, yy + 0.011, zh - 0.011, zh + 0.011)
    if top_handle:
        xm = (x0 + x1) / 2
        pts = [(xm - 0.06, yc, h), (xm - 0.05, yc, h + 0.022), (xm + 0.05, yc, h + 0.022), (xm + 0.06, yc, h)]
        g.pipe(hw, rounded(pts, 0.008, 2) if lod == 0 else pts, 0.006, 6 if lod == 0 else 3)
        if lod == 0:
            for xx in (xm - 0.06, xm + 0.06):
                g.box(hw, xx - 0.012, xx + 0.012, yc - 0.010, yc + 0.010, h - 0.001, h + 0.004)
    parts.append(hw)
    if lod == 0:
        rb = P(name + "_ribs", "box_plain")                                     # ribs on the face
        for z in (0.035, h - lt - 0.025):
            g.box(rb, x0 + 0.02, x1 - 0.02, y0 - 0.003, y0, z - 0.006, z + 0.006)
        parts.append(rb)
    if lod == 0 and corners:
        cn = P(name + "_corners", "hw")                                         # front bottom angles
        for xa, xb in ((x0 - 0.002, x0 + 0.028), (x1 - 0.028, x1 + 0.002)):
            g.box(cn, xa, xb, y0 - 0.002, y0 + 0.028, 0.0, 0.028, r=0.003, seg=1)
        parts.append(cn)
    return parts


def build_under(spec):
    lod, n = spec["lod"], spec["sides"]
    parts = steel_box("box1", "box1", B1, lod, corners=True) + steel_box("box2", "box2", B2, lod, top_handle=True)
    if lod == 0:
        sl = P("box1_seal", "seal")                                              # seal on the left lock
        g.cyl(sl, (B1["x0"] + 0.08, B1["y0"] - 0.014, B1["h"] - B1["lid"] - 0.068), "y", 0.009, 0.005, 10)
        g.pipe(sl, [(B1["x0"] + 0.08, B1["y0"] - 0.012, B1["h"] - B1["lid"] - 0.060),
                    (B1["x0"] + 0.08, B1["y0"] - 0.012, B1["h"] - B1["lid"] - 0.040)], 0.0012, 4)
        parts.append(sl)
    # reel: cheeks with windows, a hub, cable turns on the drum, an axle, a frame with a handle and
    # a crank
    r = L.REEL
    x, y, z, w = r["x"], r["y"], r["z"], r["w"]
    rl = P("reel", "reel")
    rs = 20 if lod == 0 else (max(8, n + 6) if lod == 1 else 6)
    for s in (-1, 1):
        g.cyl(rl, (x + s * (w / 2 - r["flange"] / 2), y, z), "x", r["r"], r["flange"], rs)
    cl = P("reel_coil", "coil")
    g.cyl(cl, (x, y, z), "x", r["coil"], w - 2 * r["flange"], rs)
    if lod == 0:
        for dx in (-0.040, 0.040):                                                # top turns
            g.cyl(cl, (x + dx, y, z), "x", r["coil"] + 0.0028, 0.024, rs, cap=False)
    parts += [rl, cl]
    fr = P("reel_frame", "hw")
    sides = 8 if lod == 0 else 3
    xs = (x - w / 2 - 0.018, x + w / 2 + 0.018)
    for xx in xs:
        g.pipe(fr, [(xx, y - 0.13, 0.009), (xx, y, z), (xx, y + 0.13, 0.009)], 0.008, sides)
    hp = [(xs[0], y, z), (xs[0], y, r["handle"]), (xs[1], y, r["handle"]), (xs[1], y, z)]
    g.pipe(fr, rounded(hp, 0.03, 3) if lod == 0 else hp, 0.009 if lod == 0 else 0.008, sides)  # posts and handle
    g.pipe(fr, [(xs[0] - 0.012, y, z), (xs[1] + 0.012, y, z)], 0.009, sides)
    if lod == 0:
        g.cyl(fr, (x, y, z), "x", 0.030, w + 0.012, 12)                          # hub
        for xx in xs:
            g.cyl(fr, (xx, y, z), "x", 0.016, 0.022, 10)                         # bearing units
    parts.append(fr)
    if lod == 0:
        hl = P("reel_holes", "black")                                            # cheek windows
        for s in (-1, 1):
            for k in range(4):
                a = math.radians(45 + 90 * k)
                g.cyl(hl, (x + s * (w / 2 + 0.0004), y + 0.082 * math.cos(a), z + 0.082 * math.sin(a)), "x",
                      0.024, 0.0012, 6)
        ck = P("reel_crank", "black")
        g.box(ck, xs[1] + 0.010, xs[1] + 0.018, y - 0.01, y + 0.01, z - 0.10, z + 0.01, r=0.002, seg=1)
        g.cyl(ck, (xs[1] + 0.035, y, z - 0.095), "x", 0.011, 0.040, 10)
        parts += [hl, ck]
    return parts


# =============================================================================
# Wires
# =============================================================================
def build_wires(spec):
    lod = spec["lod"]
    if lod == 2:
        return []
    parts = []
    yb = L.MY1
    # laptop (port at the rear right) -> the gap between it and the CRT -> over the rear table
    # edge in a loop down (the CRT back is flush with the edge) -> up to the plug on the back
    vga_l = (L.LX1 - 0.022, L.LY1 + 0.014, TOP + 0.018)
    vga_c = (-0.05, yb + 0.018, TOP + 0.080)
    pts = [vga_l, (L.LX1 + 0.002, L.LY1 + 0.030, TOP + 0.006), (L.LX1 + 0.010, 0.05, TOP + 0.0045),
           (L.LX1 + 0.010, 0.22, TOP + 0.0045), (L.LX1 + 0.011, 0.292, TOP + 0.004), (-0.172, yb + 0.012, TOP - 0.012),
           (-0.140, yb + 0.026, TOP - 0.045), (-0.090, yb + 0.034, TOP - 0.030), (-0.056, yb + 0.030, TOP + 0.040),
           (-0.050, yb + 0.026, TOP + 0.072), vga_c]
    parts += cable("cable_vga", "cable", pts, 0.0042, lod)
    # CRT power: from the plug on the back, over the rear table edge to the floor
    pw_c = (0.08, yb + 0.022, TOP + 0.080)
    pts = [pw_c, (0.083, yb + 0.034, TOP + 0.055), (0.088, yb + 0.030, TOP + 0.010), (0.092, yb + 0.024, TOP - 0.040),
           (0.10, yb + 0.026, 0.40), (0.12, yb + 0.040, 0.06), (0.16, yb + 0.050, 0.007), (0.32, yb + 0.060, 0.006)]
    parts += cable("cable_crt_power", "cable", pts, 0.0038, lod)
    # laptop power: from the plug on the left side, straight over the left table edge down and along
    # the floor back
    lp = (L.LX0 - 0.016, L.LY1 - 0.030, TOP + 0.018)
    pts = [lp, (L.LX0 - 0.012, L.LY1 - 0.029, TOP + 0.010), (L.TX0 - 0.004, L.LY1 - 0.026, TOP + 0.002),
           (L.TX0 - 0.010, L.LY1 - 0.022, TOP - 0.040), (L.TX0 - 0.014, 0.0, 0.45), (L.TX0 - 0.006, 0.15, 0.05),
           (L.TX0 + 0.010, 0.28, 0.007), (-0.42, 0.36, 0.006), (-0.30, 0.42, 0.006)]
    parts += cable("cable_laptop", "cable", pts, 0.0032, lod)
    # radio handset -> the plug in the socket on the panel
    hx, hy, hdg = L.HANDSET
    a = math.radians(hdg)
    he = (hx + 0.098 * math.cos(a), hy + 0.098 * math.sin(a), TOP + 0.02)
    sx, sy = L.R_SOCK[0]
    pts = [he, (he[0] + 0.012, he[1] + 0.02, TOP + 0.010), (sx, L.RY0 - 0.014, TOP + 0.006),
           (sx, L.RY0 - 0.008, TOP + 0.04), (sx, L.RY0 - 0.007, L.RZ1 - 0.04), (sx, L.RY0 - 0.004, L.RZ1 + 0.012),
           (sx, sy - 0.016, L.RZ1 + 0.050), (sx, sy, L.RZ1 + 0.048)]
    parts += cable("cable_handset", "cable", pts, 0.003, lod)
    # coaxial cable: the plug on the antenna socket -> a sag -> the socket of the matching unit on
    # the mast
    ax, ay = L.R_ANT
    ux, uy, uz = ANT_SOCK
    pts = [(ax, ay, L.RZ1 + 0.052), (ax + 0.006, ay + 0.004, L.RZ1 + 0.072), (ax + 0.040, ay - 0.020, L.RZ1 + 0.058),
           (0.540, 0.190, L.RZ1 - 0.010), (0.562, 0.130, uz + 0.030), (ux - 0.040, uy + 0.004, uz + 0.002),
           (ux - 0.028, uy, uz)]
    parts += cable("cable_coax", "cable", pts, 0.0045, lod)
    # TA-57 field cable -> reel: two cores from the terminal block through the left wall of the
    # body, along the table in the gap between the laptop and the telephone, over the front table
    # edge down and under the table
    r = L.REEL
    end = (r["x"] - 0.03, r["y"] - 0.07, r["z"] + 0.095)
    xg = L.PH_X0 - 0.008
    for k, dx in enumerate((-0.0035, 0.0035)):
        pts = [(L.PH_X0 + 0.025, L.PH_Y0 + 0.035 + dx, TOP + L.PH_HB + 0.006),
               (L.PH_X0 + 0.004, L.PH_Y0 + 0.030 + dx, TOP + L.PH_HB + 0.001),
               (xg - dx, L.PH_Y0 + 0.020, TOP + 0.012), (xg - dx, L.TY0 + 0.005, TOP + 0.0025),
               (xg - dx, L.TY0 - 0.004, TOP - 0.004), (xg + 0.002 - dx, L.TY0 - 0.010, TOP - 0.05),
               (-0.172 - dx, L.TY0 - 0.013, 0.60), (-0.135 - dx, L.TY0 - 0.012, 0.49), (-0.040 - dx, L.TY0 - 0.006, 0.40),
               (0.140 - dx, -0.25, 0.30), (end[0] - dx, end[1], end[2])]
        parts += cable("cable_field%d" % k, "cable_f", pts, 0.0022, lod, 5)
    if lod > 0:
        return parts
    # plugs at the cable ends
    pl = P("plugs", "black")
    g.box(pl, L.LX0 - 0.016, L.LX0 + 0.0005, L.LY1 - 0.037, L.LY1 - 0.023, TOP + 0.011, TOP + 0.025, r=0.003, seg=1)
    g.box(pl, vga_l[0] - 0.015, vga_l[0] + 0.015, L.LY1 - 0.0005, L.LY1 + 0.012, TOP + 0.011, TOP + 0.025,
          r=0.002, seg=1)
    g.box(pl, vga_c[0] - 0.020, vga_c[0] + 0.020, yb - 0.0005, yb + 0.016, TOP + 0.068, TOP + 0.092, r=0.002, seg=1)
    g.box(pl, pw_c[0] - 0.015, pw_c[0] + 0.015, yb - 0.0005, yb + 0.020, TOP + 0.066, TOP + 0.094, r=0.003, seg=1)
    g.cyl(pl, (sx, sy, L.RZ1 + 0.024), "z", 0.0095, 0.024, 10)                  # handset plug
    g.cyl(pl, (sx, sy, L.RZ1 + 0.042), "z", 0.0065, 0.012, 8, r2=0.0035)
    sx2, sy2 = L.R_SOCK[1]
    g.cyl(pl, (sx2, sy2, L.RZ1 + 0.015), "z", 0.0105, 0.006, 10)                # cap of the second socket
    g.cyl(pl, (ux - 0.019, uy, uz), "x", 0.0085, 0.018, 10)                     # coax plug at the unit
    parts.append(pl)
    mt = P("plugs_metal", "metal")
    for dx in (-0.024, 0.024):                                                   # connector screws on the CRT back
        g.cyl(mt, (vga_c[0] + dx, yb + 0.006, TOP + 0.080), "y", 0.0035, 0.012, 6)
    g.cyl(mt, (ax, ay, L.RZ1 + 0.041), "z", 0.0092, 0.022, 10)                   # coax plug on the radio
    g.cyl(mt, (ax, ay, L.RZ1 + 0.034), "z", 0.0115, 0.007, 12)                   # coupling nut
    parts.append(mt)
    return parts


def build_lod(spec):
    parts = build_table(spec) + build_laptop(spec) + build_crt(spec) + build_radio(spec) + build_phone(spec)
    parts += build_desk_bits(spec) + build_antenna(spec) + build_under(spec) + build_wires(spec)
    parts = [p for p in parts if p.bm.faces]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """The table with everything under it, up to the tabletop, and a box above the table - CRT,
    radio, laptop. The antenna and the wires have no collision (a component thinner than 0.5 m
    does not work in the engine).
    """
    steel = kx.PEN + r"\metalplate.rvmat"
    tbl = kx.box_pts(L.TX0 - 0.01, L.TX1 + 0.01, L.TY0 - 0.03, L.TY1 + 0.01, 0.0, TOP)
    up = kx.box_pts(L.LX0, L.RX1, L.MY0 - 0.04, L.MY1, TOP, L.MZ1)
    comps = [(tbl, steel), (up, steel)]
    memory = {
        "invView": [(0.0, -2.3, 1.4)],
        "ce_center": [(0.0, 0.0, 0.7)],
        "ce_radius": [(0.9, 0.0, 0.7)],
        "ozl_needle_axis": NEEDLE_AXIS,                      # up, toward the person (see NEEDLE_ANIM)
    }
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2] + 0.004)
    return comps, 90.0, memory, bbox


# The first four are the --look preview (overall view, screens, radio, under the table); the first
# two also for the working look
SHOTS = [
    ("front", (-0.9, -2.6, 1.7), (0.05, 0.0, 0.75), 30),
    ("screens", (-0.20, -1.05, 1.25), (-0.12, 0.0, 0.92), 34),
    ("radio", (0.80, -0.85, 1.35), (0.33, 0.05, 0.90), 34),
    ("under", (0.40, -1.6, 0.55), (0.0, 0.0, 0.22), 30),
    ("laptop", (-0.45, -0.75, 1.15), (-0.34, -0.12, 0.82), 36),
    ("phone", (0.10, -0.80, 1.20), (0.05, -0.18, 0.76), 36),
    ("right", (2.0, -0.7, 1.3), (0.1, 0.0, 0.75), 30),
    ("top", (0.1, -0.9, 2.5), (0.0, 0.0, 0.75), 30),
    ("back", (1.2, 2.3, 1.6), (0.0, 0.1, 0.6), 30),
]

def _posed(place):
    """Preview: the indicator needle is where the engine will put it (engine_rot): in the working
    look (move is the look dictionary ON_MOVE) - at the middle of the sway, in the other shots
    - at rest (phase 0, the left tick). It is drawn in the middle of the scale, so without this
    wrapper the preview would show something other than what is in the game. It does not go
    into the p3d - there model.cfg animates.
    """
    def wrapped(parts, *a, **kw):
        obs = place(parts, *a, **kw)
        rot = engine_rot(NEEDLE_MID if kw.get("move") is ON_MOVE else 0.0)
        for p, ob in zip(parts, obs):
            if p.group == SEL_NEEDLE:
                loc = Matrix.Translation(Vector(ob.location))
                ob.matrix_world = loc @ rot
        return obs
    return wrapped


krender.place_look = _posed(krender.place_look)
krender.place = _posed(krender.place)

M.look_shots = (4, 3)                    # working look has the 3rd view (radio needle)
M.run(build_lod, collision, SHOTS, row_step=1.7, row_shot=((1.7, -6.4, 2.0), (1.7, 0, 0.8)))
