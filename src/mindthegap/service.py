import logging
import re
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from mindthegap import scoring
from mindthegap.collectors import depsdev, github, pypi
from mindthegap.config import get_settings
from mindthegap.models import Package

log = logging.getLogger(__name__)


def normalize(name: str) -> str:
    """PEP 503 normalization so 'Foo_Bar' and 'foo-bar' are the same row."""
    return re.sub(r"[-_.]+", "-", name).lower()


def get_package(session: Session, name: str, ecosystem: str = "pypi") -> Package | None:
    return session.scalar(select(Package).where(Package.ecosystem == ecosystem, Package.name == normalize(name)))


def refresh_package(session: Session, name: str, client: httpx.Client) -> Package:
    """Collect all signals for a PyPI package, rescore it, and upsert. Partial failures are tolerated."""
    settings = get_settings()
    reg = pypi.fetch(client, name)  # the registry is required; let this raise

    pkg = get_package(session, name) or Package(ecosystem="pypi", name=normalize(name))
    session.add(pkg)
    pkg.summary = reg.summary
    pkg.latest_version = reg.latest_version
    pkg.last_release_at = reg.last_release_at
    pkg.release_count = reg.release_count
    pkg.repo_url = reg.repo_url

    errors: dict[str, str] = {}
    if reg.repo_url:
        try:
            gh = github.fetch(client, reg.repo_url, settings.github_token)
            pkg.last_commit_at = gh.last_commit_at
            pkg.archived = gh.archived
            pkg.open_issues = gh.open_issues
            pkg.contributor_count = gh.contributor_count
            pkg.top_contributor_share = gh.top_contributor_share
        except httpx.HTTPError as exc:
            log.warning("github collection failed for %s: %s", name, exc)
            errors["github"] = str(exc)

    if reg.latest_version:
        try:
            pkg.dependent_count = depsdev.fetch(client, pkg.name, reg.latest_version)
        except httpx.HTTPError as exc:
            log.warning("deps.dev collection failed for %s: %s", name, exc)
            errors["depsdev"] = str(exc)

    result = scoring.score(
        scoring.Signals(
            last_release_at=pkg.last_release_at,
            last_commit_at=pkg.last_commit_at,
            archived=pkg.archived,
            contributor_count=pkg.contributor_count,
            top_contributor_share=pkg.top_contributor_share,
            dependent_count=pkg.dependent_count,
        )
    )
    pkg.risk_score = result.score
    pkg.risk_factors = {**result.factors, "collection_errors": errors}
    pkg.refreshed_at = datetime.now(timezone.utc)
    session.commit()
    return pkg
