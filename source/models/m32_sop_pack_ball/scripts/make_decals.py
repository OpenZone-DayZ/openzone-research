"""Decals of the SOP weapon cabinet (system Python + Pillow): the cabinet number stenciled in
white paint on the left door (digits with stencil bridges, soft edge, paint worn in patches)
and stencil stripes on the faces of the ammo crates (as on M23, other places and colors).
Digits only, no letters. Positions come from layout.py.

    python make_decals.py      -> ../work/decal_*.png
"""
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 2                                   # supersampling, then downscaled - smooth edges
WHITE = (214, 212, 200)

# Stencil digits on a 6 x 10 grid (unit = stroke width, 1/6 of the width): rectangles
# (x0, y0, x1, y1), y runs top to bottom; the stencil bridges are the gaps left between them
DIGITS = {
    "0": [(0, 1, 1.2, 4.6), (0, 5.4, 1.2, 9), (4.8, 1, 6, 4.6), (4.8, 5.4, 6, 9), (1, 0, 5, 1.2), (1, 8.8, 5, 10)],
    "1": [(2.4, 0, 3.8, 4.6), (2.4, 5.4, 3.8, 10), (1.2, 0.6, 2.3, 1.8)],
    "2": [(0.4, 0, 5, 1.2), (4.8, 1, 6, 4.4), (0.6, 4.2, 5.4, 5.4), (0, 5.6, 1.2, 8.8), (0, 8.8, 6, 10)],
    "3": [(0.2, 0, 5, 1.2), (4.8, 1, 6, 4.4), (1.6, 4.4, 5, 5.6), (4.8, 5.6, 6, 9), (0.2, 8.8, 5, 10)],
    "4": [(0, 0, 1.2, 5.6), (0, 5.6, 4.2, 6.8), (3.6, 0, 4.8, 5.3), (3.6, 7.0, 4.8, 10)],
    "5": [(0.4, 0, 6, 1.2), (0, 0.6, 1.2, 4.4), (0.4, 4.2, 5, 5.4), (4.8, 5.6, 6, 9), (0, 8.8, 5, 10)],
    "7": [(0, 0, 4.6, 1.2), (4.8, 0, 6, 2.6), (3.6, 3.2, 4.8, 6.2), (2.6, 6.8, 3.8, 10)],
}


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, size)


def worn_mask(W, H, rnd, n, rmin, rmax, blur):
    """Worn-paint patches: 255 - paint intact, 0 - worn off."""
    m = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(m)
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        r = rnd.uniform(rmin, rmax)
        d.ellipse((x - r, y - r * rnd.uniform(0.3, 1.0), x + r, y + r * rnd.uniform(0.3, 1.0)), fill=0)
    return m.filter(ImageFilter.GaussianBlur(blur))


def make_number():
    """Door number: two stenciled digits, brushed paint - soft edge, worn in places."""
    k = 1400 * S
    W, H = int(L.NUM["w"] * k), int(L.NUM["h"] * k)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    n = len(L.NUM["text"])
    cell_h = H * 0.86
    u = cell_h / 10.0
    cell_w = 6 * u
    gap = 1.6 * u
    x = (W - (n * cell_w + (n - 1) * gap)) / 2
    y = (H - cell_h) / 2
    for ch in L.NUM["text"]:
        for a, b, c, e in DIGITS[ch]:
            d.rectangle((x + a * u, y + b * u, x + c * u, y + e * u), fill=235)
        x += cell_w + gap
    rnd = random.Random(32)
    m = m.filter(ImageFilter.GaussianBlur(1.0 * S))
    m = ImageChops.multiply(m, worn_mask(W, H, rnd, 70, 1.5 * S, 7 * S, 1.2 * S).point(lambda v: 70 + v * 185 // 255))
    img = Image.new("RGBA", (W, H), WHITE + (0,))
    img.putalpha(m)
    save(img, (W // S, H // S), "decal_number.png")


def make_stencil():
    """Crate face: stencil stripes in spray paint - overspray at the edge, specks around."""
    cx0, cx1, _, _, _, h = L.CRATES[0]
    k = 1600 * S
    W, H = int((cx1 - cx0) * k), int(h * k)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rnd = random.Random(17)
    za, zb = L.STRIPE_Z
    for a, b, c in L.STRIPES:
        col = (24, 24, 22) if c == "black" else (150, 32, 26)
        m = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(m)
        d.rectangle((a * k, (h - zb) * k, b * k, (h - za) * k), fill=235)
        for _ in range(240):
            x = rnd.uniform(a - 0.008, b + 0.008) * k
            y = rnd.uniform(h - zb - 0.008, h - za + 0.008) * k
            r = rnd.uniform(0.4, 1.4) * S
            d.ellipse((x - r, y - r, x + r, y + r), fill=rnd.randint(60, 180))
        m = m.filter(ImageFilter.GaussianBlur(1.5 * S))
        m = ImageChops.multiply(m, worn_mask(W, H, rnd, 40, 2 * S, 9 * S, 1.5 * S).point(lambda v: 60 + v * 195 // 255))
        layer = Image.new("RGBA", (W, H), col + (0,))
        layer.putalpha(m)
        img = Image.alpha_composite(img, layer)
    save(img, (W // S, H // S), "decal_stencil.png")


if __name__ == "__main__":
    make_number()
    make_stencil()
