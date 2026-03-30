from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import JobProfileStatus, QuestionType


class JobProfile(Base):
    __tablename__ = "job_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_puesto: Mapped[str] = mapped_column(String(255), index=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("areas.id"), index=True)
    seniority: Mapped[str] = mapped_column(String(100))
    modalidad: Mapped[str] = mapped_column(String(100))
    ubicacion: Mapped[str] = mapped_column(String(255))
    descripcion_general: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1)
    estado: Mapped[JobProfileStatus] = mapped_column(Enum(JobProfileStatus), default=JobProfileStatus.BORRADOR)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    requirements = relationship("JobRequirement", back_populates="job_profile", cascade="all, delete-orphan")
    questions = relationship("JobQuestion", back_populates="job_profile", cascade="all, delete-orphan")


class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_profile_id: Mapped[int] = mapped_column(ForeignKey("job_profiles.id"), index=True)
    tipo: Mapped[str] = mapped_column(String(100))
    nombre: Mapped[str] = mapped_column(String(255))
    descripcion: Mapped[str] = mapped_column(Text, default="")
    obligatorio: Mapped[bool] = mapped_column(default=False)
    peso: Mapped[int] = mapped_column(Integer, default=10)
    valor_esperado: Mapped[str] = mapped_column(String(255), default="")

    job_profile = relationship("JobProfile", back_populates="requirements")


class JobQuestion(Base):
    __tablename__ = "job_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_profile_id: Mapped[int] = mapped_column(ForeignKey("job_profiles.id"), index=True)
    pregunta: Mapped[str] = mapped_column(Text)
    tipo_respuesta: Mapped[QuestionType] = mapped_column(Enum(QuestionType), default=QuestionType.TEXTO)
    obligatoria: Mapped[bool] = mapped_column(default=True)
    eliminatoria: Mapped[bool] = mapped_column(default=False)
    peso: Mapped[int] = mapped_column(Integer, default=10)
    orden: Mapped[int] = mapped_column(Integer, default=1)

    job_profile = relationship("JobProfile", back_populates="questions")
