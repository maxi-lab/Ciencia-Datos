# eval_metrics.py
from services.rag_service import _col
from eval_dataset import EVAL_SET


def retrieved_sources_for(query: str, k: int) -> set[str]:
    docs = _col("policies").as_retriever(search_kwargs={"k": k}).invoke(query)
    return {d.metadata.get("source") for d in docs}


def recall_at_k(relevant: set[str], retrieved: set[str]):
    if not relevant:
        return None
    return len(relevant & retrieved) / len(relevant)


def precision_at_k(relevant: set[str], retrieved: set[str]):
    if not retrieved:
        return None
    return len(relevant & retrieved) / len(retrieved)


def run_eval(k_values=(3, 6, 10)):
    print(f"Evaluando sobre {len(EVAL_SET)} perfiles de prueba...\n")
    resumen_r = {k: [] for k in k_values}
    resumen_p = {k: [] for k in k_values}

    for i, case in enumerate(EVAL_SET, 1):
        relevant = set(case["relevant_sources"])
        print(f"[{i}] relevantes esperados: {relevant}")
        for k in k_values:
            retrieved = retrieved_sources_for(case["query"], k)
            r = recall_at_k(relevant, retrieved)
            p = precision_at_k(relevant, retrieved)
            resumen_r[k].append(r)
            resumen_p[k].append(p)
            print(f"    k={k:2d}  Recall={r:.2f}  Precision={p:.2f}  (recuperados: {retrieved})")
        print()

    print("─" * 60)
    print(f"{'k':>4} | {'Recall promedio':>16} | {'Precision promedio':>19}")
    print("─" * 60)
    for k in k_values:
        avg_r = sum(v for v in resumen_r[k] if v is not None) / len(resumen_r[k])
        avg_p = sum(v for v in resumen_p[k] if v is not None) / len(resumen_p[k])
        print(f"{k:>4} | {avg_r:>16.3f} | {avg_p:>19.3f}")


if __name__ == "__main__":
    run_eval()