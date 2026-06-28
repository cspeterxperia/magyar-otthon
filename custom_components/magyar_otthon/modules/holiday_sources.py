"""Holiday source implementations for the Hungarian holiday engine."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Final

from .holiday_models import HolidayRule, HolidaySource


FIXED_HOLIDAYS: Final[dict[tuple[int, int], str]] = {
    (1, 1): "Újév",
    (3, 15): "1848-as forradalom és szabadságharc",
    (5, 1): "Munka ünnepe",
    (8, 20): "Szent István ünnepe",
    (10, 23): "1956-os forradalom",
    (11, 1): "Mindenszentek",
    (12, 25): "Karácsony első napja",
    (12, 26): "Karácsony második napja",
}


class FixedHolidaySource(HolidaySource):
    """Provide fixed Hungarian public holidays."""

    name = "fixed"

    def get_holidays(self, year: int) -> list[HolidayRule]:
        """Return fixed holiday rules for the given year."""

        return [
            HolidayRule(
                name=self.name,
                holiday_date=date(year, month, day),
                summary=summary,
            )
            for (month, day), summary in FIXED_HOLIDAYS.items()
        ]


class MovableHolidaySource(HolidaySource):
    """Provide movable Hungarian public holidays."""

    name = "movable"

    def get_holidays(self, year: int) -> list[HolidayRule]:
        """Return movable holiday rules for the given year."""

        easter_sunday = self._easter_sunday(year)
        return [
            HolidayRule(
                name=self.name,
                holiday_date=easter_sunday - timedelta(days=2),
                summary="Nagypéntek",
            ),
            HolidayRule(
                name=self.name,
                holiday_date=easter_sunday,
                summary="Húsvét vasárnap",
            ),
            HolidayRule(
                name=self.name,
                holiday_date=easter_sunday + timedelta(days=1),
                summary="Húsvét hétfő",
            ),
            HolidayRule(
                name=self.name,
                holiday_date=easter_sunday + timedelta(days=49),
                summary="Pünkösd vasárnap",
            ),
            HolidayRule(
                name=self.name,
                holiday_date=easter_sunday + timedelta(days=50),
                summary="Pünkösd hétfő",
            ),
        ]

    def _easter_sunday(self, year: int) -> date:
        """Calculate Easter Sunday for a given year using the Meeus/Jones/Butcher algorithm."""

        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        return date(year, month, day)


class GovernmentHolidaySource(HolidaySource):
    """Placeholder source for government-issued holiday changes."""

    name = "government"

    def get_holidays(self, year: int) -> list[HolidayRule]:
        """Return government holiday rules for the given year."""

        del year
        return []


class WorkdayTransferSource(HolidaySource):
    """Placeholder source for workday-transfer rules."""

    name = "workday_transfer"

    def get_holidays(self, year: int) -> list[HolidayRule]:
        """Return workday transfer rules for the given year."""

        del year
        return []


class SchoolHolidaySource(HolidaySource):
    """Placeholder source for school calendar holidays."""

    name = "school"

    def get_holidays(self, year: int) -> list[HolidayRule]:
        """Return school holiday rules for the given year."""

        del year
        return []


class UserHolidaySource(HolidaySource):
    """Placeholder source for user-defined holidays."""

    name = "user"

    def get_holidays(self, year: int) -> list[HolidayRule]:
        """Return user-defined holiday rules for the given year."""

        del year
        return []
