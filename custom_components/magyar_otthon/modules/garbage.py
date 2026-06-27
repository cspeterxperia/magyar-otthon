"""Hulladékszállítás számítási modul."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(slots=True)
class GarbageSchedule:
    """Egy hulladéktípus ürítési szabálya."""

    name: str
    start_date: date
    weekday: int  # hétfő=0 ... vasárnap=6
    interval_days: int = 7
    active_from_month: int = 1
    active_to_month: int = 12


def is_collection_day(schedule: GarbageSchedule, day: date) -> bool:
    """Igaz, ha az adott napon ürítés van."""

    if not schedule.active_from_month <= day.month <= schedule.active_to_month:
        return False

    if day.weekday() != schedule.weekday:
        return False

    diff = (day - schedule.start_date).days

    if diff < 0:
        return False

    return diff % schedule.interval_days == 0


def next_collection(schedule: GarbageSchedule, from_day: date) -> date:
    """Következő ürítési nap."""

    day = from_day

    for _ in range(730):
        if is_collection_day(schedule, day):
            return day

        day += timedelta(days=1)

    raise RuntimeError("Nem található következő ürítési nap.")