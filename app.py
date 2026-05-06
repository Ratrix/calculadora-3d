import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora 3D - Calibrando Flow", page_icon="⚖️", layout="wide")

st.title("⚖️ Calculadora 3D Pro")
st.markdown("---")

# --- MEMÓRIA DOS DADOS ---
if 'df_insumos' not in st.session_state:
    # Adicionamos uma coluna 'Selecionar' para o controle de exclusão
    st.session_state.df_insumos = pd.DataFrame(columns=["Selecionar", "Material", "Preço", "Qtd"])

# --- BARRA LATERAL ---
st.sidebar.header("⚙️ Custos Fixos")
custo_kwh = st.sidebar.number_input("Energia (R$/kWh)", value=0.98)
valor_sua_hora = st.sidebar.number_input("Sua Hora Técnica (R$)", value=30.0)
taxa_falha = st.sidebar.slider("Taxa de Risco/Falha (%)", 0, 30, 10)

st.sidebar.header("📠 Tecnologia")
tecnologia = st.sidebar.selectbox("Tipo de Impressão", ["FDM (FILAMENTO)", "Resina"])

if tecnologia == "FDM (FILAMENTO)":
    v_maquina, v_util, pot_media = 2500.0, 5000, 200
else:
    v_maquina, v_util, pot_media = 3500.0, 3000, 60

# --- DADOS PRINCIPAIS ---
col_p1, col_p2 = st.columns(2)
with col_p1:
    nome_peca = st.text_input("Nome do Projeto", value="Cabeça")
    preco_material = st.number_input("Preço do Material Base (R$)", value=160.0)
    
    st.write("Consumo da Peça")
    c_col1, c_col2 = st.columns([2, 1])
    consumo_valor = c_col1.number_input("Quantidade", min_value=0.0, step=0.1, key="cons_val")
    unidade = c_col2.selectbox("Unidade", ["g", "kg", "ml", "L"], key="cons_uni")

with col_p2:
    st.write("Tempo de Máquina")
    h_col, m_col = st.columns(2)
    horas = h_col.number_input("Horas", min_value=0, value=15)
    minutos = m_col.number_input("Minutos", min_value=0, max_value=59, value=12)
    tempo_pos = st.number_input("Seu Tempo de Trabalho (minutos)", value=20)

st.markdown("---")

# --- SEÇÃO DE INSUMOS ---
st.subheader("📦 Insumos e Materiais Extras")

# 1. Campos de Adição
with st.container():
    col_add1, col_add2, col_add3, col_add4 = st.columns([3, 1, 1, 1])
    with col_add1:
        novo_mat = st.text_input("Descrição do Material", placeholder="Ex: Lixa, Álcool...", key="input_mat")
    with col_add2:
        novo_preco = st.number_input("Valor Unit. (R$)", min_value=0.0, step=0.5, key="input_preco")
    with col_add3:
        novo_qtd = st.number_input("Qtd", min_value=1, step=1, key="input_qtd")
    with col_add4:
        st.write(" ") 
        st.write(" ")
        if st.button("➕ Adicionar"):
            if novo_mat:
                nova_linha = pd.DataFrame([{"Selecionar": False, "Material": novo_mat, "Preço": novo_preco, "Qtd": novo_qtd}])
                st.session_state.df_insumos = pd.concat([st.session_state.df_insumos, nova_linha], ignore_index=True)
                st.rerun()

# 2. Tabela de Visualização e Edição
st.write("💡 **Para Editar:** Clique na célula. | **Para Excluir:** Marque a caixa 'Selecionar' e clique no botão de excluir abaixo.")

st.session_state.df_insumos = st.data_editor(
    st.session_state.df_insumos,
    column_config={
        "Selecionar": st.column_config.CheckboxColumn("Excluir?", default=False),
        "Material": st.column_config.TextColumn("Descrição", width="large"),
        "Preço": st.column_config.NumberColumn("Valor Unit. (R$)", format="R$ %.2f"),
        "Qtd": st.column_config.NumberColumn("Qtd"),
    },
    num_rows="fixed", 
    use_container_width=True,
    key="editor_insumos"
)

# 3. BOTÕES DE EXCLUSÃO
col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("❌ Deletar Selecionados"):
        # Filtra a tabela mantendo apenas quem NÃO está selecionado
        st.session_state.df_insumos = st.session_state.df_insumos[st.session_state.df_insumos["Selecionar"] == False]
        st.rerun()
with col_btn2:
    if st.button("🗑️ Limpar Toda a Lista"):
        st.session_state.df_insumos = pd.DataFrame(columns=["Selecionar", "Material", "Preço", "Qtd"])
        st.rerun()

# --- CÁLCULOS FINAIS ---
fator = consumo_valor / 1000 if unidade in ["g", "ml"] else consumo_valor
tempo_total_h = horas + (minutos / 60)
custo_energia = (pot_media * tempo_total_h / 1000) * custo_kwh
custo_mat_base = fator * preco_material
depreciacao = (v_maquina / v_util) * tempo_total_h
mao_de_obra = (tempo_pos / 60) * valor_sua_hora

df_calc = st.session_state.df_insumos.copy().fillna(0)
total_extras = (pd.to_numeric(df_calc["Preço"]) * pd.to_numeric(df_calc["Qtd"])).sum()

custo_producao = (custo_mat_base + custo_energia + depreciacao + mao_de_obra + total_extras) * (1 + (taxa_falha / 100))

st.markdown("---")
markup = st.slider("Margem de Lucro Desejada (%)", 0, 500, 100) 
preco_venda = custo_producao * (1 + (markup / 100))

# --- RESULTADOS ---
res1, res2, res3 = st.columns(3)
res1.metric("Custo de Produção", f"R$ {custo_producao:.2f}")
res2.metric("Preço de Venda", f"R$ {preco_venda:.2f}")
res3.metric("Lucro Líquido", f"R$ {(preco_venda - custo_producao):.2f}")

if st.button("Gerar Resumo WhatsApp"):
    resumo = f"*Orçamento Calibrando Flow 3D*\n\n*Projeto:* {nome_peca}\n*Valor:* R$ {preco_venda:.2f}"
    st.code(resumo)
