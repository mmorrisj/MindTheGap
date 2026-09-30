from collections.abc import Iterator
from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from mindthegap import service
from mindthegap.config import get_settings
from mindthegap.db import get_session, init_db
from mindthegap.models import Claim, ClaimStatus, Package
from mindthegap.schemas import ClaimIn, ClaimOut, ClaimStatusIn, PackageOut

LIVE = (ClaimStatus.offered, ClaimStatus.active)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="MindTheGap", version="0.1.0", lifespan=lifespan)


def get_http_client() -> Iterator[httpx.Client]:
    with httpx.Client(timeout=get_settings().http_timeout, headers={"User-Agent": "mindthegap/0.1"}) as client:
        yield client


def _out(pkg: Package) -> PackageOut:
    out = PackageOut.model_validate(pkg)
    out.active_claims = sum(1 for c in pkg.claims if c.status in LIVE)
    return out


def _require(session: Session, name: str) -> Package:
    pkg = service.get_package(session, name)
    if pkg is None:
        raise HTTPException(404, f"{name!r} not tracked yet; POST /packages/{name}/refresh first")
    return pkg


@app.post("/packages/{name}/refresh", response_model=PackageOut)
def refresh(name: str, session: Session = Depends(get_session), client: httpx.Client = Depends(get_http_client)):
    try:
        pkg = service.refresh_package(session, name, client)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(404, f"{name!r} not found on PyPI") from exc
        raise HTTPException(502, f"PyPI error: {exc}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"PyPI unreachable: {exc}") from exc
    return _out(pkg)


@app.get("/packages", response_model=list[PackageOut])
def list_packages(
    min_risk: float = Query(0, ge=0, le=100),
    limit: int = Query(50, ge=1, le=500),
    session: Session = Depends(get_session),
):
    stmt = (
        select(Package)
        .where(func.coalesce(Package.risk_score, 0) >= min_risk)
        .order_by(Package.risk_score.desc().nulls_last())
        .limit(limit)
    )
    return [_out(p) for p in session.scalars(stmt)]


@app.get("/gaps", response_model=list[PackageOut])
def gaps(
    min_risk: float = Query(40, ge=0, le=100),
    limit: int = Query(50, ge=1, le=500),
    session: Session = Depends(get_session),
):
    """High-risk packages with no live claim: the coordination to-do list."""
    has_live_claim = select(Claim.id).where(Claim.package_id == Package.id, Claim.status.in_(LIVE)).exists()
    stmt = (
        select(Package)
        .where(Package.risk_score >= min_risk, ~has_live_claim)
        .order_by(Package.risk_score.desc())
        .limit(limit)
    )
    return [_out(p) for p in session.scalars(stmt)]


@app.get("/packages/{name}", response_model=PackageOut)
def get_package(name: str, session: Session = Depends(get_session)):
    return _out(_require(session, name))


@app.get("/packages/{name}/claims", response_model=list[ClaimOut])
def list_claims(name: str, session: Session = Depends(get_session)):
    return _require(session, name).claims


@app.post("/packages/{name}/claims", response_model=ClaimOut, status_code=201)
def create_claim(name: str, body: ClaimIn, session: Session = Depends(get_session)):
    pkg = _require(session, name)
    claim = Claim(package=pkg, **body.model_dump())
    session.add(claim)
    session.commit()
    return claim


@app.patch("/claims/{claim_id}", response_model=ClaimOut)
def update_claim(claim_id: int, body: ClaimStatusIn, session: Session = Depends(get_session)):
    claim = session.get(Claim, claim_id)
    if claim is None:
        raise HTTPException(404, "claim not found")
    claim.status = body.status
    session.commit()
    return claim
