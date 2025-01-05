# ha-flightgear

A Home Assistant custom integration for FlightGear Flight Simulator, providing real-time flight data and video streaming capabilities.

## Features

- Real-time flight data (altitude, speed, heading, position)
- Live video streaming from FlightGear
- Automatic dashboard casting to Google Home devices
- Custom services for manual control

## Installation

### HACS Installation
1. Add this repository to HACS as a custom repository
   - URL: `https://github.com/yourusername/ha-flightgear`
   - Category: Integration
2. Install the integration through HACS
3. Restart Home Assistant

### Configuration

The integration can be configured through the UI:
1. Go to Configuration -> Integrations
2. Click the + button and search for "FlightGear"
3. Enter your FlightGear connection details

## Usage

After installation, you can:
- View flight data in Home Assistant
- Create automations based on flight parameters
- Cast flight dashboard to Google Home devices
- Stream live FlightGear video

## Requirements

- FlightGear must be configured to:
  - Enable telnet output on specified port
  - Enable HTTP screenshot server
  - Configure RTSP streaming (optional)

## License

MIT License - see LICENSE file
