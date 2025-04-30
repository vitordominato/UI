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

if "leito_em_edicao" not in st.session_state:
    st.session_state.leito_em_edicao = None

st.sidebar.title("🔧 Navegação")
opcao = st.sidebar.radio("Escolha a visualização:", ["Painel de Leitos", "Visão do Plantonista", "Listas do Dia", "Painel de Indicadores", "Cadastro de Médico"])

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

if opcao == "Painel de Leitos":
    st.title("📋 Painel de Leitos por Unidade e Andar")

    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        unidade_selecionada = st.selectbox("Unidade", list(estrutura_leitos.keys()))
    with col_f2:
        andar_selecionado = st.selectbox("Andar", list(estrutura_leitos[unidade_selecionada].keys()))

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
                    st.session_state.leito_em_edicao = chave
                if st.session_state.leito_em_edicao == chave:
                    with st.expander(f"Editar Leito {leito} - {unidade} - {andar}", expanded=True):
                        if st.session_state.nome_em_transicao:
                            nome = st.text_input("Nome do paciente", value=st.session_state.nome_em_transicao.get("nome", ""), key=f"nome_{chave}")
                            origem = st.session_state.nome_em_transicao.get("origem", "")
                            obs_trans = st.session_state.nome_em_transicao.get("observacoes", "")
                            st.markdown(f"🔄 Dados importados da transição: Origem: **{origem}** | Obs: {obs_trans}")
                        else:
                            nome = st.text_input("Nome do paciente", value=paciente.get("nome", ""), key=f"nome_{chave}")

                        medico = st.selectbox("Médico responsável", options=lista_medicos, index=lista_medicos.index(paciente.get("medico")) if paciente.get("medico") in lista_medicos else 0, key=f"medico_{chave}") if lista_medicos else st.text_input("Médico responsável", key=f"medico_{chave}")

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
                            risco = st.selectbox("Risco assistencial", ["Baixo", "Moderado", "Alto"], key=f"risco_{chave}")
                            operadora = st.text_input("Operadora", key=f"operadora_{chave}")
                            pendencia = st.text_area("Pendência da rotina", key=f"pendencia_{chave}")
                            paliativo = st.radio("Cuidados paliativos?", ["Sim", "Não"], horizontal=True, key=f"paliativo_{chave}")
                            cirurgia = st.radio("Cirurgia programada?", ["Sim", "Não"], horizontal=True, key=f"cirurgia_{chave}")
                            desospitalizacao = st.radio("Em desospitalização?", ["Sim", "Não"], horizontal=True, key=f"desospitalizacao_{chave}")
                            alta_amanha = st.radio("Alta prevista para amanhã?", ["Sim", "Não"], horizontal=True, key=f"alta_{chave}")
                            intercorrencia = st.selectbox("Intercorrência", ["Nenhuma", "Verde", "Amarela", "Laranja", "Azul", "Outro"], key=f"intercorrencia_{chave}")
                            desc_intercorrencia = st.text_area("Descrição da intercorrência", key=f"desc_inter_{chave}")
                            reavaliacao = st.radio("Reavaliação necessária?", ["Sim", "Não"], horizontal=True, key=f"reavaliacao_{chave}")
                            observacoes = st.text_area("Observações gerais", key=f"obs_{chave}")

                            if st.button("Salvar ficha clínica", key=f"salvar_ficha_{chave}"):
                                st.session_state.dados_pacientes[chave].update({
                                    "risco": risco,
                                    "operadora": operadora,
                                    "pendencia": pendencia,
                                    "paliativo": paliativo,
                                    "cirurgia": cirurgia,
                                    "desospitalizacao": desospitalizacao,
                                    "alta_amanha": alta_amanha,
                                    "intercorrencia": intercorrencia,
                                    "desc_intercorrencia": desc_intercorrencia,
                                    "reavaliacao": reavaliacao,
                                    "observacoes": observacoes,
                                })
                                st.success("Ficha clínica salva com sucesso!")

                            st.markdown("---")
                            st.subheader("📤 Ações de Saída")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                if st.button("Alta", key=f"alta_{chave}"):
                                    st.session_state.historico_movimentos.append({"tipo": "Alta", "dados": st.session_state.dados_pacientes[chave], "leito": chave, "data": datetime.now().strftime("%d/%m/%Y %H:%M")})
                                    st.session_state.dados_pacientes.pop(chave, None)
                                    st.session_state.leito_em_edicao = None
                                    st.success("Paciente transferido para painel de indicadores (Alta)")
                            with col2:
                                if st.button("Transferência", key=f"transferencia_{chave}"):
                                    st.session_state.historico_movimentos.append({"tipo": "Transferência", "dados": st.session_state.dados_pacientes[chave], "leito": chave, "data": datetime.now().strftime("%d/%m/%Y %H:%M")})
                                    st.session_state.dados_pacientes.pop(chave, None)
                                    st.session_state.leito_em_edicao = None
                                    st.success("Paciente transferido para painel de indicadores (Transferência)")
                            with col3:
                                if st.button("Óbito", key=f"obito_{chave}"):
                                    st.session_state.historico_movimentos.append({"tipo": "Óbito", "dados": st.session_state.dados_pacientes[chave], "leito": chave, "data": datetime.now().strftime("%d/%m/%Y %H:%M")})
                                    st.session_state.dados_pacientes.pop(chave, None)
                                    st.session_state.leito_em_edicao = None
                                    st.success("Paciente transferido para painel de indicadores (Óbito)")

    leitos_exibir = estrutura_leitos[unidade_selecionada][andar_selecionado]
    exibir_leitos(unidade_selecionada, andar_selecionado, leitos_exibir)
