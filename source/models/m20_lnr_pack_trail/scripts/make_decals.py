"""Decals for the M20 map cabinet (system Python + Pillow): a terrain map on the side (own, invented:
forest, swamp, river, roads, a power line, contour lines, a kilometre grid with digits at the edge, no
names; a pencil route, marker marks, pin traces and folds), the crack of the right side (coming out from
under the plywood patch) and an inventory tag with a punched number. No letters: only digits and
symbols.

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
PX_M = 2000                             # pixels per metre for the map
MARKER = (186, 30, 26)
PENCIL = (70, 70, 76)


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
        o = wobble * (math.sin(t * 6.0 + ph1) * 0.6 + math.sin(t * 11.0 + ph2) * 0.3) * math.sin(math.pi * t) ** 0.3
        pts.append((x0 + dx * t + nx * o, y0 + dy * t + ny * o))
    return pts


def make_map():
    """Topographic map sheet 340 x 480 mm, hanging in portrait. The picture differs from the M15 map (a sheet
    on the spotter's table panel): half the map is swamp, a river with a tributary, a power line, a pencil route."""
    y0, y1, z0, z1 = L.MAP
    wm, hm = y1 - y0, z1 - z0
    W, H = int(wm * PX_M * S), int(hm * PX_M * S)
    rnd = random.Random(20)
    img = Image.new("RGB", (W, H), (232, 228, 206))
    d = ImageDraw.Draw(img)
    # forest by the mask
    forest = noise_field(W, H, rnd, 70, W * 0.06, W * 0.22, W * 0.035).point(lambda v: 255 if v > 50 else 0)
    img.paste((172, 202, 150), mask=forest)
    # swamp: blue hatching over the lower part
    marsh = noise_field(W, H, rnd, 26, W * 0.10, W * 0.24, W * 0.05).point(lambda v: 255 if v > 40 else 0)
    band = Image.new("L", (W, H), 0)
    ImageDraw.Draw(band).rectangle([0, int(H * 0.55), W, H], fill=255)
    marsh = Image.composite(marsh, Image.new("L", (W, H), 0), band)
    hatch = Image.new("L", (W, H), 0)
    hd = ImageDraw.Draw(hatch)
    for yy in range(0, H, S * 9):
        for xx in range(rnd.randint(0, S * 12), W, S * 26):
            hd.line([(xx, yy), (xx + S * 12, yy)], fill=255, width=S * 2)
    img.paste((70, 128, 176), mask=Image.composite(hatch, Image.new("L", (W, H), 0), marsh))
    # contour lines
    hgt = noise_field(W, H, rnd, 80, W * 0.12, W * 0.5, W * 0.08)
    steps = hgt.point(lambda v: (v // 8) * 40 % 256)
    edges = steps.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 10 else 0)
    img.paste((168, 116, 66), mask=edges.filter(ImageFilter.MaxFilter(3)))
    # river with a tributary and a small lake
    river = curve(rnd, (W * 0.15, -10), (W * 0.75, H + 10), W * 0.18, 44)
    d.line(river, fill=(132, 182, 216), width=S * 10, joint="curve")
    d.line(river, fill=(56, 116, 168), width=S * 2, joint="curve")
    trib = curve(rnd, river[20], (W + 10, H * 0.35), W * 0.06, 20)
    d.line(trib, fill=(56, 116, 168), width=S * 3, joint="curve")
    cx, cy, r = W * 0.30, H * 0.78, W * 0.07
    d.ellipse([cx - r * 1.5, cy - r, cx + r * 1.5, cy + r], fill=(150, 196, 222), outline=(56, 116, 168), width=S * 2)
    # highway and dirt roads
    road = curve(rnd, (-10, H * 0.30), (W + 10, H * 0.48), W * 0.06, 30)
    d.line(road, fill=(60, 50, 40), width=S * 9, joint="curve")
    d.line(road, fill=(232, 150, 64), width=S * 6, joint="curve")
    for _ in range(4):
        tr = curve(rnd, (rnd.uniform(0, W), rnd.uniform(0, H)), (rnd.uniform(0, W), rnd.uniform(0, H)), W * 0.05, 80)
        for i in range(0, len(tr) - 1, 2):
            d.line([tr[i], tr[i + 1]], fill=(92, 72, 52), width=S * 2)
    # power line: a straight line with triangle pylons
    a, b = (W * -0.05, H * 0.12), (W * 1.05, H * 0.66)
    d.line([a, b], fill=(40, 40, 40), width=S * 2)
    for k in range(1, 9):
        t = k / 9
        px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        d.polygon([(px, py - S * 6), (px - S * 5, py + S * 4), (px + S * 5, py + S * 4)], outline=(40, 40, 40), width=S)
    # hamlets: black houses in clusters
    for _ in range(4):
        cx, cy = rnd.uniform(0.1, 0.9) * W, rnd.uniform(0.08, 0.5) * H
        for _ in range(rnd.randint(4, 10)):
            hx, hy = cx + rnd.uniform(-1, 1) * W * 0.05, cy + rnd.uniform(-1, 1) * H * 0.025
            d.rectangle([hx, hy, hx + S * 6, hy + S * 4], fill=(30, 30, 30))
    # kilometre grid with digits at the edge
    step = 0.08 * PX_M * S
    fnt = font(int(S * 15))
    gx, k = step * 0.55, 0
    while gx < W:
        d.line([(gx, 0), (gx, H)], fill=(40, 40, 64), width=S)
        d.text((gx + S * 3, S * 3), "%02d" % (52 + k), fill=(40, 40, 64), font=fnt)
        gx, k = gx + step, k + 1
    gy, k = H - step * 0.35, 0
    while gy > 0:
        d.line([(0, gy), (W, gy)], fill=(40, 40, 64), width=S)
        d.text((S * 3, gy - S * 18), "%02d" % (18 + k), fill=(40, 40, 64), font=fnt)
        gy, k = gy - step, k + 1
    d.rectangle([0, 0, W - 1, H - 1], outline=(30, 30, 30), width=S * 4)
    # pencil route with ticks and marker marks
    pts = [(W * 0.12, H * 0.92), (W * 0.30, H * 0.70), (W * 0.52, H * 0.62), (W * 0.48, H * 0.40),
           (W * 0.70, H * 0.26), (W * 0.86, H * 0.12)]
    for p, q in zip(pts, pts[1:]):
        n = int(math.hypot(q[0] - p[0], q[1] - p[1]) / (S * 10))
        for j in range(0, n, 2):
            t0, t1 = j / n, (j + 1) / n
            d.line([(p[0] + (q[0] - p[0]) * t0, p[1] + (q[1] - p[1]) * t0),
                    (p[0] + (q[0] - p[0]) * t1, p[1] + (q[1] - p[1]) * t1)], fill=PENCIL, width=S * 3)
    for i, (x, y) in enumerate(pts[1:]):
        r = S * rnd.uniform(16, 22)
        if i == 2:
            d.line([(x - r, y - r), (x + r, y + r)], fill=MARKER, width=S * 4)
            d.line([(x - r, y + r), (x + r, y - r)], fill=MARKER, width=S * 4)
        else:
            d.ellipse([x - r, y - r * 0.85, x + r, y + r * 0.85], outline=MARKER, width=S * 4)
    # danger spot: a circle with hatching, a radiation sign inside
    cx, cy, R = W * 0.68, H * 0.52, W * 0.11
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=MARKER, width=S * 4)
    for j in range(-8, 9):
        o = j * R / 8
        h = math.sqrt(max(0.0, R * R - o * o)) * 0.7
        d.line([(cx + o - h, cy + h), (cx + o + h, cy - h)], fill=MARKER + (0,), width=S)
    rr = R * 0.35
    for k in range(3):
        a0 = -90 + k * 120 - 30
        d.pieslice([cx - rr, cy - rr, cx + rr, cy + rr], a0, a0 + 60, fill=(30, 30, 30))
    d.ellipse([cx - rr * 0.22, cy - rr * 0.22, cx + rr * 0.22, cy + rr * 0.22], fill=(30, 30, 30))
    img = aged(img, rnd)
    save(img, (int(wm * PX_M), int(hm * PX_M)), "decal_map.png")


def aged(img, rnd):
    """Yellowed spots, worn folds (the sheet was folded in four), dirt at the edges from hands."""
    W, H = img.size
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for _ in range(6):
        r = rnd.uniform(0.08, 0.2) * W
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(120, 90, 40, rnd.randint(20, 45)))
    for x in (0, W):
        d.rectangle([x - W * 0.06, H * 0.3, x + W * 0.06, H * 0.7], fill=(70, 56, 40, 40))
    ov = ov.filter(ImageFilter.GaussianBlur(S * 8))
    f = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(f)
    fd.line([(0, H / 2), (W, H / 2)], fill=(90, 80, 60, 70), width=S * 3)
    fd.line([(W / 2, 0), (W / 2, H)], fill=(90, 80, 60, 55), width=S * 3)
    f = f.filter(ImageFilter.GaussianBlur(S * 1.5))
    return Image.alpha_composite(Image.alpha_composite(img.convert("RGBA"), ov), f)


def make_crack(px_m=2500):
    """Crack along the grain of the right side: a ragged dark gap with branches, light raised fibres along
    the gap edges; the middle is covered by the plywood patch. Transparent background."""
    y0, y1, z0, z1 = L.CRACK
    W, H = int((y1 - y0) * px_m * S), int((z1 - z0) * px_m * S)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rnd = random.Random(2004)
    # the gap: from the bottom (the image bottom is the bottom of the side) up, small kinks along the grain
    n = 90
    x = W * 0.5
    pts = []
    for i in range(n + 1):
        x += rnd.uniform(-1.0, 1.0) * S * 2.2
        x = min(max(x, W * 0.25), W * 0.75)
        pts.append((x, H * (1.0 - i / n)))
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        # toward the ends the gap tapers off
        s = math.sin(math.pi * (i + 0.5) / n) ** 0.6
        wd = max(1, int(S * (1.0 + 2.2 * s * rnd.uniform(0.6, 1.0))))
        d.line([(p[0] + S * 1.5, p[1]), (q[0] + S * 1.5, q[1])], fill=(196, 160, 118, int(120 * s)), width=S)
        d.line([p, q], fill=(30, 18, 12, int(235 * s + 20)), width=wd)
    # branches - short slanted cracks
    for _ in range(6):
        i = rnd.randint(8, n - 8)
        x, y = pts[i]
        dx = rnd.choice((-1, 1)) * rnd.uniform(4, 10) * S
        d.line([(x, y), (x + dx, y - rnd.uniform(14, 40) * S)], fill=(40, 26, 18, 150), width=S)
    save(img, (W // S, H // S), "decal_crack.png")


def make_tag():
    """Inventory tag 60 x 30 mm: aluminium, frame, two nail holes, a number punched in digits. The tag is on
    the left side facing -x: the picture is mirrored so that the number reads from outside."""
    y0, y1, z0, z1 = L.TAG
    W, H = int((y1 - y0) * 8000), int((z1 - z0) * 8000)
    img = Image.new("RGBA", (W, H), (176, 178, 176, 255))
    d = ImageDraw.Draw(img)
    rnd = random.Random(417)
    for _ in range(400):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        d.line([(x, y), (x + rnd.uniform(4, 20), y + rnd.uniform(-1, 1))], fill=(150, 152, 150, 255), width=1)
    d.rectangle([6, 6, W - 7, H - 7], outline=(120, 122, 120, 255), width=3)
    for cx in (W * 0.08, W * 0.92):
        d.ellipse([cx - 9, H / 2 - 9, cx + 9, H / 2 + 9], fill=(40, 40, 40, 255))
    fnt = font(int(H * 0.52))
    for off, col in (((2, 2), (220, 222, 220, 255)), ((0, 0), (70, 70, 72, 255))):
        d.text((W * 0.22 + off[0], H * 0.20 + off[1]), "4417", fill=col, font=fnt)
    img = img.transpose(Image.FLIP_LEFT_RIGHT)
    save(img, (W // 2, H // 2), "decal_tag.png")


if __name__ == "__main__":
    make_map()
    make_crack()
    make_tag()
