"""Decals for the glove box (system Python + Pillow): the radiation hazard sign and the draft gauge
scale. No letters: the sign is a symbol, the scale has digits only.

    python make_decals.py      -> ../work/decal_trefoil.png, ../work/decal_gauge.png
"""
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
BLACK = (22, 20, 18, 255)
YELLOW = (236, 186, 22, 255)


def font(px):
    for name in ("arial.ttf", "consola.ttf"):
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


def trefoil_mask(n, cx, cy, r):
    """Sign built per GOST 17925 / ISO 361: a circle of radius r in the centre, three 60-degree blades
    between radii 1.5r and 5r; one blade points down."""
    m = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(m)
    R = 5.0 * r
    for k in range(3):
        mid = 90 + 120 * k                         # PIL: angles run clockwise from +x, 90 is down
        d.pieslice([cx - R, cy - R, cx + R, cy + R], mid - 30, mid + 30, fill=255)
    hole = Image.new("L", (n, n), 0)
    ImageDraw.Draw(hole).ellipse([cx - 1.5 * r, cy - 1.5 * r, cx + 1.5 * r, cy + 1.5 * r], fill=255)
    m = ImageChops.subtract(m, hole)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    return m


def make_trefoil(px=512):
    """Yellow plate with rounded corners, black border, black trefoil."""
    n = px * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, n - 1, n - 1], radius=int(n * 0.08), fill=BLACK)
    m = int(n * 0.045)
    d.rounded_rectangle([m, m, n - 1 - m, n - 1 - m], radius=int(n * 0.06), fill=YELLOW)
    sym = trefoil_mask(n, n / 2, n / 2, n * 0.078)
    img.paste(Image.new("RGBA", (n, n), BLACK), (0, 0), sym)
    img = img.resize((px, px), Image.LANCZOS)
    a = img.getchannel("A").filter(ImageFilter.GaussianBlur(0.8))
    img.putalpha(a)
    path = os.path.join(WORK, "decal_trefoil.png")
    img.save(path)
    print("wrote", path)


def make_gauge(px=512):
    """Draft gauge scale: white field, 270-degree arc, ticks, digits 0..60 every 10, a red sector at the
    end. There is no needle on the scale: it is its own part with the bone ozl_needle in the generator
    and trembles in "work"."""
    n = px * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = n / 2
    d.ellipse([0, 0, n - 1, n - 1], fill=(28, 28, 28, 255))      # rim
    d.ellipse([n * 0.05, n * 0.05, n * 0.95, n * 0.95], fill=(236, 234, 226, 255))
    r_out, r_big, r_small = 0.40 * n, 0.31 * n, 0.35 * n
    start, sweep = 135.0, 270.0
    d.arc([c - r_out, c - r_out, c + r_out, c + r_out], start + sweep * 0.8, start + sweep, fill=(180, 30, 25, 255),
          width=int(0.035 * n))
    for i in range(61):
        if i % 2:
            continue
        a = math.radians(start + sweep * i / 60)
        r0 = r_big if i % 10 == 0 else r_small
        w = int(0.012 * n) if i % 10 == 0 else int(0.006 * n)
        d.line([(c + math.cos(a) * r0, c + math.sin(a) * r0), (c + math.cos(a) * r_out, c + math.sin(a) * r_out)],
               fill=(25, 25, 25, 255), width=w)
    f = font(int(0.075 * n))
    for i in range(0, 61, 10):
        a = math.radians(start + sweep * i / 60)
        rr = 0.23 * n
        d.text((c + math.cos(a) * rr, c + math.sin(a) * rr), str(i), fill=(25, 25, 25, 255), font=f, anchor="mm")
    img = img.resize((px, px), Image.LANCZOS)
    path = os.path.join(WORK, "decal_gauge.png")
    img.save(path)
    print("wrote", path)


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    make_trefoil()
    make_gauge()
