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
                assert result.count("collection-item") == 1

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
