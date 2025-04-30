import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gestão de Internações", layout="wide")

# Colunas padrão
colunas = [
    "Data de Atualização", "Risco Assistencial", "Número do Atendimento", "Nome do Paciente",
    "Número do Leito", "Unidade", "Andar", "Equipe", "Nome do Médico Responsável",
    "Cuidado Paliativo", "Pendência do Turno", "Aguarda Desospitalização", "Aguarda Cirurgia",
    "Operadora de Saúde", "Origem do Paciente", "Intercorrência", "Descrição da Intercorrência",
    "Data/Hora da Intercorrência", "Alta Prevista para Amanhã", "Foi Alta", "Setor Atual", "Observações"
]

def carregar_planilha(caminho, colunas_ref=None):
    try:
        df = pd.read_excel(caminho)
        if colunas_ref:
            for col in colunas_ref:
                if col not in df.columns:
                    df[col] = ""
        return df
    except:
        return pd.DataFrame(columns=colunas_ref if colunas_ref else [])

def salvar_planilha(df, caminho):
    df.to_excel(caminho, index=False)

# Carga
df_pacientes = carregar_planilha("Planilha_Mestre_Internacoes_Atualizada.xlsx", colunas)
df_medicos = carregar_planilha("Cadastro_Medicos.xlsx", ["Nome do Médico"])
df_altas = carregar_planilha("Pacientes_Altas_Atualizada.xlsx", colunas)
df_obitos = carregar_planilha("Pacientes_Obitos_Atualizada.xlsx", colunas)

st.sidebar.title("Menu")
pagina = st.sidebar.radio("Navegação", ["Painel de Internações", "Cadastro de Paciente", "Cadastro de Médico"])
st.sidebar.button("🔄 Atualizar Lista", on_click=st.rerun)

if pagina == "Cadastro de Paciente":
    st.title("Cadastro de Novo Paciente")
    with st.form("form_paciente"):
        atendimento = st.text_input("Número do Atendimento *")
        nome = st.text_input("Nome do Paciente *")
        leito = st.text_input("Número do Leito *")
        unidade = st.selectbox("Unidade *", ["Unidade I", "Unidade III", "Unidade IV"])
        andar = st.selectbox("Andar *", [str(i) for i in range(4, 10)])
        equipe = st.selectbox("Equipe *", ["hematologia", "oncologia", "tmo", "hepatologia", "cardiologia", "clínica médica", "GO", "pediatria", "MA"])
        medico = st.selectbox("Nome do Médico Responsável *", sorted(df_medicos["Nome do Médico"].dropna().unique().tolist()))
        risco = st.selectbox("Risco Assistencial *", ["Baixo", "Moderado", "Alto"])
        setor = st.text_input("Setor Atual *")
        salvar = st.form_submit_button("Salvar")
        if salvar:
            nova_linha = {
                "Data de Atualização": datetime.now().date(),
                "Risco Assistencial": risco,
                "Número do Atendimento": atendimento,
                "Nome do Paciente": nome,
                "Número do Leito": leito,
                "Unidade": unidade,
                "Andar": andar,
                "Equipe": equipe,
                "Nome do Médico Responsável": medico,
                "Setor Atual": setor
            }
            for col in colunas:
                if col not in nova_linha:
                    nova_linha[col] = ""
            df_pacientes = pd.concat([df_pacientes, pd.DataFrame([nova_linha])], ignore_index=True)
            salvar_planilha(df_pacientes, "Planilha_Mestre_Internacoes_Atualizada.xlsx")
            st.success("Paciente cadastrado com sucesso.")
            st.rerun()

elif pagina == "Cadastro de Médico":
    st.title("Cadastro de Médico")
    with st.form("form_medico"):
        novo_medico = st.text_input("Nome do Médico *")
        salvar = st.form_submit_button("Salvar")
        if salvar and novo_medico:
            df_medicos = pd.concat([df_medicos, pd.DataFrame([{"Nome do Médico": novo_medico}])], ignore_index=True)
            salvar_planilha(df_medicos, "Cadastro_Medicos.xlsx")
            st.success("Médico cadastrado com sucesso.")
            st.rerun()
