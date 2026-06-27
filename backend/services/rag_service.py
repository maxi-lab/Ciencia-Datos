"""
RAG service principal.

Colecciones ChromaDB:
  - policies  → documentos de políticas de empresa
  - employees → perfiles de empleados (para historial y búsqueda)
"""

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from config import settings
from models import EmployeeProfile

embeddings = OpenAIEmbeddings(
    model=settings.embedding_model,
    openai_api_key=settings.openai_api_key,
)

llm = ChatOpenAI(
    model=settings.openai_model,
    openai_api_key=settings.openai_api_key,
    temperature=0.3,
)

splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)


def _col(name: str) -> Chroma:
    return Chroma(
        collection_name=name,
        embedding_function=embeddings,
        persist_directory=settings.chroma_persist_dir,
    )


# ─── POLÍTICAS ────────────────────────────────────────────────────────────────

def ingest_policy_text(text: str, source_name: str) -> dict:
    docs = splitter.create_documents(
        [text], metadatas=[{"source": source_name, "type": "policy"}]
    )
    _col("policies").add_documents(docs)
    return {"chunks_added": len(docs), "source": source_name}


def ingest_policy_pdf(file_path: str, source_name: str) -> dict:
    pages = PyPDFLoader(file_path).load()
    docs = splitter.split_documents(pages)
    for d in docs:
        d.metadata.update({"source": source_name, "type": "policy"})
    _col("policies").add_documents(docs)
    return {"chunks_added": len(docs), "source": source_name}


def list_policies() -> list[dict]:
    db = _col("policies")
    results = db.get(include=["metadatas"])
    seen, out = set(), []
    for meta in results["metadatas"]:
        src = meta.get("source", "unknown")
        if src not in seen:
            seen.add(src)
            out.append({"source": src})
    return out


def delete_policy(source_name: str) -> dict:
    db = _col("policies")
    results = db.get(include=["metadatas"])
    ids = [
        results["ids"][i]
        for i, m in enumerate(results["metadatas"])
        if m.get("source") == source_name
    ]
    if ids:
        db.delete(ids=ids)
    return {"deleted_chunks": len(ids), "source": source_name}


# ─── EMPLEADOS ────────────────────────────────────────────────────────────────

def ingest_employee(profile: EmployeeProfile) -> dict:
    text = profile.to_text()
    meta = {
        "employee_id": profile.employee_id or "",
        "employee_name": profile.employee_name or "",
        "type": "employee_profile",
    }
    docs = splitter.create_documents([text], metadatas=[meta])
    _col("employees").add_documents(docs)
    return {"chunks_added": len(docs), "employee_id": profile.employee_id}


def list_employees() -> list[dict]:
    db = _col("employees")
    results = db.get(include=["metadatas"])
    seen, out = set(), []
    for m in results["metadatas"]:
        eid = m.get("employee_id", "")
        if eid and eid not in seen:
            seen.add(eid)
            out.append({"employee_id": eid, "employee_name": m.get("employee_name", "")})
    return out


def bulk_ingest_employees(profiles: list[EmployeeProfile]) -> dict:
    total_chunks = 0
    for p in profiles:
        r = ingest_employee(p)
        total_chunks += r["chunks_added"]
    return {"employees_ingested": len(profiles), "total_chunks": total_chunks}


# ─── GENERACIÓN DEL PLAN ─────────────────────────────────────────────────────

PROMPT = ChatPromptTemplate.from_template("""
Eres un consultor senior de Recursos Humanos. Tu tarea es generar un plan de acción
personalizado y accionable para un empleado, basándote ESTRICTAMENTE en:

1. Las políticas de la empresa (recuperadas del vector store).
2. El perfil completo del empleado.

Analizá especialmente los indicadores de satisfacción, el tiempo sin promoción,
el riesgo de rotación (Attrition), las horas extra, y el desempeño. Cruzá estos
datos con las políticas para fundamentar cada acción propuesta.

---
POLÍTICAS DE LA EMPRESA (fragmentos más relevantes):
{policies_context}

---
PERFIL DEL EMPLEADO:
{employee_profile}

---
Generá el plan con las siguientes secciones EXACTAS:

## Diagnóstico
Análisis de la situación actual cruzando datos del perfil con las políticas.
Identificá los 2-3 puntos críticos que requieren acción inmediata.

## Objetivos del Plan
Lista de 3 a 5 objetivos SMART (específicos, medibles, con plazo).

## Acciones Concretas
Para cada objetivo, definí acciones específicas con:
- Responsable (empleado / manager / RRHH)
- Plazo sugerido (ej: 30 días / 3 meses / 6 meses)

## Indicadores de Éxito
Métricas concretas para evaluar el avance (qué medir y cada cuánto).

## Próximos 30 Días
Las 3 acciones más urgentes e inmediatas.

Sé directo, específico y fundamentá cada recomendación en las políticas y el perfil.
Si el empleado tiene riesgo de rotación, priorizá acciones de retención.
""")


def generate_action_plan(profile: EmployeeProfile) -> dict:
    profile_text = profile.to_text()

    # 1. Recuperar políticas relevantes
    policy_db = _col("policies")
    policy_docs: list[Document] = policy_db.as_retriever(
        search_kwargs={"k": 6}
    ).invoke(profile_text)

    policies_context = "\n\n---\n\n".join(d.page_content for d in policy_docs)
    if not policies_context.strip():
        policies_context = (
            "(No se encontraron políticas en la base de conocimiento. "
            "Cargue al menos una política antes de generar planes.)"
        )

    # 2. Enriquecer con historial del empleado si existe
    full_profile = profile_text
    if profile.employee_id:
        emp_db = _col("employees")
        try:
            historical = emp_db.similarity_search(
                profile_text, k=3,
                filter={"employee_id": profile.employee_id}
            )
            if historical:
                extra = "\n\n".join(d.page_content for d in historical)
                full_profile += f"\n\n[HISTORIAL PREVIO DEL EMPLEADO]\n{extra}"
        except Exception:
            pass

    # 3. Generar
    response = (PROMPT | llm).invoke({
        "policies_context": policies_context,
        "employee_profile": full_profile,
    })

    return {
        "plan": response.content,
        "policies_used": len(policy_docs),
        "employee_id": profile.employee_id,
        "employee_name": profile.employee_name,
    }
