"""Holiday engine for Hungarian public holidays."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEvent

from .holiday_models import HolidayRule, HolidaySource
from .holiday_sources import (
    FixedHolidaySource,
    GovernmentHolidaySource,
    MovableHolidaySource,
    SchoolHolidaySource,
    UserHolidaySource,
    WorkdayTransferSource,
)


class HolidayEngine:
    """Calculate and merge Hungarian holiday data for providers."""

    def __init__(self, sources: list[HolidaySource] | None = None) -> None:
        """Initialize the engine with optional holiday sources."""

        self._sources = list(sources or [])
        if not self._sources:
            self._sources = [
                FixedHolidaySource(),
                MovableHolidaySource(),
                GovernmentHolidaySource(),
                WorkdayTransferSource(),
                SchoolHolidaySource(),
                UserHolidaySource(),
            ]
        self._source_cache: dict[tuple[str, int], dict[date, HolidayRule]] = {}

    def register_source(self, source: HolidaySource) -> None:
        """Register an additional holiday source."""

        self._sources.append(source)
        self._source_cache.clear()

    def get_holidays(self, start_date: datetime, end_date: datetime) -> list[CalendarEvent]:
        """Return all holidays between the requested dates as calendar events."""

        events: list[CalendarEvent] = []
        current_day = start_date.date()
        end_day = end_date.date()

        while current_day <= end_day:
            rule = self._get_rule_for_day(current_day)
            if rule is not None:
                events.append(self._create_event(rule, current_day))
            current_day += timedelta(days=1)

        return events

    def get_holiday_name(self, day: date) -> str | None:
        """Return the holiday name for a specific day, if any."""

        rule = self._get_rule_for_day(day)
        return rule.summary if rule is not None else None

    def is_holiday(self, day: date) -> bool:
        """Return whether the given day is a holiday."""

        return self._get_rule_for_day(day) is not None

    def get_events(self, start: datetime, end: datetime) -> list[CalendarEvent]:
        """Return the holiday events for the requested range."""

        return self.get_holidays(start, end)

    def _get_rule_for_day(self, day: date) -> HolidayRule | None:
        """Resolve the holiday rule for a day from the registered sources."""

        for source in self._sources:
            for rule in self._get_source_rules(source, day.year):
                if rule.holiday_date == day:
                    return rule

        return None

    def _get_source_rules(self, source: HolidaySource, year: int) -> list[HolidayRule]:
        """Return cached holiday rules for an external source and year."""

        source_name = getattr(source, "name", "unknown")
        cache_key = (source_name, year)
        if cache_key not in self._source_cache:
            self._source_cache[cache_key] = {
                rule.holiday_date: rule for rule in source.get_holidays(year)
            }
        return list(self._source_cache[cache_key].values())


    def _create_event(self, rule: HolidayRule, day: date) -> CalendarEvent:
        """Create a calendar event from a holiday rule."""

        return CalendarEvent(
            summary=rule.summary,
            start=day,
            end=day + timedelta(days=1),
            description=rule.description,
        )
