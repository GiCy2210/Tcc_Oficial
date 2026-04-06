"""
Serviço de geração de plano de estudos personalizado.
"""
from typing import Dict, Any, List
from ..prompts.study_prompt import get_study_plan_prompt
from .gemini_service import chamar_gemini

def gerar_plano_estudos(notas: Dict, erros: List[str], tempo_disponivel: str = "médio") -> Dict[str, Any]:
    """
    Gera um plano de estudos baseado no desempenho do aluno.
    
    Args:
        notas: Dicionário com notas por competência
        erros: Lista de erros identificados
        tempo_disponivel: "pouco", "médio" ou "muito"
    
    Returns:
        Dicionário com plano de estudos estruturado
    """
    prompt = get_study_plan_prompt(notas, erros, tempo_disponivel)
    resultado = chamar_gemini(prompt, esperar_json=True)
    
    if "erro" in resultado:
        return {
            "erro": resultado["erro"],
            "plano_de_estudos": [],
            "prioridade": "Não foi possível gerar plano"
        }
    
    return {
        "plano_de_estudos": resultado.get("plano_de_estudos", []),
        "prioridade": resultado.get("prioridade", "Foco em todas as competências"),
        "recursos_sugeridos": resultado.get("recursos_sugeridos", [])
    }