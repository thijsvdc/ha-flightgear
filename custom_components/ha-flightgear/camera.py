# camera.py
"""Support for FlightGear camera."""
from __future__ import annotations

import logging
from typing import Any

import requests
from homeassistant.components.camera import Camera, CameraEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_HTTP_PORT, CONF_RTSP_PORT

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the FlightGear camera."""
    camera_entity = FlightGearCamera(
        config_entry.data,
        CameraEntityDescription(
            key="flightgear_view",
            name="View",
        ),
    )
    async_add_entities([camera_entity], True)

class FlightGearCamera(Camera):
    """Implementation of the FlightGear camera."""

    def __init__(
        self,
        config: dict[str, Any],
        description: CameraEntityDescription,
    ) -> None:
        """Initialize the camera."""
        super().__init__()
        self.entity_description = description
        self._attr_unique_id = f"{config[CONF_HOST]}_camera"
        self._attr_name = f"{config[CONF_NAME]} {description.name}"
        self._host = config[CONF_HOST]
        self._http_port = config[CONF_HTTP_PORT]
        self._rtsp_port = config[CONF_RTSP_PORT]
        self._attr_has_entity_name = True
        
        # Set up URLs for still image and streaming
        self._still_image_url = f"http://{self._host}:{self._http_port}/screenshot"
        self._stream_source = f"rtsp://{self._host}:{self._rtsp_port}/flightgear"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": "FlightGear Simulator",
            "manufacturer": "FlightGear",
            "model": "Flight Simulator",
            "sw_version": "2025.1.0",
        }

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of camera image."""
        return await self.hass.async_add_executor_job(self._camera_image)

    def _camera_image(self) -> bytes | None:
        """Get camera image."""
        try:
            response = requests.get(self._still_image_url, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as error:
            _LOGGER.error("Error getting camera image: %s", error)
            return None

    @property
    def stream_source(self) -> str | None:
        """Return the source of the stream."""
        return self._stream_source

    @property
    def supported_features(self) -> int:
        """Return supported features."""
        return self.SUPPORT_STREAM
