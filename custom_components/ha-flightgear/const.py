"""Constants for the FlightGear integration."""
from homeassistant.const import Platform

DOMAIN = "HA FlightGear"
PLATFORMS = [Platform.SENSOR, Platform.CAMERA]

DEFAULT_NAME = "FlightGear"
DEFAULT_HOST = "localhost"
DEFAULT_TELNET_PORT = 5500
DEFAULT_HTTP_PORT = 8080
DEFAULT_RTSP_PORT = 8554

CONF_TELNET_PORT = "telnet_port"
CONF_HTTP_PORT = "http_port"
CONF_RTSP_PORT = "rtsp_port"
