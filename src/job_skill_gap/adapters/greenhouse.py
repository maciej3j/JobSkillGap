import html
from asyncio import timeout
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from job_skill_gap.adapters.base import UnifiedOffer

BASE = "https://boards-api.greenhouse.io/v1/boards"


def html_to_text(escaped_html: str | None) -> str | None:
    if not escaped_html:
        return None
    return BeautifulSoup(html.unescape(escaped_html), "html.parser").get_text(
        "\n", strip=True
    )


class GreenhouseAdapter:
    name = "greenhouse"

    def fetch(self, board_token: str) -> list[dict]:
        r = httpx.get(
            f"{BASE}/{board_token}/jobs",
            params={"content": "true"},
            timeout=60,
            headers={"User-Agent": "jobskillgap/0.1"},
        )
        r.raise_for_status()
        return r.json()["jobs"]

    def external_id(self, payload: dict) -> str:
        return str(payload["id"])

    def to_unified(self, payload: dict) -> UnifiedOffer:
        departments = payload.get("departments") or []
        updated = payload.get("updated_at")
        return UnifiedOffer(
            title=payload["title"],
            location=(payload.get("location") or {}).get("name"),
            department=departments[0]["name"] if departments else None,
            description_text=html_to_text(payload.get("content")),
            url=payload.get("absolute_url"),
            updated_at_source=datetime.fromisoformat(updated) if updated else None,
        )
