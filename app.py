import streamlit as st
import pandas as pd
from datetime import date
from firebase_utils import salvar_leito, obter_leitos, salvar_medico, obter_medicos, salvar_admissao, obter_admissoes, salvar_historico_admissao, obter_historico_admissoes

# Carregamento único de df_leitos para uso global em todas as abas
COLUNAS_LEITOS = [
    'leito', 'nome', 'medico', 'equipe', 'especialidade', 'risco_assistencial', 'operadora',
    'pendencia_rotina', 'descricao_pendencia', 'cuidados_paliativos', 'autorizacao_pendente',
    'desospitalizacao', 'alta_amanha', 'intercorrencia_24h', 'desc_intercorrencia',
    'reavaliacao_medica', 'observacoes_gerais'
]

st.set_page_config(page_title="Gestão de Leitos", layout="wide")

# --- Cache otimizado para leitos ---
@st.cache_data(ttl=60)
def get_leitos_cached():
    dados = obter_leitos()
    df = pd.DataFrame(dados)
    if df.empty:
        df = pd.DataFrame(columns=COLUNAS_LEITOS)
    return df

df_leitos = get_leitos_cached()

# Garantir que todas as colunas essenciais existam no DataFrame
essential_columns = [
    'leito', 'nome', 'medico', 'equipe', 'especialidade', 'risco_assistencial', 'operadora',
    'pendencia_rotina', 'descricao_pendencia', 'cuidados_paliativos', 'autorizacao_pendente',
    'desospitalizacao', 'alta_amanha', 'intercorrencia_24h', 'desc_intercorrencia',
    'reavaliacao_medica', 'observacoes_gerais'
]
for col in essential_columns:
    if col not in df_leitos.columns:
        df_leitos[col] = ""

# (Restante do código original do app.py aqui)

# Exemplo de função alterada para salvar só o leito editado (ficha clínica)
def ficha_clinica_form(info_leito, leito, df_leitos, caminho_leitos, key_prefix="ficha"):
    # ... (seu código original até o salvamento)
    risco = info_leito['risco_assistencial'].values[0] if 'risco_assistencial' in df_leitos.columns and not info_leito.empty else ""
    operadora = info_leito['operadora'].values[0] if 'operadora' in df_leitos.columns and not info_leito.empty else ""
    pendencia_rotina = info_leito['pendencia_rotina'].values[0] if 'pendencia_rotina' in df_leitos.columns and not info_leito.empty else ""
    descricao_pendencia = info_leito['descricao_pendencia'].values[0] if 'descricao_pendencia' in df_leitos.columns and not info_leito.empty else ""
    pendencia_resolvida = info_leito['pendencia_resolvida'].values[0] if 'pendencia_resolvida' in df_leitos.columns and not info_leito.empty else "Não"
    paliativo = info_leito['cuidados_paliativos'].values[0] if 'cuidados_paliativos' in df_leitos.columns and not info_leito.empty else ""
    autorizacao = info_leito['autorizacao_pendente'].values[0] if 'autorizacao_pendente' in df_leitos.columns and not info_leito.empty else ""
    desospitalizacao = info_leito['desospitalizacao'].values[0] if 'desospitalizacao' in df_leitos.columns and not info_leito.empty else ""
    alta_amanha = info_leito['alta_amanha'].values[0] if 'alta_amanha' in df_leitos.columns and not info_leito.empty else ""
    intercorrencia = info_leito['intercorrencia_24h'].values[0] if 'intercorrencia_24h' in df_leitos.columns and not info_leito.empty else ""
    desc_intercorrencia = info_leito['desc_intercorrencia'].values[0] if 'desc_intercorrencia' in df_leitos.columns and not info_leito.empty else ""
    reavaliacao = info_leito['reavaliacao_medica'].values[0] if 'reavaliacao_medica' in df_leitos.columns and not info_leito.empty else ""
    obs_gerais = info_leito['observacoes_gerais'].values[0] if 'observacoes_gerais' in df_leitos.columns and not info_leito.empty else ""
    resposta_aut = info_leito['resposta_aut'].values[0] if 'resposta_aut' in df_leitos.columns and not info_leito.empty else ""
    detalhe_aut = info_leito['detalhe_aut'].values[0] if 'detalhe_aut' in df_leitos.columns and not info_leito.empty else ""

    # ... (código de formulário)

    alterou_ficha = (
        novo_risco != risco or
        nova_operadora != operadora or
        novo_paliativo != paliativo or
        nova_autorizacao != autorizacao or
        nova_resposta_aut != resposta_aut or
        novo_detalhe_aut != detalhe_aut or
        nova_desospitalizacao != desospitalizacao or
        nova_alta_amanha != alta_amanha or
        nova_intercorrencia != intercorrencia or
        nova_desc_intercorrencia != desc_intercorrencia or
        novas_obs_gerais != obs_gerais or
        nova_pendencia_rotina != pendencia_rotina or
        nova_descricao_pendencia != descricao_pendencia
    )
    if alterou_ficha:
        df_leitos.loc[df_leitos['leito'] == leito, 'risco_assistencial'] = novo_risco
        df_leitos.loc[df_leitos['leito'] == leito, 'operadora'] = nova_operadora
        df_leitos.loc[df_leitos['leito'] == leito, 'cuidados_paliativos'] = novo_paliativo
        df_leitos.loc[df_leitos['leito'] == leito, 'autorizacao_pendente'] = nova_autorizacao
        df_leitos.loc[df_leitos['leito'] == leito, 'resposta_aut'] = nova_resposta_aut
        df_leitos.loc[df_leitos['leito'] == leito, 'detalhe_aut'] = novo_detalhe_aut
        df_leitos.loc[df_leitos['leito'] == leito, 'desospitalizacao'] = nova_desospitalizacao
        df_leitos.loc[df_leitos['leito'] == leito, 'alta_amanha'] = nova_alta_amanha
        df_leitos.loc[df_leitos['leito'] == leito, 'intercorrencia_24h'] = nova_intercorrencia
        df_leitos.loc[df_leitos['leito'] == leito, 'desc_intercorrencia'] = nova_desc_intercorrencia
        df_leitos.loc[df_leitos['leito'] == leito, 'observacoes_gerais'] = novas_obs_gerais
        df_leitos.loc[df_leitos['leito'] == leito, 'pendencia_rotina'] = nova_pendencia_rotina
        # Mantém o status da pendência se já existe, senão inicializa como 'Não'
        if 'pendencia_resolvida' not in df_leitos.columns or pd.isna(df_leitos.loc[df_leitos['leito'] == leito, 'pendencia_resolvida']).all():
            df_leitos.loc[df_leitos['leito'] == leito, 'pendencia_resolvida'] = 'Não'
        # Salva apenas o leito alterado
        dados_salvar = df_leitos[df_leitos['leito'] == leito].iloc[0].to_dict()
        salvar_leito(leito, dados_salvar)
        st.cache_data.clear()
        st.success("Ficha clínica salva!")
