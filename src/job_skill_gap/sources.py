from enum import StrEnum
from pathlib import Path

from job_skill_gap.adapters.ashby import AshbyAdapter
from job_skill_gap.adapters.greenhouse import GreenhouseAdapter
from job_skill_gap.adapters.lever import LeverAdapter

ADAPTERS = {
    "greenhouse": GreenhouseAdapter,
    "lever": LeverAdapter,
    "ashby": AshbyAdapter,
}


class SourceName(StrEnum):
    greenhouse = "greenhouse"
    level = "lever"
    ashby = "ashby"


def read_tokens(path: Path) -> list[str]:
    lines = (line.strip() for line in path.read_text().splitlines())
    return [line for line in lines if line and not line.startswith("#")]


def company_file(company: str) -> Path:
    return Path("data") / "companies" / f"{company}.txt"
