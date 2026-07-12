from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from config import settings
from models import Severidad, Correccion, ValidacionPlan, RelevanciaChunk
import json

PROMPT = """
Eres un auditor estricto de RRHH. Tu tarea es validar el plan de acción generado.

REGLA DE SEVERIDAD:
Marca cada corrección como "critico" si invalida el plan (alucinación de datos,
violación de política), o "menor" si es solo una mejora de estilo/redacción.

QUÉ INCLUYE EL CONTEXTO:
El CONTEXTO que recibís abajo tiene DOS partes: las políticas de la empresa
Y el perfil completo del empleado (con campos estructurados como satisfacción,
riesgo de rotación, involucramiento laboral, antigüedad, desempeño, etc.).
Ambas partes son fuente de verdad válida. Antes de marcar algo como
"alucinacion", revisá TODO el contexto (políticas Y perfil), no solo las políticas.

QUÉ CUENTA COMO EVIDENCIA VÁLIDA:
Los datos crudos y estructurados del empleado (números, etiquetas categóricas,
campos como "attrition_risk", "satisfaction_score", "job_involvement",
"years_in_role", etc.), TAL COMO APARECEN en el contexto, son evidencia
suficiente y válida para respaldar una afirmación del plan. NO exijas que
además haya una justificación narrativa, un análisis cualitativo, o una
fuente adicional para un dato que ya está presente en el contexto.

Ejemplo: si el contexto dice "attrition_risk: Low" y el plan dice
"el empleado presenta bajo riesgo de rotación", esto NO es una alucinación:
el dato está respaldado directamente por el contexto.

Solo marca "alucinacion" cuando el plan afirma un dato, cifra o hecho que
NO aparece en el contexto de ninguna forma (ni como texto, ni como campo,
ni como valor numérico, ni en las políticas ni en el perfil) — es decir,
cuando el generador inventó algo que no está en ninguna parte del contexto.

RESTRICCIÓN IMPORTANTE AL EXPLICAR UNA ALUCINACIÓN O VIOLACIÓN DE POLÍTICA:
En el campo "problema", limitate a citar la frase exacta del plan que no
está respaldada y a señalar qué dato del contexto la contradice o su
ausencia. NO inventes categorías, clasificaciones, políticas o reglas que
no estén literalmente presentes en el CONTEXTO para justificar tu decisión.
Si no encontrás una política o dato exacto que respalde tu objeción, no
generes esa corrección.

CRITERIOS (evalúa cada uno explícitamente):
1. Cumplimiento de políticas de RRHH
2. Tono profesional
3. Formato SMART (Específico, Medible, Alcanzable, Relevante, Temporal)

Para cada criterio que NO se cumpla, generá una corrección con:
- criterio: politicas | alucinacion | tono | smart
- severidad: critico | menor
- problema: qué frase exacta del plan falla y por qué, citando el dato del contexto en conflicto (o su ausencia)
- fix_sugerido: cómo corregirlo, de forma concreta y accionable

Si un criterio se cumple, no generes corrección para él.

CONTEXTO (políticas de la empresa + perfil del empleado):
{context}

PLAN A VALIDAR:
{plan_content}
"""
embeddings = OpenAIEmbeddings(
    model=settings.embedding_model,
    openai_api_key=settings.openai_api_key,
)

llm = ChatOpenAI(
    model=settings.judge_model,
    openai_api_key=settings.openai_api_key,
    temperature=0.0,
)

# LLM "atado" al schema estructurado
llm_judge = llm.with_structured_output(ValidacionPlan)

def normalizar_aprobacion(v: ValidacionPlan, umbral_criticos: float = 0.3) -> ValidacionPlan:
    """
    No confiamos en que el LLM calcule 'aprobado' de forma consistente
    con la lista de correcciones. Lo recalculamos nosotros:
    aprobado = True si no hay correcciones, o si la proporción de
    correcciones críticas es menor al umbral (default 30%).
    """
    total = len(v.correcciones)
    criticos = sum(1 for c in v.correcciones if c.severidad == Severidad.CRITICO)

    if total == 0:
        proporcion_criticos = 0.0
        v.aprobado = True
    else:
        proporcion_criticos = criticos / total
        v.aprobado = proporcion_criticos < umbral_criticos

    print(
        f"Validación: {total} correcciones, {criticos} críticas "
        f"({proporcion_criticos:.0%}). Umbral={umbral_criticos:.0%}. Aprobado={v.aprobado}"
    )
    return v


def validate_action_plan(plan_content: str, context: str) -> ValidacionPlan:
    prompt = PROMPT.format(context=context, plan_content=plan_content)
    resultado: ValidacionPlan = llm_judge.invoke(prompt)
    return normalizar_aprobacion(resultado)

#a nivel de diseño, tendria que ser otro modelo a parte.

def evaluar_relevancia_chunks(profile_text: str, chunks: list[str]) -> list[RelevanciaChunk]:
    fragmentos_str = "\n\n".join(f"[{i}] {c}" for i, c in enumerate(chunks))

    prompt = f"""
Sos un evaluador experto en RRHH. Te paso el perfil de un empleado y una lista
de fragmentos de políticas recuperados por un sistema de búsqueda semántica.

Para cada fragmento, decidí si es RELEVANTE (aporta información aplicable para
generar un plan de acción para ESTE empleado en particular) o NO relevante
(genérico, no aplica a su situación, ruido).

PERFIL DEL EMPLEADO:
{profile_text}

FRAGMENTOS RECUPERADOS:
{fragmentos_str}

Devolvé SOLO un JSON válido, sin texto adicional, con esta forma exacta:
[
  {{"chunk_index": 0, "relevante": true, "justificacion": "..."}},
  {{"chunk_index": 1, "relevante": false, "justificacion": "..."}}
]
"""
    response = llm.invoke(prompt)
    content = response.content.strip()

    # Por si el modelo devuelve con ```json ... ```
    if content.startswith("```"):
        content = content.strip("`")
        content = content.replace("json\n", "", 1) if content.startswith("json") else content

    data = json.loads(content)
    return [RelevanciaChunk(**item) for item in data]
