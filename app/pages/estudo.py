import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from src.services.study_plan_service import gerar_plano_estudos

st.set_page_config(
    page_title="Plano de Estudos",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Plano de Estudos Personalizado")
st.markdown("Receba um plano de estudos adaptado às suas necessidades específicas.")

# Entrada de dados
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🎯 Seu Desempenho")
    
    # Opção de usar notas da correção anterior
    if 'notas_para_estudo' in st.session_state:
        notas = st.session_state['notas_para_estudo']
        st.info("Usando notas da última correção.")
        
        # Mostra as notas
        for i in range(5):
            st.metric(f"Competência {i+1}", f"{notas[f'competencia_{i+1}']}/200")
    else:
        st.warning("Nenhuma correção recente encontrada.")
        st.markdown("Digite manualmente suas notas:")
        
        notas = {}
        for i in range(5):
            nota = st.number_input(f"Competência {i+1}", min_value=0, max_value=200, value=100, step=10)
            notas[f'competencia_{i+1}'] = nota

with col2:
    st.subheader("⚙️ Configurações")
    
    tempo_estudo = st.select_slider(
        "Tempo disponível por semana:",
        options=["pouco (2-3h)", "médio (4-6h)", "muito (7-10h+)", "intensivo (10h+)"],
        value="médio (4-6h)"
    )
    
    data_prova = st.date_input("Data da prova (opcional):")
    
    objetivos = st.multiselect(
        "Objetivos específicos:",
        ["Aumentar nota geral", "Melhorar gramática", "Fortalecer argumentação", 
         "Melhorar coesão", "Aprender repertório", "Dominar proposta de intervenção"]
    )

# Erros manuais (opcional)
with st.expander("Adicionar erros específicos (opcional)"):
    erros_manuais = st.text_area(
        "Liste os erros que você sabe que comete:",
        placeholder="Exemplo:\n- Uso excessivo de vírgulas\n- Argumentos rasos\n- Falta de conectivos"
    )

# Botão para gerar plano
if st.button("📚 Gerar Meu Plano de Estudos", type="primary", use_container_width=True):
    with st.spinner("Criando plano personalizado..."):
        # Prepara erros
        erros_lista = []
        if erros_manuais:
            erros_lista = [e.strip() for e in erros_manuais.split('\n') if e.strip()]
        
        # Gera plano
        plano = gerar_plano_estudos(notas, erros_lista, tempo_estudo)
        
        if "erro" in plano:
            st.error(f"❌ Erro ao gerar plano: {plano['erro']}")
        else:
            # Prioridade
            st.success(f"🎯 **Prioridade de estudo:** {plano['prioridade']}")
            st.markdown("---")
            
            # Plano detalhado
            for item in plano.get("plano_de_estudos", []):
                with st.expander(f"📌 Semana {item['semana']}: {item['foco']} ({item['carga_horaria']})", expanded=True):
                    st.markdown("**Atividades recomendadas:**")
                    for atividade in item["atividades"]:
                        st.markdown(f"- {atividade}")
            
            # Recursos sugeridos
            if plano.get("recursos_sugeridos"):
                st.subheader("📖 Recursos Sugeridos")
                for recurso in plano["recursos_sugeridos"]:
                    st.markdown(f"- {recurso}")
            
            # Dicas extras
            st.subheader("💡 Dicas para otimizar seus estudos")
            st.info("""
            1. **Pratique pelo menos 1 redação por semana**
            2. **Revise a correção anterior antes de escrever a próxima**
            3. **Leia redações nota 1000 para referência**
            4. **Crie um caderno de erros recorrentes**
            5. **Treine parágrafos específicos, não redações inteiras sempre**
            """)

# Download do plano
if 'plano' in locals() and "erro" not in plano:
    import json
    plano_json = json.dumps(plano, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 Baixar plano (JSON)",
        data=plano_json,
        file_name="plano_estudos.json",
        mime="application/json",
        use_container_width=True
    )

st.markdown("---")
st.caption("📚 Plano adaptado ao seu desempenho e disponibilidade de tempo.")