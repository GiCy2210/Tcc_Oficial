import re

def validar_redacao(texto: str) -> dict:
    """
    Valida se a redação está em condições de ser analisada.
    """
    if not texto or not texto.strip():
        return {"valido": False, "erro": "Redação vazia"}
    
    palavras = texto.split()
    if len(palavras) < 50:
        return {"valido": False, "erro": f"Redação muito curta: {len(palavras)} palavras (mínimo 50)"}
    
    if len(palavras) > 500:
        return {"valido": False, "erro": f"Redação muito longa: {len(palavras)} palavras (máximo 500)"}
    
    return {"valido": True, "palavras": len(palavras)}

def normalizar_texto(texto: str) -> str:
    """
    Normaliza o texto removendo espaços extras e quebras de linha.
    """
    texto = re.sub(r'\n+', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()