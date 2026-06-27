"""Calendar platform for Magyar Otthon."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .calendar_provider import CalendarDataProvider
from .const import DOMAIN
from .coordinator import MagyarOtthonCoordinator
from .modules.holidays import HolidaysCalendarProvider


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the calendar platform."""

    coordinator: MagyarOtthonCoordinator = hass.data[DOMAIN][entry.entry_id]
    providers: list[CalendarDataProvider] = [HolidaysCalendarProvider()]
    async_add_entities([MagyarOtthonCalendar(coordinator, entry.entry_id, providers)])


class MagyarOtthonCalendar(
    CoordinatorEntity[MagyarOtthonCoordinator],
    CalendarEntity,
):
    """Magyar Otthon calendar entity."""

    _attr_has_entity_name = True
    _attr_name = "Magyar Naptár"

    def __init__(
        self,
        coordinator: MagyarOtthonCoordinator,
        entry_id: str,
        providers: list[CalendarDataProvider],
    ) -> None:
        """Initialize the calendar entity."""

        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_magyar_naptar"
        self._providers = providers
        self._next_event: CalendarEvent | None = None

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""

        return self.coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """Refresh the next event when the entity is added."""

        await super().async_added_to_hass()
        await self.async_update()

    async def async_update(self) -> None:
        """Refresh the cached next event from all providers."""

        self._next_event = await self._get_next_upcoming_event()

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event from the available providers."""

        return self._next_event

    async def _get_next_upcoming_event(self) -> CalendarEvent | None:
        """Collect and return the nearest future event from all providers."""

        now = dt_util.now()
        end_date = now + timedelta(days=365)
        upcoming_events: list[CalendarEvent] = []

        for provider in self._providers:
            upcoming_events.extend(
                await provider.async_get_events(now, end_date)
            )

        future_events = [event for event in upcoming_events if event.start >= now]
        if not future_events:
            return None

        return min(future_events, key=lambda event: event.start)

    async def async_get_events(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return events from all providers within the requested range."""

        events: list[CalendarEvent] = []
        for provider in self._providers:
            events.extend(await provider.async_get_events(start_date, end_date))

        return sorted(events, key=lambda event: event.start)

    def _handle_coordinator_update(self) -> None:
        """Handle updated coordinator data."""

        self.hass.async_create_task(self._async_refresh_state())

    async def _async_refresh_state(self) -> None:
        """Refresh the cached event state and publish it."""

        await self.async_update()
        self.async_write_ha_state()