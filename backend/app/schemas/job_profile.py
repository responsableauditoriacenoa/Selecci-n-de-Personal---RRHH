from datetime import datetime

from pydantic import BaseModel

from app.models.enums import JobProfileStatus, QuestionType


class JobRequirementBase(BaseModel):
    tipo: str
    nombre: str
    descripcion: str = ""
    obligatorio: bool = False
    peso: int = 10
    valor_esperado: str = ""


class JobRequirementRead(JobRequirementBase):
    id: int

    class Config:
        from_attributes = True


class JobQuestionBase(BaseModel):
    pregunta: str
    tipo_respuesta: QuestionType = QuestionType.TEXTO
    obligatoria: bool = True
    eliminatoria: bool = False
    peso: int = 10
    orden: int = 1


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
    version: int = 1
    estado: JobProfileStatus = JobProfileStatus.BORRADOR


class JobProfileCreate(JobProfileBase):
    requirements: list[JobRequirementBase] = []
    questions: list[JobQuestionBase] = []


class JobProfileUpdate(JobProfileCreate):
    pass


class JobProfileRead(JobProfileBase):
    id: int
    created_by: int
    created_at: datetime
    requirements: list[JobRequirementRead] = []
    questions: list[JobQuestionRead] = []

    class Config:
        from_attributes = True


class JobProfileDocumentAnalysisRead(BaseModel):
    job_profile_id: int
    file_name: str
    score_compatibilidad: int
    clasificacion: str
    comentario_analisis: str
    coincidencias_clave: list[str] = []
    alertas: list[str] = []
