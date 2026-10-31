"""Render text with a decoded .fnt + atlas the way the engine lays it out (previews, tests).

  pen_x starts at 0; for each code point:
     g = glyph or fallback (U+25A1 if present, else skipped -- vanilla Metron has no box)
     pen_x += kern(prev, cp)
     pen_x += g.pre;  blit atlas[x:x+w, y:y+h] at (pen_x, line_top);  pen_x += g.w + g.post
"""
import os

from PIL import Image, ImageDraw

from . import edds, fnt


def load(fnt_path, atlas_path=None):
    f = fnt.read(fnt_path)
    if atlas_path is None:
        atlas_path = os.path.splitext(fnt_path)[0] + ".edds"
    if atlas_path.endswith(".edds"):
        atlas = edds.to_rgba_images(edds.read(atlas_path))[0]
    else:
        atlas = Image.open(atlas_path).convert("RGBA")
    return f, atlas


def render_line(f, atlas, text, color=(255, 255, 255), boxes=False):
    m = f.by_cp()
    kern = {(a, b): dx for a, b, dx in f.kern}
    lh = f.line_height
    fallback = m.get(0x25A1)
    seq = []
    pen = 0
    prev = None
    for ch in text:
        cp = ord(ch)
        g = m.get(cp, fallback)
        if g is None:
            seq.append((None, pen, cp))
            prev = None
            continue
        if prev is not None:
            pen += kern.get((prev, cp), 0)
        pen += g.pre
        seq.append((g, pen, cp))
        pen += g.w + g.post
        prev = cp
    width = max(1, pen + 2)
    img = Image.new("RGBA", (width, lh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    for g, x, cp in seq:
        if g is None:
            continue
        cell = atlas.crop((g.x, g.y, g.x + g.w, g.y + g.h))
        r, gg, b, a = cell.split()
        tinted = Image.merge("RGBA", (
            r.point(lambda v: v * color[0] // 255),
            gg.point(lambda v: v * color[1] // 255),
            b.point(lambda v: v * color[2] // 255), a))
        img.alpha_composite(tinted, (x, 0))
        if boxes:
            dr.rectangle((x, 0, x + max(g.w, 1) - 1, g.h - 1), outline=(255, 64, 64, 160))
    missing = [cp for g, _, cp in seq if g is None]
    return img, missing


def sheet(rows, scale=2, bg=(24, 26, 38, 255), pad=8):
    """rows: [(label, image)] -> one PNG-able image."""
    lab_h = 14
    w = max(r[1].width for r in rows) * scale + 2 * pad
    h = sum(r[1].height * scale + lab_h + pad for r in rows) + pad
    out = Image.new("RGBA", (max(w, 400), h), bg)
    dr = ImageDraw.Draw(out)
    y = pad
    for label, im in rows:
        dr.text((pad, y), label, fill=(150, 200, 255, 255))
        y += lab_h
        big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        out.alpha_composite(big, (pad, y))
        dr.line((pad, y + big.height, pad + big.width, y + big.height), fill=(70, 70, 90, 255))
        y += big.height + pad
    return out
