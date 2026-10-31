#!/usr/bin/env python3
"""Draw the ecolog header's tracked title and device label with the vanilla Metron glyphs.

The mockup tracks the terminal's title (.title: 20 px, letter-spacing .14em) and its device label
(.dev: 12 px, .14em). A TextWidget cannot track (letter spacing draws nothing, skill gui-layouts
§32) and a Metron space is twice that tracking, so the bake draws both as pictures -- the sprites
`title` and `dev` of sprites.json, keys STR_OZL_SKIN_ECOLOG_TITLE_IMG / _DEV_IMG. They are drawn
with the glyphs the game draws Metron with (the vanilla Metron48 atlas, the same face as every
live text of the window), scaled to the label's cell from ui/tokens/ecolog.json at the bake's
1.5 px per unit, white (the game tints them).

The device picture starts where the title starts and carries its text 18 units after the
title's tracked width IN THE SAME LANGUAGE (the mockup's .ehead gap): the pair needs no measuring
in the game.

    python source/ui/ecolog/metron_words.py [fonts folder, default P:/gui/fonts]

writes source/ui/ecolog/words/{title,dev}_{ua,en}.png and prints the sprite boxes for
sprites.json and the layout (ozl_tree_ecolog: EcoTitleImg, EcoDevImg).
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "source" / "fonts"))
from fontkit import edds, fnt  # noqa: E402

SCALE = 1.5          # the bake's px per unit (sprites.json "scale")
OVER = 4             # drawn this many times larger, then reduced: sub-pixel pen positions
GAP = 18             # .ehead gap between the title and the device label
WORDS = {            # sprite: (string key, token font, mockup px, mockup letter-spacing em)
    "title": ("STR_OZL_SKIN_ECOLOG_TITLE", "ecolog_title", 20, 0.14),
    "dev": ("STR_OZL_SKIN_ECOLOG_DEV", "ecolog_dev", 12, 0.14),
}
LANGS = {"ua": 1, "en": 2}   # stringtable columns


def upper(text: str) -> str:
    """Capitals as OZL_Text.Upper writes them: the vanilla Metron has no Cyrillic І (U+0406)."""
    return text.upper().replace("\u0406", "I")


def strings() -> dict[str, list[str]]:
    with open(REPO / "OpenZone_Research" / "stringtable.csv", encoding="utf-8-sig", newline="") as f:
        return {row[0]: row for row in csv.reader(f) if row}


def run(text: str, cell: float, track: float, face) -> tuple[list[tuple[object, float]], float, float]:
    """Glyphs with their pen positions (units), the advance sum with the tracking after EVERY
    letter (as CSS adds it, the last one included), and the ink's right edge."""
    font, glyphs, _ = face
    k = cell / font.line_height
    pen = 0.0
    out = []
    ink = 0.0
    for ch in text:
        g = glyphs.get(ord(ch))
        if g is None:
            raise SystemExit(f"Metron48 has no glyph for {ch!r} (U+{ord(ch):04X}) in {text!r}")
        out.append((g, pen))
        if g.w:
            ink = pen + (g.pre + g.w) * k
        pen += g.advance * k + track
    return out, pen, ink


def draw(placed, cell: float, face, width: float, height: float, offset: float = 0.0) -> Image.Image:
    font, _, atlas = face
    big = OVER * SCALE
    k = cell / font.line_height
    canvas = Image.new("L", (round(width * big), round(height * big)), 0)
    for g, pen in placed:
        if not g.w:
            continue
        a = atlas.crop((g.x, g.y, g.x + g.w, g.y + g.h)).getchannel("A")
        a = a.resize((max(1, round(g.w * k * big)), max(1, round(g.h * k * big))), Image.Resampling.LANCZOS)
        canvas.paste(a, (round((offset + pen + g.pre * k) * big), 0), a)
    alpha = canvas.resize((round(width * SCALE), round(height * SCALE)), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", alpha.size, (255, 255, 255, 0))
    out.putalpha(alpha)
    return out


def even_up(v: float) -> int:
    """A box in whole even units: x 1.5 is then whole pixels."""
    n = math.ceil(v)
    return n + (n % 2)


def main() -> None:
    fonts = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("P:/gui/fonts")
    font = fnt.read(str(fonts / "Metron48.fnt"))
    atlas = max(edds.to_rgba_images(edds.read(str(fonts / "Metron48.edds"))), key=lambda i: i.size[0])
    face = (font, font.by_cp(), atlas)
    tokens = json.loads((REPO / "ui" / "tokens" / "ecolog.json").read_text(encoding="utf-8"))["font"]
    rows = strings()

    runs = {}
    for name, (key, token, px, em) in WORDS.items():
        cell = float(tokens[token]["size"])
        for lang, col in LANGS.items():
            text = upper(rows[key][col])
            runs[name, lang] = (text, cell, *run(text, cell, px * em, face))

    out = HERE / "words"
    out.mkdir(exist_ok=True)
    title_w = even_up(max(runs["title", lang][4] for lang in LANGS) + 2)
    title_h = even_up(runs["title", "ua"][1])
    dev_w = even_up(max(runs["title", lang][3] + GAP + runs["dev", lang][4] for lang in LANGS) + 2)
    dev_h = even_up(runs["dev", "ua"][1])
    for lang in LANGS:
        _, cell, placed, _, _ = runs["title", lang]
        draw(placed, cell, face, title_w, title_h).save(out / f"title_{lang}.png")
        _, cell, placed, _, _ = runs["dev", lang]
        draw(placed, cell, face, dev_w, dev_h, runs["title", lang][3] + GAP).save(out / f"dev_{lang}.png")
        print(f"{lang}: title ink {runs['title', lang][4]:.2f}, advance {runs['title', lang][3]:.2f}; "
              f"device text at {runs['title', lang][3] + GAP:.2f}, ink to "
              f"{runs['title', lang][3] + GAP + runs['dev', lang][4]:.2f}")
    print(f"sprite title {title_w} x {title_h}, sprite dev {dev_w} x {dev_h} (units)")


if __name__ == "__main__":
    main()
