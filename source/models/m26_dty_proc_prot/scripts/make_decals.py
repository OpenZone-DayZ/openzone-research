"""Decals of the plate shooting test stand (system Python + Pillow): the display of the registration
unit (speed and shot number, vacuum fluorescent), chalk circles with numbers around the hits on the
plate, a measuring scale on the lower crossbar of the frame, the scale of the needle indicator, toggle
marks and the limb of the unit knob, an inventory tag with stamped digits. No letters: only digits,
ticks, circles.

The display has its own part texture: screen_off.png "off" and the "working" frames screen_fNN.png
(OZL_WorkFx frames): 36 frames - a series of six shots, six stages per shot: ready (dashes), counting
(the digits run to the speed), result, hold (the signal bar fades).

    python make_decals.py      -> ../work/decal_*.png, ../work/screen_*.png
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout26 as lay  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscaling - smooth edges
WHITE = (226, 224, 214, 255)
INK = (24, 24, 24, 255)

SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc", "7": "abc",
       "8": "abcdefg", "9": "abcdfg", " ": "", "-": "g"}


def font(px):
    for name in ("arialbd.ttf", "arial.ttf", "consola.ttf"):
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def glow(img, layer, r):
    img = Image.alpha_composite(img, layer.filter(ImageFilter.GaussianBlur(r)))
    return Image.alpha_composite(img, layer)


def segments(base, layer, W, H, text, x0f, x1f, y0f, y1f, color, dim, skew=0.08):
    """Seven-segment digits (as in M24, but thinner and with a separator dot)."""
    digits = [c for c in text if c != "."]
    dots, k = set(), 0
    for c in text:
        if c == ".":
            dots.add(k - 1)
        else:
            k += 1
    cw = W * (x1f - x0f) / len(digits)
    b, g = ImageDraw.Draw(base), ImageDraw.Draw(layer)
    for i, ch in enumerate(digits):
        xa, xb = W * x0f + i * cw + cw * 0.22, W * x0f + i * cw + cw * 0.70
        ya, ym, yb = H * y0f, H * (y0f + y1f) / 2, H * y1f
        t = max(S * 2, cw * 0.09)
        sk = (yb - ya) * skew

        def p(x, y):
            return (x + sk * (yb - y) / (yb - ya), y)
        segs = {"a": [p(xa, ya), p(xb, ya)], "g": [p(xa, ym), p(xb, ym)], "d": [p(xa, yb), p(xb, yb)],
                "f": [p(xa, ya), p(xa, ym)], "b": [p(xb, ya), p(xb, ym)], "e": [p(xa, ym), p(xa, yb)],
                "c": [p(xb, ym), p(xb, yb)]}
        for s, ln in segs.items():
            if dim is not None:
                b.line(ln, fill=dim, width=int(t))
            if color is not None and s in SEG[ch]:
                g.line(ln, fill=color, width=int(t))
        if i in dots:
            box = [xb + cw * 0.10, yb - t, xb + cw * 0.10 + t * 1.2, yb + t * 0.2]
            (g if color is not None else b).ellipse(box, fill=color or dim)


def make_display(name, on, speed="838.4", shot=" 6", bar=14, w=600, h=172):
    """Registration unit display: on the left the bullet speed, m/s, large, on the right the shot number
    in the series, smaller, under them a strip of divisions (the frame signal level). Vacuum fluorescent,
    turquoise - so as not to repeat the red LEDs of M24. "Off" - a dark filter, segments barely visible.
    The image covers the whole display (0.150 x 0.043 m): the part's own texture, UV 0..1."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (14, 22, 22, 255) if on else (18, 20, 20, 255))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    col = (120, 255, 226, 255) if on else None
    dim = (26, 40, 38, 255) if on else (30, 33, 33, 255)
    segments(img, layer, W, H, speed, 0.03, 0.62, 0.12, 0.70, col, dim)
    segments(img, layer, W, H, shot, 0.70, 0.97, 0.26, 0.70, col, dim)
    d, dl = ImageDraw.Draw(img), ImageDraw.Draw(layer)
    n = 20
    for i in range(n):
        x0 = W * (0.05 + 0.60 * i / n)
        box = [x0, H * 0.80, x0 + W * 0.60 / n * 0.6, H * 0.90]
        d.rectangle(box, fill=dim)
        if on and i < bar:
            dl.rectangle(box, fill=col)
    # separator between the fields
    d.line([(W * 0.665, H * 0.14), (W * 0.665, H * 0.86)], fill=(40, 46, 46, 255), width=S * 2)
    img = glow(img, layer, H * 0.03) if on else img
    # a fine filter grid and a highlight over the glass - so that the display is not a flat fill
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    do = ImageDraw.Draw(over)
    for k in range(0, W, S * 8):
        do.line([(k, 0), (k, H)], fill=(0, 0, 0, 40), width=S)
    do.polygon([(W * 0.08, 0), (W * 0.30, 0), (W * 0.18, H), (0, H)], fill=(255, 255, 255, 12))
    img = Image.alpha_composite(img, over.filter(ImageFilter.GaussianBlur(S * 0.8)))
    save(img, (w, h), name)


# a series of six shots (7.62 x 54R at the plate): speed at the frames, m/s
SERIES = ["838.4", "835.9", "841.2", "830.7", "836.1", "839.5"]
# signal bar of the frames at the shot stages (out of 20 divisions): the burst of the first frame and its
# fall, full - the second frame, hold - fading; slightly different for each shot so that the series does
# not repeat one frame
BAR_COUNT = ((12, 6), (11, 5), (13, 7), (12, 6), (10, 5), (13, 7))
BAR_HOLD = ((9, 3), (11, 4), (8, 2), (10, 3), (9, 4), (11, 2))


def shot_stages(k, v, rnd):
    """Stages of shot k (from zero) at speed v (the string "838.4"): [(speed field, number, bar)]: ready -
    dashes and the number of this shot, the bar is empty; counting - the bullet is between the frames, the
    digits run to the speed (a quarter, then two thirds), the bar is the burst of the first frame and its
    fall; result - the speed, the bar is full (the second frame); hold - the speed stays, the bar fades."""
    num = " %d" % (k + 1)
    speed = float(v)
    run = ["%5.1f" % (speed * rnd.uniform(*f) + rnd.uniform(0.0, 0.9)) for f in ((0.20, 0.32), (0.58, 0.72))]
    return [("---.-", num, 0), (run[0], num, BAR_COUNT[k][0]), (run[1], num, BAR_COUNT[k][1]), (v, num, 20),
            (v, num, BAR_HOLD[k][0]), (v, num, BAR_HOLD[k][1])]


def make_screen_frames():
    """The "off" frame and the "working" frames: a series of six shots, six stages per shot (shot_stages) -
    36 OZL_WorkFx frames of ~0.25 s each, the series takes 9 s. Frame 0 is the result of the first shot
    (the "working" preview shows it), the last three are the ready and counting stages of the first shot:
    the series loops without a break."""
    make_display("screen_off.png", False)
    rnd = random.Random(26)
    seq = [st for k, v in enumerate(SERIES) for st in shot_stages(k, v, rnd)]
    assert len(seq) == lay.SCREEN_FRAMES, "display frames %d, in layout26 - %d" % (len(seq), lay.SCREEN_FRAMES)
    seq = seq[3:] + seq[:3]
    for i, (speed, num, bar) in enumerate(seq):
        make_display("screen_f%02d.png" % i, True, speed, num, bar)


def make_meter(name, w=600, h=380):
    """Scale of the needle indicator of the frame signal level: a 90-degree arc, ticks every division,
    digits 0, 5, 10, a red sector at the end of the scale; the needle pivot is at the bottom center.
    Transparent background (the base is cream, in "working" backlit - given by the material). The image
    frame = the scale window."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    a0, a1, b0, b1 = lay.METER_WIN
    sx, sy = W / (a1 - a0), H / (b1 - b0)
    cx, cy = (lay.METER_PIVOT[0] - a0) * sx, (b1 - lay.METER_PIVOT[1]) * sy
    r = lay.METER_R * sx
    f = font(int(H * 0.13))
    rest, sweep = lay.METER_REST, lay.METER_SWEEP

    def at(frac, rr):
        a = math.radians(rest - sweep * frac)
        return cx + math.cos(a) * rr, cy - math.sin(a) * rr
    # red sector 8..10
    for k in range(40):
        fr = 0.8 + 0.2 * k / 40
        d.line([at(fr, r * 0.93), at(fr, r * 1.0)], fill=(176, 36, 30, 255), width=S * 4)
    arc = [at(i / 60, r * 0.92) for i in range(61)]
    d.line(arc, fill=INK, width=S * 3)
    for i in range(21):
        ln = 0.80 if i % 10 == 0 else 0.84 if i % 2 == 0 else 0.875
        d.line([at(i / 20, r * ln), at(i / 20, r * 0.92)], fill=INK, width=S * (4 if i % 2 == 0 else 2))
    for i, txt in ((0, "0"), (10, "5"), (20, "10")):
        d.text(at(i / 20, r * 0.66), txt, fill=INK, font=f, anchor="mm")
    # zero corrector screw under the pivot - a dark circle
    d.ellipse([cx - S * 14, cy - S * 14, cx + S * 14, cy + S * 14], fill=(60, 58, 54, 255))
    save(img, (w, h), name)


def make_hits(name, w=500, h=600):
    """Chalk circles around the hits on the plate face and the shot number beside them (this is how a
    series is marked at tests). Transparent background; the image frame = the plate face."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rnd = random.Random(26)
    f = font(int(H * 0.045))
    sx, sz = W / (lay.PX1 - lay.PX0), H / (lay.PZ1 - lay.PZ0)
    chalk = (236, 232, 214, 235)
    for k, (x, z, r) in enumerate(lay.HITS):
        cx, cy = (x - lay.PX0) * sx, (lay.PZ1 - z) * sz
        rr = r * 2.6 * sx
        pts = []
        a0 = rnd.uniform(0, math.tau)
        for i in range(41):
            a = a0 + math.tau * 1.06 * i / 40
            q = rr * (1 + 0.07 * math.sin(a * 3 + k) + rnd.uniform(-0.03, 0.03))
            pts.append((cx + math.cos(a) * q, cy + math.sin(a) * q))
        d.line(pts, fill=chalk, width=int(S * 3.2))
        tx = cx + rr * 1.25 * (1 if x < 0.03 else -1)
        d.text((tx, cy - rr * 0.9), str(k + 1), fill=chalk, font=f, anchor="mm")
    img = img.filter(ImageFilter.GaussianBlur(S * 0.6))
    save(img, (w, h), name)


def make_scale(name, w=1200, h=60):
    """Measuring scale in white paint on the face of the lower crossbar: 0.60 m, a tick every 1 cm, a long
    one every 5, digits every 10 (from the middle in both directions)."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font(int(H * 0.42))
    for i in range(61):
        x = W * i / 60
        cm = i - 30
        ln = 0.55 if cm % 5 == 0 else 0.30
        d.line([(x, 0), (x, H * ln)], fill=WHITE, width=S * (3 if cm % 5 == 0 else 2))
        if cm % 10 == 0 and abs(cm) < 30:
            d.text((x, H * 0.78), str(abs(cm)), fill=WHITE, font=f, anchor="mm")
    img = img.filter(ImageFilter.GaussianBlur(S * 0.4))
    save(img, (w, h), name)


def make_unit_panel(name, w=780, h=120):
    """Marks on the unit face under the display (the lay.PANEL strip): above the two toggles "on" arrows,
    under them nameplates with the numbers of frames 1 and 2; the limb of the threshold knob (ticks and
    digits 0-9); around the mains lamp a white ring. The positions are from layout26 (the same as for the
    parts)."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    a0, a1, b0, b1 = lay.PANEL

    def px(a, b):
        return (a - a0) / (a1 - a0) * W, (b1 - b) / (b1 - b0) * H
    f = font(int(H * 0.20))
    for i, a in enumerate(lay.TOGS):
        x, _ = px(a, 0)
        _, ytop = px(a, lay.TOG_B + 0.017)
        d.polygon([(x, ytop), (x - W * 0.010, ytop + H * 0.12), (x + W * 0.010, ytop + H * 0.12)], fill=WHITE)
        _, yb = px(a, 0.008)
        d.rectangle([x - W * 0.030, yb - H * 0.12, x + W * 0.030, yb + H * 0.12], fill=(206, 204, 196, 255))
        d.text((x, yb), str(i + 1), fill=INK, font=f, anchor="mm")
    cx, cy = px(*lay.KNOB)
    rr = lay.KNOB_R * 1.75 / (a1 - a0) * W
    fs = font(int(H * 0.11))
    for k in range(10):
        a = math.radians(135 + 270 * k / 9)
        d.line([(cx + math.cos(a) * rr * 0.80, cy + math.sin(a) * rr * 0.80),
                (cx + math.cos(a) * rr, cy + math.sin(a) * rr)], fill=WHITE, width=S * 2)
        d.text((cx + math.cos(a) * rr * 0.62, cy + math.sin(a) * rr * 0.62), str(k), fill=WHITE, font=fs, anchor="mm")
    lx, ly = px(*lay.LAMP)
    lr = 0.0125 / (a1 - a0) * W
    d.ellipse([lx - lr, ly - lr, lx + lr, ly + lr], outline=WHITE, width=S * 2)
    save(img, (w, h), name)


def make_tag(name, w=320, h=200):
    """Inventory tag: aluminum, a stamped frame around the edge, a stamped number in the middle, no text."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (176, 178, 176, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([W * 0.06, H * 0.10, W * 0.94, H * 0.90], outline=(96, 98, 98, 255), width=S * 3)
    f = font(int(H * 0.36))
    d.text((W * 0.5 + S * 2, H * 0.52 + S * 2), "0417", fill=(220, 222, 220, 255), font=f, anchor="mm")
    d.text((W * 0.5, H * 0.52), "0417", fill=(84, 86, 86, 255), font=f, anchor="mm")
    for x in (0.12, 0.88):
        d.ellipse([W * x - S * 8, H * 0.5 - S * 8, W * x + S * 8, H * 0.5 + S * 8], fill=(70, 70, 70, 255))
    save(img, (w, h), name)


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    make_screen_frames()
    make_meter("decal_meter.png")
    make_hits("decal_hits.png")
    make_scale("decal_scale.png")
    make_unit_panel("decal_unit.png")
    make_tag("decal_tag.png")
