import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export const LoginPage = () => {
  const [email, setEmail] = useState("admin@rrhh.com");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(email, password);
      navigate("/");
    } catch {
      setError("Credenciales inválidas. Verificá tu email y contraseña.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="public-wrap" style={{ justifyContent: "center" }}>
      <div className="public-card" style={{ maxWidth: 440 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 32, justifyContent: "center" }}>
          <div className="public-brand-icon" style={{ width: 44, height: 44 }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </div>
          <div>
            <div style={{ fontWeight: 800, fontSize: "1.1rem", color: "var(--text)", letterSpacing: "-0.02em" }}>TalentFlow RRHH</div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Sistema de Selección de Personal</div>
          </div>
        </div>
        <h2 style={{ fontSize: "1.3rem", marginBottom: 6 }}>Bienvenido</h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.875rem", marginBottom: 24 }}>
          Ingresá a tu cuenta para gestionar vacantes y postulaciones.
        </p>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <label className="field">
            Email
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="admin@empresa.com" required />
          </label>
          <label className="field">
            Contraseña
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="�?��?��?��?��?��?��?��?�" required />
          </label>
          {error && <div className="alert alert-danger" style={{ padding: "10px 12px" }}>{error}</div>}
          <button type="submit" disabled={loading} style={{ marginTop: 4, padding: "11px", fontSize: "0.9rem" }}>
            {loading ? "Ingresando..." : "Ingresar al sistema"}
          </button>
        </form>
      </div>
    </div>
  );
};


