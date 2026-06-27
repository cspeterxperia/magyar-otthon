"""Magyar Otthon szenzorok."""

from __future__ import annotations

from datetime import date

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .modules.garbage import GarbageSchedule, next_collection


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Szenzorok létrehozása."""

    schedule = GarbageSchedule(
        name="Kommunális hulladék",
        start_date=date(2026, 1, 6),
        weekday=1,  # kedd
        interval_days=14,
    )

    async_add_entities(
        [
            GarbageNextCollectionSensor(schedule),
        ]
    )


class GarbageNextCollectionSensor(SensorEntity):
    """Következő hulladékszállítás."""

    _attr_has_entity_name = True

    def __init__(self, schedule: GarbageSchedule) -> None:
        self._schedule = schedule
        self._attr_name = schedule.name
        self._attr_unique_id = (
            f"magyar_otthon_{schedule.name.lower().replace(' ', '_')}"
        )

    @property
    def native_value(self):
        """Szenzor állapota."""

        return next_collection(
            self._schedule,
            date.today(),
        ).isoformat()

    @property
    def extra_state_attributes(self):
        """Extra attribútumok."""

        next_day = next_collection(
            self._schedule,
            date.today(),
        )

        return {
            "következő_ürítés": next_day.isoformat(),
            "hulladék_típus": self._schedule.name,
        }