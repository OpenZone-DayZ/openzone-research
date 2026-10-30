"""Decals for the diagnostic case (system Python + Pillow): screen of the S1-94 oscilloscope - "off" (dark
CRT without a beam) and "work" frames (the beam runs along the sweep and draws damped oscillations, the
trace fades - afterglow; own screen texture, the frames are stepped by the mod's OZL_WorkFx), the
analogue multimeter scale (no needle - the needle is in the model, bone ozl_needle), a stencil for the
ammo box (stripes and digits), probe board, selector dial on a dark panel, lightning sign. No letters:
only digits, ticks and symbols.

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
INK = (24, 24, 24, 255)
RED = (176, 32, 26, 255)


def font(px, bold=False):
    for name in (("arialbd.ttf",) if bold else ()) + ("arial.ttf", "consola.ttf"):
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


def crt_base(w, h, nx, ny, phosphor, grid):
    """Phosphor and a grid of nx x ny divisions with ticks on the axes (as in M06); returns the image and
    the grid area."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), phosphor)
    d = ImageDraw.Draw(img)
    mx, my = W * 0.04, H * 0.05
    gw, gh = W - 2 * mx, H - 2 * my
    for i in range(nx + 1):
        x = mx + gw * i / nx
        d.line([(x, my), (x, my + gh)], fill=grid, width=S * (2 if i in (0, nx // 2, nx) else 1))
    for j in range(ny + 1):
        y = my + gh * j / ny
        d.line([(mx, y), (mx + gw, y)], fill=grid, width=S * (2 if j in (0, ny // 2, ny) else 1))
    for i in range(nx * 5 + 1):
        x = mx + gw * i / (nx * 5)
        d.line([(x, my + gh / 2 - S * 4), (x, my + gh / 2 + S * 4)], fill=grid, width=S)
    for j in range(ny * 5 + 1):
        y = my + gh * j / (ny * 5)
        d.line([(mx + gw / 2 - S * 4, y), (mx + gw / 2 + S * 4, y)], fill=grid, width=S)
    return img, (mx, my, gw, gh)


def make_crt(name, w, h, trace, nx=10, ny=8, phosphor=(14, 26, 20, 255), beam=(150, 255, 170, 255),
             grid=(70, 110, 90, 255)):
    """CRT screen: grid and the glowing beam trace. trace(t) -> -1..1 vertically, t 0..1 across the width;
    None - the instrument is off, no beam."""
    img, (mx, my, gw, gh) = crt_base(w, h, nx, ny, phosphor, grid)
    if trace is not None:
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        b = ImageDraw.Draw(lay)
        pts = [(mx + gw * k / 600, my + gh / 2 - gh * 0.36 * trace(k / 600)) for k in range(601)]
        b.line(pts, fill=beam, width=S * 3)
        img = Image.alpha_composite(img, lay.filter(ImageFilter.GaussianBlur(S * 4)))
        img = Image.alpha_composite(img, lay)
    save(img, (w, h), name)


def make_crt_frames(prefix, w, h, n, trace, nx=10, ny=8, phosphor=(6, 14, 10, 255), beam=(150, 255, 170),
                    grid=(26, 50, 38, 255), decay=3.2):
    """Work frames: slow sweep - a bright beam spot crosses the screen in n frames, behind it a bright fresh
    trace, farther on it fades (phosphor afterglow, brightness exp(-decay * age)); the trace of the previous
    pass to the right of the spot has almost faded. Frame k - spot at (k + 1) / n of the width.
    The phosphor and grid of these frames are darker than in "off": the "work" material glows in game with
    the texture colour x10 (kexport.EMISSIVE_GAIN), and a brighter grid such as (70, 110, 90) would burn
    almost like the beam - the running trace would get lost in it."""
    m = 600
    for k in range(n):
        img, (mx, my, gw, gh) = crt_base(w, h, nx, ny, phosphor, grid)
        s = (k + 1) / n
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        b = ImageDraw.Draw(lay)
        pts = [(mx + gw * i / m, my + gh / 2 - gh * 0.36 * trace(i / m)) for i in range(m + 1)]
        for i in range(m):
            age = (s - i / m) % 1.0
            a = int(255 * math.exp(-decay * age))
            if a < 6:
                continue
            b.line([pts[i], pts[i + 1]], fill=beam + (a,), width=S * 3)
        sx, sy = pts[min(m, int(round(s * m)))]
        b.ellipse([sx - S * 5, sy - S * 5, sx + S * 5, sy + S * 5], fill=(220, 255, 228, 255))
        img = Image.alpha_composite(img, lay.filter(ImageFilter.GaussianBlur(S * 4)))
        img = Image.alpha_composite(img, lay)
        save(img, (w, h), "%s%02d.png" % (prefix, k))


def make_meter(name, w, h, pivot, radius, sweep):
    """Scale of a combined instrument (after the Ts4315): white field, three arcs - black (resistance,
    reversed, 0 on the right), black (voltage and current, 0..50) and red (decibels), a mirror strip. The
    needle axis is pivot (fractions of width and height), the radius of the upper arc is a fraction of the
    height, sweep is the full scale angle (symmetric about the vertical). The needle is in the model."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (236, 234, 224, 255))
    d = ImageDraw.Draw(img)
    cx, cy = W * pivot[0], H * pivot[1]
    r = H * radius
    a0, a1 = -90.0 - sweep / 2, -90.0 + sweep / 2

    def at(frac, rr):
        a = math.radians(a0 + (a1 - a0) * frac)
        return cx + math.cos(a) * rr, cy + math.sin(a) * rr

    def arc(rr, col, n, labels, out, minor=5, inverse=False):
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], a0, a1, fill=col, width=int(H * 0.008))
        for i in range(n * minor + 1):
            big = i % minor == 0
            k = (1.07 if big else 1.04) if out else (0.93 if big else 0.96)
            f = i / (n * minor)
            if inverse:
                f = 1.0 - (1.0 - f) ** 1.8                    # ohmmeter scale compressed toward the end
            d.line([at(f, rr), at(f, rr * k)], fill=col, width=int(H * (0.010 if big else 0.005)))
        fnt = font(int(H * 0.075))
        for i, lab in enumerate(labels):
            f = i / (len(labels) - 1)
            if inverse:
                f = 1.0 - (1.0 - f) ** 1.8
            d.text(at(f, rr * (1.15 if out else 0.85)), lab, fill=col, font=fnt, anchor="mm")
    arc(r, INK, 5, ["", "10", "3", "1", "0.3", "0"], True, inverse=True)
    arc(r * 0.84, INK, 5, ["0", "10", "20", "30", "40", "50"], False)
    arc(r * 0.66, RED, 4, ["-15", "-10", "-5", "0", "+2"], False, minor=4)
    d.arc([cx - r * 0.92, cy - r * 0.92, cx + r * 0.92, cy + r * 0.92], a0, a1, fill=(150, 156, 160, 255),
          width=int(H * 0.025))
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 44, 50, 255), width=S * 3)
    save(img, (w, h), name)


def make_stencil(name, w, h):
    """Ammo-box stencil in black paint: a wide stripe, a row of digits (quantity), diamonds - after the
    packing marks of army boxes, no letters. Edges slightly ragged, like paint through a stencil.
    The image lies on the box face from 6 to 116 mm above the bottom (build_m12, STENCIL); the gap between the
    face boards is at 0.44-0.49 of the height from the top: the stripe and "2" on the upper board, "880" on
    the lower one."""
    rnd = random.Random(5)
    W, H = w * S, h * S
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    d.rectangle([W * 0.04, H * 0.07, W * 0.96, H * 0.19], fill=255)
    f2 = font(int(H * 0.27), bold=True)
    d.text((W * 0.64, H * 0.31), "2", fill=255, font=f2, anchor="mm")
    for cx, cy, s in ((W * 0.82, H * 0.31, H * 0.08), (W * 0.84, H * 0.71, H * 0.10)):
        d.polygon([(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)], fill=255)
    f = font(int(H * 0.36), bold=True)
    d.text((W * 0.32, H * 0.71), "880", fill=255, font=f, anchor="mm")
    d.rectangle([W * 0.04, H * 0.91, W * 0.62, H * 0.95], fill=255)
    # stencil bridges and unpainted spots
    for x in (0.30, 0.62):
        d.line([(W * x, H * 0.05), (W * x, H * 0.21)], fill=0, width=S * 3)
    for _ in range(140):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        rr = rnd.uniform(1, 4) * S
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=0)
    m = m.filter(ImageFilter.GaussianBlur(S * 0.8))
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.paste((22, 22, 22, 225), (0, 0), m)
    save(img, (w, h), name)


def make_pcb(name, w=512, h=256, seed=12):
    """Probe board (as in M06): green mask, copper traces and pads, part outlines in silkscreen without letters,
    gold-plated edge connector along the bottom edge (the board stands in the socket by it)."""
    rnd = random.Random(seed)
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (34, 92, 52, 255))
    d = ImageDraw.Draw(img)
    copper = (176, 150, 70, 255)
    silk = (220, 224, 210, 255)
    pads = [(rnd.uniform(0.05, 0.95) * W, rnd.uniform(0.08, 0.78) * H) for _ in range(60)]
    for i in range(len(pads) - 1):
        if rnd.random() < 0.7:
            (xa, ya), (xb, yb) = pads[i], pads[(i + rnd.randint(1, 4)) % len(pads)]
            d.line([(xa, ya), (xb, ya), (xb, yb)], fill=(52, 120, 64, 255), width=S * 5)
            d.line([(xa, ya), (xb, ya), (xb, yb)], fill=copper, width=S * 2)
    for x, y in pads:
        d.ellipse([x - S * 5, y - S * 5, x + S * 5, y + S * 5], fill=copper)
        d.ellipse([x - S * 2, y - S * 2, x + S * 2, y + S * 2], fill=(20, 30, 20, 255))
    for _ in range(10):
        x, y = rnd.uniform(0.06, 0.82) * W, rnd.uniform(0.08, 0.60) * H
        d.rectangle([x, y, x + rnd.uniform(0.06, 0.14) * W, y + rnd.uniform(0.08, 0.16) * H], outline=silk, width=S * 2)
    n = 22
    for i in range(n):
        x = W * (0.08 + 0.84 * (i + 0.5) / n)
        d.rectangle([x - W * 0.012, H * 0.86, x + W * 0.012, H * 0.99], fill=(212, 176, 70, 255))
    save(img, (w, h), name)


def make_ring(name, px, labels, sweep, ink=(226, 226, 216, 255)):
    """Selector dial: ticks and digits along an arc on transparent (lies on the dark panel)."""
    n = px * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = n / 2
    k = len(labels)
    start = -90 - sweep / 2
    f = font(int(n * 0.11))
    for i, lab in enumerate(labels):
        a = math.radians(start + sweep * i / (k - 1))
        d.line([(c + math.cos(a) * n * 0.30, c + math.sin(a) * n * 0.30),
                (c + math.cos(a) * n * 0.36, c + math.sin(a) * n * 0.36)], fill=ink, width=int(n * 0.018))
        if lab:
            d.text((c + math.cos(a) * n * 0.44, c + math.sin(a) * n * 0.44), lab, fill=ink, font=f, anchor="mm")
    save(img, (px, px), name)


def make_bolt(name, px):
    """Electric shock hazard sign: yellow triangle, black border and a lightning bolt."""
    W = px * S
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    tri = [(W * 0.5, W * 0.06), (W * 0.96, W * 0.90), (W * 0.04, W * 0.90)]
    d.polygon(tri, fill=INK)
    inner = [(W * 0.5, W * 0.20), (W * 0.84, W * 0.83), (W * 0.16, W * 0.83)]
    d.polygon(inner, fill=(236, 196, 30, 255))
    bolt = [(W * 0.55, W * 0.32), (W * 0.40, W * 0.58), (W * 0.50, W * 0.58), (W * 0.43, W * 0.79),
            (W * 0.62, W * 0.50), (W * 0.52, W * 0.50), (W * 0.60, W * 0.32)]
    d.polygon(bolt, fill=INK)
    save(img, (px, px), name)


# build_m12: CRT ("work" frames), period 0.05 s (every OZL_WorkFx tick) - one pass takes 1.2 s
CRT_FRAMES = 24


if __name__ == "__main__":
    # S1-94 (screen 60 x 40 mm, 10 x 8 divisions): damped oscillations - checking the circuit on the board;
    # the sweep triggers on the signal edge at 0.06 of the width
    def ring_down(t):
        u = t - 0.06
        return 0.0 if u < 0 else 0.9 * math.exp(-2.6 * u) * math.sin(2 * math.pi * 6.5 * u)
    make_crt("decal_crt_off.png", 384, 256, None, phosphor=(20, 24, 22, 255), grid=(44, 54, 48, 255))
    make_crt_frames("decal_crt_f", 384, 256, CRT_FRAMES, ring_down)
    make_meter("decal_meter.png", 384, 256, (0.5, 0.94), 0.70, 90.0)
    make_stencil("decal_stencil.png", 512, 188)
    make_pcb("decal_pcb.png")
    make_ring("decal_ring.png", 256, ["1", "2", "3", "4", "5", "6", "7", "8"], 210.0)
    make_bolt("decal_bolt.png", 128)
