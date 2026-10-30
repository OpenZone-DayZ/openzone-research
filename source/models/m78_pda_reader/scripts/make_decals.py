"""Decals of the PDA reader (system Python + Pillow):
- the Palm III LCD: off (blank grey-green glass) and the work frames decal_lcd_f00..f07 (green
  backlight, a sync screen: header tab, a two-arrow circle icon, a progress bar, text-free row bars);
  the arrows turn 22.5 degrees per frame, the bar grows, and on the fifth frame the next record
  starts; the OZL_WorkFx mod script steps through the frames, 0.25 s each, one circle takes 2 s;
- the handwriting field under the screen (a frame and four round pictograms without captions);
- pictograms on the buttons (handset, calendar, checklist, note with a pencil, rocker arrows);
- the sync icon on the dock button and an inventory label with a barcode and digits.
No letters or brand marks.

    python make_decals.py      -> ../work/decal_*.png

Sizes match build_m78.py (LCD_*, SILK_*, KEYS_*, HS_R, LABEL_*).
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4

LCD_W, LCD_H = 0.058, 0.0556            # LCD area, 160 x 160 dots (the glass is taller: it continues into the input field)
SILK_W, SILK_H = 0.058, 0.0186          # handwriting input field
KEYS_W, KEYS_H = 0.068, 0.020           # button strip
KEY_U = (-0.0255, -0.0125, 0.0, 0.0125, 0.0255)   # button centres across the width (0 is the rocker)
HS_D = 0.016                            # sync button on the dock
LABEL_W, LABEL_H = 0.034, 0.014         # label on the board


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


LCD_FRAMES = 8                          # work frames (build_m78.py, SCREEN)


def sync_arrows(d, cx, cy, r, fill, width, rot=0.0):
    """Sync icon: two arcs around a circle, each with an arrowhead; rot turns it clockwise (along the
    arrows), in degrees.
    """
    box = [cx - r, cy - r, cx + r, cy + r]
    for a0 in (200 + rot, 20 + rot):
        d.arc(box, a0, a0 + 140, fill=fill, width=width)
        a = math.radians(a0 + 140)
        tx, ty = cx + r * math.cos(a), cy + r * math.sin(a)
        dx, dy = -math.sin(a), math.cos(a)                 # tangent along the arc (PIL goes clockwise)
        nx, ny = math.cos(a), math.sin(a)
        h = width * 1.9
        d.polygon([(tx + dx * h * 1.1, ty + dy * h * 1.1), (tx + nx * h, ty + ny * h), (tx - nx * h, ty - ny * h)],
                  fill=fill)


def make_lcd(name, px, on, frame=0):
    """LCD 160 x 160. Off: plain glass with the bezel's shadow at the top. Work: the backlight and the
    sync screen (no text: tab, icon, progress bar, row bars), frame `frame` of LCD_FRAMES. The icon is
    symmetric under 180 degrees, so over a full loop it turns half a revolution without a jump; the
    progress bar starts at 60 %, grows by 1/8 per frame and restarts after 100 % (the next record).
    """
    rot = 180.0 * frame / LCD_FRAMES
    fill = (0.60 + frame / LCD_FRAMES) % 1.0
    h = int(round(px * LCD_H / LCD_W))
    W, H = px * S, h * S
    bg = (172, 206, 160, 255) if on else (138, 148, 128, 255)
    ink = (34, 52, 40, 255)
    img = Image.new("RGBA", (W, H), bg)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H * 0.07], fill=(0, 0, 0, 70))
    ImageDraw.Draw(sh).rectangle([0, 0, W * 0.03, H], fill=(0, 0, 0, 40))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(H * 0.025)))
    d = ImageDraw.Draw(img)
    if on:
        # header tab on the left and a line under it across the full width
        d.rounded_rectangle([W * 0.04, H * 0.035, W * 0.40, H * 0.115], radius=int(H * 0.02), fill=ink)
        d.line([(W * 0.04, H * 0.115), (W * 0.96, H * 0.115)], fill=ink, width=int(S * 1.6))
        # sync icon
        sync_arrows(d, W * 0.5, H * 0.37, W * 0.14, ink, int(W * 0.035), rot)
        # progress bar: the frame and the filled part
        d.rectangle([W * 0.14, H * 0.60, W * 0.86, H * 0.67], outline=ink, width=int(S * 1.6))
        d.rectangle([W * 0.15, H * 0.61, W * (0.15 + 0.70 * fill), H * 0.66], fill=ink)
        # row bars (instead of captions) and a button bar at the bottom
        for i, (x0, x1) in enumerate(((0.10, 0.74), (0.10, 0.58), (0.10, 0.66))):
            y = H * (0.73 + i * 0.06)
            d.rectangle([W * x0, y, W * x1, y + H * 0.022], fill=(52, 72, 58, 255))
        d.rounded_rectangle([W * 0.36, H * 0.90, W * 0.64, H * 0.965], radius=int(H * 0.03), outline=ink,
                            width=int(S * 1.4))
        d.rectangle([W * 0.42, H * 0.925, W * 0.58, H * 0.94], fill=ink)
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 44, 40, 255), width=S * 2)
    save(img, (px, h), name)


def make_silk(name, px):
    """Input field under the screen: light glass, the field frame with centre marks and two pairs of round
    pictograms at the sides (home arrow, menu rows, calculator grid, magnifier). No captions.
    """
    h = int(round(px * SILK_H / SILK_W))
    W, H = px * S, h * S
    k = W / SILK_W
    img = Image.new("RGBA", (W, H), (150, 162, 144, 255))
    d = ImageDraw.Draw(img)
    ink = (52, 62, 52, 255)
    lw = int(S * 1.2)
    # field frame in the middle
    x0, x1 = W / 2 - 0.0172 * k, W / 2 + 0.0172 * k
    d.rectangle([x0, H * 0.06, x1, H * 0.94], outline=ink, width=lw)
    d.polygon([(W / 2 - S * 3, H * 0.06), (W / 2 + S * 3, H * 0.06), (W / 2, H * 0.06 + S * 4)], fill=ink)
    d.polygon([(W / 2 - S * 3, H * 0.94), (W / 2 + S * 3, H * 0.94), (W / 2, H * 0.94 - S * 4)], fill=ink)
    d.ellipse([x0 + S * 4, H * 0.80, x0 + S * 7, H * 0.80 + S * 3], fill=ink)
    d.ellipse([x1 - S * 7, H * 0.80, x1 - S * 4, H * 0.80 + S * 3], fill=ink)
    r = 0.0036 * k
    cx_l, cx_r = 0.0055 * k, W - 0.0055 * k
    for cx in (cx_l, cx_r):
        for cy in (H * 0.28, H * 0.72):
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ink, width=lw)
    # home arrow (applications)
    cx, cy = cx_l, H * 0.28
    d.arc([cx - r * 0.55, cy - r * 0.2, cx + r * 0.75, cy + r * 1.1], 180, 300, fill=ink, width=lw)
    d.polygon([(cx + r * 0.25, cy - r * 0.55), (cx + r * 0.65, cy - r * 0.05), (cx + r * 0.05, cy - r * 0.05)], fill=ink)
    # menu: three rows
    cx, cy = cx_l, H * 0.72
    for i in range(3):
        y = cy - r * 0.4 + i * r * 0.4
        d.line([(cx - r * 0.45, y), (cx + r * 0.45, y)], fill=ink, width=lw)
    # calculator: 3 x 3 grid
    cx, cy = cx_r, H * 0.28
    q = r * 0.5
    d.rectangle([cx - q, cy - q, cx + q, cy + q], outline=ink, width=lw)
    for t in (-q / 3, q / 3):
        d.line([(cx + t, cy - q), (cx + t, cy + q)], fill=ink, width=int(S * 0.8))
        d.line([(cx - q, cy + t), (cx + q, cy + t)], fill=ink, width=int(S * 0.8))
    # magnifier
    cx, cy = cx_r, H * 0.72
    d.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.15, cy + r * 0.15], outline=ink, width=lw)
    d.line([(cx + r * 0.08, cy + r * 0.08), (cx + r * 0.5, cy + r * 0.5)], fill=ink, width=int(S * 1.8))
    save(img, (px, h), name)


def make_keys(name, px):
    """Pictograms on the buttons (light grey paint on dark plastic, transparent background): handset,
    calendar, rocker with up and down arrows, checklist, note with a pencil.
    """
    h = int(round(px * KEYS_H / KEYS_W))
    W, H = px * S, h * S
    k = W / KEYS_W
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ink = (196, 198, 194, 255)
    lw = int(S * 1.1)
    cy = H / 2
    q = 0.0026 * k
    xs = [W / 2 + u * k for u in KEY_U]
    # handset
    cx = xs[0]
    d.arc([cx - q, cy - q, cx + q, cy + q], 110, 250, fill=ink, width=int(S * 2.2))
    d.ellipse([cx - q * 0.9, cy - q * 1.15, cx - q * 0.2, cy - q * 0.6], fill=ink)
    d.ellipse([cx - q * 0.9, cy + q * 0.6, cx - q * 0.2, cy + q * 1.15], fill=ink)
    # calendar
    cx = xs[1]
    d.rectangle([cx - q, cy - q * 0.8, cx + q, cy + q], outline=ink, width=lw)
    d.rectangle([cx - q, cy - q * 0.8, cx + q, cy - q * 0.35], fill=ink)
    for i in range(3):
        for j in range(2):
            x = cx - q * 0.6 + i * q * 0.6
            y = cy + j * q * 0.55
            d.rectangle([x - S, y - S, x + S, y + S], fill=ink)
    # rocker: up and down arrows
    cx = xs[2]
    for sgn in (-1, 1):
        y = cy + sgn * 0.0042 * k
        d.polygon([(cx - q * 0.5, y - sgn * q * 0.2), (cx + q * 0.5, y - sgn * q * 0.2), (cx, y + sgn * q * 0.45)],
                  fill=ink)
    # checklist
    cx = xs[3]
    for i in range(3):
        y = cy - q * 0.7 + i * q * 0.7
        d.line([(cx - q, y), (cx - q * 0.75, y + q * 0.25), (cx - q * 0.35, y - q * 0.3)], fill=ink, width=lw)
        d.line([(cx - q * 0.1, y), (cx + q, y)], fill=ink, width=lw)
    # note with a pencil
    cx = xs[4]
    d.polygon([(cx - q * 0.9, cy - q), (cx + q * 0.4, cy - q), (cx + q * 0.4, cy + q), (cx - q * 0.9, cy + q)],
              outline=ink, width=lw)
    for i in range(3):
        y = cy - q * 0.5 + i * q * 0.45
        d.line([(cx - q * 0.65, y), (cx + q * 0.1, y)], fill=ink, width=int(S * 0.8))
    d.line([(cx + q * 1.0, cy - q * 1.0), (cx - q * 0.1, cy + q * 0.6)], fill=ink, width=int(S * 2.0))
    save(img, (px, h), name)


def make_hotsync(name, px):
    """Dock button: the sync icon in light paint on dark, the paint rubbed off in patches."""
    W = px * S
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ink = (200, 202, 198, 255)
    c = W / 2
    d.ellipse([c - W * 0.32, c - W * 0.32, c + W * 0.32, c + W * 0.32], outline=ink, width=int(W * 0.035))
    sync_arrows(d, c, c, W * 0.19, ink, int(W * 0.05))
    # wear: some paint rubbed off by a finger
    rnd = random.Random(78)
    mask = Image.new("L", (W, W), 255)
    md = ImageDraw.Draw(mask)
    for _ in range(140):
        x, y = rnd.uniform(0.25, 0.75) * W, rnd.uniform(0.25, 0.75) * W
        rr = rnd.uniform(0.01, 0.035) * W
        md.ellipse([x - rr, y - rr, x + rr, y + rr], fill=rnd.randint(40, 160))
    a = img.getchannel("A")
    img.putalpha(Image.composite(a, Image.new("L", (W, W), 0), mask.filter(ImageFilter.GaussianBlur(S))))
    save(img, (px, px), name)


def make_label(name, px):
    """Inventory label: white paper slightly yellowed, a barcode and digits below it, a frame; one corner
    rubbed and dirty.
    """
    h = int(round(px * LABEL_H / LABEL_W))
    W, H = px * S, h * S
    img = Image.new("RGBA", (W, H), (226, 222, 206, 255))
    d = ImageDraw.Draw(img)
    rnd = random.Random(5)
    x = W * 0.08
    while x < W * 0.92:
        bw = rnd.choice((1, 1, 2, 3)) * S * 0.9
        if rnd.random() < 0.62:
            d.rectangle([x, H * 0.12, x + bw, H * 0.66], fill=(28, 28, 30, 255))
        x += bw + rnd.choice((1, 1, 2)) * S * 0.9
    f = font(int(H * 0.24))
    d.text((W * 0.5, H * 0.82), "3 004512 07", fill=(36, 36, 38, 255), font=f, anchor="mm")
    d.rectangle([S, S, W - S - 1, H - S - 1], outline=(150, 146, 132, 255), width=S)
    grime = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grime)
    gd.ellipse([-W * 0.25, H * 0.45, W * 0.25, H * 1.6], fill=(120, 104, 70, 90))
    gd.ellipse([W * 0.7, -H * 0.6, W * 1.2, H * 0.4], fill=(120, 104, 70, 60))
    img = Image.alpha_composite(img, grime.filter(ImageFilter.GaussianBlur(H * 0.12)))
    save(img, (px, h), name)


if __name__ == "__main__":
    make_lcd("decal_lcd_off.png", 256, False)
    for i in range(LCD_FRAMES):
        make_lcd("decal_lcd_f%02d.png" % i, 256, True, i)
    make_silk("decal_silk.png", 256)
    make_keys("decal_keys.png", 384)
    make_hotsync("decal_hotsync.png", 128)
    make_label("decal_label.png", 192)
