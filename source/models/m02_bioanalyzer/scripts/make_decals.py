"""Decals for the M02 bioanalyzer (system Python + Pillow). No letters: digits, symbols, rulers.

    python make_decals.py      -> ../work/decal_*.png

- decal_vfd_off.png, decal_vfd_f00..07.png - the display (vacuum fluorescent, 2 lines of 16
  characters in a 5 x 7 matrix): "off" is idle (thermostat 37.0, dashes), the "work" frames show the
  sample number, test N of 8, optical density growing and a measurement progress bar; the part's own
  texture (kmodel panels);
- decal_keys.png - keypad symbols on the slope (digits, arrows, plus-minus, start and stop), in keypad
  axes (a, b) - projected from above (m02_layout.slope_xy);
- decal_rotor.png - slot numbers 1-16 and ticks on the carousel rotor, top view;
- decal_tape.png - the whole 57 mm thermal tape: dot-matrix results in columns of digits, a block per
  sample (same paper as the M62 tape); the top of the image is at the printer slot, the bottom is the
  head of the printout;
- decal_plate.png - nameplate on the back wall: frame, rulers, digits (mirrored: it is viewed from behind);
- decal_label.png - inventory tag with a barcode on the cabinet door.
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m02_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                                         # antialiasing: draw larger, then downscale

DOT5x7 = {
    "0": "01110 10001 10011 10101 11001 10001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11111 00010 00100 00010 00001 10001 01110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    ".": "00000 00000 00000 00000 00000 01100 01100", "-": "00000 00000 00000 11111 00000 00000 00000",
    ":": "00000 01100 01100 00000 01100 01100 00000", "/": "00001 00001 00010 00100 01000 10000 10000",
    "*": "00000 00100 10101 01110 10101 00100 00000", "=": "00000 00000 11111 00000 11111 00000 00000",
    "+": "00000 00100 00100 11111 00100 00100 00000", "#": "11111 11111 11111 11111 11111 11111 11111",
    "<": "00010 00100 01000 10000 01000 00100 00010", ">": "01000 00100 00010 00001 00010 00100 01000",
    " ": "00000 00000 00000 00000 00000 00000 00000",
}


def save(img, name):
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, img.size)


def font(px, bold=True):
    for name in (("arialbd.ttf", "arial.ttf") if bold else ("arial.ttf",)) + ("DejaVuSans-Bold.ttf",):
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


# =============================================================================
# Display
# =============================================================================
VFD_OFF = ("-- -/-     37.0 ", "-.---           ")
VFD_FRAMES = [("07  %d/8    37.%d%s" % (i + 1, (0, 0, 0, 1, 1, 0, 0, 0)[i], "*" if i % 2 == 0 else " "),
               ("%.3f " % v) + "#" * (i + 1) + " " * (10 - i))
              for i, v in enumerate((0.128, 0.215, 0.302, 0.367, 0.421, 0.468, 0.497, 0.512))]


def vfd_image(lines, lit):
    """Display glass: dark blue-green field, a grid of unlit dots, two lines of 5 x 7 characters; lit -
    glowing (the "work" frames, with glow), otherwise dim (idle)."""
    w, h = L.VFD_PX
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (7, 16, 13, 255))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grid = ImageDraw.Draw(img)
    d = ImageDraw.Draw(glow)
    px, py = 4.8 * S, 5.4 * S                                     # dot pitch
    x0, y0 = 24 * S, 14 * S
    r = 1.7 * S
    col = (96, 255, 206, 255) if lit else (52, 128, 106, 255)
    for li, text in enumerate(lines):
        for ci, ch in enumerate(text.ljust(16)[:16]):
            rows = DOT5x7.get(ch, DOT5x7[" "]).split()
            for ry in range(7):
                for rx in range(5):
                    cx = x0 + (ci * 6 + rx) * px
                    cy = y0 + (li * 9 + ry) * py
                    grid.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(16, 34, 29, 255))
                    if rows[ry][rx] == "1":
                        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    if lit:
        img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(3.0 * S)))
    img = Image.alpha_composite(img, glow)
    # glass: a glare on top and a light haze
    shine = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shine).rectangle([0, 0, W, int(H * 0.18)], fill=26)
    img = Image.composite(Image.new("RGBA", (W, H), (150, 170, 165, 255)), img, shine.filter(ImageFilter.GaussianBlur(6 * S)))
    return img.resize((w, h), Image.LANCZOS)


def make_vfd():
    save(vfd_image(VFD_OFF, False), "decal_vfd_off.png")
    for i, lines in enumerate(VFD_FRAMES):
        save(vfd_image(lines, True), "decal_vfd_f%02d.png" % i)


# =============================================================================
# Keypad
# =============================================================================
def symbol(d, kind, cx, cy, s, col):
    """Key symbol without letters: s is half the symbol height, px."""
    w = max(2, int(s * 0.28))
    if kind in ("up", "down", "left", "right", "play", "tri"):
        k = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0), "play": (1, 0), "tri": (0, -1)}[kind]
        tip = (cx + k[0] * s, cy + k[1] * s)
        nx, ny = -k[1], k[0]
        b1 = (cx - k[0] * s * 0.7 + nx * s * 0.85, cy - k[1] * s * 0.7 + ny * s * 0.85)
        b2 = (cx - k[0] * s * 0.7 - nx * s * 0.85, cy - k[1] * s * 0.7 - ny * s * 0.85)
        if kind == "tri":
            d.polygon([tip, b1, b2], outline=col, width=w)
        else:
            d.polygon([tip, b1, b2], fill=col)
    elif kind in ("stop", "square"):
        q = s * 0.8
        if kind == "stop":
            d.rectangle([cx - q, cy - q, cx + q, cy + q], fill=col)
        else:
            d.rectangle([cx - q, cy - q, cx + q, cy + q], outline=col, width=w)
    elif kind == "circle":
        d.ellipse([cx - s * 0.85, cy - s * 0.85, cx + s * 0.85, cy + s * 0.85], outline=col, width=w)
    elif kind == "dot":
        d.ellipse([cx - s * 0.3, cy - s * 0.3, cx + s * 0.3, cy + s * 0.3], fill=col)
    elif kind == "star":
        pts = []
        for k in range(10):
            a = -math.pi / 2 + math.pi * k / 5
            rr = s * (0.95 if k % 2 == 0 else 0.42)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=col)
    elif kind == "back":
        d.line([(cx + s * 0.9, cy), (cx - s * 0.5, cy)], fill=col, width=w)
        d.polygon([(cx - s * 0.95, cy), (cx - s * 0.35, cy - s * 0.5), (cx - s * 0.35, cy + s * 0.5)], fill=col)
    else:                                                       # digits, point, arithmetic
        f = font(int(s * 2.0))
        d.text((cx, cy), {"*": "×", "/": "÷", "-": "−"}.get(kind, kind), font=f, fill=col,
               anchor="mm")


def make_keys(ppm=8000):
    a0, a1, b0, b1 = L.KEYPAD
    W, H = int((a1 - a0) * ppm), int((b1 - b0) * ppm)
    img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def P(a, b):
        return (a - a0) * ppm * S, (b1 - b) * ppm * S
    ink = {"key": (44, 42, 40, 255), "key_dark": (222, 220, 210, 255), "key_green": (236, 240, 230, 255),
           "key_red": (240, 232, 226, 255)}
    for a, b, w, h, kind, leg in L.keys():
        cx, cy = P(a, b)
        s = min(w, h) * ppm * S * (0.30 if kind.startswith("key_") and kind != "key_dark" else 0.27)
        symbol(d, leg, cx, cy, s, ink[kind])
    save(img.resize((W, H), Image.LANCZOS), "decal_keys.png")


# =============================================================================
# Rotor: slot numbers
# =============================================================================
def make_rotor(px=1024):
    size = 2 * L.R_ROT
    k = px * S / size
    img = Image.new("RGBA", (px * S, px * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = px * S / 2
    ink = (52, 54, 58, 255)
    for rr in (0.1228, 0.1395):
        d.ellipse([c - rr * k, c - rr * k, c + rr * k, c + rr * k], outline=ink, width=int(0.0006 * k))
    f = font(int(0.0068 * k))
    for i in range(L.N_CUPS):
        a = 2 * math.pi * i / L.N_CUPS
        # slot: a dark ring around the cup (clearance in the rotor hole)
        gx, gy, rr = c + L.R_CUPS * k * math.cos(a), c - L.R_CUPS * k * math.sin(a), 0.0080 * k
        d.ellipse([gx - rr, gy - rr, gx + rr, gy + rr], outline=(34, 34, 36, 255), width=int(0.0024 * k))
        # tick between the slots
        am = a + math.pi / L.N_CUPS
        d.line([(c + 0.1228 * k * math.cos(am), c - 0.1228 * k * math.sin(am)),
                (c + 0.1300 * k * math.cos(am), c - 0.1300 * k * math.sin(am))], fill=ink, width=int(0.0007 * k))
        # number: the bottom of the digits points outward (readable from outside the carousel)
        t = Image.new("RGBA", (int(0.016 * k), int(0.010 * k)), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((t.width / 2, t.height / 2), str(i + 1), font=f, fill=ink, anchor="mm")
        t = t.rotate(90 + math.degrees(a), expand=True, resample=Image.BICUBIC)
        x, y = c + L.R_NUM * k * math.cos(a), c - L.R_NUM * k * math.sin(a)
        img.alpha_composite(t, (int(x - t.width / 2), int(y - t.height / 2)))
    save(img.resize((px, px), Image.LANCZOS), "decal_rotor.png")


# =============================================================================
# Printer tape
# =============================================================================
THERMAL = (44, 46, 60)


def make_tape(ppm=10000):
    """Thermal 5 x 7 matrix print, 24 characters per line (as on the M62 tape): blocks per sample - sample
    number and time, tests: number, result, an asterisk when out of range, range limits; bars at the
    bottom of a block. The top of the image is fresh print at the printer slot, the bottom is the head
    of the printout."""
    W, H = int(L.TAPE_W * ppm), int(math.ceil(L.TAPE_LEN * ppm)) + 20
    k = ppm / 1000.0
    rnd = random.Random(207)
    img = Image.new("RGB", (W, H), (240, 239, 232))
    d = ImageDraw.Draw(img)
    pitch, dot, lh, x0 = 0.30 * k, 0.13 * k, 3.3 * k, 4.4 * k

    def line(y, text, fade=1.0):
        for ci, ch in enumerate(text):
            for ry, row in enumerate(DOT5x7[ch].split()):
                for rx, bit in enumerate(row):
                    if bit != "1" or rnd.random() > 0.97 * fade:
                        continue
                    cx, cy = x0 + (ci * 6 + rx) * pitch, y + ry * pitch
                    v = int(rnd.uniform(0.0, 0.25) * 200)
                    d.ellipse([cx - dot, cy - dot, cx + dot, cy + dot], fill=tuple(min(255, c + v) for c in THERMAL))

    def num(v, nd):
        return ("%." + str(nd) + "f") % v
    blocks = []
    sample = 7
    while sum(len(b) for b in blocks) * lh < H + 40 * k:
        block = ["=" * 24, " %03d-%02d          %02d:%02d" % (sample, rnd.randint(1, 12), rnd.randint(8, 18),
                                                            rnd.randint(0, 59)), "-" * 24]
        for t in range(rnd.randint(5, 8)):
            lo = rnd.uniform(0.2, 40)
            hi = lo * rnd.uniform(1.3, 2.2)
            v = rnd.uniform(lo * 0.7, hi * 1.25)
            nd = 2 if hi < 10 else 1
            flag = "*" if v < lo or v > hi else " "
            block.append((" %02d %7s %s %s-%s" % (t + 1, num(v, nd), flag, num(lo, nd), num(hi, nd)))[:24])
        block.append("-" * 24)
        block += ["".join(rnd.choice("#  ##  ###  #  ") for _ in range(24))[:24], " " * 24]
        blocks.append(block)
        sample -= 1
    # the last sample (07) is on top, earlier ones below: printing goes from the head toward the slot
    y = 2.5 * k
    for block in blocks:
        for text in block:
            if y > H - 4 * k:
                break
            line(y, text.ljust(24)[:24], fade=rnd.uniform(0.85, 1.0))
            y += lh
        y += 2.0 * k
    m = Image.new("L", (W, H), 0)
    sx = int(rnd.uniform(0.3, 0.7) * W)
    ImageDraw.Draw(m).rectangle([sx, 0, sx + int(0.5 * k), H], fill=150)    # pale thermal head strip
    img = Image.composite(Image.new("RGB", (W, H), (236, 235, 228)), img, m.filter(ImageFilter.GaussianBlur(0.4 * k)))
    save(img, "decal_tape.png")


# =============================================================================
# Nameplate and tag
# =============================================================================
def make_plate(ppm=8000):
    x0, x1, z0, z1 = L.PLATE
    W, H = int((x1 - x0) * ppm), int((z1 - z0) * ppm)
    img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ink = (36, 38, 40, 255)
    m = int(0.004 * ppm * S)
    d.rounded_rectangle([m, m, W * S - m, H * S - m], radius=int(0.002 * ppm * S), outline=ink, width=S * 3)
    f = font(int(0.0042 * ppm * S))
    rows = [("47 118 3", 0.30), ("220   50   0.4", 0.52), ("0 4 1 2", 0.74)]     # no year
    for txt, fy in rows:
        d.text((W * S * 0.52, H * S * fy), txt, font=f, fill=ink, anchor="mm")
    for fy in (0.41, 0.63):
        d.line([(W * S * 0.16, H * S * fy), (W * S * 0.88, H * S * fy)], fill=ink, width=S * 2)
    img = ImageOps.mirror(img.resize((W, H), Image.LANCZOS))     # viewed from behind (normal +Y)
    save(img, "decal_plate.png")


def make_label(w=256, h=128):
    """Inventory tag: white, frame, barcode and number in digits."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=int(H * 0.08), fill=(238, 236, 228, 255),
                        outline=(40, 40, 40, 255), width=S * 2)
    rnd = random.Random(7)
    x = W * 0.08
    while x < W * 0.92:
        bw = rnd.choice((1, 1, 2, 3)) * S * 2
        if rnd.random() < 0.6:
            d.rectangle([x, H * 0.14, x + bw, H * 0.64], fill=(25, 25, 25, 255))
        x += bw + S * 2
    d.text((W * 0.5, H * 0.80), "0 4 7 1 1 9 8 6 2", font=font(int(H * 0.16), bold=False), fill=(25, 25, 25, 255),
           anchor="mm")
    save(img.resize((w, h), Image.LANCZOS), "decal_label.png")


if __name__ == "__main__":
    make_vfd()
    make_keys()
    make_rotor()
    make_tape()
    make_plate()
    make_label()
