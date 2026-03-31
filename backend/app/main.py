from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers.admin import applications, auth, job_profiles, org, reports, vacancies
from app.routers.public import applications_public, vacancy_public

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


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "status": "ok",
        "health": "/health",
        "docs": "/docs",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
