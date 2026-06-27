#!/usr/bin/env python3
"""
Script de carga masiva del dataset de empleados al vector store.

Uso:
    python bulk_ingest.py --file ../datos/HR_Employee_Attrition_Cleaned.xlsx
    python bulk_ingest.py --file datos.csv --batch-size 50

El script mapea las 24 columnas útiles del dataset al schema EmployeeProfile
y las ingesta en ChromaDB a través del endpoint /employees/bulk-ingest.
"""

import argparse
import math
import sys
import requests
import pandas as pd

API_URL = "http://localhost:8000"

COLUMN_MAP = {
    "Age": "age",
    "Attrition": None,                    # especial: Yes/No -> bool
    "BusinessTravel": "business_travel",
    "Department": "department",
    "DistanceFromHome": "distance_from_home",
    "EnvironmentSatisfaction": "environment_satisfaction",
    "JobInvolvement": "job_involvement",
    "JobLevel": "job_level",
    "JobRole": "job_role",
    "JobSatisfaction": "job_satisfaction",
    "MonthlyIncome": "monthly_income",
    "NumCompaniesWorked": "num_companies_worked",
    "OverTime": None,                     # especial: Yes/No -> bool
    "PercentSalaryHike": "percent_salary_hike",
    "PerformanceRating": "performance_rating",
    "RelationshipSatisfaction": "relationship_satisfaction",
    "StockOptionLevel": "stock_option_level",
    "TotalWorkingYears": "total_working_years",
    "TrainingTimesLastYear": "training_times_last_year",
    "WorkLifeBalance": "work_life_balance",
    "YearsAtCompany": "years_at_company",
    "YearsInCurrentRole": "years_in_current_role",
    "YearsSinceLastPromotion": "years_since_last_promotion",
    "YearsWithCurrManager": "years_with_curr_manager",
}


def row_to_profile(row: pd.Series, index: int) -> dict:
    profile = {"employee_id": f"EMP-{index+1:04d}"}

    for col, field in COLUMN_MAP.items():
        if col not in row.index:
            continue
        val = row[col]
        if pd.isna(val):
            continue

        if col == "Attrition":
            profile["attrition"] = str(val).strip().lower() in ("yes", "1", "true")
        elif col == "OverTime":
            profile["over_time"] = str(val).strip().lower() in ("yes", "1", "true")
        elif field:
            if isinstance(val, float) and val == int(val):
                profile[field] = int(val)
            else:
                profile[field] = val

    return profile


def ingest(file_path: str, batch_size: int = 50):
    print(f"Leyendo {file_path}...")
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    print(f"  {len(df)} filas encontradas.")
    profiles = [row_to_profile(row, i) for i, row in df.iterrows()]
    total_batches = math.ceil(len(profiles) / batch_size)

    for b in range(total_batches):
        batch = profiles[b * batch_size:(b + 1) * batch_size]
        res = requests.post(
            f"{API_URL}/employees/bulk-ingest",
            json={"employees": batch},
            timeout=120,
        )
        if res.ok:
            data = res.json()
            print(f"  Lote {b+1}/{total_batches}: {data.get('employees_ingested')} empleados, {data.get('total_chunks')} chunks")
        else:
            print(f"  ERROR en lote {b+1}: {res.status_code} — {res.text[:200]}")
            sys.exit(1)

    print(f"\nCarga completa: {len(profiles)} empleados ingresados.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Carga masiva de empleados al RAG")
    parser.add_argument("--file", required=True, help="Ruta al CSV o XLSX")
    parser.add_argument("--batch-size", type=int, default=50, help="Tamaño del lote (default: 50)")
    args = parser.parse_args()
    ingest(args.file, args.batch_size)
