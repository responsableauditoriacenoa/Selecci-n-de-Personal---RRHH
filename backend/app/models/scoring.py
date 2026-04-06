from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import ScoreReasonType


class ApplicationScore(Base):
    __tablename__ = "application_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), unique=True, index=True)
    score_total: Mapped[int] = mapped_column(Integer, default=0)
    score_formacion: Mapped[int] = mapped_column(Integer, default=0)
    score_experiencia: Mapped[int] = mapped_column(Integer, default=0)
    score_tecnico: Mapped[int] = mapped_column(Integer, default=0)
    score_preguntas: Mapped[int] = mapped_column(Integer, default=0)
    score_competencias: Mapped[int] = mapped_column(Integer, default=0)
    dimension_scores: Mapped[list[dict[str, object]]] = mapped_column("dimension_scores_json", JSON, default=list)
    clasificacion: Mapped[str] = mapped_column(Text)
    resumen_analisis: Mapped[str] = mapped_column(Text)
    fecha_calculo: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ScoreReason(Base):
    __tablename__ = "score_reasons"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_score_id: Mapped[int] = mapped_column(ForeignKey("application_scores.id"), index=True)
    tipo: Mapped[ScoreReasonType] = mapped_column(Enum(ScoreReasonType), default=ScoreReasonType.OBSERVACION)
    descripcion: Mapped[str] = mapped_column(Text)
    impacto: Mapped[int] = mapped_column(Integer, default=0)
