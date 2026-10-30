"""Hryvnias for the loot (M13 and M14 hold identical copies of this file): banknote sizes of the
National Bank of Ukraine and a front-side design without inscriptions (project rule: only digits and
pictures).

Sizes, mm (banknotes in circulation): 20 UAH - 130 x 69, 50 - 136 x 72, 100 - 142 x 75, 200 - 148 x 75,
500 - 154 x 75, 1000 - 160 x 75.

Design after the 2014-2019 samples (20 - 2018, 50 - 2019, 100 - 2014, 200 - 2019, 500 - 2015, 1000 - 2019;
colours taken from scans of the front side): a light field on the left, an engraved portrait left of
the middle (each denomination has its own traits: moustache, beard, glasses, beads), on the right a field
in the denomination colour with a picture (palette for 100, lotus for 200, book for 500, flag and rider
for 50, mountains for 20), a security thread, a vertical stripe in the denomination colour with large
digits across it, large denomination digits bottom left and small ones top left, the trident top
centre, ornamental cross stripes near the edges, a tactile mark for the blind (circle - 50, triangle -
20, square - 100, two bars - 200, three dots - 500, three bars - 1000) and embossed strokes at the left
edge. There are no inscriptions: blank where the bank name, the country name, signatures, quotations and
the denomination in words would be.

Denomination colour: 20 - green, 50 - violet, 100 - olive-yellow with pink, 200 - pink, 500 -
beige-brown, 1000 - turquoise.

Pillow is imported only inside the drawing functions: Blender takes only the sizes (SIZE) from the
module, make_decals.py draws with the system Python. Randomness only through random.Random(seed): the
picture is the same from run to run.
"""
import math
import random

# banknote width and height, m
SIZE = {20: (0.130, 0.069), 50: (0.136, 0.072), 100: (0.142, 0.075), 200: (0.148, 0.075),
        500: (0.154, 0.075), 1000: (0.160, 0.075)}

# colours (sRGB) from the samples: paper on the left, field on the right, stripe with digits, cross stripes,
# portrait ink, large digits at the bottom (two inks and an outline), small digits at the top, denomination
# picture, mark for the blind; face - portrait traits
PAL = {
    20: dict(paper=(242, 249, 236), field=(204, 230, 178), band=(160, 204, 118), rail=(122, 156, 108),
             ink=(62, 52, 40), num=((92, 150, 80), (132, 94, 64)), num_line=(40, 46, 30), small=(96, 104, 186),
             accent=(176, 104, 160), accent2=(116, 172, 98), mark="triangle",
             face=dict(hair="full", mustache=True, beard=False, glasses=False, beads=False, stitch=True)),
    50: dict(paper=(238, 236, 248), field=(212, 190, 230), band=(166, 128, 206), rail=(94, 96, 166),
             ink=(98, 38, 46), num=((70, 62, 172), (178, 52, 96)), num_line=(58, 26, 56), small=(80, 176, 188),
             accent=(120, 202, 206), accent2=(110, 104, 122), mark="circle",
             face=dict(hair="bald", mustache=True, beard=True, glasses=True, beads=False, stitch=False)),
    100: dict(paper=(251, 248, 230), field=(234, 222, 160), band=(220, 204, 116), rail=(176, 136, 122),
              ink=(80, 72, 50), num=((168, 84, 62), (212, 146, 104)), num_line=(94, 62, 44), small=(224, 166, 46),
              accent=(232, 178, 168), accent2=(164, 94, 52), mark="square",
              face=dict(hair="full", mustache=True, beard=False, glasses=False, beads=False, stitch=False)),
    200: dict(paper=(253, 242, 247), field=(242, 196, 218), band=(236, 150, 194), rail=(214, 124, 146),
              ink=(70, 62, 106), num=((84, 98, 178), (232, 102, 132)), num_line=(74, 52, 88), small=(64, 186, 176),
              accent=(128, 208, 198), accent2=(150, 58, 128), mark="two",
              face=dict(hair="woman", mustache=False, beard=False, glasses=False, beads=True, stitch=True)),
    500: dict(paper=(253, 245, 232), field=(242, 216, 180), band=(232, 186, 120), rail=(154, 158, 172),
              ink=(68, 56, 54), num=((110, 126, 168), (140, 100, 76)), num_line=(50, 46, 62), small=(140, 118, 202),
              accent=(208, 184, 216), accent2=(48, 140, 76), mark="dots",
              face=dict(hair="short", mustache=False, beard=False, glasses=False, beads=False, stitch=False)),
    1000: dict(paper=(230, 239, 240), field=(176, 216, 228), band=(116, 186, 210), rail=(162, 134, 170),
               ink=(84, 36, 40), num=((122, 56, 106), (152, 96, 78)), num_line=(70, 28, 44), small=(64, 170, 198),
               accent=(238, 204, 112), accent2=(148, 136, 48), mark="three",
               face=dict(hair="swept", mustache=True, beard=True, glasses=True, beads=False, stitch=False)),
}


def mix(a, b, t):
    return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


class Canvas:
    """Banknote canvas W x H pixels (already supersampled by S): layers, masks, noise."""

    def __init__(self, W, H, S, rnd):
        from PIL import Image
        self.W, self.H, self.S, self.rnd = W, H, S, rnd
        self.Image = Image

    def X(self, f):
        return f * self.W

    def Y(self, f):
        return f * self.H

    def layer(self):
        return self.Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))

    def noise(self, cw, ch, blur=0.0):
        """Smooth noise 0..255 (effect_noise is unsuitable: it differs from run to run)."""
        from PIL import ImageFilter
        small = self.Image.frombytes("L", (cw, ch), bytes(self.rnd.randrange(256) for _ in range(cw * ch)))
        big = small.resize((self.W, self.H), self.Image.BICUBIC)
        return big.filter(ImageFilter.GaussianBlur(blur)) if blur else big

    def hgrad(self, stops):
        """Mask across the width: [(x fraction, 0..1)] -> L."""
        row = []
        for i in range(256):
            x = i / 255.0
            v = stops[0][1] if x < stops[0][0] else stops[-1][1]
            for (x0, v0), (x1, v1) in zip(stops, stops[1:]):
                if x0 <= x <= x1:
                    v = v0 + (v1 - v0) * (x - x0) / max(1e-6, x1 - x0)
                    break
            row.append(int(255 * min(1.0, max(0.0, v))))
        return self.Image.frombytes("L", (256, 1), bytes(row)).resize((self.W, self.H), self.Image.BILINEAR)

    def over(self, base, top, mask=None, k=1.0):
        """Layer top (RGBA) over base; mask (L) and k - strength."""
        from PIL import ImageChops
        if mask is not None or k < 1.0:
            a = top.getchannel("A")
            if mask is not None:
                a = ImageChops.multiply(a, mask)
            if k < 1.0:
                a = a.point(lambda v: int(v * k))
            top = top.copy()
            top.putalpha(a)
        return self.Image.alpha_composite(base, top)

    def paint(self, base, color, mask):
        """Fill with a colour through a mask (L)."""
        top = self.Image.new("RGBA", (self.W, self.H), tuple(color[:3]) + (255,))
        top.putalpha(mask)
        return self.Image.alpha_composite(base, top)


def font(px):
    from PIL import ImageFont
    for name in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, max(4, int(px)))
        except OSError:
            pass
    return ImageFont.load_default()


def note_image(denom, px_per_m, seed=0, wear=0.5, fold=None, S=4):
    """Front side of a note of denom hryvnias: RGBA exactly the size of the note (S x px_per_m pixels per
    metre), the top of the image is the top of the note. wear - wear 0..1 (dirt toward the edges, stains),
    fold - a fold across (fraction of the width) or None."""
    from PIL import Image, ImageChops, ImageDraw, ImageFilter

    w_m, h_m = SIZE[denom]
    W, H = int(round(w_m * px_per_m * S)), int(round(h_m * px_per_m * S))
    p = PAL[denom]
    c = Canvas(W, H, S, random.Random(seed * 7919 + denom))
    X, Y = c.X, c.Y
    lw = max(1, S // 2)
    txt = str(denom)

    # --- paper, even guilloche (waves with a phase shift) - faint on the left, stronger on the field
    img = Image.new("RGBA", (W, H), p["paper"] + (255,))
    gl = c.layer()
    d = ImageDraw.Draw(gl)
    for k in range(34):
        y0 = Y(k / 33.0)
        pts = [(x, y0 + Y(0.03) * math.sin(x / X(0.045) + k * 0.45)) for x in range(0, W + 8, 6)]
        d.line(pts, fill=mix(p["paper"], p["field"], 1.0) + (255,), width=lw)
    img = c.over(img, gl, c.hgrad([(0.0, 0.25), (0.30, 0.30), (0.50, 0.85), (1.0, 0.85)]))

    # --- field in the denomination colour on the right: soft from the portrait to the stripe
    fmask = c.hgrad([(0.0, 0.0), (0.34, 0.0), (0.50, 0.80), (0.80, 0.96), (1.0, 1.0)])
    fmask = ImageChops.multiply(fmask, c.noise(9, 5, Y(0.06)).point(lambda v: 170 + v * 85 // 255))
    img = c.paint(img, p["field"], fmask)
    img = scene(c, img, denom, p)
    # guilloche waves over the field
    gl = c.layer()
    d = ImageDraw.Draw(gl)
    for k in range(7):
        pts = [(x, Y(0.5) + Y(0.40) * math.sin(x / X(0.06) + k * 0.55) * math.cos(x / X(0.21)))
               for x in range(int(X(0.46)), int(X(0.83)), 5)]
        d.line(pts, fill=mix(p["field"], p["ink"], 0.30) + (80,), width=lw)
    img = c.over(img, gl)

    # --- security thread with windows
    th = c.layer()
    d = ImageDraw.Draw(th)
    tx0, tx1 = X(0.826), X(0.846)
    d.rectangle([tx0, 0, tx1, H], fill=mix(p["field"], p["band"], 0.7) + (220,))
    for k in range(9):
        y0 = Y(0.035 + k * 0.115)
        d.rectangle([tx0 + S * 0.5, y0, tx1 - S * 0.5, y0 + Y(0.062)],
                    fill=mix(p["band"], p["num_line"], 0.50) + (235,))
    img = c.over(img, th)

    # --- vertical denomination stripe: tiles with a pattern at the top
    # and bottom, strokes instead of the denomination in words
    bd = c.layer()
    d = ImageDraw.Draw(bd)
    bx0, bx1 = X(0.858), X(0.972)
    d.rectangle([bx0, 0, bx1, H], fill=p["band"] + (255,))
    for y0, y1 in ((0, Y(0.055)), (Y(0.945), H)):
        d.rectangle([bx0, y0, bx1, y1], fill=mix(p["band"], p["num_line"], 0.35) + (255,))
        for k in range(5):
            cx = bx0 + (bx1 - bx0) * (k + 0.5) / 5
            r = Y(0.012)
            d.ellipse([cx - r, (y0 + y1) / 2 - r, cx + r, (y0 + y1) / 2 + r], fill=mix(p["band"], (255, 255, 255), 0.5))
    for k in range(5):
        x = bx0 + (bx1 - bx0) * (0.22 + 0.14 * k)
        d.line([(x, Y(0.58)), (x, Y(0.93))], fill=mix(p["band"], p["num_line"], 0.20) + (255,), width=lw)
    img = c.over(img, bd)
    # large digits across the stripe (turned clockwise: read top to bottom), light with an outline
    fh = (bx1 - bx0) * 0.92
    f = font(fh)
    tw = ImageDraw.Draw(img).textlength(txt, font=f)
    big = Image.new("RGBA", (int(tw + fh), int(fh * 1.6)), (0, 0, 0, 0))
    ImageDraw.Draw(big).text((fh / 2, fh * 0.8), txt, font=f, anchor="lm",
                             fill=mix(p["band"], (255, 255, 255), 0.82) + (255,), stroke_width=max(1, int(fh * 0.04)),
                             stroke_fill=mix(p["band"], p["num_line"], 0.62) + (255,))
    big = big.rotate(-90, expand=True)
    big = big.crop(big.getbbox())
    room = Y(0.355)
    if big.size[1] > room:
        big = big.resize((max(1, int(big.size[0] * room / big.size[1])), int(room)), Image.LANCZOS)
    img.alpha_composite(big, (int((bx0 + bx1) / 2 - big.size[0] / 2), int(Y(0.075))))

    # --- cross stripes near the edges: on the right with hatching, on the left with a flower ornament
    rl = c.layer()
    d = ImageDraw.Draw(rl)
    d.rectangle([X(0.866), Y(0.445), W, Y(0.545)], fill=p["rail"] + (240,))
    for k in range(-6, 40):
        x = X(0.866) + k * Y(0.022)
        d.line([(x, Y(0.545)), (x + Y(0.10), Y(0.445))], fill=mix(p["rail"], (255, 255, 255), 0.35) + (210,), width=lw)
    d.rectangle([0, Y(0.43), X(0.066), Y(0.57)], fill=p["rail"] + (235,))
    for k in range(30):
        y = Y(0.43) + k * Y(0.0048)
        d.line([(0, y), (X(0.066), y)], fill=mix(p["rail"], (255, 255, 255), 0.18) + (150,), width=max(1, S // 4))
    cx, cy, r = X(0.034), Y(0.50), Y(0.052)
    white = mix(p["paper"], (255, 255, 255), 0.6) + (255,)
    for k in range(8):
        a = math.pi * k / 4
        px, py = cx + r * 0.62 * math.cos(a), cy + r * 0.62 * math.sin(a)
        d.ellipse([px - r * 0.28, py - r * 0.28, px + r * 0.28, py + r * 0.28], outline=white, width=max(1, S // 2))
    d.ellipse([cx - r * 0.30, cy - r * 0.30, cx + r * 0.30, cy + r * 0.30], fill=white)
    img = c.over(img, rl)

    # --- engraved portrait
    img = portrait(c, img, p)

    # --- large denomination digits bottom left: two inks, outline, hatching inside
    fh = Y(0.215)
    f = font(fh)
    x0, yb = X(0.072), Y(0.955)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).text((x0, yb), txt, font=f, anchor="ls", fill=255)
    box = m.getbbox() or (0, 0, W, H)
    bw = (box[2] - box[0]) / W
    g = c.hgrad([(box[0] / W + 0.20 * bw, 0.0), (box[0] / W + 0.85 * bw, 1.0)])
    ink_a, ink_b = (Image.new("RGBA", (W, H), p["num"][k] + (255,)) for k in (0, 1))
    col = Image.composite(ink_b, ink_a, g)
    hatch = c.layer()
    hd = ImageDraw.Draw(hatch)
    for k in range(-80, 260):
        x = box[0] + k * S * 2.2
        hd.line([(x, box[3]), (x + (box[3] - box[1]) * 0.6, box[1])], fill=(255, 255, 255, 40), width=max(1, S // 2))
    col = Image.alpha_composite(col, hatch)
    col.putalpha(m)
    ol = Image.new("L", (W, H), 0)
    ImageDraw.Draw(ol).text((x0, yb), txt, font=f, anchor="ls", fill=255, stroke_width=max(1, int(fh * 0.022)),
                            stroke_fill=255)
    img = c.paint(img, p["num_line"], ImageChops.subtract(ol, m))
    img = Image.alpha_composite(img, col)

    # --- small digits top left, trident, mark for the blind, embossed strokes
    sm = c.layer()
    d = ImageDraw.Draw(sm)
    d.text((X(0.032), Y(0.165)), txt, font=font(Y(0.085)), anchor="ls", fill=p["small"] + (240,))
    tryzub(d, X(0.572), Y(0.040), Y(0.105), mix(p["ink"], p["field"], 0.15) + (240,), S)
    mark_col = mix(p["rail"], p["ink"], 0.45) + (235,)
    mx, my, mr = X(0.050), Y(0.665), Y(0.032)
    mk = p["mark"]
    if mk == "circle":
        d.ellipse([mx - mr, my - mr, mx + mr, my + mr], outline=mark_col, width=max(2, S))
    elif mk == "triangle":
        d.polygon([(mx, my - mr), (mx + mr * 1.05, my + mr * 0.8), (mx - mr * 1.05, my + mr * 0.8)], outline=mark_col,
                  width=max(2, S))
    elif mk == "square":
        d.rectangle([mx - mr, my - mr, mx + mr, my + mr], outline=mark_col, width=max(2, S))
    elif mk in ("two", "three"):
        n = 2 if mk == "two" else 3
        for k in range(n):
            x = mx + (k - (n - 1) / 2) * mr * 0.7
            d.line([(x, my - mr), (x, my + mr)], fill=mark_col, width=max(2, S))
    elif mk == "dots":
        for k in range(3):
            y = my + (k - 1) * mr * 0.9
            d.ellipse([mx - mr * 0.3, y - mr * 0.3, mx + mr * 0.3, y + mr * 0.3], fill=mark_col)
    for k in range(4):
        y = Y(0.80 + k * 0.035)
        d.line([(0, y), (X(0.045), y)], fill=mark_col, width=max(1, S // 2))
        d.ellipse([X(0.045) - S, y - S, X(0.045) + S, y + S], outline=mark_col, width=max(1, S // 3))
    img = c.over(img, sm)

    # --- worn note: paper of uneven tone, dirt toward the edges, stains, fold
    edge = Image.new("L", (W, H), 0)
    ed = ImageDraw.Draw(edge)
    for k in range(12):
        inset = Y(0.006) * k
        ed.rectangle([inset, inset, W - inset, H - inset], fill=int(255 * (k + 1) / 12))
    edge = edge.filter(ImageFilter.GaussianBlur(Y(0.02)))
    grime = ImageChops.multiply(ImageChops.invert(edge), c.noise(14, 7, Y(0.02)))
    stain = c.noise(7, 4, Y(0.05)).point(lambda v: max(0, v - 160) * 2)
    dirt = ImageChops.add(grime.point(lambda v: int(v * wear * 0.7)), stain.point(lambda v: int(v * wear * 0.45)))
    img = c.paint(img, (104, 92, 70), dirt.point(lambda v: min(120, v)))
    tone = c.noise(40, 20, S * 1.5).point(lambda v: int(abs(v - 128) * 0.12 * (0.5 + wear)))
    img = c.paint(img, (70, 60, 46), tone)
    if fold is not None:
        fd = c.layer()
        d = ImageDraw.Draw(fd)
        x = X(fold)
        d.line([(x - S, 0), (x - S + Y(0.02), H)], fill=(255, 255, 255, 80), width=S)
        d.line([(x + S, 0), (x + S + Y(0.02), H)], fill=(40, 34, 26, 70), width=S)
        img = c.over(img, fd.filter(ImageFilter.GaussianBlur(S * 0.6)))
    return img


def tryzub(d, cx, top, h, col, S):
    """Trident of height h: the middle prong with a point, side prongs with points inward, inner offshoots,
    a base arc with a spike at the bottom (drawn with lines along the centre lines, width ~ h / 13)."""
    k = h / 140.0
    w = max(2, int(10 * k))

    def P(x, y):
        return (cx + x * k, top + y * k)

    for s in (-1, 1):
        # side prong: up along the edge, at the bottom an arc toward the middle
        d.line([P(s * 42, 16), P(s * 42, 92), P(s * 36, 108), P(s * 22, 120), P(0, 126)], fill=col, width=w,
               joint="curve")
        d.polygon([P(s * 48, 20), P(s * 42, 0), P(s * 30, 24)], fill=col)                  # point inward
        # inner offshoot from the base of the middle prong
        d.line([P(0, 112), P(s * 14, 100), P(s * 20, 78), P(s * 20, 62)], fill=col, width=max(2, int(w * 0.8)),
               joint="curve")
    d.line([P(0, 22), P(0, 126)], fill=col, width=w)
    d.polygon([P(0, 0), P(8, 18), P(0, 34), P(-8, 18)], fill=col)                             # middle point
    d.polygon([P(-7, 124), P(0, 140), P(7, 124)], fill=col)                                   # spike of the base
    d.line([P(-9, 102), P(9, 102)], fill=col, width=max(2, int(w * 0.8)))                    # crossbar


def scene(c, img, denom, p):
    """Denomination picture on the coloured field (after the samples, simplified, no inscriptions)."""
    from PIL import ImageDraw, ImageFilter

    X, Y, S, rnd = c.X, c.Y, c.S, c.rnd
    lw = max(1, S // 2)
    a1, a2 = p["accent"], p["accent2"]
    soft = c.layer()                                       # blurred background of the picture
    d = ImageDraw.Draw(soft)
    sharp = c.layer()                                      # sharp details on top
    e = ImageDraw.Draw(sharp)
    if denom == 100:
        # pink wash and an artist's palette with brushes
        d.ellipse([X(0.48), Y(0.16), X(0.84), Y(0.88)], fill=a1 + (210,))
        cx, cy = X(0.655), Y(0.60)
        e.ellipse([cx - Y(0.12), cy - Y(0.09), cx + Y(0.12), cy + Y(0.11)], fill=a2 + (240,))
        e.ellipse([cx + Y(0.05), cy - Y(0.13), cx + Y(0.17), cy - Y(0.01)], fill=(0, 0, 0, 0))   # notch
        e.ellipse([cx - Y(0.07), cy + Y(0.00), cx - Y(0.025), cy + Y(0.045)], fill=a1 + (255,))  # hole
        for k in range(3):                                     # brushes in a fan
            x = cx - Y(0.035) + k * Y(0.035)
            e.line([(x, cy + Y(0.05)), (x + (k - 1) * Y(0.03), Y(0.30))], fill=mix(a2, (40, 30, 20), 0.3) + (255,),
                   width=max(2, int(S * 1.2)))
    elif denom == 200:
        # turquoise wave from top to bottom, orange flowers, a lilac lotus on a leaf
        pts = [(X(0.60) + X(0.035) * math.sin(y / Y(0.07)), y) for y in range(0, c.H + 6, 6)]
        d.line(pts, fill=a1 + (210,), width=int(Y(0.06)))
        d.ellipse([X(0.62), Y(0.10), X(0.82), Y(0.48)], fill=(240, 200, 150, 150))
        for k in range(7):                                     # flowers with five petals
            cx, cy = X(0.70 + rnd.uniform(-0.05, 0.08)), Y(0.29 + rnd.uniform(-0.13, 0.12))
            r = Y(0.022)
            for j in range(5):
                a = 2 * math.pi * j / 5 + k
                px, py = cx + r * math.cos(a), cy + r * math.sin(a)
                e.ellipse([px - r * 0.8, py - r * 0.8, px + r * 0.8, py + r * 0.8], fill=(236, 168, 80, 190))
            e.ellipse([cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5], fill=(200, 120, 50, 220))
        cx, cy = X(0.64), Y(0.62)
        e.ellipse([cx - Y(0.15), cy + Y(0.03), cx + Y(0.15), cy + Y(0.11)], fill=mix(a2, (60, 40, 70), 0.3) + (220,))
        for ang in (-150, -122, -90, -58, -30):
            a = math.radians(ang)
            tip = (cx + Y(0.16) * math.cos(a), cy + Y(0.16) * math.sin(a))
            n = (-math.sin(a) * Y(0.035), math.cos(a) * Y(0.035))
            mid = (cx + Y(0.08) * math.cos(a), cy + Y(0.08) * math.sin(a))
            e.polygon([(cx, cy + Y(0.04)), (mid[0] + n[0], mid[1] + n[1]), tip, (mid[0] - n[0], mid[1] - n[1])],
                      fill=a2 + (235,))
    elif denom == 500:
        # light-green wave, a lilac scene with a quill (fountain), a green open book
        d.ellipse([X(0.52), Y(0.06), X(0.86), Y(0.46)], fill=(214, 228, 150, 160))
        d.ellipse([X(0.54), Y(0.46), X(0.81), Y(0.84)], fill=a1 + (190,))
        for k in range(15):
            x = X(0.565) + k * X(0.015)
            e.line([(x, Y(0.52 + 0.05 * math.sin(k))), (x + X(0.004), Y(0.80))], fill=(120, 100, 172, 120), width=lw)
        cx, cy = X(0.665), Y(0.27)
        for s in (-1, 1):
            e.polygon([(cx, cy + Y(0.09)), (cx + s * X(0.065), cy + Y(0.05)), (cx + s * X(0.072), cy - Y(0.11)),
                       (cx + s * X(0.004), cy - Y(0.06))], fill=a2 + (245,))
        e.line([(cx - X(0.075), cy + Y(0.13)), (cx + X(0.075), cy + Y(0.13))], fill=a2 + (245,), width=max(2, S))
    elif denom == 50:
        # turquoise scene with a rider and a grey fluttering flag
        d.ellipse([X(0.54), Y(0.34), X(0.83), Y(0.88)], fill=a1 + (210,))
        for k in range(16):
            x = X(0.57) + k * X(0.015)
            e.line([(x, Y(0.42)), (x - X(0.01), Y(0.82))], fill=(60, 150, 160, 90), width=lw)
        cx, cy = X(0.675), Y(0.64)
        e.ellipse([cx - Y(0.10), cy - Y(0.035), cx + Y(0.09), cy + Y(0.065)], fill=(52, 124, 136, 200))  # horse
        for s in (-1, 1):
            e.line([(cx + s * Y(0.06), cy + Y(0.05)), (cx + s * Y(0.075), cy + Y(0.16))], fill=(52, 124, 136, 200),
                   width=max(2, S))
        e.line([(cx + Y(0.08), cy), (cx + Y(0.13), cy - Y(0.09))], fill=(52, 124, 136, 200), width=max(3, S * 2))
        e.ellipse([cx - Y(0.03), cy - Y(0.15), cx + Y(0.025), cy - Y(0.02)], fill=(52, 124, 136, 200))     # rider
        fx, fy = X(0.60), Y(0.17)
        pts = [(fx + X(0.11) * t, fy + Y(0.025) * math.sin(t * 6.0)) for t in [i / 10 for i in range(11)]]
        pts += [(fx + X(0.11) * t, fy + Y(0.10) + Y(0.025) * math.sin(t * 6.0))
                for t in [1 - i / 10 for i in range(11)]]
        e.polygon(pts, fill=a2 + (230,))
    elif denom == 20:
        # Carpathians: lilac mountains, green slopes with firs, a lilac rosette
        e.polygon([(X(0.50), Y(0.62)), (X(0.62), Y(0.33)), (X(0.70), Y(0.45)), (X(0.76), Y(0.36)), (X(0.84), Y(0.55)),
                   (X(0.84), Y(0.70)), (X(0.50), Y(0.70))], fill=(172, 174, 216, 200))
        e.polygon([(X(0.50), Y(0.90)), (X(0.56), Y(0.60)), (X(0.66), Y(0.52)), (X(0.78), Y(0.60)), (X(0.84), Y(0.56)),
                   (X(0.84), Y(0.92)), (X(0.50), Y(0.92))], fill=a2 + (230,))
        for k in range(26):
            x, y = X(0.53 + rnd.uniform(0.0, 0.29)), Y(0.62 + rnd.uniform(0.0, 0.26))
            e.polygon([(x, y - Y(0.05)), (x + Y(0.018), y), (x - Y(0.018), y)], fill=(70, 120, 66, 210))
        cx, cy, r = X(0.665), Y(0.22), Y(0.075)
        for k in range(8):
            a = math.pi * k / 4
            px, py = cx + r * 0.55 * math.cos(a), cy + r * 0.55 * math.sin(a)
            e.ellipse([px - r * 0.48, py - r * 0.48, px + r * 0.48, py + r * 0.48], outline=a1 + (235,),
                      width=max(2, S))
    else:   # 1000: yellow arcs and an olive sign
        for k in range(5):
            r = Y(0.25 + 0.07 * k)
            e.arc([X(0.68) - r, Y(0.55) - r, X(0.68) + r, Y(0.55) + r], 200, 340, fill=a1 + (140,), width=int(Y(0.018)))
        d.ellipse([X(0.52), Y(0.40), X(0.78), Y(0.95)], fill=(214, 168, 176, 120))
        cx, cy = X(0.66), Y(0.28)
        e.regular_polygon((cx, cy, Y(0.08)), 6, fill=a2 + (240,))
        e.ellipse([cx - Y(0.035), cy - Y(0.035), cx + Y(0.035), cy + Y(0.035)], fill=(60, 60, 30, 240))
    img = c.over(img, soft.filter(ImageFilter.GaussianBlur(Y(0.03))))
    return c.over(img, sharp)


def portrait(c, img, p):
    """Engraved portrait: a tone map (hair, face with light from the left, eyes, eyebrows, nose, mouth, neck,
    frock coat and a light shirt), diagonal hatching on top; the traits of the denomination are p["face"].
    Sizes are fractions of the note height, the middle of the face is at 0.42 of the width."""
    from PIL import Image, ImageChops, ImageDraw, ImageFilter

    fc = p["face"]
    W, H, S = c.W, c.H, c.S
    cx = W * 0.42
    U = H

    def P(dx, dy):
        return (cx + dx * U, dy * U)

    tone = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(tone)

    def ell(x0, y0, x1, y1, v):
        a, b = P(x0, y0), P(x1, y1)
        d.ellipse([a[0], a[1], b[0], b[1]], fill=v)

    def poly(pts, v):
        d.polygon([P(*q) for q in pts], fill=v)

    # clothes: shoulders to the bottom of the note, dark frock coat, light shirt
    poly([(-0.50, 1.02), (-0.40, 0.88), (-0.16, 0.80), (0.17, 0.80), (0.42, 0.87), (0.53, 1.02)], 230)
    poly([(-0.12, 0.80), (0.0, 1.02), (0.13, 0.80)], 45)
    # hair (under the face): cap and sides
    hair = fc["hair"]
    if hair == "woman":
        ell(-0.27, 0.04, 0.27, 0.64, 205)
        poly([(-0.27, 0.40), (0.27, 0.40), (0.24, 0.72), (-0.24, 0.72)], 205)
    elif hair == "bald":
        ell(-0.25, 0.10, 0.25, 0.58, 120)
        ell(-0.27, 0.26, -0.15, 0.52, 190)
        ell(0.15, 0.26, 0.27, 0.52, 190)
    elif hair == "short":
        ell(-0.24, 0.07, 0.25, 0.56, 215)
    elif hair == "swept":
        ell(-0.25, 0.04, 0.27, 0.56, 200)
        ell(-0.05, 0.02, 0.30, 0.30, 215)
    else:
        ell(-0.27, 0.04, 0.27, 0.60, 225)
    # neck (shadow under the chin)
    poly([(-0.10, 0.62), (0.11, 0.62), (0.12, 0.84), (-0.11, 0.84)], 100)
    poly([(-0.10, 0.70), (0.11, 0.70), (0.11, 0.76), (-0.10, 0.76)], 150)
    # face: oval, light from the left - shadow on the right, smooth
    top = {"woman": 0.19, "bald": 0.13, "short": 0.21, "swept": 0.20, "full": 0.21}[hair]
    fm = Image.new("L", (W, H), 0)
    a, b = P(-0.20, top), P(0.21, 0.74)
    ImageDraw.Draw(fm).ellipse([a[0], a[1], b[0], b[1]], fill=255)
    lit = c.hgrad([((cx - 0.20 * U) / W, 0.17), ((cx + 0.0 * U) / W, 0.24), ((cx + 0.21 * U) / W, 0.52)])
    ld = ImageDraw.Draw(lit)
    for (x0, y0, x1, y1), v in (((0.07, 0.47, 0.24, 0.76), 140), ((-0.14, 0.67, 0.16, 0.78), 115)):
        a, b = P(x0, y0), P(x1, y1)                         # cheekbone and jaw on the right, bottom of the chin
        ld.ellipse([a[0], a[1], b[0], b[1]], fill=v)
    tone.paste(lit, (0, 0), fm)
    if hair == "woman":                                    # parting in the middle
        poly([(-0.005, 0.05), (0.008, 0.05), (0.004, top + 0.01), (-0.002, top + 0.01)], 60)
    # ears
    ell(-0.235, 0.38, -0.18, 0.53, 110)
    ell(0.19, 0.38, 0.24, 0.53, 160)
    if hair == "woman":
        ell(-0.27, 0.36, -0.17, 0.56, 205)
        ell(0.17, 0.36, 0.27, 0.56, 205)
    # eyes: socket, eyelid, pupil; eyebrows
    for s in (-1, 1):
        x = s * 0.085 + 0.01
        ell(x - 0.050, 0.392, x + 0.050, 0.452, 92 if s < 0 else 135)
        poly([(x - 0.040, 0.420), (x - 0.010, 0.405), (x + 0.030, 0.408), (x + 0.042, 0.420), (x + 0.010, 0.415),
              (x - 0.020, 0.418)], 225)
        ell(x - 0.013, 0.408, x + 0.013, 0.434, 245)
        poly([(x - 0.055, 0.373), (x + 0.045, 0.360), (x + 0.052, 0.374), (x - 0.050, 0.387)], 195)
    # nose: shadow on the right, nostrils; mouth: line of the lips, shadow under the lower lip
    poly([(0.022, 0.42), (0.058, 0.55), (0.03, 0.572), (0.012, 0.55)], 135)
    ell(-0.032, 0.556, -0.008, 0.574, 200)
    ell(0.028, 0.556, 0.052, 0.574, 210)
    poly([(-0.058, 0.636), (0.0, 0.628), (0.068, 0.632), (0.062, 0.644), (0.0, 0.640), (-0.054, 0.646)], 205)
    ell(-0.035, 0.655, 0.045, 0.675, 120)
    if fc["mustache"]:
        poly([(-0.10, 0.645), (-0.05, 0.592), (0.01, 0.605), (0.07, 0.592), (0.12, 0.645), (0.07, 0.625),
              (0.01, 0.618), (-0.05, 0.625)], 238)
    if fc["beard"]:
        poly([(-0.20, 0.52), (-0.12, 0.66), (0.0, 0.69), (0.13, 0.66), (0.21, 0.52), (0.22, 0.72), (0.14, 0.95),
              (0.0, 1.02), (-0.13, 0.95), (-0.21, 0.72)], 222)
    if fc["glasses"]:
        for s in (-1, 1):
            x = s * 0.088 + 0.01
            a, b = P(x - 0.062, 0.385), P(x + 0.062, 0.46)
            d.ellipse([a[0], a[1], b[0], b[1]], outline=250, width=max(2, int(S * 1.4)))
        d.line([P(-0.016, 0.415), P(0.036, 0.415)], fill=250, width=max(2, S))
    if fc["beads"]:
        for row, (y0, n) in enumerate(((0.80, 11), (0.86, 13), (0.92, 15))):
            for k in range(n):
                t = (k / (n - 1)) * 2 - 1
                x = t * (0.15 + row * 0.04)
                y = y0 + 0.05 * (1 - t * t)
                ell(x - 0.018, y - 0.018, x + 0.018, y + 0.018, 250 if k % 2 else 150)
    if fc["stitch"]:                                       # embroidery along the collar
        for k in range(6):
            for s in (-1, 1):
                x, y = s * (0.035 + 0.015 * k), 0.83 + k * 0.03
                ell(x - 0.012, y - 0.012, x + 0.012, y + 0.012, 215)
    tone = tone.filter(ImageFilter.GaussianBlur(H * 0.005))

    # diagonal hatching: lines merge in the dark and show in the light (engraving)
    hatch = Image.new("L", (W, H), 0)
    hd = ImageDraw.Draw(hatch)
    step = max(4, int(S * 2.6))
    for k in range(-H // step - 4, (W + H) // step + 4):
        x = k * step
        hd.line([(x, H), (x + H * 0.45, 0)], fill=255, width=max(1, S // 2))
    hatch = hatch.filter(ImageFilter.GaussianBlur(S * 0.5))
    alpha = ImageChops.multiply(tone, hatch.point(lambda v: 165 + v * 90 // 255))
    # hair and shoulders dissolve to the left (as on the samples)
    fade = c.hgrad([(0.0, 0.0), ((cx - 0.40 * U) / W, 0.0), ((cx - 0.22 * U) / W, 1.0), (1.0, 1.0)])
    alpha = ImageChops.multiply(alpha, fade)
    return c.paint(img, p["ink"], alpha)
