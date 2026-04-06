import { FormEvent, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Briefcase, CheckCircle, ClipboardList, Plus, QrCode, Sparkles, Upload } from "lucide-react";
import axios from "axios";
import { vacancyService } from "../../services/vacancyService";

const EMPRESAS = ["Autosol", "Autolux", "Ciel", "Cumbre Motors", "Kompas", "Portico", "La Luz"];
const LOCALIDADES = ["Jujuy", "Salta", "Tartagal", "Lajitas"];
const AREAS = ["Comercial", "Administracion", "Postventa", "Planes de Ahorro", "Staff"];
const DIMENSION_OPTIONS = [
  { key: "formacion", label: "Formación" },
  { key: "experiencia", label: "Experiencia requerida" },
  { key: "tecnico", label: "Habilidades técnicas" },
  { key: "competencias", label: "Competencias blandas" },
  { key: "condiciones", label: "Condiciones" },
  { key: "valor_agregado", label: "Valor agregado" }
] as const;

type DimensionKey = (typeof DIMENSION_OPTIONS)[number]["key"];

type ScreeningQuestion = {
  id: string;
  pregunta: string;
  dimension: DimensionKey;
  tipo_respuesta: "texto" | "booleano" | "numerico" | "opcion";
  opciones: string;
  respuestas_aceptadas: string;
  peso: number;
  obligatoria: boolean;
  eliminatoria: boolean;
  failure_mode: "revisar" | "alerta" | "descarte";
};

type RuleSections = Record<DimensionKey | "excluyentes", string>;

const buildTemplateQuestions = (): ScreeningQuestion[] => [
  {
    id: crypto.randomUUID(),
    pregunta: "¿Tenés experiencia en recepción?",
    dimension: "experiencia",
    tipo_respuesta: "booleano",
    opciones: "",
    respuestas_aceptadas: "si",
    peso: 10,
    obligatoria: true,
    eliminatoria: false,
    failure_mode: "revisar"
  },
  {
    id: crypto.randomUUID(),
    pregunta: "¿Cuántos años de experiencia tenés en atención al cliente?",
    dimension: "experiencia",
    tipo_respuesta: "numerico",
    opciones: "",
    respuestas_aceptadas: "2",
    peso: 10,
    obligatoria: true,
    eliminatoria: false,
    failure_mode: "revisar"
  },
  {
    id: crypto.randomUUID(),
    pregunta: "¿Trabajaste en concesionarias, talleres o empresas de servicios?",
    dimension: "valor_agregado",
    tipo_respuesta: "booleano",
    opciones: "",
    respuestas_aceptadas: "si",
    peso: 6,
    obligatoria: true,
    eliminatoria: false,
    failure_mode: "revisar"
  },
  {
    id: crypto.randomUUID(),
    pregunta: "¿Tenés experiencia manejando turnos o agendas?",
    dimension: "tecnico",
    tipo_respuesta: "booleano",
    opciones: "",
    respuestas_aceptadas: "si",
    peso: 8,
    obligatoria: true,
    eliminatoria: false,
    failure_mode: "revisar"
  },
  {
    id: crypto.randomUUID(),
    pregunta: "¿Cuál es tu nivel de Excel?",
    dimension: "tecnico",
    tipo_respuesta: "opcion",
    opciones: "Basico,Intermedio,Avanzado",
    respuestas_aceptadas: "Basico,Intermedio,Avanzado",
    peso: 6,
    obligatoria: true,
    eliminatoria: false,
    failure_mode: "revisar"
  },
  {
    id: crypto.randomUUID(),
    pregunta: "¿Tenés disponibilidad full time?",
    dimension: "condiciones",
    tipo_respuesta: "booleano",
    opciones: "",
    respuestas_aceptadas: "si",
    peso: 10,
    obligatoria: true,
    eliminatoria: true,
    failure_mode: "descarte"
  },
  {
    id: crypto.randomUUID(),
    pregunta: "¿Vivís en la ciudad o zona requerida?",
    dimension: "condiciones",
    tipo_respuesta: "booleano",
    opciones: "",
    respuestas_aceptadas: "si",
    peso: 8,
    obligatoria: true,
    eliminatoria: false,
    failure_mode: "alerta"
  },
  {
    id: crypto.randomUUID(),
    pregunta: "¿Tenés experiencia en atención telefónica?",
    dimension: "tecnico",
    tipo_respuesta: "booleano",
    opciones: "",
    respuestas_aceptadas: "si",
    peso: 7,
    obligatoria: true,
    eliminatoria: false,
    failure_mode: "revisar"
  },
  {
    id: crypto.randomUUID(),
    pregunta: "¿Tenés experiencia con sistemas administrativos o CRM?",
    dimension: "tecnico",
    tipo_respuesta: "booleano",
    opciones: "",
    respuestas_aceptadas: "si",
    peso: 8,
    obligatoria: true,
    eliminatoria: false,
    failure_mode: "revisar"
  }
];

const TEMPLATE_RULES: RuleSections = {
  formacion: "secundario completo\nterciario o universitario afin: deseable\ncursos de atencion al cliente / administracion: valor agregado",
  experiencia: "experiencia en recepcion\nexperiencia en atencion al cliente presencial\nexperiencia administrativa basica\nexperiencia en concesionarias o talleres: deseable\nmanejo de agenda/turnos: deseable",
  tecnico: "Excel basico/intermedio\nmanejo de correo electronico\nmanejo de sistemas administrativos o CRM\ncarga de datos\natencion telefonica\ngestion de turnos",
  competencias: "buena presencia profesional\ncomunicacion clara\namabilidad\norden\norganizacion\ntolerancia a la presion\ntrato cordial con clientes\ncapacidad multitarea\nresponsabilidad\npuntualidad",
  condiciones: "disponibilidad horaria\nresidencia cercana\nmovilidad propia si aplica",
  valor_agregado: "experiencia en rubro automotriz o similar\nexperiencia en entornos de servicio\nformacion superior a la requerida\nperfil administrativo adaptable",
  excluyentes: "secundario completo\natencion al publico\ndisponibilidad full time\nmanejo basico de PC"
};

const defaultSections = (): RuleSections => ({
  formacion: "",
  experiencia: "",
  tecnico: "",
  competencias: "",
  condiciones: "",
  valor_agregado: "",
  excluyentes: ""
});

const splitLines = (value: string) =>
  value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);

const splitCsv = (value: string) =>
  value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

const normalizePlainText = (value: string) =>
  value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim();

const inferKeywords = (line: string) => {
  const clean = line.replace(/:(.*)$/u, "").trim();
  const parts = clean.split(/[\/,;]+/).map((item) => item.trim()).filter(Boolean);
  const keywords = new Set<string>([clean]);
  parts.forEach((part) => {
    keywords.add(part);
    part.split(/\s+/).forEach((token) => {
      if (token.length >= 4) keywords.add(token);
    });
  });
  return Array.from(keywords);
};

const buildDimensionPayload = (weights: Record<DimensionKey, number>) =>
  DIMENSION_OPTIONS.map((dimension) => ({
    key: dimension.key,
    label: dimension.label,
    weight: Number(weights[dimension.key] || 0)
  }));

const buildDescriptor = (title: string, sections: RuleSections, summary: string) => {
  const blocks = [
    summary,
    `Formacion:\n${sections.formacion}`,
    `Experiencia requerida:\n${sections.experiencia}`,
    `Habilidades tecnicas:\n${sections.tecnico}`,
    `Competencias blandas:\n${sections.competencias}`,
    `Condiciones:\n${sections.condiciones}`,
    `Valor agregado:\n${sections.valor_agregado}`,
    `Requisitos excluyentes:\n${sections.excluyentes}`
  ].filter(Boolean);
  return `${title}\n\n${blocks.join("\n\n")}`.trim();
};

export const VacancyFormPage = () => {
  const [created, setCreated] = useState<any | null>(null);
  const [descriptivoFile, setDescriptivoFile] = useState<File | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    empresa: EMPRESAS[0],
    localidad: LOCALIDADES[0],
    area: AREAS[0],
    titulo_publicacion: "",
    descripcion_publicacion: "",
    resumen_perfil: "Recepcionista automotriz orientada a la atencion integral del cliente, coordinacion de turnos y soporte administrativo basico.",
    seniority: "Junior / Semi senior",
    modalidad: "Presencial",
    fecha_apertura: new Date().toISOString().slice(0, 10),
    fecha_cierre: new Date().toISOString().slice(0, 10),
    estado: "abierta"
  });
  const [dimensionWeights, setDimensionWeights] = useState<Record<DimensionKey, number>>({
    formacion: 25,
    experiencia: 20,
    tecnico: 15,
    competencias: 15,
    condiciones: 10,
    valor_agregado: 15
  });
  const [sections, setSections] = useState<RuleSections>(defaultSections());
  const [questions, setQuestions] = useState<ScreeningQuestion[]>(buildTemplateQuestions());

  const totalWeight = useMemo(
    () => Object.values(dimensionWeights).reduce((acc, value) => acc + Number(value || 0), 0),
    [dimensionWeights]
  );

  const applyReceptionTemplate = () => {
    setForm((current) => ({
      ...current,
      titulo_publicacion: current.titulo_publicacion || "Recepcionista automotriz",
      descripcion_publicacion:
        current.descripcion_publicacion ||
        "Buscamos una persona para recepcion, atencion al cliente, coordinacion de turnos y soporte administrativo en concesionaria.",
      resumen_perfil:
        "Recepcionista automotriz enfocada en atencion al cliente presencial y telefonica, coordinacion de agendas, carga de datos y soporte administrativo comercial/postventa.",
      seniority: "Junior / Semi senior",
      modalidad: "Presencial"
    }));
    setSections(TEMPLATE_RULES);
    setDimensionWeights({
      formacion: 25,
      experiencia: 20,
      tecnico: 15,
      competencias: 15,
      condiciones: 10,
      valor_agregado: 15
    });
    setQuestions(buildTemplateQuestions());
  };

  const addQuestion = () => {
    setQuestions((current) => [
      ...current,
      {
        id: crypto.randomUUID(),
        pregunta: "",
        dimension: "experiencia",
        tipo_respuesta: "booleano",
        opciones: "",
        respuestas_aceptadas: "si",
        peso: 8,
        obligatoria: true,
        eliminatoria: false,
        failure_mode: "revisar"
      }
    ]);
  };

  const updateQuestion = (id: string, field: keyof ScreeningQuestion, value: string | number | boolean) => {
    setQuestions((current) => current.map((question) => (question.id === id ? { ...question, [field]: value } : question)));
  };

  const removeQuestion = (id: string) => {
    setQuestions((current) => current.filter((question) => question.id !== id));
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError(null);

    if (totalWeight !== 100) {
      setError("La suma de las dimensiones debe ser 100 para que el scoring sea consistente.");
      setSaving(false);
      return;
    }

    const requirements = [
      ...DIMENSION_OPTIONS.flatMap((dimension) =>
        splitLines(sections[dimension.key]).map((line) => {
          const normalized = normalizePlainText(line);
          const isDesired = normalized.includes(": deseable");
          const isValueAdd = normalized.includes("valor agregado");
          const cleanName = line.replace(/:(.*)$/u, "").trim();
          return {
            tipo: dimension.key,
            dimension: isValueAdd ? "valor_agregado" : dimension.key,
            nombre: cleanName,
            descripcion: cleanName,
            obligatorio: !isDesired && !isValueAdd,
            peso: isValueAdd ? 4 : isDesired ? 6 : 10,
            valor_esperado: cleanName,
            keywords: inferKeywords(cleanName),
            match_mode: "any",
            failure_mode: "revisar"
          };
        })
      ),
      ...splitLines(sections.excluyentes).map((line) => ({
        tipo: "filtro",
        dimension: "filtro",
        nombre: line,
        descripcion: line,
        obligatorio: true,
        peso: 0,
        valor_esperado: line,
        keywords: inferKeywords(line),
        match_mode: "any",
        failure_mode: "descarte"
      }))
    ];

    const preparedQuestions = questions
      .filter((question) => question.pregunta.trim())
      .map((question, index) => ({
        pregunta: question.pregunta.trim(),
        dimension: question.dimension,
        tipo_respuesta: question.tipo_respuesta,
        obligatoria: question.obligatoria,
        eliminatoria: question.eliminatoria,
        peso: Number(question.peso || 0),
        orden: index + 1,
        opciones: splitCsv(question.opciones),
        respuestas_aceptadas: splitCsv(question.respuestas_aceptadas),
        failure_mode: question.failure_mode
      }));

    const jobProfileConfig = {
      nombre_puesto: form.titulo_publicacion,
      seniority: form.seniority,
      modalidad: form.modalidad,
      ubicacion: form.localidad,
      descripcion_general: form.resumen_perfil,
      scoring_dimensions: buildDimensionPayload(dimensionWeights),
      requirements,
      questions: preparedQuestions
    };

    const payload = {
      empresa: form.empresa,
      localidad: form.localidad,
      area: form.area,
      titulo_publicacion: form.titulo_publicacion,
      descripcion_publicacion: form.descripcion_publicacion,
      descriptivo_puesto: buildDescriptor(form.titulo_publicacion, sections, form.resumen_perfil),
      fecha_apertura: form.fecha_apertura,
      fecha_cierre: form.fecha_cierre,
      estado: form.estado,
      job_profile_config_json: JSON.stringify(jobProfileConfig)
    };

    try {
      const response = await vacancyService.create(payload, descriptivoFile);
      setCreated(response);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail = (err.response?.data as { detail?: string })?.detail;
        setError(detail || "No se pudo guardar la vacante. Intenta nuevamente.");
      } else {
        setError("No se pudo guardar la vacante. Intenta nuevamente.");
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-header-text">
          <h1 className="page-title">Nueva Vacante</h1>
          <p className="page-subtitle">Define el filtro excluyente, las dimensiones del score y las preguntas que van a comparar a todos los postulantes con la misma vara.</p>
        </div>
      </div>

      {!created ? (
        <div className="card">
          <form onSubmit={submit}>
            {error && (
              <div style={{ marginBottom: 14, border: "1px solid #ef4444", background: "#fef2f2", color: "#991b1b", padding: "10px 12px", borderRadius: 10, fontSize: "0.875rem" }}>
                {error}
              </div>
            )}

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, marginBottom: 18, padding: 14, borderRadius: 18, background: "linear-gradient(135deg, rgba(37,99,235,0.08), rgba(15,23,42,0.04))", border: "1px solid rgba(148,163,184,0.25)" }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 8, fontWeight: 700, marginBottom: 4 }}>
                  <Sparkles size={16} /> Plantilla sugerida
                </div>
                <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                  Carga automaticamente una vacante de recepcionista automotriz con filtros, preguntas y dimensiones listas para ajustar.
                </div>
              </div>
              <button type="button" className="btn secondary" onClick={applyReceptionTemplate}>
                <ClipboardList size={15} /> Aplicar plantilla
              </button>
            </div>

            <div className="form-section">
              <div className="form-section-title">Información de la posición</div>
              <div className="form-grid">
                <label className="field">
                  Empresa
                  <select value={form.empresa} onChange={(e) => setForm({ ...form, empresa: e.target.value })}>
                    {EMPRESAS.map((option) => <option key={option} value={option}>{option}</option>)}
                  </select>
                </label>
                <label className="field">
                  Localidad
                  <select value={form.localidad} onChange={(e) => setForm({ ...form, localidad: e.target.value })}>
                    {LOCALIDADES.map((option) => <option key={option} value={option}>{option}</option>)}
                  </select>
                </label>
                <label className="field">
                  Área
                  <select value={form.area} onChange={(e) => setForm({ ...form, area: e.target.value })}>
                    {AREAS.map((option) => <option key={option} value={option}>{option}</option>)}
                  </select>
                </label>
                <label className="field">
                  Título del puesto
                  <input value={form.titulo_publicacion} onChange={(e) => setForm({ ...form, titulo_publicacion: e.target.value })} placeholder="Ej: Recepcionista automotriz" required />
                </label>
                <label className="field">
                  Seniority
                  <input value={form.seniority} onChange={(e) => setForm({ ...form, seniority: e.target.value })} placeholder="Ej: Junior / Semi senior" />
                </label>
                <label className="field">
                  Modalidad
                  <input value={form.modalidad} onChange={(e) => setForm({ ...form, modalidad: e.target.value })} placeholder="Ej: Presencial" />
                </label>
                <label className="field" style={{ gridColumn: "1 / -1" }}>
                  Descripción pública
                  <textarea rows={3} value={form.descripcion_publicacion} onChange={(e) => setForm({ ...form, descripcion_publicacion: e.target.value })} placeholder="Texto breve visible para el candidato." />
                </label>
                <label className="field" style={{ gridColumn: "1 / -1" }}>
                  Resumen interno del perfil
                  <textarea rows={3} value={form.resumen_perfil} onChange={(e) => setForm({ ...form, resumen_perfil: e.target.value })} placeholder="Síntesis del puesto para RRHH y scoring." />
                </label>
              </div>
            </div>

            <div className="form-section">
              <div className="form-section-title">Dimensiones del score</div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: 12 }}>
                {DIMENSION_OPTIONS.map((dimension) => (
                  <label className="field" key={dimension.key}>
                    {dimension.label}
                    <input
                      type="number"
                      min={0}
                      max={100}
                      value={dimensionWeights[dimension.key]}
                      onChange={(e) => setDimensionWeights({ ...dimensionWeights, [dimension.key]: Number(e.target.value) })}
                    />
                  </label>
                ))}
              </div>
              <div style={{ marginTop: 10, fontSize: "0.84rem", color: totalWeight === 100 ? "var(--success)" : "var(--warning)" }}>
                Suma actual: {totalWeight}/100
              </div>
            </div>

            <div className="form-section">
              <div className="form-section-title">Criterios del perfil</div>
              <div style={{ display: "grid", gap: 14 }}>
                {DIMENSION_OPTIONS.map((dimension) => (
                  <label className="field" key={dimension.key}>
                    {dimension.label}
                    <textarea
                      rows={5}
                      value={sections[dimension.key]}
                      onChange={(e) => setSections({ ...sections, [dimension.key]: e.target.value })}
                      placeholder="Un criterio por línea. Usa ': deseable' o ': valor agregado' cuando corresponda."
                    />
                  </label>
                ))}
                <label className="field">
                  Requisitos excluyentes
                  <textarea
                    rows={4}
                    value={sections.excluyentes}
                    onChange={(e) => setSections({ ...sections, excluyentes: e.target.value })}
                    placeholder="Un requisito excluyente por línea. Estos filtros no suman puntaje: deciden alerta o descarte."
                  />
                </label>
              </div>
            </div>

            <div className="form-section">
              <div className="form-section-title">Preguntas de postulación</div>
              <div style={{ display: "grid", gap: 14 }}>
                {questions.map((question) => (
                  <div key={question.id} style={{ border: "1px solid var(--border)", borderRadius: 16, padding: 14, background: "var(--surface-2)" }}>
                    <div style={{ display: "grid", gap: 12 }}>
                      <label className="field">
                        Pregunta
                        <input value={question.pregunta} onChange={(e) => updateQuestion(question.id, "pregunta", e.target.value)} placeholder="Ej: ¿Tenés experiencia en recepción?" />
                      </label>
                      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 12 }}>
                        <label className="field">
                          Dimensión
                          <select value={question.dimension} onChange={(e) => updateQuestion(question.id, "dimension", e.target.value as DimensionKey)}>
                            {DIMENSION_OPTIONS.map((option) => <option key={option.key} value={option.key}>{option.label}</option>)}
                          </select>
                        </label>
                        <label className="field">
                          Tipo de respuesta
                          <select value={question.tipo_respuesta} onChange={(e) => updateQuestion(question.id, "tipo_respuesta", e.target.value as ScreeningQuestion["tipo_respuesta"])}>
                            <option value="booleano">Sí / No</option>
                            <option value="numerico">Numérica</option>
                            <option value="opcion">Opciones</option>
                            <option value="texto">Texto libre</option>
                          </select>
                        </label>
                        <label className="field">
                          Peso relativo
                          <input type="number" min={0} max={100} value={question.peso} onChange={(e) => updateQuestion(question.id, "peso", Number(e.target.value))} />
                        </label>
                        <label className="field">
                          Modo si falla
                          <select value={question.failure_mode} onChange={(e) => updateQuestion(question.id, "failure_mode", e.target.value as ScreeningQuestion["failure_mode"])}>
                            <option value="revisar">Revisar</option>
                            <option value="alerta">Alerta</option>
                            <option value="descarte">Descarte</option>
                          </select>
                        </label>
                      </div>
                      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
                        <label className="field">
                          Opciones
                          <input value={question.opciones} onChange={(e) => updateQuestion(question.id, "opciones", e.target.value)} placeholder="Solo para tipo opción. Separadas por coma." />
                        </label>
                        <label className="field">
                          Respuesta aceptada
                          <input value={question.respuestas_aceptadas} onChange={(e) => updateQuestion(question.id, "respuestas_aceptadas", e.target.value)} placeholder="Ej: si o Basico,Intermedio" />
                        </label>
                      </div>
                      <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
                        <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          <input type="checkbox" checked={question.obligatoria} onChange={(e) => updateQuestion(question.id, "obligatoria", e.target.checked)} />
                          Obligatoria
                        </label>
                        <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          <input type="checkbox" checked={question.eliminatoria} onChange={(e) => updateQuestion(question.id, "eliminatoria", e.target.checked)} />
                          Eliminatoria
                        </label>
                        <button type="button" className="btn secondary" onClick={() => removeQuestion(question.id)}>
                          Quitar pregunta
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
                <button type="button" className="btn secondary" onClick={addQuestion}>
                  <Plus size={15} /> Agregar pregunta
                </button>
              </div>
            </div>

            <div className="form-section">
              <div className="form-section-title">Documento descriptivo del puesto</div>
              <div style={{ padding: "16px", borderRadius: "var(--r-sm)", border: "1.5px dashed var(--border)", background: "var(--surface-2)", display: "flex", alignItems: "center", gap: 12 }}>
                <Upload size={18} style={{ color: "var(--text-muted)", flexShrink: 0 }} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: "0.875rem" }}>{descriptivoFile ? descriptivoFile.name : "Seleccionar archivo PDF o DOCX"}</div>
                  <div style={{ fontSize: "0.775rem", color: "var(--text-muted)", marginTop: 2 }}>
                    Es opcional. Puede complementar el contexto, pero el score va a usar las reglas configuradas arriba.
                  </div>
                </div>
                <label style={{ cursor: "pointer" }}>
                  <span className="btn secondary" style={{ fontSize: "0.8rem", padding: "7px 12px" }}>Elegir archivo</span>
                  <input type="file" accept=".pdf,.docx" style={{ display: "none" }} onChange={(e) => setDescriptivoFile(e.target.files?.[0] ?? null)} />
                </label>
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 8 }}>
              <button type="submit" style={{ padding: "10px 24px" }} disabled={saving}>
                <Briefcase size={15} strokeWidth={2} />
                {saving ? "Guardando..." : "Guardar vacante y generar QR"}
              </button>
            </div>
          </form>
        </div>
      ) : (
        <div className="card">
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}>
            <CheckCircle size={22} style={{ color: "var(--success)", flexShrink: 0 }} />
            <div>
              <div style={{ fontWeight: 700, fontSize: "1rem" }}>Vacante creada con scoring configurable</div>
              <div style={{ fontSize: "0.8125rem", color: "var(--text-muted)" }}>El QR público ya quedó asociado al filtro y a las preguntas que definiste.</div>
            </div>
          </div>

          <div className="qr-block">
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
              <QrCode size={14} style={{ color: "var(--text-muted)" }} />
              <img src={`data:image/png;base64,${created.qr_base64_png}`} alt="Código QR de vacante" />
            </div>
            <div className="qr-block-info">
              <div className="info-pills" style={{ marginBottom: 12 }}>
                <span className="info-pill blue">{created.empresa}</span>
                <span className="info-pill">{created.localidad}</span>
                <span className="info-pill">{created.area}</span>
              </div>
              <div style={{ fontWeight: 700, fontSize: "1.05rem", marginBottom: 8 }}>{created.titulo_publicacion}</div>
              {created.descriptivo_archivo_nombre && (
                <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: 12 }}>
                  Documento adjunto: {created.descriptivo_archivo_nombre}
                </div>
              )}
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: 16, wordBreak: "break-all" }}>{created.public_url}</div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <a className="btn" href={created.public_url} target="_blank" rel="noreferrer">
                  Abrir portal público
                </a>
                <Link className="btn secondary" to={`/vacancies/${created.id}`}>
                  Ver detalle
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};