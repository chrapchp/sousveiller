#include <Arduino.h>
#include <DebugLog.h>
#include "config.h"
#include "config_manager.h"
#include "bt_scanner.h"
#include "gps_sim.h"
#include "wifi_client.h"

static AppConfig cfg;
static unsigned long last_scan_ms = 0;
Stream *debugOutputStream = NULL;

void setup()
{

#ifdef DBG_LOG
    Serial.begin(115200);
    delay(500);
    Serial.println("\n\nHome Hydroponics System Starting...");
    debugOutputStream = &Serial;
#endif


    config_manager_init(cfg);

    gps_sim_init(DEFAULT_SIM_START_LAT, DEFAULT_SIM_START_LNG,
                 cfg.sim_step_lat, cfg.sim_step_lng, DEFAULT_SIM_STEPS_TURN);

    bt_scanner_init();

    double lat, lng;
    if (wifi_client_get_location_override(cfg.server_url, lat, lng))
        gps_sim_override(lat, lng);

    Serial.println("[Main] Setup complete");
}

void loop()
{
    config_manager_check_button();

    if (config_manager_portal_requested())
    {
        config_manager_relaunch_portal(cfg);
        gps_sim_init(DEFAULT_SIM_START_LAT, DEFAULT_SIM_START_LNG,
                     cfg.sim_step_lat, cfg.sim_step_lng, DEFAULT_SIM_STEPS_TURN);
    }

    unsigned long now = millis();
    if (now - last_scan_ms >= (unsigned long)cfg.scan_interval_ms)
    {
        last_scan_ms = now;

        GpsCoord pos = gps_sim_next();
        std::vector<BLEDeviceData> devs = bt_scanner_scan(
            cfg.scan_duration_ms, cfg.min_rssi, DEFAULT_MAX_BATCH_SIZE);

        if (!devs.empty())
            wifi_client_post_scan(cfg.server_url, cfg.device_id, devs, pos);
        else
            LOG_INFO("[Main] No devices in scan window");
     

        double lat, lng;
        if (wifi_client_get_location_override(cfg.server_url, lat, lng))
            gps_sim_override(lat, lng);
    }
}
