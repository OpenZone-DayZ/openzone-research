"""Decals of the lead case (system Python + Pillow):
- radiation hazard sign stencilled straight onto the lead: yellow square, black trefoil
  (GOST 17925-72), stencil bridges visible, paint worn in patches; no text;
- blank aluminium nameplate: embossed frame, empty line fields, two rivets at the edges;
- aluminium inventory tag on the handle: punched digits of the number (digits only), a ring hole.

    python make_decals.py      -> ../work/decal_*.png
"""
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
YELLOW = (220, 180, 40, 255)
INK = (26, 24, 22, 255)


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


def make_trefoil(name, mm, px_mm=6):
    """Stencil on lead, mm x mm: a yellow square with rounded corners, a trefoil with stencil bridges
    (the blades are split from the disc by narrow gaps, as a stencil is cut). Paint holds badly on
    soft lead: worn in patches and along the edges, the metal shows through the yellow (alpha).
    """
    W = mm * px_mm * S
    img = Image.new("RGBA", (W, W), YELLOW)
    d = ImageDraw.Draw(img)
    cx = cy = W / 2
    R, r0 = W * 0.40, W * 0.085
    for k in range(3):
        a = 270 + 120 * k
        d.pieslice([cx - R, cy - R, cx + R, cy + R], -(a + 30), -(a - 30), fill=INK)
    d.ellipse([cx - r0 * 1.5, cy - r0 * 1.5, cx + r0 * 1.5, cy + r0 * 1.5], fill=YELLOW)
    d.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], fill=INK)
    # stencil bridges: narrow yellow slits across the blades at the outer edge
    for k in range(3):
        a = 270 + 120 * k
        d.arc([cx - R * 0.78, cy - R * 0.78, cx + R * 0.78, cy + R * 0.78], -(a + 31), -(a - 31),
              fill=YELLOW, width=int(W * 0.018))
    # brush stroke: the paint lay unevenly, the yellow field is slightly blotchy
    rnd = random.Random(77)
    stain = Image.new("L", (W, W), 0)
    sd = ImageDraw.Draw(stain)
    for _ in range(30):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, W), rnd.uniform(0.05, 0.18) * W
        sd.ellipse([x - r, y - r, x + r, y + r], fill=rnd.randint(10, 40))
    stain = stain.filter(ImageFilter.GaussianBlur(W * 0.05))
    img = Image.composite(Image.new("RGBA", (W, W), (110, 96, 64, 255)), img, stain)
    # shape: a rounded square with an uneven edge (paint crept under the stencil)
    a = Image.new("L", (W, W), 0)
    ImageDraw.Draw(a).rounded_rectangle([W * 0.02, W * 0.02, W * 0.98, W * 0.98], radius=W * 0.08, fill=255)
    a = a.filter(ImageFilter.GaussianBlur(W * 0.006))
    # wear: large patches at the lower right corner and a scatter over the field
    wear = Image.new("L", (W, W), 255)
    wd = ImageDraw.Draw(wear)
    for _ in range(9):
        x, y = rnd.uniform(0.55, 1.0) * W, rnd.uniform(0.6, 1.0) * W
        r = rnd.uniform(0.03, 0.09) * W
        wd.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=0)
    wear = wear.filter(ImageFilter.GaussianBlur(W * 0.01)).point(lambda v: 255 if v > 150 else 0)
    a = ImageChops.multiply(a, wear)
    a = ImageChops.multiply(a, speckle((W, W), 78, 0.0000030, W * 0.012))
    a = a.point(lambda v: int(v * 0.94))
    img.putalpha(a)
    save(img, (mm * px_mm, mm * px_mm), name)


def make_plate(name, w_mm, h_mm, px_mm=8):
    """Blank nameplate: aluminium, embossed frame, three empty line fields, rivets at the edges."""
    W, H = w_mm * px_mm * S, h_mm * px_mm * S
    base = (168, 170, 168, 255)
    img = Image.new("RGBA", (W, H), base)
    d = ImageDraw.Draw(img)
    m = W * 0.06
    # embossed frame: light edge at the top left, dark at the bottom right
    d.rounded_rectangle([m, m, W - m, H - m], radius=H * 0.08, outline=(206, 208, 204, 255), width=int(S * 2.4))
    d.rounded_rectangle([m + S * 2, m + S * 2, W - m + S * 0.6, H - m + S * 0.6], radius=H * 0.08,
                        outline=(112, 114, 112, 255), width=int(S * 1.6))
    # empty line fields (thin dark lines where a number would be punched, left unfilled)
    for k in range(3):
        y = H * (0.36 + 0.20 * k)
        d.line([W * 0.22, y, W * 0.78, y], fill=(120, 122, 120, 255), width=int(S * 1.2))
    # rivets
    for x in (W * 0.11, W * 0.89):
        r = H * 0.11
        d.ellipse([x - r, H / 2 - r, x + r, H / 2 + r], fill=(132, 132, 128, 255))
        d.ellipse([x - r * 0.6, H / 2 - r * 0.8, x + r * 0.3, H / 2 - r * 0.1], fill=(196, 196, 190, 255))
    # dirt in the corners and fine scratches
    rnd = random.Random(79)
    stain = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(stain)
    for _ in range(20):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.05, 0.2) * H
        sd.ellipse([x - r, y - r, x + r, y + r], fill=rnd.randint(15, 50))
    stain = stain.filter(ImageFilter.GaussianBlur(H * 0.08))
    img = Image.composite(Image.new("RGBA", (W, H), (70, 64, 54, 255)), img, stain)
    for _ in range(14):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        L = rnd.uniform(0.05, 0.2) * W
        d2 = ImageDraw.Draw(img)
        d2.line([x, y, x + L, y + rnd.uniform(-0.1, 0.1) * L], fill=(200, 200, 196, 255), width=S)
    a = Image.new("L", (W, H), 0)
    ImageDraw.Draw(a).rounded_rectangle([0, 0, W - 1, H - 1], radius=H * 0.12, fill=255)
    img.putalpha(a)
    save(img, (w_mm * px_mm, h_mm * px_mm), name)


def make_tag(name, w_mm, h_mm, text, px_mm=8):
    """Inventory tag: aluminium, a ring hole on the left, punched digits (dark dents with a light lower
    edge), rubbed by fingers.
    """
    W, H = w_mm * px_mm * S, h_mm * px_mm * S
    img = Image.new("RGBA", (W, H), (160, 162, 160, 255))
    try:
        font = ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf", int(H * 0.46))
    except OSError:
        font = ImageFont.load_default()
    d = ImageDraw.Draw(img)
    tx, ty = W * 0.60, H * 0.52
    d.text((tx + S * 1.2, ty + S * 1.2), text, fill=(204, 204, 198, 255), font=font, anchor="mm")
    d.text((tx, ty), text, fill=(58, 58, 56, 255), font=font, anchor="mm")
    rnd = random.Random(80)
    stain = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(stain)
    for _ in range(16):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.08, 0.25) * H
        sd.ellipse([x - r, y - r, x + r, y + r], fill=rnd.randint(15, 45))
    stain = stain.filter(ImageFilter.GaussianBlur(H * 0.1))
    img = Image.composite(Image.new("RGBA", (W, H), (84, 78, 66, 255)), img, stain)
    a = Image.new("L", (W, H), 0)
    ad = ImageDraw.Draw(a)
    ad.rounded_rectangle([0, 0, W - 1, H - 1], radius=H * 0.18, fill=255)
    r = H * 0.12
    ad.ellipse([W * 0.12 - r, H / 2 - r, W * 0.12 + r, H / 2 + r], fill=0)
    img.putalpha(a)
    save(img, (w_mm * px_mm, h_mm * px_mm), name)


if __name__ == "__main__":
    make_trefoil("decal_trefoil.png", 34)
    make_plate("decal_plate.png", 40, 22)
    make_tag("decal_tag.png", 30, 16, "0417")
