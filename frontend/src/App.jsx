import { useState } from "react";
import ActionPlanPage from "./pages/ActionPlanPage";
import PoliciesPage from "./pages/PoliciesPage";
import "./App.css";

export default function App() {
  const [tab, setTab] = useState("plan");

  return (
    <div className="layout">
      <header className="header">
        <div className="header-inner">
          <div className="brand">
            <span className="brand-mark">🧭</span>
            <div>
              <div className="brand-name">ActionPlan AI</div>
              <div className="brand-sub">Planes de acción inteligentes basados en políticas de empresa</div>
            </div>
          </div>
          <nav className="nav">
            <button
              className={`nav-btn${tab === "plan" ? " active" : ""}`}
              onClick={() => setTab("plan")}
            >
              🎯 Plan de acción
            </button>
            <button
              className={`nav-btn${tab === "policies" ? " active" : ""}`}
              onClick={() => setTab("policies")}
            >
              📋 Políticas
            </button>
          </nav>
        </div>
      </header>

      <main className="main">
        <div className="container">
          {tab === "plan" ? <ActionPlanPage /> : <PoliciesPage />}
        </div>
      </main>

      <footer className="footer">
        FastAPI · LangChain · ChromaDB · OpenAI · React
      </footer>
    </div>
  );
}
