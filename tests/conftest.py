from fastapi.testclient import TestClient
from job_skill_gap.main import create_application
from sqlalchemy.orm import Session
from job_skill_gap.db import Base, get_db
import os
from sqlalchemy import create_engine, Engine
import pytest


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(os.environ["TEST_DATABASE_URL"])
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def db(test_engine: Engine):
    with test_engine.connect() as conn:
        transaction = conn.begin()
        session = Session(bind=conn, join_transaction_mode="create_savepoint")
        yield session
        session.close()
        transaction.rollback()


@pytest.fixture
def client(db):
    app = create_application()
    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app)
