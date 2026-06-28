"""School data source implementations prepared for future extension."""

from __future__ import annotations

from .school_models import SchoolDataSource, SchoolRule


class BMDecreeSource(SchoolDataSource):
    """Placeholder source for future BM decree-based school data."""

    name = "bm_decree"

    def get_rules(self, year: int) -> list[SchoolRule]:
        """Return rules for the requested year."""

        del year
        return []


class JsonSource(SchoolDataSource):
    """Placeholder source for future JSON-backed school data."""

    name = "json"

    def get_rules(self, year: int) -> list[SchoolRule]:
        """Return rules for the requested year."""

        del year
        return []


class IcsSource(SchoolDataSource):
    """Placeholder source for future ICS-backed school data."""

    name = "ics"

    def get_rules(self, year: int) -> list[SchoolRule]:
        """Return rules for the requested year."""

        del year
        return []


class RestApiSource(SchoolDataSource):
    """Placeholder source for future REST API-backed school data."""

    name = "rest_api"

    def get_rules(self, year: int) -> list[SchoolRule]:
        """Return rules for the requested year."""

        del year
        return []


class LocalFileSource(SchoolDataSource):
    """Placeholder source for future local-file-backed school data."""

    name = "local_file"

    def get_rules(self, year: int) -> list[SchoolRule]:
        """Return rules for the requested year."""

        del year
        return []


class ManualSource(SchoolDataSource):
    """Placeholder source for future manual school data entries."""

    name = "manual"

    def get_rules(self, year: int) -> list[SchoolRule]:
        """Return rules for the requested year."""

        del year
        return []
