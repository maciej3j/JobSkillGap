from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from job_skill_gap.db import Base


class Source(Base):
    __tablename__ = "sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = (UniqueConstraint("source_id", "board_token"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    board_token: Mapped[str] = mapped_column(String(200))
    name: Mapped[str] = mapped_column(String(300))


class ImportRun(Base):
    __tablename__ = "import_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="running")
    new_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_count: Mapped[int] = mapped_column(Integer, default=0)
    unchanged_count: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text)


class RawOffer(Base):
    __tablename__ = "raw_offers"
    __table_args__ = (UniqueConstraint("source_id", "external_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    external_id: Mapped[str] = mapped_column(String(100))
    payload: Mapped[dict] = mapped_column(JSONB)
    content_hash: Mapped[str] = mapped_column(String(64))

    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    import_run_id: Mapped[int] = mapped_column(ForeignKey("import_runs.id"))
    offer: Mapped["JobOffer"] = relationship(back_populates="raw", uselist=False)  # noqa: UP037


class JobOffer(Base):
    __tablename__ = "job_offers"
    id: Mapped[int] = mapped_column(primary_key=True)
    raw_offer_id: Mapped[int] = mapped_column(ForeignKey("raw_offers.id"), unique=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    title: Mapped[str] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(Text)
    department: Mapped[str | None] = mapped_column(Text)
    description_text: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text)
    updated_at_source: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    raw: Mapped[RawOffer] = relationship(back_populates="offer")
