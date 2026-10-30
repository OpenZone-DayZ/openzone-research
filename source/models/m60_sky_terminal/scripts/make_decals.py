"""Decals of the M60 field HQ (system Python + Pillow): the laptop screen, a map on graph paper,
stencils, the CS stripe and the radio panel. No letters: the screen shows a schematic map, bars and a
tree of blocks; the map has squiggles instead of captions; digits appear only as numbers on the crates,
the frequency in the wafer switch windows and the map grid margins. Where things go - layout.py.

    python make_decals.py      -> ../work/decal_*.png

- decal_screen_off.png          the 246 x 184 laptop screen 'off': a dark panel with a glare (the
                                screen's own texture, section screen - kmodel panels);
- decal_screen_f00..f11.png     12 'work' frames (an OZL_WorkFx frames loop of 0.25 s): a field
                                schematic map on dark (contours, swamp, river), the route dashes
                                crawl, the mark pulses, anomaly marks blink; on the right the link
                                bars jump, the active node of the research tree blinks and a carrier
                                reception bar grows; a block runs along the bottom;
- decal_crate0.png, _crate1.png the number and a stripe in black paint by stencil on the crate faces;
- decal_arrows.png              'up' arrows on the side of a crate - the crate stands on end, so they
                                look sideways;
- decal_radio_band.png          a pale-blue CS stripe with a brush across the radio face;
- decal_radio_top.png           the radio top: wafer switch windows with frequency digits, the knob
                                scale, frames;
- decal_map.png                 a swamp schematic in coloured pencils on A4 graph paper, rotated as
                                the tablet lies;
- decal_bolt.png                a lightning sign on the extension block.
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 2                                   # supersampling, then downscaling: clean edges
PX_M = 1400                             # pixels per metre (before downscaling)
K = PX_M * S
KH = 2 * PX_M * S                      # the screen and map are twice as dense: they are looked at close up
FONTS = "C:/Windows/Fonts/"
BLACK = (26, 26, 24)

# stencil digits on a 6 x 10 grid - from M32/M33/M36
DIGITS = {
    "0": [(0, 1, 1.2, 4.6), (0, 5.4, 1.2, 9), (4.8, 1, 6, 4.6), (4.8, 5.4, 6, 9), (1, 0, 5, 1.2), (1, 8.8, 5, 10)],
    "1": [(2.4, 0, 3.8, 4.6), (2.4, 5.4, 3.8, 10), (1.2, 0.6, 2.3, 1.8)],
    "2": [(0.4, 0, 5, 1.2), (4.8, 1, 6, 4.4), (0.6, 4.2, 5.4, 5.4), (0, 5.6, 1.2, 8.8), (0, 8.8, 6, 10)],
    "3": [(0.2, 0, 5, 1.2), (4.8, 1, 6, 4.4), (1.6, 4.4, 5, 5.6), (4.8, 5.6, 6, 9), (0.2, 8.8, 5, 10)],
    "4": [(0, 0, 1.2, 5.6), (0, 5.6, 4.2, 6.8), (3.6, 0, 4.8, 5.3), (3.6, 7.0, 4.8, 10)],
    "5": [(0.4, 0, 6, 1.2), (0, 0.6, 1.2, 4.4), (0.4, 4.2, 5, 5.4), (4.8, 5.6, 6, 9), (0, 8.8, 5, 10)],
    "7": [(0, 0, 4.6, 1.2), (4.8, 0, 6, 2.6), (3.6, 3.2, 4.8, 6.2), (2.6, 6.8, 3.8, 10)],
}


def font(name, h):
    return ImageFont.truetype(FONTS + name, max(8, int(h)))


def save(img, name):
    img = img.resize((max(1, img.width // S), max(1, img.height // S)), Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, img.size)


def worn_mask(W, H, rnd, n, rmin, rmax, blur):
    """Worn paint blotches: 255 - paint intact, 0 - worn off (from M32)."""
    m = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(m)
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        r = rnd.uniform(rmin, rmax)
        d.ellipse((x - r, y - r * rnd.uniform(0.3, 1.0), x + r, y + r * rnd.uniform(0.3, 1.0)), fill=0)
    return m.filter(ImageFilter.GaussianBlur(blur))


def paint(m, rnd, name, col=BLACK, n=60, keep=70, soft=1.0):
    """Mask -> paint by brush or stencil: a soft edge, worn in places (from M33/M36)."""
    W, H = m.size
    m = m.filter(ImageFilter.GaussianBlur(soft * S))
    m = ImageChops.multiply(m, worn_mask(W, H, rnd, n, 1.5 * S, 7 * S, 1.2 * S).point(
        lambda v: keep + v * (255 - keep) // 255))
    img = Image.new("RGBA", (W, H), col + (0,))
    img.putalpha(m)
    save(img, name)


def stencil_digits(d, text, x, y, cell_h, fill=235):
    u = cell_h / 10.0
    for ch in text:
        for a, b, c, e in DIGITS[ch]:
            d.rectangle((x + a * u, y + b * u, x + c * u, y + e * u), fill=fill)
        x += 7.6 * u


def wobble(rnd, pts, n=10, amp=0.0):
    """Polyline -> a smooth hand-drawn line: Catmull-Rom and a slight tremor."""
    out = []
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else pts[i + 1]
        for s in range(n):
            t = s / n
            q = [0.5 * (2 * p1[k] + (p2[k] - p0[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t +
                        (3 * p1[k] - p0[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in range(2)]
            out.append((q[0] + rnd.uniform(-amp, amp), q[1] + rnd.uniform(-amp, amp)))
    out.append(pts[-1])
    return out


def dashed(d, pts, dash, gap, fill, width, phase=0.0):
    """Dashes along a polyline; phase shifts the pattern along the line (the dashes 'crawl' from frame
    to frame): the point at length s is a dash if (s - phase) modulo (dash + gap) is less than dash.
    """
    q = (-phase) % (dash + gap)
    on, acc = (True, q) if q < dash else (False, q - dash)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        ln = math.hypot(x1 - x0, y1 - y0)
        t = 0.0
        while t < ln:
            step = min((dash if on else gap) - acc, ln - t)
            if on:
                a, b = t / ln, (t + step) / ln
                d.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)],
                       fill=fill, width=width)
            t += step
            acc += step
            if acc >= (dash if on else gap) - 1e-6:
                acc, on = 0.0, not on


def scribble(d, rnd, x, y, h, length, fill, width):
    """A hand-written caption without letters: a wavy line with loops."""
    pts, xx = [], x
    while xx < x + length:
        pts.append((xx, y + rnd.uniform(-0.45, 0.45) * h))
        xx += h * rnd.uniform(0.35, 0.6)
    d.line(wobble(rnd, pts, 4), fill=fill, width=width)


# =============================================================================
# Laptop screen
# =============================================================================
SCREEN_FRAMES = 12
# 'work': colours of the camp comms program on a dark screen
BG, GRID, CON, SWP, RIV = (6, 14, 12), (20, 52, 40), (70, 170, 96), (60, 150, 170), (70, 120, 230)
YEL, RED, WH, DIM = (240, 214, 70), (240, 70, 50), (210, 226, 214), (40, 96, 70)


def make_screen():
    """The laptop screen - its own texture (section screen): 'off' and the 'work' frames (an OZL_WorkFx
    frames loop).
    """
    K = KH
    W, H = int(L.LCD_W * K), int(L.LCD_H * K)
    off = Image.new("RGB", (W, H), (28, 31, 31))
    d = ImageDraw.Draw(off)
    for i in range(W):
        k = max(0.0, 1.0 - abs(i / W - 0.68) * 2.6)
        d.line([(i, 0), (i, H)], fill=(int(28 + 9 * k), int(31 + 9 * k), int(31 + 9 * k)))
    off = off.filter(ImageFilter.GaussianBlur(8 * S))
    save(off.convert("RGBA"), "decal_screen_off.png")
    for f in range(SCREEN_FRAMES):
        save(screen_frame(W, H, f).convert("RGBA"), "decal_screen_f%02d.png" % f)


def screen_frame(W, H, f):
    """Frame f of 'work': a field schematic map on dark - the screen of the camp comms program, without
    a single word. Everything static is drawn identically (the same random generator); what changes: the
    route dashes (crawl by a third of a step per frame), the mark on the route (pulses, 4 frames),
    anomaly marks (blink every other frame), link bars, the active tree node (blinks), the carrier
    reception bar (grows over 12 frames), the block in the status line.
    """
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    rnd = random.Random(60)
    lw = max(2, int(W * 0.004))
    bar = H * 0.065
    # top bar and status line: blocks instead of words; a transmit dot blinks on the right
    d.rectangle((0, 0, W, bar), fill=(18, 60, 46))
    xx = W * 0.015
    for k in range(5):
        w = W * rnd.uniform(0.06, 0.1)
        d.rectangle((xx, bar * 0.3, xx + w, bar * 0.7), fill=(150, 200, 170))
        xx += w + W * 0.035
    r = bar * 0.26
    d.ellipse((W * 0.965 - r, bar / 2 - r, W * 0.965 + r, bar / 2 + r), fill=RED if f % 2 == 0 else (70, 40, 34))
    d.rectangle((0, H - bar, W, H), fill=(18, 60, 46))
    for k in range(8):
        x = W * (0.02 + 0.12 * k)
        d.rectangle((x, H - bar * 0.72, x + W * 0.018, H - bar * 0.28), fill=WH)
        d.rectangle((x + W * 0.026, H - bar * 0.72, x + W * 0.09, H - bar * 0.28), fill=(60, 120, 92))
    x = W * (0.02 + 0.96 * f / SCREEN_FRAMES)                                 # running transmit block
    d.rectangle((x, H - bar * 0.86, x + W * 0.05, H - bar * 0.14), fill=YEL)
    # map window on the left
    mx0, my0, mx1, my1 = W * 0.02, bar * 1.4, W * 0.70, H - bar * 1.4
    d.rectangle((mx0, my0, mx1, my1), outline=CON, width=lw)
    mw, mh = mx1 - mx0, my1 - my0
    for k in range(1, 6):                                                     # grid
        x = mx0 + mw * k / 6
        d.line([(x, my0), (x, my1)], fill=GRID, width=max(1, lw // 2))
    for k in range(1, 5):
        y = my0 + mh * k / 5
        d.line([(mx0, y), (mx1, y)], fill=GRID, width=max(1, lw // 2))
    # contours round the hill at the top right
    cx, cy = mx0 + mw * 0.72, my0 + mh * 0.32
    for k in range(5):
        r = mw * (0.05 + 0.045 * k)
        pts = []
        for a in range(0, 361, 15):
            rr = r * (1 + 0.18 * math.sin(math.radians(a * 3 + k * 40)))
            pts.append((cx + rr * math.cos(math.radians(a)), cy + rr * 0.7 * math.sin(math.radians(a))))
        d.line(pts, fill=CON, width=lw)
    # river with a swamp
    riv = wobble(rnd, [(mx0, my0 + mh * 0.62), (mx0 + mw * 0.2, my0 + mh * 0.55), (mx0 + mw * 0.38, my0 + mh * 0.72),
                       (mx0 + mw * 0.55, my0 + mh * 0.66), (mx0 + mw * 0.8, my0 + mh * 0.85), (mx1, my0 + mh * 0.8)], 8)
    d.line(riv, fill=RIV, width=lw * 2)
    for _ in range(26):                                                       # swamp marks
        x = mx0 + mw * rnd.uniform(0.05, 0.5)
        y = my0 + mh * rnd.uniform(0.74, 0.95)
        s = mw * 0.018
        for j in range(3):
            d.line([(x - s + j * s * 0.2, y + j * s * 0.35), (x + s - j * s * 0.2, y + j * s * 0.35)], fill=SWP,
                   width=max(1, lw // 2))
    # route dashes (crawl by a third of a step per frame), route points, the camp
    route = [(mx0 + mw * 0.12, my0 + mh * 0.40), (mx0 + mw * 0.30, my0 + mh * 0.30), (mx0 + mw * 0.47, my0 + mh * 0.46),
             (mx0 + mw * 0.60, my0 + mh * 0.38), (mx0 + mw * 0.86, my0 + mh * 0.58)]
    dash, gap = mw * 0.025, mw * 0.015
    dashed(d, route, dash, gap, YEL, lw, phase=(dash + gap) * f / 3.0)
    for x, y in route:
        s = mw * 0.012
        d.rectangle((x - s, y - s, x + s, y + s), fill=YEL)
    cx, cy = route[0]
    d.rectangle((cx - mw * 0.03, cy - mw * 0.03, cx + mw * 0.03, cy + mw * 0.03), outline=WH, width=lw)
    # group mark on the route: the ring expands over 4 frames and fades
    x, y = route[2]
    ph = (f % 4) / 4.0
    r = mw * (0.022 + 0.05 * ph)
    c = tuple(int(WH[i] * (1.0 - ph) + BG[i] * ph) for i in range(3))
    d.ellipse((x - r, y - r, x + r, y + r), outline=c, width=lw)
    d.ellipse((x - mw * 0.016, y - mw * 0.016, x + mw * 0.016, y + mw * 0.016), fill=WH)
    # anomaly marks: blink every other frame
    rc = RED if f % 2 == 0 else (96, 40, 32)
    for x, y in ((mx0 + mw * 0.40, my0 + mh * 0.18), (mx0 + mw * 0.66, my0 + mh * 0.70)):
        r = mw * 0.035
        d.ellipse((x - r, y - r, x + r, y + r), outline=rc, width=lw)
        d.line([(x - r * 0.6, y - r * 0.6), (x + r * 0.6, y + r * 0.6)], fill=rc, width=lw)
        d.line([(x - r * 0.6, y + r * 0.6), (x + r * 0.6, y - r * 0.6)], fill=rc, width=lw)
    # crosshair cursor on the last point
    x, y = route[-1]
    d.line([(x - mw * 0.06, y), (x + mw * 0.06, y)], fill=WH, width=lw)
    d.line([(x, y - mw * 0.06), (x, y + mw * 0.06)], fill=WH, width=lw)
    # right: link level bars (jump from frame to frame) and the research tree of blocks
    sx0, sx1 = W * 0.73, W * 0.98
    d.rectangle((sx0, my0, sx1, my0 + mh * 0.36), outline=CON, width=lw)
    for k in range(7):
        lev = 0.25 + 0.75 * abs(math.sin(k * 1.3 + 0.4 + 0.9 * f + 0.35 * math.sin(f * 2.1 + k)))
        h = mh * 0.3 * lev
        x = sx0 + (sx1 - sx0) * (0.08 + 0.125 * k)
        d.rectangle((x, my0 + mh * 0.33 - h, x + (sx1 - sx0) * 0.08, my0 + mh * 0.33), fill=CON if k != 4 else YEL)
    ty0 = my0 + mh * 0.42
    d.rectangle((sx0, ty0, sx1, my1), outline=CON, width=lw)
    bw, bh = (sx1 - sx0) * 0.30, mh * 0.075
    nodes = {"r": ((sx0 + sx1) / 2, ty0 + mh * 0.09)}
    for i, fx in enumerate((0.22, 0.5, 0.78)):
        nodes["a%d" % i] = (sx0 + (sx1 - sx0) * fx, ty0 + mh * 0.25)
    for i, fx in enumerate((0.22, 0.5, 0.78)):
        nodes["b%d" % i] = (sx0 + (sx1 - sx0) * fx, ty0 + mh * 0.41)
    edges = [("r", "a0"), ("r", "a1"), ("r", "a2"), ("a0", "b0"), ("a1", "b1"), ("a2", "b2")]
    done = {"r", "a0", "a2", "b0"}
    for a, b in edges:
        (xa, ya), (xb, yb) = nodes[a], nodes[b]
        ym = (ya + yb) / 2
        d.line([(xa, ya + bh / 2), (xa, ym), (xb, ym), (xb, yb - bh / 2)], fill=WH if b in done else DIM, width=lw)
    for k, (x, y) in nodes.items():
        box = (x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2)
        if k in done:
            d.rectangle(box, fill=CON)
        elif k == "a1":
            # active node: blinks while a carrier is being received
            if f % 2 == 0:
                d.rectangle(box, fill=YEL)
            else:
                d.rectangle(box, outline=YEL, width=lw)
        else:
            d.rectangle(box, outline=DIM, width=lw)
    # carrier reception bar under the tree: grows over all frames
    py0, py1 = my1 - mh * 0.075, my1 - mh * 0.035
    px0, px1 = sx0 + (sx1 - sx0) * 0.08, sx1 - (sx1 - sx0) * 0.08
    d.rectangle((px0, py0, px1, py1), outline=CON, width=max(1, lw // 2))
    d.rectangle((px0 + lw, py0 + lw, px0 + lw + (px1 - px0 - 2 * lw) * (f + 1) / SCREEN_FRAMES, py1 - lw), fill=YEL)
    img = img.filter(ImageFilter.GaussianBlur(0.6 * S))
    glow = img.filter(ImageFilter.GaussianBlur(2.5 * S))
    return ImageChops.add(img, glow.point(lambda v: v // 3))


# =============================================================================
# Crate stencils
# =============================================================================
CRATE_DECAL = (0.30, 0.40)               # width, height of the decal on the crate face (centred on the face)


def make_crates():
    """Crate face (a former lid): a big number, below it a stripe with a rhombus - black paint by
    stencil over the blue. On the side - 'up' arrows: the crate stands on end, so they look sideways.
    """
    for i, text in enumerate(L.CRATE_NUM):
        rnd = random.Random(600 + i)
        W, H = int(CRATE_DECAL[0] * K), int(CRATE_DECAL[1] * K)
        m = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(m)
        ch = 0.095 * K
        u = ch / 10
        tw = len(text) * 7.6 * u - 1.6 * u
        stencil_digits(d, text, (W - tw) / 2, H * 0.10, ch)
        y = H * 0.50
        d.rectangle((W * 0.08, y, W * 0.44, y + 0.022 * K), fill=235)
        d.rectangle((W * 0.56, y, W * 0.92, y + 0.022 * K), fill=235)
        cx, cy, r = W * 0.5, y + 0.011 * K, 0.026 * K
        d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=235)
        stencil_digits(d, "3" if i == 0 else "2", W * 0.40, H * 0.66, 0.05 * K)
        paint(m, rnd, "decal_crate%d.png" % i, n=70, keep=60)
    # 'up' arrows: two arrows in a frame, drawn tip up and rotated by 90 - they face the player (-y)
    rnd = random.Random(610)
    W, H = int(0.16 * K), int(0.12 * K)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    lw = int(0.008 * K)
    for fx in (0.32, 0.68):
        x = W * fx
        d.rectangle((x - lw / 2, H * 0.35, x + lw / 2, H * 0.80), fill=235)
        d.polygon([(x, H * 0.12), (x + W * 0.11, H * 0.40), (x - W * 0.11, H * 0.40)], fill=235)
    d.rectangle((W * 0.12, H * 0.86, W * 0.88, H * 0.86 + lw), fill=235)
    m = m.rotate(90, expand=True)
    paint(m, rnd, "decal_arrows.png", n=40, keep=60)


# =============================================================================
# Radio
# =============================================================================
def make_radio():
    # pale-blue CS stripe with a brush across the face: ragged edges, strokes
    rnd = random.Random(621)
    W, H = int((L.RX1 - L.RX0) * K), int((L.BAND_Z[1] - L.BAND_Z[0]) * K)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    for k in range(9):
        y0 = H * rnd.uniform(0.04, 0.2)
        y1 = H * rnd.uniform(0.8, 0.96)
        x0 = W * rnd.uniform(0.0, 0.05)
        x1 = W * rnd.uniform(0.95, 1.0)
        d.rectangle((x0, y0, x1, y1), fill=int(rnd.uniform(200, 255)))
    for _ in range(40):
        x = rnd.uniform(0, W)
        d.line([(x, rnd.uniform(0, H * 0.2)), (x + rnd.uniform(-8, 8) * S, rnd.uniform(H * 0.8, H))], fill=255,
               width=int(rnd.uniform(1, 3) * S))
    paint(m, rnd, "decal_radio_band.png", col=(150, 192, 214), n=30, keep=150, soft=0.8)

    # panel on top: wafer switch windows with frequency digits, the scale at the volume knob, socket
    # frames
    x0, x1, y0, y1 = L.R_PANEL
    W, H = int((x1 - x0) * K), int((y1 - y0) * K)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def px(x, y):
        """Panel point (world) -> pixel: x to the right, world y is up in the picture."""
        return (x - x0) * K, (y1 - y) * K
    WH = (226, 226, 214, 255)
    f = font("arialbd.ttf", 0.011 * K)
    for (sx, sy), ch in zip(L.R_SWITCH, L.R_FREQ):
        cx, cy = px(sx, L.R_WIN_Y)
        w, h = 0.010 * K, 0.014 * K
        d.rectangle((cx - w, cy - h / 2, cx + w, cy + h / 2), fill=(12, 12, 12, 255), outline=WH, width=S)
        d.text((cx, cy), ch, font=f, fill=WH, anchor="mm")
        kx, ky = px(sx, sy)                                                   # tick marks round a wafer switch
        for a in range(0, 360, 36):
            r0, r1 = 0.0125 * K, 0.0155 * K
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            d.line([(kx + r0 * ca, ky + r0 * sa), (kx + r1 * ca, ky + r1 * sa)], fill=WH, width=S)
    cx, cy = px(*L.R_KNOB)                                                    # volume scale 0..10
    for k in range(11):
        a = math.radians(135 + 27 * k)
        r0, r1 = 0.015 * K, 0.019 * K if k % 5 else 0.022 * K
        d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))],
               fill=WH, width=S)
    for (tx, ty) in L.R_TERM + [L.R_ANT, L.R_CONN, L.R_LAMP]:                 # frames round the sockets and the lamp
        cx, cy = px(tx, ty)
        r = 0.022 * K if (tx, ty) in (L.R_ANT, L.R_CONN) else 0.014 * K
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=WH, width=S)
    ax, ay = px(L.R_SWITCH[0][0] - 0.016, L.R_WIN_Y + 0.016)                  # frame of the frequency block
    bx, by = px(L.R_SWITCH[-1][0] + 0.016, L.R_SWITCH[0][1] - 0.020)
    d.rectangle((ax, ay, bx, by), outline=WH, width=S)
    img = img.filter(ImageFilter.GaussianBlur(0.4 * S))
    save(img, "decal_radio_top.png")


# =============================================================================
# Map in coloured pencils on graph paper
# =============================================================================
def pencil_layer(W, H, rnd, grain=0.55):
    """A transparent layer for strokes and its grain: pencil lies unevenly, the paper shows through a
    stroke.
    """
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = Image.effect_noise((W, H), 90).point(lambda v: 255 if v > 255 * (1 - grain) else int(v * 1.6))
    return layer, g.filter(ImageFilter.GaussianBlur(0.5 * S))


def hatch(d, poly, step, ang, fill, width):
    """Hatching of a polygon with parallel lines at angle ang (degrees)."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    xs = [p[0] * ca + p[1] * sa for p in poly]
    ys = [-p[0] * sa + p[1] * ca for p in poly]
    v = min(ys)
    while v < max(ys):
        cuts = []
        for i in range(len(poly)):
            y0, y1 = ys[i], ys[(i + 1) % len(poly)]
            if (y0 <= v < y1) or (y1 <= v < y0):
                t = (v - y0) / (y1 - y0)
                cuts.append(xs[i] + (xs[(i + 1) % len(poly)] - xs[i]) * t)
        cuts.sort()
        for u0, u1 in zip(cuts[::2], cuts[1::2]):
            d.line([(u0 * ca - v * sa, u0 * sa + v * ca), (u1 * ca - v * sa, u1 * sa + v * ca)], fill=fill, width=width)
        v += step


def blob(rnd, cx, cy, rx, ry, n=14, k=0.22):
    return [(cx + rx * (1 + rnd.uniform(-k, k)) * math.cos(2 * math.pi * i / n),
             cy + ry * (1 + rnd.uniform(-k, k)) * math.sin(2 * math.pi * i / n)) for i in range(n)]


def make_map():
    """An A4 sheet of graph paper (1/5/10 mm grid, orange), with a swamp schematic in coloured pencils
    on it: green - forest by hatching, blue - the river, the lake and the swamp by marks, brown - paths
    dashed, red - anomalies by crosses, a dangerous area by hatching and the route by an arrow, plain
    pencil - squares with numbers in the margins and the camp by a flag. Squiggles instead of captions.
    Folded in half, with a stain. The picture is rotated by MAP_DEG, as the tablet lies: a decal
    projects along world axes. The exercise-book sheet with a blue pen is the M51 sample; this is
    another sheet and another drawing.
    """
    K = KH
    pw, ph, _ = L.MAP_PAPER
    W, H = int(pw * K), int(ph * K)
    rnd = random.Random(6060)
    PAPER = (240, 236, 220)
    G1, G5, G10 = (240, 226, 208), (236, 204, 172), (224, 166, 120)
    GREEN, BLUE, BROWN = (52, 120, 60), (40, 76, 168), (120, 78, 40)
    RED, PEN = (200, 46, 36), (70, 70, 74)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mm = 0.001 * K
    m0 = 8 * mm                                                               # sheet margins without the grid
    for k in range(int((W - 2 * m0) / mm) + 1):
        x = m0 + k * mm
        d.line([(x, m0), (x, H - m0)], fill=G10 if k % 10 == 0 else (G5 if k % 5 == 0 else G1),
               width=2 if k % 10 == 0 else 1)
    for k in range(int((H - 2 * m0) / mm) + 1):
        y = m0 + k * mm
        d.line([(m0, y), (W - m0, y)], fill=G10 if k % 10 == 0 else (G5 if k % 5 == 0 else G1),
               width=2 if k % 10 == 0 else 1)
    lw = max(2, int(0.0010 * K))
    layer, grain = pencil_layer(W, H, rnd)
    p = ImageDraw.Draw(layer)
    # forest: green patches by hatching with an outline
    for cx, cy, rx, ry in ((0.70, 0.20, 0.20, 0.12), (0.22, 0.14, 0.14, 0.07), (0.80, 0.62, 0.12, 0.10)):
        poly = blob(rnd, W * cx, H * cy, W * rx, H * ry)
        hatch(p, poly, 0.0022 * K, 35 + rnd.uniform(-8, 8), GREEN + (200,), max(1, lw // 2 + 1))
        p.line(wobble(rnd, poly + poly[:1], 4, 0.4 * S), fill=GREEN + (255,), width=lw)
    # river with a tributary, a lake, the swamp by marks
    river = wobble(rnd, [(W * 0.03, H * 0.34), (W * 0.18, H * 0.40), (W * 0.30, H * 0.52), (W * 0.46, H * 0.56),
                         (W * 0.58, H * 0.70), (W * 0.64, H * 0.86), (W * 0.70, H * 0.98)], 10, 0.4 * S)
    p.line(river, fill=BLUE + (255,), width=lw * 3)
    trib = wobble(rnd, [(W * 0.97, H * 0.44), (W * 0.82, H * 0.48), (W * 0.66, H * 0.54), (W * 0.50, H * 0.56)], 8,
                  0.4 * S)
    p.line(trib, fill=BLUE + (255,), width=lw * 2)
    lake = blob(rnd, W * 0.24, H * 0.72, W * 0.10, H * 0.05, 16, 0.18)
    hatch(p, lake, 0.0018 * K, 0, BLUE + (170,), max(1, lw // 2 + 1))
    p.line(wobble(rnd, lake + lake[:1], 4, 0.3 * S), fill=BLUE + (255,), width=lw)
    for _ in range(40):
        x, y = rnd.uniform(W * 0.06, W * 0.52), rnd.uniform(H * 0.80, H * 0.95)
        if rnd.random() < 0.35:
            x, y = rnd.uniform(W * 0.05, W * 0.22), rnd.uniform(H * 0.42, H * 0.62)
        s = 0.004 * K
        for j in range(2):
            p.line([(x - s + j * s * 0.3, y + j * s * 0.5), (x + s - j * s * 0.3, y + j * s * 0.5)], fill=BLUE + (230,),
                   width=max(1, lw // 2 + 1))
        for j in (-1, 0, 1):
            p.line([(x + j * s * 0.5, y - s * 0.1), (x + j * s * 0.75, y - s * 0.8)], fill=BLUE + (230,),
                   width=max(1, lw // 2))
    # paths in brown dashes
    for pts in ([(W * 0.10, H * 0.10), (W * 0.24, H * 0.24), (W * 0.38, H * 0.30), (W * 0.44, H * 0.46),
                 (W * 0.40, H * 0.64), (W * 0.46, H * 0.86)],
                [(W * 0.38, H * 0.30), (W * 0.54, H * 0.32), (W * 0.66, H * 0.40), (W * 0.90, H * 0.80)]):
        dashed(p, wobble(rnd, pts, 6, 0.3 * S), 0.006 * K, 0.0035 * K, BROWN + (255,), lw)
    # red: a dangerous area by hatching, anomalies by crosses, the route by an arrow
    zone = blob(rnd, W * 0.66, H * 0.30, W * 0.08, H * 0.05, 12, 0.25)
    hatch(p, zone, 0.003 * K, -40, RED + (190,), max(1, lw // 2 + 1))
    p.line(wobble(rnd, zone + zone[:1], 4, 0.5 * S), fill=RED + (255,), width=lw)
    for x, y in ((W * 0.58, H * 0.46), (W * 0.30, H * 0.88), (W * 0.84, H * 0.30), (W * 0.18, H * 0.30)):
        r = 0.007 * K
        p.line([(x - r, y - r), (x + r, y + r)], fill=RED + (255,), width=lw * 2)
        p.line([(x - r, y + r), (x + r, y - r)], fill=RED + (255,), width=lw * 2)
    arr = wobble(rnd, [(W * 0.40, H * 0.33), (W * 0.48, H * 0.40), (W * 0.54, H * 0.44)], 8, 0.3 * S)
    p.line(arr, fill=RED + (255,), width=lw * 2)
    (ax, ay), (bx, by) = arr[-2], arr[-1]
    a = math.atan2(by - ay, bx - ax)
    hl = 0.009 * K
    p.polygon([(bx, by), (bx - hl * math.cos(a - 0.45), by - hl * math.sin(a - 0.45)),
               (bx - hl * math.cos(a + 0.45), by - hl * math.sin(a + 0.45))], fill=RED + (255,))
    # plain pencil: the camp by a flag, squares, numbers in the margins, squiggle captions
    cx, cy = W * 0.38, H * 0.30
    s = 0.007 * K
    p.rectangle((cx - s, cy - s, cx + s, cy + s), outline=PEN + (255,), width=lw)
    p.line([(cx, cy - s), (cx, cy - s * 3.2)], fill=PEN + (255,), width=lw)
    p.polygon([(cx, cy - s * 3.2), (cx + s * 1.8, cy - s * 2.7), (cx, cy - s * 2.2)], fill=PEN + (255,))
    gx = [W * f for f in (0.12, 0.40, 0.68, 0.96)]
    gy = [H * f for f in (0.06, 0.26, 0.46, 0.66, 0.86)]
    for x in gx[:-1]:
        p.line(wobble(rnd, [(x, H * 0.04), (x + rnd.uniform(-3, 3) * S, H * 0.97)], 6, 0.5 * S),
               fill=PEN + (150,), width=max(1, lw // 2))
    for y in gy[1:]:
        p.line(wobble(rnd, [(W * 0.04, y), (W * 0.97, y + rnd.uniform(-3, 3) * S)], 6, 0.5 * S),
               fill=PEN + (150,), width=max(1, lw // 2))
    fs = font("comic.ttf", 0.006 * K)
    for i, x in enumerate(gx[:-1]):
        p.text(((x + gx[i + 1]) / 2, H * 0.025), str(36 + i), font=fs, fill=PEN + (255,), anchor="mm")
    for i, y in enumerate(gy[:-1]):
        p.text((W * 0.025, (y + gy[i + 1]) / 2), str(81 - i), font=fs, fill=PEN + (255,), anchor="mm")
    for x, y, ln, col in ((W * 0.42, H * 0.27, 0.03, PEN), (W * 0.60, H * 0.22, 0.028, RED),
                          (W * 0.10, H * 0.68, 0.025, BLUE), (W * 0.66, H * 0.10, 0.03, GREEN),
                          (W * 0.24, H * 0.92, 0.028, PEN), (W * 0.74, H * 0.74, 0.026, BROWN)):
        scribble(p, rnd, x, y, 0.004 * K, ln * K, col + (255,), max(1, lw // 2 + 1))
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), grain))
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    img = img.filter(ImageFilter.GaussianBlur(0.3 * S))
    # fold in half across and a mug stain
    sh = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(sh)
    yf = H * 0.50
    sd.line([(0, yf), (W, yf + 0.002 * K)], fill=90, width=int(0.0012 * K))
    cx, cy, r = W * 0.80, H * 0.90, 0.036 * K
    sd.ellipse((cx - r, cy - r, cx + r, cy + r), outline=60, width=int(0.003 * K))
    sh = sh.filter(ImageFilter.GaussianBlur(1.2 * S))
    img = Image.composite(Image.new("RGB", (W, H), (150, 128, 96)), img, sh.point(lambda v: v // 2))
    grime = worn_mask(W, H, rnd, 30, 0.01 * K, 0.03 * K, 0.02 * K).point(lambda v: (255 - v) // 10)
    img = Image.composite(Image.new("RGB", (W, H), (180, 170, 150)), img, grime)
    img = img.convert("RGBA").rotate(L.MAP_DEG, resample=Image.BICUBIC, expand=True)
    save(img, "decal_map.png")


def make_bolt():
    """Lightning sign: a yellow triangle with a black border and a bolt, no text."""
    W = H = int(0.040 * K)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    tri = [(W * 0.5, H * 0.06), (W * 0.96, H * 0.92), (W * 0.04, H * 0.92)]
    d.polygon(tri, fill=(20, 20, 18, 255))
    inner = [(W * 0.5, H * 0.20), (W * 0.84, H * 0.85), (W * 0.16, H * 0.85)]
    d.polygon(inner, fill=(236, 190, 30, 255))
    d.polygon([(W * 0.55, H * 0.34), (W * 0.40, H * 0.60), (W * 0.52, H * 0.60), (W * 0.44, H * 0.80),
               (W * 0.62, H * 0.52), (W * 0.50, H * 0.52), (W * 0.58, H * 0.34)], fill=(20, 20, 18, 255))
    save(img, "decal_bolt.png")


if __name__ == "__main__":
    make_screen()
    make_crates()
    make_radio()
    make_map()
    make_bolt()
