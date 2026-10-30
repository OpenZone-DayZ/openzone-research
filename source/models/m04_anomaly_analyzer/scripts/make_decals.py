"""Decals for the anomaly analyzer (system Python + Pillow): radiation sign, scales of the two pointer
meters, the recorder scale and knob limbs; parts with their own texture: the analyzer's gas-discharge
digits and the recorder tape - "off" and "work" frames. No letters: the sign is a symbol, the scales
have digits only.

    python make_decals.py      -> ../work/decal_*.png

The meter needles are separate bones (OZL_WorkFx wobble), they are not drawn on the scales. The tape:
72 frames of 0.1 s - the tape creeps down 2.8 mm per frame, under the pen line is the pen trace (a
sum of three oscillations, layout.py), the curve goes down and does not repeat within 7.2 s; digits -
64 frames (a 16 s count). The recorder scale is 0..100 exactly above the tape field (the pen at zero
stands on "0").
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
S = 4                                   # supersampling, then downscale: smooth edges
BLACK = (22, 20, 18, 255)
YELLOW = (236, 186, 22, 255)
FACE = (236, 234, 224, 255)
INK = (24, 24, 24, 255)
RED = (176, 32, 26, 255)


def font(px, name="arial.ttf"):
    for n in (name, "arial.ttf", "consola.ttf"):
        try:
            return ImageFont.truetype(n, px)
        except OSError:
            continue
    return ImageFont.load_default()


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def trefoil_mask(n, cx, cy, r):
    """Sign built per GOST 17925 / ISO 361: a circle of radius r in the centre, three 60-degree blades
    between radii 1.5r and 5r; one blade points down."""
    m = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(m)
    R = 5.0 * r
    for k in range(3):
        mid = 90 + 120 * k                         # PIL: angles run clockwise from +x, 90 is down
        d.pieslice([cx - R, cy - R, cx + R, cy + R], mid - 30, mid + 30, fill=255)
    hole = Image.new("L", (n, n), 0)
    ImageDraw.Draw(hole).ellipse([cx - 1.5 * r, cy - 1.5 * r, cx + 1.5 * r, cy + 1.5 * r], fill=255)
    m = ImageChops.subtract(m, hole)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    return m


def make_trefoil(px=512):
    """Yellow plate with rounded corners, black border, black trefoil (as in M03)."""
    n = px * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, n - 1, n - 1], radius=int(n * 0.08), fill=BLACK)
    m = int(n * 0.045)
    d.rounded_rectangle([m, m, n - 1 - m, n - 1 - m], radius=int(n * 0.06), fill=YELLOW)
    img.paste(Image.new("RGBA", (n, n), BLACK), (0, 0), trefoil_mask(n, n / 2, n / 2, n * 0.078))
    save(img, (px, px), "decal_trefoil.png")


def meter_geom(w, h):
    """Axis and radius of the scale arc (px): build_m04.py puts the needle axis in the same place."""
    r = min(h * 0.80, w * 0.50)                   # the outer digits must fit by width
    return w / 2, h * 0.10 + r * 1.27, r


def make_meter(name, w, h, labels, red_from=None, minor=5):
    """Panel meter face (like the M4200): white field, an 80-degree arc with the axis below the field, a
    mirror strip, ticks, digits above the arc, a red sector at the end. The needle is its own part (a bone)."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), FACE)
    d = ImageDraw.Draw(img)
    cx, cy, r = (v * S for v in meter_geom(w, h))
    a0, a1 = -130.0, -50.0                         # PIL: clockwise from +x, -90 is up

    def at(frac, rr):
        a = math.radians(a0 + (a1 - a0) * frac)
        return cx + math.cos(a) * rr, cy + math.sin(a) * rr
    # mirror strip and red sector
    d.arc([cx - r * 0.93, cy - r * 0.93, cx + r * 0.93, cy + r * 0.93], a0, a1, fill=(150, 156, 160, 255),
          width=int(H * 0.035))
    if red_from is not None:
        d.arc([cx - r * 1.01, cy - r * 1.01, cx + r * 1.01, cy + r * 1.01], a0 + (a1 - a0) * red_from, a1,
              fill=RED, width=int(H * 0.045))
    d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=INK, width=int(H * 0.008))
    n_major = len(labels) - 1
    n = n_major * minor
    for i in range(n + 1):
        frac = i / n
        big = i % minor == 0
        p0, p1 = at(frac, r), at(frac, r * (1.10 if big else 1.06))
        d.line([p0, p1], fill=INK, width=int(H * (0.014 if big else 0.007)))
    f = font(int(H * 0.11))
    for k, lab in enumerate(labels):
        d.text(at(k / n_major, r * 1.21), lab, fill=INK, font=f, anchor="mm")
    # needle axis slot (dark) and zero corrector screw
    d.ellipse([cx - H * 0.05, cy - H * 0.05, cx + H * 0.05, cy + H * 0.05], fill=(40, 40, 40, 255))
    d.ellipse([W * 0.08, H * 0.80, W * 0.14, H * 0.80 + W * 0.06], outline=INK, width=S * 2)
    d.line([(W * 0.08, H * 0.80 + W * 0.03), (W * 0.14, H * 0.80 + W * 0.03)], fill=INK, width=S * 2)
    save(img, (w, h), name)


def nixie_digit(ch, cw, ch_h, color):
    """Gas-discharge indicator digit: narrow (like an IN-12 cathode), on transparent."""
    big = Image.new("RGBA", (int(cw * 1.5), int(ch_h)), (0, 0, 0, 0))
    ImageDraw.Draw(big).text((big.width / 2, big.height * 0.52), ch, fill=color, font=font(int(ch_h * 0.80)),
                             anchor="mm")
    return big.resize((int(cw), int(ch_h)), Image.LANCZOS)


def make_nixie(name, w, h, digits):
    """Gas-discharge indicators (like the IN-12): dark glass, an anode grid, a stack of digit cathodes
    (dark), the lit digit is orange with a glow; digits=None - all off."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (14, 12, 12, 255))
    d = ImageDraw.Draw(img)
    n = 6
    cw = W / n
    for i in range(n):
        x0 = i * cw + cw * 0.08
        d.rounded_rectangle([x0, H * 0.06, x0 + cw * 0.84, H * 0.94], radius=int(cw * 0.25), fill=(34, 26, 22, 255))
    # unlit cathodes: all digits one behind another - dark wire
    cath = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for i in range(n):
        for ch in "0123456789":
            g = nixie_digit(ch, cw * 0.62, H * 0.86, (70, 60, 52, 90))
            cath.alpha_composite(g, (int(i * cw + cw * 0.19), int(H * 0.07)))
    img = Image.alpha_composite(img, cath)
    d = ImageDraw.Draw(img)
    for i in range(n):                             # anode grid over the cathodes
        x0 = i * cw + cw * 0.08
        for k in range(0, int(cw * 0.84), S * 6):
            d.line([(x0 + k, H * 0.10), (x0 + k, H * 0.90)], fill=(52, 42, 34, 255), width=S)
    if digits is not None:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for i, ch in enumerate(digits):
            glow.alpha_composite(nixie_digit(ch, cw * 0.62, H * 0.86, (255, 150, 50, 255)),
                                 (int(i * cw + cw * 0.19), int(H * 0.07)))
        img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(H * 0.06)))
        img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(H * 0.015)))
        img = Image.alpha_composite(img, glow)
    save(img, (w, h), name)


def nixie_counts(n=L.NIXIE_FRAMES, seed=4):
    """Count by frames: 0 is a reset, then the sample pulses per 0.25 s - about 140 with statistical
    scatter (the last three digits change per frame, the fourth once per 7 frames); up to ~9000 over 64 frames."""
    rnd = random.Random(seed)
    out, count = [], 0
    for _ in range(n):
        out.append(count)
        count += max(90, int(round(rnd.gauss(140.0, 14.0))))
    return out


def make_nixie_set(w=512, h=128):
    """Off state - all unlit; frames: 0 is the count reset, then the count grows (sample pulses)."""
    make_nixie("decal_nixie_off.png", w, h, None)
    for k, count in enumerate(nixie_counts()):
        make_nixie("decal_nixie_f%02d.png" % k, w, h, "%06d" % count)


def make_scale(w=1024, h=96, margin=(L.SCALE_W - L.FIELD_W) / 2 / L.SCALE_W):
    """Recorder scale above the window: a white strip, ticks 0..100 every 2 and 10, digits every 10; 0 and
    100 are above the edges of the tape field."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), FACE)
    d = ImageDraw.Draw(img)
    x0, x1 = W * margin, W * (1 - margin)
    f = font(int(H * 0.40))
    for i in range(51):
        x = x0 + (x1 - x0) * i / 50
        big = i % 5 == 0
        d.line([(x, H * 0.98), (x, H * (0.55 if big else 0.75))], fill=INK, width=int(S * (2.5 if big else 1.2)))
        if i % 5 == 0:
            d.text((x, H * 0.28), str(i * 2), fill=INK, font=f, anchor="mm")
    save(img, (w, h), "decal_scale.png")


def make_knob_ring(name, px, labels, sweep):
    """Limb under a knob: black ticks and digits along an arc on transparent (laid on the panel)."""
    n = px * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = n / 2
    k = len(labels)
    start = -90 - sweep / 2
    f = font(int(n * 0.13))
    for i, lab in enumerate(labels):
        a = math.radians(start + sweep * i / (k - 1))
        d.line([(c + math.cos(a) * n * 0.30, c + math.sin(a) * n * 0.30),
                (c + math.cos(a) * n * 0.36, c + math.sin(a) * n * 0.36)], fill=INK, width=int(n * 0.018))
        d.text((c + math.cos(a) * n * 0.44, c + math.sin(a) * n * 0.44), lab, fill=INK, font=f, anchor="mm")
    save(img, (px, px), name)


# --- recorder tape ------------------------------------------------------------------------------
PX_MM = 2.0                                       # tape image: 2 px per mm (560 x 468)


def pen_mm(t):
    """Pen at work time t: mm from the left edge of the tape (layout.pen_x is from the field zero, in metres)."""
    return (L.FIELD_X0 + L.pen_x(t)) * 1000.0


def make_chart(name, t, on):
    """Tape at work time t (s): shifted down by v * t; grid every 10 and 50 mm in the recording field, edge
    perforation, the pen trace under the pen (violet ink): the point d below the pen was written at
    t - d / v. on=False - the tape stands and the pen has gone to zero after the work: from the end of
    the trace to zero a stroke along the pen line."""
    w_mm, h_mm = L.CHART_W * 1000.0, L.CHART_H * 1000.0
    W, H = int(w_mm * PX_MM) * S, int(h_mm * PX_MM) * S
    sc = PX_MM * S                                # px per mm when supersampled
    rnd = random.Random(11)
    img = Image.new("RGBA", (W, H), (240, 236, 222, 255))
    # paper: light tone patches, yellowing toward the edges
    tint = Image.new("L", (32, 28), 0)
    tint.putdata([rnd.randint(0, 255) for _ in range(32 * 28)])
    tint = tint.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(sc * 6))
    img = Image.composite(Image.new("RGBA", (W, H), (226, 218, 194, 255)), img, tint.point(lambda v: int(v * 0.45)))
    d = ImageDraw.Draw(img)
    v = L.TAPE_RUN * 1000.0 / L.CYCLE                 # mm/s
    shift = (v * t) % (L.TAPE_RUN * 1000.0)           # mm: how far the tape has gone down (modulo the loop)
    fx0, fx1 = L.FIELD_X0 * 1000.0, (L.FIELD_X0 + L.FIELD_W) * 1000.0
    fine, bold = (232, 176, 156, 255), (204, 112, 88, 255)
    # longitudinal lines (stationary): every 10 mm, every fifth one bold
    for i in range(26):
        x = (fx0 + 10.0 * i) * sc
        d.line([(x, 0), (x, H)], fill=bold if i % 5 == 0 else fine, width=int(sc * (0.55 if i % 5 == 0 else 0.3)))
    # cross lines (move with the tape)
    j0 = -int(shift // 10.0) - 1
    for j in range(j0, j0 + int(h_mm // 10.0) + 3):
        s = 10.0 * j                                  # coordinate on the tape
        y = (s + shift) * sc
        if -sc < y < H + sc:
            b = j % 5 == 0
            d.line([(fx0 * sc, y), (fx1 * sc, y)], fill=bold if b else fine, width=int(sc * (0.55 if b else 0.3)))
    # edge perforation: 10 mm step, holes of diameter 3.5
    for j in range(j0, j0 + int(h_mm // 10.0) + 3):
        y = (10.0 * j + 5.0 + shift) * sc
        for xc in (7.5, w_mm - 7.5):
            r = 1.75 * sc
            d.ellipse([xc * sc - r, y - r, xc * sc + r, y + r], fill=(46, 44, 42, 255))
    # pen trace: below the pen line, by recording time
    ink = (72, 48, 140, 255)
    yp = L.PEN_D * 1000.0
    pts = []
    yy = yp
    while yy <= h_mm + 2.0:
        pts.append((pen_mm(t - (yy - yp) / v) * sc, yy * sc))
        yy += 0.25
    if not on:
        # the tape stopped at once, the pen slid along the pen line to zero in 1.5 s (OZL_WorkFx: wobble eases to 0)
        pts = [(fx0 * sc, yp * sc)] + pts
    d.line(pts, fill=ink, width=int(sc * 0.9), joint="curve")
    save(img, (W // S, H // S), name)


def make_chart_set():
    """Off state - the tape at frame 0 and a stroke to zero; frames 0..CHART_FRAMES-1 - in a loop."""
    make_chart("decal_chart_off.png", L.frame_time(0), False)
    for k in range(L.CHART_FRAMES):
        make_chart("decal_chart_f%02d.png" % k, L.frame_time(k), True)


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    make_trefoil()
    # intensity meter: logarithmic count-rate scale
    make_meter("decal_meter_rate.png", 512, 416, ["1", "10", "10²", "10³", "10⁴"], red_from=0.85, minor=9)
    # detector high-voltage kilovoltmeter
    make_meter("decal_meter_hv.png", 384, 320, ["0", "0.5", "1.0", "1.5", "2.0"], red_from=0.88)
    make_nixie_set()
    make_scale()
    make_knob_ring("decal_ring10.png", 256, [str(i) for i in range(11)], 270.0)
    make_knob_ring("decal_ring6.png", 256, [str(i) for i in range(1, 7)], 150.0)
    make_chart_set()
