import logging
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from job_skill_gap.adapters.greenhouse import GreenhouseAdapter
from job_skill_gap.db import SessionLocal
from job_skill_gap.importer import run_import

app = typer.Typer(name="JobSkillGap-cli", no_args_is_help=True)

ADAPTERS = {"greenhouse": GreenhouseAdapter}


class SourceName(StrEnum):
    greenhouse = "greenhouse"


def read_tokens(path: Path) -> list[str]:
    lines = (line.strip() for line in path.read_text().splitlines())
    return [line for line in lines if line and not line.startswith("#")]


@app.command("import", no_args_is_help=True)
def import_offers(
    source: SourceName,
    file: Annotated[
        Path, typer.Option(exists=True, help="Plik z firmami, jedna na linię")
    ],
    pause: Annotated[float, typer.Option(help="Sekundy przerwy między firmami")] = 0.0,
) -> None:
    """Importuj oferty z jednego źródła."""
    logging.basicConfig(level=logging.INFO)
    adapter = ADAPTERS[source.value]()
    with SessionLocal() as db:
        run = run_import(db, adapter, read_tokens(file), pause=pause)

    typer.echo(
        f"run #{run.id}: {run.status} | new={run.new_count} "
        f"updated={run.updated_count} unchanged={run.unchanged_count}"
    )
    if run.error:
        typer.echo(run.error)


if __name__ == "__main__":
    app()
