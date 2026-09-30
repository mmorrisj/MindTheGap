from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from mindthegap.models import ClaimKind, ClaimStatus


class ClaimIn(BaseModel):
    who: str = Field(min_length=1, max_length=255, description="Name, handle, or org")
    kind: ClaimKind
    note: str | None = Field(default=None, max_length=2000)


class ClaimOut(ClaimIn):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: ClaimStatus
    created_at: datetime


class ClaimStatusIn(BaseModel):
    status: ClaimStatus


class PackageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ecosystem: str
    name: str
    summary: str | None
    repo_url: str | None
    latest_version: str | None
    last_release_at: datetime | None
    release_count: int | None
    last_commit_at: datetime | None
    archived: bool | None
    open_issues: int | None
    contributor_count: int | None
    top_contributor_share: float | None
    dependent_count: int | None
    risk_score: float | None
    risk_factors: dict
    refreshed_at: datetime | None
    active_claims: int = 0

