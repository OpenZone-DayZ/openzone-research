"""Decals of the pressure test pump module (system Python + Pillow): a 100 mm pressure gauge dial
(a white 0-16 scale on a 270-degree arc, like the technical gauges MP-100 / MTP-100: big ticks and
digits every 2, medium every 1, small every 0.5; a red tick of the working pressure at 10; the
accuracy class "2,5" at the bottom - digits only) and an aluminium inventory tag on the tank (a
punched number, a frame, two holes for rivets).

    python make_decals.py      -> ../work/decal_*.png

Sizes match build_m84.py (DIAL_R, TAG_W, TAG_H).
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4

DIAL_R = 0.046                          # dial radius under the glass
TAG_W, TAG_H = 0.044, 0.024             # tag on the tank
FACE = (236, 233, 222, 255)             # white dial enamel, slightly yellowed
INK = (24, 24, 26, 255)
RED = (190, 30, 26, 255)


def font(px, bold=True):
    for name in (("arialbd.ttf", "arial.ttf") if bold else ("arial.ttf",)):
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


def make_dial(name, px):
    """Scale 0-16: a 270-degree arc from the bottom left (0) clockwise to the bottom right (16), as on
    gauges to GOST 2405. A square of 2*DIAL_R, transparent outside the circle (the case ring is there).
    """
    W = px * S
    k = W / (2 * DIAL_R)
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = W / 2
    d.ellipse([0, 0, W - 1, W - 1], fill=FACE)
    r_out = 0.0405 * k

    def at(frac, rr):
        a = math.radians(225.0 - 270.0 * frac)
        return c + rr * math.cos(a), c - rr * math.sin(a)
    # arc under the ticks
    r_arc = r_out - 0.0050 * k
    d.arc([c - r_arc, c - r_arc, c + r_arc, c + r_arc], -225 + 360, 45 + 360, fill=INK, width=int(S * 1.4))
    for i in range(33):                 # every 0.5
        frac = i / 32
        if i % 4 == 0:
            ln, w = 0.0064, 3.0
        elif i % 2 == 0:
            ln, w = 0.0050, 2.0
        else:
            ln, w = 0.0038, 1.4
        d.line([at(frac, r_out - ln * k), at(frac, r_out)], fill=INK, width=int(S * w))
    f = font(int(0.0074 * k))
    for i in range(9):
        d.text(at(i / 8, 0.0272 * k), str(2 * i), fill=INK, font=f, anchor="mm")
    # red tick of the working pressure at 10 (over the scale, as applied during verification)
    d.line([at(10 / 16, r_out - 0.0080 * k), at(10 / 16, r_out + 0.0010 * k)], fill=RED, width=int(S * 3.4))
    # accuracy class and the needle stop at zero
    d.text((c, c + 0.0215 * k), "2,5", fill=INK, font=font(int(0.0046 * k), bold=False), anchor="mm")
    sx, sy = at(-0.035, r_out - 0.0035 * k)
    rr = 0.0012 * k
    d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], fill=(90, 90, 92, 255))
    # slight yellowing toward the edge - old glass and enamel
    edge = Image.new("L", (W, W), 0)
    ImageDraw.Draw(edge).ellipse([0.06 * W, 0.06 * W, 0.94 * W, 0.94 * W], fill=255)
    edge = edge.filter(ImageFilter.GaussianBlur(W * 0.05))
    tint = Image.new("RGBA", (W, W), (214, 200, 160, 255))
    mask = Image.new("L", (W, W), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, W - 1, W - 1], fill=90)
    mask = Image.composite(Image.new("L", (W, W), 0), mask, edge)
    img = Image.composite(tint, img, mask)
    save(img, (px, px), name)


def make_tag(name, px):
    """Tag: a punched frame along the edge, the number "0417" and two rivet holes (the rivets themselves
    are geometry). Transparent background - the tag's aluminium is under it.
    """
    h = int(round(px * TAG_H / TAG_W))
    W, H = px * S, h * S
    k = W / TAG_W
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ink = (60, 62, 64, 230)
    m = 0.0022 * k
    d.rounded_rectangle([m, m, W - m, H - m], radius=0.0016 * k, outline=ink, width=int(S * 1.6))
    d.text((W / 2, H / 2 + 0.0004 * k), "0417", fill=ink, font=font(int(0.0105 * k)), anchor="mm")
    for x in (0.0046 * k, W - 0.0046 * k):
        r = 0.0016 * k
        d.ellipse([x - r, H / 2 - r, x + r, H / 2 + r], fill=(40, 40, 42, 255))
    save(img, (px, h), name)


if __name__ == "__main__":
    make_dial("decal_dial.png", 512)
    make_tag("decal_tag.png", 256)
