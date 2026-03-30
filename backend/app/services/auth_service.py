from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.user import User


def login(db: Session, email: str, password: str) -> str:
    user = db.scalar(select(User).where(User.email == email))
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

    try:
        valid_password = verify_password(password, user.hashed_password)
    except Exception:
        valid_password = False

    if not valid_password:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

    return create_access_token(str(user.id))
