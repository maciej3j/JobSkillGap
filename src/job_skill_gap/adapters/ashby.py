from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from job_skill_gap.adapters.base import UnifiedOffer

BASE = "https://api.ashbyhq.com/posting-api/job-board"


def html_to_text(raw_html: str | None) -> str | None:
    if not raw_html:
        return None
    return BeautifulSoup(raw_html, "html.parser").get_text("\n", strip=True)


class AshbyAdapter:
    name = "ashby"

    def fetch(self, board_token: str) -> list[dict]:
        r = httpx.get(
            f"{BASE}/{board_token}",
            timeout=60,
            headers={"User-Agent": "jobskillgap/0.1"},
        )
        r.raise_for_status()
        jobs = r.json().get("jobs") or []
        return [j for j in jobs if j.get("isListed", True)]

    def external_id(self, payload: dict) -> str:
        job_id = payload.get("id")
        if job_id:
            return str(job_id)
        slug = (payload.get("jobUrl") or "").rstrip("/").split("/")[-1]
        if not slug:
            raise ValueError("Ashby payload doesn't have id and jobUrl!")
        return slug

    def to_unified(self, payload: dict) -> UnifiedOffer:
        published = payload.get("publishedAt")
        return UnifiedOffer(
            title=payload["title"],
            location=payload.get("location"),
            department=payload.get("department") or payload.get("team"),
            description_text=payload.get("descriptionPlain")
            or html_to_text(payload.get("descriptionHtml")),
            url=payload.get("jobUrl"),
            updated_at_source=(
                datetime.fromisoformat(published) if published else None
            ),
        )
