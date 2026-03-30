import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Briefcase, Plus, ExternalLink, Eye } from "lucide-react";
import { vacancyService } from "../../services/vacancyService";
import { StatusChip } from "../../components/StatusChip";
import type { Vacancy } from "../../types";

export const VacanciesListPage = () => {
  const [data, setData] = useState<Vacancy[]>([]);

  useEffect(() => {
    vacancyService.list().then(setData);
  }, []);

  return (
    <div>
      <div className="page-header">
        <div className="page-header-text">
          <h1 className="page-title">Vacantes</h1>
          <p className="page-subtitle">{data.length} vacante{data.length !== 1 ? "s" : ""} registrada{data.length !== 1 ? "s" : ""} en el sistema.</p>
        </div>
        <div className="page-header-actions">
          <Link to="/vacancies/new" className="btn">
            <Plus size={15} strokeWidth={2.5} />
            Nueva Vacante
          </Link>
        </div>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Puesto</th>
              <th>Empresa</th>
              <th>Localidad</th>
              <th>Área</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {data.length === 0 && (
              <tr><td colSpan={7} style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)" }}>
                <Briefcase size={28} style={{ display: "block", margin: "0 auto 8px", opacity: 0.3 }} />
                No hay vacantes registradas
              </td></tr>
            )}
            {data.map((item) => (
              <tr key={item.id}>
                <td style={{ color: "var(--text-muted)", fontWeight: 500, fontSize: "0.8rem" }}>#{item.id}</td>
                <td>
                  <div style={{ fontWeight: 600, fontSize: "0.875rem" }}>{item.titulo_publicacion}</div>
                </td>
                <td>{item.empresa || <span style={{ color: "var(--text-light)" }}>�?"</span>}</td>
                <td>{item.localidad || <span style={{ color: "var(--text-light)" }}>�?"</span>}</td>
                <td>{item.area || <span style={{ color: "var(--text-light)" }}>�?"</span>}</td>
                <td><StatusChip status={item.estado} /></td>
                <td>
                  <div className="table-actions">
                    <Link to={`/vacancies/${item.id}`} className="btn-sm-ghost">
                      <Eye size={13} />
                      Ver
                    </Link>
                    <a href={item.public_url} target="_blank" rel="noreferrer" className="btn-sm-ghost">
                      <ExternalLink size={13} />
                      Portal
                    </a>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};


