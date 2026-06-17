#pragma once

// Network defaults (overridden by WiFiManager/Preferences at runtime)
#define DEFAULT_SERVER_URL        "http://192.168.1.77:8000"
#define DEFAULT_DEVICE_ID         "sourveiller-001"

// Scanning defaults
#define DEFAULT_SCAN_INTERVAL_MS  30000   // ms between scan batches
#define DEFAULT_SCAN_DURATION_MS   5000   // ms to scan per batch
#define DEFAULT_MIN_RSSI            -90   // ignore weaker signals
#define DEFAULT_MAX_BATCH_SIZE       50   // max devices per POST

// Simulated GPS defaults
#define DEFAULT_SIM_START_LAT     51.0742777778
#define DEFAULT_SIM_START_LNG   -114.0675
#define DEFAULT_SIM_STEP_LAT     0.00005  // ~5m per step
#define DEFAULT_SIM_STEP_LNG     0.00003  // ~3m per step
#define DEFAULT_SIM_STEPS_TURN       20   // steps before direction change

// Hardware
#define CONFIG_BUTTON_PIN             0   // GPIO0 = BOOT button
#define CONFIG_PORTAL_TIMEOUT_S     180   // portal auto-closes after 3 min
