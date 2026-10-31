# Fonts

*[Українською](README.uk.md)*

The mod's own bitmap fonts: OFL typefaces converted to the DayZ font format -- an FNT3 `.fnt`
with its `.edds` atlas -- by the scripts in this folder. The built files are committed in
`OpenZone_Research/gui/fonts/`; rebuild them after changing anything here.

## What is bundled

| Font file | Typeface (source) | For | `"exact text size"` |
|---|---|---|---|
| `ozl_hand48` | Caveat 400 (`caveat/Caveat[wght].ttf`) | bandit, neutral: all text | up to 32 |
| `ozl_hand72` | Caveat 400 | bandit, neutral: headings | 33 to 48 |
| `ozl_type30` | PT Mono (`ptmono/PTM55FT.ttf`) | duty: typed text; freedom: counters | up to 20 |
| `ozl_narrow28` | PT Sans Narrow (`ptsansnarrow/PT_Sans-Narrow-Web-Regular.ttf`) | duty: form labels | up to 18 |
| `ozl_narrowb36` | PT Sans Narrow Bold (`ptsansnarrow/PT_Sans-Narrow-Web-Bold.ttf`) | duty: headings | up to 24 |
| `ozl_narrowb60` | PT Sans Narrow Bold | duty: the title | 25 to 40 |
| `ozl_oswald40` | Oswald 400 (`oswald/Oswald[wght].ttf`) | sop: text | up to 27 |
| `ozl_oswald64` | Oswald 400 | sop: the timer | 28 to 43 |
| `ozl_oswaldb42` | Oswald 600 | sop: bold labels | up to 28 |
| `ozl_oswaldb70` | Oswald 600 | sop, freedom: big headings (the mockup's Impact) | 29 to 47 |
| `ozl_serif36` | PT Serif (`ptserif/PT_Serif-Web-Regular.ttf`) | freedom: the mockup's Times New Roman | up to 24 |
| `ozl_sans28` | PT Sans (`ptsans/PT_Sans-Web-Regular.ttf`) | freedom: the mockup's Verdana | up to 18 |
| `ozl_sansb28` | PT Sans Bold (`ptsans/PT_Sans-Web-Bold.ttf`) | freedom: bold Verdana | up to 18 |
| `ozl_comic30` | Pangolin (`pangolin/Pangolin-Regular.ttf`) | freedom: the mockup's Comic Sans | up to 20 |
| `ozl_comic52` | Pangolin | freedom: the research button | 21 to 35 |

The last column is the range of `"exact text size"` each file is built for: never magnified on
a 3840x1600 screen (at most cell / 1.48). Smaller sizes than the range still draw, slightly
softer on 1920x1080.

## In a layout

    font "OpenZone_Research/gui/fonts/ozl_hand48"
    "exact text" 1
    "exact text size" 24

- No extension: the engine reads `ozl_hand48.fnt` and finds the atlas as the same path with
  `.edds`.
- **`"exact text size"` is the cell height** in layout units (measured on the stand
  2026-10-31): the whole line, from the top of `Й` to the bottom of `щ`. The number in the file
  name is only the resolution of the atlas; it never sets the size on screen.
- To match a CSS `font-size` E of the mockup, set `"exact text size"` = round(E x r), r being
  the cell height per em of the face:

  | Caveat | PT Mono | PT Sans Narrow | its Bold | Oswald 400 | Oswald 600 | PT Serif | PT Sans | its Bold | Pangolin |
  |---|---|---|---|---|---|---|---|---|---|
  | 1.156 | 1.100 | 1.100 | 1.104 | 1.236 | 1.238 | 1.113 | 1.100 | 1.104 | 1.076 |

  Caveat body text at 21 px in the mockup: round(21 x 1.156) = 24, so `ozl_hand48`.
- Then take the file of the face whose range holds that number.
- The atlas is white; the widget's `color` tints it (dark ink on a paper panel works: measured).
- The Latin I and the Cyrillic І both draw, so the stringtable's Latin-I rule (made for the
  vanilla fonts) does no harm here.
- A character the font lacks should draw as a box: every font carries U+25A1, the glyph the
  engine draws for a missing character. Inferred, not measured -- the vanilla SDF fonts do
  it; no FNT3 font of the stand probe missed a character.
- There are no family files (`.xml`): the engine's choice among the sizes of a family was
  measured unpredictable (a 28-high row took the 22-pixel file), so a layout names the size.

## Character set

Every font carries printable ASCII; the Latin-1 signs U+00A0-U+00BF (without the soft hyphen)
and × ÷; the Cyrillic letters А-я, U+0401 and U+0451, Є є, І і, Ї ї, Ґ ґ;
– — ‘ ’ ‚ “ ” „ • … ‹ › № ₴ ′ ″ ʼ; and the box □. Where a face has them and they fit its
cell, also ← ↑ → ↓ ◆ ◇ ● ○ ★ ☆ ✓ ✔ ✕ ✗ ☮ ♥ ∞ (PT Mono has the arrows, ● ○ ♥ ∞; Caveat
none; the others only ∞).

The cell of a face is set by ASCII, the Cyrillic letters and the punctuation of running text.
A sign taller than that is left out instead of shrinking every glyph: the spacing cedilla ¸
in Oswald and PT Serif, ¹ ² ³ in Pangolin. The PT faces have no ′ ″ and draw ' and " for
them. Every face has every Ukrainian letter.

The build stops (non-zero exit, naming the face, the cell and the code points) when a font
would lack a required character: the English and Ukrainian alphabets, the digits, the Latin I
and ’ « » · — – “ ” №. Only the Cyrillic І and і may be drawn with the Latin letter when a
face lacks them, and the build prints a WARNING when it does. An output name holding a
Reserved Font Name of its face's `OFL.txt` stops the build too.

## Rebuilding

Python 3.10 or newer with Pillow.

    python source/fonts/build_fonts.py              # build all, drop ozl_* files no longer listed
    python source/fonts/build_fonts.py --check      # are the committed files up to date?
    python source/fonts/build_fonts.py --preview D  # also atlas and sample PNGs in folder D

The build is deterministic: the same manifest and TTFs give the same bytes. To add a size or
a face, add an entry to `fonts.json` -- `name` (role + cell height), `face` (path below this
folder), `wght` (the weight of a variable font, else `null`), `cell`, `charset` -- then build
and commit `OpenZone_Research/gui/fonts/`.

`fontbuild.py` on its own converts any TTF/OTF/TTC:

    python source/fonts/fontbuild.py FONT.ttf --name ozl_x --cells 32 --out FOLDER

## How the cell sizes were chosen

The engine scales a cell of N pixels to S x k screen pixels, k being 1.0 on 1920x1080 and
1.48 on 3840x1600. Simulated -- a GPU-style model of that scaling run on the real atlases,
not a shot of the engine: magnifying blurs; shrinking samples the atlas's mip chain,
sharpest at exactly one half. In that simulation a cell of twice the body text size
puts it at one half on 1920x1080 and at 0.74 on 3840x1600, and nothing is magnified on
either. A cell equal to the text size blurs on 3840x1600; one of 1.48 times it softens on
1920x1080. So: the cell is twice the most common text size of the face, plus a second,
larger cell where its biggest text would otherwise be magnified on 3840x1600.

## Names and licence

All the typefaces are under the SIL Open Font License 1.1, not under the mod's licence. Each
TTF has its `OFL.txt` beside it, and the build writes `OpenZone_Research/gui/fonts/OFL.txt`
(every copyright line and the licence), so the licence ships inside the pbo with the fonts.
The repository's `NOTICE` lists them too.

A converted font is a Modified Version under the OFL and must not carry a Reserved Font
Name. ParaType reserves "PT Sans", "PT Serif", "PT Mono" and "ParaType"; Caveat, Oswald and
Pangolin reserve none. So every output is named by its role and cell height, `ozl_<role><N>`,
never after the typeface.

## Files

- `fontbuild.py` -- the converter (TTF to `.fnt` + `.edds`)
- `build_fonts.py` -- builds everything in `fonts.json`
- `fonts.json` -- the list of outputs
- `fontkit/` -- readers and writers of the `.fnt` (FNT3) and `.edds` formats, the LZ4 codec,
  the TrueType tables the converter reads; the format notes are in their docstrings
- `<typeface>/` -- the TTF and its `OFL.txt`, downloaded 2026-10-31 from the `ofl/` folders of
  github.com/google/fonts and checked against GitHub's size and blob hash
