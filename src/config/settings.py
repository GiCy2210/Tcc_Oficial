import os
from dotenv import load_dotenv
import google.generativeai as genai
import spacy
from spacy.language import Language

# Carrega variáveis de ambiente
load_dotenv()

# ========== CONFIGURAÇÃO GEMINI ==========
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    MODEL = genai.GenerativeModel("gemini-2.5-flash")
else:
    MODEL = None
    print("⚠️  ERRO: Chave da API Gemini não encontrada!")

# ========== CONFIGURAÇÃO SPACY ==========
def carregar_spacy():
    """Carrega o modelo de português do spaCy"""
    try:
        # Tenta carregar o modelo médio (melhor para análise)
        nlp = spacy.load("pt_core_news_md")
        print("✅ spaCy carregado com modelo médio")
    except OSError:
        try:
            # Se não tiver o médio, tenta o pequeno
            nlp = spacy.load("pt_core_news_sm")
            print("✅ spaCy carregado com modelo pequeno")
        except OSError:
            print("❌ Modelo do spaCy não encontrado!")
            print("📝 Execute: python -m spacy download pt_core_news_md")
            nlp = None
    return nlp

# Carrega o modelo
nlp = carregar_spacy()

# Configurações do sistema
MAX_REDACOES_HISTORICO = 10
CACHE_TEMPO_SEGUNDOS = 3600
    
# Competências do ENEM
COMPETENCIAS = {
    1: "Domínio da norma culta",
    2: "Compreensão do tema e repertório",
    3: "Organização e argumentação",
    4: "Coesão e articulação",
    5: "Proposta de intervenção"
}