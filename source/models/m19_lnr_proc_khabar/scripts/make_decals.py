"""Decals for the detector TV set (system Python + Pillow).

The picture tube screen is its own texture: "off" is dark grey glass, "work" is 12 sweep frames: a
glowing dot runs left to right and draws the detector signal (a noisy baseline, two peaks, ringing after
the large one), behind it the trace slowly fades like the phosphor of a black-and-white tube; white-blue,
no green. The microammeter scale (digits are allowed), the detector block panel (ticks and symbols
without letters), the laminate board (as in the "Rubin"), the channel selector dial (digits 1-12) and
three decals without text: a radiation sign, a round "sun", a rectangular one with a lightning bolt.

The meter scale sits on a face that looks toward +Y (to the removed back wall): a person sees +X on the
left, so its picture is mirrored - the digits read correctly on the model.

    python make_decals.py      -> ../work/decal_*.png
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m19_layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
FRAMES = 12                             # "work" frames of the screen


def font(px):
    for name in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


def save(img, size, name, mirror=False):
    img = img.resize(size, Image.LANCZOS)
    if mirror:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def vignette(W, H, k):
    """L mask: 255 in the centre, darker toward the edges by k (0..1)
    - the picture tube screen fades toward the corners."""
    v = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(v)
    n = 24
    for i in range(n):
        f = i / n
        d.ellipse([W * (-0.25 + 0.3 * f), H * (-0.25 + 0.3 * f), W * (1.25 - 0.3 * f), H * (1.25 - 0.3 * f)],
                  fill=int(255 * (1 - k) + 255 * k * f))
    return v.filter(ImageFilter.GaussianBlur(W * 0.05))


def raster(W, H, k=0.92, n=5.0):
    """L mask of the lit raster: a superellipse a little smaller than the glass (the mask window is 0.97 of
    the glass), a soft edge."""
    m = Image.new("L", (W, H), 0)
    pts = []
    for i in range(256):
        t = 2 * math.pi * i / 256
        sx, sz = math.cos(t), math.sin(t)
        lam = (abs(sx) ** n + abs(sz) ** n) ** (-1.0 / n)
        pts.append((W / 2 + W / 2 * k * sx * lam, H / 2 - H / 2 * k * sz * lam))
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m.filter(ImageFilter.GaussianBlur(W * 0.012))


def make_screen_off(name):
    """Switched-off tube: dark grey glass, darker toward the edges, a hazy slanted glint at the top left."""
    w, h = L.SCREEN_PX
    W, H = w * 2, h * 2
    base = Image.new("RGBA", (W, H), (30, 32, 33, 255))
    light = Image.new("RGBA", (W, H), (56, 59, 61, 255))
    img = Image.composite(light, base, vignette(W, H, 0.9))
    hl = Image.new("L", (W, H), 0)
    ImageDraw.Draw(hl).polygon([(W * 0.10, H * 0.12), (W * 0.40, H * 0.08), (W * 0.22, H * 0.46), (W * 0.08, H * 0.40)],
                               fill=40)
    hl = hl.filter(ImageFilter.GaussianBlur(W * 0.05))
    img = Image.composite(Image.new("RGBA", (W, H), (104, 108, 112, 255)), img, hl)
    save(img, (w, h), name)


def detector_trace(t):
    """Detector signal: a noisy baseline, two peaks of different heights and damped ringing after the big one."""
    rnd = random.Random(int(t * 997))
    v = 0.06 * math.sin(t * 61.0) + 0.04 * (rnd.random() - 0.5)
    v += 0.95 * math.exp(-((t - 0.58) / 0.035) ** 2)
    v += 0.35 * math.exp(-((t - 0.27) / 0.03) ** 2)
    if t > 0.62:
        v += 0.25 * math.exp(-(t - 0.62) * 9.0) * math.sin((t - 0.62) * 80.0)
    return v


def make_screen_frames(prefix, n=FRAMES):
    """Work frames: the raster glows grey-blue, sweep lines, a dim baseline with divisions; the beam dot in
    frame k is at (k + 0.5) / n of the width, to the left of it the trace is fresh, farther on it fades
    (phosphor), to the right is the remainder of the previous pass. The frames loop - the same signal pass
    after pass."""
    w, h = L.SCREEN_PX
    s = 2
    W, H = w * s, h * s
    mx, y0, amp = W * 0.09, H * 0.70, H * 0.52
    samples = 720
    pts = [(mx + (W - 2 * mx) * i / samples, y0 - amp * detector_trace(i / samples)) for i in range(samples + 1)]
    ras = raster(W, H)
    for f in range(n):
        dot = (f + 0.5) / n
        img = Image.new("RGBA", (W, H), (22, 24, 29, 255))
        lit = Image.new("RGBA", (W, H), (60, 70, 88, 255))
        mask = Image.composite(vignette(W, H, 0.7), Image.new("L", (W, H), 0), ras)
        img = Image.composite(lit, img, mask)
        # sweep lines - a separate layer (drawing straight into RGBA
        # is wrong: the line alpha would land in the picture)
        sl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(sl)
        for y in range(0, H, s * 5):
            d.line([(0, y), (W, y)], fill=(10, 12, 18, 40), width=s)
        img = Image.alpha_composite(img, sl)
        # baseline with divisions - dim
        base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        b = ImageDraw.Draw(base)
        b.line([(mx, y0), (W - mx, y0)], fill=(130, 150, 186, 110), width=s * 2)
        for i in range(11):
            x = mx + (W - 2 * mx) * i / 10
            b.line([(x, y0 - s * 6), (x, y0 + s * 6)], fill=(130, 150, 186, 110), width=s * 2)
        img = Image.alpha_composite(img, base.filter(ImageFilter.GaussianBlur(s * 1.2)))
        # beam trace: brightness by the "age" of a point (the fraction of the pass since the beam crossed it)
        tr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dt, dg = ImageDraw.Draw(tr), ImageDraw.Draw(glow)
        for i in range(samples):
            age = (dot - (i + 0.5) / samples) % 1.0
            k = math.exp(-age * 2.6)
            a = int(255 * (0.22 + 0.78 * k))
            col = tuple(int(c0 + (c1 - c0) * k) for c0, c1 in zip((120, 150, 205), (236, 244, 255)))
            dt.line([pts[i], pts[i + 1]], fill=col + (a,), width=int(s * (2.5 + 2.0 * k)))
            dg.line([pts[i], pts[i + 1]], fill=(140, 180, 250, int(210 * k)), width=s * 12)
        img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(s * 7)))
        img = Image.alpha_composite(img, tr.filter(ImageFilter.GaussianBlur(s * 0.6)))
        # beam dot with a halo
        xd, yd = mx + (W - 2 * mx) * dot, y0 - amp * detector_trace(dot)
        bl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(bl).ellipse([xd - s * 16, yd - s * 16, xd + s * 16, yd + s * 16], fill=(170, 200, 255, 200))
        img = Image.alpha_composite(img, bl.filter(ImageFilter.GaussianBlur(s * 9)))
        ImageDraw.Draw(img).ellipse([xd - s * 4, yd - s * 4, xd + s * 4, yd + s * 4], fill=(250, 252, 255, 255))
        # outside the raster - dark glass
        dark = Image.new("RGBA", (W, H), (20, 22, 24, 255))
        img = Image.composite(img, dark, ras)
        save(img, (w, h), "%s%02d.png" % (prefix, f))


def make_meter(name):
    """Microammeter scale (window DIAL_W x DIAL_H): a cream field, a 90 degree arc about the needle axis
    under the window, 0-10 with large divisions, a red sector 8-10. The picture is mirrored (the face looks
    toward +Y)."""
    k = 4000 * S                                     # pixels per metre
    W, H = int(L.DIAL_W * k), int(L.DIAL_H * k)
    img = Image.new("RGBA", (W, H), (226, 220, 202, 255))
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, H + L.PIVOT_DZ * k
    R = L.ARC_R * k
    ink = (34, 32, 30, 255)

    def at(v, r):
        a = math.radians(135.0 - 90.0 * v)
        return cx + r * math.cos(a), cy - r * math.sin(a)
    # red sector 8-10 - an arc behind the divisions (PIL angles go from +x clockwise, y down)
    rr = R * 1.15
    d.arc([cx - rr, cy - rr, cx + rr, cy + rr], -63, -45, fill=(176, 40, 30, 255), width=S * 7)
    d.arc([cx - R, cy - R, cx + R, cy + R], -135, -45, fill=ink, width=S * 3)
    f = font(int(S * 26))
    for i in range(51):
        v = i / 50
        big = i % 5 == 0
        x0, y0 = at(v, R)
        x1, y1 = at(v, R * (1.10 if big else 1.05))
        d.line([(x0, y0), (x1, y1)], fill=ink, width=S * (3 if big else 2))
        if i % 10 == 0:
            x, y = at(v, R * 0.82)
            d.text((x, y), str(i // 5), fill=ink, font=f, anchor="mm")
    # plug screw of the zero corrector under the scale
    d.ellipse([cx - S * 10, H - S * 22, cx + S * 10, H - S * 2], fill=(60, 58, 54, 255))
    save(img, (W // S, H // S), name, mirror=True)


def make_detpanel(name):
    """Aluminium panel of the detector block: brushing, ticks around the knob, toggle marks (a dot - on, a
    circle - off) and a rim around the lamp. No letters; the picture is in model coordinates (x left to
    right), the marks are symmetric - no mirroring needed."""
    x0, x1, z0, z1 = L.PLATE
    k = 4000 * 2
    W, H = int((x1 - x0) * k), int((z1 - z0) * k)
    rnd = random.Random(7)
    img = Image.new("RGBA", (W, H), (170, 172, 170, 255))
    d = ImageDraw.Draw(img)
    for _ in range(900):
        y = rnd.uniform(0, H)
        c = rnd.randint(150, 192)
        d.line([(rnd.uniform(-W * 0.2, W), y), (rnd.uniform(0, W * 1.2), y)], fill=(c, c + 2, c, 255), width=1)

    def px(x, z):
        return (x - x0) * k, (z1 - z) * k
    ink = (40, 38, 36, 255)
    cx, cy = px(*L.KNOB)
    for i in range(7):
        a = math.radians(225.0 - 270.0 * i / 6)
        r0, r1 = 0.0195 * k, (0.0235 if i in (0, 6) else 0.022) * k
        d.line([(cx + r0 * math.cos(a), cy - r0 * math.sin(a)), (cx + r1 * math.cos(a), cy - r1 * math.sin(a))],
               fill=ink, width=4)
    tx, ty = px(*L.TOGGLE)
    d.ellipse([tx - 7, ty - 0.017 * k - 7, tx + 7, ty - 0.017 * k + 7], fill=ink)
    d.ellipse([tx - 7, ty + 0.017 * k - 7, tx + 7, ty + 0.017 * k + 7], outline=ink, width=3)
    lx, ly = px(*L.LAMP)
    r = 0.0135 * k
    d.ellipse([lx - r, ly - r, lx + r, ly + r], outline=ink, width=3)
    save(img, (W // 2, H // 2), name)


def make_pcb(name, w=512, h=384, seed=19):
    """Laminate board of the "Rubin": brown-red, copper traces under lacquer, pads, part outlines without
    letters; an edge connector along the edge."""
    rnd = random.Random(seed)
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (112, 46, 34, 255))
    d = ImageDraw.Draw(img)
    copper = (196, 150, 84, 255)
    pads = [(rnd.uniform(0.05, 0.95) * W, rnd.uniform(0.06, 0.86) * H) for _ in range(90)]
    for i in range(len(pads) - 1):
        if rnd.random() < 0.65:
            (xa, ya), (xb, yb) = pads[i], pads[(i + rnd.randint(1, 5)) % len(pads)]
            d.line([(xa, ya), (xb, ya), (xb, yb)], fill=(138, 64, 44, 255), width=S * 6)
            d.line([(xa, ya), (xb, ya), (xb, yb)], fill=copper, width=S * 2)
    for x, y in pads:
        d.ellipse([x - S * 5, y - S * 5, x + S * 5, y + S * 5], fill=copper)
        d.ellipse([x - S * 2, y - S * 2, x + S * 2, y + S * 2], fill=(30, 22, 18, 255))
    # parts: resistors, capacitors - coloured blobs with leads
    cols = [(60, 110, 160), (176, 60, 40), (210, 180, 120), (70, 70, 74), (190, 120, 40)]
    for _ in range(26):
        x, y = rnd.uniform(0.06, 0.9) * W, rnd.uniform(0.08, 0.80) * H
        c = rnd.choice(cols)
        if rnd.random() < 0.5:
            d.rounded_rectangle([x, y, x + W * 0.05, y + H * 0.025], radius=S * 4, fill=c + (255,))
        else:
            r = W * rnd.uniform(0.012, 0.024)
            d.ellipse([x - r, y - r, x + r, y + r], fill=c + (255,), outline=(30, 26, 22, 255), width=S)
    n = 18
    for i in range(n):
        x = W * (0.10 + 0.80 * (i + 0.5) / n)
        d.rectangle([x - W * 0.014, H * 0.90, x + W * 0.014, H * 0.99], fill=(214, 178, 76, 255))
    save(img, (w, h), name)


def make_dial(name, n):
    """Channel selector dial: a dark ring, 12 ticks and the digits 1-12 in white; the centre is transparent."""
    W = n * S
    c = W / 2
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, W - 1, W - 1], fill=(36, 34, 32, 255))
    ink = (224, 222, 210, 255)
    f = font(int(W * 0.10))
    for k in range(12):
        a = 2 * math.pi * k / 12 - math.pi / 2
        d.line([(c + c * 0.86 * math.cos(a), c + c * 0.86 * math.sin(a)), (c + c * 0.97 * math.cos(a),
                                                                          c + c * 0.97 * math.sin(a))],
               fill=ink, width=S * 3)
        d.text((c + c * 0.70 * math.cos(a), c + c * 0.70 * math.sin(a)), str(k + 1), fill=ink, font=f, anchor="mm")
    hole = Image.new("L", (W, W), 255)
    ImageDraw.Draw(hole).ellipse([c - c * 0.52, c - c * 0.52, c + c * 0.52, c + c * 0.52], fill=0)
    alpha = Image.new("L", (W, W), 0)
    ImageDraw.Draw(alpha).ellipse([0, 0, W - 1, W - 1], fill=255)
    img.putalpha(Image.composite(alpha, Image.new("L", (W, W), 0), hole))
    save(img, (n, n), name)


def worn(img, seed):
    """The decal is worn: transparency patches and fading."""
    W, H = img.size
    rnd = random.Random(seed)
    a = img.getchannel("A")
    m = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(m)
    for _ in range(26):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(0.02, 0.07) * W
        d.ellipse([x - r, y - r, x + r, y + r], fill=rnd.randint(40, 170))
    m = m.filter(ImageFilter.GaussianBlur(W * 0.01))
    img.putalpha(Image.composite(a, Image.new("L", (W, H), 0), m))
    fade = Image.new("RGBA", (W, H), (230, 226, 210, 0))
    fade.putalpha(m.point(lambda v: int((255 - v) * 0.25)))
    return Image.alpha_composite(img, fade)


def make_radiation(name, n):
    """Radiation sign on a yellow circle, a black border."""
    W = n * S
    c = W / 2
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, W - 1, W - 1], fill=(20, 20, 20, 255))
    d.ellipse([W * 0.05, W * 0.05, W * 0.95, W * 0.95], fill=(232, 190, 40, 255))
    r0, r1 = c * 0.20, c * 0.78
    for k in range(3):
        a = -90 + 120 * k - 30
        d.pieslice([c - r1, c - r1, c + r1, c + r1], a, a + 60, fill=(20, 20, 20, 255))
    d.ellipse([c - r0, c - r0, c + r0, c + r0], fill=(232, 190, 40, 255))
    d.ellipse([c - r0 * 0.65, c - r0 * 0.65, c + r0 * 0.65, c + r0 * 0.65], fill=(20, 20, 20, 255))
    save(worn(img, 5), (n, n), name)


def make_sun(name, n):
    """Round decal without text: an orange sun with rays on blue."""
    W = n * S
    c = W / 2
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([0, 0, W - 1, W - 1], fill=(46, 84, 150, 255))
    for k in range(12):
        a = 2 * math.pi * k / 12
        b = a + 0.12
        d.polygon([(c, c), (c + c * 0.82 * math.cos(a), c + c * 0.82 * math.sin(a)),
                   (c + c * 0.82 * math.cos(b), c + c * 0.82 * math.sin(b))], fill=(236, 150, 40, 255))
    d.ellipse([c - c * 0.38, c - c * 0.38, c + c * 0.38, c + c * 0.38], fill=(244, 176, 52, 255))
    save(worn(img, 9), (n, n), name)


def make_bolt(name, w, h):
    """Rectangular decal without text: a white lightning bolt on red with a white frame."""
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=W * 0.06, fill=(236, 232, 220, 255))
    d.rounded_rectangle([W * 0.06, H * 0.06, W * 0.94, H * 0.94], radius=W * 0.04, fill=(178, 40, 32, 255))
    d.polygon([(W * 0.58, H * 0.14), (W * 0.30, H * 0.56), (W * 0.48, H * 0.56), (W * 0.40, H * 0.88),
               (W * 0.72, H * 0.42), (W * 0.53, H * 0.42)], fill=(240, 236, 226, 255))
    save(worn(img, 13), (w, h), name)


if __name__ == "__main__":
    make_screen_off("decal_screen_off.png")
    make_screen_frames("decal_screen_f")
    make_meter("decal_meter.png")
    make_detpanel("decal_detpanel.png")
    make_pcb("decal_pcb.png")
    make_dial("decal_dial.png", 256)
    make_radiation("decal_radiation.png", 256)
    make_sun("decal_sun.png", 256)
    make_bolt("decal_bolt.png", 192, 256)
