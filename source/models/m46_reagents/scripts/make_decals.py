"""Reagent kit decals (system Python + Pillow): the colour comparator scale on the card in the lid (two
rows of squares from pale to saturated, concentration digits below, like water-analysis kits) and the
inventory tag on the side (a number in digits). No letters.

    python make_decals.py      -> ../work/decal_*.png

Sizes match build_m46.py (CHART_*, TAG_*).
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4
INK = (34, 34, 38, 255)

CHART_W, CHART_H = 0.150, 0.088         # comparator card on the inner side of the lid
TAG_W, TAG_H = 0.032, 0.020             # tag on the side


def font(px):
    for name in ("arialbd.ttf", "arial.ttf"):
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


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)) + (255,)


def make_chart(name, px):
    """Yellowed card: frame, two rows of 6 squares (pink - ammonia/nitrite, blue - phosphate), the
    digits 0 0.1 0.2 0.5 1 2 below each; a couple of dashes instead of text on top.
    """
    h = int(round(px * CHART_H / CHART_W))
    W, H = px * S, h * S
    img = Image.new("RGBA", (W, H), (232, 226, 204, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([S * 4, S * 4, W - S * 5, H - S * 5], outline=(80, 74, 66, 255), width=S * 2)
    for i, w in enumerate((0.42, 0.28)):                       # title: bars without letters
        y = H * (0.10 + 0.05 * i)
        d.line([(W * 0.08, y), (W * (0.08 + w), y)], fill=(120, 112, 100, 255), width=S * 2)
    rows = [((246, 236, 232), (184, 30, 92)), ((236, 240, 238), (24, 58, 150))]
    labels = ("0", "0.1", "0.2", "0.5", "1", "2")
    f = font(int(H * 0.075))
    side = W * 0.118
    gap = (W * 0.84 - 6 * side) / 5
    for r, (c0, c1) in enumerate(rows):
        y0 = H * (0.24 + 0.38 * r)
        for i in range(6):
            x0 = W * 0.08 + i * (side + gap)
            d.rectangle([x0, y0, x0 + side, y0 + side * 0.9], fill=mix(c0, c1, (i / 5) ** 0.8),
                        outline=(60, 56, 52, 255), width=S)
            d.text((x0 + side / 2, y0 + side * 0.9 + H * 0.06), labels[i], fill=INK, font=f, anchor="mm")
    save(img, (px, h), name)


def make_tag(name, px):
    """Inventory tag: yellowed paper, frame, a number in digits, a strip for a signature."""
    h = int(round(px * TAG_H / TAG_W))
    W, H = px * S, h * S
    img = Image.new("RGBA", (W, H), (226, 214, 176, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([S * 3, S * 3, W - S * 4, H - S * 4], outline=(70, 60, 50, 255), width=S * 2)
    d.text((W * 0.5, H * 0.40), "0592", fill=(40, 36, 60, 255), font=font(int(H * 0.36)), anchor="mm")
    d.line([(W * 0.18, H * 0.74), (W * 0.82, H * 0.74)], fill=(70, 60, 50, 255), width=S * 2)
    save(img, (px, h), name)


if __name__ == "__main__":
    make_chart("decal_chart.png", 384)
    make_tag("decal_tag.png", 128)
