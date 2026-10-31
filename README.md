# OpenZone Research

*[Українською](README.uk.md)*

Research points and a technology tree for OpenZone servers, on the OpenZone core.

**Status: research by lines.** Seven lines -- biology, anomalies, electronics, loot,
trails, ballistics, protection -- each with one sample, one analysis and one carrier,
shared by every faction that works the line. The mod starts empty; two packs of configs
ship under `examples/`.

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
   the sample is worth (`Points`, the rarity of the input) and its starting purity
   (`Purity`, 0.7 by default). Every working module of the line in the packer's three
   slots adds 0.1 to the purity and 10% to the chance that the packer gives two samples
   instead of one. A rule may require modules (`RequiredTools`).
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
and sends the id, so the client decides nothing. `TreeBackground`, also optional, replaces the
backdrop of the tree canvas that the skin draws with a picture of your own.

A node has one of five statuses: `locked` (the parents are not done), `short` ("not enough": the
parents are done, but the faction pool or the materials in the cargo of its own terminal near the
player do not cover the cost), `available`, `researching` and `completed`. `short` is a hint: the
start checks the cost itself. With no terminal near the player the materials are unknown, and
unknown materials do not make a node `short`.

The fog of war is counted by the server. A node is shown when it is a root, completed or running,
or when it lies within `TreeVisibilityDepth` steps of a completed node: 1, the default, shows the
next step only; 0 shows nothing beyond the completed nodes. Every other node of the branch reaches
the client as a nameless stub that carries only its place, its tier and the parents that are shown;
the counter of the branch still counts them all.

## Files

Configs live in the server profile, `$profile:OpenZone\`:

| file | holds |
|---|---|
| `OZ_Research_Settings.json` | default owner, the two post names, the fog depth of the tree |
| `OZ_Research_PointTypes.json` | point types, one per line (version 2) |
| `OZ_Research_Owners.json` | per faction: terminals, devices, the tree window (`Skin`), an optional tree backdrop |
| `OZ_Research_Rules.json` | processing rules in groups (version 2) |
| `OZ_Research_Tree.json` | branches with nodes (version 2) |
| `OZ_Research_Modules.json` | modules: purity bonus and double-output chance (version 2) |
| `OZ_Research_Statics.json` | static stations to place once |

A version 1 file of point types, rules, tree or modules is not converted: the core moves
it to quarantine and the mod starts on defaults.

The faction state, `research\<faction>.json`, holds the pool, the completed nodes and the
running projects. `OZ_Research_Statics_State.json` remembers which statics were placed.

Editing: the seven configs are registered with the core's editor, so they are edited in
the OpenZone admin window (VPPAdminTools, CONFIG pane) with validation and a backup on
every write; the RESEARCH pane (the `_VPP` glue mod) lists the factions with their pools
and runs resets, grants, completions and reloads.

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
statics and a journal. Until the site learns the version 2 configs, edit them in the VPP
editor: the mod refuses a version 1 file from the site. The console client
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
- The RESEARCH pane (`OpenZone_Research_VPP`) also needs OpenZone Core VPP and
  VPPAdminTools.

## Repository

| directory | what |
|---|---|
| `OpenZone_Research/` | the mod: configs, items, stations, the terminal, the tree, the service, the models |
| `OpenZone_Research_VPP/` | the RESEARCH pane of the admin window |
| `OpenZone_Research_Bridge/` | a stand-only verb for the `dayz` MCP bridge, never published |
| `source/models/` | the Blender generators of the models; see its README |
| `ui/` | layout descriptions; `layout_build` writes the `.layout` files from them |
| `examples/` | config packs: `full` (seven factions) and `test-stand` |
| `packaging/` | what a published `@Mod` needs besides the pbo |
| `docs/` | measurements; the design lives in the series' `docs/specs/` |

Design: `E:\openzone\docs\specs\2026-09-20-openzone-research-design.md` and, for the lines,
`E:\openzone\docs\specs\2026-10-30-research-lines-rework-design.md` (the OpenZone series
repository).

## Licence

CC BY-NC-SA 4.0 with an additional permission -- see `LICENSE` and `NOTICE`.
