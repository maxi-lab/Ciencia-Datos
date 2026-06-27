import { useState, useEffect } from "react";
import { api } from "../services/api";
import { Field, Alert, FileDrop, SectionCard } from "../components/UI";


export default function PoliciesPage() {
  const [policies, setPolicies] = useState([]);
  const [mode, setMode] = useState("text");
  const [sourceName, setSourceName] = useState("");
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState(null);

  const flash = (text, type = "success") => {
    setMsg({ text, type });
    setTimeout(() => setMsg(null), 3500);
  };

  const load = async () => {
    try { setPolicies(await api.policies.list()); }
    catch { /* backend offline */ }
  };

  useEffect(() => { load(); }, []);

  const handleAdd = async () => {
    if (!sourceName.trim()) return flash("Ingresá un nombre para la política.", "error");
    setLoading(true);
    try {
      if (mode === "text") {
        if (!text.trim()) return flash("El contenido no puede estar vacío.", "error");
        await api.policies.uploadText(text, sourceName);
      } else {
        if (!file) return flash("Seleccioná un PDF.", "error");
        await api.policies.uploadPdf(file, sourceName);
      }
      flash("Política cargada correctamente.");
      setSourceName(""); setText(""); setFile(null);
      load();
    } catch (e) {
      flash(e.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (src) => {
    if (!confirm(`¿Eliminar la política "${src}"?`)) return;
    try { await api.policies.delete(src); load(); }
    catch (e) { flash(e.message, "error"); }
  };

  return (
    <div className="page">
      <SectionCard title="Agregar política">
        <div className="tab-row">
          <button className={`tab-btn${mode === "text" ? " active" : ""}`} onClick={() => setMode("text")}>Texto</button>
          <button className={`tab-btn${mode === "pdf" ? " active" : ""}`} onClick={() => setMode("pdf")}>PDF</button>
        </div>

        <Field label="Nombre de la política">
          <input
            type="text" value={sourceName} onChange={e => setSourceName(e.target.value)}
            placeholder="Ej: Política de Desempeño 2024"
          />
        </Field>

        {mode === "text" ? (
          <Field label="Contenido">
            <textarea
              value={text} onChange={e => setText(e.target.value)}
              placeholder="Pegá aquí el texto completo de la política..." rows={6}
            />
          </Field>
        ) : (
          <Field label="Archivo PDF">
            <FileDrop id="pol-pdf" file={file} onChange={setFile} />
          </Field>
        )}

        {msg && <Alert type={msg.type === "error" ? "error" : "success"}>{msg.text}</Alert>}

        <button className="btn-primary" onClick={handleAdd} disabled={loading}>
          {loading ? "Cargando..." : "Agregar política"}
        </button>
      </SectionCard>

      <SectionCard title="Políticas en la base de conocimiento">
        {policies.length === 0
          ? <p className="empty-hint">Aún no hay políticas. Cargá al menos una antes de generar planes.</p>
          : policies.map(p => (
              <div key={p.source} className="policy-item">
                <span className="policy-name">📌 {p.source}</span>
                <button className="del-btn" onClick={() => handleDelete(p.source)} title="Eliminar">✕</button>
              </div>
            ))
        }
      </SectionCard>
    </div>
  );
}
