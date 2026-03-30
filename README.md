# Plataforma RRHH - Reclutamiento y Preseleccion

Base profesional fullstack para gestion de vacantes, portal publico por QR, postulaciones, scoring explicable y backoffice interno de RRHH.

## Stack
- Backend: FastAPI + SQLAlchemy + PostgreSQL + Alembic + JWT
- Frontend: React + Vite + TypeScript
- Utilidades: parser CV (PDF/DOCX), generacion QR, trazabilidad con AuditLog
- Contenedores: docker-compose para PostgreSQL + backend + frontend

## Estructura
- backend/
  - app/
    - core/
    - models/
    - schemas/
    - routers/
      - admin/
      - public/
    - services/
    - repositories/
    - utils/
    - jobs/
  - alembic/
  - uploads/
- frontend/
  - src/
    - app/
    - pages/
      - admin/
      - public/
    - components/
    - layouts/
    - services/
    - hooks/
    - types/

## Arquitectura Objetivo
```text
proyecto-rrhh/
│
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── public/
│   │   │   │   ├── vacancy_public.py
│   │   │   │   └── applications_public.py
│   │   │   ├── admin/
│   │   │   │   ├── auth.py
│   │   │   │   ├── vacancies.py
│   │   │   │   ├── applications.py
│   │   │   │   └── reports.py
│   │   ├── services/
│   │   │   ├── cv_parser.py
│   │   │   ├── scoring_service.py
│   │   │   ├── compatibility_service.py
│   │   │   └── application_service.py
│   │   ├── models/
│   │   ├── schemas/
│   │   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── public/
│   │   │   │   ├── VacancyLanding.tsx
│   │   │   │   ├── ApplyForm.tsx
│   │   │   │   └── ApplySuccess.tsx
│   │   │   ├── admin/
│   │   │   │   ├── Login.tsx
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── Vacancies.tsx
│   │   │   │   └── CandidateDetail.tsx
│   │   ├── components/
│   │   └── services/
│
└── README.md
```

## Pipeline de Postulacion
Cuando el frontend publico recibe una postulacion, el backend ejecuta el flujo orquestado en `application_service.py`:
1. validacion de token y payload
2. guardado o actualizacion del candidato
3. guardado del CV
4. extraccion de texto del CV
5. scoring inicial
6. compatibilidad comparativa con la vacante
7. generacion de hallazgos
8. conclusion analitica final

## Endpoints Implementados
- Auth
  - POST /auth/login
  - GET /auth/me
- Organization
  - GET/POST /org/companies
  - GET/POST /org/branches
  - GET/POST /org/areas
- Job Profiles
  - GET /job-profiles
  - POST /job-profiles
  - GET /job-profiles/{id}
  - PUT /job-profiles/{id}
- Vacancies
  - GET /vacancies
  - POST /vacancies
  - GET /vacancies/{id}
  - PUT /vacancies/{id}
  - GET /vacancies/{id}/applications
  - GET /vacancies/{id}/qr
- Public
  - GET /public/vacancies
  - GET /public/vacancy/{token}
  - POST /public/upload-cv
  - POST /public/applications
  - POST /public/intake
- Applications
  - GET /applications/{id}
  - POST /applications/{id}/recalculate-score
  - POST /applications/{id}/change-status
  - POST /applications/{id}/notes
- Reports
  - GET /reports/dashboard

## Motor de Scoring (v1)
Reglas implementadas:
1. valida requisitos excluyentes (obligatorios)
2. puntua coincidencias CV vs requisitos
3. puntua respuestas de screening
4. registra motivos por tipo (fortaleza, observacion, descarte, alerta)
5. clasifica en:
   - 85-100: muy recomendado
   - 70-84: recomendado
   - 50-69: revisar
   - <50: baja compatibilidad

La explicabilidad se guarda en `application_scores` y `score_reasons`.

## Ejecucion Local

### Opcion A: Docker (recomendada)
1. En raiz del proyecto:
```bash
docker compose up --build
```
2. Backend: http://localhost:8000/docs
3. Frontend: http://localhost:5173

### Opcion B: Manual

#### 1) PostgreSQL
Crear DB `rrhh` y usuario/password segun `backend/.env`.

#### 2) Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Crear primera migracion y aplicar:
```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

Cargar seed inicial:
```bash
python -m app.jobs.seed
```

Levantar API:
```bash
uvicorn app.main:app --reload
```

#### 3) Frontend
```bash
cd frontend
npm install
npm run dev
```

#### 4) Portal Streamlit (opcional)
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
Configura `BACKEND_URL` en `.streamlit/secrets.toml` o usa el campo lateral dentro de la app.

## Credenciales Seed
- email: admin@rrhh.com
- password: admin123

## Pantallas Frontend Incluidas
Backoffice:
1. Login
2. Dashboard
3. Lista de descriptivos
4. Alta/edicion descriptivo
5. Lista de vacantes
6. Alta de vacante
7. Detalle de vacante + QR
8. Postulaciones por vacante
9. Ficha de postulacion/candidato
10. Vista score y motivos
11. Gestion de estados
12. Notas internas

Portal Publico:
1. Landing de vacante por token
2. Formulario de postulacion
3. Confirmacion

## Reglas de negocio contempladas
- Cada vacante tiene `qr_token` unico + `public_url`
- La vacante referencia un `job_profile_id` (version concreta)
- Postulaciones no se eliminan fisicamente (`is_deleted`)
- Descartes automaticos guardan motivos en `score_reasons`
- RRHH puede cambiar estado manualmente
- Scoring basado en reglas, sin IA externa
- Auditoria en `audit_logs` para acciones relevantes

## Proximos pasos recomendados
1. Agregar migracion inicial versionada dentro de `alembic/versions`
2. Integrar almacenamiento de archivos en S3 o MinIO
3. Agregar tests unitarios y de integracion
4. Expandir editor de requirements/questions en frontend
5. Sumar filtros y reportes avanzados en dashboard

## Deploy en Streamlit Cloud
- Main file path: `streamlit_app.py`
- Requirements file: `requirements.txt` en la raiz
- Secret recomendado: `BACKEND_URL = "https://tu-backend-publico.com"`

### Flujo recomendado para que funcione en Cloud
1. Desplegar backend publico (Render):
  - Usa `render.yaml` en la raiz del repo.
  - Render crea `rrhh-backend` + `rrhh-db`.
  - El backend corre migraciones y seed automaticamente con `backend/start.sh`.
2. Copiar URL publica del backend, por ejemplo:
  - `https://rrhh-backend.onrender.com`
3. Configurar Streamlit Cloud > App > Settings > Secrets:
  - `BACKEND_URL = "https://rrhh-backend.onrender.com"`
4. En Streamlit, usar `Cargar postulaciones`.
  - La app consulta `GET /public/vacancies`.
  - Muestra vacantes abiertas creadas en backoffice.
  - Las postulaciones se envian a `POST /public/intake`.
5. Verificacion final:
  - Backend: `https://rrhh-backend.onrender.com/health`
  - Streamlit: debe listar vacantes y permitir subir CV.
