# =================================================================
# PROJETO: CALCULADORA 3D PRO  - Calibrando Flow 3D
# DESENVOLVIDO POR: Joseanderson Langner
# FORMAÇÃO: Engenharia de Controle e Automação
# DATA DE DESENVOLVIMENTO: Maio de 2026
# DESCRIÇÃO: Ferramenta de gestão e orçamentação para impressão 3D
# =================================================================

import streamlit as st
import pandas as pd

# Configuração da página para layout expandido estilo Dashboard
st.set_page_config(page_title="Calculadora 3D Pro", page_icon="⚖️", layout="wide")

# --- LÓGICA DE MEMÓRIA (Session State) ---
if 'df_insumos' not in st.session_state:
    st.session_state.df_insumos = pd.DataFrame(columns=["Selecionar", "Material", "Preço", "Qtd"])

if 'df_pecas' not in st.session_state:
    st.session_state.df_pecas = pd.DataFrame(columns=["Selecionar", "Item", "Nome da Parte", "Peso (g)", "Horas", "Minutos"])

# --- DICIONÁRIO DE TARIFAS (kWh por Estado) ---
tarifas_estados = {
    "Personalizado": 0.00, "Acre (AC)": 0.92, "Alagoas (AL)": 0.88, "Amapá (AP)": 0.85, 
    "Amazonas (AM)": 0.90, "Bahia (BA)": 0.91, "Ceará (CE)": 0.87, "Distrito Federal (DF)": 0.82,
    "Espírito Santo (ES)": 0.84, "Goiás (GO)": 0.86, "Maranhão (MA)": 0.89, "Mato Grosso (MT)": 0.93, 
    "Mato Grosso do Sul (MS)": 0.92, "Minas Gerais (MG)": 0.95, "Pará (PA)": 1.05, "Paraíba (PB)": 0.86, 
    "Paraná (PR)": 0.84, "Pernambuco (PE)": 0.87, "Piauí (PI)": 0.90, "Rio de Janeiro (RJ)": 1.02,
    "Rio Grande do Norte (RN)": 0.88, "Rio Grande do Sul (RS)": 0.86, "Rondônia (RO)": 0.91, 
    "Roraima (RR)": 0.85, "Santa Catarina (SC)": 0.81, "São Paulo (SP)": 0.94, "Sergipe (SE)": 0.88, 
    "Tocantins (TO)": 0.91
}

# --- BARRA LATERAL (Configurações de Engenharia e Máquina) ---
st.sidebar.header("⚙️ Configurações do Sistema")
nome_loja = st.sidebar.text_input("Nome da sua Marca", value="Calibrando Flow 3D")

st.sidebar.subheader("🔌 Parâmetros de Energia")
estado_sel = st.sidebar.selectbox("Selecione seu Estado para kWh", list(tarifas_estados.keys()), index=25)
valor_sugerido = tarifas_estados[estado_sel]
custo_kwh = st.sidebar.number_input("Energia (R$/kWh)", value=valor_sugerido if valor_sugerido > 0 else 0.98, step=0.01)
potencia_maquina = st.sidebar.number_input("Potência Média da Impressora (W)", value=200, step=10)

st.sidebar.subheader("💰 Planejamento de Depreciação")
valor_maquina = st.sidebar.number_input("Valor da Máquina (R$)", value=2500.0)
meses_depreciacao = st.sidebar.number_input("Vida útil estimada (meses)", value=36, min_value=1)
uso_mensal_horas = st.sidebar.number_input("Horas de uso por mês", value=160, min_value=1)
depreciacao_hora = (valor_maquina / meses_depreciacao) / uso_mensal_horas
st.sidebar.write(f"📊 **Depreciação:** R$ {depreciacao_hora:.2f}/hora")

# --- CORPO PRINCIPAL (Layout em Colunas do Dashboard) ---
st.title(f"📊 Painel de Custos 3D — {nome_loja}")
st.markdown("---")

# Dividindo a tela em Duas Colunas: Esquerda para Inputs, Direita para Resultados (Estilo a imagem de referência)
col_dados_esquerda, col_resultados_direita = st.columns([2, 1])

with col_dados_esquerda:
    # Card 1: Dados do Projeto Geral
    with st.container(border=True):
        st.subheader("📝 Dados Básicos do Projeto")
        c1, c2, c3 = st.columns(3)
        nome_projeto = c1.text_input("Nome do Projeto", value="Colecionável Completo")
        preco_material = c2.number_input("Preço do Material Base (R$/kg ou L)", value=160.0)
        valor_modelagem = c3.number_input("Modelagem/Trabalho 3D (R$)", value=0.0)
        
        c4, c5 = st.columns(2)
        valor_sua_hora = c4.number_input("Sua Hora Técnica (R$)", value=30.0)
        tempo_pos = c5.number_input("Tempo de Setup e Pós-Processo (minutos)", value=20)

    # Card 2: Partes Fatiadas do Projeto (A sua lógica de fatiamento)
    with st.container(border=True):
        st.subheader("🧩 Fatiamento de Peças do Projeto")
        st.write("Insira os dados gerados pelo seu fatiador:")
        
        col_padd1, col_padd2, col_padd3, col_padd4 = st.columns([3, 2, 1, 1])
        nova_parte_nome = col_padd1.text_input("Nome da Parte (Ex: Cabeça, Torso)", key="input_parte_nome")
        nova_parte_peso = col_padd2.number_input("Peso da Peça (g)", min_value=0.0, step=0.1, key="input_parte_peso")
        nova_parte_horas = col_padd3.number_input("Horas", min_value=0, step=1, key="input_parte_horas")
        nova_parte_min = col_padd4.number_input("Min", min_value=0, max_value=59, step=1, key="input_parte_min")
        
        if st.button("➕ Adicionar Parte ao Projeto", use_container_width=True):
            if nova_parte_nome and (nova_parte_peso > 0 or nova_parte_horas > 0 or nova_parte_min > 0):
                proximo_item = len(st.session_state.df_pecas) + 1
                nova_linha_peca = pd.DataFrame([{
                    "Selecionar": False, "Item": f"Peça {proximo_item}", "Nome da Parte": nova_parte_nome, 
                    "Peso (g)": nova_parte_peso, "Horas": nova_parte_horas, "Minutos": nova_parte_min
                }])
                st.session_state.df_pecas = pd.concat([st.session_state.df_pecas, nova_linha_peca], ignore_index=True)
                st.rerun()

        # Tabela sem índice (Início no 1 humano)
        st.session_state.df_pecas = st.data_editor(
            st.session_state.df_pecas,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn("Excluir?"),
                "Item": st.column_config.TextColumn("Nº", disabled=True),
                "Nome da Parte": st.column_config.TextColumn("Parte do Projeto"),
                "Peso (g)": st.column_config.NumberColumn("Peso"),
            },
            num_rows="fixed", hide_index=True, use_container_width=True, key="editor_pecas"
        )
        
        if st.button("❌ Remover Peças Selecionadas"):
            st.session_state.df_pecas = st.session_state.df_pecas[st.session_state.df_pecas["Selecionar"] == False]
            st.session_state.df_pecas["Item"] = [f"Peça {i+1}" for i in range(len(st.session_state.df_pecas))]
            st.rerun()

    # Card 3: Insumos Extras
    with st.container(border=True):
        st.subheader("📦 Insumos e Materiais Extras")
        col_add1, col_add2, col_add3 = st.columns([3, 1, 1])
        novo_mat = col_add1.text_input("Descrição (Lixa, Primer, Caixa...)", key="input_mat")
        novo_preco = col_add2.number_input("Valor Unitário (R$)", min_value=0.0, key="input_preco")
        novo_qtd = col_add3.number_input("Qtd", min_value=1, value=1, key="input_qtd")
        
        if st.button("➕ Adicionar Insumo Extra", use_container_width=True):
            if novo_mat:
                nova_linha = pd.DataFrame([{"Selecionar": False, "Material": novo_mat, "Preço": novo_preco, "Qtd": novo_qtd}])
                st.session_state.df_insumos = pd.concat([st.session_state.df_insumos, nova_linha], ignore_index=True)
                st.rerun()

        st.session_state.df_insumos = st.data_editor(
            st.session_state.df_insumos,
            column_config={
                "Selecionar": st.column_config.CheckboxColumn("Excluir?"),
                "Material": st.column_config.TextColumn("Descrição"),
            },
            num_rows="fixed", hide_index=True, use_container_width=True, key="editor_insumos"
        )
        if st.button("❌ Remover Insumos Selecionados"):
            st.session_state.df_insumos = st.session_state.df_insumos[st.session_state.df_insumos["Selecionar"] == False]
            st.rerun()

    # Card 4: Taxas, Plataformas e Comissões (Melhoria baseada na imagem de referência)
    with st.container(border=True):
        st.subheader("📊 Impostos e Taxas de Venda")
        t1, t2, t3, t4 = st.columns(4)
        taxa_falha = t1.slider("Risco/Falhas (%)", 0, 30, 10)
        imposto = t2.number_input("Imposto Nota Fiscal (%)", min_value=0.0, value=0.0)
        taxa_cartao = t3.number_input("Taxa de Cartão/Maquininha (%)", min_value=0.0, value=0.0)
        custo_anuncio = t4.number_input("Taxa Marketplace/Anúncio (%)", min_value=0.0, value=0.0)

# --- CÁLCULOS MATEMÁTICOS DE SOMA ---
total_peso_g = pd.to_numeric(st.session_state.df_pecas["Peso (g)"]).sum()
total_horas_pecas = pd.to_numeric(st.session_state.df_pecas["Horas"]).sum()
total_minutos_pecas = pd.to_numeric(st.session_state.df_pecas["Minutos"]).sum()
tempo_total_h = total_horas_pecas + (total_minutos_pecas / 60)

# Consolidação de custos diretos
fator_material = total_peso_g / 1000
custo_mat_base = fator_material * preco_material
custo_energia = (potencia_maquina * tempo_total_h / 1000) * custo_kwh 
custo_depreciacao = tempo_total_h * depreciacao_hora
custo_mao_de_obra = (tempo_pos / 60) * valor_sua_hora
total_extras = (pd.to_numeric(st.session_state.df_insumos["Preço"]) * pd.to_numeric(st.session_state.df_insumos["Qtd"])).sum()

# Custo Total de Produção Base antes das Taxas Mercadológicas
custo_producao_liquido = (custo_mat_base + custo_energia + custo_depreciacao + custo_mao_de_obra + total_extras + valor_modelagem)
custo_total_com_falha = custo_producao_liquido * (1 + (taxa_falha / 100))

with col_resultados_direita:
    # Card de Resultados Dinâmicos (Lado Direito da Referência)
    with st.container(border=True):
        st.subheader("💰 Resumo de Custos")
        
        # Estrutura de tabela limpa de saída de dados
        st.write(f"🔹 **Material Base:** R$ {custo_mat_base:.2f} ({total_peso_g:.1f}g)")
        st.write(f"⚡ **Energia Elétrica:** R$ {custo_energia:.2f}")
        st.write(f"📠 **Depreciação de Máquina:** R$ {custo_depreciacao:.2f}")
        st.write(f"👨‍🏭 **Mão de Obra (Pós):** R$ {custo_mao_de_obra:.2f}")
        st.write(f"📦 **Insumos Extras:** R$ {total_extras:.2f}")
        if valor_modelagem > 0:
            st.write(f"🛠️ **Modelagem 3D:** R$ {valor_modelagem:.2f}")
        st.write(f"⚠️ **Custo de Falha adicionado:** R$ {(custo_total_com_falha - custo_producao_liquido):.2f}")
        
        st.markdown("---")
        st.error(f"### CUSTO TOTAL: R$ {custo_total_com_falha:.2f}")

    # Card de Precificação Inteligente
    with st.container(border=True):
        st.subheader("🎯 Precificação do Projeto")
        margem_lucro = st.slider("Margem de Lucro Desejada (%)", 0, 90, 50)
        
        # Soma total de todas as retenções percentuais sobre o preço de venda final
        total_taxas_venda = margem_lucro + imposto + taxa_cartao + custo_anuncio
        
        if total_taxas_venda < 100:
            preco_venda = custo_total_com_falha / (1 - (total_taxas_venda / 100))
        else:
            st.warning("⚠️ Alerta: A soma das taxas e margem superou 100%. Reduza os valores para calcular.")
            preco_venda = custo_total_com_falha

        # Deduções reais do ganho
        v_imposto = preco_venda * (imposto / 100)
        v_cartao = preco_venda * (taxa_cartao / 100)
        v_anuncio = preco_venda * (custo_anuncio / 100)
        lucro_liquido_real = preco_venda - custo_total_com_falha - v_imposto - v_cartao - v_anuncio

        st.success(f"## Preço sugerido:\n# R$ {preco_venda:.2f}")
        st.metric("Lucro Líquido Real", f"R$ {lucro_liquido_real:.2f}")

        # Detalhamento de taxas retidas no preço de venda
        if (v_imposto + v_cartao + v_anuncio) > 0:
            st.write("---")
            st.write("**Descontos do Preço de Venda:**")
            if v_imposto > 0: st.write(f"💸 Imposto NF: R$ {v_imposto:.2f}")
            if v_cartao > 0: st.write(f"💳 Tarifa Cartão: R$ {v_cartao:.2f}")
            if v_anuncio > 0: st.write(f"🏛️ Taxa Anúncio: R$ {v_anuncio:.2f}")

        if st.button("Gerar Resumo WhatsApp", use_container_width=True):
            horas_f, minutos_f = divmod(int(tempo_total_h * 60), 60)
            resumo = (
                f"*Orçamento {nome_loja}*\n\n"
                f"*Projeto:* {nome_projeto}\n"
                f"*Material Total:* {total_peso_g:.1f}g\n"
                f"*Tempo de Impressão:* {horas_f}h {minutos_f}min\n"
                f"*Valor Final:* R$ {preco_venda:.2f}"
            )
            st.code(resumo)

# --- RODAPÉ DE CRÉDITOS ---
st.markdown("---")
st.caption("🚀 Desenvolvido por: Joseanderson Langner | Engenharia de Controle e Automação")
