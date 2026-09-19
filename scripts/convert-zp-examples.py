#!/usr/bin/env python3
"""Convert a ZP_Research example pack into OpenZone Research config files.

    python scripts/convert-zp-examples.py <zp-pack-dir> <out-dir>

Reads Factions.json, PointTypes.json, DataItems.json, Modules.json,
SampleTypes.json, ProcessingRules/*.json, TechTree/*.json and (if present)
StaticDevices.json, and writes OZ_Research_*.json with the OZL_ class names,
one file per entity. Faction ids are kept as they are: the ones the core's
registry knows become live, the others sleep until such a faction exists.
Bools are written as 1/0, the way the engine writes them itself.
"""
import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CORE_OWNERS = {"ecolog", "duty", "freedom", "bandit", "loner", "neutral", "mercenary", "military", "monolith"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def dump(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=4) + "\n", encoding="utf-8", newline="\n")


def cls(name: str) -> str:
    """ZP_ -> OZL_ in a class name, keeping a `|1` suffix."""
    return name.replace("ZP_", "OZL_") if isinstance(name, str) else name


def flag(v) -> int:
    return 1 if v in (1, True, "1", "true") else 0


def convert(src: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    report: list[str] = []

    # --- owners (was Factions)
    f = load(src / "Factions.json")
    owners = []
    dormant = []
    for d in f.get("Factions", []):
        oid = d.get("Id", "")
        if oid not in CORE_OWNERS:
            dormant.append(oid)
        bg = d.get("TreeBackgroundImage", "") or ""
        bg = bg.replace("ZP_Research/gui/textures", "OpenZone_Research/gui/textures")
        owners.append({
            "Id": oid,
            "TerminalClasses": [cls(x) for x in d.get("TerminalClasses", [])],
            "DeviceClasses": [cls(x) for x in d.get("DeviceClasses", [])],
            "TreeBackground": bg,
        })
    dump(out / "OZ_Research_Owners.json", {"Version": 1, "Owners": owners})
    report.append(f"owners: {len(owners)} (dropped Armbands, DisplayName, Supertype; dormant ids: {dormant or 'none'})")

    # --- point types
    p = load(src / "PointTypes.json")
    dump(out / "OZ_Research_PointTypes.json", {
        "Version": 1,
        "PointTypes": [{k: t.get(k, "" if k not in ("SortOrder", "Tier") else 0)
                        for k in ("Id", "Name", "Icon", "Color", "SortOrder", "Category", "Kind", "Tier")}
                       for t in p.get("PointTypes", [])],
        "Categories": [{k: c.get(k, "" if k != "SortOrder" else 0) for k in ("Id", "Name", "SortOrder")} for c in p.get("Categories", [])],
        "Kinds": [{k: c.get(k, "" if k != "SortOrder" else 0) for k in ("Id", "Name", "SortOrder")} for c in p.get("Kinds", [])],
    })
    report.append(f"point types: {len(p.get('PointTypes', []))}")

    # --- rules: one group per former file
    groups = []
    nrules = 0
    dropped_mode = 0
    for rf in sorted((src / "ProcessingRules").glob("*.json")):
        d = load(rf)
        rules = []
        for r in d.get("Rules", []):
            if "Mode" in r:
                dropped_mode += 1
            inp = r.get("InputItem", {}) or {}
            rules.append({
                "Id": r.get("Id", ""),
                "Enabled": flag(r.get("Enabled", 1)),
                "Device": cls(r.get("Device", "")),
                "InputItem": {
                    "Classname": cls(inp.get("Classname", "")),
                    "Quantity": inp.get("Quantity", 1),
                    "ConsumeInput": flag(inp.get("ConsumeInput", 1)),
                    "Content": inp.get("Content", ""),
                    "RequireFullQuantity": flag(inp.get("RequireFullQuantity", 0)),
                },
                "BasePurityMin": r.get("BasePurityMin", 0.5),
                "BasePurityMax": r.get("BasePurityMax", 0.5),
                "TimeSec": r.get("TimeSec", 10),
                "Consumables": [{"Classname": cls(c.get("Classname", "")), "Quantity": c.get("Quantity", 1), "Content": c.get("Content", "")}
                                for c in r.get("Consumables", [])],
                "Outputs": [{"Classname": cls(o.get("Classname", "")), "Quantity": o.get("Quantity", 1), "Chance": o.get("Chance", 1.0), "Content": o.get("Content", "")}
                            for o in r.get("Outputs", [])],
                "RequiredNode": r.get("RequiredNode", ""),
                "RequiredFactions": list(r.get("RequiredFactions", [])),
                "RequiredWorn": [cls(x) for x in r.get("RequiredWorn", [])],
                "RequiredTools": [cls(x) for x in r.get("RequiredTools", [])],
                "Notes": r.get("Notes", ""),
            })
        groups.append({"Id": rf.stem, "Rules": rules})
        nrules += len(rules)
    dump(out / "OZ_Research_Rules.json", {"Version": 1, "Groups": groups})
    report.append(f"rules: {nrules} in {len(groups)} group(s) (dropped the Mode field on {dropped_mode})")

    # --- tree: one branch per former file
    branches = []
    nnodes = 0
    for tf in sorted((src / "TechTree").glob("*.json")):
        d = load(tf)
        b = d.get("Branch", {}) or {}
        nodes = []
        for n in d.get("Nodes", []):
            nodes.append({
                "Id": n.get("Id", ""),
                "Name": n.get("Name", ""),
                "Description": n.get("Description", ""),
                "Icon": n.get("Icon", ""),
                "Tier": n.get("Tier", 1),
                "Parents": list(n.get("Parents", [])),
                "ParentsMode": n.get("ParentsMode", "all"),
                "Cost": [{"Type": c.get("Type", ""), "Amount": c.get("Amount", 0)} for c in n.get("Cost", [])],
                "ItemCost": [{"Classname": cls(c.get("Classname", "")), "Quantity": c.get("Quantity", 1), "Content": c.get("Content", "")}
                             for c in n.get("ItemCost", [])],
                "ResearchTimeSec": n.get("ResearchTimeSec", 0),
                "RequiredFactions": list(n.get("RequiredFactions", [])),
            })
        branches.append({
            "Id": b.get("Id", tf.stem),
            "Name": b.get("Name", ""),
            "Icon": b.get("Icon", ""),
            "SortOrder": b.get("SortOrder", 0),
            "Owners": list(b.get("Factions", [])),
            "Nodes": nodes,
        })
        nnodes += len(nodes)
    dump(out / "OZ_Research_Tree.json", {"Version": 1, "Branches": branches})
    report.append(f"tree: {nnodes} node(s) in {len(branches)} branch(es)")

    # --- data items, modules, sample types
    d = load(src / "DataItems.json")
    dump(out / "OZ_Research_DataItems.json", {"Version": 1, "Items": [
        {"Id": cls(i.get("Id", "")), "Enabled": flag(i.get("Enabled", 1)), "Name": i.get("Name", ""), "Description": i.get("Description", ""),
         "Points": [{"Type": r.get("Type", ""), "Amount": r.get("Amount", 0)} for r in i.get("Points", [])]}
        for i in d.get("Items", [])]})
    report.append(f"data items: {len(d.get('Items', []))}")

    m = load(src / "Modules.json")
    dump(out / "OZ_Research_Modules.json", {"Version": 1, "Modules": [
        {"Classname": cls(x.get("Classname", "")), "PurityBonus": x.get("PurityBonus", 0), "Devices": [cls(y) for y in x.get("Devices", [])], "Notes": x.get("Notes", "")}
        for x in m.get("Modules", [])]})
    report.append(f"modules: {len(m.get('Modules', []))}")

    s = load(src / "SampleTypes.json")
    dump(out / "OZ_Research_SampleTypes.json", {"Version": 1, "Items": [
        {"Id": cls(i.get("Id", "")), "Enabled": flag(i.get("Enabled", 1)), "Name": i.get("Name", ""), "Description": i.get("Description", "")}
        for i in s.get("Items", [])]})
    report.append(f"sample types: {len(s.get('Items', []))}")

    # --- statics (optional in the pack)
    entries = []
    sd = src / "StaticDevices.json"
    if sd.exists():
        for e in load(sd).get("Entries", []):
            entries.append({"Id": e.get("Id", ""), "ClassName": cls(e.get("Classname", "")), "Pos": list(e.get("Pos", [])), "Yaw": e.get("Yaw", 0), "Note": e.get("Notes", "")})
    dump(out / "OZ_Research_Statics.json", {"Version": 1, "Entries": entries})
    report.append(f"statics: {len(entries)}")

    print("\n".join(report))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    args = ap.parse_args()
    convert(Path(args.src), Path(args.out))


if __name__ == "__main__":
    main()
