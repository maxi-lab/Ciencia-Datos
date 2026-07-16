# eval_recall.py
from services.rag_service import _col
from eval_dataset import EVAL_SET


def retrieved_sources_for(query: str, k: int) -> set[str]:
    docs = _col("policies").as_retriever(search_kwargs={"k": k}).invoke(query)
    return {d.metadata.get("source") for d in docs}


def recall_at_k(relevant: set[str], retrieved: set[str]):
    if not relevant:
        return None
    return len(relevant & retrieved) / len(relevant)


def run_eval(k_values=(3, 6, 10)):
    print(f"Evaluando sobre {len(EVAL_SET)} perfiles de prueba...\n")
    resumen = {k: [] for k in k_values}

    for i, case in enumerate(EVAL_SET, 1):
        relevant = set(case["relevant_sources"])
        print(f"[{i}] relevantes esperados: {relevant}")
        for k in k_values:
            retrieved = retrieved_sources_for(case["query"], k)
            r = recall_at_k(relevant, retrieved)
            resumen[k].append(r)
            faltantes = relevant - retrieved
            estado = "OK" if not faltantes else f"faltó: {faltantes}"
            print(f"    Recall@{k} = {r:.2f}  ({estado})")
        print()

    print("─" * 50)
    for k in k_values:
        vals = [v for v in resumen[k] if v is not None]
        avg = sum(vals) / len(vals)
        print(f"Recall@{k} promedio: {avg:.3f}")


if __name__ == "__main__":
    run_eval()