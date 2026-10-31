# UI bake: from the mockup's CSS to DayZ textures

*[Українською](README.ua.md)*

The research tree window is drawn from the owner's HTML mockup, and everything the mockup draws
with CSS (frames, paper, scraps, hexagons, buttons, stamps, a picture-tube bezel) has to be a
texture in the game. Nobody redraws those by hand. `bake.py` takes the CSS and the markup of each
picture, has headless Chrome draw it on a transparent ground, cuts the pictures out, packs them
into an atlas, writes the `.imageset` and turns the atlas into a `_ca.paa`.

    sprites.json  ->  Chrome draws the page  ->  Pillow cuts, packs  ->  .imageset + _ca.paa

## Sets

One folder per set, each with a `sprites.json`:

| Folder | Imageset | What it holds |
|---|---|---|
| `common` | `ozl_common` | the shared set: white, tintable shapes that any skin may use -- the status marks (`mark_lock`, `mark_check`, `mark_dot`, `mark_wait`, `mark_query`), the line chip, the link knots (`and_square`, `or_diamond`) |
| `ecolog` `clearsky` `duty` `freedom` `sop` `bandit` `neutral` | `ozl_<skin>` | the pictures of one faction window. Until a skin is drawn its manifest holds one 8x8 transparent sprite, `blank`, so the imageset that `config.cpp` registers exists |
| `_demo` | -- | an example of every manifest feature, baked only with `--out` (see below) |

All eight imagesets are registered in `OpenZone_Research/config.cpp` (`CfgMods > defs > imageSets`).
A set that is not registered loads as blank pictures with no error, so `bake.py` warns when the
set it baked is missing there.

## Requirements

- Python 3.10 or newer with Pillow 9.1 or newer, nothing else
- Node.js 22 or newer: `shoot.mjs` drives Chrome through its built-in `WebSocket`
- Google Chrome (`C:\Program Files\Google\Chrome\Application\chrome.exe`)
- DayZ Tools: `Bin\ImageToPAA\ImageToPAA.exe`
- the fonts a picture uses: Windows system fonts by name (Arial, Impact, Consolas, Courier New,
  Segoe Print, Ink Free, Bahnschrift, ...), or a font file named in `@font-face`. There is no
  network during the bake, so a web-font `<link>` such as Google Fonts does not load.

Other paths: `--chrome`, `--node`, `--dayz-tools`, or the environment variables `CHROME`, `NODE`,
`DAYZ_TOOLS`.

## Running

    python source/ui/bake.py common           # one set
    python source/ui/bake.py duty freedom     # several
    python source/ui/bake.py --all            # every set with a sprites.json except the _examples

The same input gives the same bytes: Chrome rasterises in software, animations are off, the packer
breaks ties by position, and a file is rewritten only if its content changed (an `.imageset` that
differs only by CRLF line endings, as a Windows checkout has it, counts as unchanged). A second run
changes nothing, and `git status` stays clean. That holds for one Chrome build: a Chrome update can
move some antialiasing by a few alpha levels, so after updating it a bake may show changed `.paa`
files. Look at them, and commit them as a change of their own.

What a run writes:

| File | What |
|---|---|
| `OpenZone_Research/gui/imagesets/ozl_<set>.imageset` | the atlas description, `Name "ozl_<set>"` |
| `OpenZone_Research/gui/imagesets/ozl_<set>_ca.paa` | the atlas, DXT5 |
| `OpenZone_Research/gui/textures/tree/<set>/<name>_ca.paa` | one standalone texture per entry of `textures` |
| `build/ui/<set>/` | git-ignored: the generated pages (`sheet.html`), what Chrome drew (`sheet.png`), the atlas PNG, the read-back of every `.paa`, and `preview.png` |

Commit the manifest together with the `.imageset` and `.paa` it produced.

## Looking at the result

Open `build/ui/<set>/preview.png`: the atlas over a checkerboard, every sprite outlined and named.
`sheet.png` is the raw page as Chrome drew it. The log of a run reports per page (the sprite sheet
and each texture), for the atlas and for each texture, not per sprite: the pixel size and the alpha
range (`alpha 0..255` with many levels means real partial transparency); and for every `.paa` that
`ImageToPAA` read it back as DXT5 with the same size and alpha range. To check one sprite, find it
in `preview.png`.

## The manifest

    {
      "scale": 1.5,
      "atlas_max": 2048,
      "gutter": 4,
      "css": ["duty.css", ":root { --ink: #1e1c19; }"],
      "body": { "data-f": "duty" },
      "sprites": [ { "name": "tag", "w": 48, "h": 20, "html": "<div class='tag'>OK</div>" } ],
      "textures": [ { "name": "sheet", "w": 1000, "h": 600, "size": [2048, 1024], "html": "..." } ]
    }

Every size is in layout units, the unit of the window layouts (the 1600x900 window of the mockup).

| Key | Default | Meaning |
|---|---|---|
| `scale` | `1.5` | device pixels per unit. The owner's 1600-line screen is 1.48, so 1.5 is one texel per pixel. Keep it the same for a whole set |
| `atlas_max` | `2048` | the largest side of the atlas, a power of two. The atlas is the smallest power-of-two rectangle that holds every sprite; it may be a rectangle, not a square |
| `gutter` | `4` | pixels around each sprite, see "The atlas" |
| `css` | none | a string or a list. An entry with a `{`, a `;` or a line break is CSS text; any other entry is the name of a `.css` file in the set's folder. It is put on the page as it is, so the mockup's CSS can be lifted without rewriting selectors. `url(...)` is relative to the set's folder, not to the file |
| `body` | none | attributes of `<body>`. The mockup scopes its rules as `body[data-f="duty"] ...`; `"body": {"data-f": "duty"}` makes them match |
| `comment` | -- | ignored, a note for people (JSON has no comments) |
| `sprites` | required | the atlas pictures, at least one |
| `textures` | none | pictures that get a texture of their own |

A sprite:

| Key | Meaning |
|---|---|
| `name` | letters, digits, `_`, starting with a letter. It becomes the image name in the imageset |
| `w`, `h` | the design box in units |
| `html` | the markup inside the box: a string, or a list of lines that is joined with line breaks (easier to write in JSON; single quotes inside SVG save the escaping) |
| `html_ua` and `html_en` | instead of `html`: two pictures, `name_ua` and `name_en`, see "Two languages". Both are required |
| `css` | declarations and nested rules scoped to this sprite's box: `"background: #fff; .core { inset: 6px; }"`. For `@font-face` or `@keyframes` use the set's `css` |
| `pad` | units kept around the box for what spills out of it (a glow, a shadow, a rotated corner) |

A texture has the same keys, minus `pad`, plus `size`.

### What the page looks like

Each picture is the content of a box of `w` x `h` units (`position: absolute`, so children can be
positioned inside it), sitting `pad` units inside a clip box. **Anything outside the clip box is cut
off.** Direct `svg` and `img` children are `display: block` (an inline one would sit on the text
baseline and drop out of a small box). The page background is transparent, and after the set's CSS
the bake adds `html, body { background: transparent !important }` and turns animations and
transitions off, so a lifted `body { background: ... }` or a blinking mark cannot spoil it. If
something still paints a background, the run stops with "the empty corner of the page is not
transparent".

All the sprites of a set are drawn on one page (`build/ui/<set>/sheet.html`), so an `id` in one
sprite's markup is an id of the whole page: two sprites that both define `<linearGradient id="g">`
would silently share the first one. **Prefix every SVG id with the name of its sprite**
(`stamp_uk_noise`, not `noise`), and give the `_ua` and `_en` variants of one sprite ids of their
own as well: they are two sprites on the same page. The bake stops when two pictures use the same
id. Reserved: `oz0`, `oz1`, ... (`oz<N>`, the box of each picture), `oz-sheet` and `oz-canary`, and
the classes `oz-c` and `oz-s`.

A sprite's picture is `ceil(w * scale) + 2 * ceil(pad * scale)` pixels wide (the same for the
height): 24 units is 36 px at 1.5. That is the `Size` in the imageset. With a `pad`, show the sprite
in a widget of `w + 2 * pad` by `h + 2 * pad` units, placed `pad` units up and left of where the
design box should be.

### The atlas

- Pictures are packed with MaxRects (best short side fit) into the smallest power-of-two
  rectangle up to `atlas_max`; `RefSize` is the texture size and `Pos`/`Size` are texture pixels,
  without the gutter. `Flags 0` and `mpix 0`, as in the other OpenZone imagesets.
- Around each sprite is a gutter of `gutter` pixels that repeats the sprite's own edge pixels, so
  filtering at a different scale cannot pull in a neighbour.
- Pixels with alpha 0 that lie within 4 px of a visible pixel get that pixel's colour (alpha is
  left alone). Chrome writes transparent pixels as black, and filtering would mix that black into
  the edge of a white glyph as a dark fringe.
- Sprites are drawn at whole-pixel positions (for 1.5 that is every 2 CSS px, 3 device px), so a
  box edge is as sharp wherever the sprite lands. Chrome's curve rasteriser is not exactly the same
  after a shift: a circle can differ by a few alpha levels on a few edge pixels when the sheet
  around it changes. For one manifest the result is still the same on every run. A `scale` with
  no whole-pixel step (1.37, say) works but prints a note.
- If the sprites do not fit `atlas_max`, the run says so: draw the large ones as textures, or lower
  the `scale`. Budget from the design: up to 2048 x 2048 per skin atlas and about 40 MB of `.paa`
  in all; the last line of a run shows the total.

### Two languages

Text does not go into pictures except stylised text (a stamp, a rotated heading, a struck-out
word). For those give `html_ua` and `html_en`; the sprites are `<name>_ua` and `<name>_en`, and
the stringtable decides which one is shown: the value of a `*_IMG` key is
`set:ozl_<skin> image:<name>_ua` in the Ukrainian cells (`original` and every column that repeats
it) and `set:ozl_<skin> image:<name>_en` in the English cell. Both are drawn with the same box, so
make it wide enough for the longer text, and they share a page, so their SVG ids must differ.

### Standalone textures

Window chrome that is too big to share an atlas goes under `textures`. Each is drawn alone and
written to `gui/textures/tree/<set>/<name>_ca.paa`, a power-of-two texture (up to 4096), which a
layout uses as a plain image:

    image0 "OpenZone_Research/gui/textures/tree/duty/sheet_ca.paa"
    mode blend
    "src alpha" 1
    "stretch mode" stretch_w_h

- **With `size`** (`"size": [2048, 1024]`, each side a power of two): the picture is stretched over
  the whole canvas, so the layout shows the whole texture over a widget of `w` x `h` units and
  nothing is wasted. A 1600 x 900 window does not fit 2048 px at 1.5, and 2048 x 1024 is the
  usual answer; the picture is drawn at least at `scale`, and larger if `size` needs it, then
  shrunk, so it stays sharp.
- **Without `size`**: the picture is `ceil(w * scale)` x `ceil(h * scale)` pixels, put in the
  **top-left** corner of the next power-of-two canvas; the rest is transparent. A widget with
  `stretch_w_h` shows the whole canvas, transparent rest included; without `stretch_w_h` it shows
  the top-left crop of the texture at native size (dayz-modding skill, gui-layouts, section 12), so
  what is visible follows the widget's size in pixels rather than the picture. Either way the
  widget has to be sized to suit; prefer `size`. The log of a run states where the content ends.

## Adding a skin's pictures

1. In `source/ui/<skin>/sprites.json` replace the `blank` placeholder with the skin's sprites (a
   skin that has real sprites does not need `blank`).
2. Lift the mockup's CSS for the skin into `source/ui/<skin>/<skin>.css`, name it in `css`, and set
   `body` if the rules are scoped by `body[...]`. Write each picture's markup in `html`, with every
   SVG id prefixed by the sprite's name.
3. `python source/ui/bake.py <skin>`, then look at `build/ui/<skin>/preview.png`.
4. Commit the manifest with the new `.imageset` and `.paa`.
5. Use a sprite in a layout (or `LoadImageFile`) as `set:ozl_<skin> image:<name>`:

        image0 "set:ozl_common image:mark_lock"
        mode blend
        "src alpha" 1
        color 0.31 0.71 0.91 1

   The shapes in `common` are white, so the widget `color` (or `SetColor` from script) is the
   colour they show in. Keep `mode blend`; the engine does not log a missing one (dayz-modding
   skill, gui-layouts, section 12).

`source/ui/_demo/` shows every feature: a CSS file next to inline CSS, `body`, a scoped `css` with a
`pad`, `html_ua` with `html_en`, and a texture with and without `size`. A folder whose name starts
with an underscore is an example, so `--all` skips it and it needs `--out` to keep it out of the mod:

    python source/ui/bake.py _demo --out build/ui/demo-out

## Tests

    python -m unittest discover -s source/ui -v

The tests cover the parts that need neither Chrome nor DayZ Tools: the colour bleed (it must not
wrap colour round the edge of a sprite), the gutter, the packer, the manifest rules and the ids.

## How the drawing is done

`bake.py` writes one HTML page per skin (all sprites at known rectangles) and one per texture, and
`shoot.mjs` has headless Chrome draw them over the DevTools protocol:
`Emulation.setDefaultBackgroundColorOverride` with alpha 0 for the ground,
`Emulation.setDeviceMetricsOverride` for the scale, `Page.captureScreenshot` with a clip. Measured,
a half-transparent `rgba(255, 0, 0, .5)` box comes out as `255, 0, 0, 128` and the empty ground as
`0, 0, 0, 0`.

The simpler `chrome --headless=new --screenshot --default-background-color=00000000` also gives a
transparent PNG, but it takes the first compositor frame, which is only partly rastered: with the
offline guard below a 2400 x 162 px page came out as its top 14 rows, every time. `shoot.mjs`
waits for fonts, images and two animation frames, and photographs again until two shots in a row
are identical. `bake.py` then checks that the last pixel of the page, a canary of colour
`1, 2, 3`, is there; a page that was only partly drawn stops the run instead of producing a
picture with a hole in it.

Chrome runs with `--disable-gpu`, `--disable-lcd-text`, `--font-render-hinting=none` and
`--force-color-profile=srgb`, which makes the pixels the same on every machine, and with
`--host-resolver-rules="MAP * ~NOTFOUND"`, so no web font or image can come from the network.

`ImageToPAA` takes the format from the name of the source: `_ca` is DXT5 with alpha, `_co` drops
the alpha. `bake.py` converts a PNG named `..._ca.png` in `build/ui/<set>/`, checks the exit code,
that the file exists, is not empty and starts with `05 ff` (DXT5), then has the tool read the
`.paa` back into a PNG and compares size and alpha range with what went in. Only then is the file
copied into the mod, and only if its bytes differ from what is there.
