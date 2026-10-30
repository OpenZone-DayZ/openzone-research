"""Scales, displays and stencils of the M33 SOP ballistic rack case (system Python + Pillow).
Digits only, no letters: the digits of the scales and displays, the number by stencil,
stripes, "up" arrows. The stencil digits come from M32 (the SOP weapon cabinet sets the
look); the seven-segment digits from M28. Positions are in layout.py.

    python make_decals.py      -> ../work/decal_*.png

- decal_meter_a..d.png    scales of the dial meters (window 66 x 56): a 90 degree arc, ticks,
                          digits; no needle on them - the needle is a separate part (bone
                          ozl_work);
- decal_lcd_off.png,      both displays as one 512 x 512 picture (the time meter window at
  decal_lcd_f00..f16.png  the top, the speed one at the bottom, layout.LCD_RECTS): "off" - a
                          dark red filter, the segment shadows are visible; "working" frames:
                          the meter shows the flight time over the sensor base, us
                          ("00419.6"), the control unit shows the speed, m/s; shot stages -
                          "ready" (zeros and dashes), counting (the time grows), result (time
                          and speed); the show order is LCD_SEQ;
- decal_side_num.png      case number in white paint by stencil on the right side;
- decal_side_band.png     two white stripes under the number;
- decal_lid.png           lid: a frame for the marking (blank, with a number), "up" arrows.
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 2                                   # supersampling, then downscaled - smooth edges
PX_M = 1400                             # pixels per meter (before downscaling)
K = PX_M * S
K2 = K * 2                              # scales and displays are small: twice the density
FONTS = "C:/Windows/Fonts/"
WHITE = (214, 212, 200)
BLACK = (22, 22, 22)
RED = (180, 34, 28)
FACE = (230, 228, 216)

# Stencil digits on a 6 x 10 grid - from M32 (unit = stroke width, 1/6 of the width)
DIGITS = {
    "0": [(0, 1, 1.2, 4.6), (0, 5.4, 1.2, 9), (4.8, 1, 6, 4.6), (4.8, 5.4, 6, 9), (1, 0, 5, 1.2), (1, 8.8, 5, 10)],
    "1": [(2.4, 0, 3.8, 4.6), (2.4, 5.4, 3.8, 10), (1.2, 0.6, 2.3, 1.8)],
    "2": [(0.4, 0, 5, 1.2), (4.8, 1, 6, 4.4), (0.6, 4.2, 5.4, 5.4), (0, 5.6, 1.2, 8.8), (0, 8.8, 6, 10)],
    "3": [(0.2, 0, 5, 1.2), (4.8, 1, 6, 4.4), (1.6, 4.4, 5, 5.6), (4.8, 5.6, 6, 9), (0.2, 8.8, 5, 10)],
    "4": [(0, 0, 1.2, 5.6), (0, 5.6, 4.2, 6.8), (3.6, 0, 4.8, 5.3), (3.6, 7.0, 4.8, 10)],
    "5": [(0.4, 0, 6, 1.2), (0, 0.6, 1.2, 4.4), (0.4, 4.2, 5, 5.4), (4.8, 5.6, 6, 9), (0, 8.8, 5, 10)],
    "7": [(0, 0, 4.6, 1.2), (4.8, 0, 6, 2.6), (3.6, 3.2, 4.8, 6.2), (2.6, 6.8, 3.8, 10)],
}


def font(name, h):
    return ImageFont.truetype(FONTS + name, max(8, int(h)))


def save(img, name):
    img = img.resize((img.width // S, img.height // S), Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, img.size)


def worn_mask(W, H, rnd, n, rmin, rmax, blur):
    """Worn-paint patches: 255 - paint intact, 0 - worn off (from M32)."""
    m = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(m)
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        r = rnd.uniform(rmin, rmax)
        d.ellipse((x - r, y - r * rnd.uniform(0.3, 1.0), x + r, y + r * rnd.uniform(0.3, 1.0)), fill=0)
    return m.filter(ImageFilter.GaussianBlur(blur))


def paint(m, rnd, name, col=WHITE, n=60, keep=70):
    """Mask -> white brushed paint: soft edge, worn in places."""
    W, H = m.size
    m = m.filter(ImageFilter.GaussianBlur(1.0 * S))
    m = ImageChops.multiply(m, worn_mask(W, H, rnd, n, 1.5 * S, 7 * S, 1.2 * S).point(
        lambda v: keep + v * (255 - keep) // 255))
    img = Image.new("RGBA", (W, H), col + (0,))
    img.putalpha(m)
    save(img, name)


def stencil_digits(d, text, x, y, cell_h, fill=235):
    u = cell_h / 10.0
    for ch in text:
        for a, b, c, e in DIGITS[ch]:
            d.rectangle((x + a * u, y + b * u, x + c * u, y + e * u), fill=fill)
        x += 7.6 * u


# =============================================================================
# Scales of the dial meters
# =============================================================================
SCALES = {
    # look: (scale end, minor ticks per scale, labels every, red zone from, mirror strip)
    "a": (10, 50, 2, None, False),
    "b": (50, 50, 25, None, False),
    "c": (100, 50, 50, 80, True),
    "d": (30, 30, 10, 27, False),
}


def make_meter(kind):
    """Scale of an M4200-class meter: a 90 degree arc above the needle axis, ticks, digits, some
    with a red zone and a mirror strip; the current type sign (a rhombus) at the bottom left.
    No needle.
    """
    top, n, lab, red, mirror = SCALES[kind]
    W, H = int(L.MW * K2), int(L.MH * K2)
    img = Image.new("RGBA", (W, H), FACE + (255,))
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, H - L.PIVOT_DZ * K2
    R = (L.NEEDLE_L - 0.003) * K2
    half = math.radians(L.ARC_DEG / 2)

    def pt(t, r):
        a = -half + 2 * half * t
        return cx + r * math.sin(a), cy - r * math.cos(a)
    if mirror:
        for i in range(60):
            t0, t1 = i / 60, (i + 1) / 60
            d.polygon([pt(t0, R * 0.80), pt(t1, R * 0.80), pt(t1, R * 0.86), pt(t0, R * 0.86)], fill=(150, 156, 160))
    if red is not None:
        k0 = red / top
        for i in range(20):
            t0, t1 = k0 + (1 - k0) * i / 20, k0 + (1 - k0) * (i + 1) / 20
            d.polygon([pt(t0, R * 0.93), pt(t1, R * 0.93), pt(t1, R * 1.0), pt(t0, R * 1.0)], fill=RED)
    d.arc((cx - R, cy - R, cx + R, cy + R), 270 - L.ARC_DEG / 2, 270 + L.ARC_DEG / 2, fill=BLACK, width=max(2, S))
    for i in range(n + 1):
        v = top * i / n
        major = abs(v / lab - round(v / lab)) < 1e-6
        mid = not major and n % 2 == 0 and i % 5 == 0
        ln = R * (0.13 if major else 0.09 if mid else 0.055)
        d.line([pt(i / n, R), pt(i / n, R - ln)], fill=BLACK, width=max(2, int(W * (0.012 if major else 0.006))))
    f = font("arial.ttf", H * 0.13)
    for v in range(0, top + 1, lab):
        x, y = pt(v / top, R * 0.70)
        s = str(v)
        l, t, rr, b = d.textbbox((0, 0), s, font=f)
        d.text((x - (rr - l) / 2 - l, y - (b - t) / 2 - t), s, font=f, fill=BLACK)
    # current type and accuracy class signs - pictograms without letters: a rhombus and a circle
    s = H * 0.05
    d.polygon([(W * 0.12, H * 0.84 - s), (W * 0.12 + s, H * 0.84), (W * 0.12, H * 0.84 + s), (W * 0.12 - s, H * 0.84)],
              outline=BLACK, width=S)
    d.ellipse((W * 0.86 - s, H * 0.84 - s, W * 0.86 + s, H * 0.84 + s), outline=BLACK, width=S)
    # yellowed scale paper, stains
    rnd = random.Random(ord(kind))
    tint = Image.new("RGBA", (W, H), (210, 196, 150, 0))
    tm = worn_mask(W, H, rnd, 8, 4 * S, 14 * S, 6 * S).point(lambda v: (255 - v) // 5)
    tint.putalpha(tm)
    img = Image.alpha_composite(img, tint)
    save(img, "decal_meter_%s.png" % kind)


# =============================================================================
# Displays: seven-segment LED indicators behind a red filter (both displays are one picture,
# working frames)
# =============================================================================
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
       "7": "abc", "8": "abcdefg", "9": "abcdfg", " ": "", "-": "g"}
# "Off" - a dark red filter under light (the segment shadows are visible); "working" - the
# background and housings are almost black, the shadows dim: the working material glows in the
# game with the texture color x10
LCD_OFF = dict(bg=(44, 12, 12), pkg=(54, 15, 14), ghost=(72, 23, 20))
LCD_ON = dict(bg=(9, 2, 2), pkg=(16, 4, 4), ghost=(32, 8, 7), seg=(255, 52, 30), core=(255, 132, 96),
              glow=(255, 44, 22), haze=(140, 18, 8))
# A shot lasts 3.0 s: 12 records of 0.25 s (OZL_WorkFx: 5 ticks of 0.05 s): "ready" 0.5 s -
# zeros on the meter, dashes on the speed; counting 0.75 s - the time grows; result 1.75 s -
# the flight time over the base and the speed. Four shots, a 12 s cycle. Frame 0 is "ready";
# for shot k frames 1 + 4k..3 + 4k are counting, 4 + 4k is the result
SHOT_V = [715, 711, 719, 708]
COUNT = (0.26, 0.53, 0.79)
LCD_FRAMES = 1 + 4 * len(SHOT_V)                             # build_m33.LCD_FRAMES
LCD_SEQ = [i for k in range(len(SHOT_V)) for i in [0, 0, 1 + 4 * k, 2 + 4 * k, 3 + 4 * k] + [4 + 4 * k] * 7]


def seg_polys(x, y, w, h, t, gap, slant, tw=None):
    """Seven segments of a character in the box x, y, w, h (y down): hexagons along the center
    lines (thickness t, drawn thickness tw) with slanted ends and a gap; slant (a tangent) - the
    top shifts right, the bottom stays.
    """
    k = (t if tw is None else tw) / 2
    xl, xr = x + t / 2, x + w - t / 2
    yt, ym, yb = y + t / 2, y + h / 2, y + h - t / 2

    def hs(yc, xa, xb):
        xa, xb = xa + gap, xb - gap
        return [(xa, yc), (xa + k, yc - k), (xb - k, yc - k), (xb, yc), (xb - k, yc + k), (xa + k, yc + k)]

    def vs(xc, ya, yb_):
        ya, yb_ = ya + gap, yb_ - gap
        return [(xc, ya), (xc + k, ya + k), (xc + k, yb_ - k), (xc, yb_), (xc - k, yb_ - k), (xc - k, ya + k)]
    segs = {"a": hs(yt, xl, xr), "g": hs(ym, xl, xr), "d": hs(yb, xl, xr),
            "f": vs(xl, yt, ym), "b": vs(xr, yt, ym), "e": vs(xl, ym, yb), "c": vs(xr, ym, yb)}
    base = y + h
    return {s: [(px + (base - py) * slant, py) for px, py in pts] for s, pts in segs.items()}


def lcd_window(wm, hm, cells, text, point, on, dens=24000.0, digit_h=0.60, aspect=0.56, pitch=1.40):
    """Display window wm x hm, m, at dens px/m: `cells` character places centered in the window;
    text - a character per place (' ' - the place is dark), point - the place after which the
    dot is lit (None - no dot). on - "working": the characters of text are lit, the other
    segments and dots are shadows; otherwise ("off") - shadows of all segments and the filter
    glare. The window edges are darker - the frame shadow. Returns RGB.
    """
    pal = LCD_ON if on else LCD_OFF
    W, H = int(round(wm * dens)), int(round(hm * dens))
    hd = hm * digit_h * dens
    wd, t = hd * aspect, hd * 0.135
    pt, gap = wd * pitch, t * 0.24
    slant = math.tan(math.radians(8.0))
    x0 = (W - (pt * (cells - 1) + wd + hd * slant)) / 2
    y0 = (H - hd) / 2
    img = Image.new("RGB", (W, H), pal["bg"])
    d = ImageDraw.Draw(img)
    for i in range(cells):                                       # indicator housings
        cx = x0 + i * pt + (wd + hd * slant) / 2
        d.rectangle([cx - pt * 0.47, H / 2 - hd * 0.68, cx + pt * 0.47, H / 2 + hd * 0.68], fill=pal["pkg"])
    lit, core = Image.new("L", (W, H), 0), Image.new("L", (W, H), 0)
    ld, cd = ImageDraw.Draw(lit), ImageDraw.Draw(core)
    for i in range(cells):
        xa = x0 + i * pt
        ch = text[i] if on else " "
        thin = seg_polys(xa, y0, wd, hd, t, gap + t * 0.35, slant, tw=t * 0.40)
        for s, poly in seg_polys(xa, y0, wd, hd, t, gap, slant).items():
            d.polygon(poly, fill=pal["ghost"])
            if s in SEG.get(ch, ""):
                ld.polygon(poly, fill=255)
                cd.polygon(thin[s], fill=255)
        r = t * 0.62                                             # dot after the character
        cy = y0 + hd - r
        cx = xa + wd + (pt - wd) * 0.40 + (y0 + hd - cy) * slant
        dot = [cx - r, cy - r, cx + r, cy + r]
        d.ellipse(dot, fill=pal["ghost"])
        if on and point == i:
            ld.ellipse(dot, fill=255)
            cd.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45], fill=255)
    if on:
        haze = lit.filter(ImageFilter.GaussianBlur(t * 3.0)).point(lambda v: v * 14 // 100)
        near = lit.filter(ImageFilter.GaussianBlur(t * 0.8)).point(lambda v: v * 40 // 100)
        img = Image.composite(Image.new("RGB", (W, H), pal["haze"]), img, haze)
        img = Image.composite(Image.new("RGB", (W, H), pal["glow"]), img, near)
        img = Image.composite(Image.new("RGB", (W, H), pal["seg"]), img, lit)
        img = Image.composite(Image.new("RGB", (W, H), pal["core"]), img,
                              core.filter(ImageFilter.GaussianBlur(t * 0.25)).point(lambda v: v * 55 // 100))
    else:
        hl = Image.new("L", (W, H), 0)
        ImageDraw.Draw(hl).polygon([(W * 0.05, 0), (W * 0.22, 0), (W * 0.12, H), (0, H)], fill=24)
        img = Image.composite(Image.new("RGB", (W, H), (255, 255, 255)), img,
                              hl.filter(ImageFilter.GaussianBlur(H * 0.03)))
    # frame shadow: darker within 5 mm of the window edge
    m = Image.new("L", (160, 40))
    px = m.load()
    for i in range(160):
        for j in range(40):
            e = min((i + 0.5) / 160 * wm, (159.5 - i) / 160 * wm, (j + 0.5) / 40 * hm, (39.5 - j) / 40 * hm)
            px[i, j] = int(255 * (0.66 + 0.34 * min(1.0, e / 0.005)))
    m = m.resize((W, H), Image.BILINEAR)
    return ImageChops.multiply(img, Image.merge("RGB", (m, m, m)))


def make_lcd(name, windows, on):
    """Picture of both displays, LCD_PX x LCD_PX (windows per layout.LCD_RECTS): windows - window
    -> characters by place (the dot is layout.READOUTS[window]["point"]); between the windows -
    background.
    """
    img = Image.new("RGB", (L.LCD_PX, L.LCD_PX), (LCD_ON if on else LCD_OFF)["bg"])
    for key, r in L.READOUTS.items():
        text = windows.get(key, " " * r["n"])
        point = r["point"] if on and key in windows and text.strip("-").strip() else None
        x0, y0, x1, y1 = L.LCD_RECTS[key]
        win = lcd_window(r["w"], r["h"], r["n"], text, point, on,
                         digit_h=0.58 if key == "timer" else 0.60)
        img.paste(win.resize((x1 - x0, y1 - y0), Image.LANCZOS), (x0, y0))
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.convert("RGBA").save(path)
    print("wrote", path, img.size)


def timer_text(us):
    """Flight time, us: "419.6" -> characters for six places with leading zeros (the dot goes
    after the fifth).
    """
    return ("%.1f" % us).replace(".", "").rjust(L.READOUTS["timer"]["n"], "0")


def make_readouts():
    """The off frame and LCD_FRAMES working frames (the show order is LCD_SEQ)."""
    n_sp = L.READOUTS["speed"]["n"]
    make_lcd("decal_lcd_off.png", {}, False)
    make_lcd("decal_lcd_f00.png", {"timer": timer_text(0.0), "speed": "-" * n_sp}, True)
    for k, v in enumerate(SHOT_V):
        us = L.SENSOR_BASE / v * 1e6
        rnd = random.Random(330 + k)
        for j, f in enumerate(COUNT):
            make_lcd("decal_lcd_f%02d.png" % (1 + 4 * k + j),
                     {"timer": timer_text(us * f + rnd.uniform(-6.0, 6.0)), "speed": "-" * n_sp}, True)
        make_lcd("decal_lcd_f%02d.png" % (4 + 4 * k), {"timer": timer_text(us), "speed": str(v).rjust(n_sp)}, True)


# =============================================================================
# Case stencils
# =============================================================================
def make_side():
    rnd = random.Random(33)
    s = L.SIDE_NUM
    W, H = int(s["w"] * K), int(s["h"] * K)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    ch = H * 0.86
    u = ch / 10
    tw = len(s["text"]) * 7.6 * u - 1.6 * u
    stencil_digits(d, s["text"], (W - tw) / 2, (H - ch) / 2, ch)
    paint(m, rnd, "decal_side_num.png")
    b = L.SIDE_BAND
    W, H = int(b["w"] * K), int(b["h"] * K)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    d.rectangle((0, H * 0.05, W, H * 0.38), fill=235)
    d.rectangle((0, H * 0.62, W, H * 0.95), fill=235)
    paint(m, rnd, "decal_side_band.png", n=40)


def make_lid():
    """Lid: a frame for the marking (blank), the case number inside; below - "up" arrows."""
    rnd = random.Random(34)
    c = L.LID_DECAL
    W, H = int(c["w"] * K), int(c["h"] * K)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    lw = int(0.012 * K)
    fx0, fy0, fx1, fy1 = W * 0.06, H * 0.04, W * 0.94, H * 0.52
    d.rectangle((fx0, fy0, fx1, fy1), outline=235, width=lw)
    ch = (fy1 - fy0) * 0.55
    u = ch / 10
    text = L.SIDE_NUM["text"]
    tw = len(text) * 7.6 * u - 1.6 * u
    stencil_digits(d, text, (W - tw) / 2, fy0 + (fy1 - fy0 - ch) / 2, ch)
    # two "up" arrows (a pictogram), a line under them
    for ax in (W * 0.36, W * 0.64):
        aw, ah = W * 0.09, H * 0.30
        top = H * 0.60
        d.polygon([(ax, top), (ax + aw, top + ah * 0.42), (ax + aw * 0.35, top + ah * 0.42),
                   (ax + aw * 0.35, top + ah), (ax - aw * 0.35, top + ah), (ax - aw * 0.35, top + ah * 0.42),
                   (ax - aw, top + ah * 0.42)], fill=235)
    d.rectangle((W * 0.22, H * 0.94, W * 0.78, H * 0.98), fill=235)
    paint(m, rnd, "decal_lid.png", n=90, keep=50)


if __name__ == "__main__":
    for k in SCALES:
        make_meter(k)
    make_readouts()
    make_side()
    make_lid()
