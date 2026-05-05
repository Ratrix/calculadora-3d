import streamlit as st

st.set_page_config(page_title="Calculadora 3D - Calibrando Flow", page_icon="⚖️")

st.title("⚖️ Calculadora 3D Pro")
st.markdown("---")

# --- Barra Lateral: Configurações de Engenharia ---
st.sidebar.header("⚙️ Custos Fixos")
custo_kwh = st.sidebar.number_input("Energia (R$/kWh)", value=0.98)
valor_sua_hora = st.sidebar.number_input("Valor da sua Hora (R$)", value=30.0)
taxa_falha = st.sidebar.slider("Taxa de Risco/Falha (%)", 0, 30, 10)

# --- Seleção de Tecnologia ---
st.sidebar.header("📠 Tecnologia")
tecnologia = st.sidebar.selectbox("Selecionar Tipo", ["FDM (FILAMENTO)", "Resina"])

# Ajuste automático de custos ocultos com base na tecnologia
if tecnologia == "FDM (FILAMENTO)":
    v_maquina, v_util, pot_media = 2500.0, 5000, 200
else:
    v_maquina, v_util, pot_media = 3500.0, 3000, 60

# --- Dados da Impressão ---
col1, col2 = st.columns(2)
with col1:
    nome_peca = st.text_input("Nome do Projeto", value="Head_teste")
    preco_material = st.number_input("Preço do Material (R$/kg ou L)", value=160.0)
    peso_vol = st.number_input("Consumo (g ou ml)", value=151.0)

with col2:
    st.write("Tempo de Máquina")
    h_col, m_col = st.columns(2)
    horas = h_col.number_input("H", min_value=0, value=12)
    minutos = m_col.number_input("M", min_value=0, max_value=59, value=10)
    tempo_pos = st.number_input("Tempo Humano (Setup/Pós) em min", value=20)

# --- Cálculos de Engenharia ---
tempo_total_h = horas + (minutos / 60)
custo_energia = (pot_media * tempo_total_h / 1000) * custo_kwh
custo_mat = (peso_vol / 1000) * preco_material
depreciacao = (v_maquina / v_util) * tempo_total_h
mao_de_obra = (tempo_pos / 60) * valor_sua_hora

# Custo Base Total com Taxa de Risco
custo_producao = (custo_mat + custo_energia + depreciacao + mao_de_obra) * (1 + (taxa_falha / 100))

# Margem de Lucro
st.markdown("---")
markup = st.slider("Margem de Lucro Desejada (%)", 0, 500, 300) 
preco_venda = custo_producao * (1 + (markup / 100))

# --- Resultados ---
res1, res2, res3 = st.columns(3)
res1.metric("Custo de Produção", f"R$ {custo_producao:.2f}")
res2.metric("Preço Sugerido", f"R$ {preco_venda:.2f}")
res3.metric("Lucro Líquido", f"R$ {(preco_venda - custo_producao):.2f}")

if st.button("Gerar Orçamento WhatsApp"):
    texto = f"*Orçamento Calibrando Flow 3D*\n\n*Projeto:* {nome_peca}\n*Tecnologia:* {tecnologia}\n*Valor:* R$ {preco_venda:.2f}\n*Prazo estimado:* {horas}h {minutos}m"
    st.code(texto)
