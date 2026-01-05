"""
##### SABnzbd
Display queue and history from SABnzbd
```ini
[variable_name]
platform = sabnzbd
host = http://localhost:8080
api_key = {{ SABnzbd API Key }}
value_template = {{ value_template }}
```
> **Returns:** `value_template` as rendered string

| Variable        | Required | Description                                                     | Options           |
|-----------------|----------|-----------------------------------------------------------------|-------------------|
| [variable_name] | Yes      | Name for the data source.                                       | [variable_name]   |
| platform        | Yes      | Name of the platform.                                           | sabnzbd           |
| host            | Yes      | URL of SABnzbd (include port)                                   | url               |
| api_key         | Yes      | ApiKey                                                          | string            |
| value_template  | Yes      | Jinja template for how the returned data from API is displayed. | jinja template    |

<br />

###### **Available fields for value_template**
* status
* paused (bool)
* speed (string with units)
* timeleft
* sizeleft
* sizeTotal
* nof_slots (queue count)
* error(for debug)

> **Example:**
>```ini
> [sabnzbd-data]
> platform = sabnzbd
> host = http://192.168.1.5:8080
> api_key = abc...
> value_template = Status: {{status}}<br />Speed: {{speed}} ({{timeleft}} left)
>```
"""

import requests
from flask import render_template_string

class Sabnzbd(object):
    def __init__(self, host, api_key):
        self.host = host
        self.api_key = api_key
        
        self.status = "Unknown"
        self.paused = False
        self.speed = "0 B/s"
        self.timeleft = "0:00:00"
        self.sizeleft = "0 GB"
        self.sizeTotal = "0 GB"
        self.nof_slots = 0
        self.error = None

    def refresh(self):
        try:
            # Mode queue matches fullqueue output mostly but simpler 'queue' is enough for summary
            url = f"{self.host}/api?mode=queue&output=json&apikey={self.api_key}"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            queue = data.get("queue", {})
            self.status = queue.get("status", "Unknown")
            self.paused = queue.get("paused", False)
            self.speed = queue.get("speed", "0") + " B/s" # usually just number for old versions? usually string in newer?
            # actually speed is usually format like "1.2 MB/s" in newer or just "1.2 M"
            # let's trust API provides reasonable string or simple float. 
             # data['queue']['speed'] is usually string like "1.2 M"
            self.speed = queue.get("speed", "0")
            
            self.timeleft = queue.get("timeleft", "0:00:00")
            self.sizeleft = queue.get("sizeleft", "0")
            self.sizeTotal = queue.get("sizeTotal", "0")
            self.nof_slots = queue.get("nof_slots", 0)
            
            self.error = None
        except Exception as e:
            self.error = f"{e}"


class Platform:
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            self.__dict__[key] = value
        
        if not hasattr(self, "api_key"): self.api_key = None
        
        self.sabnzbd = Sabnzbd(self.host, self.api_key)

    def process(self):
        if self.api_key is None: return "api_key missing"
        if not hasattr(self, "host"): return "host missing"

        self.sabnzbd.refresh()
        value_template = render_template_string(
            self.value_template, **self.sabnzbd.__dict__
        )
        return value_template
