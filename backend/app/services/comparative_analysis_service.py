from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationInsight
from app.models.enums import ScoreReasonType
from app.models.scoring import ApplicationScore, ScoreReason
from app.models.vacancy import Vacancy


def _contains(text: str, token: str) -> bool:
    return token.strip().lower() in text


def _build_conclusion(
    score_total: int,
    critical_gaps: int,
    strengths: int,
    opportunities: int,
) -> str:
    if score_total >= 85 and critical_gaps == 0:
        return "Perfil fuertemente alineado al puesto, con evidencia suficiente para avanzar a entrevista tecnica y validacion final."
    if score_total >= 70 and critical_gaps <= 1:
        return "Perfil compatible con el puesto. Se recomienda avanzar con revision focalizada en brechas puntuales."
    if score_total >= 50:
        return "Perfil parcialmente compatible, recomendable para revision manual con foco en validaciones tecnicas y de experiencia."
    if strengths > 0 and opportunities > 0:
        return "Perfil con aportes potenciales, pero sin evidencia suficiente en requisitos criticos del puesto."
    return "Perfil de baja compatibilidad por incumplimiento o falta de evidencia en condiciones centrales de la vacante."


def generate_or_update_application_insight(
    db: Session,
    application_id: int,
    score_total: int,
) -> ApplicationInsight:
    application = db.get(Application, application_id)
    if not application:
        raise ValueError("Application not found")

    vacancy = db.get(Vacancy, application.vacancy_id)
    score = db.scalar(select(ApplicationScore).where(ApplicationScore.application_id == application_id))
    reasons = []
    if score:
        reasons = db.scalars(select(ScoreReason).where(ScoreReason.application_score_id == score.id)).all()

    fortalezas_detectadas: list[str] = []
    debilidades_detectadas: list[str] = []
    oportunidades_detectadas: list[str] = []
    coincidencias_clave: list[str] = []
    faltantes_relevantes: list[str] = []

    for reason in reasons:
        if reason.tipo == ScoreReasonType.FORTALEZA:
            fortalezas_detectadas.append(reason.descripcion)
            coincidencias_clave.append(reason.descripcion)
        elif reason.tipo in {ScoreReasonType.ALERTA, ScoreReasonType.DESCARTE}:
            debilidades_detectadas.append(reason.descripcion)
            faltantes_relevantes.append(reason.descripcion)
        else:
            oportunidades_detectadas.append(reason.descripcion)
            faltantes_relevantes.append(reason.descripcion)

    if score and score.dimension_scores:
        low_dimensions = [item for item in score.dimension_scores if int(item.get("score", 0)) <= max(int(item.get("weight", 0)) // 3, 1)]
        for item in low_dimensions[:3]:
            faltantes_relevantes.append(f"Dimension a reforzar: {item.get('label', 'Sin nombre')}.")

    if vacancy and vacancy.area:
        coincidencias_clave.append(f"Vacante analizada para el area {vacancy.area}.")

    # Deduplicate preserving insertion order.
    def _uniq(items: list[str]) -> list[str]:
        seen: set[str] = set()
        unique: list[str] = []
        for item in items:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        return unique

    fortalezas_detectadas = _uniq(fortalezas_detectadas)
    debilidades_detectadas = _uniq(debilidades_detectadas)
    oportunidades_detectadas = _uniq(oportunidades_detectadas)
    coincidencias_clave = _uniq(coincidencias_clave)
    faltantes_relevantes = _uniq(faltantes_relevantes)

    conclusion_analitica = _build_conclusion(
        score_total=score_total,
        critical_gaps=len(debilidades_detectadas) + len(faltantes_relevantes),
        strengths=len(fortalezas_detectadas),
        opportunities=len(oportunidades_detectadas),
    )

    insight = db.scalar(select(ApplicationInsight).where(ApplicationInsight.application_id == application_id))
    if not insight:
        insight = ApplicationInsight(application_id=application_id)
        db.add(insight)
        db.flush()

    insight.strengths_json = fortalezas_detectadas
    insight.weaknesses_json = debilidades_detectadas
    insight.opportunities_json = oportunidades_detectadas
    insight.matches_json = coincidencias_clave
    insight.gaps_json = faltantes_relevantes
    insight.analytical_conclusion = conclusion_analitica
    insight.generated_at = datetime.utcnow()

    return insight
