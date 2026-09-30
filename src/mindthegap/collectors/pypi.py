import re
from dataclasses import dataclass
from datetime import datetime

import httpx

PYPI_URL = "https://pypi.org/pypi/{name}/json"
_GITHUB_RE = re.compile(r"https?://(?:www\.)?github\.com/([\w.-]+)/([\w.-]+?)(?:\.git)?(?:[/#?].*)?$")


@dataclass
class PypiSignals:
    name: str
    summary: str | None
    latest_version: str | None
    last_release_at: datetime | None
    release_count: int
    repo_url: str | None


def find_github_repo(urls: list[str]) -> str | None:
    """Return a canonical https://github.com/owner/repo URL from a list of candidate links."""
    for url in urls:
        m = _GITHUB_RE.match(url.strip()) if url else None
        if m and m.group(1).lower() not in {"sponsors", "orgs"}:
            return f"https://github.com/{m.group(1)}/{m.group(2)}"
    return None


def parse(payload: dict) -> PypiSignals:
    info = payload["info"]
    upload_times = [
        datetime.fromisoformat(f["upload_time_iso_8601"].replace("Z", "+00:00"))
        for files in payload.get("releases", {}).values()
        for f in files
        if not f.get("yanked")
    ]
    project_urls = info.get("project_urls") or {}
    # Prefer explicit source-code links over homepage/docs links.
    ordered = sorted(project_urls.items(), key=lambda kv: kv[0].lower() not in {"source", "source code", "repository", "code"})
    candidates = [u for _, u in ordered] + [info.get("home_page") or ""]
    return PypiSignals(
        name=info["name"],
        summary=info.get("summary"),
        latest_version=info.get("version"),
        last_release_at=max(upload_times) if upload_times else None,
        release_count=sum(1 for files in payload.get("releases", {}).values() if files),
        repo_url=find_github_repo(candidates),
    )


def fetch(client: httpx.Client, name: str) -> PypiSignals:
    resp = client.get(PYPI_URL.format(name=name))
    resp.raise_for_status()
    return parse(resp.json())
