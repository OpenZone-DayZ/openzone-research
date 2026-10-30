"""LCD display frames of M75 for the "working" state (OZL_WorkFx frames): the DRG-01T1 measures loot
("khabar"), the reading changes from measurement to measurement.

Drawn by Blender itself (numpy and bpy.data.images, no Pillow) with the same construction as
make_lcd() in make_decals.py: four slanted seven-segment digit places, a dot after the first, the
visor shadow on top, a dark glass edge, 4x supersampling and downscaling. So the frames appear on any
run of build_m75.py (and in the bake machine's run), and make_decals.py need not be run for them. The
"off" state is decal_lcd_off.png from make_decals.py (blank glass with a pale shadow of segments).

    import lcd_frames
    names = lcd_frames.write(WORK, ["0152", "0148", ...])   # -> work/decal_lcd_f00.png ...
"""
import math
import os

import numpy as np

S = 4                                    # supersampling, as in make_decals.py
LCD_W, LCD_H = 0.049, 0.017              # display glass, m (build_m75.LCD)
BG_ON, INK_ON = (176, 196, 150), (22, 28, 22)       # backlight and segments, as in decal_lcd_on.png
EDGE = (38, 42, 36)
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
       "7": "abc", "8": "abcdefg", "9": "abcdfg"}


def _bar(X, Y, ax, ay, bx, by, th):
    """A segment of thickness th with square ends (like ImageDraw.line with width)."""
    dx, dy = bx - ax, by - ay
    ln = math.hypot(dx, dy)
    t = ((X - ax) * dx + (Y - ay) * dy) / (ln * ln)
    d = np.abs((X - ax) * dy - (Y - ay) * dx) / ln
    return (t >= 0.0) & (t <= 1.0) & (d <= th / 2.0)


def image(text, bg=BG_ON, ink=INK_ON, px=196, dot=1):
    """Display: text is four digits, a dot after the dot-th; returns an array (h, px, 3) sRGB 0..1, rows
    from the top."""
    h = int(round(px * LCD_H / LCD_W))
    W, H = px * S, h * S
    X, Y = np.meshgrid(np.arange(W) + 0.5, np.arange(H) + 0.5)
    img = np.empty((H, W, 3))
    img[:] = np.array(bg[:3]) / 255.0
    # visor shadow: a 22 % strip at the top, blurred (Gaussian, sigma 0.07 of the height), black at 60/255
    sig = H * 0.07
    a = np.array([0.5 * math.erfc((y - H * 0.22) / (math.sqrt(2.0) * sig)) for y in np.arange(H) + 0.5]) * 60 / 255
    img *= (1.0 - a)[:, None, None]
    cw, chh, gap = W * 0.13, H * 0.60, W * 0.06
    x, y0, th = W * 0.20, H * 0.20, int(H * 0.08)
    sk = 0.12 * cw
    mask = np.zeros((H, W), bool)
    for i, ch in enumerate(text):
        pts = {"a": ((x, y0), (x + cw, y0)), "b": ((x + cw, y0), (x + cw, y0 + chh / 2)),
               "c": ((x + cw, y0 + chh / 2), (x + cw, y0 + chh)), "d": ((x, y0 + chh), (x + cw, y0 + chh)),
               "e": ((x, y0 + chh / 2), (x, y0 + chh)), "f": ((x, y0), (x, y0 + chh / 2)),
               "g": ((x, y0 + chh / 2), (x + cw, y0 + chh / 2))}
        for s in SEG.get(ch, ""):
            (ax, ay), (bx, by) = pts[s]
            mask |= _bar(X, Y, ax + sk * (1 - 2 * (ay - y0) / chh), ay, bx + sk * (1 - 2 * (by - y0) / chh), by, th)
        if i == dot - 1:
            r = H * 0.04
            cx = x + cw + gap * 0.22 + r
            mask |= (X - cx) ** 2 + (Y - H * 0.80) ** 2 <= r * r
        x += cw + gap
    img[mask] = np.array(ink[:3]) / 255.0
    b = S * 3
    edge = np.zeros((H, W), bool)
    edge[:b, :] = edge[-b:, :] = True
    edge[:, :b] = edge[:, -b:] = True
    img[edge] = np.array(EDGE) / 255.0
    return img.reshape(h, S, px, S, 3).mean(axis=(1, 3))


def save_png(img, path):
    import bpy
    h, w = img.shape[:2]
    im = bpy.data.images.new(os.path.basename(path), w, h, alpha=True)
    rgba = np.ones((h, w, 4), np.float32)
    rgba[..., :3] = img
    im.pixels.foreach_set(rgba[::-1].ravel())          # Blender rows run bottom to top
    im.filepath_raw = path
    im.file_format = "PNG"
    im.save()
    bpy.data.images.remove(im)


def write(work, values, prefix="decal_lcd_f", src=None):
    """Frames in work: <prefix>NN.png. Redraws only if a frame is missing or older than this file and src
    (the model generator where the readings are recorded) - the bake machine's Blender copies
    (kbake.Split) do not write the same file at once. Returns the file names."""
    os.makedirs(work, exist_ok=True)
    stamp = max(os.path.getmtime(f) for f in (os.path.abspath(__file__), src) if f)
    names = []
    for i, v in enumerate(values):
        fn = "%s%02d.png" % (prefix, i)
        path = os.path.join(work, fn)
        if not os.path.exists(path) or os.path.getmtime(path) < stamp:
            save_png(image(v), path)
            print("lcd frame:", path, v)
        names.append(fn)
    return names
