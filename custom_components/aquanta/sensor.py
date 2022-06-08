"""Aquanta sensor component."""
from homeassistant.components.sensor import (
    DEVICE_CLASS_TEMPERATURE,
    STATE_CLASS_MEASUREMENT,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS, PERCENTAGE, PRECISION_WHOLE
from homeassistant.core import HomeAssistant
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
    async_add_entities(
        AquantaWaterHeaterControlEnabledSensor(coordinator, aquanta_id)
        for aquanta_id in coordinator.data["devices"]
    )
    async_add_entities(
        AquantaWaterHeaterIntelligenceEnabledSensor(coordinator, aquanta_id)
        for aquanta_id in coordinator.data["devices"]
    )
    async_add_entities(
        AquantaWaterHeaterThermostatEnabledSensor(coordinator, aquanta_id)
        for aquanta_id in coordinator.data["devices"]
    )
    async_add_entities(
        AquantaWaterHeaterTimeOfUseEnabledSensor(coordinator, aquanta_id)
        for aquanta_id in coordinator.data["devices"]
    )
    async_add_entities(
        AquantaWaterHeaterTimerEnabledSensor(coordinator, aquanta_id)
        for aquanta_id in coordinator.data["devices"]
    )


class AquantaWaterHeaterTemperatureSensor(AquantaEntity, SensorEntity):
    """Represents a temperature for an Aquanta water heater controller."""

    entity_description: SensorEntityDescription(
        key="current_temperature",
        device_class=DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
        native_unit_of_measurement=TEMP_CELSIUS,
    )

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id = f"{self._attr_unique_id}_current_temperature"

    @property
    def name(self) -> str | None:
        return f"{self.device_name()} Current Temperature"

    @property
    def precision(self):
        """Defines the precision of the value."""
        return PRECISION_WHOLE

    @property
    def native_value(self):
        return self.coordinator.data["devices"][self._id]["water"]["temperature"]


class AquantaWaterHeaterSetPointSensor(AquantaEntity, SensorEntity):
    """Represents the set point for an Aquanta water heater controller."""

    entity_description: SensorEntityDescription(
        key="set_point",
        device_class=DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
        native_unit_of_measurement=TEMP_CELSIUS,
    )

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id = f"{self._attr_unique_id}_set_point"

    @property
    def name(self) -> str | None:
        return f"{self.device_name()} Set Point"

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

    entity_description: SensorEntityDescription(
        key="hot_water_available",
        device_class="hot_water_available",
        state_class=STATE_CLASS_MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    )

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id = f"{self._attr_unique_id}_hot_water_available"

    @property
    def name(self) -> str | None:
        return f"{self.device_name()} Hot Water Available"

    @property
    def native_value(self):
        return self.coordinator.data["devices"][self._id]["water"]["available"]

    @property
    def icon(self):
        return "mdi:percent"


class AquantaWaterHeaterCurrentModeSensor(AquantaEntity, SensorEntity):
    """Represents the current mode the Aquanta device is in."""

    entity_description: SensorEntityDescription(
        key="current_mode",
    )

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id = f"{self._attr_unique_id}_current_mode"

    @property
    def name(self) -> str | None:
        return f"{self.device_name()} Current Mode"

    @property
    def native_value(self):
        return self.coordinator.data["devices"][self._id]["info"]["currentMode"]["type"]


class AquantaWaterHeaterControlEnabledSensor(AquantaEntity, SensorEntity):
    """Represents whether the Aquanta device is controlling the water heater."""

    entity_description: SensorEntityDescription(
        key="control_enabled",
    )

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id = f"{self._attr_unique_id}_control_enabled"

    @property
    def name(self) -> str | None:
        return f"{self.device_name()} Control Enabled"

    @property
    def native_value(self):
        return self.coordinator.data["devices"][self._id]["advanced"]["controlEnabled"]


class AquantaWaterHeaterIntelligenceEnabledSensor(AquantaEntity, SensorEntity):
    """Represents whether the Aquanta has intelligence enabled."""

    entity_description: SensorEntityDescription(
        key="intelligence_enabled",
    )

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id = f"{self._attr_unique_id}_intelligence_enabled"

    @property
    def name(self) -> str | None:
        return f"{self.device_name()} Intelligence Enabled"

    @property
    def native_value(self):
        return (
            self.coordinator.data["devices"][self._id]["advanced"]["controlEnabled"]
            and self.coordinator.data["devices"][self._id]["advanced"]["intelEnabled"]
        )


class AquantaWaterHeaterThermostatEnabledSensor(AquantaEntity, SensorEntity):
    """Represents whether the Aquanta has its thermostat control enabled."""

    entity_description: SensorEntityDescription(
        key="thermostat_enabled",
    )

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id = f"{self._attr_unique_id}_thermostat_enabled"

    @property
    def name(self) -> str | None:
        return f"{self.device_name()} Thermostat Enabled"

    @property
    def native_value(self):
        return (
            self.coordinator.data["devices"][self._id]["advanced"]["controlEnabled"]
            and self.coordinator.data["devices"][self._id]["advanced"][
                "thermostatEnabled"
            ]
        )


class AquantaWaterHeaterTimeOfUseEnabledSensor(AquantaEntity, SensorEntity):
    """Represents whether the Aquanta has its Time of Use control enabled."""

    entity_description: SensorEntityDescription(
        key="time_of_use_enabled",
    )

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id = f"{self._attr_unique_id}_time_of_use_enabled"

    @property
    def name(self) -> str | None:
        return f"{self.device_name()} Time-of-Use Enabled"

    @property
    def native_value(self):
        return (
            self.coordinator.data["devices"][self._id]["advanced"]["controlEnabled"]
            and self.coordinator.data["devices"][self._id]["advanced"]["touEnabled"]
        )


class AquantaWaterHeaterTimerEnabledSensor(AquantaEntity, SensorEntity):
    """Represents whether the Aquanta has its timer control enabled."""

    entity_description: SensorEntityDescription(
        key="timer_enabled",
    )

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id = f"{self._attr_unique_id}_timer_enabled"

    @property
    def name(self) -> str | None:
        return f"{self.device_name()} Timer Enabled"

    @property
    def native_value(self):
        return (
            self.coordinator.data["devices"][self._id]["advanced"]["controlEnabled"]
            and self.coordinator.data["devices"][self._id]["advanced"]["timerEnabled"]
        )
