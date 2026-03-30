from pydantic import BaseModel, EmailStr


class PublicJobQuestionRead(BaseModel):
    id: int
    pregunta: str
    tipo_respuesta: str
    obligatoria: bool
    eliminatoria: bool
    orden: int


class PublicVacancyListItem(BaseModel):
    vacancy_id: int
    token: str
    titulo_publicacion: str
    empresa: str = ""
    localidad: str = ""
    area: str = ""
    public_url: str = ""


class PublicVacancyRead(BaseModel):
    vacancy_id: int
    titulo_publicacion: str
    descripcion_publicacion: str
    empresa: str = ""
    localidad: str = ""
    area: str = ""
    company_name: str = ""
    branch_name: str = ""
    area_name: str = ""
    questions: list[PublicJobQuestionRead] = []


class PublicApplicationAnswer(BaseModel):
    job_question_id: int
    respuesta: str


class PublicApplicationCreate(BaseModel):
    token: str
    nombre: str
    apellido: str
    email: EmailStr
    telefono: str
    ciudad: str
    provincia: str
    linkedin: str | None = None
    consentimiento_datos: bool
    fuente: str = "qr_publico"
    answers: list[PublicApplicationAnswer] = []


class PublicApplicationResult(BaseModel):
    application_id: int
    message: str
    score_total: int
    clasificacion: str
    resumen_analisis: str
