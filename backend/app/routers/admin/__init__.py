from .applications import router as applications_router
from .auth import router as auth_router
from .job_profiles import router as job_profiles_router
from .org import router as org_router
from .reports import router as reports_router
from .vacancies import router as vacancies_router

__all__ = [
	"applications_router",
	"auth_router",
	"job_profiles_router",
	"org_router",
	"reports_router",
	"vacancies_router",
]
