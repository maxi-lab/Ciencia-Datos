import tempfile, os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from models import ActionPlanRequest, EmployeeProfile, BulkIngestRequest
from services.rag_service import (
    ingest_employee, list_employees, generate_action_plan, bulk_ingest_employees
)

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("/action-plan")
def create_action_plan(body: ActionPlanRequest):
    if body.save_profile:
        ingest_employee(body.profile)
    return {"ok": True, **generate_action_plan(body.profile)}


@router.post("/action-plan/pdf")
async def create_action_plan_from_pdf(
    file: UploadFile = File(...),
    employee_id: str = Form(None),
    employee_name: str = Form(None),
    save_profile: bool = Form(False),
):
    """Extrae texto del PDF y genera el plan. El PDF puede ser un perfil libre."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Solo se aceptan archivos PDF.")

    from langchain_community.document_loaders import PyPDFLoader
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        pages = PyPDFLoader(tmp_path).load()
        pdf_text = "\n\n".join(p.page_content for p in pages)
    finally:
        os.unlink(tmp_path)

    profile = EmployeeProfile(
        employee_id=employee_id,
        employee_name=employee_name,
        manager_notes=pdf_text,
    )

    if save_profile:
        ingest_employee(profile)

    return {"ok": True, **generate_action_plan(profile)}


@router.post("/ingest")
def ingest_one(profile: EmployeeProfile):
    """Guarda un perfil individual en el vector store."""
    return {"ok": True, **ingest_employee(profile)}


@router.post("/bulk-ingest")
def bulk_ingest(body: BulkIngestRequest):
    """Carga masiva desde el dataset. Se usa con el script de ingesta."""
    return {"ok": True, **bulk_ingest_employees(body.employees)}


@router.get("/")
def get_employees():
    return list_employees()
