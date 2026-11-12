# Option A: Spoolman via SpoolmanSync

[Version française](README.fr.md) · [Back to the main guide](../../README.md)

Keep **Spoolman** in sync with your printer: filament usage is tracked and the right Spoolman spool is assigned automatically to the CFS slot that reads a tag.

> **Choose A or B, not both.** This option shares helpers, sensors, a utility meter and an automation id with [option B (stock in Home Assistant)](../stock-ha/README.md). Install only one of them.
>
> **Status:** this option was validated by the author, who then moved to option B because the chain was too complex and too sensitive to updates. It is no longer the author's running setup.

## How it works
1. The integration exposes one sensor per CFS slot (`sensor.k2pro_creality_cfs_box_1_slot_1_filament`, ...) with attributes such as `vendor`, `type`, `color_hex`, `rfid`, `spool_key` and `selected`.
2. Two SpoolmanSync automations track the active slot and the filament length used (cm) and send it to SpoolmanSync.
3. A third automation **assigns the Spoolman spool to the slot** when a tag is read: it looks in Spoolman for non-archived spools with the **same vendor, material and color** as the tag. If several match, it picks the spool already started with the least filament left, otherwise the first one.

### Matching rule (important)
In Spoolman:
- the **vendor name** must equal the brand written on the tag (e.g. `eSun`), case-insensitive. **For the external spool slot the vendor is optional**, which helps with a spool without a tag;
- the **material** must equal the filament type (e.g. `PLA`);
- the **color hex** must equal the color written on the tag (without `#`, case-insensitive).

## Tested with
Home Assistant OS 18.5, Creality WebSocket Integration ([ha_creality_ws](https://github.com/3dg1luk43/ha_creality_ws)) 0.9.10, [Spoolman](https://github.com/Donkie/Spoolman) 0.27.0 (port 7912 by default) and [SpoolmanSync](https://github.com/gibz104/SpoolmanSync) 1.6.14 (port 3000 by default).

## Installation
1. Install and configure Spoolman and SpoolmanSync, and add your printer in SpoolmanSync.
2. Add the blocks of [`configuration_extrait.yaml`](configuration_extrait.yaml) to your `configuration.yaml`. Replace `k2pro_creality` with the entity prefix of your printer, and the placeholder addresses `SPOOLMANSYNC_IP` and `SPOOLMAN_IP` with yours (often the same machine). Merge with your existing `template:`, `input_number:` and `utility_meter:` blocks instead of duplicating them.
3. Put your SpoolmanSync webhook token in `secrets.yaml` (see [`secrets.example.yaml`](secrets.example.yaml)). **Never publish your real token.**
4. Add the three automations of [`automations_extrait.yaml`](automations_extrait.yaml) to your `automations.yaml` (or recreate them in the interface with "Edit in YAML"). In the last one, set `printer_ip` to your printer's IP address.
5. Restart Home Assistant.
6. **Test first:** `dry_run` is `true` by default, so the automation only sends a notification saying which spool it *would* assign. Insert a tagged spool, check the notification, then set `dry_run: false`.

## Good to know
- **Slot indexing:** SpoolmanSync counts slots from 0, while the CFS sensors are numbered from 1. The assignment automation writes `slot_<n-1>`: CFS slot 1 becomes `slot_0`.
- **External spool:** it is supported by the automatic assignment (sensor `cfs_external_filament`). The vendor is optional for this slot; the material and the color are required.
- **Several identical spools:** when several Spoolman spools share the same vendor, material and color, the automation picks the one already started with the least filament left. This is a heuristic, not a certainty: the `spool_key` attribute of the sensors matches the brand and the color, **not** a unique tag number, so Home Assistant cannot tell two identical spools apart.
- If no spool matches, a persistent notification asks you to assign it manually in SpoolmanSync.
- The entity names keep their `spoolmansync_*` prefix: they match the configuration that was actually tested.

## Troubleshooting
- **The spool of slot 2 shows up on slot 3 (and so on):** this is the index offset described above. Use the current `automations_extrait.yaml`, which writes `slot_<n-1>`.
- **Nothing is assigned:** check that `dry_run` is set to `false`, then check that a non-archived Spoolman spool has the same material and color (and the same vendor, except for the external slot).

## Files
| File | Role |
|---|---|
| `configuration_extrait.yaml` | Helper, utility meter, REST commands to SpoolmanSync and Spoolman, sensors |
| `automations_extrait.yaml` | Usage update, tray change and automatic assignment |
| `secrets.example.yaml` | Template for the SpoolmanSync token |
