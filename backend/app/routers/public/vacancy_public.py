from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job_profile import JobQuestion
from app.models.organization import Area, Branch, Company
from app.repositories.vacancy_repository import get_by_token
from app.schemas.public import PublicJobQuestionRead, PublicVacancyRead

router = APIRouter()


@router.get("/vacancy/{token}", response_model=PublicVacancyRead)
def get_public_vacancy(token: str, db: Session = Depends(get_db)) -> PublicVacancyRead:
    vacancy = get_by_token(db, token)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Vacante no encontrada")

    company = db.get(Company, vacancy.company_id) if vacancy.company_id else None
    branch = db.get(Branch, vacancy.branch_id) if vacancy.branch_id else None
    area = db.get(Area, vacancy.area_id) if vacancy.area_id else None
    questions = []
    if vacancy.job_profile_id:
        questions = db.scalars(
            select(JobQuestion)
            .where(JobQuestion.job_profile_id == vacancy.job_profile_id)
            .order_by(JobQuestion.orden.asc(), JobQuestion.id.asc())
        ).all()

    empresa = vacancy.empresa or (company.name if company else "")
    localidad = vacancy.localidad or (branch.name if branch else "")
    area_name = vacancy.area or (area.name if area else "")

    return PublicVacancyRead(
        vacancy_id=vacancy.id,
        titulo_publicacion=vacancy.titulo_publicacion,
        descripcion_publicacion=vacancy.descripcion_publicacion,
        empresa=empresa,
        localidad=localidad,
        area=area_name,
        company_name=empresa,
        branch_name=localidad,
        area_name=area_name,
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
