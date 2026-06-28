"""Provider for Hungarian public holidays."""

from __future__ import annotations

from datetime import date, datetime

from homeassistant.components.calendar import CalendarEvent

from ..calendar_provider import CalendarDataProvider
from .holiday_engine import HolidayEngine


class HolidaysCalendarProvider(CalendarDataProvider):
    """Provide Hungarian public holidays as calendar events."""

    name = "holidays"

    def __init__(self, engine: HolidayEngine | None = None) -> None:
        """Initialize the provider with a holiday engine."""

        self._engine = engine or HolidayEngine()

    async def async_get_events(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return Hungarian public holidays within the requested range."""

        return self._engine.get_holidays(start_date, end_date)


def get_fixed_holiday(day: date) -> str | None:
    """Backward-compatible helper for fixed holiday lookup."""

    return HolidayEngine().get_holiday_name(day)


def is_fixed_holiday(day: date) -> bool:
    """Backward-compatible helper for fixed holiday detection."""

    return get_fixed_holiday(day) is not None