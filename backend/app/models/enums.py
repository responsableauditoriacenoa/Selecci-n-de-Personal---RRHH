from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    RRHH = "rrhh"
    LIDER_SOLICITANTE = "lider_solicitante"


class JobProfileStatus(StrEnum):
    BORRADOR = "borrador"
    ACTIVO = "activo"
    ARCHIVADO = "archivado"


class VacancyStatus(StrEnum):
    ABIERTA = "abierta"
    PAUSADA = "pausada"
    CERRADA = "cerrada"


class QuestionType(StrEnum):
    TEXTO = "texto"
    BOOLEANO = "booleano"
    NUMERICO = "numerico"
    OPCION = "opcion"


class ApplicationStatus(StrEnum):
    POSTULADO = "postulado"
    EN_ANALISIS = "en_analisis"
    RECOMENDADO = "recomendado"
    REVISION_RRHH = "revision_rrhh"
    PRESELECCIONADO = "preseleccionado"
    ENTREVISTA_PENDIENTE = "entrevista_pendiente"
    ENTREVISTADO = "entrevistado"
    EVALUACION_FINAL = "evaluacion_final"
    RECHAZADO = "rechazado"
    CONTRATADO = "contratado"
    RESERVA = "reserva"


class ScoreReasonType(StrEnum):
    FORTALEZA = "fortaleza"
    OBSERVACION = "observacion"
    DESCARTE = "descarte"
    ALERTA = "alerta"
