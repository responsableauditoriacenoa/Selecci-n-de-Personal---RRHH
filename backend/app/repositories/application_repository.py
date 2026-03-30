from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application import Application


def get_application(db: Session, application_id: int) -> Application | None:
    return db.get(Application, application_id)


def list_by_vacancy(db: Session, vacancy_id: int) -> list[Application]:
    return db.scalars(
        select(Application).where(Application.vacancy_id == vacancy_id, Application.is_deleted.is_(False)).order_by(Application.id.desc())
    ).all()
