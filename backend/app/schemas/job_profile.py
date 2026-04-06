from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import JobProfileStatus, QuestionType


class ScoringDimensionBase(BaseModel):
    key: str
    label: str
    weight: int


class JobRequirementBase(BaseModel):
    tipo: str
    dimension: str = "general"
    nombre: str
    descripcion: str = ""
    obligatorio: bool = False
    peso: int = 10
    valor_esperado: str = ""
    keywords: list[str] = Field(default_factory=list)
    match_mode: str = "any"
    failure_mode: str = "revisar"


class JobRequirementRead(JobRequirementBase):
    id: int

    class Config:
        from_attributes = True


class JobQuestionBase(BaseModel):
    pregunta: str
    dimension: str = "preguntas"
    tipo_respuesta: QuestionType = QuestionType.TEXTO
    obligatoria: bool = True
    eliminatoria: bool = False
    peso: int = 10
    orden: int = 1
    opciones: list[str] = Field(default_factory=list)
    respuestas_aceptadas: list[str] = Field(default_factory=list)
    failure_mode: str = "revisar"


class JobQuestionRead(JobQuestionBase):
    id: int

    class Config:
        from_attributes = True


class JobProfileBase(BaseModel):
    nombre_puesto: str
    area_id: int
    seniority: str
    modalidad: str
    ubicacion: str
    descripcion_general: str
    scoring_dimensions: list[ScoringDimensionBase] = Field(default_factory=list)
    version: int = 1
    estado: JobProfileStatus = JobProfileStatus.BORRADOR


class JobProfileCreate(JobProfileBase):
    requirements: list[JobRequirementBase] = Field(default_factory=list)
    questions: list[JobQuestionBase] = Field(default_factory=list)


class JobProfileUpdate(JobProfileCreate):
    pass


class JobProfileRead(JobProfileBase):
    id: int
    created_by: int
    created_at: datetime
    requirements: list[JobRequirementRead] = Field(default_factory=list)
    questions: list[JobQuestionRead] = Field(default_factory=list)

    class Config:
        from_attributes = True


class JobProfileDocumentAnalysisRead(BaseModel):
    job_profile_id: int
    file_name: str
    score_compatibilidad: int
    clasificacion: str
    comentario_analisis: str
    coincidencias_clave: list[str] = Field(default_factory=list)
    alertas: list[str] = Field(default_factory=list)
