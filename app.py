import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

# Configuração da página
st.set_page_config(layout="wide")

# Caminhos dos arquivos
CAMINHO_MEDICOS = "Cadastro_Medicos.xlsx"
CAMINHO_LEITOS = "base_leitos.xlsx"
CAMINHO_TRANSICOES = "transicoes.xlsx"

# Inicializar variáveis de sessão
if "modo" not in st.session_state:
    st.session_state.modo = None
if "leito_selecionado" not in st.session_state:
    st.session_state.leito_selecionado = None
if "unidade_selecionada" not in st.session_state:
    st.session_state.unidade_selecionada = "Unidade I"
if "andar_selecionado" not in st.session_state:
    st.session_state.andar_selecionado = "4º andar"

# Estrutura de leitos
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

# Carregar médicos
if Path(CAMINHO_MEDICOS).exists():
    df_medicos = pd.read_excel(CAMINHO_MEDICOS)
    lista_medicos = sorted(df_medicos["Nome do Médico"].dropna().unique().tolist())
else:
    lista_medicos = []

# Carregar base de leitos
if Path(CAMINHO_LEITOS).exists():
    df_leitos = pd.read_excel(CAMINHO_LEITOS)
else:
    df_leitos = pd.DataFrame(columns=["chave", "nome", "medico", "especialidade", "risco", "operadora", "intercorrencia", "paliativo", "alta_amanha", "pendencia", "procedimento", "cirurgia", "observacao"])

# Navegação
st.sidebar.title("🧭 Navegação")
pagina = st.sidebar.radio("Escolha a aba:", ["Painel de Leitos", "Cadastro de Médico"])

# Página: Cadastro de Médico
if pagina == "Cadastro de Médico":
    st.markdown("## 🩺 Cadastro de Médico")
    novo_nome = st.text_input("Nome completo do novo médico")

    if st.button("Adicionar Médico"):
        if novo_nome.strip() != "":
            df_novo = pd.DataFrame([[novo_nome]], columns=["Nome do Médico"])
            df_medicos = pd.concat([df_medicos, df_novo], ignore_index=True).drop_duplicates().sort_values("Nome do Médico")
            df_medicos.to_excel(CAMINHO_MEDICOS, index=False)
            st.success("✅ Médico cadastrado com sucesso!")
        else:
            st.warning("⚠️ Nome inválido.")

    st.markdown("### 👨‍⚕️ Médicos Cadastrados")
    st.dataframe(df_medicos)

# Página: Painel de Leitos
elif pagina == "Painel de Leitos":
    st.title("📋 Painel de Leitos")

    unidade = st.selectbox("Unidade", list(estrutura_leitos.keys()), index=list(estrutura_leitos.keys()).index(st.session_state.unidade_selecionada))
    st.session_state.unidade_selecionada = unidade

    andares_disponiveis = list(estrutura_leitos[unidade].keys())
    if st.session_state.andar_selecionado not in andares_disponiveis:
        st.session_state.andar_selecionado = andares_disponiveis[0]

    andar = st.selectbox("Andar", andares_disponiveis, index=andares_disponiveis.index(st.session_state.andar_selecionado))
    st.session_state.andar_selecionado = andar

    leitos = sorted(estrutura_leitos[unidade][andar])

    for leito in leitos:
        chave = f"{unidade}_{andar}_{leito}"
        dados = df_leitos[df_leitos["chave"] == chave].iloc[0] if chave in df_leitos["chave"].values else pd.Series()
        nome = dados.get("nome", "[Vazio]") if not dados.empty else "[Vazio]"

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### Leito {leito}")
        with col2:
            if st.button(f"✏️ {nome}", key=f"cadastro_{chave}"):
                st.session_state.modo = "cadastro"
                st.session_state.leito_selecionado = chave
                st.experimental_rerun()

# Página de edição separada
if st.session_state.modo == "cadastro" and st.session_state.leito_selecionado:
    st.title(f"✏️ Cadastro – {st.session_state.leito_selecionado.replace('_', ' – ')}")

    if st.button("🔙 Voltar", key="voltar"):
        st.session_state.modo = None
        st.experimental_rerun()

    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome do paciente")
    with col2:
        medico = st.selectbox("Médico responsável", options=lista_medicos)

    if st.button("Salvar cadastro"):
        dados_novos = {
            "chave": st.session_state.leito_selecionado,
            "nome": nome,
            "medico": medico,
            "registrado_em": datetime.now().strftime("%d/%m/%Y %H:%M")
        }

        df_leitos = df_leitos[df_leitos["chave"] != st.session_state.leito_selecionado]
        df_leitos = pd.concat([df_leitos, pd.DataFrame([dados_novos])], ignore_index=True)
        df_leitos.to_excel(CAMINHO_LEITOS, index=False)

        st.session_state.modo = None
        st.experimental_rerun()