"""Decals of the ballistic sample M52 (system Python + Pillow), no letters:
- decal_tag.png - a tag of white card 48 x 24 mm with corners cut at the eyelet: a blue stripe along the
  edge (the Ballistics line), empty fields, a number in digits in pencil, a reinforcing ring of the
  eyelet; rotated as on the model (TAG_ROT), in the TAG_BOX square of world axes around TAG_C;
- decal_sticker.png - an empty inventory sticker on the face of the body: yellowed paper, a frame and
  empty fields, worn edges and corner.

    python make_decals.py      -> ../work/decal_*.png

Sizes come from m52_layout.py (shared with build_m52.py).
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m52_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                       # supersampling factor for drawing (the result is downscaled)

CARD = (234, 230, 216)
BLUE = (38, 84, 168)
INK = (92, 92, 96)          # ink of the fields
PENCIL = (70, 72, 78)


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def font(names, px):
    for name in names:
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


def noise_layer(size, scale, seed, lo=0, hi=255):
    """Soft noise (L): a random grid, stretched and blurred."""
    rnd = random.Random(seed)
    w, h = max(2, size[0] // scale), max(2, size[1] // scale)
    small = Image.new("L", (w, h))
    small.putdata([rnd.randint(lo, hi) for _ in range(w * h)])
    return small.resize(size, Image.BICUBIC).filter(ImageFilter.GaussianBlur(scale * 0.35))


def grime_edge(img, k, width, color, seed):
    """Worn edge: a dark rim with noise."""
    W, H = img.size
    edge = Image.new("L", (W, H), 0)
    ImageDraw.Draw(edge).rectangle([0, 0, W - 1, H - 1], outline=120, width=int(width * k))
    edge = ImageChops.multiply(edge.filter(ImageFilter.GaussianBlur(width * 1.2 * k)), noise_layer((W, H), 3 * k, seed))
    return Image.composite(Image.new("RGBA", (W, H), color + (255,)), img, edge)


def make_tag(name, ppm):
    """Tag in its own axes (the long axis runs left to right, the eyelet on the left), then rotated and
    pasted into the world-axes square (the top of the image is the model's +Y).
    """
    k = ppm * S
    W, H = int(L.TAG_L * 1000 * k), int(L.TAG_W * 1000 * k)
    img = Image.new("RGBA", (W, H), CARD + (255,))
    tone = noise_layer((W, H), 5 * k, 4, 0, 60)
    img = Image.composite(Image.new("RGBA", (W, H), (214, 208, 190, 255)), img, tone)
    d = ImageDraw.Draw(img)
    # blue stripe along the top edge (the Ballistics line), from the eyelet to the end
    d.rectangle([int(W * 0.24), int(H * 0.08), W, int(H * 0.30)], fill=BLUE + (255,))
    # fields
    for i, y in enumerate((0.55, 0.74, 0.92)):
        d.line([(W * 0.27, H * y), (W * 0.95, H * y)], fill=INK + (255,), width=max(1, int(0.16 * k)))
    d.line([(W * 0.66, H * 0.40), (W * 0.66, H * 0.55)], fill=INK + (255,), width=max(1, int(0.16 * k)))
    # hand-written number in pencil (digits)
    f = font(("Inkfree.ttf", "segoepr.ttf", "segoesc.ttf", "arial.ttf"), int(H * 0.20))
    d.text((W * 0.29, H * 0.53), "12-0731", fill=PENCIL + (255,), font=f, anchor="ls")
    d.text((W * 0.70, H * 0.53), "4", fill=PENCIL + (255,), font=f, anchor="ls")
    # eyelet: a reinforcing ring and a hole
    hx = W / 2 - L.TAG_HOLE * 1000 * k
    hy = H / 2
    r1, r0 = 3.6 * k, 1.6 * k
    d.ellipse([hx - r1, hy - r1, hx + r1, hy + r1], fill=(196, 206, 222, 255), outline=(150, 160, 178, 255),
              width=int(0.3 * k))
    d.ellipse([hx - r0, hy - r0, hx + r0, hy + r0], fill=(60, 62, 64, 255))
    img = grime_edge(img, k, 1.0, (150, 140, 118), 9)
    # rotation as on the model and pasting into the TAG_BOX square centred at TAG_C
    rot = img.rotate(L.TAG_ROT, resample=Image.BICUBIC, expand=True)
    B = int(L.TAG_BOX * 1000 * k)
    box = Image.new("RGBA", (B, B), (0, 0, 0, 0))
    box.alpha_composite(rot, ((B - rot.size[0]) // 2, (B - rot.size[1]) // 2))
    save(box, (B // S, B // S), name)


def make_sticker(name, ppm):
    """Empty inventory sticker: a frame, empty fields, a worn corner."""
    k = ppm * S
    W, H = int(L.STK[0] * 1000 * k), int(L.STK[1] * 1000 * k)
    img = Image.new("RGBA", (W, H), (226, 220, 196, 255))
    tone = noise_layer((W, H), 4 * k, 12, 0, 90)
    img = Image.composite(Image.new("RGBA", (W, H), (200, 190, 156, 255)), img, tone)
    d = ImageDraw.Draw(img)
    m = 1.6 * k
    d.rectangle([m, m, W - m, H - m], outline=(110, 108, 100, 255), width=int(0.35 * k))
    d.line([(m, H * 0.34), (W - m, H * 0.34)], fill=(110, 108, 100, 255), width=int(0.3 * k))
    for y in (0.56, 0.78):
        d.line([(W * 0.12, H * y), (W * 0.88, H * y)], fill=(150, 146, 134, 255), width=int(0.22 * k))
    # rubbed by fingers at the lower right corner
    rub = Image.new("L", (W, H), 0)
    ImageDraw.Draw(rub).ellipse([W * 0.70, H * 0.55, W * 1.15, H * 1.25], fill=150)
    rub = ImageChops.multiply(rub.filter(ImageFilter.GaussianBlur(2.0 * k)), noise_layer((W, H), 2 * k, 14))
    img = Image.composite(Image.new("RGBA", (W, H), (150, 142, 118, 255)), img, rub)
    img = grime_edge(img, k, 1.4, (96, 90, 74), 13)
    save(img, (W // S, H // S), name)


if __name__ == "__main__":
    make_tag("decal_tag.png", 10)
    make_sticker("decal_sticker.png", 10)
