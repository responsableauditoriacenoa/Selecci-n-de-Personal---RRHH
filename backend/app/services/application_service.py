from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.application import Application, ApplicationAnswer
from app.models.candidate import Candidate
from app.repositories.vacancy_repository import get_by_token
from app.schemas.public import PublicApplicationCreate, PublicApplicationResult
from app.services.compatibility_service import generate_application_compatibility
from app.services.cv_parser import extract_text, save_upload_file
from app.services.scoring_service import recalculate_application_score


def _get_or_create_candidate(db: Session, payload: PublicApplicationCreate) -> Candidate:
    candidate = db.scalar(select(Candidate).where(Candidate.email == payload.email))
    if candidate:
        candidate.nombre = payload.nombre
        candidate.apellido = payload.apellido
        candidate.telefono = payload.telefono
        candidate.ciudad = payload.ciudad
        candidate.provincia = payload.provincia
        candidate.linkedin = payload.linkedin
        db.flush()
        return candidate

    candidate = Candidate(
        nombre=payload.nombre,
        apellido=payload.apellido,
        email=payload.email,
        telefono=payload.telefono,
        ciudad=payload.ciudad,
        provincia=payload.provincia,
        linkedin=payload.linkedin,
    )
    db.add(candidate)
    db.flush()
    return candidate


def _save_cv_and_extract_text(file: UploadFile) -> tuple[str, str]:
    settings = get_settings()
    cv_file_path = save_upload_file(settings.upload_dir, file)
    cv_text = extract_text(cv_file_path)
    return cv_file_path, cv_text


def _create_application_record(
    db: Session,
    vacancy_id: int,
    candidate_id: int,
    payload: PublicApplicationCreate,
    cv_file_path: str,
    cv_text: str,
) -> Application:
    application = Application(
        vacancy_id=vacancy_id,
        candidate_id=candidate_id,
        consentimiento_datos=payload.consentimiento_datos,
        cv_file_path=cv_file_path,
        cv_text_extracted=cv_text,
        fuente=payload.fuente,
    )
    db.add(application)
    db.flush()
    return application


def _save_answers(db: Session, application_id: int, payload: PublicApplicationCreate) -> None:
    for answer in payload.answers:
        db.add(
            ApplicationAnswer(
                application_id=application_id,
                job_question_id=answer.job_question_id,
                respuesta=answer.respuesta,
            )
        )
    db.flush()


def process_public_application(
    db: Session,
    payload: PublicApplicationCreate,
    file: UploadFile,
) -> PublicApplicationResult:
    vacancy = get_by_token(db, payload.token)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")

    candidate = _get_or_create_candidate(db, payload)
    cv_file_path, cv_text = _save_cv_and_extract_text(file)
    application = _create_application_record(db, vacancy.id, candidate.id, payload, cv_file_path, cv_text)
    _save_answers(db, application.id, payload)

    score = recalculate_application_score(db, application.id)
    insight = generate_application_compatibility(db, application.id, score.score_total)
    db.commit()

    _ = {
        "hallazgos": sum(
            len(items or [])
            for items in [
                insight.strengths_json,
                insight.weaknesses_json,
                insight.opportunities_json,
                insight.matches_json,
                insight.gaps_json,
            ]
        ),
        "conclusion": insight.analytical_conclusion,
    }

    return PublicApplicationResult(
        application_id=application.id,
        message="Postulacion enviada correctamente",
    )
