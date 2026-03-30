import { FormEvent, useState } from "react";
import { ToggleLeft, CheckCircle2 } from "lucide-react";
import { applicationService } from "../../services/applicationService";

const STATUS_OPTIONS = [
  "postulado",
  "en_analisis",
  "recomendado",
  "revision_rrhh",
  "preseleccionado",
  "entrevista_pendiente",
  "entrevistado",
  "evaluacion_final",
  "rechazado",
  "contratado",
  "reserva",
];

export const StatusManagementPage = () => {
  const [applicationId, setApplicationId] = useState("");
  const [estado, setEstado] = useState("en_analisis");
  const [message, setMessage] = useState("");

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    await applicationService.changeStatus(applicationId, estado);
    setMessage("Estado actualizado correctamente");
  };

  return (
    <div>
      <div className="page-header" style={{ marginBottom: 20 }}>
        <div className="page-header-text">
          <h1 className="page-title">Gestion de estados</h1>
          <p className="page-subtitle">Actualizacion manual del estado de un candidato</p>
        </div>
      </div>

      <div className="card" style={{ maxWidth: 520 }}>
        <div className="card-header" style={{ marginBottom: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <ToggleLeft size={16} style={{ color: "var(--primary)" }} />
            <span className="card-title">Actualizar estado</span>
          </div>
        </div>

        <form className="form-grid" onSubmit={submit}>
          <label>
            Application ID
            <input
              value={applicationId}
              onChange={(e) => setApplicationId(e.target.value)}
              placeholder="Ej: 42"
            />
          </label>
          <label>
            Nuevo estado
            <select value={estado} onChange={(e) => setEstado(e.target.value)}>
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </label>
          <button type="submit">Actualizar</button>
        </form>

        {message && (
          <div className="alert alert-success" style={{ marginTop: 14 }}>
            <CheckCircle2 size={15} style={{ flexShrink: 0 }} />
            <span>{message}</span>
          </div>
        )}
      </div>
    </div>
  );
};

