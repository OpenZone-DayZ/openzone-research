"""Decal for the anomaly probe (system Python + Pillow): a round yellow sticker with the radiation
hazard trefoil on the probe tube. No lettering, the sign is a symbol. Round rather than the square
plate of M03, so the module and the bench it stands on do not look alike.

    python make_decals.py      -> ../work/decal_trefoil.png

Size matches build_m69.py (STICKER_D).
"""
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
BLACK = (22, 20, 18, 255)
YELLOW = (232, 184, 26, 255)
STICKER_D = 0.030


def trefoil_mask(n, cx, cy, r):
    """Hazard sign as built to GOST 17925 / ISO 361: a circle of radius r in the centre, three blades of
    60 degrees between radii 1.5r and 5r; one blade points down (as in M03)."""
    m = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(m)
    R = 5.0 * r
    for k in range(3):
        mid = 90 + 120 * k                         # PIL angles run clockwise from +x, so 90 is down
        d.pieslice([cx - R, cy - R, cx + R, cy + R], mid - 30, mid + 30, fill=255)
    hole = Image.new("L", (n, n), 0)
    ImageDraw.Draw(hole).ellipse([cx - 1.5 * r, cy - 1.5 * r, cx + 1.5 * r, cy + 1.5 * r], fill=255)
    m = ImageChops.subtract(m, hole)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    return m


def make_trefoil(px=256):
    """Round sticker: yellow field, thin black rim, black trefoil, light scratches over the field. The
    worn edge comes from the sticker material (chips down to the tube metal, build_m69.py)."""
    n = px * S
    rng = random.Random(69)
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, n - 1, n - 1], fill=BLACK)
    m = int(n * 0.035)
    d.ellipse([m, m, n - 1 - m, n - 1 - m], fill=YELLOW)
    sym = trefoil_mask(n, n / 2, n / 2, n * 0.082)
    img.paste(Image.new("RGBA", (n, n), BLACK), (0, 0), sym)
    # scratches: short light strokes (the sticker is rubbed against the shelf and the cradle)
    sc = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sc)
    for _ in range(14):
        x, y = rng.uniform(0.15, 0.85) * n, rng.uniform(0.15, 0.85) * n
        L = rng.uniform(0.05, 0.16) * n
        ds.line([(x, y), (x + L, y + rng.uniform(-0.25, 0.25) * L)], fill=(246, 232, 190, 150), width=S)
    img = Image.alpha_composite(img, Image.composite(sc, Image.new("RGBA", (n, n), (0, 0, 0, 0)), img.getchannel("A")))
    img = img.resize((px, px), Image.LANCZOS)
    img.putalpha(img.getchannel("A").filter(ImageFilter.GaussianBlur(0.6)))
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, "decal_trefoil.png")
    img.save(path)
    print("wrote", path)


if __name__ == "__main__":
    make_trefoil()
