import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Sistema de Correção ENEM",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🎓 Sistema Inteligente de Correção de Redações ENEM")
st.markdown("---")

# Mensagem de boas-vindas
st.markdown("""
## 👋 Bem-vindo!

Este sistema utiliza **Inteligência Artificial** para ajudar você a melhorar suas redações no modelo ENEM.

### 📌 Navegação
Use o menu lateral para acessar as funcionalidades:

- **📝 Corretor** - Envie sua redação e receba correção imediata
- **🔍 Análise de Erros** - Identifique erros específicos
- **📚 Plano de Estudos** - Receba um plano personalizado

### 🎯 Objetivo
Ajudar estudantes a identificar pontos fracos e melhorar continuamente seu desempenho na redação do ENEM.
""")

# Sidebar com informações
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2232/2232688.png", width=100)
    st.markdown("---")
    st.markdown("### 📊 Status")
    st.markdown("✅ Sistema Online")
    st.markdown("🤖 IA: Google Gemini")
    st.markdown("📝 Modelo: ENEM 5 Competências")
    st.markdown("---")
    st.markdown("### 👨‍🎓 TCC")
    st.markdown("**Autor:** Giovane Micael")
    st.markdown("**Orientador:** Prof. Sérgio Gabriel")
    st.markdown("**Ano:** 2026")