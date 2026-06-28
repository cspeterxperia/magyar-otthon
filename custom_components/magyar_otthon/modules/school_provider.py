"""Provider interface for the future school engine."""

from __future__ import annotations

from typing import Protocol

from homeassistant.components.calendar import CalendarEvent

from .school_engine import SchoolEngine


class SchoolProvider(Protocol):
    """Interface for providers that expose school events."""

    name: str

    async def async_get_events(self, start_date, end_date) -> list[CalendarEvent]:
        """Return school events in the requested range."""
