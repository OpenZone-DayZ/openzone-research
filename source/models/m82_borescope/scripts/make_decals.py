"""Decals of the borescope (system Python + Pillow):
- the reminder in the case lid - a laminated card without text: at the top a dark strip with an
  eye pictogram, in the middle a diagram - the borescope with an illuminator inserted into a
  barrel, the eye at the eyepiece, a magnifier callout with the rifling of the bore; at the bottom
  three pictograms (batteries, a cotton swab, "do not bend" - a bent probe crossed out) and grey
  bars in place of lines;
- a cotton swab pack (in the case lid): a transparent pack, swabs with white heads on dark sticks,
  a welded seam with teeth along the edge;
- an inventory number in white brush paint on the case face - digits only, the paint worn.

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
INK = (34, 38, 46, 255)
NAVY = (36, 50, 82, 255)
CARD = (234, 230, 216, 255)
FONT = r"C:\Windows\Fonts\arialbd.ttf"  # a zero without a slash, like brush-painted digits


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def stains(img, seed, n, rmin, rmax, col, amax, blur):
    """Dirt stains: n soft spots of colour col, opacity up to amax."""
    W, H = img.size
    rnd = random.Random(seed)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    for _ in range(n):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(rmin, rmax) * min(W, H)
        d.ellipse([x - r, y - r, x + r, y + r], fill=rnd.randint(int(amax * 0.3), amax))
    m = m.filter(ImageFilter.GaussianBlur(blur * min(W, H)))
    return Image.composite(Image.new("RGBA", (W, H), col), img, m)


def eye(d, cx, cy, w, col, bg, lw):
    """Eye pictogram: an almond of two arcs (outline), an iris, a highlight."""
    h = w * 0.30

    def almond(s):
        up = [(cx + w * s * (t / 16 - 0.5), cy - h * s * math.sin(math.pi * t / 16)) for t in range(17)]
        dn = [(cx + w * s * (0.5 - t / 16), cy + h * s * math.sin(math.pi * t / 16)) for t in range(17)]
        return up + dn
    d.polygon(almond(1.0), fill=col)
    d.polygon(almond(0.78), fill=bg)
    r = h * 0.80
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    r2 = h * 0.26
    d.ellipse([cx + r * 0.15 - r2, cy - r * 0.35 - r2, cx + r * 0.15 + r2, cy - r * 0.35 + r2], fill=bg)


def make_card(name, w_mm, h_mm, px_mm=8):
    """Reminder in the lid: a diagram without words. The card is laminated - rounded corners, a
    transparent film edge along the border (slightly lighter), thumbed by fingers.
    """
    k = px_mm * S
    W, H = w_mm * k, h_mm * k
    img = Image.new("RGBA", (W, H), CARD)
    d = ImageDraw.Draw(img)
    lw = int(0.35 * k)
    # film edge and frame
    d.rounded_rectangle([1.2 * k, 1.2 * k, W - 1.2 * k, H - 1.2 * k], radius=2.0 * k, outline=INK, width=lw)
    # top strip with an eye
    d.rectangle([1.2 * k, 1.2 * k, W - 1.2 * k, 9.0 * k], fill=NAVY)
    eye(d, 7.0 * k, 5.1 * k, 7.5 * k, CARD, NAVY, lw)
    for i in range(3):                                    # three "steps" - dots, no words
        cx = W - (8.0 + 5.0 * i) * k
        d.ellipse([cx - 1.1 * k, 5.1 * k - 1.1 * k, cx + 1.1 * k, 5.1 * k + 1.1 * k], fill=CARD)
    # barrel: two generatrices, rifling as slanted strokes, the muzzle cut at the right
    y0, y1 = 25.0 * k, 33.0 * k
    xb0, xb1 = 34.0 * k, W - 6.0 * k
    d.rectangle([xb0, y0 - 2.4 * k, xb1, y0], fill=INK)
    d.rectangle([xb0, y1, xb1, y1 + 2.4 * k], fill=INK)
    x = xb0 + 1.5 * k
    while x < xb1 - 1.0 * k:
        d.line([x, y0, x + 2.2 * k, y0 + 1.6 * k], fill=INK, width=int(0.25 * k))
        d.line([x + 2.2 * k, y1 - 1.6 * k, x, y1], fill=INK, width=int(0.25 * k))
        x += 3.0 * k
    # borescope: eyepiece, body, the probe goes into the barrel
    yc = (y0 + y1) / 2
    d.rectangle([13.0 * k, yc - 4.2 * k, 15.0 * k, yc + 4.2 * k], fill=INK)            # eyecup
    d.rectangle([15.0 * k, yc - 3.4 * k, 22.0 * k, yc + 3.4 * k], fill=INK)            # eyepiece
    d.rectangle([22.0 * k, yc - 2.6 * k, 28.0 * k, yc + 2.6 * k], outline=INK, width=lw, fill=CARD)
    d.polygon([(28.0 * k, yc - 2.6 * k), (30.5 * k, yc - 0.8 * k), (30.5 * k, yc + 0.8 * k),
               (28.0 * k, yc + 2.6 * k)], fill=INK)
    d.rectangle([30.5 * k, yc - 0.7 * k, 70.0 * k, yc + 0.7 * k], fill=INK)            # probe
    # illuminator down from the body: a fitting, a handle with knurling
    d.rectangle([24.4 * k, yc + 2.6 * k, 25.6 * k, yc + 5.0 * k], fill=INK)
    d.rounded_rectangle([23.0 * k, yc + 5.0 * k, 27.0 * k, H - 22.0 * k], radius=0.8 * k, outline=INK,
                        width=lw, fill=CARD)
    yy = yc + 7.0 * k
    while yy < H - 23.0 * k:
        d.line([23.6 * k, yy, 26.4 * k, yy + 0.9 * k], fill=INK, width=int(0.2 * k))
        yy += 1.3 * k
    # eye at the eyepiece and the insertion arrow
    eye(d, 7.5 * k, yc, 6.0 * k, INK, CARD, lw)
    d.line([36.0 * k, 18.0 * k, 52.0 * k, 18.0 * k], fill=INK, width=lw)
    d.polygon([(52.0 * k, 16.6 * k), (55.0 * k, 18.0 * k), (52.0 * k, 19.4 * k)], fill=INK)
    # callout magnifier: from the probe end to a circle with the bore rifling
    cx, cy, r = W - 14.0 * k, 16.5 * k, 6.8 * k
    for t in range(0, 10, 2):                             # dashed line
        a0 = (70.0 * k + (cx - r * 0.7 - 70.0 * k) * t / 10, yc - 1.0 * k + (cy + r * 0.7 - yc + 1.0 * k) * t / 10)
        a1 = (70.0 * k + (cx - r * 0.7 - 70.0 * k) * (t + 1) / 10,
              yc - 1.0 * k + (cy + r * 0.7 - yc + 1.0 * k) * (t + 1) / 10)
        d.line([a0, a1], fill=INK, width=int(0.25 * k))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CARD, outline=INK, width=lw)
    ri = r * 0.62
    d.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], outline=INK, width=int(0.25 * k))
    for i in range(6):                                    # rifling lands
        a = math.radians(60 * i + 15)
        p0 = (cx + ri * math.cos(a), cy + ri * math.sin(a))
        p1 = (cx + r * 0.9 * math.cos(a + 0.25), cy + r * 0.9 * math.sin(a + 0.25))
        d.line([p0, p1], fill=INK, width=int(0.35 * k))
    d.ellipse([cx - 0.9 * k, cy - 0.9 * k, cx + 0.9 * k, cy + 0.9 * k], fill=INK)
    # bottom row: three pictograms in frames, grey bars of lines
    by0, by1 = H - 17.0 * k, H - 5.0 * k
    for i in range(3):
        bx0 = 4.0 * k + i * 14.0 * k
        d.rounded_rectangle([bx0, by0, bx0 + 12.0 * k, by1], radius=1.2 * k, outline=INK, width=lw)
        mx, my = bx0 + 6.0 * k, (by0 + by1) / 2
        if i == 0:                                        # two batteries
            for dx in (-2.0, 2.0):
                d.rectangle([mx + (dx - 1.3) * k, my - 3.4 * k, mx + (dx + 1.3) * k, my + 4.0 * k], fill=INK)
                d.rectangle([mx + (dx - 0.6) * k, my - 4.4 * k, mx + (dx + 0.6) * k, my - 3.4 * k], fill=INK)
        elif i == 1:                                      # cotton swab
            d.line([mx - 4.0 * k, my + 3.0 * k, mx + 4.0 * k, my - 3.0 * k], fill=INK, width=int(0.4 * k))
            for sx in (-1, 1):
                ex, ey = mx + sx * 4.2 * k, my - sx * 3.2 * k
                d.ellipse([ex - 1.4 * k, ey - 1.0 * k, ex + 1.4 * k, ey + 1.0 * k], fill=CARD, outline=INK,
                          width=int(0.3 * k))
        else:                                             # bent probe crossed out
            d.line([(mx - 4.2 * k, my - 2.0 * k), (mx - 0.5 * k, my - 0.6 * k), (mx + 1.8 * k, my + 1.2 * k),
                    (mx + 3.0 * k, my + 4.2 * k)], fill=INK, width=int(0.6 * k), joint="curve")
            d.line([mx - 4.5 * k, my - 4.5 * k, mx + 4.5 * k, my + 4.5 * k], fill=(168, 40, 34, 255), width=lw)
            d.line([mx - 4.5 * k, my + 4.5 * k, mx + 4.5 * k, my - 4.5 * k], fill=(168, 40, 34, 255), width=lw)
    rnd = random.Random(82)
    for j in range(4):                                    # lines are grey bars, not text
        y = by0 + 1.4 * k + j * 2.9 * k
        L = rnd.uniform(0.55, 1.0) * (W - 51.0 * k)
        d.rectangle([47.0 * k, y, 47.0 * k + L, y + 1.1 * k], fill=(150, 150, 146, 255))
    # dirt and thumbed corners
    img = stains(img, 83, 24, 0.03, 0.12, (120, 108, 86, 255), 55, 0.04)
    rnd = random.Random(84)
    m = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(m)
    for cx, cy in ((W * 0.03, H * 0.95), (W * 0.97, H * 0.94), (W * 0.96, H * 0.06)):
        for _ in range(6):
            x, y, r = cx + rnd.uniform(-1, 1) * 4 * k, cy + rnd.uniform(-1, 1) * 4 * k, rnd.uniform(2, 5) * k
            md.ellipse([x - r, y - r, x + r, y + r], fill=rnd.randint(30, 70))
    m = m.filter(ImageFilter.GaussianBlur(2.0 * k))
    img = Image.composite(Image.new("RGBA", (W, H), (96, 86, 70, 255)), img, m)
    a = Image.new("L", (W, H), 0)
    ImageDraw.Draw(a).rounded_rectangle([0, 0, W - 1, H - 1], radius=2.4 * k, fill=255)
    img.putalpha(a)
    save(img, (w_mm * px_mm, h_mm * px_mm), name)


def make_swabs(name, w_mm, h_mm, n=7, px_mm=8):
    """Cotton swab pack: transparent film over blue foam - the bluish tone shows through it; swabs lie
    across, dark sticks, white heads on both sides; a welded seam with teeth on the right; highlights
    of the film folds.
    """
    k = px_mm * S
    W, H = w_mm * k, h_mm * k
    img = Image.new("RGBA", (W, H), (146, 168, 190, 255))
    d = ImageDraw.Draw(img)
    seam = W - 6.0 * k
    pitch = (H - 6.0 * k) / n
    for i in range(n):
        y = 3.0 * k + pitch * (i + 0.5)
        x0, x1 = 3.0 * k, seam - 3.0 * k
        d.rectangle([x0 + 4.0 * k, y - 0.55 * k, x1 - 4.0 * k, y + 0.55 * k], fill=(30, 30, 33, 255))
        for ex in (x0 + 2.2 * k, x1 - 2.2 * k):
            d.ellipse([ex - 3.0 * k, y - 1.7 * k, ex + 3.0 * k, y + 1.7 * k], fill=(238, 236, 228, 255))
            d.ellipse([ex - 2.0 * k, y - 1.2 * k, ex + 0.6 * k, y - 0.2 * k], fill=(250, 250, 246, 255))
    # welded seam: a strip with teeth along the edge
    d.rectangle([seam, 0, W, H], fill=(196, 206, 214, 255))
    for j in range(int(H / (1.6 * k)) + 1):
        y = j * 1.6 * k
        d.polygon([(W, y), (W - 1.2 * k, y + 0.8 * k), (W, y + 1.6 * k)], fill=(120, 140, 160, 255))
        d.line([seam + 1.0 * k, y, seam + 4.0 * k, y], fill=(176, 188, 198, 255), width=int(0.3 * k))
    # highlights of the film folds
    rnd = random.Random(85)
    hl = Image.new("L", (W, H), 0)
    hd = ImageDraw.Draw(hl)
    for _ in range(7):
        x = rnd.uniform(0.05, 0.85) * W
        hd.line([x, 0, x + rnd.uniform(-0.1, 0.1) * W, H], fill=rnd.randint(40, 90), width=int(rnd.uniform(1, 3) * k))
    hl = hl.filter(ImageFilter.GaussianBlur(1.2 * k))
    img = Image.composite(Image.new("RGBA", (W, H), (236, 242, 246, 255)), img, hl)
    img = stains(img, 86, 10, 0.05, 0.15, (110, 104, 92, 255), 40, 0.05)
    a = Image.new("L", (W, H), 0)
    ImageDraw.Draw(a).rounded_rectangle([0, 0, W - 1, H - 1], radius=1.5 * k, fill=255)
    img.putalpha(a)
    save(img, (w_mm * px_mm, h_mm * px_mm), name)


def make_number(name, w_mm, h_mm, text, px_mm=12):
    """Inventory number in white enamel by brush: an uneven edge, the paint worn along the digit edges."""
    k = px_mm * S
    W, H = w_mm * k, h_mm * k
    img = Image.new("RGBA", (W, H), (226, 224, 214, 255))
    txt = Image.new("L", (W, H), 0)
    font = ImageFont.truetype(FONT, int(H * 0.92))
    rnd = random.Random(87)
    td = ImageDraw.Draw(txt)
    x = W * 0.03
    for ch in text:
        td.text((x, H / 2 + rnd.uniform(-0.04, 0.04) * H), ch, font=font, fill=255, anchor="lm")
        x += W * 0.245
    txt = txt.filter(ImageFilter.GaussianBlur(0.12 * k))
    # wear: patches over the field
    wear = Image.new("L", (W, H), 255)
    wd = ImageDraw.Draw(wear)
    for _ in range(40):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.04, 0.12) * H
        wd.ellipse([x - r, y - r, x + r, y + r], fill=rnd.randint(0, 120))
    wear = wear.filter(ImageFilter.GaussianBlur(0.4 * k))
    a = ImageChops.multiply(txt, wear).point(lambda v: 255 if v > 120 else int(v * 1.6))
    img.putalpha(a)
    save(img, (w_mm * px_mm, h_mm * px_mm), name)


if __name__ == "__main__":
    make_card("decal_card.png", 90, 62)
    make_swabs("decal_swabs.png", 76, 30)
    make_number("decal_inv.png", 24, 8, "5109")
