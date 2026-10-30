"""Decals of the soldering station module (system Python + Pillow): the temperature knob scale (ticks
and digits 150-450 over a 270 degree arc, as on the Weller WECP-20 - a 150-450 C potentiometer; digits
only), a soldering iron pictogram above the socket (as on the WTCP-S panel), a yellow "hot surface"
triangle (a flame, no letters) on the left side of the unit, the cover's ventilation slots (five
slits on each side near the top at the back, as on the WTCP-S), the stand's sponge - yellow cellulose
in pores with scorched marks from the tip.

    python make_decals.py      -> ../work/decal_*.png

Sizes are as in build_m73.py (SCALE_D, ICON_*, WARN_D, SPONGE, SLOTS_*).
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4
INK = (226, 228, 224, 255)              # white print on the black panel

SCALE_D = 0.056                         # scale square, the knob of r 0.015 in the centre
ICON_W, ICON_H = 0.012, 0.010           # soldering iron pictogram
WARN_D = 0.026                          # triangle on the side
SPONGE_W, SPONGE_H = 0.064, 0.042       # sponge in plan
SLOTS_W, SLOTS_H = 0.046, 0.030         # slots on the side


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


def make_scale(name, px):
    """Scale 150-450: a 270 degree arc from the bottom left clockwise, a long tick and a digit every 50, a
    short tick every 25, a thin arc under the ticks. The background is transparent - the black panel is
    under it."""
    W = px * S
    k = W / SCALE_D
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = W / 2
    r0, r1, rt = 0.0172 * k, 0.0198 * k, 0.0240 * k

    def at(frac, rr):
        a = math.radians(225.0 - 270.0 * frac)
        return c + rr * math.cos(a), c - rr * math.sin(a)
    d.arc([c - r0, c - r0, c + r0, c + r0], -225 + 360, 45 + 360, fill=INK, width=int(S * 1.2))
    for i in range(13):
        big = i % 2 == 0
        d.line([at(i / 12, r0), at(i / 12, r1 if big else r0 + (r1 - r0) * 0.55)], fill=INK,
               width=int(S * (2.2 if big else 1.2)))
    f = font(int(0.0036 * k))
    for i in range(7):
        d.text(at(i / 6, rt), str(150 + 50 * i), fill=INK, font=f, anchor="mm")
    save(img, (px, px), name)


def make_icon(name, px):
    """Soldering iron pictogram: tip, handle, cord - a white outline, no letters."""
    h = int(round(px * ICON_H / ICON_W))
    W, H = px * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # the axis is tilted: the tip at the bottom left, the handle at the top right
    a = math.radians(28)
    ux, uy = math.cos(a), -math.sin(a)
    nx, ny = -uy, ux

    def P(s, t):
        return (W * 0.08 + 0.84 * (s * W * ux + t * W * nx), H * 0.86 + 0.84 * (s * W * uy + t * W * ny))
    d.line([P(0.0, 0), P(0.22, 0)], fill=INK, width=int(S * 2.0))                       # tip
    d.polygon([P(0.22, -0.035), P(0.30, -0.06), P(0.30, 0.06), P(0.22, 0.035)], fill=INK)  # nut
    d.polygon([P(0.30, -0.07), P(0.72, -0.06), P(0.72, 0.06), P(0.30, 0.07)], outline=INK, width=int(S * 1.6))
    d.line([P(0.72, 0), P(0.84, 0.0), P(0.92, 0.07)], fill=INK, width=int(S * 1.4))      # cord
    save(img, (px, h), name)


def make_warn(name, px):
    """A "hot surface" triangle: yellow, a black border, a flame inside."""
    W = px * S
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = W * 0.04
    top, bl, br = (W / 2, m + W * 0.06), (m, W - m - W * 0.08), (W - m, W - m - W * 0.08)
    d.polygon([top, bl, br], fill=(18, 18, 18, 255))
    inset = W * 0.075
    d.polygon([(W / 2, top[1] + inset * 1.9), (bl[0] + inset * 1.65, bl[1] - inset * 0.95),
               (br[0] - inset * 1.65, br[1] - inset * 0.95)], fill=(236, 186, 22, 255))
    # flame: three tongues and a base
    cx, by = W / 2, bl[1] - W * 0.16
    flame = [(cx - W * 0.14, by), (cx - W * 0.15, by - W * 0.12), (cx - W * 0.08, by - W * 0.20),
             (cx - W * 0.07, by - W * 0.12), (cx - W * 0.02, by - W * 0.30), (cx + W * 0.03, by - W * 0.16),
             (cx + W * 0.09, by - W * 0.22), (cx + W * 0.10, by - W * 0.11), (cx + W * 0.14, by - W * 0.04),
             (cx + W * 0.13, by)]
    d.polygon(flame, fill=(18, 18, 18, 255))
    d.rectangle([cx - W * 0.19, by + W * 0.03, cx + W * 0.19, by + W * 0.055], fill=(18, 18, 18, 255))
    save(img, (px, px), name)


def make_slots(name, px):
    """Five ventilation slots of the cover: dark slits with rounded ends and a light edge below (the
    bent-over rim), the background is transparent - the enamel of the cover is under it."""
    h = int(round(px * SLOTS_H / SLOTS_W))
    W, H = px * S, h * S
    k = W / SLOTS_W
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(5):
        zc = (0.0035 + i * 0.0058) * k
        x0, x1, hh = 0.003 * k, (SLOTS_W - 0.003) * k, 0.0013 * k
        d.rounded_rectangle([x0, H - zc - hh - 0.0005 * k, x1, H - zc + hh + 0.0005 * k], radius=hh, fill=(150, 160, 168, 120))
        d.rounded_rectangle([x0, H - zc - hh, x1, H - zc + hh], radius=hh, fill=(10, 11, 12, 255))
    save(img, (px, h), name)


def make_sponge(name, px):
    """Sponge: yellow cellulose, pores as dark dots, scorched streaks from the tip along the middle."""
    h = int(round(px * SPONGE_H / SPONGE_W))
    W, H = px * S, h * S
    rnd = random.Random(73)
    img = Image.new("RGBA", (W, H), (206, 160, 62, 255))
    d = ImageDraw.Draw(img)
    for _ in range(int(W * H / 90)):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        r = rnd.uniform(0.6, 2.4) * S / 2
        t = rnd.uniform(0.55, 0.85)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(int(206 * t), int(160 * t), int(62 * t), 255))
    burn = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(burn)
    for _ in range(26):                     # marks from wiping the tip: short strokes along the sponge
        x = rnd.uniform(W * 0.18, W * 0.82)
        y = rnd.uniform(H * 0.22, H * 0.78)
        L = rnd.uniform(W * 0.06, W * 0.20)
        a = rnd.uniform(-0.25, 0.25)
        bd.line([(x - L / 2 * math.cos(a), y - L / 2 * math.sin(a)), (x + L / 2 * math.cos(a), y + L / 2 * math.sin(a))],
                fill=(54, 40, 22, rnd.randint(90, 190)), width=int(rnd.uniform(1.5, 4.0) * S))
    for _ in range(9):                      # solder drops and flux stains
        x, y = rnd.uniform(W * 0.15, W * 0.85), rnd.uniform(H * 0.2, H * 0.8)
        r = rnd.uniform(1.5, 3.5) * S
        bd.ellipse([x - r, y - r, x + r, y + r], fill=(30, 24, 16, 200))
    img = Image.alpha_composite(img, burn.filter(ImageFilter.GaussianBlur(S * 0.8)))
    save(img, (px, h), name)


if __name__ == "__main__":
    make_scale("decal_scale.png", 256)
    make_icon("decal_icon.png", 96)
    make_warn("decal_warn.png", 128)
    make_sponge("decal_sponge.png", 256)
    make_slots("decal_slots.png", 192)
