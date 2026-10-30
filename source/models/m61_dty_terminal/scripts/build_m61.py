"""M61 - command desk: the Duty faction terminal (OZL_Dty_Terminal). Result carriers are handed in here
and the research tree is opened, like reporting to the commander; there are no modules.

    blender --background --python build_m61.py -- [--geo] [--look] [--stats] [--skip-bake] [--no-paa] [--preview]

Before the first run, run make_decals.py with the system Python (the map under the glass, the cover
of the "Delo" folder, the spread of the open folder). Where things go: layout.py (shared with
make_decals.py); own geometry: m61_geo.py.

The device is the commander's desk at headquarters. Sizes:
- two-pedestal writing desk: 1.50 x 0.75 m, desktop at 0.76 (a writing desk is 750 high per GOST
  13025.3-85); pedestals 0.40 each, legroom opening 0.66, plinth 0.05;
- 8 mm thick glass on the desktop (1.42 x 0.69) with its own map 0.90 x 0.60 under it (make_decals.py);
- cardboard "Delo" folder ~0.24 x 0.33 (measured against a ruler in a reference photo; a listing
  quotes 36 x 25 cm), with ties, a cover without text, empty fields only;
- TA-57 field telephone: 222 x 165 x 79 mm, 2.8 kg (Wikipedia: TA-57; a Hungarian postal museum
  catalogue gives 220 x 170 x 80), case and lid with rounded corners, hinges at the side, a handset
  with a push-to-talk key; the call lamp on the lid (ozl_lamp_2) is invented, a real TA-57 has none;
- R-158 portable radio: 80 x 165 x 263 mm, 3.6 kg (Wikipedia: R-158), stands on the desk, flexible
  antenna, push-to-talk handset beside it on a coiled cord; dark grey case (not olive);
- gooseneck desk lamp: base D0.14, stem ~0.55, shade D0.13 - estimated from photos of Soviet lamps;
- stamped ashtray D0.10, 200 ml glass in a holder (D66 x 105), stamp with a turned handle and an ink
  pad in a tin, red-blue pencil 175 mm (D7.5, hexagonal) - estimated; cigarette pack 88 x 55 x 22
  (as in M16).

Layout. Pedestal drawers and the player are on the -Y side (the working side, the commander's seat),
an apron panel is at the back (+Y). The left pedestal has a drawer on top and a door with a red panel
in mouldings (the swappable Duty colour), the right one has four drawers; a flat drawer sits in the
middle under the desktop. Handles are aluminium brackets with rosettes, the door has a bracket and
hinges, drawers and door carry brass lock plates; the side of the left pedestal has an empty
inventory tag on tacks.
On the desk: glass with the map under it; flags on lead stands across the map (a pin cannot be pushed
into glass); two stacks of folders on the left, the top ones tied with bows; the open folder at the
front centre (inventory and typescript unreadable, a blue stamp without text) with a red-blue pencil,
a paper clip and a pen on it; the lamp at back left with the shade over the map; the TA-57 on the
right, the handset lies on the lid, the field cable goes behind the desk to the floor; the R-158 at
back right, the push-to-talk handset on a coiled cord; an ashtray with papirosa butts, a cigarette
pack, matches, a glass in a holder, a stamp and an ink pad.
Duty look: dark wood and a red panel, no olive; worn by frequent use - the varnish is rubbed down to
light wood on the desktop edges and by the drawer and door handles, scratches; everything in place,
no rust (own build_wood_worn; build_worn comes from the M23 generator, for the red panel and metal).

Detailing:
- "dayz" look (matte, dirtier, coloured AO); on small items (telephone, radio, lamp, glass holder,
  flags) the profile's dirt layers are finer (SMALL; the `small` wrapper swaps Tree.coords while the
  material is built, the kit is untouched);
- no angularity: the desktop has a rounded edge and corners, the facades have rounded edges, handles
  are smooth oval-section brackets with rosettes, the door has hinges and mouldings around the panel,
  lock plates; glass with a polished edge; folders with rounded corners, a spine and an uneven pile
  of sheets, ties as ribbons;
- TA-57: case and lid with rounded corners and edges, a seam, hinges, latches, terminals with knurled
  nuts; the handset follows a reference photo: earpiece cup, a handle with a key, microphone cup,
  cord socket;
- R-158: rounded case, a battery-compartment seam with latches, a speaker grille in a frame, an empty
  nameplate on rivets, knurled knobs with arrows, a spring-mounted antenna with a tip, strap rings;
  cast push-to-talk handset with a key, coiled cord;
- lamp: corrugated gooseneck with sleeves, a shade with a rolled edge and ventilation slits at the top
  (they glow when working, so a lit lamp is visible from above too), turned base, push-button
  switch, smooth cord;
- small items: glass holder with a knurled band and a ribbon handle, a thin glass with a spoon;
  stamped ashtray with notches (as in M17), papirosa butts with a crushed sleeve; stamp with a turned
  handle; flags are cloth pennants with a wave, pins with heads; red-blue pencil;
- vanilla DayZ items as proxies (no Proxy<name> class): a pen on the sheet, a compass on the map,
  binoculars on the rear stack, matches by the ashtray, a flashlight at the edge of the map; the
  cigarette pack is an own box with the vanilla pack texture by path (as in M16/M17: for a proxy pack
  the config sets the brand);
- working state: the lamp is lit - shade interior, bulb and slits (onSelections ozl_lamp); the TA-57
  call lamp blinks (blink ozl_lamp_2). There are no moving parts.

Machine states: the lamp (shade interior, slits and bulb) is ozl_lamp, the TA-57 call lamp is
ozl_lamp_2 (both in hiddenSelections); "working" is the atlas _on_co and the rvmat _on with emission.

The desktop glass and the tea glass use the glass section (_ca + glass rvmat, as in M01/M02). LODs:
the middle one makes a box per folder, without ties, paper clips, rosette handles and coiled cords
(a flag is a plate); the far one makes each stack a single box, without flags, clips and glass.

Blender axes: X is width, Y is depth (the front face is -Y), Z is up.
"""
import contextlib
import math
import os
import random
import sys

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
import m61_geo as G  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

# =============================================================================
# Dimensions, m
# =============================================================================
X0, X1, Y0, Y1, ZT = L.X0, L.X1, L.Y0, L.Y1, L.ZT
ZU = ZT - L.TOP_T                                            # underside of the desktop
ZG = L.ZG                                                    # top of the glass
PED = ((-0.73, -0.33), (0.33, 0.73))                         # pedestals along x
PY0, PY1 = -0.352, 0.352                                     # pedestal body along y
ZP = 0.05                                                    # plinth
FT = 0.018                                                   # facade thickness
YF = PY0 - FT                                                # face of the facades
# right pedestal: four drawers (bottom to top, facade heights)
DRAWERS_R = ((0.060, 0.235), (0.239, 0.400), (0.404, 0.560), (0.564, 0.718))
# left pedestal: a door and a drawer above it
DOOR = (0.060, 0.556)
DRAWER_L = (0.560, 0.718)
# middle drawer under the desktop
MID = (-0.326, 0.326, 0.640, 0.718)
HANDLE_W = 0.096

LOD_SPECS = [
    dict(lod=0, sides=16),
    dict(lod=1, sides=8),
    dict(lod=2, sides=5),
]

REGIONS = {
    "top": ("top", 0.9), "carcass": ("carcass", 0.5), "front": ("front", 0.8), "door": ("door", 0.8),
    "red": ("red", 0.8), "plinth": ("plinth", 0.3), "handle": ("handle", 2.0), "brass": ("brass", 2.4),
    "plate": ("plate", 3.0), "map": ("map", 3.6), "glass": ("steel", 1.0),
    "card": ("card", 1.6), "card_b": ("card_b", 1.6), "paper": ("paper", 2.2), "paper_old": ("paper_old", 0.6),
    # lower folders and sheets: their tops are covered, only the edges show, so they get little atlas space
    "card_lo": ("card", 0.35), "card_b_lo": ("card_b", 0.35), "paper_lo": ("paper", 0.35),
    "tape": ("tape", 1.5), "clip": ("clip", 2.0),
    "bakelite": ("bakelite", 2.2), "black": ("black", 2.0), "lamp2": ("lamp2", 4.0), "chrome": ("chrome", 2.0),
    "cable": ("cable", 0.25), "antenna": ("antenna", 0.6), "radio": ("radio", 1.8), "grille": ("grille", 2.5),
    "knob": ("knob", 2.5), "rubber": ("rubber", 2.0), "gasket": ("gasket", 1.5),
    "lamp_body": ("lamp_body", 1.6), "goose": ("goose", 0.9), "shade_in": ("shade_in", 1.6), "bulb": ("bulb", 2.0),
    "vent": ("vent", 3.0),
    "ashtray": ("ashtray", 2.0), "ash": ("ash", 2.0), "butt": ("butt", 3.0),
    "nickel": ("nickel", 2.2), "tea": ("tea", 2.0),
    "flag_red": ("flag_red", 3.0), "flag_blue": ("flag_blue", 3.0), "pin": ("pin", 3.0), "lead": ("lead", 3.0),
    "wood_knob": ("wood_knob", 2.5), "stamp_rubber": ("stamp_rubber", 2.0), "tin": ("tin", 2.0), "pad": ("pad", 2.5),
    "pencil_red": ("pencil_red", 3.0), "pencil_blue": ("pencil_blue", 3.0), "pencil_wood": ("pencil_wood", 3.0),
    "carton": ("paper_old", 1.0),
}


# =============================================================================
# Materials
# =============================================================================
def rub_mask(t, pos, grain, rub):
    """Sum of "rubbed by hands" ellipsoids: [(centre, semi-axes, strength)], weaker towards the edge."""
    f = 0.0
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
        m = t.math("MULTIPLY", t.math("MULTIPLY", near, grain), k)
        f = m if isinstance(f, float) else t.math("ADD", f, m)
    return f


def build_wood_worn(mat, origin, color, bare, seed=1.0, along="x", gloss=0.42, spec=0.22, wear=(0.66, 0.72),
                    edge_k=0.8, rub=(), scratch=0.0, rings=0.35, floor_z=0.0, dust=0.12, grime=0.3, decal_items=()):
    """Dark stained wood under varnish, worn by frequent use (Duty look): on the edges (edge_k) and where
    hands rub (rub) the varnish and stain are worn down to the light wood bare, which is more matte;
    scratches along the grain. The grain pattern is as in kwood.build_wood."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    k = {"x": (0.04, 1.0, 1.0), "y": (1.0, 0.04, 1.0), "z": (1.0, 1.0, 0.04)}[along]
    fib = t.stretch(vec, *k)
    fibers = t.noise(fib, 160.0, 4.0, 0.7)
    wave = t.node("ShaderNodeTexWave", Scale=9.0, Distortion=6.0, **{"Detail": 3.0, "Detail Scale": 1.5})
    wave.wave_type = "RINGS"
    t.link(fib, wave.inputs["Vector"])
    ring = t.math("MULTIPLY", wave.outputs["Fac"], rings)
    tone = t.maprange(t.noise(vec, 1.6, 3.0, 0.5), 0.3, 0.7, 0.0, 1.0)

    def grain_col(c):
        dark = tuple(x * 0.6 for x in c[:3]) + (1,)
        b = t.mixc(tone, tuple(x * 0.88 for x in c[:3]) + (1,), tuple(min(1.0, x * 1.1) for x in c[:3]) + (1,))
        b = t.mixc(t.math("MULTIPLY", ring, 0.8), b, dark)
        return t.mixc(t.math("MULTIPLY", t.math("SUBTRACT", fibers, 0.35), 0.5), b, dark)
    col = grain_col(color)
    col = kmats.decals(t, col, sep, nsep, decal_items)
    edge = t.maprange(t.edge_wear(0.004), 0.05, 0.22, 0.0, 1.0)
    grain = t.maprange(t.noise(vec, 34.0, 8.0, 0.7), 0.3, 0.7, 0.55, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 11.0, 10.0, 0.7), 0.75), t.math("MULTIPLY", edge, edge_k))
    if rub:
        f = t.math("ADD", f, rub_mask(t, pos, grain, rub))
    worn = t.step(f, wear[0], wear[1])
    soft = t.step(f, wear[0] - 0.08, wear[1])                 # half-worn varnish: the transition
    col = t.mixc(t.math("MULTIPLY", soft, 0.5), col, grain_col(tuple((a + b) / 2 for a, b in zip(color, bare))))
    col = t.mixc(worn, col, grain_col(bare))
    g_ = t.math("SUBTRACT", gloss, t.math("MULTIPLY", soft, gloss - 0.12))
    s_ = t.math("SUBTRACT", spec, t.math("MULTIPLY", soft, spec - 0.06))
    h = t.math("ADD", t.math("MULTIPLY", fibers, 0.2), t.math("MULTIPLY", worn, -0.15))
    if scratch > 0:
        sc = t.step(t.noise(t.stretch(vec, 0.02, 1.0, 1.0), 260.0, 2.0, 0.5), 0.70, 0.73)
        sc = t.math("MULTIPLY", sc, t.maprange(t.noise(vec, 5.0, 4.0, 0.5), 0.35, 0.65, 0.0, scratch))
        col = t.mixc(t.math("MULTIPLY", sc, 0.6), col, grain_col(bare))
        h = t.math("SUBTRACT", h, t.math("MULTIPLY", sc, 0.12))
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    return kmats.out(t, col, g_, s_, h)


def build_worn(mat, origin, color, bare=kmats.lin((112, 112, 116)), seed=1.0, gloss=0.32, spec=0.25,
               wear=(0.66, 0.71), edge_k=0.7, rub=(), scratch=0.0, floor_z=0.0, dust=0.15, grime=0.3):
    """Paint worn down to metal (or to wood, bare) on the edges and where hands rub, no rust (Duty look):
    the M23 builder without stripes, oil and decals."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, seed)
    nsep = t.normal()
    pos = sep.inputs[0].links[0].from_socket
    col = t.mixc(t.maprange(t.noise(vec, 2.5, 6.0, 0.55), 0.3, 0.75, 0.0, 1.0),
                 tuple(c * 0.9 for c in color[:3]) + (1,), color)
    edge = t.maprange(t.edge_wear(0.004), 0.05, 0.22, 0.0, 1.0)
    f = t.math("ADD", t.math("MULTIPLY", t.noise(vec, 11.0, 10.0, 0.7), 0.75), t.math("MULTIPLY", edge, edge_k))
    grain = t.maprange(t.noise(vec, 34.0, 8.0, 0.7), 0.3, 0.7, 0.55, 1.0)
    if rub:
        f = t.math("ADD", f, rub_mask(t, pos, grain, rub))
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
    col, dirt = kmats.weather(t, col, vec, sep, nsep, floor_z, dust, grime)
    g_ = t.math("SUBTRACT", g_, t.math("MULTIPLY", dirt, gloss * 0.5))
    s_ = t.math("SUBTRACT", s_, t.math("MULTIPLY", dirt, spec * 0.4))
    return kmats.out(t, col, g_, s_, h)


def build_print(mat, origin, color, gloss=0.08, spec=0.04, mottle=0.06, decal_items=()):
    """Paper and cardboard: an even tone in blotches plus print (decals), with no dirt and no corner shading;
    on the map under the glass and on the folders those would bake in as dark spots from neighbouring items."""
    t = kmats.Tree(mat)
    vec, sep = t.coords(origin, 6.0)
    nsep = t.normal()
    col = t.mixc(t.maprange(t.noise(vec, 9.0, 4.0, 0.5), 0.3, 0.7, 0.0, 1.0),
                 tuple(c * (1 - mottle) for c in color[:3]) + (1,), color)
    col = kmats.decals(t, col, sep, nsep, decal_items)
    return kmats.out(t, col, gloss, spec, 0.0)


# The "dayz" profile layers (tonal blotches, streaks, grease stains, scratches - kmats.dayz_layers) are
# tuned for machines 1-2 m in size: on a 22 cm telephone or a glass holder a single blotch covers the
# whole item. For small items the material noise is made SMALL times finer: while their material is built
# the pattern coordinates (Tree.coords) are stretched, and the kit is not changed (same SMALL as in M62).
SMALL = 3.0


@contextlib.contextmanager
def fine(k):
    orig = kmats.Tree.coords

    def coords(self, origin, seed):
        vec, sep = orig(self, origin, seed)
        return self.stretch(vec, k, k, k), sep
    kmats.Tree.coords = coords
    try:
        yield
    finally:
        kmats.Tree.coords = orig


def small(builder, k=SMALL):
    """Material builder for small items: the same, but the pattern and dirt layers are k times finer."""
    def fn(mat, origin, **kw):
        b = kmats.BUILDERS[builder] if isinstance(builder, str) else builder
        with fine(k):
            return b(mat, origin, **kw)
    return fn


def top_decal(name, center, size, z, tol=0.0008):
    """Decal facing up, only on faces at height z."""
    return (os.path.join(WORK, name), "z", 1, ("x", "y"), center, size, (z - tol, z + tol))


WOOD = kmats.lin((66, 38, 22))                               # walnut stain, almost black (warmer: the dayz profile desaturates)
BARE = kmats.lin((122, 90, 62))                             # wood under worn varnish
RED = kmats.lin((140, 26, 22))
CLEAN = dict(chip=(0.99, 1.0), rust=(0.99, 1.0), rust_low=0.0, dust=0.0, grime=0.0)
HX = [(a + b) / 2 for a, b in PED]                            # pedestal centres
FRONT_RUB = ([((HX[1], YF, zb - 0.045), (0.08, 0.04, 0.035), 0.38) for a, zb in DRAWERS_R] +
             [((HX[0], YF, DRAWER_L[1] - 0.045), (0.08, 0.04, 0.035), 0.38),
              ((-0.16, YF, (MID[2] + MID[3]) / 2), (0.07, 0.04, 0.03), 0.38),
              ((0.16, YF, (MID[2] + MID[3]) / 2), (0.07, 0.04, 0.03), 0.38)])
DOOR_X = PED[0][1] - 0.05                                    # door bracket at the right edge (hinges on the left)
DOOR_RUB = [((DOOR_X, YF, 0.40), (0.06, 0.05, 0.12), 0.55)]
TOP_RUB = [((0.0, Y0, ZT), (0.50, 0.06, 0.06), 0.28),       # front edge: elbows and papers
           ((-0.40, Y0, ZT), (0.12, 0.05, 0.06), 0.25),
           ((0.45, Y0, ZT), (0.12, 0.05, 0.06), 0.25)]
FOLDER_DECALS = [top_decal("decal_folder.png", (x, y), (L.FOLDER_W, L.FOLDER_D), L.stack_top(n))
                 for x, y, n, _ in L.STACKS]
OPEN_DECAL = [(os.path.join(WORK, "decal_open.png"), "z", 1, ("x", "y"), L.OPEN_C, L.OPEN_S,
               (ZG + 0.0002, L.OPEN_Z + 0.0008))]
MAP_DECAL = [top_decal("decal_map.png", L.MAP_C, L.MAP_S, L.ZM, tol=0.0002)]

KINDS = kmats.std_kinds(floor_z=0.0)
KINDS.update({
    "top": (build_wood_worn, dict(color=WOOD, bare=BARE, seed=1.4, along="x", edge_k=0.95, rub=TOP_RUB,
                                  scratch=0.5, floor_z=ZT, dust=0.05, grime=0.1)),
    "carcass": (build_wood_worn, dict(color=WOOD, bare=BARE, seed=2.2, along="z", wear=(0.70, 0.76), edge_k=0.7,
                                      scratch=0.2, dust=0.15, grime=0.45)),
    "front": (build_wood_worn, dict(color=WOOD, bare=BARE, seed=3.1, along="x", edge_k=0.8, rub=FRONT_RUB,
                                    scratch=0.3, dust=0.1, grime=0.35)),
    "door": (build_wood_worn, dict(color=WOOD, bare=BARE, seed=3.9, along="z", edge_k=0.8, rub=DOOR_RUB,
                                   scratch=0.3, dust=0.1, grime=0.4)),
    "plinth": (build_wood_worn, dict(color=kmats.lin((36, 24, 18)), bare=BARE, seed=4.6, along="x", wear=(0.62, 0.70),
                                     edge_k=0.9, dust=0.2, grime=0.9)),
    # red door panel: enamel over wood, worn down to wood by the bracket and along the edges
    "red": (build_worn, dict(color=RED, bare=kmats.lin((120, 84, 56)), seed=5.2, wear=(0.68, 0.73), edge_k=0.8,
                             rub=[((DOOR_X, YF, 0.40), (0.07, 0.05, 0.10), 0.35)], scratch=0.3, dust=0.1,
                             grime=0.35)),
    # handles are aluminium (lighter than steel, matte), lock plates are darkened brass
    "handle": (small("steel"), dict(seed=5.8, tone=0.42, along="x", gloss=0.5, spec=0.6, floor_z=0.0, dust=0.1,
                                    grime=0.35)),
    "brass": (small("paint"), dict(CLEAN, color=kmats.lin((140, 112, 60)), gloss=0.5, spec=0.5, dust=0.05,
                                   grime=0.5)),
    "plate": (small("steel"), dict(seed=6.3, tone=0.42, along="x", gloss=0.5, spec=0.6, dust=0.15, grime=0.2)),
    "map": (build_print, dict(color=kmats.lin((208, 196, 156)), gloss=0.12, spec=0.06, mottle=0.0,
                              decal_items=MAP_DECAL)),
    # folder cardboard is grey-beige, the paper is yellowed; cover print and the spread are decals (below)
    "paper_old": (small("plastic"), dict(color=kmats.lin((206, 186, 136)), gloss=0.06, spec=0.03, mottle=0.18,
                                         floor_z=ZG, dust=0.1, grime=0.2, scuff=(0.9, 1.0))),
    "tape": (small("plastic"), dict(color=kmats.lin((198, 188, 166)), gloss=0.05, spec=0.03, mottle=0.15,
                                    dust=0.1, grime=0.3)),
    "clip": (small("steel"), dict(seed=4.4, tone=0.38, along="x", gloss=0.6, spec=0.7, dust=0.0, grime=0.2)),
    # TA-57: bakelite, brown-black with swirls
    "bakelite": (small("plastic"), dict(color=kmats.lin((62, 32, 22)), gloss=0.55, spec=0.4, mottle=0.3, floor_z=ZG,
                                        dust=0.1, grime=0.25, scuff=(0.62, 0.7))),
    "black": (small("plastic"), dict(color=kmats.lin((22, 22, 23)), gloss=0.35, spec=0.25, dust=0.15)),
    "lamp2": ("flat", dict(color=kmats.lin((92, 52, 18)), gloss=0.85, spec=0.8)),
    "lamp2_on": ("flat", dict(color=kmats.lin((255, 170, 60)), gloss=0.85, spec=0.8)),
    "chrome": (small("steel"), dict(seed=7.1, tone=0.34, along="z", gloss=0.7, spec=0.8, floor_z=ZG, dust=0.1,
                                    grime=0.25)),
    "antenna": (small("steel"), dict(seed=7.3, tone=0.20, along="z", gloss=0.5, spec=0.5, floor_z=ZG, dust=0.05,
                                     grime=0.2)),
    "cable": ("plastic", dict(color=kmats.lin((26, 26, 24)), gloss=0.3, spec=0.2, dust=0.2, grime=0.3)),
    # R-158: dark grey enamel, worn to metal by the knobs and along the edges
    "radio": (small(build_worn), dict(color=kmats.lin((50, 52, 52)), seed=7.7, wear=(0.70, 0.75), edge_k=0.8,
                                      scratch=0.4, floor_z=ZG, dust=0.1, grime=0.2)),
    "grille": (small("steel"), dict(seed=8.0, tone=0.18, along="x", holes=(("x", "z"), 0.006, 0.30), gloss=0.3,
                                    spec=0.3, dust=0.2, grime=0.2)),
    "knob": (small("plastic"), dict(color=kmats.lin((20, 20, 21)), gloss=0.3, spec=0.25, dust=0.2,
                                    scuff=(0.6, 0.68))),
    "rubber": (small("plastic"), dict(color=kmats.lin((26, 26, 26)), gloss=0.1, spec=0.05, dust=0.3, scuff=(0.9, 1.0))),
    "gasket": (small("plastic"), dict(color=kmats.lin((14, 14, 14)), gloss=0.1, spec=0.05, dust=0.2, scuff=(0.9, 1.0))),
    # lamp: black enamel, base and shade worn along the edge; chrome gooseneck stem
    "lamp_body": (small(build_worn), dict(color=kmats.lin((26, 26, 28)), seed=8.4, wear=(0.70, 0.75), edge_k=0.9,
                                          floor_z=ZG, dust=0.15, grime=0.1)),
    "goose": (small("steel"), dict(seed=8.8, tone=0.34, along="z", gloss=0.6, spec=0.75, floor_z=ZG, dust=0.15,
                                   grime=0.3)),
    "shade_in": ("plastic", dict(color=kmats.lin((214, 208, 190)), gloss=0.6, spec=0.45, dust=0.2, grime=0.2)),
    "shade_in_on": ("flat", dict(color=kmats.lin((255, 244, 214)), gloss=0.6, spec=0.45)),
    # shade slits: shadow inside at rest, light when working (remap to shade_in_on)
    "vent": ("flat", dict(color=kmats.lin((46, 44, 40)), gloss=0.2, spec=0.1)),
    "bulb": ("flat", dict(color=kmats.lin((210, 206, 194)), gloss=0.7, spec=0.6)),
    "bulb_on": ("flat", dict(color=kmats.lin((255, 248, 222)), gloss=0.7, spec=0.6)),
    "ashtray": (small("steel"), dict(seed=9.2, tone=0.36, along="x", gloss=0.45, spec=0.55, floor_z=ZG, dust=0.0,
                                     grime=0.6)),
    "ash": ("plastic", dict(color=kmats.lin((112, 110, 106)), gloss=0.05, spec=0.03, mottle=0.4, dust=0.0, grime=0.0)),
    # papirosa sleeves: white paper, yellowed at the mouthpiece
    "butt": (small("plastic"), dict(color=kmats.lin((214, 206, 184)), gloss=0.1, spec=0.05, mottle=0.2, dust=0.0,
                                    grime=0.4)),
    # glass holder: melchior (cupronickel), darkened in the pattern
    "nickel": (small("steel"), dict(seed=9.6, tone=0.34, along="z", gloss=0.65, spec=0.75, floor_z=ZG, dust=0.0,
                                    grime=0.7)),
    "tea": ("flat", dict(color=kmats.lin((96, 46, 14)), gloss=0.9, spec=0.6)),
    "flag_red": (small("plastic"), dict(color=kmats.lin((168, 30, 26)), gloss=0.15, spec=0.08, mottle=0.12,
                                        dust=0.1)),
    "flag_blue": (small("plastic"), dict(color=kmats.lin((34, 60, 140)), gloss=0.15, spec=0.08, mottle=0.12,
                                         dust=0.1)),
    "pin": (small("steel"), dict(seed=9.9, tone=0.34, along="z", gloss=0.6, spec=0.7, dust=0.0, grime=0.2)),
    "lead": (small("plastic"), dict(color=kmats.lin((70, 72, 74)), gloss=0.35, spec=0.3, mottle=0.15, dust=0.1)),
    "wood_knob": (small("plastic"), dict(color=kmats.lin((150, 102, 60)), gloss=0.4, spec=0.25, mottle=0.2, dust=0.05,
                                         scuff=(0.55, 0.65))),
    "stamp_rubber": (small("plastic"), dict(color=kmats.lin((40, 36, 64)), gloss=0.1, spec=0.05, mottle=0.2,
                                            dust=0.0)),
    "tin": (small(build_worn), dict(color=kmats.lin((40, 40, 42)), seed=10.2, wear=(0.66, 0.71), edge_k=0.9,
                                    floor_z=ZG, dust=0.05, grime=0.2)),
    "pad": ("plastic", dict(color=kmats.lin((40, 46, 96)), gloss=0.15, spec=0.08, mottle=0.25, dust=0.0, grime=0.0)),
    # red-blue pencil: varnish, worn on the facets; the wood of the cut is light
    "pencil_red": (small("plastic"), dict(color=kmats.lin((168, 28, 24)), gloss=0.5, spec=0.35, mottle=0.08,
                                          dust=0.0, scuff=(0.6, 0.7))),
    "pencil_blue": (small("plastic"), dict(color=kmats.lin((30, 56, 140)), gloss=0.5, spec=0.35, mottle=0.08,
                                           dust=0.0, scuff=(0.6, 0.7))),
    "pencil_wood": (small("plastic"), dict(color=kmats.lin((200, 160, 112)), gloss=0.15, spec=0.08, mottle=0.2,
                                           dust=0.0)),
})
# folder decals go on cardboard and paper (by height, only the top of the decal's own folder and the
# spread are hit)
PAPER_DECALS = FOLDER_DECALS + OPEN_DECAL
KINDS.update({
    "card": (build_print, dict(color=kmats.lin((192, 174, 132)), mottle=0.1, decal_items=PAPER_DECALS)),
    "card_b": (build_print, dict(color=kmats.lin((172, 162, 136)), mottle=0.1, decal_items=PAPER_DECALS)),
    "paper": (build_print, dict(color=kmats.lin((222, 208, 168)), gloss=0.06, spec=0.03, decal_items=PAPER_DECALS)),
})

OBJ, NAME = "m61_dty_terminal", "ozr_dty_terminal"
# Machine states: the lamp is ozl_lamp, the telephone call lamp is ozl_lamp_2 (both in hiddenSelections);
# the default is "off", "working" is the atlas _on_co and the rvmat _on with emission; in the mod
# (OZL_Work) the lamp burns steadily and the call lamp blinks.
SEL_LAMP, SEL_LAMP2 = "ozl_lamp", "ozl_lamp_2"
ON = dict(remap={"shade_in": "shade_in_on", "vent": "shade_in_on", "bulb": "bulb_on", "lamp2": "lamp2_on"},
          emissive=(1.0, 1.0, 1.0, 1.0))
# cigarette pack: an own box with the vanilla pack texture by path (as in M16/M17)
CIGS = (r"dz\gear\medical\data\pack_of_cigs_cherno_co.paa", r"dz\gear\medical\data\pack_of_cigs.rvmat")
CIGS_UV = {"front": (0.117, 0.462, 0.43, 1.0), "side": (0.885, 0.970, 0.60, 1.0), "end": (0.26, 0.45, 0.20, 0.30)}
# vanilla DayZ items as proxies: a pen on a sheet of the open folder, a compass on the map, binoculars
# on the rear stack, matches by the ashtray, a flashlight at the edge of the map
BINOC = r"dz\gear\optics\binoculars"
COMPASS = r"dz\gear\navigation\compass"
DECOR = [
    kv.put("pen", (L.PEN[0], L.PEN[1], L.OPEN_Z), **kv.flat(L.PEN[2])),
    kv.put(COMPASS, (L.COMPASS[0], L.COMPASS[1], ZG), up=(0, 0, 1), fwd=(0.12, -1, 0)),
    kv.put(BINOC, (L.STACKS[1][0] + 0.002, L.STACKS[1][1] + 0.01, L.stack_top(L.STACKS[1][2])), **kv.flat(90)),
    kv.put("matchbox", (L.MATCHES[0], L.MATCHES[1], ZG), **kv.flat(L.MATCHES[2])),
    kv.put("flashlight", (L.FLASHLIGHT[0], L.FLASHLIGHT[1], ZG), **kv.flat(L.FLASHLIGHT[2])),
]
M = kmodel.Model(__file__, OBJ, NAME, REGIONS, KINDS, LOD_SPECS, atlas=2048, look="dayz",
                 glass=dict(base=(0.56, 0.66, 0.62), clear=0.05, edge=0.22, smudge=0.07, streaks=0.0),
                 selections=(SEL_LAMP, SEL_LAMP2), hidden=(SEL_LAMP, SEL_LAMP2), states={"on": ON},
                 decor=DECOR, vsections={"cigs": CIGS})
P = M.part
BOUNDS = {}


def rot_frame(cx, cy, z, deg):
    """Coordinate frame rotated about the vertical: local (a, b, c) are along, across, up."""
    return G.frame_z(cx, cy, deg, z)


# =============================================================================
# Desk
# =============================================================================
def handle(part, x, y, z, w, lod, vertical=False):
    """Bracket handle (aluminium, 96 mm between the posts): a flat-oval rod 11 x 6.5 mm with smooth bends,
    rosettes at the post bases; vertical means it stands along z (the door)."""
    if lod == 2:
        return
    d = 0.024

    def at(s, t):
        return (x, y - t, z + s) if vertical else (x + s, y - t, z)
    h = w / 2
    if lod == 1:
        if vertical:
            g.box(part, x - 0.005, x + 0.005, y - d - 0.003, y, z - h, z + h)
        else:
            g.box(part, x - h, x + h, y - d - 0.003, y, z - 0.005, z + 0.005)
        return
    # straight posts, the bend to the crossbar is an arc of two segments
    path = [at(-h, -0.002), at(-h, 0.013), at(-h + 0.0035, 0.0205), at(-h + 0.011, d), at(h - 0.011, d),
            at(h - 0.0035, 0.0205), at(h, 0.013), at(h, -0.002)]
    rad = (0.0055, 0.0032) if vertical else (0.0032, 0.0055)
    g.tube_var(part, path, [rad] * len(path), 6)
    for s in (-h, h):
        G.lathe(part, [(0.0078, 0.0), (0.0062, 0.0020), (0.0, 0.0030)], 8, at(s, 0.0), axis="-y")


def keyhole(br, bl, x, z):
    """Brass lock plate with a key slot."""
    G.lathe(br, [(0.0095, 0.0), (0.0082, 0.0012), (0.0, 0.0013)], 10, (x, YF, z), axis="-y")
    g.box(bl, x - 0.0011, x + 0.0011, YF - 0.0015, YF - 0.0011, z - 0.0055, z + 0.0005)
    g.cyl(bl, (x, YF - 0.0013, z + 0.0012), "y", 0.0021, 0.0004, 6)


def build_desk(spec):
    """Desktop, pedestals, plinth, facades, handles, lock plates, door with mouldings and hinges, apron,
    inventory tag."""
    lod = spec["lod"]
    parts = []
    tp = P("desk_top", "top")
    if lod == 0:
        G.slab(tp, X0, X1, Y0, Y1, ZU, ZT, rc=0.016, nc=3, re=0.009, ne=3, rb=0.003, nb=1)
    elif lod == 1:
        G.slab(tp, X0, X1, Y0, Y1, ZU, ZT, rc=0.016, nc=1, re=0.006, ne=1)
    else:
        g.box(tp, X0, X1, Y0, Y1, ZU, ZT)
    parts.append(tp)
    cc = P("carcass", "carcass")
    pl = P("plinth", "plinth")
    bev = dict(r=0.003, seg=1) if lod == 0 else {}
    for xa, xb in PED:
        g.box(cc, xa, xb, PY0, PY1, ZP, ZU, **bev)
        g.box(pl, xa + 0.02, xb - 0.02, PY0 + 0.035, PY1 - 0.02, 0.0, ZP, **(dict(r=0.002, seg=1) if lod == 0 else {}))
    # apron panel at the back
    g.box(cc, PED[0][1], PED[1][0], PY1 - 0.02, PY1, 0.24, ZU, **bev)
    # the underframe is a part of its own: otherwise its back shares an atlas projection with the back of
    # the apron
    sf = P("subframe", "carcass")
    g.box(sf, PED[0][1], PED[1][0], PY0 + 0.01, PY1 - 0.02, MID[2] - 0.012, MID[2])
    parts += [cc, sf, pl]
    fr = P("fronts", "front")
    hd = P("handles", "handle")
    fbev = dict(r=0.0035, seg=2) if lod == 0 else {}
    xa, xb = PED[1]
    for za, zb in DRAWERS_R:
        g.box(fr, xa + 0.004, xb - 0.004, YF, PY0, za, zb, **fbev)
        handle(hd, (xa + xb) / 2, YF, zb - 0.045, HANDLE_W, lod)
    xl0, xl1 = PED[0]
    g.box(fr, xl0 + 0.004, xl1 - 0.004, YF, PY0, DRAWER_L[0], DRAWER_L[1], **fbev)
    handle(hd, (xl0 + xl1) / 2, YF, DRAWER_L[1] - 0.045, HANDLE_W, lod)
    g.box(fr, MID[0], MID[1], YF, PY0, MID[2], MID[3], **fbev)
    for hx in (-0.16, 0.16):
        handle(hd, hx, YF, (MID[2] + MID[3]) / 2, HANDLE_W * 0.8, lod)
    parts += [fr, hd]
    # door: a wooden frame holding the red panel (the swappable Duty colour) in mouldings
    dr = P("door", "door")
    rd = P("door_panel", "red")
    za, zb = DOOR
    x0d, x1d = xl0 + 0.004, xl1 - 0.004
    rail = 0.055
    if lod == 0:
        rb = dict(r=0.003, seg=1)
        g.box(dr, x0d, x1d, YF, PY0, za, za + rail, **rb)
        g.box(dr, x0d, x1d, YF, PY0, zb - rail, zb, **rb)
        g.box(dr, x0d, x0d + rail, YF, PY0, za + rail - 0.002, zb - rail + 0.002, **rb)
        g.box(dr, x1d - rail, x1d, YF, PY0, za + rail - 0.002, zb - rail + 0.002, **rb)
        g.box(rd, x0d + rail, x1d - rail, YF + 0.006, PY0, za + rail, zb - rail)
        # mouldings: a half-round bead along the panel edge
        a0, a1, b0, b1 = x0d + rail + 0.003, x1d - rail - 0.003, za + rail + 0.003, zb - rail - 0.003
        for p, q in (((a0 - 0.003, b0), (a1 + 0.003, b0)), ((a0 - 0.003, b1), (a1 + 0.003, b1)),
                     ((a0, b0 - 0.003), (a0, b1 + 0.003)), ((a1, b0 - 0.003), (a1, b1 + 0.003))):
            G.rod(dr, (p[0], YF + 0.006, p[1]), (q[0], YF + 0.006, q[1]), 0.0042, 6)
    else:
        g.box(dr, x0d, x1d, YF + 0.002, PY0, za, zb)
        g.box(rd, x0d + rail, x1d - rail, YF, YF + 0.002, za + rail, zb - rail)
    parts += [dr, rd]
    handle(hd, DOOR_X, YF, 0.41, HANDLE_W, lod, vertical=True)
    if lod == 0:
        # door hinges on the left, lock plates: door, left drawer, upper right, middle
        for z in (za + 0.075, zb - 0.075):
            g.cyl(hd, (x0d - 0.0012, YF - 0.0035, z), "z", 0.0045, 0.050, 8)
            for s in (-1, 1):
                G.lathe(hd, [(0.0045, 0.0), (0.0030, 0.0025), (0.0, 0.0032)], 8, (x0d - 0.0012, YF - 0.0035, z + s * 0.025),
                        axis="z" if s > 0 else "-z")
        br = P("brass", "brass")
        bl = P("keyholes", "black")
        for x, z in ((DOOR_X, 0.335), (HX[0], DRAWER_L[1] - 0.019), (HX[1], DRAWERS_R[3][1] - 0.019),
                     (MID[1] - 0.048, (MID[2] + MID[3]) / 2)):
            keyhole(br, bl, x, z)
        parts += [br, bl]
        # empty inventory tag on two tacks
        bp = P("inv_plate", "plate")
        G.slab(bp, -0.06, 0.02, 0.62, 0.66, 0.0, 0.0012, rc=0.004, nc=2, re=0.0005, ne=1,
               frame=g.Frame((PED[0][0], 0.0, 0.0), (0, 1, 0), (0, 0, 1), (-1, 0, 0)))
        for yy in (-0.052, 0.012):
            G.lathe(bp, [(0.0022, 0.0), (0.0018, 0.0008), (0.0, 0.0010)], 6, (PED[0][0] - 0.0012, yy, 0.64), axis="-x")
        parts.append(bp)
    return parts


def build_glass_map(spec):
    """Map on the desktop and 8 mm glass with a polished edge over it (the far LOD has no glass)."""
    lod = spec["lod"]
    mp = P("map", "map")
    (cx, cy), (w, d) = L.MAP_C, L.MAP_S
    g.box(mp, cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2, ZT, L.ZM)
    parts = [mp]
    if lod == 2:
        return parts
    gx0, gx1, gy0, gy1 = L.GLASS
    gl = P("glass_top", "glass", section="glass")
    if lod == 0:
        G.slab(gl, gx0, gx1, gy0, gy1, ZT + 0.0015, ZG, rc=0.012, nc=2, re=0.0015, ne=1, rb=0.0010, nb=1)
    else:
        g.box(gl, gx0, gx1, gy0, gy1, ZT + 0.0015, ZG)
    gl.glass_frame = (g.Frame((gx0, gy0, ZT), (1, 0, 0), (0, 1, 0), (0, 0, 1)), 0.0, gx1 - gx0, 0.0, gy1 - gy0)
    parts.append(gl)
    return parts


# =============================================================================
# Folders
# =============================================================================
def tie_bow(tp, frame, a1, zt, z0, zdesk, side=0.0):
    """Folder ties as a bow at the open edge a1 (local axes of frame): the upper one comes from the cover,
    the lower one from under the sheets, the knot is outside at the edge, two loops and two tails down
    to the desk. Ribbons are 8 mm."""
    def pts(seq):
        return [tuple(frame.p(*q)) for q in seq]
    zk = (zt + z0) / 2
    kn = (a1 + 0.006, side, zk)
    up = (0, 0, 1)
    G.ribbon(tp, pts(G.spline([(a1 - 0.03, side, zt + 0.0003), (a1 - 0.004, side, zt + 0.0005),
                               (a1 + 0.004, side, zt - 0.003), kn], 2)), frame.v, 0.004, 0.0003)
    G.ribbon(tp, pts(G.spline([(a1 - 0.015, side + 0.010, z0 + L.CARD_T + 0.0003), (a1 + 0.002, side + 0.010, z0 + 0.002),
                               kn], 2)), frame.v, 0.004, 0.0003)
    # bow loops: sideways along the edge, lowered
    for s in (-1, 1):
        G.ribbon(tp, pts(G.spline([kn, (a1 + 0.010, side + s * 0.014, zk + 0.004), (a1 + 0.011, side + s * 0.026, zk - 0.002),
                                   (a1 + 0.008, side + s * 0.012, zk - 0.004), kn], 2)), up, 0.0035, 0.0003)
    # tails down to the desk: down the edge facing outwards, flat on the desk
    for s, ln in ((-1, 0.03), (1, 0.045)):
        G.ribbon(tp, pts(G.spline([kn, (a1 + 0.010, side + s * 0.006, zdesk + 0.012), (a1 + 0.016, side + s * 0.012, zdesk + 0.0004),
                                   (a1 + 0.016 + ln, side + s * 0.022, zdesk + 0.0004)], 2)), frame.v, 0.004, 0.0003)
    g.cyl(tp, tuple(frame.p(*kn)), "z", 0.0045, 0.006, 8)


def folder(parts, frame, lod, card, z0, top=False, seed=0, zdesk=None):
    """Folder in the local axes of frame (centre, a is width, b is depth): 1 mm covers with rounded corners,
    a spine on the left, an uneven pile of yellowed sheets between them; the top folder gets bow ties."""
    w, d, t, ct = L.FOLDER_W, L.FOLDER_D, L.FOLDER_T, L.CARD_T
    a0, a1, b0, b1 = -w / 2, w / 2, -d / 2, d / 2
    if lod > 0:
        g.box(parts[card], a0, a1, b0, b1, z0, z0 + t, frame=frame)
        return
    for za, zb in ((z0, z0 + ct), (z0 + t - ct, z0 + t)):
        G.slab(parts[card], a0, a1, b0, b1, za, zb, rc=0.006, nc=2 if top else 1, frame=frame)
    # spine: cardboard bent around the pile
    g.cyl(parts[card], (a0 + 0.001, 0.0, z0 + t / 2), "y", t / 2, d - 0.004, 8 if top else 6, frame=frame)
    rnd = random.Random(seed)
    zp = [z0 + ct, z0 + ct + (t - 2 * ct) * 0.45, z0 + t - ct]
    for k in range(2):
        da, db = rnd.uniform(-0.003, 0.002), rnd.uniform(-0.003, 0.003)
        g.box(parts["paper_old"], a0 + 0.004, a1 - 0.006 + da, b0 + 0.005 + db, b1 - 0.006 + db, zp[k], zp[k + 1],
              frame=frame)
    if top:
        tie_bow(parts["tape"], frame, a1, z0 + t, z0, zdesk if zdesk is not None else ZG)


def build_stacks(spec):
    """Two stacks of "Delo" folders: the lower ones are slightly rotated and shifted, the top one lies
    straight (the cover print is a decal on it)."""
    lod = spec["lod"]
    out = []
    for si, (x, y, n, seed) in enumerate(L.STACKS):
        if lod == 2:
            cd = P("stack%d_0_card" % si, "card")
            g.box(cd, x - L.FOLDER_W / 2, x + L.FOLDER_W / 2, y - L.FOLDER_D / 2, y + L.FOLDER_D / 2, ZG,
                  L.stack_top(n))
            out.append(cd)
            continue
        rnd = random.Random(seed)
        for i in range(n):
            top = i == n - 1
            deg = 0.0 if top else rnd.uniform(-4.0, 4.0)
            dx, dy = (0.0, 0.0) if top else (rnd.uniform(-0.008, 0.008), rnd.uniform(-0.008, 0.008))
            fr = rot_frame(x + dx, y + dy, 0.0, deg)
            # each folder is made of its own parts: the covers of a stack lie one above another, and in a shared
            # part they would share one top projection in the atlas (the lower cover would bake dark)
            card = ("card" if (i + seed) % 3 else "card_b") + ("" if top else "_lo")
            parts = {k: P("stack%d_%d_%s" % (si, n - 1 - i, k), k) for k in (card, "paper_old", "tape")}
            folder(parts, fr, lod, card, ZG + i * L.FOLDER_T, top, seed=seed * 10 + i)
            out += list(parts.values())
    if lod == 0:
        out.append(build_clip(L.STACKS[0][0] + 0.07, L.STACKS[0][1] + L.FOLDER_D / 2 - 0.012,
                              L.stack_top(L.STACKS[0][2]), "stack_clip"))
    return out


def build_clip(x, y, z, name, deg=90.0):
    """Paper clip (32 mm) lying flat: 0.9 mm wire, two loops with smooth bends."""
    cp = P(name, "clip")
    a = math.radians(deg)
    u, v = Vector((math.cos(a), math.sin(a), 0)), Vector((-math.sin(a), math.cos(a), 0))
    o = Vector((x, y, z + 0.0006))
    loop = [(0.0, -0.003), (0.026, -0.003), (0.030, 0.0), (0.026, 0.003), (0.004, 0.003), (0.001, 0.0),
            (0.004, -0.0015), (0.022, -0.0015)]
    g.pipe(cp, [tuple(o + u * p + v * q) for p, q in G.spline(loop, 2)], 0.00045, 4)
    return cp


def build_open(spec):
    """Open folder: the left half is the cover from inside (the inventory), the right one is a cover with
    sheets, the lower ones slightly rotated; the ties lie at the sides; a paper clip on the top sheet,
    the red-blue pencil on the inventory (the pen is a vanilla item, DECOR)."""
    lod = spec["lod"]
    (cx, cy), w, d = L.OPEN_C, L.FOLDER_W, L.FOLDER_D
    cd = P("open_card", "card")
    if lod == 2:
        g.box(cd, cx - w, cx + w, cy - d / 2, cy + d / 2, ZG, L.OPEN_ZL)
        return [cd]
    if lod == 0:
        G.slab(cd, cx - w, cx - 0.002, cy - d / 2, cy + d / 2, ZG, L.OPEN_ZL, rc=0.006, nc=2)
        G.slab(cd, cx + 0.002, cx + w, cy - d / 2, cy + d / 2, ZG, L.OPEN_ZL, rc=0.006, nc=2)
    else:
        g.box(cd, cx - w, cx - 0.002, cy - d / 2, cy + d / 2, ZG, L.OPEN_ZL)
        g.box(cd, cx + 0.002, cx + w, cy - d / 2, cy + d / 2, ZG, L.OPEN_ZL)
    g.box(cd, cx - 0.002, cx + 0.002, cy - d / 2, cy + d / 2, ZG, ZG + 0.0006)               # spine fold
    parts = [cd]
    n = 3 if lod == 0 else 1
    rnd = random.Random(5)
    for i in range(n):
        pp = P("open_sheet%d" % (n - 1 - i), "paper" if i == n - 1 else "paper_lo")
        parts.append(pp)
        z0 = L.OPEN_ZL + i * (L.OPEN_Z - L.OPEN_ZL) / n
        z1 = L.OPEN_ZL + (i + 1) * (L.OPEN_Z - L.OPEN_ZL) / n
        last = i == n - 1
        deg = 0.0 if last else rnd.uniform(-2.5, 2.5)
        fr = rot_frame(cx + w / 2 + (0.0 if last else rnd.uniform(-0.006, 0.006)), cy, 0.0, deg)
        g.box(pp, -w / 2 + 0.008, w / 2 - 0.006, -d / 2 + 0.006, d / 2 - 0.008, z0, z1, frame=fr)
    if lod == 0:
        tp = P("open_tapes", "tape")
        for pts in ([(cx - w + 0.025, cy - 0.004, ZG + 0.0012), (cx - w - 0.005, cy - 0.006, ZG + 0.0004),
                     (cx - w - 0.03, cy + 0.004, ZG + 0.0004), (cx - w - 0.05, cy - 0.002, ZG + 0.0004)],
                    [(cx + w - 0.025, cy + 0.006, ZG + 0.0012), (cx + w + 0.005, cy + 0.004, ZG + 0.0004),
                     (cx + w + 0.03, cy - 0.006, ZG + 0.0004), (cx + w + 0.06, cy + 0.002, ZG + 0.0004)]):
            G.ribbon(tp, G.spline(pts, 3), (0, 0, 1), 0.004, 0.0003)
        parts.append(tp)
        parts.append(build_clip(cx + 0.02, cy + d / 2 - 0.02, L.OPEN_Z, "open_clip", deg=0.0))
        parts += build_pencil(L.PENCIL[0], L.PENCIL[1], L.OPEN_ZL, L.PENCIL[2])
    return parts


def build_pencil(x, y, z, deg):
    """Red-blue pencil, 175 mm, hexagonal D7.5, sharpened at both ends; lies on a facet."""
    fr = rot_frame(x, y, z, deg)
    r = 0.0042
    zc = z + r * math.sin(math.radians(60))
    axis = tuple(fr.u)
    c = Vector((x, y, zc))
    red, blue, wood = P("pencil_red", "pencil_red"), P("pencil_blue", "pencil_blue"), P("pencil_wood", "pencil_wood")
    G.lathe(red, [(r, -0.0725), (r, 0.0)], 6, c, axis=axis)
    G.lathe(blue, [(r, 0.0), (r, 0.0725)], 6, c, axis=axis)
    G.lathe(wood, [(0.0013, -0.0865), (r, -0.0725)], 6, c, axis=axis)
    G.lathe(wood, [(r, 0.0725), (0.0013, 0.0865)], 6, c, axis=axis)
    G.lathe(red, [(0.0, -0.0895), (0.0013, -0.0865)], 6, c, axis=axis)
    G.lathe(blue, [(0.0013, 0.0865), (0.0, 0.0895)], 6, c, axis=axis)
    return [red, blue, wood]


# =============================================================================
# TA-57
# =============================================================================
def handset(parts, fr, lod):
    """TA-57 handset lying on the lid: the earpiece cup down, a handle with a key, the microphone cup and
    the cord socket; fr: u runs from the earpiece cup to the microphone, n is up."""
    tb = parts["black"]
    n = 16 if lod == 0 else 8
    if lod > 0:
        g.box(tb, -0.035, 0.18, -0.016, 0.016, 0.0, 0.026, frame=fr)
        return
    G.lathe(tb, [(0.031, 0.0), (0.0355, 0.004), (0.0362, 0.012), (0.034, 0.020), (0.026, 0.0255), (0.0, 0.0265)], n,
            fr.p(0.0, 0.0, 0.0))
    path = [fr.p(0.024, 0.0, 0.018), fr.p(0.07, 0.0, 0.0225), fr.p(0.115, 0.0, 0.0215), fr.p(0.150, 0.0, 0.0155)]
    pp = G.spline(path, 2)
    g.tube_var(tb, pp, [(0.0125, 0.0085)] * len(pp), 8)
    G.slab(tb, 0.068, 0.106, -0.0075, 0.0075, 0.028, 0.0335, rc=0.004, nc=2, re=0.0015, ne=1, frame=fr)    # key
    G.lathe(tb, [(0.0205, 0.0), (0.0232, 0.004), (0.0235, 0.015), (0.019, 0.0215), (0.0, 0.0228)], 14,
            fr.p(0.163, 0.0, 0.0))
    ch = parts["chrome"]
    G.lathe(ch, [(0.0078, 0.0), (0.0078, 0.010), (0.0060, 0.014), (0.0, 0.0145)], 10, fr.p(0.180, 0.0, 0.011),
            axis=tuple(fr.u))


def build_phone(spec):
    """TA-57 field telephone, closed case lying flat: bakelite case and lid with rounded corners and a seam,
    hinges at the back, latches at the front, terminals with knurled nuts on the right end; the handset
    on the lid on its cord; a field cable from the terminals behind the desk to the floor; the call lamp
    (ozl_lamp_2)."""
    lod, sd = spec["lod"], spec["sides"]
    cx, cy = L.PHONE_C
    hw, hd, h = 0.111, 0.0825, 0.079
    zs = ZG + 0.044                                          # seam between the case and the lid
    bk = P("phone", "bakelite")
    if lod == 2:
        g.box(bk, cx - hw, cx + hw, cy - hd, cy + hd, ZG, ZG + h)
        return [bk]
    # the upper half is a part of its own: otherwise its lid shares an atlas projection with the lid of the
    # lower one
    bu = P("phone_lid", "bakelite")
    if lod == 0:
        G.slab(bk, cx - hw, cx + hw, cy - hd, cy + hd, ZG, zs, rc=0.024, nc=3, re=0.0025, ne=1, rb=0.004, nb=1)
        G.slab(bu, cx - hw, cx + hw, cy - hd, cy + hd, zs + 0.0015, ZG + h, rc=0.024, nc=3, re=0.010, ne=3,
               rb=0.0025, nb=1)
    else:
        G.slab(bk, cx - hw, cx + hw, cy - hd, cy + hd, ZG, zs, rc=0.024, nc=1)
        G.slab(bu, cx - hw, cx + hw, cy - hd, cy + hd, zs + 0.0015, ZG + h, rc=0.024, nc=1, re=0.008, ne=1)
    parts = [bk, bu]
    zt = ZG + h
    # handset along the lid diagonal: earpiece cup at back right, microphone at front left (both cups rest
    # on the flat top of the lid, clear of the lamp), the cord goes into the case on the left
    hp = {"black": P("phone_handset", "black"), "chrome": P("phone_metal", "chrome")}
    ha = math.radians(30.5)
    handset(hp, g.Frame((cx + 0.064, cy + 0.036, zt), (-math.cos(ha), -math.sin(ha), 0),
                        (math.sin(ha), -math.cos(ha), 0), (0, 0, 1)), lod)
    parts += list(hp.values())
    # call lamp on the lid at front right: holder and lens
    lp = P("phone_lamp", "lamp2", group=SEL_LAMP2)
    lx, ly = cx + 0.085, cy - 0.060
    if lod == 0:
        G.lathe(hp["chrome"], [(0.0112, 0.0), (0.0112, 0.0018), (0.0098, 0.0030), (0.0078, 0.0030)], 14, (lx, ly, zt))
        G.lathe(lp, [(0.0080, 0.0028), (0.0074, 0.0055), (0.0050, 0.0080), (0.0, 0.0088)], 12, (lx, ly, zt))
    else:
        g.cyl(lp, (lx, ly, zt + 0.004), "z", 0.0085, 0.008, 6)
    parts.append(lp)
    if lod > 0:
        return parts
    ch = hp["chrome"]
    for x in (cx - 0.06, cx + 0.06):                                                         # latches at the front
        G.slab(ch, x - 0.012, x + 0.012, zs - 0.012, zs + 0.014, 0.0, 0.0035, rc=0.003, nc=1, re=0.0012, ne=1,
               frame=g.Frame((0, cy - hd, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0)))
    for x in (cx - 0.07, cx + 0.07):                                                         # hinges at the back
        g.cyl(ch, (x, cy + hd + 0.0025, zs + 0.0008), "x", 0.0040, 0.030, 8)
    # terminals on the right end: washer, knurled nut
    for y in (cy - 0.02, cy + 0.02):
        G.lathe(ch, [(0.0075, 0.0), (0.0075, 0.0012), (0.0, 0.0013)], 10, (cx + hw - 0.0005, y, ZG + 0.03), axis="x")
        G.knurl(hp["black"], (cx + hw, y, ZG + 0.03), "x", 0.0062, 0.0012, 0.012, 8, 0.0007)
    cb = P("phone_cable", "cable")
    # handset cord: from the socket over the front left corner down into the case on the left
    G.cord(cb, [(cx - 0.1035, cy - 0.0625, zt + 0.011), (cx - 0.114, cy - 0.071, zt + 0.002),
                (cx - 0.118, cy - 0.062, zt - 0.016), (cx - hw - 0.004, cy - 0.046, ZG + 0.040),
                (cx - hw + 0.002, cy - 0.040, ZG + 0.033)], 0.0028, 8)
    # P-274 field cable: two cores from the terminals join into a pair, run back over the glass and over
    # the edge to the floor
    for dy in (-0.02, 0.02):
        G.cord(cb, [(cx + hw + 0.012, cy + dy, ZG + 0.03), (cx + hw + 0.026, cy + dy * 0.5, ZG + 0.016),
                    (cx + hw + 0.034, cy + 0.02, ZG + 0.0035)], 0.0021, 6)
    G.cord(cb, [(cx + hw + 0.034, cy + 0.02, ZG + 0.0030), (cx + hw + 0.040, cy + 0.08, ZG + 0.0030),
                (0.700, Y1 - 0.08, ZG + 0.0030), (0.702, L.GLASS[3] + 0.006, ZT + 0.0030),
                (0.704, Y1 + 0.004, ZT - 0.006), (0.705, Y1 + 0.010, 0.62), (0.70, Y1 + 0.016, 0.20),
                (0.69, Y1 + 0.04, 0.025), (0.66, Y1 + 0.10, 0.003), (0.55, Y1 + 0.15, 0.003)], 0.0030, 6)
    parts.append(cb)
    return parts


# =============================================================================
# R-158
# =============================================================================
def build_radio(spec):
    """R-158 standing: rounded case 165 x 80 x 263, a battery-compartment seam with latches, a speaker grille
    in a frame facing the player, an empty nameplate; knurled knobs on top, a headset socket and a
    spring-mounted antenna; strap rings; the push-to-talk handset lies beside it on a coiled cord."""
    lod, sd = spec["lod"], spec["sides"]
    cx, cy = L.RADIO_C
    hw, hd, h = 0.0825, 0.040, 0.263
    zt = ZG + h
    rd = P("radio", "radio")
    if lod == 0:
        G.slab(rd, cx - hw, cx + hw, cy - hd, cy + hd, ZG, zt, rc=0.009, nc=2, re=0.005, ne=2, rb=0.002, nb=1)
    elif lod == 1:
        G.slab(rd, cx - hw, cx + hw, cy - hd, cy + hd, ZG, zt, rc=0.009, nc=1)
    else:
        g.box(rd, cx - hw, cx + hw, cy - hd, cy + hd, ZG, zt)
        return [rd]
    parts = [rd]
    front = g.Frame((cx, cy - hd, ZG), (1, 0, 0), (0, 0, 1), (0, -1, 0))                 # a is x, b is z, c is towards the player
    gr = P("radio_grille", "grille")
    if lod == 0:
        G.slab(gr, -0.060, 0.060, 0.115, 0.215, -0.001, 0.0012, rc=0.008, nc=2, re=0.0008, ne=1, frame=front)
    else:
        g.box(gr, cx - 0.06, cx + 0.06, cy - hd - 0.0012, cy - hd + 0.001, ZG + 0.115, ZG + 0.215)
    parts.append(gr)
    kn = P("radio_knobs", "knob")
    ch = P("radio_metal", "chrome")
    for dx, r, hh in ((-0.042, 0.0145, 0.018), (-0.004, 0.0115, 0.016), (0.026, 0.0085, 0.013)):
        if lod == 0:
            G.knurl(kn, (cx + dx, cy, zt - 0.001), "z", r, 0.0, hh - 0.003, 10, 0.0008, cap=False)
            G.lathe(kn, [(r - 0.0008, hh - 0.003), (r * 0.62, hh), (0.0, hh)], 10, (cx + dx, cy, zt - 0.001))
            g.box(ch, cx + dx - 0.0007, cx + dx + 0.0007, cy - r * 0.58, cy - r * 0.12, zt + hh - 0.0012, zt + hh - 0.0003)
        else:
            g.cyl(kn, (cx + dx, cy, zt + hh / 2), "z", r, hh, sd)
    parts.append(kn)
    # antenna socket and antenna: a spring at the base, a flexible whip, a tip
    ax, ay = cx + 0.062, cy
    if lod == 0:
        G.lathe(ch, [(0.0092, 0.0), (0.0092, 0.004), (0.0075, 0.006), (0.0075, 0.014), (0.0, 0.016)],
                10, (ax, ay, zt - 0.001))
        sp = G.coil_on([(ax, ay, zt + 0.016), (ax, ay + 0.0002, zt + 0.040)], 0.0042, 4, 5)
        g.pipe(ch, sp, 0.0011, 4)
    else:
        g.cyl(ch, (ax, ay, zt + 0.012), "z", 0.008, 0.024, 4)
    an = P("radio_antenna", "antenna")
    path = G.spline([(ax, ay, zt + 0.016), (ax + 0.004, ay + 0.008, zt + 0.15), (ax + 0.016, ay + 0.03, zt + 0.32),
                     (ax + 0.04, ay + 0.06, zt + 0.48)], 4 if lod == 0 else 1)
    g.tube_var(an, path, [(0.0026 - 0.0012 * i / (len(path) - 1),) * 2 for i in range(len(path))], 6 if lod == 0 else 3)
    if lod == 0:
        G.lathe(kn, [(0.0, -0.0035), (0.0028, -0.0025), (0.0035, 0.0), (0.0028, 0.0025), (0.0, 0.0035)], 8,
                path[-1], axis=tuple((Vector(path[-1]) - Vector(path[-2])).normalized()))
    parts += [an, ch]
    if lod > 0:
        return parts
    # headset socket with a knurled cap
    G.lathe(ch, [(0.0065, 0.0), (0.0065, 0.006), (0.0, 0.0062)], 10, (cx + 0.045, cy + 0.016, zt - 0.001))
    G.knurl(kn, (cx + 0.045, cy + 0.016, zt + 0.005), "z", 0.0075, 0.0, 0.008, 8, 0.0006)
    # battery-compartment seam (rubber band) and latches at the sides
    gs = P("radio_gasket", "gasket")
    G.slab(gs, cx - hw - 0.0008, cx + hw + 0.0008, cy - hd - 0.0008, cy + hd + 0.0008, ZG + 0.068, ZG + 0.072,
           rc=0.0098, nc=2)
    parts.append(gs)
    for s in (-1, 1):
        side = g.Frame((cx + s * hw, cy, ZG), (0, -s, 0), (0, 0, 1), (s, 0, 0))
        G.slab(ch, -0.008, 0.008, 0.052, 0.088, 0.0, 0.0035, rc=0.003, nc=1, re=0.0012, ne=1, frame=side)
        # strap ring at the top: a bracket and a half-ring
        G.slab(ch, -0.010, 0.010, h - 0.040, h - 0.026, 0.0, 0.003, rc=0.003, nc=1, frame=side)
        G.torus(ch, g.Frame((cx + s * (hw + 0.003), cy, zt - 0.033), (0, 1, 0), (s, 0, 0), (0, 0, 1)), 0.009, 0.0016, 6, 4,
                arc=(0.0, math.pi))
    # empty nameplate on two rivets under the grille
    pl = P("radio_plate", "plate")
    G.slab(pl, -0.035, 0.035, 0.084, 0.104, 0.0, 0.0008, rc=0.002, nc=1, frame=front)
    for a in (-0.031, 0.031):
        G.lathe(pl, [(0.0018, 0.0), (0.0014, 0.0007), (0.0, 0.0009)], 6, front.p(a, 0.094, 0.0007), axis="-y")
    parts.append(pl)
    # push-to-talk handset: a cast body with a key in front of the radio, a coiled cord into the socket on
    # the left side
    tg = P("radio_ptt", "black")
    tf = rot_frame(cx - 0.065, cy - 0.100, ZG, 100.0)
    G.slab(tg, -0.032, 0.032, -0.019, 0.019, 0.0, 0.024, rc=0.010, nc=2, re=0.007, ne=2, rb=0.002, nb=1, frame=tf)
    G.slab(tg, -0.012, 0.016, -0.009, 0.009, 0.023, 0.0265, rc=0.004, nc=1, re=0.0012, ne=1, frame=tf)        # key
    parts.append(tg)
    cbl = P("radio_cord", "cable")
    a = tf.p(0.031, 0.0, 0.010)
    path = G.spline([tuple(a), tuple(tf.p(0.046, 0.002, 0.007)), (cx - 0.095, cy - 0.035, ZG + 0.008),
                     (cx - 0.103, cy - 0.013, ZG + 0.016), (cx - hw - 0.012, cy - 0.002, ZG + 0.030),
                     (cx - hw - 0.002, cy, ZG + 0.034)], 3)
    g.pipe(cbl, G.coil_on(path, 0.0036, 10, 5), 0.0012, 4)
    G.lathe(ch, [(0.0055, 0.0), (0.0055, 0.008), (0.0, 0.0085)], 8, (cx - hw + 0.0005, cy, ZG + 0.034), axis="-x")
    parts.append(cbl)
    return parts


# =============================================================================
# Gooseneck lamp
# =============================================================================
def build_lamp(spec):
    """Heavy turned base with a button, a flexible chrome stem (corrugated) with sleeves, a conical shade
    with a rolled edge over the map; the shade interior and the bulb are ozl_lamp; the cord runs behind
    the desk."""
    lod, sd = spec["lod"], spec["sides"]
    bx, by = L.LAMP_BASE
    n = 20 if lod == 0 else sd
    parts = []
    bd = P("lamp_base", "lamp_body")
    if lod == 0:
        G.lathe(bd, [(0.0, 0.0005), (0.0690, 0.0005), (0.0705, 0.003), (0.0705, 0.009), (0.0660, 0.015),
                     (0.0420, 0.026), (0.0260, 0.031), (0.0225, 0.036), (0.0, 0.036)], n, (bx, by, ZG))
    else:
        G.lathe(bd, [(0.07, 0.0), (0.06, 0.02), (0.022, 0.032), (0.0, 0.032)], n, (bx, by, ZG))
    parts.append(bd)
    # stem: up, bending forward towards the middle of the desk, the end pointing down
    path = [(bx, by, ZG + 0.036), (bx, by, ZG + 0.20), (bx + 0.03, by - 0.06, ZG + 0.33),
            (bx + 0.10, by - 0.16, ZG + 0.38), (bx + 0.15, by - 0.22, ZG + 0.37), (bx + 0.17, by - 0.25, ZG + 0.345)]
    gs = P("lamp_neck", "goose")
    if lod == 0:
        # corrugation: shallow rings at a 15 mm pitch, sleeves at the ends
        pp = G.resample(G.spline(path, 6), 0.0075)
        rr = [(0.0079, 0.0079) if i % 2 else (0.0071, 0.0071) for i in range(len(pp))]
        g.tube_var(gs, pp, rr, 8)
        for p0, p1 in ((path[0], pp[2]), (path[-1], pp[-3])):
            ax = tuple((Vector(p1) - Vector(p0)).normalized())
            G.lathe(gs, [(0.0105, -0.002), (0.0105, 0.018), (0.0088, 0.022), (0.0080, 0.024)], 12, p0, axis=ax)
    else:
        g.pipe(gs, G.spline(path, 1) if lod == 1 else path[::2] + [path[-1]], 0.008, 5 if lod == 1 else 3)
    parts.append(gs)
    # shade: a cone flaring downwards, vertical axis, rolled edge
    sx, sy, sz = path[-1]
    prof = [(0.0605, -0.0855), (0.0650, -0.0860), (0.0665, -0.0835), (0.0640, -0.0790), (0.0580, -0.0700),
            (0.0400, -0.0300), (0.0220, -0.0040), (0.0200, 0.0)]
    sh = P("lamp_shade", "lamp_body")
    ns = 28 if lod == 0 else n                                # the shade is large and in plain view: rounder than the base
    G.lathe(sh, prof if lod == 0 else [(0.065, -0.085), (0.040, -0.03), (0.020, 0.0)], ns, (sx, sy, sz))
    G.lathe(sh, [(0.0215, -0.002), (0.0215, 0.012), (0.0160, 0.016), (0.0, 0.017)] if lod == 0 else
            [(0.020, 0.0), (0.020, 0.012), (0.0, 0.012)], 12 if lod == 0 else n, (sx, sy, sz))
    parts.append(sh)
    if lod == 2:
        return parts
    si = P("lamp_shade_in", "shade_in", group=SEL_LAMP)
    pin = [(0.0605, -0.0855), (0.0565, -0.0700), (0.0385, -0.0300), (0.0200, -0.0060), (0.0, -0.0050)]
    G.lathe(si, pin[::-1] if lod == 0 else [(0.0, -0.005), (0.038, -0.03), (0.063, -0.085)], ns, (sx, sy, sz))
    if lod == 0:
        # ventilation slits at the top of the shade: dark at rest, glowing when working, so a lit lamp is
        # visible from above and not only from below under the rim
        si.use("vent", *REGIONS["vent"])
        h0, h1, dr = -0.026, -0.016, (0.022 - 0.040) / 0.026
        nr, nz = 0.026 / 0.0316, 0.018 / 0.0316
        for k in range(16):
            t = 2 * math.pi * (k + 0.5) / 16
            rad = Vector((math.cos(t), math.sin(t), 0.0))
            tng = Vector((-math.sin(t), math.cos(t), 0.0))
            nrm = rad * nr + Vector((0, 0, nz))
            vs = []
            for h, s in ((h0, -1), (h0, 1), (h1, 1), (h1, -1)):
                r = 0.040 + dr * (h + 0.030)
                vs.append(si.bm.verts.new(Vector((sx, sy, sz + h)) + rad * r + tng * (s * 0.0021) + nrm * 0.0005))
            G.face(si, vs, nrm)
    parts.append(si)
    bl = P("lamp_bulb", "bulb", group=SEL_LAMP)
    bp = [(0.0, -0.077), (0.0080, -0.0755), (0.0170, -0.070), (0.0240, -0.060), (0.0272, -0.048), (0.0250, -0.034),
          (0.0160, -0.024), (0.0135, -0.014), (0.0135, -0.006)]
    G.lathe(bl, bp if lod == 0 else bp[::2], 14 if lod == 0 else 6, (sx, sy, sz))
    parts.append(bl)
    if lod == 0:
        sw = P("lamp_switch", "black")
        G.lathe(sw, [(0.0075, 0.0), (0.0075, 0.004), (0.0060, 0.0055), (0.0, 0.006)], 12,
                (bx, by - 0.050, ZG + 0.0160), axis=(0.0, -0.45, 0.89))
        parts.append(sw)
        cb = P("lamp_cord", "cable")
        G.cord(cb, [(bx + 0.010, by + 0.066, ZG + 0.006), (bx + 0.020, by + 0.085, ZG + 0.0028),
                    (bx + 0.045, L.GLASS[3] - 0.01, ZG + 0.0028), (bx + 0.050, L.GLASS[3] + 0.008, ZT + 0.0028),
                    (bx + 0.052, Y1 + 0.004, ZT - 0.006), (bx + 0.055, Y1 + 0.010, 0.55), (bx + 0.07, Y1 + 0.02, 0.15),
                    (bx + 0.10, Y1 + 0.05, 0.003), (bx + 0.20, Y1 + 0.09, 0.003)], 0.0026, 6)
        parts.append(cb)
    return parts


# =============================================================================
# Small items on the desk
# =============================================================================
def ashtray(part, cx, cy, z, n):
    """Stamped tin ashtray D100 (M17 profile, scaled x0.86): a bottom, a sloping wall, a rolled rim with
    three notches for a papirosa; the walk goes from the outside up, over the rim, inside and down to
    the bottom."""
    k = 0.86
    prof = [(0.047 * k, 0.0), (0.052 * k, 0.003), (0.056 * k, 0.016), (0.058 * k, 0.019), (0.056 * k, 0.0215),
            (0.053 * k, 0.019), (0.049 * k, 0.006), (0.042 * k, 0.003), (0.0, 0.003)]
    wgt = [0.0, 0.0, 0.7, 1.0, 1.0, 0.9, 0.0, 0.0, 0.0]
    bm = part.bm
    rings = []
    for i, (r, hh) in enumerate(prof):
        if r < 1e-7:
            rings.append(bm.verts.new((cx, cy, z + hh)))
            continue
        ring = []
        for kk in range(n):
            t = 2 * math.pi * kk / n
            dip = max(0.0, math.cos(3 * t)) ** 10
            ring.append(bm.verts.new((cx + r * math.cos(t), cy + r * math.sin(t), z + hh - 0.007 * wgt[i] * dip)))
        rings.append(ring)
    for i in range(len(prof) - 1):
        (r0, h0), (r1, h1) = prof[i], prof[i + 1]
        R0, R1 = rings[i], rings[i + 1]
        for kk in range(n):
            j = (kk + 1) % n
            tm = 2 * math.pi * (kk + 0.5) / n
            want = Vector((math.cos(tm) * (h1 - h0), math.sin(tm) * (h1 - h0), -(r1 - r0)))
            vs = [R0[kk], R0[j], R1[j], R1[kk]] if isinstance(R1, list) else [R0[kk], R0[j], R1]
            G.face(part, vs, want)
    G.face(part, rings[0], (0, 0, -1))


def papirosa(bt, ah, p, d, length, sd=6):
    """Papirosa butt: a sleeve D7.5 crushed crosswise at the mouthpiece, a short tobacco part, ash."""
    p, d = Vector(p), Vector(d).normalized()
    side = Vector((-d.y, d.x, 0.0))
    pts = [p, p + d * 0.008 + side * 0.0008, p + d * 0.016 - side * 0.0006, p + d * (length - 0.006),
           p + d * length + Vector((0, 0, -0.0008))]
    radii = [(0.0040, 0.0011), (0.0034, 0.0022), (0.0016, 0.0036), (0.0037, 0.0037), (0.0036, 0.0036)]
    g.tube_var(bt, [tuple(q) for q in pts], radii, sd)
    e = pts[-1]
    g.tube_var(ah, [tuple(e), tuple(e + d * 0.003)], [(0.0034, 0.0034), (0.0026, 0.0026)], sd)


def cig_pack(part, fr, L_=0.088, W=0.055, H=0.022):
    """Cigarette pack lying face up in frame fr (u along the pack, v across, n up): a box, each face with
    UVs onto its own piece of the vanilla texture (CIGS_UV); the top of the front picture points to +u
    (from M16/M17)."""
    bm = part.bm
    uvl = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    hl, hw = L_ / 2, W / 2
    sides = [
        ([(a, b, H) for a, b in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))], (0, 0, 1), "front",
         lambda a, b, c: ((hw - b) / W, (a + hl) / L_)),
        ([(a, b, 0.0) for a, b in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))], (0, 0, -1), "front",
         lambda a, b, c: ((b + hw) / W, (a + hl) / L_)),
        ([(a, -hw, c) for a, c in ((-hl, 0.0), (hl, 0.0), (hl, H), (-hl, H))], (0, -1, 0), "side",
         lambda a, b, c: (c / H, (a + hl) / L_)),
        ([(a, hw, c) for a, c in ((-hl, 0.0), (hl, 0.0), (hl, H), (-hl, H))], (0, 1, 0), "side",
         lambda a, b, c: (1.0 - c / H, (a + hl) / L_)),
        ([(-hl, b, c) for b, c in ((-hw, 0.0), (hw, 0.0), (hw, H), (-hw, H))], (-1, 0, 0), "end",
         lambda a, b, c: ((b + hw) / W, c / H)),
        ([(hl, b, c) for b, c in ((-hw, 0.0), (hw, 0.0), (hw, H), (-hw, H))], (1, 0, 0), "end",
         lambda a, b, c: ((hw - b) / W, c / H)),
    ]
    for corners, nrm, rect, st in sides:
        vs = [bm.verts.new(fr.p(*q)) for q in corners]
        loc = {v: q for v, q in zip(vs, corners)}
        f = G.face(part, vs, fr.u * nrm[0] + fr.v * nrm[1] + fr.n * nrm[2])
        x0, x1, y0, y1 = CIGS_UV[rect]
        for lp in f.loops:
            s, t = st(*loc[lp.vert])
            lp[uvl].uv = (x0 + (x1 - x0) * s, 1.0 - (y1 - (y1 - y0) * t))


def build_tea(spec):
    """Glass of tea in a melchior holder: a foot, a knurled band, a rolled top, a handle made of bent
    ribbon; a thin glass, tea, a spoon."""
    lod, sd = spec["lod"], spec["sides"]
    tx, ty = L.TEA_C
    parts = []
    nk = P("tea_holder", "nickel")
    if lod == 0:
        prof = [(0.0, 0.0020), (0.0300, 0.0), (0.0350, 0.0040), (0.0318, 0.0110), (0.0340, 0.0190), (0.0342, 0.0600),
                (0.0362, 0.0720), (0.0362, 0.0800), (0.0346, 0.0795), (0.0338, 0.0700)]

        def flutes(i, t):
            return 1.0 - 0.045 * (0.5 + 0.5 * math.cos(9 * t)) if i in (4, 5) else 1.0
        G.lathe(nk, prof, 18, (tx, ty, ZG), rfn=flutes)
        hpath = G.spline([(tx + 0.034, ty, ZG + 0.069), (tx + 0.052, ty, ZG + 0.073), (tx + 0.062, ty, ZG + 0.058),
                          (tx + 0.059, ty, ZG + 0.036), (tx + 0.048, ty, ZG + 0.024), (tx + 0.034, ty, ZG + 0.021)], 3)
        g.tube_var(nk, hpath, [(0.0042, 0.0018)] * len(hpath), 6)
    else:
        g.cyl(nk, (tx, ty, ZG + 0.04), "z", 0.036, 0.08, sd)
    parts.append(nk)
    if lod == 2:
        return parts
    gl = P("tea_glass", "glass", section="glass")
    if lod == 0:
        G.lathe(gl, [(0.0290, 0.004), (0.0315, 0.020), (0.0330, 0.104), (0.0334, 0.1055)], 16, (tx, ty, ZG))
        G.lathe(gl, [(0.0334, 0.1055), (0.0322, 0.1062), (0.0314, 0.104), (0.0300, 0.088)], 16, (tx, ty, ZG))
    else:
        g.cyl(gl, (tx, ty, ZG + 0.095), "z", 0.032, 0.02, 6)
    parts.append(gl)
    te = P("tea", "tea")
    g.cyl(te, (tx, ty, ZG + 0.050), "z", 0.0298 if lod == 0 else 0.03, 0.076, 16 if lod == 0 else 6)
    parts.append(te)
    if lod == 0:
        # the spoon stands in the glass resting on the rim; its bowl is under the tea
        sp = P("tea_spoon", "nickel")
        pts = G.spline([(tx + 0.012, ty - 0.008, ZG + 0.016), (tx - 0.006, ty + 0.0055, ZG + 0.060),
                        (tx - 0.024, ty + 0.019, ZG + 0.106), (tx - 0.038, ty + 0.0295, ZG + 0.142)], 2)
        rr = [(0.0022, 0.0009)] * 4 + [(0.0026, 0.0009), (0.0032, 0.0010), (0.0040, 0.0012)]
        g.tube_var(sp, pts, rr[:len(pts)], 6)
        parts.append(sp)
    return parts


def build_small(spec):
    """Ashtray with papirosa butts, cigarette pack, glass of tea, stamp and ink pad, flags on stands."""
    lod, sd = spec["lod"], spec["sides"]
    parts = []
    ax, ay = L.ASHTRAY_C
    at = P("ashtray", "ashtray")
    if lod == 0:
        ashtray(at, ax, ay, ZG, 18)                          # 18 faces: the notches at 0, 120, 240 degrees land on vertices
        ash = P("ash", "ash")
        G.lathe(ash, [(0.030, 0.0034), (0.021, 0.0050), (0.009, 0.0058), (0.0, 0.0060)], 12, (ax + 0.002, ay - 0.002, ZG))
        bt = P("butts", "butt")
        for p, d, ln in (((ax + 0.028, ay + 0.002, ZG + 0.0072), (-1.0, 0.25, 0.0), 0.034),
                         ((ax - 0.024, ay + 0.018, ZG + 0.0070), (0.8, -0.5, 0.0), 0.030),
                         ((ax + 0.004, ay - 0.030, ZG + 0.0068), (0.15, 1.0, 0.05), 0.036),
                         ((ax + 0.050, ay + 0.0, ZG + 0.0200), (-1.0, 0.0, -0.25), 0.040)):
            papirosa(bt, ash, p, d, ln)
        parts += [ash, bt]
    elif lod == 1:
        g.cyl(at, (ax, ay, ZG + 0.010), "z", 0.049, 0.02, sd)
    parts.append(at)
    if lod < 2:
        pk = P("pack", "carton", section="cigs")
        pk.fixed_uv = True
        cig_pack(pk, G.frame_z(L.PACK[0], L.PACK[1], L.PACK[2], ZG))
        parts.append(pk)
    parts += build_tea(spec)
    # stamp and ink pad in a tin
    sx, sy = L.STAMP_C
    if lod < 2:
        tn = P("stamp_pad", "tin")
        if lod == 0:
            G.slab(tn, sx - 0.06, sx + 0.02, sy - 0.03, sy + 0.03, ZG, ZG + 0.012, rc=0.007, nc=2, re=0.0018, ne=1,
                   rb=0.001, nb=1)
        else:
            g.box(tn, sx - 0.06, sx + 0.02, sy - 0.03, sy + 0.03, ZG, ZG + 0.012)
        parts.append(tn)
        wk = P("stamp", "wood_knob")
        hx, hy = sx + 0.060, sy - 0.003
        if lod == 0:
            G.slab(wk, sx + 0.035, sx + 0.085, sy - 0.018, sy + 0.012, ZG + 0.006, ZG + 0.021, rc=0.003, nc=1, re=0.002,
                   ne=1)
            G.lathe(wk, [(0.0068, 0.020), (0.0056, 0.033), (0.0064, 0.047), (0.0150, 0.066), (0.0156, 0.071),
                         (0.0120, 0.079), (0.0, 0.082)], 12, (hx, hy, ZG))
        else:
            g.box(wk, sx + 0.035, sx + 0.085, sy - 0.018, sy + 0.012, ZG + 0.006, ZG + 0.022)
            G.lathe(wk, [(0.007, 0.022), (0.014, 0.065), (0.0, 0.08)], 5, (hx, hy, ZG))
        parts.append(wk)
        rb = P("stamp_rubber", "stamp_rubber")
        g.box(rb, sx + 0.037, sx + 0.083, sy - 0.016, sy + 0.010, ZG, ZG + 0.006)
        parts.append(rb)
    if lod == 0:
        pd = P("stamp_ink", "pad")
        G.slab(pd, sx - 0.055, sx + 0.015, sy - 0.025, sy + 0.025, ZG + 0.0118, ZG + 0.0126, rc=0.004, nc=1)
        parts.append(pd)
    # flags: a lead stand, a pin with a head, a cloth pennant with a wave
    if lod < 2:
        fr = P("flags_red", "flag_red")
        fb = P("flags_blue", "flag_blue")
        pn = P("flag_pins", "pin")
        ld = P("flag_bases", "lead")
        for k, (x, y, c) in enumerate(L.FLAGS):
            fl = fr if c == "red" else fb
            if lod == 0:
                G.lathe(ld, [(0.0100, 0.0), (0.0098, 0.0028), (0.0062, 0.0066), (0.0, 0.0080)], 8, (x, y, ZG))
                G.rod(pn, (x, y, ZG + 0.007), (x, y, ZG + 0.064), 0.00085, 4)
                G.lathe(pn, [(0.0, -0.0022), (0.0021, 0.0), (0.0, 0.0022)], 5, (x, y, ZG + 0.0655))
                ph = 1.3 * k

                def wave(s, t, ph=ph):
                    return 0.0035 * math.sin(s * math.pi * 1.6 + ph) * s + 0.0006 * t
                G.cloth(fl, g.Frame((x + 0.0008, y, ZG + 0.040), (1, 0, 0), (0, 1, 0), (0, 0, 1)), 0.034, 0.022, 4, 1,
                        wave, taper=0.92)
            else:
                g.box(fl, x, x + 0.032, y - 0.001, y + 0.001, ZG + 0.040, ZG + 0.062)
                g.box(pn, x - 0.001, x + 0.001, y - 0.001, y + 0.001, ZG, ZG + 0.064)
        parts += [fr, fb, pn] + ([ld] if lod == 0 else [])
    return parts


def build_lod(spec):
    parts = build_desk(spec) + build_glass_map(spec) + build_stacks(spec) + build_open(spec)
    parts += build_phone(spec) + build_radio(spec) + build_lamp(spec) + build_small(spec)
    parts = [p for p in parts if len(p.bm.faces)]
    g.triangulate(parts)
    if spec["lod"] == 0:
        vs = [v.co for p in parts for v in p.bm.verts]
        BOUNDS["lo"] = tuple(min(v[i] for v in vs) for i in range(3))
        BOUNDS["hi"] = tuple(max(v[i] for v in vs) for i in range(3))
    return parts


def collision():
    """One convex part: the desk with the glass; props on the desk have no collision."""
    wood = kx.PEN + r"\wood.rvmat"
    body = kx.box_pts(X0, X1, Y0, Y1, 0.0, ZG)
    comps = [(body, wood)]
    memory = {
        "invView": [(0.0, -2.6, 1.5)],
        "ce_center": [(0.0, 0.0, 0.5)],
        "ce_radius": [(0.9, 0.0, 0.5)],
    }
    lo, hi = BOUNDS["lo"], BOUNDS["hi"]
    bbox = (lo[0], hi[0], lo[1], hi[1], 0.0, hi[2])
    return comps, 90.0, memory, bbox


# the first five are for the --look preview: general view, lamp from below (the shade interior is visible;
# it glows in the "working" state), desk from above (map, folders, telephone), TA-57 and R-158 close up,
# folders; the "working" state uses the first two
SHOTS = [
    ("front", (-1.3, -2.3, 1.75), (0.0, 0.0, 0.62), 32),
    ("lamp", (0.30, -0.75, 0.98), (-0.16, 0.0, 0.92), 32),
    ("map", (0.0, -0.75, 1.75), (-0.02, -0.02, ZT), 30),
    ("phone", (0.85, -0.70, 1.20), (0.55, 0.06, 0.86), 36),
    ("folders", (-0.20, -0.80, 1.22), (-0.42, -0.02, 0.82), 34),
    ("tea", (0.20, -0.45, 1.05), (0.36, 0.20, 0.82), 40),
    ("pedestal", (-0.6, -1.6, 0.75), (-0.1, 0.0, 0.38), 32),
    ("top", (0.0, -0.05, 2.4), (0.0, 0.0, ZT), 30),
    ("back", (1.3, 2.0, 1.6), (0.0, 0.0, 0.6), 32),
]

M.look_shots = (5, 2)
M.run(build_lod, collision, SHOTS, row_step=1.8, row_shot=((1.8, -6.0, 2.0), (1.8, 0, 0.6)))
