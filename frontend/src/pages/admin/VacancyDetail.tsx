import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Users, Download, Eye, FileText, QrCode } from "lucide-react";
import { StatusChip } from "../../components/StatusChip";
import { vacancyService } from "../../services/vacancyService";

export const VacancyDetailPage = () => {
  const params = useParams();
  const [detail, setDetail] = useState<any>(null);
  const [qr, setQr] = useState<any>(null);

  useEffect(() => {
    if (params.id) {
      vacancyService.detail(params.id).then(setDetail);
      vacancyService.qr(params.id).then(setQr);
    }
  }, [params.id]);

  if (!detail) return <div className="card">Cargando...</div>;
  return (
    <div>
      <div className="page-header">
        <div className="page-header-text">
          <div className="info-pills" style={{ marginBottom: 8 }}>
            {detail.empresa  && <span className="info-pill blue">{detail.empresa}</span>}
            {detail.localidad && <span className="info-pill">{detail.localidad}</span>}
            {detail.area     && <span className="info-pill">{detail.area}</span>}
          </div>
          <h1 className="page-title">{detail.titulo_publicacion}</h1>
          <div style={{ marginTop: 6 }}><StatusChip status={detail.estado} /></div>
        </div>
        <div className="page-header-actions">
          <Link to={`/vacancies/${detail.id}/applications`} className="btn">
            <Users size={15} strokeWidth={2} />
            Ver postulaciones
          </Link>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 16, alignItems: "start" }}>
        <div>
          <div className="card" style={{ marginBottom: 16 }}>
            <div style={{ fontWeight: 700, fontSize: "0.8rem", textTransform: "uppercase", letterSpacing: "0.07em", color: "var(--text-muted)", marginBottom: 12 }}>Enlace público</div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 12px", background: "var(--surface-2)", borderRadius: "var(--r-sm)", border: "1px solid var(--border)" }}>
              <span style={{ flex: 1, fontSize: "0.8125rem", color: "var(--text-muted)", wordBreak: "break-all" }}>{detail.public_url}</span>
              <a href={detail.public_url} target="_blank" rel="noreferrer" className="btn-sm-ghost" style={{ flexShrink: 0 }}>
                <Eye size={13} />
                Abrir
              </a>
            </div>
          </div>

          {detail.descriptivo_documento_cargado && (
            <div className="card">
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <FileText size={18} style={{ color: "var(--primary)" }} />
                  <div>
                    <div style={{ fontWeight: 600, fontSize: "0.875rem" }}>{detail.descriptivo_archivo_nombre}</div>
                    <div style={{ fontSize: "0.775rem", color: "var(--text-muted)" }}>Documento descriptivo del puesto</div>
                  </div>
                </div>
                <div className="action-bar">
                  <button className="btn-sm-ghost" onClick={() => vacancyService.viewProfileDocument(String(detail.id))}>
                    <Eye size={13} /> Ver
                  </button>
                  <button className="btn-sm-ghost" onClick={() => vacancyService.downloadProfileDocument(String(detail.id))}>
                    <Download size={13} /> Descargar
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {qr?.qr_base64_png && (
          <div className="card" style={{ textAlign: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, justifyContent: "center", marginBottom: 10 }}>
              <QrCode size={14} style={{ color: "var(--text-muted)" }} />
              <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Código QR</span>
            </div>
            <img src={`data:image/png;base64,${qr.qr_base64_png}`} alt="QR vacante" style={{ width: 180, borderRadius: "var(--r)", border: "1px solid var(--border)", padding: 6 }} />
          </div>
        )}
      </div>
    </div>
  );
};


