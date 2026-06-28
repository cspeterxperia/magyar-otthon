"""Config flow a Magyar Otthon integrációhoz."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN
from .options_flow import MagyarOtthonOptionsFlowHandler


class MagyarOtthonConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Magyar Otthon."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        """Create the options flow for this integration."""

        return MagyarOtthonOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(
                title="Magyar Otthon",
                data={},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
        )