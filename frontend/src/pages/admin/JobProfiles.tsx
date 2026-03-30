import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { jobProfileService } from "../../services/jobProfileService";
import type { JobProfile } from "../../types";

export const JobProfilesListPage = () => {
  const [data, setData] = useState<JobProfile[]>([]);

  useEffect(() => {
    jobProfileService.list().then(setData);
  }, []);

  return (
    <section>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
        <h2>Descriptivos de Puesto</h2>
        <Link to="/job-profiles/new" className="btn">
          Nuevo descriptivo
        </Link>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Puesto</th>
              <th>Seniority</th>
              <th>Version</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item) => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.nombre_puesto}</td>
                <td>{item.seniority}</td>
                <td>{item.version}</td>
                <td>{item.estado}</td>
                <td>
                  <Link to={`/job-profiles/${item.id}/edit`}>Editar</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};

