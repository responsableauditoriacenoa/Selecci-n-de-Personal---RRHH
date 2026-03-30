from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import VacancyStatus


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_profile_id: Mapped[int] = mapped_column(ForeignKey("job_profiles.id"), index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), index=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("areas.id"), index=True)
    empresa: Mapped[str] = mapped_column(String(100), default="")
    localidad: Mapped[str] = mapped_column(String(100), default="")
    area: Mapped[str] = mapped_column(String(100), default="")
    titulo_publicacion: Mapped[str] = mapped_column(String(255))
    descripcion_publicacion: Mapped[str] = mapped_column(Text)
    descriptivo_puesto: Mapped[str] = mapped_column(Text, default="")
    fecha_apertura: Mapped[date] = mapped_column(Date)
    fecha_cierre: Mapped[date] = mapped_column(Date)
    estado: Mapped[VacancyStatus] = mapped_column(Enum(VacancyStatus), default=VacancyStatus.ABIERTA)
    qr_token: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    public_url: Mapped[str] = mapped_column(String(500))
    descriptivo_archivo_nombre: Mapped[str | None] = mapped_column(String(255), nullable=True)
    descriptivo_archivo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    descriptivo_texto_extraido: Mapped[str] = mapped_column(Text, default="")
