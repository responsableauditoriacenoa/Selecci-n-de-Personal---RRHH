from __future__ import annotations

import json
import os
from typing import Any

import requests
import streamlit as st


st.set_page_config(
    page_title="Portal de Postulacion RRHH",
    page_icon="📄",
    layout="centered",
)


API_TIMEOUT = 30


CSS = """
<style>
    .stApp {
        background: radial-gradient(circle at top, #eff6ff 0%, #f8fafc 38%, #eef2ff 100%);
    }
    .hero-card, .section-card, .success-card {
        background: #ffffff;
        border: 1px solid #dbe4f0;
        border-radius: 20px;
        padding: 1.25rem 1.35rem;
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
    }
    .brand-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.45rem 0.8rem;
        border-radius: 999px;
        background: #eff6ff;
        color: #1d4ed8;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 0.9rem;
    }
    .page-title {
        font-size: 2rem;
        line-height: 1.1;
        font-weight: 800;
        color: #0f172a;
        margin: 0 0 0.35rem 0;
    }
    .page-subtitle {
        color: #475569;
        font-size: 0.96rem;
        line-height: 1.6;
        margin: 0;
    }
    .pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    .info-pill {
        display: inline-flex;
        align-items: center;
        padding: 0.42rem 0.72rem;
        border-radius: 999px;
        background: #f8fafc;
        border: 1px solid #dbe4f0;
        color: #0f172a;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .section-title {
        font-size: 1rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .section-subtitle {
        color: #64748b;
        font-size: 0.88rem;
        margin-bottom: 0.9rem;
    }
    .question-box {
        padding: 0.8rem 0.9rem;
        border-radius: 14px;
        border: 1px solid #dbe4f0;
        background: #f8fafc;
        margin-bottom: 0.55rem;
        color: #334155;
        font-size: 0.9rem;
    }
    .success-card {
        border-color: #bbf7d0;
        background: linear-gradient(180deg, #ffffff 0%, #f0fdf4 100%);
    }
    .score-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 1rem;
        font-weight: 800;
        color: #166534;
        background: #dcfce7;
        border: 1px solid #bbf7d0;
        border-radius: 999px;
        padding: 0.5rem 0.8rem;
        margin: 0.5rem 0 0.75rem 0;
    }
    .small-note {
        color: #64748b;
        font-size: 0.8rem;
        line-height: 1.5;
    }
</style>
"""


st.markdown(CSS, unsafe_allow_html=True)


def _get_secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, default)
        return str(value).strip()
    except Exception:
        return default


def _is_local_backend_url(url: str) -> bool:
    normalized = (url or "").lower().strip()
    return normalized.startswith("http://127.0.0.1") or normalized.startswith("http://localhost")


def _friendly_backend_error(exc: requests.RequestException, backend_url: str) -> str:
    if _is_local_backend_url(backend_url):
        return (
            "No se pudo conectar con el backend porque estas usando una URL local (127.0.0.1/localhost). "
            "En Streamlit Cloud debes usar la URL publica de tu API, por ejemplo https://tu-backend.onrender.com"
        )
    return f"No se pudo conectar con el backend: {exc}"


DEFAULT_BACKEND_URL = os.getenv("BACKEND_URL", _get_secret("BACKEND_URL", "http://127.0.0.1:8000")).rstrip("/")
DEFAULT_TOKEN = os.getenv("DEFAULT_TOKEN", _get_secret("DEFAULT_TOKEN", "")).strip()


if "vacancy_data" not in st.session_state:
    st.session_state.vacancy_data = None
if "application_result" not in st.session_state:
    st.session_state.application_result = None
if "vacancy_options" not in st.session_state:
    st.session_state.vacancy_options = []


query_params = st.query_params
query_token = str(query_params.get("token", DEFAULT_TOKEN)).strip() if query_params else DEFAULT_TOKEN
query_backend = str(query_params.get("backend", DEFAULT_BACKEND_URL)).strip() if query_params else DEFAULT_BACKEND_URL


def _query_param_value(name: str) -> str:
    value = st.query_params.get(name, "")
    if isinstance(value, list):
        return str(value[0]).strip() if value else ""
    return str(value).strip()


def _set_query_param_if_changed(name: str, value: str) -> None:
    new_value = str(value).strip()
    if _query_param_value(name) != new_value:
        st.query_params[name] = new_value


with st.sidebar:
    st.header("Configuracion")
    backend_url = st.text_input("Backend URL", value=query_backend or DEFAULT_BACKEND_URL, help="URL publica de tu API FastAPI")
    typed_token = st.text_input("Token de vacante (opcional)", value=query_token)
    auto_fetch = st.button("Cargar postulaciones", use_container_width=True)
    st.caption("En Streamlit Cloud conviene definir BACKEND_URL en Secrets.")
    if _is_local_backend_url(backend_url):
        st.warning("127.0.0.1 solo funciona en local. En Streamlit Cloud usa la URL publica del backend.")


def fetch_vacancy(base_url: str, token: str) -> dict[str, Any] | None:
    if not base_url or not token:
        return None
    response = requests.get(f"{base_url.rstrip('/')}/public/vacancy/{token}", timeout=API_TIMEOUT)
    response.raise_for_status()
    return response.json()


def fetch_public_vacancies(base_url: str) -> list[dict[str, Any]]:
    response = requests.get(f"{base_url.rstrip('/')}/public/vacancies", timeout=API_TIMEOUT)
    response.raise_for_status()
    return response.json()


def submit_application(base_url: str, form_data: dict[str, str], file_name: str, file_bytes: bytes, mime_type: str) -> dict[str, Any]:
    response = requests.post(
        f"{base_url.rstrip('/')}/public/intake",
        data=form_data,
        files={"file": (file_name, file_bytes, mime_type)},
        timeout=API_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


if auto_fetch and backend_url:
    try:
        st.session_state.vacancy_options = fetch_public_vacancies(backend_url)
        st.session_state.vacancy_data = None
        st.session_state.application_result = None
    except requests.HTTPError as exc:
        st.error(f"No se pudieron obtener vacantes: {exc.response.text}")
    except requests.RequestException as exc:
        st.error(_friendly_backend_error(exc, backend_url))

selected_token = ""
vacancy_options = st.session_state.vacancy_options
if vacancy_options:
    labels: list[str] = []
    tokens_by_label: dict[str, str] = {}
    for item in vacancy_options:
        empresa = item.get("empresa") or "Empresa"
        localidad = item.get("localidad") or "Localidad"
        area = item.get("area") or "Area"
        titulo = item.get("titulo_publicacion") or "Vacante"
        token = item.get("token") or ""
        label = f"{titulo} - {empresa} - {localidad} - {area}"
        labels.append(label)
        tokens_by_label[label] = token

    with st.sidebar:
        selected_label = st.selectbox("Postulaciones disponibles", options=labels, index=0)
        selected_token = tokens_by_label.get(selected_label, "")

vacancy_token = selected_token or typed_token

if backend_url and vacancy_token:
    try:
        st.session_state.vacancy_data = fetch_vacancy(backend_url, vacancy_token)
        _set_query_param_if_changed("token", vacancy_token)
        _set_query_param_if_changed("backend", backend_url)
    except requests.HTTPError as exc:
        if st.session_state.vacancy_data is None:
            st.error(f"No se pudo cargar la vacante seleccionada: {exc.response.text}")
    except requests.RequestException as exc:
        if st.session_state.vacancy_data is None:
            st.error(_friendly_backend_error(exc, backend_url))


vacancy = st.session_state.vacancy_data
result = st.session_state.application_result


st.markdown('<div class="hero-card">', unsafe_allow_html=True)
st.markdown('<div class="brand-pill">Portal de empleo RRHH</div>', unsafe_allow_html=True)
st.markdown('<h1 class="page-title">Postulacion online</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="page-subtitle">Publica esta URL para que el candidato vea la vacante, cargue su CV y envíe su postulacion directamente al backend.</p>',
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

if result:
    st.markdown('<div class="success-card">', unsafe_allow_html=True)
    st.success("Postulacion enviada correctamente")
    st.markdown(f"**ID de postulacion:** {result.get('application_id', '-')}")
    score_total = result.get("score_total", 0)
    clasificacion = result.get("clasificacion", "sin clasificacion")
    st.markdown(f'<div class="score-chip">Score {score_total}/100 · {clasificacion}</div>', unsafe_allow_html=True)
    if result.get("resumen_analisis"):
        st.write(result["resumen_analisis"])
    if st.button("Enviar otra postulacion", use_container_width=True):
        st.session_state.application_result = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

if not vacancy:
    st.info("Haz clic en Cargar postulaciones para ver vacantes disponibles o usa un token manual.")
    st.stop()


st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown(f'<div class="section-title">{vacancy.get("titulo_publicacion", "Vacante")}</div>', unsafe_allow_html=True)
if vacancy.get("descripcion_publicacion"):
    st.markdown(f'<div class="section-subtitle">{vacancy.get("descripcion_publicacion")}</div>', unsafe_allow_html=True)

pill_parts = []
for value in [vacancy.get("empresa"), vacancy.get("localidad"), vacancy.get("area")]:
    if value:
        pill_parts.append(f'<span class="info-pill">{value}</span>')
if pill_parts:
    st.markdown(f'<div class="pill-row">{"".join(pill_parts)}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

questions = vacancy.get("questions", []) or []
if questions:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Preguntas de preseleccion</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Estas preguntas se responderan dentro del formulario.</div>', unsafe_allow_html=True)
    for question in questions:
        st.markdown(f'<div class="question-box">{question.get("pregunta", "")}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.write("")

with st.form("apply_form", clear_on_submit=False):
    st.markdown('<div class="section-title">Formulario de postulacion</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Completa tus datos y adjunta tu CV en PDF o DOCX.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre")
        email = st.text_input("Email")
        ciudad = st.text_input("Ciudad")
    with col2:
        apellido = st.text_input("Apellido")
        telefono = st.text_input("Telefono")
        provincia = st.text_input("Provincia")

    linkedin = st.text_input("LinkedIn (opcional)")

    answers_payload: list[dict[str, Any]] = []
    if questions:
        st.write("")
        st.markdown("**Responde las preguntas**")
        for question in questions:
            question_id = int(question["id"])
            question_label = question.get("pregunta", "Pregunta")
            if question.get("tipo_respuesta") == "booleano":
                value = st.selectbox(question_label, options=["", "si", "no"], key=f"q_{question_id}")
            else:
                value = st.text_input(question_label, key=f"q_{question_id}")
            if str(value).strip():
                answers_payload.append({"job_question_id": question_id, "respuesta": str(value).strip()})

    uploaded_file = st.file_uploader("CV (PDF o DOCX)", type=["pdf", "docx"])
    consentimiento = st.checkbox("Acepto la politica de privacidad y el tratamiento de mis datos personales")

    submitted = st.form_submit_button("Enviar postulacion", use_container_width=True, type="primary")

    if submitted:
        if not backend_url:
            st.error("Debes definir la URL del backend.")
        elif not vacancy_token:
            st.error("Debes cargar un token de vacante.")
        elif not uploaded_file:
            st.error("Debes adjuntar un CV en PDF o DOCX.")
        elif not consentimiento:
            st.error("Debes aceptar el tratamiento de datos personales.")
        else:
            try:
                form_data = {
                    "token": vacancy_token,
                    "nombre": nombre.strip(),
                    "apellido": apellido.strip(),
                    "email": email.strip(),
                    "telefono": telefono.strip(),
                    "ciudad": ciudad.strip(),
                    "provincia": provincia.strip(),
                    "linkedin": linkedin.strip(),
                    "consentimiento_datos": str(consentimiento).lower(),
                    "fuente": "streamlit_publico",
                    "answers_json": json.dumps(answers_payload, ensure_ascii=False),
                }
                result_data = submit_application(
                    backend_url,
                    form_data,
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type or "application/octet-stream",
                )
                st.session_state.application_result = result_data
                st.rerun()
            except requests.HTTPError as exc:
                detail = exc.response.text if exc.response is not None else str(exc)
                st.error(f"El backend rechazo la postulacion: {detail}")
            except requests.RequestException as exc:
                st.error(_friendly_backend_error(exc, backend_url))

st.write("")
st.caption("Main file path para Streamlit Cloud: streamlit_app.py")
st.markdown('<div class="small-note">Necesitaras un backend FastAPI publico y accesible desde internet. En Streamlit Cloud configura BACKEND_URL en Secrets o agrega `?backend=https://tu-api` a la URL.</div>', unsafe_allow_html=True)
