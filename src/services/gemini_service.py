"""
Serviço de comunicação com a API do Google Gemini.
"""
import json
import re
from typing import Dict, Any
from ..config.settings import MODEL

def chamar_gemini(prompt: str, esperar_json: bool = True) -> Dict[str, Any]:
    """
    Envia um prompt para o Gemini e retorna a resposta.
    
    Args:
        prompt: Texto do prompt
        esperar_json: Se True, tenta extrair JSON da resposta
    
    Returns:
        Dicionário com a resposta ou erro
    """
    if not MODEL:
        return {"erro": "Modelo não configurado. Verifique a chave da API."}
    
    try:
        response = MODEL.generate_content(prompt)
        resposta_texto = response.text
        
        if esperar_json:
            # Tenta extrair JSON da resposta
            json_match = re.search(r'\{.*\}', resposta_texto, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return {"erro": "Resposta sem JSON válido", "resposta_bruta": resposta_texto}
        
        return {"resposta": resposta_texto}
        
    except Exception as e:
        return {"erro": f"Erro na chamada da API: {str(e)}"}