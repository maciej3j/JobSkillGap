import logging
from pathlib import Path
from typing import Annotated

import typer

from job_skill_gap.db import SessionLocal
from job_skill_gap.importer import run_import
from job_skill_gap.sources import ADAPTERS, SourceName, read_tokens

app = typer.Typer(name="JobSkillGap-cli", no_args_is_help=True)


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
