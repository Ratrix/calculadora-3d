import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora 3D - Calibrando Flow", page_icon="⚖️", layout="wide")

st.title("⚖️ Calculadora 3D Pro")
st.markdown("---")

# --- MEMÓRIA DOS DADOS ---
if 'df_insumos' not in st.session_state:
    st.session_state.df_insumos = pd.DataFrame(columns=["Selecionar", "Material", "Preço", "Qtd"])

# --- BARRA LATERAL (Custos Fixos e Payback) ---
st.sidebar.header("⚙️ Configurações Base")
custo_kwh = st.sidebar.number_input("Energia (R$/kWh)", value=0.98)
valor_sua_hora = st.sidebar.number_input("Sua Hora Técnica (R$)", value=30.0)
taxa_falha = st.sidebar.slider("Margem de Segurança/Falha (%)", 0, 30, 10)

st.sidebar.header("💰 Planejamento de Payback")
valor_maquina = st.sidebar.number_input("Valor da Máquina (R$)", value=2500.0)
meses_payback = st.sidebar.number_input("Quitar em quantos meses?", value=12, min_value=1)
uso_mensal_horas = st.sidebar.number_input("Horas de uso por mês", value=160, min_value=1)

# Cálculo da Depreciação por Objetivo Financeiro
# (Valor / Meses) = Quanto ela tem que render por mês. 
# (Rendimento Mensal / Horas de uso) = Custo de depreciação por hora de impressão.
depreciacao_hora = (valor_maquina / meses_payback) / uso_mensal_horas

st.sidebar.write(f"📊 **Custo de Máquina:** R$ {depreciacao_hora:.2f}/hora")

st.sidebar.header("🛠️ Tecnologia")
tecnologia = st.sidebar.selectbox("Tipo de Impressão", ["FDM (FILAMENTO)", "Resina"])
pot_media = 200 if tecnologia == "FDM (FILAMENTO)" else 60

# --- DADOS DO PROJETO ---
col_p1, col_p2 = st.columns(2)
with col_p1:
    nome_peca = st.text_input("Nome do Projeto", value="Peça Exemplo")
    preco_material = st.number_input("Preço do Material Base (R$/kg ou L)", value=160.0)
    
    st.write("Consumo de Material")
    c_col1, c_col2 = st.columns([2, 1])
    consumo_valor = c_col1.number_input("Qtd Consumida", min_value=0.0, step=0.1)
    unidade = c_col2.selectbox("Unidade", ["g", "kg", "ml", "L"])

with col_p2:
    st.write("Tempo de Impressão (Máquina)")
    h_col, m_col = st.columns(2)
    horas = h_col.number_input("Horas", min_value=0, value=1)
    minutos = m_col.number_input("Minutos", min_value=0, max_value=59, value=0)
    
    st.write("Custos de Engenharia")
    tempo_pos = st.number_input("Setup e Pós-Processo (min)", value=20)
    valor_modelagem = st.number_input("Valor da Modelagem 3D (R$)", value=0.0)

st.markdown("---")

# --- SEÇÃO DE INSUMOS EXTRAS ---
st.subheader("📦 Insumos e Materiais Extras")
with st.container():
    col_add1, col_add2, col_add3, col_add4 = st.columns([3, 1, 1, 1])
    with col_add1:
        novo_mat = st.text_input("Descrição (Lixa, Álcool, Caixa...)", key="input_mat")
    with col_add2:
        novo_preco = st.number_input("Valor (R$)", min_value=0.0, key="input_preco")
    with col_add3:
        novo_qtd = st.number_input("Qtd", min_value=1, key="input_qtd")
    with col_add4:
        st.write(" ")
        st.write(" ")
        if st.button("➕ Adicionar"):
            if novo_mat:
                nova_linha = pd.DataFrame([{"Selecionar": False, "Material": novo_mat, "Preço": novo_preco, "Qtd": novo_qtd}])
                st.session_state.df_insumos = pd.concat([st.session_state.df_insumos, nova_linha], ignore_index=True)
                st.rerun()

st.session_state.df_insumos = st.data_editor(
    st.session_state.df_insumos,
    column_config={
        "Selecionar": st.column_config.CheckboxColumn("Excluir?", default=False),
        "Material": st.column_config.TextColumn("Descrição"),
        "Preço": st.column_config.NumberColumn("Valor Unit.", format="R$ %.2f"),
    },
    num_rows="fixed", use_container_width=True, key="editor_insumos"
)

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("❌ Deletar"):
        st.session_state.df_insumos = st.session_state.df_insumos[st.session_state.df_insumos["Selecionar"] == False]
        st.rerun()
with col_btn2:
    if st.button("🗑️ Limpar Tudo"):
        st.session_state.df_insumos = pd.DataFrame(columns=["Selecionar", "Material", "Preço", "Qtd"])
        st.rerun()

# --- CÁLCULOS TÉCNICOS ---
fator = consumo_valor / 1000 if unidade in ["g", "ml"] else consumo_valor
tempo_total_h = horas + (minutos / 60)

custo_mat_base = fator * preco_material
custo_energia = (pot_media * tempo_total_h / 1000) * custo_kwh
custo_depreciacao = tempo_total_h * depreciacao_hora
custo_mao_de_obra = (tempo_pos / 60) * valor_sua_hora

df_calc = st.session_state.df_insumos.copy().fillna(0)
total_extras = (pd.to_numeric(df_calc["Preço"]) * pd.to_numeric(df_calc["Qtd"])).sum()

custo_producao_base = (custo_mat_base + custo_energia + custo_depreciacao + custo_mao_de_obra + total_extras + valor_modelagem)
custo_final_com_falha = custo_producao_base * (1 + (taxa_falha / 100))

st.markdown("---")
markup = st.slider("Margem de Lucro Desejada (%)", 0, 500, 100) 
preco_venda = custo_final_com_falha * (1 + (markup / 100))

# --- RESULTADOS ---
res1, res2, res3 = st.columns(3)
res1.metric("Custo de Produção", f"R$ {custo_final_com_falha:.2f}")
res2.metric("Preço de Venda Sugerido", f"R$ {preco_venda:.2f}")
res3.metric("Lucro Líquido", f"R$ {(preco_venda - custo_final_com_falha):.2f}")

if st.button("Gerar Resumo WhatsApp"):
    resumo = f"*Orçamento Calibrando Flow 3D*\n\n*Projeto:* {nome_peca}\n*Técnica:* {tecnologia}\n*Valor:* R$ {preco_venda:.2f}"
    st.code(resumo)
