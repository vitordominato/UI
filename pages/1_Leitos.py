import streamlit as st
import pandas as pd
from firebase_utils import salvar_leito, obter_leitos, salvar_ficha_clinica, obter_ficha_clinica

# Colunas essenciais do leito (não mude!)
COLUNAS_LEITOS = [
    'leito', 'nome', 'medico', 'equipe', 'especialidade', 'unidade', 'andar',
    'risco_assistencial', 'operadora', 'pendencia_rotina', 'descricao_pendencia',
    'cuidados_paliativos', 'autorizacao_pendente', 'desospitalizacao', 'alta_amanha',
    'intercorrencia_24h', 'desc_intercorrencia', 'reavaliacao_medica', 'observacoes_gerais'
]

st.set_page_config(page_title="Gestão de Leitos", layout="wide")

@st.cache_data(ttl=60)
def get_leitos_cached():
    dados = obter_leitos()
    df = pd.DataFrame(dados)
    if df.empty:
        df = pd.DataFrame(columns=COLUNAS_LEITOS)
    return df

def garantir_colunas(df):
    for col in COLUNAS_LEITOS:
        if col not in df.columns:
            df[col] = ""
    return df

def ficha_clinica_form(leito, leito_id, key_prefix="ficha"):
    ficha = obter_ficha_clinica(leito_id)
    ficha = ficha if ficha else {}
    risco = ficha.get('risco_assistencial', "")
    operadora = ficha.get('operadora', "")
    pendencia_rotina = ficha.get('pendencia_rotina', "")
    descricao_pendencia = ficha.get('descricao_pendencia', "")
    pendencia_resolvida = ficha.get('pendencia_resolvida', "Não")
    paliativo = ficha.get('cuidados_paliativos', "")
    autorizacao = ficha.get('autorizacao_pendente', "")
    desospitalizacao = ficha.get('desospitalizacao', "")
    alta_amanha = ficha.get('alta_amanha', "")
    intercorrencia = ficha.get('intercorrencia_24h', "")
    desc_intercorrencia = ficha.get('desc_intercorrencia', "")
    reavaliacao = ficha.get('reavaliacao_medica', "")
    obs_gerais = ficha.get('observacoes_gerais', "")
    resposta_aut = ficha.get('resposta_aut', "")
    detalhe_aut = ficha.get('detalhe_aut', "")

    col_campos = st.columns(5)
    with col_campos[0]:
        st.markdown("Operadora")
        nova_operadora = st.selectbox("", ["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"], index=["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"].index(operadora) if operadora in ["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"] else 0, key=f"{key_prefix}_operadora_{leito_id}")
    with col_campos[1]:
        st.markdown("Risco assistencial")
        novo_risco = st.selectbox("", ["", "Baixo", "Moderado", "Alto"], index=["", "Baixo", "Moderado", "Alto"].index(risco) if risco in ["", "Baixo", "Moderado", "Alto"] else 0, key=f"{key_prefix}_risco_{leito_id}")
    with col_campos[2]:
        st.markdown("Cuidados paliativos?")
        novo_paliativo = st.selectbox("", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(paliativo) if paliativo in ["", "Sim", "Não"] else 0, key=f"{key_prefix}_paliativo_{leito_id}")
    with col_campos[3]:
        st.markdown("Desospitalização?")
        nova_desospitalizacao = st.selectbox("", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(desospitalizacao) if desospitalizacao in ["", "Sim", "Não"] else 0, key=f"{key_prefix}_desospitalizacao_{leito_id}")
    with col_campos[4]:
        st.markdown("Alta prevista para amanhã?")
        nova_alta_amanha = st.selectbox("", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(alta_amanha) if alta_amanha in ["", "Sim", "Não"] else 0, key=f"{key_prefix}_alta_amanha_{leito_id}")

    st.markdown("---")
    nova_pendencia_rotina = st.selectbox("Pendência do dia", ["nenhuma", "rotina tarde", "plantão noturno"], index=["nenhuma", "rotina tarde", "plantão noturno"].index(pendencia_rotina) if pendencia_rotina in ["nenhuma", "rotina tarde", "plantão noturno"] else 0, key=f"{key_prefix}_pendencia_rotina_{leito_id}")
    nova_descricao_pendencia = st.text_input("Descrição da pendência", value=descricao_pendencia, key=f"{key_prefix}_descricao_pendencia_{leito_id}")

    nova_intercorrencia = st.selectbox("Intercorrência nas últimas 24h?", ["", "Não", "Verde", "Laranja", "Amarela", "Azul", "Outras"], index=["", "Não", "Verde", "Laranja", "Amarela", "Azul", "Outras"].index(intercorrencia) if intercorrencia in ["", "Não", "Verde", "Laranja", "Amarela", "Azul", "Outras"] else 0, key=f"{key_prefix}_intercorrencia_{leito_id}")
    nova_desc_intercorrencia = st.text_area("Descrição da intercorrência", value=desc_intercorrencia, key=f"{key_prefix}_desc_intercorrencia_{leito_id}")
    novas_obs_gerais = st.text_area("Observações gerais", value=obs_gerais, key=f"{key_prefix}_obs_gerais_{leito_id}")

    alterou_ficha = (
        novo_risco != risco or
        nova_operadora != operadora or
        novo_paliativo != paliativo or
        nova_desospitalizacao != desospitalizacao or
        nova_alta_amanha != alta_amanha or
        nova_intercorrencia != intercorrencia or
        nova_desc_intercorrencia != desc_intercorrencia or
        novas_obs_gerais != obs_gerais or
        nova_pendencia_rotina != pendencia_rotina or
        nova_descricao_pendencia != descricao_pendencia
    )
    if alterou_ficha:
        ficha_dict = {
            'risco_assistencial': novo_risco,
            'operadora': nova_operadora,
            'cuidados_paliativos': novo_paliativo,
            'desospitalizacao': nova_desospitalizacao,
            'alta_amanha': nova_alta_amanha,
            'intercorrencia_24h': nova_intercorrencia,
            'desc_intercorrencia': nova_desc_intercorrencia,
            'observacoes_gerais': novas_obs_gerais,
            'pendencia_rotina': nova_pendencia_rotina,
            'descricao_pendencia': nova_descricao_pendencia
        }
        salvar_ficha_clinica(leito_id, ficha_dict)
        st.success("Ficha clínica salva!")

st.header("Painel de Leitos")
df_leitos = garantir_colunas(get_leitos_cached())
df_leitos = df_leitos.sort_values(by=["leito"]).reset_index(drop=True)

for idx, leito in df_leitos.iterrows():
    with st.container():
        cols = st.columns([1, 3, 3, 2])
        cols[0].markdown(f"**Leito {leito['leito']}**")
        novo_nome = cols[1].text_input("Nome do paciente", value=leito.get("nome", ""), key=f"edit_nome_{leito['leito']}")
        novo_medico = cols[2].text_input("Médico", value=leito.get("medico", ""), key=f"edit_medico_{leito['leito']}")
        novo_equipe = cols[3].text_input("Equipe", value=leito.get("equipe", ""), key=f"edit_equipe_{leito['leito']}")
        # Salvamento manual simples
        if st.button(f"Salvar alterações do leito {leito['leito']}", key=f"salvar_{leito['leito']}"):
            leito_dict = leito.to_dict()
            leito_dict.update({
                "nome": novo_nome,
                "medico": novo_medico,
                "equipe": novo_equipe
            })
            salvar_leito(leito['leito'], leito_dict)
            st.success("Alterações salvas!")
        with st.expander("Ficha Clínica", expanded=False):
            ficha_clinica_form(leito, leito['leito'], key_prefix=f"painel_{leito['leito']}")
        st.markdown("---")
