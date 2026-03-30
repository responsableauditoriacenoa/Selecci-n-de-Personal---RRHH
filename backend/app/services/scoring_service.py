from datetime import datetime
import re

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.scoring_parameters import (
    KEYWORDS_BY_CLUSTER,
    RECOMMENDATION_MATRIX,
    SCORING_THRESHOLDS,
    SCORING_WEIGHTS,
)
from app.models.application import Application, ApplicationAnswer
from app.models.enums import ScoreReasonType
from app.models.job_profile import JobQuestion, JobRequirement
from app.models.scoring import ApplicationScore, ScoreReason
from app.models.vacancy import Vacancy
from app.services.comparative_analysis_service import generate_or_update_application_insight


def _classification(total: int) -> str:
    if total >= SCORING_THRESHOLDS["muy_recomendado"]:
        return "muy recomendado"
    if total >= SCORING_THRESHOLDS["recomendado"]:
        return "recomendado"
    if total >= SCORING_THRESHOLDS["revisar"]:
        return "revisar"
    return "baja compatibilidad"


def _extract_keywords(text: str, candidates: list[str]) -> list[str]:
    return [token for token in candidates if token in text]


def _extract_profile_terms(text: str, limit: int = 12) -> list[str]:
    stopwords = {
        "para", "como", "con", "del", "las", "los", "una", "uno", "que", "por", "sus", "ser", "se",
        "sobre", "desde", "hasta", "entre", "sin", "más", "mas", "muy", "perfil", "puesto", "vacante",
        "empresa", "trabajo", "experiencia", "años", "anos", "responsable", "capacidad", "requisito",
        "requisitos", "deseable", "excluyente", "modalidad", "ubicacion", "seniority", "postulante",
    }
    counts: dict[str, int] = {}
    for token in re.findall(r"[a-zA-Záéíóúñü]{4,}", text.lower()):
        if token in stopwords:
            continue
        counts[token] = counts.get(token, 0) + 1
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [item[0] for item in ordered[:limit]]


def _build_executive_summary(
    clasificacion: str,
    total: int,
    strengths: int,
    observations: int,
    critical_flags: int,
    cv_word_count: int,
    technical_hits: list[str],
    experience_hits: list[str],
    competency_hits: list[str],
) -> str:
    recomendacion = RECOMMENDATION_MATRIX[clasificacion]
    return (
        f"Dictamen tecnico RRHH: {clasificacion} ({total}/100). "
        f"Se registran {strengths} fortalezas, {observations} observaciones y {critical_flags} alertas o descartes. "
        f"Fuente analizada: CV con ~{cv_word_count} palabras y respuestas de screening. "
        f"Cobertura tecnica detectada: {', '.join(technical_hits) if technical_hits else 'sin evidencia robusta'}. "
        f"Indicadores de experiencia: {', '.join(experience_hits) if experience_hits else 'sin senales concluyentes'}. "
        f"Competencias observables: {', '.join(competency_hits) if competency_hits else 'sin trazas suficientes'}. "
        f"Recomendacion operativa: {recomendacion}"
    )


def recalculate_application_score(db: Session, application_id: int) -> ApplicationScore:
    application = db.get(Application, application_id)
    if not application:
        raise ValueError("Application not found")

    vacancy = db.get(Vacancy, application.vacancy_id)
    requirements = []
    questions = []
    if vacancy.job_profile_id:
        requirements = db.scalars(select(JobRequirement).where(JobRequirement.job_profile_id == vacancy.job_profile_id)).all()
        questions = db.scalars(select(JobQuestion).where(JobQuestion.job_profile_id == vacancy.job_profile_id)).all()
    answers = db.scalars(select(ApplicationAnswer).where(ApplicationAnswer.application_id == application_id)).all()

    cv_text = (application.cv_text_extracted or "").lower()
    reasons: list[ScoreReason] = []
    cv_word_count = len([token for token in cv_text.split() if token.strip()])
    screening_text = " ".join(a.respuesta.strip().lower() for a in answers)
    evidence_text = f"{cv_text} {screening_text}".strip()
    vacancy_profile_text = (
        (vacancy.descriptivo_puesto or "")
        + " "
        + (vacancy.descriptivo_texto_extraido or "")
        + " "
        + (vacancy.descripcion_publicacion or "")
    ).lower()
    profile_terms = _extract_profile_terms(vacancy_profile_text)

    technical_hits = _extract_keywords(evidence_text, KEYWORDS_BY_CLUSTER["tecnico"])
    experience_hits = _extract_keywords(evidence_text, KEYWORDS_BY_CLUSTER["experiencia"])
    competency_hits = _extract_keywords(evidence_text, KEYWORDS_BY_CLUSTER["competencias"])
    profile_term_hits = [term for term in profile_terms if term in evidence_text]
    missing_profile_terms = [term for term in profile_terms if term not in evidence_text][:5]

    if cv_word_count < 40:
        reasons.append(
            ScoreReason(
                tipo=ScoreReasonType.ALERTA,
                descripcion="El CV presenta poco contenido legible; se sugiere validacion manual del archivo.",
                impacto=-10,
            )
        )
    else:
        reasons.append(
            ScoreReason(
                tipo=ScoreReasonType.OBSERVACION,
                descripcion=f"Extraccion de CV completada con aproximadamente {cv_word_count} palabras utiles.",
                impacto=0,
            )
        )

    req_points = 0

    for req in requirements:
        expected = (req.valor_esperado or "").lower().strip()
        matched = expected and expected in cv_text

        if req.obligatorio and not matched:
            reasons.append(
                ScoreReason(
                    tipo=ScoreReasonType.DESCARTE,
                    descripcion=f"No se evidencia requisito obligatorio en CV: {req.nombre}.",
                    impacto=-25,
                )
            )
            req_points -= 25
        elif matched:
            req_points += req.peso
            reasons.append(
                ScoreReason(
                    tipo=ScoreReasonType.FORTALEZA,
                    descripcion=f"Se valida evidencia alineada al requisito: {req.nombre}.",
                    impacto=req.peso,
                )
            )
        else:
            reasons.append(
                ScoreReason(
                    tipo=ScoreReasonType.OBSERVACION,
                    descripcion=f"No se detecta evidencia concluyente para el requisito: {req.nombre}. Requiere validacion en entrevista.",
                    impacto=-5,
                )
            )
            req_points -= 5

    ans_map = {a.job_question_id: a.respuesta.strip().lower() for a in answers}
    question_score = 0

    for question in questions:
        answer = ans_map.get(question.id, "")
        if question.obligatoria and not answer:
            reasons.append(
                ScoreReason(
                    tipo=ScoreReasonType.ALERTA,
                    descripcion=f"Falta respuesta en pregunta obligatoria de screening: {question.pregunta}",
                    impacto=-10,
                )
            )
            question_score -= 10
        elif answer:
            if question.eliminatoria and answer in {"no", "false", "0"}:
                reasons.append(
                    ScoreReason(
                        tipo=ScoreReasonType.DESCARTE,
                        descripcion=f"Respuesta con criterio eliminatorio en screening: {question.pregunta}",
                        impacto=-30,
                    )
                )
                question_score -= 30
            else:
                reasons.append(
                    ScoreReason(
                        tipo=ScoreReasonType.FORTALEZA,
                        descripcion=f"Respuesta favorable en screening: {question.pregunta}.",
                        impacto=question.peso,
                    )
                )
                question_score += question.peso

    profile_alignment_bonus = min(len(profile_term_hits) * 2, 15)
    tech_bonus = min(len(technical_hits) * 3, 18)
    exp_bonus = min(len(experience_hits) * 3, 15)
    comp_bonus = min(len(competency_hits) * 2, 10)

    score_formacion = max(min((req_points // 3) + (exp_bonus // 3), SCORING_WEIGHTS["formacion"]), 0)
    score_experiencia = max(min((req_points // 2) + exp_bonus + (profile_alignment_bonus // 2), SCORING_WEIGHTS["experiencia"]), 0)
    score_tecnico = max(min((req_points // 2) + tech_bonus + profile_alignment_bonus, SCORING_WEIGHTS["tecnico"]), 0)
    score_preguntas = max(min(question_score, SCORING_WEIGHTS["preguntas"]), 0)
    score_competencias = max(min((comp_bonus + score_preguntas // 4), SCORING_WEIGHTS["competencias"]), 0)

    total = max(min(score_formacion + score_experiencia + score_tecnico + score_preguntas + score_competencias, 100), 0)
    clasificacion = _classification(total)
    critical_flags = len([reason for reason in reasons if reason.tipo in {ScoreReasonType.DESCARTE, ScoreReasonType.ALERTA}])
    strengths = len([reason for reason in reasons if reason.tipo == ScoreReasonType.FORTALEZA])
    observations = len([reason for reason in reasons if reason.tipo == ScoreReasonType.OBSERVACION])

    if technical_hits:
        reasons.append(
            ScoreReason(
                tipo=ScoreReasonType.FORTALEZA,
                descripcion=f"Fortaleza tecnica transversal detectada: {', '.join(technical_hits)}.",
                impacto=min(len(technical_hits) * 2, 12),
            )
        )
    else:
        reasons.append(
            ScoreReason(
                tipo=ScoreReasonType.ALERTA,
                descripcion="No se identifican suficientes senales tecnicas en el CV para la vacante actual.",
                impacto=-8,
            )
        )

    if profile_term_hits:
        reasons.append(
            ScoreReason(
                tipo=ScoreReasonType.FORTALEZA,
                descripcion=f"Alineacion con ejes del descriptivo adjunto: {', '.join(profile_term_hits[:6])}.",
                impacto=min(len(profile_term_hits) * 2, 12),
            )
        )

    if missing_profile_terms:
        reasons.append(
            ScoreReason(
                tipo=ScoreReasonType.OBSERVACION,
                descripcion=f"Oportunidades de validacion en entrevista: {', '.join(missing_profile_terms)}.",
                impacto=-4,
            )
        )

    if competency_hits:
        reasons.append(
            ScoreReason(
                tipo=ScoreReasonType.OBSERVACION,
                descripcion=f"Competencias blandas detectadas: {', '.join(competency_hits)}.",
                impacto=min(len(competency_hits), 5),
            )
        )

    strengths = len([reason for reason in reasons if reason.tipo == ScoreReasonType.FORTALEZA])
    observations = len([reason for reason in reasons if reason.tipo == ScoreReasonType.OBSERVACION])
    critical_flags = len([reason for reason in reasons if reason.tipo in {ScoreReasonType.DESCARTE, ScoreReasonType.ALERTA}])

    score = db.scalar(select(ApplicationScore).where(ApplicationScore.application_id == application_id))
    if not score:
        score = ApplicationScore(application_id=application_id, clasificacion=clasificacion, resumen_analisis="")
        db.add(score)
        db.flush()

    score.score_total = total
    score.score_formacion = score_formacion
    score.score_experiencia = score_experiencia
    score.score_tecnico = score_tecnico
    score.score_preguntas = score_preguntas
    score.score_competencias = score_competencias
    score.clasificacion = clasificacion
    score.resumen_analisis = _build_executive_summary(
        clasificacion=clasificacion,
        total=total,
        strengths=strengths,
        observations=observations,
        critical_flags=critical_flags,
        cv_word_count=cv_word_count,
        technical_hits=technical_hits,
        experience_hits=experience_hits,
        competency_hits=competency_hits,
    )
    score.fecha_calculo = datetime.utcnow()

    db.execute(delete(ScoreReason).where(ScoreReason.application_score_id == score.id))
    db.flush()

    for reason in reasons:
        reason.application_score_id = score.id
        db.add(reason)

    generate_or_update_application_insight(
        db=db,
        application_id=application_id,
        score_total=total,
    )

    return score
