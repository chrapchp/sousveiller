#include <WiFiManager.h>
#include <Preferences.h>
#include <DebugLog.h>

#include "config_manager.h"
#include "config.h"
#include "app_helpers.h"

static WiFiManager   wm;
static bool          portal_requested  = false;
static unsigned long button_held_since = 0;

static void load_prefs(AppConfig &cfg) {
    Preferences p;
    p.begin("sousveiller", true);
    cfg.server_url      = p.getString("server_url",   DEFAULT_SERVER_URL);
    cfg.device_id       = p.getString("device_id",    DEFAULT_DEVICE_ID);
    cfg.scan_interval_ms = p.getInt("scan_interval",  DEFAULT_SCAN_INTERVAL_MS);
    cfg.scan_duration_ms = p.getInt("scan_duration",  DEFAULT_SCAN_DURATION_MS);
    cfg.min_rssi        = p.getInt("min_rssi",        DEFAULT_MIN_RSSI);
    cfg.sim_step_lat    = p.getFloat("sim_step_lat",  DEFAULT_SIM_STEP_LAT);
    cfg.sim_step_lng    = p.getFloat("sim_step_lng",  DEFAULT_SIM_STEP_LNG);
    p.end();
}

void config_manager_save(const AppConfig &cfg) {
    Preferences p;
    p.begin("sousveiller", false);
    p.putString("server_url",  cfg.server_url);
    p.putString("device_id",   cfg.device_id);
    p.putInt("scan_interval",  cfg.scan_interval_ms);
    p.putInt("scan_duration",  cfg.scan_duration_ms);
    p.putInt("min_rssi",       cfg.min_rssi);
    p.putFloat("sim_step_lat", cfg.sim_step_lat);
    p.putFloat("sim_step_lng", cfg.sim_step_lng);
    p.end();
}

static void run_portal(AppConfig &cfg) {
    WiFiManagerParameter p_srv("server_url",    "Server URL",       cfg.server_url.c_str(),              64);
    WiFiManagerParameter p_id("device_id",      "Device ID",        cfg.device_id.c_str(),               32);
    WiFiManagerParameter p_si("scan_interval",  "Scan interval ms", String(cfg.scan_interval_ms).c_str(), 8);
    WiFiManagerParameter p_sd("scan_duration",  "Scan duration ms", String(cfg.scan_duration_ms).c_str(), 8);
    WiFiManagerParameter p_rs("min_rssi",       "Min RSSI",         String(cfg.min_rssi).c_str(),          8);
    WiFiManagerParameter p_lt("sim_step_lat",   "Sim step lat",     String(cfg.sim_step_lat, 6).c_str(),  12);
    WiFiManagerParameter p_ln("sim_step_lng",   "Sim step lng",     String(cfg.sim_step_lng, 6).c_str(),  12);

    wm.addParameter(&p_srv);
    wm.addParameter(&p_id);
    wm.addParameter(&p_si);
    wm.addParameter(&p_sd);
    wm.addParameter(&p_rs);
    wm.addParameter(&p_lt);
    wm.addParameter(&p_ln);

    wm.setConfigPortalTimeout(CONFIG_PORTAL_TIMEOUT_S);
    wm.startConfigPortal("Sousveiller-Setup");

    cfg.server_url       = p_srv.getValue();
    cfg.device_id        = p_id.getValue();
    cfg.scan_interval_ms = String(p_si.getValue()).toInt();
    cfg.scan_duration_ms = String(p_sd.getValue()).toInt();
    cfg.min_rssi         = String(p_rs.getValue()).toInt();
    cfg.sim_step_lat     = String(p_lt.getValue()).toFloat();
    cfg.sim_step_lng     = String(p_ln.getValue()).toFloat();

    config_manager_save(cfg);
    LOG_INFO("[Config] Settings saved from portal");

    
}

void config_manager_init(AppConfig &cfg) {
    load_prefs(cfg);
    pinMode(CONFIG_BUTTON_PIN, INPUT_PULLUP);

    wm.setConfigPortalTimeout(CONFIG_PORTAL_TIMEOUT_S);
    if (!wm.autoConnect("Sousveiller-Setup")) {
        Serial.println("[Config] Auto-connect failed, launching portal");
        run_portal(cfg);
    }
    LOG_INFO("[Config] Connected — server: ", cfg.server_url.c_str(), "device: " , cfg.device_id.c_str());

}

void config_manager_check_button() {
    if (digitalRead(CONFIG_BUTTON_PIN) == LOW) {
        if (button_held_since == 0) button_held_since = millis();
        if (millis() - button_held_since >= 3000 && !portal_requested) {
            portal_requested = true;
            LOG_INFO("[Config] Button held 3s — portal requested");
        }
    } else {
        button_held_since = 0;
    }
}

bool config_manager_portal_requested() {
    if (!portal_requested) return false;
    portal_requested = false;
    return true;
}

void config_manager_relaunch_portal(AppConfig &cfg) {
    LOG_INFO("[Config] Relaunching config portal");
    run_portal(cfg);
}
