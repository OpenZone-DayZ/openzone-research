"""Decals of the ballistic test stand (system Python + Pillow): the faces of three needle gauges, the
CRT screen (an oscillogram of the pulses of two frames) and the speed and shot number display - "off"
and the "working" frames, toggle marks, knob limbs, a printer tape, a rail ruler, yellow-black hazard
hatching. No letters: only digits, ticks, arrows and grids. The needles are not in the decals: they
are model bones.

The "working" frames. A shot is a 5.0 s cycle:
- the CRT screen (own texture, kmodel panels, section crt): 20 distinct frames; "working" plays a
  list of 50 entries of 0.1 s (CRT_SEQ) in four stages:
  1. shot - the sweep is triggered by the pulse of the "start" frame, the beam spot crosses the
     screen in 1 s and draws the pulses of the "start" and "stop" frames (10 frames);
  2. measurement - the sweep is over, the trace stays bright (a storage tube), then cursors appear
     on the pulses and under the trace an interval bracket with the number of microseconds (1.6 s);
  3. the trace fades (0.8 s, 4 frames);
  4. waiting - the triggered sweep runs along an empty line, a pass takes 0.4 s (1.6 s, 4 frames);
- the display (section led, own texture 512 x 512: both windows in one image, the speed window on
  top, the shot number below, LED_RECTS; the unwrap of the parts is set by build_m24, LED_UV) - a
  series of five shots, entries of 1.0 s (LED_SEQ): while the beam runs, the speed window shows
  dashes and the number window shows the number of this shot; when the sweep ends the speed appears.
  The digits are seven-segment: hexagonal segments with slanted ends and gaps, an 8-degree slant,
  each cell has its own indicator body behind a dark red filter, unlit segments are visible as a
  shadow; the glow is narrow, without a red blotch (the "working" material in the game glows with the
  texture color x10, kexport.EMISSIVE_GAIN).

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscaling - smooth edges
INK = (24, 24, 24, 255)
WHITE = (222, 222, 214, 255)
CRT_FRAMES, LED_FRAMES = 20, 10         # distinct frames - build_m24.CRT_FRAMES, LED_FRAMES
# A shot is 5.0 s: the screen has 50 entries of 0.1 s, the display 5 entries of 1.0 s. OZL_WorkFx counts
# in ticks of 0.05 s: 0.1 s is 2 ticks, 1.0 s is 20 (exact in both float32 and double), so the display
# changes exactly at the end of the sweep and does not lag behind the beam. The numbers are frame
# numbers decal_crt_fNN / decal_led_fNN.
CRT_SEQ = list(range(10)) + [10, 10] + [11] * 14 + [12, 12, 13, 13, 14, 14, 15, 15] + [16, 17, 18, 19] * 4
# a series of five shots: bullet speed, m/s; frame k - dashes and the shot number k + 1, frame 5 + k -
# its speed
SHOT_V = [715.4, 712.9, 718.1, 709.6, 716.3]
LED_SEQ = [i for k in range(len(SHOT_V)) for i in [k] + [len(SHOT_V) + k] * 4]


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


def glow(img, lay, r):
    img = Image.alpha_composite(img, lay.filter(ImageFilter.GaussianBlur(r)))
    return Image.alpha_composite(img, lay)


# =============================================================================
# Needle gauges
# =============================================================================
def make_gauge(name, labels, on, sweep=240.0, red_from=None, minor=5, px=256):
    """Round army gauge: a black face, a scale along the arc sweep (zero at the bottom left, growing
    clockwise), light ticks and digits; the pivot is in the center (the needle is a model bone).
    "Working" - a red scale backlight, like night-lit instruments; "off" - light gray ticks."""
    W = px * S
    face = (34, 14, 12, 255) if on else (22, 22, 22, 255)
    ink = (255, 132, 96, 255) if on else (196, 196, 188, 255)
    img = Image.new("RGBA", (W, W), face)
    lay = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    c = W / 2
    a0 = 270.0 - sweep / 2               # zero angle in image axes (y down): bottom left

    def at(frac, rr):
        a = math.radians(a0 + sweep * frac)
        return c + math.cos(a) * rr, c + math.sin(a) * rr
    rr = W * 0.40
    n = (len(labels) - 1) * minor
    box = [c - rr, c - rr, c + rr, c + rr]
    d.arc(box, a0, a0 + sweep, fill=ink, width=int(W * 0.010))
    if red_from is not None:
        d.arc([c - rr * 0.96, c - rr * 0.96, c + rr * 0.96, c + rr * 0.96], a0 + sweep * red_from, a0 + sweep,
              fill=(200, 40, 30, 255), width=int(W * 0.030))
    for i in range(n + 1):
        big = i % minor == 0
        d.line([at(i / n, rr), at(i / n, rr * (0.84 if big else 0.91))], fill=ink, width=int(W * (0.016 if big else 0.008)))
    f = font(int(W * 0.085))
    for k, lab in enumerate(labels):
        d.text(at(k / (len(labels) - 1), rr * 0.66), lab, fill=ink, font=f, anchor="mm")
    img = glow(img, lay, W * 0.012) if on else Image.alpha_composite(img, lay)
    if on:
        sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([W * 0.15, W * 0.1, W * 0.85, W * 0.8], fill=(255, 70, 40, 40))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(W * 0.1)))
    save(img, (px, px), name)


# =============================================================================
# CRT screen: an 8 x 8 grid (100 us per division) and an oscillogram of the pulses of the "start" and "stop" frames
# =============================================================================
G0, G1 = 0.16, 0.84                     # grid field (fractions of the image) inside the screen circle
# frame pulses (fractions of the sweep): "start" on the first division, "stop" 559 us later (a frame base
# of 0.40 m at 715 m/s) - after 5.6 divisions
T_START, T_STOP = 0.12, 0.12 + 0.699
DT_US = 559


def wave(t, idle=False):
    """Signal as a fraction of the height (0 is the top): the baseline at 0.60, frame pulses with
    decaying ringing, noise; idle - an empty line (a triggered sweep, no shot)."""
    y = 0.60
    for t0, a in () if idle else ((T_START, 0.27), (T_STOP, 0.24)):
        dt = t - t0
        y -= a * math.exp(-(dt / 0.010) ** 2)
        if dt > 0:
            y += a * 0.30 * math.exp(-dt / 0.035) * math.sin(dt * 260.0)
    return y + 0.004 * math.sin(t * 190.0) + 0.003 * math.sin(t * 517.0 + 1.3)


def crt_base(on, px=512):
    """Phosphor and grid. In "working" the grid and the background are darker: the "working" material in
    the game glows with the texture color x10, and a brighter grid would burn almost like the beam."""
    W = px * S
    bg = (8, 20, 12, 255) if on else (34, 40, 37, 255)
    img = Image.new("RGBA", (W, W), bg)
    d = ImageDraw.Draw(img)
    grid = (24, 56, 34, 255) if on else (44, 52, 48, 255)
    n = 8
    for k in range(n + 1):
        q = W * (G0 + (G1 - G0) * k / n)
        d.line([(q, W * G0), (q, W * G1)], fill=grid, width=S * 2)
        d.line([(W * G0, q), (W * G1, q)], fill=grid, width=S * 2)
    for j in range(5 * n + 1):
        q = W * (G0 + (G1 - G0) * j / (5 * n))
        d.line([(W * 0.494, q), (W * 0.506, q)], fill=grid, width=S)
        d.line([(q, W * 0.494), (q, W * 0.506)], fill=grid, width=S)
    return img, W


def crt_finish(img, W, on):
    if on:
        sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([W * 0.12, W * 0.12, W * 0.88, W * 0.88], fill=(50, 130, 70, 22))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(W * 0.12)))
    else:
        # highlight on the bulb glass
        sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([W * 0.20, W * 0.12, W * 0.55, W * 0.34], fill=(150, 160, 155, 40))
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(W * 0.05)))
    # dark edge of the bulb, black outside the circle
    mask = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    md = ImageDraw.Draw(mask)
    md.ellipse([W * 0.01, W * 0.01, W * 0.99, W * 0.99], outline=(0, 0, 0, 170), width=int(W * 0.07))
    img = Image.alpha_composite(img, mask.filter(ImageFilter.GaussianBlur(W * 0.03)))
    out = Image.new("RGBA", (W, W), (0, 0, 0, 255))
    circ = Image.new("L", (W, W), 0)
    ImageDraw.Draw(circ).ellipse([0, 0, W, W], fill=255)
    return Image.composite(img, out, circ)


def crt_off(name, px=512):
    img, W = crt_base(False, px)
    save(crt_finish(img, W, False), (px, px), name)


def crt_marks(d, W, a, xy):
    """Measurement marks: cursors on the pulses (dashed over the grid height) and an interval bracket
    under the trace with the number of microseconds; a is the brightness 0..1."""
    col = (150, 255, 160, int(225 * a))
    dim = (150, 255, 160, int(120 * a))
    xs, xe = xy(T_START)[0], xy(T_STOP)[0]
    for x in (xs, xe):
        y = W * (G0 + 0.012)
        while y < W * 0.71:
            d.line([(x, y), (x, min(y + W * 0.014, W * 0.71))], fill=dim, width=S * 2)
            y += W * 0.028
    y = W * 0.775
    d.line([(xs, y), (xe, y)], fill=col, width=S * 3)
    for x in (xs, xe):
        d.line([(x, y - W * 0.028), (x, y + W * 0.028)], fill=col, width=S * 3)
    d.text(((xs + xe) / 2, y - W * 0.020), str(DT_US), fill=col, font=font(int(W * 0.062)), anchor="mb")


def crt_frame(name, head, inten, spot=True, idle=False, marks=0.0, px=512, n=600):
    """A "working" frame: the beam trace from the sweep start to head (a fraction of the width), the trace
    brightness inten(t) 0..1, a light beam spot at head (spot); idle - an empty line; marks - the
    brightness of the measurement marks."""
    img, W = crt_base(True, px)
    lay = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)

    def xy(t):
        return W * (G0 + (G1 - G0) * t), W * wave(t, idle)
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        if t1 > head + 1e-9:
            break
        a = inten((t0 + t1) / 2)
        if a < 0.02:
            continue
        d.line([xy(t0), xy(t1)], fill=(int(90 + 70 * a), 255, int(100 + 70 * a), int(255 * a)), width=S * 4)
    if spot:
        hx, hy = xy(head)
        d.ellipse([hx - S * 7, hy - S * 7, hx + S * 7, hy + S * 7], fill=(220, 255, 220, 255))
    if marks > 0:
        crt_marks(d, W, marks, xy)
    img = glow(img, lay, W * 0.008)
    save(crt_finish(img, W, True), (px, px), name)


def crt_frames():
    """20 "working" frames (display order - CRT_SEQ): 0-9 - the shot (the spot crosses the screen in 1 s),
    10-11 - measurement (the whole trace, then cursors and the bracket), 12-15 - the trace fades, 16-19 -
    the triggered sweep."""
    names = iter(["decal_crt_f%02d.png" % k for k in range(CRT_FRAMES)])
    for i in range(10):
        h = (i + 1) / 10
        crt_frame(next(names), h, lambda t, h=h: max(0.55, math.exp(-(h - t) / 0.6)))
    crt_frame(next(names), 1.0, lambda t: 0.95, spot=False)
    crt_frame(next(names), 1.0, lambda t: 0.95, spot=False, marks=1.0)
    for a, m in ((0.62, 0.6), (0.40, 0.35), (0.22, 0.15), (0.10, 0.0)):
        crt_frame(next(names), 1.0, lambda t, a=a: a, spot=False, marks=m)
    for i in range(4):
        h = (i + 1) / 4
        crt_frame(next(names), h, lambda t, h=h: math.exp(-(h - t) / 0.12), idle=True)
    assert next(names, None) is None


# =============================================================================
# Display: seven-segment LED indicators behind a red filter
# =============================================================================
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
       "7": "abc", "8": "abcdefg", "9": "abcdfg", " ": "", "-": "g"}
LED_PX = 512                            # build_m24: PANELS["led"]["size"]
# display windows, m (build_m24: SPEED, N_SHOTS) and the cells in them; where the windows are in the
# LED_PX x LED_PX image: x0, y0, x1, y1 (pixels, y down): speed on top, shot number below, an 8 px gap
# between them (mip levels do not mix the windows). The UV of the same rectangles is build_m24.LED_UV
LED_WIN = {"speed": (0.170, 0.042, 6), "shots": (0.095, 0.042, 3)}
LED_RECTS = {"speed": (0, 0, 512, 252), "shots": (0, 260, 286, 512)}
# "working": the background and bodies are almost black, segment shadows are dim (in the game everything
# glows x10); "off" - a dark red filter under light, segment shadows visible
LED_ON = dict(bg=(8, 2, 2), pkg=(15, 4, 4), ghost=(32, 8, 7), seg=(255, 46, 26), core=(255, 128, 92),
              glow=(255, 40, 20), haze=(140, 16, 8))
LED_OFF = dict(bg=(30, 9, 8), pkg=(42, 13, 12), ghost=(66, 21, 18))


def seg_polys(x, y, w, h, t, gap, slant, tw=None):
    """Seven segments of a character in the box x, y, w, h (y down): hexagons along the center lines
    (thickness t, drawn tw) with slanted ends and a gap; slant (tangent) - the top goes right, the bottom
    stays."""
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


def led_window(wm, hm, cells, text, point, on, dens=24000.0, digit_h=0.64, aspect=0.56, pitch=1.45):
    """Display window wm x hm, m, at dens px/m: cells character cells in the center of the window; text -
    the character in each cell (' ' - the cell is off), point - the cell after which the dot is lit (None
    - none). on - "working": the characters of text are lit, the other segments and dots are shadows;
    otherwise ("off") - shadows of all segments and the reflection of the filter. The window edges are
    darker - the shadow of the frame. Returns RGB."""
    pal = LED_ON if on else LED_OFF
    W, H = int(round(wm * dens)), int(round(hm * dens))
    hd = hm * digit_h * dens
    wd, t = hd * aspect, hd * 0.135
    pt, gap = wd * pitch, t * 0.24
    slant = math.tan(math.radians(8.0))
    x0 = (W - (pt * (cells - 1) + wd + hd * slant)) / 2
    y0 = (H - hd) / 2
    img = Image.new("RGB", (W, H), pal["bg"])
    d = ImageDraw.Draw(img)
    for i in range(cells):                                       # indicator bodies
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
        ImageDraw.Draw(hl).polygon([(W * 0.06, 0), (W * 0.20, 0), (W * 0.13, H), (-W * 0.01, H)], fill=18)
        img = Image.composite(Image.new("RGB", (W, H), (255, 255, 255)), img,
                              hl.filter(ImageFilter.GaussianBlur(H * 0.04)))
    # frame shadow: darker within 6 mm of the window edge
    m = Image.new("L", (160, 40))
    px = m.load()
    for i in range(160):
        for j in range(40):
            e = min((i + 0.5) / 160 * wm, (159.5 - i) / 160 * wm, (j + 0.5) / 40 * hm, (39.5 - j) / 40 * hm)
            px[i, j] = int(255 * (0.62 + 0.38 * min(1.0, e / 0.006)))
    m = m.resize((W, H), Image.BILINEAR)
    return ImageChops.multiply(img, Image.merge("RGB", (m, m, m)))


def speed_cells(v, cells):
    """Speed "715.4" -> characters by cell from the right (leading cells off) and the dot cell."""
    digits = ("%.1f" % v).replace(".", "")
    return digits.rjust(cells), cells - 2


def make_led(name, windows, on):
    """Display LED_PX x LED_PX: windows by LED_RECTS, windows: window -> (characters by cell, dot cell or
    None); the background between the windows."""
    img = Image.new("RGB", (LED_PX, LED_PX), (LED_ON if on else LED_OFF)["bg"])
    for key, (wm, hm, cells) in LED_WIN.items():
        text, point = windows.get(key, (" " * cells, None))
        x0, y0, x1, y1 = LED_RECTS[key]
        win = led_window(wm, hm, cells, text, point, on)
        img.paste(win.resize((x1 - x0, y1 - y0), Image.LANCZOS), (x0, y0))
    path = os.path.join(WORK, name)
    img.convert("RGBA").save(path)
    print("wrote", path)


def led_frames():
    """10 display frames (display order - LED_SEQ): 0-4 - the beam runs, the speed window shows dashes,
    the shot number 1..5; 5-9 - the speed of that shot."""
    n_sp, n_sh = LED_WIN["speed"][2], LED_WIN["shots"][2]
    for k in range(len(SHOT_V)):
        make_led("decal_led_f%02d.png" % k, {"speed": ("----".rjust(n_sp), None),
                                             "shots": (str(k + 1).rjust(n_sh), None)}, True)
    for k, v in enumerate(SHOT_V):
        make_led("decal_led_f%02d.png" % (len(SHOT_V) + k), {"speed": speed_cells(v, n_sp),
                                                             "shots": (str(k + 1).rjust(n_sh), None)}, True)


# =============================================================================
# Table: toggle marks, limbs; printer tape; ruler; hatching
# =============================================================================
def make_toggle_row(name, n, w=640, h=160):
    """Marks of a toggle row: above each an "up" arrow and a tick, below it a white blank nameplate with
    the channel number. The toggles are at fractions (i + 0.5) / n of the width, at 0.55 of the height."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font(int(H * 0.20))
    for i in range(n):
        x = W * (i + 0.5) / n
        d.polygon([(x, H * 0.04), (x - W * 0.012, H * 0.16), (x + W * 0.012, H * 0.16)], fill=WHITE)
        d.line([(x, H * 0.16), (x, H * 0.26)], fill=WHITE, width=S * 3)
        d.rectangle([x - W * 0.045, H * 0.70, x + W * 0.045, H * 0.96], fill=(206, 204, 196, 255))
        d.text((x, H * 0.83), str(i + 1), fill=INK, font=f, anchor="mm")
    save(img, (w, h), name)


def make_ring(name, px, labels, sweep, ink=WHITE):
    """Limb under a knob: ticks and digits along an arc on a transparent background."""
    n = px * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = n / 2
    k = len(labels)
    start = -90 - sweep / 2
    f = font(int(n * 0.11))
    for i, lab in enumerate(labels):
        a = math.radians(start + sweep * i / (k - 1))
        d.line([(c + math.cos(a) * n * 0.31, c + math.sin(a) * n * 0.31),
                (c + math.cos(a) * n * 0.37, c + math.sin(a) * n * 0.37)], fill=ink, width=int(n * 0.018))
        if lab:
            d.text((c + math.cos(a) * n * 0.44, c + math.sin(a) * n * 0.44), lab, fill=ink, font=f, anchor="mm")
    save(img, (px, px), name)


def make_paper(name, w=128, h=512, seed=24):
    """Printer tape: a column of measurements - shot number and speed, a line, the total (digits only)."""
    rnd = random.Random(seed)
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (232, 230, 220, 255))
    d = ImageDraw.Draw(img)
    f = font(int(W * 0.13))
    y = H * 0.04
    for i in range(1, 11):
        d.text((W * 0.08, y), "%02d %d" % (i, 708 + rnd.randint(0, 14)), fill=(60, 60, 70, 255), font=f)
        y += H * 0.07
    d.line([(W * 0.08, y + H * 0.02), (W * 0.9, y + H * 0.02)], fill=(60, 60, 70, 255), width=S * 2)
    d.text((W * 0.08, y + H * 0.04), "715", fill=(60, 60, 70, 255), font=f)
    d.text((W * 0.08, y + H * 0.11), "6.2", fill=(60, 60, 70, 255), font=f)
    save(img, (w, h), name)


def make_ruler(name, length_cm=80, w=2048, h=40):
    """Steel ruler on the rail: divisions every 1 cm, long ones every 10 cm with digits 0..80 - the
    reading from the muzzle to the frames."""
    W, H = w * S // 2, h * S // 2
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font(int(H * 0.42))
    ink = (28, 28, 30, 255)
    for i in range(length_cm + 1):
        x = W * (0.004 + 0.992 * i / length_cm)
        ln = 0.62 if i % 10 == 0 else (0.42 if i % 5 == 0 else 0.26)
        d.line([(x, 0), (x, H * ln)], fill=ink, width=max(2, S // 2 * (2 if i % 10 == 0 else 1)))
        if i % 10 == 0 and 0 < i < length_cm:
            d.text((x + W * 0.004, H * 0.98), str(i), fill=ink, font=f, anchor="lb")
    save(img, (w, h), name)


def make_hazard(name, w=512, h=96):
    """Yellow-black warning hatching at 45 degrees."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (214, 170, 30, 255))
    d = ImageDraw.Draw(img)
    step = H * 1.0
    x = -H
    while x < W + H:
        d.polygon([(x, H), (x + step / 2, H), (x + step / 2 + H, 0), (x + H, 0)], fill=(20, 20, 20, 255))
        x += step
    save(img, (w, h), name)


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    # bullet speed, m/s; frame supply voltage, V; chamber pressure, hundreds of MPa (notional)
    GAUGES = [(["0", "200", "400", "600", "800", "1000"], 0.8), (["0", "5", "10", "15", "20", "25", "30"], None),
              (["0", "1", "2", "3", "4", "5"], 0.7)]
    for i, (labs, red) in enumerate(GAUGES):
        for st in ("off", "on"):
            make_gauge("decal_gauge%d_%s.png" % (i + 1, st), labs, st == "on", red_from=red,
                       minor=4 if len(labs) > 6 else 5)
    crt_off("decal_crt_off.png")
    crt_frames()
    make_led("decal_led_off.png", {}, False)
    led_frames()
    make_toggle_row("decal_toggles.png", 6)
    make_ring("decal_ring11.png", 256, [str(i) for i in range(11)], 270.0)
    make_ring("decal_ring6.png", 256, ["1", "2", "3", "4", "5", "6"], 150.0)
    make_paper("decal_paper.png")
    make_ruler("decal_ruler.png")
    make_hazard("decal_hazard.png")
