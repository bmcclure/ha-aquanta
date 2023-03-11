"""Aquanta sensor component."""
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    TEMP_CELSIUS,
    PERCENTAGE,
    PRECISION_WHOLE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, AquantaCoordinator, AquantaEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize Aquanta devices from config entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        AquantaWaterHeaterTemperatureSensor(coordinator, aquanta_id)
        for aquanta_id in coordinator.data["devices"]
    )
    async_add_entities(
        AquantaWaterHeaterSetPointSensor(coordinator, aquanta_id)
        for aquanta_id in coordinator.data["devices"]
    )
    async_add_entities(
        AquantaWaterHeaterWaterAvailableSensor(coordinator, aquanta_id)
        for aquanta_id in coordinator.data["devices"]
    )
    async_add_entities(
        AquantaWaterHeaterCurrentModeSensor(coordinator, aquanta_id)
        for aquanta_id in coordinator.data["devices"]
    )


class AquantaWaterHeaterTemperatureSensor(AquantaEntity, SensorEntity):
    """Represents a temperature for an Aquanta water heater controller."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_has_entity_name = True
    _attr_icon = "mdi:water-thermometer"

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id += "_current_temperature"

    @property
    def name(self):
        return "Temperature"

    @property
    def precision(self):
        """Defines the precision of the value."""
        return PRECISION_WHOLE

    @property
    def native_value(self):
        return self.coordinator.data["devices"][self._id]["water"]["temperature"]


class AquantaWaterHeaterSetPointSensor(AquantaEntity, SensorEntity):
    """Represents the set point for an Aquanta water heater controller."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = TEMP_CELSIUS
    _attr_icon = "mdi:thermometer-water"
    _attr_has_entity_name = True

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id += "_set_point"

    @property
    def name(self):
        return "Set point"

    @property
    def precision(self):
        """Defines the precision of the value."""
        return PRECISION_WHOLE

    @property
    def native_value(self):
        if self.coordinator.data["devices"][self._id]["advanced"]["thermostatEnabled"]:
            return self.coordinator.data["devices"][self._id]["advanced"]["setPoint"]
        else:
            return None


class AquantaWaterHeaterWaterAvailableSensor(AquantaEntity, SensorEntity):
    """Represents the available water for an Aquanta water heater controller."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:water-percent"
    _attr_has_entity_name = True
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id += "_hot_water_available"

    @property
    def name(self):
        return "Hot water available"

    @property
    def native_value(self):
        return self.coordinator.data["devices"][self._id]["water"]["available"] * 100

    @property
    def icon(self):
        return "mdi:percent"


class AquantaWaterHeaterCurrentModeSensor(AquantaEntity, SensorEntity):
    """Represents the current mode the Aquanta device is in."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_icon = "mdi:water-sync"
    _attr_options = [
        "setpoint",
        "intelligence",
        "boost",
        "away",
        "off",
    ]

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id += "_current_mode"

    @property
    def name(self):
        return "Mode"

    @property
    def native_value(self):
        return self.coordinator.data["devices"][self._id]["info"]["currentMode"]["type"]
