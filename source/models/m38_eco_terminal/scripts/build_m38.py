"""M38 - the computer terminal of the Scientists (OZL_Eco_Terminal, "EOM terminal"): a
scientist hands in media here as for machine input and opens the research tree. A
terminal: an explicit screen, no modules.

    blender --background --python build_m38.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run: make_decals.py with the system Python (the screen "off" and the
"working" frames, the keyboard, the numbered disc, the counter, the tag, paper, log pages).
Positions are in layout.py (shared with make_decals.py).

Card: the computer terminal of an institute computing center - a computer cabinet with a
tape drive behind glass and lamps, next to it a desk with a CRT terminal, a keyboard and a
printer with fan-fold paper. 2.0 x 1.8 x 0.8 m.

Look: "dayz" (matte, light wear - dust, stains, scuffs at the keyboard), corners and edges
are rounded (cabinet, console, tabletop, terminal body, keyboard, printer), the reels are
flanges with three windows (the winding is visible) with a hub with three latches; the
keyboard is separate keys; the printer is a mechanism under a transparent cover (platen,
guides, a carriage with a head, a ribbon cartridge, a pressure bar), pulling tractors on
the rear block; the cables are smooth curves behind the desk into the raised floor. Small
items are vanilla proxy things (kvanilla): a pen on the open log, three punched cards, a
sheet of paper on the desk, a GP-5 gas mask on a hook on the left side of the cabinet. The
log is our own: open, the pages curved toward the spine, ruling without text.

Reference and dimensions:
- the cabinet - the ES-5017 magnetic tape drive (Carl Zeiss Jena, ES EVM; the Technische
  Sammlungen Dresden): a white front frame, a window with two reels on an aluminium panel,
  a Y-shaped vacuum column cover between them (concave sides, a narrow neck), a head block
  at the bottom of the window, a white band with nameplates, a grey-green (blue-green in the
  photo) lower panel, on top on legs a dark console with a numbered disc in a chrome rim and
  square lamp buttons in chrome frames. No ES-5017 passport was found; the class is the
  same as the IBM 3420 (the ES-5017 is its analog): 66 1/2 x 29 3/4 x 29 5/8" =
  1690 x 756 x 752 mm (Computer History Museum). The width is taken as 0.76, the height with
  the console 1.80 (card), the depth 0.62 - per the card (0.6), not 0.75 as at IBM: the
  cabinet stands flush with the back of a desk 0.8 deep;
- the 1/2" tape reel - 10.5" (267 mm) per the ECMA/GOST standard for 12.7 mm tape; the file
  reel on the left is full, the machine one on the right has less winding; the flange
  windows run from 64 to 118 mm in radius (estimated from photos of 10.5" reels);
- the ES-1055 operator console: a cream desk on blue-green legs, a thick rounded tabletop
  edge, a CRT in a body, a black keyboard with a beige service block. The terminal is of
  the Robotron K 8924 class: H x W x D 33 x 51 x 42 cm, 25.6 kg (Heinz Nixdorf
  MuseumsForum) - taken as 0.34 x 0.48 x 0.42; the visible 12" glass 264 x 199 (an
  estimate); the keyboard ~480 x 200 x 52 - an estimate (K 7637 class), 19 mm key pitch;
- the printer - an 80-column dot-matrix, Epson FX class: 414 x 350 x 167.5 mm, 7.2 kg
  (FX-890; the FX-80 of the 1980s is the same size class); fan-fold paper 9.5" (241 mm with
  the perforation), sheet 11" (279 mm), 6 lines per inch, 10 characters per inch - the head
  travel of 80 characters = 8" = 203 mm; platen dia 42 (an estimate);
- the desk: tabletop 1.22 x 0.80 at 0.735 (GOST 13025.3 - 0.72-0.76), a pedestal under the
  printer with a shelf for the paper stack, the web goes through a slot in the tabletop to
  the tractor at the printer back;
- the log - an office ledger 150 x 205 mm (an estimate, A5 format); the GP-5 gas mask is
  vanilla.

The Scientists: clean, laboratory - the enamel is intact, the glass is clear, the plastic is
not yellowed; the "dayz" look gives light dust, hand stains and scuffs, the keys at the
keyboard are worn. White and grey-green enamel, chrome, glass. Marks: a digit on the tape
drive disc, the digits of the hour counter, blank nameplates, a paper tag without text;
strokes instead of text on the paper, the screen and in the log.

Machine look and "working" - a loop: the terminal screen has its own texture (the screen
section): "off" - dark glass, "working" - the _screen_fNN frames (OZL_WorkFx frames: the
receiving table rows are marked one by one, the tape scale grows, the bars shift, the
cursor blinks); the lamps use the _on atlas: ozl_lamp_work steady (some console buttons,
the terminal lamp, the printer power lamp), ozl_lamp_blink blinking (two console buttons,
the printer "ready" lamp; the red ones are not lit); the reels are the bones ozl_reel_l and
ozl_reel_r on the source ozl_work: a model.cfg loop (sourceAddress loop), per pass the file
reel makes 3 turns, the machine one (less winding, the same tape speed) 4, a pass takes 3 s
(animPeriod in the mod config): 1 and 1.33 rev/s, both the same direction; the printer
carriage with the head is the bone ozl_head on the source ozl_head (OZL_WorkFx wobble: it
moves along the line back and forth). LODs: the middle one has no small items and no
printer mechanism, the far one has boxes, reels as discs, no glass and no paper web.

Blender axes: X - width, Y - depth (front at -Y), Z - up.
"""
import math
import os
import sys

import bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kexport as kx  # noqa: E402
import kgeo as g  # noqa: E402
import kmats  # noqa: E402
import kmodel  # noqa: E402
import kvanilla as kv  # noqa: E402
import layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
DZ = L.DZ

LOD_SPECS = [
    dict(lod=0, sides=30),
    dict(lod=1, sides=12),
    dict(lod=2, sides=6),
]

REGIONS = {
    "white": ("white", 1.0), "green": ("green", 0.7), "green_dark": ("green_dark", 0.8),
    "console": ("console", 1.2), "deck": ("deck", 1.0), "chrome": ("chrome", 1.0), "flange": ("flange", 1.0),
    "tape": ("tape", 1.0), "hub": ("hub", 1.6), "hub_metal": ("hub_metal", 1.6),
    "disc": ("disc", 3.0), "counter": ("counter", 4.0), "tag": ("tag", 3.0), "yellow": ("yellow", 2.0),
    "btn_y": ("btn_y", 1.2), "btn_w": ("btn_w", 1.2), "btn_r": ("btn_r", 1.2),
    "lamp_y": ("lamp_y", 1.2), "lamp_w": ("lamp_w", 1.2), "lamp_g": ("lamp_g", 1.2),
    "led_g": ("led_g", 1.5), "led_a": ("led_a", 1.5), "led_off": ("led_off", 1.5),
    "white_top": ("white_top", 0.9), "bezel": ("bezel", 1.4), "case": ("case", 1.2), "case_dark": ("case_dark", 1.0),
    "keyboard": ("keyboard", 3.0), "key_black": ("key_black", 1.5), "key_beige": ("key_beige", 1.5),
    "paper": ("paper", 2.0), "paper_plain": ("paper_plain", 0.6), "pages": ("pages", 2.5),
    "label": ("label", 1.5), "plate_dark": ("plate_dark", 1.0), "black": ("black", 0.8), "rubber": ("rubber", 0.5),
    "logbook": ("logbook", 1.2), "platen": ("platen", 1.4), "ribbon": ("ribbon", 1.2), "head": ("head", 2.0),
    "cable": ("cable", 0.8), "cable_beige": ("cable_beige", 0.8), "grille": ("grille_v", 0.8),
    "glass": ("deck", 1.0), "screen": ("black", 1.0),
}

# =============================================================================
# Materials
# =============================================================================


def wdecal(name):
    return os.path.join(WORK, name)


def decal_y(name, x0, x1, z0, z1, y0, y1):
    """A decal on a face looking toward -y, the face depth between y0 and y1."""
    return (wdecal(name), "y", -1, ("x", "z"), ((x0 + x1) / 2, (z0 + z1) / 2), (x1 - x0, z1 - z0), (y0, y1))


def decal_z(name, x0, x1, y0, y1, z0, z1):
    return (wdecal(name), "z", 1, ("x", "y"), ((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0, y1 - y0), (z0, z1))


CY_F = L.CON_Y                                                 # console face
DISC_D = decal_y("decal_disc.png", L.DISC[0] - L.DISC[2], L.DISC[0] + L.DISC[2], L.DISC[1] - L.DISC[2],
                 L.DISC[1] + L.DISC[2], CY_F - 0.010, CY_F - 0.004)
COUNTER_D = decal_y("decal_counter.png", *L.COUNTER, CY_F - 0.004, CY_F - 0.001)
TAG_D = decal_y("decal_tag.png", *L.TAG, CY_F - 0.003, CY_F - 0.0005)
KEYS_D = decal_z("decal_keys.png", *L.KEYS, L.KZ_F - 0.003, L.KZ_B + 0.006)
STACK_D = decal_z("decal_stack_top.png", *L.STACK[:4], L.STACK[5] - 0.002, L.STACK[5] + 0.002)
PRINT_D = decal_y("decal_print.png", *L.PRINT, 0.05, 0.10)
LOG_D = decal_z("decal_log.png", L.LOG[0] - L.LOG_PAGE[0], L.LOG[0] + L.LOG_PAGE[0], L.LOG[1] - L.LOG_PAGE[1] / 2,
                L.LOG[1] + L.LOG_PAGE[1] / 2, DZ, DZ + 0.02)

# Scientists: intact enamel, no chips or rust; a little dust on top and grime in the corners - not
# factory-new
CLEAN = dict(chip=(0.97, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.10, grime=0.10)
LIT = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
WHITE = kmats.lin((230, 230, 222))
GREEN = kmats.lin((118, 144, 132))                             # grey-green enamel


def flat(rgb, gloss=0.7, spec=0.6):
    return ("flat", dict(color=kmats.lin(rgb), gloss=gloss, spec=spec))


KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "white": ("paint", dict(CLEAN, color=WHITE, under=kmats.lin((170, 170, 164)), seed=2.1, gloss=0.45, spec=0.3)),
    # tabletop - plastic; worn by the keyboard (scuff)
    "white_top": ("plastic", dict(color=kmats.lin((226, 222, 206)), seed=2.7, gloss=0.35, spec=0.25, mottle=0.05,
                                  dust=0.12, grime=0.10, scuff=(0.74, 0.84))),
    "green": ("paint", dict(CLEAN, color=GREEN, under=kmats.lin((90, 96, 92)), seed=3.4, gloss=0.42, spec=0.3)),
    "green_dark": ("paint", dict(CLEAN, color=kmats.lin((76, 98, 90)), under=kmats.lin((60, 62, 60)), seed=3.9,
                                 gloss=0.4, spec=0.3)),
    "console": ("paint", dict(CLEAN, color=kmats.lin((66, 68, 70)), under=kmats.lin((40, 40, 42)), seed=4.6,
                              gloss=0.35, spec=0.3)),
    "deck": ("steel", dict(seed=5.3, tone=0.62, along="x", gloss=0.45, spec=0.55, dust=0.08, grime=0.08)),
    "chrome": ("steel", dict(seed=6.2, tone=0.72, along="z", gloss=0.8, spec=0.9, dust=0.06, grime=0.06)),
    # hub - white plastic, the middle is aluminium
    "hub": ("plastic", dict(color=kmats.lin((214, 212, 204)), seed=6.8, gloss=0.45, spec=0.35, mottle=0.03,
                            dust=0.06, grime=0.04, scuff=(0.92, 1.0))),
    "hub_metal": ("steel", dict(seed=6.9, tone=0.55, along="x", gloss=0.6, spec=0.7, dust=0.03, grime=0.03)),
    "flange": ("plastic", dict(color=kmats.lin((44, 46, 50)), seed=7.1, gloss=0.7, spec=0.55, mottle=0.03, dust=0.05,
                               grime=0.0, scuff=(0.95, 1.0))),
    "tape": ("plastic", dict(color=kmats.lin((70, 44, 28)), seed=7.5, gloss=0.5, spec=0.35, mottle=0.08, dust=0.0,
                             grime=0.0, scuff=(0.95, 1.0))),
    "disc": ("paint", dict(LIT, color=kmats.lin((236, 234, 226)), gloss=0.5, spec=0.35, decal_items=[DISC_D])),
    "counter": ("paint", dict(LIT, color=kmats.lin((20, 20, 20)), gloss=0.6, spec=0.4, decal_items=[COUNTER_D])),
    "tag": ("paint", dict(LIT, color=kmats.lin((236, 222, 170)), gloss=0.15, spec=0.1, decal_items=[TAG_D])),
    "yellow": ("plastic", dict(color=kmats.lin((206, 172, 52)), seed=4.9, gloss=0.4, spec=0.3, dust=0.05, grime=0.0)),
    # buttons without lamps and lamps (while working the lamps are lit - remap to *_on)
    "btn_y": flat((150, 128, 50)), "btn_w": flat((176, 170, 156)), "btn_r": flat((110, 30, 26)),
    "lamp_y": flat((150, 128, 50)), "lamp_w": flat((176, 170, 156)), "lamp_g": flat((34, 80, 44)),
    "lamp_y_on": flat((255, 220, 70)), "lamp_w_on": flat((255, 250, 228)), "lamp_g_on": flat((90, 255, 110)),
    "led_g": flat((34, 64, 40), 0.85, 0.8), "led_g_on": flat((130, 255, 140), 0.85, 0.8),
    "led_a": flat((80, 56, 22), 0.85, 0.8), "led_a_on": flat((255, 176, 40), 0.85, 0.8),
    "led_off": flat((80, 56, 22), 0.85, 0.8),
    "bezel": ("plastic", dict(color=kmats.lin((30, 30, 32)), seed=8.1, gloss=0.4, spec=0.3, mottle=0.05, dust=0.05,
                              grime=0.0, scuff=(0.95, 1.0))),
    "case": ("plastic", dict(color=kmats.lin((216, 214, 202)), seed=8.6, gloss=0.35, spec=0.25, mottle=0.04, dust=0.08,
                             grime=0.05, scuff=(0.88, 0.95))),
    "case_dark": ("plastic", dict(color=kmats.lin((138, 142, 140)), seed=8.9, gloss=0.4, spec=0.3, mottle=0.04,
                                  dust=0.06, grime=0.02, scuff=(0.92, 1.0))),
    "keyboard": ("paint", dict(LIT, color=kmats.lin((44, 44, 46)), gloss=0.3, spec=0.2, decal_items=[KEYS_D])),
    # keys: the middle is rubbed to a shine by fingers (scuff)
    "key_black": ("plastic", dict(color=kmats.lin((34, 34, 36)), seed=9.1, gloss=0.4, spec=0.3, mottle=0.05,
                                  dust=0.04, grime=0.06, scuff=(0.66, 0.78))),
    "key_beige": ("plastic", dict(color=kmats.lin((206, 198, 178)), seed=9.3, gloss=0.35, spec=0.25, mottle=0.05,
                                  dust=0.04, grime=0.08, scuff=(0.72, 0.84))),
    "paper": ("paint", dict(LIT, color=kmats.lin((240, 238, 228)), gloss=0.1, spec=0.05,
                            decal_items=[STACK_D, PRINT_D])),
    "paper_plain": ("paint", dict(LIT, color=kmats.lin((236, 234, 224)), gloss=0.1, spec=0.05)),
    "pages": ("paint", dict(LIT, color=kmats.lin((238, 234, 220)), gloss=0.1, spec=0.05, decal_items=[LOG_D])),
    "label": ("steel", dict(seed=9.2, tone=0.70, along="x", gloss=0.55, spec=0.6, dust=0.02, grime=0.0)),
    "plate_dark": ("paint", dict(LIT, color=kmats.lin((44, 70, 66)), gloss=0.5, spec=0.4)),
    "logbook": ("plastic", dict(color=kmats.lin((52, 66, 92)), seed=9.6, gloss=0.3, spec=0.2, mottle=0.06, dust=0.05,
                                grime=0.04, scuff=(0.84, 0.92))),
    "platen": ("plastic", dict(color=kmats.lin((24, 24, 24)), seed=9.7, gloss=0.25, spec=0.15, dust=0.02, grime=0.0,
                               scuff=(0.95, 1.0))),
    "ribbon": ("plastic", dict(color=kmats.lin((18, 18, 20)), seed=9.8, gloss=0.35, spec=0.25, dust=0.02)),
    "head": ("steel", dict(seed=9.9, tone=0.22, along="y", gloss=0.5, spec=0.55, dust=0.02, grime=0.1)),
    "cable": ("plastic", dict(color=kmats.lin((58, 60, 62)), seed=10.1, gloss=0.3, spec=0.2, dust=0.15, grime=0.1)),
    "cable_beige": ("plastic", dict(color=kmats.lin((184, 180, 166)), seed=10.3, gloss=0.3, spec=0.2, dust=0.12,
                                    grime=0.1)),
})

OBJ, NAME = "m38_eco_terminal", "ozr_eco_terminal"
SEL_SCREEN, SEL_LAMP, SEL_BLINK = "ozl_screen", "ozl_lamp_work", "ozl_lamp_blink"
SEL_RL, SEL_RR, SEL_HEAD = "ozl_reel_l", "ozl_reel_r", "ozl_head"
REEL_TURNS = (3, 4)                                            # turns per loop pass: file, machine
# preview of the working look: the lamps are lit, the printer carriage is mid-line (does not go into
# the p3d)
ON = dict(remap={"lamp_y": "lamp_y_on", "lamp_w": "lamp_w_on", "lamp_g": "lamp_g_on", "led_g": "led_g_on",
                 "led_a": "led_a_on"}, emissive=(1.0, 1.0, 1.0, 1.0),
          move={SEL_HEAD: (L.HEAD_TRAVEL * 0.5, 0.0, 0.0)})


def reel_anim(side, sel, turns):
    return ("ozl_reel_%s_spin" % side, dict(type="rotation", source="ozl_work", sourceAddress="loop", selection=sel,
                                            axis="ozl_reel_%s_axis" % side, memory=1, minValue=0.0,
                                            maxValue=1.0 / turns, angle0=0.0, angle1=2 * math.pi))


# carriage axis - one meter along x: offset in meters
HEAD_ANIM = ("ozl_head_move", dict(type="translation", source="ozl_head", selection=SEL_HEAD, axis="ozl_head_axis",
                                   memory=1, minValue=0.0, maxValue=1.0, offset0=0.0, offset1=L.HEAD_TRAVEL))
SCREEN = dict(off="decal_screen_off.png", frames=["decal_screen_f%02d.png" % i for i in range(12)], size=256,
              gloss=0.8)


# --- Log: a page curved toward the spine (t - from the spine 0 to the edge 1) -----------------
COVER_T = 0.003


def page_f(t):
    """Fraction of the page block thickness: at the spine the pages go into the fold, at the edge
    it is thin.
    """
    f = 1.0 - t * t
    return f * (0.55 + 0.45 * min(1.0, t / 0.15))


def page_z(t):
    return DZ + COVER_T + L.LOG_H[0] + (L.LOG_H[1] - L.LOG_H[0]) * page_f(t)


PEN_T = 0.62
DECOR = [
    # pen on the right page of the log, along the page
    kv.put("pen", (L.LOG[0] + PEN_T * L.LOG_PAGE[0], L.LOG[1] - 0.012, page_z(PEN_T)), **kv.flat(96)),
    # punched cards fanned out left of the keyboard (media are handed in for input)
    kv.put("punchedcard", (-0.135, -0.300, DZ), **kv.flat(8)),
    kv.put("punchedcard", (-0.122, -0.278, DZ), lift=0.0012, **kv.flat(24)),
    kv.put("punchedcard", (-0.108, -0.258, DZ), lift=0.0024, **kv.flat(41)),
    # printout by the wall on the left
    kv.put("paper", (-0.110, 0.170, DZ), **kv.flat(91)),
    # gas mask on a hook on the left side of the cabinet, facing outward
    kv.put("gp5", (L.X0 - 0.0005, L.GP5[0], L.GP5[1]), up=(0, 0, 1), fwd=(-1, 0, 0), normal=(-1, 0, 0)),
]

M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.84, 0.88, 0.88), clear=0.04, edge=0.08, smudge=0.02, streaks=0.01),
                 selections=(SEL_SCREEN, SEL_LAMP, SEL_BLINK, SEL_RL, SEL_RR, SEL_HEAD),
                 hidden=(SEL_SCREEN, SEL_LAMP, SEL_BLINK), states={"on": ON},
                 bones=((SEL_RL, ""), (SEL_RR, ""), (SEL_HEAD, "")),
                 animations=(reel_anim("l", SEL_RL, REEL_TURNS[0]), reel_anim("r", SEL_RR, REEL_TURNS[1]), HEAD_ANIM),
                 decor=DECOR, panels={"screen": SCREEN},
                 sources={"ozl_work": dict(animPeriod=3.0), "ozl_head": dict(animPeriod=0.2)})
P = M.part
BOUNDS = {}


def use(part, region):
    return part.use(region, *REGIONS[region])


def bev(lod, r=0.004, seg=1):
    return dict(r=r, seg=seg) if lod == 0 else {}


def boxp(name, region, x0, x1, y0, y1, z0, z1, group="body", **kw):
    """A separate part from one box: each has its own unwrap, the projections are not shared."""
    p = P(name, region, group=group)
    g.box(p, x0, x1, y0, y1, z0, z1, **kw)
    return p


# =============================================================================
# Primitives that kgeo lacks
# =============================================================================
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


def face(part, verts, want):
    """Face from bmesh vertices, flipped to look toward want."""
    f = part.bm.faces.new(verts)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def closed(part, faces):
    """Normals of a closed solid point outward."""
    bmesh.ops.recalc_face_normals(part.bm, faces=faces)
    return part.tag(faces)


def lathe(part, prof, sides, center, axis=(0, 0, 1), cap0=False, cap1=False, a0=0.0):
    """Solid of revolution: prof [(r, h)] along the axis from center; the profile goes around the
    section counterclockwise (r to the right, h up) - (dh, -dr) points outward; cap0 / cap1 -
    close the first / last ring.
    """
    bm = part.bm
    w = Vector(axis).normalized()
    ref = Vector((0, 0, 1)) if abs(w.z) < 0.9 else Vector((1, 0, 0))
    u = w.cross(ref).normalized()
    v = w.cross(u).normalized()
    c0 = Vector(center)

    def rad(a):
        return u * math.cos(a) + v * math.sin(a)
    rings = [[bm.verts.new(c0 + w * h + rad(a0 + 2 * math.pi * k / sides) * r) for k in range(sides)] for r, h in prof]
    new = []
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        for k in range(sides):
            j = (k + 1) % sides
            want = rad(a0 + 2 * math.pi * (k + 0.5) / sides) * (h1 - h0) - w * (r1 - r0)
            new.append(face(part, [rings[i][k], rings[i][j], rings[i + 1][j], rings[i + 1][k]], want))
    if cap0:
        new.append(face(part, rings[0], -w))
    if cap1:
        new.append(face(part, rings[-1], w))
    return part.tag(new)


def rrect(cx, cy, w, h, r, k):
    """Rounded rectangle, counterclockwise: 4 corners of k + 1 points each."""
    r = max(1e-4, min(r, w / 2 - 1e-4, h / 2 - 1e-4))
    pts = []
    for sx, sy, a in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        ccx, ccy = cx + sx * (w / 2 - r), cy + sy * (h / 2 - r)
        for i in range(k + 1):
            t = math.radians(a + 90.0 * i / max(k, 1))
            pts.append((ccx + r * math.cos(t), ccy + r * math.sin(t)))
    return pts


def fillet_poly(poly, radii, k=3):
    """Polygon [(a, b)] with rounded corners (the radius of corner i is radii[i], 0 - sharp)."""
    out = []
    n = len(poly)
    for i in range(n):
        r = radii[i]
        p = Vector(poly[i])
        if r <= 0:
            out.append((p.x, p.y))
            continue
        a, b = Vector(poly[i - 1]), Vector(poly[(i + 1) % n])
        d1, d2 = (a - p).normalized(), (b - p).normalized()
        ang = math.acos(max(-1.0, min(1.0, d1.dot(d2))))
        t = min(r / math.tan(ang / 2), (a - p).length * 0.45, (b - p).length * 0.45)
        rr = t * math.tan(ang / 2)
        p1, p2 = p + d1 * t, p + d2 * t
        c = p + (d1 + d2).normalized() * (rr / math.sin(ang / 2))
        a1, a2 = math.atan2(p1.y - c.y, p1.x - c.x), math.atan2(p2.y - c.y, p2.x - c.x)
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for s in range(k + 1):
            q = a1 + da * s / k
            out.append((c.x + rr * math.cos(q), c.y + rr * math.sin(q)))
    return out


def inset2(prof, d):
    """Convex polygon moved inward by d (along the corner bisectors)."""
    n = len(prof)
    area = sum(prof[i][0] * prof[(i + 1) % n][1] - prof[(i + 1) % n][0] * prof[i][1] for i in range(n))
    s = 1.0 if area > 0 else -1.0
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(prof[i - 1]), Vector(prof[i]), Vector(prof[(i + 1) % n])
        e1, e2 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n1, n2 = Vector((-e1.y, e1.x)) * s, Vector((-e2.y, e2.x)) * s
        b = n1 + n2
        b = n1 if b.length < 1e-9 else b.normalized()
        q = p1 + b * (d / max(0.3, b.dot(n1)))
        out.append((q.x, q.y))
    return out


def profile_x(part, prof, x0, x1, ch=0.0):
    """Profile [(y, z)] (convex) along x from x0 to x1; the ends are chamfered ch."""
    bm = part.bm
    if ch > 0:
        ins = inset2(prof, ch)
        rings = [[(x0, y, z) for y, z in ins], [(x0 + ch, y, z) for y, z in prof],
                 [(x1 - ch, y, z) for y, z in prof], [(x1, y, z) for y, z in ins]]
    else:
        rings = [[(x0, y, z) for y, z in prof], [(x1, y, z) for y, z in prof]]
    vs = [[bm.verts.new(Vector(p)) for p in ring] for ring in rings]
    n = len(prof)
    new = []
    for i in range(len(vs) - 1):
        for k in range(n):
            j = (k + 1) % n
            new.append(bm.faces.new([vs[i][k], vs[i][j], vs[i + 1][j], vs[i + 1][k]]))
    new += [bm.faces.new(vs[0]), bm.faces.new(vs[-1][::-1])]
    return closed(part, new)


def frame_ring(part, cx, cz, wo, ho, wi, hi, y_front, y_back):
    """Flat frame facing -y (a chrome button frame): the face and the outer walls (y_back None -
    only the face: a flush overlay).
    """
    bm = part.bm
    oc = [(cx - wo / 2, cz - ho / 2), (cx + wo / 2, cz - ho / 2), (cx + wo / 2, cz + ho / 2), (cx - wo / 2, cz + ho / 2)]
    ic = [(cx - wi / 2, cz - hi / 2), (cx + wi / 2, cz - hi / 2), (cx + wi / 2, cz + hi / 2), (cx - wi / 2, cz + hi / 2)]
    of = [bm.verts.new((x, y_front, z)) for x, z in oc]
    inn = [bm.verts.new((x, y_front, z)) for x, z in ic]
    ob = [bm.verts.new((x, y_back, z)) for x, z in oc] if y_back is not None else None
    new = []
    for i in range(4):
        j = (i + 1) % 4
        new.append(face(part, [of[i], of[j], inn[j], inn[i]], (0, -1, 0)))
        if ob:
            mid = Vector(((oc[i][0] + oc[j][0]) / 2 - cx, 0, (oc[i][1] + oc[j][1]) / 2 - cz))
            new.append(face(part, [of[i], of[j], ob[j], ob[i]], mid))
    return part.tag(new)


def polar_plate(part, cx, cz, y0, y1, radii, n_ang, windows, a0=0.0, front_only=False):
    """Reel flange around the y axis between y0 (the face, toward -y) and y1: rings radii (from the
    hub to the rim) by n_ang sectors; the cells in the windows [(middle, half-width - rad, r0,
    r1)] are dropped. Walls - along the rim and the window edges (no wall at the hub - the
    shaft is there). front_only - the face and the rim: the back of the front flange and the
    1.6 mm window walls are not visible (the winding is behind them).
    """
    bm = part.bm
    nr = len(radii)

    def pt(i, j, y):
        a = a0 + 2 * math.pi * j / n_ang
        return Vector((cx + radii[i] * math.cos(a), y, cz + radii[i] * math.sin(a)))
    F = [[bm.verts.new(pt(i, j, y0)) for j in range(n_ang)] for i in range(nr)]
    B = [[bm.verts.new(pt(i, j, y1)) for j in range(n_ang)] for i in range(nr)]

    def solid(i, j):
        if i < 0 or i >= nr - 1:
            return False
        rm = (radii[i] + radii[i + 1]) / 2
        am = a0 + 2 * math.pi * (j % n_ang + 0.5) / n_ang
        for ac, hw, r0, r1 in windows:
            d = (am - ac + math.pi) % (2 * math.pi) - math.pi
            if abs(d) < hw and r0 < rm < r1:
                return False
        return True
    new = []
    for i in range(nr - 1):
        for j in range(n_ang):
            if not solid(i, j):
                continue
            j2 = (j + 1) % n_ang
            am = a0 + 2 * math.pi * (j + 0.5) / n_ang
            rad = Vector((math.cos(am), 0, math.sin(am)))
            tan = Vector((-math.sin(am), 0, math.cos(am)))
            new.append(face(part, [F[i][j], F[i][j2], F[i + 1][j2], F[i + 1][j]], (0, -1, 0)))
            if i == nr - 2:
                new.append(face(part, [F[i + 1][j], F[i + 1][j2], B[i + 1][j2], B[i + 1][j]], rad))
            if front_only:
                continue
            new.append(face(part, [B[i][j], B[i + 1][j], B[i + 1][j2], B[i][j2]], (0, 1, 0)))
            if i > 0 and not solid(i - 1, j):
                new.append(face(part, [F[i][j], F[i][j2], B[i][j2], B[i][j]], -rad))
            if i < nr - 2 and not solid(i + 1, j):
                new.append(face(part, [F[i + 1][j], F[i + 1][j2], B[i + 1][j2], B[i + 1][j]], rad))
            if not solid(i, j - 1):
                new.append(face(part, [F[i][j], F[i + 1][j], B[i + 1][j], B[i][j]], -tan))
            if not solid(i, j + 1):
                new.append(face(part, [F[i][j2], F[i + 1][j2], B[i + 1][j2], B[i][j2]], tan))
    loose = [v for row in F + B for v in row if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context="VERTS")
    return part.tag(new)


def hull(part, pts):
    bm = part.bm
    before = set(bm.faces)
    vs = [bm.verts.new(Vector(p)) for p in pts]
    bmesh.ops.convex_hull(bm, input=vs)
    faces = [f for f in bm.faces if f not in before]
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return part.tag(faces)


def bulge_rr(part, cx, y_edge, cz, w, h, r, k, sag, n_rings):
    """Convex CRT glass with rounded corners: contour rings from the center to the edge, facing
    -y, the edges at y_edge, the middle is `sag` closer.
    """
    bm = part.bm
    ring0 = rrect(0.0, 0.0, w, h, r, k)
    rings = [[bm.verts.new((cx + a * s, y_edge - sag * (1 - s * s), cz + b * s)) for a, b in ring0]
             for s in [(i + 1) / n_rings for i in range(n_rings)]]
    c = bm.verts.new((cx, y_edge - sag, cz))
    n = len(ring0)
    new = [face(part, [c, rings[0][q], rings[0][(q + 1) % n]], (0, -1, 0)) for q in range(n)]
    for i in range(n_rings - 1):
        for q in range(n):
            j = (q + 1) % n
            new.append(face(part, [rings[i][q], rings[i + 1][q], rings[i + 1][j], rings[i][j]], (0, -1, 0)))
    return part.tag(new)


def knurl_x(part, cx, cy, cz, x0, x1, r, n, depth):
    """Knurled knob along x: 2n vertices around, every other one sunk by depth."""
    poly = [(cy + (r - depth * (k % 2)) * math.cos(math.pi * k / n), cz + (r - depth * (k % 2)) * math.sin(math.pi * k / n))
            for k in range(2 * n)]
    return g.prism(part, poly, (1, 2), cx + x0, cx + x1)


def keycap(part, x0, x1, y0, y1, h, ins):
    """Key on the sloped keyboard top: the bottom is a rectangle on the plate, the top is inset by
    ins and raised by h along the normal to the slope; no bottom.
    """
    bm = part.bm
    a = math.atan2(L.KZ_B - L.KZ_F, L.KY1 - L.KY0)
    nrm = Vector((0.0, -math.sin(a), math.cos(a)))

    def at(x, y):
        return Vector((x, y, L.key_zs(y) + 0.0022))
    b = [at(x0, y0), at(x1, y0), at(x1, y1), at(x0, y1)]
    t = [at(x0 + ins, y0 + ins) + nrm * h, at(x1 - ins, y0 + ins) + nrm * h, at(x1 - ins, y1 - ins) + nrm * h,
         at(x0 + ins, y1 - ins) + nrm * h]
    vb, vt = [bm.verts.new(p) for p in b], [bm.verts.new(p) for p in t]
    c = sum(b, Vector()) / 4
    new = [face(part, vt, nrm)]
    for i in (0, 1, 3):                                        # back is covered by next row
        j = (i + 1) % 4
        m = (b[i] + b[j]) / 2 - c
        new.append(face(part, [vb[i], vb[j], vt[j], vt[i]], (m.x, m.y, 0.0)))
    return part.tag(new)


def button(part, cx, cz, w, h, y_face, depth, ch):
    """Button facing -y: walls from the device face, a chamfer ch on the front edge, the face; no
    back face.
    """
    bm = part.bm

    def ring(dx, dz, y):
        return [bm.verts.new((cx + sx * dx, y, cz + sz * dz)) for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    r0 = ring(w / 2, h / 2, y_face)
    r1 = ring(w / 2, h / 2, y_face - depth + ch)
    r2 = ring(w / 2 - ch, h / 2 - ch, y_face - depth)
    new = []
    for a, b, fwd in ((r0, r1, 0.0), (r1, r2, 1.0)):
        for i in range(4):
            j = (i + 1) % 4
            m = Vector(((a[i].co.x + a[j].co.x) / 2 - cx, 0.0, (a[i].co.z + a[j].co.z) / 2 - cz)).normalized()
            new.append(face(part, [a[i], a[j], b[j], b[i]], m + Vector((0.0, -fwd, 0.0))))
    new.append(face(part, r2, (0, -1, 0)))
    return part.tag(new)


def cable(name, region, pts, r, lod, k=2, sides=5):
    """A cable as a smooth curve (not g.tube: that one twists the rings)."""
    p = P(name, region)
    g.pipe(p, spline(pts, k) if lod == 0 else pts, r, sides if lod == 0 else 4)
    return p


def paper_web(name, region, path, lod, k=2):
    """Fan-fold paper web: a 241 mm strip along x following the path in the y-z plane."""
    p = P(name, region)
    pts = [(L.PXC, y, z) for y, z in path]
    g.sweep(p, spline(pts, k) if lod == 0 and k > 1 else pts, (1, 0, 0), 0.0004, L.PAPER_W / 2)
    return p


# =============================================================================
# Tape drive cabinet
# =============================================================================
def build_cabinet(spec):
    lod = spec["lod"]
    x0, x1, y0, y1 = L.X0, L.X1, L.CY0, L.CY1
    wx0, wx1, wz0, wz1 = L.WIN
    yf = y0 + L.FRONT_T
    parts = []
    if lod == 2:
        # far LOD: the body, the white face, the window panel and the lower panel as overlays on the
        # face
        parts.append(boxp("cab_body", "green", x0, x1, yf, y1, 0.0, L.CH))
        parts.append(boxp("cab_rail", "white", x0, x1, y0 + 0.004, yf, 0.0, L.CH))
        parts.append(boxp("cab_deck", "deck", wx0, wx1, y0, y0 + 0.004, wz0, wz1))
        parts.append(boxp("cab_lower", "green", wx0, wx1, y0, y0 + 0.004, L.LOWER[0], L.LOWER[1]))
        return parts
    # body of sheets: the bottom, the niche back, the niche sides (outside - the cabinet sides), the
    # roof
    parts.append(boxp("cab_body", "green", x0, x1, yf, y1, L.PLINTH, wz0, **bev(lod, 0.006, 1)))
    parts.append(boxp("cab_back", "green", wx0, wx1, L.YD, y1, wz0, wz1))
    for s, (a, b) in (("l", (x0, wx0)), ("r", (wx1, x1))):
        parts.append(boxp("cab_side_%s" % s, "green", a, b, yf, y1, wz0, wz1, **bev(lod, 0.004, 1)))
    parts.append(boxp("cab_roof", "green", x0, x1, yf, y1, wz1, L.CH, **bev(lod, 0.006, 1)))
    parts.append(boxp("cab_deck", "deck", wx0, wx1, L.YD - 0.004, L.YD, wz0, wz1))
    # white front frame: full-height posts, a top bar, a band under the window, the niche sill
    for s, (a, b) in (("l", (x0, wx0)), ("r", (wx1, x1))):
        parts.append(boxp("cab_stile_%s" % s, "white", a, b, y0, yf, L.PLINTH, L.CH, **bev(lod, 0.006, 1)))
    parts.append(boxp("cab_rail", "white", wx0, wx1, y0, yf, wz1, L.CH, **bev(lod, 0.005, 1)))
    parts.append(boxp("cab_band", "white", wx0, wx1, L.YP, yf, L.BAND[0], wz0, **bev(lod, 0.004, 1)))
    parts.append(boxp("cab_sill", "white", wx0, wx1, yf - 0.004, L.YD, wz0 - 0.006, wz0))
    # lower door and a recessed plinth
    parts.append(boxp("cab_lower", "green", wx0 + 0.002, wx1 - 0.002, L.YP, yf, L.LOWER[0] + 0.002, L.LOWER[1] - 0.002,
                      **bev(lod, 0.005, 2)))
    parts.append(boxp("cab_plinth", "green_dark", x0 + 0.012, x1 - 0.012, y0 + 0.04, y1 - 0.012, 0.0, L.PLINTH))
    # window glass in an aluminium frame with rounded corners
    t = 0.010
    if lod == 0:
        fr = P("cab_glass_frame", "chrome")
        bm = fr.bm
        cxw, czw, ww, hw = (wx0 + wx1) / 2, (wz0 + wz1) / 2, wx1 - wx0, wz1 - wz0
        out = rrect(cxw, czw, ww, hw, L.WIN_R, 2)
        inn = rrect(cxw, czw, ww - 2 * t, hw - 2 * t, L.WIN_R - t * 0.6, 2)
        rings = [[bm.verts.new((x, yy, z)) for x, z in ring] for ring, yy in
                 ((out, y0 + 0.004), (out, y0 + 0.016), (inn, y0 + 0.016), (inn, y0 + 0.004))]
        n = len(out)
        new = []
        for i in range(4):
            for q in range(n):
                j = (q + 1) % n
                a, b = rings[i], rings[(i + 1) % 4]
                new.append(bm.faces.new([a[q], a[j], b[j], b[q]]))
        closed(fr, new)
        parts.append(fr)
        gl = P("cab_glass", "glass", section="glass")
        g.prism(gl, rrect(cxw, czw, ww - 2 * t + 0.004, hw - 2 * t + 0.004, L.WIN_R - t * 0.5, 2), (0, 2),
                L.YG - 0.002, L.YG + 0.002)
        parts.append(gl)
    else:
        fr = P("cab_glass_frame", "chrome")
        for a, b, c, d in ((wx0, wx1, wz0, wz0 + t), (wx0, wx1, wz1 - t, wz1), (wx0, wx0 + t, wz0, wz1),
                           (wx1 - t, wx1, wz0, wz1)):
            g.box(fr, a, b, y0 + 0.004, y0 + 0.016, c, d)
        parts.append(fr)
        gl = P("cab_glass", "glass", section="glass")
        g.box(gl, wx0 + t, wx1 - t, L.YG - 0.002, L.YG + 0.002, wz0 + t, wz1 - t)
        parts.append(gl)
    # nameplates on the white band - blank
    parts.append(boxp("cab_plate", "label", *L.PLATE[:2], L.YP - 0.003, L.YP, *L.PLATE[2:], **bev(lod, 0.0015, 1)))
    parts.append(boxp("cab_plate2", "plate_dark", *L.PLATE2[:2], L.YP - 0.003, L.YP, *L.PLATE2[2:],
                      **bev(lod, 0.0015, 1)))
    if lod == 0:
        hw_ = P("cab_hw", "chrome")
        # nameplate rivets, panel screws in the niche, the lower door lock
        for (a, b, c, d) in (L.PLATE, L.PLATE2):
            for xx in (a + 0.006, b - 0.006):
                lathe(hw_, [(0.0022, 0.0), (0.0012, 0.0012)], 6, (xx, L.YP - 0.003, (c + d) / 2), (0, -1, 0), cap1=True)
        for xx in (wx0 + 0.022, wx1 - 0.022):
            for zz in (wz0 + 0.022, wz1 - 0.022):
                lathe(hw_, [(0.0055, 0.0), (0.0035, 0.0028)], 8, (xx, L.YD - 0.004, zz), (0, -1, 0),
                      cap1=True)
        lx, lz = L.LOCK
        lathe(hw_, [(0.013, 0.0), (0.013, 0.002), (0.0110, 0.0045), (0.009, 0.0072)], 12, (lx, L.YP, lz), (0, -1, 0),
              cap1=True)
        parts.append(hw_)
        kh = P("cab_keyhole", "black")
        g.box(kh, lx - 0.0012, lx + 0.0012, L.YP - 0.0075, L.YP - 0.0070, lz - 0.0045, lz + 0.0045)
        parts.append(kh)
        # ventilation slots at the bottom of the door
        vt = P("cab_vents", "black")
        for k in range(9):
            x = wx0 + 0.07 + k * (wx1 - wx0 - 0.14) / 8
            g.box(vt, x - 0.023, x + 0.023, L.YP - 0.0006, L.YP + 0.001, 0.124, 0.136)
        parts.append(vt)
        # back: a vent grille and a cable into the raised floor
        parts.append(boxp("cab_grille", "grille", x0 + 0.10, x1 - 0.10, y1, y1 + 0.002, 0.95, 1.50))
        parts.append(cable("cab_cable", "cable", [(L.CXC + 0.10, y1, 0.22), (L.CXC + 0.12, y1 + 0.04, 0.18),
                                                  (L.CXC + 0.15, y1 + 0.07, 0.08), (L.CXC + 0.17, y1 + 0.08, 0.01),
                                                  (L.CXC + 0.18, y1 + 0.08, -0.03)], 0.011, lod))
        # gas mask hook on the left side
        hk = P("cab_hook", "chrome")
        gy = L.GP5[0]
        g.box(hk, x0 - 0.003, x0, gy - 0.012, gy + 0.012, L.HOOK_Z - 0.022, L.HOOK_Z + 0.006)
        g.pipe(hk, spline([(x0 - 0.001, gy, L.HOOK_Z - 0.008), (x0 - 0.016, gy, L.HOOK_Z - 0.012),
                           (x0 - 0.030, gy, L.HOOK_Z - 0.004), (x0 - 0.033, gy, L.HOOK_Z + 0.012)], 2), 0.0028, 5)
        parts.append(hk)
    return parts


def build_tape_deck(spec):
    """Reels (bones), the vacuum column cover, the head block with rollers and the tape between
    them (in the niche behind the glass).
    """
    lod, n = spec["lod"], spec["sides"]
    parts = []
    yf, yb = L.REEL_Y
    ym = (yf + yb) / 2
    nb = 24 if lod == 0 else n                                 # rear flange and winding
    for side, (rx, rz, pack), sel in (("l", L.REELS[0], SEL_RL), ("r", L.REELS[1], SEL_RR)):
        if lod == 2:
            pk = P("reel_%s_pack" % side, "flange", group=sel)
            g.cyl(pk, (rx, ym, rz), "y", L.REEL_R, yb - yf, n)
            parts.append(pk)
            continue
        bk = P("reel_%s_back" % side, "flange", group=sel)
        g.cyl(bk, (rx, yb + 0.0008, rz), "y", L.REEL_R, 0.0016, nb)
        parts.append(bk)
        pk = P("reel_%s_pack" % side, "tape", group=sel)
        g.cyl(pk, (rx, ym, rz), "y", pack, yb - yf - 0.003, nb)
        parts.append(pk)
        hb = P("reel_%s_hub" % side, "hub", group=sel)
        if lod == 1:
            g.cyl(hb, (rx, yf - 0.004, rz), "y", L.HUB_R, yb - yf + 0.008, 8)
            parts.append(hb)
            continue
        # front flange: three windows (the winding is visible), spokes and a rim; the windows of the
        # reels are rotated differently. A window is 3 of 5 sectors of a third of the circle (12
        # degrees each), the window middle is the sector middle
        a0 = math.radians(0.0 if side == "l" else 37.0)
        cell = 2 * math.pi / n
        wc = max(1, int(round(n / 3 * 0.6)) | 1)
        wins = [(a0 + (k * n // 3 + (wc - 1) / 2 + 0.5) * cell, wc / 2 * cell, L.WINDOW_R[0] - 0.001,
                 L.WINDOW_R[1] + 0.001) for k in range(3)]
        fr = P("reel_%s_front" % side, "flange", group=sel)
        polar_plate(fr, rx, rz, yf - 0.0008, yf + 0.0008, [L.HUB_R, L.WINDOW_R[0], L.WINDOW_R[1], L.REEL_R], n, wins,
                    a0, front_only=True)
        parts.append(fr)
        # drive hub: a white ring with a step, an aluminium middle, three latches (the hub is not
        # visible inside the winding - it starts at the front flange)
        d = yb - yf
        lathe(hb, [(L.HUB_R, d - 0.002), (L.HUB_R, d + 0.006), (0.046, d + 0.010), (0.031, d + 0.011),
                   (0.0285, d + 0.014)], 16, (rx, yb, rz), (0, -1, 0))
        use(hb, "hub_metal")
        lathe(hb, [(0.0285, d + 0.014), (0.012, d + 0.016)], 16, (rx, yb, rz), (0, -1, 0), cap1=True)
        parts.append(hb)
        kn = P("reel_%s_latch" % side, "chrome", group=sel)
        for k in range(3):
            a = math.radians(30 + 120 * k) + a0
            lathe(kn, [(0.0055, 0.0), (0.0055, 0.004), (0.0025, 0.0072)], 6,
                  (rx + 0.0385 * math.cos(a), yb - d - 0.0098, rz + 0.0385 * math.sin(a)), (0, -1, 0), cap1=True)
        parts.append(kn)
    if lod == 2:
        return parts
    # Y-shaped vacuum column cover: concave sides, a narrow neck, slightly wider at the bottom
    zt, zn, zb = L.WIN[3] - 0.012, 1.375, 1.17
    wt, wn, wb = 0.050, 0.022, 0.027
    right = [(L.CXC + wn + (wt - wn) * (1 - i / 6.0) ** 2, zt + (zn - zt) * i / 6.0) for i in range(7)] + \
            [(L.CXC + wn + (wb - wn) * (i / 3.0) ** 2, zn + (zb - zn) * i / 3.0) for i in range(1, 4)]
    if lod == 1:
        right = right[::3]
    left = [(2 * L.CXC - x, z) for x, z in right]
    cv = P("deck_column", "green_dark")
    g.prism(cv, right[::-1] + left, (0, 2), L.YD - 0.006, L.YD - 0.0005)
    parts.append(cv)
    # head block: a rounded box, an aluminium cover, rollers at the corners
    hx0, hx1, hz0, hz1 = L.HEAD
    parts.append(boxp("deck_head", "green_dark", hx0, hx1, L.YD - 0.075, L.YD - 0.0005, hz0, hz1, **bev(lod, 0.006, 2)))
    if lod == 0:
        parts.append(boxp("deck_head_lid", "deck", hx0 + 0.006, hx1 - 0.006, L.YD - 0.070, L.YD - 0.002, hz1,
                          hz1 + 0.006, r=0.002, seg=1))
        rl = P("deck_rollers", "chrome")
        for rxx, rzz in L.ROLLS:
            g.cyl(rl, (rxx, L.YD - 0.026, rzz), "y", L.ROLL_R, 0.050, 10)
            g.cyl(rl, (rxx, L.YD - 0.052, rzz), "y", L.ROLL_R + 0.004, 0.003, 10)
        parts.append(rl)
    # tape: from the winding tangentially to the rollers and across the head block cover
    zr = hz1 + (0.0075 if lod == 0 else 0.002)
    pts = []
    for k, ((rx, rz, pack), (rxx, rzz)) in enumerate(zip(L.REELS, L.ROLLS)):
        s = 1 if k == 0 else -1
        px_, pz_ = rxx + s * L.ROLL_R * 0.7, rzz + L.ROLL_R * 0.7
        dx, dz = px_ - rx, pz_ - rz
        dd = math.hypot(dx, dz)
        th = math.atan2(dz, dx) + s * math.acos(min(1.0, pack / dd))
        tp = (rx + pack * math.cos(th), ym, rz + pack * math.sin(th))
        side_pts = [tp, (px_, ym, pz_), (rxx + s * 0.03, ym, zr)]
        pts.append(side_pts if k == 0 else side_pts[::-1])
    tp = P("deck_tape", "tape")
    g.sweep(tp, pts[0] + pts[1], (0, 1, 0), 0.0005, 0.0064)
    parts.append(tp)
    return parts


def build_console(spec):
    """Console on the cabinet roof: a rounded box on two legs, a numbered disc in a chrome rim,
    lamp buttons in chrome frames, a counter, a tag, a yellow plate.
    """
    lod = spec["lod"]
    x0, x1, y0, y1, z0, z1 = L.CON
    parts = [boxp("con_box", "console", x0, x1, y0, y1, z0, z1, **bev(lod, 0.012, 2))]
    if lod == 0:
        lg = P("con_legs", "black")
        for x in (x0 + 0.15, x1 - 0.15):
            g.cyl(lg, (x, (y0 + y1) / 2, L.CH + 0.0125), "z", 0.025, 0.025, 8)
        parts.append(lg)
    if lod < 2:
        ds = P("con_disc", "disc")
        g.cyl(ds, (L.DISC[0], y0 - 0.004, L.DISC[1]), "y", L.DISC[2], 0.006, 24 if lod == 0 else 12)
        parts.append(ds)
        parts.append(boxp("con_counter", "counter", L.COUNTER[0], L.COUNTER[1], y0 - 0.002, y0 + 0.001, L.COUNTER[2],
                          L.COUNTER[3]))
        parts.append(boxp("con_tag", "tag", L.TAG[0], L.TAG[1], y0 - 0.0012, y0 + 0.001, L.TAG[2], L.TAG[3]))
    if lod == 0:
        rm = P("con_chrome", "chrome")
        # disc rim, button and counter frames (the frames are 1 mm overlays: no walls visible)
        lathe(rm, [(L.DISC[2] + 0.0085, 0.0), (L.DISC[2] + 0.0070, 0.0065), (L.DISC[2] + 0.0030, 0.0085),
                   (L.DISC[2] + 0.0005, -0.001)], 20, (L.DISC[0], y0, L.DISC[1]), (0, -1, 0))
        for bx, bz, c, role in L.BTN_TOP + L.BTN_LOW:
            frame_ring(rm, bx, bz, L.BTN + 0.007, L.BTN + 0.007, L.BTN + 0.001, L.BTN + 0.001, y0 - 0.001, None)
        cx_, cz_ = (L.COUNTER[0] + L.COUNTER[1]) / 2, (L.COUNTER[2] + L.COUNTER[3]) / 2
        frame_ring(rm, cx_, cz_, L.COUNTER[1] - L.COUNTER[0] + 0.006, L.COUNTER[3] - L.COUNTER[2] + 0.006,
                   L.COUNTER[1] - L.COUNTER[0], L.COUNTER[3] - L.COUNTER[2], y0 - 0.0028, y0 + 0.001)
        parts.append(rm)
        parts.append(boxp("con_yellow", "yellow", L.YELLOW[0], L.YELLOW[1], y0 - 0.0012, y0 + 0.001, L.YELLOW[2],
                          L.YELLOW[3]))
    # buttons: without lamps - the body, lamps - ozl_lamp_work, blinking - ozl_lamp_blink
    h = L.BTN / 2
    groups = {"btn": P("con_buttons", "btn_w"), "lamp": P("con_lamps", "lamp_y", group=SEL_LAMP),
              "blink": P("con_lamps_blink", "lamp_y", group=SEL_BLINK)}
    for bx, bz, c, role in L.BTN_TOP + L.BTN_LOW:
        p = groups[role]
        use(p, ("btn_" if role == "btn" else "lamp_") + c)
        if lod > 0:
            g.quad(p, [(bx - h, y0 - 0.001, bz - h), (bx + h, y0 - 0.001, bz - h), (bx + h, y0 - 0.001, bz + h),
                       (bx - h, y0 - 0.001, bz + h)])
        else:
            button(p, bx, bz, L.BTN - 0.001, L.BTN - 0.001, y0 + 0.001, 0.0075, 0.002)
    parts += [p for p in groups.values() if len(p.bm.faces)]
    return parts


# =============================================================================
# Desk with a pedestal
# =============================================================================
def build_desk(spec):
    lod = spec["lod"]
    x0, x1, y0, y1 = L.DX0, L.DX1, L.DY0, L.DY1
    s0, s1 = L.SLOT
    sx0, sx1 = L.PXC - L.PAPER_W / 2 - 0.012, L.PXC + L.PAPER_W / 2 + 0.012
    parts = []
    if lod == 0:
        # the whole tabletop with rounded edges (the thick edge of the ES-1055), the slot by boolean
        base = P("desk_top_base", "white_top")
        g.box(base, x0, x1, y0, y1, L.DZ0, DZ, r=L.TOP_R, seg=2)
        cut = P("desk_slot_cut", "white_top")
        g.box(cut, sx0, sx1, s0, s1, L.DZ0 - 0.01, DZ + 0.01)
        parts.append(M.boolean("desk_top", base, [cut]))
    elif lod == 1:
        parts.append(boxp("desk_top", "white_top", x0, x1, y0, s0, L.DZ0, DZ))
        parts.append(boxp("desk_top_back", "white_top", x0, x1, s1, y1, L.DZ0, DZ))
        parts.append(boxp("desk_top_mid_l", "white_top", x0, sx0, s0, s1, L.DZ0, DZ))
        parts.append(boxp("desk_top_mid_r", "white_top", sx1, x1, s0, s1, L.DZ0, DZ))
    else:
        parts.append(boxp("desk_top", "white_top", x0, x1, y0, y1, L.DZ0, DZ))
    a, b = L.PED
    if lod == 2:
        parts.append(boxp("desk_leg", "green", x0 + 0.01, x0 + 0.04, y0 + 0.04, y1 - 0.04, 0.0, L.DZ0))
        parts.append(boxp("ped_side_l", "green", a, b, y0 + 0.02, y1 - 0.02, 0.0, L.DZ0))
        parts.append(boxp("desk_modesty", "green", x0 + 0.04, a, y1 - 0.07, y1 - 0.05, 0.30, L.DZ0))
        return parts
    # left panel leg on a support with adjustable feet
    parts.append(boxp("desk_leg", "green", x0 + 0.012, x0 + 0.040, y0 + 0.05, y1 - 0.05, 0.040, L.DZ0,
                      **bev(lod, 0.004, 1)))
    parts.append(boxp("desk_foot", "green_dark", x0 + 0.002, x0 + 0.050, y0 + 0.02, y1 - 0.02, 0.012, 0.042,
                      **bev(lod, 0.008, 1)))
    # pedestal under the printer: sides, back, shelf, plinth, a drawer on top
    parts.append(boxp("ped_side_l", "green", a, a + 0.022, y0 + 0.02, y1 - 0.02, 0.0, L.DZ0, **bev(lod, 0.003, 1)))
    parts.append(boxp("ped_side_r", "green", b - 0.022, b, y0 + 0.02, y1 - 0.02, 0.0, L.DZ0, **bev(lod, 0.003, 1)))
    parts.append(boxp("ped_back", "green", a + 0.022, b - 0.022, y1 - 0.045, y1 - 0.02, 0.0, L.DZ0))
    parts.append(boxp("ped_shelf", "white", a + 0.022, b - 0.022, y0 + 0.03, y1 - 0.045, L.PED_SHELF - 0.02,
                      L.PED_SHELF, **bev(lod, 0.003, 1)))
    parts.append(boxp("ped_kick", "green_dark", a + 0.022, b - 0.022, y0 + 0.05, y0 + 0.07, 0.0,
                      L.PED_SHELF - 0.02))
    parts.append(boxp("ped_drawer", "green", a + 0.025, b - 0.025, y0 + 0.012, y0 + 0.03, DRAWER_Z, L.DZ0 - 0.004,
                      **bev(lod, 0.005, 2)))
    parts.append(boxp("ped_rail", "green", a + 0.022, b - 0.022, y0 + 0.03, y1 - 0.045, DRAWER_Z, L.DZ0))
    # modesty panel behind the legs
    parts.append(boxp("desk_modesty", "green", x0 + 0.04, a, y1 - 0.07, y1 - 0.05, 0.30, L.DZ0, **bev(lod, 0.004, 1)))
    if lod == 0:
        # drawer bracket handle on posts, a tag frame, a lock
        hw = P("desk_handle", "chrome")
        cx = (a + b) / 2
        zh = DRAWER_Z + 0.030
        yy = y0 + 0.012
        g.pipe(hw, spline([(cx - 0.060, yy + 0.004, zh), (cx - 0.060, yy - 0.014, zh), (cx - 0.048, yy - 0.024, zh),
                           (cx + 0.048, yy - 0.024, zh), (cx + 0.060, yy - 0.014, zh), (cx + 0.060, yy + 0.004, zh)], 2),
               0.0045, 6)
        for xx in (cx - 0.060, cx + 0.060):
            lathe(hw, [(0.0075, 0.0), (0.0055, 0.0040)], 8, (xx, yy, zh), (0, -1, 0), cap1=True)
        frame_ring(hw, cx, DRAWER_Z + 0.056, 0.064, 0.024, 0.056, 0.016, yy - 0.0016, yy + 0.001)
        lathe(hw, [(0.0065, 0.0), (0.0055, 0.004)], 8, (b - 0.075, yy, DRAWER_Z + 0.056), (0, -1, 0), cap1=True)
        parts.append(hw)
        parts.append(boxp("desk_label", "paper_plain", cx - 0.028, cx + 0.028, yy - 0.0008, yy + 0.001,
                          DRAWER_Z + 0.048, DRAWER_Z + 0.064))
        # glides under the leg support (the pedestal sides stand on the floor)
        gl = P("desk_glides", "black")
        for yy_ in (y0 + 0.045, y1 - 0.045):
            g.cyl(gl, (x0 + 0.026, yy_, 0.006), "z", 0.014, 0.012, 8)
        parts.append(gl)
    return parts


DRAWER_Z = L.DZ0 - 0.075


# =============================================================================
# Terminal and keyboard
# =============================================================================
def build_terminal(spec):
    lod, n = spec["lod"], spec["sides"]
    cx, w = L.TXC, L.TW / 2
    y0, yb = L.TY0, L.TY0 + L.T_FRONT
    z0, z1 = L.TZ0, L.TZ1
    pw, ph, pr, pd = L.POCKET
    parts = []
    # plinth: a rounded plate
    pl = P("term_plinth", "case_dark")
    if lod == 0:
        g.prism(pl, rrect(cx, (y0 + 0.05 + L.TY1 - 0.07) / 2, 0.36, L.TY1 - 0.07 - y0 - 0.05, 0.03, 3), (0, 1), DZ, z0)
    else:
        g.box(pl, cx - 0.18, cx + 0.18, y0 + 0.05, L.TY1 - 0.07, DZ, z0)
    parts.append(pl)
    if lod == 0:
        # front part of the body - a rounded box, the tube window cut by boolean (the window walls
        # are a black frame)
        base = P("term_front_base", "case")
        g.box(base, cx - w, cx + w, y0, yb, z0, z1, r=L.T_R, seg=2)
        cut = P("term_pocket", "bezel")
        g.prism(cut, rrect(cx, L.SCR_Z, pw, ph, pr, 4), (0, 2), y0 - 0.01, y0 + pd)
        parts.append(M.boolean("term_front", base, [cut]))
    else:
        fr = P("term_front", "case")
        sx0, sx1 = cx - pw / 2, cx + pw / 2
        sz0, sz1 = L.SCR_Z - ph / 2, L.SCR_Z + ph / 2
        if lod == 2:
            g.box(fr, cx - w, cx + w, y0, yb, z0, z1)
        else:
            g.box(fr, cx - w, sx0, y0, yb, z0, z1)
            g.box(fr, sx1, cx + w, y0, yb, z0, z1)
            g.box(fr, sx0, sx1, y0, yb, sz1, z1)
            g.box(fr, sx0, sx1, y0, yb, z0, sz0)
            bz = P("term_bezel", "bezel")
            g.box(bz, sx0, sx1, y0 + 0.004, y0 + pd, sz0, sz1)
            parts.append(bz)
        parts.append(fr)
    # rear part - narrows toward the back and downward
    bk = P("term_back", "case")
    k = 2 if lod == 0 else 1
    front_ring = [(x, yb - 0.002, z) for x, z in rrect(cx, (z0 + z1) / 2, 2 * w - 0.012, z1 - z0 - 0.012, 0.02, k)]
    back_ring = [(x, L.TY1, z) for x, z in rrect(cx, z0 + 0.105, 0.30, 0.19, 0.03, k)]
    hull(bk, front_ring + back_ring)
    parts.append(bk)
    # tube glass has its own texture (the screen section): the mod script cycles the working frames
    sc = P("term_screen", "screen", group=SEL_SCREEN, section="screen")
    y_edge = y0 + pd - 0.0012
    if lod == 2:
        g.quad(sc, [(cx - L.SCR_W / 2, y0 - 0.002, L.SCR_Z - L.SCR_H / 2), (cx + L.SCR_W / 2, y0 - 0.002, L.SCR_Z - L.SCR_H / 2),
                    (cx + L.SCR_W / 2, y0 - 0.002, L.SCR_Z + L.SCR_H / 2), (cx - L.SCR_W / 2, y0 - 0.002, L.SCR_Z + L.SCR_H / 2)])
        y_edge = y0 - 0.002
    else:
        bulge_rr(sc, cx, y_edge, L.SCR_Z, L.SCR_W, L.SCR_H, L.SCR_R, 4 if lod == 0 else 1, L.SCR_SAG, 3 if lod == 0 else 2)
    sc.glass_frame = (g.Frame((cx, y_edge, L.SCR_Z), (1, 0, 0), (0, 0, 1), (0, -1, 0)), -L.SCR_W / 2, L.SCR_W / 2,
                      -L.SCR_H / 2, L.SCR_H / 2)
    parts.append(sc)
    ld = P("term_lamp", "led_g", group=SEL_LAMP)
    lx, lz = L.T_LAMP
    if lod == 0:
        lathe(ld, [(0.0042, -0.001), (0.0042, 0.0018), (0.0020, 0.0036)], 8, (lx, y0, lz), (0, -1, 0), cap1=True)
    else:
        g.quad(ld, [(lx - 0.004, y0 - 0.001, lz - 0.004), (lx + 0.004, y0 - 0.001, lz - 0.004),
                    (lx + 0.004, y0 - 0.001, lz + 0.004), (lx - 0.004, y0 - 0.001, lz + 0.004)])
    parts.append(ld)
    if lod == 0:
        kn = P("term_knobs", "black")
        for kx_, kz in L.T_KNOBS:
            lathe(kn, [(0.0105, -0.001), (0.0105, 0.004), (0.0080, 0.0135)], 10, (kx_, y0, kz),
                  (0, -1, 0), cap1=True)
        # key switch on the right of the chin
        button(kn, cx + 0.209, z0 + 0.036, 0.018, 0.020, y0 + 0.001, 0.007, 0.002)
        # slots on the roof of the rear part, along the slope
        zf, zb_ = z1 - 0.006, z0 + 0.105 + 0.095
        for q in range(5):
            yy = yb + 0.045 + 0.04 * q
            zt = zf + (yy - yb + 0.002) / (L.TY1 - yb + 0.002) * (zb_ - zf)
            g.box(kn, cx - 0.10, cx + 0.10, yy - 0.0045, yy + 0.0045, zt - 0.0025, zt + 0.0012)
        # keyboard cord socket on the right side, a plug
        g.cyl(kn, (cx + w + 0.006, y0 + 0.045, z0 + 0.032), "x", 0.0075, 0.014, 8)
        parts.append(kn)
    # keyboard: a wedge-shaped body with rounded edges, a plate with keys
    kb = P("kbd_case", "case" if lod < 2 else "case_dark")
    prof = [(L.KY0, DZ + 0.0015), (L.KY1, DZ + 0.0015), (L.KY1, L.KZ_B), (L.KY0, L.KZ_F)]
    if lod == 0:
        profile_x(kb, fillet_poly(prof, (0.004, 0.004, 0.006, 0.009), 3), L.KX0, L.KX1, ch=0.003)
    else:
        g.prism(kb, prof, (1, 2), L.KX0, L.KX1)
    parts.append(kb)
    if lod < 2:
        pl = P("keyboard", "keyboard")
        ya, yb_ = L.KEYS[2] - 0.004, L.KEYS[3] + 0.004
        g.prism(pl, [(ya, L.key_zs(ya) - 0.001), (yb_, L.key_zs(yb_) - 0.001), (yb_, L.key_zs(yb_) + 0.002),
                     (ya, L.key_zs(ya) + 0.002)], (1, 2), L.KEYS[0] - 0.004, L.KEYS[1] + 0.004)
        parts.append(pl)
    if lod == 0:
        kk = {False: P("kbd_keys", "key_black"), True: P("kbd_keys_fn", "key_beige")}
        for kx0_, kx1_, ky0_, ky1_, beige in L.key_rects():
            keycap(kk[beige], kx0_, kx1_, ky0_, ky1_, 0.0075, 0.0018)
        parts += list(kk.values())
        # cord to the socket on the terminal side
        parts.append(cable("kbd_cord", "black", [(L.KX1 - 0.04, L.KY1 - 0.002, DZ + 0.030),
                                                 (L.KX1 - 0.03, L.KY1 + 0.025, DZ + 0.004),
                                                 (cx + w + 0.020, y0 - 0.030, DZ + 0.0035),
                                                 (cx + w + 0.034, y0 + 0.020, DZ + 0.012),
                                                 (cx + w + 0.024, y0 + 0.045, z0 + 0.026),
                                                 (cx + w + 0.012, y0 + 0.045, z0 + 0.032)], 0.0032, lod))
        # power and data cable (in one braid) from the back - over the rear table edge into the
        # raised floor
        r = 0.006
        parts.append(cable("term_cable", "cable",
                           [(cx - 0.05, L.TY1 - 0.004, z0 + 0.045), (cx - 0.06, L.TY1 + 0.006, z0 + 0.012),
                            (cx - 0.07, L.DY1 - 0.008, DZ + r + 0.0005), (cx - 0.075, L.DY1 + 0.009, DZ - 0.006),
                            (cx - 0.08, L.DY1 + 0.018, DZ - 0.12), (cx - 0.085, L.DY1 + 0.03, 0.10),
                            (cx - 0.09, L.DY1 + 0.045, -0.02)], r, lod))
    return parts


# =============================================================================
# Printer and paper
# =============================================================================
def lid_z(y):
    """Height of the sloped printer cover above point y."""
    (ya, za), (yb, zb) = L.P_FRONT, L.P_REAR
    return za + (y - ya) * (zb - za) / (yb - ya)


def build_printer(spec):
    lod, n = spec["lod"], spec["sides"]
    x0, x1, y0, y1 = L.PX0, L.PX1, L.PY0, L.PY1
    bx0, bx1, by0, by1, bz0 = L.P_BAY
    sil = [(y0, DZ + 0.002), (y1, DZ + 0.002), (y1, L.P_REAR[1]), L.P_REAR, L.P_FRONT, (y0 + 0.012, DZ + 0.088),
           (y0, DZ + 0.078)]
    parts = []
    if lod == 0:
        # body - a rounded profile, the mechanism bay under the cover cut by boolean (black inside)
        base = P("printer_base", "case")
        profile_x(base, fillet_poly(sil, (0.003, 0.003, 0.008, 0.004, 0.004, 0.012, 0.004), 3), x0, x1, ch=0.005)
        cut = P("printer_bay", "black")
        g.box(cut, bx0, bx1, by0, by1, bz0, L.PZ1 + 0.05)
        parts.append(M.boolean("printer", base, [cut]))
        # cover - transparent (the glass section): the platen and the carriage are visible under it
        lid = P("printer_lid", "glass", section="glass")
        ya, yb = by0 - 0.004, L.P_EXIT[0]
        g.prism(lid, [(ya, lid_z(ya) + 0.0004), (yb, lid_z(yb) + 0.0004), (yb, lid_z(yb) + 0.0034),
                      (ya, lid_z(ya) + 0.0034)], (1, 2), bx0 - 0.004, bx1 + 0.004)
        parts.append(lid)
    else:
        pr = P("printer", "case")
        g.prism(pr, sil, (1, 2), x0, x1)
        parts.append(pr)
        if lod == 1:
            lid = P("printer_lid", "case_dark")
            ya, yb = by0, L.P_EXIT[0]
            g.prism(lid, [(ya, lid_z(ya)), (yb, lid_z(yb)), (yb, lid_z(yb) + 0.003), (ya, lid_z(ya) + 0.003)], (1, 2),
                    bx0, bx1)
            parts.append(lid)
    if lod < 2:
        # knurled platen knob on the right side
        kn = P("printer_knob", "black")
        py_, pz_, _ = L.PLATEN
        if lod == 0:
            knurl_x(kn, x1, py_, pz_, 0.0, 0.020, 0.021, 12, 0.0016)
            lathe(kn, [(0.019, 0.020), (0.013, 0.0245), (0.006, 0.0255)], 12, (x1, py_, pz_), (1, 0, 0), cap1=True)
        else:
            g.cyl(kn, (x1 + 0.011, py_, pz_), "x", 0.021, 0.022, 8)
        parts.append(kn)
    if lod == 0:
        # mechanism: platen, guides, ribbon cartridge, a pressure bar with rollers, tractors and the
        # feed slot
        py_, pz_, pr_ = L.PLATEN
        mc = P("printer_platen", "platen")
        g.cyl(mc, ((bx0 + bx1) / 2, py_, pz_), "x", pr_, bx1 - bx0 - 0.008, 20)
        parts.append(mc)
        rb = P("printer_ribbon", "ribbon")
        g.box(rb, bx0 + 0.010, bx1 - 0.010, by0 + 0.006, by0 + 0.034, bz0, bz0 + 0.036, r=0.003, seg=1)
        parts.append(rb)
        st = P("printer_steel", "chrome")
        for yy, zz in ((L.P_HEAD_Y - 0.010, bz0 + 0.020), (L.P_HEAD_Y + 0.010, bz0 + 0.020)):
            g.cyl(st, ((bx0 + bx1) / 2, yy, zz), "x", 0.0035, bx1 - bx0, 8)
        g.cyl(st, ((bx0 + bx1) / 2, py_ + 0.022, pz_ + 0.022), "x", 0.0025, bx1 - bx0 - 0.004, 6)
        parts.append(st)
        rr = P("printer_bail_rollers", "rubber")
        for xx in (L.PXC - 0.08, L.PXC, L.PXC + 0.08):
            g.cyl(rr, (xx, py_ + 0.022, pz_ + 0.022), "x", 0.0062, 0.014, 8)
        parts.append(rr)
        tr = P("printer_tractors", "case_dark")
        for xx in (L.PXC - L.PAPER_W / 2 + 0.007, L.PXC + L.PAPER_W / 2 - 0.007):
            g.box(tr, xx - 0.016, xx + 0.016, 0.098, 0.172, L.P_REAR[1], L.P_REAR[1] + 0.016, r=0.003, seg=1)
        parts.append(tr)
        sl = P("printer_slot", "black")
        g.box(sl, L.PXC - L.PAPER_W / 2 - 0.004, L.PXC + L.PAPER_W / 2 + 0.004, 0.124, 0.142, L.P_REAR[1] - 0.0005,
              L.P_REAR[1] + 0.0012)
        parts.append(sl)
        # carriage with the head (bone ozl_head): a body, a radiator of fins, a nose toward the
        # platen
        hd = P("printer_head", "head", group=SEL_HEAD)
        hx = L.PXC - L.HEAD_TRAVEL / 2
        g.box(hd, hx - 0.017, hx + 0.017, L.P_HEAD_Y - 0.016, L.P_HEAD_Y + 0.012, bz0 + 0.012, bz0 + 0.052,
              r=0.002, seg=1)
        for q in range(4):
            xx = hx - 0.012 + q * 0.008
            g.box(hd, xx - 0.0012, xx + 0.0012, L.P_HEAD_Y - 0.014, L.P_HEAD_Y + 0.008, bz0 + 0.052, bz0 + 0.064)
        g.box(hd, hx - 0.006, hx + 0.006, L.P_HEAD_Y + 0.012, py_ - pr_ - 0.002, pz_ - 0.008, pz_ + 0.006)
        parts.append(hd)
        # panel buttons at the front right
        bt = P("printer_buttons", "case_dark")
        for q in range(3):
            button(bt, x1 - 0.110 + 0.025 * q, L.P_LAMP_Z - 0.024, 0.017, 0.012, y0 + 0.001, 0.005, 0.0015)
        parts.append(bt)
        # Centronics connector on the back and a cable over the table edge into the raised floor
        parts.append(boxp("printer_plug", "cable_beige", x0 + 0.040, x0 + 0.095, y1, y1 + 0.022, DZ + 0.030, DZ + 0.055,
                          r=0.003, seg=1))
        parts.append(cable("printer_cable", "cable_beige",
                           [(x0 + 0.068, y1 + 0.020, DZ + 0.042), (x0 + 0.064, y1 + 0.060, DZ + 0.020),
                            (x0 + 0.060, L.DY1 - 0.012, DZ + 0.0065), (x0 + 0.058, L.DY1 + 0.009, DZ - 0.006),
                            (x0 + 0.056, L.DY1 + 0.018, DZ - 0.13), (x0 + 0.050, L.DY1 + 0.03, 0.10),
                            (x0 + 0.046, L.DY1 + 0.04, -0.02)], 0.006, lod))
    # lamps: power is steady, "ready" blinks, "no paper" is off
    groups = {"lamp": P("printer_lamps", "led_g", group=SEL_LAMP), "blink": P("printer_lamps_blink", "led_a", group=SEL_BLINK),
              "off": P("printer_lamp_off", "led_off")}
    for lx, c, role in L.P_LAMPS:
        p = groups[role]
        use(p, "led_off" if role == "off" else "led_" + c)
        if lod == 2:
            g.quad(p, [(lx - 0.004, y0 - 0.001, L.P_LAMP_Z - 0.003), (lx + 0.004, y0 - 0.001, L.P_LAMP_Z - 0.003),
                       (lx + 0.004, y0 - 0.001, L.P_LAMP_Z + 0.003), (lx - 0.004, y0 - 0.001, L.P_LAMP_Z + 0.003)])
        elif lod == 1:
            g.box(p, lx - 0.004, lx + 0.004, y0 - 0.002, y0, L.P_LAMP_Z - 0.003, L.P_LAMP_Z + 0.003)
        else:
            lathe(p, [(0.0035, -0.001), (0.0035, 0.0015), (0.0015, 0.0031)], 8, (lx, y0 + 0.0005, L.P_LAMP_Z),
                  (0, -1, 0), cap1=True)
    parts += [p for p in groups.values() if len(p.bm.faces)]
    # paper: a stack on the pedestal shelf, a web through the slot to the tractor, the printed web
    # on top
    sx0, sx1, py0, py1, pz0, pz1 = L.STACK
    parts.append(boxp("paper_stack", "paper", sx0, sx1, py0, py1, pz0, pz1, **bev(lod, 0.0015, 1)))
    if lod < 2:
        parts.append(paper_web("paper_in", "paper_plain", L.IN_PATH, lod, k=1))
        parts.append(paper_web("paper_out", "paper", L.OUT_PATH, lod, k=2))
    return parts


def build_logbook(spec):
    """Media receiving log: open, a cover, the pages curved toward the spine (the ruling is a
    decal).
    """
    lod = spec["lod"]
    cx, cy = L.LOG
    pw, ph = L.LOG_PAGE
    if lod == 2:
        return []
    if lod == 1:
        return [boxp("logbook", "logbook", cx - pw, cx + pw, cy - ph / 2 - 0.003, cy + ph / 2 + 0.003, DZ, DZ + 0.010)]
    cv = P("logbook", "logbook")
    for s in (-1, 1):
        g.box(cv, *sorted((cx + s * 0.0012, cx + s * (pw + 0.004))), cy - ph / 2 - 0.004, cy + ph / 2 + 0.004, DZ,
              DZ + COVER_T)
    g.cyl(cv, (cx, cy, DZ + 0.0015), "y", 0.0045, ph + 0.008, 8)
    pg = P("logbook_pages", "pages")
    for s in (-1, 1):
        ts = [i / 8.0 for i in range(9)]
        top = [(cx + s * (0.0015 + t * (pw - 0.003)), page_z(t)) for t in ts]
        poly = top + [(cx + s * (pw - 0.0015), DZ + COVER_T), (cx + s * 0.0015, DZ + COVER_T)]
        if s < 0:
            poly = poly[::-1]
        g.prism(pg, poly, (0, 2), cy - ph / 2, cy + ph / 2)
    return [cv, pg]


def build_lod(spec):
    parts = build_cabinet(spec) + build_tape_deck(spec) + build_console(spec) + build_desk(spec)
    parts += build_terminal(spec) + build_printer(spec) + build_logbook(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """The cabinet with the console; the desk with the terminal up to the top of the CRT body; the
    right part of the desk with the printer. A component thinner than 0.5 m does not work in
    the engine, so the desk is boxes down to the floor.
    """
    metal = kx.PEN + r"\metalplate.rvmat"
    plastic = kx.PEN + r"\plastic.rvmat"
    comps = [(kx.box_pts(L.X0, L.X1, L.CY0 - 0.02, L.CY1, 0.0, L.CON[5]), metal),
             (kx.box_pts(L.DX0, L.PED[0], L.DY0, L.DY1, 0.0, L.TZ1), plastic),
             (kx.box_pts(L.PED[0], L.DX1, L.DY0, L.DY1 + 0.015, 0.0, L.PZ1), metal)]
    rl, rr = L.REELS
    hx = L.PXC - L.HEAD_TRAVEL / 2
    hz = L.P_BAY[4] + 0.03
    memory = {
        "invView": [(0.1, -2.7, 1.5)],
        "ce_center": [(0.0, 0.0, 0.9)],
        "ce_radius": [(1.1, 0.0, 0.9)],
        "ozl_reel_l_axis": [(rl[0], L.YD, rl[1]), (rl[0], L.YD - 0.05, rl[1])],
        "ozl_reel_r_axis": [(rr[0], L.YD, rr[1]), (rr[0], L.YD - 0.05, rr[1])],
        "ozl_head_axis": [(hx, L.P_HEAD_Y, hz), (hx + 1.0, L.P_HEAD_Y, hz)],
    }
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 150.0, memory, bbox


# The first ones are for the --look preview: overall view, the terminal (screen and lamps while
# working), reels, printer, console
SHOTS = [
    ("front", (-0.95, -3.25, 1.75), (0.0, 0.0, 0.88), 30),
    ("terminal", (0.36, -1.12, 1.28), (0.34, -0.06, 0.86), 32),
    ("reels", (-0.45, -1.15, 1.45), (L.CXC, L.YD, 1.30), 34),
    ("printer", (1.25, -0.92, 1.24), (L.PXC, 0.0, 0.84), 32),
    ("console", (-0.45, -0.95, 1.95), (L.CXC, L.CON_Y, 1.72), 36),
    ("left", (-2.5, -1.3, 1.55), (-0.62, 0.05, 1.05), 30),
    ("right", (2.4, -0.9, 1.4), (0.0, 0.0, 0.8), 30),
    ("back", (1.4, 2.6, 1.6), (0.0, 0.1, 0.8), 30),
]

M.look_shots = (5, 3)
M.run(build_lod, collision, SHOTS, row_step=2.4, row_shot=((2.4, -8.5, 2.2), (2.4, 0, 0.9)))
