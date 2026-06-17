import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////app/data/sousveiller.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def migrate_schema() -> None:
    """Add columns introduced after the initial schema without losing existing data."""
    additions = [
        ("sightings", "fingerprint_hash", "TEXT"),
        ("devices",   "service_uuids",    "TEXT"),
        ("devices",   "fingerprint_hash", "TEXT"),
    ]
    with engine.connect() as conn:
        for table, column, col_type in additions:
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                conn.commit()
            except Exception:
                pass  # column already exists


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
