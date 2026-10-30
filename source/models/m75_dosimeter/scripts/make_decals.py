"""Decals of the dosimeter module (system Python + Pillow). No letters:

- the switch panel face of the DRG-01T1: a frame, brackets and ticks of the modes, a backlight icon
  and a circular reset arrow (the real panel has mode captions here; they are omitted);
- marker writing on the case: in the reference photo the case is written on in violet marker - here
  only digits (an inventory number) and a line;
- the LCD display in two states: "off" (blank glass with a pale shadow of segments) and "working" (a
  reading in digits, backlight);
- the lead sheet in the lid: a radiation hazard sign slapped on with a brush in red enamel with drips,
  and a strip of masking tape with a column of readings in pencil (digits);
- nail heads on the front and back walls of the box.

    python make_decals.py      -> ../work/decal_*.png

Sizes are as in build_m75.py (LEGEND_*, MARKS_*, LCD_*, LEAD_*, BOX_*). The images are drawn
"instrument up" (the display towards the top of the image); how they lie on the model is in
build_m75.py.
"""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
INK = (40, 42, 40, 255)

LEGEND_W, LEGEND_H = 0.035, 0.057       # switch panel: across the instrument, along it
MARKS_W, MARKS_H = 0.060, 0.022         # field of the marker writing between the display and the panel
LCD_W, LCD_H = 0.049, 0.017             # display glass
LEAD_W, LEAD_H = 0.176, 0.090           # lead sheet in the lid
BOX_W, BOX_H = 0.200, 0.047             # front (back) wall of the box above the bottom
NAILS = [(-0.096, 0.012), (-0.096, 0.035), (0.096, 0.012), (0.096, 0.035)]   # from the wall centre, the bottom is 0


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


# --- handwritten digits: strokes in a 0..1 cell (x to the right, y down) --------------------------
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
    """A string of handwritten digits: height h, slant, each digit has its own shift and stroke jitter."""
    w = h * 0.55
    for ch in text:
        if ch == " ":
            x += w * adv * 1.4
            continue
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


# --- switch panel face ----------------------------------------------------------------------------
def make_legend(name, px_mm=12):
    """A 35 x 57 mm panel: a dark edge along the outline with rounded top corners and a screw cutout at the
    bottom; three rows of modes - ticks and brackets (after the photo, no captions), below them a
    backlight icon and a circular reset arrow above the button brackets."""
    W, H = int(LEGEND_W * 1000 * px_mm) * S, int(LEGEND_H * 1000 * px_mm) * S
    k = W / (LEGEND_W * 1000)                       # pixels per mm
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lw = int(0.45 * k)

    def P(xm, ym):                                   # mm from the top left corner
        return xm * k, ym * k
    edge = (92, 96, 88, 255)
    d.rounded_rectangle([*P(0.3, 0.3), *P(34.7, 56.7)], radius=int(2.4 * k), outline=edge, width=int(0.5 * k))
    d.arc([*P(13.0, 50.6), *P(22.0, 59.6)], 180, 360, fill=edge, width=int(0.5 * k))
    # mode rows: y is mm from the top of the panel
    rows = [(6.5, "top"), (12.8, "mid"), (18.6, "bot")]
    for y, kind in rows:
        for side in (-1, 1):
            xo, xi = (2.0, 15.0) if side < 0 else (33.0, 20.0)
            # a line under the caption (there is no caption)
            d.line([P(xo + side * -2.6, y), P(xi, y)], fill=INK, width=lw)
            if kind == "top":
                d.line([P(xo, y), P(xo, y + 3.2)], fill=INK, width=lw)
                d.line([P(xo - side * -1.6, y + 3.2), P(xo, y + 3.2)], fill=INK, width=lw)
            elif kind == "mid":
                d.line([P(xo + side * 0.5, y), P(xo + side * -1.0, y)], fill=INK, width=lw)
            else:
                d.line([P(xo, y - 3.2), P(xo, y)], fill=INK, width=lw)
                d.line([P(xo - side * -1.6, y - 3.2), P(xo, y - 3.2)], fill=INK, width=lw)
        # dot pointer of the switch position
        d.ellipse([*P(16.9, y - 2.4), *P(18.1, y - 1.2)], fill=INK)
    # backlight icon: a bulb with rays
    cx, cy = P(10.5, 39.0)
    r = 1.6 * k
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=lw)
    d.line([(cx - r * 0.5, cy + r * 1.05), (cx + r * 0.5, cy + r * 1.05)], fill=INK, width=lw)
    for a in range(-150, 35, 45):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        d.line([(cx + ca * r * 1.45, cy + sa * r * 1.45), (cx + ca * r * 2.2, cy + sa * r * 2.2)], fill=INK, width=lw)
    # reset icon: a circular arrow
    cx, cy = P(25.0, 39.0)
    d.arc([cx - r * 1.3, cy - r * 1.3, cx + r * 1.3, cy + r * 1.3], 60, 340, fill=INK, width=lw)
    tip = (cx + r * 1.3 * math.cos(math.radians(340)), cy + r * 1.3 * math.sin(math.radians(340)))
    d.polygon([(tip[0] - 0.9 * k, tip[1] - 1.0 * k), (tip[0] + 0.9 * k, tip[1] - 0.5 * k), (tip[0], tip[1] + 0.7 * k)],
              fill=INK)
    # button brackets
    for x0, x1, xs in ((3.0, 16.0, 3.0), (19.0, 32.0, 32.0)):
        d.line([P(x0, 43.5), P(x1, 43.5)], fill=INK, width=lw)
        d.line([P(xs, 43.5), P(xs, 47.0)], fill=INK, width=lw)
        d.line([P(xs - 1.2, 47.0), P(xs + 1.2, 47.0)], fill=INK, width=lw)
    # scratches over the panel (thin, light)
    rnd = random.Random(75)
    for _ in range(5):
        x, y = rnd.uniform(3, 32) * k, rnd.uniform(4, 50) * k
        a = math.radians(rnd.uniform(60, 120))
        L = rnd.uniform(6, 22) * k
        d.line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], fill=(214, 216, 208, 150), width=max(1, S // 2))
    save(img, (W // S, H // S), name)


def make_marks(name, px_mm=10):
    """Violet marker on the case (as in the reference photo): an inventory number in digits with an
    underline and a "tick + digit" note at the side; the ink has faded and is worn off in places."""
    W, H = int(MARKS_W * 1000 * px_mm) * S, int(MARKS_H * 1000 * px_mm) * S
    k = W / (MARKS_W * 1000)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rnd = random.Random(1175)
    ink = (156, 54, 122, 215)
    x = hand_text(d, 6.0 * k, 3.0 * k, 9.5 * k, "4176", ink, int(1.0 * k), rnd)
    d.line([(6.5 * k, 15.0 * k), (x * 0.55 + 6.0 * k * 0.45, 14.2 * k), (x - 1.0 * k, 15.4 * k)], fill=ink,
           width=int(0.9 * k), joint="curve")
    # at the side - a "tick" and the digit 2 (a handwritten verification mark)
    d.line([(44.0 * k, 9.0 * k), (46.5 * k, 13.5 * k), (51.5 * k, 3.5 * k)], fill=ink, width=int(1.0 * k), joint="curve")
    hand_text(d, 52.5 * k, 8.5 * k, 8.0 * k, "2", ink, int(0.9 * k), rnd)
    # worn off by hands: a mask of patches
    a = img.getchannel("A")
    rub = Image.new("L", (W, H), 255)
    rd = ImageDraw.Draw(rub)
    for _ in range(26):
        cx, cy, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.8, 3.0) * k
        rd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rnd.randint(60, 170))
    rub = rub.filter(ImageFilter.GaussianBlur(0.8 * k))
    img.putalpha(ImageChops.multiply(a, rub))
    save(img, (W // S, H // S), name)


SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
       "7": "abc", "8": "abcdefg", "9": "abcdfg"}


def seg_digit(d, x, y, w, h, ch, fill, th):
    """Seven-segment digit: (x, y) is the top left, w x h, slanted like an LCD."""
    pts = {"a": [(x, y), (x + w, y)], "b": [(x + w, y), (x + w, y + h / 2)], "c": [(x + w, y + h / 2), (x + w, y + h)],
           "d": [(x, y + h), (x + w, y + h)], "e": [(x, y + h / 2), (x, y + h)], "f": [(x, y), (x, y + h / 2)],
           "g": [(x, y + h / 2), (x + w, y + h / 2)]}
    sk = 0.12 * w
    for s in SEG.get(ch, ""):
        (ax, ay), (bx, by) = pts[s]
        d.line([(ax + sk * (1 - 2 * (ay - y) / h), ay), (bx + sk * (1 - 2 * (by - y) / h), by)], fill=fill, width=th)


def make_lcd(name, px, text, bg, ink, dot=1):
    """LCD display of the DRG-01T1: four digit places and a dot; text is what is lit ("8888" pale is "off").
    A dark glass edge, the visor shadow on top."""
    h = int(round(px * LCD_H / LCD_W))
    W, H = px * S, h * S
    img = Image.new("RGBA", (W, H), bg)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H * 0.22], fill=(0, 0, 0, 60))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(H * 0.07)))
    d = ImageDraw.Draw(img)
    cw, chh, gap = W * 0.13, H * 0.60, W * 0.06
    x = W * 0.20
    for i, ch in enumerate(text):
        seg_digit(d, x, H * 0.20, cw, chh, ch, ink, int(H * 0.08))
        if i == dot - 1:
            d.ellipse([x + cw + gap * 0.22, H * 0.76, x + cw + gap * 0.22 + H * 0.08, H * 0.84], fill=ink)
        x += cw + gap
    d.rectangle([0, 0, W - 1, H - 1], outline=(38, 42, 36, 255), width=S * 3)
    save(img, (px, h), name)


# --- lead sheet in the lid ------------------------------------------------------------------------
def make_lead(name, px_mm=5):
    """A radiation sign brushed in red enamel (uneven edges, strokes, drips downwards, the paint knocked off
    in places) and a strip of masking tape with a column of readings in pencil; the picture is the front
    view of the open lid."""
    W, H = int(LEAD_W * 1000 * px_mm) * S, int(LEAD_H * 1000 * px_mm) * S
    k = W / (LEAD_W * 1000)
    rnd = random.Random(7575)
    # sign: the paint mask
    paint = Image.new("L", (W, H), 0)
    pd = ImageDraw.Draw(paint)
    cx, cy, R = 58.0 * k, 44.0 * k, 25.0 * k
    for kk in range(3):
        a0 = 30 + 120 * kk                              # blades: two on top, one below (as in GOST 17925-72)
        poly = []
        for i in range(17):
            a = math.radians(a0 - 30 + 60 * i / 16)
            rr = R * (1 + rnd.uniform(-0.035, 0.035))
            poly.append((cx + math.cos(a) * rr, cy - math.sin(a) * rr))
        for i in range(9):
            a = math.radians(a0 + 30 - 60 * i / 8)
            rr = R * 0.30 * (1 + rnd.uniform(-0.05, 0.05))
            poly.append((cx + math.cos(a) * rr, cy - math.sin(a) * rr))
        pd.polygon(poly, fill=255)
    r0 = R * 0.20
    pd.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], fill=255)
    # drips: from the lower edges of the blades downwards
    for _ in range(7):
        x = cx + rnd.uniform(-0.85, 0.85) * R
        y0 = cy + R * rnd.uniform(0.25, 0.55)
        L = rnd.uniform(4, 15) * k
        wdt = rnd.uniform(0.7, 1.4) * k
        pd.line([(x, y0), (x + rnd.uniform(-0.4, 0.4) * k, y0 + L)], fill=255, width=int(wdt))
        pd.ellipse([x - wdt, y0 + L - wdt, x + wdt, y0 + L + wdt * 1.4], fill=255)
    # brush strokes along the edge and knocked-off paint
    paint = paint.filter(ImageFilter.GaussianBlur(0.35 * k))
    chip = Image.new("L", (W, H), 255)
    cd = ImageDraw.Draw(chip)
    for _ in range(34):
        x, y = cx + rnd.uniform(-1.1, 1.1) * R, cy + rnd.uniform(-1.1, 1.1) * R
        r = rnd.uniform(0.2, 0.8) * k
        cd.ellipse([x - r, y - r, x + r * 1.6, y + r], fill=0)
    for _ in range(4):                                  # lengthwise brush stripes - thinner paint
        y = cy + rnd.uniform(-1, 1) * R
        cd.line([(cx - R, y), (cx + R, y + rnd.uniform(-2, 2) * k)], fill=225, width=int(0.4 * k))
    paint = Image.composite(paint, Image.new("L", (W, H), 0), chip)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    red = Image.new("RGBA", (W, H), (168, 34, 24, 255))
    img = Image.composite(red, img, paint)
    # masking tape with a column of readings
    tw, th = 40.0 * k, 64.0 * k
    tape = Image.new("RGBA", (int(tw), int(th)), (0, 0, 0, 0))
    td = ImageDraw.Draw(tape)
    poly = [(tw * 0.03, th * 0.02), (tw * 0.35, 0), (tw * 0.70, th * 0.025), (tw * 0.98, th * 0.01), (tw, th * 0.98),
            (tw * 0.62, th * 0.995), (tw * 0.30, th * 0.97), (tw * 0.01, th)]
    td.polygon(poly, fill=(214, 202, 160, 255))
    pencil = (70, 70, 74, 230)
    y = 4.0 * k
    for val in ("0.02", "0.03", "0.15", "1.4", "0.08", "0.31", "0.02"):
        hand_text(td, 4.0 * k, y, 5.0 * k, val, pencil, max(2, int(0.45 * k)), rnd, slant=0.12, adv=0.45)
        y += 8.4 * k
    td.line([(3.0 * k, 4.0 * k + 3 * 8.4 * k - 1.6 * k), (30.0 * k, 4.0 * k + 3 * 8.4 * k - 1.4 * k)],
            fill=pencil, width=max(2, int(0.4 * k)))
    # dirty fingers along the tape edge
    stain = Image.new("L", tape.size, 0)
    sd = ImageDraw.Draw(stain)
    for _ in range(10):
        x, yy, r = rnd.uniform(0, tw), rnd.choice((rnd.uniform(0, th * 0.15), rnd.uniform(th * 0.85, th))), rnd.uniform(2, 6) * k
        sd.ellipse([x - r, yy - r, x + r, yy + r], fill=rnd.randint(20, 60))
    stain = stain.filter(ImageFilter.GaussianBlur(2 * k))
    dirty = Image.new("RGBA", tape.size, (90, 80, 62, 255))
    tape = Image.composite(dirty, tape, Image.composite(stain, Image.new("L", tape.size, 0), tape.getchannel("A")))
    tape = tape.rotate(-3.5, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(tape, (int(122.0 * k), int(10.0 * k)))
    save(img, (W // S, H // S), name)


def make_nails(name, px_mm=4):
    """Nail heads on the wall: dark metal, a rusty orange halo of rust on the wood."""
    W, H = int(BOX_W * 1000 * px_mm) * S, int(BOX_H * 1000 * px_mm) * S
    k = W / (BOX_W * 1000)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    d = ImageDraw.Draw(img)
    for x, z in NAILS:
        cx, cy = (x + BOX_W / 2) * 1000 * k, (BOX_H - z) * 1000 * k
        r = 3.0 * k
        hd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(84, 46, 20, 120))
        r = 1.2 * k
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(46, 44, 42, 255))
        d.arc([cx - r, cy - r, cx + r, cy + r], 200, 300, fill=(120, 116, 108, 255), width=max(1, int(0.3 * k)))
    halo = halo.filter(ImageFilter.GaussianBlur(1.2 * k))
    img = Image.alpha_composite(halo, img)
    save(img, (W // S, H // S), name)


if __name__ == "__main__":
    make_legend("decal_legend.png")
    make_marks("decal_marks.png")
    make_lcd("decal_lcd_off.png", 196, "8888", (142, 150, 128, 255), (137, 145, 123, 255))
    make_lcd("decal_lcd_on.png", 196, "0014", (176, 196, 150, 255), (22, 28, 22, 255))
    make_lead("decal_lead.png")
    make_nails("decal_nails.png")
