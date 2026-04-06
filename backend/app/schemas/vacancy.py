from datetime import date

from pydantic import BaseModel, Field

from app.models.enums import VacancyStatus
from app.schemas.job_profile import JobQuestionBase, JobRequirementBase, ScoringDimensionBase


class VacancyJobProfileConfig(BaseModel):
    nombre_puesto: str = ""
    seniority: str = ""
    modalidad: str = ""
    ubicacion: str = ""
    descripcion_general: str = ""
    scoring_dimensions: list[ScoringDimensionBase] = Field(default_factory=list)
    requirements: list[JobRequirementBase] = Field(default_factory=list)
    questions: list[JobQuestionBase] = Field(default_factory=list)


class VacancyBase(BaseModel):
    job_profile_id: int = 1
    company_id: int = 1
    branch_id: int = 1
    area_id: int = 1
    empresa: str = ""
    localidad: str = ""
    area: str = ""
    titulo_publicacion: str
    descripcion_publicacion: str = ""
    descriptivo_puesto: str = ""
    fecha_apertura: date
    fecha_cierre: date
    estado: VacancyStatus = VacancyStatus.ABIERTA


class VacancyCreate(VacancyBase):
    job_profile_config: VacancyJobProfileConfig | None = None


class VacancyUpdate(VacancyBase):
    job_profile_config: VacancyJobProfileConfig | None = None


class VacancyRead(VacancyBase):
    id: int
    qr_token: str
    public_url: str
    descriptivo_archivo_nombre: str | None = None
    descriptivo_documento_cargado: bool = False

    class Config:
        from_attributes = True


class VacancyQRRead(BaseModel):
    vacancy_id: int
    token: str
    public_url: str
    qr_base64_png: str


class VacancyCreateResponse(VacancyRead):
    qr_base64_png: str
