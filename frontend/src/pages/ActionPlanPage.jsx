import { useState } from "react";
import { api } from "../services/api";
import { Field, RatingButtons, Toggle, SectionCard, Alert, Spinner, FileDrop } from "../components/UI";

const DEPARTMENTS = ["Sales", "Research & Development", "Human Resources"];
const JOB_ROLES = [
  "Sales Executive", "Sales Representative", "Research Scientist",
  "Laboratory Technician", "Manufacturing Director", "Healthcare Representative",
  "Research Director", "Manager",
];
const TRAVEL_OPTIONS = [
  { value: "Non-Travel", label: "Sin viajes" },
  { value: "Travel_Rarely", label: "Ocasionalmente" },
  { value: "Travel_Frequently", label: "Frecuentemente" },
];
const SATISFACTION_LABELS = ["", "Muy bajo/a", "Bajo/a", "Alto/a", "Muy alto/a"];

const EMPTY = {
  employee_id: "", employee_name: "",
  department: "", job_role: "", job_level: "",
  age: "", monthly_income: "", percent_salary_hike: "", stock_option_level: null,
  years_at_company: "", years_in_current_role: "", years_since_last_promotion: "",
  years_with_curr_manager: "", total_working_years: "", num_companies_worked: "",
  training_times_last_year: "", business_travel: "", distance_from_home: "",
  job_satisfaction: null, environment_satisfaction: null, work_life_balance: null,
  job_involvement: null, relationship_satisfaction: null,
  performance_rating: null, over_time: false, attrition: false,
  manager_notes: "",
};

function PlanRenderer({ text }) {
  const lines = text.split("\n");
  return (
    <div className="plan-body">
      {lines.map((line, i) => {
        if (line.startsWith("## ")) return <h3 key={i} className="plan-h2">{line.slice(3)}</h3>;
        if (line.startsWith("# ")) return <h2 key={i} className="plan-h1">{line.slice(2)}</h2>;
        if (line.startsWith("- ") || line.startsWith("* "))
          return <li key={i} className="plan-li" dangerouslySetInnerHTML={{ __html: bold(line.slice(2)) }} />;
        if (/^\d+\./.test(line))
          return <li key={i} className="plan-li plan-num" dangerouslySetInnerHTML={{ __html: bold(line.replace(/^\d+\.\s*/, "")) }} />;
        if (!line.trim()) return <div key={i} className="plan-gap" />;
        return <p key={i} className="plan-p" dangerouslySetInnerHTML={{ __html: bold(line) }} />;
      })}
    </div>
  );
}

function bold(t) {
  return t.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
}

export default function ActionPlanPage() {
  const [form, setForm] = useState({ ...EMPTY });
  const [pdfMode, setPdfMode] = useState(false);
  const [pdfFile, setPdfFile] = useState(null);
  const [saveProfile, setSaveProfile] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const set = (key, val) => setForm(f => ({ ...f, [key]: val }));
  const num = (key, val) => set(key, val === "" ? "" : Number(val));

  const buildProfile = () => {
    const p = { ...form };
    // Convertir strings vacíos a null para campos numéricos
    const numFields = [
      "job_level", "age", "monthly_income", "percent_salary_hike",
      "years_at_company", "years_in_current_role", "years_since_last_promotion",
      "years_with_curr_manager", "total_working_years", "num_companies_worked",
      "training_times_last_year", "distance_from_home",
    ];
    numFields.forEach(k => { if (p[k] === "") p[k] = null; else if (p[k] !== null) p[k] = Number(p[k]); });
    // Strings vacíos -> null
    ["employee_id", "employee_name", "department", "job_role", "business_travel", "manager_notes"].forEach(k => {
      if (!p[k]) p[k] = null;
    });
    return p;
  };

  const handleGenerate = async () => {
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      let res;
      if (pdfMode) {
        if (!pdfFile) throw new Error("Seleccioná un PDF.");
        res = await api.employees.generatePlanPdf(
          pdfFile, form.employee_id || null, form.employee_name || null, saveProfile
        );
      } else {
        res = await api.employees.generatePlan(buildProfile(), saveProfile);
      }
      setResult(res);
      window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
    } catch (e) {
      setError(
        e.message.includes("fetch")
          ? "No se pudo conectar con el backend. Asegurate de que FastAPI esté corriendo en localhost:8000."
          : e.message
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setForm({ ...EMPTY });
    setResult(null);
    setError(null);
    setPdfFile(null);
  };

  return (
    <div className="page">

      {/* ── Identificación ── */}
      <SectionCard title="Identificación">
        <div className="grid-2">
          <Field label="Nombre del empleado">
            <input type="text" value={form.employee_name} onChange={e => set("employee_name", e.target.value)} placeholder="Juan Pérez" />
          </Field>
          <Field label="ID de empleado">
            <input type="text" value={form.employee_id} onChange={e => set("employee_id", e.target.value)} placeholder="EMP-042" />
          </Field>
        </div>
        <div className="grid-3" style={{ marginTop: 12 }}>
          <Field label="Departamento">
            <select value={form.department} onChange={e => set("department", e.target.value)}>
              <option value="">Seleccionar...</option>
              {DEPARTMENTS.map(d => <option key={d}>{d}</option>)}
            </select>
          </Field>
          <Field label="Rol">
            <select value={form.job_role} onChange={e => set("job_role", e.target.value)}>
              <option value="">Seleccionar...</option>
              {JOB_ROLES.map(r => <option key={r}>{r}</option>)}
            </select>
          </Field>
          <Field label="Nivel jerárquico (1–5)">
            <select value={form.job_level} onChange={e => set("job_level", e.target.value)}>
              <option value="">—</option>
              {[1,2,3,4,5].map(n => <option key={n}>{n}</option>)}
            </select>
          </Field>
        </div>
      </SectionCard>

      {/* ── Modo de ingreso ── */}
      <SectionCard title="Datos del perfil">
        <div className="tab-row" style={{ marginBottom: 16 }}>
          <button className={`tab-btn${!pdfMode ? " active" : ""}`} onClick={() => setPdfMode(false)}>Formulario</button>
          <button className={`tab-btn${pdfMode ? " active" : ""}`} onClick={() => setPdfMode(true)}>PDF</button>
        </div>

        {pdfMode ? (
          <Field label="PDF del perfil del empleado" hint="El texto completo del PDF será procesado como contexto adicional.">
            <FileDrop id="emp-pdf" file={pdfFile} onChange={setPdfFile} />
          </Field>
        ) : (
          <>
            {/* ── Situación económica ── */}
            <div className="subsection-label">Situación económica</div>
            <div className="grid-3">
              <Field label="Edad">
                <input type="number" value={form.age} onChange={e => num("age", e.target.value)} placeholder="35" min={18} max={65} />
              </Field>
              <Field label="Ingreso mensual (USD)">
                <input type="number" value={form.monthly_income} onChange={e => num("monthly_income", e.target.value)} placeholder="5000" min={0} />
              </Field>
              <Field label="% último aumento salarial">
                <input type="number" value={form.percent_salary_hike} onChange={e => num("percent_salary_hike", e.target.value)} placeholder="12" min={0} max={100} />
              </Field>
            </div>

            {/* ── Trayectoria ── */}
            <div className="subsection-label" style={{ marginTop: 16 }}>Trayectoria</div>
            <div className="grid-3">
              <Field label="Años en la empresa">
                <input type="number" value={form.years_at_company} onChange={e => num("years_at_company", e.target.value)} placeholder="5" min={0} />
              </Field>
              <Field label="Años en el rol actual">
                <input type="number" value={form.years_in_current_role} onChange={e => num("years_in_current_role", e.target.value)} placeholder="3" min={0} />
              </Field>
              <Field label="Años sin promoción">
                <input type="number" value={form.years_since_last_promotion} onChange={e => num("years_since_last_promotion", e.target.value)} placeholder="2" min={0} />
              </Field>
              <Field label="Años con el manager actual">
                <input type="number" value={form.years_with_curr_manager} onChange={e => num("years_with_curr_manager", e.target.value)} placeholder="2" min={0} />
              </Field>
              <Field label="Experiencia laboral total (años)">
                <input type="number" value={form.total_working_years} onChange={e => num("total_working_years", e.target.value)} placeholder="10" min={0} />
              </Field>
              <Field label="Empresas anteriores">
                <input type="number" value={form.num_companies_worked} onChange={e => num("num_companies_worked", e.target.value)} placeholder="3" min={0} />
              </Field>
            </div>

            {/* ── Desarrollo ── */}
            <div className="subsection-label" style={{ marginTop: 16 }}>Desarrollo</div>
            <div className="grid-3">
              <Field label="Capacitaciones (último año)">
                <input type="number" value={form.training_times_last_year} onChange={e => num("training_times_last_year", e.target.value)} placeholder="2" min={0} max={10} />
              </Field>
              <Field label="Viajes laborales">
                <select value={form.business_travel} onChange={e => set("business_travel", e.target.value)}>
                  <option value="">—</option>
                  {TRAVEL_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
              </Field>
              <Field label="Distancia al trabajo (km)">
                <input type="number" value={form.distance_from_home} onChange={e => num("distance_from_home", e.target.value)} placeholder="15" min={0} />
              </Field>
            </div>

            {/* ── Satisfacción ── */}
            <div className="subsection-label" style={{ marginTop: 16 }}>Indicadores de satisfacción <span className="scale-hint">escala 1–4</span></div>

            {[
              { key: "job_satisfaction", label: "Satisfacción con el trabajo" },
              { key: "environment_satisfaction", label: "Satisfacción con el ambiente" },
              { key: "work_life_balance", label: "Balance vida–trabajo" },
              { key: "job_involvement", label: "Involucramiento en el trabajo" },
              { key: "relationship_satisfaction", label: "Satisfacción relaciones interpersonales" },
            ].map(({ key, label }) => (
              <Field key={key} label={label} hint={form[key] ? SATISFACTION_LABELS[form[key]] : ""}>
                <RatingButtons
                  id={key}
                  value={form[key]}
                  onChange={v => set(key, v)}
                />
              </Field>
            ))}

            {/* ── Desempeño y riesgo ── */}
            <div className="subsection-label" style={{ marginTop: 16 }}>Desempeño y riesgo</div>
            <div className="grid-2">
              <Field label="Calificación de desempeño">
                <RatingButtons
                  id="performance_rating"
                  value={form.performance_rating}
                  onChange={v => set("performance_rating", v)}
                  options={[{ v: 3, label: "3 – Bueno" }, { v: 4, label: "4 – Excelente" }]}
                />
              </Field>
              <Field label="Stock options (nivel 0–3)">
                <RatingButtons
                  id="stock_option_level"
                  value={form.stock_option_level}
                  onChange={v => set("stock_option_level", v)}
                  options={[0,1,2,3].map(n => ({ v: n, label: String(n) }))}
                />
              </Field>
            </div>

            <div className="toggles-row">
              <Toggle
                id="overtime"
                checked={form.over_time}
                onChange={v => set("over_time", v)}
                label="Realiza horas extra regularmente"
              />
              <Toggle
                id="attrition"
                checked={form.attrition}
                onChange={v => set("attrition", v)}
                label="Riesgo de rotación (Attrition = Yes)"
                danger
              />
            </div>
          </>
        )}

        <div className="subsection-label" style={{ marginTop: 16 }}>Observaciones del manager</div>
        <Field hint="Contexto adicional, proyectos recientes, conflictos, metas personales...">
          <textarea
            value={form.manager_notes}
            onChange={e => set("manager_notes", e.target.value)}
            placeholder="El empleado manifestó interés en moverse a otro rol. Tuvo un conflicto con el equipo..."
            rows={4}
          />
        </Field>
      </SectionCard>

      {/* ── Opciones y botón ── */}
      <SectionCard>
        <Toggle
          id="save-profile"
          checked={saveProfile}
          onChange={setSaveProfile}
          label="Guardar este perfil en la base de conocimiento para futuras consultas"
        />

        {error && <Alert type="error">{error}</Alert>}

        <div className="action-row">
          <button className="btn-primary" onClick={handleGenerate} disabled={loading}>
            {loading ? <><Spinner /> Generando plan...</> : "Generar plan de acción"}
          </button>
          <button className="btn-ghost" onClick={handleReset} disabled={loading}>Limpiar</button>
        </div>
      </SectionCard>

      {/* ── Resultado ── */}
      {result && (
        <SectionCard title={`Plan de acción${result.employee_name ? ` — ${result.employee_name}` : ""}`}>
          <div className="result-meta">
            <span className="badge-policies">📚 {result.policies_used} políticas consultadas</span>
            <button className="btn-ghost sm" onClick={() => navigator.clipboard.writeText(result.plan)}>
              📋 Copiar
            </button>
          </div>
          <PlanRenderer text={result.plan} />
        </SectionCard>
      )}
    </div>
  );
}
