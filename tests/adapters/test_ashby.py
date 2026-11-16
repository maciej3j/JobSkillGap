import json
from pathlib import Path

from job_skill_gap.adapters.ashby import AshbyAdapter

FIX = Path(__file__).parent.parent / "fixtures/ashby/openai.json"


def test_to_unified_on_fixture():
    jobs = json.loads(FIX.read_text())["jobs"]
    adapter = AshbyAdapter()
    job = jobs[0]

    offer = adapter.to_unified(job)

    assert offer.title == job["title"]
    assert offer.url == job["jobUrl"]
    assert adapter.external_id(job) == str(job["id"])


def test_external_id_falls_back_to_slug():
    adapter = AshbyAdapter()
    payload = {"jobUrl": "https://jobs.ashbyhq.com/acme/abc-123/"}
    assert adapter.external_id(payload) == "abc-123"
