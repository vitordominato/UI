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
df_leitos = pd.read_excel(CAMINHO_LEITOS)
df_transicoes = pd.read_excel(CAMINHO_TRANSICOES)
df_medicos = pd.read_excel(CAMINHO_MEDICOS)
lista_medicos = sorted(df_medicos["Nome do Médico"].dropna().unique().tolist())

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

# Interface Streamlit
st.set_page_config(layout="wide")
st.sidebar.title("🔧 Navegação")
opcao = st.sidebar.radio("Escolha a visualização:", ["Painel de Leitos", "Visão do Plantonista", "Listas do Dia", "Painel de Indicadores", "Cadastro de Médico"])

# Painel de Leitos com slots por Unidade/Andar
if opcao == "Painel de Leitos":
    st.title("📋 Painel de Leitos por Unidade e Andar")
    unidade = st.selectbox("Unidade", list(estrutura_leitos.keys()))
    andar = st.selectbox("Andar", list(estrutura_leitos[unidade].keys()))
    leitos = estrutura_leitos[unidade][andar]

    cols = st.columns(2 if st.session_state.get("is_mobile") else 6)
    for i, leito in enumerate(leitos):
        chave = f"{unidade}_{andar}_{leito}"
        paciente = df_leitos[df_leitos["chave"] == chave]
        nome = paciente["nome"].values[0] if not paciente.empty else "[Vazio]"

        with cols[i % len(cols)]:
            st.markdown(f"**Leito {leito}**")
            if st.button(f"✏️ {nome}", key=f"edit_{chave}"):
                st.session_state["editando"] = chave

        if st.session_state.get("editando") == chave:
            with st.expander(f"Editar Leito {leito} - {unidade} - {andar}", expanded=True):
                dados = paciente.iloc[0] if not paciente.empty else {}
                nome = st.text_input("Nome do paciente", value=dados.get("nome", ""))
                medico = st.selectbox("Médico responsável", options=lista_medicos, index=lista_medicos.index(dados.get("medico")) if dados.get("medico") in lista_medicos else 0)
                risco = st.selectbox("Risco assistencial", ["Baixo", "Moderado", "Alto"], index=["Baixo", "Moderado", "Alto"].index(dados.get("risco", "Baixo")))
                operadora = st.selectbox("Operadora", ["AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"], index=0)
                pendencia = st.text_area("Pendência da rotina", value=dados.get("pendencia", ""))
                paliativo = st.radio("Cuidados paliativos?", ["Sim", "Não"], horizontal=True, index=0 if dados.get("paliativo") == "Sim" else 1)
                cirurgia = st.radio("Cirurgia programada?", ["Sim", "Não"], horizontal=True, index=0 if dados.get("cirurgia") == "Sim" else 1)
                desospitalizacao = st.radio("Em desospitalização?", ["Sim", "Não"], horizontal=True, index=0 if dados.get("desospitalizacao") == "Sim" else 1)
                alta_amanha = st.radio("Alta prevista para amanhã?", ["Sim", "Não"], horizontal=True, index=0 if dados.get("alta_amanha") == "Sim" else 1)
                intercorrencia = st.selectbox("Intercorrência", ["Nenhuma", "Verde", "Amarela", "Laranja", "Azul", "Outro"], index=["Nenhuma", "Verde", "Amarela", "Laranja", "Azul", "Outro"].index(dados.get("intercorrencia", "Nenhuma")))
                desc_intercorrencia = st.text_area("Descrição da intercorrência", value=dados.get("desc_intercorrencia", ""))
                reavaliacao = st.radio("Reavaliação necessária?", ["Sim", "Não"], horizontal=True, index=0 if dados.get("reavaliacao") == "Sim" else 1)
                observacoes = st.text_area("Observações gerais", value=dados.get("observacoes", ""))

                if st.button("Salvar", key=f"salvar_{chave}"):
                    df_leitos.drop(df_leitos[df_leitos["chave"] == chave].index, inplace=True)
                    novo = pd.DataFrame.from_dict([{
                        "chave": chave, "nome": nome, "medico": medico, "registrado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "leito": leito, "unidade": unidade, "andar": andar, "risco": risco, "operadora": operadora, "pendencia": pendencia,
                        "paliativo": paliativo, "cirurgia": cirurgia, "desospitalizacao": desospitalizacao, "alta_amanha": alta_amanha,
                        "intercorrencia": intercorrencia, "desc_intercorrencia": desc_intercorrencia, "reavaliacao": reavaliacao, "observacoes": observacoes
                    }])
                    df_leitos = pd.concat([df_leitos, novo], ignore_index=True)
                    df_leitos.to_excel(CAMINHO_LEITOS, index=False)
                    del st.session_state["editando"]
                    st.success("Leito salvo com sucesso!")
                    st.rerun()
