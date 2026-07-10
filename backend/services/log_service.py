import json
from datetime import datetime, timezone

def log_retrieval(query: str, employee_id: str, retrieved: list, metricas: dict, log_path="retrieval_logs.jsonl"):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "employee_id": employee_id,
        "query_preview": query[:300],
        "retrieved_docs": retrieved,
        "precision_at_k": metricas["precision_at_k"],
        "relevantes": metricas["relevantes"],
        "total_recuperados": metricas["total_recuperados"],
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n") 