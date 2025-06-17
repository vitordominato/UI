import streamlit as st
import pandas as pd
from firebase_utils import (
    obter_leitos, salvar_leito, limpar_leito, salvar_ficha_clinica, obter_ficha_clinica
)

# ---- Funções auxiliares, copie igual do seu app.py original ----

def garantir_colunas(df):
    colunas = [
        'leito', 'nome', 'medico', 'equipe', 'especialidade', 'unidade', 'andar',
        'risco_assistencial', 'operadora', 'pendencia_rotina', 'descricao_pendencia',
        'cuidados_paliativos', 'autorizacao_pendente', 'desospitalizacao', 'alta_amanha',
        'intercorrencia_24h', 'desc_intercorrencia', 'reavaliacao_medica', 'observacoes_gerais'
    ]
    for col in colunas:
        if col not in df.columns:
            df[col] = ""
    return df

def ficha_clinica_form(info_leito, leito_id, key_prefix="ficha"):
    ficha = obter_ficha_clinica(leito_id)
    if ficha is None:
        ficha = {}

    with st.form(f"ficha_clinica_{key_prefix}_{leito_id}"):
        col1, col2 = st.columns(2)
        diagnostico = col1.text_input("Diagnóstico principal", value=ficha.get("diagnostico", ""))
        problemas_atuais = col2.text_area("Problemas atuais", value=ficha.get("problemas_atuais", ""))
        braden = col1.text_input("Braden", value=ficha.get("braden", ""))
        morse = col2.text_input("Morse", value=ficha.get("morse", ""))
        fugulin = col1.text_input("Fugulin", value=ficha.get("fugulin", ""))
        mrc = col2.text_input("MRC", value=ficha.get("mrc", ""))
        triagem_alta = col1.text_input("Triagem de Alta", value=ficha.get("triagem_alta", ""))
        asg = col2.text_input("ASG", value=ficha.get("asg", ""))
        charlson = col1.text_input("Índice de Charlson", value=ficha.get("charlson", ""))
        comorbidades = col2.text_area("Comorbidades", value=ficha.get("comorbidades", ""))
        tratamentos = st.text_area("Tratamentos em uso", value=ficha.get("tratamentos", ""))
        culturas = st.text_area("Culturas/Exames", value=ficha.get("culturas", ""))
        resultados = st.text_area("Resultados de exames", value=ficha.get("resultados", ""))
        pareceres = st.text_area("Pareceres", value=ficha.get("pareceres", ""))
        prescricao = st.text_area("Prescrição atual", value=ficha.get("prescricao", ""))
        observacoes = st.text_area("Observações gerais", value=ficha.get("observacoes", ""))

        submitted = st.form_submit_button("Salvar ficha clínica")
        if submitted:
            ficha_dict = {
                "diagnostico": diagnostico,
                "problemas_atuais": problemas_atuais,
                "braden": braden,
                "morse": morse,
                "fugulin": fugulin,
                "mrc": mrc,
                "triagem_alta": triagem_alta,
                "asg": asg,
                "charlson": charlson,
                "comorbidades": comorbidades,
                "tratamentos": tratamentos,
                "culturas": culturas,
                "resultados": resultados,
                "pareceres": pareceres,
                "prescricao": prescricao,
                "observacoes": observacoes,
            }
            salvar_ficha_clinica(leito_id, ficha_dict)
            st.success("Ficha clínica salva com sucesso!")

# ----------------------------------------------------------------

st.set_page_config(page_title="Painel de Leitos", layout="wide")
st.header("Painel de Leitos Hospitalares")

@st.cache_data(ttl=30)
def get_leitos_cached():
    dados = obter_leitos()
    df = pd.DataFrame(dados)
    if df.empty:
        df = pd.DataFrame(columns=[
            'leito', 'nome', 'medico', 'equipe', 'especialidade', 'unidade', 'andar'
        ])
    return df

df_leitos = garantir_colunas(get_leitos_cached())

if st.button("🔄 Atualizar dados"):
    st.cache_data.clear()

for idx, leito in df_leitos.iterrows():
    with st.expander(f"Leito {leito['leito']} | {leito.get('nome','')}", expanded=False):
        col1, col2, col3 = st.columns(3)
        novo_nome = col1.text_input("Nome do paciente", value=leito.get('nome', ''), key=f"nome_{leito['leito']}")
        novo_medico = col2.text_input("Médico", value=leito.get('medico', ''), key=f"medico_{leito['leito']}")
        novo_equipe = col3.text_input("Equipe", value=leito.get('equipe', ''), key=f"equipe_{leito['leito']}")

        col4, col5 = st.columns(2)
        nova_especialidade = col4.text_input("Especialidade", value=leito.get('especialidade', ''), key=f"especialidade_{leito['leito']}")
        nova_unidade = col5.text_input("Unidade", value=leito.get('unidade', ''), key=f"unidade_{leito['leito']}")
        novo_andar = st.text_input("Andar", value=leito.get('andar', ''), key=f"andar_{leito['leito']}")

        leito_dict = {
            'leito': leito['leito'],
            'nome': novo_nome,
            'medico': novo_medico,
            'equipe': novo_equipe,
            'especialidade': nova_especialidade,
            'unidade': nova_unidade,
            'andar': novo_andar,
        }

        if st.button(f"Salvar alterações do leito {leito['leito']}", key=f"salvar_{leito['leito']}"):
            salvar_leito(leito['leito'], leito_dict)
            st.success("Alterações salvas! Outros usuários verão após atualizar a tela.")
            st.cache_data.clear()

        st.markdown("### Ficha Clínica")
        ficha_clinica_form(leito, leito['leito'], key_prefix=f"ficha_{leito['leito']}")
