import streamlit as st

# Configuração da página profissional
st.set_page_config(page_title="Calibrando Flow 3D - Calculadora Pro", page_icon="⚖️")

st.title("⚖️ Calculadora de Custos 3D Pro")
st.markdown("---")

# --- Barra Lateral (Configurações Gerais) ---
st.sidebar.header("⚙️ Configurações Base")
custo_kwh = st.sidebar.number_input("Custo da Energia (R$/kWh)", value=0.84)
taxa_falha = st.sidebar.slider("Taxa de Falha Estimada (%)", 0, 30, 10)
markup_base = st.sidebar.slider("Margem de Lucro Desejada (%)", 0, 1000, 100, step=10)

# --- Entrada de Dados da Peça ---
col1, col2 = st.columns(2)

with col1:
    nome_peca = st.text_input("Nome da Peça", placeholder="Ex: Action Figure")
    tecnologia = st.selectbox("Tecnologia", ["Filamento (FDM)", "Resina (SLA)"])
    preco_material = st.number_input("Preço do Material (R$)", value=95.0)

with col2:
    st.write("Tempo de Impressão")
    h_col, m_col = st.columns(2)
    horas = h_col.number_input("Horas", min_value=0, value=1)
    minutos = m_col.number_input("Minutos", min_value=0, max_value=59, value=0)
    peso_vol = st.number_input("Peso/Volume (g ou ml)", value=50.0)

# --- Depreciação e Invisíveis ---
with st.expander("🛠️ Custos Ocultos e Depreciação"):
    valor_maquina = st.number_input("Valor da Máquina (R$)", value=2500.0)
    vida_util = st.number_input("Vida Útil (Horas)", value=5000)
    # Custos de insumo baseados na tecnologia
    insumo_default = 2.0 if tecnologia == "Filamento (FDM)" else 7.0
    insumos_fixos = st.number_input("Insumos extras (Luvas/IPA/Bicos)", value=insumo_default)

# --- Lógica de Cálculo ---
tempo_total_h = horas + (minutos / 60)
potencia = 350 if tecnologia == "Filamento (FDM)" else 60
custo_energia = (potencia * tempo_total_h / 1000) * custo_kwh
custo_mat = (peso_vol / 1000) * preco_material
depreciacao = (valor_maquina / vida_util) * tempo_total_h

custo_base = custo_mat + custo_energia + depreciacao + insumos_fixos
custo_total_real = custo_base * (1 + (taxa_falha / 100))
valor_lucro = custo_total_real * (markup_base / 100)
preco_venda = custo_total_real + valor_lucro

# --- Resultados ---
st.markdown("---")
res1, res2, res3 = st.columns(3)
res1.metric("Custo Produção", f"R$ {custo_total_real:.2f}")
res2.metric("Preço de Venda", f"R$ {preco_venda:.2f}")
res3.metric("Lucro Líquido", f"R$ {valor_lucro:.2f}")

if st.button("Gerar Resumo para WhatsApp"):
    texto = f"*Orçamento Calibrando Flow 3D*\n*Peça:* {nome_peca}\n*Valor:* R$ {preco_venda:.2f}"
    st.code(texto)
