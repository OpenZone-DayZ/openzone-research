"""Decals of the plate clamp M86 (system Python + Pillow), digits and signs only - no letters or brand
marks. Both variants write here too, into ../work (build_m86b.py takes them from here).

Variant A (screw press):
- cast digits "0,5" (the press force in tonnes) on the side of the C-frame post: on the raised
  digits the blue enamel is worn down to cast iron, with a relief shadow and highlight along the edge;
- black marker on Kevlar: a dashed circle for the next sample and the layer count "12".
Variant B (square and clamps):
- chalk on a piece of armour plate: a 50 x 50 square for a sample, a marking cross and the number "4";
- a bullet-hit mark: a lead "pancake" with ragged rays and a dark crater in the middle;
- cast digits "100" (the clamp opening, mm) along the fixed bracket - the enamel is worn off the relief;
- a stamp "17" on the end of the square base: punched digits, the pit edges lighter than the scale.

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges


def font(names, px):
    for name in names:
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def blotches(size, seed, n, rmin, rmax, fill_lo, fill_hi, blur):
    """Mask of patches (0..255): wear, uneven pressure of chalk and marker."""
    rnd = random.Random(seed)
    w, h = size
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.uniform(rmin, rmax) * w
        d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=rnd.randint(fill_lo, fill_hi))
    return m.filter(ImageFilter.GaussianBlur(blur))


def centered(d, box, text, fnt, **kw):
    l, t, r, b = d.textbbox((0, 0), text, font=fnt)
    x0, y0, x1, y1 = box
    d.text(((x0 + x1 - (r - l)) / 2 - l, (y0 + y1 - (b - t)) / 2 - t), text, font=fnt, **kw)


def cast_relief(text, W, H, seed, metal, shade, light, rotate=False):
    """Cast digits: relief along the edge - a shadow at the lower right and a highlight at the upper left;
    on the relief tops the enamel is worn down to metal in patches (the picture lies over the enamel,
    transparent outside the digits).
    """
    w0, h0 = (H, W) if rotate else (W, H)
    fnt = font(["arialbd.ttf", "bahnschrift.ttf"], int(h0 * 0.9))
    mask = Image.new("L", (w0, h0), 0)
    centered(ImageDraw.Draw(mask), (0, 0, w0, h0), text, fnt, fill=255)
    if rotate:
        mask = mask.rotate(90, expand=True)
    mask = mask.filter(ImageFilter.GaussianBlur(min(W, H) * 0.008))
    off = max(1, int(min(W, H) * 0.03))
    shadow = ImageChops.subtract(ImageChops.offset(mask, off, off), mask)
    hl = ImageChops.subtract(ImageChops.offset(mask, -off, -off), mask)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wear = blotches((W, H), seed, 40, 0.03, 0.10, 120, 255, min(W, H) * 0.04)
    img = Image.composite(Image.new("RGBA", (W, H), metal), img, ImageChops.multiply(mask, wear))
    img = Image.composite(Image.new("RGBA", (W, H), shade), img, shadow.point(lambda v: int(v * 0.75)))
    img = Image.composite(Image.new("RGBA", (W, H), light), img, hl.point(lambda v: int(v * 0.45)))
    return img


def make_cast_a(name, w_mm, h_mm, px_mm=12):
    """"0,5" on the blue enamel of the post: the metal is grey cast iron."""
    W, H = w_mm * px_mm * S, h_mm * px_mm * S
    img = cast_relief("0,5", W, H, 5, (112, 110, 104, 255), (16, 22, 36, 255), (120, 150, 196, 255))
    save(img, (W // S, H // S), name)


def make_cast_b(name, w_mm, h_mm, px_mm=14):
    """"100" along the clamp bracket (the picture is portrait, the digits are rotated): red enamel, dark
    malleable iron under it.
    """
    W, H = w_mm * px_mm * S, h_mm * px_mm * S
    img = cast_relief("100", W, H, 100, (84, 82, 80, 255), (40, 8, 6, 255), (214, 110, 96, 255), rotate=True)
    save(img, (W // S, H // S), name)


def rough_stroke(d, pts, width, fill):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d.line([(x0, y0), (x1, y1)], fill=fill, width=width)
        d.ellipse([x1 - width / 2, y1 - width / 2, x1 + width / 2, y1 + width / 2], fill=fill)


def make_marker(name, w_mm, h_mm, px_mm=14):
    """Black marker on Kevlar: a dashed circle of D 30 for the next sample on the left and "12" on the
    right. The fabric absorbs marker unevenly - the stroke breaks along the weave (a net of thin gaps).
    """
    W, H = w_mm * px_mm * S, h_mm * px_mm * S
    k = px_mm * S
    rnd = random.Random(12)
    a = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(a)
    cx, cy, r = 17 * k, 17 * k, 15 * k
    n = 22
    for i in range(n):
        if i % 2:
            continue
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1.1) / n
        pts = [(cx + (r + rnd.uniform(-0.3, 0.3) * k) * math.cos(a0 + (a1 - a0) * s / 4),
                cy + (r + rnd.uniform(-0.3, 0.3) * k) * math.sin(a0 + (a1 - a0) * s / 4)) for s in range(5)]
        rough_stroke(d, pts, int(1.3 * k), 250)
    # centre cross
    d.line([(cx - 2.5 * k, cy), (cx + 2.5 * k, cy)], fill=230, width=int(1.0 * k))
    d.line([(cx, cy - 2.5 * k), (cx, cy + 2.5 * k)], fill=230, width=int(1.0 * k))
    fnt = font(["segoeprb.ttf", "segoepr.ttf", "arialbd.ttf"], int(16 * k))
    d.text((36 * k, 5 * k), "12", font=fnt, fill=255, stroke_width=int(0.4 * k), stroke_fill=255)
    d.line([(36 * k, 27 * k), (57 * k, 26 * k)], fill=240, width=int(1.3 * k))
    weave = Image.new("L", (W, H), 255)
    wd = ImageDraw.Draw(weave)
    step = int(3 * k)
    for x in range(0, W, step):
        wd.line([(x, 0), (x, H)], fill=190, width=max(1, int(0.25 * k)))
    for y in range(0, H, step):
        wd.line([(0, y), (W, y)], fill=190, width=max(1, int(0.25 * k)))
    press = ImageChops.add(blotches((W, H), 3, 30, 0.04, 0.12, 120, 255, H * 0.05), Image.new("L", (W, H), 170))
    a = ImageChops.multiply(ImageChops.multiply(a, weave), press)
    img = Image.new("RGBA", (W, H), (18, 18, 22, 255))
    img.putalpha(a)
    save(img, (W // S, H // S), name)


def make_chalk(name, w_mm, h_mm, px_mm=10):
    """Chalk on painted steel: a 50 x 50 square for a sample (with overlapping corners), a diagonal cross
    marking the centre and the number "4" on the right; chalk lays down ragged - grain and pressure in
    patches.
    """
    W, H = w_mm * px_mm * S, h_mm * px_mm * S
    k = px_mm * S
    rnd = random.Random(4)
    a = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(a)

    def j(x, y):
        return (x * k + rnd.uniform(-0.4, 0.4) * k, y * k + rnd.uniform(-0.4, 0.4) * k)
    x0, y0, x1, y1 = 5, 5, 55, 55
    lw = int(1.1 * k)
    rough_stroke(d, [j(x0 - 2, y0), j(30, y0 + 0.3), j(x1 + 3, y0 - 0.2)], lw, 230)
    rough_stroke(d, [j(x1, y0 - 2), j(x1 - 0.3, 30), j(x1 + 0.2, y1 + 2)], lw, 230)
    rough_stroke(d, [j(x1 + 2, y1), j(30, y1 - 0.4), j(x0 - 3, y1 + 0.2)], lw, 230)
    rough_stroke(d, [j(x0, y1 + 2), j(x0 + 0.4, 30), j(x0 - 0.2, y0 - 3)], lw, 230)
    rough_stroke(d, [j(26, 30), j(34, 30)], int(0.9 * k), 200)
    rough_stroke(d, [j(30, 26), j(30, 34)], int(0.9 * k), 200)
    fnt = font(["segoepr.ttf", "segoeprb.ttf", "arialbd.ttf"], int(30 * k))
    d.text((62 * k, 12 * k), "4", font=fnt, fill=235)
    d.ellipse([60 * k, 14 * k, 86 * k, 46 * k], outline=190, width=int(1.0 * k))
    grain = Image.effect_noise((W, H), 90).filter(ImageFilter.GaussianBlur(S * 0.6))
    grain = grain.point(lambda v: 255 if v > 132 else int(v * 0.7))
    press = ImageChops.add(blotches((W, H), 44, 30, 0.04, 0.14, 110, 255, H * 0.05), Image.new("L", (W, H), 70))
    a = ImageChops.multiply(ImageChops.multiply(a, grain), press)
    img = Image.new("RGBA", (W, H), (226, 224, 214, 255))
    img.putalpha(a)
    save(img, (W // S, H // S), name)


def make_hit(name, mm, px_mm=16):
    """Bullet mark on a steel plate: a lead "pancake" with ragged rays, a dark crater in the centre,
    around it a light ring of knocked-off paint.
    """
    W = H = mm * px_mm * S
    rnd = random.Random(9)
    c = W / 2
    ring = Image.new("L", (W, H), 0)
    ImageDraw.Draw(ring).ellipse([c - W * 0.46, c - H * 0.46, c + W * 0.46, c + H * 0.46], fill=255)
    ring = ring.filter(ImageFilter.GaussianBlur(W * 0.03))
    lead = Image.new("L", (W, H), 0)
    ld = ImageDraw.Draw(lead)
    pts = []
    a = 0.0
    while a < 2 * math.pi - 0.05:
        spike = rnd.random() < 0.35
        r = W * (0.17 + (rnd.uniform(0.10, 0.27) if spike else rnd.uniform(0.0, 0.07)))
        pts.append((c + r * math.cos(a), c + r * math.sin(a) * 0.92))
        a += rnd.uniform(0.10, 0.30)
    ld.polygon(pts, fill=255)
    lead = lead.filter(ImageFilter.GaussianBlur(W * 0.01))
    core = Image.new("L", (W, H), 0)
    ImageDraw.Draw(core).ellipse([c - W * 0.10, c - H * 0.10, c + W * 0.10, c + H * 0.10], fill=255)
    core = core.filter(ImageFilter.GaussianBlur(W * 0.03))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img = Image.composite(Image.new("RGBA", (W, H), (120, 122, 120, 255)), img, ring.point(lambda v: int(v * 0.85)))
    tone = Image.effect_noise((W, H), 40).point(lambda v: int(140 + (v - 128) * 0.4))
    lead_rgb = Image.merge("RGBA", (tone, tone, tone.point(lambda v: min(255, v + 6)), Image.new("L", (W, H), 255)))
    img = Image.composite(lead_rgb, img, lead)
    img = Image.composite(Image.new("RGBA", (W, H), (36, 36, 38, 255)), img, core)
    save(img, (W // S, H // S), name)


def make_stamp(name, w_mm, h_mm, px_mm=24):
    """Stamp "17" on the end of the base: the punched digits wobble (each has its own punch), the pit
    bottoms are dark, the rims light - the scale is knocked off.
    """
    W, H = w_mm * px_mm * S, h_mm * px_mm * S
    rnd = random.Random(17)
    fnt = font(["consolab.ttf", "lucon.ttf", "arialbd.ttf"], int(H * 0.82))
    dark = Image.new("L", (W, H), 0)
    edge = Image.new("L", (W, H), 0)
    dd, ed = ImageDraw.Draw(dark), ImageDraw.Draw(edge)
    step = W * 0.36
    for k, ch in enumerate("17"):
        x = W * 0.16 + k * step + rnd.uniform(-0.05, 0.05) * step
        y = rnd.uniform(-0.06, 0.06) * H
        l, t, r, b = dd.textbbox((0, 0), ch, font=fnt)
        pos = (x - l, (H - (b - t)) / 2 - t + y)
        ed.text(pos, ch, font=fnt, fill=255, stroke_width=int(H * 0.05), stroke_fill=255)
        dd.text(pos, ch, font=fnt, fill=255)
    rim = ImageChops.subtract(edge, dark)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img = Image.composite(Image.new("RGBA", (W, H), (150, 150, 148, 255)), img, rim.point(lambda v: int(v * 0.8)))
    img = Image.composite(Image.new("RGBA", (W, H), (16, 16, 18, 255)), img, dark.point(lambda v: int(v * 0.9)))
    save(img, (W // S, H // S), name)


def preview(names, name, bg_col):
    """Decals on a grey background, to look at."""
    ims = [Image.open(os.path.join(WORK, n)) for n in names]
    sc = 2
    ims = [im.resize((im.width * sc, im.height * sc), Image.NEAREST) for im in ims]
    W = max(im.width for im in ims) + 40
    H = sum(im.height for im in ims) + 20 * (len(ims) + 1)
    bg = Image.new("RGBA", (W, H), bg_col)
    y = 20
    for im in ims:
        bg.alpha_composite(im, (20, y))
        y += im.height + 20
    bg.save(os.path.join(WORK, name))
    print("wrote", os.path.join(WORK, name))


if __name__ == "__main__":
    make_cast_a("decal_a_cast.png", 22, 11)
    make_marker("decal_a_marker.png", 60, 34)
    make_chalk("decal_b_chalk.png", 90, 60)
    make_hit("decal_b_hit.png", 22)
    make_cast_b("decal_b_cast.png", 10, 26)
    make_stamp("decal_b_stamp.png", 14, 6)
    preview(["decal_a_cast.png", "decal_a_marker.png"], "decals_a_preview.png", (150, 128, 60, 255))
    preview(["decal_b_chalk.png", "decal_b_hit.png", "decal_b_cast.png", "decal_b_stamp.png"],
            "decals_b_preview.png", (70, 72, 70, 255))
