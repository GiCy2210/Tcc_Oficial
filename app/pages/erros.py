import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.services.error_service import analisar_erros
from src.utils.nlp_utils import analisador

st.set_page_config(
    page_title="Análise de Erros",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Análise Detalhada de Erros")
st.markdown("Identifique erros específicos na sua redação e receba sugestões de correção.")

# Verifica se veio do corretor
if 'redacao_para_analise' in st.session_state:
    redacao = st.session_state['redacao_para_analise']
    correcao = st.session_state.get('correcao_para_analise', None)
else:
    # Opção de digitar nova redação
    redacao = st.text_area(
        "Digite ou cole sua redação para análise:",
        height=300,
        placeholder="Cole aqui sua redação..."
    )

# Botão de análise
if st.button("🔍 Analisar Erros", type="primary", use_container_width=True):
    if not redacao.strip():
        st.error("❌ Digite uma redação para análise.")
    else:
        with st.spinner("Analisando erros com IA + NLP..."):
            # Análise com spaCy
            analise_nlp = analisador.analisar_gramatica(redacao)
            repeticoes = analisador.detectar_repeticao(redacao)
            densidade = analisador.calcular_densidade_lexical(redacao)
            palavras_chave = analisador.extrair_palavras_chave(redacao, 10)
            
            # Análise com IA
            erros = analisar_erros(redacao, correcao)
            
            # Exibe resultados em abas
            tab1, tab2, tab3, tab4 = st.tabs(["📋 Erros Gramaticais", "🔗 Erros de Coesão", "💭 Erros Argumentativos", "📊 Estatísticas NLP"])
            
            with tab1:
                st.subheader("Erros Gramaticais")
                if erros.get("erros_gramaticais"):
                    for erro in erros["erros_gramaticais"]:
                        with st.container():
                            st.markdown(f"**❌ Erro:** {erro['erro']}")
                            st.markdown(f"**📝 Trecho:** `{erro['trecho']}`")
                            st.markdown(f"**💡 Sugestão:** {erro['sugestao']}")
                            st.markdown("---")
                else:
                    st.success("✅ Nenhum erro gramatical grave detectado!")
            
            with tab2:
                st.subheader("Erros de Coesão")
                if erros.get("erros_coesao"):
                    for erro in erros["erros_coesao"]:
                        with st.container():
                            st.markdown(f"**❌ Erro:** {erro['erro']}")
                            st.markdown(f"**📝 Trecho:** `{erro['trecho']}`")
                            st.markdown(f"**💡 Sugestão:** {erro['sugestao']}")
                            st.markdown("---")
                else:
                    st.success("✅ Coesão textual adequada!")
            
            with tab3:
                st.subheader("Erros Argumentativos")
                if erros.get("erros_argumentativos"):
                    for erro in erros["erros_argumentativos"]:
                        with st.container():
                            st.markdown(f"**❌ Erro:** {erro['erro']}")
                            st.markdown(f"**📝 Trecho:** `{erro['trecho']}`")
                            st.markdown(f"**💡 Sugestão:** {erro['sugestao']}")
                            st.markdown("---")
                else:
                    st.success("✅ Argumentação consistente!")
            
            with tab4:
                st.subheader("Estatísticas do Texto (spaCy)")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Palavras", analise_nlp["num_tokens"])
                col2.metric("Frases", analise_nlp["num_sentencas"])
                col3.metric("Densidade Lexical", f"{densidade:.2f}")
                
                st.subheader("Classes Gramaticais")
                for classe, qtd in analise_nlp["classes_gramaticais"].items():
                    st.progress(qtd / max(analise_nlp["num_tokens"], 1), text=f"{classe}: {qtd}")
                
                st.subheader("Palavras-chave")
                for palavra, relevancia in palavras_chave:
                    st.markdown(f"- **{palavra}** (relevância: {relevancia})")
                
                if repeticoes:
                    st.subheader("⚠️ Palavras Repetidas")
                    for rep in repeticoes:
                        st.warning(f"**'{rep['palavra']}'** aparece {rep['vezes']} vezes. {rep['sugestao']}")
            
            # Sugestões gerais
            st.subheader("💡 Sugestões de Correção")
            for sugestao in erros.get("sugestoes_correcao", []):
                st.info(f"📌 {sugestao}")
            
            # Botão para ir para plano de estudos
            if st.button("📚 Gerar Plano de Estudos", use_container_width=True):
                st.session_state['notas_para_estudo'] = correcao['notas'] if correcao else None
                st.switch_page("app/pages/3_Estudos.py")

st.markdown("---")
st.caption("🔬 A análise combina IA generativa com processamento de linguagem natural (spaCy).")