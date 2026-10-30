"""Decals for the electronics analyzer (system Python + Pillow): the screens of two oscilloscopes and
the counter display - own textures: "off" and "work" frames (cycled by the mod's script, OZL_WorkFx
frames); faces of pointer instruments (the needles are model parts, they wobble in "work"),
generator decade windows, the recorder scale, knob limbs, the probe board, an inventory tag, a ground
plate, a "caution, voltage" sign. No letters: only digits, scales and signs.

    python make_decals.py      -> ../work/decal_*.png

"Work" frames:
- S1-65A (decal_crt_fNN, 12): slow sweep - a glowing dot moves left to right and draws pulses with
  overshoots on the edges, behind it the trace of the previous pass fades (phosphor afterglow);
- S1-94 (decal_crt2_fNN, 12): the sine "floats" (sync does not hold) - a shift by 1/12 of a period
  per frame, the amplitude breathes a little; after 12 frames the picture returns to the first, the
  seam is invisible;
- Ch3-63 (decal_led_fNN, 8): 1000.215 kHz, the last digits change from count to count;
- KSP4 recorder tape (decal_chart_fNN, 72): the tape creeps down 2.8 mm per frame, under the pen line
  is the pen trace (a sum of three oscillations, m06_chart.py), the curve goes down and does not
  repeat within 7.2 s; "off" - the tape stands, from the end of the trace to zero a stroke of the
  pen along the pen line.
The recorder scale is 0..100 exactly above the tape field (the pen at zero stands on "0").
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m06_chart as CH  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
FACE = (236, 234, 224, 255)
INK = (24, 24, 24, 255)
RED = (176, 32, 26, 255)
PHOSPHOR = (14, 26, 20, 255)            # phosphor under current (the background glows slightly)
BEAM = (150, 255, 170, 255)
GRID_ON = (88, 132, 104, 255)           # scale backlight on
OFF = dict(phosphor=(20, 24, 22, 255), grid=(44, 54, 48, 255))


def font(px):
    for name in ("arial.ttf", "consola.ttf"):
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def graticule(d, W, H, nx, ny, grid):
    """Screen grid of nx x ny divisions with fine ticks along the axes; returns the field (mx, my, gw, gh)."""
    mx, my = W * 0.04, H * 0.05
    gw, gh = W - 2 * mx, H - 2 * my
    for i in range(nx + 1):
        x = mx + gw * i / nx
        d.line([(x, my), (x, my + gh)], fill=grid, width=S * (2 if i in (0, nx // 2, nx) else 1))
    for j in range(ny + 1):
        y = my + gh * j / ny
        d.line([(mx, y), (mx + gw, y)], fill=grid, width=S * (2 if j in (0, ny // 2, ny) else 1))
    for i in range(nx * 5 + 1):
        x = mx + gw * i / (nx * 5)
        d.line([(x, my + gh / 2 - S * 4), (x, my + gh / 2 + S * 4)], fill=grid, width=S)
    for j in range(ny * 5 + 1):
        y = my + gh * j / (ny * 5)
        d.line([(mx + gw / 2 - S * 4, y), (mx + gw / 2 + S * 4, y)], fill=grid, width=S)
    return mx, my, gw, gh


def crt_off(name, w, h, nx=10, ny=8):
    """Screen off: dark CRT glass, the scale grid barely visible, no beam."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), OFF["phosphor"])
    graticule(ImageDraw.Draw(img), W, H, nx, ny, OFF["grid"])
    save(img, (w, h), name)


def crt_frame(name, w, h, wave, head=None, nx=10, ny=8, amp=0.36, n=600, glow_px=4):
    """Screen frame under current: a lit grid, the beam trace wave(t) -> -1..1 (t 0..1 across the width).
    head is where the beam is now (slow sweep): before it the trace is bright and fades toward the start
    of the pass, after it - the dim trace of the previous pass, at head - a glowing dot. head None - an
    even trace."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), PHOSPHOR)
    mx, my, gw, gh = graticule(ImageDraw.Draw(img), W, H, nx, ny, GRID_ON)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    b = ImageDraw.Draw(lay)
    pts = [(mx + gw * k / n, my + gh / 2 - gh * amp * wave(k / n)) for k in range(n + 1)]
    for k in range(n):
        t = (k + 0.5) / n
        if head is None:
            a = 1.0
        elif t <= head:
            a = 1.0 - 0.55 * (head - t)
        else:
            a = 0.30 * (1.0 - 0.6 * (t - head))
        col = tuple(int(c * a) for c in BEAM[:3]) + (int(255 * min(1.0, 0.25 + a)),)
        b.line([pts[k], pts[k + 1]], fill=col, width=S * 3)
    if head is not None:
        k = min(n, int(head * n))
        x, y = pts[k]
        b.ellipse([x - S * 5, y - S * 5, x + S * 5, y + S * 5], fill=(220, 255, 225, 255))
    img = Image.alpha_composite(img, lay.filter(ImageFilter.GaussianBlur(S * glow_px)))
    img = Image.alpha_composite(img, lay)
    save(img, (w, h), name)


def make_meter(name, w, h, labels, labels2=None, minor=5):
    """Pointer instrument face: white field, an arc with ticks, digits; labels2 is a second scale under the
    first (the millivoltmeter has 0..3 and 0..10). No needle: it is a model part (a bone, wobbles in
    "work"); the needle axis is at the bottom edge: (W/2, 0.10 H + 1.27 r), r = min(0.8 H, 0.5 W) - the
    same numbers are in build_m06.py (meter_pivot)."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), FACE)
    d = ImageDraw.Draw(img)
    r = min(H * 0.80, W * 0.50)
    cx, cy = W / 2, H * 0.10 + r * 1.27
    a0, a1 = -130.0, -50.0

    def at(frac, rr):
        a = math.radians(a0 + (a1 - a0) * frac)
        return cx + math.cos(a) * rr, cy + math.sin(a) * rr

    def scale(labs, rr, out):
        n_major = len(labs) - 1
        n = n_major * minor
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], a0, a1, fill=INK, width=int(H * 0.008))
        for i in range(n + 1):
            big = i % minor == 0
            k = (1.10 if big else 1.06) if out else (0.90 if big else 0.94)
            d.line([at(i / n, rr), at(i / n, rr * k)], fill=INK, width=int(H * (0.014 if big else 0.007)))
        f = font(int(H * 0.10))
        for k, lab in enumerate(labs):
            d.text(at(k / n_major, rr * (1.21 if out else 0.80)), lab, fill=INK, font=f, anchor="mm")
    d.arc([cx - r * 0.95, cy - r * 0.95, cx + r * 0.95, cy + r * 0.95], a0, a1, fill=(150, 156, 160, 255),
          width=int(H * 0.03))
    scale(labels, r, True)
    if labels2:
        scale(labels2, r * 0.90, False)
    # mirror strip under the scale (accuracy class) - a grey arc
    d.arc([cx - r * 1.015, cy - r * 1.015, cx + r * 1.015, cy + r * 1.015], a0 + 2, a1 - 2,
          fill=(186, 190, 194, 255), width=int(H * 0.012))
    save(img, (w, h), name)


def make_led(name, w, h, text, color=(255, 60, 40, 255), dim=(90, 20, 18, 255), bg=(40, 8, 8, 255)):
    """Counter display: a dark red filter, seven-segment digits with glow and a point; dim is the unlit
    segments behind the filter."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), bg)
    digits = [c for c in text if c != "."]
    dots = set()
    k = 0
    for c in text:
        if c == ".":
            dots.add(k - 1)
        else:
            k += 1
    n = len(digits)
    cw = W / n
    seg = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
           "7": "abc", "8": "abcdefg", "9": "abcdfg", " ": ""}
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(lay)
    base = ImageDraw.Draw(img)
    for i, ch in enumerate(digits):
        x0, x1 = i * cw + cw * 0.22, i * cw + cw * 0.74
        y0, ym, y1 = H * 0.16, H * 0.50, H * 0.84
        t = max(S * 3, cw * 0.09)
        segs = {"a": [(x0, y0), (x1, y0)], "g": [(x0, ym), (x1, ym)], "d": [(x0, y1), (x1, y1)],
                "f": [(x0, y0), (x0, ym)], "b": [(x1, y0), (x1, ym)], "e": [(x0, ym), (x0, y1)],
                "c": [(x1, ym), (x1, y1)]}
        for s, ln in segs.items():
            base.line(ln, fill=dim, width=int(t))
            if s in seg[ch]:
                g.line(ln, fill=color, width=int(t))
        if i in dots:
            g.ellipse([x1 + cw * 0.08, y1 - t, x1 + cw * 0.08 + t * 1.3, y1 + t * 0.3], fill=color)
    img = Image.alpha_composite(img, lay.filter(ImageFilter.GaussianBlur(H * 0.04)))
    img = Image.alpha_composite(img, lay)
    save(img, (w, h), name)


def make_windows(name, w, h, digits):
    """Generator decade switch windows: a black frame, white digits on black drums."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (18, 18, 18, 255))
    d = ImageDraw.Draw(img)
    n = len(digits)
    cw = W / n
    f = font(int(H * 0.70))
    for i, ch in enumerate(digits):
        d.rectangle([i * cw + cw * 0.12, H * 0.08, i * cw + cw * 0.88, H * 0.92], fill=(36, 36, 38, 255))
        d.text(((i + 0.5) * cw, H * 0.52), ch, fill=(236, 236, 228, 255), font=f, anchor="mm")
    save(img, (w, h), name)


def make_scale(w=1024, h=96, margin=(CH.SCALE_W - CH.FIELD_W) / 2 / CH.SCALE_W):
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
        if big:
            d.text((x, H * 0.28), str(i * 2), fill=INK, font=f, anchor="mm")
    save(img, (w, h), "decal_scale.png")


def make_knob_ring(name, px, labels, sweep):
    """Limb under a knob: ticks and digits along an arc on transparent (laid on the cream panel)."""
    n = px * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = n / 2
    k = len(labels)
    start = -90 - sweep / 2
    f = font(int(n * 0.12))
    for i, lab in enumerate(labels):
        a = math.radians(start + sweep * i / (k - 1))
        d.line([(c + math.cos(a) * n * 0.30, c + math.sin(a) * n * 0.30),
                (c + math.cos(a) * n * 0.36, c + math.sin(a) * n * 0.36)], fill=INK, width=int(n * 0.018))
        if lab:
            d.text((c + math.cos(a) * n * 0.44, c + math.sin(a) * n * 0.44), lab, fill=INK, font=f, anchor="mm")
    save(img, (px, px), name)


def make_pcb(w=512, h=256, seed=9):
    """Probe board: green mask, copper traces and pads, part outlines in silkscreen without letters, a gold
    knife-edge connector along the bottom edge (the board stands in the block by it)."""
    rnd = random.Random(seed)
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (34, 92, 52, 255))
    d = ImageDraw.Draw(img)
    copper = (176, 150, 70, 255)
    silk = (220, 224, 210, 255)
    pads = [(rnd.uniform(0.05, 0.95) * W, rnd.uniform(0.08, 0.78) * H) for _ in range(60)]
    for i in range(len(pads) - 1):
        if rnd.random() < 0.7:
            (xa, ya), (xb, yb) = pads[i], pads[(i + rnd.randint(1, 4)) % len(pads)]
            d.line([(xa, ya), (xb, ya), (xb, yb)], fill=(52, 120, 64, 255), width=S * 5)
            d.line([(xa, ya), (xb, ya), (xb, yb)], fill=copper, width=S * 2)
    for x, y in pads:
        d.ellipse([x - S * 5, y - S * 5, x + S * 5, y + S * 5], fill=copper)
        d.ellipse([x - S * 2, y - S * 2, x + S * 2, y + S * 2], fill=(20, 30, 20, 255))
    for _ in range(10):
        x, y = rnd.uniform(0.06, 0.82) * W, rnd.uniform(0.08, 0.60) * H
        d.rectangle([x, y, x + rnd.uniform(0.06, 0.14) * W, y + rnd.uniform(0.08, 0.16) * H], outline=silk, width=S * 2)
    n = 22                                                  # connector fingers
    for i in range(n):
        x = W * (0.08 + 0.84 * (i + 0.5) / n)
        d.rectangle([x - W * 0.012, H * 0.86, x + W * 0.012, H * 0.99], fill=(212, 176, 70, 255))
    save(img, (w, h), "decal_pcb.png")


def make_tag(w=280, h=120, number="0417"):
    """Inventory tag: an aluminium plate, a rim around the edge, stamped digits (no letters)."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (186, 188, 184, 255))
    d = ImageDraw.Draw(img)
    rnd = random.Random(4)
    for _ in range(140):                                    # brushing along
        y = rnd.uniform(0, H)
        c = rnd.randint(170, 200)
        d.line([(0, y), (W, y + rnd.uniform(-4, 4))], fill=(c, c + 2, c - 2, 255), width=S)
    d.rounded_rectangle([S * 6, S * 6, W - S * 6, H - S * 6], radius=S * 8, outline=(120, 122, 120, 255), width=S * 3)
    f = font(int(H * 0.52))
    for dx, dy, col in ((S * 2, S * 2, (232, 234, 230, 255)), (0, 0, (70, 72, 70, 255))):
        d.text((W / 2 + dx, H * 0.53 + dy), number, fill=col, font=f, anchor="mm")
    save(img, (w, h), "decal_tag.png")


def make_ground(px=128):
    """Ground plate: the protective ground sign in a circle, black on aluminium."""
    n = px * S
    img = Image.new("RGBA", (n, n), (186, 188, 184, 255))
    d = ImageDraw.Draw(img)
    c = n / 2
    w = int(n * 0.045)
    d.ellipse([n * 0.08, n * 0.08, n * 0.92, n * 0.92], outline=INK, width=w)
    d.line([(c, n * 0.22), (c, n * 0.52)], fill=INK, width=w)
    for k, half in enumerate((0.26, 0.17, 0.08)):
        y = n * (0.52 + 0.11 * k)
        d.line([(c - n * half, y), (c + n * half, y)], fill=INK, width=w)
    save(img, (px, px), "decal_ground.png")


def make_hv(w=128, h=112):
    """Sign "caution, electrical voltage": a yellow triangle, a black border and a lightning bolt."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    tri = [(W * 0.5, H * 0.03), (W * 0.97, H * 0.97), (W * 0.03, H * 0.97)]
    d.polygon(tri, fill=INK)
    inner = [(W * 0.5, H * 0.17), (W * 0.86, H * 0.89), (W * 0.14, H * 0.89)]
    d.polygon(inner, fill=(236, 190, 30, 255))
    bolt = [(W * 0.56, H * 0.30), (W * 0.40, H * 0.60), (W * 0.50, H * 0.60), (W * 0.42, H * 0.84),
            (W * 0.62, H * 0.52), (W * 0.52, H * 0.52), (W * 0.62, H * 0.30)]
    d.polygon(bolt, fill=INK)
    save(img, (w, h), "decal_hv.png")


# --- recorder tape ---------------------------------------------------------------------------
PX_MM = 2.0                                       # tape image: 2 px per mm (560 x 468)


def pen_mm(t):
    """Pen at work time t: mm from the left edge of the tape (m06_chart.pen_x is from the field zero, in metres)."""
    return (CH.FIELD_X0 + CH.pen_x(t)) * 1000.0


def make_chart(name, t, on):
    """Tape at work time t (s): shifted down by v * t; grid every 10 and 50 mm in the recording field, edge
    perforation, the pen trace under the pen (violet ink): the point d below the pen was written at
    t - d / v. on=False - the tape stands and the pen has gone to zero after the work: from the end of
    the trace to zero a stroke along the pen line."""
    w_mm, h_mm = CH.CHART_W * 1000.0, CH.CHART_H * 1000.0
    W, H = int(w_mm * PX_MM) * S, int(h_mm * PX_MM) * S
    sc = PX_MM * S                                # px per mm when supersampled
    rnd = random.Random(11)
    img = Image.new("RGBA", (W, H), (240, 236, 222, 255))
    # paper: light tone patches
    tint = Image.new("L", (32, 28), 0)
    tint.putdata([rnd.randint(0, 255) for _ in range(32 * 28)])
    tint = tint.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(sc * 6))
    img = Image.composite(Image.new("RGBA", (W, H), (228, 222, 200, 255)), img, tint.point(lambda v: int(v * 0.45)))
    d = ImageDraw.Draw(img)
    v = CH.TAPE_RUN * 1000.0 / CH.CYCLE               # mm/s
    shift = (v * t) % (CH.TAPE_RUN * 1000.0)          # mm: how far the tape has gone down (modulo the loop)
    fx0, fx1 = CH.FIELD_X0 * 1000.0, (CH.FIELD_X0 + CH.FIELD_W) * 1000.0
    fine, bold = (226, 164, 142, 255), (198, 112, 90, 255)
    # longitudinal lines (stationary): every 10 mm, every fifth one bold
    for i in range(26):
        x = (fx0 + 10.0 * i) * sc
        d.line([(x, 0), (x, H)], fill=bold if i % 5 == 0 else fine, width=int(sc * (0.55 if i % 5 == 0 else 0.3)))
    # cross lines (move with the tape)
    j0 = -int(shift // 10.0) - 1
    for j in range(j0, j0 + int(h_mm // 10.0) + 3):
        y = (10.0 * j + shift) * sc
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
    yp = CH.PEN_D * 1000.0
    pts = []
    yy = yp
    while yy <= h_mm + 2.0:
        pts.append((pen_mm(t - (yy - yp) / v) * sc, yy * sc))
        yy += 0.25
    if not on:
        # the tape stopped at once, the pen slid along the pen line to zero in 1.5 s (OZL_WorkFx: wobble eases to 0)
        pts = [(fx0 * sc, yp * sc)] + pts
    d.line(pts, fill=ink, width=int(sc * 1.0), joint="curve")
    save(img, (W // S, H // S), name)


def make_chart_set():
    """Off state - the tape at frame 0 and a stroke to zero; frames 0..CHART_FRAMES-1 - in a loop."""
    make_chart("decal_chart_off.png", CH.frame_time(0), False)
    for k in range(CH.CHART_FRAMES):
        make_chart("decal_chart_f%02d.png" % k, CH.frame_time(k), True)


def square(t, cycles=3.0, ph=0.0):
    """Square wave with overshoots and ringing on the edges (the board responds to generator pulses)."""
    p = (t * cycles + ph) % 1.0
    v = 0.8 if p < 0.5 else -0.8
    edge = min(p, abs(p - 0.5), 1.0 - p)
    sgn = 1 if p < 0.5 else -1
    since = p if p < 0.5 else p - 0.5
    ring = 0.16 * math.exp(-since * 40.0) * math.cos(since * 120.0) * sgn
    return v + ring + 0.03 * math.exp(-edge * 400.0)


if __name__ == "__main__":
    os.makedirs(WORK, exist_ok=True)
    # S1-65A (screen of 8 x 10 divisions): "off" and 12 frames of slow sweep
    crt_off("decal_crt_off.png", 480, 384)
    # the first frame (also the preview and onTextures) - the beam has passed three quarters of the screen; then in
    # a loop
    for k in range(12):
        crt_frame("decal_crt_f%02d.png" % k, 480, 384, square, head=((k + 8) % 12 + 1) / 12.0)
    # S1-94 (60 x 40 mm, 10 x 8): "off" and 12 frames of a floating sine
    crt_off("decal_crt2_off.png", 384, 256)
    for k in range(12):
        ph = 2 * math.pi * k / 12
        a = 0.80 + 0.06 * math.sin(ph)
        crt_frame("decal_crt2_f%02d.png" % k, 384, 256,
                  lambda t, ph=ph, a=a: a * math.sin(2 * math.pi * 2.5 * t - ph), amp=0.36, glow_px=3)
    # Ch3-63: "off" and 8 counts (1000.215 kHz, the last digits wander)
    make_led("decal_led_off.png", 640, 96, "        ", color=(0, 0, 0, 0), dim=(46, 16, 15, 255), bg=(26, 9, 9, 255))
    for k, txt in enumerate((" 1000.215", " 1000.216", " 1000.214", " 1000.215", " 1000.217", " 1000.216",
                             " 1000.215", " 1000.213")):
        make_led("decal_led_f%02d.png" % k, 640, 96, txt)
    # G3-118: output voltmeter; decade windows - 1 0 0 0 (1 kHz)
    make_meter("decal_meter_g3.png", 320, 224, ["0", "1", "2", "3", "4", "5"])
    make_windows("decal_g3_windows.png", 384, 96, "1000")
    # V3-38: two scales 0..3 and 0..10
    make_meter("decal_meter_v3.png", 384, 288, ["0", "1", "2", "3"], labels2=["0", "2", "4", "6", "8", "10"])
    make_scale()
    make_knob_ring("decal_ring11.png", 256, [str(i) for i in range(11)], 270.0)
    make_knob_ring("decal_ring6.png", 256, ["", "", "", "", "", ""], 150.0)
    make_pcb()
    make_tag()
    make_ground()
    make_hv()
    # KSP4 recorder tape: "off" and 72 frames of 0.1 s
    make_chart_set()
