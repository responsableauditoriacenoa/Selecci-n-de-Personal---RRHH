import json

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.schemas.public import PublicApplicationCreate, PublicApplicationResult
from app.services.application_service import process_public_application
from app.services.cv_parser import save_upload_file

router = APIRouter()


@router.post("/upload-cv")
def upload_cv(file: UploadFile = File(...)) -> dict[str, str]:
    settings = get_settings()
    path = save_upload_file(settings.upload_dir, file)
    return {"cv_file_path": path}


@router.post("/applications", response_model=PublicApplicationResult)
def create_public_application(
    token: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(...),
    ciudad: str = Form(...),
    provincia: str = Form(...),
    consentimiento_datos: bool = Form(...),
    fuente: str = Form("qr_publico"),
    linkedin: str | None = Form(None),
    answers_json: str = Form("[]"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> PublicApplicationResult:
    payload = PublicApplicationCreate(
        token=token,
        nombre=nombre,
        apellido=apellido,
        email=email,
        telefono=telefono,
        ciudad=ciudad,
        provincia=provincia,
        consentimiento_datos=consentimiento_datos,
        fuente=fuente,
        linkedin=linkedin,
        answers=[item for item in json.loads(answers_json)],
    )
    return process_public_application(db, payload, file)


@router.post("/intake", response_model=PublicApplicationResult)
def intake_public_application(
    token: str = Form(...),
    nombre: str = Form(...),
    apellido: str = Form(...),
    email: str = Form(...),
    telefono: str = Form(...),
    ciudad: str = Form(...),
    provincia: str = Form(...),
    consentimiento_datos: bool = Form(...),
    fuente: str = Form("qr_publico"),
    linkedin: str | None = Form(None),
    answers_json: str = Form("[]"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> PublicApplicationResult:
    payload = PublicApplicationCreate(
        token=token,
        nombre=nombre,
        apellido=apellido,
        email=email,
        telefono=telefono,
        ciudad=ciudad,
        provincia=provincia,
        consentimiento_datos=consentimiento_datos,
        fuente=fuente,
        linkedin=linkedin,
        answers=[item for item in json.loads(answers_json)],
    )
    return process_public_application(db, payload, file)
