# External Data Feeds — Design Spec

Three new independent platform plugins for displaying external data feeds on the DashMachine dashboard: RSS, iCalendar, and Weather Forecast.

## Approach

Three standalone platform plugins in `dashmachine/platform/`, following the existing pattern (each exports a `Platform` class with `__init__` and `process()`). No shared abstraction layer — each plugin is self-contained.

## RSS Platform (`platform/rss.py`)

**Config:**
```ini
[my-rss-feed]
platform = rss
url = https://example.com/feed.xml
max_items = 5
show_date = true
show_description = true
```

- Fetches and parses RSS 2.0 and Atom feeds using `feedparser`
- Displays as a Materialize `collection` list: linked titles, optional dates in muted text, optional truncated descriptions
- Errors render inline as themed error messages

**New dependency:** `feedparser`

## iCalendar Platform (`platform/icalendar.py`)

**Config:**
```ini
[my-calendar]
platform = icalendar
url = https://example.com/calendar.ics
max_events = 5
days_ahead = 14
```

- Fetches `.ics` files over HTTP (public iCal URLs)
- Parses with `icalendar` library + `python-dateutil` for recurrence/timezone handling
- Shows upcoming events within `days_ahead` window, sorted chronologically
- Agenda-style `collection` list: event summary, date/time (or "All day"), optional location

**New dependencies:** `icalendar`, `python-dateutil`

**Out of scope:** CalDAV authentication, event creation, multi-calendar merging.

## Weather Forecast Platform (`platform/weather_forecast.py`)

**Config:**
```ini
[my-forecast]
platform = weather_forecast
latitude = 52.52
longitude = 13.41
temp_unit = c
wind_speed_unit = kph
days = 5
```

- Uses Open-Meteo `daily` forecast endpoint (no API key needed)
- Imports `get_weather_icon()` and `get_weather_desc()` from existing `weather.py`
- Shows daily max/min temps, weather icons, precipitation probability
- Horizontal row of day columns — widget style, visually distinct from list-style cards
- `days` parameter controls forecast length (1-7, default 5)

**No new dependencies.** Reuses `requests` and the Open-Meteo API.

**Relationship to `weather.py`:** Separate plugin. `weather.py` = current conditions. `weather_forecast.py` = multi-day outlook. Both can coexist.

## Template Apps

Add template INI files in `template_apps/` for each new platform:
- `template_apps/rss.ini`
- `template_apps/icalendar.ini`
- `template_apps/weather_forecast.ini`

## Dependencies Update

Add to `requirements.txt`:
- `feedparser`
- `icalendar`
- `python-dateutil`
