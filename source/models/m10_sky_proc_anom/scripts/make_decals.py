"""Decals for the washing-machine centrifuge (system Python + Pillow): the knob scales of the Sibir
panel (dots and digits, as in the panel photo, no lettering), the scale of the M42100 microammeter
of the detector unit in two states ("off" - unlit, "work" - backlit; the needle is in the model, bone
ozl_meter), the signs of the unit's front panel (the knob scale, toggle marks, lamp signs, the probe
socket ring), a "high voltage" sign (a lightning bolt in a triangle), a yellow-black warning stripe
on the crate, signs on the dosimeter cover (radiation, buttons, grille) and the dosimeter display -
an own texture (section lcd): "off" is empty, "work" is 8 frames with readings in seven-segment
digits. No letters. Where things are - m10_layout.py (shared with build_m10.py).

    python make_decals.py      -> ../work/decal_*.png, ../work/lcd_*.png
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m10_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
INK = (30, 32, 34, 255)

# instrument scale: the window and the needle axis are as in build_m10 (m10_layout)
DIAL_W, DIAL_H, PIVOT_DZ, ARC_R = L.DIAL_W, L.DIAL_H, L.PIVOT_DZ, L.ARC_R


def font(px):
    for name in ("arialbd.ttf", "arial.ttf"):
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


def make_panel(name, w):
    """Scales of the three knobs: "wash" 0-5, "spin" 0-3, "mode" 1-2 - dots along an arc from the top
    clockwise and digits, a dash at zero (panel photo). The background is transparent: the panel paint
    is under it."""
    h = int(round(w * L.PANEL_H / L.PANEL_W))
    W, H = w * S, h * S
    k = W / L.PANEL_W                                     # px per metre
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font(int(0.016 * k))
    for (fr, marks) in zip(L.KNOB_FR, ((0, 1, 2, 3, 4, 5), (0, 1, 2, 3), (1, 2))):
        cx, cy = fr * W, H / 2
        n = len(marks)
        for i, mk in enumerate(marks):
            a = math.radians(100.0 - (115.0 if n > 2 else 60.0) * i / max(1, n - 1))
            rd, rt = (L.WELL_R + 0.006) * k, (L.WELL_R + 0.017) * k
            px, py = cx + rd * math.cos(a), cy - rd * math.sin(a)
            d.ellipse([px - 0.0018 * k, py - 0.0018 * k, px + 0.0018 * k, py + 0.0018 * k], fill=INK)
            d.text((cx + rt * math.cos(a), cy - rt * math.sin(a)), str(mk), fill=INK, font=f, anchor="mm")
            if mk == 0:
                q = (cx + rd * math.cos(a + 0.22), cy - rd * math.sin(a + 0.22))
                d.line([q, (cx + rd * math.cos(a + 0.42), cy - rd * math.sin(a + 0.42))], fill=INK, width=int(0.003 * k))
        # underline under the knob instead of a name
        d.line([(cx - 0.03 * k, cy + (L.WELL_R + 0.012) * k), (cx + 0.03 * k, cy + (L.WELL_R + 0.012) * k)], fill=INK,
               width=int(0.0022 * k))
    save(img, (w, h), name)


def make_dial(name, w, bg, ink, glow=None):
    """M42100 scale: a 90-degree arc about the needle axis (slightly below the window), divisions, digits
    0-100, a mirror strip. There is no needle - it is in the model."""
    h = int(round(w * DIAL_H / DIAL_W))
    W, H = w * S, h * S
    k = W / DIAL_W
    img = Image.new("RGBA", (W, H), bg)
    if glow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([W * 0.05, H * 0.05, W * 0.95, H * 1.4], fill=glow)
        img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(H * 0.12)))
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, H + PIVOT_DZ * k
    R = ARC_R * k

    def at(frac, rr):
        a = math.radians(135.0 - 90.0 * frac)
        return cx + rr * math.cos(a), cy - rr * math.sin(a)
    d.arc([cx - R, cy - R, cx + R, cy + R], -135, -45, fill=ink, width=S * 2)
    for i in range(51):
        big, mid = i % 10 == 0, i % 5 == 0
        d.line([at(i / 50, R), at(i / 50, R * (1.12 if big else (1.08 if mid else 1.05)))], fill=ink,
               width=S * (3 if big else 1))
    f = font(int(0.0055 * k))
    for i in range(6):
        d.text(at(i / 5, R * 1.24), str(i * 20), fill=ink, font=f, anchor="mm")
    d.arc([cx - R * 0.90, cy - R * 0.90, cx + R * 0.90, cy + R * 0.90], -135, -45, fill=(150, 154, 158, 255), width=S * 4)
    d.arc([cx - R * 0.84, cy - R * 0.84, cx + R * 0.84, cy + R * 0.84], -135 + 90 * 0.8, -45,
          fill=(170, 40, 30, 255), width=S * 3)
    d.rectangle([0, 0, W - 1, H - 1], outline=(30, 30, 30, 255), width=S * 2)
    save(img, (w, h), name)


def trefoil(d, cx, cy, r, fill, bg=None):
    """Radiation sign: three 60-degree blades and a dot in the centre."""
    if bg is not None:
        d.ellipse([cx - r * 1.12, cy - r * 1.12, cx + r * 1.12, cy + r * 1.12], fill=bg)
    for k in range(3):
        a0 = -90.0 + 120.0 * k - 30.0
        d.pieslice([cx - r, cy - r, cx + r, cy + r], a0, a0 + 60.0, fill=fill)
    d.ellipse([cx - r * 0.30, cy - r * 0.30, cx + r * 0.30, cy + r * 0.30], fill=bg or (0, 0, 0, 0))
    d.ellipse([cx - r * 0.20, cy - r * 0.20, cx + r * 0.20, cy + r * 0.20], fill=fill)


def make_detpanel(name, px_per_m=4000):
    """Front panel of the detector unit (a transparent background over light aluminium): a frame along the
    edge, the sensitivity knob scale 0-10 (270 degrees), toggle marks (a bar is on, a circle is off),
    under the lamps a wave (power) and a radiation sign (count), a ring around the probe socket; there
    are no screw marks - the screws are in the model. Coordinates are from the top left corner of the
    panel (x right, z down)."""
    x0, x1, z0, z1 = L.PLATE
    w, h = int((x1 - x0) * px_per_m), int((z1 - z0) * px_per_m)
    W, H = w * S, h * S
    k = W / (x1 - x0)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def p(x, z):
        return (x - x0) * k, (z1 - z) * k
    ink = (34, 34, 36, 255)
    m = 0.0035 * k
    d.rounded_rectangle([m, m, W - m, H - m], radius=0.004 * k, outline=ink, width=int(0.0006 * k))
    # knob scale
    cx, cy = p(*L.KNOB)
    f = font(int(0.0042 * k))
    for i in range(11):
        a = math.radians(225.0 - 27.0 * i)
        big = i % 5 == 0
        r0, r1 = 0.0195 * k, (0.0245 if big else 0.0225) * k
        d.line([(cx + r0 * math.cos(a), cy - r0 * math.sin(a)), (cx + r1 * math.cos(a), cy - r1 * math.sin(a))], fill=ink,
               width=int((0.0009 if big else 0.0006) * k))
        if big:
            rt = 0.0295 * k
            d.text((cx + rt * math.cos(a), cy - rt * math.sin(a)), str(i), fill=ink, font=f, anchor="mm")
    # toggle: a bar at the top (on), a circle at the bottom (off)
    tx, tz = p(*L.TOGGLE)
    d.line([(tx, tz - 0.0125 * k), (tx, tz - 0.0175 * k)], fill=ink, width=int(0.0010 * k))
    rr = 0.0024 * k
    d.ellipse([tx - rr, tz + 0.015 * k - rr, tx + rr, tz + 0.015 * k + rr], outline=ink, width=int(0.0008 * k))
    # under the lamps: a wave (power) and a radiation sign (count)
    gx, gz = p(*L.LAMP_G)
    wave = [(gx - 0.005 * k + 0.010 * k * i / 24, gz + 0.0155 * k - 0.0018 * k * math.sin(2 * math.pi * i / 24))
            for i in range(25)]
    d.line(wave, fill=ink, width=int(0.0008 * k))
    rx, rz = p(*L.LAMP_R)
    trefoil(d, rx, rz + 0.0160 * k, 0.0042 * k, ink)
    # a ring around the probe socket and an arrow to it
    bx, bz = p(*L.BNC)
    rr = 0.0118 * k
    d.ellipse([bx - rr, bz - rr, bx + rr, bz + rr], outline=ink, width=int(0.0007 * k))
    d.polygon([(bx, bz + 0.0145 * k), (bx - 0.0022 * k, bz + 0.0185 * k), (bx + 0.0022 * k, bz + 0.0185 * k)], fill=ink)
    save(img, (w, h), name)


def make_dos(name, px_per_m=4000):
    """Dosimeter cover (a transparent background over dark plastic): a radiation sign at the left end, a
    display frame, button rings and signs by them (a triangle, a dot), a beeper grille frame, a dividing
    line. The top of the image is toward the back edge (+Y): the dosimeter lies facing the person."""
    x, y, ln, wd, _ = L.DOS
    x0, y1 = x - ln / 2, y + wd / 2
    w, h = int(ln * px_per_m), int(wd * px_per_m)
    W, H = w * S, h * S
    k = W / ln
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def p(xx, yy):
        return (xx - x0) * k, (y1 - yy) * k
    ink = (196, 194, 184, 255)
    tx, ty = p(x - ln / 2 + 0.0125, y)
    trefoil(d, tx, ty, 0.0050 * k, (34, 30, 26, 255), bg=(220, 186, 40, 255))
    lx, ly = p(L.LCD[0], L.LCD[1])
    d.rounded_rectangle([lx - 0.0335 * k, ly - 0.0170 * k, lx + 0.0335 * k, ly + 0.0170 * k], radius=0.003 * k,
                        outline=ink, width=int(0.0006 * k))
    for i, (bx, by) in enumerate(L.DOS_BTN):
        cx, cy = p(bx, by)
        rr = 0.0068 * k
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=ink, width=int(0.0006 * k))
        sx = cx + 0.0105 * k
        if i == 0:
            d.polygon([(sx, cy - 0.0022 * k), (sx - 0.0022 * k, cy + 0.0016 * k), (sx + 0.0022 * k, cy + 0.0016 * k)],
                      fill=ink)
        else:
            d.ellipse([sx - 0.0016 * k, cy - 0.0016 * k, sx + 0.0016 * k, cy + 0.0016 * k], fill=ink)
    gx0, gx1, gy0, gy1 = L.DOS_GRILLE
    a, b = p(gx0, gy1), p(gx1, gy0)
    d.rounded_rectangle([a[0] - 0.003 * k, a[1] - 0.003 * k, b[0] + 0.003 * k, b[1] + 0.003 * k], radius=0.003 * k,
                        outline=ink, width=int(0.0006 * k))
    sx = (p(L.LCD[0] + 0.031, 0)[0] + p(L.DOS_BTN[0][0] - 0.0068, 0)[0]) / 2
    d.line([(sx, 0.012 * k), (sx, H - 0.012 * k)], fill=ink, width=int(0.0005 * k))
    save(img, (w, h), name)


def make_bolt(name, px):
    """Sign "high voltage": a black lightning bolt in a yellow triangle with a black border."""
    W = px * S
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    tri = [(W / 2, W * 0.06), (W * 0.96, W * 0.90), (W * 0.04, W * 0.90)]
    d.polygon(tri, fill=(22, 22, 22, 255))
    inner = [(W / 2, W * 0.17), (W * 0.86, W * 0.84), (W * 0.14, W * 0.84)]
    d.polygon(inner, fill=(232, 190, 30, 255))
    bolt = [(W * 0.55, W * 0.30), (W * 0.38, W * 0.58), (W * 0.50, W * 0.58), (W * 0.43, W * 0.80),
            (W * 0.63, W * 0.50), (W * 0.51, W * 0.50), (W * 0.60, W * 0.30)]
    d.polygon(bolt, fill=(22, 22, 22, 255))
    save(img, (px, px), name)


def make_stripes(name, w, h):
    """Yellow-black warning stripe, diagonal, paint on wood with scuffs."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (226, 182, 34, 240))
    d = ImageDraw.Draw(img)
    step = H * 1.4
    x = -H
    while x < W + H:
        d.polygon([(x, H), (x + step / 2, H), (x + step / 2 + H, 0), (x + H, 0)], fill=(24, 24, 24, 240))
        x += step
    save(img, (w, h), name)


# --- dosimeter display: seven-segment digits -------------------------------------------------
SEGS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc", "7": "abc",
        "8": "abcdefg", "9": "abcdfg"}


def seg_polys(x, y, w, h, t, slant):
    """Segments a..g of a digit in the frame (x, y, w, h), thickness t; slant shifts the top to the right (a
    fraction of h)."""
    def hor(cx, cy, ln):
        return [(cx - ln / 2, cy), (cx - ln / 2 + t / 2, cy - t / 2), (cx + ln / 2 - t / 2, cy - t / 2), (cx + ln / 2, cy),
                (cx + ln / 2 - t / 2, cy + t / 2), (cx - ln / 2 + t / 2, cy + t / 2)]

    def ver(cx, cy, ln):
        return [(cx, cy - ln / 2), (cx + t / 2, cy - ln / 2 + t / 2), (cx + t / 2, cy + ln / 2 - t / 2), (cx, cy + ln / 2),
                (cx - t / 2, cy + ln / 2 - t / 2), (cx - t / 2, cy - ln / 2 + t / 2)]
    gap = t * 0.18
    lh, lv = w - t - 2 * gap, h / 2 - t / 2 - 2 * gap
    polys = {"a": hor(x + w / 2, y + t / 2, lh), "g": hor(x + w / 2, y + h / 2, lh), "d": hor(x + w / 2, y + h - t / 2, lh),
             "f": ver(x + t / 2, y + h / 4 + t / 4, lv), "b": ver(x + w - t / 2, y + h / 4 + t / 4, lv),
             "e": ver(x + t / 2, y + 3 * h / 4 - t / 4, lv), "c": ver(x + w - t / 2, y + 3 * h / 4 - t / 4, lv)}
    return {k: [(px + (y + h - py) * slant, py) for px, py in v] for k, v in polys.items()}


def make_lcd(name, text, px_per_m=8000, ghost=False):
    """RKSB-104 display (52 x 22 mm): a grey-green field, four seven-segment digit positions with a decimal
    point; ghost is the switched-off display: only the barely visible segments of "8.888"."""
    w, h = int(L.LCD[2] * px_per_m), int(L.LCD[3] * px_per_m)
    W, H = w * S, h * S
    bg = (140, 150, 126)
    img = Image.new("RGBA", (W, H), bg + (255,))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H * 0.25], fill=(0, 0, 0, 30))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(H * 0.15)))
    d = ImageDraw.Draw(img)
    on = (42, 46, 40, 255)
    off = (128, 138, 115, 255)
    dw, dh, t = W * 0.17, H * 0.62, H * 0.085
    x = W * 0.12
    y = H * 0.19
    chars = list(text.replace(".", ""))
    dot_after = text.index(".") - 1 if "." in text else -1
    for i in range(4):
        ch = chars[i] if i < len(chars) else " "
        polys = seg_polys(x, y, dw, dh, t, 0.08)
        for sname, poly in polys.items():
            lit = (not ghost) and ch in SEGS and sname in SEGS[ch]
            if lit or ghost:
                d.polygon(poly, fill=on if lit else off)
        if i == dot_after or (ghost and i == 0):
            r = t * 0.55
            cxp, cyp = x + dw + t * 0.75, y + dh - r
            d.ellipse([cxp - r, cyp - r, cxp + r, cyp + r], fill=off if ghost else on)
        x += dw + W * 0.035
    d.rectangle([0, 0, W - 1, H - 1], outline=(96, 104, 88, 255), width=S * 2)
    save(img, (w, h), name)


if __name__ == "__main__":
    make_panel("decal_panel.png", 1024)
    make_dial("decal_dial_off.png", 272, (196, 192, 176, 255), (40, 40, 38, 255))
    make_dial("decal_dial_on.png", 272, (252, 238, 196, 255), (26, 24, 20, 255), glow=(255, 250, 220, 120))
    make_detpanel("decal_detpanel.png")
    make_dos("decal_dos.png")
    make_bolt("decal_bolt.png", 192)
    make_stripes("decal_stripes.png", 512, 96)
    make_lcd("lcd_off.png", "8888", ghost=True)
    # work: dose rate readings creep up and back while the sample spins in the drum
    for i, v in enumerate(("0.124", "0.151", "0.137", "0.192", "0.264", "0.331", "0.287", "0.213")):
        make_lcd("lcd_f%02d.png" % i, v)
