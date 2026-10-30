"""Decals of the gunsmith's workbench (system Python + Pillow): white silhouettes of the own tools on
the board (under each tool, slightly wider than it; none under the vanilla ones, whose shapes are
unknown) and stencil stripes on the face of the ammo crates (two black and a red one, sprayed edges,
the paint worn off in places). No letters or digits. The layout is in layout.py.

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
S = 2                                   # supersampling, then downscaling - smooth edges
PX_M = 1200
WHITE = (222, 220, 210)


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, size)


def worn_mask(W, H, rnd, n, rmin, rmax, blur):
    """Worn paint spots: 255 - paint intact, 0 - worn off."""
    m = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(m)
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        r = rnd.uniform(rmin, rmax)
        d.ellipse((x - r, y - r * rnd.uniform(0.3, 1.0), x + r, y + r * rnd.uniform(0.3, 1.0)), fill=0)
    return m.filter(ImageFilter.GaussianBlur(blur))


def make_board():
    x0, x1, z0, z1 = L.BOARD
    k = PX_M * S
    W, H = int((x1 - x0) * k), int((z1 - z0) * k)

    def px(x, z):
        return ((x - x0) * k, (z1 - z) * k)
    sil = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(sil)
    for kind, x, z, p in L.TOOLS:
        for sh in L.shapes(kind, x, z, p):
            if sh[0] == "rect":
                (a, b), (c, e) = px(sh[1], sh[4]), px(sh[2], sh[3])
                d.rectangle((a, b, c, e), fill=255)
            elif sh[0] == "circle":
                cx, cz = px(sh[1], sh[2])
                r = sh[3] * k
                d.ellipse((cx - r, cz - r, cx + r, cz + r), fill=255)
            else:
                d.polygon([px(*q) for q in sh[1]], fill=255)
    # the silhouette is ~4 mm wider than the tool: a white rim shows around the hanging tool
    grow = int(0.004 * k) * 2 + 1
    sil = sil.filter(ImageFilter.MaxFilter(grow))
    rnd = random.Random(23)
    # a stencil brush: the edge is slightly soft, the paint is worn off in places by hands
    sil = sil.filter(ImageFilter.GaussianBlur(1.2 * S))
    wear = worn_mask(W, H, rnd, 140, 2 * S, 8 * S, 1.5 * S)
    alpha = ImageChops.multiply(sil, wear.point(lambda v: 90 + v * 165 // 255))
    img = Image.new("RGBA", (W, H), WHITE + (0,))
    img.putalpha(alpha)
    save(img, (W // S, H // S), "decal_board.png")


def make_stencil():
    """Crate face: stencil stripes sprayed from a can - an edge with overspray, dots around."""
    cx0, cx1, _, _, _, h = L.CRATES[0]
    k = 1600 * S
    W, H = int((cx1 - cx0) * k), int(h * k)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rnd = random.Random(7)
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
    make_board()
    make_stencil()
