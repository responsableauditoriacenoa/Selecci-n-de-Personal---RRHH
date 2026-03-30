import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Eye, Download, RefreshCw, BarChart2, MessageSquare, TrendingUp, TrendingDown, Target, CheckCircle2, AlertCircle, Info } from "lucide-react";
import { applicationService } from "../../services/applicationService";
import { StatusChip } from "../../components/StatusChip";

export const ApplicationDetailPage = () => {
  const params = useParams();
  const [detail, setDetail] = useState<any>(null);

  const load = () => {
    if (params.id) applicationService.detail(params.id).then(setDetail);
  };

  useEffect(() => {
    load();
  }, [params.id]);

  if (!detail) return <div className="card">Cargando...</div>;
  const insight  = detail.insight;
  const score    = detail.score;
  const scoreVal = score?.score_total ?? 0;
  const scoreColor = scoreVal >= 70 ? "var(--success)" : scoreVal >= 50 ? "var(--warning)" : "var(--danger)";

  return (
    <div>
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="candidate-header">
          <div className="candidate-avatar">
            {(detail.candidate?.nombre?.[0] ?? "?").toUpperCase()}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div className="candidate-name">{detail.candidate?.nombre} {detail.candidate?.apellido}</div>
            <div className="candidate-email">{detail.candidate?.email}</div>
            <div className="candidate-meta">
              <StatusChip status={detail.estado} />
              {score && (
                <span style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: "0.8rem", fontWeight: 700, color: scoreColor }}>
                  <span style={{ fontSize: "1.05rem", fontWeight: 900 }}>{scoreVal}</span>
                  <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>/100</span>
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="action-bar">
          <Link className="btn" to={`/applications/${detail.id}/score`}>
            <BarChart2 size={15} strokeWidth={2} />
            Score completo
          </Link>
          <button className="secondary" onClick={() => applicationService.viewCv(String(detail.id))}>
            <Eye size={14} /> Ver CV
          </button>
          <button className="secondary" onClick={() => applicationService.downloadCv(String(detail.id))}>
            <Download size={14} /> Descargar CV
          </button>
          <button className="btn-sm-ghost" style={{ marginLeft: "auto" }} onClick={async () => { await applicationService.recalculate(detail.id); load(); }}>
            <RefreshCw size={13} /> Recalcular
          </button>
        </div>
      </div>

      {detail.answers?.length > 0 && (
        <div className="card" style={{ marginBottom: 16 }}>
          <div className="card-header" style={{ marginBottom: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <MessageSquare size={16} style={{ color: "var(--primary)" }} />
              <span className="card-title">Respuestas de preselección</span>
            </div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {detail.answers.map((ans: any) => (
              <div key={ans.id} style={{ padding: "10px 14px", borderRadius: "var(--r-sm)", background: "var(--surface-2)", border: "1px solid var(--border)" }}>
                <div style={{ fontSize: "0.72rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 3 }}>Pregunta #{ans.job_question_id}</div>
                <div style={{ fontSize: "0.875rem", fontWeight: 500 }}>{ans.respuesta}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card">
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
          <Target size={16} style={{ color: "var(--primary)" }} />
          <span className="card-title">Análisis comparativo del perfil</span>
        </div>
        {insight ? (
          <>
            {insight.conclusion_analitica && (
              <div className="alert alert-info" style={{ marginTop: 14, marginBottom: 4 }}>
                <Info size={15} style={{ flexShrink: 0, marginTop: 1 }} />
                <span>{insight.conclusion_analitica}</span>
              </div>
            )}
            <div className="insight-grid">
              <div className="insight-block fortaleza">
                <div className="insight-block-title" style={{ display: "flex", alignItems: "center", gap: 5 }}><TrendingUp size={12} /> Fortalezas detectadas</div>
                <ul>{insight.fortalezas_detectadas?.length > 0 ? insight.fortalezas_detectadas.map((i: string) => <li key={i}>{i}</li>) : <li style={{ opacity: 0.6 }}>Sin fortalezas concluyentes.</li>}</ul>
              </div>
              <div className="insight-block debilidad">
                <div className="insight-block-title" style={{ display: "flex", alignItems: "center", gap: 5 }}><TrendingDown size={12} /> Debilidades detectadas</div>
                <ul>{insight.debilidades_detectadas?.length > 0 ? insight.debilidades_detectadas.map((i: string) => <li key={i}>{i}</li>) : <li style={{ opacity: 0.6 }}>Sin debilidades explicitadas.</li>}</ul>
              </div>
              <div className="insight-block oportunidad">
                <div className="insight-block-title" style={{ display: "flex", alignItems: "center", gap: 5 }}><AlertCircle size={12} /> Oportunidades de validación</div>
                <ul>{insight.oportunidades_detectadas?.length > 0 ? insight.oportunidades_detectadas.map((i: string) => <li key={i}>{i}</li>) : <li style={{ opacity: 0.6 }}>Sin oportunidades registradas.</li>}</ul>
              </div>
              <div className="insight-block coincidencia">
                <div className="insight-block-title" style={{ display: "flex", alignItems: "center", gap: 5 }}><CheckCircle2 size={12} /> Coincidencias clave</div>
                <ul>{insight.coincidencias_clave?.length > 0 ? insight.coincidencias_clave.map((i: string) => <li key={i}>{i}</li>) : <li style={{ opacity: 0.6 }}>Sin coincidencias detectadas.</li>}</ul>
              </div>
              <div className="insight-block faltante">
                <div className="insight-block-title" style={{ display: "flex", alignItems: "center", gap: 5 }}><AlertCircle size={12} /> Faltantes relevantes</div>
                <ul>{insight.faltantes_relevantes?.length > 0 ? insight.faltantes_relevantes.map((i: string) => <li key={i}>{i}</li>) : <li style={{ opacity: 0.6 }}>Sin faltantes por reglas actuales.</li>}</ul>
              </div>
            </div>
          </>
        ) : (
          <div style={{ textAlign: "center", padding: "32px", color: "var(--text-muted)" }}>
            <Target size={32} style={{ display: "block", margin: "0 auto 10px", opacity: 0.25 }} />
            <p style={{ marginBottom: 12 }}>Sin análisis comparativo disponible.</p>
            <button className="secondary" onClick={async () => { await applicationService.recalculate(detail.id); load(); }} style={{ fontSize: "0.85rem" }}>
              <RefreshCw size={13} /> Generar análisis
            </button>
          </div>
        )}
      </div>
    </div>
  );
};


