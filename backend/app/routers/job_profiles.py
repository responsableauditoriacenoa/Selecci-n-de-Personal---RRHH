from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.job_profile import JobProfile, JobQuestion, JobRequirement
from app.models.user import User
from app.repositories.job_profile_repository import get_job_profile, list_job_profiles
from app.schemas.job_profile import JobProfileCreate, JobProfileDocumentAnalysisRead, JobProfileRead, JobProfileUpdate
from app.services.audit_service import log_action
from app.services.job_profile_analysis_service import analyze_document_against_job_profile

router = APIRouter()


@router.get("", response_model=list[JobProfileRead])
def list_route(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[JobProfile]:
    return list_job_profiles(db)


@router.post("", response_model=JobProfileRead)
def create_route(payload: JobProfileCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> JobProfile:
    entity = JobProfile(
        nombre_puesto=payload.nombre_puesto,
        area_id=payload.area_id,
        seniority=payload.seniority,
        modalidad=payload.modalidad,
        ubicacion=payload.ubicacion,
        descripcion_general=payload.descripcion_general,
        version=payload.version,
        estado=payload.estado,
        created_by=user.id,
    )
    db.add(entity)
    db.flush()

    for req in payload.requirements:
        db.add(JobRequirement(job_profile_id=entity.id, **req.model_dump()))

    for q in payload.questions:
        db.add(JobQuestion(job_profile_id=entity.id, **q.model_dump()))

    log_action(db, user, "job_profile", entity.id, "create", payload.model_dump())
    db.commit()
    db.refresh(entity)
    return entity


@router.get("/{job_profile_id}", response_model=JobProfileRead)
def detail_route(job_profile_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> JobProfile:
    entity = get_job_profile(db, job_profile_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Descriptivo no encontrado")
    return entity


@router.put("/{job_profile_id}", response_model=JobProfileRead)
def update_route(
    job_profile_id: int,
    payload: JobProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> JobProfile:
    entity = get_job_profile(db, job_profile_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Descriptivo no encontrado")

    for field, value in payload.model_dump(exclude={"requirements", "questions"}).items():
        setattr(entity, field, value)

    entity.version += 1

    db.query(JobRequirement).filter(JobRequirement.job_profile_id == job_profile_id).delete()
    db.query(JobQuestion).filter(JobQuestion.job_profile_id == job_profile_id).delete()

    for req in payload.requirements:
        db.add(JobRequirement(job_profile_id=entity.id, **req.model_dump()))

    for q in payload.questions:
        db.add(JobQuestion(job_profile_id=entity.id, **q.model_dump()))

    log_action(db, user, "job_profile", entity.id, "update", payload.model_dump())
    db.commit()
    db.refresh(entity)
    return entity


@router.post("/{job_profile_id}/analyze-document", response_model=JobProfileDocumentAnalysisRead)
def analyze_document_route(
    job_profile_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> JobProfileDocumentAnalysisRead:
    entity = get_job_profile(db, job_profile_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Descriptivo no encontrado")

    settings = get_settings()
    analysis = analyze_document_against_job_profile(entity, file, settings.upload_dir)

    log_action(
        db,
        user,
        "job_profile",
        entity.id,
        "analyze_document",
        {
            "file_name": file.filename,
            "score_compatibilidad": analysis["score_compatibilidad"],
            "clasificacion": analysis["clasificacion"],
        },
    )
    db.commit()

    return JobProfileDocumentAnalysisRead(
        job_profile_id=entity.id,
        file_name=file.filename or "documento",
        score_compatibilidad=analysis["score_compatibilidad"],
        clasificacion=analysis["clasificacion"],
        comentario_analisis=analysis["comentario_analisis"],
        coincidencias_clave=analysis["coincidencias_clave"],
        alertas=analysis["alertas"],
    )
