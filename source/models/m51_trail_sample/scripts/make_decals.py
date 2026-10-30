"""Sheet drawing of M51 (system Python + Pillow): a double sheet from the middle of a squared school
exercise book with a careless hand-drawn sketch map on the front side of the spread. No letters: signs,
crosses, arrows and digits at the marks.

    python make_decals.py      -> ../work/paper_map.png (colour), ../work/paper_height.png (relief)

The image is the whole sheet in its coordinates (m51_layout: s left to right, t bottom to top, the top
of the image is t = SHEET_H). The generator puts it onto the faces by the unfolded sheet coordinates, so
the folds cut the drawing the same way as on a real folded sheet.

What is on the sheet:
- paper: greyish exercise-book paper, a lilac-blue 5 mm grid, red 20 mm margins at the outer edges (GOST
  12063-89 - 170 x 205 mm; the margins and grid offsets follow the exercise-book template);
- pencil: a road (double line), a dashed dirt road, a railway with cross ticks, a river with banks, a
  forest as 'clouds', a swamp as ticks, heights as hatches, a lake, houses as squares, erased places;
- blue pen: a trail (partly traced twice, partly dashed), direction arrows, crosses numbered 1-7,
  distance digits, the start as a triangle, the end as a circled cross, a north arrow (no letter), a
  crossed-out dead end;
- red: anomaly circles (double, hatched), a dashed field boundary with a trefoil, a cross on the dead
  end;
- traces: yellowing and dirt at the edges, the outer (right) page is dirtier - it was held in hands; the
  folds are worn, the paper is rubbed through at fold crossings; a mug ring, water stains, a dirty
  fingerprint, rusty staple punctures on the spine.
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m51_layout as ly  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
D = 10                                   # pixels per mm when drawing
OUT = 5                                  # pixels per mm in the colour image
OUT_H = 4                                # pixels per mm in the relief
SW, SH = ly.SHEET_W * 1000.0, ly.SHEET_H * 1000.0
SPINE, FOLD2 = ly.SPINE * 1000.0, ly.FOLD2 * 1000.0
OLD = [f * 1000.0 for f in ly.OLD_FOLD]
W, H = int(SW * D), int(SH * D)

PAPER = (226, 221, 201)
PAPER_OLD = (208, 197, 165)
GRID = (138, 152, 204)
MARGIN_RED = (206, 86, 98)
GRAPHITE = (74, 74, 82)
PEN_BLUE = (28, 48, 150)
RED = (196, 34, 30)
GRIME = (112, 98, 74)
TEA = (138, 92, 46)
RUST = (128, 64, 30)


def px(s, t):
    return (s * D, (SH - t) * D)


class Ink:
    def __init__(self, color):
        self.color = color
        self.a = Image.new("L", (W, H), 0)
        self.d = ImageDraw.Draw(self.a)


# --- strokes ---------------------------------------------------------------------------------
def chaikin(pts, it):
    for _ in range(it):
        out = [pts[0]]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            out += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1), (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        out.append(pts[-1])
        pts = out
    return pts


def resample(pts, step):
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        out += [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(1, n + 1)]
    return out


def wobble(pts, amp, seed):
    """Hand tremor: a smooth random shift of each point."""
    r = random.Random(seed)
    ox = oy = 0.0
    out = []
    for x, y in pts:
        ox = ox * 0.82 + r.uniform(-1, 1) * amp * 0.55
        oy = oy * 0.82 + r.uniform(-1, 1) * amp * 0.55
        out.append((x + ox, y + oy))
    return out


def stroke(ink, pts, width, val=255, amp=0.25, seed=0, dash=None, smooth=2, step=0.8, press=0.3):
    """Hand-drawn line through points (mm): smoothing, tremor, pressure (the width wanders), dashes
    (dash, gap) in mm.
    """
    p = wobble(resample(chaikin(list(pts), smooth) if smooth else list(pts), step), amp, seed)
    r = random.Random(seed + 7919)
    w = width
    run = 0.0
    for a, b in zip(p, p[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        run += seg
        if dash and (run % (dash[0] + dash[1])) > dash[0]:
            continue
        w = w * 0.7 + width * (1 + r.uniform(-press, press)) * 0.3
        A, B = px(*a), px(*b)
        wp = max(1, int(round(w * D)))
        ink.d.line([A, B], fill=val, width=wp)
        rr = wp / 2.0
        ink.d.ellipse([B[0] - rr, B[1] - rr, B[0] + rr, B[1] + rr], fill=val)


def sketch(ink, pts, width, val=230, seed=0, passes=2, spread=0.35, **kw):
    """Pencil in several passes: each with its own tremor and slightly aside."""
    r = random.Random(seed + 31)
    for k in range(passes):
        dx, dy = r.uniform(-spread, spread), r.uniform(-spread, spread)
        stroke(ink, [(x + dx, y + dy) for x, y in pts], width, int(val * (1.0 - 0.25 * k)), seed=seed + 101 * k, **kw)


def offset_line(pts, d):
    """Parallel line (for a double road, banks)."""
    p = resample(chaikin(list(pts), 2), 1.5)
    out = []
    for i, (x, y) in enumerate(p):
        a, b = p[max(i - 1, 0)], p[min(i + 1, len(p) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        n = math.hypot(tx, ty) or 1.0
        out.append((x - ty / n * d, y + tx / n * d))
    return out


def hand_circle(c, r, seed, sweep=385.0, ell=0.07):
    """Hand-drawn circle: not closed exactly, slightly oval, the radius drifts."""
    rr = random.Random(seed)
    a0, phi = rr.uniform(0, 360), rr.uniform(0, 6.28)
    n = int(max(28, r * 5))
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + sweep * i / n)
        k = 1 + ell * math.sin(2 * a + phi) + 0.06 * (i / n - 0.5)
        pts.append((c[0] + r * k * math.cos(a), c[1] + r * k * math.sin(a)))
    return pts


def scallop(c, rx, ry, bumps, seed):
    """Forest outline as a 'cloud': arcs outwards, sharp notches between them."""
    rr = random.Random(seed)
    a0 = rr.uniform(0, 6.28)
    pts = []
    n = bumps * 8
    for i in range(n + 1):
        a = a0 + 2 * math.pi * i / n
        k = 0.86 + 0.18 * abs(math.sin(bumps * (a - a0) / 2)) + rr.uniform(-0.02, 0.02)
        pts.append((c[0] + rx * k * math.cos(a), c[1] + ry * k * math.sin(a)))
    return pts


def cross(ink, c, size, width, seed, val=255):
    r = random.Random(seed)
    a = math.radians(r.uniform(30, 60))
    for k in (0, 1):
        aa = a + k * math.pi / 2 + r.uniform(-0.15, 0.15)
        dx, dy = math.cos(aa) * size / 2, math.sin(aa) * size / 2
        stroke(ink, [(c[0] - dx * 1.1, c[1] - dy * 1.1), (c[0] + dx, c[1] + dy)], width, val, amp=0.1,
               seed=seed + k, smooth=0, step=0.4)


def arrowhead(ink, tip, ang_deg, size, width, seed, val=255):
    for s in (-1, 1):
        a = math.radians(ang_deg + 180 + s * 27)
        stroke(ink, [tip, (tip[0] + math.cos(a) * size, tip[1] + math.sin(a) * size)], width, val, amp=0.08,
               seed=seed + s, smooth=0, step=0.4)


def hatch(ink, c, r, ang_deg, gap, width, seed, val=200):
    """Hatching inside a circle."""
    a = math.radians(ang_deg)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    k = -r + gap / 2
    i = 0
    while k < r:
        h = math.sqrt(max(r * r - k * k, 0)) * 0.9
        p0 = (c[0] + nx * k - ux * h, c[1] + ny * k - uy * h)
        p1 = (c[0] + nx * k + ux * h, c[1] + ny * k + uy * h)
        stroke(ink, [p0, p1], width, val, amp=0.12, seed=seed + i, smooth=0, step=0.6)
        k += gap
        i += 1


def font(px_size):
    for name in ("Inkfree.ttf", "segoepr.ttf", "comic.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, px_size)
        except OSError:
            continue
    return ImageFont.load_default()


def digits(ink, text, at, size_mm, angle, val=235):
    """Hand-written digits (digits only)."""
    f = font(int(size_mm * D))
    tw = int(size_mm * D * (0.75 * len(text) + 1.0))
    tmp = Image.new("L", (tw, int(size_mm * D * 1.8)), 0)
    ImageDraw.Draw(tmp).text((int(size_mm * D * 0.4), int(size_mm * D * 0.2)), text, font=f, fill=val,
                             stroke_width=max(1, int(0.2 * D)), stroke_fill=val)
    tmp = tmp.rotate(angle, resample=Image.BICUBIC, expand=True)
    x, y = px(*at)
    box = (int(x - tmp.width / 2), int(y - tmp.height / 2))
    reg = ink.a.crop((box[0], box[1], box[0] + tmp.width, box[1] + tmp.height))
    ink.a.paste(ImageChops.lighter(reg, tmp), box)


def trefoil(ink, c, r, seed, val=215):
    """Hand-drawn radiation trefoil: three blades and a dot in the centre."""
    rr = random.Random(seed)
    for k in range(3):
        a0 = math.radians(90 + 120 * k - 30)
        a1 = math.radians(90 + 120 * k + 30)
        pts = []
        for i in range(9):
            a = a0 + (a1 - a0) * i / 8
            pts.append((c[0] + r * math.cos(a) * rr.uniform(0.94, 1.04), c[1] + r * math.sin(a) * rr.uniform(0.94, 1.04)))
        for i in range(9):
            a = a1 - (a1 - a0) * i / 8
            pts.append((c[0] + 0.32 * r * math.cos(a), c[1] + 0.32 * r * math.sin(a)))
        ink.d.polygon([px(*p) for p in pts], fill=val)
    rd = 0.2 * r * D
    x, y = px(*c)
    ink.d.ellipse([x - rd, y - rd, x + rd, y + rd], fill=val)


def house(ink, c, w, h, ang, seed, val=220):
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    corners = [(c[0] + ux * sx * w / 2 + nx * sy * h / 2, c[1] + uy * sx * w / 2 + ny * sy * h / 2)
               for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    stroke(ink, corners + [corners[0], corners[1]], 0.55, val, amp=0.12, seed=seed, smooth=0, step=0.5)
    for i in range(1, 4):                                   # diagonal hatching
        f = i / 4.0
        p0 = (corners[0][0] + (corners[1][0] - corners[0][0]) * f, corners[0][1] + (corners[1][1] - corners[0][1]) * f)
        p1 = (corners[3][0] + (corners[2][0] - corners[3][0]) * (f - 0.2), corners[3][1] + (corners[2][1] - corners[3][1]) * (f - 0.2))
        stroke(ink, [p0, p1], 0.4, int(val * 0.7), amp=0.08, seed=seed + 10 + i, smooth=0, step=0.5)


# --- noise -------------------------------------------------------------------------------------
def field(cell_mm, seed, size=(W, H)):
    """Smooth noise 0..255 with blotches ~cell_mm."""
    w, h = max(2, int(SW / cell_mm) + 2), max(2, int(SH / cell_mm) + 2)
    r = random.Random(seed)
    return Image.frombytes("L", (w, h), r.randbytes(w * h)).resize(size, Image.BICUBIC)


def grain(seed, lo, hi, size=(W, H)):
    """Paper / pencil grain: lo..hi."""
    r = random.Random(seed)
    w, h = size[0] // 2, size[1] // 2
    im = Image.frombytes("L", (w, h), r.randbytes(w * h)).resize(size, Image.BILINEAR)
    return im.point(lambda v: int(lo + (hi - lo) * v / 255.0))


def levels(im, a, b, lo=0, hi=255):
    """a..b -> lo..hi with clipping."""
    def f(v):
        x = min(max((v - a) / float(b - a), 0.0), 1.0)
        return int(lo + (hi - lo) * x)
    return im.point(f)


def put(base, color, alpha, k=1.0):
    if k != 1.0:
        alpha = alpha.point(lambda v: int(v * k))
    return Image.composite(Image.new("RGB", base.size, color), base, alpha)


def mask_rect(s0, s1, t0, t1, blur_mm=0.0):
    m = Image.new("L", (W, H), 0)
    x0, y1 = px(s0, t0)
    x1, y0 = px(s1, t1)
    ImageDraw.Draw(m).rectangle([x0, y0, x1, y1], fill=255)
    return m.filter(ImageFilter.GaussianBlur(blur_mm * D)) if blur_mm else m


# --- sheet -----------------------------------------------------------------------------------
def paper():
    base = Image.new("RGB", (W, H), PAPER)
    base = put(base, PAPER_OLD, levels(field(28.0, 1), 90, 220), 0.55)              # yellowing in patches
    edge = Image.new("L", (W, H), 255)
    x0, y0 = px(6, SH - 6)
    x1, y1 = px(SW - 6, 6)
    ImageDraw.Draw(edge).rectangle([x0, y0, x1, y1], fill=0)
    edge = edge.filter(ImageFilter.GaussianBlur(7 * D))
    base = put(base, PAPER_OLD, edge, 0.8)                                           # yellower towards the edges
    # the outer page (right) was held in hands: dirtier, in patches
    outer = ImageChops.multiply(mask_rect(SPINE + 1, SW, 0, SH, 2.0), levels(field(16.0, 2), 120, 245))
    outer = ImageChops.multiply(outer, levels(field(4.0, 33), 60, 255, 90, 255))
    base = put(base, GRIME, outer, 0.13)
    return put(base, (190, 184, 166), grain(3, 0, 70), 0.5)                         # grain


def grid(base):
    g = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(g)
    cell, t0, t1 = ly.CELL * 1000, ly.GRID_TB * 1000, SH - ly.GRID_TB * 1000
    lw = max(1, int(0.22 * D))
    for s_from, s_to, step in ((SPINE - ly.GRID_SPINE * 1000, 0.0, -cell), (SPINE + ly.GRID_SPINE * 1000, SW, cell)):
        s = s_from
        while (s >= s_to - 0.01) if step < 0 else (s <= s_to + 0.01):
            x0, y0 = px(s, t1)
            x1, y1 = px(s, t0)
            d.line([(x0, y0), (x1, y1)], fill=170, width=lw)
            s += step
        lo, hi = sorted((s_from, s_to))
        t = t0
        while t <= t1 + 0.01:
            x0, y = px(lo, t)
            x1, _ = px(hi, t)
            d.line([(x0, y), (x1, y)], fill=170, width=lw)
            t += cell
    g = ImageChops.multiply(g, grain(4, 150, 255))                                   # uneven print
    base = put(base, GRID, g)
    m = Ink(MARGIN_RED)
    for s in (ly.MARGIN * 1000, SW - ly.MARGIN * 1000):
        stroke(m, [(s, 0), (s, SH)], 0.38, 190, amp=0.0, smooth=0, step=5.0, press=0.0)
    return put(base, MARGIN_RED, ImageChops.multiply(m.a, grain(5, 160, 255)))


def pencil_layer():
    p = Ink(GRAPHITE)
    road = [(0, 150), (30, 146), (62, 141), (95, 131), (128, 119), (160, 111), (190, 112), (222, 118), (255, 121),
            (288, 117), (318, 108), (340, 104)]
    sketch(p, offset_line(road, 1.6), 0.6, seed=11, smooth=0)
    sketch(p, offset_line(road, -1.6), 0.6, seed=12, smooth=0)
    sketch(p, [(222, 118), (231, 140), (236, 165), (231, 190), (227, 205)], 0.55, seed=13, dash=(2.5, 1.8), passes=1)
    rail = [(176, 0), (200, 14), (226, 30), (258, 46), (290, 60), (322, 72), (340, 78)]
    sketch(p, rail, 0.6, seed=14)
    rp = resample(chaikin(rail, 2), 4.0)
    for i, (x, y) in enumerate(rp[1:-1], 1):                                          # sleepers
        a, b = rp[i - 1], rp[i + 1]
        tx, ty = b[0] - a[0], b[1] - a[1]
        n = math.hypot(tx, ty)
        nx, ny = -ty / n * 1.4, tx / n * 1.4
        stroke(p, [(x - nx, y - ny), (x + nx, y + ny)], 0.45, 200, amp=0.05, seed=200 + i, smooth=0, step=0.5)
    river = [(0, 88), (20, 81), (38, 66), (50, 46), (68, 31), (95, 23), (124, 13), (150, 0)]
    sketch(p, river, 0.6, seed=15, amp=0.45)
    sketch(p, offset_line(river, 2.4), 0.5, seed=16, amp=0.5, passes=1)
    rv = resample(chaikin(river, 2), 9.0)
    for i, (x, y) in enumerate(rv[1:-1], 1):                                          # ripples
        stroke(p, [(x - 1.0, y + 1.4), (x + 1.2, y + 1.6)], 0.3, 150, seed=300 + i, smooth=0, step=0.5)
    for c, rx, ry, n, sd in (((40, 26), 18, 11, 9, 21), ((136, 64), 22, 14, 11, 22), ((196, 22), 15, 10, 8, 23),
                             ((200, 172), 16, 18, 10, 24), ((300, 186), 26, 12, 12, 25)):
        sketch(p, scallop(c, rx, ry, n, sd), 0.55, seed=sd, smooth=0, passes=1, amp=0.15)
        rr = random.Random(sd)
        for k in range(int(rx * ry / 45)):                                           # trees as small circles
            a, q = rr.uniform(0, 6.28), math.sqrt(rr.uniform(0, 1)) * 0.7
            cc = (c[0] + rx * q * math.cos(a), c[1] + ry * q * math.sin(a))
            stroke(p, hand_circle(cc, rr.uniform(0.9, 1.6), sd * 10 + k, sweep=360), 0.4, 180, smooth=0, step=0.4)
    rr = random.Random(41)
    for k in range(22):                                                               # swamp
        x, y = rr.uniform(78, 112), rr.uniform(48, 70)
        stroke(p, [(x, y), (x + rr.uniform(3, 6), y + rr.uniform(-0.3, 0.3))], 0.35, 180, seed=400 + k, smooth=0)
    for c, r0, a0, a1, sd in (((60, 182), 17, 200, 340, 51), ((96, 196), 10, 190, 350, 52), ((160, 40), 9, 0, 300, 53)):
        n = int((a1 - a0) / 9)                                                        # heights as hatches
        for i in range(n):
            a = math.radians(a0 + (a1 - a0) * i / n)
            p0 = (c[0] + r0 * math.cos(a), c[1] + r0 * math.sin(a))
            p1 = (c[0] + (r0 + 3.0) * math.cos(a), c[1] + (r0 + 3.0) * math.sin(a))
            stroke(p, [p0, p1], 0.35, 200, seed=sd * 10 + i, smooth=0, step=0.5)
    lake = hand_circle((132, 176), 13, 61, sweep=362, ell=0.25)
    sketch(p, lake, 0.55, seed=61, smooth=0)
    for i in range(6):
        y = 168 + i * 3.2
        stroke(p, [(124 + (i % 2) * 2, y), (139 - (i % 3), y + 0.3)], 0.3, 150, seed=620 + i, smooth=0)
    for c, w, h, a, sd in (((104, 134), 6, 4, -18, 71), ((114, 128), 5, 4, -20, 72), ((124, 136), 7, 5, -16, 73),
                           ((186, 64), 11, 6, 8, 74), ((306, 86), 6, 4, 20, 75), ((316, 92), 5, 4, 15, 76),
                           ((312, 79), 7, 4, 25, 77), ((246, 140), 6, 5, 80, 78), ((252, 152), 7, 4, 82, 79),
                           ((242, 162), 5, 4, 75, 80), ((262, 146), 6, 4, 85, 81)):
        house(p, c, w, h, a, sd)
    # erased: smeared graphite and traces of the line under it
    smear = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(smear)
    for (s, t), rx, ry in (((231, 84), 9, 5), ((62, 138), 8, 6), ((150, 92), 6, 4)):
        x, y = px(s, t)
        sd.ellipse([x - rx * D, y - ry * D, x + rx * D, y + ry * D], fill=60)
    stroke(p, [(224, 80), (230, 85), (238, 87)], 0.4, 70, seed=90)
    p.a = ImageChops.lighter(p.a, smear.filter(ImageFilter.GaussianBlur(2.5 * D)))
    p.a = ImageChops.multiply(p.a, grain(6, 120, 255))
    return p


TRAIL = [(12, 58), (28, 62), (46, 72), (64, 86), (84, 92), (104, 98), (122, 104), (140, 108), (156, 104), (168, 98),
         (178, 100), (190, 104), (200, 103), (206, 90), (214, 74), (226, 62), (240, 56), (252, 44), (262, 32),
         (280, 24), (298, 30), (314, 44), (324, 62), (326, 82), (318, 100), (310, 118), (304, 134), (300, 150),
         (300, 164)]
MARKS = [((46, 72), "1"), ((156, 104), "2"), ((214, 74), "3"), ((280, 24), "4"), ((324, 62), "5"), ((310, 118), "6")]


def pen_layer():
    b = Ink(PEN_BLUE)
    stroke(b, TRAIL[:12], 0.75, 235, seed=101, amp=0.3)
    stroke(b, TRAIL[11:20], 0.75, 235, seed=102, amp=0.3, dash=(3.2, 1.6))              # unsure - dashed
    stroke(b, TRAIL[19:], 0.75, 235, seed=103, amp=0.3)
    stroke(b, [(x + 0.5, y - 0.4) for x, y in TRAIL[19:26]], 0.6, 200, seed=104, amp=0.35)   # traced once more
    for i, ((x, y), n) in enumerate(MARKS):
        cross(b, (x, y), 3.8, 0.75, 110 + i)
        digits(b, n, (x + 4.6, y + 3.8), 5.4, random.Random(i).uniform(-12, 12))
    for (x, y), a in (((24, 61), 15), ((96, 96), 20), ((206, 92), -75), ((268, 28), -15), ((318, 50), 62),
                      ((304, 136), 100)):
        arrowhead(b, (x, y), a, 2.8, 0.65, 130 + int(x))
    for (x, y), n, a in (((236, 66), "300", 10), ((299, 36), "150", -20), ((88, 99), "40", 8), ((182, 108), "15", 0)):
        digits(b, n, (x, y), 4.6, a, 215)
    tri = [(12, 58), (12 - 3.4, 58 - 2.6), (12 + 3.6, 58 - 2.4), (12, 58 + 3.8)]           # start
    stroke(b, [tri[1], tri[2], tri[3], tri[1], tri[2]], 0.65, 235, seed=140, smooth=0, step=0.4, amp=0.1)
    for r, sd in ((4.0, 150), (5.6, 151)):                                                  # end
        stroke(b, hand_circle((300, 166), r, sd), 0.65, 235, smooth=0, step=0.5, seed=sd)
    cross(b, (300, 166), 5.0, 0.75, 152)
    digits(b, "7", (309, 173), 5.8, -8)
    stroke(b, [(20, 180), (20.4, 192), (20.8, 198)], 0.7, 235, seed=160, smooth=0)          # north - without a letter
    b.d.polygon([px(20.8, 201), px(18.4, 194.5), px(23.0, 194.8)], fill=235)
    stroke(b, [(240, 56), (236, 44), (230, 32), (224, 22)], 0.65, 220, seed=170)               # dead end
    zz = [(239 - k * 1.6 + (2.6 if k % 2 else -2.6), 54 - k * 3.0) for k in range(11)]
    stroke(b, zz, 0.6, 210, seed=171, smooth=0, step=0.4)                                     # crossed out
    b.a = ImageChops.multiply(b.a, grain(7, 175, 255))
    return b


def red_layer():
    r = Ink(RED)
    for c, rad, sd, dbl, hat in (((268, 58), 9.5, 1, True, False), ((246, 82), 7.0, 2, False, True),
                                 ((206, 48), 6.0, 3, False, False), ((333, 22), 4.5, 4, False, False),
                                 ((70, 47), 8.5, 5, True, False), ((150, 28), 5.5, 6, False, True),
                                 ((36, 124), 6.5, 7, False, False), ((270, 180), 8.5, 8, True, False),
                                 ((320, 140), 6.5, 9, False, True), ((160, 160), 5.0, 10, False, False)):
        stroke(r, hand_circle(c, rad, sd), 1.0, 225, smooth=0, step=0.5, seed=sd, amp=0.12)
        if dbl:
            stroke(r, hand_circle(c, rad * 1.28, sd + 50, sweep=300), 0.8, 200, smooth=0, step=0.5, seed=sd + 50)
        if hat:
            hatch(r, c, rad * 0.85, 40 + sd * 13, 1.7, 0.5, sd * 20)
    zone = hand_circle((117, 38), 21, 21, sweep=362, ell=0.35)                                  # field - dashed
    stroke(r, zone, 0.8, 215, smooth=0, step=0.5, seed=21, dash=(2.2, 1.6))
    trefoil(r, (117, 37), 6.0, 22)
    cross(r, (224, 22), 5.0, 1.0, 23, 230)                                                       # cross on the dead end
    r.a = ImageChops.multiply(r.a, grain(8, 150, 255))
    return r


def stains(base):
    # worn folds (stronger on the outer page) and rubbed-through fold crossings
    f = Ink(GRIME)
    stroke(f, [(SPINE, 0), (SPINE, SH)], 0.9, 120, amp=0.15, smooth=0, step=2.0, press=0.4, seed=501)
    stroke(f, [(0, FOLD2), (SPINE, FOLD2)], 0.8, 70, amp=0.2, smooth=0, step=2.0, press=0.4, seed=502)
    stroke(f, [(SPINE, FOLD2), (SW, FOLD2)], 1.0, 130, amp=0.2, smooth=0, step=2.0, press=0.4, seed=503)
    for s in OLD:
        stroke(f, [(s, 0), (s, SH)], 0.7, 60, amp=0.2, smooth=0, step=2.0, press=0.5, seed=504 + int(s))
    halo = f.a.filter(ImageFilter.GaussianBlur(1.6 * D))
    base = put(base, GRIME, ImageChops.lighter(f.a.filter(ImageFilter.GaussianBlur(0.25 * D)), halo), 0.6)
    wear = Image.new("L", (W, H), 0)
    wd = ImageDraw.Draw(wear)
    for s, k in ((SPINE, 1.0), (OLD[0], 0.6), (OLD[1], 0.8)):
        x, y = px(s, FOLD2)
        wd.ellipse([x - 3.2 * D, y - 2.6 * D, x + 3.2 * D, y + 2.6 * D], fill=int(150 * k))
    wear = wear.filter(ImageFilter.GaussianBlur(1.2 * D))
    base = put(base, (176, 168, 150), ImageChops.multiply(wear, grain(9, 60, 255)))
    # edges: a dirty frayed rim
    e = Image.new("L", (W, H), 255)
    x0, y0 = px(1.6, SH - 1.6)
    x1, y1 = px(SW - 1.6, 1.6)
    ImageDraw.Draw(e).rectangle([x0, y0, x1, y1], fill=0)
    e = e.filter(ImageFilter.GaussianBlur(1.1 * D))
    e = ImageChops.multiply(ImageChops.multiply(e, levels(field(7.0, 10), 40, 230)), grain(34, 90, 255))
    base = put(base, GRIME, e, 0.75)
    # mug ring on the outer page
    ring = Ink(TEA)
    stroke(ring, hand_circle((300, 20), 16.5, 601, sweep=300, ell=0.03), 1.1, 150, smooth=0, step=0.6, seed=601,
           amp=0.2, press=0.6)
    stroke(ring, hand_circle((300.6, 20.4), 15.6, 602, sweep=200, ell=0.03), 0.5, 90, smooth=0, step=0.6, seed=602)
    fill = Image.new("L", (W, H), 0)
    x, y = px(300, 20)
    ImageDraw.Draw(fill).ellipse([x - 16 * D, y - 16 * D, x + 16 * D, y + 16 * D], fill=26)
    ring.a = ImageChops.lighter(ring.a.filter(ImageFilter.GaussianBlur(0.35 * D)), fill.filter(ImageFilter.GaussianBlur(D)))
    base = put(base, TEA, ImageChops.multiply(ring.a, levels(field(4.0, 11), 40, 255, 120, 255)))
    # water stains: a blotch with a brown rim
    for c, rx, ry, sd in (((214, 16), 24, 14, 12), ((42, 8), 20, 9, 13), ((312, 186), 30, 20, 14)):
        blob = Image.new("L", (W, H), 0)
        pts = scallop(c, rx, ry, 5, sd)
        ImageDraw.Draw(blob).polygon([px(*q) for q in pts], fill=255)
        blob = blob.filter(ImageFilter.GaussianBlur(1.5 * D))
        rim = ImageChops.subtract(blob, blob.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(1.2 * D)))
        base = put(base, (196, 182, 146), blob, 0.18)
        base = put(base, (150, 126, 86), rim, 0.5)
    # dirty fingerprint at the open edge of the outer page
    fp = Image.new("L", (W, H), 0)
    fd = ImageDraw.Draw(fp)
    cx, cy = px(329, 40)
    for k in range(9):
        rx, ry = (1.2 + k * 1.15) * D, (1.8 + k * 1.5) * D
        fd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=200, width=max(1, int(0.35 * D)))
    blot = Image.new("L", (W, H), 0)
    ImageDraw.Draw(blot).ellipse([cx - 11 * D, cy - 14 * D, cx + 11 * D, cy + 14 * D], fill=255)
    fp = ImageChops.multiply(fp, blot.filter(ImageFilter.GaussianBlur(3 * D)))
    fp = ImageChops.multiply(fp.rotate(18, center=(cx, cy)), levels(field(3.0, 15), 60, 220))
    base = put(base, (92, 80, 62), fp, 0.55)
    # rusty staple punctures on the spine
    rust = Image.new("L", (W, H), 0)
    rd = ImageDraw.Draw(rust)
    for t in (ly.STAPLES[0] * 1000, ly.STAPLES[1] * 1000):
        for dt in (-ly.STAPLE_LEG * 1000, ly.STAPLE_LEG * 1000):
            x, y = px(SPINE, t + dt)
            rd.ellipse([x - 1.6 * D, y - 1.6 * D, x + 1.6 * D, y + 1.6 * D], fill=110)
        x0, y0 = px(SPINE - 0.4, t + ly.STAPLE_LEG * 1000)
        x1, y1 = px(SPINE + 0.4, t - ly.STAPLE_LEG * 1000)
        rd.rectangle([x0, y0, x1, y1], fill=120)
    base = put(base, RUST, rust.filter(ImageFilter.GaussianBlur(0.8 * D)))
    holes = Image.new("L", (W, H), 0)
    hd = ImageDraw.Draw(holes)
    for t in (ly.STAPLES[0] * 1000, ly.STAPLES[1] * 1000):
        for dt in (-ly.STAPLE_LEG * 1000, ly.STAPLE_LEG * 1000):
            x, y = px(SPINE, t + dt)
            hd.ellipse([x - 0.45 * D, y - 0.45 * D, x + 0.45 * D, y + 0.45 * D], fill=230)
    return put(base, (48, 30, 18), holes)


def height():
    """Relief: old folds are troughs, small creases, paper unevenness. 128 is flat."""
    size = (int(SW * OUT_H), int(SH * OUT_H))
    k = OUT_H / float(D)
    im = Image.new("L", size, 150)
    im = Image.blend(im, field(7.0, 31, size), 0.12)
    d = ImageDraw.Draw(im)

    def P(s, t):
        x, y = px(s, t)
        return (x * k, y * k)
    for s in OLD:
        d.line([P(s, 0), P(s, SH)], fill=70, width=max(1, int(0.5 * OUT_H)))
    rr = random.Random(32)
    for i in range(40):
        s, t = rr.uniform(0, SW), rr.uniform(0, SH)
        a, ln = rr.uniform(0, math.pi), rr.uniform(10, 45)
        p0 = (s - math.cos(a) * ln / 2, t - math.sin(a) * ln / 2)
        p1 = (s + math.cos(a) * ln / 2 + rr.uniform(-3, 3), t + math.sin(a) * ln / 2 + rr.uniform(-3, 3))
        d.line([P(*p0), P((p0[0] + p1[0]) / 2 + rr.uniform(-2, 2), (p0[1] + p1[1]) / 2 + rr.uniform(-2, 2)), P(*p1)],
               fill=rr.choice((95, 110, 185, 200)), width=1)
    return im.filter(ImageFilter.GaussianBlur(0.6 * OUT_H))


def main():
    base = grid(paper())
    for layer, k in ((pencil_layer(), 0.9), (pen_layer(), 0.92), (red_layer(), 0.9)):
        base = put(base, layer.color, layer.a, k)
    base = stains(base)
    os.makedirs(WORK, exist_ok=True)
    out = base.resize((int(SW * OUT), int(SH * OUT)), Image.LANCZOS)
    out.save(os.path.join(WORK, "paper_map.png"))
    print("wrote paper_map.png", out.size)
    h = height()
    h.save(os.path.join(WORK, "paper_height.png"))
    print("wrote paper_height.png", h.size)


if __name__ == "__main__":
    main()
