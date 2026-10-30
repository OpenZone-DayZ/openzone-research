"""Frames of the M72 oscilloscope screen in the "working" state (OZL_WorkFx frames).

Drawn inside Blender (numpy and bpy.data.images, no Pillow): the base is the same blanked screen
decal_screen.png that make_decals.py draws (the CRT filter, a 10 x 8 grid), with the beam on top. The
screen shows a digital signal from the board under the probe: a burst of pulses three divisions tall,
ringing on the edges, noise; the bits change from frame to frame (data runs), the first two bits are
a sync word that the trigger locks on, so the picture does not "drift". The edges are dimmer than the
flats - the beam moves quickly along them, as on a real tube; each frame carries a pale trace of the
previous one (afterglow), and for the first frame that is the last one: a seamless loop.

    make_frames(work, renders) -> work/decal_screen_fNN.png (+ renders/look_on_frames.png - all the
    frames on a sheet, for the preview)

build_m72.py calls it on every build (except --stats, --uv-hash and --bake-part copies): the frames
are not kept in git, they can always be redrawn from decal_screen.png; the same seed gives the same
frames.
"""
import math
import os

import bpy
import numpy as np

import m72_layout as L

N_FRAMES = 12
BASE = "decal_screen.png"
FRAME = "decal_screen_f%02d.png"
SEED = 72

# signal, screen metres (0 is the middle): over a 60 x 48 mm grid, a division is 6 mm
X0, X1 = -0.0318, 0.0312          # the sweep is slightly wider than the grid, as on a real tube
LOW, HIGH = -0.0090, 0.0090       # three divisions of swing
BITS = 22
RISE = 0.00016                    # edge duration
RING = (0.20, 0.00055, 0.00078)   # ringing after the edge: fraction of the swing, decay, wavelength
NOISE = 0.00011
GHOST = 0.22                      # afterglow of the previous frame
CORE = (0.66, 1.00, 0.74)         # phosphor: the middle of the beam is almost white
HALO = (0.10, 0.78, 0.36)


def _load(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    a = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(a)
    bpy.data.images.remove(img)
    return a.reshape(h, w, 4)            # rows run bottom to top: the row index grows with z


def _save(arr, path):
    h, w, _ = arr.shape
    img = bpy.data.images.new("m72_screen_tmp", width=w, height=h, alpha=True)
    img.pixels.foreach_set(np.ascontiguousarray(arr, dtype=np.float32).ravel())
    tmp = path + ".tmp.png"
    img.filepath_raw = tmp
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)
    os.replace(tmp, path)


def _bits(rng):
    b = list(rng.integers(0, 2, BITS))
    b[0], b[1] = 1, 0                    # sync word - the trigger locks on it
    return b


def _signal(xs, bits, rng):
    bw = (X1 - X0) / BITS
    y = np.full_like(xs, LOW if bits[0] == 0 else HIGH)
    amp, tau, lam = RING
    prev = bits[0]
    for i in range(1, BITS):
        if bits[i] == prev:
            continue
        xe = X0 + i * bw
        d = (HIGH - LOW) * (1 if bits[i] > prev else -1)
        t = (xs - xe) / RISE
        y += d * np.clip(0.5 + 0.5 * np.tanh(t * 2.2), 0.0, 1.0)
        after = np.clip(xs - xe - RISE, 0.0, None)
        y += np.where(xs > xe + RISE, d * amp * np.exp(-after / tau) * np.sin(2 * math.pi * after / lam), 0.0)
        prev = bits[i]
    n = rng.normal(0.0, 1.0, xs.size)
    k = np.ones(25) / 25.0
    y += np.convolve(n, k, mode="same") * NOISE * 4.0
    return y


def _splat(h, w, k, xs, ys):
    """A dense beam line into the buffer: points every 0.35 px of length, the weight is the fraction of
    travel along x (on the edges the beam is fast and dim)."""
    px = (xs + L.SCREEN_WH[0] / 2) * k - 0.5
    py = (ys + L.SCREEN_WH[1] / 2) * k - 0.5
    dx, dy = np.diff(px), np.diff(py)
    seg = np.hypot(dx, dy)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    ss = np.arange(0.0, s[-1], 0.35)
    qx, qy = np.interp(ss, s, px), np.interp(ss, s, py)
    wt = np.interp(ss, s[1:], np.clip(np.abs(dx) / np.maximum(seg, 1e-9), 0.18, 1.0))
    acc = np.zeros((h, w), dtype=np.float64)
    ix, iy = np.floor(qx).astype(int), np.floor(qy).astype(int)
    fx, fy = qx - ix, qy - iy
    for ox, oy, ww in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        jx, jy = ix + ox, iy + oy
        ok = (jx >= 0) & (jx < w) & (jy >= 0) & (jy < h)
        np.add.at(acc, (jy[ok], jx[ok]), (wt * ww)[ok])
    return acc


def _blur(a, sigma):
    r = int(math.ceil(sigma * 3))
    x = np.arange(-r, r + 1)
    g = np.exp(-0.5 * (x / sigma) ** 2)
    g /= g.sum()
    a = np.apply_along_axis(lambda v: np.convolve(v, g, mode="same"), 1, a)
    return np.apply_along_axis(lambda v: np.convolve(v, g, mode="same"), 0, a)


def make_frames(work, renders=None):
    base = _load(os.path.join(work, BASE))
    h, w, _ = base.shape
    k = w / L.SCREEN_WH[0]                         # pixels per metre
    rng = np.random.default_rng(SEED)
    xs = np.linspace(X0, X1, 9000)
    accs = []
    for f in range(N_FRAMES):
        accs.append(_splat(h, w, k, xs, _signal(xs, _bits(rng), rng)))
    dens = 1.0 / 0.35                              # points per pixel of length of a horizontal flat
    sc, sh = 1.5, 7.0
    names, frames = [], []
    for f in range(N_FRAMES):
        acc = accs[f] + GHOST * accs[f - 1]        # f - 1 for the first frame is the last one: a seamless loop
        core = np.clip(_blur(acc, sc) / (dens / (math.sqrt(2 * math.pi) * sc)), 0.0, 1.25) ** 0.8
        halo = np.clip(_blur(acc, sh) / (dens / (math.sqrt(2 * math.pi) * sh)), 0.0, 1.5)
        out = base.copy()
        out[..., :3] *= 1.08                       # a powered tube: the background is slightly lighter
        out[..., :3] += core[..., None] * np.array(CORE) + 0.35 * halo[..., None] * np.array(HALO)
        out[..., :3] = np.clip(out[..., :3], 0.0, 1.0)
        out[..., 3] = 1.0
        name = FRAME % f
        _save(out, os.path.join(work, name))
        names.append(name)
        frames.append(out)
    if renders:
        _sheet(frames, os.path.join(renders, "look_on_frames.png"))
    print("m72_screen: %d frames %dx%d" % (len(names), w, h))
    return names


def _sheet(frames, path, cols=4, gap=10):
    """All frames on a 4 x 3 sheet (halved), the first at the top left: shows how the signal runs."""
    small = [f[: f.shape[0] // 2 * 2, : f.shape[1] // 2 * 2].reshape(f.shape[0] // 2, 2, f.shape[1] // 2, 2, 4)
             .mean(axis=(1, 3)) for f in frames]
    fh, fw, _ = small[0].shape
    rows = (len(small) + cols - 1) // cols
    W, H = cols * fw + (cols + 1) * gap, rows * fh + (rows + 1) * gap
    sheet = np.zeros((H, W, 4), dtype=np.float32)
    sheet[..., :3] = 0.12
    sheet[..., 3] = 1.0
    for i, s in enumerate(small):
        r, c = divmod(i, cols)
        y0 = H - (r + 1) * (fh + gap)              # rows run bottom to top: the first row is at the top
        x0 = gap + c * (fw + gap)
        sheet[y0:y0 + fh, x0:x0 + fw] = s
    os.makedirs(os.path.dirname(path), exist_ok=True)
    _save(sheet, path)
