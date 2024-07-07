"""AquantaEntity class."""

from __future__ import annotations

from datetime import timedelta, datetime, timezone

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import ATTRIBUTION, DOMAIN, MODEL, NAME
from .coordinator import AquantaCoordinator


class AquantaEntity(CoordinatorEntity):
    """Defines a main class for an Aquanta entity."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: AquantaCoordinator, aquanta_id) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._base_unique_id = f"{coordinator.data['id']}_{aquanta_id}"
        self.aquanta_id = aquanta_id
        self._api = coordinator.aquanta

    @property
    def device_info(self) -> DeviceInfo:
        """Return info for device registry."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._base_unique_id)},
            manufacturer=NAME,
            model=MODEL,
            name=self.coordinator.data["devices"][self.aquanta_id]["info"]["title"],
        )

    def device_name(self):
        """Get the device name from the latest API request."""
        return self.coordinator.data["devices"][self.aquanta_id]["info"]["title"]

    @property
    def is_away_mode_on(self):
        """Return true if away mode is on."""
        on_value = (
            self.coordinator.data["devices"][self.aquanta_id]["info"]["currentMode"][
                "type"
            ]
            == "away"
        )

        if not on_value:
            for record in self.coordinator.data["devices"][self.aquanta_id]["info"][
                "records"
            ]:
                if record["type"] == "away" and record["state"] == "ongoing":
                    on_value = True
                    break

        return on_value

    async def async_turn_away_mode_on(self):
        """Turn away mode on."""
        schedule = self.get_away_schedule()
        await self.hass.async_add_executor_job(
            self._api[self.aquanta_id].set_away, schedule["start"], schedule["stop"]
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_away_mode_off(self):
        """Turn away mode off."""
        await self.hass.async_add_executor_job(self._api[self.aquanta_id].delete_away)
        await self.coordinator.async_request_refresh()

    def get_away_schedule(self):
        """Get a schedule in the correct format for enabling Away mode."""
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
            self.coordinator.data["devices"][self.aquanta_id]["info"]["currentMode"][
                "type"
            ]
            == "boost"
        )

        if not on_value:
            for record in self.coordinator.data["devices"][self.aquanta_id]["info"][
                "records"
            ]:
                if record["type"] == "boost" and record["state"] == "ongoing":
                    on_value = True
                    break

        return on_value

    async def async_turn_boost_mode_on(self, **kwargs):
        """Turn on boost mode."""
        schedule = self.get_boost_schedule()
        await self.hass.async_add_executor_job(
            self._api[self.aquanta_id].set_boost, schedule["start"], schedule["stop"]
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_boost_mode_off(self, **kwargs):
        """Turn off boost mode."""
        await self.hass.async_add_executor_job(self._api[self.aquanta_id].delete_boost)
        await self.coordinator.async_request_refresh()

    def get_boost_schedule(self):
        """Get a schedule in the correct format for enabling Boost mode."""
        start = datetime.now(timezone.utc)
        end = start + timedelta(minutes=30)
        time_format = "%Y-%m-%dT%H:%M:%S.000Z"

        return {
            "start": start.strftime(time_format),
            "stop": end.strftime(time_format),
        }
