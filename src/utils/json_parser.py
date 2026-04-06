import json
import re
from typing import Dict, Any

def extrair_json(texto: str) -> Dict[str, Any]:
    """
    Extrai e parseia um JSON de uma string que pode conter texto adicional.
    """
    # Tenta encontrar um bloco JSON
    match = re.search(r'\{.*\}', texto, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    
    # Se não encontrou, tenta limpar a string
    texto_limpo = re.sub(r'```json\s*|\s*```', '', texto)
    try:
        return json.loads(texto_limpo)
    except json.JSONDecodeError:
        return {"erro": "Não foi possível extrair JSON", "resposta_bruta": texto}

def validar_estrutura_correcao(dados: Dict) -> bool:
    """
    Valida se o JSON tem a estrutura esperada para correção.
    """
    if "notas" not in dados:
        return False
    
    notas = dados["notas"]
    campos_necessarios = ["competencia_1", "competencia_2", "competencia_3", 
                         "competencia_4", "competencia_5", "total"]
    
    for campo in campos_necessarios:
        if campo not in notas:
            return False
    
    if "feedback" not in dados:
        return False
    
    return True