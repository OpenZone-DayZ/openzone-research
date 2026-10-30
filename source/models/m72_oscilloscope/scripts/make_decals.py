"""Decals of the M72 oscilloscope module (system Python + Pillow):
- control panel: scales of the "time / div." and "volt / div." switches with digits (like on the
  S1-94), separator lines instead of headings, pictograms at the buttons (power, square wave, edges,
  sine and straight line), a case ground sign by the terminal, arrows at the shift knobs - no letters;
- screen: a green CRT filter with a 10 x 8 division grid, the beam blanked (the "working" frames are
  drawn by m72_screen.py);
- left side: two trimmer holes, a slot; right side: an inventory sticker with a number in digits;
- tray slots and the perforation of the power supply box.

    python make_decals.py      -> ../work/decal_*.png

Sizes and places come from m72_layout.py (the same file is read by build_m72.py).
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import m72_layout as L

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4
INK = (30, 32, 34, 255)
WHITE = (236, 236, 228, 255)


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


class Sheet:
    """Canvas in model metres: (u, v) -> pixels; v is up. ppmm is pixels per millimetre."""

    def __init__(self, u0, u1, v0, v1, ppmm, bg=(0, 0, 0, 0)):
        self.u0, self.v1, self.k = u0, v1, ppmm * 1000.0 * S
        self.size = (int(round((u1 - u0) * ppmm * 1000.0)), int(round((v1 - v0) * ppmm * 1000.0)))
        self.img = Image.new("RGBA", (self.size[0] * S, self.size[1] * S), bg)
        self.d = ImageDraw.Draw(self.img)

    def p(self, u, v):
        return ((u - self.u0) * self.k, (self.v1 - v) * self.k)

    def m(self, x):
        return x * self.k

    def line(self, pts, w, fill=INK):
        self.d.line([self.p(*q) for q in pts], fill=fill, width=max(1, int(round(self.m(w)))))

    def rect(self, u0, v0, u1, v1, fill=None, outline=None, w=0.0003):
        a, b = self.p(u0, v1), self.p(u1, v0)
        self.d.rectangle([a, b], fill=fill, outline=outline, width=max(1, int(round(self.m(w)))) if outline else 0)

    def circle(self, u, v, r, fill=None, outline=None, w=0.0003):
        cu, cv = self.p(u, v)
        rr = self.m(r)
        self.d.ellipse([cu - rr, cv - rr, cu + rr, cv + rr], fill=fill, outline=outline,
                       width=max(1, int(round(self.m(w)))) if outline else 0)

    def text(self, u, v, s, h, fill=INK):
        self.d.text(self.p(u, v), s, fill=fill, font=font(int(self.m(h))), anchor="mm")


def scale(sh, c, labels, r_in, r_out, r_txt, h_txt):
    """Switch scale: ticks at every position along the arc SCALE_A0..A1, digits outside, brackets at the
    ends of the arc - as on the S1-94."""
    cx, cz = c
    n = len(labels)
    for i, lab in enumerate(labels):
        a = math.radians(L.SCALE_A0 + (L.SCALE_A1 - L.SCALE_A0) * i / (n - 1))
        ca, sa = math.cos(a), math.sin(a)
        sh.line([(cx + r_in * ca, cz + r_in * sa), (cx + r_out * ca, cz + r_out * sa)], 0.00045)
        sh.text(cx + r_txt * ca, cz + r_txt * sa, lab, h_txt)
    # bracket arc under the ticks
    pts = []
    for k in range(41):
        a = math.radians(L.SCALE_A0 + (L.SCALE_A1 - L.SCALE_A0) * k / 40)
        pts.append((cx + r_in * math.cos(a), cz + r_in * math.sin(a)))
    sh.line(pts, 0.0003)


def button_icon(sh, u, v, kind):
    """Pictogram on a dark plate to the left of a button (9 x 6 mm)."""
    w, h = 0.0085, 0.0058
    sh.rect(u - w / 2, v - h / 2, u + w / 2, v + h / 2, fill=INK)
    lw = 0.00042
    if kind == "power":                        # an O and a bar - the power sign
        sh.circle(u - 0.0018, v, 0.0016, outline=WHITE, w=lw)
        sh.line([(u + 0.0020, v - 0.0017), (u + 0.0020, v + 0.0017)], lw, WHITE)
    elif kind == "range":                      # square wave of two periods
        sh.line([(u - 0.0038, v - 0.0012), (u - 0.0026, v - 0.0012), (u - 0.0026, v + 0.0012), (u - 0.0014, v + 0.0012),
                 (u - 0.0014, v - 0.0012), (u - 0.0002, v - 0.0012)], lw, WHITE)
        sh.line([(u + 0.0006, v - 0.0012), (u + 0.0012, v - 0.0012), (u + 0.0012, v + 0.0012), (u + 0.0018, v + 0.0012),
                 (u + 0.0018, v - 0.0012), (u + 0.0024, v - 0.0012), (u + 0.0024, v + 0.0012), (u + 0.0030, v + 0.0012),
                 (u + 0.0030, v - 0.0012), (u + 0.0038, v - 0.0012)], lw, WHITE)
    elif kind == "mode":                       # a single pulse and a burst
        sh.line([(u - 0.0038, v - 0.0012), (u - 0.0026, v - 0.0012), (u - 0.0026, v + 0.0012), (u - 0.0016, v + 0.0012),
                 (u - 0.0016, v - 0.0012), (u - 0.0004, v - 0.0012)], lw, WHITE)
        for k in range(3):
            x = u + 0.0006 + 0.0011 * k
            sh.line([(x, v - 0.0012), (x, v + 0.0012)], lw, WHITE)
    elif kind == "slope":                      # rising and falling edges
        sh.line([(u - 0.0038, v - 0.0012), (u - 0.0022, v - 0.0012), (u - 0.0010, v + 0.0012), (u - 0.0002, v + 0.0012)], lw, WHITE)
        sh.line([(u + 0.0006, v + 0.0012), (u + 0.0018, v + 0.0012), (u + 0.0030, v - 0.0012), (u + 0.0038, v - 0.0012)], lw, WHITE)
    elif kind == "source":                     # an arrow into a square and out of it
        sh.rect(u - 0.0036, v - 0.0015, u - 0.0006, v + 0.0015, outline=WHITE, w=lw)
        sh.line([(u + 0.0036, v), (u + 0.0008, v)], lw, WHITE)
        sh.line([(u + 0.0016, v + 0.0008), (u + 0.0008, v), (u + 0.0016, v - 0.0008)], lw, WHITE)
    elif kind == "coupling":                   # a sine and a straight line
        sh.line([(u - 0.0038 + 0.0034 * k / 16, v + 0.0012 * math.sin(2 * math.pi * k / 16)) for k in range(17)], lw, WHITE)
        sh.line([(u + 0.0006, v), (u + 0.0038, v)], lw, WHITE)
        sh.line([(u + 0.0006, v - 0.0012), (u + 0.0038, v - 0.0012)], lw * 0.8, WHITE)


def arrow2(sh, u, v, horiz, size=0.0045):
    """Double arrow (beam shift)."""
    lw, a = 0.0004, 0.0012
    if horiz:
        sh.line([(u - size / 2, v), (u + size / 2, v)], lw)
        for s in (-1, 1):
            sh.line([(u + s * (size / 2 - a), v + a * 0.8), (u + s * size / 2, v), (u + s * (size / 2 - a), v - a * 0.8)], lw)
    else:
        sh.line([(u, v - size / 2), (u, v + size / 2)], lw)
        for s in (-1, 1):
            sh.line([(u - a * 0.8, v + s * (size / 2 - a)), (u, v + s * size / 2), (u + a * 0.8, v + s * (size / 2 - a))], lw)


def make_panel():
    x0, x1 = L.PANEL_X
    z0, z1 = L.PANEL_Z
    sh = Sheet(x0, x1, z0, z1, 8)
    scale(sh, L.BIG_T, L.T_LABELS, 0.0150, 0.0168, 0.0205, 0.0036)
    scale(sh, L.BIG_V, L.V_LABELS, 0.0150, 0.0168, 0.0205, 0.0036)
    # separator lines instead of the headings "sweep", "amplifier", "trigger"
    sh.line([(-0.031, 0.1115), (0.017, 0.1115)], 0.0005)
    sh.line([(-0.026, 0.0590), (0.017, 0.0590)], 0.0005)
    sh.line([(0.019, 0.0795), (0.046, 0.0795)], 0.0005)
    sh.line([(0.019, 0.0490), (0.046, 0.0490)], 0.0005)
    # plates with pictograms to the left of the buttons; the power dot
    for z, kind in zip(L.BUTTONS, ("power", "range", "mode", "slope", "source", "coupling")):
        button_icon(sh, 0.0262, z, kind)
    sh.circle(0.0262, L.BUTTONS[0] + 0.0055, 0.0011, fill=INK)
    # left column: shift arrows, level knob marks, the trigger socket circle, input ticks
    arrow2(sh, L.KNOB_POS_X[0], L.KNOB_POS_X[1] + 0.0083, True)
    arrow2(sh, L.KNOB_POS_Y[0] + 0.0090, L.KNOB_POS_Y[1], False)
    for k in range(7):
        a = math.radians(210 - 40 * k)
        cx, cz = L.KNOB_LEVEL
        sh.line([(cx + 0.0062 * math.cos(a), cz + 0.0062 * math.sin(a)),
                 (cx + 0.0074 * math.cos(a), cz + 0.0074 * math.sin(a))], 0.00035)
    sh.circle(L.JACK_TRIG[0] + 0.0085, L.JACK_TRIG[1], 0.0016, outline=INK, w=0.00035)
    sh.line([(L.JACK_TRIG[0] + 0.0072, L.JACK_TRIG[1]), (L.JACK_TRIG[0] + 0.0098, L.JACK_TRIG[1])], 0.00035)
    sh.circle(L.INPUT_Y[0], L.INPUT_Y[1], 0.0098, outline=INK, w=0.0003)
    sh.text(L.INPUT_Y[0], L.INPUT_Y[1] - 0.0128, "1:1", 0.0030)
    # case ground sign above the terminal
    gx, gz = L.GROUND[0], L.GROUND[1] + 0.0080
    sh.line([(gx, gz + 0.0022), (gx, gz - 0.0004)], 0.0004)
    sh.line([(gx - 0.0022, gz - 0.0004), (gx + 0.0022, gz - 0.0004)], 0.0004)
    save(sh.img, sh.size, "decal_panel.png")


def make_screen():
    """CRT filter: green, darker towards the corners (a round tube behind a rectangular window), a light
    10 x 8 grid with ticks on the axes; no beam."""
    w, h = L.SCREEN_WH
    sh = Sheet(-w / 2, w / 2, -h / 2, h / 2, 12, bg=(16, 46, 38, 255))
    glow = Image.new("RGBA", sh.img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    r = sh.m(0.034)
    cx, cy = sh.p(0, 0)
    gd.ellipse([cx - r, cy - r * 0.9, cx + r, cy + r * 0.9], fill=(44, 116, 96, 255))
    sh.img = Image.alpha_composite(sh.img, glow.filter(ImageFilter.GaussianBlur(sh.m(0.006))))
    sh.d = ImageDraw.Draw(sh.img)
    gw, gh = L.GRID_DIV * L.GRID_NX, L.GRID_DIV * L.GRID_NY
    col = (150, 214, 188, 255)
    for i in range(L.GRID_NX + 1):
        x = -gw / 2 + L.GRID_DIV * i
        sh.line([(x, -gh / 2), (x, gh / 2)], 0.0004 if i in (0, L.GRID_NX) else 0.00028, col)
    for j in range(L.GRID_NY + 1):
        z = -gh / 2 + L.GRID_DIV * j
        sh.line([(-gw / 2, z), (gw / 2, z)], 0.0004 if j in (0, L.GRID_NY) else 0.00028, col)
    for i in range(L.GRID_NX * 5 + 1):
        x = -gw / 2 + L.GRID_DIV / 5 * i
        sh.line([(x, -0.0007), (x, 0.0007)], 0.00022, col)
    for j in range(L.GRID_NY * 5 + 1):
        z = -gh / 2 + L.GRID_DIV / 5 * j
        sh.line([(-0.0007, z), (0.0007, z)], 0.00022, col)
    # glass highlight at the top left
    hl = Image.new("RGBA", sh.img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse([sh.m(0.004), sh.m(0.003), sh.m(0.030), sh.m(0.014)], fill=(210, 240, 230, 40))
    sh.img = Image.alpha_composite(sh.img, hl.filter(ImageFilter.GaussianBlur(sh.m(0.003))))
    save(sh.img, sh.size, "decal_screen.png")


def make_side():
    """Left side (-x): two trimmer holes and a slot with a drop of locking paint. The picture is laid by the
    model's y coordinate, which runs right to left on the left side, so there is only round stuff here,
    no digits."""
    (cy, cz), (w, h) = L.SIDE_C, L.SIDE_WH
    sh = Sheet(cy - w / 2, cy + w / 2, cz - h / 2, cz + h / 2, 5)
    for y, z in L.SIDE_HOLES:
        sh.circle(y, z, 0.0026, fill=(88, 92, 88, 255))
        sh.circle(y, z, 0.0021, fill=(10, 10, 10, 255))
    y, z = L.SIDE_SCREW
    sh.circle(y, z, 0.0030, fill=(96, 98, 94, 255))
    sh.line([(y - 0.0024, z), (y + 0.0024, z)], 0.0007, (40, 40, 40, 255))
    sh.circle(y + 0.0006, z - 0.0005, 0.0012, fill=(150, 40, 30, 200))           # drop of locking paint
    save(sh.img, sh.size, "decal_side.png")


def make_tag():
    """Inventory sticker on the right side: paper, a frame, a number in digits, wear."""
    tw, th = L.TAG_WH
    sh = Sheet(-tw / 2, tw / 2, -th / 2, th / 2, 20)
    sh.rect(-tw / 2, -th / 2, tw / 2, th / 2, fill=(226, 218, 196, 255))
    sh.rect(-tw / 2 + 0.0008, -th / 2 + 0.0008, tw / 2 - 0.0008, th / 2 - 0.0008, outline=INK, w=0.0003)
    sh.text(0, 0.0012, "04172", 0.0060, (40, 40, 60, 255))
    sh.line([(-tw / 2 + 0.003, -0.0038), (tw / 2 - 0.003, -0.0038)], 0.0003)
    rnd = random.Random(72)
    px = sh.img.load()
    W, H = sh.img.size
    for _ in range(600):                                                       # paper wear
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        r = rnd.uniform(2, 9)
        for i in range(max(0, int(x - r)), min(W, int(x + r))):
            for j in range(max(0, int(y - r)), min(H, int(y + r))):
                if (i - x) ** 2 + (j - y) ** 2 < r * r:
                    q = px[i, j]
                    px[i, j] = (min(255, q[0] + 8), min(255, q[1] + 8), min(255, q[2] + 6), int(q[3] * 0.6))
    save(sh.img, sh.size, "decal_tag.png")


def make_vents():
    """Two staggered rows of 5 x 1.6 mm slots along the side of the tray."""
    (cy, cz), (w, h) = L.VENT_C, L.VENT_WH
    sh = Sheet(cy - w / 2, cy + w / 2, cz - h / 2, cz + h / 2, 10)
    n = int(w / 0.007)
    for row, dz in enumerate((0.0021, -0.0021)):
        for i in range(n):
            y = cy - w / 2 + 0.004 + 0.007 * i + (0.0035 if row else 0.0)
            if y + 0.0025 > cy + w / 2 - 0.003:
                continue
            sh.rect(y - 0.0025, cz + dz - 0.0008, y + 0.0025, cz + dz + 0.0008, fill=(12, 12, 12, 255))
    save(sh.img, sh.size, "decal_vents.png")


def make_holes(name, w, h, cols, rows, gap_row=None):
    """Perforation of the power supply box: round D 4 mm holes in a grid."""
    sh = Sheet(-w / 2, w / 2, -h / 2, h / 2, 10)
    for i in range(cols):
        for j in range(rows):
            if j == gap_row:
                continue
            u = -w / 2 + w * (i + 0.5) / cols
            v = -h / 2 + h * (j + 0.5) / rows
            sh.circle(u, v, 0.0021, fill=(14, 14, 14, 255))
    save(sh.img, sh.size, name)


if __name__ == "__main__":
    make_panel()
    make_screen()
    make_side()
    make_tag()
    make_vents()
    pw, ph = L.PSU_X[1] - L.PSU_X[0], L.PSU_Z[1] - L.PSU_Z[0]
    make_holes("decal_psu_back.png", pw, ph, 7, 10, gap_row=3)
    make_holes("decal_psu_side.png", L.PSU_Y[1] - L.PSU_Y[0], ph, 3, 10, gap_row=3)
