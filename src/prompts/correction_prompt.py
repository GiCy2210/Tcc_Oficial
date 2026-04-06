def get_correction_prompt(redacao: str) -> str:
    return f"""
Você é um corretor especialista em redações do ENEM. Analise a redação a seguir com base nas 5 competências oficiais.

**Competências avaliadas:**
1. Domínio da norma padrão da língua portuguesa
2. Compreensão do tema e aplicação de repertório sociocultural
3. Seleção e organização da argumentação
4. Coesão e articulação entre as partes do texto
5. Elaboração da proposta de intervenção

**Redação a ser analisada:**
{redacao}

**Formato de resposta (APENAS JSON):**
{{
    "notas": {{
        "competencia_1": 0,
        "competencia_2": 0,
        "competencia_3": 0,
        "competencia_4": 0,
        "competencia_5": 0,
        "total": 0
    }},
    "feedback": {{
        "pontos_fortes": "Liste os principais acertos do aluno",
        "pontos_fracos": "Liste os principais erros e áreas de melhoria"
    }}
}}

ATENÇÃO: Retorne APENAS o JSON, sem texto adicional fora da estrutura.
As notas vão de 0 a 200 por competência (total máximo 1000).
"""