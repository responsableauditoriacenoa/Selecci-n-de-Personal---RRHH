from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.scoring_parameters import KEYWORDS_BY_CLUSTER
from app.models.application import Application, ApplicationAnswer, ApplicationInsight
from app.models.job_profile import JobQuestion, JobRequirement
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
    answers = db.scalars(select(ApplicationAnswer).where(ApplicationAnswer.application_id == application_id)).all()

    requirements = []
    questions = []
    if vacancy and vacancy.job_profile_id:
        requirements = db.scalars(select(JobRequirement).where(JobRequirement.job_profile_id == vacancy.job_profile_id)).all()
        questions = db.scalars(select(JobQuestion).where(JobQuestion.job_profile_id == vacancy.job_profile_id)).all()

    cv_text = (application.cv_text_extracted or "").lower()
    answers_text = " ".join(item.respuesta.lower().strip() for item in answers)
    evidence_text = f"{cv_text} {answers_text}".strip()

    descriptive_text = (
        (vacancy.descriptivo_puesto or "")
        + " "
        + (vacancy.descriptivo_texto_extraido or "")
        + " "
        + (vacancy.descripcion_publicacion or "")
    ).lower()

    fortalezas_detectadas: list[str] = []
    debilidades_detectadas: list[str] = []
    oportunidades_detectadas: list[str] = []
    coincidencias_clave: list[str] = []
    faltantes_relevantes: list[str] = []

    for req in requirements:
        esperado = (req.valor_esperado or "").strip().lower()
        if esperado and _contains(evidence_text, esperado):
            coincidencias_clave.append(f"Coincide requisito {req.nombre}: se detecta evidencia de '{esperado}'.")
            if req.obligatorio:
                fortalezas_detectadas.append(f"Cumple requisito excluyente: {req.nombre}.")
            else:
                fortalezas_detectadas.append(f"Cumple requisito deseable: {req.nombre}.")
        elif req.obligatorio:
            msg = f"No se evidencia cumplimiento de requisito excluyente: {req.nombre}."
            debilidades_detectadas.append(msg)
            faltantes_relevantes.append(msg)
        else:
            faltantes_relevantes.append(f"No surge evidencia del requisito deseable: {req.nombre}.")

    answer_map = {item.job_question_id: item.respuesta.strip().lower() for item in answers}
    for question in questions:
        value = answer_map.get(question.id, "")
        if question.obligatoria and not value:
            faltantes_relevantes.append(f"Sin respuesta en pregunta obligatoria de screening: {question.pregunta}")
        elif value:
            coincidencias_clave.append(f"Screening respondido: {question.pregunta}")
            if question.eliminatoria and value in {"no", "false", "0"}:
                debilidades_detectadas.append(f"Respuesta con riesgo eliminatorio en screening: {question.pregunta}")

    for token in KEYWORDS_BY_CLUSTER["tecnico"]:
        if _contains(evidence_text, token):
            if _contains(descriptive_text, token):
                coincidencias_clave.append(f"Match tecnico: {token}")
            else:
                oportunidades_detectadas.append(f"Conocimiento adicional detectado no explicito en vacante: {token}")

    for token in KEYWORDS_BY_CLUSTER["competencias"]:
        if _contains(evidence_text, token):
            if _contains(descriptive_text, token):
                fortalezas_detectadas.append(f"Competencia alineada al puesto: {token}")
            else:
                oportunidades_detectadas.append(f"Competencia transferible detectada: {token}")

    if "certificacion" in evidence_text or "certificado" in evidence_text:
        oportunidades_detectadas.append("Presenta indicios de certificaciones o formacion complementaria.")

    if "lider" in evidence_text or "liderazgo" in evidence_text:
        oportunidades_detectadas.append("Muestra potencial para asumir responsabilidades de coordinacion o liderazgo.")

    if len(cv_text.split()) < 60:
        debilidades_detectadas.append("El CV contiene informacion limitada para validar integralmente el perfil.")

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
