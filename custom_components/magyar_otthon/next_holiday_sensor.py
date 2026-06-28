"""Next Hungarian holiday sensor."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import CONF_HOLIDAYS_ENABLED, DEFAULT_OPTIONS, DOMAIN
from .logger import LOGGER
from .modules.holidays import HolidaysCalendarProvider


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the next holiday sensor."""

    options = {**DEFAULT_OPTIONS, **entry.options}
    if not options.get(CONF_HOLIDAYS_ENABLED, True):
        return

    provider = HolidaysCalendarProvider()
    LOGGER.debug("Loading next holiday sensor for entry %s", entry.entry_id)
    async_add_entities([NextHolidaySensor(provider, entry.entry_id)])


class NextHolidaySensor(SensorEntity):
    """Expose the next Hungarian holiday as a sensor."""

    _attr_has_entity_name = True
    _attr_name = "Next Hungarian Holiday"

    def __init__(self, provider: HolidaysCalendarProvider, entry_id: str) -> None:
        """Initialize the sensor."""

        self._provider = provider
        self._entry_id = entry_id
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_next_holiday"
        self._attr_native_value = None

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return holiday details as attributes."""

        now = dt_util.now().date()
        holiday = self._get_next_holiday(now)
        if holiday is None:
            return {}

        days_remaining = (holiday.start - now).days
        return {
            "holiday_name": holiday.summary,
            "date": holiday.start.isoformat(),
            "days_remaining": days_remaining,
            "is_today": days_remaining == 0,
            "is_tomorrow": days_remaining == 1,
        }

    @property
    def native_value(self) -> str | None:
        """Return the holiday name or None."""

        holiday = self._get_next_holiday(dt_util.now().date())
        return holiday.summary if holiday is not None else None

    def _get_next_holiday(self, today: date) -> object | None:
        """Return the next holiday from the provider for the current range."""

        try:
            events = self._provider._engine.get_holidays(
                datetime.combine(today, datetime.min.time()),
                datetime.combine(today + timedelta(days=365), datetime.max.time()),
            )
        except Exception:  # pragma: no cover - defensive guard
            LOGGER.exception("Failed to refresh next holiday sensor")
            return None

        future_events = [event for event in events if event.start >= today]
        if not future_events:
            return None
        return min(future_events, key=lambda event: event.start)
