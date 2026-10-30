"""Working frames of the M36 screens: the screen is its own section, the frames are small PAAs
cycled by OZL_WorkFx (view "frames"). They are derived from the finished decals of
make_decals.py - the same picture, only the part that "lives" changes - so Pillow is not
needed: build_m36.py calls make() inside Blender (numpy ships with Blender) before the model
is built and redraws the frames only when the decal is newer.

- CRT (decal_crt_on.png -> decal_crt_fNN.png): the column of lines on the right creeps up one
  line per frame (12 lines - 12 frames, the loop seam is invisible), the progress bar grows,
  a light sweep band runs down the screen, the cursor frame on the map blinks (2 frames lit,
  2 dimmed).
- Laptop (decal_lcd_on.png -> decal_lcd_fNN.png): the selection frame walks over the
  available blocks of the tree (3 frames per block), the progress line at the bottom grows.

Positions in the pictures are fractions of the width and height, as in make_decals.py
(make_crt, make_lcd).
"""
import os

import bpy
import numpy as np

N_CRT = 12
N_LCD = 12


def load(path):
    """PNG -> array (height, width, RGBA), top row first, values 0..1 as in the file (byte values,
    no recalculation).
    """
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    a = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(a)
    bpy.data.images.remove(img)
    return a.reshape(h, w, 4)[::-1].copy()


def save(a, path):
    h, w = a.shape[:2]
    img = bpy.data.images.new(os.path.basename(path), w, h, alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(np.clip(a, 0.0, 1.0)[::-1]).ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def rgb(c):
    return np.array([v / 255.0 for v in c], np.float32)


def crt(src, n=N_CRT):
    a = load(src)
    H, W = a.shape[:2]
    bg = rgb((14, 7, 2))
    rh = H / 26.0
    my0 = 0.07 * H
    r0, r1 = int(round(my0 + 0.09 * H)), int(round(my0 + 0.09 * H + 12 * rh))
    c0, c1 = int(W * 0.74) + 3, int(W * 0.97) - 2
    # progress bar: inside the frame (0.755..0.955 W, 0.80..0.85 H), filled up to 0.8665 W
    bx0, bx1 = int(W * 0.755) + 3, int(W * 0.955) - 3
    by0, by1 = int(H * 0.80) + 3, int(H * 0.85) - 2
    full = a[by0:by1, int(W * 0.80)].copy()
    empty = a[by0:by1, int(W * 0.92)].copy()
    cx, cy, hw, hh = W * 0.60, H * 0.50, H * 0.105, H * 0.066 + 2
    cur = (slice(int(cy - hh), int(cy + hh) + 1), slice(int(cx - hw), int(cx + hw) + 1))
    ys = np.arange(H, dtype=np.float32)[:, None]
    out = []
    for f in range(n):
        b = a.copy()
        sh = int(round(f * (r1 - r0) / 12.0))
        b[r0:r1, c0:c1] = np.roll(a[r0:r1, c0:c1], -sh, axis=0)
        x_end = bx0 + (bx1 - bx0) * (0.14 + 0.80 * f / (n - 1))
        for x in range(bx0, bx1):
            b[by0:by1, x] = full if x < x_end else empty
        if f % 4 >= 2:                                          # cursor frame and its sign dimmed
            reg = b[cur]
            hi = (reg[..., 1] > 0.74) | (reg[..., 2] > 0.42)
            reg[hi, :3] = bg + (reg[hi, :3] - bg) * 0.28
        yc = -0.12 * H + 1.24 * H * f / n                       # sweep band, top to bottom
        gain = 1.0 + 0.55 * np.exp(-((ys - yc) / (0.045 * H)) ** 2)
        b[..., :3] = b[..., :3] * gain[..., None] + 0.04 * (gain[..., None] - 1.0)
        out.append(b)
    return out


def lcd(src, n=N_LCD):
    a = load(src)
    H, W = a.shape[:2]
    BG, WH, FR = rgb((8, 10, 150)), rgb((220, 222, 226)), rgb((80, 200, 210))
    rh, cw = H / 25.0, W / 80.0
    bw, bh = cw * 9, rh * 1.6
    m = 3.0                                                     # selection frame: 3 px off, 1 px

    def band(c, i, o):
        x, y = c
        xs, ys = np.arange(W)[None, :], np.arange(H)[:, None]
        dx, dy = np.abs(xs - x), np.abs(ys - y)
        outer = (dx <= bw / 2 + o) & (dy <= bh / 2 + o)
        inner = (dx <= bw / 2 + i) & (dy <= bh / 2 + i)
        return outer & ~inner, dx
    sel0 = (W * 0.28, rh * 14.0)
    route = [sel0, (W * 0.20, rh * 19.0), (W * 0.50, rh * 9.0), (W * 0.80, rh * 19.0)]
    ring0, dx0 = band(sel0, 1.0, m + 2.2)                       # margin: source frame is blurred
    base = a.copy()
    keep = (dx0 <= 2.0) & (np.arange(H)[:, None] < sel0[1])     # keep the connector above the block
    base[ring0 & ~keep, :3] = BG                                 # erase the frame
    sy0, sy1 = int(round(H - rh * 2.05)), int(round(H - rh * 1.8)) + 1
    sx0, sx1 = int(cw * 3), int(W - cw * 3)
    out = []
    for f in range(n):
        b = base.copy()
        c = route[(f // 3) % len(route)]
        core = band(c, m - 0.5, m + 0.6)[0]
        edge = band(c, m - 1.0, m + 1.1)[0] & ~core                # soft edge, matches the blur
        b[core, :3] = WH
        b[edge, :3] = b[edge, :3] * 0.5 + WH * 0.5
        x_end = int(sx0 + (sx1 - sx0) * (0.10 + 0.85 * f / (n - 1)))
        b[sy0:sy1, sx0:sx1, :3] = BG
        b[sy0:sy1, sx0:x_end, :3] = FR
        out.append(b)
    return out


def make(work):
    """Frames into work: [decal_crt_fNN.png], [decal_lcd_fNN.png]. Redrawn if the frames are missing
    or the decal (or this file) is newer. Returns the file names (relative to work).
    """
    names = {}
    for key, fn, n in (("crt", crt, N_CRT), ("lcd", lcd, N_LCD)):
        src = os.path.join(work, "decal_%s_on.png" % key)
        outs = ["decal_%s_f%02d.png" % (key, i) for i in range(n)]
        paths = [os.path.join(work, o) for o in outs]
        t = max(os.path.getmtime(src), os.path.getmtime(os.path.abspath(__file__)))
        if not all(os.path.exists(p) and os.path.getmtime(p) >= t for p in paths):
            for img, p in zip(fn(src), paths):
                save(img, p)
            print("frames: %s - %d" % (key, n))
        names[key] = outs
    return names
