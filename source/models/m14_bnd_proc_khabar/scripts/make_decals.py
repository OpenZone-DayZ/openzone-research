"""Decals for the buyer's scale (system Python + Pillow): the RP-150Ts13 dial scale (0-150 kg per full
turn, 0.5 kg division, digits every 10 - as in photos of the Ts13 series scale, no inscriptions or
maker's mark), the dosimeter and calculator displays - own textures with "work" frames, the tops of the
money bundles - hryvnias of 100, 200 and 500 UAH (uah.py: size and design by denomination, digits only).
No letters: the displays carry only seven-segment digits and symbols.

    python make_decals.py      -> ../work/decal_*.png

The display is a 256 x 256 square (kmodel stretches it over the display window by UV 0..1): it is drawn
in the window proportions and squeezed into the square. Dosimeter DRG-01T1: the dose rate in four digits
("0.381"), the measuring triangle blinks, a battery bar; "off" is blank glass. Calculator: eight
digits, the entry "4750 x 2 =".
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import uah  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
PX_M = 2400                             # pixels per metre for notes
UAH = (100, 200, 500)                   # bundle denominations on the stool (m14_props.CASH)
INK = (28, 28, 30, 255)
LCD_DOS = (0.062, 0.029)                # dosimeter display window, m (build_m14: LCD)
LCD_CALC = (0.062, 0.020)               # calculator display window (CALC_LCD)
SEGS = {"0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg", "5": "acdfg", "6": "acdefg", "7": "abc",
        "8": "abcdefg", "9": "abcdfg", "-": "g", " ": ""}


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


def make_dial(name, px):
    """Scale: transparent background (the cream enamel with rust from the material shows under it), divisions
    around the circle clockwise from the top: 300 divisions of 0.5 kg, longer every 5 kg, digits every 10.
    Zero is at the top, 150 meets zero ("150 0", like "1000 0" in the photo). The recessed window in the
    centre is not drawn: the RP-150Ts13 mechanism is covered."""
    W = px * S
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = W / 2
    R = W / 2 * 0.93                                     # outer edge of the divisions

    def at(frac, rr):
        a = math.radians(90.0 - 360.0 * frac)
        return c + rr * math.cos(a), c - rr * math.sin(a)
    d.ellipse([c - R, c - R, c + R, c + R], outline=INK, width=S * 2)
    for i in range(300):
        big, mid = i % 20 == 0, i % 10 == 0
        ln = 0.075 if big else (0.055 if mid else 0.03)
        d.line([at(i / 300, R), at(i / 300, R * (1 - ln))], fill=INK, width=S * (3 if big else (2 if mid else 1)))
    f = font(int(W * 0.050))
    for k in range(15):
        txt = "150 0" if k == 0 else str(k * 10)
        d.text(at(k / 15, R * 0.80), txt, fill=INK, font=f, anchor="mm")
    # the inner circle and the "kg" mark are not needed (letters); a blank window nameplate instead
    r2 = R * 0.62
    d.ellipse([c - r2, c - r2, c + r2, c + r2], outline=(60, 58, 54, 255), width=S)
    d.rectangle([c - W * 0.06, c + W * 0.16, c + W * 0.06, c + W * 0.21], outline=INK, width=S * 2)
    save(img, (px, px), name)


def seg_polys(x, y, w, h, t, slant=0.10):
    """Seven segments of a digit in the rectangle x, y, w, h (y down), thickness t, slanted to the right."""
    hw, gap = t / 2, t * 0.18

    def sk(px, py):
        return px + (y + h / 2 - py) * slant, py

    def hseg(cx, cy, L):
        return [sk(*p) for p in ((cx - L / 2, cy), (cx - L / 2 + hw, cy - hw), (cx + L / 2 - hw, cy - hw), (cx + L / 2, cy),
                                 (cx + L / 2 - hw, cy + hw), (cx - L / 2 + hw, cy + hw))]

    def vseg(cx, cy, L):
        return [sk(*p) for p in ((cx, cy - L / 2), (cx + hw, cy - L / 2 + hw), (cx + hw, cy + L / 2 - hw), (cx, cy + L / 2),
                                 (cx - hw, cy + L / 2 - hw), (cx - hw, cy - L / 2 + hw))]
    lh, lv = w - t - 2 * gap, h / 2 - t / 2 - 2 * gap
    return {"a": hseg(x + w / 2, y + hw, lh), "g": hseg(x + w / 2, y + h / 2, lh), "d": hseg(x + w / 2, y + h - hw, lh),
            "f": vseg(x + hw, y + h / 4 + hw / 2, lv), "b": vseg(x + w - hw, y + h / 4 + hw / 2, lv),
            "e": vseg(x + hw, y + 3 * h / 4 - hw / 2, lv), "c": vseg(x + w - hw, y + 3 * h / 4 - hw / 2, lv)}


def lcd_digits(d, text, x0, y0, dw, dh, pitch, t, ink, ghost):
    """A row on the display: digits in segments, the point after a digit; ghost - the colour of unlit segments."""
    cells, i = [], 0
    while i < len(text):
        ch, dp = text[i], i + 1 < len(text) and text[i + 1] == "."
        cells.append((ch, dp))
        i += 2 if dp else 1
    for k, (ch, dp) in enumerate(cells):
        x = x0 + k * pitch
        polys = seg_polys(x, y0, dw, dh, t)
        if ghost:
            for p in polys.values():
                d.polygon(p, fill=ghost)
        for sname in SEGS.get(ch, ""):
            d.polygon(polys[sname], fill=ink)
        r = t * 0.55
        cx, cy = x + dw + (pitch - dw) * 0.45, y0 + dh - r
        if ghost:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ghost)
        if dp:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ink)


def lcd_canvas(size, base, seed):
    """Display field: an even tone, faint blotches (old glass), a dark edge."""
    W, H = size
    img = Image.new("RGBA", (W, H), base)
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(14):
        r = rnd.uniform(0.08, 0.25) * H
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        k = rnd.uniform(-4, 3)
        d.ellipse([x - r * 2, y - r, x + r * 2, y + r], fill=tuple(max(0, min(255, c + int(k))) for c in base[:3]) + (255,))
    img = img.resize((W // 24, H // 24), Image.BILINEAR).resize((W, H), Image.BICUBIC)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=(50, 54, 48, 255), width=max(2, H // 40))
    return img, d


def make_dos_lcd(name, text, mark, base=(150, 160, 136, 255)):
    """DRG-01T1 display: four digits, the measuring triangle (mark), the battery bar; text None - off."""
    H = 256 * S
    W = int(H * LCD_DOS[0] / LCD_DOS[1])
    img, d = lcd_canvas((W, H), base if text else (104, 110, 98, 255), 3)
    ink, ghost = (34, 38, 32, 255), tuple(c - 6 for c in base[:3]) + (255,)
    dh = H * 0.56
    dw, pitch, t = dh * 0.52, dh * 0.74, dh * 0.12
    x0, y0 = W * 0.20, H * 0.20
    if text:
        lcd_digits(d, text, x0, y0, dw, dh, pitch, t, ink, ghost)
        if mark:                                                     # triangle "measuring"
            d.polygon([(W * 0.06, H * 0.30), (W * 0.13, H * 0.30), (W * 0.095, H * 0.42)], fill=ink)
        for k in range(3):                                           # battery: three divisions
            d.rectangle([W * (0.05 + 0.03 * k), H * 0.70, W * (0.07 + 0.03 * k), H * 0.80], fill=ink)
        d.rectangle([W * 0.045, H * 0.68, W * 0.145, H * 0.82], outline=ink, width=S * 2)
    save(img, (256, 256), name)


def make_calc_lcd(name, text, base=(156, 164, 142, 255)):
    """Calculator display: eight digits, the number is pushed to the right; text None - empty (off)."""
    H = 256 * S
    W = int(H * LCD_CALC[0] / LCD_CALC[1])
    img, d = lcd_canvas((W, H), base, 9)
    ink = (30, 34, 30, 255)
    dh = H * 0.62
    dw, pitch, t = dh * 0.50, W * 0.112, dh * 0.11
    if text:
        digits = len(text.replace(".", ""))
        x0 = W * 0.06 + (8 - digits) * pitch
        lcd_digits(d, text, x0, H * 0.19, dw, dh, pitch, t, ink, None)
    save(img, (256, 256), name)


def make_note(den, seed):
    """Top of a bundle: a note of denomination den (uah.py), lies exactly along the axes: the long side
    along x, the top of the picture toward the stool back. The rubber band across the bundle is geometry."""
    w_m, h_m = uah.SIZE[den]
    img = uah.note_image(den, PX_M, seed=seed, wear=0.5, S=S)
    save(img, (int(round(w_m * PX_M)), int(round(h_m * PX_M))), "decal_uah%d.png" % den)


# "work" frames: the dosimeter measures (the readings wander around 0.4), the calculator computes "4750 x 2 ="
DOS_FRAMES = ["0.381", "0.412", "0.398", "0.437", "0.421", "0.395", "0.428", "0.446"]
CALC_FRAMES = ["0.", "4.", "47.", "475.", "4750.", "4750.", "2.", "9500.", "9500.", "9500."]

if __name__ == "__main__":
    make_dial("decal_dial.png", 1024)
    make_dos_lcd("decal_lcd_off.png", None, False)
    for i, v in enumerate(DOS_FRAMES):
        make_dos_lcd("decal_lcd_f%02d.png" % i, v, i % 2 == 0)
    make_calc_lcd("decal_calc_off.png", None)
    for i, v in enumerate(CALC_FRAMES):
        make_calc_lcd("decal_calc_f%02d.png" % i, v)
    for i, den in enumerate(UAH):
        make_note(den, 21 + i)
