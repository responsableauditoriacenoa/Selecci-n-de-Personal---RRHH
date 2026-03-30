#!/usr/bin/env sh
set -e

# Run schema migrations before serving API.
alembic upgrade head

# Seed is idempotent; ensures admin user and demo reference data exist.
python -m app.jobs.seed

exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
