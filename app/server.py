"""
server.py — v3
API Flask do CorretorIA ENEM.
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS

# ── Configuração de Caminhos ──────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))
sys.path.insert(0, str(BASE_DIR / "src" / "services"))

# ── FUNÇÃO TEMPORÁRIA (MOCK) ──────────────────────────────────────────────────
# Nome alterado para 'chat_tutor_funcao' para não dar conflito com a rota
def chat_tutor_funcao(pergunta, contexto, api_key):
    return "O serviço de chat está sendo configurado no correction_service.py."

# ── Imports dos Serviços ──────────────────────────────────────────────────────
try:
    from correction_service import corrigir_redacao, resultado_para_dict # type: ignore
    from database_service import ( # type: ignore
        buscar_correcao, buscar_historico, buscar_por_tema, contar_total,
        deletar_correcao, distribuicao_notas, evolucao_temporal,
        media_notas, salvar_correcao,
    )
    # Proteção para o exportar_csv
    try:
        from database_service import exportar_csv # type: ignore
    except ImportError:
        def exportar_csv(limit=200): return "id,tema,nota\n0,Sem dados,0"

    from theme_service import gerar_tema, temas_predefinidos # type: ignore
except ImportError as e:
    logging.error(f"Erro de importação controlado: {e}")

# ── App ───────────────────────────────────────────────────────────────────────

app = Flask(__name__, static_folder=None)
CORS(app, resources={r"/api/*": {"origins": "*"}})

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

API_KEY_ENV = os.environ.get("GEMINI_API_KEY", "")

# ── Helpers ───────────────────────────────────────────────────────────────────

def _err(msg: str, code: int = 400):
    return jsonify({"erro": msg}), code

def _key() -> str:
    """Retorna a API key configurada no servidor (.env). Nunca vem do frontend."""
    return API_KEY_ENV

# ── Frontend ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(Path(__file__).parent, "index.html")

# ── Correção ──────────────────────────────────────────────────────────────────

@app.route("/api/corrigir", methods=["POST"])
def corrigir():
    data    = request.get_json(silent=True) or {}
    redacao = data.get("redacao", "").strip()
    tema    = data.get("tema",    "Tema não informado").strip()
    api_key = _key()

    if not redacao:               return _err("Texto da redação está vazio.")
    if len(redacao.split()) < 50: return _err("Redação muito curta. Mínimo 50 palavras.")
    if not api_key:               return _err("Chave Gemini API não configurada no servidor. Contate o administrador.")

    try:
        obj       = corrigir_redacao(redacao, tema, api_key)
        resultado = resultado_para_dict(obj)
        resultado["tema"] = tema
        resultado["id"]   = salvar_correcao(tema, redacao, resultado)
        return jsonify(resultado)
    except Exception as e:
        logger.exception("Erro em /api/corrigir")
        return _err(f"Erro interno: {e}", 500)

# ── Chat tutor ────────────────────────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def api_chat_endpoint(): # NOME ÚNICO PARA EVITAR ASSERTIONERROR
    data       = request.get_json(silent=True) or {}
    pergunta   = data.get("pergunta", "").strip()
    contexto   = data.get("contexto", {})
    api_key    = _key()

    if not pergunta: return _err("Pergunta não pode ser vazia.")
    if not api_key:  return _err("Chave Gemini não configurada no servidor.")

    try:
        # Chama a função que definimos no topo
        resposta = chat_tutor_funcao(pergunta, contexto, api_key)
        return jsonify({"resposta": resposta})
    except Exception as e:
        return _err(f"Erro no chat: {e}", 500)

# ── Histórico ─────────────────────────────────────────────────────────────────

@app.route("/api/historico", methods=["GET"])
def historico():
    limit  = min(int(request.args.get("limit", 20)), 100)
    offset = max(int(request.args.get("offset", 0)), 0)
    try:
        dados = buscar_historico(limit, offset)
        return jsonify({"items": dados, "total": contar_total()})
    except Exception as e:
        return _err(str(e), 500)

@app.route("/api/historico/buscar", methods=["GET"])
def historico_buscar():
    q = request.args.get("q", "").strip()
    if not q: return _err("Informe ?q=termo")
    return jsonify(buscar_por_tema(q))

@app.route("/api/historico/<int:id>", methods=["GET"])
def historico_detalhe(id: int):
    dado = buscar_correcao(id)
    return jsonify(dado) if dado else _err("Não encontrado.", 404)

@app.route("/api/historico/<int:id>", methods=["DELETE"])
def historico_deletar(id: int):
    if deletar_correcao(id):
        return jsonify({"ok": True})
    return _err("Não encontrado.", 404)

# ── Estatísticas ──────────────────────────────────────────────────────────────

@app.route("/api/stats", methods=["GET"])
def stats():            return jsonify(media_notas())

@app.route("/api/stats/evolucao", methods=["GET"])
def stats_evol():
    limit = min(int(request.args.get("limit", 30)), 100)
    # Fallback se a função não existir no DB_SERVICE
    try:
        from database_service import evolucao_temporal # type: ignore
        return jsonify(evolucao_temporal(limit))
    except:
        return jsonify([])

@app.route("/api/stats/distribuicao", methods=["GET"])
def stats_dist():
    try:
        from database_service import distribuicao_notas # type: ignore
        return jsonify(distribuicao_notas())
    except:
        return jsonify({})

# ── Temas ─────────────────────────────────────────────────────────────────────

@app.route("/api/temas", methods=["GET"])
def temas():            return jsonify(temas_predefinidos())

@app.route("/api/temas/gerar", methods=["POST"])
def temas_gerar():
    data    = request.get_json(silent=True) or {}
    api_key = _key()
    if not api_key: return _err("Chave Gemini não configurada no servidor.")
    try:
        return jsonify(gerar_tema(api_key))
    except Exception as e:
        return _err(f"Erro ao gerar tema: {e}", 500)

# ── Exportação ────────────────────────────────────────────────────────────────

@app.route("/api/exportar", methods=["GET"])
def exportar():
    limit = min(int(request.args.get("limit", 200)), 500)
    csv_data = exportar_csv(limit)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=correcoes_enem.csv"},
    )

# ── Health ────────────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():           return jsonify({"status": "ok", "versao": "3.0"})

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000, host="0.0.0.0")