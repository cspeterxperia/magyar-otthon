"""Options flow for Magyar Otthon."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import (
    CONF_CALENDAR_COLOR,
    CONF_COUNTRY,
    CONF_COUNTY,
    CONF_CUSTOM_CALENDAR_ENABLED,
    CONF_GARBAGE_ENABLED,
    CONF_HOLIDAYS_ENABLED,
    CONF_MUNICIPALITY,
    CONF_NAMEDAYS_ENABLED,
    CONF_REFRESH_INTERVAL,
    CONF_SCHOOL_ENABLED,
    CONF_SCHOOL_TYPE,
    CONF_WASTE_PROVIDER,
    DEFAULT_OPTIONS,
    DOMAIN,
)


class MagyarOtthonOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle integration options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow."""

        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the integration options."""

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {**DEFAULT_OPTIONS, **self.config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_HOLIDAYS_ENABLED, default=options[CONF_HOLIDAYS_ENABLED]): bool,
                    vol.Optional(CONF_SCHOOL_ENABLED, default=options[CONF_SCHOOL_ENABLED]): bool,
                    vol.Optional(CONF_GARBAGE_ENABLED, default=options[CONF_GARBAGE_ENABLED]): bool,
                    vol.Optional(CONF_NAMEDAYS_ENABLED, default=options[CONF_NAMEDAYS_ENABLED]): bool,
                    vol.Optional(CONF_CUSTOM_CALENDAR_ENABLED, default=options[CONF_CUSTOM_CALENDAR_ENABLED]): bool,
                    vol.Optional(CONF_COUNTRY, default=options[CONF_COUNTRY]): str,
                    vol.Optional(CONF_COUNTY, default=options[CONF_COUNTY]): str,
                    vol.Optional(CONF_MUNICIPALITY, default=options[CONF_MUNICIPALITY]): str,
                    vol.Optional(CONF_WASTE_PROVIDER, default=options[CONF_WASTE_PROVIDER]): str,
                    vol.Optional(CONF_SCHOOL_TYPE, default=options[CONF_SCHOOL_TYPE]): str,
                    vol.Optional(CONF_CALENDAR_COLOR, default=options[CONF_CALENDAR_COLOR]): str,
                    vol.Optional(CONF_REFRESH_INTERVAL, default=options[CONF_REFRESH_INTERVAL]): int,
                }
            ),
        )
