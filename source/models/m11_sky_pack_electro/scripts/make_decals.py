"""Decals for the field assembly table (system Python + Pillow): multimeter LCD - its own part texture
(section lcd): "off" is blank glass, "on" is frames where the battery voltage 3336 flickers in the last
digit (4.46-4.49); multimeter face with the range selector scale; car voltmeter scale 8-16 V on the
junction box; lightning sign; blank inventory tag. No letters: only digits, scale marks and symbols.

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges

# seven-segment digits: segments a b c d e f g
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
       "7": "abc", "8": "abcdefg", "9": "abcdfg"}
LCD_FRAMES = ["4.48", "4.47", "4.48", "4.49", "4.48", "4.46"]


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def font(px):
    for name in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


def digit(d, x, y, w, h, ch, ink):
    """Seven-segment digit in frame (x, y, w, h); segments are slightly slanted, as on an LCD."""
    t = w * 0.18
    segs = {"a": (x + t, y, x + w - t, y + t), "g": (x + t, y + h / 2 - t / 2, x + w - t, y + h / 2 + t / 2),
            "d": (x + t, y + h - t, x + w - t, y + h), "f": (x, y + t, x + t, y + h / 2 - t / 2),
            "b": (x + w - t, y + t, x + w, y + h / 2 - t / 2), "e": (x, y + h / 2 + t / 2, x + t, y + h - t),
            "c": (x + w - t, y + h / 2 + t / 2, x + w, y + h - t)}
    for s in SEG[ch]:
        x0, y0, x1, y1 = segs[s]
        k = 0.10 * w                                    # slant: the top is shifted right
        sh0, sh1 = k * (1 - (y0 - y) / h), k * (1 - (y1 - y) / h)
        d.polygon([(x0 + sh0, y0), (x1 + sh0, y0), (x1 + sh1, y1), (x0 + sh1, y1)], fill=ink)


def make_lcd(name, w, h, text):
    """LCD panel: grey-green glass; text is digits (with a point) or empty. Faint "shadows" of all
    segments, as on a real LCD seen at an angle."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (118, 128, 106, 255))
    d = ImageDraw.Draw(img)
    ink, ghost = (26, 30, 24, 255), (108, 117, 97, 255)
    dw, dh = W * 0.16, H * 0.62
    x = W * 0.14
    for ch in "8.88":
        if ch == ".":
            continue
        digit(d, x, H * 0.19, dw, dh, ch, ghost)
        x += dw + W * 0.06
    if text:
        x = W * 0.14
        for ch in text:
            if ch == ".":
                d.rectangle([x - W * 0.045, H * 0.74, x - W * 0.015, H * 0.81], fill=ink)
                continue
            digit(d, x, H * 0.19, dw, dh, ch, ink)
            x += dw + W * 0.06
    # shadow of the frame at top and left
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.rectangle([0, 0, W, H * 0.10], fill=(0, 0, 0, 90))
    sd.rectangle([0, 0, W * 0.03, H], fill=(0, 0, 0, 60))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(H * 0.05)))
    save(img, (w, h), name)


def make_face(name, w, h):
    """Multimeter face (top toward the display): dark panel, selector circle with sector ticks and range
    digits, probe sockets at the bottom as light rings (as on the model: 0.18 / 0.5 / 0.82)."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (36, 36, 38, 255))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([W * 0.03, H * 0.02, W * 0.97, H * 0.98], radius=W * 0.06, outline=(70, 70, 72, 255),
                        width=S * 2)
    cx, cy, R = W / 2, H * 0.55, W * 0.36
    for k in range(20):
        a = math.radians(90 + 18 * k)
        ln = 0.18 if k % 5 == 0 else 0.10
        p = (cx + R * math.cos(a), cy - R * math.sin(a))
        q = (cx + R * (1 - ln) * math.cos(a), cy - R * (1 - ln) * math.sin(a))
        d.line([p, q], fill=(232, 232, 226, 255), width=S * 2)
    # range sectors as coloured arcs (no letters), range digits small
    for a0, a1, col in ((100, 160, (232, 232, 226)), (170, 230, (220, 60, 50)), (240, 300, (232, 232, 226)),
                        (310, 350, (90, 170, 220))):
        d.arc([cx - R * 1.08, cy - R * 1.08, cx + R * 1.08, cy + R * 1.08], -a1, -a0, fill=col + (255,), width=S * 3)
    f = font(int(W * 0.07))
    for ang, txt in ((115, "200"), (145, "20"), (185, "2"), (215, "200"), (255, "20"), (285, "2"), (330, "10")):
        a = math.radians(ang)
        p = (cx + R * 1.24 * math.cos(a), cy - R * 1.24 * math.sin(a))
        d.text(p, txt, fill=(220, 220, 214, 255), font=f, anchor="mm")
    for x, col in ((W * 0.18, (232, 232, 226)), (W * 0.5, (232, 232, 226)), (W * 0.82, (220, 60, 50))):
        y = H * 0.88
        d.ellipse([x - W * 0.075, y - W * 0.075, x + W * 0.075, y + W * 0.075], outline=col + (255,), width=S * 2)
    save(img, (w, h), name)


def make_volt(name, px):
    """Car voltmeter scale 8-16 V: cream dial, arc -50..+50 degrees from vertical, large ticks with digits
    every 2 V, red zones 8-11 and 15-16, green 12-14.5; battery symbol (+ and -) at the bottom.
    No needle: it is a separate part of the model (ozl_needle)."""
    W = px * S
    img = Image.new("RGBA", (W, W), (226, 222, 206, 255))
    d = ImageDraw.Draw(img)
    c = W / 2

    def pt(v, r):
        a = math.radians(-50 + 100 * (v - 8.0) / 8.0)
        return (c + r * math.sin(a), c - r * math.cos(a))

    def arc(v0, v1, r0, r1, col):
        n = 24
        outer = [pt(v0 + (v1 - v0) * k / n, r1) for k in range(n + 1)]
        inner = [pt(v1 - (v1 - v0) * k / n, r0) for k in range(n + 1)]
        d.polygon(outer + inner, fill=col)
    arc(8.0, 11.0, W * 0.40, W * 0.44, (190, 40, 32, 255))
    arc(12.0, 14.5, W * 0.40, W * 0.44, (60, 140, 60, 255))
    arc(15.0, 16.0, W * 0.40, W * 0.44, (190, 40, 32, 255))
    for k in range(0, 33):
        v = 8.0 + k * 0.25
        big = k % 8 == 0
        mid = k % 4 == 0
        r0 = W * (0.345 if big else (0.37 if mid else 0.39))
        d.line([pt(v, r0), pt(v, W * 0.44)], fill=(22, 22, 22, 255), width=S * (3 if big else 2 if mid else 1))
    f = font(int(W * 0.075))
    for v in (8, 10, 12, 14, 16):
        d.text(pt(v, W * 0.285), str(v), fill=(22, 22, 22, 255), font=f, anchor="mm")
    # battery symbol under the axis
    bx, by, bw, bh = c, W * 0.72, W * 0.20, W * 0.10
    d.rectangle([bx - bw / 2, by - bh / 2, bx + bw / 2, by + bh / 2], outline=(22, 22, 22, 255), width=S * 2)
    for sx in (-1, 1):
        d.rectangle([bx + sx * bw * 0.28 - W * 0.015, by - bh / 2 - W * 0.022, bx + sx * bw * 0.28 + W * 0.015,
                     by - bh / 2], fill=(22, 22, 22, 255))
    d.line([(bx - bw * 0.36, by), (bx - bw * 0.20, by)], fill=(22, 22, 22, 255), width=S * 2)
    d.line([(bx + bw * 0.20, by), (bx + bw * 0.36, by)], fill=(22, 22, 22, 255), width=S * 2)
    d.line([(bx + bw * 0.28, by - bh * 0.18), (bx + bw * 0.28, by + bh * 0.18)], fill=(22, 22, 22, 255), width=S * 2)
    # shadow rim from the bezel
    sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([0, 0, W, W], outline=(0, 0, 0, 120), width=int(W * 0.05))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(W * 0.02)))
    save(img, (px, px), name)


def make_bolt(name, px):
    """Electric shock hazard sign: black lightning bolt in a yellow triangle with a black border."""
    W = px * S
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    tri = [(W / 2, W * 0.06), (W * 0.96, W * 0.90), (W * 0.04, W * 0.90)]
    d.polygon(tri, fill=(22, 22, 22, 255))
    k = 0.08
    inner = [(W / 2, W * (0.06 + 2 * k)), (W * (0.96 - 1.6 * k), W * (0.90 - 0.6 * k)),
             (W * (0.04 + 1.6 * k), W * (0.90 - 0.6 * k))]
    d.polygon(inner, fill=(226, 184, 30, 255))
    bolt = [(W * 0.54, W * 0.30), (W * 0.40, W * 0.58), (W * 0.50, W * 0.58), (W * 0.44, W * 0.80),
            (W * 0.62, W * 0.50), (W * 0.52, W * 0.50), (W * 0.60, W * 0.30)]
    d.polygon(bolt, fill=(22, 22, 22, 255))
    save(img, (px, px), name)


def make_tag(name, w, h):
    """Blank inventory tag: aluminium plate, two rivets, punched frame."""
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
    make_lcd("decal_lcd_off.png", 192, 96, "")
    for i, txt in enumerate(LCD_FRAMES):
        make_lcd("decal_lcd_f%02d.png" % i, 192, 96, txt)
    make_face("decal_face.png", 128, 240)
    make_volt("decal_volt.png", 256)
    make_bolt("decal_bolt.png", 128)
    make_tag("decal_tag.png", 160, 64)
