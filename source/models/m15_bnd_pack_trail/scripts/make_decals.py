"""Decals for the spotter's table (system Python + Pillow): the terrain map on the back panel (own,
invented: forest, fields, a river, roads, a railway, contour lines, a kilometre grid with digits, no
names) with marker marks under the pins and a dotted route; photos and notes on the board; papers on the
table (scribbled lines, a table of digits, a hand-drawn sketch, a photo); the pager display - own
texture: "off" and 8 "work" frames (digits run, the envelope blinks); the "Elektronika-302" tape
recorder - an aluminium strip (knob scales, key symbols), the recording indicator scale, the cassette
label; traces on the boards at the empty places of modules 1 and 3. No letters: the scribbles do not
form words, only digits, divisions and symbols. Papers are turned the way they lie (layout.py): kmats
projects decals along the world axes.

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
S = 2                                   # supersampling, then downscale: smooth edges
PX_M = 1600                             # pixels per metre for the map and papers
PAPER = (226, 222, 204)
INK = (40, 46, 70)
MARKER = (196, 28, 24)


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


def rotated(img, deg, name, w_m, h_m, px_m=PX_M):
    """Image of an item w_m x h_m metres, rotated by deg (counter-clockwise, top view), with transparent
    corners: the size is the frame of the rotated rectangle (as in M13)."""
    a = math.radians(deg)
    bw = w_m * abs(math.cos(a)) + h_m * abs(math.sin(a))
    bh = w_m * abs(math.sin(a)) + h_m * abs(math.cos(a))
    big = img.convert("RGBA").rotate(deg, resample=Image.BICUBIC, expand=True)
    save(big, (max(8, int(bw * px_m)), max(8, int(bh * px_m))), name)


def aged(img, rnd, stains=3):
    """Yellowed spots, worn folds, dirty prints - the paper is not new."""
    W, H = img.size
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for _ in range(stains):
        r = rnd.uniform(0.06, 0.18) * min(W, H)
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(120, 90, 40, rnd.randint(20, 45)))
    # ring from a mug
    if rnd.random() < 0.5:
        r = 0.04 * PX_M * S
        x, y = rnd.uniform(0.2, 0.8) * W, rnd.uniform(0.2, 0.8) * H
        d.ellipse([x - r, y - r, x + r, y + r], outline=(110, 70, 30, 70), width=S * 3)
    ov = ov.filter(ImageFilter.GaussianBlur(S * 6))
    # folds
    f = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(f)
    fd.line([(0, H / 2), (W, H / 2)], fill=(90, 80, 60, 50), width=S * 2)
    if W > H:
        fd.line([(W / 2, 0), (W / 2, H)], fill=(90, 80, 60, 40), width=S * 2)
    f = f.filter(ImageFilter.GaussianBlur(S))
    return Image.alpha_composite(Image.alpha_composite(img.convert("RGBA"), ov), f)


def scribble(d, x0, y, x1, h, rnd, ink, width):
    """A line of scribbles: a wave with loops and gaps between "words" - reads like handwriting, but there
    are no letters."""
    x = x0
    while x < x1:
        wl = rnd.uniform(0.6, 2.2) * h * 2
        pts = []
        xe = min(x + wl, x1)
        k = 0
        while x < xe:
            pts.append((x, y - h * (0.5 + 0.5 * math.sin(k * 1.9 + rnd.uniform(-0.6, 0.6))) * rnd.uniform(0.6, 1.0)))
            x += h * rnd.uniform(0.25, 0.45)
            k += 1
        if len(pts) > 1:
            d.line(pts, fill=ink, width=width, joint="curve")
        x += h * rnd.uniform(0.8, 1.4)


# =============================================================================
# Map
# =============================================================================
def noise_field(W, H, rnd, n, rmin, rmax, blur):
    """Hill blobs: random circles, blurred - a height field / forest mask."""
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    for _ in range(n):
        r = rnd.uniform(rmin, rmax)
        x, y = rnd.uniform(-r, W + r), rnd.uniform(-r, H + r)
        d.ellipse([x - r, y - r, x + r, y + r], fill=rnd.randint(30, 90))
    return im.filter(ImageFilter.GaussianBlur(blur))


def curve(rnd, p0, p1, wobble, n=24):
    """A winding line from p0 to p1."""
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy)
    nx, ny = -dy / ln, dx / ln
    ph1, ph2 = rnd.uniform(0, 6), rnd.uniform(0, 6)
    pts = []
    for i in range(n + 1):
        t = i / n
        o = wobble * (math.sin(t * 7.0 + ph1) * 0.6 + math.sin(t * 13.0 + ph2) * 0.3) * math.sin(math.pi * t) ** 0.3
        pts.append((x0 + dx * t + nx * o, y0 + dy * t + ny * o))
    return pts


def make_map():
    x0, x1, z0, z1 = L.MAP
    wm, hm = x1 - x0, z1 - z0
    W, H = int(wm * PX_M * S), int(hm * PX_M * S)
    rnd = random.Random(15)

    def px(x, z):
        return ((x - x0) / wm * W, (z1 - z) / hm * H)
    img = Image.new("RGB", (W, H), (234, 230, 208))
    # forest: green masses by the mask
    forest = noise_field(W, H, rnd, 60, H * 0.08, H * 0.25, H * 0.04).point(lambda v: 255 if v > 48 else 0)
    img.paste((178, 206, 156), mask=forest)
    # fields: light-yellow rectangles
    d = ImageDraw.Draw(img)
    for _ in range(9):
        cx, cy = rnd.uniform(0, W), rnd.uniform(0, H)
        w, h = rnd.uniform(0.05, 0.12) * W, rnd.uniform(0.08, 0.2) * H
        d.rectangle([cx - w, cy - h, cx + w, cy + h], fill=(240, 232, 186))
    # contour lines: a height field, steps, step edges as brown lines
    hgt = noise_field(W, H, rnd, 90, H * 0.1, H * 0.45, H * 0.08)
    steps = hgt.point(lambda v: (v // 9) * 40 % 256)
    edges = steps.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 10 else 0)
    img.paste((170, 120, 70), mask=edges.filter(ImageFilter.MaxFilter(3)) if S > 1 else edges)
    # lake and swamp
    for _ in range(2):
        cx, cy, r = rnd.uniform(0.2, 0.8) * W, rnd.uniform(0.2, 0.8) * H, rnd.uniform(0.04, 0.07) * H
        d.ellipse([cx - r * 1.6, cy - r, cx + r * 1.6, cy + r], fill=(150, 196, 222), outline=(60, 120, 170), width=S * 2)
    for _ in range(30):
        cx, cy = rnd.uniform(0.6, 0.9) * W, rnd.uniform(0.55, 0.9) * H
        d.line([(cx, cy), (cx + S * 10, cy)], fill=(60, 120, 170), width=S * 2)
    # river
    river = curve(rnd, (-10, H * 0.25), (W + 10, H * 0.75), H * 0.12, 40)
    d.line(river, fill=(130, 180, 214), width=S * 9, joint="curve")
    d.line(river, fill=(60, 120, 170), width=S * 2, joint="curve")
    # roads: a highway (orange with an outline) and dirt roads (dotted)
    for p0, p1, wd in (((0, H * 0.62), (W, H * 0.38), 7), ((W * 0.35, H), (W * 0.55, 0), 5)):
        road = curve(rnd, p0, p1, H * 0.05, 30)
        d.line(road, fill=(60, 50, 40), width=S * (wd + 2), joint="curve")
        d.line(road, fill=(236, 150, 60), width=S * wd, joint="curve")
    for _ in range(5):
        tr = curve(rnd, (rnd.uniform(0, W), rnd.uniform(0, H)), (rnd.uniform(0, W), rnd.uniform(0, H)), H * 0.05, 90)
        for i in range(0, len(tr) - 1, 2):
            d.line([tr[i], tr[i + 1]], fill=(90, 70, 50), width=S * 2)
    # railway: a black-and-white stripe
    rail = curve(rnd, (W * 0.1, 0), (W * 0.9, H), H * 0.02, 30)
    d.line(rail, fill=(30, 30, 30), width=S * 6, joint="curve")
    for i in range(0, len(rail) - 1, 2):
        d.line([rail[i], rail[i + 1]], fill=(250, 250, 250), width=S * 3)
    # villages: blocks of black houses
    for _ in range(6):
        cx, cy = rnd.uniform(0.08, 0.92) * W, rnd.uniform(0.1, 0.9) * H
        for _ in range(rnd.randint(6, 14)):
            hx, hy = cx + rnd.uniform(-1, 1) * W * 0.03, cy + rnd.uniform(-1, 1) * H * 0.05
            d.rectangle([hx, hy, hx + S * 6, hy + S * 4], fill=(30, 30, 30))
    # kilometre grid with digits at the edge
    step = 0.10 * PX_M * S
    fnt = font(int(S * 14))
    k = 0
    gx = step * 0.4
    while gx < W:
        d.line([(gx, 0), (gx, H)], fill=(40, 40, 60), width=S)
        d.text((gx + S * 3, S * 2), "%02d" % (34 + k), fill=(40, 40, 60), font=fnt)
        gx += step
        k += 1
    k = 0
    gy = H - step * 0.3
    while gy > 0:
        d.line([(0, gy), (W, gy)], fill=(40, 40, 60), width=S)
        d.text((S * 3, gy - S * 16), "%02d" % (61 + k), fill=(40, 40, 60), font=fnt)
        gy -= step
        k += 1
    # frame
    d.rectangle([0, 0, W - 1, H - 1], outline=(30, 30, 30), width=S * 4)
    # marker: circles and crosses under the pins on the map, a dotted route, hatching of a zone
    on_map = [(x, z) for x, z, _ in L.PINS if x0 < x < x1 and z0 < z < z1]
    for i, (x, z) in enumerate(on_map):
        cx, cy = px(x, z)
        r = S * rnd.uniform(18, 26)
        if i % 3 == 2:
            d.line([(cx - r, cy - r), (cx + r, cy + r)], fill=MARKER, width=S * 4)
            d.line([(cx - r, cy + r), (cx + r, cy - r)], fill=MARKER, width=S * 4)
        else:
            d.ellipse([cx - r, cy - r * 0.9, cx + r, cy + r * 0.9], outline=MARKER, width=S * 4)
    route = [px(*p) for p in on_map[:5]]
    for a, b in zip(route, route[1:]):
        n = int(math.hypot(b[0] - a[0], b[1] - a[1]) / (S * 14))
        for j in range(0, n, 2):
            t0, t1 = j / n, (j + 1) / n
            d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0),
                    (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], fill=(30, 30, 140), width=S * 3)
    cx, cy = px(0.15, 1.00)
    for j in range(-6, 7):
        d.line([(cx + j * S * 10 - S * 40, cy + S * 40), (cx + j * S * 10 + S * 40, cy - S * 40)], fill=MARKER, width=S * 2)
    d.ellipse([cx - S * 50, cy - S * 50, cx + S * 50, cy + S * 50], outline=MARKER, width=S * 4)
    img = aged(img, rnd, 6)
    save(img, (int(wm * PX_M), int(hm * PX_M)), "decal_map.png")


# =============================================================================
# Photos and papers
# =============================================================================
def photo_img(w_m, h_m, seed):
    """Photo 9 x 13 with a white border: a grey-green landscape - a forest edge, the silhouette of a building
    or a tower, blurred (shot on a point-and-shoot camera)."""
    rnd = random.Random(seed)
    W, H = int(w_m * PX_M * S * 2), int(h_m * PX_M * S * 2)
    img = Image.new("RGB", (W, H), (236, 234, 226))
    m = int(min(W, H) * 0.06)
    ph = Image.new("RGB", (W - 2 * m, H - 2 * m), (150, 160, 150))
    d = ImageDraw.Draw(ph)
    pw, phh = ph.size
    sky = rnd.uniform(0.35, 0.5) * phh
    d.rectangle([0, 0, pw, sky], fill=(176, 182, 184))
    d.rectangle([0, sky, pw, phh], fill=(86, 96, 70))
    pts = [(0, sky)] + [(x, sky - rnd.uniform(0.02, 0.12) * phh) for x in range(0, pw + 20, max(4, pw // 18))] + [(pw, sky)]
    d.polygon(pts, fill=(54, 66, 50))
    kind = seed % 3
    if kind == 0:     # building with windows
        bx = rnd.uniform(0.2, 0.5) * pw
        d.rectangle([bx, sky - 0.35 * phh, bx + 0.35 * pw, sky + 0.05 * phh], fill=(120, 116, 108))
        for i in range(5):
            for j in range(3):
                d.rectangle([bx + (0.03 + 0.065 * i) * pw, sky - (0.31 - 0.1 * j) * phh,
                             bx + (0.06 + 0.065 * i) * pw, sky - (0.25 - 0.1 * j) * phh], fill=(40, 40, 44))
    elif kind == 1:   # tower
        bx = rnd.uniform(0.3, 0.6) * pw
        d.line([(bx, sky + 0.05 * phh), (bx + 0.06 * pw, sky - 0.5 * phh), (bx + 0.12 * pw, sky + 0.05 * phh)],
               fill=(40, 40, 40), width=max(2, pw // 80))
        d.rectangle([bx + 0.03 * pw, sky - 0.56 * phh, bx + 0.09 * pw, sky - 0.48 * phh], fill=(50, 50, 50))
    else:             # road and posts
        d.polygon([(pw * 0.4, phh), (pw * 0.48, sky), (pw * 0.52, sky), (pw * 0.75, phh)], fill=(110, 104, 94))
        for k in range(4):
            x = pw * (0.6 + 0.08 * k)
            d.line([(x, sky - 0.2 * phh / (k + 1)), (x, sky + 0.25 * phh / (k + 1))], fill=(30, 30, 30), width=3)
    ph = ph.filter(ImageFilter.GaussianBlur(max(1, pw // 160)))
    img.paste(ph, (m, m))
    return aged(img, rnd, 1)


def note_img(w_m, h_m, seed, kind):
    """Sheet: lines of scribbles (lines), a table of digits (table, digits are allowed), a sketch (sketch)."""
    rnd = random.Random(seed)
    W, H = int(w_m * PX_M * S), int(h_m * PX_M * S)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    ink = INK if seed % 2 else (30, 30, 30)
    lw = max(1, S * 2)
    if kind == "lines":
        # school notebook grid
        c = 0.005 * PX_M * S
        x = c
        while x < W:
            d.line([(x, 0), (x, H)], fill=(196, 206, 214), width=1)
            x += c
        y = c
        while y < H:
            d.line([(0, y), (W, y)], fill=(196, 206, 214), width=1)
            y += c
        y = H * 0.08
        while y < H * 0.92:
            scribble(d, W * 0.08, y, W * rnd.uniform(0.6, 0.92), c * 0.9, rnd, ink, lw)
            y += c * 2
    elif kind == "table":
        fnt = font(int(H * 0.028))
        rows, cols = 16, 4
        for i in range(rows + 1):
            y = H * (0.08 + 0.84 * i / rows)
            d.line([(W * 0.06, y), (W * 0.94, y)], fill=(60, 60, 60), width=1)
        for j in range(cols + 1):
            x = W * (0.06 + 0.88 * j / cols)
            d.line([(x, H * 0.08), (x, H * 0.92)], fill=(60, 60, 60), width=1)
        for i in range(rows):
            for j in range(cols):
                if rnd.random() < 0.85:
                    s = ["%02d" % rnd.randint(1, 31), "%04d" % rnd.randint(0, 9999), "%d.%02d" % (rnd.randint(0, 9), rnd.randint(0, 99)),
                         "%03d" % rnd.randint(0, 360)][j]
                    d.text((W * (0.09 + 0.88 * j / cols), H * (0.085 + 0.84 * i / rows)), s, fill=ink, font=fnt)
        # three lines crossed out with a marker
        for i in rnd.sample(range(rows), 3):
            y = H * (0.08 + 0.84 * (i + 0.5) / rows)
            d.line([(W * 0.05, y), (W * 0.95, y)], fill=MARKER, width=S * 3)
    else:  # sketch: hand-drawn plan - road, stream, forest symbols, north arrow, crosses
        d.line(curve(rnd, (0, H * 0.7), (W, H * 0.4), H * 0.06), fill=ink, width=lw * 2)
        d.line(curve(rnd, (0, H * 0.75), (W, H * 0.45), H * 0.06), fill=ink, width=lw * 2)
        d.line(curve(rnd, (W * 0.3, 0), (W * 0.45, H), W * 0.05), fill=(40, 80, 160), width=lw * 2)
        for _ in range(40):
            x, y = rnd.uniform(0.55, 0.95) * W, rnd.uniform(0.05, 0.35) * H
            r = S * rnd.uniform(5, 8)
            d.ellipse([x - r, y - r, x + r, y + r], outline=ink, width=lw)
            d.line([(x, y + r), (x, y + r * 2)], fill=ink, width=lw)
        for _ in range(4):
            x, y = rnd.uniform(0.1, 0.5) * W, rnd.uniform(0.1, 0.9) * H
            d.rectangle([x, y, x + S * 16, y + S * 12], outline=ink, width=lw)
        ax, ay = W * 0.9, H * 0.8
        d.line([(ax, ay), (ax, ay - H * 0.12)], fill=ink, width=lw * 2)
        d.polygon([(ax - S * 8, ay - H * 0.10), (ax, ay - H * 0.14), (ax + S * 8, ay - H * 0.10)], fill=ink)
        for x, y in ((0.2, 0.5), (0.62, 0.62), (0.78, 0.25)):
            cx, cy, r = x * W, y * H, S * 14
            d.line([(cx - r, cy - r), (cx + r, cy + r)], fill=MARKER, width=S * 4)
            d.line([(cx - r, cy + r), (cx + r, cy - r)], fill=MARKER, width=S * 4)
        fnt = font(int(H * 0.04))
        for x, y in ((0.25, 0.42), (0.66, 0.70)):
            d.text((x * W, y * H), "%d" % rnd.randint(100, 900), fill=ink, font=fnt)
    return aged(img, rnd, 3)


def make_papers():
    for nm, x0, x1, z0, z1 in L.PINNED:
        w, h = x1 - x0, z1 - z0
        img = photo_img(w, h, len(nm) + int(x0 * 100)) if nm.startswith("photo") else note_img(w, h, 7 + int(z0 * 10), "lines")
        save(img, (int(w * PX_M), int(h * PX_M)), "decal_%s.png" % nm)
    for i, (nm, c, deg, (w, h), dz, kind, curl) in enumerate(L.PAPERS):
        img = photo_img(w, h, 5 + i) if kind == "photo" else note_img(w, h, 11 + i, kind)
        rotated(img, deg, "decal_%s.png" % nm, w, h)


# =============================================================================
# Pager display - own texture (section pager): "off" and "work" frames
# =============================================================================
PAGER_MSG = "0417 23  1186 05  2240 "
PAGER_FRAMES = 8


def pager_img(text, icon):
    """Digital pager display (LCD 36 x 16): grey-green field, dark digits and an envelope icon. The image is
    in the pager axes (u along, v toward the display top): the part UV 0..1 over its frame."""
    W, H = 360 * S, 160 * S
    on = text is not None
    img = Image.new("RGBA", (W, H), (166, 180, 140, 255) if on else (82, 90, 78, 255))
    d = ImageDraw.Draw(img)
    # shadow of the frame along the glass edge
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H], outline=(0, 0, 0, 90), width=S * 10)
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(S * 6)))
    d = ImageDraw.Draw(img)
    if on:
        ink = (26, 32, 24, 255)
        d.text((W * 0.06, H * 0.60), text, fill=ink, font=font(int(H * 0.50)), anchor="lm")
        # status line: charge divisions and an envelope icon (no letters)
        for k in range(4):
            d.rectangle([W * (0.74 + 0.05 * k), H * 0.10, W * (0.77 + 0.05 * k), H * 0.22], fill=ink)
        if icon:
            x0, y0, x1, y1 = W * 0.06, H * 0.08, W * 0.20, H * 0.26
            d.rectangle([x0, y0, x1, y1], outline=ink, width=S * 2)
            d.line([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2), (x1, y0)], fill=ink, width=S * 2)
    return img


def make_pager():
    save(pager_img(None, False), (256, 128), "decal_pager_off.png")
    msg = PAGER_MSG * 2
    for k in range(PAGER_FRAMES):
        save(pager_img(msg[k:k + 8], k % 2 == 0), (256, 128), "decal_pager_f%02d.png" % k)


# =============================================================================
# "Elektronika-302" tape recorder: strip with knobs and keys, indicator scale, cassette label
# =============================================================================
PX_REC = 4000                           # pixels per metre for the recorder details


def make_rec_strip():
    """Slanted aluminium strip in plan view (x is the recorder width, the picture top is toward the deck):
    brushed finish, knob scales (divisions and digits 2-14), the field under the keys, key symbols - record
    (red dot), rewind, play, stop, eject. No letters."""
    y0, y1, z0, z1 = L.REC_STRIP
    W, H = int(L.REC_W * PX_REC * S), int((y1 - y0) * PX_REC * S)
    rnd = random.Random(302)
    img = Image.new("RGBA", (W, H), (192, 194, 190, 255))
    d = ImageDraw.Draw(img)
    for k in range(0, H, S):                        # brushing along x
        c = 186 + rnd.randint(-6, 8)
        d.line([(0, k), (W, k)], fill=(c, c + 2, c, 255), width=1)

    def px(x, y):
        return ((x + L.REC_W / 2) / L.REC_W * W, (y1 - y) / (y1 - y0) * H)
    cosk = (y1 - y0) / math.hypot(y1 - y0, z1 - z0)
    ys = y0 + 0.030 * cosk                          # knob axis - 30 mm up the slope
    ink = (30, 30, 32, 255)
    fnt = font(int(S * 0.0042 * PX_REC))
    for xk in L.KNOBS:
        cx, cy = px(xk, ys)
        for i in range(13):
            a = math.radians(-225 + 270 * i / 12)
            r0, r1 = 0.0112 * PX_REC * S, (0.0128 if i % 2 == 0 else 0.0121) * PX_REC * S
            d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a) * cosk),
                    (cx + r1 * math.cos(a), cy + r1 * math.sin(a) * cosk)], fill=ink, width=S * 2)
        for i, num in ((0, "2"), (6, "8"), (12, "14")):
            a = math.radians(-225 + 270 * i / 12)
            r = 0.0150 * PX_REC * S
            d.text((cx + r * math.cos(a), cy + r * math.sin(a) * cosk), num, fill=ink, font=fnt, anchor="mm")
    # dark field under the indicator and keys
    vx, vw, vh = L.VU
    a, b = px(vx - vw / 2 - 0.003, ys + 0.010), px(vx + vw / 2 + 0.003, ys - 0.010)
    d.rectangle([a[0], a[1], b[0], b[1]], fill=(40, 40, 42, 255))
    kx0, kx1, n = L.KEYS_REC
    a, b = px(kx0 - 0.004, y1), px(kx1 + 0.004, y0)
    d.rectangle([a[0], a[1] + H * 0.18, b[0], b[1]], fill=(26, 26, 28, 255))
    # key symbols above them (at the back edge of the strip)
    kw = (kx1 - kx0) / n
    for k in range(n):
        cx, cy = px(kx0 + kw * (k + 0.5), y1 - 0.0045 * cosk)
        r = 0.0022 * PX_REC * S
        if k == 0:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(190, 30, 26, 255))
        elif k in (1, 2):
            sgn = -1 if k == 1 else 1
            for off in (-0.55, 0.55):
                ox = cx + off * r * 1.2
                d.polygon([(ox + sgn * r, cy), (ox - sgn * r, cy - r * 0.8), (ox - sgn * r, cy + r * 0.8)], fill=ink)
        elif k == 3:
            d.polygon([(cx + r, cy), (cx - r * 0.8, cy - r), (cx - r * 0.8, cy + r)], fill=ink)
        elif k == 4:
            d.rectangle([cx - r * 0.8, cy - r * 0.8, cx + r * 0.8, cy + r * 0.8], fill=ink)
        else:
            d.polygon([(cx, cy - r), (cx - r, cy + r * 0.2), (cx + r, cy + r * 0.2)], fill=ink)
            d.rectangle([cx - r, cy + r * 0.5, cx + r, cy + r * 0.9], fill=ink)
    # edge at the face and finger wear at the knobs
    d.rectangle([0, H - S * 3, W, H], fill=(70, 70, 72, 255))
    img = aged_metal(img, rnd)
    save(img, (W // S, H // S), "decal_rec_strip.png")


def aged_metal(img, rnd):
    """Wear and dirt in the corners of the aluminium strip."""
    W, H = img.size
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for _ in range(18):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.02, 0.08) * H
        d.ellipse([x - r * 3, y - r, x + r * 3, y + r], fill=(60, 54, 44, rnd.randint(18, 40)))
    return Image.alpha_composite(img, ov.filter(ImageFilter.GaussianBlur(S * 4)))


def make_vu():
    """Scale of the needle "recording monitor" indicator: an arc of divisions from stop to stop (needle swing
    80 degrees, axis at the bottom centre), green field on the left, red on the right."""
    vx, vw, vh = L.VU
    W, H = int(vw * PX_REC * 2 * S), int(vh * PX_REC * 2 * S)
    img = Image.new("RGBA", (W, H), (232, 226, 200, 255))
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, H * 1.02
    R0, R1 = H * 0.70, H * 0.86
    for a0, a1, col in ((-40, 12, (60, 150, 70, 255)), (12, 40, (200, 40, 32, 255))):
        for k in range(24):
            t0 = math.radians(a0 + (a1 - a0) * k / 24 - 90)
            t1 = math.radians(a0 + (a1 - a0) * (k + 1) / 24 - 90)
            d.polygon([(cx + R0 * math.cos(t0), cy + R0 * math.sin(t0)), (cx + R1 * math.cos(t0), cy + R1 * math.sin(t0)),
                       (cx + R1 * math.cos(t1), cy + R1 * math.sin(t1)), (cx + R0 * math.cos(t1), cy + R0 * math.sin(t1))],
                      fill=col)
    for i in range(11):
        t = math.radians(-40 + 8 * i - 90)
        r1 = R1 + H * (0.10 if i % 5 == 0 else 0.05)
        d.line([(cx + R1 * math.cos(t), cy + R1 * math.sin(t)), (cx + r1 * math.cos(t), cy + r1 * math.sin(t))],
               fill=(30, 30, 30, 255), width=S * 2)
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 40, 40, 255), width=S * 2)
    save(img, (W // S, H // S), "decal_vu.png")


def make_cass_label():
    """Cassette from above (100.4 x 63.8): grey body along the edge, a cream label with a coloured stripe and
    hand scribbles, a window cutout in the middle (the window is a separate part there), five screws. No letters."""
    cx, cy, cw, ch, ct = L.CASS
    W, H = int(cw * PX_REC * S), int(ch * PX_REC * S)
    rnd = random.Random(60)
    img = Image.new("RGBA", (W, H), (56, 56, 60, 255))
    d = ImageDraw.Draw(img)
    m = W * 0.05
    d.rectangle([m, H * 0.08, W - m, H * 0.80], fill=(226, 220, 196, 255))
    d.rectangle([m, H * 0.56, W - m, H * 0.66], fill=(196, 96, 40, 255))
    # window cutout and rings around the reels
    d.rectangle([W * 0.19, H * 0.34, W * 0.81, H * 0.66], fill=(30, 30, 32, 255))
    for sx in (0.288, 0.712):
        r = 0.0125 * PX_REC * S
        d.ellipse([W * sx - r, H * 0.50 - r, W * sx + r, H * 0.50 + r], outline=(150, 146, 130, 255), width=S * 2)
    y = H * 0.14
    while y < H * 0.30:
        scribble(d, W * 0.10, y, W * rnd.uniform(0.6, 0.9), H * 0.045, rnd, (30, 40, 90, 255), S * 2)
        y += H * 0.075
    for x, yy in ((0.03, 0.05), (0.97, 0.05), (0.03, 0.95), (0.97, 0.95), (0.5, 0.93)):
        r = S * 6
        d.ellipse([W * x - r, H * yy - r, W * x + r, H * yy + r], fill=(24, 24, 26, 255))
    img = aged(img, rnd, 1)
    save(img, (W // S, H // S), "decal_cass_label.png")


# =============================================================================
# Traces on the boards at the empty places of modules 1 and 3: a clean spot with a dusty rim
# =============================================================================
def make_traces():
    for i in (0, 2):
        (x0, y0), (x1, y1) = L.MOD_BOX[i]
        w, h = x1 - x0 + 0.03, y1 - y0 + 0.03
        W, H = int(w * 1000 * S), int(h * 1000 * S)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        m = 0.015 * 1000 * S
        d.rectangle([m - S * 5, m - S * 5, W - m + S * 5, H - m + S * 5], outline=(184, 174, 148, 215), width=S * 8)
        d.rectangle([m, m, W - m, H - m], fill=(44, 33, 22, 170))
        img = img.filter(ImageFilter.GaussianBlur(S * 2))
        save(img, (W // S, H // S), "decal_trace%d.png" % (i + 1))


if __name__ == "__main__":
    make_map()
    make_papers()
    make_pager()
    make_rec_strip()
    make_vu()
    make_cass_label()
    make_traces()
