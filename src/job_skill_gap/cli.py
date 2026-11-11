import logging
from pathlib import Path
from typing import Annotated

import typer

from job_skill_gap.config import get_settings
from job_skill_gap.db import SessionLocal
from job_skill_gap.importer import run_import
from job_skill_gap.sources import ADAPTERS, SourceName, company_file, read_tokens

app = typer.Typer(name="JobSkillGap-cli", no_args_is_help=True)
settings = get_settings()


def _import_one(source: SourceName, file: Path | None, pause: float) -> None:
    path = file or company_file(source.value)
    if not path.exists():
        raise typer.BadParameter(f"No file with companies: {path}")
    adapter = ADAPTERS[source.value]
    with SessionLocal() as db:
        run = run_import(db, adapter, read_tokens(path), pause=pause)
    typer.echo(
        f"[{source.value}] run #{run.id}: {run.status}: | new={run.new_count} "
        f"updated={run.updated_count} unchanged={run.unchanged_count}"
    )
    if run.error:
        typer.echo(run.error)


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
    _import_one(source, file, pause)


@app.command("import-all")
def import_all(
    pause: Annotated[
        float, typer.Option(help="Seconds delay between companies")
    ] = settings.import_pause,
) -> None:
    logging.basicConfig(level=logging.INFO)
    for source in SourceName:
        _import_one(source, None, pause)


if __name__ == "__main__":
    app()
