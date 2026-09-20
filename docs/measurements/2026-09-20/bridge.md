# The research kind of the bridge on the stand (2026-09-20)

The full-stack retail stand (`E:\dayzmod\testserver`, `verifySignatures=2`,
the core's bridge client polling `http://127.0.0.1:8787/`) against the Node
bridge with `RESEARCH_DIR=E:\dayzmod\testserver\profiles\OpenZone`. Mod at
`f32538f` plus the respawn refusal below; bridge at `62fb03e`..`51f4634`.
Everything below is read out of the two logs and the CLI's own timing.

## Boot

| What | Measured |
|---|---|
| class dump at start | `classes: 11602 written`, `research\xchg\classes.txt` 275 786 bytes |
| boot letter answer | `v1/research/boot ok, 52 b` |
| bridge on boot | `9 configs (9 new versions), 11602 classes, revision 1` the first time; `0 new versions` on every later boot with unchanged files |
| ready line | `... problems=0 identity=present bridge=on` |
| verdict with the bridge up | pass, 0 warnings, counters as declared |

## Boot before the bridge knew the kind

With the old bridge on 8787 (no research routes) the boot letter gets HTTP
404, which the engine reports as `EREST_ERROR` (code 5). Every failed call
flips the core's "bridge answers" latch, so a retry every 5 s cost two core
lines per attempt: `WARNING: bridge: v1/research/boot failed, code 5` and
`bridge: answering again`. Measured on the first build: 16 attempts in a
few minutes. The mod now retries with a doubling pause (5 s .. 5 min) and
writes one line of its own per reason change:

```
bridge: boot refused (code 5), retrying with a pause of 5 s doubling up to 300 s
```

Second build, same bridge: 2 core warnings in the first minute, then the
gaps grow. The verdict of such a run fails on the core's warnings, which is
right: a bridge without the kind is a deployment error worth a fail.

## Hello

The bridge was restarted with the research kind while the game kept
running. The game's first poll after the restart carried `{op:"hello"}`,
the game answered with the boot letter at once:

```
bridge: hello from the bridge, sending boot
dbg: bridge: v1/research/boot ok, 52 b
bridge: boot accepted, revision 1
```

No server restart was needed to bring the kind up. The poll failures while
the bridge was down arrived as code 7 (`EREST_ERROR_SERVERERROR`), recorded
in the skill.

## A config edit through the CLI

`get ResearchOwners --out owners.json`, one class added to the loner's
`DeviceClasses`, `put ResearchOwners owners-edited.json`:

```
candidate ResearchOwners.687cff16439d.json: version 2 pending, token 687cff16439d
answer: ok warnings=0 problems=0
ResearchOwners: version 2 applied
```

| What | Measured |
|---|---|
| put to the game's answer, as seen by the CLI | 1.33 s (the CLI asks for the result once a second, so the true latency is under that; the push wakes the held poll at once) |
| poll item carrying `cfg_apply` | `v1/poll ok, 198 b` |
| the game | `config ResearchOwners replaced, revision 2`, `bridge: cfg_apply by covalschi done warnings=0 problems=0` |
| the bridge | `ResearchOwners changed by bridge:covalschi: version 2 (the candidate applied), revision 2` |
| exchange directory after | `classes.txt` only: the game deleted the candidate |
| history | version 2 applied by `covalschi`, source `admin`; version 1 by `game` |

The game rewrites the file in its own formatting; the canonical hash
(sorted keys) still matched the candidate, so the pending version was
promoted and no second version appeared.

## Refusals

| Case | Result |
|---|---|
| `put` of text that is not json | the CLI refuses (`save: not json: ...`), no file, no command, exit 1 |
| `put` with `Version: 99` | the game refuses `version 99 is newer than this build knows`; version 3 `rejected` with that reason; `ResearchOwners.f857c0edde10.json` stays in `xchg` for the admin; the game logs one WARNING pair |
| `grant nobody bio_field_t1 3` | accepted by the game, which creates `research\nobody.json`: the game's grant takes any path-safe owner, as the VPP pane does. The web will offer owners from the config, so a typo is unlikely there; the file was removed by hand |
| `respawn zps_207684159` with the static standing | `STR_OZL_ERR_SPAWN_FAILED` on the first build, from the spawner's "already stands there, marked as spawned" path; now its own refusal `STR_OZL_ERR_STATIC_STANDS`, and the id is marked spawned |

## Live commands

Each through the CLI, each answered `ok` within 1.2 s as the CLI sees it:

| Command | Effect |
|---|---|
| `grant loner bio_field_t1 3` | pool 12 -> 15, `admin bridge:covalschi: owner 'loner' granted 3 bio_field_t1` |
| `complete mercenary pb_osnovy` | node completed for the owner |
| `reset mercenary` | `owner 'mercenary' reset: 0 station(s) stopped`, the file now holds an empty pool |
| `reload` | `configs reloaded, revision 3`, then nine `changed` letters (10 in the log with the apply's one), 0 new versions on the bridge |

## The queue across restarts

1. Server stopped. `grant loner bio_field_t1 1` queued on the bridge
   (token `0c47030a975f`, status `sent`).
2. Bridge restarted: the in-memory queue is gone, the row is not.
3. Server started with a fresh build. Its first poll (`Fresh`) carried the
   command straight into its items: bridge `stand: 1 unanswered command(s)
   re-sent`, game `bridge: grant by covalschi done`, pool 15 -> 16, then the
   boot letter (`0 new versions`).
4. `result 0c47030a975f`: `grant by covalschi: ok (2026-09-20 02:58:29)`.

A server's first poll skips the shared push queue, which is why the re-send
rides that poll's own items (research-routes.js, `poll`).

## The stand verb

`world_exec verb=oz_research args={"op":"bridge"}` after the restart:
`enabled=true up=true booted=true letters=3 answered=2 last=c7262405ed7d`.

## Traps met on the way

- `process.exit()` right after a `fetch` aborts Node 24 on Windows with a
  libuv assertion (`async.c:76`, `UV_HANDLE_CLOSING`) and exit code 127,
  the answer already printed. Both CLIs now leave through `process.exitCode`.
- A Bash `printf` turned `\t` in a Windows path into a tab inside `.env`;
  the bridge said `no such directory: E:\dayzmod<TAB>estserver...`. The
  line was rewritten from PowerShell.
