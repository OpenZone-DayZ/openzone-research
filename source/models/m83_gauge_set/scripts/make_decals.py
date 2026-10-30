"""Decals of the gauge set (system Python + Pillow). Digits only, no letters:

- stamps on the insert: gauge numbers punched into the wood, the left group "2" (the bore gauge)
  and "3", "4", "5" (go, no-go and reject plug gauges), like the digits under the sockets of the
  Ericsson box; on the real 56-I-01 the numbers are on the gauges themselves;
- group plates: aluminium, a black field, raised light marks and two rivets at the edges - as on
  the 56-I-01 "56-I-212 / 231 / 327", but without the letter: "56-212", "56-231", "56-327"; the
  set plate "56-01" is the same;
- the inventory in the lid: yellowed paper, a typewritten table - number, index, quantity
  (digits), a round violet stamp with a star and no text; corners with glue and dirt;
- the acceptance stamp on the front wall: a violet rectangle, a star and digits.

    python make_decals.py      -> ../work/decal_*.png

Sizes match build_m83.py (INSERT_*, PLATES, PAPER_*, FRONT_*). The pictures are drawn "top toward
the back wall" (insert, plates) and "top up" (inventory, stamp); how they lie is in build_m83.py.
"""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
FONTS = "C:/Windows/Fonts/"

# insert: x -0.091..0.091, y (from the middle of the box) -0.052..0.052; stamps - (text, x, y,
# height), m
INSERT_W, INSERT_H = 0.182, 0.104
STAMPS = [("2", -0.034, 0.0292, 0.0060), ("3", -0.0755, 0.0050, 0.0060), ("4", -0.0090, 0.0050, 0.0060),
          ("5", -0.0450, -0.0170, 0.0060)]
# plates: (text, width, height), m
PLATES = {"01": ("56-01", 0.032, 0.0080), "212": ("56-212", 0.024, 0.0068), "231": ("56-231", 0.024, 0.0068),
          "327": ("56-327", 0.024, 0.0068)}
PAPER_W, PAPER_H = 0.120, 0.074
FRONT_W, FRONT_H = 0.028, 0.015


def font(name, px):
    try:
        return ImageFont.truetype(FONTS + name, max(8, int(px)))
    except OSError:
        return ImageFont.load_default()


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def blotches(size, seed, n, rmin, rmax, fill_lo, fill_hi, blur):
    """Mask of patches (0..255): wear, uneven pressure."""
    rnd = random.Random(seed)
    w, h = size
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    for _ in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.uniform(rmin, rmax) * w
        d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=rnd.randint(fill_lo, fill_hi))
    return m.filter(ImageFilter.GaussianBlur(blur))


def centered(d, cx, cy, text, fnt, **kw):
    l, t, r, b = d.textbbox((0, 0), text, font=fnt)
    d.text((cx - (r - l) / 2 - l, cy - (b - t) / 2 - t), text, font=fnt, **kw)


def star(d, cx, cy, r, fill, rot=-90):
    pts = []
    for i in range(10):
        a = math.radians(rot + 36 * i)
        rr = r if i % 2 == 0 else r * 0.40
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    d.polygon(pts, fill=fill)


# --- stamps on the insert -------------------------------------------------------------------------
def make_insert(name, px_mm=6):
    """Punched digits: a dark impression bottom (the wood is crushed and greasy), a light rim on one
    side; the impression is uneven - the pressure varies across the digit.
    """
    W, H = int(INSERT_W * 1000 * px_mm) * S, int(INSERT_H * 1000 * px_mm) * S
    k = W / (INSERT_W * 1000)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    for text, x, y, h in STAMPS:
        cx, cy = (x + INSERT_W / 2) * 1000 * k, (INSERT_H / 2 - y) * 1000 * k
        centered(md, cx, cy, text, font("ARIALNB.TTF", h * 1000 * k * 1.28), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0.12 * k))
    press = blotches((W, H), 83, 120, 0.004, 0.012, 200, 255, 0.6 * k)
    deep = ImageChops.multiply(mask, press)
    off = max(1, int(0.25 * k))
    rim = ImageChops.subtract(ImageChops.offset(mask, -off, -off), mask)
    img = Image.composite(Image.new("RGBA", (W, H), (226, 170, 104, 255)), img, rim.point(lambda v: int(v * 0.55)))
    img = Image.composite(Image.new("RGBA", (W, H), (58, 28, 10, 255)), img, deep.point(lambda v: int(v * 0.95)))
    save(img, (W // S, H // S), name)


# --- plates ---------------------------------------------------------------------------------------
def make_plate(name, text, w, h, px_mm=24):
    """Aluminium plate: a light edge, a black field (enamel), raised marks - bare metal, the paint is
    worn off them; two rivets in the field at the edges; scratches and dull patches on the edge.
    """
    W, H = int(w * 1000 * px_mm) * S, int(h * 1000 * px_mm) * S
    k = W / (w * 1000)
    rnd = random.Random(sum(map(ord, text)))
    img = Image.new("RGBA", (W, H), (176, 178, 176, 255))
    d = ImageDraw.Draw(img)
    e = 0.55 * k
    d.rounded_rectangle([e, e, W - e, H - e], radius=int(0.5 * k), fill=(24, 24, 26, 255))
    fnt = font("arialbd.ttf", H * 0.62)
    glyph = Image.new("L", (W, H), 0)
    centered(ImageDraw.Draw(glyph), W / 2, H / 2, text, fnt, fill=255)
    img = Image.composite(Image.new("RGBA", (W, H), (196, 198, 196, 255)), img, glyph)
    # relief shadow under the marks
    sh = ImageChops.subtract(ImageChops.offset(glyph, int(0.12 * k), int(0.14 * k)), glyph)
    img = Image.composite(Image.new("RGBA", (W, H), (6, 6, 7, 255)), img, sh)
    d = ImageDraw.Draw(img)
    for cx in (1.6 * k, W - 1.6 * k):
        r = 0.9 * k
        d.ellipse([cx - r, H / 2 - r, cx + r, H / 2 + r], fill=(150, 152, 150, 255))
        d.arc([cx - r, H / 2 - r, cx + r, H / 2 + r], 200, 320, fill=(220, 222, 220, 255), width=int(0.2 * k))
        d.arc([cx - r, H / 2 - r, cx + r, H / 2 + r], 20, 140, fill=(70, 72, 72, 255), width=int(0.2 * k))
    # scratches and dullness
    for _ in range(6):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        a = math.radians(rnd.uniform(-25, 25))
        L = rnd.uniform(3, 10) * k
        d.line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], fill=(120, 122, 120, 140), width=max(1, S // 2))
    dull = blotches((W, H), rnd.randint(0, 999), 14, 0.03, 0.10, 20, 70, 1.5 * k)
    img = Image.composite(Image.new("RGBA", (W, H), (96, 92, 84, 255)), img, dull)
    save(img, (W // S, H // S), name)


# --- inventory in the lid -------------------------------------------------------------------------
def make_paper(name, px_mm=8):
    """Yellowed sheet: a table in 4 columns (number, gauge index, quantity, tick), typewritten digits; a
    violet round stamp with a star and a rim without letters; glue showed through in patches along the
    edges, the corners are greasy from fingers, fading over the sheet.
    """
    W, H = int(PAPER_W * 1000 * px_mm) * S, int(PAPER_H * 1000 * px_mm) * S
    k = W / (PAPER_W * 1000)
    rnd = random.Random(5601)
    img = Image.new("RGBA", (W, H), (214, 200, 160, 255))
    tone = blotches((W, H), 11, 40, 0.05, 0.20, 0, 60, 6 * k)
    img = Image.composite(Image.new("RGBA", (W, H), (190, 168, 118, 255)), img, tone)
    d = ImageDraw.Draw(img)
    ink = (52, 50, 56, 235)
    lw = max(2, int(0.22 * k))
    x0, x1, y0 = 6.0 * k, 114.0 * k, 8.0 * k
    cols = [x0, 16.0 * k, 64.0 * k, 84.0 * k, x1]
    rows = 10
    rh = 5.6 * k
    for i in range(rows + 1):
        y = y0 + i * rh
        d.line([(x0, y), (x1, y)], fill=ink, width=lw * (2 if i in (0, 1, rows) else 1))
    for x in cols:
        d.line([(x, y0), (x, y0 + rows * rh)], fill=ink, width=lw)
    tf = font("cour.ttf", rh * 0.78)
    head = ["1", "2", "3", "4"]
    for c, txt in enumerate(head):
        centered(d, (cols[c] + cols[c + 1]) / 2, y0 + rh * 0.52, txt, tf, fill=ink)
    lines = [("1", "212-231-327-2", "1"), ("2", "212-231-327-3", "1"), ("3", "212-231-327-4", "1"),
             ("4", "212-231-327-5", "1"), ("5", "212-231-1", "1"), ("6", "212-6", "1"), ("7", "231-6", "1"),
             ("8", "327-1", "1"), ("9", "327-6", "1")]
    for i, (n, idx, q) in enumerate(lines):
        y = y0 + (i + 1.52) * rh
        jit = rnd.uniform(-0.25, 0.25) * k
        centered(d, (cols[0] + cols[1]) / 2 + jit, y, n, tf, fill=ink)
        d.text((cols[1] + 1.6 * k + jit, y - rh * 0.40), idx, font=tf, fill=ink)
        centered(d, (cols[2] + cols[3]) / 2 + jit, y, q, tf, fill=ink)
    # pencil ticks in the last column - someone checked
    pencil = (84, 84, 90, 200)
    for i in range(9):
        if i in (6,):
            continue
        cx, cy = (cols[3] + cols[4]) / 2 + rnd.uniform(-3, 3) * k, y0 + (i + 1.5) * rh
        d.line([(cx - 2.0 * k, cy - 0.3 * k), (cx - 0.6 * k, cy + 1.4 * k), (cx + 2.6 * k, cy - 2.0 * k)],
               fill=pencil, width=max(2, int(0.35 * k)), joint="curve")
    # stamp: a double ring, a star; the paint lay unevenly
    stamp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    vio = (104, 62, 150, 200)
    cx, cy, R = 92.0 * k, 64.0 * k, 9.0 * k
    sd.ellipse([cx - R, cy - R, cx + R, cy + R], outline=vio, width=int(0.6 * k))
    sd.ellipse([cx - R * 0.78, cy - R * 0.78, cx + R * 0.78, cy + R * 0.78], outline=vio, width=int(0.4 * k))
    star(sd, cx, cy, R * 0.55, vio)
    for i in range(24):                                     # notches around the ring instead of a legend
        a = math.radians(i * 15)
        sd.line([(cx + math.cos(a) * R * 0.82, cy + math.sin(a) * R * 0.82),
                 (cx + math.cos(a) * R * 0.95, cy + math.sin(a) * R * 0.95)], fill=vio, width=int(0.35 * k))
    stamp = stamp.rotate(14, resample=Image.BICUBIC, center=(cx, cy))
    patchy = blotches((W, H), 77, 60, 0.01, 0.04, 90, 255, 1.0 * k)
    stamp.putalpha(ImageChops.multiply(stamp.getchannel("A"), patchy))
    img = Image.alpha_composite(img, stamp)
    # glue and dirt along the edges, greasy corners
    edge = Image.new("L", (W, H), 0)
    ed = ImageDraw.Draw(edge)
    ed.rectangle([0, 0, W, H], outline=150, width=int(1.6 * k))
    for cxx, cyy in ((0, 0), (W, 0), (0, H), (W, H)):
        r = rnd.uniform(7, 12) * k
        ed.ellipse([cxx - r, cyy - r, cxx + r, cyy + r], fill=rnd.randint(110, 170))
    edge = edge.filter(ImageFilter.GaussianBlur(2.2 * k))
    img = Image.composite(Image.new("RGBA", (W, H), (138, 110, 70, 255)), img, edge)
    # fading: the table is paler in places
    fade = blotches((W, H), 19, 18, 0.06, 0.18, 0, 90, 5 * k)
    img = Image.composite(Image.new("RGBA", (W, H), (206, 190, 150, 255)), img, fade)
    save(img, (W // S, H // S), name)


# --- acceptance stamp on the front wall -----------------------------------------------------------
def make_front(name, px_mm=16):
    """Violet stamp: a frame, a star and the number "47"; the paint is dull, with gaps on wood."""
    W, H = int(FRONT_W * 1000 * px_mm) * S, int(FRONT_H * 1000 * px_mm) * S
    k = W / (FRONT_W * 1000)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    vio = (92, 52, 130, 215)
    d.rectangle([0.8 * k, 0.8 * k, W - 0.8 * k, H - 0.8 * k], outline=vio, width=int(0.7 * k))
    star(d, 7.0 * k, H / 2, 4.2 * k, vio)
    centered(d, 18.5 * k, H / 2, "47", font("arialbd.ttf", 9.0 * k), fill=vio)
    img = img.rotate(-2.5, resample=Image.BICUBIC)
    patchy = blotches((W, H), 47, 50, 0.02, 0.07, 140, 255, 0.8 * k)
    img.putalpha(ImageChops.multiply(img.getchannel("A"), patchy))
    save(img, (W // S, H // S), name)


if __name__ == "__main__":
    make_insert("decal_insert.png")
    for key, (text, w, h) in PLATES.items():
        make_plate("decal_plate_%s.png" % key, text, w, h)
    make_paper("decal_paper.png")
    make_front("decal_front.png")
