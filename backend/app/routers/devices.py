from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Device, Fingerprint, Sighting
from ..schemas import DeviceOut, FingerprintDetailOut, FingerprintOut, StatsOut

router = APIRouter()


@router.get("/devices", response_model=list[DeviceOut])
async def list_devices(db: Session = Depends(get_db)) -> list[DeviceOut]:
    return db.query(Device).order_by(Device.last_seen.desc()).all()


@router.get("/stats", response_model=StatsOut)
async def get_stats(db: Session = Depends(get_db)) -> StatsOut:
    total_devices   = db.query(func.count(Device.mac)).scalar() or 0
    total_sightings = db.query(func.count(Sighting.id)).scalar() or 0
    last_scan       = db.query(func.max(Sighting.seen_at)).scalar()

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=5)
    active_scanners = (
        db.query(func.count(func.distinct(Sighting.device_id)))
        .filter(Sighting.seen_at >= cutoff)
        .scalar() or 0
    )

    return StatsOut(
        total_devices=total_devices,
        total_sightings=total_sightings,
        active_scanners=active_scanners,
        last_scan=last_scan,
    )


@router.get("/fingerprints", response_model=list[FingerprintOut])
async def list_fingerprints(db: Session = Depends(get_db)) -> list[FingerprintOut]:
    return db.query(Fingerprint).order_by(Fingerprint.last_seen.desc()).all()


@router.get("/fingerprints/{fingerprint_hash}", response_model=FingerprintDetailOut)
async def get_fingerprint(fingerprint_hash: str, db: Session = Depends(get_db)) -> FingerprintDetailOut:
    fp = db.query(Fingerprint).filter(Fingerprint.fingerprint_hash == fingerprint_hash).first()
    if fp is None:
        raise HTTPException(status_code=404, detail="Fingerprint not found")
    devices = (
        db.query(Device)
        .filter(Device.fingerprint_hash == fingerprint_hash)
        .order_by(Device.last_seen.desc())
        .all()
    )
    return FingerprintDetailOut(
        fingerprint_hash=fp.fingerprint_hash,
        strategy=fp.strategy,
        service_uuids_key=fp.service_uuids_key,
        mfr_prefix=fp.mfr_prefix,
        first_seen=fp.first_seen,
        last_seen=fp.last_seen,
        mac_count=fp.mac_count,
        sighting_count=fp.sighting_count,
        devices=[DeviceOut.model_validate(d) for d in devices],
    )
