# eval_dataset.py
from models import EmployeeProfile

# ⚠️ AJUSTAR: estos strings tienen que ser EXACTOS a lo que devuelve
# list_policies() -- correr el comando de arriba y comparar.
SRC = {
    "reclutamiento": "reclutamiento",
    "capacitacion":  "capacitacion",
    "desempeno":     "desempeno",
    "promocion":     "promocion",
    "compensacion":  "compensacion",
    "bienestar":     "bienestar",
    "asistencia":    "asistencia",
    "talento":       "talento",
    "plan_accion":   "plan_accion",
    "introduccion":  "introdoccion",   # ⚠️ ojo, así quedó guardado (con "doccion", no "duccion")
    "valores":       "valores",
}

# Cada tupla = (perfil de prueba, lista de políticas que DEBERÍAN salir)
# El criterio de relevancia lo definiste vos, leyendo los capítulos 5-11 de tus PDFs.
PERFILES_TEST = [
    # Cap 8 Regla4 + Cap 10 Caso A + Cap 11 Protocolo3: riesgo de burnout
    (
        EmployeeProfile(
            employee_id="EMP-001", employee_name="Test Burnout",
            performance_rating=4, over_time=True, work_life_balance=1,
            job_involvement=4, job_satisfaction=1, attrition=True,
        ),
        [SRC["bienestar"], SRC["talento"], SRC["plan_accion"]],
    ),
    # Cap 6 Regla1 + Cap 7 Regla1 + Cap 11 Protocolo2: alto desempeño sin promoción
    (
        EmployeeProfile(
            employee_id="EMP-002", employee_name="Test Sin Promocion",
            performance_rating=4, years_since_last_promotion=6,
            monthly_income=3000,
        ),
        [SRC["promocion"], SRC["compensacion"], SRC["plan_accion"]],
    ),
    # Cap 4 Caso1 + Cap 11 Protocolo5: sin capacitación
    (
        EmployeeProfile(
            employee_id="EMP-003", employee_name="Test Sin Capacitacion",
            training_times_last_year=0, performance_rating=3,
        ),
        [SRC["capacitacion"], SRC["plan_accion"]],
    ),
    # Cap 9 Regla2/4 + Cap 10: ausentismo + riesgo de abandono alto
    (
        EmployeeProfile(
            employee_id="EMP-004", employee_name="Test Ausentismo",
            job_satisfaction=1, attrition=True, over_time=True,
        ),
        [SRC["asistencia"], SRC["talento"], SRC["bienestar"]],
    ),
    # Cap 7 Regla3 + Cap 10 Regla3: bajo salario + riesgo alto
    (
        EmployeeProfile(
            employee_id="EMP-005", employee_name="Test Bajo Salario",
            monthly_income=2200, attrition=True, performance_rating=3,
        ),
        [SRC["compensacion"], SRC["talento"]],
    ),
    # Cap 6 Regla3 + Cap 11 Protocolo10: estancamiento profesional
    (
        EmployeeProfile(
            employee_id="EMP-006", employee_name="Test Estancado",
            years_in_current_role=8, performance_rating=3,
        ),
        [SRC["promocion"], SRC["plan_accion"]],
    ),
    # Cap 8 Caso D + Cap 11 Protocolo13: sin necesidad de intervención
    (
        EmployeeProfile(
            employee_id="EMP-007", employee_name="Test Sin Intervencion",
            performance_rating=4, job_satisfaction=4, work_life_balance=4,
            environment_satisfaction=4, attrition=False,
        ),
        [SRC["bienestar"], SRC["plan_accion"]],
    ),
    # Cap 5 Regla1 + Cap 11 Protocolo1: desempeño crítico + insatisfacción
    (
        EmployeeProfile(
            employee_id="EMP-008", employee_name="Test Critico",
            performance_rating=2, job_satisfaction=1, over_time=True,
            attrition=True,
        ),
        [SRC["desempeno"], SRC["bienestar"], SRC["talento"], SRC["plan_accion"]],
    ),
]

EVAL_SET = [
    {"query": profile.to_text(), "relevant_sources": relevant}
    for profile, relevant in PERFILES_TEST
]