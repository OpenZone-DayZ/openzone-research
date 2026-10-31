# examples

Starter packs of configuration for `$profile:OpenZone\`. Copy the six
`OZ_Research_*.json` files of a pack into the server's profile folder; the mod
creates the settings file, and any other missing file, with defaults on its first start.

- `full/` -- seven factions (ecolog, clearsky, bandit, neutral, duty, freedom, sop),
  each with its own packers, analyzers and terminal. 1039 packer rules turn raw items
  into the samples of their line, worth 1, 5 or 25 points for common, rare and legendary
  input; 16 analyzer rules turn samples into carriers. The tree costs line points: a node
  of the first row costs 4-6, of the fifth 205-450.
- `test-stand/` -- the stand pack: all 39 stations in one line along the strip of the
  north-west airfield of Chernarus, faction after faction, each
  packer with two rules on vanilla items (a plain one worth 1 point, and one showing the
  options: 25 points, the line's first module required, purity 0.5), every analyzer with
  its rule, ten seconds a cycle, two cheap nodes per faction. This is what the `dayz` MCP
  stand of this repository runs.

Both packs use the faction `sop`, which is not among the factions mod's defaults: add it
to `OZ_Factions.json`. A player outside an organisation belongs to the base faction
`stalker`, and neither pack lists devices for it.

Every faction of both packs names its own tree window in `OZ_Research_Owners.json`
(`"Skin"`: the faction's own id). The packs name no tree backdrop (`TreeBackground`), so each
window draws its own.
