"""Decals of the thermal sample case (system Python + Pillow): a biohazard sign on a yellow sticker
(lid), a paper tag with an eyelet and empty fields (no text), white snowflakes on the blue cold pack. No
letters: only the sign, the fields and pictograms.

    python make_decals.py      -> ../work/decal_*.png

Sizes and positions match build_m47.py (BIO_*, TAG_*, PACK_*): the tag is rotated there, so the image is
drawn in the world axes of the TAG_BOX square around the tag centre.
"""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4

BIO = 0.025                                   # biohazard sticker, square
TAG_C = (0.0815, -0.002)                      # tag centre on the lid (x, y)
TAG_L, TAG_W, TAG_CUT = 0.040, 0.022, 0.005   # length, width, corner cut at the eyelet
TAG_ROT = 14.0                                # rotation of the long axis from +y, counter-clockwise, degrees
TAG_HOLE = 0.0145                             # eyelet: from the centre along the long axis
TAG_BOX = 0.052                               # square of the tag image
PACK_L, PACK_W = 0.170, 0.040                 # top of the cold pack
SNOW = [(-0.046, 0.000, 0.0125), (0.066, 0.004, 0.0100), (-0.075, -0.004, 0.0100), (0.010, 0.0, 0.011)]


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def disc(mask_size, cx, cy, r):
    m = Image.new("L", mask_size, 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    return m


def trefoil(n, rs):
    """Mask of a biohazard sign of radius rs in an n square: three crescents (a big circle minus a
    circle shifted outwards), a hole in the centre, a ring with gaps at the crescents.
    """
    c = n / 2
    sz = (n, n)

    def crescents(grow):
        m = Image.new("L", sz, 0)
        for k in range(3):
            a = math.radians(90 + 120 * k)
            ca, sa = math.cos(a), -math.sin(a)
            big = disc(sz, c + ca * 0.42 * rs, c + sa * 0.42 * rs, (0.58 + grow) * rs)
            cut = disc(sz, c + ca * 0.63 * rs, c + sa * 0.63 * rs, (0.42 - grow) * rs)
            m = ImageChops.lighter(m, ImageChops.subtract(big, cut))
        return m
    body = crescents(0.0)
    halo = crescents(0.05)
    ring = ImageChops.subtract(disc(sz, c, c, 0.70 * rs), disc(sz, c, c, 0.60 * rs))
    ring = ImageChops.subtract(ring, halo)
    m = ImageChops.lighter(body, ring)
    return ImageChops.subtract(m, disc(sz, c, c, 0.15 * rs))


def make_bio(name, px):
    """Yellow sticker with a black frame and the sign, the edges slightly worn (the sticker is not new)."""
    n = px * S
    img = Image.new("RGBA", (n, n), (236, 182, 26, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([n * 0.05, n * 0.05, n * 0.95, n * 0.95], outline=(22, 20, 18, 255), width=int(n * 0.035))
    sym = trefoil(n, n * 0.36)
    img.paste((22, 20, 18, 255), (0, 0), sym)
    rnd = random.Random(47)
    wear = Image.new("L", (n, n), 0)
    dw = ImageDraw.Draw(wear)
    for _ in range(70):                                    # wear is heavier towards the edges
        x, y = rnd.random() * n, rnd.random() * n
        e = min(x, y, n - x, n - y) / n
        if rnd.random() > e * 6:
            r = n * (0.004 + rnd.random() * 0.012)
            dw.ellipse([x - r, y - r, x + r, y + r], fill=int(120 + rnd.random() * 100))
    wear = wear.filter(ImageFilter.GaussianBlur(n * 0.004))
    img = Image.composite(Image.new("RGBA", (n, n), (238, 226, 190, 255)), img, wear)
    save(img, (px, px), name)


def make_tag(name, px):
    """Tag: manila card, darker edge, an eyelet (a light ring; the hole shows the lid colour under it),
    four empty pencil fields, a couple of stains. The TAG_BOX square is in world axes: right +x, up +y.
    """
    n = px * S
    k = n / TAG_BOX
    img = Image.new("RGBA", (n, n), (212, 188, 138, 255))
    d = ImageDraw.Draw(img)
    a = math.radians(TAG_ROT)
    dl = (-math.sin(a), math.cos(a))                       # along the long axis
    dt = (math.cos(a), math.sin(a))                        # across

    def P(s, t):
        x = TAG_C[0] + s * dl[0] + t * dt[0]
        y = TAG_C[1] + s * dl[1] + t * dt[1]
        return ((x - TAG_C[0]) * k + n / 2, n / 2 - (y - TAG_C[1]) * k)
    h, w, cut = TAG_L / 2, TAG_W / 2, TAG_CUT
    outline = [P(-h, -w), P(-h, w), P(h - cut, w), P(h, w - cut), P(h, -w + cut), P(h - cut, -w)]
    rnd = random.Random(7)
    stains = Image.new("L", (n, n), 0)
    ds = ImageDraw.Draw(stains)
    for _ in range(5):
        s, t = (rnd.random() - 0.5) * TAG_L * 0.8, (rnd.random() - 0.5) * TAG_W * 0.8
        x, y = P(s, t)
        r = k * (0.002 + rnd.random() * 0.004)
        ds.ellipse([x - r, y - r, x + r, y + r], fill=int(60 + rnd.random() * 60))
    stains = stains.filter(ImageFilter.GaussianBlur(k * 0.0012))
    img = Image.composite(Image.new("RGBA", (n, n), (176, 146, 96, 255)), img, stains)
    d = ImageDraw.Draw(img)
    d.line(outline + outline[:1], fill=(160, 132, 88, 255), width=int(k * 0.0008))
    for s in (-0.012, -0.0055, 0.001, 0.0075):            # empty fields
        d.line([P(s, -w + 0.003), P(s, w - 0.003)], fill=(118, 116, 132, 255), width=int(k * 0.00035))
    hx, hy = P(TAG_HOLE, 0.0)
    for r, col in ((0.0047, (226, 210, 168, 255)), (0.0021, (214, 212, 200, 255))):
        d.ellipse([hx - r * k, hy - r * k, hx + r * k, hy + r * k], fill=col, outline=(150, 128, 90, 255),
                  width=int(k * 0.0003))
    save(img, (px, px), name)


def snowflake(d, cx, cy, r, col, wd):
    for i in range(6):
        a = math.radians(90 + 60 * i)
        ex, ey = cx + r * math.cos(a), cy - r * math.sin(a)
        d.line([(cx, cy), (ex, ey)], fill=col, width=wd)
        for f in (0.45, 0.72):                             # side branches
            bx, by = cx + r * f * math.cos(a), cy - r * f * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.radians(42)
                L = r * (0.34 if f < 0.6 else 0.24)
                d.line([(bx, by), (bx + L * math.cos(b), by - L * math.sin(b))], fill=col, width=wd)


def make_snow(name, px):
    """Snowflakes on the top of the cold pack: white, translucent (print on film)."""
    h = int(round(px * PACK_W / PACK_L))
    W, H = px * S, h * S
    k = W / PACK_L
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for x, y, r in SNOW:
        snowflake(d, (x + PACK_L / 2) * k, (PACK_W / 2 - y) * k, r * k, (236, 242, 255, 225), int(k * 0.0011))
    save(img, (px, h), name)


if __name__ == "__main__":
    make_bio("decal_bio.png", 256)
    make_tag("decal_tag.png", 256)
    make_snow("decal_snow.png", 1024)
