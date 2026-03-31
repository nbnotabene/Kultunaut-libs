# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

Kultunaut-libs powers **Svaneke Bio**, a local Danish movie theater website. It fetches event data from the Kultunaut cultural events API, enriches it with TMDB movie metadata, persists everything in MariaDB, then generates a static HTML site deployed via StaticHost.eu. The full pipeline runs automatically via cron.

## Commands

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run a single test file
poetry run pytest tests/test_lib.py

# Generate the static site from DB
python3 UI_root.py

# Fetch events from Kultunaut API and upsert to DB
python3 fetchKult.py

# Test DB connection
python3 kultunaut/lib/DBtestConnection.py
```

## Architecture

**Data flow:**
```
Kultunaut API → jsoncache (filecache/YYYY/WW.json)
    → Events → kultevents table (MD5 upsert)
    → Arrangements + TMDB API → kultarrs table
    → UI.py + Jinja2 templates → webroot/ static HTML
    → git commit → StaticHost.eu webhook deploy
```

**Cron entry points** (via `fetchKult.sh` / `generateUI.sh` wrappers that git pull, run, then commit/push):
- `fetchKult.py` — data ingestion
- `UI_root.py` — static site generation

**Core library** (`kultunaut/lib/`):
- `event.py` / `events.py` — `Event` (single occurrence) and `Events` (MutableMapping over DB rows); MD5 hash-based upsert skips unchanged records
- `arrangement.py` / `arrangements.py` — `Arrangement` (movie + TMDB metadata) and container; same MutableMapping pattern
- `MariaDBInterface.py` — Singleton async MariaDB connector
- `JinjaRenderer.py` — Singleton Jinja2 renderer; skips file writes when content is unchanged
- `jsoncache.py` — Fetches and caches Kultunaut JSON responses by week
- `PosterImage.py` — Downloads posters, uses binary search over JPEG quality to hit ~100 KB target
- `lib.py` — Config loader and `Singleton` metaclass used by `MariaDBInterface` and `JinjaRenderer`

**DB tables:**
- `kultevents` — raw event occurrences; `kulthash` (MD5) detects changes
- `kultarrs` — arrangements with TMDB JSON blob
- `curEvents` / `curArrs` — SQL views filtered to future events

**Templates** (`kultunaut/templates/`): Jinja2 `extends` pattern; `baselayout.html` is the base. Output goes to `webroot/`, with one subfolder per arrangement at `webroot/arr/{AinfoNr}/`.

## Configuration

Two-tier config via `python-dotenv`:
- `.env` — public settings (URLs, paths, DB host/port/user, `WS` workspace selector, `SQLCONN` JSON)
- `.env.secret` — gitignored; holds `TMDBKEY`, `SECRET_KEY`, DB password

The `WS` variable selects which entry in `SQLCONN` to use (values: `digi`, `yogaws`, `dellxps`, `minipc`). Config is accessed at runtime via `lib.conf`.
