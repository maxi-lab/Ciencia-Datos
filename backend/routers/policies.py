import tempfile, os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from models import PolicyTextRequest
from services.rag_service import (
    ingest_policy_text, ingest_policy_pdf, list_policies, delete_policy
)

router = APIRouter(prefix="/policies", tags=["policies"])


@router.post("/text")
def upload_policy_text(body: PolicyTextRequest):
    if not body.text.strip():
        raise HTTPException(400, "El texto no puede estar vacío.")
    return {"ok": True, **ingest_policy_text(body.text, body.source_name)}


@router.post("/pdf")
async def upload_policy_pdf(
    file: UploadFile = File(...),
    source_name: str = Form(...),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Solo se aceptan archivos PDF.")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        result = ingest_policy_pdf(tmp_path, source_name)
    finally:
        os.unlink(tmp_path)
    return {"ok": True, **result}


@router.get("/")
def get_policies():
    return list_policies()


@router.delete("/{source_name}")
def remove_policy(source_name: str):
    return {"ok": True, **delete_policy(source_name)}
