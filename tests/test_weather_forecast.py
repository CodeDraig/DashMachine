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
