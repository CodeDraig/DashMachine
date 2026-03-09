# DashMachine
### Another web application bookmark dashboard, with fun features.
![Subreddit subscribers](https://img.shields.io/reddit/subreddit-subscribers/dashmachine?style=social)

![GitHub last commit](https://img.shields.io/github/last-commit/rmountjoy92/dashmachine)
![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/rmountjoy/dashmachine)

![Docker Pulls](https://img.shields.io/docker/pulls/rmountjoy/dashmachine)
![GitHub Repo stars](https://img.shields.io/github/stars/rmountjoy92/dashmachine?style=social)

![GitHub repo size](https://img.shields.io/github/repo-size/rmountjoy92/dashmachine)
![Docker Image Size (tag)](https://img.shields.io/docker/image-size/rmountjoy/dashmachine/latest?label=Docker%20Image%20Size)
![Lines of code](https://img.shields.io/tokei/lines/github/rmountjoy92/dashmachine)

[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![Awesome](https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/sindresorhus/awesome)

[![Donate](https://img.shields.io/badge/$-support-ff69b4.svg?style=flat)](https://liberapay.com/rmountjoy) 
![Bountysource](https://img.shields.io/bountysource/team/dashmachine/activity)

Want a feature added now? [Open a bounty](https://www.bountysource.com/teams/dashmachine-app)

## Screenshots

![screenshot](https://raw.githubusercontent.com/rmountjoy92/DashMachine/master/screenshot1.png)

![screenshot](https://raw.githubusercontent.com/rmountjoy92/DashMachine/master/screenshot2.png)

![screenshot](https://raw.githubusercontent.com/rmountjoy92/DashMachine/master/screenshot3.png)

![screenshot](https://raw.githubusercontent.com/rmountjoy92/DashMachine/master/screenshot4.png)


## Installation
### Docker
```
docker create \
  --name=dashmachine \
  -p 5000:5000 \
  -v path/to/data:/dashmachine/dashmachine/user_data \
  --restart unless-stopped \
  rmountjoy/dashmachine:latest
```
To run in a subfolder, use a CONTEXT_PATH environment variable. For example, to run at localhost:5000/dash:
```
docker create \
  --name=dashmachine \
  -p 5000:5000 \
  -e CONTEXT_PATH=/dash
  -v path/to/data:/dashmachine/dashmachine/user_data \
  --restart unless-stopped \
  rmountjoy/dashmachine:latest
```
### Synology
Check out this awesome guide: https://nashosted.com/manage-your-self-hosted-applications-using-dashmachine/
### Python
Instructions are for linux.
```
virtualenv --python=python3 DashMachineEnv
cd DashMachineEnv && source bin/activate
git clone https://github.com/rmountjoy92/DashMachine.git
cd DashMachine && pip install -r requirements.txt
python3 run.py
```
Then open a web browser and go to localhost:5000

## Default user/password
```
User: admin
Password: admin
```

## Updating
For python, use git. For docker, just pull the latest image and recreate the container.

## Configuration
The user data folder is located at DashMachine/dashmachine/user_data. This is where the config.ini, custom backgrounds/icons, and the database file live. A reference for what can go into the config.ini file can be found on the settings page of the dashmachine by clicking the info icon next to 'Config'. 


#### Main Settings

##### Settings
This is the configuration entry for DashMachine's settings. DashMachine will not work if this is missing. As for all config entries, [Settings] can only appear once in the config. If you change the config.ini file, you either have to restart the container (or python script) or click the ‘save’ button in the config section of settings for the config to be applied.
```ini
[Settings]
theme = light
accent = orange
background = None
roles = admin,user,public_user
home_access_groups = admin_only
settings_access_groups = admin_only
custom_app_title = DashMachine
sidebar_default = open
tags_expanded = True
```

| Variable               | Required | Description                                              | Options                                                                                                                                                                        |
|------------------------|----------|----------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Settings]             | Yes      | Config section name.                                                          | [Settings]                                                                                                                                                                     |
| theme                  | Yes      | UI theme.                                                                     | light, dark                                                                                                                                                                    |
| accent                 | Yes      | UI accent color                                                               | orange, red, pink, purple, deepPurple, indigo, blue, lightBlue,cyan, teal, green, lightGreen, lime, yellow, amber, deepOrange, brown, grey, blueGrey                           |
| background             | Yes      | Background image for the UI                                                   | /static/images/backgrounds/yourpicture.png, external link to image, None, random                                                                                               |
| roles                  | No       | User roles for access groups.                                                 | comma separated string, if not defined, this is set to 'admin,user,public_user'. Note: admin, user, public_user roles are required and will be added automatically if omitted. |
| home_access_groups     | No       | Define which access groups can access the /home page                          | Groups defined in your config. If not defined, default is admin_only                                                                                                           |
| settings_access_groups | No       | Define which access groups can access the /settings page                      | Groups defined in your config. If not defined, default is admin_only                                                                                                           |
| custom_app_title       | No       | Change the title of the app for browser tabs                                  | string                                                                                                                                                                         |
| sidebar_default        | No       | Select the default state for the sidebar                                      | open, closed, no_sidebar                                                                                                                                                       |
| tags                   | No       | Set custom options for your tags. Json options are "name", "icon", "sort_pos" | comma separated json dicts. For "icon" use material design icons: https://material.io/resources/icons                                                                          |
| tags_expanded          | No       | Set to False to have your tags collapsed by default                           | True, False                                                                                                                                                   |

##### Users
Each user requires a config entry, and there must be at least one user in the config (otherwise the default user is added). Each user has a username, a role for configuring access groups, and a password. By default there is one user, named 'admin', with role 'admin' and password 'admin'. To change this user's name, password or role, just modify the config entry's variables and press save. To add a new user, add another user config entry UNDER all existing user config entries. A user with role 'admin' must appear first in the config. Do not change the order of users in the config once they have been defined, otherwise their passwords will not match the next time the config is applied. When users are removed from the config, they are deleted and their cached password is also deleted when the config is applied.
```ini
[admin]
role = admin
password = admin
confirm_password = admin
```

| Variable         | Required | Description                                                                                                                                                                                                                            | Options          |
|------------------|----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------|
| [Username]       | Yes      | The user's name for logging in                                                                                                                                                                                                         | [Username]       |
| role             | Yes      | The user's role. This is used for access groups and controlling who can view /home and /settings. There must be at least one 'admin' user, and it must be defined first in the config. Otherwise, the first user will be set to admin. | string           |
| password         | No       | Add a password to this variable to change the password for this user. The password will be hashed, cached and removed from the config. When adding a new user, specify the password, otherwise 'admin' will be used.                   | string           |
| confirm_password | No       | When adding a new user or changing an existing user's password you must confirm the password in this variable                                                                                                                          | string           |
| theme            | No       | Override the theme from Settings for this user                                                                                                                                                                                         | same as Settings |
| accent           | No       | Override the accent from Settings for this user                                                                                                                                                                                        | same as Settings |
| sidebar_default  | No       | Override the sidebar_default from Settings for this user                                                                                                                                                                               | same as Settings |

##### Access Groups
You can create access groups to control what user roles can access parts of the ui. Access groups are just a collection of roles, and each user has an attribute 'role'. Each application can have an access group, if the user's role is not in the group, the app will be hidden. Also, in the settings entry you can specify `home_access_groups` and `settings_access_groups` to control which groups can access /home and /settings
```ini
[admin_only]
roles = admin
```

| Variable     | Required | Description                                                                    | Options                                                                          |
|--------------|----------|--------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| [Group Name] | Yes      | Name for access group.                                                         | [Group Name]                                                                     |
| roles        | Yes      | A comma separated list of user roles allowed to view apps in this access group | Roles defined in your config. If not defined, defaults are admin and public_user |

> Say we wanted to create a limited user that still has a login, but can only access `/home` and certain apps we would first create a group:
>```ini
>[users]
>roles = admin, user
>```
>then we would change in the `[Settings]` entry:
>```ini
>home_access_groups = users
>```
>By default here, the `user` user could access `/home`, but would see no apps. To allow access, we would add to apps:
>```ini
>groups = users
>```
>Say we then wanted to allow some access for users without a login (`public_user`), we would add:
>```ini
>[public]
>roles = admin, user, public_user
>```
>then we would change in the `[Settings]` entry:
>```ini
>home_access_groups = public
>```
>By default here, the `public_user` user could access `/home`, but would see no apps. To allow access, we would add to apps:
>```ini
>groups = public
>```


>It’s also important to note, when setting up roles in `[Settings]`, say we had roles set like this:
>```ini
>roles = my_people
>```
>Dashmachine will automatically add `admin,user,public_user`, so really you would have 4 roles: `my_people,admin,user,public_user`. Also, the `admin_only` group is required and added by default if omitted.



##### Apps
These entries are the standard card type for displaying apps on your dashboard and sidenav.
```ini
[App Name]
prefix = https://
url = your-website.com
icon = static/images/apps/default.png
sidebar_icon = static/images/apps/default.png
description = Example description
open_in = iframe
data_sources = None
tags = Example Tag
groups = admin_only
```

| Variable     | Required | Description                                                                                                                         | Options                                                      |
|--------------|----------|-------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------|
| [App Name]   | Yes      | The name of your app.                                                                                                               | [App Name]                                                   |
| prefix       | Yes      | The prefix for the app's url.                                                                                                       | web prefix, e.g. http:// or https://                         |
| url          | Yes      | The url for your app.                                                                                                               | web url, e.g. myapp.com                                      |
| open_in      | Yes      | open the app in the current tab, an iframe or a new tab                                                                             | iframe, new_tab, this_tab                                    |
| icon         | Yes      | Icon for the dashboard.                                                                                                             | /static/images/icons/yourpicture.png, external link to image |
| sidebar_icon | No       | Icon for the sidenav.                                                                                                               | /static/images/icons/yourpicture.png, external link to image |
| description  | No       | A short description for the app.                                                                                                    | HTML                                                       |
| data_sources | No       | Data sources to be included on the app's card.*Note: you must have a data source set up in the config above this application entry. | comma separated string                                       |
| tags         | No       | Optionally specify tags for organization on /home                                                                                   | comma separated string                                       |
| groups       | No       | Optionally specify the access groups that can see this app.                                                                         | comma separated string                                       |

##### Collection
These entries provide a card on the dashboard containing a list of links.
```ini
[Collection Name]
type = collection
icon = collections_bookmark
urls = {"url": "https://google.com", "icon": "static/images/apps/default.png", "name": "Google", "open_in": "new_tab"},{"url": "https://duckduckgo.com", "icon": "static/images/apps/default.png", "name": "DuckDuckGo", "open_in": "this_tab"}
```

| Variable          | Required | Description                                                                                  | Options                             |
|-------------------|----------|----------------------------------------------------------------------------------------------|-------------------------------------|
| [Collection Name] | Yes      | Name for the collection                                                                      | [Collection Name]                   |
| type              | Yes      | This tells DashMachine what type of card this is.                                            | collection                          |
| icon              | No       | The material design icon class for the collection.                                           | https://material.io/resources/icons |
| urls              | Yes      | The urls to include in your collection. Json options are "url", "icon", "name" and "open_in" | comma separated json dicts, "open_in" only has options "this_tab", "new_tab"          |
| tags              | No       | Optionally specify tags for organization on /home                                            | comma separated string              |
| groups            | No       | Optionally specify the access groups that can see this app.                                  | comma separated string              |

##### Custom Card
These entries provide an empty card on the dashboard to be populated by a data source. This allows the data source to populate the entire card.
```ini
[Collection Name]
type = custom
data_sources = my_data_source
```

| Variable          | Required | Description                                                                                  | Options                             |
|-------------------|----------|----------------------------------------------------------------------------------------------|-------------------------------------|
| [Collection Name] | Yes      | Name for the collection                                                                      | [Collection Name]                   |
| type              | Yes      | This tells DashMachine what type of card this is.                                            | custom                              |
| data_sources      | Yes      | What data sources to display on the card.                                                    | comma separated string              |
| tags              | No       | Optionally specify tags for organization on /home                                            | comma separated string              |
| groups            | No       | Optionally specify the access groups that can see this app.                                  | comma separated string              |


> **Working example:**
>```ini
>[test]
>platform = curl
>resource = https://api.myip.com
>value_template = <div class="row center-align"><div class="col s12"><h5><i class="material-icons-outlined" style="position:relative; top: 4px;">dns</i> My IP Address</h5><span class="theme-primary-text">{{value.ip}}</span></div></div>
>response_type = json
>
>[MyIp.com]
>type = custom
>data_sources = test
>```

#### Data Source Platforms
DashMachine includes several different 'platforms' for displaying data on your dash applications. Platforms are essentially plugins. All data source config entries require the `platform` variable, which tells DashMachine which platform file in the platform folder to load. **Note:** you are able to load your own platform files by placing them in the platform folder and referencing them in the config. However currently they will be deleted if you update the application, if you would like to make them permanent, submit a pull request for it to be added by default!

> To add a data source to your app, add a data source config entry from one of the samples below
**above** the application entry in config.ini, then add the following to your app config entry:
`data_source = variable_name`

### Note
If you change the config.ini file, you either have to restart the container (or python script) or click the 'save' button in the config section of settings for the config to be applied. Pictures added to the backgrounds/icons folders are available immediately.

## Want to contribute?
Please use the pull request template at:
https://github.com/rmountjoy92/DashMachine/blob/master/pull_request_template.md

See this link for how to create a pull request:
https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request

## Tech used
* Flask (Python 3)
* SQLalchemy w/ SQLite database
* HTML5/Jinja2
* Materialize css
* JavaScript/jQuery/jQueryUI
* .ini (for configuration)

## FAQs
1. application does not work in iframe
see https://github.com/rmountjoy92/DashMachine/issues/6
