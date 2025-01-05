"""Config flow for FlightGear integration."""
from __future__ import annotations

import logging
import socket
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

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

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_TELNET_PORT, default=DEFAULT_TELNET_PORT): int,
        vol.Required(CONF_HTTP_PORT, default=DEFAULT_HTTP_PORT): int,
        vol.Required(CONF_RTSP_PORT, default=DEFAULT_RTSP_PORT): int,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""

    try:
        # Test telnet connection
        reader, writer = await hass.loop.create_connection(
            lambda: socket.socket(socket.AF_INET, socket.SOCK_STREAM),
            data[CONF_HOST],
            data[CONF_TELNET_PORT],
        )
        writer.close()
        await writer.wait_closed()
    except Exception as err:
        raise CannotConnect from err

    # Return info that you want to store in the config entry.
    return {"title": data[CONF_NAME]}

class FlightGearConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FlightGear."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
