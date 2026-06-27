"""Magyar munkaszüneti napok."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEvent

from ..calendar_provider import CalendarDataProvider


FIXED_HOLIDAYS = {
    (1, 1): "Újév",
    (3, 15): "1848-as forradalom és szabadságharc",
    (5, 1): "Munka ünnepe",
    (8, 20): "Szent István ünnepe",
    (10, 23): "1956-os forradalom",
    (11, 1): "Mindenszentek",
    (12, 25): "Karácsony első napja",
    (12, 26): "Karácsony második napja",
}


class HolidaysCalendarProvider(CalendarDataProvider):
    """Provide Hungarian public holidays as calendar events."""

    name = "holidays"

    async def async_get_events(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return fixed public holidays within the requested range."""

        events: list[CalendarEvent] = []
        current = start_date.date()
        while current <= end_date.date():
            holiday_name = FIXED_HOLIDAYS.get((current.month, current.day))
            if holiday_name is not None:
                events.append(
                    CalendarEvent(
                        summary=holiday_name,
                        start=datetime.combine(current, datetime.min.time()),
                        end=datetime.combine(current + timedelta(days=1), datetime.min.time()),
                        description="Magyar közszabadság nap",
                        location="Magyarország",
                    )
                )
            current += timedelta(days=1)

        return events


def get_fixed_holiday(day: date) -> str | None:
    """Visszaadja a fix ünnep nevét."""

    return FIXED_HOLIDAYS.get((day.month, day.day))


def is_fixed_holiday(day: date) -> bool:
    """Igaz, ha a nap fix magyar munkaszüneti nap."""

    return (day.month, day.day) in FIXED_HOLIDAYS