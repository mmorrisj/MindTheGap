# MindTheGap

Find **critical-but-fragile** open-source dependencies, and coordinate who steps in to help.

See [docs/GAPS.md](docs/GAPS.md) for the research behind this: five under-invested challenges and why this one was chosen first. [docs/KAGGLE.md](docs/KAGGLE.md) reviews open Kaggle competitions suited to one developer working with AI.

## What it does

1. **Collects** health signals per PyPI package:
   - PyPI: release history and repo link
   - GitHub: last push, archived flag, contributor concentration
   - deps.dev: number of dependents
2. **Scores** risk as `fragility × impact` with a transparent breakdown (`risk_factors`), including which signals were missing.
3. **Coordinates:** anyone can record a *claim* on a package (`watch`, `triage`, `comaintain`, `fund`). `GET /gaps` returns high-risk packages that **nobody has claimed yet**. That is the to-do list.

## Quickstart

```bash
pip install -e ".[dev]"            # add ",postgres" for psycopg
cp .env.example .env               # set MTG_GITHUB_TOKEN (60 req/h without it)
docker compose up -d db            # optional; defaults to SQLite if MTG_DATABASE_URL is unset

mindthegap scan requirements.txt   # CLI: rank your own dependencies
uvicorn mindthegap.api:app --reload  # API docs at http://localhost:8000/docs
pytest
```

## API

| Method | Path | Purpose |
|---|---|---|
| POST | `/packages/{name}/refresh` | Collect signals and rescore |
| GET | `/packages?min_risk=` | All tracked packages, riskiest first |
| GET | `/packages/{name}` | One package with its factors |
| GET | `/gaps?min_risk=40` | High-risk and unclaimed |
| GET/POST | `/packages/{name}/claims` | List or offer help |
| PATCH | `/claims/{id}` | Mark a claim `active` or `withdrawn` |

## Suggested next increments
1. Alembic migrations (the schema currently uses `create_all`).
2. A `signal_snapshots` table so trends are kept, not just the latest values.
3. Seed with the scientific Python stack (numpy/scipy/pandas and their transitive dependencies) and review the top 50 by hand to calibrate weights.
4. Background refresh plus ETag caching for the GitHub API.
5. pgvector embeddings of package summaries, to match people offering help to packages by domain.
