from datetime import datetime, timezone, UTC

import httpx
from bs4 import BeautifulSoup

from job_skill_gap.adapters.base import UnifiedOffer

BASE = "https://api.level.co/v0/postings"
PAGE_SIZE = 100


def html_to_text(raw_html: str | None) -> str | None:
    if not raw_html:
        return None
    return BeautifulSoup(raw_html, "html.parser").get_text("\n", strip=True)


class LeverAdapter:
    name = "lever"

    def fetch(self, board_token: str) -> list[dict]:
        jobs: list[dict] = []
        seen: set[str] = set()
        skip = 0
        while True:
            r = httpx.get(
                f"{BASE}/{board_token}",
                params={"mode": "json", "skip": skip, "limit": PAGE_SIZE},
                timeout=60,
                headers={"User-Agent": "jobskillgap/0.1"},
            )
            r.raise_for_status()
            page = r.json()
            fresh = [j for j in page if str(j["id"]) not in seen]
            if not fresh:
                return jobs
            for j in fresh:
                seen.add(str(j["id"]))
            jobs.extend(fresh)
            if len(page) < PAGE_SIZE:
                return jobs
            skip += PAGE_SIZE

    def external_id(self, payload: dict) -> str:
        return str(payload["id"])

    def to_unified(self, payload: dict) -> UnifiedOffer:
        categories = payload.get("categories") or {}
        created = payload.get("createdAt")
        return UnifiedOffer(
            title=payload["text"],
            location=categories.get("location") or payload.get("country"),
            department=categories.get("department") or payload.get("team"),
            description_text=payload.get("descriptionPlain")
            or html_to_text(payload.get("description")),
            url=payload.get("hostedUrl"),
            updated_at_source=(
                datetime.fromtimestamp(created / 1000, tz=UTC) if created else None
            ),
        )
