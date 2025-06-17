import streamlit as st
from firebase_utils import obter_leitos, obter_ficha_clinica, salvar_ficha_clinica

st.set_page_config(page_title="Ficha Clínica", layout="wide")
st.header("Ficha Clínica do Paciente")

# Função para listar leitos disponíveis
@st.cache_data(ttl=30)
def get_leitos_lista():
    leitos = obter_leitos()
    return sorted(leitos, key=lambda x: x.get("leito", ""))

leitos_lista = get_leitos_lista()
leitos_nomes = [f"{l['leito']} | {l.get('nome', '')}" for l in leitos_lista]
leito_idx = st.selectbox("Selecione o leito/paciente para editar ficha clínica", options=range(len(leitos_nomes)), format_func=lambda i: leitos_nomes[i] if leitos_nomes else "")

leito_sel = leitos_lista[leito_idx]
leito_id = leito_sel["leito"]

# Carrega a ficha clínica existente, se houver
ficha = obter_ficha_clinica(leito_id)

st.markdown("### Dados da Ficha Clínica")

with st.form("ficha_clinica"):
    # 1. Diagnóstico principal
    diagnostico = st.text_area("Diagnóstico principal", value=ficha.get("diagnostico", ""))
    # 2. Problemas atuais
    problemas_atuais = st.text_area("Problemas atuais", value=ficha.get("problemas_atuais", ""))
    # 3. Escalas (preencha apenas as que usar)
    col1, col2, col3 = st.columns(3)
    braden = col1.text_input("Braden", value=ficha.get("braden", ""))
    morse = col2.text_input("Morse", value=ficha.get("morse", ""))
    fugulin = col3.text_input("Fugulin", value=ficha.get("fugulin", ""))
    mrc = col1.text_input("MRC", value=ficha.get("mrc", ""))
    triagem_alta = col2.text_input("Triagem de Alta", value=ficha.get("triagem_alta", ""))
    asg = col3.text_input("ASG", value=ficha.get("asg", ""))
    charlson = col1.text_input("Índice de Charlson", value=ficha.get("charlson", ""))
    # 4. Comorbidades
    comorbidades = st.text_area("Comorbidades", value=ficha.get("comorbidades", ""))
    # 5. Tratamentos em uso
    tratamentos = st.text_area("Tratamentos em uso", value=ficha.get("tratamentos", ""))
    # 6. Culturas/Exames
    culturas = st.text_area("Culturas/Exames", value=ficha.get("culturas", ""))
    # 7. Resultados de exames
    resultados = st.text_area("Resultados de exames", value=ficha.get("resultados", ""))
    # 8. Pareceres
    pareceres = st.text_area("Pareceres", value=ficha.get("pareceres", ""))
    # 9. Prescrição atual
    prescricao = st.text_area("Prescrição atual", value=ficha.get("prescricao", ""))
    # 10. Observações gerais
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
