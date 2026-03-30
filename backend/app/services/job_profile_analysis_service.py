from fastapi import UploadFile

from app.models.job_profile import JobProfile
from app.services.cv_parser import extract_text, save_upload_file


def _classification(score: int) -> str:
    if score >= 75:
        return "alta compatibilidad"
    if score >= 50:
        return "compatibilidad media"
    return "baja compatibilidad"


def _recommendation(score: int, mandatory_gaps: int) -> str:
    if score >= 75 and mandatory_gaps == 0:
        return "Recomendacion RRHH: perfil apto para avanzar a evaluacion formal."
    if score >= 50:
        return "Recomendacion RRHH: continuar en revision, validando profundidad tecnica y contexto laboral."
    if mandatory_gaps > 0:
        return "Recomendacion RRHH: revisar con criterio humano antes de una decision de descarte."
    return "Recomendacion RRHH: mantener como alternativa secundaria para la vacante actual."


def analyze_document_against_job_profile(job_profile: JobProfile, file: UploadFile, upload_dir: str) -> dict:
    file_path = save_upload_file(upload_dir, file)
    extracted_text = extract_text(file_path).lower()

    coincidencias_clave: list[str] = []
    alertas: list[str] = []

    score = 0
    max_score = 0
    mandatory_gaps = 0

    # Requisitos con peso explicito del descriptivo.
    for req in job_profile.requirements:
        weight = max(req.peso, 5)
        max_score += weight
        valor_esperado = (req.valor_esperado or "").strip().lower()

        if valor_esperado and valor_esperado in extracted_text:
            score += weight
            coincidencias_clave.append(f"Evidencia compatible con requisito: {req.nombre} ({valor_esperado}).")
        elif req.obligatorio:
            alertas.append(f"No se detecta evidencia del requisito obligatorio: {req.nombre}.")
            mandatory_gaps += 1
            score -= min(15, weight)

    contexto = [
        job_profile.nombre_puesto,
        job_profile.seniority,
        job_profile.modalidad,
        job_profile.ubicacion,
    ]

    for item in contexto:
        term = (item or "").strip().lower()
        if not term:
            continue
        max_score += 8
        if term in extracted_text:
            score += 8
            coincidencias_clave.append(f"Coincidencia de contexto del puesto: {item}.")

    total = int(max(min((score / max(max_score, 1)) * 100, 100), 0))
    clasificacion = _classification(total)

    comentario = (
        f"Informe de compatibilidad documental: {clasificacion} ({total}/100). "
        f"Se registran {len(coincidencias_clave)} coincidencias clave y {len(alertas)} alertas de revision. "
        "Analisis generado con reglas del descriptivo para soporte de decision en preseleccion. "
        f"{_recommendation(total, mandatory_gaps)}"
    )

    return {
        "score_compatibilidad": total,
        "clasificacion": clasificacion,
        "comentario_analisis": comentario,
        "coincidencias_clave": coincidencias_clave,
        "alertas": alertas,
    }
