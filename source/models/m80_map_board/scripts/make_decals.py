"""Pictures for the M80 map board module (system Python + Pillow), no letters: digits, scales, map
symbols, grease-pencil marks, a hand-drawn radiation sign.

    python make_decals.py      -> ../work/*.png

- map.png / map_gloss.png - a sheet of a 1 : 50 000 topographic map under celluloid (194 x 195 mm,
  coordinates - m80_layout.MAP): forest, contour lines (every fifth thicker), a two-line river, a
  stream, a pond, a marsh, a highway, dirt roads, a railway, a power line, a village with a bridge,
  spot heights in digits, a kilometre grid every 20 mm, at the bottom the sheet frame with a minute
  scale and grid digits; the sheet is folded in four. On top, what is on the celluloid: a route in
  red grease pencil with arrows and points 1-5, hatched anomaly circles, a radiation sign in a
  circle, a blue zone border with teeth, a rubbed-out old route; the celluloid has yellowed, with
  scratches and cloudy patches. map_gloss is the celluloid gloss (L): the grease pencil and the
  scratches are matte.
- ruler_ca.png - an officer's ruler 200 x 100 (glass section, RGBA): green transparent plastic,
  stencils as transparent cut-outs (digits, circles, squares, triangles, rhombi, flags, ovals),
  coordinate-measurer windows with scales, a protractor, millimetre scales, a toothed edge. The top
  of the image is the top of the ruler (under the clamp bar and past the board edge).
- curv_top.png - the face of the KU-A curvimeter (RGBA, 44 x 66 mm, up is toward the handle): a
  white 0-100 dial, a needle, three screws; transparent outside the parts.
- comp_top.png - the Adrianov compass from above (RGBA, 48 x 48 mm, up is up the board): a black
  limb with luminous marks and the digits 0, 15, 30, 45 (thousandths), a needle with a luminous tip,
  on the sighting ring ticks every 3 degrees and a luminous pointer by the front sight.
- tag.png - an aluminium inventory tag on the lip, 28 x 11 mm: punched digits, two nails.

Digits are drawn with own strokes (as in M62, M65, M68): the images do not depend on system fonts.
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m80_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))


def save(img, name):
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, img.size, img.mode)


# --- digits (from M62/M65/M68): strokes in a 0.6 x 1 cell, y down ---------------------------------
HAND = {
    "0": [[(0.30, 0.0), (0.08, 0.15), (0.0, 0.5), (0.08, 0.86), (0.30, 1.0), (0.52, 0.86), (0.60, 0.5),
           (0.52, 0.14), (0.28, 0.0)]],
    "1": [[(0.12, 0.25), (0.40, 0.0), (0.38, 1.0)]],
    "2": [[(0.04, 0.24), (0.20, 0.02), (0.44, 0.02), (0.58, 0.22), (0.50, 0.46), (0.04, 1.0), (0.62, 0.98)]],
    "3": [[(0.04, 0.10), (0.30, 0.0), (0.52, 0.12), (0.50, 0.34), (0.24, 0.48), (0.54, 0.62), (0.56, 0.86),
           (0.30, 1.0), (0.02, 0.90)]],
    "4": [[(0.46, 1.0), (0.44, 0.0), (0.0, 0.68), (0.62, 0.66)]],
    "5": [[(0.56, 0.0), (0.12, 0.02), (0.06, 0.46), (0.34, 0.40), (0.58, 0.60), (0.54, 0.88), (0.28, 1.0),
           (0.02, 0.90)]],
    "6": [[(0.50, 0.04), (0.24, 0.16), (0.05, 0.55), (0.10, 0.90), (0.30, 1.0), (0.52, 0.88), (0.55, 0.66),
           (0.34, 0.52), (0.08, 0.62)]],
    "7": [[(0.0, 0.02), (0.60, 0.0), (0.24, 1.0)]],
    "8": [[(0.30, 0.48), (0.08, 0.32), (0.12, 0.08), (0.30, 0.0), (0.50, 0.08), (0.52, 0.30), (0.30, 0.48),
           (0.05, 0.70), (0.10, 0.95), (0.30, 1.0), (0.52, 0.92), (0.56, 0.70), (0.30, 0.48)]],
    "9": [[(0.55, 0.40), (0.34, 0.50), (0.10, 0.42), (0.05, 0.20), (0.25, 0.0), (0.50, 0.05), (0.55, 0.40),
           (0.48, 1.0)]],
    ".": [[(0.24, 0.94), (0.30, 1.0)]],
}


def adv(ch, h):
    return h * 0.5 if ch == " " else h * (0.32 if ch == "." else 0.78)


def text_w(text, h):
    return sum(adv(ch, h) for ch in text)


def digits(d, text, x, y, h, width, rnd=None, slant=0.0, jitter=0.03, fill=255):
    """Digits: a string from the lower left corner (x, y), height h (px). rnd=None means even (print)."""
    cx = x
    for ch in text:
        if ch == " ":
            cx += h * 0.5
            continue
        hh = h * (rnd.uniform(0.9, 1.08) if rnd else 1.0)
        dy = rnd.uniform(-0.06, 0.06) * h if rnd else 0.0
        for stroke in HAND[ch]:
            pts = []
            for px, py in stroke:
                jx, jy = (rnd.uniform(-jitter, jitter), rnd.uniform(-jitter, jitter)) if rnd else (0, 0)
                pts.append((cx + (px + jx) * hh + (1 - py) * slant * hh, y - hh + (py + jy) * hh + dy))
            d.line(pts, fill=fill, width=width, joint="curve")
        cx += adv(ch, hh) * (rnd.uniform(0.92, 1.08) if rnd else 1.0)
    return cx


def digits_c(d, text, cx, cy, h, width, **kw):
    """Digits centred at (cx, cy)."""
    return digits(d, text, cx - text_w(text, h) / 2 + h * 0.08, cy + h / 2, h, width, **kw)


def catmull(pts, sub=6):
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(0, i - 1)], pts[i], pts[i + 1]
        p3 = pts[min(len(pts) - 1, i + 2)]
        for s in range(sub):
            t = s / sub
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                                    + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in range(2)))
    out.append(pts[-1])
    return out


def resample(pts, step):
    """Polyline -> points at an equal step (for dashes and arrows)."""
    out, cum = [pts[0]], 0.0
    for a, b in zip(pts, pts[1:]):
        seg = math.dist(a, b)
        while cum + seg >= step and seg > 1e-9:
            t = (step - cum) / seg
            a = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            out.append(a)
            seg = math.dist(a, b)
            cum = 0.0
        cum += seg
    return out


def smooth_field(w, h, cells, seed, octaves=((1.0, 1), (0.45, 2), (0.2, 4)), blur=6):
    rnd = random.Random(seed)
    acc, acc_w = None, 0.0
    for a, f in octaves:
        cw, ch = cells[0] * f, cells[1] * f
        small = Image.new("L", (cw, ch))
        small.putdata([rnd.randint(0, 255) for _ in range(cw * ch)])
        big = small.resize((w, h), Image.BICUBIC)
        acc = big if acc is None else Image.blend(acc, big, a / (acc_w + a))
        acc_w += a
    return acc.filter(ImageFilter.GaussianBlur(blur))


def paint(img, col, mask, k=1.0):
    if k != 1.0:
        mask = mask.point(lambda v: int(v * k))
    img.paste(Image.new("RGB", img.size, col), (0, 0), mask)


# =============================================================================
# Map
# =============================================================================
MAP_K = 6.0                                   # px/mm

PAPER = (236, 231, 211)
FOREST = (198, 222, 166)
FOREST_EDGE = (128, 168, 108)
CONTOUR = (176, 114, 62)
WATER = (172, 206, 230)
WATER_LINE = (58, 112, 182)
BLACK = (34, 34, 36)
ROAD = (234, 148, 62)
BUILT = (238, 196, 128)
WAX_RED = (196, 38, 34)
WAX_BLUE = (36, 70, 168)
WAX_BLACK = (30, 28, 30)


def wax(mask, rnd_seed, k):
    """Grease pencil: the wax lays down unevenly - fine grain and gaps in the stroke."""
    w, h = mask.size
    grain = Image.effect_noise((w, h), 70).point(lambda v: max(0, min(255, int((v - 50) * 2.2))))
    grain = grain.filter(ImageFilter.GaussianBlur(0.4))
    return ImageChops.multiply(mask.filter(ImageFilter.GaussianBlur(0.35 * k / 4)), grain)


def make_map():
    k = MAP_K
    wmm, hmm = L.MAP_W_MM, L.MAP_H_MM
    W, H = int(round(wmm * k)), int(round(hmm * k))
    rnd = random.Random(8001)

    def P(x, y):
        return x * k, y * k

    def lw(mm):
        return max(1, int(round(mm * k)))

    img = Image.new("RGB", (W, H), PAPER)
    tone = smooth_field(W, H, (6, 6), 80011, blur=10)
    paint(img, (226, 219, 194), tone.point(lambda v: max(0, min(255, (v - 110) * 2))), 0.6)
    FRAME_Y = 183.5                                             # inner frame of the sheet (at the bottom)

    # --- forest: field patches, clearings are rare windows ---
    forest = smooth_field(W, H, (5, 5), 80012).point(lambda v: 255 if v > 128 else 0)
    forest = forest.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 128 else 0)
    paint(img, FOREST, forest)
    edge = forest.filter(ImageFilter.FIND_EDGES).point(lambda v: 170 if v > 40 else 0)
    paint(img, FOREST_EDGE, edge)
    # forest symbols (a circle-tree) in a sparse grid
    marks = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(marks)
    fpx = forest.load()
    for gy in range(4, int(FRAME_Y), 9):
        for gx in range(4, int(wmm), 9):
            x, y = gx + rnd.uniform(-1.5, 1.5), gy + rnd.uniform(-1.5, 1.5)
            if fpx[min(W - 1, int(x * k)), min(H - 1, int(y * k))] > 0 and rnd.random() < 0.55:
                md.ellipse([P(x - 0.45, y - 0.45), P(x + 0.45, y + 0.45)], outline=255, width=lw(0.12))
                md.line([P(x, y + 0.45), P(x, y + 1.1)], fill=255, width=lw(0.12))
    paint(img, (60, 110, 60), marks, 0.8)

    # --- relief: a hill at the upper right, the river valley along the diagonal ---
    hf = smooth_field(W, H, (4, 4), 80013, octaves=((1.0, 1), (0.35, 2)), blur=18)
    hill = Image.new("L", (W, H), 0)
    ImageDraw.Draw(hill).ellipse([P(118, 18), P(176, 62)], fill=150)
    ImageDraw.Draw(hill).ellipse([P(20, 120), P(60, 150)], fill=90)
    hf = ImageChops.add(hf.point(lambda v: int(v * 0.75)), hill.filter(ImageFilter.GaussianBlur(14 * k)))
    # height steps are cleaned with a mode filter: otherwise 8-bit noise gives "hairy" contour lines
    q = hf.point(lambda v: (v // 8) * 8).filter(ImageFilter.ModeFilter(9))
    q = q.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 0 else 0)
    qi = hf.point(lambda v: (v // 40) * 40).filter(ImageFilter.ModeFilter(9))
    qi = qi.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 0 else 0)
    qi = qi.filter(ImageFilter.MaxFilter(3))
    cont = ImageChops.lighter(q.point(lambda v: v * 160 // 255), qi.point(lambda v: v * 225 // 255))
    paint(img, CONTOUR, cont.filter(ImageFilter.GaussianBlur(0.35)))
    # hachures on the hilltop
    bd = ImageDraw.Draw(img)
    for i in range(10):
        a = i * 2 * math.pi / 10 + 0.2
        cx, cy = 147 + 22 * math.cos(a) * 0.62, 40 + 15 * math.sin(a) * 0.62
        bd.line([P(cx, cy), P(cx + 1.4 * math.cos(a), cy + 1.4 * math.sin(a))], fill=CONTOUR, width=lw(0.18))

    d = ImageDraw.Draw(img)
    # --- marsh: blue strokes over the lowland on the left ---
    marsh = Image.new("L", (W, H), 0)
    mk = ImageDraw.Draw(marsh)
    for y in range(92, 128, 3):
        for x in range(4, 46, 5):
            xx, yy = x + rnd.uniform(-1, 1) + (y % 2) * 2.0, y + rnd.uniform(-0.4, 0.4)
            if (xx - 24) ** 2 / 22 ** 2 + (yy - 110) ** 2 / 17 ** 2 < 1.0:
                mk.line([P(xx, yy), P(xx + rnd.uniform(2.0, 3.2), yy)], fill=255, width=lw(0.22))
    paint(img, WATER_LINE, marsh.filter(ImageFilter.GaussianBlur(0.4)))

    # --- river in two lines with a fill, a stream, a pond ---
    river = catmull([(-4, 18), (22, 30), (44, 52), (52, 80), (78, 96), (104, 108), (126, 130), (150, 150),
                     (170, 176), (200, 190)], sub=10)
    d.line([P(*p) for p in river], fill=WATER_LINE, width=lw(2.1), joint="curve")
    d.line([P(*p) for p in river], fill=WATER, width=lw(1.5), joint="curve")
    stream = catmull([(110, -4), (100, 14), (106, 30), (92, 46), (96, 62), (84, 74), (80, 95)], sub=10)
    d.line([P(*p) for p in stream], fill=WATER_LINE, width=lw(0.35), joint="curve")
    pond = [(32 + 9 * math.cos(a) + rnd.uniform(-1.2, 1.2), 160 + 5.5 * math.sin(a) + rnd.uniform(-1.0, 1.0))
            for a in [i * 2 * math.pi / 16 for i in range(16)]]
    d.polygon([P(*p) for p in pond], fill=WATER, outline=WATER_LINE)

    # --- roads: highway (orange in a black outline), dirt roads, a dotted track ---
    road = catmull([(-4, 62), (30, 70), (62, 82), (92, 100), (112, 120), (128, 150), (136, 186)], sub=10)
    d.line([P(*p) for p in road], fill=BLACK, width=lw(1.6), joint="curve")
    d.line([P(*p) for p in road], fill=ROAD, width=lw(1.0), joint="curve")
    for pts in ([(62, 82), (70, 60), (66, 34), (74, 6), (80, -4)],
                [(128, 150), (150, 136), (176, 132), (200, 120)]):
        d.line([P(*p) for p in catmull(pts, sub=10)], fill=BLACK, width=lw(0.35), joint="curve")
    track = resample(catmull([(4, 150), (20, 140), (46, 132), (72, 138), (96, 150), (116, 172)], sub=12), 0.4)
    for i in range(0, len(track) - 4, 7):
        d.line([P(*track[i]), P(*track[i + 4])], fill=BLACK, width=lw(0.25))

    # --- railway: a black-and-white strip across the top of the sheet ---
    rail = catmull([(-4, 8), (60, 14), (120, 6), (200, 2)], sub=14)
    d.line([P(*p) for p in rail], fill=BLACK, width=lw(1.0), joint="curve")
    rp = resample(rail, 0.25)
    for i in range(0, len(rp) - 10, 20):
        d.line([P(*rp[i]), P(*rp[i + 10])], fill=(250, 250, 248), width=lw(0.55))

    # --- power line: a line with pylon dots ---
    lep = resample([(150, -4), (162, 60), (172, 120), (182, 186)], 0.5)
    d.line([P(*p) for p in [lep[0], lep[-1]]], fill=BLACK, width=lw(0.15))
    for p in lep[::16]:
        d.ellipse([P(p[0] - 0.45, p[1] - 0.45), P(p[0] + 0.45, p[1] + 0.45)], fill=BLACK)

    # --- village by the bridge: built-up blocks and houses ---
    for poly in ([(98, 92), (110, 98), (106, 108), (94, 101)], [(114, 112), (124, 108), (130, 120), (118, 125)]):
        d.polygon([P(*p) for p in poly], fill=BUILT, outline=BLACK)
    for _ in range(22):
        x, y = rnd.uniform(84, 138), rnd.uniform(84, 132)
        if math.dist((x, y), (112, 120)) < 26:
            s = rnd.uniform(1.0, 1.8)
            d.rectangle([P(x, y), P(x + s, y + s * 0.8)], fill=BLACK)
    # bridge: two brackets across the river
    for sgn in (-1, 1):
        d.line([P(106, 113 + sgn * 1.8), P(110, 111 + sgn * 1.8)], fill=BLACK, width=lw(0.3))

    # --- kilometre grid: 1 km = 20 mm ---
    grid = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(grid)
    for i in range(10):
        x = 9.0 + i * 20.0
        gd.line([P(x, 0), P(x, FRAME_Y)], fill=255, width=lw(0.13))
    for i in range(10):
        y = 3.0 + i * 20.0
        if y < FRAME_Y:
            gd.line([P(0, y), P(wmm, y)], fill=255, width=lw(0.13))
    paint(img, BLACK, grid, 0.85)

    # --- spot heights ---
    hd = Image.new("L", (W, H), 0)
    hdd = ImageDraw.Draw(hd)
    for x, y, t in ((147, 40, "214.6"), (40, 135, "187.2"), (16, 46, "166.9"), (176, 96, "201.3"),
                    (70, 172, "171.0"), (122, 66, "196.4")):
        hdd.ellipse([P(x - 0.45, y - 0.45), P(x + 0.45, y + 0.45)], fill=255)
        digits(hdd, t, *P(x + 0.9, y + 0.9), 1.7 * k, lw(0.17))
    # triangulation point on the hill
    hdd.polygon([P(147, 37.6), P(145.6, 40.0), P(148.4, 40.0)], outline=255, width=lw(0.18))
    paint(img, BLACK, hd)

    # --- sheet frame at the bottom: inner line, minute scale, outer frame, grid digits ---
    d.rectangle([P(-1, FRAME_Y), P(wmm + 1, hmm + 1)], fill=(244, 241, 228))
    d.line([P(0, FRAME_Y), P(wmm, FRAME_Y)], fill=BLACK, width=lw(0.12))
    for i in range(-1, 10):
        x0 = 4.0 + i * 23.3
        if i % 2 == 0:
            d.rectangle([P(x0, FRAME_Y + 0.6), P(x0 + 23.3, FRAME_Y + 1.6)], fill=BLACK)
        for j in range(1, 6):
            xt = x0 + j * 23.3 / 6
            d.line([P(xt, FRAME_Y + 0.6), P(xt, FRAME_Y + 1.6)], fill=BLACK, width=lw(0.1))
    d.rectangle([P(-1, FRAME_Y + 0.6), P(wmm + 1, FRAME_Y + 1.6)], outline=BLACK, width=lw(0.1))
    d.line([P(0, FRAME_Y + 2.6), P(wmm, FRAME_Y + 2.6)], fill=BLACK, width=lw(0.55))
    gm = Image.new("L", (W, H), 0)
    gmd = ImageDraw.Draw(gm)
    for i in range(10):
        x = 9.0 + i * 20.0
        gmd.line([P(x, FRAME_Y + 2.6), P(x, FRAME_Y + 3.8)], fill=255, width=lw(0.13))
        if 4 < x < wmm - 4:
            digits_c(gmd, "%02d" % (12 + i), *P(x, FRAME_Y + 6.2), 2.2 * k, lw(0.22))
    paint(img, BLACK, gm)

    # --- the sheet was folded in four: creases ---
    for vertical, pos in ((True, 101.0), (False, 96.0)):
        for off, col, a in ((-0.35, (255, 255, 250), 80), (0.35, (120, 112, 96), 60)):
            m = Image.new("L", (W, H), 0)
            md2 = ImageDraw.Draw(m)
            if vertical:
                md2.line([P(pos + off, 0), P(pos + off + 0.8, hmm)], fill=a, width=lw(0.5))
            else:
                md2.line([P(0, pos + off), P(wmm, pos + off - 0.6)], fill=a, width=lw(0.5))
            paint(img, col, m.filter(ImageFilter.GaussianBlur(0.4 * k)))
    # wear at the crossing of the creases
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([P(96, 91), P(106, 101)], fill=80)
    paint(img, (250, 248, 240), m.filter(ImageFilter.GaussianBlur(2 * k)))

    # =========================================================================
    # Celluloid: grease-pencil marks, rubbed-out old ones, scratches, yellowing
    # =========================================================================
    gloss = Image.new("L", (W, H), 214)
    # rubbed-out old route: a pink haze
    old = Image.new("L", (W, H), 0)
    od = ImageDraw.Draw(old)
    od.line([P(*p) for p in catmull([(22, 150), (34, 124), (58, 104), (64, 80), (84, 60)])], fill=255,
            width=lw(1.6), joint="curve")
    od.ellipse([P(54, 52), P(70, 66)], outline=255, width=lw(1.2))
    old = old.filter(ImageFilter.GaussianBlur(1.6 * k))
    paint(img, (214, 150, 140), old, 0.35)
    gloss.paste(150, (0, 0), old.point(lambda v: v // 2))

    red = Image.new("L", (W, H), 0)
    rd = ImageDraw.Draw(red)
    route = catmull([(116, 182), (106, 162), (86, 140), (72, 114), (84, 92), (98, 72), (122, 52), (146, 36),
                     (168, 30)], sub=12)
    rd.line([P(*p) for p in route], fill=255, width=lw(1.1), joint="curve")
    # direction arrows along the route
    rp = resample(route, 0.5)
    for i in range(28, len(rp) - 6, 44):
        (x0, y0), (x1, y1) = rp[i - 4], rp[i]
        ang = math.atan2(y1 - y0, x1 - x0)
        for s in (-1, 1):
            a = ang + math.pi + s * 0.5
            rd.line([P(x1, y1), P(x1 + 3.2 * math.cos(a), y1 + 3.2 * math.sin(a))], fill=255, width=lw(0.9))
    # points 1-5 in circles (digits beside them)
    for n, (x, y, dx, dy) in enumerate(((86, 140, -9, 2), (72, 114, -9, 3), (98, 72, 4, 4), (146, 36, -2, -5),
                                        (168, 30, 3, 5)), 1):
        rd.ellipse([P(x - 2.4, y - 2.4), P(x + 2.4, y + 2.4)], outline=255, width=lw(0.8))
        digits(rd, str(n), *P(x + dx, y + dy), 4.2 * k, lw(0.75), rnd=rnd, slant=0.18, jitter=0.04)
    # start - a triangle, end - a cross
    rd.polygon([P(116, 178.5), P(112.6, 184.6), P(119.4, 184.6)], outline=255, width=lw(0.8))
    # anomalies: hatched circles
    for cx, cy, r in ((40, 112, 10.0), (116, 92, 6.5), (60, 46, 7.5)):
        rd.ellipse([P(cx - r, cy - r), P(cx + r, cy + r)], outline=255, width=lw(0.9))
        s2 = math.sqrt(0.5)
        t = -r + 1.2
        while t < r - 0.8:                                  # diagonal strokes within the circle
            c = math.sqrt(max(0.0, r * r - t * t)) * 0.9
            x0, y0 = cx + t * s2, cy - t * s2
            rd.line([P(x0 - c * s2, y0 - c * s2), P(x0 + c * s2, y0 + c * s2)], fill=255, width=lw(0.5))
            t += 1.9
    # hand-drawn radiation sign in a circle
    cx, cy, r = 172, 104, 8.5
    rd.ellipse([P(cx - r, cy - r), P(cx + r, cy + r)], outline=255, width=lw(0.9))
    rd.ellipse([P(cx - 1.1, cy - 1.1), P(cx + 1.1, cy + 1.1)], fill=255)
    for i in range(3):
        a0 = math.radians(-90 + i * 120 - 30 + rnd.uniform(-4, 4))
        a1 = a0 + math.radians(60)
        pts = [P(cx + 1.8 * math.cos(a0), cy + 1.8 * math.sin(a0))]
        pts += [P(cx + 6.4 * math.cos(a0 + (a1 - a0) * t / 8), cy + 6.4 * math.sin(a0 + (a1 - a0) * t / 8)) for t in range(9)]
        pts += [P(cx + 1.8 * math.cos(a1), cy + 1.8 * math.sin(a1))]
        rd.polygon(pts, fill=255)
    red = wax(red, 8002, k)
    paint(img, WAX_RED, red)
    gloss.paste(96, (0, 0), red.point(lambda v: 255 if v > 60 else v * 4))

    blue = Image.new("L", (W, H), 0)
    bdw = ImageDraw.Draw(blue)
    zone = catmull([(6, 82), (24, 70), (34, 52), (32, 30), (46, 16), (72, 22), (88, 18)], sub=12)
    bdw.line([P(*p) for p in zone], fill=255, width=lw(1.0), joint="curve")
    zp = resample(zone, 0.5)
    for i in range(3, len(zp) - 3, 10):
        (x0, y0), (x1, y1) = zp[i - 2], zp[i + 2]
        ang = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
        x, y = zp[i]
        bdw.line([P(x, y), P(x + 2.4 * math.cos(ang), y + 2.4 * math.sin(ang))], fill=255, width=lw(0.8))
    # blue detour arrow by the highway
    arr = catmull([(150, 176), (156, 160), (166, 150), (178, 146)], sub=10)
    bdw.line([P(*p) for p in arr], fill=255, width=lw(0.9), joint="curve")
    bdw.polygon([P(178.6, 146), P(173, 142.2), P(174.2, 149.6)], fill=255)
    blue = wax(blue, 8003, k)
    paint(img, WAX_BLUE, blue)
    gloss.paste(96, (0, 0), blue.point(lambda v: 255 if v > 60 else v * 4))

    # black cross at the end of the route
    blk = Image.new("L", (W, H), 0)
    bk = ImageDraw.Draw(blk)
    for s in (-1, 1):
        bk.line([P(164, 26 + s * 0), P(172, 34)] if s < 0 else [P(172, 26), P(164, 34)], fill=255, width=lw(1.1))
    blk = wax(blk, 8004, k)
    paint(img, WAX_BLACK, blk)
    gloss.paste(96, (0, 0), blk.point(lambda v: 255 if v > 60 else v * 4))

    # yellowing of the celluloid: an even tone, thicker toward the edges
    yel = Image.new("L", (W, H), 46)
    ye = ImageDraw.Draw(yel)
    for i in range(int(8 * k)):
        ye.rectangle([i, i, W - 1 - i, H - 1 - i], outline=int(46 + 70 * (1 - i / (8 * k)) ** 2))
    img = Image.composite(ImageChops.multiply(img, Image.new("RGB", (W, H), (244, 226, 170))), img, yel)
    # cloudy patches (wiped with a sleeve) and scratches
    haze = Image.new("L", (W, H), 0)
    hz = ImageDraw.Draw(haze)
    for _ in range(16):
        x, y, r = rnd.uniform(0, wmm), rnd.uniform(0, hmm), rnd.uniform(10, 30)
        hz.ellipse([P(x - r, y - r * 0.6), P(x + r, y + r * 0.6)], fill=rnd.randint(16, 40))
    haze = haze.filter(ImageFilter.GaussianBlur(8 * k))
    scr = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(scr)
    for _ in range(520):
        x, y = rnd.gauss(wmm / 2, wmm / 3.0), rnd.gauss(hmm / 2, hmm / 3.0)
        a, ln = rnd.uniform(0, math.pi), rnd.uniform(2.0, 16.0)
        sd.line([P(x, y), P(x + ln * math.cos(a), y + ln * math.sin(a))], fill=rnd.randint(40, 120), width=1)
    for _ in range(30):                                     # long arcs - wiped
        cx, cy, r = rnd.uniform(0, wmm), rnd.uniform(0, hmm), rnd.uniform(40, 120)
        a0 = rnd.uniform(0, 2 * math.pi)
        pts = [P(cx + r * math.cos(a0 + t * 0.02), cy + r * math.sin(a0 + t * 0.02)) for t in range(rnd.randint(8, 28))]
        sd.line(pts, fill=rnd.randint(30, 80), width=1)
    light = ImageChops.lighter(haze, scr)
    paint(img, (250, 250, 244), light, 0.55)
    gloss = ImageChops.subtract(gloss, haze.point(lambda v: v * 2))
    gloss = ImageChops.subtract(gloss, scr.point(lambda v: v // 2))
    save(img, "map.png")
    save(gloss, "map_gloss.png")


# =============================================================================
# Officer's ruler (glass section)
# =============================================================================
def make_ruler():
    wmm, hmm = L.RULER[0] * 1000, L.RULER[1] * 1000
    W, H = 1024, 512
    k = W / wmm                                                  # 5.12 px/mm
    rnd = random.Random(8010)

    def P(x, y):
        return x * k, y * k

    def lw(mm):
        return max(1, int(round(mm * k)))
    cut = Image.new("L", (W, H), 0)                              # 255 - a cut-out through the plastic
    c = ImageDraw.Draw(cut)
    eng = Image.new("L", (W, H), 0)                              # engraving of the scales (light)
    e = ImageDraw.Draw(eng)

    # millimetre scale along the top edge 0-19 cm and along the left one 0-9 cm
    for i in range(0, 191):
        x = 5.0 + i
        ln = 3.4 if i % 10 == 0 else (2.4 if i % 5 == 0 else 1.5)
        e.line([P(x, 0.4), P(x, 0.4 + ln)], fill=255, width=1)
        if i % 10 == 0 and 0 < i < 190:
            digits_c(e, str(i // 10), *P(x, 5.6), 2.0 * k, lw(0.22))
    for i in range(0, 91):
        y = 6.0 + i
        if y > hmm - 2:
            break
        ln = 3.0 if i % 10 == 0 else (2.0 if i % 5 == 0 else 1.2)
        e.line([P(0.4, y), P(0.4 + ln, y)], fill=255, width=1)

    # digit stencil (stroke cut-outs)
    x = 14.0
    for ch in "1234567890":
        digits(c, ch, *P(x, 15.5), 6.2 * k, lw(1.1))
        x += 5.6
    # a row of rectangles and squares
    for i in range(8):
        x0 = 14 + i * 7.2
        c.rectangle([P(x0, 19.5), P(x0 + 4.4 + (i % 3) * 0.6, 24.5)], fill=255)
    # a big circle and a scatter of circles
    c.ellipse([P(80, 9), P(102, 31)], fill=255)
    for cx, cy, r in ((72, 12, 2.4), (108, 12, 1.6), (112, 22, 3.0), (64, 30, 4.0), (72, 40, 2.0), (106, 36, 2.6),
                      (60, 52, 3.4), (66, 62, 1.5), (128, 46, 1.6), (186, 18, 1.4), (150, 66, 2.2)):
        c.ellipse([P(cx - r, cy - r), P(cx + r, cy + r)], fill=255)
    # coordinate-measurer windows (1 : 25 000 - 40 mm, 1 : 50 000 - 20 mm) with 0-1000 scales
    for x0, y0, w, h in ((8, 30, 40, 15), (8, 56, 20, 12)):
        c.rectangle([P(x0, y0), P(x0 + w, y0 + h)], fill=255)
        for j in range(11):
            xx = x0 + w * j / 10
            e.line([P(xx, y0 + h + 0.3), P(xx, y0 + h + (2.0 if j % 5 == 0 else 1.2))], fill=255, width=1)
        for j in range(6):
            digits_c(e, str(j * 200), *P(x0 + w * j / 5, y0 + h + 3.4), 1.5 * k, lw(0.18))
        for j in range(int(h // 2) + 1):
            yy = y0 + h - j * 2.0 * (40.0 / w if w < 40 else 1.0) / (1.0 if w >= 40 else 2.0)
            if yy >= y0:
                e.line([P(x0 + w + 0.3, yy), P(x0 + w + 1.6, yy)], fill=255, width=1)
    # rhombi, triangles, flags, arrows
    for i, (cx, cy) in enumerate(((122, 10), (132, 10), (142, 10), (128, 18), (138, 18), (148, 18))):
        s = 3.2
        c.polygon([P(cx, cy - s), P(cx + s * 1.3, cy), P(cx, cy + s), P(cx - s * 1.3, cy)], fill=255)
    for i, (cx, cy) in enumerate(((158, 10), (168, 12), (176, 28), (158, 30), (168, 40))):
        s = 3.6 + (i % 2)
        c.polygon([P(cx, cy - s), P(cx + s, cy + s * 0.8), P(cx - s, cy + s * 0.8)], fill=255)
    for cx, cy in ((122, 30), (134, 30), (146, 30)):
        c.polygon([P(cx - 3, cy - 3), P(cx + 3, cy - 1.5), P(cx - 3, cy)], fill=255)
        c.rectangle([P(cx - 3.4, cy - 3), P(cx - 2.8, cy + 3)], fill=255)
    for cx, cy in ((122, 42), (138, 42)):
        c.polygon([P(cx - 5, cy - 1), P(cx + 1, cy - 1), P(cx + 1, cy - 3), P(cx + 5, cy), P(cx + 1, cy + 3),
                   P(cx + 1, cy + 1), P(cx - 5, cy + 1)], fill=255)
    # drops and rectangular "flags" at the right
    for cx, cy in ((158, 52), (168, 54)):
        c.ellipse([P(cx - 3, cy - 2), P(cx + 3, cy + 4)], fill=255)
        c.polygon([P(cx - 2.6, cy - 0.5), P(cx, cy - 6), P(cx + 2.6, cy - 0.5)], fill=255)
    for i in range(4):
        c.rectangle([P(178, 38 + i * 9), P(186, 44 + i * 9)], fill=255)
    # a big oval and a small oval
    c.ellipse([P(156, 62), P(184, 84)], fill=255)
    c.ellipse([P(132, 76), P(148, 86)], fill=255)
    # protractor: an arc with degrees, holes every 10 degrees, digits
    cx, cy, r = 100.0, 99.0, 34.0
    for deg in range(0, 181):
        a = math.radians(180 - deg)
        ln = 2.6 if deg % 10 == 0 else (1.8 if deg % 5 == 0 else 1.0)
        e.line([P(cx + r * math.cos(a), cy - r * math.sin(a)),
                P(cx + (r - ln) * math.cos(a), cy - (r - ln) * math.sin(a))], fill=255, width=1)
        if deg % 20 == 0:
            ra = r + 2.6
            digits_c(e, str(deg), *P(cx + ra * math.cos(a), cy - ra * math.sin(a)), 1.6 * k, lw(0.18))
        if deg % 10 == 0:
            rh = r - 4.4
            c.ellipse([P(cx + rh * math.cos(a) - 0.8, cy - rh * math.sin(a) - 0.8),
                       P(cx + rh * math.cos(a) + 0.8, cy - rh * math.sin(a) + 0.8)], fill=255)
    e.arc([P(cx - r, cy - r), P(cx + r, cy + r)], 180, 360, fill=255, width=1)
    e.line([P(cx - r - 1, cy - 0.6), P(cx + r + 1, cy - 0.6)], fill=255, width=1)
    for cx2, cy2, s in ((88, 82, 4.0), (100, 78, 3.2), (112, 82, 4.0)):
        c.rectangle([P(cx2 - s / 2, cy2 - s / 2), P(cx2 + s / 2, cy2 + s / 2)], fill=255)
    c.ellipse([P(98.6, 90), P(101.4, 92.8)], fill=255)
    # toothed right edge (for tracing) and an arrow notch at the lower left
    for i in range(10):
        y = 52 + i * 4.6
        c.ellipse([P(wmm - 1.6, y - 1.5), P(wmm + 1.6, y + 1.5)], fill=255)
    c.polygon([P(-1, 88), P(5, 94), P(-1, 100)], fill=255)

    cut = cut.point(lambda v: 255 if v > 100 else 0)
    rim = ImageChops.subtract(cut.filter(ImageFilter.MaxFilter(5)), cut)
    eng = eng.filter(ImageFilter.GaussianBlur(0.35))
    # scuffs and scratches of the plastic
    scr = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(scr)
    for _ in range(260):
        x, y = rnd.uniform(0, wmm), rnd.uniform(0, hmm)
        a, ln = rnd.uniform(0, math.pi), rnd.uniform(1.5, 12.0)
        sd.line([P(x, y), P(x + ln * math.cos(a), y + ln * math.sin(a))], fill=rnd.randint(30, 90), width=1)
    tone = smooth_field(W, H, (5, 3), 8011, blur=12)
    img = Image.new("RGBA", (W, H))
    px = img.load()
    cp, rp, ep, sp, tp = cut.load(), rim.load(), eng.load(), scr.load(), tone.load()
    border = int(0.7 * k)
    for y in range(H):
        for x in range(W):
            if cp[x, y]:
                px[x, y] = (150, 200, 160, 0)
                continue
            tt = (tp[x, y] - 128) / 128.0
            r, g, b, a = 128 + 10 * tt, 186 + 8 * tt, 150 + 6 * tt, 66 + 10 * tt
            edge = x < border or y < border or x >= W - border or y >= H - border
            if edge or rp[x, y]:
                r, g, b, a = 196, 232, 204, 168 if edge else 150
            ev = ep[x, y] / 255.0
            if ev > 0:
                r, g, b, a = r + (232 - r) * ev, g + (244 - g) * ev, b + (232 - b) * ev, a + (196 - a) * ev
            sv = sp[x, y] / 255.0
            if sv > 0:
                r, g, b, a = r + (220 - r) * sv, g + (236 - g) * sv, b + (220 - b) * sv, a + 50 * sv
            px[x, y] = (int(r), int(g), int(b), int(min(255, a)))
    save(img, "ruler_ca.png")


# =============================================================================
# Curvimeter KU-A: face
# =============================================================================
def make_curv():
    k = 10.0
    wmm, hmm = 44.0, 66.0                                        # u: -22..22, v: -33..33 (up is toward the handle)
    W, H = int(wmm * k), int(hmm * k)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def P(u, v):                                                 # mm from the dial centre
        return (u + wmm / 2) * k, (hmm / 2 - v) * k
    R = L.CURV_DIAL_R * 1000
    d.ellipse([P(-R, R), P(R, -R)], fill=(236, 234, 226, 255))
    ink = Image.new("L", (W, H), 0)
    e = ImageDraw.Draw(ink)
    e.ellipse([P(-R + 0.5, R - 0.5), P(R - 0.5, -R + 0.5)], outline=255, width=int(0.25 * k))
    for i in range(100):
        a = math.radians(90 - i * 3.6)
        ln = 2.4 if i % 10 == 0 else (1.7 if i % 5 == 0 else 1.1)
        r0 = R - 1.0
        e.line([P(r0 * math.cos(a), r0 * math.sin(a)), P((r0 - ln) * math.cos(a), (r0 - ln) * math.sin(a))],
               fill=255, width=max(1, int((0.28 if i % 5 == 0 else 0.16) * k)))
        if i % 10 == 0:
            rr = R - 5.6
            digits_c(e, str(i), *P(rr * math.cos(a), rr * math.sin(a)), 2.4 * k, int(0.3 * k))
    img.paste((24, 24, 26, 255), (0, 0), ink.filter(ImageFilter.GaussianBlur(0.4)))
    # needle (blued) and hub
    a = math.radians(90 - 37 * 3.6)
    tip, tail = R - 2.0, 3.0
    d.line([P(-tail * math.cos(a), -tail * math.sin(a)), P(tip * math.cos(a), tip * math.sin(a))],
           fill=(30, 34, 46, 255), width=int(0.5 * k))
    d.ellipse([P(-1.1, 1.1), P(1.1, -1.1)], fill=(150, 120, 70, 255))
    # screws on the black body
    for u, v in ((0.0, 23.6), (-6.2, -22.6), (6.2, -22.6)):
        d.ellipse([P(u - 1.3, v + 1.3), P(u + 1.3, v - 1.3)], fill=(176, 178, 180, 255))
        d.line([P(u - 1.0, v + 0.5), P(u + 1.0, v - 0.5)], fill=(70, 70, 72, 255), width=int(0.3 * k))
    save(img, "curv_top.png")


# =============================================================================
# Adrianov compass: limb, needle, sighting ring
# =============================================================================
def make_compass():
    k = 10.0
    S = 48.0
    W = H = int(S * k)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def P(u, v):
        return (u + S / 2) * k, (S / 2 - v) * k
    LUM = (206, 222, 168, 255)                                   # luminous compound, yellowed
    RD, RB = L.COMP_DIAL_R * 1000, L.COMP_BEZEL_R * 1000
    # sighting ring: black, ticks every 3 degrees (white, worn), a luminous pointer by the front
    # sight
    d.ellipse([P(-RB, RB), P(RB, -RB)], fill=(22, 20, 19, 255))
    rot = math.radians(L.BEZEL_ROT)
    ink = Image.new("L", (W, H), 0)
    e = ImageDraw.Draw(ink)
    for i in range(120):
        a = math.pi / 2 + rot + i * math.radians(3)
        ln = 1.6 if i % 5 == 0 else 0.9
        e.line([P((RB - 0.4) * math.cos(a), (RB - 0.4) * math.sin(a)),
                P((RB - 0.4 - ln) * math.cos(a), (RB - 0.4 - ln) * math.sin(a))], fill=255, width=max(1, int(0.18 * k)))
    img.paste((196, 194, 182, 255), (0, 0), ink.filter(ImageFilter.GaussianBlur(0.3)).point(lambda v: v * 3 // 4))
    a = math.pi / 2 + rot
    tri = [P((RB - 2.2) * math.cos(a), (RB - 2.2) * math.sin(a)),
           P((RB - 4.2) * math.cos(a + 0.09), (RB - 4.2) * math.sin(a + 0.09)),
           P((RB - 4.2) * math.cos(a - 0.09), (RB - 4.2) * math.sin(a - 0.09))]
    d.polygon(tri, fill=LUM)
    # limb: black, a scale every 3 degrees, luminous marks at 0, 15, 30, 45, digits
    d.ellipse([P(-RD, RD), P(RD, -RD)], fill=(16, 16, 18, 255))
    ink = Image.new("L", (W, H), 0)
    e = ImageDraw.Draw(ink)
    for i in range(120):
        a = math.pi / 2 - i * math.radians(3)
        ln = 1.8 if i % 10 == 0 else (1.2 if i % 5 == 0 else 0.7)
        r0 = RD - 0.5
        e.line([P(r0 * math.cos(a), r0 * math.sin(a)), P((r0 - ln) * math.cos(a), (r0 - ln) * math.sin(a))],
               fill=255, width=max(1, int(0.16 * k)))
    for j, t in enumerate(("0", "15", "30", "45")):
        a = math.pi / 2 - j * math.pi / 2
        rr = RD - 4.6
        digits_c(e, t, *P(rr * math.cos(a), rr * math.sin(a)), 2.2 * k, int(0.28 * k))
    img.paste((214, 212, 200, 255), (0, 0), ink.filter(ImageFilter.GaussianBlur(0.3)))
    for j in range(4):
        a = math.pi / 2 - j * math.pi / 2
        rr = RD - 2.6
        cx, cy = rr * math.cos(a), rr * math.sin(a)
        if j == 0:
            d.polygon([P(cx, cy - 1.0), P(cx - 1.1, cy + 1.0), P(cx + 1.1, cy + 1.0)], fill=LUM)
        else:
            d.ellipse([P(cx - 0.7, cy + 0.7), P(cx + 0.7, cy - 0.7)], fill=LUM)
    # needle: bluish black, the north end glows, a brass hub
    a = math.radians(90 + L.NEEDLE_DEG)
    ln = RD - 3.4
    ca, sa = math.cos(a), math.sin(a)
    pa, pb = (-sa, ca), (sa, -ca)
    w = 1.3
    d.polygon([P(ln * ca, ln * sa), P(pa[0] * w, pa[1] * w), P(-ln * ca, -ln * sa), P(pb[0] * w, pb[1] * w)],
              fill=(40, 44, 58, 255))
    d.polygon([P(ln * ca, ln * sa), P(pa[0] * w * 0.6 + ln * 0.45 * ca, pa[1] * w * 0.6 + ln * 0.45 * sa),
               P(pb[0] * w * 0.6 + ln * 0.45 * ca, pb[1] * w * 0.6 + ln * 0.45 * sa)], fill=LUM)
    d.ellipse([P(-1.0, 1.0), P(1.0, -1.0)], fill=(168, 136, 78, 255))
    save(img, "comp_top.png")


# =============================================================================
# Inventory tag
# =============================================================================
def make_tag():
    k = 20.0
    wmm, hmm = L.TAG[0] * 1000, L.TAG[1] * 1000
    W, H = int(wmm * k), int(hmm * k)
    rnd = random.Random(8020)
    base = smooth_field(W, H, (6, 3), 8021, blur=4)
    img = Image.merge("RGB", [base.point(lambda v: 150 + v // 6)] * 3)
    m = Image.new("L", (W, H), 0)
    digits(ImageDraw.Draw(m), "4706", 7.0 * k, 8.6 * k, 6.0 * k, int(0.7 * k), rnd=rnd, slant=0.0, jitter=0.01)
    lo = m.transform(m.size, Image.AFFINE, (1, 0, -3, 0, 1, -3)).filter(ImageFilter.GaussianBlur(1.0))
    hi = m.transform(m.size, Image.AFFINE, (1, 0, 3, 0, 1, 3)).filter(ImageFilter.GaussianBlur(1.0))
    paint(img, (214, 216, 218), lo, 0.8)                         # punched out of the face: a light edge
    paint(img, (70, 72, 76), hi, 0.8)
    d = ImageDraw.Draw(img)
    for x in (2.2, wmm - 2.2):                                  # nails
        d.ellipse([(x - 1.0) * k, (hmm / 2 - 1.0) * k, (x + 1.0) * k, (hmm / 2 + 1.0) * k], fill=(96, 92, 86))
        d.ellipse([(x - 0.5) * k, (hmm / 2 - 0.7) * k, (x + 0.3) * k, (hmm / 2 - 0.1) * k], fill=(150, 146, 140))
    d.rectangle([0, 0, W - 1, H - 1], outline=(110, 112, 116), width=int(0.4 * k))
    save(img, "tag.png")


if __name__ == "__main__":
    make_map()
    make_ruler()
    make_curv()
    make_compass()
    make_tag()
