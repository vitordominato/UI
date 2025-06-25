import streamlit as st
import pandas as pd
from firebase_utils import (
    obter_leitos,
    salvar_leito,
    obter_ficha_clinica,
    salvar_ficha_clinica,
    limpar_ficha_clinica
)

COLUNAS_BASE = ["leito", "nome", "medico", "equipe", "unidade", "andar"]

def app():
    st.header("Painel de Leitos")
    leitos = pd.DataFrame(obter_leitos())
    if leitos.empty:
        st.info("Nenhum leito encontrado.")
        return

    unidades = sorted(leitos["unidade"].unique())
    filt_undo = st.sidebar.selectbox("Unidade", ["Todas"] + unidades)
    filtered = leitos[leitos["unidade"] == filt_undo] if filt_undo != "Todas" else leitos

    andares = sorted(filtered["andar"].unique())
    filt_anda = st.sidebar.selectbox("Andar", ["Todos"] + andares)
    filtered = filtered[filtered["andar"] == filt_anda] if filt_anda != "Todos" else filtered

    st.sidebar.button("Atualizar")

    for _, row in filtered.sort_values("leito").iterrows():
        with st.container():
            cols = st.columns([1, 3, 3, 2, 1])
            cols[0].markdown(f"**Leito {row['leito']}**")
            novo_nome = cols[1].text_input("Paciente", value=row.get("nome", ""), key=f"nome_{row['leito']}")
            novo_med = cols[2].text_input("Médico", value=row.get("medico", ""), key=f"med_{row['leito']}")
            nova_eq = cols[3].text_input("Equipe", value=row.get("equipe", ""), key=f"eq_{row['leito']}")
            if cols[4].button("Salvar", key=f"save_{row['leito']}"):
                data = row.to_dict()
                data.update({"nome": novo_nome, "medico": novo_med, "equipe": nova_eq})
                salvar_leito(row["leito"], data)
                st.success("Salvo!")

            with st.expander("Ficha Clínica"):
                render_ficha(row["leito"])

            st.markdown("---")

def render_ficha(leito_id):
    ficha = obter_ficha_clinica(leito_id) or {}
    oper = st.selectbox("Operadora", ["", "AMIL", "UNIMED", "Outros"], index=["", "AMIL", "UNIMED", "Outros"].index(ficha.get("operadora", "")), key=f"op_{leito_id}")
    risco = st.selectbox("Risco assistencial", ["", "Baixo", "Moderado", "Alto"], index=["", "Baixo", "Moderado", "Alto"].index(ficha.get("risco", "")), key=f"ri_{leito_id}")
    pend = st.selectbox("Pendência rotina?", ["Sim", "Não"], index=["Sim", "Não"].index(ficha.get("pendencia", "Não")), key=f"pe_{leito_id}")
    obs = st.text_area("Observações", value=ficha.get("obs", ""), key=f"ob_{leito_id}")
    if st.button("Alta", key=f"alta_{leito_id}"):
        limpar_ficha_clinica(leito_id)
        st.success("Paciente teve alta e ficha apagada.")
    if st.button("Salvar Ficha", key=f"sf_{leito_id}"):
        salvar_ficha_clinica(leito_id, {"operadora": oper, "risco": risco, "pendencia": pend, "obs": obs})
        st.success("Ficha salva!")
