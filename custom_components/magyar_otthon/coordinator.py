"""Coordinator a Magyar Otthon integrációhoz."""

from __future__ import annotations

from datetime import datetime

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

LOGGER = logging.getLogger(__name__)


class MagyarOtthonCoordinator(DataUpdateCoordinator[dict[str, object]]):
    """A Magyar Otthon központi adatkezelője."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Inicializálás."""

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=None,
        )

    async def _async_update_data(self) -> dict[str, object]:
        """Adatok frissítése."""

        return {
            "last_update": datetime.now().isoformat(),
            "holidays": {},
            "garbage": {},
            "school": {},
            "reminders": {},
        }