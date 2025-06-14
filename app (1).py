
import streamlit as st
from firebase_utils import (
    get_leitos_cached, salvar_leito, obter_ficha_clinica, salvar_ficha_clinica
)
import pandas as pd
import numpy as np

st.set_page_config(page_title="Gestão Hospitalar", layout="wide")

st.title("Gestão de Leitos Hospitalares")
st.caption("Multiusuário com Firebase. Filtros por unidade, andar, médico e leito.")

def garantir_colunas(df):
    colunas_obrigatorias = ["leito", "unidade", "andar", "medico", "nome"]
    for col in colunas_obrigatorias:
        if col not in df.columns:
            df[col] = ""
    return df

def sanitize_dict(dados):
    for k, v in dados.items():
        if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
            dados[k] = ""
        if v is None:
            dados[k] = ""
    return dados

df_leitos = garantir_colunas(get_leitos_cached())

if df_leitos.empty:
    st.warning("Nenhum leito cadastrado.")
    st.stop()

col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
with col_f1:
    unidade = st.selectbox("Unidade", sorted(df_leitos["unidade"].dropna().unique()))
with col_f2:
    andares_disp = sorted(df_leitos[df_leitos["unidade"] == unidade]["andar"].dropna().unique())
    andar = st.selectbox("Andar", andares_disp)
with col_f3:
    medicos_disp = sorted(df_leitos["medico"].dropna().unique())
    medico = st.selectbox("Médico", ["Todos"] + medicos_disp)

df_filtrado = df_leitos[
    (df_leitos["unidade"] == unidade) & 
    (df_leitos["andar"] == andar)
]
if medico != "Todos":
    df_filtrado = df_filtrado[df_filtrado["medico"] == medico]

df_filtrado = df_filtrado.sort_values("leito")

st.header(f"Leitos - {unidade}, {andar} ({'Todos' if medico=='Todos' else medico})")

for idx, row in df_filtrado.iterrows():
    leito_id = row['leito']
    with st.expander(f"Leito {leito_id} | Paciente: {row.get('nome','') or 'Vago'}", expanded=False):
        novo_nome = st.text_input("Nome do paciente", value=row.get("nome", ""), key=f"nome_{leito_id}")
        novo_medico = st.text_input("Médico responsável", value=row.get("medico", ""), key=f"medico_{leito_id}")
        nova_unidade = st.text_input("Unidade", value=row.get("unidade", ""), key=f"unidade_{leito_id}")
        novo_andar = st.text_input("Andar", value=row.get("andar", ""), key=f"andar_{leito_id}")

        if st.button("Salvar dados do leito", key=f"save_leito_{leito_id}"):
            novos_dados = {
                "leito": leito_id,
                "nome": novo_nome,
                "medico": novo_medico,
                "unidade": nova_unidade,
                "andar": novo_andar,
            }
            salvar_leito(leito_id, sanitize_dict(novos_dados))
            st.success("Dados do leito atualizados!")

        st.markdown("#### Ficha Clínica Completa")
        ficha = obter_ficha_clinica(leito_id) or {}

        diagnostico = st.text_input("Diagnóstico", value=ficha.get("diagnostico", ""), key=f"diag_{leito_id}")
        risco = st.selectbox("Risco assistencial", ["", "Baixo", "Médio", "Alto"], index=["", "Baixo", "Médio", "Alto"].index(ficha.get("risco", "")), key=f"risco_{leito_id}")
        observacoes = st.text_area("Observações", value=ficha.get("observacoes", ""), key=f"obs_{leito_id}")

        if st.button("Salvar ficha clínica", key=f"save_ficha_{leito_id}"):
            ficha_salvar = {
                "diagnostico": diagnostico,
                "risco": risco,
                "observacoes": observacoes,
            }
            salvar_ficha_clinica(leito_id, sanitize_dict(ficha_salvar))
            st.success("Ficha clínica salva!")

        if st.button("Limpar leito (alta)", key=f"limpar_{leito_id}"):
            salvar_leito(leito_id, sanitize_dict({
                "leito": leito_id,
                "nome": "",
                "medico": "",
                "unidade": nova_unidade,
                "andar": novo_andar,
            }))
            salvar_ficha_clinica(leito_id, {})
            st.success("Leito liberado para nova internação.")

st.caption("Desenvolvido por Vitor Dominato | Backend 100% Firebase | Multiusuário em tempo real.")
