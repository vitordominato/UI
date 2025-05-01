
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Caminhos dos arquivos
CAMINHO_LEITOS = "base_leitos.xlsx"
CAMINHO_TRANSICOES = "transicoes.xlsx"
CAMINHO_MEDICOS = "Cadastro_Medicos.xlsx"
CAMINHO_HISTORICO = "historico_leitos.xlsx"

# Campos padrão
CAMPOS = [
    "chave", "nome", "medico", "registrado_em", "leito", "unidade", "andar",
    "risco", "operadora", "pendencia", "paliativo", "cirurgia", "desospitalizacao",
    "alta_amanha", "intercorrencia", "desc_intercorrencia", "reavaliacao", "observacoes"
]

# Inicialização das planilhas
for path, cols in [
    (CAMINHO_LEITOS, CAMPOS),
    (CAMINHO_TRANSICOES, ["nome", "origem", "observacoes"]),
    (CAMINHO_MEDICOS, ["Nome do Médico"]),
    (CAMINHO_HISTORICO, CAMPOS + ["desfecho", "data_desfecho"])
]:
    if not os.path.exists(path):
        pd.DataFrame(columns=cols).to_excel(path, index=False)

# Carregamento
df_leitos = pd.read_excel(CAMINHO_LEITOS)
df_transicoes = pd.read_excel(CAMINHO_TRANSICOES)
df_medicos = pd.read_excel(CAMINHO_MEDICOS)
df_historico = pd.read_excel(CAMINHO_HISTORICO)
lista_medicos = sorted(df_medicos["Nome do Médico"].dropna().unique().tolist())
lista_operadoras = ["AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"]

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

# Streamlit
st.set_page_config(layout="wide")
st.sidebar.title("🔧 Navegação")
opcao = st.sidebar.radio("Escolha a visualização:", [
    "Painel de Leitos", "Visão do Plantonista", "Listas do Dia",
    "Painel de Indicadores", "Cadastro de Médico"
])

if opcao == "Painel de Leitos":
    st.title("📋 Painel de Leitos por Unidade e Andar")
    unidade = st.selectbox("Unidade", list(estrutura_leitos.keys()))
    andar = st.selectbox("Andar", list(estrutura_leitos[unidade].keys()))
    leitos = estrutura_leitos[unidade][andar]
    colunas = st.columns(6)

    for i, leito in enumerate(leitos):
        chave = f"{unidade}_{andar}_{leito}"
        paciente = df_leitos[df_leitos["chave"] == chave]
        nome = paciente["nome"].values[0] if not paciente.empty else "[Vazio]"

        with colunas[i % 6]:
            st.markdown(f"**Leito {leito}**")
            if st.button(f"✏️ {nome}", key=f"btn_{chave}"):
                st.session_state["editando"] = chave

        if st.session_state.get("editando") == chave:
            with st.expander(f"Editar Leito {leito} - {unidade} - {andar}", expanded=True):
                dados = paciente.iloc[0] if not paciente.empty else {}
                nome = st.text_input("Nome do paciente", value=dados.get("nome", ""))
                medico = st.selectbox("Médico responsável", options=lista_medicos)

                if st.button("Salvar cadastro inicial", key=f"salvar_inicial_{chave}") and nome and medico:
                    df_leitos = df_leitos[df_leitos["chave"] != chave]
                    novo = pd.DataFrame([{
                        "chave": chave, "nome": nome, "medico": medico, "registrado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "leito": leito, "unidade": unidade, "andar": andar,
                        "risco": "", "operadora": "", "pendencia": "", "paliativo": "",
                        "cirurgia": "", "desospitalizacao": "", "alta_amanha": "",
                        "intercorrencia": "", "desc_intercorrencia": "", "reavaliacao": "", "observacoes": ""
                    }])
                    df_leitos = pd.concat([df_leitos, novo], ignore_index=True)
                    df_leitos.to_excel(CAMINHO_LEITOS, index=False)
                    st.success("Paciente cadastrado. Agora preencha a ficha clínica.")
                    st.rerun()
