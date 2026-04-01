from pathlib import Path
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.candidate import Candidate
from app.models.enums import JobProfileStatus
from app.models.job_profile import JobProfile
from app.models.organization import Area, Branch, Company
from app.models.user import User
from app.models.vacancy import Vacancy
from app.repositories.application_repository import list_by_vacancy
from app.repositories.vacancy_repository import get_vacancy, list_vacancies
from app.schemas.application import ApplicationRead, CandidateRead
from app.schemas.vacancy import VacancyCreate, VacancyCreateResponse, VacancyQRRead, VacancyRead, VacancyUpdate
from app.services.audit_service import log_action
from app.services.cv_parser import extract_text, save_upload_file
from app.services.qr_service import build_public_url, generate_qr_base64, generate_qr_token

router = APIRouter()
logger = logging.getLogger(__name__)


def _resolve_dependencies(
    db: Session,
    user: User,
    *,
    job_profile_id: int,
    company_id: int,
    branch_id: int,
    area_id: int,
    empresa: str,
    localidad: str,
    area_name: str,
    titulo_publicacion: str,
) -> tuple[int, int, int, int]:
    company = db.get(Company, company_id)
    company_name = (empresa or "").strip() or "Empresa General"
    if not company:
        company = db.scalar(select(Company).where(Company.name == company_name))
    if not company:
        company = Company(name=company_name)
        db.add(company)
        db.flush()

    branch = db.get(Branch, branch_id)
    branch_name = (localidad or "").strip() or "Casa Central"
    if not branch or branch.company_id != company.id:
        branch = db.scalar(select(Branch).where(Branch.company_id == company.id, Branch.name == branch_name))
    if not branch:
        branch = Branch(company_id=company.id, name=branch_name)
        db.add(branch)
        db.flush()

    area_entity = db.get(Area, area_id)
    normalized_area_name = (area_name or "").strip() or "General"
    if not area_entity:
        area_entity = db.scalar(select(Area).where(Area.name == normalized_area_name))
    if not area_entity:
        area_entity = Area(name=normalized_area_name)
        db.add(area_entity)
        db.flush()

    profile = db.get(JobProfile, job_profile_id)
    if not profile:
        profile = db.scalar(select(JobProfile).order_by(JobProfile.id.asc()))
    if not profile:
        profile = JobProfile(
            nombre_puesto=titulo_publicacion.strip() or "Perfil General",
            area_id=area_entity.id,
            seniority="No definido",
            modalidad="Presencial",
            ubicacion=branch_name,
            descripcion_general="Perfil generado automaticamente para permitir la carga de vacantes.",
            version=1,
            estado=JobProfileStatus.ACTIVO,
            created_by=user.id,
        )
        db.add(profile)
        db.flush()

    return profile.id, company.id, branch.id, area_entity.id


def _serialize_vacancy(entity: Vacancy) -> VacancyRead:
    return VacancyRead(
        id=entity.id,
        job_profile_id=entity.job_profile_id,
        company_id=entity.company_id,
        branch_id=entity.branch_id,
        area_id=entity.area_id,
        empresa=entity.empresa or "",
        localidad=entity.localidad or "",
        area=entity.area or "",
        titulo_publicacion=entity.titulo_publicacion,
        descripcion_publicacion=entity.descripcion_publicacion,
        descriptivo_puesto=entity.descriptivo_puesto,
        fecha_apertura=entity.fecha_apertura,
        fecha_cierre=entity.fecha_cierre,
        estado=entity.estado,
        qr_token=entity.qr_token,
        public_url=entity.public_url,
        descriptivo_archivo_nombre=entity.descriptivo_archivo_nombre,
        descriptivo_documento_cargado=bool(entity.descriptivo_archivo_path),
    )


@router.get("", response_model=list[VacancyRead])
def list_route(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[Vacancy]:
    return [_serialize_vacancy(item) for item in list_vacancies(db)]


@router.post("", response_model=VacancyCreateResponse)
def create_route(
    job_profile_id: int = Form(1),
    company_id: int = Form(1),
    branch_id: int = Form(1),
    area_id: int = Form(1),
    empresa: str = Form(""),
    localidad: str = Form(""),
    area: str = Form(""),
    titulo_publicacion: str = Form(...),
    descripcion_publicacion: str = Form(""),
    descriptivo_puesto: str = Form(""),
    fecha_apertura: str = Form(...),
    fecha_cierre: str = Form(...),
    estado: str = Form(...),
    descriptivo_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> VacancyCreateResponse:
    try:
        resolved_job_profile_id, resolved_company_id, resolved_branch_id, resolved_area_id = _resolve_dependencies(
            db,
            user,
            job_profile_id=job_profile_id,
            company_id=company_id,
            branch_id=branch_id,
            area_id=area_id,
            empresa=empresa,
            localidad=localidad,
            area_name=area,
            titulo_publicacion=titulo_publicacion,
        )

        payload = VacancyCreate(
            job_profile_id=resolved_job_profile_id,
            company_id=resolved_company_id,
            branch_id=resolved_branch_id,
            area_id=resolved_area_id,
            empresa=empresa,
            localidad=localidad,
            area=area,
            titulo_publicacion=titulo_publicacion,
            descripcion_publicacion=descripcion_publicacion,
            descriptivo_puesto=descriptivo_puesto,
            fecha_apertura=fecha_apertura,
            fecha_cierre=fecha_cierre,
            estado=estado,
        )
        token = generate_qr_token()
        entity = Vacancy(**payload.model_dump(), qr_token=token, public_url=build_public_url(token))

        if descriptivo_file is not None:
            settings = get_settings()
            file_path = save_upload_file(settings.upload_dir, descriptivo_file)
            entity.descriptivo_archivo_nombre = descriptivo_file.filename
            entity.descriptivo_archivo_path = file_path
            try:
                entity.descriptivo_texto_extraido = extract_text(file_path)
            except HTTPException as exc:
                logger.warning("No se pudo extraer texto de descriptivo '%s': %s", descriptivo_file.filename, exc.detail)
                entity.descriptivo_texto_extraido = ""

        db.add(entity)
        db.flush()
        log_action(db, user, "vacancy", entity.id, "create", payload.model_dump())
        db.commit()
        db.refresh(entity)
        return VacancyCreateResponse(
            **_serialize_vacancy(entity).model_dump(),
            qr_base64_png=generate_qr_base64(entity.public_url),
        )
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Error SQL al crear vacante")
        raise HTTPException(status_code=400, detail=f"Error al guardar en base de datos: {str(exc)}")
    except Exception as exc:
        db.rollback()
        logger.exception("Error inesperado al crear vacante")
        raise HTTPException(status_code=500, detail=f"Error inesperado al crear vacante: {str(exc)}")


@router.get("/{vacancy_id}", response_model=VacancyRead)
def detail_route(vacancy_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> Vacancy:
    entity = get_vacancy(db, vacancy_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")
    return _serialize_vacancy(entity)


@router.put("/{vacancy_id}", response_model=VacancyRead)
def update_route(
    vacancy_id: int,
    job_profile_id: int = Form(1),
    company_id: int = Form(1),
    branch_id: int = Form(1),
    area_id: int = Form(1),
    empresa: str = Form(""),
    localidad: str = Form(""),
    area: str = Form(""),
    titulo_publicacion: str = Form(...),
    descripcion_publicacion: str = Form(""),
    descriptivo_puesto: str = Form(""),
    fecha_apertura: str = Form(...),
    fecha_cierre: str = Form(...),
    estado: str = Form(...),
    descriptivo_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Vacancy:
    try:
        resolved_job_profile_id, resolved_company_id, resolved_branch_id, resolved_area_id = _resolve_dependencies(
            db,
            user,
            job_profile_id=job_profile_id,
            company_id=company_id,
            branch_id=branch_id,
            area_id=area_id,
            empresa=empresa,
            localidad=localidad,
            area_name=area,
            titulo_publicacion=titulo_publicacion,
        )

        payload = VacancyUpdate(
            job_profile_id=resolved_job_profile_id,
            company_id=resolved_company_id,
            branch_id=resolved_branch_id,
            area_id=resolved_area_id,
            empresa=empresa,
            localidad=localidad,
            area=area,
            titulo_publicacion=titulo_publicacion,
            descripcion_publicacion=descripcion_publicacion,
            descriptivo_puesto=descriptivo_puesto,
            fecha_apertura=fecha_apertura,
            fecha_cierre=fecha_cierre,
            estado=estado,
        )
        entity = get_vacancy(db, vacancy_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Vacante no encontrada")

        for field, value in payload.model_dump().items():
            setattr(entity, field, value)

        if descriptivo_file is not None:
            settings = get_settings()
            file_path = save_upload_file(settings.upload_dir, descriptivo_file)
            entity.descriptivo_archivo_nombre = descriptivo_file.filename
            entity.descriptivo_archivo_path = file_path
            try:
                entity.descriptivo_texto_extraido = extract_text(file_path)
            except HTTPException as exc:
                logger.warning("No se pudo extraer texto de descriptivo '%s': %s", descriptivo_file.filename, exc.detail)
                entity.descriptivo_texto_extraido = ""

        log_action(db, user, "vacancy", entity.id, "update", payload.model_dump())
        db.commit()
        db.refresh(entity)
        return _serialize_vacancy(entity)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Error SQL al actualizar vacante")
        raise HTTPException(status_code=400, detail=f"Error al actualizar en base de datos: {str(exc)}")


@router.get("/{vacancy_id}/applications", response_model=list[ApplicationRead])
def applications_route(vacancy_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[ApplicationRead]:
    applications = list_by_vacancy(db, vacancy_id)
    result = []
    for app in applications:
        candidate = db.get(Candidate, app.candidate_id)
        result.append(
            ApplicationRead(
                id=app.id,
                vacancy_id=app.vacancy_id,
                candidate_id=app.candidate_id,
                fecha_postulacion=app.fecha_postulacion,
                estado=app.estado,
                consentimiento_datos=app.consentimiento_datos,
                cv_file_path=app.cv_file_path,
                cv_text_extracted=app.cv_text_extracted,
                fuente=app.fuente,
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
            )
        )
    return result


@router.get("/{vacancy_id}/qr", response_model=VacancyQRRead)
def qr_route(vacancy_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> VacancyQRRead:
    entity = get_vacancy(db, vacancy_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")

    return VacancyQRRead(
        vacancy_id=entity.id,
        token=entity.qr_token,
        public_url=entity.public_url,
        qr_base64_png=generate_qr_base64(entity.public_url),
    )


@router.get("/{vacancy_id}/profile-document")
def profile_document_route(
    vacancy_id: int,
    disposition: str = Query("attachment", pattern="^(inline|attachment)$"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> FileResponse:
    entity = get_vacancy(db, vacancy_id)
    if not entity or not entity.descriptivo_archivo_path:
        raise HTTPException(status_code=404, detail="Documento descriptivo no encontrado")

    file_path = Path(entity.descriptivo_archivo_path)
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path
    file_path = file_path.resolve()
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Documento descriptivo no encontrado")

    media_type = "application/octet-stream"
    if file_path.suffix.lower() == ".pdf":
        media_type = "application/pdf"
    elif file_path.suffix.lower() == ".docx":
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    filename = entity.descriptivo_archivo_nombre or file_path.name
    response = FileResponse(path=str(file_path), media_type=media_type, filename=filename)
    if disposition == "inline":
        response.headers["Content-Disposition"] = f'inline; filename="{filename}"'
    return response
