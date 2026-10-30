"""Decals for the chest with the film isolator (system Python + Pillow): the digital thermometer
display - "off" (an empty LCD) and the "work" frames (the temperature digits wander, the measurement
mark blinks; the screen is its own texture with frames), the thermostat knob scale on the panel, a
biohazard sign, an empty inventory tag. No letters: only digits, divisions and a sign.

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges

SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
       "7": "abc", "8": "abcdefg", "9": "abcdfg", "-": "g", " ": ""}
# display frames in "work": the compressor holds minus eighteen, the digit after the point wanders, the
# measurement mark in the corner blinks every other frame (OZL_Work frames, 0.5 s period)
LCD_FRAMES = ["-18.4", "-18.5", "-18.5", "-18.6", "-18.6", "-18.5"]
LCD_PX = (216, 80)                      # display window proportions 86 x 32 mm


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def make_lcd(name, w, h, text, bg, ink, ghost, mark=False):
    """LCD display of the 1990s: a grey-green field, seven-segment digits; ghost is the trace of the
    segments on an empty display, ink - visible digits (None - off, no digits); mark - the measurement
    mark in the top right corner."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), bg)
    d = ImageDraw.Draw(img)
    digits = [c for c in text if c != "."]
    dot = text.index(".") - 1 if "." in text else -1
    cw = W * 0.86 / len(digits)
    for i, ch in enumerate(digits):
        x0 = W * 0.04 + i * cw + cw * 0.22
        x1 = W * 0.04 + i * cw + cw * 0.76
        y0, ym, y1 = H * 0.20, H * 0.50, H * 0.80
        t = int(max(S * 2, cw * 0.11))
        segs = {"a": [(x0, y0), (x1, y0)], "g": [(x0, ym), (x1, ym)], "d": [(x0, y1), (x1, y1)],
                "f": [(x0, y0), (x0, ym)], "b": [(x1, y0), (x1, ym)], "e": [(x0, ym), (x0, y1)],
                "c": [(x1, ym), (x1, y1)]}
        for s, ln in segs.items():
            d.line(ln, fill=ghost, width=t)
            if ink and s in SEG[ch]:
                d.line(ln, fill=ink, width=t)
        if ink and i == dot:
            d.ellipse([x1 + cw * 0.06, y1 - t, x1 + cw * 0.06 + t * 1.2, y1 + t * 0.2], fill=ink)
    # measurement mark: a small square in the corner (the trace is always there, it is visible in the frames with
    # mark)
    mx0, my0 = W * 0.915, H * 0.18
    d.rectangle([mx0, my0, mx0 + W * 0.04, my0 + W * 0.04], fill=ghost)
    if ink and mark:
        d.rectangle([mx0, my0, mx0 + W * 0.04, my0 + W * 0.04], fill=ink)
    # display frame and a light shadow on top (the glass is recessed)
    d.rectangle([0, 0, W - 1, H - 1], outline=(30, 32, 30, 255), width=S * 3)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H * 0.14], fill=(0, 0, 0, 80))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(H * 0.05)))
    save(img, (w, h), name)


def make_panel(name, w, h, knob, lamps):
    """Chest panel face (0.30 x 0.10 m): dark enamel, a thin white frame, the thermostat knob scale - a
    270-degree arc with divisions and digits 1-7 around knob (fractions of width and height), white
    rings around the lamps lamps. No words."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (38, 40, 42, 255))
    d = ImageDraw.Draw(img)
    ink = (214, 214, 206, 255)
    m = S * 6
    d.rounded_rectangle([m, m, W - m, H - m], radius=S * 10, outline=ink, width=S * 2)
    cx, cy = knob[0] * W, (1 - knob[1]) * H
    r0, r1 = H * 0.255, H * 0.305
    for k in range(25):
        a = math.radians(225 - 270 * k / 24)
        long = k % 4 == 0
        ra = r0 if long else r0 + (r1 - r0) * 0.45
        d.line([(cx + ra * math.cos(a), cy - ra * math.sin(a)), (cx + r1 * math.cos(a), cy - r1 * math.sin(a))],
               fill=ink, width=S * (3 if long else 2))
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arialbd.ttf", int(H * 0.10))
    except OSError:
        font = None
    for k in range(7):
        a = math.radians(225 - 270 * k / 6)
        rr = r1 + H * 0.075
        x, y = cx + rr * math.cos(a), cy - rr * math.sin(a)
        d.text((x, y), str(k + 1), fill=ink, font=font, anchor="mm")
    for lx in lamps:
        x = lx * W
        d.ellipse([x - H * 0.17, cy - H * 0.17, x + H * 0.17, cy + H * 0.17], outline=ink, width=S * 2)
    save(img, (w, h), name)


def make_biohazard(name, px):
    """Biohazard sign: black on a yellow triangle with a black border."""
    W = px * S
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = W * 0.03
    tri = [(W / 2, m), (W - m, W - m * 2.2), (m, W - m * 2.2)]
    d.polygon(tri, fill=(20, 20, 20, 255))
    k = W * 0.07
    inner = [(W / 2, m + k * 1.9), (W - m - k * 1.65, W - m * 2.2 - k), (m + k * 1.65, W - m * 2.2 - k)]
    d.polygon(inner, fill=(236, 190, 30, 255))
    cx, cy, r = W / 2, W * 0.60, W * 0.17
    sym = Image.new("L", (W, W), 0)
    s = ImageDraw.Draw(sym)
    for a in (90, 210, 330):
        ox, oy = cx + math.cos(math.radians(a)) * r * 0.62, cy - math.sin(math.radians(a)) * r * 0.62
        s.ellipse([ox - r, oy - r, ox + r, oy + r], fill=255)
    for a in (90, 210, 330):
        ox, oy = cx + math.cos(math.radians(a)) * r * 0.86, cy - math.sin(math.radians(a)) * r * 0.86
        s.ellipse([ox - r * 0.62, oy - r * 0.62, ox + r * 0.62, oy + r * 0.62], fill=0)
    s.ellipse([cx - r * 0.30, cy - r * 0.30, cx + r * 0.30, cy + r * 0.30], fill=0)
    s.ellipse([cx - r * 1.05, cy - r * 1.05, cx + r * 1.05, cy + r * 1.05], outline=255, width=int(r * 0.16))
    for a in (90, 210, 330):
        ox, oy = cx + math.cos(math.radians(a)) * r * 1.0, cy - math.sin(math.radians(a)) * r * 1.0
        s.ellipse([ox - r * 0.13, oy - r * 0.13, ox + r * 0.13, oy + r * 0.13], fill=0)
    img.paste((20, 20, 20, 255), (0, 0), sym)
    save(img, (px, px), name)


def make_tag(name, w, h):
    """Inventory tag without text: an aluminium plate, two rivets, a stamped frame."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (178, 182, 184, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([S * 6, S * 6, W - S * 6, H - S * 6], outline=(120, 124, 128, 255), width=S * 2)
    for x in (S * 14, W - S * 14):
        d.ellipse([x - S * 5, H / 2 - S * 5, x + S * 5, H / 2 + S * 5], fill=(96, 98, 100, 255))
    for i in range(5):
        y = H * (0.3 + 0.1 * i)
        d.line([(W * 0.22, y), (W * 0.78, y)], fill=(150, 154, 156, 255), width=S)
    save(img, (w, h), name)


if __name__ == "__main__":
    w, h = LCD_PX
    make_lcd("decal_lcd_off.png", w, h, "-18.4", (112, 120, 104, 255), None, (104, 112, 97, 255))
    for i, txt in enumerate(LCD_FRAMES):
        make_lcd("decal_lcd_f%02d.png" % i, w, h, txt, (170, 196, 120, 255), (28, 34, 24, 255), (158, 182, 112, 255),
                 mark=i % 2 == 0)
    # panel 0.40..0.70 x 0.66..0.76: thermostat knob at x 0.48, lamps at 0.61 and 0.655, all at z 0.71
    make_panel("decal_panel.png", 600, 200, ((0.48 - 0.40) / 0.30, 0.5), [(0.61 - 0.40) / 0.30, (0.655 - 0.40) / 0.30])
    make_biohazard("decal_biohazard.png", 256)
    make_tag("decal_tag.png", 160, 64)
