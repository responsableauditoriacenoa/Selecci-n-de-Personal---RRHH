from pathlib import Path
from uuid import uuid4

from docx import Document
from fastapi import HTTPException, UploadFile
from pypdf import PdfReader


ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def save_upload_file(upload_dir: str, file: UploadFile) -> str:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Formato no soportado. Use PDF o DOCX")

    target_dir = Path(upload_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    safe_stem = Path(file.filename or "cv").stem.replace(" ", "_")
    target_path = target_dir / f"{safe_stem}_{uuid4().hex}{suffix}"

    with target_path.open("wb") as buffer:
        buffer.write(file.file.read())

    return str(target_path)


def extract_text(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return extract_pdf_text(file_path)
    if suffix == ".docx":
        return extract_docx_text(file_path)
    raise HTTPException(status_code=400, detail="Formato no soportado")


def extract_pdf_text(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"No se pudo leer el PDF cargado: {exc}")


def extract_docx_text(file_path: str) -> str:
    try:
        document = Document(file_path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"No se pudo leer el DOCX cargado: {exc}")
