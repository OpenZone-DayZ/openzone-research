"""Decals of the M79 radio scanner module (system Python + Pillow). No letters: the real AR3000A
labels all keys and knobs, here ticks, brackets and icons stand in for captions:

- front bezel: tick scales around the squelch and volume knobs, "pressed / released" icons by the
  power button, a headphone icon, the column divider lines, "x10" by the step button;
- keypad: an orange line and brackets, orange digits by the keys (as in the photo), short strokes
  instead of captions (orange and light, after the colour of the words in the photo);
- LCD: off (grey-green glass without segments) and 12 frames of the work loop (yellow-green
  backlight: the frequency in seven-segment digits, bank, mode and search icons, S-meter bars,
  scale digits) - m79_layout.LCD_FRAMES; frame 0 is decal_lcd_on.png;
- a masking tape strip on the roof - three frequencies in black marker by hand (digits only);
- rear panel: icons by the connectors (antenna, power polarity, speaker, record), a blank label
  with a number made of digits and strokes.

    python make_decals.py      -> ../work/decal_*.png

Positions come from m79_layout.py (build_m79.py reads the same file).
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m79_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
WHITE = (204, 204, 198, 255)            # bezel print (white in the photo)
ORANGE = (222, 140, 40, 255)            # keypad print (orange in the photo)
GROOVE = (30, 31, 33, 200)


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


class Sheet:
    """Decal canvas for the rectangle (x0, x1) x (z0, z1) in instrument axes; mirror - seen from behind
    (+x on the left).
    """

    def __init__(self, xr, zr, px_mm, mirror=False):
        self.x0, self.x1 = xr
        self.z0, self.z1 = zr
        self.k = px_mm * 1000 * S                        # canvas pixels per metre
        self.W = int(round((self.x1 - self.x0) * self.k))
        self.H = int(round((self.z1 - self.z0) * self.k))
        self.mirror = mirror
        self.img = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def P(self, x, z):
        u = (self.x1 - x) if self.mirror else (x - self.x0)
        return u * self.k, (self.z1 - z) * self.k

    def m(self, metres):
        return metres * self.k

    def line(self, pts, fill, width_m):
        self.d.line([self.P(*p) for p in pts], fill=fill, width=max(1, int(self.m(width_m))))

    def rect(self, x0, z0, x1, z1, fill=None, outline=None, width_m=0.0003):
        (a, b), (c, e) = self.P(x0, z1), self.P(x1, z0)
        self.d.rectangle([min(a, c), b, max(a, c), e], fill=fill, outline=outline,
                         width=max(1, int(self.m(width_m))) if outline else 0)

    def save(self, name):
        save(self.img, (self.W // S, self.H // S), name)


# --- digits: seven-segment (display) and block (keypad print) ------------------------------------
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
       "7": "abc", "8": "abcdefg", "9": "abcdfg", "-": "g"}


def seg_digit(d, x, y, w, h, ch, fill, th, skew=0.12):
    """Seven-segment digit: (x, y) is the top left, w x h, slanted like an LCD."""
    pts = {"a": [(x, y), (x + w, y)], "b": [(x + w, y), (x + w, y + h / 2)], "c": [(x + w, y + h / 2), (x + w, y + h)],
           "d": [(x, y + h), (x + w, y + h)], "e": [(x, y + h / 2), (x, y + h)], "f": [(x, y), (x, y + h / 2)],
           "g": [(x, y + h / 2), (x + w, y + h / 2)]}
    sk = skew * w
    for s in SEG.get(ch, ""):
        (ax, ay), (bx, by) = pts[s]
        d.line([(ax + sk * (1 - 2 * (ay - y) / h), ay), (bx + sk * (1 - 2 * (by - y) / h), by)], fill=fill, width=th)


# block digits of the print: strokes in the 0..1 cell (x to the right, y down)
PRINT = {
    "0": [[(0.15, 0.1), (0.85, 0.1), (0.85, 0.9), (0.15, 0.9), (0.15, 0.1)]],
    "1": [[(0.3, 0.25), (0.55, 0.1), (0.55, 0.9)]],
    "2": [[(0.15, 0.1), (0.85, 0.1), (0.85, 0.5), (0.15, 0.5), (0.15, 0.9), (0.85, 0.9)]],
    "3": [[(0.15, 0.1), (0.85, 0.1), (0.85, 0.9), (0.15, 0.9)], [(0.3, 0.5), (0.85, 0.5)]],
    "4": [[(0.15, 0.1), (0.15, 0.55), (0.85, 0.55)], [(0.7, 0.1), (0.7, 0.9)]],
    "5": [[(0.85, 0.1), (0.15, 0.1), (0.15, 0.5), (0.85, 0.5), (0.85, 0.9), (0.15, 0.9)]],
    "6": [[(0.85, 0.1), (0.15, 0.1), (0.15, 0.9), (0.85, 0.9), (0.85, 0.5), (0.15, 0.5)]],
    "7": [[(0.15, 0.1), (0.85, 0.1), (0.45, 0.9)]],
    "8": [[(0.15, 0.1), (0.85, 0.1), (0.85, 0.9), (0.15, 0.9), (0.15, 0.1)], [(0.15, 0.5), (0.85, 0.5)]],
    "9": [[(0.85, 0.5), (0.15, 0.5), (0.15, 0.1), (0.85, 0.1), (0.85, 0.9), (0.15, 0.9)]],
}


def print_digit(d, cx, cy, h, ch, fill, th):
    """Print digit of height h centred at (cx, cy), width 0.6 h; "." is a square dot."""
    w = h * 0.6
    if ch == ".":
        r = th * 0.9
        d.rectangle([cx - r, cy + h * 0.5 - 2 * r, cx + r, cy + h * 0.5], fill=fill)
        return
    for stroke in PRINT[ch]:
        d.line([(cx - w / 2 + px * w, cy - h / 2 + py * h) for px, py in stroke], fill=fill, width=th, joint="curve")


# hand-written digits (marker) - as in make_decals.py of M75
HAND = {
    "0": [[(0.50, 0.0), (0.12, 0.18), (0.05, 0.55), (0.20, 0.92), (0.55, 1.0), (0.88, 0.75), (0.92, 0.35),
           (0.70, 0.04), (0.45, 0.02)]],
    "1": [[(0.20, 0.25), (0.62, 0.0), (0.55, 1.0)]],
    "2": [[(0.08, 0.25), (0.35, 0.02), (0.75, 0.05), (0.85, 0.32), (0.55, 0.62), (0.05, 1.0), (0.95, 0.96)]],
    "3": [[(0.10, 0.10), (0.55, 0.0), (0.85, 0.20), (0.45, 0.48), (0.88, 0.70), (0.60, 1.0), (0.08, 0.90)]],
    "4": [[(0.62, 1.0), (0.70, 0.0), (0.05, 0.68), (0.98, 0.66)]],
    "5": [[(0.90, 0.02), (0.22, 0.04), (0.15, 0.45), (0.62, 0.40), (0.90, 0.70), (0.55, 1.0), (0.08, 0.88)]],
    "6": [[(0.80, 0.05), (0.30, 0.25), (0.08, 0.70), (0.40, 1.0), (0.85, 0.78), (0.62, 0.48), (0.15, 0.62)]],
    "7": [[(0.05, 0.05), (0.95, 0.02), (0.35, 1.0)], [(0.30, 0.52), (0.78, 0.50)]],
    "8": [[(0.50, 0.48), (0.15, 0.22), (0.48, 0.0), (0.82, 0.20), (0.18, 0.75), (0.48, 1.0), (0.85, 0.75),
           (0.50, 0.48)]],
    "9": [[(0.85, 0.30), (0.50, 0.50), (0.12, 0.30), (0.45, 0.02), (0.85, 0.25), (0.70, 1.0)]],
    ".": [[(0.45, 0.92), (0.55, 1.0)]],
}


def hand_text(d, x, y, h, text, fill, width, rnd, slant=0.18, adv=0.62):
    """A line of hand-written digits: height h, slant, each digit has its own offset and stroke jitter."""
    w = h * 0.55
    for ch in text:
        dy = rnd.uniform(-0.06, 0.06) * h
        for stroke in HAND[ch]:
            pts = []
            for px, py in stroke:
                jx, jy = rnd.uniform(-0.04, 0.04) * w, rnd.uniform(-0.03, 0.03) * h
                pts.append((x + px * w + (1 - py) * slant * h + jx, y + py * h + dy + jy))
            d.line(pts, fill=fill, width=width, joint="curve")
            r = width / 2
            for q in (pts[0], pts[-1]):
                d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=fill)
        x += w * (0.45 if ch == "." else 1.0) + w * adv * 0.4
    return x


def scuff(img, rnd, n, k, alpha=(60, 170)):
    """Print rubbed off by fingers: a mask of patches over the alpha."""
    W, H = img.size
    rub = Image.new("L", (W, H), 255)
    rd = ImageDraw.Draw(rub)
    for _ in range(n):
        cx, cy, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.6, 2.2) * k
        rd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rnd.randint(*alpha))
    rub = rub.filter(ImageFilter.GaussianBlur(0.6 * k))
    img.putalpha(ImageChops.multiply(img.getchannel("A"), rub))


# --- front bezel ----------------------------------------------------------------------------------
def knob_scale(s, c, r0, r1, n, fill):
    """Scale ticks around a knob: from the lower left (225 degrees) over the top to the lower right (-45)."""
    for i in range(n):
        a = math.radians(225.0 - 270.0 * i / (n - 1))
        rr = r1 + (0.0008 if i in (0, n - 1) else 0.0)
        s.line([(c[0] + math.cos(a) * r0, c[1] + math.sin(a) * r0), (c[0] + math.cos(a) * rr, c[1] + math.sin(a) * rr)],
               fill, 0.00035)


def make_bezel(name, px_mm=8):
    s = Sheet((-L.W / 2, L.W / 2), L.BEZ_Z, px_mm)
    # left column: a divider seam and a seam above the headphone jack
    s.line([(L.LEFT_X[1], L.BEZ_Z[0] + 0.002), (L.LEFT_X[1], L.BEZ_Z[1] - 0.002)], GROOVE, 0.0006)
    s.line([(L.LEFT_X[0] + 0.002, L.PHONE_DIV_Z), (L.LEFT_X[1], L.PHONE_DIV_Z)], GROOVE, 0.0006)
    # frame of the right part: a thin seam around the nameplate, display and keypad
    s.rect(L.LEFT_X[1] + 0.0012, L.BEZ_Z[0] + 0.0012, L.W / 2 - 0.0016, L.BEZ_Z[1] - 0.0014, outline=GROOVE,
           width_m=0.0004)
    # power button: a bracket and two icons - "pressed" (filled) and "released" (outline)
    px, pz = L.POWER
    xb = px - L.POWER_WH[0] / 2 - 0.0022
    s.line([(px - L.POWER_WH[0] / 2 + 0.001, pz + 0.0055), (xb, pz + 0.0055), (xb, pz - 0.0045),
            (px - L.POWER_WH[0] / 2 + 0.001, pz - 0.0045)], WHITE, 0.0003)
    for dz, filled in ((0.0062, True), (0.0010, False)):
        x0, z0 = xb - 0.0042, pz + dz - 0.0040
        s.rect(x0, z0 + 0.0008, x0 + 0.0030, z0 + 0.0018, fill=WHITE if filled else None,
               outline=None if filled else WHITE, width_m=0.0002)
        s.line([(x0, z0), (x0 + 0.0030, z0)], WHITE, 0.0002)
    # knob scales
    for c in (L.SQL, L.VOL):
        knob_scale(s, c, L.SKIRT_R + 0.0008, L.SKIRT_R + 0.0022, 11, WHITE)
    # headphone icon: a band and two cups
    cx, cz = L.PHONE_ICON
    r = 0.0030
    (a, b), (c, e) = s.P(cx - r, cz + r + 0.0006), s.P(cx + r, cz - r + 0.0006)
    s.d.arc([a, b, c, e], 180, 360, fill=WHITE, width=int(s.m(0.0004)))
    for sg in (-1, 1):
        s.rect(cx + sg * r - 0.0009, cz - 0.0024, cx + sg * r + 0.0009, cz + 0.0006, fill=WHITE)
    # "x10" by the upper button right of the display (digits are allowed), an arrow "slow" by the
    # lower one
    bx, bz = L.SMALL_BTN[0]
    tx = bx + 0.0045
    s.line([(tx - 0.0008, bz + 0.0008), (tx + 0.0008, bz - 0.0008)], WHITE, 0.0003)
    s.line([(tx - 0.0008, bz - 0.0008), (tx + 0.0008, bz + 0.0008)], WHITE, 0.0003)
    for i, ch in enumerate("10"):
        x, y = s.P(tx + 0.0022 + i * 0.0018, bz)
        print_digit(s.d, x, y, s.m(0.0026), ch, WHITE, int(s.m(0.0003)))
    bx, bz = L.SMALL_BTN[1]
    tx = bx + 0.0045
    s.line([(tx - 0.0008, bz), (tx + 0.0040, bz)], WHITE, 0.0003)
    s.line([(tx + 0.0026, bz + 0.0010), (tx + 0.0040, bz), (tx + 0.0026, bz - 0.0010)], WHITE, 0.0003)
    scuff(s.img, random.Random(791), 40, s.m(0.001))
    s.save(name)


# --- keypad -----------------------------------------------------------------------------------
def make_keypad(name, px_mm=12):
    s = Sheet(L.KEYPAD_X, L.KEYPAD_Z, px_mm)
    rnd = random.Random(792)
    kw, kh = L.KEY_WH
    zl = L.KEYPAD_Z[1] - 0.0025
    s.line([(L.KEYPAD_X[0] + 0.002, zl), (L.KEYPAD_X[1] - 0.0035, zl)], ORANGE, 0.0004)
    s.line([(L.KEYPAD_X[1] - 0.0035, zl), (L.KEYPAD_X[1] - 0.0035, zl - 0.0012)], ORANGE, 0.0004)
    grey = (196, 192, 182, 255)
    keys = [(x, z) for z in L.KEY_ROWS for x in L.KEY_COLS] + L.KEY_EXTRA
    for i, (x, z) in enumerate(keys):
        # short strokes instead of a caption: the first word is often orange (as in the photo)
        zt = z + kh / 2 + 0.0015
        col, row = (i % 5, i // 5) if i < 20 else (None, None)
        first = ORANGE if i >= 20 or col == 1 or (col == 0 and row >= 1) or (col, row) == (4, 3) else grey
        w1 = rnd.uniform(0.0035, 0.0055)
        s.line([(x - kw / 2 + 0.0004, zt), (x - kw / 2 + 0.0004 + w1, zt)], first, 0.0007)
        if i < 20 and rnd.random() < 0.7:
            w2 = rnd.uniform(0.0025, 0.0040)
            x2 = x - kw / 2 + 0.0004 + w1 + 0.0010
            s.line([(x2, zt), (min(x2 + w2, x + kw / 2), zt)], grey, 0.0007)
    # digits by the keys
    th = int(s.m(0.00075))
    for ci, ri, ch in L.KEY_DIGITS:
        x = L.KEY_COLS[ci] + kw / 2 + 0.00155
        z = L.KEY_ROWS[ri] - 0.0003
        px, py = s.P(x, z)
        print_digit(s.d, px, py, s.m(0.0044), ch, ORANGE, th)
    # brackets
    for ri in (0, 3):
        x = L.KEY_COLS[0] - kw / 2 - 0.0014
        z = L.KEY_ROWS[ri]
        s.line([(x, z - 0.0026), (x, z + 0.0030)], ORANGE, 0.0005)
    xe, ze = L.KEY_COLS[4], L.KEY_ROWS[3]
    for sg in (-1, 1):
        x = xe + sg * (kw / 2 + 0.0014)
        s.line([(x, ze - 0.0026), (x, ze + 0.0030)], ORANGE, 0.0005)
    scuff(s.img, rnd, 60, s.m(0.001))
    s.save(name)


# --- LCD display
# ---------------------------------------------------------------------------------------
def make_lcd(name, on, px_mm=10, text="1455250", bars=11, search=False):
    """Bottom of the display window: dark margins of the glass (wider on the left) and the glass itself.
    on - backlight and a reading: frequency text (seven characters, a space is a blanked digit), bars
    of the S-meter, search - the search icon (frames of the work loop - m79_layout.LCD_FRAMES).
    """
    s = Sheet(L.LCD_X, L.LCD_Z, px_mm)
    d, k = s.d, s.m
    bg = (186, 214, 96, 255) if on else (104, 112, 96, 255)
    ink = (34, 44, 28, 255)
    s.rect(L.LCD_X[0], L.LCD_Z[0], L.LCD_X[1], L.LCD_Z[1], fill=(18, 20, 20, 255))
    gx0, gx1 = L.LCD_X[0] + 0.0035, L.LCD_X[1] - 0.0012
    gz0, gz1 = L.LCD_Z[0] + 0.0012, L.LCD_Z[1] - 0.0012
    s.rect(gx0, gz0, gx1, gz1, fill=bg)
    glass = Image.new("RGBA", s.img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glass)
    (a, b), (c, e) = s.P(gx0, gz1), s.P(gx1, gz0)
    if on:
        # backlight: brighter in the middle, darker toward the edges (LEDs at the sides)
        for i in range(12):
            t = i / 11
            gd.rectangle([a + (c - a) * t * 0.45, b, c - (c - a) * t * 0.45, e], fill=(255, 255, 220, int(6 + 4 * t)))
        g = ImageDraw.Draw(s.img)
        # frequency: seven large digits on the right, the dot after the third
        cw, ch, gap = k(0.0042), k(0.0084), k(0.0016)
        x = s.P(gx1 - 0.0016, 0)[0] - len(text) * (cw + gap)
        y = s.P(0, gz0 + 0.0042 + 0.0084)[1]
        for i, c_ in enumerate(text):
            seg_digit(g, x, y, cw, ch, c_, ink, int(k(0.0008)))
            if i == 2:
                g.rectangle([x + cw + gap * 0.15, y + ch - k(0.0010), x + cw + gap * 0.15 + k(0.0010), y + ch], fill=ink)
            x += cw + gap
        # top left: a bank icon - a small digit in a frame, short mode blocks beside it
        bx, by = s.P(gx0 + 0.0020, gz1 - 0.0016)
        g.rectangle([bx, by, bx + k(0.0046), by + k(0.0040)], outline=ink, width=int(k(0.0003)))
        seg_digit(g, bx + k(0.0014), by + k(0.0008), k(0.0016), k(0.0024), "3", ink, int(k(0.00035)))
        for dx, w in ((0.0080, 0.0055), (0.0150, 0.0030), (0.0290, 0.0045)) + (((0.0200, 0.0070),) if search else ()):
            px, py = s.P(gx0 + dx, gz1 - 0.0024)
            g.rectangle([px, py, px + k(w), py + k(0.0011)], fill=ink)
        # S-meter at the bottom: a line, ticks, the level bar, scale digits
        z = gz0 + 0.0022
        x0, x1 = gx0 + 0.0030, gx0 + 0.0400
        s.line([(x0, z), (x1, z)], ink, 0.0003)
        for i in range(9):
            xt = x0 + (x1 - x0) * i / 8
            s.line([(xt, z), (xt, z + 0.0008)], ink, 0.0003)
        for i in range(bars):
            xt = x0 + 0.0003 + i * 0.0021
            s.rect(xt, z + 0.0012, xt + 0.0015, z + 0.0026, fill=ink)
        for i, ch_ in enumerate("1359"):
            px, py = s.P(x0 + (x1 - x0) * (i * 2 + 0.5) / 8, z - 0.0007)
            seg_digit(g, px - k(0.0005), py - k(0.0006), k(0.0010), k(0.0013), ch_, ink, int(k(0.00025)))
    else:
        # blanked glass: the reflection at the top is lighter
        gd.rectangle([a, b, c, b + (e - b) * 0.35], fill=(255, 255, 255, 14))
    s.img.alpha_composite(glass.filter(ImageFilter.GaussianBlur(k(0.0015))))
    # shadow of the bezel's peak at the top
    sh = Image.new("RGBA", s.img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([a, b, c, b + (e - b) * 0.18], fill=(0, 0, 0, 70))
    s.img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(k(0.0008))))
    s.save(name)


# --- tape on the roof
# -----------------------------------------------------------------------------------
def make_tape(name, px_mm=12):
    """Masking tape with three frequencies in marker. The image is a top view (the top of the image faces
    the rear panel); the tape is rotated by TAPE_ROT degrees, transparent around it.
    """
    tw, th = L.TAPE_WH
    k = px_mm * 1000 * S
    W, H = int(tw * k), int(th * k)
    rnd = random.Random(7979)
    tape = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tape)
    poly = [(W * 0.01, H * 0.04), (W * 0.30, 0), (W * 0.62, H * 0.03), (W * 0.99, H * 0.01), (W, H * 0.97),
            (W * 0.70, H), (W * 0.35, H * 0.97), (0, H * 0.99)]
    td.polygon(poly, fill=(212, 200, 158, 255))
    ink = (24, 24, 30, 235)
    y = 0.0022 * k
    for val in ("145.50", "433.92", "27.065"):
        hand_text(td, 0.004 * k, y, 0.0050 * k, val, ink, max(2, int(0.0006 * k)), rnd, slant=0.15, adv=0.5)
        y += 0.0068 * k
    # finger stains and dust along the tape edge
    stain = Image.new("L", tape.size, 0)
    sd = ImageDraw.Draw(stain)
    for _ in range(12):
        x = rnd.uniform(0, W)
        yy = rnd.choice((rnd.uniform(0, H * 0.2), rnd.uniform(H * 0.8, H)))
        r = rnd.uniform(1.5, 4.0) * 0.001 * k
        sd.ellipse([x - r, yy - r, x + r, yy + r], fill=rnd.randint(25, 70))
    stain = stain.filter(ImageFilter.GaussianBlur(0.0015 * k))
    dirty = Image.new("RGBA", tape.size, (96, 86, 66, 255))
    tape = Image.composite(dirty, tape, Image.composite(stain, Image.new("L", tape.size, 0), tape.getchannel("A")))
    tape = tape.rotate(L.TAPE_ROT, resample=Image.BICUBIC, expand=True)      # like the face in build_m79.py
    save(tape, (tape.width // S, tape.height // S), name)


# --- rear panel -----------------------------------------------------------------------------------
def make_rear(name, px_mm=8):
    s = Sheet((-L.CASE_X, L.CASE_X), L.CASE_Z, px_mm, mirror=True)
    d, k = s.d, s.m
    lw = 0.0004
    # antenna by the BNC: a mast with rays
    x, z = L.BNC[0] - 0.0105, L.BNC[1]
    s.line([(x, z - 0.0035), (x, z + 0.0030)], WHITE, lw)
    s.line([(x - 0.0025, z + 0.0030), (x, z), (x + 0.0025, z + 0.0030)], WHITE, lw)
    # power polarity by the 12 V jack: a circle with a dot and two leads
    x, z = L.DCJ[0], L.DCJ[1] + 0.0090
    (a, b), (c, e) = s.P(x - 0.0016, z + 0.0016), s.P(x + 0.0016, z - 0.0016)
    d.ellipse([min(a, c), b, max(a, c), e], outline=WHITE, width=int(k(lw)))
    d.ellipse([min(a, c) + k(0.0011), b + k(0.0011), max(a, c) - k(0.0011), e - k(0.0011)], fill=WHITE)
    for sg in (-1, 1):
        s.line([(x + sg * 0.0016, z), (x + sg * 0.0040, z)], WHITE, lw)
    s.line([(x + 0.0050, z), (x + 0.0064, z)], WHITE, lw)
    s.line([(x - 0.0050, z), (x - 0.0064, z)], WHITE, lw)
    s.line([(x - 0.0057, z - 0.0007), (x - 0.0057, z + 0.0007)], WHITE, lw)
    # speaker by the external speaker jack: a small box and a horn
    x, z = L.EXTSP[0], L.EXTSP[1] + 0.0090
    s.rect(x - 0.0020, z - 0.0010, x - 0.0010, z + 0.0010, outline=WHITE, width_m=lw)
    s.line([(x - 0.0010, z - 0.0010), (x + 0.0012, z - 0.0026), (x + 0.0012, z + 0.0026), (x - 0.0010, z + 0.0010)],
           WHITE, lw)
    # record: a circle with a dot in the centre (record icon)
    x, z = L.RECJ[0], L.RECJ[1] + 0.0090
    (a, b), (c, e) = s.P(x - 0.0019, z + 0.0019), s.P(x + 0.0019, z - 0.0019)
    d.ellipse([min(a, c), b, max(a, c), e], outline=WHITE, width=int(k(lw)))
    d.ellipse([min(a, c) + k(0.0012), b + k(0.0012), max(a, c) - k(0.0012), e - k(0.0012)], fill=WHITE)
    # DB-25 port: a frame icon
    x, z = L.DB25[0], L.DB25[1] + 0.0098
    s.line([(x - 0.006, z), (x + 0.006, z)], WHITE, lw)
    for i in range(5):
        xx = x - 0.005 + i * 0.0025
        s.line([(xx, z), (xx, z - 0.0012)], WHITE, lw)
    # label: silver film, a frame, strokes and a number in digits
    (lx, lz), (lw_, lh) = L.LABEL, L.LABEL_WH
    s.rect(lx - lw_ / 2, lz - lh / 2, lx + lw_ / 2, lz + lh / 2, fill=(178, 180, 178, 255))
    s.rect(lx - lw_ / 2 + 0.0008, lz - lh / 2 + 0.0008, lx + lw_ / 2 - 0.0008, lz + lh / 2 - 0.0008,
           outline=(70, 72, 74, 255), width_m=0.0003)
    rnd = random.Random(793)
    ink = (40, 42, 44, 255)
    for row in range(3):
        zz = lz + lh / 2 - 0.0030 - row * 0.0022
        xx = lx - lw_ / 2 + 0.0022
        for _ in range(4):
            w = rnd.uniform(0.0015, 0.0045)
            s.line([(xx, zz), (min(xx + w, lx + lw_ / 2 - 0.002), zz)], ink, 0.0005)
            xx += w + 0.0012
    # number: print digits
    th = int(k(0.00035))
    for i, ch in enumerate("0473156"):
        px, py = s.P(lx + lw_ / 2 - 0.0035 - i * 0.0026, lz - lh / 2 + 0.0030)     # from behind +x is on the left
        print_digit(d, px, py, k(0.0030), ch, ink, th)
    scuff(s.img, rnd, 30, k(0.001), alpha=(110, 220))
    s.save(name)


if __name__ == "__main__":
    make_bezel("decal_bezel.png")
    make_keypad("decal_keypad.png")
    make_lcd("decal_lcd_off.png", False)
    # frames of the work loop: frame 0 is decal_lcd_on.png, then f01..f11
    for i, (text, bars, search) in enumerate(L.LCD_FRAMES):
        make_lcd("decal_lcd_on.png" if i == 0 else "decal_lcd_f%02d.png" % i, True, text=text, bars=bars,
                 search=search)
    make_tape("decal_tape.png")
    make_rear("decal_rear.png")
