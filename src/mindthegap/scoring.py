"""Transparent, deliberately simple risk heuristic.

risk = fragility x impact. Fragility asks "how likely is this to go unmaintained?";
impact asks "how many people get hurt if it does?". Every input and its contribution
is returned so the score can be argued with, not just trusted. Weights and thresholds
are uncalibrated first guesses: tune them against known incidents before relying on them.
"""

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone

FRESH_DAYS = 180  # at or under this, staleness contributes nothing
STALE_DAYS = 3 * 365  # at or over this, staleness is maxed out
IMPACT_SATURATION = 100_000  # dependents count at which impact reaches 1.0

WEIGHTS = {"release_staleness": 1.0, "commit_staleness": 1.5, "bus_factor": 2.0}


@dataclass
class Signals:
    last_release_at: datetime | None = None
    last_commit_at: datetime | None = None
    archived: bool | None = None
    contributor_count: int | None = None
    top_contributor_share: float | None = None
    dependent_count: int | None = None


@dataclass
class RiskResult:
    score: float
    fragility: float
    impact: float
    factors: dict = field(default_factory=dict)


def _staleness(ts: datetime | None, now: datetime) -> float | None:
    if ts is None:
        return None
    if ts.tzinfo is None:  # SQLite drops tzinfo; values are stored as UTC
        ts = ts.replace(tzinfo=timezone.utc)
    days = (now - ts).days
    return min(1.0, max(0.0, (days - FRESH_DAYS) / (STALE_DAYS - FRESH_DAYS)))


def _bus_factor(count: int | None, top_share: float | None) -> float | None:
    if count is None and top_share is None:
        return None
    if count is not None and count <= 1:
        return 1.0
    # 50% of commits from one person is normal-ish; 95%+ is effectively a single maintainer.
    return min(1.0, max(0.0, ((top_share or 0.0) - 0.5) / 0.45))


def score(s: Signals, now: datetime | None = None) -> RiskResult:
    now = now or datetime.now(timezone.utc)
    components = {
        "release_staleness": _staleness(s.last_release_at, now),
        "commit_staleness": _staleness(s.last_commit_at, now),
        "bus_factor": _bus_factor(s.contributor_count, s.top_contributor_share),
    }
    known = {k: v for k, v in components.items() if v is not None}
    if s.archived:
        fragility = 1.0
    elif known:
        fragility = sum(WEIGHTS[k] * v for k, v in known.items()) / sum(WEIGHTS[k] for k in known)
    else:
        fragility = 0.5  # no evidence either way

    if s.dependent_count is None:
        impact = 0.5
    else:
        impact = min(1.0, math.log10(s.dependent_count + 1) / math.log10(IMPACT_SATURATION))

    # Floor on impact so a fragile niche package still registers, just lower.
    risk = 100 * fragility * (0.25 + 0.75 * impact)
    factors = {
        **{k: (round(v, 3) if v is not None else None) for k, v in components.items()},
        "archived": s.archived,
        "fragility": round(fragility, 3),
        "impact": round(impact, 3),
        "missing": sorted([k for k, v in components.items() if v is None] + (["dependent_count"] if s.dependent_count is None else [])),
    }
    return RiskResult(score=round(risk, 1), fragility=fragility, impact=impact, factors=factors)
