"""Decals for the biosafety cabinet (system Python + Pillow): biohazard sign on a yellow triangle,
dial scale of the airflow gauge, and the control-panel LCD texture. The LCD has an "off" state
(dark glass) and eight "work" frames: airflow speed in large seven-segment digits (0.44-0.46 m/s),
a level bar and a spinning fan icon (the mod's OZL_WorkFx script cycles the frames). No letters:
the mod runs on servers of different languages, so the models carry no readable lettering; digits
on the dial and screen are fine.

    python make_decals.py      -> ../work/decal_biohazard.png, decal_dial.png, decal_lcd_off.png, decal_lcd_fNN.png
"""
import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges


def disc(size, cx, cy, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    return m


def biohazard_mask(n, cx, cy, R):
    """Biohazard sign built the classic way: three crescents (circle minus an offset circle), a ring
    broken near the crescents, a hole in the centre. R is the sign radius."""
    size = (n, n)
    outers = Image.new("L", size, 0)
    inners = Image.new("L", size, 0)
    gaps = Image.new("L", size, 0)
    for k in range(3):
        a = math.radians(-90 + 120 * k)
        ca, sa = math.cos(a), math.sin(a)
        outers = ImageChops.lighter(outers, disc(size, cx + ca * 0.40 * R, cy + sa * 0.40 * R, 0.55 * R))
        inners = ImageChops.lighter(inners, disc(size, cx + ca * 0.64 * R, cy + sa * 0.64 * R, 0.40 * R))
        gaps = ImageChops.lighter(gaps, disc(size, cx + ca * 0.64 * R, cy + sa * 0.64 * R, 0.46 * R))
    # crescents: all outer circles minus ALL inner ones, otherwise a neighbour's outer circle fills the cut-out
    sym = ImageChops.subtract(outers, inners)
    # the ring passes through the crescents and is broken with a gap at their cut-outs
    ring = ImageChops.subtract(disc(size, cx, cy, 0.62 * R), disc(size, cx, cy, 0.50 * R))
    sym = ImageChops.lighter(sym, ImageChops.subtract(ring, gaps))
    return ImageChops.subtract(sym, disc(size, cx, cy, 0.15 * R))


def make_biohazard(px=512):
    n = px * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = 0.04 * n
    tri = [(n / 2, m), (n - m, n - m * 1.6), (m, n - m * 1.6)]
    d.polygon(tri, fill=(20, 18, 16, 255))                       # black border
    inset = 0.075 * n
    cxg = n / 2
    k = inset / math.sin(math.radians(30))
    tri_in = [(cxg, m + k), (n - m - inset * 1.73, n - m * 1.6 - inset), (m + inset * 1.73, n - m * 1.6 - inset)]
    d.polygon(tri_in, fill=(232, 178, 20, 255))                  # yellow
    sym = biohazard_mask(n, n / 2, n * 0.60, n * 0.235)
    black = Image.new("RGBA", (n, n), (20, 18, 16, 255))
    img.paste(black, (0, 0), sym)
    img = img.resize((px, px), Image.LANCZOS)
    # corners are rounded and slightly worn: the alpha along the edge is blurred
    a = img.getchannel("A").filter(ImageFilter.GaussianBlur(0.8))
    img.putalpha(a)
    path = os.path.join(WORK, "decal_biohazard.png")
    img.save(path)
    print("wrote", path)


def make_dial(px=512):
    """Dial scale: cream field, 270-degree arc, major ticks every 10, minor every 2, digits 0..10 at the
    major ticks, red sector at the start (low airflow)."""
    n = px * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = n / 2
    d.ellipse([0, 0, n - 1, n - 1], fill=(28, 28, 28, 255))      # black rim
    d.ellipse([n * 0.05, n * 0.05, n * 0.95, n * 0.95], fill=(232, 226, 205, 255))
    r_out, r_big, r_small = 0.40 * n, 0.31 * n, 0.35 * n
    start, sweep = 135.0, 270.0
    d.arc([c - r_out, c - r_out, c + r_out, c + r_out], start, start + sweep * 0.2, fill=(180, 30, 25, 255),
          width=int(0.035 * n))
    for i in range(51):
        a = math.radians(start + sweep * i / 50)
        r0 = r_big if i % 5 == 0 else r_small
        w = int(0.012 * n) if i % 5 == 0 else int(0.006 * n)
        d.line([(c + math.cos(a) * r0, c + math.sin(a) * r0), (c + math.cos(a) * r_out, c + math.sin(a) * r_out)],
               fill=(25, 25, 25, 255), width=w)
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arial.ttf", int(0.075 * n))
    except OSError:
        font = None
    for i in range(0, 11, 2):
        a = math.radians(start + sweep * i / 10)
        rr = 0.23 * n
        x, y = c + math.cos(a) * rr, c + math.sin(a) * rr
        d.text((x, y), str(i), fill=(25, 25, 25, 255), font=font, anchor="mm")
    img = img.resize((px, px), Image.LANCZOS)
    path = os.path.join(WORK, "decal_dial.png")
    img.save(path)
    print("wrote", path)


LCD_W, LCD_H = 512, 128                 # screen 172 x 44 mm, the same 3.9 : 1
LCD_FRAMES = 8                          # work frames: 8 x 0.25 s, one loop per 2 s
LCD_SPEED = ("045", "045", "046", "046", "045", "044", "044", "045")
LCD_BARS = (7, 8, 8, 9, 8, 7, 7, 8)
# digit segments a..g: (x0, y0, x1, y1) as fractions of the cell (y down); the slant is applied separately
SEG = {"a": (0.16, 0.00, 0.84, 0.10), "b": (0.80, 0.06, 0.92, 0.48), "c": (0.80, 0.52, 0.92, 0.94),
       "d": (0.16, 0.90, 0.84, 1.00), "e": (0.08, 0.52, 0.20, 0.94), "f": (0.08, 0.06, 0.20, 0.48),
       "g": (0.16, 0.45, 0.84, 0.55)}
DIGIT = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
         "7": "abc", "8": "abcdefg", "9": "abcdfg"}


def seven(d, x, y, w, h, ch, ink, ghost=None, slant=0.10):
    """Seven-segment digit in the cell (x, y, w, h); ghost is the colour of the unlit segments (visible on an LCD)."""
    for s, (x0, y0, x1, y1) in SEG.items():
        lit = s in DIGIT.get(ch, "")
        col = ink if lit else ghost
        if col is None:
            continue
        pts = []
        for u, v in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            pts.append((x + w * u + w * slant * (1.0 - v), y + h * v))
        # segment ends are cut to a wedge, like on real LCDs
        cx = sum(p[0] for p in pts) / 4
        cy = sum(p[1] for p in pts) / 4
        horiz = (x1 - x0) > (y1 - y0)
        k = 0.35 * min(w * (x1 - x0), h * (y1 - y0))
        if horiz:
            poly = [(pts[0][0] + k, pts[0][1]), (pts[1][0] - k, pts[1][1]), (pts[1][0], cy), (pts[2][0] - k, pts[2][1]),
                    (pts[3][0] + k, pts[3][1]), (pts[0][0], cy)]
        else:
            poly = [(pts[0][0], pts[0][1] + k), (cx, pts[0][1]), (pts[1][0], pts[1][1] + k), (pts[2][0], pts[2][1] - k),
                    (cx, pts[2][1]), (pts[3][0], pts[3][1] - k)]
        d.polygon(poly, fill=col)


def fan(d, cx, cy, r, ang, ink):
    """Fan icon: three blades around a hub, rotated by ang degrees."""
    for k in range(3):
        a = math.radians(ang + 120 * k)
        pts = []
        for t in range(9):
            q = a + math.radians(-30 + 60 * t / 8)
            rr = r * (0.25 + 0.75 * math.sin(math.pi * t / 8) ** 0.6)
            pts.append((cx + rr * math.cos(q), cy + rr * math.sin(q)))
        d.polygon([(cx, cy)] + pts, fill=ink)
    d.ellipse([cx - r * 0.22, cy - r * 0.22, cx + r * 0.22, cy + r * 0.22], fill=ink)


def lcd_frame(on, fr=0):
    """Control-panel LCD: airflow speed "0.45" in large digits on the left, fan icon and a ten-step level
    bar on the right. Off: dark grey-green glass where only the unlit segments are visible."""
    W, H = LCD_W * S, LCD_H * S
    bg = (158, 186, 92, 255) if on else (40, 46, 40, 255)
    img = Image.new("RGBA", (W, H), bg)
    d = ImageDraw.Draw(img)
    if on:                                       # backlight is brighter toward the middle
        for k in range(24):
            c = tuple(min(255, int(v * (1.0 + 0.10 * (1 - abs(k - 12) / 12.0)))) for v in bg[:3]) + (255,)
            d.rectangle([0, H * k / 24, W, H * (k + 1) / 24], fill=c)
    ink = (22, 30, 18, 255) if on else None
    ghost = (142, 170, 84, 255) if on else (48, 55, 47, 255)
    speed = LCD_SPEED[fr]
    cw, chh = W * 0.115, H * 0.66
    x0, y0 = W * 0.05, H * 0.17
    for i, ch in enumerate(speed):
        seven(d, x0 + i * cw * 1.18, y0, cw, chh, ch if on else "", ink or ghost, ghost)
    # decimal point after the first digit
    px, py = x0 + cw * 1.08, y0 + chh * 0.92
    d.ellipse([px - S * 6, py - S * 6, px + S * 6, py + S * 6], fill=ink or ghost)
    # level bar: ten steps, LCD_BARS[fr] of them lit
    bx0, by1 = W * 0.60, H * 0.84
    for k in range(10):
        bh = H * (0.12 + 0.05 * k)
        col = ink if (on and k < LCD_BARS[fr]) else ghost
        d.rectangle([bx0 + k * W * 0.022, by1 - bh, bx0 + k * W * 0.022 + W * 0.014, by1], fill=col)
    # fan icon: 3 blades repeat every 120 degrees, so 8 frames at 15 degrees (120 / 8) loop seamlessly
    fan(d, W * 0.89, H * 0.48, H * 0.30, 15.0 * fr, ink or ghost)
    d.ellipse([W * 0.89 - H * 0.36, H * 0.12, W * 0.89 + H * 0.36, H * 0.84], outline=ink or ghost, width=S * 3)
    if not on:                                   # faint diagonal glare on the dark glass
        for k in range(16):
            c = 44 + (16 - k) // 4
            d.line([(W * 0.04 + k * S * 5, H), (W * 0.20 + k * S * 5, 0)], fill=(c, c + 5, c, 255), width=S * 4)
    return img.resize((LCD_W, LCD_H), Image.LANCZOS)


def make_lcd():
    lcd_frame(False).save(os.path.join(WORK, "decal_lcd_off.png"))
    print("wrote", os.path.join(WORK, "decal_lcd_off.png"))
    for fr in range(LCD_FRAMES):
        path = os.path.join(WORK, "decal_lcd_f%02d.png" % fr)
        lcd_frame(True, fr).save(path)
        print("wrote", path)


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    make_biohazard()
    make_dial()
    make_lcd()
