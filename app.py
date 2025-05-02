import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import os

# ------------------------------
# Configurações iniciais
# ------------------------------
st.set_page_config(layout="wide")
st.title("📋 Painel de Leitos")

# ------------------------------
# Funções auxiliares
# ------------------------------
def carregar_medicos():
    caminho = "Cadastro_Medicos.xlsx"
    if Path(caminho).exists():
        df = pd.read_excel(caminho)
        return sorted(df["Nome do Médico"].dropna().unique().tolist())
    return []

def carregar_base():
    if Path("base_leitos.xlsx").exists():
        return pd.read_excel("base_leitos.xlsx")
    return pd.DataFrame(columns=["leito", "nome", "medico", "especialidade", "operadora", "pendencia", "procedimento", "cirurgia", "observacao", "risco"])

def salvar_base(df):
    df.to_excel("base_leitos.xlsx", index=False)

def valor(campo):
    val = st.session_state.get("dados", {}).get(campo, "")
    return "" if pd.isna(val) else val

# ------------------------------
# Sessões e estado
# ------------------------------
if "modo" not in st.session_state:
    st.session_state.modo = None
if "editando" not in st.session_state:
    st.session_state.editando = None
if "unidade_selecionada" not in st.session_state:
    st.session_state.unidade_selecionada = "Unidade I"
if "andar_selecionado" not in st.session_state:
    st.session_state.andar_selecionado = "4º andar"

# ------------------------------
# Dados principais
# ------------------------------
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

unidade = st.selectbox("Unidade", list(estrutura_leitos.keys()), index=list(estrutura_leitos.keys()).index(st.session_state.unidade_selecionada))
st.session_state.unidade_selecionada = unidade

if st.session_state.andar_selecionado not in estrutura_leitos[unidade]:
    st.session_state.andar_selecionado = list(estrutura_leitos[unidade].keys())[0]

andar = st.selectbox("Andar", list(estrutura_leitos[unidade].keys()), index=list(estrutura_leitos[unidade].keys()).index(st.session_state.andar_selecionado))
st.session_state.andar_selecionado = andar

# ------------------------------
# Carregar dados persistentes
# ------------------------------
df_leitos = carregar_base()
medicos = carregar_medicos()

# ------------------------------
# Edição ou ficha clínica
# ------------------------------
if st.session_state.modo == "cadastro" and st.session_state.editando:
    chave = st.session_state.editando
    unidade, andar, leito = chave.split("_")
    st.markdown(f"### 📝 Cadastro – Leito {leito} – {unidade} – {andar}")
    if st.button("⬅️ Voltar", key="voltar"):
        st.session_state.modo = None
        st.session_state.editando = None
        st.rerun()

    with st.form("cadastro_form"):
        nome = st.text_input("Nome do paciente", value=valor("nome"))
        medico = st.selectbox("Médico responsável", medicos, index=medicos.index(valor("medico")) if valor("medico") in medicos else 0)
        if st.form_submit_button("Salvar cadastro"):
            df_leitos.loc[df_leitos["leito"] == leito, ["nome", "medico"]] = [nome, medico]
            salvar_base(df_leitos)
            st.session_state.modo = None
            st.session_state.editando = None
            st.rerun()

elif st.session_state.modo == "ficha" and st.session_state.editando:
    chave = st.session_state.editando
    unidade, andar, leito = chave.split("_")
    st.markdown(f"### 📄 Ficha Clínica – Leito {leito} – {unidade} – {andar}")
    if st.button("⬅️ Voltar", key="voltar_ficha"):
        st.session_state.modo = None
        st.session_state.editando = None
        st.rerun()

    with st.form("ficha_form"):
        especialidade = st.selectbox("Especialidade médica", ["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Obstetrícia", "Pediatria", "Médico Assistente"], index=0 if valor("especialidade") == "" else ["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Obstetrícia", "Pediatria", "Médico Assistente"].index(valor("especialidade")))
        operadora = st.text_input("Operadora", value=valor("operadora"))
        pendencia = st.text_input("Pendência da rotina", value=valor("pendencia"))
        procedimento = st.text_input("Aguardando procedimento?", value=valor("procedimento"))
        cirurgia = st.text_input("Cirurgia programada?", value=valor("cirurgia"))
        observacao = st.text_area("Observações gerais", value=valor("observacao"))
        risco = st.selectbox("Risco assistencial", ["", "Baixo", "Moderado", "Alto"], index=0 if valor("risco") == "" else ["", "Baixo", "Moderado", "Alto"].index(valor("risco")))

        if st.form_submit_button("Salvar ficha clínica"):
            df_leitos.loc[df_leitos["leito"] == leito, ["especialidade", "operadora", "pendencia", "procedimento", "cirurgia", "observacao", "risco"]] = [
                especialidade, operadora, pendencia, procedimento, cirurgia, observacao, risco
            ]
            salvar_base(df_leitos)
            st.session_state.modo = None
            st.session_state.editando = None
            st.rerun()

else:
    leitos = estrutura_leitos[unidade][andar]
    df_leitos = carregar_base()
    colunas = st.columns(6)
    for i, leito in enumerate(sorted(leitos)):
        with colunas[i % 6]:
            st.markdown(f"**Leito {leito}**")
            dados_leito = df_leitos[df_leitos["leito"] == leito].squeeze()
            nome = dados_leito["nome"] if not dados_leito.empty else "[Vazio]"
            chave = f"{unidade}_{andar}_{leito}"
            if st.button(f"✏️ {nome}", key=f"cadastro_{chave}"):
                st.session_state.editando = chave
                st.session_state.modo = "cadastro"
                st.rerun()
            if nome != "[Vazio]" and st.button("📝 Ficha Clínica", key=f"ficha_{chave}"):
                st.session_state.editando = chave
                st.session_state.modo = "ficha"
                st.rerun()

# ------------------------------
# Cadastro de Médicos (Aba lateral)
# ------------------------------
st.sidebar.title("🩺 Cadastro de Médico")
novo_nome = st.sidebar.text_input("Nome completo do novo médico")
if st.sidebar.button("Adicionar Médico"):
    if novo_nome.strip():
        df_medicos = pd.DataFrame({"Nome do Médico": [novo_nome]})
        path = "Cadastro_Medicos.xlsx"
        if Path(path).exists():
            df_existente = pd.read_excel(path)
            df_final = pd.concat([df_existente, df_medicos]).drop_duplicates().sort_values("Nome do Médico")
        else:
            df_final = df_medicos
        df_final.to_excel(path, index=False)
        st.sidebar.success("Médico adicionado com sucesso!")
        st.rerun()

if Path("Cadastro_Medicos.xlsx").exists():
    st.sidebar.markdown("### 👨‍⚕️ Médicos Cadastrados")
    st.sidebar.dataframe(pd.read_excel("Cadastro_Medicos.xlsx"))
