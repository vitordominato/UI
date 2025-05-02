import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

st.set_page_config(layout="wide")

# Arquivos
CAMINHO_MEDICOS = "Cadastro_Medicos.xlsx"
CAMINHO_LEITOS = "base_leitos.xlsx"

# Sessão
if "modo" not in st.session_state:
    st.session_state.modo = None
if "editando" not in st.session_state:
    st.session_state.editando = None
if "unidade_selecionada" not in st.session_state:
    st.session_state.unidade_selecionada = "Unidade I"
if "andar_selecionado" not in st.session_state:
    st.session_state.andar_selecionado = "4º andar"

# Estrutura
estrutura_leitos = {
    "Unidade I": {
        "4º andar": list(range(401, 433)),
        "5º andar": list(range(501, 536)),
        "6º andar": list(range(601, 638)),
    }
}

# Carregar arquivos
df_medicos = pd.read_excel(CAMINHO_MEDICOS) if Path(CAMINHO_MEDICOS).exists() else pd.DataFrame(columns=["Nome do Médico"])
lista_medicos = sorted(df_medicos["Nome do Médico"].dropna().unique().tolist())

colunas_necessarias = ["leito", "nome", "medico", "especialidade", "operadora", "pendencia", "procedimento",
    "cirurgia", "observacao", "risco", "intercorrencia", "descricao_intercorrencia", "paliativo", "desospitalizacao", "alta_amanha"]

df_leitos = pd.read_excel(CAMINHO_LEITOS) if Path(CAMINHO_LEITOS).exists() else pd.DataFrame(columns=colunas_necessarias)
for col in colunas_necessarias:
    if col not in df_leitos.columns:
        df_leitos[col] = ""

# Navegação
st.sidebar.title("🧭 Navegação")
pagina = st.sidebar.radio("Aba:", ["Painel de Leitos", "Cadastro de Médico"])

# Aba Cadastro de Médico
if pagina == "Cadastro de Médico":
    st.title("🩺 Cadastro de Médico")
    nome_novo = st.text_input("Nome do Médico")
    if st.button("Adicionar Médico"):
        if nome_novo.strip() and nome_novo not in lista_medicos:
            df_medicos.loc[len(df_medicos)] = [nome_novo]
            df_medicos.to_excel(CAMINHO_MEDICOS, index=False)
            st.success("Médico adicionado com sucesso!")
            st.rerun()
    st.subheader("👨‍⚕️ Médicos Cadastrados")
    st.dataframe(df_medicos)

# Aba Painel de Leitos
elif pagina == "Painel de Leitos":
    st.title("📋 Painel de Leitos")

    unidade = st.selectbox("Unidade", list(estrutura_leitos.keys()), index=list(estrutura_leitos.keys()).index(st.session_state.unidade_selecionada))
    st.session_state.unidade_selecionada = unidade

    andares = list(estrutura_leitos[unidade].keys())
    andar = st.selectbox("Andar", andares, index=andares.index(st.session_state.andar_selecionado))
    st.session_state.andar_selecionado = andar

    leitos = estrutura_leitos[unidade][andar]
    colunas = st.columns(6)

    for i, leito in enumerate(sorted(leitos)):
        with colunas[i % 6]:
            dados = df_leitos[df_leitos["leito"] == leito].squeeze()
            st.markdown(f"**Leito {leito}**")
            nome = dados["nome"] if "nome" in dados and pd.notna(dados["nome"]) else "[Vazio]"
            st.markdown(f"{nome}")
            if "medico" in dados and pd.notna(dados["medico"]):
                st.markdown(f"👨‍⚕️ {dados['medico']}")
            if st.button(f"✏️", key=f"cadastro_{leito}"):
                st.session_state.modo = "cadastro"
                st.session_state.editando = leito
                st.rerun()

# Tela de ficha clínica
if st.session_state.modo == "cadastro" and st.session_state.editando:
    leito = st.session_state.editando
    st.title(f"📝 Ficha Clínica – Leito {leito}")
    if st.button("⬅️ Voltar", key="voltar"):
        st.session_state.modo = None
        st.session_state.editando = None
        st.rerun()

    dados = df_leitos[df_leitos["leito"] == leito].squeeze() if leito in df_leitos["leito"].values else pd.Series()
    def val(campo): return dados[campo] if campo in dados and pd.notna(dados[campo]) else ""

    with st.form("ficha_form"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do paciente", value=val("nome"))
        with col2:
            medico = st.selectbox("Médico responsável", options=lista_medicos, index=lista_medicos.index(val("medico")) if val("medico") in lista_medicos else 0)
        especialidade = st.selectbox("Especialidade médica", ["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Obstetrícia", "Pediatria", "Médico Assistente"], index=0 if val("especialidade") == "" else ["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Obstetrícia", "Pediatria", "Médico Assistente"].index(val("especialidade")))
        operadora = st.text_input("Operadora", value=val("operadora"))
        pendencia = st.text_input("Pendência da rotina", value=val("pendencia"))
        procedimento = st.text_input("Aguardando procedimento?", value=val("procedimento"))
        cirurgia = st.text_input("Cirurgia programada?", value=val("cirurgia"))
        risco = st.selectbox("Risco assistencial", ["", "Baixo", "Moderado", "Alto"], index=0 if val("risco") == "" else ["", "Baixo", "Moderado", "Alto"].index(val("risco")))
        observacao = st.text_area("Observações gerais", value=val("observacao"))

        if st.form_submit_button("Salvar ficha clínica"):
            if leito not in df_leitos["leito"].values:
                novo = pd.DataFrame([[""] * len(df_leitos.columns)], columns=df_leitos.columns)
                novo.loc[0, "leito"] = leito
                novo.loc[0, "nome"] = nome
                novo.loc[0, "medico"] = medico
                novo.loc[0, "especialidade"] = especialidade
                novo.loc[0, "operadora"] = operadora
                novo.loc[0, "pendencia"] = pendencia
                novo.loc[0, "procedimento"] = procedimento
                novo.loc[0, "cirurgia"] = cirurgia
                novo.loc[0, "observacao"] = observacao
                novo.loc[0, "risco"] = risco
                df_leitos = pd.concat([df_leitos, novo], ignore_index=True)
            else:
                df_leitos.loc[df_leitos["leito"] == leito, ["nome", "medico", "especialidade", "operadora", "pendencia", "procedimento", "cirurgia", "observacao", "risco"]] = [nome, medico, especialidade, operadora, pendencia, procedimento, cirurgia, observacao, risco]
            df_leitos.to_excel(CAMINHO_LEITOS, index=False)
            st.success("Ficha clínica salva com sucesso!")
            st.session_state.modo = None
            st.session_state.editando = None
            st.rerun()