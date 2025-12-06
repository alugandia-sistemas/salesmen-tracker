import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os
import sys

# Add backend to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, Base, get_db

# Use an in-memory SQLite database or a separate test DB. 
# Since we use PostGIS/Geography, SQLite with SpatiaLite is complex to set up.
# We will mock the database session or use the existing DB with transaction rollback.
# For simplicity in this environment, let's use the existing DB URL but force rollbacks.

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/salesmen_tracker")

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception:
    print("Warning: Database connection failed. Tests might fail if they require DB.")
    engine = None
    TestingSessionLocal = None

@pytest.fixture(scope="session")
def test_db_engine():
    if engine:
        return engine
    pytest.skip("No database connection available")

@pytest.fixture
def db(test_db_engine):
    """
    Creates a new database session for a test.
    Rolls back the transaction after the test is complete.
    """
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    """
    FastAPI TestClient with overridden get_db dependency.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]
