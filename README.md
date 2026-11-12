# OpenZone Research

*[Українською](README.ua.md)*

Research points and a technology tree for OpenZone servers, on the OpenZone core.

**Status: research by lines.** Seven lines -- biology, anomalies, electronics, loot,
trails, ballistics, protection -- each with one sample, one analysis and one carrier,
shared by every faction that works the line. A fresh server starts with the `example` pack:
the mod carries it in `OpenZone_Research/defaults` and writes each research config the
profile does not have yet; a file already in the profile is not touched. The one exception
is a profile with no owners, no rules and no tree at all -- what a fresh start wrote before
the mod carried the pack: the pack is written over it, and the old files go to
`Backup/before-defaults.<file>`. The pack places no stations: the administrator puts them
in `OZ_Research_Statics.json`. Both packs, `example` and `test-stand`, are under `examples/`.

## What it does

Three things of the game, all described by the administrator's JSON:

- **Stations.** Put the input into a station's cargo and press F. The station takes the
  input and the consumables at once, works by the calendar (a restart does not lose the
  work), puts the result into its own cargo and starts the next cycle by itself while
  input is left. A result that does not fit stays as a pending record until collected.
- **Rules.** Which device takes what, how long, what comes out and with what chance.
- **The tree.** Branches belong to factions; nodes cost points and materials, complete
  at once or as a timed project, and unlock by their parents (`all` or `any`). Rules may
  require a node; a completed node is a fact of the faction, not of the player.

## Lines

Every sample, carrier, packer, analyzer and module belongs to a line (`ozlLine` in
`config.cpp`); the line is also the point type.

1. **Packer.** Takes raw input and gives the line's sample. The rule says how many points
   the sample is worth (`Points`, the rarity of the input). The sample starts at the purity
   of its line, the `BasePurity` of the line's point type (0.7 by default); a rule may name
   a `Purity` of its own (above 0, up to 1) for that one item. A `Purity` of 0, -1 or none
   at all takes the line's, and a `BasePurity` of 0 or none at all is 0.7: nobody sets a
   purity of zero on purpose, and a key left out of the file reads as 0. Every working
   module of the line in the packer's three slots adds 0.1 to the purity and 10% to the
   chance that the packer gives two samples instead of one. A rule may require modules
   (`RequiredTools`).
2. **Analyzer.** Takes one sample of its line and gives the line's carrier. The sample's
   purity is the chance that the analysis succeeds; the carrier takes the sample's points.
   Analyzers and terminals have no module slots.
3. **Terminal.** A carrier handed in pays its points of its line to the pool of the
   faction of the one who hands it in. Stations pay nothing; the terminal does.

The points and the purity travel in the item itself, as a short versioned string that only
the server reads.

## Factions and who spends

The faction is the core's: the player's organisation (a member of Duty is `duty`), else
their base faction (`stalker` among the factions mod's defaults). The pool and the
completed nodes belong to that faction. Spending is the leader's right, and the right of
whoever holds the post named in the settings: `ResearchPost` for organisations,
`BasePost` for the base axis; an empty post name means nobody but the leader.

Terminals and stations are listed per faction in `OZ_Research_Owners.json`. If any
faction lists devices, a faction without a list gets none; if nobody lists any, every
device is everyone's.

## The tree screen

Each faction looks at its tree through a window of its own, a skin: `ecolog`, `clearsky`,
`duty`, `freedom`, `sop`, `bandit` or `neutral`. The window changes the layout, the shape of a
node, the direction the tree grows and the look of the node panel; the data and the actions are
the same in all of them. The skin is the optional field `Skin` of a faction in
`OZ_Research_Owners.json`. Left out, it is the faction's own id (a member of `duty` looks through
the `duty` window), and a faction whose id is none of the seven gets `neutral`. Any faction may
name any skin; an unknown name is cleared with a warning in the log. The server resolves the skin
and sends the id, so the client decides nothing.

A node has one of five statuses: `locked` (the parents are not done), `short` ("not enough": the
parents are done, but the faction pool or the materials in the cargo of its own terminal near the
player do not cover the cost), `available`, `researching` and `completed`. `short` is a hint: the
start checks the cost itself. With no terminal near the player the materials are unknown, and
unknown materials do not make a node `short`.

The fog of war is counted by the server. A node is shown when it is a root, completed or running,
or when it lies within `TreeVisibilityDepth` steps of a completed node: 1, the default, shows the
next step only; 0 shows nothing beyond the completed nodes. A hidden node one step past the shown
ones (with at least one shown parent) reaches the client as a nameless stub that carries only its
place, its tier and the parents that are shown; deeper nodes are not sent at all. No terminal tells
how many technologies remain: the counter of a branch counts the shown nodes, the client gets no
branch total, and the places (`Index`) are dense over what is sent, so a gap cannot betray a
hidden node.

## Files

Configs live in the server profile, `$profile:OpenZone\`:

| file | holds |
|---|---|
| `OZ_Research_Settings.json` | default owner, the two post names, the fog depth of the tree |
| `OZ_Research_PointTypes.json` | point types, one per line, each with the line's base purity `BasePurity` (version 3) |
| `OZ_Research_Owners.json` | per faction: terminals, devices, the tree window (`Skin`) |
| `OZ_Research_Rules.json` | processing rules in groups; a `Purity` of 0 or -1 takes the line's (version 3) |
| `OZ_Research_Tree.json` | branches with nodes (version 2) |
| `OZ_Research_Modules.json` | modules: purity bonus and double-output chance (version 2) |
| `OZ_Research_Statics.json` | static stations to place once |

A version 1 file of point types, rules, tree or modules is not converted: the core moves
it to quarantine and the mod starts on defaults. A version 2 file of point types or rules
is converted when it is read and written back as version 3, the old file kept in the
core's backup: every line gets a `BasePurity` of 0.7, and a rule whose `Purity` is 0.7
gets -1, the line's; any other `Purity` stays as it was.

The faction state, `research\<faction>.json`, holds the pool, the completed nodes and the
running projects. `OZ_Research_Statics_State.json` remembers which statics were placed.

Editing: the seven configs are registered with the core's editor, so they are edited in
the OpenZone admin window (VPPAdminTools) with validation and a backup on every write. The
research module of that window (the `_VPP` glue mod) has eight pages in the window's rail:
Overview (the factions with their pools; resets, grants, completions and reloads), Tree,
Chains, Point types, Owners, Modules, Statics and Settings -- one draft of the seven files
with its problems, undo, redo, discard and apply. Settings asks the core who gives the
factions and dims what that source does not know.

## The bridge and the web editor

With the Discord bridge (`openzone-bridge`, `RESEARCH_DIR` in its `.env`) the mod
subscribes the kind `research` to the core's bridge client: after start it posts a boot
letter (revision, counters, the seven config names), after every applied edit a `changed`
letter, and it answers every command of the bridge with a `result` letter by token. The
classes the editor checks against are the core's business: `OpenZone_Core` dumps every
class of the server with its parent and its game names into `$profile:OpenZone\classes.tsv`
at each start, and the bridge reads that file itself. Commands come down
as poll items: `cfg_apply` reads a candidate file from `research\xchg\` and applies it
the way the VPP editor does (validation, one backed-up write, a live replace, a resync of
the clients), deleting the file on success and leaving it on refusal; `reset`, `grant`,
`complete`, `reload` and `respawn` share the admin section with the VPP pane and are
logged as `admin bridge:<who>`. The last hundred answered tokens are remembered, so a
command the bridge re-sends after its own restart gets its stored answer. The boot letter
retries with a doubling pause (5 s up to 5 min) while the bridge does not answer; a
bridge that knows the kind asks for it with a poll item `{op:"hello"}`.

The bridge's admin site edits the configs as tables and canvases, checks them the way the
game will, keeps every version with restore, and shows the factions with their pools, the
statics and a journal. Since bridge commit 959ad7d it knows the seven configs at their
current versions (point types and rules 3, tree and modules 2) and converts version-2 files
the way the game does; a bridge older than that writes files the mod refuses, so edit in
the VPP editor there. The console client
`scripts/research.mjs` of the bridge does the same from a terminal. Without the bridge
nothing changes: the mod writes one line, `bridge: boot refused`, and the VPP editor
remains the way to edit. The shared secret of the bridge is the whole authority of its
commands; `OZ_Perm.IsAdmin` takes no part in them.

Measurements: `docs/measurements/2026-09-20/bridge.md`. Design:
`E:\openzone\docs\specs\2026-09-20-openzone-research-bridge-design.md`.

## Requires

- [Community Framework](https://steamcommunity.com/sharedfiles/filedetails/?id=1559212036)
- [OpenZone Core](https://steamcommunity.com/sharedfiles/filedetails/?id=3798432022)
- Factions come from [OpenZone Factions](https://steamcommunity.com/sharedfiles/filedetails/?id=3798436325);
  without it every player belongs to the default owner from the settings.
- The research pages (`OpenZone_Research_VPP`) also need OpenZone Core VPP and
  VPPAdminTools.

## Repository

| directory | what |
|---|---|
| `OpenZone_Research/` | the mod: configs, items, stations, the terminal, the tree, the service, the models |
| `OpenZone_Research_VPP/` | the research pages of the admin window |
| `OpenZone_Research_Bridge/` | a stand-only verb for the `dayz` MCP bridge, never published |
| `source/models/` | the Blender generators of the models; see its README |
| `ui/` | layout descriptions; `layout_build` writes the `.layout` files from them |
| `examples/` | config packs: `example` (seven factions, what the mod ships) and `test-stand` |
| `packaging/` | what a published `@Mod` needs besides the pbo |
| `docs/` | measurements; the design lives in the series' `docs/specs/` |

Design: `E:\openzone\docs\specs\2026-09-20-openzone-research-design.md` and, for the lines,
`E:\openzone\docs\specs\2026-10-30-research-lines-rework-design.md` (the OpenZone series
repository).

## Licence

CC BY-NC-SA 4.0 with an additional permission -- see `LICENSE` and `NOTICE`.
