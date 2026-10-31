# Model generators

*[Українською](README.ua.md)*

Every station, sample, carrier and module model of OpenZone Research is built by a Blender
script, `source/models/<obj>/scripts/build_mNN.py`, with the shared kit in `source/models/_kit`.

## Requirements

- Blender 5.2 (the models were built with 5.2.3; 5.2.0 builds the same geometry)
- DayZ Tools (ImageToPAA) and the unpacked game data: a P: drive with `dz`
- the Windows fonts the decals use: Arial, Impact, Consolas, Courier New, Lucida Console,
  Segoe Print, Segoe Script, Ink Free, Comic Sans, Bahnschrift
- Python 3 with Pillow for the `make_decals.py` scripts

Copy `settings.example.json` to `settings.local.json` and set the paths.

## Rebuilding a model

    cd source/models/<obj>/scripts
    python make_decals.py                      # if the model has one
    blender --background --python build_mNN.py -- --skip-bake --no-paa   # MLOD, rvmat, model.cfg
    blender --background --python build_mNN.py                           # full build with baking

The MLOD goes to `build/model-root/OpenZone_Research/models/<obj>/`; `model.cfg` to
`OpenZone_Research/models/<obj>/`, the rvmats and PAA textures to its `data/`; renders, baked
PNGs and `install.json` to `source/models/<obj>/work/`. Then, with the dayz MCP open on this
repository:

    asset_build(mod="OpenZone_Research", source="models/<obj>")
    asset_check(mod="OpenZone_Research")
    mod_build()

`model=`, `hiddenSelections`, `AnimationSources` and `class OZL_Work` in `config.cpp` are edited
by hand when a model changes its selections or animations; the generator leaves
`work/install.json` with the values.

## Reproducible builds

Blender's Python hashes strings with a random seed, and the atlas layout of some models follows
the order of such sets. Two builds of the same model can then place parts differently in the
atlas: the geometry, the LODs, the selections and the points stay the same, the UVs of the near
LOD do not (measured on M01 and M75; M47 came out byte-identical). With a fixed seed every build
of a model writes the same MLOD: set `PYTHONHASHSEED=0` in the environment and start Blender with
`--python-use-system-env`, without which it ignores the variable.

The textures in the mod were baked with a random seed, so an MLOD-only build (`--skip-bake`) of
such a model does not match them: rebuild it with baking.

The table of models (model, class, line, role) is at the end of this file.

## Models

| Model | Class | Line | Role |
|---|---|---|---|
| M01 | `OZL_Eco_Pack_Bio` | bio | packer |
| M02 | `OZL_Eco_Proc_Bio` | bio | analyzer |
| M03 | `OZL_Eco_Pack_Anom` | anomaly | packer |
| M04 | `OZL_Eco_Proc_Anom` | anomaly | analyzer |
| M05 | `OZL_Eco_Pack_Electro` | electronics | packer |
| M06 | `OZL_Eco_Proc_Electro` | electronics | analyzer |
| M07 | `OZL_Sky_Pack_Bio` | bio | packer |
| M08 | `OZL_Sky_Proc_Bio` | bio | analyzer |
| M09 | `OZL_Sky_Pack_Anom` | anomaly | packer |
| M10 | `OZL_Sky_Proc_Anom` | anomaly | analyzer |
| M11 | `OZL_Sky_Pack_Electro` | electronics | packer |
| M12 | `OZL_Sky_Proc_Electro` | electronics | analyzer |
| M13 | `OZL_Bnd_Pack_Khabar` | khabar | packer |
| M14 | `OZL_Bnd_Proc_Khabar` | khabar | analyzer |
| M15 | `OZL_Bnd_Pack_Trail` | trails | packer |
| M16 | `OZL_Bnd_Proc_Trail` | trails | analyzer |
| M17 | `OZL_Bnd_Terminal` | - | terminal |
| M18 | `OZL_Lnr_Pack_Khabar` | khabar | packer |
| M19 | `OZL_Lnr_Proc_Khabar` | khabar | analyzer |
| M20 | `OZL_Lnr_Pack_Trail` | trails | packer |
| M21 | `OZL_Lnr_Proc_Trail` | trails | analyzer |
| M22 | `OZL_Lnr_Terminal` | - | terminal |
| M23 | `OZL_Dty_Pack_Ball` | ballistics | packer |
| M24 | `OZL_Dty_Proc_Ball` | ballistics | analyzer |
| M25 | `OZL_Dty_Pack_Prot` | protection | packer |
| M26 | `OZL_Dty_Proc_Prot` | protection | analyzer |
| M27 | `OZL_Frd_Pack_Ball` | ballistics | packer |
| M28 | `OZL_Frd_Proc_Ball` | ballistics | analyzer |
| M29 | `OZL_Frd_Pack_Prot` | protection | packer |
| M30 | `OZL_Frd_Proc_Prot` | protection | analyzer |
| M31 | `OZL_Frd_Terminal` | - | terminal |
| M32 | `OZL_Sop_Pack_Ball` | ballistics | packer |
| M33 | `OZL_Sop_Proc_Ball` | ballistics | analyzer |
| M34 | `OZL_Sop_Pack_Prot` | protection | packer |
| M35 | `OZL_Sop_Proc_Prot` | protection | analyzer |
| M36 | `OZL_Sop_Terminal` | - | terminal |
| M38 | `OZL_Eco_Terminal` | - | terminal |
| M44 | `OZL_Tool_Optics` | bio | module, slot 1 |
| M45 | `OZL_Tool_Centrifuge` | bio | module, slot 2 |
| M46 | `OZL_Tool_Reagents` | bio | module, slot 3 |
| M47 | `OZL_Sample_Bio` | bio | sample |
| M48 | `OZL_Sample_Anom` | anomaly | sample |
| M49 | `OZL_Sample_Electro` | electronics | sample |
| M50 | `OZL_Sample_Khabar` | khabar | sample |
| M51 | `OZL_Sample_Trail` | trails | sample |
| M52 | `OZL_Sample_Ball` | ballistics | sample |
| M53 | `OZL_Sample_Prot` | protection | sample |
| M60 | `OZL_Sky_Terminal` | - | terminal |
| M61 | `OZL_Dty_Terminal` | - | terminal |
| M62 | `OZL_Carrier_Bio` | bio | carrier |
| M63 | `OZL_Carrier_Anom` | anomaly | carrier |
| M64 | `OZL_Carrier_Electro` | electronics | carrier |
| M65 | `OZL_Carrier_Khabar` | khabar | carrier |
| M66 | `OZL_Carrier_Trail` | trails | carrier |
| M67 | `OZL_Carrier_Ball` | ballistics | carrier |
| M68 | `OZL_Carrier_Prot` | protection | carrier |
| M69 | `OZL_Tool_AnomProbe` | anomaly | module, slot 1 |
| M70 | `OZL_Tool_Radiometer` | anomaly | module, slot 2 |
| M71 | `OZL_Tool_LeadShield` | anomaly | module, slot 3 |
| M72 | `OZL_Tool_Oscilloscope` | electronics | module, slot 1 |
| M73 | `OZL_Tool_SolderStation` | electronics | module, slot 2 |
| M74 | `OZL_Tool_Programmer` | electronics | module, slot 3 |
| M75 | `OZL_Tool_Dosimeter` | khabar | module, slot 1 |
| M76 | `OZL_Tool_JewelerLoupe` | khabar | module, slot 2 |
| M77 | `OZL_Tool_LeadCapsule` | khabar | module, slot 3 |
| M78 | `OZL_Tool_PdaReader` | trails | module, slot 1 |
| M79 | `OZL_Tool_RadioScanner` | trails | module, slot 2 |
| M80 | `OZL_Tool_MapBoard` | trails | module, slot 3 |
| M81 | `OZL_Tool_BarrelVise` | ballistics | module, slot 1 |
| M82 | `OZL_Tool_Borescope` | ballistics | module, slot 2 |
| M83 | `OZL_Tool_GaugeSet` | ballistics | module, slot 3 |
| M84 | `OZL_Tool_Compressor` | protection | module, slot 1 |
| M85 | `OZL_Tool_GasAnalyzer` | protection | module, slot 2 |
| M86 | `OZL_Tool_PlateClamp` | protection | module, slot 3 |
