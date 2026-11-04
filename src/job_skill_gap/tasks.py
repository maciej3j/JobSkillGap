from job_skill_gap.celery_app import celery_app, settings
from job_skill_gap.db import SessionLocal
from job_skill_gap.importer import run_import
from job_skill_gap.sources import ADAPTERS, company_file, read_tokens


@celery_app.task(name="job_skill_gap.tasks.import_source")
def import_source(source: str) -> int:
    return _import_source(source)


def _import_source(source: str, db_factory=SessionLocal) -> int:
    adapter = ADAPTERS[source]()
    tokens = read_tokens(company_file(source))
    with db_factory() as db:
        run = run_import(db, adapter, tokens, pause=settings.import_pause)
        return run.id
