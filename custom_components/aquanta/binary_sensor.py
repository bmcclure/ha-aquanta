"""Binary sensor platform for aqaunta."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import AquantaEntity
from .const import DOMAIN, LOGGER
from .coordinator import AquantaCoordinator

ENTITY_DESCRIPTIONS = (
    {
        "desc": BinarySensorEntityDescription(
            key="control_enabled",
            name="Control enabled",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        "is_on": lambda entity: entity.coordinator.data["devices"][entity.aquanta_id][
            "advanced"
        ]["controlEnabled"],
    },
    {
        "desc": BinarySensorEntityDescription(
            key="intelligence_enabled",
            name="Intelligence enabled",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        "is_on": lambda entity: (
            entity.coordinator.data["devices"][entity.aquanta_id]["advanced"][
                "controlEnabled"
            ]
            and entity.coordinator.data["devices"][entity.aquanta_id]["advanced"][
                "intelEnabled"
            ]
        ),
    },
    {
        "desc": BinarySensorEntityDescription(
            key="thermostat_enabled",
            name="Thermostat enabled",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        "is_on": lambda entity: (
            entity.coordinator.data["devices"][entity.aquanta_id]["advanced"][
                "controlEnabled"
            ]
            and entity.coordinator.data["devices"][entity.aquanta_id]["advanced"][
                "thermostatEnabled"
            ]
        ),
    },
    {
        "desc": BinarySensorEntityDescription(
            key="time_of_use_enabled",
            name="Time-of-use enabled",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        "is_on": lambda entity: (
            entity.coordinator.data["devices"][entity.aquanta_id]["advanced"][
                "controlEnabled"
            ]
            and entity.coordinator.data["devices"][entity.aquanta_id]["advanced"][
                "touEnabled"
            ]
        ),
    },
    {
        "desc": BinarySensorEntityDescription(
            key="timer_enabled",
            name="Timer enabled",
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        "is_on": lambda entity: (
            entity.coordinator.data["devices"][entity.aquanta_id]["advanced"][
                "controlEnabled"
            ]
            and entity.coordinator.data["devices"][entity.aquanta_id]["advanced"][
                "timerEnabled"
            ]
        ),
    },
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize Aquanta devices from config entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities: list[AquantaBinarySensor] = []

    for aquanta_id in coordinator.data["devices"]:
        for entity_info in ENTITY_DESCRIPTIONS:
            entities.append(
                AquantaBinarySensor(
                    coordinator, aquanta_id, entity_info["desc"], entity_info["is_on"]
                )
            )

    async_add_entities(entities)


class AquantaBinarySensor(AquantaEntity, BinarySensorEntity):
    """Represents a binary sensor for an Aquanta device."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AquantaCoordinator,
        aquanta_id,
        entity_description: BinarySensorEntityDescription,
        is_on_func,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, aquanta_id)
        self.entity_description = entity_description
        self._is_on_func = is_on_func
        self._attr_name = entity_description.name
        self._attr_should_poll = True
        self._attr_unique_id = self._base_unique_id + "_" + entity_description.key
        LOGGER.debug("Created binary sensor with unique ID %s", self._attr_unique_id)

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        if self.is_on:
            return "mdi:check-circle"
        return "mdi:check-circle-outline"

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._is_on_func(self)
