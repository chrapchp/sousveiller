#include <BLEDevice.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include <map>
#include <climits>
#include <DebugLog.h>

#include "bt_scanner.h"

static BLEScan *ble_scan = nullptr;

class ScanCallback : public BLEAdvertisedDeviceCallbacks {
public:
    int                             min_rssi = -90;
    std::map<String, BLEDeviceData> seen;

    void onResult(BLEAdvertisedDevice dev) override {
        if (dev.getRSSI() < min_rssi) return;

        String mac = dev.getAddress().toString().c_str();
        if (seen.count(mac)) return;

        BLEDeviceData d;
        d.mac            = mac;
        d.rssi           = dev.getRSSI();
        d.name           = dev.haveName() ? dev.getName().c_str() : "";
        d.tx_power       = dev.haveTXPower() ? (int)dev.getTXPower() : INT_MIN;
        d.adv_interval_ms = -1;

        if (dev.haveManufacturerData()) {
            String raw = dev.getManufacturerData().c_str();
            String hex;
            for (char c : raw) {
                char buf[3];
                snprintf(buf, sizeof(buf), "%02x", (uint8_t)c);
                hex += buf;
            }
            d.manufacturer_data = hex;
        }

        for (int i = 0; i < dev.getServiceUUIDCount(); i++)
            d.service_uuids.push_back(dev.getServiceUUID(i).toString().c_str());

        seen[mac] = d;
    }
};

static ScanCallback cb;

void bt_scanner_init() {
    BLEDevice::init("");
    ble_scan = BLEDevice::getScan();
    ble_scan->setAdvertisedDeviceCallbacks(&cb, false);
    ble_scan->setActiveScan(true);
    ble_scan->setInterval(100);
    ble_scan->setWindow(99);
    LOG_INFO("[BT] Scanner initialized");

}

std::vector<BLEDeviceData> bt_scanner_scan(int duration_ms, int min_rssi, int max_results) {
    cb.seen.clear();
    cb.min_rssi = min_rssi;

    ble_scan->start(duration_ms / 1000, false);

    std::vector<BLEDeviceData> results;
    for (auto &kv : cb.seen) {
        results.push_back(kv.second);
        if ((int)results.size() >= max_results) break;
    }

    ble_scan->clearResults();
    LOG_INFO("[BT] Scan complete, found device(s):", (int)results.size());
    return results;
}
