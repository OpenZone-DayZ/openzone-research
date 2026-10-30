"""Decals of the lead house (system Python + Pillow): a yellow sticker with a radiation hazard sign (a
black trefoil, GOST 17925-72; no caption), a torn-off corner, worn edges; hand-painted white
inventory numbers on the bricks - digits only.

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
YELLOW = (224, 186, 36, 255)
INK = (24, 22, 20, 255)


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def speckle(size, seed, density, rmax):
    """Mask of small chips (255 is intact, 0 is chipped out)."""
    rnd = random.Random(seed)
    m = Image.new("L", size, 255)
    d = ImageDraw.Draw(m)
    w, h = size
    for _ in range(int(w * h * density)):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.uniform(0.3, 1.0) * rmax
        d.ellipse([x - r, y - r, x + r, y + r], fill=0)
    return m


def make_sticker(name, w_mm, h_mm, px_mm=5):
    """40 x 54 mm sticker: a yellow field, a black trefoil, an empty black strip-frame under it. The bottom
    right corner is torn off, the edges are chipped, there is wear over the field."""
    W, H = w_mm * px_mm * S, h_mm * px_mm * S
    img = Image.new("RGBA", (W, H), YELLOW)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=INK, width=int(W * 0.04))
    cx, cy = W / 2, H * 0.40
    R, r0 = W * 0.36, W * 0.075
    for k in range(3):
        a = 270 + 120 * k
        d.pieslice([cx - R, cy - R, cx + R, cy + R], -(a + 30), -(a - 30), fill=INK)
    d.ellipse([cx - r0 * 1.5, cy - r0 * 1.5, cx + r0 * 1.5, cy + r0 * 1.5], fill=YELLOW)
    d.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], fill=INK)
    # empty field under the sign (for a hand entry - left blank)
    d.rectangle([W * 0.14, H * 0.80, W * 0.86, H * 0.90], outline=INK, width=int(W * 0.018))
    # fading and dirt: darker and lighter patches
    rnd = random.Random(71)
    stain = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(stain)
    for _ in range(40):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.04, 0.16) * W
        sd.ellipse([x - r, y - r, x + r, y + r], fill=rnd.randint(10, 45))
    stain = stain.filter(ImageFilter.GaussianBlur(W * 0.05))
    img = Image.composite(Image.new("RGBA", (W, H), (96, 84, 60, 255)), img, stain)
    # shape: a torn-off corner (a ragged polyline edge), chips along the edge
    a = Image.new("L", (W, H), 255)
    ad = ImageDraw.Draw(a)
    pts = [(W * 0.52, H + 2)]
    n = 14
    for i in range(1, n):
        t = i / n
        x = W * 0.52 + (W * 0.48) * t + rnd.uniform(-1, 1) * W * 0.02
        y = H - H * 0.30 * t + rnd.uniform(-1, 1) * H * 0.012
        pts.append((x, y))
    pts += [(W + 2, H * 0.70), (W + 2, H + 2)]
    ad.polygon(pts, fill=0)
    edge = Image.new("L", (W, H), 0)
    ImageDraw.Draw(edge).rectangle([int(W * 0.03), int(W * 0.03), W - int(W * 0.03), H - int(W * 0.03)], fill=255)
    edge = edge.filter(ImageFilter.GaussianBlur(W * 0.02))
    holes = speckle((W, H), 72, 0.0000035, W * 0.02)
    rim = ImageChops.lighter(edge, holes)                      # chips only at the edge
    a = ImageChops.multiply(a, rim.point(lambda v: 255 if v > 120 else 0))
    a = ImageChops.multiply(a, speckle((W, H), 73, 0.0000008, W * 0.012))   # rare wear over the field
    img.putalpha(a)
    save(img, (w_mm * px_mm, h_mm * px_mm), name)


def make_number(name, text, w_mm, h_mm, angle, seed, px_mm=6):
    """Inventory number in hand-painted white: uneven strokes, the paint has worn off in places."""
    W, H = w_mm * px_mm * S, h_mm * px_mm * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\segoeprb.ttf", int(H * 0.82))
    except OSError:
        font = ImageFont.load_default()
    lay = Image.new("L", (W, H), 0)
    ImageDraw.Draw(lay).text((W / 2, H / 2), text, fill=255, font=font, anchor="mm")
    lay = lay.rotate(angle, resample=Image.BICUBIC, center=(W / 2, H / 2))
    lay = lay.filter(ImageFilter.GaussianBlur(S * 0.8)).point(lambda v: 255 if v > 110 else 0)
    wear = speckle((W, H), seed, 0.0000400, H * 0.035).filter(ImageFilter.GaussianBlur(S))
    a = ImageChops.multiply(lay, wear.point(lambda v: 235 if v > 128 else 40))
    img = Image.new("RGBA", (W, H), (226, 224, 214, 255))
    img.putalpha(a)
    save(img, (w_mm * px_mm, h_mm * px_mm), name)


if __name__ == "__main__":
    make_sticker("decal_sticker.png", 40, 54)
    make_number("decal_num_12.png", "12", 36, 24, 4.0, 81)
    make_number("decal_num_7.png", "7", 24, 34, -6.0, 82)
    make_number("decal_num_31.png", "31", 36, 24, -3.0, 83)
