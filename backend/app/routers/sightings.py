import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Sighting
from ..schemas import SightingOut

router = APIRouter()


def _row_to_out(s: Sighting) -> SightingOut:
    return SightingOut(
        id=s.id,
        mac=s.mac,
        rssi=s.rssi,
        name=s.name,
        manufacturer_data=s.manufacturer_data,
        service_uuids=json.loads(s.service_uuids) if s.service_uuids else [],
        tx_power=s.tx_power,
        lat=s.lat,
        lng=s.lng,
        simulated=s.simulated,
        device_id=s.device_id,
        seen_at=s.seen_at,
    )


@router.get("/sightings", response_model=list[SightingOut])
async def list_sightings(
    limit:  int               = Query(100, ge=1, le=1000),
    offset: int               = Query(0, ge=0),
    mac:    Optional[str]     = None,
    since:  Optional[datetime] = None,
    db:     Session           = Depends(get_db),
) -> list[SightingOut]:
    q = db.query(Sighting)
    if mac:   q = q.filter(Sighting.mac == mac)
    if since: q = q.filter(Sighting.seen_at >= since)
    rows = q.order_by(Sighting.seen_at.desc()).offset(offset).limit(limit).all()
    return [_row_to_out(r) for r in rows]


@router.get("/sightings/{mac}", response_model=list[SightingOut])
async def sightings_by_mac(mac: str, db: Session = Depends(get_db)) -> list[SightingOut]:
    rows = (
        db.query(Sighting)
        .filter(Sighting.mac == mac)
        .order_by(Sighting.seen_at.desc())
        .all()
    )
    return [_row_to_out(r) for r in rows]
