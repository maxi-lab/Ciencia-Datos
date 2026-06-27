const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function req(method, path, body, isForm = false) {
  const opts = { method, headers: {} };
  if (body) {
    if (isForm) {
      opts.body = body;
    } else {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(body);
    }
  }
  const res = await fetch(`${BASE}${path}`, opts);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Error del servidor");
  }
  return res.json();
}

export const api = {
  health: () => req("GET", "/health"),

  policies: {
    list: () => req("GET", "/policies/"),
    uploadText: (text, sourceName) =>
      req("POST", "/policies/text", { text, source_name: sourceName }),
    uploadPdf: (file, sourceName) => {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("source_name", sourceName);
      return req("POST", "/policies/pdf", fd, true);
    },
    delete: (sourceName) =>
      req("DELETE", `/policies/${encodeURIComponent(sourceName)}`),
  },

  employees: {
    list: () => req("GET", "/employees/"),
    generatePlan: (profile, saveProfile) =>
      req("POST", "/employees/action-plan", { profile, save_profile: saveProfile }),
    generatePlanPdf: (file, employeeId, employeeName, saveProfile) => {
      const fd = new FormData();
      fd.append("file", file);
      if (employeeId) fd.append("employee_id", employeeId);
      if (employeeName) fd.append("employee_name", employeeName);
      fd.append("save_profile", String(saveProfile));
      return req("POST", "/employees/action-plan/pdf", fd, true);
    },
  },
};
