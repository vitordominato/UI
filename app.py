import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Gestão de Internações", layout="wide")

# Colunas padrão
colunas = [
    "Data de Atualização", "Risco Assistencial", "Número do Atendimento", "Nome do Paciente",
    "Número do Leito", "Unidade", "Andar", "Equipe", "Nome do Médico Responsável",
    "Cuidado Paliativo", "Pendência do Turno", "Aguarda Desospitalização", "Aguarda Cirurgia",
    "Operadora de Saúde", "Origem do Paciente", "Intercorrência", "Descrição da Intercorrência",
    "Data/Hora da Intercorrência", "Alta Prevista para Amanhã", "Foi Alta", "Setor Atual", "Observações"
]

# Funções auxiliares
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

# Carga de dados
df_pacientes = carregar_planilha("Planilha_Mestre_Internacoes_Atualizada.xlsx", colunas)
df_medicos = carregar_planilha("Cadastro_Medicos.xlsx", ["Nome do Médico"])
df_altas = carregar_planilha("Pacientes_Altas_Atualizada.xlsx", colunas)
df_obitos = carregar_planilha("Pacientes_Obitos_Atualizada.xlsx", colunas)

st.sidebar.title("Menu")
pagina = st.sidebar.radio("Navegação", ["Painel de Internações", "Cadastro de Paciente", "Cadastro de Médico"])
st.sidebar.button("🔄 Atualizar Lista", on_click=st.rerun)

# ------------------ PAINEL ------------------
if pagina == "Painel de Internações":
    st.title("Pacientes Internados")

    if df_pacientes.empty:
        st.info("Nenhum paciente registrado no momento.")
    else:
        with st.sidebar.expander("Filtros"):
            medico = st.selectbox("Médico Responsável", ["Todos"] + sorted(df_medicos["Nome do Médico"].dropna().unique().tolist()))
            unidade = st.selectbox("Unidade", ["Todos"] + sorted(df_pacientes["Unidade"].dropna().unique().tolist()))
            andar = st.selectbox("Andar", ["Todos"] + sorted(df_pacientes["Andar"].dropna().astype(str).unique().tolist()))
            risco = st.selectbox("Risco Assistencial", ["Todos", "Baixo", "Moderado", "Alto"])
            setor = st.selectbox("Setor Atual", ["Todos"] + sorted(df_pacientes["Setor Atual"].dropna().unique().tolist()))
            interc = st.selectbox("Com Intercorrência", ["Todos", "Sim"])
            alta_prevista = st.selectbox("Alta Amanhã", ["Todos", "Sim", "Não"])
            paliativo = st.selectbox("Cuidado Paliativo", ["Todos", "Sim", "Não"])

        filtro = df_pacientes.copy()
        if medico != "Todos":
            filtro = filtro[filtro["Nome do Médico Responsável"] == medico]
        if unidade != "Todos":
            filtro = filtro[filtro["Unidade"] == unidade]
        if andar != "Todos":
            filtro = filtro[filtro["Andar"].astype(str) == andar]
        if risco != "Todos":
            filtro = filtro[filtro["Risco Assistencial"] == risco]
        if setor != "Todos":
            filtro = filtro[filtro["Setor Atual"] == setor]
        else:
            filtro = filtro[filtro["Setor Atual"] != "CTI"]
        if interc == "Sim":
            filtro = filtro[filtro["Intercorrência"] != ""]
        if alta_prevista != "Todos":
            filtro = filtro[filtro["Alta Prevista para Amanhã"] == alta_prevista]
        if paliativo != "Todos":
            filtro = filtro[filtro["Cuidado Paliativo"] == paliativo]

        if filtro.empty:
            st.warning("Nenhum paciente encontrado com os filtros aplicados.")
        else:
            for i, row in filtro.iterrows():
                if st.button(f"Editar Leito {row['Número do Leito']} - {row['Nome do Paciente']} - Dr. {row['Nome do Médico Responsável']}", key=f"edit_{i}"):
                    st.session_state['editar_paciente'] = row["Número do Atendimento"]

    if 'editar_paciente' in st.session_state:
        atendimento = st.session_state['editar_paciente']
        linha = df_pacientes[df_pacientes["Número do Atendimento"] == atendimento]
        if not linha.empty:
            i = linha.index[0]
            st.subheader("Editar Paciente")
            with st.form("form_edicao"):
                st.text_input("Data de Atualização", value=str(df_pacientes.at[i, "Data de Atualização"]), disabled=True)
                df_pacientes.at[i, "Risco Assistencial"] = st.selectbox("Risco Assistencial", ["Baixo", "Moderado", "Alto"], index=["Baixo", "Moderado", "Alto"].index(df_pacientes.at[i, "Risco Assistencial"]) if df_pacientes.at[i, "Risco Assistencial"] in ["Baixo", "Moderado", "Alto"] else 0)
                df_pacientes.at[i, "Pendência do Turno"] = st.text_area("Pendência do Turno", value=df_pacientes.at[i, "Pendência do Turno"])
                df_pacientes.at[i, "Intercorrência"] = st.selectbox("Intercorrência", ["", "Código Azul", "Código Amarelo", "Código Laranja", "Código Verde", "Outro"], index=0 if pd.isna(df_pacientes.at[i, "Intercorrência"]) else ["", "Código Azul", "Código Amarelo", "Código Laranja", "Código Verde", "Outro"].index(df_pacientes.at[i, "Intercorrência"]))
                df_pacientes.at[i, "Descrição da Intercorrência"] = st.text_input("Descrição da Intercorrência", value=df_pacientes.at[i, "Descrição da Intercorrência"])
                salvar = st.form_submit_button("Salvar")
                if salvar:
                    df_pacientes.at[i, "Data de Atualização"] = datetime.now().date()
                    if df_pacientes.at[i, "Intercorrência"] and not df_pacientes.at[i, "Data/Hora da Intercorrência"]:
                        df_pacientes.at[i, "Data/Hora da Intercorrência"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                    salvar_planilha(df_pacientes, "Planilha_Mestre_Internacoes_Atualizada.xlsx")
                    st.success("Alterações salvas com sucesso.")
                    st.rerun()

            if st.button("Transferir para CTI"):
                df_pacientes.at[i, "Setor Atual"] = "CTI"
                salvar_planilha(df_pacientes, "Planilha_Mestre_Internacoes_Atualizada.xlsx")
                st.success("Transferido para CTI.")
                st.rerun()

            if st.button("Dar Alta"):
                df_pacientes.at[i, "Foi Alta"] = "Sim"
                df_altas = pd.concat([df_altas, pd.DataFrame([df_pacientes.loc[i]])], ignore_index=True)
                salvar_planilha(df_altas, "Pacientes_Altas_Atualizada.xlsx")
                df_pacientes.drop(i, inplace=True)
                salvar_planilha(df_pacientes, "Planilha_Mestre_Internacoes_Atualizada.xlsx")
                st.success("Alta registrada.")
                st.rerun()

            if st.button("Registrar Óbito"):
                df_obitos = pd.concat([df_obitos, pd.DataFrame([df_pacientes.loc[i]])], ignore_index=True)
                salvar_planilha(df_obitos, "Pacientes_Obitos_Atualizada.xlsx")
                df_pacientes.drop(i, inplace=True)
                salvar_planilha(df_pacientes, "Planilha_Mestre_Internacoes_Atualizada.xlsx")
                st.success("Óbito registrado.")
                st.rerun()

# ------------------ CADASTRO DE MÉDICO ------------------
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
