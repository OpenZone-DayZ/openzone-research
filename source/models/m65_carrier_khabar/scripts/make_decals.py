"""Images for the M65 "Khabar" carrier (system Python + Pillow), without letters: hand-drawn squiggles,
digits, a radiation sign, ruling.

    python make_decals.py      -> ../work/*.png

- sheets.png - all six sheets of the stack side by side, in the SLOT_W x SLOT_H cells (m65_layout):
  pad ruling (5 mm squares or 7 mm rules), a glue strip from the pad binding at the top, handwriting:
  on the top sheet a buyer's "price list": a title with an underline and a date in digits, lines made
  of a number, squiggles for the name, a dot leader, two columns of prices on the right (what he buys
  at / what he sells at), edits - crossed-out prices with new ones above them, red ticks, sections, a
  radiation sign at a couple of lines, pencil notes; the lower sheets continue the list in different
  ink, s3 has a total at the bottom with a double underline and a flourish. Wear: yellowing towards
  the edges, stains, a mug ring, a greasy fingerprint at the corner, rust from the clip jaws. RGBA:
  transparent outside the sheets.
- board_print.png - the front of the backing board (BW x BH): a remnant of the old folder's printed
  rules at the original corner, on the visible strip at the bottom a pen tested with a spiral, tally
  sticks and a digit in a circle.

The squiggles are chains of handwritten loops and humps smoothed with a spline, slanted and jittery:
they look like fluent handwriting, but not a single letter can be read. The digits are our own strokes
(as in M62): the image does not depend on system fonts. Sizes come from m65_layout.py (shared with
build_m65.py).
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m65_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
PPM = 6000                         # px per metre of the sheet image (6 px/mm)
K = PPM / 1000.0                   # px per mm

INKS = {
    "blue": ((34, 48, 128), 0.93),        # ballpoint pen
    "violet": ((86, 46, 124), 0.90),      # violet ink
    "black": ((30, 30, 36), 0.92),
    "pencil": ((84, 84, 92), 0.62),       # graphite
    "red": ((168, 38, 32), 0.85),         # red pencil
}
GRID = (168, 186, 206)
LINE = (160, 180, 210)
MARGIN = (214, 104, 104)


def save(img, name):
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, img.size)


# --- handwritten digits (from M62): strokes in a 0.6 x 1 cell, y down -----------------------------
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


def digits_width(text, h):
    return sum(h * 0.5 if ch == " " else h * (0.32 if ch == "." else 0.78) for ch in text)


def hand(d, text, x, y, h, rnd, width, slant=0.16):
    """Handwritten digits: the string text from the bottom left corner (x, y), height h (px). Returns the
    right edge."""
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
                pts.append((cx + (px + jx) * hh + (1 - py) * slant * hh, y - hh + (py + jy) * hh + dy))
            d.line(pts, fill=255, width=width, joint="curve")
        cx += hh * (0.32 if ch == "." else 0.78) * rnd.uniform(0.92, 1.08)
    return cx


# --- squiggles ------------------------------------------------------------------------------------
# "letters" of fluent handwriting: points (shift from the letter start, height) in fractions of the
# lowercase height; 0 is the baseline
GLYPHS = {
    "n": [(0.10, 1.0), (0.42, 0.95), (0.60, 0.0)],
    "m": [(0.08, 1.0), (0.28, 0.9), (0.36, 0.0), (0.48, 1.0), (0.68, 0.9), (0.78, 0.0)],
    "u": [(0.08, 1.0), (0.20, 0.05), (0.46, 0.9), (0.54, 0.0)],
    "e": [(0.40, 0.70), (0.28, 1.0), (0.12, 0.55), (0.30, 0.0), (0.56, 0.25)],
    "o": [(0.35, 1.0), (0.12, 0.55), (0.30, 0.0), (0.52, 0.55), (0.36, 1.0), (0.62, 0.85)],
    "l": [(0.30, 2.2), (0.16, 2.0), (0.20, 0.0), (0.42, 0.3)],
    "b": [(0.30, 2.1), (0.15, 1.9), (0.18, 0.0), (0.45, 0.6), (0.30, 1.0), (0.55, 0.9)],
    "g": [(0.35, 1.0), (0.12, 0.55), (0.32, 0.1), (0.48, 1.0), (0.44, -1.1), (0.24, -0.9), (0.52, 0.2)],
    "a": [(0.40, 0.95), (0.12, 0.6), (0.28, 0.0), (0.50, 0.7), (0.50, 0.95), (0.56, 0.0)],
    "r": [(0.10, 1.0), (0.25, 0.80), (0.40, 1.0), (0.45, 0.0)],
    "s": [(0.25, 1.0), (0.45, 0.4), (0.12, 0.0)],
    "t": [(0.25, 1.8), (0.22, 0.0), (0.45, 0.2)],
    "d": [(0.40, 0.95), (0.12, 0.6), (0.28, 0.0), (0.50, 0.7), (0.52, 2.1), (0.56, 0.0)],
    "y": [(0.10, 1.0), (0.24, 0.05), (0.48, 1.0), (0.40, -1.1), (0.20, -0.9), (0.55, 0.2)],
    "w": [(0.08, 1.0), (0.18, 0.0), (0.32, 0.8), (0.45, 0.0), (0.60, 1.0)],
    "z": [(0.10, 1.0), (0.45, 0.95), (0.10, 0.0), (0.45, -0.8), (0.30, -0.9), (0.55, 0.1)],
}
WIDE = 1.45                        # fluent handwriting is wider than "printed" loops
WEIGHTS = {"n": 5, "m": 3, "u": 4, "e": 5, "o": 4, "l": 2, "b": 1.2, "g": 1.2, "a": 4, "r": 3, "s": 2,
           "t": 2, "d": 1.5, "y": 1.2, "w": 1.5, "z": 0.6}


def catmull(pts, sub=4):
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(0, i - 1)], pts[i], pts[i + 1]
        p3 = pts[min(len(pts) - 1, i + 2)]
        for k in range(sub):
            t = k / sub
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2
                                    + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in (0, 1)))
    out.append(pts[-1])
    return out


def scribble(d, x, y, xh, n, rnd, width, slant=0.32, sloppy=1.0):
    """A word in squiggles: n "letters" from the left edge x on the line y (px), lowercase height xh.
    Returns the right edge."""
    keys = list(WEIGHTS)
    pts = [(x - 0.15 * xh, y - 0.15 * xh)]
    cx = x
    marks = []
    wave_a, wave_f = rnd.uniform(0.05, 0.16) * xh, rnd.uniform(0.15, 0.4) / xh
    for i in range(n):
        g = rnd.choices(keys, [WEIGHTS[k] for k in keys])[0]
        sc = rnd.uniform(0.75, 1.25) * xh
        wk = rnd.uniform(0.65, 1.2) * (1.0 - 0.2 * sloppy * rnd.random())
        base = y + wave_a * math.sin((cx - x) * wave_f)          # the baseline wanders
        for dx, hy in GLYPHS[g]:
            hy = hy * rnd.uniform(0.7, 1.15) if hy > 0 else hy * rnd.uniform(0.7, 1.1)
            pts.append((cx + dx * sc * wk * WIDE + rnd.uniform(-0.08, 0.08) * xh, base - hy * sc))
        if g == "t" or (g in "nu" and rnd.random() < 0.15):
            marks.append((cx + 0.05 * sc, y - 1.25 * sc, cx + 0.55 * sc, y - 1.35 * sc))
        cx += GLYPHS[g][-1][0] * sc * wk * WIDE + 0.06 * xh
    pts.append((cx + 0.2 * xh, y - 0.35 * xh))
    smooth = catmull(pts)
    sl = slant * rnd.uniform(0.8, 1.3)
    q = [(px + (y - py) * sl + rnd.uniform(-0.05, 0.05) * xh, py + rnd.uniform(-0.05, 0.05) * xh)
         for px, py in smooth]
    d.line(q, fill=255, width=width, joint="curve")
    for x0, y0, x1, y1 in marks:
        d.line([(x0 + (y - y0) * slant, y0), (x1 + (y - y1) * slant, y1)], fill=255, width=width)
    return cx + 0.2 * xh


def phrase(d, x, y, xh, words, rnd, width, **kw):
    for n in words:
        x = scribble(d, x, y, xh, n, rnd, width, **kw) + rnd.uniform(0.7, 1.1) * xh
    return x


def wavy(d, x0, x1, y, rnd, width, amp=0.4):
    pts = []
    n = max(3, int((x1 - x0) / (2.5 * K)))
    for i in range(n + 1):
        t = i / n
        pts.append((x0 + (x1 - x0) * t, y + math.sin(t * 9.0 + rnd.random()) * amp * K + rnd.uniform(-0.2, 0.2) * K))
    d.line(pts, fill=255, width=width, joint="curve")


def check(d, x, y, s, width):
    d.line([(x, y - 0.45 * s), (x + 0.35 * s, y), (x + 1.0 * s, y - 1.1 * s)], fill=255, width=width, joint="curve")


def trefoil(d, cx, cy, r, width):
    """Hand-drawn radiation sign: a small circle and three sectors in outline, a dot in the centre."""
    d.ellipse([cx - r * 0.18, cy - r * 0.18, cx + r * 0.18, cy + r * 0.18], fill=255)
    for k in range(3):
        a0 = math.radians(-90 + 120 * k - 30)
        a1 = math.radians(-90 + 120 * k + 30)
        pts = [(cx + r * 0.3 * math.cos(a0), cy + r * 0.3 * math.sin(a0))]
        for j in range(7):
            a = a0 + (a1 - a0) * j / 6
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        pts.append((cx + r * 0.3 * math.cos(a1), cy + r * 0.3 * math.sin(a1)))
        d.polygon(pts, fill=255)


def price(rnd, big=False):
    v = rnd.choice([50, 80, 100, 120, 150, 200, 250, 300, 350, 400, 500, 600, 700, 800, 900, 1000, 1200, 1500,
                    2000, 2500, 3000, 4000, 5000, 7000])
    if big:
        v *= rnd.choice([1, 2, 3, 5])
    s = str(v)
    r = rnd.random()
    if r < 0.25:
        s += "-"
    elif r < 0.35:
        s += ".00"
    return s


# --- sheet ----------------------------------------------------------------------------------------
class Sheet:
    """Drawing on sheet s in the shared image: coordinates are mm from the top left corner of the sheet."""

    def __init__(self, canvas, inks, s):
        self.s, self.canvas, self.inks = s, canvas, inks
        self.ox = (s["slot"] + 0.5) * L.SLOT_W * PPM - L.SW / 2 * PPM
        self.oy = (L.SLOT_H / 2 - L.SH / 2) * PPM
        self.d = {k: ImageDraw.Draw(m) for k, m in inks.items()}
        self.base = ImageDraw.Draw(canvas)

    def P(self, xm, ym):
        return self.ox + xm * K, self.oy + ym * K

    def box(self):
        return (int(self.ox), int(self.oy), int(self.ox + L.SW * PPM), int(self.oy + L.SH * PPM))


def ruling(sh, rnd):
    d = sh.base
    s = sh.s
    w = max(1, int(0.16 * K))
    if s["rule"] == "grid":
        x0, x1, y0, y1 = 4.0, 144.0, 6.0, 206.0
        x = x0
        while x <= x1 + 0.01:
            d.line([sh.P(x, y0), sh.P(x, y1)], fill=GRID, width=w)
            x += 5.0
        y = y0
        while y <= y1 + 0.01:
            d.line([sh.P(x0, y), sh.P(x1, y)], fill=GRID, width=w)
            y += 5.0
    else:
        y = 15.0
        while y <= 205.0:
            d.line([sh.P(0, y), sh.P(L.SW * 1000, y)], fill=LINE, width=w)
            y += 7.0
        d.line([sh.P(14.0, 0), sh.P(14.0, L.SH * 1000)], fill=MARGIN, width=w)
    # glue strip from the pad binding at the top: yellower, with ragged remnants
    for i in range(int(2.4 * K)):
        a = 1.0 - i / (2.4 * K)
        col = (int(206 + 20 * (1 - a)), int(196 + 22 * (1 - a)), int(160 + 40 * (1 - a)))
        x = 0
        while x < L.SW * 1000:
            seg = rnd.uniform(2, 9)
            if rnd.random() < 0.75 + 0.2 * a:
                d.line([sh.P(x, i / K), sh.P(x + seg, i / K)], fill=col, width=1)
            x += seg


def price_list(sh, rnd, ink, rows, y0, step, xh, two_cols=True, header=True, num_start=1, red=True,
               rad_rows=(), cross_rows=(), pencil_tail=True):
    """A column "name ..... price [price]" from y0 (mm) with pitch step."""
    d = sh.d[ink]
    w = max(1, int(0.34 * K))
    y = y0
    if header:
        x = phrase(d, *sh.P(24, y), xh * K * 1.25, [rnd.randint(5, 8), rnd.randint(4, 7)], rnd, w + 1, slant=0.28)
        wavy(d, sh.P(22, 0)[0], x, sh.P(0, y + 1.6)[1], rnd, w)
        wavy(d, sh.P(26, 0)[0], x - 4 * K, sh.P(0, y + 2.6)[1], rnd, w)
        hand(d, "%02d.%02d" % (rnd.randint(1, 28), rnd.randint(1, 12)), *sh.P(116, y - 0.5), 3.4 * K, rnd, w)
        y += step * 1.6
    n = num_start
    for r in range(rows):
        if r in (7, 15) and header:                       # section: a rule and a subheading
            d.line([sh.P(8, y - step * 0.55), sh.P(140, y - step * 0.5)], fill=255, width=w)
            x = phrase(d, *sh.P(40, y), xh * K * 1.1, [rnd.randint(4, 7), rnd.randint(3, 6)], rnd, w, slant=0.3)
            wavy(d, sh.P(38, 0)[0], x, sh.P(0, y + 1.4)[1], rnd, w, amp=0.25)
            y += step * 1.25
        hand(d, "%d." % n, *sh.P(5.0 if n < 10 else 3.6, y), 2.9 * K, rnd, w)
        xend = phrase(d, *sh.P(13, y), xh * K, [rnd.randint(3, 8) for _ in range(rnd.choice((1, 2, 2, 3)))], rnd, w)
        col1, col2 = (103.0, 140.0) if two_cols else (138.0, None)
        p1 = price(rnd, big=r % 5 == 2)
        x1 = sh.P(col1, 0)[0] - digits_width(p1, 2.9 * K)
        xd = xend + 1.4 * K                                # dot leader
        while xd < x1 - 1.6 * K:
            dd = 0.17 * K
            yy = sh.P(0, y - 0.15)[1] + rnd.uniform(-0.2, 0.2) * K
            d.ellipse([xd - dd, yy - dd, xd + dd, yy + dd], fill=255)
            xd += rnd.uniform(1.8, 2.3) * K
        if r in cross_rows:                                # the old price is crossed out, the new one above it
            xe = hand(d, p1, x1, sh.P(0, y)[1], 2.9 * K, rnd, w)
            d.line([(x1 - 0.5 * K, sh.P(0, y - 1.3)[1]), (xe + 0.5 * K, sh.P(0, y - 1.6)[1])], fill=255, width=w)
            p1b = price(rnd)
            dr = sh.d["red"] if red else d
            hand(dr, p1b, x1 + 1.5 * K, sh.P(0, y - 3.6)[1], 2.4 * K, rnd, w)
        else:
            hand(d, p1, x1, sh.P(0, y)[1], 2.9 * K, rnd, w)
        if col2:
            p2 = price(rnd, big=r % 5 == 2)
            hand(d, p2, sh.P(col2, 0)[0] - digits_width(p2, 2.9 * K), sh.P(0, y)[1], 2.9 * K, rnd, w)
        if r in rad_rows:
            trefoil(d, *sh.P(10.0 + (xend - sh.P(10.0, 0)[0]) / K + 3.0, y - 1.6), 1.7 * K, w)
        if red and rnd.random() < 0.3:
            check(sh.d["red"], *sh.P(0.8, y - 0.3), 2.4 * K, w + 1)
        y += step
        n += 1
        if y > 203:
            break
    if pencil_tail and y < 196:                            # pencil notes
        dp = sh.d["pencil"]
        for k in range(2):
            phrase(dp, *sh.P(16, y + 1), xh * K * 0.95, [rnd.randint(3, 7) for _ in range(rnd.randint(2, 4))], rnd,
                   w + 1, slant=0.22)
            hand(dp, price(rnd), *sh.P(118, y + 1), 2.8 * K, rnd, w + 1)
            y += step
    return y


def wear(canvas, sh, rnd, edge_mm=5.0, spots=30, col=(214, 204, 178), strength=150):
    """Yellowing towards the edges and stains within the sheet."""
    x0, y0, x1, y1 = sh.box()
    w, h = x1 - x0, y1 - y0
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    e = int(edge_mm * K)
    for i in range(e):
        d.rectangle([i, i, w - 1 - i, h - 1 - i], outline=int(strength * (1 - i / e) ** 2))
    for _ in range(spots):
        x, y, r = rnd.random() * w, rnd.random() * h, rnd.uniform(0.3, 1.6) * K
        d.ellipse([x - r, y - r, x + r, y + r], fill=int(rnd.uniform(25, 70)))
    m = m.filter(ImageFilter.GaussianBlur(e * 0.25))
    canvas.paste(Image.new("RGB", (w, h), col), (x0, y0), m)


def coffee_ring(canvas, sh, cx, cy, r, rnd):
    x0, y0, x1, y1 = sh.box()
    w, h = x1 - x0, y1 - y0
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    px, py = (cx * K, cy * K)
    for k in range(120):
        a = 2 * math.pi * k / 120
        if 0.6 < a < 1.6:                                  # the ring is not closed
            continue
        rr = r * K * (1 + 0.012 * math.sin(a * 5) + rnd.uniform(-0.004, 0.004))
        d.ellipse([px + rr * math.cos(a) - 1.2 * K, py + rr * math.sin(a) - 1.2 * K,
                   px + rr * math.cos(a) + 1.2 * K, py + rr * math.sin(a) + 1.2 * K], fill=55)
    d.ellipse([px - r * K, py - r * K, px + r * K, py + r * K], outline=110, width=int(0.4 * K))
    inner = Image.new("L", (w, h), 0)
    ImageDraw.Draw(inner).ellipse([px - r * K, py - r * K, px + r * K, py + r * K], fill=12)
    m = ImageChops.lighter(m.filter(ImageFilter.GaussianBlur(0.5 * K)), inner.filter(ImageFilter.GaussianBlur(2 * K)))
    canvas.paste(Image.new("RGB", (w, h), (150, 104, 60)), (x0, y0), m)


def thumbprint(canvas, sh, cx, cy, rnd, col=(118, 104, 86), alpha=55):
    """Greasy fingerprint: ridge arcs in an ellipse."""
    x0, y0, x1, y1 = sh.box()
    w, h = x1 - x0, y1 - y0
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    px, py = cx * K, cy * K
    rot = rnd.uniform(-0.6, 0.6)
    for i in range(1, 16):
        rx, ry = i * 0.55 * K, i * 0.72 * K
        pts = []
        for k in range(41):
            a = 2 * math.pi * k / 40
            ex, ey = rx * math.cos(a), ry * math.sin(a)
            pts.append((px + ex * math.cos(rot) - ey * math.sin(rot), py + ex * math.sin(rot) + ey * math.cos(rot)))
        d.line(pts, fill=alpha, width=max(1, int(0.2 * K)))
    fade = Image.new("L", (w, h), 0)
    ImageDraw.Draw(fade).ellipse([px - 7 * K, py - 9 * K, px + 7 * K, py + 9 * K], fill=255)
    m = ImageChops.multiply(m, fade.filter(ImageFilter.GaussianBlur(2.5 * K)))
    canvas.paste(Image.new("RGB", (w, h), col), (x0, y0), m)


def clip_rust(canvas, sh, rnd):
    """Rust from the clip jaws: two brown marks at the curls and a strip along the jaw."""
    x0, y0, x1, y1 = sh.box()
    w, h = x1 - x0, y1 - y0
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    yj = (L.Y_TOP - L.CY_J) * 1000                          # jaw line, mm from the top of the sheet
    xc = L.SW * 500 - sh.s["c"][0] * 1000
    for sgn in (-1, 1):
        cx = xc + sgn * (L.CW * 500 - 3.0)
        for _ in range(12):
            r = rnd.uniform(0.3, 1.1) * K
            x, y = (cx + rnd.uniform(-2.5, 2.5)) * K, (yj + rnd.uniform(-0.8, 0.6)) * K
            d.ellipse([x - r, y - r, x + r, y + r], fill=int(rnd.uniform(60, 140)))
    d.line([((xc - 14) * K, yj * K), ((xc + 14) * K, yj * K)], fill=28, width=int(0.6 * K))
    m = m.filter(ImageFilter.GaussianBlur(0.4 * K))
    canvas.paste(Image.new("RGB", (w, h), (138, 70, 30)), (x0, y0), m)


def make_sheets():
    W, H = int(L.SLOT_W * L.N_SHEETS * PPM), int(L.SLOT_H * PPM)
    canvas = Image.new("RGB", (W, H), (236, 233, 222))
    alpha = Image.new("L", (W, H), 0)
    inks = {k: Image.new("L", (W, H), 0) for k in INKS}
    papers = {"s1": (234, 232, 220), "s2": (238, 236, 228), "s3": (232, 228, 212), "s4": (236, 234, 224),
              "s5": (235, 232, 219), "top": (238, 235, 224)}
    sheets = {}
    for s in L.SHEETS:
        sh = Sheet(canvas, inks, s)
        sheets[s["name"]] = sh
        ImageDraw.Draw(canvas).rectangle(sh.box(), fill=papers[s["name"]])
        ImageDraw.Draw(alpha).rectangle(sh.box(), fill=255)
        rnd = random.Random(650 + s["slot"])
        ruling(sh, rnd)
    # handwriting: the top sheet is the price list, below it the continuation in different ink
    price_list(sheets["top"], random.Random(6501), "blue", 22, 22.0, 8.2, 2.3, rad_rows=(4, 12),
               cross_rows=(2, 9, 13))
    price_list(sheets["s5"], random.Random(6502), "violet", 22, 18.0, 8.6, 2.4, header=False, num_start=24,
               rad_rows=(6,), cross_rows=(16,))
    price_list(sheets["s4"], random.Random(6503), "violet", 20, 14.0, 9.0, 2.5, num_start=1, red=False)
    y = price_list(sheets["s3"], random.Random(6504), "blue", 19, 22.0, 7.0, 2.2, header=False, num_start=46,
                   two_cols=False, cross_rows=(3,), pencil_tail=False)
    # total at the bottom of s3 (visible from under the stack): a double rule, the sum, a flourish, a tick
    sh3, rnd = sheets["s3"], random.Random(6505)
    d3 = sh3.d["blue"]
    w = max(1, int(0.34 * K))
    yt = 205.5                                             # s3 is lowered by 10.5 mm: its bottom ~10 mm shows
    d3.line([sh3.P(84, yt - 5.3), sh3.P(141, yt - 5.6)], fill=255, width=w)
    d3.line([sh3.P(84, yt - 4.4), sh3.P(141, yt - 4.7)], fill=255, width=w)
    hand(d3, "12 450", *sh3.P(108, yt), 3.4 * K, rnd, w + 1)
    phrase(d3, *sh3.P(20, yt - 0.5), 2.4 * K, [5, 3], rnd, w)
    xs = scribble(d3, *sh3.P(58, yt + 0.5), 2.8 * K, 6, rnd, w, slant=0.45)
    d3.line([(xs, sh3.P(0, yt - 0.2)[1]), (xs + 8 * K, sh3.P(0, yt - 2.6)[1])], fill=255, width=w)
    check(sh3.d["red"], *sh3.P(94, yt + 0.5), 3.0 * K, w + 1)
    price_list(sheets["s2"], random.Random(6506), "black", 24, 22.0, 7.0, 2.2, header=False, num_start=12,
               two_cols=False, red=False, pencil_tail=False)
    price_list(sheets["s1"], random.Random(6507), "pencil", 20, 16.0, 9.0, 2.4, red=False, pencil_tail=False)
    # ink onto the paper: ballpoint and ink with uneven pressure, graphite grainy
    grain = Image.effect_noise((W, H), 70).point(lambda v: min(255, max(0, int((v - 40) * 1.6))))
    for name, (col, op) in INKS.items():
        m = inks[name].filter(ImageFilter.GaussianBlur(0.35))
        if name == "pencil":
            m = ImageChops.multiply(m, grain)
        m = m.point(lambda v, op=op: int(v * op))
        canvas.paste(Image.new("RGB", (W, H), col), (0, 0), m)
    # wear over the handwriting
    for name, sh in sheets.items():
        rnd = random.Random(660 + sh.s["slot"])
        wear(canvas, sh, rnd, spots=24 if name == "top" else 12)
    top = sheets["top"]
    coffee_ring(canvas, top, 128.0, 52.0, 34.0, random.Random(6601))
    thumbprint(canvas, top, 132.0, 196.0, random.Random(6602))
    thumbprint(canvas, top, 14.0, 172.0, random.Random(6603), alpha=45)
    clip_rust(canvas, top, random.Random(6604))
    img = canvas.convert("RGBA")
    img.putalpha(alpha)
    save(img, "sheets.png")


# --- backing board --------------------------------------------------------------------------------
def make_board(ppm=4000):
    W, H = int(L.BW * ppm), int(L.BH * ppm)
    k = ppm / 1000.0

    def P(xm, ym):                                         # mm from the top left corner of the board
        return xm * k, ym * k
    rnd = random.Random(6510)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # remnant of the old folder's print at the original (top right) corner: two rules
    ink = (34, 26, 18, 190)
    for y in (14.0, 22.0):
        d.line([P(L.BW * 1000 - 34, y), P(L.BW * 1000 - 4, y)], fill=ink, width=max(2, int(0.6 * k)))
    # visible strip at the bottom: a pen was tested with a spiral, tally sticks, a digit in a circle
    pen = (36, 52, 140, 230)
    w = max(2, int(0.4 * k))
    yb = L.BH * 1000 - 10.0
    cx, cy = 26.0, yb
    pts = []
    for i in range(160):
        a = i * 0.32
        r = 0.6 + i * 0.045
        pts.append(P(cx + r * math.cos(a) * 1.3, cy + r * math.sin(a)))
    d.line(pts, fill=pen, width=w, joint="curve")
    d.line([P(36, yb + 2), P(44, yb - 3), P(52, yb + 3), P(60, yb - 2)], fill=pen, width=w, joint="curve")
    x = 98.0
    for gi in range(2):
        for j in range(5 if gi == 0 else 3):
            d.line([P(x + rnd.uniform(-0.2, 0.2), yb - 3.2), P(x + rnd.uniform(-0.4, 0.4), yb + 3.0)], fill=pen, width=w)
            x += 2.0
        if gi == 0:
            d.line([P(x - 11.5, yb + 2.0), P(x - 0.5, yb - 2.2)], fill=pen, width=w)
        x += 3.5
    d.ellipse([P(134, yb - 5), P(144, yb + 5)], outline=pen, width=w)
    m = Image.new("L", (W, H), 0)
    hand(ImageDraw.Draw(m), "7", *P(136.6, yb + 3.2), 6.0 * k, rnd, w)
    img.paste(Image.new("RGBA", (W, H), pen), (0, 0), m)
    a = img.split()[3]
    holes = Image.effect_noise((W, H), 60).point(lambda v: 0 if v < 36 else 255).filter(ImageFilter.GaussianBlur(0.6))
    img.putalpha(ImageChops.multiply(a, holes))
    save(img, "board_print.png")


if __name__ == "__main__":
    make_sheets()
    make_board()
