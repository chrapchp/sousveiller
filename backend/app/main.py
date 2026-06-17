import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine, migrate_schema
from .routers import scans, sightings, devices

Base.metadata.create_all(bind=engine)
migrate_schema()

app = FastAPI(title="Sousveiller API", version="0.1.0")

_origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scans.router,     prefix="/api")
app.include_router(sightings.router, prefix="/api")
app.include_router(devices.router,   prefix="/api")
