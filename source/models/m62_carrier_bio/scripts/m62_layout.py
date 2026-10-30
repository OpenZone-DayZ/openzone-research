"""M62 - dimensions shared by build_m62.py (Blender) and make_decals.py (system Python + Pillow):
a binder folder, a stack of forms, a loose form, the label on the cover, accordion-folded thermal
tape, ties. No dependencies - both import it.

Generator axes: X is the folder width (spine at -X, open edge at +X), Y is the folder height (the top
of the cover at +Y, the bottom towards the viewer, at -Y), Z is up. The origin is the centre of the
back cover on the ground.

Coordinates on paper (the vertex attribute `pp` in the generator, the images of make_decals.py), metres:
- tape: (t, -s), s is the length from the free end on the ground (the head of the printout) to the
  end of the tape inside the accordion, t = x - TAPE_X; tape image: width TAPE_W, height TAPE_LEN,
  the top of the image is the head (s = 0);
- loose form: (u, v) from the sheet centre, u to the right, v up along the sheet;
- label: world (x, y), it is not rotated, centre LABEL_C.
"""
import math

# --- folder: cardboard A4 "Delo" (catalogues BRAUBERG 110923 / 128987: 305 x 220 mm, spine 22-25 mm,
#     board 280-440 g/m2 ~ 0.3-0.6 mm; OfficeSpace 257305: 310 x 220) ------------------------------
FW, FH = 0.220, 0.305
X0, X1 = -FW / 2, FW / 2          # spine, open edge
Y0, Y1 = -FH / 2, FH / 2          # bottom, top
CB = 0.0007                       # cover board (made slightly thicker than 0.6 mm for looks)
H0 = 0.0026                       # gap at the spine: forms 1.2 mm + the binder bar

# --- A4 forms (GOST 9327: 210 x 297), 8 sheets on the binder --------------------------------------
SW, SH = 0.210, 0.297
FORM_X0 = X0 + 0.004              # towards the spine
FORM_T = 0.0010                   # stack (visual thickness)
FORM_Z0 = CB
FORM_Z1 = CB + FORM_T
# binder: holes per ISO 838 (80 mm), 12 mm from the sheet edge; the clamping bar is 110 x 13 mm
# (estimated), under the cover and visible as relief
HOLE_X = FORM_X0 + 0.012
HOLE_Y = 0.040
BAR_W, BAR_L = 0.013, 0.110

# loose form (not bound): shifted towards the viewer and rotated, it peeks out from under the bottom by 20-30 mm
LOOSE_C = (0.0005, -0.0290)
LOOSE_ROT = -3.0                  # degrees, counter-clockwise
LOOSE_T = 0.0002
LOOSE_Z0 = FORM_Z1
LOOSE_Z1 = FORM_Z1 + LOOSE_T
LOOSE_STRIP = 0.034               # bottom strip of the sheet (the visible part): its own atlas region


def loose_point(u, v):
    """Point of the loose form (u, v from the sheet centre) as world x, y."""
    a = math.radians(LOOSE_ROT)
    return (LOOSE_C[0] + u * math.cos(a) - v * math.sin(a), LOOSE_C[1] + u * math.sin(a) + v * math.cos(a))


# --- label on the cover: a paper tag 90 x 60 mm (instead of the printed "DELO") -------------------
LABEL_X = (-0.085, 0.005)
LABEL_Y = (0.040, 0.100)
LABEL_C = ((LABEL_X[0] + LABEL_X[1]) / 2, (LABEL_Y[0] + LABEL_Y[1]) / 2)
LABEL_S = (LABEL_X[1] - LABEL_X[0], LABEL_Y[1] - LABEL_Y[0])

# --- thermal tape: standard 57 mm till / instrument tape (analyser thermal printers, e.g. MPRINT G58
#     in the Laktan 1-4M), folded accordion-style at ~105 mm, 7 layers -----------------------------
TAPE_W = 0.057
TAPE_X = 0.042                    # centre of the tape
TAPE_X0, TAPE_X1 = TAPE_X - TAPE_W / 2, TAPE_X + TAPE_W / 2
TAPE_TH = 0.0002                  # sheet (visual; the real one is 0.06 mm)
PITCH = 0.105
PROT = 0.035                      # the accordion sticks out past the top of the cover
Y_OUT = Y1 + PROT
Y_IN = Y_OUT - PITCH
N_LAYERS = 7                      # odd: the bottom and top layers go inwards, the end of the tape is inside
Z_BASE = LOOSE_Z1                 # the accordion lies on the forms
G_IN, G_E, G_O = 0.00045, 0.00055, 0.0016    # layer pitch: inside, at the cover edge, outside (fanned out)
Z_O0 = 0.0012                     # outside, the bottom layer sags to the ground


def z_layer(k, where):
    """Centre line of layer k (0 is the bottom) inside (in), at the cover edge (edge), outside (out)."""
    if where == "in":
        return Z_BASE + TAPE_TH / 2 + k * G_IN
    if where == "edge":
        return Z_BASE + TAPE_TH / 2 + k * G_E
    return Z_O0 + k * G_O


def stack_top(y):
    """Top of the accordion under the cover (y from Y_IN to Y1): the lower boundary of the cover above it."""
    f = min(max((y - Y_IN) / (Y1 - Y_IN), 0.0), 1.0)
    top = N_LAYERS - 1
    return (1 - f) * z_layer(top, "in") + f * z_layer(top, "edge") + TAPE_TH / 2


# the free end (the head of the printout) comes out from under the bottom layer and lies on the ground:
# (y from Y_OUT, z), from the end towards the accordion
TAIL = [(0.050, 0.0009), (0.043, 0.00026), (0.030, 0.00024), (0.018, 0.00030), (0.009, 0.0006), (0.003, 0.0010)]


def tape_path(layers=None, turn_in=1, turn_out=2, tail=TAIL, labels=False):
    """Centre line of the tape in the (y, z) plane from the free end on the ground (s = 0, the head of the
    printout): the tail, the bottom layer inwards, a fold, the next one outwards... the top layer inwards,
    the end of the tape is under the cover. layers are layer indices (all by default; the simplified LOD
    takes every second one, with the same heights). labels is [(y, z, layer)]: the tail belongs to the
    bottom layer, a fold to the layer before it."""
    layers = list(range(N_LAYERS)) if layers is None else layers
    pts = [(Y_OUT + dy, z) for dy, z in tail]
    lab = [layers[0]] * len(pts)
    for i, k in enumerate(layers):
        inward = i % 2 == 0
        row = [(Y_OUT, z_layer(k, "out")), (Y1, z_layer(k, "edge")), (Y_IN, z_layer(k, "in"))]
        pts += row if inward else row[::-1]
        lab += [k] * 3
        if i == len(layers) - 1:
            break
        k2 = layers[i + 1]
        if inward:                                          # inside: a half-circle around -y
            za, zb, n, y0, sgn = z_layer(k, "in"), z_layer(k2, "in"), turn_in, Y_IN, -1
        else:                                               # outside: around +y
            za, zb, n, y0, sgn = z_layer(k, "out"), z_layer(k2, "out"), turn_out, Y_OUT, 1
        zc, r = (za + zb) / 2, (zb - za) / 2
        for j in range(1, n + 1):
            ang = -math.pi / 2 + math.pi * j / (n + 1)
            pts.append((y0 + sgn * r * math.cos(ang), zc + r * math.sin(ang)))
            lab.append(k)
    return [(y, z, k) for (y, z), k in zip(pts, lab)] if labels else pts


def path_len(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


TAPE_LEN = path_len(tape_path())

# --- ties: 8 mm cotton tape, a bow at the middle of the open edge ---------------------------------
TIE_W, TIE_TH = 0.008, 0.0005
Y_BOW = -0.020
