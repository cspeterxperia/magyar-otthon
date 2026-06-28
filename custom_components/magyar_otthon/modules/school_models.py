"""Shared data models for the future school engine."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class SchoolRule:
    """A school-related rule that can be resolved by the engine."""

    name: str
    start_date: date
    end_date: date | None = None
    kind: str = "unknown"
    summary: str = ""
    description: str = ""
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class SchoolEvent:
    """A normalized school event emitted by the engine."""

    summary: str
    start: datetime
    end: datetime
    description: str = ""
    kind: str = "unknown"
    metadata: dict[str, Any] | None = None


class SchoolDataSource(ABC):
    """Abstract base class for pluggable school data sources."""

    name: str = ""

    @abstractmethod
    def get_rules(self, year: int) -> list[SchoolRule]:
        """Return school rules for the requested year."""
