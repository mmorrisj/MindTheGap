import os
import tempfile
from datetime import datetime, timedelta, timezone

# Must be set before mindthegap.db creates its engine.
os.environ["MTG_DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"
os.environ.pop("MTG_GITHUB_TOKEN", None)

import httpx  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from mindthegap.api import app, get_http_client  # noqa: E402
from mindthegap.db import Base, engine, init_db  # noqa: E402

NOW = datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S.000000Z")


def pypi_payload(name: str, last_release: datetime, repo: str | None = None) -> dict:
    return {
        "info": {
            "name": name,
            "summary": f"{name} does things",
            "version": "1.0.0",
            "project_urls": {"Source": repo} if repo else {},
            "home_page": None,
        },
        "releases": {
            "0.9.0": [{"upload_time_iso_8601": iso(last_release - timedelta(days=400)), "yanked": False}],
            "1.0.0": [{"upload_time_iso_8601": iso(last_release), "yanked": False}],
            "1.0.1": [{"upload_time_iso_8601": iso(NOW), "yanked": True}],
        },
    }


# name -> (pypi payload, github repo payload, contributors, dependents)
FIXTURES = {
    "stale-solo": (
        pypi_payload("stale-solo", NOW - timedelta(days=4 * 365), "https://github.com/alice/stale-solo"),
        {"pushed_at": iso(NOW - timedelta(days=3 * 365)), "archived": False, "open_issues_count": 80},
        [{"contributions": 500}, {"contributions": 5}],
        50_000,
    ),
    "healthy-team": (
        pypi_payload("healthy-team", NOW - timedelta(days=10), "https://github.com/org/healthy-team"),
        {"pushed_at": iso(NOW - timedelta(days=1)), "archived": False, "open_issues_count": 20},
        [{"contributions": 100}, {"contributions": 90}, {"contributions": 80}],
        50_000,
    ),
}


def handler(request: httpx.Request) -> httpx.Response:
    host, path = request.url.host, request.url.path
    for name, (pypi, repo, contribs, deps) in FIXTURES.items():
        if host == "pypi.org" and path == f"/pypi/{name}/json":
            return httpx.Response(200, json=pypi)
        if host == "api.github.com" and path.endswith(f"/{name}/contributors"):
            return httpx.Response(200, json=contribs)
        if host == "api.github.com" and path.endswith(f"/{name}"):
            return httpx.Response(200, json=repo)
        if host == "api.deps.dev" and f"/packages/{name}/" in path:
            return httpx.Response(200, json={"dependentCount": deps})
    return httpx.Response(404, json={})


@pytest.fixture
def http_client():
    with httpx.Client(transport=httpx.MockTransport(handler)) as c:
        yield c


@pytest.fixture
def client(http_client):
    Base.metadata.drop_all(engine)
    init_db()
    app.dependency_overrides[get_http_client] = lambda: http_client
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
