from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.models.application import Application
from app.models.enums import JobProfileStatus, QuestionType, UserRole, VacancyStatus
from app.models.job_profile import JobProfile, JobQuestion, JobRequirement
from app.models.organization import Area, Branch, Company
from app.models.scoring import ApplicationScore
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
    assert body["message"] == "Postulacion enviada correctamente"
    assert "score_total" not in body
    assert "clasificacion" not in body
    assert "resumen_analisis" not in body


def test_public_intake_uses_configurable_scoring_rules(client_and_session, monkeypatch):
    client, db_factory = client_and_session
    vacancy = _seed_public_vacancy(db_factory, token="vac-score-config")

    with db_factory() as db:
        profile = db.get(JobProfile, vacancy.job_profile_id)
        profile.scoring_dimensions = [
            {"key": "formacion", "label": "Formación", "weight": 40},
            {"key": "experiencia", "label": "Experiencia", "weight": 30},
            {"key": "condiciones", "label": "Condiciones", "weight": 30},
        ]
        db.add_all(
            [
                JobRequirement(
                    job_profile_id=profile.id,
                    tipo="formacion",
                    dimension="formacion",
                    nombre="Secundario completo",
                    descripcion="Secundario completo",
                    obligatorio=True,
                    peso=10,
                    valor_esperado="secundario completo",
                    keywords=["secundario completo"],
                    match_mode="any",
                    failure_mode="revisar",
                ),
                JobRequirement(
                    job_profile_id=profile.id,
                    tipo="experiencia",
                    dimension="experiencia",
                    nombre="Experiencia en recepción",
                    descripcion="Experiencia en recepción",
                    obligatorio=True,
                    peso=10,
                    valor_esperado="recepcion",
                    keywords=["recepcion", "recepcionista"],
                    match_mode="any",
                    failure_mode="revisar",
                ),
                JobQuestion(
                    job_profile_id=profile.id,
                    pregunta="¿Tenés disponibilidad full time?",
                    dimension="condiciones",
                    tipo_respuesta=QuestionType.BOOLEANO,
                    obligatoria=True,
                    eliminatoria=True,
                    peso=10,
                    orden=1,
                    opciones=[],
                    respuestas_aceptadas=["si"],
                    failure_mode="descarte",
                ),
            ]
        )
        db.commit()

    monkeypatch.setattr("app.services.application_service.save_upload_file", lambda *_: "uploads/test_cv.pdf")
    monkeypatch.setattr("app.services.application_service.extract_text", lambda *_: "secundario completo y experiencia en recepcion")

    success_response = client.post(
        "/public/intake",
        data={
            "token": "vac-score-config",
            "nombre": "Laura",
            "apellido": "Diaz",
            "email": "laura.diaz@test.com",
            "telefono": "388-222222",
            "ciudad": "Salta",
            "provincia": "Salta",
            "linkedin": "",
            "consentimiento_datos": "true",
            "fuente": "qr_publico",
            "answers_json": "[{\"job_question_id\": 1, \"respuesta\": \"si\"}]",
        },
        files={"file": ("cv.pdf", b"fake-pdf", "application/pdf")},
    )

    assert success_response.status_code == 200

    reject_response = client.post(
        "/public/intake",
        data={
            "token": "vac-score-config",
            "nombre": "Mario",
            "apellido": "Perez",
            "email": "mario.perez@test.com",
            "telefono": "388-333333",
            "ciudad": "Salta",
            "provincia": "Salta",
            "linkedin": "",
            "consentimiento_datos": "true",
            "fuente": "qr_publico",
            "answers_json": "[{\"job_question_id\": 1, \"respuesta\": \"no\"}]",
        },
        files={"file": ("cv.pdf", b"fake-pdf", "application/pdf")},
    )

    assert reject_response.status_code == 200

    with db_factory() as db:
        applications = db.scalars(select(Application).order_by(Application.id.asc())).all()
        success_score = db.scalar(select(ApplicationScore).where(ApplicationScore.application_id == applications[0].id))
        reject_score = db.scalar(select(ApplicationScore).where(ApplicationScore.application_id == applications[1].id))

        assert success_score is not None
        assert success_score.score_total == 100
        assert success_score.clasificacion == "muy recomendado"
        assert [item["score"] for item in success_score.dimension_scores] == [40, 30, 30]

        assert reject_score is not None
        assert reject_score.score_total == 70
        assert reject_score.clasificacion == "baja compatibilidad"
        assert any(item["key"] == "condiciones" and item["score"] == 0 for item in reject_score.dimension_scores)
