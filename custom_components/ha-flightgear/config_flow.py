import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_HOST,
    DEFAULT_TELNET_PORT,
    DEFAULT_HTTP_PORT,
    DEFAULT_RTSP_PORT,
    CONF_TELNET_PORT,
    CONF_HTTP_PORT,
    CONF_RTSP_PORT,
)

class FlightGearConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the FlightGear integration."""

    VERSION = 1

    def __init__(self):
        """Initialize the configuration flow."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        self._errors = {}

        if user_input is not None:
            # Validate the input if needed
            errors = await self._validate_input(user_input)
            if not errors:
                return self.async_create_entry(
                    title=user_input.get("name", DEFAULT_NAME), data=user_input
                )
            self._errors.update(errors)

        return self._show_form(user_input)

    async def _validate_input(self, user_input):
        """Validate user input."""
        errors = {}

        # Example validation: Ensure ports are valid integers
        for port_key in [CONF_TELNET_PORT, CONF_HTTP_PORT, CONF_RTSP_PORT]:
            try:
                int(user_input.get(port_key))
            except (ValueError, TypeError):
                errors[port_key] = "invalid_port"

        # Add more validation logic if required

        return errors

    def _show_form(self, user_input):
        """Show the configuration form to the user."""
        default_values = {
            "name": DEFAULT_NAME,
            "host": DEFAULT_HOST,
            CONF_TELNET_PORT: DEFAULT_TELNET_PORT,
            CONF_HTTP_PORT: DEFAULT_HTTP_PORT,
            CONF_RTSP_PORT: DEFAULT_RTSP_PORT,
        }
        fields = {
            vol.Optional("name", default=user_input.get("name", DEFAULT_NAME)): str,
            vol.Required("host", default=user_input.get("host", DEFAULT_HOST)): str,
            vol.Required(
                CONF_TELNET_PORT, default=user_input.get(CONF_TELNET_PORT, DEFAULT_TELNET_PORT)
            ): int,
            vol.Required(
                CONF_HTTP_PORT, default=user_input.get(CONF_HTTP_PORT, DEFAULT_HTTP_PORT)
            ): int,
            vol.Required(
                CONF_RTSP_PORT, default=user_input.get(CONF_RTSP_PORT, DEFAULT_RTSP_PORT)
            ): int,
        }
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(fields), errors=self._errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return FlightGearOptionsFlow(config_entry)


class FlightGearOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for the FlightGear integration."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options for the custom component."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Optional(
                CONF_TELNET_PORT,
                default=self.config_entry.options.get(CONF_TELNET_PORT, DEFAULT_TELNET_PORT),
            ): int,
            vol.Optional(
                CONF_HTTP_PORT,
                default=self.config_entry.options.get(CONF_HTTP_PORT, DEFAULT_HTTP_PORT),
            ): int,
            vol.Optional(
                CONF_RTSP_PORT,
                default=self.config_entry.options.get(CONF_RTSP_PORT, DEFAULT_RTSP_PORT),
            ): int,
        }
        return self.async_show_form(step_id="init", data_schema=vol.Schema(options))
