import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora 3D - Calibrando Flow", page_icon="⚖️", layout="wide")

st.title("⚖️ Calculadora 3D Pro")
st.markdown("---")

# --- Inicialização da Lista de Insumos Extras no Estado da Sessão ---
if 'insumos_extras' not in st.session_state:
    st.session_state.insumos_extras = []

# --- Barra Lateral: Configurações de Engenharia ---
st.sidebar.header("⚙️ Custos Fixos")
custo_kwh = st.sidebar.number_input("Energia (R$/kWh)", value=0.98)
valor_sua_hora = st.sidebar.number_input("Sua Hora Técnica (R$)", value=30.0)
taxa_falha = st.sidebar.slider("Taxa de Risco/Falha (%)", 0, 30, 10)

st.sidebar.header("📠 Tecnologia")
tecnologia = st.sidebar.selectbox("Tipo de Impressão", ["FDM (FILAMENTO)", "Resina"])

# Parâmetros técnicos silenciosos por tecnologia
if tecnologia == "FDM (FILAMENTO)":
    v_maquina, v_util, pot_media = 2500.0, 5000, 200
else:
    v_maquina, v_util, pot_media = 3500.0, 3000, 60

# --- Seção 1: Dados da Impressão ---
col1, col2 = st.columns(2)
with col1:
    nome_peca = st.text_input("Nome do Projeto", value="Projeto_Exemplo")
    preco_material = st.number_input("Preço do Material Base (R$)", value=160.0)
    peso_vol = st.number_input("Consumo da Peça (g ou ml)", value=100.0)

with col2:
    st.write("Tempo de Máquina")
    h_col, m_col = st.columns(2)
    horas = h_col.number_input("Horas", min_value=0, value=1)
    minutos = m_col.number_input("Minutos", min_value=0, max_value=59, value=0)
    tempo_pos = st.number_input("Seu Tempo de Trabalho (minutos)", value=20)

st.markdown("---")

# --- Seção 2: Gerenciador de Insumos Extras (Papel, Álcool, Caixas, etc.) ---
st.subheader("📦 Insumos e Materiais Extras")
st.info("Adicione aqui tudo o que comprou para este projeto (Lixas, Álcool, Papel Toalha, Caixa de Correio, etc.)")

col_add1, col_add2, col_add3 = st.columns([3, 1, 1])
novo_item = col_add1.text_input("Descrição do Material", placeholder="Ex: Álcool Isopropílico")
valor_item = col_add2.number_input("Valor Pago (R$)", min_value=0.0, step=1.0)
qtd_item = col_add3.number_input("Quantidade", min_value=1, step=1)

if st.button("➕ Adicionar Material"):
    if novo_item:
        st.session_state.insumos_extras.append({
            "Material": novo_item,
            "Preço": valor_item,
            "Qtd": qtd_item,
            "Total": valor_item * qtd_item
        })
        st.rerun()

# Exibição e Remoção de Itens
total_insumos_extras = 0.0
if st.session_state.insumos_extras:
    df_insumos = pd.DataFrame(st.session_state.insumos_extras)
    st.table(df_insumos)
    total_insumos_extras = df_insumos["Total"].sum()
    
    if st.button("🗑️ Limpar Todos os Materiais"):
        st.session_state.insumos_extras = []
        st.rerun()

# --- Cálculos Finais de Engenharia ---
tempo_total_h = horas + (minutos / 60)
custo_energia = (pot_media * tempo_total_h / 1000) * custo_kwh
custo_mat_base = (peso_vol / 1000) * preco_material
depreciacao = (v_maquina / v_util) * tempo_total_h
mao_de_obra = (tempo_pos / 60) * valor_sua_hora

# Custo total somando os materiais extras adicionados
custo_producao = (custo_mat_base + custo_energia + depreciacao + mao_de_obra + total_insumos_extras) * (1 + (taxa_falha / 100))

st.markdown("---")
markup = st.slider("Margem de Lucro Desejada (%)", 0, 500, 100) 
preco_venda = custo_producao * (1 + (markup / 100))

# --- Resultados ---
res1, res2, res3 = st.columns(3)
res1.metric("Custo Total de Produção", f"R$ {custo_producao:.2f}")
res2.metric("Preço de Venda Final", f"R$ {preco_venda:.2f}")
res3.metric("Lucro Bruto", f"R$ {(preco_venda - custo_producao):.2f}")

if st.button("Gerar Resumo para WhatsApp"):
    resumo = f"*Orçamento Calibrando Flow 3D*\n\n*Projeto:* {nome_peca}\n*Valor:* R$ {preco_venda:.2f}"
    st.code(resumo)
