import pytest
import sys
from pathlib import Path

# 1. CONFIGURAÇÃO DE PATHS (Forçando todos os níveis de pastas)
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))
sys.path.insert(0, str(BASE_DIR / "src" / "services"))
sys.path.insert(0, str(BASE_DIR / "app"))

# 2. IMPORTS DOS MÓDULOS
# Tentamos o import direto (que o Python usará na execução)
# O "# type: ignore" serve para calar o VS Code se ele for teimoso
try:
    import database_service # type: ignore
    from correction_service import Competencia, ResultadoCorrecao, resultado_para_dict # type: ignore
    from server import app # type: ignore
except ImportError:
    # Caso o VS Code só aceite o caminho completo no editor
    from src.services import database_service
    from src.services.correction_service import Competencia, ResultadoCorrecao, resultado_para_dict
    from app.server import app
# ===== TESTES: DATABASE SERVICE =====

def test_init_db_cria_arquivo(tmp_path, monkeypatch):
    monkeypatch.setattr(database_service, "DB_PATH", tmp_path / "test.db")
    database_service.init_db()
    assert (tmp_path / "test.db").exists()

def test_salvar_e_buscar_correcao(tmp_path, monkeypatch):
    monkeypatch.setattr(database_service, "DB_PATH", tmp_path / "test.db")

    resultado_mock = {
        "nota_total": 680,
        "fuga_ao_tema": False,
        "violacao_direitos_humanos": False,
        "feedback_geral": "Boa redação com espaço para melhoras.",
        "competencias": {
            "c1": {"nota": 120, "justificativa": "ok", "erros": [], "dicas": []},
            "c2": {"nota": 160, "justificativa": "ok", "erros": [], "dicas": []},
            "c3": {"nota": 120, "justificativa": "ok", "erros": [], "dicas": []},
            "c4": {"nota": 160, "justificativa": "ok", "erros": [], "dicas": []},
            "c5": {"nota": 120, "justificativa": "ok", "erros": [], "dicas": []},
        },
        "plano_estudos": []
    }

    id_salvo = database_service.salvar_correcao(
        tema="Tema teste",
        redacao="Texto de teste da redação.",
        resultado=resultado_mock
    )
    assert id_salvo == 1

    historico = database_service.buscar_historico()
    assert len(historico) == 1
    assert historico[0]["nota_total"] == 680
    assert historico[0]["tema"] == "Tema teste"

def test_buscar_correcao_inexistente(tmp_path, monkeypatch):
    monkeypatch.setattr(database_service, "DB_PATH", tmp_path / "test.db")
    result = database_service.buscar_correcao(999)
    assert result is None

def test_media_notas_sem_dados(tmp_path, monkeypatch):
    monkeypatch.setattr(database_service, "DB_PATH", tmp_path / "test.db")
    media = database_service.media_notas()
    assert media["total_redacoes"] == 0

def test_media_notas_com_dados(tmp_path, monkeypatch):
    monkeypatch.setattr(database_service, "DB_PATH", tmp_path / "test.db")

    resultado = lambda nota: {
        "nota_total": nota,
        "fuga_ao_tema": False,
        "violacao_direitos_humanos": False,
        "feedback_geral": "",
        "competencias": {
            k: {"nota": nota // 5, "justificativa": "", "erros": [], "dicas": []}
            for k in ["c1","c2","c3","c4","c5"]
        },
        "plano_estudos": []
    }

    database_service.salvar_correcao("T1", "R1", resultado(600))
    database_service.salvar_correcao("T2", "R2", resultado(800))

    media = database_service.media_notas()
    assert media["total_redacoes"] == 2
    assert media["media_total"] == 700

# ===== TESTES: CORRECTION SERVICE (sem API) =====

def test_resultado_para_dict_estrutura():
    mock = ResultadoCorrecao(
        c1=Competencia(160, "Bom domínio", ["erro1"], ["dica1"]),
        c2=Competencia(120, "Tema parcial", [], ["dica2"]),
        c3=Competencia(80,  "Argumentação fraca", ["e1", "e2"], []),
        c4=Competencia(160, "Boa coesão", [], []),
        c5=Competencia(120, "Proposta vaga", [], ["dica3"]),
        nota_total=640,
        fuga_ao_tema=False,
        violacao_direitos_humanos=False,
        feedback_geral="Feedback geral aqui.",
        plano_estudos=[{"competencia": "C3", "foco": "Argumentação", "exercicio": "Escreva mais", "prioridade": "alta"}]
    )

    d = resultado_para_dict(mock)
    assert d["nota_total"] == 640
    assert d["fuga_ao_tema"] is False
    assert "c1" in d["competencias"]
    assert d["competencias"]["c1"]["nota"] == 160
    assert d["competencias"]["c3"]["erros"] == ["e1", "e2"]
    assert len(d["plano_estudos"]) == 1

def test_nota_total_soma_competencias():
    notas = [200, 160, 120, 160, 200]
    mock = ResultadoCorrecao(
        c1=Competencia(notas[0], "", [], []),
        c2=Competencia(notas[1], "", [], []),
        c3=Competencia(notas[2], "", [], []),
        c4=Competencia(notas[3], "", [], []),
        c5=Competencia(notas[4], "", [], []),
        nota_total=sum(notas),
        fuga_ao_tema=False,
        violacao_direitos_humanos=False,
        feedback_geral="",
        plano_estudos=[]
    )
    d = resultado_para_dict(mock)
    soma = sum(d["competencias"][c]["nota"] for c in ["c1","c2","c3","c4","c5"])
    assert soma == d["nota_total"]

# ===== TESTES: FLASK API =====

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database_service, "DB_PATH", tmp_path / "test.db")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_api_corrigir_sem_redacao(client):
    res = client.post("/api/corrigir", json={"redacao": "", "tema": "teste", "api_key": "fake"})
    assert res.status_code == 400
    assert "erro" in res.get_json()

def test_api_corrigir_redacao_curta(client):
    res = client.post("/api/corrigir", json={"redacao": "texto curto", "tema": "teste", "api_key": "fake"})
    assert res.status_code == 400

def test_api_corrigir_sem_api_key(client):
    res = client.post("/api/corrigir", json={"redacao": " ".join(["palavra"] * 60), "tema": "teste", "api_key": ""})
    assert res.status_code == 400

def test_api_historico_vazio(client):
    res = client.get("/api/historico")
    assert res.status_code == 200
    data = res.get_json()
    assert data["items"] == []
    assert data["total"] == 0

def test_api_stats_vazio(client):
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.get_json()
    assert data["total_redacoes"] == 0

def test_api_historico_detalhe_inexistente(client):
    res = client.get("/api/historico/999")
    assert res.status_code == 404