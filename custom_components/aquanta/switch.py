"""Aquanta sensor component."""
from datetime import datetime, timedelta, timezone

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
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
        AquantaWaterHeaterAwaySwitch(coordinator, aquanta_id)
        for aquanta_id in coordinator.data["devices"]
    )
    async_add_entities(
        AquantaWaterHeaterBoostSwitch(coordinator, aquanta_id)
        for aquanta_id in coordinator.data["devices"]
    )


class AquantaWaterHeaterAwaySwitch(AquantaEntity, SwitchEntity):
    """Represents the away mode of the Aquanta device."""

    _attr_has_entity_name = True
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id += "_away"

    @property
    def name(self):
        return "Away"

    @property
    def is_on(self):
        return self.is_away_mode_on

    async def async_turn_on(self, **kwargs):
        return await self.async_turn_away_mode_on(**kwargs)

    async def async_turn_off(self, **kwargs):
        return await self.async_turn_away_mode_off(**kwargs)


class AquantaWaterHeaterBoostSwitch(AquantaEntity, SwitchEntity):
    """Represents the boost mode of the Aquanta device."""

    _attr_has_entity_name = True
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator, aquanta_id)
        self._attr_should_poll = True
        self._attr_unique_id += "_boost"

    @property
    def name(self):
        return "Boost"

    @property
    def is_on(self):
        return self.is_boost_mode_on

    async def async_turn_on(self, **kwargs):
        return await self.async_turn_boost_mode_on(**kwargs)

    async def async_turn_off(self, **kwargs):
        return await self.async_turn_boost_mode_off(**kwargs)
