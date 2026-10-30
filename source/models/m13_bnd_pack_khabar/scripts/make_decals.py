"""Decals for the lead box (system Python + Pillow): the tops of the money bundles and loose notes -
hryvnias (uah.py: size and design by denomination, digits without inscriptions), the back of the deck
and three face-up cards (suits and digits only), wristwatch dials (ticks, digits, hands - no
inscriptions), the pager screen "off" and "work" frames (seven-segment digits of the number and icons),
a radiation sign in stencil paint. No letters. Bundles, cards and watches are turned the way they lie
(loot.py): kmats projects decals from above, along the world axes.

    python make_decals.py      -> ../work/decal_*.png, ../work/pager_*.png
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import loot  # noqa: E402
import uah  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscale: smooth edges
PX_M = 2400                             # pixels per metre for decals on the loot
PX_M_DIAL = 5600                        # for dials (small)


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


def rotated(img, deg, name, w_m, h_m, px_m=PX_M):
    """Image of an item w_m x h_m metres, rotated by deg (counter-clockwise, top view) with transparent
    corners: the size is the frame of the rotated rectangle."""
    a = math.radians(deg)
    bw = w_m * abs(math.cos(a)) + h_m * abs(math.sin(a))
    bh = w_m * abs(math.sin(a)) + h_m * abs(math.cos(a))
    big = img.rotate(deg, resample=Image.BICUBIC, expand=True)
    save(big, (max(8, int(bw * px_m)), max(8, int(bh * px_m))), name)
    return bw, bh


def note(nm, seed, wear, fold=None):
    """Top of a bundle or a loose note nm - a hryvnia note of its denomination (loot.UAH, design in uah.py)
    supersampled by S; the bundle is held by rubber bands (geometry), there is no paper band over the portrait."""
    return uah.note_image(loot.UAH[nm], PX_M, seed=seed, wear=wear, fold=fold, S=S)


def card_back():
    w, h = int(loot.CARD[0] * 1000) * S, int(loot.CARD[1] * 1000) * S
    img = Image.new("RGBA", (w, h), (236, 232, 222, 255))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([S * 3, S * 3, w - S * 3, h - S * 3], radius=S * 4, fill=(150, 34, 36, 255))
    for i in range(-h, w + h, S * 5):
        d.line([(i, 0), (i + h, h)], fill=(176, 60, 56, 255), width=S)
        d.line([(i + h, 0), (i, h)], fill=(176, 60, 56, 255), width=S)
    d.rounded_rectangle([S * 3, S * 3, w - S * 3, h - S * 3], radius=S * 4, outline=(236, 232, 222, 255), width=S * 2)
    return img


def suit(d, kind, cx, cy, s, col):
    if kind == "h":
        d.ellipse([cx - s, cy - s * 0.9, cx, cy + s * 0.1], fill=col)
        d.ellipse([cx, cy - s * 0.9, cx + s, cy + s * 0.1], fill=col)
        d.polygon([(cx - s * 0.98, cy - s * 0.25), (cx + s * 0.98, cy - s * 0.25), (cx, cy + s)], fill=col)
    elif kind == "d":
        d.polygon([(cx, cy - s), (cx + s * 0.7, cy), (cx, cy + s), (cx - s * 0.7, cy)], fill=col)
    else:   # spades: an upside-down heart and a stem
        d.ellipse([cx - s, cy - s * 0.1, cx, cy + s * 0.9], fill=col)
        d.ellipse([cx, cy - s * 0.1, cx + s, cy + s * 0.9], fill=col)
        d.polygon([(cx - s * 0.98, cy + s * 0.25), (cx + s * 0.98, cy + s * 0.25), (cx, cy - s)], fill=col)
        d.polygon([(cx, cy + s * 0.3), (cx - s * 0.4, cy + s * 1.2), (cx + s * 0.4, cy + s * 1.2)], fill=col)


def card_face(code):
    """Face-up card: the digit in the corners and the suits laid out by rank."""
    val, st = code[:-1], code[-1]
    n = int(val)
    w, h = int(loot.CARD[0] * 1000) * S, int(loot.CARD[1] * 1000) * S
    img = Image.new("RGBA", (w, h), (238, 236, 228, 255))
    d = ImageDraw.Draw(img)
    col = (180, 28, 30, 255) if st in "hd" else (24, 24, 24, 255)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=S * 4, outline=(170, 168, 160, 255), width=S)
    f = font(int(h * 0.13))
    d.text((w * 0.14, h * 0.09), val, fill=col, font=f, anchor="mm")
    d.text((w * 0.86, h * 0.91), val, fill=col, font=f, anchor="mm")
    suit(d, st, w * 0.14, h * 0.19, w * 0.05, col)
    suit(d, st, w * 0.86, h * 0.81, w * 0.05, col)
    rows = {7: [2, 1, 2, 2], 9: [2, 2, 1, 2, 2], 10: [2, 1, 2, 2, 1, 2]}[n]
    for i, k in enumerate(rows):
        y = h * (0.22 + 0.56 * i / (len(rows) - 1))
        for j in range(k):
            x = w * (0.5 if k == 1 else (0.32 + 0.36 * j))
            suit(d, st, x, y, w * 0.08, col)
    return img


# --- dials ---------------------------------------------------------------------------------
DIALS = {
    # field, ticks and digits, hands, seconds hand, digits 12/3/6/9 or ticks only, small seconds dial
    "black": ((24, 24, 26), (226, 224, 214), (232, 230, 220), (196, 40, 32), False, False),
    "gold": ((206, 178, 112), (96, 70, 30), (90, 64, 26), (90, 64, 26), False, False),
    "white": ((236, 232, 220), (30, 30, 32), (28, 28, 30), (170, 30, 28), True, False),
    "blue": ((30, 46, 92), (210, 212, 216), (220, 222, 226), (220, 222, 226), False, False),
    "white2": ((228, 218, 192), (34, 32, 30), (40, 34, 28), (40, 34, 28), True, True),
}


def dial(style, seed):
    """Dial face up, 12 o'clock at the top of the image: a field with a faint "sun", minute marks, hour
    ticks (some with digits 12, 3, 6, 9), hands set to a random time."""
    field, mark, hand, sec, numerals, small_sec = DIALS[style]
    W = 400
    c = W / 2
    R = W / 2 - 2
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([c - R, c - R, c + R, c + R], fill=field + (255,))
    # "sun": lighter toward the centre on one side
    glow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([c - R * 0.9, c - R * 0.9, c + R * 0.2, c + R * 0.2], fill=(255, 255, 255, 34))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(W * 0.08)))
    d = ImageDraw.Draw(img)
    for k in range(60):
        a = math.radians(90 - 6 * k)
        r0, w_ = (R * 0.80, 9) if k % 5 == 0 else (R * 0.90, 3)
        if k % 5 == 0 and numerals and k % 15 == 0:
            continue
        x0, y0 = c + r0 * math.cos(a), c - r0 * math.sin(a)
        x1, y1 = c + R * 0.96 * math.cos(a), c - R * 0.96 * math.sin(a)
        d.line([(x0, y0), (x1, y1)], fill=mark + (255,), width=w_)
    if numerals:
        f = font(int(R * 0.30))
        for k, txt in ((0, "12"), (15, "3"), (30, "6"), (45, "9")):
            if small_sec and txt == "6":
                continue
            a = math.radians(90 - 6 * k)
            d.text((c + R * 0.76 * math.cos(a), c - R * 0.76 * math.sin(a)), txt, fill=mark + (255,), font=f, anchor="mm")
    if small_sec:
        sc = (c, c + R * 0.45)
        d.ellipse([sc[0] - R * 0.20, sc[1] - R * 0.20, sc[0] + R * 0.20, sc[1] + R * 0.20], outline=mark + (255,), width=3)
    rnd = random.Random(seed)
    hh, mm, ss = rnd.uniform(0, 12), rnd.uniform(0, 60), rnd.uniform(0, 60)

    def hand_(ang_deg, length, width, col, tail=0.15):
        a = math.radians(90 - ang_deg)
        dx, dy = math.cos(a), -math.sin(a)
        px, py = -dy, dx
        tip = (c + dx * length, c + dy * length)
        back = (c - dx * length * tail, c - dy * length * tail)
        pts = [(back[0] + px * width / 2, back[1] + py * width / 2), (tip[0] + px * width / 5, tip[1] + py * width / 5),
               (tip[0] - px * width / 5, tip[1] - py * width / 5), (back[0] - px * width / 2, back[1] - py * width / 2)]
        d.polygon(pts, fill=col + (255,))
    hand_(hh * 30, R * 0.52, 16, hand)
    hand_(mm * 6, R * 0.78, 11, hand)
    if not small_sec:
        hand_(ss * 6, R * 0.86, 4, sec, 0.25)
    d.ellipse([c - 9, c - 9, c + 9, c + 9], fill=hand + (255,))
    # shadow rim at the edge and a glass glint
    sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([c - R, c - R, c + R, c + R], outline=(0, 0, 0, 120), width=10)
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(5)))
    return img


# --- pager screen -----------------------------------------------------------------------------
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc", "7": "abc",
       "8": "abcdefg", "9": "abcdfg", "-": "g", " ": ""}


def seven_seg(d, x, y, w, h, ch, col):
    """A digit in seven segments (6 degree slant), top-left corner (x, y), size w x h."""
    t = w * 0.20
    sk = math.tan(math.radians(6))

    def P(px, py):
        return (x + px + (h - py) * sk, y + py)
    segs = {
        "a": [(t * 0.6, 0), (w - t * 0.6, 0), (w - t * 1.1, t), (t * 1.1, t)],
        "d": [(t * 1.1, h - t), (w - t * 1.1, h - t), (w - t * 0.6, h), (t * 0.6, h)],
        "g": [(t * 0.7, h / 2), (t * 1.2, h / 2 - t / 2), (w - t * 1.2, h / 2 - t / 2), (w - t * 0.7, h / 2),
              (w - t * 1.2, h / 2 + t / 2), (t * 1.2, h / 2 + t / 2)],
        "f": [(0, t * 0.6), (t, t * 1.1), (t, h / 2 - t * 0.6), (0, h / 2 - t * 0.2)],
        "e": [(0, h / 2 + t * 0.2), (t, h / 2 + t * 0.6), (t, h - t * 1.1), (0, h - t * 0.6)],
        "b": [(w, t * 0.6), (w, h / 2 - t * 0.2), (w - t, h / 2 - t * 0.6), (w - t, t * 1.1)],
        "c": [(w, h / 2 + t * 0.2), (w, h - t * 0.6), (w - t, h - t * 1.1), (w - t, h / 2 + t * 0.6)],
    }
    for s in SEG.get(ch, ""):
        d.polygon([P(*q) for q in segs[s]], fill=col)


def pager_screen(text, on, icon=False, cursor=False):
    """Pager LCD 38 x 13 mm: icons on the left (bell, new-message envelope), 8 character cells in the
    middle, a battery on the right. on - backlit (yellow-green), otherwise grey-green glass with no marks,
    with the shadows of the segments."""
    w_m, h_m = loot.PAGER_SCREEN[1]
    W, H = int(w_m * 16000) * S // 4, int(h_m * 16000) * S // 4
    bg = (150, 182, 104) if on else (112, 120, 104)
    img = Image.new("RGBA", (W, H), bg + (255,))
    d = ImageDraw.Draw(img)
    ink = (34, 44, 30, 255)
    ghost = tuple(int(c * 0.93) for c in bg) + (255,)
    cw, ch_ = W * 0.078, H * 0.60
    step = cw * 1.16
    x0, y0 = W * 0.155, H * 0.20
    for k in range(8):
        seven_seg(d, x0 + k * step, y0, cw, ch_, "8", ghost)
    if on:
        for k, c in enumerate(text.rjust(8)[-8:]):
            seven_seg(d, x0 + k * step, y0, cw, ch_, c, ink)
        if cursor:
            d.rectangle([x0 + 7 * step, y0 + ch_ * 1.06, x0 + 7 * step + cw * 0.8, y0 + ch_ * 1.16], fill=ink)
        # bell
        bx, by = W * 0.04, H * 0.16
        d.polygon([(bx, by + H * 0.26), (bx + W * 0.03, by), (bx + W * 0.06, by + H * 0.26)], fill=ink)
        d.rectangle([bx - W * 0.004, by + H * 0.26, bx + W * 0.064, by + H * 0.30], fill=ink)
        # battery on the right
        rx, ry = W * 0.925, H * 0.22
        d.rectangle([rx, ry, rx + W * 0.045, ry + H * 0.17], outline=ink, width=S)
        d.rectangle([rx + W * 0.045, ry + H * 0.05, rx + W * 0.052, ry + H * 0.12], fill=ink)
        d.rectangle([rx + W * 0.007, ry + H * 0.035, rx + W * 0.03, ry + H * 0.135], fill=ink)
        if icon:
            # envelope - new message
            ex, ey = W * 0.035, H * 0.56
            d.rectangle([ex, ey, ex + W * 0.075, ey + H * 0.24], outline=ink, width=S)
            d.line([(ex, ey), (ex + W * 0.0375, ey + H * 0.14), (ex + W * 0.075, ey)], fill=ink, width=S)
    # frame and the shadow of the window visor
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 42, 38, 255), width=S * 2)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([0, 0, W, H * 0.16], fill=(0, 0, 0, 70))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(H * 0.05)))
    return img


# number on the screen: appears digit by digit from the right, the envelope blinks (8 frames, OZL_WorkFx frames)
PAGER_MSG = "2150638"
PAGER_FRAMES = 8


def make_pager():
    w_m, h_m = loot.PAGER_SCREEN[1]
    size = (int(w_m * 8000), int(h_m * 8000))
    save(pager_screen("", False), size, "pager_off.png")
    for i in range(PAGER_FRAMES):
        txt = PAGER_MSG[:i] if i < PAGER_FRAMES - 1 else PAGER_MSG
        save(pager_screen(txt, True, icon=(i % 2 == 0), cursor=(i < PAGER_FRAMES - 1)), size, "pager_f%d.png" % i)


def make_spray_trefoil(name, px):
    """Radiation sign in stencil paint: yellow, ragged edge, stencil bridges, drips."""
    W = px * S
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    m = Image.new("L", (W, W), 0)
    d = ImageDraw.Draw(m)
    cx = cy = W / 2
    R, r0 = W * 0.40, W * 0.08
    for k in range(3):
        a = 90 + 120 * k
        d.pieslice([cx - R, cy - R, cx + R, cy + R], -(a + 30), -(a - 30), fill=255)
    d.ellipse([cx - r0 * 1.6, cy - r0 * 1.6, cx + r0 * 1.6, cy + r0 * 1.6], fill=0)
    d.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], fill=255)
    # stencil bridges
    for k in range(3):
        a = math.radians(90 + 120 * k)
        x, y = cx + R * 0.62 * math.cos(a), cy - R * 0.62 * math.sin(a)
        d.line([(x - W * 0.08 * math.sin(a), y - W * 0.08 * math.cos(a)),
                (x + W * 0.08 * math.sin(a), y + W * 0.08 * math.cos(a))], fill=0, width=int(W * 0.02))
    rnd = random.Random(5)
    for _ in range(9):
        x = cx + rnd.uniform(-R, R) * 0.8
        y0 = cy + rnd.uniform(0.0, R * 0.6)
        d.line([(x, y0), (x, y0 + rnd.uniform(W * 0.06, W * 0.22))], fill=200, width=int(W * 0.012))
    m = m.filter(ImageFilter.GaussianBlur(W * 0.006))
    noise = Image.effect_noise((W, W), 70).filter(ImageFilter.GaussianBlur(S))
    m = Image.composite(m, Image.new("L", (W, W), 0), noise.point(lambda v: 255 if v > 70 else 0))
    yellow = Image.new("RGBA", (W, W), (214, 172, 34, 255))
    img = Image.composite(yellow, img, m.point(lambda v: int(v * 0.92)))
    save(img, (px, px), name)


if __name__ == "__main__":
    for i, (nm, c, deg, z, t) in enumerate(loot.CASH):
        rotated(note(nm, i, 0.45), deg, "decal_%s.png" % nm, *loot.note_size(nm))
    for i, (nm, c, deg, z) in enumerate(loot.NOTES):
        rotated(note(nm, i + 5, 0.75, fold=0.48 + 0.06 * i), deg, "decal_%s.png" % nm, *loot.note_size(nm))
    rotated(card_back(), loot.DECK[2], "decal_deck.png", *loot.CARD)
    for nm, c, deg, z, code in loot.FAN:
        rotated(card_face(code), deg, "decal_%s.png" % nm, *loot.CARD)
    for i, w in enumerate(loot.WATCHES + [loot.WATCH_TILT]):
        nm, c, deg, r = w[0], w[1], w[2], w[3]
        style = w[6] if len(w) > 7 else w[5]
        dr = 2 * r * 0.80
        rotated(dial(style, 11 + i), deg - 90.0, "decal_dial_%s.png" % nm, dr, dr, PX_M_DIAL)
    make_pager()
    make_spray_trefoil("decal_trefoil_spray.png", 256)
