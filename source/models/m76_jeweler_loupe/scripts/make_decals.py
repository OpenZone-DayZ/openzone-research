"""Decals of the stand loupe (system Python + Pillow): an inventory number in white paint on the
cast-iron base and a pen entry on the ring tag - the "585" hallmark. Digits only, no letters.

    python make_decals.py      -> ../work/decal_*.png
"""
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
PAINT = (226, 224, 214, 255)
INK = (34, 44, 120, 255)                # blue ballpoint ink


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def speckle(size, seed, density, rmax):
    """Mask of small chips (255 = intact, 0 = chipped out)."""
    rnd = random.Random(seed)
    m = Image.new("L", size, 255)
    d = ImageDraw.Draw(m)
    w, h = size
    for _ in range(int(w * h * density)):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.uniform(0.3, 1.0) * rmax
        d.ellipse([x - r, y - r, x + r, y + r], fill=0)
    return m


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def make_number(name, text, w_mm, h_mm, angle, seed, px_mm=8):
    """White-paint inventory number by hand (as on M71): uneven strokes, paint worn off in places."""
    W, H = w_mm * px_mm * S, h_mm * px_mm * S
    lay = Image.new("L", (W, H), 0)
    ImageDraw.Draw(lay).text((W / 2, H / 2), text, fill=255, font=font(r"C:\Windows\Fonts\segoeprb.ttf", int(H * 0.80)),
                             anchor="mm")
    lay = lay.rotate(angle, resample=Image.BICUBIC, center=(W / 2, H / 2))
    lay = lay.filter(ImageFilter.GaussianBlur(S * 0.8)).point(lambda v: 255 if v > 110 else 0)
    wear = speckle((W, H), seed, 0.0000500, H * 0.04).filter(ImageFilter.GaussianBlur(S))
    a = ImageChops.multiply(lay, wear.point(lambda v: 230 if v > 128 else 30))
    img = Image.new("RGBA", (W, H), PAINT)
    img.putalpha(a)
    save(img, (w_mm * px_mm, h_mm * px_mm), name)


def make_tag(name, w_mm, h_mm, px_mm=24):
    """Tag face, 24 x 13 mm (hole on the left): the "585" hallmark in ballpoint pen with an underline,
    a cardboard reinforcing ring around the hole, the hole itself dark (velvet under it). The
    background is transparent: the cardboard comes from the tag material.
    """
    W, H = w_mm * px_mm * S, h_mm * px_mm * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    hx, hy, hr = H * 0.42, H * 0.50, H * 0.12
    d.ellipse([hx - hr * 2.0, hy - hr * 2.0, hx + hr * 2.0, hy + hr * 2.0], fill=(196, 178, 132, 255))
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(14, 18, 40, 255))
    ink = Image.new("L", (W, H), 0)
    di = ImageDraw.Draw(ink)
    di.text((W * 0.66, H * 0.44), "585", fill=255, font=font(r"C:\Windows\Fonts\Inkfree.ttf", int(H * 0.50)),
            anchor="mm")
    rnd = random.Random(76)
    pts = [(W * 0.42 + W * 0.46 * t, H * 0.80 + rnd.uniform(-1, 1) * H * 0.015 - H * 0.04 * t)
           for t in [i / 8 for i in range(9)]]
    di.line(pts, fill=255, width=int(H * 0.035))
    ink = ink.rotate(-3.0, resample=Image.BICUBIC, center=(W * 0.6, H * 0.5))
    # the ink lays down unevenly: paler in places
    pale = speckle((W, H), 77, 0.0000020, H * 0.05).filter(ImageFilter.GaussianBlur(S * 2))
    ink = ImageChops.multiply(ink, pale.point(lambda v: 255 if v > 128 else 150))
    img.paste(Image.new("RGBA", (W, H), INK), (0, 0), ink)
    save(img, (w_mm * px_mm, h_mm * px_mm), name)


if __name__ == "__main__":
    make_number("decal_num.png", "36", 16, 10, 3.0, 91)
    make_tag("decal_tag.png", 24, 13)
