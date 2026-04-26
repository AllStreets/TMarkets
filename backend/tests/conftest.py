import os
# Set env vars before any app imports so database.py uses SQLite
os.environ.setdefault("POSTGRES_URL", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app import models  # noqa

TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture
def db():
    # StaticPool shares a single in-memory connection across all threads,
    # which is required for TestClient (runs in a thread) to see the same data.
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
