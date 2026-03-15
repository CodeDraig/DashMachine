"""
##### Weather Forecast
Multi-day weather forecast provided by [Open-Meteo](https://open-meteo.com/).
No API key required.

```ini
[variable_name]
platform = weather_forecast
latitude = 52.52
longitude = 13.41
temp_unit = c
wind_speed_unit = kph
days = 5
```
> **Returns:** HTML for custom card

| Variable        | Required | Description                                            | Options           |
|-----------------|----------|--------------------------------------------------------|-------------------|
| [variable_name] | Yes      | Name for the data source.                              | [variable_name]   |
| platform        | Yes      | Name of the platform.                                  | weather_forecast  |
| latitude        | No       | Latitude. Default: 52.52 (Berlin)                      | float             |
| longitude       | No       | Longitude. Default: 13.41 (Berlin)                     | float             |
| temp_unit       | No       | Temperature unit. Default: c                           | c, f              |
| wind_speed_unit | No       | Wind speed unit. Default: kph                          | kph, mph          |
| days            | No       | Number of forecast days (1-7). Default: 5              | integer           |

> **Working example:**
>```ini
> [my-forecast]
> platform = weather_forecast
> latitude = 40.71
> longitude = -74.01
> temp_unit = f
> days = 5
>
> [NYC Weather]
> type = custom
> data_sources = my-forecast
>```
"""

import requests
from datetime import datetime
from flask import render_template_string
from dashmachine.platform.weather import get_weather_icon, get_weather_desc


class Platform:
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            self.__dict__[key] = value

        if not hasattr(self, "latitude"):
            self.latitude = 52.52
        if not hasattr(self, "longitude"):
            self.longitude = 13.41

        self.temp_unit = "celsius" if getattr(self, "temp_unit", "c").lower() == "c" else "fahrenheit"
        self.wind_speed_unit = "kmh" if getattr(self, "wind_speed_unit", "kph").lower() == "kph" else "mph"
        self.days = max(1, min(7, int(getattr(self, "days", "5"))))

        self.html_template = """
        <div class="row center-align" style="margin-bottom: 0;">
            {% for day in forecast %}
            <div class="col" style="flex: 1; padding: 4px;">
                <div class="theme-muted-text" style="font-size: 0.8em; font-weight: 700;">{{ day.name }}</div>
                <div style="font-size: 28px; line-height: 1.2;">
                    {% if day.icon_is_class %}<i class="mw {{ day.icon }}"></i>{% else %}{{ day.icon }}{% endif %}
                </div>
                <div class="theme-primary-text font-weight-700" style="font-size: 0.9em;">{{ day.max }}&deg;</div>
                <div class="theme-muted-text" style="font-size: 0.8em;">{{ day.min }}&deg;</div>
                {% if day.precip_prob is not none %}
                <div class="theme-muted-text" style="font-size: 0.75em;">{{ day.precip_prob }}%</div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        """

    def process(self):
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={self.latitude}&longitude={self.longitude}"
                f"&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_probability_max"
                f"&temperature_unit={self.temp_unit}"
                f"&wind_speed_unit={self.wind_speed_unit}"
                f"&forecast_days={self.days}"
            )
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            daily = data.get("daily", {})
            forecast = []
            for i in range(len(daily.get("time", [])[:self.days])):
                dt = datetime.strptime(daily["time"][i], "%Y-%m-%d")
                icon = get_weather_icon(daily["weather_code"][i])
                icon_is_class = icon.isascii() and icon.replace("-", "").replace("_", "").isalpha()
                precip_list = daily.get("precipitation_probability_max", [])
                forecast.append(
                    {
                        "name": dt.strftime("%a"),
                        "icon": icon,
                        "icon_is_class": icon_is_class,
                        "desc": get_weather_desc(daily["weather_code"][i]),
                        "max": daily["temperature_2m_max"][i],
                        "min": daily["temperature_2m_min"][i],
                        "precip_prob": precip_list[i] if i < len(precip_list) else None,
                    }
                )

            return render_template_string(self.html_template, forecast=forecast)
        except Exception as e:
            return f"<div class='theme-failure-text'>Forecast Error: {e}</div>"
