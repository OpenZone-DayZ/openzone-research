"""Decals for the lead cabinet (system Python + Pillow): the radiation hazard sign on a plate, the
draft gauge scale (zero in the middle, divisions and digits), an empty inventory tag. No letters:
only digits, divisions and signs.

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def font(px):
    try:
        return ImageFont.truetype("arial.ttf", int(px))
    except OSError:
        return ImageFont.load_default()


def make_trefoil(name, px):
    """Radiation hazard sign: a black trefoil on a yellow square with a black border, bolt holes in the corners."""
    W = px * S
    img = Image.new("RGBA", (W, W), (226, 184, 30, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, W - 1], outline=(22, 22, 22, 255), width=int(W * 0.035))
    cx, cy = W / 2, W / 2
    R, r0 = W * 0.36, W * 0.075
    for k in range(3):
        a = 270 + 120 * k
        d.pieslice([cx - R, cy - R, cx + R, cy + R], -(a + 30), -(a - 30), fill=(22, 22, 22, 255))
    d.ellipse([cx - r0 * 1.5, cy - r0 * 1.5, cx + r0 * 1.5, cy + r0 * 1.5], fill=(226, 184, 30, 255))
    d.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], fill=(22, 22, 22, 255))
    for x in (W * 0.08, W * 0.92):
        for y in (W * 0.08, W * 0.92):
            d.ellipse([x - W * 0.025, y - W * 0.025, x + W * 0.025, y + W * 0.025], fill=(60, 60, 60, 255))
    save(img, (px, px), name)


def make_gauge(name, px):
    """Draft gauge scale (vacuum in the cabinet): round, zero at the top in the middle, 40 divisions each
    way over 135 degrees, digits 0-10-20-30-40 without signs, a red mark of the working vacuum at the
    left, a white backing with the shadow of the rim. The needle is a model part (ozl_needle)."""
    W = px * S
    c = W / 2
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, W - 1, W - 1], fill=(26, 26, 26, 255))                  # black edge under the rim
    R0 = W * 0.47
    d.ellipse([c - R0, c - R0, c + R0, c + R0], fill=(232, 228, 214, 255))
    ink = (28, 28, 26, 255)
    R = W * 0.40
    for k in range(-40, 41):
        a = math.radians(90 - 135 * k / 40)                                # 0 is at the top, +k to the right
        ln = 0.13 if k % 10 == 0 else (0.085 if k % 5 == 0 else 0.05)
        p = (c + R * math.cos(a), c - R * math.sin(a))
        q = (c + R * (1 - ln) * math.cos(a), c - R * (1 - ln) * math.sin(a))
        d.line([p, q], fill=ink, width=S * (3 if k % 10 == 0 else 1) + (1 if k % 5 == 0 else 0))
    d.arc([c - R, c - R, c + R, c + R], -(90 + 135), -(90 - 135), fill=ink, width=S * 2)
    # working vacuum zone - a red arc at the left (the needle is there in "work")
    Rr = R * 0.93
    d.arc([c - Rr, c - Rr, c + Rr, c + Rr], -(90 + 135 * 0.75), -(90 + 135 * 0.35), fill=(176, 36, 28, 255),
          width=S * 5)
    f = font(W * 0.085)
    for k in range(-40, 41, 10):
        a = math.radians(90 - 135 * k / 40)
        p = (c + R * 0.68 * math.cos(a), c - R * 0.68 * math.sin(a))
        d.text(p, str(abs(k)), fill=ink, font=f, anchor="mm")
    # scale signs: minus on the left (vacuum), plus on the right (pressure) - not letters
    for sx, sign in ((-1, "-"), (1, "+")):
        d.text((c + sx * R * 0.30, c + R * 0.30), sign, fill=ink, font=font(W * 0.12), anchor="mm")
    d.ellipse([c - W * 0.045, c - W * 0.045, c + W * 0.045, c + W * 0.045], fill=(40, 40, 40, 255))
    # rim shadow along the scale edge
    sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([c - R0, c - R0, c + R0, c + R0], outline=(0, 0, 0, 110), width=int(W * 0.04))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(W * 0.02)))
    save(img, (px, px), name)


def make_tag(name, w, h):
    """Inventory tag without text: an aluminium plate, two rivets, a stamped frame."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (178, 182, 184, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([S * 6, S * 6, W - S * 6, H - S * 6], outline=(120, 124, 128, 255), width=S * 2)
    for x in (S * 14, W - S * 14):
        d.ellipse([x - S * 5, H / 2 - S * 5, x + S * 5, H / 2 + S * 5], fill=(96, 98, 100, 255))
    for i in range(5):
        y = H * (0.3 + 0.1 * i)
        d.line([(W * 0.22, y), (W * 0.78, y)], fill=(150, 154, 156, 255), width=S)
    save(img, (w, h), name)


if __name__ == "__main__":
    make_trefoil("decal_trefoil.png", 256)
    make_gauge("decal_gauge.png", 256)
    make_tag("decal_tag.png", 160, 64)
