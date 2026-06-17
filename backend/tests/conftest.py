import os
import pathlib
import tempfile

# Point the app at a temp file DB before any app module is imported.
# This must be the first non-stdlib code in this file.
_TEST_DB = pathlib.Path(tempfile.mkdtemp()) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, engine, get_db
from app.main import app  # triggers create_all + migrate_schema against test DB

_TestSession = sessionmaker(bind=engine)


@pytest.fixture()
def client():
    # Fresh schema for every test — drop then recreate all tables.
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def _override_get_db():
        db = _TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
