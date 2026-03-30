from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models.application import Application, ApplicationAnswer
from app.models.candidate import Candidate
from app.models.job_profile import JobQuestion
from app.models.organization import Area, Branch, Company
from app.repositories.vacancy_repository import get_by_token
from app.schemas.public import PublicApplicationCreate, PublicApplicationResult, PublicJobQuestionRead, PublicVacancyRead
from app.services.cv_parser import extract_text, save_upload_file
from app.services.scoring_service import recalculate_application_score

router = APIRouter()


@router.get("/vacancy/{token}", response_model=PublicVacancyRead)
def get_public_vacancy(token: str, db: Session = Depends(get_db)) -> PublicVacancyRead:
    vacancy = get_by_token(db, token)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")

    company = db.get(Company, vacancy.company_id)
    branch = db.get(Branch, vacancy.branch_id)
    area = db.get(Area, vacancy.area_id)
    questions = []
    if vacancy.job_profile_id:
        questions = db.scalars(
            select(JobQuestion)
            .where(JobQuestion.job_profile_id == vacancy.job_profile_id)
            .order_by(JobQuestion.orden.asc(), JobQuestion.id.asc())
        ).all()

    return PublicVacancyRead(
        vacancy_id=vacancy.id,
        titulo_publicacion=vacancy.titulo_publicacion,
        descripcion_publicacion=vacancy.descripcion_publicacion,
        company_name=company.name,
        branch_name=branch.name,
        area_name=area.name,
        questions=[
            PublicJobQuestionRead(
                id=question.id,
                pregunta=question.pregunta,
                tipo_respuesta=question.tipo_respuesta.value,
                obligatoria=question.obligatoria,
                eliminatoria=question.eliminatoria,
                orden=question.orden,
            )
            for question in questions
        ],
    )


@router.post("/upload-cv")
def upload_cv(file: UploadFile = File(...)) -> dict[str, str]:
    settings = get_settings()
    path = save_upload_file(settings.upload_dir, file)
    return {"cv_file_path": path}


@router.post("/applications")
def create_public_application(
    token: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(...),
    ciudad: str = Form(...),
    provincia: str = Form(...),
    consentimiento_datos: bool = Form(...),
    fuente: str = Form("qr_publico"),
    linkedin: str | None = Form(None),
    answers_json: str = Form("[]"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> PublicApplicationResult:
    import json

    payload = PublicApplicationCreate(
        token=token,
        nombre=nombre,
        apellido=apellido,
        email=email,
        telefono=telefono,
        ciudad=ciudad,
        provincia=provincia,
        consentimiento_datos=consentimiento_datos,
        fuente=fuente,
        linkedin=linkedin,
        answers=[item for item in json.loads(answers_json)],
    )

    vacancy = get_by_token(db, payload.token)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")

    candidate = db.scalar(select(Candidate).where(Candidate.email == payload.email))
    if not candidate:
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

    settings = get_settings()
    cv_file_path = save_upload_file(settings.upload_dir, file)
    cv_text = extract_text(cv_file_path)

    application = Application(
        vacancy_id=vacancy.id,
        candidate_id=candidate.id,
        consentimiento_datos=payload.consentimiento_datos,
        cv_file_path=cv_file_path,
        cv_text_extracted=cv_text,
        fuente=payload.fuente,
    )
    db.add(application)
    db.flush()

    for ans in payload.answers:
        db.add(
            ApplicationAnswer(
                application_id=application.id,
                job_question_id=ans.job_question_id,
                respuesta=ans.respuesta,
            )
        )

    score = recalculate_application_score(db, application.id)

    db.commit()
    return PublicApplicationResult(
        application_id=application.id,
        message="Postulacion enviada con analisis inicial",
        score_total=score.score_total,
        clasificacion=score.clasificacion,
        resumen_analisis=score.resumen_analisis,
    )
