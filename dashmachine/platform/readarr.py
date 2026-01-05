"""
##### Readarr
Display information from Readarr API
```ini
[variable_name]
platform = readarr
prefix = http://
host = localhost
port = 8787
api_key = {{ Readarr API Key }}
verify = true
api_version = v1
value_template = {{ value_template }}
```
> **Returns:** `value_template` as rendered string

| Variable        | Required | Description                                                     | Options           |
|-----------------|----------|-----------------------------------------------------------------|-------------------|
| [variable_name] | Yes      | Name for the data source.                                       | [variable_name]   |
| platform        | Yes      | Name of the platform.                                           | readarr           |
| prefix          | No       | The prefix for the app's url.                                   | web prefix, e.g. http:// or https://              |
| host            | Yes      | Readarr Host                                                    | url,ip            |
| port            | No       | Readarr Port (Default 8787)                                     | port              |
| api_key         | Yes      | ApiKey                                                          | api key           |
| api_version     | No       | API Version (default v1)                                        | v1                |
| verify          | No       | Turn TLS verification on or off, default is true                | true,false        |
| value_template  | Yes      | Jinja template for how the returned data from API is displayed. | jinja template    |

<br />

###### **Available fields for value_template**
* version
* author_count
* book_count
* queue
* diskspace[x]['path']
* error (for debug)

> **Working example:**
>```ini
> [readarr-data]
> platform = readarr
> host = 192.168.0.110
> port = 8787
> api_key = {{ API Key }}
> value_template = Books: {{book_count}}<br />Authors: {{author_count}}
>```
"""

import requests
from flask import render_template_string

class Readarr(object):
    def __init__(self, method, prefix, host, port, api_key, api_version, verify):
        self.endpoint = "/api/" + api_version
        self.method = method
        self.prefix = prefix
        self.host = host
        self.port = port
        self.api_key = api_key
        self.verify = verify

        # Initialize results
        self.error = None
        self.version = "?"
        self.author_count = 0
        self.book_count = 0
        self.queue = 0
        self.diskspace = []

    def _get_request(self, path):
        verify = (
            False
            if str(self.verify).lower() == "false"
            or str(self.prefix).lower() == "http://"
            else True
        )
        headers = {"X-Api-Key": self.api_key}
        port = "" if self.port is None else ":" + self.port
        
        url = f"{self.prefix}{self.host}{port}{self.endpoint}{path}"
        
        try:
            resp = requests.get(url, headers=headers, verify=verify, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            self.error = f"{e}"
            return None

    def refresh(self):
        # System Status
        status = self._get_request("/system/status")
        if status:
            self.version = status.get("version", "?")
            
        # Authors (Artist equivalent)
        # Assuming v1 API structure similar to Lidarr/Sonarr
        # Readarr uses /author
        authors = self._get_request("/author")
        if authors and isinstance(authors, list):
            self.author_count = len(authors)
            
        # Books
        # Readarr uses /book
        # We might want total records if paged, but lets check default behavior
        # Assuming list return for simplicity or we should check totalRecords if object
        # It's safer to not fetch all books if library is huge. 
        # But for simple stats, we might not have a choice without a stats endpoint.
        # Actually *Arr usually has a /book?pageSize=1 to get totalRecords
        books = self._get_request("/book?pageSize=1") 
        if books:
            if isinstance(books, dict):
                self.book_count = books.get("totalRecords", 0)
            elif isinstance(books, list):
                self.book_count = len(books)

        # Queue
        queue = self._get_request("/queue")
        if queue:
             self.queue = queue.get("totalRecords", len(queue) if isinstance(queue, list) else 0)

        # Diskspace
        disk = self._get_request("/diskspace")
        if disk:
            self.diskspace = disk
            # Formatting logic similar to sonarr
            for item in self.diskspace:
                total = item.get("totalSpace", 0)
                free = item.get("freeSpace", 0)
                item["used"] = self.formatSize(total - free)
                item["total"] = self.formatSize(total)
                item["free"] = self.formatSize(free)
                item.pop("totalSpace", None)
                item.pop("freeSpace", None)
        
        if self.error is None:
             self.error = ""

    def formatSize(self, size):
        power = 2 ** 10
        n = 0
        power_labels = {0: "", 1: "KB", 2: "MB", 3: "GB", 4: "TB"}
        while size > power:
            size /= power
            n += 1
        return str(round(size, 1)) + " " + power_labels[n]


class Platform:
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            self.__dict__[key] = value

        if not hasattr(self, "method"): self.method = "GET"
        if not hasattr(self, "prefix"): self.prefix = "http://"
        if not hasattr(self, "host"): self.host = None
        if not hasattr(self, "port"): self.port = "8787"
        if not hasattr(self, "api_key"): self.api_key = None
        if not hasattr(self, "api_version"): self.api_version = "v1"
        if not hasattr(self, "verify"): self.verify = True

        self.readarr = Readarr(
            self.method, self.prefix, self.host, self.port, self.api_key, self.api_version, self.verify
        )

    def process(self):
        if self.api_key is None: return "api_key missing"
        if self.host is None: return "host missing"

        self.readarr.refresh()
        value_template = render_template_string(
            self.value_template, **self.readarr.__dict__
        )
        return value_template
