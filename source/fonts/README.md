# Fonts

*[Українською](README.ua.md)*

The mod's own fonts: OFL typefaces converted to the DayZ font formats by the scripts in this
folder -- bitmap fonts (FNT3) for single lines and distance-field fonts (FNT5, `ozl_sdf_*`)
for wrapped text, each a `.fnt` with its `.edds` atlas. The built files are committed in
`OpenZone_Research/gui/fonts/`; rebuild them after changing anything here.

## What is bundled

### Bitmap fonts (FNT3)

| Font file | Typeface (source) | For | `"exact text size"` |
|---|---|---|---|
| `ozl_hand32` | Caveat 400 (`caveat/Caveat[wght].ttf`) | bandit, neutral: labels | up to 21 |
| `ozl_hand48` | Caveat 400 | bandit, neutral: all text | up to 32 |
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

### Distance-field fonts (FNT5), for wrapped text

`MultilineTextWidget` and `RichTextWidget` ignore `"exact text size"` for every bitmap font,
the vanilla ones too (`metronbook22`, `amorserifpro22`): they draw it at the atlas's own pixel
size on every screen -- `ozl_hand48` takes 48 screen pixels a line at 18, 24 or 32, on
1920x1080 and on 3840x1600 alike (measured 2026-10-31). A plain `TextWidget` honours the size.
Distance-field fonts scale in all three, so wrapped text takes one of these:

| Font file | Typeface | Wraps the text of | One line measures |
|---|---|---|---|
| `ozl_sdf_hand32` | Caveat 400 | `ozl_hand32`, `ozl_hand48`, `ozl_hand72` | 1.375 x S |
| `ozl_sdf_type32` | PT Mono | `ozl_type30` | 1.375 x S |
| `ozl_sdf_oswald32` | Oswald 400 | `ozl_oswald40`, `ozl_oswald64` | 1.375 x S |
| `ozl_sdf_oswaldb32` | Oswald 600 | `ozl_oswaldb42`, `ozl_oswaldb70` | 1.375 x S |
| `ozl_sdf_serif32` | PT Serif | `ozl_serif36` | 1.562 x S |
| `ozl_sdf_sans32` | PT Sans | `ozl_sans28` | 1.5 x S |
| `ozl_sdf_comic32` | Pangolin | `ozl_comic30`, `ozl_comic52` | 1.625 x S |

PT Sans Narrow and the bold PT Sans have no distance-field file yet: add one to `fonts.json`
when a skin wraps text in them. The last column is explained below.

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
- Then take the file of the face whose range holds that number -- or, for a
  `MultilineTextWidget` or a `RichTextWidget`, the face's `ozl_sdf_*` file at that same number.
- The atlas is white; the widget's `color` tints it (dark ink on a paper panel works: measured).
- The Latin I and the Cyrillic І both draw, so the stringtable's Latin-I rule (made for the
  vanilla fonts) does no harm here.
- A character the font lacks should draw as a box: every font carries U+25A1, the glyph the
  engine draws for a missing character. Inferred, not measured -- the vanilla SDF fonts do
  it; no FNT3 font of the stand probe missed a character.
- There are no family files (`.xml`): the engine's choice among the sizes of a family was
  measured unpredictable (a 28-high row took the 22-pixel file), so a layout names the size.

### The distance-field fonts

Measured on the stand 2026-10-31, on 1920x1080 and 3840x1600:

- `"exact text size"` means what it means for a bitmap file: the lines are S apart, and
  `ozl_sdf_hand32` at S draws the glyphs of `ozl_hand48` at S (equal widths to the pixel). One
  file serves every size: the field stays sharp magnified.
- One line measures taller than S -- the last column of the table above (the vanilla
  `sdf_MetronBook24`: 1.5 x S). That is the height `GetTextSize` and `"size to text v"` give
  one line; several lines measure (lines - 1) x S plus it. The glyphs sit 2-3 px lower in that
  box than a bitmap font's at the same size (1920x1080). Give a `TextWidget` with such a font
  that height.
- `GetTextSize` gives about one font unit (S / 32 px) a character more width than is drawn --
  the vanilla SDF fonts too -- so leave that slack when sizing a box to the text.
- No kerning: the FNT5 kerning record is not known, so pairs like `AV` or `Wa` are not
  tightened and a line comes out a little wider than in the bitmap font.
- The edges come out softer than a bitmap font's; measured against an ideal rendering of the
  same line, neither kind is closer at every size.
- In a `WrapSpacerWidget` with `"Size To Content V"`, `MultilineTextWidget` children with
  `"size to text v"` get their wrapped height and stack right, but the spacer itself keeps the
  sum of their one-line heights and clips the rest -- with bitmap and distance-field fonts
  alike, and still so 4 s after loading.

## Character set

Every font carries printable ASCII; the Latin-1 signs U+00A0-U+00BF (without the soft hyphen)
and × ÷; the Cyrillic letters А-я, U+0401 and U+0451, Є є, І і, Ї ї, Ґ ґ;
– — ‘ ’ ‚ “ ” „ • … ‹ › № ₴ ′ ″ ʼ; and the box □. Where a face has them and they fit its
cell, also ← ↑ → ↓ ◆ ◇ ● ○ ★ ☆ ✓ ✔ ✕ ✗ ☮ ♥ ∞ (PT Mono has the arrows, ● ○ ♥ ∞; Caveat
none; the others only ∞). A distance-field file carries the characters of its face's bitmap
files.

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

Python 3.10 or newer with Pillow; numpy too for the distance-field files.

    python source/fonts/build_fonts.py              # build all, drop ozl_* files no longer listed
    python source/fonts/build_fonts.py --check      # are the committed files up to date?
    python source/fonts/build_fonts.py --preview D  # also atlas and sample PNGs in folder D

The build is deterministic: the same manifest and TTFs give the same bytes. To add a size or
a face, add an entry to `fonts.json` -- `name` (role + cell height), `kind` (`bitmap` or
`sdf`), `face` (path below this folder), `wght` (the weight of a variable font, else `null`),
`cell`, `charset` -- then build and commit `OpenZone_Research/gui/fonts/`.

`fontbuild.py` on its own converts any TTF/OTF/TTC (`--sdf` for a distance-field font):

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

Measured in the engine 2026-10-31, each Caveat label of 13 to 23 compared with an ideal
rendering of the same line: `ozl_hand32` is no sharper than `ozl_hand48` on 1920x1080 (as
close at 13 and 16, a little further at 20 and 23) and a little closer at 13 and 20 on
3840x1600.

A distance-field atlas stores the distance to the outline (6 atlas pixels each side of the
edge) instead of coverage, so one cell of 32 serves every size.

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

- `fontbuild.py` -- the converter (TTF to `.fnt` + `.edds`, bitmap or distance field)
- `build_fonts.py` -- builds everything in `fonts.json`
- `fonts.json` -- the list of outputs
- `fontkit/` -- readers and writers of the `.fnt` (FNT3, FNT5) and `.edds` formats, the LZ4
  codec, the distance field, the TrueType tables the converter reads; the format notes are in
  their docstrings
- `<typeface>/` -- the TTF and its `OFL.txt`, downloaded 2026-10-31 from the `ofl/` folders of
  github.com/google/fonts and checked against GitHub's size and blob hash
