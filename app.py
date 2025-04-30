import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Caminhos dos arquivos
CAMINHO_LEITOS = "base_leitos.xlsx"
CAMINHO_TRANSICOES = "transicoes.xlsx"
CAMINHO_MEDICOS = "Cadastro_Medicos.xlsx"

# Inicialização
colunas_leitos = [
    "chave", "nome", "medico", "registrado_em", "leito", "unidade", "andar",
    "risco", "operadora", "pendencia", "paliativo", "cirurgia",
    "desospitalizacao", "alta_amanha", "intercorrencia",
    "desc_intercorrencia", "reavaliacao", "observacoes"]

for path, columns in [
    (CAMINHO_LEITOS, colunas_leitos),
    (CAMINHO_TRANSICOES, ["nome", "origem", "observacoes"]),
    (CAMINHO_MEDICOS, ["Nome do Médico"])
]:
    if not os.path.exists(path):
        pd.DataFrame(columns=columns).to_excel(path, index=False)

# Carregar dados
try:
    df_leitos = pd.read_excel(CAMINHO_LEITOS)
except:
    df_leitos = pd.DataFrame(columns=colunas_leitos)

try:
    df_transicoes = pd.read_excel(CAMINHO_TRANSICOES)
except:
    df_transicoes = pd.DataFrame(columns=["nome", "origem", "observacoes"])

try:
    df_medicos = pd.read_excel(CAMINHO_MEDICOS)
    lista_medicos = sorted(df_medicos["Nome do Médico"].dropna().unique().tolist())
except:
    df_medicos = pd.DataFrame(columns=["Nome do Médico"])
    lista_medicos = []

# Interface Streamlit
st.set_page_config(layout="wide")
st.sidebar.title("🔧 Navegação")
opcao = st.sidebar.radio("Escolha a visualização:", ["Painel de Leitos", "Visão do Plantonista", "Listas do Dia", "Painel de Indicadores", "Cadastro de Médico"])

# Painel de Leitos
if opcao == "Painel de Leitos":
    st.title("🏥 Painel de Leitos")
    if df_leitos.empty:
        st.warning("Nenhum leito cadastrado ainda. Cadastre pelo plantonista ou manualmente.")
    else:
        df_leitos = df_leitos.sort_values(by=["unidade", "andar", "leito"])
        for idx, row in df_leitos.iterrows():
            with st.expander(f"{row['unidade']} - {row['andar']} - Leito {row['leito']}"):
                st.markdown(f"**Paciente:** {row['nome']}  ")
                st.markdown(f"**Médico:** {row['medico']}  ")
                st.markdown(f"**Risco:** {row['risco']} | **Alta Amanhã:** {row['alta_amanha']}")
                st.markdown(f"**Intercorrência:** {row['intercorrencia']} — {row['desc_intercorrencia']}")
                st.markdown(f"**Paliativo:** {row['paliativo']} | **Reavaliação:** {row['reavaliacao']}")
                st.markdown(f"**Obs:** {row['observacoes']}")

# Visão do Plantonista
elif opcao == "Visão do Plantonista":
    st.title("👨‍⚕️ Visão do Plantonista")
    with st.form("form_transicao"):
        nome = st.text_input("Nome do paciente")
        origem = st.selectbox("Origem", ["Emergência", "CTI", "Outros"])
        obs = st.text_area("Observações")
        submitted = st.form_submit_button("Adicionar à Transição")
        if submitted and nome:
            novo = pd.DataFrame([[nome, origem, obs]], columns=["nome", "origem", "observacoes"])
            df_transicoes = pd.concat([df_transicoes, novo], ignore_index=True)
            df_transicoes.to_excel(CAMINHO_TRANSICOES, index=False)
            st.success("Paciente adicionado à fila de transição.")

    st.subheader("📋 Pacientes aguardando leito")
    for idx, row in df_transicoes.iterrows():
        with st.expander(f"{row['nome']} ({row['origem']})"):
            st.text(row['observacoes'])
            if st.button("Admitir", key=f"admitir_{idx}"):
                novo_leito = {
                    "chave": f"trans_{idx}", "nome": row['nome'], "medico": "",
                    "registrado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "leito": "", "unidade": "", "andar": "",
                    "risco": "Baixo", "operadora": "Outros", "pendencia": "",
                    "paliativo": "Não", "cirurgia": "Não", "desospitalizacao": "Não",
                    "alta_amanha": "Não", "intercorrencia": "Nenhuma", "desc_intercorrencia": "",
                    "reavaliacao": "Não", "observacoes": row['observacoes']
                }
                df_leitos = pd.concat([df_leitos, pd.DataFrame([novo_leito])], ignore_index=True)
                df_leitos.to_excel(CAMINHO_LEITOS, index=False)
                df_transicoes.drop(index=idx, inplace=True)
                df_transicoes.to_excel(CAMINHO_TRANSICOES, index=False)
                st.rerun()

# Listas do Dia
elif opcao == "Listas do Dia":
    st.title("📆 Listas do Dia")
    if "alta_amanha" in df_leitos.columns:
        st.subheader("🟢 Altas previstas para hoje")
        st.dataframe(df_leitos[df_leitos["alta_amanha"] == "Sim"][["leito", "nome", "medico"]])

    if "operadora" in df_leitos.columns:
        st.subheader("💳 Pacientes com operadora AMIL")
        amil = df_leitos[df_leitos["operadora"] == "AMIL"]
        st.dataframe(amil[["leito", "nome", "medico"]])

# Painel de Indicadores
elif opcao == "Painel de Indicadores":
    st.title("📊 Painel de Indicadores")
    st.markdown("### Indicadores baseados em registros persistentes")

    if "intercorrencia" in df_leitos.columns:
        total_pacientes = len(df_leitos)
        interc_por_cor = df_leitos["intercorrencia"].value_counts()
        paliativos = df_leitos[df_leitos["paliativo"] == "Sim"]

        st.metric("Pacientes internados", total_pacientes)
        for cor in ["Verde", "Amarela", "Laranja", "Azul"]:
            st.metric(f"Intercorrências {cor}", interc_por_cor.get(cor, 0))

        st.subheader("📌 Pacientes com >1 intercorrência em 72h (simulado)")
        df_multi = df_leitos[df_leitos.duplicated("nome", keep=False)]
        st.dataframe(df_multi[["leito", "nome", "intercorrencia"]])

        st.subheader("🧠 Risco alto + intercorrência recente")
        df_critico = df_leitos[(df_leitos["risco"] == "Alto") & (df_leitos["intercorrencia"] != "Nenhuma")]
        st.dataframe(df_critico[["leito", "nome", "intercorrencia", "risco"]])

# Cadastro de Médico
elif opcao == "Cadastro de Médico":
    st.title("🩺 Cadastro de Médico")
    nome_medico = st.text_input("Nome completo do novo médico")
    if st.button("Adicionar Médico") and nome_medico.strip():
        df_medicos = pd.concat([df_medicos, pd.DataFrame([[nome_medico]], columns=["Nome do Médico"])])
        df_medicos = df_medicos.drop_duplicates().sort_values("Nome do Médico")
        df_medicos.to_excel(CAMINHO_MEDICOS, index=False)
        st.success("Médico cadastrado com sucesso!")
    st.dataframe(df_medicos)

