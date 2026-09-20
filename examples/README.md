# examples

Starter packs of configuration for `$profile:OpenZone\`. Copy the nine
`OZ_Research_*.json` files of a pack into the server's profile folder; the mod
creates any missing file with defaults on its first start.

- `zone-protocol/` -- the seven-faction pack of the [UA] STALKER: Zone Protocol
  server, converted from the `ZP_Research` examples by
  `scripts/convert-zp-examples.py`. Its owners are the core's faction ids; the
  branches and rules of `clearsky` and `sop` keep those ids and stay dormant
  until such factions exist in the core's registry.

The tree background textures the pack refers to
(`OpenZone_Research/gui/textures/tree/*.paa`) ship inside the mod.

- `test-stand/` -- the stand pack: vanilla inputs only, so every rule is live on a
  server without the modpack; a few static stations placed for the test stand.
  This is what the `dayz` MCP stand of this repository runs.
  Completed by hand after conversion: every faction of the core's registry
  has an owner entry, the five ZP factions with their own device sets and the
  other four (neutral, mercenary, military, monolith) and loner with the generic lab
  (microscope, lab computer, sample fridge), so a test account of any faction
  can run the `pb_*` chain and research the `pb_nauka` branch; the four static entries with a class that does
  not exist or a duplicate position are gone.
