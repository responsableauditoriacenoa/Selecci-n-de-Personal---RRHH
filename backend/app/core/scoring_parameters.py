SCORING_THRESHOLDS = {
    "muy_recomendado": 85,
    "recomendado": 70,
    "revisar": 50,
}

SCORING_WEIGHTS = {
    "formacion": 20,
    "experiencia": 25,
    "tecnico": 30,
    "preguntas": 20,
    "competencias": 5,
}

KEYWORDS_BY_CLUSTER = {
    "tecnico": [
        "sql",
        "python",
        "power bi",
        "excel",
        "etl",
        "tableau",
        "analytics",
        "modelado de datos",
    ],
    "experiencia": [
        "liderazgo",
        "gestion",
        "implementacion",
        "proyecto",
        "equipo",
        "stakeholders",
        "kpi",
    ],
    "competencias": [
        "comunicacion",
        "proactividad",
        "planificacion",
        "negociacion",
        "orientacion a resultados",
        "adaptabilidad",
    ],
}

RECOMMENDATION_MATRIX = {
    "muy recomendado": "Avanzar a entrevista tecnica y validacion de ajuste cultural en esta semana.",
    "recomendado": "Pasar a revision tecnica prioritaria y validar profundidad de experiencia declarada.",
    "revisar": "Mantener en pipeline de revision con entrevista de calibracion y chequeo de brechas.",
    "baja compatibilidad": "Continuar solo si no hay perfiles superiores; requerir validacion manual RRHH.",
}
