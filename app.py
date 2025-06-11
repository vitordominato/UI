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
import streamlit as st
import pandas as pd
from datetime import date
from firebase_utils import salvar_leito, obter_leitos, salvar_medico, obter_medicos, salvar_admissao, obter_admissoes, salvar_historico_admissao, obter_historico_admissoes

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

# --- Função utilitária para reconstruir o dicionário do leito a partir dos widgets ---
def get_leito_dict_from_state(leito_id):
    dados = {}
    for col in essential_columns:
        dados[col] = st.session_state.get(f"{col}_{leito_id}", "")
    return dados

# --- Callback de salvamento automático ---
def salvar_leito_automatico(leito_id):
    dados = get_leito_dict_from_state(leito_id)
    salvar_leito(leito_id, dados)
    st.cache_data.clear()
    # st.experimental_rerun()  # Descomente se quiser atualizar a interface imediatamente

# --- Exemplo de painel de edição de leitos com salvamento automático ---
def painel_edicao_leito(leito):
    leito_id = leito['leito']
    cols = st.columns(len(essential_columns))
    for idx, col_name in enumerate(essential_columns):
        cols[idx].text_input(
            col_name.replace('_', ' ').capitalize(),
            value=leito.get(col_name, ""),
            key=f"{col_name}_{leito_id}",
            on_change=salvar_leito_automatico,
            args=(leito_id,)
        )

# --- Renderizar painel de edição para cada leito ---
if "Leitos" in menu:
    st.header("Painel de Leitos - Edição com Salvamento Automático")
    for idx, leito in df_leitos.iterrows():
        with st.expander(f"Leito {leito['leito']}"):
            painel_edicao_leito(leito)

# Backup automático removido: dados agora são exclusivamente no Firebase

# Menu lateral principal (bolinhas)
menu = [
    "Leitos", "Visão do Plantonista", "Pendência tarde", "Admissão", "Médicos", "Gestão", "Dashboard", "🧮 IRAH", "Rastreio e Vacinação"
]

aba_selecionada = st.sidebar.radio("Menu", menu, index=0)

st.markdown("""
    <style>
    div.stButton > button {
        background-color: #f0f0f0;
        color: #222;
    }
    div.stButton > button:has(span:contains('Realizado')) {
        background-color: #22c55e !important;
        color: white !important;
    }
    div.stButton > button:has(span:contains('Cancelado')) {
        background-color: #ef4444 !important;
        color: white !important;
    }
    div.stButton > button:has(span:contains('Desfazer')) {
        background-color: #facc15 !important;
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)

from datetime import datetime, date

# Função centralizada para exibir e editar a Ficha Clínica

def ficha_clinica_form(info_leito, leito, df_leitos, caminho_leitos, key_prefix="ficha"):
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

    col_campos = st.columns(5)
    with col_campos[0]:
        st.markdown("Operadora")
        nova_operadora = st.selectbox("", ["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"], index=["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"].index(operadora) if operadora in ["", "AMIL", "CABERJ", "MEDSENIOR", "UNIMED", "Bradesco", "Sul America", "Notre Dame/Intermedica", "Outros"] else 0, key=f"{key_prefix}_operadora_{leito}")
    with col_campos[1]:
        st.markdown("Risco assistencial")
        novo_risco = st.selectbox("", ["", "Baixo", "Moderado", "Alto"], index=["", "Baixo", "Moderado", "Alto"].index(risco) if risco in ["", "Baixo", "Moderado", "Alto"] else 0, key=f"{key_prefix}_risco_{leito}")
    with col_campos[2]:
        st.markdown("Cuidados paliativos?")
        novo_paliativo = st.selectbox("", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(paliativo) if paliativo in ["", "Sim", "Não"] else 0, key=f"{key_prefix}_paliativo_{leito}")
    with col_campos[3]:
        st.markdown("Desospitalização?")
        nova_desospitalizacao = st.selectbox("", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(desospitalizacao) if desospitalizacao in ["", "Sim", "Não"] else 0, key=f"{key_prefix}_desospitalizacao_{leito}")
    with col_campos[4]:
        st.markdown("Alta prevista para amanhã?")
        nova_alta_amanha = st.selectbox("", ["", "Sim", "Não"], index=["", "Sim", "Não"].index(alta_amanha) if alta_amanha in ["", "Sim", "Não"] else 0, key=f"{key_prefix}_alta_amanha_{leito}")

    col_autorizacao = st.columns([2, 2, 6])
    with col_autorizacao[0]:
        st.markdown("Autorização")
        nova_autorizacao = st.selectbox(
            "", ["", "Não", "Procedimento", "Medicação"],
            index=["", "Não", "Procedimento", "Medicação"].index(autorizacao) if autorizacao in ["", "Não", "Procedimento", "Medicação"] else 0,
            key=f"{key_prefix}_autorizacao_{leito}"
        )
    with col_autorizacao[1]:
        st.markdown("Resposta")
        nova_resposta_aut = st.selectbox(
            "", ["", "Autorizado", "Em análise"],
            index=["", "Autorizado", "Em análise"].index(resposta_aut) if resposta_aut in ["", "Autorizado", "Em análise"] else 0,
            key=f"{key_prefix}_resposta_aut_{leito}"
        )
    with col_autorizacao[2]:
        st.markdown("Detalhe")
        novo_detalhe_aut = st.text_input(
            "", value=detalhe_aut, key=f"{key_prefix}_detalhe_aut_{leito}"
        )

    # Pendência do dia (em linha)
    col_pendencia = st.columns([2, 6])
    with col_pendencia[0]:
        nova_pendencia_rotina = st.selectbox(
            "Pendência do dia",
            ["nenhuma", "rotina tarde", "plantão noturno"],
            index=["nenhuma", "rotina tarde", "plantão noturno"].index(pendencia_rotina) if pendencia_rotina in ["nenhuma", "rotina tarde", "plantão noturno"] else 0,
            key=f"{key_prefix}_pendencia_rotina_{leito}"
        )
    with col_pendencia[1]:
        nova_descricao_pendencia = st.text_input(
            "Descrição",
            value=descricao_pendencia,
            key=f"{key_prefix}_descricao_pendencia_{leito}"
        )
    # Sinalização visual da pendência
    if nova_pendencia_rotina != "nenhuma":
        cor = "green" if pendencia_resolvida == "Sim" else "red"
        texto = "Resolvida" if pendencia_resolvida == "Sim" else "Pendente"
        st.markdown(f"<span style='color:{cor}; font-weight:bold'>Status da Pendência: {texto}</span>", unsafe_allow_html=True)

    nova_intercorrencia = st.selectbox("Intercorrência nas últimas 24h?", ["", "Não", "Verde", "Laranja", "Amarela", "Azul", "Outras"], index=["", "Não", "Verde", "Laranja", "Amarela", "Azul", "Outras"].index(intercorrencia) if intercorrencia in ["", "Não", "Verde", "Laranja", "Amarela", "Azul", "Outras"] else 0, key=f"{key_prefix}_intercorrencia_{leito}")
    nova_desc_intercorrencia = st.text_area("Descrição da intercorrência", value=desc_intercorrencia, key=f"{key_prefix}_desc_intercorrencia_{leito}")
    novas_obs_gerais = st.text_area("Observações gerais", value=obs_gerais, key=f"{key_prefix}_obs_gerais_{leito}")

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
        for _, row in df_leitos.iterrows():
            salvar_leito(row['leito'], row.to_dict())
        st.cache_data.clear()
        st.success("Ficha clínica salva!")

    col1, col2, col3 = st.columns(3)
    if col1.button("🟩 Alta", key=f"{key_prefix}_alta_{leito}"):
        # Salva paciente em altas_hoje.csv antes de zerar
        ALTAS_HOJE_PATH = os.path.join('data', 'altas_hoje.csv')
        # ... (restante do código)

    if col2.button("Limpar leito", key=f"{key_prefix}_limpar_{leito}"):
        for campo in ['nome','medico','equipe','especialidade','risco_assistencial','operadora','pendencia_rotina','descricao_pendencia','cuidados_paliativos','autorizacao_pendente','desospitalizacao','alta_amanha','intercorrencia_24h','desc_intercorrencia','reavaliacao_medica','observacoes_gerais']:
            df_leitos.loc[df_leitos['leito'] == leito, campo] = ""
        df_leitos.loc[df_leitos['leito'] == leito, 'pendencia_resolvida'] = 'Não'
        for _, row in df_leitos.iterrows():
            salvar_leito(row['leito'], row.to_dict())
        st.cache_data.clear()
        st.success("Leito limpo! Cadastro do paciente e ficha clínica zerados.")
        st.experimental_rerun()
        st.success("Leito liberado por transferência!")


# Funções auxiliares e caminhos para admissões/admitidos
# Caminhos removidos, uso direto de Google Sheets
ADMISSOES_SHEET = 'admissoes'
ADMITIDOS_SHEET = 'admitidos'
HISTORICO_ADMISSOES_SHEET = 'historico_admissoes'
HISTORICO_AUTORIZACAO_SHEET = 'historico_autorizacao'
HISTORICO_DESOSP_SHEET = 'historico_desospitalizacao'

def registrar_historico_admissao(acao, nome_paciente, origem, observacoes, detalhes_adicionais=None):
    """
    Registra uma ação no histórico de admissões com data e hora.
    """
    data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    linha = {
        'data_hora': data_hora,
        'acao': acao,
        'nome_paciente': nome_paciente,
        'origem': origem,
        'observacoes': observacoes,
        'detalhes_adicionais': detalhes_adicionais or ''
    }
    try:
        df_hist = pd.DataFrame(obter_historico_admissoes())
        if df_hist.empty:
            df_hist = pd.DataFrame(columns=linha.keys())
        df_hist = pd.concat([df_hist, pd.DataFrame([linha])], ignore_index=True)
        salvar_historico_admissoes(df_hist)
    except Exception:
        pass

def carregar_admissoes():
    try:
        df = pd.DataFrame(obter_admissoes())
        if df.empty:
            df = pd.DataFrame(columns=["nome_paciente","origem","observacoes"])
        return df
    except Exception:
        return pd.DataFrame(columns=["nome_paciente","origem","observacoes"])
def carregar_admitidos():
    try:
        df = pd.DataFrame(obter_admitidos())
        if df.empty:
            df = pd.DataFrame(columns=["nome_paciente","origem","observacoes","data_admissao"])
        return df
    except Exception:
        return pd.DataFrame(columns=["nome_paciente","origem","observacoes","data_admissao"])
from firebase_utils import salvar_admissao
import uuid

import numpy as np

def salvar_admissoes(df):
    for _, row in df.iterrows():
        adm_id = row.get('admissao_id') or str(uuid.uuid4())
        dados = row.replace([np.nan, np.inf, -np.inf], '').to_dict()
        salvar_admissao(adm_id, dados)
from firebase_utils import salvar_admitido
import uuid

import numpy as np

def salvar_admitidos(df):
    import numpy as np
    print("DEBUG salvar_admitidos, df:", df)
    for _, row in df.iterrows():
        admitido_id = row.get('admitido_id') or str(uuid.uuid4())
        dados = row.replace([np.nan, np.inf, -np.inf], '').to_dict()
        print(f"Salvando admitido_id={admitido_id}, dados={dados}")
        salvar_admitido(admitido_id, dados)
    debug_print_admitidos_firebase()

def debug_print_admitidos_firebase():
    from firebase_utils import inicializar_firebase
    import firebase_utils
    inicializar_firebase()
    ref = firebase_utils.db.reference('admitidos')
    print("DEBUG Firebase admitidos:", ref.get())


# Diretórios e arquivos




# Colunas dos DataFrames
colunas_leitos = [
    "leito", "nome", "medico", "especialidade", "risco", "operadora",
    "pendencia_rotina", "exame", "reavaliacao", "descricao_pendencia", "paliativo", "cirurgia", "medicacao",
    "desospitalizacao", "alta_amanha", "intercorrencia", "cor_intercorrencia", "observacao"
]
colunas_medicos = ["Nome do Médico", "CRM", "Especialidade", "Equipe"]

# Layout responsivo: menu hambúrguer e filtros rápidos
# Estrutura dos andares por unidade
CONFIG_ANDARES = {
    "Unidade I": {
        "4º andar": (401, 432),
        "5º andar": (501, 535),
        "6º andar": (601, 637),
    },
    "Unidade III": {
        "4º andar (Unidade III)": (401, 404),
        "5º andar (Pediatria)": (501, 510),
        "6º andar (Pediatria)": (601, 610),
        "7º andar": (701, 710),
        "8º andar (Obstetrícia)": (801, 810),
        "9º andar (Obstetrícia)": (901, 910),
    },
    "Unidade IV": {
        "6º andar (TMO)": (601, 626),
        "7º andar (Cardiologia)": (701, 728),
        "8º andar (Unidade IV)": (801, 828),
        "9º andar (Unidade IV)": (901, 928),
    }
}

# Carregar dados dos médicos diretamente do Firebase
try:
    import pandas as pd
    df_medicos = pd.DataFrame(obter_medicos())
    if df_medicos.empty:
        df_medicos = pd.DataFrame(columns=colunas_medicos)
except Exception:
    df_medicos = pd.DataFrame(columns=colunas_medicos)
medicos_lista = df_medicos['Nome do Médico'].dropna().unique().tolist()

with st.sidebar:
    st.title("🏥 Gestão de Leitos")
    st.markdown("---")
    st.subheader("Filtros rápidos")
    unidade = st.selectbox("Unidade", list(CONFIG_ANDARES.keys()), key="unidade_filtro")
    andares_disponiveis = list(CONFIG_ANDARES[unidade].keys())
    andar = st.selectbox("Andar", andares_disponiveis, key="andar_filtro")
    # Dropdown de médicos cadastrados para filtro
    if len(medicos_lista) > 0:
        medico_filtro = st.selectbox("Filtrar por médico", ["(Todos)"] + medicos_lista, key="medico_filtro_select")
    else:
        medico_filtro = "(Todos)"
    st.markdown("---")



# --- IRAH: Cálculo do Índice de Risco Assistencial Hospitalar ---
if aba_selecionada == "🧮 IRAH":
    st.header("🧮 Índice de Risco Assistencial Hospitalar (IRAH)")
    st.markdown("Selecione o leito e preencha os campos abaixo para calcular e atualizar o risco assistencial.")
    # Carregar leitos
    try:
        import pandas as pd
        df_leitos = pd.DataFrame(obter_leitos())
        if df_leitos.empty:
            df_leitos = pd.DataFrame(columns=colunas_leitos)
    except Exception:
        df_leitos = pd.DataFrame(columns=colunas_leitos)
    leitos_disponiveis = df_leitos['leito'].unique().tolist()
    leito_sel = st.selectbox("Leito", leitos_disponiveis)
    # Campo de texto livre Atendimento
    atendimento = st.text_area("Atendimento", value="", key="atendimento_irah")
    info_leito = df_leitos[df_leitos['leito'] == leito_sel]
    # Entradas
    fugulin = st.number_input("Pontuação da Escala Fugulin", min_value=0, max_value=100, step=1, value=int(info_leito['fugulin'].values[0]) if 'fugulin' in info_leito and info_leito['fugulin'].values[0].isdigit() else 0)
    asg = st.selectbox("Classificação da ASG", ["", "Bem nutrido (ASG A)", "Moderadamente desnutrido (ASG B)", "Gravemente desnutrido (ASG C)"], index=["", "Bem nutrido (ASG A)", "Moderadamente desnutrido (ASG B)", "Gravemente desnutrido (ASG C)"].index(info_leito['asg'].values[0]) if 'asg' in info_leito and info_leito['asg'].values[0] in ["", "Bem nutrido (ASG A)", "Moderadamente desnutrido (ASG B)", "Gravemente desnutrido (ASG C)"] else 0)
    mrc = st.number_input("Pontuação da Escala MRC (0 a 60)", min_value=0, max_value=60, step=1, value=int(info_leito['mrc'].values[0]) if 'mrc' in info_leito and info_leito['mrc'].values[0].isdigit() else 0)
    triagem = st.number_input("Pontuação da Triagem de Alta", min_value=0, max_value=20, step=1, value=int(info_leito['triagem'].values[0]) if 'triagem' in info_leito and info_leito['triagem'].values[0].isdigit() else 0)
    charlson = st.number_input("Índice de Charlson", min_value=0, max_value=50, step=1, value=int(info_leito['charlson'].values[0]) if 'charlson' in info_leito and info_leito['charlson'].values[0].isdigit() else 0)
    # Normalizações
    if fugulin == 0:
        fugulin_norm = 0
    elif fugulin < 17:
        fugulin_norm = 0
    elif 18 <= fugulin <= 22:
        fugulin_norm = 0.14
    elif 23 <= fugulin <= 34:
        fugulin_norm = 0.43
    elif fugulin > 34:
        fugulin_norm = 1
    asg_map = {"": 0, "Bem nutrido (ASG A)": 0, "Moderadamente desnutrido (ASG B)": 0.5, "Gravemente desnutrido (ASG C)": 1}
    asg_norm = asg_map.get(asg, 0)
    mrc_norm = 1 if mrc <= 35 else 0
    triagem_norm = 1 if triagem >= 10 else 0
    charlson_norm = 1 if charlson >= 6 else (charlson / 6) * 0.75 if charlson else 0
    irah = round((fugulin_norm + asg_norm + mrc_norm + triagem_norm + charlson_norm) / 5, 2)
    risco = "Baixo" if irah <= 0.3 else "Moderado" if irah <= 0.59 else "Alto"
    st.markdown("---")
    st.subheader("Resultado do IRAH")
    st.metric("Pontuação do IRAH", f"{irah}")
    st.success(f"Classificação: {risco}")
    # Botões lado a lado: Atualizar ficha clínica e Exportar histórico IRAH
    col_irah_btns = st.columns([2, 2])
    with col_irah_btns[0]:
        if st.button("Atualizar risco assistencial na ficha clínica", key="atualizar_irah"):
            df_leitos.loc[df_leitos['leito'] == leito_sel, 'risco_assistencial'] = risco
            df_leitos.loc[df_leitos['leito'] == leito_sel, 'irah'] = irah
            df_leitos.loc[df_leitos['leito'] == leito_sel, 'fugulin'] = fugulin
            df_leitos.loc[df_leitos['leito'] == leito_sel, 'asg'] = asg
            df_leitos.loc[df_leitos['leito'] == leito_sel, 'mrc'] = mrc
            df_leitos.loc[df_leitos['leito'] == leito_sel, 'triagem'] = triagem
            df_leitos.loc[df_leitos['leito'] == leito_sel, 'charlson'] = charlson
            # Salvar
            for _, row in df_leitos.iterrows():
                salvar_leito(row['leito'], row.to_dict())
            # Registrar histórico local
            HISTORICO_IRAH_SHEET = 'historico_irah'
            try:
                df_hist = pd.DataFrame(obter_historico_irah())
                if df_hist.empty:
                    df_hist = pd.DataFrame(columns=['data_hora', 'leito', 'fugulin', 'asg', 'mrc', 'triagem', 'charlson', 'irah', 'classificacao'])
            except Exception:
                df_hist = pd.DataFrame(columns=['data_hora', 'leito', 'fugulin', 'asg', 'mrc', 'triagem', 'charlson', 'irah', 'classificacao'])
            now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            historico = pd.DataFrame([{ 'data_hora': now, 'leito': leito_sel, 'fugulin': fugulin, 'asg': asg, 'mrc': mrc, 'triagem': triagem, 'charlson': charlson, 'irah': irah, 'classificacao': risco }])
            df_hist = pd.concat([df_hist, historico], ignore_index=True)
            salvar_historico_irah(df_hist)
            st.success("Risco assistencial atualizado e histórico salvo!")
    with col_irah_btns[1]:
        # Exportar histórico IRAH para Firebase
        if st.button("Exportar histórico IRAH", key="exportar_irah_fb"):
            import pandas as pd
            from firebase_utils import salvar_historico_irah
            HISTORICO_IRAH_SHEET = 'historico_irah'
            try:
                df_hist = pd.DataFrame(obter_historico_irah())
                if df_hist.empty:
                    df_hist = pd.DataFrame(columns=['data_hora', 'leito', 'fugulin', 'asg', 'mrc', 'triagem', 'charlson', 'irah', 'classificacao'])
            except Exception:
                df_hist = pd.DataFrame(columns=['data_hora', 'leito', 'fugulin', 'asg', 'mrc', 'triagem', 'charlson', 'irah', 'classificacao'])
            # Adiciona coluna Atendimento se não existir
            if 'Atendimento' not in df_hist.columns:
                df_hist['Atendimento'] = ""
            # Atualiza Atendimento da linha mais recente (opcional: pode ser customizado)
            if not df_hist.empty:
                df_hist.at[df_hist.index[-1], 'Atendimento'] = atendimento
            salvar_historico_irah(df_hist)
            st.success('Histórico IRAH exportado para Firebase com sucesso!')
        # Removido histórico local do IRAH da interface


# Dashboard: Total de pacientes por médico e por equipe
if aba_selecionada == "Dashboard":
    st.header("Dashboard de Pacientes")
    st.subheader("Total de Pacientes por Médico")
    try:
        import pandas as pd
        df_leitos = pd.DataFrame(obter_leitos())
        if df_leitos.empty:
            df_leitos = pd.DataFrame(columns=colunas_leitos)
    except Exception:
        df_leitos = pd.DataFrame(columns=colunas_leitos)
    total_por_medico = df_leitos['medico'].value_counts().reset_index()
    total_por_medico.columns = ['Médico', 'Total de Pacientes']
    st.dataframe(total_por_medico, hide_index=True)
    st.subheader("Total de Pacientes por Equipe")
    total_por_equipe = df_leitos['equipe'].value_counts().reset_index()
    total_por_equipe.columns = ['Equipe', 'Total de Pacientes']
    st.dataframe(total_por_equipe, hide_index=True)

    # --- NOVO PAINEL: Pacientes por equipe e por andar ---
    st.subheader("Pacientes por Equipe e por Andar")
    # Filtros internos
    unidades_config = list(CONFIG_ANDARES.keys())
    unidade_filtro = st.selectbox("Filtrar por unidade", ["(Todas)"] + unidades_config, key="dashboard_unidade_filtro")

    # Opções de andar dependem da unidade escolhida
    if unidade_filtro == "(Todas)":
        andares_opcoes = ["(Todos)"]
        for u in unidades_config:
            andares_opcoes += [f"{a} ({u})" for a in CONFIG_ANDARES[u].keys()]
    else:
        andares_opcoes = ["(Todos)"] + list(CONFIG_ANDARES[unidade_filtro].keys())
    andar_filtro = st.selectbox("Filtrar por andar", andares_opcoes, key="dashboard_andar_filtro")

    # Filtro por equipe
    if 'equipe' in df_leitos.columns:
        equipes_unicas = sorted([e for e in df_leitos['equipe'].dropna().unique() if e.strip() != ""])
        equipe_filtro = st.selectbox("Filtrar por equipe", ["(Todas)"] + equipes_unicas, key="dashboard_equipe_filtro")
    else:
        equipe_filtro = "(Todas)"

    if 'leito' in df_leitos.columns and 'equipe' in df_leitos.columns and 'nome' in df_leitos.columns:
        setores = []
        # Monta lista de setores (unidade, andar, leitos)
        for u in unidades_config:
            for a in CONFIG_ANDARES[u].keys():
                inicio, fim = CONFIG_ANDARES[u][a]
                if u == "Unidade III":
                    leitos = [f"{i}-3" for i in range(inicio, fim + 1)]
                elif u == "Unidade IV":
                    leitos = [f"{i}-4" for i in range(inicio, fim + 1)]
                else:
                    leitos = [str(i) for i in range(inicio, fim + 1)]
                setores.append({"unidade": u, "andar": a, "leitos": leitos})

        # Filtrar setores conforme seleção
        setores_filtrados = []
        if unidade_filtro == "(Todas)":
            setores_filtrados = setores
        else:
            setores_filtrados = [s for s in setores if s["unidade"] == unidade_filtro]
        if andar_filtro != "(Todos)":
            if unidade_filtro == "(Todas)":
                # andar_filtro formato: "7º andar (Unidade IV)"
                andar_nome, unidade_nome = andar_filtro.rsplit(" (", 1)
                unidade_nome = unidade_nome.rstrip(")")
                setores_filtrados = [s for s in setores_filtrados if s["andar"] == andar_nome and s["unidade"] == unidade_nome]
            else:
                setores_filtrados = [s for s in setores_filtrados if s["andar"] == andar_filtro]

        # DataFrame filtrado por equipe, se necessário
        df_filtrado = df_leitos.copy()
        if equipe_filtro != "(Todas)":
            df_filtrado = df_filtrado[df_filtrado['equipe'] == equipe_filtro]

        if andar_filtro == "(Todos)":
            # Se unidade e andar = (Todas), mostrar lista setor a setor
            if unidade_filtro == "(Todas)":
                for setor in setores_filtrados:
                    st.markdown(f"#### {setor['andar']} ({setor['unidade']})")
                    df_andar = df_filtrado[df_filtrado['leito'].isin(setor['leitos'])]
                    if equipe_filtro == "(Todas)":
                        equipes = df_andar['equipe'].value_counts().reset_index()
                        equipes.columns = ['Equipe', 'Total de Pacientes']
                        for idx, row in equipes.iterrows():
                            st.write(f"- {row['Equipe']}: {row['Total de Pacientes']} paciente(s)")
                    else:
                        total = df_andar.shape[0]
                        st.write(f"- Total de Pacientes da Equipe '{equipe_filtro}': {total}")
                    total_ocupados = df_andar['nome'].replace('', pd.NA).dropna().shape[0]
                    st.write(f"**Total de leitos ocupados:** {total_ocupados}")
                    st.markdown('---')
            else:
                # Visão geral: total por equipe (ou geral) na unidade
                if equipe_filtro == "(Todas)":
                    total_por_equipe = df_filtrado['equipe'].value_counts().reset_index()
                    total_por_equipe.columns = ['Equipe', 'Total de Pacientes']
                    st.write(f"#### Total de Pacientes por Equipe na {unidade_filtro}")
                    st.dataframe(total_por_equipe, hide_index=True)
                else:
                    total = df_filtrado.shape[0]
                    st.write(f"#### Total de Pacientes da Equipe '{equipe_filtro}' na {unidade_filtro}: {total}")
        else:
            # Mostra detalhado por setor filtrado
            for setor in setores_filtrados:
                st.markdown(f"#### {setor['andar']} ({setor['unidade']})")
                df_andar = df_filtrado[df_filtrado['leito'].isin(setor['leitos'])]
                equipes = df_andar['equipe'].value_counts().reset_index()
                equipes.columns = ['Equipe', 'Total de Pacientes']
                for idx, row in equipes.iterrows():
                    st.write(f"- {row['Equipe']}: {row['Total de Pacientes']} paciente(s)")
                total_ocupados = df_andar['nome'].replace('', pd.NA).dropna().shape[0]
                st.write(f"**Total de leitos ocupados:** {total_ocupados}")
                st.markdown('---')
    else:
        st.info("Colunas necessárias ausentes para gerar o painel de pacientes por equipe e andar.")

# Painel de Leitos (tela principal)
if aba_selecionada == "Leitos":
    col_leitos1, col_leitos2, col_leitos3 = st.columns([5, 1, 1])
    col_leitos1.header("Painel de Leitos")
    if col_leitos2.button('Importar', help='Importar dados dos leitos do Firebase', key='importar_leitos'):
        from firebase_utils import importar_leitos
        df_importado = importar_leitos()
        if not df_importado.empty:
            st.success('Dados de leitos importados do Firebase com sucesso!')
        else:
            st.warning('Nenhum dado foi importado do Firebase. Verifique se a coleção está preenchida.')
    if col_leitos3.button('Exportar', help='Exportar dados dos leitos para Firebase', key='exportar_leitos'):
        from firebase_utils import exportar_leitos
        try:
            import pandas as pd
            df_leitos = pd.DataFrame(obter_leitos())
            if df_leitos.empty:
                df_leitos = pd.DataFrame(columns=colunas_leitos)
        except Exception:
            df_leitos = pd.DataFrame(columns=colunas_leitos)
        exportar_leitos(df_leitos)
        st.success('Dados de leitos exportados para Firebase com sucesso!')

    # Carregar dados reais dos leitos e médicos
    try:
        import pandas as pd
        df_leitos = pd.DataFrame(obter_leitos())
        if df_leitos.empty:
            df_leitos = pd.DataFrame(columns=colunas_leitos)
    except Exception:
        df_leitos = pd.DataFrame(columns=colunas_leitos)

    # Garante colunas de autorização para evitar KeyError
    if 'resposta_aut' not in df_leitos.columns:
        df_leitos['resposta_aut'] = ''
    if 'detalhe_aut' not in df_leitos.columns:
        df_leitos['detalhe_aut'] = ''

    if len(df_leitos) == 0:
        st.info("Nenhum leito cadastrado.")
    elif medico_filtro != "(Todos)":
        # Filtra todos os pacientes do médico, agrupados por unidade e andar
        setores = {}
        for unidade_nome, andares in CONFIG_ANDARES.items():
            for andar_nome, (inicio, fim) in andares.items():
                # Gera o range de leitos com sufixo correto
                if unidade_nome == "Unidade III":
                    leitos_setor = [f"{i}-3" for i in range(inicio, fim + 1)]
                elif unidade_nome == "Unidade IV":
                    leitos_setor = [f"{i}-4" for i in range(inicio, fim + 1)]
                else:
                    leitos_setor = [str(i) for i in range(inicio, fim + 1)]
                for leito in leitos_setor:
                    info_leito = df_leitos[df_leitos['leito'] == leito]
                    if not info_leito.empty:
                        nome_medico = info_leito['medico'].values[0]
                        nome_paciente = info_leito['nome'].values[0]
                        equipe = info_leito['equipe'].values[0] if ('equipe' in df_leitos.columns) else ""
                        if nome_medico == medico_filtro and nome_paciente:
                            chave_setor = f"{unidade_nome} - {andar_nome}"
                            if chave_setor not in setores:
                                setores[chave_setor] = []
                            setores[chave_setor].append({
                                'leito': leito,
                                'paciente': nome_paciente,
                                'equipe': equipe
                            })
        if not setores:
            st.info("Nenhum paciente encontrado para este médico.")
        else:
            for setor, pacientes in setores.items():
                st.markdown(f"### {setor}")
                for p in pacientes:
                    leito = p['leito']
                    info_leito = df_leitos[df_leitos['leito'] == leito]
                    nome_paciente = p['paciente']
                    equipe = p['equipe']
                    # Exibe informações básicas
                    st.write(f"Leito: {leito} | Paciente: {nome_paciente} | Equipe: {equipe}")
                    descricao_pendencia = info_leito['descricao_pendencia'].values[0] if 'descricao_pendencia' in df_leitos.columns and not info_leito.empty else ""
                    with st.expander("Ficha Clínica", expanded=False):
                        ficha_clinica_form(info_leito, leito, df_leitos, None, key_prefix="medico")
                    st.markdown("---")
    else:
        # Exibe todos os leitos normalmente
        if andar in CONFIG_ANDARES[unidade]:
            inicio, fim = CONFIG_ANDARES[unidade][andar]
        else:
            st.error(f"O andar selecionado ('{andar}') não existe para a unidade '{unidade}'. Por favor, selecione um andar válido.")
            st.stop()
        if unidade == "Unidade III":
            leitos_range = [f"{i}-3" for i in range(inicio, fim + 1)]
        elif unidade == "Unidade IV":
            leitos_range = [f"{i}-4" for i in range(inicio, fim + 1)]
        else:
            leitos_range = [str(i) for i in range(inicio, fim + 1)]

        for leito in leitos_range:
            info_leito = df_leitos[df_leitos['leito'] == leito]
            nome_paciente = info_leito['nome'].values[0] if not info_leito.empty else ""
            nome_medico = info_leito['medico'].values[0] if not info_leito.empty else ""
            equipe = info_leito['equipe'].values[0] if ('equipe' in df_leitos.columns and not info_leito.empty) else ""

            with st.container():
                cols = st.columns([1, 3, 3, 2])
                cols[0].markdown(f"**Leito {leito}**")
                # Campos editáveis SEMPRE visíveis
                novo_nome = cols[1].text_input("Nome do paciente", value=nome_paciente, key=f"edit_nome_{leito}")
                medicos_lista_com_branco = [""] + medicos_lista
                idx_medico = medicos_lista_com_branco.index(nome_medico) if nome_medico in medicos_lista_com_branco else 0
                novo_medico = cols[2].selectbox("Médico", medicos_lista_com_branco, index=idx_medico, key=f"edit_medico_{leito}")
                opcoes_equipe = ["", "Clínica Médica", "Cardiologia", "Hepatologia", "Cirurgia Geral", "Ortopedia", "Obstetrícia", "Pediatria", "Médico Assistente", "Hematologia", "Oncologia", "CABERJ", "MEDSENIOR", "REAL GRANDEZA"]
                idx_equipe = opcoes_equipe.index(equipe) if equipe in opcoes_equipe else 0
                novo_equipe = cols[3].selectbox("Equipe", opcoes_equipe, index=idx_equipe, key=f"edit_equipe_{leito}")
                # Salvamento automático
                alterou = (
                    novo_nome != nome_paciente or
                    novo_medico != nome_medico or
                    novo_equipe != equipe
                )
                if alterou:
                    # Se o leito não existe, cria uma nova linha
                    if info_leito.empty:
                        nova_linha = {col: '' for col in df_leitos.columns}
                        nova_linha['leito'] = leito
                        df_leitos = pd.concat([df_leitos, pd.DataFrame([nova_linha])], ignore_index=True)
                    df_leitos.loc[df_leitos['leito'] == leito, 'nome'] = novo_nome
                    df_leitos.loc[df_leitos['leito'] == leito, 'medico'] = novo_medico
                    df_leitos.loc[df_leitos['leito'] == leito, 'equipe'] = novo_equipe
                    for _, row in df_leitos.iterrows():
                        salvar_leito(row['leito'], row.to_dict())
                    st.success("Salvo!")
                # Ficha Clínica como expander (seta para baixo)
                descricao_pendencia = info_leito['descricao_pendencia'].values[0] if 'descricao_pendencia' in df_leitos.columns and not info_leito.empty else ""
                with st.expander("Ficha Clínica", expanded=False):
                    ficha_clinica_form(info_leito, leito, df_leitos, None, key_prefix="painel")
                st.markdown("---")


if aba_selecionada == "Visão do Plantonista":
    st.header("Resumo do Plantão")
    # Lista Pacientes em Cuidados Paliativos
    with st.expander("Pacientes em Cuidados Paliativos", expanded=True):
        if len(df_leitos) > 0:
            df_leitos_paliativos = df_leitos[df_leitos['cuidados_paliativos'].str.lower() == 'sim']
            paliativos = df_leitos_paliativos.copy()
            if not paliativos.empty:
                for idx, row in paliativos.iterrows():
                    cols = st.columns([1, 3, 2, 2, 2, 2])
                    cols[0].markdown(f"<b>Leito:</b> {row['leito']}", unsafe_allow_html=True)
                    cols[1].markdown(f"<b>Paciente:</b> {row['nome']}", unsafe_allow_html=True)
                    cols[2].markdown(f"<b>Médico responsável:</b> {row['medico']}", unsafe_allow_html=True)
                    cols[3].markdown(f"<b>Equipe:</b> {row['equipe']}", unsafe_allow_html=True)
                    cols[4].markdown(f"<b>Operadora:</b> {row['operadora']}", unsafe_allow_html=True)
                    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
            else:
                st.caption("Nenhum paciente em cuidados paliativos no momento.")
        else:
            st.caption("Nenhum dado de leitos disponível.")
    # Lista Pendência Noite
    with st.expander("Pendência noite", expanded=True):
        if len(df_leitos) > 0:
            df_leitos_pendencia = df_leitos[(df_leitos['pendencia_rotina'] == 'plantão noturno') & (df_leitos['pendencia_resolvida'] != 'Sim')]
            pendencias_noite = df_leitos_pendencia.copy()
            if not pendencias_noite.empty:
                for idx, row in pendencias_noite.iterrows():
                    cols = st.columns([1, 2, 2, 2, 2, 3, 1])
                    cols[0].markdown(f"<b>Leito:</b> {row['leito']}", unsafe_allow_html=True)
                    cols[1].markdown(f"<b>Paciente:</b> {row['nome']}", unsafe_allow_html=True)
                    cols[2].markdown(f"<b>Médico:</b> {row['medico']}", unsafe_allow_html=True)
                    cols[3].markdown(f"<b>Equipe:</b> {row['equipe']}", unsafe_allow_html=True)
                    cols[4].markdown(f"<b>Tipo:</b> {row['pendencia_rotina']}", unsafe_allow_html=True)
                    cols[5].markdown(f"<b>Descrição:</b> {row['descricao_pendencia']}", unsafe_allow_html=True)
                    if cols[6].button("Realizado", key=f"realizado_noite_{row['leito']}"):
                        df_leitos_pendencia.loc[df_leitos_pendencia['leito'] == row['leito'], 'pendencia_resolvida'] = 'Sim'
                        for _, row in df_leitos_pendencia.iterrows():
                            salvar_leito(row['leito'], row.to_dict())
                        st.success(f"Pendência do leito {row['leito']} marcada como realizada.")
                        st.experimental_rerun()
                    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
            else:
                st.caption("Nenhuma pendência de plantão noturno aberta.")
        else:
            st.caption("Nenhum dado de leitos disponível.")
    # Código Amarelo segue abaixo
    with st.expander("Código Amarelo nas últimas 24h", expanded=True):
        if len(df_leitos) > 0:
            df_leitos_codigo = df_leitos[df_leitos['intercorrencia_24h'].str.lower() == 'amarela']
            amarelos = df_leitos_codigo.copy()
            if not amarelos.empty:
                for idx, row in amarelos.iterrows():
                    cols = st.columns([1, 2, 2, 3])
                    cols[0].markdown(f"<b>Leito:</b> {row['leito']}", unsafe_allow_html=True)
                    cols[1].markdown(f"<b>Paciente:</b> {row['nome']}", unsafe_allow_html=True)
                    equipe = row['equipe'] if 'equipe' in row else ''
                    cols[2].markdown(f"<b>Equipe:</b> {equipe}", unsafe_allow_html=True)
                    descricao = row['desc_intercorrencia'] if 'desc_intercorrencia' in row else ''
                    cols[3].markdown(f"<b>Descrição:</b> {descricao}", unsafe_allow_html=True)
                    st.markdown('<hr style=\"margin-top: 0.5rem; margin-bottom: 0.5rem;\">', unsafe_allow_html=True)
            else:
                st.caption("Nenhum paciente com intercorrência amarela nas últimas 24h.")
        else:
            st.caption("Nenhum dado de leitos disponível.")

if aba_selecionada == "Pendência tarde":
    st.header("Pendência tarde")
    if len(df_leitos) > 0:
        df_leitos_pendencia = df_leitos[(df_leitos['pendencia_rotina'] == 'rotina tarde') & (df_leitos['pendencia_resolvida'] != 'Sim')]
        pendencias_tarde = df_leitos_pendencia.copy()
        if not pendencias_tarde.empty:
            for idx, row in pendencias_tarde.iterrows():
                cols = st.columns([1, 2, 2, 2, 2, 3, 1])
                cols[0].markdown(f"<b>Leito:</b> {row['leito']}", unsafe_allow_html=True)
                cols[1].markdown(f"<b>Paciente:</b> {row['nome']}", unsafe_allow_html=True)
                cols[2].markdown(f"<b>Médico:</b> {row['medico']}", unsafe_allow_html=True)
                cols[3].markdown(f"<b>Equipe:</b> {row['equipe']}", unsafe_allow_html=True)
                cols[4].markdown(f"<b>Tipo:</b> {row['pendencia_rotina']}", unsafe_allow_html=True)
                cols[5].markdown(f"<b>Descrição:</b> {row['descricao_pendencia']}", unsafe_allow_html=True)
                if cols[6].button("Realizado", key=f"realizado_tarde_{row['leito']}"):
                    df_leitos_pendencia.loc[df_leitos_pendencia['leito'] == row['leito'], 'pendencia_resolvida'] = 'Sim'
                    for _, row in df_leitos_pendencia.iterrows():
                        salvar_leito(row['leito'], row.to_dict())
                    st.success(f"Pendência do leito {row['leito']} marcada como realizada.")
                    st.experimental_rerun()
                st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
        else:
            st.caption("Nenhuma pendência de rotina tarde aberta.")
    else:
        st.caption("Nenhum dado de leitos disponível.")

if aba_selecionada == "Admissão":
    st.header("Admissão de Paciente")
    with st.expander("Nova Admissão", expanded=True):
        nome_paciente = st.text_input("Nome do paciente", key="admissao_nome_admissao")
        origem = st.selectbox("Origem", ["Emergência", "CTI", "Outros"], key="admissao_origem_admissao")
        obs = st.text_area("Observações", key="admissao_obs_admissao")
        if st.button("Salvar Admissão", key="admissao_salvar_admissao"):
            df_adm = carregar_admissoes()
            nova = {"nome_paciente": nome_paciente, "origem": origem, "observacoes": obs}
            df_adm = pd.concat([df_adm, pd.DataFrame([nova])], ignore_index=True)
            salvar_admissoes(df_adm)
            registrar_historico_admissao("admissao_cadastrada", nome_paciente, origem, obs)
            st.success("Paciente adicionado à lista de admissões!")
        if st.button("Cancelar", key="admissao_cancelar_admissao"):
            st.session_state['modal_admissao'] = False

    st.subheader("Admissões Pendentes")
    df_adm = carregar_admissoes()
    for idx, row in df_adm.reset_index().iterrows():
        c1, c2, c3, c4, c5, c6 = st.columns([3,2,4,4,2,2])
        c1.write(row['nome_paciente'])
        c2.write(row['origem'])
        c3.write(row['observacoes'])
        realizado_key = f"realizado_{row['nome_paciente']}_{row['origem']}_{idx}"
        cancel_key = f"cancelado_{row['nome_paciente']}_{row['origem']}_{idx}"
        if c5.button("Realizado", key=realizado_key, type="secondary"):
            st.markdown("""
                <style>
                div[data-testid='stButton'] button[kind='secondary'] {background-color: #22c55e !important; color: white !important;}
                </style>
            """, unsafe_allow_html=True)
            # Migrar para admitidos
            df_admitidos = carregar_admitidos()
            data_hoje = date.today().strftime('%Y-%m-%d')
            import uuid
            novo = {
                "admitido_id": str(uuid.uuid4()),
                "nome_paciente": row['nome_paciente'],
                "origem": row['origem'],
                "observacoes": row['observacoes'],
                "data_admissao": data_hoje
            }
            df_admitidos = pd.concat([df_admitidos, pd.DataFrame([novo])], ignore_index=True)
            salvar_admitidos(df_admitidos)
            registrar_historico_admissao("admissao_realizada", row['nome_paciente'], row['origem'], row['observacoes'])
            # Remover do Firebase
            from firebase_utils import excluir_admissao
            excluir_admissao(row.get('admissao_id'))
            st.cache_data.clear()
            st.experimental_rerun()
        if c6.button("Cancelado", key=cancel_key, type="secondary"):
            st.markdown("""
                <style>
                div[data-testid='stButton'] button[kind='secondary'] {background-color: #ef4444 !important; color: white !important;}
                </style>
            """, unsafe_allow_html=True)
            # Remove a linha da lista de admissões
            registrar_historico_admissao("admissao_cancelada", row['nome_paciente'], row['origem'], row['observacoes'])
            from firebase_utils import excluir_admissao
            excluir_admissao(row.get('admissao_id'))
            st.cache_data.clear()
            st.experimental_rerun()

    st.subheader("Admitidos")
    df_admitidos = carregar_admitidos()
    for idx, row in df_admitidos.iterrows():
        c1, c2, c3, c4, c5 = st.columns([3,2,4,3,2])
        c1.write(row.get('nome_paciente', ''))
        c2.write(row.get('origem', ''))
        c3.write(row.get('observacoes', ''))
        c4.write(row.get('data_admissao', ''))
        cancelar_key = f"cancelar_admitido_{row.get('admitido_id', idx)}"
        if c5.button("Cancelar", key=cancelar_key, type="secondary"):
            st.markdown("""
                <style>
                div[data-testid='stButton'] button[kind='secondary'] {background-color: #ef4444 !important; color: white !important;}
                </style>
            """, unsafe_allow_html=True)
            # Remover admitido do Firebase
            from firebase_utils import salvar_admissao, excluir_admitido
            excluir_admitido = globals().get('excluir_admitido')
            if excluir_admitido is None:
                def excluir_admitido(admitido_id):
                    import firebase_utils
                    firebase_utils.inicializar_firebase()
                    ref = firebase_utils.db.reference(f'admitidos/{admitido_id}')
                    ref.delete()
            excluir_admitido(row.get('admitido_id'))
            # Retornar para admissões pendentes
            nova = {"nome_paciente": row.get('nome_paciente',''), "origem": row.get('origem',''), "observacoes": row.get('observacoes','')}
            df_adm = carregar_admissoes()
            df_adm = pd.concat([df_adm, pd.DataFrame([nova])], ignore_index=True)
            salvar_admissoes(df_adm)
            st.cache_data.clear()
            st.experimental_rerun()

if aba_selecionada == "Médicos":
    col_med1, col_med2, col_med3 = st.columns([5, 1, 1])
    col_med1.header("Gestão de Médicos")
    if col_med2.button('Importar', help='Importar dados dos médicos do Firebase', key='importar_medicos'):
        from firebase_utils import importar_medicos
        df_importado = importar_medicos()
        if not df_importado.empty:
            st.success('Dados de médicos importados do Firebase com sucesso!')
        else:
            st.warning('Nenhum dado foi importado do Firebase. Verifique se a coleção está preenchida.')
    if col_med3.button('Exportar', help='Exportar dados dos médicos para Firebase', key='exportar_medicos'):
        from firebase_utils import exportar_medicos
        df_medicos = pd.DataFrame(obter_medicos())
        exportar_medicos(df_medicos)
        st.success('Dados de médicos exportados para Firebase com sucesso!')
    import uuid
    if len(df_medicos) > 0:
        df_medicos = pd.DataFrame(obter_medicos())
    else:
        df_medicos = pd.DataFrame(columns=["Nome do Médico", "medico_id"])
    # Garante que todos os médicos tenham medico_id único
    if not 'medico_id' in df_medicos.columns:
        df_medicos['medico_id'] = None
    for idx, row in df_medicos.iterrows():
        if pd.isna(row.get('medico_id', None)) or row.get('medico_id', '') == '':
            df_medicos.at[idx, 'medico_id'] = str(uuid.uuid4())
    # Formulário para adicionar novo médico
    with st.expander("Cadastrar novo médico", expanded=True):
        with st.form(key="form_cadastro_medico"):
            nome_medico = st.text_input("Nome do Médico")
            submit = st.form_submit_button("Cadastrar")
            if submit:
                if nome_medico.strip() == "":
                    st.warning("Digite o nome do médico antes de salvar.")
                else:
                    if nome_medico.strip() not in df_medicos['Nome do Médico'].values:
                        novo_medico = {"Nome do Médico": nome_medico.strip(), "medico_id": str(uuid.uuid4())}
                        df_medicos = pd.concat([df_medicos, pd.DataFrame([novo_medico])], ignore_index=True)
                        for _, row in df_medicos.iterrows():
                            salvar_medico(row['medico_id'], row.to_dict())
                        st.success("Médico cadastrado com sucesso!")
                        st.experimental_rerun()
                    else:
                        st.info("Este médico já está cadastrado.")
    # Lista de médicos cadastrados
    st.subheader("Lista de médicos cadastrados")
    if not df_medicos.empty:
        for idx, row in df_medicos.iterrows():
            col_nome, col_excluir = st.columns([6,1])
            col_nome.write(row["Nome do Médico"] if "Nome do Médico" in row else "")
            if col_excluir.button("Excluir", key=f"excluir_medico_{idx}"):
                from firebase_utils import excluir_medico
                excluir_medico(row['medico_id'])
                st.cache_data.clear()
                st.experimental_rerun()
    else:
        st.info("Nenhum médico cadastrado ainda.")

if aba_selecionada == "Gestão":
    st.header("Gestão de Leitos")
    # --- Lista de Pacientes com Alto Risco ---
    st.subheader("Pacientes com alto risco")
    if len(df_leitos) > 0:
        df_leitos_gestao = df_leitos[df_leitos['risco_assistencial'].str.lower() == 'alto']
        altos = df_leitos_gestao.copy()
        if altos.empty:
            st.info("Nenhum paciente com risco assistencial alto no momento.")
        else:
            st.table(altos[['leito', 'nome']].rename(columns={'leito': 'Leito', 'nome': 'Paciente'}).reset_index(drop=True))
    st.markdown("---")

    st.header("Gestão")

    # Histórico de admissões
    with st.expander("Histórico de Admissões", expanded=False):
        import pandas as pd
        
        HISTORICO_ADMISSOES_PATH = os.path.join('data', 'historico_admissoes.csv')
        if os.path.exists(HISTORICO_ADMISSOES_PATH):
            df_hist_adm = pd.read_csv(HISTORICO_ADMISSOES_PATH, dtype=str).fillna("")
            st.dataframe(df_hist_adm, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum histórico de admissões registrado.")

    # Histórico de autorizações
    with st.expander("Histórico de Autorizações", expanded=False):
        HISTORICO_AUTORIZACAO_PATH = os.path.join('data', 'historico_autorizacao.csv')
        if os.path.exists(HISTORICO_AUTORIZACAO_PATH):
            df_hist_aut = pd.read_csv(HISTORICO_AUTORIZACAO_PATH, dtype=str).fillna("")
            st.dataframe(df_hist_aut, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum histórico de autorizações registrado.")

    # Histórico de desospitalização
    with st.expander("Histórico de Desospitalização", expanded=False):
        HISTORICO_DESOSP_PATH = os.path.join('data', 'historico_desospitalizacao.csv')
        if os.path.exists(HISTORICO_DESOSP_PATH):
            df_hist_desosp = pd.read_csv(HISTORICO_DESOSP_PATH, dtype=str).fillna("")
            st.dataframe(df_hist_desosp, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum histórico de desospitalização registrado.")

    if len(df_leitos) > 0:
        df_gestao = df_leitos.copy()
        # Lista 1: Pacientes AMIL
        with st.expander("Pacientes AMIL", expanded=True):
            amil = df_gestao[df_gestao['operadora'].str.upper() == 'AMIL']
            if not amil.empty:
                for idx, row in amil.iterrows():
                    cols = st.columns([1, 3, 2, 2, 2, 2])
                    cols[0].markdown(f"<b>Leito:</b> {row.get('leito','')}", unsafe_allow_html=True)
                    cols[1].markdown(f"<b>Paciente:</b> {row.get('nome','')}", unsafe_allow_html=True)
                    cols[2].markdown(f"<b>Médico:</b> {row.get('medico','')}", unsafe_allow_html=True)
                    cols[3].markdown(f"<b>Equipe:</b> {row.get('equipe','') if 'equipe' in row else ''}", unsafe_allow_html=True)
                    cols[4].markdown(f"<b>Operadora:</b> {row.get('operadora','')}", unsafe_allow_html=True)
                    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
            else:
                st.caption("Nenhum paciente AMIL encontrado.")
        # Lista 2: Desospitalização
        with st.expander("Desospitalização", expanded=True):
            desosp = df_gestao[df_gestao['desospitalizacao'].str.lower() == 'sim']
            if not desosp.empty:
                for idx, row in desosp.iterrows():
                    cols = st.columns([1, 3, 2, 2, 2, 2])
                    # Exibe corretamente cada campo, inclusive para casos de erro de preenchimento
                    leito_num = row['leito'] if 'leito' in row and row['leito'] and str(row['leito']).strip() not in ('', 'nan', 'None', 'null', 'NaN', '0') else '(não informado)'
                    paciente = row['nome'] if 'nome' in row else ''
                    medico = row['medico'] if 'medico' in row else ''
                    equipe = row['equipe'] if 'equipe' in row else ''
                    desosp_txt = row['desospitalizacao'] if 'desospitalizacao' in row else ''
                    operadora = row['operadora'] if 'operadora' in row else ''
                    cols[0].markdown(f"<b>Leito:</b> {leito_num}", unsafe_allow_html=True)
                    cols[1].markdown(f"<b>Paciente:</b> {paciente}", unsafe_allow_html=True)
                    cols[2].markdown(f"<b>Médico:</b> {medico}", unsafe_allow_html=True)
                    cols[3].markdown(f"<b>Equipe:</b> {equipe}", unsafe_allow_html=True)
                    cols[4].markdown(f"<b>Desospitalização:</b> {desosp_txt}", unsafe_allow_html=True)
                    cols[5].markdown(f"<b>Operadora:</b> {operadora}", unsafe_allow_html=True)
                    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
            else:
                st.caption("Nenhum paciente em desospitalização.")
        # Lista 3: Autorização
        with st.expander("Autorização", expanded=True):
            # Garante que todas as colunas necessárias existem
            for col in ['autorizacao_pendente', 'resposta_aut', 'procedimento', 'detalhe_aut']:
                if col not in df_gestao.columns:
                    df_gestao[col] = ''
            # Exibir todos os pacientes com qualquer valor nos campos de autorização, resposta, procedimento ou detalhe
            autorizacao = df_gestao[
                df_gestao['autorizacao_pendente'].isin(['Procedimento', 'Medicação'])
            ]
            if not autorizacao.empty:
                for idx, row in autorizacao.iterrows():
                    cols = st.columns([1, 3, 2, 2, 2, 2, 3])
                    cols[0].markdown(f"<b>Leito:</b> {row.get('leito','')}", unsafe_allow_html=True)
                    cols[1].markdown(f"<b>Paciente:</b> {row.get('nome','')}", unsafe_allow_html=True)
                    cols[2].markdown(f"<b>Médico:</b> {row.get('medico','')}", unsafe_allow_html=True)
                    cols[3].markdown(f"<b>Equipe:</b> {row.get('equipe','') if 'equipe' in row else ''}", unsafe_allow_html=True)
                    # Editáveis
                    nova_autorizacao = cols[4].selectbox(
                        "Autorização", ["", "Não", "Procedimento", "Medicação"],
                        index=["", "Não", "Procedimento", "Medicação"].index(row.get('autorizacao_pendente','')) if row.get('autorizacao_pendente','') in ["", "Não", "Procedimento", "Medicação"] else 0,
                        key=f"gestao_autorizacao_{row['leito']}"
                    )
                    nova_resposta = cols[5].selectbox(
                        "Resposta", ["", "Autorizado", "Em análise"],
                        index=["", "Autorizado", "Em análise"].index(row.get('resposta_aut','')) if row.get('resposta_aut','') in ["", "Autorizado", "Em análise"] else 0,
                        key=f"gestao_resposta_{row['leito']}"
                    )
                    novo_detalhe = cols[6].text_input(
                        "Detalhe", value=row.get('detalhe_aut',''),
                        key=f"gestao_detalhe_{row['leito']}"
                    )
                    # Sincronizar alterações
                    if (
                        nova_autorizacao != row.get('autorizacao_pendente','') or
                        nova_resposta != row.get('resposta_aut','') or
                        novo_detalhe != row.get('detalhe_aut','')
                    ):
                        df_gestao.loc[df_gestao['leito'] == row['leito'], 'autorizacao_pendente'] = nova_autorizacao
                        df_gestao.loc[df_gestao['leito'] == row['leito'], 'resposta_aut'] = nova_resposta
                        df_gestao.loc[df_gestao['leito'] == row['leito'], 'detalhe_aut'] = novo_detalhe
                        # Registrar histórico de autorização
                        registrar_historico_autorizacao(
                            acao="autorizacao_editada",
                            leito=row.get('leito',''),
                            paciente=row.get('nome',''),
                            detalhe=f"autorizacao: {nova_autorizacao}, resposta: {nova_resposta}",
                            observacoes=novo_detalhe
                        )
                        for _, row in df_gestao.iterrows():
                            salvar_leito(row['leito'], row.to_dict())
                        st.experimental_rerun()
                    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
            else:
                st.caption("Nenhuma autorização pendente.")
        # Lista 4: Alta prevista para amanhã
        with st.expander("Alta prevista para amanhã", expanded=True):
            alta = df_gestao[df_gestao['alta_amanha'].str.lower() == 'sim']
            if not alta.empty:
                for idx, row in alta.iterrows():
                    cols = st.columns([1, 3, 2, 2, 2, 2])
                    cols[0].markdown(f"<b>Leito:</b> {row.get('leito','')}", unsafe_allow_html=True)
                    cols[1].markdown(f"<b>Paciente:</b> {row.get('nome','')}", unsafe_allow_html=True)
                    cols[2].markdown(f"<b>Médico:</b> {row.get('medico','')}", unsafe_allow_html=True)
                    cols[3].markdown(f"<b>Equipe:</b> {row.get('equipe','') if 'equipe' in row else ''}", unsafe_allow_html=True)
                    cols[4].markdown(f"<b>Alta prevista para amanhã:</b> {row.get('alta_amanha','')}", unsafe_allow_html=True)
                    cols[5].markdown(f"<b>Operadora:</b> {row.get('operadora','')}", unsafe_allow_html=True)
                    st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
            else:
                st.caption("Nenhum paciente com alta prevista para amanhã.")
        # Lista 5: Altas Hoje
        ALTAS_HOJE_PATH = os.path.join('data', 'altas_hoje.csv')
        with st.expander("Altas Hoje", expanded=True):
            if os.path.exists(ALTAS_HOJE_PATH):
                altas_hoje = pd.read_csv(ALTAS_HOJE_PATH, dtype=str).fillna("")
                hoje = date.today().strftime('%Y-%m-%d')
                altas_hoje = altas_hoje[altas_hoje['data_alta'] == hoje]
                if not altas_hoje.empty:
                    for idx, row in altas_hoje.iterrows():
                        cols = st.columns([1, 3, 2, 2])
                        cols[0].markdown(f"<b>Leito:</b> {row.get('leito','')}", unsafe_allow_html=True)
                        cols[1].markdown(f"<b>Paciente:</b> {row.get('nome','')}", unsafe_allow_html=True)
                        cols[2].markdown(f"<b>Médico:</b> {row.get('medico','')}", unsafe_allow_html=True)
                        cols[3].markdown(f"<b>Equipe:</b> {row.get('equipe','')}", unsafe_allow_html=True)
                        st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
                else:
                    st.caption("Nenhuma alta registrada hoje.")
            else:
                st.caption("Nenhuma alta registrada hoje.")
    else:
        st.info("Nenhum dado de leitos disponível.")




# Nova aba: Rastreio e Vacinação
if aba_selecionada == "Rastreio e Vacinação":
    st.header("🏥 Assistente de Rastreamento e Vacinação")
    # Carregar DataFrame dos leitos
    if len(df_leitos) > 0:
        df_leitos = df_leitos.copy()
        # Filtra apenas leitos que são números válidos (ex: '101', '202')
        leitos_disponiveis = [l.strip() for l in df_leitos['leito'].unique().tolist() if l and l.strip().isdigit()]
        leitos_disponiveis = sorted(leitos_disponiveis, key=int)
    else:
        df_leitos = pd.DataFrame()
        leitos_disponiveis = []
    # Dropdown de leitos por número
    leito_selecionado = st.selectbox("Leito (número)", leitos_disponiveis, key="rast_leito")
    risco_leito = ""
    if leito_selecionado and not df_leitos.empty:
        info_leito = df_leitos[df_leitos['leito'] == leito_selecionado]
        risco_leito = info_leito['risco_assistencial'].values[0] if 'risco_assistencial' in df_leitos.columns and not info_leito.empty else ""
        st.markdown(f"**Risco assistencial do leito selecionado:** `{risco_leito}`")
    with st.form("formulario_vacina"):
        sexo = st.selectbox("Sexo biológico", ["", "Feminino", "Masculino"])
        idade = st.number_input("Idade", min_value=0, max_value=120, step=1)
        profissional_saude = st.checkbox("Profissional de Saúde")

        st.markdown("### 📋 Fatores clínicos e antecedentes")
        col1, col2 = st.columns(2)
        with col1:
            imc_alto = st.checkbox("IMC ≥ 25")
            tabagista = st.checkbox("Tabagista ou ex-tabagista")
            gestante = st.checkbox("Gestante")
            ca_mama = st.checkbox("Histórico familiar de câncer de mama")
            ca_prostata = st.checkbox("Histórico familiar de câncer de próstata")
            ca_colon = st.checkbox("Histórico familiar de câncer colorretal")
        with col2:
            dm = st.checkbox("Diabetes Mellitus")
            dpoc = st.checkbox("DPOC")
            imunossuprimido = st.checkbox("Imunossuprimido")
            cardiovascular = st.checkbox("Doença cardiovascular crônica")
            renal = st.checkbox("Doença renal crônica")
            hepatopatia = st.checkbox("Doença hepática crônica")
            cancer = st.checkbox("Neoplasia ativa")

        submit = st.form_submit_button("Gerar Recomendações")

    if submit:
        respostas = []
        # Rastreio de mama
        if sexo == "Feminino":
            if 40 <= idade <= 74:
                respostas.append("✔️ Mamografia anual recomendada. [Ver diretriz (PDF)](./PDF/cancer mama rastreio.pdf)")
            if ca_mama and idade >= 35:
                respostas.append("✔️ Rastreio antecipado para câncer de mama.")
            if 25 <= idade <= 65:
                respostas.append("✔️ Papanicolau recomendado. [Ver diretriz (PDF)](./PDF/diretrizes_para_o_rastreamento_do_cancer_do_colo_do_utero_2016_corrigido (3).pdf)")
        # Rastreio de próstata
        if sexo == "Masculino":
            if idade >= 50:
                respostas.append("✔️ PSA e USG prostático recomendados. [Ver diretriz (PDF)](./PDF/rastreamento_próstat_2023_sociedades.pdf)")
            if ca_prostata and idade >= 45:
                respostas.append("✔️ Rastreio antecipado para câncer de próstata.")
        # Rastreio de câncer colorretal
        if ca_colon and idade >= 40:
            respostas.append("✔️ Colonoscopia antecipada recomendada devido a histórico familiar de câncer colorretal (parente de primeiro grau). Iniciar rastreamento aos 40 anos ou 10 anos antes da idade de diagnóstico do familiar, o que ocorrer primeiro. [Ver diretriz (PDF)](./PDF/CÂNCER COLORRETAL_DO DIAGNÓSTICO AO TRATAMENTO.pdf)")
        # TC de Tórax para tabagistas
        if tabagista and 50 <= idade <= 80:
            respostas.append("✔️ TC de Tórax de baixa dose para tabagistas. [Ver diretriz (PDF)](./PDF/tabagismo ca pulmao.pdf)")
        # Avaliação metabólica
        if imc_alto or dm or cardiovascular or renal or hepatopatia:
            respostas.append("✔️ Avaliação metabólica recomendada. [Ver diretriz (PDF)](./PDF/Diretrizes-Brasileiras-de-Obesidade-2016 (3).pdf)")
        # Avaliação para gamopatias monoclonais
        if idade >= 50:
            respostas.append("✔️ Avaliação para gamopatias monoclonais. [Ver diretriz (PDF)](./PDF/gamopatia monoclonal 2007.pdf)")
        # Vacinação para profissionais da saúde
        if profissional_saude:
            respostas.append("💉 Recomendada vacinação DTPa, Hepatite B, Influenza, COVID-19 (profissionais de saúde).")
        # Vacinação para gestantes
        if gestante:
            respostas.append("💉 Recomendada vacinação DTPa (20–36 semanas) e VSR (32–36 semanas) para gestantes.")
        # Indicação de vacinação em comorbidades
        if dpoc or cardiovascular or renal or imunossuprimido or gestante or dm or cancer or hepatopatia:
            respostas.append("💉 Indicação de vacinação pneumocócica 20V + 23V; considerar herpes-zóster; considerar vacina para dengue.")
        # HPV
        if 18 <= idade <= 45:
            respostas.append("💉 Vacinação contra HPV recomendada.")
        st.success("\n\n".join(respostas))
        st.markdown('---')
        st.markdown('### 📚 Sugestão de Leitura: Documentos em PDF')
        pdf_dir = "PDF"
        
        try:
            pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf") or ".pdf_" in f]
            if pdf_files:
                import base64
                for pdf in sorted(pdf_files):
                    pdf_path = os.path.join(pdf_dir, pdf)
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    st.download_button(
                        label=f"📄 Baixar/abrir {pdf}",
                        data=pdf_bytes,
                        file_name=pdf,
                        mime="application/pdf",
                        key=f"download_{pdf}"
                    )
                st.info("Clique no botão para baixar ou abrir o PDF correspondente.")
            else:
                st.warning("Nenhum PDF encontrado na pasta PDF.")
        except Exception as e:
            st.error(f"Erro ao listar PDFs: {e}")

# Rodapé
st.markdown("---")
st.caption("Sistema desenvolvido para uso hospitalar, mobile-first, multiusuário e com sincronização em tempo real.")
