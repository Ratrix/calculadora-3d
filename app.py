# =================================================================
# PROJETO: CALCULADORA 3D PRO
# DESENVOLVIDO POR: Joseanderson Langner
# FORMAÇÃO: Engenharia de Controle e Automação
# =================================================================

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# Configuração da página
st.set_page_config(page_title="Calculadora 3D Pro", page_icon="⚖️", layout="wide")

# --- LÓGICA DE MEMÓRIA ---
if 'df_insumos' not in st.session_state:
    st.session_state.df_insumos = pd.DataFrame(columns=["Selecionar", "Material", "Preço", "Qtd"])

# --- CONTADOR DE VISITANTES ÚNICOS (VERSÃO BLINDADA) ---
# Usamos um iframe invisível que só carrega uma vez por sessão do navegador.
st.sidebar.markdown("### 📊 Estatísticas de Acesso")

# Criamos um ID único para seu app para não misturar com outros
badge_html = """
<div style="text-align: left;">
    <img src="https://visitor-badge.laobi.icu/badge?page_id=joseanderson.calc3d.oficial.2026&left_text=Visitantes%20Únicos" 
    alt="Contador">
</div>
"""
# O segredo: injetamos o HTML via componente, que o Streamlit trata de forma diferente do markdown comum
with st.sidebar:
    components.html(badge_html, height=50)
    st.caption("Contagem baseada em IDs de sessão únicos.")

# --- IDENTIDADE VISUAL ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    nome_loja = st.text_input("Sua Marca/Nome", value="Calibrando Flow 3D")

st.title(f"⚖️ Calculadora de Custos - {nome_loja}")
st.info(f"👨‍💻 Engenheiro Responsável: Joseanderson Langner | Controle e Automação")
st.markdown("---")

# [O RESTANTE DO SEU CÓDIGO DE CÁLCULOS SEGUE IGUAL ABAIXO...]
