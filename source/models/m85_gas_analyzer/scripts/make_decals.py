"""Decals of the M85 gas analyzer module (UG-2; system Python + Pillow). No letters: on the real
device the plate is punched with "UG-2", a number and a year - here there is only a number made of
digits, and the second plate is blank.

- a numbered plate (black anodized, the digits punched down to the metal) and a blank plate, both
  on two rivets;
- the label on the rod head - a white square with the volume "100" (as in the photo);
- the scale card in the lid: three reading scales by the length of the stained column (ticks and
  mg/m3 digits without captions), at the left of each "before / after" powder colour samples, a frame;
- the label on the front end of the tube box: a frame, a large digit with the number of tubes, a
  batch number in digits, a round inspection stamp without text (rings and a star).

    python make_decals.py      -> ../work/decal_*.png

Positions and sizes come from m85_layout.py (build_m85.py reads the same file).
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m85_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
INK = (28, 28, 30, 255)
PAPER = (226, 220, 198, 255)
ANOD = (30, 30, 33, 255)                # black anodizing of the plates
SILVER = (196, 198, 200, 255)


def font(px):
    for name in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, max(1, px))
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
    """Canvas in metres: (u, v) -> pixels, v up; ppmm - pixels per millimetre of the finished picture."""

    def __init__(self, w, h, ppmm, bg=(0, 0, 0, 0)):
        self.w, self.h, self.k = w, h, ppmm * 1000.0 * S
        self.size = (int(round(w * ppmm * 1000.0)), int(round(h * ppmm * 1000.0)))
        self.img = Image.new("RGBA", (self.size[0] * S, self.size[1] * S), bg)
        self.d = ImageDraw.Draw(self.img)

    def p(self, u, v):
        return (u * self.k, (self.h - v) * self.k)

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

    def text(self, u, v, s, h, fill=INK, anchor="mm"):
        self.d.text(self.p(u, v), s, fill=fill, font=font(int(self.m(h))), anchor=anchor)

    def wear(self, seed, amount, blotch=0.0006, keep_alpha=True):
        """Print wear: random patches where the print is rubbed down to the background (alpha lower)."""
        rng = random.Random(seed)
        mask = Image.new("L", self.img.size, 255)
        md = ImageDraw.Draw(mask)
        n = int(amount * self.w * self.h * 1e6 * 0.25)   # per mm2 of area
        for _ in range(n):
            x, y = rng.uniform(0, self.img.size[0]), rng.uniform(0, self.img.size[1])
            r = self.m(blotch) * rng.uniform(0.3, 1.0)
            md.ellipse([x - r, y - r, x + r, y + r], fill=rng.randint(120, 200))
        mask = mask.filter(ImageFilter.GaussianBlur(self.m(blotch) * 0.6))
        a = self.img.getchannel("A")
        self.img.putalpha(Image.composite(a, Image.new("L", a.size, 0), mask) if keep_alpha else mask)

    def save(self, name):
        save(self.img, self.size, name)


def plate(name, w, h, digits, seed):
    """Plate: black anodizing, a light edge, two rivets, digits punched down to the metal."""
    sh = Sheet(w, h, 24, ANOD)
    sh.rect(0.0004, 0.0004, w - 0.0004, h - 0.0004, outline=(120, 122, 124, 255), w=0.00035)
    for u in (0.0022, w - 0.0022):
        sh.circle(u, h / 2, 0.0011, fill=(150, 152, 154, 255))
        sh.circle(u - 0.0002, h / 2 + 0.0002, 0.0005, fill=(205, 206, 208, 255))
    if digits:
        sh.text(w / 2, h / 2 - 0.0002, digits, 0.0050, fill=SILVER)
    else:                                   # blank: an embossed frame for the inscription
        sh.rect(0.0048, 0.0022, w - 0.0048, h - 0.0022, outline=(70, 72, 75, 255), w=0.0003)
    # patches rubbed down to the metal near the edges
    rng = random.Random(seed)
    for _ in range(14):
        u = rng.choice((rng.uniform(0, 0.0015), rng.uniform(w - 0.0015, w), rng.uniform(0, w)))
        v = rng.uniform(0, h) if u < 0.0015 or u > w - 0.0015 else rng.choice((rng.uniform(0, 0.001),
                                                                               rng.uniform(h - 0.001, h)))
        sh.circle(u, v, rng.uniform(0.0002, 0.0005), fill=(110, 112, 114, 255))
    sh.save(name)


def head_label():
    """White label on the rod head: the volume "100" (photo), slightly rubbed by fingers."""
    w = L.LABEL_W
    sh = Sheet(w, w, 40)
    sh.rect(0, 0, w, w, fill=(232, 230, 222, 255))
    sh.rect(0.0006, 0.0006, w - 0.0006, w - 0.0006, outline=INK, w=0.0003)
    sh.text(w / 2, w / 2 - 0.0002, "100", 0.0058)
    sh.wear(7, 0.9, blotch=0.0005)
    # the label has both background and print: a rubbed place shows the head chrome
    sh.save("decal_head.png")


def card():
    """Scale card in the lid: three scales of the stained column length, the digits are mg/m3."""
    w, h = L.CARD_WH
    sh = Sheet(w, h, 12)
    sh.rect(0, 0, w, h, fill=PAPER)
    sh.rect(0.0015, 0.0015, w - 0.0015, h - 0.0015, outline=INK, w=0.0004)
    scales = [
        ((214, 190, 70), (70, 104, 176), ["0", "20", "40", "60", "80", "100"]),
        ((232, 230, 220), (120, 82, 48), ["0", "5", "10", "15", "20", "30"]),
        ((176, 196, 214), (232, 226, 196), ["0", "50", "100", "150", "200", "250"]),
    ]
    rows = [h - 0.015, h - 0.036, h - 0.057]
    u0, u1 = 0.020, w - 0.006
    for (c0, c1, labels), v in zip(scales, rows):
        # powder colour samples: before and after
        sh.rect(0.005, v - 0.0035, 0.0105, v + 0.0035, fill=c0 + (255,), outline=INK, w=0.00025)
        sh.rect(0.0115, v - 0.0035, 0.0170, v + 0.0035, fill=c1 + (255,), outline=INK, w=0.00025)
        # ruler: a long line, ticks every 1/10 and digits under the large ones
        sh.line([(u0, v), (u1, v)], 0.0004)
        n = (len(labels) - 1) * 4
        for i in range(n + 1):
            u = u0 + (u1 - u0) * i / n
            big = i % 4 == 0
            sh.line([(u, v), (u, v + (0.0040 if big else 0.0020))], 0.0003 if big else 0.0002)
            if big:
                sh.text(u, v - 0.0040, labels[i // 4], 0.0034)
        # bold zero line - the start of reading from the swab edge
        sh.line([(u0, v - 0.0012), (u0, v + 0.0050)], 0.0007)
    # table number and a blank frame at the bottom right
    sh.text(0.010, 0.0060, "3", 0.0060)
    sh.rect(w - 0.032, 0.0035, w - 0.006, 0.0090, outline=INK, w=0.0003)
    # yellowed and rubbed along the edges
    rng = random.Random(3)
    ov = Image.new("RGBA", sh.img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for _ in range(60):
        x, y = rng.uniform(0, sh.img.size[0]), rng.uniform(0, sh.img.size[1])
        r = sh.m(rng.uniform(0.002, 0.008))
        od.ellipse([x - r, y - r, x + r, y + r], fill=(150, 120, 60, rng.randint(6, 18)))
    ov = ov.filter(ImageFilter.GaussianBlur(sh.m(0.003)))
    sh.img = Image.alpha_composite(sh.img, ov)
    sh.d = ImageDraw.Draw(sh.img)
    sh.save("decal_card.png")


def box_label():
    """Label on the box end: a frame, a large "8" (tubes in the box), a batch number, an inspection stamp."""
    w, h = L.BOX_LABEL
    sh = Sheet(w, h, 16)
    sh.rect(0, 0, w, h, fill=(214, 206, 176, 255))
    sh.rect(0.0008, 0.0008, w - 0.0008, h - 0.0008, outline=INK, w=0.0004)
    sh.line([(0.014, 0.0008), (0.014, h - 0.0008)], 0.0004)
    sh.text(0.0074, h / 2, "8", 0.010)
    # batch number and table lines
    sh.text(0.016, h - 0.0045, "0347-12", 0.0036, anchor="lm")
    for i, v in enumerate((h - 0.0080, h - 0.0105, h - 0.0130)):
        sh.line([(0.016, v), (0.016 + (0.016, 0.012, 0.017)[i], v)], 0.0005)
    # round stamp without text: two rings, a star, violet ink, slightly skewed and pale
    cu, cv, r = w - 0.0085, h / 2 - 0.0005, 0.0062
    st = Sheet(w, h, 16)
    ink = (92, 64, 150, 200)
    st.circle(cu, cv, r, outline=ink, w=0.0005)
    st.circle(cu, cv, r * 0.66, outline=ink, w=0.0003)
    pts = []
    for k in range(10):
        a = math.pi / 2 + k * math.pi / 5
        rr = r * (0.42 if k % 2 == 0 else 0.18)
        pts.append(st.p(cu + rr * math.cos(a), cv + rr * math.sin(a)))
    st.d.polygon(pts, fill=ink)
    st.wear(11, 1.6, blotch=0.0007)
    sh.img = Image.alpha_composite(sh.img, st.img)
    sh.d = ImageDraw.Draw(sh.img)
    sh.save("decal_box_label.png")


def main():
    (x0, x1), (y0, y1) = L.PLATE1
    plate("decal_plate1.png", x1 - x0, y1 - y0, "04217", 1)
    (x0, x1), (y0, y1) = L.PLATE2
    plate("decal_plate2.png", x1 - x0, y1 - y0, "", 2)
    head_label()
    card()
    box_label()


main()
