from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.application import Application, ApplicationAnswer
from app.models.audit import CandidateNote
from app.models.candidate import Candidate
from app.models.scoring import ApplicationScore, ScoreReason
from app.models.application import ApplicationInsight
from app.models.user import User
from app.schemas.application import (
    ApplicationAnswerRead,
    ApplicationRead,
    ApplicationInsightRead,
    ApplicationScoreRead,
    CandidateNoteCreate,
    CandidateNoteRead,
    CandidateRead,
    ChangeApplicationStatusRequest,
    ScoreReasonRead,
)
from app.services.audit_service import log_action
from app.services.scoring_service import recalculate_application_score

router = APIRouter()


@router.get("/{application_id}/cv")
def get_application_cv(
    application_id: int,
    disposition: str = Query("inline", pattern="^(inline|attachment)$"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> FileResponse:
    entity = db.get(Application, application_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Postulacion no encontrada")

    file_path = Path(entity.cv_file_path)
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path

    file_path = file_path.resolve()
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="CV no encontrado")

    media_type = "application/octet-stream"
    if file_path.suffix.lower() == ".pdf":
        media_type = "application/pdf"
    elif file_path.suffix.lower() == ".docx":
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    response = FileResponse(path=str(file_path), media_type=media_type, filename=file_path.name)
    if disposition == "inline":
        response.headers["Content-Disposition"] = f'inline; filename="{file_path.name}"'
    return response


@router.get("/{application_id}", response_model=ApplicationRead)
def detail_route(application_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> ApplicationRead:
    entity = db.get(Application, application_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Postulacion no encontrada")

    candidate = db.get(Candidate, entity.candidate_id)
    answers = db.scalars(select(ApplicationAnswer).where(ApplicationAnswer.application_id == entity.id)).all()

    score = db.scalar(select(ApplicationScore).where(ApplicationScore.application_id == entity.id))
    score_data = None
    if score:
        reasons = db.scalars(select(ScoreReason).where(ScoreReason.application_score_id == score.id)).all()
        score_data = ApplicationScoreRead(
            id=score.id,
            score_total=score.score_total,
            score_formacion=score.score_formacion,
            score_experiencia=score.score_experiencia,
            score_tecnico=score.score_tecnico,
            score_preguntas=score.score_preguntas,
            score_competencias=score.score_competencias,
            clasificacion=score.clasificacion,
            resumen_analisis=score.resumen_analisis,
            fecha_calculo=score.fecha_calculo,
            reasons=[
                ScoreReasonRead(id=r.id, tipo=r.tipo, descripcion=r.descripcion, impacto=r.impacto)
                for r in reasons
            ],
        )

    insight = db.scalar(select(ApplicationInsight).where(ApplicationInsight.application_id == entity.id))
    insight_data = None
    if insight:
        insight_data = ApplicationInsightRead(
            application_id=insight.application_id,
            fortalezas_detectadas=insight.strengths_json or [],
            debilidades_detectadas=insight.weaknesses_json or [],
            oportunidades_detectadas=insight.opportunities_json or [],
            coincidencias_clave=insight.matches_json or [],
            faltantes_relevantes=insight.gaps_json or [],
            conclusion_analitica=insight.analytical_conclusion,
            generated_at=insight.generated_at,
        )

    return ApplicationRead(
        id=entity.id,
        vacancy_id=entity.vacancy_id,
        candidate_id=entity.candidate_id,
        fecha_postulacion=entity.fecha_postulacion,
        estado=entity.estado,
        consentimiento_datos=entity.consentimiento_datos,
        cv_file_path=entity.cv_file_path,
        cv_text_extracted=entity.cv_text_extracted,
        fuente=entity.fuente,
        candidate=CandidateRead(
            id=candidate.id,
            nombre=candidate.nombre,
            apellido=candidate.apellido,
            email=candidate.email,
            telefono=candidate.telefono,
            ciudad=candidate.ciudad,
            provincia=candidate.provincia,
            linkedin=candidate.linkedin,
        ),
        answers=[ApplicationAnswerRead(id=a.id, job_question_id=a.job_question_id, respuesta=a.respuesta) for a in answers],
        score=score_data,
        insight=insight_data,
    )


@router.post("/{application_id}/recalculate-score")
def recalculate_route(
    application_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    try:
        score = recalculate_application_score(db, application_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    log_action(db, user, "application", application_id, "recalculate_score", {"score_total": score.score_total})
    db.commit()
    return {"application_id": application_id, "score_total": score.score_total, "clasificacion": score.clasificacion}


@router.post("/{application_id}/change-status")
def change_status_route(
    application_id: int,
    payload: ChangeApplicationStatusRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    entity = db.get(Application, application_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Postulacion no encontrada")

    previous = entity.estado
    entity.estado = payload.estado

    log_action(
        db,
        user,
        "application",
        application_id,
        "change_status",
        {"from": previous, "to": payload.estado},
    )
    db.commit()
    return {"application_id": application_id, "estado": entity.estado}


@router.post("/{application_id}/notes", response_model=CandidateNoteRead)
def add_note_route(
    application_id: int,
    payload: CandidateNoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CandidateNote:
    if not db.get(Application, application_id):
        raise HTTPException(status_code=404, detail="Postulacion no encontrada")

    note = CandidateNote(application_id=application_id, user_id=user.id, comentario=payload.comentario)
    db.add(note)
    log_action(db, user, "application", application_id, "add_note", payload.model_dump())
    db.commit()
    db.refresh(note)
    return note
