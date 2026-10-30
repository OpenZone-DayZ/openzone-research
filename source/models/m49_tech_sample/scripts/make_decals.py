"""Decals and film of the M49 technical sample (system Python + Pillow), no letters:
- decal_pcb_front.png / decal_pcb_back.png - the 80 x 100 mm board: green mask, traces, tinned pads,
  silkscreen part outlines (no designators), gold-plated connector contacts, resistors and disc
  capacitors drawn in; the solder side has solder drops, clipped leads and a jumper wire (the board has
  been repaired);
- decal_chips.png - the tops of the chips: key, first-lead dot, marking stripes without characters, the
  ROM's quartz window with the die;
- decal_tag.png - the manila tag with an orange stripe (the Electronics line), empty fields, a
  hand-written number in digits; rotated as on the model (TAG_ROT);
- bag_ca.png - the film texture (glass section, 512 x 512): the bag front on the right, the back on the
  left; silvery translucent film, clearer over the board (one layer), denser at the edges (two layers),
  welded seams, weld ribbing, folds, fingerprints; on the front the ESD mark (a hand in a triangle with
  an arc) and two bar lines without letters.

    python make_decals.py      -> ../work/decal_*.png, ../work/bag_ca.png

Sizes come from m49_layout.py (shared with build_m49.py).
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m49_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                       # supersampling factor for drawing (the result is downscaled)

MASK = (34, 96, 58)
TRACE = (58, 128, 80)
TIN = (196, 196, 186)
SOLDER = (214, 214, 206)
SILK = (226, 228, 218)
GOLD = (214, 170, 72)


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


def noise_layer(size, scale, seed, lo=0, hi=255):
    """Soft noise (L): a random grid, stretched and blurred."""
    rnd = random.Random(seed)
    w, h = max(2, size[0] // scale), max(2, size[1] // scale)
    small = Image.new("L", (w, h))
    small.putdata([rnd.randint(lo, hi) for _ in range(w * h)])
    return small.resize(size, Image.BICUBIC).filter(ImageFilter.GaussianBlur(scale * 0.35))


# --- board ------------------------------------------------------------------------------------
class Board:
    """Board canvas in mm: x from -40 to 40, z' from 0 to 100 (the bottom is the contacts)."""

    def __init__(self, ppm):
        self.k = ppm * S
        self.W, self.H = int(L.PCB_W * 1000 * self.k), int(L.PCB_H * 1000 * self.k)

    def p(self, x, z):
        return ((x + 40.0) * self.k, (100.0 - z) * self.k)

    def rect(self, d, x0, z0, x1, z1, **kw):
        a, b = self.p(x0, z1), self.p(x1, z0)
        d.rectangle([a[0], a[1], b[0], b[1]], **kw)

    def circle(self, d, x, z, r, **kw):
        c = self.p(x, z)
        d.ellipse([c[0] - r * self.k, c[1] - r * self.k, c[0] + r * self.k, c[1] + r * self.k], **kw)

    def line(self, d, pts, w, fill):
        d.line([self.p(*q) for q in pts], fill=fill, width=max(1, int(w * self.k)), joint="curve")


def pins(part):
    """DIP lead pads: [(x, z')] - the bottom row left to right, the top row right to left."""
    kind, cx, cz, lx, wz, h, n = part
    half = n // 2
    rs = L.row_spacing(n) / 2
    x0 = cx - (half - 1) * 2.54 / 2
    bot = [(x0 + i * 2.54, cz - rs) for i in range(half)]
    top = [(x0 + i * 2.54, cz + rs) for i in reversed(range(half))]
    return bot + top


def axial_pads(part):
    kind, cx, cz, lx, wz, h, n = part
    return [(cx - lx / 2 - 2.6, cz), (cx + lx / 2 + 2.6, cz)]


def all_pads():
    out = []
    for part in L.PARTS:
        out += pins(part) if part[0] in ("dip", "eprom") else axial_pads(part)
    for x, z in L.RESISTORS:
        out += [(x - 5.1, z), (x + 5.1, z)]
    for x, z in L.CERAMIC:
        out += [(x - 1.27, z), (x + 1.27, z)]
    return out


def traces(bd, d, rnd, pads, count, w, fill):
    """Hand-routed traces: from a pad sideways, a 45-degree turn and then straight to another pad."""
    for _ in range(count):
        a, b = rnd.sample(pads, 2)
        if abs(a[0] - b[0]) + abs(a[1] - b[1]) > 45:
            continue
        dx, dz = b[0] - a[0], b[1] - a[1]
        m = min(abs(dx), abs(dz)) * rnd.choice((0.0, 1.0))
        mid1 = (a[0] + math.copysign(m, dx), a[1] + math.copysign(m, dz))
        if abs(dx) > abs(dz):
            mid2 = (b[0], mid1[1]) if rnd.random() < 0.5 else (mid1[0], b[1])
        else:
            mid2 = (mid1[0], b[1]) if rnd.random() < 0.5 else (b[0], mid1[1])
        bd.line(d, [a, mid1, mid2, b], w, fill)


def fingers(bd, d):
    z0, z1, x0, x1, pitch, key = L.FINGERS
    x = x0
    while x <= x1 + 1e-6:
        if not (key[0] - 1.0 < x < key[1] + 1.0):
            bd.rect(d, x - 0.85, z0 + 0.4, x + 0.85, z1, fill=GOLD)
            bd.line(d, [(x, z1), (x, z1 + 3.0)], 0.4, TRACE)
        x += pitch
    bd.rect(d, key[0], -1.0, key[1], z1 - 2.5, fill=(18, 30, 22))      # key notch (shadow)


def base_board(bd, seed):
    img = Image.new("RGB", (bd.W, bd.H), MASK)
    tone = noise_layer(img.size, 40 * S, seed, 0, 40)
    img = Image.composite(Image.new("RGB", img.size, tuple(int(c * 0.86) for c in MASK)), img, tone)
    return img


def make_pcb_front(name, ppm):
    bd = Board(ppm)
    rnd = random.Random(49)
    img = base_board(bd, 11)
    d = ImageDraw.Draw(img)
    pads = all_pads()
    traces(bd, d, rnd, pads, 70, 0.35, TRACE)
    for x, z in pads:
        bd.circle(d, x, z, 0.8, fill=TIN)
        bd.circle(d, x, z, 0.35, fill=(90, 92, 88))
    # silkscreen: part outlines, key, '+' at capacitors - no designators
    for part in L.PARTS:
        kind, cx, cz, lx, wz, h, n = part
        m = 1.0
        bd.rect(d, cx - lx / 2 - m, cz - wz / 2 - m, cx + lx / 2 + m, cz + wz / 2 + m, outline=SILK,
                width=max(1, int(0.22 * bd.k)))
        if kind in ("dip", "eprom"):
            c = bd.p(cx - lx / 2 - m, cz)
            r = 1.4 * bd.k
            d.arc([c[0] - r, c[1] - r, c[0] + r, c[1] + r], -90, 90, fill=SILK, width=max(1, int(0.22 * bd.k)))
        if kind == "cap":
            px, pz = cx + lx / 2 + 3.0, cz + 4.2
            bd.line(d, [(px - 1, pz), (px + 1, pz)], 0.25, SILK)
            bd.line(d, [(px, pz - 1), (px, pz + 1)], 0.25, SILK)
    # MLT resistors: body with stripes, leads to the pads
    bands = [(120, 72, 40), (20, 20, 20), (190, 40, 30), (200, 160, 60)]
    for x, z in L.RESISTORS:
        bd.line(d, [(x - 5.1, z), (x + 5.1, z)], 0.5, (176, 176, 170))
        bd.rect(d, x - 3.0, z - 1.1, x + 3.0, z + 1.1, fill=(204, 170, 128))
        bd.rect(d, x - 3.0, z + 0.45, x + 3.0, z + 1.1, fill=(226, 200, 160))      # highlight
        for i, col in enumerate(bands):
            bx = x - 2.0 + i * 1.1 + (0.5 if i == 3 else 0.0)
            bd.rect(d, bx - 0.3, z - 1.1, bx + 0.3, z + 1.1, fill=col)
    # disc ceramic capacitors
    for x, z in L.CERAMIC:
        bd.circle(d, x, z, 2.0, fill=(196, 112, 48))
        bd.circle(d, x - 0.5, z + 0.5, 0.9, fill=(222, 150, 84))
    fingers(bd, d)
    for x, z in L.HOLES:
        bd.circle(d, x, z, 2.6, fill=TIN)
        bd.circle(d, x, z, 1.6, fill=(14, 16, 14))
    for _ in range(40):                                    # vias
        x, z = rnd.uniform(-37, 37), rnd.uniform(10, 98)
        bd.circle(d, x, z, 0.45, fill=TIN)
    save(img, (bd.W // S, bd.H // S), name)


def make_pcb_back(name, ppm):
    bd = Board(ppm)
    rnd = random.Random(1949)
    img = base_board(bd, 23)
    d = ImageDraw.Draw(img)
    pads = all_pads()
    traces(bd, d, rnd, pads, 140, 0.5, TRACE)
    # power buses along the edges
    bd.line(d, [(-38.5, 9.0), (-38.5, 98.5), (38.5, 98.5), (38.5, 9.0)], 1.6, TRACE)
    for x, z in pads:
        bd.circle(d, x, z, 1.0, fill=SOLDER)
        bd.circle(d, x + 0.25, z + 0.25, 0.45, fill=(236, 236, 230))       # drop, highlight
        bd.circle(d, x - 0.1, z - 0.1, 0.18, fill=(120, 120, 116))         # clipped lead
    fingers(bd, d)
    for x, z in L.HOLES:
        bd.circle(d, x, z, 2.6, fill=TIN)
        bd.circle(d, x, z, 1.6, fill=(14, 16, 14))
    # jumper wire MGTF - a repair after a trace
    bd.line(d, [(-21.0 + 1.27 * 3, 16.2), (-12.0, 30.0), (-12.0, 48.0), (-8.0, 30.9)], 0.6, (196, 60, 48))
    for q in ((-21.0 + 1.27 * 3, 16.2), (-8.0, 30.9)):
        bd.circle(d, q[0], q[1], 0.9, fill=SOLDER)
    # rosin traces near a pair of rows
    flux = Image.new("RGBA", img.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(flux)
    for part in L.PARTS[3:6]:
        cx, cz = part[1], part[2]
        c = bd.p(cx, cz)
        r = (8 + rnd.random() * 6) * bd.k
        fd.ellipse([c[0] - r * 1.6, c[1] - r * 0.6, c[0] + r * 1.6, c[1] + r * 0.6], fill=(170, 120, 40, 70))
    flux = flux.filter(ImageFilter.GaussianBlur(3 * bd.k))
    img = Image.alpha_composite(img.convert("RGBA"), flux).convert("RGB")
    save(img, (bd.W // S, bd.H // S), name)


def make_chips(name, ppm):
    """Chip tops in board coordinates; transparent outside the packages."""
    bd = Board(ppm)
    rnd = random.Random(7)
    img = Image.new("RGBA", (bd.W, bd.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for part in L.PARTS:
        kind, cx, cz, lx, wz, h, n = part
        if kind not in ("dip", "eprom"):
            continue
        x0 = cx - lx / 2
        # key - a semicircular notch on the end, a dot at the first lead
        c = bd.p(x0, cz)
        r = min(1.4, wz * 0.22) * bd.k
        d.pieslice([c[0] - r, c[1] - r, c[0] + r, c[1] + r], -90, 90, fill=(12, 12, 13, 255))
        bd.circle(d, x0 + 2.2, cz - wz / 2 + 1.6, 0.55, fill=(16, 16, 17, 255))
        if kind == "eprom":
            # erase window: a quartz disc with the die and its leads under it
            bd.circle(d, cx + 2.0, cz, 4.0, fill=(150, 146, 136, 255))
            bd.circle(d, cx + 2.0, cz, 3.3, fill=(44, 40, 52, 255))
            bd.rect(d, cx + 0.2, cz - 1.8, cx + 3.8, cz + 1.8, fill=(176, 150, 82, 255))
            bd.rect(d, cx + 0.8, cz - 1.2, cx + 3.2, cz + 1.2, fill=(96, 90, 110, 255))
            bd.circle(d, cx + 0.9, cz + 1.6, 1.0, fill=(220, 226, 240, 140))   # quartz highlight
            mx = cx - lx / 2 + 6.0
        else:
            mx = x0 + 4.2
        # marking - light stripes without characters (worn off)
        for i, frac in enumerate((0.62, 0.42)):
            zz = cz + (0.25 - 0.55 * i) * wz * 0.5
            ln = (lx - 9.0) * frac * (0.8 + 0.3 * rnd.random())
            bd.rect(d, mx, zz - 0.45, mx + ln, zz + 0.45, fill=(150, 150, 146, 170))
    save(img, (bd.W // S, bd.H // S), name)


# --- tag --------------------------------------------------------------------------------------
def make_tag(name, ppm):
    k = ppm * S
    W, H = int(L.TAG_W * 1000 * k), int(L.TAG_H * 1000 * k)
    img = Image.new("RGBA", (W, H), (228, 214, 172, 255))
    tone = noise_layer((W, H), 6 * k, 5, 0, 70)
    img = Image.composite(Image.new("RGBA", (W, H), (206, 190, 146, 255)), img, tone)
    d = ImageDraw.Draw(img)
    d.rectangle([0, int(H * 0.16), W, int(H * 0.36)], fill=(230, 116, 30, 255))     # line stripe
    ink = (66, 60, 56, 255)
    for i, y in enumerate((0.56, 0.74, 0.90)):
        d.line([(W * 0.07, H * y), (W * (0.93 if i else 0.50), H * y)], fill=ink, width=max(1, int(0.18 * k)))
    d.line([(W * 0.56, H * 0.46), (W * 0.56, H * 0.56)], fill=ink, width=max(1, int(0.18 * k)))
    # hand-written number in blue pen
    f = font(("Inkfree.ttf", "segoepr.ttf", "segoesc.ttf", "arial.ttf"), int(H * 0.17))
    d.text((W * 0.10, H * 0.545), "17-0412", fill=(40, 52, 140, 255), font=f, anchor="ls")
    d.text((W * 0.62, H * 0.545), "26", fill=(40, 52, 140, 255), font=f, anchor="ls")
    # staple puncture and dirt at the edge
    d.rectangle([W * 0.5 - 6.0 * k, H * 0.115 - 0.5 * k, W * 0.5 + 6.0 * k, H * 0.115 + 0.5 * k],
                fill=(150, 140, 120, 255))
    edge = Image.new("L", (W, H), 0)
    ImageDraw.Draw(edge).rectangle([0, 0, W - 1, H - 1], outline=110, width=int(1.2 * k))
    edge = ImageChops.multiply(edge.filter(ImageFilter.GaussianBlur(1.5 * k)), noise_layer((W, H), 3 * k, 9))
    img = Image.composite(Image.new("RGBA", (W, H), (150, 132, 96, 255)), img, edge)
    img = img.rotate(L.TAG_ROT, resample=Image.BICUBIC, expand=True)
    save(img, (img.size[0] // S, img.size[1] // S), name)


# --- film -------------------------------------------------------------------------------------
def esd_symbol(d, cx, cy, size, k, ink):
    """ESD mark (ANSI/ESD S8.1, protective): a triangle with a hand in it and an arc above it."""
    h = size * math.sqrt(3) / 2
    tri = [(cx, cy - h * 0.62), (cx - size / 2, cy + h * 0.38), (cx + size / 2, cy + h * 0.38)]
    d.polygon(tri, outline=ink, width=int(1.1 * k))
    # hand: a palm with four fingers and a thumb, reaching to the tip
    u = size / 22.0
    hand = [(-3.2, 5.6), (-3.6, 0.6), (-4.6, -2.0), (-3.6, -2.4), (-2.4, -0.4), (-2.4, -5.4), (-1.3, -5.6),
            (-0.9, -1.6), (-0.6, -6.4), (0.6, -6.4), (0.7, -1.6), (1.4, -5.8), (2.5, -5.4), (2.0, -1.0),
            (3.2, -4.4), (4.1, -3.9), (2.6, 1.2), (2.4, 5.6)]
    d.polygon([(cx + x * u, cy + (y + 1.6) * u) for x, y in hand], fill=ink)
    r = size * 0.70
    oy = cy + h * 0.10
    d.arc([cx - r, oy - r, cx + r, oy + r], 205, 335, fill=ink, width=int(1.1 * k))


def film_half(front, k):
    """Half of the film texture (front or back) on a mm canvas: RGBA."""
    Wm, Hm = L.BAG_W * 1000, L.BAG_H * 1000
    W, H = int(Wm * k), int(Hm * k)

    def p(x, z):                         # model metres -> canvas px (x left to right as on the front)
        return ((x + L.HX) * 1000 * k, (L.HZ - z) * 1000 * k)
    seed = 3 if front else 8
    alpha = Image.new("L", (W, H), 170)                     # two film layers
    ad = ImageDraw.Draw(alpha)
    a, b = p(L.pcb_x(-40), L.pcb_z(100)), p(L.pcb_x(40), L.pcb_z(0))
    ad.rectangle([a[0], a[1], b[0], b[1]], fill=106)      # over the board - one layer
    alpha = alpha.filter(ImageFilter.GaussianBlur(2.0 * k))
    ad = ImageDraw.Draw(alpha)
    sm = L.SIDE_SEAM * 1000 * k
    for box in ((0, 0, sm, H), (W - sm, 0, W, H), (0, H - sm, W, H)):
        ad.rectangle(box, fill=208)
    s0, s1 = p(0, L.SEAL_Z1)[1], p(0, L.SEAL_Z0)[1]
    ad.rectangle([0, 0, W, s0], fill=176)                     # neck above the weld
    y = s0
    i = 0
    while y < s1:                                             # weld ribbing, 1 mm pitch
        ad.rectangle([0, y, W, y + 0.5 * k], fill=222 if i % 2 else 200)
        y += 0.5 * k
        i += 1
    rgb = Image.new("RGB", (W, H), (134, 137, 143))         # smoky silver of the metallisation
    light = Image.new("RGB", (W, H), (166, 169, 174))
    seams = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(seams)
    for box in ((0, 0, sm, H), (W - sm, 0, W, H), (0, H - sm, W, H), (0, s0, W, s1)):
        sd.rectangle(box, fill=150)
    rgb = Image.composite(light, rgb, seams.filter(ImageFilter.GaussianBlur(0.3 * k)))
    # smudges and fingerprints: tone and density
    mott = noise_layer((W, H), int(9 * k), seed, 0, 255)
    rgb = Image.composite(Image.new("RGB", (W, H), (120, 123, 129)), rgb, mott.point(lambda v: v // 4))
    alpha = ImageChops.add(alpha, mott.point(lambda v: max(0, v - 150) // 5))
    rnd = random.Random(seed)
    prints = Image.new("L", (W, H), 0)
    pd = ImageDraw.Draw(prints)
    for _ in range(3 if front else 2):                       # fingerprints - blotches with rings
        cx, cy = rnd.uniform(0.15, 0.85) * W, rnd.uniform(0.15, 0.9) * H
        for j in range(7):
            r = (2.0 + j * 1.1) * k
            pd.ellipse([cx - r, cy - r * 1.3, cx + r, cy + r * 1.3], outline=60, width=int(0.4 * k))
    prints = prints.filter(ImageFilter.GaussianBlur(0.4 * k))
    rgb = Image.composite(Image.new("RGB", (W, H), (160, 162, 166)), rgb, prints)
    alpha = ImageChops.add(alpha, prints.point(lambda v: v // 3))
    # folds: light crease lines (one follows the model fold), small creases at the edges
    cr = Image.new("L", (W, H), 0)
    cd = ImageDraw.Draw(cr)
    (x0, z0), (x1, z1) = L.CREASE
    cd.line([p(x0, z0), p(x1, z1)], fill=210, width=int(0.7 * k))
    (x0, z0), (x1, z1) = L.DOGEAR
    cd.line([p(x0, z0), p(x1, z1)], fill=230, width=int(0.8 * k))
    for _ in range(16):
        x, z = rnd.uniform(-L.HX, L.HX), rnd.uniform(-L.HZ, L.HZ)
        if abs(x) < 0.03 and abs(z) < 0.04:
            continue                                          # the film is taut over the board
        ang = rnd.uniform(0, math.pi)
        ln = rnd.uniform(0.006, 0.020)
        pts = [p(x, z)]
        for _ in range(3):
            ang += rnd.uniform(-0.4, 0.4)
            x, z = x + math.cos(ang) * ln / 3, z + math.sin(ang) * ln / 3
            pts.append(p(x, z))
        cd.line(pts, fill=rnd.randint(110, 190), width=max(1, int(0.35 * k)))
    cr = cr.filter(ImageFilter.GaussianBlur(0.35 * k))
    rgb = Image.composite(Image.new("RGB", (W, H), (204, 206, 210)), rgb, cr)
    alpha = ImageChops.add(alpha, cr.point(lambda v: v // 4))
    img = rgb.convert("RGBA")
    img.putalpha(alpha)
    if front:
        # paint print: the ESD mark and two bar lines (no letters)
        ink = (22, 22, 24, 236)
        pr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(pr)
        c = p(*L.ESD_C)
        esd_symbol(dd, c[0], c[1], L.ESD_SIZE * 1000 * k, k, ink)
        for j, ln in enumerate((24.0, 17.0)):
            yy = c[1] + (L.ESD_SIZE * 1000 * 0.62 + 3.0 + 3.0 * j) * k
            dd.rectangle([c[0] - ln / 2 * k, yy, c[0] + ln / 2 * k, yy + 1.1 * k], fill=(22, 22, 24, 200))
        wear = noise_layer((W, H), int(2 * k), 31, 0, 255).point(lambda v: 255 if v > 70 else 120)
        pr.putalpha(ImageChops.multiply(pr.getchannel("A"), wear))
        img = Image.alpha_composite(img, pr)
    return img


def make_bag_ca(name, size=512):
    k = 8
    front = film_half(True, k).resize((size // 2, size), Image.LANCZOS)
    back = film_half(False, k).resize((size // 2, size), Image.LANCZOS)     # x as on the front
    img = Image.new("RGBA", (size, size))
    img.paste(back, (0, 0))
    img.paste(front, (size // 2, 0))
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


if __name__ == "__main__":
    make_pcb_front("decal_pcb_front.png", 5)
    make_pcb_back("decal_pcb_back.png", 5)
    make_chips("decal_chips.png", 5)
    make_tag("decal_tag.png", 8)
    make_bag_ca("bag_ca.png")
