import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Gestão de Internações", layout="wide")

# Funções auxiliares
def carregar_dados_pacientes():
    try:
        return pd.read_excel("Planilha_Mestre_Internacoes_Atualizada.xlsx")
    except:
        return pd.DataFrame(columns=colunas)

def carregar_dados_medicos():
    try:
        return pd.read_excel("Cadastro_Medicos.xlsx")
    except:
        return pd.DataFrame(columns=["Nome do Médico"])

def salvar_dados_pacientes(df):
    df.to_excel("Planilha_Mestre_Internacoes_Atualizada.xlsx", index=False)

def carregar_dados_altas():
    try:
        return pd.read_excel("Pacientes_Altas_Atualizada.xlsx")
    except:
        return pd.DataFrame(columns=colunas)

def salvar_dados_altas(df):
    df.to_excel("Pacientes_Altas_Atualizada.xlsx", index=False)

def carregar_dados_obitos():
    try:
        return pd.read_excel("Pacientes_Obitos_Atualizada.xlsx")
    except:
        return pd.DataFrame(columns=colunas)

def salvar_dados_obitos(df):
    df.to_excel("Pacientes_Obitos_Atualizada.xlsx", index=False)

colunas = [
    "Data de Atualização", "Risco Assistencial", "Número do Atendimento", "Nome do Paciente",
    "Número do Leito", "Unidade", "Andar", "Equipe", "Nome do Médico Responsável",
    "Cuidado Paliativo", "Pendência do Turno", "Aguarda Desospitalização", "Aguarda Cirurgia",
    "Operadora de Saúde", "Origem do Paciente", "Intercorrência", "Descrição da Intercorrência",
    "Data/Hora da Intercorrência", "Alta Prevista para Amanhã", "Foi Alta", "Setor Atual", "Observações"
]

# Carregamento inicial
df_pacientes = carregar_dados_pacientes()
df_medicos = carregar_dados_medicos()
df_altas = carregar_dados_altas()
df_obitos = carregar_dados_obitos()

st.sidebar.title("Menu")
menu = st.sidebar.radio("Navegação", ["Painel de Internações", "Cadastro de Paciente", "Cadastro de Médico"])

if st.sidebar.button("🔄 Atualizar Lista"):
    st.experimental_rerun()

# Painel
if menu == "Painel de Internações":
    st.title("Painel de Internações")

    with st.sidebar.expander("📋 Filtros"):
        medico = st.selectbox("Médico Responsável", ["Todos"] + sorted(df_medicos["Nome do Médico"].dropna().unique().tolist()))
        equipe = st.selectbox("Equipe", ["Todos"] + sorted(df_pacientes["Equipe"].dropna().unique().tolist()))
        unidade = st.selectbox("Unidade", ["Todos"] + sorted(df_pacientes["Unidade"].dropna().unique().tolist()))
        andar = st.selectbox("Andar", ["Todos"] + sorted(df_pacientes["Andar"].dropna().unique().tolist()))
        risco = st.selectbox("Risco Assistencial", ["Todos", "Baixo", "Moderado", "Alto"])
        paliativo = st.selectbox("Cuidado Paliativo", ["Todos", "Sim", "Não"])
        setor = st.selectbox("Setor Atual", ["Todos"] + sorted(df_pacientes["Setor Atual"].dropna().unique().tolist()))
        interc = st.selectbox("Com Intercorrência", ["Todos", "Sim"])
        alta_prevista = st.selectbox("Alta Amanhã", ["Todos", "Sim", "Não"])

    if st.sidebar.button("🧹 Limpar Filtros"):
        st.experimental_rerun()

    if st.sidebar.button("🌙 Modo Plantão"):
        agora = datetime.now()
        ontem = agora - timedelta(hours=24)
        df_pacientes = df_pacientes[
            pd.to_datetime(df_pacientes["Data/Hora da Intercorrência"], errors='coerce') >= ontem
        ]

    # Aplicação dos filtros
    if medico != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Nome do Médico Responsável"] == medico]
    if equipe != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Equipe"] == equipe]
    if unidade != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Unidade"] == unidade]
    if andar != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Andar"] == andar]
    if risco != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Risco Assistencial"] == risco]
    if paliativo != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Cuidado Paliativo"] == paliativo]
    if setor != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Setor Atual"] == setor]
    else:
        df_pacientes = df_pacientes[df_pacientes["Setor Atual"] != "CTI"]
    if interc == "Sim":
        df_pacientes = df_pacientes[df_pacientes["Intercorrência"] != ""]
    if alta_prevista != "Todos":
        df_pacientes = df_pacientes[df_pacientes["Alta Prevista para Amanhã"] == alta_prevista]

    for i, row in df_pacientes.iterrows():
        if st.button(f"Editar Leito {row['Número do Leito']} - {row['Nome do Paciente']} - Dr. {row['Nome do Médico Responsável']}", key=i):
            st.session_state['paciente_editando'] = i

    if 'paciente_editando' in st.session_state:
        i = st.session_state['paciente_editando']
        with st.form("form_edit"):
            for col in colunas:
                if col == "Número do Atendimento":
                    st.text_input(col, value=df_pacientes.at[i, col], disabled=True)
                elif col in ["Data de Atualização", "Data/Hora da Intercorrência", "Foi Alta"]:
                    continue
                else:
                    df_pacientes.at[i, col] = st.text_input(col, value=df_pacientes.at[i, col])
            salvar = st.form_submit_button("Salvar")
            if salvar:
                df_pacientes.at[i, "Data de Atualização"] = datetime.now().date()
                if df_pacientes.at[i, "Intercorrência"] and not df_pacientes.at[i, "Data/Hora da Intercorrência"]:
                    df_pacientes.at[i, "Data/Hora da Intercorrência"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                salvar_dados_pacientes(df_pacientes)
                st.success("Alterações salvas.")
                st.experimental_rerun()

        if st.button("Transferir para CTI"):
            df_pacientes.at[i, "Setor Atual"] = "CTI"
            salvar_dados_pacientes(df_pacientes)
            st.success("Transferido para CTI.")
            st.experimental_rerun()

        if st.button("Dar Alta"):
            df_pacientes.at[i, "Foi Alta"] = "Sim"
            df_altas = pd.concat([df_altas, pd.DataFrame([df_pacientes.loc[i]])], ignore_index=True)
            salvar_dados_altas(df_altas)
            df_pacientes.drop(i, inplace=True)
            salvar_dados_pacientes(df_pacientes)
            st.success("Alta registrada.")
            st.experimental_rerun()

        if st.button("Registrar Óbito"):
            df_obitos = pd.concat([df_obitos, pd.DataFrame([df_pacientes.loc[i]])], ignore_index=True)
            salvar_dados_obitos(df_obitos)
            df_pacientes.drop(i, inplace=True)
            salvar_dados_pacientes(df_pacientes)
            st.success("Óbito registrado.")
            st.experimental_rerun()
