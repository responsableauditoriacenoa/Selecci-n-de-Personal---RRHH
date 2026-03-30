from datetime import datetime

from pydantic import BaseModel

from app.models.enums import ApplicationStatus, ScoreReasonType


class ApplicationAnswerRead(BaseModel):
    id: int
    job_question_id: int
    respuesta: str


class ScoreReasonRead(BaseModel):
    id: int
    tipo: ScoreReasonType
    descripcion: str
    impacto: int


class ApplicationScoreRead(BaseModel):
    id: int
    score_total: int
    score_formacion: int
    score_experiencia: int
    score_tecnico: int
    score_preguntas: int
    score_competencias: int
    clasificacion: str
    resumen_analisis: str
    fecha_calculo: datetime
    reasons: list[ScoreReasonRead] = []


class ApplicationInsightRead(BaseModel):
    application_id: int
    fortalezas_detectadas: list[str] = []
    debilidades_detectadas: list[str] = []
    oportunidades_detectadas: list[str] = []
    coincidencias_clave: list[str] = []
    faltantes_relevantes: list[str] = []
    conclusion_analitica: str
    generated_at: datetime


class CandidateRead(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: str
    telefono: str
    ciudad: str
    provincia: str
    linkedin: str | None


class ApplicationRead(BaseModel):
    id: int
    vacancy_id: int
    candidate_id: int
    fecha_postulacion: datetime
    estado: ApplicationStatus
    consentimiento_datos: bool
    cv_file_path: str
    cv_text_extracted: str
    fuente: str
    candidate: CandidateRead | None = None
    answers: list[ApplicationAnswerRead] = []
    score: ApplicationScoreRead | None = None
    insight: ApplicationInsightRead | None = None


class ChangeApplicationStatusRequest(BaseModel):
    estado: ApplicationStatus


class CandidateNoteCreate(BaseModel):
    comentario: str


class CandidateNoteRead(BaseModel):
    id: int
    application_id: int
    user_id: int
    comentario: str
    fecha: datetime
