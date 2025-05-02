# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
import os

CAMINHO_LEITOS = "base_leitos.xlsx"
CAMINHO_TRANSICOES = "transicoes.xlsx"
CAMINHO_MEDICOS = "Cadastro_Medicos.xlsx"

CAMPOS_PADRAO = [
    "chave", "nome", "medico", "registrado_em", "leito", "unidade", "andar",
    "risco", "operadora", "pendencia", "paliativo", "cirurgia", "desospitalizacao",
    "alta_amanha", "intercorrencia", "desc_intercorrencia", "reavaliacao", "observacoes"
]

# Garante existência das planilhas
for path, columns in [
    (CAMINHO_LEITOS, CAMPOS_PADRAO),
    (CAMINHO_TRANSICOES, ["nome", "origem", "observacoes"]),
    (CAMINHO_MEDICOS, ["Nome do Médico"])
]:
    if not os.path.exists(path):
        pd.DataFrame(columns=columns).to_excel(path, index=False)

# Carrega as planilhas
df_leitos = pd.read_excel(CAMINHO_LEITOS)
df_transicoes = pd.read_excel(CAMINHO_TRANSICOES)
df_medicos = pd.read_excel(CAMINHO_MEDICOS)
lista_medicos = sorted(df_medicos["Nome do Médico"].dropna().unique().tolist())

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
st.sidebar.title("🔧 Navegação")
opcao = st.sidebar.radio("Escolha a visualização:", ["Painel de Leitos", "Visão do Plantonista", "Listas do Dia", "Painel de Indicadores", "Cadastro de Médico"])

def salvar_leitos(df):
    df.to_excel(CAMINHO_LEITOS, index=False)

if opcao == "Painel de Leitos":
    st.title("📋 Painel de Leitos por Unidade e Andar")
    unidade = st.selectbox("Unidade", list(estrutura_leitos.keys()))
    andar = st.selectbox("Andar", list(estrutura_leitos[unidade].keys()))
    leitos = estrutura_leitos[unidade][andar]
    colunas = st.columns(6)

    for i, leito in enumerate(sorted(leitos)):
        chave = f"{unidade}_{andar}_{leito}"
        paciente = df_leitos[df_leitos["chave"] == chave]
        nome = paciente["nome"].values[0] if not paciente.empty else "[Vazio]"

        with colunas[i % 6]:
            st.markdown(f"**Leito {leito}**")
            if "medico" in dados and pd.notna(dados["medico"]):
                st.markdown(f"👨‍⚕️ {dados['medico']}")
            if st.button(f"✏️ {nome}", key=f"btn_{chave}"):
                st.session_state["editando"] = chave

        if st.session_state.get("editando") == chave:
            with st.expander(f"Editar Leito {leito} - {unidade} - {andar}", expanded=True):
                dados = paciente.iloc[0] if not paciente.empty else {}
                nome = st.text_input("Nome do paciente", value=dados.get("nome", ""))
                medico = st.selectbox("Médico responsável", options=lista_medicos)
                risco = st.selectbox("Risco assistencial", ["Baixo", "Moderado", "Alto"])
                operadora = st.selectbox("Operadora", ["AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"])
                pendencia = st.text_area("Pendência da rotina", value=dados.get("pendencia", ""))
                paliativo = st.radio("Cuidados paliativos?", ["Sim", "Não"], horizontal=True)
                cirurgia = st.radio("Cirurgia programada?", ["Sim", "Não"], horizontal=True)
                desospitalizacao = st.radio("Em desospitalização?", ["Sim", "Não"], horizontal=True)
                alta_amanha = st.radio("Alta prevista para amanhã?", ["Sim", "Não"], horizontal=True)
                intercorrencia = st.selectbox("Intercorrência", ["Nenhuma", "Verde", "Amarela", "Laranja", "Azul", "Outro"])
                desc_intercorrencia = st.text_area("Descrição da intercorrência", value=dados.get("desc_intercorrencia", ""))
                reavaliacao = st.radio("Reavaliação necessária?", ["Sim", "Não"], horizontal=True)
                observacoes = st.text_area("Observações gerais", value=dados.get("observacoes", ""))

                if st.button("Salvar", key=f"salvar_{chave}"):
                    df_leitos.drop(df_leitos[df_leitos["chave"] == chave].index, inplace=True)
                    novo = pd.DataFrame([{
                        "chave": chave, "nome": nome, "medico": medico, "registrado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "leito": leito, "unidade": unidade, "andar": andar, "risco": risco, "operadora": operadora,
                        "pendencia": pendencia, "paliativo": paliativo, "cirurgia": cirurgia,
                        "desospitalizacao": desospitalizacao, "alta_amanha": alta_amanha,
                        "intercorrencia": intercorrencia, "desc_intercorrencia": desc_intercorrencia,
                        "reavaliacao": reavaliacao, "observacoes": observacoes
                    }])
                    df_leitos = pd.concat([df_leitos, novo], ignore_index=True)
                    salvar_leitos(df_leitos)
                    del st.session_state["editando"]
                    st.rerun()

elif opcao == "Visão do Plantonista":
    st.title("👨‍⚕️ Visão do Plantonista")
    with st.form("form_transicao"):
        nome = st.text_input("Nome do paciente")
        origem = st.selectbox("Origem", ["Emergência", "CTI", "Outros"])
        obs = st.text_area("Observações")
        if st.form_submit_button("Adicionar à Transição") and nome:
            df_transicoes = pd.concat([df_transicoes, pd.DataFrame([[nome, origem, obs]], columns=df_transicoes.columns)], ignore_index=True)
            df_transicoes.to_excel(CAMINHO_TRANSICOES, index=False)
            st.success("Paciente adicionado à transição.")

    st.subheader("📋 Pacientes aguardando leito")
    for idx, row in df_transicoes.iterrows():
        with st.expander(f"{row['nome']} ({row['origem']})"):
            st.text(row["observacoes"])
            if st.button("Admitir", key=f"admitir_{idx}"):
                df_transicoes.drop(index=idx, inplace=True)
                df_transicoes.to_excel(CAMINHO_TRANSICOES, index=False)
                st.session_state["nome_em_transicao"] = row.to_dict()
                st.success("Informações transferidas para cadastro de leito.")

elif opcao == "Listas do Dia":
    st.title("📆 Listas do Dia")
    st.subheader("🟢 Altas previstas para hoje")
    st.dataframe(df_leitos[df_leitos["alta_amanha"] == "Sim"][["leito", "nome", "medico"]])

    st.subheader("💳 Pacientes com operadora AMIL")
    st.dataframe(df_leitos[df_leitos["operadora"] == "AMIL"][["leito", "nome", "medico"]])

elif opcao == "Painel de Indicadores":
    st.title("📊 Painel de Indicadores")
    total = len(df_leitos)
    interc = df_leitos["intercorrencia"].value_counts()
    paliativos = len(df_leitos[df_leitos["paliativo"] == "Sim"])
    st.metric("Pacientes internados", total)
    for cor in ["Verde", "Amarela", "Laranja", "Azul"]:
        st.metric(f"Intercorrências {cor}", interc.get(cor, 0))
    df_multi = df_leitos[df_leitos.duplicated("nome", keep=False)]
    df_critico = df_leitos[(df_leitos["risco"] == "Alto") & (df_leitos["intercorrencia"] != "Nenhuma")]
    st.subheader("⚠️ Múltiplas intercorrências")
    st.dataframe(df_multi[["leito", "nome", "intercorrencia"]])
    st.subheader("🧠 Risco alto + intercorrência")
    st.dataframe(df_critico[["leito", "nome", "intercorrencia", "risco"]])

elif opcao == "Cadastro de Médico":
    st.title("🩺 Cadastro de Médico")
    nome_medico = st.text_input("Nome completo do novo médico")
    if st.button("Adicionar Médico") and nome_medico.strip():
        df_medicos = pd.concat([df_medicos, pd.DataFrame([[nome_medico]], columns=["Nome do Médico"])])
        df_medicos = df_medicos.drop_duplicates().sort_values("Nome do Médico")
        df_medicos.to_excel(CAMINHO_MEDICOS, index=False)
        st.success("Médico cadastrado com sucesso!")
    st.dataframe(df_medicos)
