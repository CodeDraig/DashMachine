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
