def get_error_analysis_prompt(redacao: str, correcao_anterior: dict = None) -> str:
    contexto = ""
    if correcao_anterior:
        contexto = f"\n**Correção anterior (para referência):**\n{correcao_anterior}\n"
    
    return f"""
Você é um analista linguístico e argumentativo. Identifique os erros específicos na redação abaixo.

{contexto}
**Redação:**
{redacao}

**Classifique os erros em 3 categorias:**

1. **Erros gramaticais**: ortografia, concordância, regência, pontuação, crase
2. **Erros de coesão**: conectivos inadequados, repetições, falta de articulação
3. **Erros argumentativos**: falácias, argumentos rasos, falta de exemplos, generalizações

**Formato de resposta (APENAS JSON):**
{{
    "erros_gramaticais": [
        {{"erro": "descrição", "trecho": "texto problemático", "sugestao": "como corrigir"}}
    ],
    "erros_coesao": [
        {{"erro": "descrição", "trecho": "texto problemático", "sugestao": "como corrigir"}}
    ],
    "erros_argumentativos": [
        {{"erro": "descrição", "trecho": "texto problemático", "sugestao": "como corrigir"}}
    ],
    "sugestoes_correcao": ["sugestão 1", "sugestão 2"]
}}

ATENÇÃO: Retorne APENAS o JSON.
"""