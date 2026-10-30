"""Decals and images for the M22 bar counter (system Python + Pillow). No letters: only digits of
the keys, displays and scales, Roman numerals and signs on the function keys.

- decal_keys.png - digits and signs on the raised keys of the "Oka" register (a projection from
  above, at the key positions of layout.keys(); the cashier stands at +y, so the signs are turned
  toward him);
- decal_disp_off.png, decal_disp_fNN.png - the register display (own texture, section disp: the
  customer window and the cashier window): seven-segment digits behind dark glass; "off" is dark
  with barely visible segments, the "working" frames are entering a sum and the total
  (layout.DISP_FRAMES), the digits glow;
- decal_scale_off.png / decal_scale_on.png - the VEF-202 scale (the needle is a separate part, a bone);
- decal_grille.png - the radio speaker grille;
- decal_top.png - the countertop: mug rings, spilled beer, burns by the ashtray, cuts.

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 2                                   # supersampling, then downscaling - smooth edges
PX_M = 3000                             # pixels per meter (keys, scale, grille)


def font(px):
    for name in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            pass
    return ImageFont.load_default()


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, size)


def px(m):
    return int(round(m * PX_M * S))


def text_c(d, xy, s, f, fill):
    x, y = xy
    b = d.textbbox((0, 0), s, font=f)
    d.text((x - (b[2] - b[0]) / 2 - b[0], y - (b[3] - b[1]) / 2 - b[1]), s, font=f, fill=fill)


# --- keys -------------------------------------------------------------------------------------------
def glyph(s, h_px, ink):
    """Key sign upright (as the cashier sees it): RGBA with a transparent background."""
    f = font(h_px)
    b = f.getbbox(s)
    w, h = b[2] - b[0] + 4, b[3] - b[1] + 4
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - b[0], 2 - b[1]), s, font=f, fill=ink)
    return im


def make_keys():
    """Digits and signs on the key tops. A projection from above in world axes: x is right, y is up in
    the image. The cashier stands at +y facing -y: the "top" of his keyboard points to -y and his left
    hand to +x, so the signs are rotated by 180 degrees; the key top lies on the slope, so it is shorter
    along y (KB_V)."""
    (cx, cy), (w, h) = L.KEYS_C, L.KEYS_S
    W, H = px(w), px(h)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    k = PX_M * S
    fore = abs(L.KB_V[1])
    ink_dark, ink_light = (34, 32, 28, 255), (226, 224, 216, 255)
    for col, a, b, wa, wb, mark in L.keys():
        if not mark:
            continue
        x, y, _ = L.kb_point(a, b, L.WELL_H + L.KEY_H)
        ink = ink_dark if col == "cream" else ink_light
        hm = 0.0085 if len(mark) == 1 else 0.0062
        gl = glyph(mark, int(hm * k), ink).rotate(180)
        gl = gl.resize((gl.width, max(1, int(gl.height * fore))), Image.LANCZOS)
        u = (x - (cx - w / 2)) * k
        v = ((cy + h / 2) - y) * k
        img.alpha_composite(gl, (int(u - gl.width / 2), int(v - gl.height / 2)))
    save(img, (W // S, H // S), "decal_keys.png")


# --- display: seven segments ------------------------------------------------------------------------
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
       "7": "abc", "8": "abcdefg", "9": "abcdfg", "-": "g", " ": ""}


def seg_polys(x0, y0, cw, ch, t, slant):
    """Segments a..g of a cell (x0, y0 - top left, cw x ch), thickness t, slant (a fraction of the height)."""
    def P(x, y):
        return (x0 + x + slant * (ch - y), y0 + y)

    def hseg(y):
        return [P(t * 0.9, y), P(t * 1.4, y - t / 2), P(cw - t * 1.4, y - t / 2), P(cw - t * 0.9, y),
                P(cw - t * 1.4, y + t / 2), P(t * 1.4, y + t / 2)]

    def vseg(x, ya, yb):
        return [P(x, ya + t * 0.9), P(x + t / 2, ya + t * 1.4), P(x + t / 2, yb - t * 1.4), P(x, yb - t * 0.9),
                P(x - t / 2, yb - t * 1.4), P(x - t / 2, ya + t * 1.4)]
    m = ch / 2
    return {"a": hseg(t / 2), "g": hseg(m), "d": hseg(ch - t / 2),
            "f": vseg(t / 2, 0, m), "b": vseg(cw - t / 2, 0, m),
            "e": vseg(t / 2, m, ch), "c": vseg(cw - t / 2, m, ch)}


def disp_image(text, lit):
    """Oka display: 7 positions right to left, the point goes after the digit, "*" is the total mark on the right."""
    W, H = 600 * S, 104 * S
    base = Image.new("RGBA", (W, H), (7, 12, 12, 255))
    d = ImageDraw.Draw(base)
    # glass: slightly lighter at the bottom, a highlight along the top
    for y in range(H):
        f = y / H
        d.line([(0, y), (W, y)], fill=(7 + int(6 * f), 12 + int(8 * f), 13 + int(8 * f), 255))
    cells, cw, ch, t = 7, 44 * S, 78 * S, 8 * S
    gap = 22 * S
    x_right = W - 64 * S
    y0 = (H - ch) // 2
    star = text.endswith("*")
    body = text.rstrip("*")
    glyphs = []
    for c in body:
        if c == "." and glyphs:
            glyphs[-1] = (glyphs[-1][0], True)
        else:
            glyphs.append((c, False))
    glyphs = [(" ", False)] * (cells - len(glyphs)) + glyphs
    ghost = (22, 36, 34, 255)
    on = (110, 255, 214, 255)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    for i, (c, dp) in enumerate(glyphs):
        x0 = x_right - (cells - i) * (cw + gap)
        polys = seg_polys(x0, y0, cw, ch, t, 0.10)
        for name, poly in polys.items():
            d.polygon(poly, fill=ghost)
            if lit and name in SEG.get(c, ""):
                dl.polygon(poly, fill=on)
        dpx, dpy = x0 + cw + gap * 0.35, y0 + ch - t * 0.6
        d.ellipse([dpx - t * 0.55, dpy - t * 0.55, dpx + t * 0.55, dpy + t * 0.55], fill=ghost)
        if lit and dp:
            dl.ellipse([dpx - t * 0.55, dpy - t * 0.55, dpx + t * 0.55, dpy + t * 0.55], fill=on)
    # total mark "*" on the right
    sx, sy, sr = W - 30 * S, y0 + ch * 0.3, 11 * S
    for k in range(3):
        a = math.pi * k / 3
        seg = [(sx - sr * math.cos(a), sy - sr * math.sin(a)), (sx + sr * math.cos(a), sy + sr * math.sin(a))]
        d.line(seg, fill=ghost, width=4 * S)
        if lit and star:
            dl.line(seg, fill=on, width=4 * S)
    if lit:
        glow = layer.filter(ImageFilter.GaussianBlur(8 * S))
        base = Image.alpha_composite(base, glow)
        base = Image.alpha_composite(base, glow)
        base = Image.alpha_composite(base, layer)
    # highlight along the top of the glass
    hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(hl).polygon([(0, 0), (W, 0), (W, H * 0.18), (0, H * 0.32)], fill=(255, 255, 255, 14))
    base = Image.alpha_composite(base, hl)
    return base


def make_disp():
    save(disp_image("8888888", False), (600, 104), "decal_disp_off.png")
    for i, txt in enumerate(L.DISP_FRAMES):
        save(disp_image(txt, True), (600, 104), "decal_disp_f%02d.png" % i)


# --- radio ------------------------------------------------------------------------------------------
def make_scale(on):
    """VEF-202 scale: five bands as rows, divisions and frequency digits. "Working" - backlit with warm
    light, "off" - dim, behind dusty glass. The needle is a separate part (moves when "working")."""
    w, h = L.SCALE_S
    W, H = px(w), px(h)
    bg = (250, 222, 150) if on else (104, 98, 84)
    ink = (60, 36, 20) if on else (36, 34, 30)
    img = Image.new("RGBA", (W, H), bg + (255,))
    d = ImageDraw.Draw(img)
    rnd = random.Random(5)
    rows = 5
    f = font(int(H / rows * 0.55))
    nums = [("150", "200", "250", "300", "350", "400"), ("55", "60", "70", "80", "100", "150"),
            ("25", "31", "41", "49", "62", "75"), ("19", "21", "25", "31", "41", "49"),
            ("11", "13", "16", "19", "21", "25")]
    for r in range(rows):
        y0 = H * (r + 0.1) / rows
        y1 = H * (r + 0.9) / rows
        d.line([W * 0.08, y1, W * 0.94, y1], fill=ink, width=S * 2)
        for i in range(31):
            x = W * 0.08 + (W * 0.86) * i / 30
            d.line([x, y1, x, y1 - (y1 - y0) * (0.35 if i % 5 else 0.6)], fill=ink, width=S * 2)
        for i, n in enumerate(nums[r]):
            x = W * 0.08 + (W * 0.86) * (i * 6 + rnd.randint(0, 2)) / 32
            text_c(d, (x + W * 0.02, (y0 + y1) / 2 - H * 0.02), n, f, ink)
        # band mark on the left - a small square instead of letters
        d.rectangle([W * 0.015, y0 + (y1 - y0) * 0.2, W * 0.045, y1 - (y1 - y0) * 0.1], fill=ink)
    if not on:
        for _ in range(160):
            x, y = rnd.uniform(0, W), rnd.uniform(0, H)
            r = rnd.uniform(1, 4) * S
            d.ellipse([x - r, y - r, x + r, y + r], fill=(130, 126, 114, 60))
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 40, 40, 255), width=S * 4)
    save(img, (W // S, H // S), "decal_scale_%s.png" % ("on" if on else "off"))


def make_grille():
    """Speaker grille: silver perforated tin, holes in staggered rows, chrome horizontal strips on the left."""
    w, h = L.GRILLE_S
    W, H = px(w), px(h)
    img = Image.new("RGBA", (W, H), (176, 178, 176, 255))
    d = ImageDraw.Draw(img)
    k = W / w
    step = 0.0045 * k
    r = 0.0012 * k
    y = step / 2
    row = 0
    while y < H:
        x = step / 2 + (step / 2 if row % 2 else 0)
        while x < W:
            d.ellipse([x - r, y - r, x + r, y + r], fill=(30, 30, 32, 255))
            x += step
        y += step * 0.87
        row += 1
    for i in range(4):
        y = H * (0.15 + 0.22 * i)
        d.rectangle([0, y, W * 0.18, y + 0.005 * k], fill=(220, 222, 220, 255))
    d.rectangle([0, 0, W - 1, H - 1], outline=(110, 110, 108, 255), width=S * 4)
    save(img, (W // S, H // S), "decal_grille.png")


# --- countertop -------------------------------------------------------------------------------------
def make_top():
    """Stains on the countertop (a projection from above): rings from mug bottoms (current mugs and old
    ones all over the counter), spilled beer streaks, cigarette burns by the ashtray and at the edge,
    knife cuts."""
    ppm = 500 * S
    (cx, cy), (w, h) = L.TOP_C, L.TOP_S
    W, H = int(w * ppm), int(h * ppm)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rnd = random.Random(2210)

    def P(x, y):
        return ((x - (cx - w / 2)) * ppm, ((cy + h / 2) - y) * ppm)

    def ring(x, y, r, a, width_m=0.0022, part=1.0, col=(46, 26, 12)):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        u, v = P(x, y)
        rr = r * ppm
        start = rnd.uniform(0, 360)
        d.arc([u - rr, v - rr, u + rr, v + rr], start, start + 360 * part, fill=col + (a,),
              width=max(2, int(width_m * ppm)))
        img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(1.2 * S)))

    def blot(x, y, r, a, col=(52, 30, 12), n=7):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for _ in range(n):
            u, v = P(x + rnd.uniform(-r, r) * 0.6, y + rnd.uniform(-r, r) * 0.4)
            rx, ry = rnd.uniform(0.4, 1.0) * r * ppm, rnd.uniform(0.3, 0.7) * r * ppm
            d.ellipse([u - rx, v - ry, u + rx, v + ry], fill=col + (a,))
        img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(6 * S)))

    # beer is spilled by the mugs and at the edge toward the player
    for x, y, _, beer in L.MUGS_TOP:
        if beer:
            blot(x + 0.03, y - 0.02, 0.06, 60)
    blot(0.30, -0.27, 0.10, 40)
    blot(-0.70, -0.26, 0.08, 36)
    blot(-0.15, 0.20, 0.07, 34)
    # rings from bottoms: by the mugs and old ones
    for x, y, _, beer in L.MUGS_TOP:
        ring(x + rnd.uniform(-0.01, 0.01), y + rnd.uniform(-0.01, 0.01), 0.041, 130, part=0.85)
        ring(x + 0.05, y + 0.03, 0.041, 80, part=0.6)
    for _ in range(18):
        x, y = rnd.uniform(-1.0, 1.0), rnd.uniform(-0.30, 0.30)
        if abs(x - L.RX) < 0.2 and -0.08 < y < 0.31:
            continue                                      # not visible under the register
        ring(x, y, rnd.choice((0.041, 0.036, 0.034)), rnd.randint(45, 95), part=rnd.uniform(0.4, 0.95))
    # burns: a dark core, a reddish rim
    for _ in range(9):
        if rnd.random() < 0.6:
            x, y = L.ASHTRAY[0] + rnd.uniform(-0.12, 0.14), L.ASHTRAY[1] + rnd.uniform(-0.12, 0.10)
        else:
            x, y = rnd.uniform(-0.9, 0.9), -0.30 + rnd.uniform(0.0, 0.04)
        u, v = P(x, y)
        ang = rnd.uniform(0, math.pi)
        ln, th = rnd.uniform(0.007, 0.012) * ppm, rnd.uniform(0.0025, 0.004) * ppm
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for sc, col in ((1.8, (120, 62, 22, 70)), (1.0, (24, 14, 8, 200))):
            pts = [(u + math.cos(ang) * ln * sc * math.cos(t) - math.sin(ang) * th * sc * math.sin(t),
                    v + math.sin(ang) * ln * sc * math.cos(t) + math.cos(ang) * th * sc * math.sin(t))
                   for t in [2 * math.pi * k / 16 for k in range(16)]]
            d.polygon(pts, fill=col)
        img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(1.0 * S)))
    # knife cuts: thin light lines
    d = ImageDraw.Draw(img)
    for _ in range(26):
        x, y = rnd.uniform(-1.05, 1.05), rnd.uniform(-0.31, 0.32)
        ang = rnd.uniform(-0.5, 0.5) + (0.0 if rnd.random() < 0.7 else math.pi / 2)
        ln = rnd.uniform(0.02, 0.09)
        u0, v0 = P(x, y)
        u1, v1 = P(x + math.cos(ang) * ln, y + math.sin(ang) * ln)
        d.line([(u0, v0), (u1, v1)], fill=(196, 160, 118, rnd.randint(50, 95)), width=max(1, S))
    save(img, (W // S, H // S), "decal_top.png")


make_keys()
make_disp()
make_scale(False)
make_scale(True)
make_grille()
make_top()
