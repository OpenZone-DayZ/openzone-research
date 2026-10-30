"""Decals of the anomalous sample (system Python + Pillow): a black trefoil on the yellow ring tag and a
number stamped on the lid. No letters: the sign is a symbol, the number is digits.

    python make_decals.py      -> ../work/decal_*.png

Sizes match build_m48.py (TREFOIL_D, STAMP_D).
"""
import os

from PIL import Image, ImageChops, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscaling: clean edges
INK = (22, 20, 18, 255)
WHITE = (255, 255, 255, 255)


def font(px):
    for name in ("consolab.ttf", "consola.ttf", "arialbd.ttf", "arial.ttf"):
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


def trefoil_mask(n, cx, cy, r):
    """Sign built per GOST 17925 / ISO 361 (as in M04): a circle of radius r, three 60-degree blades
    between radii 1.5r and 5r; one blade points down.
    """
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


def make_trefoil(px=128):
    """Black trefoil on transparent: the background is the yellow paint of the ring tag."""
    n = px * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    img.paste(Image.new("RGBA", (n, n), INK), (0, 0), trefoil_mask(n, n / 2, n / 2, n * 0.098))
    save(img, (px, px), "decal_trefoil.png")


def make_stamp(px=256):
    """Lid stamp: the inventory number '0347' in the centre, a smaller batch number '126' below it (not
    a date: a year must not appear on the model) and a punch dot on top. White on transparent - the
    generator takes the alpha as the mask of the pressed relief.
    """
    n = px * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for text, size, cy in (("0347", 0.20, 0.47), ("126", 0.12, 0.66)):
        f = font(int(n * size))
        x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f)
        d.text((n / 2 - (x0 + x1) / 2, n * cy - (y0 + y1) / 2), text, font=f, fill=WHITE)
    r = n * 0.022
    d.ellipse([n / 2 - r, n * 0.27 - r, n / 2 + r, n * 0.27 + r], fill=WHITE)
    save(img, (px, px), "decal_stamp.png")


if __name__ == "__main__":
    make_trefoil()
    make_stamp()
