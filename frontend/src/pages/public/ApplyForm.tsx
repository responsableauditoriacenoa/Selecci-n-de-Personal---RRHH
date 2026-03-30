import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { User, Upload, HelpCircle, ChevronRight, Briefcase } from "lucide-react";
import { publicService } from "../../services/publicService";

export const PublicApplicationPage = () => {
  const { token } = useParams();
  const navigate = useNavigate();
  const [vacancy, setVacancy] = useState<any>(null);
  const [form, setForm] = useState({
    nombre: "",
    apellido: "",
    email: "",
    telefono: "",
    ciudad: "",
    provincia: "",
    linkedin: "",
    consentimiento_datos: false,
  });
  const [file, setFile] = useState<File | null>(null);
  const [answersByQuestionId, setAnswersByQuestionId] = useState<Record<number, string>>({});

  useEffect(() => {
    if (token) {
      publicService.vacancy(token).then((data) => {
        setVacancy(data);
        const initialAnswers: Record<number, string> = {};
        (data.questions || []).forEach((q: any) => { initialAnswers[q.id] = ""; });
        setAnswersByQuestionId(initialAnswers);
      });
    }
  }, [token]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!file || !token) return;
    const formData = new FormData();
    formData.append("token", token);
    formData.append("nombre", form.nombre);
    formData.append("apellido", form.apellido);
    formData.append("email", form.email);
    formData.append("telefono", form.telefono);
    formData.append("ciudad", form.ciudad);
    formData.append("provincia", form.provincia);
    formData.append("linkedin", form.linkedin);
    formData.append("consentimiento_datos", String(form.consentimiento_datos));
    formData.append("fuente", "qr_publico");
    const answersPayload = Object.entries(answersByQuestionId)
      .filter(([, respuesta]) => respuesta.trim() !== "")
      .map(([jobQuestionId, respuesta]) => ({
        job_question_id: Number(jobQuestionId),
        respuesta,
      }));
    formData.append("answers_json", JSON.stringify(answersPayload));
    formData.append("file", file);
    const result = await publicService.apply(formData);
    navigate("/public/confirmation", { state: result });
  };

  if (!vacancy) return (
    <div className="public-wrap">
      <div className="loading-wrap"><div className="spinner" />Cargando formulario...</div>
    </div>
  );

  return (
    <div className="public-wrap">
      <div className="public-card">
        <div className="public-brand-bar">
          <div className="public-brand-icon"><Briefcase size={20} /></div>
          <span>{vacancy.titulo_publicacion}</span>
        </div>

        <h2 style={{ fontFamily: "var(--font-heading)", fontWeight: 800, fontSize: "1.2rem", marginBottom: 4 }}>
          Formulario de postulacion
        </h2>
        <p style={{ fontSize: "0.85rem", color: "var(--text-muted)", marginBottom: 20, lineHeight: 1.5 }}>
          Completa tus datos y subi tu CV en PDF o DOCX.
        </p>

        <form onSubmit={submit}>
          {/* Datos personales */}
          <div className="form-section">
            <div className="form-section-title">
              <User size={13} /> Datos personales
            </div>
            <div className="form-grid">
              <label>Nombre<input value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} /></label>
              <label>Apellido<input value={form.apellido} onChange={(e) => setForm({ ...form, apellido: e.target.value })} /></label>
              <label>Email<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
              <label>Telefono<input value={form.telefono} onChange={(e) => setForm({ ...form, telefono: e.target.value })} /></label>
              <label>Ciudad<input value={form.ciudad} onChange={(e) => setForm({ ...form, ciudad: e.target.value })} /></label>
              <label>Provincia<input value={form.provincia} onChange={(e) => setForm({ ...form, provincia: e.target.value })} /></label>
              <label style={{ gridColumn: "1 / -1" }}>
                LinkedIn (opcional)
                <input value={form.linkedin} onChange={(e) => setForm({ ...form, linkedin: e.target.value })} placeholder="linkedin.com/in/tu-perfil" />
              </label>
            </div>
          </div>

          {/* CV Upload */}
          <div className="form-section">
            <div className="form-section-title">
              <Upload size={13} /> Curriculum Vitae
            </div>
            <label style={{ display: "block", cursor: "pointer" }}>
              <div style={{ border: "2px dashed var(--border)", borderRadius: "var(--r)", padding: "20px 16px", textAlign: "center", background: file ? "var(--surface-2)" : "transparent", transition: "background .15s" }}>
                <Upload size={20} style={{ display: "block", margin: "0 auto 8px", color: file ? "var(--primary)" : "var(--text-muted)" }} />
                <div style={{ fontWeight: 600, fontSize: "0.875rem", color: file ? "var(--primary)" : "var(--text)" }}>
                  {file ? file.name : "Haz clic para seleccionar tu CV"}
                </div>
                <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: 4 }}>PDF o DOCX, max 5 MB</div>
              </div>
              <input
                type="file"
                accept=".pdf,.docx"
                style={{ display: "none" }}
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              />
            </label>
          </div>

          {/* Preguntas */}
          {vacancy.questions?.length > 0 && (
            <div className="form-section">
              <div className="form-section-title">
                <HelpCircle size={13} /> Preguntas de preseleccion
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                {vacancy.questions.map((question: any) => (
                  <label key={question.id} style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: "0.875rem" }}>
                    <span style={{ fontWeight: 500 }}>{question.pregunta}</span>
                    {question.tipo_respuesta === "booleano" ? (
                      <select
                        value={answersByQuestionId[question.id] ?? ""}
                        onChange={(e) => setAnswersByQuestionId((prev) => ({ ...prev, [question.id]: e.target.value }))}
                      >
                        <option value="">Seleccionar</option>
                        <option value="si">Si</option>
                        <option value="no">No</option>
                      </select>
                    ) : (
                      <input
                        value={answersByQuestionId[question.id] ?? ""}
                        onChange={(e) => setAnswersByQuestionId((prev) => ({ ...prev, [question.id]: e.target.value }))}
                        placeholder="Escribi tu respuesta"
                      />
                    )}
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Consentimiento */}
          <label style={{ display: "flex", alignItems: "flex-start", gap: 10, fontSize: "0.82rem", color: "var(--text-muted)", margin: "16px 0 20px", lineHeight: 1.5, cursor: "pointer" }}>
            <input
              type="checkbox"
              style={{ width: 16, height: 16, marginTop: 2, flexShrink: 0 }}
              checked={form.consentimiento_datos}
              onChange={(e) => setForm({ ...form, consentimiento_datos: e.target.checked })}
            />
            Acepto la politica de privacidad y el tratamiento de mis datos personales para el proceso de seleccion.
          </label>

          <button type="submit" style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}>
            Enviar postulacion <ChevronRight size={15} />
          </button>
        </form>
      </div>
    </div>
  );
};

