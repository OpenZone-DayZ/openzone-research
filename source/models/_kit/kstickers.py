"""Stickers of the Freedom faction, shared by its models (system Python + Pillow, no Blender).

Freedom gets a peace sign and a cannabis leaf with the caption LEGALIZE (short English words are
allowed on Freedom stickers). The drawing functions work like the st_* ones in make_decals.py of
the m27-m31 models: (width, height in pixels) -> RGB / RGBA; wear, fading and the peeled corner
are added by sticker() of make_decals itself. Hooking into make_decals.py:

    sys.path.insert(0, <source/models/_kit>)
    import kstickers
    KINDS.update(kstickers.kinds())

Add new kinds at the END of the face() lists: random.Random(seed) is consumed in order, so the
existing stickers stay where they were (checked by comparing PNGs before and after).
"""
import math

from PIL import Image, ImageDraw, ImageFont

import ksettings

FONTS = ksettings.FONTS
BLACK, WHITE = (22, 22, 22), (238, 236, 226)
GREEN, LEAF, CREAM = (60, 170, 60), (46, 128, 40), (232, 226, 204)


def _font(name, h):
    return ImageFont.truetype(FONTS + name, max(8, int(h)))


def _text_fit(d, box, s, fname, fill):
    x0, y0, x1, y1 = box
    f = _font(fname, y1 - y0)
    while True:
        l, t, r, b = d.textbbox((0, 0), s, font=f)
        if ((r - l) <= (x1 - x0) and (b - t) <= (y1 - y0)) or f.size <= 8:
            break
        f = _font(fname, f.size * 0.93)
    l, t, r, b = d.textbbox((0, 0), s, font=f)
    d.text(((x0 + x1 - (r - l)) / 2 - l, (y0 + y1 - (b - t)) / 2 - t), s, font=f, fill=fill)


def peace(d, cx, cy, r, fill, width):
    """Peace sign: a ring, a vertical bar through the center, two branches going down at 45 degrees."""
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=fill, width=width)
    ri = r - width / 2
    d.line([(cx, cy - ri), (cx, cy + ri)], fill=fill, width=width)
    for s in (-1, 1):
        a = math.radians(45)
        d.line([(cx, cy), (cx + s * ri * math.sin(a), cy + ri * math.cos(a))], fill=fill, width=width)


def leaf(d, cx, cy, size, fill):
    """Cannabis leaf: seven serrated lobes fanning up from the base point (cx, cy); size is the
    length of the middle lobe. Lobe angles are 0, +-28, +-56, +-86 degrees, lengths 1 / 0.86 / 0.64 / 0.38."""
    for ang, ln in ((86, 0.38), (-86, 0.38), (56, 0.64), (-56, 0.64), (28, 0.86), (-28, 0.86), (0, 1.0)):
        a = math.radians(ang)
        ux, uy = math.sin(a), -math.cos(a)          # along the lobe (up at 0)
        vx, vy = -uy, ux                            # across the lobe
        L = size * ln
        wmax = size * 0.11 * (0.75 + 0.25 * ln)
        n, teeth = 40, 9
        left, right = [], []
        for i in range(n + 1):
            t = i / n
            w = wmax * math.sin(math.pi * min(1.0, t * 1.05) ** 0.85)
            saw = (t * teeth) % 1.0                 # teeth slanted toward the tip
            w *= 0.82 + 0.30 * saw
            px, py = cx + ux * L * t, cy + uy * L * t
            left.append((px + vx * w, py + vy * w))
            right.append((px - vx * w, py - vy * w))
        d.polygon(left + right[::-1], fill=fill)
    d.line([(cx, cy), (cx, cy + size * 0.22)], fill=fill, width=max(2, int(size * 0.045)))


def st_peace(w, h):
    """Round sticker: a black disc, a white peace sign, a green rim."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, w - 1, h - 1), fill=GREEN)
    m = w * 0.06
    d.ellipse((m, m, w - 1 - m, h - 1 - m), fill=BLACK)
    peace(d, w / 2, h / 2, w * 0.34, WHITE, max(2, int(w * 0.075)))
    return im


def st_legalize(w, h):
    """Rectangular cream sticker: a green leaf on the left, LEGALIZE on the right."""
    im = Image.new("RGB", (w, h), CREAM)
    d = ImageDraw.Draw(im)
    b = max(2, int(h * 0.06))
    d.rectangle((b, b, w - 1 - b, h - 1 - b), outline=LEAF, width=max(2, int(h * 0.04)))
    leaf(d, h * 0.56, h * 0.74, h * 0.56, LEAF)
    _text_fit(d, (h * 1.0, h * 0.17, w - h * 0.10, h * 0.83), "LEGALIZE", "impact.ttf", BLACK)
    return im


def st_leaf(w, h):
    """Round sticker without words: a green leaf on yellow."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, w - 1, h - 1), fill=(236, 196, 30))
    leaf(d, w / 2, h * 0.70, h * 0.50, LEAF)
    return im


def kinds():
    """Kinds for KINDS of make_decals.py: kind -> (drawing function, width, height in meters, shape)."""
    return {
        "peace": (st_peace, 0.060, 0.060, "shape"),
        "legalize": (st_legalize, 0.125, 0.052, "rect"),
        "leaf": (st_leaf, 0.055, 0.055, "shape"),
    }


if __name__ == "__main__":
    import os
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "kstickers_sheet.png"
    K = 2800
    tiles = [fn(int(wm * K), int(hm * K)).convert("RGBA") for fn, wm, hm, _ in kinds().values()]
    W = sum(t.width for t in tiles) + 40 * (len(tiles) + 1)
    H = max(t.height for t in tiles) + 80
    sheet = Image.new("RGBA", (W, H), (120, 124, 120, 255))
    x = 40
    for t in tiles:
        sheet.alpha_composite(t, (x, 40))
        x += t.width + 40
    sheet.save(out)
    print("wrote", os.path.abspath(out), sheet.size)
