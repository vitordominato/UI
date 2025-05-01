
import streamlit as st
import pandas as pd
from datetime import datetime
import os

CAMINHO_LEITOS = "base_leitos.xlsx"
CAMINHO_MEDICOS = "Cadastro_Medicos.xlsx"
CAMPOS = [
    "chave", "nome", "medico", "registrado_em", "leito", "unidade", "andar",
    "especialidade", "risco", "operadora", "pendencia", "paliativo", "cirurgia",
    "desospitalizacao", "alta_amanha", "intercorrencia", "desc_intercorrencia",
    "reavaliacao", "observacoes"
]

# Inicializa arquivos
for path, cols in [(CAMINHO_LEITOS, CAMPOS), (CAMINHO_MEDICOS, ["Nome do Médico"])]:
    if not os.path.exists(path):
        pd.DataFrame(columns=cols).to_excel(path, index=False)

df_leitos = pd.read_excel(CAMINHO_LEITOS)
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

# ---------------------- MODO CADASTRO ----------------------
if "editando" in st.session_state and st.session_state.get("modo") == "cadastro":
    selected_chave = st.session_state["editando"]
    unidade_sel, andar_sel, leito_sel = selected_chave.split("_")
    leito_sel = int(leito_sel)
    paciente_sel = df_leitos[df_leitos["chave"] == selected_chave]
    nome_sel = paciente_sel["nome"].values[0] if not paciente_sel.empty else ""
    medico_sel = paciente_sel["medico"].values[0] if not paciente_sel.empty else ""

    st.title(f"✏️ Cadastro – Leito {leito_sel} – {unidade_sel} – {andar_sel}")
    nome = st.text_input("Nome do paciente", value=nome_sel, key=f"nome_{selected_chave}")
    if lista_medicos:
        medico = st.selectbox("Médico responsável", options=lista_medicos,
                              index=lista_medicos.index(medico_sel) if medico_sel in lista_medicos else 0,
                              key=f"medico_{selected_chave}")
else:
    st.title("📋 Painel de Leitos")
    if "unidade_selecionada" not in st.session_state or st.session_state.unidade_selecionada not in estrutura_leitos:
        st.session_state.unidade_selecionada = list(estrutura_leitos.keys())[0]
    if "andar_selecionado" not in st.session_state or st.session_state.andar_selecionado not in estrutura_leitos[st.session_state.unidade_selecionada]:
        st.session_state.andar_selecionado = list(estrutura_leitos[st.session_state.unidade_selecionada].keys())[0]
    unidade = st.selectbox("Unidade", list(estrutura_leitos.keys()), index=list(estrutura_leitos.keys()).index(st.session_state.unidade_selecionada))
    if st.session_state.andar_selecionado not in estrutura_leitos[unidade]:
        st.session_state.andar_selecionado = list(estrutura_leitos[unidade].keys())[0]
    andar = st.selectbox("Andar", list(estrutura_leitos[unidade].keys()), index=list(estrutura_leitos[unidade].keys()).index(st.session_state.andar_selecionado))
    st.session_state.unidade_selecionada = unidade
    st.session_state.andar_selecionado = andar
    leitos = sorted(estrutura_leitos[unidade][andar])
    for leito in leitos:
        chave = f"{unidade}_{andar}_{leito}"
        paciente = df_leitos[df_leitos["chave"] == chave]
        nome = paciente["nome"].values[0] if not paciente.empty else "[Vazio]"
        st.markdown(f"**Leito {leito}**")
        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button(f"✏️ {nome}", key=f"cadastro_{chave}"):
                st.session_state["modo"] = "cadastro"
                st.session_state["editando"] = chave
                st.rerun()
        with col2:
            if not paciente.empty:
                if st.button("📝", key=f"ficha_{chave}"):
                    st.session_state["modo"] = "ficha"
                    st.session_state["editando"] = chave
                    st.rerun()
# ---------------------- MODO FICHA CLÍNICA ----------------------
elif "editando" in st.session_state and st.session_state.get("modo") == "ficha":
# ---------------------- PAINEL DE LEITOS ----------------------
else:
