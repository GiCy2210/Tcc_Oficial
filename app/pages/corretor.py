import sys
import os

# Adiciona a raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.services.correction_service import corrigir_redacao
from src.utils.validators import validar_redacao

st.set_page_config(
    page_title="Corretor de Redações",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Corretor de Redações ENEM")
st.markdown("Envie sua redação e receba uma correção completa baseada nas 5 competências do ENEM.")

# Layout em duas colunas
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📄 Sua Redação")
    redacao = st.text_area(
        "Digite ou cole sua redação abaixo:",
        height=400,
        placeholder="Cole aqui sua redação no formato ENEM...\n\nMínimo de 50 palavras, máximo de 500 palavras."
    )

with col2:
    st.subheader("⚙️ Configurações")
    mostrar_feedback = st.checkbox("Mostrar feedback detalhado", value=True)
    salvar_historico = st.checkbox("Salvar no histórico", value=False)
    
    st.markdown("---")
    st.markdown("### 📊 Competências Avaliadas")
    st.markdown("""
    1. **C1** - Norma culta (0-200)
    2. **C2** - Tema/Repertório (0-200)
    3. **C3** - Argumentação (0-200)
    4. **C4** - Coesão (0-200)
    5. **C5** - Intervenção (0-200)
    """)

# Botão de correção
if st.button("🚀 Corrigir Redação", type="primary", use_container_width=True):
    if not redacao.strip():
        st.error("❌ Por favor, digite ou cole uma redação para análise.")
    else:
        # Validação
        validacao = validar_redacao(redacao)
        if not validacao["valido"]:
            st.error(f"❌ {validacao['erro']}")
        else:
            st.success(f"✅ Redação validada: {validacao['palavras']} palavras")
            
            with st.spinner("🔄 Analisando sua redação com IA..."):
                correcao = corrigir_redacao(redacao)
                
                if "erro" in correcao:
                    st.error(f"❌ Erro na correção: {correcao['erro']}")
                else:
                    # Exibe notas
                    st.subheader("📊 Resultado da Correção")
                    notas = correcao["notas"]
                    
                    # Métricas em colunas
                    cols = st.columns(5)
                    comps = ["C1 - Norma", "C2 - Tema", "C3 - Argumento", "C4 - Coesão", "C5 - Intervenção"]
                    for i, col in enumerate(cols):
                        nota = notas[f'competencia_{i+1}']
                        col.metric(
                            label=comps[i],
                            value=f"{nota}/200",
                            delta=f"{nota - 120:+d}" if nota != 120 else None,
                            delta_color="normal"
                        )
                    
                    # Nota total em destaque
                    st.markdown("---")
                    nota_total = notas['total']
                    if nota_total >= 900:
                        st.balloons()
                        st.success(f"### 🎉 NOTA TOTAL: {nota_total}/1000 - PARABÉNS! 🎉")
                    elif nota_total >= 700:
                        st.info(f"### 📈 NOTA TOTAL: {nota_total}/1000 - BOM TRABALHO!")
                    elif nota_total >= 500:
                        st.warning(f"### ⚠️ NOTA TOTAL: {nota_total}/1000 - PODE MELHORAR")
                    else:
                        st.error(f"### ❌ NOTA TOTAL: {nota_total}/1000 - PRECISA REVISAR")
                    
                    # Feedback
                    if mostrar_feedback:
                        st.subheader("📖 Feedback Detalhado")
                        with st.expander("Pontos Fortes", expanded=True):
                            st.write(correcao['feedback']['pontos_fortes'])
                        with st.expander("Pontos a Melhorar", expanded=True):
                            st.write(correcao['feedback']['pontos_fracos'])
                    
                    # Botão para ir para análise de erros
                    if st.button("🔍 Analisar Erros Detalhadamente", use_container_width=True):
                        st.session_state['redacao_para_analise'] = redacao
                        st.session_state['correcao_para_analise'] = correcao
                        st.switch_page("app/pages/2_Erros.py")

st.markdown("---")
st.caption("💡 Dica: Redações mais completas e bem estruturadas recebem melhores análises.")