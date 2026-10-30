"""Decals and pictures for the programmer (system Python + Pillow). No letters or brands: only slots, a
die in a window, scale and inventory number digits, a pictogram.

    python make_decals.py      -> ../work/decal_*.png

Sizes are the same as in build_m74.py (ZIF_L x ZIF_W, CHIP_*, SPARE_*, SCALE_D, INV_*, UV_*).
Orientation (as in kmats.decals): the u axis of the image is the model X from left to right, the v
axis is Y from bottom to top, i.e. the top of the image points to the back wall (+Y) when looking at
the top of the item from the front.

- decal_zif.png    - the top of a 40-pin lever socket (Textool 240-1280 and clones): two rows of 20
                     slots at a 2.54 mm pitch, the rows 15.24 mm apart; three screws on the axis; a
                     marker stroke across - where an inserted 24-pin IC ends (as in the reference photo).
- decal_chip.png   - the top of a K573RF5 in a white ceramic package: a round quartz window, the die
                     with bond wires under it, a key (notch) at pin 1. No markings.
- decal_label.png  - the top of a spare KS573RF4 (dark ceramic): the window is covered with a paper
                     slip - a programmed chip is protected from light this way; a pencil number on the slip.
- decal_scale.png  - the scale of the IC-type wafer switch: ticks and digits 1-5 in white transfer
                     paint around the knob.
- decal_inv.png    - an inventory number painted with a brush in white enamel on getinax.
- decal_screw.png  - a countersunk panel screw (flush with the getinax - a decal rather than a part).
- decal_uv.png     - a yellow triangle with an "optical radiation" pictogram (ISO 7010 W027 in
                     meaning: a circle with rays) on the eraser lid, without a caption.
"""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
FONT = r"C:\Windows\Fonts\arialbd.ttf"
S = 4                                   # supersampling

ZIF_L, ZIF_W = 0.064, 0.024
CHIP_L, CHIP_W = 0.0315, 0.0150         # K573RF5, DIP-24 (along X)
SPARE_L, SPARE_W = 0.0365, 0.0150       # KS573RF4, DIP-28 (along Y)
SCALE_D = 0.036
INV_W, INV_H = 0.024, 0.009
UV_W, UV_H = 0.030, 0.027


def canvas(w_m, h_m, ppm):
    """An empty canvas for a size in metres: ppm is pixels per mm (before supersampling)."""
    w, h = int(round(w_m * 1000 * ppm)), int(round(h_m * 1000 * ppm))
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img), (w, h), ppm * S


def save(img, size, name, blur=0.5):
    img = img.resize(size, Image.LANCZOS)
    if blur:
        img.putalpha(img.getchannel("A").filter(ImageFilter.GaussianBlur(blur)))
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def to_px(img, k, x_mm, y_mm):
    """A point in mm from the image centre (x to the right, y towards the back wall) -> pixels."""
    return img.width / 2 + x_mm * k, img.height / 2 - y_mm * k


def make_zif():
    img, d, size, k = canvas(ZIF_L, ZIF_W, 10)
    rng = random.Random(741)
    # shadow along the edge of the top plate
    d.rectangle([0, 0, img.width - 1, img.height - 1], outline=(10, 40, 32, 90), width=int(0.5 * k))
    # the middle bar is slightly lighter (smoother casting)
    x0, y0 = to_px(img, k, -27.0, 3.6)
    x1, y1 = to_px(img, k, 27.0, -3.6)
    d.rectangle([x0, y0, x1, y1], fill=(150, 220, 200, 40))
    for row in (-1, 1):
        for i in range(20):
            cx, cy = (i - 9.5) * 2.54, row * 7.62
            ax, ay = to_px(img, k, cx - 0.65, cy + 1.7)
            bx, by = to_px(img, k, cx + 0.65, cy - 1.7)
            d.rectangle([ax, ay, bx, by], fill=(12, 18, 16, 245))
            # highlight on the far edge of the slot - the contact inside
            d.rectangle([ax, ay, bx, ay + 0.35 * k], fill=(120, 110, 70, 160))
    for sx in (-28.6, 0.0, 28.6):
        cx, cy = to_px(img, k, sx, 0.0)
        r = 1.3 * k
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(176, 178, 176, 255), outline=(70, 72, 70, 255),
                  width=int(0.2 * k))
        a = rng.uniform(0, math.pi)
        for t in (a, a + math.pi / 2):
            d.line([(cx - 0.9 * k * math.cos(t), cy - 0.9 * k * math.sin(t)),
                    (cx + 0.9 * k * math.cos(t), cy + 0.9 * k * math.sin(t))], fill=(60, 60, 58, 255),
                   width=int(0.3 * k))
    # marker stroke across the bar: the boundary of the inserted IC (stepped, as in the photo)
    xm = -8.4
    pts = [(xm - 0.3, 3.2), (xm, 1.2), (xm + 1.4, 1.0), (xm + 1.6, -1.1), (xm + 0.2, -1.3), (xm + 0.1, -3.3)]
    d.line([to_px(img, k, x, y) for x, y in pts], fill=(48, 26, 70, 220), width=int(0.45 * k), joint="curve")
    save(img, size, "decal_zif.png")


def die(d, img, k, cx_mm, cy_mm, w_mm, h_mm, rng):
    """Die: a grey-violet rectangle, array blocks, bond pads and wires."""
    x0, y0 = to_px(img, k, cx_mm - w_mm / 2, cy_mm + h_mm / 2)
    x1, y1 = to_px(img, k, cx_mm + w_mm / 2, cy_mm - h_mm / 2)
    d.rectangle([x0, y0, x1, y1], fill=(112, 104, 122, 255))
    # the array is two halves, a fine grid
    for half in (-1, 1):
        bx0, bx1 = cx_mm + half * 0.15 * w_mm - 0.17 * w_mm, cx_mm + half * 0.15 * w_mm + 0.17 * w_mm
        ax, ay = to_px(img, k, bx0, cy_mm + 0.30 * h_mm)
        bx, by = to_px(img, k, bx1, cy_mm - 0.22 * h_mm)
        d.rectangle([ax, ay, bx, by], fill=(84, 92, 118, 255))
        for j in range(1, 9):
            yy = ay + (by - ay) * j / 9
            d.line([(ax, yy), (bx, yy)], fill=(130, 136, 160, 200), width=1)
    # decoder and periphery - a strip along the bottom
    ax, ay = to_px(img, k, cx_mm - 0.42 * w_mm, cy_mm - 0.28 * h_mm)
    bx, by = to_px(img, k, cx_mm + 0.42 * w_mm, cy_mm - 0.40 * h_mm)
    d.rectangle([ax, ay, bx, by], fill=(150, 128, 104, 255))
    # pads around the perimeter and wires to the window frame
    n = 12
    for i in range(n):
        t = (i + 0.5) / n
        for side in (-1, 1):
            px_, py_ = cx_mm - w_mm / 2 + t * w_mm, cy_mm + side * (h_mm / 2 - 0.15)
            ex, ey = px_ + (t - 0.5) * 1.2, cy_mm + side * (h_mm / 2 + 0.9 + rng.uniform(0.0, 0.2))
            a = to_px(img, k, px_, py_)
            b = to_px(img, k, ex, ey)
            d.rectangle([a[0] - 0.08 * k, a[1] - 0.08 * k, a[0] + 0.08 * k, a[1] + 0.08 * k], fill=(214, 188, 120, 255))
            d.line([a, b], fill=(222, 190, 110, 230), width=max(1, int(0.05 * k)))


def window(d, img, k, cx_mm, cy_mm, r_mm, rng):
    """Quartz window: dark glass in a light rim, the die, a highlight."""
    cx, cy = to_px(img, k, cx_mm, cy_mm)
    r = r_mm * k
    d.ellipse([cx - r - 0.35 * k, cy - r - 0.35 * k, cx + r + 0.35 * k, cy + r + 0.35 * k], fill=(120, 116, 104, 255))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(38, 42, 52, 255))
    die(d, img, k, cx_mm, cy_mm, 3.6, 3.0, rng)
    # highlight - a light arc across the glass
    d.arc([cx - 0.8 * r, cy - 0.8 * r, cx + 0.8 * r, cy + 0.8 * r], 200, 250, fill=(235, 240, 255, 120),
          width=int(0.35 * k))


def notch(d, img, k, cx_mm, cy_mm, r_mm, start, col):
    cx, cy = to_px(img, k, cx_mm, cy_mm)
    r = r_mm * k
    d.pieslice([cx - r, cy - r, cx + r, cy + r], start, start + 180, fill=col)


def make_chip():
    img, d, size, k = canvas(CHIP_L, CHIP_W, 20)
    rng = random.Random(742)
    window(d, img, k, 0.0, 0.0, 3.2, rng)
    notch(d, img, k, -CHIP_L * 500, 0.0, 0.9, 270, (90, 86, 76, 230))   # key notch on the -X end
    cx, cy = to_px(img, k, -CHIP_L * 500 + 2.6, -CHIP_W * 500 + 2.2)
    d.ellipse([cx - 0.5 * k, cy - 0.5 * k, cx + 0.5 * k, cy + 0.5 * k], fill=(150, 146, 134, 200))
    save(img, size, "decal_chip.png", blur=0.3)


def make_label():
    img, d, size, k = canvas(SPARE_W, SPARE_L, 20)
    rng = random.Random(743)
    notch(d, img, k, 0.0, SPARE_L * 500, 0.9, 0, (40, 38, 36, 230))      # notch on the +Y end
    # a paper slip over the window, stuck on slightly askew
    lab = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lab)
    cx, cy = to_px(img, k, 0.0, -1.0)
    w, h = 12.2 * k, 14.0 * k
    ld.rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], fill=(228, 220, 194, 255))
    # finger stains and yellowing - over the paper, not instead of it
    sm = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sm)
    for _ in range(18):
        x, y = cx + rng.uniform(-0.45, 0.45) * w, cy + rng.uniform(-0.45, 0.45) * h
        r = rng.uniform(0.4, 1.4) * k
        sd.ellipse([x - r, y - r, x + r, y + r], fill=(196, 180, 140, 60))
    lab = Image.alpha_composite(lab, sm.filter(ImageFilter.GaussianBlur(0.6 * k)))
    ld = ImageDraw.Draw(lab)
    # pencil number: 27 and a line under it
    font = ImageFont.truetype(FONT, int(5.6 * k))
    txt = Image.new("L", img.size, 0)
    ImageDraw.Draw(txt).text((cx, cy - 1.2 * k), "27", font=font, fill=255, anchor="mm")
    txt = txt.filter(ImageFilter.MinFilter(5))
    grain = Image.effect_noise(img.size, 60).point(lambda v: 255 if v > 110 else 0)
    txt = ImageChops.multiply(txt, grain)
    lab.paste(Image.new("RGBA", img.size, (84, 84, 92, 255)), (0, 0), txt.point(lambda v: int(v * 0.85)))
    ld.line([(cx - 3.4 * k, cy + 3.2 * k), (cx + 3.0 * k, cy + 3.0 * k)], fill=(90, 90, 98, 200), width=int(0.35 * k))
    lab = lab.rotate(4.0, resample=Image.BICUBIC, center=(cx, cy))
    img = Image.alpha_composite(img, lab)
    save(img, size, "decal_label.png", blur=0.3)


def make_scale():
    img, d, size, k = canvas(SCALE_D, SCALE_D, 12)
    rng = random.Random(744)
    col = (232, 228, 214, 255)
    font = ImageFont.truetype(FONT, int(3.0 * k))
    cx, cy = img.width / 2, img.height / 2
    for i in range(5):
        a = math.radians(150 - 30 * i)                       # 1 at the top left ... 5 at the top right
        ca, sa = math.cos(a), -math.sin(a)                   # PIL: y is down
        d.line([(cx + 10.2 * k * ca, cy + 10.2 * k * sa), (cx + 12.0 * k * ca, cy + 12.0 * k * sa)], fill=col,
               width=int(0.45 * k))
        d.text((cx + 14.6 * k * ca, cy + 14.6 * k * sa), str(i + 1), font=font, fill=col, anchor="mm")
    # wear: the paint has been worn off in places
    wear = Image.effect_noise(img.size, 90).point(lambda v: 0 if v > 180 + rng.randint(0, 20) else 255)
    a = img.getchannel("A")
    img.putalpha(ImageChops.multiply(a, wear))
    save(img, size, "decal_scale.png", blur=0.4)


def make_inv():
    img, d, size, k = canvas(INV_W, INV_H, 16)
    rng = random.Random(745)
    font = ImageFont.truetype(FONT, int(6.6 * k))
    txt = Image.new("L", img.size, 0)
    td = ImageDraw.Draw(txt)
    x = img.width * 0.12
    for ch in "2386":                                         # brush: the characters dance
        td.text((x, img.height / 2 + rng.uniform(-0.3, 0.3) * k), ch, font=font, fill=255, anchor="lm")
        x += 4.6 * k + rng.uniform(-0.2, 0.2) * k
    txt = txt.filter(ImageFilter.GaussianBlur(0.25 * k)).point(lambda v: 255 if v > 120 else 0)
    streak = Image.effect_noise(img.size, 70).filter(ImageFilter.BoxBlur(2)).point(lambda v: 255 if v > 96 else 140)
    txt = ImageChops.multiply(txt, streak)
    img.paste(Image.new("RGBA", img.size, (226, 222, 208, 255)), (0, 0), txt)
    save(img, size, "decal_inv.png", blur=0.3)


def make_screw():
    """Countersunk M3 screw with a straight slot: light steel, a dark socket edge, the slot."""
    img, d, size, k = canvas(0.0056, 0.0056, 20)
    w = img.width
    d.ellipse([0, 0, w - 1, w - 1], fill=(64, 52, 40, 230))
    m = 0.35 * k
    d.ellipse([m, m, w - 1 - m, w - 1 - m], fill=(168, 168, 164, 255))
    d.ellipse([2 * m, 2 * m, w - 1 - 2 * m, w - 1 - 2 * m], outline=(206, 206, 200, 255), width=int(0.2 * k))
    d.line([(0.18 * w, 0.62 * w), (0.82 * w, 0.38 * w)], fill=(40, 40, 40, 255), width=int(0.55 * k))
    save(img, size, "decal_screw.png", blur=0.3)


def make_uv():
    img, d, size, k = canvas(UV_W, UV_H, 12)
    rng = random.Random(746)
    w, h = img.width, img.height
    tri = [(w / 2, 0.02 * h), (0.02 * w, 0.98 * h), (0.98 * w, 0.98 * h)]
    d.polygon(tri, fill=(22, 20, 18, 255))
    inset = 0.11
    cxm, cym = w / 2, h * 0.66
    tri_in = [(cxm + (x - cxm) * (1 - inset * 1.6), cym + (y - cym) * (1 - inset * 1.6)) for x, y in tri]
    d.polygon(tri_in, fill=(232, 184, 26, 255))
    # pictogram: a circle with rays
    sx, sy, r = w / 2, h * 0.64, 0.11 * w
    d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(22, 20, 18, 255))
    for i in range(10):
        a = 2 * math.pi * i / 10 + math.pi / 2
        d.line([(sx + 1.45 * r * math.cos(a), sy + 1.45 * r * math.sin(a)),
                (sx + 2.15 * r * math.cos(a), sy + 2.15 * r * math.sin(a))], fill=(22, 20, 18, 255), width=int(0.6 * k))
    # scratches over the field
    for _ in range(10):
        x, y = rng.uniform(0.3, 0.7) * w, rng.uniform(0.45, 0.9) * h
        L = rng.uniform(0.05, 0.14) * w
        d.line([(x, y), (x + L, y + rng.uniform(-0.3, 0.3) * L)], fill=(244, 226, 170, 140), width=S)
    save(img, size, "decal_uv.png")


if __name__ == "__main__":
    make_zif()
    make_chip()
    make_label()
    make_scale()
    make_inv()
    make_uv()
    make_screw()
