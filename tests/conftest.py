import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

# 1. Create a temporary in-memory SQLite database for testing
# "check_same_thread=False" is needed for SQLite in multi-threaded tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

# 2. Override the dependency
# This forces FastAPI to use our test DB instead of the real one


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# 3. Create a Test Client Fixture


@pytest.fixture(scope="module")
def client():
    # Create tables in the test DB
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as c:
        yield c

    # Drop tables after tests finish (Clean up)
    Base.metadata.drop_all(bind=engine)
