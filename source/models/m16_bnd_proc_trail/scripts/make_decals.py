"""Decals for the drilling machine with a reader (system Python + Pillow): the laptop screen - own
texture: "off" is dark glass, "work" is frames decal_screen_fNN.png along which run lines of a PDA memory
dump (an address and eight bytes in digits), a reading bar grows and a cursor blinks (the frames are
stepped by the mod script, OZL_WorkFx frames); the laptop keyboard (keys without marks), the board of a
disassembled PDA (traces, pads, ICs) and the board of a home-made card reader, the face of a boom box
(two speaker grilles, cassette windows, a tuning scale with frequency digits). No letters or logos: only
digits and scales.

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges


def font(px, mono=False):
    for name in (("consolab.ttf", "cour.ttf") if mono else ()) + ("arialbd.ttf", "arial.ttf"):
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


def make_screen(name, w, h, on):
    """Laptop screen (90s passive matrix): "off" is dark grey glass with a glint, "work" is a dark blue
    field, dump lines (an address and eight bytes in digits), a window frame and a reading bar."""
    W, H = w * S, h * S
    if not on:
        img = Image.new("RGBA", (W, H), (34, 38, 38, 255))
        d = ImageDraw.Draw(img)
        for k in range(12):                              # slanted glint at the top left
            c = 52 - k
            d.line([(0, H * 0.05 + k * S * 3), (W * 0.6 - k * S * 6, 0)], fill=(c, c + 6, c + 6, 255), width=S * 3)
        d.rectangle([0, 0, W - 1, H - 1], outline=(18, 20, 20, 255), width=S * 3)
        save(img, (w, h), name)
        return
    rnd = random.Random(16)
    img = Image.new("RGBA", (W, H), (16, 22, 88, 255))
    d = ImageDraw.Draw(img)
    ink, dim = (196, 206, 214, 255), (120, 132, 170, 255)
    m = W * 0.04
    d.rectangle([m, m, W - m, H - m], outline=ink, width=S * 2)
    d.rectangle([m, m, W - m, m + H * 0.07], fill=(150, 160, 176, 255))
    f = font(int(H * 0.052), mono=True)
    rows = 11
    for r in range(rows):
        y = m + H * 0.11 + r * H * 0.062
        d.text((m * 1.6, y), "%04d" % (r * 16 + 2048), fill=dim, font=f)
        for c in range(8):
            d.text((m * 1.6 + W * 0.15 + c * W * 0.085, y), "%02d" % rnd.randint(0, 99), fill=ink, font=f)
    # reading bar: ~60 % filled
    y0, y1 = H - m - H * 0.10, H - m - H * 0.04
    d.rectangle([m * 2, y0, W - m * 2, y1], outline=ink, width=S * 2)
    d.rectangle([m * 2 + S * 3, y0 + S * 3, m * 2 + (W - m * 4) * 0.62, y1 - S * 3], fill=ink)
    d.text((W - m * 2.4, y0 - H * 0.012), "62", fill=ink, font=f, anchor="rb")
    save(img, (w, h), name)


FRAMES = 12                             # "work" frames: 12 of 0.12 s - a cycle in 1.4 s
ROWS = 12                               # dump rows on the screen (a 13th would lie on the reading bar)


def make_screen_frames(w, h):
    """Work frames (own screen texture): the dump creeps up one row per frame, the bottom row is printed
    byte by byte, the cursor blinks, the reading bar grows. The same layout as make_screen(on=True): the dark
    blue field of a passive matrix, a window frame, a title bar without text."""
    rnd = random.Random(16)
    lines = [["%02d" % rnd.randint(0, 99) for _ in range(8)] for _ in range(ROWS + FRAMES + 1)]
    W, H = w * S, h * S
    ink, dim, bar = (196, 206, 214, 255), (120, 132, 170, 255), (150, 160, 176, 255)
    m = W * 0.04
    f = font(int(H * 0.048), mono=True)
    for fr in range(FRAMES):
        img = Image.new("RGBA", (W, H), (16, 22, 88, 255))
        d = ImageDraw.Draw(img)
        for yy in range(0, H, S * 3):                   # scan lines of the passive matrix
            d.line([(0, yy), (W, yy)], fill=(13, 18, 80, 255), width=S)
        d.rectangle([m, m, W - m, H - m], outline=ink, width=S * 2)
        d.rectangle([m, m, W - m, m + H * 0.07], fill=bar)
        for r in range(ROWS):
            k = fr + r
            y = m + H * 0.10 + r * H * 0.056
            last = r == ROWS - 1
            d.text((m * 1.6, y), "%04d" % (k * 16 + 2048), fill=dim, font=f)
            n = 8 if not last else 1 + (fr * 7) // (FRAMES - 1)          # the bottom row is being printed
            for c in range(n):
                d.text((m * 1.6 + W * 0.15 + c * W * 0.085, y), lines[k][c], fill=ink, font=f)
            if last and fr % 2 == 0:                    # cursor after the last byte
                x = m * 1.6 + W * 0.15 + n * W * 0.085
                d.rectangle([x, y + H * 0.008, x + W * 0.03, y + H * 0.045], fill=ink)
        y0, y1 = H - m - H * 0.10, H - m - H * 0.04
        d.rectangle([m * 2, y0, W - m * 2, y1], outline=ink, width=S * 2)
        p = 0.12 + 0.80 * fr / (FRAMES - 1)
        d.rectangle([m * 2 + S * 3, y0 + S * 3, m * 2 + (W - m * 4) * p, y1 - S * 3], fill=ink)
        d.text((W - m * 2.4, y0 - H * 0.012), "%02d" % int(p * 100), fill=ink, font=f, anchor="rb")
        save(img, (w, h), "decal_screen_f%02d.png" % fr)


def make_keyboard(name, w, h):
    """Laptop keyboard: dark keys without marks, a narrower row of function keys, a long space bar, keys
    in the middle worn to a shine."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (30, 30, 32, 255))
    d = ImageDraw.Draw(img)
    rows = [(15, 0.55)] + [(14, 1.0)] * 4 + [(None, 1.0)]
    hs = sum(r[1] for r in rows)
    y = H * 0.03
    for i, (n, k) in enumerate(rows):
        rh = (H * 0.94) * k / hs
        if n is None:                                    # bottom row: small, space, small
            xs = [(0.0, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0)]
        else:
            xs = [(c / n, (c + 1) / n) for c in range(n)]
        for a, b in xs:
            x0, x1 = W * 0.02 + a * W * 0.96, W * 0.02 + b * W * 0.96
            worn = 0.3 < (a + b) / 2 < 0.6 and 1 <= i <= 4
            col = (70, 70, 72, 255) if worn else (52, 52, 55, 255)
            d.rounded_rectangle([x0 + S * 2, y + S * 2, x1 - S * 2, y + rh - S * 2], radius=S * 2, fill=col)
        y += rh
    save(img, (w, h), name)


def make_pcb(name, w, h, seed, chips):
    """Board: green mask, copper traces, pads, ICs (black packages with leads), a pin comb at the edge -
    the wires are attached to it."""
    rnd = random.Random(seed)
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (28, 84, 46, 255))
    d = ImageDraw.Draw(img)
    cu = (150, 128, 60, 255)
    for _ in range(46):                                  # traces as polylines at 90/45
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        pts = [(x, y)]
        for _k in range(rnd.randint(2, 4)):
            dx, dy = rnd.choice(((1, 0), (0, 1), (1, 1), (-1, 1)))
            L = rnd.uniform(0.05, 0.25) * W
            x, y = x + dx * L, y + dy * L
            pts.append((x, y))
        d.line(pts, fill=(44, 112, 62, 255), width=S * 2)
        d.ellipse([x - S * 3, y - S * 3, x + S * 3, y + S * 3], fill=cu)
    for cx, cy, cw, ch in chips:
        x0, y0, x1, y1 = W * (cx - cw / 2), H * (cy - ch / 2), W * (cx + cw / 2), H * (cy + ch / 2)
        n = max(4, int(cw * 40))
        for k in range(n):                               # leads
            px = x0 + (x1 - x0) * (k + 0.5) / n
            d.rectangle([px - S, y0 - S * 4, px + S, y1 + S * 4], fill=(180, 180, 176, 255))
        d.rectangle([x0, y0, x1, y1], fill=(22, 22, 24, 255))
        d.ellipse([x0 + S * 3, y0 + S * 3, x0 + S * 7, y0 + S * 7], fill=(60, 60, 62, 255))
    for k in range(12):                                  # comb at the edge
        x = W * (0.2 + 0.6 * k / 11)
        d.rectangle([x - S * 3, H * 0.90, x + S * 3, H * 0.98], fill=(206, 170, 70, 255))
    for k in range(4):                                   # mounting holes
        x, y = (W * 0.05, W * 0.95)[k % 2], (H * 0.06, H * 0.94)[k // 2]
        d.ellipse([x - S * 6, y - S * 6, x + S * 6, y + S * 6], fill=cu)
        d.ellipse([x - S * 3, y - S * 3, x + S * 3, y + S * 3], fill=(10, 10, 10, 255))
    save(img, (w, h), name)


def make_boombox(name, w, h):
    """Face of a 90s two-cassette boom box: speaker grilles at the sides, cassette windows in the middle,
    above them a tuning scale with frequency digits, cassette keys below. No brand name."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (36, 36, 38, 255))
    d = ImageDraw.Draw(img)
    for cx in (W * 0.15, W * 0.85):                      # grilles
        r = H * 0.42
        d.ellipse([cx - r, H * 0.5 - r, cx + r, H * 0.5 + r], fill=(24, 24, 26, 255), outline=(90, 90, 92, 255),
                  width=S * 3)
        for yy in range(-10, 11):
            for xx in range(-10, 11):
                px, py = cx + xx * r / 10, H * 0.5 + yy * r / 10
                if math.hypot(px - cx, py - H * 0.5) < r * 0.92:
                    d.ellipse([px - S * 2, py - S * 2, px + S * 2, py + S * 2], fill=(10, 10, 10, 255))
        d.ellipse([cx - r * 0.25, H * 0.5 - r * 0.25, cx + r * 0.25, H * 0.5 + r * 0.25], outline=(70, 70, 72, 255),
                  width=S * 2)
    # tuning scale
    x0, x1, y0, y1 = W * 0.32, W * 0.68, H * 0.08, H * 0.26
    d.rectangle([x0, y0, x1, y1], fill=(196, 186, 150, 255))
    f = font(int(H * 0.07))
    for k, fq in enumerate((88, 92, 96, 100, 104, 108)):
        x = x0 + (x1 - x0) * (0.08 + 0.84 * k / 5)
        d.line([(x, y1 - H * 0.07), (x, y1 - S * 2)], fill=(30, 30, 30, 255), width=S * 2)
        d.text((x, y0 + H * 0.05), str(fq), fill=(30, 30, 30, 255), font=f, anchor="mm")
    d.line([(x0 + (x1 - x0) * 0.47, y0 + S * 2), (x0 + (x1 - x0) * 0.47, y1 - S * 2)], fill=(190, 40, 30, 255),
           width=S * 3)
    # cassette windows
    for k in range(2):
        a = W * (0.33 + 0.18 * k)
        d.rectangle([a, H * 0.33, a + W * 0.16, H * 0.72], fill=(20, 20, 22, 255), outline=(110, 110, 112, 255),
                    width=S * 2)
        d.rectangle([a + W * 0.02, H * 0.42, a + W * 0.14, H * 0.60], fill=(60, 52, 44, 255))
        for cx in (a + W * 0.05, a + W * 0.11):
            d.ellipse([cx - H * 0.04, H * 0.51 - H * 0.04, cx + H * 0.04, H * 0.51 + H * 0.04], fill=(220, 218, 210, 255))
        for j in range(5):                                # keys
            b = a + W * (0.005 + 0.031 * j)
            d.rectangle([b, H * 0.78, b + W * 0.027, H * 0.90], fill=(150, 150, 152, 255))
    save(img, (w, h), name)


if __name__ == "__main__":
    make_screen("decal_screen_off.png", 512, 384, False)
    make_screen_frames(512, 384)
    make_keyboard("decal_kbd.png", 512, 200)
    # memory IC under the spindle (the board centre): the drill enters it (feed)
    make_pcb("decal_pcb.png", 512, 344, 7, [(0.45, 0.47, 0.30, 0.22), (0.80, 0.30, 0.16, 0.16), (0.62, 0.76, 0.22, 0.10)])
    make_pcb("decal_reader.png", 384, 256, 9, [(0.40, 0.45, 0.26, 0.20), (0.75, 0.45, 0.12, 0.12)])
    make_boombox("decal_boombox.png", 1024, 320)
