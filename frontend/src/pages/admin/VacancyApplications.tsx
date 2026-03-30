import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Eye, Download, FileText, User } from "lucide-react";
import { StatusChip } from "../../components/StatusChip";
import { applicationService } from "../../services/applicationService";
import { vacancyService } from "../../services/vacancyService";

export const VacancyApplicationsPage = () => {
  const params = useParams();
  const [items, setItems] = useState<any[]>([]);

  useEffect(() => {
    if (params.id) {
      vacancyService.applications(params.id).then(setItems);
    }
  }, [params.id]);

  return (
    <div>
      <div className="page-header">
        <div className="page-header-text">
          <h1 className="page-title">Postulaciones</h1>
          <p className="page-subtitle">{items.length} candidato{items.length !== 1 ? "s" : ""} postulado{items.length !== 1 ? "s" : ""} a esta vacante.</p>
        </div>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Candidato</th>
              <th>Email</th>
              <th>Estado</th>
              <th>CV</th>
              <th>Ficha</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 && (
              <tr><td colSpan={6} style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)" }}>
                <User size={28} style={{ display: "block", margin: "0 auto 8px", opacity: 0.3 }} />
                Aún no hay postulaciones para esta vacante
              </td></tr>
            )}
            {items.map((item) => (
              <tr key={item.id}>
                <td style={{ color: "var(--text-muted)", fontSize: "0.8rem", fontWeight: 500 }}>#{item.id}</td>
                <td>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{ width: 28, height: 28, borderRadius: "50%", background: "var(--primary-light)", color: "var(--primary)", display: "grid", placeItems: "center", fontSize: "0.7rem", fontWeight: 800, flexShrink: 0 }}>
                      {(item.candidate?.nombre?.[0] ?? "?").toUpperCase()}
                    </div>
                    <span style={{ fontWeight: 600, fontSize: "0.875rem" }}>
                      {item.candidate?.nombre} {item.candidate?.apellido}
                    </span>
                  </div>
                </td>
                <td style={{ color: "var(--text-muted)", fontSize: "0.8125rem" }}>{item.candidate?.email}</td>
                <td><StatusChip status={item.estado} /></td>
                <td>
                  <div className="table-actions">
                    <button type="button" className="btn-sm-ghost" onClick={() => applicationService.viewCv(String(item.id))}>
                      <Eye size={13} /> Ver CV
                    </button>
                    <button type="button" className="btn-sm-ghost" onClick={() => applicationService.downloadCv(String(item.id))}>
                      <Download size={13} />
                    </button>
                  </div>
                </td>
                <td>
                  <Link to={`/applications/${item.id}`} className="btn-sm-ghost">
                    <FileText size={13} /> Ficha
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};


