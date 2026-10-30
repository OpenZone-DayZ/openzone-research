"""Images for the M68 "Protection" carrier (system Python + Pillow), without letters: digits, fields,
scales, pictograms, signature squiggles, a stamp without text, a map without captions.

    python make_decals.py      -> ../work/*.png

- protocol.png - an A5 (148 x 210) test protocol form: a grey stripe of the "Protection" line on top
  (like the M53 sample tag), empty header fields with squiggles, a number and a date in digits, a
  "bullet - plate" pictogram instead of a title, a plate firing diagram with hit points 1-6 and
  dimensions, a "penetration fraction - velocity" graph with scales, a table of 7 fields x 8 rows
  (field numbers in digits, hand-written data in blue ballpoint: distance, velocity, angle,
  penetration +/-, dent depth), the penetration circled in red pencil, signature flourishes and a
  violet round stamp without text. Folded in half, slight yellowing, stains. RGBA: transparent outside
  the sheet.
- copy.png - the second sheet under the protocol: a carbon copy on thin paper (the left edge is visible).
- map.png - the map under the celluloid of the window (around the protocol): topographic, without
  captions - contour lines, forest, river, lake, roads, a settlement, a kilometre grid, elevation marks
  in digits, the officer's marks in red and blue pencil, folds.
- cell_scr.png - scratches, wear and cracks of the celluloid (L, 0..255).
- leather_print.png - the layout from above (model coordinates): stitching on the leather (leaf, window
  frame, front wall, pocket, pencil holder tacks, tab, strap), stitching on the suede of the flap, a
  stamp on the suede (a frame with lines and size digits), the lock rivets.
- sheet2.png - the corner of the second sheet from under the flap: the same form (grey stripe, fields,
  digits).

The digits are our own strokes (as in M62, M65): the images do not depend on system fonts. Sizes come
from m68_layout.py (shared with build_m68.py).
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m68_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))

PRINT = (52, 52, 58)              # printing ink of the form
BLUE = (34, 48, 126)              # ballpoint pen
RED = (176, 40, 34)               # red pencil
VIOLET = (96, 62, 150)            # stamp ink
CARBON = (62, 58, 150)            # carbon paper
LINE_GREY = (112, 112, 110)       # colour of the "Protection" line (the stripe of the M53 tag)


def save(img, name):
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, img.size)


# --- digits (from M62/M65): strokes in a 0.6 x 1 cell, y down -------------------------------------
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
    ",": [[(0.30, 0.90), (0.20, 1.12)]],
}


def adv(ch, h):
    return h * 0.5 if ch == " " else h * (0.32 if ch in ".," else 0.78)


def text_w(text, h):
    return sum(adv(ch, h) for ch in text)


def digits(d, text, x, y, h, width, rnd=None, slant=0.16, jitter=0.03):
    """Digits: a string from the bottom left corner (x, y), height h (px). rnd=None gives even strokes
    (print)."""
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
            d.line(pts, fill=255, width=width, joint="curve")
        cx += adv(ch, hh) * (rnd.uniform(0.92, 1.08) if rnd else 1.0)
    return cx


# --- squiggles for signatures and fields (from M65) -----------------------------------------------
GLYPHS = {
    "n": [(0.10, 1.0), (0.42, 0.95), (0.60, 0.0)],
    "m": [(0.08, 1.0), (0.28, 0.9), (0.36, 0.0), (0.48, 1.0), (0.68, 0.9), (0.78, 0.0)],
    "u": [(0.08, 1.0), (0.20, 0.05), (0.46, 0.9), (0.54, 0.0)],
    "e": [(0.40, 0.70), (0.28, 1.0), (0.12, 0.55), (0.30, 0.0), (0.56, 0.25)],
    "o": [(0.35, 1.0), (0.12, 0.55), (0.30, 0.0), (0.52, 0.55), (0.36, 1.0), (0.62, 0.85)],
    "l": [(0.30, 2.2), (0.16, 2.0), (0.20, 0.0), (0.42, 0.3)],
    "a": [(0.40, 0.95), (0.12, 0.6), (0.28, 0.0), (0.50, 0.7), (0.50, 0.95), (0.56, 0.0)],
    "r": [(0.10, 1.0), (0.25, 0.80), (0.40, 1.0), (0.45, 0.0)],
    "s": [(0.25, 1.0), (0.45, 0.4), (0.12, 0.0)],
    "d": [(0.40, 0.95), (0.12, 0.6), (0.28, 0.0), (0.50, 0.7), (0.52, 2.1), (0.56, 0.0)],
    "y": [(0.10, 1.0), (0.24, 0.05), (0.48, 1.0), (0.40, -1.1), (0.20, -0.9), (0.55, 0.2)],
}
WEIGHTS = {"n": 5, "m": 3, "u": 4, "e": 5, "o": 4, "l": 2, "a": 4, "r": 3, "s": 2, "d": 1.5, "y": 1.2}


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


def scribble(d, x, y, xh, n, rnd, width, slant=0.32):
    """A word in squiggles (n "letters") from the left edge x on the line y, lowercase height xh (px)."""
    keys = list(WEIGHTS)
    pts = [(x - 0.15 * xh, y - 0.15 * xh)]
    cx = x
    wave_a, wave_f = rnd.uniform(0.05, 0.16) * xh, rnd.uniform(0.15, 0.4) / xh
    for _ in range(n):
        g = rnd.choices(keys, [WEIGHTS[k] for k in keys])[0]
        sc = rnd.uniform(0.75, 1.25) * xh
        wk = rnd.uniform(0.65, 1.2)
        base = y + wave_a * math.sin((cx - x) * wave_f)
        for dx, hy in GLYPHS[g]:
            hy = hy * rnd.uniform(0.7, 1.15)
            pts.append((cx + dx * sc * wk * 1.45 + rnd.uniform(-0.08, 0.08) * xh, base - hy * sc))
        cx += GLYPHS[g][-1][0] * sc * wk * 1.45 + 0.06 * xh
    pts.append((cx + 0.2 * xh, y - 0.35 * xh))
    sl = slant * rnd.uniform(0.8, 1.3)
    q = [(px + (y - py) * sl, py) for px, py in catmull(pts)]
    d.line(q, fill=255, width=width, joint="curve")
    return cx + 0.2 * xh


def signature(d, x, y, xh, rnd, width):
    """Flourish: squiggles and a loop with a long tail."""
    xe = scribble(d, x, y, xh, rnd.randint(4, 6), rnd, width, slant=0.5)
    tail = [(xe, y - 0.3 * xh), (xe + 2.5 * xh, y - 1.8 * xh), (xe + 1.2 * xh, y + 0.4 * xh),
            (x - 0.5 * xh, y + 0.6 * xh), (x - 1.2 * xh, y + 0.1 * xh)]
    d.line(catmull(tail), fill=255, width=width, joint="curve")


# --- canvas in millimetres ------------------------------------------------------------------------
class Sheet:
    """A w x h mm sheet, ppmm px per mm, ink layers (L) per colour; coordinates are mm from the top left."""

    def __init__(self, w, h, ppmm, paper, inks):
        self.k = ppmm
        self.W, self.H = int(round(w * ppmm)), int(round(h * ppmm))
        self.img = Image.new("RGB", (self.W, self.H), paper)
        self.base = ImageDraw.Draw(self.img)
        self.inks = {name: Image.new("L", (self.W, self.H), 0) for name in inks}
        self.cols = inks
        self.d = {name: ImageDraw.Draw(m) for name, m in self.inks.items()}

    def P(self, x, y):
        return x * self.k, y * self.k

    def w(self, mm):
        return max(1, int(round(mm * self.k)))

    def line(self, ink, pts, mm=0.2):
        self.d[ink].line([self.P(*p) for p in pts], fill=255, width=self.w(mm), joint="curve")

    def rect(self, ink, x0, y0, x1, y1, mm=0.2):
        self.d[ink].rectangle([self.P(x0, y0), self.P(x1, y1)], outline=255, width=self.w(mm))

    def num(self, ink, text, x, y, h, mm=0.22, rnd=None, slant=0.16):
        return digits(self.d[ink], text, *self.P(x, y), h * self.k, self.w(mm), rnd, slant if rnd else 0.0)

    def flush(self, blur=0.3, grain=None):
        for name, (col, op) in self.cols.items():
            m = self.inks[name].filter(ImageFilter.GaussianBlur(blur * self.k / 4))
            if grain is not None and name in grain:
                m = ImageChops.multiply(m, Image.effect_noise((self.W, self.H), 60).point(
                    lambda v: min(255, max(0, int((v - 30) * 1.7)))))
            m = m.point(lambda v, op=op: int(v * op))
            self.img.paste(Image.new("RGB", (self.W, self.H), col), (0, 0), m)


def yellowing(img, rnd, edge_mm, k, col=(214, 202, 168), strength=120, spots=20):
    w, h = img.size
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    e = int(edge_mm * k)
    for i in range(e):
        d.rectangle([i, i, w - 1 - i, h - 1 - i], outline=int(strength * (1 - i / e) ** 2))
    for _ in range(spots):
        x, y, r = rnd.random() * w, rnd.random() * h, rnd.uniform(0.4, 2.0) * k
        d.ellipse([x - r, y - r, x + r, y + r], fill=int(rnd.uniform(20, 60)))
    m = m.filter(ImageFilter.GaussianBlur(e * 0.25))
    img.paste(Image.new("RGB", (w, h), col), (0, 0), m)


def crease(img, y_px, k, light=True, angle=0.0):
    """A fold across the sheet: a light and a dark stripe side by side."""
    w, h = img.size
    for off, col, a in ((-0.35, (255, 255, 250), 70 if light else 30), (0.35, (120, 112, 96), 55)):
        m = Image.new("L", (w, h), 0)
        y = y_px + off * k
        ImageDraw.Draw(m).line([(0, y), (w, y + w * math.tan(math.radians(angle)))], fill=a, width=max(1, int(0.5 * k)))
        img.paste(Image.new("RGB", (w, h), col), (0, 0), m.filter(ImageFilter.GaussianBlur(0.4 * k)))


# --- protocol -------------------------------------------------------------------------------------
def plate_scheme(s, x0, y0, rnd):
    """Firing diagram: a plate outline with chamfered top corners, dimensions, hit points."""
    w, h, ch = 44.0, 58.0, 8.0
    outline = [(x0 + ch, y0), (x0 + w - ch, y0), (x0 + w, y0 + ch), (x0 + w, y0 + h), (x0, y0 + h), (x0, y0 + ch),
               (x0 + ch, y0)]
    s.line("print", outline, 0.35)
    s.line("print", [(x0 + 1.2 + (p[0] - x0) * 0.946, y0 + 1.2 + (p[1] - y0) * 0.958) for p in outline], 0.12)
    # dimensions: arrows and digits
    yd = y0 + h + 4.0
    s.line("print", [(x0, yd), (x0 + w, yd)], 0.15)
    for xa, sg in ((x0, 1), (x0 + w, -1)):
        s.line("print", [(xa + sg * 1.6, yd - 0.6), (xa, yd), (xa + sg * 1.6, yd + 0.6)], 0.15)
        s.line("print", [(xa, y0 + h + 1.0), (xa, yd + 1.0)], 0.12)
    s.num("print", "250", x0 + w / 2 - text_w("250", 2.0) / 2, yd - 0.6, 2.0, 0.16)
    xd = x0 - 4.0
    s.line("print", [(xd, y0), (xd, y0 + h)], 0.15)
    for ya, sg in ((y0, 1), (y0 + h, -1)):
        s.line("print", [(xd - 0.6, ya + sg * 1.6), (xd, ya), (xd + 0.6, ya + sg * 1.6)], 0.15)
    s.num("print", "300", xd - 3.2, y0 + h / 2 + 1.0, 2.0, 0.16)
    # hit points: a circle with a cross, a handwritten number; 4 is a penetration, circled in red
    hits = [(14, 16), (30, 13), (22, 29), (34, 34), (12, 43), (27, 49)]
    for i, (hx, hy) in enumerate(hits):
        cx, cy = x0 + hx, y0 + hy
        s.d["blue"].ellipse([s.P(cx - 1.5, cy - 1.5), s.P(cx + 1.5, cy + 1.5)], outline=255, width=s.w(0.3))
        s.line("blue", [(cx - 2.2, cy - 2.2), (cx + 2.2, cy + 2.2)], 0.22)
        s.line("blue", [(cx - 2.2, cy + 2.2), (cx + 2.2, cy - 2.2)], 0.22)
        s.num("blue", str(i + 1), cx + 2.4, cy - 1.2, 2.6, 0.26, rnd)
    cx, cy = x0 + hits[3][0], y0 + hits[3][1]
    pts = [(cx + 4.6 * math.cos(a / 10.0 * 2 * math.pi) * (1 + 0.08 * math.sin(a)), cy + 4.0 * math.sin(a / 10.0 * 2 * math.pi))
           for a in range(12)]
    s.line("red", pts, 0.45)


def v50_graph(s, x0, y0, w, h, rnd):
    """The "penetration fraction - bullet velocity" graph: axes, ticks with digits, points and a hand-drawn
    curve."""
    s.line("print", [(x0, y0), (x0, y0 + h), (x0 + w, y0 + h)], 0.25)
    s.line("print", [(x0 - 0.8, y0 + 1.8), (x0, y0), (x0 + 0.8, y0 + 1.8)], 0.2)
    s.line("print", [(x0 + w - 1.8, y0 + h - 0.8), (x0 + w, y0 + h), (x0 + w - 1.8, y0 + h + 0.8)], 0.2)
    for i, v in enumerate(("400", "500", "600", "700")):
        x = x0 + 6 + i * (w - 12) / 3
        s.line("print", [(x, y0 + h), (x, y0 + h + 1.2)], 0.18)
        s.line("print", [(x, y0 + 3), (x, y0 + h)], 0.07)
        s.num("print", v, x - text_w(v, 1.9) / 2, y0 + h + 4.0, 1.9, 0.15)
    for i, v in enumerate(("0", "50", "100")):
        y = y0 + h - i * (h - 6) / 2
        s.line("print", [(x0 - 1.2, y), (x0, y)], 0.18)
        s.line("print", [(x0, y), (x0 + w - 3, y)], 0.07)
        s.num("print", v, x0 - 1.8 - text_w(v, 1.9), y + 0.9, 1.9, 0.15)

    def to(vx, py):
        return x0 + 6 + (vx - 400) / 300 * (w - 12), y0 + h - py * (h - 6)
    curve = [to(400 + 300 * i / 24, 1 / (1 + math.exp(-(400 + 300 * i / 24 - 562) / 22))) for i in range(25)]
    s.line("blue", [(p[0] + rnd.uniform(-0.15, 0.15), p[1] + rnd.uniform(-0.15, 0.15)) for p in curve], 0.3)
    for vx, py, full in ((520, 0.0, False), (541, 0.0, False), (556, 0.0, False), (566, 1.0, True), (571, 0.0, False),
                         (589, 1.0, True), (604, 1.0, True), (630, 1.0, True)):
        cx, cy = to(vx, py)
        box = [s.P(cx - 0.9, cy - 0.9), s.P(cx + 0.9, cy + 0.9)]
        if full:
            s.d["blue"].ellipse(box, fill=255)
        else:
            s.d["blue"].ellipse(box, outline=255, width=s.w(0.25))
    xv, _ = to(562, 0)
    y = y0 + 3
    while y < y0 + h:
        s.line("blue", [(xv, y), (xv, min(y + 1.6, y0 + h))], 0.22)
        y += 2.8
    s.num("blue", "562", xv + 1.0, y0 + 9.0, 2.6, 0.26, rnd)


def pictogram(s, cx, cy):
    """A wordless title: a bullet flies into a plate, star-shaped cracks on the plate."""
    s.rect("print", cx - 17, cy - 6, cx + 17, cy + 6, 0.3)
    bx, by = cx - 12.0, cy
    body = [(bx, by - 1.3), (bx + 7.0, by - 1.3), (bx + 9.6, by - 0.6), (bx + 10.6, by), (bx + 9.6, by + 0.6),
            (bx + 7.0, by + 1.3), (bx, by + 1.3)]
    s.d["print"].polygon([s.P(*p) for p in body], fill=255)
    for k in range(3):
        s.line("print", [(bx - 2.0 - k * 1.6, by - 0.9 + k * 0.9), (bx - 0.6 - k * 1.6, by - 0.9 + k * 0.9)], 0.22)
    px = cx + 5.0
    s.d["print"].rectangle([s.P(px, cy - 4.6), s.P(px + 2.2, cy + 4.6)], fill=255)
    for a in (-60, -20, 25, 70, 150, 200):
        r = 3.6 if a % 40 else 2.6
        s.line("print", [(px + 3.2, cy), (px + 3.2 + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))], 0.18)


def stamp(s, ink, cx, cy, r, rnd, ring_digits="0 4 1 7"):
    """Round stamp without text: two rings, dots and digits around the circle, a star in the centre."""
    d = s.d[ink]
    for rr, mm in ((r, 0.45), (r * 0.94, 0.15), (r * 0.62, 0.3)):
        d.ellipse([s.P(cx - rr, cy - rr), s.P(cx + rr, cy + rr)], outline=255, width=s.w(mm))
    n = 26
    for i in range(n):
        a = 2 * math.pi * i / n
        if i % 7 == 0:
            continue
        x, y = cx + r * 0.78 * math.cos(a), cy + r * 0.78 * math.sin(a)
        d.line([s.P(x - 0.7 * math.sin(a), y + 0.7 * math.cos(a)), s.P(x + 0.7 * math.sin(a), y - 0.7 * math.cos(a))],
               fill=255, width=s.w(0.5))
    star = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r * (0.42 if i % 2 == 0 else 0.17)
        star.append(s.P(cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(star, fill=255)
    # uneven impression: part of it printed weakly
    m = Image.new("L", s.inks[ink].size, 255)
    md = ImageDraw.Draw(m)
    for _ in range(14):
        x, y, q = cx + rnd.uniform(-r, r), cy + rnd.uniform(-r, r), rnd.uniform(1.0, 4.0)
        md.ellipse([s.P(x - q, y - q), s.P(x + q, y + q)], fill=rnd.randint(40, 170))
    s.inks[ink] = ImageChops.multiply(s.inks[ink], m.filter(ImageFilter.GaussianBlur(1.2 * s.k)))
    s.d[ink] = ImageDraw.Draw(s.inks[ink])


ROWS = [  # distance, velocity, angle, penetration, dent (mm)
    ("5", "520", "0", "-", "17"), ("5", "541", "0", "-", "19"), ("5", "556", "0", "-", "22"),
    ("5", "566", "0", "+", "-"), ("5", "571", "30", "-", "14"), ("5", "589", "0", "+", "-"),
    ("10", "604", "0", "+", "-"), ("10", "630", "30", "+", "-"),
]


def protocol_form(s, rnd, copy=False):
    """Protocol form; copy=True is a carbon copy: the print is paler, the handwriting is in carbon colour."""
    hand = "blue"                                          # on the copy the "blue" layer is the carbon
    W = 148.0
    # grey stripe of the line on top
    s.d["grey"].rectangle([s.P(8, 6), s.P(W - 8, 10.5)], fill=255)
    # header: fields with squiggles on the left, the number and date on the right
    for i, y in enumerate((19.0, 25.0, 31.0)):
        s.line("print", [(10, y), (78, y)], 0.15)
        scribble(s.d[hand], *s.P(12 + 3 * i, y - 0.8), 1.6 * s.k, rnd.randint(8, 12), rnd, s.w(0.25), slant=0.55)
    s.rect("print", 96, 14, 138, 32, 0.25)
    s.line("print", [(96, 23), (138, 23)], 0.15)
    s.num(hand, "68-0417", 99, 21.0, 4.4, 0.32, rnd)
    s.num(hand, "17.04", 104, 30.0, 3.6, 0.28, rnd)
    pictogram(s, W / 2, 41.0)
    s.line("print", [(10, 41), (W / 2 - 20, 41)], 0.12)
    s.line("print", [(W / 2 + 20, 41), (W - 10, 41)], 0.12)
    # diagram and graph
    plate_scheme(s, 16.0, 52.0, rnd)
    v50_graph(s, 76.0, 52.0, 62.0, 52.0, rnd)
    # table: a header with field numbers, 8 rows
    cols = [8.0, 17.0, 33.0, 55.0, 72.0, 92.0, 116.0, 140.0]
    y0, yh, rh = 124.0, 133.0, 7.4
    y1 = yh + rh * len(ROWS)
    for x in cols:
        s.line("print", [(x, y0), (x, y1)], 0.18)
    for y in (y0, yh - 3.6, yh):
        s.line("print", [(cols[0], y), (cols[-1], y)], 0.25 if y != yh - 3.6 else 0.12)
    for i in range(len(ROWS) + 1):
        s.line("print", [(cols[0], yh + i * rh), (cols[-1], yh + i * rh)], 0.12 if i < len(ROWS) else 0.25)
    for i in range(len(cols) - 1):
        t = str(i + 1)
        s.num("print", t, (cols[i] + cols[i + 1]) / 2 - text_w(t, 2.0) / 2, yh - 0.8, 2.0, 0.16)
        # field "headings" are short printed rules, without words
        cw = cols[i + 1] - cols[i]
        s.line("print", [(cols[i] + cw * 0.22, y0 + 2.4), (cols[i + 1] - cw * 0.22, y0 + 2.4)], 0.5)
    for r, row in enumerate(ROWS):
        yb = yh + (r + 1) * rh - 1.6
        vals = (str(r + 1),) + row
        for c, v in enumerate(vals):
            cx = (cols[c] + cols[c + 1]) / 2
            if v in "+-" and len(v) == 1 and c == 4:
                s.num(hand, v, cx - 1.6, yb + 0.4, 4.2, 0.4, rnd)
            elif v == "-":
                s.line(hand, [(cx - 2.0, yb - 2.2), (cx + 2.0, yb - 2.4)], 0.3)
            else:
                s.num(hand, v, cx - text_w(v, 3.2) / 2, yb, 3.2, 0.3, rnd)
        # the last field is the inspector's tick
        cx = (cols[6] + cols[7]) / 2
        s.line(hand, [(cx - 3, yb - 1.8), (cx - 1.6, yb - 0.4), (cx + 2.8, yb - 3.6)], 0.28)
    if not copy:
        # penetrations are underlined in red pencil
        for r in (3, 5):
            yb = yh + (r + 1) * rh - 0.8
            s.line("red", [(cols[0] + 1, yb + rnd.uniform(-0.3, 0.3)), (cols[-1] - 2, yb + rnd.uniform(-0.3, 0.3))], 0.45)
    # signatures and the stamp
    for x in (12.0, 82.0):
        s.line("print", [(x, 206), (x + 50, 206)], 0.15)
        signature(s.d[hand], *s.P(x + 6, 204.5), 2.6 * s.k, rnd, s.w(0.3))
    if not copy:
        stamp(s, "violet", 112.0, 196.0, 12.5, rnd)


def make_protocol():
    rnd = random.Random(6801)
    s = Sheet(L.PROT_W * 1000, L.PROT_H * 1000, 8.0, (238, 236, 226),
              {"print": (PRINT, 0.92), "grey": (LINE_GREY, 0.95), "blue": (BLUE, 0.92), "red": (RED, 0.80),
               "violet": (VIOLET, 0.72)})
    protocol_form(s, rnd)
    s.flush(grain=("red",))
    img = s.img
    yellowing(img, rnd, 6.0, s.k, spots=30)
    crease(img, 105.0 * s.k, s.k)                          # the form was folded in half
    # greasy corner at the bottom right, where it is picked up, and a stain
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse([s.P(124, 184), s.P(160, 222)], fill=60)
    ImageDraw.Draw(m).ellipse([s.P(20, 140), s.P(31, 151)], fill=35)
    img.paste(Image.new("RGB", img.size, (170, 150, 112)), (0, 0), m.filter(ImageFilter.GaussianBlur(4 * s.k)))
    a = Image.new("L", img.size, 255)
    # the top left corner is torn
    ImageDraw.Draw(a).polygon([s.P(0, 0), s.P(3.2, 0), s.P(2.0, 1.1), s.P(0.8, 1.6), s.P(0, 3.0)], fill=0)
    out = img.convert("RGBA")
    out.putalpha(a)
    save(out, "protocol.png")


def make_copy():
    rnd = random.Random(6802)
    s = Sheet(L.COPY_W * 1000, L.COPY_H * 1000, 4.0, (228, 232, 236),
              {"print": ((70, 70, 80), 0.75), "grey": (LINE_GREY, 0.8), "blue": (CARBON, 0.70), "red": (RED, 0.0),
               "violet": (VIOLET, 0.0)})
    protocol_form(s, rnd, copy=True)
    s.flush(blur=0.8)
    yellowing(s.img, rnd, 5.0, s.k, col=(206, 206, 196), spots=12)
    out = s.img.convert("RGBA")
    save(out, "copy.png")


# --- map ------------------------------------------------------------------------------------------
def smooth_field(w, h, cells, seed, octaves=((1.0, 1), (0.45, 2), (0.2, 4))):
    rnd = random.Random(seed)
    acc, acc_w = None, 0.0
    for a, f in octaves:
        cw, ch = cells[0] * f, cells[1] * f
        small = Image.new("L", (cw, ch))
        small.putdata([rnd.randint(0, 255) for _ in range(cw * ch)])
        big = small.resize((w, h), Image.BICUBIC)
        acc = big if acc is None else Image.blend(acc, big, a / (acc_w + a))
        acc_w += a
    return acc.filter(ImageFilter.GaussianBlur(6))


def make_map():
    k = 5.0                                                 # px/mm
    wmm, hmm = L.MAP_S[0] * 1000, L.MAP_S[1] * 1000
    W, H = int(wmm * k), int(hmm * k)
    rnd = random.Random(6803)
    img = Image.new("RGB", (W, H), (240, 236, 214))
    # forest
    forest = smooth_field(W, H, (5, 6), 68031).point(lambda v: 255 if v > 136 else 0).filter(ImageFilter.GaussianBlur(1))
    img.paste(Image.new("RGB", (W, H), (196, 222, 166)), (0, 0), forest)
    edge = forest.filter(ImageFilter.FIND_EDGES).point(lambda v: 160 if v > 40 else 0)
    img.paste(Image.new("RGB", (W, H), (112, 160, 96)), (0, 0), edge)
    # contour lines: every fifth one thicker
    hf = smooth_field(W, H, (4, 5), 68032)
    q = hf.point(lambda v: (v // 9) * 9).filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 0 else 0)
    qi = hf.point(lambda v: (v // 45) * 45).filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 0 else 0)
    qi = qi.filter(ImageFilter.MaxFilter(3))
    cont = ImageChops.lighter(q.point(lambda v: v * 150 // 255), qi.point(lambda v: v * 210 // 255))
    img.paste(Image.new("RGB", (W, H), (178, 116, 64)), (0, 0), cont.filter(ImageFilter.GaussianBlur(0.4)))
    d = ImageDraw.Draw(img)

    def P(x, y):                                            # mm from the top left corner
        return x * k, y * k
    # lake and river
    lake = [(150 + 14 * math.cos(a) + rnd.uniform(-2, 2), 30 + 9 * math.sin(a) + rnd.uniform(-2, 2))
            for a in [i * 2 * math.pi / 14 for i in range(14)]]
    d.polygon([P(*p) for p in lake], fill=(176, 210, 236), outline=(70, 120, 190))
    river = catmull([(-5, 60), (25, 72), (40, 98), (32, 130), (55, 160), (90, 178), (120, 200), (150, 240), (200, 262)])
    d.line([P(*p) for p in river], fill=(72, 124, 196), width=int(1.0 * k), joint="curve")
    # roads: the highway is orange with a black outline, the dirt road is thin
    road = catmull([(-5, 210), (40, 196), (80, 150), (110, 118), (150, 96), (200, 90)])
    d.line([P(*p) for p in road], fill=(30, 30, 30), width=int(1.7 * k), joint="curve")
    d.line([P(*p) for p in road], fill=(232, 150, 64), width=int(1.0 * k), joint="curve")
    track = catmull([(10, -5), (18, 40), (12, 90), (26, 140), (20, 190), (34, 262)], sub=240)
    cum = [0.0]
    for a, b in zip(track, track[1:]):
        cum.append(cum[-1] + math.dist(a, b))
    on = [p for p, c in zip(track, cum) if c % 3.2 < 2.0]  # 2 mm dashes with 1.2 mm gaps
    for p in on:
        d.ellipse([P(p[0] - 0.16, p[1] - 0.16), P(p[0] + 0.16, p[1] + 0.16)], fill=(40, 40, 40))
    # settlement: a built-up block and houses
    d.polygon([P(118, 104), P(140, 98), P(146, 116), P(124, 124)], fill=(232, 196, 124), outline=(40, 40, 40))
    for _ in range(18):
        x, y = rnd.uniform(96, 176), rnd.uniform(84, 132)
        s = rnd.uniform(1.2, 2.2)
        d.rectangle([P(x, y), P(x + s, y + s * 0.8)], fill=(28, 28, 28))
    # kilometre grid at 1 : 50 000 - 20 mm
    for i in range(-1, 12):
        x = i * 20.0 + 6.0
        d.line([P(x, -2), P(x + 1.2, hmm + 2)], fill=(44, 44, 48), width=max(1, int(0.18 * k)))
    for i in range(-1, 15):
        y = i * 20.0 + 11.0
        d.line([P(-2, y), P(wmm + 2, y - 1.0)], fill=(44, 44, 48), width=max(1, int(0.18 * k)))
    # elevation marks
    marks = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(marks)
    for x, y, t in ((9, 30, "214.6"), (172, 150, "187.2"), (60, 232, "203.9"), (176, 222, "196.1"), (8, 176, "221.0")):
        md.ellipse([P(x - 0.5, y - 0.5), P(x + 0.5, y + 0.5)], fill=255)
        digits(md, t, *P(x + 1.0, y + 0.8), 1.8 * k, max(1, int(0.18 * k)))
    img.paste(Image.new("RGB", (W, H), (30, 30, 30)), (0, 0), marks)
    # the officer's marks: a blue arrow, a red semicircle of defence
    pen = Image.new("L", (W, H), 0)
    pd = ImageDraw.Draw(pen)
    arrow = catmull([(170, 250), (178, 215), (170, 180), (182, 150)])
    pd.line([P(*p) for p in arrow], fill=255, width=int(0.8 * k), joint="curve")
    pd.polygon([P(176, 154), P(186, 144), P(184, 158)], fill=255)
    img.paste(Image.new("RGB", (W, H), (40, 70, 170)), (0, 0), pen.filter(ImageFilter.GaussianBlur(0.4)))
    pen = Image.new("L", (W, H), 0)
    pd = ImageDraw.Draw(pen)
    arc = [(12 + 9 * math.cos(a), 108 + 15 * math.sin(a)) for a in [math.pi * (0.4 + i * 0.1) for i in range(13)]]
    pd.line([P(*p) for p in arc], fill=255, width=int(0.9 * k), joint="curve")
    for p in arc[1:-1:2]:
        pd.line([P(*p), P(p[0] - 2.0, p[1])], fill=255, width=int(0.6 * k))
    pd.line([P(*p) for p in catmull([(30, 8), (50, 4), (80, 10), (120, 6), (160, 14)])], fill=255,
            width=int(0.7 * k), joint="curve")
    img.paste(Image.new("RGB", (W, H), (190, 46, 40)), (0, 0), pen.filter(ImageFilter.GaussianBlur(0.4)))
    # map folds and wear on them
    crease(img, 70.0 * k, k)
    crease(img, 190.0 * k, k)
    vf = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vf).line([P(98, 0), P(98, hmm)], fill=60, width=int(0.8 * k))
    img.paste(Image.new("RGB", (W, H), (255, 255, 248)), (0, 0), vf.filter(ImageFilter.GaussianBlur(0.5 * k)))
    yellowing(img, rnd, 3.0, k, col=(220, 210, 176), strength=60, spots=10)
    save(img, "map.png")


# --- celluloid scratches --------------------------------------------------------------------------
def make_scratches():
    k = 5.0
    wmm, hmm = L.MAP_S[0] * 1000, L.MAP_S[1] * 1000
    W, H = int(wmm * k), int(hmm * k)
    rnd = random.Random(6804)
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    # small scratches in all directions, denser in the middle
    for _ in range(420):
        x, y = rnd.gauss(wmm / 2, wmm / 3.2), rnd.gauss(hmm / 2, hmm / 3.0)
        a, ln = rnd.uniform(0, math.pi), rnd.uniform(2.0, 18.0)
        d.line([(x * k, y * k), ((x + ln * math.cos(a)) * k, (y + ln * math.sin(a)) * k)],
               fill=rnd.randint(40, 120), width=1)
    # long arcs - wiped with a sleeve
    for _ in range(26):
        cx, cy, r = rnd.uniform(0, wmm), rnd.uniform(0, hmm), rnd.uniform(40, 120)
        a0 = rnd.uniform(0, 2 * math.pi)
        pts = [((cx + r * math.cos(a0 + t * 0.02)) * k, (cy + r * math.sin(a0 + t * 0.02)) * k) for t in range(rnd.randint(8, 30))]
        d.line(pts, fill=rnd.randint(30, 80), width=1)
    # small cracks at the fold (the hinge side is on the right)
    for _ in range(60):
        x, y = wmm - rnd.uniform(0, 9), rnd.uniform(0, hmm)
        pts = [(x * k, y * k)]
        for _ in range(4):
            x += rnd.uniform(-3, 1)
            y += rnd.uniform(-2, 2)
            pts.append((x * k, y * k))
        d.line(pts, fill=rnd.randint(70, 160), width=1)
    # a crease across (the celluloid was bent): a light stripe with fine kinks
    y0 = 58.0
    pts = [(x * k, (y0 + 0.6 * math.sin(x * 0.4) + rnd.uniform(-0.3, 0.3)) * k) for x in range(0, int(wmm) + 2, 2)]
    d.line(pts, fill=150, width=int(0.5 * k))
    # wear in patches - a cloudy bloom
    haze = Image.new("L", (W, H), 0)
    hd = ImageDraw.Draw(haze)
    for _ in range(14):
        x, y, r = rnd.uniform(0, wmm), rnd.uniform(0, hmm), rnd.uniform(8, 26)
        hd.ellipse([(x - r) * k, (y - r * 0.6) * k, (x + r) * k, (y + r * 0.6) * k], fill=rnd.randint(14, 34))
    img = ImageChops.lighter(img, haze.filter(ImageFilter.GaussianBlur(8 * k)))
    save(img, "cell_scr.png")


# --- leather from above: stitching, stamp, rivets -------------------------------------------------
class Top:
    """Layout from above in model coordinates (metres, y up) -> pixels."""

    def __init__(self, ppmm=3.0):
        self.k = ppmm * 1000.0
        self.W, self.H = int(L.PRINT_S[0] * self.k), int(L.PRINT_S[1] * self.k)
        self.img = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def P(self, x, y):
        return ((x - L.PRINT_C[0] + L.PRINT_S[0] / 2) * self.k, (L.PRINT_C[1] + L.PRINT_S[1] / 2 - y) * self.k)

    def stitch(self, pts, col, closed=False, dash=0.0026, gap=0.0011, width=0.00055, rnd=None):
        """Stitching: stitches of dash with gap between them along a polyline (metres)."""
        pts = list(pts) + ([pts[0]] if closed else [])
        cum = [0.0]
        for a, b in zip(pts, pts[1:]):
            cum.append(cum[-1] + math.dist(a, b))

        def at(s):
            for i in range(len(pts) - 1):
                if s <= cum[i + 1] or i == len(pts) - 2:
                    ln = max(cum[i + 1] - cum[i], 1e-12)
                    t = min(1.0, max(0.0, (s - cum[i]) / ln))
                    return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t)
        w = max(1, int(round(width * self.k)))
        s = gap / 2
        while s + dash <= cum[-1]:
            j = rnd.uniform(-0.00012, 0.00012) if rnd else 0.0
            a, b = at(s), at(s + dash)
            self.d.line([self.P(a[0] + j, a[1] - j), self.P(b[0] + j, b[1] - j)], fill=col + (255,), width=w)
            s += dash + gap

    def offset(self, pts, off):
        """A polyline shifted to the left (along the direction of travel) by off."""
        out = []
        for i, p in enumerate(pts):
            a = pts[max(0, i - 1)]
            b = pts[min(len(pts) - 1, i + 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(tx, ty) or 1.0
            out.append((p[0] - ty / ln * off, p[1] + tx / ln * off))
        return out


def make_leather_print():
    t = Top(3.0)
    rnd = random.Random(6805)
    thread = (132, 98, 64)
    # leaf: stitching along the edge and around the window
    t.stitch(L.rrect(L.LXC, 0.0, L.W - 0.010, L.HL - 0.010, L.R_C - 0.005, nc=6), thread, closed=True, rnd=rnd)
    t.stitch(L.rrect(L.LXC, 0.0, L.W - 0.023, L.HL - 0.023, L.R_C - 0.0115, nc=6), thread, closed=True, rnd=rnd)
    # body front wall: stitching by the edge
    t.stitch(L.rrect(L.BXC, 0.0, L.W - 0.009, L.HL - 0.009, L.R_C - 0.0045, nc=6), thread, closed=True, rnd=rnd)
    # pocket: three sides and the folded-over top
    p = L.POCKET
    i = 0.0028
    t.stitch([(p["x0"] + i, p["y1"] - 0.002), (p["x0"] + i, p["y0"] + i), (p["x1"] - i, p["y0"] + i),
              (p["x1"] - i, p["y1"] - 0.002)], thread, rnd=rnd)
    t.stitch([(p["x0"] + 0.004, p["y1"] - 0.005), (p["x1"] - 0.004, p["y1"] - 0.005)], thread, rnd=rnd)
    # pencil holder: tacks between the loops and at the ends of the strips
    for by in L.BAND_YS:
        xs = [L.BAND_X0 + 0.0035] + [(a + b) / 2 for a, b in zip(L.PEN_XS, L.PEN_XS[1:])] + [L.BAND_X1 - 0.0035]
        for x in xs:
            for dx in (-0.0011, 0.0011):
                t.stitch([(x + dx, by - L.BAND_W / 2 + 0.0015), (x + dx, by + L.BAND_W / 2 - 0.0015)], thread,
                         dash=0.0018, gap=0.0008, rnd=rnd)
    # tab
    hw = L.TAB_W / 2 - 0.003
    tab = [(L.TAB_X - hw, L.BY0 - 0.003)]
    for k in range(9):
        a = math.radians(180.0 + 180.0 * k / 8)
        tab.append((L.TAB_X + hw * math.cos(a), L.TAB_Y1 + L.TAB_W / 2 + hw * math.sin(a)))
    tab.append((L.TAB_X + hw, L.BY0 - 0.003))
    t.stitch(tab, thread, rnd=rnd)
    # strap: two lines of stitching along the edges
    strap_thread = (96, 60, 32)
    for off in (L.STRAP_W / 2 - 0.0025, -(L.STRAP_W / 2 - 0.0025)):
        t.stitch(t.offset(L.STRAP, off), strap_thread, rnd=rnd)
    # strap across the window: stitching in the middle
    t.stitch([(L.WSTRAP_X, L.WSTRAP_Y0 + 0.004), (L.WSTRAP_X, L.WSTRAP_Y1 - 0.004)], thread, rnd=rnd)
    # flap (suede): stitching along the edge except the root
    fo = L.flap_outline(0.0055)
    fo = [(x, max(y, L.BY1 + 0.003)) for x, y in fo[1:] + [fo[0]]]   # stitching goes under the body at the root
    t.stitch(fo, (104, 72, 44), rnd=rnd)
    # stamp on the suede: a frame, lines, size digits - no words
    st = Image.new("L", (t.W, t.H), 0)
    sd = ImageDraw.Draw(st)
    s = L.STAMP
    cx, cy, w, h = s["x"], s["y"], s["w"], s["h"]
    corners = [L.rot((cx + dx, cy + dy), (cx, cy), s["rot"]) for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2),
                                                                                (w / 2, h / 2), (-w / 2, h / 2))]
    sd.line([t.P(*c) for c in corners + [corners[0]]], fill=255, width=max(1, int(0.0006 * t.k)))
    for j, frac in enumerate((0.28, 0.52, 0.76)):
        a = L.rot((cx - w / 2 + 0.004, cy + h / 2 - h * frac), (cx, cy), s["rot"])
        b = L.rot((cx + w / 2 - (0.004 if j != 1 else 0.016), cy + h / 2 - h * frac), (cx, cy), s["rot"])
        sd.line([t.P(*a), t.P(*b)], fill=200, width=max(1, int(0.0009 * t.k)))
    pnum = L.rot((cx + w / 2 - 0.013, cy + h / 2 - h * 0.52 - 0.0016), (cx, cy), s["rot"])
    digits(sd, "34", *t.P(*pnum), 0.0042 * t.k, max(1, int(0.0006 * t.k)))
    holes = Image.effect_noise((t.W, t.H), 70).point(lambda v: 0 if v < 70 else 255).filter(ImageFilter.GaussianBlur(1.2))
    st = ImageChops.multiply(st.filter(ImageFilter.GaussianBlur(0.8)), holes).point(lambda v: int(v * 0.55))
    t.img.paste(Image.new("RGBA", (t.W, t.H), (78, 52, 92, 150)), (0, 0), st)
    # lock rivets on the suede
    for x, y in L.RIVETS:
        r = 0.0026
        t.d.ellipse([t.P(x - r, y + r), t.P(x + r, y - r)], fill=(176, 174, 168, 255), outline=(70, 66, 60, 255),
                    width=max(1, int(0.0005 * t.k)))
        t.d.ellipse([t.P(x - 0.0009, y + 0.0009), t.P(x + 0.0009, y - 0.0009)], fill=(214, 212, 206, 255))
    save(t.img, "leather_print.png")


# --- corner of the second sheet from under the flap -----------------------------------------------
def make_sheet2():
    k = 6.0 * 1000                                          # px per metre
    W, H = int(L.S2_S[0] * k), int(L.S2_S[1] * k)

    def P(x, y):
        return (x - L.S2_C[0] + L.S2_S[0] / 2) * k, (L.S2_C[1] + L.S2_S[1] / 2 - y) * k
    rnd = random.Random(6806)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = L.S2_CORNER
    a = math.radians(L.S2_A)
    u = (-math.cos(a), -math.sin(a))                        # from the corner along the top edge of the sheet
    v = (math.sin(a), -math.cos(a))                         # from the corner down along the side edge

    def S(su, sv):                                          # mm from the sheet corner -> model metres
        return cx + (u[0] * su + v[0] * sv) / 1000, cy + (u[1] * su + v[1] * sv) / 1000
    poly = [S(0, 0), S(120, 0), S(120, 120), S(0, 120)]
    d.polygon([P(*p) for p in poly], fill=(238, 234, 226, 255))
    ink = Image.new("L", (W, H), 0)
    di = ImageDraw.Draw(ink)
    grey = Image.new("L", (W, H), 0)
    ImageDraw.Draw(grey).polygon([P(*S(su, sv)) for su, sv in ((8, 6), (140, 6), (140, 10.5), (8, 10.5))], fill=255)
    lw = max(1, int(0.00018 * k))
    for sv in (19, 25, 31):
        di.line([P(*S(10, sv)), P(*S(78, sv))], fill=255, width=lw)
    # continuation table: fields and rows
    for su in (8, 17, 33, 55):
        di.line([P(*S(su, 40)), P(*S(su, 120))], fill=255, width=lw)
    for sv in (40, 44, 49, 56.4, 63.8, 71.2):
        di.line([P(*S(8, sv)), P(*S(70, sv))], fill=255, width=lw)
    # a sheet row runs against u (the corner is the top right), up the sheet runs against v
    right = (-u[0], -u[1])
    for i, su in enumerate((12.5, 25, 44)):
        digits_rot(di, str(i + 1), S(su + 0.8, 48.2), 2.0, right, P, k, None, 0.00018)
    blue = Image.new("L", (W, H), 0)
    db = ImageDraw.Draw(blue)
    for r, (n, dist, vel) in enumerate((("9", "10", "612"), ("10", "10", "618"), ("11", "15", "597"))):
        sv = 56.4 + r * 7.4 - 1.6
        for su, txt in ((12.5, n), (25, dist), (44, vel)):
            digits_rot(db, txt, S(su + text_w(txt, 3.2) / 2, sv), 3.2, right, P, k, rnd, 0.00030)
    img.paste(Image.new("RGBA", (W, H), PRINT + (255,)), (0, 0), ink.point(lambda q: int(q * 0.85)))
    img.paste(Image.new("RGBA", (W, H), LINE_GREY + (255,)), (0, 0), ImageChops.multiply(grey, img.split()[3]))
    img.paste(Image.new("RGBA", (W, H), BLUE + (255,)), (0, 0), blue.filter(ImageFilter.GaussianBlur(0.4)))
    save(img, "sheet2.png")


def digits_rot(d, text, start, hmm, right, P, k, rnd, width):
    """Digits along a sheet row: from the point start (model metres, the bottom of the row) in direction
    right (a unit vector), up is right rotated by 90 degrees counter-clockwise; height hmm (mm)."""
    x, y = start
    up = (-right[1], right[0])
    h = hmm / 1000
    cx = 0.0
    for ch in text:
        hh = h * (rnd.uniform(0.92, 1.06) if rnd else 1.0)
        for stroke in HAND[ch]:
            pts = []
            for px, py in stroke:
                sx = cx + (px + (0.16 if rnd else 0.0) * (1 - py)) * hh
                sy = (1 - py) * hh
                pts.append(P(x + right[0] * sx + up[0] * sy, y + right[1] * sx + up[1] * sy))
            d.line(pts, fill=255, width=max(1, int(width * k)), joint="curve")
        cx += adv(ch, hh)


if __name__ == "__main__":
    make_protocol()
    make_copy()
    make_map()
    make_scratches()
    make_leather_print()
    make_sheet2()
