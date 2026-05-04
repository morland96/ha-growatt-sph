"""Sensor definitions for SPH devices accessed via the classic mobile API.

The keys here mirror the response shape of `sph_system_status`,
`sph_energy_overview`, and `sph_settings` (newTwoSphAPI.do), which is
distinct from the V1 OpenAPI's sph_detail/sph_energy response — hence
the separate set.
"""

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
)

from .sensor_entity_description import GrowattSensorEntityDescription

SPH_CLASSIC_SENSOR_TYPES: tuple[GrowattSensorEntityDescription, ...] = (
    # --- Battery ---
    GrowattSensorEntityDescription(
        key="sph_soc",
        translation_key="mix_statement_of_charge",
        api_key="SOC",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
    ),
    GrowattSensorEntityDescription(
        key="sph_battery_voltage",
        translation_key="mix_battery_voltage",
        api_key="vBat",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
    ),
    GrowattSensorEntityDescription(
        key="sph_battery_charge_kw",
        translation_key="mix_battery_charge",
        api_key="pCharge1",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    GrowattSensorEntityDescription(
        key="sph_battery_discharge_kw",
        translation_key="mix_battery_discharge_w",
        api_key="pDisCharge1",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    # --- PV ---
    GrowattSensorEntityDescription(
        key="sph_pv_power",
        translation_key="mix_wattage_pv_all",
        api_key="ppv",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    GrowattSensorEntityDescription(
        key="sph_pv1_voltage",
        translation_key="mix_pv1_voltage",
        api_key="vpv1",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
    ),
    GrowattSensorEntityDescription(
        key="sph_pv2_voltage",
        translation_key="mix_pv2_voltage",
        api_key="vpv2",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
    ),

    # --- Grid ---
    GrowattSensorEntityDescription(
        key="sph_grid_voltage",
        translation_key="mix_grid_voltage",
        api_key="vAc1",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
    ),
    GrowattSensorEntityDescription(
        key="sph_grid_frequency",
        translation_key="sph_grid_frequency",
        api_key="fAc",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
    ),
    GrowattSensorEntityDescription(
        key="sph_export_to_grid",
        translation_key="mix_export_to_grid",
        api_key="pacToGrid",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    GrowattSensorEntityDescription(
        key="sph_import_from_grid",
        translation_key="mix_import_from_grid",
        api_key="pacToUser",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    # --- Load ---
    GrowattSensorEntityDescription(
        key="sph_local_load",
        translation_key="mix_load_consumption",
        api_key="pLocalLoad",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    # --- Energy totals (from sph_energy_overview) ---
    GrowattSensorEntityDescription(
        key="sph_solar_energy_today",
        translation_key="mix_solar_generation_today",
        api_key="epvToday",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    GrowattSensorEntityDescription(
        key="sph_solar_energy_total",
        translation_key="mix_solar_generation_lifetime",
        api_key="epvTotal",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        never_resets=True,
    ),
    GrowattSensorEntityDescription(
        key="sph_battery_charged_today",
        translation_key="mix_battery_charge_today",
        api_key="eChargeToday",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    GrowattSensorEntityDescription(
        key="sph_battery_charged_total",
        translation_key="mix_battery_charge_lifetime",
        api_key="eChargeTotal",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        never_resets=True,
    ),
    GrowattSensorEntityDescription(
        key="sph_battery_discharged_today",
        translation_key="mix_battery_discharge_today",
        api_key="eDisChargeToday",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    GrowattSensorEntityDescription(
        key="sph_battery_discharged_total",
        translation_key="mix_battery_discharge_lifetime",
        api_key="eDisChargeTotal",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        never_resets=True,
    ),
    GrowattSensorEntityDescription(
        key="sph_local_load_today",
        translation_key="mix_load_consumption_today",
        api_key="elocalLoadToday",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    GrowattSensorEntityDescription(
        key="sph_local_load_total",
        translation_key="mix_load_consumption_lifetime",
        api_key="elocalLoadTotal",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        never_resets=True,
    ),
    GrowattSensorEntityDescription(
        key="sph_export_to_grid_today",
        translation_key="mix_export_to_grid_today",
        api_key="eToGridToday",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    GrowattSensorEntityDescription(
        key="sph_export_to_grid_total",
        translation_key="mix_export_to_grid_lifetime",
        api_key="eToGridTotal",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        never_resets=True,
    ),

    # --- Settings (diagnostic, read-only) ---------------------------
    # Exposed so values are visible in HA. To change them use the
    # `growatt_server.set_sph_parameter` service.
    GrowattSensorEntityDescription(
        key="sph_setting_sys_work_mode",
        name="System work mode",
        api_key="sys_work_mode",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    GrowattSensorEntityDescription(
        key="sph_setting_pv_on_off",
        name="PV output enabled",
        api_key="pv_on_off",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    GrowattSensorEntityDescription(
        key="sph_setting_cutoff_soc",
        name="Discharge cutoff SoC",
        api_key="cutoff_soc",
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    GrowattSensorEntityDescription(
        key="sph_setting_cuton_soc",
        name="Charge cutoff SoC",
        api_key="cuton_soc",
        native_unit_of_measurement=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    GrowattSensorEntityDescription(
        key="sph_setting_bat_max_charge_current",
        name="Battery max charge current",
        api_key="bat_max_charge_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    GrowattSensorEntityDescription(
        key="sph_setting_bat_max_discharge_current",
        name="Battery max discharge current",
        api_key="bat_max_discharge_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    GrowattSensorEntityDescription(
        key="sph_setting_zero_ct_sell",
        name="Zero export at CT",
        api_key="zero_ct_sell",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    GrowattSensorEntityDescription(
        key="sph_setting_zero_load_sell",
        name="Zero export at load meter",
        api_key="zero_load_sell",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)
