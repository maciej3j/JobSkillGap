import json
from copy import deepcopy
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from job_skill_gap.adapters.greenhouse import GreenhouseAdapter
from job_skill_gap.importer import run_import
from job_skill_gap.models import JobOffer, RawOffer

FIXTURE = Path(__file__).parent / "fixtures" / "greenhouse" / "gitlab.json"


class FakeGreenhouse(GreenhouseAdapter):
    def __init__(self, data: dict) -> None:
        self.data = data

    def fetch(self, board_token: str) -> list[dict]:
        result = self.data[board_token]
        if isinstance(result, Exception):
            raise result
        return deepcopy(result)


@pytest.fixture
def jobs() -> list[dict]:
    return json.loads(FIXTURE.read_text())["jobs"]


def count(db: Session, model) -> int:
    return db.scalar(select(func.count()).select_from(model))


def test_import_twice_creates_no_duplicates(db: Session, jobs: list[dict]):
    adapter = FakeGreenhouse({"gitlab": jobs})
    n = len(jobs)
    first = run_import(db, adapter, ["gitlab"])
    assert (first.new_count, first.updated_count, first.unchanged_count) == (n, 0, 0)

    second = run_import(db, adapter, ["gitlab"])
    assert (second.new_count, second.updated_count, second.unchanged_count) == (0, 0, n)
    assert count(db, RawOffer) == n
    assert count(db, JobOffer) == n


def test_changed_payload_is_updated(db: Session, jobs: list[dict]):
    adapter = FakeGreenhouse({"gitlab": jobs})
    run_import(db, adapter, ["gitlab"])
    changed = deepcopy(jobs)
    changed[0]["title"] = "New Title"
    adapter.data["gitlab"] = changed

    run = run_import(db, adapter, ["gitlab"])
    assert run.updated_count == 1
    assert run.unchanged_count == len(jobs) - 1

    raw = db.scalar(
        select(RawOffer).where(RawOffer.external_id == str(changed[0]["id"]))
    )
    assert raw.payload["title"] == "New Title"
    assert raw.offer.title == "New Title"
    assert count(db, RawOffer) == len(jobs)


def test_every_offer_links_to_raw_payload(db: Session, jobs: list[dict]):
    run_import(db, FakeGreenhouse({"gitlab": jobs}), ["gitlab"])

    offers = db.scalars(select(JobOffer)).all()
    assert len(offers) == len(jobs)
    for offer in offers:
        assert offer.raw.external_id == str(offer.raw.payload["id"])
        assert offer.raw.payload["title"] == offer.title


def test_failing_company_does_not_stop_others(db: Session, jobs):
    adapter = FakeGreenhouse({"bad": RuntimeError("boom"), "gitlab": jobs})

    run = run_import(db, adapter, ["bad", "gitlab"])

    assert run.status == "partial"
    assert run.new_count == len(jobs)
    assert "bad" in run.error
    assert count(db, RawOffer) == len(jobs)


def test_all_companies_failing_marks_run_failed(db: Session):
    adapter = FakeGreenhouse({"a": RuntimeError("boom1"), "b": RuntimeError("boom2")})

    run = run_import(db, adapter, ["a", "b"])

    assert run.status == "failed"
    assert count(db, RawOffer) == 0
