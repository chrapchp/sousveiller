from __future__ import annotations
import json
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, field_validator


class LocationIn(BaseModel):
    lat: float
    lng: float
    simulated: bool = True


class DeviceIn(BaseModel):
    mac: str
    rssi: int
    name: Optional[str] = None
    manufacturer_data: Optional[str] = None
    service_uuids: list[str] = []
    tx_power: Optional[int] = None
    adv_interval_ms: Optional[int] = None


class ScanBatch(BaseModel):
    device_id: str
    scanned_at: datetime
    location: LocationIn
    devices: list[DeviceIn]


class ScanResponse(BaseModel):
    accepted: int
    duplicate: int
    rejected: int


class SightingOut(BaseModel):
    id: int
    mac: str
    rssi: int
    name: Optional[str]
    manufacturer_data: Optional[str]
    service_uuids: list[str]
    tx_power: Optional[int]
    fingerprint_hash: Optional[str] = None
    lat: float
    lng: float
    simulated: bool
    device_id: str
    seen_at: datetime

    model_config = {"from_attributes": True}


class DeviceOut(BaseModel):
    mac: str
    name: Optional[str]
    manufacturer_data: Optional[str]
    service_uuids: list[str] = []
    fingerprint_hash: Optional[str] = None
    first_seen: datetime
    last_seen: datetime
    sighting_count: int
    avg_rssi: float
    last_lat: float
    last_lng: float

    @field_validator("service_uuids", mode="before")
    @classmethod
    def _parse_service_uuids(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            return json.loads(v) if v else []
        return v or []

    model_config = {"from_attributes": True}


class FingerprintOut(BaseModel):
    fingerprint_hash: str
    strategy: str
    service_uuids_key: Optional[str]
    mfr_prefix: Optional[str]
    first_seen: datetime
    last_seen: datetime
    mac_count: int
    sighting_count: int

    model_config = {"from_attributes": True}


class FingerprintDetailOut(FingerprintOut):
    devices: list[DeviceOut]


class StatsOut(BaseModel):
    total_devices: int
    total_sightings: int
    active_scanners: int
    last_scan: Optional[datetime]


class LocationOverrideIn(BaseModel):
    lat: float
    lng: float


class LocationOverrideOut(BaseModel):
    lat: float
    lng: float
    set_at: Optional[datetime] = None


class StatusResponse(BaseModel):
    status: str
