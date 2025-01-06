"""Config flow for FlightGear integration."""
from __future__ import annotations

import logging
import socket
import telnetlib
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
    
    async def try_connect():
        """Try to connect to FlightGear."""
        try:
            # Create telnet connection with longer timeout
            tn = telnetlib.Telnet(timeout=10)
            _LOGGER.debug("Attempting to connect to %s:%s", data[CONF_HOST], data[CONF_TELNET_PORT])
            
            # Connect
            tn.open(data[CONF_HOST], data[CONF_TELNET_PORT])
            
            # Wait for data
            _LOGGER.debug("Connected, waiting for data...")
            response = tn.read_until(b"\n", timeout=5)
            _LOGGER.debug("Received data: %s", response)
            
            # Close connection
            tn.close()
            
            if not response:
                raise CannotConnect("No data received from FlightGear")
                
            return True
            
        except EOFError:
            _LOGGER.error("Connection closed by FlightGear")
            raise CannotConnect("Connection closed by FlightGear")
        except ConnectionRefusedError:
            _LOGGER.error("Connection refused")
            raise CannotConnect("Connection refused by FlightGear")
        except socket.timeout:
            _LOGGER.error("Connection timed out")
            raise CannotConnect("Connection timed out")
        except Exception as err:
            _LOGGER.exception("Unexpected error")
            raise CannotConnect(f"Connection error: {str(err)}")
        finally:
            try:
                tn.close()
            except Exception:  # pylint: disable=broad-except
                pass

    try:
        await hass.async_add_executor_job(try_connect)
    except Exception as err:
        _LOGGER.error("Failed to connect: %s", str(err))
        raise

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
