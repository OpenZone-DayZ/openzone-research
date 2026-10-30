"""Decals of the centrifuge module (system Python + Pillow): the timer knob scale (dots and
digits 0-30 minutes along an arc, as on the MPW-2), the tachometer scale (ticks and digits
0-6, thousands of rpm) in two looks - "off" and "working" (lit, like the "mains" lamp), the
rotation arrow on the lid, an inventory tag without text (the number in digits). Digits
only, no letters.

The tachometer needle is not drawn: it is a part on the bone ozl_needle (build_m45.py) and
sways while working; a drawn one would stay at zero as a second needle. The axis dot stays -
the needle hub covers it.

    python make_decals.py      -> ../work/decal_*.png

Sizes match build_m45.py (TIMER_*, METER_*, ARROW_*, TAG_*).
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4
INK = (28, 30, 32, 255)

TIMER_D = 0.054                         # timer scale square, knob r 0.012 in the center
METER_W, METER_H = 0.028, 0.022         # tachometer face
ARROW_D = 0.060                         # rotation arrow on the lid
TAG_W, TAG_H = 0.032, 0.020             # tag on the side


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


def make_timer(name, px):
    """Timer 0-30 min: dots every 5 minutes along a 270 degree arc from the bottom left clockwise,
    digits 0, 10, 20, 30, small ticks every minute. Transparent background - the panel enamel
    shows through.
    """
    W = px * S
    k = W / TIMER_D
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = W / 2
    r0, r1, rt = 0.0145 * k, 0.0175 * k, 0.0228 * k

    def at(frac, rr):
        a = math.radians(225.0 - 270.0 * frac)
        return c + rr * math.cos(a), c - rr * math.sin(a)
    for i in range(31):
        big = i % 5 == 0
        d.line([at(i / 30, r0), at(i / 30, r1 if big else r0 + (r1 - r0) * 0.5)], fill=INK,
               width=int(S * (2.2 if big else 1.0)))
    f = font(int(0.0042 * k))
    for i in (0, 10, 20, 30):
        d.text(at(i / 30, rt), str(i), fill=INK, font=f, anchor="mm")
    save(img, (px, px), name)


def make_meter(name, px, bg, ink, glow=None):
    """Tachometer: a 90 degree arc, 31 ticks, digits 0-6, a red zone at the end, the dot of the
    needle axis (the needle itself is a model part), a dark frame.
    """
    h = int(round(px * METER_H / METER_W))
    W, H = px * S, h * S
    k = W / METER_W
    img = Image.new("RGBA", (W, H), bg)
    if glow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([W * 0.05, H * 0.1, W * 0.95, H * 1.5], fill=glow)
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(H * 0.12)))
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, H * 0.92
    R = 0.0145 * k

    def at(frac, rr):
        a = math.radians(135.0 - 90.0 * frac)
        return cx + rr * math.cos(a), cy - rr * math.sin(a)
    for i in range(31):
        big, mid = i % 5 == 0, i % 5 == 0
        d.line([at(i / 30, R), at(i / 30, R * (1.14 if big else 1.07))], fill=ink, width=int(S * (2 if mid else 1)))
    f = font(int(0.0034 * k))
    for i in range(7):
        d.text(at(i / 6, R * 1.30), str(i), fill=ink, font=f, anchor="mm")
    d.arc([cx - R * 0.94, cy - R * 0.94, cx + R * 0.94, cy + R * 0.94], -135 + 90 * 0.82, -45,
          fill=(176, 40, 30, 255), width=S * 3)
    d.ellipse([cx - S * 4, cy - S * 4, cx + S * 4, cy + S * 4], fill=(20, 20, 20, 255))
    d.rectangle([0, 0, W - 1, H - 1], outline=(26, 26, 26, 255), width=S * 3)
    save(img, (px, h), name)


def make_arrow(name, px):
    """Rotation direction arrow: a 150 degree arc with an arrowhead, clockwise (top view)."""
    W = px * S
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c, R, th = W / 2, W * 0.34, W * 0.07
    a0, a1 = 190.0, 320.0                                 # PIL angles: from +x clockwise (y down)
    d.arc([c - R, c - R, c + R, c + R], a0, a1, fill=(30, 30, 30, 235), width=int(th))
    a = math.radians(a1)
    rm = R - th / 2                                       # middle of the arc thickness
    tip0 = (c + rm * math.cos(a), c + rm * math.sin(a))
    t = (-math.sin(a), math.cos(a))                       # along the arc (PIL angle grows)
    n = (math.cos(a), math.sin(a))
    L, Wd = W * 0.14, W * 0.10
    d.polygon([(tip0[0] + t[0] * L, tip0[1] + t[1] * L), (tip0[0] + n[0] * Wd, tip0[1] + n[1] * Wd),
               (tip0[0] - n[0] * Wd, tip0[1] - n[1] * Wd)], fill=(30, 30, 30, 235))
    save(img, (px, px), name)


def make_tag(name, px):
    """Inventory tag: yellowed paper, a frame, the number in digits, a strip for a signature."""
    h = int(round(px * TAG_H / TAG_W))
    W, H = px * S, h * S
    img = Image.new("RGBA", (W, H), (226, 214, 176, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([S * 3, S * 3, W - S * 4, H - S * 4], outline=(70, 60, 50, 255), width=S * 2)
    d.text((W * 0.5, H * 0.40), "0417", fill=(40, 36, 60, 255), font=font(int(H * 0.36)), anchor="mm")
    d.line([(W * 0.18, H * 0.74), (W * 0.82, H * 0.74)], fill=(70, 60, 50, 255), width=S * 2)
    save(img, (px, h), name)


if __name__ == "__main__":
    make_timer("decal_timer.png", 256)
    make_meter("decal_meter_off.png", 192, (214, 210, 194, 255), (36, 36, 34, 255))
    make_meter("decal_meter_on.png", 192, (252, 240, 204, 255), (26, 24, 20, 255), glow=(255, 248, 214, 130))
    make_arrow("decal_arrow.png", 160)
    make_tag("decal_tag.png", 128)
