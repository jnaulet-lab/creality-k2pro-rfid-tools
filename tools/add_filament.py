#!/usr/bin/env python3
# Copyright (c) 2026 jnaulet-lab
# MIT License - see LICENSE and LICENSES/MIT.txt in the repository.
"""
add_filament.py - add filaments to the Creality K2 Pro catalog (material_database.json)
from filament presets exported by Creality Print.
Ajoute des filaments au catalogue de la K2 Pro (material_database.json) à partir
de préréglages exportés depuis Creality Print.

For each preset the script:
  1. finds the matching generic entry (via the preset's "inherits", e.g. "Generic PLA @Creality K2 Pro 0.4 nozzle"),
  2. copies it, then sets a new id, the brand (filament_vendor), a readable name, rank, min/max temperatures
     and the base density taken from the preset,
  3. overlays the preset values onto the entry's kvParam (only keys that already exist there),
  4. updates result.count and raises result.version by at least 1 on every change (the CFS RFID app
     only downloads the catalog again when the version has changed),
  5. saves a timestamped backup of the original file before writing.

Usage / Utilisation:
  python add_filament.py material_database.json eSun_PLA-Basic.json Sunlu_PETG-Basic.json
  python add_filament.py material_database.json my_preset.json --id 90010 --dry-run
  python add_filament.py material_database.json my_preset.json --out new_database.json

Use at your own risk and keep your own backup / À utiliser à tes risques, garde ta propre sauvegarde.
"""
import argparse
import copy
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_VERSION = 9876543210   # very large on purpose / volontairement très grand
DEFAULT_RANK = 3000            # sort order of the new entries / ordre de tri des nouvelles entrées
FIRST_CUSTOM_ID = 90001        # custom ids start here, outside the Creality range / plage hors Creality
IGNORED_PRESET_KEYS = {"base_id", "filament_settings_id", "from", "name", "version"}


def first(value):
    """Presets store values as one-item lists: ["60"] -> "60"."""
    if isinstance(value, list):
        return value[0] if len(value) == 1 else None
    return value


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def is_generic(entry):
    return entry["base"].get("brand") == "Generic" and "userMaterial" not in entry


def find_generic(entries, preset):
    """Find the generic entry the preset is based on."""
    inherits = first(preset.get("inherits")) or ""
    wanted = inherits.split(" @")[0].strip()          # "Generic PLA @Creality ..." -> "Generic PLA"
    generics = [e for e in entries if is_generic(e)]
    for e in generics:
        if e["base"]["name"].lower() == wanted.lower():
            return e
    names = ", ".join(sorted(e["base"]["name"] for e in generics))
    raise ValueError(f'no generic entry matches inherits="{inherits}". Available: {names}')


def next_custom_id(entries):
    used = [int(e["base"]["id"]) for e in entries
            if str(e["base"]["id"]).isdigit() and int(e["base"]["id"]) >= FIRST_CUSTOM_ID - 1]
    return str(max(used) + 1) if used else str(FIRST_CUSTOM_ID)


def build_entry(generic, preset, new_id, rank):
    entry = copy.deepcopy(generic)
    entry.pop("userMaterial", None)
    kv = entry["kvParam"]
    warnings = []

    for key, raw in preset.items():
        if key in IGNORED_PRESET_KEYS:
            continue
        value = first(raw)
        if value is None:
            warnings.append(f"skipped multi-valued key: {key}")
        elif key in kv:
            kv[key] = str(value)
        else:
            warnings.append(f"skipped unknown key (not in catalog entries): {key}")

    settings_id = first(preset.get("filament_settings_id")) or preset.get("name")
    vendor = first(preset.get("filament_vendor"))
    if not settings_id or not vendor:
        raise ValueError("preset needs 'filament_settings_id' (or 'name') and 'filament_vendor'")

    base = entry["base"]
    base["id"] = new_id
    base["brand"] = vendor
    base["name"] = settings_id.replace("_", " ")
    base["rank"] = rank
    low = first(preset.get("nozzle_temperature_range_low"))
    high = first(preset.get("nozzle_temperature_range_high"))
    if low:
        base["minTemp"] = int(float(low))
    if high:
        base["maxTemp"] = int(float(high))
    density = first(kv.get("filament_density"))
    if density:
        base["density"] = float(density)      # keep base and kvParam consistent
    return entry, warnings


def write_json(path, data, trailing_newline):
    text = json.dumps(data, indent=2, separators=(",", ":"), ensure_ascii=False)
    if trailing_newline:
        text += "\n"
    json.loads(text)                           # sanity check: output must be valid JSON
    Path(path).write_text(text, encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("database", help="material_database.json")
    p.add_argument("presets", nargs="+", help="filament presets exported from Creality Print (.json)")
    p.add_argument("--id", help="id for the new entry (only with a single preset); default: next free id from 90001")
    p.add_argument("--rank", type=int, default=DEFAULT_RANK, help=f"sort order (default {DEFAULT_RANK})")
    p.add_argument("--version", type=int, default=DEFAULT_VERSION,
                   help=f"minimum catalog version (default {DEFAULT_VERSION}); on every change the version is also raised by 1 over the current one, never lowered")
    p.add_argument("--replace", action="store_true", help="replace an existing entry with the same brand and name")
    p.add_argument("--out", help="write to this file instead of modifying the database in place")
    p.add_argument("--dry-run", action="store_true", help="show what would change, write nothing")
    args = p.parse_args()

    if args.id and len(args.presets) > 1:
        p.error("--id can only be used with a single preset")

    db_path = Path(args.database)
    trailing_newline = db_path.read_text(encoding="utf-8").endswith("\n")   # keep the original file style
    data = load_json(db_path)
    result = data["result"]
    entries = result["list"]
    added = []

    for preset_path in args.presets:
        preset = load_json(preset_path)
        try:
            generic = find_generic(entries, preset)
            existing = None
            vendor = first(preset.get("filament_vendor"))
            name = (first(preset.get("filament_settings_id")) or preset.get("name", "")).replace("_", " ")
            for i, e in enumerate(entries):
                if is_generic(e) or "userMaterial" in e:
                    continue
                if e["base"]["brand"] == vendor and e["base"]["name"] == name:
                    existing = i
            if existing is not None and not args.replace:
                print(f"[skip] {preset_path}: '{vendor} / {name}' already in the catalog (use --replace)")
                continue
            if existing is not None:
                new_id = entries[existing]["base"]["id"]
            else:
                new_id = args.id or next_custom_id(entries)
                if any(e["base"]["id"] == new_id and not is_generic(e) and "userMaterial" not in e
                       for e in entries):
                    raise ValueError(f"id {new_id} is already used")
            entry, warnings = build_entry(generic, preset, new_id, args.rank)
        except (ValueError, KeyError) as exc:
            print(f"[error] {preset_path}: {exc}", file=sys.stderr)
            sys.exit(1)

        if existing is not None:
            entries[existing] = entry
        else:
            entries.append(entry)
        b = entry["base"]
        print(f"[{'replace' if existing is not None else 'add'}] id {b['id']} | {b['brand']} | {b['name']} | "
              f"{b['meterialType']} | {b['minTemp']}-{b['maxTemp']} C")
        for w in warnings:
            print(f"        warning: {w}")
        added.append(new_id)

    if not added:
        print("Nothing to do.")
        return

    result["count"] = len(entries)
    current = str(result.get("version", ""))
    bumped = int(current) + 1 if current.isdigit() else 0     # always different from the previous version
    result["version"] = str(max(bumped, args.version))
    print(f"count = {result['count']} | version = {result['version']}")

    if args.dry_run:
        print("Dry run: nothing written.")
        return

    target = Path(args.out) if args.out else db_path
    if not args.out:
        backup = db_path.with_name(f"{db_path.name}.bak-{datetime.now():%Y%m%d-%H%M%S}")
        shutil.copy2(db_path, backup)
        print(f"Backup saved: {backup}")
    write_json(target, data, trailing_newline)
    print(f"Written: {target}")


if __name__ == "__main__":
    main()
