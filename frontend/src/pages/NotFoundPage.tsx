import { Link } from "react-router-dom";
import { SearchX, Home } from "lucide-react";

export const NotFoundPage = () => (
  <div className="public-wrap">
    <div className="public-card" style={{ textAlign: "center" }}>
      <SearchX size={52} style={{ color: "var(--border)", display: "block", margin: "0 auto 12px" }} />
      <h2 style={{ fontFamily: "var(--font-heading)", fontWeight: 800, fontSize: "1.5rem", marginBottom: 6 }}>
        404 — Pagina no encontrada
      </h2>
      <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: 24, lineHeight: 1.6 }}>
        La pagina que buscas no existe o fue movida.
      </p>
      <Link to="/" className="btn" style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
        <Home size={14} /> Volver al inicio
      </Link>
    </div>
  </div>
);
