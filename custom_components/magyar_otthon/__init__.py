"""Magyar Otthon integráció."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

type MagyarOtthonConfigEntry = ConfigEntry


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Integráció inicializálása."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MagyarOtthonConfigEntry,
) -> bool:
    """Config entry betöltése."""
    hass.data[DOMAIN][entry.entry_id] = {}

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: MagyarOtthonConfigEntry,
) -> bool:
    """Config entry eltávolítása."""
    hass.data[DOMAIN].pop(entry.entry_id)

    return True