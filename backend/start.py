import os
import subprocess
import sys
import time

import uvicorn
from sqlalchemy import create_engine, text


def _normalize_database_url(raw_url: str) -> str:
    return (
        raw_url.replace("postgres://", "postgresql+psycopg://", 1)
        .replace("postgresql://", "postgresql+psycopg://", 1)
    )


def _validate_required_env() -> None:
    missing = [name for name in ("DATABASE_URL", "SECRET_KEY") if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")


def _wait_for_database(url: str, attempts: int = 20, delay_seconds: int = 3) -> None:
    engine = create_engine(url, future=True, pool_pre_ping=True)
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print(f"[startup] Database reachable on attempt {attempt}/{attempts}")
            return
        except Exception as exc:  # pragma: no cover
            last_error = exc
            print(f"[startup] Database not ready ({attempt}/{attempts}): {exc}")
            time.sleep(delay_seconds)

    raise RuntimeError(f"Database never became reachable: {last_error}")


def _run_alembic() -> bool:
    result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=False)
    return result.returncode == 0


def _fallback_create_all() -> None:
    from app.core.database import Base, engine

    Base.metadata.create_all(bind=engine)


def _run_seed() -> None:
    from app.jobs.seed import run_seed

    run_seed()


def main() -> None:
    _validate_required_env()
    os.environ["DATABASE_URL"] = _normalize_database_url(os.environ["DATABASE_URL"])

    print("[startup] Waiting for database...")
    _wait_for_database(os.environ["DATABASE_URL"])

    print("[startup] Running database migrations...")
    migrated = _run_alembic()
    if not migrated:
        print("[startup] Alembic failed. Falling back to metadata create_all().")
        _fallback_create_all()

    print("[startup] Running seed job...")
    try:
        _run_seed()
    except Exception as exc:  # pragma: no cover
        print(f"[startup] Seed failed (continuing): {exc}")

    port = int(os.getenv("PORT", "8000"))
    print(f"[startup] Starting API on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()