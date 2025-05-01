
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

if "editando" in st.session_state and st.session_state.get("modo") == "cadastro":
    selected_chave = st.session_state["editando"]
    unidade_sel, andar_sel, leito_sel = selected_chave.split("_")
    leito_sel = int(leito_sel)
    paciente_sel = df_leitos[df_leitos["chave"] == selected_chave]

    def valor(col):
        return paciente_sel[col].values[0] if not paciente_sel.empty and col in paciente_sel else ""

    st.title(f"📝 Editar Leito {leito_sel} - {unidade_sel} - {andar_sel}")
    nome = st.text_input("Nome do paciente", value=valor("nome"), key=f"nome_{selected_chave}")
    if lista_medicos:
        medico = st.selectbox("Médico responsável", options=lista_medicos,
                              index=lista_medicos.index(valor("medico")) if valor("medico") in lista_medicos else 0,
                              key=f"medico_{selected_chave}")
    else:
        medico = st.text_input("Médico responsável", value=valor("medico"), key=f"medico_text_{selected_chave}")

    if st.button("Salvar cadastro inicial", key=f"salvar_{selected_chave}"):
        del st.session_state["editando"]
        del st.session_state["modo"]
        st.rerun()
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
    especialidade = st.selectbox("Especialidade médica", ["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Médico Assistente"], index=["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Médico Assistente"].index(valor("especialidade")) if valor("especialidade") in ["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Médico Assistente"] else 0, key=f"esp_{selected_chave}")
    risco = st.selectbox("Risco assistencial", ["", "Baixo", "Moderado", "Alto"], index=["", "Baixo", "Moderado", "Alto"].index(valor("risco")) if valor("risco") in ["", "Baixo", "Moderado", "Alto"] else 0, key=f"risco_{selected_chave}")
    operadora = st.selectbox("Operadora", ["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"], index=["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"].index(valor("operadora")) if valor("operadora") in ["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"] else 0, key=f"op_{selected_chave}")
    pendencia = st.text_area("Pendência da rotina", value=valor("pendencia"), key=f"pend_{selected_chave}")
    paliativo = st.radio("Cuidados paliativos?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(valor("paliativo")) if valor("paliativo") in ["", "Sim", "Não"] else 0, horizontal=True, key=f"palia_{selected_chave}")
    cirurgia = st.radio("Cirurgia programada?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(valor("cirurgia")) if valor("cirurgia") in ["", "Sim", "Não"] else 0, horizontal=True, key=f"cir_{selected_chave}")
    desospitalizacao = st.radio("Em desospitalização?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(valor("desospitalizacao")) if valor("desospitalizacao") in ["", "Sim", "Não"] else 0, horizontal=True, key=f"deso_{selected_chave}")
    alta_amanha = st.radio("Alta prevista para amanhã?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(valor("alta_amanha")) if valor("alta_amanha") in ["", "Sim", "Não"] else 0, horizontal=True, key=f"alta_{selected_chave}")
    intercorrencia = st.selectbox("Intercorrência", ["", "Nenhuma", "Verde", "Amarela", "Laranja", "Azul", "Outro"], index=["", "Nenhuma", "Verde", "Amarela", "Laranja", "Azul", "Outro"].index(valor("intercorrencia")) if valor("intercorrencia") in ["", "Nenhuma", "Verde", "Amarela", "Laranja", "Azul", "Outro"] else 0, key=f"inter_{selected_chave}")
    desc_intercorrencia = st.text_area("Descrição da intercorrência", value=valor("desc_intercorrencia"), key=f"desc_{selected_chave}")
    reavaliacao = st.radio("Reavaliação necessária?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(valor("reavaliacao")) if valor("reavaliacao") in ["", "Sim", "Não"] else 0, horizontal=True, key=f"reavalia_{selected_chave}")
    observacoes = st.text_area("Observações gerais", value=valor("observacoes"), key=f"obs_{selected_chave}")

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

if "editando" not in st.session_state:
    st.title("📋 Painel de Leitos")
    unidade = st.selectbox("Unidade", list(estrutura_leitos.keys()))
    andar = st.selectbox("Andar", list(estrutura_leitos[unidade].keys()))
    leitos = estrutura_leitos[unidade][andar]
    colunas = st.columns(6)

    
for i, leito in enumerate(leitos):
    chave = f"{unidade}_{andar}_{leito}"
    paciente = df_leitos[df_leitos["chave"] == chave]
    nome = paciente["nome"].values[0] if not paciente.empty else "[Vazio]"

    with colunas[i % 6]:
        st.markdown(f"**Leito {leito}**")
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(f"✏️ {nome}", key=f"cadastro_{chave}"):
                st.session_state["modo"] = "cadastro"
                st.session_state["editando"] = chave
                st.rerun()
        with col2:
            if not paciente.empty:
                if st.button("📝", key=f"ficha_{chave}"):
                    st.session_state["modo"] = "ficha"
                    st.session_state["editando"] = chave
                    st.rerun()

            st.markdown(f"**Leito {leito}**")
            if st.button(f"✏️ {nome}", key=f"cadastro_{chave}"):
                st.session_state["modo"] = "cadastro"
                st.session_state["modo"] = "ficha"
                st.session_state["editando"] = chave
                st.rerun()
                st.session_state["modo"] = "ficha"
                st.session_state["editando"] = chave
                st.rerun()



if "editando" in st.session_state and st.session_state.get("modo") == "ficha":
    selected_chave = st.session_state["editando"]
    df_leitos = pd.read_excel(CAMINHO_LEITOS)
    paciente_sel = df_leitos[df_leitos["chave"] == selected_chave]
    def valor(col): return paciente_sel[col].values[0] if not paciente_sel.empty and col in paciente_sel else ""
    st.title(f"📝 Ficha Clínica – {valor('nome')} – Leito {valor('leito')}")

    especialidade = st.selectbox("Especialidade médica", ["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Médico Assistente"], index=["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Médico Assistente"].index(valor("especialidade")) if valor("especialidade") in ["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Médico Assistente"] else 0, key=f"esp_{selected_chave}")
    risco = st.selectbox("Risco assistencial", ["", "Baixo", "Moderado", "Alto"], index=["", "Baixo", "Moderado", "Alto"].index(valor("risco")) if valor("risco") in ["", "Baixo", "Moderado", "Alto"] else 0, key=f"risco_{selected_chave}")
    operadora = st.selectbox("Operadora", ["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"], index=["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"].index(valor("operadora")) if valor("operadora") in ["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"] else 0, key=f"op_{selected_chave}")
    pendencia = st.text_area("Pendência da rotina", value=valor("pendencia"), key=f"pend_{selected_chave}")
    paliativo = st.radio("Cuidados paliativos?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(valor("paliativo")) if valor("paliativo") in ["", "Sim", "Não"] else 0, horizontal=True, key=f"palia_{selected_chave}")
    cirurgia = st.radio("Cirurgia programada?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(valor("cirurgia")) if valor("cirurgia") in ["", "Sim", "Não"] else 0, horizontal=True, key=f"cir_{selected_chave}")
    desospitalizacao = st.radio("Em desospitalização?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(valor("desospitalizacao")) if valor("desospitalizacao") in ["", "Sim", "Não"] else 0, horizontal=True, key=f"deso_{selected_chave}")
    alta_amanha = st.radio("Alta prevista para amanhã?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(valor("alta_amanha")) if valor("alta_amanha") in ["", "Sim", "Não"] else 0, horizontal=True, key=f"alta_{selected_chave}")
    intercorrencia = st.selectbox("Intercorrência", ["", "Nenhuma", "Verde", "Amarela", "Laranja", "Azul", "Outro"], index=["", "Nenhuma", "Verde", "Amarela", "Laranja", "Azul", "Outro"].index(valor("intercorrencia")) if valor("intercorrencia") in ["", "Nenhuma", "Verde", "Amarela", "Laranja", "Azul", "Outro"] else 0, key=f"inter_{selected_chave}")
    desc_intercorrencia = st.text_area("Descrição da intercorrência", value=valor("desc_intercorrencia"), key=f"desc_{selected_chave}")
    reavaliacao = st.radio("Reavaliação necessária?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(valor("reavaliacao")) if valor("reavaliacao") in ["", "Sim", "Não"] else 0, horizontal=True, key=f"reavalia_{selected_chave}")
    observacoes = st.text_area("Observações gerais", value=valor("observacoes"), key=f"obs_{selected_chave}")

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
        del st.session_state["modo"]
        st.rerun()
