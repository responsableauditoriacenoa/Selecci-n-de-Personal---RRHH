from datetime import date

from sqlalchemy.orm import sessionmaker

from app.models.enums import JobProfileStatus, UserRole, VacancyStatus
from app.models.job_profile import JobProfile
from app.models.organization import Area, Branch, Company
from app.models.user import User
from app.models.vacancy import Vacancy


def _seed_public_vacancy(db_factory: sessionmaker, token: str = "token-demo") -> Vacancy:
    with db_factory() as db:
        company = Company(name="Autosol")
        area = Area(name="Comercial")
        db.add_all([company, area])
        db.flush()

        branch = Branch(company_id=company.id, name="Salta")
        user = User(
            email="admin@rrhh.com",
            full_name="Admin RRHH",
            hashed_password="hash",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add_all([branch, user])
        db.flush()

        profile = JobProfile(
            nombre_puesto="Vendedor",
            area_id=area.id,
            seniority="semi senior",
            modalidad="presencial",
            ubicacion="Salta",
            descripcion_general="Venta de unidades",
            version=1,
            estado=JobProfileStatus.ACTIVO,
            created_by=user.id,
        )
        db.add(profile)
        db.flush()

        vacancy = Vacancy(
            job_profile_id=profile.id,
            company_id=company.id,
            branch_id=branch.id,
            area_id=area.id,
            empresa="Autosol",
            localidad="Salta",
            area="Comercial",
            titulo_publicacion="Asesor comercial",
            descripcion_publicacion="Atencion comercial de clientes",
            descriptivo_puesto="Ventas y atencion",
            fecha_apertura=date.today(),
            fecha_cierre=date.today(),
            estado=VacancyStatus.ABIERTA,
            qr_token=token,
            public_url=f"http://localhost:5173/public/vacancy/{token}",
            descriptivo_texto_extraido="ventas comerciales",
        )
        db.add(vacancy)
        db.commit()
        db.refresh(vacancy)
        return vacancy


def test_public_vacancy_returns_location_fields(client_and_session):
    client, db_factory = client_and_session
    _seed_public_vacancy(db_factory, token="vac-123")

    response = client.get("/public/vacancy/vac-123")
    assert response.status_code == 200
    payload = response.json()
    assert payload["empresa"] == "Autosol"
    assert payload["localidad"] == "Salta"
    assert payload["area"] == "Comercial"


def test_public_vacancies_lists_available_tokens(client_and_session):
    client, db_factory = client_and_session
    _seed_public_vacancy(db_factory, token="vac-list-1")

    response = client.get("/public/vacancies")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) >= 1
    assert any(item["token"] == "vac-list-1" for item in items)


def test_public_intake_creates_application(client_and_session, monkeypatch):
    client, db_factory = client_and_session
    _seed_public_vacancy(db_factory, token="vac-intake")

    monkeypatch.setattr("app.services.application_service.save_upload_file", lambda *_: "uploads/test_cv.pdf")
    monkeypatch.setattr("app.services.application_service.extract_text", lambda *_: "experiencia comercial y ventas")

    response = client.post(
        "/public/intake",
        data={
            "token": "vac-intake",
            "nombre": "Ana",
            "apellido": "Lopez",
            "email": "ana.lopez@test.com",
            "telefono": "388-111111",
            "ciudad": "Salta",
            "provincia": "Salta",
            "linkedin": "",
            "consentimiento_datos": "true",
            "fuente": "qr_publico",
            "answers_json": "[]",
        },
        files={"file": ("cv.pdf", b"fake-pdf", "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["application_id"] > 0
    assert body["message"] == "Postulacion enviada con analisis inicial"
    assert isinstance(body["score_total"], int)
    assert body["clasificacion"]
