
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração inicial
st.set_page_config(layout="wide")
CAMINHO_MEDICOS = "Cadastro_Medicos.xlsx"
CAMINHO_LEITOS = "base_leitos.xlsx"

# Listas padrão
especialidades = ["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Obstetrícia", "Pediatria", "Médico Assistente"]
operadoras = ["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermédica", "outros"]
risco_assistencial = ["", "Baixo", "Moderado", "Alto"]
intercorrencias = ["", "Verde", "Amarela", "Laranja", "Azul", "Outros"]

# Carrega médicos
if os.path.exists(CAMINHO_MEDICOS):
    df_medicos = pd.read_excel(CAMINHO_MEDICOS)
    lista_medicos = sorted(df_medicos["Nome do Médico"].dropna().unique().tolist())
else:
    lista_medicos = []

# Carrega dados dos leitos
if os.path.exists(CAMINHO_LEITOS):
    df_leitos = pd.read_excel(CAMINHO_LEITOS)
else:
    df_leitos = pd.DataFrame(columns=[
        "leito", "nome", "medico", "especialidade", "risco", "operadora", "pendencia", "paliativo",
        "cirurgia", "desospitalizacao", "alta_amanha", "intercorrencia", "descricao_intercorrencia", "reavaliacao", "observacoes"
    ])

# Funções utilitárias
def salvar_df():
    df_leitos.sort_values(by="leito", inplace=True)
    df_leitos.to_excel(CAMINHO_LEITOS, index=False)

# Navegação
aba = st.sidebar.radio("Navegação", ["Painel de Leitos", "Cadastro de Médico"])

# Aba: Cadastro de Médico
if aba == "Cadastro de Médico":
    st.title("Cadastro de Médico")
    novo = st.text_input("Nome do Médico")
    if st.button("Salvar Médico"):
        if novo and novo not in lista_medicos:
            df_medicos.loc[len(df_medicos)] = [novo]
            df_medicos.drop_duplicates().to_excel(CAMINHO_MEDICOS, index=False)
            st.success("Médico salvo com sucesso.")

# Aba: Painel de Leitos
elif aba == "Painel de Leitos":
    st.title("📋 Painel de Leitos")
    leitos_ordenados = sorted(df_leitos["leito"].unique()) if not df_leitos.empty else []
    leito_sel = st.selectbox("Selecione um leito", leitos_ordenados)

    paciente = df_leitos[df_leitos["leito"] == leito_sel]
    if not paciente.empty:
        dados = paciente.iloc[0].to_dict()
        st.subheader(f"Leito {leito_sel} – {dados.get('nome', '')}")
        with st.form("ficha"):
            nome = st.text_input("Nome do paciente", value=dados.get("nome", "") or "")
            medico = st.selectbox("Médico responsável", options=lista_medicos, index=lista_medicos.index(dados["medico"]) if dados.get("medico") in lista_medicos else 0)
            especialidade = st.selectbox("Especialidade médica", especialidades, index=especialidades.index(dados.get("especialidade") or ""))
            risco = st.selectbox("Risco assistencial", risco_assistencial, index=risco_assistencial.index(dados.get("risco") or ""))
            operadora = st.selectbox("Operadora", operadoras, index=operadoras.index(dados.get("operadora") or ""))
            pendencia = st.selectbox("Pendência da rotina", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(dados.get("pendencia") or ""))
            paliativo = st.selectbox("Cuidados paliativos", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(dados.get("paliativo") or ""))
            cirurgia = st.selectbox("Cirurgia programada", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(dados.get("cirurgia") or ""))
            desospitalizacao = st.selectbox("Desospitalização", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(dados.get("desospitalizacao") or ""))
            alta = st.selectbox("Alta amanhã?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(dados.get("alta_amanha") or ""))
            intercorrencia = st.selectbox("Intercorrência", intercorrencias, index=intercorrencias.index(dados.get("intercorrencia") or ""))
            descricao = st.text_area("Descrição da intercorrência", value=dados.get("descricao_intercorrencia") if pd.notna(dados.get("descricao_intercorrencia")) else "")
            reavaliacao = st.selectbox("Reavaliação", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(dados.get("reavaliacao") or ""))
            observacoes = st.text_area("Observações", value=dados.get("observacoes") if pd.notna(dados.get("observacoes")) else "")

            col1, col2, col3 = st.columns(3)
            salvar = col1.form_submit_button("Salvar")
            alta_btn = col2.form_submit_button("Alta / Óbito / Transferência")
            voltar = col3.form_submit_button("↩️ Voltar")

        if salvar:
            df_leitos.loc[df_leitos["leito"] == leito_sel] = [leito_sel, nome, medico, especialidade, risco, operadora,
                                                              pendencia, paliativo, cirurgia, desospitalizacao,
                                                              alta, intercorrencia, descricao, reavaliacao, observacoes]
            salvar_df()
            st.success("Ficha atualizada.")

        if alta_btn:
            df_leitos = df_leitos[df_leitos["leito"] != leito_sel]
            salvar_df()
            st.warning("Leito liberado por alta, óbito ou transferência.")

        if voltar:
            st.experimental_rerun()
