"""Decals for the radio-intercept rack (system Python + Pillow): the scale window of the R-250M2,
its needle gauge, the tuning-knob limb and the subrange table; S-meters of the IC-R7000 and
FRG-7700, knob limbs, the card-reader board, a notepad sheet with frequencies, an inventory tag,
a grounding sign, the loudspeaker grille on the IC-R7000 lid. No letters: only digits, ticks and
grids. The scale window and the S-meters come in two versions: "off" and "working" (backlit). The
S-meter needles and the scale cursor are not in the decals: they are model parts (bones that swing
and creep when "working").

The displays and screens have their own textures: "off" and the frames of "working", which the mod
script (OZL_WorkFx frames) cycles through:
- IC-R7000 display (decal_vfd7_fNN, 8): scans memory channels - the frequency and the channel
  number change, and on one channel the scanner stays for three frames (caught a signal, the busy
  marks light up);
- FRG-7700 display (decal_vfdf_fNN, 6): the operator tunes - the last digit wanders back and forth;
- AR3000A LCD (decal_lcd_fNN, 8): search over the band in 12.5 kHz steps, a level bar;
- PDA screen (decal_pda_fNN, 12): spectrum and waterfall of the intercept - the waterfall creeps
  one row per frame, the rows repeat every 12 frames (the loop seam is invisible).

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscaling - smooth edges
INK = (24, 24, 24, 255)
WHITE = (226, 226, 218, 255)


def font(px, italic=False):
    names = ("ariali.ttf", "arial.ttf") if italic else ("arial.ttf", "consola.ttf")
    for name in names:
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


def glow(img, lay, r):
    img = Image.alpha_composite(img, lay.filter(ImageFilter.GaussianBlur(r)))
    return Image.alpha_composite(img, lay)


# =============================================================================
# R-250M2
# =============================================================================
def make_r250_window(name, on, w=640, h=256):
    """Scale window in a bakelite surround: at the top the subrange drum window (a digit), below it a
    linear 1.5-3.5 MHz scale with ticks every 0.05 and 0.25. The cursor (a red thread) is a model part:
    when "working" it creeps along the scale with the knob rotation. "Working" - the scale is backlit
    with warm light, the ticks are dark; "off" - dark glass, the ticks barely visible."""
    W, H = w * S, h * S
    bg = (212, 176, 104, 255) if on else (40, 34, 28, 255)
    ink = (40, 26, 14, 255) if on else (98, 90, 78, 255)
    img = Image.new("RGBA", (W, H), (14, 12, 10, 255))
    d = ImageDraw.Draw(img)
    # drum window
    d.rectangle([W * 0.30, H * 0.06, W * 0.70, H * 0.40], fill=bg)
    f = font(int(H * 0.26))
    for k, lab in enumerate(("6", "7", "8")):
        d.text((W * (0.38 + 0.12 * k), H * 0.23), lab, fill=ink if k == 1 else ink[:3] + (120,), font=f, anchor="mm")
    # linear scale
    y0, y1 = H * 0.52, H * 0.94
    d.rectangle([W * 0.04, y0, W * 0.96, y1], fill=bg)
    x0, x1 = W * 0.08, W * 0.92
    n = 40
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        big = i % 5 == 0
        d.line([(x, y0 + H * 0.03), (x, y0 + H * (0.20 if big else 0.12))], fill=ink, width=int(S * (2.4 if big else 1.2)))
    fs = font(int(H * 0.14))
    for k in range(5):
        d.text((x0 + (x1 - x0) * k / 4, y0 + H * 0.30), "%.1f" % (1.5 + 0.5 * k), fill=ink, font=fs, anchor="mm")
    if on:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([W * 0.2, H * 0.3, W * 0.8, H * 1.3], fill=(255, 220, 150, 60))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(H * 0.2)))
    save(img, (w, h), name)


def make_meter(name, w, h, labels, face=(232, 226, 206, 255), ink=INK, red_from=None, minor=5, arc=(-138.0, -42.0),
               labels2=None):
    """Face of a needle gauge without the needle (the needle is a bone in the model): an arc with ticks,
    digits; red_from - the fraction of the scale from which the arc is red; the pivot is at the bottom
    center (0.08 of the height below the bottom edge). labels2 - a second scale under the first."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), face)
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, H * 1.08
    r = min(H * 1.10, W * 0.56)
    a0, a1 = arc

    def at(frac, rr):
        a = math.radians(a0 + (a1 - a0) * frac)
        return cx + math.cos(a) * rr, cy + math.sin(a) * rr

    def scale(labs, rr, out):
        n = (len(labs) - 1) * minor
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], a0, a1, fill=ink, width=int(H * 0.012))
        if red_from is not None and out:
            d.arc([cx - rr, cy - rr, cx + rr, cy + rr], a0 + (a1 - a0) * red_from, a1, fill=(178, 34, 26, 255),
                  width=int(H * 0.04))
        for i in range(n + 1):
            big = i % minor == 0
            k = (1.10 if big else 1.05) if out else (0.90 if big else 0.95)
            d.line([at(i / n, rr), at(i / n, rr * k)], fill=ink, width=int(H * (0.020 if big else 0.010)))
        f = font(int(H * 0.13))
        for k, lab in enumerate(labs):
            d.text(at(k / (len(labs) - 1), rr * (1.22 if out else 0.78)), lab, fill=ink, font=f, anchor="mm")
    scale(labels, r * 0.80, True)
    if labels2:
        scale(labels2, r * 0.70, False)
    save(img, (w, h), name)


def make_limb(name, px, n_major=10, minor=10, ink=WHITE):
    """Tuning-knob limb around the full circle: ticks every 1 and 10 divisions, digits 0..90 - on a
    transparent background (laid over a black disc)."""
    n = px * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = n / 2
    tot = n_major * minor
    f = font(int(n * 0.065))
    for i in range(tot):
        a = math.radians(-90 + 360.0 * i / tot)
        big = i % minor == 0
        mid = i % (minor // 2) == 0
        r0 = n * (0.40 if big else (0.43 if mid else 0.45))
        d.line([(c + math.cos(a) * r0, c + math.sin(a) * r0), (c + math.cos(a) * n * 0.48, c + math.sin(a) * n * 0.48)],
               fill=ink, width=int(n * (0.008 if big else 0.004)))
        if big:
            d.text((c + math.cos(a) * n * 0.34, c + math.sin(a) * n * 0.34), str(i // minor * 10), fill=ink, font=f,
                   anchor="mm")
    save(img, (px, px), name)


def make_table(name, w=256, h=320):
    """Subrange table on the panel: 12 rows "number - from-to MHz", digits only."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (200, 198, 186, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([S * 6, S * 6, W - S * 6, H - S * 6], outline=INK, width=S * 3)
    rows = 12
    top = H * 0.08
    d.line([(S * 6, top), (W - S * 6, top)], fill=INK, width=S * 2)
    d.line([(W * 0.26, S * 6), (W * 0.26, H - S * 6)], fill=INK, width=S * 2)
    f = font(int(H * 0.055))
    lo = 1.5
    for k in range(rows):
        y = top + (H - top - S * 6) * (k + 0.5) / rows
        d.text((W * 0.13, y), str(k + 1), fill=INK, font=f, anchor="mm")
        hi = lo + (2.0 if k < 6 else 2.5 + 0.5 * (k - 6))
        d.text((W * 0.63, y), "%.1f - %.1f" % (lo, hi), fill=INK, font=f, anchor="mm")
        lo = hi
    save(img, (w, h), name)


# =============================================================================
# Displays
# =============================================================================
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
       "7": "abc", "8": "abcdefg", "9": "abcdfg", " ": "", "-": "g"}


def segments(base, lay, W, H, text, x0f, x1f, y0f, y1f, color, dim, skew=0.12):
    """Seven-segment digits in the strip x0f..x1f, y0f..y1f (fractions); '.' after a digit is the dot."""
    digits = [c for c in text if c != "."]
    dots, k = set(), 0
    for c in text:
        if c == ".":
            dots.add(k - 1)
        else:
            k += 1
    n = len(digits)
    cw = W * (x1f - x0f) / n
    b, g = ImageDraw.Draw(base), ImageDraw.Draw(lay)
    for i, ch in enumerate(digits):
        xa, xb = W * x0f + i * cw + cw * 0.20, W * x0f + i * cw + cw * 0.72
        ya, ym, yb = H * y0f, H * (y0f + y1f) / 2, H * y1f
        t = max(S * 2, cw * 0.10)
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
        if i in dots and color is not None:
            g.ellipse([xb + cw * 0.06, yb - t, xb + cw * 0.06 + t * 1.3, yb + t * 0.3], fill=color)


def make_vfd(name, w, h, text, small, on, color, dim, bg, marks=(2, 4)):
    """Vacuum fluorescent display: the frequency large, the channel number small on the right, a row of
    short mode indicator strokes on top (no letters): the strokes in marks are lit. The glass edges
    are slightly darker."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), bg)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    col = color if on else None
    segments(img, lay, W, H, text, 0.03, 0.78, 0.30, 0.86, col, dim)
    if small:
        segments(img, lay, W, H, small, 0.82, 0.98, 0.50, 0.86, col, dim)
    g = ImageDraw.Draw(lay)
    for k in range(6):
        x = W * (0.05 + 0.12 * k)
        ImageDraw.Draw(img).rectangle([x, H * 0.08, x + W * 0.06, H * 0.16], fill=dim)
        if on and k in marks:
            g.rectangle([x, H * 0.08, x + W * 0.06, H * 0.16], fill=color)
    img = glow(img, lay, H * 0.05) if on else img
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H], outline=(0, 0, 0, 120), width=int(H * 0.10))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(H * 0.06)))
    save(img, (w, h), name)


def make_lcd(name, w, h, text, on, level=9):
    """Scanner LCD: "working" - yellow-green backlight, black frequency digits and a level bar of
    level divisions (out of 9); "off" - empty gray-green glass."""
    W, H = w * S, h * S
    bg = (168, 186, 92, 255) if on else (74, 80, 66, 255)
    img = Image.new("RGBA", (W, H), bg)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if on:
        ink = (26, 32, 18, 255)
        segments(img, lay, W, H, text, 0.04, 0.80, 0.18, 0.72, ink, (150, 166, 84, 255), skew=0.08)
        g = ImageDraw.Draw(lay)
        for k in range(9):
            x = W * (0.06 + 0.07 * k)
            g.rectangle([x, H * 0.80, x + W * 0.05, H * 0.92], fill=ink if k < level else (150, 166, 84, 255))
        img = Image.alpha_composite(img, lay)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle([0, 0, W, H], outline=(90, 110, 40, 140), width=int(H * 0.12))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(H * 0.08)))
    save(img, (w, h), name)


PDA_ROWS, PDA_LOOP = 26, 12


def pda_row(t, n):
    """Waterfall row at "time" t (modulo PDA_LOOP, so the loop has no seam): which of the n columns
    are lit. Two steady signals and a third that comes and goes."""
    rnd = random.Random(1000 + t % PDA_LOOP)
    on = []
    for k in range(n):
        p = 0.07 + 0.80 * math.exp(-((k - 23) / 2.0) ** 2) + 0.55 * math.exp(-((k - 9) / 1.3) ** 2)
        if (t % PDA_LOOP) in (2, 3, 4, 5, 9):
            p += 0.7 * math.exp(-((k - 32) / 1.2) ** 2)
        on.append(rnd.random() < p)
    return on


def make_pda(name, on, frame=0):
    """Monochrome 160 x 160 PDA LCD: "working" - the spectrum of the intercepted air (bars, peaks at the
    signal frequencies, jittering from frame to frame) and under it a waterfall that creeps down one
    row per frame; a level strip on top; "off" - empty gray-green glass."""
    W = H = 160 * S * 2
    bg = (150, 166, 128) if on else (78, 86, 74)
    img = Image.new("RGBA", (W, H), bg + (255,))
    d = ImageDraw.Draw(img)
    if on:
        ink = (24, 34, 22, 255)
        rnd = random.Random(21 + frame)
        d.rectangle([0, 0, W, H * 0.1], fill=ink)
        d.rectangle([W * 0.05, H * 0.03, W * (0.40 + 0.03 * (frame % 4)), H * 0.07], fill=bg + (255,))
        n = 40
        third = frame % PDA_LOOP in (2, 3, 4, 5, 9)
        for k in range(n):
            x = W * (0.04 + 0.92 * k / n)
            v = 0.10 + 0.08 * rnd.random() + (0.50 + 0.08 * rnd.random()) * math.exp(-((k - 23) / 2.2) ** 2) + \
                (0.22 + 0.06 * rnd.random()) * math.exp(-((k - 9) / 1.5) ** 2) + \
                (0.35 * math.exp(-((k - 32) / 1.3) ** 2) if third else 0.0)
            d.rectangle([x, H * (0.55 - 0.40 * v), x + W * 0.016, H * 0.55], fill=ink)
        d.line([(0, H * 0.56), (W, H * 0.56)], fill=ink, width=S * 2)
        # waterfall: the top row is this frame, the older ones below
        for row in range(PDA_ROWS):
            y = H * (0.60 + 0.38 * row / PDA_ROWS)
            for k, lit in enumerate(pda_row(frame - row, n)):
                if lit:
                    x = W * (0.04 + 0.92 * k / n)
                    d.rectangle([x, y, x + W * 0.018, y + H * 0.010], fill=ink)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H * 0.06], fill=(0, 0, 0, 80))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(H * 0.03)))
    save(img, (256, 256), name)


# =============================================================================
# Small parts
# =============================================================================
def make_knob_ring(name, px, labels, sweep, ink=INK):
    """Limb under a knob: ticks and digits along an arc on a transparent background."""
    n = px * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = n / 2
    k = len(labels)
    start = -90 - sweep / 2
    f = font(int(n * 0.12))
    for i, lab in enumerate(labels):
        a = math.radians(start + sweep * i / (k - 1))
        d.line([(c + math.cos(a) * n * 0.30, c + math.sin(a) * n * 0.30),
                (c + math.cos(a) * n * 0.36, c + math.sin(a) * n * 0.36)], fill=ink, width=int(n * 0.018))
        if lab:
            d.text((c + math.cos(a) * n * 0.44, c + math.sin(a) * n * 0.44), lab, fill=ink, font=f, anchor="mm")
    save(img, (px, px), name)


def make_pcb(name, w=384, h=256, seed=12):
    """Board of the homemade card reader: green mask, hand-drawn traces, pads, outlines of parts
    without letters, a comb of slot contacts at the edge."""
    rnd = random.Random(seed)
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (36, 88, 50, 255))
    d = ImageDraw.Draw(img)
    copper = (180, 150, 72, 255)
    pads = [(rnd.uniform(0.06, 0.94) * W, rnd.uniform(0.08, 0.92) * H) for _ in range(40)]
    for i in range(len(pads) - 1):
        if rnd.random() < 0.75:
            (xa, ya), (xb, yb) = pads[i], pads[(i + rnd.randint(1, 3)) % len(pads)]
            d.line([(xa, ya), (xa, yb), (xb, yb)], fill=copper, width=S * 3)
    for x, y in pads:
        d.ellipse([x - S * 6, y - S * 6, x + S * 6, y + S * 6], fill=copper)
        d.ellipse([x - S * 2, y - S * 2, x + S * 2, y + S * 2], fill=(20, 26, 20, 255))
    for _ in range(5):
        x, y = rnd.uniform(0.1, 0.7) * W, rnd.uniform(0.1, 0.6) * H
        d.rectangle([x, y, x + rnd.uniform(0.12, 0.25) * W, y + rnd.uniform(0.12, 0.22) * H],
                    outline=(214, 220, 206, 255), width=S * 2)
    for i in range(8):
        x = W * (0.30 + 0.05 * i)
        d.rectangle([x, H * 0.02, x + W * 0.025, H * 0.12], fill=(212, 176, 70, 255))
    save(img, (w, h), name)


def make_notepad(name, w=320, h=448, seed=4):
    """Squared notepad sheet: a column of hand-written frequencies and times (digits only), a couple
    circled, one crossed out."""
    rnd = random.Random(seed)
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (226, 222, 204, 255))
    d = ImageDraw.Draw(img)
    step = W / 16
    for i in range(1, 16):
        d.line([(i * step, 0), (i * step, H)], fill=(170, 186, 200, 255), width=S)
    for j in range(1, int(H / step) + 1):
        d.line([(0, j * step), (W, j * step)], fill=(170, 186, 200, 255), width=S)
    blue = (36, 48, 120, 255)
    f = font(int(step * 1.25), italic=True)
    y = step * 1.6
    for k in range(11):
        freq = "%d.%03d" % (rnd.choice((27, 145, 146, 148, 151, 162, 433, 446)), rnd.randrange(0, 1000, 5))
        tm = "%02d.%02d" % (rnd.randrange(6, 23), rnd.randrange(0, 60))
        x = step * (1.2 + rnd.uniform(-0.2, 0.3))
        d.text((x, y), freq, fill=blue, font=f, anchor="lm")
        d.text((W * 0.66, y), tm, fill=blue, font=f, anchor="lm")
        if k in (3, 7):
            d.ellipse([x - step * 0.4, y - step * 0.9, x + step * 6.2, y + step * 0.9], outline=blue, width=S * 3)
        if k == 5:
            d.line([(x - step * 0.2, y + step * 0.1), (x + step * 6.0, y - step * 0.2)], fill=blue, width=S * 3)
        y += step * 1.9
    # ring from a mug
    d.ellipse([W * 0.45, H * 0.70, W * 0.95, H * 1.06], outline=(150, 112, 70, 120), width=S * 6)
    save(img, (w, h), name)


def make_tag(w=280, h=120, number="1183"):
    """Inventory tag (as in M06): aluminum plate, edge rim, stamped digits (no letters)."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (186, 188, 184, 255))
    d = ImageDraw.Draw(img)
    rnd = random.Random(7)
    for _ in range(140):                                    # grinding marks along the plate
        y = rnd.uniform(0, H)
        c = rnd.randint(170, 200)
        d.line([(0, y), (W, y + rnd.uniform(-4, 4))], fill=(c, c + 2, c - 2, 255), width=S)
    d.rounded_rectangle([S * 6, S * 6, W - S * 6, H - S * 6], radius=S * 8, outline=(120, 122, 120, 255), width=S * 3)
    f = font(int(H * 0.52))
    for dx, dy, col in ((S * 2, S * 2, (232, 234, 230, 255)), (0, 0, (70, 72, 70, 255))):
        d.text((W / 2 + dx, H * 0.53 + dy), number, fill=col, font=f, anchor="mm")
    save(img, (w, h), "decal_tag.png")


def make_ground(px=128):
    """Grounding plate (as in M06): the protective earth sign in a circle, black on aluminum."""
    n = px * S
    img = Image.new("RGBA", (n, n), (186, 188, 184, 255))
    d = ImageDraw.Draw(img)
    c = n / 2
    w = int(n * 0.045)
    d.ellipse([n * 0.08, n * 0.08, n * 0.92, n * 0.92], outline=INK, width=w)
    d.line([(c, n * 0.22), (c, n * 0.52)], fill=INK, width=w)
    for k, half in enumerate((0.26, 0.17, 0.08)):
        y = n * (0.52 + 0.11 * k)
        d.line([(c - n * half, y), (c + n * half, y)], fill=INK, width=w)
    save(img, (px, px), "decal_ground.png")


def make_grille(w=512, h=192, nx=40, ny=14):
    """Loudspeaker grille on the IC-R7000 lid: a rectangular field of small round holes on a
    transparent background - dark holes, a light rim on one side."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = min(W / nx, H / ny) * 0.30
    for i in range(nx):
        for j in range(ny):
            x, y = W * (i + 0.5) / nx, H * (j + 0.5) / ny
            d.ellipse([x - r + S, y - r + S, x + r + S, y + r + S], fill=(70, 70, 72, 150))
            d.ellipse([x - r, y - r, x + r, y + r], fill=(6, 6, 7, 255))
    save(img, (w, h), "decal_r7_grille.png")


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    # R-250M2
    make_r250_window("decal_r250_win_off.png", False)
    make_r250_window("decal_r250_win_on.png", True)
    # meter faces keep the proportions of their faces in build_m21.py (M_R, M_7, M_F): the bone needle sweeps along the arc
    make_meter("decal_r250_meter.png", 264, 220, ["0", "1", "2", "3", "4", "5"], face=(236, 232, 218, 255))
    make_limb("decal_r250_limb.png", 512)
    make_table("decal_r250_table.png")
    # IC-R7000: S-meter 1-9, +20..+60 in red, frequency and channel display
    sm = ["1", "3", "5", "7", "9", "+20", "+40", "+60"]
    make_meter("decal_r7000_meter_off.png", 352, 160, sm, face=(150, 140, 110, 255), red_from=4 / 7, minor=2)
    make_meter("decal_r7000_meter_on.png", 352, 160, sm, face=(246, 222, 150, 255), red_from=4 / 7, minor=2)
    # the IC-R7000 display has its own texture: "off" and 8 frames of memory channel scanning (on channel 04
    # the scanner stays for three frames - caught a signal, the busy marks light up)
    v7 = dict(color=(255, 92, 48, 255), dim=(64, 16, 12, 255), bg=(36, 8, 8, 255))
    make_vfd("decal_vfd7_off.png", 448, 160, "        ", "  ", False, None, (52, 14, 12, 255), (30, 8, 8, 255))
    for k, (fq, ch, mk) in enumerate((("145.5000", "01", (2,)), ("145.5250", "02", (2,)), ("146.0000", "03", (2,)),
                                      ("433.9200", "04", (2, 4)), ("433.9200", "04", (2, 4, 5)),
                                      ("433.9200", "04", (2, 4)), ("151.8250", "05", (2,)), ("162.4750", "06", (2,)))):
        make_vfd("decal_vfd7_f%02d.png" % k, 448, 160, fq, ch, True, v7["color"], v7["dim"], v7["bg"], marks=mk)
    # FRG-7700: the S-meter and the (blue-green) display have their own texture: "off" and 6 tuning frames
    fm = ["0", "1", "3", "5", "7", "9", "+30"]
    make_meter("decal_frg_meter_off.png", 320, 192, fm, face=(140, 146, 140, 255), red_from=5 / 6, minor=2)
    make_meter("decal_frg_meter_on.png", 320, 192, fm, face=(214, 240, 236, 255), red_from=5 / 6, minor=2)
    make_vfd("decal_vfdf_off.png", 512, 128, "        ", "  ", False, None, (10, 34, 36, 255), (6, 18, 20, 255))
    for k, last in enumerate("012321"):
        make_vfd("decal_vfdf_f%02d.png" % k, 512, 128, " 9.415." + last, "21", True, (80, 255, 220, 255),
                 (14, 46, 48, 255), (6, 20, 22, 255), marks=(1, 3))
    # AR3000A: the LCD has its own texture: "off" and 8 frames of search in 12.5 kHz steps
    make_lcd("decal_lcd_off.png", 384, 144, "145.5000", False)
    for k, lv in enumerate((2, 3, 2, 6, 8, 7, 3, 2)):
        make_lcd("decal_lcd_f%02d.png" % k, 384, 144, "%.4f" % (145.5 + 0.0125 * k), True, level=lv)
    # PDA: "off" and 12 waterfall frames
    make_pda("decal_pda_off.png", False)
    for k in range(PDA_LOOP):
        make_pda("decal_pda_f%02d.png" % k, True, frame=k)
    # small parts
    make_knob_ring("decal_ring11.png", 256, [str(i) for i in range(11)], 270.0)
    make_knob_ring("decal_ring6.png", 256, ["1", "2", "3", "4", "5", "6"], 150.0)
    make_knob_ring("decal_ring12.png", 256, [str(i) for i in range(1, 13)], 300.0)
    make_knob_ring("decal_ring_w.png", 256, ["", "", "", "", "", "", "", "", ""], 270.0, ink=WHITE)
    make_pcb("decal_reader_pcb.png")
    make_notepad("decal_notepad.png")
    make_tag()
    make_ground()
    make_grille()
