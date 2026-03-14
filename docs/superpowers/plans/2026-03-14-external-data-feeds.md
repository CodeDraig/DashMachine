# External Data Feeds Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three new platform plugins (RSS, iCalendar, Weather Forecast) for displaying external data feeds on the DashMachine dashboard.

**Architecture:** Three independent platform plugins in `dashmachine/platform/`, each following the existing `Platform` class pattern (`__init__` with `*args, **kwargs`, `process()` returning HTML). No shared abstractions. Each plugin fetches external data and renders it via inline Jinja templates with `render_template_string()`.

**Tech Stack:** Python 3, Flask, feedparser, icalendar, python-dateutil, recurring-ical-events, Open-Meteo API, Materialize CSS

**Spec:** `docs/superpowers/specs/2026-03-14-external-data-feeds-design.md`

---

## File Structure

| Action | File | Responsibility |
|--------|------|----------------|
| Modify | `requirements.txt` | Add new dependencies |
| Create | `dashmachine/platform/rss.py` | RSS/Atom feed platform plugin |
| Create | `dashmachine/platform/ical.py` | iCalendar platform plugin |
| Create | `dashmachine/platform/weather_forecast.py` | Multi-day weather forecast plugin |
| Create | `tests/test_rss.py` | RSS platform tests |
| Create | `tests/test_ical.py` | iCalendar platform tests |
| Create | `tests/test_weather_forecast.py` | Weather forecast platform tests |

**Note on naming:** The spec calls the file `icalendar.py`, but `icalendar` is also the name of the third-party library we're importing. To avoid import shadowing, use `ical.py` as the filename and `platform = ical` in config.

---

## Chunk 1: Dependencies and RSS Platform

### Task 1: Add Dependencies

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Add new dependencies to requirements.txt**

Append these lines after `pytest==7.4.4`:

```
feedparser==6.0.11
icalendar==6.1.3
python-dateutil==2.9.0
recurring-ical-events==3.5.1
```

- [ ] **Step 2: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: All packages install successfully, no conflicts.

- [ ] **Step 3: Commit**

```bash
git add requirements.txt
git commit -m "deps: add feedparser, icalendar, python-dateutil, recurring-ical-events"
```

---

### Task 2: RSS Platform — Tests

**Files:**
- Create: `tests/test_rss.py`

**Context:** The existing test pattern (see `tests/platform_verification.py`) instantiates `Platform` directly with kwargs — no first positional arg needed since `*args` absorbs it. Tests need a Flask app context for `render_template_string()`. We'll use pytest (already in requirements) rather than the informal print-based style.

- [ ] **Step 1: Write the test file**

```python
import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask
from unittest.mock import patch, MagicMock


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


class TestRSSPlatformInit:
    def test_defaults(self, app):
        with app.app_context():
            from dashmachine.platform.rss import Platform

            p = Platform(url="https://example.com/feed.xml")
            assert p.url == "https://example.com/feed.xml"
            assert p.max_items == 5
            assert p.show_date is True
            assert p.show_description is True

    def test_custom_options(self, app):
        with app.app_context():
            from dashmachine.platform.rss import Platform

            p = Platform(
                url="https://example.com/feed.xml",
                max_items="3",
                show_date="false",
                show_description="false",
            )
            assert p.max_items == 3
            assert p.show_date is False
            assert p.show_description is False

    def test_missing_url(self, app):
        with app.app_context():
            from dashmachine.platform.rss import Platform

            p = Platform()
            result = p.process()
            assert "theme-failure-text" in result
            assert "url" in result.lower()


class TestRSSPlatformProcess:
    def test_successful_feed(self, app):
        with app.app_context():
            from dashmachine.platform.rss import Platform

            mock_feed = MagicMock()
            mock_feed.bozo = False
            mock_feed.entries = [
                MagicMock(
                    title="Test Article",
                    link="https://example.com/1",
                    published="Mon, 01 Jan 2024 00:00:00 GMT",
                    get=lambda k, d=None: {
                        "summary": "A test summary"
                    }.get(k, d),
                ),
                MagicMock(
                    title="Second Article",
                    link="https://example.com/2",
                    published="Tue, 02 Jan 2024 00:00:00 GMT",
                    get=lambda k, d=None: {
                        "summary": "Another summary"
                    }.get(k, d),
                ),
            ]

            with patch("dashmachine.platform.rss.feedparser.parse", return_value=mock_feed):
                p = Platform(url="https://example.com/feed.xml", max_items="2")
                result = p.process()
                assert "Test Article" in result
                assert "Second Article" in result
                assert "collection" in result

    def test_max_items_limits_output(self, app):
        with app.app_context():
            from dashmachine.platform.rss import Platform

            mock_feed = MagicMock()
            mock_feed.bozo = False
            mock_feed.entries = [
                MagicMock(
                    title=f"Article {i}",
                    link=f"https://example.com/{i}",
                    published="Mon, 01 Jan 2024 00:00:00 GMT",
                    get=lambda k, d=None: None,
                )
                for i in range(10)
            ]

            with patch("dashmachine.platform.rss.feedparser.parse", return_value=mock_feed):
                p = Platform(url="https://example.com/feed.xml", max_items="2")
                result = p.process()
                assert "Article 0" in result
                assert "Article 1" in result
                assert "Article 2" not in result

    def test_network_error(self, app):
        with app.app_context():
            from dashmachine.platform.rss import Platform

            with patch(
                "dashmachine.platform.rss.feedparser.parse",
                side_effect=Exception("Connection refused"),
            ):
                p = Platform(url="https://example.com/feed.xml")
                result = p.process()
                assert "theme-failure-text" in result


class TestRSSPlatformDataSourceArg:
    """Test that Platform works when called with a positional data_source arg,
    matching how get_data_source() in main/utils.py calls it:
        platform = module.Platform(data_source, **data_source_args)
    """

    def test_with_positional_data_source(self, app):
        with app.app_context():
            from dashmachine.platform.rss import Platform

            data_source = {"name": "my-rss", "platform": "rss"}
            p = Platform(data_source, url="https://example.com/feed.xml")
            assert p.url == "https://example.com/feed.xml"
            assert p.max_items == 5
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_rss.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'dashmachine.platform.rss'`

- [ ] **Step 3: Commit test file**

```bash
git add tests/test_rss.py
git commit -m "test: add RSS platform tests (red)"
```

---

### Task 3: RSS Platform — Implementation

**Files:**
- Create: `dashmachine/platform/rss.py`

- [ ] **Step 1: Write the RSS platform**

```python
"""
##### RSS
Display items from an RSS or Atom feed.

```ini
[variable_name]
platform = rss
url = https://example.com/feed.xml
max_items = 5
show_date = true
show_description = true
```
> **Returns:** HTML for custom card

| Variable         | Required | Description                                    | Options        |
|------------------|----------|------------------------------------------------|----------------|
| [variable_name]  | Yes      | Name for the data source.                      | [variable_name]|
| platform         | Yes      | Name of the platform.                          | rss            |
| url              | Yes      | URL of the RSS or Atom feed.                   | url            |
| max_items        | No       | Maximum number of items to display. Default: 5 | integer        |
| show_date        | No       | Show publication date. Default: true           | true, false    |
| show_description | No       | Show item description. Default: true           | true, false    |

> **Working example:**
>```ini
> [news-feed]
> platform = rss
> url = https://hnrss.org/frontpage
> max_items = 5
> show_date = true
> show_description = false
>
> [Hacker News]
> type = custom
> data_sources = news-feed
>```
"""

import feedparser
from flask import render_template_string


class Platform:
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            self.__dict__[key] = value

        if not hasattr(self, "url"):
            self.url = None
        self.max_items = int(getattr(self, "max_items", "5"))
        self.show_date = getattr(self, "show_date", "true").lower() == "true"
        self.show_description = getattr(self, "show_description", "true").lower() == "true"

        self.html_template = """
        <div class="collection">
            {% for entry in entries %}
            <a href="{{ entry.link }}" target="_blank" class="collection-item" style="text-decoration: none;">
                <span class="font-weight-900 theme-primary-text">{{ entry.title }}</span>
                {% if show_date and entry.published %}
                <br><span class="theme-muted-text" style="font-size: 0.85em;">{{ entry.published }}</span>
                {% endif %}
                {% if show_description and entry.summary %}
                <br><span class="theme-muted-text" style="font-size: 0.85em;">{{ entry.summary[:120] }}{% if entry.summary|length > 120 %}...{% endif %}</span>
                {% endif %}
            </a>
            {% endfor %}
        </div>
        """

    def process(self):
        if not self.url:
            return "<div class='theme-failure-text'>RSS Error: url is required</div>"
        try:
            feed = feedparser.parse(self.url)
            entries = []
            for entry in feed.entries[: self.max_items]:
                entries.append(
                    {
                        "title": getattr(entry, "title", "Untitled"),
                        "link": getattr(entry, "link", "#"),
                        "published": getattr(entry, "published", None),
                        "summary": entry.get("summary"),
                    }
                )
            return render_template_string(
                self.html_template,
                entries=entries,
                show_date=self.show_date,
                show_description=self.show_description,
            )
        except Exception as e:
            return f"<div class='theme-failure-text'>RSS Error: {e}</div>"
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/test_rss.py -v`
Expected: All tests PASS.

- [ ] **Step 3: Commit**

```bash
git add dashmachine/platform/rss.py
git commit -m "feat: add RSS feed platform plugin"
```

---

## Chunk 2: iCalendar Platform

### Task 4: iCalendar Platform — Tests

**Files:**
- Create: `tests/test_ical.py`

- [ ] **Step 1: Write the test file**

```python
import sys
import os
import pytest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask
from unittest.mock import patch, MagicMock


SAMPLE_ICS = """\
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
DTSTART:{start}
DTEND:{end}
SUMMARY:Team Standup
LOCATION:Room 42
END:VEVENT
BEGIN:VEVENT
DTSTART;VALUE=DATE:{allday}
SUMMARY:Company Holiday
END:VEVENT
END:VCALENDAR
"""

SAMPLE_RECURRING_ICS = """\
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
DTSTART:{start}
DTEND:{end}
SUMMARY:Daily Standup
RRULE:FREQ=DAILY;COUNT=5
END:VEVENT
END:VCALENDAR
"""


def make_recurring_ics(days_offset=0):
    start = datetime.now() + timedelta(days=days_offset)
    end = start + timedelta(hours=1)
    return SAMPLE_RECURRING_ICS.format(
        start=start.strftime("%Y%m%dT%H%M%S"),
        end=end.strftime("%Y%m%dT%H%M%S"),
    )


def make_ics(days_offset_event=1, days_offset_allday=3):
    start = datetime.now() + timedelta(days=days_offset_event)
    end = start + timedelta(hours=1)
    allday = (datetime.now() + timedelta(days=days_offset_allday)).strftime("%Y%m%d")
    return SAMPLE_ICS.format(
        start=start.strftime("%Y%m%dT%H%M%S"),
        end=end.strftime("%Y%m%dT%H%M%S"),
        allday=allday,
    )


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


class TestICalPlatformInit:
    def test_defaults(self, app):
        with app.app_context():
            from dashmachine.platform.ical import Platform

            p = Platform(url="https://example.com/cal.ics")
            assert p.url == "https://example.com/cal.ics"
            assert p.max_events == 5
            assert p.days_ahead == 14

    def test_custom_options(self, app):
        with app.app_context():
            from dashmachine.platform.ical import Platform

            p = Platform(url="https://example.com/cal.ics", max_events="10", days_ahead="30")
            assert p.max_events == 10
            assert p.days_ahead == 30

    def test_missing_url(self, app):
        with app.app_context():
            from dashmachine.platform.ical import Platform

            p = Platform()
            result = p.process()
            assert "theme-failure-text" in result


class TestICalPlatformProcess:
    def test_successful_calendar(self, app):
        with app.app_context():
            from dashmachine.platform.ical import Platform

            mock_response = MagicMock()
            mock_response.text = make_ics()
            mock_response.raise_for_status = MagicMock()

            with patch("dashmachine.platform.ical.requests.get", return_value=mock_response):
                p = Platform(url="https://example.com/cal.ics", days_ahead="14")
                result = p.process()
                assert "Team Standup" in result
                assert "Company Holiday" in result
                assert "collection" in result

    def test_max_events_limits_output(self, app):
        with app.app_context():
            from dashmachine.platform.ical import Platform

            mock_response = MagicMock()
            mock_response.text = make_ics()
            mock_response.raise_for_status = MagicMock()

            with patch("dashmachine.platform.ical.requests.get", return_value=mock_response):
                p = Platform(url="https://example.com/cal.ics", max_events="1", days_ahead="14")
                result = p.process()
                assert "Team Standup" in result
                # Second event may or may not appear depending on sort order,
                # but total rendered events should be limited to 1
                # Count collection-item occurrences
                assert result.count("collection-item") == 1

    def test_network_error(self, app):
        with app.app_context():
            from dashmachine.platform.ical import Platform

            with patch(
                "dashmachine.platform.ical.requests.get",
                side_effect=Exception("Connection refused"),
            ):
                p = Platform(url="https://example.com/cal.ics")
                result = p.process()
                assert "theme-failure-text" in result

    def test_recurring_events(self, app):
        with app.app_context():
            from dashmachine.platform.ical import Platform

            mock_response = MagicMock()
            mock_response.text = make_recurring_ics(days_offset=0)
            mock_response.raise_for_status = MagicMock()

            with patch("dashmachine.platform.ical.requests.get", return_value=mock_response):
                p = Platform(url="https://example.com/cal.ics", max_events="10", days_ahead="7")
                result = p.process()
                assert "Daily Standup" in result
                # RRULE:FREQ=DAILY;COUNT=5 should produce multiple occurrences
                assert result.count("collection-item") >= 2

    def test_shows_location(self, app):
        with app.app_context():
            from dashmachine.platform.ical import Platform

            mock_response = MagicMock()
            mock_response.text = make_ics()
            mock_response.raise_for_status = MagicMock()

            with patch("dashmachine.platform.ical.requests.get", return_value=mock_response):
                p = Platform(url="https://example.com/cal.ics", days_ahead="14")
                result = p.process()
                assert "Room 42" in result


class TestICalPlatformDataSourceArg:
    def test_with_positional_data_source(self, app):
        with app.app_context():
            from dashmachine.platform.ical import Platform

            data_source = {"name": "my-cal", "platform": "ical"}
            p = Platform(data_source, url="https://example.com/cal.ics")
            assert p.url == "https://example.com/cal.ics"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_ical.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'dashmachine.platform.ical'`

- [ ] **Step 3: Commit test file**

```bash
git add tests/test_ical.py
git commit -m "test: add iCalendar platform tests (red)"
```

---

### Task 5: iCalendar Platform — Implementation

**Files:**
- Create: `dashmachine/platform/ical.py`

- [ ] **Step 1: Write the iCalendar platform**

```python
"""
##### iCalendar
Display upcoming events from an iCal (.ics) feed.

```ini
[variable_name]
platform = ical
url = https://example.com/calendar.ics
max_events = 5
days_ahead = 14
```
> **Returns:** HTML for custom card

| Variable        | Required | Description                                          | Options        |
|-----------------|----------|------------------------------------------------------|----------------|
| [variable_name] | Yes      | Name for the data source.                            | [variable_name]|
| platform        | Yes      | Name of the platform.                                | ical           |
| url             | Yes      | URL of the .ics calendar feed.                       | url            |
| max_events      | No       | Maximum number of events to display. Default: 5      | integer        |
| days_ahead      | No       | How many days ahead to look for events. Default: 14  | integer        |

> **Working example:**
>```ini
> [my-calendar]
> platform = ical
> url = https://calendar.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics
> max_events = 5
> days_ahead = 30
>
> [Calendar]
> type = custom
> data_sources = my-calendar
>```
"""

import requests
from datetime import datetime, date, timedelta
from icalendar import Calendar
import recurring_ical_events
from flask import render_template_string


class Platform:
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            self.__dict__[key] = value

        if not hasattr(self, "url"):
            self.url = None
        self.max_events = int(getattr(self, "max_events", "5"))
        self.days_ahead = int(getattr(self, "days_ahead", "14"))

        self.html_template = """
        <div class="collection">
            {% for event in events %}
            <div class="collection-item">
                <span class="font-weight-900 theme-primary-text">{{ event.summary }}</span>
                <span class="secondary-content theme-muted-text" style="font-size: 0.85em;">{{ event.when }}</span>
                {% if event.location %}
                <br><span class="theme-muted-text" style="font-size: 0.85em;">{{ event.location }}</span>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        """

    def process(self):
        if not self.url:
            return "<div class='theme-failure-text'>iCal Error: url is required</div>"
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()

            cal = Calendar.from_ical(response.text)
            start_date = date.today()
            end_date = start_date + timedelta(days=self.days_ahead)
            recurring = recurring_ical_events.of(cal).between(start_date, end_date)

            events = []
            for component in recurring:
                dtstart = component.get("DTSTART")
                if dtstart is None:
                    continue
                dt = dtstart.dt
                if isinstance(dt, datetime):
                    when = dt.strftime("%b %d, %H:%M")
                else:
                    when = "All day — " + dt.strftime("%b %d")

                sort_dt = dt if isinstance(dt, datetime) else datetime.combine(dt, datetime.min.time())
                if hasattr(sort_dt, "tzinfo") and sort_dt.tzinfo is not None:
                    sort_dt = sort_dt.replace(tzinfo=None)

                events.append(
                    {
                        "summary": str(component.get("SUMMARY", "Untitled")),
                        "when": when,
                        "location": str(component.get("LOCATION", "")) or None,
                        "sort_key": sort_dt,
                    }
                )

            events.sort(key=lambda e: e["sort_key"])
            events = events[: self.max_events]

            return render_template_string(self.html_template, events=events)
        except Exception as e:
            return f"<div class='theme-failure-text'>iCal Error: {e}</div>"
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/test_ical.py -v`
Expected: All tests PASS.

- [ ] **Step 3: Commit**

```bash
git add dashmachine/platform/ical.py
git commit -m "feat: add iCalendar platform plugin"
```

---

## Chunk 3: Weather Forecast Platform

### Task 6: Weather Forecast Platform — Tests

**Files:**
- Create: `tests/test_weather_forecast.py`

**Context:** The weather forecast platform imports `get_weather_icon` and `get_weather_desc` from `dashmachine/platform/weather.py`. The `get_weather_icon()` function returns mixed types: emoji strings for most codes, but `"mw-cloudy"` (a CSS class) for codes 1 and 2. The template must handle both.

- [ ] **Step 1: Write the test file**

```python
import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask
from unittest.mock import patch, MagicMock


SAMPLE_FORECAST_RESPONSE = {
    "daily": {
        "time": ["2026-03-14", "2026-03-15", "2026-03-16"],
        "temperature_2m_max": [15.2, 12.8, 18.1],
        "temperature_2m_min": [5.1, 3.4, 7.2],
        "weather_code": [0, 2, 61],
        "precipitation_probability_max": [0, 10, 80],
    }
}


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


class TestWeatherForecastInit:
    def test_defaults(self, app):
        with app.app_context():
            from dashmachine.platform.weather_forecast import Platform

            p = Platform(latitude="52.52", longitude="13.41")
            assert p.days == 5
            assert p.temp_unit == "celsius"

    def test_days_clamped_high(self, app):
        with app.app_context():
            from dashmachine.platform.weather_forecast import Platform

            p = Platform(days="10")
            assert p.days == 7

    def test_days_clamped_low(self, app):
        with app.app_context():
            from dashmachine.platform.weather_forecast import Platform

            p = Platform(days="0")
            assert p.days == 1

    def test_fahrenheit(self, app):
        with app.app_context():
            from dashmachine.platform.weather_forecast import Platform

            p = Platform(temp_unit="f")
            assert p.temp_unit == "fahrenheit"


class TestWeatherForecastProcess:
    def test_successful_forecast(self, app):
        with app.app_context():
            from dashmachine.platform.weather_forecast import Platform

            mock_response = MagicMock()
            mock_response.json.return_value = SAMPLE_FORECAST_RESPONSE
            mock_response.raise_for_status = MagicMock()

            with patch("dashmachine.platform.weather_forecast.requests.get", return_value=mock_response):
                p = Platform(latitude="52.52", longitude="13.41", days="3")
                result = p.process()
                assert "15.2" in result  # max temp day 1
                assert "5.1" in result   # min temp day 1
                assert "18.1" in result  # max temp day 3

    def test_days_limits_columns(self, app):
        with app.app_context():
            from dashmachine.platform.weather_forecast import Platform

            mock_response = MagicMock()
            mock_response.json.return_value = SAMPLE_FORECAST_RESPONSE
            mock_response.raise_for_status = MagicMock()

            with patch("dashmachine.platform.weather_forecast.requests.get", return_value=mock_response):
                p = Platform(latitude="52.52", longitude="13.41", days="2")
                result = p.process()
                assert "18.1" not in result  # day 3 excluded

    def test_network_error(self, app):
        with app.app_context():
            from dashmachine.platform.weather_forecast import Platform

            with patch(
                "dashmachine.platform.weather_forecast.requests.get",
                side_effect=Exception("Timeout"),
            ):
                p = Platform(latitude="52.52", longitude="13.41")
                result = p.process()
                assert "theme-failure-text" in result

    def test_handles_css_class_icon(self, app):
        """Weather code 2 returns 'mw-cloudy' CSS class, not emoji."""
        with app.app_context():
            from dashmachine.platform.weather_forecast import Platform

            response_data = {
                "daily": {
                    "time": ["2026-03-14"],
                    "temperature_2m_max": [10.0],
                    "temperature_2m_min": [2.0],
                    "weather_code": [2],
                    "precipitation_probability_max": [5],
                }
            }
            mock_response = MagicMock()
            mock_response.json.return_value = response_data
            mock_response.raise_for_status = MagicMock()

            with patch("dashmachine.platform.weather_forecast.requests.get", return_value=mock_response):
                p = Platform(latitude="52.52", longitude="13.41", days="1")
                result = p.process()
                # Should render CSS class icon as <i> element, not raw text
                assert "10.0" in result
                assert "theme-failure-text" not in result
                assert "mw-cloudy" in result
                assert '<i class="mw' in result


class TestWeatherForecastDataSourceArg:
    def test_with_positional_data_source(self, app):
        with app.app_context():
            from dashmachine.platform.weather_forecast import Platform

            data_source = {"name": "forecast", "platform": "weather_forecast"}
            p = Platform(data_source, latitude="52.52", longitude="13.41")
            assert p.days == 5
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_weather_forecast.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'dashmachine.platform.weather_forecast'`

- [ ] **Step 3: Commit test file**

```bash
git add tests/test_weather_forecast.py
git commit -m "test: add weather forecast platform tests (red)"
```

---

### Task 7: Weather Forecast Platform — Implementation

**Files:**
- Create: `dashmachine/platform/weather_forecast.py`

**Context:** Import `get_weather_icon` and `get_weather_desc` from `dashmachine.platform.weather`. The `get_weather_icon()` function returns `"mw-cloudy"` for codes 1-2 (a CSS class name) and emoji strings for everything else. Use `str.isascii()` and `str.isalpha()` to detect CSS class names vs emoji in the template.

- [ ] **Step 1: Write the weather forecast platform**

```python
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
                forecast.append(
                    {
                        "name": dt.strftime("%a"),
                        "icon": icon,
                        "icon_is_class": icon_is_class,
                        "desc": get_weather_desc(daily["weather_code"][i]),
                        "max": daily["temperature_2m_max"][i],
                        "min": daily["temperature_2m_min"][i],
                        "precip_prob": daily.get("precipitation_probability_max", [None] * 7)[i],
                    }
                )

            return render_template_string(self.html_template, forecast=forecast)
        except Exception as e:
            return f"<div class='theme-failure-text'>Forecast Error: {e}</div>"
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/test_weather_forecast.py -v`
Expected: All tests PASS.

- [ ] **Step 3: Run all tests to verify nothing is broken**

Run: `pytest tests/ -v`
Expected: All tests PASS (smoke_test + rss + ical + weather_forecast).

- [ ] **Step 4: Commit**

```bash
git add dashmachine/platform/weather_forecast.py
git commit -m "feat: add weather forecast platform plugin"
```

---

### Task 8: Final Verification

- [ ] **Step 1: Run the full test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 2: Verify imports work in Flask app context**

Run: `python -c "from flask import Flask; app = Flask(__name__); ctx = app.app_context(); ctx.push(); from dashmachine.platform.rss import Platform as R; from dashmachine.platform.ical import Platform as I; from dashmachine.platform.weather_forecast import Platform as W; print('All platforms import OK')"`
Expected: `All platforms import OK`

- [ ] **Step 3: Verify the dev server starts**

Run: `timeout 5 python run.py || true`
Expected: Server starts without import errors (will timeout after 5s, that's fine).
