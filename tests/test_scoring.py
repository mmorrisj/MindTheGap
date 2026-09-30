from datetime import datetime, timedelta, timezone

from mindthegap.scoring import Signals, score

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_fresh_team_project_is_low_risk():
    r = score(Signals(NOW, NOW, False, 20, 0.3, 10_000), now=NOW)
    assert r.fragility == 0
    assert r.score == 0


def test_stale_single_maintainer_high_impact_is_high_risk():
    old = NOW - timedelta(days=4 * 365)
    r = score(Signals(old, old, False, 1, 1.0, 100_000), now=NOW)
    assert r.score == 100.0


def test_impact_scales_risk():
    old = NOW - timedelta(days=4 * 365)
    niche = score(Signals(old, old, False, 1, 1.0, 3), now=NOW)
    popular = score(Signals(old, old, False, 1, 1.0, 50_000), now=NOW)
    assert 0 < niche.score < popular.score


def test_archived_forces_max_fragility():
    assert score(Signals(NOW, NOW, True, 20, 0.3, 0), now=NOW).fragility == 1.0


def test_missing_signals_are_reported_not_guessed_silently():
    r = score(Signals(last_release_at=NOW), now=NOW)
    assert set(r.factors["missing"]) == {"commit_staleness", "bus_factor", "dependent_count"}
    assert r.impact == 0.5


def test_naive_datetimes_treated_as_utc():
    naive = (NOW - timedelta(days=4 * 365)).replace(tzinfo=None)
    assert score(Signals(last_release_at=naive), now=NOW).factors["release_staleness"] == 1.0
