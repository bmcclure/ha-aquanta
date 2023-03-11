"""Aquanta sensor component."""
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry

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


class AquantaWaterHeaterControlEnabledSensor(AquantaEntity, BinarySensorEntity):
    """Represents whether the Aquanta device is controlling the water heater."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id += "_control_enabled"

    @property
    def name(self):
        return "Control enabled"

    @property
    def icon(self):
        if self.is_on:
            return "mdi:check-circle"
        return "mdi:check-circle-outline"

    @property
    def is_on(self):
        return self.coordinator.data["devices"][self._id]["advanced"]["controlEnabled"]


class AquantaWaterHeaterIntelligenceEnabledSensor(AquantaEntity, BinarySensorEntity):
    """Represents whether the Aquanta has intelligence enabled."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id += "_intelligence_enabled"

    @property
    def name(self):
        return "Intelligence enabled"

    @property
    def icon(self):
        if self.is_on:
            return "mdi:check-circle"
        return "mdi:check-circle-outline"

    @property
    def is_on(self):
        return (
            self.coordinator.data["devices"][self._id]["advanced"]["controlEnabled"]
            and self.coordinator.data["devices"][self._id]["advanced"]["intelEnabled"]
        )


class AquantaWaterHeaterThermostatEnabledSensor(AquantaEntity, BinarySensorEntity):
    """Represents whether the Aquanta has its thermostat control enabled."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id += "_thermostat_enabled"

    @property
    def name(self):
        return "Thermostat enabled"

    @property
    def icon(self):
        if self.is_on:
            return "mdi:check-circle"
        return "mdi:check-circle-outline"

    @property
    def is_on(self):
        return (
            self.coordinator.data["devices"][self._id]["advanced"]["controlEnabled"]
            and self.coordinator.data["devices"][self._id]["advanced"][
                "thermostatEnabled"
            ]
        )


class AquantaWaterHeaterTimeOfUseEnabledSensor(AquantaEntity, BinarySensorEntity):
    """Represents whether the Aquanta has its Time of Use control enabled."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id += "_time_of_use_enabled"

    @property
    def name(self):
        return "Time-of-Use enabled"

    @property
    def icon(self):
        if self.is_on:
            return "mdi:check-circle"
        return "mdi:check-circle-outline"

    @property
    def is_on(self):
        return (
            self.coordinator.data["devices"][self._id]["advanced"]["controlEnabled"]
            and self.coordinator.data["devices"][self._id]["advanced"]["touEnabled"]
        )


class AquantaWaterHeaterTimerEnabledSensor(AquantaEntity, BinarySensorEntity):
    """Represents whether the Aquanta has its timer control enabled."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id += "_timer_enabled"

    @property
    def icon(self):
        if self.is_on:
            return "mdi:check-circle"
        return "mdi:check-circle-outline"

    @property
    def name(self):
        return "Timer enabled"

    @property
    def is_on(self):
        return (
            self.coordinator.data["devices"][self._id]["advanced"]["controlEnabled"]
            and self.coordinator.data["devices"][self._id]["advanced"]["timerEnabled"]
        )
