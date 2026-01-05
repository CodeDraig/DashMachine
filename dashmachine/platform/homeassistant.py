"""
##### Home Assistant
Display state of a specific Entity from Home Assistant
```ini
[variable_name]
platform = homeassistant
host = http://homeassistant.local:8123
token = long_lived_access_token
entity_id = sensor.temperature
value_template = {{ value_template }}
```
> **Returns:** `value_template` as rendered string

| Variable        | Required | Description                                                     | Options           |
|-----------------|----------|-----------------------------------------------------------------|-------------------|
| [variable_name] | Yes      | Name for the data source.                                       | [variable_name]   |
| platform        | Yes      | Name of the platform.                                           | homeassistant     |
| host            | Yes      | URL of HA Instance (include port)                               | url               |
| token           | Yes      | Long Lived Access Token (Create in Profile)                     | string            |
| entity_id       | Yes      | Entity ID to fetch state for                                    | string            |
| value_template  | Yes      | Jinja template for how the returned data from API is displayed. | jinja template    |

<br />

###### **Available fields for value_template**
* state (The main state string, e.g. "on", "25.5", "home")
* attributes (Dictionary of attributes)
* last_changed
* last_updated
* friendly_name (Shortcut for attributes.friendly_name)
* unit_of_measurement (Shortcut for attributes.unit_of_measurement)
* error

> **Example:**
>```ini
> [ha-temp]
> platform = homeassistant
> host = http://192.168.1.5:8123
> token = eyJhbGc...
> entity_id = sensor.living_room_temperature
> value_template = {{friendly_name}}: {{state}} {{unit_of_measurement}}
>```
"""

import requests
from flask import render_template_string

class HomeAssistant(object):
    def __init__(self, host, token, entity_id):
        self.host = host
        self.token = token
        self.entity_id = entity_id
        
        self.state = "?"
        self.attributes = {}
        self.last_changed = None
        self.last_updated = None
        self.friendly_name = ""
        self.unit_of_measurement = ""
        self.error = None

    def refresh(self):
        try:
            url = f"{self.host}/api/states/{self.entity_id}"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code == 404:
                self.error = "Entity not found"
                return
                
            resp.raise_for_status()
            data = resp.json()
            
            self.state = data.get("state", "?")
            self.attributes = data.get("attributes", {})
            self.last_changed = data.get("last_changed")
            self.last_updated = data.get("last_updated")
            
            self.friendly_name = self.attributes.get("friendly_name", self.entity_id)
            self.unit_of_measurement = self.attributes.get("unit_of_measurement", "")
            
            self.error = None
        except Exception as e:
            self.error = f"{e}"


class Platform:
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            self.__dict__[key] = value
        
        self.ha = HomeAssistant(self.host, self.token, self.entity_id)

    def process(self):
        if not hasattr(self, "token"): return "token missing"
        if not hasattr(self, "host"): return "host missing"
        if not hasattr(self, "entity_id"): return "entity_id missing"

        self.ha.refresh()
        value_template = render_template_string(
            self.value_template, **self.ha.__dict__
        )
        return value_template
