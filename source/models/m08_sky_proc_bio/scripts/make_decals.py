"""Decals for the field autoclave (system Python + Pillow): the cooker gauge dial (without the needle -
the needle is in the model, bone ozl_needle), the KFK-2 photocolorimeter scale in two states ("off" -
an unlit window, "work" - backlight; the needle is also in the model, bone ozl_meter), panel outlines
and digits at the knobs on the KFK-2 face and the hotplate, a stencilled biohazard sign on the
crate, an empty inventory tag. No letters: only digits, ticks and a sign. Where things are -
layout.py.

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
INK = (24, 24, 24, 255)
RED = (176, 32, 26, 255)
PX_M = 2400                             # pixels per metre for the face decals (before downscaling)


def font(px):
    for name in ("arial.ttf", "consola.ttf"):
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def make_gauge(name, px):
    """Gauge dial 0-4 kgf/cm2: a white field, a 270-degree scale from the bottom left clockwise, a red
    sector at the end, digits, two dial screws. Zero is at 225 degrees (left-down): that is where the
    model needle points at phase 0."""
    W = px * S
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c, r = W / 2, W * 0.47
    d.ellipse([c - r, c - r, c + r, c + r], fill=(236, 233, 222, 255))
    rs = r * 0.80

    def at(frac, rr):
        a = math.radians(L.GAUGE_ZERO - L.GAUGE_SPAN * frac)      # clockwise from the bottom left
        return c + math.cos(a) * rr, c - math.sin(a) * rr
    # red sector: the last 12 % of the scale
    for k in range(40):
        f = 0.88 + 0.12 * k / 39
        d.line([at(f, rs * 0.96), at(f, rs * 1.10)], fill=RED, width=int(W * 0.02))
    n = 40
    for i in range(n + 1):
        big = i % 10 == 0
        mid = i % 5 == 0
        d.line([at(i / n, rs), at(i / n, rs * (1.16 if big else (1.11 if mid else 1.07)))], fill=INK,
               width=int(W * (0.014 if big else 0.007)))
    f = font(int(W * 0.10))
    for k in range(5):
        d.text(at(k / 4, rs * 0.76), str(k), fill=INK, font=f, anchor="mm")
    for sx in (-1, 1):                                           # dial screws
        x, y = c + sx * r * 0.42, c + r * 0.50
        d.ellipse([x - W * 0.018, y - W * 0.018, x + W * 0.018, y + W * 0.018], fill=(150, 150, 146, 255))
        d.line([x - W * 0.012, y, x + W * 0.012, y], fill=(90, 90, 88, 255), width=int(W * 0.005))
    d.ellipse([c - r, c - r, c + r, c + r], outline=(150, 150, 146, 255), width=int(W * 0.012))
    save(img, (px, px), name)


def make_scale(name, w, h, bg, ink, glow=None):
    """KFK-2 scale window: a transmittance arc 0-100 with digits and below it an optical density arc (red),
    a mirror strip. There is no needle - it is in the model (bone ozl_meter, the axis is in layout)."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), bg)
    d = ImageDraw.Draw(img)
    r = W * L.SCALE_R
    cx, cy = W / 2, H * L.SCALE_TOP + r
    a0, a1 = L.SCALE_A

    def at(frac, rr):
        a = math.radians(a0 + (a1 - a0) * frac)
        return cx + math.cos(a) * rr, cy + math.sin(a) * rr
    if glow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([W * 0.1, -H * 0.4, W * 0.9, H * 1.1], fill=glow)
        img = Image.alpha_composite(img, sh)
        d = ImageDraw.Draw(img)
    d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=ink, width=int(H * 0.012))
    n = 50
    for i in range(n + 1):
        big = i % 5 == 0
        d.line([at(i / n, r), at(i / n, r * (1.07 if big else 1.04))], fill=ink, width=int(H * (0.014 if big else 0.007)))
    f = font(int(H * 0.11))
    for k in range(11):
        d.text(at(k / 10, r * 1.13), str(k * 10), fill=ink, font=f, anchor="mm")
    # optical density scale: uneven ticks below the arc, red
    r2 = r * 0.90
    d.arc([cx - r2, cy - r2, cx + r2, cy + r2], a0, a1, fill=RED, width=int(H * 0.010))
    for k in range(1, 20):
        frac = 10 ** (-k / 10.0)                           # D = k/10 -> T = 10^-D
        d.line([at(frac, r2), at(frac, r2 * 0.96)], fill=RED, width=int(H * 0.008))
    # mirror strip under the needle
    d.arc([cx - r * 0.97, cy - r * 0.97, cx + r * 0.97, cy + r * 0.97], a0, a1, fill=(150, 156, 160, 255), width=int(H * 0.02))
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 44, 50, 255), width=S * 3)
    save(img, (w, h), name)


def make_biohazard(name, px):
    """Biohazard sign by stencil: black paint, no yellow field (Clear Sky crate)."""
    W = px * S
    sym = Image.new("L", (W, W), 0)
    s = ImageDraw.Draw(sym)
    cx, cy, r = W / 2, W * 0.52, W * 0.21
    for a in (90, 210, 330):
        ox, oy = cx + math.cos(math.radians(a)) * r * 0.62, cy - math.sin(math.radians(a)) * r * 0.62
        s.ellipse([ox - r, oy - r, ox + r, oy + r], fill=255)
    for a in (90, 210, 330):
        ox, oy = cx + math.cos(math.radians(a)) * r * 0.86, cy - math.sin(math.radians(a)) * r * 0.86
        s.ellipse([ox - r * 0.62, oy - r * 0.62, ox + r * 0.62, oy + r * 0.62], fill=0)
    s.ellipse([cx - r * 0.30, cy - r * 0.30, cx + r * 0.30, cy + r * 0.30], fill=0)
    s.ellipse([cx - r * 1.05, cy - r * 1.05, cx + r * 1.05, cy + r * 1.05], outline=255, width=int(r * 0.16))
    for a in (90, 210, 330):
        ox, oy = cx + math.cos(math.radians(a)) * r * 1.0, cy - math.sin(math.radians(a)) * r * 1.0
        s.ellipse([ox - r * 0.13, oy - r * 0.13, ox + r * 0.13, oy + r * 0.13], fill=0)
    # stencil bridges: thin gaps along three axes
    for a in (30, 150, 270):
        x1, y1 = cx + math.cos(math.radians(a)) * r * 1.3, cy - math.sin(math.radians(a)) * r * 1.3
        s.line([(cx, cy), (x1, y1)], fill=0, width=int(r * 0.05))
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    img.paste((26, 26, 28, 230), (0, 0), sym)
    save(img, (px, px), name)


def make_tag(name, w, h):
    """Inventory tag without text: an aluminium plate, two rivets, a stamped frame."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (178, 182, 184, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([S * 6, S * 6, W - S * 6, H - S * 6], outline=(120, 124, 128, 255), width=S * 2)
    for x in (S * 14, W - S * 14):
        d.ellipse([x - S * 5, H / 2 - S * 5, x + S * 5, H / 2 + S * 5], fill=(96, 98, 100, 255))
    for i in range(5):
        y = H * (0.3 + 0.1 * i)
        d.line([(W * 0.22, y), (W * 0.78, y)], fill=(150, 154, 156, 255), width=S)
    save(img, (w, h), name)


class Face:
    """Picture on a face rectangle (x0, x1, z0, z1) in model metres: points are in model coordinates."""

    def __init__(self, rect, px_m=PX_M):
        self.x0, self.x1, self.z0, self.z1 = rect
        self.W = int(round((self.x1 - self.x0) * px_m)) * S
        self.H = int(round((self.z1 - self.z0) * px_m)) * S
        self.size = (self.W // S, self.H // S)
        self.img = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.m = self.W / (self.x1 - self.x0)            # pixels (supersampled) per metre

    def p(self, x, z):
        return (x - self.x0) * self.m, (self.z1 - z) * self.m

    def mm(self, v):
        return v * 0.001 * self.m


def arc_marks(fc, cx, cz, r, a_from, a_to, n, tick, width, fill):
    """Ticks along an arc around a knob (angles are from +x counter-clockwise, like a clock in reverse)."""
    for i in range(n):
        a = math.radians(a_from + (a_to - a_from) * i / max(1, n - 1))
        p0 = fc.p(cx + math.cos(a) * r, cz + math.sin(a) * r)
        p1 = fc.p(cx + math.cos(a) * (r + tick), cz + math.sin(a) * (r + tick))
        fc.d.line([p0, p1], fill=fill, width=width)


def labels(fc, cx, cz, r, items, px, a_from, a_to):
    """Digits along an arc around a knob: items - [(text, colour)]."""
    f = font(int(fc.mm(px)))
    n = len(items)
    for i, (txt, col) in enumerate(items):
        a = math.radians(a_from + (a_to - a_from) * i / max(1, n - 1))
        fc.d.text(fc.p(cx + math.cos(a) * r, cz + math.sin(a) * r), txt, fill=col, font=f, anchor="mm")


def rounded(fc, x0, x1, z0, z1, rad, width, fill):
    a, b = fc.p(x0, z1), fc.p(x1, z0)
    fc.d.rounded_rectangle([a, b], radius=fc.mm(rad * 1000), outline=fill, width=width)


def make_kfk_panels(name_l, name_r):
    """Panel outlines on the KFK-2 face (as in the photo, no lettering): at the left the filter knob,
    wavelength digits along an arc (long ones in red), a socket for the indicator above it; at the right
    a shaped outline, the sensitivity knob with digits 1-3, arcs above the small "set 100" knobs."""
    ink = (52, 54, 58, 255)
    lw = int(S * 2.2)
    fl = Face(L.PANEL_L)
    x0, x1, z0, z1 = L.PANEL_L
    rounded(fl, x0 + 0.002, x1 - 0.002, z0 + 0.002, z1 - 0.002, 0.012, lw, ink)
    kx, kz, kr, _ = L.KNOBS[0]
    waves = [("364", ink), ("400", ink), ("440", ink), ("490", ink), ("540", ink), ("590", RED), ("670", RED),
             ("750", RED)]
    labels(fl, kx, kz, kr + 0.017, waves, 6.0, 215.0, -35.0)
    arc_marks(fl, kx, kz, kr + 0.004, 215.0, -35.0, 8, 0.004, int(S * 1.6), ink)
    lx, lz = L.KLAMP
    fl.d.ellipse([fl.p(lx - 0.010, lz + 0.010), fl.p(lx + 0.010, lz - 0.010)], outline=ink, width=lw)
    save(fl.img, fl.size, name_l)

    fr = Face(L.PANEL_R)
    x0, x1, z0, z1 = L.PANEL_R
    # shaped outline: a rectangle with rounding and a "hump" around the upper small knob
    rounded(fr, x0 + 0.002, x1 - 0.002, z0 + 0.002, z1 - 0.030, 0.012, lw, ink)
    hx, hz, hr, _ = L.KNOBS[2]
    fr.d.arc([fr.p(hx - hr - 0.009, hz + hr + 0.009), fr.p(hx + hr + 0.009, hz - hr - 0.009)], 200, 340, fill=ink,
             width=lw)
    sx, sz, sr, _ = L.KNOBS[1]
    labels(fr, sx, sz, sr + 0.014, [("1", ink), ("2", ink), ("3", ink)], 6.5, 130.0, 50.0)
    arc_marks(fr, sx, sz, sr + 0.004, 130.0, 50.0, 3, 0.004, int(S * 1.6), ink)
    for k in (2, 3):                                          # arcs above the small knobs
        mx, mz, mr, _ = L.KNOBS[k]
        fr.d.arc([fr.p(mx - mr - 0.006, mz + mr + 0.006), fr.p(mx + mr + 0.006, mz - mr - 0.006)], 200, 340,
                 fill=ink, width=int(S * 1.6))
    save(fr.img, fr.size, name_r)


def make_plate_front(name):
    """Hotplate face: step digits 0-3 along an arc and ticks at each knob, a white rim at the lamp."""
    x0, x1 = L.XP - L.PW / 2, L.XP + L.PW / 2
    fc = Face((x0, x1, L.ZP0, L.ZPT))
    ink = (40, 38, 34, 255)
    for bx, _ in L.BURN:
        labels(fc, bx, L.PKNOB_Z, L.PKNOB_R + 0.010, [("0", ink), ("1", ink), ("2", ink), ("3", ink)], 6.0, 150.0, 30.0)
        arc_marks(fc, bx, L.PKNOB_Z, L.PKNOB_R + 0.002, 150.0, 30.0, 4, 0.003, int(S * 1.6), ink)
    px, pz = L.PILOT
    fc.d.ellipse([fc.p(px - 0.010, pz + 0.010), fc.p(px + 0.010, pz - 0.010)], outline=ink, width=int(S * 1.6))
    save(fc.img, fc.size, name)


if __name__ == "__main__":
    make_gauge("decal_gauge.png", 256)
    make_scale("decal_scale_off.png", 320, 112, (150, 150, 140, 255), (40, 40, 40, 255))
    make_scale("decal_scale_on.png", 320, 112, (246, 240, 214, 255), INK, glow=(255, 250, 225, 90))
    make_biohazard("decal_biohazard.png", 256)
    make_tag("decal_tag.png", 160, 64)
    make_kfk_panels("decal_kfk_panel_l.png", "decal_kfk_panel_r.png")
    make_plate_front("decal_plate_front.png")
