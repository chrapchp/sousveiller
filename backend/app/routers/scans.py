import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..fingerprint import compute_fingerprint, features_from_device_in, get_active_strategy
from ..models import Device, Fingerprint, LocationOverride, Sighting
from ..schemas import (LocationOverrideIn, LocationOverrideOut,
                       ScanBatch, ScanResponse, StatusResponse)

router = APIRouter()


@router.post("/scans", response_model=ScanResponse)
async def ingest_scan(batch: ScanBatch, db: Session = Depends(get_db)) -> ScanResponse:
    accepted = duplicate = rejected = 0

    for dev in batch.devices:
        already = (
            db.query(Sighting)
            .filter(Sighting.mac == dev.mac, Sighting.seen_at == batch.scanned_at)
            .first()
        )
        if already:
            duplicate += 1
            continue
        sp = db.begin_nested()
        try:
            features               = features_from_device_in(dev)
            fp_hash, fp_components = compute_fingerprint(features)

            sighting = Sighting(
                mac=dev.mac,
                rssi=dev.rssi,
                name=dev.name,
                manufacturer_data=dev.manufacturer_data,
                service_uuids=json.dumps(dev.service_uuids),
                tx_power=dev.tx_power,
                adv_interval_ms=dev.adv_interval_ms,
                fingerprint_hash=fp_hash,
                lat=batch.location.lat,
                lng=batch.location.lng,
                simulated=batch.location.simulated,
                device_id=batch.device_id,
                seen_at=batch.scanned_at,
            )
            db.add(sighting)

            is_new_mac = _upsert_device(db, dev, batch, fp_hash)
            if fp_hash:
                _upsert_fingerprint(db, fp_hash, fp_components, batch.scanned_at, is_new_mac)

            sp.commit()
            accepted += 1
        except Exception:
            sp.rollback()
            rejected += 1

    db.commit()
    return ScanResponse(accepted=accepted, duplicate=duplicate, rejected=rejected)


def _upsert_device(db: Session, dev, batch: ScanBatch, fp_hash: str | None) -> bool:
    """Upsert the device summary row. Returns True if this MAC is new to fp_hash."""
    device = db.query(Device).filter(Device.mac == dev.mac).first()
    if device is None:
        db.add(Device(
            mac=dev.mac,
            name=dev.name,
            manufacturer_data=dev.manufacturer_data,
            service_uuids=json.dumps(dev.service_uuids),
            fingerprint_hash=fp_hash,
            first_seen=batch.scanned_at,
            last_seen=batch.scanned_at,
            sighting_count=1,
            avg_rssi=float(dev.rssi),
            last_lat=batch.location.lat,
            last_lng=batch.location.lng,
        ))
        return True

    is_new_to_fp = device.fingerprint_hash != fp_hash
    n = device.sighting_count
    device.avg_rssi       = (device.avg_rssi * n + dev.rssi) / (n + 1)
    device.sighting_count += 1
    device.last_seen      = batch.scanned_at
    device.last_lat       = batch.location.lat
    device.last_lng       = batch.location.lng
    if dev.name:               device.name = dev.name
    if dev.manufacturer_data:  device.manufacturer_data = dev.manufacturer_data
    if dev.service_uuids:      device.service_uuids = json.dumps(dev.service_uuids)
    device.fingerprint_hash = fp_hash
    return is_new_to_fp


def _upsert_fingerprint(
    db: Session,
    fp_hash: str,
    components: dict[str, str],
    timestamp: datetime,
    is_new_mac: bool,
) -> None:
    fp = db.query(Fingerprint).filter(Fingerprint.fingerprint_hash == fp_hash).first()
    if fp is None:
        db.add(Fingerprint(
            fingerprint_hash=fp_hash,
            strategy=get_active_strategy().name,
            service_uuids_key=components.get("service_uuids_key"),
            mfr_prefix=components.get("mfr_prefix"),
            first_seen=timestamp,
            last_seen=timestamp,
            mac_count=1,
            sighting_count=1,
        ))
    else:
        fp.sighting_count += 1
        fp.last_seen = timestamp
        if is_new_mac:
            fp.mac_count += 1


@router.post("/location", response_model=StatusResponse)
async def set_location(loc: LocationOverrideIn, db: Session = Depends(get_db)) -> StatusResponse:
    now      = datetime.now(timezone.utc)
    override = db.query(LocationOverride).filter(LocationOverride.id == 1).first()
    if override is None:
        db.add(LocationOverride(id=1, lat=loc.lat, lng=loc.lng, set_at=now))
    else:
        override.lat    = loc.lat
        override.lng    = loc.lng
        override.set_at = now
    db.commit()
    return StatusResponse(status="ok")


@router.get("/location", response_model=LocationOverrideOut)
async def get_location(db: Session = Depends(get_db)) -> LocationOverrideOut:
    override = db.query(LocationOverride).filter(LocationOverride.id == 1).first()
    if override is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No location override set")
    return LocationOverrideOut(lat=override.lat, lng=override.lng, set_at=override.set_at)
