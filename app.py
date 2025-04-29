import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração do app para celular
st.set_page_config(page_title="Gestão de Internações", layout="wide")

# Estilo do botão Salvar (verde)
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Funções auxiliares
def carregar_dados_pacientes():
    try:
        return pd.read_excel("Planilha_Mestre_Internacoes_Com_Setor.xlsx")
    except:
        return pd.DataFrame(columns=[
            "Data de Atualização", "Número do Atendimento", "Número do Leito",
            "Unidade", "Andar", "Equipe", "Nome do Médico Responsável",
            "Pendência do Turno", "Aguarda Desospitalização", "Aguarda Cirurgia",
            "Operadora de Saúde", "Origem do Paciente", "Intercorrência",
            "Código da Intercorrência", "Risco Assistencial",
            "Alta Prevista para Amanhã", "Foi Alta", "Observações"
        ])

def carregar_dados_medicos():
    try:
        return pd.read_excel("Cadastro_Medicos.xlsx")
    except:
        return pd.DataFrame(columns=["Nome do Médico"])

def salvar_dados_pacientes(df):
    df.to_excel("Planilha_Mestre_Internacoes_Com_Setor.xlsx", index=False)

def salvar_dados_medicos(df):
    df.to_excel("Cadastro_Medicos.xlsx", index=False)

# Carregamento inicial
df_pacientes = carregar_dados_pacientes()
df_medicos = carregar_dados_medicos()

# Menu lateral
menu = st.sidebar.radio("Menu", ["Painel de Internações", "Cadastro de Paciente", "Cadastro de Médico"])

# Painel de Internações
if menu == "Painel de Internações":
    st.title("Painel de Internações")

    filtro_medico = st.selectbox("Filtrar por Médico (ou deixe vazio para ver todos):", ["Todos"] + sorted(df_medicos["Nome do Médico"].dropna().tolist()))

    if filtro_medico != "Todos":
        pacientes_filtrados = df_pacientes[(df_pacientes["Nome do Médico Responsável"] == filtro_medico) & (df_pacientes["Foi Alta"] != "Sim")]
    else:
        pacientes_filtrados = df_pacientes[df_pacientes["Foi Alta"] != "Sim"]

    pacientes_filtrados = pacientes_filtrados.sort_values(by=["Unidade", "Andar", "Número do Leito"])

    st.dataframe(pacientes_filtrados)

    st.subheader("Dar Alta a Paciente")
    numero_atendimento_alta = st.text_input("Número do Atendimento do Paciente para Alta:")

    if st.button("Salvar Alta"):
        if numero_atendimento_alta:
            df_pacientes.loc[df_pacientes["Número do Atendimento"] == numero_atendimento_alta, "Foi Alta"] = "Sim"
            salvar_dados_pacientes(df_pacientes)
            st.success("Alta registrada com sucesso!")
        else:
            st.error("Por favor, preencha o número do atendimento.")

# Cadastro de Paciente
elif menu == "Cadastro de Paciente":
    st.title("Cadastro de Novo Paciente")

    with st.form("cadastro_paciente"):
        numero_atendimento = st.text_input("Número do Atendimento *")
        numero_leito = st.text_input("Número do Leito *")
        unidade = st.selectbox("Unidade *", ["Unidade I", "Unidade III", "Unidade IV"])
        andar = st.number_input("Andar *", step=1)
        equipe = st.selectbox("Equipe *", ["Hematologia", "Oncologia", "TMO", "Hepatologia", "Cardiologia", "Clínica Médica", "GO", "Pediatria", "MA"])
        nome_medico = st.selectbox("Nome do Médico Responsável *", sorted(df_medicos["Nome do Médico"].dropna().tolist()))
        pendencia_turno = st.text_area("Pendência do Turno")
        aguarda_desospitalizacao = st.selectbox("Aguarda Desospitalização? *", ["Sim", "Não"])
        aguarda_cirurgia = st.selectbox("Aguarda Cirurgia? *", ["Sim", "Não"])
        operadora = st.text_input("Operadora de Saúde")
        origem_paciente = st.selectbox("Origem do Paciente", ["UTI", "Emergência", "Outros"])

        opcao_intercorrencia = st.selectbox("Intercorrência", ["", "Código Azul", "Código Amarelo", "Código Laranja", "Código Verde", "Outro"])
        if opcao_intercorrencia == "Outro":
            codigo_intercorrencia = st.text_input("Descreva a intercorrência")
        else:
            codigo_intercorrencia = opcao_intercorrencia

        risco_assistencial = st.selectbox("Risco Assistencial *", ["Baixo", "Moderado", "Alto"])
        alta_prevista = st.selectbox("Alta Prevista para Amanhã? *", ["Sim", "Não"])
        observacoes = st.text_area("Observações")

        submitted = st.form_submit_button("Salvar")

        if submitted:
            novo_paciente = {
                "Data de Atualização": datetime.now(),
                "Número do Atendimento": numero_atendimento,
                "Número do Leito": numero_leito,
                "Unidade": unidade,
                "Andar": andar,
                "Equipe": equipe,
                "Nome do Médico Responsável": nome_medico,
                "Pendência do Turno": pendencia_turno,
                "Aguarda Desospitalização": aguarda_desospitalizacao,
                "Aguarda Cirurgia": aguarda_cirurgia,
                "Operadora de Saúde": operadora,
                "Origem do Paciente": origem_paciente,
                "Intercorrência": "Sim" if codigo_intercorrencia else "Não",
                "Código da Intercorrência": codigo_intercorrencia,
                "Risco Assistencial": risco_assistencial,
                "Alta Prevista para Amanhã": alta_prevista,
                "Foi Alta": "Não",
                "Observações": observacoes
            }
            df_pacientes = pd.concat([df_pacientes, pd.DataFrame([novo_paciente])], ignore_index=True)
            salvar_dados_pacientes(df_pacientes)
            st.success("Paciente cadastrado com sucesso!")

# Cadastro de Médico
elif menu == "Cadastro de Médico":
    st.title("Cadastro de Médico")

    with st.form("cadastro_medico"):
        novo_medico = st.text_input("Nome do Médico *")
        submitted_medico = st.form_submit_button("Salvar")

        if submitted_medico and novo_medico:
            df_medicos = pd.concat([df_medicos, pd.DataFrame([{"Nome do Médico": novo_medico}])], ignore_index=True)
            salvar_dados_medicos(df_medicos)
            st.success("Médico cadastrado com sucesso!")
