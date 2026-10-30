"""Images for the M66 "Trails" carrier (system Python + Pillow), without letters:
- map.png - the edge of an A2 tracing paper sheet with a map inked from a topographic map (RGBA: the
  ink colour, alpha where there is ink; the paper is drawn by the material). A strip at the edge of
  the sheet that sticks out of the tube: s from the end of the roll (0) deep into MAP_S, t along the
  sheet in the winding direction from the free edge (0) over the full length (594 mm). On it: a
  topographic map frame with minute "checks" and kilometre grid numbers outside the frame,
  registration crosses, contour lines in brown ink (every fifth thicker), a river and a stream in
  blue, a road as a double line with a bridge, a forest edge in dots with tree symbols, a marsh in
  dashes, a route in red ink dashed with arrows, points 1-7 in circles, the end of the route a flag in
  a double circle, anomaly zones as hatched red circles with a trefoil in one; pencil distance and
  mark numbers;
- label.png - a tag on the body: a red stripe (the colour of the "Trails" line; other lines use green
  M47, yellow M48, orange M49, blue M52, grey M53), a frame, empty fields, a number in pen, a violet
  round stamp with a wind rose and no text.

    python make_decals.py      -> ../work/*.png

The digits are our own strokes (as in M63): no system fonts are needed, the image does not depend on
the machine.
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m66_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 3                       # drawing is done at S times the final resolution

MAP_S = 0.110               # sheet strip from the end of the roll
MAP_PPM = 5000              # pixels per metre in the final image (5 px/mm)

INK_BLACK = (22, 22, 26)
INK_RED = (188, 30, 26)
INK_BLUE = (28, 70, 158)
INK_BROWN = (128, 74, 36)
GRAPHITE = (84, 84, 92)


# --- handwritten digits: strokes in a 1 x 1.6 box (y up), from the M63 generator ------------------
def _arc(cx, cy, rx, ry, a0, a1, n=10):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


GLYPHS = {
    "0": [_arc(0.5, 0.8, 0.42, 0.78, 95, 455, 16)],
    "1": [[(0.22, 1.25), (0.55, 1.6), (0.52, 0.0)]],
    "2": [_arc(0.5, 1.15, 0.4, 0.42, 160, -20, 8) + [(0.1, 0.0), (0.95, 0.05)]],
    "3": [_arc(0.48, 1.2, 0.38, 0.38, 150, -90, 8) + _arc(0.48, 0.42, 0.44, 0.42, 90, -150, 8)],
    "4": [[(0.7, 0.0), (0.72, 1.6), (0.05, 0.45), (0.98, 0.45)]],
    "5": [[(0.9, 1.58), (0.2, 1.55), (0.12, 0.9)] + _arc(0.5, 0.5, 0.45, 0.5, 125, -150, 9)],
    "6": [_arc(0.6, 1.0, 0.45, 0.62, 70, 190, 6) + _arc(0.5, 0.45, 0.42, 0.45, 180, 540, 12)],
    "7": [[(0.05, 1.55), (0.95, 1.58), (0.35, 0.0)]],
    "8": [_arc(0.5, 1.2, 0.34, 0.38, -90, 270, 12) + _arc(0.5, 0.42, 0.42, 0.42, 90, 450, 12)],
    "9": [_arc(0.48, 1.15, 0.4, 0.43, -10, 350, 12) + [(0.86, 1.0), (0.6, 0.0)]],
    "-": [[(0.15, 0.75), (0.85, 0.78)]],
    ".": [[(0.45, 0.02), (0.52, 0.0)]],
}


def handwrite(draw, text, x, y, h, fill, width, rng, slant=0.18, rot=0.0):
    """A string of handwritten digits: bottom left corner (x, y) in image pixels (y down), height h."""
    w = h / 1.6
    cx = x
    ca, sa = math.cos(rot), math.sin(rot)
    for ch in text:
        if ch == " ":
            cx += w * 0.8
            continue
        jit = (rng.uniform(-0.05, 0.05) * h, rng.uniform(-0.06, 0.06) * h)
        sc = 1.0 + rng.uniform(-0.06, 0.06)
        for stroke in GLYPHS[ch]:
            pts = []
            for gx, gy in stroke:
                px = (gx + gy * slant) * w * sc + rng.uniform(-0.02, 0.02) * h
                py = gy * w * sc + rng.uniform(-0.02, 0.02) * h
                dx, dy = cx - x + px + jit[0], -py + jit[1]
                pts.append((x + dx * ca - dy * sa, y + dx * sa + dy * ca))
            draw.line(pts, fill=fill, width=width, joint="curve")
            for p in (pts[0], pts[-1]):
                r = width / 2
                draw.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=fill)
        cx += w * (1.15 if ch not in "1." else 0.7)


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    img.save(os.path.join(WORK, name))
    print("wrote", name, size)


def noise_img(w, h, cell, rng, lo=0, hi=255):
    """Smooth noise: a random grid enlarged bicubically."""
    gw, gh = max(2, int(w / cell) + 2), max(2, int(h / cell) + 2)
    small = Image.new("L", (gw, gh))
    small.putdata([rng.randint(lo, hi) for _ in range(gw * gh)])
    return small.resize((w, h), Image.BICUBIC)


# --- map on tracing paper -------------------------------------------------------------------------
class Sheet:
    """A single-colour ink layer: an L mask in sheet coordinates (t, s) in mm."""

    def __init__(self, w_mm, h_mm, k, fr=0.0, squeeze=1.0):
        self.k = k
        self.w, self.h = int(w_mm * k), int(h_mm * k)
        self.h_mm = h_mm
        self.fr, self.squeeze = fr, squeeze

    def layer(self):
        im = Image.new("L", (self.w, self.h), 0)
        return im, ImageDraw.Draw(im)

    def px(self, t, s):
        """(t, s) mm -> pixels: t to the right, s = 0 (the end of the roll) is the bottom row of the image. The
        drawing beyond the frame (s > fr) is squeezed towards the edge by a factor of squeeze: only 80 mm of
        the sheet stick out of the tube."""
        if s > self.fr:
            s = self.fr + (s - self.fr) * self.squeeze
        return (t * self.k, (self.h_mm - s) * self.k)


def smooth(pts, it=3):
    for _ in range(it):
        out = [pts[0]]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            out += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1), (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        out.append(pts[-1])
        pts = out
    return pts


def resample(pts, step):
    out = [pts[0]]
    acc = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        d = step - acc
        while d <= seg:
            f = d / seg
            out.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f))
            d += step
        acc = (acc + seg) % step
    out.append(pts[-1])
    return out


def length(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def pen_line(sh, d, pts_mm, width_mm, dash=None, fill=255):
    """A ruling-pen line: points in sheet mm; dash = (dash, gap) mm."""
    w = max(1, int(round(width_mm * sh.k)))
    pts = resample(pts_mm, 0.4)
    if dash is None:
        d.line([sh.px(*p) for p in pts], fill=fill, width=w, joint="curve")
        return
    on, off = dash
    run, cur, draw_on = 0.0, [pts[0]], True
    for a, b in zip(pts, pts[1:]):
        run += math.hypot(b[0] - a[0], b[1] - a[1])
        cur.append(b)
        lim = on if draw_on else off
        if run >= lim:
            if draw_on and len(cur) > 1:
                d.line([sh.px(*p) for p in cur], fill=fill, width=w, joint="curve")
            draw_on = not draw_on
            run, cur = 0.0, [b]
    if draw_on and len(cur) > 1:
        d.line([sh.px(*p) for p in cur], fill=fill, width=w, joint="curve")


def circle(sh, d, c, r, width_mm, fill=255, solid=False):
    x, y = sh.px(*c)
    rr = r * sh.k
    if solid:
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=fill)
    else:
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=fill, width=max(1, int(width_mm * sh.k)))


def wobbly_loop(c, rx, ry, rng, n=40, amp=0.18, rot=0.0):
    ph = [rng.uniform(0, 2 * math.pi) for _ in range(3)]
    pts = []
    for i in range(n + 1):
        a = 2 * math.pi * i / n
        f = 1 + amp * (0.5 * math.sin(2 * a + ph[0]) + 0.3 * math.sin(3 * a + ph[1]) + 0.2 * math.sin(5 * a + ph[2]))
        x, y = rx * f * math.cos(a), ry * f * math.sin(a)
        pts.append((c[0] + x * math.cos(rot) - y * math.sin(rot), c[1] + x * math.sin(rot) + y * math.cos(rot)))
    return pts


def clip_frame(pts, s_min):
    """Keep the segments inside the frame (s > s_min)."""
    runs, cur = [], []
    for p in pts:
        if p[1] > s_min:
            cur.append(p)
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return [r for r in runs if len(r) > 1]


def map_img():
    W_MM, H_MM = L.SHEET_T * 1000.0, MAP_S * 1000.0
    k = MAP_PPM / 1000.0 * S
    FR = 12.0                         # inner frame line: s, mm
    sh = Sheet(W_MM, H_MM, k, FR, 0.70)
    rng = random.Random(6601)
    layers = {}

    # --- frame: a thick outer line, a thin inner one, minute checks between them ------------------
    blk, db = sh.layer()
    pen_line(sh, db, [(0, 8.0), (W_MM, 8.0)], 0.8)
    pen_line(sh, db, [(0, FR), (W_MM, FR)], 0.35)
    pen_line(sh, db, [(0, 9.6), (W_MM, 9.6)], 0.25)
    t = 3.0
    on = True
    while t < W_MM:
        if on:
            x0, y0 = sh.px(t, 9.6)
            x1, y1 = sh.px(min(t + 9.3, W_MM), 8.0)
            db.rectangle((x0, y0, x1, y1), fill=255)
        t += 9.3
        on = not on
    # kilometre grid: line exits beyond the frame with numbers at them, registration crosses inside
    for i, tg in enumerate([22.0 + 40.0 * j for j in range(15)]):
        if tg > W_MM - 4:
            break
        pen_line(sh, db, [(tg, 4.5), (tg, 8.0)], 0.3)
        x, y = sh.px(tg + 1.0, 1.2)
        handwrite(db, "%02d" % (38 + i), x, y, 3.2 * k, 255, max(1, int(0.3 * k)), rng, slant=0.05)
        for sg in (52.0, 92.0):
            if (i + (sg > 60)) % 2 == 0:
                pen_line(sh, db, [(tg - 3.5, sg), (tg + 3.5, sg)], 0.3)
                pen_line(sh, db, [(tg, sg - 4.5), (tg, sg + 4.5)], 0.3)

    # --- contour lines: two hills and a slope to the river ----------------------------------------
    brn, dn = sh.layer()
    for c, rx0, ry0, n, rot in (((236.0, 78.0), 10.0, 6.5, 6, 0.4), ((468.0, 46.0), 8.0, 6.0, 5, -0.3),
                                ((92.0, 60.0), 14.0, 9.0, 3, 0.1)):
        for j in range(n):
            loop = wobbly_loop(c, rx0 + j * 5.6, ry0 + j * 3.8, random.Random(70 + j + int(c[0])), amp=0.12 + 0.02 * j, rot=rot)
            for run in clip_frame(smooth(loop, 2), FR + 0.8):
                pen_line(sh, dn, run, 0.5 if j % 5 == 4 or j == n - 1 and n == 6 else 0.3)
    # elevation marks in pencil, and an ink dot on the summits
    for c in ((236.0, 78.0), (468.0, 46.0)):
        circle(sh, dn, c, 0.6, 0.3, solid=True)
    # --- water: river and stream, marsh -----------------------------------------------------------
    blu, dw = sh.layer()
    river = [(0.0, 101.0), (40.0, 96.0), (70.0, 99.0), (118.0, 86.0), (150.0, 72.0), (172.0, 52.0),
             (204.0, 40.0), (262.0, 34.0), (300.0, 24.0), (338.0, 19.0), (372.0, 22.0), (420.0, 16.5)]
    river = smooth(river, 4)
    for run in clip_frame(river, FR + 0.5):
        n = len(run)
        for i in range(0, n - 1, 6):
            seg = run[i:i + 7]
            pen_line(sh, dw, seg, 0.5 + 0.5 * (i / n))
    brook = smooth([(150.0, 72.0), (156.0, 84.0), (150.0, 96.0), (162.0, 108.0), (170.0, 112.0)], 3)
    pen_line(sh, dw, brook, 0.35)
    for i in range(9):                                   # marsh: short dashes in rows
        y = 82.0 + (i % 3) * 3.2
        x = 520.0 + (i // 3) * 8.0 + (i % 3) * 2.0
        pen_line(sh, dw, [(x, y), (x + 4.5, y)], 0.3)
        pen_line(sh, dw, [(x + 1.2, y + 1.6), (x + 3.2, y + 1.6)], 0.3)

    # --- road as a double line, bridge, forest ----------------------------------------------------
    road = smooth([(96.0, 113.0), (120.0, 104.0), (170.0, 95.0), (200.0, 70.0), (232.0, 52.0), (290.0, 46.0),
                   (330.0, 38.0), (372.0, 26.0), (394.0, 13.0)], 4)
    road = resample(road, 0.6)
    for side in (-1.0, 1.0):
        off = []
        for i, p in enumerate(road):
            a, b = road[max(i - 1, 0)], road[min(i + 1, len(road) - 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy) or 1.0
            off.append((p[0] - dy / ln * side, p[1] + dx / ln * side))
        for run in clip_frame(off, FR + 0.5):
            pen_line(sh, db, run, 0.3)
    # bridge: where the road crosses the river, two brackets
    best = min(((math.hypot(p[0] - q[0], p[1] - q[1]), p) for p in road[::3] for q in river[::2]), key=lambda z: z[0])[1]
    for sgn in (-1, 1):
        x, y = best[0] + sgn * 2.4, best[1]
        pen_line(sh, db, [(x + sgn * 1.2, y - 3.4), (x, y - 2.2), (x, y + 2.2), (x + sgn * 1.2, y + 3.4)], 0.35)
    forest = wobbly_loop((300.0, 82.0), 34.0, 17.0, random.Random(81), n=70, amp=0.16)
    for run in clip_frame(resample(smooth(forest, 2), 1.9), FR + 2.0):
        for p in run:
            circle(sh, db, p, 0.42, 0.1, solid=True)
    rt = random.Random(82)
    for _ in range(14):                                  # tree symbols: a circle on a stem
        a = rt.uniform(0, 2 * math.pi)
        rr = math.sqrt(rt.uniform(0.05, 0.6))
        x, y = 300.0 + 30.0 * rr * math.cos(a), 82.0 + 14.0 * rr * math.sin(a)
        circle(sh, db, (x, y + 1.3), 1.15, 0.28)
        pen_line(sh, db, [(x, y), (x, y - 1.2)], 0.28)

    # --- route in red ink, points, anomaly zones --------------------------------------------------
    red, dr = sh.layer()
    route = [(6.0, 64.0), (30.0, 72.0), (58.0, 86.0), (84.0, 84.0), (118.0, 66.0), (140.0, 48.0),
             (176.0, 30.0), (214.0, 26.0), (246.0, 40.0), (268.0, 58.0), (282.0, 92.0), (318.0, 104.0),
             (352.0, 96.0), (384.0, 74.0), (412.0, 62.0), (438.0, 70.0), (470.0, 86.0), (506.0, 72.0),
             (540.0, 60.0), (566.0, 44.0), (588.0, 36.0)]
    rs = smooth(route, 4)
    pen_line(sh, dr, rs, 0.9, dash=(4.6, 2.0))
    marks = []
    acc, nxt, num = 0.0, 40.0, 1
    for a, b in zip(rs, rs[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        acc += seg
        if acc >= nxt and num <= 7:
            marks.append((b, math.atan2(b[1] - a[1], b[0] - a[0]), num))
            nxt += 78.0
            num += 1
    for (x, y), ang, n in marks:
        circle(sh, dr, (x, y), 2.6, 0.5)
        nx, ny = -math.sin(ang), math.cos(ang)
        px_, py_ = sh.px(x + nx * 4.0 + 0.8, y + ny * 4.0 - 1.6)
        handwrite(dr, str(n), px_, py_, 4.2 * k, 255, max(1, int(0.45 * k)), rng, slant=0.1)
        # direction arrow 14 mm after the point
    for i in range(2, len(rs) - 2, 22):
        (x0, y0), (x1, y1) = rs[i], rs[i + 1]
        ang = math.atan2(y1 - y0, x1 - x0)
        for sgn in (-1, 1):
            a2 = ang + math.pi + sgn * 0.45
            pen_line(sh, dr, [(x1, y1), (x1 + 3.4 * math.cos(a2), y1 + 3.4 * math.sin(a2))], 0.75)
    end = rs[-1]
    circle(sh, dr, end, 4.0, 0.55)
    circle(sh, dr, end, 2.6, 0.45)
    pen_line(sh, dr, [(end[0], end[1]), (end[0], end[1] + 8.0)], 0.55)
    pen_line(sh, dr, [(end[0], end[1] + 8.0), (end[0] + 4.6, end[1] + 6.6), (end[0], end[1] + 5.2)], 0.5)
    # anomalies: hatching in circles, a dashed border, a trefoil
    for c, r, rot, tri in (((196.0, 58.0), 9.0, 0.6, False), ((352.0, 64.0), 11.0, -0.5, True),
                           ((540.0, 92.0), 7.5, 0.9, False)):
        loop = wobbly_loop(c, r, r * 0.85, random.Random(int(c[0])), amp=0.08, rot=rot)
        pen_line(sh, dr, smooth(loop, 2), 0.5, dash=(2.0, 1.2))
        hatch = Image.new("L", (sh.w, sh.h), 0)
        dh = ImageDraw.Draw(hatch)
        for j in range(-10, 11):
            o = j * 2.2
            p0 = (c[0] + o * math.cos(rot) - r * 1.2 * math.sin(rot), c[1] + o * math.sin(rot) + r * 1.2 * math.cos(rot))
            p1 = (c[0] + o * math.cos(rot) + r * 1.2 * math.sin(rot), c[1] + o * math.sin(rot) - r * 1.2 * math.cos(rot))
            pen_line(sh, dh, [p0, p1], 0.32)
        mask = Image.new("L", (sh.w, sh.h), 0)
        ImageDraw.Draw(mask).polygon([sh.px(*p) for p in loop], fill=255)
        if tri:
            ImageDraw.Draw(mask).ellipse([*sh.px(c[0] - 5.0, c[1] + 5.0), *sh.px(c[0] + 5.0, c[1] - 5.0)], fill=0)
            cx, cy = sh.px(*c)
            ri, ro = 1.0 * k, 4.2 * k
            dr.ellipse((cx - 0.7 * k, cy - 0.7 * k, cx + 0.7 * k, cy + 0.7 * k), fill=255)
            for j in range(3):
                a0, a1 = math.radians(90 + 120 * j - 30), math.radians(90 + 120 * j + 30)
                pts = [(cx + ri * math.cos(a0 + (a1 - a0) * q / 8), cy - ri * math.sin(a0 + (a1 - a0) * q / 8)) for q in range(9)]
                pts += [(cx + ro * math.cos(a1 - (a1 - a0) * q / 8), cy - ro * math.sin(a1 - (a1 - a0) * q / 8)) for q in range(9)]
                dr.polygon(pts, fill=255)
        red.paste(255, (0, 0), ImageChops.multiply(hatch, mask))

    # --- pencil: distance and mark numbers --------------------------------------------------------
    gra, dg = sh.layer()
    for (t_, s_), txt in (((48.0, 76.0), "350"), ((128.0, 50.0), "1.2"), ((226.0, 86.0), "214"), ((288.0, 74.0), "60"),
                          ((400.0, 80.0), "800"), ((462.0, 52.0), "187"), ((556.0, 64.0), "2.5"), ((250.0, 20.0), "1430")):
        x, y = sh.px(t_, s_)
        handwrite(dg, txt, x, y, 3.6 * k, 210, max(1, int(0.3 * k)), rng, slant=0.2, rot=rng.uniform(-0.15, 0.1))
    pen_line(sh, dg, [(412.0, 62.0), (420.0, 58.5), (440.0, 57.0)], 0.3)

    # --- composite: red and blue over brown, black over all, pencil paler -------------------------
    out = Image.new("RGBA", (sh.w, sh.h), (0, 0, 0, 0))
    grain = noise_img(sh.w, sh.h, 0.6 * k, rng, 170, 255)
    for im, col, k_a in ((gra, GRAPHITE, 0.55), (brn, INK_BROWN, 0.95), (blu, INK_BLUE, 0.95), (blk, INK_BLACK, 1.0),
                         (red, INK_RED, 1.0)):
        a = ImageChops.multiply(im.filter(ImageFilter.GaussianBlur(0.05 * k)), grain).point(lambda v, k_a=k_a: int(v * k_a))
        lay = Image.new("RGBA", (sh.w, sh.h), col + (0,))
        lay.putalpha(a)
        out = Image.alpha_composite(out, lay)
    size = (int(W_MM * MAP_PPM / 1000.0), int(H_MM * MAP_PPM / 1000.0))
    save(out, size, "map.png")


# --- tag ------------------------------------------------------------------------------------------
def label_img():
    ppm = 12000
    lw_, lh_ = L.LABEL_SIZE
    W, H = int(lw_ * ppm), int(lh_ * ppm)
    W3, H3 = W * S, H * S
    k = ppm * S
    rng = random.Random(6602)
    img = Image.new("RGB", (W3, H3), (234, 228, 206))
    d = ImageDraw.Draw(img)
    stripe = 0.007 * k
    d.rectangle((0, 0, stripe, H3), fill=(186, 44, 36))
    ink = (58, 60, 76)
    lw = max(1, int(0.00022 * k))
    m = 0.002 * k
    d.rectangle((stripe + m, m, W3 - m, H3 - m), outline=ink, width=lw)
    rows = 4
    top, bot = m + 0.0010 * k, H3 - m - 0.0010 * k
    for i in range(1, rows):
        y = top + (bot - top) * i / rows
        d.line((stripe + m, y, W3 - m, y), fill=ink, width=lw)
    for i in range(rows):                                  # field number: an empty small square on the left
        y = top + (bot - top) * (i + 0.5) / rows
        s = 0.0022 * k
        d.rectangle((stripe + m + 0.0018 * k, y - s / 2, stripe + m + 0.0018 * k + s, y + s / 2), outline=ink, width=lw)
    for i, xk in ((0, 0.037), (1, 0.040), (3, 0.026)):
        d.line((stripe + xk * k, top + (bot - top) * i / rows, stripe + xk * k, top + (bot - top) * (i + 1) / rows),
               fill=ink, width=lw)
    pen = (36, 54, 132)
    pw = max(1, int(0.00035 * k))
    handwrite(d, "07-214", stripe + 0.0075 * k, top + (bot - top) * 0.84 / rows, 0.0058 * k, pen, pw, rng, rot=-0.02)
    handwrite(d, "7", stripe + 0.0080 * k, top + (bot - top) * 1.84 / rows, 0.0056 * k, pen, pw, rng)
    handwrite(d, "1430", stripe + 0.0075 * k, top + (bot - top) * 3.84 / rows, 0.0052 * k, pen, pw, rng, rot=0.02)
    d.line((stripe + 0.031 * k, top + (bot - top) * 1.55 / rows, stripe + 0.040 * k, top + (bot - top) * 1.5 / rows),
           fill=pen, width=pw)

    # violet stamp: a double ring and a wind rose (four rays), an uneven impression
    st = Image.new("L", (W3, H3), 0)
    ds = ImageDraw.Draw(st)
    cx, cy, R = W3 - 0.0150 * k, H3 * 0.42, 0.0092 * k
    ds.ellipse((cx - R, cy - R, cx + R, cy + R), outline=255, width=int(0.0009 * k))
    r2 = R - 0.0016 * k
    ds.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), outline=255, width=int(0.00045 * k))
    rot = math.radians(-12)
    for j in range(8):
        a = rot + math.pi / 4 * j
        ro = (0.0062 if j % 2 == 0 else 0.0036) * k
        ri = 0.0011 * k
        pts = [(cx + ro * math.cos(a), cy - ro * math.sin(a)),
               (cx + ri * math.cos(a + 0.6), cy - ri * math.sin(a + 0.6)),
               (cx, cy),
               (cx + ri * math.cos(a - 0.6), cy - ri * math.sin(a - 0.6))]
        ds.polygon(pts, fill=255 if j % 2 == 0 else 200)
    for j in range(16):                                   # notches around the ring
        a = 2 * math.pi * j / 16
        ds.line((cx + (r2 - 0.0012 * k) * math.cos(a), cy - (r2 - 0.0012 * k) * math.sin(a),
                 cx + r2 * math.cos(a), cy - r2 * math.sin(a)), fill=255, width=int(0.0003 * k))
    patchy = noise_img(W3, H3, 0.0012 * k, rng, 90, 255)
    fade = Image.new("L", (W3, H3), 0)
    ImageDraw.Draw(fade).ellipse((cx - R * 2.2, cy - R * 1.2, cx + R * 0.6, cy + R * 2.4), fill=255)
    fade = fade.filter(ImageFilter.GaussianBlur(R * 0.8)).point(lambda a: 120 + a // 2)
    st = ImageChops.multiply(ImageChops.multiply(st, patchy), fade).filter(ImageFilter.GaussianBlur(0.00012 * k))
    img = Image.composite(Image.new("RGB", (W3, H3), (104, 62, 142)), img, st.point(lambda a: int(a * 0.80)))

    # the tag edges are dirtier, a finger stain at the edge
    e = Image.new("L", (W3, H3), 0)
    ImageDraw.Draw(e).rectangle((0, 0, W3, H3), outline=255, width=int(0.0012 * k))
    e = e.filter(ImageFilter.GaussianBlur(0.001 * k)).point(lambda a: int(a * 0.32))
    img = Image.composite(Image.new("RGB", (W3, H3), (140, 128, 104)), img, e)
    sm = Image.new("L", (W3, H3), 0)
    ImageDraw.Draw(sm).ellipse((W3 * 0.70, H3 * 0.72, W3 * 0.96, H3 * 1.15), fill=255)
    sm = ImageChops.multiply(sm.filter(ImageFilter.GaussianBlur(0.002 * k)),
                            noise_img(W3, H3, 0.0008 * k, rng, 0, 255).filter(ImageFilter.GaussianBlur(0.0004 * k)))
    img = Image.composite(Image.new("RGB", (W3, H3), (120, 108, 88)), img, sm.point(lambda a: int(a * 0.28)))
    save(img, (W, H), "label.png")


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    map_img()
    label_img()
