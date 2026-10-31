# Tree windows ("skins"): the contract

*[Українською](SKINS.uk.md)*

The research tree screen (menu 135) is ONE script, `OZL_TreeMenu`, drawing seven faction windows:
`ecolog`, `clearsky`, `duty`, `freedom`, `sop`, `bandit`, `neutral`. A window is a skin: its layouts,
its pictures, its colours and fonts, and a small script class with data and hooks. The menu finds
widgets by **role** (a widget name) and fills what it finds; a role the layout lacks is simply not
drawn. This file is everything a skin author needs besides the owner's mockup and
[`STRINGS.md`](STRINGS.md). `neutral` («Записник сталкера») is the worked example: read its files
next to this text.

## Files of a skin

A skin task owns exactly these, and edits nothing else:

| File | What |
|---|---|
| `OpenZone_Research/scripts/5_Mission/OpenZone_Research/OZL_TreeSkin_<Name>.c` | the skin class (data + hooks) |
| `ui/OpenZone_Research/ozl_tree_<skin>.json` | the window description; every list row template lives in it |
| `ui/OpenZone_Research/ozl_node_<skin>.json` | the node description |
| `OpenZone_Research/gui/layouts/ozl_tree_<skin>.layout`, `ozl_node_<skin>.layout`, `ozl_<skin>_<row>.layout` | generated from the two descriptions (`python -m dayz_mcp.layoutgen <repo> OpenZone_Research`) |
| `ui/tokens/<skin>.json` | the skin's colours and fonts; every name starts with `<skin>_` |
| `source/ui/<skin>/` | the bake manifest (`sprites.json`) and its CSS |
| `OpenZone_Research/gui/imagesets/ozl_<skin>.imageset`, `ozl_<skin>_ca.paa`, `gui/textures/tree/<skin>/` | baked from the manifest (`python source/ui/bake.py <skin>`) |

Shared, NOT a skin's to edit: `OZL_TreeMenu.c`, `OZL_TreePlan.c`, `OZL_TreeLines.c`, `OZL_TreeSkin.c`
(the base class and the factory), `OZL_Text.c`, `ozl_tree_host.json`, the `ozl_common` set
(`source/ui/common/`), `config.cpp`, `stringtable.csv`, `dayz-mcp.toml`, other skins' files. If a
skin needs a new hook, a new role or a new string, ask the controller: the change goes into the
shared files once, for everybody.

The tokens are layered: `[build] tokens` in `dayz-mcp.toml` lists the core's file first, then the
seven skin files. A later file replaces a same-named entry WHOLE (a font entry restates `face`,
`size` and `fixed`); the `<skin>_` prefix keeps the seven files apart.

## How the window comes up

1. The menu's own layout is the host (`ozl_tree_host`): the whole screen dimmed, "Дерево
   завантажується...", an invisible probe frame.
2. The server answers with the tree and `OZL_TreeView.Skin`, already resolved to one of the seven.
3. `OZL_TreeSkins.Make(id)` makes the skin; the menu creates `ozl_tree_<skin>.layout` INTO the host.
   A window whose layout file is not there yet (`FileExist` sees files inside a pbo too) or
   produces no widgets (its task is not done yet) falls back to `neutral` with one
   `[OpenZone/Research] tree: window '<id>' has no layout yet ...` line; an id the client does not
   know is an ERROR line and `neutral` too (defence only).
4. Roles are looked up once (`menu.Role(name)`, cached), `skin.OnShow(menu)` runs, then every
   answer paints: header, branches, pool, tree, registry, card, `skin.OnPaint(menu)`.

The window is re-created only when the skin changes; the selected node and branch survive a
refresh.

## Units — measured, do not guess

Everything in this contract is in **layout units of the 1600x900 window** (the mockup's stage).
On a screen H pixels high one unit is `H / 1080` pixels. Measured on the stand 2026-10-31 (3840x1600,
1.48 px per unit; and 1920x1080):

- `SetPos` / `SetSize` from script take **screen pixels** (`SetPos(100)` moved a widget 100 px at
  1600 rows just as at 1080: 67.5 units there, 100 here) — on layout widgets and on widgets made
  by `CreateWidgets` alike.
  `GetScreenPos` / `GetScreenSize` return pixels. So the menu converts: `menu.PlaceUnits(w, x, y)`,
  `menu.SizeUnits(w, w, h)`, `menu.UnitsOf(w, out w, out h)` — use them, never raw numbers.
- Scroll positions (`HScrollToPos`, `GetVScrollPos`) are pixels.
- `CanvasWidget.DrawLine` draws in pixels from the canvas's top-left; a canvas 3230 x 1659 px (a
  2180 x 1120-unit tree) draws to its far edge.
- A `FrameWidget` clips its children to its own box unless the layout says `clipchildren 0`. The
  menu clears it on the node cell, on NodeHit's containers and on the label rows, so a mark may
  stick out of a cell.

## The tree: plan and geometry

`OZL_TreePlan` lays the selected branch out from the skin's geometry (spec §3; the mockup's `SKINS`):

| Field | Meaning |
|---|---|
| `Dir` | `"down"`, `"up"` or `"right"`: where the tree grows |
| `NodeW`, `NodeH` | the node SHAPE's size (where the lines attach) |
| `Keep` | room kept under a label across the lane; 0 = half the node |
| `Row`, `Col` | step between tiers along, between nodes across |
| `Top`, `Side`, `Shift` | room before the first tier; margins across; shift of the group across |
| `AnchorX`, `AnchorY` | the centre of the shape INSIDE the node cell |

Tiers of the visible nodes go along, ascending; within a tier nodes are ordered by the mean
position of their already placed parents (ties: `Index`). A node's point is `(u, v)` with
`u = Top + Row x (tier index + 1/2)`; content size = `max(view, Side x 2 + Col x widest tier)`
across, `max(view, Top + tiers x Row + 40)` along, plus room for the fog when the branch has hidden
nodes. `(u, v)` becomes `(x, y)`: down `(v, u)`, up `(v, H - u)`, right `(u, v)`. The menu places
each cell at `(x - AnchorX, y - AnchorY)` in `TreeNodes` and sizes `TreeContent` to the plan.

"Home" when the window opens or the branch changes: down — top, up — bottom, right — left edge;
across — centred. Press-and-drag on the tree scrolls it (a move over 4 units turns the release
into a drag, not a click); the wheel scrolls natively.

## Roles of the window (`ozl_tree_<skin>.layout`, root `TreeWindow`)

The root may be the whole screen (neutral: the desk, tiled, and a centred 1600x900 `TreeStage`).

### Tree

| Role | Type | What the menu does |
|---|---|---|
| `TreeScroll` | ScrollWidget (`clipchildren 1`, `"Scrollbar V"`/`"Scrollbar H"` as wanted) | its size is the view; home, drag; one child: `TreeContent` |
| `TreeContent` | FrameWidget, exact size | resized to the plan; children below are `size fill` (proportional) so they follow |
| `TreeBg` | ImageWidget, fill | the admin's `TreeBackground` is loaded into it and shown; without one it stays as the layout made it |
| `TreeTiers` | frame, fill | tier labels: rows `tier_label` (child `TierText`), the row's corner on the label's point (`x = 22` across, the tier's centre along) |
| `TreeLines` | CanvasWidget, fill, `ignorepointer 1` | the paper grid (`GridStep`) and every link (`OZL_TreeLines`), redrawn on selection, hover, data, layout |
| `TreeFogEdge` | image, optional | the 80-unit fade at the start of the fog; the menu places and sizes it along the skin's direction |
| `TreeFog` | panel or image | the rest of the fog, after the fade |
| `TreeNodes` | frame, fill | node cells; the `АБО` labels (rows `or_label`, child `OrText`) with the row's corner on the diamond |
| `TreeTip` | frame, hidden | above the hovered node, as wide as `TreeTipText` + 2 x `TipPadX`; children `TreeTipEdge` (fill), `TreeTipBg` (inset 1, resized), `TreeTipText` (self-sized, `w: auto`, at `TipPadX`) |
| `TreeLegend` | anything | static: the six legend items are in the layout |

### Header

`BranchName` (text), `BranchSub` (text: `<faction> · досліджено N з M`), `DevName` (static, a key in
the layout), `BtnClose` (button).

### Lists — row templates `ozl_<skin>_<row>.layout`

A list container is any widget the menu can create rows into (a `stack` = WrapSpacer, or a `list`'s
stack). Row templates are declared as `rows` of some `list` in the window description; rows that
live outside lists (tier and OR labels, price chips) go on a hidden `TreeTemplates` list.

| Container | Row | Children the menu fills |
|---|---|---|
| `BranchList` | `branch_row` | `RowHit` (button, renamed `branch:<id>`; without it the row root is renamed), `RowName`, `RowCount` (`done / total`), `RowPick` (shown on the open branch), `RowBar`/`RowBarFill` (done fraction) |
| `PoolList` | `pool_row` | via `PaintPoolRow`: `PoolChip` (line colour), `PoolName`, `PoolValue`, `PoolSeg0`..`PoolSeg9` (on = have / largest single-node cost), anything the skin adds; `PoolEmpty` (optional) shows when there is no line |
| `CardCostList`, `CardItemList` | `cost_row` | via `PaintCostRow`: `CostChip`, `CostName`, `CostValue` (`have / need`, or `need` when paid or unknown), `CostBar`/`CostBarFill` |
| `CardOpensList` | `opens_chip` | lined up left to right with wrapping; the first text child (`ChipText`) sets the width; `ChipHit` (renamed `open:<id>`) and `ChipLine` are stretched to it; a hidden node's chip has no `ChipHit` |
| `Registry` | `registry_row` | `RegNum` (`Index + 1`, two digits), `RegName`, `RegTier`, `RegState`, `RegPick`; root renamed `reg:<id>`; a hidden node's row reads `— невідомо —` |
| `TreeTiers` | `tier_label` | `TierText` |
| `TreeNodes` | `or_label` | `OrText` |
| `NodePrice` (in the node) | `price_chip` | `PriceChip` (line colour), `PriceText` (amount); the tail `+N предм.` is one more chip with `PriceChip` hidden |

### Card

`CardEmpty` (shown when nothing is selected) / `CardBody`; `CardName`, `CardMeta`
(`тир N · після: … / після всіх: … / після будь-якого з: …`, hidden parents = `невідомо`),
`CardStatus` (word and colour from the skin), `CardDesc`; section heads `CardDescHead`,
`CardCostHead`, `CardItemsHead`, `CardTimeHead`, `CardOpensHead` (text from `SectionText`;
`CardItemsHead`/`CardItemList` hide when the node costs no material, `CardOpensHead`/`CardOpensList`
when it opens nothing); `CardTime`, `CardTimer` (the bare clock, shown while researching);
`CardSegs` + `CardSeg0`..`CardSeg19` or `CardBar`/`CardBarFill`; `BtnResearch` (+ `BtnResearchText`,
`BtnResearchHover` shown under the mouse while enabled), always visible; `CardWhy` (the reason a
button is disabled, a refusal of the server, "Запит надіслано..."); `CardStamp` + `CardStampImg`
(`StampOf`); `CardScroll` (scrolled to the top on every selection) and `CardFlow` (the stack,
updated after the card changes) if the card scrolls.

**Wrapped text.** `CardName`, `CardMeta`, `CardDesc` and the node's `NodeName` may each be ONE
TextWidget, or a container holding labels `<Name>0`, `<Name>1`, … — then the menu word-wraps the
text into those labels (measured with the first one), hides the unused ones and gives the last one
the rest. Use the container form with the mod's own fonts: a `MultilineTextWidget` or
`RichTextWidget` ignores `"exact text size"` with them and draws at the atlas cell (48 or 72 units),
measured 2026-10-31. Labels in a `stack` take no room when hidden.

## Roles of the node (`ozl_node_<skin>.layout`, root `NodeCell`)

`NodeCell` is the cell (renamed `cell:<id>`); give it room for everything that sticks out.

| Role | What |
|---|---|
| `NodeHit` | THE pointer target: a button with `style Empty`, renamed `node:<id>`, under the shape |
| `NodeShape` | ImageWidget; the skin's `Shapes` are loaded into slots 0..7, `ShapeOf` picks one, `ShapeColorOf` tints |
| `NodeRing`, `NodeSel` | the available ring (`RingShown`) and the selected ring |
| `NodeIcon` | the node's own icon from the tree config, tinted by `IconColorOf` |
| `NodeName` | text, or a container of `NodeName0`, `NodeName1` (wrapped) |
| `NodePrice` | a container the price chips are lined up in (clips them) |
| `NodePriceText` | plain text instead of chips: `Досліджено`, `Лишилось m:ss`, or the price when there is no chip row |
| `NodeBar`/`NodeBarFill` | shown while researching; filled to the done fraction |
| `NodeMark`, `NodeMarkText` | `Marks` slot from `MarkOf`, word from `MarkTextOf`, tinted by `MarkColorOf` |
| `NodeNum` | `Index + 1`, two digits |

### The pointer rule (stand, 2026-10-31)

A `FrameWidget` without `ignorepointer 1` takes the mouse. The first neutral node had its name and
price in frames: hover and click worked only on the rim of the card, where `NodeHit` was not
covered. So:

1. In the node, **every widget except `NodeHit` has `ignorepointer 1`**. In a description,
   containers are `panel` with `"color": "$none"` (the generator gives panels `ignorepointer 1` and
   frames not); the one exception is a container that holds `NodeHit` (it lies under it and only
   sees the cell's margins). Check the GENERATED `.layout`, not only the description.
2. Every clickable thing is a ButtonWidget with `style Empty` (a `raw` node with
   `"props": {"style": "Empty", "text": ""}`): a style-less button paints a light box under the
   mouse.
3. The menu enforces 1 anyway: after creating a cell it sets `IGNOREPOINTER` on everything but
   `NodeHit` and its containers, and it resolves a node from ANY widget it is told about by walking
   up to `node:<id>` / `cell:<id>`. Label rows (`tier_label`, `or_label`, `price_chip`) and
   `TreeTip` ignore the pointer entirely.

## The skin class (`OZL_TreeSkin`)

Data (set in the constructor; `Named("<id>")` fills the layout names): `Id`, `WindowLayout`,
`NodeLayout`, `RowPrefix`; the geometry above; colours as ARGB — `Txt`, `Dim`, `Acc`, `Ok`, `Bad`,
`LineDim`, `LineLit` (= Txt), `LineHl` (= Acc), `Lcd` (fill of the `АБО` diamond), `FogColor`;
`LineStyle` (`"plain"` / `"sketch"`), `LineW` (2), `LineWHl` (2.5), `DashOn`/`DashOff` (6/5);
`GridStep`, `GridColor`, `GridX`, `GridY`, `GridW` (the paper grid, drawn on the canvas; skipped
under the admin's background); `Shapes`, `ShapeHover` (slot under the mouse, -1 none), `ShapeColors`
(status -> tint); `Marks`; `SegOn`, `SegOff` (0 = Acc / LineDim); `TipPadX`.

Keep these ARGB numbers equal to the skin's `ui/tokens/<skin>.json` (the engine cannot read JSON at
compile time).

Hooks — each works without an override:

| Hook | Default |
|---|---|
| `int ShapeOf(status, selected)` | slot 0 if `Shapes` has any, else -1 (keep the layout's image) |
| `int ShapeColorOf(status)` | `ShapeColors[status]`, else white |
| `bool RingShown(status, selected)` | available and not selected |
| `int NameColorOf(status)` / `PriceColorOf` / `IconColorOf` / `StatusColorOf` | the mockup's: locked Dim, short Bad, available/researching Acc, completed Ok (name: Txt, locked Dim) |
| `int MarkOf(status)` / `string MarkTextOf(status)` / `int MarkColorOf(status)` | lock / check / dot = `Marks` slots 0/1/2 for locked / completed / researching; no text |
| `string StatusText(status)` | the status key's word (`StatusKey`) |
| `string SectionText(key)` | the key's word (paper adds `:`, clearsky prepends `// `, upper-case skins `OZL_Text.Upper`) |
| `string NodeNameText(name)` | the name (also the card's name) |
| `string TierText(tier)` | `I`, `II`…; `right` trees `тир I` |
| `void PaintNode(menu, cell, node, status, selected)` | shape, rings, icon, name, mark, number (price and bar are the menu's) |
| `void PaintPoolRow(menu, row, line, have, need, color)` | name, value, chip, segments |
| `void PaintCostRow(menu, row, label, text, verdict)` | name, value coloured by verdict (1 ok / -1 bad / 0 unknown), bar colour |
| `void PaintButton(menu, btn, enabled)` | `BtnResearchText` Acc or Dim |
| `string StampOf(status)` | none |
| `float DrawSegment(canvas, x1, y1, x2, y2, width, color, dashed, phase)` | a straight piece, dashed 6/5 with the phase carried along the polyline |
| `void DrawStroke(canvas, xs, ys, width, color, dashed, seed)` | the polyline; `LineStyle "sketch"` = the mockup's `sketch()` (short strokes with jitter and bend, a faint second stroke), seeded by the edge id so nothing trembles |
| `void DrawOrKnot` / `DrawAllKnot` | the `АБО` diamond (filled with Lcd, outlined) / the 10-unit square — a thick `DrawLine` is a filled rectangle |
| `void OnShow(menu)` | — (static texts, start animations) |
| `void OnUpdate(menu, dt)` | — (every frame: marquee, blinking, flicker) |
| `void OnPaint(menu)` | — (after every full paint) |
| `void OnSelect(menu, node, status, canResearch)` | — (node null = nothing selected) |
| `bool OnClick(menu, w)` | false (clicks the menu did not recognise: helper buttons...) |

Helpers on the menu for hooks: `Role(name)`, `PlaceUnits`, `SizeUnits`, `UnitsOf`, `Px()`,
`PutText(w, text, color)` (a text role, wrapped if it is a container), `FitLater(text, target, pad,
mode)` (next frame: `target` as wide as the text — underlines, strikes; mode 0 keep x, 1 right-anchored,
2 centred in the parent), `BarLater(track, fill, fraction)`, `FlowLater(box, gap, pad, wrap)`,
`PointName(line)`, `PointColor(line)`, `PoolOf(line)`, `ItemLabel(item)`, `LeftOf(node)`,
`View()`, `CurrentBranch()`, `BranchCount()`, `SelectedId()`, `HoveredId()`, `NodeIdAt(widget)`.
Strings: `OZL_Text.Words(key)`, `OZL_Text.Upper(text)` (Latin and Ukrainian Cyrillic; `і` becomes
the Latin `I`), `Duration`, `Clock`, `Roman`, `Two`.

## Pictures

Everything the mockup draws with CSS is a picture, baked: write `source/ui/<skin>/sprites.json`
(see [`README.md`](README.md)), run `python source/ui/bake.py <skin>`, look at
`build/ui/<skin>/preview.png`, commit the manifest with the `.imageset` and `.paa`. A sprite is
`set:ozl_<skin> image:<name>`; draw what is tinted in white and tint it in the layout or with
`SetColor`. Its imageset size includes its `pad`: show it in a widget of `w + 2 pad` by `h + 2 pad`,
`pad` up and left. Big pieces go under `textures` (`gui/textures/tree/<skin>/<name>_ca.paa`); a
texture without `"stretch mode"` tiles at its own pixel size (neutral's desk and dash). The shared
set `ozl_common` holds white `mark_lock`, `mark_check`, `mark_dot`, `mark_wait`, `mark_query`
(24x24), `chip`, `and_square` (10x10), `or_diamond` (16x16). Text goes into a picture only when it
is rotated or styled; then two sprites `_uk`/`_en` and a `*_IMG` key (STRINGS.md). Budget: up to
2048x2048 per skin. Neutral: one 1024x512 atlas and three small textures (0.08 MB).

## Fonts

The mod's bitmap fonts are in `OpenZone_Research/gui/fonts/` (see `source/fonts/README.md`): in a
layout `font "OpenZone_Research/gui/fonts/ozl_hand48"` with `"exact text size"` = the CELL height in
units = round(CSS px x the face's cell ratio). Put them in the skin's tokens as fonts. They work in
TextWidget labels; for wrapped text use line labels (above).

## Checking a skin

`python -m dayz_mcp.layoutgen <repo> OpenZone_Research`, then MCP `mod_lint`, `mod_build`,
`client_compile_check`, `server_start`, `log_verdict`; on the stand:
`world_exec verb=oz_research args={"op":"demo","owner":"<faction>"}` and
`{"op":"treeui","owner":"<faction>","as":"post"}` (as=post with `Settings.ResearchPost` set lets the
player spend). Look at it at 1920x1080 and 3840x1600, in English and Ukrainian. Move the real mouse
over the middle of a node (`ui_click via=cursor` on its name): the tooltip and the highlighted links
must appear and the click must select it.
