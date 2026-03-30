import { Link, useLocation } from "react-router-dom";
import { CheckCircle2, Star, BarChart2 } from "lucide-react";

export const PublicConfirmationPage = () => {
  const location = useLocation();
  const result = (location.state || {}) as {
    application_id?: number;
    score_total?: number;
    clasificacion?: string;
    resumen_analisis?: string;
  };

  const score = result.score_total ?? 0;
  const scoreColor = score >= 70 ? "var(--success)" : score >= 50 ? "var(--warning)" : "var(--danger)";

  return (
    <div className="public-wrap">
      <div className="public-card" style={{ textAlign: "center" }}>
        <div className="public-brand-bar">
          <div className="public-brand-icon" style={{ background: "var(--success)" }}><CheckCircle2 size={20} /></div>
          <span>Postulacion enviada</span>
        </div>

        <CheckCircle2 size={52} style={{ color: "var(--success)", margin: "16px auto 8px", display: "block" }} />
        <h2 style={{ fontFamily: "var(--font-heading)", fontWeight: 800, fontSize: "1.3rem", marginBottom: 6 }}>
          Todo listo!
        </h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: 20, lineHeight: 1.6 }}>
          Tu informacion fue registrada correctamente. Gracias por postularte.
        </p>

        {result.application_id && (
          <div style={{ background: "var(--surface-2)", border: "1px solid var(--border)", borderRadius: "var(--r)", padding: "16px 20px", marginBottom: 16, textAlign: "left" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 10, fontWeight: 600, fontSize: "0.8rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-muted)" }}>
              <BarChart2 size={13} /> Resultado del analisis inicial
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span style={{ fontSize: "2rem", fontWeight: 900, color: scoreColor, lineHeight: 1 }}>{score}</span>
              <div>
                <div style={{ fontWeight: 700, color: scoreColor, fontSize: "0.95rem" }}>{result.clasificacion}</div>
                <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Postulacion #{result.application_id}</div>
              </div>
              <Star size={18} style={{ marginLeft: "auto", color: score >= 70 ? "var(--warning)" : "var(--border)" }} />
            </div>
            {result.resumen_analisis && (
              <p style={{ marginTop: 10, fontSize: "0.82rem", color: "var(--text-muted)", lineHeight: 1.55 }}>{result.resumen_analisis}</p>
            )}
          </div>
        )}

        <Link to="/" className="btn" style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 6, width: "100%" }}>
          Volver al inicio
        </Link>
      </div>
    </div>
  );
};

