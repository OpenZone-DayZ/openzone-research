"""Decals, screen and keyboard of the homemade Freedom chronograph M28 (system Python + Pillow).
Freedom decals overlap, some carry short English words of the kind seen on equipment and in workshops
(CAUTION, FRAGILE, HIGH VOLTAGE, THIS SIDE UP, KEEP DRY, WARNING, DANGER; words are allowed on Freedom
decals only), the rest are pictograms and patterns. No names, brands, logos or jokes. The decals are
scuffed, faded, some have a peeled corner. The decal drawers are from the M27 make_decals.py, only the
faces and the screen are different.

    python make_decals.py      -> ../work/decal_*.png

Faces (the layout is in layout.py):
- decal_case_front.png, decal_case_top.png, decal_case_side.png - the green case: the face, the top
  around the laptop and the unit, the right side - the densest;
- decal_lid.png      - the back of the laptop lid;
- decal_rail.png     - the rail face: small decals between the turns of tape;
- decal_keys.png     - the laptop keyboard: keys without letters (the same places as the raised keys
  of the near LOD, layout.key_rects), a red trackpoint;
- decal_panel_off.png, decal_panel_fNN.png - the own texture of the laptop screen and the unit display
  (section screen, 512 x 512: the 4:3 screen on top, the 4:1 display below). "Off" - a dark matrix and
  an empty display; the "working" frames (the mod script cycles them, OZL_WorkFx frames) - a series of
  10 shots: on the screen a DOS-style chronograph program (a blue field, the speed of the last shot
  large, a series table, bars, a totals line, a blinking cursor - digits only), on the display the
  same speed in seven-segment digits. Frame 0 is the whole series (the "working" preview shows it),
  1-9 are the shots of a new series one by one.
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


def sticker(kind, rnd, scale=1.0, tilt=14.0):
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
    return out.rotate(rnd.uniform(-tilt, tilt), resample=Image.BICUBIC, expand=True)


def overlap(a, b):
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    ix = max(0.0, min(ax1, bx1) - max(ax0, bx0))
    iy = max(0.0, min(ay1, by1) - max(ay0, by0))
    return ix * iy / min((ax1 - ax0) * (ay1 - ay0), (bx1 - bx0) * (by1 - by0))


def face(name, wm, hm, kinds, seed, max_ov=0.45, scale=(0.85, 1.15), keep_out=(), margin=0.01, tilt=14.0):
    """A wm x hm meter face (v is up), decals kinds at random places, overlapping by at most max_ov of the
    area of the smaller of the two; keep_out - [(u0, u1, v0, v1)] meters where there are no decals."""
    W, H = int(wm * K), int(hm * K)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rnd = random.Random(seed)
    boxes = []
    for kind in kinds:
        st = sticker(kind, rnd, rnd.uniform(*scale), tilt)
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


SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
       "7": "abc", "8": "abcdefg", "9": "abcdfg"}


def seven(d, x, y, w, h, ch, fill):
    """Seven-segment digit: top left (x, y), w x h."""
    t = w * 0.18
    segs = {"a": (x + t, y, x + w - t, y + t), "g": (x + t, y + h / 2 - t / 2, x + w - t, y + h / 2 + t / 2),
            "d": (x + t, y + h - t, x + w - t, y + h), "f": (x, y + t, x + t, y + h / 2 - t / 2),
            "b": (x + w - t, y + t, x + w, y + h / 2 - t / 2), "e": (x, y + h / 2 + t / 2, x + t, y + h - t),
            "c": (x + w - t, y + h / 2 + t / 2, x + w, y + h - t)}
    for s in SEG.get(ch, ""):
        d.rectangle(segs[s], fill=fill)


# a series of 10 shots, m/s x 10 (the last digit is tenths); "working" frame k shows the series up to and
# including shot k, frame 0 - the whole series
SHOTS = [28513, 28382, 28467, 28291, 28614, 28405, 28356, 28498, 28521, 28436]
FRAMES = 10


def screen_off(W, H):
    """A switched-off matrix: dark gray glass, a highlight on top."""
    off = Image.new("RGB", (W, H), (26, 30, 29))
    d = ImageDraw.Draw(off)
    for i in range(H):
        k = max(0.0, 1.0 - i / (H * 0.7))
        d.line([(0, i), (W, i)], fill=(int(26 + 14 * k), int(30 + 15 * k), int(29 + 14 * k)))
    return off


def screen_frame(W, H, n, cursor):
    """A DOS-style chronograph program for the first n shots of the series: a blue field, double frames,
    large - the speed of the last shot and its number, a table (number, speed; empty rows are dashes),
    scatter bars, a totals line (mean, spread, min, max, range) and a cursor - digits only."""
    BG, FG, HI, CY_, GR = (0, 0, 168), (232, 232, 232), (252, 252, 84), (84, 252, 252), (170, 170, 170)
    on = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(on)
    lw = max(2, int(W * 0.004))
    cw = W / 40.0                                               # character cell: 40 columns

    def frame(x0, y0, x1, y1):
        d.rectangle((x0, y0, x1, y1), outline=GR, width=lw)
        d.rectangle((x0 + lw * 2, y0 + lw * 2, x1 - lw * 2, y1 - lw * 2), outline=GR, width=lw)

    mono, monob = "cour.ttf", "courbd.ttf"
    vals = SHOTS[:n]
    last = vals[-1]
    frame(cw * 0.5, H * 0.03, W - cw * 0.5, H * 0.30)
    text_fit(d, (cw * 2, H * 0.06, W * 0.62, H * 0.27), "%d.%d" % (last // 10, last % 10), monob, HI)
    text_fit(d, (W * 0.66, H * 0.10, W - cw * 2, H * 0.23), "# %2d" % n, monob, FG)
    frame(cw * 0.5, H * 0.33, W * 0.48, H * 0.88)
    rh = (H * 0.53) / 10.4
    for i in range(10):
        y = H * 0.355 + i * rh
        text_fit(d, (cw * 2, y, cw * 5, y + rh * 0.86), "%2d" % (i + 1), mono, GR)
        s = "%d" % (vals[i] // 10) if i < n else "----"
        text_fit(d, (cw * 7, y, cw * 14, y + rh * 0.86), s, mono, HI if i == n - 1 else (FG if i < n else GR))
    frame(W * 0.50, H * 0.33, W - cw * 0.5, H * 0.88)
    bx0, bx1, by0, by1 = W * 0.54, W - cw * 1.8, H * 0.37, H * 0.83
    d.line([(bx0, by1), (bx1, by1)], fill=GR, width=lw)
    d.line([(bx0, by0), (bx0, by1)], fill=GR, width=lw)
    for j in range(1, 5):
        yy = by1 - (by1 - by0) * j / 5
        d.line([(bx0 - cw * 0.4, yy), (bx0, yy)], fill=GR, width=lw)
    bw = (bx1 - bx0) / 10
    for i, v in enumerate(vals):
        f = (v / 10.0 - 2800) / 70.0
        d.rectangle((bx0 + bw * i + bw * 0.18, by1 - (by1 - by0) * f, bx0 + bw * (i + 1) - bw * 0.18, by1 - lw),
                    fill=HI if i == n - 1 else CY_)
    d.rectangle((0, H * 0.91, W, H), fill=GR)
    ms = [v / 10.0 for v in vals]
    avg = sum(ms) / n
    sd = (sum((m - avg) ** 2 for m in ms) / max(1, n - 1)) ** 0.5
    for k, s in enumerate(("%d" % round(avg), "%.1f" % sd, "%d" % min(ms), "%d" % max(ms), "%d" % (max(ms) - min(ms)))):
        text_fit(d, (cw * (1 + 7.4 * k), H * 0.925, cw * (6.4 + 7.4 * k), H * 0.99), s, monob, BG)
    if cursor:
        d.rectangle((cw * 37.6, H * 0.93, cw * 38.8, H * 0.985), fill=BG)
    # raster of a 90s matrix: dark lines
    for yy in range(0, H, 3 * S):
        d.line([(0, yy), (W, yy)], fill=(0, 0, 120), width=1)
    return on


def lcd(W, H, value):
    """Unit display: "off" (value None) - empty gray-green glass, "working" - backlight and four
    seven-segment speed digits."""
    im = Image.new("RGB", (W, H), (96, 104, 88) if value is None else (178, 206, 70))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W - 1, H - 1), outline=(40, 42, 38), width=3 * S)
    if value is not None:
        cw, ch = W * 0.15, H * 0.66
        for i, c in enumerate("%4d" % value):
            seven(d, W * 0.12 + i * cw * 1.25, H * 0.17, cw, ch, c, (24, 28, 20))
    return im


def make_panel():
    """The own texture of the laptop screen and the unit display (layout.PANEL_*): the screen on top, the
    display below."""
    W = L.PANEL_PX * S
    hl = int(W * L.PANEL_SPLIT)
    hs = W - hl

    def compose(scr, lc):
        img = Image.new("RGB", (W, W))
        img.paste(scr, (0, 0))
        img.paste(lc, (0, hs))
        return img.convert("RGBA")
    save(compose(screen_off(W, hs), lcd(W, hl, None)), "decal_panel_off.png")
    for fr in range(FRAMES):
        n = FRAMES if fr == 0 else fr
        save(compose(screen_frame(W, hs, n, fr % 2 == 0), lcd(W, hl, SHOTS[n - 1] // 10)), "decal_panel_f%02d.png" % fr)


def make_keys():
    """Keyboard: six rows of keys without letters (layout.key_rects - the same places as the raised keys),
    a smaller row of F keys, a space bar; some keys are rubbed to a shine, between the rows a red
    trackpoint."""
    x0, x1, y0, y1 = L.KEYS
    W, H = int((x1 - x0) * K), int((y1 - y0) * K)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rnd = random.Random(7)
    gap = L.KEY_GAP * K
    for kx0, kx1, ky0, ky1 in L.key_rects():
        x, w = (kx0 - x0) * K, (kx1 - kx0) * K
        y, h = (y1 - ky1) * K, (ky1 - ky0) * K
        tone = rnd.choice((52, 54, 56)) + (12 if rnd.random() < 0.2 else 0)
        d.rounded_rectangle((x, y, x + w, y + h), radius=int(gap), fill=(tone, tone, tone + 2, 255))
        d.line([(x + gap, y + h * 0.15), (x + w - gap, y + h * 0.15)], fill=(tone + 14, tone + 14, tone + 16, 255),
               width=S)
    r = 0.0035 * K
    cx, cy = W * L.TRACK[0], H * L.TRACK[1]
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(176, 30, 26, 255))
    save(img, "decal_keys.png")


def wh(box):
    a0, a1, b0, b1 = box
    return a1 - a0, b1 - b0


if __name__ == "__main__":
    # case face: below the lid seam, past the latches and the valve (the case is pelican() from M27)
    u0 = L.CASE_FRONT[0]
    lat = L.CASE[0] / 2 - 0.13 * L.CASE[0] / 0.5
    ko = [(L.CASE_C[0] + s * lat - u0 - 0.026, L.CASE_C[0] + s * lat - u0 + 0.026, 0.07, 0.12) for s in (-1, 1)]
    vx = L.CASE_C[0] + L.CASE[0] / 2 - 0.05 - u0
    ko.append((vx - 0.018, vx + 0.018, 0.045, 0.085))
    face("decal_case_front.png", *wh(L.CASE_FRONT),
         ["caution", "sun", "fragile", "hazard", "sideup", "star", "warning", "chevrons", "keepdry", "spiral",
          "danger", "checker", "peace"],
         seed=28, max_ov=0.5, scale=(0.7, 0.95), keep_out=ko, margin=0.004)
    # case top: around the laptop and the interface unit
    u0, v0 = L.CASE_TOP[0], L.CASE_TOP[2]
    ko = [(L.LX0 - u0 - 0.005, L.LX1 - u0 + 0.005, L.LY0 - v0 - 0.005, L.LY1 - v0 + 0.06),
          (L.BOX[0] - u0 - 0.005, L.BOX[1] - u0 + 0.005, L.BOX[2] - v0 - 0.005, L.BOX[3] - v0 + 0.005)]
    face("decal_case_top.png", *wh(L.CASE_TOP),
         ["voltage", "hazard", "sun", "caution", "nosmoke", "star", "fragile", "chevrons", "target", "keepdry",
          "spiral", "warning"],
         seed=29, max_ov=0.45, scale=(0.7, 0.95), keep_out=ko, margin=0.004)
    face("decal_case_side.png", *wh(L.CASE_SIDE),
         ["sideup", "warning", "sun", "hazard", "star", "flammable"], seed=31, max_ov=0.35, scale=(0.7, 0.9),
         margin=0.004)
    # back of the laptop lid (in z - with the lid tilt)
    face("decal_lid.png", L.LT_W - 0.02, (L.LT_D - 0.02) * math.cos(math.radians(L.LID_DEG)),
         ["target", "caution", "sun", "chevrons", "danger", "star", "keepdry", "spiral", "legalize", "peace"],
         seed=37, max_ov=0.4, scale=(0.7, 0.9), margin=0.004)
    # rail face: small ones, almost straight, clear of the tape
    u0 = L.RAIL_FRONT[0]
    ko = [(x - L.TAPE_W / 2 - u0 - 0.004, x + L.TAPE_W / 2 - u0 + 0.004, 0.0, 0.04) for x in L.TAPE_X]
    face("decal_rail.png", *wh(L.RAIL_FRONT),
         ["hazard", "caution", "chevrons", "warning", "hazard", "voltage", "checker"],
         seed=41, max_ov=0.1, scale=(0.42, 0.5), keep_out=ko, margin=0.001, tilt=3.0)
    make_keys()
    make_panel()