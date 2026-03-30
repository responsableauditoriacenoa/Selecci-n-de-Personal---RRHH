import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Briefcase, Users, Star, FolderOpen, ArrowRight } from "lucide-react";
import { MetricCard } from "../../components/MetricCard";
import { dashboardService } from "../../services/dashboardService";
import type { DashboardMetrics } from "../../types";

export const DashboardPage = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);

  useEffect(() => {
    dashboardService.getMetrics().then(setMetrics);
  }, []);

  return (
    <div>
      <div className="page-header">
        <div className="page-header-text">
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Vista general del proceso de selección de personal.</p>
        </div>
        <div className="page-header-actions">
          <Link to="/vacancies/new" className="btn">
            <Briefcase size={15} strokeWidth={2} />
            Nueva Vacante
          </Link>
        </div>
      </div>

      <div className="grid-metrics">
        <MetricCard title="Vacantes Totales"  value={metrics?.total_vacancies ?? 0}        icon={Briefcase}   color="blue"   />
        <MetricCard title="Vacantes Abiertas" value={metrics?.open_vacancies ?? 0}         icon={FolderOpen}  color="green"  />
        <MetricCard title="Postulaciones"     value={metrics?.total_applications ?? 0}     icon={Users}       color="blue"   />
        <MetricCard title="Recomendados"      value={metrics?.recommended_applications ?? 0} icon={Star}      color="yellow" />
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <div className="card-title">Accesos rápidos</div>
            <div className="card-subtitle">Navegá a las secciones principales del sistema</div>
          </div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 }}>
          {[
            { to: "/vacancies",     label: "Ver vacantes",        sub: "Listado completo" },
            { to: "/vacancies/new", label: "Crear vacante",       sub: "Con QR automático" },
            { to: "/status",        label: "Gestionar estados",   sub: "Actualizar candidatos" },
            { to: "/notes",         label: "Notas internas",      sub: "Comentarios del equipo" },
          ].map(({ to, label, sub }) => (
            <Link
              key={to}
              to={to}
              style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "13px 14px", borderRadius: "var(--r-sm)", border: "1px solid var(--border)", background: "var(--surface-2)", transition: "all var(--ease)" }}
              onMouseEnter={(e) => { const el = e.currentTarget as HTMLElement; el.style.borderColor = "var(--primary)"; el.style.background = "var(--primary-light)"; }}
              onMouseLeave={(e) => { const el = e.currentTarget as HTMLElement; el.style.borderColor = "var(--border)"; el.style.background = "var(--surface-2)"; }}
            >
              <div>
                <div style={{ fontWeight: 600, fontSize: "0.875rem" }}>{label}</div>
                <div style={{ fontSize: "0.775rem", color: "var(--text-muted)", marginTop: 2 }}>{sub}</div>
              </div>
              <ArrowRight size={15} style={{ color: "var(--text-light)", flexShrink: 0 }} />
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};


