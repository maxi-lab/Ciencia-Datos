
# ActionPlan AI — Employee RAG

Genera planes de acción personalizados para empleados usando RAG sobre políticas de empresa.

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI + LangChain |
| Vector Store | ChromaDB (persistido localmente) |
| LLM | OpenAI gpt-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Frontend | React + Vite |

## Estructura del proyecto

```
employee-rag/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings (.env)
│   ├── models.py            # Schemas: EmployeeProfile, requests
│   ├── bulk_ingest.py       # Script carga masiva del dataset
│   ├── requirements.txt
│   ├── .env.example
│   ├── services/
│   │   └── rag_service.py   # ChromaDB + LangChain + prompt
│   └── routers/
│       ├── policies.py      # CRUD de políticas
│       └── employees.py     # Generación de planes + ingesta
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── App.jsx / App.css
        ├── main.jsx
        ├── services/api.js
        ├── components/UI.jsx
        └── pages/
            ├── ActionPlanPage.jsx
            └── PoliciesPage.jsx
```

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Editá .env y poné tu OPENAI_API_KEY

uvicorn main:app --reload --port 8000
# Docs: http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# App: http://localhost:5173
```

## Carga masiva del dataset (cuando esté listo el EDA)

```bash
cd backend
source venv/bin/activate
python bulk_ingest.py --file ../datos/HR_Employee_Attrition_Cleaned.xlsx
```

El script mapea automáticamente las 24 columnas útiles del dataset:
- Age, Department, JobRole, JobLevel
- MonthlyIncome, PercentSalaryHike, StockOptionLevel
- YearsAtCompany, YearsInCurrentRole, YearsSinceLastPromotion, YearsWithCurrManager
- TotalWorkingYears, NumCompaniesWorked, TrainingTimesLastYear
- BusinessTravel, DistanceFromHome
- JobSatisfaction, EnvironmentSatisfaction, WorkLifeBalance, JobInvolvement, RelationshipSatisfaction
- PerformanceRating, OverTime, Attrition

**Columnas excluidas** (sin valor semántico para el plan): DailyRate, HourlyRate, MonthlyRate.

## Arquitectura RAG

```
Políticas de empresa ──► ChromaDB (colección: policies)
                                    │
Perfil de empleado ─────────────────┤
  (24 campos estructurados)         │  similarity_search k=6
                                    ▼
                           Fragmentos relevantes
                                    │
                              Prompt enriquecido
                              (perfil + políticas)
                                    │
                            GPT-4o-mini
                                    │
                    Plan de acción estructurado
                    (5 secciones: diagnóstico,
                     objetivos, acciones, KPIs,
                     próximos 30 días)
```

## Endpoints

```
GET  /health

POST /policies/text          Carga política en texto plano
POST /policies/pdf           Carga política desde PDF
GET  /policies/              Lista políticas cargadas
DELETE /policies/{name}      Elimina política

POST /employees/action-plan          Genera plan (perfil estructurado)
POST /employees/action-plan/pdf      Genera plan desde PDF libre
POST /employees/ingest               Guarda un perfil individual
POST /employees/bulk-ingest          Carga masiva (desde dataset)
GET  /employees/             Lista empleados guardados
```
