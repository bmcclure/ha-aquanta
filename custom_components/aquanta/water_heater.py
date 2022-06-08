"""Aquanta water heater component."""
from datetime import datetime, timedelta, timezone

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
    STATE_OFF,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN, AquantaEntity

STATE_MAP = {
    "off": STATE_ELECTRIC,
    "setpoint": STATE_PERFORMANCE,
    "intelligence": STATE_ECO,
    "boost": STATE_HIGH_DEMAND,
    "away": STATE_OFF,
}

ATTR_HOT_WATER_AVAILABLE = "hot_water_available"


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

    _attr_supported_features = WaterHeaterEntityFeature.AWAY_MODE
    _attr_temperature_unit = TEMP_CELSIUS

    def __init__(self, coordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_unique_id = f"{self._attr_unique_id}_water_heater"

    @property
    def name(self) -> str | None:
        return f"{self.device_name()} Water Heater"

    @property
    def current_temperature(self) -> str | None:
        return self.coordinator.data["devices"][self._id]["water"]["temperature"]

    @property
    def target_temperature(self) -> float | None:
        if self.coordinator.data["devices"][self._id]["advanced"]["thermostatEnabled"]:
            return self.coordinator.data["devices"][self._id]["advanced"]["setPoint"]
        else:
            return None

    @property
    def is_away_mode_on(self) -> bool | None:
        return (
            self.coordinator.data["devices"][self._id]["info"]["currentMode"]["type"]
            == "away"
        )

    def turn_away_mode_on(self):
        schedule = self.get_away_schedule()
        self._api[self._id].set_away(schedule["start"], schedule["stop"])

    def turn_away_mode_off(self):
        self._api[self._id].delete_away()

    def get_away_schedule(self):
        """Gets a schedule in the correct format for enabling Away mode"""
        start = datetime.now(timezone.utc)
        end = start + timedelta(days=30)
        time_format = "%Y-%m-%dT%H:%M:%S.000Z"

        return {
            "start": start.strftime(time_format),
            "stop": end.strftime(time_format),
        }
