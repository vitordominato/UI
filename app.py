import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

CAMINHO_MEDICOS = "Cadastro_Medicos.xlsx"
CAMINHO_LEITOS = "base_leitos.xlsx"
CAMINHO_TRANSICOES = "transicoes.xlsx"

if not Path(CAMINHO_LEITOS).exists():
    df_leitos = pd.DataFrame(columns=["leito", "nome", "medico", "especialidade", "risco", "operadora", "pendencia", "paliativo", "cirurgia", "desospitalizacao", "alta_amanha", "intercorrencia", "observacoes"])
    df_leitos.to_excel(CAMINHO_LEITOS, index=False)
else:
    df_leitos = pd.read_excel(CAMINHO_LEITOS)

if not Path(CAMINHO_MEDICOS).exists():
    df_medicos = pd.DataFrame(columns=["Nome do Médico"])
    df_medicos.to_excel(CAMINHO_MEDICOS, index=False)
else:
    df_medicos = pd.read_excel(CAMINHO_MEDICOS)

if not Path(CAMINHO_TRANSICOES).exists():
    df_transicoes = pd.DataFrame(columns=["nome", "origem", "observacoes"])
    df_transicoes.to_excel(CAMINHO_TRANSICOES, index=False)
else:
    df_transicoes = pd.read_excel(CAMINHO_TRANSICOES)

lista_medicos = sorted(df_medicos["Nome do Médico"].dropna().unique().tolist())
lista_operadoras = ["AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "outros"]
lista_especialidades = ["Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Obstetrícia", "Pediatria", "Médico Assistente"]

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

st.set_page_config(page_title="Painel de Leitos", layout="wide")
st.title("📋 Painel de Leitos - Cadastro Inicial")

unidade = st.selectbox("Unidade", list(estrutura_leitos.keys()))
andar = st.selectbox("Andar", list(estrutura_leitos[unidade].keys()))

colunas = st.columns(6)
leitos_ordenados = sorted(estrutura_leitos[unidade][andar])

if "editando" not in st.session_state:
    st.session_state["editando"] = None

for i, leito in enumerate(leitos_ordenados):
    with colunas[i % 6]:
        dados = df_leitos[df_leitos["leito"] == leito]
        nome = dados["nome"].values[0] if not dados.empty else "[Vazio]"
        medico = dados["medico"].values[0] if not dados.empty else ""
        st.markdown(f"**Leito {leito}**")
        if st.button(f"✏️ {nome}", key=f"btn_{unidade}_{andar}_{leito}"):
            st.session_state["editando"] = leito
        if not pd.isna(medico) and medico != "":
            st.caption(f"👨‍⚕️ {medico}")

st.markdown("---")

if st.session_state["editando"]:
    leito = st.session_state["editando"]
    st.subheader(f"Cadastro para o Leito {leito}")
    dados = df_leitos[df_leitos["leito"] == leito]
    nome = dados["nome"].values[0] if not dados.empty else ""
    medico = dados["medico"].values[0] if not dados.empty else ""
    especialidade = dados["especialidade"].values[0] if not dados.empty else ""
    
    with st.form("formulario_cadastro"):
        nome_paciente = st.text_input("Nome do Paciente", value="" if pd.isna(nome) else nome)
        medico_responsavel = st.selectbox("Médico Responsável", options=[""] + lista_medicos, index=([""] + lista_medicos).index(medico) if medico in lista_medicos else 0)
        especialidade_medica = st.selectbox("Especialidade", options=[""] + lista_especialidades, index=([""] + lista_especialidades).index(especialidade) if especialidade in lista_especialidades else 0)

        col1, col2 = st.columns(2)
        with col1:
            salvar = st.form_submit_button("💾 Salvar")
        with col2:
            voltar = st.form_submit_button("↩️ Voltar")

        if salvar:
            if leito in df_leitos["leito"].values:
                df_leitos.loc[df_leitos["leito"] == leito, ["nome", "medico", "especialidade"]] = [nome_paciente, medico_responsavel, especialidade_medica]
            else:
                novo = pd.DataFrame([[leito, nome_paciente, medico_responsavel, especialidade_medica, "", "", "", "", "", "", "", "", ""]], columns=df_leitos.columns)
                df_leitos = pd.concat([df_leitos, novo], ignore_index=True)
            df_leitos.to_excel(CAMINHO_LEITOS, index=False)
            st.session_state["editando"] = None
import streamlit.runtime.scriptrunner.script_run_context as context
if context.get_script_run_ctx():
    st.experimental_rerun()

        if voltar:
            st.session_state["editando"] = None
