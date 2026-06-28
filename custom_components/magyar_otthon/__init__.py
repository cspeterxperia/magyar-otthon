"""Magyar Otthon integráció."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import MagyarOtthonCoordinator
from .logger import LOGGER


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Integráció inicializálása."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Config entry betöltése."""

    coordinator = MagyarOtthonCoordinator(hass)
    LOGGER.debug("Setting up config entry %s", entry.entry_id)
    LOGGER.debug("Forwarding platforms: %s", PLATFORMS)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Config entry eltávolítása."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok