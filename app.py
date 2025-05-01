
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Caminhos dos arquivos
CAMINHO_LEITOS = "base_leitos.xlsx"
CAMINHO_MEDICOS = "Cadastro_Medicos.xlsx"

# Campos mínimos
CAMPOS = ["chave", "nome", "medico", "registrado_em", "leito", "unidade", "andar"]

# Inicialização dos arquivos
for path, cols in [(CAMINHO_LEITOS, CAMPOS), (CAMINHO_MEDICOS, ["Nome do Médico"])]:
    if not os.path.exists(path):
        pd.DataFrame(columns=cols).to_excel(path, index=False)

# Carregamento
df_leitos = pd.read_excel(CAMINHO_LEITOS)
df_medicos = pd.read_excel(CAMINHO_MEDICOS)
lista_medicos = sorted(df_medicos["Nome do Médico"].dropna().unique().tolist())

# Estrutura dos leitos
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
st.title("📋 Painel de Leitos - Versão Mínima")

# Seleção de unidade e andar
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
            nome = st.text_input("Nome do paciente", value=nome)
            medico = st.selectbox("Médico responsável", options=lista_medicos) if lista_medicos else st.text_input("Médico responsável")

            if st.button("Salvar", key=f"salvar_{chave}"):
                df_leitos = df_leitos[df_leitos["chave"] != chave]
                novo = pd.DataFrame([{
                    "chave": chave, "nome": nome, "medico": medico,
                    "registrado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "leito": leito, "unidade": unidade, "andar": andar
                }])
                df_leitos = pd.concat([df_leitos, novo], ignore_index=True)
                df_leitos.to_excel(CAMINHO_LEITOS, index=False)
                st.success("Leito atualizado com sucesso.")
                st.rerun()
