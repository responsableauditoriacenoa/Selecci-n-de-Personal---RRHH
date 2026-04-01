from pathlib import Path
import logging

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.routers.admin import applications, auth, job_profiles, org, reports, vacancies
from app.routers.public import applications_public, vacancy_public

logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(org.router, prefix="/org", tags=["organization"])
app.include_router(job_profiles.router, prefix="/job-profiles", tags=["job-profiles"])
app.include_router(vacancies.router, prefix="/vacancies", tags=["vacancies"])
app.include_router(applications.router, prefix="/applications", tags=["applications"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(vacancy_public.router, prefix="/public", tags=["public-vacancy"])
app.include_router(applications_public.router, prefix="/public", tags=["public-applications"])

PANEL_DIST_DIR = Path(__file__).resolve().parents[1] / "panel_dist"
PANEL_ASSETS_DIR = PANEL_DIST_DIR / "assets"

logger.info(f"Panel dist directory: {PANEL_DIST_DIR}")
logger.info(f"Panel dist exists: {PANEL_DIST_DIR.exists()}")

if PANEL_ASSETS_DIR.exists():
    app.mount("/panel/assets", StaticFiles(directory=PANEL_ASSETS_DIR), name="panel-assets")
else:
    logger.warning(f"Panel assets directory not found: {PANEL_ASSETS_DIR}")


@app.get("/panel", include_in_schema=False, response_model=None)
def panel_index() -> Response:
    panel_index_file = PANEL_DIST_DIR / "index.html"
    if not panel_index_file.exists():
        logger.error(f"Panel index.html not found at {panel_index_file}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Panel not built",
                "message": "panel_dist/index.html not found",
                "checked_path": str(panel_index_file),
            },
        )
    response = FileResponse(panel_index_file)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/panel/{full_path:path}", include_in_schema=False, response_model=None)
def panel_routes(full_path: str) -> Response:
    candidate = PANEL_DIST_DIR / full_path
    if candidate.is_file():
        return FileResponse(candidate)
    panel_index_file = PANEL_DIST_DIR / "index.html"
    if not panel_index_file.exists():
        logger.error(f"Panel index.html not found at {panel_index_file}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Panel not built",
                "message": "panel_dist/index.html not found",
                "checked_path": str(panel_index_file),
            },
        )
    response = FileResponse(panel_index_file)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/panel/")


@app.get("/api", include_in_schema=False)
def api_info() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "status": "ok",
        "health": "/health",
        "docs": "/docs",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
