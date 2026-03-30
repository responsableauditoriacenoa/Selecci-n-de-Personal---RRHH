from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import ApplicationStatus


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    vacancy_id: Mapped[int] = mapped_column(ForeignKey("vacancies.id"), index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True)
    fecha_postulacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    estado: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus), default=ApplicationStatus.POSTULADO)
    consentimiento_datos: Mapped[bool] = mapped_column(default=False)
    cv_file_path: Mapped[str] = mapped_column(String(500))
    cv_text_extracted: Mapped[str] = mapped_column(Text, default="")
    fuente: Mapped[str] = mapped_column(String(120), default="qr_publico")
    is_deleted: Mapped[bool] = mapped_column(default=False)


class ApplicationAnswer(Base):
    __tablename__ = "application_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), index=True)
    job_question_id: Mapped[int] = mapped_column(ForeignKey("job_questions.id"), index=True)
    respuesta: Mapped[str] = mapped_column(Text)


class ApplicationInsight(Base):
    __tablename__ = "application_insights"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), unique=True, index=True)
    strengths_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    weaknesses_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    opportunities_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    matches_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    gaps_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    analytical_conclusion: Mapped[str] = mapped_column(Text, default="")
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
