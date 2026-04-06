"""
Serviço de análise de erros da redação.
"""
from typing import Dict, Any, List
from ..prompts.error_prompt import get_error_analysis_prompt
from .gemini_service import chamar_gemini
from ..utils.nlp_utils import analisador  # Importa o analisador

def analisar_erros(texto_redacao: str, correcao_anterior: Dict = None) -> Dict[str, Any]:
    """
    Analisa os erros específicos da redação usando IA + NLP.
    """
    
    # ========== ANÁLISE COM SPACY ==========
    analise_nlp = analisador.analisar_gramatica(texto_redacao)
    repeticoes = analisador.detectar_repeticao(texto_redacao)
    densidade = analisador.calcular_densidade_lexical(texto_redacao)
    palavras_chave = analisador.extrair_palavras_chave(texto_redacao, 5)
    
    # ========== ANÁLISE COM IA ==========
    prompt = get_error_analysis_prompt(texto_redacao, correcao_anterior)
    resultado_ia = chamar_gemini(prompt, esperar_json=True)
    
    # ========== COMBINA OS RESULTADOS ==========
    if "erro" in resultado_ia:
        return {
            "erro": resultado_ia["erro"],
            "erros_gramaticais": [],
            "erros_coesao": [],
            "erros_argumentativos": [],
            "sugestoes_correcao": [],
            "analise_nlp": {
                "densidade_lexical": densidade,
                "palavras_chave": palavras_chave,
                "repeticoes": repeticoes
            }
        }
    
    # Adiciona análise do spaCy
    resultado_ia["analise_nlp"] = {
        "num_sentencas": analise_nlp["num_sentencas"],
        "num_tokens": analise_nlp["num_tokens"],
        "classes_gramaticais": analise_nlp["classes_gramaticais"],
        "entidades": analise_nlp["entidades"],
        "densidade_lexical": densidade,
        "palavras_chave": palavras_chave,
        "repeticoes": repeticoes
    }
    
    # Adiciona sugestões baseadas no spaCy
    if repeticoes:
        for rep in repeticoes[:3]:  # Limita a 3 sugestões
            resultado_ia["sugestoes_correcao"].append(rep["sugestao"])
    
    if densidade < 0.4:
        resultado_ia["sugestoes_correcao"].append(
            "Sua redação tem baixa densidade lexical. Use vocabulário mais variado e específico."
        )
    
    return resultado_ia