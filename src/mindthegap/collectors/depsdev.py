from urllib.parse import quote

import httpx

# deps.dev dependents endpoint is in the v3alpha API and may change.
DEPENDENTS_URL = "https://api.deps.dev/v3alpha/systems/pypi/packages/{name}/versions/{version}:dependents"


def parse(payload: dict) -> int | None:
    value = payload.get("dependentCount")
    return int(value) if value is not None else None


def fetch(client: httpx.Client, name: str, version: str) -> int | None:
    resp = client.get(DEPENDENTS_URL.format(name=quote(name, safe=""), version=quote(version, safe="")))
    resp.raise_for_status()
    return parse(resp.json())
