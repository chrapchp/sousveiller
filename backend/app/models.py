from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class Sighting(Base):
    __tablename__ = "sightings"

    id:                Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    mac:               Mapped[str]           = mapped_column(Text,    nullable=False, index=True)
    rssi:              Mapped[int]           = mapped_column(Integer, nullable=False)
    name:              Mapped[str | None]    = mapped_column(Text,    nullable=True)
    manufacturer_data: Mapped[str | None]    = mapped_column(Text,    nullable=True)
    service_uuids:     Mapped[str | None]    = mapped_column(Text,    nullable=True)  # JSON array string
    tx_power:          Mapped[int | None]    = mapped_column(Integer, nullable=True)
    adv_interval_ms:   Mapped[int | None]    = mapped_column(Integer, nullable=True)
    fingerprint_hash:  Mapped[str | None]    = mapped_column(Text,    nullable=True, index=True)
    lat:               Mapped[float]         = mapped_column(Float,   nullable=False)
    lng:               Mapped[float]         = mapped_column(Float,   nullable=False)
    simulated:         Mapped[bool]          = mapped_column(Boolean, nullable=False)
    device_id:         Mapped[str]           = mapped_column(Text,    nullable=False)
    seen_at:           Mapped[datetime]      = mapped_column(DateTime, nullable=False)


class Device(Base):
    __tablename__ = "devices"

    mac:               Mapped[str]        = mapped_column(Text,    primary_key=True)
    name:              Mapped[str | None] = mapped_column(Text,    nullable=True)
    manufacturer_data: Mapped[str | None] = mapped_column(Text,    nullable=True)
    service_uuids:     Mapped[str | None] = mapped_column(Text,    nullable=True)  # JSON array string
    fingerprint_hash:  Mapped[str | None] = mapped_column(Text,    nullable=True, index=True)
    first_seen:        Mapped[datetime]   = mapped_column(DateTime, nullable=False)
    last_seen:         Mapped[datetime]   = mapped_column(DateTime, nullable=False)
    sighting_count:    Mapped[int]        = mapped_column(Integer, nullable=False, default=0)
    avg_rssi:          Mapped[float]      = mapped_column(Float,   nullable=False, default=0.0)
    last_lat:          Mapped[float]      = mapped_column(Float,   nullable=False)
    last_lng:          Mapped[float]      = mapped_column(Float,   nullable=False)


class Fingerprint(Base):
    __tablename__ = "fingerprints"

    fingerprint_hash:  Mapped[str]        = mapped_column(Text,    primary_key=True)
    strategy:          Mapped[str]        = mapped_column(Text,    nullable=False)
    service_uuids_key: Mapped[str | None] = mapped_column(Text,    nullable=True)
    mfr_prefix:        Mapped[str | None] = mapped_column(Text,    nullable=True)
    first_seen:        Mapped[datetime]   = mapped_column(DateTime, nullable=False)
    last_seen:         Mapped[datetime]   = mapped_column(DateTime, nullable=False)
    mac_count:         Mapped[int]        = mapped_column(Integer, nullable=False, default=1)
    sighting_count:    Mapped[int]        = mapped_column(Integer, nullable=False, default=0)


class LocationOverride(Base):
    __tablename__ = "location_override"

    id:     Mapped[int]      = mapped_column(Integer, primary_key=True, default=1)
    lat:    Mapped[float]    = mapped_column(Float,   nullable=False)
    lng:    Mapped[float]    = mapped_column(Float,   nullable=False)
    set_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
