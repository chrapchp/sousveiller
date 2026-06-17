#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include <climits>
#include <DebugLog.h>

#include "wifi_client.h"

static String iso_timestamp() {
    time_t     now = time(nullptr);
    struct tm *t   = gmtime(&now);
    char       buf[32];
    strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", t);
    return String(buf);
}

static bool http_post(const String &url, const String &body) {
    for (int attempt = 1; attempt <= 3; attempt++) {
        HTTPClient http;
        http.begin(url);
        http.addHeader("Content-Type", "application/json");
        int code = http.POST(body);
        http.end();
        if (code == 200 || code == 201) return true;
        LOG_WARN("[HTTP] POST attempt", attempt, "failed, code ", code);
        delay(2000);
    }
    return false;
}

bool wifi_client_post_scan(const String &server_url, const String &device_id,
                           const std::vector<BLEDeviceData> &devices,
                           const GpsCoord &location) {
    JsonDocument doc;
    doc["device_id"]  = device_id;
    doc["scanned_at"] = iso_timestamp();

    JsonObject loc = doc["location"].to<JsonObject>();
    loc["lat"]       = location.lat;
    loc["lng"]       = location.lng;
    loc["simulated"] = location.simulated;

    JsonArray arr = doc["devices"].to<JsonArray>();
    for (const auto &d : devices) {
        JsonObject obj = arr.add<JsonObject>();
        obj["mac"]               = d.mac;
        obj["rssi"]              = d.rssi;
        obj["name"]              = d.name;
        obj["manufacturer_data"] = d.manufacturer_data;
        JsonArray uuids = obj["service_uuids"].to<JsonArray>();
        for (const auto &u : d.service_uuids) uuids.add(u);
        if (d.tx_power != INT_MIN)  obj["tx_power"]       = d.tx_power;
        if (d.adv_interval_ms >= 0) obj["adv_interval_ms"] = d.adv_interval_ms;
    }

    String body;
    serializeJson(doc, body);
    LOG_INFO("[HTTP] Posting", (int)devices.size(), "device(s) to", (server_url + "/api/scans").c_str());
    return http_post(server_url + "/api/scans", body);
}

bool wifi_client_get_location_override(const String &server_url,
                                       double &out_lat, double &out_lng) {
    HTTPClient http;
    http.begin(server_url + "/api/location");
    int code = http.GET();
    if (code != 200) {
        http.end();
        return false;
    }
    String resp = http.getString();
    http.end();

    JsonDocument doc;
    if (deserializeJson(doc, resp) || !doc["lat"].is<double>()) return false;

    out_lat = doc["lat"].as<double>();
    out_lng = doc["lng"].as<double>();
    return true;
}
