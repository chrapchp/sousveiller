#pragma once
#include <Arduino.h>
#include <vector>
#include "bt_scanner.h"
#include "gps_sim.h"

bool wifi_client_post_scan(const String &server_url, const String &device_id,
                           const std::vector<BLEDeviceData> &devices,
                           const GpsCoord &location);

// Returns true and populates out_lat/out_lng when an override is active on the server.
bool wifi_client_get_location_override(const String &server_url,
                                       double &out_lat, double &out_lng);
