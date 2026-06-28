"""Binary sensor platform for Magyar Otthon."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .holiday_sensors import async_setup_binary_sensor_entry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the integration's binary sensors."""

    await async_setup_binary_sensor_entry(hass, entry, async_add_entities)
