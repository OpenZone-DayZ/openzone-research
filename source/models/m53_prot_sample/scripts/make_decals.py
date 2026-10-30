"""Decals of the protection sample M53 (system Python + Pillow), no letters:
- decal_kev.png / decal_kev_h.png - the top of the aramid piece (the KV_BOX square in world axes): four
  claw furrows (inside - fresh, unfaded fabric of the lower layers, a gap, torn threads across, frayed
  edges), two holes (a dark funnel, turned-out fibres, soot all round), the stitching along the original
  left edge, a couple of brown stains. _h is the relief in alpha (0.5 is flat);
- decal_plate.png / decal_plate_h.png - the face of the titanium plate: at the dents the paint is
  knocked down to the metal, lead splashes as rays, tombac traces, soot, the paint has flaked off in a
  ring round the edge of a dent; three claw scratches down to the metal; a stamped number in digits;
- decal_tag.png - a manila tag with a grey stripe (the Protection line): empty fields, a hand-written
  number in digits, an eyelet; in world axes of the TAG_BOX square around the tag centre.

    python make_decals.py      -> ../work/decal_*.png

Sizes come from m53_layout.py (shared with build_m53.py).
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m53_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 3                       # supersampling factor for drawing (the result is downscaled)

TORN = (150, 106, 38)       # torn lower layers in the shadow of a furrow
TORN_DEEP = (108, 72, 24)
CREVICE = (52, 36, 16)
FUZZ = (238, 220, 158)
SOOT = (58, 50, 40)
TI = (104, 104, 102)
LEAD = (92, 93, 98)
TOMBAC = (132, 96, 70)


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def font(names, px):
    for name in names:
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


class Canvas:
    """A pair of images, colour + relief, in a world rectangle (cx, cy, w, h): px(x, y) -> pixel."""

    def __init__(self, cx, cy, w, h, px_w):
        self.cx, self.cy, self.w, self.h = cx, cy, w, h
        self.W = px_w * S
        self.H = int(round(px_w * h / w)) * S
        self.k = self.W / w
        self.col = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        self.hgt = Image.new("L", (self.W, self.H), 128)
        self.dh = ImageDraw.Draw(self.hgt)
        self.lay = None
        self.begin()

    def begin(self):
        """A new colour layer: within a layer the drawing replaces, between layers it is
        alpha-composited.
        """
        self.end()
        self.lay = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        self.dc = ImageDraw.Draw(self.lay)

    def end(self):
        if self.lay is not None:
            self.col = Image.alpha_composite(self.col, self.lay)
            self.lay = None

    def px(self, x, y):
        return ((x - self.cx) * self.k + self.W / 2, self.H / 2 - (y - self.cy) * self.k)

    def m(self, d):
        return d * self.k

    def line(self, pts, col, width, h=None):
        p = [self.px(*q) for q in pts]
        if col is not None:
            self.dc.line(p, fill=col, width=max(1, int(self.m(width))))
        if h is not None:
            self.dh.line(p, fill=h, width=max(1, int(self.m(width))))

    def disc(self, x, y, r, col, h=None):
        cx, cy = self.px(x, y)
        rr = self.m(r)
        if col is not None:
            self.dc.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col)
        if h is not None:
            self.dh.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=h)

    def poly(self, pts, col, h=None):
        p = [self.px(*q) for q in pts]
        if col is not None:
            self.dc.polygon(p, fill=col)
        if h is not None:
            self.dh.polygon(p, fill=h)

    def blot(self, x, y, r, col, rnd, n=7, h=None):
        """Uneven blot: several small circles round a centre."""
        for _ in range(n):
            a = rnd.uniform(0, 2 * math.pi)
            q = rnd.uniform(0, r * 0.6)
            self.disc(x + q * math.cos(a), y + q * math.sin(a), r * rnd.uniform(0.35, 0.7), col, h)

    def paste(self, color, mask):
        """Fill the colour through a mask over everything drawn."""
        self.end()
        self.col.paste(color, (0, 0), mask)
        self.begin()

    def save(self, name, px_w, blur=0.0):
        """Colour - name.png, relief - name_h.png (white RGB, the relief in alpha)."""
        self.end()
        col = self.col
        if blur:
            col = col.filter(ImageFilter.GaussianBlur(blur * S))
        size = (self.W // S, self.H // S)
        save(col, size, name + ".png")
        hg = self.hgt.filter(ImageFilter.GaussianBlur(0.6 * S))
        himg = Image.new("RGBA", (self.W, self.H), (255, 255, 255, 255))
        himg.putalpha(hg)
        save(himg, size, name + "_h.png")


def fibre_tufts(cv, x, y, ang, spread, n, l0, l1, rnd, col, width=0.00012, h=200, base=0.0):
    """A tuft of short fibres from a point: direction ang +- spread, length l0..l1."""
    for _ in range(n):
        a = ang + rnd.uniform(-spread, spread)
        ln = rnd.uniform(l0, l1)
        x0 = x + base * math.cos(a)
        y0 = y + base * math.sin(a)
        # the fibre is slightly curved
        mx = x0 + ln * 0.5 * math.cos(a) + rnd.uniform(-0.15, 0.15) * ln * math.sin(a)
        my = y0 + ln * 0.5 * math.sin(a) - rnd.uniform(-0.15, 0.15) * ln * math.cos(a)
        cv.line([(x0, y0), (mx, my), (x0 + ln * math.cos(a), y0 + ln * math.sin(a))],
                col + (rnd.randint(150, 235),), width, h)


def make_kevlar():
    cv = Canvas(L.KV_C[0], L.KV_C[1], L.KV_BOX, L.KV_BOX, 1024)
    rnd = random.Random(531)
    # soot and holes
    for hx, hy, r in L.HOLES:
        for i in range(14, 0, -1):                       # soot: a soft uneven blot
            f = i / 14
            cv.begin()
            cv.blot(hx, hy, r * (1.1 + 2.3 * f), SOOT + (int(22 * (1 - f) + 6),), rnd, n=5)
        cv.begin()
        cv.disc(hx, hy, r * 1.15, (96, 70, 34, 200))
        cv.begin()
        fibre_tufts(cv, hx, hy, 0.0, math.pi, 90, r * 0.7, r * 1.2, rnd, FUZZ, h=215, base=r * 0.55)
        cv.begin()
        cv.disc(hx, hy, r * 0.88, (88, 62, 26, 255), h=60)
        fibre_tufts(cv, hx, hy, 0.0, math.pi, 40, r * 0.3, r * 0.6, rnd, (196, 160, 90), h=150, base=r * 0.5)
        cv.begin()
        cv.disc(hx, hy, r * 0.50, CREVICE + (255,), h=20)
        cv.disc(hx, hy, r * 0.28, (24, 17, 9, 255), h=0)
        for _ in range(4):                               # long pulled-out threads
            a = rnd.uniform(0, 2 * math.pi)
            ln = rnd.uniform(r * 1.2, r * 2.2)
            cv.line([(hx + r * 0.4 * math.cos(a), hy + r * 0.4 * math.sin(a)),
                     (hx + ln * math.cos(a + 0.3), hy + ln * math.sin(a + 0.3))], FUZZ + (230,), 0.00016, 220)
    # claw furrows
    for k, ((ax, ay), (bx, by)) in enumerate(L.FURROWS):
        dx, dy = bx - ax, by - ay
        ln = math.hypot(dx, dy)
        ux, uy = dx / ln, dy / ln
        nx, ny = -uy, ux
        st = 40
        left, right, mid = [], [], []
        for i in range(st + 1):
            t = i / st
            depth, hw = L.furrow_profile(k, t)
            hw += 0.0008 if 0 < i < st else 0.0          # like the edge line in the geometry (build_m53)
            jl = rnd.uniform(-0.00025, 0.00025)
            jr = rnd.uniform(-0.00025, 0.00025)
            cx, cy = ax + dx * t, ay + dy * t
            left.append((cx + nx * (hw + jl), cy + ny * (hw + jl)))
            right.append((cx - nx * (hw + jr), cy - ny * (hw + jr)))
            mid.append((cx + nx * rnd.uniform(-0.0002, 0.0002), cy + ny * rnd.uniform(-0.0002, 0.0002)))
        # frayed edges: short light fibres outwards from the edge
        cv.begin()
        for side, edge in ((1, left), (-1, right)):
            for i, (ex, ey) in enumerate(edge):
                if 0 < i < st:
                    a = math.atan2(side * ny, side * nx)
                    fibre_tufts(cv, ex, ey, a, 0.9, 3, 0.0005, 0.0022, rnd, FUZZ, h=210)
        cv.begin()
        cv.poly(left + right[::-1], TORN + (255,), h=70)
        cv.begin()
        inl = [(m[0] * 0.45 + l[0] * 0.55, m[1] * 0.45 + l[1] * 0.55) for m, l in zip(mid, left)]
        inr = [(m[0] * 0.45 + r[0] * 0.55, m[1] * 0.45 + r[1] * 0.55) for m, r in zip(mid, right)]
        cv.poly(inl + inr[::-1], TORN_DEEP + (255,), h=50)
        cv.begin()
        # threads across the furrow (not all are torn)
        for i in range(3, st - 2, 3):
            if rnd.random() < 0.55:
                t = i / st
                _, hw = L.furrow_profile(k, t)
                hw += 0.0008
                cx, cy = ax + dx * t, ay + dy * t
                sk = rnd.uniform(-0.6, 0.6) * hw
                cv.line([(cx + nx * hw * 1.1 + ux * sk, cy + ny * hw * 1.1 + uy * sk),
                         (cx - nx * hw * 1.1 - ux * sk, cy - ny * hw * 1.1 - uy * sk)],
                        (214, 176, 96, 220), 0.00018, 150)
        cv.begin()
        cv.line(mid, CREVICE + (255,), 0.0009, 25)
        cv.begin()
        cv.line(mid[3:-3], (24, 16, 8, 255), 0.00045, 0)
    # stitching along the original left edge: 3 mm stitches, 4 mm pitch, khaki polyester thread
    cv.begin()
    lx = -L.KV_A + L.SEAM_IN
    ly = -L.KV_B + 0.004
    while ly + 0.003 < L.KV_B - 0.004:
        p0 = L.kv_world(lx + rnd.uniform(-0.0001, 0.0001), ly)
        p1 = L.kv_world(lx + rnd.uniform(-0.0001, 0.0001), ly + 0.003)
        cv.line([p0, p1], (96, 88, 58, 255), 0.0006, 168)
        cv.disc(*p0, 0.0003, (70, 52, 26, 200), h=90)
        ly += 0.004
    # brown stains (dried) near the ends of the furrows - a few
    for (px_, py_), r in (((0.026, -0.024), 0.0035), ((-0.012, -0.031), 0.0022), ((-0.033, 0.006), 0.0028)):
        for i in range(6, 0, -1):
            cv.begin()
            cv.blot(px_, py_, r * (0.5 + i * 0.12), (74, 40, 22, 22), rnd, n=4)
    cv.save("decal_kev", 1024)


def make_plate():
    cv = Canvas(0.0, 0.0, L.PL_X + 0.004, L.PL_Y + 0.004, 768)
    rnd = random.Random(532)
    for dx, dy, r, dep in L.DENTS:
        # soot and lead splashes as rays
        for i in range(10, 0, -1):
            cv.begin()
            cv.blot(dx, dy, r * (0.6 + 0.09 * i), (36, 34, 32, 20), rnd, n=4)
        cv.begin()
        for _ in range(30):
            a = rnd.uniform(0, 2 * math.pi)
            r0, r1 = r * rnd.uniform(0.35, 0.55), r * rnd.uniform(0.8, 1.7)
            w = rnd.uniform(0.0002, 0.0007)
            al = rnd.randint(70, 150)
            rm = (r0 + r1) / 2
            cv.line([(dx + r0 * math.cos(a), dy + r0 * math.sin(a)), (dx + rm * math.cos(a), dy + rm * math.sin(a))],
                    LEAD + (al,), w, 140)
            cv.line([(dx + rm * math.cos(a), dy + rm * math.sin(a)), (dx + r1 * math.cos(a), dy + r1 * math.sin(a))],
                    LEAD + (al // 2,), w * 0.5, 134)
        # the paint has flaked off in a ring round the edge of the dent (the metal was drawn)
        cv.begin()
        for _ in range(22):
            a = rnd.uniform(0, 2 * math.pi)
            q = r * rnd.uniform(0.7, 1.05)
            cv.disc(dx + q * math.cos(a), dy + q * math.sin(a), rnd.uniform(0.0002, 0.0006), (124, 124, 121, 200), h=110)
        # middle: paint knocked down to the metal, lead smeared, tombac traces
        cv.begin()
        cv.blot(dx, dy, r * 0.62, TI + (255,), rnd, n=9, h=118)
        cv.begin()
        cv.blot(dx, dy, r * 0.42, LEAD + (255,), rnd, n=8, h=150)
        cv.begin()
        for _ in range(3):
            a = rnd.uniform(0, 2 * math.pi)
            q = r * rnd.uniform(0.15, 0.40)
            cv.line([(dx + q * math.cos(a), dy + q * math.sin(a)),
                     (dx + (q + r * 0.25) * math.cos(a), dy + (q + r * 0.25) * math.sin(a))], TOMBAC + (170,), 0.0006, 140)
        cv.disc(dx, dy, r * 0.12, (88, 88, 92, 255), h=100)
    # claw scratches: down to the metal, edges with turned-out paint
    ca, sa = math.cos(L.PL_CLAW_DIR), math.sin(L.PL_CLAW_DIR)
    for x0, y0, ln in L.PL_CLAWS:
        pts = []
        n = 16
        for i in range(n + 1):
            f = i / n
            bend = 0.0012 * math.sin(math.pi * f)
            pts.append((x0 + ca * ln * f - sa * bend, y0 + sa * ln * f + ca * bend))
        # a groove down to the metal, narrower towards the ends: the claw went in and slipped off
        for i in range(n):
            f = math.sin(math.pi * (i + 0.5) / n) ** 0.5
            w = 0.0013 * f
            cv.begin()
            cv.line(pts[i:i + 2], (30, 30, 32, 60), w * 1.8, 150)
            cv.begin()
            cv.line(pts[i:i + 2], (112, 112, 109, 235), w, 70)
            cv.line(pts[i:i + 2], (146, 146, 142, 235), w * 0.45, 60)
    # stamped number (digits) near the front right corner
    f = font(["arialbd.ttf", "arial.ttf"], int(cv.m(0.0042)))
    x, y = cv.px(*L.STAMP)
    num = Image.new("L", (cv.W, cv.H), 0)
    ImageDraw.Draw(num).text((x, y), "1147", font=f, fill=255, anchor="mm")
    cv.hgt.paste(40, (0, 0), num)
    cv.paste((34, 34, 36, 150), num)
    cv.save("decal_plate", 768)


def make_tag():
    tcx, tcy = L.tag_center()
    cv = Canvas(tcx, tcy, L.TAG_BOX, L.TAG_BOX, 256)
    rnd = random.Random(533)
    h, w, cut = L.TAG_L, L.TAG_W / 2, L.TAG_CUT
    outline = [L.tag_point(s, t) for s, t in ((0, -w + cut), (cut, -w), (h, -w), (h, w), (cut, w), (0, w - cut))]
    cv.poly(outline, (204, 178, 128, 255), h=128)
    # grey stripe of the Protection line
    s0, s1 = L.TAG_STRIPE
    cv.begin()
    cv.poly([L.tag_point(s0, -w), L.tag_point(s1, -w), L.tag_point(s1, w), L.tag_point(s0, w)], (112, 112, 110, 255))
    cv.begin()
    # fields in pencil and a hand-written number in digits
    for s in (0.016, 0.023, 0.030):
        cv.line([L.tag_point(s, -w + 0.002), L.tag_point(s, w - 0.002)], (118, 116, 130, 255), 0.00035)
    f = font(["Inkfree.ttf", "BRADHITC.TTF"], int(cv.m(0.0042)))
    num = Image.new("L", (cv.W, cv.H), 0)
    x, y = cv.px(*L.tag_point(0.0265, 0.0))
    ImageDraw.Draw(num).text((x, y), "13-0927", font=f, fill=255, anchor="mm")
    num = num.rotate(L.TAG_ROT - 90.0 + rnd.uniform(-3, 3), center=(x, y))
    cv.paste((40, 44, 82, 235), num)
    # eyelet (under the band, the edge shows)
    hx, hy = L.tag_point(L.TAG_HOLE, 0.0)
    cv.disc(hx, hy, 0.0042, (178, 152, 92, 255), h=200)
    cv.disc(hx, hy, 0.0020, (40, 32, 18, 255), h=40)
    # stains and a worn edge
    for _ in range(6):
        s, t = rnd.uniform(0.01, h - 0.003), rnd.uniform(-w * 0.8, w * 0.8)
        cv.begin()
        cv.blot(*L.tag_point(s, t), rnd.uniform(0.0015, 0.004), (150, 120, 80, 40), rnd, n=4)
    cv.begin()
    cv.line(outline + outline[:1], (168, 140, 96, 255), 0.0007)
    cv.save("decal_tag", 256)


if __name__ == "__main__":
    make_kevlar()
    make_plate()
    make_tag()
