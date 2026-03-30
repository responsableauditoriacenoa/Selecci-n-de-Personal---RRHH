import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Briefcase, MapPin, Building2, ChevronRight, HelpCircle } from "lucide-react";
import { publicService } from "../../services/publicService";

export const PublicVacancyPage = () => {
  const { token } = useParams();
  const [vacancy, setVacancy] = useState<any>(null);

  useEffect(() => {
    if (token) publicService.vacancy(token).then(setVacancy);
  }, [token]);

  if (!vacancy) return (
    <div className="public-wrap">
      <div className="loading-wrap"><div className="spinner" />Cargando vacante...</div>
    </div>
  );

  return (
    <div className="public-wrap">
      <div className="public-card">
        <div className="public-brand-bar">
          <div className="public-brand-icon"><Briefcase size={20} /></div>
          <span>Portal de empleo</span>
        </div>

        <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "1.5rem", fontWeight: 800, marginBottom: 6, color: "var(--text)" }}>{vacancy.titulo_publicacion}</h1>

        <div className="info-pills" style={{ marginBottom: 16 }}>
          {vacancy.empresa && <span className="info-pill"><Building2 size={12} />{vacancy.empresa}</span>}
          {vacancy.localidad && <span className="info-pill"><MapPin size={12} />{vacancy.localidad}</span>}
          {vacancy.area && <span className="info-pill">{vacancy.area}</span>}
        </div>

        {vacancy.descripcion_publicacion && (
          <p style={{ fontSize: "0.9rem", color: "var(--text-muted)", lineHeight: 1.65, marginBottom: 20 }}>{vacancy.descripcion_publicacion}</p>
        )}

        {vacancy.questions?.length > 0 && (
          <div style={{ marginBottom: 20 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 10, fontWeight: 600, fontSize: "0.85rem", color: "var(--text)" }}>
              <HelpCircle size={14} style={{ color: "var(--primary)" }} /> Preguntas de preseleccion
            </div>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 6 }}>
              {vacancy.questions.map((question: any) => (
                <li key={question.id} style={{ display: "flex", alignItems: "flex-start", gap: 8, fontSize: "0.875rem", color: "var(--text-muted)", padding: "8px 12px", background: "var(--surface-2)", borderRadius: "var(--r-sm)", border: "1px solid var(--border)" }}>
                  <ChevronRight size={13} style={{ flexShrink: 0, marginTop: 2, color: "var(--primary)" }} />
                  {question.pregunta}
                </li>
              ))}
            </ul>
          </div>
        )}

        <Link className="btn" to={`/public/apply/${token}`} style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 6, width: "100%" }}>
          Postularme ahora <ChevronRight size={15} />
        </Link>
      </div>
    </div>
  );
};

