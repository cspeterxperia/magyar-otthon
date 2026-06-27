"""Közös entity alaposztály a Magyar Otthon integrációhoz."""

from __future__ import annotations

from homeassistant.helpers.entity import Entity

from .const import DOMAIN


class MagyarOtthonEntity(Entity):
    """A Magyar Otthon összes entitásának közös alaposztálya."""

    _attr_has_entity_name = True

    def __init__(self, entry_id: str) -> None:
        """Entity inicializálása."""
        self._entry_id = entry_id

    @property
    def device_info(self):
        """Eszközinformáció a Home Assistant számára."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": "Magyar Otthon",
            "manufacturer": "CsPeter & OpenAI",
            "model": "Magyar Otthon",
            "sw_version": "0.3.1",
        }