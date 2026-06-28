"""Additional holiday-related sensors for the integration."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import CONF_HOLIDAYS_ENABLED, DEFAULT_OPTIONS, DOMAIN
from .logger import LOGGER
from .modules.holidays import HolidaysCalendarProvider


async def async_setup_sensor_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the holiday-related sensor entities."""

    options = {**DEFAULT_OPTIONS, **entry.options}
    if not options.get(CONF_HOLIDAYS_ENABLED, True):
        return

    provider = HolidaysCalendarProvider()
    LOGGER.debug("Adding holiday sensor entities for entry %s", entry.entry_id)
    async_add_entities(
        [
            DaysUntilNextHolidaySensor(provider, entry.entry_id),
            HolidayCountThisYearSensor(provider, entry.entry_id),
        ]
    )


async def async_setup_binary_sensor_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the holiday-related binary sensor entity."""

    options = {**DEFAULT_OPTIONS, **entry.options}
    if not options.get(CONF_HOLIDAYS_ENABLED, True):
        return

    provider = HolidaysCalendarProvider()
    LOGGER.debug("Adding holiday binary sensor for entry %s", entry.entry_id)
    async_add_entities([TodayIsHolidayBinarySensor(provider, entry.entry_id)])


class DaysUntilNextHolidaySensor(SensorEntity):
    """Expose the number of days until the next holiday."""

    _attr_has_entity_name = True
    _attr_name = "Következő ünnep napjai"

    def __init__(self, provider: HolidaysCalendarProvider, entry_id: str) -> None:
        self._provider = provider
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_days_until_next_holiday"

    @property
    def native_value(self) -> int | None:
        """Return the day count until the next holiday."""

        today = dt_util.now().date()
        holiday = self._get_next_holiday(today)
        if holiday is None:
            return None
        return (holiday.start - today).days

    def _get_next_holiday(self, today: date) -> object | None:
        try:
            events = self._provider._engine.get_holidays(
                datetime.combine(today, datetime.min.time()),
                datetime.combine(today + timedelta(days=365), datetime.max.time()),
            )
        except Exception:  # pragma: no cover - defensive guard
            LOGGER.exception("Failed to compute days until next holiday")
            return None

        future_events = [event for event in events if event.start >= today]
        if not future_events:
            return None
        return min(future_events, key=lambda event: event.start)


class TodayIsHolidayBinarySensor(BinarySensorEntity):
    """Indicate whether today is a holiday."""

    _attr_has_entity_name = True
    _attr_name = "Ma ünnepnap van"

    def __init__(self, provider: HolidaysCalendarProvider, entry_id: str) -> None:
        self._provider = provider
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_today_is_holiday"

    @property
    def is_on(self) -> bool:
        """Return whether today is a holiday."""

        today = dt_util.now().date()
        return self._provider._engine.is_holiday(today)

    @property
    def extra_state_attributes(self) -> dict[str, object]:
        """Return holiday details when today is a holiday."""

        today = dt_util.now().date()
        if not self._provider._engine.is_holiday(today):
            return {}

        return {
            "ünnepnap_neve": self._provider._engine.get_holiday_name(today),
            "ünnepnap_dátuma": today.isoformat(),
        }


class HolidayCountThisYearSensor(SensorEntity):
    """Expose the number of holidays remaining this year."""

    _attr_has_entity_name = True
    _attr_name = "Ünnepnapok száma ebben az évben"

    def __init__(self, provider: HolidaysCalendarProvider, entry_id: str) -> None:
        self._provider = provider
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_holiday_count_this_year"

    @property
    def native_value(self) -> int:
        """Return the number of holidays remaining this year."""

        today = dt_util.now().date()
        try:
            events = self._provider._engine.get_holidays(
                datetime.combine(today, datetime.min.time()),
                datetime.combine(date(today.year, 12, 31), datetime.max.time()),
            )
        except Exception:  # pragma: no cover - defensive guard
            LOGGER.exception("Failed to count holidays this year")
            return 0
        return len(events)
