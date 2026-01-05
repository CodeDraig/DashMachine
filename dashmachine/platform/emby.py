"""
##### Emby
Connect to Emby Media Server and see current sessions details
```ini
[variable_name]
platform = emby
host = http://emby_host:emby_port
api_key = emby_api_key
value_template = {{ value_template }}
```
> **Returns:** `value_template` as rendered string

| Variable        | Required | Description                                                     | Options           |
|-----------------|----------|-----------------------------------------------------------------|-------------------|
| [variable_name] | Yes      | Name for the data source.                                       | [variable_name]   |
| platform        | Yes      | Name of the platform.                                           | emby              |
| host            | Yes      | URL of Emby Server (include port, normally 8096)                | url               |
| api_key         | Yes      | Emby API Key (create in Emby Dashboard > Advanced > Security)   | string            |
| value_template  | Yes      | Jinja template for how the returned data from API is displayed. | jinja template    |

<br />

###### **Available fields for value_template**
* server_name
* version
* active_sessions
* library_count
* collections
* error

> **Example:**
>```ini
>[emby-data]
>platform = emby
>host = http://192.168.1.5:8096
>api_key = 852f8x999...
>value_template = Server: {{server_name}} (v{{version}})<br />Sessions: {{active_sessions}}
>```
"""
import requests
from flask import render_template_string

json_header = {"Accept": "application/json"}

class Emby(object):
    def __init__(self, host, api_key, verify):
        self.host = host
        self.api_key = api_key
        self.verify = verify
        self.server_name = "?"
        self.version = "?"
        self.active_sessions = 0
        self.library_count = 0
        self.collections = []
        self.error = None

    def refresh(self):
        try:
            # Server Info
            info_url = f"{self.host}/System/Info?api_key={self.api_key}"
            info_resp = requests.get(info_url, headers=json_header, verify=self.verify, timeout=10)
            info_resp.raise_for_status()
            info_data = info_resp.json()
            
            self.server_name = info_data.get("ServerName", "?")
            self.version = info_data.get("Version", "?")

            # Sessions
            sessions_url = f"{self.host}/Sessions?api_key={self.api_key}"
            sessions_resp = requests.get(sessions_url, headers=json_header, verify=self.verify, timeout=10)
            sessions_resp.raise_for_status()
            sessions_data = sessions_resp.json()
            # Emby sessions returns list of session objects
            self.active_sessions = len(sessions_data)

            # Libraries (VirtualFolders)
            lib_url = f"{self.host}/Library/VirtualFolders?api_key={self.api_key}"
            lib_resp = requests.get(lib_url, headers=json_header, verify=self.verify, timeout=10)
            lib_resp.raise_for_status()
            lib_data = lib_resp.json()
            
            self.library_count = len(lib_data)
            self.collections = [lib.get("Name") for lib in lib_data]
            
            self.error = None

        except Exception as e:
             self.error = f"{e}"

class Platform:
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            self.__dict__[key] = value

        if not hasattr(self, "verify"):
            self.verify = True
        
        # backwards compatibility for 'token' vs 'api_key' if user confuses with plex
        if not hasattr(self, "api_key") and hasattr(self, "token"):
            self.api_key = self.token
            
        if not hasattr(self, "api_key"):
            self.api_key = None

        self.emby = Emby(self.host, self.api_key, self.verify)

    def process(self):
        if self.api_key is None:
            return "api_key missing"
            
        self.emby.refresh()
        value_template = render_template_string(
            self.value_template, **self.emby.__dict__
        )
        return value_template
