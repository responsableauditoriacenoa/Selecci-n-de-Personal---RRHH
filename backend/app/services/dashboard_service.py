from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.enums import ApplicationStatus, VacancyStatus
from app.models.vacancy import Vacancy


def get_dashboard_metrics(db: Session) -> dict[str, int]:
    total_vacancies = db.scalar(select(func.count()).select_from(Vacancy)) or 0
    open_vacancies = (
        db.scalar(select(func.count()).select_from(Vacancy).where(Vacancy.estado == VacancyStatus.ABIERTA)) or 0
    )
    total_applications = db.scalar(select(func.count()).select_from(Application)) or 0
    recommended_applications = (
        db.scalar(
            select(func.count()).select_from(Application).where(Application.estado.in_([ApplicationStatus.RECOMENDADO]))
        )
        or 0
    )

    return {
        "total_vacancies": total_vacancies,
        "open_vacancies": open_vacancies,
        "total_applications": total_applications,
        "recommended_applications": recommended_applications,
    }
