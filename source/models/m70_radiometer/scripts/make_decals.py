"""Decals of the radiometer module (system Python + Pillow): the console face (rings of buttons with
symbols, the mode table - a bracket, ticks and digits, no letters: on a real console these are the
mode captions and the device name), the LCD display in two states - "off" (blank glass with pale
segments) and "working" (a reading in digits), a round sticker with a radiation hazard sign on the
door of the little house, an aluminium inventory plate with a stamped number, a strip of adhesive tape
with a hand-written sample number on the cuvette. No letters.

Display frames of the "working" state (the OZL_Work frames loop): decal_lcd_f01..f07.png - the reading
dances around 0.274 (counting goes on, a statistical spread of ~4 %); frame 0 is decal_lcd_on.png.

    python make_decals.py      -> ../work/decal_*.png

Sizes are as in build_m70.py (PANEL_*, LCD_*, SIGN_D, PLATE_*, TAPE_*).
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4
INK = (30, 32, 34, 255)

PULT_W, PULT_L = 0.078, 0.145           # console face, x across, y along (the display is towards +y)
LCD_W, LCD_H = 0.054, 0.019             # display glass
SIGN_D = 0.052                          # sticker on the door
PLATE_W, PLATE_H = 0.040, 0.024         # plate on the right side of the little house
TAPE_W, TAPE_H = 0.030, 0.011           # tape on the end of the cuvette
BTN = [(-0.017, 0.014), (0.017, 0.022)]  # "mode" and "start" buttons from the face centre (x, y)


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


def trefoil(d, cx, cy, r, fill, bg):
    """Radiation hazard sign: three blades of 60 degrees (two on top, one below), a gap in the background
    colour and a small circle in the centre."""
    for k in range(3):
        a0 = 120 * k                                 # a blade from a0 to a0 + 60 (counter-clockwise)
        d.pieslice([cx - r, cy - r, cx + r, cy + r], -a0 - 60, -a0, fill=fill)   # PIL angles are clockwise
    d.ellipse([cx - r * 0.30, cy - r * 0.30, cx + r * 0.30, cy + r * 0.30], fill=bg)
    d.ellipse([cx - r * 0.20, cy - r * 0.20, cx + r * 0.20, cy + r * 0.20], fill=fill)


def make_panel(name, px):
    """Console face (top view, the top of the image is towards the display): rings and symbols at the
    buttons (a "start" triangle, a "mode" circular arrow), below the mode table: a vertical tick scale,
    seven ticks with digits 1-7 and multipliers, a bracket on the right. Beside the display on the left, a
    radiation symbol by the LED."""
    W = px * S
    H = int(round(px * PULT_L / PULT_W)) * S
    k = W / PULT_W
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def at(x, y):                                    # metres from the face centre -> pixels
        return W / 2 + x * k, H / 2 - y * k
    # rings around the buttons and symbols above them
    for i, (bx, by) in enumerate(BTN):
        cx, cy = at(bx, by)
        r = 0.0095 * k
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=int(S * 1.6))
        sx, sy = at(bx, by + 0.0135)
        s = 0.0022 * k
        if i == 1:                                   # "start" is a triangle
            d.polygon([(sx - s, sy - s), (sx - s, sy + s), (sx + s * 1.2, sy)], fill=INK)
        else:                                        # "mode" is a circular arrow
            d.arc([sx - s, sy - s, sx + s, sy + s], 40, 320, fill=INK, width=int(S * 1.4))
            d.polygon([(sx + s * 0.6, sy - s * 1.3), (sx + s * 1.5, sy - s * 0.5), (sx + s * 0.4, sy - s * 0.2)],
                      fill=INK)
    # mode table
    x0 = -0.016
    ytop, ybot = -0.004, -0.050
    d.line([at(x0, ytop), at(x0, ybot)], fill=INK, width=int(S * 1.3))
    f = font(int(0.0036 * k))
    vals = ["1", "10", "100", "500", "1000", "2000", "-"]
    for i in range(7):
        y = ytop - 0.003 - i * 0.0063
        d.line([at(x0, y), at(x0 + 0.004, y)], fill=INK, width=int(S * 1.0))
        d.text(at(x0 + 0.006, y), str(i + 1), fill=INK, font=f, anchor="lm")
        d.line([at(x0 + 0.011, y), at(x0 + 0.014, y)], fill=INK, width=int(S * 0.8))
        d.text(at(x0 + 0.016, y), vals[i], fill=INK, font=f, anchor="lm")
    yb0, yb1 = ytop - 0.009, ytop - 0.003 - 5 * 0.0063
    xb = x0 + 0.034
    d.line([at(xb - 0.003, yb0), at(xb, yb0), at(xb, yb1), at(xb - 0.003, yb1)], fill=INK, width=int(S * 1.0))
    d.line([at(xb, (yb0 + yb1) / 2), at(xb + 0.003, (yb0 + yb1) / 2)], fill=INK, width=int(S * 1.0))
    # radiation symbol by the LED and an engraved frame in place of the device name
    cx, cy = at(-0.016, 0.066)
    trefoil(d, cx, cy, 0.0028 * k, INK, (0, 0, 0, 0))
    d.rounded_rectangle([*at(-0.020, -0.058), *at(0.020, -0.066)], radius=int(0.001 * k),
                        outline=(120, 124, 126, 255), width=int(S * 1.0))
    save(img, (px, int(round(px * PULT_L / PULT_W))), name)


SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
       "7": "abc", "8": "abcdefg", "9": "abcdfg"}


def seg_digit(d, x, y, w, h, ch, fill, th):
    """Seven-segment digit: (x, y) is the top left, w x h."""
    on = SEG.get(ch, "")
    pts = {"a": [(x, y), (x + w, y)], "b": [(x + w, y), (x + w, y + h / 2)], "c": [(x + w, y + h / 2), (x + w, y + h)],
           "d": [(x, y + h), (x + w, y + h)], "e": [(x, y + h / 2), (x, y + h)], "f": [(x, y), (x, y + h / 2)],
           "g": [(x, y + h / 2), (x + w, y + h / 2)]}
    for s in on:
        (ax, ay), (bx, by) = pts[s]
        sk = 0.12 * w                                # slant, as on an LCD
        d.line([(ax + sk * (1 - 2 * (ay - y) / h), ay), (bx + sk * (1 - 2 * (by - y) / h), by)], fill=fill,
               width=th)


def make_lcd(name, px, text, bg, ink):
    """LCD display: grey-green glass, four digit places; text is what is lit ("8888" is the pale shadow of
    all segments in the "off" state), a dot after the first digit, a mode indicator tick on the left."""
    h = int(round(px * LCD_H / LCD_W))
    W, H = px * S, h * S
    img = Image.new("RGBA", (W, H), bg)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H * 0.18], fill=(0, 0, 0, 50))           # shadow of the frame at the top
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(H * 0.06)))
    d = ImageDraw.Draw(img)
    cw, chh, gap = W * 0.13, H * 0.62, W * 0.065
    x = W * 0.22
    for i, ch in enumerate(text):
        seg_digit(d, x, H * 0.19, cw, chh, ch, ink, int(H * 0.075))
        if i == 0:
            d.ellipse([x + cw + gap * 0.25, H * 0.77, x + cw + gap * 0.25 + H * 0.08, H * 0.85], fill=ink)
        x += cw + gap
    d.polygon([(W * 0.05, H * 0.30), (W * 0.11, H * 0.40), (W * 0.05, H * 0.50)], fill=ink)      # indicator
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 44, 40, 255), width=S * 2)
    save(img, (px, h), name)


def make_sign(name, px):
    """Round sticker per GOST 17925-72: a black sign on yellow, a border; the paint has faded slightly."""
    W = px * S
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = W / 2
    d.ellipse([S, S, W - S, W - S], fill=(226, 186, 40, 255), outline=(36, 34, 30, 255), width=int(W * 0.035))
    trefoil(d, c, c, W * 0.34, (30, 28, 26, 255), (226, 186, 40, 255))
    save(img, (px, px), name)


def make_plate(name, px):
    """Inventory plate: aluminium, a stamped number in digits, the two rivets are drawn by the geometry."""
    h = int(round(px * PLATE_H / PLATE_W))
    W, H = px * S, h * S
    img = Image.new("RGBA", (W, H), (188, 190, 186, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([S * 2, S * 2, W - S * 3, H - S * 3], outline=(120, 122, 120, 255), width=S * 2)
    f = font(int(H * 0.34))
    d.text((W * 0.5 + S, H * 0.52 + S), "0832", fill=(236, 236, 230, 200), font=f, anchor="mm")   # edge highlight
    d.text((W * 0.5, H * 0.52), "0832", fill=(72, 74, 74, 255), font=f, anchor="mm")
    save(img, (px, h), name)


def make_tape(name, px):
    """A strip of masking tape with a sample number in ballpoint pen, torn ends."""
    h = int(round(px * TAPE_H / TAPE_W))
    W, H = px * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    poly = [(W * 0.03, H * 0.05), (W * 0.97, 0), (W * 0.99, H * 0.3), (W * 0.96, H * 0.6), (W, H),
            (W * 0.02, H * 0.97), (0, H * 0.6), (W * 0.04, H * 0.3)]
    d.polygon(poly, fill=(222, 210, 168, 255))
    pen = (36, 46, 110, 255)
    # "17" in hand-drawn strokes
    d.line([(W * 0.36, H * 0.32), (W * 0.42, H * 0.18), (W * 0.42, H * 0.82)], fill=pen, width=S * 3)
    d.line([(W * 0.52, H * 0.20), (W * 0.66, H * 0.20), (W * 0.56, H * 0.84)], fill=pen, width=S * 3)
    d.line([(W * 0.55, H * 0.52), (W * 0.64, H * 0.50)], fill=pen, width=S * 2)
    save(img, (px, h), name)


if __name__ == "__main__":
    make_panel("decal_panel.png", 256)
    make_lcd("decal_lcd_off.png", 192, "8888", (150, 158, 140, 255), (138, 146, 128, 255))
    make_lcd("decal_lcd_on.png", 192, "0274", (178, 190, 160, 255), (24, 28, 24, 255))
    make_sign("decal_sign.png", 192)
    make_plate("decal_plate.png", 128)
    make_tape("decal_tape.png", 96)
    # "working" display frames: frame 0 is decal_lcd_on.png (0.274), the rest are a scatter of readings
    for i, text in enumerate(("0281", "0268", "0277", "0285", "0271", "0263", "0279"), 1):
        make_lcd("decal_lcd_f%02d.png" % i, 192, text, (178, 190, 160, 255), (24, 28, 24, 255))
