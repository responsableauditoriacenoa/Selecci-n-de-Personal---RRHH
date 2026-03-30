from datetime import date

from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.core.security import get_password_hash
from app.models.enums import JobProfileStatus, QuestionType, UserRole, VacancyStatus
from app.models.job_profile import JobProfile, JobQuestion, JobRequirement
from app.models.organization import Area, Branch, Company
from app.models.user import User
from app.models.vacancy import Vacancy
from app.services.qr_service import build_public_url, generate_qr_token


def run_seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        admin = db.scalar(select(User).where(User.email == "admin@rrhh.com"))
        if not admin:
            admin = User(
                email="admin@rrhh.com",
                full_name="Administrador RRHH",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
            )
            db.add(admin)
            db.flush()
        else:
            admin.full_name = "Administrador RRHH"
            admin.hashed_password = get_password_hash("admin123")
            admin.role = UserRole.ADMIN
            admin.is_active = True
            db.flush()

        company = db.scalar(select(Company).where(Company.name == "Empresa Demo"))
        if not company:
            company = Company(name="Empresa Demo")
            db.add(company)
            db.flush()

        branch = db.scalar(select(Branch).where(Branch.name == "Casa Central"))
        if not branch:
            branch = Branch(company_id=company.id, name="Casa Central")
            db.add(branch)
            db.flush()

        area = db.scalar(select(Area).where(Area.name == "Tecnologia"))
        if not area:
            area = Area(name="Tecnologia")
            db.add(area)
            db.flush()

        profile = db.scalar(select(JobProfile).where(JobProfile.nombre_puesto == "Analista de Datos"))
        if not profile:
            profile = JobProfile(
                nombre_puesto="Analista de Datos",
                area_id=area.id,
                seniority="Semi Senior",
                modalidad="Hibrido",
                ubicacion="Buenos Aires",
                descripcion_general="Rol orientado a analisis de informacion de negocio.",
                version=1,
                estado=JobProfileStatus.ACTIVO,
                created_by=admin.id,
            )
            db.add(profile)
            db.flush()
            db.add(
                JobRequirement(
                    job_profile_id=profile.id,
                    tipo="tecnico",
                    nombre="SQL",
                    descripcion="Manejo de SQL intermedio",
                    obligatorio=True,
                    peso=20,
                    valor_esperado="sql",
                )
            )
            db.add(
                JobQuestion(
                    job_profile_id=profile.id,
                    pregunta="Tenes experiencia en modelado de datos?",
                    tipo_respuesta=QuestionType.BOOLEANO,
                    obligatoria=True,
                    eliminatoria=False,
                    peso=10,
                    orden=1,
                )
            )

        vacancy = db.scalar(select(Vacancy).where(Vacancy.titulo_publicacion == "Analista de Datos SR"))
        if not vacancy:
            token = generate_qr_token()
            vacancy = Vacancy(
                job_profile_id=profile.id,
                company_id=company.id,
                branch_id=branch.id,
                area_id=area.id,
                titulo_publicacion="Analista de Datos SR",
                descripcion_publicacion="Buscamos analista con foco en BI y SQL.",
                fecha_apertura=date.today(),
                fecha_cierre=date.today(),
                estado=VacancyStatus.ABIERTA,
                qr_token=token,
                public_url=build_public_url(token),
            )
            db.add(vacancy)

        db.commit()
        print("Seed ejecutado correctamente")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
