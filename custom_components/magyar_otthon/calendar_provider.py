"""Calendar data provider interface for Magyar Otthon."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from homeassistant.components.calendar import CalendarEvent


class CalendarDataProvider(Protocol):
    """Interface for calendar data providers."""

    name: str

    async def async_get_events(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events for the requested time range."""
