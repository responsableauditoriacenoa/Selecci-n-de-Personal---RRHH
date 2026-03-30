import { FormEvent, useState } from "react";
import { StickyNote, CheckCircle2 } from "lucide-react";
import { applicationService } from "../../services/applicationService";

export const NotesPage = () => {
  const [applicationId, setApplicationId] = useState("");
  const [comentario, setComentario] = useState("");
  const [message, setMessage] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    await applicationService.addNote(applicationId, comentario);
    setComentario("");
    setMessage("Nota registrada correctamente");
  };

  return (
    <div>
      <div className="page-header" style={{ marginBottom: 20 }}>
        <div className="page-header-text">
          <h1 className="page-title">Notas internas</h1>
          <p className="page-subtitle">Registra comentarios internos sobre un candidato</p>
        </div>
      </div>

      <div className="card" style={{ maxWidth: 600 }}>
        <div className="card-header" style={{ marginBottom: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <StickyNote size={16} style={{ color: "var(--primary)" }} />
            <span className="card-title">Nueva nota</span>
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
          <label style={{ gridColumn: "1 / -1" }}>
            Comentario interno
            <textarea
              value={comentario}
              rows={5}
              onChange={(e) => setComentario(e.target.value)}
              placeholder="Escribe aqui tus observaciones sobre el candidato..."
            />
          </label>
          <button type="submit">Guardar nota</button>
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

