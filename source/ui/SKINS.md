# Tree windows ("skins"): the contract

*[Українською](SKINS.ua.md)*

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
   завантажується...", an invisible probe frame. A refusal of the server or an unreadable answer
   before the first window takes the place of that line.
2. The server answers with the tree and `OZL_TreeView.Skin`, already resolved to one of the seven.
3. `OZL_TreeSkins.Make(id)` makes the skin; the menu creates `ozl_tree_<skin>.layout` INTO the host.
   A window whose layout file is not there yet or produces no widgets (its task is not done yet)
   falls back to `neutral` with one `[OpenZone/Research] tree: window '<id>' has no layout yet ...`
   line; an id the client does not know is an ERROR line and `neutral` too (defence only). The
   menu tests the file with `FileExist`, which sees files packed in a pbo — inferred from vanilla
   (its particle list checks every `.ptc` that way and stays silent), not probed head-on; so
   `neutral`'s own layout is always tried without the test.
4. Roles are looked up once (`menu.Role(name)`, cached), `skin.OnShow(menu)` runs, then every
   answer paints: header, branches, pool, tree, registry, card, `skin.OnPaint(menu)`.

While the menu is open the game HUD (status icons, stamina, the hotbar) is hidden the vanilla way
— `ShowHudUI(false)` + `ShowQuickbarUI(false)`, as the map, the note and the radial quickbar do —
and restored in `OnHide`, which the engine calls on every close (ESC, the button, death, another
menu on top). A skin does nothing for it. (Why context flags and not `Hud.Show(false)`: that call
hides the whole `HudPanel` too, but any later `Hud.Show(true)` brings the panel back over the tree —
VPP's `UnlockPlayerControl`, OpenZone's link and PDA menus on their close and the MCP preview's
unload all show it again — while the flags hide the elements themselves and survive that. Which
caller put the HUD back in the sop snapshot of 13:47 was not measured.)

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
- **Every widget the menu places or sizes needs an exact position and size** (`hexactpos`,
  `vexactpos`, `hexactsize`, `vexactsize` 1; the generator writes them for a node with `at` and
  `size`): the node cell, tier and `АБО` labels, `TreeContent`, `TreeFog`/`TreeFogEdge`, `TreeTip`
  and `TreeTipBg`, every bar fill, every `FitLater` target and `FlowLater` item. A proportional
  (`fill`) widget takes the numbers as fractions of its parent. Only children that should follow
  their parent are `fill`. A wrapping `FlowLater` box (`CardOpensList`) is the one exception: the
  menu sets only its height (exact) and leaves its width as it is, proportional included (its
  fraction is read once per widget and kept; a proportional child of a ScrollWidget is measured
  against the scroll's width minus the 10-unit bar, which is what the engine gives it).

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
into a drag, not a click); a press in `TreeScroll`'s scrollbar strips (its bottom and right
10 units, each only while its bar is drawn — `TreeContent` wider, or taller, than the view) moves
the bar natively and does not drag the content — the menu tells them by position, because on an
empty part of the tree the engine reports `TreeScroll` itself; the wheel scrolls natively.

### Scrollbars: colour yes, width no

A ScrollWidget draws the engine's plain white bars unless styled. **`color` + `style blank` on the
ScrollWidget draws the thumb in that colour and the track in half of it**, both bars (measured by
the sop skin on the stand, 2026-10-31: thumb (68,64,47), track (34,32,24)) — the vanilla inventory
scrollers do exactly this (`color 0.502 0.502 0.502 0.8`, `style blank`). Nothing else about the bar
can be set: the vanilla ScrollWidget styles (`blank`, `dashed`, `Colorable` in `dayzwidgets.styles`)
define only the widget's frame, no scrollbar parts, and the vanilla layouts use no scroll keys but
`"Scrollbar V"`, `"Scrollbar H"` and `"Scrollbar V Left"`. So a skin themes the colour, per
ScrollWidget, in its layout:

- in a description, a `raw` ScrollWidgetClass takes `"color": "$<token>"` and
  `"props": {"style": "blank", ...}` (neutral's and sop's `TreeScroll`);
- a `list` does NOT carry them (the generator ignores `color` there and has no `props`): a card
  that wants a styled bar is a `raw` ScrollWidget with a `stack` child (sop's `CardScroll` +
  `CardFlow`), its row templates on another list;
- leaving a bar out (`"Scrollbar V"` 0) keeps drag and the wheel — the wheel without a bar is not
  measured yet: check it on the stand before relying on it. Not on `TreeScroll`, though: there the
  menu keeps the bottom and right 10 units of the view for a bar whenever the content overflows,
  drawn or not (`OnScrollbar` does not read the layout's `"Scrollbar H"` / `"Scrollbar V"`), so
  with a bar left out a press in that strip starts no drag. Keep both bars on `TreeScroll`, as all
  seven skins do.

Neutral draws its tree bars in pencil (`$neutral_dim`); its card is still a `list`, so its card bar
is the engine's — open.

## Roles of the window (`ozl_tree_<skin>.layout`, root `TreeWindow`)

The root may be the whole screen (neutral: the desk, tiled, and a centred 1600x900 `TreeStage`).

### Tree

| Role | Type | What the menu does |
|---|---|---|
| `TreeScroll` | ScrollWidget (`clipchildren 1`, `"Scrollbar V"` and `"Scrollbar H"` both 1 — the menu keeps their strips, see above; `color` + `style blank` for themed bars) | its size is the view; home, drag; one child: `TreeContent` |
| `TreeContent` | FrameWidget, exact size | resized to the plan; children below are `size fill` (proportional) so they follow. A static picture put first inside it scrolls with the tree, under the tiers and the links; the menu does not touch it |
| `TreeTiers` | frame, fill | tier labels: rows `tier_label` (child `TierText`), the row's corner on the label's point (`x = 22` across, the tier's centre along) |
| `TreeLines` | CanvasWidget, fill, `ignorepointer 1` | the paper grid (`GridStep`) and every link (`OZL_TreeLines`), redrawn on selection, hover, data, layout |
| `TreeFogEdge` | image, optional | the 80-unit fade at the start of the fog, tinted `FogColor`; the menu places and sizes it, but does not turn the picture: draw the fade in your tree's direction, clear where the visible tiers end and solid where `TreeFog` starts — `down`: clear at the top; `up`: clear at the bottom; `right`: clear on the left |
| `TreeFog` | panel or image | the rest of the fog, after the fade, tinted `FogColor` |
| `TreeNodes` | frame, fill | node cells; the `АБО` labels (rows `or_label`, child `OrText`) with the row's corner on the diamond |
| `TreeTip` | frame, hidden | above the hovered node, as wide as the TEXT of `TreeTipText` + 2 x `TipPadX`; children `TreeTipEdge` (fill), `TreeTipBg` (inset 1, resized), `TreeTipText` (at `TipPadX`, a fixed width wider than any tip — see Fonts — the frame clips the rest) |
| `TreeLegend` | anything | static: the six legend items are in the layout. Neutral lines them up by their texts: the items sit in a container `LegendRow` and its `OnShow` calls `menu.FlowLater(menu.Role("LegendRow"), 14, 0, false)` |

### Header

`BranchName` (text), `BranchSub` (text: `<faction> · досліджено N з M`, M = the nodes VISIBLE
through the fog, see "What the player may know"), `DevName` (static, a key in the layout),
`BtnClose` (button).

### Lists — row templates `ozl_<skin>_<row>.layout`

A list container is any widget the menu can create rows into (a `stack` = WrapSpacer, or a `list`'s
stack). Row templates are declared as `rows` of some `list` in the window description; rows that
live outside lists (tier and OR labels, price chips) go on a hidden `TreeTemplates` list. **A
container role without its row template costs two `SCRIPT (E)` "Cannot load layout" lines for
every row the menu tries** (`CreateWidgets` on a missing file): declare the row, or leave the
container out.

**Clickable rows** (branch, opens chip, registry) carry a `...Hit` child: a ButtonWidget with
`style Empty` that the menu renames `branch:<id>` / `open:<id>` / `reg:<id>`; everything else in
the row is made to ignore the pointer. Without the `...Hit` child the row ROOT is renamed, and then
the root itself must be such a button — a frame root gets no click. The menu finds the name on the
clicked widget or any of its parents. **Hover**: when the mouse enters or leaves a clickable row the
menu calls `OnRowHover(menu, row, kind, id, on)` (`kind` = `reg` / `branch` / `open`, `row` = the
row's root); the default shows a child `RegHover` / `RowHover` / `ChipHover` while the mouse is on
the row, if the row has one. When a repaint replaces the rows of a list under the pointer (a click
that selects, a new answer), the menu forgets the old hovered row WITHOUT an `OnRowHover(…, false)`
call — the row is gone — and the new row under a still pointer lights at the next move of the mouse
(expected, not measured).

| Container | Row | Children the menu fills |
|---|---|---|
| `BranchList` | `branch_row` | `RowHit` (the click, `branch:<id>`), `RowName`, `RowCount` (`done / visible`), `RowPick` (shown on the open branch), `RowBar`/`RowBarFill` (done fraction of the visible), `RowHover` (optional, under the mouse) |
| `PoolList` | `pool_row` | via `PaintPoolRow`: `PoolChip` (line colour), `PoolName`, `PoolValue` — the name and the number, nothing else: the owner removed the segment gauges (2026-10-31), the menu computes no `need` and there are no `PoolSeg` roles; anything the skin adds (bandit's tally marks draw the number itself); `PoolEmpty` (optional) shows when there is no line |
| `CardCostList`, `CardItemList` | `cost_row` | via `PaintCostRow`: `CostChip`, `CostName`, `CostValue` (`have / need`, or `need` when paid or unknown), `CostBar`/`CostBarFill` |
| `CardOpensList` | `opens_chip` | lined up left to right with wrapping, `OpensGap` units apart; the first text child (`ChipText`) sets the width, plus `OpensPad`; `ChipHit` (the click, `open:<id>`) and `ChipLine` are stretched to it; text and look via `PaintOpenChip`; a hidden node's chip (`??? невідомо`, the next step only) has its `ChipHit` hidden and takes no click; `ChipHover` (optional, under the mouse) |
| `Registry` | `registry_row` | via `PaintRegistryRow`: `RegHit` (the click, `reg:<id>`), `RegNum` (the dense number `menu.NumberOf`, two digits), `RegName`, `RegTier`, `RegState`, `RegPick`, `RegHover` (optional, under the mouse); ONLY the visible nodes, tier by tier, within a tier by `Index` — no rows for hidden nodes |
| `TreeTiers` | `tier_label` | `TierText` |
| `TreeNodes` | `or_label` | `OrText` |
| `NodePrice` (in the node) | `price_chip` | `PriceChip` (line colour), `PriceText` (amount); the tail `+N предм.` is one more chip with `PriceChip` hidden |

### Card

`CardEmpty` (shown when nothing is selected) / `CardBody`; `CardName`, `CardMeta`
(`тир N · після: … / після всіх: … / після будь-якого з: …`, hidden parents = `невідомо`; the
line is `menu.MetaOf(node)` — a skin that writes it otherwise takes it there instead of copying
it), `CardStatus` (word from `CardStatusText`, colour from `StatusColorOf`), `CardDesc`; section
heads `CardDescHead`,
`CardCostHead`, `CardItemsHead`, `CardTimeHead`, `CardOpensHead` (text from `SectionText`;
`CardItemsHead`/`CardItemList` hide when the node costs no material, `CardOpensHead`/`CardOpensList`
when it opens nothing); `CardTime`, `CardTimer` (the bare clock, shown while researching);
`CardSegs` + `CardSeg0`..`CardSeg19` or `CardBar`/`CardBarFill`; `BtnResearch` (+ `BtnResearchText`
from `ButtonText`, `BtnResearchHover` shown under the mouse while enabled), always visible; `CardWhy` (the reason a
button is disabled, a refusal of the server, "Запит надіслано..."); `CardStamp` + `CardStampImg`
(`StampOf`); `CardScroll` (scrolled to the top on every selection) and `CardFlow` (the stack,
updated after the card changes) if the card scrolls. `menu.RefreshCard()` updates exactly these
two. The menu calls it after every card paint, after a word-wrap inside `CardFlow` and after every
wrapping `FlowLater` (the opens list) — a ScrollWidget does not notice its content growing until it
is updated. A stack that sits elsewhere is the skin's own to update, and no hook follows its
`FlowLater`: `OnSelect` runs at the end of the card paint, BEFORE the flow lays the opens list out
(the next frame, or up to 12 frames later while the texts are measured), and `OnWrapped` fires only
after text wraps. So keep the opens list inside `CardFlow`, where the flow's own `RefreshCard`
reaches it; otherwise update that stack from `OnUpdate` for a dozen frames after `OnSelect`, then
call `menu.RefreshCard()`.

**Wrapped text.** `CardName`, `CardMeta`, `CardDesc` and the node's `NodeName` may each be ONE
text widget (a `TextWidget` for one line, or a `MultilineTextWidget` with an SDF font that the
engine wraps), or a container holding labels `<Name>0`, `<Name>1`, … — then the menu word-wraps the
text into those labels (measured with the first one), hides the unused ones and gives the last one
the rest. Which to pick is the rule in "Fonts" below: wrapped text is an SDF face or these line
labels. Labels in a `stack` take no room when hidden. The same text in the same colour is not
wrapped a second time.

## Roles of the node (`ozl_node_<skin>.layout`, root `NodeCell`)

`NodeCell` is the cell (renamed `cell:<id>`); give it room for everything that sticks out.

| Role | What |
|---|---|
| `NodeHit` | THE pointer target: a button with `style Empty`, renamed `node:<id>`, under the shape |
| `NodeShape` | ImageWidget; the skin's `Shapes` are loaded into slots 0..7, `ShapeOfNode` (by default `ShapeOf`) picks one, `ShapeColorOf` tints |
| `NodeRing`, `NodeSel` | the available ring (`RingShown`) and the selected ring |
| `NodeIcon` | the node's own icon from the tree config, tinted by `IconColorOf` |
| `NodeName` | text, or a container of `NodeName0`, `NodeName1` (wrapped) |
| `NodePrice` | a container the price chips are lined up in (clips them) |
| `NodePriceText` | plain text instead of chips: `Досліджено`, `Лишилось m:ss`, or the price when there is no chip row |
| `NodeBar`/`NodeBarFill` | shown while researching; filled to the done fraction |
| `NodeMark`, `NodeMarkText` | `Marks` slot from `MarkOf`, word from `MarkTextOf`, tinted by `MarkColorOf` |
| `NodeNum` | the dense number `menu.NumberOf(id)` (1, 2… over the VISIBLE nodes in display order, as in the registry), two digits — never `Index + 1` |

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
   `TreeTip` ignore the pointer entirely; for clickable rows see "Lists".

## The skin class (`OZL_TreeSkin`)

Data (set in the constructor; `Named("<id>")` fills the layout names): `Id`, `WindowLayout`,
`NodeLayout`, `RowPrefix`; the geometry above; colours as ARGB — `Txt`, `Dim`, `Acc`, `Ok`, `Bad`,
`LineDim`, `LineLit` (= Txt), `LineHl` (= Acc), `Lcd` (fill of the `АБО` diamond), `FogColor` (the
menu tints `TreeFog` and `TreeFogEdge` with it, whatever colour the layout gave them);
`LineStyle` (`"plain"` / `"sketch"`), `LineW` (2), `LineWHl` (2.5), `DashOn`/`DashOff` (6/5);
`GridStep`, `GridColor`, `GridX`, `GridY`, `GridW` (the paper grid, drawn on the canvas); `Shapes`,
`ShapeHover` (slot under the mouse, -1 none), `ShapeColors` (status -> tint); `Marks`; `SegOn`,
`SegOff` (0 = Acc / LineDim); `TipPadX`; `OpensGap` (6), `OpensPad` (4) — the opens chips' gap and
the room right of each chip's text, units.

Keep these ARGB numbers equal to the skin's `ui/tokens/<skin>.json` (the engine cannot read JSON at
compile time).

Hooks — each works without an override:

| Hook | Default |
|---|---|
| `int ShapeOf(status, selected)` | slot 0 if `Shapes` has any, else -1 (keep the layout's image) |
| `int ShapeOfNode(node, status, selected)` | `ShapeOf(status, selected)`; override to pick a variant per node — by `node.Id` (stable) or `menu.NumberOf(node.Id)`, not by `Index` (a wire order that shifts when the fog moves). The menu and `PaintNode` call this one |
| `int ShapeColorOf(status)` | `ShapeColors[status]`, else white |
| `bool RingShown(status, selected)` | available and not selected |
| `int NameColorOf(status)` / `PriceColorOf` / `IconColorOf` / `StatusColorOf` | the mockup's: locked Dim, short Bad, available/researching Acc, completed Ok (name: Txt, locked Dim) |
| `int MarkOf(status)` / `string MarkTextOf(status)` / `int MarkColorOf(status)` | lock / check / dot = `Marks` slots 0/1/2 for locked / completed / researching, **only when `Marks` has at least three slots** — with fewer `MarkOf` is always -1, so a skin with one or two marks overrides it (neutral: one tick); no text |
| `string StatusText(status)` | the status key's word (`StatusKey`) — tooltip and registry |
| `string CardStatusText(status)` | `StatusText(status)`; the word in `CardStatus` only (upper case, spread) |
| `string ButtonText(status, enabled)` | `Досліджено` for a completed node, else `Дослідити` |
| `string SectionText(key)` | the key's word (paper adds `:`, upper-case skins `OZL_Text.Upper`). A skin may split a decoration off into a widget of its own and return the word alone: clearsky draws `//` as its own dim label in front of the head |
| `string NodeNameText(name)` | the name (also the card's and the registry's name) |
| `string DataText(text)` | the text as it is. EVERY text the menu shows from the config — node and branch names, the faction, the description, the meta line, opens chips, the tooltip `name · status`, cost and pool labels — passes through it as the LAST step, after `NodeNameText` and with the menu's words around it, so a font filter sees every letter. A skin on a vanilla font without the Cyrillic capital `І` (U+0406) swaps it for the Latin `I` here, once (ecolog); a skin that sets such a text itself calls it too |
| `string TierText(tier)` | `I`, `II`…; `right` trees `тир I` |
| `void PaintNode(menu, cell, node, status, selected)` | shape, rings, icon, name, mark, number (price and bar are the menu's) |
| `void PaintPoolRow(menu, row, index, line, have, color)` | name (through `DataText`), value, chip; `index` = the row's place from the top (0, 1, …). No `need`: the gauges are gone (owner, 2026-10-31) |
| `void PaintRegistryRow(menu, row, node, number, tier, selected)` | `RegNum` = `Two(number)`, `RegName` = `DataText(NodeNameText(name))`, `RegTier`, `RegState` (`StatusText`, `StatusColorOf`), `RegPick`; the click name is the menu's |
| `void OnRowHover(menu, row, kind, id, on)` | shows / hides the row's `RegHover` / `RowHover` / `ChipHover` |
| `void PaintCostRow(menu, row, label, text, verdict)` | name, value coloured by verdict (1 ok / -1 bad / 0 unknown), bar colour |
| `void PaintButton(menu, btn, enabled)` | `BtnResearchText` Acc or Dim |
| `void PaintOpenChip(menu, chip, text, fogged)` | `ChipText` = text in Txt; a fogged chip (`??? невідомо`) in Dim. Its underline or frame is the skin's call: the mockup's paper drops it (neutral hides `ChipLine`), the base style dashes it |
| `string StampOf(status)` | none |
| `float DrawSegment(canvas, x1, y1, x2, y2, width, color, dashed, phase)` | a straight piece, dashed 6/5 with the phase carried along the polyline |
| `void DrawStroke(canvas, xs, ys, width, color, dashed, seed)` | the polyline; `LineStyle "sketch"` = the mockup's `sketch()` (short strokes with jitter and bend, a faint second stroke), seeded by the edge id so nothing trembles |
| `void DrawOrKnot` / `DrawAllKnot` | the `АБО` diamond (filled with Lcd, outlined) / the 10-unit square — a thick `DrawLine` is a filled rectangle |
| `void GridLine(canvas, x1, y1, x2, y2)` | one line of the paper grid in `GridColor`, `GridW` thick (called for every grid line when `GridStep` > 0) |
| `void OnShow(menu)` | — (static texts, start animations) |
| `void OnUpdate(menu, dt)` | — (every frame: marquee, blinking, flicker) |
| `void OnPaint(menu)` | — (after every full paint: a new answer of the server, another branch; a node selection is `OnSelect`, not a full paint) |
| `void OnSelect(menu, node, status, canResearch)` | — (node null = nothing selected) |
| `void OnWrapped(menu, box)` | — (the frame after `PutText`: the menu has just word-wrapped a container `box` — a node name, `CardName`, `CardMeta`, `CardDesc`. When `box` lies inside `CardFlow` the menu has already called `RefreshCard`; for a box outside it (a node name) it has not. Update your own stacks here) |
| `bool OnClick(menu, w)` | false (clicks the menu did not recognise: helper buttons...) |

Helpers on the menu for hooks: `Role(name)`, `PlaceUnits`, `SizeUnits`, `UnitsOf`, `Px()`,
`PutText(w, text, color)` (a text role, wrapped if it is a container), `FitLater(text, target, pad,
mode)` (next frame: `target` as wide as the text — underlines, strikes; mode 0 keep x, 1 right-anchored,
2 centred in the parent), `BarLater(track, fill, fraction)`, `FlowLater(box, gap, pad, wrap)` (next
frame: the box's children left to right, each as wide as from its left edge to the right end of its
first visible text — `GetTextSize`, the text left-aligned — plus `pad`, then `gap`),
`PointName(line)`, `PointColor(line)`, `PoolOf(line)`, `ItemLabel(item)`, `LeftOf(node)`,
`View()`, `CurrentBranch()`, `BranchCount()`, `SelectedId()`, `HoveredId()`, `NodeIdAt(widget)`,
`TaggedAt(widget, "open:")` (the id from a `<tag><id>` name on the widget or a parent),
`NumberOf(id)` (the dense number of a visible node, 0 if not in the current branch),
`MetaOf(node)` (the card's meta line), `RefreshCard()` (updates `CardFlow` and `CardScroll`).
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
is rotated or styled; then two sprites `_ua`/`_en` and a `*_IMG` key (STRINGS.md). Budget: up to
2048x2048 per skin. Neutral: one 1024x512 atlas and three small textures (0.08 MB).

## Fonts

The mod's fonts are in `OpenZone_Research/gui/fonts/` (see `source/fonts/README.md`): in a layout
`font "OpenZone_Research/gui/fonts/ozl_hand48"` with `"exact text size"` = the CELL height in units
= round(CSS px x the face's cell ratio). Put them in the skin's tokens as fonts.

**The rule for wrapped text: an SDF face, or the menu's line labels.** A `MultilineTextWidget` or
`RichTextWidget` draws every BITMAP (FNT3) font at its atlas's own pixel size, whatever
`"exact text size"` asks and on every screen — the vanilla bitmap fonts too (skill gui-layouts
§30, measured 2026-10-31 at 1920x1080 and 3840x1600); only SDF (FNT5) fonts scale there. So:

- a text the ENGINE wraps (`MultilineTextWidget`, `RichTextWidget`) uses one of the SDF faces:
  `ozl_sdf_hand32`, `ozl_sdf_type32`, `ozl_sdf_serif32`, `ozl_sdf_sans32`, `ozl_sdf_comic32`,
  `ozl_sdf_oswald32`, `ozl_sdf_oswaldb32`. One SDF line takes k x S (S = the text size, k =
  1.375–1.625: an SDF line measures more than the size it is drawn at) and every further line adds
  S, so n lines need (n − 1) x S + k x S — not n x k x S;
- with a bitmap face (`ozl_hand48`, `ozl_hand72`, …) the text is a container of line labels that
  the MENU wraps (`PutText`, above) — neutral does this;
- a `WrapSpacer` with `"Size To Content V"` does NOT grow when its multiline children wrap: it keeps
  the sum of their one-line heights and clips the rest. A multiline text inside the card's stack
  (`CardFlow`) needs a height of its own, or the line labels.

Bitmap faces are fine in every one-line `TextWidget`. The vanilla `7segment` faces carry only
` +,-./0123456789` — no colon: a clock in them draws its `:` as a sprite (sop does).

**A TextWidget clips its own text at its box, and `"w": "auto"` (`"size to text h"`) makes the box
the sum of the glyphs' advances** (measured 2026-10-31). The last letter of a slanted face reaches
past its advance and loses its top: in Caveat the English `locked` drew as `lockea` and `after all`
as `after alı`, in a GridSpacer, a WrapSpacer and a plain frame alike; Ukrainian words lose it too
(the opens chip `??? невідомо` drew as `невідомc`). So no label with a slanted face is sized to its
text: give it a box wider than any text it gets and size or line up the rest by the text
(`FitLater`, `FlowLater` and the tooltip measure with `GetTextSize`, not the box) — neutral's
legend, opens chips and `TreeTipText` do. A fixed-width label ending far from its right edge is
safe as it is.

## What the player may know (owner, 2026-10-31)

"The player must not know how many technologies remain — on any terminal." So nothing a skin
shows may count or number the hidden nodes:

- `досліджено N з M` (`BranchSub`, `RowCount`): M = the nodes VISIBLE through the fog;
- the registry lists only visible nodes, numbered 01, 02… densely in display order (tier, then
  `Index`); `NodeNum` uses the same number (`menu.NumberOf`);
- the server sends no branch total, and stubs (`Hidden`) only for the NEXT step — a hidden node
  with at least one visible parent: they feed the opens chips `??? невідомо` and the fog band;
  deeper nodes are not sent at all;
- `Index` on the wire is a dense ORDER over what is sent (visible nodes and those stubs, in the
  config's order) — use it to sort, never print it.

A skin never shows `Index + 1`, `Hidden.Count()` or a total of its own.

## Layout mix-up (stand, 2026-10-31; cause unknown)

`CreateWidgets("OpenZone_Research/gui/layouts/ozl_sop_or_label.layout")` returned the widgets of
`ozl_sop_price_chip.layout` (its root `OZL_SopPriceChip` and its children) on two freshly started
clients and in one `ui_load` of that path — an earlier `ui_load` of the same path in the same
session gave the right file. The pbo entry and the loose file held the right text, a byte-identical
copy under another name loaded right, and neutral's pair of files with the same two row names never
mixed. Not the cause: the two roots had different names; 25 common string hashes (CRC32, FNV-1/1a
32/64, djb2, sdbm, one-at-a-time, murmur3, xxHash32, SuperFastHash, ELF, …) of 12 spellings of the
two paths (as written, lower/upper case, backslashes, no extension, file name only, no mod prefix)
at 64, 32, 24 and 16 bits never collide.

It was not sop's pair alone. A later client log (2026-10-31 15:49) has ecolog's `tier_label` coming
back as duty's price chip (`OZL_DutyPriceChip`) and clearsky's as ecolog's opens chip
(`OZL_EcologOpensChip`); bandit's second pool row arrived as clearsky's opens chip; and in the
combined pass (log 16:59, windows opened duty, freedom, ecolog) ecolog's node cells, made from
`ozl_node_ecolog.layout`, held freedom's branch row. The wrong file was always one created earlier in
the same client session.

Measured on the stand (2026-10-31 17:08), when `ozl_sop_opens_chip.layout` came back as
`OZL_BanditCostRow`: loading the same path again gave the same wrong row, and so did the path in
lower case — **the engine's layout cache key ignores letter case**. The spellings with a `./` segment
and with a doubled `/` were refused by the engine (two `SCRIPT (E)` lines, "Cannot open layout" and
"Cannot load layout", and no widget). The same path with backslashes
(`OpenZone_Research\gui\layouts\ozl_sop_opens_chip.layout`) loaded the right file — **the key does tell
the two kinds of slash apart**.

What to do:

- look at the ROOT's name in `ui_tree` — it says which file the engine used;
- the menu guards every layout file it creates widgets from (`MakeWidgets()`: the host, each window,
  each node cell, each row): the root's name must be the expected one, ignoring underscores and
  case — a row layout's file name (`ozl_sop_or_label.layout` → `OZL_SopOrLabel`; the generator names
  every root that way, and a hand-written row layout must too), `NodeCell` for
  `ozl_node_<skin>.layout`, `TreeWindow` for `ozl_tree_<skin>.layout`, `OZL_TreeHost` for the host.
  On a mismatch it unlinks the wrong widget and creates it ONCE more with the path's `/` replaced by
  `\` — the spelling measured above — and keeps that one when its root is right. When the backslash
  spelling is wrong too, or returns nothing, the last widget is kept, as before the guard. Either way
  it writes ONE line: `tree: <path> gave '<root>', wanted '<root>' (another file's root); <what the
  backslash retry gave>`; the same path with the same outcome is written once per window. The node and
  window roots are the same in all seven skins, so a swap between two skins' node cells (or two
  windows) is invisible to the guard, while a swap between kinds (a row, the host, a window, a node
  cell) is caught. Widgets a skin creates itself with `CreateWidgets` are not guarded;
- when the name cannot change, give both files the same widgets and let the script show the right
  ones by where the row sits (sop's workaround: whichever file arrives, the row works); when it
  can, rename.

## Checking a skin

`python -m dayz_mcp.layoutgen <repo> OpenZone_Research`, then MCP `mod_lint`, `mod_build`,
`client_compile_check`, `server_start`, `log_verdict`; on the stand:
`world_exec verb=oz_research args={"op":"demo","owner":"<faction>"}` and
`{"op":"treeui","owner":"<faction>","as":"post"}` (as=post with `Settings.ResearchPost` set lets the
player spend). Look at it at 1920x1080 and 3840x1600, in English and Ukrainian. Move the real mouse
over the middle of a node (`ui_click via=cursor` on its name): the tooltip and the highlighted links
must appear and the click must select it.
