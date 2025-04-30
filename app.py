
import streamlit as st
import pandas as pd
from datetime import datetime
import openpyxl

st.set_page_config(layout="wide")

# Carregamento das planilhas
df_pacientes = pd.read_excel("Planilha_Mestre_Internacoes_Atualizada.xlsx")
df_medicos = pd.read_excel("Cadastro_Medicos.xlsx")

st.sidebar.title("Menu")
pagina = st.sidebar.radio("Navegação", ["Painel de Internações", "Cadastro de Paciente", "Cadastro de Médico"])

if pagina == "Painel de Internações":
    st.title("Painel de Internações")

    with st.sidebar.expander("Filtros"):
        medico = st.selectbox("Médico", ["Todos"] + sorted(df_pacientes["Nome do Médico Responsável"].dropna().unique().tolist()))
        unidade = st.selectbox("Unidade", ["Todos"] + sorted(df_pacientes["Unidade"].dropna().unique().tolist()))
        andar = st.selectbox("Andar", ["Todos"] + sorted(df_pacientes["Andar"].dropna().astype(str).unique().tolist()))
        risco = st.selectbox("Risco Assistencial", ["Todos"] + sorted(df_pacientes["Risco Assistencial"].dropna().unique().tolist()))
        paliativo = st.selectbox("Cuidado Paliativo", ["Todos"] + sorted(df_pacientes["Cuidado Paliativo"].dropna().astype(str).str.capitalize().unique().tolist()))
        alta_amanha = st.selectbox("Alta Prevista para Amanhã", ["Todos"] + sorted(df_pacientes["Alta Prevista para Amanhã"].dropna().astype(str).str.capitalize().unique().tolist()))
        equipe = st.selectbox("Equipe", ["Todos"] + sorted(df_pacientes["Equipe"].dropna().unique().tolist()))
        operadora = st.selectbox("Operadora de Saúde", ["Todos"] + sorted(df_pacientes["Operadora de Saúde"].dropna().unique().tolist()))
        cirurgia = st.selectbox("Aguarda Cirurgia", ["Todos"] + sorted(df_pacientes["Aguarda Cirurgia"].dropna().astype(str).str.capitalize().unique().tolist()))
        desosp = st.selectbox("Aguarda Desospitalização", ["Todos"] + sorted(df_pacientes["Aguarda Desospitalização"].dropna().astype(str).str.capitalize().unique().tolist()))

    if medico != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Nome do Médico Responsável"] == medico]
    if unidade != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Unidade"] == unidade]
    if andar != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Andar"].astype(str) == andar]
    if risco != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Risco Assistencial"] == risco]
    if paliativo != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Cuidado Paliativo"].str.lower() == paliativo.lower()]
    if alta_amanha != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Alta Prevista para Amanhã"].str.lower() == alta_amanha.lower()]
    if equipe != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Equipe"] == equipe]
    if operadora != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Operadora de Saúde"] == operadora]
    if cirurgia != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Aguarda Cirurgia"].str.lower() == cirurgia.lower()]
    if desosp != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Aguarda Desospitalização"].str.lower() == desosp.lower()]

    for _, row in df_pacientes.iterrows():
        st.button(f"{row['Nome do Paciente']} - Leito {row['Número do Leito']} - Dr. {row['Nome do Médico Responsável']}")
