
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

if not os.path.exists(CAMINHO_LEITOS):
    pd.DataFrame(columns=CAMPOS).to_excel(CAMINHO_LEITOS, index=False)

if not os.path.exists(CAMINHO_MEDICOS):
    pd.DataFrame(columns=["Nome do Médico"]).to_excel(CAMINHO_MEDICOS, index=False)

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
    nome_sel = paciente_sel["nome"].values[0] if not paciente_sel.empty else ""
    medico_sel = paciente_sel["medico"].values[0] if not paciente_sel.empty else ""

    st.title(f"✏️ Cadastro – Leito {leito_sel} – {unidade_sel} – {andar_sel}")
    nome = st.text_input("Nome do paciente", value=nome_sel, key=f"nome_{selected_chave}")
    if lista_medicos:
        medico = st.selectbox("Médico responsável", options=lista_medicos,
                              index=lista_medicos.index(medico_sel) if medico_sel in lista_medicos else 0,
                              key=f"medico_{selected_chave}")
    else:
        medico = st.text_input("Médico responsável", value=medico_sel, key=f"medico_text_{selected_chave}")

    if st.button("Salvar cadastro", key=f"salvar_cadastro_{selected_chave}"):
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
        st.success("Cadastro salvo com sucesso.")
        st.session_state.unidade_selecionada = unidade_sel
        st.session_state.andar_selecionado = andar_sel
        del st.session_state["editando"]
        del st.session_state["modo"]
        st.rerun()

elif "editando" in st.session_state and st.session_state.get("modo") == "ficha":
    selected_chave = st.session_state["editando"]
    paciente_sel = df_leitos[df_leitos["chave"] == selected_chave]
    def valor(c): return paciente_sel[c].values[0] if not paciente_sel.empty and c in paciente_sel else ""
    st.title(f"📝 Ficha Clínica – {valor('nome')}")

    especialidade = st.selectbox("Especialidade médica", ["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Obstetrícia", "Pediatria", "Médico Assistente"], index=["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Obstetrícia", "Pediatria", "Médico Assistente"].index(valor("especialidade") if str(valor("especialidade")) != "nan" else "") if valor("especialidade") if str(valor("especialidade")) != "nan" else "" in ["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Obstetrícia", "Pediatria", "Médico Assistente"] else 0)
    risco = st.selectbox("Risco assistencial", ["", "Baixo", "Moderado", "Alto"], index=["", "Baixo", "Moderado", "Alto"].index(valor("risco") if str(valor("risco")) != "nan" else "") if valor("risco") if str(valor("risco")) != "nan" else "" in ["", "Baixo", "Moderado", "Alto"] else 0)
    operadora = st.selectbox("Operadora", ["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"], index=["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"].index(valor("operadora") if str(valor("operadora")) != "nan" else "") if valor("operadora") if str(valor("operadora")) != "nan" else "" in ["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"] else 0)
    pendencia = st.text_area("Pendência da rotina", value=valor("pendencia") if str(valor("pendencia")) != "nan" else "")
    paliativo = st.radio("Cuidados paliativos?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(valor("paliativo") if str(valor("paliativo")) != "nan" else "") if valor("paliativo") if str(valor("paliativo")) != "nan" else "" in ["", "Sim", "Não"] else 0, horizontal=True)
    cirurgia = st.radio("Cirurgia programada?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(valor("cirurgia") if str(valor("cirurgia")) != "nan" else "") if valor("cirurgia") if str(valor("cirurgia")) != "nan" else "" in ["", "Sim", "Não"] else 0, horizontal=True)
    desospitalizacao = st.radio("Em desospitalização?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(valor("desospitalizacao") if str(valor("desospitalizacao")) != "nan" else "") if valor("desospitalizacao") if str(valor("desospitalizacao")) != "nan" else "" in ["", "Sim", "Não"] else 0, horizontal=True)
    alta_amanha = st.radio("Alta prevista para amanhã?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(valor("alta_amanha") if str(valor("alta_amanha")) != "nan" else "") if valor("alta_amanha") if str(valor("alta_amanha")) != "nan" else "" in ["", "Sim", "Não"] else 0, horizontal=True)
    intercorrencia = st.selectbox("Intercorrência", ["", "Nenhuma", "Verde", "Amarela", "Laranja", "Azul", "Outro"], index=["", "Nenhuma", "Verde", "Amarela", "Laranja", "Azul", "Outro"].index(valor("intercorrencia") if str(valor("intercorrencia")) != "nan" else "") if valor("intercorrencia") if str(valor("intercorrencia")) != "nan" else "" in ["", "Nenhuma", "Verde", "Amarela", "Laranja", "Azul", "Outro"] else 0)
    desc_intercorrencia = st.text_area("Descrição da intercorrência", value=valor("desc_intercorrencia") if str(valor("desc_intercorrencia")) != "nan" else "")
    reavaliacao = st.radio("Reavaliação necessária?", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(valor("reavaliacao") if str(valor("reavaliacao")) != "nan" else "") if valor("reavaliacao") if str(valor("reavaliacao")) != "nan" else "" in ["", "Sim", "Não"] else 0, horizontal=True)
    observacoes = st.text_area("Observações gerais", value=valor("observacoes") if str(valor("observacoes")) != "nan" else "")

    if st.button("Salvar ficha clínica", key=f"salvar_ficha_{selected_chave}"):
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
        st.success("Ficha clínica salva.")
        st.session_state.unidade_selecionada = valor("unidade") if str(valor("unidade")) != "nan" else ""
        st.session_state.andar_selecionado = valor("andar") if str(valor("andar")) != "nan" else ""
        del st.session_state["editando"]
        del st.session_state["modo"]
        st.rerun()

else:
    st.title("📋 Painel de Leitos")

    if "unidade_selecionada" not in st.session_state or st.session_state.unidade_selecionada not in estrutura_leitos:
        st.session_state.unidade_selecionada = list(estrutura_leitos.keys())[0]

    if "andar_selecionado" not in st.session_state or st.session_state.andar_selecionado not in estrutura_leitos[st.session_state.unidade_selecionada]:
        st.session_state.andar_selecionado = list(estrutura_leitos[st.session_state.unidade_selecionada].keys())[0]

    unidade = st.selectbox("Unidade", list(estrutura_leitos.keys()), index=list(estrutura_leitos.keys()).index(st.session_state.unidade_selecionada))
    if st.session_state.andar_selecionado not in estrutura_leitos[unidade]:
        st.session_state.andar_selecionado = list(estrutura_leitos[unidade].keys())[0]
    andar = st.selectbox("Andar", list(estrutura_leitos[unidade].keys()), index=list(estrutura_leitos[unidade].keys()).index(st.session_state.andar_selecionado))

    st.session_state.unidade_selecionada = unidade
    st.session_state.andar_selecionado = andar
    leitos = sorted(estrutura_leitos[unidade][andar])

    for leito in leitos:
        chave = f"{unidade}_{andar}_{leito}"
        paciente = df_leitos[df_leitos["chave"] == chave]
        nome = paciente["nome"].values[0] if not paciente.empty else "[Vazio]"

        st.markdown(f"**Leito {leito}**")
        col1, col2 = st.columns([5, 1])
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
