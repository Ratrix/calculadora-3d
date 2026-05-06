import streamlit as st
import pandas as pd

# Configuração da página para aproveitar o espaço lateral
st.set_page_config(page_title="Calculadora 3D - Calibrando Flow", page_icon="⚖️", layout="wide")

st.title("⚖️ Calculadora 3D Pro")
st.markdown("---")

# --- LÓGICA DE MEMÓRIA (Impede os dados de sumirem ao dar Enter) ---
if 'df_insumos' not in st.session_state:
    # Criamos a tabela inicial vazia
    st.session_state.df_insumos = pd.DataFrame(columns=["Material", "Preço", "Qtd"])

# --- Barra Lateral: Configurações de Engenharia ---
st.sidebar.header("⚙️ Custos Fixos")
custo_kwh = st.sidebar.number_input("Energia (R$/kWh)", value=0.98)
valor_sua_hora = st.sidebar.number_input("Sua Hora Técnica (R$)", value=30.0)
taxa_falha = st.sidebar.slider("Taxa de Risco/Falha (%)", 0, 30, 10)

st.sidebar.header("📠 Tecnologia")
tecnologia = st.sidebar.selectbox("Tipo de Impressão", ["FDM (FILAMENTO)", "Resina"])

# Parâmetros técnicos das suas máquinas (Bambu Lab / Elegoo)
if tecnologia == "FDM (FILAMENTO)":
    v_maquina, v_util, pot_media = 2500.0, 5000, 200
else:
    v_maquina, v_util, pot_media = 3500.0, 3000, 60

# --- Seção 1: Dados Principais ---
col1, col2 = st.columns(2)
with col1:
    nome_peca = st.text_input("Nome do Projeto", value="Cabeça")
    preco_material = st.number_input("Preço do Material Base (R$)", value=160.0)
    
    st.write("Consumo da Peça")
    c_col1, c_col2 = st.columns([2, 1])
    consumo_valor = c_col1.number_input("Quantidade", min_value=0.0, value=0.0, step=0.1, label_visibility="collapsed")
    unidade = c_col2.selectbox("Unidade", ["g", "kg", "ml", "L"], label_visibility="collapsed")

with col2:
    st.write("Tempo de Máquina")
    h_col, m_col = st.columns(2)
    horas = h_col.number_input("Horas", min_value=0, value=15)
    minutos = m_col.number_input("Minutos", min_value=0, max_value=59, value=12)
    tempo_pos = st.number_input("Seu Tempo de Trabalho (minutos)", value=20)

st.markdown("---")

# --- Seção 2: Insumos Extras (Tabela Corrigida) ---
st.subheader("📦 Insumos e Materiais Extras")
st.write("💡 **Edição:** Clique em qualquer campo para alterar (✎).")
st.write("💡 **Exclusão:** Marque a linha à esquerda e aperte 'Delete' no teclado ou use a lixeira no topo direito da tabela.")

# O 'data_editor' atualiza o session_state automaticamente para não perder dados
st.session_state.df_insumos = st.data_editor(
    st.session_state.df_insumos,
    column_config={
        "Material": st.column_config.TextColumn("Descrição (✎)", width="large", required=True),
        "Preço": st.column_config.NumberColumn("Valor (R$)", min_value=0, format="R$ %.2f"),
        "Qtd": st.column_config.NumberColumn("Qtd", min_value=1, step=1),
    },
    num_rows="dynamic", # Permite adicionar e deletar linhas
    use_container_width=True,
    key="editor_principal"
)

if st.button("🗑️ Limpar Toda a Lista"):
    st.session_state.df_insumos = pd.DataFrame(columns=["Material", "Preço", "Qtd"])
    st.rerun()

# --- Cálculos Finais ---
# Conversão de unidades
fator = consumo_valor / 1000 if unidade in ["g", "ml"] else consumo_valor

# Custos Base
tempo_total_h = horas + (minutos / 60)
custo_energia = (pot_media * tempo_total_h / 1000) * custo_kwh
custo_mat_base = fator * preco_material
depreciacao = (v_maquina / v_util) * tempo_total_h
mao_de_obra = (tempo_pos / 60) * valor_sua_hora

# Soma dos Extras da Tabela
df_calc = st.session_state.df_insumos.copy().fillna(0)
total_extras = (pd.to_numeric(df_calc["Preço"]) * pd.to_numeric(df_calc["Qtd"])).sum()

# Total com margem de segurança
custo_producao = (custo_mat_base + custo_energia + depreciacao + mao_de_obra + total_extras) * (1 + (taxa_falha / 100))

st.markdown("---")
markup = st.slider("Margem de Lucro Desejada (%)", 0, 500, 100) 
preco_venda = custo_producao * (1 + (markup / 100))

# --- Exibição de Resultados ---
res1, res2, res3 = st.columns(3)
res1.metric("Custo de Produção", f"R$ {custo_producao:.2f}")
res2.metric("Preço de Venda", f"R$ {preco_venda:.2f}")
res3.metric("Lucro Líquido", f"R$ {(preco_venda - custo_producao):.2f}")

if st.button("Gerar Resumo para WhatsApp"):
    resumo = f"*Orçamento Calibrando Flow 3D*\n\n*Projeto:* {nome_peca}\n*Valor:* R$ {preco_venda:.2f}"
    st.code(resumo)
