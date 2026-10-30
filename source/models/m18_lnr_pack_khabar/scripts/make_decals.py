"""Decals for the bartender's safe (system Python + Pillow): the code dial scale (100 divisions, digits
every 10 - digits on a dial are allowed), enamel wear around the wheel handle and the dial (patches of
primer and metal, semi-transparent, laid on the door face over the enamel), a blank nameplate with a
frame and rivets - no letters or logos; a golden trim line on the door and the sides (frames with
concave corners, as on old fireproof cabinets; worn in places) and the leather pad under the loupe:
stitching along the edge and a ring pressed by the loupe bell.

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import m18_layout as L

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges


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


def make_dial(name, n):
    """Code dial face: bronze, a ring with divisions and digits 0..90 near the edge, a smooth centre;
    transparent outside the circle."""
    W = n * S
    c = W / 2
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, W - 1, W - 1], fill=(150, 116, 62, 255))
    d.ellipse([W * 0.30, W * 0.30, W * 0.70, W * 0.70], fill=(132, 100, 52, 255))
    ink = (40, 30, 18, 255)
    f = font(int(W * 0.075))
    for k in range(100):
        a = 2 * math.pi * k / 100 - math.pi / 2
        r0 = c * (0.80 if k % 10 == 0 else (0.86 if k % 5 == 0 else 0.90))
        d.line([(c + r0 * math.cos(a), c + r0 * math.sin(a)), (c + c * 0.97 * math.cos(a), c + c * 0.97 * math.sin(a))],
               fill=ink, width=S * (3 if k % 10 == 0 else 2))
        if k % 10 == 0:
            rt = c * 0.66
            d.text((c + rt * math.cos(a), c + rt * math.sin(a)), str(k), fill=ink, font=f, anchor="mm")
    # glints polished by fingers along the ring
    rnd = random.Random(18)
    hl = Image.new("L", (W, W), 0)
    hd = ImageDraw.Draw(hl)
    for _ in range(18):
        a = rnd.uniform(0, 2 * math.pi)
        r = c * rnd.uniform(0.35, 0.95)
        s = W * rnd.uniform(0.02, 0.05)
        hd.ellipse([c + r * math.cos(a) - s, c + r * math.sin(a) - s, c + r * math.cos(a) + s, c + r * math.sin(a) + s],
                   fill=rnd.randint(30, 70))
    hl = hl.filter(ImageFilter.GaussianBlur(W * 0.02))
    img = Image.composite(Image.new("RGBA", (W, W), (196, 164, 100, 255)), img, hl)
    mask = Image.new("L", (W, W), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, W - 1, W - 1], fill=255)
    img.putalpha(mask)
    save(img, (n, n), name)


def make_wear(name, w, h, spots):
    """Enamel wear at the handle and the dial: calm patches lighter than the enamel (rubbed by hands),
    inside - orange primer and bare metal. spots - [(cx, cy, r)] in image fractions: where hands take hold.
    A transparent decal over the door enamel."""
    W, H = w * S, h * S
    rnd = random.Random(7)
    a_rub = Image.new("L", (W, H), 0)
    a_primer = Image.new("L", (W, H), 0)
    a_metal = Image.new("L", (W, H), 0)
    dr, dp, dm = ImageDraw.Draw(a_rub), ImageDraw.Draw(a_primer), ImageDraw.Draw(a_metal)
    for cx, cy, r in spots:
        for _ in range(70):
            a = rnd.uniform(0, 2 * math.pi)
            q = rnd.random() ** 0.7
            x, y = W * cx + W * r * q * math.cos(a), H * cy + W * r * q * math.sin(a)
            s = W * r * rnd.uniform(0.10, 0.28)
            dr.ellipse([x - s, y - s * 0.7, x + s, y + s * 0.7], fill=rnd.randint(120, 210))
            if q < 0.8 and rnd.random() < 0.6:
                s2 = s * rnd.uniform(0.25, 0.6)
                dp.ellipse([x - s2, y - s2 * 0.6, x + s2, y + s2 * 0.6], fill=rnd.randint(140, 230))
                if rnd.random() < 0.35:
                    s3 = s2 * 0.5
                    dm.ellipse([x - s3, y - s3 * 0.6, x + s3, y + s3 * 0.6], fill=rnd.randint(160, 240))
    a_rub = a_rub.filter(ImageFilter.GaussianBlur(W * 0.03))
    a_primer = a_primer.filter(ImageFilter.GaussianBlur(W * 0.004))
    a_metal = a_metal.filter(ImageFilter.GaussianBlur(W * 0.003))
    img = Image.new("RGBA", (W, H), (146, 104, 74, 0))
    img.putalpha(a_rub)
    for col, a in (((120, 58, 32, 255), a_primer), ((128, 122, 112, 255), a_metal)):
        layer = Image.new("RGBA", (W, H), col)
        img = Image.composite(layer, img, a)
    save(img, (w, h), name)


def make_plate(name, w, h):
    """Blank nameplate: brass, edge, four rivets, the inscriptions are rubbed off - only scratches."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (164, 132, 72, 255))
    d = ImageDraw.Draw(img)
    m = S * 6
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=H * 0.25, outline=(96, 72, 36, 255), width=S * 5)
    d.rounded_rectangle([m * 2, m * 2, W - 1 - m * 2, H - 1 - m * 2], radius=H * 0.18, outline=(120, 92, 46, 255),
                        width=S * 2)
    for x, y in ((0.07, 0.25), (0.93, 0.25), (0.07, 0.75), (0.93, 0.75)):
        r = H * 0.07
        d.ellipse([W * x - r, H * y - r, W * x + r, H * y + r], fill=(110, 84, 42, 255))
    rnd = random.Random(3)
    for _ in range(40):
        x, y = rnd.uniform(W * 0.15, W * 0.85), rnd.uniform(H * 0.3, H * 0.7)
        l = rnd.uniform(W * 0.01, W * 0.06)
        a = rnd.uniform(-0.5, 0.5)
        d.line([(x, y), (x + l * math.cos(a), y + l * math.sin(a))], fill=(186, 156, 96, 255), width=S)
    save(img, (w, h), name)


def notched_frame(d, box, corner, width):
    """Frame with concave corners: straight lines along the sides and quarter circles around the vertices (px)."""
    x0, y0, x1, y1 = box
    c = corner
    d.line([(x0 + c, y0), (x1 - c, y0)], fill=255, width=width)
    d.line([(x0 + c, y1), (x1 - c, y1)], fill=255, width=width)
    d.line([(x0, y0 + c), (x0, y1 - c)], fill=255, width=width)
    d.line([(x1, y0 + c), (x1, y1 - c)], fill=255, width=width)
    for (cx, cy), (a0, a1) in (((x0, y0), (0, 90)), ((x1, y0), (90, 180)), ((x1, y1), (180, 270)),
                               ((x0, y1), (270, 360))):
        d.arc([cx - c, cy - c, cx + c, cy + c], a0, a1, fill=255, width=width)


def make_pinstripe(name, size, frames, ppm, seed, color=(178, 138, 64)):
    """Trim line: golden frames with concave corners on a transparent field. size - (width, height) of the
    field, m; frames - [(inset from the field edge, line width, corner radius)], m. The paint is old: worn in
    patches and thinner at the edges."""
    w, h = int(round(size[0] * ppm)), int(round(size[1] * ppm))
    W, H = w * S, h * S
    k = ppm * S
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    for inset, lw, corner in frames:
        e = inset * k
        notched_frame(d, (e, e, W - 1 - e, H - 1 - e), corner * k, max(S, int(round(lw * k))))
    mask = mask.filter(ImageFilter.GaussianBlur(S * 0.6))
    # worn: light and dark alpha patches, small bald spots
    rnd = random.Random(seed)
    keep = Image.new("L", (W, H), 235)
    kd = ImageDraw.Draw(keep)
    for _ in range(int(60 * size[0] * size[1] / 0.5) + 20):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        s = k * rnd.uniform(0.004, 0.03)
        kd.ellipse([x - s, y - s * rnd.uniform(0.3, 1.0), x + s, y + s * rnd.uniform(0.3, 1.0)],
                   fill=rnd.randint(0, 150))
    keep = keep.filter(ImageFilter.GaussianBlur(k * 0.002))
    alpha = Image.composite(keep, Image.new("L", (W, H), 0), mask)
    img = Image.new("RGBA", (W, H), color + (0,))
    img.putalpha(alpha)
    save(img, (w, h), name)


def make_pad(name, ppm):
    """Leather pad under the loupe: stitching along the edge, a ring pressed by the loupe bell (darker,
    greasy) and a couple of scuffs. The field is the whole pad, the image top is the back (+y)."""
    cx, cy, pw, ph, _ = L.PAD
    w, h = int(round(pw * ppm)), int(round(ph * ppm))
    W, H = w * S, h * S
    k = ppm * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # stitching: 4 mm strokes every 2.5 mm, 7 mm from the edge
    st = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(st)
    e = 0.007 * k
    dash, gap = 0.004 * k, 0.0025 * k
    for (xa, ya), (xb, yb) in ((((e, e), (W - e, e))), ((W - e, e), (W - e, H - e)), ((W - e, H - e), (e, H - e)),
                               ((e, H - e), (e, e))):
        length = math.hypot(xb - xa, yb - ya)
        n = int(length // (dash + gap))
        for i in range(n):
            t0, t1 = i * (dash + gap) / length, (i * (dash + gap) + dash) / length
            d.line([(xa + (xb - xa) * t0, ya + (yb - ya) * t0), (xa + (xb - xa) * t1, ya + (yb - ya) * t1)],
                   fill=230, width=max(S, int(0.0012 * k)))
    img = Image.composite(Image.new("RGBA", (W, H), (176, 138, 96, 255)), img, st)
    # trace of the loupe bell: a ring, darker and greasy
    bx, by, br = L.LOUPE_BELL
    px, py = (bx - (cx - pw / 2)) * k, ((cy + ph / 2) - by) * k
    ring = Image.new("L", (W, H), 0)
    rd = ImageDraw.Draw(ring)
    r = br * k
    rd.ellipse([px - r, py - r, px + r, py + r], outline=150, width=int(0.005 * k))
    rd.ellipse([px - r * 0.8, py - r * 0.8, px + r * 0.8, py + r * 0.8], fill=40)
    ring = ring.filter(ImageFilter.GaussianBlur(0.0015 * k))
    img = Image.composite(Image.new("RGBA", (W, H), (34, 22, 14, 255)), img, ring)
    # scuffs where hands and things go: light patches
    rnd = random.Random(23)
    sc = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(sc)
    for _ in range(40):
        x, y = rnd.uniform(0.1, 0.9) * W, rnd.uniform(0.45, 0.95) * H
        s = k * rnd.uniform(0.0015, 0.005)
        sd.ellipse([x - s * 2.5, y - s, x + s * 2.5, y + s], fill=rnd.randint(30, 90))
    sc = sc.filter(ImageFilter.GaussianBlur(0.001 * k))
    img = Image.composite(Image.new("RGBA", (W, H), (150, 112, 78, 255)), img, sc)
    save(img, (w, h), name)


if __name__ == "__main__":
    make_dial("decal_dial.png", 512)
    # door face at the handle: a 0.40 x 0.62 m image centred on the door axis, z 0.62..1.24; the handle is at
    # 0.74, the dial at 1.02 (WEAR in m18_layout.py; image rows go top to bottom)
    make_wear("decal_door_wear.png", 512, 794, [(0.50, 0.81, 0.30), (0.50, 0.355, 0.16)])
    make_plate("decal_plate.png", 512, 256)
    # door trim line: the field is the whole door; the outer line 2.5
    # mm at PIN_IN from the edge, the inner 1 mm - 8 mm deeper
    door = (L.DX1 - L.DX0, L.DZ1 - L.DZ0)
    make_pinstripe("decal_pin_door.png", door, [(L.PIN_IN, 0.0025, 0.030), (L.PIN_IN + 0.008, 0.001, 0.022)], 1400, 31)
    # sides: the field is the whole side (depth x body height)
    side = (L.Y1 - L.Y0, L.ZR - L.ZB)
    make_pinstripe("decal_pin_side.png", side, [(L.PIN_SIDE, 0.0025, 0.034), (L.PIN_SIDE + 0.008, 0.001, 0.026)], 1100, 37)
    make_pad("decal_pad.png", 2400)
