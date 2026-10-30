"""Decals of the barrel vise (system Python + Pillow), digits only - no letters or brand marks:
- cast digits "63" on the side of the body (the jaw width, like the cast "80" on Soviet vises):
  on the raised digits the enamel is worn down to cast iron, with a relief shadow along the lower edge;
- a pencil caliber mark "7,62" and a centre tick on the wooden insert;
- a serial stamp on the barrel breech: punched digits, the pit edges lighter than the bluing.

    python make_decals.py      -> ../work/decal_*.png
"""
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
    """Mask of patches (0..255): wear, uneven pencil pressure."""
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


def make_cast(name, w_mm, h_mm, px_mm=10):
    """Cast digits "63": relief along the digit edges - a shadow at the lower right and a highlight at the
    upper left; on the relief tops the enamel is worn down to grey cast iron in patches (the picture
    lies over the body enamel).
    """
    W, H = w_mm * px_mm * S, h_mm * px_mm * S
    fnt = font(["arialbd.ttf", "bahnschrift.ttf"], int(H * 0.92))
    mask = Image.new("L", (W, H), 0)
    centered(ImageDraw.Draw(mask), (0, 0, W, H), "63", fnt, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(H * 0.008))    # cast: the edges are rounded
    off = int(H * 0.022)
    shadow = ImageChops.subtract(ImageChops.offset(mask, off, off), mask)
    light = ImageChops.subtract(ImageChops.offset(mask, -off, -off), mask)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # digit tops: the enamel is worn in places (cast iron), intact in places (the same colour as the
    # body - transparent)
    wear = blotches((W, H), 63, 40, 0.03, 0.10, 120, 255, H * 0.04)
    iron = Image.new("RGBA", (W, H), (112, 110, 104, 255))
    img = Image.composite(iron, img, ImageChops.multiply(mask, wear))
    img = Image.composite(Image.new("RGBA", (W, H), (18, 26, 26, 255)), img, shadow.point(lambda v: int(v * 0.75)))
    img = Image.composite(Image.new("RGBA", (W, H), (150, 176, 172, 255)), img, light.point(lambda v: int(v * 0.45)))
    save(img, (W // S, H // S), name)


def make_pencil(name, w_mm, h_mm, px_mm=16):
    """Pencil on wood: "7,62" slanted, a centre tick of the insert beside it; the graphite lies unevenly -
    pressure in patches, a ragged stroke along the grain.
    """
    W, H = w_mm * px_mm * S, h_mm * px_mm * S
    rnd = random.Random(762)
    a = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(a)
    fnt = font(["segoepr.ttf", "segoeprb.ttf", "arial.ttf"], int(H * 0.78))
    d.text((W * 0.03, -H * 0.02), "7,62", font=fnt, fill=230)
    # tick: a short cross line and a second one, crossed out (the first mark was corrected)
    xr = W * 0.84
    d.line([(xr, H * 0.08), (xr + W * 0.01, H * 0.92)], fill=220, width=int(H * 0.06))
    d.line([(xr - W * 0.07, H * 0.15), (xr - W * 0.065, H * 0.85)], fill=150, width=int(H * 0.05))
    d.line([(xr - W * 0.10, H * 0.62), (xr - W * 0.035, H * 0.38)], fill=150, width=int(H * 0.04))
    # pressure and a ragged stroke: multiply by patches and by stripes along the grain (the image X
    # axis)
    press = blotches((W, H), 7, 30, 0.04, 0.12, 140, 255, H * 0.08)
    press = ImageChops.add(press, Image.new("L", (W, H), 90))
    grain = Image.new("L", (W, H), 255)
    gd = ImageDraw.Draw(grain)
    for _ in range(int(H / S * 2)):
        y = rnd.uniform(0, H)
        gd.line([(0, y), (W, y + rnd.uniform(-2, 2) * S)], fill=rnd.randint(60, 160), width=max(1, S // 2))
    grain = grain.filter(ImageFilter.GaussianBlur(S * 0.4))
    a = ImageChops.multiply(ImageChops.multiply(a, press), grain)
    img = Image.new("RGBA", (W, H), (46, 46, 52, 255))
    img.putalpha(a)
    save(img, (W // S, H // S), name)


def make_stamp(name, w_mm, h_mm, px_mm=24):
    """Stamp on the breech: four punched digits, the row wobbles a little (each digit has its own punch),
    the pit bottoms are dark, the rims light - the bluing is knocked off.
    """
    W, H = w_mm * px_mm * S, h_mm * px_mm * S
    rnd = random.Random(3317)
    fnt = font(["consolab.ttf", "lucon.ttf", "arialbd.ttf"], int(H * 0.82))
    dark = Image.new("L", (W, H), 0)
    edge = Image.new("L", (W, H), 0)
    dd, ed = ImageDraw.Draw(dark), ImageDraw.Draw(edge)
    step = W / 4.4
    for k, ch in enumerate("3317"):
        x = W * 0.05 + k * step + rnd.uniform(-0.04, 0.04) * step
        y = rnd.uniform(-0.05, 0.05) * H
        l, t, r, b = dd.textbbox((0, 0), ch, font=fnt)
        pos = (x - l, (H - (b - t)) / 2 - t + y)
        ed.text(pos, ch, font=fnt, fill=255, stroke_width=int(H * 0.05), stroke_fill=255)
        dd.text(pos, ch, font=fnt, fill=255)
    rim = ImageChops.subtract(edge, dark)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img = Image.composite(Image.new("RGBA", (W, H), (150, 152, 156, 255)), img, rim.point(lambda v: int(v * 0.8)))
    img = Image.composite(Image.new("RGBA", (W, H), (14, 14, 16, 255)), img, dark.point(lambda v: int(v * 0.9)))
    save(img, (W // S, H // S), name)


def preview(names, name):
    """All decals on a grey background, to look at."""
    ims = [Image.open(os.path.join(WORK, n)) for n in names]
    sc = 3
    ims = [im.resize((im.width * sc, im.height * sc), Image.NEAREST) for im in ims]
    W = max(im.width for im in ims) + 40
    H = sum(im.height for im in ims) + 20 * (len(ims) + 1)
    bg = Image.new("RGBA", (W, H), (96, 140, 138, 255))
    y = 20
    for im in ims:
        bg.alpha_composite(im, (20, y))
        y += im.height + 20
    bg.save(os.path.join(WORK, name))
    print("wrote", os.path.join(WORK, name))


if __name__ == "__main__":
    make_cast("decal_cast.png", 22, 13)
    make_pencil("decal_pencil.png", 30, 9)
    make_stamp("decal_stamp.png", 16, 4)
    preview(["decal_cast.png", "decal_pencil.png", "decal_stamp.png"], "decals_preview.png")
