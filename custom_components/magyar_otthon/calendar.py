"""Calendar platform for Magyar Otthon."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .calendar_provider import CalendarDataProvider
from .const import CONF_CALENDAR_COLOR, CONF_HOLIDAYS_ENABLED, DEFAULT_OPTIONS, DOMAIN
from .coordinator import MagyarOtthonCoordinator
from .logger import LOGGER
from .modules.holidays import HolidaysCalendarProvider


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the calendar platform."""

    coordinator: MagyarOtthonCoordinator = hass.data[DOMAIN][entry.entry_id]
    options = dict(DEFAULT_OPTIONS)
    options.update(entry.options)
    providers: list[CalendarDataProvider] = []
    if options.get(CONF_HOLIDAYS_ENABLED, True):
        LOGGER.debug("Loading holidays provider for calendar")
        providers.append(HolidaysCalendarProvider())
    LOGGER.debug("Setting up calendar providers: %s", [provider.name for provider in providers])
    async_add_entities([MagyarOtthonCalendar(coordinator, entry.entry_id, providers, options)])


class MagyarOtthonCalendar(
    CoordinatorEntity[MagyarOtthonCoordinator],
    CalendarEntity,
):
    """Magyar Otthon calendar entity."""

    _attr_has_entity_name = True
    _attr_name = "Magyar Naptár"
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: MagyarOtthonCoordinator,
        entry_id: str,
        providers: list[CalendarDataProvider],
        options: dict[str, object],
    ) -> None:
        """Initialize the calendar entity."""

        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_magyar_naptar"
        self._providers = providers
        self._options = options
        self._next_event: CalendarEvent | None = None
        color = options.get(CONF_CALENDAR_COLOR)
        if isinstance(color, str) and color:
            self._attr_initial_color = color

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""

        return self.coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """Refresh the next event when the entity is added."""

        await super().async_added_to_hass()
        await self.async_update()
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Refresh the cached next event from all providers."""

        try:
            self._next_event = await self._get_next_upcoming_event()
        except Exception:  # pragma: no cover - defensive guard for runtime stability
            LOGGER.exception("Failed to refresh calendar events")
            self._next_event = None

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
            try:
                upcoming_events.extend(await provider.async_get_events(now, end_date))
            except Exception:  # pragma: no cover - keep the calendar available if one provider fails
                LOGGER.exception("Failed to fetch events from provider %s", provider.name)

        future_events = []
        for event in upcoming_events:
            start = event.start
            if isinstance(start, datetime):
                is_future = start >= now
            else:
                is_future = start >= now.date()
            if is_future:
                future_events.append(event)

        if not future_events:
            return None

        return min(future_events, key=lambda event: event.start)

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return events from all providers within the requested range."""

        del hass
        events: list[CalendarEvent] = []
        for provider in self._providers:
            try:
                events.extend(await provider.async_get_events(start_date, end_date))
            except Exception:  # pragma: no cover - keep the calendar available if one provider fails
                LOGGER.exception("Failed to fetch events from provider %s", provider.name)

        return sorted(events, key=lambda event: event.start)

    def _handle_coordinator_update(self) -> None:
        """Handle updated coordinator data."""

        self.hass.async_create_task(self._async_refresh_state())

    async def _async_refresh_state(self) -> None:
        """Refresh the cached event state and publish it."""

        await self.async_update()
        self.async_write_ha_state()