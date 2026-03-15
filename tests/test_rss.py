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
