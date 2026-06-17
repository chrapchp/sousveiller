#pragma once
#include <Arduino.h>

struct AppConfig {
    String server_url;
    String device_id;
    int    scan_interval_ms;
    int    scan_duration_ms;
    int    min_rssi;
    float  sim_step_lat;
    float  sim_step_lng;
};

void config_manager_init(AppConfig &cfg);
void config_manager_check_button();
bool config_manager_portal_requested();
void config_manager_relaunch_portal(AppConfig &cfg);
void config_manager_save(const AppConfig &cfg);
