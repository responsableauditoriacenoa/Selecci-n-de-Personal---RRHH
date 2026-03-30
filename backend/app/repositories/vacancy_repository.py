from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.vacancy import Vacancy


def list_vacancies(db: Session) -> list[Vacancy]:
    return db.scalars(select(Vacancy).order_by(Vacancy.id.desc())).all()


def get_vacancy(db: Session, vacancy_id: int) -> Vacancy | None:
    return db.get(Vacancy, vacancy_id)


def get_by_token(db: Session, token: str) -> Vacancy | None:
    return db.scalar(select(Vacancy).where(Vacancy.qr_token == token))
