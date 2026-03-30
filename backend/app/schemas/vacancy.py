from datetime import date

from pydantic import BaseModel

from app.models.enums import VacancyStatus


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
    pass


class VacancyUpdate(VacancyBase):
    pass


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
