"""Calendar platform for Magyar Otthon."""

from __future__ import annotations

from homeassistant.components.calendar import CalendarEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the calendar platform."""
    async_add_entities([MagyarOtthonCalendar()])


class MagyarOtthonCalendar(CalendarEntity):
    """Magyar Otthon calendar."""

    _attr_has_entity_name = True
    _attr_name = "Magyar Naptár"

    @property
    def event(self):
        """Current event."""
        return None

    async def async_update(self) -> None:
        """Update calendar."""
        return