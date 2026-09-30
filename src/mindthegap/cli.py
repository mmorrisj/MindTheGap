"""`mindthegap scan requirements.txt` — score every dependency and print the riskiest first."""

import argparse
import re
import sys
from pathlib import Path

import httpx

from mindthegap import service
from mindthegap.config import get_settings
from mindthegap.db import SessionLocal, init_db

_REQ_NAME = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def parse_requirements(text: str) -> list[str]:
    names = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith(("-", "git+", "http")):
            continue  # skip options (-r, -e, --index-url) and direct URLs
        m = _REQ_NAME.match(line)
        if m:
            names.append(service.normalize(m.group(1)))
    return list(dict.fromkeys(names))


def scan(path: Path) -> int:
    init_db()
    names = parse_requirements(path.read_text())
    rows = []
    with SessionLocal() as session, httpx.Client(timeout=get_settings().http_timeout) as client:
        for name in names:
            try:
                pkg = service.refresh_package(session, name, client)
                rows.append((pkg.risk_score or 0, pkg.name, pkg.risk_factors))
            except httpx.HTTPError as exc:
                session.rollback()
                print(f"  ! {name}: {exc}", file=sys.stderr)
    rows.sort(reverse=True)
    print(f"{'risk':>5}  {'package':<30} fragility impact  missing")
    for risk, name, f in rows:
        print(f"{risk:>5.1f}  {name:<30} {f['fragility']:>9.2f} {f['impact']:>6.2f}  {','.join(f['missing']) or '-'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mindthegap")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_scan = sub.add_parser("scan", help="score dependencies from a requirements file")
    p_scan.add_argument("requirements", type=Path)
    args = parser.parse_args(argv)
    if args.cmd == "scan":
        return scan(args.requirements)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
