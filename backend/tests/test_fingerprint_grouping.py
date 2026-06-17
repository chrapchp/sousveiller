"""
Synthetic injection tests for BLE fingerprint grouping.

Each test POSTs crafted scan batches with controlled feature sets and
asserts that /api/fingerprints reflects the expected grouping.
"""
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_T0 = "2026-06-17T10:00:00Z"
_T1 = "2026-06-17T10:01:00Z"
_T2 = "2026-06-17T10:02:00Z"


def _batch(
    mac: str,
    *,
    service_uuids: list[str] | None = None,
    mfr_data: str | None = None,
    timestamp: str = _T0,
) -> dict:
    device: dict = {"mac": mac, "rssi": -60}
    if service_uuids is not None:
        device["service_uuids"] = service_uuids
    if mfr_data is not None:
        device["manufacturer_data"] = mfr_data
    return {
        "device_id": "test-unit",
        "scanned_at": timestamp,
        "location": {"lat": 37.7749, "lng": -122.4194, "simulated": True},
        "devices": [device],
    }


def _post(client: TestClient, batch: dict) -> dict:
    r = client.post("/api/scans", json=batch)
    assert r.status_code == 200, r.text
    return r.json()


def _fingerprints(client: TestClient) -> list[dict]:
    r = client.get("/api/fingerprints")
    assert r.status_code == 200
    return r.json()


def _fingerprint_detail(client: TestClient, fp_hash: str) -> dict:
    r = client.get(f"/api/fingerprints/{fp_hash}")
    assert r.status_code == 200
    return r.json()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_same_features_grouped_under_one_fingerprint(client: TestClient):
    """Two different MACs with identical service UUIDs and the same mfr prefix
    must land in one fingerprint group with mac_count == 2."""
    _post(client, _batch("AA:BB:CC:DD:EE:01",
        service_uuids=["fe9f", "fd6f"], mfr_data="4c001200", timestamp=_T0))
    _post(client, _batch("AA:BB:CC:DD:EE:02",
        service_uuids=["fe9f", "fd6f"], mfr_data="4c001299", timestamp=_T1))
    # "4c001200" and "4c001299" share the same 3-byte prefix "4c0012"

    fps = _fingerprints(client)
    assert len(fps) == 1
    assert fps[0]["mac_count"] == 2
    assert fps[0]["sighting_count"] == 2


def test_uuid_order_does_not_affect_grouping(client: TestClient):
    """Service UUIDs are sorted before hashing, so advertisement order must
    not produce different fingerprints for the same logical set."""
    _post(client, _batch("AA:BB:CC:DD:EE:01",
        service_uuids=["fe9f", "fd6f"], timestamp=_T0))
    _post(client, _batch("AA:BB:CC:DD:EE:02",
        service_uuids=["fd6f", "fe9f"], timestamp=_T1))

    fps = _fingerprints(client)
    assert len(fps) == 1
    assert fps[0]["mac_count"] == 2


def test_different_features_produce_separate_fingerprints(client: TestClient):
    """Devices with distinct service UUIDs must not be merged."""
    _post(client, _batch("AA:BB:CC:DD:EE:01",
        service_uuids=["fe9f"], timestamp=_T0))
    _post(client, _batch("AA:BB:CC:DD:EE:02",
        service_uuids=["180d"], timestamp=_T1))

    fps = _fingerprints(client)
    assert len(fps) == 2
    for fp in fps:
        assert fp["mac_count"] == 1


def test_no_signal_produces_no_fingerprint(client: TestClient):
    """A device advertising no service UUIDs and no manufacturer data
    cannot be fingerprinted and must not appear in the fingerprints list."""
    _post(client, _batch("AA:BB:CC:DD:EE:01",
        service_uuids=[], mfr_data=None, timestamp=_T0))

    assert _fingerprints(client) == []

    devices = client.get("/api/devices").json()
    assert len(devices) == 1
    assert devices[0]["fingerprint_hash"] is None


def test_mfr_prefix_only_is_sufficient_for_grouping(client: TestClient):
    """When no service UUIDs are present, devices sharing only the mfr data
    prefix (first 3 bytes) must still be grouped together."""
    _post(client, _batch("AA:BB:CC:DD:EE:01",
        service_uuids=[], mfr_data="4c0012aabbcc", timestamp=_T0))
    _post(client, _batch("AA:BB:CC:DD:EE:02",
        service_uuids=[], mfr_data="4c001299ddeeff", timestamp=_T1))

    fps = _fingerprints(client)
    assert len(fps) == 1
    assert fps[0]["mac_count"] == 2
    assert fps[0]["mfr_prefix"] == "4c0012"


def test_same_mac_repeated_increments_sightings_not_mac_count(client: TestClient):
    """Re-seeing the same physical device (same MAC) must increment
    sighting_count but never inflate mac_count."""
    _post(client, _batch("AA:BB:CC:DD:EE:01",
        service_uuids=["fe9f"], timestamp=_T0))
    _post(client, _batch("AA:BB:CC:DD:EE:01",
        service_uuids=["fe9f"], timestamp=_T1))

    fps = _fingerprints(client)
    assert len(fps) == 1
    assert fps[0]["mac_count"] == 1
    assert fps[0]["sighting_count"] == 2


def test_fingerprint_detail_lists_all_linked_macs(client: TestClient):
    """GET /fingerprints/{hash} must return every device MAC that shares
    this fingerprint, enabling the re-identification view in the UI."""
    _post(client, _batch("AA:BB:CC:DD:EE:01",
        service_uuids=["fe9f"], timestamp=_T0))
    _post(client, _batch("AA:BB:CC:DD:EE:02",
        service_uuids=["fe9f"], timestamp=_T1))
    _post(client, _batch("AA:BB:CC:DD:EE:03",
        service_uuids=["fe9f"], timestamp=_T2))

    fps = _fingerprints(client)
    assert len(fps) == 1

    detail = _fingerprint_detail(client, fps[0]["fingerprint_hash"])
    linked_macs = {d["mac"] for d in detail["devices"]}
    assert linked_macs == {
        "AA:BB:CC:DD:EE:01",
        "AA:BB:CC:DD:EE:02",
        "AA:BB:CC:DD:EE:03",
    }


def test_scan_response_counts_are_accurate(client: TestClient):
    """The accepted/duplicate/rejected counts in the POST /scans response
    must reflect actual DB outcomes, not silently swallow errors."""
    result = _post(client, _batch("AA:BB:CC:DD:EE:01",
        service_uuids=["fe9f"], timestamp=_T0))
    assert result == {"accepted": 1, "duplicate": 0, "rejected": 0}

    # Same MAC + same timestamp → duplicate
    result = _post(client, _batch("AA:BB:CC:DD:EE:01",
        service_uuids=["fe9f"], timestamp=_T0))
    assert result == {"accepted": 0, "duplicate": 1, "rejected": 0}
