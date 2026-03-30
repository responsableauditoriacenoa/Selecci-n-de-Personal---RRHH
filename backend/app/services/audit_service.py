from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.user import User


def log_action(db: Session, user: User, entity: str, entity_id: int, action: str, detail: dict) -> None:
    entry = AuditLog(
        usuario=user.email,
        entidad=entity,
        entidad_id=entity_id,
        accion=action,
        detalle_json=jsonable_encoder(detail),
    )
    db.add(entry)
