from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass
class UnifiedOffer:
    title: str
    location: str | None
    department: str | None
    description_text: str | None
    url: str | None
    updated_at_source: datetime | None


class SourceAdapter(Protocol):
    name: str

    def fetch(self, board_token: str) -> list[dict]: ...
    def external_id(self, payload: dict) -> str: ...
    def to_unified(self, payload: dict) -> UnifiedOffer: ...
