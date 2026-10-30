"""Scales, regulator dial, sign and stencil of the M35 SOP muffle furnace (system Python +
Pillow). Digits only, no letters: the digits of the scales and the dial, the inventory
number by stencil, a "hot surface" sign. The stencil digits come from M32/M33 (make_decals.py
of m33_sop_proc_ball). Positions are in layout.py.

    python make_decals.py      -> ../work/decal_*.png

- decal_meter_t.png    scale of the pyrometric millivoltmeter (window 120 x 90): 0-1200
                       degrees every 200, red zone from 1000, mirror strip; the needle is
                       a separate part (ozl_needle);
- decal_meter_a.png    scale of the heater ammeter (window 66 x 56): 0-30, red zone from 25
                       (ozl_needle_2);
- decal_dial.png       power regulator dial on the furnace side: black ring, ticks and digits
                       0-10 along a 270 degree arc (as on the MP-2U);
- decal_heat.png       "hot surface" sign: yellow triangle, black border, heat waves;
- decal_stencil.png    inventory number in white paint by stencil on the cabinet door.
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 2
PX_M = 1400
K = PX_M * S
K2 = K * 2
FONTS = "C:/Windows/Fonts/"
WHITE = (214, 212, 200)
BLACK = (22, 22, 22)
RED = (180, 34, 28)
FACE = (230, 228, 216)

DIGITS = {
    "0": [(0, 1, 1.2, 4.6), (0, 5.4, 1.2, 9), (4.8, 1, 6, 4.6), (4.8, 5.4, 6, 9), (1, 0, 5, 1.2), (1, 8.8, 5, 10)],
    "1": [(2.4, 0, 3.8, 4.6), (2.4, 5.4, 3.8, 10), (1.2, 0.6, 2.3, 1.8)],
    "4": [(0, 0, 1.2, 5.6), (0, 5.6, 4.2, 6.8), (3.6, 0, 4.8, 5.3), (3.6, 7.0, 4.8, 10)],
    "7": [(0, 0, 4.6, 1.2), (4.8, 0, 6, 2.6), (3.6, 3.2, 4.8, 6.2), (2.6, 6.8, 3.8, 10)],
}


def font(name, h):
    return ImageFont.truetype(FONTS + name, max(8, int(h)))


def save(img, name):
    img = img.resize((img.width // S, img.height // S), Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, img.size)


def worn_mask(W, H, rnd, n, rmin, rmax, blur):
    m = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(m)
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        r = rnd.uniform(rmin, rmax)
        d.ellipse((x - r, y - r * rnd.uniform(0.3, 1.0), x + r, y + r * rnd.uniform(0.3, 1.0)), fill=0)
    return m.filter(ImageFilter.GaussianBlur(blur))


def centered(d, x, y, s, f, fill):
    l, t, r, b = d.textbbox((0, 0), s, font=f)
    d.text((x - (r - l) / 2 - l, y - (b - t) / 2 - t), s, font=f, fill=fill)


# =============================================================================
# Scales of the panel meters
# =============================================================================
SCALES = {
    # look: (scale end, minor ticks, labels every, red zone from, mirror strip)
    "t": (1200, 60, 400, 1000, True),
    "a": (30, 30, 10, 25, False),
}


def make_meter(m):
    top, n, lab, red, mirror = SCALES[m["scale"]]
    W, H = int(m["w"] * K2), int(m["h"] * K2)
    img = Image.new("RGBA", (W, H), FACE + (255,))
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, H - L.PIVOT_K * H
    R = L.NEEDLE_K * H * 0.93
    half = math.radians(L.ARC_DEG / 2)

    def pt(t, r):
        a = -half + 2 * half * t
        return cx + r * math.sin(a), cy - r * math.cos(a)
    if mirror:
        for i in range(60):
            t0, t1 = i / 60, (i + 1) / 60
            d.polygon([pt(t0, R * 0.80), pt(t1, R * 0.80), pt(t1, R * 0.86), pt(t0, R * 0.86)], fill=(150, 156, 160))
    k0 = red / top
    for i in range(20):
        t0, t1 = k0 + (1 - k0) * i / 20, k0 + (1 - k0) * (i + 1) / 20
        d.polygon([pt(t0, R * 0.93), pt(t1, R * 0.93), pt(t1, R * 1.0), pt(t0, R * 1.0)], fill=RED)
    d.arc((cx - R, cy - R, cx + R, cy + R), 270 - L.ARC_DEG / 2, 270 + L.ARC_DEG / 2, fill=BLACK, width=max(2, S))
    for i in range(n + 1):
        v = top * i / n
        major = abs(v / lab - round(v / lab)) < 1e-6
        mid = not major and (i % 5 == 0 if m["scale"] != "t" else i % 10 == 0)
        ln = R * (0.13 if major else 0.09 if mid else 0.055)
        d.line([pt(i / n, R), pt(i / n, R - ln)], fill=BLACK, width=max(2, int(W * (0.010 if major else 0.005))))
    f = font("arial.ttf", H * 0.12)
    for v in range(0, top + 1, lab):
        x, y = pt(v / top, R * 0.68)
        centered(d, x, y, str(v), f, BLACK)
    # thermocouple sign (two circles joined by a line) and accuracy class as a circle; no letters
    s = H * 0.045
    y0 = H * 0.86
    d.ellipse((W * 0.10 - s, y0 - s, W * 0.10 + s, y0 + s), outline=BLACK, width=S)
    if m["scale"] == "t":
        d.line([(W * 0.10 + s, y0), (W * 0.18 - s, y0)], fill=BLACK, width=S)
        d.ellipse((W * 0.18 - s, y0 - s, W * 0.18 + s, y0 + s), fill=BLACK)
    d.polygon([(W * 0.88, y0 - s), (W * 0.88 + s, y0), (W * 0.88, y0 + s), (W * 0.88 - s, y0)], outline=BLACK, width=S)
    rnd = random.Random(ord(m["scale"]))
    tint = Image.new("RGBA", (W, H), (210, 192, 140, 0))
    tint.putalpha(worn_mask(W, H, rnd, 10, 4 * S, 16 * S, 6 * S).point(lambda v: (255 - v) // 4))
    img = Image.alpha_composite(img, tint)
    save(img, "decal_meter_%s.png" % m["scale"])


# =============================================================================
# Regulator dial: a black ring with white ticks and digits 0-10, a 270 degree arc
# =============================================================================
def make_dial():
    r = L.DIAL["r"]
    W = H = int(2 * r * K2)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = W / 2
    d.ellipse((0, 0, W - 1, H - 1), fill=(150, 146, 136, 255))                  # chrome rim
    d.ellipse((W * 0.05, H * 0.05, W * 0.95, H * 0.95), fill=(26, 24, 22, 255))
    R0, R1 = c * 0.86, c * 0.74
    f = font("arial.ttf", H * 0.085)
    for i in range(51):
        a = math.radians(-135 + 270 * i / 50)
        major = i % 5 == 0
        r1 = R1 if major else R1 + (R0 - R1) * 0.5
        d.line([(c + R0 * math.sin(a), c - R0 * math.cos(a)), (c + r1 * math.sin(a), c - r1 * math.cos(a))],
               fill=(220, 214, 196, 255), width=max(2, S * (2 if major else 1)))
        if major:
            rr = c * 0.60
            centered(d, c + rr * math.sin(a), c - rr * math.cos(a), str(i // 5), f, (220, 214, 196, 255))
    rnd = random.Random(7)
    wm = worn_mask(W, H, rnd, 14, 2 * S, 6 * S, 1.5 * S).point(lambda v: 255 if v > 140 else 200)
    a = ImageChops.multiply(img.getchannel("A"), wm)
    img.putalpha(a)
    save(img, "decal_dial.png")


# =============================================================================
# "Hot surface" sign
# =============================================================================
def make_heat():
    s = L.HEAT_SIGN["s"]
    W = H = int(s * K2)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    tri = [(W * 0.5, H * 0.06), (W * 0.97, H * 0.90), (W * 0.03, H * 0.90)]
    d.polygon(tri, fill=(22, 22, 20, 255))
    k = 0.11
    inner = [(W * 0.5, H * (0.06 + k * 1.7)), (W * (0.97 - k * 1.2), H * (0.90 - k * 0.55)),
             (W * (0.03 + k * 1.2), H * (0.90 - k * 0.55))]
    d.polygon(inner, fill=(222, 178, 30, 255))
    # three heat waves above the line
    for j in (-1, 0, 1):
        x0 = W * 0.5 + j * W * 0.12
        pts = [(x0 + W * 0.025 * math.sin(t / 6 * 2 * math.pi), H * 0.74 - H * 0.30 * t / 12) for t in range(13)]
        d.line(pts, fill=(22, 22, 20, 255), width=int(W * 0.035))
    d.rectangle((W * 0.30, H * 0.76, W * 0.70, H * 0.79), fill=(22, 22, 20, 255))
    rnd = random.Random(9)
    soot = Image.new("RGBA", (W, H), (30, 28, 24, 0))
    soot.putalpha(worn_mask(W, H, rnd, 10, 4 * S, 12 * S, 5 * S).point(lambda v: (255 - v) // 3))
    img = Image.alpha_composite(img, Image.composite(soot, Image.new("RGBA", (W, H)), img.getchannel("A")))
    save(img, "decal_heat.png")


# =============================================================================
# Stencil inventory number
# =============================================================================
def make_stencil():
    rnd = random.Random(35)
    s = L.STENCIL
    W, H = int(s["w"] * K), int(s["h"] * K)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    ch = H * 0.86
    u = ch / 10
    x = (W - (len(s["text"]) * 7.6 * u - 1.6 * u)) / 2
    for c in s["text"]:
        for a, b, cc, e in DIGITS[c]:
            d.rectangle((x + a * u, (H - ch) / 2 + b * u, x + cc * u, (H - ch) / 2 + e * u), fill=235)
        x += 7.6 * u
    m = m.filter(ImageFilter.GaussianBlur(1.0 * S))
    m = ImageChops.multiply(m, worn_mask(W, H, rnd, 60, 1.5 * S, 7 * S, 1.2 * S).point(lambda v: 70 + v * 185 // 255))
    img = Image.new("RGBA", (W, H), WHITE + (0,))
    img.putalpha(m)
    save(img, "decal_stencil.png")


if __name__ == "__main__":
    for m in L.METERS:
        make_meter(m)
    make_dial()
    make_heat()
    make_stencil()
