from collections import defaultdict
from datetime import datetime
import re
import unicodedata

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.scoring_parameters import RECOMMENDATION_MATRIX, SCORING_THRESHOLDS
from app.models.application import Application, ApplicationAnswer
from app.models.candidate import Candidate
from app.models.enums import QuestionType, ScoreReasonType
from app.models.job_profile import JobProfile, JobQuestion, JobRequirement
from app.models.scoring import ApplicationScore, ScoreReason
from app.models.vacancy import Vacancy
from app.services.comparative_analysis_service import generate_or_update_application_insight

NEGATIVE_ANSWERS = {"no", "false", "0", "n", "negativo"}
POSITIVE_ANSWERS = {"si", "sí", "yes", "true", "1", "afirmativo"}
DIMENSION_LABELS = {
    "formacion": "Formación",
    "experiencia": "Experiencia requerida",
    "tecnico": "Habilidades técnicas",
    "competencias": "Competencias blandas",
    "condiciones": "Condiciones",
    "valor_agregado": "Valor agregado",
    "preguntas": "Preguntas filtro",
    "filtro": "Requisitos excluyentes",
    "general": "Compatibilidad general",
}
KEYWORD_SYNONYMS = {
    "recepcion": ["recepcion", "recepcionista", "front desk", "recepcion de clientes"],
    "atencion al cliente": ["atencion al cliente", "atencion al publico", "customer service", "trato con clientes"],
    "atencion telefonica": ["atencion telefonica", "llamadas", "call center", "conmutador"],
    "agenda": ["agenda", "turnos", "citas", "calendario"],
    "crm": ["crm", "salesforce", "sistema administrativo", "sistema de gestion"],
    "excel": ["excel", "planillas", "hojas de calculo"],
    "concesionaria": ["concesionaria", "automotriz", "taller", "postventa"],
    "full time": ["full time", "jornada completa", "disponibilidad horaria", "horario completo"],
    "secundario completo": ["secundario completo", "bachiller", "educacion secundaria completa"],
    "pc": ["pc", "computadora", "office", "excel", "word", "outlook"],
}


def _strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _normalize_text(value: str) -> str:
    cleaned = _strip_accents((value or "").lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def _normalize_key(value: str) -> str:
    normalized = _normalize_text(value)
    return re.sub(r"[^a-z0-9]+", "_", normalized).strip("_") or "general"


def _split_keywords(value: str) -> list[str]:
    if not value:
        return []
    parts = re.split(r"[\n,;|/]+", value)
    items: list[str] = []
    for part in parts:
        candidate = _normalize_text(part)
        if candidate:
            items.append(candidate)
    return items


def _expand_keywords(*values: str) -> list[str]:
    raw: list[str] = []
    for value in values:
        raw.extend(_split_keywords(value))
        normalized_value = _normalize_text(value)
        if normalized_value:
            raw.append(normalized_value)

    expanded: list[str] = []
    seen: set[str] = set()
    for item in raw:
        candidates = [item]
        for key, synonyms in KEYWORD_SYNONYMS.items():
            if key in item or item in synonyms:
                candidates.extend(_normalize_text(entry) for entry in synonyms)
        candidates.extend(token for token in re.findall(r"[a-z0-9]{3,}", item) if token not in {"con", "para", "del", "las", "los"})
        for candidate in candidates:
            if candidate and candidate not in seen:
                seen.add(candidate)
                expanded.append(candidate)
    return expanded


def _contains(text: str, token: str) -> bool:
    return bool(token) and token in text


def _parse_number(value: str) -> float | None:
    if value is None:
        return None
    match = re.search(r"-?\d+(?:[\.,]\d+)?", str(value))
    if not match:
        return None
    return float(match.group(0).replace(",", "."))


def _humanize_dimension(key: str) -> str:
    normalized = _normalize_key(key)
    if normalized in DIMENSION_LABELS:
        return DIMENSION_LABELS[normalized]
    return normalized.replace("_", " ").title()


def _normalize_dimensions(profile: JobProfile | None, requirements: list[JobRequirement], questions: list[JobQuestion]) -> list[dict[str, object]]:
    configured = list((profile.scoring_dimensions if profile else []) or [])
    dimensions: list[dict[str, object]] = []

    for item in configured:
        key = _normalize_key(str(item.get("key", "")))
        weight = max(int(item.get("weight", 0) or 0), 0)
        if not key or weight <= 0:
            continue
        dimensions.append({"key": key, "label": str(item.get("label") or _humanize_dimension(key)), "weight": weight})

    used_dimension_weights: dict[str, int] = defaultdict(int)
    for req in requirements:
        used_dimension_weights[_normalize_key(req.dimension or req.tipo or "general")] += max(int(req.peso or 0), 0)
    for question in questions:
        used_dimension_weights[_normalize_key(question.dimension or "preguntas")] += max(int(question.peso or 0), 0)

    known_keys = {item["key"] for item in dimensions}
    for key, weight in used_dimension_weights.items():
        if key not in known_keys and weight > 0:
            dimensions.append({"key": key, "label": _humanize_dimension(key), "weight": weight})

    if not dimensions:
        dimensions = [{"key": "general", "label": "Compatibilidad general", "weight": 100}]

    total_weight = sum(int(item["weight"]) for item in dimensions)
    base_weights = [int(item["weight"]) for item in dimensions]
    raw_scores = [(weight / max(total_weight, 1)) * 100 for weight in base_weights]
    normalized_weights = [int(value) for value in raw_scores]
    remaining = 100 - sum(normalized_weights)
    order = sorted(range(len(raw_scores)), key=lambda index: (raw_scores[index] - normalized_weights[index]), reverse=True)
    for index in order[:remaining]:
        normalized_weights[index] += 1

    for index, item in enumerate(dimensions):
        item["weight"] = normalized_weights[index]
    return dimensions


def _legacy_dimension_scores(dimension_scores: list[dict[str, int]]) -> dict[str, int]:
    score_map = {item["key"]: int(item["score"]) for item in dimension_scores}
    return {
        "score_formacion": score_map.get("formacion", 0),
        "score_experiencia": score_map.get("experiencia", 0),
        "score_tecnico": score_map.get("tecnico", 0),
        "score_preguntas": score_map.get("preguntas", score_map.get("filtro", 0)),
        "score_competencias": score_map.get("competencias", 0),
    }


def _build_executive_summary(
    clasificacion: str,
    total: int,
    strengths: int,
    observations: int,
    critical_flags: int,
    dimension_scores: list[dict[str, int]],
) -> str:
    strongest = sorted(dimension_scores, key=lambda item: (-item["score"], item["label"]))[:3]
    weakest = sorted(dimension_scores, key=lambda item: (item["score"], item["label"]))[:2]
    strongest_text = ", ".join(f"{item['label']} {item['score']}/{item['weight']}" for item in strongest) or "sin tramos destacados"
    weakest_text = ", ".join(f"{item['label']} {item['score']}/{item['weight']}" for item in weakest) or "sin brechas marcadas"
    return (
        f"Dictamen tecnico RRHH: {clasificacion} ({total}/100). "
        f"Se registran {strengths} fortalezas, {observations} observaciones y {critical_flags} alertas o descartes. "
        f"Dimensiones mas fuertes: {strongest_text}. "
        f"Dimensiones a validar: {weakest_text}. "
        f"Recomendacion operativa: {RECOMMENDATION_MATRIX[clasificacion]}"
    )


def _reason_type_for_failure(failure_mode: str, *, eliminatory: bool = False) -> ScoreReasonType:
    normalized = _normalize_key(failure_mode)
    if eliminatory or normalized == "descarte":
        return ScoreReasonType.DESCARTE
    if normalized == "alerta":
        return ScoreReasonType.ALERTA
    return ScoreReasonType.OBSERVACION


def _evaluate_requirement(req: JobRequirement, evidence_text: str) -> tuple[bool, list[str]]:
    keywords = list(req.keywords or []) or _expand_keywords(req.valor_esperado, req.nombre, req.descripcion)
    matches = [keyword for keyword in keywords if _contains(evidence_text, _normalize_text(keyword))]
    mode = _normalize_key(req.match_mode)
    matched = all(_contains(evidence_text, _normalize_text(keyword)) for keyword in keywords) if keywords and mode == "all" else bool(matches)
    return matched, matches


def _evaluate_question(question: JobQuestion, answer: str) -> tuple[bool, str]:
    normalized_answer = _normalize_text(answer)
    accepted = [_normalize_text(item) for item in (question.respuestas_aceptadas or []) if str(item).strip()]

    if question.tipo_respuesta == QuestionType.BOOLEANO:
        if not accepted:
            accepted = ["si"]
        return normalized_answer in accepted or (normalized_answer in POSITIVE_ANSWERS and any(item in {"si", "yes", "true", "1"} for item in accepted)), normalized_answer

    if question.tipo_respuesta == QuestionType.NUMERICO:
        current = _parse_number(normalized_answer)
        threshold = _parse_number(accepted[0]) if accepted else 0
        return current is not None and threshold is not None and current >= threshold, normalized_answer

    if not accepted:
        return bool(normalized_answer), normalized_answer

    return any(item == normalized_answer or item in normalized_answer for item in accepted), normalized_answer


def _classification(total: int, discard_count: int, alert_count: int) -> str:
    if discard_count > 0:
        return "baja compatibilidad"
    if total >= SCORING_THRESHOLDS["muy_recomendado"] and alert_count == 0:
        return "muy recomendado"
    if total >= SCORING_THRESHOLDS["recomendado"] and alert_count <= 1:
        return "recomendado"
    if total >= SCORING_THRESHOLDS["revisar"]:
        return "revisar"
    return "baja compatibilidad"


def recalculate_application_score(db: Session, application_id: int) -> ApplicationScore:
    application = db.get(Application, application_id)
    if not application:
        raise ValueError("Application not found")

    vacancy = db.get(Vacancy, application.vacancy_id)
    candidate = db.get(Candidate, application.candidate_id) if application.candidate_id else None
    requirements: list[JobRequirement] = []
    questions: list[JobQuestion] = []
    profile = db.get(JobProfile, vacancy.job_profile_id) if vacancy and vacancy.job_profile_id else None
    if profile:
        requirements = db.scalars(select(JobRequirement).where(JobRequirement.job_profile_id == profile.id)).all()
        questions = db.scalars(select(JobQuestion).where(JobQuestion.job_profile_id == profile.id)).all()
    answers = db.scalars(select(ApplicationAnswer).where(ApplicationAnswer.application_id == application_id)).all()

    candidate_text = " ".join(
        value for value in [candidate.ciudad if candidate else "", candidate.provincia if candidate else "", candidate.linkedin if candidate else ""] if value
    )
    cv_text = _normalize_text(application.cv_text_extracted or "")
    screening_text = " ".join(_normalize_text(answer.respuesta) for answer in answers)
    evidence_text = _normalize_text(f"{cv_text} {screening_text} {candidate_text}")

    dimensions = _normalize_dimensions(profile, requirements, questions)
    dimension_possible: dict[str, int] = defaultdict(int)
    dimension_achieved: dict[str, int] = defaultdict(int)
    reasons: list[ScoreReason] = []

    for req in requirements:
        dimension_key = _normalize_key(req.dimension or req.tipo or "general")
        weight = max(int(req.peso or 0), 0)
        if weight > 0:
            dimension_possible[dimension_key] += weight

        matched, matches = _evaluate_requirement(req, evidence_text)
        if matched:
            if weight > 0:
                dimension_achieved[dimension_key] += weight
            detail = f"Palabras clave detectadas: {', '.join(matches[:4])}." if matches else ""
            reasons.append(
                ScoreReason(
                    tipo=ScoreReasonType.FORTALEZA,
                    descripcion=f"Cumple criterio definido por RRHH: {req.nombre}. {detail}".strip(),
                    impacto=weight,
                )
            )
            continue

        if req.obligatorio:
            reasons.append(
                ScoreReason(
                    tipo=_reason_type_for_failure(req.failure_mode),
                    descripcion=f"No se pudo validar el requisito obligatorio: {req.nombre}.",
                    impacto=-max(weight, 10),
                )
            )
        else:
            reasons.append(
                ScoreReason(
                    tipo=ScoreReasonType.OBSERVACION,
                    descripcion=f"No se detecta evidencia suficiente para el criterio deseable: {req.nombre}.",
                    impacto=-max(weight // 2, 2),
                )
            )

    answers_map = {answer.job_question_id: answer.respuesta.strip() for answer in answers}
    for question in questions:
        dimension_key = _normalize_key(question.dimension or "preguntas")
        weight = max(int(question.peso or 0), 0)
        if weight > 0:
            dimension_possible[dimension_key] += weight

        raw_answer = answers_map.get(question.id, "")
        if not raw_answer:
            if question.obligatoria:
                reasons.append(
                    ScoreReason(
                        tipo=_reason_type_for_failure(question.failure_mode, eliminatory=question.eliminatoria),
                        descripcion=f"Falta respuesta en pregunta de screening: {question.pregunta}",
                        impacto=-max(weight, 8),
                    )
                )
            continue

        is_favorable, normalized_answer = _evaluate_question(question, raw_answer)
        if is_favorable:
            if weight > 0:
                dimension_achieved[dimension_key] += weight
            reasons.append(
                ScoreReason(
                    tipo=ScoreReasonType.FORTALEZA,
                    descripcion=f"Respuesta alineada al filtro definido: {question.pregunta}",
                    impacto=weight,
                )
            )
        else:
            reason_type = _reason_type_for_failure(question.failure_mode, eliminatory=question.eliminatoria)
            reasons.append(
                ScoreReason(
                    tipo=reason_type,
                    descripcion=f"Respuesta no alineada al filtro definido: {question.pregunta}. Valor informado: {normalized_answer or raw_answer}.",
                    impacto=-max(weight, 8),
                )
            )

    dimension_scores: list[dict[str, int]] = []
    for dimension in dimensions:
        key = str(dimension["key"])
        weight = int(dimension["weight"])
        possible = dimension_possible.get(key, 0)
        achieved = min(dimension_achieved.get(key, 0), possible) if possible else 0
        score_value = int(round((achieved / possible) * weight)) if possible > 0 else 0
        dimension_scores.append(
            {
                "key": key,
                "label": str(dimension["label"]),
                "weight": weight,
                "score": score_value,
                "achieved_weight": achieved,
                "possible_weight": possible,
            }
        )

    total = max(min(sum(item["score"] for item in dimension_scores), 100), 0)
    discard_count = len([reason for reason in reasons if reason.tipo == ScoreReasonType.DESCARTE])
    alert_count = len([reason for reason in reasons if reason.tipo == ScoreReasonType.ALERTA])
    clasificacion = _classification(total, discard_count, alert_count)

    strengths = len([reason for reason in reasons if reason.tipo == ScoreReasonType.FORTALEZA])
    observations = len([reason for reason in reasons if reason.tipo == ScoreReasonType.OBSERVACION])
    critical_flags = len([reason for reason in reasons if reason.tipo in {ScoreReasonType.DESCARTE, ScoreReasonType.ALERTA}])

    legacy_scores = _legacy_dimension_scores(dimension_scores)

    score = db.scalar(select(ApplicationScore).where(ApplicationScore.application_id == application_id))
    if not score:
        score = ApplicationScore(application_id=application_id, clasificacion=clasificacion, resumen_analisis="")
        db.add(score)
        db.flush()

    score.score_total = total
    score.score_formacion = legacy_scores["score_formacion"]
    score.score_experiencia = legacy_scores["score_experiencia"]
    score.score_tecnico = legacy_scores["score_tecnico"]
    score.score_preguntas = legacy_scores["score_preguntas"]
    score.score_competencias = legacy_scores["score_competencias"]
    score.dimension_scores = dimension_scores
    score.clasificacion = clasificacion
    score.resumen_analisis = _build_executive_summary(
        clasificacion=clasificacion,
        total=total,
        strengths=strengths,
        observations=observations,
        critical_flags=critical_flags,
        dimension_scores=dimension_scores,
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