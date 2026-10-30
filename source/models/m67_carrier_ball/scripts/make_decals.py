"""Images for the M67 "Ballistics" carrier (system Python + Pillow), without letters: the target rings and
digits, the protocol fields and digits.

    python make_decals.py      -> ../work/*.png

- target.png - the whole sheet of target No. 4 (RGBA, SHEET x SHEET, the image centre is the centre of
  the rings; alpha is the print, the holes and marks, the paper is in the generator's material): rings
  every 50 mm, a black "bull" D 200 with white rings, the inner ten, digits 1-9 on the vertical and
  horizontal; 9 mm holes with a torn edge, a wipe ring, and the paper of the next layer in shadow in
  the hole; two close-range holes with soot, powder specks, and scorching at the nearer one; in
  pencil, the distance by them and the total in a circle, a violet judge's stamp without text, an
  empty number field with handwritten digits;
- target_holes.png - the hole mask (L): hole 255, tears ~120 - for the relief (_nohq);
- protocol.png - an A5 shooting protocol form (RGBA, PROTO_W x PROTO_H, the top of the image is the top
  of the sheet): a blue diagonal band (the line colour, camoGround), items with numbers and lines for
  entries, a table for 10 shots with field numbers, a hit diagram with rings and a grid, signature
  lines; by hand, ballpoint digits, pencil hit points, the dispersion circle and the mean point of
  impact; signature flourishes and a violet stamp without text.

The fonts are our own (printed digits as strokes, handwritten ones as jittery strokes): the images do
not depend on system fonts. Sizes come from m67_layout.py (shared with build_m67.py).
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m67_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
PEN = (34, 44, 122)               # ballpoint pen
PENCIL = (88, 88, 92)
STAMP = (104, 64, 150)            # violet stamp ink


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
    "+": [[(0.05, 0.55), (0.55, 0.55)], [(0.30, 0.30), (0.30, 0.80)]],
    "/": [[(0.60, 0.0), (0.0, 1.0)]],
}


def glyphs(d, s, x, y, h, fill, width, slant=0.0, rnd=None, jitter=0.0, adv=0.80):
    """A string of digits from the bottom left corner (x, y), height h, all in px. rnd and jitter give the
    handwritten look."""
    cx = x
    for ch in s:
        if ch == " ":
            cx += h * 0.5
            continue
        hh = h * (rnd.uniform(0.9, 1.08) if rnd else 1.0)
        dy = rnd.uniform(-0.06, 0.06) * h if rnd else 0.0
        for stroke in GLYPH[ch]:
            pts = []
            for px, py in stroke:
                jx = jy = 0.0
                if rnd and jitter:
                    jx, jy = rnd.uniform(-1, 1) * jitter, rnd.uniform(-1, 1) * jitter
                pts.append((cx + (px + jx) * hh + (1 - py) * slant * hh, y - hh + (py + jy) * hh + dy))
            d.line(pts, fill=fill, width=width, joint="curve")
        cx += hh * (adv if ch not in ".:" else 0.42) * (rnd.uniform(0.92, 1.1) if rnd else 1.0)
    return cx


def text_w(s, h, adv=0.80):
    return sum(h * 0.5 if c == " " else h * (adv if c not in ".:" else 0.42) for c in s) - h * (adv - 0.62)


def squiggle(d, x0, y0, w, h, rnd, col, width):
    """Signature flourish (not letters): slanted loops and a tail; px."""
    pts, n = [], 44
    for i in range(n + 1):
        t = i / n
        a = t * math.pi * 7.0
        pts.append((x0 + t * w + math.cos(a) * h * 0.36, y0 - math.sin(a) * h * 0.5 * (1 - 0.5 * t)
                    + rnd.uniform(-1, 1) * h * 0.04))
    pts.append((x0 + w * 1.25, y0 - h * 0.65))
    d.line(pts, fill=col, width=width, joint="curve")


def stamp_mask(r, rnd, strength=0.8):
    """Round stamp without text: two rings with strokes between them around the circle (like a line of text,
    but not letters), a star in the centre; the ink goes on unevenly. Returns an L mask of side ~2r."""
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
    m = m.point(lambda v: int(v * strength)).filter(ImageFilter.GaussianBlur(0.8))
    return m.rotate(rnd.uniform(-25, 25))


def put(img, col, mask, x, y):
    """Put colour col through mask (L) centred at (x, y) onto RGBA img: alpha takes the maximum."""
    w, h = mask.size
    layer = Image.new("RGBA", img.size, col + (0,))
    full = Image.new("L", img.size, 0)
    full.paste(mask, (int(x - w / 2), int(y - h / 2)))
    layer.putalpha(full)
    return Image.alpha_composite(img, layer)


def paint(img, mask, col, strength=1.0):
    """A layer of colour col through the mask over the full size of img."""
    m = mask.point(lambda v: int(v * strength)) if strength != 1.0 else mask
    layer = Image.new("RGBA", img.size, col + (0,))
    layer.putalpha(m)
    return Image.alpha_composite(img, layer)


# --- target ---------------------------------------------------------------------------------------
TK = 6.0                                  # px per mm
TN = int(L.SHEET * 1000 * TK)


def TP(s, t):
    """mm from the centre of the rings (s to the right, t up) -> image px."""
    return (TN / 2 + s * TK, TN / 2 - t * TK)


def hole_shape(r, rnd, n=40):
    """Ragged hole outline: a radius with unevenness by angle (px)."""
    ph = [rnd.uniform(0, 6.3) for _ in range(4)]
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1.0 + 0.06 * math.sin(3 * a + ph[0]) + 0.05 * math.sin(5 * a + ph[1]) + rnd.uniform(-0.05, 0.05)
        pts.append((r * k * math.cos(a), r * k * math.sin(a)))
    return pts


def make_target():
    rnd = random.Random(67)
    ink = Image.new("RGBA", (TN, TN), (0, 0, 0, 0))
    # print: the black ink mask
    pm = Image.new("L", (TN, TN), 0)
    d = ImageDraw.Draw(pm)
    lw = max(1, round(0.45 * TK))
    cx, cy = TP(0, 0)

    def circ(r_mm, fill=None, outline=None, width=lw):
        r = r_mm * TK
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=width)
    circ(L.R_BLACK * 1000, fill=255)
    for r in L.R_RING:
        rm = r * 1000
        circ(rm, outline=0 if rm < L.R_BLACK * 1000 - 0.5 else 255)
    circ(L.R_X * 1000, outline=0)
    # digits 1-9 on the vertical and horizontal: in the middle of their zone, white in the black
    h = 9.0 * TK
    for k in range(1, 10):
        rm = 25.0 * (10.5 - k)
        s = str(k)
        w = text_w(s, h)
        col = 0 if rm < L.R_BLACK * 1000 else 255
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            px, py = TP(dx * rm, dy * rm)
            glyphs(d, s, px - w / 2, py + h / 2, h, col, max(1, round(1.25 * TK)), adv=0.80)
    # the target number field (empty, no caption) in the upper half to the left of the axis
    bx0, by0 = TP(52, 241)
    bx1, by1 = TP(84, 229)
    d.rectangle([bx0, by0, bx1, by1], outline=255, width=lw)
    # the print is not perfect: the ink is slightly blotchy, the edges are soft
    grain = Image.effect_noise((TN // 4, TN // 4), 40).resize((TN, TN)).point(lambda v: min(255, 238 + v // 8))
    pm = ImageChops.multiply(pm, grain).filter(ImageFilter.GaussianBlur(0.5))
    # solid ink is opaque: the gamma of black is steep, 1 % of paper showing through is already a grey grain
    pm = pm.point(lambda v: 255 if v > 228 else v)
    ink = paint(ink, pm, L.INK)

    holes = Image.new("L", (TN, TN), 0)
    hd = ImageDraw.Draw(holes)
    for s, t, r, kind in L.HOLES:
        x, y = TP(s, t)
        R = r * TK
        on_black = math.hypot(s, t) < L.R_BLACK * 1000 - r
        # soot and powder specks (before the hole: the hole goes on top)
        if kind:
            near = kind == "soot"
            sr = (15.0 if near else 22.0) * TK
            n = int(sr * 2.6)
            m = Image.radial_gradient("L").resize((n, n)).point(lambda v: max(0, 255 - v * (1.45 if near else 1.25)))
            m = m.resize((n, int(n * rnd.uniform(0.8, 0.9)))).rotate(rnd.uniform(0, 180), expand=True)
            tex = Image.effect_noise(m.size, 70).point(lambda v: 130 + v // 2)
            m = ImageChops.multiply(m, tex).filter(ImageFilter.GaussianBlur(2.5))
            ink = put(ink, (40, 38, 36), m.point(lambda v: int(v * (0.92 if near else 0.55))), x + R * 0.4, y - R * 0.2)
            spm = Image.new("L", (TN, TN), 0)
            sd = ImageDraw.Draw(spm)
            for _ in range(140 if near else 220):
                a = rnd.uniform(0, 2 * math.pi)
                rr = abs(rnd.gauss(0, (11.0 if near else 18.0))) * TK + R
                pr = rnd.uniform(0.25, 0.7) * TK
                px, py = x + rr * math.cos(a), y + rr * math.sin(a)
                sd.ellipse([px - pr, py - pr, px + pr, py + pr], fill=rnd.randint(150, 255))
            ink = paint(ink, spm, (30, 28, 30))
            if near:                                         # scorching: a brown rim around the hole
                bm = Image.new("L", (TN, TN), 0)
                ImageDraw.Draw(bm).polygon([(x + px * 1.9, y + py * 1.9) for px, py in hole_shape(R, rnd)], fill=200)
                bm = bm.filter(ImageFilter.GaussianBlur(2.2 * TK))
                ink = paint(ink, bm, (112, 74, 38), 0.85)
        # tears: short rays from the edge - the paper tears in a star, the edges are lighter
        tear = Image.new("L", (TN, TN), 0)
        td = ImageDraw.Draw(tear)
        for _ in range(rnd.randint(4, 7)):
            a = rnd.uniform(0, 2 * math.pi)
            l0, l1 = R * 0.9, R + rnd.uniform(0.8, 2.6) * TK
            td.line([(x + l0 * math.cos(a), y + l0 * math.sin(a)), (x + l1 * math.cos(a), y + l1 * math.sin(a))],
                    fill=255, width=max(1, round(0.35 * TK)))
        hd.bitmap((0, 0), tear.point(lambda v: v // 2))
        # wipe ring: a grey ring along the edge (not visible on black, where the fibres are light)
        shape = hole_shape(R, rnd)
        ring = Image.new("L", (TN, TN), 0)
        ImageDraw.Draw(ring).polygon([(x + px * 1.22, y + py * 1.22) for px, py in shape], fill=255)
        ring = ring.filter(ImageFilter.GaussianBlur(0.7 * TK))
        if on_black:
            ink = paint(ink, tear, (196, 192, 182), 0.8)
            ink = paint(ink, ring, (70, 68, 66), 0.35)
        else:
            ink = paint(ink, ring, (82, 80, 80), 0.75)
            ink = paint(ink, tear, (90, 88, 86), 0.6)
        # hole: under it the back of the next layer in shadow, lighter towards one edge
        hm = Image.new("L", (TN, TN), 0)
        ImageDraw.Draw(hm).polygon([(x + px, y + py) for px, py in shape], fill=255)
        hd.polygon([(x + px, y + py) for px, py in shape], fill=255)
        sh = Image.new("L", (TN, TN), 0)
        ImageDraw.Draw(sh).ellipse([x - R * 0.7 + R * 0.35, y - R * 0.7 + R * 0.35, x + R * 0.7 + R * 0.35,
                                    y + R * 0.7 + R * 0.35], fill=255)
        ink = paint(ink, hm, (150, 146, 138))
        ink = paint(ink, ImageChops.multiply(sh.filter(ImageFilter.GaussianBlur(R * 0.3)), hm), (196, 192, 182), 0.8)
    save(holes, "target_holes.png")

    # pencil and pen: the distance by the holes with soot (cm), the total in a circle, the number in the field
    dd = ImageDraw.Draw(ink)
    hh = 7.0 * TK
    for s, t, r, kind in L.HOLES:
        if kind:
            x, y = TP(s + 9.0, t + 10.0)
            glyphs(dd, "2" if kind == "soot" else "15", x, y, hh, PENCIL + (215,), max(1, round(0.5 * TK)),
                   slant=0.2, rnd=rnd, jitter=0.03)
            dd.line([TP(s + 8.0, t + 8.5), TP(s + 4.5, t + 5.0)], fill=PENCIL + (200,), width=max(1, round(0.45 * TK)))
    x, y = TP(32, 168)
    glyphs(dd, "81", x, y, 11.0 * TK, PENCIL + (225,), max(1, round(0.6 * TK)), slant=0.2, rnd=rnd, jitter=0.03)
    pts = []
    for i in range(41):
        a = 2 * math.pi * i / 40 * 1.08
        pts.append(TP(38.5 + 12.5 * math.cos(a) + rnd.uniform(-0.4, 0.4), 173.0 + 9.5 * math.sin(a)))
    dd.line(pts, fill=PENCIL + (200,), width=max(1, round(0.45 * TK)), joint="curve")
    x, y = TP(58, 231.5)
    glyphs(dd, "17", x, y, 9.0 * TK, PEN + (230,), max(1, round(0.5 * TK)), slant=0.2, rnd=rnd, jitter=0.03)
    # judge's stamp (no text) by the field
    ink = put(ink, STAMP, stamp_mask(15.0 * TK, rnd, 0.75), *TP(24, 214))
    # finger marks and graphite at the folds - the paper was held by the corner
    sm = Image.new("L", (TN, TN), 0)
    smd = ImageDraw.Draw(sm)
    for s, t, rr in ((8, 12, 20), (60, -4, 16), (-3, 70, 14), (130, 4, 18)):
        x, y = TP(s, t)
        smd.ellipse([x - rr * TK, y - rr * TK * 0.7, x + rr * TK, y + rr * TK * 0.7], fill=rnd.randint(40, 70))
    sm = ImageChops.multiply(sm, Image.effect_noise((TN, TN), 60).point(lambda v: 128 + v // 2))
    ink = paint(ink, sm.filter(ImageFilter.GaussianBlur(4 * TK)), (110, 104, 92), 0.5)
    save(ink, "target.png")
    return ink


# --- protocol -------------------------------------------------------------------------------------
PK = 8.0
PWp, PHp = int(L.PROTO_W * 1000 * PK), int(L.PROTO_H * 1000 * PK)


def make_protocol():
    rnd = random.Random(671)
    img = Image.new("RGBA", (PWp, PHp), (0, 0, 0, 0))
    P = lambda x, y: (x * PK, y * PK)  # noqa: E731
    # blue diagonal band (printed under everything else): from the bottom left corner to the top right
    bm = Image.new("L", (PWp, PHp), 0)
    a = math.radians(L.BAND_ANG)
    hw = L.BAND_W * 1000 / 2
    nx, ny = -math.sin(a), math.cos(a)                       # normal to the band axis (u, v up)
    cxm, cym = L.PROTO_W * 1000 / 2, L.PROTO_H * 1000 / 2
    far = 400.0
    poly = []
    for sgn, k in ((-1, -1), (-1, 1), (1, 1), (1, -1)):
        u = k * far * math.cos(a) + sgn * hw * nx
        v = k * far * math.sin(a) + sgn * hw * ny
        poly.append(P(cxm + u, cym - v))
    poly = [poly[0], poly[1], poly[2], poly[3]]
    ImageDraw.Draw(bm).polygon(poly, fill=255)
    tex = Image.effect_noise((PWp, PHp), 30).point(lambda v: min(255, 232 + v // 8))
    bm = ImageChops.multiply(bm, tex).filter(ImageFilter.GaussianBlur(0.6))
    img = paint(img, bm, L.BAND)

    pm = Image.new("L", (PWp, PHp), 0)
    d = ImageDraw.Draw(pm)
    W = lambda mm: max(1, round(mm * PK))  # noqa: E731

    def hl(y, x0, x1, w=0.25):
        d.line([P(x0, y), P(x1, y)], fill=255, width=W(w))

    def vl(x, y0, y1, w=0.25):
        d.line([P(x, y0), P(x, y1)], fill=255, width=W(w))

    def num(s, x, y, h=2.6):
        glyphs(d, s, x * PK, y * PK, h * PK, 255, W(0.3))

    hl(9.0, 8, 140, 0.7)
    hl(10.4, 8, 140, 0.25)
    # items 1-4: a number and a line for the entry
    items = [(1, 8, 19.5, 14, 70), (2, 76, 19.5, 82, 140), (3, 8, 28.0, 14, 70), (4, 76, 28.0, 82, 140)]
    for n, x, y, l0, l1 in items:
        num("%d." % n, x, y)
        hl(y + 0.4, l0, l1)
    # table: 6 fields, a row of field numbers, 10 shots, the total
    cols = [8, 17, 40, 63, 86, 103, 140]
    y0, rh = 34.0, 6.4
    rows = 13
    for i in range(rows + 1):
        hl(y0 + i * rh, cols[0], cols[-1], 0.5 if i in (0, 2, rows - 1, rows) else 0.25)
    for x in cols:
        vl(x, y0, y0 + rows * rh, 0.5 if x in (cols[0], cols[-1]) else 0.25)
    # the field header is empty (no captions), with short rule-"lines" for text: lines only
    for j in range(6):
        cxm2 = (cols[j] + cols[j + 1]) / 2
        num(str(j + 1), cxm2 - 0.8, y0 + rh * 2 - 1.6, 2.4)
    for i in range(10):
        num(str(i + 1), cols[0] + (1.6 if i < 9 else 0.6), y0 + rh * (3 + i) - 1.7, 2.6)
    ty = y0 + rows * rh
    # hit diagram: a 56 mm square with a 7 mm grid and rings
    sx0, sy0, sz = 9.0, ty + 7.0, 56.0
    d.rectangle([P(sx0, sy0), P(sx0 + sz, sy0 + sz)], outline=255, width=W(0.5))
    for k in range(1, 8):
        vl(sx0 + k * 7.0, sy0, sy0 + sz, 0.12)
        hl(sy0 + k * 7.0, sx0, sx0 + sz, 0.12)
    scx, scy = sx0 + sz / 2, sy0 + sz / 2
    for rr in (5.0, 10.0, 15.0, 20.0, 25.0):
        d.ellipse([P(scx - rr, scy - rr), P(scx + rr, scy + rr)], outline=255, width=W(0.3))
    vl(scx, sy0, sy0 + sz, 0.35)
    hl(scy, sx0, sx0 + sz, 0.35)
    # items 5-9 to the right of the diagram: lines for entries and signatures
    for n, y in ((5, sy0 + 6.0), (6, sy0 + 14.0), (7, sy0 + 22.0)):
        num("%d." % n, 72, y)
        hl(y + 0.4, 78, 140)
    for n, y in ((8, sy0 + 40.0), (9, sy0 + 52.0)):
        num("%d." % n, 72, y)
        hl(y + 0.4, 78, 140)
    grain = Image.effect_noise((PWp // 3, PHp // 3), 40).resize((PWp, PHp)).point(lambda v: 205 + v // 5)
    pm = ImageChops.multiply(pm, grain).filter(ImageFilter.GaussianBlur(0.45))
    img = paint(img, pm, (30, 30, 34))

    # by hand: ballpoint pen
    dd = ImageDraw.Draw(img)
    pw = max(1, round(0.32 * PK))

    def hand(s, x, y, h=3.6, col=PEN + (235,)):
        return glyphs(dd, s, x * PK, y * PK, h * PK, col, pw, slant=0.2, rnd=rnd, jitter=0.03)
    hand("12-07", 22, 18.6)
    hand("14.06", 90, 18.6)
    hand("25", 26, 27.1)
    hand("10", 96, 27.1)
    shots = [("+14", "+22", "26", "9"), ("+39", "+8", "40", "9"), ("+6", "+47", "47", "9"),
             ("+55", "+30", "63", "8"), ("+29", "+60", "67", "8"), ("+70", "+13", "71", "8"),
             ("+22", "+121", "123", "6"), ("+114", "+22", "116", "6"), ("+24", "-44", "50", "9"),
             ("-31", "+17", "35", "9")]
    for i, (x, y, r, sc) in enumerate(shots):
        yy = y0 + rh * (3 + i) - 1.2
        hand(x, cols[1] + 4, yy, 3.4)
        hand(y, cols[2] + 4, yy, 3.4)
        hand(r, cols[3] + 6, yy, 3.4)
        hand(sc, cols[4] + 6, yy, 3.4)
        if i in (6, 7):                                    # note: the shot distance, cm
            hand("2" if i == 6 else "15", cols[5] + 8, yy, 3.4)
    hand("81", cols[4] + 4, ty - 1.2, 3.6)
    # diagram: hit points in pencil (scale 1:5), the dispersion circle and the mean point of impact
    pd = ImageDraw.Draw(img)
    sc5 = 1 / 5.0
    for s, t, r, kind in L.HOLES:
        px, py = scx + s * sc5 * 1.0, scy - t * sc5 * 1.0
        if abs(px - scx) > sz / 2 - 1 or abs(py - scy) > sz / 2 - 1:
            continue
        rr = 0.9
        pd.ellipse([P(px - rr, py - rr), P(px + rr, py + rr)], fill=PENCIL + (235,))
    gx, gy = scx + 34.2 * sc5, scy - 29.6 * sc5
    pts = []
    for i in range(46):
        a = 2 * math.pi * i / 44
        rr = 8.6 + rnd.uniform(-0.2, 0.2)
        pts.append(P(gx + rr * math.cos(a), gy + rr * math.sin(a) * 0.97))
    pd.line(pts, fill=PENCIL + (215,), width=max(1, round(0.3 * PK)), joint="curve")
    pd.line([P(gx - 2.2, gy), P(gx + 2.2, gy)], fill=PENCIL + (230,), width=max(1, round(0.3 * PK)))
    pd.line([P(gx, gy - 2.2), P(gx, gy + 2.2)], fill=PENCIL + (230,), width=max(1, round(0.3 * PK)))
    hand("86", 92, sy0 + 5.2)
    hand("+34", 90, sy0 + 13.2)
    hand("+30", 90, sy0 + 21.2)
    squiggle(dd, 84 * PK, (sy0 + 39.4) * PK, 30 * PK, 6 * PK, rnd, PEN + (230,), pw)
    squiggle(dd, 88 * PK, (sy0 + 51.4) * PK, 26 * PK, 5 * PK, rnd, PEN + (230,), pw)
    img = put(img, STAMP, stamp_mask(13.0 * PK, rnd, 0.8), 122 * PK, (sy0 + 44.0) * PK)
    # stains: a graphite finger at the top edge (where the clip is), a drop at the bottom
    sm = Image.new("L", (PWp, PHp), 0)
    sd = ImageDraw.Draw(sm)
    sd.ellipse([P(96, 2), P(116, 16)], fill=55)
    sd.ellipse([P(20, 190), P(34, 200)], fill=40)
    sm = ImageChops.multiply(sm, Image.effect_noise((PWp, PHp), 60).point(lambda v: 128 + v // 2))
    img = paint(img, sm.filter(ImageFilter.GaussianBlur(3 * PK)), (100, 96, 88), 0.6)
    save(img, "protocol.png")
    return img


if __name__ == "__main__":
    make_target()
    make_protocol()
