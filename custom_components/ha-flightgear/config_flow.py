"""Config flow for FlightGear integration."""
from __future__ import annotations

import logging
import socket
import asyncio
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
    _LOGGER.debug("Starting connection validation to %s:%s", data[CONF_HOST], data[CONF_TELNET_PORT])

    try:
        # Create a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout
        
        _LOGGER.debug("Socket created, attempting connection...")
        
        # Convert the socket connect to an async operation
        await hass.async_add_executor_job(
            sock.connect, (data[CONF_HOST], data[CONF_TELNET_PORT])
        )
        
        _LOGGER.debug("Connected successfully, attempting to receive data...")
        
        # Try to receive some data
        try:
            initial_data = await hass.async_add_executor_job(
                sock.recv, 1024
            )
            _LOGGER.debug("Received data: %s", initial_data)
        except socket.timeout:
            _LOGGER.error("Timeout while receiving data")
            raise CannotConnect("Timeout while receiving data")
        
        # Close the socket properly
        sock.close()
        _LOGGER.debug("Connection test completed successfully")
        
        if not initial_data:
            _LOGGER.error("No data received from FlightGear")
            raise CannotConnect("No data received from FlightGear")
        
    except socket.timeout:
        _LOGGER.error("Connection timed out")
        raise CannotConnect("Connection timed out")
    except ConnectionRefusedError:
        _LOGGER.error("Connection refused")
        raise CannotConnect("Connection refused")
    except socket.gaierror:
        _LOGGER.error("Address resolution error")
        raise CannotConnect("Address resolution error")
    except Exception as err:
        _LOGGER.exception("Unexpected error during connection test")
        raise CannotConnect(f"Unexpected error: {str(err)}")

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
                _LOGGER.debug("Processing user input: %s", user_input)
                info = await validate_input(self.hass, user_input)
                _LOGGER.debug("Validation successful, creating entry")
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect as err:
                _LOGGER.error("Cannot connect: %s", str(err))
                errors["base"] = "cannot_connect"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception: %s", str(err))
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
    def __init__(self, message="Failed to connect"):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
