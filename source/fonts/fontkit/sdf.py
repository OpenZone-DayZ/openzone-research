"""Signed distance fields for FNT5 (SDF) font atlases.

The vanilla SDF atlases (gui/fonts/sdf_*.edds) keep the field in R, G and B -- a
multi-channel field whose median is the distance -- with A = 255, the edge at 128,
inside brighter, about 21 levels per atlas pixel: +-6 px of distance between 0 and 255.
A single-channel field written to all three channels has that same median, so it draws
through the same shader (corners come out slightly rounder than a true MSDF's).

signed_distance() measures, for every pixel centre of an atlas cell, the distance to the
glyph outline taken from a mask drawn `k` times larger: exact to about 1/(2k) px.
"""
import numpy as np

RANGE = 6.0                 # atlas pixels of distance from the edge to 0 or 255
SLOPE = 127.0 / RANGE       # levels per pixel, like the vanilla atlases


def boundary_points(mask):
    """Centres (y, x) of the pixels where the mask changes, in hi-res pixel units: the
    point between two neighbouring pixels of different value."""
    pts = []
    h_edges = mask[:, 1:] != mask[:, :-1]
    ys, xs = np.nonzero(h_edges)
    pts.append(np.stack([ys + 0.5, xs + 1.0], axis=1))
    v_edges = mask[1:, :] != mask[:-1, :]
    ys, xs = np.nonzero(v_edges)
    pts.append(np.stack([ys + 1.0, xs + 0.5], axis=1))
    return np.concatenate(pts, axis=0) if pts else np.zeros((0, 2))


def signed_distance(mask, k, cell_w, cell_h, chunk=512):
    """mask: bool array (cell_h*k, cell_w*k), True inside the glyph.
    Returns uint8 (cell_h, cell_w): 128 + SLOPE * distance in atlas px, inside positive."""
    pts = boundary_points(mask)
    ys = (np.arange(cell_h) + 0.5) * k
    xs = (np.arange(cell_w) + 0.5) * k
    gy, gx = np.meshgrid(ys, xs, indexing="ij")
    samples = np.stack([gy.ravel(), gx.ravel()], axis=1)
    if len(pts) == 0:
        dist = np.full(len(samples), RANGE * k * 2.0)
    else:
        dist = np.empty(len(samples))
        p2 = (pts ** 2).sum(axis=1)[None, :]
        for s in range(0, len(samples), chunk):
            block = samples[s:s + chunk]
            d2 = (block ** 2).sum(axis=1)[:, None] + p2 - 2.0 * block @ pts.T
            dist[s:s + chunk] = np.sqrt(np.maximum(d2.min(axis=1), 0.0))
    inside = mask[np.minimum((gy.ravel()).astype(int), mask.shape[0] - 1),
                  np.minimum((gx.ravel()).astype(int), mask.shape[1] - 1)]
    signed = np.where(inside, dist, -dist) / k
    value = np.clip(np.round(128.0 + signed * SLOPE), 0, 255).astype(np.uint8)
    return value.reshape(cell_h, cell_w)
