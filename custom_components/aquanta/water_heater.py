"""Aquanta water heater component."""
from homeassistant.components.water_heater import (
    STATE_ECO,
    STATE_ELECTRIC,
    STATE_HIGH_DEMAND,
    STATE_PERFORMANCE,
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_TEMPERATURE,
    STATE_OFF,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    Platform,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN

STATE_MAP = {
    "off": STATE_ELECTRIC,
    "setpoint": STATE_PERFORMANCE,
    "intelligence": STATE_ECO,
    "boost": STATE_HIGH_DEMAND,
    "away": STATE_OFF,
}


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


class AquantaWaterHeater(CoordinatorEntity, WaterHeaterEntity):
    """Representation of an Aquanta water heater controller."""

    _attr_supported_features = (
        WaterHeaterEntityFeature.TARGET_TEMPERATURE | WaterHeaterEntityFeature.AWAY_MODE
    )
    _attr_temperature_unit = TEMP_CELSIUS

    def __init__(self, coordinator, aquanta_id) -> None:
        super().__init__(coordinator)
        self._id = aquanta_id
        self._attr_name = DOMAIN.title()
        self._attr_unique_id = f"{coordinator.data['id']}-{aquanta_id}"
        self._attr_operation_list = [
            STATE_OFF,
            STATE_ELECTRIC,
            STATE_ECO,
            STATE_PERFORMANCE,
            STATE_HIGH_DEMAND,
        ]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from coordinator."""
        data = self.coordinator.data["devices"][self._id]
        self._attr_current_temperature = data["water"]["temperature"]
        self._attr_current_operation = STATE_MAP[data["info"]["currentMode"]["type"]]
        self._attr_is_away_mode_on = data["info"]["currentMode"]["type"] == "away"
        return super()._handle_coordinator_update()

    @property
    def device_info(self) -> DeviceInfo:
        """Return info for device registry."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            manufacturer="Aquanta",
            model="Aquanta Water Heater Controller",
            name=self.coordinator.data["devices"][self._id]["info"]["title"],
        )
