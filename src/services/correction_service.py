"""
Serviço de correção de redações.
"""
from typing import Dict, Any
from ..prompts.correction_prompt import get_correction_prompt
from .gemini_service import chamar_gemini

def corrigir_redacao(texto_redacao: str) -> Dict[str, Any]:
    """
    Corrige uma redação usando IA.
    
    Args:
        texto_redacao: Texto completo da redação
    
    Returns:
        Dicionário com notas, feedback e erros
    """
    prompt = get_correction_prompt(texto_redacao)
    resultado = chamar_gemini(prompt, esperar_json=True)
    
    # Estrutura padrão de retorno
    if "erro" in resultado:
        return {
            "erro": resultado["erro"],
            "notas": None,
            "feedback": None
        }
    
    # Garante que a estrutura existe
    if "notas" not in resultado:
        resultado["notas"] = {
            "competencia_1": 0,
            "competencia_2": 0,
            "competencia_3": 0,
            "competencia_4": 0,
            "competencia_5": 0,
            "total": 0
        }
    
    if "feedback" not in resultado:
        resultado["feedback"] = {
            "pontos_fortes": "Não foi possível gerar feedback.",
            "pontos_fracos": "Não foi possível gerar feedback."
        }
    
    return resultado