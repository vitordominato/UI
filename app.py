
import streamlit as st
import pandas as pd
from datetime import datetime
import os

CAMINHO_LEITOS = "base_leitos.xlsx"
CAMINHO_MEDICOS = "Cadastro_Medicos.xlsx"
CAMPOS = [
    "chave", "nome", "medico", "registrado_em", "leito", "unidade", "andar",
    "especialidade", "risco", "operadora", "pendencia", "paliativo", "cirurgia",
    "desospitalizacao", "alta_amanha", "intercorrencia", "desc_intercorrencia",
    "reavaliacao", "observacoes"
]

# Inicializa arquivos
for path, cols in [(CAMINHO_LEITOS, CAMPOS), (CAMINHO_MEDICOS, ["Nome do Médico"])]:
    if not os.path.exists(path):
        pd.DataFrame(columns=cols).to_excel(path, index=False)

df_leitos = pd.read_excel(CAMINHO_LEITOS)
df_medicos = pd.read_excel(CAMINHO_MEDICOS)
lista_medicos = sorted(df_medicos["Nome do Médico"].dropna().unique().tolist())

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

st.set_page_config(layout="wide")
st.title("📋 Painel de Leitos")

unidade = st.selectbox("Unidade", list(estrutura_leitos.keys()))
andar = st.selectbox("Andar", list(estrutura_leitos[unidade].keys()))
leitos = estrutura_leitos[unidade][andar]
colunas = st.columns(6)

selected_chave = st.session_state.get("editando")

# Edição no topo
if selected_chave:
    unidade_sel, andar_sel, leito_sel = selected_chave.split("_")
    leito_sel = int(leito_sel)
    st.markdown(f"### ✏️ Editando Leito {leito_sel} - {unidade_sel} - {andar_sel}")
    paciente_sel = df_leitos[df_leitos["chave"] == selected_chave]
    nome_sel = paciente_sel["nome"].values[0] if not paciente_sel.empty else ""
    medico_sel = paciente_sel["medico"].values[0] if not paciente_sel.empty else ""
    nome = st.text_input("Nome do paciente", value=nome_sel, key=f"nome_{selected_chave}")
    if lista_medicos:
        medico = st.selectbox("Médico responsável", options=lista_medicos,
                              index=lista_medicos.index(medico_sel) if medico_sel in lista_medicos else 0,
                              key=f"medico_{selected_chave}")
    else:
        medico = st.text_input("Médico responsável", value=medico_sel, key=f"medico_text_{selected_chave}")

    if st.button("Salvar cadastro inicial", key=f"salvar_{selected_chave}"):
        df_leitos = df_leitos[df_leitos["chave"] != selected_chave]
        novo = pd.DataFrame([{
            "chave": selected_chave,
            "nome": nome,
            "medico": medico,
            "registrado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "leito": leito_sel,
            "unidade": unidade_sel,
            "andar": andar_sel
        }])
        df_leitos = pd.concat([df_leitos, novo], ignore_index=True)
        df_leitos.to_excel(CAMINHO_LEITOS, index=False)
        st.success("Leito atualizado com sucesso.")
        st.rerun()

    st.markdown("### 📋 Ficha Clínica Assistencial")
    especialidade = st.selectbox("Especialidade médica", ["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Médico Assistente"], key=f"esp_{selected_chave}")
    risco = st.selectbox("Risco assistencial", ["", "Baixo", "Moderado", "Alto"], key=f"risco_{selected_chave}")
    operadora = st.selectbox("Operadora", ["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"], key=f"op_{selected_chave}")
    pendencia = st.text_area("Pendência da rotina", key=f"pend_{selected_chave}")
    paliativo = st.radio("Cuidados paliativos?", ["", "Sim", "Não"], horizontal=True, key=f"palia_{selected_chave}")
    cirurgia = st.radio("Cirurgia programada?", ["", "Sim", "Não"], horizontal=True, key=f"cir_{selected_chave}")
    desospitalizacao = st.radio("Em desospitalização?", ["", "Sim", "Não"], horizontal=True, key=f"deso_{selected_chave}")
    alta_amanha = st.radio("Alta prevista para amanhã?", ["", "Sim", "Não"], horizontal=True, key=f"alta_{selected_chave}")
    intercorrencia = st.selectbox("Intercorrência", ["", "Nenhuma", "Verde", "Amarela", "Laranja", "Azul", "Outro"], key=f"inter_{selected_chave}")
    desc_intercorrencia = st.text_area("Descrição da intercorrência", key=f"desc_{selected_chave}")
    reavaliacao = st.radio("Reavaliação necessária?", ["", "Sim", "Não"], horizontal=True, key=f"reavalia_{selected_chave}")
    observacoes = st.text_area("Observações gerais", key=f"obs_{selected_chave}")

    if st.button("Salvar ficha clínica", key=f"ficha_{selected_chave}"):
        df_leitos.loc[df_leitos["chave"] == selected_chave, [
            "especialidade", "risco", "operadora", "pendencia", "paliativo",
            "cirurgia", "desospitalizacao", "alta_amanha", "intercorrencia",
            "desc_intercorrencia", "reavaliacao", "observacoes"
        ]] = [
            especialidade, risco, operadora, pendencia, paliativo,
            cirurgia, desospitalizacao, alta_amanha, intercorrencia,
            desc_intercorrencia, reavaliacao, observacoes
        ]
        df_leitos.to_excel(CAMINHO_LEITOS, index=False)
        st.success("Ficha clínica salva com sucesso.")
        del st.session_state["editando"]
        st.rerun()

# Exibição dos leitos
for i, leito in enumerate(leitos):
    chave = f"{unidade}_{andar}_{leito}"
    paciente = df_leitos[df_leitos["chave"] == chave]
    nome = paciente["nome"].values[0] if not paciente.empty else "[Vazio]"

    with colunas[i % 6]:
        st.markdown(f"**Leito {leito}**")
        if st.button(f"✏️ {nome}", key=f"btn_{chave}"):
            st.session_state["editando"] = chave
            st.rerun()
