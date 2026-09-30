import enum
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mindthegap.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Package(Base):
    """Latest collected health signals for one package, plus its computed risk."""

    __tablename__ = "packages"
    __table_args__ = (UniqueConstraint("ecosystem", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    ecosystem: Mapped[str] = mapped_column(String(32), default="pypi")
    name: Mapped[str] = mapped_column(String(255), index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    repo_url: Mapped[str | None] = mapped_column(String(512))

    # Registry signals
    latest_version: Mapped[str | None] = mapped_column(String(64))
    last_release_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    release_count: Mapped[int | None] = mapped_column(Integer)

    # Repository signals
    last_commit_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    archived: Mapped[bool | None]
    open_issues: Mapped[int | None] = mapped_column(Integer)
    contributor_count: Mapped[int | None] = mapped_column(Integer)
    top_contributor_share: Mapped[float | None] = mapped_column(Float)

    # Impact signals
    dependent_count: Mapped[int | None] = mapped_column(Integer)

    risk_score: Mapped[float | None] = mapped_column(Float, index=True)
    risk_factors: Mapped[dict] = mapped_column(JSON, default=dict)
    refreshed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    claims: Mapped[list["Claim"]] = relationship(back_populates="package", cascade="all, delete-orphan")


class ClaimKind(str, enum.Enum):
    watch = "watch"  # I'll keep an eye on it and flag problems
    triage = "triage"  # I'll help triage issues / review PRs
    comaintain = "comaintain"  # I'm willing to become a co-maintainer
    fund = "fund"  # I (or my org) can put money toward it


class ClaimStatus(str, enum.Enum):
    offered = "offered"
    active = "active"
    withdrawn = "withdrawn"


class Claim(Base):
    """A person/org publicly committing some kind of help to a package: the coordination layer."""

    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(primary_key=True)
    package_id: Mapped[int] = mapped_column(ForeignKey("packages.id", ondelete="CASCADE"), index=True)
    who: Mapped[str] = mapped_column(String(255))
    kind: Mapped[ClaimKind] = mapped_column(Enum(ClaimKind, native_enum=False))
    status: Mapped[ClaimStatus] = mapped_column(Enum(ClaimStatus, native_enum=False), default=ClaimStatus.offered)
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    package: Mapped[Package] = relationship(back_populates="claims")
