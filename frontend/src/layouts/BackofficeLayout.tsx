import { NavLink, Outlet, useLocation } from "react-router-dom";
import { LayoutDashboard, Briefcase, ToggleLeft, StickyNote, LogOut } from "lucide-react";
import { useAuth } from "../hooks/useAuth";

const links = [
  { to: "/",         label: "Dashboard",      icon: LayoutDashboard, end: true },
  { to: "/vacancies",label: "Vacantes",        icon: Briefcase },
  { to: "/status",   label: "Estados",         icon: ToggleLeft },
  { to: "/notes",    label: "Notas internas",  icon: StickyNote },
];

const PAGE_TITLES: Record<string, string> = {
  "/":           "Dashboard",
  "/vacancies":  "Vacantes",
  "/vacancies/new": "Nueva Vacante",
  "/status":     "Gestión de Estados",
  "/notes":      "Notas Internas",
};

export const BackofficeLayout = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const pageTitle =
    PAGE_TITLES[location.pathname] ??
    (location.pathname.includes("/applications/") ? "Postulación" :
     location.pathname.includes("/vacancies/")   ? "Vacante" : "RRHH");

  const initials = user?.full_name
    ?.split(" ")
    .slice(0, 2)
    .map((w) => w[0])
    .join("") ?? "U";

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="brand">
            <div className="brand-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </div>
            TalentFlow
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section-label">Menú principal</div>
          {links.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
            >
              <Icon size={16} strokeWidth={2} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="sidebar-avatar">{initials}</div>
            <div className="sidebar-user-info">
              <div className="sidebar-user-name">{user?.full_name}</div>
              <div className="sidebar-user-role">{user?.role}</div>
            </div>
          </div>
          <button
            className="btn-ghost"
            onClick={logout}
            style={{ width: "100%", marginTop: 4, color: "rgba(255,255,255,0.4)", fontSize: "0.8rem", justifyContent: "flex-start", paddingLeft: 10 }}
          >
            <LogOut size={14} />
            Cerrar sesión
          </button>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="topbar-left">
            <div>
              <div className="topbar-title">{pageTitle}</div>
              <div className="topbar-sub">Sistema de Selección de Personal</div>
            </div>
          </div>
          <div className="topbar-right">
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>{user?.email}</span>
          </div>
        </header>
        <div className="page-content">
          <Outlet />
        </div>
      </main>
    </div>
  );
};
