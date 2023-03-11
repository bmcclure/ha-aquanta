"""The Aquanta integration."""
from __future__ import annotations

from datetime import timedelta, datetime, timezone
import logging

import async_timeout
from aquanta import Aquanta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
    CoordinatorEntity,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.WATER_HEATER,
]

OPERATION_MODE_NORMAL = "Normal"
OPERATION_MODE_BOOST = "Boost"

CONTROL_MODE_OFF = "Off (No Control)"
CONTROL_MODE_AQUANTA_INTELLIGENCE = "Aquanta Intelligence"
CONTROL_MODE_THERMOSTAT = "Thermostat"
CONTROL_MODE_TIMER = "Manual Timer"
CONTROL_MODE_TOU = "Time of Use"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Aquanta from a config entry."""

    try:
        aquanta = await hass.async_add_executor_job(
            Aquanta, entry.data["username"], entry.data["password"]
        )
    except RuntimeError as err:
        raise ConfigEntryAuthFailed(err) from err

    coordinator = AquantaCoordinator(
        hass,
        aquanta,
        entry.data["username"],
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    if entry.unique_id is None:
        hass.config_entries.async_update_entry(entry, unique_id=entry.data["username"])

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class AquantaCoordinator(DataUpdateCoordinator):
    """Defines an Aquanta data update coordinator."""

    def __init__(self, hass: HomeAssistant, aquanta, account_id) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN.title(),
            update_interval=timedelta(seconds=60),
        )
        self.aquanta = aquanta
        self.account_id = account_id

    def get_device_data(self):
        """Gets all data from the Aquanta API for each device"""
        data = {"id": self.account_id, "devices": {}}

        for aquanta_id in self.aquanta.devices():
            data["devices"][aquanta_id] = {
                "water": self.aquanta[aquanta_id].water,
                "info": self.aquanta[aquanta_id].infocenter,
                "advanced": self.aquanta[aquanta_id].advanced,
            }

        return data

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(10):
                return await self.hass.async_add_executor_job(self.get_device_data)
        except RuntimeError as err:
            raise UpdateFailed(f"Error communicating with Aquanta: {err}") from err


class AquantaEntity(CoordinatorEntity):
    """Defines a main class for an Aquanta controller-based entity."""

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        super().__init__(coordinator)
        self._id = aquanta_id
        self._api = coordinator.aquanta
        self._attr_unique_id = f"{coordinator.data['id']}_{aquanta_id}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return info for device registry."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self.coordinator.data['id']}_{self._id}")},
            manufacturer="Aquanta",
            model="Aquanta Water Heater Controller",
            name=self.coordinator.data["devices"][self._id]["info"]["title"],
        )

    def device_name(self):
        """Get the device name from the latest API request"""
        return self.coordinator.data["devices"][self._id]["info"]["title"]

    @property
    def is_away_mode_on(self):
        """Return true if away mode is on."""
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

    async def async_turn_away_mode_on(self):
        """Turn away mode on."""
        schedule = self.get_away_schedule()
        await self.hass.async_add_executor_job(
            self._api[self._id].set_away, schedule["start"], schedule["stop"]
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_away_mode_off(self):
        """Turn away mode off."""
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

    @property
    def is_boost_mode_on(self):
        """Return true if boost mode is on."""
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

    async def async_turn_boost_mode_on(self, **kwargs):
        """Turn on boost mode."""
        schedule = self.get_boost_schedule()
        await self.hass.async_add_executor_job(
            self._api[self._id].set_boost, schedule["start"], schedule["stop"]
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_boost_mode_off(self, **kwargs):
        """Turn off boost mode."""
        await self.hass.async_add_executor_job(self._api[self._id].delete_boost)
        await self.coordinator.async_request_refresh()

    def get_boost_schedule(self):
        """Gets a schedule in the correct format for enabling Boost mode"""
        start = datetime.now(timezone.utc)
        end = start + timedelta(minutes=30)
        time_format = "%Y-%m-%dT%H:%M:%S.000Z"

        return {
            "start": start.strftime(time_format),
            "stop": end.strftime(time_format),
        }
