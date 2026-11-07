# examples

Starter packs of configuration for `$profile:OpenZone\`. Copy the six
`OZ_Research_*.json` files of a pack into the server's profile folder; the mod
creates the settings file, and any other missing file, with defaults on its first start.

`example` is also what the mod ships: the same six files sit in
`OpenZone_Research/defaults` and go into the pbo, and a research config the profile does
not have yet is written from there. Change both copies together.

Both packs take vanilla items only, so they load with no rule disabled on a server that
runs no item mods.

- `example/` -- seven factions (ecolog, clearsky, bandit, neutral, duty, freedom, sop),
  each with its own packers, analyzers and terminal. 131 packer rules turn vanilla items
  into the samples of their line, worth 1, 5 or 25 points for common, rare and legendary
  input; 16 analyzer rules turn samples into carriers. The tree costs line points: a node
  of the first row costs 4-6, of the fifth 205-450. No stations are placed: the
  administrator puts them in `OZ_Research_Statics.json`.
- `test-stand/` -- the stand pack: all 39 stations in one line along the strip of the
  north-west airfield of Chernarus, faction after faction, each
  packer with two rules on vanilla items (a plain one worth 1 point, which takes the
  line's base purity, 0.7, and one showing the options: 25 points, the line's first
  module required, a purity of its own, 0.5), every analyzer with
  its rule, ten seconds a cycle, two cheap nodes per faction. This is what the `dayz` MCP
  stand of this repository runs.

Both packs use the faction `sop`, which is not among the factions mod's defaults: add it
to `OZ_Factions.json`. A player outside an organisation belongs to the base faction
`stalker`, and neither pack lists devices for it.

Every faction of both packs names its own tree window in `OZ_Research_Owners.json`
(`"Skin"`: the faction's own id).

In both packs a rule's `Purity` of -1 takes the `BasePurity` of its line from
`OZ_Research_PointTypes.json`; a `Purity` of 0 or no key does the same, and a `BasePurity`
of 0 or no key is 0.7.
