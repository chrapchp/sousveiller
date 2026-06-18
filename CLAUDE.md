# Sousveiller — Claude Code Context

> Bluetooth device surveying tool with simulated GPS, FastAPI backend,
> and Nuxt 3 map frontend.

---

## Project Structure

```
sousveiller/
├── firmware/      # ESP32 / PlatformIO / C++
├── backend/       # FastAPI / SQLite / Python
├── frontend/      # Nuxt 3 / Tailwind / Leaflet
├── data/          # host-mapped SQLite volume (gitignored)
├── docker-compose.yml
└── docker-compose.dev.yml
```

Full requirements in `REQUIREMENTS.md`.

---

## Firmware (firmware/)

- **Platform:** ESP32 / Arduino framework via PlatformIO
- **IDE:** VS Code + PlatformIO extension
- **Language:** C++17
- All tunable parameters have compile-time defaults in `src/config.h`
- Runtime values override defaults via **WiFiManager + Preferences library**
- WiFiManager portal SSID: `Sousveiller-Setup` — launches on first boot or
  when CONFIG_BUTTON_PIN held 3 seconds
- Config split into modules: `bt_scanner`, `gps_sim`, `wifi_client`, `config_manager`
- Serial output for all scan and connection events (baud 115200)
- Use `ArduinoJson` for JSON serialization
- Use `WiFiClientSecure` / `HTTPClient` for REST calls
- `config.h` contains only DEFAULT_* constants — no secrets, safe to commit

### Build & Flash
```bash
cd firmware
pio run                    # build
pio run --target upload    # flash
pio device monitor         # serial monitor
```

---

## Backend (backend/)

- **Framework:** FastAPI
- **Database:** SQLite via SQLAlchemy (sync, simple for POC)
- **DB file:** `/app/data/sousveiller.db` (mapped to `./data/` on host)
- **Python version:** 3.11+
- Use Pydantic v2 schemas for all request/response models
- Routers split by domain: `scans`, `sightings`, `devices`
- Auto-docs available at `http://localhost:8000/docs`

### Code Style
- Type hints on all functions
- Async route handlers where possible
- Return explicit Pydantic response models, not raw dicts
- Use `httpx` for any outbound HTTP (not `requests`)

### Run locally (outside Docker)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Run via Docker
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up backend
```

---

## Frontend (frontend/)

- **Framework:** Nuxt 3 (Vue 3)
- **Styling:** Tailwind CSS v4
- **Map:** Leaflet via `@vue-leaflet/vue-leaflet`
- **State:** Pinia
- **API calls:** Nuxt `$fetch` / `useFetch` with base URL from runtime config
- **Theme:** Dark (surveillance/night aesthetic)

### Config
```ts
// nuxt.config.ts
runtimeConfig: {
  public: {
    apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api'
  }
}
```

### Code Style
- Composition API with `<script setup>` — no Options API
- TypeScript throughout
- One component per file, PascalCase filenames
- Tailwind utility classes only — no custom CSS unless unavoidable
- Responsive: sidebar nav ≥ lg, bottom tab nav < lg

### Run locally (outside Docker)
```bash
cd frontend
npm install
npm run dev
```

---

## Docker

```bash
# Development (hot reload)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production build
docker compose up --build

# Tear down
docker compose down

# View logs
docker compose logs -f backend
docker compose logs -f frontend
```

Data persists in `./data/sousveiller.db` on the host OS.

---

## API Reference (summary)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/scans` | ESP32 pushes scan batch |
| GET | `/api/sightings` | All sightings (paginated) |
| GET | `/api/sightings/:mac` | History for one device |
| GET | `/api/devices` | Unique devices + stats |
| GET | `/api/stats` | Dashboard summary |
| POST | `/api/location` | Inject mock GPS override |

Full schemas in `REQUIREMENTS.md` section 5.

---

## Git Policy

- **Never** run `git commit`, `git push`, `git branch`, or any write command
- Read-only git operations are fine: `git status`, `git diff`, `git log`
- Suggest commit messages as comments only — the developer commits manually
- One logical change per suggested commit message
- Never create or switch branches

---

## Key Conventions

- Never commit `data/` directory contents (SQLite file)
- `config.h` is safe to commit — contains only DEFAULT_* constants, no secrets
- WiFiManager handles all WiFi credentials at runtime — never hardcode SSID/password
- All scan parameters tunable via WiFiManager portal + Preferences — no magic numbers in logic
- Keep CLAUDE.md under 200 lines

---

## Out of Scope (POC)

Do not implement unless explicitly asked:
- BLE fingerprinting / re-identification
- Authentication or API keys
- Real GPS hardware
- Heatmaps or analytics
- Production TLS / deployment
- Multi-unit ESP32 support

### File Header Requirements

All source files must include a standard header comment at the very top, before any imports or code.

### Standard Format

**C/C++ (`.h`, `.cpp`)**
```cpp
/***************************************************
 * Project:     <project name>
 * Author:      <author name>
 * Date:        <yyyyMMMdd>
 * History:     <yyyyMMMdd> - Initial creation
 ***************************************************/
```

**TypeScript / JavaScript (`.ts`, `.tsx`, `.js`)**
```ts
/***************************************************
 * Project:     <project name>
 * Author:      <author name>
 * Date:        <yyyyMMMdd>
 * History:     <yyyyMMMdd> - Initial creation
 ***************************************************/
```

**Python (`.py`)**
```python
###################################################
# Project:     <project name>
# Author:      <author name>
# Date:        <yyyyMMMdd>
# History:     <yyyyMMMdd> - Initial creation
###################################################
```

**Vue (`.vue`)** — place before the first `<template>` tag
```vue
<!--*************************************************
 * Project:     <project name>
 * Author:      <author name>
 * Date:        <yyyyMMMdd>
 * History:     <yyyyMMMdd> - Initial creation
 *************************************************-->
```

**CSS (`.css`)** — global stylesheets only, not scoped component styles
```css
/***************************************************
 * Project:     <project name>
 * Author:      <author name>
 * Date:        <yyyyMMMdd>
 * History:     <yyyyMMMdd> - Initial creation
 ***************************************************/
```

### Rules
- Every new file must include the header at the top.
- Date format is `yyyyMMMdd` with month as 3-letter abbreviation, e.g. `2026Jun17`.
- `Date` is the original creation date and never changes.
- `History` first entry matches `Date` with the description `Initial creation`.
- When modifying an existing file, append a new `History` line with the current date and a brief description of the change.
- Do not remove or reorder existing `History` entries.
- Infer `Project` from the repository or workspace name if available, otherwise leave as a placeholder.
- Infer `Author` from the git config (`user.name`) if available, otherwise leave as a placeholder.
- Do not add headers to scoped `<style>` blocks inside `.vue` files.

### Enforcement
- Before writing any file changes, always update the header first.
- **New file** — generate the full header using the standard format before writing any code.
- **Modified file** — check if a compliant header exists at the top of the file:
  - If missing, add the full header before proceeding.
  - If present, append a new `History` line with the current date and a brief description of the change made.
- **Never** modify the `Project`, `Author`, or `Date` fields on existing files.
- **Never** remove or reorder existing `History` entries.