import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

# Carregar cadastro de médicos
CAMINHO_MEDICOS = "Cadastro_Medicos.xlsx"
if os.path.exists(CAMINHO_MEDICOS):
    df_medicos = pd.read_excel(CAMINHO_MEDICOS)
    lista_medicos = sorted(df_medicos["Nome do Médico"].dropna().unique().tolist())
else:
    lista_medicos = []

# Dados simulados para estrutura de leitos por andar/unidade
estrutura_leitos = {
    "Unidade I": {
        "4º andar": list(range(401, 433)),
        "5º andar": list(range(501, 536)),
        "6º andar": list(range(601, 638)),
    },
    "Unidade III": {
        "4º andar": list(range(401, 405)),
        "5º andar (Pediatria)": list(range(501, 511)),
        "6º andar (Pediatria)": list(range(601, 611)),
        "7º andar": list(range(701, 711)),
        "8º andar (Obstetrícia)": list(range(801, 811)),
        "9º andar (Obstetrícia)": list(range(901, 911)),
    },
    "Unidade IV": {
        "6º andar (TMO)": list(range(601, 627)),
        "7º andar (Cardiologia)": list(range(701, 729)),
        "8º andar": list(range(801, 829)),
        "9º andar": list(range(901, 929)),
    }
}

st.set_page_config(layout="wide")

if "dados_pacientes" not in st.session_state:
    st.session_state.dados_pacientes = {}

if "historico_movimentos" not in st.session_state:
    st.session_state.historico_movimentos = []

if "transicao" not in st.session_state:
    st.session_state.transicao = []

if "nome_em_transicao" not in st.session_state:
    st.session_state.nome_em_transicao = None

st.sidebar.title("🔧 Navegação")
opcao = st.sidebar.radio("Escolha a visualização:", ["Painel de Leitos", "Visão do Plantonista", "Listas do Dia", "Painel de Indicadores", "Cadastro de Médico"])

# Nova aba: Cadastro de Médico
if opcao == "Cadastro de Médico":
    st.title("🩺 Cadastro de Médico")
    novo_medico = st.text_input("Nome completo do novo médico")
    if st.button("Adicionar ao Cadastro"):
        if novo_medico.strip() != "":
            novo_registro = pd.DataFrame([[novo_medico]], columns=["Nome do Médico"])
            if os.path.exists(CAMINHO_MEDICOS):
                df_existente = pd.read_excel(CAMINHO_MEDICOS)
                df_atualizado = pd.concat([df_existente, novo_registro]).drop_duplicates().sort_values("Nome do Médico")
            else:
                df_atualizado = novo_registro
            df_atualizado.to_excel(CAMINHO_MEDICOS, index=False)
            st.success("Médico adicionado com sucesso!")
        else:
            st.warning("Por favor, insira um nome válido.")

# Substituição do campo de médico no Painel de Leitos
if opcao == "Painel de Leitos":
    st.title("📋 Painel de Leitos por Unidade e Andar")

    def exibir_leitos(unidade, andar, leitos):
        st.markdown(f"### {unidade} – {andar}")
        cols = st.columns(6)
        for i, leito in enumerate(leitos):
            with cols[i % 6]:
                chave = f"{unidade}_{andar}_{leito}"
                paciente = st.session_state.dados_pacientes.get(chave, {})
                nome_display = paciente.get("nome", "[Vazio]")
                st.markdown(f"**Leito {leito}**")
                if st.button(f"✏️ {nome_display}", key=f"btn_{chave}"):
                    with st.modal(f"Editar Leito {leito} - {unidade} - {andar}"):
                        if st.session_state.nome_em_transicao:
                            nome = st.text_input("Nome do paciente", value=st.session_state.nome_em_transicao.get("nome", ""))
                            origem = st.session_state.nome_em_transicao.get("origem", "")
                            obs_trans = st.session_state.nome_em_transicao.get("observacoes", "")
                            st.markdown(f"🔄 Dados importados da transição: Origem: **{origem}** | Obs: {obs_trans}")
                        else:
                            nome = st.text_input("Nome do paciente", value=paciente.get("nome", ""))

                        medico = st.selectbox("Médico responsável", options=lista_medicos) if lista_medicos else st.text_input("Médico responsável")

                        if st.button("Salvar cadastro inicial", key=f"salvar_{chave}"):
                            st.session_state.dados_pacientes[chave] = {
                                "nome": nome,
                                "medico": medico,
                                "registrado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                "leito": leito,
                            }
                            st.session_state.nome_em_transicao = None
                            st.success("Dados salvos com sucesso!")

                        if nome and medico:
                            st.markdown("---")
                            st.subheader("📌 Ficha Clínica Assistencial")
                            # ... restante da ficha omitido para foco

    # ✅ CHAMADA ESSENCIAL PARA EXIBIR OS LEITOS
    for unidade, andares in estrutura_leitos.items():
        for andar, leitos in andares.items():
            exibir_leitos(unidade, andar, leitos)
