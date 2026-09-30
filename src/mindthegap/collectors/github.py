from dataclasses import dataclass
from datetime import datetime

import httpx

API = "https://api.github.com"


@dataclass
class GithubSignals:
    last_commit_at: datetime | None
    archived: bool
    open_issues: int
    contributor_count: int
    top_contributor_share: float | None


def _owner_repo(repo_url: str) -> str:
    return repo_url.rstrip("/").removeprefix("https://github.com/")


def parse(repo: dict, contributors: list[dict]) -> GithubSignals:
    counts = [c.get("contributions", 0) for c in contributors]
    total = sum(counts)
    return GithubSignals(
        # pushed_at covers any branch; a cheap proxy for "someone is still active here".
        last_commit_at=datetime.fromisoformat(repo["pushed_at"].replace("Z", "+00:00")) if repo.get("pushed_at") else None,
        archived=bool(repo.get("archived")),
        # GitHub's open_issues_count includes open PRs.
        open_issues=repo.get("open_issues_count", 0),
        contributor_count=len(counts),
        top_contributor_share=round(max(counts) / total, 3) if total else None,
    )


def fetch(client: httpx.Client, repo_url: str, token: str | None = None) -> GithubSignals:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    slug = _owner_repo(repo_url)
    repo = client.get(f"{API}/repos/{slug}", headers=headers)
    repo.raise_for_status()
    # First page only (top 100 by commits): enough to estimate concentration, bounded cost.
    contrib = client.get(f"{API}/repos/{slug}/contributors", params={"per_page": 100}, headers=headers)
    contrib.raise_for_status()
    # 204 No Content is returned for empty repos.
    return parse(repo.json(), contrib.json() if contrib.content else [])
