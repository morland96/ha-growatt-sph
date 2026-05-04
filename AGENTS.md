# AGENTS.md — Growatt SPH for Home Assistant

You're an AI agent picking up this project. Read this before diving in. It tells you what's here, why each piece exists, and the small set of gotchas that will trip you up.

## What this project is

A Home Assistant integration that supports newer Growatt **SPH/SPM hybrid inverters** (e.g. **SPM-10000TL-HU**) that the bundled HA `growatt_server` integration cannot read because:

- Legacy `mix_*`/`tlx_*`/`storage_*` endpoints return null/zero for these devices.
- The V1 OpenAPI's `sph_*` methods fail because V1's `device_list` omits them.

The fix uses a **regional mobile-API host** (`server-{region}-api.growatt.com`, equivalently `openapi-{region}.growatt.com`) and the `newTwoSphAPI.do` / `newTwoDeviceAPI.do` endpoints that the ShinePhone app uses. Same `newTwoLoginAPI.do` auth flow as the existing library.

## Workspace layout (`/Users/morland/Projects/growatt/`)

```
PyPi_GrowattServer/      Fork of indykoning/PyPi_GrowattServer.
                         origin = morland96/PyPi_GrowattServer
                         upstream = indykoning/PyPi_GrowattServer
                         Branches:
                           master                                (tracks upstream)
                           feature/regional-mobile-sph-support   (PR-clean, base)
                           feature/sph-all-params                (extends w/ sph_all_params)
                         Tags:
                           v2.1.0+sph-classic.2     (PR tip)
                           v2.1.0+sph-all-params.1  (all-params tip — what HA installs)

ha_repo/                 The HA custom integration repo.
                         origin = morland96/ha-growatt-sph (public, HACS-installable)
                         Branch: main
                         Latest commit: ed5d412 Add missing PV3 voltage sensor

custom_components/       Local working copy of growatt_server/ — edit here, sync to ha_repo/
                         to commit and push.

ha_core_reference/       Pristine sparse-checkout of HA core's growatt_server/ at upstream/dev.
                         Useful for `diff -ruN` to see exactly what we changed.

ha_core_fork/            Sparse-checkout of the user's HA core fork (morland96/core).
                         Used once for the now-closed except-syntax PR.

probe/                   Exploration scripts.
                         .venv/ has the patched library installed editable.
                         .env (gitignored) holds GROWATT_USERNAME, _PASSWORD,
                              _PLANT_ID, _SPH_SN, _API_TOKEN.
                         Active probes: probe_lib_unified.py (smoke test),
                              probe_regional_mobile.py, probe_sph_chart.py,
                              probe_sph_write.py.
                         Old probes live in _archive/.
```

## Quick commands

**Test the library against the user's account**
```bash
cd /Users/morland/Projects/growatt/probe
set -a; source .env; set +a
.venv/bin/python probe_lib_unified.py
```

**Reinstall the library after fork edits**
```bash
cd /Users/morland/Projects/growatt/probe
.venv/bin/pip install -q --force-reinstall --no-deps -e ../PyPi_GrowattServer
```

**Sync custom_components → ha_repo and push**
```bash
cp -r /Users/morland/Projects/growatt/custom_components/growatt_server/. \
      /Users/morland/Projects/growatt/ha_repo/custom_components/growatt_server/
rm -rf /Users/morland/Projects/growatt/ha_repo/custom_components/growatt_server/__pycache__ \
       /Users/morland/Projects/growatt/ha_repo/custom_components/growatt_server/sensor/__pycache__
cd /Users/morland/Projects/growatt/ha_repo
git add -A
git status --short    # ALWAYS verify before committing — see "translations path" gotcha
git commit -m "..."
git push origin main
```

**Tag a new library version**
```bash
cd /Users/morland/Projects/growatt/PyPi_GrowattServer
git tag v2.1.0+sph-XXX HEAD
git push origin v2.1.0+sph-XXX
# Update manifest.json in custom_components to point at the new tag.
```

## Style conventions

- **Commits**: short imperative title matching HA-core style (e.g. `"Fix invalid except syntax in growatt_server coordinator"`). Body explains *why* in 2-4 sentences. **NEVER** include `Co-Authored-By: Claude...` lines — the user has explicitly asked for this multiple times.
- **Entity descriptions**: prefer `translation_key="..."` over `name="..."`. Add the actual label string under `entity.<platform>.<key>.name` in `strings.json` and mirror to `translations/en.json`.
- **Lifetime sensors over today sensors**: explain to the user that lifetime sensors are preferred for HA's Energy dashboard (no midnight-bounce edge case). Both still get exposed.
- **Unit handling**: power values from `sph_system_status` are kW (strings); from `sph_all_params` are W (then unit-stripped to numbers). Coordinator's `_all_params_overlapped()` does W→kW.

## Architecture cheatsheet

```
HA polling cycle (configurable; defaults: fast=5min, slow=5min, source=Standard):

  every fast-tick:
    api.sph_system_status(plant_id, sph_sn)            # live snapshot

  every slow-tick:
    api.sph_energy_overview(plant_id, sph_sn)          # daily/lifetime kWh
    api.sph_settings(sph_sn)                           # 149 adjustable params
    api.sph_all_params(sph_sn)                         # detailed snapshot (always)
    if source == standard:
      api.sph_energy_prod_and_cons(...chart_type=0)    # today's grid import
      api.sph_energy_prod_and_cons(...chart_type=3)    # lifetime grid import

  always:
    detailed-only fields (temps, currents, etc.) ← sph_all_params
    overlapped fields (SOC, ppv, pacToGrid, etc.) ← source-picked endpoint
```

## Known gotchas

### 1. translations/en.json path
When syncing files between `custom_components/` and `ha_repo/`, **always** include the `translations/` segment in the destination path or use `cp -r .../growatt_server/.` to recursively sync the whole tree. I've made the mistake several times of `cp .../translations/en.json .../growatt_server/` — that drops the file at the component root. Verify with `git status --short` before committing; if you see `?? .../growatt_server/en.json`, that's the bug.

### 2. strings.json [%key:%] cross-references
HA core's `strings.json` uses `[%key:component::DOMAIN::a::b%]` references that the build pipeline inlines at release. Custom integrations don't run that pipeline. Resolve them before shipping `translations/en.json` — see `probe/resolve_translations.py`.

### 3. Python 3.14 unparenthesized except
HA core's dev branch uses `except A, B:` syntax (PEP 758, Python 3.14+). My local Python is 3.12 so `python3 -m py_compile coordinator.py` fails on those lines. **Don't** "fix" it — that syntax is valid on HA's runtime. Test syntax of files I edit only.

### 4. Date passed to chart endpoints
`sph_energy_prod_and_cons` is timezone-sensitive: server interprets the date in plant local time. Coordinator passes `dt_util.now().date()` (HA's TZ) explicitly. The library default is now system-local (was UTC before — fixed in v2.1.0+sph-classic.2).

### 5. Entity_id locking
HA preserves entity_ids across renames. If translations weren't loaded at first creation, entity_ids fell back to device-class names with `_2`/`_3` suffixes (e.g. `sensor.hcq2f8b058_voltage_2`). The user can rename via Settings → Entities → gear icon. Don't change `key=` on existing entries unless asked — that breaks unique_ids and orphans the old entities.

### 6. mqy_bs@hotmail.com is the test account
The probe's `.env` holds real credentials for plant `2778270` / SPH `HCQ2F8B058` in Bentleigh East, Australia. Don't paste these into commits or memory. The user is willing to let you make controlled toggles (sys_work_mode, energy_mode) but **always restore the original value** in a `try/finally` block.

## Library API surface (post-our-changes)

### `feature/regional-mobile-sph-support` (PR-clean)
```python
api.sph_system_status(plant_id, sph_sn)        # live snapshot, ~39 fields
api.sph_energy_overview(plant_id, sph_sn)      # daily + lifetime kWh totals
api.sph_energy_prod_and_cons(plant_id, sph_sn,
    date=None,                                  # defaults to system-local today
    chart_type=0|1|2|3)                        # day | month | year | all-time
api.sph_settings(sph_sn)                       # all 149 adjustable params
api.update_sph_inverter_setting(sn, type, params)  # write any setting
```

### `feature/sph-all-params` (extends above; current installed branch)
```python
api.sph_all_params(sph_sn, language=1, strip_units=True)
# Returns nested dict: {battery, solar, grid, inverter, load, sphType}
# Auto strips unit suffixes ("53.1V" → 53.1, "1.0kWh" → 1.0)
# New fields not in sph_system_status:
#   battery: bmsBatteryTemp, bmsBatteryCurr, spStatus, version
#   solar:   ipv1, ipv2, ipv3 (per-string currents)
#   grid:    etoUserToday, etoUserTotal (cleaner than chart endpoint)
#   inverter: dcTemp, invTemp, epsIac1, upsPac1
#   load:    rLoadVol
```

## HA integration entity inventory

**Platforms**: `number`, `select`, `sensor`, `switch`. Defined in `const.py:PLATFORMS`.

**SPH classic-mode sensors** (`sensor/sph_classic.py`): ~40 entries covering battery (SoC, voltage, charge/discharge kW + kWh), PV (per-string voltages and powers, total, lifetime/today kWh), grid (voltage, frequency, in/out kW + kWh), load, settings (diagnostic), and detailed-mode-only fields (temperatures, per-string currents, inverter output, load voltage).

**SPH classic-mode switches** (`switch.py`):
- `sph_pv_sell_back_home` ↔ `zero_ct_sell`
- `sph_pv_sell_back_backup` ↔ `zero_load_sell`
- *(polarity is direct, despite "zero_*_sell" name — value 1 means sell-back enabled)*

**SPH classic-mode numbers** (`number.py`):
- `sph_max_sell_power` ↔ `psell_max` (W, NumberDeviceClass.POWER, 0–15000 step 100)

**SPH classic-mode selects** (`select.py`):
- `sph_sys_work_mode` ↔ `sys_work_mode` — three options:
  - On Grid Mode = 1
  - Export Limit to Backup Load = 2
  - Export Limit to Home Load = 3
- `sph_pv_priority` ↔ `energy_mode` — two options:
  - Battery First = 0
  - Load First = 1

**Service**: `growatt_server.set_sph_parameter(device_id, setting, value)` for arbitrary writes against the 149-parameter setting bean.

**Options flow** (`config_flow.py:GrowattServerOptionsFlow`):
- `scan_interval_minutes` (1–60, default 5) — fast cadence
- `slow_scan_interval_minutes` (1–60, default 5) — slow cadence
- `sph_data_source` (standard | detailed) — overlapped-field source picker

## When the user asks something hardware-specific

The user has SPM-10000TL-HU in Australia. Plant `2778270`, SN `HCQ2F8B058`, datalogger `VWQ0F480U8`, GMT+10. They have a battery (lifetime ~509 kWh charged, 365 kWh discharged) and a non-zero export configuration. Use this context when interpreting numbers.

## Closing notes from previous sessions

- The user clearly prefers terse, action-first responses. Don't over-explain.
- Tasks are tracked one-shot; we don't keep a running task list.
- The user expects every change to be pushed to `ha_repo` immediately so they can pull via HACS and test in HA.
- The user has explicitly asked NOT to mention "Claude Code" or include `Co-Authored-By: Claude` lines in commits.
- Commit messages should mirror upstream HA core style (terse imperative).
- The PR to upstream HA core (`fix-growatt-server-except-syntax`) was a false alarm — the original syntax is valid on Python 3.14. The PR should be closed; we offered the user that option but didn't close it ourselves.
