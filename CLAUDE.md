# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DashMachine is a self-hosted web application bookmark dashboard built with Flask (Python 3). It uses INI-based configuration, SQLite via SQLAlchemy, and a plugin system for data source integrations (Sonarr, Radarr, Plex, Home Assistant, etc.).

## Commands

### Development
```bash
pip install -r requirements.txt
python3 run.py                    # Runs debug server on 0.0.0.0:5000
```

### Production
```bash
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

### Testing
```bash
pytest tests/smoke_test.py                   # App initialization smoke test
python tests/platform_verification.py        # Platform integration structural tests
```

### Docker
```bash
docker build -t dashmachine .
docker run -p 5000:5000 -v /path/to/data:/dashmachine/dashmachine/user_data dashmachine
```

## Architecture

### Entry Points
- `run.py` — development server (debug=True)
- `wsgi.py` — production WSGI entry point
- `dashmachine/__init__.py` — Flask app factory, registers extensions (SQLAlchemy, Bcrypt, Login, Cache, RESTful) and blueprints

### Blueprint Structure
- `dashmachine/main/` — Dashboard routes (`/`, `/home`, `/app_view`), data models (Apps, DataSources, Tags, Groups, Files), config reader, initialization
- `dashmachine/user_system/` — Authentication (login/logout), User model
- `dashmachine/settings_system/` — Settings UI and management, Settings model
- `dashmachine/error_pages/` — Error handlers
- `dashmachine/rest_api/` — RESTful API (currently only `/api/version`)

### Initialization Flow
`run.py`/`wsgi.py` → `dashmachine/__init__.py` → `dashmachine_init()` in `main/utils.py` → creates DB schema, sets up `user_data/` directories and symlinks, copies default config if missing, calls `read_config()` which parses `user_data/config.ini` into database models.

### Platform Plugin System
`dashmachine/platform/` contains ~20 integration modules (weather, sonarr, radarr, plex, home_assistant, docker, etc.). Each module exports a `Platform` class. Platforms are loaded dynamically via `importlib.import_module()` based on the `platform` key in config.ini data source entries. Each platform renders its output through Jinja2 templates.

### Configuration System
INI-file based (`user_data/config.ini`). Sections define settings, users, access groups, data sources, and apps. The config is parsed by `main/read_config.py` and populates SQLAlchemy models. Config changes require restart or clicking "save" in the settings UI.

### Frontend
- Materialize CSS framework with Material Design Icons
- jQuery/jQueryUI
- CSS minified via custom `dashmachine/cssmin.py`
- Context processor in `dashmachine/sources.py` provides apps, settings, tags, and JS/CSS bundles to all templates

### Key Directories
- `dashmachine/user_data/` — runtime data: config.ini, site.db (SQLite), custom icons/backgrounds, .secret key
- `dashmachine/templates/` — Jinja2 templates
- `dashmachine/static/` — CSS, JS, images, app icons
- `template_apps/` — 100+ pre-configured INI templates for common services
- `migrations/` — Alembic database migrations

### Access Control
Role-based (admin, user, public_user + custom roles) with group-based visibility. Apps and pages are assigned access groups; users have roles checked against groups. The first user in config must have role `admin`.

### Environment Variables
- `CONTEXT_PATH` — deploy under a URL subfolder (e.g., `/dash`)

## Default Credentials
- Username: `admin`, Password: `admin`
