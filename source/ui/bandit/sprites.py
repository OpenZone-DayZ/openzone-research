#!/usr/bin/env python3
"""Write sprites.json of the bandit window («Записи братви») -- the bake manifest.

    python source/ui/bandit/sprites.py      # then: python source/ui/bake.py bandit

The manifest is generated because much of it repeats: five turned variants of the torn scrap,
the tally marks, and the pictures that lie on a page and "walk" with its paper. Every picture is
the mockup's own markup and CSS (bandit.css holds the lifted rules), so Chrome draws here what it
draws in the mockup. Sizes are layout units (the 1600x900 window), drawn at 1.5 px per unit.
Pictures drawn white are tinted in the layout or by the skin; the rest carry their own colours and
are shown with color 1 1 1 1.

LINEAR LIGHT. The game blends the UI in linear light, Chrome in sRGB, so a half-transparent layer
comes out paler in the game (skill gui-layouts). The alphas of the margin drawings, the blots, the
tape and the notebook's shadow are therefore raised here to what gives the mockup's colours in
the game (solved per layer in linear values over the paper or the desk under it; the mockup's
value is written beside each).

THE PAGE WARP. The mockup bends both pages, and everything on them, with one SVG filter
(#bwarp: fractal noise displacing by up to 3 units). A displacement filter gives the same
pattern wherever it is applied to a box of the same size, so a picture that lies on a page is
drawn here inside a page-sized box shifted to its place, through its own copy of the filter:
the title, the pool heading and the button ring bend exactly as the page under them does.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

PAPER_HI = "#e8dcbc"
FOG = "#c9b88f"

# The torn scrap of a node (.node .cell clip-path of the paper block), 176 x 64.
SCRAP_CLIP = ("polygon(0 6%, 7% 0, 15% 4%, 24% 1%, 33% 5%, 45% 0, 56% 4%, 67% 1%, 78% 5%, 88% 0, 100% 4%, "
              "98% 30%, 100% 55%, 97% 80%, 100% 100%, 86% 96%, 74% 100%, 61% 95%, 49% 100%, 37% 96%, 25% 100%, "
              "13% 95%, 3% 100%, 1% 74%, 3% 48%, 0 26%)")
PAGE_L_CLIP = ("polygon(3% 0, 100% 0, 100% 100%, 1% 100%, 0 96%, 1.2% 91%, 0.2% 86%, 1.4% 79%, 0 72%, 1% 64%, "
               "0.3% 57%, 1.5% 49%, 0 42%, 1.1% 35%, 0.2% 27%, 1.3% 20%, 0 13%, 2.4% 9%, 1% 5%)")
PAGE_R_CLIP = ("polygon(0 0, 98.6% 0, 100% 2.5%, 99.1% 8%, 100% 14%, 99.2% 22%, 100% 31%, 99% 41%, 100% 52%, "
               "99.3% 62%, 100% 71%, 99% 79%, 100% 85%, 97% 88%, 95.5% 92%, 93% 94.5%, 91.5% 98%, 89% 100%, 0 100%)")

# The turned scraps: the nth-child rotations of the bandit block, in the order the skin picks
# them (OZL_TreeSkin_Bandit.Turn): odd, none, 3n, 4n, 5n. No shadow: the mockup gives the cell
# a box-shadow, but its own clip-path cuts it away, so no scrap in the mockup has one (and none
# changes under the mouse). A locked scrap is this picture tinted (ShapeColors).
SCRAP_TURNS = ["rotate(-3.5deg)", "none", "rotate(2.8deg) translateY(3px)", "rotate(-1deg) translateX(-4px)", "rotate(4.5deg)"]
# Where on the right page's crumple each variant takes its creases from (page units).
SCRAP_CREASES = [(40, 140), (300, 330), (520, 120), (150, 560), (560, 470)]

# Linear light: the alpha of black over the desk that darkens it as the mockup's sRGB alpha
# 0, .1 ... 1 does -- the notebook's drop-shadow goes through this table.
SHADOW_ALPHA = "0 .158 .3 .427 .54 .638 .723 .797 .865 .933 1"

# Seeds of the mockup's crumple() per page.
CRUMPLE_SEEDS = {"l": (7, 31), "r": (19, 5)}


def crumple_filter(fid: str, seeds: tuple[int, int], region: str = 'x="0" y="0" width="100%" height="100%"') -> str:
    big, fine = seeds
    return (f'<filter id="{fid}" {region} color-interpolation-filters="sRGB">'
            f'<feTurbulence type="fractalNoise" baseFrequency=".0042 .005" numOctaves="4" seed="{big}" result="big"/>'
            f'<feTurbulence type="turbulence" baseFrequency=".011 .013" numOctaves="2" seed="{fine}" result="fine"/>'
            '<feComposite in="big" in2="fine" operator="arithmetic" k2=".8" k3=".22" result="h"/>'
            '<feDiffuseLighting in="h" surfaceScale="9" lighting-color="#fff" result="lit"><feDistantLight azimuth="235" elevation="50"/></feDiffuseLighting>'
            '<feComponentTransfer><feFuncR type="linear" slope="1.7" intercept="-.8"/><feFuncG type="linear" slope="1.7" intercept="-.8"/>'
            '<feFuncB type="linear" slope="1.7" intercept="-.8"/></feComponentTransfer></filter>')


def crumple_page(fid: str, page: str) -> str:
    """crumple() of the mockup: the whole page, soft light."""
    return ('<div class="crumple"><svg viewBox="0 0 760 852" preserveAspectRatio="none"><defs>'
            + crumple_filter(fid, CRUMPLE_SEEDS[page]) + f'</defs><rect width="760" height="852" filter="url(#{fid})"/></svg></div>')


def crumple_window(fid: str, page: str, x: float, y: float, w: float, h: float) -> str:
    """The same crumple, seen through a window (x, y, w, h) of the page: a box of w x h shows
    the creases the page has there."""
    region = f'filterUnits="userSpaceOnUse" x="{x}" y="{y}" width="{w}" height="{h}"'
    return (f'<svg style="position:absolute;left:0;top:0;width:{w}px;height:{h}px;display:block;mix-blend-mode:soft-light" '
            f'viewBox="{x} {y} {w} {h}" preserveAspectRatio="none"><defs>' + crumple_filter(fid, CRUMPLE_SEEDS[page], region)
            + f'</defs><rect x="{x}" y="{y}" width="{w}" height="{h}" filter="url(#{fid})"/></svg>')


def tear_hole(left: float) -> str:
    """The right page's outline (PAGE_R_CLIP on 760 x 852) as clip-path points, shifted `left`
    units to the left: the hole the paper makes in a picture that starts at x = `left`."""
    points = []
    for pair in PAGE_R_CLIP[len("polygon("):-1].split(","):
        sx, sy = pair.split()
        x = 760 * float(sx.rstrip("%")) / 100 if sx.endswith("%") else float(sx)
        y = 852 * float(sy.rstrip("%")) / 100 if sy.endswith("%") else float(sy)
        points.append(f"{x - left:g}px {y:g}px")
    return ", ".join(points)


def warp_filter(fid: str) -> str:
    """#bwarp of the mockup under an id of its own."""
    return (f'<svg width="0" height="0" style="position:absolute"><filter id="{fid}" x="-2%" y="-2%" width="104%" height="104%">'
            '<feTurbulence type="fractalNoise" baseFrequency=".007 .009" numOctaves="2" seed="4"/>'
            '<feDisplacementMap in="SourceGraphic" scale="6" xChannelSelector="R" yChannelSelector="G"/></filter></svg>')


def on_page(name: str, at: tuple[float, float], inner: str) -> str:
    """`inner` (positioned in page units) drawn on a page-sized box that bends like the page.
    The picture's own box sits at `at` on the page, so the page box is shifted back by it."""
    x, y = at
    return (warp_filter(f"{name}_warp")
            + f'<div style="position:absolute;left:{-x}px;top:{-y}px;width:760px;height:852px;filter:url(#{name}_warp)">{inner}</div>')


def sprite(name, w, h, html, pad=0):
    s = {"name": name, "w": w, "h": h}
    if pad:
        s["pad"] = pad
    s["html"] = html
    return s


def scraps() -> list[dict]:
    out = []
    for i, (turn, (cx, cy)) in enumerate(zip(SCRAP_TURNS, SCRAP_CREASES)):
        name = f"scrap_{i}"
        html = (f'<div style="position:absolute;left:0;top:0;width:176px;height:64px;transform:{turn}">'
                f'<div style="position:absolute;inset:0;clip-path:{SCRAP_CLIP};background:{PAPER_HI};isolation:isolate">'
                + crumple_window(f"{name}_cf", "r", cx, cy, 176, 64) + '</div></div>')
        # pad 12: the most turned scrap, moved 3 down, reaches 10 units past its box
        out.append(sprite(name, 176, 64, html, pad=12))
    return out


def rings() -> list[dict]:
    # .node::after: the ink ring of an available node, dashed red round the selected one. A
    # pseudo-element is not matched by the mockup's `* { box-sizing: border-box }`, so its 2-px
    # border lies OUTSIDE its 200 x 84: the ring is 204 x 88 from (-100, -42), turned about its
    # own centre (stand 2026-10-31: drawn 200 x 84, it came 4 units short on the right and at
    # the bottom). This div is matched by bandit.css's `*`, so it is given the outer size.
    out = []
    for name, style in (("ring", "solid"), ("ring_dash", "dashed")):
        out.append(sprite(name, 204, 88, (
            f'<div style="position:absolute;left:0;top:0;width:204px;height:88px;border:2px {style} #fff;'
            'border-radius:48% 52% 46% 54% / 55% 45% 55% 45%;transform:rotate(-3deg)"></div>'), pad=6))
    return out


def tally() -> list[dict]:
    """tally() of the mockup: tens as crossed squares, fives as four struck bars, the rest bars.
    Each text mark is the span of the mockup's .tally (26 px Caveat, letter-spacing -2 px, 33 high)."""
    out = [sprite("tally_ten", 20, 20, '<div class="t10"></div>', pad=2)]
    # pad 8: the slanted bar of Caveat reaches far past its advance at the top right
    out.append(sprite("tally_five", 26.4, 33, '<span class="tally">||||<i></i></span>', pad=8))
    for n in range(1, 5):
        out.append(sprite(f"tally_{n}", round(6.6 * n, 1), 33, f'<span class="tally">{"|" * n}</span>', pad=8))
    return out


def waves() -> list[dict]:
    """The wavy underlines, long; the layout clips each to its text (a frame as wide as the text).
    wave_name: the card's node name (.cname: 36 px, 1 px, 6 px below); its wave lies 38.75..42.5
    units below the top of the line box, here 1.25..5. wave_sec: the section heads (.sec: 22 px,
    1.5 px, 5 px below): 26.25..32.75 below the line box, here 0.75..7.25."""
    return [
        sprite("wave_name", 660, 6, '<div class="wave" style="top:-37.5px;font-size:36px;line-height:1.15;'
               'text-decoration-thickness:1px;text-underline-offset:6px">' + "x" * 64 + "</div>"),
        sprite("wave_sec", 300, 8, '<div class="wave" style="top:-25.5px;font-size:22px;'
               'text-decoration-thickness:1.5px;text-underline-offset:5px">' + "x" * 48 + "</div>"),
    ]


def page_texts() -> list[dict]:
    """The title with its struck word and the pool heading with its wave, in both languages,
    bent with the left page. Title: .title at (74, 26) of the page; heading: .h at (74, 72)."""
    titles = {"ua": ("Дерево", "знань", "досліджень"), "en": ("Tree of", "knowledge", "research")}
    heads = {"ua": "Общак", "en": "The pot"}
    out = []
    t = {"name": "title", "w": 430, "h": 54}
    for lang, (a, b, c) in titles.items():
        t[f"html_{lang}"] = on_page(f"title_{lang}", (70, 18),
                                    f'<div class="title" style="left:74px;top:26px">{a} <s>{b}</s> {c}</div>')
    out.append(t)
    h = {"name": "pool", "w": 180, "h": 50}
    for lang, word in heads.items():
        h[f"html_{lang}"] = on_page(f"pool_{lang}", (70, 66), f'<div class="h" style="left:74px;top:72px">{word}</div>')
    out.append(h)
    return out


def button() -> list[dict]:
    """.go of the paper block: circled in ink; its hover fill has the same outline. Drawn where the
    button lies when the card has its 'opens' block (69, 752 of the page), bent with the page."""
    return [
        sprite("btn_ring", 657, 58, on_page("btn_ring", (69, 752), '<div class="go" style="left:69px;top:752px"></div>'), pad=6),
        sprite("btn_fill", 657, 58, on_page("btn_fill", (69, 752), '<div class="go fill" style="left:69px;top:752px"></div>'), pad=6),
    ]


def marks() -> list[dict]:
    """The tick of a completed node and the dot of a price chip, white.

    The tick is the mockup's own glyph: .node .mark is ✓ at 34 px in the paper font stack, which
    has no ✓, so Chrome draws its fallback -- drawn here the same way. The sprite's box starts 1
    unit right of and 11 below the .mark box (its ink, measured in the mockup, lies 1..22.5 and
    12..36 inside that box): the node shows it at (170 + 1, 6 + 11) of the cell, pad 2."""
    return [
        sprite("tick", 24, 26, "<div style='position:absolute;left:-1px;top:-11px;font-family:Caveat,\"Segoe Print\",\"Ink Free\",cursive;"
               "font-size:34px;line-height:normal;white-space:nowrap;color:#fff'>\u2713</div>", pad=2),
        sprite("dot", 6, 6, "<div style='position:absolute;inset:0;border-radius:50%;background:#fff'></div>"),
    ]


def legend() -> list[dict]:
    """The legend's marks, white: the dashed box of 'locked' and the two link kinds."""
    return [
        sprite("legend_box", 12, 12, "<div style='position:absolute;inset:0;border:1px dashed #fff'></div>"),
        sprite("legend_all", 34, 12, "<svg xmlns='http://www.w3.org/2000/svg' width='34' height='12'><path d='M0 6H26' "
               "stroke='#fff' stroke-width='2'/><rect x='26' y='2' width='8' height='8' fill='#fff'/></svg>"),
        sprite("legend_any", 38, 12, "<svg xmlns='http://www.w3.org/2000/svg' width='38' height='12'><path d='M0 6H26' "
               "stroke='#fff' stroke-width='2' stroke-dasharray='4 3'/><path d='M32 1l5 5-5 5-5-5z' fill='none' "
               "stroke='#fff' stroke-width='1.5'/></svg>"),
    ]


def margins() -> list[dict]:
    """The tape over the corner, the three ink blots and the doodles of the margins, each with
    the mockup's box, turned as the mockup turns it, in their own colours."""
    def doodle(name, w, h, svg, turn="none", pad=4, viewbox="0 0 100 100"):
        return sprite(name, w, h, f'<div class="doodle" style="left:0;top:0;width:{w}px;height:{h}px;transform:{turn}">'
                                  f'<svg viewBox="{viewbox}">{svg}</svg></div>', pad=pad)
    return [
        # the mockup's .55 over the desk is .32 in linear light (over the paper the two agree)
        sprite("tape", 96, 22, '<div style="position:absolute;left:0;top:0;width:96px;height:22px;'
               'background:rgba(235,225,190,.32);transform:rotate(14deg)"></div>', pad=12),
        sprite("blot_a", 58, 46, '<div class="blot" style="left:0;top:0;width:58px;height:46px"></div>'),
        sprite("blot_b", 40, 34, '<div class="blot" style="left:0;top:0;width:40px;height:34px;transform:rotate(70deg)"></div>', pad=8),
        sprite("blot_c", 30, 26, '<div class="blot" style="left:0;top:0;width:30px;height:26px"></div>'),
        doodle("doodle_skull", 84, 84, '<path d="M28 56C18 30 38 14 55 17 76 20 84 40 73 58L71 72H37Z"/><circle cx="45" cy="44" r="7"/>'
               '<circle cx="64" cy="45" r="7"/><path d="M55 54l-3 7h7zM44 72v10M52 72v11M60 72v10M68 72v9"/>'),
        doodle("doodle_knife", 60, 60, '<path d="M14 82 70 20l9 4-55 62z"/><path d="M24 86 8 99M19 82l9 9"/>', "rotate(-20deg)", pad=10),
        doodle("doodle_arrow", 120, 60, '<path d="M110 8C80 2 50 14 30 44"/><path d="M26 30l2 16 15-4"/>', viewbox="0 0 120 60"),
        sprite("doodle_bang", 21.4, 34, '<div class="doodle txt" style="left:0;top:0;transform:rotate(-12deg)">!!!</div>', pad=8),
        doodle("doodle_spiral", 70, 70, '<path d="M50 50a5 5 0 1 1 10 0 10 10 0 1 1-20 0 15 15 0 1 1 30 0 20 20 0 1 1-40 0 25 25 0 1 1 50 0"/>'),
        doodle("doodle_star", 46, 46, '<path d="M50 8 61 40h33L67 59l10 33-27-20-27 20 10-33L6 40h33z"/>', "rotate(12deg)", pad=6),
    ]


def textures() -> list[dict]:
    spread = (warp_filter("spread_warp")
              + '<div class="spread">'
              + '<div class="pg pg-l">' + crumple_page("spread_cfl", "l") + '</div>'
              + '<div class="spine"></div>'
              + '<div class="pg pg-r"><div class="bg"></div><div class="legend"></div>' + crumple_page("spread_cfr", "r") + '</div>'
              + '</div>')
    def spread_shadow(extra: str = "") -> str:
        return ('<div style="position:absolute;left:28px;top:24px;width:1544px;height:852px;'
                f'filter:drop-shadow(0 8px 14px rgba(0,0,0,.6)){extra}">'
                f'<div style="position:absolute;left:0;top:0;width:760px;height:852px;background:#000;clip-path:{PAGE_L_CLIP}"></div>'
                '<div style="position:absolute;left:760px;top:0;width:24px;height:852px;background:#000"></div>'
                f'<div style="position:absolute;left:784px;top:0;width:760px;height:852px;background:#000;clip-path:{PAGE_R_CLIP}"></div>'
                '</div>')
    # The shadow texture is blended by the game in linear light: its alpha goes through
    # SHADOW_ALPHA. The tear patch below composites the plain shadow over the desk, opaque.
    shadow = ('<svg width="0" height="0" style="position:absolute"><filter id="shadow_lin" x="-20%" y="-20%" width="140%" height="140%">'
              f'<feComponentTransfer><feFuncA type="table" tableValues="{SHADOW_ALPHA}"/></feComponentTransfer></filter></svg>'
              + spread_shadow(" url(#shadow_lin)"))
    # The fog of the tree: the mockup's --fog under the page's crumple. TreeFog and TreeFogEdge
    # show these as they are (the skin's FogColor is white). fog_edge is the 80-unit fade, clear
    # at the top; fog the rest -- one strip of the right page's crumple, 476..806.
    # Under the fade lie the mockup's stripes (`repeating-linear-gradient(135deg, txt 4 % 0 8px,
    # transparent 8px 16px)` under the fog's gradient), so they show only through the fade;
    # 4 % -> 7.5 % in linear light (over the squared paper).
    fog_edge = ('<div style="position:absolute;left:0;top:0;width:748px;height:80px;'
                'background:repeating-linear-gradient(135deg,rgba(42,32,24,.075) 0 8px,transparent 8px 16px)"></div>'
                f'<div style="position:absolute;left:0;top:0;width:748px;height:80px;isolation:isolate;background:{FOG};'
                '-webkit-mask-image:linear-gradient(180deg,transparent,#000);mask-image:linear-gradient(180deg,transparent,#000)">'
                + crumple_window("fog_edge_cf", "r", 0, 476, 748, 80) + '</div>')
    fog = (f'<div style="position:absolute;left:0;top:0;width:748px;height:250px;isolation:isolate;background:{FOG}">'
           + crumple_window("fog_cf", "r", 0, 556, 748, 250) + '</div>')
    # What the torn right edge and the torn-off corner take away from the tree: the mockup's
    # clip-path cuts the whole page, its fog, scraps and scrollbars included; in the game nothing
    # clips to a torn outline, so this lies over the tree's right end (page x 676..760, y 0..818)
    # and draws the desk with the notebook's shadow wherever the paper is gone. The desk's faint
    # stripes are left out: their tiling depends on the screen.
    # The texture repeats: its last texel column is sampled into its first (stand 2026-10-31: a
    # 1-px dark seam along the patch's left edge, where the paper shows through). So the picture
    # is 2 units wider than the patch and those 2 stay clear, like its first column (the shadow
    # layer runs past the clip box, so the patch is cut at 84 first); TearR is as
    # wide, its last 2 units lie past the page's 760 over the same desk, and the patch still
    # covers the tree's scrollbar to the page's edge as before.
    tear = ('<div style="position:absolute;left:0;top:0;width:84px;height:818px;overflow:hidden">'
            '<div style="position:absolute;left:0;top:0;width:84px;height:818px;'
            f'clip-path:polygon(evenodd, -2px -2px, 86px -2px, 86px 820px, -2px 820px, -2px -2px, {tear_hole(676)})">'
            '<div style="position:absolute;inset:0;background:#2b1b10"></div>'
            f'<div style="position:absolute;left:-1488px;top:-24px;width:1600px;height:900px">{spread_shadow()}</div></div></div>')
    return [
        {"name": "spread", "w": 1544, "h": 852, "size": [2048, 1024], "html": spread},
        {"name": "shadow", "w": 1600, "h": 900, "size": [1024, 512], "html": shadow},
        {"name": "fog_edge", "w": 748, "h": 80, "size": [512, 64], "html": fog_edge},
        {"name": "fog", "w": 748, "h": 250, "size": [512, 256], "html": fog},
        {"name": "tear_r", "w": 86, "h": 818, "size": [128, 1024], "html": tear},
        # The desk under the notebook (#stage of the paper skins), tiled at its own size; the
        # mockup's stripes run at 92 degrees, a tile needs them square.
        {"name": "desk", "w": 120, "h": 120, "size": [128, 128],
         "html": "<div style='position:absolute;inset:0;background:#2b1b10 repeating-linear-gradient(90deg,rgba(0,0,0,.18) 0 3px,"
                 "transparent 3px 22px,rgba(255,200,140,.04) 22px 24px,transparent 24px 60px)'></div>"},
        # A dashed line of the paper (the progress line of a node, the underline of an 'opens'
        # chip), tiled: 4 on, 4 off, 2 high, white.
        {"name": "dash", "w": 16, "h": 16, "size": [16, 16],
         "html": "<div style='position:absolute;left:0;top:0;width:4px;height:2px;background:#fff'></div>"
                 "<div style='position:absolute;left:8px;top:0;width:4px;height:2px;background:#fff'></div>"},
    ]


def manifest() -> dict:
    return {
        "comment": [
            "GENERATED by sprites.py next to this file -- edit that, then run it and bake.",
            "The bandit window («Записи братви»): every picture the mockup draws with CSS. Sizes are layout units,",
            "drawn at 1.5 px per unit. White pictures are tinted in the game; the rest carry their own colours.",
        ],
        "scale": 1.5,
        "css": ["bandit.css"],
        "body": {"data-f": "bandit"},
        "sprites": (scraps() + rings() + marks() + tally() + waves() + page_texts() + button() + legend() + margins()),
        "textures": textures(),
    }


def main() -> None:
    text = json.dumps(manifest(), ensure_ascii=False, indent=2) + "\n"
    (HERE / "sprites.json").write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {HERE / 'sprites.json'}")


if __name__ == "__main__":
    main()
