import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { Briefcase, Upload, CheckCircle, QrCode } from "lucide-react";
import axios from "axios";
import { vacancyService } from "../../services/vacancyService";

const EMPRESAS = ["Autosol", "Autolux", "Ciel", "Cumbre Motors", "Kompas", "Portico", "La Luz"];
const LOCALIDADES = ["Jujuy", "Salta", "Tartagal", "Lajitas"];
const AREAS = ["Comercial", "Administracion", "Postventa", "Planes de Ahorro", "Staff"];

export const VacancyFormPage = () => {
  const [created, setCreated] = useState<any | null>(null);
  const [descriptivoFile, setDescriptivoFile] = useState<File | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    empresa: EMPRESAS[0],
    localidad: LOCALIDADES[0],
    area: AREAS[0],
    titulo_publicacion: "",
    fecha_apertura: new Date().toISOString().slice(0, 10),
    fecha_cierre: new Date().toISOString().slice(0, 10),
    estado: "abierta"
  });

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const response = await vacancyService.create(form, descriptivoFile);
      setCreated(response);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail = (err.response?.data as { detail?: string })?.detail;
        setError(detail || "No se pudo guardar la vacante. Intenta nuevamente.");
      } else {
        setError("No se pudo guardar la vacante. Intenta nuevamente.");
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-header-text">
          <h1 className="page-title">Nueva Vacante</h1>
          <p className="page-subtitle">El sistema genera el QR y enlace público automáticamente al guardar.</p>
        </div>
      </div>

      {!created ? (
        <div className="card">
          <form onSubmit={submit}>
            {error && (
              <div style={{ marginBottom: 14, border: "1px solid #ef4444", background: "#fef2f2", color: "#991b1b", padding: "10px 12px", borderRadius: 10, fontSize: "0.875rem" }}>
                {error}
              </div>
            )}
            <div className="form-section">
              <div className="form-section-title">Información de la posición</div>
              <div className="form-grid">
                <label className="field">
                  Empresa
                  <select value={form.empresa} onChange={(e) => setForm({ ...form, empresa: e.target.value })}>
                    {EMPRESAS.map((op) => <option key={op} value={op}>{op}</option>)}
                  </select>
                </label>
                <label className="field">
                  Localidad
                  <select value={form.localidad} onChange={(e) => setForm({ ...form, localidad: e.target.value })}>
                    {LOCALIDADES.map((op) => <option key={op} value={op}>{op}</option>)}
                  </select>
                </label>
                <label className="field">
                  Área
                  <select value={form.area} onChange={(e) => setForm({ ...form, area: e.target.value })}>
                    {AREAS.map((op) => <option key={op} value={op}>{op}</option>)}
                  </select>
                </label>
                <label className="field">
                  Título del puesto
                  <input
                    value={form.titulo_publicacion}
                    onChange={(e) => setForm({ ...form, titulo_publicacion: e.target.value })}
                    placeholder="Ej: Vendedor de planes de ahorro"
                    required
                  />
                </label>
              </div>
            </div>

            <div className="form-section">
              <div className="form-section-title">Documento descriptivo del puesto</div>
              <div style={{ padding: "16px", borderRadius: "var(--r-sm)", border: "1.5px dashed var(--border)", background: "var(--surface-2)", display: "flex", alignItems: "center", gap: 12 }}>
                <Upload size={18} style={{ color: "var(--text-muted)", flexShrink: 0 }} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: "0.875rem" }}>
                    {descriptivoFile ? descriptivoFile.name : "Seleccionar archivo PDF o DOCX"}
                  </div>
                  <div style={{ fontSize: "0.775rem", color: "var(--text-muted)", marginTop: 2 }}>
                    Este documento se usará como base para el análisis comparativo de todos los CV recibidos.
                  </div>
                </div>
                <label style={{ cursor: "pointer" }}>
                  <span className="btn secondary" style={{ fontSize: "0.8rem", padding: "7px 12px" }}>Elegir archivo</span>
                  <input type="file" accept=".pdf,.docx" style={{ display: "none" }} onChange={(e) => setDescriptivoFile(e.target.files?.[0] ?? null)} />
                </label>
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
              <button type="submit" style={{ padding: "10px 24px" }} disabled={saving}>
                <Briefcase size={15} strokeWidth={2} />
                {saving ? "Guardando..." : "Guardar y generar QR"}
              </button>
            </div>
          </form>
        </div>
      ) : (
        <div className="card">
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}>
            <CheckCircle size={22} style={{ color: "var(--success)", flexShrink: 0 }} />
            <div>
              <div style={{ fontWeight: 700, fontSize: "1rem" }}>¡Vacante creada exitosamente!</div>
              <div style={{ fontSize: "0.8125rem", color: "var(--text-muted)" }}>Compartí el QR o el enlace para que los candidatos se postulen.</div>
            </div>
          </div>

          <div className="qr-block">
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
              <QrCode size={14} style={{ color: "var(--text-muted)" }} />
              <img
                src={`data:image/png;base64,${created.qr_base64_png}`}
                alt="Código QR de vacante"
              />
            </div>
            <div className="qr-block-info">
              <div className="info-pills" style={{ marginBottom: 12 }}>
                <span className="info-pill blue">{created.empresa}</span>
                <span className="info-pill">{created.localidad}</span>
                <span className="info-pill">{created.area}</span>
              </div>
              <div style={{ fontWeight: 700, fontSize: "1.05rem", marginBottom: 8 }}>{created.titulo_publicacion}</div>
              {created.descriptivo_archivo_nombre && (
                <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: 12 }}>
                  �Y"" {created.descriptivo_archivo_nombre}
                </div>
              )}
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: 16, wordBreak: "break-all" }}>
                {created.public_url}
              </div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <a className="btn" href={created.public_url} target="_blank" rel="noreferrer">
                  Abrir portal público
                </a>
                <Link className="btn secondary" to={`/vacancies/${created.id}`}>
                  Ver detalle
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};


