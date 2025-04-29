import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração do app
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
            "Data de Atualização", "Risco Assistencial", "Número do Atendimento", "Nome do Paciente",
            "Número do Leito", "Unidade", "Andar", "Equipe", "Nome do Médico Responsável",
            "Cuidado Paliativo", "Pendência do Turno", "Aguarda Desospitalização", "Aguarda Cirurgia",
            "Operadora de Saúde", "Origem do Paciente", "Intercorrência", "Código da Intercorrência",
            "Alta Prevista para Amanhã", "Foi Alta", "Setor Atual", "Observações"
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

def carregar_dados_altas():
    try:
        return pd.read_excel("Pacientes_Altas.xlsx")
    except:
        return pd.DataFrame()

def salvar_dados_altas(df):
    df.to_excel("Pacientes_Altas.xlsx", index=False)

def carregar_dados_obitos():
    try:
        return pd.read_excel("Pacientes_Obitos.xlsx")
    except:
        return pd.DataFrame()

def salvar_dados_obitos(df):
    df.to_excel("Pacientes_Obitos.xlsx", index=False)

# Carregar dados iniciais
df_pacientes = carregar_dados_pacientes()
df_medicos = carregar_dados_medicos()
df_altas = carregar_dados_altas()
df_obitos = carregar_dados_obitos()

# Menu lateral
menu = st.sidebar.radio("Menu", ["Painel de Internações", "Cadastro de Paciente", "Cadastro de Médico"])

if menu == "Painel de Internações":
    st.title("Painel de Internações")

    filtro_medico = st.selectbox("Filtrar por Médico (ou Todos):", ["Todos"] + sorted(df_medicos["Nome do Médico"].dropna().tolist()))

    if filtro_medico != "Todos":
        pacientes_filtrados = df_pacientes[(df_pacientes["Nome do Médico Responsável"] == filtro_medico) & (df_pacientes["Foi Alta"] != "Sim") & (df_pacientes["Setor Atual"] != "CTI")]
    else:
        pacientes_filtrados = df_pacientes[(df_pacientes["Foi Alta"] != "Sim") & (df_pacientes["Setor Atual"] != "CTI")]

    pacientes_filtrados = pacientes_filtrados.sort_values(by=["Unidade", "Andar", "Número do Leito"])

    for index, paciente in pacientes_filtrados.iterrows():
        if st.button(f"Editar {paciente['Número do Atendimento']} - {paciente['Nome do Paciente']}"):
            with st.form(f"editar_paciente_{index}"):
                risco = st.selectbox("Risco Assistencial *", ["Baixo", "Moderado", "Alto"], index=["Baixo", "Moderado", "Alto"].index(paciente["Risco Assistencial"]))
                nome = st.text_input("Nome do Paciente *", value=paciente["Nome do Paciente"])
                numero_leito = st.text_input("Número do Leito *", value=paciente["Número do Leito"])
                unidade = st.selectbox("Unidade *", ["Unidade I", "Unidade III", "Unidade IV"], index=["Unidade I", "Unidade III", "Unidade IV"].index(paciente["Unidade"]))
                andar = st.number_input("Andar *", value=int(paciente["Andar"]), step=1)
                equipe = st.selectbox("Equipe *", ["Hematologia", "Oncologia", "TMO", "Hepatologia", "Cardiologia", "Clínica Médica", "GO", "Pediatria", "MA"], index=["Hematologia", "Oncologia", "TMO", "Hepatologia", "Cardiologia", "Clínica Médica", "GO", "Pediatria", "MA"].index(paciente["Equipe"]))
                medico = st.selectbox("Nome do Médico Responsável *", sorted(df_medicos["Nome do Médico"].dropna().tolist()), index=sorted(df_medicos["Nome do Médico"].dropna().tolist()).index(paciente["Nome do Médico Responsável"]))
                paliativo = st.selectbox("Cuidado Paliativo *", ["Sim", "Não"], index=["Sim", "Não"].index(paciente["Cuidado Paliativo"]))
                pendencia = st.text_area("Pendência do Turno", value=paciente["Pendência do Turno"])
                desospitalizacao = st.selectbox("Aguarda Desospitalização? *", ["Sim", "Não"], index=["Sim", "Não"].index(paciente["Aguarda Desospitalização"]))
                cirurgia = st.selectbox("Aguarda Cirurgia? *", ["Sim", "Não"], index=["Sim", "Não"].index(paciente["Aguarda Cirurgia"]))
                operadora = st.text_input("Operadora de Saúde", value=paciente["Operadora de Saúde"])
                origem = st.selectbox("Origem do Paciente", ["UTI", "Emergência", "Outros"], index=["UTI", "Emergência", "Outros"].index(paciente["Origem do Paciente"]))
                intercorrencia = st.selectbox("Intercorrência", ["", "Código Azul", "Código Amarelo", "Código Laranja", "Código Verde", "Outro"], index=["", "Código Azul", "Código Amarelo", "Código Laranja", "Código Verde", "Outro"].index(paciente["Intercorrência"]))
                codigo_intercorrencia = st.text_input("Código da Intercorrência", value=paciente["Código da Intercorrência"])
                alta_prevista = st.selectbox("Alta Prevista para Amanhã?", ["Sim", "Não"], index=["Sim", "Não"].index(paciente["Alta Prevista para Amanhã"]))
                observacoes = st.text_area("Observações", value=paciente["Observações"])

                salvar = st.form_submit_button("Salvar")
                alta = st.form_submit_button("Dar Alta")
                transferir_cti = st.form_submit_button("Transferir para CTI")
                obito = st.form_submit_button("Registrar Óbito")

                if salvar:
                    df_pacientes.at[index, "Data de Atualização"] = datetime.now().date()
                    df_pacientes.at[index, "Risco Assistencial"] = risco
                    df_pacientes.at[index, "Nome do Paciente"] = nome
                    df_pacientes.at[index, "Número do Leito"] = numero_leito
                    df_pacientes.at[index, "Unidade"] = unidade
                    df_pacientes.at[index, "Andar"] = andar
                    df_pacientes.at[index, "Equipe"] = equipe
                    df_pacientes.at[index, "Nome do Médico Responsável"] = medico
                    df_pacientes.at[index, "Cuidado Paliativo"] = paliativo
                    df_pacientes.at[index, "Pendência do Turno"] = pendencia
                    df_pacientes.at[index, "Aguarda Desospitalização"] = desospitalizacao
                    df_pacientes.at[index, "Aguarda Cirurgia"] = cirurgia
                    df_pacientes.at[index, "Operadora de Saúde"] = operadora
                    df_pacientes.at[index, "Origem do Paciente"] = origem
                    df_pacientes.at[index, "Intercorrência"] = intercorrencia
                    df_pacientes.at[index, "Código da Intercorrência"] = codigo_intercorrencia
                    df_pacientes.at[index, "Alta Prevista para Amanhã"] = alta_prevista
                    df_pacientes.at[index, "Observações"] = observacoes
                    salvar_dados_pacientes(df_pacientes)
                    st.success("Alterado com sucesso!")

                if alta:
                    df_pacientes.at[index, "Foi Alta"] = "Sim"
                    df_altas = pd.concat([df_altas, pd.DataFrame([df_pacientes.loc[index]])], ignore_index=True)
                    salvar_dados_altas(df_altas)
                    df_pacientes.drop(index, inplace=True)
                    salvar_dados_pacientes(df_pacientes)
                    st.success("Alta realizada com sucesso!")

                if transferir_cti:
                    df_pacientes.at[index, "Setor Atual"] = "CTI"
                    salvar_dados_pacientes(df_pacientes)
                    st.success("Paciente transferido para CTI!")

                if obito:
                    df_obitos = pd.concat([df_obitos, pd.DataFrame([df_pacientes.loc[index]])], ignore_index=True)
                    df_obitos.at[len(df_obitos)-1, "Data de Atualização"] = datetime.now().date()
                    salvar_dados_obitos(df_obitos)
                    df_pacientes.drop(index, inplace=True)
                    salvar_dados_pacientes(df_pacientes)
                    st.success("Óbito registrado com sucesso!")

# Cadastro de Paciente
elif menu == "Cadastro de Paciente":
    st.title("Cadastro de Novo Paciente")

    with st.form("cadastro_paciente"):
        numero_atendimento = st.text_input("Número do Atendimento *")
        nome_paciente = st.text_input("Nome do Paciente *")
        numero_leito = st.text_input("Número do Leito *")
        unidade = st.selectbox("Unidade *", ["Unidade I", "Unidade III", "Unidade IV"])
        andar = st.number_input("Andar *", step=1)
        equipe = st.selectbox("Equipe *", ["Hematologia", "Oncologia", "TMO", "Hepatologia", "Cardiologia", "Clínica Médica", "GO", "Pediatria", "MA"])
        nome_medico = st.selectbox("Nome do Médico Responsável *", sorted(df_medicos["Nome do Médico"].dropna().tolist()))
        paliativo = st.selectbox("Cuidado Paliativo *", ["Sim", "Não"])
        pendencia_turno = st.text_area("Pendência do Turno")
        aguarda_desospitalizacao = st.selectbox("Aguarda Desospitalização?", ["Sim", "Não"])
        aguarda_cirurgia = st.selectbox("Aguarda Cirurgia?", ["Sim", "Não"])
        operadora = st.text_input("Operadora de Saúde")
        origem_paciente = st.selectbox("Origem do Paciente", ["UTI", "Emergência", "Outros"])
        intercorrencia = st.selectbox("Intercorrência", ["", "Código Azul", "Código Amarelo", "Código Laranja", "Código Verde", "Outro"])
        codigo_intercorrencia = st.text_input("Código da Intercorrência")
        risco_assistencial = st.selectbox("Risco Assistencial *", ["Baixo", "Moderado", "Alto"])
        alta_prevista = st.selectbox("Alta Prevista para Amanhã?", ["Sim", "Não"])
        observacoes = st.text_area("Observações")

        submitted = st.form_submit_button("Salvar")

        if submitted:
            novo_paciente = {
                "Data de Atualização": datetime.now().date(),
                "Risco Assistencial": risco_assistencial,
                "Número do Atendimento": numero_atendimento,
                "Nome do Paciente": nome_paciente,
                "Número do Leito": numero_leito,
                "Unidade": unidade,
                "Andar": andar,
                "Equipe": equipe,
                "Nome do Médico Responsável": nome_medico,
                "Cuidado Paliativo": paliativo,
                "Pendência do Turno": pendencia_turno,
                "Aguarda Desospitalização": aguarda_desospitalizacao,
                "Aguarda Cirurgia": aguarda_cirurgia,
                "Operadora de Saúde": operadora,
                "Origem do Paciente": origem_paciente,
                "Intercorrência": intercorrencia,
                "Código da Intercorrência": codigo_intercorrencia,
                "Alta Prevista para Amanhã": alta_prevista,
                "Foi Alta": "Não",
                "Setor Atual": "Leito",
                "Observações": observacoes
            }
            df_pacientes = pd.concat([df_pacientes, pd.DataFrame([novo_paciente])], ignore_index=True)
            salvar_dados_pacientes(df_pacientes)
            st.success("Paciente cadastrado com sucesso!")

elif menu == "Cadastro de Médico":
    st.title("Cadastro de Médico")

    with st.form("cadastro_medico"):
        novo_medico = st.text_input("Nome do Médico *")
        submitted_medico = st.form_submit_button("Salvar")

        if submitted_medico and novo_medico:
            df_medicos = pd.concat([df_medicos, pd.DataFrame([{"Nome do Médico": novo_medico}])], ignore_index=True)
            salvar_dados_medicos(df_medicos)
            st.success("Médico cadastrado com sucesso!")
