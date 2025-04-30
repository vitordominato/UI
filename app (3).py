import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gestão de Internações", layout="wide")

# Colunas conforme planilha mestre
colunas = [
    "Data de Atualização", "Risco Assistencial", "Número do Atendimento", "Nome do Paciente",
    "Número do Leito", "Unidade", "Andar", "Equipe", "Nome do Médico Responsável",
    "Cuidado Paliativo", "Pendência do Turno", "Aguarda Desospitalização", "Aguarda Cirurgia",
    "Operadora de Saúde", "Origem do Paciente", "Intercorrência", "Descrição da Intercorrência",
    "Data/Hora da Intercorrência", "Alta Prevista para Amanhã", "Foi Alta", "Observações"
]

def carregar_planilha(caminho, colunas_ref):
    try:
        df = pd.read_excel(caminho)
        for col in colunas_ref:
            if col not in df.columns:
                df[col] = ""
        return df
    except:
        return pd.DataFrame(columns=colunas_ref)

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

# ---------------- PAINEL ----------------
if pagina == "Painel de Internações":
    st.title("Painel de Internações")
    if df_pacientes.empty:
        st.info("Nenhum paciente registrado.")
    else:
        with st.sidebar.expander("Filtros"):
            medico = st.selectbox("Médico", ["Todos"] + sorted(df_medicos["Nome do Médico"].dropna().unique().tolist()))
            unidade = st.selectbox("Unidade", ["Todos"] + sorted(df_pacientes["Unidade"].dropna().unique().tolist()))
            andar = st.selectbox("Andar", ["Todos"] + sorted(df_pacientes["Andar"].dropna().astype(str).unique().tolist()))
            risco = st.selectbox("Risco Assistencial", ["Todos", "Baixo", "Moderado", "Alto"])
            paliativo = st.selectbox("Cuidado Paliativo", ["Todos", "Sim", "Não"])
            alta_amanha = st.selectbox("Alta Amanhã", ["Todos", "Sim", "Não"])

        filtro = df_pacientes.copy()
        if medico != "Todos":
            filtro = filtro[filtro["Nome do Médico Responsável"] == medico]
        if unidade != "Todos":
            filtro = filtro[filtro["Unidade"] == unidade]
        if andar != "Todos":
            filtro = filtro[filtro["Andar"].astype(str) == andar]
        if risco != "Todos":
            filtro = filtro[filtro["Risco Assistencial"] == risco]
        if paliativo != "Todos":
            filtro = filtro[filtro["Cuidado Paliativo"] == paliativo]
        if alta_amanha != "Todos":
            filtro = filtro[filtro["Alta Prevista para Amanhã"] == alta_amanha]
        filtro = filtro[filtro["Foi Alta"] != "Sim"]

        if filtro.empty:
            st.warning("Nenhum paciente com os filtros aplicados.")
        else:
            for i, row in filtro.iterrows():
                if st.button(f"Editar: {row['Nome do Paciente']} - Leito {row['Número do Leito']} - Dr. {row['Nome do Médico Responsável']}", key=f"edit_{i}"):
                    st.session_state["editar"] = row["Número do Atendimento"]

    if "editar" in st.session_state:
        atendimento = st.session_state["editar"]
        linha = df_pacientes[df_pacientes["Número do Atendimento"] == atendimento]
        if not linha.empty:
            i = linha.index[0]
            st.subheader("Editar Paciente")
            with st.form("editar_paciente"):
                st.text_input("Data de Atualização", value=str(datetime.now().date()), disabled=True)
                df_pacientes.at[i, "Pendência do Turno"] = st.text_area("Pendência do Turno", value=df_pacientes.at[i, "Pendência do Turno"])
                opcoes_interc = ["", "Código Azul", "Código Amarelo", "Código Laranja", "Código Verde", "Outro"]
                val_interc = df_pacientes.at[i, "Intercorrência"]
                idx_interc = opcoes_interc.index(val_interc) if val_interc in opcoes_interc else 0
                df_pacientes.at[i, "Intercorrência"] = st.selectbox("Intercorrência", opcoes_interc, index=idx_interc)
                df_pacientes.at[i, "Descrição da Intercorrência"] = st.text_input("Descrição da Intercorrência", value=df_pacientes.at[i, "Descrição da Intercorrência"])
                df_pacientes.at[i, "Observações"] = st.text_area("Observações", value=df_pacientes.at[i, "Observações"])
                salvar = st.form_submit_button("Salvar")
                if salvar:
                    df_pacientes.at[i, "Data de Atualização"] = datetime.now().date()
                    if df_pacientes.at[i, "Intercorrência"] and not df_pacientes.at[i, "Data/Hora da Intercorrência"]:
                        df_pacientes.at[i, "Data/Hora da Intercorrência"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                    salvar_planilha(df_pacientes, "Planilha_Mestre_Internacoes_Atualizada.xlsx")
                    st.success("Paciente atualizado.")
                    st.rerun()

            if st.button("Transferir para CTI"):
                df_pacientes.at[i, "Origem do Paciente"] = "CTI"
                salvar_planilha(df_pacientes, "Planilha_Mestre_Internacoes_Atualizada.xlsx")
                st.success("Paciente transferido.")
                st.rerun()

            if st.button("Dar Alta"):
                df_pacientes.at[i, "Foi Alta"] = "Sim"
                df_altas = pd.concat([df_altas, pd.DataFrame([df_pacientes.loc[i]])], ignore_index=True)
                df_pacientes.drop(i, inplace=True)
                salvar_planilha(df_altas, "Pacientes_Altas_Atualizada.xlsx")
                salvar_planilha(df_pacientes, "Planilha_Mestre_Internacoes_Atualizada.xlsx")
                st.success("Alta registrada.")
                st.rerun()

            if st.button("Registrar Óbito"):
                df_obitos = pd.concat([df_obitos, pd.DataFrame([df_pacientes.loc[i]])], ignore_index=True)
                df_pacientes.drop(i, inplace=True)
                salvar_planilha(df_obitos, "Pacientes_Obitos_Atualizada.xlsx")
                salvar_planilha(df_pacientes, "Planilha_Mestre_Internacoes_Atualizada.xlsx")
                st.success("Óbito registrado.")
                st.rerun()

# ---------------- CADASTRO DE PACIENTE ----------------
elif pagina == "Cadastro de Paciente":
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
        paliativo = st.selectbox("Cuidado Paliativo *", ["Sim", "Não"])
        alta_amanha = st.selectbox("Alta Prevista para Amanhã", ["Sim", "Não"])
        cirurgia = st.selectbox("Aguarda Cirurgia", ["Sim", "Não"])
        desosp = st.selectbox("Aguarda Desospitalização", ["Sim", "Não"])
        operadora = st.text_input("Operadora de Saúde")
        origem = st.selectbox("Origem do Paciente", ["Emergência", "CTI", "Eletiva"])
        salvar = st.form_submit_button("Salvar")
        if salvar:
            nova = {
                "Data de Atualização": datetime.now().date(),
                "Risco Assistencial": risco,
                "Número do Atendimento": atendimento,
                "Nome do Paciente": nome,
                "Número do Leito": leito,
                "Unidade": unidade,
                "Andar": andar,
                "Equipe": equipe,
                "Nome do Médico Responsável": medico,
                "Cuidado Paliativo": paliativo,
                "Alta Prevista para Amanhã": alta_amanha,
                "Aguarda Cirurgia": cirurgia,
                "Aguarda Desospitalização": desosp,
                "Operadora de Saúde": operadora,
                "Origem do Paciente": origem
            }
            for col in colunas:
                if col not in nova:
                    nova[col] = ""
            df_pacientes = pd.concat([df_pacientes, pd.DataFrame([nova])], ignore_index=True)
            salvar_planilha(df_pacientes, "Planilha_Mestre_Internacoes_Atualizada.xlsx")
            st.success("Paciente cadastrado com sucesso.")
            st.rerun()

# ---------------- CADASTRO DE MÉDICO ----------------
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
