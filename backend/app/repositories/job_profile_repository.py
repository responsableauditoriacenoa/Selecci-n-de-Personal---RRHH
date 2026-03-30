from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job_profile import JobProfile


def list_job_profiles(db: Session) -> list[JobProfile]:
    return db.scalars(select(JobProfile).order_by(JobProfile.id.desc())).all()


def get_job_profile(db: Session, job_profile_id: int) -> JobProfile | None:
    return db.get(JobProfile, job_profile_id)
