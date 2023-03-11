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
        on_value = (
            self.coordinator.data["devices"][self._id]["info"]["currentMode"]["type"]
            == "away"
        )

        if not on_value:
            for record in self.coordinator.data["devices"][self._id]["info"]["records"]:
                if record["type"] == "away" and record["state"] == "ongoing":
                    on_value = True
                    break

        return on_value

    async def async_turn_on(self, **kwargs):
        schedule = self.get_away_schedule()
        await self.hass.async_add_executor_job(
            self._api[self._id].set_away, schedule["start"], schedule["stop"]
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(self._api[self._id].delete_away)
        await self.coordinator.async_request_refresh()

    def get_away_schedule(self):
        """Gets a schedule in the correct format for enabling Away mode"""
        start = datetime.now(timezone.utc)
        end = start + timedelta(days=30)
        time_format = "%Y-%m-%dT%H:%M:%S.000Z"

        return {
            "start": start.strftime(time_format),
            "stop": end.strftime(time_format),
        }


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
        on_value = (
            self.coordinator.data["devices"][self._id]["info"]["currentMode"]["type"]
            == "boost"
        )

        if not on_value:
            for record in self.coordinator.data["devices"][self._id]["info"]["records"]:
                if record["type"] == "boost" and record["state"] == "ongoing":
                    on_value = True
                    break

        return on_value

    async def async_turn_on(self, **kwargs):
        schedule = self.get_boost_schedule()
        await self.hass.async_add_executor_job(
            self._api[self._id].set_boost, schedule["start"], schedule["stop"]
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(self._api[self._id].delete_boost)
        await self.coordinator.async_request_refresh()

    def get_boost_schedule(self):
        """Gets a schedule in the correct format for enabling Boost mode"""
        start = datetime.now(timezone.utc)
        end = start + timedelta(days=30)
        time_format = "%Y-%m-%dT%H:%M:%S.000Z"

        return {
            "start": start.strftime(time_format),
            "stop": end.strftime(time_format),
        }
