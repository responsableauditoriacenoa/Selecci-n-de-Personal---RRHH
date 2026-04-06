import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { TrendingUp, TrendingDown, AlertCircle, ArrowLeft, Award } from "lucide-react";
import { applicationService } from "../../services/applicationService";

const BAR_LABELS: Record<string, string> = {
  score_formacion: "Formación académica",
  score_experiencia: "Experiencia laboral",
  score_tecnico: "Perfil técnico",
};

type ScoreBar = {
  key: string;
  label: string;
  value: number;
  max: number;
};

export const ScoreViewPage = () => {
  const params   = useParams();
  const navigate = useNavigate();
  const [detail, setDetail] = useState<any>(null);

  useEffect(() => {
    if (params.id) applicationService.detail(params.id).then(setDetail);
  }, [params.id]);

  if (!detail) return <div className="loading-wrap"><div className="spinner" />Cargando...</div>;

  const score      = detail?.score;
  const total      = score?.score_total ?? 0;
  const clasif     = score?.clasificacion ?? "sin cálculo";
  const fortalezas  = (score?.reasons || []).filter((r: any) => r.tipo === "fortaleza");
  const oportunidades = (score?.reasons || []).filter((r: any) => r.tipo === "observacion");
  const debilidades = (score?.reasons || []).filter((r: any) => r.tipo === "alerta" || r.tipo === "descarte");
  const dimensionBars = useMemo<ScoreBar[]>(() => {
    if (score?.dimension_scores?.length) {
      return score.dimension_scores.map((item: any): ScoreBar => ({
        key: item.key,
        label: item.label,
        value: item.score,
        max: item.weight
      }));
    }
    return (["score_formacion", "score_experiencia", "score_tecnico"] as const).map((key) => ({
      key,
      label: BAR_LABELS[key],
      value: score?.[key] ?? 0,
      max: 100
    }));
  }, [score]);

  const colorClass = total >= 70 ? "high" : total >= 50 ? "mid" : "low";
  const clasifColor = total >= 70 ? "var(--success)" : total >= 50 ? "var(--warning)" : "var(--danger)";

  return (
    <div>
      <div className="page-header" style={{ marginBottom: 20 }}>
        <div className="page-header-text">
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <button className="btn-sm-ghost" onClick={() => navigate(-1)} style={{ gap: 4 }}>
              <ArrowLeft size={14} /> Volver
            </button>
          </div>
          <h1 className="page-title">Score del candidato</h1>
          <p className="page-subtitle">{detail.candidate?.nombre} {detail.candidate?.apellido}</p>
        </div>
      </div>

      {/* Hero score block */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="score-hero">
          <div className={`score-number ${colorClass}`}>{total}</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Award size={16} style={{ color: clasifColor }} />
              <span style={{ fontWeight: 700, fontSize: "1rem", color: clasifColor }}>{clasif}</span>
            </div>
            {score?.resumen_analisis && (
              <p style={{ fontSize: "0.875rem", color: "var(--text-muted)", maxWidth: 520, lineHeight: 1.5 }}>{score.resumen_analisis}</p>
            )}
          </div>
        </div>

        {/* Score bars */}
        <div className="score-bars">
          {dimensionBars.map((bar) => {
            const val = bar.value ?? 0;
            const percent = Math.max(Math.min((val / Math.max(bar.max, 1)) * 100, 100), 0);
            const bc  = percent >= 70 ? "high" : percent >= 50 ? "mid" : "low";
            return (
              <div className="score-bar-row" key={bar.key}>
                <div className="score-bar-header">
                  <span>{bar.label}</span>
                  <span style={{ fontWeight: 700 }}>{val}/{bar.max}</span>
                </div>
                <div style={{ background: "var(--border)", borderRadius: 99, height: 8, overflow: "hidden" }}>
                  <div className={`score-bar-fill ${bc}`} style={{ width: `${percent}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Reasons */}
      <div className="insight-grid">
        <div className="insight-block fortaleza">
          <div className="insight-block-title" style={{ display: "flex", alignItems: "center", gap: 5 }}><TrendingUp size={12} /> Fortalezas ({fortalezas.length})</div>
          <ul>{fortalezas.length > 0 ? fortalezas.map((r: any) => <li key={r.id}>{r.descripcion}</li>) : <li style={{ opacity: 0.6 }}>Sin fortalezas concluyentes.</li>}</ul>
        </div>
        <div className="insight-block oportunidad">
          <div className="insight-block-title" style={{ display: "flex", alignItems: "center", gap: 5 }}><AlertCircle size={12} /> Oportunidades ({oportunidades.length})</div>
          <ul>{oportunidades.length > 0 ? oportunidades.map((r: any) => <li key={r.id}>{r.descripcion}</li>) : <li style={{ opacity: 0.6 }}>Sin oportunidades registradas.</li>}</ul>
        </div>
        <div className="insight-block debilidad">
          <div className="insight-block-title" style={{ display: "flex", alignItems: "center", gap: 5 }}><TrendingDown size={12} /> Debilidades y riesgos ({debilidades.length})</div>
          <ul>{debilidades.length > 0 ? debilidades.map((r: any) => <li key={r.id}>{r.descripcion}</li>) : <li style={{ opacity: 0.6 }}>Sin debilidades críticas.</li>}</ul>
        </div>
      </div>
    </div>
  );
};


