import { FormEvent, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { jobProfileService } from "../../services/jobProfileService";

const defaultForm = {
  nombre_puesto: "",
  area_id: 1,
  seniority: "",
  modalidad: "Hibrido",
  ubicacion: "",
  descripcion_general: "",
  version: 1,
  estado: "borrador",
  requirements: [],
  questions: []
};

export const JobProfileFormPage = () => {
  const [form, setForm] = useState<any>(defaultForm);
  const [analysisFile, setAnalysisFile] = useState<File | null>(null);
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);
  const [analysisError, setAnalysisError] = useState("");
  const params = useParams();
  const navigate = useNavigate();
  const isEdit = useMemo(() => Boolean(params.id), [params.id]);

  useEffect(() => {
    if (params.id) {
      jobProfileService.detail(params.id).then(setForm);
    }
  }, [params.id]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (params.id) {
      await jobProfileService.update(params.id, form);
    } else {
      await jobProfileService.create(form);
    }
    navigate("/job-profiles");
  };

  const analyze = async () => {
    if (!params.id) {
      setAnalysisError("Primero guarda el descriptivo y luego subi el documento para analizar.");
      return;
    }
    if (!analysisFile) {
      setAnalysisError("Selecciona un documento PDF o DOCX para analizar.");
      return;
    }

    setAnalysisError("");
    const result = await jobProfileService.analyzeDocument(params.id, analysisFile);
    setAnalysisResult(result);
  };

  return (
    <section className="card">
      <h2>{isEdit ? "Editar descriptivo" : "Nuevo descriptivo"}</h2>
      <p style={{ color: "var(--muted)" }}>
        Carga datos del perfil y luego podes subir un documento para estimar compatibilidad automaticamente.
      </p>
      <form className="form-grid" onSubmit={submit}>
        <label>
          Nombre puesto
          <input value={form.nombre_puesto} onChange={(e) => setForm({ ...form, nombre_puesto: e.target.value })} />
        </label>
        <label>
          ID de area
          <input
            type="number"
            value={form.area_id}
            onChange={(e) => setForm({ ...form, area_id: Number(e.target.value) })}
          />
        </label>
        <label>
          Seniority
          <input value={form.seniority} onChange={(e) => setForm({ ...form, seniority: e.target.value })} />
        </label>
        <label>
          Modalidad
          <input value={form.modalidad} onChange={(e) => setForm({ ...form, modalidad: e.target.value })} />
        </label>
        <label>
          Ubicacion
          <input value={form.ubicacion} onChange={(e) => setForm({ ...form, ubicacion: e.target.value })} />
        </label>
        <label style={{ gridColumn: "1 / -1" }}>
          Descripcion
          <textarea
            rows={4}
            value={form.descripcion_general}
            onChange={(e) => setForm({ ...form, descripcion_general: e.target.value })}
          />
        </label>
        <button type="submit">Guardar</button>
      </form>

      <article className="card" style={{ marginTop: 16, background: "var(--surface-2)" }}>
        <h3>Analizar documento contra este descriptivo</h3>
        <p style={{ color: "var(--muted)" }}>
          Sube un CV o perfil (PDF/DOCX) y el sistema calcula compatibilidad con comentario explicativo.
        </p>
        <div className="form-grid">
          <label style={{ gridColumn: "1 / -1" }}>
            Documento a analizar
            <input type="file" accept=".pdf,.docx" onChange={(e) => setAnalysisFile(e.target.files?.[0] ?? null)} />
          </label>
          <button type="button" onClick={analyze}>
            Analizar compatibilidad
          </button>
        </div>

        {analysisError && <p style={{ color: "var(--danger)" }}>{analysisError}</p>}

        {analysisResult && (
          <div style={{ marginTop: 12 }}>
            <p>
              <strong>Puntuacion:</strong> {analysisResult.score_compatibilidad}/100
            </p>
            <p>
              <strong>Clasificacion:</strong> {analysisResult.clasificacion}
            </p>
            <p>{analysisResult.comentario_analisis}</p>

            {analysisResult.coincidencias_clave?.length > 0 && (
              <>
                <h4>Coincidencias clave</h4>
                <ul>
                  {analysisResult.coincidencias_clave.map((item: string) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </>
            )}

            {analysisResult.alertas?.length > 0 && (
              <>
                <h4>Alertas</h4>
                <ul>
                  {analysisResult.alertas.map((item: string) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </>
            )}
          </div>
        )}
      </article>
    </section>
  );
};

