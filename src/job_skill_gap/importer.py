import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from job_skill_gap.adapters.base import SourceAdapter, UnifiedOffer
from job_skill_gap.models import Company, ImportRun, JobOffer, RawOffer, Source

log = logging.getLogger(__name__)


def compute_hash(payload: dict) -> str:
    canonical = json.dumps(
        payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def get_or_create_source(db: Session, name: str) -> Source:
    source = db.scalar(select(Source).where(Source.name == name))
    if source is None:
        source = Source(name=name)
        db.add(source)
        db.flush()
    return source


def get_or_create_company(db: Session, source: Source, token: str) -> Company:
    company = db.scalar(
        select(Company).where(
            Company.source_id == source.id, Company.board_token == token
        )
    )
    if company is None:
        company = Company(source_id=source.id, board_token=token, name=token)
        db.add(company)
        db.flush()
    return company


def _new_offer(company_id: int, unified: UnifiedOffer) -> JobOffer:
    return JobOffer(company_id=company_id, **asdict(unified))


@dataclass
class ImportRunStats:
    new: int = 0
    updated: int = 0
    unchanged: int = 0


def import_company(
    db: Session,
    adapter: SourceAdapter,
    source: Source,
    company: Company,
    run: ImportRun,
) -> ImportRunStats:
    payloads = adapter.fetch(company.board_token)
    ids = [adapter.external_id(p) for p in payloads]

    existing = {
        raw.external_id: raw
        for raw in db.scalars(
            select(RawOffer).where(
                RawOffer.source_id == source.id, RawOffer.external_id.in_(ids)
            )
        )
    }
    counts = ImportRunStats()
    now = datetime.now(ZoneInfo("Europe/Warsaw"))
    for payload, ext_id in zip(payloads, ids, strict=True):
        content_hash = compute_hash(payload)
        raw = existing.get(ext_id)

        if raw is None:
            raw = RawOffer(
                source_id=source.id,
                company_id=company.id,
                external_id=ext_id,
                payload=payload,
                content_hash=content_hash,
                import_run_id=run.id,
            )
            raw.offer = _new_offer(company.id, adapter.to_unified(payload))
            db.add(raw)
            existing[ext_id] = raw
            counts.new += 1
        elif raw.content_hash != content_hash:
            raw.payload = payload
            raw.content_hash = content_hash
            raw.last_seen_at = now
            raw.import_run_id = run.id
            for field, value in asdict(adapter.to_unified(payload)).items():
                setattr(raw.offer, field, value)
            counts.updated += 1
        else:
            raw.last_seen_at = now
            raw.import_run_id = run.id
            counts.unchanged += 1
    return counts


def run_import(
    db: Session, adapter: SourceAdapter, board_tokens: list[str], pause: float = 0
) -> ImportRun:
    source = get_or_create_source(db, adapter.name)
    run = ImportRun(
        source_id=source.id,
        status="running",
        new_count=0,
        updated_count=0,
        unchanged_count=0,
    )
    db.add(run)
    db.commit()

    failures: list[str] = []
    for i, token in enumerate(board_tokens):
        if i and pause:
            time.sleep(pause)
        company = get_or_create_company(db, source, token)
        try:
            with db.begin_nested():
                counts = import_company(db, adapter, source, company, run)
        except Exception as e:
            log.exception(f"Import firmy {token} nie powiódł się")
            failures.append(f"{token}: {e!r}")
            continue

        run.new_count += counts.new
        run.updated_count += counts.updated
        run.unchanged_count += counts.unchanged
        db.commit()
    run.finished_at = datetime.now(ZoneInfo("Europe/Warsaw"))
    if not failures:
        run.status = "success"
    elif len(failures) == len(board_tokens):
        run.status = "failed"
    else:
        run.status = "partial"
    run.error = "\n".join(failures) or None
    db.commit()
    return run
