"""Production-ready architecture skeleton for the future school engine."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from homeassistant.util import dt as dt_util

from .school_models import SchoolDataSource, SchoolEvent, SchoolRule
from .school_sources import (
    BMDecreeSource,
    IcsSource,
    JsonSource,
    LocalFileSource,
    ManualSource,
    RestApiSource,
)


class SchoolEngine:
    """Resolve school-related rules into normalized school events."""

    def __init__(self, sources: list[SchoolDataSource] | None = None) -> None:
        """Initialize the engine with optional data sources."""

        self._sources = list(sources or [])
        if not self._sources:
            self._sources = [
                BMDecreeSource(),
                JsonSource(),
                IcsSource(),
                RestApiSource(),
                LocalFileSource(),
                ManualSource(),
            ]
        self._cache: dict[tuple[str, int], list[SchoolRule]] = {}

    def register_source(self, source: SchoolDataSource) -> None:
        """Register an additional source."""

        self._sources.append(source)
        self._cache.clear()

    def get_events(self, start: datetime, end: datetime) -> list[SchoolEvent]:
        """Return normalized school events for the requested range."""

        rules: list[SchoolRule] = []
        for source in self._sources:
            rules.extend(self._get_rules_for_year(source, start.year))
            rules.extend(self._get_rules_for_year(source, end.year))

        events: list[SchoolEvent] = []
        for rule in rules:
            if self._rule_intersects(rule, start.date(), end.date()):
                events.append(self._create_event(rule, start, end))

        return sorted(events, key=lambda event: event.start)

    def get_rules(self, year: int) -> list[SchoolRule]:
        """Return all rules for a given year from all configured sources."""

        rules: list[SchoolRule] = []
        for source in self._sources:
            rules.extend(self._get_rules_for_year(source, year))
        return rules

    def _get_rules_for_year(self, source: SchoolDataSource, year: int) -> list[SchoolRule]:
        """Return cached rules for a source/year pair."""

        cache_key = (getattr(source, "name", "unknown"), year)
        if cache_key not in self._cache:
            self._cache[cache_key] = source.get_rules(year)
        return list(self._cache[cache_key])

    def _rule_intersects(self, rule: SchoolRule, start_day: date, end_day: date) -> bool:
        """Return whether a rule overlaps the requested date range."""

        if rule.end_date is None:
            return rule.start_date <= end_day and rule.start_date >= start_day

        return rule.start_date <= end_day and rule.end_date >= start_day

    def _create_event(self, rule: SchoolRule, start: datetime, end: datetime) -> SchoolEvent:
        """Create a normalized school event from a rule."""

        event_start = dt_util.start_of_local_day(rule.start_date)
        event_end = dt_util.start_of_local_day(rule.end_date or rule.start_date + timedelta(days=1))
        return SchoolEvent(
            summary=rule.summary or rule.name,
            start=event_start,
            end=event_end,
            description=rule.description,
            kind=rule.kind,
            metadata=rule.metadata,
        )
