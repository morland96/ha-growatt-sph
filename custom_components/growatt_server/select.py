"""Select platform for Growatt — currently only used for SPH classic-mode controls."""

from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GrowattConfigEntry, GrowattCoordinator

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1


# sys_work_mode value mappings observed on SPM-10000TL-HU (Australian
# market). Confirmed in-field: 1 = On Grid Mode, 2 = Export Limit to
# Backup Load, 3 = Export Limit to Home Load.
SYS_WORK_MODE_OPTIONS = {
    "On Grid Mode": 1,
    "Export Limit to Backup Load": 2,
    "Export Limit to Home Load": 3,
}
SYS_WORK_MODE_REVERSE = {v: k for k, v in SYS_WORK_MODE_OPTIONS.items()}


@dataclass(frozen=True, kw_only=True)
class GrowattSelectEntityDescription(SelectEntityDescription):
    """Describes a Growatt select entity."""

    api_key: str
    write_key: str | None = None
    options_map: dict[str, int] | None = None


SPH_CLASSIC_SELECT_TYPES: tuple[GrowattSelectEntityDescription, ...] = (
    GrowattSelectEntityDescription(
        key="sph_sys_work_mode",
        name="System work mode",
        api_key="sys_work_mode",
        options=list(SYS_WORK_MODE_OPTIONS.keys()),
        options_map=SYS_WORK_MODE_OPTIONS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GrowattConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Growatt select entities."""
    runtime_data = entry.runtime_data
    async_add_entities(
        GrowattSelect(device_coordinator, description)
        for device_coordinator in runtime_data.devices.values()
        if (
            device_coordinator.device_type == "sph"
            and device_coordinator.api_version == "classic"
        )
        for description in SPH_CLASSIC_SELECT_TYPES
    )


class GrowattSelect(CoordinatorEntity[GrowattCoordinator], SelectEntity):
    """Representation of a Growatt select entity."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG
    entity_description: GrowattSelectEntityDescription

    def __init__(
        self,
        coordinator: GrowattCoordinator,
        description: GrowattSelectEntityDescription,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device_id)},
            manufacturer="Growatt",
            name=coordinator.device_id,
            serial_number=coordinator.device_id,
        )

    @property
    def current_option(self) -> str | None:
        """Return the current option label."""
        raw = self.coordinator.data.get(self.entity_description.api_key)
        if raw is None:
            return None
        try:
            value = int(raw)
        except (TypeError, ValueError):
            return None
        # Reverse-map the integer to the label. If the device reports a
        # value we don't have a label for, expose it as a numeric string
        # so the user can see it (rather than silently going None).
        if self.entity_description.api_key == "sys_work_mode":
            return SYS_WORK_MODE_REVERSE.get(value, f"Unknown ({value})")
        return None

    async def async_select_option(self, option: str) -> None:
        """Set the option."""
        if (
            self.entity_description.options_map is None
            or option not in self.entity_description.options_map
        ):
            raise HomeAssistantError(f"Unsupported option: {option}")
        api_value = self.entity_description.options_map[option]
        parameter_id = (
            self.entity_description.write_key or self.entity_description.api_key
        )
        try:
            await self.hass.async_add_executor_job(
                self.coordinator.api.update_sph_inverter_setting,
                self.coordinator.device_id,
                parameter_id,
                api_value,
            )
        except Exception as exc:  # noqa: BLE001
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="api_error",
                translation_placeholders={"error": str(exc)},
            ) from exc
        _LOGGER.debug("Set %s to %s (%d)", parameter_id, option, api_value)
        self.coordinator.data[self.entity_description.api_key] = api_value
        self.async_write_ha_state()
