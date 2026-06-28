"""Shared models for the holiday engine and holiday sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class HolidayRule:
    """A holiday source rule that can be merged into the engine."""

    name: str
    holiday_date: date
    summary: str
    description: str = "Magyar munkaszüneti nap"
    priority: int = 0


class HolidaySource(ABC):
    """Abstract base class for plug-in holiday data sources."""

    name: str = ""

    @abstractmethod
    def get_holidays(self, year: int) -> list[HolidayRule]:
        """Return holiday rules for a given year."""
