from pydantic import BaseModel
from typing import Optional, Literal


SATISFACTION_LABELS = {1: "Muy bajo/a", 2: "Bajo/a", 3: "Alto/a", 4: "Muy alto/a"}
PERFORMANCE_LABELS = {3: "Bueno", 4: "Excelente"}
TRAVEL_LABELS = {
    "Non-Travel": "Sin viajes de trabajo",
    "Travel_Rarely": "Viaja ocasionalmente",
    "Travel_Frequently": "Viaja frecuentemente",
}


class EmployeeProfile(BaseModel):
    # Identificación
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None

    # Puesto
    department: Optional[str] = None          # Sales | Research & Development | Human Resources
    job_role: Optional[str] = None            # 8 roles
    job_level: Optional[int] = None           # 1-5

    # Datos personales
    age: Optional[int] = None

    # Situación económica
    monthly_income: Optional[int] = None
    percent_salary_hike: Optional[int] = None
    stock_option_level: Optional[int] = None  # 0-3

    # Trayectoria
    years_at_company: Optional[int] = None
    years_in_current_role: Optional[int] = None
    years_since_last_promotion: Optional[int] = None
    years_with_curr_manager: Optional[int] = None
    total_working_years: Optional[int] = None
    num_companies_worked: Optional[int] = None

    # Desarrollo
    training_times_last_year: Optional[int] = None
    business_travel: Optional[str] = None     # Non-Travel | Travel_Rarely | Travel_Frequently
    distance_from_home: Optional[int] = None

    # Satisfacción (1-4)
    job_satisfaction: Optional[int] = None
    environment_satisfaction: Optional[int] = None
    work_life_balance: Optional[int] = None
    job_involvement: Optional[int] = None
    relationship_satisfaction: Optional[int] = None

    # Desempeño y riesgo
    performance_rating: Optional[int] = None  # 3 | 4
    over_time: Optional[bool] = None
    attrition: Optional[bool] = None

    # Contexto libre del manager
    manager_notes: Optional[str] = None

    def to_text(self) -> str:
        """Convierte el perfil estructurado a texto para embeddings y prompts."""
        def sat(v): return f"{v} – {SATISFACTION_LABELS.get(v,'')}" if v else "No especificado"
        def yn(v): return "Sí" if v else "No" if v is not None else "No especificado"
        def val(v, suffix=""): return f"{v}{suffix}" if v is not None else "No especificado"

        lines = [
            "PERFIL DE EMPLEADO",
            "==================",
            f"Nombre: {self.employee_name or 'No especificado'}",
            f"ID: {self.employee_id or 'No especificado'}",
            "",
            "PUESTO Y DEPARTAMENTO",
            f"Departamento: {self.department or 'No especificado'}",
            f"Rol: {self.job_role or 'No especificado'}",
            f"Nivel jerárquico: {val(self.job_level)} / 5",
            f"Edad: {val(self.age, ' años')}",
            "",
            "SITUACIÓN ECONÓMICA",
            f"Ingreso mensual: USD {val(self.monthly_income)}",
            f"Último aumento salarial: {val(self.percent_salary_hike, '%')}",
            f"Stock options nivel: {val(self.stock_option_level)} / 3",
            "",
            "TRAYECTORIA",
            f"Años en la empresa: {val(self.years_at_company)}",
            f"Años en el rol actual: {val(self.years_in_current_role)}",
            f"Años sin promoción: {val(self.years_since_last_promotion)}",
            f"Años con el manager actual: {val(self.years_with_curr_manager)}",
            f"Experiencia laboral total: {val(self.total_working_years, ' años')}",
            f"Empresas anteriores: {val(self.num_companies_worked)}",
            "",
            "DESARROLLO",
            f"Capacitaciones el último año: {val(self.training_times_last_year)}",
            f"Viajes laborales: {TRAVEL_LABELS.get(self.business_travel, self.business_travel or 'No especificado')}",
            f"Distancia al trabajo (km aprox.): {val(self.distance_from_home)}",
            "",
            "INDICADORES DE SATISFACCIÓN (escala 1–4)",
            f"  Satisfacción con el trabajo:           {sat(self.job_satisfaction)}",
            f"  Satisfacción con el ambiente:          {sat(self.environment_satisfaction)}",
            f"  Balance vida–trabajo:                  {sat(self.work_life_balance)}",
            f"  Involucramiento en el trabajo:         {sat(self.job_involvement)}",
            f"  Satisfacción relaciones interpersonales: {sat(self.relationship_satisfaction)}",
            "",
            "DESEMPEÑO Y RIESGO",
            f"Calificación de desempeño: {PERFORMANCE_LABELS.get(self.performance_rating, val(self.performance_rating))}",
            f"Horas extra regulares: {yn(self.over_time)}",
            f"Riesgo de rotación (Attrition): {'⚠️ SÍ — marcado como posible renuncia' if self.attrition else 'No'}",
        ]

        if self.manager_notes and self.manager_notes.strip():
            lines += ["", "OBSERVACIONES DEL MANAGER", self.manager_notes]

        return "\n".join(lines)


class ActionPlanRequest(BaseModel):
    profile: EmployeeProfile
    save_profile: bool = False


class PolicyTextRequest(BaseModel):
    text: str
    source_name: str


class BulkIngestRequest(BaseModel):
    """Para carga masiva desde dataset procesado."""
    employees: list[EmployeeProfile]
