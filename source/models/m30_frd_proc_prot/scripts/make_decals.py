"""Decals and the dial of the Freedom gas mask test stand M30 (system Python + Pillow). The decal
drawers and wear are a copy of make_decals.py of the M29 chest (which also has HIGH PRESSURE and NO
OIL), and those come from the M27 gunsmith's table (the first Freedom model: their look). Freedom
decals overlap, some carry short English words of the kind seen on equipment and in workshops (words
are allowed on Freedom decals only), the rest are pictograms and patterns. No names, brands, logos or
jokes. The decals are scuffed, faded, scratched, some have a peeled corner.

    python make_decals.py      -> ../work/decal_*.png

Faces (the layout is in layout.py):
- decal_apron_f.png  the face of the table apron - the densest;
- decal_apron_r.png  the right apron of the table;
- decal_blk_top.png  the top of the control unit (clear of the valves);
- decal_blk_side.png the right side of the unit;
- decal_comp.png     the face of the compressor receiver on the shelf;
- decal_gauge.png    the dial of a dia. 100 gauge: a 0-6 scale over 270 degrees, digits, a red zone from
                     5; there is no needle on it - the needle is a separate part (bone ozl_needle);
                     the same dial is used on the dia. 40 compressor gauge;
- decal_lcd_off.png  the unit display (a 3-digit LCD, 90 x 34 mm) "off": dark, no backlight;
- decal_lcd_f00..07  the "working" frames (frames): backlight, the pressure 2.38-2.44 jitters, the
                     measurement dot blinks, a level bar. Digits and signs only, no words.
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as L  # noqa: E402

sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "_kit")))
import kstickers  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 2                                   # supersampling, then downscaling - smooth edges
PX_M = 1400                             # pixels per meter (before downscaling)
K = PX_M * S
FONTS = "C:/Windows/Fonts/"

YELLOW, BLACK, WHITE = (236, 196, 30), (22, 22, 22), (238, 236, 226)
RED, ORANGE, BLUE = (196, 36, 30), (232, 112, 26), (34, 84, 160)
GREEN, PAPER = (60, 170, 60), (226, 218, 196)


def font(name, h):
    return ImageFont.truetype(FONTS + name, max(8, int(h)))


def text_fit(d, box, s, fname, fill):
    """A word centered in box, the font fitted to the width and height."""
    x0, y0, x1, y1 = box
    h = y1 - y0
    f = font(fname, h)
    while True:
        l, t, r, b = d.textbbox((0, 0), s, font=f)
        if (r - l) <= (x1 - x0) and (b - t) <= h or f.size <= 8:
            break
        f = font(fname, f.size * 0.92)
    l, t, r, b = d.textbbox((0, 0), s, font=f)
    d.text(((x0 + x1 - (r - l)) / 2 - l, (y0 + y1 - (b - t)) / 2 - t), s, font=f, fill=fill)


def bolt(d, cx, cy, h, fill):
    """Lightning bolt (the "high voltage" pictogram)."""
    p = [(0.10, -0.50), (-0.22, 0.06), (0.0, 0.06), (-0.12, 0.50), (0.24, -0.08), (0.02, -0.08), (0.16, -0.50)]
    d.polygon([(cx + x * h, cy + y * h) for x, y in p], fill=fill)


def arrow_up(d, cx, cy, h, fill):
    w = h * 0.5
    d.polygon([(cx, cy - h / 2), (cx - w / 2, cy - h / 2 + w * 0.6), (cx - w / 5, cy - h / 2 + w * 0.6),
               (cx - w / 5, cy + h / 2), (cx + w / 5, cy + h / 2), (cx + w / 5, cy - h / 2 + w * 0.6),
               (cx + w / 2, cy - h / 2 + w * 0.6)], fill=fill)


def glass(d, cx, cy, h, fill, bg):
    """A glass with a crack ("fragile")."""
    w = h * 0.45
    d.polygon([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w * 0.3, cy - h * 0.05),
               (cx + w * 0.06, cy + h * 0.05), (cx + w * 0.06, cy + h * 0.38), (cx + w * 0.35, cy + h / 2),
               (cx - w * 0.35, cy + h / 2), (cx - w * 0.06, cy + h * 0.38), (cx - w * 0.06, cy + h * 0.05),
               (cx - w * 0.3, cy - h * 0.05)], fill=fill)
    d.line([(cx - w * 0.05, cy - h / 2), (cx + w * 0.08, cy - h * 0.32), (cx - w * 0.06, cy - h * 0.22),
            (cx + w * 0.04, cy - h * 0.08)], fill=bg, width=max(2, int(h * 0.05)))


def umbrella(d, cx, cy, h, fill):
    r = h * 0.42
    d.pieslice((cx - r, cy - h / 2, cx + r, cy - h / 2 + 2 * r), 180, 360, fill=fill)
    lw = max(2, int(h * 0.06))
    d.line([(cx, cy - h / 2 + r), (cx, cy + h * 0.38)], fill=fill, width=lw)
    d.arc((cx - h * 0.14, cy + h * 0.24, cx, cy + h * 0.5), 0, 180, fill=fill, width=lw)
    for k in (-1, 0, 1):
        d.line([(cx + k * r * 0.6 - h * 0.06, cy + h * 0.02), (cx + k * r * 0.6 - h * 0.12, cy + h * 0.16)],
               fill=fill, width=lw)


def flame(d, cx, cy, h, fill):
    pts = []
    for i in range(41):
        a = 2 * math.pi * i / 40
        r = h * (0.30 + 0.18 * max(0.0, -math.sin(a)) ** 3)
        x = math.cos(a) * r * (0.75 + 0.25 * math.sin(a))
        y = math.sin(a) * r * 1.25 - (h * 0.25 * max(0.0, -math.sin(a)) ** 6)
        pts.append((cx + x, cy + y + h * 0.08))
    d.polygon(pts, fill=fill)
    d.line([(cx - h * 0.4, cy + h * 0.46), (cx + h * 0.4, cy + h * 0.46)], fill=fill, width=max(2, int(h * 0.06)))


def hazard(d, box, a, b, step):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=a)
    hgt = y1 - y0
    x = x0 - hgt
    while x < x1:
        d.polygon([(x, y1), (x + step / 2, y1), (x + step / 2 + hgt, y0), (x + hgt, y0)], fill=b)
        x += step


# --- decals: a function draws onto a w x h pixel image ---------------------------------------------
def st_caution(w, h):
    im = Image.new("RGB", (w, h), YELLOW)
    d = ImageDraw.Draw(im)
    b = int(h * 0.08)
    d.rectangle((b, b, w - b - 1, h - b - 1), outline=BLACK, width=max(2, b // 2))
    tri = h * 0.62
    d.polygon([(b * 3, h / 2 + tri / 2), (b * 3 + tri * 0.58, h / 2 - tri / 2), (b * 3 + tri * 1.16, h / 2 + tri / 2)],
              fill=BLACK)
    text_fit(d, (b * 3 + tri * 0.4, h / 2 - tri * 0.05, b * 3 + tri * 0.76, h / 2 + tri * 0.45), "!", "arialbd.ttf",
             YELLOW)
    text_fit(d, (b * 4 + tri * 1.16, h * 0.2, w - b * 3, h * 0.8), "CAUTION", "impact.ttf", BLACK)
    return im


def st_fragile(w, h):
    im = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), outline=RED, width=max(3, int(h * 0.07)))
    glass(d, h * 0.42, h / 2, h * 0.66, RED, WHITE)
    text_fit(d, (h * 0.8, h * 0.22, w - h * 0.12, h * 0.78), "FRAGILE", "arialbd.ttf", RED)
    return im


def st_voltage(w, h):
    im = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(im)
    tri = [(w / 2, h * 0.04), (w * 0.94, h * 0.66), (w * 0.06, h * 0.66)]
    d.polygon(tri, fill=BLACK)
    c = (w / 2, h * 0.44)
    d.polygon([(c[0] + (x - c[0]) * 0.8, c[1] + (y - c[1]) * 0.8) for x, y in tri], fill=YELLOW)
    bolt(d, w / 2, h * 0.45, h * 0.36, BLACK)
    text_fit(d, (w * 0.05, h * 0.71, w * 0.95, h * 0.95), "HIGH VOLTAGE", "arialbd.ttf", BLACK)
    return im


def st_sideup(w, h):
    im = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), outline=BLACK, width=max(2, int(h * 0.04)))
    for cx in (w * 0.33, w * 0.67):
        arrow_up(d, cx, h * 0.38, h * 0.5, BLACK)
    d.line([(w * 0.18, h * 0.66), (w * 0.82, h * 0.66)], fill=BLACK, width=max(2, int(h * 0.04)))
    text_fit(d, (w * 0.08, h * 0.72, w * 0.92, h * 0.93), "THIS SIDE UP", "arialbd.ttf", BLACK)
    return im


def st_keepdry(w, h):
    im = Image.new("RGB", (w, h), BLUE)
    d = ImageDraw.Draw(im)
    umbrella(d, w / 2, h * 0.40, h * 0.58, WHITE)
    text_fit(d, (w * 0.1, h * 0.76, w * 0.9, h * 0.94), "KEEP DRY", "arialbd.ttf", WHITE)
    return im


def st_warning(w, h):
    im = Image.new("RGB", (w, h), ORANGE)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, h * 0.7, h), fill=BLACK)
    text_fit(d, (h * 0.12, h * 0.1, h * 0.58, h * 0.9), "!", "impact.ttf", ORANGE)
    text_fit(d, (h * 0.85, h * 0.18, w - h * 0.15, h * 0.82), "WARNING", "impact.ttf", BLACK)
    return im


def st_danger(w, h):
    im = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, h * 0.62), fill=RED)
    d.ellipse((w * 0.1, h * 0.06, w * 0.9, h * 0.58), fill=WHITE)
    d.ellipse((w * 0.14, h * 0.11, w * 0.86, h * 0.53), fill=RED)
    text_fit(d, (w * 0.18, h * 0.14, w * 0.82, h * 0.5), "DANGER", "arialbd.ttf", WHITE)
    text_fit(d, (w * 0.12, h * 0.68, w * 0.88, h * 0.92), "KEEP OUT", "arialbd.ttf", BLACK)
    return im


def st_flammable(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(w / 2, 0), (w, h / 2), (w / 2, h), (0, h / 2)], fill=RED)
    d.polygon([(w / 2, h * 0.05), (w * 0.95, h / 2), (w / 2, h * 0.95), (w * 0.05, h / 2)], outline=WHITE,
              width=max(2, int(h * 0.02)))
    flame(d, w / 2, h * 0.36, h * 0.34, WHITE)
    text_fit(d, (w * 0.24, h * 0.58, w * 0.76, h * 0.68), "FLAMMABLE", "arialbd.ttf", WHITE)
    return im


def st_hazard(w, h):
    im = Image.new("RGB", (w, h), YELLOW)
    hazard(ImageDraw.Draw(im), (0, 0, w, h), YELLOW, BLACK, h * 1.4)
    return im


def st_nosmoke(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, w - 1, h - 1), fill=WHITE)
    lw = int(w * 0.09)
    d.rectangle((w * 0.2, h * 0.47, w * 0.72, h * 0.57), fill=BLACK)
    d.rectangle((w * 0.74, h * 0.47, w * 0.8, h * 0.57), fill=BLACK)
    d.arc((w * 0.74, h * 0.18, w * 0.9, h * 0.46), 200, 330, fill=BLACK, width=max(2, lw // 3))
    d.ellipse((lw / 2, lw / 2, w - 1 - lw / 2, h - 1 - lw / 2), outline=RED, width=lw)
    d.line([(w * 0.2, h * 0.2), (w * 0.8, h * 0.8)], fill=RED, width=lw)
    return im


def st_target(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, c in enumerate((WHITE, BLACK, WHITE, RED)):
        m = w * 0.13 * i
        d.ellipse((m, m, w - 1 - m, h - 1 - m), fill=c)
    lw = max(2, int(w * 0.02))
    d.line([(w / 2, 0), (w / 2, h)], fill=BLACK, width=lw)
    d.line([(0, h / 2), (w, h / 2)], fill=BLACK, width=lw)
    return im


def st_sun(w, h):
    """A pattern instead of graffiti: a circle with rays."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, w - 1, h - 1), fill=BLACK)
    c, r = w / 2, w * 0.46
    for k in range(16):
        a0, a1 = 2 * math.pi * k / 16, 2 * math.pi * (k + 0.5) / 16
        d.polygon([(c, c), (c + r * math.cos(a0), c + r * math.sin(a0)), (c + r * math.cos(a1), c + r * math.sin(a1))],
                  fill=GREEN if k % 2 else YELLOW)
    d.ellipse((c - w * 0.15, c - w * 0.15, c + w * 0.15, c + w * 0.15), fill=BLACK)
    return im


def st_chevrons(w, h):
    im = Image.new("RGB", (w, h), BLACK)
    d = ImageDraw.Draw(im)
    for i in range(5):
        x = w * (0.05 + 0.19 * i)
        d.polygon([(x, 0), (x + w * 0.09, 0), (x + w * 0.19, h / 2), (x + w * 0.09, h), (x, h), (x + w * 0.1, h / 2)],
                  fill=GREEN if i % 2 == 0 else WHITE)
    return im


def st_checker(w, h):
    im = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(im)
    n = 5
    for i in range(n):
        for j in range(n):
            if (i + j) % 2:
                d.rectangle((w * i / n, h * j / n, w * (i + 1) / n, h * (j + 1) / n), fill=BLACK)
    d.ellipse((w * 0.3, h * 0.3, w * 0.7, h * 0.7), fill=GREEN)
    return im


def st_star(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, w - 1, h - 1), fill=GREEN)
    c = w / 2
    pts = [(c + (w * (0.42 if k % 2 == 0 else 0.17)) * math.sin(math.pi * k / 5),
            c - (w * (0.42 if k % 2 == 0 else 0.17)) * math.cos(math.pi * k / 5)) for k in range(10)]
    d.polygon(pts, fill=WHITE)
    return im


def st_spiral(w, h):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, w - 1, h - 1), fill=YELLOW)
    c = w / 2
    pts = [(c + w * 0.42 * (t / 400) * math.cos(t / 400 * 6 * math.pi), c + w * 0.42 * (t / 400) * math.sin(t / 400 * 6 * math.pi))
           for t in range(401)]
    d.line(pts, fill=BLACK, width=max(2, int(w * 0.06)))
    return im


def st_pressure(w, h):
    """HIGH PRESSURE: a yellow warning diamond and the word."""
    im = Image.new("RGB", (w, h), YELLOW)
    d = ImageDraw.Draw(im)
    b = int(h * 0.07)
    d.rectangle((b, b, w - b - 1, h - b - 1), outline=BLACK, width=max(2, b // 2))
    c, r = h * 0.55, h * 0.36
    d.polygon([(c, h / 2 - r), (c + r, h / 2), (c, h / 2 + r), (c - r, h / 2)], fill=BLACK)
    for k in (-1, 0, 1):                                           # three arrows outward
        d.line([(c, h / 2), (c + r * 0.7, h / 2 + k * r * 0.45)], fill=YELLOW, width=max(2, int(h * 0.05)))
    text_fit(d, (c + r + b * 2, h * 0.16, w - b * 3, h * 0.84), "HIGH PRESSURE", "impact.ttf", BLACK)
    return im


def st_nooil(w, h):
    """NO OIL: a crossed-out oil can (oxygen and masks - no oil) and the word."""
    im = Image.new("RGB", (w, h), WHITE)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), outline=BLUE, width=max(3, int(h * 0.07)))
    c, r = h * 0.5, h * 0.36
    d.polygon([(c - r * 0.55, c + r * 0.45), (c + r * 0.25, c + r * 0.45), (c + r * 0.25, c - r * 0.05),
               (c + r * 0.75, c - r * 0.5), (c + r * 0.6, c - r * 0.6), (c, c - r * 0.1), (c - r * 0.55, c - r * 0.1)],
              fill=BLACK)
    lw = max(3, int(h * 0.08))
    d.ellipse((c - r, c - r, c + r, c + r), outline=RED, width=lw)
    d.line([(c - r * 0.7, c - r * 0.7), (c + r * 0.7, c + r * 0.7)], fill=RED, width=lw)
    text_fit(d, (h * 0.95, h * 0.2, w - h * 0.1, h * 0.8), "NO OIL", "arialbd.ttf", BLUE)
    return im


# kind -> (drawer, width, height in meters, shape: rect / round)
KINDS = {
    "caution": (st_caution, 0.13, 0.048, "rect"),
    "fragile": (st_fragile, 0.12, 0.056, "rect"),
    "voltage": (st_voltage, 0.075, 0.072, "rect"),
    "sideup": (st_sideup, 0.085, 0.070, "rect"),
    "keepdry": (st_keepdry, 0.060, 0.066, "rect"),
    "warning": (st_warning, 0.11, 0.040, "rect"),
    "danger": (st_danger, 0.080, 0.066, "rect"),
    "flammable": (st_flammable, 0.075, 0.075, "shape"),
    "hazard": (st_hazard, 0.15, 0.030, "rect"),
    "nosmoke": (st_nosmoke, 0.060, 0.060, "shape"),
    "target": (st_target, 0.065, 0.065, "shape"),
    "sun": (st_sun, 0.070, 0.070, "shape"),
    "chevrons": (st_chevrons, 0.10, 0.035, "rect"),
    "checker": (st_checker, 0.050, 0.050, "rect"),
    "star": (st_star, 0.055, 0.055, "shape"),
    "spiral": (st_spiral, 0.050, 0.050, "shape"),
    "pressure": (st_pressure, 0.14, 0.045, "rect"),
    "nooil": (st_nooil, 0.10, 0.044, "rect"),
}
KINDS.update(kstickers.kinds())


def round_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=255)
    return m


def wear_mask(w, h, rnd, n, rmin, rmax):
    """Worn spots: 255 - intact, 0 - worn off."""
    m = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(m)
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.uniform(rmin, rmax)
        d.ellipse((x - r, y - r * rnd.uniform(0.3, 1.0), x + r, y + r * rnd.uniform(0.3, 1.0)), fill=0)
    return m.filter(ImageFilter.GaussianBlur(1.2 * S))


def sticker(kind, rnd, scale=1.0):
    """RGBA decal: faded, scratched, edges worn, sometimes a peeled corner."""
    fn, wm, hm, shape = KINDS[kind]
    w, h = int(wm * scale * K), int(hm * scale * K)
    im = fn(w, h).convert("RGBA")
    if shape == "rect":
        a = round_mask(w, h, int(min(w, h) * 0.08))
        im.putalpha(ImageChops.multiply(im.getchannel("A"), a))
    rgb = im.convert("RGB")
    # faded in the light, yellowed and dusty
    fade = rnd.uniform(0.08, 0.30)
    rgb = Image.blend(rgb, Image.new("RGB", (w, h), (214, 204, 178)), fade)
    alpha = im.getchannel("A")
    # scratches: thin light strokes, the decal is worn off in them
    sc = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(sc)
    for _ in range(int(rnd.uniform(4, 14) * scale)):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        a = rnd.uniform(-0.5, 0.5) + (0 if rnd.random() < 0.7 else math.pi / 2)
        ln = rnd.uniform(0.1, 0.6) * w
        d.line([(x, y), (x + ln * math.cos(a), y + ln * math.sin(a))], fill=rnd.randint(0, 90),
               width=rnd.choice((1, 1, 2)) * S)
    worn = ImageChops.multiply(wear_mask(w, h, rnd, int(10 * scale) + 4, 1.5 * S, 5 * S), sc)
    # the edge is worn more
    edge = alpha.filter(ImageFilter.MinFilter(2 * (S * 2) + 1)).filter(ImageFilter.GaussianBlur(2 * S))
    worn = ImageChops.multiply(worn, edge.point(lambda v: 150 + v * 105 // 255))
    alpha = ImageChops.multiply(alpha, worn.point(lambda v: 105 + v * 150 // 255))
    out = rgb.copy()
    out.putalpha(alpha)
    # peeled corner: the corner is cut off, in its place the back (paper) folded over
    if shape == "rect" and rnd.random() < 0.4:
        c = rnd.randrange(4)
        s = int(min(w, h) * rnd.uniform(0.25, 0.45))
        cx, cy = (0 if c in (0, 3) else w), (0 if c in (0, 1) else h)
        sx, sy = (1 if cx == 0 else -1), (1 if cy == 0 else -1)
        tri = [(cx, cy), (cx + sx * s, cy), (cx, cy + sy * s)]
        cut = Image.new("L", (w, h), 255)
        ImageDraw.Draw(cut).polygon(tri, fill=0)
        out.putalpha(ImageChops.multiply(out.getchannel("A"), cut))
        fold = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(fold).polygon([(cx + sx * s, cy), (cx, cy + sy * s), (cx + sx * s * 0.9, cy + sy * s * 0.9)],
                                     fill=(206, 200, 184, 235))
        out = Image.alpha_composite(out, fold)
    return out.rotate(rnd.uniform(-14, 14), resample=Image.BICUBIC, expand=True)


def overlap(a, b):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    ix = max(0.0, min(ax1, bx1) - max(ax0, bx0))
    iy = max(0.0, min(ay1, by1) - max(ay0, by0))
    return ix * iy / min((ax1 - ax0) * (ay1 - ay0), (bx1 - bx0) * (by1 - by0))


def face(name, wm, hm, kinds, seed, max_ov=0.45, scale=(0.85, 1.15), keep_out=(), margin=0.01):
    """A wm x hm meter face (v is up), decals kinds at random places, overlapping by at most max_ov of the
    area of the smaller of the two; keep_out - [(u0, u1, v0, v1)] meters where there are no decals."""
    W, H = int(wm * K), int(hm * K)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rnd = random.Random(seed)
    boxes = []
    for kind in kinds:
        st = sticker(kind, rnd, rnd.uniform(*scale))
        sw, sh = st.size
        for _ in range(400):
            x = rnd.uniform(margin * K, W - sw - margin * K)
            y = rnd.uniform(margin * K, H - sh - margin * K)
            b = (x, y, x + sw, y + sh)
            ko = [((u0 * K), H - v1 * K, u1 * K, H - v0 * K) for u0, u1, v0, v1 in keep_out]
            if all(overlap(b, o) <= max_ov for o in boxes) and all(overlap(b, o) == 0 for o in ko):
                break
        else:
            print("  no room for", kind, "on", name)
            continue
        boxes.append(b)
        img.alpha_composite(st, (int(x), int(y)))
    save(img, name)


def save(img, name):
    img = img.resize((img.width // S, img.height // S), Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, img.size)


def make_gauge():
    """Gauge dial: white, a 0-6 scale over 270 degrees (zero at the bottom left, clockwise), small
    divisions every 0.1, digits every 1, a red arc from 5 to 6. No units or lettering; no needle."""
    W = int(L.GAUGE_D * K)
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c, r = W / 2, W / 2
    d.ellipse((0, 0, W - 1, W - 1), fill=(232, 230, 220, 255))
    d.arc((r * 0.14, r * 0.14, W - r * 0.14, W - r * 0.14), 135 + 225, 135 + 270, fill=RED, width=int(W * 0.035))
    for i in range(61):
        a = math.radians(135 + 270 * i / 60)
        ln = r * (0.16 if i % 10 == 0 else 0.10 if i % 5 == 0 else 0.06)
        d.line([(c + (r * 0.88) * math.cos(a), c + (r * 0.88) * math.sin(a)),
                (c + (r * 0.88 - ln) * math.cos(a), c + (r * 0.88 - ln) * math.sin(a))], fill=BLACK,
               width=max(2, int(W * (0.016 if i % 10 == 0 else 0.008))))
    f = font("arialbd.ttf", W * 0.10)
    for v in range(7):
        a = math.radians(135 + 45 * v)
        x, y = c + r * 0.56 * math.cos(a), c + r * 0.56 * math.sin(a)
        l, t, rr, b = d.textbbox((0, 0), str(v), font=f)
        d.text((x - (rr - l) / 2 - l, y - (b - t) / 2 - t), str(v), font=f, fill=BLACK)
    rnd = random.Random(11)
    a = ImageChops.multiply(img.getchannel("A"), wear_mask(W, W, rnd, 30, 1 * S, 3 * S).point(lambda v: 200 + v * 55 // 255))
    img.putalpha(a)
    save(img, "decal_gauge.png")


# --- display: seven-segment digits -----------------------------------------------------------------
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
       "7": "abc", "8": "abcdefg", "9": "abcdfg", "-": "g"}


def seg_polys(x, y, w, h, t, slant):
    """Segments of a digit in the box x, y (top left), w x h, thickness t, slant (a fraction of w per height)."""
    def sk(px, py):
        return (px + slant * (y + h - py), py)

    def hseg(yc):
        return [sk(x + t * 0.6, yc), sk(x + t, yc - t / 2), sk(x + w - t, yc - t / 2), sk(x + w - t * 0.6, yc),
                sk(x + w - t, yc + t / 2), sk(x + t, yc + t / 2)]

    def vseg(xc, ya, yb):
        return [sk(xc, ya + t * 0.6), sk(xc + t / 2, ya + t), sk(xc + t / 2, yb - t), sk(xc, yb - t * 0.6),
                sk(xc - t / 2, yb - t), sk(xc - t / 2, ya + t)]
    ym = y + h / 2
    return {"a": hseg(y + t / 2), "g": hseg(ym), "d": hseg(y + h - t / 2),
            "f": vseg(x + t / 2, y, ym), "b": vseg(x + w - t / 2, y, ym),
            "e": vseg(x + t / 2, ym, y + h), "c": vseg(x + w - t / 2, ym, y + h)}


LCD_W, LCD_H = 540, 204                         # display proportion 90 x 34 mm
LCD_VALUES = ["2.38", "2.41", "2.43", "2.42", "2.40", "2.39", "2.41", "2.44"]


def make_lcd(name, text, on, dot=False, level=0.0):
    """Display frame: 3 digits with a dot, a measurement dot on the left, a level bar at the bottom. on - backlight."""
    bg = (150, 168, 112) if on else (50, 58, 50)
    ghost = (138, 155, 104) if on else (53, 61, 52)
    ink = (26, 32, 24)
    img = Image.new("RGB", (LCD_W, LCD_H), bg)
    d = ImageDraw.Draw(img)
    # the backlight is uneven: darker toward the edges
    for i in range(14):
        k = 1.0 - 0.016 * (14 - i)
        c = tuple(int(v * k) for v in bg)
        d.rectangle((i * 3, i * 2, LCD_W - 1 - i * 3, LCD_H - 1 - i * 2), outline=c, width=3)
    dw, dh, t, gap = 104, 132, 16, 34
    x0, y0 = 118, 22
    digits = text.replace(".", "")
    pos = text.index(".") if "." in text else -1
    for i in range(3):
        x = x0 + i * (dw + gap)
        polys = seg_polys(x, y0, dw, dh, t, 0.10)
        ch = digits[i] if i < len(digits) else " "
        for sn, poly in polys.items():
            lit = on and sn in SEG.get(ch, "")
            d.polygon(poly, fill=ink if lit else ghost)
        if i == pos - 1:
            cx, cy = x + dw + gap / 2 - 2, y0 + dh - t / 2
            d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=ink if on else ghost)
    # measurement dot on the left (blinks by frame), the level bar
    d.ellipse((30, 40, 56, 66), fill=ink if (on and dot) else ghost)
    n = 18
    for k in range(n):
        x = 92 + k * 23
        lit = on and k < int(round(level * n))
        d.rectangle((x, 172, x + 17, 188), fill=ink if lit else ghost)
    img = img.filter(ImageFilter.GaussianBlur(0.7))
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, img.size)


def make_lcds():
    make_lcd("decal_lcd_off.png", "8.88", False)
    for i, v in enumerate(LCD_VALUES):
        make_lcd("decal_lcd_f%02d.png" % i, v, True, dot=i % 2 == 0, level=float(v) / 4.0 + 0.02 * (i % 3))


def wh(box):
    a0, a1, b0, b1 = box
    return a1 - a0, b1 - b0


if __name__ == "__main__":
    # apron face: small ones, the densest - it is seen first
    face("decal_apron_f.png", *wh(L.APRON_F),
         ["caution", "sun", "pressure", "hazard", "fragile", "star", "nooil", "chevrons", "warning", "spiral",
          "keepdry", "checker", "target", "legalize", "peace"],
         seed=30, max_ov=0.45, scale=(0.55, 0.75), margin=0.003)
    face("decal_apron_r.png", *wh(L.APRON_R), ["sideup", "hazard", "danger", "sun", "warning", "star"],
         seed=31, max_ov=0.35, scale=(0.5, 0.7), margin=0.003)
    # top of the unit: clear of the valves (their handwheels are dia. 0.05)
    u0, v0 = L.BLK_TOP[0], L.BLK_TOP[2]
    ko = [(x - 0.035 - u0, x + 0.035 - u0, L.VALVES[1] - 0.035 - v0, L.VALVES[1] + 0.035 - v0) for x in L.VALVES[0]]
    face("decal_blk_top.png", *wh(L.BLK_TOP), ["voltage", "caution", "target", "chevrons", "nosmoke"],
         seed=33, max_ov=0.4, scale=(0.6, 0.8), keep_out=ko, margin=0.004)
    face("decal_blk_side.png", *wh(L.BLK_SIDE), ["pressure", "sun", "fragile", "spiral", "hazard", "leaf"],
         seed=35, max_ov=0.4, scale=(0.6, 0.8), margin=0.004)
    face("decal_comp.png", *wh(L.COMP_FRONT), ["nooil", "pressure", "star"], seed=37, max_ov=0.2,
         scale=(0.6, 0.7), margin=0.004)
    make_gauge()
    make_lcds()
