"""The Aquanta integration."""
from __future__ import annotations

from datetime import timedelta
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

PLATFORMS: list[Platform] = [Platform.WATER_HEATER, Platform.SENSOR]

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

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

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
        self.aquanta_id = aquanta_id
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
