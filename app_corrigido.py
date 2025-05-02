
import streamlit as st
import pandas as pd
from datetime import datetime

# Simulação de dados
CAMINHO_MEDICOS = "Cadastro_Medicos.xlsx"
CAMINHO_LEITOS = "base_leitos.xlsx"

# Inicialização
if "pagina" not in st.session_state:
    st.session_state.pagina = "Painel de Leitos"

if "editando" not in st.session_state:
    st.session_state.editando = None

if "modo" not in st.session_state:
    st.session_state.modo = None

# Carregar lista de médicos
if Path(CAMINHO_MEDICOS).exists():
    df_medicos = pd.read_excel(CAMINHO_MEDICOS)
    lista_medicos = sorted(df_medicos["Nome do Médico"].dropna().unique().tolist())
else:
    df_medicos = pd.DataFrame(columns=["Nome do Médico"])
    lista_medicos = []

# Sidebar
st.sidebar.title("🔍 Navegação")
aba = st.sidebar.radio("Escolha a aba:", ["Painel de Leitos", "Cadastro de Médico"])
st.session_state.pagina = aba

# Aba: Cadastro de Médico
if st.session_state.pagina == "Cadastro de Médico":
    st.title("🩺 Cadastro de Médico")

    nome_novo = st.text_input("Nome completo do novo médico")
    if st.button("Adicionar Médico"):
        if nome_novo and nome_novo not in lista_medicos:
            df_medicos = pd.concat([df_medicos, pd.DataFrame([[nome_novo]], columns=["Nome do Médico"])])
            df_medicos = df_medicos.drop_duplicates().sort_values("Nome do Médico")
            df_medicos.to_excel(CAMINHO_MEDICOS, index=False)
            st.success("Médico adicionado com sucesso!")
        else:
            st.warning("Nome inválido ou já cadastrado.")

    st.subheader("👨‍⚕️ Médicos Cadastrados")
    st.dataframe(df_medicos)

# Aba: Painel de Leitos
elif st.session_state.pagina == "Painel de Leitos":
    st.title("📋 Painel de Leitos")

    estrutura_leitos = {
        "Unidade I": {"4º andar": list(range(401, 433))},
        "Unidade II": {"5º andar": list(range(501, 536))}
    }

    unidade = st.selectbox("Unidade", list(estrutura_leitos.keys()), key="unidade_selecionada")
    andar = st.selectbox("Andar", list(estrutura_leitos[unidade].keys()), key="andar_selecionado")

    leitos = estrutura_leitos[unidade][andar]
    leitos.sort()

    for leito in leitos:
        chave = f"{unidade}_{andar}_{leito}"
        nome = st.session_state.get(chave, {}).get("nome", "[Vazio]")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Leito {leito}**")
        with col2:
            if st.button(f"✏️ {nome}", key=f"btn_{chave}"):
                st.session_state.editando = chave
                st.session_state.modo = "cadastro"
                st.rerun()

# Página de edição/cadastro
if "editando" in st.session_state and st.session_state.editando:
    chave = st.session_state.editando
    unidade, andar, leito = chave.split("_")
    leito = int(leito)

    st.title(f"📝 Cadastro – Leito {leito} – {unidade} – {andar}")

    if st.button("🔙 Voltar", key="voltar"):
        st.session_state.modo = None
        st.session_state.editando = None
        st.rerun()

    nome_sel = st.session_state.get(chave, {}).get("nome", "")
    medico_sel = st.session_state.get(chave, {}).get("medico", lista_medicos[0] if lista_medicos else "")

    nome = st.text_input("Nome do paciente", value=nome_sel, key=f"nome_{chave}")
    if lista_medicos:
        medico = st.selectbox("Médico responsável", options=lista_medicos, index=lista_medicos.index(medico_sel) if medico_sel in lista_medicos else 0, key=f"medico_{chave}")
    else:
        medico = st.text_input("Médico responsável", value=medico_sel, key=f"medico_txt_{chave}")

    if st.button("Salvar cadastro"):
        st.session_state[chave] = {
            "nome": nome,
            "medico": medico,
            "hora": datetime.now().strftime("%H:%M:%S")
        }
        st.success("Cadastro salvo com sucesso!")
        st.session_state.modo = None
        st.session_state.editando = None
        st.rerun()
