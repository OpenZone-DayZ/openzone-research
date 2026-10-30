"""Screen, keyboard, paper and small marks of the M38 computer terminal of the Scientists
(system Python + Pillow). No lettering: the console disc carries the tape drive number
digit, the counter window has digits, the tag and nameplates are blank, and paper and
screen have strokes instead of text.

    python make_decals.py      -> ../work/decal_*.png

- decal_screen_off.png - CRT screen off (grey-green glass with a glare); the screen has its
  own texture;
- decal_screen_fNN.png - 12 "working" frames (OZL_WorkFx frames, 0.2 s each): green
  phosphor, a header line, on the left the media receiving table - rows are marked one by
  one (a mark in the first column, the current row highlighted), on the right the tape
  position scale grows and the bars shift left, at the bottom the input line is typed and
  the cursor blinks;
- decal_keys.png     - terminal keyboard: black keys of the main block, beige service keys
  on the right;
- decal_disc.png     - white disc with the tape drive number (digit "1");
- decal_counter.png  - hour counter window (drums with digits);
- decal_tag.png      - paper inventory tag without text (blank columns);
- decal_stack_top.png - top of the fan-fold paper stack: perforation at the edges, green
  stripes;
- decal_print.png    - printed web above the printer: stripes, perforation, lines of dots;
- decal_log.png      - media receiving log spread: light blue ruling, red margins, entries
  are ink strokes (no letters), a shadow in the fold.
"""
import os
import random
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import layout as L  # noqa: E402

WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 2                                   # supersampling
FONTS = "C:/Windows/Fonts/"


def px(m, k=1400):
    return int(m * k * S)


def save(img, name):
    img = img.resize((max(1, img.width // S), max(1, img.height // S)), Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path, img.size)


def font(name, h):
    return ImageFont.truetype(FONTS + name, max(8, int(h)))


def digit(d, box, s, fill, fname="arialbd.ttf"):
    x0, y0, x1, y1 = box
    f = font(fname, (y1 - y0) * 1.25)
    l, t, r, b = d.textbbox((0, 0), s, font=f)
    while (b - t) > (y1 - y0) or (r - l) > (x1 - x0):
        f = font(fname, f.size * 0.92)
        l, t, r, b = d.textbbox((0, 0), s, font=f)
    d.text(((x0 + x1 - (r - l)) / 2 - l, (y0 + y1 - (b - t)) / 2 - t), s, font=f, fill=fill)


def make_screen():
    k = 2600
    W, H = px(L.SCR_W, k), px(L.SCR_H, k)
    off = Image.new("RGB", (W, H), (40, 46, 42))
    d = ImageDraw.Draw(off)
    for i in range(H):
        t = max(0.0, 1.0 - i / (H * 0.85))
        d.line([(0, i), (W, i)], fill=(int(40 + 12 * t), int(46 + 14 * t), int(42 + 12 * t)))
    d.ellipse((W * 0.06, H * 0.05, W * 0.40, H * 0.28), fill=(70, 78, 74))
    off = off.filter(ImageFilter.GaussianBlur(12 * S))
    save(off.convert("RGBA"), "decal_screen_off.png")

    for fr in range(FRAMES):
        save(screen_frame(W, H, fr).convert("RGBA"), "decal_screen_f%02d.png" % fr)


FRAMES = 12                             # working frames: 12 x 0.2 s - a loop of 2.4 s
ROWS = 12                               # rows in the receiving table


def screen_frame(W, H, fr):
    """Working frame: the same layout every time; what changes are the row marks, the highlight of
    the current row, the tape scale, the bars (shift left by one per frame), the input line and
    the cursor.
    """
    BG, FG, HI, DIM = (3, 12, 5), (64, 226, 90), (186, 255, 190), (26, 110, 42)
    on = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(on)
    lw = max(2, int(W * 0.0035))
    cw, rh = W / 80.0, H / 24.0                                  # 80 x 24 cells, ES style
    # table rows, bars and input line words are the same in all frames
    rows = random.Random(38)
    cells = [[[rows.randint(1, 3) if i == 0 else rows.randint(2, 6) for _ in range(4)] for i in range(4)]
             for _ in range(ROWS)]
    bars = [random.Random(500 + k).uniform(0.2, 0.95) for k in range(FRAMES + 9)]
    typing = random.Random(77)
    words = [typing.randint(3, 7) for _ in range(6)]

    def dashes(x0, x1, y, col, sizes):
        x = x0
        for n in sizes:
            w = min(n * cw, x1 - x)
            if w > cw * 0.6:
                d.rectangle((x, y + rh * 0.28, x + w - cw * 0.3, y + rh * 0.72), fill=col)
            x += w + cw
            if x >= x1:
                break
    # header: an inverted line, a blinking receive sign on the right
    d.rectangle((0, 0, W, rh * 1.1), fill=DIM)
    for k_ in range(3):
        d.rectangle((cw * (3 + 16 * k_), rh * 0.3, cw * (11 + 16 * k_), rh * 0.8), fill=BG)
    if fr % 2 == 0:
        d.rectangle((cw * 70, rh * 0.25, cw * 76, rh * 0.85), fill=HI)
    # receiving table: columns and rows; the rows before the current one are marked, the current
    # one is highlighted
    tx0, tx1, ty0, ty1 = cw * 1.5, W * 0.62, rh * 2.0, rh * 19.5
    d.rectangle((tx0, ty0, tx1, ty1), outline=FG, width=lw)
    cols = [tx0, tx0 + cw * 6, tx0 + cw * 22, tx0 + cw * 36, tx1]
    for x in cols[1:-1]:
        d.line([(x, ty0), (x, ty1)], fill=DIM, width=lw)
    d.line([(tx0, ty0 + rh * 1.4), (tx1, ty0 + rh * 1.4)], fill=FG, width=lw)
    for i in range(4):
        dashes(cols[i] + cw, cols[i + 1] - cw * 2, ty0 + rh * 0.2, HI, (3, 4))
    cur = fr % ROWS
    for r in range(ROWS):
        y = ty0 + rh * (1.8 + r * 1.35)
        if r == cur:
            d.rectangle((tx0 + lw * 2, y, tx1 - lw * 2, y + rh * 1.15), fill=DIM)
        for i in range(4):
            dashes(cols[i] + cw * (3 if i == 0 else 1), cols[i + 1] - cw, y, HI if r == cur else FG, cells[r][i])
        if r < cur:                                              # received: first-column mark
            d.rectangle((cols[0] + cw * 0.8, y + rh * 0.25, cols[0] + cw * 2.2, y + rh * 0.85), fill=HI)
    # right side: the tape position (a scale with a slider) and bars
    rx0, rx1 = W * 0.66, W - cw * 1.5
    d.rectangle((rx0, ty0, rx1, rh * 9.0), outline=FG, width=lw)
    d.rectangle((rx0 + cw, rh * 3.5, rx1 - cw, rh * 4.6), outline=FG, width=lw)
    p = 0.10 + 0.82 * fr / (FRAMES - 1)
    d.rectangle((rx0 + cw + lw * 2, rh * 3.5 + lw * 2, rx0 + cw + lw * 2 + (rx1 - rx0 - cw * 2 - lw * 4) * p,
                 rh * 4.6 - lw * 2), fill=FG)
    for i in range(3):
        dashes(rx0 + cw, rx1 - cw * 3, rh * (5.6 + i * 1.1), DIM, (2, 3, 4, 2))
    d.rectangle((rx0, rh * 10.0, rx1, ty1), outline=FG, width=lw)
    n = 9
    bw = (rx1 - rx0 - cw * 2) / n
    for i in range(n):
        hgt = bars[fr + i] * (ty1 - rh * 12.0)
        x = rx0 + cw + i * bw
        d.rectangle((x + bw * 0.2, ty1 - rh * 1.0 - hgt, x + bw * 0.8, ty1 - rh * 1.0), fill=HI if i == n - 1 else FG)
    # the input line is typed word by word, the cursor blinks; the status line is under it
    shown = words[:1 + (fr * len(words)) // FRAMES]
    xe = cw * 2 + sum((k + 1) * cw for k in shown)
    dashes(cw * 2, W * 0.8, H - rh * 2.6, FG, shown)
    if fr % 2 == 0:
        d.rectangle((xe, H - rh * 2.5, xe + cw, H - rh * 1.6), fill=HI)
    dashes(cw * 2, W * 0.8, H - rh * 1.3, DIM, (2, 5, 3, 4))
    glow = on.filter(ImageFilter.GaussianBlur(3 * S))
    on = ImageChops.add(on, glow.point(lambda v: v // 2))
    d = ImageDraw.Draw(on)
    for yy in range(0, H, 3 * S):
        d.line([(0, yy), (W, yy)], fill=(0, 0, 0), width=1)
    vign = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vign).rounded_rectangle((W * 0.02, H * 0.03, W * 0.98, H * 0.97), radius=int(W * 0.08), fill=255)
    vign = vign.filter(ImageFilter.GaussianBlur(W * 0.04))
    return Image.composite(on, Image.new("RGB", (W, H), BG), vign)


def make_keys():
    """Main block of 15 x 5 rows of black keys, a beige service block 4 x 5 on the right; a
    space bar.
    """
    x0, x1, y0, y1 = L.KEYS
    W, H = px(x1 - x0, 2000), px(y1 - y0, 2000)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    rnd = random.Random(7)
    BLACK, BEIGE = (30, 30, 32), (210, 202, 182)
    gap = 0.0018 * 2000 * S
    u = (W - gap) / 20.5
    kh = (H - gap) / 5.0

    def key(cx, cy, w, h, tone):
        k = rnd.uniform(0.92, 1.0)
        c = tuple(int(v * k) for v in tone) + (255,)
        d.rounded_rectangle((cx + gap, cy + gap, cx + w * u - gap, cy + h * kh - gap), radius=int(gap), fill=c)
        hl = tuple(min(255, int(v * 1.6 + 20)) for v in tone) + (255,)
        d.line([(cx + gap * 2, cy + gap * 1.6), (cx + w * u - gap * 2, cy + gap * 1.6)], fill=hl, width=S)
    rows = [(0, [(i, 1) for i in range(14)] + [(14, 1)]),
            (1, [(0, 1.5)] + [(1.5 + i, 1) for i in range(12)] + [(13.5, 1.5)]),
            (2, [(0, 1.75)] + [(1.75 + i, 1) for i in range(11)] + [(12.75, 2.25)]),
            (3, [(0, 2.25)] + [(2.25 + i, 1) for i in range(10)] + [(12.25, 2.75)]),
            (4, [(0, 1.5), (1.5, 1.5), (3.0, 9.0), (12.0, 1.5), (13.5, 1.5)])]
    for r, ks in rows:
        for x, w in ks:
            key(x * u, r * kh, w, 1, BLACK)
    for i in range(4):
        for j in range(5):
            key((16.0 + i * 1.1) * u, j * kh, 1, 1, BEIGE)
    save(img, "decal_keys.png")


def make_disc():
    W = px(L.DISC[2] * 2, 2400)
    img = Image.new("RGBA", (W, W), (236, 234, 226, 255))
    d = ImageDraw.Draw(img)
    d.ellipse((W * 0.06, W * 0.06, W * 0.94, W * 0.94), outline=(150, 150, 146, 255), width=max(2, W // 60))
    digit(d, (W * 0.30, W * 0.18, W * 0.70, W * 0.82), "1", (20, 20, 20, 255))
    save(img, "decal_disc.png")


def make_counter():
    x0, x1, z0, z1 = L.COUNTER
    W, H = px(x1 - x0, 3000), px(z1 - z0, 3000)
    img = Image.new("RGBA", (W, H), (18, 18, 18, 255))
    d = ImageDraw.Draw(img)
    n = 5
    cw = W / n
    for i, s in enumerate("03721"):
        d.rectangle((i * cw + S, S * 2, (i + 1) * cw - S, H - S * 2), fill=(232, 230, 222, 255) if i < 4 else
                    (200, 40, 32, 255))
        digit(d, (i * cw + cw * 0.2, H * 0.2, (i + 1) * cw - cw * 0.2, H * 0.8), s,
              (20, 20, 20, 255) if i < 4 else (240, 240, 240, 255), "arial.ttf")
    save(img, "decal_counter.png")


def make_tag():
    x0, x1, z0, z1 = L.TAG
    W, H = px(x1 - x0, 2400), px(z1 - z0, 2400)
    img = Image.new("RGBA", (W, H), (236, 222, 170, 255))
    d = ImageDraw.Draw(img)
    lw = max(1, S)
    d.rectangle((W * 0.03, H * 0.08, W * 0.97, H * 0.92), outline=(120, 100, 70, 255), width=lw)
    for k in (0.36, 0.64):
        d.line([(W * 0.03, H * k), (W * 0.97, H * k)], fill=(120, 100, 70, 255), width=lw)
    d.line([(W * 0.30, H * 0.08), (W * 0.30, H * 0.92)], fill=(120, 100, 70, 255), width=lw)
    img = img.filter(ImageFilter.GaussianBlur(0.6 * S))
    save(img, "decal_tag.png")


def fanfold(W, H, k, rnd, printed):
    """Paper web: perforation at the edges, green stripes every 1/2 in; printed - lines made of
    dots.
    """
    img = Image.new("RGBA", (W, H), (240, 238, 228, 255))
    d = ImageDraw.Draw(img)
    m = 0.5 * 0.0254 * k * S                                     # margin with perforation, 1/2 in
    bar = 0.5 * 0.0254 * k * S
    y = 0.0
    i = 0
    while y < H:
        if i % 2 == 0:
            d.rectangle((m, y, W - m, y + bar), fill=(206, 228, 204, 255))
        y += bar
        i += 1
    d.line([(m, 0), (m, H)], fill=(200, 200, 190, 255), width=S)
    d.line([(W - m, 0), (W - m, H)], fill=(200, 200, 190, 255), width=S)
    step = 0.5 * 0.0254 * k * S
    r = 0.002 * k * S
    yy = step / 2
    while yy < H:
        for cx in (m / 2, W - m / 2):
            d.ellipse((cx - r, yy - r, cx + r, yy + r), fill=(60, 62, 60, 255))
        yy += step
    if printed:
        line = 1 / 6 * 0.0254 * k * S                           # 6 lines per inch
        dot = max(1, int(0.00045 * k * S))
        y = m * 0.8
        while y < H - line:
            x = m * 1.4
            if rnd.random() < 0.18:
                y += line
                continue
            end = W - m * 1.4 - rnd.uniform(0, W * 0.4)
            while x < end:
                n = rnd.randint(2, 9)
                w = n * 0.00254 * k * S                         # 10 characters per inch
                for xx in range(int(x), int(min(x + w, end)), dot * 3):
                    for dy in range(0, int(line * 0.55), dot * 3):
                        if rnd.random() < 0.7:
                            d.rectangle((xx, y + dy, xx + dot, y + dy + dot), fill=(48, 48, 56, 255))
                x += w + 0.00254 * k * S
            y += line
    return img


def make_paper():
    rnd = random.Random(3)
    k = 2400
    x0, x1, y0, y1, _, _ = L.STACK
    W, H = px(x1 - x0, k), px(y1 - y0, k)
    save(fanfold(W, H, k, rnd, False), "decal_stack_top.png")
    x0, x1, z0, z1 = L.PRINT
    W, H = px(x1 - x0, k), px(z1 - z0, k)
    save(fanfold(W, H, k, rnd, True), "decal_print.png")


def make_log():
    """Log spread: two pages side by side, light blue lines every 7 mm, a red margin, entries are
    ink strokes of different length (no letters), a shadow in the fold in the middle.
    """
    pw, ph = L.LOG_PAGE
    k = 2400
    W, H = px(2 * pw, k), px(ph, k)
    img = Image.new("RGBA", (W, H), (238, 234, 220, 255))
    d = ImageDraw.Draw(img)
    rnd = random.Random(52)
    line = 0.007 * k * S
    lw = max(1, S)
    rows = int((H - line * 4) / line)
    for side in (0, 1):
        x0 = side * W / 2
        y = line * 3.0
        while y < H - line:
            d.line([(x0 + W * 0.01, y), (x0 + W / 2 - W * 0.01, y)], fill=(160, 186, 214, 255), width=lw)
            y += line
        mx = x0 + (W * 0.08 if side == 1 else W / 2 - W * 0.08)
        d.line([(mx, 0), (mx, H)], fill=(210, 120, 120, 255), width=lw)
        # entries: left page full, right page filled to the middle (the log is in use)
        last = rows if side == 0 else rows // 2
        for r in range(last):
            yy = line * (3.0 + r) - line * 0.35
            x = x0 + (W * 0.10 if side == 1 else W * 0.02)
            xe = x0 + W / 2 - W * (0.03 if side == 1 else 0.10) - rnd.uniform(0, W * 0.10)
            while x < xe:
                w = rnd.uniform(0.010, 0.032) * k * S
                d.line([(x, yy + rnd.uniform(-0.6, 0.6) * S), (min(x + w, xe), yy + rnd.uniform(-0.6, 0.6) * S)],
                       fill=(40, 46, 96, 255), width=max(1, int(0.0006 * k * S)))
                x += w + rnd.uniform(0.004, 0.009) * k * S
    shade = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(shade)
    n = int(W * 0.06)
    for i in range(n):
        a = int(70 * (1 - i / n) ** 2)
        sd.line([(W / 2 - i, 0), (W / 2 - i, H)], fill=a)
        sd.line([(W / 2 + i, 0), (W / 2 + i, H)], fill=a)
    img = Image.composite(Image.new("RGBA", (W, H), (120, 112, 96, 255)), img, shade)
    save(img, "decal_log.png")


if __name__ == "__main__":
    make_screen()
    make_keys()
    make_disc()
    make_counter()
    make_tag()
    make_paper()
    make_log()
