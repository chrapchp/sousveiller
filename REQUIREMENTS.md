# Sousveiller — Project Requirements (POC)

> *Sousveiller*: inverse surveillance — mapping the Bluetooth devices around you.

---

## 1. Project Overview

A self-contained Bluetooth surveying tool consisting of:
- An **ESP32 device** that scans for nearby Bluetooth devices and reports
  scan batches with simulated GPS coordinates to a backend server
- A **FastAPI backend** that ingests scan batches, stores sightings, and
  exposes a REST API
- A **Nuxt 3 frontend** that displays device sightings on an interactive map

The POC uses simulated GPS movement on the ESP32 to avoid hardware
dependency. All parameters are tunable via a config system.

---

## 2. Architecture

```
ESP32 (C++ / PlatformIO)
  ├── Bluetooth scanner (BLE + Classic)
  ├── Simulated GPS (walking path)
  ├── Tunable config (scan_interval, rssi threshold, etc.)
  └── WiFi REST client → POST /api/scans

FastAPI Backend (Python)
  ├── POST /api/scans       ← receives ESP32 batches
  ├── GET  /api/sightings   ← all sightings
  ├── GET  /api/sightings/:mac
  ├── GET  /api/devices     ← unique devices
  ├── POST /api/location    ← inject mock GPS override
  └── SQLite via SQLAlchemy

Nuxt 3 Frontend
  ├── Tailwind CSS
  ├── Leaflet map
  └── Pinia state management

Infrastructure
  └── Docker Compose
        ├── backend  (port 8000)
        └── frontend (port 3000)
        └── ./data/  mapped to host OS (SQLite file)
```

---

## 3. Folder Structure

```
sousveiller/
├── firmware/                  # PlatformIO project
│   ├── platformio.ini
│   ├── src/
│   │   ├── main.cpp
│   │   ├── bt_scanner.cpp / .h
│   │   ├── gps_sim.cpp / .h
│   │   ├── wifi_client.cpp / .h
│   │   ├── config_manager.cpp / .h  # WiFiManager + Preferences
│   │   └── config.h                 # compile-time defaults only
│   └── include/
├── backend/                   # FastAPI project
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   └── routers/
│   │       ├── scans.py
│   │       ├── sightings.py
│   │       └── devices.py
│   └── data/                  # gitignored, mapped to host
├── frontend/                  # Nuxt 3 project
│   ├── Dockerfile
│   ├── nuxt.config.ts
│   ├── tailwind.config.ts
│   ├── pages/
│   │   ├── index.vue          # dashboard
│   │   ├── map.vue            # Leaflet map
│   │   ├── devices/
│   │   │   ├── index.vue      # device table
│   │   │   └── [mac].vue      # device history
│   ├── components/
│   │   ├── AppNav.vue
│   │   ├── StatCard.vue
│   │   ├── DeviceTable.vue
│   │   └── MapView.vue
│   └── stores/
│       ├── devices.ts
│       └── sightings.ts
├── data/                      # host-mapped SQLite volume
├── docker-compose.yml
├── docker-compose.dev.yml
├── CLAUDE.md
└── README.md
```

---

## 4. Firmware Spec (ESP32)

### 4.1 Config System

Two-layer config: **compile-time defaults** in `config.h`, overridden at
runtime by values stored in ESP32 flash via the **Preferences library**.
Values are set through the **WiFiManager captive portal** on first boot
or on demand (hold config button 3 seconds to re-trigger portal).

#### `config.h` — compile-time defaults only

```cpp
// Network defaults (overridden by WiFiManager/Preferences at runtime)
#define DEFAULT_SERVER_URL        "http://192.168.1.100:8000"
#define DEFAULT_DEVICE_ID         "esp32-unit-01"

// Scanning defaults
#define DEFAULT_SCAN_INTERVAL_MS  30000   // ms between scan batches
#define DEFAULT_SCAN_DURATION_MS   5000   // ms to scan per batch
#define DEFAULT_MIN_RSSI            -90   // ignore weaker signals
#define DEFAULT_MAX_BATCH_SIZE       50   // max devices per POST

// Simulated GPS defaults
#define DEFAULT_SIM_START_LAT     37.7749
#define DEFAULT_SIM_START_LNG   -122.4194
#define DEFAULT_SIM_STEP_LAT     0.00005  // ~5m per step
#define DEFAULT_SIM_STEP_LNG     0.00003  // ~3m per step
#define DEFAULT_SIM_STEPS_TURN       20   // steps before direction change

// Hardware
#define CONFIG_BUTTON_PIN             0   // GPIO0 = BOOT button
#define CONFIG_PORTAL_TIMEOUT_S     180   // portal auto-closes after 3 min
```

#### WiFiManager Portal

- On boot, if no WiFi credentials saved → launch portal automatically
- Hold `CONFIG_BUTTON_PIN` for 3 seconds → re-launch portal on demand
- Portal SSID: `Sousveiller-Setup`, no password
- Custom fields exposed in portal UI:

| Field | Key | Default |
|-------|-----|---------|
| Server URL | `server_url` | `DEFAULT_SERVER_URL` |
| Device ID | `device_id` | `DEFAULT_DEVICE_ID` |
| Scan interval (ms) | `scan_interval` | `30000` |
| Scan duration (ms) | `scan_duration` | `5000` |
| Min RSSI | `min_rssi` | `-90` |
| Sim step size (lat) | `sim_step_lat` | `0.00005` |
| Sim step size (lng) | `sim_step_lng` | `0.00003` |

#### Preferences Storage

All values saved to ESP32 flash under namespace `sousveiller`:

```cpp
Preferences prefs;
prefs.begin("sousveiller", false);

// Save after portal submit
prefs.putString("server_url",    server_url);
prefs.putString("device_id",     device_id);
prefs.putInt("scan_interval",    scan_interval_ms);
prefs.putInt("scan_duration",    scan_duration_ms);
prefs.putInt("min_rssi",         min_rssi);
prefs.putFloat("sim_step_lat",   sim_step_lat);
prefs.putFloat("sim_step_lng",   sim_step_lng);

// Read on boot (fall back to DEFAULT_* if not set)
scan_interval_ms = prefs.getInt("scan_interval", DEFAULT_SCAN_INTERVAL_MS);
```

#### Config module files
- `src/config.h` — compile-time defaults (committed, no secrets)
- `src/config_manager.cpp / .h` — WiFiManager setup, Preferences read/write
- No `config.h` with real credentials — WiFiManager handles all of that

### 4.2 Bluetooth Scanner

- Use ESP32 BLE Arduino library
- Scan for BLE advertising packets
- Capture per device:
  - MAC address (string)
  - RSSI (int, dBm)
  - Device name (string, if available)
  - Manufacturer data (hex string)
  - Service UUIDs (array of strings)
  - TX power (int, if available)
  - Advertising interval estimate (ms)
- Filter devices below `MIN_RSSI`
- Deduplicate MACs within a single scan window

### 4.3 GPS Simulator

- Starts at `SIM_START_LAT / SIM_START_LNG`
- Each scan batch increments position by `SIM_STEP_LAT / SIM_STEP_LNG`
- After `SIM_STEPS_BEFORE_TURN` steps, rotate direction 90 degrees
- Simulates a square walking path indefinitely
- Optionally overridden by POST to `/api/location` on the backend
  (ESP32 polls this endpoint on startup and after each batch)

### 4.4 WiFi REST Client

- WiFiManager handles initial connection and credential storage
- On boot: auto-connect using saved credentials
- If connection fails after 3 retries → re-launch config portal
- After each scan, POST batch to `server_url/api/scans` (from Preferences)
- Retry up to 3 times on failure with 2s backoff
- Log all connection events to Serial

### 4.5 Scan Batch Payload

```json
{
  "device_id": "esp32-unit-01",
  "scanned_at": "2026-06-07T10:30:00Z",
  "location": {
    "lat": 37.7749,
    "lng": -122.4194,
    "simulated": true
  },
  "devices": [
    {
      "mac": "AA:BB:CC:DD:EE:FF",
      "rssi": -65,
      "name": "MyDevice",
      "manufacturer_data": "4c0012",
      "service_uuids": ["fe9f", "fd6f"],
      "tx_power": -59,
      "adv_interval_ms": 200
    }
  ]
}
```

---

## 5. API Contract

### Base URL
`http://localhost:8000/api`

### Endpoints

#### POST `/scans`
Receive a scan batch from ESP32.

**Request body:** scan batch payload (see 4.5)

**Response:**
```json
{ "accepted": 12, "duplicate": 3, "rejected": 1 }
```

---

#### GET `/sightings`
All device sightings, paginated.

**Query params:**
- `limit` (default 100)
- `offset` (default 0)
- `mac` (optional filter)
- `since` (optional ISO timestamp)

**Response:**
```json
[
  {
    "id": 1,
    "mac": "AA:BB:CC:DD:EE:FF",
    "rssi": -65,
    "name": "MyDevice",
    "manufacturer_data": "4c0012",
    "service_uuids": ["fe9f"],
    "tx_power": -59,
    "lat": 37.7749,
    "lng": -122.4194,
    "simulated": true,
    "device_id": "esp32-unit-01",
    "seen_at": "2026-06-07T10:30:00Z"
  }
]
```

---

#### GET `/sightings/:mac`
Full sighting history for one device MAC.

**Response:** array of sighting objects (same schema as above)

---

#### GET `/devices`
All unique devices ever seen, with summary stats.

**Response:**
```json
[
  {
    "mac": "AA:BB:CC:DD:EE:FF",
    "name": "MyDevice",
    "manufacturer_data": "4c0012",
    "first_seen": "2026-06-07T09:00:00Z",
    "last_seen": "2026-06-07T10:30:00Z",
    "sighting_count": 14,
    "avg_rssi": -67.3,
    "last_lat": 37.7749,
    "last_lng": -122.4194
  }
]
```

---

#### POST `/location`
Inject a mock GPS location override (ESP32 polls this).

**Request body:**
```json
{ "lat": 37.7749, "lng": -122.4194 }
```

**Response:**
```json
{ "status": "ok" }
```

---

#### GET `/stats`
Dashboard summary stats.

**Response:**
```json
{
  "total_devices": 142,
  "total_sightings": 3841,
  "active_scanners": 1,
  "last_scan": "2026-06-07T10:30:00Z"
}
```

---

## 6. Data Model

### Table: `sightings`

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | auto increment |
| mac | TEXT | device MAC address |
| rssi | INTEGER | signal strength dBm |
| name | TEXT | nullable |
| manufacturer_data | TEXT | hex string, nullable |
| service_uuids | TEXT | JSON array as string |
| tx_power | INTEGER | nullable |
| adv_interval_ms | INTEGER | nullable |
| lat | REAL | |
| lng | REAL | |
| simulated | BOOLEAN | GPS was simulated |
| device_id | TEXT | which ESP32 unit |
| seen_at | DATETIME | scan timestamp |

### Table: `devices` (materialized summary)

| Column | Type | Notes |
|--------|------|-------|
| mac | TEXT PK | |
| name | TEXT | latest known name |
| manufacturer_data | TEXT | latest |
| first_seen | DATETIME | |
| last_seen | DATETIME | |
| sighting_count | INTEGER | |
| avg_rssi | REAL | |
| last_lat | REAL | |
| last_lng | REAL | |

### Table: `location_override`

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | always row 1 |
| lat | REAL | |
| lng | REAL | |
| set_at | DATETIME | |

---

## 7. Frontend Spec (Nuxt 3 + Tailwind + Leaflet)

### 7.1 Pages

#### `/` — Dashboard
- Total devices seen (stat card)
- Total sightings (stat card)
- Last scan time (stat card)
- Active scanner status (stat card)
- Recent sightings list (last 10)

#### `/map` — Map View
- Full viewport Leaflet map
- Marker per sighting, colored by recency
- Click marker → popup with MAC, name, RSSI, time
- Filter panel: by MAC, by time range
- Auto-refresh every 30 seconds

#### `/devices` — Device Table
- Sortable table: MAC, name, first seen, last seen, sighting count, avg RSSI
- Search/filter by MAC or name
- Click row → navigate to device history

#### `/devices/[mac]` — Device History
- Device summary card (MAC, name, total sightings)
- Leaflet map showing all sighting locations for this device
- Timeline table of all sightings (time, location, RSSI)

### 7.2 Layout
- Sidebar navigation on desktop (≥ lg breakpoint)
- Bottom tab navigation on mobile
- Dark theme preferred (surveillance/night aesthetic)
- Tailwind CSS utility classes throughout

### 7.3 State Management (Pinia)
- `useDevicesStore` — device list, fetch, filter
- `useSightingsStore` — sightings list, fetch, filter, auto-refresh

### 7.4 API Client
- Use Nuxt `$fetch` / `ofetch`
- Base URL from runtime config (`NUXT_PUBLIC_API_BASE`)
- Handle loading and error states on all pages

---

## 8. Docker Compose

### `docker-compose.yml` (production)

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///./data/sousveiller.db
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NUXT_PUBLIC_API_BASE=http://localhost:8000/api
    depends_on:
      - backend
    restart: unless-stopped
```

### `docker-compose.dev.yml` (development overrides)

```yaml
services:
  backend:
    volumes:
      - ./backend:/app
      - ./data:/app/data
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    volumes:
      - ./frontend:/app
    command: npm run dev
```

### Run commands
```bash
# Development (hot reload)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker compose up --build

# Stop
docker compose down
```

---

## 9. POC Milestones

1. **Firmware — WiFiManager** — portal launches, saves config to Preferences
2. **Firmware — BT Scanner** — scans BT devices, logs to Serial
3. **Firmware — GPS Sim** — simulated walking path increments each scan
4. **Firmware — REST Client** — POSTs scan batches to backend
5. **Backend** — FastAPI ingests batches, stores to SQLite, serves API
6. **Frontend** — Dashboard and map render live data from backend
7. **Integration** — Full pipeline running end to end via Docker Compose
8. **Validation** — Simulated walk produces visible device trail on map

---

## 10. Out of Scope (POC)

- BLE fingerprinting / re-identification across MAC rotations
- Multi-ESP32 unit support
- Authentication / API keys
- Real GPS module integration
- Mobile app
- Heatmaps and analytics
- Production deployment / TLS
