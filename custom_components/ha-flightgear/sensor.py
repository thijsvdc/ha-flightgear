"""Support for FlightGear sensors."""
from __future__ import annotations

import logging
import socket
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfLength,
    UnitOfSpeed,
    UnitOfTemperature,
    CONF_HOST,
    CONF_NAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CONF_TELNET_PORT

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=1)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="altitude",
        name="Altitude",
        native_unit_of_measurement=UnitOfLength.FEET,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="speed",
        name="Speed",
        native_unit_of_measurement=UnitOfSpeed.KNOTS,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="heading",
        name="Heading",
        native_unit_of_measurement="°",
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the FlightGear sensor."""
    entities = []
    for description in SENSOR_TYPES:
        entities.append(
            FlightGearSensor(
                config_entry.data,
                description,
            )
        )
    async_add_entities(entities, True)

class FlightGearSensor(SensorEntity):
    """Implementation of the FlightGear sensor."""

    def __init__(
        self,
        config: dict[str, Any],
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        self._attr_unique_id = f"{config[CONF_HOST]}_{description.key}"
        self._attr_name = f"{config[CONF_NAME]} {description.name}"
        self._host = config[CONF_HOST]
        self._port = config[CONF_TELNET_PORT]
        self._attr_native_value = None
        self._attributes: dict[str, Any] = {}
        self._attr_has_entity_name = True
        self._attr_should_poll = True

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

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        try:
            data = await self.hass.async_add_executor_job(self._fetch_data)
            if data:
                self._attr_native_value = data.get(self.entity_description.key)
                self._attributes = data
        except Exception as error:
            _LOGGER.error("Error updating FlightGear sensor: %s", error)

    def _fetch_data(self) -> dict[str, Any]:
        """Fetch data from FlightGear."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(10)
            sock.connect((self._host, self._port))
            data = sock.recv(1024).decode()
            parsed_data = data.strip().split(',')
            return {
                "altitude": float(parsed_data[0]),
                "speed": float(parsed_data[1]),
                "heading": float(parsed_data[2]),
                "latitude": float(parsed_data[3]),
                "longitude": float(parsed_data[4]),
            }
