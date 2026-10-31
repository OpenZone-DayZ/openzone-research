# Генератори моделей

*[In English](README.md)*

Кожну модель станції, проби, носія й модуля OpenZone Research будує скрипт Blender,
`source/models/<obj>/scripts/build_mNN.py`, на спільному наборі `source/models/_kit`.

## Потрібно

- Blender 5.2 (моделі зібрано в 5.2.3; 5.2.0 будує ту саму геометрію)
- DayZ Tools (ImageToPAA) і розпаковані дані гри: диск P: з `dz`
- шрифти Windows, якими пишуться декалі: Arial, Impact, Consolas, Courier New, Lucida Console,
  Segoe Print, Segoe Script, Ink Free, Comic Sans, Bahnschrift
- Python 3 з Pillow для скриптів `make_decals.py`

Скопіюйте `settings.example.json` у `settings.local.json` і впишіть шляхи.

## Перезбирання моделі

    cd source/models/<obj>/scripts
    python make_decals.py                      # якщо в моделі він є
    blender --background --python build_mNN.py -- --skip-bake --no-paa   # MLOD, rvmat, model.cfg
    blender --background --python build_mNN.py                           # повна збірка із запіканням

MLOD лягає в `build/model-root/OpenZone_Research/models/<obj>/`; `model.cfg` -- в
`OpenZone_Research/models/<obj>/`, rvmat і текстури PAA -- в його `data/`; рендери, запечені
PNG і `install.json` -- в `source/models/<obj>/work/`. Далі, з MCP dayz, відкритим на цьому
репозиторії:

    asset_build(mod="OpenZone_Research", source="models/<obj>")
    asset_check(mod="OpenZone_Research")
    mod_build()

`model=`, `hiddenSelections`, `AnimationSources` і `class OZL_Work` у `config.cpp` правляться
руками, коли модель міняє вибірки чи анімації; генератор лишає значення в
`work/install.json`.

## Відтворювані збірки

Python у Blender хешує рядки з випадковим зерном, а розкладка атласу деяких моделей іде за
порядком таких множин. Тоді дві збірки однієї моделі можуть покласти частини в атлас
по-різному: геометрія, LOD, вибірки й точки ті самі, UV ближнього LOD -- ні (виміряно на M01 і
M75; M47 вийшла байт у байт). З фіксованим зерном кожна збірка моделі пише той самий MLOD:
задайте `PYTHONHASHSEED=0` у середовищі й запустіть Blender з `--python-use-system-env`, без
якого він змінну ігнорує.

Текстури в моді запечено з випадковим зерном, тож збірка лише MLOD (`--skip-bake`) такої
моделі з ними не збігається: перезбирайте її із запіканням.

Таблиця моделей (модель, клас, лінія, роль) -- наприкінці цього файлу.

## Моделі

| Модель | Клас | Лінія | Роль |
|---|---|---|---|
| M01 | `OZL_Eco_Pack_Bio` | bio | пакувальник |
| M02 | `OZL_Eco_Proc_Bio` | bio | аналізатор |
| M03 | `OZL_Eco_Pack_Anom` | anomaly | пакувальник |
| M04 | `OZL_Eco_Proc_Anom` | anomaly | аналізатор |
| M05 | `OZL_Eco_Pack_Electro` | electronics | пакувальник |
| M06 | `OZL_Eco_Proc_Electro` | electronics | аналізатор |
| M07 | `OZL_Sky_Pack_Bio` | bio | пакувальник |
| M08 | `OZL_Sky_Proc_Bio` | bio | аналізатор |
| M09 | `OZL_Sky_Pack_Anom` | anomaly | пакувальник |
| M10 | `OZL_Sky_Proc_Anom` | anomaly | аналізатор |
| M11 | `OZL_Sky_Pack_Electro` | electronics | пакувальник |
| M12 | `OZL_Sky_Proc_Electro` | electronics | аналізатор |
| M13 | `OZL_Bnd_Pack_Khabar` | khabar | пакувальник |
| M14 | `OZL_Bnd_Proc_Khabar` | khabar | аналізатор |
| M15 | `OZL_Bnd_Pack_Trail` | trails | пакувальник |
| M16 | `OZL_Bnd_Proc_Trail` | trails | аналізатор |
| M17 | `OZL_Bnd_Terminal` | - | термінал |
| M18 | `OZL_Lnr_Pack_Khabar` | khabar | пакувальник |
| M19 | `OZL_Lnr_Proc_Khabar` | khabar | аналізатор |
| M20 | `OZL_Lnr_Pack_Trail` | trails | пакувальник |
| M21 | `OZL_Lnr_Proc_Trail` | trails | аналізатор |
| M22 | `OZL_Lnr_Terminal` | - | термінал |
| M23 | `OZL_Dty_Pack_Ball` | ballistics | пакувальник |
| M24 | `OZL_Dty_Proc_Ball` | ballistics | аналізатор |
| M25 | `OZL_Dty_Pack_Prot` | protection | пакувальник |
| M26 | `OZL_Dty_Proc_Prot` | protection | аналізатор |
| M27 | `OZL_Frd_Pack_Ball` | ballistics | пакувальник |
| M28 | `OZL_Frd_Proc_Ball` | ballistics | аналізатор |
| M29 | `OZL_Frd_Pack_Prot` | protection | пакувальник |
| M30 | `OZL_Frd_Proc_Prot` | protection | аналізатор |
| M31 | `OZL_Frd_Terminal` | - | термінал |
| M32 | `OZL_Sop_Pack_Ball` | ballistics | пакувальник |
| M33 | `OZL_Sop_Proc_Ball` | ballistics | аналізатор |
| M34 | `OZL_Sop_Pack_Prot` | protection | пакувальник |
| M35 | `OZL_Sop_Proc_Prot` | protection | аналізатор |
| M36 | `OZL_Sop_Terminal` | - | термінал |
| M38 | `OZL_Eco_Terminal` | - | термінал |
| M44 | `OZL_Tool_Optics` | bio | модуль, слот 1 |
| M45 | `OZL_Tool_Centrifuge` | bio | модуль, слот 2 |
| M46 | `OZL_Tool_Reagents` | bio | модуль, слот 3 |
| M47 | `OZL_Sample_Bio` | bio | проба |
| M48 | `OZL_Sample_Anom` | anomaly | проба |
| M49 | `OZL_Sample_Electro` | electronics | проба |
| M50 | `OZL_Sample_Khabar` | khabar | проба |
| M51 | `OZL_Sample_Trail` | trails | проба |
| M52 | `OZL_Sample_Ball` | ballistics | проба |
| M53 | `OZL_Sample_Prot` | protection | проба |
| M60 | `OZL_Sky_Terminal` | - | термінал |
| M61 | `OZL_Dty_Terminal` | - | термінал |
| M62 | `OZL_Carrier_Bio` | bio | носій |
| M63 | `OZL_Carrier_Anom` | anomaly | носій |
| M64 | `OZL_Carrier_Electro` | electronics | носій |
| M65 | `OZL_Carrier_Khabar` | khabar | носій |
| M66 | `OZL_Carrier_Trail` | trails | носій |
| M67 | `OZL_Carrier_Ball` | ballistics | носій |
| M68 | `OZL_Carrier_Prot` | protection | носій |
| M69 | `OZL_Tool_AnomProbe` | anomaly | модуль, слот 1 |
| M70 | `OZL_Tool_Radiometer` | anomaly | модуль, слот 2 |
| M71 | `OZL_Tool_LeadShield` | anomaly | модуль, слот 3 |
| M72 | `OZL_Tool_Oscilloscope` | electronics | модуль, слот 1 |
| M73 | `OZL_Tool_SolderStation` | electronics | модуль, слот 2 |
| M74 | `OZL_Tool_Programmer` | electronics | модуль, слот 3 |
| M75 | `OZL_Tool_Dosimeter` | khabar | модуль, слот 1 |
| M76 | `OZL_Tool_JewelerLoupe` | khabar | модуль, слот 2 |
| M77 | `OZL_Tool_LeadCapsule` | khabar | модуль, слот 3 |
| M78 | `OZL_Tool_PdaReader` | trails | модуль, слот 1 |
| M79 | `OZL_Tool_RadioScanner` | trails | модуль, слот 2 |
| M80 | `OZL_Tool_MapBoard` | trails | модуль, слот 3 |
| M81 | `OZL_Tool_BarrelVise` | ballistics | модуль, слот 1 |
| M82 | `OZL_Tool_Borescope` | ballistics | модуль, слот 2 |
| M83 | `OZL_Tool_GaugeSet` | ballistics | модуль, слот 3 |
| M84 | `OZL_Tool_Compressor` | protection | модуль, слот 1 |
| M85 | `OZL_Tool_GasAnalyzer` | protection | модуль, слот 2 |
| M86 | `OZL_Tool_PlateClamp` | protection | модуль, слот 3 |
