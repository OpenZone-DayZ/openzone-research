#!/usr/bin/env python3
"""TTF/OTF/TTC -> DayZ font: a `.fnt` and its `.edds` atlas -- bitmap (FNT3) by default,
distance field (FNT5) with --sdf.

    python source/fonts/fontbuild.py FONT.ttf --name ozl_hand --cells 24 32 --out DIR [options]

MultilineTextWidget and RichTextWidget draw every FNT3 font at its atlas's own pixel size,
whatever "exact text size" asks (the vanilla FNT3 fonts too; measured 2026-10-31); only
FNT5 fonts scale there. TextWidget scales both. See build_sdf() for the FNT5 output.

For every cell height N it writes DIR/<name><N>.fnt and DIR/<name><N>.edds. A layout uses

    font "<pbo prefix>/<dir>/<name><N>"     (no extension; the engine adds .fnt and finds
                                             the texture as the same path with .edds)
    "exact text" 1
    "exact text size" S                     S = the CELL HEIGHT in layout units

"exact text size" scales the whole glyph cell (measured on the stand 2026-10-31), so N only
decides how sharp the text is, never how big. Every glyph cell is the full line (mode
"fit"): N pixels from the top of the tallest accent to the bottom of the deepest descender
of the text characters -- letters, digits, punctuation -- with the baseline inside it; a
rarer sign that does not fit is left out. The em size is N divided by a ratio fixed per
face, so the glyphs grow exactly with N and one "exact text size" means one glyph size in
every cell height of a face.

The atlas is white with coverage in alpha (the widget colour tints it), A8R8G8B8, power of
two, a full mip chain, LZ4 blocks -- the shape of the vanilla and Workshop font atlases.
The output is deterministic: the same inputs give the same bytes.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True            # keep __pycache__ out of the source tree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fontkit import edds, fnt, kern, render, sfnt  # noqa: E402


def _r(a, b):
    return list(range(a, b + 1))


CHARSETS = {
    # printable ASCII
    "latin": _r(0x20, 0x7E),
    # Latin-1 punctuation and signs: NBSP ¡ ¢ £ ¤ ¥ ¦ § ¨ © ª « ¬ ® ¯ ° ± ² ³ ´ µ ¶ · ¸ ¹ º » ¼ ½ ¾ ¿, × ÷
    "latin1": [c for c in _r(0xA0, 0xBF) if c != 0xAD] + [0xD7, 0xF7],
    # Cyrillic letters: А..я, U+0401 U+0451, Є є, І і, Ї ї, Ґ ґ (every Ukrainian letter among them)
    "cyrillic": _r(0x410, 0x44F) + [0x401, 0x451, 0x404, 0x454, 0x406, 0x456, 0x407, 0x457, 0x490, 0x491],
    # the whole basic Cyrillic block (Serbian, Macedonian, Belarusian letters too)
    "cyrillic_full": _r(0x400, 0x45F) + [0x490, 0x491],
    # typography: – — ‘ ’ ‚ “ ” „ • … ‹ › № ₴ ′ ″ and the Ukrainian apostrophe ʼ
    "punct": [0x2013, 0x2014, 0x2018, 0x2019, 0x201A, 0x201C, 0x201D, 0x201E, 0x2022, 0x2026,
              0x2039, 0x203A, 0x2116, 0x20B4, 0x2032, 0x2033, 0x02BC],
    # the engine draws U+25A1 for a character the font lacks, when the font has it
    "box": [0x25A1],
}
DEFAULT_CHARSET = "latin+latin1+cyrillic+punct+box"

# The characters whose ink defines the cell in "fit" mode: printable ASCII, the Cyrillic
# letters and the punctuation of running text. Everything else in the set (Latin-1 signs,
# superscripts, the spacing cedilla, ₴, the box...) is kept only if it fits that cell --
# one deep cedilla would otherwise shrink every glyph of the face by 5 %.
EXTENT = set(_r(0x21, 0x7E)) | set(CHARSETS["cyrillic_full"]) | {
    0xAB, 0xBB, 0x2013, 0x2014, 0x2018, 0x2019, 0x201A, 0x201C, 0x201D, 0x201E, 0x2026, 0x2116}

# Signs some faces carry; added only when the face has them AND they fit the cell the
# character set above defines (they never make the cell taller).
SYMBOLS = [0x2190, 0x2191, 0x2192, 0x2193,          # ← ↑ → ↓
           0x25C6, 0x25C7, 0x25CF, 0x25CB,          # ◆ ◇ ● ○
           0x2605, 0x2606, 0x2713, 0x2714, 0x2715, 0x2717,   # ★ ☆ ✓ ✔ ✕ ✗
           0x262E, 0x2665, 0x221E]                  # ☮ ♥ ∞

# Stand-ins used only when the face lacks the first character: the record points at the
# second character's cell (FNT3 lets two code points share one cell).
ALIASES = {0x02BC: 0x2019,   # ʼ -> ’
           0x0406: 0x0049,   # І -> I
           0x0456: 0x0069,   # і -> i
           0x2032: 0x0027,   # ′ -> '
           0x2033: 0x0022}   # ″ -> "

# What the mod's text cannot do without: the English and Ukrainian alphabets, the digits,
# the Latin I the stringtables put for the Cyrillic one, the apostrophe and the punctuation
# of the UI. Whatever of this the requested character set holds must end up in the font, or
# the build stops (check_required). A stand-in counts only for І and і -- they look like the
# Latin I and i in most faces -- and is reported every time.
UKRAINIAN = "АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
REQUIRED = sorted({ord(c) for c in UKRAINIAN} | set(_r(0x30, 0x39)) | set(_r(0x41, 0x5A))
                  | set(_r(0x61, 0x7A)) | {0x2019, 0xAB, 0xBB, 0xB7, 0x2014, 0x2013, 0x201C,
                                           0x201D, 0x2116})
LOUD_STAND_INS = {0x0406, 0x0456}


def check_required(path, n, want, glyphs, stand_ins):
    """Stop on a required character the font lacks; return the warnings for allowed stand-ins."""
    final = {g.cp for g in glyphs}
    via = dict(stand_ins)
    required = [c for c in REQUIRED if c in set(want)]
    bad = [c for c in required if c not in final or (c in via and c not in LOUD_STAND_INS)]
    if bad:
        raise SystemExit("%s, cell %d: the font would lack required character(s): %s" % (
            os.path.basename(path), n, ", ".join("U+%04X %s" % (c, chr(c)) for c in bad)))
    return ["the face has no U+%04X %s: the font draws U+%04X %s for it" % (c, chr(c), via[c], chr(via[c]))
            for c in required if c in via]

SAMPLE = ("Обов’язок: Їжак, ґанок, єнот — «ІЇЄҐ іїєґ» № 7 · "
          "Quick brown fox 0123456789 AV To Wa")


def parse_charset(spec):
    cps = set()
    for part in spec.split("+"):
        part = part.strip()
        if part not in CHARSETS:
            raise SystemExit("unknown charset part %r (known: %s)" % (part, ", ".join(sorted(CHARSETS))))
        cps |= set(CHARSETS[part])
    return sorted(cps)


def open_font(path, size, face_index=0, wght=None):
    """A Pillow FreeType font; `wght` sets the weight axis of a variable font."""
    font = ImageFont.truetype(path, size=size, index=face_index, layout_engine=ImageFont.Layout.BASIC)
    if wght is not None:
        try:
            axes = font.get_variation_axes()
        except OSError:
            raise SystemExit("%s is not a variable font; drop the weight" % os.path.basename(path))
        values = []
        for ax in axes:
            name = ax.get("name", b"")
            name = name.decode("latin1") if isinstance(name, bytes) else str(name)
            values.append(float(wght) if name.lower() in ("weight", "wght") else ax["default"])
        font.set_variation_by_axes(values)
    return font


SS = 4          # glyphs are drawn 4x larger and box-filtered down: outline-true shapes and
                # metrics that scale linearly with the cell (hinting would make the glyph
                # size jump from one cell height to the next, and the engine scales the
                # cell anyway, so hinted pixels would not survive)
REF_PX = 512    # size at which the ink extent of the character set is measured


def ink_extent(path, cps, face_index=0, wght=None, size=REF_PX):
    """Highest ink above and deepest ink below the baseline, over `cps`, at `size` px."""
    font = open_font(path, size, face_index, wght)
    top = bot = 0.0
    for cp in cps:
        l, t, r, b = font.getbbox(chr(cp), anchor="ls")
        if r > l:
            top, bot = max(top, -t), max(bot, b)
    return top, bot


def cell_ratio(path, cps, face_index=0, wght=None):
    """Cell height / em size of a face in "fit" mode -- the same for every cell height."""
    top, bot = ink_extent(path, cps, face_index, wght)
    return (top + bot) / REF_PX


def choose_size(path, n, cps, mode, face_index, wght):
    """-> (FreeType em size in px, baseline offset from the cell top, cell height).

    `cps` are the characters whose ink must fit (the EXTENT part of the set)."""
    if mode == "line":      # ascent + descent = N (vanilla Metron); ink beyond is clipped
        best = n * 0.4
        s = n * 0.4
        while s <= n * 1.6:
            a, d = open_font(path, s, face_index, wght).getmetrics()
            if a + d <= n:
                best = s
            s = round(s + 0.05, 2)
        a, d = open_font(path, best, face_index, wght).getmetrics()
        return best, a, a + d
    top, bot = ink_extent(path, cps, face_index, wght)
    if mode == "em":        # FreeType em size N, the cell is as tall as the ink needs
        k = n / REF_PX
        base = int(-(-top * k // 1))
        return float(n), base, base + int(-(-bot * k // 1))
    # fit: the em size at which the ink of the set -- accents and descenders included --
    # is exactly N pixels tall, measured once at REF_PX, so the glyphs grow in proportion
    # to N. The baseline goes where the ink at the real size clips least.
    px = n * REF_PX / (top + bot)
    real_top, real_bot = ink_extent(path, cps, face_index, wght, px * SS)
    real_top, real_bot = real_top / SS, real_bot / SS
    best = None
    for base in sorted({int(real_top), int(real_top) + 1, int(round(top * px / REF_PX))}):
        cut = max(real_top - base, real_bot - (n - base), 0)
        if best is None or cut < best[0]:
            best = (cut, base)
    return px, best[1], n


def glyph_box(font_ss, cp):
    """Ink box (left, top, right, bottom) of a glyph at the 4x size, relative to pen/baseline."""
    return font_ss.getbbox(chr(cp), anchor="ls")


def next_pow2(v):
    p = 1
    while p < v:
        p *= 2
    return p


class Built:
    """One finished size: `font` (fnt.Font), `atlas` (RGBA image) and the numbers behind them."""


def build(path, name, n, charset=DEFAULT_CHARSET, wght=None, mode="fit", symbols=True,
          kerning=True, box=True, aliases=True, mips=True, pad=None, face_index=0):
    """Build one cell height `n` of a face. Returns a Built; nothing is written."""
    want = parse_charset(charset)
    covered = sfnt.coverage(path, face_index)
    have = [c for c in want if c in covered]
    stand_ins = []
    if aliases:
        for src, dst in ALIASES.items():
            if src in want and src not in covered and dst in covered:
                stand_ins.append((src, dst))
                if dst not in have:
                    have.append(dst)
    have.sort()
    missing = [c for c in want if c not in covered and c != 0x25A1 and c not in dict(stand_ins)]
    if any(c > 0xFFFF for c in have):
        raise SystemExit("FNT3 stores 16-bit code points; drop non-BMP characters")

    core = [c for c in have if c in EXTENT] or have
    px, top, cell = choose_size(path, n, core, mode, face_index, wght)
    bottom = cell - top
    font_ss = open_font(path, px * SS, face_index, wght)

    def overflow(box):
        l, t, r, b = box
        return 0.0 if r <= l else max(-t - top * SS, b - bottom * SS, 0) / SS

    # whether a sign outside the core fits is decided once, in em units at REF_PX, so
    # every cell height of a face carries the same characters
    font_ref = open_font(path, REF_PX, face_index, wght)
    ref_top, ref_bot = ink_extent(path, core, face_index, wght)

    def fits(cp):
        l, t, r, b = font_ref.getbbox(chr(cp), anchor="ls")
        return r <= l or (-t <= ref_top + 0.01 * REF_PX and b <= ref_bot + 0.01 * REF_PX)

    boxes, dropped = {}, []
    for cp in have:
        if cp in core or fits(cp):
            boxes[cp] = glyph_box(font_ss, cp)
        elif cp != 0x25A1:
            dropped.append(cp)          # too tall or too deep for the cell: left out
    extra = []
    if symbols:
        for cp in SYMBOLS:
            if cp in covered and cp not in boxes and fits(cp):
                b4 = glyph_box(font_ss, cp)
                if b4[2] > b4[0]:
                    boxes[cp] = b4
                    extra.append(cp)
    # ink the cell cuts off, in pixels: a fringe under half a pixel in "fit" mode
    clipped = {cp: round(overflow(b4), 2) for cp, b4 in boxes.items() if overflow(b4) > 0.5}

    pad = (4 if mips else 1) if pad is None else pad
    glyphs, images = [], {}
    for cp in sorted(boxes):
        l, t, r, b = boxes[cp]
        advance = int(round(font_ss.getlength(chr(cp)) / SS))
        if r > l:
            pre = l // SS                       # floor
            w = max(1, -(-r // SS) - pre)        # ceil(r / SS) - pre
            big = Image.new("L", (w * SS, cell * SS), 0)
            ImageDraw.Draw(big).text((-pre * SS, top * SS), chr(cp), font=font_ss, fill=255, anchor="ls")
            img = big.resize((w, cell), Image.BOX)
        else:               # a blank glyph is a 1-pixel empty column, as in vanilla fonts
            w, pre = 1, 0
            img = Image.new("L", (1, cell), 0)
        glyphs.append(fnt.Glyph(cp, 0, 0, w, cell, pre, advance - pre - w))
        images[cp] = img

    if box and 0x25A1 not in boxes:
        cap = -boxes[ord("H")][1] / SS if ord("H") in boxes else top * 0.7
        bh = max(4, min(int(round(cap)), top))
        bw = max(4, int(round(bh * 0.7)))
        stroke = max(1, n // 18)
        img = Image.new("L", (bw, cell), 0)
        ImageDraw.Draw(img).rectangle((0, top - bh, bw - 1, top - 1), outline=255, width=stroke)
        side = max(1, n // 16)
        glyphs.append(fnt.Glyph(0x25A1, 0, 0, bw, cell, side, side))
        images[0x25A1] = img
        glyphs.sort(key=lambda g: g.cp)

    # shelf packing in code-point order, padding all round, smallest power-of-two area
    best = None
    for width in (64, 128, 256, 512, 1024, 2048, 4096):
        x, y, place, fits = pad, pad, {}, True
        for g in glyphs:
            if g.w + 2 * pad > width:
                fits = False
                break
            if x + g.w + pad > width:
                x, y = pad, y + cell + pad
            place[g.cp] = (x, y)
            x += g.w + pad
        height = next_pow2(y + cell + pad)
        if not fits or height > 4096:
            continue
        key = (width * height, max(width, height) / min(width, height), width)
        if best is None or key < best[0]:
            best = (key, width, height, place)
    if best is None:
        raise SystemExit("%s%d: the glyphs do not fit a 4096 atlas" % (name, n))
    _, width, height, place = best
    alpha = Image.new("L", (width, height), 0)
    for g in glyphs:
        g.x, g.y = place[g.cp]
        alpha.paste(images[g.cp], (g.x, g.y))
    white = Image.new("L", (width, height), 255)
    atlas = Image.merge("RGBA", (white, white, white, alpha))

    by_cp = {g.cp: g for g in glyphs}
    for src, dst in stand_ins:
        d = by_cp[dst]
        glyphs.append(fnt.Glyph(src, d.x, d.y, d.w, d.h, d.pre, d.post))
    glyphs.sort(key=lambda g: g.cp)
    warnings = check_required(path, n, want, glyphs, stand_ins)

    pairs = []
    if kerning:
        units, upem = kern.kerning(path, [g.cp for g in glyphs if g.cp in boxes], face_index)
        for (a, b), v in sorted(units.items()):
            dx = int(round(v * px / upem))
            if dx:
                pairs.append((a, b, dx))
        for src, dst in stand_ins:
            pairs += [(src, b, dx) for a, b, dx in list(pairs) if a == dst]
            pairs += [(a, src, dx) for a, b, dx in list(pairs) if b == dst]
        pairs = sorted(set(pairs))

    f = fnt.Font()
    f.kind = "FNT3"
    f.name = "%s%d" % (name, n)
    f.size = cell
    f.glyphs = glyphs
    f.kern = pairs
    f.chunk_order = ["GLPS", "TCRD", "KERN", "HEAD"]      # the order the stand probe drew

    out = Built()
    out.name, out.n, out.font, out.atlas, out.mips = "%s%d" % (name, n), n, f, atlas, mips
    out.freetype_px, out.cell, out.baseline = px, cell, top
    out.missing, out.stand_ins, out.symbols, out.clipped = missing, stand_ins, extra, clipped
    out.dropped, out.warnings = dropped, warnings
    return out


SDF_PAD = 8     # atlas px of field around each glyph's ink box (the u16 of the vanilla HEAD)
SDF_K = 4       # the outline is measured on a mask drawn this many times larger


def build_sdf(path, name, n, charset=DEFAULT_CHARSET, wght=None, symbols=True, box=True,
              aliases=True, face_index=0):
    """Build an FNT5 (SDF) font whose line is `n` atlas pixels -- the same cell and the same
    glyph size per "exact text size" as the FNT3 font of that cell, but drawn from a
    distance field: it scales in every widget, MultilineTextWidget and RichTextWidget
    included (they draw FNT3 fonts at their native size whatever the size asked).

    HEAD size = n, so "exact text size" S scales the font by S / n: the line pitch is S and
    the em S / r, as with the FNT3 cells -- the same glyphs as the FNT3 font of the face at
    the same S (measured: equal ink widths). One line measures S x cell / n high, cell being
    the HEAD's u32 (GetTextSize, "size to text v"); several lines (lines - 1) x S + that.
    No kerning: no vanilla SDF font carries pairs and the FNT5 KERN record layout is unknown."""
    import numpy as np
    from fontkit import sdf

    want = parse_charset(charset)
    covered = sfnt.coverage(path, face_index)
    have = [c for c in want if c in covered]
    stand_ins = []
    if aliases:
        for src, dst in ALIASES.items():
            if src in want and src not in covered and dst in covered:
                stand_ins.append((src, dst))
                if dst not in have:
                    have.append(dst)
    have.sort()
    missing = [c for c in want if c not in covered and c != 0x25A1 and c not in dict(stand_ins)]
    core = [c for c in have if c in EXTENT] or have
    px, top, cell = choose_size(path, n, core, "fit", face_index, wght)
    font_ref = open_font(path, REF_PX, face_index, wght)
    ref_top, ref_bot = ink_extent(path, core, face_index, wght)

    def fits(cp):
        l, t, r, b = font_ref.getbbox(chr(cp), anchor="ls")
        return r <= l or (-t <= ref_top + 0.01 * REF_PX and b <= ref_bot + 0.01 * REF_PX)

    chosen, dropped = [], []
    for cp in have:
        if cp in core or fits(cp):
            chosen.append(cp)
        elif cp != 0x25A1:
            dropped.append(cp)
    extra = [cp for cp in SYMBOLS if symbols and cp in covered and cp not in chosen and fits(cp)]
    chosen = sorted(chosen + extra)

    # The vanilla layout (sdf_MetronBook24, measured): every glyph sits in a square cell of
    # the HEAD's u32 size (36 there), its ink box centred in it; the cells stand in slots one
    # pixel apart (pitch u32 + 2, the first at 1,1); TCRD x, y is the cell's corner. The
    # engine samples the whole cell around the ink, so the ink MUST be centred.
    k, pad = SDF_K, SDF_PAD
    font_hi = open_font(path, px * k, face_index, wght)
    metrics = {}                                 # cp -> (bx, by, w, h, adv) in atlas px
    for cp in chosen:
        l, t, r, b = font_hi.getbbox(chr(cp), anchor="ls")
        adv = int(round(font_hi.getlength(chr(cp)) / k))
        if r <= l:                               # blank: no ink, like the vanilla space
            metrics[cp] = (0, 0, 0, 0, adv)
            continue
        bx, by = l // k, -(t // k)               # floor of the left edge; ceil of the top
        metrics[cp] = (bx, by, max(1, -(-r // k) - bx), max(1, -(-b // k) + by), adv)
    drawn_box = box and 0x25A1 not in metrics
    if drawn_box:
        cap = metrics[ord("H")][1] if ord("H") in metrics else int(top * 0.7)
        bh = max(4, cap)
        bw = max(4, int(round(bh * 0.7)))
        side = max(1, n // 16)
        metrics[0x25A1] = (side, bh, bw, bh, bw + 2 * side)
    size = max(max(m[2], m[3]) for m in metrics.values()) + 2 * pad
    size += size % 2                             # even: (size - w) / 2 lands on a k grid
    pitch = size + 2

    def field_of(cp):
        bx, by, w, h, _ = metrics[cp]
        big = Image.new("L", (size * k, size * k), 0)
        ox, oy = (size - w) * k // 2, (size - h) * k // 2      # ink box corner, hi-res px
        if cp == 0x25A1 and drawn_box:
            stroke = max(1, n // 18) * k
            ImageDraw.Draw(big).rectangle((ox, oy, ox + w * k - 1, oy + h * k - 1), outline=255, width=stroke)
        else:
            ImageDraw.Draw(big).text((ox - bx * k, oy + by * k), chr(cp), font=font_hi, fill=255, anchor="ls")
        return sdf.signed_distance(np.asarray(big) >= 128, k, size, size)

    inked = [cp for cp in sorted(metrics) if metrics[cp][2]]
    slots = len(inked) + 1                       # slot 0 stays empty: the blank glyphs point there
    best = None
    for width in (256, 512, 1024, 2048, 4096):
        cols = (width - 1) // pitch
        if cols < 1:
            continue
        height = next_pow2(1 + -(-slots // cols) * pitch)
        if height > 4096:
            continue
        key = (width * height, max(width, height) / min(width, height), width)
        if best is None or key < best[0]:
            best = (key, width, height, cols)
    if best is None:
        raise SystemExit("%s%d: the SDF glyphs do not fit a 4096 atlas" % (name, n))
    _, width, height, cols = best
    field = np.zeros((height, width), dtype=np.uint8)
    glyphs = []
    for cp in sorted(metrics):
        bx, by, w, h, adv = metrics[cp]
        g = fnt.Glyph(cp, 1, 1, w, h, bx, adv - bx - w, top=by, adv=adv)
        if w:
            i = inked.index(cp) + 1
            g.x, g.y = 1 + (i % cols) * pitch, 1 + (i // cols) * pitch
            field[g.y:g.y + size, g.x:g.x + size] = field_of(cp)
        glyphs.append(g)
    rgb = Image.fromarray(field, "L")
    atlas = Image.merge("RGBA", (rgb, rgb, rgb, Image.new("L", (width, height), 255)))

    by_cp = {g.cp: g for g in glyphs}
    for src, dst in stand_ins:
        d = by_cp[dst]
        glyphs.append(fnt.Glyph(src, d.x, d.y, d.w, d.h, d.pre, d.post, top=d.top, adv=d.adv))
    glyphs.sort(key=lambda g: g.cp)
    warnings = check_required(path, n, want, glyphs, stand_ins)

    f = fnt.Font()
    f.kind = "FNT5"
    f.name = "%s%d" % (name, n)
    f.size = cell
    f.head_tail = fnt.head_fnt5(size, float(top), float(cell), pad)
    f.glyphs = glyphs
    f.kern = []
    f.chunk_order = ["HEAD", "GLPS", "TCRD", "KERN"]      # the vanilla SDF order

    out = Built()
    out.name, out.n, out.font, out.atlas, out.mips = "%s%d" % (name, n), n, f, atlas, True
    out.freetype_px, out.cell, out.baseline = px, cell, top
    out.missing, out.stand_ins, out.symbols, out.clipped = missing, stand_ins, extra, {}
    out.dropped, out.warnings = dropped, warnings
    return out


def write(built, out_dir, codec="lz4"):
    """Write <name><N>.fnt and .edds into out_dir; returns their paths."""
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.join(out_dir, built.name)
    fnt.write(built.font, stem + ".fnt")
    edds.write(stem + ".edds", built.atlas, mipmaps=built.mips,
               lz4_min=(1 << 62) if codec == "copy" else 512)
    return stem + ".fnt", stem + ".edds"


def preview(built, fnt_path, out_dir, text=SAMPLE):
    """Atlas on a dark ground and the sample line read back from the written files."""
    os.makedirs(out_dir, exist_ok=True)
    bg = Image.new("RGBA", built.atlas.size, (24, 26, 38, 255))
    bg.alpha_composite(built.atlas)
    bg.convert("RGB").save(os.path.join(out_dir, built.name + "_atlas.png"))
    f, atlas = render.load(fnt_path)
    line, miss = render.render_line(f, atlas, text)
    label = "%s: cell %d px, FreeType %.2f px, %d glyphs, %d kern pairs, missing: %s" % (
        built.name, built.cell, built.freetype_px, len(f.glyphs), len(f.kern),
        "".join(chr(c) for c in miss) or "-")
    render.sheet([(label, line)], scale=1).convert("RGB").save(os.path.join(out_dir, built.name + "_sample.png"))


def describe(built):
    parts = ["%s: cell %d px = FreeType %.2f px (cell/em %.3f), %d glyphs, %d kern pairs, atlas %dx%d" % (
        built.name, built.cell, built.freetype_px, built.cell / built.freetype_px, len(built.font.glyphs),
        len(built.font.kern), built.atlas.size[0], built.atlas.size[1])]
    if built.missing:
        parts.append("lacks " + "".join(chr(c) for c in built.missing))
    if built.dropped:
        parts.append("left out, taller than the cell: " + "".join(chr(c) for c in built.dropped))
    if built.stand_ins:
        parts.append("stand-ins " + " ".join("%s->%s" % (chr(a), chr(b)) for a, b in built.stand_ins))
    if built.clipped:
        parts.append("clipped " + " ".join("%s %.1fpx" % (chr(c), v) for c, v in sorted(built.clipped.items())))
    return ", ".join(parts)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("face", help="TTF/OTF/TTC file")
    ap.add_argument("--name", required=True, help="output stem: ozl_hand -> ozl_hand32.fnt")
    ap.add_argument("--cells", type=int, nargs="+", required=True, help="cell heights in pixels")
    ap.add_argument("--out", required=True, help="output folder")
    ap.add_argument("--wght", type=float, default=None, help="weight of a variable font, e.g. 600")
    ap.add_argument("--mode", choices=("fit", "em", "line"), default="fit",
                    help="fit: all ink inside an N-pixel cell (default); em: FreeType size N, "
                         "cell as tall as the ink; line: ascent+descent = N, ink beyond clipped")
    ap.add_argument("--charset", default=DEFAULT_CHARSET,
                    help="+-joined parts of: %s" % ", ".join(sorted(CHARSETS)))
    ap.add_argument("--no-symbols", dest="symbols", action="store_false", help="leave out the optional signs")
    ap.add_argument("--codec", choices=("lz4", "copy"), default="lz4", help="edds block codec")
    ap.add_argument("--no-mips", dest="mips", action="store_false", help="one level, no mip chain")
    ap.add_argument("--pad", type=int, default=None, help="atlas padding (default 4 with mips, 1 without)")
    ap.add_argument("--no-kern", dest="kerning", action="store_false")
    ap.add_argument("--no-box", dest="box", action="store_false", help="do not draw U+25A1 when the face lacks it")
    ap.add_argument("--no-alias", dest="aliases", action="store_false", help="no stand-ins for lacking characters")
    ap.add_argument("--face-index", type=int, default=0, help="face of a TTC collection")
    ap.add_argument("--sdf", action="store_true",
                    help="FNT5 distance field (for MultilineTextWidget, RichTextWidget); needs numpy; "
                         "--mode, --no-mips, --pad and --no-kern do not apply (no kerning in FNT5)")
    ap.add_argument("--preview", default="", help="also write atlas and sample PNGs here")
    args = ap.parse_args(argv)
    for n in args.cells:
        if args.sdf:
            b = build_sdf(args.face, args.name, n, args.charset, args.wght, args.symbols,
                          args.box, args.aliases, args.face_index)
        else:
            b = build(args.face, args.name, n, args.charset, args.wght, args.mode, args.symbols,
                      args.kerning, args.box, args.aliases, args.mips, args.pad, args.face_index)
        fnt_path, _ = write(b, args.out, args.codec)
        if args.preview:
            preview(b, fnt_path, args.preview)
        print(describe(b))
        for w in b.warnings:
            print("WARNING %s: %s" % (b.name, w), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
