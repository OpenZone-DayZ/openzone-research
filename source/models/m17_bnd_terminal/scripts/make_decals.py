"""M17 - window decals (system Python + Pillow), no inscriptions - only digits and symbols:
- a crack in the armoured glass from an impact - a star of rays and arcs, white lines on transparent
  (decal_crack.png);
- bullet marks on the face of the lower wall (decal_shots.png): paint knocked down to metal, dents,
  through holes, paint cracks around and rusty streaks running down (Bandits); the places are SHOTS, the
  image covers the whole wall;
- the exchange-rate board - own texture: "off" is dark glass with unlit segments (decal_board_off.png),
  "work" is frames decal_board_fNN.png: the top row is a sum, counted up, and blinks when it gets there;
  the bottom one is the rate; the pointer triangles are lit (the frames are stepped by the mod script,
  OZL_WorkFx frames). Frame 0 is the final sum: the "work" preview shows it.

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S, K = 1024, 3


def save(img, name, size=None):
    if size:
        img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def crack():
    rnd = random.Random(17)
    im = Image.new("L", (S * K, S * K), 0)
    d = ImageDraw.Draw(im)
    c = S * K / 2
    rays = []
    for i in range(11):
        a = 2 * math.pi * i / 11 + rnd.uniform(-0.2, 0.2)
        r_end = S * K * rnd.uniform(0.25, 0.48)
        pts, r, ang = [(c, c)], 0.0, a
        while r < r_end:
            r += S * K * rnd.uniform(0.02, 0.05)
            ang += rnd.uniform(-0.12, 0.12)
            pts.append((c + r * math.cos(ang), c + r * math.sin(ang)))
        d.line(pts, fill=255, width=int(K * rnd.uniform(1.5, 3.0)))
        rays.append(pts)
    # arcs between neighbouring rays - crack rings
    for ring in (0.25, 0.5, 0.8):
        for i in range(len(rays)):
            a, b = rays[i], rays[(i + 1) % len(rays)]
            ia, ib = int(len(a) * ring), int(len(b) * ring)
            if ia < len(a) and ib < len(b) and rnd.random() < 0.8:
                d.line([a[ia], b[ib]], fill=200, width=int(K * 1.5))
    # impact point - chipped out
    d.ellipse((c - 14 * K, c - 14 * K, c + 14 * K, c + 14 * K), fill=255)
    im = im.resize((S, S), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.5))
    rgba = Image.new("RGBA", (S, S), (235, 238, 240, 0))
    rgba.putalpha(im)
    save(rgba, "decal_crack.png")


# bullet marks: (x, z on the wall, m; through hole). The wall in the image: x -0.88..0.88, z 0.06..0.94
# (build_m17.SHOTS_DECAL); clear of the ribs at x -0.45 / 0 / 0.45 and the shelf brackets at +-0.70
SHOTS = [(-0.62, 0.58, True), (-0.54, 0.665, True), (-0.22, 0.34, False), (0.27, 0.71, True), (0.355, 0.625, False),
         (0.62, 0.27, True)]
WALL = (-0.88, 0.88, 0.06, 0.94)


def shots():
    W, Hh = 1536, 768
    k = 2
    im = Image.new("RGBA", (W * k, Hh * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    mm = W * k / ((WALL[1] - WALL[0]) * 1000.0)          # pixels per mm
    rnd = random.Random(1717)

    def px(x, z):
        return ((x - WALL[0]) / (WALL[1] - WALL[0]) * W * k, (WALL[3] - z) / (WALL[3] - WALL[2]) * Hh * k)
    # rust streaks - a separate layer, soft
    rust = Image.new("RGBA", im.size, (0, 0, 0, 0))
    rd = ImageDraw.Draw(rust)
    for x, z, hole in SHOTS:
        cx, cy = px(x, z)
        ln = rnd.uniform(60, 140) * mm
        w0 = rnd.uniform(5, 9) * mm
        steps = 24
        for i in range(steps):
            t = i / steps
            yy = cy + t * ln
            ww = w0 * (1 - 0.8 * t)
            xx = cx + math.sin(t * 5 + x * 9) * 1.5 * mm
            a = int((150 if hole else 90) * (1 - t) ** 1.3)
            rd.ellipse((xx - ww / 2, yy - ww / 2, xx + ww / 2, yy + ww / 2), fill=(112, 54, 24, a))
    rust = rust.filter(ImageFilter.GaussianBlur(2.0 * mm))
    im.alpha_composite(rust)
    for x, z, hole in SHOTS:
        cx, cy = px(x, z)
        R = rnd.uniform(15, 22) * mm
        # paint cracks as rays
        for _ in range(9):
            a = rnd.uniform(0, 2 * math.pi)
            r0, r1 = R * 0.8, R * rnd.uniform(1.3, 1.9)
            d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)),
                    (cx + r1 * math.cos(a + 0.12), cy + r1 * math.sin(a + 0.12))], fill=(92, 90, 84, 200), width=max(1, int(0.8 * mm)))
        # paint knocked down to metal - an uneven spot
        pts = []
        for i in range(18):
            a = 2 * math.pi * i / 18
            rr = R * rnd.uniform(0.75, 1.1)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=(132, 128, 120, 255))
        # dent: darker toward the middle
        for i in range(6):
            rr = R * (0.65 - i * 0.09)
            c = 112 - i * 12
            d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(c, c - 3, c - 8, 255))
        if hole:
            rh = rnd.uniform(4.0, 5.0) * mm
            d.ellipse((cx - rh * 1.35, cy - rh * 1.35, cx + rh * 1.35, cy + rh * 1.35), fill=(62, 58, 52, 255))
            d.ellipse((cx - rh, cy - rh, cx + rh, cy + rh), fill=(10, 9, 8, 255))
    im = im.resize((W, Hh), Image.LANCZOS)
    save(im, "decal_shots.png")


# --- board ------------------------------------------------------------------------------------
BW_, BH_ = 760, 320                      # board window 0.38 x 0.16 m: 2 pixels per mm
DIGITS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
          "7": "abc", "8": "abcdefg", "9": "abcdfg", " ": ""}
LIT, UNLIT = (255, 58, 30), (42, 13, 11)
# sum per frame: 0 - the final one (the preview shows it), 1 - blinked, 2..11 - being counted
SUMS = [1250, None, 0, 50, 125, 250, 400, 550, 700, 875, 1050, 1200]
RATE = " 420"                            # bottom row: rate 4.20 (the point after the second character)


def seg_polys(x, y, w, h, t, slant):
    """Segments of a digit in the rectangle (x, y) - (x + w, y + h): hexagons a-g, slanted right."""
    def hseg(x0, x1, yc):
        return [(x0, yc), (x0 + t / 2, yc - t / 2), (x1 - t / 2, yc - t / 2), (x1, yc), (x1 - t / 2, yc + t / 2),
                (x0 + t / 2, yc + t / 2)]

    def vseg(xc, y0, y1):
        return [(xc, y0), (xc + t / 2, y0 + t / 2), (xc + t / 2, y1 - t / 2), (xc, y1), (xc - t / 2, y1 - t / 2),
                (xc - t / 2, y0 + t / 2)]
    gap = t * 0.18
    xl, xr = x + t / 2, x + w - t / 2
    yt, ym, yb = y + t / 2, y + h / 2, y + h - t / 2
    polys = {"a": hseg(xl + gap, xr - gap, yt), "g": hseg(xl + gap, xr - gap, ym), "d": hseg(xl + gap, xr - gap, yb),
             "f": vseg(xl, yt + gap, ym - gap), "b": vseg(xr, yt + gap, ym - gap),
             "e": vseg(xl, ym + gap, yb - gap), "c": vseg(xr, ym + gap, yb - gap)}
    return {k: [(px + (ym - py) * slant, py) for px, py in v] for k, v in polys.items()}


def board(name, top, bottom, on, arrows):
    """top / bottom - rows of 4 characters (a space is unlit); None - the whole row is unlit; on - glowing."""
    k = 3
    W, Hh = BW_ * k, BH_ * k
    bg = (30, 9, 8) if on else (15, 6, 6)
    img = Image.new("RGBA", (W, Hh), bg + (255,))
    d = ImageDraw.Draw(img)
    for i in range(0, Hh, 4 * k):                       # LED raster - barely visible rows
        c = tuple(max(0, v - 3) for v in bg)
        d.line([(0, i), (W, i)], fill=c + (255,), width=k)
    lit_mask = Image.new("L", (W, Hh), 0)
    lm = ImageDraw.Draw(lit_mask)
    dw, dh, t, step = 64 * k, 112 * k, 13 * k, 84 * k
    x0 = (W - (3 * step + dw)) // 2 + 36 * k
    rows = [(top, 24 * k, False), (bottom, 184 * k, True)]
    for text, y, dp in rows:
        for i in range(4):
            ch = text[i] if text is not None else " "
            polys = seg_polys(x0 + i * step, y, dw, dh, t, 0.09)
            for s, poly in polys.items():
                lit = on and text is not None and s in DIGITS[ch]
                d.polygon(poly, fill=(LIT if lit else UNLIT) + (255,))
                if lit:
                    lm.polygon(poly, fill=255)
            if i == 1:                                     # decimal point after the second character
                cx, cy = x0 + i * step + dw + 6 * k, y + dh - t / 2
                lit = on and dp and text is not None
                d.ellipse((cx - t * 0.55, cy - t * 0.55, cx + t * 0.55, cy + t * 0.55), fill=(LIT if lit else UNLIT) + (255,))
                if lit:
                    lm.ellipse((cx - t * 0.55, cy - t * 0.55, cx + t * 0.55, cy + t * 0.55), fill=255)
    # pointers on the left: up at the top row, down at the bottom one
    ax = x0 - 70 * k
    for (yc, up), lit in zip(((24 * k + dh / 2, True), (184 * k + dh / 2, False)), arrows):
        s = 18 * k
        tri = [(ax - s, yc + s * 0.6), (ax + s, yc + s * 0.6), (ax, yc - s * 0.8)] if up else \
              [(ax - s, yc - s * 0.6), (ax + s, yc - s * 0.6), (ax, yc + s * 0.8)]
        on_ = on and lit
        d.polygon(tri, fill=(LIT if on_ else UNLIT) + (255,))
        if on_:
            lm.polygon(tri, fill=255)
    if on:
        # halo over the background and unlit segments, lit segments sharp over it
        glow = lit_mask.filter(ImageFilter.GaussianBlur(9 * k))
        layer = Image.new("RGBA", (W, Hh), LIT + (0,))
        layer.putalpha(glow.point(lambda v: int(v * 0.55)))
        out = img.copy()
        out.alpha_composite(layer)
        lit_only = img.copy()
        lit_only.putalpha(lit_mask)
        out.alpha_composite(lit_only)
        img = out
    # glint on the board glass at the top left
    hl = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    hd.polygon([(0, 0), (W * 0.42, 0), (W * 0.18, Hh), (0, Hh)], fill=(255, 255, 255, 10))
    img.alpha_composite(hl)
    save(img, name, (BW_, BH_))


def boards():
    board("decal_board_off.png", "8888", "8888", False, (False, False))
    for i, v in enumerate(SUMS):
        top = None if v is None else ("%4d" % v)
        board("decal_board_f%02d.png" % i, top, RATE, True, (2 <= i, True))


crack()
shots()
boards()
print("decals ->", WORK)
