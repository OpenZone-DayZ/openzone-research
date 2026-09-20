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
