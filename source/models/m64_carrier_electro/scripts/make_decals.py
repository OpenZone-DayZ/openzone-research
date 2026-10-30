"""Images for the M64 "Electronics" carrier (system Python + Pillow), without letters: schematic lines,
symbols, fields, digits.

    python make_decals.py      -> ../work/*.png

- schematic.png - the top sheet of the folded diagram (RGBA, the whole sheet PW x PH, the top of the
  image is the top of the sheet): a fragment of a circuit diagram per ESKD (GOST 2.728/2.730/2.743:
  resistors 4 x 10 mm, transistors in a D 12 circle, an IC with pin fields, coils, diodes, a
  connector), a bundle of link lines, dash-dot unit frames, oscillograms in frames and a voltage table
  (digits only), a frame and a title block per GOST 2.104 form 1 with empty fields; reference
  designators are numbers only, no letters. On top red pencil (a circled stage, a corrected value) and
  finger marks at the bent corner. The lines are blue-violet, like a diazo copy (a "blueprint"); the
  paper colour is in the generator's material (alpha is only the print and marks);
- cd_top.png - the disc from above (RGBA, CD_D x CD_D in disc axes): a transparent clamping zone with
  the diagram under it, a mirror band and a rim with a rainbow, a paper label D 117 / D 41 - white,
  with an orange stripe (the "Electronics" line colour, like the M49 tag) and a handwritten marker
  number;
- cd_data.png - the data side from below: a rainbow, the recorded zone darker (CD-R).

The digit font is our own (strokes, GOST 2.304 type B slanted at 75 degrees): the images do not depend
on system fonts. Sizes come from m64_layout.py (shared with build_m64.py).
"""
import colorsys
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m64_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
K = 8.0                           # px per mm for the sheet
W_MAIN, W_LINE, W_THIN = 0.65, 0.4, 0.25


def save(img, name):
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, img.size)


# --- digits: strokes in a 0.6 x 1 cell (y down) ---------------------------------------------------
GLYPH = {
    "0": [[(0.30, 0.0), (0.08, 0.15), (0.0, 0.5), (0.08, 0.86), (0.30, 1.0), (0.52, 0.86), (0.60, 0.5),
           (0.52, 0.14), (0.30, 0.0)]],
    "1": [[(0.12, 0.25), (0.40, 0.0), (0.40, 1.0)]],
    "2": [[(0.04, 0.24), (0.20, 0.02), (0.44, 0.02), (0.58, 0.22), (0.50, 0.46), (0.04, 1.0), (0.62, 1.0)]],
    "3": [[(0.04, 0.10), (0.30, 0.0), (0.52, 0.12), (0.50, 0.34), (0.24, 0.48), (0.54, 0.62), (0.56, 0.86),
           (0.30, 1.0), (0.02, 0.90)]],
    "4": [[(0.46, 1.0), (0.46, 0.0), (0.0, 0.68), (0.62, 0.68)]],
    "5": [[(0.56, 0.0), (0.12, 0.0), (0.06, 0.46), (0.34, 0.40), (0.58, 0.60), (0.54, 0.88), (0.28, 1.0),
           (0.02, 0.90)]],
    "6": [[(0.50, 0.04), (0.24, 0.16), (0.05, 0.55), (0.10, 0.90), (0.30, 1.0), (0.52, 0.88), (0.55, 0.66),
           (0.34, 0.52), (0.08, 0.62)]],
    "7": [[(0.0, 0.0), (0.60, 0.0), (0.24, 1.0)]],
    "8": [[(0.30, 0.48), (0.08, 0.32), (0.12, 0.08), (0.30, 0.0), (0.50, 0.08), (0.52, 0.30), (0.30, 0.48),
           (0.05, 0.70), (0.10, 0.95), (0.30, 1.0), (0.52, 0.92), (0.56, 0.70), (0.30, 0.48)]],
    "9": [[(0.55, 0.40), (0.34, 0.50), (0.10, 0.42), (0.05, 0.20), (0.25, 0.0), (0.50, 0.05), (0.55, 0.40),
           (0.48, 1.0)]],
    "-": [[(0.08, 0.56), (0.50, 0.56)]], ".": [[(0.22, 0.92), (0.30, 1.0)]],
    ",": [[(0.30, 0.86), (0.26, 1.06), (0.16, 1.18)]],
    "+": [[(0.05, 0.55), (0.55, 0.55)], [(0.30, 0.30), (0.30, 0.80)]],
    ":": [[(0.26, 0.30), (0.30, 0.36)], [(0.24, 0.90), (0.28, 0.96)]],
}


def text(d, s, x, y, h, fill=255, width=None, slant=0.27, rnd=None, jitter=0.0, scale=K):
    """A string of digits from the bottom left corner (x, y) in mm, h mm high; slant is the slant (75
    degrees per GOST)."""
    width = width or max(1, int(h * 0.11 * scale))
    cx = x
    for ch in s:
        if ch == " ":
            cx += h * 0.5
            continue
        hh = h * (rnd.uniform(0.92, 1.06) if rnd and jitter else 1.0)
        dy = (rnd.uniform(-1, 1) * jitter * h) if rnd else 0.0
        for stroke in GLYPH[ch]:
            pts = []
            for px, py in stroke:
                jx = jy = 0.0
                if rnd and jitter:
                    jx, jy = rnd.uniform(-1, 1) * jitter, rnd.uniform(-1, 1) * jitter
                X = cx + (px + jx) * hh + (1 - py) * slant * hh
                Y = y - hh + (py + jy) * hh + dy
                pts.append((X * scale, Y * scale))
            d.line(pts, fill=fill, width=width, joint="curve")
        cx += hh * (0.80 if ch not in ".,:" else 0.42)
    return cx


# --- diagram: symbols (mm, y down) ----------------------------------------------------------------
class Sheet:
    def __init__(self, w, h):
        self.W, self.H = int(w * K), int(h * K)
        self.m = Image.new("L", (self.W, self.H), 0)
        self.d = ImageDraw.Draw(self.m)

    @staticmethod
    def P(x, y):
        return (x * K, y * K)

    def line(self, pts, w=W_LINE):
        self.d.line([self.P(*p) for p in pts], fill=255, width=max(1, round(w * K)), joint="curve")

    def rect(self, x0, y0, x1, y1, w=W_LINE, fill=False):
        if fill:
            self.d.rectangle([self.P(x0, y0), self.P(x1, y1)], fill=255)
        else:
            self.d.rectangle([self.P(x0, y0), self.P(x1, y1)], outline=255, width=max(1, round(w * K)))

    def circle(self, x, y, r, w=W_LINE, fill=False):
        box = [self.P(x - r, y - r), self.P(x + r, y + r)]
        if fill:
            self.d.ellipse(box, fill=255)
        else:
            self.d.ellipse(box, outline=255, width=max(1, round(w * K)))

    def dot(self, x, y):
        self.circle(x, y, 0.75, fill=True)

    def num(self, s, x, y, h=2.5):
        text(self.d, s, x, y, h, width=max(1, round(0.25 * K)))

    # resistor 4 x 10 (GOST 2.728), centre (x, y); the leads are the ends of the body
    def resistor(self, x, y, vert=True, n=None, val=None, pot=False, left=False):
        if vert:
            self.rect(x - 2, y - 5, x + 2, y + 5)
            lx = x - 3.0 - 2.0 * max(len(n or ""), len(val or "")) if left else x + 3.0
            dy = 2.0 if left else 0.0                       # on the left: lower, so captions do not meet
            if n:
                self.num(n, lx, y - 0.6 + dy)
            if val:
                self.num(val, lx, y + 3.4 + dy, 2.2)
            if pot:                                         # wiper with an arrow
                self.line([(x + 6, y + 1), (x + 2.4, y)])
                self.d.polygon([self.P(x + 2.2, y), self.P(x + 3.6, y - 0.9), self.P(x + 3.8, y + 0.9)], fill=255)
            return (x, y - 5), (x, y + 5)
        self.rect(x - 5, y - 2, x + 5, y + 2)
        if n:
            self.num(n, x - 2.5, y - 3.0)
        if val:
            self.num(val, x - 2.5, y + 6.0, 2.2)
        return (x - 5, y), (x + 5, y)

    # capacitor: plates 8 mm, gap 1.5 mm; polar means electrolytic (one plate is a rectangle)
    def capacitor(self, x, y, vert=True, n=None, val=None, polar=False):
        if vert:
            self.line([(x - 4, y - 0.75), (x + 4, y - 0.75)], W_MAIN)
            if polar:
                self.rect(x - 4, y + 0.5, x + 4, y + 1.6, W_LINE)
                self.line([(x - 4.5, y - 3.2), (x - 2.5, y - 3.2)], W_THIN)
                self.line([(x - 3.5, y - 4.2), (x - 3.5, y - 2.2)], W_THIN)
            else:
                self.line([(x - 4, y + 0.75), (x + 4, y + 0.75)], W_MAIN)
            if n:
                self.num(n, x + 5.0, y - 0.4)
            if val:
                self.num(val, x + 5.0, y + 3.2, 2.2)
            return (x, y - 0.75), (x, y + (1.6 if polar else 0.75))
        self.line([(x - 0.75, y - 4), (x - 0.75, y + 4)], W_MAIN)
        self.line([(x + 0.75, y - 4), (x + 0.75, y + 4)], W_MAIN)
        if n:
            self.num(n, x - 2.0, y - 5.0)
        if val:
            self.num(val, x - 2.5, y + 7.6, 2.2)
        return (x - 0.75, y), (x + 0.75, y)

    # transistor (GOST 2.730): a D 12 circle, base on the left; leads: base, collector (up), emitter (down)
    def transistor(self, x, y, n=None, pnp=False):
        self.circle(x, y, 6.0)
        self.line([(x - 2.2, y - 3.6), (x - 2.2, y + 3.6)], W_MAIN)
        self.line([(x - 9.0, y), (x - 2.2, y)])
        self.line([(x - 2.2, y - 1.6), (x + 2.5, y - 4.4), (x + 2.5, y - 9.0)])
        self.line([(x - 2.2, y + 1.6), (x + 2.5, y + 4.4), (x + 2.5, y + 9.0)])
        ex, ey = (x + 1.2, y + 3.6) if not pnp else (x - 0.6, y + 2.5)
        ang = math.atan2(2.8, 4.7) if not pnp else math.atan2(-2.8, -4.7)
        ca, sa = math.cos(ang), math.sin(ang)
        tri = [(ex, ey), (ex - 2.0 * ca + 0.8 * sa, ey - 2.0 * sa - 0.8 * ca), (ex - 2.0 * ca - 0.8 * sa, ey - 2.0 * sa + 0.8 * ca)]
        self.d.polygon([self.P(*p) for p in tri], fill=255)
        if n:
            self.num(n, x + 6.5, y + 7.0)
        return (x - 9.0, y), (x + 2.5, y - 9.0), (x + 2.5, y + 9.0)

    # diode: a 5 mm triangle towards the bar; dir is where the current flows ("r", "l", "u", "d")
    def diode(self, x, y, dir="r", n=None):
        v = {"r": (1, 0), "l": (-1, 0), "u": (0, -1), "d": (0, 1)}[dir]
        px, py = -v[1], v[0]
        a = (x - 2.5 * v[0], y - 2.5 * v[1])
        b = (x + 2.5 * v[0], y + 2.5 * v[1])
        tri = [(a[0] + 2.5 * px, a[1] + 2.5 * py), (a[0] - 2.5 * px, a[1] - 2.5 * py), b]
        self.d.polygon([self.P(*p) for p in tri], outline=255, width=max(1, round(W_LINE * K)))
        self.line([(b[0] + 2.5 * px, b[1] + 2.5 * py), (b[0] - 2.5 * px, b[1] - 2.5 * py)], W_MAIN)
        if n:
            self.num(n, x + 3.4 * abs(px) + 1.0, y - 3.0 * abs(py) - 2.2)
        return a, b

    # coil: n half-circles of D 3 along the axis (GOST 2.723)
    def inductor(self, x, y, vert=True, n=4, side=1, core=False):
        r = 1.5
        L_ = n * 2 * r
        for i in range(n):
            if vert:
                cy = y - L_ / 2 + r + 2 * r * i
                box = [self.P(x - r, cy - r), self.P(x + r, cy + r)]
                self.d.arc(box, -90 if side > 0 else 90, 90 if side > 0 else 270, fill=255, width=max(1, round(W_LINE * K)))
            else:
                cx = x - L_ / 2 + r + 2 * r * i
                box = [self.P(cx - r, y - r), self.P(cx + r, y + r)]
                self.d.arc(box, 180 if side > 0 else 0, 360 if side > 0 else 180, fill=255, width=max(1, round(W_LINE * K)))
        if core:
            for k in (1, 2):
                if vert:
                    self.line([(x - side * (r + 1.0 * k), y - L_ / 2), (x - side * (r + 1.0 * k), y + L_ / 2)], W_LINE)
        if vert:
            return (x, y - L_ / 2), (x, y + L_ / 2)
        return (x - L_ / 2, y), (x + L_ / 2, y)

    # chassis / ground: three bars of decreasing length
    def ground(self, x, y):
        self.line([(x, y), (x, y + 2.5)])
        for i, w in enumerate((3.0, 2.0, 1.0)):
            self.line([(x - w, y + 2.5 + i * 1.0), (x + w, y + 2.5 + i * 1.0)], W_LINE)

    # IC (GOST 2.743): the main field and pin fields of 5 mm; pins every 5 mm with numbers
    def ic(self, x0, y0, w, h, left, right, n=None):
        self.rect(x0, y0, x0 + w, y0 + h, W_LINE)
        self.line([(x0 + 5, y0), (x0 + 5, y0 + h)], W_THIN)
        self.line([(x0 + w - 5, y0), (x0 + w - 5, y0 + h)], W_THIN)
        pins = {}
        for i, p in enumerate(left):
            yy = y0 + 5 + 5 * i
            self.line([(x0 - 5, yy), (x0, yy)])
            self.num(p, x0 - 4.6, yy - 0.6, 2.2)
            pins[p] = (x0 - 5, yy)
        for i, p in enumerate(right):
            yy = y0 + 5 + 5 * i
            self.line([(x0 + w, yy), (x0 + w + 5, yy)])
            self.num(p, x0 + w + 0.8, yy - 0.6, 2.2)
            pins[p] = (x0 + w + 5, yy)
        if n:
            self.num(n, x0 + w / 2 - 2, y0 - 1.5)
        return pins

    # connector: a column of contacts every 5 mm, sockets are half-circles, numbers in the cells
    def connector(self, x, y0, k, n=None):
        self.rect(x, y0, x + 8, y0 + 5 * k, W_LINE)
        pts = []
        for i in range(k):
            yy = y0 + 2.5 + 5 * i
            if i:
                self.line([(x, y0 + 5 * i), (x + 8, y0 + 5 * i)], W_THIN)
            self.num(str(i + 1), x + 1.0, yy + 1.2, 2.2)
            self.d.arc([self.P(x + 4.6, yy - 1.2), self.P(x + 7.0, yy + 1.2)], 90, 270, fill=255,
                       width=max(1, round(W_LINE * K)))
            pts.append((x, yy))
        if n:
            self.num(n, x + 1.0, y0 - 1.5)
        return pts

    def dashdot(self, x0, y0, x1, y1, dash=12.0, gap=1.5, dot=1.0, w=W_THIN):
        """Dash-dot unit frame: dash 12, gap, dot, gap."""
        for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            Lseg = math.dist(a, b)
            ux, uy = (b[0] - a[0]) / Lseg, (b[1] - a[1]) / Lseg
            s = 0.0
            while s < Lseg:
                e = min(Lseg, s + dash)
                self.line([(a[0] + ux * s, a[1] + uy * s), (a[0] + ux * e, a[1] + uy * e)], w)
                s = e + gap
                if s < Lseg:
                    e = min(Lseg, s + dot)
                    self.line([(a[0] + ux * s, a[1] + uy * s), (a[0] + ux * e, a[1] + uy * e)], w)
                s = e + gap

    def arrow_out(self, x, y, dir=1, n=None):
        """A broken link line with a continuation number (to another sheet or unit)."""
        self.line([(x, y), (x + dir * 3.0, y)])
        self.d.polygon([self.P(x + dir * 3.0, y - 1.0), self.P(x + dir * 5.0, y), self.P(x + dir * 3.0, y + 1.0)],
                       fill=255)
        if n:
            self.num(n, x + dir * 1.0 - (3.0 if dir < 0 else 0), y - 1.4, 2.2)


# --- common-emitter stage -------------------------------------------------------------------------
def stage(s, x, yr, yg, rnd, nums):
    """Transistor, base divider, collector resistor, emitter resistor and capacitor. Returns
    (base node, collector node)."""
    ym = (yr + yg) / 2
    nR, nC, nT = nums
    tx = x + 18.0
    b, c, e = s.transistor(tx, ym, n=str(nT))
    xc = c[0]
    vals = ["1,5", "4,7", "10", "33", "68", "120", "2,2", "390", "820", "56", "15", "270"]
    t, bt = s.resistor(xc, (yr + c[1] - 3) / 2, n=str(nR), val=rnd.choice(vals))
    s.line([(xc, yr), t])
    s.line([bt, c])
    t, bt = s.resistor(xc, (e[1] + 3 + yg) / 2, n=str(nR + 1), val=rnd.choice(vals), left=True)
    s.line([e, t])
    s.line([bt, (xc, yg)])
    en = (xc, e[1] + 1.6)
    xe = xc + 7.0
    ct, cb = s.capacitor(xe, (e[1] + 3 + yg) / 2, n=str(nC), polar=True)
    s.line([en, (xe, en[1]), ct])
    s.line([cb, (xe, yg)])
    s.dot(*en)
    xb = x + 4.0
    t, bt = s.resistor(xb, (yr + ym) / 2 - 1.5, n=str(nR + 2), val=rnd.choice(vals))
    s.line([(xb, yr), t])
    s.line([bt, (xb, ym)])
    t, bt = s.resistor(xb, (ym + yg) / 2 - 0.5, n=str(nR + 3), val=rnd.choice(vals))
    s.line([(xb, ym), t])
    s.line([bt, (xb, yg)])
    s.line([(xb, ym), b])
    for p in ((xb, ym), (xb, yr), (xc, yr), (xb, yg), (xc, yg), (xe, yg)):
        s.dot(*p)
    return (xb, ym), (xc, c[1] - 1.8)


def make_schematic():
    rnd = random.Random(64)
    s = Sheet(L.PW * 1000, L.PH * 1000)
    # --- row 1: IF amplifier, five common-emitter stages ------------------------------------------
    yr, yg = 14.0, 76.0
    s.line([(-1, yr), (199, yr)])
    s.line([(-1, yg), (199, yg)])
    s.num("+12", 186, yr - 1.4, 2.5)
    s.ground(199, yg)
    nR, nC, nT = 31, 12, 4
    xs = [6.0, 42.0, 78.0, 114.0, 150.0]
    nodes = []
    for i, x in enumerate(xs):
        bn, cn = stage(s, x, yr, yg, rnd, (nR, nC, nT))
        # coupling capacitor: the input comes from the left edge of the sheet, then from the previous collector
        if i == 0:
            l, r = s.capacitor(bn[0] - 5.0, bn[1], vert=False, n=str(nC + 1))
            s.line([(-1.0, bn[1]), l])
            s.line([r, bn])
        else:
            pc = nodes[-1][1]
            l, r = s.capacitor(pc[0] + 9.0, pc[1], vert=False, n=str(nC + 1))
            s.line([pc, l])
            s.line([r, (bn[0], pc[1])])
            s.dot(*pc)
            s.dot(bn[0], pc[1])
        nodes.append((bn, cn))
        nR, nC, nT = nR + 4, nC + 2, nT + 1
    # the output of the last stage: a tank coil and a line to the right edge
    pc = nodes[-1][1]
    xk = pc[0] + 12.0
    s.line([pc, (xk, pc[1])])
    s.dot(*pc)
    t, bt = s.inductor(xk, pc[1] + 8.0, n=4, core=True)
    s.line([(xk, pc[1]), t])
    s.line([bt, (xk, pc[1] + 18.0), (201.0, pc[1] + 18.0)])
    s.num("57", xk + 2.5, pc[1] + 2.0)
    s.dashdot(-6.0, 6.0, 203.0, 83.0)

    # --- row 2: IC with a tank circuit, detector, regulator, transformer --------------------------
    y0 = 96.0
    pins = s.ic(14.0, y0, 22.0, 40.0, ["1", "2", "3", "4", "5", "6", "7"], ["14", "13", "12", "11", "10", "9", "8"],
                n="1")
    for p in ("1", "2", "3"):
        s.line([(-1, pins[p][1]), pins[p]])
    gx = pins["7"][0] - 4.0
    s.line([pins["7"], (gx, pins["7"][1]), (gx, y0 + 48.0)])
    s.ground(gx, y0 + 48.0)
    # tank circuit on pins 13-12: a coil and a capacitor in parallel
    a, b = pins["13"], pins["11"]
    xk = a[0] + 8.0
    s.line([a, (xk, a[1])])
    s.line([b, (xk, b[1])])
    t, bt = s.inductor(xk, (a[1] + b[1]) / 2, n=3)
    s.line([(xk, a[1]), t])
    s.line([bt, (xk, b[1])])
    xk2 = xk + 9.0
    ct, cb = s.capacitor(xk2, (a[1] + b[1]) / 2, n="28", val="47")
    s.line([(xk, a[1]), (xk2, a[1]), ct])
    s.line([(xk, b[1]), (xk2, b[1]), cb])
    s.dot(xk, a[1])
    s.dot(xk, b[1])
    # detector: a diode from pin 9 and an RC load
    p9 = pins["9"]
    da, db = s.diode(p9[0] + 12.0, p9[1], "r", n="3")
    s.line([p9, da])
    xo = db[0] + 6.0
    s.line([db, (xo, p9[1])])
    t, bt = s.resistor(xo, p9[1] + 10.0, n="47", val="3,3")
    s.line([(xo, p9[1]), t])
    s.ground(xo, bt[1])
    xcap = xo + 13.0
    ct, cb = s.capacitor(xcap, p9[1] + 9.0, n="29", val="0,01")
    s.line([(xo, p9[1]), (xcap, p9[1]), ct])
    s.ground(xcap, cb[1])
    s.dot(xo, p9[1])
    # regulator (variable resistor) and a line to the video amplifier
    xp = xcap + 14.0
    s.line([(xcap, p9[1]), (xp, p9[1])])
    s.dot(xcap, p9[1])
    t, bt = s.resistor(xp, p9[1] + 9.0, n="48", val="22", pot=True)
    s.line([(xp, p9[1]), t])
    s.ground(xp, bt[1])
    s.line([(xp + 6.0, p9[1] + 10.0), (xp + 12.0, p9[1] + 10.0), (xp + 12.0, y0 + 2.0), (xp + 30.0, y0 + 2.0)])
    s.dashdot(4.0, y0 - 6.0, xp + 18.0, y0 + 56.0)
    # IC supply: pin 14 through decoupling
    p14 = pins["14"]
    s.line([p14, (p14[0] + 3.0, p14[1]), (p14[0] + 3.0, y0 - 9.0), (130.0, y0 - 9.0)])
    # transformer: two windings on a core
    tx = 150.0
    t1, b1 = s.inductor(tx - 4.0, y0 + 20.0, n=5, side=1)
    t2, b2 = s.inductor(tx + 4.0, y0 + 20.0, n=4, side=-1)
    for dx in (-0.8, 0.8):
        s.line([(tx + dx, y0 + 12.0), (tx + dx, y0 + 28.0)], W_LINE)
    s.line([(130.0, y0 - 9.0), (130.0, t1[1]), t1])
    s.line([b1, (tx - 4.0, b1[1] + 6.0)])
    s.ground(tx - 4.0, b1[1] + 6.0)
    s.num("2", tx - 3.0, y0 + 9.0)
    # secondary: a diode rectifier and an electrolytic capacitor
    da, db = s.diode(tx + 19.0, t2[1] - 4.0, "r", n="7")
    s.line([t2, (tx + 4.0, t2[1] - 4.0), da])
    s.line([db, (tx + 30.0, t2[1] - 4.0)])
    ct, cb = s.capacitor(tx + 30.0, y0 + 26.0, n="31", val="500", polar=True)
    s.line([(tx + 30.0, t2[1] - 4.0), ct])
    s.line([b2, (tx + 4.0, y0 + 40.0), (tx + 30.0, y0 + 40.0), cb])
    s.dot(tx + 30.0, t2[1] - 4.0)
    s.line([(tx + 30.0, t2[1] - 4.0), (tx + 44.0, t2[1] - 4.0)])
    s.num("+24", tx + 36.0, t2[1] - 5.4, 2.5)
    s.ground(tx + 17.0, y0 + 40.0)
    s.dot(tx + 17.0, y0 + 40.0)
    s.dashdot(122.0, y0 - 2.0, 199.0, y0 + 50.0)

    # --- row 3: a bundle of link lines to the connector, a diode bridge ---------------------------
    yb = 160.0
    xconn = 136.0
    cp = s.connector(xconn, yb - 2.0, 8, n="1")
    for i, (cx, cy) in enumerate(cp):
        xin = 26.0 + 9.0 * i
        s.line([(xin, cy), (cx, cy)])
        if i % 2 == 0:
            ytop_ = 151.5 if i < 4 else yb - 5.0
            s.line([(xin, cy), (xin, ytop_)])
            s.dot(xin, cy)
            s.num(str(10 + i), xin + 0.8, ytop_ + 3.0, 2.2)
        else:
            s.line([(xin, cy), (-1.0, cy)])
    for i in range(3):                                      # thick group link lines
        s.line([(-1.0, yb + 44.0 - 6.0 * i), (120.0 - 14.0 * i, yb + 44.0 - 6.0 * i),
                (126.0 - 14.0 * i, yb + 38.0 - 6.0 * i)], W_MAIN)
    # bridge
    mx, my = 176.0, yb + 18.0
    for (ax, ay, d_) in ((mx - 7, my - 7, "u"), (mx + 7, my - 7, "d"), (mx - 7, my + 7, "d"), (mx + 7, my + 7, "u")):
        s.diode(ax, ay, d_)
    s.line([(mx - 7, my - 9.5), (mx - 7, my - 12.0), (mx + 7, my - 12.0), (mx + 7, my - 9.5)])
    s.line([(mx - 7, my + 9.5), (mx - 7, my + 12.0), (mx + 7, my + 12.0), (mx + 7, my + 9.5)])
    s.line([(mx - 7, my - 4.5), (mx - 7, my + 4.5)])
    s.line([(mx + 7, my - 4.5), (mx + 7, my + 4.5)])
    # AC comes from the connector to the top and bottom nodes, DC from the side ones
    s.line([(xconn + 8.0, cp[0][1]), (mx, cp[0][1]), (mx, my - 12.0)])
    s.line([(xconn + 8.0, cp[7][1]), (mx, cp[7][1]), (mx, my + 12.0)])
    s.line([(mx - 7, my), (mx - 14.0, my)])
    s.ground(mx - 14.0, my)
    s.line([(mx + 7, my), (199.0, my)])
    s.num("+15", 189.0, my - 1.4, 2.5)
    for p in ((mx - 7, my), (mx + 7, my), (mx, my - 12.0), (mx, my + 12.0)):
        s.dot(*p)
    s.num("6", mx + 9.0, my - 13.0)

    # --- oscillograms and the voltage table above the title block ---------------------------------
    ytop, hbox = 210.0, 15.0
    for i in range(4):
        x0 = 4.0 + i * 28.0
        s.rect(x0, ytop, x0 + 24.0, ytop + hbox, W_THIN)
        s.line([(x0 + 2.0, ytop + hbox / 2), (x0 + 22.0, ytop + hbox / 2)], W_THIN * 0.7)
        pts = []
        for k in range(61):
            u = k / 60.0
            xx = x0 + 2.0 + 20.0 * u
            if i == 0:                                      # sine
                yy = math.sin(u * 4 * math.pi)
            elif i == 1:                                    # line pulses
                yy = 0.9 if (u * 3) % 1 < 0.18 else -0.5
            elif i == 2:                                    # sawtooth
                yy = 1.6 * ((u * 3) % 1) - 0.8
            else:                                           # composite colour TV signal: sync pulse and steps
                ph = (u * 2) % 1
                yy = -0.9 if ph < 0.08 else (0.8 - 0.3 * int(ph * 5) if ph > 0.2 else 0.1)
            pts.append((xx, ytop + hbox / 2 - yy * hbox * 0.36))
        s.line(pts, W_LINE)
        s.num(str(i + 1), x0 + 0.8, ytop - 0.8, 2.2)
        s.num(["1,5", "40", "6", "2,8"][i], x0 + 15.0, ytop + hbox + 3.6, 2.2)
    tx0, ty0, tw, th = 120.0, 206.0, 80.0, 25.0
    s.rect(tx0, ty0, tx0 + tw, ty0 + th, W_LINE)
    for r in range(1, 4):
        s.line([(tx0, ty0 + 6.25 * r), (tx0 + tw, ty0 + 6.25 * r)], W_THIN)
    for c in range(1, 8):
        xx = tx0 + 12.0 + 9.7 * (c - 1)
        s.line([(xx, ty0), (xx, ty0 + th)], W_THIN)
    for c in range(7):
        xx = tx0 + 12.0 + 9.7 * c
        s.num(str(c + 1), xx + 3.4, ty0 + 5.0, 2.2)
        for r in range(1, 4):
            v = rnd.choice(["0", "1,2", "3,5", "6,8", "11", "0,6", "4,2", "9,1", "12"])
            s.num(v, xx + 1.4, ty0 + 6.25 * r + 5.0, 2.2)
    for r in range(1, 4):
        s.num(str(r), tx0 + 4.5, ty0 + 6.25 * r + 5.0, 2.2)

    # --- frame and title block (GOST 2.104-68, form 1) --------------------------------------------
    s.line([(L.FRAME_R, -1.0), (L.FRAME_R, L.FRAME_B), (-1.0, L.FRAME_B)], W_MAIN)
    x0, y0_ = L.TB_X0, L.TB_Y0
    s.rect(x0, y0_, L.FRAME_R, L.FRAME_B, W_MAIN)
    for dx in (7, 17, 40, 55, 65):                          # left part: columns
        s.line([(x0 + dx, y0_), (x0 + dx, L.FRAME_B)], W_MAIN if dx in (7, 17, 40, 55, 65) else W_THIN)
    for r in range(1, 11):                                  # rows of 5 mm
        y = y0_ + 5 * r
        s.line([(x0, y), (x0 + 65, y)], W_MAIN if r in (5, 6) else W_THIN)
    xr = x0 + 65
    s.line([(xr, y0_ + 15), (L.FRAME_R, y0_ + 15)], W_MAIN)
    s.line([(xr + 70, y0_ + 15), (xr + 70, L.FRAME_B)], W_MAIN)
    for y in (y0_ + 20, y0_ + 35, y0_ + 40):
        s.line([(xr + 70, y), (L.FRAME_R, y)], W_MAIN)
    for x in (xr + 85, xr + 102):
        s.line([(x, y0_ + 15), (x, y0_ + 35)], W_MAIN)
    for x in (xr + 75, xr + 80):
        s.line([(x, y0_ + 20), (x, y0_ + 35)], W_THIN)
    s.line([(xr + 90, y0_ + 35), (xr + 90, y0_ + 40)], W_MAIN)
    # digits: the designation without the letter code, scale, sheet and number of sheets
    s.num("468157.001", xr + 26.0, y0_ + 10.6, 5.0)
    s.num("1:1", xr + 105.0, y0_ + 30.8, 3.5)
    s.num("1", xr + 84.0, y0_ + 39.2, 2.5)
    s.num("2", xr + 108.0, y0_ + 39.2, 2.5)

    # --- diazo copy print: the lines are slightly smeared, the density is uneven ------------------
    m = s.m.filter(ImageFilter.GaussianBlur(0.55))
    dens = Image.effect_noise((s.W // 8, s.H // 8), 40).resize((s.W, s.H), Image.BILINEAR)
    dens = dens.point(lambda v: max(150, min(255, 110 + v)))
    m = ImageChops.multiply(m, dens)
    ink = Image.new("RGBA", (s.W, s.H), L.INK + (0,))
    ink.putalpha(m)

    # signatures in the title block are blue pen flourishes (not letters)
    pen = Image.new("L", (s.W, s.H), 0)
    dp = ImageDraw.Draw(pen)
    for r, w in ((6, 11.0), (7, 9.0), (10, 10.0)):
        squiggle(dp, x0 + 41.5, y0_ + 5 * r + 4.0, w, 3.0, rnd)
    pen = pen.filter(ImageFilter.GaussianBlur(0.5))
    ink = paint(ink, pen, (40, 52, 128), 0.85)

    # red pencil: the third stage is circled, the collector resistor value is corrected, an arrow
    red = Image.new("L", (s.W, s.H), 0)
    dr = ImageDraw.Draw(red)
    tx3, ty3 = xs[2] + 18.0, (yr + yg) / 2
    pts = []
    for k in range(48):
        a = 2 * math.pi * k / 46 + 0.3
        rr = 11.5 + rnd.uniform(-0.6, 0.6)
        pts.append(((tx3 + 1.0 + rr * 1.15 * math.cos(a)) * K, (ty3 + rr * 0.95 * math.sin(a)) * K))
    dr.line(pts, fill=255, width=int(0.7 * K), joint="curve")
    xc3 = tx3 + 2.5
    yv = (yr + ty3 - 12) / 2 + 3.4
    dr.line([((xc3 + 2.6) * K, (yv - 1.0) * K), ((xc3 + 8.5) * K, (yv - 2.4) * K)], fill=255, width=int(0.5 * K))
    text(dr, "6,8", xc3 + 9.0, yv + 0.1, 3.5, width=int(0.55 * K), rnd=rnd, jitter=0.04, slant=0.15)
    dr.line([((tx3 + 14) * K, (ty3 + 9) * K), ((tx3 + 26) * K, (ty3 + 16) * K)], fill=255, width=int(0.5 * K))
    dr.line([((tx3 + 14) * K, (ty3 + 9) * K), ((tx3 + 17.5) * K, (ty3 + 9.2) * K)], fill=255, width=int(0.5 * K))
    dr.line([((tx3 + 14) * K, (ty3 + 9) * K), ((tx3 + 15.6) * K, (ty3 + 12.0) * K)], fill=255, width=int(0.5 * K))
    grain = Image.effect_noise((s.W, s.H), 90).point(lambda v: 255 if v > 100 else int(v * 2.0))
    red = ImageChops.multiply(red, grain).filter(ImageFilter.GaussianBlur(0.5))
    ink = paint(ink, red, (176, 52, 46), 0.9)

    # plain pencil: ticks at the checked values
    gr = Image.new("L", (s.W, s.H), 0)
    dg = ImageDraw.Draw(gr)
    for (cx, cy) in ((xs[0] + 27, 22), (xs[1] + 27, 22), (xs[3] + 27, 62), (60.0, 128.0), (96.0, 130.0)):
        dg.line([((cx - 1.2) * K, (cy - 0.4) * K), (cx * K, (cy + 1.0) * K), ((cx + 2.4) * K, (cy - 2.2) * K)],
                fill=255, width=int(0.35 * K), joint="curve")
    gr = ImageChops.multiply(gr, grain).filter(ImageFilter.GaussianBlur(0.4))
    ink = paint(ink, gr, (70, 70, 74), 0.6)

    # finger marks at the bent corner (graphite and dirt): light swirl-shaped blotches
    fp = Image.new("L", (s.W, s.H), 0)
    df = ImageDraw.Draw(fp)
    for (cx, cy, rx, ry, a) in ((193.0, 266.0, 7.5, 10.0, 30.0), (184.0, 281.0, 7.0, 9.0, 60.0)):
        for k in range(14):
            rr = 1.0 - k / 14.0
            df.ellipse([(cx - rx * rr) * K, (cy - ry * rr) * K, (cx + rx * rr) * K, (cy + ry * rr) * K],
                       outline=int(90 * (1 - 0.5 * rr)), width=int(0.25 * K))
        _ = a
    fp = ImageChops.multiply(fp, grain).filter(ImageFilter.GaussianBlur(1.6))
    ink = paint(ink, fp, (92, 90, 96), 0.55)
    save(ink, "schematic.png")
    return ink


def squiggle(d, x0, y0, w, h, rnd):
    """Signature flourish (not letters): slanted loops and a tail; mm."""
    pts, n = [], 36
    for i in range(n + 1):
        t = i / n
        a = t * math.pi * 6.0
        pts.append(((x0 + t * w + math.cos(a) * h * 0.36) * K,
                    (y0 - math.sin(a) * h * 0.45 * (1 - 0.5 * t) + rnd.uniform(-1, 1) * h * 0.04) * K))
    pts.append(((x0 + w * 1.2) * K, (y0 - h * 0.55) * K))
    d.line(pts, fill=255, width=max(1, int(0.3 * K)), joint="curve")


def paint(img, mask, col, strength):
    """Add a layer mask in colour col over RGBA img (alpha takes the maximum)."""
    m = mask.point(lambda v: int(v * strength))
    layer = Image.new("RGBA", img.size, col + (0,))
    layer.putalpha(m)
    return Image.alpha_composite(img, layer)


def composite(ink):
    """The sheet as it looks: blueprint paper and print - for what shows through the transparent disc."""
    base = Image.new("RGBA", ink.size, L.PAPER + (255,))
    return Image.alpha_composite(base, ink).convert("RGB")


# --- disc -----------------------------------------------------------------------------------------
CK = 10.0                         # px per mm for the disc
CN = int(L.CD_D * 1000 * CK)


def rainbow(n, seed, sat=0.55, val=0.92, base=(200, 204, 210), mix=0.75):
    """Diffraction rainbow by angle: wide colour sectors that repeat every half-turn, with rays along the
    radius; n is the image side (px)."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 1) for _ in range(4)]
    img = Image.new("RGB", (n, n))
    px = img.load()
    c = (n - 1) / 2
    for j in range(n):
        for i in range(n):
            x, y = i - c, j - c
            r = math.hypot(x, y) / c
            a = math.atan2(y, x)
            h = (2 * a / (2 * math.pi) + 0.08 * math.sin(3 * a + ph[0] * 6) + 0.15 * r + ph[1]) % 1.0
            v = val * (0.82 + 0.18 * math.cos(4 * a + ph[2] * 6)) * (0.9 + 0.1 * math.cos(r * 30 + ph[3] * 6))
            s_ = sat * (0.55 + 0.45 * abs(math.sin(2 * a + ph[3] * 3)))
            rr, gg, bb = colorsys.hsv_to_rgb(h, s_, v)
            px[i, j] = (int((rr * 255) * mix + base[0] * (1 - mix)), int((gg * 255) * mix + base[1] * (1 - mix)),
                        int((bb * 255) * mix + base[2] * (1 - mix)))
    return img.resize((CN, CN), Image.BICUBIC)


def ring_mask(r0, r1, blur=0.0):
    m = Image.new("L", (CN, CN), 0)
    d = ImageDraw.Draw(m)
    c = CN / 2
    d.ellipse([c - r1 * CK, c - r1 * CK, c + r1 * CK, c + r1 * CK], fill=255)
    if r0 > 0:
        d.ellipse([c - r0 * CK, c - r0 * CK, c + r0 * CK, c + r0 * CK], fill=0)
    return m.filter(ImageFilter.GaussianBlur(blur)) if blur else m


def under_disc(sheet_rgb):
    """The sheet under the disc in disc axes (what shows through the transparent clamping zone)."""
    a = math.radians(L.CD_ROT)
    ca, sa = math.cos(a), math.sin(a)
    half = L.CD_R * 1000
    cx = (L.CD_C[0] - L.X0) * 1000
    cy = (L.Y1 - L.CD_C[1]) * 1000
    s = K / CK
    data = (s * ca, s * sa, K * (cx - half * ca - half * sa),
            -s * sa, s * ca, K * (cy + half * sa - half * ca))
    return sheet_rgb.transform((CN, CN), Image.AFFINE, data, resample=Image.BICUBIC)


def make_cd(sheet_rgb):
    rnd = random.Random(641)
    R = {k: getattr(L, k) * 1000 for k in ("R_HOLE", "R_CLAMP", "R_LABEL0", "R_LABEL1", "CD_R")}
    img = Image.new("RGB", (CN, CN), (205, 207, 212))
    # mirror zones: the rainbow
    rb = rainbow(240, 7)
    img.paste(rb, (0, 0), ring_mask(R["R_CLAMP"] + 0.6, R["CD_R"]))
    # transparent clamping zone: the sheet under it, slightly greyer and lighter; the moulded ring and the
    # matrix digits
    under = under_disc(sheet_rgb)
    clear = Image.blend(under, Image.new("RGB", (CN, CN), (214, 218, 224)), 0.28)
    img.paste(clear, (0, 0), ring_mask(R["R_HOLE"], R["R_CLAMP"], 0.6))
    d = ImageDraw.Draw(img)
    c = CN / 2
    for rr, col, w in ((11.2, (188, 192, 198), 0.5), (R["R_CLAMP"] + 0.25, (150, 154, 162), 0.6)):
        d.ellipse([c - rr * CK, c - rr * CK, c + rr * CK, c + rr * CK], outline=col, width=max(1, int(w * CK)))
    mold = Image.new("L", (CN, CN), 0)
    dm = ImageDraw.Draw(mold)
    for k, s_ in enumerate(("0412", "17", "3")):            # matrix digits around the circle
        a = math.radians(200 + 70 * k)
        r = 13.6
        text(dm, s_, (c / CK) + r * math.cos(a) - 2.0, (c / CK) + r * math.sin(a) + 0.6, 1.4,
             width=max(1, int(0.18 * CK)), slant=0.0, scale=CK)
    img.paste((166, 170, 178), (0, 0), mold.filter(ImageFilter.GaussianBlur(0.4)))
    # label: white paper, an orange stripe, rules, a marker number
    lab = Image.new("RGB", (CN, CN), (243, 242, 236))
    dl = ImageDraw.Draw(lab)
    v0, v1 = 27.0, 40.0                                     # stripe: v from 27 to 40 mm (up)
    dl.rectangle([0, c - v1 * CK, CN, c - v0 * CK], fill=L.LINE_ORANGE)
    for v in (-34.5, -48.0):
        hw = math.sqrt(max(0.0, (R["R_LABEL1"] - 4.0) ** 2 - v * v))
        dl.line([(c - hw * CK, c - v * CK), (c + hw * CK, c - v * CK)], fill=(176, 178, 182), width=max(1, int(0.2 * CK)))
    mk = Image.new("L", (CN, CN), 0)
    dk = ImageDraw.Draw(mk)
    text(dk, "17-0412", -26.0 + c / CK, 33.5 + c / CK, 8.5, width=int(0.9 * CK), rnd=rnd, jitter=0.05, slant=0.12,
         scale=CK)
    text(dk, "26.04", -13.0 + c / CK, 47.0 + c / CK, 6.5, width=int(0.8 * CK), rnd=rnd, jitter=0.05, slant=0.12,
         scale=CK)
    mk = mk.filter(ImageFilter.GaussianBlur(0.7))
    lab.paste((26, 26, 30), (0, 0), mk)
    # wear and dirt along the label edge, scratches
    wear = Image.new("L", (CN, CN), 0)
    dw = ImageDraw.Draw(wear)
    for k in range(30):
        rr = R["R_LABEL1"] - rnd.uniform(0.0, 2.0)
        a0 = rnd.uniform(0, 360)
        dw.arc([c - rr * CK, c - rr * CK, c + rr * CK, c + rr * CK], a0, a0 + rnd.uniform(5, 30),
               fill=int(rnd.uniform(40, 110)), width=max(1, int(0.4 * CK)))
    for k in range(9):
        x, y = rnd.uniform(-50, 50), rnd.uniform(-50, 50)
        a = rnd.uniform(0, math.pi)
        ln = rnd.uniform(4, 14)
        dw.line([((c / CK + x) * CK, (c / CK + y) * CK),
                 ((c / CK + x + ln * math.cos(a)) * CK, (c / CK + y + ln * math.sin(a)) * CK)],
                fill=60, width=max(1, int(0.15 * CK)))
    lab.paste((150, 146, 136), (0, 0), wear.filter(ImageFilter.GaussianBlur(0.8)))
    img.paste(lab, (0, 0), ring_mask(R["R_LABEL0"], R["R_LABEL1"], 0.5))
    out = img.convert("RGBA")
    out.putalpha(ring_mask(R["R_HOLE"], R["CD_R"]))
    save(out, "cd_top.png")

    # data side: a stronger rainbow, the recorded CD-R zone darker
    data = rainbow(240, 9, sat=0.65, val=0.85, base=(120, 150, 165), mix=0.65)
    dye = Image.new("RGB", (CN, CN), (52, 92, 120))
    data.paste(Image.blend(data, dye, 0.45), (0, 0), ring_mask(23.0, 44.5, 1.0))
    data.paste(Image.blend(data, Image.new("RGB", (CN, CN), (150, 170, 140)), 0.25), (0, 0), ring_mask(44.5, 58.0, 1.0))
    data.paste((150, 156, 166), (0, 0), ring_mask(R["R_HOLE"], R["R_CLAMP"]))
    out = data.convert("RGBA")
    out.putalpha(ring_mask(R["R_HOLE"], R["CD_R"]))
    save(out, "cd_data.png")


if __name__ == "__main__":
    ink = make_schematic()
    make_cd(composite(ink))
