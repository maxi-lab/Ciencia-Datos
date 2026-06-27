// ─── Reutilizables ────────────────────────────────────────────────────────────

export function Field({ label, children, hint }) {
  return (
    <div className="field">
      {label && <label className="field-label">{label}</label>}
      {children}
      {hint && <span className="field-hint">{hint}</span>}
    </div>
  );
}

export function RatingButtons({ id, value, onChange, options }) {
  const opts = options || [
    { v: 1, label: "1" }, { v: 2, label: "2" },
    { v: 3, label: "3" }, { v: 4, label: "4" },
  ];
  return (
    <div className="rating-group" id={id}>
      {opts.map(o => (
        <button
          key={o.v}
          type="button"
          className={`rating-btn${value === o.v ? " active" : ""}`}
          onClick={() => onChange(o.v)}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

export function Toggle({ id, checked, onChange, label, danger }) {
  return (
    <label className="toggle-row" htmlFor={id}>
      <span className={`toggle-track${checked ? " on" : ""}`} onClick={() => onChange(!checked)}>
        <span className="toggle-thumb" />
      </span>
      <span className={`toggle-label${danger ? " danger" : ""}`}>{label}</span>
    </label>
  );
}

export function SectionCard({ title, children }) {
  return (
    <div className="section-card">
      {title && <div className="section-title">{title}</div>}
      {children}
    </div>
  );
}

export function Alert({ type, children }) {
  return <div className={`alert alert-${type}`}>{children}</div>;
}

export function Spinner() {
  return <span className="spinner" aria-hidden="true" />;
}

export function FileDrop({ id, file, onChange, accept = ".pdf" }) {
  return (
    <div className="file-drop" onClick={() => document.getElementById(id).click()}>
      {file
        ? <span className="file-name">📄 {file.name}</span>
        : <span className="file-placeholder">Clic para seleccionar {accept.toUpperCase()}</span>
      }
      <input
        id={id} type="file" accept={accept} hidden
        onChange={e => onChange(e.target.files[0] || null)}
      />
    </div>
  );
}
