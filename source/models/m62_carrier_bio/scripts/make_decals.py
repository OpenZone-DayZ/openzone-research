"""Images for the M62 "Bio" carrier (system Python + Pillow), without letters: only fields, digits,
the biohazard sign and stamps without text.

    python make_decals.py      -> ../work/*.png

- cover_print.png - print on the front cover (like the "Delo" folder, but wordless): five rules in
  the middle and two short ones below; RGBA, the whole cover FW x FH, the top of the image is the top
  of the folder;
- cover_height.png - relief of the front cover: spine creases, the binder bar and its prongs under
  the board, a smoothed corner fold; grey 128 is flat;
- label.png - paper label 90 x 60 mm: a frame, the biohazard sign, fields with a sample number in
  handwriting, a violet stamp without text;
- form.png - A4 form (the loose sheet): a header with empty fields and number boxes, a results table
  with handwritten digits, a signature flourish, a stamp; only the bottom strip is visible;
- tape.png - the whole thermal tape (57 mm x TAPE_LEN): the analyser's dot-matrix print as columns of
  digits, blocks per sample; the top of the image is the head of the printout (the free end of the
  tape on the ground).

The fonts are our own (a 5 x 7 matrix and handwritten digits as strokes): the image does not depend
on system fonts. Sizes come from m62_layout.py (shared with build_m62.py).
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m62_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

PAPER = (238, 235, 223)
FORM_INK = (92, 98, 112)          # printed form fields
PEN = (38, 58, 142)               # ballpoint pen
STAMP = (112, 72, 150)            # stamp ink
THERMAL = (44, 46, 60)            # thermal print


def save(img, name):
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, img.size)


# --- fonts ----------------------------------------------------------------------------------------
DOT5x7 = {
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11111 00010 00100 00010 00001 10001 01110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    ".": "00000 00000 00000 00000 00000 01100 01100", "-": "00000 00000 00000 11111 00000 00000 00000",
    ":": "00000 01100 01100 00000 01100 01100 00000", "/": "00001 00001 00010 00100 01000 10000 10000",
    "*": "00000 00100 10101 01110 10101 00100 00000", "=": "00000 00000 11111 00000 11111 00000 00000",
    "+": "00000 00100 00100 11111 00100 00100 00000", "#": "11111 11111 11111 11111 11111 11111 11111",
    "<": "00010 00100 01000 10000 01000 00100 00010", ">": "01000 00100 00010 00001 00010 00100 01000",
    " ": "00000 00000 00000 00000 00000 00000 00000",
}

# handwritten digits: strokes in a 0.6 x 1 cell (y down)
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
    "/": [[(0.60, 0.0), (0.0, 1.0)]], "-": [[(0.05, 0.56), (0.50, 0.52)]], ".": [[(0.24, 0.94), (0.30, 1.0)]],
    "+": [[(0.05, 0.55), (0.55, 0.53)], [(0.30, 0.30), (0.29, 0.80)]],
}


def hand(d, text, x, y, h, rnd, col=PEN, width=None, slant=0.18, gap=0.18):
    """Handwritten digits: the string text from the bottom left corner (x, y), height h (px)."""
    width = width or max(1, int(h * 0.09))
    cx = x
    for ch in text:
        if ch == " ":
            cx += h * 0.5
            continue
        hh = h * rnd.uniform(0.9, 1.08)
        dy = rnd.uniform(-0.06, 0.06) * h
        for stroke in HAND[ch]:
            pts = []
            for px, py in stroke:
                jx, jy = rnd.uniform(-0.03, 0.03), rnd.uniform(-0.03, 0.03)
                X = cx + (px + jx) * hh + (1 - py) * slant * hh
                Y = y - hh + (py + jy) * hh + dy
                pts.append((X, Y))
            d.line(pts, fill=col, width=width, joint="curve")
        cx += hh * (0.6 + gap) * rnd.uniform(0.92, 1.1)
    return cx


def squiggle(d, x0, y0, w, h, rnd, col=PEN, width=2):
    """Signature flourish (not letters): slanted loops and a tail."""
    pts, n = [], 40
    for i in range(n + 1):
        t = i / n
        a = t * math.pi * 7.0
        pts.append((x0 + t * w + math.cos(a) * h * 0.36, y0 - math.sin(a) * h * 0.5 * (1 - 0.5 * t)
                    + rnd.uniform(-1, 1) * h * 0.04))
    pts.append((x0 + w * 1.25, y0 - h * 0.65))
    d.line(pts, fill=col, width=width, joint="curve")


def stamp(img, cx, cy, r, rnd, strength=0.75):
    """Round stamp without text: two rings with strokes between them around the circle (like a line of text,
    but not letters), a star in the centre; the ink goes on unevenly."""
    n = int(r * 2 + 8)
    m = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(m)
    c = n / 2
    w = max(1, int(r * 0.05))
    for rr in (r, r * 0.66):
        d.ellipse([c - rr, c - rr, c + rr, c + rr], outline=255, width=w)
    k = 34
    for i in range(k):
        a = 2 * math.pi * i / k + rnd.uniform(-0.03, 0.03)
        r0, r1 = r * rnd.uniform(0.72, 0.76), r * rnd.uniform(0.88, 0.94)
        if rnd.random() < 0.85:
            d.line([(c + r0 * math.cos(a), c + r0 * math.sin(a)), (c + r1 * math.cos(a), c + r1 * math.sin(a))],
                   fill=255, width=max(1, int(r * 0.06)))
    star = [(c + (r * (0.36 if i % 2 == 0 else 0.15)) * math.cos(-math.pi / 2 + math.pi * i / 5),
             c + (r * (0.36 if i % 2 == 0 else 0.15)) * math.sin(-math.pi / 2 + math.pi * i / 5)) for i in range(10)]
    d.polygon(star, fill=255)
    noise = Image.effect_noise((n, n), 90).point(lambda v: 255 if v > 112 else int(v * 1.6))
    fade = Image.linear_gradient("L").resize((n, n)).rotate(rnd.uniform(0, 360)).point(lambda v: 110 + v // 2)
    m = ImageChops.multiply(ImageChops.multiply(m, noise), fade)
    m = m.point(lambda v: int(v * strength)).filter(ImageFilter.GaussianBlur(0.6))
    m = m.rotate(rnd.uniform(-25, 25))
    img.paste(Image.new("RGB", (n, n), STAMP), (int(cx - c), int(cy - c)), m)


def disc(mask_size, cx, cy, r):
    m = Image.new("L", mask_size, 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    return m


def trefoil(n, rs):
    """Biohazard sign mask (as in M47): three crescents, a hole in the centre, a ring with gaps."""
    c = n / 2
    sz = (n, n)

    def crescents(grow):
        m = Image.new("L", sz, 0)
        for k in range(3):
            a = math.radians(90 + 120 * k)
            ca, sa = math.cos(a), -math.sin(a)
            big = disc(sz, c + ca * 0.42 * rs, c + sa * 0.42 * rs, (0.58 + grow) * rs)
            cut = disc(sz, c + ca * 0.63 * rs, c + sa * 0.63 * rs, (0.42 - grow) * rs)
            m = ImageChops.lighter(m, ImageChops.subtract(big, cut))
        return m
    body = crescents(0.0)
    halo = crescents(0.05)
    ring = ImageChops.subtract(disc(sz, c, c, 0.70 * rs), disc(sz, c, c, 0.60 * rs))
    ring = ImageChops.subtract(ring, halo)
    return ImageChops.subtract(ImageChops.lighter(body, ring), disc(sz, c, c, 0.15 * rs))


def paper_wear(img, rnd, edge_px, col=(214, 206, 184), spots=40):
    """Yellowing towards the edges and small stains: the paper is not new."""
    w, h = img.size
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    for i in range(edge_px):
        v = int(150 * (1 - i / edge_px) ** 2)
        d.rectangle([i, i, w - 1 - i, h - 1 - i], outline=v)
    for _ in range(spots):
        x, y, r = rnd.random() * w, rnd.random() * h, rnd.uniform(0.002, 0.012) * w
        d.ellipse([x - r, y - r, x + r, y + r], fill=int(rnd.uniform(25, 70)))
    m = m.filter(ImageFilter.GaussianBlur(edge_px * 0.25))
    return Image.composite(Image.new("RGB", (w, h), col), img, m)


# --- cover ----------------------------------------------------------------------------------------
def make_cover(ppm=4000):
    W, H = int(L.FW * ppm), int(L.FH * ppm)
    k = ppm / 1000.0                                       # px per mm

    def P(xm, ym):                                         # mm from the top left corner
        return xm * k, ym * k
    rnd = random.Random(62)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ink = (24, 30, 26, 215)
    lw = max(2, int(0.6 * k))
    for i in range(5):                                     # rules under the case title
        y = 146 + 11 * i
        d.line([P(62, y), P(166, y)], fill=ink, width=lw)
    for y, segs in ((232, ((62, 126), (131, 141))), (244, ((62, 126), (131, 141)))):
        for a, b in segs:
            d.line([P(a, y), P(b, y)], fill=ink, width=lw)
    # uneven print: the ink did not take in places
    a = img.split()[3]
    holes = Image.effect_noise((W, H), 60).point(lambda v: 0 if v < 40 else 255).filter(ImageFilter.GaussianBlur(0.6))
    img.putalpha(ImageChops.multiply(a, holes))
    save(img, "cover_print.png")

    hgt = Image.new("L", (W, H), 128)
    d = ImageDraw.Draw(hgt)
    # the binder bar under the board (raised), with prongs at the holes
    bx = (L.HOLE_X - L.X0) * 1000
    yc = L.FH * 500
    d.rectangle([P(bx - L.BAR_W * 500, yc - L.BAR_L * 500), P(bx + L.BAR_W * 500, yc + L.BAR_L * 500)], fill=176)
    for s in (-1, 1):
        x, y = P(bx, yc + s * L.HOLE_Y * 1000)
        d.ellipse([x - 4 * k, y - 6 * k, x + 4 * k, y + 6 * k], fill=196)
    hgt = hgt.filter(ImageFilter.GaussianBlur(2.2 * k))
    d = ImageDraw.Draw(hgt)
    for xm in (4.0, 9.0, 14.0):                            # spine creases (pressed in)
        d.line([P(xm, 0), P(xm, L.FH * 1000)], fill=78, width=max(1, int(0.7 * k)))
    # smoothed fold of the bottom right corner
    d.line([P(186, L.FH * 1000), P(L.FW * 1000, 268)], fill=104, width=max(1, int(0.8 * k)))
    hgt = hgt.filter(ImageFilter.GaussianBlur(0.35 * k))
    save(hgt, "cover_height.png")


# --- label ----------------------------------------------------------------------------------------
def make_label(ppm=8000):
    W, H = int(L.LABEL_S[0] * ppm), int(L.LABEL_S[1] * ppm)
    k = ppm / 1000.0
    rnd = random.Random(621)
    img = Image.new("RGB", (W, H), (240, 236, 220))
    img = paper_wear(img, rnd, int(3 * k), spots=25)
    d = ImageDraw.Draw(img)
    ink = (30, 34, 32)
    d.rectangle([2.5 * k, 2.5 * k, W - 2.5 * k, H - 2.5 * k], outline=ink, width=max(1, int(0.5 * k)))
    d.rectangle([3.6 * k, 3.6 * k, W - 3.6 * k, H - 3.6 * k], outline=ink, width=max(1, int(0.25 * k)))
    # biohazard sign on the left, short fields under it
    n = int(24 * k)
    sym = trefoil(n, n * 0.46)
    img.paste((150, 26, 22), (int(6 * k), int(7 * k)), sym)
    d.line([(6 * k, 37 * k), (30 * k, 37 * k)], fill=ink, width=max(1, int(0.35 * k)))
    d.line([(31 * k, 6 * k), (31 * k, H - 6 * k)], fill=ink, width=max(1, int(0.35 * k)))
    for y in (14, 26, 38, 50):                             # fields on the right
        d.line([(35 * k, y * k), (W - 6 * k, y * k)], fill=FORM_INK, width=max(1, int(0.3 * k)))
    hand(d, "017-04", 38 * k, 13 * k, 7 * k, rnd)
    hand(d, "12", 40 * k, 25 * k, 7 * k, rnd)
    hand(d, "3/7", 39 * k, 37 * k, 7 * k, rnd)
    hand(d, "6", 13 * k, 47 * k, 6 * k, rnd)
    stamp(img, 70 * k, 42 * k, 10 * k, rnd, 0.7)
    save(img, "label.png")


# --- form -----------------------------------------------------------------------------------------
def make_form(ppm=5000):
    W, H = int(L.SW * ppm), int(L.SH * ppm)
    k = ppm / 1000.0
    rnd = random.Random(623)
    img = Image.new("RGB", (W, H), PAPER)
    img = paper_wear(img, rnd, int(4 * k), col=(220, 212, 190), spots=30)
    d = ImageDraw.Draw(img)
    lw, lt = max(1, int(0.35 * k)), max(1, int(0.2 * k))

    def hl(y, a=20, b=195, w=lw):
        d.line([(a * k, y * k), (b * k, y * k)], fill=FORM_INK, width=w)

    def vl(x, a, b, w=lw):
        d.line([(x * k, a * k), (x * k, b * k)], fill=FORM_INK, width=w)
    # header: frame, number boxes, empty fields
    d.rectangle([20 * k, 14 * k, 195 * k, 58 * k], outline=FORM_INK, width=lw)
    for i in range(8):
        d.rectangle([(130 + 8 * i) * k, 20 * k, (137 + 8 * i) * k, 28 * k], outline=FORM_INK, width=lt)
    hand(d, "0", 131.5 * k, 27 * k, 6 * k, rnd)
    for i, ch in enumerate("01704"):
        hand(d, ch, (139.5 + 8 * i) * k, 27 * k, 6 * k, rnd)
    for y in (34, 42, 50):
        hl(y, 26, 190, lt)
    hand(d, "12", 40 * k, 33 * k, 5.5 * k, rnd)
    hand(d, "3", 120 * k, 41 * k, 5.5 * k, rnd)
    # results table
    cols = [20, 30, 74, 104, 134, 164, 195]
    top, rh, rows = 66, 8, 24
    bot = top + rh * (rows + 1)                            # 266 mm
    d.rectangle([20 * k, top * k, 195 * k, (top + rh) * k], fill=(212, 210, 204))
    for c in cols:
        vl(c, top, bot)
    for r in range(rows + 2):
        hl(top + rh * r, w=lw if r in (0, 1, rows + 1) else lt)
    for r in range(rows):
        y = top + rh * (r + 2) - 1.8
        if r in (17, 18):
            continue
        hand(d, "%02d" % (r + 1), 21.5 * k, y * k, 5 * k, rnd)
        v = rnd.choice(["%.2f" % rnd.uniform(0.1, 9.9), "%.1f" % rnd.uniform(10, 199), "%d" % rnd.randint(2, 480)])
        hand(d, v, 34 * k, y * k, 5 * k, rnd)
        hand(d, "%d-%d" % (rnd.randint(1, 30), rnd.randint(31, 160)), 77 * k, y * k, 4.5 * k, rnd)
        if rnd.random() < 0.3:
            hand(d, "+", 115 * k, y * k, 4.5 * k, rnd)
        hand(d, "%d" % rnd.randint(1, 9), 146 * k, y * k, 4.5 * k, rnd)
    # the bottom of the sheet shows from under the cover (20-30 mm, the right edge lower): total boxes with
    # digits, a signature flourish, a stamp, the form code as strokes
    for i in range(10):
        d.rectangle([(20 + 8 * i) * k, 275 * k, (28 + 8 * i) * k, 283 * k], outline=FORM_INK, width=lt)
        if i < 8:
            hand(d, str(rnd.randint(0, 9)), (22.2 + 8 * i) * k, 281.6 * k, 5.4 * k, rnd)
    hl(287, 118, 180, lt)
    squiggle(d, 124 * k, 285.5 * k, 34 * k, 6.5 * k, rnd, width=max(1, int(0.32 * k)))
    stamp(img, 166 * k, 279 * k, 11 * k, rnd, 0.8)
    for i in range(6):
        d.line([((20 + 1.6 * i) * k, 292 * k), ((20 + 1.6 * i) * k, 293.5 * k)], fill=FORM_INK, width=lt)
    save(img, "form.png")


# --- thermal tape ---------------------------------------------------------------------------------
def make_tape(ppm=10000):
    W, H = int(L.TAPE_W * ppm), int(L.TAPE_LEN * ppm)
    k = ppm / 1000.0
    rnd = random.Random(624)
    img = Image.new("RGB", (W, H), (240, 239, 232))
    d = ImageDraw.Draw(img)
    pitch = 0.30 * k                                       # dot pitch
    dot = 0.13 * k
    lh = 3.3 * k                                           # line pitch
    x0 = 4.4 * k

    def line(y, text, fade=1.0):
        for ci, ch in enumerate(text):
            rows = DOT5x7[ch].split()
            for ry, row in enumerate(rows):
                for rx, bit in enumerate(row):
                    if bit != "1" or rnd.random() > 0.97 * fade:
                        continue
                    cx = x0 + (ci * 6 + rx) * pitch
                    cy = y + ry * pitch
                    v = int(rnd.uniform(0.0, 0.25) * 200)
                    col = tuple(min(255, c + v) for c in THERMAL)
                    d.ellipse([cx - dot, cy - dot, cx + dot, cy + dot], fill=col)

    def num(lo, hi, nd):
        return ("%." + str(nd) + "f") % rnd.uniform(lo, hi)
    y = 5.0 * k                                            # the head of the printout is the free end
    sample = 17
    while y < H - 8 * k:
        block = ["=" * 24, " %03d-%02d          %02d:%02d" % (sample, rnd.randint(1, 12), rnd.randint(8, 18),
                                                            rnd.randint(0, 59)), "-" * 24]
        for t in range(rnd.randint(5, 7)):
            lo = rnd.uniform(0.2, 40)
            hi = lo * rnd.uniform(1.3, 2.2)
            v = rnd.uniform(lo * 0.7, hi * 1.25)
            flag = "*" if v < lo or v > hi else " "
            nd = 2 if hi < 10 else 1
            block.append(" %02d %7s %s %s-%s" % (t + 1, num(v, v, nd), flag, num(lo, lo, nd), num(hi, hi, nd))[:24])
        block.append("-" * 24)
        bars = "".join(rnd.choice("#  ##  ###  #  ") for _ in range(24))[:24]
        block += [bars, " " * 24]
        for text in block:
            if y > H - 8 * k:
                break
            line(y, text.ljust(24)[:24], fade=rnd.uniform(0.85, 1.0))
            y += lh
        y += 2.0 * k
        sample += 1
    # thermal head traces: a dull lengthwise streak where the print is paler
    m = Image.new("L", (W, H), 0)
    sx = int(rnd.uniform(0.3, 0.7) * W)
    ImageDraw.Draw(m).rectangle([sx, 0, sx + int(0.5 * k), H], fill=150)
    m = m.filter(ImageFilter.GaussianBlur(0.4 * k))
    img = Image.composite(Image.new("RGB", (W, H), (236, 235, 228)), img, m)
    save(img, "tape.png")


if __name__ == "__main__":
    make_cover()
    make_label()
    make_form()
    make_tape()
