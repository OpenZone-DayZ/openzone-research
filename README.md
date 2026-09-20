# OpenZone Research

*[Українською](README.uk.md)*

Research points and a technology tree for OpenZone servers, on the OpenZone core.

**Status: first release after `ZP_Research`.** The game rules are the ones of ZP_Research;
the code is new and stands on the core's services. Nothing carries over from a ZP_Research
server: this mod starts empty. A converter turns the ZP example packs into this mod's
configs (`scripts/convert-zp-examples.py`); two converted packs ship under `examples/`.

## What it does

Three things of the game, all described by the administrator's JSON:

- **Stations.** Put the input into a station's cargo and press F. The station takes the
  input and the consumables at once, works by the calendar (a restart does not lose the
  work), puts the result into its own cargo and starts the next cycle by itself while
  input is left. A result that does not fit stays as a pending record until collected.
- **Rules.** Which device takes what, how long, what comes out and with what chance.
  Samples carry a purity; modules in the station's slots add to it; a sample's purity
  multiplies the chance of the rule that consumes it.
- **The tree.** Branches belong to factions; nodes cost points and materials, complete
  at once or as a timed project, and unlock by their parents (`all` or `any`). Rules may
  require a node; a completed node is a fact of the faction, not of the player.

Between them: **carriers**, items that hide a point value until identified at a terminal,
and **data items** with fixed rewards. Handing either in at a faction terminal pays the
pool of the faction of the one who hands it in. Stations pay nothing; the terminal does.

## Factions and who spends

The faction is the core's: the player's organisation, else their base faction (a lone
stalker is `loner`, a bandit is `bandit`, a member of Duty is `duty`). The pool and the
completed nodes belong to that faction. Spending is the leader's right, and the right of
whoever holds the post named in the settings: `ResearchPost` for organisations,
`BasePost` for the base axis; an empty post name means nobody but the leader.

Terminals and stations are listed per faction in `OZ_Research_Owners.json`. If any
faction lists devices, a faction without a list gets none; if nobody lists any, every
device is everyone's.

## Files

Configs live in the server profile, `$profile:OpenZone\`:

| file | holds |
|---|---|
| `OZ_Research_Settings.json` | default owner, the two post names, tree visibility depth |
| `OZ_Research_PointTypes.json` | point types with category, kind and tier |
| `OZ_Research_Owners.json` | per faction: terminals, devices, tree background |
| `OZ_Research_Rules.json` | processing rules in groups |
| `OZ_Research_Tree.json` | branches with nodes |
| `OZ_Research_DataItems.json` | data items and their rewards |
| `OZ_Research_Modules.json` | modules: purity bonus and which devices take them |
| `OZ_Research_SampleTypes.json` | sample types and their names |
| `OZ_Research_Statics.json` | static stations to place once |

The faction state, `research\<faction>.json`, holds the pool, the completed nodes and the
running projects. `OZ_Research_Statics_State.json` remembers which statics were placed.

Editing: the nine configs are registered with the core's editor, so they are edited in
the OpenZone admin window (VPPAdminTools, CONFIG pane) with validation and a backup on
every write; the RESEARCH pane (the `_VPP` glue mod) lists the factions with their pools
and runs resets, grants, completions and reloads. Item names come from the JSON, not from
the config.cpp, so a server can rename samples and data without a repack.

## The bridge and the web editor

With the Discord bridge (`openzone-bridge`, `RESEARCH_DIR` in its `.env`) the mod
subscribes the kind `research` to the core's bridge client: after start it posts a boot
letter (revision, counters, the nine config names, and a dump of every class of the five
roots the rules check into `research\xchg\classes.tsv`: root, name, parent, game name
in the `original` and the `english` column -- the server reads every `stringtable.csv` it
can open in the loaded archives, ours and the neighbours', and a class whose key no table
holds gets the name the server itself resolves; the whole dump takes under a second), after
every applied edit a `changed` letter, and it answers every command of the bridge with a
`result` letter by token. Commands come down
as poll items: `cfg_apply` reads a candidate file from `research\xchg\` and applies it
the way the VPP editor does (validation, one backed-up write, a live replace, a resync of
the clients), deleting the file on success and leaving it on refusal; `reset`, `grant`,
`complete`, `reload` and `respawn` share the admin section with the VPP pane and are
logged as `admin bridge:<who>`. The last hundred answered tokens are remembered, so a
command the bridge re-sends after its own restart gets its stored answer. The boot letter
retries with a doubling pause (5 s up to 5 min) while the bridge does not answer; a
bridge that knows the kind asks for it with a poll item `{op:"hello"}`.

The bridge's admin site edits the nine configs as tables and canvases (the tree by
Tier columns, the rules as chains), checks them the way the game will, keeps every
version with restore, and shows the factions with their pools, the statics and a
journal. The console client `scripts/research.mjs` does the same from a terminal.
Without the bridge nothing changes: the mod writes one line, `bridge: boot refused`,
and the VPP editor remains the way to edit. The shared secret of the bridge is the
whole authority of its commands; `OZ_Perm.IsAdmin` takes no part in them.

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
| `OpenZone_Research/` | the mod: configs, items, stations, the terminal, the tree, the service |
| `OpenZone_Research_VPP/` | the RESEARCH pane of the admin window |
| `OpenZone_Research_Bridge/` | a stand-only verb for the `dayz` MCP bridge, never published |
| `ui/` | layout descriptions; `layout_build` writes the `.layout` files from them |
| `examples/` | the converted packs: `zone-protocol` (production) and `test-stand` |
| `packaging/` | what a published `@Mod` needs besides the pbo |
| `docs/` | measurements; the design lives in the series' `docs/specs/` |

Design: `E:\openzone\docs\specs\2026-09-20-openzone-research-design.md` (the OpenZone
series repository).

## Licence

CC BY-NC-SA 4.0 with an additional permission -- see `LICENSE` and `NOTICE`.
