# External Data Feeds — Design Spec

Three new independent platform plugins for displaying external data feeds on the DashMachine dashboard: RSS, iCalendar, and Weather Forecast.

## Approach

Three standalone platform plugins in `dashmachine/platform/`, following the existing pattern (each exports a `Platform` class with `__init__` and `process()`). No shared abstraction layer — each plugin is self-contained.

### Common conventions across all three plugins

- **Rendering:** Each plugin defines an inline `self.html_template` Jinja string in `__init__` and renders it via `render_template_string()` in `process()`, matching the `weather.py` pattern. No user-supplied `value_template`.
- **Return contract:** `process()` returns an HTML string. On error, it returns a `<div class='theme-failure-text'>` message, matching `weather.py`.
- **Type coercion:** All config values arrive as strings from the INI parser. `__init__` must cast explicitly: `int()` for counts/days, `float()` for coordinates, string comparison for booleans (e.g., `getattr(self, "show_date", "true").lower() == "true"`).
- **HTTP timeout:** All `requests.get()` calls use `timeout=10`, matching existing plugins.
- **Docstrings:** Each plugin includes a module-level docstring with INI config example, variable table, and working example — matching the `sonarr.py`/`weather.py` documentation convention.

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
- Errors (bad URL, parse failure, timeout) render inline as themed error messages

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
- Parses with `icalendar` library + `recurring-ical-events` for recurrence expansion within the `days_ahead` window
- Shows upcoming events sorted chronologically
- Agenda-style `collection` list: event summary, date/time (or "All day"), optional location

**New dependencies:** `icalendar`, `python-dateutil`, `recurring-ical-events`

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
- `days` parameter: clamped to 1-7 range in `__init__`, default 5
- **Icon handling:** `get_weather_icon()` returns mixed types (emoji strings and CSS class name `"mw-cloudy"`). The forecast template must handle both: if the value contains no spaces and is ASCII-only, treat as a CSS icon class; otherwise render as inline text.

**No new dependencies.** Reuses `requests` and the Open-Meteo API.

**Relationship to `weather.py`:** Separate plugin. `weather.py` = current conditions. `weather_forecast.py` = multi-day outlook. Both can coexist.

## Caching

No plugin-level caching in this iteration. Each `process()` call makes a network request, matching the existing behavior of `weather.py` and other platforms. Flask-Caching is already available in the app if caching is needed later.

## Dependencies Update

Add to `requirements.txt` (pinned):
- `feedparser==6.0.11`
- `icalendar==6.1.3`
- `python-dateutil==2.9.0`
- `recurring-ical-events==3.5.1`
