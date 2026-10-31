#!/usr/bin/env python3
"""Write sprites.json of the freedom window («ВОЛЯ.narod») -- the bake manifest.

    python source/ui/freedom/sprites.py      # then: python source/ui/bake.py freedom

The manifest is generated because most of it repeats: sixteen frames of the spinning peace
sign, the pieces of the two 5-unit ridge frames and of the 3-unit Windows 98 bevel, a face
per node status and its hovered twin. Every picture is the mockup's own markup and CSS
(freedom.css holds the lifted rules), so Chrome draws here exactly what it draws in the
mockup. Sizes are layout units (the 1600x900 window), drawn at 1.5 px per unit; every size
is a whole number of pixels at that scale (even units), and where a piece needs an odd
size the extra unit lies on its transparent inner side. Pictures drawn white are tinted in
the layout; the rest carry their own colours and are shown with color 1 1 1 1.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------- the mockup's symbols

PEACE_INNER = ("<circle cx='50' cy='50' r='42' fill='none' stroke='currentColor' stroke-width='9'/>"
               "<path d='M50 8v84M50 50 21 79M50 50l29 29' stroke='currentColor' stroke-width='9' fill='none'/>")

LEAF_PARTS = [(-78, .42), (-52, .62), (-26, .86), (0, 1), (26, .86), (52, .62), (78, .42)]


def leaf_inner(color: str) -> str:
    """leafSvg() of the mockup without the <svg> wrapper: seven leaflets and the stem."""
    parts = "".join(
        f"<path transform='rotate({a} 50 84) translate(50 84) scale(1 {k}) translate(-50 -84)' "
        "d='M50 84C43 70 42 40 50 6 58 40 57 70 50 84Z'/>" for a, k in LEAF_PARTS)
    return f"<g fill='{color}'>{parts}</g><path d='M50 84v14' stroke='{color}' stroke-width='3'/>"


def sized_svg(inner: str, w: float, h: float) -> str:
    """A symbol as a block-level picture of w x h units (the mockup's .sym is 66 x 66)."""
    return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' width='{w}' height='{h}' "
            f"style='display:block'>{inner}</svg>")


def helper_svg(eye_scale: float) -> str:
    """HELPER of the mockup: the leaf with eyes; the pupils (.eye) squashed to eye_scale (blink)."""
    eye = "" if eye_scale == 1 else f" style='transform: scaleY({eye_scale})'"
    return ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>" + leaf_inner("#3fd12a")
            + "<path d='M50 84C47 74 46 62 50 46 54 62 53 74 50 84Z' fill='#7cf05a' opacity='.5'/>"
            "<g transform='translate(0 6)'>"
            "<ellipse cx='40' cy='44' rx='9' ry='11' fill='#fff' stroke='#000' stroke-width='2'/>"
            "<ellipse cx='62' cy='44' rx='9' ry='11' fill='#fff' stroke='#000' stroke-width='2'/>"
            f"<g class='eye'{eye}><circle cx='43' cy='47' r='4.5'/><circle cx='65' cy='47' r='4.5'/></g>"
            "<path d='M30 29q9-6 17 0M54 29q9-6 17 0' fill='none' stroke='#000' stroke-width='2.5' stroke-linecap='round'/>"
            "<path d='M40 64q11 10 22 0' fill='none' stroke='#000' stroke-width='2.5' stroke-linecap='round'/>"
            "</g></svg>")


def ftile() -> str:
    """FTILE of the mockup: the 140-unit tile (peace sign, leaf, two dots) as a CSS url().
    The nested <svg> elements carry no size, exactly as in the mockup: each fills the whole
    140-unit tile before the group's scale, so the symbols are 58.8 and 70 units across."""
    t = ("<svg xmlns='http://www.w3.org/2000/svg' width='140' height='140'>"
         "<g transform='translate(8 8) scale(.42)' opacity='.55' style='color:#4fae2a'>"
         f"<svg viewBox='0 0 100 100'>{PEACE_INNER}</svg></g>"
         "<g transform='translate(76 70) scale(.5) rotate(18 50 50)' opacity='.6'>"
         f"<svg viewBox='0 0 100 100'>{leaf_inner('#3f9a20')}</svg></g>"
         "<circle cx='110' cy='24' r='2' fill='#ff66ff' opacity='.5'/>"
         "<circle cx='34' cy='118' r='2' fill='#ffff66' opacity='.45'/></svg>")
    return 'url("data:image/svg+xml,' + quote(t, safe="") + '")'


# ---------------------------------------------------------------- helpers

def dark_fade(color: str, solid_until: int, reverse: bool = False) -> str:
    """Gradient stops of a DARK layer fading from opaque to clear, corrected for the game's
    linear-light blending: where the mockup's straight fade has alpha a, the stop has
    1 - (1 - a)^2.2, so the layer darkens what lies under it as much as Chrome's does
    (skill gui-layouts section 32). `solid_until` (percent) stays opaque, then nine stops to clear;
    `reverse` lists them from clear to opaque (a gradient drawn bottom up)."""
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    stops = []
    for k in range(9):
        t = k / 8                      # 0 = opaque end of the fade, 1 = clear end
        a = 1 - (t ** 2.2)             # corrected alpha of the straight fade's 1 - t
        pos = solid_until + (100 - solid_until) * t
        stops.append((pos, a))
    if reverse:
        stops = [(100 - pos, a) for pos, a in reversed(stops)]
    return ",".join(f"rgba({r},{g},{b},{a:.3f}) {pos:.1f}%" for pos, a in stops)


def box(style: str, inner: str = "") -> str:
    return f"<div style='position:absolute;{style}'>{inner}</div>"


def sprite(name: str, w: float, h: float, html: str, pad: float = 0) -> dict:
    s = {"name": name, "w": w, "h": h, "html": html}
    if pad:
        s["pad"] = pad
    return s


def pieces(prefix: str, border: str, side: int, cell: int) -> list[dict]:
    """The corners and edges of a bordered box, each cut out of the same CSS box by its clip.

    `side` = the border width; every piece is `cell` units across the border (cell > side
    when side is odd, so the piece is a whole number of pixels: the extra unit is the box's
    transparent inside). Corners are cell x cell; edges are 4 units along, stretched in the
    layout. The box is 40 units square, so its far border sits at 40 - cell."""
    big = 40
    far = cell - big            # offset that puts the box's far edge on the piece's far edge
    mid = -(big // 2 - 2)       # 4-unit window in the middle of an edge
    css = f"width:{big}px;height:{big}px;border:{border}"
    out = []
    for name, x, y, w, h in (
            ("tl", 0, 0, cell, cell), ("tr", far, 0, cell, cell),
            ("bl", 0, far, cell, cell), ("br", far, far, cell, cell),
            ("t", mid, 0, 4, cell), ("b", mid, far, 4, cell),
            ("l", 0, mid, cell, 4), ("r", far, mid, cell, 4)):
        out.append(sprite(f"{prefix}_{name}", w, h, box(f"left:{x}px;top:{y}px;{css}")))
    return out


# ---------------------------------------------------------------- the manifest

def build() -> dict:
    sprites: list[dict] = []

    # Node: a Windows 98 button 180x64, one face per status, and the hovered face
    # (.node:hover .cell { filter: brightness(1.08) }).
    for st in ("locked", "short", "available", "researching", "completed"):
        sprites.append(sprite(f"face_{st}", 180, 64, f"<div class='w98 {st}'></div>"))
        sprites.append(sprite(f"face_{st}_hover", 180, 64, f"<div class='w98 {st} hover'></div>"))
    # The selected node: a dotted outline 5 units out (.node.sel .cell), white, tinted yellow.
    sprites.append(sprite("sel_ring", 180, 64, box("inset:0;outline:2px dotted #fff;outline-offset:5px"), pad=8))
    # Marks above the node's right corner, as the mockup draws them: ✔ with a black shadow,
    # the padlock and the hourglass as the colour emoji Chrome shows.
    mark = "font:bold 15px Verdana,Tahoma,sans-serif;white-space:nowrap;line-height:20px;left:0;top:0"
    sprites.append(sprite("mark_check", 22, 20, box(mark + ";color:#33ff66;text-shadow:1px 1px 0 #000", "✔"), pad=2))
    sprites.append(sprite("mark_lock", 22, 20, box(mark + ";color:#c0c0c0", "\U0001F512"), pad=2))
    sprites.append(sprite("mark_wait", 22, 20, box(mark + ";color:#000080", "⏳"), pad=2))
    # Navy dashes of the progress bars, revealed by a clipping frame as the bar fills.
    sprites.append(sprite("dash_node", 168, 6, box("left:0;top:0;width:168px;height:5px;"
                          "background:repeating-linear-gradient(90deg,#000080 0 6px,transparent 6px 8px)")))
    sprites.append(sprite("dash_cost", 358, 8, box("inset:0;background:repeating-linear-gradient(90deg,#000080 0 8px,transparent 8px 10px)")))

    # info.exe: the research button up and pressed, the title bar with its three buttons
    # (the title is live text), the 3-unit bevel of the window, the inset bars of the card.
    sprites.append(sprite("btn_up", 382, 56, "<div class='w98'></div>"))
    sprites.append(sprite("btn_down", 382, 56, "<div class='w98 down'></div>"))
    sprites.append(sprite("title_bar", 418, 28, "<div class='ftitle'><span><i>_</i><i>□</i><i>×</i></span></div>"))
    sprites += pieces("win", "3px solid;border-color:#fff #404040 #404040 #fff", 3, 4)
    sprites.append(sprite("cost_bar", 362, 12, "<div class='inset2'></div>"))
    sprites.append(sprite("seg_bar", 382, 16, "<div class='inset2'></div>"))

    # The two framed boxes (menu, tree): 5-unit ridge #66cc33.
    sprites += pieces("ridge", "5px ridge #66cc33", 5, 6)
    # The menu box: title bars, the hazard sign, the line chip, the 'you are here' arrow.
    sprites.append(sprite("fbar", 308, 28, box("left:0;top:0;width:308px;height:27px", "<div class='fbar' style='height:27px'></div>")))
    sprites.append(sprite("uc_frame", 284, 50, box("left:0;top:0;width:284px;height:49px", "<div class='uc' style='height:49px'></div>")))
    sprites.append(sprite("dot", 10, 10, box("inset:0;border-radius:50%;background:#fff")))
    sprites.append(sprite("here_arrow", 12, 16, box("left:0;top:0;font:12px Verdana,Tahoma,sans-serif;line-height:16px;color:#fff", "←")))
    # LED counter boxes (pool: 64 wide; footer: 98); the digits are live text, their glow a text shadow.
    sprites.append(sprite("led_box", 64, 24, "<div class='led'></div>"))
    sprites.append(sprite("led_foot", 98, 24, "<div class='led'></div>"))

    # The helper: the bubble in three slices (top, a stretchable middle, the bottom with the
    # tail), each cut from one 60-unit bubble; the leaf with eyes open, half and shut.
    bubble = "<div class='fbubble' style='position:absolute;left:0;top:{top}px;height:60px'></div>"
    sprites.append(sprite("bubble_top", 266, 12, bubble.format(top=0)))
    sprites.append(sprite("bubble_mid", 266, 4, bubble.format(top=-20)))
    sprites.append(sprite("bubble_bot", 266, 22, bubble.format(top=-48)))
    for name, scale in (("leaf_open", 1), ("leaf_half", .55), ("leaf_shut", .1)):
        sprites.append(sprite(name, 112, 124, f"<div class='fleaf' style='position:absolute;left:0;top:0'>{helper_svg(scale)}</div>", pad=6))

    # The banner: sixteen frames of the spinning peace sign (white, tinted yellow), the
    # leaf, and the rainbow WordArt title in both languages (centred in a shared box).
    for i in range(16):
        sprites.append(sprite(f"peace_{i:02d}", 66, 66,
                              box(f"inset:0;color:#fff;transform:rotate({i * 22.5}deg)", sized_svg(PEACE_INNER, 66, 66))))
    sprites.append(sprite("leaf_sym", 66, 66, sized_svg(leaf_inner("#fff"), 66, 66)))
    wa = "<div style='position:absolute;inset:0;display:flex;align-items:center;justify-content:center'><div class='wordart'>{}</div></div>"
    sprites.append({"name": "wordart", "w": 660, "h": 80, "pad": 20,
                    "html_ua": wa.format("~ Дерево досліджень ~"),
                    "html_en": wa.format("~ Research tree ~")})

    # Footer: the star around NEW and the peace sign after the copyright line (white, tinted).
    glyph = "left:0;top:0;font:13px Verdana,Tahoma,sans-serif;line-height:18px;color:#fff;white-space:nowrap"
    sprites.append(sprite("star", 12, 18, box(glyph, "★")))
    sprites.append(sprite("peace_small", 12, 18, box(glyph, "☮")))

    # The tree: legend swatches, the header shade, the edge of the fog (clear at the bottom:
    # the tree grows up).
    sprites.append(sprite("legend_locked", 12, 12, box("inset:0;border:1px dashed #fff")))
    sprites.append(sprite("legend_all", 34, 12, "<svg xmlns='http://www.w3.org/2000/svg' width='34' height='12'><path d='M0 6H26' stroke='#fff' stroke-width='2'/><rect x='26' y='2' width='8' height='8' fill='#fff'/></svg>"))
    sprites.append(sprite("legend_any", 38, 12, "<svg xmlns='http://www.w3.org/2000/svg' width='38' height='12'><path d='M0 6H26' stroke='#fff' stroke-width='2' stroke-dasharray='4 3'/><path d='M32 1l5 5-5 5-5-5z' fill='none' stroke='#fff' stroke-width='1.5'/></svg>"))
    sprites.append(sprite("thead", 8, 90, box("inset:0;background:linear-gradient(" + dark_fade("#020602", 60) + ")")))
    sprites.append(sprite("fog_edge", 8, 80, box("inset:0;background:linear-gradient(0deg," + dark_fade("#ffffff", 0, reverse=True) + ")")))

    textures = [
        # The site's background: 4 x 4 of the mockup's 140-unit tile over #0d0418, so the
        # layout lays 560-unit squares edge to edge and the pattern keeps its size on every
        # screen (a texture tiled at its own pixel size would not).
        {"name": "tile", "w": 560, "h": 560, "size": [1024, 1024],
         "html": box("inset:0;background:#0d0418", box(f"inset:0;opacity:.9;background-image:{ftile()}"))},
    ]

    return {
        "comment": [
            "The freedom window («ВОЛЯ.narod»): every picture the mockup draws with CSS or SVG.",
            "GENERATED by sprites.py next to this file -- edit that, then run it and bake.py freedom.",
            "Sizes are layout units drawn at 1.5 px per unit; white pictures are tinted in the layout.",
        ],
        "scale": 1.5,
        "css": ["freedom.css"],
        "body": {"data-f": "freedom"},
        "sprites": sprites,
        "textures": textures,
    }


def main() -> None:
    text = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    (HERE / "sprites.json").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {HERE / 'sprites.json'}")


if __name__ == "__main__":
    main()
