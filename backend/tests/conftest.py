import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.api.deps import get_db
from app.models.user import User
from app.models.organization import Organization
from app.core.security import hash_password

# Use a separate test database (PostgreSQL)
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db:5432/test_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after test session
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def get_auth_headers(client, username, password):
    """Helper function to get authentication headers"""
    response = client.post(
        "/auth/login", 
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code != 200:
        raise Exception(f"Login failed: {response.json()}")
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
