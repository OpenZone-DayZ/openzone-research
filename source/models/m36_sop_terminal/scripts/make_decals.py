"""Screens, keyboard, stencils and radio panel of the M36 SOP staff terminal (system Python +
Pillow). No letters: the screens show a schematic map, a tree of blocks and lines made of
strokes; digits appear only in the stencil numbers and in the frequency windows of the
counters. The stencil digits come from M32/M33. Positions are in layout.py.

    python make_decals.py      -> ../work/decal_*.png

- decal_crt_off.png / _on.png   CRT glass 268 x 201: dark glass with a glare / amber
                                phosphor - a schematic map (grid, contour lines, river,
                                road, markers), a column of lines and a scale on the right;
- decal_lcd_off.png / _on.png   laptop screen 246 x 184: dark matrix / a blue 90s shell
                                screen in a double frame: a research tree of blocks, a row
                                of function keys;
- decal_keys.png                laptop keyboard: light keys without letters, grey service
                                keys;
- decal_box1.png, _band.png,    numbers in white paint by stencil on the boxes and on the CRT
  decal_box2.png,               case, a stripe on the box;
  decal_crt_num.png
- decal_radio.png               top of the radio: counter windows with frequency digits,
                                scales around the knobs, socket frames, blank nameplates.
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 2                                   # supersampling, then downscaled - smooth edges
PX_M = 1400                             # pixels per meter (before downscaling)
K = PX_M * S
FONTS = "C:/Windows/Fonts/"
WHITE = (214, 212, 200)

# Stencil digits on a 6 x 10 grid - from M32/M33
DIGITS = {
    "0": [(0, 1, 1.2, 4.6), (0, 5.4, 1.2, 9), (4.8, 1, 6, 4.6), (4.8, 5.4, 6, 9), (1, 0, 5, 1.2), (1, 8.8, 5, 10)],
    "1": [(2.4, 0, 3.8, 4.6), (2.4, 5.4, 3.8, 10), (1.2, 0.6, 2.3, 1.8)],
    "2": [(0.4, 0, 5, 1.2), (4.8, 1, 6, 4.4), (0.6, 4.2, 5.4, 5.4), (0, 5.6, 1.2, 8.8), (0, 8.8, 6, 10)],
    "3": [(0.2, 0, 5, 1.2), (4.8, 1, 6, 4.4), (1.6, 4.4, 5, 5.6), (4.8, 5.6, 6, 9), (0.2, 8.8, 5, 10)],
    "4": [(0, 0, 1.2, 5.6), (0, 5.6, 4.2, 6.8), (3.6, 0, 4.8, 5.3), (3.6, 7.0, 4.8, 10)],
    "5": [(0.4, 0, 6, 1.2), (0, 0.6, 1.2, 4.4), (0.4, 4.2, 5, 5.4), (4.8, 5.6, 6, 9), (0, 8.8, 5, 10)],
    "7": [(0, 0, 4.6, 1.2), (4.8, 0, 6, 2.6), (3.6, 3.2, 4.8, 6.2), (2.6, 6.8, 3.8, 10)],
}


def font(name, h):
    return ImageFont.truetype(FONTS + name, max(8, int(h)))


def save(img, name):
    img = img.resize((img.width // S, img.height // S), Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, img.size)


def worn_mask(W, H, rnd, n, rmin, rmax, blur):
    """Worn-paint patches: 255 - paint intact, 0 - worn off (from M32)."""
    m = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(m)
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        r = rnd.uniform(rmin, rmax)
        d.ellipse((x - r, y - r * rnd.uniform(0.3, 1.0), x + r, y + r * rnd.uniform(0.3, 1.0)), fill=0)
    return m.filter(ImageFilter.GaussianBlur(blur))


def paint(m, rnd, name, col=WHITE, n=60, keep=70):
    """Mask -> white brushed paint: soft edge, worn in places (from M33)."""
    W, H = m.size
    m = m.filter(ImageFilter.GaussianBlur(1.0 * S))
    m = ImageChops.multiply(m, worn_mask(W, H, rnd, n, 1.5 * S, 7 * S, 1.2 * S).point(
        lambda v: keep + v * (255 - keep) // 255))
    img = Image.new("RGBA", (W, H), col + (0,))
    img.putalpha(m)
    save(img, name)


def stencil_digits(d, text, x, y, cell_h, fill=235):
    u = cell_h / 10.0
    for ch in text:
        for a, b, c, e in DIGITS[ch]:
            d.rectangle((x + a * u, y + b * u, x + c * u, y + e * u), fill=fill)
        x += 7.6 * u


def crt_finish(img, bg, W, H):
    """Phosphor glow, raster, darkening toward the tube edges (as in M31)."""
    glow = img.filter(ImageFilter.GaussianBlur(3 * S))
    img = ImageChops.add(img, glow.point(lambda v: v // 2))
    d = ImageDraw.Draw(img)
    for yy in range(0, H, 3 * S):
        d.line([(0, yy), (W, yy)], fill=(0, 0, 0), width=1)
    vign = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vign).rounded_rectangle((W * 0.02, H * 0.03, W * 0.98, H * 0.97), radius=int(W * 0.08), fill=255)
    vign = vign.filter(ImageFilter.GaussianBlur(W * 0.04))
    return Image.composite(img, Image.new("RGB", (W, H), bg), vign)


# =============================================================================
# CRT: a schematic map in amber phosphor
# =============================================================================
def make_crt():
    W, H = int(L.CRT_W * K), int(L.CRT_H * K)
    off = Image.new("RGB", (W, H), (30, 34, 32))
    d = ImageDraw.Draw(off)
    for i in range(H):
        k = max(0.0, 1.0 - i / (H * 0.8))
        d.line([(0, i), (W, i)], fill=(int(30 + 12 * k), int(34 + 13 * k), int(32 + 12 * k)))
    d.ellipse((W * 0.06, H * 0.05, W * 0.40, H * 0.30), fill=(56, 62, 60))
    off = off.filter(ImageFilter.GaussianBlur(10 * S))
    save(off.convert("RGBA"), "decal_crt_off.png")

    BG, FG, HI, DIM = (14, 7, 2), (250, 168, 40), (255, 226, 150), (110, 62, 12)
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    rnd = random.Random(36)
    lw = max(2, int(W * 0.004))
    mx1 = W * 0.70                                              # map left, column right
    my0, my1 = H * 0.07, H * 0.93
    d.rectangle((W * 0.03, my0, mx1, my1), outline=FG, width=lw)
    # square grid
    for i in range(1, 8):
        x = W * 0.03 + (mx1 - W * 0.03) * i / 8
        d.line([(x, my0), (x, my1)], fill=DIM, width=max(1, lw // 2))
    for j in range(1, 6):
        y = my0 + (my1 - my0) * j / 6
        d.line([(W * 0.03, y), (mx1, y)], fill=DIM, width=max(1, lw // 2))
    # contour lines - closed curves around two heights
    for cx, cy, rr in ((W * 0.22, H * 0.35, H * 0.20), (W * 0.52, H * 0.66, H * 0.16)):
        for k in range(4):
            r = rr * (1 - 0.22 * k)
            pts = []
            for s in range(41):
                a = 2 * math.pi * s / 40
                q = r * (1 + 0.18 * math.sin(3 * a + k) + 0.08 * math.cos(5 * a))
                pts.append((cx + q * math.cos(a) * 1.3, cy + q * math.sin(a)))
            d.line(pts, fill=DIM if k < 3 else FG, width=max(1, lw // 2))
    # river and road, dashed
    river = [(W * 0.03, H * 0.80), (W * 0.15, H * 0.74), (W * 0.30, H * 0.82), (W * 0.40, H * 0.55),
             (W * 0.36, H * 0.30), (W * 0.48, H * 0.12), (W * 0.60, H * 0.07)]
    d.line(river, fill=FG, width=lw * 2)
    road = [(W * 0.08, my0), (W * 0.18, H * 0.55), (W * 0.45, H * 0.85), (mx1, H * 0.78)]
    for (x0, y0), (x1, y1) in zip(road[:-1], road[1:]):
        n = 10
        for s in range(0, n, 2):
            d.line([(x0 + (x1 - x0) * s / n, y0 + (y1 - y0) * s / n),
                    (x0 + (x1 - x0) * (s + 1) / n, y0 + (y1 - y0) * (s + 1) / n)], fill=FG, width=lw)
    # markers: triangles, squares, circles; one is inside the cursor frame
    marks = [(0.12, 0.22, "t"), (0.27, 0.48, "s"), (0.33, 0.70, "c"), (0.55, 0.28, "t"), (0.60, 0.50, "s"),
             (0.48, 0.80, "c"), (0.64, 0.16, "s")]
    sz = H * 0.03
    for fx, fy, kind in marks:
        x, y = W * fx, H * fy
        if kind == "t":
            d.polygon([(x, y - sz), (x + sz, y + sz * 0.8), (x - sz, y + sz * 0.8)], fill=HI)
        elif kind == "s":
            d.rectangle((x - sz, y - sz, x + sz, y + sz), outline=HI, width=lw)
        else:
            d.ellipse((x - sz, y - sz, x + sz, y + sz), fill=FG)
    x, y = W * 0.60, H * 0.50
    d.rectangle((x - sz * 2.2, y - sz * 2.2, x + sz * 2.2, y + sz * 2.2), outline=HI, width=lw)
    d.line([(x - sz * 3.5, y), (x - sz * 2.4, y)], fill=HI, width=lw)
    d.line([(x + sz * 2.4, y), (x + sz * 3.5, y)], fill=HI, width=lw)
    # right column: lines made of strokes and a scale
    cx0, cx1 = W * 0.74, W * 0.97
    d.rectangle((cx0, my0, cx1, my1), outline=FG, width=lw)
    d.rectangle((cx0, my0, cx1, my0 + H * 0.06), fill=FG)
    rh = H / 26
    for i in range(12):
        y = my0 + H * 0.09 + i * rh
        x = cx0 + W * 0.015
        while x < cx1 - W * 0.03:
            w = rnd.uniform(0.02, 0.06) * W
            d.rectangle((x, y + rh * 0.3, min(x + w, cx1 - W * 0.015), y + rh * 0.7), fill=FG if i % 5 else HI)
            x += w + W * 0.012
    d.rectangle((cx0 + W * 0.015, H * 0.80, cx1 - W * 0.015, H * 0.85), outline=FG, width=lw)
    d.rectangle((cx0 + W * 0.015 + lw * 2, H * 0.80 + lw * 2, cx0 + (cx1 - cx0) * 0.55, H * 0.85 - lw * 2), fill=FG)
    img = crt_finish(img, BG, W, H)
    save(img.convert("RGBA"), "decal_crt_on.png")


# =============================================================================
# Laptop: a blue 90s shell screen, the research tree
# =============================================================================
def make_lcd():
    W, H = int(L.LCD_W * K), int(L.LCD_H * K)
    off = Image.new("RGB", (W, H), (30, 33, 32))
    d = ImageDraw.Draw(off)
    for i in range(W):
        k = max(0.0, 1.0 - abs(i / W - 0.3) * 2.5)
        d.line([(i, 0), (i, H)], fill=(int(30 + 8 * k), int(33 + 8 * k), int(32 + 8 * k)))
    off = off.filter(ImageFilter.GaussianBlur(8 * S))
    save(off.convert("RGBA"), "decal_lcd_off.png")

    BG, FR, WH, YE, BK, CY = (8, 10, 150), (80, 200, 210), (220, 222, 226), (240, 230, 90), (6, 6, 8), (40, 150, 160)
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    rnd = random.Random(37)
    lw = max(2, int(W * 0.004))
    rh = H / 25.0
    cw = W / 80.0
    # top menu line - turquoise with black "words"
    d.rectangle((0, 0, W, rh), fill=CY)
    for k in range(6):
        d.rectangle((cw * (2 + 12 * k), rh * 0.3, cw * (8 + 12 * k), rh * 0.7), fill=BK)
    # double window frame
    x0, y0, x1, y1 = cw, rh * 1.6, W - cw, H - rh * 2.2
    d.rectangle((x0, y0, x1, y1), outline=FR, width=lw)
    d.rectangle((x0 + lw * 2.5, y0 + lw * 2.5, x1 - lw * 2.5, y1 - lw * 2.5), outline=FR, width=lw)
    d.rectangle(((x0 + x1) / 2 - cw * 8, y0 - lw, (x0 + x1) / 2 + cw * 8, y0 + lw * 3), fill=BG)
    d.rectangle(((x0 + x1) / 2 - cw * 6, y0 - rh * 0.2, (x0 + x1) / 2 + cw * 6, y0 + rh * 0.3), fill=WH)
    # tree: the root on top, branches going down; researched blocks are filled white, the
    # available one yellow, locked ones are outlines only
    bw, bh = cw * 9, rh * 1.6
    root = (W * 0.50, rh * 4.2)
    lv1 = [(W * 0.20, rh * 9.0), (W * 0.50, rh * 9.0), (W * 0.80, rh * 9.0)]
    lv2 = [(W * 0.12, rh * 14.0), (W * 0.28, rh * 14.0), (W * 0.50, rh * 14.0), (W * 0.72, rh * 14.0),
           (W * 0.88, rh * 14.0)]
    lv3 = [(W * 0.20, rh * 19.0), (W * 0.50, rh * 19.0), (W * 0.80, rh * 19.0)]
    edges = [(root, p) for p in lv1] + [(lv1[0], lv2[0]), (lv1[0], lv2[1]), (lv1[1], lv2[2]), (lv1[2], lv2[3]),
                                        (lv1[2], lv2[4]), (lv2[0], lv3[0]), (lv2[2], lv3[1]), (lv2[4], lv3[2])]
    done = {root, lv1[0], lv1[2], lv2[0], lv2[4]}
    avail = {lv2[1], lv3[0], lv3[2], lv1[1]}
    for a, b in edges:
        ym = (a[1] + b[1]) / 2
        d.line([(a[0], a[1] + bh / 2), (a[0], ym), (b[0], ym), (b[0], b[1] - bh / 2)],
               fill=WH if b in done else FR, width=lw)
    for p in [root] + lv1 + lv2 + lv3:
        box = (p[0] - bw / 2, p[1] - bh / 2, p[0] + bw / 2, p[1] + bh / 2)
        if p in done:
            d.rectangle(box, fill=WH)
            d.rectangle((box[0] + cw * 1.5, p[1] - rh * 0.18, box[2] - cw * 1.5, p[1] + rh * 0.18), fill=BG)
        elif p in avail:
            d.rectangle(box, fill=YE)
            d.rectangle((box[0] + cw * 1.5, p[1] - rh * 0.18, box[2] - cw * 3.5, p[1] + rh * 0.18), fill=BK)
        else:
            d.rectangle(box, outline=FR, width=lw)
    # selected block - an inverted frame
    c = lv2[1]
    d.rectangle((c[0] - bw / 2 - lw * 3, c[1] - bh / 2 - lw * 3, c[0] + bw / 2 + lw * 3, c[1] + bh / 2 + lw * 3),
                outline=WH, width=lw)
    # status line and function keys at the bottom: a black digit-stroke + a turquoise field
    y = H - rh * 1.6
    for i in range(10):
        x = cw * (1 + 8 * i)
        d.rectangle((x, y + rh * 0.25, x + cw * 1.2, y + rh * 0.9), fill=WH)
        d.rectangle((x + cw * 1.6, y, x + cw * 7.4, y + rh * 1.2), fill=CY)
    d.rectangle((cw * 3, H - rh * 2.05, W * rnd.uniform(0.3, 0.5), H - rh * 1.8), fill=FR)
    img = img.filter(ImageFilter.GaussianBlur(0.6 * S))
    save(img.convert("RGBA"), "decal_lcd_on.png")


# =============================================================================
# Laptop keyboard
# =============================================================================
def make_keys():
    """CF-27 keyboard: light yellowed keys, grey service keys, arrows at the bottom right, no
    letters; some keys are worn and darker.
    """
    x0, x1, y0, y1 = L.KEYS
    W, H = int((x1 - x0) * K), int((y1 - y0) * K)
    img = Image.new("RGBA", (W, H), (20, 20, 21, 255))
    d = ImageDraw.Draw(img)
    rnd = random.Random(36)
    LIGHT, GREY = (214, 206, 180), (156, 156, 150)
    gap = 0.0012 * K
    u = W / 15.0
    kh = H / 6.0

    def key(cx, cy, w, h, grey):
        tone = GREY if grey else LIGHT
        k = rnd.uniform(0.82, 0.95) if rnd.random() < 0.3 else 1.0
        c = tuple(int(v * k) for v in tone) + (255,)
        d.rounded_rectangle((cx + gap, cy + gap, cx + w * u - gap, cy + h * kh - gap), radius=int(gap), fill=c)
        d.line([(cx + gap * 2, cy + h * kh - gap * 1.5), (cx + w * u - gap * 2, cy + h * kh - gap * 1.5)],
               fill=tuple(int(v * 0.72) for v in tone) + (255,), width=S)
    # the F-key row is low
    for i in range(15):
        key(i * u, 0, 1, 0.8, 1 if i in (0, 13, 14) else 0)
    rows = [(1, [(i, 1, 0) for i in range(13)] + [(13, 2, 1)]),
            (2, [(0, 1.5, 1)] + [(1.5 + i, 1, 0) for i in range(12)] + [(13.5, 1.5, 1)]),
            (3, [(0, 1.75, 1)] + [(1.75 + i, 1, 0) for i in range(11)] + [(12.75, 2.25, 1)]),
            (4, [(0, 2.25, 1)] + [(2.25 + i, 1, 0) for i in range(10)] + [(12.25, 1.75, 1), (14, 1, 1)]),
            (5, [(0, 1, 1), (1, 1, 1), (2, 1, 1), (3, 1, 1), (4, 5, 0), (9, 1, 1), (10, 1, 1), (11, 1, 1),
                 (12, 1, 1), (13, 1, 1), (14, 1, 1)])]
    for r, ks in rows:
        for x, w, grey in ks:
            key(x * u, (r - 0.2) * kh + kh * 0.2, w, 1, grey)
    save(img, "decal_keys.png")


# =============================================================================
# Stencils: numbers on the boxes and the case, a stripe
# =============================================================================
def number(spec, name, seed, n=60, keep=70):
    rnd = random.Random(seed)
    W, H = int(spec["w"] * K), int(spec["h"] * K)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    ch = H * 0.86
    u = ch / 10
    tw = len(spec["text"]) * 7.6 * u - 1.6 * u
    stencil_digits(d, spec["text"], (W - tw) / 2, (H - ch) / 2, ch)
    paint(m, rnd, name, n=n, keep=keep)


def make_stencils():
    number(L.BOX1_NUM, "decal_box1.png", 361)
    number(L.BOX2_NUM, "decal_box2.png", 362, n=40)
    number(L.CRT_NUM, "decal_crt_num.png", 363, n=80, keep=50)
    b = L.BOX1_BAND
    rnd = random.Random(364)
    W, H = int(b["w"] * K), int(b["h"] * K)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    d.rectangle((0, H * 0.05, W * 0.46, H * 0.95), fill=235)
    d.rectangle((W * 0.54, H * 0.05, W, H * 0.95), fill=235)
    paint(m, rnd, "decal_box1_band.png", n=50)


# =============================================================================
# Top of the radio
# =============================================================================
def make_radio():
    """Control panel from above (top view, x to the right, y goes up the picture away from the
    player): counter windows with the frequency in white digits on black, limb scales around
    the frequency knobs (ticks, digits 0-9), frames around the sockets and the lamp, two blank
    nameplates. The paint is light and worn in places.
    """
    x0, x1, y0, y1 = L.R_PANEL
    W, H = int((x1 - x0) * K), int((y1 - y0) * K)

    def P(x, y):
        return (x - x0) * K, (y1 - y) * K
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lw = max(2, int(0.0012 * K))
    PAINT = (210, 208, 196, 255)
    # frequency knob limbs
    for (kx, ky, r), (wx, wy) in zip(L.R_KNOBS, L.R_WINDOWS):
        cx, cy = P(kx, ky)
        R = (r + 0.006) * K
        for i in range(31):
            a = math.radians(-135 + 270 * i / 30)
            l = 0.006 * K if i % 5 == 0 else 0.0035 * K
            d.line([(cx + R * math.sin(a), cy - R * math.cos(a)),
                    (cx + (R + l) * math.sin(a), cy - (R + l) * math.cos(a))], fill=PAINT, width=lw)
        f = font("arialbd.ttf", 0.0055 * K)
        for i in range(0, 31, 5):
            a = math.radians(-135 + 270 * i / 30)
            q = R + 0.011 * K
            s = str(i // 3 if i < 30 else 0)
            tx, ty = cx + q * math.sin(a), cy - q * math.cos(a)
            l_, t_, r_, b_ = d.textbbox((0, 0), s, font=f)
            d.text((tx - (r_ - l_) / 2 - l_, ty - (b_ - t_) / 2 - t_), s, font=f, fill=PAINT)
    # counter windows: a painted frame, a black window, white drum digits
    ww, wh = L.R_WIN
    f = font("consolab.ttf", wh * 0.72 * K)
    for (wx, wy), (text, _) in zip(L.R_WINDOWS, L.R_FREQ):
        a = P(wx - ww / 2, wy + wh / 2)
        b = P(wx + ww / 2, wy - wh / 2)
        d.rectangle((a[0] - lw * 2, a[1] - lw * 2, b[0] + lw * 2, b[1] + lw * 2), outline=PAINT, width=lw)
        d.rectangle((a[0], a[1], b[0], b[1]), fill=(12, 12, 12, 255))
        digits = text.replace(".", "")
        cw = (b[0] - a[0]) / len(digits)
        for i, ch in enumerate(digits):
            cx = a[0] + cw * (i + 0.5)
            d.rectangle((cx - cw * 0.42, a[1] + lw, cx + cw * 0.42, b[1] - lw), fill=(30, 30, 30, 255))
            l_, t_, r_, b_ = d.textbbox((0, 0), ch, font=f)
            d.text((cx - (r_ - l_) / 2 - l_, (a[1] + b[1]) / 2 - (b_ - t_) / 2 - t_), ch, font=f, fill=(226, 224, 214, 255))
    # frames of the sockets, knobs and the lamp
    for sx, sy in L.R_SOCK:
        cx, cy = P(sx, sy)
        R = 0.017 * K
        d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=PAINT, width=lw)
    for kx, ky, r in L.R_SMALL:
        cx, cy = P(kx, ky)
        R = (r + 0.005) * K
        for i in range(11):
            a = math.radians(-120 + 240 * i / 10)
            d.line([(cx + R * math.sin(a), cy - R * math.cos(a)),
                    (cx + (R + 0.003 * K) * math.sin(a), cy - (R + 0.003 * K) * math.cos(a))], fill=PAINT, width=lw)
    lx, ly = P(*L.R_LAMP)
    R = 0.011 * K
    d.rectangle((lx - R, ly - R, lx + R, ly + R), outline=PAINT, width=lw)
    # blank nameplates - light metal with a frame
    for sx, sy, w, h in ((x0 + 0.03, 0.245, 0.07, 0.022), (x0 + 0.03, -0.010, 0.05, 0.014)):
        a, b = P(sx, sy + h / 2), P(sx + w, sy - h / 2)
        d.rectangle((a[0], a[1], b[0], b[1]), fill=(176, 176, 170, 255), outline=(90, 90, 86, 255), width=lw)
    # paint wear
    rnd = random.Random(365)
    mask = worn_mask(W, H, rnd, 140, 1.0 * S, 5 * S, 1.0 * S).point(lambda v: 90 + v * 165 // 255)
    al = ImageChops.multiply(img.getchannel("A"), mask)
    img.putalpha(al)
    save(img, "decal_radio.png")


if __name__ == "__main__":
    make_crt()
    make_lcd()
    make_keys()
    make_stencils()
    make_radio()
