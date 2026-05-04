# Growatt (with SPH classic support)

A drop-in replacement for Home Assistant's bundled `growatt_server`
integration that adds support for newer SPH/SPM hybrid inverters
(e.g. **SPM-10000TL-HU**) which the upstream version cannot read because:

- The legacy `mix_*`/`tlx_*`/`storage_*` endpoints return null/zero for
  these models.
- The V1 OpenAPI's `sph_*` endpoints fail because V1's `device_list`
  omits the device entirely.

This component routes `device_type=='sph' && api_version=='classic'`
through the new `newTwoSphAPI.do` path on the regional mobile host —
the same surface ShinePhone uses. V1-token configurations are
unchanged.

## Install via HACS (recommended)

1. In HACS, click the three-dot menu → **Custom repositories**.
2. Add `https://github.com/morland96/ha-growatt-sph` as type
   **Integration**.
3. Install the entry that appears, then restart Home Assistant.
4. Add the integration normally: **Settings → Devices & Services →
   Add Integration → Growatt**. Use the **Username/Password** flow.
   Pick the regional host that matches your account — for AU users,
   **Australia / New Zealand** (= `openapi-au.growatt.com`) serves the
   new SPH endpoints just as well as `server-au-api.growatt.com`.

The patched `growattServer` library is pulled in automatically by
Home Assistant via the manifest.

## Install manually

1. Copy `custom_components/growatt_server/` from this repo into your
   HA config directory at `<config>/custom_components/growatt_server/`.
2. Restart Home Assistant — the custom component takes precedence over
   the core one because they share the `growatt_server` domain.
3. Configure as above.

## Changes vs upstream HA core

- `manifest.json` — installs the patched library directly from this
  fork: `growattServer @ git+https://github.com/morland96/PyPi_GrowattServer.git@v2.1.0+sph-classic.1`.
- `coordinator.py` — branches the SPH handler on `api_version`.
  V1 path unchanged; classic path calls `sph_system_status()` and
  `sph_energy_overview()` from the patched library.
- `sensor/sph_classic.py` *(new)* — 22 sensor descriptions matching
  the field names returned by the classic-mode SPH endpoints (`SOC`,
  `vBat`, `pDisCharge1`, energy totals, etc.).
- `sensor/__init__.py` — when device type is SPH, picks
  `SPH_SENSOR_TYPES` (V1) or `SPH_CLASSIC_SENSOR_TYPES` based on
  `coordinator.api_version`.

All other files are identical to upstream.

## Library

The patched library lives at
[morland96/PyPi_GrowattServer](https://github.com/morland96/PyPi_GrowattServer)
on the `feature/regional-mobile-sph-support` branch (tagged
`v2.1.0+sph-classic.1`). Adds five `sph_*` methods on `GrowattApi`:
`sph_system_status`, `sph_energy_overview`, `sph_energy_prod_and_cons`,
`sph_settings`, `update_sph_inverter_setting`.

## License

Same as Home Assistant: Apache-2.0.
