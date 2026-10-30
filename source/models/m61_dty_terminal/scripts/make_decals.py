"""Decals for the M61 command desk (system Python + Pillow, no numpy): the map under the glass, the
printed cover of the "Delo" case-file folder (empty fields only) and the spread of the open folder.
Where things go: layout.py.

The map is original and procedural, not taken from any game (copying the trilogy's map art is not
allowed). Style: a Soviet topographic map with working marks: khaki-beige paper, brown contour lines
over random relief, a blue river with a tributary, a lake and a hatched marsh, green forest patches,
a railway (black-and-white strip) with a station and a settlement, roads, a kilometre grid with
numbers in the margins. On top, red and blue pencil: a front line with teeth, arrows, district ovals,
circles, hatching. Captions are unreadable squiggles, no letters are drawn; grid digits are allowed
(scales and digits are fine). Folds, stains, a glass ring.

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 2                                   # supersampling, then downscale: smooth edges


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, size)


def smooth_noise(rnd, W, H, cells, mode=Image.BICUBIC):
    """Smooth noise 0..255: a random grid of cells columns (rows by aspect ratio) stretched to W x H."""
    cw = max(2, cells)
    ch = max(2, int(round(cells * H / W)))
    small = Image.frombytes("L", (cw, ch), bytes(rnd.randrange(256) for _ in range(cw * ch)))
    return small.resize((W, H), mode)


def fbm(rnd, W, H, octaves=((5, 0.5), (11, 0.25), (23, 0.15), (47, 0.1))):
    """Sum of noise octaves, stretched to 0..255."""
    acc, wsum = None, 0.0
    for cells, w in octaves:
        n = smooth_noise(rnd, W, H, cells)
        if acc is None:
            acc, wsum = n, w
        else:
            wsum += w
            acc = Image.blend(acc, n, w / wsum)
    return ImageOps.autocontrast(acc, cutoff=1)


def layer(W, H, col):
    """Empty colour layer and its drawing mask."""
    m = Image.new("L", (W, H), 0)
    return col, m, ImageDraw.Draw(m)


def put(img, col, mask, k=1.0):
    """Blend colour col in through the mask (0..255) with strength k."""
    if k != 1.0:
        mask = mask.point(lambda v: int(v * k))
    lay = Image.new("RGBA", img.size, col + (0,))
    lay.putalpha(mask)
    return Image.alpha_composite(img, lay)


def curve(rnd, pts, n=24, wob=0.0):
    """Smoothed polyline (Catmull-Rom) through pts, with a slight jitter."""
    out = []
    p = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * (2 * p1[0] + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * (2 * p1[1] + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x + rnd.uniform(-wob, wob), y + rnd.uniform(-wob, wob)))
    out.append(pts[-1])
    return out


def scribble(d, rnd, x, y, h, length, fill=255, slant=0.25):
    """Unreadable caption: a row of cursive-like squiggles of height h, no letters."""
    cx = x
    while cx < x + length:
        w = rnd.uniform(0.35, 0.8) * h
        pts = []
        for k in range(rnd.randint(3, 6)):
            px = cx + w * k / 5.0
            py = y - rnd.uniform(0.0, 1.0) * h * (1.0 if k % 2 else 0.4)
            pts.append((px + (y - py) * slant, py))
        d.line(pts, fill=fill, width=max(1, int(h / 7)), joint="curve")
        cx += w + (rnd.uniform(0.5, 1.2) * h if rnd.random() < 0.2 else rnd.uniform(0.05, 0.2) * h)


def pencil(mask, rnd, grain=0.55):
    """Pencil: a stroke with paper grain, i.e. the mask multiplied by noise."""
    W, H = mask.size
    g = Image.effect_noise((W, H), 90).point(lambda v: int(255 * (1 - grain) + v * grain))
    g = g.filter(ImageFilter.GaussianBlur(0.6 * S))
    return ImageChops.multiply(mask.filter(ImageFilter.GaussianBlur(0.7 * S)), g)


def arrow(d, pts, w, head):
    """Tactical arrow: a shaft along a polyline and a triangular head."""
    d.line(pts, fill=255, width=int(w), joint="curve")
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    a = math.atan2(y1 - y0, x1 - x0)
    tip = (x1 + math.cos(a) * head * 0.9, y1 + math.sin(a) * head * 0.9)
    l = (x1 + math.cos(a + 2.4) * head * 0.6, y1 + math.sin(a + 2.4) * head * 0.6)
    r = (x1 + math.cos(a - 2.4) * head * 0.6, y1 + math.sin(a - 2.4) * head * 0.6)
    d.polygon([tip, l, r], fill=255)


# =============================================================================
# Map
# =============================================================================
def make_map():
    mw, mh = L.MAP_S
    PXM = 2000 * S
    W, H = int(mw * PXM), int(mh * PXM)
    rnd = random.Random(61)
    M = int(0.022 * PXM)                       # margin before the frame
    ix0, iy0, ix1, iy1 = M, M, W - M, H - M    # sheet frame

    # --- paper: khaki-beige with tonal blotches ---
    paper = Image.new("RGBA", (W, H), (208, 196, 156, 255))
    tone = fbm(rnd, W, H, ((4, 0.6), (13, 0.4)))
    paper = Image.composite(Image.new("RGBA", (W, H), (190, 172, 124, 255)), paper,
                            tone.point(lambda v: max(0, v - 120) * 2))
    img = paper

    inside = Image.new("L", (W, H), 0)
    ImageDraw.Draw(inside).rectangle((ix0, iy0, ix1, iy1), fill=255)

    # --- relief ---
    hgt = fbm(rnd, W, H, ((4, 0.55), (9, 0.3), (19, 0.15))).filter(ImageFilter.GaussianBlur(3 * S))
    # river valley: the relief is lower along the river curve
    river = curve(rnd, [(ix0 - 50, H * 0.62), (W * 0.18, H * 0.55), (W * 0.33, H * 0.66), (W * 0.47, H * 0.58),
                        (W * 0.62, H * 0.70), (W * 0.78, H * 0.62), (ix1 + 50, H * 0.67)], n=40)
    valley = Image.new("L", (W, H), 0)
    ImageDraw.Draw(valley).line(river, fill=255, width=int(0.10 * PXM))
    valley = valley.filter(ImageFilter.GaussianBlur(0.05 * PXM))
    hgt = ImageChops.subtract(hgt, valley.point(lambda v: v // 2))

    # --- forest: green patches with a dark edge ---
    forest_n = fbm(rnd, W, H, ((6, 0.6), (17, 0.3), (60, 0.1)))
    forest = forest_n.point(lambda v: 255 if v > 150 else 0)
    forest = ImageChops.multiply(forest, inside)
    img = put(img, (150, 176, 104), forest, 0.62)
    edge = forest.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))
    img = put(img, (74, 104, 52), edge, 0.55)

    # --- marsh: lowlands by the river, light-blue fill and short blue dashes ---
    swamp = ImageChops.multiply(valley.point(lambda v: 255 if v > 150 else 0),
                                hgt.point(lambda v: 255 if v < 95 else 0))
    swamp = ImageChops.multiply(swamp.filter(ImageFilter.MaxFilter(9)), inside)
    img = put(img, (150, 186, 196), swamp, 0.55)
    hatch = Image.new("L", (W, H), 0)
    hd = ImageDraw.Draw(hatch)
    step = int(0.006 * PXM)
    for y in range(iy0, iy1, step):
        x = ix0 + rnd.randint(0, step * 2)
        while x < ix1:
            ln = rnd.randint(int(0.004 * PXM), int(0.009 * PXM))
            hd.line((x, y, x + ln, y), fill=255, width=max(2, S + 1))
            x += ln + rnd.randint(int(0.003 * PXM), int(0.008 * PXM))
    img = put(img, (40, 92, 160), ImageChops.multiply(hatch, swamp), 0.85)

    # --- contour lines: brown, every fifth one thicker ---
    band = 14
    q = hgt.point(lambda v: (v // band) * band)
    lines = q.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 0 else 0)
    q5 = hgt.point(lambda v: (v // (band * 5)) * band * 5)
    lines5 = q5.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 0 else 0).filter(ImageFilter.MaxFilter(5))
    lines = ImageChops.lighter(lines.filter(ImageFilter.GaussianBlur(0.5 * S)).point(lambda v: min(255, v * 3)), lines5)
    lines = ImageChops.multiply(lines, ImageChops.invert(swamp.point(lambda v: v // 2)))
    img = put(img, (150, 90, 46), ImageChops.multiply(lines, inside), 0.7)

    # --- water: river, tributary, lake ---
    _, wm, wd = layer(W, H, None)
    for i in range(len(river) - 1):
        w = int((0.0035 + 0.004 * i / len(river)) * PXM)
        wd.line((river[i], river[i + 1]), fill=255, width=w)
    trib = curve(rnd, [(W * 0.36, iy0 - 20), (W * 0.39, H * 0.2), (W * 0.35, H * 0.38), (W * 0.40, H * 0.52),
                       (W * 0.42, H * 0.60)], n=30)
    wd.line(trib, fill=255, width=int(0.0022 * PXM), joint="curve")
    trib2 = curve(rnd, [(W * 0.70, iy1 + 20), (W * 0.68, H * 0.84), (W * 0.715, H * 0.74), (W * 0.70, H * 0.66)], n=30)
    wd.line(trib2, fill=255, width=int(0.0018 * PXM), joint="curve")
    lx, ly = W * 0.20, H * 0.74
    wd.ellipse((lx - 0.035 * PXM, ly - 0.02 * PXM, lx + 0.045 * PXM, ly + 0.022 * PXM), fill=255)
    wm = ImageChops.multiply(wm, inside)
    img = put(img, (120, 168, 206), wm, 0.9)
    img = put(img, (36, 84, 160), wm.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3)), 0.9)

    # --- roads: highway (orange with a black outline), dirt tracks dashed ---
    road = curve(rnd, [(ix0 - 30, H * 0.30), (W * 0.25, H * 0.34), (W * 0.52, H * 0.30), (W * 0.60, H * 0.46),
                       (W * 0.66, H * 0.80), (W * 0.70, iy1 + 30)], n=30)
    _, rm, rd = layer(W, H, None)
    rd.line(road, fill=255, width=int(0.0045 * PXM), joint="curve")
    rm = ImageChops.multiply(rm, inside)
    img = put(img, (30, 26, 22), rm.filter(ImageFilter.MaxFilter(5)), 0.9)
    img = put(img, (214, 128, 52), rm, 1.0)
    _, gm, gd = layer(W, H, None)
    for pts in ([(W * 0.52, H * 0.30), (W * 0.48, H * 0.12), (W * 0.55, iy0)],
                [(W * 0.25, H * 0.34), (W * 0.15, H * 0.48), (W * 0.10, H * 0.85), (W * 0.14, iy1)],
                [(W * 0.60, H * 0.46), (W * 0.80, H * 0.40), (W * 0.92, H * 0.28), (ix1, H * 0.24)]):
        c = curve(rnd, pts, n=30)
        for i in range(0, len(c) - 1, 2):
            if (i // 2) % 3 != 2:
                gd.line((c[i], c[i + 1]), fill=255, width=max(3, int(0.0012 * PXM)))
    img = put(img, (40, 34, 28), ImageChops.multiply(gm, inside), 0.85)

    # --- railway: black strip with white checks, station and settlement ---
    rail = curve(rnd, [(ix0 - 30, H * 0.14), (W * 0.30, H * 0.20), (W * 0.58, H * 0.38), (W * 0.84, H * 0.45),
                       (ix1 + 30, H * 0.50)], n=40)
    _, km, kd = layer(W, H, None)
    kd.line(rail, fill=255, width=int(0.0030 * PXM), joint="curve")
    img = put(img, (24, 22, 20), ImageChops.multiply(km, inside), 1.0)
    _, cm, cd = layer(W, H, None)
    acc = 0.0
    seg = 0.010 * PXM
    for i in range(len(rail) - 1):
        (xa, ya), (xb, yb) = rail[i], rail[i + 1]
        dl = math.hypot(xb - xa, yb - ya)
        if int(acc // seg) % 2 == 0:
            cd.line((xa, ya, xb, yb), fill=255, width=int(0.0014 * PXM))
        acc += dl
    img = put(img, (226, 220, 200), ImageChops.multiply(cm, inside), 1.0)
    # settlement by the station: blocks as black outlines with orange fill, along the highway and the railway
    sx, sy = W * 0.58, H * 0.38
    _, bm, bd = layer(W, H, None)
    _, bf, bfd = layer(W, H, None)
    for k in range(34):
        bx = sx + rnd.gauss(0, 0.045 * PXM)
        by = sy + rnd.gauss(0, 0.028 * PXM) + 0.02 * PXM
        bw, bh = rnd.uniform(0.006, 0.016) * PXM, rnd.uniform(0.004, 0.009) * PXM
        bd.rectangle((bx, by, bx + bw, by + bh), outline=255, width=max(2, S))
        bfd.rectangle((bx, by, bx + bw, by + bh), fill=255)
    img = put(img, (212, 150, 90), bf, 0.75)
    img = put(img, (28, 24, 20), bm, 0.9)
    # station building and the platform along the tracks
    plat = Image.new("L", (W, H), 0)
    ImageDraw.Draw(plat).rectangle((sx - 0.02 * PXM, sy - 0.012 * PXM, sx + 0.012 * PXM, sy - 0.006 * PXM), fill=255)
    img = put(img, (20, 18, 16), plat.rotate(-math.degrees(math.atan2(0.07, 0.26)), center=(sx, sy)), 1.0)
    # farmsteads: single black squares
    _, hm, hdr = layer(W, H, None)
    for k in range(26):
        hx, hy = rnd.uniform(ix0 + 40, ix1 - 40), rnd.uniform(iy0 + 40, iy1 - 40)
        r = rnd.uniform(0.0015, 0.003) * PXM
        hdr.rectangle((hx - r, hy - r, hx + r, hy + r), fill=255)
    img = put(img, (26, 22, 18), hm, 0.9)

    # --- kilometre grid: thin black lines, numbers in the margins ---
    gs = 0.05 * PXM
    _, sm, sd = layer(W, H, None)
    font = ImageFont.load_default(size=int(0.0085 * PXM))
    k0 = rnd.randint(10, 60)
    x = ix0 + gs * 0.37
    i = 0
    while x < ix1:
        sd.line((x, iy0, x, iy1), fill=255, width=max(2, S))
        for yy in (iy0 - 0.012 * PXM, iy1 + 0.003 * PXM):
            sd.text((x - 0.005 * PXM, yy), "%02d" % ((k0 + i) % 100), fill=255, font=font)
        x += gs
        i += 1
    y = iy0 + gs * 0.61
    j = 0
    k1 = rnd.randint(10, 60)
    while y < iy1:
        sd.line((ix0, y, ix1, y), fill=255, width=max(2, S))
        for xx in (ix0 - 0.017 * PXM, ix1 + 0.003 * PXM):
            sd.text((xx, y - 0.005 * PXM), "%02d" % ((k1 + 40 - j) % 100), fill=255, font=font)
        y += gs
        j += 1
    img = put(img, (34, 30, 26), sm, 0.7)
    # sheet frame: thin and thick
    fr = Image.new("L", (W, H), 0)
    fd = ImageDraw.Draw(fr)
    fd.rectangle((ix0, iy0, ix1, iy1), outline=255, width=max(2, S))
    fd.rectangle((ix0 - 0.004 * PXM, iy0 - 0.004 * PXM, ix1 + 0.004 * PXM, iy1 + 0.004 * PXM), outline=255,
                 width=int(0.0016 * PXM))
    img = put(img, (24, 22, 20), fr, 0.95)

    # --- unreadable captions: by the settlement, blue by the river, by the forest, title in the top margin ---
    _, tm, td = layer(W, H, None)
    _, tb, tbd = layer(W, H, None)
    for k in range(30):
        tx, ty = rnd.uniform(ix0 + 60, ix1 - 300), rnd.uniform(iy0 + 60, iy1 - 30)
        scribble(td, rnd, tx, ty, rnd.uniform(0.0035, 0.006) * PXM, rnd.uniform(0.02, 0.05) * PXM)
    scribble(td, rnd, sx + 0.03 * PXM, sy - 0.03 * PXM, 0.009 * PXM, 0.07 * PXM, slant=0.0)
    for k in range(5):
        i0 = rnd.randrange(len(river) // 6, len(river) * 5 // 6)
        rx, ry = river[i0]
        scribble(tbd, rnd, rx, ry - 0.008 * PXM, 0.005 * PXM, 0.035 * PXM, slant=0.4)
    img = put(img, (30, 26, 22), tm, 0.85)
    img = put(img, (36, 80, 150), tb, 0.85)

    # --- pencil: front line, arrows, districts, circles, hatching ---
    red, blue = (178, 40, 34), (40, 66, 150)
    _, pr, prd = layer(W, H, None)
    front = curve(rnd, [(W * 0.08, H * 0.42), (W * 0.22, H * 0.48), (W * 0.36, H * 0.43), (W * 0.48, H * 0.50),
                        (W * 0.60, H * 0.56), (W * 0.74, H * 0.52), (W * 0.90, H * 0.58)], n=30, wob=1.5 * S)
    prd.line(front, fill=255, width=int(0.0028 * PXM), joint="curve")
    for i in range(3, len(front) - 3, 7):                     # teeth point at the enemy (down the sheet)
        (xa, ya), (xb, yb) = front[i - 1], front[i + 1]
        a = math.atan2(yb - ya, xb - xa) + math.pi / 2
        x0, y0 = front[i]
        prd.line((x0, y0, x0 + math.cos(a) * 0.009 * PXM, y0 + math.sin(a) * 0.009 * PXM), fill=255,
                 width=int(0.0022 * PXM))
    arrow(prd, curve(rnd, [(W * 0.30, H * 0.30), (W * 0.36, H * 0.38), (W * 0.40, H * 0.47)], n=12),
          0.004 * PXM, 0.018 * PXM)
    arrow(prd, curve(rnd, [(W * 0.66, H * 0.26), (W * 0.67, H * 0.38), (W * 0.62, H * 0.52)], n=12),
          0.004 * PXM, 0.018 * PXM)
    for cx, cy, r in ((W * 0.44, H * 0.36, 0.012), (W * 0.20, H * 0.35, 0.010), (W * 0.78, H * 0.44, 0.011)):
        prd.ellipse((cx - r * PXM, cy - r * PXM, cx + r * PXM, cy + r * PXM), outline=255, width=int(0.0022 * PXM))
    # district hatched in red
    poly = [(W * 0.50, H * 0.18), (W * 0.60, H * 0.14), (W * 0.64, H * 0.24), (W * 0.54, H * 0.28)]
    prd.line(poly + [poly[0]], fill=255, width=int(0.0022 * PXM), joint="curve")
    hz = Image.new("L", (W, H), 0)
    ImageDraw.Draw(hz).polygon(poly, fill=255)
    hl = Image.new("L", (W, H), 0)
    hld = ImageDraw.Draw(hl)
    for k in range(-H, W, int(0.006 * PXM)):
        hld.line((k, H, k + H, 0), fill=150, width=max(2, S))
    pr = ImageChops.lighter(pr, ImageChops.multiply(hl, hz))
    # unit numbers in pencil (digits are allowed)
    fnt = ImageFont.load_default(size=int(0.014 * PXM))
    for tx, ty, s_ in ((W * 0.26, H * 0.38, "35"), (W * 0.55, H * 0.43, "71"), (W * 0.82, H * 0.50, "12")):
        prd.text((tx, ty), s_, fill=255, font=fnt)
    img = put(img, red, ImageChops.multiply(pencil(pr, rnd), inside), 0.9)

    _, pb, pbd = layer(W, H, None)
    for cx, cy, rx, ry in ((W * 0.40, H * 0.75, 0.07, 0.035), (W * 0.76, H * 0.78, 0.06, 0.03)):
        pbd.ellipse((cx - rx * PXM, cy - ry * PXM, cx + rx * PXM, cy + ry * PXM), outline=255,
                    width=int(0.0026 * PXM))
    arrow(pbd, curve(rnd, [(W * 0.46, H * 0.86), (W * 0.50, H * 0.74), (W * 0.47, H * 0.63)], n=12),
          0.0035 * PXM, 0.016 * PXM)
    blue_front = curve(rnd, [(W * 0.10, H * 0.66), (W * 0.30, H * 0.64), (W * 0.52, H * 0.71), (W * 0.86, H * 0.68)],
                       n=30, wob=1.5 * S)
    for i in range(0, len(blue_front) - 1, 2):                # dashed line
        if (i // 2) % 3 != 2:
            pbd.line((blue_front[i], blue_front[i + 1]), fill=255, width=int(0.0024 * PXM))
    img = put(img, blue, ImageChops.multiply(pencil(pb, rnd), inside), 0.85)

    # --- ageing: folds, stains, a glass ring, rubbed edges ---
    folds = Image.new("L", (W, H), 0)
    fdd = ImageDraw.Draw(folds)
    for fx in (W / 4, W / 2, 3 * W / 4):
        fdd.line((fx, 0, fx, H), fill=255, width=int(0.0016 * PXM))
    fdd.line((0, H / 2, W, H / 2), fill=255, width=int(0.0016 * PXM))
    folds = folds.filter(ImageFilter.GaussianBlur(1.5 * S))
    img = put(img, (236, 228, 200), folds, 0.55)
    sh = ImageChops.offset(folds, 2 * S, 2 * S)
    img = put(img, (120, 104, 72), sh, 0.25)
    stains = fbm(rnd, W, H, ((7, 0.5), (19, 0.5))).point(lambda v: max(0, v - 175) * 3)
    img = put(img, (150, 118, 66), stains.filter(ImageFilter.GaussianBlur(4 * S)), 0.35)
    ring = Image.new("L", (W, H), 0)
    rx, ry, rr = W * 0.84, H * 0.22, 0.034 * PXM
    ImageDraw.Draw(ring).ellipse((rx - rr, ry - rr, rx + rr, ry + rr), outline=255, width=int(0.0022 * PXM))
    ring = ImageChops.multiply(ring.filter(ImageFilter.GaussianBlur(1.2 * S)), fbm(rnd, W, H, ((30, 1.0),)))
    img = put(img, (130, 84, 40), ring, 0.6)
    edge = Image.new("L", (W, H), 255)
    ImageDraw.Draw(edge).rectangle((int(0.01 * PXM), int(0.01 * PXM), W - int(0.01 * PXM), H - int(0.01 * PXM)),
                                   fill=0)
    edge = edge.filter(ImageFilter.GaussianBlur(0.012 * PXM))
    img = put(img, (150, 126, 80), edge, 0.8)
    save(img.convert("RGB"), (W // S, H // S), "decal_map.png")


# =============================================================================
# "Delo" folders
# =============================================================================
INK = (52, 44, 36)


def make_folder():
    """Folder cover (printed by a print shop): a double cartouche frame at the top, a number field without
    "Delo No." (a short segment and a long line), empty lines below, "started / finished" fields at the
    bottom, also wordless, lines only. Scuffs and stains."""
    k = 3000 * S
    W, H = int(L.FOLDER_W * k), int(L.FOLDER_D * k)
    rnd = random.Random(12)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    lw = max(2, int(0.0006 * k))
    d.rectangle((0.03 * k, 0.03 * k, W - 0.03 * k, 0.075 * k), outline=255, width=lw)
    d.rectangle((0.033 * k, 0.033 * k, W - 0.033 * k, 0.072 * k), outline=255, width=max(1, lw // 2))
    y = 0.115 * k
    d.line((0.10 * k, y, 0.13 * k, y), fill=255, width=lw)          # number field: a short segment
    d.line((0.14 * k, y, W - 0.04 * k, y), fill=255, width=lw)
    for i in range(5):
        y = 0.15 * k + i * 0.022 * k
        d.line((0.04 * k, y, W - 0.04 * k, y), fill=255, width=lw)
    for i, yy in enumerate((0.285, 0.30)):
        d.line((0.12 * k, yy * k, W - 0.04 * k, yy * k), fill=255, width=lw)
    # scuffs in the print
    wear = Image.new("L", (W, H), 255)
    wd = ImageDraw.Draw(wear)
    for _ in range(90):
        x, yv, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1, 6) * S
        wd.ellipse((x - r, yv - r, x + r, yv + r), fill=rnd.randint(40, 160))
    alpha = ImageChops.multiply(m.filter(ImageFilter.GaussianBlur(0.6 * S)), wear)
    img = Image.new("RGBA", (W, H), INK + (0,))
    img.putalpha(alpha.point(lambda v: v * 220 // 255))
    # stains and rubbed corners in brown
    st = fbm(rnd, W, H, ((5, 0.6), (13, 0.4))).point(lambda v: max(0, v - 170) * 2)
    img = put(img, (140, 112, 70), st.filter(ImageFilter.GaussianBlur(3 * S)), 0.5)
    save(img, (W // S, H // S), "decal_folder.png")


def make_open():
    """Spread of the open folder: on the left the inside of the cover with a printed inventory table (no
    words), on the right the top sheet: typescript as unreadable lines, red pencil, a round blue stamp
    without text (rings and strokes)."""
    k = 3000 * S
    W, H = int(L.OPEN_S[0] * k), int(L.OPEN_S[1] * k)
    hw = W // 2
    rnd = random.Random(31)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # left: the inventory, a grid
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    lw = max(2, int(0.0005 * k))
    x0, x1, y0, y1 = 0.02 * k, hw - 0.02 * k, 0.05 * k, H - 0.03 * k
    d.rectangle((x0, y0, x1, y1), outline=255, width=lw)
    for xx in (0.035, 0.15, 0.185):
        d.line((x0 + xx * k, y0, x0 + xx * k, y1), fill=255, width=lw)
    yy = y0 + 0.02 * k
    while yy < y1:
        d.line((x0, yy, x1, yy), fill=255, width=lw)
        yy += 0.012 * k
    img = put(img, INK, m.filter(ImageFilter.GaussianBlur(0.5 * S)), 0.75)
    # a few handwritten lines in blue ink in the inventory
    _, hm, hdr = layer(W, H, None)
    yy = y0 + 0.02 * k + 0.009 * k
    for i in range(9):
        scribble(hdr, rnd, x0 + 0.04 * k, yy, 0.006 * k, rnd.uniform(0.05, 0.10) * k)
        scribble(hdr, rnd, x0 + 0.155 * k, yy, 0.006 * k, 0.02 * k)
        yy += 0.012 * k
    img = put(img, (40, 54, 120), hm.filter(ImageFilter.GaussianBlur(0.4 * S)), 0.75)
    # right: typescript, even lines of short word-like bars
    _, tm, tdr = layer(W, H, None)
    yy = 0.05 * k
    while yy < H - 0.04 * k:
        x = hw + 0.03 * k + (0.02 * k if rnd.random() < 0.12 else 0)
        end = W - 0.025 * k - (rnd.uniform(0, 0.08) * k if rnd.random() < 0.15 else 0)
        while x < end:
            wl = rnd.uniform(0.004, 0.016) * k
            for c in range(int(wl / (0.0021 * k))):
                cx = x + c * 0.0021 * k
                ch = rnd.uniform(0.0016, 0.0026) * k
                tdr.rectangle((cx, yy - ch, cx + 0.0013 * k, yy), fill=rnd.randint(150, 255))
            x += wl + 0.0021 * k
        yy += 0.0075 * k if rnd.random() > 0.08 else 0.015 * k
    img = put(img, (40, 38, 36), tm.filter(ImageFilter.GaussianBlur(0.5 * S)), 0.8)
    # red pencil: underlines and a tick in the margin
    _, rm, rdr = layer(W, H, None)
    for yv in (0.11, 0.18, 0.235):
        rdr.line((hw + 0.04 * k, yv * k + 0.002 * k, hw + rnd.uniform(0.12, 0.2) * k, yv * k + 0.003 * k), fill=255,
                 width=int(0.0012 * k))
    rdr.line((hw + 0.012 * k, 0.15 * k, hw + 0.018 * k, 0.158 * k, hw + 0.03 * k, 0.138 * k), fill=255,
             width=int(0.0012 * k))
    img = put(img, (176, 40, 34), pencil(rm, rnd), 0.9)
    # blue stamp: two rings and strokes between them instead of text
    _, sm, sdr = layer(W, H, None)
    cx, cy, r = hw + 0.17 * k, H - 0.07 * k, 0.02 * k
    sdr.ellipse((cx - r, cy - r, cx + r, cy + r), outline=255, width=int(0.0009 * k))
    sdr.ellipse((cx - r * 0.72, cy - r * 0.72, cx + r * 0.72, cy + r * 0.72), outline=255, width=int(0.0007 * k))
    for a in range(0, 360, 9):
        ra = math.radians(a)
        sdr.line((cx + math.cos(ra) * r * 0.78, cy + math.sin(ra) * r * 0.78, cx + math.cos(ra) * r * 0.92,
                  cy + math.sin(ra) * r * 0.92), fill=255, width=max(2, int(0.0006 * k)))
    sdr.regular_polygon((cx, cy, r * 0.32), 5, fill=255)
    stamp = ImageChops.multiply(sm.filter(ImageFilter.GaussianBlur(0.8 * S)),
                                fbm(rnd, W, H, ((40, 0.6), (90, 0.4))).point(lambda v: min(255, v + 60)))
    img = put(img, (52, 70, 160), stamp.rotate(-12, center=(cx, cy)), 0.8)
    save(img, (W // S, H // S), "decal_open.png")


if __name__ == "__main__":
    make_map()
    make_folder()
    make_open()
