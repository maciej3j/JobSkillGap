from fastapi.testclient import TestClient

from job_skill_gap.main import app


def test_health_check():
    r = TestClient(app).get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "OK"}
