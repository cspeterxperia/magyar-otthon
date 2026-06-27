"""Magyar Otthon integráció."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

PLATFORMS: list[str] = []


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Integráció inicializálása."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Config entry betöltése."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    if PLATFORMS:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Config entry eltávolítása."""
    if PLATFORMS:
        unload_ok = await hass.config_entries.async_unload_platforms(
            entry,
            PLATFORMS,
        )
    else:
        unload_ok = True

    hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok