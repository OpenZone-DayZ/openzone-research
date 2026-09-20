# Stations on the stand (plan T6), 2026-09-20

Full-stack retail stand (core, factions, VPP, the MCP bridge, this mod), the
test-stand pack, the owner's account connected through the retail client.
Every step went through the `dayz` MCP: `world_action` for the player's
actions, the mod's own `oz_research` verb (OpenZone_Research_Bridge, server
only) for what no generic verb reaches -- items created in a station's cargo,
a station's state, a faction's pool.

## What was measured

| Step | Result |
|---|---|
| owner of the connected player | `owner=loner base=loner org= maySpend=0 identity=present` -- the core answers, the mod does not guess |
| `pb_pak_bio` on the sample fridge (Apple + Rag consumable, 10 s) | started by `OZL_ActionStart`; Apple deleted, one rag taken off the stack; output `OZL_Sample_01` content `Apple` purity 0.797 (base roll x quality 1.0) |
| auto-continue | after the cycle the station picked `pb_pak_teh` (Rag -> `OZL_Sample_17`) on its own and ran it until the rags were gone, one cycle per 10 s + 1 s |
| `pb_analiz_bio` on the microscope (sample in, 15 s) | quality 0.8 = the sample's purity, output purity 0.4, chance x0.8; `OZL_Data_01` produced |
| refusals | no input -> `STR_OZL_ERR_NEED_INPUT`, the reason (`short of 1 x Rag in cargo`) only in the dbg log; the client shows the key as a 4 s notification titled by the mod name |
| success notices | `STR_OZL_MSG_STARTED`, `STR_OZL_MSG_COLLECTED` seen on screen (Ukrainian client) |
| full cargo | cycle ends with `placed=0 stuck=1`, state DONE, a WARNING line; after one slot is freed, `OZL_ActionCollect` hands the item out (`handed=1 left=0`) and the line resumes |
| restart mid-cycle | graceful `server_stop` while RUNNING; after the boot `resumed 'pb_pak_teh', -67 s left`, the cycle completed at once, the line continued; cargo (Apple, Rag) survived two restarts |
| statics | 47 entries spawned once (`statics: entries=47 spawned=47`), the state file lists them, the next boots spawn 0; two entries with a class the mod does not have and two duplicates of one position were dropped from the pack |

## The bug the stand found

The first cycles ran 16..26 s instead of 10: `m_OZL_EndSec = OZL_Clock.NowSec() +
time` with a `float time` is computed in float32, and calendar seconds (~2^28)
round to a multiple of 16 there (`end - now = 16` for `time = 10`). The
deadline is now an `int` end to end. Recorded in the dayz-modding skill.

## Not covered here

`CanReleaseAttachment` (a tool locked while a rule runs) needs an inventory
drag; a stream of a foreign version needs a future build. Both stay as read.

# The terminal and the tree (plan T7), same stand, later the same night

| Step | Result |
|---|---|
| `OZL_ActionIdentify` with a carrier `bio_lab_t1:7` in hands at the lab computer | status line `Наукові дані: Лабораторне дослідження біології 1 тиру (Біологія, лабораторні, T1) +7`, toast `Дані визначено`; the prompt list on the terminal shows start (instant), identify/open tree (instant, cycled) and `Здати дані [УДЕРЖИВАЙТЕ]` |
| `OZL_ActionDeposit` (3 s hold) | carrier deleted, `bio_lab_t1` +7 in `research/loner.json`, status line with the amount, `deposit: ... -> loner` in the log |
| `OZL_ActionOpenTree` with empty hands | `show research_tree to <uid>` -- the core's OZ_Show reaches the client (the menu is plan T9) |
| service `research`, op `research` without the post | `STR_OZL_ERR_NO_ACCESS`: the gate asks the core (OZ_Roles), the stand player holds no post in Discord |
| `pb_osnovy` (instant, cost 5) with the post pretended for one call | pool 20 -> 15, node completed, `OZL_Events.OnNodeCompleted` |
| `pb_bio_zbir` (cost 8 + Paper x2 from the terminal cargo) | pool 15 -> 7, both papers consumed from the lab computer's cargo, node completed |
| `pb_bio_anatom` (60 s project, cost bio_field_t2 10 + bio_lab_t1 4) | pool paid at the start, the project written to the state file with its EndSec; the 10 s poller completed it after the deadline (see the log line below) |
| `reload` op | the tree pack edited on disk (loner added to the science branch) took effect on the running server without a restart |

The stand player holds no Discord post, and posts come from the live projection
of the bridge, not from the player file: the `as=post` argument of the stand
verb applies a projection with the post for one call (the next bridge poll
restores the real one), so the gate itself runs unchanged.

# The admin section and the RESEARCH pane (plan T8)

| Step | Result |
|---|---|
| boot | the core's line reads `admin=research,spawns,news,players,config,factions services=research` |
| section `list` through the stand verb | one row per faction of the core's registry plus every state file: id, name, pool, completed/active, `Known` 0 for factions without a state file (the list creates none) |
| section `grant:loner:bio_field_t1:5` | the loner file went 7 -> 12 with `admin <uid>: owner 'loner' granted 5 bio_field_t1` in the log; the answer is the fresh list |
| `ui_preview` of `oz_research_vpp_pane.layout` (host 1000 x 620, root shown by a fixture) | 56 widgets, 0 issues; the two listboxes, the three fields, the five buttons and the statics text sit where the description says |

The MCP bridge now rides on the client too (`dayz-mcp.local.toml`): the preview tools talk to its client half, and a fixture must name `nth` explicitly -- an absent member of a fixture op reads as 0, not the constructor's 1.

# The tree screen (plan T9)

| Step | Result |
|---|---|
| `OZL_ActionOpenTree` at the lab computer (`world_action`, radius 1.6 so the nearest of three computers is the target) | `show research_tree to <uid>` on the server, `ui_menu` reports `OZL_TreeMenu`, the client asked `tree` and got it |
| the screen | faction name from the core in the header with its colour chip, the pool line, the branch list with done / total, the node grid by level and row with status bars, the card on a click (name, description, cost with names and the pool in brackets, materials, duration, status) |
| geometry | TreeArea 1630 x 1161 px = 1100 x 784 units at 1.4815; a node instance created into it measures 296 x 95 px = 200 x 64 units: CreateWidgets into a panel keeps the layout scale, SetPos takes layout units |
| `BtnResearch` | hidden while the server said MaySpend 0; visible after the stand verb pretended the post before the client's request |
| a click on `BtnResearch` (through the menu's handler, `ui_click`) | `research` on the server, pool 10 -> 2 of the cost type, the node completed, the fresh tree repainted the node green and the branch counter 3 -> 4, the toast `Дослідження розпочато` |
| first draw | connector lines went from a parent's bottom to a child's top and crossed the grid; the tree grows left to right, so they now run from the parent's right edge to the child's left edge |

The stand's test account holds no post, so a real client sees no research button until Discord gives it the post: that part is the owner's check with a leader account.
| English client (`client_start(language="english")`) | the mod's own strings switch (Branches, Close, Cost, Duration, Completed, the hint); node, branch and point type names stay the administrator's Ukrainian from the JSON, as designed |
| node width 200 -> 176 | the 44-unit gap between columns gives the lines room; a single cost shows as "8 anomaly_field_t1", several as "10 + 4" with the names on the card |
