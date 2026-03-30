import os
import subprocess

import uvicorn


def _run_alembic() -> bool:
    result = subprocess.run(["python", "-m", "alembic", "upgrade", "head"], check=False)
    return result.returncode == 0


def _fallback_create_all() -> None:
    from app.core.database import Base, engine

    Base.metadata.create_all(bind=engine)


def _run_seed() -> None:
    from app.jobs.seed import run_seed

    run_seed()


def main() -> None:
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