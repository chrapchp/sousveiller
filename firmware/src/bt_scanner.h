#pragma once
#include <Arduino.h>
#include <vector>

struct BLEDeviceData {
    String              mac;
    int                 rssi;
    String              name;
    String              manufacturer_data;
    std::vector<String> service_uuids;
    int                 tx_power;       // INT_MIN if unavailable
    int                 adv_interval_ms; // -1 if unavailable
};

void                       bt_scanner_init();
std::vector<BLEDeviceData> bt_scanner_scan(int duration_ms, int min_rssi, int max_results);
