import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

st.set_page_config(layout="wide")

CAMINHO_MEDICOS = "Cadastro_Medicos.xlsx"
CAMINHO_LEITOS = "base_leitos.xlsx"

# Sessão de controle
if "modo" not in st.session_state:
    st.session_state.modo = None
if "editando" not in st.session_state:
    st.session_state.editando = None
if "unidade_selecionada" not in st.session_state:
    st.session_state.unidade_selecionada = "Unidade I"
if "andar_selecionado" not in st.session_state:
    st.session_state.andar_selecionado = "4º andar"

# Estrutura dos leitos
estrutura_leitos = {
    "Unidade I": {
        "4º andar": list(range(401, 433)),
        "5º andar": list(range(501, 536)),
        "6º andar": list(range(601, 638)),
    },
    "Unidade III": {
        "4º andar": list(range(401, 405)),
        "5º andar (Pediatria)": list(range(501, 511)),
        "6º andar (Pediatria)": list(range(601, 611)),
        "7º andar": list(range(701, 711)),
        "8º andar (Obstetrícia)": list(range(801, 811)),
        "9º andar (Obstetrícia)": list(range(901, 911)),
    },
    "Unidade IV": {
        "6º andar (TMO)": list(range(601, 627)),
        "7º andar (Cardiologia)": list(range(701, 729)),
        "8º andar": list(range(801, 829)),
        "9º andar": list(range(901, 929)),
    }
}

# Carregamento de dados
df_medicos = pd.read_excel(CAMINHO_MEDICOS) if Path(CAMINHO_MEDICOS).exists() else pd.DataFrame(columns=["Nome do Médico"])
lista_medicos = sorted(df_medicos["Nome do Médico"].dropna().unique().tolist())

colunas_ficha = [
    "leito", "nome", "medico", "especialidade", "operadora", "pendencia", "procedimento", "cirurgia",
    "paliativo", "desospitalizacao", "alta_amanha", "intercorrencia", "descricao_intercorrencia", "reavaliacao",
    "observacao", "risco"
]
df_leitos = pd.read_excel(CAMINHO_LEITOS) if Path(CAMINHO_LEITOS).exists() else pd.DataFrame(columns=colunas_ficha)
for col in colunas_ficha:
    if col not in df_leitos.columns:
        df_leitos[col] = ""

# Navegação
st.sidebar.title("🧭 Navegação")
aba = st.sidebar.radio("Ir para:", ["Painel de Leitos", "Cadastro de Médico"])

# Aba Cadastro de Médico
if aba == "Cadastro de Médico":
    st.title("🩺 Cadastro de Médico")
    novo_nome = st.sidebar.text_input("Nome do Médico")
    if st.sidebar.button("Adicionar Médico"):
        if novo_nome and novo_nome not in lista_medicos:
            df_medicos.loc[len(df_medicos)] = [novo_nome]
            df_medicos.to_excel(CAMINHO_MEDICOS, index=False)
            st.sidebar.success("Médico adicionado!")
            st.rerun()
    st.sidebar.markdown("### 👨‍⚕️ Médicos Atuais")
    st.sidebar.dataframe(df_medicos)

# Tela de ficha clínica
if st.session_state.modo == "ficha" and st.session_state.editando:
    leito = st.session_state.editando
    st.title(f"📝 Ficha Clínica – Leito {leito}")
    dados = df_leitos[df_leitos["leito"] == leito].squeeze() if leito in df_leitos["leito"].values else pd.Series()
    def val(campo): return dados[campo] if campo in dados and pd.notna(dados[campo]) else ""

    with st.form("form_ficha"):
        nome = st.text_input("Nome do paciente", value=val("nome"))
        medico = st.selectbox("Médico responsável", lista_medicos, index=lista_medicos.index(val("medico")) if val("medico") in lista_medicos else 0)
        especialidade = st.selectbox("Especialidade médica", ["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Obstetrícia", "Pediatria", "Médico Assistente"], index=0 if val("especialidade")=="" else ["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Obstetrícia", "Pediatria", "Médico Assistente"].index(val("especialidade")))
        operadora = st.text_input("Operadora", value=val("operadora"))
        pendencia = st.text_input("Pendência da rotina", value=val("pendencia"))
        procedimento = st.text_input("Aguardando procedimento?", value=val("procedimento"))
        cirurgia = st.text_input("Cirurgia programada?", value=val("cirurgia"))
        paliativo = st.selectbox("Cuidados paliativos?", ["", "Sim", "Não"], index=0 if val("paliativo")=="" else ["", "Sim", "Não"].index(val("paliativo")))
        desospitalizacao = st.selectbox("Em desospitalização?", ["", "Sim", "Não"], index=0 if val("desospitalizacao")=="" else ["", "Sim", "Não"].index(val("desospitalizacao")))
        alta_amanha = st.selectbox("Alta prevista para amanhã?", ["", "Sim", "Não"], index=0 if val("alta_amanha")=="" else ["", "Sim", "Não"].index(val("alta_amanha")))
        intercorrencia = st.selectbox("Intercorrência", ["", "Verde", "Amarela", "Laranja", "Azul", "Outros"], index=0 if val("intercorrencia")=="" else ["", "Verde", "Amarela", "Laranja", "Azul", "Outros"].index(val("intercorrencia")))
        descricao_intercorrencia = st.text_input("Descrição da intercorrência", value=val("descricao_intercorrencia"))
        reavaliacao = st.selectbox("Necessita reavaliação?", ["", "Sim", "Não"], index=0 if val("reavaliacao")=="" else ["", "Sim", "Não"].index(val("reavaliacao")))
        observacao = st.text_area("Observações gerais", value=val("observacao"))
        risco = st.selectbox("Risco assistencial", ["", "Baixo", "Moderado", "Alto"], index=0 if val("risco")=="" else ["", "Baixo", "Moderado", "Alto"].index(val("risco")))

        if st.form_submit_button("Salvar ficha"):
            df_leitos.loc[df_leitos["leito"] == leito, colunas_ficha[1:]] = [nome, medico, especialidade, operadora, pendencia, procedimento, cirurgia, paliativo, desospitalizacao, alta_amanha, intercorrencia, descricao_intercorrencia, reavaliacao, observacao, risco]
            df_leitos.to_excel(CAMINHO_LEITOS, index=False)
            st.success("Ficha salva!")
            st.session_state.modo = None
            st.session_state.editando = None
            st.rerun()

    if st.button("⬅️ Voltar"):
        st.session_state.modo = None
        st.session_state.editando = None
        st.rerun()

# Tela principal: Painel de Leitos
if st.session_state.modo is None and aba == "Painel de Leitos":
    st.title("📋 Painel de Leitos")
    unidade = st.selectbox("Unidade", list(estrutura_leitos.keys()), index=list(estrutura_leitos.keys()).index(st.session_state.unidade_selecionada))
    st.session_state.unidade_selecionada = unidade
    andar = st.selectbox("Andar", list(estrutura_leitos[unidade].keys()), index=list(estrutura_leitos[unidade].keys()).index(st.session_state.andar_selecionado))
    st.session_state.andar_selecionado = andar
    leitos = estrutura_leitos[unidade][andar]
    colunas = st.columns(6)

    for i, leito in enumerate(sorted(leitos)):
        with colunas[i % 6]:
            dados = df_leitos[df_leitos["leito"] == leito].squeeze()
            nome = dados["nome"] if "nome" in dados and pd.notna(dados["nome"]) else "[Vazio]"
            medico = dados["medico"] if "medico" in dados and pd.notna(dados["medico"]) else ""
            st.markdown(f"**Leito {leito}**")
            st.markdown(f"{nome}")
            if medico:
                st.markdown(f"👨‍⚕️ {medico}")
            if st.button(f"✏️", key=f"cadastro_{leito}"):
                st.session_state.modo = "cadastro"
                st.session_state.editando = leito
                st.rerun()
            if nome != "[Vazio]":
                if st.button(f"📝 Ficha Clínica", key=f"ficha_{leito}"):
                    st.session_state.modo = "ficha"
                    st.session_state.editando = leito
                    st.rerun()
