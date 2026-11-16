import json
from pathlib import Path

from job_skill_gap.adapters.lever import LeverAdapter

FIX = Path(__file__).parent.parent / "fixtures/lever/gopuff.json"


def test_to_unified_on_fixture():
    jobs = json.loads(FIX.read_text())
    adapter = LeverAdapter()
    job = jobs[0]

    offer = adapter.to_unified(job)

    assert offer.title == job["text"]
    assert offer.url == job["hostedUrl"]
    assert offer.updated_at_source is not None
    assert adapter.external_id(job) == str(job["id"])
