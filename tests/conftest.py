"""Shared pytest fixtures.

Each test gets a fresh in-memory SQLite database with the `get_db` dependency
overridden so tests never touch the real `app.db` file.

Fixture = "Prepare everything needed before the test runs, and clean up afterward if necessary."

"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.dependencies import get_db
from app.main import app


@pytest.fixture()
def db_session():
    # In-memory SQLite. StaticPool keeps a single shared connection so the
    # schema persists across sessions within one test.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_user_payload():
    return {
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30,
        "is_active": True,
    }
