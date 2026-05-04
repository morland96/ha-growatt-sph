# growatt_server (custom override)

A drop-in replacement for the bundled Home Assistant `growatt_server`
integration that adds support for newer SPH/SPM hybrid inverters
(e.g. SPM-10000TL-HU) which the upstream version cannot read because:

- The legacy mix_*/tlx_*/storage_* endpoints return null/zero for these
  models.
- The V1 OpenAPI's sph_* endpoints return errors because V1's
  device_list omits the device entirely.

This component routes `device_type=='sph' && api_version=='classic'`
through the new `newTwoSphAPI.do` path on the regional mobile host —
the same surface the ShinePhone app uses. V1-token configurations are
unchanged.

## Install

1. Install the patched library into your HA Python environment:

       pip install \
         git+https://github.com/morland96/PyPi_GrowattServer.git@feature/regional-mobile-sph-support

2. Copy `custom_components/growatt_server/` into your HA config
   directory at `<config>/custom_components/growatt_server/`.

3. Restart Home Assistant. The custom component takes precedence over
   the core one because it has the same `domain`.

4. Add the integration normally (Settings → Devices & Services → Add).
   Pick the regional host that matches your account — for SPH-classic
   users in Australia / NZ, choose **Australia / New Zealand**, which
   maps to `openapi-au.growatt.com`. That host serves the new SPH
   endpoints just as well as `server-au-api.growatt.com`.

## Changes vs upstream

- `manifest.json` — pins `growattServer==2.1.0`, marks integration as
  custom (renamed display name + version stamp + new codeowner).
- `coordinator.py` — branches the SPH handler on `api_version`. V1
  path unchanged; classic path calls `sph_system_status()` +
  `sph_energy_overview()` from the patched library.
  (Also fixes a pre-existing `except A, B:` syntax bug at line 502.)
- `sensor/sph_classic.py` (new) — 22 sensor descriptions matching the
  field names returned by the classic-mode SPH endpoints (`SOC`,
  `vBat`, `pDisCharge1`, etc.).
- `sensor/__init__.py` — when device is SPH, picks
  `SPH_SENSOR_TYPES` (V1) or `SPH_CLASSIC_SENSOR_TYPES` based on
  `coordinator.api_version`.

No other files differ from upstream.
