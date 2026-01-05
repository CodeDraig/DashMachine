"""
##### Weather
Weather data provided by [Open-Meteo](https://open-meteo.com/).
No API key required.

```ini
[variable_name]
platform = weather
latitude = 52.52
longitude = 13.41
temp_unit = c
wind_speed_unit = kph
```
> **Returns:** HTML for custom card
"""

import requests
from flask import render_template_string

# WMO Weather interpretation codes (WW)
# Code	Description
# 0	Clear sky
# 1, 2, 3	Mainly clear, partly cloudy, and overcast
# 45, 48	Fog and depositing rime fog
# 51, 53, 55	Drizzle: Light, moderate, and dense intensity
# 56, 57	Freezing Drizzle: Light and dense intensity
# 61, 63, 65	Rain: Slight, moderate and heavy intensity
# 66, 67	Freezing Rain: Light and heavy intensity
# 71, 73, 75	Snow fall: Slight, moderate, and heavy intensity
# 77	Snow grains
# 80, 81, 82	Rain showers: Slight, moderate, and violent
# 85, 86	Snow showers slight and heavy
# 95, 96, 99	Thunderstorm: Slight or moderate

def get_weather_icon(code):
    # Mapping WMO codes to Emojis for simplicity and robustness
    if code == 0: return "☀️"
    if code in [1, 2]: return "mw-cloudy" # Partly cloudy
    if code == 3: return "☁️"
    if code in [45, 48]: return "🌫️"
    if code in [51, 53, 55, 56, 57]: return "🌧️"
    if code in [61, 63, 65, 66, 67, 80, 81, 82]: return "🌧️"
    if code in [71, 73, 75, 77, 85, 86]: return "❄️"
    if code in [95, 96, 99]: return "⛈️"
    return "❓"

def get_weather_desc(code):
    codes = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Drizzle: Light", 53: "Drizzle: Moderate", 55: "Drizzle: Dense",
        56: "Freezing Drizzle: Light", 57: "Freezing Drizzle: Dense",
        61: "Rain: Slight", 63: "Rain: Moderate", 65: "Rain: Heavy",
        66: "Freezing Rain: Light", 67: "Freezing Rain: Heavy",
        71: "Snow: Slight", 73: "Snow: Moderate", 75: "Snow: Heavy",
        77: "Snow grains",
        80: "Rain showers: Slight", 81: "Rain showers: Moderate", 82: "Rain showers: Violent",
        85: "Snow showers: Slight", 86: "Snow showers: Heavy",
        95: "Thunderstorm", 96: "Thunderstorm: Slight Hail", 99: "Thunderstorm: Heavy Hail"
    }
    return codes.get(code, "Unknown")

class Platform:
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            self.__dict__[key] = value

        if not hasattr(self, "latitude"):
            self.latitude = 52.52 # Default to Berlin
        if not hasattr(self, "longitude"):
            self.longitude = 13.41
        
        # Open-Meteo handles units in the request usually, but we can do client side conv if needed to match old logic
        # For simplicity, we'll map config to API params where possible
        
        self.temp_unit = "celsius" if getattr(self, "temp_unit", "c").lower() == "c" else "fahrenheit"
        self.wind_speed_unit = "kmh" if getattr(self, "wind_speed_unit", "kph").lower() == "kph" else "mph"
        # precipitation_unit default mm
        
        self.html_template = """
        <div class="row">
            <div class="col s6">
                <span class="mt-0 mb-0 theme-primary-text font-weight-700" style="font-size: 36px">{{ current.temperature_2m }}&deg;{{ temp_symbol }}</span>
            </div>
            <div class="col s6 right-align">
                <span style="font-size: 48px">{{ icon }}</span>
            </div>
        </div>
        <div class="row">
            <h6 class="font-weight-900 center theme-muted-text">{{ desc }}</h6>
        </div>
        <div class="row center-align">
            <div class="col s12">
                <div class="collection theme-muted-text">
                     <div class="collection-item"><span class="font-weight-900">Wind: </span>{{ current.wind_speed_10m }} {{ wind_symbol }}</div>
                     <!-- Add more fields if desired, Open-Meteo has many -->
                </div>
            </div>
        </div>
        """

    def process(self):
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={self.latitude}&longitude={self.longitude}&current=temperature_2m,weather_code,wind_speed_10m&temperature_unit={self.temp_unit}&wind_speed_unit={self.wind_speed_unit}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            weather_code = current.get("weather_code", 0)
            
            icon = get_weather_icon(weather_code)
            desc = get_weather_desc(weather_code)
            
            temp_symbol = "C" if self.temp_unit == "celsius" else "F"
            wind_symbol = "km/h" if self.wind_speed_unit == "kmh" else "mph"

            return render_template_string(
                self.html_template,
                current=current,
                icon=icon,
                desc=desc,
                temp_symbol=temp_symbol,
                wind_symbol=wind_symbol
            )
            
        except Exception as e:
            return f"<div class='theme-failure-text'>Weather Error: {e}</div>"
