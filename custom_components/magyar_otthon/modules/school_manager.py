"""Manager for future school engine initialization and extension points."""

from __future__ import annotations

from .school_engine import SchoolEngine
from .school_models import SchoolDataSource


class SchoolManager:
    """Create and configure the school engine for future integrations."""

    def __init__(self, engine: SchoolEngine | None = None) -> None:
        """Initialize the manager with an engine instance."""

        self._engine = engine or SchoolEngine()

    def get_engine(self) -> SchoolEngine:
        """Return the configured school engine."""

        return self._engine

    def register_source(self, source: SchoolDataSource) -> None:
        """Register a new school source."""

        self._engine.register_source(source)
