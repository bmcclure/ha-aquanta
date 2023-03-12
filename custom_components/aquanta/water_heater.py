"""Aquanta water heater component."""
from __future__ import annotations

from homeassistant.components.water_heater import (
    STATE_ECO,
    STATE_PERFORMANCE,
    STATE_OFF,
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import AquantaEntity
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize Aquanta devices from config entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        AquantaWaterHeater(coordinator, aquanta_id)
        for aquanta_id in coordinator.data["devices"]
    )


class AquantaWaterHeater(AquantaEntity, WaterHeaterEntity):
    """Representation of an Aquanta water heater controller."""

    _attr_has_entity_name = True
    _attr_supported_features = WaterHeaterEntityFeature.AWAY_MODE
    _attr_temperature_unit = TEMP_CELSIUS
    _attr_operation_list = [STATE_ECO, STATE_PERFORMANCE, STATE_OFF]
    _attr_name = "Water heater"

    def __init__(self, coordinator, aquanta_id) -> None:
        """Initialize the water heater."""
        super().__init__(coordinator, aquanta_id)
        self._attr_unique_id += "_water_heater"

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self.coordinator.data["devices"][self.aquanta_id]["water"]["temperature"]

    @property
    def current_operation(self):
        """Return current operation ie. eco, performance, off."""
        operation = STATE_OFF

        if (
            self.coordinator.data["devices"][self.aquanta_id]["info"]["currentMode"][
                "type"
            ]
            != "off"
        ):
            found = False

            for record in self.coordinator.data["devices"][self.aquanta_id]["info"][
                "records"
            ]:
                if record["type"] == "boost" and record["state"] == "ongoing":
                    operation = STATE_PERFORMANCE
                    found = True
                elif record["type"] == "away" and record["state"] == "ongoing":
                    operation = STATE_OFF
                    found = True
                    break

            if not found:
                operation = STATE_ECO

        return operation

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        if self.coordinator.data["devices"][self.aquanta_id]["advanced"][
            "thermostatEnabled"
        ]:
            return self.coordinator.data["devices"][self.aquanta_id]["advanced"][
                "setPoint"
            ]
        else:
            return None
