import google.generativeai as genai
import json
import re

TEMAS_BASE = [
    "Desafios da saúde mental no Brasil contemporâneo",
    "O impacto das redes sociais na democracia brasileira",
    "Desigualdade educacional no Brasil",
    "A invisibilidade da população em situação de rua",
    "Os desafios da inclusão digital no Brasil",
    "A violência contra a mulher no Brasil",
    "Os impactos da desinformação na sociedade",
    "Crise habitacional nas grandes cidades brasileiras",
    "O papel do Estado na preservação ambiental",
    "Desafios do sistema prisional brasileiro",
]

PROMPT_GERADOR = """
Você é um elaborador de provas do ENEM. Gere um tema de redação inédito, atual e relevante,
no estilo oficial do ENEM, com textos motivadores reais.

O tema deve:
- Ser atual e socialmente relevante para o Brasil
- Ter relação com alguma área do conhecimento (Ciências Humanas, Natureza, Linguagens ou Matemática)
- Ser suficientemente amplo para diferentes abordagens argumentativas
- NÃO repetir temas já muito usados (cotas, bullying, redes sociais)

Retorne APENAS JSON puro, sem markdown:
{{
  "tema": "Título do tema completo",
  "area": "Área do conhecimento relacionada",
  "textos_motivadores": [
    {{
      "tipo": "texto jornalístico",
      "fonte": "Nome do veículo, Ano",
      "conteudo": "Trecho do texto motivador (3-5 linhas)"
    }},
    {{
      "tipo": "dado estatístico",
      "fonte": "Fonte oficial, Ano",
      "conteudo": "Dado ou estatística relevante"
    }},
    {{
      "tipo": "charge ou imagem",
      "fonte": "Autor, Ano",
      "conteudo": "Descrição do que a charge/imagem representaria"
    }}
  ],
  "palavras_chave": ["palavra1", "palavra2", "palavra3"],
  "dicas_abordagem": ["dica1", "dica2", "dica3"]
}}
"""

def gerar_tema(api_key: str) -> dict:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(PROMPT_GERADOR)
    texto = response.text.strip()
    texto = re.sub(r'```json\s*', '', texto)
    texto = re.sub(r'```\s*', '', texto)
    return json.loads(texto.strip())

def temas_predefinidos() -> list[str]:
    return TEMAS_BASE