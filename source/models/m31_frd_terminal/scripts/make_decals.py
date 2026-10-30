"""Decals, screen and keyboard of the M31 Freedom computer (system Python + Pillow).
Freedom is the only faction whose decals carry words: overlapping stickers, some with short
English words found on equipment and in a workshop (CAUTION, FRAGILE, HIGH VOLTAGE, THIS
SIDE UP, KEEP DRY, WARNING, DANGER), the rest pictograms and patterns. No names, brands,
logos or jokes. The stickers are worn and faded, some have a peeled corner. The sticker
drawers come from M27 (make_decals.py of m27_frd_pack_ball, through M28); only the faces
and the screen are specific here.

    python make_decals.py      -> ../work/decal_*.png

Faces (positions are in layout.py):
- decal_case0_front.png, decal_case1_front.png - fronts of the case pedestals (at the base,
  clear of the latches);
- decal_case0_side.png, decal_case1_side.png - outer sides of the cases - the densest;
- decal_tower_side.png, decal_tower_front.png - right side of the tower and the lower part
  of its front;
- decal_mon_top.png  - top of the monitor bezel;
- decal_radio.png    - left side of the radio;
- decal_keys.png     - keyboard: beige keys without letters, grey service keys (the same as
  in the model);
- decal_screen_off.png, decal_screen_fNN.png - the CRT screen (its own texture): off (dark
  grey glass) and 12 "working" frames - green phosphor: a research tree of blocks with links
  (the next block fills in, the cursor blinks), a receiving log of stroke lines (they crawl
  up), a load bar - no word and no digit that could be read as lettering.
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
import kstickers  # noqa: E402  (peace sign, LEGALIZE and the sheet)

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 2                                   # supersampling, then downscaled - smooth edges
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
    """Lightning bolt (a "high voltage" pictogram)."""
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


# --- Stickers: each function draws on a w x h pixel image -------------------------------------
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
    """Wear patches: 255 - intact, 0 - worn off."""
    m = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(m)
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.uniform(rmin, rmax)
        d.ellipse((x - r, y - r * rnd.uniform(0.3, 1.0), x + r, y + r * rnd.uniform(0.3, 1.0)), fill=0)
    return m.filter(ImageFilter.GaussianBlur(1.2 * S))


def sticker(kind, rnd, scale=1.0, tilt=14.0):
    """RGBA sticker: faded, scratched, worn edges, sometimes a peeled corner."""
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
    # scratches: thin light strokes where the sticker is worn off
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
    # peeled corner: the corner is cut off and replaced by the back side (paper) folded over
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
    """Face of wm x hm meters (v is up), stickers `kinds` in random places, overlapping by at most
    max_ov of the smaller area; keep_out - [(u0, u1, v0, v1)] meters with no stickers.
    """
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



FRAMES = 12                             # working frames: 12 x 0.25 s - 3 s loop (OZL_WorkFx)


def crt(on, W, H, BG):
    """Phosphor glow, raster, darkening toward the tube edges."""
    glow = on.filter(ImageFilter.GaussianBlur(3 * S))
    on = ImageChops.add(on, glow.point(lambda v: v // 2))
    d = ImageDraw.Draw(on)
    for yy in range(0, H, 3 * S):
        d.line([(0, yy), (W, yy)], fill=(0, 0, 0), width=1)
    vign = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vign).rounded_rectangle((W * 0.02, H * 0.03, W * 0.98, H * 0.97), radius=int(W * 0.08), fill=255)
    vign = vign.filter(ImageFilter.GaussianBlur(W * 0.04))
    return Image.composite(on, Image.new("RGB", (W, H), BG), vign)


def screen_frame(W, H, fr):
    """Working frame: green phosphor on black. On the left a research tree of blocks with links
    (finished ones are filled, the next block fills in over the frames, the cursor frame
    blinks, the link to it runs as a dashed line), on the right the media receiving log -
    stroke lines crawl up, the bottom one is being typed, the load bar grows, the media icon
    blinks; at the bottom a status line and a blinking cursor. No words or digits.
    """
    BG, FG, HI, DIM = (4, 14, 6), (70, 236, 96), (190, 255, 190), (30, 120, 46)
    on = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(on)
    lw = max(2, int(W * 0.004))
    cw, rh = W / 64.0, H / 30.0                                  # 64 x 30 cells
    log = random.Random(31)
    lines = [[log.randint(2, 7) for _ in range(8)] for _ in range(FRAMES + 12)]
    tails = [log.randint(0, 8) for _ in range(FRAMES + 12)]

    def dashes(x0, x1, y, col, words, upto=None):
        """A line of "text" made of strokes - words of `words` cells in length; upto - how many
        cells are visible.
        """
        x, used = x0, 0
        for n in words:
            if upto is not None and used >= upto:
                break
            n_ = n if upto is None else min(n, upto - used)
            w = min(n_ * cw, x1 - x)
            if w > cw * 0.6:
                d.rectangle((x, y + rh * 0.25, x + w - cw * 0.3, y + rh * 0.75), fill=col)
            x += n * cw + cw
            used += n + 1
            if x >= x1:
                break
    # menu line: an inverted bar, the current item blinks
    d.rectangle((0, 0, W, rh * 1.2), fill=DIM)
    for k in range(5):
        d.rectangle((cw * (2 + 11 * k), rh * 0.3, cw * (8 + 11 * k), rh * 0.9), fill=HI if k == 2 and fr % 4 < 2 else BG)
    # left window: the tree - a root, three branches, leaves
    d.rectangle((cw, rh * 2, W * 0.58, H - rh * 2.5), outline=FG, width=lw)
    d.rectangle((cw + lw * 2, rh * 2 + lw * 2, W * 0.58 - lw * 2, H - rh * 2.5 - lw * 2), outline=DIM, width=lw)
    bw, bh = cw * 6, rh * 1.6
    root = (W * 0.30, rh * 4.0)
    lv1 = [(W * 0.10, rh * 9.5), (W * 0.30, rh * 9.5), (W * 0.50, rh * 9.5)]
    lv2 = [(W * 0.07, rh * 15.5), (W * 0.17, rh * 15.5), (W * 0.30, rh * 15.5), (W * 0.43, rh * 15.5),
           (W * 0.53, rh * 15.5)]
    lv3 = [(W * 0.12, rh * 21.5), (W * 0.30, rh * 21.5), (W * 0.48, rh * 21.5)]
    edges = [(root, p) for p in lv1] + [(lv1[0], lv2[0]), (lv1[0], lv2[1]), (lv1[1], lv2[2]), (lv1[2], lv2[3]),
                                        (lv1[2], lv2[4]), (lv2[1], lv3[0]), (lv2[2], lv3[1]), (lv2[3], lv3[2])]
    done = {root, lv1[0], lv1[1], lv1[2], lv2[1], lv2[2], lv3[0]}
    cur = lv2[3]
    for a, b in edges:
        ym = (a[1] + b[1]) / 2
        path = [(a[0], a[1] + bh / 2), (a[0], ym), (b[0], ym), (b[0], b[1] - bh / 2)]
        if b is cur:
            # link to the next block - a running dashed line
            d.line(path, fill=DIM, width=lw)
            st = cw * 1.2
            for (xa, ya), (xb, yb) in zip(path, path[1:]):
                ln = abs(xb - xa) + abs(yb - ya)
                t = (fr % 4) * st / 4
                while ln > 0 and t < ln:
                    f0, f1 = t / ln, min(1.0, (t + st * 0.5) / ln)
                    d.line([(xa + (xb - xa) * f0, ya + (yb - ya) * f0), (xa + (xb - xa) * f1, ya + (yb - ya) * f1)],
                           fill=HI, width=lw)
                    t += st
            continue
        d.line(path, fill=FG if b in done else DIM, width=lw)
    for p in [root] + lv1 + lv2 + lv3:
        box = (p[0] - bw / 2, p[1] - bh / 2, p[0] + bw / 2, p[1] + bh / 2)
        if p in done:
            d.rectangle(box, fill=FG)
            d.rectangle((box[0] + cw, p[1] - rh * 0.2, box[2] - cw, p[1] + rh * 0.2), fill=BG)
        elif p is cur:
            d.rectangle(box, outline=FG, width=lw)
            part = (fr + 1) / FRAMES
            d.rectangle((box[0] + lw * 2, box[1] + lw * 2, box[0] + lw * 2 + (bw - lw * 4) * part, box[3] - lw * 2),
                        fill=FG)
        else:
            d.rectangle(box, outline=FG, width=lw)
    if fr % 2 == 0:                                              # cursor frame on next block blinks
        d.rectangle((cur[0] - bw / 2 - lw * 3, cur[1] - bh / 2 - lw * 3, cur[0] + bw / 2 + lw * 3,
                     cur[1] + bh / 2 + lw * 3), outline=HI, width=lw)
    # right window: the log - lines crawl up, the bottom one is typed; the load bar
    x0, x1 = W * 0.61, W - cw
    d.rectangle((x0, rh * 2, x1, H - rh * 2.5), outline=FG, width=lw)
    d.rectangle((x0, rh * 2, x1, rh * 3.4), fill=FG)
    for i in range(10):
        k = fr + i
        dashes(x0 + cw * 1.5, x1 - cw * (1.5 + tails[k]), rh * (4.2 + i * 1.25), HI if k % 5 == 0 else FG, lines[k],
               upto=(4 + 3 * (fr % 4)) if i == 9 else None)
    d.rectangle((x0 + cw * 1.5, rh * 17.8, x1 - cw * 1.5, rh * 19.2), outline=FG, width=lw)
    p = 0.08 + 0.88 * fr / (FRAMES - 1)
    d.rectangle((x0 + cw * 1.5 + lw * 2, rh * 17.8 + lw * 2, x0 + cw * 1.5 + lw * 2 + (x1 - x0 - cw * 3 - lw * 4) * p,
                 rh * 19.2 - lw * 2), fill=FG)
    # media icon: a rectangle and an inward arrow, blinking
    if fr % 2 == 1:
        d.rectangle((x0 + cw * 1.5, rh * 20.4, x0 + cw * 6.5, rh * 23.0), outline=HI, width=lw)
        d.polygon([(x0 + cw * 8, rh * 21.7), (x0 + cw * 10, rh * 20.9), (x0 + cw * 10, rh * 22.5)], fill=HI)
    for i in range(2):
        dashes(x0 + cw * 12, x1 - cw * 3, rh * (20.6 + i * 1.25), DIM, (2, 5, 3))
    # status line and cursor
    dashes(cw * 2, W * 0.5, H - rh * 1.7, DIM, (3, 6, 4, 2, 5))
    if fr % 2 == 0:
        d.rectangle((W * 0.52, H - rh * 1.6, W * 0.52 + cw, H - rh * 0.9), fill=HI)
    return crt(on, W, H, BG)


def make_screen():
    """CRT screen 285 x 215 mm. "Off" - dark grey glass with a glare at the top left; "working" -
    FRAMES frames (screen_frame).
    """
    W, H = int(L.SCR_W * K), int(L.SCR_H * K)
    off = Image.new("RGB", (W, H), (34, 38, 36))
    d = ImageDraw.Draw(off)
    for i in range(H):
        k = max(0.0, 1.0 - i / (H * 0.8))
        d.line([(0, i), (W, i)], fill=(int(34 + 12 * k), int(38 + 13 * k), int(36 + 12 * k)))
    d.ellipse((W * 0.05, H * 0.04, W * 0.42, H * 0.30), fill=(58, 64, 62))
    off = off.filter(ImageFilter.GaussianBlur(10 * S))
    save(off.convert("RGBA"), "decal_screen_off.png")
    for fr in range(FRAMES):
        save(screen_frame(W, H, fr).convert("RGBA"), "decal_screen_f%02d.png" % fr)


def make_keys():
    """Model M class keyboard - the same keys as in the model (layout.key_rects): beige letter
    keys, grey service keys, no letters; some keys are worn and darker. The near LOD has
    separate keys on top (with gaps between them), the middle LOD uses only this picture as the
    keyboard.
    """
    x0, x1, y0, y1 = L.KEYS
    W, H = int((x1 - x0) * K), int((y1 - y0) * K)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rnd = random.Random(13)
    BEIGE, GREY = (214, 206, 184), (150, 148, 140)
    for kx0, kx1, ky0, ky1, grey in L.key_rects():
        tone = GREY if grey else BEIGE
        k = rnd.uniform(0.86, 0.97) if rnd.random() < 0.3 else 1.0
        c = tuple(int(v * k) for v in tone) + (255,)
        a, b, a1, b1 = (kx0 - x0) * K, (y1 - ky1) * K, (kx1 - x0) * K, (y1 - ky0) * K
        d.rounded_rectangle((a, b, a1, b1), radius=int(0.0015 * K), fill=c)
        d.line([(a + S * 2, b1 - S * 2), (a1 - S * 2, b1 - S * 2)], fill=tuple(int(v * 0.75) for v in tone) + (255,),
               width=S)
    save(img, "decal_keys.png")


def wh(box):
    a0, a1, b0, b1 = box
    return a1 - a0, b1 - b0


if __name__ == "__main__":
    # case fronts: at the base (between the side and the seam), clear of the latches and the handle
    for i in (0, 1):
        x0, x1, z0, z1 = L.CASE_FRONT[i]
        sx = L.seam_x(i)
        ko = [(sx - x0 - 0.05, sx - x0 + 0.05, z - z0 - 0.05, z - z0 + 0.05) for z in L.LATCH_Z]
        ko.append((sx - x0 - 0.045, sx - x0 + 0.045, L.HANDLE_Z - z0 - 0.09, L.HANDLE_Z - z0 + 0.09))
        face("decal_case%d_front.png" % i, x1 - x0, z1 - z0,
             [["caution", "sun", "fragile", "hazard", "sideup", "star", "warning", "checker", "keepdry"],
              ["voltage", "chevrons", "danger", "spiral", "caution", "nosmoke", "target", "fragile", "star", "peace"]][i],
             seed=310 + i, max_ov=0.5, scale=(0.75, 1.0), keep_out=ko, margin=0.004)
    face("decal_case0_side.png", *wh(L.CASE_SIDE),
         ["warning", "sun", "hazard", "fragile", "star", "keepdry", "caution", "spiral", "flammable", "chevrons",
          "sideup", "target", "danger"], seed=313, max_ov=0.45, scale=(0.8, 1.1), margin=0.004)
    face("decal_case1_side.png", *wh(L.CASE_SIDE),
         ["sideup", "voltage", "checker", "caution", "sun", "nosmoke", "warning", "star", "hazard", "spiral",
          "keepdry", "danger", "legalize"], seed=314, max_ov=0.45, scale=(0.8, 1.1), margin=0.004)
    face("decal_tower_side.png", *wh(L.TOWER_SIDE),
         ["voltage", "sun", "caution", "chevrons", "star", "warning", "spiral", "target", "keepdry", "hazard", "leaf",
          "peace"],
         seed=315, max_ov=0.45, scale=(0.75, 1.0), margin=0.004)
    tf = L.TOWER_FRONT
    face("decal_tower_front.png", *wh(tf), ["hazard", "star", "caution", "checker"],
         seed=316, max_ov=0.3, scale=(0.5, 0.65), margin=0.003, tilt=8.0,
         keep_out=[(L.T_POWER[0] - tf[0] - 0.03, L.T_POWER[0] - tf[0] + 0.03, L.T_POWER[1] - tf[2] - 0.03, 1.0),
                   (0.0, L.T_LEDS[1][0] - tf[0] + 0.02, L.T_LEDS[0][1] - tf[2] - 0.02, 1.0)])
    face("decal_mon_top.png", *wh(L.MON_TOP), ["sun", "warning", "spiral", "danger"], seed=317, max_ov=0.4,
         scale=(0.6, 0.8), margin=0.004)
    face("decal_radio.png", *wh(L.RADIO_SIDE), ["target", "caution", "star", "hazard", "keepdry", "chevrons"],
         seed=318, max_ov=0.4, scale=(0.6, 0.8), margin=0.004)
    make_keys()
    make_screen()
