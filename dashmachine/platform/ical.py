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
