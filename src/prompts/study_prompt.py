def get_study_plan_prompt(notas: dict, erros: list, tempo_disponivel: str = "médio") -> str:
    return f"""
Você é um tutor educacional especializado em ENEM. Crie um plano de estudos personalizado.

**Desempenho do aluno:**
Notas por competência: {notas}
Erros identificados: {erros}
Tempo disponível para estudo: {tempo_disponivel} ("pouco" = 2h/semana, "médio" = 5h/semana, "muito" = 10h+/semana)

**Formato de resposta (APENAS JSON):**
{{
    "plano_de_estudos": [
        {{
            "semana": 1,
            "foco": "competência ou habilidade principal",
            "atividades": ["atividade 1", "atividade 2", "atividade 3"],
            "carga_horaria": "X horas"
        }}
    ],
    "prioridade": "competência com menor nota ou erro mais grave",
    "recursos_sugeridos": ["link vídeo 1", "link artigo 2", "exercício específico"]
}}

ATENÇÃO: Retorne APENAS o JSON.
"""