"""Decals for the electronics packer (system Python + Pillow): scales of the supply's pointer meters
(the needles are their own parts and bones, not in the image), knob limbs, housing slots, the EOP
power board, the EOP screen "off" and the "work" frames (phosphor glow, "snow"), rosin stains and
solder drops on the bench sheet. No letters: only digits on the scales. Sizes of the scales and the
screen are in layout.py (shared with build_m05.py).

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import layout as L

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
FACE = (236, 234, 224, 255)
INK = (24, 24, 24, 255)
RED = (176, 32, 26, 255)


def font(px):
    for name in ("arial.ttf", "consola.ttf"):
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


def make_meter(name, labels, minor=5):
    """Panel meter face (like the M4200): white field, arc, ticks, digits, a red sector at the end of the
    scale. No needle: it is its own part (bone ozl_needle_*), the axis is layout.PIVOT."""
    w, h = L.DIAL_PX
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), FACE)
    d = ImageDraw.Draw(img)
    cx, cy = W * L.PIVOT[0], H * L.PIVOT[1]
    r = H * L.ARC_R
    a0, a1 = L.ARC_DEG

    def at(frac, rr):
        a = math.radians(a0 + (a1 - a0) * frac)
        return cx + math.cos(a) * rr, cy - math.sin(a) * rr
    # arc: PIL counts angles clockwise from +x, we count counter-clockwise
    d.arc([cx - r, cy - r, cx + r, cy + r], -a0, -a1, fill=INK, width=int(H * 0.012))
    # red sector - the last 10 % of the scale
    for k in range(9):
        f = 0.9 + 0.1 * k / 8
        d.line([at(f, r * 1.015), at(f, r * 1.05)], fill=RED, width=int(H * 0.018))
    n_major = len(labels) - 1
    n = n_major * minor
    for i in range(n + 1):
        big = i % minor == 0
        mid = (i % minor) * 2 == minor
        d.line([at(i / n, r), at(i / n, r * (1.11 if big else (1.08 if mid else 1.055)))], fill=INK,
               width=int(H * (0.016 if big else 0.008)))
    f = font(int(H * 0.13))
    for k, lab in enumerate(labels):
        d.text(at(k / n_major, r * 1.25), lab, fill=INK, font=f, anchor="mm")
    # mirror strip under the arc (accurate reading without parallax) - a grey arc
    d.arc([cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86], -a0 + 2, -a1 - 2, fill=(150, 150, 146, 255),
          width=int(H * 0.03))
    # scale mounting screws
    for sx in (0.10, 0.90):
        x, y = W * sx, H * 0.86
        d.ellipse([x - H * 0.025, y - H * 0.025, x + H * 0.025, y + H * 0.025], fill=(120, 120, 116, 255))
        d.line([x - H * 0.02, y, x + H * 0.02, y], fill=(60, 60, 58, 255), width=int(H * 0.008))
    save(img, (w, h), name)


def make_knob_ring(name, px, labels, sweep, color=INK):
    """Limb under a knob: ticks and digits along an arc on transparent (laid on the panel)."""
    n = px * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = n / 2
    k = len(labels)
    start = -90 - sweep / 2
    f = font(int(n * 0.11))
    for i in range(2 * (k - 1) + 1):
        a = math.radians(start + sweep * i / (2 * (k - 1)))
        big = i % 2 == 0
        r0, r1 = n * 0.31, n * (0.37 if big else 0.345)
        d.line([(c + math.cos(a) * r0, c + math.sin(a) * r0), (c + math.cos(a) * r1, c + math.sin(a) * r1)], fill=color,
               width=int(n * (0.018 if big else 0.010)))
        if big:
            lab = labels[i // 2]
            d.text((c + math.cos(a) * n * 0.45, c + math.sin(a) * n * 0.45), lab, fill=color, font=f, anchor="mm")
    save(img, (px, px), name)


def make_vents(name, w=512, h=256, rows=2, n=9):
    """Supply housing slots: two rows of elongated dark slits with a shadow on transparent."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    sw, sh = W * 0.055, H * 0.30
    for rr in range(rows):
        y0 = H * (0.12 + 0.46 * rr)
        for i in range(n):
            x0 = W * 0.08 + i * (W * 0.84 - sw) / (n - 1)
            d.rounded_rectangle([x0 - S * 2, y0 - S * 2, x0 + sw + S * 2, y0 + sh + S * 2], radius=sw / 2,
                                fill=(200, 196, 180, 120))
            d.rounded_rectangle([x0, y0, x0 + sw, y0 + sh], radius=sw / 2, fill=(14, 14, 14, 255))
    save(img, (w, h), name)


def make_pcb(w=512, h=320, seed=5):
    """EOP power board from the night-vision goggle: green mask, copper traces and pads, a white silkscreen
    outline without letters (part outlines), input pads at the left, output at the back."""
    rnd = random.Random(seed)
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (34, 92, 52, 255))
    d = ImageDraw.Draw(img)
    copper = (176, 150, 70, 255)
    silk = (220, 224, 210, 255)
    pads = [(rnd.uniform(0.06, 0.94) * W, rnd.uniform(0.08, 0.92) * H) for _ in range(52)]
    for i in range(len(pads) - 1):
        if rnd.random() < 0.7:
            (xa, ya), (xb, yb) = pads[i], pads[(i + rnd.randint(1, 4)) % len(pads)]
            d.line([(xa, ya), (xb, ya), (xb, yb)], fill=(52, 120, 64, 255), width=S * 5)
            d.line([(xa, ya), (xb, ya), (xb, yb)], fill=copper, width=S * 2)
    for x, y in pads:
        d.ellipse([x - S * 5, y - S * 5, x + S * 5, y + S * 5], fill=copper)
        d.ellipse([x - S * 2, y - S * 2, x + S * 2, y + S * 2], fill=(20, 30, 20, 255))
    for _ in range(9):
        x, y = rnd.uniform(0.08, 0.80) * W, rnd.uniform(0.1, 0.75) * H
        d.rectangle([x, y, x + rnd.uniform(0.08, 0.16) * W, y + rnd.uniform(0.08, 0.16) * H], outline=silk, width=S * 2)
    d.rectangle([S * 6, S * 6, W - S * 6, H - S * 6], outline=silk, width=S * 2)
    # input pads (left, for alligator clips) and output to the EOP (back)
    for y in (0.26, 0.60):
        d.rectangle([0, y * H - S * 10, W * 0.07, y * H + S * 10], fill=copper)
    for x in (0.44, 0.56):
        d.rectangle([x * W - S * 9, 0, x * W + S * 9, H * 0.08], fill=copper)
    for x, y in ((0.04, 0.06), (0.96, 0.06), (0.04, 0.94), (0.96, 0.94)):
        d.ellipse([x * W - S * 10, y * H - S * 10, x * W + S * 10, y * H + S * 10], fill=copper)
        d.ellipse([x * W - S * 6, y * H - S * 6, x * W + S * 6, y * H + S * 6], fill=(10, 12, 10, 255))
    # rosin drops by the solder joints
    for _ in range(7):
        x, y = rnd.uniform(0.1, 0.9) * W, rnd.uniform(0.1, 0.9) * H
        rr = rnd.uniform(4, 9) * S
        d.ellipse([x - rr, y - rr * 0.8, x + rr, y + rr * 0.8], fill=(150, 100, 30, 150))
    save(img, (w, h), "decal_pcb.png")


def make_eop():
    """EOP screen (output window, 18 mm working field): "off" - dark greenish glass with a glare; "work"
    frames - yellow-green phosphor glow with "snow" (noise flashes) and a soft field edge; the frames
    differ, so the snow flickers (OZL_WorkFx frames)."""
    n = L.EOP_PX * S
    c = n / 2
    off = Image.new("RGBA", (n, n), (16, 22, 18, 255))
    d = ImageDraw.Draw(off)
    for k in range(40, 0, -1):
        v = 16 + int(14 * (1 - k / 40))
        d.ellipse([c - n * 0.48 * k / 40, c - n * 0.48 * k / 40, c + n * 0.48 * k / 40, c + n * 0.48 * k / 40],
                  fill=(v, v + 8, v + 2, 255))
    d.ellipse([n * 0.22, n * 0.16, n * 0.42, n * 0.30], fill=(70, 84, 76, 255))
    off = off.filter(ImageFilter.GaussianBlur(S * 3))
    save(off, (L.EOP_PX, L.EOP_PX), "decal_eop_off.png")
    for f in range(L.EOP_FRAMES):
        rnd = random.Random(100 + f)
        img = Image.new("RGBA", (n, n), (0, 0, 0, 255))
        d = ImageDraw.Draw(img)
        gain = 0.88 + 0.12 * rnd.random()
        for k in range(48, 0, -1):
            t = k / 48
            g = gain * (0.55 + 0.45 * (1 - t) ** 0.6)
            d.ellipse([c - n * 0.49 * t, c - n * 0.49 * t, c + n * 0.49 * t, c + n * 0.49 * t],
                      fill=(int(120 * g), int(230 * g), int(90 * g), 255))
        snow = Image.new("RGBA", (n, n), (0, 0, 0, 0))
        sd = ImageDraw.Draw(snow)
        for _ in range(260):
            a, rr = rnd.uniform(0, 2 * math.pi), n * 0.47 * math.sqrt(rnd.random())
            x, y = c + rr * math.cos(a), c + rr * math.sin(a)
            s = rnd.uniform(0.6, 2.2) * S
            v = rnd.randint(170, 255)
            sd.ellipse([x - s, y - s, x + s, y + s], fill=(min(255, v), 255, min(255, v - 40), rnd.randint(120, 255)))
        img = Image.alpha_composite(img, snow.filter(ImageFilter.GaussianBlur(S * 0.8)))
        # field edge - soft darkening
        mask = Image.new("L", (n, n), 0)
        ImageDraw.Draw(mask).ellipse([n * 0.03, n * 0.03, n * 0.97, n * 0.97], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(S * 3))
        bg = Image.new("RGBA", (n, n), (8, 14, 8, 255))
        img = Image.composite(img, bg, mask)
        save(img, (L.EOP_PX, L.EOP_PX), "decal_eop_f%02d.png" % f)


def make_rosin(seed=11):
    """Bench sheet where the soldering station stands (slot 2): rosin stains (amber, streaks with a dark
    rim), solder drops (light with a glare), burnt dots, a grey film under the stand."""
    rnd = random.Random(seed)
    w, h = L.ROSIN_PX
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # dark film where the unit stood (blurred spot)
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(haze).rounded_rectangle([W * 0.10, H * 0.22, W * 0.60, H * 0.76], radius=W * 0.06,
                                           fill=(40, 36, 30, 40))
    img = Image.alpha_composite(img, haze.filter(ImageFilter.GaussianBlur(S * 18)))
    # rosin drops - soft blobs of several ellipses: dark rim, amber middle; denser by the soldering iron
    # stand (right), sparser around
    blobs = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blobs)
    core = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(core)
    for _ in range(22):
        if rnd.random() < 0.6:
            x, y = rnd.gauss(0.74, 0.10) * W, rnd.gauss(0.45, 0.16) * H
        else:
            x, y = rnd.uniform(0.08, 0.92) * W, rnd.uniform(0.08, 0.92) * H
        r = rnd.uniform(2.5, 11) * S
        for _k in range(rnd.randint(2, 4)):
            ox, oy = rnd.uniform(-0.6, 0.6) * r, rnd.uniform(-0.6, 0.6) * r
            rx, ry = r * rnd.uniform(0.6, 1.1), r * rnd.uniform(0.5, 0.9)
            bd.ellipse([x + ox - rx, y + oy - ry, x + ox + rx, y + oy + ry], fill=(92, 52, 14, 190))
            cd.ellipse([x + ox - rx * 0.7, y + oy - ry * 0.7, x + ox + rx * 0.7, y + oy + ry * 0.7], fill=(182, 118, 38, 200))
    img = Image.alpha_composite(img, blobs.filter(ImageFilter.GaussianBlur(S * 0.7)))
    img = Image.alpha_composite(img, core.filter(ImageFilter.GaussianBlur(S * 1.2)))
    d = ImageDraw.Draw(img)
    for _ in range(16):
        x, y = rnd.uniform(0.05, 0.95) * W, rnd.uniform(0.05, 0.95) * H
        r = rnd.uniform(1.2, 4.0) * S
        d.ellipse([x - r, y - r, x + r, y + r], fill=(120, 122, 124, 255))
        d.ellipse([x - r * 0.45, y - r * 0.6, x - r * 0.05, y - r * 0.2], fill=(220, 222, 224, 255))
    for _ in range(6):
        x, y = rnd.uniform(0.1, 0.9) * W, rnd.uniform(0.1, 0.9) * H
        r = rnd.uniform(1.5, 3.0) * S
        d.ellipse([x - r, y - r, x + r, y + r], fill=(26, 20, 16, 230))
    save(img, (w, h), "decal_rosin.png")


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    # supply voltmeter (0..30 V) and ammeter (0..3 A)
    for key, fn in (("v", "decal_meter_v.png"), ("a", "decal_meter_a.png")):
        make_meter(fn, L.METERS[key]["labels"], L.METERS[key]["minor"])
    # voltage knob limb: 0..10 along a 270-degree arc
    make_knob_ring("decal_knob_ring.png", 256, [str(i) for i in range(0, 11, 2)], 270.0, color=(226, 224, 214, 255))
    make_vents("decal_vents.png")
    make_pcb()
    make_eop()
    make_rosin()
