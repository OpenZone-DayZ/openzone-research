#!/usr/bin/env python3
"""Bake HTML/CSS pictures into DayZ textures: sprites -> atlas -> .imageset -> _ca.paa.

    python source/ui/bake.py common duty   # these sets (the shared `common` and the skin `duty`)
    python source/ui/bake.py --all         # every set that has a sprites.json

Input   source/ui/<set>/sprites.json and the CSS files it names
Output  OpenZone_Research/gui/imagesets/ozl_<set>.imageset + ozl_<set>_ca.paa
        OpenZone_Research/gui/textures/tree/<set>/<name>_ca.paa
        build/ui/<set>/      pages, PNGs, preview (git-ignored, safe to delete)

Needs Python 3 with Pillow, Node 22+ and Google Chrome (shoot.mjs draws the pages), and DayZ Tools
(ImageToPAA). The manifest format, the rules and the reasons are in source/ui/README.md; this file
only does it.
"""
from __future__ import annotations

import argparse
import html as htmllib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
MOD = "OpenZone_Research"          # the pbo prefix ($PBOPREFIX$) -- the root of every in-game path
LANGS = ("uk", "en")               # html_uk + html_en make name_uk + name_en
BLEED = 4                          # px of colour carried from a visible pixel into transparent ones
MIN_ATLAS = 32
MIN_TEXTURE = 16
MAX_TEXTURE = 4096
POT = (16, 32, 64, 128, 256, 512, 1024, 2048, 4096)
CANARY = (1, 2, 3, 255)            # the pixel every page ends with: proof that the whole page was painted

DEFAULT_CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DEFAULT_TOOLS = r"E:\Programs\Steam\steamapps\common\DayZ Tools"

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
SET_RE = re.compile(r"^_?[a-z][a-z0-9_]*$")
TOP_KEYS = {"comment", "scale", "atlas_max", "gutter", "css", "body", "sprites", "textures"}
ITEM_KEYS = {"name", "w", "h", "html", "html_uk", "html_en", "css"}
SPRITE_KEYS = ITEM_KEYS | {"pad"}
TEXTURE_KEYS = ITEM_KEYS | {"size"}


class BakeError(Exception):
    """A problem the person running the bake can fix; reported without a traceback."""


def fail(msg: str):
    raise BakeError(msg)


# ----------------------------------------------------------------------------- manifest


@dataclass
class Item:
    """One picture to draw: an atlas sprite or a standalone texture."""

    name: str
    w: float                        # design box, layout units
    h: float
    html: str
    css: str = ""                   # declarations and nested rules, scoped to this picture's box
    pad: float = 0.0                # units kept around the box for glows and shadows
    size: tuple[int, int] | None = None   # textures only: the power-of-two canvas to stretch to
    pad_px: int = 0                 # the pad in whole device pixels (set when the picture is placed)
    pw: int = 0                     # size of the picture in device pixels, pad included
    ph: int = 0


@dataclass
class Skin:
    """A folder of source/ui: a faction skin, or the shared `common` set."""

    name: str
    folder: Path
    scale: float
    atlas_max: int
    gutter: int
    css: str
    body: dict[str, str]
    sprites: list[Item]
    textures: list[Item]

    @property
    def set_name(self) -> str:
        return "ozl_" + self.name.lstrip("_")


def _number(v, what: str, lo: float, hi: float, integer: bool = False):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        fail(f"{what}: expected a number, got {v!r}")
    if integer and v != int(v):
        fail(f"{what}: expected a whole number, got {v!r}")
    if not lo <= v <= hi:
        fail(f"{what}: {v!r} is outside {lo}..{hi}")
    return int(v) if integer else v


def _text(v, what: str) -> str:
    """A string, or a list of strings that is joined with newlines (easier to write in JSON)."""
    if isinstance(v, str):
        return v
    if isinstance(v, list) and all(isinstance(s, str) for s in v):
        return "\n".join(v)
    fail(f"{what}: expected a string or a list of strings")


def _css(v, folder: Path, what: str) -> str:
    """CSS from the manifest: each entry is inline text (it has a '{') or a file name."""
    parts = v if isinstance(v, list) else [v]
    out = []
    for i, part in enumerate(parts):
        if not isinstance(part, str):
            fail(f"{what}[{i}]: expected a string")
        if "{" in part or "\n" in part or ";" in part:
            out.append(part)
            continue
        path = folder / part
        if not path.is_file():
            fail(f"{what}[{i}]: {part!r} has no '{{' so it is a file name, and {path} does not exist")
        out.append(path.read_text(encoding="utf-8-sig"))
    return "\n".join(out)


def _items(raw_list, kind: str) -> list[Item]:
    if not isinstance(raw_list, list):
        fail(f"{kind}s: expected a list")
    allowed = SPRITE_KEYS if kind == "sprite" else TEXTURE_KEYS
    items: list[Item] = []
    for i, raw in enumerate(raw_list):
        where = f"{kind}s[{i}]"
        if not isinstance(raw, dict):
            fail(f"{where}: expected an object")
        extra = set(raw) - allowed
        if extra:
            fail(f"{where}: unknown key(s) {sorted(extra)}; allowed: {sorted(allowed)}")
        name = raw.get("name")
        if not isinstance(name, str) or not NAME_RE.match(name):
            fail(f"{where}: name must be letters, digits and underscores, starting with a letter: {name!r}")
        where = f"{kind} {name}"
        w = _number(raw.get("w"), f"{where}: w", 0.5, 8192)
        h = _number(raw.get("h"), f"{where}: h", 0.5, 8192)
        pad = _number(raw.get("pad", 0), f"{where}: pad", 0, 1024) if kind == "sprite" else 0
        css = _text(raw["css"], f"{where}: css") if "css" in raw else ""
        size = None
        if "size" in raw:
            s = raw["size"]
            if not (isinstance(s, list) and len(s) == 2 and all(isinstance(n, int) and n in POT for n in s)):
                fail(f"{where}: size must be [width, height], each a power of two in {POT[0]}..{POT[-1]}")
            size = (s[0], s[1])

        plain = "html" in raw
        langs = [lang for lang in LANGS if f"html_{lang}" in raw]
        if plain and langs:
            fail(f"{where}: give html, or html_uk with html_en, not both")
        if not plain and not langs:
            fail(f"{where}: no html (use html, or html_uk with html_en)")
        if langs and len(langs) != len(LANGS):
            missing = [f"html_{lang}" for lang in LANGS if lang not in langs]
            fail(f"{where}: language variants come in a set, {missing} is missing")
        sources = [(name, raw["html"])] if plain else [(f"{name}_{lang}", raw[f"html_{lang}"]) for lang in LANGS]
        for out_name, markup in sources:
            items.append(Item(out_name, w, h, _text(markup, f"{where}: html"), css, pad, size))
    return items


def load_skin(name: str, ui_dir: Path = HERE) -> Skin:
    if not SET_RE.match(name):
        fail(f"{name!r} is not a set name (lowercase letters, digits, underscores; a leading _ marks an example)")
    folder = ui_dir / name
    path = folder / "sprites.json"
    if not path.is_file():
        known = sorted(p.parent.name for p in ui_dir.glob("*/sprites.json"))
        fail(f"{path} not found; sets with a manifest: {', '.join(known) or 'none'}")
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        fail(f"{path}: not valid JSON: {exc}")
    if not isinstance(data, dict):
        fail(f"{path}: the top level must be an object")
    extra = set(data) - TOP_KEYS
    if extra:
        fail(f"{path}: unknown key(s) {sorted(extra)}; allowed: {sorted(TOP_KEYS)}")

    scale = _number(data.get("scale", 1.5), "scale", 0.25, 8)
    atlas_max = _number(data.get("atlas_max", 2048), "atlas_max", 64, 4096, integer=True)
    if atlas_max not in POT:
        fail(f"atlas_max: {atlas_max} is not a power of two")
    gutter = _number(data.get("gutter", 4), "gutter", 0, 32, integer=True)
    body = data.get("body", {})
    if not (isinstance(body, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in body.items())):
        fail("body: expected an object of attribute name -> string")
    sprites = _items(data.get("sprites", []), "sprite")
    textures = _items(data.get("textures", []), "texture")
    if not sprites:
        fail(f"{path}: no sprites -- every set needs an atlas, add the 8x8 transparent 'blank'")
    for kind, group in (("sprite", sprites), ("texture", textures)):
        seen: set[str] = set()
        for it in group:
            if it.name in seen:
                fail(f"{kind} name {it.name!r} is used twice")
            seen.add(it.name)
    css = _css(data["css"], folder, "css") if "css" in data else ""
    return Skin(name, folder, scale, atlas_max, gutter, css, body, sprites, textures)


# ------------------------------------------------------------------------- pages


def px_of(units: float, dsf: float) -> int:
    return max(1, math.ceil(units * dsf - 1e-6))


def grid_step(dsf: float) -> int:
    """Smallest whole number of CSS px that is also a whole number of device px.

    Sprites sit on the sheet at multiples of it, so each one is drawn from the same pixel
    phase wherever it lands. Returns 1 (and sprites may be half a pixel off) if there is none.
    """
    for q in range(1, 5):
        if abs(q * dsf - round(q * dsf)) < 1e-9:
            return q
    return 1


@dataclass
class Sheet:
    """One page to draw: pictures at known rectangles on a transparent ground."""

    stem: str
    items: list[Item]
    dsf: float
    placed: list[tuple[Item, int, int]]     # item, x, y in CSS px
    width: int                              # page size in CSS px
    height: int
    gap: int
    page: Path
    png: Path


def make_sheet(skin: Skin, items: list[Item], dsf: float, build: Path, stem: str) -> Sheet:
    """Size every picture, put them in shelf rows (manifest order), write the page."""
    for it in items:
        it.pad_px = math.ceil(it.pad * dsf - 1e-6) if it.pad > 0 else 0
        it.pw = px_of(it.w, dsf) + 2 * it.pad_px
        it.ph = px_of(it.h, dsf) + 2 * it.pad_px
    q = grid_step(dsf)
    gap = q * math.ceil(4 / q)                # >= 4 CSS px between pictures and round the page
    boxes = [(it, it.pw / dsf, it.ph / dsf) for it in items]
    widest = max(math.ceil(bw) for _, bw, _ in boxes)
    one_row = math.ceil(sum(bw + gap for _, bw, _ in boxes)) + gap
    width = max(widest + 2 * gap, min(1600, one_row))
    placed: list[tuple[Item, int, int]] = []
    x = y = gap
    row = 0.0
    for it, bw, bh in boxes:
        if x > gap and x + bw > width - gap:
            x, y, row = gap, y + math.ceil(row / q) * q + gap, 0.0
        placed.append((it, x, y))
        x = math.ceil((x + bw + gap) / q) * q
        row = max(row, bh)
    height = y + math.ceil(row) + gap
    page = build / f"{stem}.html"
    page.write_text(build_page(skin, placed, width, height, gap, dsf), encoding="utf-8", newline="\n")
    return Sheet(stem, items, dsf, placed, width, height, gap, page, build / f"{stem}.png")


RESET_CSS = (
    "html,body{margin:0;padding:0}\n"
    "#oz-sheet{position:fixed;left:0;top:0}\n"
    ".oz-c{position:absolute;overflow:hidden}\n"
    ".oz-s{position:absolute;box-sizing:border-box}\n"
    # an inline svg sits on the text baseline and would drop a few units out of a small box
    ".oz-s>svg,.oz-s>img{display:block}\n"
)
# After the skin's CSS, so a lifted `body { background: ... }` or a blinking mark cannot spoil the bake.
FINAL_CSS = (
    "html,body{background:transparent!important}\n"
    "*,*::before,*::after{animation:none!important;transition:none!important}\n"
)


def build_page(skin: Skin, placed: list[tuple[Item, int, int]], width: int, height: int, gap: int, dsf: float) -> str:
    boxes, scoped = [], []
    for n, (it, x, y) in enumerate(placed):
        boxes.append(
            f'<div class="oz-c" style="left:{x}px;top:{y}px;width:{it.pw / dsf:.6f}px;height:{it.ph / dsf:.6f}px">'
            f'<div class="oz-s" id="oz{n}" style="left:{it.pad_px / dsf:.6f}px;top:{it.pad_px / dsf:.6f}px;'
            f'width:{it.w:g}px;height:{it.h:g}px">{it.html}</div></div>'
        )
        if it.css.strip():
            scoped.append(f"#oz{n} {{\n{it.css}\n}}")
    canary = (f'<div id="oz-canary" style="position:absolute;left:{width - gap}px;top:{height - gap}px;'
              f'width:2px;height:2px;background:rgb({CANARY[0]},{CANARY[1]},{CANARY[2]})"></div>')
    attrs = "".join(f' {k}="{htmllib.escape(v, quote=True)}"' for k, v in skin.body.items())
    return (
        '<!doctype html>\n<html lang="uk"><head><meta charset="utf-8">\n'
        f'<base href="{skin.folder.as_uri()}/">\n'
        f"<style>\n{RESET_CSS}{skin.css}\n{chr(10).join(scoped)}\n{FINAL_CSS}</style>\n</head>\n"
        f'<body{attrs}>\n<div id="oz-sheet" style="width:{width}px;height:{height}px">\n'
        + "\n".join(boxes) + f"\n{canary}\n</div>\n</body></html>\n"
    )


# ------------------------------------------------------------------------- Chrome


def find_chrome(arg: str | None) -> Path:
    for cand in (arg, os.environ.get("CHROME"), DEFAULT_CHROME, shutil.which("chrome"), shutil.which("google-chrome")):
        if cand and Path(cand).is_file():
            return Path(cand)
    fail(f"Google Chrome not found (tried {arg or os.environ.get('CHROME') or DEFAULT_CHROME}); pass --chrome or set CHROME")


def find_node(arg: str | None) -> Path:
    cand = arg or os.environ.get("NODE") or shutil.which("node")
    if not cand or not Path(cand).is_file():
        fail("Node.js 22 or newer not found (shoot.mjs draws the pages with it); pass --node or put node on PATH")
    return Path(cand)


def find_image_to_paa(arg: str | None) -> Path:
    tools = arg or os.environ.get("DAYZ_TOOLS") or DEFAULT_TOOLS
    exe = Path(tools) / "Bin" / "ImageToPAA" / "ImageToPAA.exe"
    if not exe.is_file():
        fail(f"ImageToPAA.exe not found at {exe}; pass --dayz-tools or set DAYZ_TOOLS")
    return exe


def render(chrome: Path, node: Path, sheets: list[Sheet], build: Path) -> None:
    """One Chrome session draws every page of the skin (shoot.mjs, over the DevTools protocol)."""
    jobs = [{"url": s.page.as_uri(), "out": str(s.png), "width": s.width, "height": s.height, "scale": s.dsf}
            for s in sheets]
    jobs_file = build / "jobs.json"
    jobs_file.write_text(json.dumps(jobs, indent=1), encoding="utf-8", newline="\n")
    for s in sheets:
        s.png.unlink(missing_ok=True)
    try:
        run = subprocess.run([str(node), str(HERE / "shoot.mjs"), str(chrome), str(jobs_file)],
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    except subprocess.TimeoutExpired:
        fail("Chrome did not finish drawing the pages in 15 minutes")
    if run.returncode != 0:
        fail(f"shoot.mjs failed (exit {run.returncode}): {(run.stderr or run.stdout).strip()[-600:]}")


def pictures(sheet: Sheet) -> list[Image.Image]:
    """Cut the pictures out of the drawn page, after checking that the page really is whole."""
    if not sheet.png.is_file():
        fail(f"no screenshot of {sheet.page.name}")
    with Image.open(sheet.png) as opened:
        shot = opened.convert("RGBA")
    want = (round(sheet.width * sheet.dsf), round(sheet.height * sheet.dsf))
    if abs(shot.width - want[0]) > 1 or abs(shot.height - want[1]) > 1:
        fail(f"{sheet.png.name} is {shot.width}x{shot.height}, expected about {want[0]}x{want[1]}")
    if shot.getpixel((shot.width - 1, shot.height - 1))[3] != 0:
        fail(f"{sheet.png.name}: the empty corner of the page is not transparent -- something paints a "
             "background (a lifted CSS rule on html, body or :root?)")
    at = (int((sheet.width - sheet.gap + 1) * sheet.dsf), int((sheet.height - sheet.gap + 1) * sheet.dsf))
    if shot.getpixel(at) != CANARY:
        fail(f"{sheet.png.name}: the last pixel of the page is missing -- the page was only partly drawn")
    left, top = round((sheet.width - sheet.gap) * sheet.dsf), round((sheet.height - sheet.gap) * sheet.dsf)
    ImageDraw.Draw(shot).rectangle((left, top, shot.width - 1, shot.height - 1), fill=(0, 0, 0, 0))   # the canary has done its job
    print(f"  {sheet.stem}: {len(sheet.items)} picture(s) on a {sheet.width}x{sheet.height} page, drawn at "
          f"{sheet.dsf:g} px per unit -> {shot.width}x{shot.height} px, {alpha_info(shot)}")
    pics = []
    for it, x, y in sheet.placed:
        px, py = round(x * sheet.dsf), round(y * sheet.dsf)
        pics.append(shot.crop((px, py, px + it.pw, py + it.ph)))
    return pics


def alpha_info(img: Image.Image) -> str:
    hist = img.getchannel("A").histogram()
    levels = [a for a, c in enumerate(hist) if c]
    return f"alpha {levels[0]}..{levels[-1]}, {len(levels)} levels" if levels else "alpha empty"


# ------------------------------------------------------------------------- pixels


def extend_edges(img: Image.Image, g: int) -> Image.Image:
    """The sprite with a gutter of `g` px whose pixels repeat the sprite's edge pixels."""
    w, h = img.size
    cell = Image.new("RGBA", (w + 2 * g, h + 2 * g), (0, 0, 0, 0))
    cell.paste(img, (g, g))
    if g:
        near = Image.Resampling.NEAREST
        cell.paste(img.crop((0, 0, w, 1)).resize((w, g), near), (g, 0))
        cell.paste(img.crop((0, h - 1, w, h)).resize((w, g), near), (g, g + h))
        cell.paste(img.crop((0, 0, 1, h)).resize((g, h), near), (0, g))
        cell.paste(img.crop((w - 1, 0, w, h)).resize((g, h), near), (g + w, g))
        for (sx, sy), (dx, dy) in (((0, 0), (0, 0)), ((w - 1, 0), (g + w, 0)),
                                   ((0, h - 1), (0, g + h)), ((w - 1, h - 1), (g + w, g + h))):
            cell.paste(Image.new("RGBA", (g, g), img.getpixel((sx, sy))), (dx, dy))
    return cell


_NEIGHBOURS = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]


def bleed(img: Image.Image, radius: int) -> Image.Image:
    """Give each fully transparent pixel within `radius` px of a visible one that pixel's colour.

    Chrome writes transparent pixels as 0,0,0,0. Filtering (bilinear, mipmaps, DXT blocks) then
    mixes that black into the edge of a white glyph and draws a dark fringe round it. The alpha
    is left alone, so nothing visible changes.
    """
    lo, hi = img.getchannel("A").getextrema()
    if radius <= 0 or hi == 0 or lo > 0:
        return img
    w, h = img.size
    work = Image.new("RGBA", (w + 2, h + 2), (0, 0, 0, 0))     # a 1 px margin stops offset() wrapping round
    work.paste(img, (1, 1))
    alpha = work.getchannel("A")
    known = alpha.point(lambda a: 255 if a else 0)
    rgb = work.convert("RGB")
    for _ in range(radius):
        new_rgb, new_known = rgb.copy(), known.copy()
        for dx, dy in _NEIGHBOURS:
            take = ImageChops.subtract(ImageChops.offset(known, dx, dy), new_known)
            new_rgb.paste(ImageChops.offset(rgb, dx, dy), mask=take)
            new_known = ImageChops.lighter(new_known, take)
        rgb, known = new_rgb, new_known
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out.crop((1, 1, w + 1, h + 1))


def next_pot(n: int) -> int:
    return 1 << max(0, n - 1).bit_length()


def _split(free, used):
    ux, uy, uw, uh = used
    keep = []
    for fx, fy, fw, fh in free:
        if ux >= fx + fw or ux + uw <= fx or uy >= fy + fh or uy + uh <= fy:
            keep.append((fx, fy, fw, fh))
            continue
        if ux > fx:
            keep.append((fx, fy, ux - fx, fh))
        if ux + uw < fx + fw:
            keep.append((ux + uw, fy, fx + fw - ux - uw, fh))
        if uy > fy:
            keep.append((fx, fy, fw, uy - fy))
        if uy + uh < fy + fh:
            keep.append((fx, uy + uh, fw, fy + fh - uy - uh))

    def inside(a, b):      # a lies wholly in b
        return a[0] >= b[0] and a[1] >= b[1] and a[0] + a[2] <= b[0] + b[2] and a[1] + a[3] <= b[1] + b[3]

    return [a for i, a in enumerate(keep)
            if not any(j != i and inside(a, b) and (a != b or j < i) for j, b in enumerate(keep))]


def _try_pack(width: int, height: int, sizes: list[tuple[int, int]], order: list[int]):
    """MaxRects, best short side fit. Ties break on position, so the result is the same every run."""
    free = [(0, 0, width, height)]
    spots: list[tuple[int, int] | None] = [None] * len(sizes)
    for i in order:
        w, h = sizes[i]
        best = None
        for fx, fy, fw, fh in free:
            if w <= fw and h <= fh:
                key = (min(fw - w, fh - h), max(fw - w, fh - h), fy, fx)
                if best is None or key < best[0]:
                    best = (key, fx, fy)
        if best is None:
            return None
        spots[i] = (best[1], best[2])
        free = _split(free, (best[1], best[2], w, h))
    return spots


def pack(sizes: list[tuple[int, int]], max_dim: int) -> tuple[tuple[int, int], list[tuple[int, int]]]:
    """The smallest power-of-two rectangle (<= max_dim) that holds every cell, and where each goes."""
    area = sum(w * h for w, h in sizes)
    order = sorted(range(len(sizes)), key=lambda i: (-(sizes[i][0] * sizes[i][1]), -max(sizes[i]), i))
    dims = [d for d in POT if MIN_ATLAS <= d <= max_dim]
    for width, height in sorted(((w, h) for w in dims for h in dims), key=lambda s: (s[0] * s[1], abs(s[0] - s[1]), -s[0])):
        if width * height < area or any(w > width or h > height for w, h in sizes):
            continue
        spots = _try_pack(width, height, sizes, order)
        if spots is not None:
            return (width, height), spots  # type: ignore[return-value]
    biggest = max(sizes, key=lambda s: s[0] * s[1])
    fail(f"the sprites do not fit one {max_dim}x{max_dim} atlas: {len(sizes)} cells, {area} px2 "
         f"(the biggest is {biggest[0]}x{biggest[1]}). Draw some as textures, or lower the scale.")


def save_png(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", compress_level=9)


# ------------------------------------------------------------------------- outputs


def write_if_changed(path: Path, data: bytes) -> bool:
    """Leave an identical file alone, so a second run touches nothing."""
    if path.is_file() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return True


def imageset_text(skin: Skin, atlas_size: tuple[int, int], texture_path: str,
                  entries: list[tuple[str, int, int, int, int]]) -> str:
    lines = [
        f"// GENERATED by source/ui/bake.py from source/ui/{skin.name}/sprites.json -- edit the manifest, not this file.",
        "ImageSetClass {", f' Name "{skin.set_name}"', f" RefSize {atlas_size[0]} {atlas_size[1]}",
        " Textures {", "  ImageSetTextureClass {", "   mpix 0", f'   path "{texture_path}"', "  }", " }", " Images {",
    ]
    for name, x, y, w, h in entries:
        lines += [f"  ImageSetDefClass {name} {{", f'   Name "{name}"', f"   Pos {x} {y}", f"   Size {w} {h}", "   Flags 0", "  }"]
    lines += [" }", " Groups {", " }", "}"]
    return "\n".join(lines) + "\n"


def to_paa(exe: Path, png: Path, dest: Path, work: Path) -> tuple[int, str]:
    """PNG (named ..._ca) -> DXT5 .paa, and read back what came out. Returns (bytes, what was checked)."""
    if not png.stem.endswith("_ca"):
        fail(f"{png.name}: ImageToPAA picks DXT5 (alpha kept) only for a name ending in _ca")
    tmp = work / (png.stem + ".paa")
    tmp.unlink(missing_ok=True)
    tool = dict(capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=work, timeout=300)
    run = subprocess.run([str(exe), str(png), str(tmp)], **tool)
    note = (run.stdout + run.stderr).strip()
    if not tmp.is_file() or tmp.stat().st_size == 0:
        fail(f"ImageToPAA (exit {run.returncode}) wrote no {tmp.name}: {note[-300:]}")
    data = tmp.read_bytes()
    if run.returncode != 0:
        fail(f"ImageToPAA exited {run.returncode} on {png.name}: {note[-300:]}")
    if data[:2] != b"\x05\xff":
        fail(f"{tmp.name} starts {data[:2].hex()}, not 05ff (DXT5): the alpha would be lost")

    # The tool also reads a .paa back into a PNG. Compare what it wrote with what it was given.
    back = work / (png.stem + ".readback.png")
    back.unlink(missing_ok=True)
    subprocess.run([str(exe), str(tmp), str(back)], **tool)
    if not back.is_file():
        fail(f"ImageToPAA cannot read back {tmp.name}")
    with Image.open(png) as a, Image.open(back) as b:
        src, got = a.convert("RGBA"), b.convert("RGBA")
    if got.size != src.size:
        fail(f"{tmp.name} reads back as {got.size}, was {src.size}")
    if got.getchannel("A").getextrema() != src.getchannel("A").getextrema():
        fail(f"{tmp.name}: alpha {src.getchannel('A').getextrema()} went in, "
             f"{got.getchannel('A').getextrema()} came out")
    write_if_changed(dest, data)
    return len(data), f"DXT5 {src.width}x{src.height}, read back {alpha_info(got)}"


@dataclass
class Report:
    files: list[tuple[str, int]] = field(default_factory=list)     # path, bytes
    paa_bytes: int = 0


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return str(path)


# ------------------------------------------------------------------------- one set


def write_preview(atlas: Image.Image, entries, path: Path) -> None:
    zoom = max(1, 1024 // max(atlas.size))
    big = atlas.resize((atlas.width * zoom, atlas.height * zoom), Image.Resampling.NEAREST)
    board = Image.new("RGBA", big.size, (64, 64, 64, 255))
    draw = ImageDraw.Draw(board)
    for ty in range(0, big.height, 16):
        for tx in range(0, big.width, 16):
            if (tx // 16 + ty // 16) % 2:
                draw.rectangle((tx, ty, tx + 15, ty + 15), fill=(96, 96, 96, 255))
    board.alpha_composite(big)
    for name, x, y, w, h in entries:
        draw.rectangle((x * zoom - 1, y * zoom - 1, (x + w) * zoom, (y + h) * zoom), outline=(0, 200, 255, 255))
        draw.text((x * zoom + 2, y * zoom + 2), name, fill=(255, 220, 0, 255))
    save_png(board, path)


def texture_dsf(skin: Skin, tex: Item) -> float:
    """Drawn at the set's scale; if `size` asks for more pixels than that gives, drawn at the size's own density."""
    if tex.size:
        return max(skin.scale, tex.size[0] / tex.w, tex.size[1] / tex.h)
    return skin.scale


def bake_skin(skin: Skin, chrome: Path, node: Path, paa_exe: Path, mod_root: Path, build_root: Path, report: Report) -> None:
    build = build_root / skin.name
    if build.exists():
        shutil.rmtree(build)
    build.mkdir(parents=True)
    g = skin.gutter
    print(f"[{skin.name}] {len(skin.sprites)} sprites, {len(skin.textures)} textures, scale {skin.scale:g}, gutter {g}")
    if grid_step(skin.scale) == 1 and abs(skin.scale - round(skin.scale)) > 1e-9:
        print(f"  note: scale {skin.scale:g} has no whole-pixel step, sprites may sit half a pixel off the pixel grid")

    # --- draw: the sprites on one page, each texture on its own, all in one Chrome session
    sheet = make_sheet(skin, skin.sprites, skin.scale, build, "sheet")
    tex_sheets = [make_sheet(skin, [t], texture_dsf(skin, t), build, f"tex_{t.name}") for t in skin.textures]
    render(chrome, node, [sheet] + tex_sheets, build)

    # --- the atlas
    pics = pictures(sheet)
    cells =[bleed(extend_edges(pic, g), BLEED) for pic in pics]
    sizes = [(c.width, c.height) for c in cells]
    (aw, ah), spots = pack(sizes, skin.atlas_max)
    atlas = Image.new("RGBA", (aw, ah), (0, 0, 0, 0))
    entries = []
    for it, cell, (cx, cy) in zip(skin.sprites, cells, spots):
        atlas.paste(cell, (cx, cy))
        entries.append((it.name, cx + g, cy + g, it.pw, it.ph))
    for i, a in enumerate(spots):            # the gutter-wide cell of one sprite must never reach another
        for j in range(i):
            b = spots[j]
            if a[0] < b[0] + sizes[j][0] and b[0] < a[0] + sizes[i][0] and a[1] < b[1] + sizes[j][1] and b[1] < a[1] + sizes[i][1]:
                fail(f"internal error: cells {skin.sprites[i].name} and {skin.sprites[j].name} overlap")
    used = sum(w * h for w, h in sizes)
    print(f"  atlas {aw}x{ah} ({100 * used // (aw * ah)} % cells), {alpha_info(atlas)}")

    png = build / f"{skin.set_name}_ca.png"
    save_png(atlas, png)
    write_preview(atlas, entries, build / "preview.png")
    sets = mod_root / "gui" / "imagesets"
    paa_len, note = to_paa(paa_exe, png, sets / f"{skin.set_name}_ca.paa", build)
    text = imageset_text(skin, (aw, ah), f"{MOD}/gui/imagesets/{skin.set_name}_ca.paa", entries)
    write_if_changed(sets / f"{skin.set_name}.imageset", text.encode("utf-8"))
    report.files += [(rel(sets / f"{skin.set_name}.imageset"), len(text)), (rel(sets / f"{skin.set_name}_ca.paa"), paa_len)]
    report.paa_bytes += paa_len
    print(f"  {rel(sets / (skin.set_name + '.imageset'))}  ({len(entries)} images)")
    print(f"  {rel(sets / (skin.set_name + '_ca.paa'))}  {paa_len:,} bytes, {note}")

    # --- the standalone textures
    for tex, tsheet in zip(skin.textures, tex_sheets):
        bake_texture(skin, tex, tsheet, paa_exe, mod_root, build, report)


def bake_texture(skin: Skin, tex: Item, sheet: Sheet, paa_exe: Path, mod_root: Path, build: Path, report: Report) -> None:
    pic = pictures(sheet)[0]
    if tex.size:
        if pic.size != tex.size:
            pic = pic.resize(tex.size, Image.Resampling.LANCZOS)
        canvas, where = pic, "fills the canvas"
    else:
        cw, ch = max(MIN_TEXTURE, next_pot(pic.width)), max(MIN_TEXTURE, next_pot(pic.height))
        canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        canvas.paste(pic, (0, 0))
        where = f"content is the top-left {pic.width}x{pic.height} px"
    if max(canvas.size) > MAX_TEXTURE:
        fail(f"texture {tex.name} would be {canvas.width}x{canvas.height}; the limit is {MAX_TEXTURE}. Use size or a lower scale.")
    canvas = bleed(canvas, BLEED)
    png = build / f"{tex.name}_ca.png"
    save_png(canvas, png)
    dest = mod_root / "gui" / "textures" / "tree" / skin.name / f"{tex.name}_ca.paa"
    paa_len, note = to_paa(paa_exe, png, dest, build)
    report.files.append((rel(dest), paa_len))
    report.paa_bytes += paa_len
    print(f"  {rel(dest)}  {paa_len:,} bytes, {note}; {where}")


def check_registered(skin: Skin) -> None:
    """A set the mod does not list in config.cpp loads as blank pictures, with no error at all."""
    config = REPO / MOD / "config.cpp"
    wanted = f"{MOD}/gui/imagesets/{skin.set_name}.imageset"
    if config.is_file() and wanted not in config.read_text(encoding="utf-8", errors="replace"):
        print(f"  WARNING: {wanted} is not in CfgMods > defs > imageSets of {rel(config)}")


# ------------------------------------------------------------------------- command line


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bake source/ui/<set>/sprites.json into imagesets and textures.")
    ap.add_argument("sets", nargs="*", help="set names, folders of source/ui (common, ecolog, ...)")
    ap.add_argument("--all", action="store_true", help="every set that has a sprites.json (not the _examples)")
    ap.add_argument("--chrome", help=f"chrome.exe (default: $CHROME or {DEFAULT_CHROME})")
    ap.add_argument("--node", help="node.exe, 22 or newer (default: $NODE or the one on PATH)")
    ap.add_argument("--dayz-tools", help=f"DayZ Tools folder (default: $DAYZ_TOOLS or {DEFAULT_TOOLS})")
    ap.add_argument("--out", type=Path, help=f"write the mod files here instead of {MOD}/ (required for an _example)")
    ap.add_argument("--build", type=Path, help="intermediate files here instead of build/ui/")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    names = sorted(p.parent.name for p in HERE.glob("*/sprites.json") if not p.parent.name.startswith("_")) if args.all else args.sets
    if not names:
        ap.error("name a set, or pass --all")
    mod_root = (args.out or REPO / MOD).resolve()
    build_root = (args.build or REPO / "build" / "ui").resolve()
    report, failed = Report(), []
    try:
        chrome, node, paa_exe = find_chrome(args.chrome), find_node(args.node), find_image_to_paa(args.dayz_tools)
    except BakeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    for name in names:
        try:
            if name.startswith("_") and not args.out:
                fail(f"{name} is an example: bake it with --out <folder> so it stays out of the mod")
            skin = load_skin(name)
            bake_skin(skin, chrome, node, paa_exe, mod_root, build_root, report)
            if not args.out:
                check_registered(skin)
        except BakeError as exc:
            print(f"error: [{name}] {exc}", file=sys.stderr)
            failed.append(name)
    print(f"{len(names) - len(failed)} of {len(names)} sets baked, {len(report.files)} files, "
          f"{report.paa_bytes / 1048576:.2f} MB of .paa")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
