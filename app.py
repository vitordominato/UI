import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📋 Painel de Leitos Hospitalar")

# Dados simulados
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

# Inicialização do estado
if "dados_pacientes" not in st.session_state:
    st.session_state["dados_pacientes"] = {}

# Filtros
unidades = list(estrutura_leitos.keys())
unidade_selecionada = st.selectbox("Unidade", unidades)
andares = list(estrutura_leitos[unidade_selecionada].keys())
andar_selecionado = st.selectbox("Andar", andares)

leitos = estrutura_leitos[unidade_selecionada][andar_selecionado]
colunas = st.columns(6)

for i, leito in enumerate(sorted(leitos)):
    chave = f"{unidade_selecionada}_{andar_selecionado}_{leito}"
    dados = st.session_state["dados_pacientes"].get(chave, {})
    nome = dados.get("nome", "[Vazio]")
    medico = dados.get("medico", "")
    with colunas[i % 6]:
        st.markdown(f"**Leito {leito}**")
        if st.button(f"✏️ {nome}", key=f"btn_{chave}"):
            st.session_state["editando"] = chave
            st.experimental_rerun()

# Tela de edição
if "editando" in st.session_state:
    chave = st.session_state["editando"]
    st.markdown("---")
    st.subheader(f"Editar Paciente – {chave}")
    nome = st.text_input("Nome do paciente", key=f"nome_{chave}")
    medico = st.text_input("Médico responsável", key=f"medico_{chave}")
    if st.button("Salvar dados", key=f"salvar_{chave}"):
        st.session_state["dados_pacientes"][chave] = {"nome": nome, "medico": medico}
        del st.session_state["editando"]
        st.experimental_rerun()