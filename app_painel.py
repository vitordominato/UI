
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Painel de Internações", layout="wide")

# Colunas padrão
colunas = [
    "Data de Atualização", "Risco Assistencial", "Número do Atendimento", "Nome do Paciente",
    "Número do Leito", "Unidade", "Andar", "Equipe", "Nome do Médico Responsável",
    "Cuidado Paliativo", "Pendência do Turno", "Aguarda Desospitalização", "Aguarda Cirurgia",
    "Operadora de Saúde", "Origem do Paciente", "Intercorrência", "Descrição da Intercorrência",
    "Data/Hora da Intercorrência", "Alta Prevista para Amanhã", "Foi Alta", "Setor Atual", "Observações"
]

# Funções auxiliares
def carregar_planilha(caminho):
    try:
        return pd.read_excel(caminho)
    except:
        return pd.DataFrame(columns=colunas)

def salvar_planilha(df, caminho):
    df.to_excel(caminho, index=False)

# Carga de dados
df_pacientes = carregar_planilha("Planilha_Mestre_Internacoes_Atualizada.xlsx")
df_medicos = carregar_planilha("Cadastro_Medicos.xlsx")

# Sidebar
st.sidebar.title("Painel de Internações")

# Filtros (exibidos sempre)
medico = st.sidebar.selectbox("Filtrar por Médico:", ["Todos"] + sorted(df_medicos["Nome do Médico"].dropna().unique().tolist()))
unidade = st.sidebar.selectbox("Unidade:", ["Todos"] + sorted(df_pacientes["Unidade"].dropna().unique().tolist()))
andar = st.sidebar.selectbox("Andar:", ["Todos"] + sorted(df_pacientes["Andar"].dropna().astype(str).unique().tolist()))

# Filtro aplicado ao DataFrame
filtro = df_pacientes.copy()
if medico != "Todos":
    filtro = filtro[filtro["Nome do Médico Responsável"] == medico]
if unidade != "Todos":
    filtro = filtro[filtro["Unidade"] == unidade]
if andar != "Todos":
    filtro = filtro[filtro["Andar"].astype(str) == andar]

# Oculta pacientes com Setor Atual = CTI
filtro = filtro[filtro["Setor Atual"] != "CTI"]

# Renderização do painel
st.title("Pacientes Internados")

if filtro.empty:
    st.info("Nenhum paciente encontrado com os filtros aplicados.")
else:
    for i, row in filtro.iterrows():
        if st.button(f"Editar Leito {row['Número do Leito']} - {row['Nome do Paciente']} - Dr. {row['Nome do Médico Responsável']}", key=f"editar_{i}"):
            st.session_state['editar_paciente'] = i

# Formulário de edição
if 'editar_paciente' in st.session_state:
    i = st.session_state['editar_paciente']
    st.subheader("Editar Paciente")

    with st.form("form_edicao"):
        st.text_input("Data de Atualização", value=df_pacientes.at[i, "Data de Atualização"], disabled=True)
        df_pacientes.at[i, "Risco Assistencial"] = st.selectbox("Risco Assistencial", ["Baixo", "Moderado", "Alto"], index=["Baixo", "Moderado", "Alto"].index(df_pacientes.at[i, "Risco Assistencial"]))
        df_pacientes.at[i, "Pendência do Turno"] = st.text_area("Pendência do Turno", value=df_pacientes.at[i, "Pendência do Turno"])
        df_pacientes.at[i, "Intercorrência"] = st.selectbox("Intercorrência", ["", "Código Azul", "Código Amarelo", "Código Laranja", "Código Verde", "Outro"], index=0 if pd.isna(df_pacientes.at[i, "Intercorrência"]) else ["", "Código Azul", "Código Amarelo", "Código Laranja", "Código Verde", "Outro"].index(df_pacientes.at[i, "Intercorrência"]))
        df_pacientes.at[i, "Descrição da Intercorrência"] = st.text_input("Descrição da Intercorrência", value=df_pacientes.at[i, "Descrição da Intercorrência"] or "")

        salvar = st.form_submit_button("Salvar")

        if salvar:
            df_pacientes.at[i, "Data de Atualização"] = datetime.now().date()
            if df_pacientes.at[i, "Intercorrência"] and not df_pacientes.at[i, "Data/Hora da Intercorrência"]:
                df_pacientes.at[i, "Data/Hora da Intercorrência"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            salvar_planilha(df_pacientes, "Planilha_Mestre_Internacoes_Atualizada.xlsx")
            st.success("Alterações salvas com sucesso.")
            st.rerun()
