import json
from pathlib import Path

from job_skill_gap.adapters.greenhouse import GreenhouseAdapter

FIX = Path(__file__).parent.parent / "fixtures/greenhouse/gitlab.json"


def test_to_unified_on_fixture():
    jobs = json.loads(FIX.read_text())["jobs"]
    adapter = GreenhouseAdapter()
    offer = adapter.to_unified(jobs[0])
    assert offer.title
    assert "&lt;" not in (offer.description_text or "")
    assert adapter.external_id(jobs[0]) == str(jobs[0]["id"])
