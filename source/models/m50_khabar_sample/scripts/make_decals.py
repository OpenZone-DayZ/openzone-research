"""Decals of the Khabar sample (system Python + Pillow): a mark scratched with a knife through the paint
of the lid - a circle with a diagonal cross, like the anomaly mark on the stalker map. No letters or
digits.

    python make_decals.py      -> ../work/decal_mark.png

The size matches build_m50.py (MARK_D).
"""
import math
import os
import random

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.normpath(os.path.join(HERE, "..", "work"))
S = 4                                   # supersampling, then downscaling: clean edges
WHITE = (255, 255, 255, 255)


def save(img, size, name):
    img = img.resize(size, Image.LANCZOS)
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, name)
    img.save(path)
    print("wrote", path)


def stroke(d, pts, w, rnd, passes=2):
    """Knife scratch: several passes slightly off each other, the width varies, the ends taper off."""
    for p in range(passes):
        # a pass is the same path, shifted as a whole and rotated a little: the hand leads the knife
        # again
        dx, dy = rnd.uniform(-1.0, 1.0) * w, rnd.uniform(-1.0, 1.0) * w
        ph, amp = rnd.uniform(0, 6.3), w * 0.5
        n = len(pts)
        off = [(x + dx + amp * math.sin(ph + i * 0.9), y + dy + amp * math.cos(ph + i * 0.7)) for i, (x, y) in enumerate(pts)]
        for i in range(n - 1):
            k = min(i, n - 2 - i) / max(1, (n - 1) / 2)          # 0 at the ends, 1 in the middle
            ww = max(1, int(w * (0.35 + 0.65 * min(1.0, k * 3.0)) * (1.0 if p == 0 else 0.6)))
            d.line([off[i], off[i + 1]], fill=WHITE, width=ww, joint="curve")


def make_mark(px=256, seed=50):
    """Mark: an uneven circle (started and not closed, the end runs past the start) and a diagonal cross
    over it, the cross ends go beyond the circle. White on transparent - the generator takes the alpha
    as the mask of a scratch down to the tin.
    """
    rnd = random.Random(seed)
    n = px * S
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c, r, w = n / 2, n * 0.33, n * 0.016
    a0 = math.radians(rnd.uniform(60, 80))
    circ = []
    for i in range(41):
        a = a0 + 2 * math.pi * 1.08 * i / 40
        rr = r * (1 + 0.06 * math.sin(3 * a + 0.7) + rnd.uniform(-0.015, 0.015))
        circ.append((c + rr * math.cos(a), c + rr * math.sin(a)))
    stroke(d, circ, w, rnd, passes=2)
    for (x0, y0), (x1, y1) in (((0.20, 0.17), (0.81, 0.84)), ((0.83, 0.19), (0.18, 0.80))):
        pts = [((x0 + (x1 - x0) * t) * n, (y0 + (y1 - y0) * t) * n) for t in [i / 8 for i in range(9)]]
        stroke(d, pts, w * 1.2, rnd, passes=3)
    save(img, (px, px), "decal_mark.png")


if __name__ == "__main__":
    make_mark()
