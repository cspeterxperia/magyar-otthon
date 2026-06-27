"""DataUpdateCoordinator a Magyar Otthon integrációhoz."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MagyarOtthonCoordinator(DataUpdateCoordinator[dict]):
    """Központi adatkezelő a Magyar Otthon integrációhoz."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Inicializálás."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )

    async def _async_update_data(self) -> dict:
        """Adatok frissítése."""

        return {
            "status": "ok",
            "version": "0.2.0",
        }