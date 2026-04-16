"""
correction_service.py — v2
Serviço de correção de redações ENEM usando Google Gemini.

Melhorias v2:
- Prompt ultra-detalhado baseado no Manual do Candidato INEP 2023
- Pré-análise textual (palavras, parágrafos, conectivos) injetada no prompt
- Validação e sanitização do JSON retornado pela IA
- Retry automático com back-off exponencial
- Recálculo automático da nota total (evita inconsistências da IA)
- temperature=0.2 para respostas mais consistentes e precisas
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

NOTAS_VALIDAS   = {0, 40, 80, 120, 160, 200}
MODELO          = "gemini-2.0-flash"
MAX_TENTATIVAS  = 3
INTERVALO_BASE  = 2  # segundos

CONECTIVOS_ADVERSATIVOS = {"no entanto", "contudo", "todavia", "porém", "entretanto"}
CONECTIVOS_CONCLUSIVOS  = {"portanto", "logo", "assim", "dessa forma", "por isso", "consequentemente"}
CONECTIVOS_EXPLICATIVOS = {"pois", "porque", "já que", "uma vez que", "visto que"}
CONECTIVOS_ADITIVOS     = {"além disso", "ademais", "outrossim", "também", "ainda"}
CONECTIVOS_CAUSAIS      = {"devido a", "em virtude de", "por causa de", "em razão de"}
TODOS_CONECTIVOS        = (
    CONECTIVOS_ADVERSATIVOS | CONECTIVOS_CONCLUSIVOS |
    CONECTIVOS_EXPLICATIVOS | CONECTIVOS_ADITIVOS | CONECTIVOS_CAUSAIS
)

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class PreAnalise:
    """Métricas extraídas do texto antes de chamar a IA."""
    total_palavras: int
    total_paragrafos: int
    total_linhas: int
    conectivos_encontrados: list[str]
    tem_proposta_intervencao: bool
    palavras_longas_count: int   # proxy de vocabulário diversificado

@dataclass
class Competencia:
    nota: int
    justificativa: str
    erros: list[str] = field(default_factory=list)
    dicas: list[str] = field(default_factory=list)

@dataclass
class ResultadoCorrecao:
    c1: Competencia
    c2: Competencia
    c3: Competencia
    c4: Competencia
    c5: Competencia
    nota_total: int
    fuga_ao_tema: bool
    violacao_direitos_humanos: bool
    feedback_geral: str
    plano_estudos: list[dict]
    pre_analise: Optional[PreAnalise] = None

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

PROMPT_SISTEMA = """\
Você é um corretor certificado de redações do ENEM, treinado pelo INEP.
Sua avaliação segue rigorosamente a Cartilha do Participante e o Manual de
Correção oficial. Você é técnico, justo, rigoroso e construtivo.

═══════════════════════════════════════════════════════════════════
COMPETÊNCIA 1 — Domínio da Modalidade Escrita Formal da Língua Portuguesa
═══════════════════════════════════════════════════════════════════
Avalia: ortografia, acentuação, pontuação, concordância nominal e verbal,
regência nominal e verbal, colocação pronominal, estrutura sintática.

• 200 → Excelente domínio. Eventuais desvios mínimos não afetam a leitura.
        Pontuação usada com precisão e intenção estilística.
• 160 → Bom domínio. Poucos desvios que não comprometem a compreensão.
• 120 → Domínio mediano. Desvios recorrentes mas texto ainda compreensível.
• 080 → Domínio insuficiente. Erros graves e frequentes (crase, regência,
        concordância) que dificultam consideravelmente a leitura.
• 040 → Domínio precário. Estrutura fragilizada, erros elementares dominantes.
• 000 → Não domínio. Texto ilegível ou ininteligível.

═══════════════════════════════════════════════════════════════════
COMPETÊNCIA 2 — Compreensão da Proposta e Repertório Sociocultural
═══════════════════════════════════════════════════════════════════
Avalia: aderência ao tema proposto, desenvolvimento argumentativo,
repertório sociocultural (filósofos, dados, leis, obras literárias,
teorias científicas, eventos históricos).

• 200 → Tema COMPLETAMENTE desenvolvido. Repertório sociocultural PRODUTIVO
        (integrado organicamente ao argumento, não apenas decorativo). Autoria clara.
• 160 → Tema desenvolvido com repertório adequado mas pode ser mais aprofundado.
• 120 → Tema parcialmente desenvolvido. Repertório previsível ou pouco integrado.
• 080 → Tangenciamento: aborda tópicos relacionados mas desvia do tema central.
• 040 → Tangenciamento grave. Quase fuga ao tema.
• 000 → Fuga total ao tema proposto.

ATENÇÃO: Dados inventados ou incorretos citados como verdadeiros = redução de nota.

═══════════════════════════════════════════════════════════════════
COMPETÊNCIA 3 — Seleção, Relação e Organização das Informações
═══════════════════════════════════════════════════════════════════
Avalia: estrutura dissertativa (introdução-desenvolvimento-conclusão),
progressão temática, defesa de ponto de vista, coerência lógica entre parágrafos.

• 200 → Argumentação consistente, encadeada e original. Ponto de vista
        claramente defendido com fundamentação sólida em todos os parágrafos.
• 160 → Argumentação adequada, bem estruturada e com desenvolvimento lógico.
• 120 → Argumentação previsível ou com alguma inconsistência lógica.
• 080 → Argumentação insuficiente. Ideias soltas ou repetição sem aprofundamento.
• 040 → Ausência quase total. Texto descritivo ou narrativo.
• 000 → Sem argumentação identificável.

═══════════════════════════════════════════════════════════════════
COMPETÊNCIA 4 — Mecanismos Linguísticos de Coesão Textual
═══════════════════════════════════════════════════════════════════
Avalia: conectivos (adversativos, conclusivos, explicativos, causais, aditivos),
referenciação (pronomes, sinônimos, elipses), progressão coesiva entre parágrafos.

• 200 → Coesão excelente. Conectivos variados e precisos. Transição fluida
        entre todos os parágrafos. Nenhuma ruptura perceptível.
• 160 → Boa coesão. Conectivos variados com poucas imprecisões.
• 120 → Coesão básica. Conectivos simples e repetitivos. Progressão presente.
• 080 → Coesão precária. Rupturas frequentes, parágrafos desconexos.
• 040 → Coesão ausente. Texto fragmentado sem articulação.
• 000 → Texto incoerente e sem articulação mínima.

═══════════════════════════════════════════════════════════════════
COMPETÊNCIA 5 — Proposta de Intervenção (respeito aos Direitos Humanos)
═══════════════════════════════════════════════════════════════════
Avalia 5 elementos obrigatórios: AGENTE + AÇÃO + MODO/MEIO + EFEITO + FINALIDADE.

• 200 → Proposta COMPLETA com todos os 5 elementos explícitos e detalhados,
        articulada com a argumentação, respeitando os direitos humanos.
• 160 → Proposta com 4 elementos presentes. Boa articulação com o texto.
• 120 → Proposta com 3 elementos. Presente mas com lacunas notáveis.
• 080 → Proposta com 1-2 elementos. Muito vaga e superficial.
• 040 → Proposta apenas mencionada, sem detalhamento algum.
• 000 → AUSENTE ou que viola direitos humanos (discriminatória, que propõe
        punições cruéis, que defende supressão de direitos fundamentais).

═══════════════════════════════════════════════════════════════════
ZERADORES AUTOMÁTICOS — nota_total DEVE ser 0
═══════════════════════════════════════════════════════════════════
• Fuga completa ao tema proposto
• Menos de ~100 palavras digitadas (equivalente a 7 linhas manuscritas)
• Cópia integral dos textos motivadores
• Proposta de intervenção que viola direitos humanos

═══════════════════════════════════════════════════════════════════
REGRAS ABSOLUTAS DE SAÍDA
═══════════════════════════════════════════════════════════════════
• Responda SOMENTE com JSON válido — ZERO texto antes ou depois
• Notas DEVEM ser múltiplos de 40: somente 0, 40, 80, 120, 160 ou 200
• nota_total = soma exata de c1+c2+c3+c4+c5
• justificativa: análise técnica com citação de TRECHOS REAIS da redação
• erros: 2-4 problemas específicos com localização (ex: "1º parágrafo: ...")
• dicas: 2-3 sugestões práticas e acionáveis (ex: "Substitua X por Y")
"""

PROMPT_CORRECAO = """\
Corrija a redação abaixo seguindo RIGOROSAMENTE os critérios do INEP.

━━━ DADOS PRÉ-CALCULADOS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TEMA: {tema}
PALAVRAS: {total_palavras} | PARÁGRAFOS: {total_paragrafos} | LINHAS: {total_linhas}
CONECTIVOS DETECTADOS: {conectivos}
PROPOSTA DE INTERVENÇÃO DETECTADA: {tem_proposta}
DIVERSIDADE DE VOCABULÁRIO (palavras longas): {palavras_longas}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REDAÇÃO:
{redacao}

━━━ CHECKLIST ANTES DE AVALIAR ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Li a redação completa antes de atribuir notas?
□ As justificativas citam trechos REAIS da redação?
□ Todas as notas são múltiplos de 40?
□ nota_total = soma exata das 5 competências?
□ Se há fuga ao tema → todas as notas = 0?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

JSON DE SAÍDA (sem nenhum texto adicional):
{{
  "fuga_ao_tema": false,
  "violacao_direitos_humanos": false,
  "competencias": {{
    "c1": {{
      "nota": 0,
      "justificativa": "Análise técnica com exemplos reais do texto entre aspas",
      "erros": ["Parágrafo X: descrição do erro específico"],
      "dicas": ["Sugestão prática e acionável"]
    }},
    "c2": {{
      "nota": 0,
      "justificativa": "Análise técnica com exemplos reais do texto entre aspas",
      "erros": ["Parágrafo X: descrição do erro específico"],
      "dicas": ["Sugestão prática e acionável"]
    }},
    "c3": {{
      "nota": 0,
      "justificativa": "Análise técnica com exemplos reais do texto entre aspas",
      "erros": ["Parágrafo X: descrição do erro específico"],
      "dicas": ["Sugestão prática e acionável"]
    }},
    "c4": {{
      "nota": 0,
      "justificativa": "Análise técnica com exemplos reais do texto entre aspas",
      "erros": ["Parágrafo X: descrição do erro específico"],
      "dicas": ["Sugestão prática e acionável"]
    }},
    "c5": {{
      "nota": 0,
      "justificativa": "Análise técnica com exemplos reais do texto entre aspas",
      "erros": ["Parágrafo X: descrição do erro específico"],
      "dicas": ["Sugestão prática e acionável"]
    }}
  }},
  "nota_total": 0,
  "feedback_geral": "Parágrafo construtivo citando pontos fortes e as 2-3 áreas mais urgentes de melhoria",
  "plano_estudos": [
    {{
      "competencia": "C1",
      "foco": "Tópico específico para estudar (ex: Regência Verbal)",
      "exercicio": "Exercício prático com instrução clara (ex: Reescreva os 3 primeiros parágrafos...)",
      "prioridade": "alta"
    }}
  ]
}}
"""

# ---------------------------------------------------------------------------
# Pré-análise textual (sem IA)
# ---------------------------------------------------------------------------

def pre_analisar(redacao: str) -> PreAnalise:
    """Extrai métricas textuais sem usar IA para enriquecer o prompt."""
    texto_lower = redacao.lower()
    palavras = [p for p in redacao.split() if p.strip()]

    # Parágrafos: tenta separar por linha em branco, senão por quebra de linha
    paragrafos = [p.strip() for p in re.split(r"\n\s*\n", redacao) if p.strip()]
    if len(paragrafos) <= 1:
        paragrafos = [l.strip() for l in redacao.split("\n") if len(l.strip()) > 30]

    linhas = [l for l in redacao.split("\n") if l.strip()]
    encontrados = sorted({c for c in TODOS_CONECTIVOS if c in texto_lower})

    termos_proposta = [
        "portanto", "assim", "logo", "deve", "deveria", "é necessário",
        "cabe ao", "o governo", "a escola", "o estado", "é preciso",
        "propõe-se", "sugere-se", "política pública", "medida", "ação",
    ]
    tem_proposta = any(t in texto_lower for t in termos_proposta)

    palavras_longas = {
        w.lower().strip(".,;:!?\"'()[]") for w in palavras
        if len(w.strip(".,;:!?\"'()[]")) >= 8
    }

    return PreAnalise(
        total_palavras=len(palavras),
        total_paragrafos=max(len(paragrafos), 1),
        total_linhas=len(linhas),
        conectivos_encontrados=encontrados,
        tem_proposta_intervencao=tem_proposta,
        palavras_longas_count=len(palavras_longas),
    )

# ---------------------------------------------------------------------------
# Validação e sanitização
# ---------------------------------------------------------------------------

def _sanitizar_nota(nota: object) -> int:
    """Arredonda qualquer valor para o múltiplo de 40 mais próximo (0-200)."""
    try:
        n = int(nota)
    except (TypeError, ValueError):
        return 0
    n = max(0, min(200, n))
    return min(NOTAS_VALIDAS, key=lambda x: abs(x - n))

def _limpar_json(texto: str) -> str:
    """Remove artefatos de markdown e extrai o JSON do texto da IA."""
    texto = re.sub(r"^```(?:json)?\s*", "", texto.strip(), flags=re.MULTILINE)
    texto = re.sub(r"\s*```$", "", texto, flags=re.MULTILINE)
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    return match.group(0) if match else texto.strip()

def _validar_e_corrigir(dados: dict) -> dict:
    """
    Valida o JSON da IA e corrige inconsistências:
    - Garante notas múltiplas de 40
    - Recalcula nota_total (fonte da verdade = soma das competências)
    - Aplica zeradores se necessário
    - Reordena plano de estudos por urgência (pior nota primeiro)
    """
    comp = dados.setdefault("competencias", {})

    for chave in ("c1", "c2", "c3", "c4", "c5"):
        c = comp.setdefault(chave, {})
        c["nota"]         = _sanitizar_nota(c.get("nota", 0))
        c["justificativa"] = str(c.get("justificativa", ""))
        # Garante listas (IA às vezes retorna string única)
        for campo in ("erros", "dicas"):
            val = c.get(campo, [])
            c[campo] = [val] if isinstance(val, str) and val else (val if isinstance(val, list) else [])

    # Aplicar zeradores
    if dados.get("fuga_ao_tema") or dados.get("violacao_direitos_humanos"):
        for chave in ("c1", "c2", "c3", "c4", "c5"):
            comp[chave]["nota"] = 0

    # Recalcular nota_total (não confiar no valor da IA)
    dados["nota_total"] = sum(comp[c]["nota"] for c in ("c1", "c2", "c3", "c4", "c5"))

    # Reordenar plano de estudos: piores notas primeiro
    plano = dados.get("plano_estudos", [])
    mapa_prioridade = {
        c: ("alta" if comp[c]["nota"] <= 80 else "media" if comp[c]["nota"] <= 120 else "baixa")
        for c in ("c1", "c2", "c3", "c4", "c5")
    }
    for item in plano:
        chave = item.get("competencia", "").lower()
        if chave in mapa_prioridade:
            item["prioridade"] = mapa_prioridade[chave]

    dados["plano_estudos"] = plano
    return dados

# ---------------------------------------------------------------------------
# Parse
# ---------------------------------------------------------------------------

def _parse_resultado(dados: dict, pre: PreAnalise) -> ResultadoCorrecao:
    comp = dados["competencias"]

    def make_comp(c: dict) -> Competencia:
        return Competencia(
            nota=c["nota"],
            justificativa=c["justificativa"],
            erros=c.get("erros", []),
            dicas=c.get("dicas", []),
        )

    return ResultadoCorrecao(
        c1=make_comp(comp["c1"]),
        c2=make_comp(comp["c2"]),
        c3=make_comp(comp["c3"]),
        c4=make_comp(comp["c4"]),
        c5=make_comp(comp["c5"]),
        nota_total=dados["nota_total"],
        fuga_ao_tema=bool(dados.get("fuga_ao_tema", False)),
        violacao_direitos_humanos=bool(dados.get("violacao_direitos_humanos", False)),
        feedback_geral=dados.get("feedback_geral", ""),
        plano_estudos=dados.get("plano_estudos", []),
        pre_analise=pre,
    )

# ---------------------------------------------------------------------------
# Função pública principal
# ---------------------------------------------------------------------------

def corrigir_redacao(redacao: str, tema: str, api_key: str) -> ResultadoCorrecao:
    """
    Corrige uma redação do ENEM usando Google Gemini.

    Args:
        redacao:  Texto completo da redação.
        tema:     Tema proposto (melhora a avaliação da C2).
        api_key:  Chave da API Google Gemini.

    Returns:
        ResultadoCorrecao com notas validadas, justificativas e plano de estudos.

    Raises:
        ValueError:   Redação muito curta ou API Key inválida.
        RuntimeError: API falhou após todas as tentativas.
    """
    if len(redacao.split()) < 50:
        raise ValueError("Redação muito curta. Escreva pelo menos 50 palavras.")

    pre = pre_analisar(redacao)
    logger.info(
        "Pré-análise: %d palavras | %d parágrafos | %d conectivos",
        pre.total_palavras, pre.total_paragrafos, len(pre.conectivos_encontrados),
    )

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=MODELO,
        system_instruction=PROMPT_SISTEMA,
        generation_config=genai.GenerationConfig(
            temperature=0.2,       # Baixo = respostas mais consistentes
            top_p=0.8,
            max_output_tokens=2048,
        ),
    )

    prompt = PROMPT_CORRECAO.format(
        tema=tema,
        total_palavras=pre.total_palavras,
        total_paragrafos=pre.total_paragrafos,
        total_linhas=pre.total_linhas,
        conectivos=(", ".join(pre.conectivos_encontrados) or "nenhum detectado"),
        tem_proposta=("Sim" if pre.tem_proposta_intervencao else "Não detectada"),
        palavras_longas=pre.palavras_longas_count,
        redacao=redacao,
    )

    ultimo_erro: Exception = RuntimeError("Erro desconhecido")

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            logger.info("Gemini — tentativa %d/%d", tentativa, MAX_TENTATIVAS)
            response = model.generate_content(prompt)
            dados = json.loads(_limpar_json(response.text.strip()))
            dados = _validar_e_corrigir(dados)
            logger.info("✓ Nota calculada: %d/1000", dados["nota_total"])
            return _parse_resultado(dados, pre)

        except json.JSONDecodeError as e:
            logger.warning("JSON inválido (tentativa %d): %s", tentativa, e)
            ultimo_erro = e

        except google_exceptions.ResourceExhausted:
            espera = INTERVALO_BASE * tentativa
            logger.warning("Rate limit — aguardando %ds...", espera)
            time.sleep(espera)
            ultimo_erro = RuntimeError("Limite de requisições atingido. Aguarde alguns instantes.")

        except google_exceptions.InvalidArgument as e:
            raise ValueError(f"API Key inválida: {e}") from e

        except Exception as e:
            logger.warning("Erro inesperado (tentativa %d): %s", tentativa, e)
            ultimo_erro = e
            if tentativa < MAX_TENTATIVAS:
                time.sleep(INTERVALO_BASE)

    raise RuntimeError(
        f"Falha após {MAX_TENTATIVAS} tentativas. Último erro: {ultimo_erro}"
    ) from ultimo_erro

# ---------------------------------------------------------------------------
# Serialização
# ---------------------------------------------------------------------------

def resultado_para_dict(r: ResultadoCorrecao) -> dict:
    """Converte ResultadoCorrecao para dict serializável em JSON."""

    def comp_dict(c: Competencia) -> dict:
        return {"nota": c.nota, "justificativa": c.justificativa,
                "erros": c.erros, "dicas": c.dicas}

    out = {
        "nota_total": r.nota_total,
        "fuga_ao_tema": r.fuga_ao_tema,
        "violacao_direitos_humanos": r.violacao_direitos_humanos,
        "feedback_geral": r.feedback_geral,
        "competencias": {k: comp_dict(getattr(r, k)) for k in ("c1", "c2", "c3", "c4", "c5")},
        "plano_estudos": r.plano_estudos,
    }
    if r.pre_analise:
        out["pre_analise"] = asdict(r.pre_analise)
    return out
