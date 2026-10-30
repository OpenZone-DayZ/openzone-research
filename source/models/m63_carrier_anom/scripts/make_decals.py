"""Decals of the M63 "Anomaly" carrier (system Python + Pillow), without letters:
- env_top.png / env_top_h.png - the back of the envelope and the inside of the open flap (u 0..0.30 m,
  v across): the edge of the glued bottom and the seam in the middle (shadow, squeezed-out glue), soft
  creases, worn light edges, dirt at the mouth and along the edges, water-stain blotches, places
  rubbed by fingers at the notch; on the flap, the back of the eyelet. _h is the relief in alpha
  (0.5 is flat);
- print.png - a 13 x 18 cm print on glossy photo paper: a photo of the screen of a multichannel
  analyser (a dark screen, a light dotted curve of a gamma spectrum on a logarithmic scale - a solid
  background, Compton edges and five peaks, with a cursor and a highlighted region at the last one),
  scale ticks without captions, a row of indicator digits in dots; on the white border in pencil,
  the sample number in digits and a "?" with an arrow at the unknown peak;
- label.png - an archive tag: a yellow stripe (the "Anomaly" line, like the sample ring of M48), a
  frame, empty fields, a number in ballpoint pen, a violet round stamp with a radiation sign and no
  text.

    python make_decals.py      -> ../work/*.png

The digits are our own strokes (handwriting) and our own 5 x 7 dot matrix (the indicator): no system
fonts are needed, the image does not depend on the machine. Sizes come from m63_layout.py (shared
with build_m63.py).
"""
import math
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m63_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 3                       # drawing is done at S times the final resolution (supersampling)

# --- handwritten digits: strokes in a 1 x 1.6 box (y up) ------------------------------------------
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
    "?": [_arc(0.5, 1.2, 0.38, 0.38, 160, -60, 8) + [(0.5, 0.55), (0.5, 0.38)], [(0.5, 0.08), (0.52, 0.0)]],
}


def handwrite(draw, text, x, y, h, color, width, rng, slant=0.18, rot=0.0):
    """A string of handwritten digits: bottom left corner (x, y) in image pixels (y down), height h."""
    w = h / 1.6                      # stroke unit: a 1 x 1.6 glyph -> height h
    cx = x
    ca, sa = math.cos(rot), math.sin(rot)
    for ch in text:
        jit = (rng.uniform(-0.05, 0.05) * h, rng.uniform(-0.06, 0.06) * h)
        sc = 1.0 + rng.uniform(-0.06, 0.06)
        for stroke in GLYPHS[ch]:
            pts = []
            for gx, gy in stroke:
                px = (gx + gy * slant) * w * sc + rng.uniform(-0.02, 0.02) * h
                py = gy * w * sc + rng.uniform(-0.02, 0.02) * h
                dx, dy = cx - x + px + jit[0], -py + jit[1]
                pts.append((x + dx * ca - dy * sa, y + dx * sa + dy * ca))
            draw.line(pts, fill=color, width=width, joint="curve")
            for p in (pts[0], pts[-1]):
                r = width / 2
                draw.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=color)
        cx += w * (1.15 if ch != "1" else 0.8)


# --- 5 x 7 dot matrix (the analyser's indicator) --------------------------------------------------
DOTS = {
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": ["00000"] * 7,
}


def dotmatrix(draw, text, x, y, pitch, r, fill):
    for i, ch in enumerate(text):
        for row, bits in enumerate(DOTS[ch]):
            for col, b in enumerate(bits):
                if b == "1":
                    cx = x + (i * 6 + col) * pitch
                    cy = y + row * pitch
                    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)


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


# --- back and flap --------------------------------------------------------------------------------
def env_top():
    ppm = 4000                       # px per metre (4 px/mm) in the final image
    W, H = int(L.ENV_IMG_L * ppm), int(L.EW * ppm)
    W3, H3 = W * S, H * S
    k = ppm * S
    rng = random.Random(6301)

    def P(u, v):
        return (u * k, (L.HW - v) * k)

    col = Image.new("RGBA", (W3, H3), (0, 0, 0, 0))
    hgt = Image.new("L", (W3, H3), 128)
    d = ImageDraw.Draw(col)
    dh = ImageDraw.Draw(hgt)
    lw = max(1, int(0.00035 * k))

    # dirt along the edges of the back and at the mouth: a soft band (a blurred mask)
    grime = Image.new("L", (W3, H3), 0)
    dg = ImageDraw.Draw(grime)
    dg.rectangle((0, 0, W3, H3), fill=0)
    edge = int(0.006 * k)
    dg.rectangle((*P(0, L.HW), *P(L.EL, L.HW - 0.004)), fill=90)
    dg.rectangle((*P(0, -L.HW + 0.004), *P(L.EL, -L.HW)), fill=90)
    dg.rectangle((*P(0, L.HW), *P(0.004, -L.HW)), fill=110)
    dg.rectangle((*P(L.EL - 0.010, L.HW), *P(L.EL, -L.HW)), fill=70)
    for cu, cv, r, a in ((L.EL - 0.006, 0.0, 0.020, 120), (L.EL - 0.020, 0.060, 0.013, 70), (L.EL - 0.018, -0.058, 0.014, 80),
                         (0.012, -0.075, 0.014, 60), (0.010, 0.078, 0.012, 55)):
        x, y = P(cu, cv)
        rr = r * k
        dg.ellipse((x - rr, y - rr * 0.7, x + rr, y + rr * 0.7), fill=a)
    # flap: the edge is thumbed, cleaner near the hinge
    tip = L.EL + L.FD
    dg.rectangle((*P(tip - 0.008, L.HW), *P(tip, -L.HW)), fill=85)
    grime = grime.filter(ImageFilter.GaussianBlur(edge))
    nz = noise_img(W3, H3, 0.012 * k, rng, 60, 255)
    grime = ImageChops.multiply(grime, nz)
    dirt = Image.new("RGBA", (W3, H3), (58, 42, 26, 255))
    dirt.putalpha(grime.point(lambda a: int(a * 0.85)))
    col = Image.alpha_composite(col, dirt)
    d = ImageDraw.Draw(col)

    # worn edges: frayed fibres are lighter (a thin band along the outline of the back and the flap)
    wear = Image.new("L", (W3, H3), 0)
    dw = ImageDraw.Draw(wear)
    ew = int(0.0012 * k)
    dw.rectangle((*P(0, L.HW), *P(L.EL, -L.HW)), outline=150, width=ew)
    fl = [P(u, v) for u, v in L.flap_outline(6)]
    dw.line(fl, fill=130, width=ew)
    wear = wear.filter(ImageFilter.GaussianBlur(ew * 0.6))
    wear = ImageChops.multiply(wear, noise_img(W3, H3, 0.004 * k, rng, 40, 255))
    light = Image.new("RGBA", (W3, H3), (214, 186, 146, 255))
    light.putalpha(wear)
    col = Image.alpha_composite(col, light)
    d = ImageDraw.Draw(col)

    # glued bottom: an edge with 45-degree corners - a shadow behind the edge, a light facet, glue
    bf = [P(0.006, -L.HW), P(L.BOT_FLAP, -L.HW + 0.022), P(L.BOT_FLAP, L.HW - 0.022), P(0.006, L.HW)]
    sh = [(x + 0.0006 * k, y) for x, y in bf]
    d.line(sh, fill=(40, 28, 16, 120), width=int(0.0009 * k), joint="curve")
    d.line(bf, fill=(205, 170, 122, 110), width=lw, joint="curve")
    dh.line([(x - 0.0008 * k, y) for x, y in bf], fill=150, width=int(0.0016 * k))
    dh.line(sh, fill=110, width=int(0.0008 * k))
    for i in range(14):                                   # squeezed-out glue: shiny specks
        a = rng.random()
        u = L.BOT_FLAP + 0.0007
        v = -L.HW + 0.024 + a * (L.EW - 0.048)
        x, y = P(u, v)
        rr = rng.uniform(0.6, 1.6) * 0.001 * k
        d.ellipse((x - rr * 0.4, y - rr, x + rr * 0.4, y + rr), fill=(86, 60, 30, 70))

    # seam in the middle: the overlap edge (+v on top), a shadow at -v, glue
    seam_u1 = L.EL - math.sqrt(max(L.NOTCH_R ** 2 - L.SEAM_V ** 2, 0.0))
    a, b = P(L.BOT_FLAP, L.SEAM_V), P(seam_u1, L.SEAM_V)
    wob = [(a[0] + (b[0] - a[0]) * i / 20, a[1] + rng.uniform(-0.25, 0.25) * 0.001 * k) for i in range(21)]
    d.line([(x, y + 0.0006 * k) for x, y in wob], fill=(40, 28, 16, 130), width=int(0.0009 * k))
    d.line(wob, fill=(205, 170, 122, 100), width=lw)
    dh.line([(x, y - 0.0012 * k) for x, y in wob], fill=150, width=int(0.0022 * k))
    dh.line([(x, y + 0.0007 * k) for x, y in wob], fill=112, width=int(0.0008 * k))
    glue = Image.new("L", (W3, H3), 0)
    ImageDraw.Draw(glue).rectangle((a[0], a[1] - 0.0008 * k, b[0], a[1] + L.SEAM_GLUE * k), fill=45)
    glue = glue.filter(ImageFilter.GaussianBlur(0.002 * k))
    gl = Image.new("RGBA", (W3, H3), (92, 66, 36, 255))
    gl.putalpha(ImageChops.multiply(glue, noise_img(W3, H3, 0.008 * k, rng, 80, 255)))
    col = Image.alpha_composite(col, gl)
    d = ImageDraw.Draw(col)

    # creases: across (the envelope was folded in half) and diagonal at the corners; a light and a dark
    # side, relief
    creases = [((0.128, -L.HW), (0.131, -0.02), (0.126, L.HW), 1.0),
               ((0.0, -0.052), (0.020, -0.071), (0.034, -L.HW), 0.8),
               ((0.0, 0.060), (0.014, 0.074), (0.021, L.HW), 0.7),
               ((0.200, -L.HW), (0.214, -0.070), (0.236, -0.058), 0.5),
               ((0.060, 0.030), (0.094, 0.050), (0.118, 0.066), 0.45)]
    for p0, p1, p2, st in creases:
        pts = []
        for i in range(25):
            tt = i / 24
            u = (1 - tt) ** 2 * p0[0] + 2 * (1 - tt) * tt * p1[0] + tt * tt * p2[0]
            v = (1 - tt) ** 2 * p0[1] + 2 * (1 - tt) * tt * p1[1] + tt * tt * p2[1]
            pts.append(P(u + rng.uniform(-0.0003, 0.0003), v))
        d.line([(x - 0.0005 * k, y) for x, y in pts], fill=(210, 178, 132, int(70 * st)), width=lw)
        d.line([(x + 0.0005 * k, y) for x, y in pts], fill=(48, 34, 20, int(80 * st)), width=lw)
        dh.line(pts, fill=128 + int(70 * st), width=int(0.0016 * k))

    # water stains: an uneven ring-shaped rim, slightly darker inside
    cu, cv = 0.050, 0.046
    ring = []
    for i in range(48):
        ang = 2 * math.pi * i / 48
        r = 0.022 * (1 + 0.18 * math.sin(3 * ang + 0.7) + 0.08 * math.sin(7 * ang))
        ring.append(P(cu + r * math.cos(ang), cv + r * 0.8 * math.sin(ang)))
    inside = Image.new("L", (W3, H3), 0)
    ImageDraw.Draw(inside).polygon(ring, fill=28)
    inside = inside.filter(ImageFilter.GaussianBlur(0.003 * k))
    st = Image.new("RGBA", (W3, H3), (96, 70, 40, 255))
    st.putalpha(inside)
    col = Image.alpha_composite(col, st)
    d = ImageDraw.Draw(col)
    d.line(ring + ring[:1], fill=(84, 58, 30, 95), width=int(0.0011 * k), joint="curve")
    d.line([(x + 0.0007 * k, y + 0.0004 * k) for x, y in ring[5:30]], fill=(96, 68, 36, 50), width=lw)

    # fingerprints at the notch: ovals made of thin arcs
    for cu, cv, rot in ((L.EL - 0.016, -0.020, 0.4), (L.EL - 0.013, 0.024, -0.3)):
        x0, y0 = P(cu, cv)
        for j in range(7):
            rr = (0.0016 + j * 0.0011) * k
            box = (x0 - rr, y0 - rr * 1.3, x0 + rr, y0 + rr * 1.3)
            d.arc(box, 200 + rot * 40, 520 + rot * 40, fill=(52, 38, 22, 34), width=lw)

    # flap inside: the back of the eyelet (a ring), the hinge crease
    x, y = P(*L.BTN_FLAP)
    for rr, c, a in ((0.0031, (120, 118, 108), 255), (0.0024, (166, 162, 150), 255), (0.0013, (60, 52, 40), 255)):
        r = rr * k
        d.ellipse((x - r, y - r, x + r, y + r), fill=c + (a,))
    r = 0.0031 * k
    dh.ellipse((x - r, y - r, x + r, y + r), fill=200)
    dh.ellipse((x - 0.0013 * k, y - 0.0013 * k, x + 0.0013 * k, y + 0.0013 * k), fill=100)
    hp = [P(L.EL + 0.0015, v) for v in (-L.HW, L.HW)]
    d.line(hp, fill=(48, 34, 20, 60), width=int(0.0012 * k))
    dh.line(hp, fill=96, width=int(0.0016 * k))

    hgt = hgt.filter(ImageFilter.GaussianBlur(0.0004 * k))
    save(col, (W, H), "env_top.png")
    h = Image.new("RGBA", (W3, H3), (128, 128, 128, 255))
    h.putalpha(hgt)
    save(h, (W, H), "env_top_h.png")


# --- print ----------------------------------------------------------------------------------------
def spectrum(x):
    """Counts in channel x (0..1): the background falls off, Compton edges behind the peaks, five peaks; the
    last one is a narrow unknown line."""
    c = 2.6e4 * math.exp(-x * 5.2) + 3.0e2 * math.exp(-x * 1.4) + 6.0
    peaks = [  # x, height, sigma, Compton edge (x, step)
        (0.050, 1.8e4, 0.006, None),
        (0.150, 2.2e3, 0.020, None),
        (0.400, 4.5e4, 0.011, (0.290, 1.5e3)),
        (0.640, 6.5e3, 0.0135, (0.530, 6.0e2)),
        (0.725, 5.5e3, 0.0145, (0.610, 5.0e2)),
        (0.810, 7.0e2, 0.016, (0.700, 50.0)),
        (0.905, 1.6e3, 0.0075, None),
    ]
    for px, h, sg, ce in peaks:
        c += h * math.exp(-0.5 * ((x - px) / sg) ** 2)
        if ce:
            ex, step = ce
            c += step * (1.0 / (1.0 + math.exp((x - ex) / 0.008))) * min(1.0, x / max(ex, 1e-3) + 0.2)
    return c


def print_img():
    ppm = 8000                       # 8 px/mm
    W, H = int(L.PRINT_L * ppm), int(L.PRINT_W * ppm)
    W3, H3 = W * S, H * S
    k = ppm * S
    rng = random.Random(6302)
    bl, br, bt, bb = L.BORDER

    def P(s, t):
        return (s * k, (L.PRINT_W - t) * k)

    img = Image.new("RGB", (W3, H3), (236, 234, 226))           # white border, slightly cream
    d = ImageDraw.Draw(img)
    x0, y0 = P(bl, L.PRINT_W - bt)
    x1, y1 = P(L.PRINT_L - br, bb)
    # frame: a CRT screen with rounded corners on black
    d.rectangle((x0, y0, x1, y1), fill=(10, 10, 10))
    ins = 0.0025 * k
    scr = Image.new("L", (W3, H3), 0)
    ImageDraw.Draw(scr).rounded_rectangle((x0 + ins, y0 + ins, x1 - ins, y1 - ins), radius=0.012 * k, fill=255)
    glow = Image.new("L", (W3, H3), 0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    ImageDraw.Draw(glow).ellipse((cx - (x1 - x0) * 0.42, cy - (y1 - y0) * 0.40, cx + (x1 - x0) * 0.42,
                                  cy + (y1 - y0) * 0.40), fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(0.02 * k))
    face = Image.new("RGB", (W3, H3), (19, 20, 20))
    face2 = Image.new("RGB", (W3, H3), (34, 35, 35))
    face = Image.composite(face2, face, glow)
    img = Image.composite(face, img, scr)
    d = ImageDraw.Draw(img)

    # scale grid: a frame, logarithmic decades dashed, ticks at the bottom and left without captions
    m = 0.008 * k
    fx0, fy0, fx1, fy1 = x0 + m + 0.004 * k, y0 + m + 0.006 * k, x1 - m, y1 - m - 0.002 * k
    grid = (92, 94, 92)
    lw = max(1, int(0.00022 * k))
    d.rectangle((fx0, fy0, fx1, fy1), outline=grid, width=lw)
    dec = 5.3
    for dcd in range(1, 6):
        y = fy1 - (fy1 - fy0) * dcd / dec
        for xx in range(int(fx0), int(fx1), int(0.002 * k)):
            d.line((xx, y, xx + 0.0008 * k, y), fill=(64, 66, 64), width=lw)
    for i in range(1, 10):
        x = fx0 + (fx1 - fx0) * i / 10
        for yy in range(int(fy0), int(fy1), int(0.002 * k)):
            d.line((x, yy, x, yy + 0.0008 * k), fill=(64, 66, 64), width=lw)
    for i in range(51):
        x = fx0 + (fx1 - fx0) * i / 50
        ln = (0.003 if i % 10 == 0 else 0.0018 if i % 5 == 0 else 0.0011) * k
        d.line((x, fy1, x, fy1 - ln), fill=grid, width=lw)
    for dcd in range(0, 6):
        for mnt in range(1, 10):
            val = dcd + math.log10(mnt)
            if val > dec:
                break
            y = fy1 - (fy1 - fy0) * val / dec
            ln = (0.003 if mnt == 1 else 0.0014) * k
            d.line((fx0, y, fx0 + ln, y), fill=grid, width=lw)

    # curve: a dot per channel, scatter at low counts (Poisson noise), phosphor glow
    trace = Image.new("L", (W3, H3), 0)
    dt = ImageDraw.Draw(trace)
    nch = 420
    roi = (0.905 - 0.022, 0.905 + 0.022)
    for i in range(nch):
        x = (i + 0.5) / nch
        c = spectrum(x)
        c = max(1.0, c + rng.gauss(0, math.sqrt(c)))
        yv = math.log10(c) / dec
        px = fx0 + (fx1 - fx0) * x
        py = fy1 - (fy1 - fy0) * min(yv, 1.0)
        bright = roi[0] <= x <= roi[1]
        r = (0.00034 if bright else 0.00025) * k
        dt.ellipse((px - r, py - r, px + r, py + r), fill=255 if bright else 215)
    halo = trace.filter(ImageFilter.GaussianBlur(0.0007 * k)).point(lambda a: int(a * 0.55))
    trace = ImageChops.lighter(trace, halo)
    # cursor at the unknown peak: a dashed line over the full height
    cxp = fx0 + (fx1 - fx0) * 0.905
    for yy in range(int(fy0), int(fy1), int(0.0016 * k)):
        dt.line((cxp, yy, cxp, yy + 0.0007 * k), fill=170, width=lw)
    # indicator: a row of dot digits at the top right
    pitch = 0.00042 * k
    dotmatrix(dt, "0905 002417", fx1 - 66 * pitch - 0.004 * k, fy0 + 0.004 * k, pitch, pitch * 0.32, 190)
    dotmatrix(dt, "4096", fx0 + 0.006 * k, fy0 + 0.004 * k, pitch, pitch * 0.32, 150)
    lum = Image.new("RGB", (W3, H3), (232, 236, 232))
    img = Image.composite(lum, img, trace)

    # photo paper grain on the frame
    grain = noise_img(W3, H3, 0.0006 * k, rng, 0, 255)
    gimg = Image.new("RGB", (W3, H3), (0, 0, 0))
    mask = Image.new("L", (W3, H3), 0)
    ImageDraw.Draw(mask).rectangle((x0, y0, x1, y1), fill=14)
    img = Image.composite(gimg, img, ImageChops.multiply(mask, grain.point(lambda a: 255 if a > 140 else 0)))
    d = ImageDraw.Draw(img)

    # pencil on the bottom border: the sample number and a "?" with an arrow under the unknown peak
    pencil = (92, 92, 98)
    hw = max(1, int(0.00028 * k))
    handwrite(d, "31-118", *P(0.104, 0.0018), 0.0045 * k, pencil, hw, rng)
    ax = fx0 + (fx1 - fx0) * 0.905
    ay0, ay1 = P(0, 0.0012)[1], P(0, bb - 0.0009)[1]          # arrow up towards the peak
    tipx = ax - 0.0008 * k
    d.line((ax - 0.0042 * k, ay0, tipx, ay1), fill=pencil, width=hw)
    d.line((tipx, ay1, tipx - 0.0019 * k, ay1 + 0.0009 * k), fill=pencil, width=hw)
    d.line((tipx, ay1, tipx + 0.0003 * k, ay1 + 0.0020 * k), fill=pencil, width=hw)
    handwrite(d, "?", ax + 0.0008 * k, P(0, 0.0014)[1], 0.0052 * k, pencil, hw, rng)

    # the border has yellowed at the edges, rubbed corners
    yel = Image.new("L", (W3, H3), 0)
    ImageDraw.Draw(yel).rectangle((0, 0, W3, H3), outline=255, width=int(0.0016 * k))
    yel = yel.filter(ImageFilter.GaussianBlur(0.0012 * k)).point(lambda a: int(a * 0.35))
    img = Image.composite(Image.new("RGB", (W3, H3), (214, 204, 178)), img, yel)
    save(img, (W, H), "print.png")


# --- tag ------------------------------------------------------------------------------------------
def label_img():
    ppm = 12000
    lw_, lh_ = L.LABEL_SIZE
    W, H = int(lw_ * ppm), int(lh_ * ppm)
    W3, H3 = W * S, H * S
    k = ppm * S
    rng = random.Random(6303)
    img = Image.new("RGB", (W3, H3), (236, 230, 210))
    d = ImageDraw.Draw(img)
    stripe = 0.007 * k
    d.rectangle((0, 0, stripe, H3), fill=(226, 184, 38))
    ink = (58, 62, 80)
    lw = max(1, int(0.00022 * k))
    m = 0.002 * k
    d.rectangle((stripe + m, m, W3 - m, H3 - m), outline=ink, width=lw)
    d.rectangle((stripe + m + 0.0006 * k, m + 0.0006 * k, W3 - m - 0.0006 * k, H3 - m - 0.0006 * k), outline=ink,
                width=max(1, lw // 2))
    rows = 4
    top, bot = m + 0.0012 * k, H3 - m - 0.0012 * k
    for i in range(1, rows):
        y = top + (bot - top) * i / rows
        d.line((stripe + m, y, W3 - m, y), fill=ink, width=lw)
    for i in range(rows):                                  # field number: an empty small square on the left
        y = top + (bot - top) * (i + 0.5) / rows
        s = 0.0022 * k
        d.rectangle((stripe + m + 0.0018 * k, y - s / 2, stripe + m + 0.0018 * k + s, y + s / 2), outline=ink, width=lw)
    d.line((stripe + 0.034 * k, top, stripe + 0.034 * k, top + (bot - top) / rows), fill=ink, width=lw)
    d.line((stripe + 0.030 * k, top + (bot - top) * 2 / rows, stripe + 0.030 * k, top + (bot - top) * 3 / rows),
           fill=ink, width=lw)
    pen = (38, 58, 138)
    pw = max(1, int(0.00035 * k))
    handwrite(d, "31-118", stripe + 0.036 * k, top + (bot - top) * 0.82 / rows, 0.0062 * k, pen, pw, rng, rot=-0.02)
    handwrite(d, "4", stripe + 0.033 * k, top + (bot - top) * 2.82 / rows, 0.0058 * k, pen, pw, rng)
    d.line((stripe + 0.011 * k, top + (bot - top) * 3.55 / rows, stripe + 0.024 * k, top + (bot - top) * 3.5 / rows),
           fill=pen, width=pw)

    # violet stamp: a double ring and a trefoil, an uneven impression
    st = Image.new("L", (W3, H3), 0)
    ds = ImageDraw.Draw(st)
    cx, cy, R = W3 - 0.016 * k, H3 * 0.55, 0.0098 * k
    ds.ellipse((cx - R, cy - R, cx + R, cy + R), outline=255, width=int(0.0009 * k))
    r2 = R - 0.0016 * k
    ds.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), outline=255, width=int(0.00045 * k))
    rc = 0.0011 * k
    ds.ellipse((cx - rc, cy - rc, cx + rc, cy + rc), fill=255)
    rot = math.radians(17)
    ri, ro = 0.0017 * k, 0.0068 * k
    for j in range(3):
        a0 = rot + math.radians(90 + 120 * j - 30)
        a1 = rot + math.radians(90 + 120 * j + 30)
        pts = [(cx + ri * math.cos(a0 + (a1 - a0) * q / 8), cy - ri * math.sin(a0 + (a1 - a0) * q / 8)) for q in range(9)]
        pts += [(cx + ro * math.cos(a1 - (a1 - a0) * q / 8), cy - ro * math.sin(a1 - (a1 - a0) * q / 8)) for q in range(9)]
        ds.polygon(pts, fill=255)
    patchy = noise_img(W3, H3, 0.0012 * k, rng, 90, 255)
    fade = Image.new("L", (W3, H3), 0)
    ImageDraw.Draw(fade).ellipse((cx - R * 2.2, cy - R * 1.2, cx + R * 0.6, cy + R * 2.4), fill=255)
    fade = fade.filter(ImageFilter.GaussianBlur(R * 0.8)).point(lambda a: 120 + a // 2)
    st = ImageChops.multiply(ImageChops.multiply(st, patchy), fade).filter(ImageFilter.GaussianBlur(0.00012 * k))
    img = Image.composite(Image.new("RGB", (W3, H3), (104, 62, 142)), img, st.point(lambda a: int(a * 0.82)))

    # the tag edges are slightly dirtier
    e = Image.new("L", (W3, H3), 0)
    ImageDraw.Draw(e).rectangle((0, 0, W3, H3), outline=255, width=int(0.0012 * k))
    e = e.filter(ImageFilter.GaussianBlur(0.001 * k)).point(lambda a: int(a * 0.3))
    img = Image.composite(Image.new("RGB", (W3, H3), (150, 138, 112)), img, e)
    save(img, (W, H), "label.png")


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    env_top()
    print_img()
    label_img()
