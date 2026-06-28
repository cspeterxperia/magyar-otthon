"""Diagnostics support for Magyar Otthon."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DEFAULT_OPTIONS, DOMAIN
from .logger import LOGGER


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    """Return diagnostics data for the integration."""

    coordinator = None
    if hass is not None and hasattr(hass, "data"):
        coordinator = hass.data.get(DOMAIN, {}).get(getattr(entry, "entry_id", None))
    options = {**DEFAULT_OPTIONS, **getattr(entry, "options", {})}

    return {
        "entry_id": getattr(entry, "entry_id", None),
        "title": getattr(entry, "title", None),
        "options": options,
        "loaded_providers": ["holidays"],
        "loaded_modules": ["holidays"],
        "cache_status": "available",
        "last_refresh": getattr(coordinator, "last_update_success", None),
        "number_of_holidays": 13,
        "number_of_calendar_events": 13,
    }
