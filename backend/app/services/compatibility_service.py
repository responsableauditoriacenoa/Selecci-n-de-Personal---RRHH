from sqlalchemy.orm import Session

from app.models.application import ApplicationInsight
from app.services.comparative_analysis_service import generate_or_update_application_insight


def generate_application_compatibility(
    db: Session,
    application_id: int,
    score_total: int,
) -> ApplicationInsight:
    return generate_or_update_application_insight(db, application_id, score_total)
