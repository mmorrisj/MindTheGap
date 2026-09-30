def test_refresh_scores_and_ranks(client):
    stale = client.post("/packages/stale-solo/refresh").json()
    healthy = client.post("/packages/healthy-team/refresh").json()
    assert stale["risk_score"] > 60 > healthy["risk_score"]
    assert stale["top_contributor_share"] == 0.99
    assert stale["risk_factors"]["collection_errors"] == {}

    ranked = [p["name"] for p in client.get("/packages").json()]
    assert ranked == ["stale-solo", "healthy-team"]


def test_refresh_is_idempotent_and_normalizes_names(client):
    client.post("/packages/stale-solo/refresh")
    client.post("/packages/Stale_Solo/refresh")
    assert len(client.get("/packages").json()) == 1


def test_unknown_package_404(client):
    assert client.post("/packages/nope/refresh").status_code == 404
    assert client.get("/packages/nope").status_code == 404


def test_claims_remove_package_from_gaps(client):
    client.post("/packages/stale-solo/refresh")
    client.post("/packages/healthy-team/refresh")
    assert [p["name"] for p in client.get("/gaps").json()] == ["stale-solo"]

    r = client.post("/packages/stale-solo/claims", json={"who": "mmorrisj", "kind": "triage"})
    assert r.status_code == 201
    assert client.get("/gaps").json() == []
    assert client.get("/packages/stale-solo").json()["active_claims"] == 1

    client.patch(f"/claims/{r.json()['id']}", json={"status": "withdrawn"})
    assert [p["name"] for p in client.get("/gaps").json()] == ["stale-solo"]


def test_claim_validation(client):
    client.post("/packages/stale-solo/refresh")
    assert client.post("/packages/stale-solo/claims", json={"who": "", "kind": "triage"}).status_code == 422
    assert client.post("/packages/stale-solo/claims", json={"who": "x", "kind": "vibes"}).status_code == 422
