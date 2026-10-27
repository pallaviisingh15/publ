# Project Instructions for Claude Code

## Stack
- **Frontend**: Python (Streamlit / Gradio — TBD)
- **Backend**: Python (FastAPI)
- **Database**: PostgreSQL via SQLAlchemy + Alembic

## Project Layout
```
src/backend/   — FastAPI app, routes, services, DB layer
src/frontend/  — Python UI app
tests/         — pytest suites mirroring src/
config/        — YAML env configs loaded at startup
.sessions/     — filesystem session-persistence (see .rd conventions below)
.claude/       — Claude Code project settings and custom commands
```

## .rd Session-Persistence Convention
Session state is serialised to `.sessions/checkpoints/<session-id>.rd.json` at every
checkpoint and to `.sessions/snapshots/<session-id>_<timestamp>.rd.json` on flush.
The `.rd.json` suffix marks runtime-data files so tooling can distinguish them from
regular application JSON.

File schema: `{ "session_id": str, "created_at": ISO8601, "updated_at": ISO8601, "data": {} }`

## Commands
- `make dev`     — start frontend + backend in dev mode
- `make migrate` — run Alembic migrations
- `make test`    — run full pytest suite
- `make lint`    — ruff + mypy

## Coding Standards
- Python 3.11+, type-annotated throughout
- Pydantic v2 for all request/response models
- SQLAlchemy 2.x declarative models under `src/backend/db/models/`
- Alembic migrations under `src/backend/db/migrations/versions/`
- Environment variables loaded via `src/backend/core/config.py` (pydantic-settings)
- No business logic in route handlers — delegate to `services/`
- Tests use pytest-asyncio; fixtures in `tests/backend/conftest.py`

## Do Not
- Commit `.env` or `.sessions/` directories
- Add sync DB calls inside async route handlers
- Bypass Alembic for schema changes
